#!/usr/bin/env python3
"""Trim data/raw/oracle-cards.jsonl.gz to the fields the site needs, merge tags/cards.yaml.

Streams the field-complete oracle-cards.jsonl.gz line-by-line (never
snapshot.jsonl — see PHASE-2-COMPLETION.md correction #4, snapshot.jsonl is a
trimmed R2-upload manifest with bare filenames, not real image_uris/card_faces).

DFC rule (locked, PHASE-2-COMPLETION.md correction #1): a card is two-image
if and only if card_faces[0].image_uris exists. Split/flip/adventure cards
HAVE card_faces but carry one root-level image_uris — never judge by
card_faces presence.

Halts loudly on: a line that fails JSON parse, a record missing oracle_id or
name, or a tags.yaml entry whose oracle_id matches no card.
"""
import argparse
import gzip
import json
import sys
from pathlib import Path

import yaml

RAW_PATH = Path("data/raw/oracle-cards.jsonl.gz")
TAGS_PATH = Path("tags/cards.yaml")
OUT_PATH = Path("data/trimmed/cards.jsonl.gz")

KEPT_FIELDS = [
    "oracle_id", "name", "mana_cost", "cmc", "type_line", "oracle_text",
    "colors", "color_identity", "keywords", "power", "toughness", "loyalty",
    "produced_mana", "rarity", "set", "collector_number", "released_at",
    "edhrec_rank", "game_changer", "scryfall_uri", "layout",
]


def halt(message: str) -> None:
    print(f"STOP — {message}", file=sys.stderr)
    sys.exit(1)


def is_dfc(card: dict) -> bool:
    faces = card.get("card_faces")
    if not faces:
        return False
    return "image_uris" in faces[0]


def has_root_image(card: dict) -> bool:
    return "image_uris" in card


def trim_card(card: dict, line_no: int) -> dict:
    if "oracle_id" not in card or not card["oracle_id"]:
        halt(f"data/raw line {line_no}: record missing oracle_id (name={card.get('name')!r})")
    if "name" not in card or not card["name"]:
        halt(f"data/raw line {line_no}: record missing name (oracle_id={card.get('oracle_id')!r})")

    trimmed = {field: card.get(field) for field in KEPT_FIELDS}

    legalities = card.get("legalities", {})
    trimmed["legalities"] = {"commander": legalities.get("commander")}

    prices = card.get("prices", {})
    trimmed["prices"] = {"usd": prices.get("usd")}

    dfc = is_dfc(card)
    trimmed["is_dfc"] = dfc
    trimmed["has_root_image"] = has_root_image(card)

    faces = card.get("card_faces")
    trimmed["card_faces"] = (
        [
            {
                "name": face.get("name"),
                "mana_cost": face.get("mana_cost"),
                "type_line": face.get("type_line"),
                "oracle_text": face.get("oracle_text"),
                "power": face.get("power"),
                "toughness": face.get("toughness"),
                "loyalty": face.get("loyalty"),
            }
            for face in faces
        ]
        if faces
        else None
    )

    return trimmed


def load_tags() -> dict:
    if not TAGS_PATH.exists():
        return {}
    with open(TAGS_PATH) as f:
        raw = yaml.safe_load(f)
    return raw or {}


def load_extra(extra_path: str | None) -> dict:
    if not extra_path:
        return {}
    path = Path(extra_path)
    if not path.exists():
        halt(f"--extra file not found: {extra_path}")
    with open(path) as f:
        data = json.load(f)
    return data or {}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--extra",
        default=None,
        help="optional extra oracle_id-keyed JSON file to merge as additional columns (reserved slot, 3.3)",
    )
    args = parser.parse_args()

    if not RAW_PATH.exists():
        halt(f"{RAW_PATH} not found — run pipeline/fetch.py first")

    tags = load_tags()
    extra = load_extra(args.extra)

    trimmed_by_oracle_id = {}
    raw_line_count = 0

    with gzip.open(RAW_PATH, "rt", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            raw_line_count += 1
            line = line.strip()
            if not line:
                continue
            try:
                card = json.loads(line)
            except json.JSONDecodeError as e:
                halt(f"data/raw line {line_no}: JSON parse failure: {e}")

            trimmed = trim_card(card, line_no)
            trimmed_by_oracle_id[trimmed["oracle_id"]] = trimmed

    for oracle_id, tag_fields in tags.items():
        if oracle_id not in trimmed_by_oracle_id:
            halt(f"tags/cards.yaml entry oracle_id={oracle_id!r} matches no card in {RAW_PATH}")
        trimmed_by_oracle_id[oracle_id].update(tag_fields)

    for oracle_id, extra_fields in extra.items():
        if oracle_id not in trimmed_by_oracle_id:
            halt(f"--extra entry oracle_id={oracle_id!r} matches no card in {RAW_PATH}")
        trimmed_by_oracle_id[oracle_id].update(extra_fields)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(OUT_PATH, "wt", encoding="utf-8") as f:
        for trimmed in trimmed_by_oracle_id.values():
            f.write(json.dumps(trimmed) + "\n")

    trimmed_count = len(trimmed_by_oracle_id)
    print(f"raw line count: {raw_line_count:,}")
    print(f"trimmed record count: {trimmed_count:,}")
    print(f"wrote {OUT_PATH}")
    print("sample records:")
    for sample in list(trimmed_by_oracle_id.values())[:3]:
        print(json.dumps(sample, indent=2))


if __name__ == "__main__":
    main()
