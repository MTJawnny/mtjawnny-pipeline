#!/usr/bin/env python3
"""The /2 codebook accessor boundary -- the single load/save/validate surface
for experiments/out/foundry/codebook.json under schema foundry-codebook/2
(B-MIGRATION-DISCOVERY.md sec.10 A1/A13, sec.9 R11).

Schema /2 in one paragraph: an axis entry's `members` (renamed from /1's
`member_oracle_ids`, CDR-11) is a list of member objects sorted by
oracle_id, each carrying a STACK of assertions -- one per support event --
sorted by (class, source_ref). Assertions are append-merge only: nothing in
this module ever modifies or removes an existing assertion except
remove_det_assertions(), which is scoped to rule-derived rows (A8). A
member-level `tier` is present IFF every assertion on it is llm-class
(full-weight human/rule-derived evidence makes the consensus tier moot);
its value follows the ratified lane-aware rule (ADDENDUM-4: intersection
across runs = corroborated, singleton = provisional, scored on the
codebook and codebook-grammar lanes only).

Everything here halts loudly rather than guessing (house style). Every
mutating script in the arc ends with lint() and writes through
write_codebook_atomic().

CLI (AG-CLI-01) -- the home for hand-ratified single-member additions:
  python3 experiments/foundry_codebook.py add-member \\
      --slug rule:some-axis --oracle-id <uuid> --class human \\
      --source-ref captain-cli-2026-08-01 --quote "<oracle clause>"
  python3 experiments/foundry_codebook.py lint
"""
import os
import re
import sys
import json
import shutil
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timezone

# --- C8.5C COMPATIBILITY BOOTSTRAP -- TEMPORARY, AND NOT A LAYOUT API -------
#
# This module used to export `REPO_ROOT`, which made it a SECOND layout
# provider beside the compatibility boundary: two independently derived
# authorities for the same repository. It is now private and may be used for
# exactly one thing -- putting `experiments` on `sys.path` so that
# `import foundry_common` resolves when this file is run as a loose script.
# Nothing can import the boundary before knowing where it is, which is the same
# irreducible knowledge as C8.5A's `src` bootstrap, and it deletes the same way:
# when the package is installed (later C8 step 5) these two lines go, and
# nothing else in this module changes.
#
# The derivation and the inserted directory are UNCHANGED -- only the name and
# its visibility. Every layout value below now comes from the boundary.
_BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_BOOTSTRAP_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402

CODEBOOK_PATH = fc.FOUNDRY_OUT_DIR / "codebook.json"
BACKUPS_DIR = fc.FOUNDRY_OUT_DIR / "backups"
LATEST_ARTIFACT_PATH = fc.DATA_ARTIFACTS_DIR / "latest.json"

# --- C8.5M SEMANTIC FACADE --------------------------------------------------
#
# THE SEMANTIC MODEL LIVES IN `mtj_foundry.codebook` AND NOWHERE ELSE. Every
# schema vocabulary, membership view, assertion primitive and the standing lint
# now have exactly one implementation; what remains here is the transitional
# boundary that keeps 30 legacy importers, the CLI and two monkeypatch seams
# working unchanged while they are repointed in later slices.
#
# WHY THE IMPORT SITS HERE AND NOT HIGHER. `foundry_common` is what puts `src`
# on `sys.path` (its own C8.5A bootstrap), so `mtj_foundry` is unreachable until
# the line above has run. No new bootstrap and no new `sys.path` call are
# needed, and none is added.
#
# TWO SHAPES, AND THE DIFFERENCE IS FAILURE, NOT BEHAVIOUR:
#
#   * a DIRECT ALIAS, where the permanent object is the legacy name. Same
#     object, same identity -- `fcb.LintError is mtj_foundry.codebook.LintError`
#     is what keeps `except fcb.LintError` working in three consumers.
#   * a TRANSLATION WRAPPER, for the exactly three entry points that used to end
#     the process. The permanent library raises; a library may not exit. Each
#     wrapper does nothing but call, return, catch and `fc.halt(str(error))`,
#     and because the permanent error carries the legacy halt's message body
#     verbatim, the stderr line and exit code are byte-identical to the base.
#
# A bare alias for those three would have been the smaller diff and the wrong
# one: `foundry_locality`'s SC8 fixture asserts `SystemExit` from
# `fcb.build_assertion(..., locality="(0, 1)")`, so aliasing it would have
# turned a green ratified control red while the library was behaving correctly.
#
# THE ALIASES ARE MODULE-LEVEL BINDINGS ON PURPOSE. `foundry_locality`'s
# selftest rebinds `fcb.lint` and `fcb.build_assertion` to prove its own
# fixtures can fail. Late binding through this module's globals is what keeps
# those seams live until their dedicated repoint slice re-aims them at an
# injected argument.
from mtj_foundry import codebook as _codebook  # noqa: E402

