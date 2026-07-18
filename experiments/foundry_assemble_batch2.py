#!/usr/bin/env python3
"""Assembles the batch-2 seed for the T3 Axis Foundry per MASTER-HANDOFF.md
section 5 (batch-seed method) with section 5.6 batch-2+ targeting:
(a) axes with thin member counts needing confirmation, (b) OTHER-lane
clusters from the prior batch, (c) strata under-covered so far.

Hand-picked portion:
  - thin/flagged-axis reinforcement: up to 3 corpus-validated NEW cards per
    codebook axis at <=2 members (or explicitly Captain-flagged for batch-2
    confirmation despite more members), found by an exact oracle-text
    pattern search per axis (no fuzzy matching -- house style), excluding
    ALL cards already used in batch 1.
  - unpromoted OTHER-lane cluster reinforcement: same method for the
    handful of coherent (non-generic-grab-bag) unpromoted clusters.
Random-fill portion: DET stratified random sample (type x color x
oracle-text-length x era) over the remaining corpus pool, fixed seed,
guaranteeing every non-empty stratum NOT touched by batch 1 gets at least
one pick before proportional fill of the remainder -- this is the concrete
mechanism for "under-covered strata" targeting.

Usage: python3 experiments/foundry_assemble_batch2.py
"""
import sys
import json
import random
from pathlib import Path
from datetime import date

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402

FOUNDRY_SEED = 20260718  # today's date, matching batch-1's seed=date-of-assembly convention
TARGET_SIZE = 1200  # middle of MASTER-HANDOFF's stated 1,000-1,500 range for batch 2+; flagged for Captain
BATCH1_ASSEMBLED = fc.FOUNDRY_OUT_DIR / "batch1_assembled.json"
THIN_PICKS = Path("/private/tmp/claude-501/-Users-jawnny-Projects-mtjawnny-pipeline-experiments-out-foundry-decisions/8a5b3788-e13c-40e3-9938-8ab52d3cb51f/scratchpad/thin_axis_picks.json")
OUT_PATH = fc.FOUNDRY_OUT_DIR / "batch2_assembled.json"

OTHER_CLUSTER_PICKS = {
    "landfall-trigger": ["Nissa, Worldsoul Speaker", "Seedship Agrarian", "Territorial Bruntar"],
    "enters-with-counters": ["Lattice Library", "Carnage Wurm", "Yorvo, Lord of Garenbrig"],
    "blink-own-creature": ["Blur", "Justiciar's Portal", "Daydream"],
}
OTHER_CLUSTERS_NOTED_NO_PICK = [
    "etb-triggered-ability", "counters-target-spell", "card-draw", "exile-target-creature",
    "counter-target-spell", "bounce-target-permanent", "draw-a-card", "life-gain-on-trigger",
    "attack-triggered-ability", "bounce-target-creature", "triggers-on-own-creature-death",
    "scry-effect",
]  # generic label-collisions (grab-bags), same shape as batch-1's lane 1d KILLs -- flagged
   # for Session B's awareness only, no reinforcement cards picked

