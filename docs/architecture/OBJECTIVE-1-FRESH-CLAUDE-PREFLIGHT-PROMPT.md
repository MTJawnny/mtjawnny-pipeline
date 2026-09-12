# Fresh Claude Code Prompt — Objective 1: S10 `foundry_common` Preflight

Status: **HANDOFF PROMPT / NON-EXECUTING**  
Objective: **1 of 5**  
Implementation authorization: **NONE**

Copy the prompt below into a fresh Claude Code session.

---

You are a fresh Claude Code **preflight investigator** for the MTJawnny Foundry repository refoundation.

Repository:

`MTJawnny/mtjawnny-pipeline`

Your task is **Objective 1 of 5: the S10 `foundry_common` dependency/preflight map**.

This is a **research / census / architecture-evidence task only**. It is **NOT S10 implementation**. Do not move code, change APIs, migrate callers, delete compatibility code, advance the migration, merge anything, update baselines, publish authority, or modify runtime semantics.

## Authority law

**Durable GitHub/repository state is authority.**

Do not rely on prior Claude memory, prior Claude sessions, ChatGPT memory, this prompt's expected values, stale handoffs, or old summaries as repository truth. This prompt is only a bootstrap map. If live durable state differs, live durable state wins.

Standing governing principle unless newer durable state supersedes it:

**PRESERVE TRUTH, NOT PLUMBING**

Manager/Worker roles remain:

- Captain = user
- Manager = ChatGPT
- Worker / preflight investigator = you, Claude Code
- durable coordination = GitHub Issue #1

Do not create or imply Manager acceptance. Evidence never self-authorizes implementation.

## Expected discovery anchors — NOT authority

At prompt creation, the expected durable anchors were:

- latest accepted migration checkpoint: `K-20260911-EXPERIMENTS-MIGRATION-S9-ACCEPTED-RECOVERY`
- expected accepted implementation head `h`: `9f92039eb9c7132a351576c31472eb30a2957a67`
- expected active task `a`: `0`
- expected strategy: `MIGRATION_FIRST`
- expected controls: `{AQ4:P, BRIDGE0:U, STEP6:N, MERGE:N}`
- planning branch: `cleanup/obsolete-doc-quarantine-2026-09-11`
- planning branch expected head after the five-objective plan set: `9d949fc9d577b4b44240329fc093144f6003280d`
- master plan: `docs/architecture/PREFLIGHT-OBJECTIVES-1-5-2026-09-11.md`
- Objective 1 plan: `docs/architecture/S10-FOUNDRY-COMMON-PREFLIGHT-PLAN.md`

Treat all of these as discovery hints only. Re-measure.

## Phase 0 — bootstrap from durable state

Before doing any substantive analysis:

1. Read root `CLAUDE.md`.
2. Read GitHub Issue #1 completely enough to identify the **latest valid Manager checkpoint `K`**.
3. From that checkpoint resolve:
   - accepted implementation head `h`;
   - active task `a`;
   - current strategy;
   - standing controls;
   - whether any later S10-related T/X/V/K exists.
4. Read the two planning documents listed above from the cleanup/architecture branch.
5. Verify the accepted implementation source tree you will study exactly matches the accepted `h` from Issue #1.
6. Verify whether S10 has already been accepted, superseded, or partially authorized.
7. Verify there is no active Worker task that conflicts with this preflight.

### Immediate STOP conditions at bootstrap

STOP without widening the task if:

- S10 is already accepted;
- a newer durable direction supersedes this preflight;
- an active task conflicts with the audit;
- accepted-head resolution is ambiguous;
- the source tree under study does not match the durable accepted head and the difference cannot be explained safely.

If S10 already landed, report that Objective 1 must be rebased as a **post-S10 conservation audit**. Do not pretend the original preflight remains current.

## Mission

Produce a **complete, mechanically grounded map of the live `experiments/foundry_common.py` dependency surface** so the later Manager can write the S10 implementation contract without asking a Worker to rediscover responsibilities while moving code.

Durable planning state refers to a **39-symbol migration surface**. That number is an expected discovery anchor only. Re-census the live accepted head. If your measured number differs, explain the exact definition and every source of difference.

This task is about **responsibilities and callers**, not filename migration.

## Mutation boundary

The accepted implementation tree is **read-only** for this task.

