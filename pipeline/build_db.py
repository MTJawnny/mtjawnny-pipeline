#!/usr/bin/env python3
"""Build cards.sqlite from trimmed+merged data + neighbors + rulings (plan 3.6).

Local artifact only tonight — not uploaded to R2 (Evening 4's job).

Tables:
  cards      — one row per trimmed+merged card, oracle_id PK. List/dict
               fields (colors, keywords, produced_mana, card_faces) stored
               as JSON text columns. Any tags/cards.yaml-merged fields
               beyond the fixed schema (e.g. "role") land in the `tags`
               JSON column instead of forcing a schema change per new tag.
  neighbors  — straight load of data/neighbors/neighbors.parquet.
  rulings    — straight load of data/raw/rulings.jsonl.gz, oracle_id FK.
  cards_fts  — FTS5 over name/type_line/oracle_text. For multi-face cards
               (root oracle_text/type_line null) the indexed text is the
               per-face values joined with " // ", same convention as
               embed.py's _face_text — so FTS can find text that only
               exists on a face (e.g. "landfall" on a transform card).
"""
import gzip
import json
import sqlite3
import sys
from pathlib import Path

import pandas as pd

TRIMMED_PATH = Path("data/trimmed/cards.jsonl.gz")
NEIGHBORS_PATH = Path("data/neighbors/neighbors.parquet")
RULINGS_PATH = Path("data/raw/rulings.jsonl.gz")
OUT_PATH = Path("data/artifacts/cards.sqlite")

# WUBRG bit order — used for the color_identity/colors canonical string form
# (e.g. ["G", "B"] -> "BG") so SQL clients can index/filter/LIKE without
# needing to reconstruct Scryfall's JSON array formatting.
WUBRG = "WUBRG"

FIXED_FIELDS = {
    "oracle_id", "name", "mana_cost", "cmc", "type_line", "oracle_text",
    "colors", "color_identity", "keywords", "power", "toughness", "loyalty",
    "produced_mana", "rarity", "set", "collector_number", "released_at",
    "edhrec_rank", "game_changer", "scryfall_uri", "legalities", "prices",
    "is_dfc", "has_root_image", "card_faces", "layout",
}

# CO-G (Phase 2b, ratified) / PHASE-3-COMPLETION.md spec: 216 names map to
# multiple oracle_ids, mostly tokens (e.g. "Elemental" x31) plus emblems,
# art series, vanguards, schemes, and planes -- none of these are real
# gameplay cards, so they should never compete with a real card for a name
# in the resolver's match space. Excluded at build time (never inserted
# into `cards`/`cards_fts` at all) rather than filtered per-query, so every
# search path (viewer LIKE search, exact-name anchor lookup) gets the fix
# for free. Verified against data/raw/oracle-cards.jsonl.gz directly: this
# resolves Llanowar Elves (real card vs. a `token` printing under the same
# name) and all but 16 of the 216 collisions -- the remaining 16 are
# genuine same-name distinct real records (mostly Un-set silver-border
# jokes, e.g. "Everythingamajig", plus a handful of real-card/joke-card
# name clashes like "Red Herring") that are NOT a layout problem and
# correctly continue to halt loudly as a real ambiguity.
EXCLUDED_LAYOUTS = {"token", "emblem", "art_series", "vanguard", "scheme", "planar"}


def halt(message: str) -> None:
    print(f"STOP — {message}", file=sys.stderr)
    sys.exit(1)


