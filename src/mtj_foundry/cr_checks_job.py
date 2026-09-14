"""CR-checks job — the determinism gate, the summary and the coverage report.

## What this is

The operator composition of the CR check-registry generator, moved by S13 out
of the legacy `foundry_cr_checks` shell. Its artifact, the tracked generated
registry `cr-checks.json`, is read at run time by the shape extractor that Gate 2
guards import, so the bytes this job gates are live.

* `gated_serialization` — serialize a built registry, rebuild it, and refuse
  unless both serializations are identical (the ×2 determinism gate);
* `summary` — the lines printed after the write;
* `coverage_lines` — the `--coverage` report text.

Wording, ordering and serialization are the shell's, character for character.

## What this is NOT

* **Not the registry or the coverage semantics.** The CR walk and every registry
  row are `mtj_foundry.mtg.cr.checks`; which slug tokens count and which keyword
  actions they leave uncovered are `mtj_foundry.codebook_coverage`. This module
  is handed their results.
* **Not a reader, writer, printer or process boundary.** The CR and codebook
  reads, the corpus load, the artifact write, printing, argument parsing and the
  `STOP — …` exit stay in the shell. A determinism failure RAISES
  `DeterminismError`; the shell turns it back into the historic stop.
"""

from __future__ import annotations

import json

__all__ = ["DeterminismError", "coverage_lines", "gated_serialization", "summary"]

# Keyword actions pressing at least this many gate-passing cards are listed.
_COVERAGE_LISTING_FLOOR = 20


class DeterminismError(RuntimeError):
    """Two builds of the registry serialized differently."""


def gated_serialization(registry: dict, rebuild) -> str:
    """The artifact text (without its trailing newline), or `DeterminismError`.

    `rebuild` is a zero-argument callable that builds the registry again from
    scratch. Only this exact comparison is caught: anything `rebuild` raises
    propagates unwrapped, because a failed build is not a determinism finding.
    """
    once = json.dumps(registry, indent=1, sort_keys=True)
    twice = json.dumps(rebuild(), indent=1, sort_keys=True)
    if once != twice:
        raise DeterminismError("determinism gate FAILED — two builds of the registry differ")
    return once


def summary(out_path, registry: dict) -> list:
    """The write confirmation and the per-kind term counts, sorted by kind."""
    out = [f"wrote {out_path}  ({registry['n_terms']} terms, determinism x2 OK)"]
    by = {}
    for row in registry["terms"]:
        by[row["kind"]] = by.get(row["kind"], 0) + 1
    for kind, count in sorted(by.items()):
        out.append(f"  {kind:16s} {count}")
    return out


def coverage_lines(n_actions: int, missing: list) -> list:
    """The `--coverage` report for `codebook_coverage`'s uncovered keyword actions.

    `missing` is `(corpus pressure, term, rule)` rows, in the owner's order.
    """
    out = [
        f"CR keyword actions        : {n_actions}",
        f"  modelled by some axis   : {n_actions - len(missing)}",
        f"  NO axis token           : {len(missing)}",
        "\n  uncovered, by corpus pressure (gate-passing cards printing the term):",
    ]
    for n, term, rule in missing:
        if n >= _COVERAGE_LISTING_FLOOR:
            out.append(f"     {n:5d}  {term:28s} CR {rule}")
    out += [
        "\n  NOTE: this matches the action's FIRST WORD against slug tokens, so a",
        "  morphological near-miss counts as uncovered (prevents-regeneration",
        "  carries 'regeneration', not 'regenerate'). Treat the list as a",
        "  worklist to verify, not a count to quote.",
    ]
    return out
