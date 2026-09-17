# NOT AUTHORIZED

**This document issues nothing.** It is a drafted option for the Manager to
review from the accepted head. No task is selected by it, and the Worker did not
execute it.

Measured at `9b7203d337c6685563ff45a76ef51432dd8c2f0c`.

## The smallest truthful next step

Fresh measurement found exactly one **executable** S15 slice — everything else
remaining is a decision, not an implementation.

### Draft slice — regenerate the stale tracked ruling registry

**Why it is executable rather than a decision.** It needs no new ruling: the
generator already exists, is already a Gate 2 row, and its correct output is
fully determined by the current document tree. The committed artifact simply
has not been regenerated since the accepted AQ4 relocation and the R8.3 /
AG-CLI-01 law extraction.

**Why it is truth, not tidying.** `docs/ACTIVATED-REGENERATE-SELF-DET-LAW.md` is
the sole home for ruling `R8.3` and is deletion-BLOCKED, yet it does not appear
in the registry that records which documents are deletion-blocked. The registry
also still lists two documents that have moved to `benchmarks/aq4/docs/`.

**Proposed bounded allowlist (2 tracked paths):**

- `docs/RATIFIED-RULINGS-REGISTRY.md` — regenerated, not hand-edited
- `tests/guards/gate2/foundry_ruling_registry.py` — only if a conservation check
  over the document table is added; if not, this path is not needed

**Proposed proof obligations:** regenerate twice and require byte-identical
output; show the committed artifact differs before and matches after; show
`ACTIVATED-REGENERATE-SELF-DET-LAW.md` present with `R8.3` and marked blocked;
show the two relocated AQ4 addenda absent; show the pinned metrics 127/86/41
unchanged; Gate 2 and the broad suite conserved.

**Negative controls it would owe:** delete the sole-home doc and require red;
add a synthetic sole-home ruling and require red; hand-edit the table instead of
regenerating and require the ×2 determinism check to fail.

## What is NOT drafted as a slice, and why

| item | why it is not an implementation task |
|---|---|
| N05, N06, N07, N08, N09 | each needs a Captain/Manager ruling first; acting would convert an unknown into a disposition without authority |
| B01/B03 shell retirement | 63 live callers; retirement is a migration programme, not an S15 cleanup slice |
| B02/B08/B11 runtime ownership | needs a ruling on where runtime lives before anything moves |
| N01 failure observability | a real defect, but repairing it changes behaviour, not S15 topology |
| AQ4 | PAUSED by standing control |
