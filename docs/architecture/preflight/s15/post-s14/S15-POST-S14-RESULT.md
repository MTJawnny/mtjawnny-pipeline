# S15.R0 Post-S14 Readiness Revalidation: Result

Status: **EVIDENCE REPAIRED BY S15.R0.R2 — NOT DELETION, ARCHIVE, OR RETIREMENT AUTHORIZATION. R0/R0.R2 acceptance is a separate Manager decision.**

| field | value |
|---|---|
| Selecting K | Issue #1 `5675514144` (`K-20260915-S15-R0-POST-S14-READINESS-REVALIDATION-ISSUED`) |
| Task | Issue #1 `5675512901` (`S15.R0.POST-S14-READINESS-REVALIDATION`) |
| Base / accepted head | `49fcb292e0668b70901118c52dedc0ffd00f389f` (S14.R3.R1) — measurement base for R0 and R0.R2 |
| R0.R2 repair | K `5683296790` → T `5683294052` (parent review `5683255432`); repair parent `7aeb24721d7511f18644afbf46d7dc4ed2fc3088` |
| Branch | `refoundation-experiments-migration-s15-r0-post-s14-readiness-2026-09-15` |
| Controls | AQ4 PAUSED · BRIDGE0 PARKED_UNUSED · STEP6 NO · MERGE NO |
| `origin/main` | `3a2db848329cfcd54846a6ef6b4f3e1a4bc606b3` (unchanged, not moved) |

The Objective-4 set under `docs/architecture/preflight/s15/` was treated as historical input measured at `9f92039e`. It is preserved byte-identical, and nothing was inherited from it.

## 0. S15.R0.R2 repair summary (read first)

R0.R2 repairs this evidence after the validated R0.R1 STOP and the Manager-reconciled adversarial audit. It re-measured, at `49fcb292`, only the scopes shown to be insufficient. **No disposition changed** (tracked `DELETE_SAFE` stays 0); prerequisites, blockers, routing/test claims and several counts did.

- **Route census.** 1589 mention lines / 754 edges over all 88 ARCHIVE_PRESERVE candidates, classified into the eight edge classes with 55 recorded manual adjudications. 76 candidates carry a material edge from outside their co-move set (82 including analyzer participation); 37 carry a current operator/law route (5 of them in `experiments/**`); 4 carry an unresolved `UNKNOWN_BLOCK` route (new blocker **N09**). R0's `NO_OPERATOR_SURFACE_FOUND` on every `experiments/**` archive candidate was false.
- **Known examples, all confirmed:** `docs/MEMBER-ADD-MUTATION-LAW.md` → `foundry_codebook.py add-member` (law route); `foundry_codebook.py` `/1` halt → `foundry_migrate_codebook_v2.py` / `foundry_reconcile.py` (diagnostic route, pinned by a source-inspection guard that would stay GREEN if the target moved); `tier_engine.py` → `invert_tags.py` (diagnostic route); `test_layout_delegation` reads `foundry_consolidate_run1_apply.py` source; `test_codebook_store` analyzes `foundry_reaudit.py`, `run1_apply` and six composed C8.5V names.
- **D1 accounting.** Raw `FAILED (failures=17, errors=8)` vs BASE `FAILED (failures=12)`; 4 new failing + 1 new erroring **method IDs**, 8 subtest errors under that one method, and **all 12 inherited-red methods changed values**. Member attribution by the repository's own analyzers is recorded; D1 remains a batch experiment.
- **Clean checkout.** 32 modules: 29 rc=0 (22 skips), 3 nonzero. Broad discover never reaches 19 modules (786 tests). Shapes substrate: 5 pre-abort error identities, 55 censored tests, all non-OK isolated outcomes missing-input.
- **Restore.** Corrected from source: live-default fetch with snapshot mode and live rulings fallback; Path-E lock is pilot-only; selected vs archived corpus containers differ only in gzip MTIME; restore needs an injected backup policy. Verified restoration is a later prerequisite — **not proved**.
- **Blocker graph.** Recovery rows now link N08 (B02/N03 kept only for codebook backups; snapshot backups link B10); unknown/historical-only rows link B07; N02 clears by conserving the guarded proposition; N03 carries every current law/operator route; **B13 stays CLEARED as timing law only.**
- **NC8b.** Corrected on all four surfaces: 11 paired sub-controls + NC8b standing-red BASE observation.
- **Negative controls for the new method:** NC-R2-1..6 PASS with byte-exact restore (NC-R2-2 first exposed and fixed a classifier gap).

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
  - NC1–NC10 hazard classes demonstrated (11 paired sub-controls + NC8b standing-red observation);
  - R0.R2 recheck: identity still `51fca151…`, no live reader, D3 failure blocks identical to BASE at value level.
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