SCHEMA_V2 = _codebook.SCHEMA_V2
SCHEMA_V1 = _codebook.SCHEMA_V1

CLASSES = _codebook.CLASSES
EVIDENCE_STATUSES = _codebook.EVIDENCE_STATUSES
LANES = _codebook.LANES
AXIS_STATUSES = _codebook.AXIS_STATUSES
SCOREABLE_LANES = _codebook.SCOREABLE_LANES
TIERS = _codebook.TIERS

ASSERTION_KEY_ORDER = _codebook.ASSERTION_KEY_ORDER
MEMBER_KEY_ORDER = _codebook.MEMBER_KEY_ORDER

_UUID_RE = _codebook._UUID_RE
_SOURCE_REF_RES = _codebook._SOURCE_REF_RES
DET_SOURCE_REF_PREFIX = _codebook.DET_SOURCE_REF_PREFIX
SOURCE_REF_FAMILIES = _codebook.SOURCE_REF_FAMILIES
_DATE_RE = _codebook._DATE_RE
AXIS_INVARIANT_EXEMPTIONS = _codebook.AXIS_INVARIANT_EXEMPTIONS

LintError = _codebook.LintError

member_ids = _codebook.member_ids
member_id_set = _codebook.member_id_set
member_by_id = _codebook.member_by_id
expected_tier = _codebook.expected_tier
_reorder_member = _codebook._reorder_member
_assertion_sort_key = _codebook._assertion_sort_key
remove_det_assertions = _codebook.remove_det_assertions
lint = _codebook.lint


def normalize_locality(locality):
    """Legacy failure translation for `mtj_foundry.codebook.normalize_locality`."""
    try:
        return _codebook.normalize_locality(locality)
    except _codebook.LocalityError as error:
        fc.halt(str(error))


def build_assertion(cls: str, source_ref: str, quote: str, corpus_ref: str,
                    evidence_status: str = "quoted", original_lane: str = None,
                    effective_lane: str = None, promotion_reason: str = None,
                    locality=None) -> dict:
    """Legacy failure translation for `mtj_foundry.codebook.build_assertion`."""
    try:
        return _codebook.build_assertion(
            cls, source_ref, quote, corpus_ref, evidence_status,
            original_lane=original_lane, effective_lane=effective_lane,
            promotion_reason=promotion_reason, locality=locality)
    except _codebook.LocalityError as error:
        fc.halt(str(error))


def merge_assertion(entry: dict, oracle_id: str, assertion: dict) -> str:
    """Legacy failure translation for `mtj_foundry.codebook.merge_assertion`."""
    try:
        return _codebook.merge_assertion(entry, oracle_id, assertion)
    except (_codebook.InvalidOracleIdError, _codebook.DuplicateAssertionError) as error:
        fc.halt(str(error))


# --------------------------------------------------------------------------
# corpus reference
# --------------------------------------------------------------------------

