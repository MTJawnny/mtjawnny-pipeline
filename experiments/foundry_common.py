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
    """Returns (cards: {oracle_id: raw_card}, name_index: {normalized_name: [oracle_id,...]})."""
    cards = te.load_cards(te.CARDS_PATH)
    name_index = te.build_name_index(cards)
    return cards, name_index


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
        "oracle_text": card.get("oracle_text") or "",
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
