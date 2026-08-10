#!/usr/bin/env python3
"""WIRE STEP 0 — CAN the codebook join move a neighbour list at all?

Product-reality audit §9.1 asks to wire `codebook.json` into `tier_engine`'s
rule:-only derived index and measure the effect on neighbours. Before measuring
the effect, measure the CAPABILITY: a join can only move an anchor's list if
the ANCHOR itself carries a membership, because `derived_agreement` is an
ANCHOR-DIRECTIONAL coverage ratio (`tier3_score`) — an anchor with zero
rule:-tags has total_anchor_weight 0 and every candidate scores 0.0.

That is a structural fact about the scoring function, not a grade of the
result, so measuring it first does not contaminate the prediction written in
docs/WIRE-PREDICTIONS-2026-08-09.md.

This script decides nothing and mutates nothing. It reports:

  1. the live active-axis / membership census (re-derived, never carried)
  2. axis SIZE distribution — an axis with n members can connect n cards
  3. for every anchor in experiments/anchors.txt: which active axes it is on
  4. the reachable-neighbour count each anchor gets from the join, i.e.
     |union of that anchor's axes' members| - 1

Usage:  python3 experiments/foundry_wire_capability.py
"""
import collections
import gzip
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
import foundry_probe as p              # noqa: E402
import foundry_common as fc            # noqa: E402

CARDS_PATH = REPO.parent / "data" / "raw" / "oracle-cards.jsonl.gz"
ANCHORS_PATH = REPO / "anchors.txt"


def anchor_names() -> list:
    names = []
    for line in ANCHORS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            names.append(line)
    if not names:
        fc.halt(f"{ANCHORS_PATH} yielded 0 anchor names — a probe reading an "
                f"empty panel reports 'no anchor is covered' as a finding.")
    return names


def name_index() -> dict:
    """name -> [oracle_id]. tier_engine reads this same jsonl, so the corpus
    boundary here is tier_engine's, NOT load_corpus_gated()'s."""
    idx = collections.defaultdict(set)
    with gzip.open(CARDS_PATH, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            card = json.loads(line)
            oid = card.get("oracle_id")
            if oid and card.get("name"):
                idx[card["name"]].add(oid)
    return {k: sorted(v) for k, v in idx.items()}


def main() -> None:
    ctx = p.corpus()
    active = p.active_axes(ctx)

    members_by_axis = {s: [m["oracle_id"] for m in (a.get("members") or [])]
                       for s, a in active.items()}
    axes_by_card = collections.defaultdict(list)
    for slug, oids in members_by_axis.items():
        for oid in oids:
            axes_by_card[oid].append(slug)

    total_memberships = sum(len(v) for v in members_by_axis.values())
    sizes = sorted(len(v) for v in members_by_axis.values())

    print("=" * 78)
    print("1. THE JOIN'S RAW MATERIAL — re-derived, not carried forward")
    print("=" * 78)
    print(f"  active axes                 {len(active):>7,}")
    print(f"  memberships                 {total_memberships:>7,}")
    print(f"  distinct cards covered      {len(axes_by_card):>7,}")

    print()
    print("=" * 78)
    print("2. AXIS SIZE — an axis with n members can connect n cards")
    print("=" * 78)
    bands = [(0, 0), (1, 1), (2, 4), (5, 9), (10, 24), (25, 99), (100, 10 ** 9)]
    for lo, hi in bands:
        n = sum(1 for s in sizes if lo <= s <= hi)
        label = f"{lo}" if lo == hi else (f"{lo}+" if hi > 10 ** 8 else f"{lo}-{hi}")
        held = sum(s for s in sizes if lo <= s <= hi)
        print(f"  {label:>7} members   {n:>4} axes   holding {held:>6,} memberships")
    mid = sizes[len(sizes) // 2]
    print(f"\n  median axis size = {mid}   max = {sizes[-1]}")
    print("  A median-size axis connects an anchor to a handful of cards, not")
    print("  to a neighbourhood. That ceiling is the join's, not the engine's.")

    print()
    print("=" * 78)
    print("3. ANCHOR COVERAGE — an anchor with 0 axes gets derived_agreement 0")
    print("=" * 78)
    names = anchor_names()
    idx = name_index()
    covered = 0
    for name in names:
        oids = idx.get(name, [])
        if len(oids) != 1:
            print(f"  {name:<32} UNRESOLVED ({len(oids)} oracle_ids in the corpus)")
            continue
        oid = oids[0]
        slugs = sorted(axes_by_card.get(oid, []))
        if not slugs:
            print(f"  {name:<32} 0 axes   → the join is a NO-OP for this anchor")
            continue
        covered += 1
        reach = set()
        for s in slugs:
            reach.update(members_by_axis[s])
        reach.discard(oid)
        print(f"  {name:<32} {len(slugs)} axes, {len(reach):>3} reachable neighbours")
        for s in slugs:
            print(f"       {s}  ({len(members_by_axis[s])} members)")

    print()
    print(f"  anchors carrying >=1 active membership: {covered} of {len(names)}")
    print()
    print("  READ THIS BEFORE THE EFFECT MEASUREMENT: the reachable count is a")
    print("  CEILING on how many cards the join can add or move for that")
    print("  anchor. It is not a prediction that any of them are good.")


if __name__ == "__main__":
    main()
