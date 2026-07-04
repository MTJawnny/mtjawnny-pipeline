#!/usr/bin/env python3
"""Upload versioned artifacts to R2 and flip /data/latest.json last (plan 3.10).

Gate: refuses to run unless pipeline/validate.py has passed *in this
invocation* — checked by recomputing sha256 of every gated artifact and
comparing against data/artifacts/.validated.json (written fresh by
validate.py). A stale marker from an earlier run, or artifacts rebuilt after
validate ran, fails the hash comparison and halts.

Upload order (the gate that makes deploys safe):
  1. Refuse-if-exists check on /data/v/<date>/ — never overwrite a versioned
     path.
  2. cards.sqlite, finisher/*, shards/*, manifest.json -> /data/v/<date>/,
     immutable cache-control.
  3. /data/latest.json LAST, max-age=300, only after everything else landed.
  4. Prune to the trailing 4 versions — never below 2 intact versions.
"""
import hashlib
import json
import os
import subprocess
import sqlite3
import sys
import time
from pathlib import Path

RCLONE_REMOTE = os.environ.get("RCLONE_REMOTE", "r2:")
BUCKET = f"{RCLONE_REMOTE}mtjawnny"

SQLITE_PATH = Path("data/artifacts/cards.sqlite")
VECTORS_PATH = Path("data/artifacts/finisher/vectors.bin")
INDEX_PATH = Path("data/artifacts/finisher/index.json.gz")
VECTORS_HEADER_PATH = Path("data/artifacts/finisher/vectors_header.json")
SHARDS_DIR = Path("data/artifacts/shards")
MARKER_PATH = Path("data/artifacts/.validated.json")
MANIFEST_LOCAL = Path("data/artifacts/manifest.json")
LATEST_LOCAL = Path("data/artifacts/latest.json")

GATED_ARTIFACTS = (SQLITE_PATH, VECTORS_PATH, INDEX_PATH)

IMMUTABLE_HEADER = "cache-control=public, max-age=31536000, immutable"
MUTABLE_HEADER = "cache-control=public, max-age=300"

KEEP_VERSIONS = 4
MIN_INTACT_VERSIONS = 2


def halt(message: str) -> None:
    print(f"STOP — {message}", file=sys.stderr)
    sys.exit(1)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_validated() -> dict:
    if not MARKER_PATH.exists():
        halt(
            f"{MARKER_PATH} not found — pipeline/validate.py has not passed "
            f"in this invocation, refusing to upload"
        )
    with open(MARKER_PATH) as f:
        marker = json.load(f)

    for path in GATED_ARTIFACTS:
        if not path.exists():
            halt(f"required artifact missing: {path}")
        expected_hash = marker.get("artifact_hashes", {}).get(str(path))
        if expected_hash is None:
            halt(f"{MARKER_PATH} has no recorded hash for {path} — validate.py must be stale")
        actual_hash = sha256_of(path)
        if actual_hash != expected_hash:
            halt(
                f"{path} sha256 does not match {MARKER_PATH} — artifacts changed "
                f"since validate.py ran, refusing to upload stale/unvalidated data "
                f"(re-run pipeline/validate.py)"
            )
    return marker


def rclone_run(args: list, description: str) -> subprocess.CompletedProcess:
    result = subprocess.run(["rclone"] + args, capture_output=True, text=True)
    if result.returncode != 0:
        halt(f"{description} failed: {result.stderr.strip()}")
    return result


def version_date() -> str:
    return time.strftime("%Y-%m-%d", time.gmtime())


def require_version_not_taken(version: str) -> None:
    remote = f"{BUCKET}/data/v/{version}"
    result = subprocess.run(["rclone", "lsf", remote], capture_output=True, text=True)
    existing = [line for line in result.stdout.splitlines() if line.strip()]
    if result.returncode == 0 and existing:
        halt(
            f"{remote} already has {len(existing)} object(s) — refusing to overwrite "
            f"a versioned path. If this is a same-day re-run, resolve manually."
        )


def upload_file(local: Path, remote_dir: str, header: str) -> None:
    rclone_run(
        ["copy", str(local), remote_dir, "-M", "--metadata-set", header],
        f"upload of {local} to {remote_dir}",
    )


def upload_dir(local_dir: Path, remote_dir: str, header: str) -> None:
    rclone_run(
        ["copy", str(local_dir), remote_dir, "-M", "--metadata-set", header],
        f"upload of {local_dir}/ to {remote_dir}",
    )


