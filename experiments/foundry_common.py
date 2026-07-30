#!/usr/bin/env python3
"""Shared corpus-loading and card-record helpers for the T3 Axis Foundry
(T3-AXIS-FOUNDRY-v3.md). Used by foundry_emit.py, foundry_reconcile.py, and
experiments/measure/axis_foundry.py -- kept here once instead of copied
three times. Never imported by tier_engine.py itself.
"""
import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import tier_engine as te  # noqa: E402

FOUNDRY_OUT_DIR = REPO_ROOT / "experiments" / "out" / "foundry"
REVIEW_DIR = FOUNDRY_OUT_DIR / "review"


def halt(message: str) -> None:
    print(f"STOP — {message}", file=sys.stderr)
    sys.exit(1)


def batch_paths(batch_num: int) -> dict:
    """Canonical per-batch output filenames for every foundry_*.py script.
    Batch 1 kept its original unsuffixed filenames (already committed
    before this convention existed); batch 2+ gets batch-numbered filenames
    so no two batches' artifacts ever collide. Single source of truth --
    foundry_stage1b.py, foundry_consolidate.py, and foundry_enrich.py all
    import this instead of each defining their own copy."""
    suffix = "" if batch_num == 1 else f"_batch{batch_num}"
    bsuffix = "-1" if batch_num == 1 else f"-{batch_num}"  # review/ files use batch-N.json naming
    return {
        "assembled": FOUNDRY_OUT_DIR / f"batch{batch_num}_assembled.json",
        "requests": FOUNDRY_OUT_DIR / f"stage1b_requests{suffix}.json",
        "batch_record": FOUNDRY_OUT_DIR / f"stage1b_batch{suffix}.json",
        "completion_note": FOUNDRY_OUT_DIR / f"stage1b_completion_note{suffix}.md",
        "cost_estimate": FOUNDRY_OUT_DIR / f"stage1b_cost_estimate{suffix}.json",
        "raw_results": FOUNDRY_OUT_DIR / f"stage1b_raw_results{suffix}.jsonl",
        "consolidated": FOUNDRY_OUT_DIR / f"consolidated_batch{batch_num}.json",
        "consolidate_clusters_raw": FOUNDRY_OUT_DIR / f"consolidate_clusters_raw{suffix}.json",
        "review": REVIEW_DIR / f"batch{bsuffix}.json",
        "enriched": REVIEW_DIR / f"batch{bsuffix}-enriched.json",
        "enriched_stats": REVIEW_DIR / f"batch{bsuffix}-enriched-stats.json",
        "digest": REVIEW_DIR / f"digest-batch-{batch_num}.md",
    }


def load_corpus():
    """Returns (cards: {oracle_id: raw_card}, name_index: {normalized_name: [oracle_id,...]}).
    Unfiltered/raw -- shared with tier_engine.py's other, non-foundry consumers,
    so this function's output must not change shape based on foundry-specific
    rulings. Foundry pipeline stages should use load_corpus_gated() instead
    (see Gate #0, batch-6 D1)."""
    cards = te.load_cards(te.CARDS_PATH)
    name_index = te.build_name_index(cards)
    return cards, name_index


def gate_passes(card: dict) -> bool:
    """Gate #0 (ratified batch-6 D1, 2026-07-30): a card is a valid target for
    the T3 Axis Foundry pipeline -- the DET pass, batch assembly, SYNTH, and
    reconcile -- iff it is legal or restricted in at least one Scryfall
    'legalities' format. Nowhere-legal cards (playtest/CMB1/CMB2/MB2, Unknown
    Event promos, prototype/event cards, bare token printings) fail outright.
    This is dataset-level and independent of the corroboration gate; it does
    not touch tier_engine.py's own load_cards()/CARDS_PATH consumers, which
    are out of this ruling's scope (production tier scoring, not foundry)."""
    legalities = card.get("legalities") or {}
    return any(v in ("legal", "restricted") for v in legalities.values())