| destination | members (no R0 strict live consumer; R0.R2 edges and prerequisites are per candidate in the matrix) |
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
| B11 pristine checkout | STILL_BLOCKED | clean Gate 2 3/16; 29/32 modules rc=0; discover aborts (19 modules never run); 22 skips; restore unproven |
| B12 cleanup truth homes | **SUPERSEDED** | AG-CLI-01 → `docs/MEMBER-ADD-MUTATION-LAW.md`, R8.3 → `docs/ACTIVATED-REGENERATE-SELF-DET-LAW.md`; B-MIGRATION stub no longer a sole home |
| B13 timing law | **CLEARED** | the whole set was re-derived at `49fcb292`; clearance holds for this base only |

**New blockers:**

- **N01:** a `SystemExit` from an absent input aborts the discover run (observability).
- **N02:** tracked archive/delete changes guarded propositions. D1: raw 17 failures / 8 errors vs 12 / 0; 4 new failing + 1 new erroring method; 12 inherited-red methods value-changed. Clears only by conserving each guarded proposition or authorized retirement.
- **N03** (DECISION_REQUIRED): current law, Gate 2 and executable diagnostics route through legacy paths (CLAUDE.md CR route, Gate-2 lint argv, AG-CLI-01 embodiment, `/1` guidance, tier_engine/shape_extractor/reach_census/run1_apply diagnostics).
- **N04:** tracked `docs/architecture/preflight/s16b/claims.jsonl` matches `*.jsonl`.
- **N05** (DECISION_REQUIRED): ignored `experiments/out/aq4/**` evidence has no home while AQ4 is PAUSED.
- **N06** (DECISION_REQUIRED): 7 sole-home documents.
- **N07** (DECISION_REQUIRED): 7 tracked files with no accepted destination.
- **N08** (DECISION_REQUIRED): recovery backups with no successor owner — 169 RECOVERY_MATERIAL rows (30 codebook backups + 139 snapshot pre-restore backups) inside 172 files, now actually linked to N08.
- **N09** (DECISION_REQUIRED, R0.R2): 5 unresolved pending-decision route edges on 4 ARCHIVE_PRESERVE candidates.

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
- **Per module (re-derived by R0.R2):** 32 modules, 29 rc=0 (22 skips; BASE populated: 0), 3 nonzero:
  - `test_layout_delegation`: the 12 inherited failures;
  - `test_s13r2_manual_operator_closure`: 2 missing-input failures (status stops at `NO_LOCAL_CODEBOOK` before any transport call). Its `selected authority NONE — manifest … absent` line is a rendering defect in `authority_cli` for that state: the tracked selector exists and was read (recorded under N01; not repaired);
  - `test_mtg_shapes_substrate`: aborts; 5 pre-abort errors (1 `setUpClass`, 4 tests), 55 censored tests; in isolation 46 ok / 28 + 7 missing-input, 0 semantic regressions.
