#!/usr/bin/env python3
"""One-off post-hoc correction to codebook v0.7: applies the D4 GRAMMAR-SS9
quote-pull on rule:pay-life-cost-for-effect that emit held back (batch-7
reconcile already ran; this is NOT a re-run of that reconcile, batch 7 is
already in batches_reconciled). Captain-approved 2026-07-30 in chat, per
the batch-7 emit's halt report and the resulting card-by-card table --
this script is that table, executed.

10 members removed for failing GRAMMAR SS9 (life must be paid on the cost
side of a colon, or as an "additional cost" clause -- gaining life as an
EFFECT, paying a different resource, or a non-activated delivery structure
all fail): Elixir of Immortality, Tanglebloom, Tough Cookie, Dedicated
Martyr, Living Airship, Pyrohemia, Tempest Harvester, Sivitri Dragon
Master, Sangrophage, Shessra Death's Whisper.

Rehomes (remove-and-rehome, D5 standing rule):
- fixed-lifegain: Elixir of Immortality, Tanglebloom, Tough Cookie, Dedicated Martyr
- graveyard-to-library-shuffle-in: Elixir of Immortality (2nd facet, Captain amendment 3)
- mass-damage-creatures-and-players: Pyrohemia (Captain amendment 1 -- overturns the
  original "no home" call; "{R}: ... deals 1 damage to each creature and each
  player" is exactly this axis's shape)
- activated-loot: Tempest Harvester (Captain amendment 2, on its "draw a card, then
  discard a card" loot effect -- the energy-cost ledger flag stands independently)
- rhystic-tax: Sivitri, Dragon Master (its own "pay-or-you-can't-attack" shape matches
  rhystic-tax's own definition)
- draw-cards-with-life-loss-cost: Shessra, Death's Whisper (already holds non-spell
  triggered members, e.g. Coercive Impetus's attack-trigger -- consistent with existing
  practice)
- Living Airship, Sangrophage: no home found, ledger-flagged only (PARENT-TREE-CANDIDATES.md)

Tough Cookie's rule:etb-create-token-food membership was independently quote-checked
(Captain amendment 4) and confirmed correct -- no change there.
"""
import sys
import json
from pathlib import Path
from datetime import date

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402

CODEBOOK_PATH = fc.FOUNDRY_OUT_DIR / "codebook.json"
REPORT_PATH = fc.FOUNDRY_OUT_DIR / "batch7_pay_life_scrub_report.json"
BATCH_TAG = 7  # logged against batch 7's history for provenance; not a reconcile re-run

REMOVE_FROM_PAY_LIFE = [
    "Elixir of Immortality", "Tanglebloom", "Tough Cookie", "Dedicated Martyr",
    "Living Airship", "Pyrohemia", "Tempest Harvester", "Sivitri, Dragon Master",
    "Sangrophage", "Shessra, Death's Whisper",
]

ADDITIONS = {
    "rule:fixed-lifegain": ["Elixir of Immortality", "Tanglebloom", "Tough Cookie", "Dedicated Martyr"],
    "rule:graveyard-to-library-shuffle-in": ["Elixir of Immortality"],
    "rule:mass-damage-creatures-and-players": ["Pyrohemia"],
    "rule:activated-loot": ["Tempest Harvester"],
    "rule:rhystic-tax": ["Sivitri, Dragon Master"],
    "rule:draw-cards-with-life-loss-cost": ["Shessra, Death's Whisper"],
}

NO_HOME_LEDGER = ["Living Airship", "Sangrophage"]
ENERGY_LEDGER_NOTE = ("Tempest Harvester (\"{T}, Pay {E}: Draw a card, then discard a card.\") -- "
                       "energy-cost activated-loot variant; rule:energy-outlet-infinite is the closest "
                       "existing candidate but its exact definition wasn't confirmed to match -- flagged "
                       "for the CORPUS-PASS-PLAN walk rather than forced. (Its loot-effect facet is "
                       "separately a real rule:activated-loot member as of this scrub.)")


def main():
    cards, name_index = fc.load_corpus()
    codebook = json.loads(CODEBOOK_PATH.read_text(encoding="utf-8"))

    def oid_of(name):
        return fc.resolve_name(name, cards, name_index)

    pay_life = codebook["axes"]["rule:pay-life-cost-for-effect"]
    remove_oids = {oid_of(n) for n in REMOVE_FROM_PAY_LIFE}
    before = len(pay_life["member_oracle_ids"])
    missing = remove_oids - set(pay_life["member_oracle_ids"])
    if missing:
        fc.halt(f"rule:pay-life-cost-for-effect: removal target(s) not currently members: {missing}")
    pay_life["member_oracle_ids"] = sorted(set(pay_life["member_oracle_ids"]) - remove_oids)
    pay_life.setdefault("history", []).append({
        "batch": BATCH_TAG, "action": "member_removed_posthoc",
        "note": ("D4 GRAMMAR-SS9 quote-pull, Captain-approved 2026-07-30 (chat, post-emit): removed "
                 + ", ".join(REMOVE_FROM_PAY_LIFE) + " -- each rehomed or ledger-flagged, see "
                 "experiments/foundry_batch7_pay_life_scrub.py and PARENT-TREE-CANDIDATES.md."),
    })
    print(f"rule:pay-life-cost-for-effect: {before} -> {len(pay_life['member_oracle_ids'])} members")

    report = {"removed_from_pay_life_cost_for_effect": REMOVE_FROM_PAY_LIFE, "additions": {}}
    for slug, names in ADDITIONS.items():
        entry = codebook["axes"].get(slug)
        if entry is None:
            fc.halt(f"member_addition target {slug!r} does not exist in codebook.json")
        add_oids = {oid_of(n) for n in names}
        before_n = len(entry["member_oracle_ids"])
        entry["member_oracle_ids"] = sorted(set(entry["member_oracle_ids"]) | add_oids)
        entry.setdefault("history", []).append({
            "batch": BATCH_TAG, "action": "member_added_posthoc",
            "note": ("D4 GRAMMAR-SS9 rehome, Captain-approved 2026-07-30 (chat, post-emit), from "
                     "rule:pay-life-cost-for-effect: " + ", ".join(names)),
        })
        print(f"{slug}: {before_n} -> {len(entry['member_oracle_ids'])} members (+{names})")
        report["additions"][slug] = names

    fc.write_json(CODEBOOK_PATH, codebook)
    fc.write_json(REPORT_PATH, {
        "ruling": "batch-7 D4 GRAMMAR-SS9 quote-pull, Captain-approved 2026-07-30 (post-emit chat)",
        "run_on": date.today().isoformat(),
        **report,
        "no_home_ledger_flagged": NO_HOME_LEDGER,
        "energy_ledger_note": ENERGY_LEDGER_NOTE,
        "tough_cookie_etb_create_token_food_check": "verified correct, no change (its text reads "
            "'When this creature enters, create a Food token.')",
    })
    print(f"wrote {CODEBOOK_PATH} (in place) and {REPORT_PATH}")


if __name__ == "__main__":
    main()
