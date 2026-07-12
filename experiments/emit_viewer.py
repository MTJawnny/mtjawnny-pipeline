#!/usr/bin/env python3
"""v2.7 VIEWER EXPORT, extended v2.9/v2.10 -- additive tooling, zero scoring
changes.

Sibling script (not a --emit-viewer mode inside tier_engine.py), by design:
this keeps tier_engine.py's gated, halt-loudly report path completely
unaware of anything export-specific. This script IMPORTS tier_engine as a
library and calls its unmodified assign_tier()/compute_candidate_rows()/
compute_affinity()/run_turn_scoped_derivation()/etc. -- the exact same
functions tier_engine.py's own main() uses -- so there is no second scoring
implementation to drift out of sync. The only changes ever made to
tier_engine.py for this deliverable were additive (v2.7: two already-
computed values -- a Tier 1/2 row's fragment DF and whether it's exact --
captured onto the row dict instead of being discarded; v2.9: keyword_df/
keyword_index threading, all pre-existing and gate-verified there).

Two data sources, deliberately kept separate:
  - data/raw/oracle-cards.jsonl.gz + experiments/out/card-tags.json.gz:
    the SAME corpus tier_engine.py itself scores from -- loaded here only
    to call its scoring functions unchanged, and to source human-readable
    (non-normalized) display text for the anchor block.
  - data/artifacts/cards.sqlite: anchor-NAME RESOLUTION (per this change
    order's explicit instruction) and Commander LEGALITY. Verified present
    with real Scryfall values (legalities_commander: legal/not_legal/
    banned) -- verify_legality_column() halts loudly if a future snapshot
    schema drops that column, rather than improvising a legality source.

Anchor list: experiments/anchors.txt, one name per line (# comments and
blank lines ignored), seeded with the six approved anchors. Unlike
tier_engine.py's own resolve_anchor() (which halts loudly on any
ambiguity), THIS script prints and skips an unresolvable name -- 0 or >1
sqlite matches, or a resolved oracle_id absent from the jsonl corpus -- and
keeps going. A batch export tool must survive one bad line.

Scoring constants are read directly from tier_engine's module-level
constants (build_score_args()) -- NOT exposed as CLI flags here -- so this
tool can never silently diverge from tier_engine.py's own approved
defaults. If tier_engine.py's gates ever fail, this exporter has nothing
of its own to re-validate; run tier_engine.py itself and fix that first.

v2.10 (folded in per the v2.9 change order's own instruction): Tier 3 is
now exported too (name, score, shared tags with idf + direct/inherited,
MVΔ, CI relation, type bucket, legality) -- full list, display-only, ZERO
scoring changes; it calls the same compute_candidate_rows() Tier 3 branch
tier_engine.py's own reports use, including the v2.6 turn-scoped tag
extension (run_turn_scoped_derivation/build_turn_scoped_tag_index), so
Tier 3 here matches the reports exactly. Every run wipes the data/
directory first (an engine change makes any prior export stale).

Output: experiments/out/viewer/data/<anchor-slug>.json (Tiers 0/1/2/3,
FULL lists, not the report's top-10 cap) + experiments/out/viewer/data/
index.json. See viewer.html (sibling file) for the consumer.
"""
import argparse
import datetime as dt
import json
import shutil
import sqlite3
import sys
import time
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tier_engine as te  # noqa: E402  (path insert must precede this import)

ANCHORS_TXT = Path("experiments/anchors.txt")
VIEWER_DATA_DIR = Path("experiments/out/viewer/data")
SLOW_ANCHOR_THRESHOLD_SECONDS = 60

# v2.10 spot-check (Captain's ruling, printed non-blocking): does Zurgo's
# Tier 3 surface the "same effect, different words" cousins that Tier 1/2
# structurally cannot reach? Absence gets a full card-tags dump so the
# cause (tag-data gap vs overlap-threshold miss) is visible, not guessed.
ZURGO = "Zurgo, Thunder's Decree"
ZURGO_T3_SPOTCHECK_TARGETS = ["Hero of Bladehold", "Caesar, Legion's Emperor", "Gornog, the Red Reaper"]


