#!/usr/bin/env python3
"""MEASUREMENT-ONLY, read-only. Phase 1 of RULING-MANIFEST-2026-07-09.md.

Re-runs the Gate-0 DF-distribution measurement with PROVENANCE SEGREGATION:
every T1 `matchable_paragraph` TEXT is classified, by inspecting every one of
its corpus-wide occurrences, as native-only / M2-injected-only / mixed (same
discipline df_distributions.py already applied to T2's 5-grams -- extended
here to whole T1 paragraphs, which df_distributions.py's Deliverable 1 did
NOT segment).

Produces three SEPARATE native-only tables (R3): T1 long (>=5 tok, ngram-scale
DF), T1 short (<5 tok, para_exact_df), and reuses df_distributions.py's
already-native-segmented T2 fragment table. Locates every FINDINGS-MEMO
landmark on the clean tables and applies the manifest's Phase 1 DECISION RULE
against the provisional band edges (10/50/172 long, 5/39 short). Writes
nothing into tier_engine.py.

Run: python3 experiments/measure/clean_recut.py
"""
import sys
import json
import bisect
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import tier_engine as te  # noqa: E402

OUT_DIR = REPO_ROOT / "experiments" / "out" / "measurement"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PERCENTILES = [1, 5, 10, 25, 50, 75, 90, 95, 99, 99.5, 99.9, 100]

# R3 provisional band edges (manifest).
LONG_FULL_CEILING = 10
LONG_DISCOUNT_CEILING = 50
LONG_RESCUE_CEILING = 172
SHORT_FULL_CEILING = 5
SHORT_DISCOUNT_CEILING = 39

# (label, anchor_name, exact paragraph text, expected provenance)
SHORT_BOILERPLATE_LANDMARKS = [
    ("draw a card.", "draw a card."),
    ("this land enters tapped.", "this land enters tapped."),
    ("choose one —  (Boros Charm)", "choose one —"),
    ("{t}: add {c}. (mana-dork/rock skeleton)", "{t}: add {c}."),
    ("{t}: add {c}{c}. (Sol Ring/Ancient Tomb skeleton, printed for the record)", "{t}: add {c}{c}."),
]

LONG_M2_BOILERPLATE_LANDMARKS = [
    ("Swiftfoot Boots equip reminder",
     "{1}: attach to target creature you control. equip only as a sorcery."),
    ("Faithless Looting flashback reminder",
     "you may cast this card from your graveyard for its flashback cost. then exile it."),
    ("Mystic Remora cumulative upkeep reminder",
     "at the beginning of your upkeep, put an age counter on this permanent, then sacrifice it "
     "unless you pay its upkeep cost for each age counter on it."),
    ("Vandalblast overload reminder",
     "you may cast this spell for its overload cost. if you do, change \"target\" in its text to \"each.\""),
]

LANE_1C_FAMILY = [
    ("Growth Spiral", "Eureka Moment", 54),
    ("Garruk's Uprising", "Elemental Bond", 57),
    ("Cultivate", "Skyshroud Claim", 70),
    ("Rhystic Study", "Reparations", 77),
    ("Rampant Growth", "Natural Connection", 119),
    ("Deadly Dispute", "Village Rites", 128),
]


def percentile_value(sorted_vals, pct):
    if not sorted_vals:
        return None
    n = len(sorted_vals)
    idx = max(0, min(n - 1, int(round(pct / 100 * (n - 1)))))
    return sorted_vals[idx]


def percentile_of_value(sorted_vals, value):
    n = len(sorted_vals)
    if n == 0 or value is None:
        return None
    left = bisect.bisect_left(sorted_vals, value)
    return round(100 * left / n, 2)


def build_percentile_table(sorted_vals, label):
    lines = [f"\n-- Percentile table: {label} (n={len(sorted_vals):,}) --"]
    lines.append(f"{'percentile':>10} | {'raw DF':>10} | {'count <= DF':>12}")
    for p in PERCENTILES:
        v = percentile_value(sorted_vals, p)
        cnt = bisect.bisect_right(sorted_vals, v) if v is not None else 0
        lines.append(f"{p:>10} | {v!s:>10} | {cnt:>12,}")
    return "\n".join(lines)


