#!/usr/bin/env python3
"""WIRE STEP 1 — measure the codebook->tier_engine join OFFLINE.

Product-reality audit §9.1 item 1. Builds the join that `PRODUCT-REALITY-AUDIT-
2026-08-09.md` recommends -- `codebook.json` memberships fed into
`tier_engine`'s rule:-namespace-only derived index -- runs the engine's OWN
scoring twice, and diffs the neighbour lists.

**NOTHING SHIPS FROM THIS SCRIPT.** `tier_engine.py` is not edited and no
artifact is written outside `experiments/out/foundry/wire/`. The predictions it
is graded against are in `docs/WIRE-PREDICTIONS-2026-08-09.md`, committed
BEFORE this file existed (`d48eb4a`).

WHY IT DRIVES tier_engine RATHER THAN RE-IMPLEMENTING IT
-------------------------------------------------------
"A measurement probe must consume the SAME preprocessing as the classifier it
is measuring, or it under-reports silently" -- CLAUDE.md, and 21 probe defects
behind it. So this script imports `tier_engine` and calls `build_card_doc`,
`gather_candidate_pool`, `tier3_score` and `compute_candidate_rows` directly.
The ONLY thing it substitutes is the `(card_tags_t3, idf_t3, df_t3)` triple
that `build_turn_scoped_tag_index` returns -- which is precisely the wire, and
precisely what that function's own docstring says Step 5 grows.

THE POOL WIDENING IS PART OF THE WIRE, NOT AN EXTRA
---------------------------------------------------
`tier_engine.py:8049` widens the candidate pool to every turn-scoped card when
the anchor carries the tag, because `gather_candidate_pool` seeds only from the
base indexes and would otherwise never DISCOVER a card that shares nothing but
a derived tag. The join inherits that requirement per derived tag. Omitting it
would make the join measure as a smaller no-op than it is -- a false negative,
which is the failure mode this whole session exists to avoid.

Usage:
    python3 experiments/foundry_wire_experiment.py                # panel from predictions
    python3 experiments/foundry_wire_experiment.py --anchor "Reanimate"
    python3 experiments/foundry_wire_experiment.py --top 10
"""
import argparse
import collections
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
import tier_engine as te              # noqa: E402
import foundry_common as fc           # noqa: E402

CODEBOOK = REPO / "out" / "foundry" / "codebook.json"
OUT_DIR = REPO / "out" / "foundry" / "wire"

# The panel from docs/WIRE-PREDICTIONS-2026-08-09.md §3, in that order, with
# the CORRECT NEIGHBOURS that document named -- transcribed from the committed
# file (d48eb4a), never extended afterwards. Grading against a list written
# after the run is grading on whatever it produced.
#
# A/B/C/D are covered anchors; E is the DF-ceiling structural test; F/G are the
# two controls predicted byte-identical.
PANEL = {
    "Rampant Growth": ["Farseek", "Nature's Lore", "Three Visits", "Into the North",
                       "Search for Tomorrow", "Wood Elves", "Sakura-Tribe Elder",
                       "Skyshroud Claim", "Explosive Vegetation", "Harrow",
                       "Solemn Simulacrum"],
    "Beast Within": ["Generous Gift", "Rapid Hybridization", "Pongify",
                     "Chaos Warp", "Reality Shift"],
    "Reanimate": ["Animate Dead", "Necromancy", "Exhume", "Dance of the Dead",
                  "Stitch Together", "Victimize", "Corpse Dance", "Life // Death"],
    "Reliquary Tower": ["Thought Vessel", "Venser's Journal", "Spellbook",
                        "Kruphix, God of Horizons"],
    "Zurgo, Thunder's Decree": [],
    "Sol Ring": [],
    "Grand Abolisher": [],
}


# POST-HOC DIAGNOSTICS, not predictions. Cards OBSERVED leaving a displayed
# top-10 in the first run; tracked here only so the write-up can state where
# they went instead of asserting it. Kept separate from PANEL on purpose --
# PANEL is the committed prediction list (d48eb4a) and is never extended after
# a run, because a prediction edited afterwards grades nothing.
TRACK = {
    "Beast Within": ["Emergency Eject", "Excavation Technique", "Stroke of Midnight",
                     "Wild Magic Surge", "Saltblast", "Commander Sofia Daguerre"],
    "Reanimate": ["Unearth", "Recommission", "Danse Macabre", "Ghastly Conscription",
                  "Shadow of the Enemy", "Monster Mash-Up"],
}