def build_score_args() -> argparse.Namespace:
    """Hard-codes tier_engine.py's own approved module-level constants --
    deliberately not CLI-overridable here, so this exporter can never
    silently diverge from the gated engine's defaults. report_cap is
    irrelevant (the exporter always writes full lists) but tier_engine's
    functions expect the field to exist."""
    return argparse.Namespace(
        clause_df_floor=te.CLAUSE_DF_FLOOR, ngram_min_len=te.NGRAM_MIN_LEN,
        ngram_df_floor=te.NGRAM_DF_FLOOR, inherited_discount=te.INHERITED_TAG_DISCOUNT,
        tier3_threshold=te.TIER3_COVERAGE_THRESHOLD, tag_score_weight=te.TAG_SCORE_WEIGHT,
        ci_penalty=te.CI_PENALTY, mv_penalty=te.MV_PENALTY, scope_penalty=te.SCOPE_PENALTY,
        duration_penalty=te.DURATION_PENALTY, exception_penalty=te.EXCEPTION_PENALTY,
        polarity_penalty=te.POLARITY_PENALTY, condition_penalty=te.CONDITION_PENALTY,
        type_match_bonus=te.TYPE_MATCH_BONUS, subtype_bonus=te.SUBTYPE_BONUS,
        subtype_bonus_cap=te.SUBTYPE_BONUS_CAP, report_cap=10,
    )


def load_anchor_names(path: Path) -> list:
    if not path.exists():
        te.halt(f"{path} not found -- create it (one card name per line, # comments allowed)")
    names = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        names.append(line)
    if not names:
        te.halt(f"{path} has no anchor names (blank/comment-only)")
    return names


def verify_legality_column(conn: sqlite3.Connection, sqlite_path: Path) -> None:
    """Halts loudly (per CLAUDE.md house style) if cards.sqlite's schema no
    longer carries Commander legality -- never improvise a legality source."""
    cols = [row[1] for row in conn.execute("PRAGMA table_info(cards)").fetchall()]
    if "legalities_commander" not in cols:
        print(f"STOP — {sqlite_path} has no legalities_commander column.", file=sys.stderr)
        print(f"Actual `cards` table columns: {cols}", file=sys.stderr)
        sys.exit(1)


def resolve_anchor_sqlite(name: str, conn: sqlite3.Connection):
    """Returns an oracle_id, or None (already printed) if unresolvable.
    Unlike tier_engine.resolve_anchor(), this does NOT halt -- a batch
    export must survive one bad anchor line."""
    rows = conn.execute("SELECT oracle_id FROM cards WHERE name = ? COLLATE NOCASE", (name,)).fetchall()
    if len(rows) == 0:
        print(f"  [SKIP] {name!r}: no match in cards.sqlite")
        return None
    if len(rows) > 1:
        print(f"  [SKIP] {name!r}: ambiguous, {len(rows)} matches in cards.sqlite ({[r[0] for r in rows]})")
        return None
    return rows[0][0]


def build_anchor_display(card: dict, legal_commander) -> dict:
    """Human-readable anchor block sourced from the RAW (non-normalized)
    jsonl card dict -- tier_engine's own card_docs strip reminder text,
    substitute the card's name with '~', and lowercase everything for
    matching purposes, which is wrong for display."""
    faces = card.get("card_faces")
    if faces:
        mana_cost = " // ".join(f.get("mana_cost") or "" for f in faces)
        type_line = card.get("type_line") or " // ".join(f.get("type_line") or "" for f in faces)
        oracle_text = "\n//\n".join(f.get("oracle_text") or "" for f in faces)
    else:
        mana_cost = card.get("mana_cost") or ""
        type_line = card.get("type_line") or ""
        oracle_text = card.get("oracle_text") or ""
    return {
        "name": card["name"],
        "oracle_id": card["oracle_id"],
        "mana_cost": mana_cost,
        "type_line": type_line,
        "oracle_text": oracle_text,
        "color_identity": card.get("color_identity") or [],
        "subtypes": sorted(te.creature_subtypes(type_line)),
        "legal_commander": legal_commander,
    }


def is_land_doc(doc: dict) -> bool:
    """Candidate's OWN type line, not the anchor-relative type_bucket
    comparison column -- a lands/nonland filter needs to know what the
    candidate actually IS, independent of how it compares to the anchor."""
    return "Land" in te.type_bucket(doc["type_line"])