def band_of(value, full_ceiling, discount_ceiling, rescue_ceiling=None):
    if value is None:
        return "UNDEFINED"
    if value <= full_ceiling:
        return "FULL WEIGHT"
    if value <= discount_ceiling:
        return "DISCOUNTED"
    if rescue_ceiling is not None and value <= rescue_ceiling:
        return "RESCUE ZONE (qualifies, buried)"
    return "DEAD"


def main():
    log = []

    def p(s=""):
        print(s)
        log.append(s)

    p("=" * 100)
    p("CLEAN-DATA RE-CUT (Phase 1, provenance-segregated) -- read-only, no engine changes")
    p("Reproduce with: python3 experiments/measure/clean_recut.py")
    p("=" * 100)

    cards = te.load_cards(te.CARDS_PATH)
    name_index = te.build_name_index(cards)
    card_docs = {oid: te.build_card_doc(c) for oid, c in sorted(cards.items())}
    paragraph_index, clause_index, clause_df, ngram_index, ngram_df = te.build_indexes(
        card_docs, te.NGRAM_MIN_LEN
    )
    p(f"loaded {len(cards):,} cards, {len(paragraph_index):,} distinct matchable paragraphs, "
      f"{len(ngram_df):,} distinct {te.NGRAM_MIN_LEN}-grams")

    # =====================================================================
    # Paragraph-level provenance classification (native / injected / mixed)
    # -- same discipline df_distributions.py already applied per-5-gram,
    #    extended here to whole T1 paragraph texts (R3/R1 scope).
    # =====================================================================
    native_oids_by_text = {}
    injected_oids_by_text = {}
    for oid in sorted(card_docs):
        doc = card_docs[oid]
        for face in doc["faces"]:
            injected_paragraphs = set(face["reminder_keyword_by_paragraph"].keys())
            for text in face["matchable_paragraphs"]:
                if text in injected_paragraphs:
                    injected_oids_by_text.setdefault(text, set()).add(oid)
                else:
                    native_oids_by_text.setdefault(text, set()).add(oid)

    native_only_texts = set()
    injected_only_texts = set()
    mixed_texts = set()
    for text in paragraph_index:
        has_native = text in native_oids_by_text
        has_injected = text in injected_oids_by_text
        if has_native and not has_injected:
            native_only_texts.add(text)
        elif has_injected and not has_native:
            injected_only_texts.add(text)
        else:
            mixed_texts.add(text)

    p(f"\nT1 paragraph provenance classification (all {len(paragraph_index):,} distinct texts, any exact_df):")
    p(f"  native-only:  {len(native_only_texts):,}")
    p(f"  M2-injected-only: {len(injected_only_texts):,}")
    p(f"  mixed (native+M2): {len(mixed_texts):,}")

    # =====================================================================
    # NATIVE-ONLY T1 LONG table (>=5 tok, ngram-scale DF -- T2's existing scale, R2)
    # =====================================================================
    p("\n" + "#" * 100)
    p("# NATIVE-ONLY T1 LONG-PARAGRAPH TABLE (>=5 tok, ngram_scale_df, exact_df>=2)")
    p("#" * 100)
    long_native = []
    for text in native_only_texts:
        exact_df = len(paragraph_index[text])
        if exact_df < 2:
            continue
        tokens = text.split()
        if len(tokens) < te.NGRAM_MIN_LEN:
            continue
        ng_df = te.ngram_df_estimate(tokens, ngram_df, te.NGRAM_MIN_LEN)
        long_native.append((text, exact_df, ng_df, len(tokens)))
    long_native_ng_sorted = sorted(t[2] for t in long_native)
    p(f"population: {len(long_native):,} distinct native-only long paragraph texts")
    p(build_percentile_table(long_native_ng_sorted, "T1 native-only LONG, ngram_scale_df"))

    # =====================================================================
    # NATIVE-ONLY T1 SHORT table (<5 tok, para_exact_df -- own metric/thresholds, R2)
    # =====================================================================
    p("\n" + "#" * 100)
    p("# NATIVE-ONLY T1 SHORT-PARAGRAPH TABLE (<5 tok, para_exact_df, exact_df>=2)")
    p("#" * 100)
    short_native = []
    for text in native_only_texts:
        exact_df = len(paragraph_index[text])
        if exact_df < 2:
            continue
        tokens = text.split()
        if len(tokens) >= te.NGRAM_MIN_LEN:
            continue
        short_native.append((text, exact_df, len(tokens)))
    short_native_exact_sorted = sorted(t[1] for t in short_native)
    p(f"population: {len(short_native):,} distinct native-only short paragraph texts")
    p(build_percentile_table(short_native_exact_sorted, "T1 native-only SHORT, para_exact_df"))

    # =====================================================================
    # Landmark placement + decision-rule verdicts
    # =====================================================================
    p("\n" + "#" * 100)
    p("# LANDMARK PLACEMENT ON THE CLEAN (NATIVE-ONLY) TABLES")
    p("#" * 100)

    all_verdicts_ok = True

    p("\n-- Short boilerplate/skeleton landmarks (native-only short table) --")
    for label, text in SHORT_BOILERPLATE_LANDMARKS:
        prov = (
            "native-only" if text in native_only_texts
            else "M2-injected-only" if text in injected_only_texts
            else "mixed" if text in mixed_texts
            else "NOT FOUND"
        )
        if text not in paragraph_index:
            p(f"  {label}: TEXT NOT FOUND in paragraph_index -- HALT, verify exact string. text={text!r}")
            all_verdicts_ok = False
            continue
        exact_df = len(paragraph_index[text])
        pctile = percentile_of_value(short_native_exact_sorted, exact_df) if prov == "native-only" else None
        band = band_of(exact_df, SHORT_FULL_CEILING, SHORT_DISCOUNT_CEILING)
        expect_dead_or_buried = band in ("DISCOUNTED", "DEAD")
        if "{c}{c}" in text:
            # printed for the record only, per Phase 1 instructions -- not a boilerplate verdict check.
            p(f"  {label} [{prov}]: para_exact_df={exact_df:,} (p{pctile!s}) band={band} -- printed for the record")
            continue
        if not expect_dead_or_buried:
            all_verdicts_ok = False
        p(
            f"  {label} [{prov}]: para_exact_df={exact_df:,} (p{pctile!s})  band={band}  "
            f"{'OK (dead/buried, as wanted)' if expect_dead_or_buried else 'VERDICT FLIP -- full weight, unwanted!'}"
        )

    p("\n-- Long M2-injected boilerplate landmarks (checked against long band edges; these are NOT in the")
    p("   native-only population by construction -- listed here for the decision-rule cross-check only) --")
    for label, text in LONG_M2_BOILERPLATE_LANDMARKS:
        prov = (
            "native-only" if text in native_only_texts
            else "M2-injected-only" if text in injected_only_texts
            else "mixed" if text in mixed_texts
            else "NOT FOUND"
        )
        if text not in paragraph_index:
            p(f"  {label}: TEXT NOT FOUND -- HALT. text={text!r}")
            all_verdicts_ok = False
            continue
        tokens = text.split()
        ng_df = te.ngram_df_estimate(tokens, ngram_df, te.NGRAM_MIN_LEN)
        band = band_of(ng_df, LONG_FULL_CEILING, LONG_DISCOUNT_CEILING, LONG_RESCUE_CEILING)
        expect_not_full = band != "FULL WEIGHT"
        if not expect_not_full:
            all_verdicts_ok = False
        p(
            f"  {label} [{prov}]: ngram_scale_df={ng_df}  band={band}  "
            f"{'OK (not full weight, as wanted)' if expect_not_full else 'VERDICT FLIP -- lands at full weight, unwanted!'}"
        )

    # gram-level provenance (same discipline as df_distributions.py Deliverable 2) --
    # needed because find_shared_fragment's returned span is a sub-paragraph window,
    # not necessarily a whole matchable_paragraph, so paragraph-level classification
    # above cannot answer whether THIS fragment is native-only.
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
                    (gram_injected if is_injected else gram_native).add(gram)

    p("\n-- Lane 1c six (native, long) -- must land in the RESCUE ZONE (51-172) on the clean scale --")
    for anchor_name, cand_name, doc_df in LANE_1C_FAMILY:
        a_doc = card_docs[te.resolve_anchor(anchor_name, cards, name_index)["oracle_id"]]
        c_doc = card_docs[te.resolve_anchor(cand_name, cards, name_index)["oracle_id"]]
        result = te.find_shared_fragment(a_doc, c_doc, ngram_df, te.NGRAM_MIN_LEN, ngram_floor=10**9)
        if result is None:
            p(f"  {anchor_name} vs {cand_name}: NO shared fragment found -- HALT, doc claim unverifiable")
            all_verdicts_ok = False
            continue
        frag_text, frag_df, frag_len = result
        frag_grams = list(te.ngrams_for_tokens(frag_text.split(), te.NGRAM_MIN_LEN))
        gram_provs = set()
        for g in frag_grams:
            is_nat, is_inj = g in gram_native, g in gram_injected
            gram_provs.add("mixed" if (is_nat and is_inj) else "native" if is_nat else "injected" if is_inj else "unknown")
        frag_prov = "native-only" if gram_provs == {"native"} else "/".join(sorted(gram_provs))
        # NOTE: "mixed" here means this exact 5-gram string ALSO occurs somewhere else in the
        # corpus inside an M2-injected reminder (a different card entirely) -- it does NOT mean
        # this anchor/candidate PAIR's own evidence is injected. Both sides of every Lane 1c pair
        # are native, hand-written text; R1's provenance discount keys on the PAIR's own evidence,
        # not on a third-party corpus-wide gram coincidence (same class of overlap as the
        # Hero-of-Bladehold case, already ratified BY DESIGN in df_distributions.py). Reported for
        # transparency only -- NOT a decision-rule verdict flip.
        band = band_of(frag_df, LONG_FULL_CEILING, LONG_DISCOUNT_CEILING, LONG_RESCUE_CEILING)
        is_rescue = band == "RESCUE ZONE (qualifies, buried)"
        if not is_rescue:
            all_verdicts_ok = False
        match_note = "MATCHES doc" if frag_df == doc_df else f"doc said {doc_df} (re-verify, not necessarily a flip)"
        p(
            f"  {anchor_name} vs {cand_name}: frag_df={frag_df} ({match_note})  gram_provenance={frag_prov} "
            f"(informational, see note)  band={band}  {'OK (rescue zone, as wanted)' if is_rescue else 'VERDICT FLIP!'}"
        )

    p("\n" + "=" * 100)
    if all_verdicts_ok:
        p("DECISION RULE: every landmark verdict holds on the clean (native-only) data.")
        p("ADOPTING the provisional band edges as ratified constants:")
        p(f"  LONG_FULL_WEIGHT_CEILING = {LONG_FULL_CEILING}")
        p(f"  LONG_DISCOUNT_CEILING = {LONG_DISCOUNT_CEILING}")
        p(f"  LONG_RESCUE_CEILING = {LONG_RESCUE_CEILING}  (DEAD above this)")
        p(f"  SHORT_FULL_WEIGHT_CEILING = {SHORT_FULL_CEILING}")
        p(f"  SHORT_DISCOUNT_CEILING = {SHORT_DISCOUNT_CEILING}  (DEAD above this)")
        p("Header note (per manifest): \"confirmed against native-only distributions.\"")
    else:
        p("DECISION RULE: at least one landmark verdict FLIPPED on the clean data.")
        p("HALTING per manifest instruction -- do not choose replacement numbers. Full clean tables above")
        p("are for Captain's review.")
    p("=" * 100)

    out_path = OUT_DIR / "clean_recut_report.txt"
    out_path.write_text("\n".join(log) + "\n", encoding="utf-8")
    print(f"\nwrote {out_path}")

    raw_path = OUT_DIR / "clean_recut_raw.json"
    raw_path.write_text(json.dumps({
        "t1_native_only_long_ngram_scale_df": long_native_ng_sorted,
        "t1_native_only_short_para_exact_df": short_native_exact_sorted,
        "counts": {
            "native_only_texts": len(native_only_texts),
            "injected_only_texts": len(injected_only_texts),
            "mixed_texts": len(mixed_texts),
        },
        "all_verdicts_ok": all_verdicts_ok,
    }, indent=0), encoding="utf-8")
    print(f"wrote {raw_path}")

    return 0 if all_verdicts_ok else 1


if __name__ == "__main__":
    sys.exit(main())
