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

    python3 experiments/foundry_cr.py             # the edition report

The GUARD is no longer here. S9 moved the ten normalize cases and every
negative control to their test owner, which the refoundation suite runs:

    python3 tests/guards/cr/test_cr_edition.py
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
# What stayed was the operator half the permanent layer must not own:
# `--report`, the CLI, and the `_CASES` negative-control fixtures with
# `_selftest`.
#
# S9 took the guard out. R5's finding was that `_selftest` was ORPHANED -- no
# Gate-2 row, no test and no workflow ever ran it, so ten cases and four
# control families had never been shown to do anything. They now live at
# `tests/guards/cr/test_cr_edition.py`, which the standing refoundation suite
# executes, and NO COPY OF THEM REMAINS HERE. `_report`, the CLI and the
# `PRIOR_CR_PATH` operator presentation are still this shell's and are still a
# later slice's to move.
#
# THE HALT BOUNDARY IS RE-ESTABLISHED HERE, NOT IMPORTED UPWARD. A library may
# not exit a process it does not own, so the permanent module raises `CRError`
# and every wrapper below converts it to the historic `fc.halt` -- same message,
# same `STOP — …`, same exit status. Legacy callers and `_selftest`, which
# catches `SystemExit`, therefore see exactly the behaviour they saw before.
from mtj_foundry.mtg.cr import edition as _edition  # noqa: E402

CRError = _edition.CRError

# THIS SHELL IS THE COMPOSITION BOUNDARY, and that is the whole point of the
# S6.R1 repair. The permanent library derives no repository root: it contributes
# the edition FILENAME and the `MTJ_CR_PATH` rule, and RECEIVES the config-CR
# directory from the accepted layout owner through the compatibility boundary
# below. A library that manufactured that root would work only when read out of
# the source checkout, which is the defect this repair removes.
#
# The provider name is deliberately NOT spelled in this comment: the delegation
# census reconciles a raw TEXTUAL count against a scoped AST count, and prose
# naming the symbol would score documentation as a second delegation. Third
# recorded instance of "a document is an API" in this repository.
CR_PATH = _edition.select_cr_path(fc.CONFIG_CR)
PRIOR_CR_PATH = _edition.PRIOR_CR_PATH

# Markup/register constants consumed by `_report` below, and by the S9
# guard owner, which reaches them through this shell's halt boundary.
_KNOWN_ENCODING_DAMAGE = _edition._KNOWN_ENCODING_DAMAGE
_MOJIBAKE = _edition._MOJIBAKE
_REQUIRED_ANCHORS = _edition._REQUIRED_ANCHORS
_MARKUP_CHARS = _edition._MARKUP_CHARS
_cache = _edition._cache

# Pure derivations: no process boundary, so they alias directly.
_pure_deletion = _edition._pure_deletion
_demojibake = _edition._demojibake


def _halting(fn, default_path=False):
    """Wrap a permanent CR entry point in the legacy process boundary.

    `default_path` supplies THIS boundary's default edition when a legacy caller
    passes none. The permanent function has no default, by design -- it does not
    know where the repository is.
    """
    def wrapper(*args, **kwargs):
        if default_path and not args and "path" not in kwargs:
            args = (CR_PATH,)
        elif default_path and args and args[0] is None:
            args = (CR_PATH,) + args[1:]
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
text = _halting(_edition.text, default_path=True)
lines = _halting(_edition.lines, default_path=True)


def effective_date(txt: str = None) -> str:
    """The CR's effective date. Defaults to THIS boundary's edition."""
    try:
        return _edition.effective_date(txt if txt is not None else text())
    except _edition.CRError as exc:
        fc.halt(str(exc))


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
    ap = argparse.ArgumentParser(
        description="Report on the selected CR edition and its declared "
                    "encoding repairs.")
    ap.parse_args()
    _report()
    return 0


if __name__ == "__main__":
    sys.exit(main())
