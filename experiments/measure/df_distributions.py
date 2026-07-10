#!/usr/bin/env python3
"""MEASUREMENT-ONLY, read-only. Gate 0 of THESAURUS-REFINEMENT-PASS-1.

Imports tier_engine.py's own functions (never re-implements corpus logic)
to compute:
  (1) DF distribution for currently-qualifying Tier 1 paragraphs.
  (2) DF distribution for currently-qualifying Tier 2 fragments, pooled and
      segmented by provenance (native / M1 keyword-kinship / M2-injected /
      mixed).
Writes nothing into tier_engine.py; writes only report text under
experiments/out/measurement/ (already-gitignored experiments/out/ tree).

Run: python3 experiments/measure/df_distributions.py
(run twice to confirm determinism -- see bottom of output)
"""
import sys
import json
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import tier_engine as te  # noqa: E402

OUT_DIR = REPO_ROOT / "experiments" / "out" / "measurement"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PERCENTILES = [1, 5, 10, 25, 50, 75, 90, 95, 99, 99.5, 99.9, 100]

BOILERPLATE_LANDMARKS = [
    # (label, anchor_name, exact paragraph text, provenance)
    ("Boros Charm 'choose one —' header", "Boros Charm", "choose one —", "native"),
    ("Swiftfoot Boots equip reminder", "Swiftfoot Boots",
     "{1}: attach to target creature you control. equip only as a sorcery.", "M2-injected"),
    ("Faithless Looting flashback reminder", "Faithless Looting",
     "you may cast this card from your graveyard for its flashback cost. then exile it.", "M2-injected"),
    ("Mystic Remora cumulative upkeep reminder", "Mystic Remora",
     "at the beginning of your upkeep, put an age counter on this permanent, then sacrifice it "
     "unless you pay its upkeep cost for each age counter on it.", "M2-injected"),
    ("Vandalblast overload reminder", "Vandalblast",
     "you may cast this spell for its overload cost. if you do, change \"target\" in its text to \"each.\"",
     "M2-injected"),
    ("Black Market Connections timing opener", "Black Market Connections",
     "at the beginning of your first main phase, choose one or more —", "native"),
]

# Lane 1c wanted-but-rejected family: (anchor, candidate, doc-reported DF)
LANE_1C_FAMILY = [
    ("Growth Spiral", "Eureka Moment", 54),
    ("Garruk's Uprising", "Elemental Bond", 57),
    ("Cultivate", "Skyshroud Claim", 70),
    ("Rhystic Study", "Reparations", 77),
    ("Rampant Growth", "Natural Connection", 119),
    ("Deadly Dispute", "Village Rites", 128),
]


def percentile_value(sorted_vals, pct):
    """Nearest-rank percentile over an already-sorted ascending list."""
    if not sorted_vals:
        return None
    n = len(sorted_vals)
    idx = max(0, min(n - 1, int(round(pct / 100 * (n - 1)))))
    return sorted_vals[idx]


def percentile_of_value(sorted_vals, value):
    """Percentile rank (0-100) of `value` within sorted_vals via bisect."""
    import bisect
    n = len(sorted_vals)
    if n == 0:
        return None
    left = bisect.bisect_left(sorted_vals, value)
    return round(100 * left / n, 2)


def build_percentile_table(sorted_vals, label):
    lines = [f"\n-- Percentile table: {label} (n={len(sorted_vals):,}) --"]
    lines.append(f"{'percentile':>10} | {'raw DF':>10} | {'count <= DF':>12}")
    import bisect
    for p in PERCENTILES:
        v = percentile_value(sorted_vals, p)
        cnt = bisect.bisect_right(sorted_vals, v)
        lines.append(f"{p:>10} | {v:>10} | {cnt:>12,}")
    return "\n".join(lines)


HIST_EDGES = [1, 2, 3, 4, 5, 10, 15, 20, 30, 40, 50, 75, 100, 150, 200, 300, 500,
              1000, 2000, 5000, 10000, 20000, 40000, 10**9]