def codebook_derived_index(n_total_cards: int, corpus_ids: set):
    """The JOIN. Returns (card_tags, idf, df) in build_turn_scoped_tag_index's
    exact shape, holding one entry per ACTIVE codebook membership.

    Every membership is `direct: True`: a codebook membership is an assertion
    about the card itself, never inherited through a parent (the parent layer
    is W9 and does not exist yet). `weight: "codebook"` mirrors the "engine"
    marker the turn-scoped entry carries -- provenance, never consumed by
    tier3_score.

    idf uses the identical convention as run_turn_scoped_derivation:
    log(n_total_cards / df). df is a genuine count, never back-derived from
    idf's log (Lesson 3's own rule, so derived_solo_qualifies has no
    floating-point round-trip risk).

    MEMBERSHIPS OUTSIDE THE ENGINE'S CORPUS ARE DROPPED AND REPORTED. The
    codebook is built over `load_corpus_gated()` (32,557 cards) and tier_engine
    reads the ungated jsonl (38,233) -- the gate is a POPULATION decision, so
    the two sets are not identical in either direction. A silently dropped
    membership would understate the join.
    """
    cb = json.loads(CODEBOOK.read_text(encoding="utf-8"))["axes"]
    live = collections.Counter(a.get("status") for a in cb.values())
    if "active" not in live:
        fc.halt("no axis in codebook.json carries status 'active'. A filter on "
                "an absent value matches NOTHING and reads as a clean no-op "
                f"result. Live values: {dict(live)}")

    by_card = collections.defaultdict(list)
    df = collections.Counter()
    dropped = 0
    for slug, axis in sorted(cb.items()):
        if axis.get("status") != "active":
            continue
        for m in (axis.get("members") or []):
            oid = m["oracle_id"]
            if oid not in corpus_ids:
                dropped += 1
                continue
            by_card[oid].append({"slug": slug, "direct": True, "weight": "codebook"})
            df[slug] += 1

    card_tags = {oid: sorted(tags, key=lambda t: t["slug"])
                 for oid, tags in by_card.items()}
    idf = {slug: math.log(n_total_cards / n) for slug, n in df.items() if n > 0}
    return card_tags, idf, dict(df), dropped


def merge_derived(base: tuple, extra: tuple) -> tuple:
    """Union two (card_tags, idf, df) triples. Halts on a slug collision --
    two different derivations claiming one slug would silently overwrite an
    idf and there is no correct answer to pick."""
    b_tags, b_idf, b_df = base
    e_tags, e_idf, e_df = extra
    clash = set(b_idf) & set(e_idf)
    if clash:
        fc.halt(f"derived-tag slug collision between the engine's own "
                f"derivations and the codebook: {sorted(clash)}. One would "
                f"silently overwrite the other's idf/df.")
    tags = {oid: list(v) for oid, v in b_tags.items()}
    for oid, v in e_tags.items():
        tags.setdefault(oid, [])
        tags[oid] = sorted(tags[oid] + list(v), key=lambda t: t["slug"])
    return tags, {**b_idf, **e_idf}, {**b_df, **e_df}


def widen_pool(pool: set, anchor_oid: str, card_tags_t3: dict) -> set:
    """tier_engine.py:8049 generalized to every derived tag.

    The engine widens to all turn-scoped cards when the anchor is turn-scoped,
    because gather_candidate_pool seeds only from the base Tagger/text indexes.
    A codebook-only neighbour is invisible for exactly the same reason, so the
    join carries the same widening or it measures its own blindness."""
    anchor_slugs = {t["slug"] for t in card_tags_t3.get(anchor_oid, [])}
    if not anchor_slugs:
        return pool
    holders = {oid for oid, tags in card_tags_t3.items()
               if any(t["slug"] in anchor_slugs for t in tags)}
    return pool | (holders - {anchor_oid})


def tier_names(tiers: dict, tier: int, top=None) -> list:
    rows = tiers[tier]
    return [r["name"] for r in (rows[:top] if top else rows)]


def rank_of(tiers: dict, name: str):
    """(tier, 1-based rank within that tier, score) for a named card, or None.

    Searched across ALL FOUR tiers, not just Tier 3. A predicted neighbour the
    engine already reaches at Tier 1/2 is not a miss -- reporting it as one
    would manufacture a gap the join then appears to close."""
    for t in (0, 1, 2, 3):
        for i, r in enumerate(tiers[t], 1):
            if r["name"] == name:
                return (t, i, r.get("_score"))
    return None