def build_row_export(row: dict, anchor_doc: dict, card_docs: dict, legality_by_oracle_id: dict) -> dict:
    oracle_id = row.get("oracle_id")
    candidate_doc = card_docs.get(oracle_id)
    keywords = te.keyword_overlap(anchor_doc, candidate_doc) if candidate_doc is not None else []
    is_land = is_land_doc(candidate_doc) if candidate_doc is not None else None
    breakdown = None
    if "_rank" in row:
        breakdown = {
            "raw": row["_raw_score"], "ci": row["_ci_term"], "mv": row["_mv_term"],
            "scope": row["_scope_term"], "dur": row["_duration_term"], "exc": row["_exception_term"],
            "pol": row["_polarity_term"], "cond": row["_condition_term"], "aff": row["_affinity_term"],
            "promo": row["_promoted_term"],
        }
    return {
        "name": row["name"],
        "oracle_id": oracle_id,
        "rank_score": row.get("_rank"),
        "breakdown": breakdown,
        "fragment": row.get("fragment"),
        "fragment_df": row.get("_fragment_df"),
        "fragment_df_exact": row.get("_fragment_df_exact"),
        "extra_fragments": row.get("_extra_fragments") or [],
        "corroboration": row.get("_corroboration") or [],
        "promoted": bool(row.get("_promoted")),
        "evidence": row.get("evidence"),
        "mv_delta": row.get("_mv_delta"),
        "ci_relation": row["facts"]["ci_relation"],
        "type_bucket": row["facts"]["type_bucket"],
        "keyword_overlap": keywords,
        "type_match": row.get("_type_match"),
        "shared_subtypes": row.get("_shared_subtypes"),
        "mechanism": row.get("_mechanism"),
        "keyword": row.get("_keyword"),
        "anchor_param": row.get("_anchor_param"),
        "candidate_param": row.get("_candidate_param"),
        "anchor_mana_fact": json_safe_mana_fact(row.get("_anchor_mana_fact")),
        "candidate_mana_fact": json_safe_mana_fact(row.get("_candidate_mana_fact")),
        "commonality_band": row.get("_commonality_band"),
        "commonality_weight": row.get("_commonality_weight"),
        "legal_commander": legality_by_oracle_id.get(oracle_id),
        "is_land": is_land,
    }


def json_safe_mana_fact(fact: dict):
    """Phase 4: mana_fact dicts carry a frozenset (colors), not directly
    JSON-serializable -- sorted list instead, order-independent per R5."""
    if fact is None:
        return None
    return {**fact, "colors": sorted(fact["colors"])}


def build_tier3_row_export(row: dict, anchor_doc: dict, card_docs: dict, legality_by_oracle_id: dict) -> dict:
    """v2.10: Tier 3 rows carry no rank breakdown (Tier 3 is tag-score-only,
    deliberately unpenalized -- a human-curation proposal queue) -- shape
    is name/score/shared_tags(idf+direct/inherited)/MVΔ/CI relation/type
    bucket/legality, per the change order."""
    oracle_id = row.get("oracle_id")
    candidate_doc = card_docs.get(oracle_id)
    mv_delta = te.mv_delta(anchor_doc, candidate_doc) if candidate_doc is not None else None
    is_land = is_land_doc(candidate_doc) if candidate_doc is not None else None
    return {
        "name": row["name"],
        "oracle_id": oracle_id,
        "score": row.get("_score"),
        "shared_tags": [
            {
                "slug": m["slug"], "idf": m["idf"],
                "anchor_direct": m["anchor_direct"], "candidate_direct": m["candidate_direct"],
            }
            for m in row.get("_matched_t3", [])
        ],
        "mv_delta": mv_delta,
        "ci_relation": row["facts"]["ci_relation"],
        "type_bucket": row["facts"]["type_bucket"],
        "legal_commander": legality_by_oracle_id.get(oracle_id),
        "is_land": is_land,
    }


