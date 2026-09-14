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
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
# S9: `foundry_probe` is test-owned at `tests/guards/probe/`. The bare-name
# import below is unchanged -- the idiom CLAUDE.md records -- so what moved
# is the directory this bootstrap names.
_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "tests" / "guards" / "probe"))
import foundry_common as fc     # noqa: E402
import foundry_cr as cr         # noqa: E402
import foundry_probe as p       # noqa: E402

# S13: the rule parse, the comparison, the report and the CLI are
# `mtj_foundry.cr_edition_diff_report`'s. This shell keeps the rule-pattern
# capture guard (its fixture and the test-owned probe), the halting CR readers,
# the prior-edition location and the historic STOP, and hands them over.
from mtj_foundry import cr_edition_diff_report as _diff  # noqa: E402

RULE_LINE = _diff.RULE_LINE

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
    """{rule number -> text}, with the historic STOP on a refused parse."""
    try:
        return _diff.parse_rules(text)
    except _diff.RuleParseError as exc:
        fc.halt(str(exc))


_sort_key = _diff.sort_key
_cosmetic = _diff.cosmetic


def _context():
    return _diff.CrEditionDiffContext(
        cr_path=cr.CR_PATH,
        prior_cr_path=cr.PRIOR_CR_PATH,
        prior_exists=lambda: cr.PRIOR_CR_PATH.exists(),
        text=lambda path: cr.text(path),
        effective_date=lambda txt: cr.effective_date(txt),
        parse_rules=lambda text: parse_rules(text),
        guard_rule_pattern=lambda: p.must_capture(RULE_LINE.match, _RULE_LINE_CASES,
                                                  name="RULE_LINE"),
        stop=lambda message: fc.halt(message),
    )


def main() -> int:
    return _diff.run(None, _context())


if __name__ == "__main__":
    sys.exit(main())
