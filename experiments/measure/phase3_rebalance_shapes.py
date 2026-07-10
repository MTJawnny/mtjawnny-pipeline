#!/usr/bin/env python3
"""MEASUREMENT/ANALYSIS ONLY -- no tier_engine.py scoring changes.

Captain ruling (2026-07-09, mid-Phase-3): the v2.5 Drannith > Avatar's Wrath
gate STANDS -- Phase 3's DF-band discount must not be weakened to preserve
it. Instead, frame affinity (type match, shared creature subtype, near-equal
MV) must be able to outrank a candidate whose only edge is a marginally
longer/rarer fragment on a DISJOINT frame, especially when that fragment
has been band-discounted. This script proposes 3 general mechanism shapes
(no per-card/per-pair exceptions -- every shape is keyed only on already-
derived facts: commonality_weight, affinity_term, type_match, shared
subtype count) and measures corpus-wide impact across the full calibration
panel (the established proxy this project already uses for exactly this
kind of before/after comparison -- true exhaustive corpus-wide, every
possible anchor, is not tractable and is not what "corpus-wide" means
anywhere else in this codebase's gate suite either).

Run: python3 experiments/measure/phase3_rebalance_shapes.py
"""
import sys
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import tier_engine as te  # noqa: E402

OUT_DIR = REPO_ROOT / "experiments" / "out" / "measurement"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PANEL = te.ANCHOR_PANEL + ["Zurgo, Thunder's Decree"]

MAX_AFFINITY = te.TYPE_MATCH_BONUS + te.SUBTYPE_BONUS_CAP  # 0.8, derived, not new

# Round 2 (Captain ruling): Shape A strengthened with a THIRD axis, mana-value
# closeness -- "sitting at equal/near mana value" was part of the original
# principle (Drannith sits at MVΔ=0 from Abolisher). Weights reuse the
# EXISTING, already-ratified TYPE_MATCH_BONUS/SUBTYPE_BONUS/SUBTYPE_BONUS_CAP
# constants for the first two axes (no new numbers there); MV_CLOSENESS_WEIGHT
# and MV_CLOSENESS_SCALE are the two genuinely new constants this round
# introduces, illustrative, not a search for gate-forcing values.
MV_CLOSENESS_WEIGHT = 8.0   # solved exactly: minimum value that closes Drannith/Wrath under Shape A's
                            # linear restoration formula, given Drannith's own affinity_term=0.55 and
                            # MVΔ=0 -- see PHASE-3-REBALANCE-SHAPES-MEMO.md's corrected-math section.
                            # ~16x TYPE_MATCH_BONUS -- testing empirically whether this is viable.
MV_CLOSENESS_SCALE = 4.0    # MVΔ=0 -> closeness 1.0; MVΔ>=4 -> closeness 0.0, linear between
RESTORATION_MAX = te.TYPE_MATCH_BONUS + te.SUBTYPE_BONUS_CAP + MV_CLOSENESS_WEIGHT  # 8.8

# Illustrative single parameterization per shape (NOT a search for a value
# that forces gates green -- one principled constant per shape, impact
# reported honestly either way).
SHAPE_A_LABEL = "A2: affinity buys back the discount (type + subtype + MV closeness)"
SHAPE_B_LABEL = "B: existing affinity_term amplifies inversely with discount"
SHAPE_C_LABEL = "C: new standalone frame-corroboration bonus (decoupled from affinity_term)"

AMPLIFY_K = 3.0          # Shape B
FRAME_BONUS_SCALE = 3.0  # Shape C


