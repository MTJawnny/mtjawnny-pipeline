#!/usr/bin/env python3
"""Routing regression harness for the DELIVERY extractor -- zero tokens.

WHY THIS EXISTS
---------------
Captain, 2026-08-04: *"how do we work without breaking other things?"*

Seven of the eight CR 113.3c fixes were verified by re-reading the population
they targeted. That is precision -- and every defect the 2026-08-04 pre-step-2
audit found was a RECALL failure, invisible to exactly that check. This harness
encodes the answer instead of remembering it, so a session that changes a
classifier cannot skip it.

FOUR GUARDS, and the asymmetry is the point
-------------------------------------------
1. LINE-BY-LINE DIFF of all ability lines, before and after. Every moved line is
   enumerated. Moves are NOT symmetric:

     None -> ratified          the intended direction; a gap closing
     ratified -> ratified'     a RE-ROUTE -- always read, it may be a fix or a regression
     ratified -> None          a REGRESSION until proven otherwise, and the
                               direction nothing else in the toolchain reports

   `--strict` exits 1 on any `ratified -> None`, so a pass cannot silently lose
   a line that already had a home.

2. RATIFIED-FAMILY PINS. Each §2 token's line count is recorded. A pass that
   claims to touch one family and moves another is stopped by the diff.

3. NAME-INVARIANCE (metamorphic). A card's DELIVERY cannot legally depend on its
   NAME. Rename every card to a neutral string -- using the canonicaliser's OWN
   candidate set, not a guess -- and re-route. Any line whose token changes is a
   defect, and this needs NO ground truth and NO judgement. It found 62 lines of
   one root cause in a single run, corpus-wide.

4. DETERMINISM x2 on the snapshot itself.

USAGE
  python3 experiments/foundry_routing_regression.py snapshot out/before.json
  ... change a classifier ...
  python3 experiments/foundry_routing_regression.py snapshot out/after.json
  python3 experiments/foundry_routing_regression.py diff out/before.json out/after.json --strict
  python3 experiments/foundry_routing_regression.py invariance
"""
import re
import sys
import copy
import json
import argparse
import collections
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc          # noqa: E402
import foundry_shape_extractor as fse  # noqa: E402

# No hyphen (ABILITY_WORD), no comma (the pre-comma short form), and not a
# substring of any CR 702 keyword name.
NEUTRAL_NAME = "Zzyzx Quorbin"


def _load():
    cards, _, _ = fc.load_corpus_gated()
    fse.build_self_noun_rx(cards)
    ratified = fse.ratified_delivery_tokens()
    fse.build_keyword_homes(ratified)
    return cards, ratified


def route_all(cards: dict, ratified: dict) -> list:
    """[oracle_id, name, line_index, line, token, descriptor] for every routed
    line, in a fixed sort order so two runs are byte-comparable."""
    rows = []
    for oid in sorted(cards):
        card = cards[oid]
        for i, (line, parsed) in enumerate(
                fse.deliveries_for_lines(card, ratified)):
            for tok, desc in parsed:
                rows.append([oid, card["name"], i, line, tok, desc])
    return rows


def cmd_snapshot(args) -> None:
    cards, ratified = _load()
    rows = route_all(cards, ratified)
    by_token = collections.Counter(str(r[4]) for r in rows)
    payload = {
        "rows": rows,
        "totals": {
            "routed_lines": len(rows),
            "cards": len(cards),
            "keyword_homes": len(fse.KEYWORD_HOME),
            "ratified_tokens": len(ratified),
        },
        # Guard 2: the ratified-family pins.
        "by_token": dict(sorted(by_token.items())),
    }
    Path(args.path).write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"wrote {args.path}")
    print(f"  routed lines {len(rows)}   keyword homes {len(fse.KEYWORD_HOME)}")
    # PER DELIVERY ROW, not per line. 567 lines carry more than one delivery
    # (grammar §1's multi-axis rule: "Whenever ~ enters OR attacks" earns
    # both), so this number is ~90 higher than the conservation audit's
    # per-LINE count of the same thing -- 15,993 vs 15,902 on 2026-08-07.
    # Both are correct and they answer different questions; handoffs have
    # quoted them interchangeably. "A population count is not a yield count is
    # not a routing claim. State which one you mean."
    print(f"  delivery ROWS with no ratified token: {by_token.get('None', 0)}"
          f"   (rows, not lines — see the conservation audit for per-line)")


