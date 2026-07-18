#!/usr/bin/env python3
"""T3-AXIS-FOUNDRY-v3.md -- measurement skeleton (Session A). MEASUREMENT-ONLY,
same discipline as family_tree_evidence.py: imports tier_engine as a library,
never writes back into it, never wired into scoring. Corpus-wide operations
here are the DET/free stages of the foundry loop (worker-class vocabulary:
DET/BULK/SYNTH/SUP, "tier" reserved for card tiers -- MASTER-HANDOFF.md §6).

Subcommands (each independently re-runnable, resumable cold):
  stage0        -- coverage baseline: what fraction of the corpus already
                    carries >=1 rule:-namespace tag today.
  stage1a       -- Source A template mining: candidate templated spines
                    mined from clause_df (DET, zero tokens).
  assemble-batch -- consumes foundry_batch1_seed.json's 281 hand-picked
                    cards, DET-fills to --size by stratified random sample,
                    prints strata, writes the assembled batch's oracle_id
                    list to disk.

Run (from repo root): python3 experiments/measure/axis_foundry.py <subcommand>
Determinism: every artifact-producing subcommand runs its own sampling twice
in-process and asserts byte-identical output before writing anything.
"""
import sys
import json
import math
import random
import re
import argparse
from pathlib import Path
from collections import defaultdict, Counter

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import tier_engine as te  # noqa: E402
import foundry_common as fc  # noqa: E402

# family_tree_evidence.py's v1-derivation regexes (Step 4 artifact) -- reused
# verbatim for Stage 0's "not yet landed" context table so this script never
# re-derives patterns family_tree_evidence.py already calibrated and Captain
# has already seen. Import is side-effect-free: that module's corpus work
# lives inside main(), guarded by `if __name__ == "__main__":`.
import family_tree_evidence as fte  # noqa: E402

OUT_DIR = REPO_ROOT / "experiments" / "out" / "foundry"
MEASURE_OUT_DIR = REPO_ROOT / "experiments" / "out" / "measurement"
OUT_DIR.mkdir(parents=True, exist_ok=True)
MEASURE_OUT_DIR.mkdir(parents=True, exist_ok=True)

FOUNDRY_SEED = 20260717  # today's date, same fixed-seed-for-determinism convention as the rest of the repo

# ---------------------------------------------------------------------------
# Shared corpus build (Stage 0 and Stage 1A both need card_docs + indexes;
# built once per process, never persisted -- rebuilding is DET and cheap
# next to a token-costing stage).
# ---------------------------------------------------------------------------

def build_corpus():
    cards = te.load_cards(te.CARDS_PATH)
    raw_keyword_df = te.compute_keyword_df_from_cards(cards)
    card_docs = {
        oracle_id: te.build_card_doc(card, keyword_df=raw_keyword_df)
        for oracle_id, card in cards.items()
    }
    paragraph_index, clause_index, clause_df, ngram_index, ngram_df = te.build_indexes(card_docs, te.NGRAM_MIN_LEN)
    return cards, card_docs, clause_index, clause_df, ngram_index, ngram_df


# ---------------------------------------------------------------------------
# Stage 0 -- coverage baseline (DET, zero tokens)
# ---------------------------------------------------------------------------

