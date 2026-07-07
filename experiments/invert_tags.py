#!/usr/bin/env python3
"""Tag-keyed -> card-keyed inversion of oracle-tags.jsonl.gz.

THESAURUS-TIER-PROTOTYPE-HANDOFF.md, script 1. Standalone experiment: reads
the Tagger snapshot, resolves parent inheritance at flip time (a card tagged
X also carries X's ancestors, walked via parent_ids with a cycle guard), and
writes an oracle_id-keyed index. Direct tags always win over an inherited
duplicate of the same slug. weight is a reserved field (see recipe doc) --
carried through for direct taggings only, unused in v1 scoring.

Not wired into trim_merge/CI. No R2 reads or writes.
"""
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

INPUT_PATH = Path("data/raw/oracle-tags.jsonl.gz")
OUTPUT_PATH = Path("experiments/out/card-tags.json.gz")


def halt(message: str) -> None:
    print(f"STOP — {message}", file=sys.stderr)
    sys.exit(1)


def load_tags(path: Path) -> list:
    if not path.exists():
        halt(f"{path} not found — rclone copy it from the snapshot first")
    tags = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                tag = json.loads(line)
            except json.JSONDecodeError as e:
                halt(f"{path} line {line_no}: JSON parse failure: {e}")
            for key in ("id", "slug", "parent_ids", "taggings"):
                if key not in tag:
                    halt(f"{path} line {line_no}: tag missing required key {key!r}")
            tags.append(tag)
    return tags


def resolve_ancestors(tag_id: str, by_id: dict, cache: dict) -> set:
    """Ancestor tag ids for tag_id (excluding itself), cycle-guarded via visited set."""
    if tag_id in cache:
        return cache[tag_id]

    ancestors = set()
    visited = {tag_id}
    frontier = list(by_id.get(tag_id, {}).get("parent_ids", []))
    while frontier:
        parent_id = frontier.pop()
        if parent_id in visited:
            continue  # cycle guard
        visited.add(parent_id)
        parent = by_id.get(parent_id)
        if parent is None:
            continue  # dangling parent_id reference; nothing to inherit from it
        ancestors.add(parent_id)
        frontier.extend(parent.get("parent_ids", []))

    cache[tag_id] = ancestors
    return ancestors


def invert(tags: list) -> dict:
    by_id = {t["id"]: t for t in tags}
    card_tags = defaultdict(dict)  # oracle_id -> slug -> {"direct": bool, "weight": str|None}
    ancestor_cache = {}

    for tag in tags:
        slug = tag["slug"]
        ancestor_ids = resolve_ancestors(tag["id"], by_id, ancestor_cache)
        ancestor_slugs = [by_id[a]["slug"] for a in ancestor_ids if a in by_id]

        for tagging in tag["taggings"]:
            oracle_id = tagging["oracle_id"]
            weight = tagging.get("weight")

            existing = card_tags[oracle_id].get(slug)
            if existing is None or not existing["direct"]:
                card_tags[oracle_id][slug] = {"direct": True, "weight": weight}

            for anc_slug in ancestor_slugs:
                if anc_slug not in card_tags[oracle_id]:
                    card_tags[oracle_id][anc_slug] = {"direct": False, "weight": None}

    output = {}
    for oracle_id in sorted(card_tags):
        entries = sorted(
            (
                {"slug": slug, "direct": info["direct"], "weight": info["weight"]}
                for slug, info in card_tags[oracle_id].items()
            ),
            key=lambda e: e["slug"],
        )
        output[oracle_id] = entries
    return output


def main() -> None:
    tags = load_tags(INPUT_PATH)
    print(f"loaded {len(tags):,} tags")

    card_tags = invert(tags)
    print(f"inverted to {len(card_tags):,} tagged cards")

    direct_count = sum(1 for entries in card_tags.values() for e in entries if e["direct"])
    inherited_count = sum(1 for entries in card_tags.values() for e in entries if not e["direct"])
    print(f"total taggings: {direct_count:,} direct, {inherited_count:,} inherited")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(OUTPUT_PATH, "wt", encoding="utf-8") as f:
        json.dump(card_tags, f, sort_keys=True)
    print(f"wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