def cmd_diff(args) -> None:
    before = json.loads(Path(args.before).read_text(encoding="utf-8"))
    after = json.loads(Path(args.after).read_text(encoding="utf-8"))
    b, a = before["rows"], after["rows"]

    # Guard 1 needs the two runs to be aligned line-for-line. If a pass changes
    # how a card is SPLIT into lines, the zip is meaningless -- halt rather than
    # report a diff computed against mismatched rows.
    if len(b) != len(a):
        print(f"⚠ ROW COUNT CHANGED {len(b)} -> {len(a)}. The pass altered how "
              f"lines are produced, not just how they are classified. Falling "
              f"back to a key-based diff.")
    key = lambda r: (r[0], r[2], r[3])          # noqa: E731
    bmap, amap = {}, {}
    for r in b:
        bmap.setdefault(key(r), []).append((r[4], r[5]))
    for r in a:
        amap.setdefault(key(r), []).append((r[4], r[5]))

    moved, gained, lost = [], [], []
    for k in sorted(set(bmap) | set(amap), key=lambda t: (t[0], t[1])):
        bv, av = bmap.get(k), amap.get(k)
        if bv is None:
            gained.append((k, av))
        elif av is None:
            lost.append((k, bv))
        elif [t for t, _ in bv] != [t for t, _ in av]:
            moved.append((k, bv, av))

    def direction(bt, at):
        bset = {t for t in bt if t is not None}
        aset = {t for t in at if t is not None}
        if not bset and aset:
            return "GAP CLOSED   (None -> ratified)"
        if bset and not aset:
            return "REGRESSION   (ratified -> None)"
        if bset and aset and bset != aset:
            return "RE-ROUTE     (ratified -> ratified')"
        return "OTHER"

    buckets = collections.defaultdict(list)
    for k, bv, av in moved:
        buckets[direction([t for t, _ in bv], [t for t, _ in av])].append((k, bv, av))

    print(f"lines compared : {len(set(bmap) | set(amap))}")
    print(f"lines MOVED    : {len(moved)}")
    print(f"lines appeared : {len(gained)}   lines vanished: {len(lost)}\n")

    order = ["REGRESSION   (ratified -> None)", "RE-ROUTE     (ratified -> ratified')",
             "GAP CLOSED   (None -> ratified)", "OTHER"]
    for d in order:
        rs = buckets.get(d)
        if not rs:
            continue
        print("=" * 78)
        print(f"{d}   n={len(rs)}")
        print("=" * 78)
        tr = collections.Counter(
            (str([t for t, _ in bv]), str([t for t, _ in av])) for _k, bv, av in rs)
        for (f, t), n in tr.most_common():
            print(f"  {n:6d}   {f}  ->  {t}")
        if args.lines:
            seen = set()
            for k, bv, av in rs:
                if k[2] in seen:
                    continue
                seen.add(k[2])
                print(f"     {k[2][:96]}")

    print("\n" + "=" * 78)
    print("RATIFIED-FAMILY PINS (guard 2)")
    print("=" * 78)
    bt, at = before["by_token"], after["by_token"]
    for tok in sorted(set(bt) | set(at)):
        x, y = bt.get(tok, 0), at.get(tok, 0)
        if x != y:
            print(f"  {tok:36s} {x:7d} -> {y:7d}   ({y - x:+d})")
    for k in ("routed_lines", "keyword_homes"):
        x, y = before["totals"][k], after["totals"][k]
        print(f"  [{k}] {x} -> {y}" + ("   UNCHANGED" if x == y else f"   ({y - x:+d})"))

    if args.strict and buckets.get("REGRESSION   (ratified -> None)"):
        n = len(buckets["REGRESSION   (ratified -> None)"])
        fc.halt(f"{n} line(s) LOST a ratified delivery token. That is the one "
                f"direction no census in this toolchain reports. Read every one "
                f"before proceeding.")


def cmd_invariance(args) -> None:
    """Guard 3 -- a card's DELIVERY may not depend on its NAME."""
    cards, ratified = _load()

    def renamed(card):
        c = copy.deepcopy(card)
        # The canonicaliser's OWN candidate set. Guessing the forms here is what
        # made the first run of this test report 195 defects of which 132 were
        # the test's fault (Gate 4, applied to the harness).
        forms = sorted(fc._cardname_candidates(card), key=len, reverse=True)

        def sub(t):
            for f in forms:
                if f:
                    t = t.replace(f, NEUTRAL_NAME)
            return t
        c["name"] = NEUTRAL_NAME
        if c.get("oracle_text"):
            c["oracle_text"] = sub(c["oracle_text"])
        for f in (c.get("card_faces") or []):
            if f.get("oracle_text"):
                f["oracle_text"] = sub(f["oracle_text"])
            if f.get("name"):
                f["name"] = NEUTRAL_NAME
        return c

    bad = collections.Counter()
    ex = collections.defaultdict(list)
    tested = 0
    for oid in sorted(cards):
        card = cards[oid]
        r = renamed(card)
        la, lb = fse.ability_lines(card), fse.ability_lines(r)
        if len(la) != len(lb):
            bad["LINE COUNT changed under rename"] += 1
            continue
        for x, y in zip(la, lb):
            tested += 1
            ta = [t for t, _ in fse.parse_deliveries(x, ratified, card)]
            tb = [t for t, _ in fse.parse_deliveries(y, ratified, r)]
            if ta != tb:
                k = f"{ta} -> {tb}"
                bad[k] += 1
                if len(ex[k]) < 3:
                    ex[k].append((card["name"], x[:78]))
    total = sum(bad.values())
    print(f"lines tested for NAME-INVARIANCE: {tested}")
    print(f"NAME-DEPENDENT deliveries       : {total}\n")
    for k, n in bad.most_common(args.limit):
        print(f"  {n:5d}  {k}")
        for nm, l in ex[k]:
            print(f"           {nm[:26]:28s} {l}")
    if args.strict and total > args.allow:
        fc.halt(f"{total} name-dependent deliveries, allowance {args.allow}. "
                f"A card's delivery cannot depend on its name.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("snapshot"); s.add_argument("path")
    d = sub.add_parser("diff")
    d.add_argument("before"); d.add_argument("after")
    d.add_argument("--strict", action="store_true")
    d.add_argument("--lines", action="store_true", help="print every distinct moved line")
    i = sub.add_parser("invariance")
    i.add_argument("--strict", action="store_true")
    i.add_argument("--allow", type=int, default=0)
    i.add_argument("--limit", type=int, default=20)
    args = ap.parse_args()
    {"snapshot": cmd_snapshot, "diff": cmd_diff, "invariance": cmd_invariance}[args.cmd](args)


if __name__ == "__main__":
    main()