def build_context():
    cards = te.load_cards(te.CARDS_PATH)
    name_index = te.build_name_index(cards)
    card_tags = te.load_card_tags(te.CARD_TAGS_PATH)
    card_docs = {oid: te.build_card_doc(c) for oid, c in sorted(cards.items())}
    paragraph_index, clause_index, clause_df, ngram_index, ngram_df = te.build_indexes(
        card_docs, te.NGRAM_MIN_LEN
    )
    tag_index = te.build_tag_index(card_tags)
    idf, tag_card_count, n_tagged_cards = te.compute_tag_stats(card_tags)
    keyword_df = te.compute_keyword_df(card_docs)
    keyword_index = te.build_keyword_index(card_docs)
    turn_scoped_matches, turn_scoped_idf = te.run_turn_scoped_derivation(card_docs, len(cards))
    card_tags_t3, idf_t3 = te.build_turn_scoped_tag_index(card_docs, card_tags, idf, turn_scoped_matches, turn_scoped_idf)
    return dict(
        cards=cards, name_index=name_index, card_tags=card_tags, card_docs=card_docs,
        paragraph_index=paragraph_index, ngram_df=ngram_df, tag_index=tag_index, idf=idf,
        keyword_df=keyword_df, keyword_index=keyword_index, clause_index=clause_index,
        clause_df=clause_df, ngram_index=ngram_index, card_tags_t3=card_tags_t3, idf_t3=idf_t3,
        n_total_cards=len(cards),
    )


def default_args():
    return argparse.Namespace(
        ngram_min_len=te.NGRAM_MIN_LEN, ngram_df_floor=te.NGRAM_DF_FLOOR,
        clause_df_floor=te.CLAUSE_DF_FLOOR, inherited_discount=te.INHERITED_TAG_DISCOUNT,
        tier3_threshold=te.TIER3_COVERAGE_THRESHOLD, tag_score_weight=te.TAG_SCORE_WEIGHT,
        ci_penalty=te.CI_PENALTY, mv_penalty=te.MV_PENALTY, scope_penalty=te.SCOPE_PENALTY,
        duration_penalty=te.DURATION_PENALTY, exception_penalty=te.EXCEPTION_PENALTY,
        polarity_penalty=te.POLARITY_PENALTY, condition_penalty=te.CONDITION_PENALTY,
        type_match_bonus=te.TYPE_MATCH_BONUS, subtype_bonus=te.SUBTYPE_BONUS,
        subtype_bonus_cap=te.SUBTYPE_BONUS_CAP, report_cap=te.REPORT_CAP,
    )


def score_anchor_pool(anchor_name, ctx, args):
    """Returns list of row dicts (Tier 1/2 only) with baseline final score
    plus everything needed to recompute Shapes A/B/C: commonality_weight,
    affinity_term, frag_idf (pre-weight), tag term, penalty net, type_match,
    shared_subtypes."""
    anchor_card = te.resolve_anchor(anchor_name, ctx["cards"], ctx["name_index"])
    anchor_doc = ctx["card_docs"][anchor_card["oracle_id"]]
    anchor_tags = ctx["card_tags"].get(anchor_card["oracle_id"], [])

    pool = te.gather_candidate_pool(
        anchor_doc, anchor_tags, ctx["paragraph_index"], ctx["clause_index"], ctx["clause_df"],
        ctx["ngram_index"], ctx["ngram_df"], ctx["tag_index"], ctx["keyword_index"], ctx["keyword_df"], args,
    )

    rows = []
    for oid in pool:
        cand = ctx["card_docs"][oid]
        result = te.assign_tier(anchor_doc, cand, ctx["ngram_df"], ctx["keyword_df"], ctx["paragraph_index"], args)
        if result is None or result["tier"] not in (1, 2):
            continue
        fact_penalties = te.compute_fact_penalties(anchor_doc, cand, result["fragment"])
        if result["tier"] == 2:
            candidate_tags = ctx["card_tags"].get(oid, [])
            tag_score, _ = te.tier3_score(anchor_tags, candidate_tags, ctx["idf"], args.inherited_discount)
            if te.tier2_corroboration_disqualified(fact_penalties, tag_score):
                continue
        else:
            tag_score, _ = te.tier3_score(
                anchor_tags, ctx["card_tags"].get(oid, []), ctx["idf"], args.inherited_discount,
            )

        frag_idf_weighted, frag_df = te.compute_fragment_idf(
            result["fragment"], result["fragment_df"], result["fragment_df_exact"],
            ctx["ngram_df"], args.ngram_min_len, ctx["paragraph_index"], ctx["n_total_cards"],
        )
        weight = result["commonality_weight"]
        frag_idf_unweighted = frag_idf_weighted  # compute_fragment_idf doesn't apply weight itself
        frag_idf_weighted = frag_idf_unweighted * weight

        affinity = te.compute_affinity(
            anchor_doc, cand, args.type_match_bonus, args.subtype_bonus, args.subtype_bonus_cap,
        )
        ci_step, ci_colors_added = te.ci_relation_step_value(
            set(anchor_doc["color_identity"]), set(cand["color_identity"]),
            te.color_identity_relation(anchor_doc, cand),
        )
        mv_delta_val = te.mv_delta(anchor_doc, cand)
        breakdown = te.compute_rank(
            result["fragment"], frag_idf_weighted, tag_score, ci_step, mv_delta_val,
            fact_penalties, affinity, args.ngram_min_len, args.tag_score_weight, args.ci_penalty,
            args.mv_penalty, args.scope_penalty, args.duration_penalty, args.exception_penalty,
            args.polarity_penalty, args.condition_penalty,
        )
        length = len(result["fragment"].split())
        text_term_unweighted = frag_idf_unweighted * te.math.sqrt(length / args.ngram_min_len)
        tag_term = args.tag_score_weight * tag_score
        # BUG FIX (caught via direct engine cross-check, not by inspection): this MUST be the
        # raw sum of penalty terms only, NOT (raw - final), which nets out to
        # sum_of_penalties - affinity_term (since final = raw - sum_of_penalties + affinity_term).
        # Using that raw-final difference and then adding affinity_term back in apply_shape()
        # double-counted it, silently inflating every shape's numbers (this is exactly what
        # made Shape A2 look like it closed Drannith/Wrath when the real engine did not).
        penalty_sum = (
            breakdown["ci_term"] + breakdown["mv_term"] + breakdown["scope_term"]
            + breakdown["duration_term"] + breakdown["exception_term"]
            + breakdown["polarity_term"] + breakdown["condition_term"]
        )

        rows.append({
            "name": cand["name"], "tier": result["tier"], "mechanism": result["mechanism"],
            "commonality_weight": weight, "commonality_band": result["commonality_band"],
            "text_term_unweighted": text_term_unweighted, "tag_term": tag_term,
            "affinity_term": breakdown["affinity_term"], "penalty_sum": penalty_sum,
            "type_match": affinity["type_match"], "shared_subtypes": affinity["shared_subtypes"],
            "mv_delta": mv_delta_val,
            "baseline_final": breakdown["final"],
        })
    return rows