def tie_block(rows: list, top: int) -> tuple:
    """(size of the score-tie block the top-N sits inside, distinct scores in
    the top N). Tier 3 sorts by (-score, name), so a wide tie block means the
    displayed list is ordered ALPHABETICALLY, not by similarity -- which is a
    property of the BASE engine and must be measured, not asserted."""
    if not rows:
        return 0, 0
    head = rows[:top]
    distinct = len({round(r["_score"], 6) for r in head})
    first = round(head[0]["_score"], 6)
    block = sum(1 for r in rows if round(r["_score"], 6) == first)
    return block, distinct


def run_anchor(name, cards, card_docs, name_index, indexes, base_derived,
               joined_derived, args, n_total_cards):
    (paragraph_index, clause_index, clause_df, ngram_index, ngram_df,
     tag_index, keyword_index, keyword_df, mana_index, granted_keyword_index,
     vanilla_creature_index, card_tags, idf) = indexes

    anchor_card = te.resolve_anchor(name, cards, name_index)
    oid = anchor_card["oracle_id"]
    anchor_doc = card_docs[oid]
    anchor_tags = card_tags.get(oid, [])

    base_pool = te.gather_candidate_pool(
        anchor_doc, anchor_tags, paragraph_index, clause_index, clause_df,
        ngram_index, ngram_df, tag_index, keyword_index, keyword_df, mana_index,
        granted_keyword_index, args, vanilla_creature_index=vanilla_creature_index,
    )

    out = {}
    for label, (ct3, i3, d3) in (("base", base_derived), ("joined", joined_derived)):
        pool = widen_pool(set(base_pool), oid, ct3)
        tiers, _dq = te.compute_candidate_rows(
            anchor_doc, anchor_tags, ct3.get(oid, []), card_docs, card_tags, ct3,
            pool, ngram_df, clause_df, keyword_df, paragraph_index, idf, i3, d3,
            n_total_cards, args,
        )
        out[label] = {"tiers": tiers, "pool": len(pool)}

    return oid, anchor_card, out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--anchor", action="append", dest="anchors")
    ap.add_argument("--top", type=int, default=10,
                    help="displayed-list depth to diff (default 10 = REPORT_CAP)")
    ap.add_argument("--json", action="store_true", help="also write the raw diff")
    cli = ap.parse_args()
    anchors = cli.anchors or PANEL

    # Engine defaults, taken from tier_engine's own parser so a constant can
    # never drift between the engine and this harness.
    args = te.main.__globals__["argparse"].Namespace(
        cards_path=str(te.CARDS_PATH), card_tags_path=str(te.CARD_TAGS_PATH),
        clause_df_floor=te.CLAUSE_DF_FLOOR, ngram_min_len=te.NGRAM_MIN_LEN,
        ngram_df_floor=te.NGRAM_DF_FLOOR, inherited_discount=te.INHERITED_TAG_DISCOUNT,
        tier3_threshold=te.TIER3_COVERAGE_THRESHOLD, tag_score_weight=te.TAG_SCORE_WEIGHT,
        derived_weight=te.DERIVED_WEIGHT, ci_penalty=te.CI_PENALTY, mv_penalty=te.MV_PENALTY,
        scope_penalty=te.SCOPE_PENALTY, duration_penalty=te.DURATION_PENALTY,
        exception_penalty=te.EXCEPTION_PENALTY, polarity_penalty=te.POLARITY_PENALTY,
        condition_penalty=te.CONDITION_PENALTY, type_match_bonus=te.TYPE_MATCH_BONUS,
        subtype_bonus=te.SUBTYPE_BONUS, subtype_bonus_cap=te.SUBTYPE_BONUS_CAP,
        report_cap=te.REPORT_CAP, anchors=None,
    )

    print("standing up tier_engine (same path main() takes)...")
    cards = te.load_cards(te.CARDS_PATH)
    card_tags = te.load_card_tags(te.CARD_TAGS_PATH)
    raw_keyword_df = te.compute_keyword_df_from_cards(cards)
    card_docs = {oid: te.build_card_doc(c, keyword_df=raw_keyword_df)
                 for oid, c in cards.items()}
    n_total_cards = len(cards)
    keyword_vocabulary = te.build_keyword_vocabulary(cards)
    for doc in card_docs.values():
        doc["granted_keyword_facts"] = te.build_granted_keyword_facts(doc, keyword_vocabulary)

    (paragraph_index, clause_index, clause_df,
     ngram_index, ngram_df) = te.build_indexes(card_docs, args.ngram_min_len)
    tag_index = te.build_tag_index(card_tags)
    idf, _tag_card_count, _n_tagged = te.compute_tag_stats(card_tags)
    keyword_df = te.compute_keyword_df(card_docs)
    keyword_index = te.build_keyword_index(card_docs)
    mana_index = te.build_mana_pip_index(card_docs)
    granted_keyword_index = te.build_granted_keyword_index(card_docs)
    vanilla_creature_index = te.build_vanilla_creature_index(card_docs)
    name_index = te.build_name_index(cards)
    indexes = (paragraph_index, clause_index, clause_df, ngram_index, ngram_df,
               tag_index, keyword_index, keyword_df, mana_index,
               granted_keyword_index, vanilla_creature_index, card_tags, idf)

    # ---- the two derived indexes ----
    ts_matches = te.find_turn_scoped_matches(card_docs)
    ts_idf = math.log(n_total_cards / len(ts_matches)) if ts_matches else 0.0
    base_derived = te.build_turn_scoped_tag_index(ts_matches, ts_idf)
    cb_tags, cb_idf, cb_df, dropped = codebook_derived_index(n_total_cards, set(cards))
    joined_derived = merge_derived(base_derived, (cb_tags, cb_idf, cb_df))

    print(f"\nBASE derived index   : {len(base_derived[0]):,} cards, "
          f"{len(base_derived[1])} slug(s)  (rule:turn-scoped, DF={len(ts_matches):,})")
    print(f"JOINED derived index : {len(joined_derived[0]):,} cards, "
          f"{len(joined_derived[1])} slugs")
    print(f"  codebook memberships joined : {sum(cb_df.values()):,}")
    print(f"  dropped, oracle_id not in tier_engine's corpus : {dropped:,}")
    ceiling_ok = sum(1 for n in cb_df.values() if n <= te.DERIVED_QUALIFY_DF_CEILING)
    print(f"  axes at or under DERIVED_QUALIFY_DF_CEILING={te.DERIVED_QUALIFY_DF_CEILING}"
          f" (may solo-qualify) : {ceiling_ok} of {len(cb_df)}")

    report = {}
    for name in anchors:
        oid, anchor_card, out = run_anchor(
            name, cards, card_docs, name_index, indexes,
            base_derived, joined_derived, args, n_total_cards)

        anchor_slugs = sorted(t["slug"] for t in joined_derived[0].get(oid, []))
        print()
        print("=" * 78)
        print(f"{name}   ({len(anchor_slugs)} derived tag(s) after the join)")
        for s in anchor_slugs:
            df_v = joined_derived[2].get(s)
            gate = "may solo-qualify" if df_v <= te.DERIVED_QUALIFY_DF_CEILING else \
                   f"DF>{te.DERIVED_QUALIFY_DF_CEILING}, CANNOT solo-qualify"
            print(f"    {s}  (DF={df_v}, {gate})")
        print("=" * 78)

        b, j = out["base"], out["joined"]
        print(f"  candidate pool   {b['pool']:,} -> {j['pool']:,}")
        for t in (0, 1, 2, 3):
            nb, nj = len(b["tiers"][t]), len(j["tiers"][t])
            flag = "" if nb == nj else "   <-- MOVED"
            print(f"  tier {t} rows     {nb:>6,} -> {nj:>6,}{flag}")

        bt3 = {r["name"] for r in b["tiers"][3]}
        jt3 = {r["name"] for r in j["tiers"][3]}
        added, lost = sorted(jt3 - bt3), sorted(bt3 - jt3)
        print(f"  tier 3 members   +{len(added)}  -{len(lost)}")

        b_block, b_distinct = tie_block(b["tiers"][3], cli.top)
        j_block, j_distinct = tie_block(j["tiers"][3], cli.top)
        print(f"  tier 3 top-{cli.top} distinct scores  {b_distinct} -> {j_distinct}"
              f"   (leading tie block {b_block} -> {j_block} rows)")
        if b_block > cli.top:
            print(f"    ^ BASE displays an alphabetical slice of a {b_block}-row "
                  f"tie, not a ranking")

        b_top = tier_names(b["tiers"], 3, cli.top)
        j_top = tier_names(j["tiers"], 3, cli.top)
        if b_top == j_top:
            print(f"  displayed top-{cli.top}: IDENTICAL")
        else:
            print(f"  displayed top-{cli.top}: CHANGED")
            print(f"    {'BEFORE':<38} {'AFTER':<38}")
            for i in range(max(len(b_top), len(j_top))):
                lhs = b_top[i] if i < len(b_top) else ""
                rhs = j_top[i] if i < len(j_top) else ""
                mark = "  " if lhs == rhs else "* "
                print(f"    {mark}{lhs:<36} {rhs}")
        if added:
            print(f"  ADDED to tier 3 ({len(added)}) — read every one:")
            jrow = {r["name"]: r for r in j["tiers"][3]}
            for nm in added[:40]:
                print(f"    + {nm:<40} score={jrow[nm]['_score']:.3f}  "
                      f"{jrow[nm]['evidence'][:60]}")
            if len(added) > 40:
                print(f"    … {len(added) - 40} more (see --json)")
        if lost:
            print(f"  LOST from tier 3 ({len(lost)}):")
            for nm in lost[:40]:
                print(f"    - {nm}")

        # ---- grade against the PREDICTED correct neighbours (§3, committed
        # before this file existed). This is the only thing that answers
        # "did neighbour QUALITY improve" rather than "did rows move".
        predicted = PANEL.get(name, [])
        graded = []
        if predicted:
            print(f"  PREDICTED correct neighbours — tier/rank before -> after:")
            for pn in predicted:
                rb, rj = rank_of(b["tiers"], pn), rank_of(j["tiers"], pn)

                def fmt(x):
                    return "ABSENT" if x is None else f"T{x[0]}#{x[1]}"
                verdict = ""
                if rb is None and rj is None:
                    verdict = "  (unreached either way)"
                elif rb is None:
                    verdict = "  <-- GAINED"
                elif rj is None:
                    verdict = "  <-- LOST"
                elif rb[0] == 3 and rj[0] == 3 and rj[1] < rb[1]:
                    verdict = f"  <-- promoted {rb[1] - rj[1]}"
                elif rb[0] == 3 and rj[0] == 3 and rj[1] > rb[1]:
                    verdict = f"  <-- demoted {rj[1] - rb[1]}"
                print(f"    {pn:<34} {fmt(rb):>8} -> {fmt(rj):<8}{verdict}")
                graded.append({"name": pn, "before": rb, "after": rj})

        tracked = []
        if TRACK.get(name):
            print("  POST-HOC (not predictions) — cards seen leaving the display:")
            for tn in TRACK[name]:
                rb, rj = rank_of(b["tiers"], tn), rank_of(j["tiers"], tn)

                def fmt2(x):
                    return "ABSENT" if x is None else f"T{x[0]}#{x[1]}"
                delta = ""
                if rb and rj and rb[0] == rj[0]:
                    delta = f"  ({rj[1] - rb[1]:+d})"
                print(f"    {tn:<34} {fmt2(rb):>8} -> {fmt2(rj):<8}{delta}")
                tracked.append({"name": tn, "before": rb, "after": rj})

        report[name] = {
            "graded_predictions": graded,
            "tracked_posthoc": tracked,
            "top_scores_base": [
                {"name": r["name"], "score": r["_score"]} for r in b["tiers"][3][:cli.top]],
            "top_scores_joined": [
                {"name": r["name"], "score": r["_score"]} for r in j["tiers"][3][:cli.top]],
            "tie_block_base": b_block, "tie_block_joined": j_block,
            "oracle_id": oid, "derived_tags": anchor_slugs,
            "pool_base": b["pool"], "pool_joined": j["pool"],
            "tier_counts_base": {t: len(b["tiers"][t]) for t in (0, 1, 2, 3)},
            "tier_counts_joined": {t: len(j["tiers"][t]) for t in (0, 1, 2, 3)},
            "t3_added": added, "t3_lost": lost,
            "top_base": b_top, "top_joined": j_top,
            "t3_added_rows": [
                {"name": r["name"], "score": r["_score"], "evidence": r["evidence"]}
                for r in j["tiers"][3] if r["name"] in set(added)
            ],
        }

    if cli.json:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUT_DIR / "wire-diff.json"
        path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
