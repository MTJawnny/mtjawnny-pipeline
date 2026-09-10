#!/usr/bin/env python3
"""THE ONE PLACE THAT KNOWS HOW A COMPREHENSIVE RULES FILE IS FORMATTED.

WHY THIS EXISTS
---------------
The 2026-08-07 CR edition is not a drop-in replacement for the vendored
2026-06-19 one. Same content, different markup:

    2026-08-07:  **205.2a.** The card types are artifact, battle, …
    2026-06-19:  205.2a The card types are artifact, battle, …

Every CR parser in this repo keys on the plain shape (`load_702`,
`type_vocabulary`, CR 113.3 / 120.1 / 205 / 207.2c / 400.1 / 701 / 702), so a
file copy makes those enumerations return empty or partial. The halt-guards
would fire — that is them working — but the fix is not a file copy.

Ratified 2026-08-09: **NORMALIZE AT READ TIME, NEVER TRANSLATE THE FILE.**
Translating the CR is transcribing it, which CLAUDE.md forbids outright, and a
translated file would need its own conservation audit forever after. So the new
file stays pristine, and this module hands every parser the shape it already
expects. One definition of "CR formatting", one place to fix it.

WHY THE BOLD FORM IS THE BETTER SOURCE, and is therefore kept
------------------------------------------------------------
`**605.1a.**` at line start is an UNAMBIGUOUS rule marker. In the plain form a
parser cannot tell `605.1a` opening a line from `605.1a` cited mid-sentence
without extra context. The ambiguity stays out of the file; the stripping lives
here.

THE CONSERVATION LAW — every transformation is a PURE DELETION
--------------------------------------------------------------
CLAUDE.md, from the 2026-08-04 hyphen disaster: *"A CENSUS CANNOT ANSWER 'did
anything get LOST' — conservation can."* Every rule below deletes markup
characters and never substitutes, reorders or inserts:

    **205.2a.** The …   ->   205.2a The …      deleted: * * . * *
    **205.2.** Card …   ->   205.2. Card …     deleted: * * * *
    > **Example:** …    ->   Example: …        deleted: > ␠ * * * *
    ### 100. General    ->   ## 100. General   deleted: #

So the law this module asserts on EVERY line is that the normalized line is a
subsequence of the raw line whose only deleted characters come from the markup
set. That is strong enough to catch the greedy-regex class of
damage, which a reassembly check cannot see, and it is
asserted per line rather than per file so a single damaged line halts the run.
(The damage it is aimed at: a greedy span regex eating everything between the
first and last delimiter on a line, which a reassembly check cannot see because
kept + removed still reassembles perfectly.)

The content guard is separate and asserts CONTENT, not cardinality — the CR 205
Oxford-comma lesson, where `len() >= 15` stayed green while the last member of
every list was destroyed.

USAGE
    import foundry_cr
    txt = foundry_cr.text()             # normalized, cached
    foundry_cr.effective_date(txt)      # "August 7, 2026"

    python3 experiments/foundry_cr.py             # report + self-test
    python3 experiments/foundry_cr.py --selftest  # guards only
"""
import re
import sys
import argparse
import collections
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402

# ---------------------------------------------------------------------------
# S6 — THIS FILE IS NOW A SHELL OVER THE PERMANENT CR SUBSTRATE
# ---------------------------------------------------------------------------
# Migration slice 6 moved every reusable CR semantic into
# `mtj_foundry.mtg.cr.edition`: edition selection and `MTJ_CR_PATH`, the markup
# vocabulary and required anchors, the declared encoding-damage register, the
# pure-deletion law, encoding detection and repair, the parseability assertions,
# and the read/cache API. NO SECOND IMPLEMENTATION REMAINS HERE.
#
# What stays is the operator half the permanent layer must not own: `--report`,
# the CLI, and the `_CASES` negative-control fixtures with `_selftest`.
#
# THE HALT BOUNDARY IS RE-ESTABLISHED HERE, NOT IMPORTED UPWARD. A library may
# not exit a process it does not own, so the permanent module raises `CRError`
# and every wrapper below converts it to the historic `fc.halt` -- same message,
# same `STOP — …`, same exit status. Legacy callers and `_selftest`, which
# catches `SystemExit`, therefore see exactly the behaviour they saw before.
from mtj_foundry.mtg.cr import edition as _edition  # noqa: E402

CRError = _edition.CRError

# The path facts are the permanent owner's. Re-exported, never re-derived.
CR_PATH = _edition.CR_PATH
PRIOR_CR_PATH = _edition.PRIOR_CR_PATH

# Markup/register constants consumed by `_report` and `_selftest` below.
_KNOWN_ENCODING_DAMAGE = _edition._KNOWN_ENCODING_DAMAGE
_MOJIBAKE = _edition._MOJIBAKE
_REQUIRED_ANCHORS = _edition._REQUIRED_ANCHORS
_MARKUP_CHARS = _edition._MARKUP_CHARS
_cache = _edition._cache

