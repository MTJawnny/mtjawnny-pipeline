# Gate 2 closeout evidence — 2026-09-13

Status: FULL GATE 2 VERIFIED; COLD-START CLOSEOUT NOT ACCEPTED.

This is historical verification evidence, not a task, checkpoint, accepted-head selector, or permission to execute anything. Current authority remains GitHub Issue #1 latest K -> active T. The Captain-authorized fresh-session closeout limits changes to audit scaffolding and durable evidence; the additional routing repairs below were not executed.

## Authority and exact source identities

- Latest K inspected: K-20260912-OBJECTIVE5-CLOSED-OBJECTIVE6-SEPARATED, Issue #1 comment 5649220022.
- Accepted implementation h: `9f92039eb9c7132a351576c31472eb30a2957a67`.
- Substantive cleanup proposal tested: `18a4260d7d5b72e6b13a36fec335d82287f24792`.
- Cleanup branch before this closeout commit: `cleanup/cold-start-archive-2026-09-12` at `2b6f89432a7e53e37bcf32eca8836108fb72b929`.
- Source execution used real detached Git worktrees at those exact commits, not reconstructed indexes: 430 accepted tracked files and 458 cleanup tracked files. Tracked worktrees were clean before and after execution. External inputs remained ignored/untracked.
- This report's containing commit is a cleanup/evidence commit, never accepted h. Its exact SHA is recorded in the accompanying Issue #1 result after publication.

## Verified external inputs

| Input | SHA-256 | Size / population |
|---|---|---|
| Selected codebook | `6aa6193f8a457ae4c7884e364f519749a9d68b96f7ecedf3fa903bfa4677426c` | 5,066,147 bytes |
| Historical Oracle gzip | `b46e0670a8f3fa2d5357ec35ff7f8d58e7c2f9f15db0e27a3b0543672b00c217` | 38,233 nonblank JSONL records |

The codebook identity was checked against each worktree's `config/selectors/codebook-authority.json`. Byte-identical copies were placed at `experiments/out/foundry/codebook.json` and `data/raw/oracle-cards.jsonl.gz`. Both digests were checked again after execution. No selector or input was changed.

## Complete canonical verification

| Exact source | Command | Rows | Passed | Known-excused | Runner-unexpected | Exit |
|---|---|---:|---:|---:|---:|---:|
| Accepted h | `python3 -u tests/guards/gate2/foundry_gate2.py` | 16 | 15 | 1 | 0 | 0 |
| Cleanup proposal | same full command | 16 | 15 | 1 | 0 | 0 | 0 |
| Accepted h negative control | full command plus `--selftest` | 17 | 15 | 1 | 1 deliberate | 1 |

The only known-excused row was family_sweep exit 3, where the tool reported exact equality to the authorized W6 fingerprint set. The sole selftest failure was SELFTEST_rigged. Every invocation completed object_lattice, locality, and qualifier_census. No rows were omitted and no baseline or guard was relaxed. The selftest appends a deliberately failing child process; it does not corrupt the codebook or source.

Cleanup Worker/cold-start guard: `python3 -m unittest tests.refoundation.test_worker_operating_contract`, 21 tests passed, including 10 corruption/negative-control tests. These scoped tests do not prove all repository prose is free of stale routing.

## Independent conservation

| Registry measurement | Accepted | Cleanup |
|---|---:|---:|
| Source documents | 142 | 142 |
| Distinct ruling IDs | 127 | 127 |
| References | 685 | 685 |
| Corroborated rulings | 86 | 86 |
| Sole-home rulings | 41 | 41 |

Both registries were rebuilt with their own `build()` functions in separate processes using the tracked-file indexes. Exact ruling ID sets, per-document ruling IDs, sole-home ownership, deletion blockers, and reference `(ID, document, statement)` multisets matched; line numbers naturally changed. All 29 archived original payloads matched the corresponding accepted-h Git blobs byte-for-byte. The provenance ledger is `archive/routing/README.md`.

There was no accepted-to-proposal diff under `src/`, `experiments/`, `config/`, `tests/fixtures/`, `tests/guards/`, `recipes/`, or `tags/`. The sole changed test file was the explicitly routing-related Worker operating-contract guard. `git diff --check` was clean. The four current routing documents exist and route to Issue #1. No production/operator executable imports or executes `archive/routing/`; the only code references to it are the routing guard's preservation/pointer checks.

The broader claim of no broken live links is NOT certified: obsolete documents below still reference old paths. Current root routing is verified, but global cold-start completeness is not.

## Residual routing findings — zero-hazard bar NOT met

The independent sweep examined tracked non-archive text for PICK-UP-HERE, NEXT, ACTIVE, fresh Claude/ChatGPT, resume, Worker executes, STOP, Objectives 1–5, AQ4, Bridge v0, STEP6, MIGRATION_FIRST, and S10–S16. It found 306 files / 2,366 matching lines; occurrences are candidates, not a defect count. Root routers, current binding law, runtime/operator references, frozen evidence, and inert stubs are legitimate categories. The following five unbannered documents still provide concrete historical session instructions and remain unresolved:

| File | Evidence | Registry sole homes |
|---|---|---|
| `docs/T3-BUILDOUT-PLAYBOOK.md` | Opening directs one step per Claude session; Step 1 claims old work is currently uncommitted and supplies subsequent execution order. | none |
| `docs/T3-AXIS-FOUNDRY-v3.md` | Opening presents a current session spec, inherits the old playbook, and directs a batch execution loop. | none |
| `docs/WORK-PACKETS-2026-08-07.md` | Describes old handoff/whole-grammar startup as current, then offers alternate context tiers and runnable packets. | none |
| `docs/B-CONSOLIDATION-REAUDIT-PACKET.md` | Opens with YOUR ROLE/read-before-everything and assigns an old external audit plus successor-session sequence. | R8.3 |
| `docs/B-MIGRATION-DIRECTIVE.md` | Directs a completed /1-to-/2 migration, expects the obsolete /1 codebook, and tells the session to proceed. | AG-CLI-01 |

At least five confirmed stale-routing hazards remain; this is a lower bound, not an exhaustive clearance. One additional item needs classification: `docs/AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md` calls itself CURRENT AQ4 ENTRY POINT and mandates reads across semantic work. It also explicitly limits itself to benchmark/pre-registration and grants no production authority. Its relationship to the paused AQ4/current task routing needs an explicit disposition rather than treating the title alone as permission or deleting preserved benchmark commitments.

The five previously bannered sole-home handoffs listed in `archive/routing/README.md` remain preserved intentionally. The two additional sole-home documents above must not be removed without mechanical truth conservation. This closeout does not authorize interpretation or relocation of their law. No residual documentation repair was attempted.

## Audit scaffolding and final diff

All five post-proposal audit commits changed only `.github/workflows/cold-start-input-verified-gate2.yml`. A second audit-only workflow, `.github/workflows/cold-start-final-audit.yml`, already existed in the substantive proposal. Both were inspected and are removed by this closeout commit. Their history remains in Git; durable measured results are retained here.

Relative to the substantive proposal, the final tree removes the remaining final-audit workflow and adds this report. Relative to the pre-closeout branch, it removes both audit workflows and adds this report. All remaining bytes must be verified equal after the branch update.

Relative to accepted h, categories remain: archived originals/provenance, inert compatibility stubs, historical-evidence banners, current router/protocol/operator prose, the routing guard update, and this verification report. No temporary audit workflow remains.

## Objective 1 and remaining refs

Objective-1 evidence remains at `architecture/objective1-foundry-common-preflight-complete-2026-09-12`, head `9eb3e0ca8cc60b00364a321967f1577a73f53ce5`. Its census and DRAFT / NOT AUTHORIZED S10 contract remain present. Census reports 87 importers, 35 externally referenced names, and 45 module-level responsibilities. This closeout does not repeat or promote that preflight into implementation acceptance.

Evidence checksum caveat: census bytes match documented SHA `11463eac388849ea8fa527bb239e13ea017179817c0dd314bc3c637563d73cc9`. The CSV stored in Git has SHA `b60be70cef45fc03324452242f144f2cfb82d4638c0208408532dfa26ab53282`; the completion document instead records `0ec96b701668730522e44d0402015df0cd943140e033b753c0544924008117e0`. Converting the 342 LF line endings to CRLF reproduces that recorded hash exactly. This explains the discrepancy but does not correct the recorded-byte claim. The Objective-1 branch was not changed.

`tmp-do-not-use` points to `df736a8c2999ed324a85688e6f5ddef6479b4231`, which is already in cleanup history and has zero unique commits relative to the cleanup branch. Deletion remains pending: the GitHub connector exposes no branch-delete operation, and a non-mutating Git push dry-run failed because shell Git had no HTTPS credentials. No branch was deleted or history rewritten.

Default branch is `main`, head `3a2db848329cfcd54846a6ef6b4f3e1a4bc606b3`; generic GitHub entry still lands on the old pre-refoundation tree.

Next Captain action: select a bounded residual-routing/conservation repair and correct the Objective-1 recorded CSV checksum. After review/acceptance, separately authorize the merge/ref/default-branch action that makes the clean tree universally visible; do not expose this proposal as fully cleared yet. The redundant temporary branch can then be deleted by an authenticated maintainer.

Accepted h, codebook, authority selector, CR, semantic behavior, AQ4, Bridge v0, Step6, S10–S16 implementation, and merge/default-branch state were not changed. Gate 2 closeout is verified; universal cold-start cleanup remains incomplete.

## Exact runner transcripts

### accepted-gate2.log

SHA-256: `bb5af0846e1479eb45c385daa723afed13a659a6bf5afe8b63b0d5918efcbce9`