You MAY create durable preflight evidence, but only on a **separate evidence/documentation branch** that does not move or amend any accepted implementation ref or active migration PR.

Preferred evidence workflow:

1. Inspect the accepted implementation head in a clean worktree.
2. Use the cleanup/architecture planning branch only as the planning-document base.
3. Create a dedicated evidence branch such as:
   `preflight/s10-foundry-common-map-2026-09-11`
   from the current planning/documentation branch **only after verifying that branch contains no source/runtime changes relative to the accepted implementation head that would contaminate the census**.
4. If that clean separation cannot be proven, keep the analysis worktree at accepted `h` and create the evidence commit separately without altering source code.

Never move `main`, the accepted migration ref, historical accepted refs, or any active implementation PR branch.

No merge.

## Required analysis

### A. Mechanical symbol census

Mechanically enumerate every `foundry_common` name referenced by tracked repository code, tests, scripts, command files, contracts, or live execution paths.

Do not equate “public” with `from foundry_common import X`.

Search at least:

- `import foundry_common as ...` followed by qualified attribute access;
- `from foundry_common import ...`;
- aliased imports;
- dynamic import/importlib patterns;
- subprocess/script invocations whose behavior depends on `foundry_common`;
- tests and negative controls;
- `.claude/commands` and operational command files;
- configuration/contracts that name symbols or behaviors;
- tracked one-off scripts that are still executable/consumed;
- any indirect compatibility contract evidenced by accepted tests or gates.

For **every live symbol**, record:

- symbol name;
- kind: constant / function / class / regex / private helper imported externally / module alias / other;
- defining file and line range;
- every direct importer/caller;
- every known indirect contract consumer;
- import-time initialization requirement, if any;
- repository-path dependency;
- tracked-config dependency;
- generated/runtime-state dependency;
- environment/process-state dependency;
- side effects: write / print / exit / mutate global / `sys.path` / other;
- existing permanent equivalent, if any;
- proposed permanent owner if current architecture makes it defensible;
- ownership evidence;
- uncertainty/blocker.

Keep a distinction between:

- **live externally consumed symbols**;
- **private implementation details only used inside `foundry_common`**;
- **dead/unreferenced definitions**;
- **symbols consumed only by historical/quarantined material**.

Do not delete or “clean up” any category; measure it.

### B. Importer × symbol matrix

Enumerate **every tracked importer** of `foundry_common` and record exactly which symbols each importer consumes.

Classify each importer as one of:

- Gate/check;
- reporter/census;
- codebook/membership mutation;
- pipeline/batch tooling;
- operator/CLI;
- authority/transport;
- AQ4;
- historical/one-off;
- test/negative control;
- other — but if `other`, explain why it cannot fit an existing category.

For every importer also record:

- whether it is live under current accepted execution paths;
- whether a later migration slice owns its eventual responsibility;
- whether S10 can migrate it directly or must preserve it through a compatibility boundary;
- whether its behavior depends on import order or `sys.path` precedence.

The result must be reproducible from repository state, not hand-listed from memory.

### C. Bootstrap and import-side-effect map

Document everything that happens merely by importing `foundry_common`, including at minimum:

- `sys.path` mutation;
- package/bootstrap path derivation;
- `ProjectPaths` construction;
- path aliases/global constants;
- imported permanent modules;
- environment sensitivity;
- global object or regex construction;
- any filesystem read;
- any import-time failure mode;
- precedence assumptions between `src`, `experiments`, installed packages, and current working directory.

Separate:

1. **domain semantics**, from
2. **legacy loose-script composition/bootstrap behavior**.

Do not recommend moving loose-script bootstrap behavior into permanent reusable libraries merely because it is currently convenient.

### D. Duplicate/equivalence census

Identify every `foundry_common` behavior that already appears to have a permanent implementation elsewhere.

For each pair, classify it as:

- exact delegation;
- compatibility wrapper;
- differential duplicate;
- semantically divergent duplicate;
- legacy-only behavior with no permanent owner yet.

Compare behavior, not names.

Where practical, perform **read-only differential measurements** against fixtures or the full corpus to establish whether two implementations really agree. Record exact commands, populations, and mismatches.

Do not “fix” mismatches.

### E. Ownership classification

Every live symbol must land in exactly one planning category:

1. `PERMANENT_OWNER_EXISTS`
2. `PERMANENT_OWNER_NEEDS_LIFT`
3. `LEGACY_COMPOSITION_BOUNDARY`
4. `DELETE_AFTER_CALLER_MIGRATION`
5. `BLOCKED_ARCHITECTURE_DECISION_REQUIRED`

No miscellaneous sixth bucket.

For every proposed permanent destination, verify:

- dependency direction remains acyclic;
- permanent library code does not rediscover repository root;
- path ownership remains with `mtj_foundry.paths.ProjectPaths`;
- process-exit/printing CLI semantics do not leak into reusable libraries;
- corpus/oracle semantics remain with accepted owners;
- no permanent package module imports `experiments`;
- no S11–S15 responsibility is pulled forward merely to make S10 easy;
- AQ4 remains PAUSED;
- Bridge v0 remains PARKED_UNUSED;
- Step6 remains not started;
- no authority publication or merge occurs.

If one symbol cannot be assigned honestly under current architecture, mark it blocked. Do not invent a new service or layer to make the table look complete.

### F. Risk register

Rank importer/symbol clusters by migration risk.

At minimum assess:

- corpus raw-vs-gated semantics;
- exact card-name resolution and ambiguity handling;
- Oracle/card-face behavior;
- self-reference normalization;
- DET role helpers;
- modal/die/level structural parsing;
- path/config aliases;
- artifact/output helpers;
- `halt()`/process-exit behavior;
- `sys.path` and loose-script bootstrap;
- duplicated permanent/legacy implementations;
- later-slice callers that must remain compatible.

For each high-risk cluster state the concrete failure that could occur if S10 migrates it incorrectly.

### G. S10 behavioral-conservation design

Design the future S10 acceptance strategy **before implementation**.

For each symbol/importer family specify the strongest practical observation method, such as:

- differential invocation old vs permanent implementation;
- fixture parity;
- full-corpus comparison;
- exact exception/error/exit-code parity at the legacy boundary;
- clean installed-package importability with repository absent from `PYTHONPATH`;
- tracked-state purity;
- exact path-value comparison;
- output hash/byte comparison where output stability is contractual;
- known-debt preservation where a later slice owns the defect.

Do not design tests that can pass merely because both old and new code share the same broken helper.

### H. Negative-control / falsification design

The acceptance design must demonstrably be capable of catching at least these failure classes:

- one importer silently remains dependent on `foundry_common` after S10;
- one symbol is copied into a second permanent owner instead of delegated;
- a permanent module imports `experiments`;
- repository-root derivation reappears outside `ProjectPaths` / composition boundary;
- `halt()`-style process exit leaks into permanent library code;
- a path alias changes value;
- a caller switches raw-vs-gated corpus semantics;
- exact-name ambiguity behavior changes;
- modal/DET preprocessing semantics drift during relocation;
- import order or `sys.path` precedence becomes behaviorally significant;
- a later-slice responsibility is accidentally pulled into S10.

For each control explain **what mutation would be injected** and **which guard/measurement must fail**.

## Evidence standards

Every important claim must be tied to repository evidence.

Record:

- exact accepted commit measured;
- exact planning/evidence branch commit;
- exact files inspected;
- exact census/search commands or scripts;
- exact counts/populations;
- discrepancies and unresolved cases;
- whether a statement is FACT, INFERENCE, RECOMMENDATION, or DECISION REQUIRED.

Do not silently turn architectural preference into measured fact.

Do not use current implementation success as the only criterion for choosing acceptance tests.

## Required durable deliverables

Create a compact but complete evidence package under a dedicated preflight/evidence location on the documentation branch. Suggested paths:

- `docs/architecture/preflight/S10-FOUNDRY-COMMON-PREFLIGHT-RESULT.md`
- `docs/architecture/preflight/S10-FOUNDRY-COMMON-SYMBOL-MAP.csv`
- `docs/architecture/preflight/S10-FOUNDRY-COMMON-IMPORTER-SYMBOL-MATRIX.csv`
- `docs/architecture/preflight/S10-FOUNDRY-COMMON-DUPLICATE-REGISTER.csv`
- `docs/architecture/preflight/S10-FOUNDRY-COMMON-DRAFT-WORKER-CONTRACT.md`

