# S15.R1 — current-head closure readiness

Measured at accepted implementation head
`9b7203d337c6685563ff45a76ef51432dd8c2f0c`.
Compared against accepted evidence `adbe6197a92711cfab5bb5e98fdd6e98c330f006`,
which was itself measured at `49fcb292e0668b70901118c52dedc0ffd00f389f`.
That package is absent from the implementation tree; the absence is lineage, not
drift, and it was read through Git objects in a detached read-only worktree.

**The Worker does not have authority to declare S15 closed.** What follows is
evidence.

## The answer

**There is S15 work left, but almost none of it is implementation.**

Exactly **one** executable slice was found, and it is one nobody had recorded:
the tracked ruling registry is stale at this head. Everything else outstanding
is a decision that belongs to the Captain or Manager, or a surface that should
permanently remain.

## What S15 actually completed

Four archive slices, each re-proven here from Git objects rather than quoted
from its `X`:

| family | members | blob-identical to its accepted head | live path resurrected | prior-art family |
|---|---:|---|---|---|
| `archive/research/batch8` | 3 | yes | no | registered |
| `archive/research/mutations` | 2 | yes | no | registered |
| `archive/research/triage` | 13 | yes | no | registered |
| `archive/research/codebook-transforms` | 7 | yes | no | registered |

The `/1 -> /2` owner is still exactly the closed schema-migration pair; no
codebook transform was folded into it; the CDR-09 derivation and walk are still
together.

The prior-art reader has **exactly four** explicit historical families with
distinct labels and no recursive `archive/research/**` scan. All four conserve
under real content-derived queries:

| family | query | live | historical | strict | label |
|---|---|---:|---:|---:|---|
| triage | `resolve removed members` | 0 | 7 | 1 | archived triage set |
| batch8 | `agreement matrix` | 0 | 1 | 1 | archived Batch-8 research set |
| mutations | `replay attribution` | 0 | 1 | 1 | archived foundry-codebook/1 -> /2 migration pair |
| codebook-transforms | `strip locality` | 0 | 1 | 1 | archived codebook-transforms set |

No query was derived from a filename.

## The one executable slice found

`docs/RATIFIED-RULINGS-REGISTRY.md` is **stale**:

- committed: 142 documents / 684 references
- regenerated at this head: 138 documents / 660 references
- it still lists two AQ4 addenda that now live under `benchmarks/aq4/docs/`
- it **omits** `docs/ACTIVATED-REGENERATE-SELF-DET-LAW.md`, the sole home for
  `R8.3`, which is deletion-**BLOCKED**

Gate 2's `ruling_registry` row runs `--check-only` and compares pinned metrics
(127 / 86 / 41). Those are unchanged, so it exits `0` and the stale table is
never compared. A deletion-blocked document is missing from the artifact that
records deletion-blocking.

The 142 → 138 drop is fully explained: it is the accepted AQ4 truth-home
relocation. This is residue of accepted S15 work, not a new defect elsewhere.

## What must remain

- `benchmarks/aq4/**` — 30 tracked frozen files with a freeze manifest. Protected
  frozen evidence, never an S15 disposal candidate. AQ4 stays PAUSED.
- the four archive owners — `ARCHIVE_PRESERVE`.
- `src/mtj_foundry/**` — 55 modules, the permanent successor package.
- `experiments/foundry_common.py` — `COMPATIBILITY_SHELL_KEEP`, with **63** live
  tracked callers measured independently (experiments 40, tests 17,
  benchmarks 6), not read off the D5 sidecar.
- ignored runtime under `experiments/out/**` and `data/**` — `GENERATED_RUNTIME`.

## What is still blocked or undecided

`DELETE_SAFE` is **0**. No candidate meets the eight-part burden.

- **B01/B03** — the shell has 63 live callers; a permanent successor existing is
  not retirement.
- **B02/B08/B11** — the selected codebook lives only in ignored runtime. The
  pristine probe is decisive: Gate 2 **16 run / 3 pass / 13 unexpected failures**,
  and the broad suite **aborted** on a missing-corpus STOP without completing.
- **B09 / N10** — the registry above.
- **B10** — `tier_engine.py`, `emit_viewer.py`, `serve_viewer.py`, `viewer.html`
  are all still tracked and live.
- **N03** — re-derived edge by edge. The `/1` migration edge is genuinely
  discharged by D6; the CR route, the Gate 2 `lint` argv, `run1_apply` →
  `foundry_wire_experiment`, the tier_engine diagnostics and the reconcile
  refusal all remain current. Partial discharge is not clearance.
- **N05** — exactly three ignored AQ4 governance artifacts, still no tracked home.
- **N06** — all seven previously listed sole-home documents remain blocked, and
  six more joined them: **13** deletion-blocked documents, 41 sole-home rulings.
  The set grew.
- **N07** — all seven files remain with live tracked consumers.
- **N08** — 172 recovery rows (was 169), zero tracked successor owners.
- **N09** — all four route edges unresolved; no authority after the accepted
  checkpoint reclassified them, so none may be converted to historical.

## Validation at this head

| | operational worktree | pristine worktree |
|---|---|---|
| `tests/refoundation` | 1977 tests, 12 failures, 0 errors, 0 skips | **aborted**, no test count |
| failing IDs | the inherited `test_layout_delegation` twelve | n/a |
| Gate 2 | 16 run / 15 pass / 1 known / **0 unexpected**, exit 0 | 16 run / 3 pass / **13 unexpected** |
| W6 | 21 green | not reached |

Operational identity anchors all verified, none forced: codebook
`6aa6193f…` / 5,066,147 bytes / `foundry-codebook/2`, matching the tracked
selector; corpus container `2be88ba8…`; decompressed `5e47e132…`.

## Closure readiness

```yaml
closure_readiness:
  remaining_executable_s15_slices:
    - regenerate the stale tracked ruling registry (N10)
  remaining_decision_required:
    - N05 ignored AQ4 governance artifacts have no home
    - N06 thirteen deletion-blocked sole-home documents
    - N07 seven tracked legacy files with no accepted destination
    - N08 172 recovery rows with no successor owner or retention rule
    - N09 four unresolved route edges
    - N03 current law/operator routes through legacy paths
  remaining_live_consumer_blockers:
    - B01/B03 foundry_common shell, 63 live callers
    - B10 tier_engine / viewer / differential peer
  remaining_truth_home_blockers:
    - B09/N10 stale tracked ruling registry
    - N04 tracked file matching an ignore rule
  remaining_runtime_owner_blockers:
    - B02 codebook store / runtime ownership
    - B08 .gitignore and var/** ownership
    - B11 pristine-checkout dependence on ignored state
  remaining_unknowns:
    - N09 four route edges
    - var/** named but absent
  work_that_belongs_outside_s15:
    - AQ4 resumption (PAUSED by standing control)
    - N01 failure-observability repair (behaviour change, not topology)
    - full retirement of the foundry_common shell (a migration programme)
  manager_closure_review_eligible: false
```

`manager_closure_review_eligible` is **false** for one sufficient reason: an
unselected executable S15 slice remains (N10). The smallest truthful next step is
to regenerate the tracked ruling registry, or for the Manager to rule that it
belongs outside S15.

No unknown was converted to historical to reach this conclusion.
