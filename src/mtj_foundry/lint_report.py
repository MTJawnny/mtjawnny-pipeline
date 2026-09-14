"""Codebook lint report — the operator presentation of the standing lint.

## What this is

The text `lint` prints when the codebook is clean: one summary line, then two
lines per declared invariant exemption that the lint actually applied. S13 moved
that presentation here from the legacy `foundry_codebook` shell, whose `lint`
subcommand is a Gate 2 row. The lines are the shell's, character for character.

## What this is NOT

* **Not the lint.** `mtj_foundry.codebook.lint` decides validity and returns the
  statistics; this module only renders statistics it is handed.
* **Not a reader or a process boundary.** Loading the codebook, the `/1` schema
  guidance, `STOP — …` and the exit code stay in the shell. Nothing here opens a
  file, prints, exits or knows where the repository is.
"""

from __future__ import annotations

from mtj_foundry import codebook

__all__ = ["lines"]


def lines(path, stats: dict) -> list:
    """The clean-lint report for `stats` from `codebook.lint(document, ...)`.

    `path` is only a label; it is rendered with `str()` exactly as the shell's
    f-string did. The exemption text is read from the codebook model at call
    time, so a ruling recorded there is what gets printed.
    """
    out = [f"lint clean: {stats['axes']} axes, {stats['members']} members, "
           f"{stats['assertions']} assertions — {path}"]
    for key in stats["exemptions_applied"]:
        out.append(f"  DECLARED EXEMPTION APPLIED — {key[0]}: {key[1]}")
        out.append(f"    {codebook.AXIS_INVARIANT_EXEMPTIONS[key]}")
    return out
