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
from collections import defaultdict
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
    # Per-face lookup (2026-07-13): this whole-card export IS "weigh both
    # faces" for a multi-faced card -- always was, silently, before this
    # feature existed. face_context is null for an ordinary single-faced
    # card (the overwhelming majority), non-null here only to give the
    # viewer's flip/weigh-both UI something to render; the tiers/rows
    # above are completely unchanged either way. Gated on FACE_SPLIT_
    # LAYOUTS (defined below), not just "more than one face" -- a
    # `card_faces`-bearing non-gameplay layout (art_series, etc.) has no
    # per-face entry in face_ctx at all, so offering a "view single face"
    # button for it would 404.
    face_names = [f["name"] for f in anchor_doc["faces"]]
    face_context = None
    if len(face_names) > 1 and ctx.cards[oracle_id].get("layout") in FACE_SPLIT_LAYOUTS:
        face_context = {
            "mode": "weigh_both", "is_multiface": True,
            "combined_name": name, "face_name": None, "face_index": None,
            "all_face_names": face_names,
        }
    data = {
        "anchor": anchor_block,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "corpus_cards": ctx.n_total_cards,
        "runtime_seconds": round(elapsed, 3),
        "tiers": tiers_export,
        "face_context": face_context,
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


# ---------------------------------------------------------------------------
# Per-face lookup (2026-07-13) -- viewer-only, on-demand from serve_viewer.py.
#
# A multi-faced card (transform/modal_dfc/split/adventure/flip) gets a
# per-face pseudo-doc PER FACE (te.build_face_scoped_doc()) instead of one
# doc joining both -- so searching just "Delver of Secrets" scores ONLY
# that face's own text, a flip button re-queries the sibling face, and a
# "weigh both" mode falls back to today's existing whole-card export_anchor()
# path, unchanged. Meld halves need none of this -- they're already
# separate single-faced records, each with its own oracle_id.
#
# Deliberately does NOT touch build_indexes()/gather_candidate_pool()'s own
# batch-pipeline invocation, tier_engine.py's gate suite, or the normal
# export_anchor() path above -- this builds a SEPARATE face-scoped corpus
# view (face_card_docs + its own paragraph/clause/ngram/keyword/mana/
# granted-keyword/vanilla-creature indexes) at server startup, then calls
# the SAME gather_candidate_pool()/compute_candidate_rows() functions
# UNMODIFIED against that view -- no second scoring implementation.
#
# Tier 3 (tag overlap) is intentionally NOT built for this view -- Tagger
# tags are a whole-card concept with no face-scoped meaning, so face mode
# only ever returns Tiers 0-2. This has one consequence beyond just "no
# Tier 3 section" (flagged in review, Fable 5's Finding N6): passing empty
# tags/idf into compute_candidate_rows() means tag_score is always 0.0 for
# every face-mode candidate, which makes tier2_corroboration_disqualified()
# (tier_engine.py) -- `polarity_mismatch AND tag_score == 0.0` -- disqualify
# EVERY polarity-mismatched Tier 2 row outright in face mode, where the
# whole-card view might have rescued some of them via real tag overlap.
# This changes Tier 2 MEMBERSHIP, not just Tier 3's absence -- a documented
# consequence of the no-tags scoping choice above, not a separate bug.
# ---------------------------------------------------------------------------

# Only these Scryfall `layout` values are "one card, two independently-
# castable/functional halves" in the sense Captain asked for -- found live,
# not assumed: a first draft split EVERY card with a `card_faces` array,
# which also covers art_series (a decorative double-sided ART card, same
# name printed on both faces for card-back art -- "Delver of Secrets //
# Delver of Secrets" collided with the real transform card's OWN "Delver
# of Secrets" face name, 404ing the very first card anyone would test this
# with) and double_faced_token -- neither of which is "two cards on one
# card," just another non-playable Scryfall object shape that happens to
# carry the same JSON field. Meld doesn't need an entry here -- meld
# halves are already separate single-faced records (their own oracle_id
# each), not `card_faces`-shaped at all.
#
# 2026-07-13 self-audit (before handing this off to Fable 5): a full scan
# of every `layout` value that actually carries `card_faces` in the corpus
# turned up "prepare" (Tarkir: Dragonstorm's mechanic -- "Adventurous
# Eater // Have a Bite," a creature with a bonus spell attached) missing
# from the first draft of this set -- structurally identical to
# "adventure" (a creature face + an independent spell face), just a
# differently-named Scryfall layout for a newer set. Added below; this was
# a real gap, not a hypothetical -- confirmed via the same corpus-scan
# methodology as build_vanilla_creature_index()'s own history of caught
# pool-seeding gaps elsewhere in this file's lineage.
FACE_SPLIT_LAYOUTS = frozenset({"transform", "modal_dfc", "split", "adventure", "flip", "prepare"})

# Recommended by Fable 5's review, 2026-07-13: the OTHER `card_faces`-
# bearing layouts confirmed live in the corpus today, deliberately NOT
# face-split (see FACE_SPLIT_LAYOUTS's own comment for why). Any
# `card_faces`-bearing layout in NEITHER set halts loudly at startup
# instead of silently keeping its one combined doc -- converts "a human
# has to notice a new layout is missing" (how the `prepare` gap above was
# actually caught) into a guaranteed stop the day Scryfall ships one.
KNOWN_NON_GAMEPLAY_CARD_FACES_LAYOUTS = frozenset({"art_series", "double_faced_token"})


def build_face_scoped_context(ctx: SimpleNamespace) -> SimpleNamespace:
    """Builds face_card_docs (every single-faced card's EXISTING doc,
    unchanged, plus TWO+ per-face pseudo-docs for every multi-faced card
    whose layout is in FACE_SPLIT_LAYOUTS, replacing its one combined doc)
    and fresh indexes over that view, once at server startup. A
    `card_faces`-bearing card OUTSIDE that layout set (art_series, etc.)
    keeps its single combined doc, unsplit -- same as any single-faced
    card here, unaffected by (and invisible to) the face-name resolution
    below. Also builds face_name_index (normalized individual face name ->
    [(real_oracle_id, face_index), ...], same ambiguity-list shape as
    te.build_name_index() so a rare cross-card face-name collision 404s
    instead of guessing) and face_meta (face_key -> sibling/combined-name
    bookkeeping for the viewer's flip/weigh-both UI)."""
    unknown_layouts = {
        (oid, ctx.cards[oid].get("layout")) for oid, doc in ctx.card_docs.items()
        if len(doc["faces"]) > 1
        and ctx.cards[oid].get("layout") not in (FACE_SPLIT_LAYOUTS | KNOWN_NON_GAMEPLAY_CARD_FACES_LAYOUTS)
    }
    if unknown_layouts:
        sample = sorted({layout for _, layout in unknown_layouts})
        te.halt(
            f"build_face_scoped_context: {len(unknown_layouts)} card(s) carry `card_faces` under layout(s) "
            f"{sample} -- neither a known gameplay dual-part layout (FACE_SPLIT_LAYOUTS) nor a known non-"
            f"gameplay one (KNOWN_NON_GAMEPLAY_CARD_FACES_LAYOUTS). Add it to whichever set it actually is "
            f"before proceeding -- never guess which bucket a new Scryfall layout belongs in."
        )

    keyword_vocabulary = te.build_keyword_vocabulary(ctx.cards)
    face_card_docs = {}
    face_name_index = defaultdict(list)
    face_meta = {}

    for oracle_id, doc in ctx.card_docs.items():
        n_faces = len(doc["faces"])
        layout = ctx.cards[oracle_id].get("layout")
        if n_faces <= 1 or layout not in FACE_SPLIT_LAYOUTS:
            face_card_docs[oracle_id] = doc
            continue
        all_names = [f["name"] for f in doc["faces"]]
        # Bug found in review (Fable 5, 2026-07-13): a transform/flip card's
        # BACK face isn't independently cast at its own cost -- CR 712.8/
        # 707.9 -- its mana VALUE is the front face's, always (you can't
        # cast "just the back half" at a different price the way you
        # genuinely can for split/adventure/modal_dfc/prepare, where each
        # face IS its own real, independently-castable spell). Left as a
        # bare mana_cost_to_cmc("") for these two layouts, EVERY transform/
        # flip back face silently ranked at mv=0 -- confirmed live example:
        # Nighteyes the Desecrator (real in-game mv 4) was showing mv_delta
        # +5 against a 4-mana card it's actually mv-even with. Only these
        # two layouts get the override; split/adventure/modal_dfc/prepare
        # keep each face's own genuinely-independent parsed cost unchanged.
        front_face_cmc = None
        for i in range(n_faces):
            face_doc = te.build_face_scoped_doc(doc, i, keyword_vocabulary)
            if i == 0:
                front_face_cmc = face_doc["cmc"]
            elif layout in ("transform", "flip"):
                face_doc["cmc"] = front_face_cmc
            face_key = face_doc["oracle_id"]
            face_card_docs[face_key] = face_doc
            face_name_index[te.normalize_name(all_names[i])].append((oracle_id, i))
            # "sibling" (singular) was dropped here (both self-audit
            # Finding B and Fable 5's independent review flagged it as
            # dead API surface -- viewer.html renders one button per
            # entry in all_face_names instead, which already covers 3+
            # face cards where "the" sibling is an ill-defined concept
            # anyway) -- all_face_names is the only face-listing the UI
            # actually reads.
            face_meta[face_key] = {
                "face_name": all_names[i],
                "face_index": i,
                "combined_name": doc["name"],
                "all_face_names": all_names,
                # Bug found in review (Fable 5, N1): every OTHER face of
                # THIS SAME card, by synthetic key -- export_face_anchor()
                # excludes these from its own candidate pool (see there),
                # so a card's own back face can no longer show up as a
                # "similar card" in its own front face's results (live
                # counterexample that motivated this: Legion's Landing's
                # own Tier 2 contained Adanto, the First Fort -- its own
                # back face -- at position 2 of 42, before this fix).
                "all_sibling_keys": [f'{oracle_id}::{j}' for j in range(n_faces) if j != i],
            }

    args = ctx.args
    face_paragraph_index, face_clause_index, face_clause_df, face_ngram_index, face_ngram_df = te.build_indexes(
        face_card_docs, args.ngram_min_len,
    )
    # Bug found in review (Fable 5, 2026-07-13): keyword DF is a corpus-wide
    # RARITY statistic -- how many distinct real CARDS carry a keyword --
    # and must not depend on which view (whole-card vs face-scoped) is
    # asking. Recomputing it over face_card_docs double-counted every
    # FACE_SPLIT_LAYOUTS card's own keywords (each contributes 2+ pool
    # entries instead of 1), measurably inflating DF for any keyword shared
    # by enough split/adventure/etc. cards -- confirmed live: aftermath
    # 27->54, daybound 37->73, disturb 32->64, nightbound 36->72, four of
    # which crossed NGRAM_DF_FLOOR=50 and would have silently DISQUALIFIED
    # from Mechanism-1 keyword kinship (and lost their pool-seeding path)
    # in face mode ONLY, never in the whole-card view. Reusing ctx's own
    # already-correct keyword_df fixes this at the root -- no card is
    # double-counted, and any keyword's rarity classification is now
    # identical whether reached via a whole card or one of its faces.
    face_keyword_df = ctx.keyword_df
    face_keyword_index = te.build_keyword_index(face_card_docs)
    face_mana_index = te.build_mana_pip_index(face_card_docs)
    face_granted_keyword_index = te.build_granted_keyword_index(face_card_docs)
    face_vanilla_creature_index = te.build_vanilla_creature_index(face_card_docs)

    return SimpleNamespace(
        face_card_docs=face_card_docs, face_name_index=dict(face_name_index), face_meta=face_meta,
        face_paragraph_index=face_paragraph_index, face_clause_index=face_clause_index,
        face_clause_df=face_clause_df, face_ngram_index=face_ngram_index, face_ngram_df=face_ngram_df,
        face_keyword_df=face_keyword_df, face_keyword_index=face_keyword_index,
        face_mana_index=face_mana_index, face_granted_keyword_index=face_granted_keyword_index,
        face_vanilla_creature_index=face_vanilla_creature_index,
    )


def build_face_anchor_display(card: dict, face_index: int, legal_commander) -> dict:
    """Mirrors build_anchor_display() above, scoped to one face's own raw
    (non-normalized) mana_cost/type_line/oracle_text -- color_identity
    stays the whole-card value (see build_face_scoped_doc()'s own comment
    on why that's correct, not a simplification)."""
    face = card["card_faces"][face_index]
    return {
        "name": face.get("name") or card["name"],
        "oracle_id": card["oracle_id"],
        "mana_cost": face.get("mana_cost") or "",
        "type_line": face.get("type_line") or "",
        "oracle_text": face.get("oracle_text") or "",
        "color_identity": card.get("color_identity") or [],
        "subtypes": sorted(te.creature_subtypes(face.get("type_line") or "")),
        "legal_commander": legal_commander,
    }


def build_face_row_export(row: dict, anchor_doc: dict, face_card_docs: dict, legality_by_oracle_id: dict) -> dict:
    """Mirrors build_row_export() above -- the only difference is the
    face-key vs real-oracle-id split: `row["oracle_id"]` here is a
    candidate's synthetic face key (e.g. "<real-id>::1") whenever the
    candidate matched via one specific face of a multi-faced card, since
    that's what the face-scoped pool/indexes are keyed by (see
    te.build_face_scoped_doc()'s own docstring) -- legality/display need
    the REAL Scryfall oracle_id instead, recovered from the candidate
    doc's own `real_oracle_id` field (absent, so falling back to the row's
    own oracle_id unchanged, for an ordinary single-faced candidate)."""
    face_key = row.get("oracle_id")
    candidate_doc = face_card_docs.get(face_key)
    real_oracle_id = candidate_doc.get("real_oracle_id", face_key) if candidate_doc is not None else face_key
    is_face_match = candidate_doc is not None and candidate_doc.get("face_index") is not None
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
        "oracle_id": real_oracle_id,
        # Present (non-null) only when this candidate matched via ONE face
        # of a multi-faced card -- the viewer uses this to annotate the row
        # ("Insectile Aberration (via Delver of Secrets // Insectile
        # Aberration)") instead of showing a bare face name with no context.
        "via_combined_name": candidate_doc.get("combined_name") if is_face_match else None,
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
        "legal_commander": legality_by_oracle_id.get(real_oracle_id),
        "is_land": is_land,
    }


