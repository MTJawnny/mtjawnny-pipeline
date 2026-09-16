#!/usr/bin/env python3
"""One-time adapter: sup-triage-decisions-v1 (decisions/batch-3.json, Captain-
ratified per TRIAGE-BATCH-3.md) -> foundry-decisions/1 (what
foundry_reconcile.py consumes). Same schema gap as batch 2's adapter bridges.

No manufactured-merge-target problem this batch: both MERGE targets
(rule:grants-creature-type, rule:sacrifice-for-card-draw) are either a
KEEP-verdict sibling within this same batch's own 158 axes or an existing
codebook axis.

One RENAME this batch (rule:stun-counter-lockdown -> rule:stun-counter) --
no definition_edit needed, the concept is unchanged, only the name and its
new parent (rule:lockdown, tracked separately in PARENT-TREE-CANDIDATES.md,
not in the codebook) are new.

captain_authored_axes -> captain_axes needs a scope assignment per slug
(not carried in decisions/batch-3.json's captain_authored_axes entries),
same as batch 2's adapter.
"""
import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402

DECISIONS_SRC = fc.FOUNDRY_OUT_DIR / "decisions" / "batch-3.json"
REVIEW_SRC = fc.FOUNDRY_OUT_DIR / "review" / "batch-3.json"
ADAPTED_OUT = fc.FOUNDRY_OUT_DIR / "decisions" / "batch-3.foundry-decisions-v1.json"

VERDICT_MAP = {"KEEP": "keep", "KILL": "kill", "MERGE": "merge", "RENAME": "rename"}

CAPTAIN_AXIS_SCOPE = {
    "rule:temporary-keyword-grant": "your-stuff",
    "rule:gives-energy-counters-immediately": "self",
    "rule:gives-energy-counters-condition": "self",
    "rule:energy-outlet-condition": "self",
    "rule:energy-outlet-infinite": "self",
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
        fc.halt(f"adapter: axis {slug!r} has member_removals but is not a batch-3 axis -- cannot resolve")
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
    for entry in src["axes"]:
        if entry["verdict"] != "MERGE":
            continue
        target = entry["merge_into"]
        if target not in review_axes_by_slug and target not in codebook["axes"]:
            fc.halt(f"adapter: MERGE target {target!r} (from {entry['slug']!r}) does not exist as a batch-3 "
                     f"axis or an existing codebook axis -- would need a manufactured-carrier workaround "
                     f"(see batch-1's adapter for that pattern), not expected for batch 3")

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
            "adapted_from": "experiments/out/foundry/decisions/batch-3.json",
            "adapter_script": "experiments/foundry_adapt_batch3_decisions.py",
        },
        "_not_carried_by_reconcile_py": {
            "override_spotcheck": src.get("override_spotcheck"),
            "ledger_candidates_carry_forward": src.get("ledger_candidates_carry_forward"),
            "new_rulings": src.get("new_rulings"),
            "punch_list": src.get("punch_list"),
            "other_lane_promotions": src.get("other_lane", {}).get("promotions"),
            "note": "these fields have no home in foundry_reconcile.py's schema; handled by separate "
                    "triage-emit steps (ledger doc, batch-4 assembly targeting) rather than dropped",
        },
    }
    fc.write_json(ADAPTED_OUT, adapted)
    print(f"wrote {ADAPTED_OUT}")
    print(f"axes: {len(out_axes)}  captain_axes: {len(captain_axes)}")


if __name__ == "__main__":
    main()
