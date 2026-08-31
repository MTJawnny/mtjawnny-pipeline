"""Corpus access and card helpers — the permanent home of a capability that has
lived, until now, inside an 8,340-line scoring engine.

## What this is

Four things and one error type: load the card corpus, split a card into its real
faces, normalize a card name, and index cards by normalized name. That is the
whole capability. It is the lowest layer anything in the Foundry reads the
corpus through.

## What this is NOT

It is not a move of `tier_engine`. The legacy implementation is the ORACLE for
these behaviors — the values below are differentially compared against it over
the full corpus — but the legacy BOUNDARY is not the target architecture, and
three of its properties are deliberately not reproduced:

* **No module-level corpus path.** `tier_engine.CARDS_PATH` is
  `Path("data/raw/oracle-cards.jsonl.gz")` — RELATIVE, so it resolves against
  the working directory. That is a repository-relative layout fact stated
  outside the layout owner, and a latent cwd bug. Here the path is a PARAMETER;
  the caller gets it from `ProjectPaths`.
* **No process exit, no printing.** The legacy loader calls `halt()`, which
  prints to stderr and calls `sys.exit(1)`. A library may not end the process.
  Fatal states raise `CorpusLoadError` and the caller decides. The transitional
  legacy facade in `foundry_common` catches it and calls the existing `halt()`,
  so legacy callers keep their halt-loudly behavior exactly.
* **No legacy imports.** Stdlib only. Nothing here imports `tier_engine`,
  `foundry_common` or any other `experiments/` module, and nothing here touches
  `sys.path`.

## Equivalence

Every successful value is VALUE_EXACT with the legacy implementation, including
two DIFFERENT duplicate rules that are easy to conflate:

* a duplicate `oracle_id` is **last-write-wins** (the loader assigns by key);
* a duplicate normalized NAME keeps **every** oracle_id, in first-seen order.

Reproducing only one of those would pass a casual eyeball and lose real data.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path

__all__ = ["CorpusLoadError", "load_cards", "card_faces", "normalize_name",
           "build_name_index"]


class CorpusLoadError(RuntimeError):
    """The corpus could not be loaded. Raised, never printed, never exited.

    Covers exactly the states the legacy loader treated as fatal: the file is
    absent, a line is not JSON, or a record carries no usable `oracle_id`. The
    message text is preserved from the legacy loader so a caller that translates
    this into the old `halt()` produces the same operator-facing line.
    """


def load_cards(path: Path | str) -> dict:
    """`{oracle_id: raw_card}` from a gzip JSONL corpus.

    Streamed line by line, never read whole into memory. Blank lines are skipped
    after stripping. A duplicate `oracle_id` overwrites the earlier record —
    last-write-wins — which is the legacy assignment semantics and is preserved
    deliberately rather than "fixed" into a first-wins or a collision error.

    Raises `CorpusLoadError` if the file is missing, a line fails to parse, or a
    record has no `oracle_id` or an empty one.
    """
    path = Path(path)
    if not path.exists():
        raise CorpusLoadError(
            f"{path} not found — run pipeline/fetch.py or rclone copy the "
            "snapshot first")
    cards: dict = {}
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                card = json.loads(line)
            except json.JSONDecodeError as error:
                raise CorpusLoadError(
                    f"{path} line {line_no}: JSON parse failure: {error}"
                ) from None
            if "oracle_id" not in card or not card["oracle_id"]:
                raise CorpusLoadError(f"{path} line {line_no}: missing oracle_id")
            cards[card["oracle_id"]] = card
    return cards


def card_faces(card: dict) -> list[dict]:
    """Per-face dicts — a REAL split, never joined.

    The root-level `oracle_text` is empty for multi-face layouts (transform,
    modal_dfc, adventure, prepare, …), so every reader of card text has to come
    through here rather than reading `card["oracle_text"]` directly. A
    single-face card falls back to the root fields, which is what makes this one
    function correct for both shapes.

    Each face carries name, oracle_text, mana_cost, type_line, power, toughness.
    Absent text becomes `""`; absent mana_cost/power/toughness stay `None`.
    """
    faces = card.get("card_faces")
    if faces:
        return [
            {
                "name": face.get("name") or card["name"],
                "oracle_text": face.get("oracle_text") or "",
                "mana_cost": face.get("mana_cost"),
                "type_line": face.get("type_line") or "",
                "power": face.get("power"),
                "toughness": face.get("toughness"),
            }
            for face in faces
        ]
    return [{
        "name": card["name"],
        "oracle_text": card.get("oracle_text") or "",
        "mana_cost": card.get("mana_cost"),
        "type_line": card.get("type_line") or "",
        "power": card.get("power"),
        "toughness": card.get("toughness"),
    }]


def normalize_name(name: str) -> str:
    """Strip, then casefold. The one normalization every name lookup shares."""
    return name.strip().casefold()


def build_name_index(cards: dict) -> dict:
    """`{normalized name: [oracle_id, ...]}`, keeping EVERY id for a shared name.

    A list, not a single id: distinct cards genuinely share a normalized name,
    and collapsing them would silently drop one. Key order follows first
    appearance in `cards`, and each list follows iteration order, so the result
    is stable for a stable input.
    """
    index: dict = {}
    for oracle_id, card in cards.items():
        index.setdefault(normalize_name(card["name"]), []).append(oracle_id)
    return index
