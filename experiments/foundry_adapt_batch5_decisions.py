#!/usr/bin/env python3
"""One-time adapter: sup-triage-decisions-v1 (decisions/batch-5.json, Captain-
ratified per TRIAGE-BATCH-5.md section 10, D1-D18) -> foundry-decisions/1
(what foundry_reconcile.py consumes). Same schema gap batches 2-4's adapters
bridge.

Nothing new needed in reconcile.py's verdict vocabulary this batch (no
DEFER) -- keep/kill/merge/rename/captain_axes/member_additions all already
exist from batches 2-4's extensions. The only adapter-level subtlety:
member_additions this batch reference cards that are sometimes NOT members
of ANY axis in this batch's own review data (e.g. Cat Burglar/Priest of the
Haunted Edge were pure OTHER-lane rows for the sorcery-speed restriction
label) -- resolved the same way batch-4's adapter did, by name-searching
the full review cards dict rather than a specific axis's member list.
"""
import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402

DECISIONS_SRC = fc.FOUNDRY_OUT_DIR / "decisions" / "batch-5.json"
REVIEW_SRC = fc.FOUNDRY_OUT_DIR / "review" / "batch-5.json"
ADAPTED_OUT = fc.FOUNDRY_OUT_DIR / "decisions" / "batch-5.foundry-decisions-v1.json"

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
        fc.halt(f"adapter: axis {slug!r} has member_removals but is not a batch-5 axis -- cannot resolve")
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
    """member_additions names a card that is a member of some OTHER axis (or
    a pure OTHER-lane row) this batch -- search the whole review cards dict
    by name."""
    matches = [oid for oid, c in review_cards.items() if c["name"] == name]
    if len(matches) == 0:
        fc.halt(f"adapter: member_addition {name!r} not found among batch-5's review cards")
    if len(matches) > 1:
        fc.halt(f"adapter: member_addition {name!r} matched {len(matches)} cards in batch-5 review -- ambiguous")
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
            fc.halt(f"adapter: MERGE target {target!r} (from {entry['slug']!r}) does not exist as a batch-5 "
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

    # captain_authored_axes -> captain_axes, example_cards (names) -> seed_members (oracle_ids).
    # OTHER-lane promotions (SUP-discovered, Captain-ratified per D4) are folded into the
    # same list -- reconcile.py's captain_axes path is the only mechanism that builds a
    # brand-new axis with real members from scratch. This mislabels their codebook
    # "source" as CAPTAIN (reconcile.py hardcodes that for every captain_axes entry); noted
    # here rather than silently accepted -- no dedicated OTHER-lane-promotion code path
    # exists in reconcile.py as of this batch (the first with a surviving promotion under
    # the SUP-triage protocol), and adding one for a cosmetic provenance-label difference
    # is out of scope for this emit.
    cards, name_index = fc.load_corpus()
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
        oid = resolve_member_addition_name(add["name"], review_cards)
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
            "adapted_from": "experiments/out/foundry/decisions/batch-5.json",
            "adapter_script": "experiments/foundry_adapt_batch5_decisions.py",
        },
        "_not_carried_by_reconcile_py": {
            "override_spotcheck": src.get("override_spotcheck"),
            "ledger_candidates_carry_forward": src.get("ledger_candidates_carry_forward"),
            "new_rulings": src.get("new_rulings"),
            "punch_list": src.get("punch_list"),
            "other_lane_promotions": src.get("other_lane", {}).get("promotions"),
            "note": "these fields have no home in foundry_reconcile.py's schema; handled by separate "
                    "triage-emit steps (ledger doc, batch-6 assembly targeting) rather than dropped",
        },
    }
    fc.write_json(ADAPTED_OUT, adapted)
    print(f"wrote {ADAPTED_OUT}")
    print(f"axes: {len(out_axes)}  captain_axes: {len(captain_axes)}  member_additions: {len(member_additions_out)}")


if __name__ == "__main__":
    main()
