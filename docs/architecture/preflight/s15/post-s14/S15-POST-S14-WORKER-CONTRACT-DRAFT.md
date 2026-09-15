# S15 Post-S14 Worker Contract — DRAFT

> # **NOT AUTHORIZED — DRAFT ONLY — NOT AN ACTIVE TASK**
>
> Generated from the S15.R0 readiness state measured at `49fcb292e0668b70901118c52dedc0ffd00f389f`. It authorizes nothing: no deletion, archive move, shell retirement, `.gitignore` edit, runtime cleanup, guard change, baseline succession, AQ4 action, merge, or successor work. Only a later Issue #1 `K` selecting a Manager-issued `T` can authorize any slice.

## Why this is not a one-shot destructive S15

At the measured base:

- **8 of the 13 old blockers are `STILL_BLOCKED`** and **8 new blockers** exist.
- **5 of those new blockers are `DECISION_REQUIRED`**: N03, N05, N06, N07, N08.
- **Tracked `DELETE_SAFE`: 0.**
- The only `DELETE_SAFE` item is one ignored local file, and it has negligible value.
- Every tracked archive or delete changes guards:
  - D1: +4 failures and +1 error;
  - D2: Gate 2 red.

A single destructive S15 contract would therefore be dishonest. The work partitions into bounded slices with an explicit prerequisite order.

## Prerequisite order

```text
P0  Manager/Captain decisions (no code): N03 CR-route law + Gate-2 lint argv, N04 tracked-but-ignored claims.jsonl,
    N05 ignored AQ4 evidence home (needs AQ4 authority; AQ4 stays PAUSED), N06 sole-home documents,
    N07 seven undecided tracked legacy files, N08 recovery-backup retention, N01 runner-abort observability.
P1  Restore proof (B11): pristine checkout obtains byte-pinned corpus (2be88ba8…) and selector-verified codebook (6aa6193f…)
    through a verified restore; no network-ambiguous "fetch latest".
P2  Ignore ownership (B08): authorized .gitignore change for var/** with NC7/NC8 bidirectional controls.
P3  Archive slices (per family), each with authorized guard retargeting (N02).
P4  Test-consumer detachment for archive-family files still loaded by guards (BLOCKED_LIVE_CONSUMER).
P5  Shell retirement per permanent owner after caller closure (B02/B03, N03).
P6  Engine family (B10) after differential-oracle retirement.
P7  foundry_common last (B01).
P8  Runtime relocation experiments/out/** -> var/** by role (B02, B07, N05, N08), after P1+P2.
P9  Document/stub topology (B09, N06) only with authorized ratchet succession.
```

## Slice template (every slice)

```yaml
schema: mtj-task/1            # to be issued by Manager; this block is a shape, not a task
status: DRAFT_NOT_AUTHORIZED
base: <ACCEPTED_HEAD_AT_ISSUE>   # must re-run S15.R0 census + NC1-NC10 at this base
allow: <EXACT_PATH_LIST_FROM_REGENERATED_MATRIX>   # members of ONE family / ONE shell only
deny:
  - benchmarks/aq4/**            # PROTECTED frozen evidence; AQ4 PAUSED
  - src/** config/** refoundation/conservation/** unless explicitly named
  - any candidate whose disposition at <BASE> is BLOCKED_* or KEEP_PERMANENT
  - .gitignore unless the slice is P2
  - any registry --update-baseline / succession unless the slice is P9 and names the authorization
required:
  - strict + conservative consumer census over the exact set = empty (or only explicitly retargeted guard pins)
  - impact rig BEFORE commit; every changed node-ID is a named, authorized retarget
  - Gate 2 row identity 16/15/1 + exact W6; broad failing/error sets == BASE (+/- named retargets only)
  - R100 byte/blob manifest for archive moves; provenance pairs move together
  - registry before/after (ids, sole-home, corroborated, ref delta attributed)
  - clean-checkout dependence not increased
  - NC1-NC10 re-executed red on the slice's own members; zero residue
stop:
  - base drift; any new strict consumer; any unexplained conservative consumer
  - any guard change beyond the named retargets
  - any need to touch a deny path
next: NONE
```

## Candidate slices derived from the measured matrix

Each slice is recorded with its members at BASE, what blocks it, and the evidence it needs. Nothing listed here is executable today.

