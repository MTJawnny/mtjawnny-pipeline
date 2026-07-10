"""Snapshot system for the Magic Thesaurus tier engine (Phase 0, inline spec in
RULING-MANIFEST-2026-07-09.md -- SNAPSHOT-SYSTEM-CHANGE-ORDER.md is lost).

Git remains the revert mechanism for logic/source. This layer is manifest-based
and adds: input pinning (checksums of the raw/derived data the engine reads),
constants fingerprinting (hash of every ruling constant tier_engine.py exposes),
gate-result capture (full tier_engine.py run, PASS/STOP lines parsed from its
stdout), and optional frozen output caching (reports + viewer cache, by checksum).

Strictest-reading choices made here (per manifest instruction to print them):
  - "dirty worktree" = ANY `git status --porcelain` output, staged, unstaged,
    OR untracked -- not just tracked modifications.
  - A pinned input that is missing halts loudly rather than being recorded as
    "absent" -- house style, not a silent gap.
  - Restore only ever touches cached OUTPUTS (reports/, viewer cache); it never
    touches data/ or source, since those are pinned-by-checksum, not owned by
    this tool. A snapshot with no cached outputs has nothing to restore.

Usage (run from repo root):
    python3 experiments/snapshot.py create <name> [--force] [--overwrite] [--cache-outputs]
    python3 experiments/snapshot.py restore <name>
    python3 experiments/snapshot.py list
    python3 experiments/snapshot.py verify-determinism [--anchor NAME ...]
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOTS_DIR = REPO_ROOT / "experiments" / "out" / "snapshots"
BACKUPS_DIR = SNAPSHOTS_DIR / "_pre-restore-backups"

ENGINE_PATH = REPO_ROOT / "experiments" / "tier_engine.py"

PINNED_INPUTS = [
    REPO_ROOT / "data" / "raw" / "oracle-cards.jsonl.gz",
    REPO_ROOT / "data" / "raw" / "oracle-tags.jsonl.gz",
    REPO_ROOT / "data" / "artifacts" / "cards.sqlite",
    REPO_ROOT / "experiments" / "out" / "card-tags.json.gz",
]

CACHED_OUTPUT_DIRS = [
    ("reports", REPO_ROOT / "experiments" / "out" / "reports"),
    ("viewer_data", REPO_ROOT / "experiments" / "out" / "viewer" / "data"),
]

CONSTANT_NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
PASS_RE = re.compile(r"\[PASS\]")
STOP_RE = re.compile(r"\[STOP\]")


def halt(message: str) -> None:
    print(f"STOP — {message}", file=sys.stderr)
    sys.exit(1)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _json_default(obj):
    if isinstance(obj, (set, frozenset)):
        try:
            return sorted(obj)
        except TypeError:
            return sorted(obj, key=repr)
    if isinstance(obj, tuple):
        return list(obj)
    if isinstance(obj, Path):
        return str(obj)
    return repr(obj)


# ---------------------------------------------------------------------------
# Git state
# ---------------------------------------------------------------------------

def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True,
    )
    if result.returncode != 0:
        halt(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def git_status_lines() -> list[str]:
    out = git("status", "--porcelain")
    return [line for line in out.splitlines() if line.strip()]


# ---------------------------------------------------------------------------
# Constants fingerprint
# ---------------------------------------------------------------------------

def collect_ruling_constants() -> dict:
    sys.path.insert(0, str(REPO_ROOT))
    import experiments.tier_engine as tier_engine  # noqa: PLC0415

    constants = {}
    for name in dir(tier_engine):
        if not CONSTANT_NAME_RE.match(name):
            continue
        value = getattr(tier_engine, name)
        if isinstance(value, (Path, re.Pattern)) or callable(value):
            continue
        constants[name] = value
    return dict(sorted(constants.items()))


def constants_fingerprint(constants: dict) -> str:
    blob = json.dumps(constants, sort_keys=True, default=_json_default).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


# ---------------------------------------------------------------------------
# Input pinning
# ---------------------------------------------------------------------------

def pin_inputs() -> dict:
    pins = {}
    for path in PINNED_INPUTS:
        if not path.exists():
            halt(f"pinned input missing: {path.relative_to(REPO_ROOT)} -- cannot snapshot without it")
        rel = str(path.relative_to(REPO_ROOT))
        stat = path.stat()
        pins[rel] = {
            "sha256": sha256_file(path),
            "size": stat.st_size,
            "mtime": stat.st_mtime,
        }
    return pins


# ---------------------------------------------------------------------------
# Gate-result capture
# ---------------------------------------------------------------------------

def run_engine(extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(ENGINE_PATH), *(extra_args or [])]
    return subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)


def capture_gate_results(extra_args: list[str] | None = None) -> tuple[dict, str]:
    proc = run_engine(extra_args)
    combined = proc.stdout + proc.stderr
    pass_count = len(PASS_RE.findall(combined))
    stop_lines = [line for line in combined.splitlines() if STOP_RE.search(line) or line.startswith("STOP —")]
    result = {
        "returncode": proc.returncode,
        "reports_written": proc.returncode == 0,
        "pass_count": pass_count,
        "stop_count": len(stop_lines),
        "stop_lines": stop_lines,
    }
    return result, combined


# ---------------------------------------------------------------------------
# Output caching
# ---------------------------------------------------------------------------

def cache_outputs(dest_dir: Path) -> dict:
    checksums = {}
    for label, src in CACHED_OUTPUT_DIRS:
        if not src.exists():
            continue
        dest = dest_dir / "outputs" / label
        dest.mkdir(parents=True, exist_ok=True)
        for f in sorted(src.rglob("*")):
            if not f.is_file():
                continue
            rel = f.relative_to(src)
            out_path = dest / rel
            out_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, out_path)
            checksums[f"{label}/{rel.as_posix()}"] = sha256_file(f)
    return checksums


def backup_current_outputs() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = BACKUPS_DIR / stamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    cache_outputs(backup_dir)
    return backup_dir


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_create(args: argparse.Namespace) -> None:
    snap_dir = SNAPSHOTS_DIR / args.name

    dirty = git_status_lines()
    print("Strictest-reading choice: any `git status --porcelain` line (staged, "
          "unstaged, or untracked) counts as a dirty worktree.")
    if dirty and not args.force:
        halt(
            "worktree is dirty, refusing to snapshot without --force:\n"
            + "\n".join(f"  {line}" for line in dirty)
        )
    if dirty and args.force:
        print(f"--force: proceeding with a dirty worktree ({len(dirty)} line(s)):")
        for line in dirty:
            print(f"  {line}")

    if snap_dir.exists() and not args.overwrite:
        halt(f"snapshot {args.name!r} already exists at {snap_dir} -- refusing to overwrite without --overwrite")
    if snap_dir.exists() and args.overwrite:
        shutil.rmtree(snap_dir)

    snap_dir.mkdir(parents=True)

    print(f"pinning {len(PINNED_INPUTS)} input file(s)...")
    input_pins = pin_inputs()
    for rel, info in input_pins.items():
        print(f"  {rel}: sha256={info['sha256'][:16]}... size={info['size']:,}")

    print("fingerprinting ruling constants...")
    constants = collect_ruling_constants()
    fp = constants_fingerprint(constants)
    (snap_dir / "constants.json").write_text(
        json.dumps(constants, indent=2, sort_keys=True, default=_json_default), encoding="utf-8"
    )
    print(f"  {len(constants)} constant(s), fingerprint={fp[:16]}...")

    print(f"running gate suite ({ENGINE_PATH.relative_to(REPO_ROOT)}, default anchor panel)...")
    gate_result, combined_log = capture_gate_results()
    (snap_dir / "gates.log").write_text(combined_log, encoding="utf-8")
    print(f"  returncode={gate_result['returncode']} pass={gate_result['pass_count']} stop={gate_result['stop_count']}")
    if gate_result["stop_lines"]:
        for line in gate_result["stop_lines"]:
            print(f"    {line}")

    output_checksums = {}
    if args.cache_outputs:
        if not gate_result["reports_written"]:
            print("--cache-outputs requested but gates failed (reports not written) -- skipping output cache.")
        else:
            print("caching outputs (reports/, viewer/data/)...")
            output_checksums = cache_outputs(snap_dir)
            print(f"  cached {len(output_checksums)} file(s)")

    manifest = {
        "name": args.name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": git("rev-parse", "HEAD"),
        "git_dirty": bool(dirty),
        "forced": bool(dirty and args.force),
        "input_pins": input_pins,
        "constants_fingerprint": fp,
        "constants_count": len(constants),
        "gate_result": gate_result,
        "output_checksums": output_checksums,
        "has_cached_outputs": bool(output_checksums),
    }
    (snap_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(f"\nsnapshot {args.name!r} written to {snap_dir}")
    if gate_result["returncode"] != 0:
        print("NOTE: gate suite did NOT pass clean in this snapshot -- see gates.log", file=sys.stderr)


def cmd_restore(args: argparse.Namespace) -> None:
    snap_dir = SNAPSHOTS_DIR / args.name
    manifest_path = snap_dir / "manifest.json"
    if not manifest_path.exists():
        halt(f"no snapshot named {args.name!r} at {snap_dir}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if not manifest.get("has_cached_outputs"):
        halt(f"snapshot {args.name!r} has no cached outputs -- nothing to restore (was it created with --cache-outputs?)")

    print("taking automatic pre-restore backup of current outputs...")
    backup_dir = backup_current_outputs()
    print(f"  backup: {backup_dir}")

    print(f"restoring cached outputs from snapshot {args.name!r}...")
    outputs_root = snap_dir / "outputs"
    for label, dest in CACHED_OUTPUT_DIRS:
        src = outputs_root / label
        if not src.exists():
            continue
        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True, exist_ok=True)
        for f in sorted(src.rglob("*")):
            if not f.is_file():
                continue
            rel = f.relative_to(src)
            out_path = dest / rel
            out_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, out_path)

    print("verifying post-restore checksums...")
    mismatches = []
    for key, expected_sha in manifest["output_checksums"].items():
        label, rel = key.split("/", 1)
        dest = dict(CACHED_OUTPUT_DIRS)[label] / rel
        if not dest.exists():
            mismatches.append((key, expected_sha, "MISSING"))
            continue
        actual_sha = sha256_file(dest)
        if actual_sha != expected_sha:
            mismatches.append((key, expected_sha, actual_sha))

    if mismatches:
        for key, expected_sha, actual_sha in mismatches:
            print(f"  MISMATCH {key}: expected {expected_sha[:16]}... got {actual_sha if actual_sha == 'MISSING' else actual_sha[:16] + '...'}", file=sys.stderr)
        halt(f"post-restore checksum mismatch on {len(mismatches)} file(s) -- pre-restore backup is at {backup_dir}")

    print(f"restore of {args.name!r} complete, {len(manifest['output_checksums'])} file(s) verified byte-identical.")


def cmd_list(args: argparse.Namespace) -> None:
    if not SNAPSHOTS_DIR.exists():
        print("no snapshots yet.")
        return
    names = sorted(
        p.name for p in SNAPSHOTS_DIR.iterdir()
        if p.is_dir() and p.name != "_pre-restore-backups" and (p / "manifest.json").exists()
    )
    if not names:
        print("no snapshots yet.")
        return
    for name in names:
        manifest = json.loads((SNAPSHOTS_DIR / name / "manifest.json").read_text(encoding="utf-8"))
        gr = manifest["gate_result"]
        gate_state = "PASS" if gr["returncode"] == 0 else "STOP"
        print(
            f"{name}: created={manifest['created_at']} commit={manifest['git_commit'][:10]} "
            f"gates={gate_state} ({gr['pass_count']} pass / {gr['stop_count']} stop) "
            f"outputs_cached={manifest['has_cached_outputs']} constants_fp={manifest['constants_fingerprint'][:12]}..."
        )


def cmd_verify_determinism(args: argparse.Namespace) -> None:
    extra_args = []
    for a in args.anchor or []:
        extra_args += ["--anchor", a]

    print("run 1...")
    result1, log1 = capture_gate_results(extra_args)
    reports_1 = {}
    for label, d in CACHED_OUTPUT_DIRS:
        if d.exists():
            reports_1[label] = {f.relative_to(d): f.read_bytes() for f in d.rglob("*") if f.is_file()}

    print("run 2...")
    result2, log2 = capture_gate_results(extra_args)
    reports_2 = {}
    for label, d in CACHED_OUTPUT_DIRS:
        if d.exists():
            reports_2[label] = {f.relative_to(d): f.read_bytes() for f in d.rglob("*") if f.is_file()}

    ok = True
    if log1 != log2:
        ok = False
        print("STDOUT/STDERR DIFFER between run 1 and run 2:", file=sys.stderr)
        lines1, lines2 = log1.splitlines(), log2.splitlines()
        for i, (a, b) in enumerate(zip(lines1, lines2)):
            if a != b:
                print(f"  first diff at line {i}:\n    run1: {a}\n    run2: {b}", file=sys.stderr)
                break
        if len(lines1) != len(lines2):
            print(f"  line count differs: run1={len(lines1)} run2={len(lines2)}", file=sys.stderr)

    if reports_1.keys() != reports_2.keys():
        ok = False
        print(f"output dir set differs: run1={sorted(reports_1)} run2={sorted(reports_2)}", file=sys.stderr)

    for label in reports_1.keys() & reports_2.keys():
        files1, files2 = reports_1[label], reports_2[label]
        if files1.keys() != files2.keys():
            ok = False
            print(f"{label}: file set differs: {set(files1) ^ set(files2)}", file=sys.stderr)
        for rel in files1.keys() & files2.keys():
            if files1[rel] != files2[rel]:
                ok = False
                print(f"{label}/{rel}: byte content differs between run 1 and run 2", file=sys.stderr)

    if result1["returncode"] != result2["returncode"]:
        ok = False
        print(f"gate returncode differs: run1={result1['returncode']} run2={result2['returncode']}", file=sys.stderr)

    if ok:
        print(f"DETERMINISM VERIFIED — byte-identical stdout/stderr and output files across 2 runs "
              f"(returncode={result1['returncode']}).")
    else:
        halt("determinism check FAILED — see diffs above")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create", help="take a new snapshot")
    p_create.add_argument("name")
    p_create.add_argument("--force", action="store_true", help="allow snapshotting a dirty worktree")
    p_create.add_argument("--overwrite", action="store_true", help="allow overwriting an existing snapshot")
    p_create.add_argument("--cache-outputs", action="store_true", help="cache reports/ + viewer/data/ by checksum")
    p_create.set_defaults(func=cmd_create)

    p_restore = sub.add_parser("restore", help="restore a snapshot's cached outputs")
    p_restore.add_argument("name")
    p_restore.set_defaults(func=cmd_restore)

    p_list = sub.add_parser("list", help="list snapshots")
    p_list.set_defaults(func=cmd_list)

    p_det = sub.add_parser("verify-determinism", help="run the gate suite twice, diff byte-for-byte")
    p_det.add_argument("--anchor", action="append", help="anchor name (repeatable); default is the fixed panel")
    p_det.set_defaults(func=cmd_verify_determinism)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
