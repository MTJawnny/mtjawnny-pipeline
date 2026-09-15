# S15.R0 Post-S14 Readiness Revalidation: Result

Status: **COMPLETE EVIDENCE: NOT DELETION, ARCHIVE, OR RETIREMENT AUTHORIZATION**

| field | value |
|---|---|
| Selecting K | Issue #1 `5675514144` (`K-20260915-S15-R0-POST-S14-READINESS-REVALIDATION-ISSUED`) |
| Task | Issue #1 `5675512901` (`S15.R0.POST-S14-READINESS-REVALIDATION`) |
| Base / accepted head | `49fcb292e0668b70901118c52dedc0ffd00f389f` (S14.R3.R1) |
| Branch | `refoundation-experiments-migration-s15-r0-post-s14-readiness-2026-09-15` |
| Controls | AQ4 PAUSED · BRIDGE0 PARKED_UNUSED · STEP6 NO · MERGE NO |
| `origin/main` | `3a2db848329cfcd54846a6ef6b4f3e1a4bc606b3` (unchanged, not moved) |

The Objective-4 set under `docs/architecture/preflight/s15/` was treated as historical input measured at `9f92039e`. It is preserved byte-identical, and nothing was inherited from it.

## 1. Candidate universe (re-enumerated at BASE)

All 556 tracked paths are partitioned exactly once: **168 individual candidates + 24 candidate sets**. A further **22 runtime sets** cover the visible ignored state.

| class | individual candidates |
|---|---:|
| tracked `experiments/**` (old: 107; −21 AQ4 R100 moves in S14) | 86 |
| docs compatibility stubs over `archive/routing/docs/**` | 29 |
| archived router pointers (`refoundation/ACTIVE-PHASE.yaml`, `BOOTSTRAP-STATE.yaml`) | 2 |
| AQ4 PAUSED pointer (`docs/AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md`) | 1 |
| sole-home stale/withheld documents | 7 |
| retired command tombstones (`.claude/commands/triage-*.md`) | 3 |
| `archive/**` | 40 |

### Dispositions

| disposition | individual | of which `experiments/**` | sets | runtime sets |
|---|---:|---:|---:|---:|
| `KEEP_PERMANENT` | 0 | 0 | 21 | 0 |
| `COMPATIBILITY_SHELL_KEEP` | 48 | 13 | 0 | 0 |
| `ARCHIVE_PRESERVE` | 88 | 48 | 3 | 0 |
| `DELETE_SAFE` | **0** | **0** | 0 | **1** (ignored) |
| `GENERATED_RUNTIME` | 0 | 0 | 0 | 6 |
| `BLOCKED_LIVE_CONSUMER` | 18 | 18 | 0 | 3 |
| `BLOCKED_TRUTH_HOME` | 7 | 0 | 0 | 3 |
| `BLOCKED_UNKNOWN` | 7 | 7 | 0 | 9 |

`benchmarks/aq4/**` (30 files) is `KEEP_PERMANENT`, flagged **protected frozen evidence**. It is not a legacy deletion candidate.

### DELETE_SAFE

- **Tracked: none.**
- **Ignored: one file**, `experiments/out/foundry/audit-baseline.json`, a superseded legacy acceptance-control copy. All eight criteria are evidenced in `S15-POST-S14-IGNORED-STATE-INVENTORY.json` → `d3_delete_safe_proof`:
  - no live reader;
  - its bytes equal the tracked genesis snapshot `51fca151…`;
  - D3 rig (removing only this file): Gate 2 and broad node-ID sets identical to BASE;
  - clean checkout never names it;
  - NC1–NC10 demonstrated.
- The classification authorizes nothing, and removing the file serves no S15 purpose.

## 2. Compatibility shells, tombstones and their current callers

**Declared shells with strict live callers** (13 in `experiments/**`):

- `foundry_codebook` (7 live / 20 legacy / 5 frozen-AQ4)
- `foundry_shape_extractor` (10 / 8 / 5)
- `foundry_cr` (6 incl. **CLAUDE.md law** / 6 / 5)
- `foundry_locality` (5 / 3 / 4)
- `foundry_object_lattice` (5 / 2 / 4)
- `validate_slug` (3 / 6 / 4)
- `foundry_cr702_classes` (3 / 2 / 4; carries the conserved `--unstated` KeyError debt)
- `foundry_det_pass` (3 / 1)
- `foundry_authority` (4: the S12/S13 guards run its legacy selftest and boundary)
- `foundry_cr_checks` (1)
- `foundry_keyword_buckets` (1)
- `foundry_cr_edition_diff` (1)
- tombstone `foundry_build_reaudit_packet` (executed by `test_residual_routing_closeout`)

**Other shells and pointers:**

- 29 docs stubs, 2 router pointers, the AQ4 pointer, and 3 command tombstones.
- `test_s13_operator_command_migration` pins the command tombstones as tracked.

**`BLOCKED_LIVE_CONSUMER`** (18):