def export_anchor(name: str, oracle_id: str, ctx: SimpleNamespace, out_dir: Path) -> dict:
    anchor_doc = ctx.card_docs[oracle_id]
    anchor_tags = ctx.card_tags.get(oracle_id, [])
    anchor_tags_t3 = ctx.card_tags_t3.get(oracle_id, [])

    start = time.perf_counter()
    pool = te.gather_candidate_pool(
        anchor_doc, anchor_tags, ctx.paragraph_index, ctx.clause_index, ctx.clause_df,
        ctx.ngram_index, ctx.ngram_df, ctx.tag_index, ctx.keyword_index, ctx.keyword_df,
        ctx.mana_index, ctx.granted_keyword_index, ctx.args,
        vanilla_creature_index=ctx.vanilla_creature_index,
    )
    # v2.6 amendment 2: widen the pool for turn-scoped Tier 3 discovery,
    # exactly mirroring tier_engine.py's own main() -- otherwise a candidate
    # sharing ONLY rule:turn-scoped with the anchor (no other overlap) would
    # never be found, since gather_candidate_pool seeds from base indexes only.
    if oracle_id in ctx.turn_scoped_matches:
        pool = pool | (set(ctx.turn_scoped_matches) - {oracle_id})
    full_tiers, _disqualified = te.compute_candidate_rows(
        anchor_doc, anchor_tags, anchor_tags_t3, ctx.card_docs, ctx.card_tags, ctx.card_tags_t3, pool,
        ctx.ngram_df, ctx.clause_df, ctx.keyword_df, ctx.paragraph_index, ctx.idf, ctx.idf_t3, ctx.n_total_cards, ctx.args,
    )
    elapsed = time.perf_counter() - start

    tiers_export = {}
    for t in (0, 1, 2):
        rows = [build_row_export(r, anchor_doc, ctx.card_docs, ctx.legality_by_oracle_id) for r in full_tiers[t]]
        tiers_export[str(t)] = {"count": len(rows), "rows": rows}
    tier3_rows = [build_tier3_row_export(r, anchor_doc, ctx.card_docs, ctx.legality_by_oracle_id) for r in full_tiers[3]]
    tiers_export["3"] = {"count": len(tier3_rows), "rows": tier3_rows}

    anchor_block = build_anchor_display(ctx.cards[oracle_id], ctx.legality_by_oracle_id.get(oracle_id))
    slug = te.filename_slug(name)
    data = {
        "anchor": anchor_block,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "corpus_cards": ctx.n_total_cards,
        "runtime_seconds": round(elapsed, 3),
        "tiers": tiers_export,
    }
    out_path = out_dir / f"{slug}.json"
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    if name == ZURGO:
        run_zurgo_t3_spotcheck(full_tiers, ctx.cards, ctx.card_docs, ctx.card_tags_t3)

    return {
        "name": name, "slug": slug, "file": out_path.name,
        "tier_counts": {t: tiers_export[t]["count"] for t in tiers_export},
        "runtime_seconds": round(elapsed, 3),
    }


def run_zurgo_t3_spotcheck(full_tiers: dict, cards: dict, card_docs: dict, card_tags_t3: dict) -> None:
    """v2.10 spot-check (Captain's ruling, printed, non-blocking): Zurgo's
    Tier 3 positions for Hero of Bladehold, Caesar Legion's Emperor, and
    Gornog the Red Reaper -- with shared-tag breakdowns. A target absent
    from Tier 3 gets checked against Tier 0/1/2 FIRST -- v2.9 Mechanism 1/2
    can promote a card OUT of Tier 3 entirely (zero verbatim overlap is
    Tier 3's own qualifying condition), which is a different, already-
    explained story from a genuine tag-data gap or overlap-threshold miss.
    Only a target absent from EVERY tier gets its full card-tags list
    printed, so the cause is visible from the printout, not guessed."""
    print(f"\nv2.10 Zurgo Tier 3 spot-check ({ZURGO}):")
    full_tier3 = full_tiers[3]
    by_name_t3 = {r["name"]: r for r in full_tier3}
    ordered = sorted(full_tier3, key=lambda r: (-r["_score"], r["name"]))
    position_by_name = {r["name"]: i + 1 for i, r in enumerate(ordered)}
    by_name_lower_tiers = {r["name"]: (t, r) for t in (0, 1, 2) for r in full_tiers[t]}
    name_index = te.build_name_index(cards)

    for target in ZURGO_T3_SPOTCHECK_TARGETS:
        row = by_name_t3.get(target)
        if row is not None:
            pos = position_by_name[target]
            tags_str = ", ".join(
                f"{m['slug']} (idf={m['idf']:.2f}, "
                f"{'direct' if m['anchor_direct'] and m['candidate_direct'] else 'inherited'})"
                for m in row.get("_matched_t3", [])[:6]
            )
            print(f"  {target}: Tier 3 position {pos}/{len(full_tier3)}, score={row['_score']:.2f} -- {tags_str}")
            continue

        promoted = by_name_lower_tiers.get(target)
        if promoted is not None:
            tier, prow = promoted
            print(
                f"  {target}: NOT in Tier 3 -- PROMOTED to Tier {tier} instead (v2.9 Mechanism "
                f"{'1/2' if prow.get('_mechanism') in ('keyword', 'reminder') else 'text'} gave it "
                f"verbatim overlap, which disqualifies it from Tier 3 by Tier 3's own definition). "
                f"evidence={prow.get('evidence')}"
            )
            continue

        try:
            target_card = te.resolve_anchor(target, cards, name_index)
        except SystemExit:
            print(f"  {target}: NOT in any tier, and unresolvable in the corpus -- check the name")
            continue
        target_tags = card_tags_t3.get(target_card["oracle_id"], [])
        print(f"  {target}: NOT in any tier (genuine gap). Full card-tags list ({len(target_tags)} tag(s)):")
        for t in sorted(target_tags, key=lambda t: t["slug"]):
            print(f"    {t['slug']} (direct={t['direct']})")