JSON may be used instead of or alongside CSV where it improves reproducibility.

The result document must include:

1. executive finding;
2. accepted head measured;
3. measured live-symbol count and definition of that count;
4. importer count and classifications;
5. bootstrap/side-effect findings;
6. ownership-category totals;
7. duplicate/equivalence findings;
8. highest-risk migration clusters;
9. unresolved blockers/decisions;
10. acceptance-test design;
11. negative-control design;
12. exact relationship to future S10;
13. explicit statement that **no S10 implementation was performed or authorized**.

The candidate Worker contract must be marked prominently:

**DRAFT / NOT AUTHORIZED / MANAGER REVIEW REQUIRED**

It should be bounded from measured evidence, not copied from old S10 assumptions.

## Git / repository constraints

- Do not edit `experiments/foundry_common.py`.
- Do not edit any runtime/package source.
- Do not move any caller.
- Do not create permanent APIs.
- Do not delete compatibility bootstrap.
- Do not update baselines or generated authority state.
- Do not write to R2 or perform authority succession.
- Do not modify AQ4.
- Do not use Bridge v0.
- Do not start Step6.
- Do not merge.
- Do not alter active implementation PRs.
- Do not start S11, S12, S13, S14, or S15 work.
- Do not perform S16A or S16B work in this session.

Read-only measurement scripts may be created transiently outside tracked source or under an evidence-only area if needed, but they must not become runtime dependencies. If committed for reproducibility, label them explicitly as preflight measurement tools and keep them isolated from production/import paths.

## STOP conditions

STOP rather than widening scope if:

- live accepted head makes the old 39-symbol premise materially false and accepted history cannot explain why;
- a live symbol has no defensible owner under current law;
- ownership would require changing a ratified semantic rule;
- a current importer requires a later-slice responsibility and cannot be preserved through a compatibility boundary;
- a proposed permanent destination creates a dependency cycle;
- a permanent solution requires repository-root rediscovery;
- the analysis depends on untracked generated/runtime state that cannot be reconstructed or proven;
- the only way to produce the evidence package would be to mutate runtime source;
- durable Issue #1 state changes during the session in a way that conflicts with this task.

A STOP is a successful preflight outcome if it identifies the exact evidence boundary and smallest decision needed.

## Completion bar

Objective 1 is COMPLETE only if a later Manager can write the S10 implementation contract without asking a Worker to rediscover:

- what `foundry_common` exposes and what is actually live;
- every tracked importer and the exact subset it consumes;
- import/bootstrap side effects;
- which behaviors already have permanent owners;
- where every remaining responsibility belongs;
- which compatibility behavior must remain temporarily;
- how S10 can prove semantic and operational conservation;
- what negative controls prove the guards are real;
- what unresolved decision, if any, prevents safe implementation.

## Durable publication

If COMPLETE:

1. commit only the evidence/preflight artifacts to the dedicated evidence branch;
2. push that branch;
3. do **not** open or merge an implementation PR;
4. add one concise Issue #1 comment clearly labeled **NON-EXECUTING PREFLIGHT RESULT** containing:
   - objective: `1/5`;
   - accepted head measured;
   - evidence branch;
   - evidence commit SHA;
   - measured live-symbol count;
   - measured importer count;
   - status `COMPLETE`;
   - blockers/decisions count;
   - statement `implementation_authorized: false`;
   - statement `next: MANAGER_REVIEW`.

If STOP:

1. preserve whatever evidence is already reliable on the evidence branch if doing so does not violate the STOP reason;
2. add one concise Issue #1 comment clearly labeled **NON-EXECUTING PREFLIGHT STOP** with exact reason/evidence boundary;
3. do not improvise a workaround;
4. do not start another objective.

Do not emit `T`, `X`, `V`, or `K` protocol records for this preflight unless the Manager has separately and durably authorized that protocol for this task. This prompt does not do so.

## Final response to Captain

Keep your final chat response short. Report only:

- `OBJECTIVE 1 PREFLIGHT COMPLETE` or `OBJECTIVE 1 PREFLIGHT STOP`;
- accepted head measured;
- evidence commit/branch if created;
- Issue #1 comment ID if created;
- one-line blocker summary if STOP.

Do not claim S10 is implemented, accepted, or authorized.