def corpus_ref_current() -> str:
    """The corpus snapshot date every quote in this repo is drawn from
    (CDR-09). Read from data/artifacts/latest.json rather than hardcoded so
    it moves with the corpus instead of rotting in a constant."""
    if not LATEST_ARTIFACT_PATH.exists():
        fc.halt(f"{LATEST_ARTIFACT_PATH} not found — cannot establish the corpus snapshot date "
                f"that corpus_ref must record; refusing to guess")
    latest = json.loads(LATEST_ARTIFACT_PATH.read_text(encoding="utf-8"))
    version = latest.get("version")
    if not isinstance(version, str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", version):
        fc.halt(f"{LATEST_ARTIFACT_PATH}: 'version' is {version!r}, expected a YYYY-MM-DD snapshot date")
    return version


# --------------------------------------------------------------------------
# load / id views
# --------------------------------------------------------------------------

def load_codebook(path: Path = None) -> dict:
    """Loads a /2 codebook. Halts on /1 (or anything else) in BOTH directions
    per the discovery's sec.3 recommendation -- /1-era tooling meeting a /2
    file already dies on `set()` of dicts, but that is an accident of Python
    semantics, not a designed failure. This is the designed one."""
    path = Path(path) if path is not None else CODEBOOK_PATH
    if not path.exists():
        fc.halt(f"{path} not found")
    with open(path, "r", encoding="utf-8") as f:
        cb = json.load(f)
    schema = cb.get("schema")
    if schema != SCHEMA_V2:
        if schema == SCHEMA_V1:
            fc.halt(f"{path} is schema {SCHEMA_V1!r} (pre-migration). This loader reads {SCHEMA_V2!r} only "
                    f"— run experiments/foundry_migrate_codebook_v2.py, or use the frozen /1 producer "
                    f"(foundry_reconcile.py) if you genuinely meant the legacy shape")
        fc.halt(f"{path}: unexpected schema {schema!r}, expected {SCHEMA_V2!r}")
    return cb


def lint_or_halt(codebook: dict, path_label: str = "codebook") -> dict:
    try:
        return lint(codebook, path_label)
    except LintError as e:
        fc.halt(str(e))


# --------------------------------------------------------------------------
# atomic write (A13)
# --------------------------------------------------------------------------

def _serialize(codebook: dict) -> str:
    return json.dumps(codebook, indent=2, ensure_ascii=False) + "\n"


def sha256_of(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_codebook_atomic(path: Path, codebook: dict, path_label: str = None) -> str:
    """Temp file -> flush+fsync -> re-read and lint the TEMP -> atomic rename
    over the live file (A13). The live file is never in a half-written state,
    and a file that fails lint never becomes the live file: the temp is what
    gets validated, so a crash between validation and rename leaves the good
    old file in place plus an inert .tmp for a human to notice.

    Returns the sha256 of the file now at `path`."""
    path = Path(path)
    label = path_label or str(path)
    lint_or_halt(codebook, f"{label} (pre-write, in memory)")

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    payload = _serialize(codebook)
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(payload)
        f.flush()
        os.fsync(f.fileno())

    with open(tmp_path, "r", encoding="utf-8") as f:
        readback = json.load(f)
    lint_or_halt(readback, f"{label} (readback of temp)")
    if _serialize(readback) != payload:
        fc.halt(f"{tmp_path}: re-serializing the readback does not reproduce the written bytes — "
                f"non-deterministic serialization, refusing to install this file")

    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    os.replace(tmp_path, path)
    if sha256_of(path) != digest:
        fc.halt(f"{path}: post-rename sha256 does not match the verified temp — filesystem-level "
                f"corruption, do not trust this file")
    return digest


def backup_codebook(tag: str, path: Path = None) -> Path:
    """Timestamped, readback-verified pre-mutation backup. codebook.json is
    gitignored (.gitignore: experiments/out/) -- these backups ARE the rollback
    path, so the readback check is not optional."""
    path = Path(path) if path is not None else CODEBOOK_PATH
    if not path.exists():
        fc.halt(f"{path} not found — nothing to back up")
    cb = json.loads(path.read_text(encoding="utf-8"))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    dest = BACKUPS_DIR / f"codebook.v{cb.get('version', '?')}.{tag}.{stamp}.json"
    shutil.copy2(path, dest)
    src_sha, dst_sha = sha256_of(path), sha256_of(dest)
    if src_sha != dst_sha or path.stat().st_size != dest.stat().st_size:
        fc.halt(f"backup readback mismatch: {path} sha={src_sha} vs {dest} sha={dst_sha} — "
                f"refusing to proceed without a verified rollback point")
    print(f"backup: {dest.name}  size={dest.stat().st_size}  sha256={dst_sha}")
    return dest


# --------------------------------------------------------------------------
# CLI (AG-CLI-01)
# --------------------------------------------------------------------------

def cmd_add_member(args):
    cb = load_codebook(CODEBOOK_PATH)
    axes = cb["axes"]
    slug = args.slug
    if slug not in axes:
        fc.halt(f"axis {slug!r} does not exist in the codebook")
    entry = axes[slug]
    status = entry.get("status")
    if status not in ("active", "deferred"):
        fc.halt(f"axis {slug!r} has status {status!r} — members are only added to active or deferred "
                f"axes; reviving or renaming an axis is a ratification, not a CLI operation")
    if not _UUID_RE.match(args.oracle_id or ""):
        fc.halt(f"{args.oracle_id!r} is not a valid oracle_id (uuid) shape")
    if args.cls not in CLASSES:
        fc.halt(f"--class {args.cls!r} not in {CLASSES}")
    if entry.get("source") == "DET" and args.cls == "rule-derived":
        fc.halt(f"axis {slug!r} is DET-owned: its rule-derived membership is written by "
                f"foundry_det_pass.py from a ratified pattern, never by hand. A human or llm "
                f"assertion on this axis is allowed (A8) — a rule-derived one is not")
    evidence_status = args.evidence_status
    quote = args.quote or ""
    if not quote.strip() and evidence_status != "legacy-captain-seed":
        fc.halt("--quote is empty and --evidence-status is not 'legacy-captain-seed' — "
                "evidence-quote-or-discard; the A3 exemption is for historical captain-seed rows only")
    if args.cls == "llm" and (args.original_lane is None or args.effective_lane is None):
        fc.halt("llm-class assertions require --original-lane and --effective-lane")

    corpus_ref = args.corpus_ref or corpus_ref_current()
    assertion = build_assertion(
        args.cls, args.source_ref, quote, corpus_ref, evidence_status,
        original_lane=args.original_lane, effective_lane=args.effective_lane,
        promotion_reason=args.promotion_reason,
    )

    backup_codebook("pre-cli-add-member")
    outcome = merge_assertion(entry, args.oracle_id, assertion)
    entry.setdefault("history", []).append({
        "batch": args.source_ref, "action": "member_assertion_merged",
        "note": (f"{outcome} member via foundry_codebook.py add-member: class={args.cls}, "
                 f"source_ref={args.source_ref}, oracle_id={args.oracle_id}"
                 + (f" — {args.note}" if args.note else "")),
    })
    digest = write_codebook_atomic(CODEBOOK_PATH, cb, "codebook.json")
    print(f"{slug}: assertion {outcome} on {args.oracle_id} "
          f"({len(entry['members'])} members on this axis)")
    print(f"codebook.json sha256={digest}")


def cmd_lint(args):
    path = Path(args.path) if args.path else CODEBOOK_PATH
    cb = load_codebook(path)
    stats = lint_or_halt(cb, str(path))
    print(f"lint clean: {stats['axes']} axes, {stats['members']} members, "
          f"{stats['assertions']} assertions — {path}")
    for key in stats["exemptions_applied"]:
        print(f"  DECLARED EXEMPTION APPLIED — {key[0]}: {key[1]}")
        print(f"    {AXIS_INVARIANT_EXEMPTIONS[key]}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add-member", help="merge one hand-ratified assertion onto an axis")
    p_add.add_argument("--slug", required=True)
    p_add.add_argument("--oracle-id", required=True)
    p_add.add_argument("--class", dest="cls", required=True, choices=list(CLASSES))
    p_add.add_argument("--source-ref", required=True)
    p_add.add_argument("--quote", default="")
    p_add.add_argument("--corpus-ref", default=None, help="defaults to the current corpus snapshot date")
    p_add.add_argument("--evidence-status", default="quoted", choices=list(EVIDENCE_STATUSES))
    p_add.add_argument("--original-lane", default=None, choices=list(LANES))
    p_add.add_argument("--effective-lane", default=None, choices=list(LANES))
    p_add.add_argument("--promotion-reason", default=None)
    p_add.add_argument("--note", default="")
    p_add.set_defaults(func=cmd_add_member)

    p_lint = sub.add_parser("lint", help="run the standing invariant check")
    p_lint.add_argument("--path", default=None)
    p_lint.set_defaults(func=cmd_lint)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
