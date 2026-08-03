#!/usr/bin/env python3
"""DET scope census inside the five self-vs-other trigger families -- zero tokens.

WHY THIS EXISTS
---------------
`DELIVERY-GAP-CENSUS-2026-08-03.md` measured 1,921 cards whose trigger is keyed
on a permanent OTHER than the source, and proposed that one scope-slot
convention could name all five families at once. That proposal cannot be ruled
on a total. It needs the breakdown, because grammar §6a makes two things axis
identity that a bare total hides:

  §6a rule 3  "another / other -- EXCLUDES the source. A slug may not claim it
              of a member whose printed text can affect itself."
  §6a rule 2  "you control / ownership -- a restriction on the affected object.
              'Any' must mean any."

So "whenever ANOTHER creature enters" and "whenever A creature enters" are NOT
the same printed shape -- the second one also fires on the source's own arrival.
And "a creature YOU CONTROL dies" is not "a creature dies". Any convention that
names only self-vs-other leaves both distinctions unnamed.

This tool measures the actual matrix so the ruling can be made on real numbers:

    SUBJECT   x   CONTROLLER   x   OBJECT CLASS

It judges nothing and writes nothing to the codebook. Shapes it cannot classify
are reported as UNCLASSIFIED with their printed clause, never bucketed.

USAGE
  python3 experiments/foundry_selfother_scope.py
  python3 experiments/foundry_selfother_scope.py --family other-creature-dies
  python3 experiments/foundry_selfother_scope.py --samples 6
  python3 experiments/foundry_selfother_scope.py --json out.json
"""
import re
import sys
import json
import argparse
import collections
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc                # noqa: E402
import foundry_shape_extractor as fse      # noqa: E402

# The five families the census named. Sourced from the extractor's own
# descriptors so the two agree by construction -- if it renames one, this halts
# rather than silently measuring nothing.
FAMILIES = [
    "other-permanent-enters",
    "other-creature-dies",
    "other-creature-attacks",
    "other-creature-combat-damage-player",
    "other-permanent-ltb",
]

# SUBJECT -- does the printed trigger subject exclude the source? (§6a rule 3)
SUBJ_ANOTHER = re.compile(r"\banother\b|\bother\b")
# CONTROLLER -- §6a rule 2. Ordered: the first match wins, most specific first.
CONTROLLER = [
    ("opponent", re.compile(r"\ban opponent controls\b|\byour opponents? controls?\b"
                            r"|\bopponent's\b")),
    ("own",      re.compile(r"\byou control\b|\byour\b")),
    ("each",     re.compile(r"\beach\b|\ball\b")),
]
OBJECT_CLASS = [
    ("creature",     re.compile(r"\bcreatures?\b")),
    ("artifact",     re.compile(r"\bartifacts?\b")),
    ("enchantment",  re.compile(r"\benchantments?\b")),
    ("planeswalker", re.compile(r"\bplaneswalkers?\b")),
    ("land",         re.compile(r"\blands?\b")),
    ("token",        re.compile(r"\btokens?\b")),
    ("permanent",    re.compile(r"\bpermanents?\b")),
]


def classify_clause(clause: str) -> dict:
    subject = "another" if SUBJ_ANOTHER.search(clause) else "bare-a"
    controller = None
    for name, rx in CONTROLLER:
        if rx.search(clause):
            controller = name
            break
    obj = None
    for name, rx in OBJECT_CLASS:
        if rx.search(clause):
            obj = name
            break
    return {"subject": subject,
            "controller": controller or "UNQUALIFIED",
            "object": obj or "UNCLASSIFIED"}


def collect(cards: dict, ratified: dict) -> list:
    rows = []
    for oid, card in cards.items():
        for line in fse.ability_lines(card):
            for tok, desc in fse.parse_deliveries(line, ratified, card):
                if tok is not None or desc not in FAMILIES:
                    continue
                body = fse.ABILITY_WORD.sub("", line.strip())
                body = fc.canonicalize_self_reference(body, card)
                clause = fse.trigger_clause(body.lower())
                row = classify_clause(clause)
                row.update({"family": desc, "name": card["name"],
                            "oracle_id": oid, "clause": clause.strip()})
                rows.append(row)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", help="restrict to one family")
    ap.add_argument("--samples", type=int, default=0,
                    help="print N printed clauses per cell")
    ap.add_argument("--json", metavar="PATH")
    args = ap.parse_args()

    cards, _, _gated_out = fc.load_corpus_gated()
    fse.build_self_noun_rx(cards)
    ratified = fse.ratified_delivery_tokens()
    rows = collect(cards, ratified)
    if not rows:
        fc.halt("Zero rows collected. The shape extractor's family descriptors "
                "have changed; re-derive FAMILIES from it, do not guess.")

    if args.family:
        if args.family not in FAMILIES:
            fc.halt(f"{args.family!r} is not one of: {', '.join(FAMILIES)}")
        rows = [r for r in rows if r["family"] == args.family]

    cards_total = len({r["oracle_id"] for r in rows})
    print(f"self-vs-other families: {len(FAMILIES)}")
    print(f"ability lines: {len(rows)}   distinct cards: {cards_total}\n")

    print("SUBJECT x CONTROLLER  -- the matrix a scope convention must cover")
    print("(§6a rule 3: 'another' excludes the source; 'a' does NOT)")
    print("-" * 74)
    grid = collections.Counter((r["subject"], r["controller"]) for r in rows)
    controllers = sorted({c for _, c in grid})
    print(f"{'subject':12s}" + "".join(f"{c:>14s}" for c in controllers)
          + f"{'total':>10s}")
    for subj in ("another", "bare-a"):
        cells = [grid.get((subj, c), 0) for c in controllers]
        print(f"{subj:12s}" + "".join(f"{n:14d}" for n in cells)
              + f"{sum(cells):10d}")

    print("\nBY FAMILY")
    print("-" * 74)
    print(f"{'family':38s}{'another':>10s}{'bare-a':>10s}{'cards':>9s}")
    for fam in FAMILIES:
        fr = [r for r in rows if r["family"] == fam]
        if not fr:
            continue
        a = sum(1 for r in fr if r["subject"] == "another")
        print(f"{fam:38s}{a:10d}{len(fr) - a:10d}"
              f"{len({r['oracle_id'] for r in fr}):9d}")

    print("\nOBJECT CLASS")
    print("-" * 74)
    for obj, n in collections.Counter(r["object"] for r in rows).most_common():
        print(f"  {obj:16s}{n:6d}")

    if args.samples:
        print("\nPRINTED CLAUSES -- evidence, per cell")
        print("=" * 74)
        cells = collections.defaultdict(list)
        for r in rows:
            cells[(r["subject"], r["controller"])].append(r)
        for key in sorted(cells):
            print(f"\n[{key[0]} / {key[1]}]  ({len(cells[key])} lines)")
            seen = set()
            for r in cells[key]:
                if r["name"] in seen:
                    continue
                seen.add(r["name"])
                print(f"  {r['name'][:34]:34s} {r['clause'][:90]}")
                if len(seen) >= args.samples:
                    break

    if args.json:
        Path(args.json).write_text(json.dumps(rows, indent=1), encoding="utf-8")
        print(f"\nwrote {args.json}")


if __name__ == "__main__":
    main()