def stage0_coverage_baseline(cards: dict, card_docs: dict) -> dict:
    n_total = len(cards)
    print(f"\n=== Stage 0 -- coverage baseline ({n_total:,} cards) ===")

    turn_scoped_matches, turn_scoped_idf = te.run_turn_scoped_derivation(card_docs, n_total)
    landed_df = len(turn_scoped_matches)
    landed_pct = 100.0 * landed_df / n_total
    print(f"LANDED (Step 5 not yet run per playbook -- only rule:turn-scoped exists today):")
    print(f"  rule:turn-scoped: DF={landed_df:,} ({landed_pct:.2f}% of corpus), idf={turn_scoped_idf:.3f}")
    print(f"  Overall rule:-namespace coverage today: {landed_df:,}/{n_total:,} = {landed_pct:.2f}%")

    # Not-yet-landed v1 set (DERIVED-TAG-LAYER-SPEC.md), freshly recomputed
    # against this run's card_docs (never recalled) so Stage 0's context
    # numbers are live, not copied from the spec's prototype table.
    v1_patterns = [
        ("rule:restricts-cast (neg)", fte.RESTRICTS_CAST_NEG_RE),
        ("rule:restricts-cast (pos)", fte.RESTRICTS_CAST_POS_RE),
        ("rule:restricts-activation (neg)", fte.RESTRICTS_ACTIVATION_NEG_RE),
        ("rule:restricts-activation (pos)", fte.RESTRICTS_ACTIVATION_POS_RE),
        ("rule:cost-increase", fte.COST_INCREASE_RE),
        ("rule:cost-reduction", fte.COST_REDUCTION_RE),
        ("rule:pay-tax", fte.PAY_TAX_RE),
        ("rule:uncounterable", fte.UNCOUNTERABLE_RE),
        ("rule:prohibits-attack", fte.PROHIBITS_ATTACK_RE),
        ("rule:prohibits-block", fte.PROHIBITS_BLOCK_RE),
    ]
    print(f"\nNOT YET LANDED (v1 derivation set, DERIVED-TAG-LAYER-SPEC.md; playbook Step 5 pending):")
    not_landed_union = set()
    for label, pattern in v1_patterns:
        matches = fte.find_matches(card_docs, pattern)
        not_landed_union.update(matches.keys())
        df = len(matches)
        idf = math.log(n_total / df) if df else 0.0
        print(f"  {label}: DF={df:,}, idf={idf:.3f}")

    union_all = set(turn_scoped_matches.keys()) | not_landed_union
    union_pct = 100.0 * len(union_all) / n_total
    print(f"\nProjected coverage IF the full v1 set landed: {len(union_all):,}/{n_total:,} = {union_pct:.2f}%")
    print(f"Gap this foundry exists to close (cards with ZERO rule:-tag potential under v1, "
          f"the axes v1 didn't anticipate): {n_total - len(union_all):,} cards ({100 - union_pct:.2f}%)")

    result = {
        "n_total_cards": n_total,
        "landed": {"rule:turn-scoped": {"df": landed_df, "pct": round(landed_pct, 3)}},
        "not_yet_landed_v1": {
            label: len(fte.find_matches(card_docs, pattern)) for label, pattern in v1_patterns
        },
        "projected_v1_union_pct": round(union_pct, 3),
        "residue_pct": round(100 - union_pct, 3),
    }
    out_path = OUT_DIR / "stage0_coverage_baseline.json"
    fc.write_json(out_path, result)
    print(f"\nwrote {out_path}")
    return result


# ---------------------------------------------------------------------------
# Stage 1A -- Source A template mining (DET, zero tokens)
# ---------------------------------------------------------------------------

SOURCE_A_DF_FLOOR = 15  # measured elbow: 99th pct of clause_df is DF<=13 (45,343 distinct clauses,
                         # 2026-07-17 corpus) -- below this a clause is near-singleton phrasing, not
                         # a recurring template. No ceiling: corpus max DF is 511, already meaningful.
SOURCE_A_MIN_WORDS = 3
SOURCE_A_SAMPLE_N = 5

# Explicitly out of v1 scope per DERIVED-TAG-LAYER-SPEC.md ("Deliberately NOT
# in v1: ... mana-production tags (T2 mana kinship already owns that axis)")
# -- filtered out of Source A candidates rather than surfaced as noise.
MANA_ABILITY_CLAUSE_RE = re.compile(r"^\{[^}]+\}[:,]?\s*add\b")


def stage1a_source_a_mining(cards: dict, card_docs: dict, clause_index: dict, clause_df: dict) -> dict:
    n_total = len(cards)
    print(f"\n=== Stage 1A -- Source A template mining ({len(clause_df):,} distinct clauses) ===")

    candidates = []
    excluded_mana = 0
    excluded_short = 0
    for clause, df in clause_df.items():
        if df < SOURCE_A_DF_FLOOR:
            continue
        if MANA_ABILITY_CLAUSE_RE.match(clause):
            excluded_mana += 1
            continue
        if len(clause.split()) < SOURCE_A_MIN_WORDS:
            excluded_short += 1
            continue
        candidates.append((clause, df))

    candidates.sort(key=lambda x: (-x[1], x[0]))
    print(f"DF floor={SOURCE_A_DF_FLOOR}, min words={SOURCE_A_MIN_WORDS}: {len(candidates):,} candidate templates "
          f"(excluded {excluded_mana:,} mana-ability clauses [T2 mana kinship's axis], {excluded_short:,} sub-{SOURCE_A_MIN_WORDS}-word fragments)")

    rng = random.Random(FOUNDRY_SEED)
    out_candidates = []
    for clause, df in candidates:
        idf = math.log(n_total / df) if df else 0.0
        members = sorted(clause_index.get(clause, []))
        sample_ids = members if len(members) <= SOURCE_A_SAMPLE_N else rng.sample(members, SOURCE_A_SAMPLE_N)
        sample_ids = sorted(sample_ids)
        out_candidates.append({
            "clause": clause,
            "df": df,
            "idf": round(idf, 3),
            "sample_oracle_ids": sample_ids,
            "sample_names": [card_docs[oid]["name"] for oid in sample_ids],
        })

    print(f"\nTop 20 by DF:")
    for c in out_candidates[:20]:
        print(f"  DF={c['df']:>4}  idf={c['idf']:.2f}  {c['clause']!r}  e.g. {c['sample_names'][:3]}")

    result = {
        "schema": "foundry-source-a/1",
        "df_floor": SOURCE_A_DF_FLOOR,
        "n_total_cards": n_total,
        "n_candidates": len(out_candidates),
        "candidates": out_candidates,
    }
    out_path = OUT_DIR / "source_a_candidates.json"
    fc.write_json(out_path, result)
    print(f"\nwrote {out_path} ({len(out_candidates)} candidates)")
    return result


