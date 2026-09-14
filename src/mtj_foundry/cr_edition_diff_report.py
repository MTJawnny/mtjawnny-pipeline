"""CR edition diff — rule-by-rule comparison of two normalized CR editions.

## What this is

The operator diagnostic that S6 rebucketed to "later operator work": parse both
editions into `{rule number -> text}`, split shared rules into byte-identical,
whitespace/quote-only and reworded, and report added and removed rules —
reported, never judged. S13 moved the parse, the comparison, the report and the
CLI here from the legacy `foundry_cr_edition_diff` shell. Every line and every
refusal message is the shell's, character for character.

## What this is NOT

* **Not CR normalization.** Both editions arrive already normalized through
  `mtj_foundry.mtg.cr.edition`, by the boundary's readers.
* **Not a reader or a process boundary.** The edition paths, whether the prior
  edition exists, the readers, the rule-pattern capture guard and the historic
  `STOP — …` all come from the composition boundary. A malformed parse RAISES
  `RuleParseError`; the boundary turns it into the stop.
"""

from __future__ import annotations

import argparse
import collections
import dataclasses
import difflib
import re
from pathlib import Path
from typing import Callable

__all__ = ["CrEditionDiffContext", "RULE_LINE", "RuleParseError", "build_parser",
           "cosmetic", "parse_rules", "run", "sort_key"]

# A rule line in the normalized shape: `205.2a <text>` or `205.2. <text>`.
# Two-letter subrules are real as of the 2026-08-07 edition (704.5aa).
RULE_LINE = re.compile(r"^(\d{3}\.\d+[a-z]{0,2})(?:\.)?\s+(\S.*)$")


class RuleParseError(RuntimeError):
    """The rule pattern produced a collision or no rules at all."""


def parse_rules(text: str) -> dict:
    """{rule number -> text} for one normalized edition.

    Refuses a duplicate number rather than letting a later line silently win:
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
            raise RuleParseError(
                f"rule {num} parsed twice with different text (line {n}). "
                f"RULE_LINE is matching something that is not a rule; fix "
                f"the pattern rather than dropping the collision.\n"
                f"  first: {out[num][:100]!r}\n  again: {body[:100]!r}")
        out[num] = body
    if not out:
        raise RuleParseError("parsed zero rules from a normalized CR — the loader or this "
                             "pattern is broken. Never report that as 'no differences'.")
    return out


def sort_key(num: str):
    m = re.match(r"^(\d{3})\.(\d+)([a-z]{0,2})$", num)
    return (int(m.group(1)), int(m.group(2)), m.group(3))


def cosmetic(a: str, b: str) -> bool:
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


@dataclasses.dataclass(frozen=True)
class CrEditionDiffContext:
    cr_path: Path
    prior_cr_path: Path
    prior_exists: Callable[[], bool]
    text: Callable[[Path], str]
    effective_date: Callable[[str], str]
    parse_rules: Callable[[str], dict]
    guard_rule_pattern: Callable[[], None]
    stop: Callable[[str], None]


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    ap.add_argument("--changed", action="store_true",
                    help="print the full text of every changed rule")
    ap.add_argument("--area", metavar="NNN",
                    help="restrict every listing to one CR rule area, e.g. 106")
    return ap


def run(argv, ctx: CrEditionDiffContext) -> int:
    args = build_parser().parse_args(argv)

    ctx.guard_rule_pattern()

    if not ctx.prior_exists():
        ctx.stop(f"the prior edition is not at {ctx.prior_cr_path}, so the new "
                 f"file cannot be verified as a COMPARISON. Refusing to report "
                 f"a fidelity result without one.")

    new_txt, old_txt = ctx.text(ctx.cr_path), ctx.text(ctx.prior_cr_path)
    new, old = ctx.parse_rules(new_txt), ctx.parse_rules(old_txt)

    added = sorted(set(new) - set(old), key=sort_key)
    removed = sorted(set(old) - set(new), key=sort_key)
    shared = sorted(set(new) & set(old), key=sort_key)
    identical = [n for n in shared if new[n] == old[n]]
    cosmetic_ = [n for n in shared if new[n] != old[n] and cosmetic(old[n], new[n])]
    reworded = [n for n in shared if new[n] != old[n] and not cosmetic(old[n], new[n])]

    def keep(nums):
        if not args.area:
            return nums
        return [n for n in nums if n.startswith(args.area + ".")]

    print("=" * 78)
    print("CR EDITION DIFF — rule by rule, both editions read through the "
          "normalizing loader")
    print("=" * 78)
    print(f"  new    {ctx.effective_date(new_txt):>16s}   {len(new):5d} rules   "
          f"{ctx.cr_path.name}")
    print(f"  prior  {ctx.effective_date(old_txt):>16s}   {len(old):5d} rules   "
          f"{ctx.prior_cr_path.name}")
    print()
    print(f"  BYTE-IDENTICAL across editions      {len(identical):5d}   "
          f"({100.0 * len(identical) / len(shared):.1f}% of shared)")
    print(f"  differ in whitespace/quotes only    {len(cosmetic_):5d}   "
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

    if cosmetic_:
        print("\n" + "=" * 78)
        print(f"⚠ {len(cosmetic_)} RULE(S) DIFFER ONLY IN WHITESPACE OR QUOTE "
              f"CHARACTERS")
        print("These are the signature of a reformatting touching content. "
              "Read them.")
        print("=" * 78)
        for num in keep(cosmetic_):
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