def canonical_colors(values) -> str:
    if not values:
        return ""
    return "".join(c for c in WUBRG if c in values)


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
            if "oracle_id" not in card or not card["oracle_id"]:
                halt(f"{TRIMMED_PATH} line {line_no}: missing oracle_id")
            cards.append(card)
    return cards


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE cards (
            oracle_id           TEXT PRIMARY KEY,
            name                TEXT NOT NULL,
            mana_cost           TEXT,
            cmc                 REAL,
            type_line           TEXT,
            oracle_text         TEXT,
            colors              TEXT,
            color_identity      TEXT,
            keywords            TEXT,
            power               TEXT,
            toughness           TEXT,
            loyalty             TEXT,
            produced_mana       TEXT,
            layout              TEXT,
            rarity              TEXT,
            "set"               TEXT,
            collector_number    TEXT,
            released_at         TEXT,
            edhrec_rank         INTEGER,
            game_changer        INTEGER,
            scryfall_uri        TEXT,
            legalities_commander TEXT,
            price_usd           TEXT,
            is_dfc              INTEGER NOT NULL,
            has_root_image      INTEGER NOT NULL,
            card_faces          TEXT,
            tags                TEXT
        );

        CREATE INDEX idx_cards_name ON cards(name COLLATE NOCASE);
        CREATE INDEX idx_cards_ci_cmc ON cards(color_identity, cmc);

        CREATE TABLE neighbors (
            oracle_id   TEXT NOT NULL,
            rank        INTEGER NOT NULL,
            neighbor_id TEXT NOT NULL,
            score       REAL NOT NULL,
            PRIMARY KEY (oracle_id, rank)
        );

        CREATE TABLE rulings (
            oracle_id    TEXT NOT NULL,
            published_at TEXT,
            comment      TEXT
        );
        CREATE INDEX idx_rulings_oracle_id ON rulings(oracle_id);

        CREATE VIRTUAL TABLE cards_fts USING fts5(
            oracle_id UNINDEXED,
            name,
            type_line,
            oracle_text
        );
        """
    )
    # oracle_id is already a unique, stable UUID string — no separate index
    # needed beyond the PRIMARY KEY (which sqlite backs with its own index).


def insert_cards(conn: sqlite3.Connection, cards: list) -> None:
    rows = []
    fts_rows = []
    excluded_count = 0
    for card in cards:
        if card.get("layout") in EXCLUDED_LAYOUTS:
            excluded_count += 1
            continue

        legalities = card.get("legalities") or {}
        prices = card.get("prices") or {}
        tag_fields = {k: v for k, v in card.items() if k not in FIXED_FIELDS}

        rows.append((
            card["oracle_id"],
            card["name"],
            card.get("mana_cost"),
            card.get("cmc"),
            card.get("type_line"),
            card.get("oracle_text"),
            json.dumps(card.get("colors")) if card.get("colors") is not None else None,
            canonical_colors(card.get("color_identity")),
            json.dumps(card.get("keywords")) if card.get("keywords") is not None else None,
            card.get("power"),
            card.get("toughness"),
            card.get("loyalty"),
            json.dumps(card.get("produced_mana")) if card.get("produced_mana") is not None else None,
            card.get("layout"),
            card.get("rarity"),
            card.get("set"),
            card.get("collector_number"),
            card.get("released_at"),
            card.get("edhrec_rank"),
            int(bool(card.get("game_changer"))),
            card.get("scryfall_uri"),
            legalities.get("commander"),
            prices.get("usd"),
            int(bool(card.get("is_dfc"))),
            int(bool(card.get("has_root_image"))),
            json.dumps(card.get("card_faces")) if card.get("card_faces") is not None else None,
            json.dumps(tag_fields) if tag_fields else None,
        ))

        fts_type_line, fts_oracle_text = face_text(card)
        fts_rows.append((card["oracle_id"], card["name"], fts_type_line, fts_oracle_text))

    conn.executemany(
        """
        INSERT INTO cards (
            oracle_id, name, mana_cost, cmc, type_line, oracle_text,
            colors, color_identity, keywords, power, toughness, loyalty,
            produced_mana, layout, rarity, "set", collector_number, released_at,
            edhrec_rank, game_changer, scryfall_uri, legalities_commander,
            price_usd, is_dfc, has_root_image, card_faces, tags
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        rows,
    )
    conn.executemany(
        "INSERT INTO cards_fts (oracle_id, name, type_line, oracle_text) VALUES (?,?,?,?)",
        fts_rows,
    )
    print(
        f"inserted {len(rows):,} cards ({len(fts_rows):,} into cards_fts) -- "
        f"excluded {excluded_count:,} non-gameplay-layout records ({sorted(EXCLUDED_LAYOUTS)})"
    )


def insert_neighbors(conn: sqlite3.Connection) -> None:
    if not NEIGHBORS_PATH.exists():
        halt(f"{NEIGHBORS_PATH} not found — run pipeline/neighbors.py first")
    df = pd.read_parquet(NEIGHBORS_PATH)
    required = {"oracle_id", "rank", "neighbor_id", "score"}
    if not required.issubset(df.columns):
        halt(f"{NEIGHBORS_PATH} missing expected columns {required - set(df.columns)}")

    rows = list(df[["oracle_id", "rank", "neighbor_id", "score"]].itertuples(index=False, name=None))
    conn.executemany(
        "INSERT INTO neighbors (oracle_id, rank, neighbor_id, score) VALUES (?,?,?,?)",
        rows,
    )
    print(f"inserted {len(rows):,} neighbor rows")


def insert_rulings(conn: sqlite3.Connection) -> None:
    if not RULINGS_PATH.exists():
        halt(f"{RULINGS_PATH} not found — run pipeline/fetch.py first")

    rows = []
    with gzip.open(RULINGS_PATH, "rt", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                ruling = json.loads(line)
            except json.JSONDecodeError as e:
                halt(f"{RULINGS_PATH} line {line_no}: JSON parse failure: {e}")
            if "oracle_id" not in ruling or not ruling["oracle_id"]:
                halt(f"{RULINGS_PATH} line {line_no}: missing oracle_id")
            rows.append((ruling["oracle_id"], ruling.get("published_at"), ruling.get("comment")))

    conn.executemany(
        "INSERT INTO rulings (oracle_id, published_at, comment) VALUES (?,?,?)",
        rows,
    )
    print(f"inserted {len(rows):,} ruling rows")

    known_ids = {r[0] for r in conn.execute("SELECT oracle_id FROM cards").fetchall()}
    orphans = sum(1 for r in rows if r[0] not in known_ids)
    if orphans:
        print(f"  note: {orphans:,} ruling rows reference an oracle_id not present in cards (not an error, just fyi)")


def main() -> None:
    cards = load_cards()
    print(f"loaded {len(cards):,} trimmed cards")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if OUT_PATH.exists():
        OUT_PATH.unlink()

    conn = sqlite3.connect(OUT_PATH)
    try:
        create_schema(conn)
        insert_cards(conn, cards)
        insert_neighbors(conn)
        insert_rulings(conn)
        conn.commit()

        conn.execute("PRAGMA page_size=1024")
        conn.commit()
        conn.execute("VACUUM")
        conn.execute("ANALYZE")
        conn.commit()
    finally:
        conn.close()

    size_bytes = OUT_PATH.stat().st_size
    print(f"wrote {OUT_PATH} — {size_bytes:,} bytes ({size_bytes / 1024 / 1024:.2f} MB)")


if __name__ == "__main__":
    main()