# Pure derivations: no process boundary, so they alias directly.
_pure_deletion = _edition._pure_deletion
_demojibake = _edition._demojibake


def _halting(fn):
    """Wrap a permanent CR entry point in the legacy process boundary."""
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except _edition.CRError as exc:
            fc.halt(str(exc))
    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    return wrapper


normalize_line = _halting(_edition.normalize_line)
normalize = _halting(_edition.normalize)
_assert_encoding = _halting(_edition._assert_encoding)
_repair_encoding = _halting(_edition._repair_encoding)
_assert_parseable = _halting(_edition._assert_parseable)
text = _halting(_edition.text)
lines = _halting(_edition.lines)
effective_date = _halting(_edition.effective_date)



# ---------------------------------------------------------------------------
# SELF-TEST — a guard that has never been shown to fail is not known to be a
# guard (CLAUDE.md, 2026-08-09). Each case below is a NEGATIVE control aimed at
# the code path, not at the module's name.
# ---------------------------------------------------------------------------
_CASES = [
    # (label, raw, expected-or-None-if-must-halt)
    ("bold subrule drops its period",
     "**205.2a.** The card types are artifact, battle, and vanguard.",
     "205.2a The card types are artifact, battle, and vanguard."),
    ("bold numbered rule KEEPS its period",
     "**702.6.** Equip", "702.6. Equip"),
    ("two-letter subrule",
     "**704.5aa.** If a player controls a permanent",
     "704.5aa If a player controls a permanent"),
    ("plain line is untouched (the prior edition still loads)",
     "205.2a The card types are artifact.",
     "205.2a The card types are artifact."),
    ("blockquoted example becomes a plain Example: line",
     "> **Example:** Lost Order of Jarkeld has power 1+*.",
     "Example: Lost Order of Jarkeld has power 1+*."),
    ("heading dedents one level",
     "### 702. Keyword Abilities", "## 702. Keyword Abilities"),
    ("top-level heading is left alone",
     "# Magic: The Gathering Comprehensive Rules",
     "# Magic: The Gathering Comprehensive Rules"),
    ("navigation label loses only its wrapper",
     "**These rules are effective as of August 7, 2026.**",
     "These rules are effective as of August 7, 2026."),
    # CR 208.2 prints a literal asterisk. A blanket `\*\*` strip would survive
    # this line by luck; the test pins that it must not be attempted.
    ("a LITERAL CR asterisk survives",
     "**208.2.** Some creature cards have power and/or toughness of */*.",
     "208.2. Some creature cards have power and/or toughness of */*."),
    ("a rule number cited MID-SENTENCE is not a marker",
     "See rule 605.1a for mana abilities.",
     "See rule 605.1a for mana abilities."),
]


