#!/usr/bin/env python3
"""One-time adapter: sup-triage-decisions-v1 (decisions/batch-4.json, Captain-
ratified per TRIAGE-BATCH-4.md section 10) -> foundry-decisions/1 (what
foundry_reconcile.py consumes). Same schema gap as batches 2-3's adapters
bridge.

Two things new this batch that batches 1-3 never needed:
- DEFER verdict (D5): maps straight through, reconcile.py was extended with
  a "defer" branch this batch to support it.
- member_additions (D2, D3): cross-axis card additions where the card is
  NOT one of that axis's own batch-4 members (Item Crate reassigned to
  rule:direct-damage-any-target; Breya, Etherium Shaper added to
  rule:targeted-planeswalker-damage per the M8 mixed-target rule). Resolved
  by NAME against the batch-4 review cards dict (searched across ALL axes'
  members, not just the target axis's own members, since by definition
  these cards are members of some OTHER axis this batch) and passed through
  to reconcile.py's own new member_additions handling.
"""
import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402

DECISIONS_SRC = fc.FOUNDRY_OUT_DIR / "decisions" / "batch-4.json"
REVIEW_SRC = fc.FOUNDRY_OUT_DIR / "review" / "batch-4.json"
ADAPTED_OUT = fc.FOUNDRY_OUT_DIR / "decisions" / "batch-4.foundry-decisions-v1.json"

VERDICT_MAP = {"KEEP": "keep", "KILL": "kill", "MERGE": "merge", "RENAME": "rename", "DEFER": "defer"}


def fold_note(entry: dict) -> str:
    parts = []
    if entry.get("reason"):
        parts.append(entry["reason"])
    if entry.get("notes"):
        parts.append(entry["notes"])
    if entry.get("params"):
        parts.append(f"params: {json.dumps(entry['params'])}")
    return " | ".join(parts)


def resolve_removed_members(slug: str, names: list, review_axes_by_slug: dict, review_cards: dict) -> list:
    axis = review_axes_by_slug.get(slug)
    if axis is None:
        fc.halt(f"adapter: axis {slug!r} has member_removals but is not a batch-4 axis -- cannot resolve")
    name_to_oid = {}
    for m in axis["members"]:
        card = review_cards.get(m["oracle_id"])
        if card is None:
            fc.halt(f"adapter: member {m['oracle_id']} of {slug!r} not found in review cards dict")
        name_to_oid.setdefault(card["name"], []).append(m["oracle_id"])
    out = []
    for name in names:
        oids = name_to_oid.get(name)
        if not oids:
            fc.halt(f"adapter: member_removal {name!r} not found among {slug!r}'s own members -- HALT rather than guess")
        if len(oids) > 1:
            fc.halt(f"adapter: member_removal {name!r} matched {len(oids)} entries in {slug!r} -- ambiguous, resolve by hand")
        out.append({"oracle_id": oids[0]})
    return out


def resolve_member_addition_name(name: str, review_cards: dict) -> str:
    """member_additions names a card that is a member of some OTHER axis this
    batch, not necessarily the target axis -- search the whole review cards
    dict by name (batch-4's card pool has no duplicate display names; the
    corpus's own known duplicate-name shape, per foundry_common.resolve_name,
    is a different concern -- this is scoped to the ~1,016 cards actually in
    this batch's review JSON)."""
    matches = [oid for oid, c in review_cards.items() if c["name"] == name]
    if len(matches) == 0:
        fc.halt(f"adapter: member_addition {name!r} not found among batch-4's review cards")
    if len(matches) > 1:
        fc.halt(f"adapter: member_addition {name!r} matched {len(matches)} cards in batch-4 review -- ambiguous")
    return matches[0]


def main():
    src = json.loads(DECISIONS_SRC.read_text(encoding="utf-8"))
    if src.get("schema") != "sup-triage-decisions-v1":
        fc.halt(f"{DECISIONS_SRC}: unexpected schema {src.get('schema')!r}, expected sup-triage-decisions-v1")

    review = json.loads(REVIEW_SRC.read_text(encoding="utf-8"))
    review_axes_by_slug = {a["slug"]: a for a in review["axes"]}
    review_cards = review["cards"]

    codebook_path = fc.FOUNDRY_OUT_DIR / "codebook.json"
    codebook = json.loads(codebook_path.read_text(encoding="utf-8")) if codebook_path.exists() else {"axes": {}}

    for entry in src["axes"]:
        if entry["verdict"] != "MERGE":
            continue
        target = entry["merge_into"]
        if target not in review_axes_by_slug and target not in codebook["axes"]:
            fc.halt(f"adapter: MERGE target {target!r} (from {entry['slug']!r}) does not exist as a batch-4 "
                     f"axis or an existing codebook axis")

    out_axes = {}
    for entry in src["axes"]:
        slug = entry["slug"]
        verdict = VERDICT_MAP.get(entry["verdict"])
        if verdict is None:
            fc.halt(f"adapter: axis {slug!r} has unrecognized verdict {entry['verdict']!r}")

        note = fold_note(entry)
        removed = None
        if entry.get("member_removals"):
            removed = resolve_removed_members(slug, entry["member_removals"], review_axes_by_slug, review_cards)

        dec = {"verdict": verdict, "note": note}
        if verdict == "merge":
            dec["merge_into"] = entry["merge_into"]
        elif verdict == "rename":
            dec["new_slug"] = entry["rename_to"]
        if removed:
            dec["removed_members"] = removed
        out_axes[slug] = dec

    member_additions_out = []
    for add in src.get("member_additions", []):
        oid = resolve_member_addition_name(add["name"], review_cards)
        member_additions_out.append({
            "slug": add["slug"],
            "oracle_id": oid,
            "name": add["name"],
            "note": add.get("reason", ""),
        })

    adapted = {
        "schema": "foundry-decisions/1",
        "batch": src["batch"],
        "axes": out_axes,
        "captain_axes": [],
        "member_additions": member_additions_out,
        "_provenance": {
            "adapted_from": "experiments/out/foundry/decisions/batch-4.json",
            "adapter_script": "experiments/foundry_adapt_batch4_decisions.py",
        },
        "_not_carried_by_reconcile_py": {
            "override_spotcheck": src.get("override_spotcheck"),
            "ledger_candidates_carry_forward": src.get("ledger_candidates_carry_forward"),
            "new_rulings": src.get("new_rulings"),
            "punch_list": src.get("punch_list"),
            "other_lane_promotions": src.get("other_lane", {}).get("promotions"),
            "note": "these fields have no home in foundry_reconcile.py's schema; handled by separate "
                    "triage-emit steps (ledger doc, batch-5 assembly targeting) rather than dropped",
        },
    }
    fc.write_json(ADAPTED_OUT, adapted)
    print(f"wrote {ADAPTED_OUT}")
    print(f"axes: {len(out_axes)}  captain_axes: 0  member_additions: {len(member_additions_out)}")


if __name__ == "__main__":
    main()