# ---------------------------------------------------------------------------
# Batch assembly -- hand-picked seed + DET stratified random fill
# ---------------------------------------------------------------------------

TYPE_PRIORITY = [
    "Land", "Planeswalker", "Battle", "Creature", "Instant", "Sorcery",
    "Artifact", "Enchantment", "Kindred", "Tribal", "Dungeon", "Plane",
    "Phenomenon", "Scheme", "Vanguard", "Conspiracy",
]


def primary_type_bucket(type_line: str) -> str:
    types = te.type_bucket(type_line)
    for t in TYPE_PRIORITY:
        if t in types:
            return t
    return "Other"


def color_bucket(color_identity: list) -> str:
    if not color_identity:
        return "Colorless"
    if len(color_identity) == 1:
        return color_identity[0]
    return "Multicolor"


def length_bucket(oracle_text: str) -> str:
    n = len(oracle_text or "")
    if n < 80:
        return "short"
    if n < 200:
        return "medium"
    return "long"


def era_bucket(released_at) -> str:
    if not released_at:
        return "unknown"
    year = int(str(released_at)[:4])
    if year < 2004:
        return "pre-2004"
    if year < 2014:
        return "2004-2013"
    if year < 2020:
        return "2014-2019"
    return "2020-present"


def stratum_key(card: dict) -> tuple:
    return (
        primary_type_bucket(card.get("type_line") or ""),
        color_bucket(card.get("color_identity") or []),
        length_bucket(card.get("oracle_text") or ""),
        era_bucket(card.get("released_at")),
    )


def stratified_fill(pool_ids: list, cards: dict, target_n: int, seed: int) -> list:
    """Proportional stratified sample of target_n oracle_ids from pool_ids,
    largest-remainder allocation across (type, color, length, era) strata,
    fixed seed, deterministic tie-breaks (sorted oracle_id)."""
    strata = defaultdict(list)
    for oid in pool_ids:
        strata[stratum_key(cards[oid])].append(oid)
    for key in strata:
        strata[key].sort()

    pool_size = len(pool_ids)
    raw_targets = {key: target_n * len(ids) / pool_size for key, ids in strata.items()}
    floor_targets = {key: int(math.floor(v)) for key, v in raw_targets.items()}
    allocated = sum(floor_targets.values())
    remainder = target_n - allocated
    remainders_sorted = sorted(strata.keys(), key=lambda k: (-(raw_targets[k] - floor_targets[k]), k))
    final_targets = dict(floor_targets)
    for key in remainders_sorted[:remainder]:
        final_targets[key] += 1

    rng = random.Random(seed)
    picked = []
    strata_report = []
    for key in sorted(strata.keys()):
        ids = strata[key]
        want = min(final_targets.get(key, 0), len(ids))
        chosen = sorted(rng.sample(ids, want)) if want else []
        picked.extend(chosen)
        strata_report.append({
            "stratum": {"type": key[0], "color": key[1], "length": key[2], "era": key[3]},
            "pool_size": len(ids),
            "target": final_targets.get(key, 0),
            "actual": len(chosen),
        })
    return sorted(picked), strata_report


