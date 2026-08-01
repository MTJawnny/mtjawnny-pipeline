#!/usr/bin/env python3
"""Batch 8 post-canonicalization re-scoring + consensus-design pricing
(Captain directive, 2026-08-01, following the packing-FAIL ruling). Reads
the already-fetched batch8_ab_raw_results.jsonl (no API spend) and:
  1. Re-scores all 6 arm pairs three ways: raw, codebook-lane-only, and
     free-lane after foundry_consolidate.canonicalize_label().
  2. Reports the variance decomposition (wording recovered by
     canonicalization vs. judgment that survives it), per lane.
  3. Prices two consensus designs at N=40 intro batch rate, using batch 8's
     REAL measured per-card cost (Arm C actuals, including observed cache
     write/read behavior -- not assumed, not "uncounted upside" this time).

Run: python3 experiments/foundry_batch8_canon_analysis.py
"""
import sys
import json
from pathlib import Path
from itertools import combinations

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402
import foundry_batch8_diff as diff  # noqa: E402
import foundry_batch8_ab as b8  # noqa: E402
import foundry_consolidate as fcon  # noqa: E402

ARMS = "ABCD"
OUT_PATH = fc.FOUNDRY_OUT_DIR / "batch8_canon_analysis.json"

CORPUS_SIZE = 32557
INTRO_IN_RATE = 2.00 * 0.5          # $1.00/MTok
CACHE_5M_WRITE_RATE = INTRO_IN_RATE * 1.25
CACHE_1H_WRITE_RATE = INTRO_IN_RATE * 2.0
CACHE_READ_RATE = INTRO_IN_RATE * 0.1
INTRO_OUT_RATE = 10.00 * 0.5        # $5.00/MTok


def jaccard(a, b):
    if not a and not b:
        return 1.0
    u = a | b
    return len(a & b) / len(u) if u else 1.0


def score_pairs(oracle_ids, extractor):
    out = {}
    for x, y in combinations(ARMS, 2):
        exact, jsum, n = 0, 0.0, 0
        for oid in oracle_ids:
            sx, sy = extractor(x, oid), extractor(y, oid)
            n += 1
            if sx == sy:
                exact += 1
            jsum += jaccard(sx, sy)
        out[f"{x}-{y}"] = {"exact_match_rate": exact / n, "mean_jaccard": jsum / n}
    return out


