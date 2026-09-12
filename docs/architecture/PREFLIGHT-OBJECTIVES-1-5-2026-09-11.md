# Foundry Preflight Objectives 1–5

Status: **ACTIVE PLANNING PROGRAM / NON-IMPLEMENTING**  
Created: 2026-09-11  
Updated: 2026-09-12  
Current pickup: `docs/architecture/PREFLIGHT-PICK-UP-HERE.md`  
Repository authority: live durable GitHub state, especially Issue #1  
Standing strategy at plan creation: `MIGRATION_FIRST`  
Standing controls: `{AQ4:P, BRIDGE0:U, STEP6:N, MERGE:N}`

## Current progress

- **Objective 1 — S10 `foundry_common` dependency/preflight map:** ownership STOP explained and Captain-approved ownership direction recorded; full accepted-head symbol/importer census remains pending.
- **Objective 2 — S16A adversarial card-reading gold suite:** **COMPLETE EVIDENCE** on `preflight/s16a-gold-suite-2026-09-12` at `fc99f3bdf0503bd325f0b644771895c05940ad15`; Issue #1 result comment `5647127271`.
- **Objective 3 — S16A parser-seam audit:** **NEXT / READY FOR FRESH CHATGPT SESSION**. Routing branch: `preflight/objective3-parser-seam-2026-09-12`. Prompt: `docs/architecture/OBJECTIVE-3-FRESH-CHATGPT-PREFLIGHT-PROMPT.md`.
- **Objectives 4–5:** planned and unexecuted.

## Purpose

Use otherwise-idle research capacity to reduce uncertainty before remaining migration and post-migration semantic work. These are **preflight/evidence tasks**, not implementation slices. They may produce durable research, censuses, matrices, benchmark specifications, parser inventories, candidate implementation contracts, and architecture evidence. They do not authorize source-code mutation, migration advancement, S16 implementation, merge, publication, deployment, or authority succession.

## Captain direction for the current execution window

The original plan assumed each objective would be run in a fresh Claude Code session. The Captain later clarified that the point of the five-objective program is to use **fresh ChatGPT Manager-side sessions while Claude Code is unavailable**.

For this window:

- ChatGPT may execute Objectives 1–5 as non-implementing research/evidence work;
- each objective should still use a fresh session and independently recover durable state;
- the Worker-only result protocol in root `CLAUDE.md` does not convert ChatGPT into Claude; Manager-side sessions should post Manager evidence/result/checkpoint records instead;
- all source/runtime/package/parser/codebook/authority/AQ4 mutation remains forbidden unless a later durable task explicitly authorizes it.

The durable Captain direction is recorded on Issue #1; live GitHub state wins if later superseded.

## Objective sequence

### 1. S10 `foundry_common` dependency/preflight map

Plan: `docs/architecture/S10-FOUNDRY-COMMON-PREFLIGHT-PLAN.md`  
Ownership decision: `docs/architecture/S10-CARD-TEXT-OWNERSHIP-DECISION-2026-09-11.md`  
Resume prompt: `docs/architecture/OBJECTIVE-1-RESUME-PROMPT-AFTER-CARD-TEXT-OWNERSHIP.md`

Current state: ownership direction resolved; full census still pending. Objective 1 remains non-implementing.

### 2. S16A adversarial card-reading gold-suite preflight — COMPLETE EVIDENCE

Plan: `docs/architecture/S16A-ADVERSARIAL-GOLD-SUITE-PREFLIGHT-PLAN.md`

Completed evidence branch/head:

- branch: `preflight/s16a-gold-suite-2026-09-12`
- head: `fc99f3bdf0503bd325f0b644771895c05940ad15`
- Issue #1 result: `5647127271`

Durable evidence package under `docs/architecture/preflight/s16a/` includes:

- 66-family structural census;
- implementation-neutral gold schema;
- 33 development gold witnesses;
- 18-card deterministic unlabeled holdout;
- 18 named semantic negative controls;
- human-readable result, coverage matrix, unsupported/risk register, provenance register, and draft S16A acceptance contract marked NOT AUTHORIZED.

The benchmark universe is the accepted Foundry Gate #0 population: **32,557** cards from the pinned 38,233-record raw Oracle corpus; **5,676** nowhere-legal records are excluded. The pinned decompressed corpus SHA-256 is `5e47e1325a3987db745a941307080830696cbac2f6aa80d8f88f8a6dad90723c`.

Objective-2 benchmark membership/labels were selected without inspecting current parser output.

### 3. S16A parser-seam audit preflight — NEXT

