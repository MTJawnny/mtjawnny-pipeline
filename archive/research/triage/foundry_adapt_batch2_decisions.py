#!/usr/bin/env python3
"""One-time adapter: sup-triage-decisions-v1 (decisions/batch-2.json, Captain-
ratified per TRIAGE-BATCH-2.md section 10) -> foundry-decisions/1 (what
foundry_reconcile.py consumes). Same schema gap as batch 1's adapter
bridges, but batch 2 has no manufactured-merge-target problem: every MERGE
target this batch is either an existing codebook axis or a KEEP-verdict
sibling within this same batch's own 149 axes, so no rename-carrier
promotion is needed (unlike batch 1's rule:drain-life /
rule:targeted-destruction case).

The one non-mechanical translation needed: rule:cost-reduction-by-graveyard-
lands RENAMEs to a brand new slug (rule:individual-cost-reduction) that
should NOT simply inherit the narrow source axis's original definition
("reduced by graveyard land count") -- it needs the broader Captain-ratified
definition ("reduces its own cost given a condition"). Supplied explicitly
via definition_edit, not left to reconcile.py's fallback.
"""
import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402

DECISIONS_SRC = fc.FOUNDRY_OUT_DIR / "decisions" / "batch-2.json"
REVIEW_SRC = fc.FOUNDRY_OUT_DIR / "review" / "batch-2.json"
ADAPTED_OUT = fc.FOUNDRY_OUT_DIR / "decisions" / "batch-2.foundry-decisions-v1.json"

VERDICT_MAP = {"KEEP": "keep", "KILL": "kill", "MERGE": "merge", "RENAME": "rename"}

# slug -> broader definition_edit for RENAME targets that need one (rather
# than inheriting the source axis's original, narrower definition verbatim).
RENAME_DEFINITION_EDITS = {
    "rule:individual-cost-reduction": (
        "Reduces the caster's own spell's cost given a condition or some other means intrinsic to that "
        "spell (as opposed to a separate permanent reducing OTHER spells' costs, see rule:cost-reduction / "
        "the planned rule:spell-cost-reduction rename). Captain-ratified family split, M5."
    ),
}

# scope values for captain-authored axes (not carried in decisions/batch-2.json's
# captain_authored_axes entries -- assigned here per the same free-text scope
# vocabulary already used elsewhere in the codebook, self/your-stuff/opponent-stuff/etc).
CAPTAIN_AXIS_SCOPE = {
    "rule:grants-ability-at-threshold-self": "self",
    "rule:grants-ability-at-threshold-board": "your-stuff",
    "rule:plus1-counters-matter": "self",
    "rule:targeted-player-damage": "opponent-stuff",
    "rule:targeted-planeswalker-damage": "opponent-stuff",
    "rule:targeted-battle-damage": "opponent-stuff",
}


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
        fc.halt(f"adapter: axis {slug!r} has member_removals but is not a batch-2 axis -- cannot resolve")
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


def main():
    src = json.loads(DECISIONS_SRC.read_text(encoding="utf-8"))
    if src.get("schema") != "sup-triage-decisions-v1":
        fc.halt(f"{DECISIONS_SRC}: unexpected schema {src.get('schema')!r}, expected sup-triage-decisions-v1")

    review = json.loads(REVIEW_SRC.read_text(encoding="utf-8"))
    review_axes_by_slug = {a["slug"]: a for a in review["axes"]}
    review_cards = review["cards"]

    codebook_path = fc.FOUNDRY_OUT_DIR / "codebook.json"
    codebook = json.loads(codebook_path.read_text(encoding="utf-8")) if codebook_path.exists() else {"axes": {}}

    # Sanity: every MERGE target must resolve somewhere (existing codebook axis
    # or a KEEP-verdict sibling within this batch) -- halt rather than silently
    # let reconcile.py discover the gap itself with a less-informative message.
    src_axes_by_slug = {a["slug"]: a for a in src["axes"]}
    for entry in src["axes"]:
        if entry["verdict"] != "MERGE":
            continue
        target = entry["merge_into"]
        if target not in review_axes_by_slug and target not in codebook["axes"]:
            fc.halt(f"adapter: MERGE target {target!r} (from {entry['slug']!r}) does not exist as a batch-2 "
                     f"axis or an existing codebook axis -- would need a manufactured-carrier workaround "
                     f"(see batch-1's adapter for that pattern), not expected for batch 2")

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
            new_slug = entry["rename_to"]
            dec["new_slug"] = new_slug
            if new_slug in RENAME_DEFINITION_EDITS:
                dec["definition_edit"] = RENAME_DEFINITION_EDITS[new_slug]
        if removed:
            dec["removed_members"] = removed
        out_axes[slug] = dec

    # captain_authored_axes -> captain_axes, example_cards (names) -> seed_members (oracle_ids)
    cards, name_index = fc.load_corpus()
    captain_axes = []
    for ca in src["captain_authored_axes"]:
        slug = ca["slug"]
        scope = CAPTAIN_AXIS_SCOPE.get(slug)
        if scope is None:
            fc.halt(f"adapter: no scope mapping defined for captain-authored axis {slug!r}")
        seed_members = []
        for name in ca.get("example_cards", []):
            oid = fc.resolve_name(name, cards, name_index)
            seed_members.append(oid)
        captain_axes.append({
            "slug": slug,
            "definition": ca["definition"],
            "scope": scope,
            "seed_members": seed_members,
        })

    adapted = {
        "schema": "foundry-decisions/1",
        "batch": src["batch"],
        "axes": out_axes,
        "captain_axes": captain_axes,
        "_provenance": {
            "adapted_from": "experiments/out/foundry/decisions/batch-2.json",
            "adapter_script": "experiments/foundry_adapt_batch2_decisions.py",
        },
        "_not_carried_by_reconcile_py": {
            "override_spotcheck": src.get("override_spotcheck"),
            "ledger_candidates_carry_forward": src.get("ledger_candidates_carry_forward"),
            "new_rulings": src.get("new_rulings"),
            "punch_list": src.get("punch_list"),
            "other_lane_promotions": src.get("other_lane", {}).get("promotions"),
            "note": "these fields have no home in foundry_reconcile.py's schema; handled by separate "
                    "triage-emit steps (ledger doc, protocol standing-rules update, batch-3 assembly "
                    "targeting) rather than dropped",
        },
    }
    fc.write_json(ADAPTED_OUT, adapted)
    print(f"wrote {ADAPTED_OUT}")
    print(f"axes: {len(out_axes)}  captain_axes: {len(captain_axes)}")


if __name__ == "__main__":
    main()