EXTRA_CONFIRMATION_AXIS = {
    # explicitly Captain-flagged in decisions/batch-1.json despite >2 members
    "rule:x-scales-with-permanent-count": ["Snow Villiers", "Kolaghan Forerunners", "Sumala Rumblers"],
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
    batch1 = json.loads(BATCH1_ASSEMBLED.read_text())
    batch1_oids = set(batch1["all_oracle_ids"])
    print(f"corpus: {len(cards)} cards; batch-1 (all prior batches) excluded: {len(batch1_oids)}")

    thin_picks = json.loads(THIN_PICKS.read_text())

    hand_picked = {}  # oracle_id -> {name, bucket}
    def add_pick(oid, name, bucket):
        if oid in batch1_oids:
            fc.halt(f"hand-pick {name!r} ({oid}) collides with a batch-1 card -- dedup failure")
        if oid in hand_picked:
            return  # already added under another bucket, fine -- same card, dedup within batch-2
        hand_picked[oid] = {"name": name, "bucket": bucket}

    for slug, data in thin_picks.items():
        for p in data["picked"]:
            add_pick(p["oracle_id"], p["name"], f"thin-axis-confirmation:{slug}")

    for slug, names in EXTRA_CONFIRMATION_AXIS.items():
        for name in names:
            oid = fc.resolve_name(name, cards, name_index)
            add_pick(oid, name, f"captain-flagged-confirmation:{slug}")

    for label, names in OTHER_CLUSTER_PICKS.items():
        for name in names:
            oid = fc.resolve_name(name, cards, name_index)
            add_pick(oid, name, f"other-lane-cluster:{label}")

    print(f"hand-picked total (deduped): {len(hand_picked)}")

    # DET stratified random fill over remaining pool.
    excluded = batch1_oids | hand_picked.keys()
    pool_by_stratum = {}
    for oid, c in cards.items():
        if oid in excluded:
            continue
        pool_by_stratum.setdefault(stratum_key(c), []).append(oid)

    # "reviewed so far" per stratum = batch-1 cards classified under this
    # script's own stratification (not batch-1's own undocumented bucket
    # labels, which can't be exactly reconstructed -- this is a fresh,
    # self-consistent stratification pass, not a byte-identical replication).
    reviewed_so_far = {}
    for oid in batch1_oids:
        c = cards.get(oid)
        if c is None:
            continue
        k = stratum_key(c)
        reviewed_so_far[k] = reviewed_so_far.get(k, 0) + 1

    remaining_budget = TARGET_SIZE - len(hand_picked)
    if remaining_budget <= 0:
        fc.halt(f"hand-picked count {len(hand_picked)} already meets/exceeds TARGET_SIZE {TARGET_SIZE}")

    rng = random.Random(FOUNDRY_SEED)
    strata_sorted = sorted(pool_by_stratum.keys())  # deterministic order

    # Pass 1: guarantee 1 pick for every non-empty stratum batch-1 never touched (under-covered targeting).
    det_filled = {}
    for k in strata_sorted:
        if reviewed_so_far.get(k, 0) == 0 and pool_by_stratum[k]:
            pool = sorted(pool_by_stratum[k])
            pick = rng.choice(pool)
            det_filled[pick] = k
            pool_by_stratum[k].remove(pick)

    # Pass 2: proportional fill of the remainder by pool_size, fixed seed.
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
        # rounding can over/under-shoot; trim/top-up deterministically by stratum order
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
            "reviewed_in_batch1": reviewed_so_far.get(k, 0),
            "det_filled_actual": actual,
            "under_covered_guarantee_used": reviewed_so_far.get(k, 0) == 0 and actual > 0,
        })

    out = {
        "schema": "foundry-seed-assembled/2",
        "batch": 2,
        "target_size": TARGET_SIZE,
        "foundry_seed": FOUNDRY_SEED,
        "assembled_on": date.today().isoformat(),
        "hand_picked_count": len(hand_picked),
        "hand_picked": [{"oracle_id": oid, **v} for oid, v in sorted(hand_picked.items())],
        "det_filled_count": len(det_filled),
        "det_filled_oracle_ids": sorted(det_filled.keys()),
        "strata": strata_report,
        "unpromoted_other_lane_clusters_noted_no_reinforcement": OTHER_CLUSTERS_NOTED_NO_PICK,
        "deduped_against": "all batch-1 cards (experiments/out/foundry/batch1_assembled.json:all_oracle_ids, n=500)",
        "all_oracle_ids": all_oids,
    }
    fc.write_json(OUT_PATH, out)
    print(f"wrote {OUT_PATH}: {len(hand_picked)} hand-picked + {len(det_filled)} DET-filled = {len(all_oids)} total")


if __name__ == "__main__":
    main()
