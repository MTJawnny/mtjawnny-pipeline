#!/usr/bin/env python3
"""RULE-BY-RULE DIFF OF TWO CR EDITIONS — is the new file trustworthy?

WHY THIS EXISTS
---------------
`docs/NEXT-SESSION-CR-NORMALIZATION.md` §"ONE THING TO CONFIRM FIRST":

    The filename says `_LLM.md`, which suggests a version prepared for LLM
    consumption — possibly a derivative rather than WotC's official text. …
    for a document this repo treats as ground truth, confirm … If third-party,
    diff it against the official text before it becomes the source of every
    derived vocabulary.

The file's own front matter answers half of it outright — `format:
"LLM-optimized Markdown"`, `source_fidelity: "content preserved; formatting
normalized"` — so it IS a reformatting, not WotC's raw release. That makes the
question measurable rather than a matter of asking: the vendored 2026-06-19
edition is WotC-derived plain text, so **every rule whose text is byte-identical
across the two editions is a rule the reformatting provably did not touch.**

What that can and cannot prove, stated because a finding without its boundary
is not reportable:

  · IT CAN PROVE that the reformatting did not silently alter the ~3,100 rules
    the two editions share. That is the failure mode that matters here — a
    derivative that quietly drops a clause is undetectable downstream and would
    poison every enumeration this pipeline parses.
  · IT CANNOT PROVE that a CHANGED rule changed the way WotC changed it. Those
    are exactly the rules the June edition cannot adjudicate, and they are
    listed by number so a human can read them against the official release.

A CHANGED rule is therefore reported, never judged — the same discipline
`foundry_cr702_classes` uses for an UNSTATED keyword class.

USAGE
    python3 experiments/foundry_cr_edition_diff.py
    python3 experiments/foundry_cr_edition_diff.py --changed     # full text
    python3 experiments/foundry_cr_edition_diff.py --area 106    # one rule area
"""
import re
import sys
import argparse
import difflib
import collections
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc     # noqa: E402
import foundry_cr as cr         # noqa: E402
import foundry_probe as p       # noqa: E402

# A rule line in the normalized shape: `205.2a <text>` or `205.2. <text>`.
# Two-letter subrules are real as of the 2026-08-07 edition (704.5aa).
RULE_LINE = re.compile(r"^(\d{3}\.\d+[a-z]{0,2})(?:\.)?\s+(\S.*)$")

# GUARD D fixture. Every case is a line that has actually appeared in one of
# the two editions, plus the near-misses that an over-narrow rule parser drops
# — and an over-narrow parser here would UNDER-report the diff, which reads as
# a clean fidelity result. That is the exact defect shape this guards.
_RULE_LINE_CASES = [
    ("205.2a The card types are artifact, battle, conspiracy.", True),
    ("702.6. Equip", True),
    ("120.1. Objects can deal damage to battles, creatures.", True),
    ("704.5aa If a player controls a permanent with start your engines!", True),
    ("113.3c Triggered abilities have a trigger condition and an effect.", True),
    # Not rule lines, and each has a shape close enough to be caught by a
    # sloppier pattern:
    ("Example: Lost Order of Jarkeld has power and toughness each 1+*.", False),
    ("## 702. Keyword Abilities", False),
    ("See rule 605.1a for mana abilities.", False),
    ("1. Text on an object that explains what that object does.", False),
    ("", False),
]


def parse_rules(text: str) -> dict:
    """{rule number -> text} for one normalized edition.

    Halts on a duplicate number rather than letting a later line silently win:
    a collision means the rule pattern is over-broad and is eating prose, which
    would then be diffed as if it were a rules change.
    """
    out = {}
    for n, line in enumerate(text.splitlines(), start=1):
        m = RULE_LINE.match(line)
        if not m:
            continue
        num, body = m.group(1), m.group(2).strip()
        if num in out and out[num] != body:
            fc.halt(f"rule {num} parsed twice with different text (line {n}). "
                    f"RULE_LINE is matching something that is not a rule; fix "
                    f"the pattern rather than dropping the collision.\n"
                    f"  first: {out[num][:100]!r}\n  again: {body[:100]!r}")
        out[num] = body
    if not out:
        fc.halt("parsed zero rules from a normalized CR — the loader or this "
                "pattern is broken. Never report that as 'no differences'.")
    return out


def _sort_key(num: str):
    m = re.match(r"^(\d{3})\.(\d+)([a-z]{0,2})$", num)
    return (int(m.group(1)), int(m.group(2)), m.group(3))


