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
  "definition_edits": {"rule:a": "corrected definition text"}
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


def apply_spec(codebook: dict, spec: dict) -> dict:
    cb = copy.deepcopy(codebook)
    axes = cb["axes"]
    batch = spec["batch"]
    ruling = spec.get("ruling", "")

    # --- create declared new axes -------------------------------------------
    for slug, meta in sorted(spec.get("new_axes", {}).items()):
        if slug in axes:
            fc.halt(f"{slug}: already exists — collision with a declared new axis")
        axes[slug] = {
            "definition": meta["definition"],
            "scope": meta["scope"],
            "source": meta.get("source", "CAPTAIN"),
            "parameterized": bool(meta.get("parameterized", False)),
            "members": [],
            "status": "active",
            "merged_into": None,
            "history": [{"batch": batch, "action": "created",
                         "note": meta.get("note", "") + (f" {ruling}" if ruling else "")}],
        }

    # --- validate every move before mutating any of them --------------------
    routed = {}
    for mv in spec.get("moves", []):
        src, dst = mv["from"], mv["to"]
        if src not in axes:
            fc.halt(f"{src}: source axis not in the codebook")
        if axes[src].get("status") != "active":
            fc.halt(f"{src}: status is {axes[src].get('status')!r}, expected 'active'")
        if dst not in axes:
            fc.halt(f"{dst}: destination axis does not exist and is not declared in new_axes")
        have = {m["oracle_id"] for m in axes[src].get("members", [])}
        for oid in mv["members"]:
            if oid not in have:
                fc.halt(f"{oid}: not a member of {src} — the spec and live state disagree")
            key = (src, oid)
            if key in routed:
                fc.halt(f"{oid}: routed twice out of {src}")
            routed[key] = dst

    # --- apply --------------------------------------------------------------
    for mv in spec.get("moves", []):
        src, dst = mv["from"], mv["to"]
        ids = set(mv["members"])
        by_id = {m["oracle_id"]: m for m in axes[src]["members"]}
        carried = [copy.deepcopy(by_id[o]) for o in sorted(ids)]

        existing = {m["oracle_id"] for m in axes[dst]["members"]}
        for m in carried:
            if m["oracle_id"] in existing:
                fc.halt(f"{m['oracle_id']}: already a member of destination {dst}")
        axes[dst]["members"] = sorted(axes[dst]["members"] + carried,
                                      key=lambda m: m["oracle_id"])
        axes[dst].setdefault("history", []).append(
            {"batch": batch, "action": "members_received",
             "note": f"received {len(carried)} member(s) from {src}: {mv.get('why', '')} {ruling}".strip()})

        axes[src]["members"] = [m for m in axes[src]["members"] if m["oracle_id"] not in ids]
        axes[src].setdefault("history", []).append(
            {"batch": batch, "action": "members_moved",
             "note": f"moved {len(carried)} member(s) to {dst}: {mv.get('why', '')} {ruling}".strip()})

    # --- definition corrections ---------------------------------------------
    for slug, new_def in sorted(spec.get("definition_edits", {}).items()):
        if slug not in axes:
            fc.halt(f"{slug}: definition_edits names an axis not in the codebook")
        axes[slug]["definition"] = new_def
        axes[slug].setdefault("history", []).append(
            {"batch": batch, "action": "definition_corrected",
             "note": f"definition corrected. {ruling}".strip()})

    return cb


def total_members(cb: dict) -> int:
    return sum(len(e.get("members", [])) for e in cb["axes"].values())


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

    before, after = total_members(cb), total_members(result)
    if before != after:
        fc.halt(f"MEMBER CONSERVATION FAILED: {before} -> {after}. Members move; they are "
                f"never created or lost by a re-homing.")
    print(f"member conservation OK ({before} unchanged)")

    print()
    for slug in sorted(spec.get("new_axes", {})):
        print(f"  + {slug}: {len(result['axes'][slug]['members'])} members "
              f"(scope={result['axes'][slug]['scope']})")
    for mv in spec.get("moves", []):
        print(f"  {mv['from']}: {len(cb['axes'][mv['from']]['members'])} -> "
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