def gather_counts() -> dict:
    conn = sqlite3.connect(SQLITE_PATH)
    try:
        cards = conn.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
        commander_legal = conn.execute(
            "SELECT COUNT(*) FROM cards WHERE legalities_commander = 'legal'"
        ).fetchone()[0]
    finally:
        conn.close()
    return {"cards": cards, "commander_legal": commander_legal}


def build_manifest(version: str, counts: dict, marker: dict) -> dict:
    artifacts = {}
    for name, path in (
        ("cards.sqlite", SQLITE_PATH),
        ("finisher/index.json.gz", INDEX_PATH),
        ("finisher/vectors.bin", VECTORS_PATH),
        ("finisher/vectors_header.json", VECTORS_HEADER_PATH),
    ):
        artifacts[name] = {
            "size": path.stat().st_size,
            "sha256": marker["artifact_hashes"].get(str(path)) or sha256_of(path),
        }
    return {
        "version": version,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "counts": counts,
        "artifacts": artifacts,
    }


def build_latest(version: str, counts: dict) -> dict:
    return {
        "version": version,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "paths": {
            "cards_sqlite": f"/data/v/{version}/cards.sqlite",
            "finisher_index": f"/data/v/{version}/finisher/index.json.gz",
            "finisher_vectors": f"/data/v/{version}/finisher/vectors.bin",
            "finisher_vectors_header": f"/data/v/{version}/finisher/vectors_header.json",
            "shards_names": f"/data/v/{version}/shards/names/",
            "shards_neighbors": f"/data/v/{version}/shards/neighbors/",
            "manifest": f"/data/v/{version}/manifest.json",
        },
        "counts": counts,
    }


def prune_old_versions(current_version: str) -> None:
    result = subprocess.run(["rclone", "lsd", f"{BUCKET}/data/v"], capture_output=True, text=True)
    if result.returncode != 0:
        halt(f"could not list {BUCKET}/data/v to prune old versions: {result.stderr.strip()}")

    versions = sorted(
        {line.split()[-1] for line in result.stdout.splitlines() if line.strip()},
        reverse=True,
    )
    if current_version not in versions:
        versions = sorted(set(versions) | {current_version}, reverse=True)

    keep = versions[:KEEP_VERSIONS]
    prune_candidates = versions[KEEP_VERSIONS:]

    if len(keep) < MIN_INTACT_VERSIONS:
        if prune_candidates:
            print(
                f"  keeping all {len(versions)} version(s) — pruning would leave "
                f"fewer than {MIN_INTACT_VERSIONS} intact"
            )
        return

    if not prune_candidates:
        print(f"  {len(versions)} version(s) total, nothing to prune (keeping trailing {KEEP_VERSIONS})")
        return

    for old_version in prune_candidates:
        remote = f"{BUCKET}/data/v/{old_version}"
        rclone_run(["purge", remote], f"prune of old version {remote}")
        print(f"  pruned {remote}")


def main() -> None:
    marker = require_validated()
    version = version_date()
    print(f"uploading version {version}")

    require_version_not_taken(version)

    version_remote = f"{BUCKET}/data/v/{version}"

    upload_file(SQLITE_PATH, version_remote, IMMUTABLE_HEADER)
    upload_dir(Path("data/artifacts/finisher"), f"{version_remote}/finisher", IMMUTABLE_HEADER)
    upload_dir(SHARDS_DIR, f"{version_remote}/shards", IMMUTABLE_HEADER)

    counts = gather_counts()
    manifest = build_manifest(version, counts, marker)
    MANIFEST_LOCAL.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_LOCAL, "w") as f:
        json.dump(manifest, f, indent=2)
    upload_file(MANIFEST_LOCAL, version_remote, IMMUTABLE_HEADER)
    print(f"uploaded version manifest: {version_remote}/manifest.json")

    latest = build_latest(version, counts)
    with open(LATEST_LOCAL, "w") as f:
        json.dump(latest, f, indent=2)
    upload_file(LATEST_LOCAL, f"{BUCKET}/data", MUTABLE_HEADER)
    print(f"flipped {BUCKET}/data/latest.json -> version {version} (LAST, as required)")

    print("pruning old versions:")
    prune_old_versions(version)

    print(f"\nUPLOAD COMPLETE — version {version} live, latest.json flipped last")
    print(json.dumps(latest, indent=2))


if __name__ == "__main__":
    main()