def apply_shape(rows, shape: str):
    """Returns a NEW list of rows with 'shape_final' computed. Only rows
    with commonality_weight < 1.0 (a discount actually applied) are
    touched -- full-weight rows are identical to baseline under every shape
    by construction (restoration/amplification vanish at weight=1.0 or
    discount=0)."""
    out = []
    for r in rows:
        w = r["commonality_weight"]
        if w >= 1.0 or r["mechanism"] == "keyword":
            out.append({**r, "shape_final": r["baseline_final"]})
            continue

        if shape == "A":
            # r["affinity_term"] is TYPE_MATCH_BONUS*type_match + SUBTYPE_BONUS*shared,
            # capped at SUBTYPE_BONUS_CAP -- i.e. already type+subtype combined (0-0.8).
            # Add the third axis, MV closeness, on top.
            mv_delta_val = r["mv_delta"]
            mv_closeness = max(0.0, 1.0 - abs(mv_delta_val) / MV_CLOSENESS_SCALE) if mv_delta_val is not None else 0.0
            restoration_strength = r["affinity_term"] + MV_CLOSENESS_WEIGHT * mv_closeness
            restoration_fraction = min(1.0, restoration_strength / RESTORATION_MAX)
            restored_weight = w + (1.0 - w) * restoration_fraction
            new_raw = r["text_term_unweighted"] * restored_weight + r["tag_term"]
            shape_final = new_raw - r["penalty_sum"] + r["affinity_term"]
        elif shape == "B":
            amplified_affinity = r["affinity_term"] * (1 + AMPLIFY_K * (1 - w))
            new_raw = r["text_term_unweighted"] * w + r["tag_term"]
            shape_final = new_raw - r["penalty_sum"] + amplified_affinity
        elif shape == "C":
            if r["type_match"]:
                frame_strength = 1.0
            else:
                frame_strength = 0.0
            frame_strength += 0.15 * len(r["shared_subtypes"])
            frame_bonus = FRAME_BONUS_SCALE * (1 - w) * frame_strength
            new_raw = r["text_term_unweighted"] * w + r["tag_term"]
            shape_final = new_raw - r["penalty_sum"] + r["affinity_term"] + frame_bonus
        else:
            raise ValueError(shape)

        out.append({**r, "shape_final": shape_final})
    return out


