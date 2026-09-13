#!/usr/bin/env python3
"""Spec-driven membership mover -- the executor for ratified re-homing.

Built reusable because the member-by-member re-audit will need it repeatedly.
Every move is declared in a JSON spec; the script never decides anything.

Gates, all enforced before a byte is written:
  * every source axis exists and is active
  * every named oracle_id is actually a member of its source
  * no oracle_id is routed to two destinations in one spec
  * a new axis may not collide with an existing slug
  * MEMBER CONSERVATION -- total member count across all axes is unchanged
    unless the spec explicitly declares `drops`. Members move; they are not
    created or lost.
  * determinism x2 byte-identical, then atomic write with temp re-lint

Members carry their assertions -- and therefore their evidence quotes --
verbatim. Nothing is re-evidenced by a move.

Spec shape:
{
  "batch": "...", "ruling": "docs/....md",
  "new_axes": {"rule:x": {"definition": "...", "scope": "...", "source": "CAPTAIN"}},
  "moves": [{"from": "rule:a", "to": "rule:x", "members": ["oid", ...]}],
  "definition_edits": {"rule:a": "corrected definition text"},
  "scope_edits": {"rule:a": "self"}
}

Usage:
  python3 experiments/foundry_membership_move.py --spec <file.json> --dry-run
  python3 experiments/foundry_membership_move.py --spec <file.json> --execute
"""
import sys
import copy
import json
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402
import foundry_codebook as fcb  # noqa: E402


# S11: the membership SEMANTICS -- every declared operation, its preconditions,
# and the member-conservation arithmetic -- are `mtj_foundry.codebook_membership`'s.
# This executor keeps the spec read, the pre/post lint, the determinism ×2 gate,
# the report lines, the dry-run/execute switch and the atomic write, and turns
# the owner's typed refusal back into the historic `STOP — …` line.
from mtj_foundry import codebook_membership as _membership  # noqa: E402


def apply_spec(codebook: dict, spec: dict) -> dict:
    """Apply `spec` to a deep copy of `codebook` (see `codebook_membership.apply_spec`)."""
    try:
        return _membership.apply_spec(codebook, spec)
    except _membership.MembershipSpecError as error:
        fc.halt(str(error))


def total_members(cb: dict) -> int:
    return _membership.total_members(cb)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--execute", action="store_true")
    args = ap.parse_args()

    spec = json.loads(Path(args.spec).read_text())
    cb = fcb.load_codebook()
    fcb.lint_or_halt(cb, "codebook (pre-move)")

    once = fcb._serialize(apply_spec(cb, spec))
    twice = fcb._serialize(apply_spec(cb, spec))
    if once != twice:
        fc.halt("determinism gate FAILED — two applications of the spec differ")
    print(f"determinism x2 byte-identical ({len(once)} bytes)")

    result = apply_spec(cb, spec)
    fcb.lint_or_halt(result, "codebook (post-move, in memory)")

    # Expected delta is derived from the DECLARED operations, so any change the
    # spec did not ask for is caught (`codebook_membership.member_conservation`).
    c = _membership.member_conservation(cb, result, spec)
    before, after, expected = c["before"], c["after"], c["expected"]
    n_adds, n_drops = c["adds"], c["drops"]
    n_rename_copies, n_merge_dupes = c["rename_copies"], c["merge_dupes"]
    if after != expected:
        fc.halt(f"MEMBER CONSERVATION FAILED: {before} -> {after}, expected {expected} "
                f"(+{n_adds} adds -{n_drops} drops +{n_rename_copies} rename-tombstone copies "
                f"-{n_merge_dupes} merge dupes). Every change must be declared.")
    print(f"member conservation OK ({before} -> {after}: +{n_adds} adds, -{n_drops} drops, "
          f"+{n_rename_copies} rename copies, -{n_merge_dupes} merge dupes)")

    print()
    for slug in sorted(spec.get("new_axes", {})):
        print(f"  + {slug}: {len(result['axes'][slug]['members'])} members "
              f"(scope={result['axes'][slug]['scope']})")
    for mv in spec.get("moves", []):
        # A move's source may itself have been created earlier in this spec (by
        # a rename), so it need not exist in the pre-state.
        was = cb["axes"].get(mv["from"], {}).get("members")
        print(f"  {mv['from']}: {len(was) if was is not None else '(new this spec)'} -> "
              f"{len(result['axes'][mv['from']]['members'])} members")
    a_b = sum(1 for e in cb["axes"].values() if e.get("status") == "active")
    a_a = sum(1 for e in result["axes"].values() if e.get("status") == "active")
    print(f"\nactive axes: {a_b} -> {a_a}")

    if args.dry_run:
        print("\nDRY RUN — nothing written.")
        return

    path = fcb.CODEBOOK_PATH
    prev = fcb.sha256_of(path)
    digest = fcb.write_codebook_atomic(path, result, "codebook")
    print(f"\nwrote {path}\n  sha256 before: {prev}\n  sha256 after : {digest}")


if __name__ == "__main__":
    main()
