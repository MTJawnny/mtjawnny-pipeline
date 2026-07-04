#!/usr/bin/env python3
"""Emit finisher/index.json.gz and finisher/vectors.bin for the Deck Finisher (plan 3.7).

Local artifact only tonight — not uploaded to R2 (Evening 4's job).

Scope: every Commander-legal card (legalities.commander == "legal"), in a
single fixed order shared by both output files (index.json.gz rows and
vectors.bin rows line up 1:1 — vectors_header.json's oracle_id_order is
that same order, so a client can zip the two without a join).

Role flags (ramp / card_draw / spot_removal / board_wipe / counterspell /
recursion / tutor / land) come from oracle-text pattern rules — a rough
heuristic layer, expected to be imperfect. A tags/cards.yaml "role" entry
(merged onto the trimmed record by trim_merge.py) REPLACES the pattern
result for that card entirely — it doesn't merge with it, it wins.
"""
import gzip
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

TRIMMED_PATH = Path("data/trimmed/cards.jsonl.gz")
CACHE_LOCAL = Path("data/cache/embeddings.parquet")
OUT_DIR = Path("data/artifacts/finisher")
INDEX_PATH = OUT_DIR / "index.json.gz"
VECTORS_PATH = OUT_DIR / "vectors.bin"
VECTORS_HEADER_PATH = OUT_DIR / "vectors_header.json"

EXPECTED_DIM = 384
EXPECTED_VECTORS_BYTES = 11 * 1024 * 1024  # plan 3.7 estimate, ~11MB
SIZE_TOLERANCE = 0.5  # halt if actual is outside [estimate*(1-t), estimate*(1+t)]

WUBRG_BITS = {"W": 1, "U": 2, "B": 4, "R": 8, "G": 16}

TYPE_BUCKET_ORDER = [
    "Land", "Creature", "Planeswalker", "Battle", "Artifact", "Enchantment",
    "Instant", "Sorcery",
]

ROLE_TEXT_PATTERNS = {
    "ramp": [
        r"search your library for .*land card",
        r"add \{[wubrgc]\}",
        r"add one mana of any (?:color|type)",
    ],
    "card_draw": [
        r"draws? (?:a|an|\d+|two|three|four|five|six|seven|x) cards?",
    ],
    "spot_removal": [
        r"destroy target creature",
        r"exile target creature",
        r"target creature gets -\d+/-\d+",
    ],
    "board_wipe": [
        r"destroy all creatures",
        r"each creature (?:gets|takes)",
        r"all creatures (?:get|deal)",
        r"deals? \d+ damage to each creature",
    ],
    "counterspell": [
        r"counter target spell",
    ],
    "recursion": [
        r"return target creature card from (?:your|a|any) graveyard",
        r"return target card from your graveyard",
    ],
    "tutor": [
        r"search your library for a card",
    ],
}
COMPILED_ROLE_PATTERNS = {
    role: [re.compile(p, re.IGNORECASE) for p in patterns]
    for role, patterns in ROLE_TEXT_PATTERNS.items()
}

SAMPLE_NAMES_FOR_REVIEW = [
    "Sakura-Tribe Elder", "Sol Ring", "Wrath of God",
    "Swords to Plowshares", "Counterspell",
]


def halt(message: str) -> None:
    print(f"STOP — {message}", file=sys.stderr)
    sys.exit(1)


def face_text(card: dict) -> tuple:
    """Same convention as embed.py's _face_text: multi-face cards carry
    real text only per-face, joined with ' // ' in face order."""
    faces = card.get("card_faces")
    type_line = card.get("type_line")
    oracle_text = card.get("oracle_text")

    if faces:
        if not type_line:
            type_line = " // ".join(face.get("type_line") or "" for face in faces)
        if not oracle_text:
            oracle_text = " // ".join(face.get("oracle_text") or "" for face in faces)

    return type_line or "", oracle_text or ""


def type_bucket(type_line: str) -> str:
    for bucket in TYPE_BUCKET_ORDER:
        if re.search(rf"\b{bucket}\b", type_line):
            return bucket.lower()
    return "other"


def color_identity_bitmask(color_identity) -> int:
    mask = 0
    for c in color_identity or []:
        mask |= WUBRG_BITS.get(c, 0)
    return mask


def pattern_derived_roles(type_line: str, oracle_text: str) -> list:
    roles = []
    if re.search(r"\bLand\b", type_line):
        roles.append("land")
    for role, patterns in COMPILED_ROLE_PATTERNS.items():
        if any(p.search(oracle_text) for p in patterns):
            roles.append(role)
    return roles


def derive_roles(card: dict, type_line: str, oracle_text: str) -> list:
    override = card.get("role")
    if override:
        return list(override)
    return pattern_derived_roles(type_line, oracle_text)