Plan: `docs/architecture/S16A-PARSER-SEAM-AUDIT-PREFLIGHT-PLAN.md`  
Fresh ChatGPT prompt: `docs/architecture/OBJECTIVE-3-FRESH-CHATGPT-PREFLIGHT-PROMPT.md`

Mission: inventory every live place where accepted code independently interprets Oracle text or Oracle-derived structure; build a semantic concept-owner map; mechanically search for duplicated parsing; differentially measure overlapping implementations across complete applicable Gate #0 populations; classify seams S0–S5; reconcile historical incidents; and produce negative controls plus NOT AUTHORIZED canonicalization/ownership recommendations.

Objective 3 consumes Objective-2 census and development evidence as adversarial inputs, but **must not reveal or manufacture holdout labels** and must not let the witness list replace full mechanical interpreter discovery.

### 4. S15 deletion-readiness preflight

Plan: `docs/architecture/S15-DELETION-READINESS-PREFLIGHT-PLAN.md`

Planned. Must be revalidated against the actual future pre-S15 accepted head before destructive action.

### 5. S16B gameplay-DNA thesaurus preflight

Plan: `docs/architecture/S16B-GAMEPLAY-DNA-PREFLIGHT-PLAN.md`

Planned. S16A remains prerequisite semantic substrate work.

## Fresh-session law

Each objective should run in a fresh ChatGPT session during the current Captain-authorized window. A fresh session must not treat chat memory or prior model claims as repository truth.

At startup:

1. read GitHub Issue #1 and identify the latest valid `K`;
2. resolve accepted implementation head `h` and active task `a`;
3. read root `CLAUDE.md` at accepted `h` for repository law, then apply later durable Captain directions;
4. read `docs/architecture/PREFLIGHT-PICK-UP-HERE.md`;
5. read the selected objective plan and its fresh-session prompt;
6. inspect the exact accepted implementation state relevant to the objective;
7. treat expected hashes/counts as discovery anchors until reverified where present-tense accuracy matters;
8. STOP on unexplained drift rather than silently adapting the task.

## Branch and mutation boundary

- Subject under study is the current accepted implementation state unless the objective explicitly says otherwise.
- Source/code analysis is read-only.
- No accepted implementation ref may move.
- No active migration PR may be amended by a preflight.
- No implementation fix may be smuggled into research evidence.
- Durable preflight outputs belong on separate documentation/evidence branches.
- Manager-side preflight completion is evidence only and does not authorize implementation.

## Relationship to S10–S15

Standing migration sequence remains:

- S10 — dissolve `foundry_common` / migrate its live dependency surface;
- S11 — codebook/store/membership move;
- S12 — authority/transport split;
- S13 — operator/CLI/pilot ownership move and command repair;
- S14 — AQ4/evaluation freeze relocation;
- S15 — archive/delete/`.gitignore`/legacy `experiments/` retirement.

Objectives 2, 3, and 5 are post-S15 product preflights researched early only because they do not alter implementation. Objective 4 prepares S15.

## Relationship to S16A and S16B

- **S16A — Oracle semantic parse / card-reading precision**
- **S16B — functional thesaurus / gameplay DNA**

S16A must establish trustworthy semantic representation before S16B treats semantic coordinates as reliable retrieval evidence. Objectives 2 and 3 prepare S16A. Objective 5 prepares S16B without bypassing S16A.

The Objective-1 ownership direction is engineering architecture, not benchmark truth. Objective 2 supplies implementation-independent benchmark evidence. Objective 3 may inspect parser behavior because its explicit purpose is to measure parser topology and divergence, but it must keep evidence classification separate from implementation authorization.

## Cross-objective deliverable rules

Every preflight result should contain:

- exact repository head(s) measured;
- exact corpus/input identity when card-level measurement is used;
- exact files/modules/documents inspected;
- method and census/search procedure;
- measured populations, not anecdotes;
- unresolved cases and explicit uncertainty;
- negative controls/falsification attempts where applicable;
- provenance for external research;
- clear separation of fact, inference, recommendation, and Captain decision;
- an implementation-neutral acceptance/implementation contract draft where useful, marked NOT AUTHORIZED;
- explicit non-goals and STOP conditions.

## Completion definition

The five-preflight program is complete when independently reviewable evidence packages let a later Manager:

1. issue S10 from a mechanically grounded symbol/importer map;
2. issue S16A benchmark work from a precommitted adversarial gold suite;
3. issue S16A parser consolidation from a measured parser-seam register;
4. issue S15 from a setwise deletion/conservation matrix and explicit blockers;
5. issue S16B from a provenance-bearing gameplay-DNA research benchmark and vocabulary methodology.

None of those later implementation tasks is authorized merely by completing these preflights.
