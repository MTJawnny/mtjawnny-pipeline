# Objective 1 Resume Prompt — after card-text ownership decision

Status: **DRAFT / NOT AN ACTIVE T / NON-EXECUTING**  
Purpose: fresh Claude Code preflight session when Claude becomes available  
Implementation authorization: **NONE**

---

You are a fresh Claude Code preflight investigator for the MTJawnny Foundry repository refoundation.

Repository:

`MTJawnny/mtjawnny-pipeline`

Use GitHub/repository state directly. Durable GitHub state is authority. Do not rely on this prompt's expected hashes, prior Claude memory, prior ChatGPT memory, chat scrollback, or historical counts as repository truth.

## Roles and law

- Captain = user.
- Manager = ChatGPT.
- Worker / preflight investigator = you, Claude Code.
- Durable Manager↔Worker control plane = GitHub Issue #1.
- Governing principle = `PRESERVE TRUTH, NOT PLUMBING`.
- Evidence never self-authorizes implementation.
- Never merge.
- Do not begin S10 implementation in this task.

## Fresh-session bootstrap

Before substantive analysis:

1. Read root `CLAUDE.md`.
2. Read GitHub Issue #1 and resolve the latest valid `K`.
3. Resolve accepted implementation head `h` and active task `a` from that checkpoint.
4. Confirm there is no newer accepted S10 work and no active task that conflicts with this preflight.
5. Read the current versions of:
   - `docs/architecture/PREFLIGHT-OBJECTIVES-1-5-2026-09-11.md`
   - `docs/architecture/S10-FOUNDRY-COMMON-PREFLIGHT-PLAN.md`
   - `docs/architecture/preflight/S10-FOUNDRY-COMMON-PREFLIGHT-RESULT.md`
   - `docs/architecture/S10-CARD-TEXT-OWNERSHIP-DECISION-2026-09-11.md`
6. Read the accepted S7 evidence relevant to the `CardTextRules` by-value failure and call-time repair, including the S7 accepted checkpoint/review.
7. Inspect the exact accepted source; do not analyze the architecture/evidence branch as if it were accepted implementation.

Discovery anchors only, not authority:

- accepted head when the ownership decision was recorded: `9f92039eb9c7132a351576c31472eb30a2957a67`
- prior Objective-1 STOP evidence commit: `b360bced4ccd2ce250d283d665b4df08b30256c2`
- earlier planning anchor: a 39-symbol `foundry_common` migration surface

If live durable state differs, live state wins. Explain the drift. STOP only if the objective is genuinely superseded or the difference prevents a truthful census.

## Mission

Resume Objective 1 from the point where the prior preflight correctly STOPped. The card-text ownership decision is now supplied; do not reopen it merely because another placement is imaginable.

Complete the mechanically grounded S10 `foundry_common` dependency/preflight map so a later Manager can issue a bounded implementation contract without rediscovering ownership, callers, side effects, or conservation requirements during migration.

This remains a **preflight/evidence task only**.

## Binding ownership direction for the previously blocked seam

Apply the Captain-approved decision as follows:

- `full_oracle_text(card)` → permanent corpus capability (`mtj_foundry.corpus`).
- DET-compatible self-reference canonicalization → permanent Oracle-text capability (`mtj_foundry.oracle_text`), but preserve it as a distinct behavioral contract from existing N2 normalization unless equivalence is separately proven and authorized.
- `is_mode_line` → Oracle-text structural recognition.
- modal-header recognition (`_MODAL_HEADER_RE` behavior) → Oracle-text structural recognition.
- roll-instruction recognition (`_ROLL_INSTRUCTION_RE` behavior) → Oracle-text structural recognition.
- die-row recognition (`_DIE_ROW_RE` behavior) → Oracle-text structural recognition.
- shapes/delivery owns semantic delivery/routing consequences of those observations, not duplicate structural definitions.
- DET preprocessing owns DET-specific synthetic scan representations; it may consume corpus/Oracle-text facts but is not itself neutral Oracle-text structure.

Apply the same ownership principle to mechanically adjacent live structural helpers such as Level/Class band recognizers if the accepted-head census shows they are live. Do not migrate or classify a symbol merely because it existed historically.

## S7 conservation requirement

Do not describe S7 as currently broken.

Historical fact to verify from durable evidence:

- the first S7 candidate injected card-text primitives by value;
- WB4 replaced `fc.canonicalize_self_reference` at runtime;
- the captured snapshot disarmed that substitution and WB4a/b/c failed;
- accepted S7 repaired this by resolving provider attributes at call time.

The future S10 design must preserve the **observable call-time substitution property**, not necessarily the `CardTextRules` plumbing.

Your S10 acceptance design must contain a negative control that would fail if the permanent route captured a stale self-reference implementation at import/setup time and thereby stopped a runtime substitution from reaching downstream consumers.

## Required work

### A. Complete symbol census

Mechanically enumerate every externally reachable/live `foundry_common` name referenced by tracked repository code, tests, scripts, commands, contracts, dynamic/module-qualified access, and documented executable paths.

For every symbol record:

- name and kind;
- definition location;
- exact live callers/importers;
- side effects / reads / writes / exits / globals / import-time behavior;
- existing permanent equivalent if any;
- behavioral relationship: exact delegation / compatibility wrapper / differential duplicate / divergent duplicate / legacy-only;
- ownership category from the S10 plan;
- proposed permanent owner when supported by accepted architecture and the ownership decision above;
- conservation proof and negative control.

Re-measure the expected `39`; do not repeat it as fact unless the accepted-head census produces it.

### B. Complete importer × symbol matrix

Enumerate every tracked `foundry_common` importer and the exact subset of symbols consumed.

Classify importers by responsibility, including:

- gate/check;
- reporter/census;
- codebook/membership mutation;
- pipeline/batch tooling;
- operator/CLI;
- authority/transport;
- AQ4/frozen benchmark;
- historical/one-off;
- test/negative control;
- other.

Do not count frozen/archive evidence as active executable code merely because bytes contain an old import.

### C. Bootstrap/import-side-effect map

Fully document `foundry_common` import-time behavior and the execution-contract consequences, including package-location bootstrap, legacy-sibling bootstrap, `ProjectPaths` creation, path aliases, globals, and failure paths.

Separate domain semantics from loose-script compatibility plumbing.

### D. Duplicate/equivalence register

Behaviorally compare every apparent legacy/permanent duplicate. Name similarity is not equivalence.

Pay particular attention to:

- corpus loading/gating/face projection;
- full-card text;
- DET self-reference canonicalization versus permanent N2 normalization;
- structural modal/die helpers;
- artifact JSON byte contract;
- DET role helpers;
- name resolution;
- any private symbol consumed across module boundaries.

### E. Ownership classification

Every live symbol must land in exactly one S10 planning category:

1. `PERMANENT_OWNER_EXISTS`
2. `PERMANENT_OWNER_NEEDS_LIFT`
3. `LEGACY_COMPOSITION_BOUNDARY`
4. `DELETE_AFTER_CALLER_MIGRATION`
5. `BLOCKED / ARCHITECTURE DECISION REQUIRED`

The card-text ownership decision removes the prior blocker; it does not ban new STOPs. If another live semantic concept truly lacks a defensible owner, identify the smallest unresolved decision rather than inventing a home.

### F. Ownership-bloat audit note

While doing the mechanical census, flag cases where a module appears to own a concept only because it is a high-fan-in consumer.

Do **not** widen this task into the later S16A parser-seam audit. Record candidates as an audit note unless they block S10.

Use this diagnostic question:

> Is this module the semantic owner of the concept, or merely the most visible consumer?

### G. Complete S10 conservation design

For every migration cluster define how the future implementation proves unchanged truth. Include where applicable:

- full-corpus differential;
- exact list/order/string equivalence;
- failure-path parity;
- path-value parity;
- installed-package importability;
- zero permanent imports from `experiments`;
- no new repository-root derivation;
- byte-level artifact parity;
- exact ambiguity behavior;
- modal/DET structural parity;
- call-time substitution preservation from S7;
- import-order / `sys.path` precedence negative controls.

### H. Draft future S10 Worker contract

After the evidence is complete, produce a bounded **DRAFT / NOT AUTHORIZED** S10 implementation contract.

The contract should normally stage work in this order, subject to your measured dependency graph:

1. lift/establish permanent owner APIs behind differential proof;
2. leave legacy compatibility facades delegating;
3. repoint `shapes.delivery` to permanent text owners without losing the S7 runtime-substitution property;
4. migrate remaining caller families according to the importer matrix;
5. prove no second semantic owner and no permanent `experiments` dependency;
6. retire `CardTextRules` compatibility injection only after it has zero required legacy role;
7. retire `foundry_common` pieces only after zero live caller proof and bootstrap prerequisites permit it;
8. run the entire contracted acceptance suite before any PASS claim.

Do not execute this draft contract.

## Required durable deliverables

Produce an evidence package containing at minimum:

1. complete symbol map;
2. complete importer × symbol matrix;
3. bootstrap/side-effect map;
4. duplicate/equivalence register;
5. ownership table;
6. ownership-bloat audit note;
7. risk register;
8. S10 conservation + negative-control design;
9. draft S10 Worker implementation contract, clearly `NOT AUTHORIZED`;
10. remaining STOP list, if any.

Prefer machine-readable CSV/JSON adjuncts for the symbol/importer matrices when useful.

If committing evidence, use a documentation/evidence branch separated from accepted implementation. Do not mutate the accepted implementation ref.

## Hard prohibitions

Do not:

- edit `experiments/foundry_common.py`;
- edit S7 implementation to "fix" the already-repaired by-value incident;
- move callers;
- create permanent APIs;
- remove `CardTextRules`;
- delete bootstraps;
- start S11–S15;
- start S16A/S16B implementation;
- consolidate N2 and DET self-reference semantics;
- change codebook, authority, baselines, CR inputs, or generated runtime state;
- resume AQ4;
- use Bridge v0;
- start Step6;
- merge anything.

## Completion bar

PASS the preflight only when a later Manager can write the real S10 implementation task without rediscovering:

- the complete live `foundry_common` surface;
- every consumer;
- every permanent/composition/archive destination;
- every bootstrap dependency;
- every behavior that must remain dynamic or byte-exact;
- every conservation proof and negative control;
- every unresolved decision.

A preflight PASS is evidence only. It authorizes no implementation.