| slice | members at BASE | blocked by | evidence it needs |
|---|---|---|---|
| **A-batch8** | `foundry_batch8_ab.py`, `foundry_batch8_canon_analysis.py`, `foundry_batch8_diff.py` → `archive/research/batch8/` | N02 (sidecar + population pins) | impact rig for these 3; sidecar retarget authority |
| **A-measure** | `experiments/measure/**` (9, including 3 memos) → `archive/research/thesaurus-measurement/` | N02 | `axis_foundry.py` and `family_tree_evidence.py` are sidecar/legacy-referenced |
| **A-triage** | `foundry_adapt_batch1..7_decisions.py`, `foundry_assemble_batch2..7.py` (13) → `archive/research/triage/` | N02 | R1 note: each batch's ratified record must be confirmed present in `docs/` |
| **A-consolidation** | `foundry_consolidate_run1_apply.py`, `foundry_consolidate_run1_enumerate.py`, `foundry_corpus_pass_run1.py`, `foundry_corroboration_pass.py` | N02 | `foundry_consolidate_run1.py` and `_classify.py` stay (live reach via `r5_attribution` → `test_layout_delegation`) |
| **A-mutations** | `foundry_any_damage_split.py`, `cdr09_derive.py`, `cdr09_walk.py`, `axis_merge_pointer_correction.py`, `batch7_pay_life_scrub.py`, `gate0_scrub.py`, `locality_backfill.py` | N02; the PAIR rule | `foundry_migrate_codebook_v2.py` must wait for `foundry_verify_migration.py`, which is loaded by `test_codebook_store` |
| **A-research** | `foundry_axis_walk.py`, `blanket_risk.py`, `reach_census.py`, `reaudit.py`, `selfother_scope.py`, `synonym_collision.py`, `w3_census.py`, `invert_tags.py` → `archive/research/` | N02; conservative references | `invert_tags.py` is named as a prerequisite in a `tier_engine` halt message (B10 coupling) |
| **A-reports** | `POKE-PUNCH-LIST.md` → `archive/reports/` | N02 | R1: ruling-registry sweep first |
| **P4 detach** | `foundry_prior_art`, `r5_attribution`, `slug_reparse`, `wire_capability`, `wire_experiment`, `reminder_conformance`, `stage1b`, `verify_migration`, `consolidate_run1{,_classify}`, `det_patterns_probe`, `snapshot` | guard/test consumers | authority to change the consuming guards (they load these files via `load_legacy`) |
| **P5 shells** | `foundry_codebook`, `foundry_cr`, `foundry_cr702_classes`, `foundry_cr_checks`, `foundry_cr_edition_diff`, `foundry_keyword_buckets`, `foundry_det_pass`, `foundry_locality`, `foundry_object_lattice`, `foundry_shape_extractor`, `validate_slug`, `foundry_authority` | caller closure; N03; frozen AQ4 surface (B01/B05-SURFACE) | per-shell caller lists are in PATH-READINESS-MATRIX; `foundry_authority` needs S12 legacy-selftest control successor coverage (B03) |
| **P6 engine** | `tier_engine.py`, `emit_viewer.py`, `serve_viewer.py`, `viewer.html`, ignored `experiments/out/snapshots/**` | B10 | differential oracles in `test_corpus_capability` / `test_oracle_text_capability` |
| **P7** | `foundry_common.py` | B01 | 88 pinned importers |
| **P9 docs** | 29 stubs, 2 router pointers, 1 AQ4 pointer, 7 sole-home documents | B09, N06 | authorized succession; canonical-law extraction |
| **Never in S15** | `benchmarks/aq4/**`, `pipeline/**`, permanent sets | — | — |
| **Ignored D3** | `experiments/out/foundry/audit-baseline.json` | — | `DELETE_SAFE` with all eight criteria; a local convenience only, not required for any slice |

## Frozen invariants every slice inherits

- AQ4 remains **PAUSED**. Frozen AQ4 code is never imported or executed.
- The frozen `/1` reconcile provenance is never resurrected as live implementation authority.
- AG-CLI-01 is behavior law, **not** permission to install or expose a mutating CLI.
- The `foundry_cr702_classes --unstated` KeyError is conserved debt, never a retirement-time repair.
- S12 authority compatibility and process-boundary negative controls need explicit successor coverage before any legacy wrapper retires.

`next: NONE`
