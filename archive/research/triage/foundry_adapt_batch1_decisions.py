#!/usr/bin/env python3
"""One-time adapter: sup-triage-decisions-v1 (decisions/batch-1.json, the
Captain-ratified authoritative record per SUP-TRIAGE-PROTOCOL's BATCH-1
PROVENANCE NOTE) -> foundry-decisions/1 (what foundry_reconcile.py consumes).

This is NOT a general-purpose translator: batch-1 predates the annotation
convention, so its decisions file uses its own shape (list of axes,
UPPERCASE verdicts, rename_to, member_removals by card NAME, params dicts,
captain_authored_axes by example-card NAME). Batches 2+ should emit
foundry-decisions/1 directly at PARSE time and won't need this script.

Two structural gaps between the two schemas, resolved explicitly here
rather than silently:

1. MERGE-target axes that are not among the batch's own 105 axis slugs
   (rule:drain-life, rule:targeted-destruction) have no "create" verdict
   in foundry_reconcile.py's vocabulary (only keep/kill/merge/rename).
   Fix: promote the largest-member source axis in each group to a RENAME
   into the new slug (with an explicit definition_edit capturing Captain's
   merged-concept prose from TRIAGE-BATCH-1.md), and MERGE the rest into
   it. This is a bookkeeping choice only -- the final member set is a
   union and is identical regardless of which source axis is nominally
   the "carrier". Flagged in the diff report for Captain's review.
2. Two OTHER-lane absorptions (Time Vault -> rule:enters-tapped,
   Felidar Sovereign -> rule:alternate-win-condition) have no mechanism
   in foundry_reconcile.py at all (it only ever reads batch["axes"], never
   batch["other_lane"]). Left OUT of this adapted file; applied as an
   explicit, logged post-patch to codebook.json after reconcile runs.
"""
import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402

DECISIONS_SRC = fc.FOUNDRY_OUT_DIR / "decisions" / "batch-1.json"
REVIEW_SRC = fc.FOUNDRY_OUT_DIR / "review" / "batch-1.json"
ADAPTED_OUT = fc.FOUNDRY_OUT_DIR / "decisions" / "batch-1.foundry-decisions-v1.json"

VERDICT_MAP = {"KEEP": "keep", "KILL": "kill", "MERGE": "merge", "RENAME": "rename"}