def build_histogram_table(sorted_vals, label):
    lines = [f"\n-- Histogram: {label} (n={len(sorted_vals):,}) --"]
    lines.append(f"{'DF range':>16} | {'count':>10} | {'upper-edge pctile':>18}")
    import bisect
    prev_edge = 0
    for edge in HIST_EDGES:
        lo = bisect.bisect_right(sorted_vals, prev_edge)
        hi = bisect.bisect_right(sorted_vals, edge)
        cnt = hi - lo
        if cnt == 0 and edge != HIST_EDGES[-1]:
            prev_edge = edge
            continue
        pct = round(100 * hi / len(sorted_vals), 2) if sorted_vals else 0
        edge_label = f"({prev_edge},{edge}]" if edge != HIST_EDGES[-1] else f">{prev_edge}"
        lines.append(f"{edge_label:>16} | {cnt:>10,} | {pct:>17}%")
        prev_edge = edge
    return "\n".join(lines)


def main():
    log = []

    def p(s=""):
        print(s)
        log.append(s)

    p("=" * 100)
    p("DF-DISTRIBUTION MEASUREMENT -- Gate 0, measurement-only")
    p("Reproduce with: python3 experiments/measure/df_distributions.py")
    p("=" * 100)

    cards = te.load_cards(te.CARDS_PATH)
    p(f"loaded {len(cards):,} cards from {te.CARDS_PATH}")
    name_index = te.build_name_index(cards)

    p("building card_docs (v2.9 mechanisms enabled -- current engine state, erratum 2)...")
    card_docs = {oid: te.build_card_doc(c) for oid, c in sorted(cards.items())}

    p("building corpus indexes (paragraph/clause/ngram/tag) via te.build_indexes()...")
    paragraph_index, clause_index, clause_df, ngram_index, ngram_df = te.build_indexes(
        card_docs, te.NGRAM_MIN_LEN
    )
    keyword_df = te.compute_keyword_df(card_docs)
    p(f"NGRAM_MIN_LEN={te.NGRAM_MIN_LEN}  NGRAM_DF_FLOOR={te.NGRAM_DF_FLOOR}")
    p(f"distinct matchable paragraphs: {len(paragraph_index):,}")
    p(f"distinct {te.NGRAM_MIN_LEN}-grams: {len(ngram_df):,}")
    p(f"distinct keywords (raw Scryfall arrays, corpus DF): {len(keyword_df):,}")

    # =====================================================================
    # DELIVERABLE 1 -- Tier 1 paragraph DF distribution
    # =====================================================================
    p("\n" + "#" * 100)
    p("# DELIVERABLE 1 -- Tier 1 paragraph DF distribution")
    p("#" * 100)
    p(
        "\nPopulation: distinct `matchable_paragraphs` texts with exact-string DF >= 2 "
        "(i.e. currently mint >=1 live Tier-1 pair via find_shared_paragraph -- it is a bare "
        "exact-string-equality check with NO length floor and NO DF gate, confirmed at "
        "tier_engine.py:1271-1281 / triage doc Lane 3)."
    )
    p(
        "Two DF metrics are reported, NOT unified, because they disagree in a load-bearing way "
        "-- see the flagged finding below the tables."
    )
    p(
        "  (a) para_exact_df  = count of distinct cards carrying this EXACT paragraph string "
        "(well-defined for every paragraph, any length; this is what find_shared_paragraph "
        "itself qualifies on today)."
    )
    p(
        "  (b) ngram_scale_df = te.ngram_df_estimate(tokens, ngram_df, NGRAM_MIN_LEN) applied to "
        "the paragraph's OWN tokens -- the exact function/scale find_shared_fragment already "
        "uses for Tier 2, i.e. the scale DRAFT RULING 1 needs if T1 and T2 are to share one band "
        "structure. UNDEFINED for paragraphs shorter than NGRAM_MIN_LEN=5 tokens (te.ngram_df_estimate "
        "returns None -- there is no 5-token window to measure)."
    )

    t1_qualifying = []  # (text, para_exact_df, ngram_scale_df_or_None, token_len)
    for text, oids in paragraph_index.items():
        exact_df = len(oids)
        if exact_df < 2:
            continue
        tokens = text.split()
        ng_df = te.ngram_df_estimate(tokens, ngram_df, te.NGRAM_MIN_LEN)
        t1_qualifying.append((text, exact_df, ng_df, len(tokens)))

    p(f"\ncurrently-qualifying T1 paragraphs (exact DF >= 2): {len(t1_qualifying):,} distinct texts")

    below_floor_len = [t for t in t1_qualifying if t[3] < te.NGRAM_MIN_LEN]
    at_or_above = [t for t in t1_qualifying if t[3] >= te.NGRAM_MIN_LEN]
    p(
        f"  -> {len(below_floor_len):,} of these are SHORTER than NGRAM_MIN_LEN({te.NGRAM_MIN_LEN}) "
        f"tokens -- ngram_scale_df is UNDEFINED for them. Total exact-DF mass of this short-paragraph "
        f"population: {sum(t[1] for t in below_floor_len):,} (cards) across {len(below_floor_len):,} "
        f"distinct texts."
    )
    p(f"  -> {len(at_or_above):,} are >= {te.NGRAM_MIN_LEN} tokens -- ngram_scale_df is defined for all of these.")

    # metric (a): exact-count DF, over ALL qualifying T1 paragraphs
    exact_df_sorted = sorted(t[1] for t in t1_qualifying)
    p(build_percentile_table(exact_df_sorted, "T1 paragraphs, metric (a) para_exact_df, ALL qualifying"))
    p(build_histogram_table(exact_df_sorted, "T1 paragraphs, metric (a) para_exact_df, ALL qualifying"))

    # metric (b): ngram-scale DF, only defined subset
    ng_df_sorted = sorted(t[2] for t in at_or_above)
    p(build_percentile_table(ng_df_sorted, "T1 paragraphs, metric (b) ngram_scale_df, len>=5 subset only"))
    p(build_histogram_table(ng_df_sorted, "T1 paragraphs, metric (b) ngram_scale_df, len>=5 subset only"))

    # top-20 by exact_df, for eyeballing what's driving the tail
    p("\n-- Top 20 T1-qualifying paragraphs by para_exact_df --")
    top20 = sorted(t1_qualifying, key=lambda t: (-t[1], t[0]))[:20]
    for text, exact_df, ng_df, tl in top20:
        p(f"  exact_df={exact_df:>6,}  ngram_scale_df={ng_df!s:>6}  tokens={tl:>3}  {text[:90]!r}")

    # ---- landmark placement ----
    p("\n-- Boilerplate landmark placement (Deliverable 1) --")
    for label, anchor_name, text, provenance in BOILERPLATE_LANDMARKS:
        oids = paragraph_index.get(text)
        if oids is None:
            p(f"  {label}: TEXT NOT FOUND in paragraph_index -- HALT, verify exact string. text={text!r}")
            continue
        exact_df = len(oids)
        tokens = text.split()
        ng_df = te.ngram_df_estimate(tokens, ngram_df, te.NGRAM_MIN_LEN)
        exact_pctile = percentile_of_value(exact_df_sorted, exact_df)
        ng_pctile = percentile_of_value(ng_df_sorted, ng_df) if ng_df is not None else None
        p(
            f"  {label} [{provenance}]: tokens={len(tokens)}  para_exact_df={exact_df:,} "
            f"(p{exact_pctile})  ngram_scale_df={ng_df!s} (p{ng_pctile!s})"
        )

    p("\n-- Lane 1c wanted-but-rejected family placement (re-verified via te.find_shared_fragment) --")
    for anchor_name, cand_name, doc_df in LANE_1C_FAMILY:
        a_doc = card_docs[te.resolve_anchor(anchor_name, cards, name_index)["oracle_id"]]
        c_doc = card_docs[te.resolve_anchor(cand_name, cards, name_index)["oracle_id"]]
        result = te.find_shared_fragment(a_doc, c_doc, ngram_df, te.NGRAM_MIN_LEN, ngram_floor=10**9)
        if result is None:
            p(f"  {anchor_name} vs {cand_name}: NO shared fragment found at all -- HALT, doc claim unverifiable")
            continue
        frag_text, frag_df, frag_len = result
        pctile = percentile_of_value(exact_df_sorted, frag_df)
        match_note = "MATCHES doc" if frag_df == doc_df else f"MISMATCH -- doc says {doc_df}"
        p(
            f"  {anchor_name} vs {cand_name}: frag_len={frag_len}  frag_df={frag_df} ({match_note})  "
            f"[not a T1 paragraph -- this is a T2 fragment match; listed here for cross-reference to "
            f"Deliverable 2's landmark table, not this T1 percentile column]  frag={frag_text[:80]!r}"
        )

    # =====================================================================
    # DELIVERABLE 2 -- Tier 2 fragment DF distribution, pooled + segmented
    # =====================================================================
    p("\n" + "#" * 100)
    p("# DELIVERABLE 2 -- Tier 2 fragment DF distribution (pooled + 3 segments)")
    p("#" * 100)
    p(
        "\nPopulation for the TEXT-based segments: the base 5-gram dictionary itself (ngram_df), "
        "restricted to df<=NGRAM_DF_FLOOR (currently-qualifying 5-grams -- the atomic unit "
        "find_shared_fragment's floor check runs on via ngram_df_estimate = min over constituent "
        "5-token windows). A longer qualifying fragment's reported DF (e.g. Growth Spiral's 54) IS "
        "the DF of one of these constituent 5-grams, so this population is the correct, non-redundant "
        "measurement unit -- NOT a re-enumeration of every anchor/candidate pair (corpus-scale pairwise "
        "enumeration is not tractable and not what 'qualifying fragments' means here)."
    )
    p(
        "Provenance is assigned PER DISTINCT 5-GRAM by inspecting every occurrence corpus-wide: if "
        "every occurrence's source paragraph is in that face's reminder_keyword_by_paragraph (v2.9 M2 "
        "injection), the gram is 'M2 reminder-injected'; if none are, it's 'native oracle text'; if "
        "BOTH occur (a card's native text and another card's injected reminder happen to share the "
        "same 5-gram), it is kept as its OWN 'mixed (native+M2)' bucket rather than force-folded into "
        "either -- this is exactly the Hero-of-Bladehold-class overlap the v2.9 erratum note ratified "
        "as BY DESIGN, and silently bucketing it would misrepresent the measurement. This is a 4-way "
        "split, not the 3 named in the prompt, because the mixed case is real and non-trivial; flagged "
        "here rather than silently resolved one way."
    )
    p(
        "M1 (keyword-kinship pseudo-fragment) population is NOT text at all: it is "
        "te.compute_keyword_df() filtered to keywords with 2 <= DF <= floor -- the exact same "
        "qualifying set keyword_kinship_match() can ever actually match on (DF=1 means only one card "
        "carries that keyword, so it can never be SHARED with a candidate -- same reasoning as the "
        "T1 exact_df>=2 filter above, applied here for consistency; the raw compute_keyword_df() output "
        "contains many DF=1 entries that would otherwise silently dominate a naive count). Its DF unit "
        "(distinct cards carrying that keyword name) is on the SAME 'count of distinct oracle_id' scale "
        "as ngram DF, so pooling is unit-consistent, but the population SIZE is drastically smaller "
        "(dozens vs thousands) -- flagged so the pooled histogram isn't misread as three comparably-"
        "weighted sources."
    )

    # classify each 5-gram's provenance
    gram_native = set()
    gram_injected = set()
    for oid in sorted(card_docs):
        doc = card_docs[oid]
        for face in doc["faces"]:
            injected_paragraphs = set(face["reminder_keyword_by_paragraph"].keys())
            for p_idx, tokens in enumerate(face["paragraph_tokens"]):
                para_text = face["matchable_paragraphs"][p_idx]
                is_injected = para_text in injected_paragraphs
                for gram in te.ngrams_for_tokens(tokens, te.NGRAM_MIN_LEN):
                    if is_injected:
                        gram_injected.add(gram)
                    else:
                        gram_native.add(gram)

    qualifying_grams = {g: df for g, df in ngram_df.items() if 2 <= df <= te.NGRAM_DF_FLOOR}
    native_only = [df for g, df in qualifying_grams.items() if g in gram_native and g not in gram_injected]
    injected_only = [df for g, df in qualifying_grams.items() if g in gram_injected and g not in gram_native]
    mixed = [df for g, df in qualifying_grams.items() if g in gram_native and g in gram_injected]
    assert len(native_only) + len(injected_only) + len(mixed) == len(qualifying_grams)

    m1_qualifying = [df for kw, df in keyword_df.items() if 2 <= df <= te.NGRAM_DF_FLOOR]
    m1_df1_count = sum(1 for kw, df in keyword_df.items() if df == 1)
    p(f"\n(discarded {m1_df1_count:,} keywords at DF=1 -- singleton, can never be a shared kinship match)")

    p(f"qualifying 5-grams total (2<=df<=floor={te.NGRAM_DF_FLOOR}): {len(qualifying_grams):,}")
    p(f"  native oracle text only:  {len(native_only):,}")
    p(f"  M2 reminder-injected only: {len(injected_only):,}")
    p(f"  mixed (native + M2):       {len(mixed):,}")
    p(f"qualifying M1 keyword-kinship pseudo-fragments (0<df<=floor): {len(m1_qualifying):,}")

    pooled = sorted(list(qualifying_grams.values()) + m1_qualifying)
    p(build_percentile_table(pooled, "T2 pooled (native+M2+mixed 5-grams + M1 keywords)"))
    p(build_histogram_table(pooled, "T2 pooled (native+M2+mixed 5-grams + M1 keywords)"))

    for seg_vals, seg_label in [
        (sorted(native_only), "T2 segment: native oracle text 5-grams"),
        (sorted(injected_only), "T2 segment: M2 reminder-injected 5-grams"),
        (sorted(mixed), "T2 segment: mixed native+M2 5-grams"),
        (sorted(m1_qualifying), "T2 segment: M1 keyword-kinship pseudo-fragments"),
    ]:
        p(build_percentile_table(seg_vals, seg_label))
        p(build_histogram_table(seg_vals, seg_label))

    p("\n-- Landmark placement on the T2 fragment scale --")
    p("(boilerplate M2-injected reminder paragraphs: min-window ngram_scale_df of the FULL reminder,")
    p(" i.e. the same metric (b) computed in Deliverable 1 -- these are >=5 tokens, so it IS defined)")
    for label, anchor_name, text, provenance in BOILERPLATE_LANDMARKS:
        tokens = text.split()
        if len(tokens) < te.NGRAM_MIN_LEN:
            p(f"  {label}: SKIPPED, {len(tokens)} tokens < NGRAM_MIN_LEN -- no T2 fragment scale value exists")
            continue
        ng_df = te.ngram_df_estimate(tokens, ngram_df, te.NGRAM_MIN_LEN)
        pctile = percentile_of_value(pooled, ng_df)
        above = "ABOVE floor (excluded from T2 today)" if ng_df > te.NGRAM_DF_FLOOR else "at/below floor (qualifies today)"
        p(f"  {label} [{provenance}]: ngram_scale_df={ng_df}  pooled-pctile={pctile}  {above}")

    p("\n(Lane 1c family already placed against the raw 5-gram/fragment DF scale in Deliverable 1's")
    p(" landmark block above -- those DF values ARE this population's own unit, so no separate table here.)")

    # write outputs
    out_path = OUT_DIR / "df_distributions_report.txt"
    out_path.write_text("\n".join(log) + "\n", encoding="utf-8")
    print(f"\nwrote {out_path}")

    raw_data_path = OUT_DIR / "df_distributions_raw.json"
    raw_data_path.write_text(json.dumps({
        "t1_exact_df": exact_df_sorted,
        "t1_ngram_scale_df": ng_df_sorted,
        "t2_native_only": sorted(native_only),
        "t2_injected_only": sorted(injected_only),
        "t2_mixed": sorted(mixed),
        "t2_m1_keywords": sorted(m1_qualifying),
        "t2_pooled": pooled,
    }, indent=0), encoding="utf-8")
    print(f"wrote {raw_data_path}")


if __name__ == "__main__":
    main()