def _selftest() -> int:
    bad = 0
    for label, raw, want in _CASES:
        got = normalize_line(raw)
        ok = got == want and _pure_deletion(raw, got)
        print(f"  [{'ok' if ok else 'FAIL'}] {label}")
        if not ok:
            bad += 1
            print(f"        raw  {raw!r}\n        want {want!r}\n        got  {got!r}")

    # Guard D — the conservation law must REJECT a deliberately broken
    # normalizer. Without this the law is decoration.
    broken = [("substitution", "205.2a x", "205.2a y"),
              ("insertion", "205.2a x", "205.2a xy"),
              ("greedy span eaten", "205.2a (see 300) x", "205.2a x"),
              ("reordering", "205.2a ab", "205.2a ba")]
    for label, raw, fake in broken:
        if _pure_deletion(raw, fake):
            print(f"  [FAIL] conservation accepted a {label}")
            bad += 1
        else:
            print(f"  [ok] conservation rejects a {label}")

    # And it must ACCEPT a legitimate markup deletion, or it is merely strict.
    if not _pure_deletion("**205.2a.** x", "205.2a x"):
        print("  [FAIL] conservation rejects a legitimate markup deletion")
        bad += 1
    else:
        print("  [ok] conservation accepts a legitimate markup deletion")

    # The encoding guard, aimed at the CODE PATH rather than at the tool's
    # name: three of eight negative controls on 2026-08-09 were mis-aimed and
    # each first read as "this gate is broken".
    def halts(text):
        try:
            _assert_encoding(text, Path("<selftest>"))
            return False
        except SystemExit:
            return True

    declared = next(iter(_KNOWN_ENCODING_DAMAGE))
    checks = [
        ("encoding guard fires on an UNDECLARED corrupted rule",
         "702.6a Equip is an activated ability of JuzÃ¡m cards.", True),
        (f"encoding guard stays quiet on the declared rule ({declared})",
         f"{declared} Those names are DandÃ¢n, JuzÃ¡m Djinn.", False),
        ("encoding guard stays quiet on correct accented text",
         "206.3a Those names are Dandân, Juzám Djinn, Ring of Ma’rûf.", False),
        ("encoding guard stays quiet on the curly apostrophe alone",
         "205.3i The land types are Urza’s, Desert.", False),
    ]
    for label, line, want_halt in checks:
        got = halts(line)
        if got == want_halt:
            print(f"  [ok] {label}")
        else:
            print(f"  [FAIL] {label} (halted={got}, wanted {want_halt})")
            bad += 1

    # THE REPAIR (D-CR-1b). Every case is aimed at the code path, not at the
    # feature's name — the three mis-aimed negative controls of 2026-08-09 each
    # first read as "this gate is broken".
    if _demojibake("JuzÃ¡m Djinn") == "Juzám Djinn":
        print("  [ok] repair is DERIVED from the damage, not typed")
    else:
        print("  [FAIL] repair derivation is wrong")
        bad += 1

    def repairs(text_in):
        try:
            return _repair_encoding(text_in, PRIOR_CR_PATH)   # skips assert 2
        except SystemExit:
            return "<HALTED>"

    rule = declared
    repair_cases = [
        ("declared damage is repaired",
         f"{rule} Those names are DandÃ¢n, GhazbÃ¡n Ogre, JuzÃ¡m Djinn, "
         f"KhabÃ¡l Ghoul, JunÃºn Efreet, Ring of Ma’rÃ»f, El-HajjÃ¢j.",
         f"{rule} Those names are Dandân, Ghazbán Ogre, Juzám Djinn, "
         f"Khabál Ghoul, Junún Efreet, Ring of Ma’rûf, El-Hajjâj."),
        # A count that does not match the register means the damage MOVED.
        # Widening the repair to fit is how a register stops being evidence.
        ("a DIFFERENT amount of damage halts rather than being absorbed",
         f"{rule} Those names are DandÃ¢n and JuzÃ¡m Djinn.", "<HALTED>"),
        # Clean text must survive the pass untouched, or the repair is a
        # rewrite wearing a repair's name.
        ("already-correct text passes through unchanged",
         f"{rule} Those names are Dandân, Juzám Djinn.",
         f"{rule} Those names are Dandân, Juzám Djinn."),
    ]
    for label, src, want in repair_cases:
        got = repairs(src)
        if got == want:
            print(f"  [ok] {label}")
        else:
            print(f"  [FAIL] {label}\n        got  {got!r}\n        want {want!r}")
            bad += 1
    return bad


def _report() -> None:
    txt = text()
    ls = txt.splitlines()
    raw = CR_PATH.read_text(encoding="utf-8", errors="strict").splitlines()
    rule_rx = re.compile(r"^\d{3}\.\d+[a-z]{0,2}[\s.]")
    print(f"CR file            {CR_PATH}")
    print(f"effective          {effective_date(txt)}")
    print(f"lines              {len(ls)}")
    print(f"rule-numbered      {sum(1 for l in ls if rule_rx.match(l))}")
    print(f"lines normalized   {sum(1 for a, b in zip(raw, ls) if a != b)}")
    print(f"curly apostrophes  {txt.count(chr(0x2019))}")
    print(f"mojibake remaining {len(_MOJIBAKE.findall(txt))}")
    print("\nDECLARED ENCODING DAMAGE, repaired at read time (D-CR-1b, Captain "
          "2026-08-09).\nAnything outside this register HALTS.")
    for rule, decl in sorted(_KNOWN_ENCODING_DAMAGE.items()):
        fixes = "  ".join(f"{c!r}->{f!r}×{n}"
                          for c, (f, n) in sorted(decl["repairs"].items()))
        print(f"  CR {rule}   {fixes}\n    {decl['why']}")
    if PRIOR_CR_PATH.exists():
        print("    verified byte-identical to the 2026-06-19 edition after "
              "repair.")
    else:
        print("    ⚠ the 2026-06-19 edition is not on this machine, so the "
              "repair was checked\n      against its pinned fixture ONLY — the "
              "positive-correctness half did\n      not run. Stated, not "
              "silently skipped.")
    print("\nanchors required by the parsers, all present:")
    for a, why in _REQUIRED_ANCHORS:
        print(f"  {a!r:44s} {why}")
    if PRIOR_CR_PATH.exists():
        prior = text(PRIOR_CR_PATH)
        print(f"\nprior edition      {effective_date(prior)}  ({PRIOR_CR_PATH})")
        print(f"  rule-numbered    "
              f"{sum(1 for l in prior.splitlines() if rule_rx.match(l))}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true",
                    help="run the guards only")
    args = ap.parse_args()
    if not args.selftest:
        _report()
        print()
    print("SELF-TEST — every guard shown to both pass and fail.")
    print("Each negative control prints its guard's real STOP message to "
          "stderr. Those\nare the controls WORKING; the verdict is the "
          "[ok]/[FAIL] column below.")
    bad = _selftest()
    if bad:
        print(f"\n{bad} self-test failure(s)")
        return 1
    print("\nall guards behaved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