# Group -> (definition_edit for the manufactured slug, source axes in the
# order Captain's TRIAGE-BATCH-1.md ratified them). The first source axis
# in each list is promoted RENAME-carrier (largest member count); the rest
# MERGE into it.
MANUFACTURED_TARGETS = {
    "rule:drain-life": {
        "carrier": "rule:drain-life-effect",
        "others": ["rule:lifegain-tied-to-drain", "rule:opponent-life-loss"],
        "definition_edit": (
            "Causes an opponent to lose life while the caster/controller gains "
            "an equivalent (or otherwise tied) amount of life -- the drain-life "
            "family (Exsanguinate, Hydra's Growth-style infiltration, Treacherous "
            "Greed, Exquisite Blood, Zulaport Cutthroat's drain face). Sanguine "
            "Bond is deliberately excluded (lifegain-payoff, not drain; see "
            "rule:drain-life-effect's member_removals)."
        ),
    },
    "rule:targeted-destruction": {
        "carrier": "rule:unconditional-permanent-removal",
        "others": [
            "rule:targeted-permanent-destruction",
            "rule:targeted-artifact-removal",
            "rule:unconditional-destroy-effect",
        ],
        "definition_edit": (
            "Destroys a target permanent; parameterized by type (creature / "
            "artifact / artifact-or-enchantment / permanent / nonland-MV<=N) "
            "and scope (e.g. Vandalblast's 'you don't control'). "
            "unconditional-exile-removal (now rule:targeted-exile) stays a "
            "separate axis -- exile vs. destroy is a real functional boundary "
            "(indestructible interaction)."
        ),
    },
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
        fc.halt(f"adapter: axis {slug!r} has member_removals but is not a batch-1 axis -- cannot resolve")
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

    src_axes_by_slug = {a["slug"]: a for a in src["axes"]}

    # Sanity: every manufactured-target source slug must actually be a
    # MERGE decision pointing at the manufactured target, and the carrier
    # must not already diverge (halt rather than silently override intent).
    for target, spec in MANUFACTURED_TARGETS.items():
        for slug in [spec["carrier"]] + spec["others"]:
            dec = src_axes_by_slug.get(slug)
            if dec is None:
                fc.halt(f"adapter: expected {slug!r} in decisions axes for manufactured target {target!r}, not found")
            if dec["verdict"] != "MERGE" or dec.get("merge_into") != target:
                fc.halt(f"adapter: {slug!r} does not have verdict=MERGE merge_into={target!r} as expected (got {dec})")
        if target in review_axes_by_slug:
            fc.halt(f"adapter: manufactured target {target!r} unexpectedly already exists as a batch-1 axis -- adapter logic is stale")

    out_axes = {}
    manufactured_carrier_slugs = {spec["carrier"]: target for target, spec in MANUFACTURED_TARGETS.items()}
    manufactured_other_slugs = {s: t for t, spec in MANUFACTURED_TARGETS.items() for s in spec["others"]}

    for entry in src["axes"]:
        slug = entry["slug"]
        verdict = VERDICT_MAP.get(entry["verdict"])
        if verdict is None:
            fc.halt(f"adapter: axis {slug!r} has unrecognized verdict {entry['verdict']!r}")

        note = fold_note(entry)
        removed = None
        if entry.get("member_removals"):
            removed = resolve_removed_members(slug, entry["member_removals"], review_axes_by_slug, review_cards)

        if slug in manufactured_carrier_slugs:
            target = manufactured_carrier_slugs[slug]
            spec = MANUFACTURED_TARGETS[target]
            dec = {
                "verdict": "rename",
                "new_slug": target,
                "definition_edit": spec["definition_edit"],
                "note": (note + " | DET-adapter: promoted to rename-carrier for manufactured merge target "
                         f"{target} (largest member count among {[spec['carrier']] + spec['others']}); "
                         "final member set is a union, identical regardless of carrier choice.").strip(" |"),
            }
            if removed:
                dec["removed_members"] = removed
            out_axes[slug] = dec
            continue

        if slug in manufactured_other_slugs:
            target = manufactured_other_slugs[slug]
            dec = {"verdict": "merge", "merge_into": target, "note": note}
            if removed:
                dec["removed_members"] = removed
            out_axes[slug] = dec
            continue

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
    scope_by_slug = {
        "rule:exile-until-source-leaves": "opponent-stuff",
        "rule:alt-win-empty-library": "self",
        "rule:targets-a-player": "targeted-player",  # novel scope value: none of the batch-1 vocabulary
                                                       # (self/your-stuff/opponent-stuff/all-players/
                                                       # any-permanent/any-creature) fits a single
                                                       # targeted-player effect; free text, not validated
                                                       # by an enum downstream.
    }
    captain_axes = []
    for ca in src["captain_authored_axes"]:
        slug = ca["slug"]
        scope = scope_by_slug.get(slug)
        if scope is None:
            fc.halt(f"adapter: no scope mapping defined for captain-authored axis {slug!r}")
        seed_members = []
        for name in ca["example_cards"]:
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
            "adapted_from": str(DECISIONS_SRC.relative_to(fc.FOUNDRY_OUT_DIR.parent.parent.parent)),
            "adapter_script": "experiments/foundry_adapt_batch1_decisions.py",
            "note": "batch-1 special case per SUP-TRIAGE-PROTOCOL BATCH-1 PROVENANCE NOTE; "
                    "batches 2+ emit foundry-decisions/1 directly and skip this adapter",
        },
        "_not_carried_by_reconcile_py": {
            "override_spotcheck": src.get("override_spotcheck"),
            "ledger_candidates_carry_forward": src.get("ledger_candidates_carry_forward"),
            "new_rulings": src.get("new_rulings"),
            "punch_list": src.get("punch_list"),
            "other_lane_promotions": src.get("other_lane", {}).get("promotions"),
            "note": "these fields have no home in foundry_reconcile.py's schema; handled by "
                    "separate triage-emit steps (ledger doc, batch-2 assembly targeting, "
                    "OTHER-lane manual codebook patch) rather than dropped",
        },
    }
    fc.write_json(ADAPTED_OUT, adapted)
    print(f"wrote {ADAPTED_OUT}")
    print(f"axes: {len(out_axes)}  captain_axes: {len(captain_axes)}")


if __name__ == "__main__":
    main()
