"""CR edition report — the operator view of the selected Comprehensive Rules edition.

## What this is

The report and CLI that S6 left in the legacy `foundry_cr` shell: which edition
is selected, its effective date, how many lines normalization touched, the
declared encoding-damage register and its repairs, the anchors the parsers
require, and the prior edition used for comparison. S13 moved it here. Every
line is the shell's, character for character, and lines are produced LAZILY so
a refusal part-way through still follows the lines printed before it.

## What this is NOT

* **Not CR semantics.** Edition selection, normalization, encoding repair, the
  anchor list and the effective date are `mtj_foundry.mtg.cr.edition`. This
  module renders what they return.
* **Not a reader or a process boundary.** The CR text, the raw file lines, the
  prior edition and whether it exists all arrive as callables from the
  composition boundary, which also owns the historic `STOP — …` those readers
  raise. Nothing here opens a file, derives a root or exits.
"""

from __future__ import annotations

import argparse
import dataclasses
import re
from pathlib import Path
from typing import Callable

from mtj_foundry.mtg.cr import edition as _edition

__all__ = ["CrReportContext", "build_parser", "report_lines", "run"]

_RULE_NUMBERED = re.compile(r"^\d{3}\.\d+[a-z]{0,2}[\s.]")


@dataclasses.dataclass(frozen=True)
class CrReportContext:
    cr_path: Path
    prior_cr_path: Path
    text: Callable[..., str]
    effective_date: Callable[[str], str]
    raw_lines: Callable[[], list]
    prior_exists: Callable[[], bool]


def report_lines(ctx: CrReportContext):
    """The edition report, one printed line at a time."""
    txt = ctx.text()
    ls = txt.splitlines()
    raw = ctx.raw_lines()
    yield f"CR file            {ctx.cr_path}"
    yield f"effective          {ctx.effective_date(txt)}"
    yield f"lines              {len(ls)}"
    yield f"rule-numbered      {sum(1 for l in ls if _RULE_NUMBERED.match(l))}"
    yield f"lines normalized   {sum(1 for a, b in zip(raw, ls) if a != b)}"
    yield f"curly apostrophes  {txt.count(chr(0x2019))}"
    yield f"mojibake remaining {len(_edition._MOJIBAKE.findall(txt))}"
    yield ("\nDECLARED ENCODING DAMAGE, repaired at read time (D-CR-1b, Captain "
           "2026-08-09).\nAnything outside this register HALTS.")
    for rule, decl in sorted(_edition._KNOWN_ENCODING_DAMAGE.items()):
        fixes = "  ".join(f"{c!r}->{f!r}×{n}"
                          for c, (f, n) in sorted(decl["repairs"].items()))
        yield f"  CR {rule}   {fixes}\n    {decl['why']}"
    if ctx.prior_exists():
        yield ("    verified byte-identical to the 2026-06-19 edition after "
               "repair.")
    else:
        yield ("    ⚠ the 2026-06-19 edition is not on this machine, so the "
               "repair was checked\n      against its pinned fixture ONLY — the "
               "positive-correctness half did\n      not run. Stated, not "
               "silently skipped.")
    yield "\nanchors required by the parsers, all present:"
    for a, why in _edition._REQUIRED_ANCHORS:
        yield f"  {a!r:44s} {why}"
    if ctx.prior_exists():
        prior = ctx.text(ctx.prior_cr_path)
        yield f"\nprior edition      {ctx.effective_date(prior)}  ({ctx.prior_cr_path})"
        yield (f"  rule-numbered    "
               f"{sum(1 for l in prior.splitlines() if _RULE_NUMBERED.match(l))}")


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        description="Report on the selected CR edition and its declared "
                    "encoding repairs.")


def run(argv, ctx: CrReportContext) -> int:
    build_parser().parse_args(argv)
    for line in report_lines(ctx):
        print(line)
    return 0
