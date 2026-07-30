#!/usr/bin/env python3
"""One-time adapter: sup-triage-decisions-v1 (decisions/batch-6.json, Captain-
ratified per TRIAGE-BATCH-6.md sections 10-11, D1-D8) -> foundry-decisions/1
(what foundry_reconcile.py consumes). Same schema gap batches 2-5's adapters
bridge.

Batch-6-specific: zero MERGE/KILL/RENAME verdicts (every axis is KEEP), so
the merge-target precheck is a no-op this batch but kept for consistency.
The one new thing this adapter does that its predecessors didn't: Gate #0
(batch-6 D1) is re-verified here, independently of the manual exclusions
already baked into decisions/batch-6.json's member_removals -- every
member_addition and every captain_axes seed_member is checked against
foundry_common.gate_passes() before being resolved to an oracle_id, and the
adapter HALTS rather than silently admit a gated card. This is a
belt-and-suspenders check, not the primary mechanism (the primary mechanism
is the member_removals already present in decisions/batch-6.json).
"""
import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402

DECISIONS_SRC = fc.FOUNDRY_OUT_DIR / "decisions" / "batch-6.json"
REVIEW_SRC = fc.FOUNDRY_OUT_DIR / "review" / "batch-6.json"
ADAPTED_OUT = fc.FOUNDRY_OUT_DIR / "decisions" / "batch-6.foundry-decisions-v1.json"

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
        fc.halt(f"adapter: axis {slug!r} has member_removals but is not a batch-6 axis -- cannot resolve")
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


def resolve_member_addition_name(name: str, review_cards: dict, cards_all: dict) -> str:
    matches = [oid for oid, c in review_cards.items() if c["name"] == name]
    if len(matches) == 0:
        fc.halt(f"adapter: member_addition {name!r} not found among batch-6's review cards")
    if len(matches) > 1:
        fc.halt(f"adapter: member_addition {name!r} matched {len(matches)} cards in batch-6 review -- ambiguous")
    oid = matches[0]
    card = cards_all.get(oid)
    if card is None or not fc.gate_passes(card):
        fc.halt(f"adapter: member_addition {name!r} ({oid}) fails Gate #0 -- should have been excluded upstream, HALT rather than admit it")
    return oid


def main():
    src = json.loads(DECISIONS_SRC.read_text(encoding="utf-8"))
    if src.get("schema") != "sup-triage-decisions-v1":
        fc.halt(f"{DECISIONS_SRC}: unexpected schema {src.get('schema')!r}, expected sup-triage-decisions-v1")

    review = json.loads(REVIEW_SRC.read_text(encoding="utf-8"))
    review_axes_by_slug = {a["slug"]: a for a in review["axes"]}
    review_cards = review["cards"]
    cards_all, _ = fc.load_corpus()  # raw -- need this to gate-check, not the pre-filtered corpus

    codebook_path = fc.FOUNDRY_OUT_DIR / "codebook.json"
    codebook = json.loads(codebook_path.read_text(encoding="utf-8")) if codebook_path.exists() else {"axes": {}}

    for entry in src["axes"]:
        if entry["verdict"] != "MERGE":
            continue
        target = entry["merge_into"]
        if target not in review_axes_by_slug and target not in codebook["axes"]:
            fc.halt(f"adapter: MERGE target {target!r} (from {entry['slug']!r}) does not exist as a batch-6 "
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
        if entry.get("definition_edit"):
            dec["definition_edit"] = entry["definition_edit"]
        if removed:
            dec["removed_members"] = removed
        out_axes[slug] = dec

    # Belt-and-suspenders: confirm every axis's STAGED (post-removal) member set is
    # entirely gate-passing. This should always be true given decisions/batch-6.json's
    # own member_removals already exclude every known gated card -- if this trips, the
    # manual exclusion list built earlier in this session missed one, and this halts
    # rather than silently reconciling a gated card into codebook v0.6.
    for slug, axis in review_axes_by_slug.items():
        dec = out_axes.get(slug)
        if dec is None:
            continue
        removed_ids = {r["oracle_id"] for r in dec.get("removed_members", [])}
        for m in axis["members"]:
            if m["oracle_id"] in removed_ids:
                continue
            card = cards_all.get(m["oracle_id"])
            if card is None or not fc.gate_passes(card):
                name = review_cards.get(m["oracle_id"], {}).get("name", m["oracle_id"])
                fc.halt(f"adapter: {slug!r} would keep gated member {name!r} ({m['oracle_id']}) -- "
                         f"missing from decisions/batch-6.json's member_removals, fix the decisions file")

    cards, name_index, _ = fc.load_corpus_gated()  # captain-authored / member_addition names must resolve against the GATED corpus
    captain_axes = []
    for ca in src["captain_authored_axes"]:
        slug = ca["slug"]
        scope = ca.get("scope")
        if scope is None:
            fc.halt(f"adapter: no scope on captain-authored axis {slug!r}")
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
    for promo in src.get("other_lane", {}).get("promotions", []):
        slug = promo["slug"]
        seed_members = [fc.resolve_name(name, cards, name_index) for name in promo.get("example_cards", [])]
        captain_axes.append({
            "slug": slug,
            "definition": promo["definition"],
            "scope": promo["scope"],
            "seed_members": seed_members,
        })

    member_additions_out = []
    for add in src.get("member_additions", []):
        oid = resolve_member_addition_name(add["name"], review_cards, cards_all)
        member_additions_out.append({
            "slug": add["slug"],
            "oracle_id": oid,
            "name": add["name"],
            "note": add.get("note", ""),
        })

    adapted = {
        "schema": "foundry-decisions/1",
        "batch": src["batch"],
        "axes": out_axes,
        "captain_axes": captain_axes,
        "member_additions": member_additions_out,
        "_provenance": {
            "adapted_from": "experiments/out/foundry/decisions/batch-6.json",
            "adapter_script": "experiments/foundry_adapt_batch6_decisions.py",
        },
        "_not_carried_by_reconcile_py": {
            "override_spotcheck": src.get("override_spotcheck"),
            "ledger_candidates_carry_forward": src.get("ledger_candidates_carry_forward"),
            "new_rulings": src.get("new_rulings"),
            "punch_list": src.get("punch_list"),
            "other_lane_promotions": src.get("other_lane", {}).get("promotions"),
            "note": "these fields have no home in foundry_reconcile.py's schema; handled by separate "
                    "triage-emit steps (ledger doc, batch-7 assembly targeting) rather than dropped",
        },
    }
    fc.write_json(ADAPTED_OUT, adapted)
    print(f"wrote {ADAPTED_OUT}")
    print(f"axes: {len(out_axes)}  captain_axes: {len(captain_axes)}  member_additions: {len(member_additions_out)}")


if __name__ == "__main__":
    main()