def load_export_context(cards_path: Path, card_tags_path: Path, cards_sqlite_path: Path) -> SimpleNamespace:
    """Loads the corpus + builds every index export_anchor() needs, and the
    Commander-legality lookup -- the SAME setup emit_viewer.py's own main()
    uses, factored out so serve_viewer.py's on-demand server can build the
    identical scoring context once at startup instead of re-implementing
    (and risking drifting from) this loading sequence."""
    if not cards_sqlite_path.exists():
        te.halt(f"{cards_sqlite_path} not found -- run the pipeline build first")
    conn = sqlite3.connect(f"file:{cards_sqlite_path}?mode=ro", uri=True)
    verify_legality_column(conn, cards_sqlite_path)

    print(f"loading legality index from {cards_sqlite_path}...")
    legality_by_oracle_id = {
        oracle_id: (legality == "legal")
        for oracle_id, legality in conn.execute("SELECT oracle_id, legalities_commander FROM cards")
    }
    print(f"  {len(legality_by_oracle_id):,} cards")

    print(f"\nloading corpus from {cards_path}...")
    cards = te.load_cards(cards_path)
    card_tags = te.load_card_tags(card_tags_path)
    print(f"  {len(cards):,} cards, tags for {len(card_tags):,}")

    print("normalizing corpus + building indexes (identical to tier_engine.py's own)...")
    # Bootstrap keyword DF from raw records BEFORE build_card_doc (2026-07-11):
    # strip_bespoke_ability_label() needs this to run inside build_card_doc
    # itself -- same ordering tier_engine.py's own main() uses, see
    # compute_keyword_df_from_cards()'s docstring for why this can't just be
    # compute_keyword_df(card_docs) reordered.
    raw_keyword_df = te.compute_keyword_df_from_cards(cards)
    card_docs = {oracle_id: te.build_card_doc(c, keyword_df=raw_keyword_df) for oracle_id, c in cards.items()}
    n_total_cards = len(cards)
    args = build_score_args()
    paragraph_index, clause_index, clause_df, ngram_index, ngram_df = te.build_indexes(card_docs, args.ngram_min_len)
    tag_index = te.build_tag_index(card_tags)
    keyword_df = te.compute_keyword_df(card_docs)
    keyword_index = te.build_keyword_index(card_docs)
    mana_index = te.build_mana_pip_index(card_docs)
    # Entry #4 (Captain's ruling, 2026-07-10): granted-keyword-SET facts,
    # same post-processing pattern as tier_engine.py's own main().
    keyword_vocabulary = te.build_keyword_vocabulary(cards)
    for doc in card_docs.values():
        doc["granted_keyword_facts"] = te.build_granted_keyword_facts(doc, keyword_vocabulary)
        # Team-pump/anthem kinship (2026-07-11): same post-processing
        # pattern, same keyword_vocabulary -- see tier_engine.py's own
        # main() for the full rationale.
        doc["team_pump_facts"] = te.build_team_pump_facts(doc, keyword_vocabulary)
    # Pool-widening fix (found + fixed 2026-07-10, same session as the Equip-
    # reminder obliteration) -- must run AFTER granted_keyword_facts is
    # attached above, same dependency mana_index has none of.
    granted_keyword_index = te.build_granted_keyword_index(card_docs)
    # Pool-widening fix (Captain's ruling, 2026-07-12): vanilla-creature
    # Tier 0's own candidate-pool seeding -- see build_vanilla_creature_
    # index()'s docstring in tier_engine.py.
    vanilla_creature_index = te.build_vanilla_creature_index(card_docs)
    idf, _tag_card_count, _n_tagged = te.compute_tag_stats(card_tags)

    turn_scoped_matches, turn_scoped_idf = te.run_turn_scoped_derivation(card_docs, n_total_cards)
    card_tags_t3, idf_t3 = te.build_turn_scoped_tag_index(card_docs, card_tags, idf, turn_scoped_matches, turn_scoped_idf)

    return SimpleNamespace(
        conn=conn, cards=cards, card_docs=card_docs, card_tags=card_tags, card_tags_t3=card_tags_t3,
        idf=idf, idf_t3=idf_t3, tag_index=tag_index, keyword_index=keyword_index, keyword_df=keyword_df,
        mana_index=mana_index, granted_keyword_index=granted_keyword_index,
        vanilla_creature_index=vanilla_creature_index,
        turn_scoped_matches=turn_scoped_matches, paragraph_index=paragraph_index, clause_index=clause_index,
        clause_df=clause_df, ngram_index=ngram_index, ngram_df=ngram_df, n_total_cards=n_total_cards,
        args=args, legality_by_oracle_id=legality_by_oracle_id,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--anchors-file", default=str(ANCHORS_TXT))
    parser.add_argument("--cards-path", default=str(te.CARDS_PATH))
    parser.add_argument("--card-tags-path", default=str(te.CARD_TAGS_PATH))
    parser.add_argument("--cards-sqlite-path", default=str(te.CARDS_SQLITE_PATH))
    parser.add_argument("--out-dir", default=str(VIEWER_DATA_DIR))
    cli_args = parser.parse_args()

    names = load_anchor_names(Path(cli_args.anchors_file))
    ctx = load_export_context(
        Path(cli_args.cards_path), Path(cli_args.card_tags_path), Path(cli_args.cards_sqlite_path),
    )

    print(f"\nresolving {len(names)} anchor name(s) against {cli_args.cards_sqlite_path}...")
    resolved = []
    for name in names:
        oracle_id = resolve_anchor_sqlite(name, ctx.conn)
        if oracle_id is not None:
            resolved.append((name, oracle_id))
    ctx.conn.close()
    if not resolved:
        te.halt("no anchor names resolved against cards.sqlite -- nothing to export")

    final = []
    for name, oracle_id in resolved:
        if oracle_id not in ctx.card_docs:
            print(f"  [SKIP] {name!r}: oracle_id {oracle_id} resolved in cards.sqlite but absent from {cli_args.cards_path}")
            continue
        final.append((name, oracle_id))
    if not final:
        te.halt("no anchor names resolved against the jsonl corpus -- nothing to export")

    out_dir = Path(cli_args.out_dir)
    if out_dir.exists():
        print(f"\nwiping stale cache at {out_dir}/ (engine change = stale export)...")
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nexporting {len(final)} anchor(s) to {out_dir}/...")
    index_entries = []
    for name, oracle_id in final:
        entry = export_anchor(name, oracle_id, ctx, out_dir)
        slow_note = f" [SLOW: >{SLOW_ANCHOR_THRESHOLD_SECONDS}s]" if entry["runtime_seconds"] > SLOW_ANCHOR_THRESHOLD_SECONDS else ""
        print(
            f"  {name}: {entry['runtime_seconds']:.2f}s{slow_note} -- tier0={entry['tier_counts']['0']} "
            f"tier1={entry['tier_counts']['1']} tier2={entry['tier_counts']['2']} "
            f"tier3={entry['tier_counts']['3']} -> {entry['file']}"
        )
        index_entries.append(entry)

    index_path = out_dir / "index.json"
    index_path.write_text(
        json.dumps(
            {"generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "anchors": index_entries},
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nwrote {index_path}")
    print(f"done — {len(final)} anchor(s) exported to {out_dir}/")


if __name__ == "__main__":
    main()
