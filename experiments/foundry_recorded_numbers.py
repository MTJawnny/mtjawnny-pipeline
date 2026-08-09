#!/usr/bin/env python3
"""ITEM 4 — RE-MEASURE THE NUMBERS THE DOCUMENTS ASSERT.

Twenty-one probe defects are on the record. The record also says most were
caught before their numbers were used. **"Most" is not "all"**, and a number
that reached a document is a number that outlived the probe that produced it --
CLAUDE.md's own rule, aimed at CLAUDE.md: *"a carried-forward count is not a
measurement."*

This re-derives every line/card count that grammar §2 CLAIMS, from the live
corpus, and reports disagreement. It changes nothing and ratifies nothing.

WHY §2 SPECIFICALLY: those rows are ratified law. A wrong count there is not a
stale note in a handoff, it is a wrong premise inside the document the
extractor parses its vocabulary from.

Built on `foundry_probe` on purpose -- the tool that exists because of probe
defects should not hand-roll its own corpus walk.

    python3 experiments/foundry_recorded_numbers.py
    python3 experiments/foundry_recorded_numbers.py --strict   # exit 1 on drift
"""
import sys
import re
import argparse
import collections
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_probe as p        # noqa: E402

GRAMMAR = REPO_ROOT.parent / "docs" / "CODEBOOK-NAMING-GRAMMAR.md"

# "Measured 2026-08-09: **30 lines / 26 cards**" and the looser "**N lines**".
CLAIM_RE = re.compile(
    r"\*\*(\d[\d,]*)\s+lines?(?:\s*/\s*(\d[\d,]*)\s+cards?)?\*\*", re.I)


def num(s):
    return int(s.replace(",", "")) if s else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    ctx = p.corpus()

    # LIVE counts, measured the one canonical way.
    lines = collections.Counter()
    cards = collections.defaultdict(set)
    for card, line, toks, descs in p.rows(ctx):
        for t in toks:
            base = t
            for pre in ("any-", "other-", "source-"):
                if base.startswith(pre) and base[len(pre):] in ctx.ratified:
                    base = base[len(pre):]
                    break
            lines[base] += 1
            cards[base].add(card["name"])

    # CLAIMED counts, read out of each §2 row.
    text = GRAMMAR.read_text(encoding="utf-8")
    rows = {}
    for line in text.splitlines():
        m = re.match(r"\|\s*`([a-z0-9\-]+)`\s*\|(.*)", line)
        if m and m.group(1) in ctx.ratified:
            rows[m.group(1)] = m.group(2)

    print("=" * 78)
    print("RECORDED vs RE-MEASURED — grammar §2 line/card claims")
    print("=" * 78)
    print(f"  §2 tokens                     {len(ctx.ratified):>6}")
    print(f"  rows carrying a count claim   "
          f"{sum(1 for b in rows.values() if CLAIM_RE.search(b)):>6}")
    print()

    agree, drift, unclaimed = [], [], []
    for tok in sorted(ctx.ratified):
        body = rows.get(tok, "")
        m = CLAIM_RE.search(body)
        live_l, live_c = lines.get(tok, 0), len(cards.get(tok, ()))
        if not m:
            unclaimed.append((tok, live_l, live_c))
            continue
        cl, cc = num(m.group(1)), num(m.group(2))
        ok = (cl == live_l) and (cc is None or cc == live_c)
        (agree if ok else drift).append((tok, cl, cc, live_l, live_c))

    print(f"{'token':34}{'claimed':>20}{'live':>22}")
    print("-" * 78)
    for tok, cl, cc, ll, lc in drift:
        c = f"{cl} lines" + (f" / {cc} cards" if cc is not None else "")
        v = f"{ll} lines / {lc} cards"
        print(f"{tok:34}{c:>20}{v:>22}   <-- DRIFT")
    for tok, cl, cc, ll, lc in agree:
        c = f"{cl} lines" + (f" / {cc} cards" if cc is not None else "")
        v = f"{ll} lines / {lc} cards"
        print(f"{tok:34}{c:>20}{v:>22}   ok")

    print()
    print(f"  claims checked                {len(agree) + len(drift):>6}")
    print(f"  ...agree with the live corpus {len(agree):>6}")
    print(f"  ...DRIFTED                    {len(drift):>6}")
    print(f"  rows with no count claimed    {len(unclaimed):>6}   (not checkable)")

    print("\n" + "=" * 78)
    print("VERDICT")
    print("=" * 78)
    if drift:
        print(f"  ✗ {len(drift)} ratified §2 row(s) assert a count the corpus")
        print("    does not support. A wrong number in §2 is a wrong premise in")
        print("    the document the extractor parses its vocabulary from.")
    else:
        print("  ✓ Every count §2 asserts reproduces from the live corpus.")

    return 1 if (drift and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
