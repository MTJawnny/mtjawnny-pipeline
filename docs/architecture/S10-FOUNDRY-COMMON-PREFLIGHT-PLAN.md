# S10 `foundry_common` Preflight Plan

Status: **PLANNED / NON-EXECUTING**  
Objective: **1 of 5**  
Fresh Claude session: **REQUIRED**  
Implementation authorization: **NONE**

## Mission

Produce a complete, mechanically grounded map of the live `experiments/foundry_common.py` dependency surface before S10 implementation begins.

The goal is to make S10 a bounded migration of known responsibilities rather than a discovery exercise performed while code is being moved.

At plan creation, durable state identifies S10 as the future dissolution of `foundry_common` and refers to a **39-symbol migration surface**. That count is an expected discovery anchor only. The preflight must re-census the live accepted head and explain any difference.

## Why this deserves its own preflight

`foundry_common` historically acted as a shared legacy foundation. Even after earlier refoundation slices removed major upward dependencies, it still combines several different responsibility classes:

- path/config aliases supplied by `ProjectPaths`;
- legacy process-exit behavior;
- corpus loading and name resolution;
- Oracle/card-face helpers;
- self-reference normalization;
- DET-pattern role helpers;
- modal/die/level structural parsing helpers;
- output/batch path helpers;
- artifact helpers and legacy compatibility behavior;
- import/bootstrap behavior needed by loose scripts.

Migrating such a module by filename is unsafe. S10 must migrate **responsibilities and callers**, not merely copy functions elsewhere.

## Live-state bootstrap

The session must first recover the latest valid Issue #1 checkpoint and accepted head. It must confirm:

- strategy remains compatible with S10 preflight;
- S10 has not already been accepted or superseded;
- no active Worker task conflicts with the audit;
- the accepted source under study is exact and clean.

If S10 has already landed, STOP and report that this plan requires rebasing into a post-S10 conservation audit rather than pretending the old task still exists.

## Required census

### 1. Symbol census

Mechanically enumerate every externally reachable name from `foundry_common` that is referenced by tracked repository code, tests, scripts, commands, or contracts.

For each symbol record:

- symbol name;
- kind: constant / function / class / regex / private helper nevertheless imported / module alias;
- defining lines;
- direct imports/callers;
- indirect contract consumers where known;
- whether import-time initialization is required;
- whether it reads repository paths, tracked config, generated state, environment, or process state;
- whether it writes, exits, prints, mutates globals, or has another side effect;
- existing permanent equivalent, if any;
- intended permanent owner if obvious from ratified architecture;
- confidence/evidence for that ownership assignment.

Do not infer “unused” from lack of `from foundry_common import X` alone. Search module-qualified access (`fc.X`), dynamic imports, subprocess invocations, command files, tests, and documented execution paths.

### 2. Importer census

Enumerate every tracked importer of `foundry_common` and classify the importer by responsibility:

- Gate/check;
- reporter/census;
- codebook/membership mutation;
- pipeline/batch tooling;
- operator/CLI;
- authority/transport;
- AQ4;
- historical/one-off;
- test/negative control;
- other.

For each importer record the exact subset of symbols consumed. This is the matrix S10 implementation should migrate against.

### 3. Bootstrap and import-side-effect census

Document every behavior that happens merely by importing `foundry_common`, including:

- `sys.path` changes;
- `ProjectPaths` creation;
- path aliases;
- imported permanent modules;
- environment sensitivity;
- any global object creation;
- any dependency that can fail at import time.

Separate “required because loose legacy scripts are not installed packages” from actual domain semantics.

### 4. Duplicate-owner census

Identify every `foundry_common` behavior that already has a permanent implementation elsewhere and determine whether the legacy function is:

- exact delegation;
- compatibility wrapper;
- differential duplicate;
- semantically divergent duplicate;
- legacy-only behavior with no permanent owner yet.

Any apparent duplicate must be compared behaviorally, not only by name.

## Ownership classification

Every live symbol must land in exactly one planning category:

1. **PERMANENT_OWNER_EXISTS** — migrate callers to an already accepted permanent API.
2. **PERMANENT_OWNER_NEEDS_LIFT** — reusable semantics belong in an identified permanent module but have not yet been lifted.
3. **LEGACY_COMPOSITION_BOUNDARY** — process exit, printing, repository-default selection, loose-script bootstrap, or similar behavior that should remain outside reusable libraries until caller retirement.
4. **DELETE_AFTER_CALLER_MIGRATION** — no independent semantic owner required once callers move.
5. **BLOCKED / ARCHITECTURE DECISION REQUIRED** — ownership cannot be assigned without changing law or creating a new cross-layer dependency.

No sixth “miscellaneous” bucket is allowed. Ambiguity must be explicit.

## Architecture checks

For every proposed permanent destination verify:

- dependency direction remains acyclic;
- permanent library code does not rediscover repository root;
- process-exit semantics do not leak into reusable libraries;
- path ownership remains with `mtj_foundry.paths.ProjectPaths`;
- corpus semantics remain with the accepted corpus/oracle owners;
- no permanent package module imports legacy `experiments` code;
- no S11–S15 work is pulled forward merely because a caller is inconvenient;
- AQ4 and Bridge remain untouched.

## Behavioral conservation map

For each migrated symbol or importer family, specify how S10 can prove behavior is unchanged. Candidate methods include:

- differential invocation old vs permanent implementation;
- fixture parity;
- full-corpus comparison;
- exact exception/exit-code parity at legacy boundary;
- importability from a clean installed environment;
- tracked-state purity checks;
- output byte/hash comparison where outputs are contractually stable;
- known-debt preservation where later slices own the defect.

The preflight does **not** run implementation-dependent acceptance tests. It designs and, where possible read-only, validates that the proposed tests can observe the relevant behavior.

## Negative controls / falsification

The preflight must show that the future S10 acceptance strategy would catch at least these failure classes:

- one importer silently left on `foundry_common`;
- one symbol copied into a second permanent owner rather than delegated;
- a permanent module starts importing `experiments`;
- repository-root derivation reappears outside `ProjectPaths`/composition boundary;
- `halt()`-style process exit leaks into permanent library code;
- a path alias changes value;
- a caller changes raw-vs-gated corpus semantics;
- a caller loses exact-name ambiguity behavior;
- modal/DET preprocessing semantics drift during relocation;
- import order or `sys.path` precedence becomes behaviorally significant.

## Required deliverables

The fresh session should produce a durable evidence package containing at minimum:

1. **Symbol map** — all live `foundry_common` symbols and ownership classification.
2. **Importer × symbol matrix** — exact dependency surface.
3. **Bootstrap/side-effect map**.
4. **Duplicate/equivalence register** — old vs permanent behavior.
5. **Risk register** — high-risk importer clusters and reasons.
6. **S10 acceptance-test design** — conservation checks and negative controls.
7. **Candidate S10 Worker contract** — bounded scope derived from evidence, clearly marked DRAFT / NOT AUTHORIZED.
8. **STOP list** — unresolved decisions that must be settled before implementation.

Machine-readable CSV/JSON adjuncts are encouraged for the symbol/importer matrix if they improve reproducibility.

## Non-goals

This preflight must not:

- edit `foundry_common.py`;
- move any caller;
- create permanent APIs;
- delete compatibility bootstraps;
- start S11 codebook/store/membership work;
- start S12 authority work;
- start S13 CLI/operator work;
- start S14 AQ4 relocation;
- start S15 deletion;
- update baselines;
- publish authority or R2 state;
- merge anything.

## STOP conditions

STOP rather than widening scope if:

- live accepted head differs in a way that makes the 39-symbol premise materially false and the difference cannot be explained by accepted history;
- a symbol has no defensible permanent owner under current architecture;
- migrating one symbol requires changing a ratified semantic rule;
- a current importer requires a later-slice responsibility and cannot be preserved through a compatibility boundary;
- permanent dependency direction would become cyclic;
- the preflight uncovers untracked generated/runtime state required to understand a live contract.

## Completion bar

Objective 1 is complete when a later Manager can write the S10 implementation contract without asking Claude to rediscover:

- what `foundry_common` exports;
- who consumes each export;
- where each responsibility belongs;
- which compatibility behavior must remain temporarily;
- how to prove semantic and operational conservation;
- which unresolved decisions would make implementation unsafe.
