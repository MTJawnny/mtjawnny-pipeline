#!/usr/bin/env python3
"""Assembles the batch-4 seed for the T3 Axis Foundry per MASTER-HANDOFF.md
section 5 (batch-seed method) with section 5.6 batch-3+ targeting: thin
2-member (or zero-member) KEEPs created/touched by batch 3, prioritizing
Captain's explicit batch-3 punch-list confirmation targets over the full
~40-thin-axis population, plus under-covered strata via DET stratified
fill. No OTHER-lane cluster reinforcement this batch either: batch 2 and
batch 3 both found the full OTHER-lane token-group residue to be generic
word-pair noise (zero promotions in either batch).

rule:free-sacrifice-outlet and rule:etb-tutor-to-hand were flagged as
"still-thin (n=1)" in TRIAGE-BATCH-3.md section 7.4, but codebook v0.3
shows both at 9 members after batch-3 reconciliation -- that prose claim
was stale/wrong, not a real gap. Dropped from batch-4 targeting on that
basis (verified against experiments/out/foundry/codebook.json directly,
not the possibly-stale digest prose). rule:targeted-battle-damage remains
a genuine zero-hit search miss for a second batch running (also zero in
batch 3's own CONFIRMATION_PICKS) -- Battle is a very new, sparsely
printed card type; carried forward empty again rather than force a match.

Usage: python3 experiments/foundry_assemble_batch4.py
"""
import sys
import json
import random
from pathlib import Path
from datetime import date

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402

FOUNDRY_SEED = 20260719  # today's date, matching the seed=date-of-assembly convention
TARGET_SIZE = 1200
OUT_PATH = fc.FOUNDRY_OUT_DIR / "batch4_assembled.json"

# Captain-flagged / batch-3-punch-list confirmation targets, found via exact
# oracle-text pattern search (no fuzzy matching), excluding all batch-1/2/3
# cards. Empty list = search found zero real matches (not a hand-pick
# failure).
CONFIRMATION_PICKS = {
    # Q2 energy family (captain_authored_axes, batch 3) -- all thin/zero-member.
    "rule:energy-outlet-infinite": ["Solstice Zealot", "Aether Hub"],
    "rule:gives-energy-counters-immediately": ["Inventor's Axe", "Hightide Hermit"],
    "rule:gives-energy-counters-condition": ["Decoction Module", "Gonti's Machinations"],
    # 3d replacement axis (captain_authored_axes, batch 3) -- n=1 (Shore Up only).
    "rule:temporary-keyword-grant": ["Mizzium Skin", "Plumecreed Escort"],
    # Q1 new candidate, kept separate from rule:stun-counter -- n=2.
    "rule:prevents-target-untap-next-step": ["Waterknot", "Shackles"],
    # M3 rejected-merge, kept standalone -- n=2.
    "rule:creates-treasure-token": ["Rapacious Dragon", "Professional Face-Breaker"],
    # Carried forward from batch 3 (also zero there): Battle is a sparsely
    # printed card type; searched again, still zero real damage-to-battle hits.
    "rule:targeted-battle-damage": [],
}


def classify_type(type_line: str) -> str:
    tl = type_line or ""
    if "Planeswalker" in tl:
        return "Planeswalker"
    if "Battle" in tl:
        return "Battle"
    for special in ("Conspiracy", "Dungeon", "Phenomenon", "Plane", "Scheme", "Vanguard"):
        if special in tl:
            return special
    if "Land" in tl:
        return "Land"
    if "Creature" in tl:
        return "Creature"
    if "Artifact" in tl:
        return "Artifact"
    if "Enchantment" in tl:
        return "Enchantment"
    if "Instant" in tl:
        return "Instant"
    if "Sorcery" in tl:
        return "Sorcery"
    return "Other"


def classify_color(color_identity: list) -> str:
    if not color_identity:
        return "Colorless"
    if len(color_identity) > 1:
        return "Multicolor"
    return color_identity[0]


def classify_length(oracle_text: str) -> str:
    n = len(oracle_text or "")
    if n < 100:
        return "short"
    if n < 300:
        return "medium"
    return "long"


def classify_era(released_at: str) -> str:
    year = int((released_at or "2000-01-01")[:4])
    if year < 2004:
        return "pre-2004"
    if year <= 2013:
        return "2004-2013"
    if year <= 2019:
        return "2014-2019"
    return "2020-present"


def stratum_key(card: dict) -> tuple:
    return (
        classify_type(card.get("type_line")),
        classify_color(card.get("color_identity")),
        classify_length(card.get("oracle_text")),
        classify_era(card.get("released_at")),
    )


