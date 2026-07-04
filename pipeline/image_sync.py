#!/usr/bin/env python3
"""Weekly incremental image sync: diff bulk data against /data/image-manifest.json,
fetch only new/changed oracle_id PNGs, upload with the immutable flag (plan 2.4).

Download/upload core ported from ~/Projects/phase2-backfill/phase2_backfill.py
(the one-time Phase 2 backfill) — same throttle, retry, and PNG-magic-check
logic, resumable via the same "bucket + manifest are the truth" pattern.

DFC rule (locked, PHASE-2-COMPLETION.md correction #1): a card is two-image
if and only if card_faces[0].image_uris exists — never judged by card_faces
presence. Layout filter matches the Phase 2 backfill: drop art_series,
vanguard, scheme, planar; skip reversible_card (oracle_id lives on faces).

The manifest value per file is the Scryfall image URL itself (which embeds a
content-version token), not a locally-computed hash — cheap to diff without
downloading anything, and changes exactly when Scryfall's asset changes.

--dry-run reports what WOULD sync without downloading/uploading/rewriting
the manifest. A real sync of >=500 files requires --force, so a surprising
delta (e.g. a bad bulk fetch) halts loudly instead of hammering R2/Scryfall.
"""
import argparse
import gzip
import json
import os
import random
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

USER_AGENT = "MTJawnnyPipeline/1.0 (mtjawnny.com)"
RAW_PATH = Path("data/raw/oracle-cards.jsonl.gz")

RCLONE_REMOTE = os.environ.get("RCLONE_REMOTE", "r2:")
BUCKET = f"{RCLONE_REMOTE}mtjawnny"
IMAGE_REMOTE_DIR = f"{BUCKET}/cards/png"
MANIFEST_REMOTE = f"{BUCKET}/data/image-manifest.json"

MANIFEST_LOCAL = Path("data/artifacts/image-manifest.json")
BATCH_DIR = Path("data/artifacts/.image_sync_batch")

IMMUTABLE_HEADER = "cache-control=public, max-age=31536000, immutable"
MUTABLE_HEADER = "cache-control=public, max-age=300"

EXCLUDE_LAYOUTS = {"art_series", "vanguard", "scheme", "planar"}

BATCH_SIZE = 500
WORKERS = 5
MAX_RPS = 8.0
MAX_RETRIES = 5
LARGE_SYNC_THRESHOLD = 500

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def halt(message: str) -> None:
    print(f"STOP — {message}", file=sys.stderr)
    sys.exit(1)


class RateLimiter:
    def __init__(self, rps: float):
        self.interval = 1.0 / rps
        self.lock = threading.Lock()
        self.next_time = time.monotonic()

    def wait(self) -> None:
        with self.lock:
            now = time.monotonic()
            if self.next_time <= now:
                self.next_time = now + self.interval
                return
            sleep_for = self.next_time - now
            self.next_time += self.interval
        time.sleep(sleep_for)


LIMITER = RateLimiter(MAX_RPS)


def http_get(url: str, timeout: int = 120) -> bytes:
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        LIMITER.wait()
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code == 429:
                wait = 35 + random.uniform(0, 5)
            elif 500 <= e.code < 600:
                wait = min(2 ** attempt, 30) + random.uniform(0, 1)
            else:
                raise
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = e
            wait = min(2 ** attempt, 30) + random.uniform(0, 1)
        if attempt < MAX_RETRIES:
            time.sleep(wait)
    raise RuntimeError(f"gave up after {MAX_RETRIES} attempts: {url} ({last_err})")


def image_targets(card: dict) -> list:
    """Return [(filename, url), ...] for this card, [] if no usable image."""
    oid = card["oracle_id"]
    faces = card.get("card_faces") or []
    if faces and (faces[0].get("image_uris") or {}).get("png"):
        out = []
        for i, suffix in enumerate(("front", "back")):
            png = (faces[i].get("image_uris") or {}).get("png")
            if not png:
                return []
            out.append((f"{oid}-{suffix}.png", png))
        return out
    png = (card.get("image_uris") or {}).get("png")
    if png:
        return [(f"{oid}.png", png)]
    return []