def load_corpus_gated():
    """Gate #0-filtered corpus for foundry pipeline stages. Returns
    (cards, name_index, gated_out_count) -- cards/name_index contain only
    gate-passing rows; name_index is rebuilt from the filtered set so
    resolve_name() can never resolve a gated-out card by name. Raw
    load_corpus() is untouched and still available for reference/debugging."""
    cards, _ = load_corpus()
    gated_cards = {oid: c for oid, c in cards.items() if gate_passes(c)}
    gated_name_index = te.build_name_index(gated_cards)
    return gated_cards, gated_name_index, len(cards) - len(gated_cards)


def resolve_name(name: str, cards: dict, name_index: dict) -> str:
    """Exact-match name resolution, house halt-loudly discipline (pipeline
    CLAUDE.md: 'never fuzzy-matches a card name'). The corpus carries a known
    class of duplicate oracle rows sharing a display name with a set_type
    'token' entry (verified 2026-07-17: Llanowar Elves x2, Ajani's Pridemate
    x2 -- both times one entry is a real paper-legal printing, the other a
    token-set duplicate that is not a constructed-legal card). When matches
    split exactly this way, auto-resolve to the non-token entry ('paper' per
    the seed's own notes field); any OTHER ambiguity halts loudly rather than
    guessing."""
    matches = name_index.get(te.normalize_name(name), [])
    if len(matches) == 0:
        halt(f"card {name!r} matched 0 cards in the corpus — check spelling, no fuzzy fallback")
    if len(matches) == 1:
        return matches[0]

    non_token = [oid for oid in matches if cards[oid].get("set_type") != "token"]
    if len(non_token) == 1:
        return non_token[0]

    detail = ", ".join(f"{oid} (set={cards[oid].get('set')}, set_type={cards[oid].get('set_type')})" for oid in matches)
    halt(f"card {name!r} matched {len(matches)} cards, ambiguity NOT the known token-duplicate shape ({detail}) — resolve by hand")


def _extract_faces(card: dict) -> list:
    raw_faces = card.get("card_faces")
    if not raw_faces:
        return []
    faces = []
    for f in raw_faces:
        faces.append({
            "name": f.get("name") or card.get("name"),
            "mana_cost": f.get("mana_cost") or "",
            "type_line": f.get("type_line") or "",
            "oracle_text": f.get("oracle_text") or "",
            "power": f.get("power"),
            "toughness": f.get("toughness"),
            "loyalty": f.get("loyalty"),
        })
    return faces


def full_oracle_text(card: dict) -> str:
    """All-faces oracle text, newline-joined -- the root-level 'oracle_text'
    field is empty for multi-face layouts (transform/modal_dfc/adventure/
    prepare/etc.), so this always goes through te.get_raw_faces() (which
    falls back to the root field itself for single-face cards) rather than
    reading card['oracle_text'] directly. Mirrors foundry_enrich.py's own
    full_oracle_text() -- same source, same join convention."""
    return "\n".join(f["oracle_text"] for f in te.get_raw_faces(card) if f["oracle_text"])


def build_review_card_record(card: dict) -> dict:
    """The exact 'cards' entry shape T3-AXIS-FOUNDRY-v3.md's batch-N.json
    schema wants, extended with the fields the review tool's card-inspector
    pane also promises (loyalty, set/rarity of the oracle print) -- the
    schema's '...' is illustrative, not a closed field list."""
    return {
        "oracle_id": card["oracle_id"],
        "name": card.get("name") or "",
        "mana_cost": card.get("mana_cost") or "",
        "type_line": card.get("type_line") or "",
        "oracle_text": full_oracle_text(card),
        "power": card.get("power"),
        "toughness": card.get("toughness"),
        "loyalty": card.get("loyalty"),
        "color_identity": card.get("color_identity") or [],
        "keywords": card.get("keywords") or [],
        "layout": card.get("layout") or "normal",
        "set": card.get("set") or "",
        "rarity": card.get("rarity") or "",
        "faces": _extract_faces(card),
    }


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