def main():
    cards, name_index = fc.load_corpus()
    b1 = json.loads((fc.FOUNDRY_OUT_DIR / "batch1_assembled.json").read_text())
    b2 = json.loads((fc.FOUNDRY_OUT_DIR / "batch2_assembled.json").read_text())
    b3 = json.loads((fc.FOUNDRY_OUT_DIR / "batch3_assembled.json").read_text())
    prior_oids = set(b1["all_oracle_ids"]) | set(b2["all_oracle_ids"]) | set(b3["all_oracle_ids"])
    print(f"corpus: {len(cards)} cards; prior batches (1+2+3) excluded: {len(prior_oids)}")

    hand_picked = {}

    def add_pick(oid, name, bucket):
        if oid in prior_oids:
            fc.halt(f"hand-pick {name!r} ({oid}) collides with a prior-batch card -- dedup failure")
        if oid in hand_picked:
            return
        hand_picked[oid] = {"name": name, "bucket": bucket}

    for slug, names in CONFIRMATION_PICKS.items():
        for name in names:
            oid = fc.resolve_name(name, cards, name_index)
            add_pick(oid, name, f"captain-flagged-confirmation:{slug}")

    print(f"hand-picked total (deduped): {len(hand_picked)}")

    excluded = prior_oids | hand_picked.keys()
    pool_by_stratum = {}
    for oid, c in cards.items():
        if oid in excluded:
            continue
        pool_by_stratum.setdefault(stratum_key(c), []).append(oid)

    reviewed_so_far = {}
    for oid in prior_oids:
        c = cards.get(oid)
        if c is None:
            continue
        k = stratum_key(c)
        reviewed_so_far[k] = reviewed_so_far.get(k, 0) + 1

    remaining_budget = TARGET_SIZE - len(hand_picked)
    if remaining_budget <= 0:
        fc.halt(f"hand-picked count {len(hand_picked)} already meets/exceeds TARGET_SIZE {TARGET_SIZE}")

    rng = random.Random(FOUNDRY_SEED)
    strata_sorted = sorted(pool_by_stratum.keys())

    det_filled = {}
    for k in strata_sorted:
        if reviewed_so_far.get(k, 0) == 0 and pool_by_stratum[k]:
            pool = sorted(pool_by_stratum[k])
            pick = rng.choice(pool)
            det_filled[pick] = k
            pool_by_stratum[k].remove(pick)

    total_pool = sum(len(v) for v in pool_by_stratum.values())
    remaining_after_pass1 = remaining_budget - len(det_filled)
    if remaining_after_pass1 > 0 and total_pool > 0:
        allocations = {}
        for k in strata_sorted:
            pool = pool_by_stratum[k]
            if not pool:
                continue
            share = round(remaining_after_pass1 * len(pool) / total_pool)
            allocations[k] = min(share, len(pool))
        allocated_total = sum(allocations.values())
        diff = remaining_after_pass1 - allocated_total
        i = 0
        keys_cycle = [k for k in strata_sorted if pool_by_stratum[k]]
        while diff != 0 and keys_cycle:
            k = keys_cycle[i % len(keys_cycle)]
            if diff > 0 and allocations.get(k, 0) < len(pool_by_stratum[k]):
                allocations[k] = allocations.get(k, 0) + 1
                diff -= 1
            elif diff < 0 and allocations.get(k, 0) > 0:
                allocations[k] -= 1
                diff += 1
            i += 1
            if i > 100000:
                break
        for k in strata_sorted:
            n = allocations.get(k, 0)
            if n <= 0:
                continue
            pool = sorted(pool_by_stratum[k])
            picks = rng.sample(pool, n)
            for p in picks:
                det_filled[p] = k

    all_oids = sorted(set(hand_picked.keys()) | set(det_filled.keys()))
    strata_report = []
    for k in strata_sorted:
        pool_size_orig = len(pool_by_stratum[k]) + sum(1 for oid, kk in det_filled.items() if kk == k)
        actual = sum(1 for oid, kk in det_filled.items() if kk == k)
        strata_report.append({
            "stratum": {"type": k[0], "color": k[1], "length": k[2], "era": k[3]},
            "pool_size_remaining_before_fill": pool_size_orig,
            "reviewed_in_prior_batches": reviewed_so_far.get(k, 0),
            "det_filled_actual": actual,
            "under_covered_guarantee_used": reviewed_so_far.get(k, 0) == 0 and actual > 0,
        })

    out = {
        "schema": "foundry-seed-assembled/2",
        "batch": 4,
        "target_size": TARGET_SIZE,
        "foundry_seed": FOUNDRY_SEED,
        "assembled_on": date.today().isoformat(),
        "hand_picked_count": len(hand_picked),
        "hand_picked": [{"oracle_id": oid, **v} for oid, v in sorted(hand_picked.items())],
        "det_filled_count": len(det_filled),
        "det_filled_oracle_ids": sorted(det_filled.keys()),
        "strata": strata_report,
        "no_other_lane_reinforcement_reason": "batches 2 and 3's OTHER-lane token groups were both sampled "
            "broadly across the full size range and found to be generic 2/3-token-overlap noise (zero "
            "promotions either batch) -- no coherent cluster to reinforce this batch.",
        "deduped_against": "all batch-1 (n=500), batch-2 (n=1200), and batch-3 (n=1200) cards",
        "all_oracle_ids": all_oids,
    }
    fc.write_json(OUT_PATH, out)
    print(f"wrote {OUT_PATH}: {len(hand_picked)} hand-picked + {len(det_filled)} DET-filled = {len(all_oids)} total")


if __name__ == "__main__":
    main()