def main():
    oracle_ids = b8._load_batch8_card_set()
    axes, missing = diff.parse_raw_results(b8.RAW_RESULTS_PATH)

    def lane_only(arm, oid, lane):
        return frozenset((l, lbl) for l, lbl in axes[arm][oid] if l == lane)

    def free_canon(arm, oid):
        return frozenset((l, fcon.canonicalize_label(lbl)) for l, lbl in axes[arm][oid] if l == "free")

    def full_canon(arm, oid):
        out = set()
        for lane, label in axes[arm][oid]:
            out.add((lane, fcon.canonicalize_label(label) if lane == "free" else label))
        return frozenset(out)

    raw = score_pairs(oracle_ids, lambda a, o: axes[a][o])
    codebook_lane = score_pairs(oracle_ids, lambda a, o: lane_only(a, o, "codebook"))
    free_raw = score_pairs(oracle_ids, lambda a, o: lane_only(a, o, "free"))
    free_canonicalized = score_pairs(oracle_ids, free_canon)
    blended_canonicalized = score_pairs(oracle_ids, full_canon)

    print("=== RAW (all axes, no canonicalization) ===")
    for pair, m in raw.items():
        print(f"{pair}: exact={m['exact_match_rate']:.1%}  jaccard={m['mean_jaccard']:.3f}")
    print("\n=== CODEBOOK-LANE ONLY ===")
    for pair, m in codebook_lane.items():
        print(f"{pair}: exact={m['exact_match_rate']:.1%}  jaccard={m['mean_jaccard']:.3f}")
    print("\n=== FREE-LANE, AFTER CANONICALIZATION (vs. raw free-lane) ===")
    for pair in free_raw:
        r, c = free_raw[pair], free_canonicalized[pair]
        print(f"{pair}: raw_exact={r['exact_match_rate']:.1%} -> canon_exact={c['exact_match_rate']:.1%}  "
              f"raw_jaccard={r['mean_jaccard']:.3f} -> canon_jaccard={c['mean_jaccard']:.3f}")

    print("\n=== VARIANCE DECOMPOSITION (free-lane): wording recovered vs. judgment survives ===")
    decomposition = {}
    for pair in free_raw:
        raw_dis = 1 - free_raw[pair]["exact_match_rate"]
        canon_dis = 1 - free_canonicalized[pair]["exact_match_rate"]
        recovered = (raw_dis - canon_dis) / raw_dis if raw_dis else 0.0
        survives = canon_dis / raw_dis if raw_dis else 0.0
        decomposition[pair] = {"wording_recovered_frac": recovered, "judgment_survives_frac": survives}
        print(f"{pair}: wording_recovered={recovered:.1%}  judgment_survives={survives:.1%}")
    print("(codebook-lane: 0% wording by construction -- labels are already exact existing slugs, "
          "100% of any disagreement there is real match/judgment divergence, not wording)")

    # --- Consensus design pricing (N=40, real batch-8 Arm C per-card cost) ---
    c_usage = {"input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 0, "c5m": 0, "c1h": 0, "n": 0}
    for line in b8.RAW_RESULTS_PATH.read_text().splitlines():
        row = json.loads(line)
        if not row["custom_id"].startswith("C-pack"):
            continue
        u = row["result"]["message"]["usage"]
        c_usage["input_tokens"] += u["input_tokens"]
        c_usage["cache_read_input_tokens"] += u["cache_read_input_tokens"]
        c_usage["output_tokens"] += u["output_tokens"]
        c_usage["c5m"] += u["cache_creation"].get("ephemeral_5m_input_tokens", 0)
        c_usage["c1h"] += u["cache_creation"].get("ephemeral_1h_input_tokens", 0)
        c_usage["n"] += 1
    arm_c_cost = (
        (c_usage["input_tokens"] / 1e6) * INTRO_IN_RATE
        + (c_usage["c5m"] / 1e6) * CACHE_5M_WRITE_RATE
        + (c_usage["c1h"] / 1e6) * CACHE_1H_WRITE_RATE
        + (c_usage["cache_read_input_tokens"] / 1e6) * CACHE_READ_RATE
        + (c_usage["output_tokens"] / 1e6) * INTRO_OUT_RATE
    )
    per_card_cost_n40 = arm_c_cost / 1200  # batch 8's 1,200-card set
    single_pass_cost = CORPUS_SIZE * per_card_cost_n40

    # B-D proxy (same-config N=20 repeat -- only same-harness-twice control we have)
    total_intersection, total_union, disputed_cards = 0, 0, 0
    for oid in oracle_ids:
        sb, sd = full_canon("B", oid), full_canon("D", oid)
        total_intersection += len(sb & sd)
        total_union += len(sb | sd)
        if sb != sd:
            disputed_cards += 1
    corroborated_frac_axis = total_intersection / total_union
    provisional_frac_axis = 1 - corroborated_frac_axis
    disputed_frac_card = disputed_cards / len(oracle_ids)

    design1_cost = 2 * single_pass_cost
    disputed_full_scale = round(CORPUS_SIZE * disputed_frac_card)
    third_pass_cost = disputed_full_scale * per_card_cost_n40
    design2_cost = design1_cost + third_pass_cost
    full_m3_cost = 3 * single_pass_cost

    p_third_matches_either = 1 - (1 - corroborated_frac_axis) ** 2
    design2_corroborated_est = (1 - disputed_frac_card) * 1.0 + disputed_frac_card * p_third_matches_either

    print(f"\n=== Consensus design pricing, N=40, intro batch rate ===")
    print(f"real per-card cost (Arm C actuals, {c_usage['n']} packs, 1,200 cards): ${per_card_cost_n40:.6f}")
    print(f"single N=40 pass over {CORPUS_SIZE:,} cards: ${single_pass_cost:.2f}")
    print()
    print(f"DESIGN 1 (M=2 intersection + provisional-singleton): ${design1_cost:.2f}")
    print(f"  corroborated axis-instances (B-D proxy): {corroborated_frac_axis:.1%}")
    print(f"  provisional axis-instances: {provisional_frac_axis:.1%}")
    print()
    print(f"DESIGN 2 (M=2 + targeted 3rd-run on disputed cards only): ${design2_cost:.2f}")
    print(f"  disputed cards (B-D proxy, full-set exact-match): {disputed_frac_card:.1%} "
          f"({disputed_full_scale:,}/{CORPUS_SIZE:,})")
    print(f"  3rd-run cost: ${third_pass_cost:.2f}  (vs. full M=3: ${full_m3_cost:.2f}, "
          f"saves ${full_m3_cost - design2_cost:.2f})")
    print(f"  [ESTIMATED, not measured -- no real 3-way data] projected corroborated after 3 runs: "
          f"{design2_corroborated_est:.1%}")
    print(f"  [ESTIMATED] projected still-provisional/halt-loudly: {1 - design2_corroborated_est:.1%}")

    fc.write_json(OUT_PATH, {
        "raw": raw, "codebook_lane": codebook_lane, "free_lane_raw": free_raw,
        "free_lane_canonicalized": free_canonicalized, "blended_canonicalized": blended_canonicalized,
        "variance_decomposition_free_lane": decomposition,
        "consensus_pricing": {
            "per_card_cost_n40": per_card_cost_n40,
            "single_pass_cost_full_corpus": single_pass_cost,
            "design1": {"cost": design1_cost, "corroborated_frac": corroborated_frac_axis,
                        "provisional_frac": provisional_frac_axis},
            "design2": {"cost": design2_cost, "disputed_frac_card": disputed_frac_card,
                        "disputed_cards_full_scale": disputed_full_scale, "third_pass_cost": third_pass_cost,
                        "full_m3_cost_comparison": full_m3_cost,
                        "projected_corroborated_estimated": design2_corroborated_est,
                        "note": "corroborated/provisional split for design2 is an ESTIMATE extrapolated from "
                                "pairwise (2-run) rates -- no real 3-way run exists to measure it directly"},
        },
    })
    print(f"\nwrote {OUT_PATH}")


if __name__ == "__main__":
    main()