def load_cards() -> list:
    if not TRIMMED_PATH.exists():
        halt(f"{TRIMMED_PATH} not found — run pipeline/trim_merge.py first")
    cards = []
    with gzip.open(TRIMMED_PATH, "rt", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                card = json.loads(line)
            except json.JSONDecodeError as e:
                halt(f"{TRIMMED_PATH} line {line_no}: JSON parse failure: {e}")
            cards.append(card)
    return cards


def load_embedding_map() -> dict:
    if not CACHE_LOCAL.exists():
        halt(f"{CACHE_LOCAL} not found — run pipeline/embed.py first")
    df = pd.read_parquet(CACHE_LOCAL)
    return {
        row.oracle_id: np.asarray(row.vector, dtype=np.float32)
        for row in df.itertuples(index=False)
    }


def build_index_rows(commander_legal_cards: list) -> list:
    rows = []
    for card in commander_legal_cards:
        type_line, oracle_text = face_text(card)
        roles = derive_roles(card, type_line, oracle_text)
        prices = card.get("prices") or {}
        rows.append({
            "oracle_id": card["oracle_id"],
            "name": card["name"],
            "ci": color_identity_bitmask(card.get("color_identity")),
            "cmc": card.get("cmc"),
            "type_bucket": type_bucket(type_line),
            "role_flags": roles,
            "edhrec_rank": card.get("edhrec_rank"),
            "price_usd": prices.get("usd"),
        })
    return rows


def write_index(rows: list) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with gzip.open(INDEX_PATH, "wt", encoding="utf-8") as f:
        json.dump(rows, f)
    size = INDEX_PATH.stat().st_size
    print(f"wrote {INDEX_PATH} — {len(rows):,} cards, {size:,} bytes ({size / 1024 / 1024:.2f} MB)")


def write_vectors(commander_legal_cards: list, embedding_map: dict) -> None:
    oracle_ids = [c["oracle_id"] for c in commander_legal_cards]
    missing = [oid for oid in oracle_ids if oid not in embedding_map]
    if missing:
        halt(
            f"{len(missing):,} commander-legal card(s) have no cached embedding "
            f"in {CACHE_LOCAL} (first missing oracle_id: {missing[0]}) — run "
            f"pipeline/embed.py first"
        )

    matrix = np.stack([embedding_map[oid] for oid in oracle_ids]).astype(np.float32)
    if matrix.shape[1] != EXPECTED_DIM:
        halt(f"embedding dim {matrix.shape[1]} != expected {EXPECTED_DIM}")

    max_abs = float(np.max(np.abs(matrix)))
    if max_abs == 0.0:
        halt("all embedding vectors are zero — refusing to quantize")
    scale = 127.0 / max_abs

    quantized = np.clip(np.round(matrix * scale), -127, 127).astype(np.int8)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    quantized.tofile(VECTORS_PATH)

    header = {
        "dim": EXPECTED_DIM,
        "count": len(oracle_ids),
        "dtype": "int8",
        "scale": scale,
        "oracle_id_order": oracle_ids,
    }
    with open(VECTORS_HEADER_PATH, "w") as f:
        json.dump(header, f)

    size = VECTORS_PATH.stat().st_size
    print(f"wrote {VECTORS_PATH} — {size:,} bytes ({size / 1024 / 1024:.2f} MB), scale={scale:.4f}")
    print(f"wrote {VECTORS_HEADER_PATH}")

    lo = EXPECTED_VECTORS_BYTES * (1 - SIZE_TOLERANCE)
    hi = EXPECTED_VECTORS_BYTES * (1 + SIZE_TOLERANCE)
    if not (lo <= size <= hi):
        halt(
            f"{VECTORS_PATH} is {size:,} bytes, wildly off from the plan 3.7 "
            f"estimate of ~11MB (expected {lo:,.0f}–{hi:,.0f} bytes)"
        )


def print_samples(commander_legal_cards: list, index_rows: list) -> None:
    rows_by_name = {}
    for card, row in zip(commander_legal_cards, index_rows):
        rows_by_name.setdefault(card["name"], row)

    print("\nsample role derivations:")
    for name in SAMPLE_NAMES_FOR_REVIEW:
        row = rows_by_name.get(name)
        if row is None:
            halt(f"sample card {name!r} not found among commander-legal cards")
        print(f"  {name:<24} role_flags={row['role_flags']}")


def main() -> None:
    cards = load_cards()
    print(f"loaded {len(cards):,} trimmed cards")

    commander_legal_cards = [
        c for c in cards if (c.get("legalities") or {}).get("commander") == "legal"
    ]
    print(f"commander-legal cards: {len(commander_legal_cards):,}")

    embedding_map = load_embedding_map()

    index_rows = build_index_rows(commander_legal_cards)
    write_index(index_rows)
    write_vectors(commander_legal_cards, embedding_map)
    print_samples(commander_legal_cards, index_rows)


if __name__ == "__main__":
    main()
