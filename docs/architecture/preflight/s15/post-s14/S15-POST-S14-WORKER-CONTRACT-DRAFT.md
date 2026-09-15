# S15 Post-S14 Worker Contract — DRAFT

> # **NOT AUTHORIZED — DRAFT ONLY — NOT AN ACTIVE TASK**
>
> Generated from the S15.R0 readiness state measured at `49fcb292e0668b70901118c52dedc0ffd00f389f` and repaired by S15.R0.R2 (Issue #1 T `5683294052`). It authorizes nothing: no deletion, archive move, shell retirement, `.gitignore` edit, runtime cleanup, guard change, baseline succession, AQ4 action, merge, or successor work. Only a later Issue #1 `K` selecting a Manager-issued `T` can authorize any slice. This file contains no executable task.

## Why this is not a one-shot destructive S15

At the measured base:

- **8 of the 13 old blockers are `STILL_BLOCKED`**, and **9 new blockers** exist; **6** are `DECISION_REQUIRED` (N03, N05, N06, N07, N08, N09).
- **Tracked `DELETE_SAFE`: 0.** The only `DELETE_SAFE` item is one ignored local file, a qualified Worker-local measurement with negligible value.
- **46 of 48** `experiments/**` ARCHIVE_PRESERVE candidates carry a material edge from outside their co-move set or analyzer participation; **5** have a current operator/law route; **4** have an unresolved `UNKNOWN_BLOCK` route (`foundry_consolidate_run1_apply.py`, `foundry_consolidate_run1_enumerate.py`, `foundry_w3_census.py`, `family_tree_evidence.py`).
- Tracked archive/delete changes guarded propositions, not only topology:
  - D1 (47-file batch): raw `FAILED (failures=17, errors=8)` vs BASE `FAILED (failures=12)`; 4 new failing + 1 new erroring method (8 subtests); all 12 inherited-red methods changed values;
  - D2: Gate 2 red.

## Prerequisite model: per slice, not ordinal

The R0 draft ordered prerequisites P0→P9. That ordering is withdrawn as a model: it implied that every decision blocks every slice, that guard changes are mechanical, and that archiving before consumer detachment is generally safe. None of those is true at this base. Each slice below names only the prerequisites that apply to its own members.

**Prerequisite kinds** (each slice lists which apply):

| kind | meaning |
|---|---|
| `EDGE:ROUTE` | a current operator/law route into a member must be retargeted, retired or explicitly kept under authority (law text needs Captain ratification; an executable diagnostic is a source change together with its guard) |
| `EDGE:GUARD` | a source-inspection guard's proposition must be conserved value-identically (retarget to the archived location or a successor owner) or its retirement separately authorized |
| `EDGE:PIN` | a population pin / analyzer participation must be re-pinned with value-level identity reconciliation, or its retirement authorized |
| `EDGE:CONSUMER` | a behavioral consumer outside the slice must be detached/migrated first |
| `CO_MOVE` | same-destination importers/routes move in the same slice |
| `DECIDE:<id>` | a named Manager/Captain decision |
| `RESTORE` | verified restoration of the selected corpus container and selector-verified codebook (B11) — needed only by slices whose proof runs need that state in a pristine checkout |
| `IGNORE` | authorized `.gitignore` / `var/**` ownership (B08) — needed only by runtime relocation |

**Composition dependencies that stay coupled:** codebook authority, backup and restore compose. `mtj_foundry.authority_restore` refuses to replace a differing codebook without a caller-supplied backup policy, and `experiments/foundry_authority.py` injects `foundry_codebook.backup_codebook`. No slice may retire `foundry_codebook`, `foundry_authority`, or relocate `experiments/out/foundry/backups/**` independently of the others.

**Separate authority track:** ignored `experiments/out/aq4/**` evidence (N05) stays outside S15 while AQ4 is PAUSED. No S15 slice imports, executes or relocates frozen AQ4 material.

## Slice template (shape only)

```yaml
schema: mtj-task/1            # shape for a future Manager T; not a task
status: DRAFT_NOT_AUTHORIZED
base: <ACCEPTED_HEAD_AT_ISSUE>   # re-run the R2 edge census, analyzer participation and NC1-NC10 + NC-R2-1..6 at this base
allow: <EXACT_PATH_LIST_FROM_REGENERATED_MATRIX>
deny:
  - benchmarks/aq4/**            # PROTECTED frozen evidence; AQ4 PAUSED
  - any path not named in allow
required:
  - every material edge on every member discharged by its own prerequisite; no UNKNOWN_BLOCK edge
  - impact rig BEFORE commit with value-level failure identity; changes only where a guarded proposition is conserved or its retirement is authorized
  - Gate 2 row identity 16/15/1 + exact W6 (or an authorized registry succession for document slices)
  - R100 byte/blob manifest for archive moves; CO_MOVE sets move together
  - clean-checkout dependence not increased
stop:
  - base drift; any new or undischarged material edge; any guard change that is not a named conservation or authorized retirement
next: NONE
```

## Candidate slices and their own prerequisites

| slice | members at BASE | prerequisites that apply |
|---|---|---|
| **A-batch8** | `foundry_batch8_ab.py`, `foundry_batch8_canon_analysis.py`, `foundry_batch8_diff.py` → `archive/research/batch8/` | `CO_MOVE` (imports + `diff` halt route to `ab`); `EDGE:PIN` (s10 sidecar, layout census) |
| **A-triage** | `foundry_adapt_batch1..7_decisions.py`, `foundry_assemble_batch2..7.py` (13) → `archive/research/triage/` | `EDGE:PIN` (s10 sidecar, layout census); R1: confirm each batch's ratified record is present in `docs/` |
| **A-mutations** | `foundry_any_damage_split.py`, `cdr09_derive.py`, `cdr09_walk.py`, `axis_merge_pointer_correction.py`, `batch7_pay_life_scrub.py`, `gate0_scrub.py`, `locality_backfill.py` | `CO_MOVE` (cdr09 import + halt route); `EDGE:GUARD` (C8.5V fifteen record for 6 members); `EDGE:PIN` |
| **A-migration-pair** | `foundry_migrate_codebook_v2.py` (+ `foundry_verify_migration.py`, still `BLOCKED_LIVE_CONSUMER`) | `EDGE:ROUTE` + `DECIDE:N03` (live `/1` halt in `foundry_codebook.py`); `EDGE:GUARD` (C3 facade guidance pin, verifier-independence guard); `EDGE:CONSUMER` for the verifier; PAIR rule |
| **A-consolidation** | `foundry_consolidate_run1_apply.py`, `foundry_consolidate_run1_enumerate.py`, `foundry_corpus_pass_run1.py`, `foundry_corroboration_pass.py` | `DECIDE:N09` (D-APPLY resume route for apply + enumerate); `EDGE:GUARD` (C8.5V/C8.5X records; layout C8.5C source reads of apply); `EDGE:PIN` |
| **A-measure** | `experiments/measure/**` (9) → `archive/research/thesaurus-measurement/` | `CO_MOVE` (axis_foundry imports family_tree_evidence; memos carry reproduction commands); `DECIDE:N09` (parent-layer S7 route to family_tree_evidence); `EDGE:ROUTE` + `DECIDE:N03`, B10 (tier_engine report text cites PHASE-1/PHASE-3 memos); `EDGE:PIN` |
| **A-research** | `foundry_axis_walk.py`, `blanket_risk.py`, `reach_census.py`, `reaudit.py`, `selfother_scope.py`, `synonym_collision.py`, `w3_census.py`, `invert_tags.py` | per member: `EDGE:GUARD` (reaudit nomination record; reach_census name-free UNKNOWN-frontier dependency); `DECIDE:N09` (w3_census re-measure route); `EDGE:ROUTE` + `DECIDE:N03`, B10 (tier_engine halt → invert_tags); `EDGE:PIN` |
| **A-reports** | `POKE-PUNCH-LIST.md` → `archive/reports/` | `EDGE:ROUTE` + `DECIDE:N03`, B10 (tier_engine report text); R1 registry sweep |
| **A-engine** | `serve_viewer.py`, `viewer.html` (+ `tier_engine.py`, `emit_viewer.py` blocked) | B10 differential-oracle retirement; `CO_MOVE` (serve_viewer serves viewer.html; viewer.html routes to serve_viewer) |
| **P4 detach** | `foundry_prior_art`, `r5_attribution`, `slug_reparse`, `wire_capability`, `wire_experiment`, `reminder_conformance`, `stage1b`, `verify_migration`, `consolidate_run1{,_classify}`, `det_patterns_probe`, `snapshot` | `EDGE:CONSUMER` authority for the consuming guards (`load_legacy`) |
| **P5 shells** | `foundry_codebook`, `foundry_cr`, `foundry_cr702_classes`, `foundry_cr_checks`, `foundry_cr_edition_diff`, `foundry_keyword_buckets`, `foundry_det_pass`, `foundry_locality`, `foundry_object_lattice`, `foundry_shape_extractor`, `validate_slug`, `foundry_authority` | caller closure; `DECIDE:N03` (CLAUDE.md CR route, Gate-2 lint argv, AG-CLI-01 embodiment, `/1` and cr_checks diagnostics); B03 S12 control successor coverage; codebook/authority/backup composition |
| **P7** | `foundry_common.py` | B01 (88 pinned importers) |
| **P9 docs** | 29 stubs, 2 router pointers, 1 AQ4 pointer, 7 sole-home documents | B09 authorized succession; `DECIDE:N06`; archive bodies stay in place (live stub/tombstone/law/register pointers and blob guards) |
| **Runtime** | `experiments/out/**` → `var/**` by role | `IGNORE` (B08); `RESTORE` (B11); `DECIDE:N08` for recovery backups (codebook backups also under the composition dependency above); B07 for unknowns; N05 separate AQ4 track |
| **Decisions that block no slice by themselves** | N04 (tracked `claims.jsonl` matches `*.jsonl`) blocks only an ignore-rule change; N01 blocks only claims that a clean checkout reports honestly | — |
| **Never in S15** | `benchmarks/aq4/**`, `pipeline/**`, permanent sets | — |

## Frozen invariants every slice inherits

- AQ4 remains **PAUSED**. Frozen AQ4 code is never imported or executed.
- The frozen `/1` reconcile provenance is never resurrected as live implementation authority.
- AG-CLI-01 is behavior law, **not** permission to install or expose a mutating CLI.
- The `foundry_cr702_classes --unstated` KeyError is conserved debt, never a retirement-time repair.
- S12 authority compatibility and process-boundary negative controls need explicit successor coverage before any legacy wrapper retires.
- Halt-loud `SystemExit` behavior is preserved; runner observability is a decision (N01), not a retirement-time repair.

`next: NONE`
