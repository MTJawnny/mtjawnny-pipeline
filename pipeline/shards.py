#!/usr/bin/env python3
"""Emit plain-JSON shards alongside cards.sqlite for zero-dependency consumers (plan 3.8).

Local artifact only tonight — not uploaded to R2 (Evening 4's job).

names/<a-z>.json    — name -> list of {oracle_id, is_dfc} (a list even for
                      a unique name, since duplicate names are real in this
                      corpus — tokens like "Elemental" have 31 distinct
                      oracle_ids — so callers always get one shape).
                      Bucketed by the first letter of the name after
                      diacritic-folding (so "Éowyn" lands under e.json).
                      Names with no a-z first letter (join cards, ante
                      cards, promos like "1996 World Champion") land in
                      misc.json.
names/misc.json
neighbors/<prefix>.json — oracle_id -> top-25 [{rank, neighbor_id, score}],
                      sharded by the first 2 hex characters of oracle_id
                      (a UUID, so this is an even, high-cardinality split —
                      unlike names, which cluster hard on a few letters).
"""
import gzip
import json
import string
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

import pandas as pd

TRIMMED_PATH = Path("data/trimmed/cards.jsonl.gz")
NEIGHBORS_PATH = Path("data/neighbors/neighbors.parquet")
NAMES_DIR = Path("data/artifacts/shards/names")
NEIGHBORS_DIR = Path("data/artifacts/shards/neighbors")


def halt(message: str) -> None:
    print(f"STOP — {message}", file=sys.stderr)
    sys.exit(1)


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


def name_bucket(name: str) -> str:
    folded = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    first = folded[:1].lower()
    return first if first in string.ascii_lowercase else "misc"


def write_name_shards(cards: list) -> None:
    buckets = defaultdict(dict)
    for card in cards:
        bucket = name_bucket(card["name"])
        entry = {"oracle_id": card["oracle_id"], "is_dfc": bool(card.get("is_dfc"))}
        buckets[bucket].setdefault(card["name"], []).append(entry)

    NAMES_DIR.mkdir(parents=True, exist_ok=True)
    total_bytes = 0
    for bucket, names in sorted(buckets.items()):
        path = NAMES_DIR / f"{bucket}.json"
        with open(path, "w") as f:
            json.dump(names, f)
        total_bytes += path.stat().st_size

    collisions = sum(1 for names in buckets.values() for entries in names.values() if len(entries) > 1)
    print(
        f"wrote {len(buckets)} name shards to {NAMES_DIR} — "
        f"{sum(len(n) for n in buckets.values()):,} unique names, "
        f"{collisions:,} names with >1 oracle_id, {total_bytes:,} bytes total"
    )


def write_neighbor_shards() -> None:
    if not NEIGHBORS_PATH.exists():
        halt(f"{NEIGHBORS_PATH} not found — run pipeline/neighbors.py first")
    df = pd.read_parquet(NEIGHBORS_PATH)
    required = {"oracle_id", "rank", "neighbor_id", "score"}
    if not required.issubset(df.columns):
        halt(f"{NEIGHBORS_PATH} missing expected columns {required - set(df.columns)}")

    df = df.sort_values(["oracle_id", "rank"])
    df["prefix"] = df["oracle_id"].str[:2].str.lower()

    NEIGHBORS_DIR.mkdir(parents=True, exist_ok=True)
    total_bytes = 0
    shard_count = 0
    for prefix, group in df.groupby("prefix"):
        shard = defaultdict(list)
        for row in group.itertuples(index=False):
            shard[row.oracle_id].append({
                "rank": int(row.rank),
                "neighbor_id": row.neighbor_id,
                "score": float(row.score),
            })
        path = NEIGHBORS_DIR / f"{prefix}.json"
        with open(path, "w") as f:
            json.dump(shard, f)
        total_bytes += path.stat().st_size
        shard_count += 1

    print(
        f"wrote {shard_count} neighbor shards to {NEIGHBORS_DIR} — "
        f"{df['oracle_id'].nunique():,} cards, {total_bytes:,} bytes total"
    )


def main() -> None:
    cards = load_cards()
    print(f"loaded {len(cards):,} trimmed cards")

    write_name_shards(cards)
    write_neighbor_shards()


if __name__ == "__main__":
    main()