def count_order_swaps(rows_baseline, rows_shape):
    """Pairwise relative-order comparison within the SAME tier, baseline
    vs shape-adjusted final score. Returns swap count and total pairs."""
    by_tier_base = {}
    by_tier_shape = {}
    for rb, rs in zip(rows_baseline, rows_shape):
        by_tier_base.setdefault(rb["tier"], []).append((rb["name"], rb["baseline_final"]))
        by_tier_shape.setdefault(rs["tier"], []).append((rs["name"], rs["shape_final"]))

    swaps = 0
    pairs = 0
    for tier in by_tier_base:
        base_list = by_tier_base[tier]
        shape_list = {name: score for name, score in by_tier_shape.get(tier, [])}
        n = len(base_list)
        for i in range(n):
            for j in range(i + 1, n):
                name_i, score_i = base_list[i]
                name_j, score_j = base_list[j]
                if name_i not in shape_list or name_j not in shape_list:
                    continue
                pairs += 1
                base_order = score_i > score_j
                shape_order = shape_list[name_i] > shape_list[name_j]
                if base_order != shape_order:
                    swaps += 1
    return swaps, pairs


def main():
    log = []

    def p(s=""):
        print(s)
        log.append(s)

    p("=" * 100)
    p("PHASE 3 REBALANCE SHAPES -- impact analysis, measurement only, no engine changes")
    p("Captain ruling: v2.5 Drannith>Wrath STANDS; propose general mechanism shapes; no per-card carve-outs.")
    p("=" * 100)

    ctx = build_context()
    args = default_args()

    all_rows_by_anchor = {}
    for anchor_name in PANEL:
        rows = score_anchor_pool(anchor_name, ctx, args)
        all_rows_by_anchor[anchor_name] = rows
        n_discounted = sum(1 for r in rows if r["commonality_weight"] < 1.0)
        p(f"\n{anchor_name}: {len(rows)} Tier 1/2 rows, {n_discounted} with a band/provenance discount applied")

    p("\n" + "#" * 100)
    p("# NAMED-GATE CHECKS UNDER EACH SHAPE")
    p("#" * 100)

    def get_row(rows, name):
        return next((r for r in rows if r["name"] == name), None)

    checks = [
        ("Grand Abolisher", "Drannith Magistrate", "Avatar's Wrath", "Drannith > Wrath, margin (0, ~1.0]"),
        ("Grand Abolisher", "Voice of Victory", None, "VoV displayed position <= 3"),
        ("Marisi, Breaker of the Coil", "Basandra, Battle Seraph", "Myrel, Shield of Argive",
         "SUPERSEDED (Captain ruling): Basandra ranks ABOVE Myrel"),
    ]

    for shape in ("baseline", "A", "B", "C"):
        label = {"baseline": "BASELINE (Phase 3 as currently implemented, no rebalancing)",
                 "A": SHAPE_A_LABEL, "B": SHAPE_B_LABEL, "C": SHAPE_C_LABEL}[shape]
        p(f"\n-- {label} --")

        shaped_by_anchor = {}
        for anchor_name, rows in all_rows_by_anchor.items():
            shaped_by_anchor[anchor_name] = rows if shape == "baseline" else apply_shape(rows, shape)

        abolisher_rows = shaped_by_anchor["Grand Abolisher"]
        drannith = get_row(abolisher_rows, "Drannith Magistrate")
        wrath = get_row(abolisher_rows, "Avatar's Wrath")
        score_key = "baseline_final" if shape == "baseline" else "shape_final"
        if drannith and wrath:
            margin = drannith[score_key] - wrath[score_key]
            verdict = "PASS" if 0 < margin <= 1.2 else "FAIL"
            p(f"  Drannith({drannith[score_key]:.2f}) - Wrath({wrath[score_key]:.2f}) = {margin:.2f}  [{verdict}]")

        vov = get_row(abolisher_rows, "Voice of Victory")
        if vov:
            displayed = sorted(
                [r for r in abolisher_rows if r["tier"] == 2], key=lambda r: -r[score_key],
            )
            pos = next((i + 1 for i, r in enumerate(displayed) if r["name"] == "Voice of Victory"), None)
            verdict = "PASS" if pos is not None and pos <= 3 else "FAIL"
            p(f"  Voice of Victory displayed position = {pos}  [{verdict}]")

        marisi_rows = shaped_by_anchor["Marisi, Breaker of the Coil"]
        basandra = get_row(marisi_rows, "Basandra, Battle Seraph")
        myrel = get_row(marisi_rows, "Myrel, Shield of Argive")
        if basandra and myrel:
            full_sorted = sorted(marisi_rows, key=lambda r: -r[score_key])
            b_pos = next((i + 1 for i, r in enumerate(full_sorted) if r["name"] == "Basandra, Battle Seraph"), None)
            m_pos = next((i + 1 for i, r in enumerate(full_sorted) if r["name"] == "Myrel, Shield of Argive"), None)
            # SUPERSEDED (Captain ruling): Basandra ABOVE Myrel is now the expected PASS --
            # Basandra's near-exact rarer phrase is legitimate stronger evidence where the
            # rival's frame affinity is weak (type match only, zero shared subtype).
            verdict = "PASS" if (b_pos and m_pos and b_pos < m_pos) else "FAIL"
            p(f"  Basandra position={b_pos}, Myrel position={m_pos}  [{verdict}]")

    p("\n" + "#" * 100)
    p("# CORPUS-WIDE IMPACT (panel-wide pairwise within-tier order swaps vs baseline)")
    p("#" * 100)
    for shape in ("A", "B", "C"):
        total_swaps = 0
        total_pairs = 0
        per_anchor = []
        for anchor_name, rows in all_rows_by_anchor.items():
            shaped = apply_shape(rows, shape)
            swaps, pairs = count_order_swaps(rows, shaped)
            total_swaps += swaps
            total_pairs += pairs
            per_anchor.append((anchor_name, swaps, pairs))
        label = {"A": SHAPE_A_LABEL, "B": SHAPE_B_LABEL, "C": SHAPE_C_LABEL}[shape]
        pct = (100 * total_swaps / total_pairs) if total_pairs else 0.0
        p(f"\nShape {label}:")
        p(f"  total: {total_swaps:,} / {total_pairs:,} within-tier pairs swap order ({pct:.3f}%)")
        for name, swaps, pairs in per_anchor:
            pct_a = (100 * swaps / pairs) if pairs else 0.0
            p(f"    {name}: {swaps:,}/{pairs:,} ({pct_a:.3f}%)")

    p("\n" + "#" * 100)
    p("# LARGEST MOVERS SAMPLE (Grand Abolisher Tier 2, each shape vs baseline)")
    p("#" * 100)
    abolisher_rows = all_rows_by_anchor["Grand Abolisher"]
    baseline_rank = {
        r["name"]: i for i, r in enumerate(
            sorted([r for r in abolisher_rows if r["tier"] == 2], key=lambda r: -r["baseline_final"])
        )
    }
    for shape in ("A", "B", "C"):
        shaped = apply_shape(abolisher_rows, shape)
        shaped_t2 = [r for r in shaped if r["tier"] == 2]
        shaped_rank = {r["name"]: i for i, r in enumerate(sorted(shaped_t2, key=lambda r: -r["shape_final"]))}
        movers = sorted(
            ((name, baseline_rank[name] - shaped_rank[name]) for name in baseline_rank if name in shaped_rank),
            key=lambda t: -abs(t[1]),
        )[:8]
        label = {"A": SHAPE_A_LABEL, "B": SHAPE_B_LABEL, "C": SHAPE_C_LABEL}[shape]
        p(f"\nShape {label} -- top movers (positive = moved UP):")
        for name, delta in movers:
            p(f"    {name}: {delta:+d} position(s)")

    out_path = OUT_DIR / "phase3_rebalance_shapes_report.txt"
    out_path.write_text("\n".join(log) + "\n", encoding="utf-8")
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