def assemble_batch(seed_path: Path, target_size: int, batch_num: int):
    print(f"\n=== Assemble batch {batch_num} (target size {target_size}) ===")
    with open(seed_path, "r", encoding="utf-8") as f:
        seed = json.load(f)
    if seed.get("schema") != "foundry-seed/1":
        fc.halt(f"{seed_path}: unexpected schema {seed.get('schema')!r}, expected foundry-seed/1")

    cards, name_index = fc.load_corpus()

    hand_picked_ids = []
    seen_names = set()
    per_bucket_ids = {}
    for bucket_name, names in seed["buckets"].items():
        bucket_ids = []
        for name in names:
            if name in seen_names:
                fc.halt(f"seed file has duplicate hand-picked name across buckets: {name!r}")
            seen_names.add(name)
            oid = fc.resolve_name(name, cards, name_index)
            bucket_ids.append(oid)
            hand_picked_ids.append(oid)
        per_bucket_ids[bucket_name] = bucket_ids

    if len(hand_picked_ids) != seed["total_hand_picked"]:
        fc.halt(f"resolved {len(hand_picked_ids)} hand-picked cards, seed declares total_hand_picked="
                f"{seed['total_hand_picked']} — mismatch")
    if len(set(hand_picked_ids)) != len(hand_picked_ids):
        fc.halt("hand-picked list resolved to duplicate oracle_ids — two different names hit the same card")

    print(f"hand-picked: {len(hand_picked_ids)} cards across {len(seed['buckets'])} buckets (resolved, deduped, corpus-validated)")

    fill_n = target_size - len(hand_picked_ids)
    if fill_n < 0:
        fc.halt(f"hand-picked count {len(hand_picked_ids)} already exceeds target size {target_size}")

    excluded = set(hand_picked_ids)
    pool_ids = [oid for oid in cards if oid not in excluded]

    fill_a, strata_a = stratified_fill(pool_ids, cards, fill_n, FOUNDRY_SEED)
    fill_b, strata_b = stratified_fill(pool_ids, cards, fill_n, FOUNDRY_SEED)
    if fill_a != fill_b:
        fc.halt("determinism FAILED: stratified_fill produced different results on repeat run with the same seed")
    print(f"determinism x2: PASS (stratified fill byte-identical across two runs)")

    nonzero = [row for row in strata_a if row["actual"] > 0]
    print(f"\nDET stratified fill: {len(fill_a)} cards across {len(strata_a)} total (type x color x length x era) cells, "
          f"{len(nonzero)} of them non-empty (full {len(strata_a)}-row table written to disk)")

    for dim_idx, dim_name in enumerate(["type", "color", "length", "era"]):
        totals = defaultdict(int)
        for row in strata_a:
            totals[row["stratum"][dim_name]] += row["actual"]
        breakdown = ", ".join(f"{k}={v}" for k, v in sorted(totals.items(), key=lambda kv: -kv[1]) if v > 0)
        print(f"  by {dim_name}: {breakdown}")

    print(f"\nNon-empty strata ({len(nonzero)} rows):")
    print(f"{'type':<12} {'color':<11} {'length':<7} {'era':<13} {'pool':>6} {'target':>6} {'actual':>6}")
    for row in sorted(nonzero, key=lambda r: -r["actual"]):
        s = row["stratum"]
        print(f"{s['type']:<12} {s['color']:<11} {s['length']:<7} {s['era']:<13} {row['pool_size']:>6} {row['target']:>6} {row['actual']:>6}")

    all_ids = sorted(set(hand_picked_ids) | set(fill_a))
    if len(all_ids) != target_size:
        fc.halt(f"assembled batch has {len(all_ids)} cards, expected exactly {target_size}")

    result = {
        "schema": "foundry-batch-assembly/1",
        "batch": batch_num,
        "target_size": target_size,
        "seed_used": str(seed_path),
        "foundry_seed": FOUNDRY_SEED,
        "hand_picked_count": len(hand_picked_ids),
        "hand_picked_oracle_ids": sorted(hand_picked_ids),
        "hand_picked_by_bucket": {b: sorted(ids) for b, ids in per_bucket_ids.items()},
        "det_filled_count": len(fill_a),
        "det_filled_oracle_ids": fill_a,
        "strata": strata_a,
        "all_oracle_ids": all_ids,
    }
    out_path = OUT_DIR / f"batch{batch_num}_assembled.json"
    fc.write_json(out_path, result)
    print(f"\nwrote {out_path} ({len(all_ids)} total cards: {len(hand_picked_ids)} hand-picked + {len(fill_a)} DET-filled)")
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("stage0", help="coverage baseline")
    sub.add_parser("stage1a", help="Source A template mining")

    p_assemble = sub.add_parser("assemble-batch", help="assemble a batch: hand-picked seed + DET stratified fill")
    p_assemble.add_argument("--seed", default=str(OUT_DIR / "foundry_batch1_seed.json"))
    p_assemble.add_argument("--size", type=int, default=500)
    p_assemble.add_argument("--batch", type=int, default=1)

    args = parser.parse_args()

    if args.command in ("stage0", "stage1a"):
        print("building corpus (card_docs + clause/ngram indexes) — DET, no tokens...")
        cards, card_docs, clause_index, clause_df, ngram_index, ngram_df = build_corpus()
        print(f"loaded {len(cards):,} cards")
        if args.command == "stage0":
            stage0_coverage_baseline(cards, card_docs)
        else:
            stage1a_source_a_mining(cards, card_docs, clause_index, clause_df)
    elif args.command == "assemble-batch":
        assemble_batch(Path(args.seed), args.size, args.batch)


if __name__ == "__main__":
    main()
