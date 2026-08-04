#!/usr/bin/env python3
"""Does the DET SCAN LAYER honour grammar §6a's reminder-text boundary?

Two ratified artifacts say it must:

  grammar §6a (Captain-ratified 2026-08-02)
      "A card's claim is its printed oracle text with reminder-text
       parentheticals EXCLUDED -- a token-definition parenthetical states what
       the TOKEN does, which §2's created-ability rule assigns to the token,
       not the card."

  docs/det-patterns-cr-actions-v1.json, the ratified CR-action batch, in its
  own note
      "Reminder text is stripped before matching (grammar §6a / tier-4 §S4):
       a Clue token's own reminder text is the TOKEN's ability."

`foundry_common.det_scan_texts()` does not strip it. `ability_lines()` does, so
the two halves of the pipeline have disagreed since the DET standard was
ratified, and 167 live codebook memberships (3.97% of all DET assignments)
exist ONLY because a pattern matched inside a parenthetical.

Nothing else in the toolchain can see this. The routing regression compares
delivery tokens, which are a different layer; the family sweep checks
pattern/axis correspondence; definition drift's C4 reads the DEFINITION, not
the evidence. The visibility audit's `align()` even documents the mismatch in
passing and compensates for it locally, without anything asking whether the
mismatch was intended.

**Exits 0 by default, on purpose.** The finding is a ruling proposal --
`docs/REMINDER-TEXT-DET-CONFORMANCE-2026-08-07.md` -- and a ruling doc is not
load-bearing until Captain ratifies it. Removing the memberships is a codebook
mutation and is LOGGED, NOT EXECUTED. `--strict` makes it a gate, for after.

    python3 experiments/foundry_reminder_conformance.py
    python3 experiments/foundry_reminder_conformance.py --strict --json out.json
"""
import sys
import re
import json
import argparse
import collections
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc            # noqa: E402
import foundry_shape_extractor as fx   # noqa: E402

BATCHES = ("det-patterns-v1.json", "det-patterns-v2.json",
           "det-patterns-cr-actions-v1.json")


def rule(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


def ratified_patterns() -> dict:
    """Every ratified DET pattern, read from the batch files, never re-typed.

    `rule:kicker-conditional-bonus-effect` carries a null pattern -- the axis
    was retired in grammar §2g -- and is skipped rather than crashed on.
    """
    docs = REPO_ROOT.parent / "docs"
    seen = {}
    for name in BATCHES:
        path = docs / name
        if not path.exists():
            fc.halt(f"ratified DET pattern batch missing: {path}. This file's "
                    f"whole premise is that those batches are the source.")
        for p in json.loads(path.read_text(encoding="utf-8")).get("patterns", []):
            if isinstance(p.get("pattern"), str):
                seen[p["slug"]] = p["pattern"]
    if not seen:
        fc.halt("no ratified DET patterns parsed — do not silently pass.")
    return seen


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 on any violation (for AFTER ratification)")
    ap.add_argument("--json")
    ap.add_argument("--limit", type=int, default=14)
    args = ap.parse_args()

    cards, _, _ = fc.load_corpus_gated()
    patterns = ratified_patterns()

    total = 0
    offend = collections.defaultdict(list)
    for slug, pat in sorted(patterns.items()):
        rx = re.compile(pat, re.I)
        for oid, card in cards.items():
            texts = fc.det_scan_texts(card)
            if not any(rx.search(t) for t in texts):
                continue
            total += 1
            # The SAME texts, with §6a applied. If the pattern no longer hits,
            # the only thing that matched was reminder text.
            if any(rx.search(fx.strip_reminder(t)) for t in texts):
                continue
            span = ""
            for t in texts:
                for m in fx.REMINDER.finditer(t):
                    if rx.search(m.group(0)):
                        span = m.group(0)
                        break
                if span:
                    break
            offend[slug].append((card["name"], span))

    n = sum(len(v) for v in offend.values())
    rule("§6a CONFORMANCE OF THE DET SCAN LAYER")
    print(f"  ratified DET patterns                {len(patterns):>7}")
    print(f"  card→pattern assignments             {total:>7}")
    print(f"  assignments from REMINDER TEXT ONLY  {n:>7}"
          + (f"   ({n / total:.2%})" if total else ""))
    print(f"  axes affected                        {len(offend):>7}")

    if offend:
        rule("BY AXIS — and the parenthetical that did it")
        for slug in sorted(offend, key=lambda s: -len(offend[s])):
            rows = offend[slug]
            print(f"\n  {slug}   n={len(rows)}")
            for span, k in collections.Counter(s for _, s in rows).most_common(2):
                print(f"     {k:>4}x  {span[:96] if span else '(no span captured)'}")
            print(f"     e.g. {', '.join(r[0] for r in rows[:3])}")

    rule("VERDICT")
    if not n:
        print("  ✓ No DET assignment depends on reminder text. §6a holds across")
        print("    both halves of the pipeline.")
    else:
        print(f"  ◐ {n} live membership(s) exist only because a pattern matched")
        print("    inside a parenthetical, against grammar §6a and against the")
        print("    ratified CR-action batch's own note.")
        print("\n    RULING PROPOSED, NOT EXECUTED — removing these is a codebook")
        print("    mutation and needs Captain's word:")
        print("      docs/REMINDER-TEXT-DET-CONFORMANCE-2026-08-07.md")
        if not args.strict:
            print("\n    Exiting 0: a ruling doc is not load-bearing until ratified.")
            print("    Use --strict to gate on it once it is.")

    if args.json:
        Path(args.json).write_text(json.dumps({
            "patterns": len(patterns), "assignments": total, "reminder_only": n,
            "by_axis": {s: [list(r) for r in v] for s, v in offend.items()},
        }, indent=2, sort_keys=True))
        print(f"\nwrote {args.json}")
    sys.exit(1 if (n and args.strict) else 0)


if __name__ == "__main__":
    main()
