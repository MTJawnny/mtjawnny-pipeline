#!/usr/bin/env python3
"""MEASUREMENT-ONLY, read-only. Gate 0 of THESAURUS-REFINEMENT-PASS-1,
Deliverable 3: pip-normalization impact measurement (DRAFT RULING 2 step 2).

Builds a SCRATCH pip-normalized copy of the fragment/paragraph index --
tier_engine.py itself is never imported for its mutation, only for its
loading/tokenization/DF-estimate primitives, which are reused unmodified.
Nothing is written back into tier_engine.py or any of its cached indexes.

Two-placeholder scheme per Captain's ruling:
  <mana> -- any color-producing symbol. A hybrid symbol ({W/U}, {2/W}, ...)
            normalizes as a SINGLE <mana> pip, not two.
  <n>    -- generic/colorless amounts. {C}-count and numeral equivalence:
            a maximal glued run of {C}/digit symbols collapses to ONE <n>,
            so {C}{C} and {2} normalize identically (both directions).
  {T}    -- stays LITERAL (a cost, not a product) -- never touched.
  {X}/{Y}/{Z} -- variable amounts. NOT folded into <n> (ruling: report as
            their own labeled subgroup, flag if anomalous). Normalized to a
            separate <var> placeholder so they can never silently collide
            with a fixed-amount <n> skeleton; every skeleton touching a var
            symbol is called out separately in every table below.
  anything else ({S}, {E}, {Q}, {P} alone, ...) -- left LITERAL and logged
  as "unhandled" rather than guessed at; halt-loudly discipline applied to
  the measurement itself, not just the engine.

Run: python3 experiments/measure/pip_normalization.py
(run twice to confirm determinism)
"""
import sys
import re
import json
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import tier_engine as te  # noqa: E402

OUT_DIR = REPO_ROOT / "experiments" / "out" / "measurement"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SYMBOL_RE = re.compile(r"\{([^{}]+)\}")


def classify_symbol(content: str) -> str:
    c = content.lower()
    if c == "t":
        return "literal_t"
    if c in ("x", "y", "z"):
        return "var"
    if c.isdigit():
        return "generic"
    if c == "c":
        return "generic"
    if "/" in c:
        return "color"  # hybrid (incl. phyrexian hybrid like w/p) -- single <mana> pip
    if c in ("w", "u", "b", "r", "g"):
        return "color"
    return "unhandled"


def normalize_pips(text: str):
    """Returns (normalized_text, has_var, unhandled_symbols_set).
    Operates on already-normalize_clause_text'd (lowercased) paragraph text.
    Glued runs (no characters between a symbol's '}' and the next '{') are
    the unit of analysis -- a generic-class run collapses to one <n>; every
    non-generic symbol in the run gets its own placeholder, resetting the
    generic accumulator."""
    spans = [(m.start(), m.end(), m.group(1)) for m in SYMBOL_RE.finditer(text)]
    if not spans:
        return text, False, set()

    runs = [[spans[0]]]
    for s in spans[1:]:
        if s[0] == runs[-1][-1][1]:
            runs[-1].append(s)
        else:
            runs.append([s])

    out = []
    last = 0
    has_var = False
    unhandled = set()
    for run in runs:
        run_start, run_end = run[0][0], run[-1][1]
        out.append(text[last:run_start])
        parts = []
        pending_generic = False
        for (_s0, _s1, content) in run:
            kind = classify_symbol(content)
            if kind == "generic":
                pending_generic = True
                continue
            if pending_generic:
                parts.append("<n>")
                pending_generic = False
            if kind == "literal_t":
                parts.append("{t}")
            elif kind == "var":
                parts.append("<var>")
                has_var = True
            elif kind == "color":
                parts.append("<mana>")
            else:
                parts.append("{" + content + "}")
                unhandled.add(content)
        if pending_generic:
            parts.append("<n>")
        out.append("".join(parts))
        last = run_end
    out.append(text[last:])
    return "".join(out), has_var, unhandled