def _cosmetic(a: str, b: str) -> bool:
    """Do these two texts differ only in whitespace and quote characters?

    Reported separately because a cosmetic difference is a REFORMATTING
    artifact — the thing the fidelity question is actually about — while a
    wording difference between a June and an August edition is most likely a
    real rules update. Neither is judged here; the split just stops the two
    from being counted as one number.
    """
    def flat(s):
        s = s.replace("’", "'").replace("“", '"').replace("”", '"')
        s = s.replace("—", "-").replace("–", "-")
        return re.sub(r"\s+", " ", s).strip()
    return flat(a) == flat(b)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--changed", action="store_true",
                    help="print the full text of every changed rule")
    ap.add_argument("--area", metavar="NNN",
                    help="restrict every listing to one CR rule area, e.g. 106")
    args = ap.parse_args()

    p.must_capture(RULE_LINE.match, _RULE_LINE_CASES, name="RULE_LINE")

    if not cr.PRIOR_CR_PATH.exists():
        fc.halt(f"the prior edition is not at {cr.PRIOR_CR_PATH}, so the new "
                f"file cannot be verified as a COMPARISON. Refusing to report "
                f"a fidelity result without one.")

    new_txt, old_txt = cr.text(cr.CR_PATH), cr.text(cr.PRIOR_CR_PATH)
    new, old = parse_rules(new_txt), parse_rules(old_txt)

    added = sorted(set(new) - set(old), key=_sort_key)
    removed = sorted(set(old) - set(new), key=_sort_key)
    shared = sorted(set(new) & set(old), key=_sort_key)
    identical = [n for n in shared if new[n] == old[n]]
    cosmetic = [n for n in shared if new[n] != old[n] and _cosmetic(old[n], new[n])]
    reworded = [n for n in shared if new[n] != old[n] and not _cosmetic(old[n], new[n])]

    def keep(nums):
        if not args.area:
            return nums
        return [n for n in nums if n.startswith(args.area + ".")]

    print("=" * 78)
    print("CR EDITION DIFF — rule by rule, both editions read through the "
          "normalizing loader")
    print("=" * 78)
    print(f"  new    {cr.effective_date(new_txt):>16s}   {len(new):5d} rules   "
          f"{cr.CR_PATH.name}")
    print(f"  prior  {cr.effective_date(old_txt):>16s}   {len(old):5d} rules   "
          f"{cr.PRIOR_CR_PATH.name}")
    print()
    print(f"  BYTE-IDENTICAL across editions      {len(identical):5d}   "
          f"({100.0 * len(identical) / len(shared):.1f}% of shared)")
    print(f"  differ in whitespace/quotes only    {len(cosmetic):5d}   "
          f"<- reformatting artifacts, if any")
    print(f"  reworded                            {len(reworded):5d}   "
          f"<- June cannot adjudicate these")
    print(f"  added in the new edition            {len(added):5d}")
    print(f"  removed since the prior edition     {len(removed):5d}")

    print("\nWHAT THIS DOES AND DOES NOT ESTABLISH")
    print("-" * 78)
    print(f"  The {len(identical)} identical rules are text the reformatting "
          f"provably did not\n  alter — they match a WotC-derived plain-text "
          f"edition character for\n  character, including every curly "
          f"apostrophe. The {len(reworded) + len(added)} reworded or new\n"
          f"  rules are NOT verified here and are listed below by number so "
          f"they can\n  be read against the official release.")

    if cosmetic:
        print("\n" + "=" * 78)
        print(f"⚠ {len(cosmetic)} RULE(S) DIFFER ONLY IN WHITESPACE OR QUOTE "
              f"CHARACTERS")
        print("These are the signature of a reformatting touching content. "
              "Read them.")
        print("=" * 78)
        for num in keep(cosmetic):
            print(f"\n  {num}")
            for line in difflib.unified_diff(
                    [old[num]], [new[num]], lineterm="", n=0,
                    fromfile="prior", tofile="new"):
                print(f"    {line[:150]}")

    print("\n" + "=" * 78)
    print(f"REWORDED — {len(reworded)}, by CR area. Reported, never judged.")
    print("=" * 78)
    by_area = collections.Counter(n.split(".")[0] for n in reworded)
    for area, count in sorted(by_area.items()):
        nums = ", ".join(n for n in reworded if n.startswith(area + "."))
        print(f"  {area}  ({count:3d})  {nums[:120]}{'…' if len(nums) > 120 else ''}")

    if added:
        print("\n" + "=" * 78)
        print(f"ADDED — {len(added)}")
        print("=" * 78)
        for num in keep(added):
            print(f"  {num:12s} {new[num][:110]}")
    if removed:
        print("\n" + "=" * 78)
        print(f"REMOVED — {len(removed)}")
        print("=" * 78)
        for num in keep(removed):
            print(f"  {num:12s} {old[num][:110]}")

    if args.changed:
        print("\n" + "=" * 78)
        print("REWORDED, in full")
        print("=" * 78)
        for num in keep(reworded):
            print(f"\n  {num}")
            print(f"    prior  {old[num]}")
            print(f"    new    {new[num]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
