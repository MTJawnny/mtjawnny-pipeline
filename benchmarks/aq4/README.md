# AQ4 — frozen benchmark evidence (PAUSED)

**AQ4 is PAUSED.** Current task authority is GitHub Issue #1: latest `K` -> active `T`.
Nothing in this directory authorizes work.

## What this directory is

Frozen, tracked research/benchmark evidence. It is the home named by the layout
owner, `mtj_foundry.paths.ProjectPaths.benchmarks_aq4`.

S14 moved the AQ4 payload here verbatim from its former live locations
(`experiments/aq4_benchmark/`, `experiments/foundry_aq4_probes.py`, the historical
contract under `archive/routing/docs/`, and six AQ4 source/review/incident papers
from top-level `docs/`). Every moved file is byte-identical to its source at the
accepted head recorded in `FREEZE-MANIFEST.json`, which lists each source path,
destination path, SHA-256 and byte size.

## What it is not

- **Not production code.** The frozen Python under `experiments/` here must not be
  imported or executed as a current implementation, and nothing in
  `src/mtj_foundry` may depend on it.
- **Not a repair target.** Old imports, `sys.path` assumptions and references to
  former paths inside the payload are historical evidence. They are preserved as
  they were and are intentionally not modernized.
- **Not a ratification.** This relocation does not ratify, amend, withdraw or
  resume any AQ4 semantics, benchmark commitment or governance decision. The
  manifest records exact bytes and topology only; it makes no claim about
  benchmark correctness.

## Frozen absences

`cohorts/cohort-4.json` and `cohorts/cohort-5.json` do not exist, and their absence
is part of the frozen state. Do not create them or placeholders for them.

## Resuming AQ4

Any future AQ4 work requires its own separate durable authorization through
Issue #1. This README and the freeze manifest grant none.