def main():
    log = []

    def p(s=""):
        print(s)
        log.append(s)

    p("=" * 100)
    p("PIP-NORMALIZATION IMPACT MEASUREMENT -- Gate 0, measurement-only, DRAFT RULING 2 step 2")
    p("Reproduce with: python3 experiments/measure/pip_normalization.py")
    p("=" * 100)

    cards = te.load_cards(te.CARDS_PATH)
    name_index = te.build_name_index(cards)
    p(f"loaded {len(cards):,} cards")

    card_docs = {oid: te.build_card_doc(c) for oid, c in sorted(cards.items())}

    # ---- Baseline (unnormalized) indexes, straight from tier_engine ----
    paragraph_index, _, _, ngram_index, ngram_df = te.build_indexes(card_docs, te.NGRAM_MIN_LEN)
    p(f"baseline: {len(paragraph_index):,} distinct matchable paragraphs, "
      f"{len(ngram_df):,} distinct {te.NGRAM_MIN_LEN}-grams")

    # ---- Build the SCRATCH pip-normalized paragraph universe ----
    # oracle_id -> list of (orig_paragraph_text, normalized_text, has_var, unhandled)
    unhandled_all = set()
    var_count = 0
    norm_paragraph_index = defaultdict(set)   # normalized text -> set(oracle_id)
    norm_ngram_df = defaultdict(int)          # normalized 5-gram -> distinct oracle_id count
    norm_ngram_seen_this_card = None

    # orig_text -> normalized_text (many-to-one), for the collapse-cluster analysis
    orig_to_norm = {}

    for oid in sorted(card_docs):
        doc = card_docs[oid]
        card_norm_ngrams = set()
        for face in doc["faces"]:
            for text in face["matchable_paragraphs"]:
                norm_text, has_var, unhandled = normalize_pips(text)
                orig_to_norm[text] = norm_text
                if has_var:
                    var_count += 1
                unhandled_all |= unhandled
                norm_paragraph_index[norm_text].add(oid)
                tokens = norm_text.split()
                card_norm_ngrams.update(te.ngrams_for_tokens(tokens, te.NGRAM_MIN_LEN))
        for ng in card_norm_ngrams:
            norm_ngram_df[ng] += 1

    p(f"\ndistinct ORIGINAL paragraphs touched by pip normalization "
      f"(contain >=1 mana symbol): {sum(1 for t in orig_to_norm if SYMBOL_RE.search(t)):,}")
    p(f"distinct NORMALIZED paragraphs after collapse: {len(norm_paragraph_index):,}")
    p(f"paragraphs whose normalization touched an {{X}}/{{Y}}/{{Z}} variable pip: {var_count:,}")
    if unhandled_all:
        p(f"UNHANDLED symbol contents encountered (left literal, flagged, not guessed at): "
          f"{sorted(unhandled_all)}")
    else:
        p("UNHANDLED symbol contents encountered: none (every symbol in the corpus classified "
          "as t / generic / color-hybrid / var)")

    # =====================================================================
    # (a) "Add"-family skeleton collapse
    # =====================================================================
    p("\n" + "#" * 100)
    p("# (a) 'Add'-family skeleton collapse")
    p("#" * 100)
    p(
        "\nPopulation: distinct ORIGINAL matchable_paragraph texts containing the token 'add' "
        "AND at least one mana symbol (paragraphs with 'add' but no symbol -- essentially none in "
        "practice -- are untouched by this normalization and excluded as out of scope)."
    )

    add_family_orig = sorted(
        t for t in orig_to_norm
        if "add" in t.split() and SYMBOL_RE.search(t)
    )
    p(f"distinct original 'Add'-family paragraph texts: {len(add_family_orig):,}")

    clusters = defaultdict(list)
    for t in add_family_orig:
        clusters[orig_to_norm[t]].append(t)

    multi = {norm: origs for norm, origs in clusters.items() if len(origs) > 1}
    p(f"distinct post-normalization 'Add'-family skeletons: {len(clusters):,}")
    p(f"skeletons that MERGE 2+ distinct original skeletons: {len(multi):,}")

    p("\n-- Merge clusters (skeleton -> pre-norm variants collapsed into it), sorted by cluster size --")
    for norm_text, origs in sorted(multi.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        post_exact_df = len(norm_paragraph_index[norm_text])
        post_ng_tokens = norm_text.split()
        post_ng_df = te.ngram_df_estimate(post_ng_tokens, norm_ngram_df, te.NGRAM_MIN_LEN)
        pre_dfs = [len(paragraph_index.get(o, ())) for o in origs]
        p(
            f"  {norm_text!r}\n"
            f"    post_exact_df={post_exact_df}  post_ngram_scale_df={post_ng_df!s}  "
            f"({len(origs)} pre-norm variants, pre_exact_dfs={pre_dfs})"
        )
        for o in origs:
            p(f"      <- {o!r}")

    # =====================================================================
    # (b) Arcane Signet vs Sol Ring family, floor position pre vs post
    # =====================================================================
    p("\n" + "#" * 100)
    p("# (b) Arcane Signet / Sol Ring family: floor position pre vs post normalization")
    p("#" * 100)

    def report_clause(label, card_name):
        card = te.resolve_anchor(card_name, cards, name_index)
        doc = card_docs[card["oracle_id"]]
        for face in doc["faces"]:
            for text in face["matchable_paragraphs"]:
                if "add" not in text.split():
                    continue
                norm_text = orig_to_norm[text]
                pre_ng = te.ngram_df_estimate(text.split(), ngram_df, te.NGRAM_MIN_LEN)
                post_exact = len(norm_paragraph_index[norm_text])
                post_ng = te.ngram_df_estimate(norm_text.split(), norm_ngram_df, te.NGRAM_MIN_LEN)
                pre_status = "undefined (<5 tok)" if pre_ng is None else (
                    "ABOVE floor" if pre_ng > te.NGRAM_DF_FLOOR else "at/below floor")
                post_status = "undefined (<5 tok)" if post_ng is None else (
                    "ABOVE floor" if post_ng > te.NGRAM_DF_FLOOR else "at/below floor")
                p(
                    f"  {label} ({card_name}): orig={text!r}\n"
                    f"    -> normalized={norm_text!r}\n"
                    f"    pre:  exact_df={len(paragraph_index.get(text, ())):,}  "
                    f"ngram_scale_df={pre_ng!s} [{pre_status}]\n"
                    f"    post: exact_df={post_exact:,}  ngram_scale_df={post_ng!s} [{post_status}]"
                )

    report_clause("Arcane Signet mana ability", "Arcane Signet")
    report_clause("Sol Ring mana ability", "Sol Ring")
    report_clause("Manalith mana ability (control, F2's confirmed collision partner)", "Manalith")
    report_clause("Mind Stone mana ability", "Mind Stone")

    p(
        "\nNote: F2 (sentence-final-period tokenization bug, CO-C, separate from this pip-normalization "
        "measurement) is NOT applied here -- these numbers reflect pip normalization ALONE, on top of "
        "today's punctuation behavior. Arcane Signet's own clause ends mid-sentence ('...in your "
        "commander's color identity.') so it is not period-glued the way the 8 absent creatures + "
        "Manalith are; that F2 interaction is orthogonal to pip normalization and already measured/"
        "diagnosed in TRIAGE-BATCH-1-similarity-corrections.md Lane 1a."
    )

    # =====================================================================
    # (c) top-20 post-normalization skeletons by DF (symbol-touched paragraphs only)
    # =====================================================================
    p("\n" + "#" * 100)
    p("# (c) Top-20 post-normalization skeletons by DF (symbol-touched paragraphs only)")
    p("#" * 100)
    p(
        "\nPopulation: normalized paragraph texts whose ORIGINAL form contained >=1 mana symbol "
        "(paragraphs untouched by normalization are excluded -- they cannot show an 'unwanted merge' "
        "since their text didn't change)."
    )
    symbol_touched_norms = {
        norm for orig, norm in orig_to_norm.items() if SYMBOL_RE.search(orig)
    }
    ranked = sorted(
        symbol_touched_norms,
        key=lambda n: (-len(norm_paragraph_index[n]), n),
    )[:20]
    for norm_text in ranked:
        exact_df = len(norm_paragraph_index[norm_text])
        ng_df = te.ngram_df_estimate(norm_text.split(), norm_ngram_df, te.NGRAM_MIN_LEN)
        n_pre_variants = len(clusters.get(norm_text, [])) if norm_text in clusters else "n/a (non-Add)"
        p(f"  post_exact_df={exact_df:>5,}  post_ngram_scale_df={ng_df!s:>6}  {norm_text!r}")

    out_path = OUT_DIR / "pip_normalization_report.txt"
    out_path.write_text("\n".join(log) + "\n", encoding="utf-8")
    print(f"\nwrote {out_path}")

    raw_path = OUT_DIR / "pip_normalization_raw.json"
    raw_path.write_text(json.dumps({
        "n_add_family_orig": len(add_family_orig),
        "n_add_family_skeletons": len(clusters),
        "n_add_family_merged_skeletons": len(multi),
        "var_touched_paragraphs": var_count,
        "unhandled_symbols": sorted(unhandled_all),
        "top20_post": [
            {"text": t, "exact_df": len(norm_paragraph_index[t]),
             "ngram_scale_df": te.ngram_df_estimate(t.split(), norm_ngram_df, te.NGRAM_MIN_LEN)}
            for t in ranked
        ],
    }, indent=0, sort_keys=True), encoding="utf-8")
    print(f"wrote {raw_path}")


if __name__ == "__main__":
    main()