def export_face_anchor(combined_name: str, oracle_id: str, face_index: int,
                        ctx: SimpleNamespace, face_ctx: SimpleNamespace, out_dir: Path) -> dict:
    """Face-scoped sibling of export_anchor() above -- Tiers 0-2 only (see
    this section's own header comment for why Tier 3 is out of scope),
    calling gather_candidate_pool()/compute_candidate_rows() UNMODIFIED
    against face_ctx's own face-scoped corpus view instead of ctx's
    whole-card one. Cached filename is the combined card's own slug plus a
    face suffix, so it can never collide with export_anchor()'s own cache
    entry for the same card's whole-card ("weigh both") export."""
    face_key = f"{oracle_id}::{face_index}"
    anchor_doc = face_ctx.face_card_docs[face_key]

    start = time.perf_counter()
    pool = te.gather_candidate_pool(
        anchor_doc, [], face_ctx.face_paragraph_index, face_ctx.face_clause_index, face_ctx.face_clause_df,
        face_ctx.face_ngram_index, face_ctx.face_ngram_df, {}, face_ctx.face_keyword_index, face_ctx.face_keyword_df,
        face_ctx.face_mana_index, face_ctx.face_granted_keyword_index, ctx.args,
        vanilla_creature_index=face_ctx.face_vanilla_creature_index,
    )
    # Bug found in review (Fable 5, N1): gather_candidate_pool()'s own
    # pool.discard(anchor_doc["oracle_id"]) only ever removes THIS face's
    # own synthetic key -- a sibling face of the SAME card is a completely
    # separate pool entry with no exclusion anywhere, so it could freely
    # appear as a "similar card" in its own sibling's results (confirmed
    # live: Adanto, the First Fort at position 2/42 in Legion's Landing's
    # own Tier 2, before this fix). A card's own other face(s) aren't a
    # different card to compare against -- see face_meta's own
    # "all_sibling_keys" (built in build_face_scoped_context()).
    pool -= set(face_ctx.face_meta[face_key]["all_sibling_keys"])
    full_tiers, _disqualified = te.compute_candidate_rows(
        anchor_doc, [], [], face_ctx.face_card_docs, {}, {}, pool,
        face_ctx.face_ngram_df, face_ctx.face_clause_df, face_ctx.face_keyword_df, face_ctx.face_paragraph_index,
        {}, {}, len(face_ctx.face_card_docs), ctx.args,
    )
    elapsed = time.perf_counter() - start

    tiers_export = {}
    for t in (0, 1, 2):
        rows = [build_face_row_export(r, anchor_doc, face_ctx.face_card_docs, ctx.legality_by_oracle_id) for r in full_tiers[t]]
        tiers_export[str(t)] = {"count": len(rows), "rows": rows}

    anchor_block = build_face_anchor_display(ctx.cards[oracle_id], face_index, ctx.legality_by_oracle_id.get(oracle_id))
    meta = face_ctx.face_meta[face_key]
    slug = f"{te.filename_slug(combined_name)}--face{face_index}"
    data = {
        "anchor": anchor_block,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "corpus_cards": len(face_ctx.face_card_docs),
        "runtime_seconds": round(elapsed, 3),
        "tiers": tiers_export,
        "face_context": {
            "mode": "face",
            "is_multiface": True,
            "combined_name": combined_name,
            "face_name": meta["face_name"],
            "face_index": face_index,
            "all_face_names": meta["all_face_names"],
        },
    }
    out_path = out_dir / f"{slug}.json"
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    return {
        "name": combined_name, "slug": slug, "file": out_path.name,
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
    # same post-processing pattern as tier_engine.py's own main(). 2026-07-12:
    # this now also covers the former team_pump mechanism's mass-pump facts.
    keyword_vocabulary = te.build_keyword_vocabulary(cards)
    for doc in card_docs.values():
        doc["granted_keyword_facts"] = te.build_granted_keyword_facts(doc, keyword_vocabulary)
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