def load_current_targets() -> dict:
    """oracle_id -> [(filename, url), ...] for every kept card in the current bulk."""
    if not RAW_PATH.exists():
        halt(f"{RAW_PATH} not found — run pipeline/fetch.py first")

    targets = {}
    with gzip.open(RAW_PATH, "rt", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                card = json.loads(line)
            except json.JSONDecodeError as e:
                halt(f"{RAW_PATH} line {line_no}: JSON parse failure: {e}")

            layout = card.get("layout") or "unknown"
            if layout == "reversible_card" or layout in EXCLUDE_LAYOUTS:
                continue
            oid = card.get("oracle_id")
            if not oid:
                continue

            files = image_targets(card)
            if files:
                targets[oid] = files
    return targets


def fetch_manifest() -> dict:
    result = subprocess.run(["rclone", "cat", MANIFEST_REMOTE], capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        print(f"no manifest found at {MANIFEST_REMOTE} — treating as empty (full first sync)")
        return {}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        halt(f"{MANIFEST_REMOTE} exists but is not valid JSON: {e}")


def fetch_bucket_filenames() -> set:
    result = subprocess.run(["rclone", "lsf", IMAGE_REMOTE_DIR], capture_output=True, text=True)
    if result.returncode != 0:
        return set()
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def diff_targets(current: dict, manifest: dict, bucket_files: set) -> tuple:
    """Split into (to_fetch, to_seed).

    to_fetch: filename missing from the manifest AND not already in the R2
    bucket — a genuine new/changed image that needs downloading.
    to_seed: filename missing from the manifest but the object already sits
    in R2 (e.g. the Phase 2 backfill uploaded it before the manifest
    existed) — no network fetch needed, just record it into the manifest.
    """
    to_fetch, to_seed = [], []
    for oid, files in current.items():
        manifest_entry = manifest.get(oid, {})
        for filename, url in files:
            if manifest_entry.get(filename) == url:
                continue
            if filename in bucket_files:
                to_seed.append((oid, filename, url))
            else:
                to_fetch.append((oid, filename, url))
    return to_fetch, to_seed


def download_one(filename: str, url: str, dest_dir: Path) -> tuple:
    try:
        data = http_get(url)
        if not data.startswith(PNG_MAGIC):
            return filename, False, "not a PNG (bad magic bytes / truncated)"
        (dest_dir / filename).write_bytes(data)
        return filename, True, None
    except Exception as e:
        return filename, False, str(e)


def rclone_run(args: list, description: str) -> None:
    result = subprocess.run(["rclone"] + args, capture_output=True, text=True)
    if result.returncode != 0:
        halt(f"{description} failed: {result.stderr.strip()}")


def do_sync(to_fetch: list, to_seed: list, manifest: dict) -> None:
    import shutil

    for oid, filename, url in to_seed:
        manifest.setdefault(oid, {})[filename] = url
    if to_seed:
        print(f"seeded {len(to_seed):,} already-uploaded file(s) into the manifest (no download needed)")

    total = len(to_fetch)
    synced_files = {}  # oracle_id -> {filename: url}
    start = time.monotonic()

    for batch_start in range(0, total, BATCH_SIZE):
        batch = to_fetch[batch_start:batch_start + BATCH_SIZE]
        if BATCH_DIR.exists():
            shutil.rmtree(BATCH_DIR)
        BATCH_DIR.mkdir(parents=True, exist_ok=True)

        ok_items = []
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            futures = {
                pool.submit(download_one, filename, url, BATCH_DIR): (oid, filename, url)
                for oid, filename, url in batch
            }
            for fut in as_completed(futures):
                oid, filename, url = futures[fut]
                _, success, err = fut.result()
                if success:
                    ok_items.append((oid, filename, url))
                else:
                    print(f"  FAILED {filename}: {err}", file=sys.stderr)

        if ok_items:
            rclone_run(
                ["copy", str(BATCH_DIR), IMAGE_REMOTE_DIR, "-M", "--metadata-set", IMMUTABLE_HEADER],
                "batch image upload",
            )
            for oid, filename, url in ok_items:
                synced_files.setdefault(oid, {})[filename] = url

        shutil.rmtree(BATCH_DIR, ignore_errors=True)
        done_n = min(batch_start + BATCH_SIZE, total)
        elapsed = time.monotonic() - start
        rate = done_n / elapsed if elapsed > 0 else 0
        print(f"  batch done: {done_n}/{total} synced, {rate:.1f} img/s")

    for oid, files in synced_files.items():
        manifest.setdefault(oid, {}).update(files)

    MANIFEST_LOCAL.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_LOCAL, "w") as f:
        json.dump(manifest, f)
    rclone_run(
        ["copy", str(MANIFEST_LOCAL), f"{BUCKET}/data", "-M", "--metadata-set", MUTABLE_HEADER],
        "manifest upload",
    )
    synced_count = sum(len(v) for v in synced_files.values())
    print(f"synced {synced_count} file(s), rewrote {MANIFEST_REMOTE}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run", action="store_true", help="report what would sync, without touching R2"
    )
    parser.add_argument(
        "--force", action="store_true",
        help=f"allow a real sync of >= {LARGE_SYNC_THRESHOLD} files without confirmation",
    )
    args = parser.parse_args()

    current = load_current_targets()
    print(f"current bulk: {len(current):,} kept cards with usable images")

    manifest = fetch_manifest()
    print(f"manifest: {len(manifest):,} oracle_ids tracked")

    bucket_files = fetch_bucket_filenames()
    print(f"R2 bucket: {len(bucket_files):,} objects under cards/png/")

    to_fetch, to_seed = diff_targets(current, manifest, bucket_files)
    print(
        f"delta: {len(to_fetch):,} file(s) need downloading, "
        f"{len(to_seed):,} already in R2 but missing from the manifest (seed-only)"
    )

    if args.dry_run:
        print("\nDRY RUN — would download:")
        for oid, filename, url in to_fetch[:20]:
            print(f"  {filename}  <-  {url}")
        if len(to_fetch) > 20:
            print(f"  ... and {len(to_fetch) - 20:,} more")
        print(f"\nDRY RUN COMPLETE — {len(to_fetch):,} file(s) would be downloaded, "
              f"{len(to_seed):,} would be seeded into the manifest with no download (not touched)")
        return

    if not to_fetch and not to_seed:
        print("nothing to sync — manifest already up to date")
        return

    if len(to_fetch) >= LARGE_SYNC_THRESHOLD and not args.force:
        halt(
            f"{len(to_fetch):,} files need downloading, >= the {LARGE_SYNC_THRESHOLD} sanity "
            f"threshold — this looks bigger than a normal week's churn. Re-run with --dry-run "
            f"to inspect, or --force if this is expected (e.g. a large set release)."
        )

    do_sync(to_fetch, to_seed, manifest)


if __name__ == "__main__":
    main()