- `foundry_common`: 88 pinned importers.
- `tier_engine`: differential oracle.
- `foundry_reconcile`: frozen `/1` provenance, byte-pinned by S13.
- `foundry_audit_baseline`: legacy ratchet oracle loaded by path.
- `emit_viewer`, `snapshot`, `foundry_consolidate`, `consolidate_run1`, `consolidate_run1_classify`, `det_patterns_probe`, `prior_art`, `r5_attribution`, `reminder_conformance`, `slug_reparse`, `stage1b`, `verify_migration`, `wire_capability`, `wire_experiment`. All are loaded by guards via `load_legacy(...)`/import, or reached through them.

**`BLOCKED_UNKNOWN`** (7): `foundry_digest`, `foundry_emit`, `foundry_enrich`, `foundry_review.html`, `foundry_slug_dossier`, `foundry_system_map`, `foundry_membership_move`.

## 3. Archive-preserve sets and successor homes

Destinations come from the accepted master plan R1 §5.1/§5.2 (Issue #1 `5608037629`), named by `ProjectPaths`. **None of these destinations is physical at BASE.**

| destination | members (no strict live consumer) |
|---|---|
| `archive/research/triage/` | 13 (adapt 1–7, assemble 2–7) |
| `archive/research/thesaurus-measurement/` | 9 (`experiments/measure/**`) |
| `archive/research/mutations/` | 8 (`migrate_codebook_v2` moves only as a PAIR with `verify_migration`, which is still blocked) |
| `archive/research/` | 8 |
| `archive/research/consolidation/` | 4 |
| `archive/research/batch8/` | 3 |
| `archive/engine/` | 2 (`serve_viewer`, `viewer.html`: behind `tier_engine`, B10) |
| `archive/reports/` | 1 (`POKE-PUNCH-LIST.md`: registry sweep first) |
| `archive/**` (already final) | 40 tracked files; `archive/routing` blobs pinned |

In-place historical sets: `docs/architecture/preflight/**`, `refoundation/preservation/**`, `docs/archive/**`.

## 4. Blockers

**Old blockers:** 4 CLEARED · 8 STILL_BLOCKED · 1 SUPERSEDED.

| id | status | current evidence (short) |
|---|---|---|
| B01 S10 caller closure | STILL_BLOCKED | `foundry_common` has 88 sidecar-pinned importers (18 guard/test strict) plus the frozen-AQ4 surface |
| B02 store/runtime ownership | STILL_BLOCKED | mirror at `experiments/out/foundry/codebook.json`; `var/codebook` not physical; 3 Gate-2 rows STOP when it is absent |
| B03 authority/transport | STILL_BLOCKED | legacy shell still runs S12 selftest controls; 10 restore/selected-truth tests skip without the codebook |
| B04 command stale refs | **CLEARED** | commands are halt-loud tombstones; 0 legacy references; S13 guard green at BASE and clean |
| B05 AQ4 truth home | **CLEARED** | `benchmarks/aq4/**` frozen, manifest `bb939fbf…`; S14 guard 23 OK; NC6 red when rigged |
| B06 ignored visibility | **CLEARED** | full local inventory 3,620 files; classification of unknowns → B07/N07 |
| B07 dynamic/unknown outputs | STILL_BLOCKED | 9 dynamic shapes resolve to 59 files; 332 ignored BLOCKED_UNKNOWN |
| B08 `.gitignore` / `var` | STILL_BLOCKED | `var/` not ignored (NC8b); `.gitignore` unchanged since the old head |
| B09 document/ruling topology | STILL_BLOCKED | registry 138/127/660/86/41 == baseline; D2: removing stubs turns Gate 2 red |
| B10 `tier_engine`/viewer | STILL_BLOCKED | differential oracles + 10 legacy importers + 2,772 snapshot files |
| B11 pristine checkout | STILL_BLOCKED | clean Gate 2 3/16; discover aborts; 22 skips; 2 clean-only failures |
| B12 cleanup truth homes | **SUPERSEDED** | AG-CLI-01 → `docs/MEMBER-ADD-MUTATION-LAW.md`, R8.3 → `docs/ACTIVATED-REGENERATE-SELF-DET-LAW.md`; B-MIGRATION stub no longer a sole home |
| B13 timing law | **CLEARED** | the whole set was re-derived at `49fcb292`; clearance holds for this base only |

**New blockers:**

- **N01:** a `SystemExit` from an absent input aborts the discover run (observability).
- **N02:** guard population pins. D1 turns 5 broad node IDs red while Gate 2 stays unchanged.
- **N03** (DECISION_REQUIRED): CLAUDE.md's CR route and the Gate-2 lint argv still go through legacy shells.
- **N04:** tracked `docs/architecture/preflight/s16b/claims.jsonl` matches `*.jsonl`.
- **N05** (DECISION_REQUIRED): ignored `experiments/out/aq4/**` evidence has no home while AQ4 is PAUSED.
- **N06** (DECISION_REQUIRED): 7 sole-home documents.
- **N07** (DECISION_REQUIRED): 7 tracked files with no accepted destination.
- **N08** (DECISION_REQUIRED): 172 recovery-backup files with no successor owner (32 codebook backups + 140 pre-restore snapshot backups).

## 5. Ignored and runtime inventory

**Measured root:** the primary checkout, read-only, sha256 over every file.

- **Totals:** `data/` 299 files and `experiments/out/` 3,321 files = **3,620 files, 3,355,335,202 B**; digest `ab3d1c10…6d27`.
- **Worktrees:** 66 registered worktrees hold only partial derived copies. No `var/` exists anywhere.
- **Critical identities:**
  - codebook mirror == selector `6aa6193f…`;
  - corpus == input-lock `2be88ba8…`;
  - legacy audit-baseline copy == genesis `51fca151…`;
  - AQ4 workqueue listed in the census (`7443de2e…`).
- **By disposition:**
  - GENERATED_RUNTIME 341 (pipeline outputs/inputs, OS noise);
  - BLOCKED_LIVE_CONSUMER 2,774 (snapshots + 2 authoritative mirrors);
  - BLOCKED_TRUTH_HOME 172 (recovery backups + AQ4 evidence);
  - BLOCKED_UNKNOWN 332;
  - DELETE_SAFE 1.
- **Not inventoried:** `.venv/` (1.2 G local interpreter). `.claude/settings.local.json` was not read or hashed.
- **Untracked docs:** the primary checkout's 9 untracked docs are byte-identical to `refoundation/preservation/captures/…`.
- **Writes during verification:** Gate 2 / `family_sweep --gate` rewrote only `experiments/out/foundry/family_sweep_report.json`, in the evidence worktree's cloned state.

## 6. Clean-checkout probe (exact BASE, no ignored state)

- **Gate 2:** rc 1, 16 run / 3 ok / 13 unexpected.
  - 3 rows STOP on the missing codebook mirror.
  - 10 rows STOP on the missing corpus.
- **Broad discover:** no summary. The corpus STOP `SystemExit` ends the process at `test_mtg_shapes_substrate`.
- **Per module:**
  - 30 modules OK, with 22 skips (BASE populated: 0);
  - `test_layout_delegation`: the 12 inherited failures;
  - `test_s13r2_manual_operator_closure`: 2 clean-only failures (its status text reports the tracked selector as "absent"; observed, not diagnosed);
  - `test_mtg_shapes_substrate`: aborts.
- **What a destructive S15 needs first:** verified restore of the byte-pinned corpus and the selector-verified codebook. Neither `pipeline/fetch.py` (fetches current bulk) nor the remote authority restore was verified in R0.

## 7. Document and ruling topology

- **Registry at BASE:** 138 docs / 127 ids / 660 refs / 86 corroborated / 41 sole-home. This equals the live `ruling_registry` baseline section (succession ordinal 1, `b0f3d6d7…`).
- **Topology homes:**
  - AG-CLI-01 sole home: `MEMBER-ADD-MUTATION-LAW.md`.
  - R8.3 sole home: `ACTIVATED-REGENERATE-SELF-DET-LAW.md`.
  - All 29 stubs: registry SAFE (no sole home).
  - 7 documents BLOCKED as sole homes.
- **Rigs:**
  - D2: stub removal turns Gate 2 red.
  - NC4: a synthetic sole home is caught.
- **Not changed:** no registry emit and no baseline/succession change. The known false-positive behavior is untouched.

## 8. Negative controls

All 10 controls ran; NC2 and NC8 were split into a/b variants, giving **12 sub-controls. All 12 are green unrigged and red rigged, with zero residue.** Details are in `S15-POST-S14-CONSERVATION-TEST-DESIGN.md` §4.

Recorded limitation: strict line-level detection is blind to a split load (NC2a). Conservative mode catches it and is mandatory before any promotion.

## 9. Old-vs-new delta (summary)

- **Universe:** 127 → 168 individual candidates plus exact sets. `experiments/**` 107 → 86.
- **AQ4:** relocated and protected.
- **AG-CLI-01 / R8.3:** extracted to canonical sole homes.
- **Tombstone:** `build_reaudit_packet` went from UNKNOWN to tombstone.
- **Commands:** retired.
- **Shells:** 13 shells now delegate to permanent owners, but no caller closure is proven.
- **Runtime:** full local inventory, and a clean checkout actually executed.

The disposition changes for every old member and every current `experiments/**` file are in `S15-POST-S14-DELTA.json`.

## 10. Verification

| check | BASE | FINAL (this commit's tree) |
|---|---|---|
| Gate 2 | rc 0 · 16 / 15 / 1 KNOWN (exact W6) / 0 unexpected | identical |
| broad suite | 1850 · 12 failures (inherited `test_layout_delegation`) · 0 errors | identical ID sets |
| old Objective-4 files | 10 files | byte-identical |
| diff vs BASE | — | exactly 12 added files under `docs/architecture/preflight/s15/post-s14/` |
| `src/**`, `tests/**`, `config/**`, `.gitignore`, `archive/**`, `benchmarks/aq4/**`, ratchet/succession | — | unchanged |
| JSON evidence ×2 | — | byte-identical regeneration |

No merge, no main movement, no AQ4 execution or import, no Bridge0, no Step6. `next: NONE`.