```text
==============================================================================
GATE 2 — every check, one exit code
==============================================================================
  [  ok  ] lint                 exit=0    0.2s
  [KNOWN ] family_sweep         exit=3    0.5s
           -> blocking findings exactly equal the authorized W6 set in docs/family-sweep-known-debt.json
           -> ◐ KNOWN DEBT — the blocking set is exactly the authorized W6, by (kind, subject):
  [  ok  ] definition_drift     exit=0    4.8s
  [  ok  ] ruling_registry      exit=0    0.4s
  [  ok  ] conservation         exit=0   22.7s
  [  ok  ] visibility           exit=0    5.5s
  [  ok  ] ground_truth         exit=0    3.7s
  [  ok  ] ground_truth_wide    exit=0    5.3s
  [  ok  ] gate_audit           exit=0   20.0s
  [  ok  ] probe_guards         exit=0    0.1s
  [  ok  ] recorded_numbers     exit=0   13.5s
  [  ok  ] invariance           exit=0   22.1s
  [  ok  ] reachability         exit=0    0.4s
  [  ok  ] object_lattice       exit=0   72.3s
  [  ok  ] locality             exit=0    4.5s
  [  ok  ] qualifier_census     exit=0   21.2s

==============================================================================
VERDICT
==============================================================================
  gates run                       16
  passed                          15
  known-failing (excused)          1
  UNEXPECTED failures              0

  ✓ Gate 2 is GREEN. Every check ran, and every one of them
    is capable of failing -- negative-controlled 2026-08-09,
    see docs/SYSTEM-SELF-TEST-2026-08-09.md.
```

### cleanup-gate2.log

SHA-256: `b0486d99700d1d95949baabdee5ca794625ab26c87c1d3540dd03ac5d735f70b`

```text
==============================================================================
GATE 2 — every check, one exit code
==============================================================================
  [  ok  ] lint                 exit=0    0.1s
  [KNOWN ] family_sweep         exit=3    0.4s
           -> blocking findings exactly equal the authorized W6 set in docs/family-sweep-known-debt.json
           -> ◐ KNOWN DEBT — the blocking set is exactly the authorized W6, by (kind, subject):
  [  ok  ] definition_drift     exit=0    4.0s
  [  ok  ] ruling_registry      exit=0    0.4s
  [  ok  ] conservation         exit=0   23.6s
  [  ok  ] visibility           exit=0    5.1s
  [  ok  ] ground_truth         exit=0    3.9s
  [  ok  ] ground_truth_wide    exit=0    5.1s
  [  ok  ] gate_audit           exit=0   18.9s
  [  ok  ] probe_guards         exit=0    0.0s
  [  ok  ] recorded_numbers     exit=0   13.6s
  [  ok  ] invariance           exit=0   21.6s
  [  ok  ] reachability         exit=0    0.4s
  [  ok  ] object_lattice       exit=0   73.3s
  [  ok  ] locality             exit=0    4.8s
  [  ok  ] qualifier_census     exit=0   21.4s

==============================================================================
VERDICT
==============================================================================
  gates run                       16
  passed                          15
  known-failing (excused)          1
  UNEXPECTED failures              0

  ✓ Gate 2 is GREEN. Every check ran, and every one of them
    is capable of failing -- negative-controlled 2026-08-09,
    see docs/SYSTEM-SELF-TEST-2026-08-09.md.
```

### accepted-gate2-selftest.log

SHA-256: `980fb9b5af43e1c63ddfdb860e9acd4b048382f314e9da165d7d07b34cce5103`

```text
==============================================================================
GATE 2 — every check, one exit code
==============================================================================
  [  ok  ] lint                 exit=0    0.1s
  [KNOWN ] family_sweep         exit=3    0.4s
           -> blocking findings exactly equal the authorized W6 set in docs/family-sweep-known-debt.json
           -> ◐ KNOWN DEBT — the blocking set is exactly the authorized W6, by (kind, subject):
  [  ok  ] definition_drift     exit=0    4.0s
  [  ok  ] ruling_registry      exit=0    0.5s
  [  ok  ] conservation         exit=0   23.0s
  [  ok  ] visibility           exit=0    5.2s
  [  ok  ] ground_truth         exit=0    3.8s
  [  ok  ] ground_truth_wide    exit=0    5.1s
  [  ok  ] gate_audit           exit=0   18.6s
  [  ok  ] probe_guards         exit=0    0.0s
  [  ok  ] recorded_numbers     exit=0   13.4s
  [  ok  ] invariance           exit=0   22.2s
  [  ok  ] reachability         exit=0    0.4s
  [  ok  ] object_lattice       exit=0   73.8s
  [  ok  ] locality             exit=0    4.5s
  [  ok  ] qualifier_census     exit=0   21.3s
  [ FAIL ] SELFTEST_rigged      exit=1    0.0s
           -> this row is rigged to fail on purpose

==============================================================================
VERDICT
==============================================================================
  gates run                       17
  passed                          15
  known-failing (excused)          1
  UNEXPECTED failures              1

  ✗ Gate 2 is RED. The failing tool's own output is the
    report -- run it directly and read it. Do not proceed on
    a red gate; that is the drift this procedure exists to stop.

  --- SELFTEST_rigged (exit 1) ---
```
