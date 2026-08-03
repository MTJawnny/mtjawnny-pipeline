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

    # --- renames -------------------------------------------------------------
    # CDR-09 precedent: the old slug becomes a `renamed` tombstone that RETAINS
    # its members, and the new slug carries them forward. Applied before moves
    # so a move may target a freshly renamed axis.
    for old, meta in sorted(spec.get("renames", {}).items()):
        if old not in axes:
            fc.halt(f"{old}: rename source not in the codebook")
        new = meta["to"]
        if new in axes:
            fc.halt(f"{old} -> {new}: rename target already exists — collision")
        entry = axes[old]
        new_entry = copy.deepcopy(entry)
        new_entry["status"] = "active"
        new_entry["merged_into"] = None
        new_entry.pop("renamed_to", None)
        if meta.get("definition"):
            new_entry["definition"] = meta["definition"]
        new_entry["history"] = list(entry.get("history", [])) + [
            {"batch": batch, "action": "created_via_rename",
             "note": f"renamed from {old}: {meta.get('why','')} {ruling}".strip()}]
        axes[new] = new_entry
        entry["status"] = "renamed"
        entry["renamed_to"] = new
        entry["merged_into"] = None
        entry.setdefault("history", []).append(
            {"batch": batch, "action": "renamed",
             "note": f"renamed to {new}: {meta.get('why','')} {ruling}".strip()})

    # --- merges --------------------------------------------------------------
    # Members RELOCATE to the target and the source is emptied, unlike a rename
    # tombstone: a merged axis's members live on the surviving slug, so keeping
    # a copy on the source would double-count them.
    for mg in spec.get("merges", []):
        src, dst = mg["from"], mg["to"]
        for s in (src, dst):
            if s not in axes:
                fc.halt(f"{s}: merge axis not in the codebook")
        have = {m["oracle_id"] for m in axes[dst]["members"]}
        moving = [m for m in axes[src]["members"] if m["oracle_id"] not in have]
        axes[dst]["members"] = sorted(axes[dst]["members"] + [copy.deepcopy(m) for m in moving],
                                      key=lambda m: m["oracle_id"])
        axes[dst].setdefault("history", []).append(
            {"batch": batch, "action": "absorbed_merge",
             "note": f"absorbed {len(moving)} member(s) from {src}: {mg.get('why','')} {ruling}".strip()})
        axes[src]["members"] = []
        axes[src]["status"] = "merged"
        axes[src]["merged_into"] = dst
        axes[src].setdefault("history", []).append(
            {"batch": batch, "action": "merged",
             "note": f"merged into {dst}: {mg.get('why','')} {ruling}".strip()})

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

    # --- multi-axis additions ------------------------------------------------
    # Captain-ratified 2026-08-02: a card holds membership on EVERY axis it
    # genuinely satisfies. An `add` copies a card onto an additional axis
    # without removing it from where it already lives, so it legitimately RAISES
    # the total member count -- the conservation gate accounts for these
    # explicitly rather than treating the increase as corruption.
    for ad in spec.get("adds", []):
        src, dst, oid = ad["from"], ad["to"], ad["member"]
        if src not in axes:
            fc.halt(f"{src}: add source axis not in the codebook")
        if dst not in axes:
            fc.halt(f"{dst}: add destination does not exist and is not declared in new_axes")
        by_id = {m["oracle_id"]: m for m in axes[src].get("members", [])}
        if oid not in by_id:
            fc.halt(f"{oid}: not a member of {src} — cannot copy a membership that is not there")
        if any(m["oracle_id"] == oid for m in axes[dst]["members"]):
            fc.halt(f"{oid}: already a member of {dst}")
        # Evidence does NOT travel unchanged. The source quote may be a FRAGMENT
        # scoped to the source axis's claim, in which case it does not prove the
        # destination's claim -- caught 2026-08-02 in the tier-1 re-audit, where
        # Blizzard Specter arrived on a bounce axis carrying "That player
        # discards a card." An add must state the quote that proves ITS axis.
        carried = copy.deepcopy(by_id[oid])
        if "quote" not in ad:
            fc.halt(f"add {oid} -> {dst}: no `quote` given. The source quote proves the "
                    f"SOURCE axis's claim and may not prove this one; state the evidence "
                    f"for this axis explicitly (evidence-quote-or-discard).")
        for a in carried.get("assertions", []):
            a["quote"] = ad["quote"]
            a["source_ref"] = batch
        axes[dst]["members"] = sorted(axes[dst]["members"] + [carried],
                                      key=lambda m: m["oracle_id"])
        axes[dst].setdefault("history", []).append(
            {"batch": batch, "action": "member_added_multi_axis",
             "note": f"also a member of {src}; multi-axis membership. "
                     f"{ad.get('why', '')} {ruling}".strip()})

    # --- drops ---------------------------------------------------------------
    # Removing a membership that was never true. Declared explicitly because it
    # LOWERS the member count, and a silent decrease is indistinguishable from
    # corruption (the sweep's membership-shrank alarm exists for that reason).
    for dr in spec.get("drops", []):
        slug, oid = dr["from"], dr["member"]
        if slug not in axes:
            fc.halt(f"{slug}: drop source not in the codebook")
        before_n = len(axes[slug]["members"])
        axes[slug]["members"] = [m for m in axes[slug]["members"] if m["oracle_id"] != oid]
        if len(axes[slug]["members"]) == before_n:
            fc.halt(f"{oid}: not a member of {slug} — nothing to drop")
        axes[slug].setdefault("history", []).append(
            {"batch": batch, "action": "member_dropped",
             "note": f"dropped {oid}: {dr.get('why','')} {ruling}".strip()})

    # --- assertion quote corrections ----------------------------------------
    # An assignment whose quote does not prove its axis is unevidenced, whatever
    # else is true of it. The re-audit needs this constantly.
    for slug, per_card in sorted(spec.get("quote_edits", {}).items()):
        if slug not in axes:
            fc.halt(f"{slug}: quote_edits names an axis not in the codebook")
        by_id = {m["oracle_id"]: m for m in axes[slug].get("members", [])}
        for oid, new_quote in sorted(per_card.items()):
            if oid not in by_id:
                fc.halt(f"{oid}: quote_edits names a non-member of {slug}")
            if not new_quote.strip():
                fc.halt(f"{oid} on {slug}: refusing to set an empty quote")
            for a in by_id[oid].get("assertions", []):
                a["quote"] = new_quote
                if a.get("evidence_status") == "legacy-captain-seed":
                    a["evidence_status"] = "quoted"
        axes[slug].setdefault("history", []).append(
            {"batch": batch, "action": "quotes_corrected",
             "note": f"corrected evidence quote(s) for {len(per_card)} member(s). {ruling}".strip()})

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

    # Expected delta is derived from the DECLARED operations, so any change the
    # spec did not ask for is caught. Renames retain members on the tombstone
    # (CDR-09 precedent) and therefore add a copy; merges relocate and are
    # neutral except for members the target already had.
    before, after = total_members(cb), total_members(result)
    n_adds, n_drops = len(spec.get("adds", [])), len(spec.get("drops", []))
    n_rename_copies = sum(len(cb["axes"][old].get("members", []))
                          for old in spec.get("renames", {}) if old in cb["axes"])
    n_merge_dupes = 0
    for mg in spec.get("merges", []):
        if mg["from"] in cb["axes"] and mg["to"] in cb["axes"]:
            have = {m["oracle_id"] for m in cb["axes"][mg["to"]]["members"]}
            n_merge_dupes += sum(1 for m in cb["axes"][mg["from"]]["members"]
                                 if m["oracle_id"] in have)
    expected = before + n_adds - n_drops + n_rename_copies - n_merge_dupes
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