- **Broad discover:** 19 modules (786 tests) are never reached.
- **Restore (source inspection only):** `pipeline/fetch.py` defaults to live Scryfall and also has `--from-snapshot --snapshot-date` (rclone), where missing archived rulings fall back to live. The Path-E input lock is pilot-only, not global corpus authority; it records selected container `2be88ba8…` and archived container `b46e0670…` with shared content `5e47e132…` (gzip MTIME differs), and the runtime checks the container digest first. `mtj_foundry.authority_restore` needs a caller-supplied backup policy to replace a differing codebook; the legacy authority shell injects `foundry_codebook.backup_codebook`.
- **What a destructive S15 needs first:** verified restoration of the selected corpus container and the selector-verified codebook. This is a later implementation prerequisite; neither R0 nor R0.R2 executed or proved any restore.

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

All 10 controls ran; NC2 and NC8 were split into a/b variants, giving **12 sub-controls**. **11 paired sub-controls** (NC1, NC2a, NC2b, NC3, NC4, NC5, NC6, NC7, NC8a, NC9, NC10) showed a normal/control state and a rigged RED/BLOCKED state. **NC8b** is an intentional **standing-red BASE observation** that `var/**` is exposed/unignored; it has no green→red pair. All NC1–NC10 hazard classes are demonstrated. Zero residue is a Worker-execution claim, not independently repo-verifiable history. Details: `S15-POST-S14-CONSERVATION-TEST-DESIGN.md` §4.

R0.R2 added **NC-R2-1..6** for the edge classifier (current-law Markdown route, executable diagnostic incl. message constant, direct source read, shell→candidate diagnostic, historical prose not promoted, validator refuses promotion over UNKNOWN_BLOCK/unfulfilled routes): all PASS with byte-exact restore; §8 of the design document.

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

| check | BASE | R0 FINAL (`7aeb247` tree) |
|---|---|---|
| Gate 2 | rc 0 · 16 / 15 / 1 KNOWN (exact W6) / 0 unexpected | identical |
| broad suite | 1850 · 12 failures (inherited `test_layout_delegation`) · 0 errors | identical ID sets |
| old Objective-4 files | 10 files | byte-identical |
| diff vs BASE | — | exactly 12 added files under `docs/architecture/preflight/s15/post-s14/` |
| `src/**`, `tests/**`, `config/**`, `.gitignore`, `archive/**`, `benchmarks/aq4/**`, ratchet/succession | — | unchanged |
| JSON evidence ×2 | — | byte-identical regeneration |

### R0.R2 verification (candidate repair tree)

| check | result |
|---|---|
| repair parent / measurement base | `7aeb247…` / `49fcb292…` |
| diff vs repair parent | exactly the 10 authorized files under `post-s14/`; TRUTH-HOME and QUARANTINE byte-identical |
| Gate 2 | rc 0 · 16 run / 15 ok / 1 KNOWN (family_sweep) / 0 unexpected; row identity equal to R0 BASE (timings excluded) |
| W6 | exact 6 blocking == authorized W6 == R0 BASE set; register config/registers/family-sweep-known-debt.json sha256 db9f0c45…8ddff |
| broad suite | 1850 · FAILED (failures=12) · 0 errors; failing method-ID set == the 12 inherited test_layout_delegation IDs; failure blocks identical to R0 BASE at value level |
| old Objective-4 files | 10 files byte-identical to 49fcb292 |
| source/test/config/.gitignore/archive/AQ4/ratchet | git diff vs 7aeb247 empty for src, tests, config, .gitignore, archive, benchmarks, refoundation, experiments, pipeline, .github, .claude, CLAUDE.md, pyproject.toml, README.md |
| JSON regeneration ×2 | all 10 repaired files byte-identical across two independent emitter runs |
| primary ignored inventory | 3,620 files / 3,355,335,202 B / digest ab3d1c10…6d27 == R0 (re-measured read-only before emitting) |

No merge, no main movement, no AQ4 execution or import, no Bridge0, no Step6. `next: NONE`.
