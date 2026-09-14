"""CR 702 keyword ability-class census — the operator report and CLI.

## What this is

The operator half S6 and S7 left in the legacy `foundry_cr702_classes` shell:
the class tables over the per-keyword rows, the unresolved-multiplicity list, the
`--unstated` listing, the `--homes` routing report and the `--json` dump. S13
moved them here. Every flag, line and output byte is the shell's.

## The declared defect travels with it, unrepaired

`--unstated` reads `r["cr_class"]`, a key no row carries, so it raises
`KeyError: 'cr_class'` after printing its section header. That is accepted,
recorded operator debt. It is moved exactly as it is and is NOT fixed here.

## What this is NOT

* **Not CR 702 parsing or classification.** `load_702`, `classify`,
  `effective_classes`, the per-keyword rows and the class vocabulary are
  `mtj_foundry.mtg.cr.keywords`; keyword homes are
  `mtj_foundry.mtg.shapes.delivery.keyword_homes`. This module composes and
  renders what they return.
* **Not a corpus loader or a process boundary.** The CR location, the halting
  loader and the corpus-bound homes computation come from the composition
  boundary, which owns the historic `STOP — …`.
"""

from __future__ import annotations

import argparse
import collections
import dataclasses
import json
from pathlib import Path
from typing import Callable

from mtj_foundry.mtg.cr import keywords as _keywords

__all__ = ["Cr702Context", "build_parser", "homes_lines", "run"]


@dataclasses.dataclass(frozen=True)
class Cr702Context:
    cr_path: Path
    load_702: Callable[[Path], dict]
    keyword_rows: Callable[[Path], list]
    homes: Callable[[list, dict], None]


def homes_lines(rows: list, recs: dict):
    """Attach each row's routed home (mutating `rows`, as the JSON dump expects)
    and yield the routing report."""
    homed = collections.defaultdict(list)
    unresolved = []
    for r in rows:
        rec = recs[int(r["cr"].split(".")[1])]
        r["home"] = rec["home"]
        r["home_descriptor"] = rec["home_descriptor"]
        r["cr_text"] = rec["cr_text"]
        if rec["home_via"]:
            r["home_via"] = rec["home_via"]
        if rec["home"] is not None:
            homed[rec["home"]].append(r)
        else:
            unresolved.append((r, rec["unresolved_reason"]))

    total = sum(len(v) for v in homed.values())
    yield (f"\n{'='*78}\nKEYWORD -> DELIVERY HOME, derived from the CR's own "
           f"templated text\n{'='*78}")
    yield f"routed to an EXISTING ratified token: {total} of {len(rows)} keywords\n"
    for tok in sorted(homed, key=lambda t: -len(homed[t])):
        names = ", ".join(sorted(r["keyword"] for r in homed[tok]))
        yield f"[{tok}]  ({len(homed[tok])})\n  {names}\n"

    yield (f"{'='*78}\nNOT ROUTED — {len(unresolved)} keywords. Reported, never "
           f"approximated.\n{'='*78}")
    by_reason = collections.defaultdict(list)
    for r, why in unresolved:
        by_reason[why].append(r["keyword"])
    for why in sorted(by_reason, key=lambda w: -len(by_reason[w])):
        yield (f"\n({len(by_reason[why])}) {why}\n  "
               + ", ".join(sorted(by_reason[why])))


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    ap.add_argument("--unstated", action="store_true",
                    help="list keywords whose CR text states no ability class")
    ap.add_argument("--homes", action="store_true",
                    help="route each keyword to its §2 DELIVERY token, derived "
                         "from the CR's own templated text")
    ap.add_argument("--json", metavar="PATH")
    return ap


def run(argv, ctx: Cr702Context) -> None:
    args = build_parser().parse_args(argv)

    keywords = ctx.load_702(ctx.cr_path)
    # The rows are the S6 owner's derivation (`keywords.keyword_rows`), reached
    # through the boundary's halting wrapper -- not restated here.
    rows = ctx.keyword_rows(ctx.cr_path)

    def label(r, key):
        v = r[key]
        return "+".join(v) if v else "UNSTATED"

    by_class = collections.Counter(label(r, "cr_classes") for r in rows)
    by_effective = collections.Counter(label(r, "effective_classes")
                                       for r in rows)

    print(f"CR file: {ctx.cr_path}")
    print(f"CR 702 keywords parsed: {len(rows)}\n")
    print("AS THE CR WORDS IT")
    print(f"{'CR ability class':26s} {'keywords':>9}")
    print("-" * 78)
    for cls, n in by_class.most_common():
        note = ""
        if cls in _keywords.SUBSUMES:
            note = (f"   -> rolls up to {_keywords.SUBSUMES[cls][0]} "
                    f"({_keywords.SUBSUMES[cls][1]})")
        print(f"{cls:26s} {n:9d}{note}")

    print("\nAFTER CR-STATED ROLLUP -- what the §2 DELIVERY slot must be")
    print(f"{'ability class':26s} {'keywords':>9}   {'§2 DELIVERY slot':s}")
    print("-" * 78)
    for cls, n in by_effective.most_common():
        slot = _keywords.CLASS_TO_DELIVERY.get(cls, "— no §2 slot —")
        print(f"{cls:26s} {n:9d}   {slot}")

    print("\nkeywords by class")
    print("-" * 78)
    grouped = collections.defaultdict(list)
    for r in rows:
        grouped[label(r, "effective_classes")].append(r["keyword"])
    for cls, n in by_effective.most_common():
        names = ", ".join(sorted(grouped[cls]))
        print(f"\n[{cls}]  ({n})\n  {names}")

    unresolved = [r for r in rows if r["multi_hint_unresolved"]]
    if unresolved:
        print("\n" + "=" * 78)
        print("⚠ MULTIPLICITY HINTED BUT NOT RESOLVED -- read these by hand.")
        print("The CR prose says the keyword represents several abilities, but")
        print("only one class sentence parsed. Reported, never assumed.")
        print("=" * 78)
        for r in unresolved:
            print(f"  {r['cr']:9s} {r['keyword']}")

    if args.unstated:
        print("\n" + "=" * 78)
        print("UNSTATED -- the CR does not call these '<X> ability' in 702.Na.")
        print("Reported, NOT assigned to a nearest class.")
        print("=" * 78)
        for r in rows:
            # Declared debt, carried unrepaired: no row has a `cr_class` key.
            if r["cr_class"] is None:
                first = (r["evidence"] or
                         keywords[int(r['cr'].split('.')[1])]["subrules"].get("a", ""))
                print(f"  {r['cr']:9s} {r['keyword']:28s} {first[:90]}")

    if args.homes:
        ctx.homes(rows, keywords)

    if args.json:
        Path(args.json).write_text(json.dumps(rows, indent=1), encoding="utf-8")
        print(f"\nwrote {args.json}")
