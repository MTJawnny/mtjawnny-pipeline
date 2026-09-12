# Foundry Preflight Objectives 1–5

Status: **PLANNED / NON-EXECUTING**  
Created: 2026-09-11  
Planning branch: `cleanup/obsolete-doc-quarantine-2026-09-11`  
Repository authority: live durable GitHub state, especially Issue #1  
Accepted implementation state at plan creation: `9f92039eb9c7132a351576c31472eb30a2957a67`  
Standing strategy at plan creation: `MIGRATION_FIRST`  
Standing controls: `{AQ4:P, BRIDGE0:U, STEP6:N, MERGE:N}`

## Purpose

Use otherwise-idle Worker capacity to reduce uncertainty before the remaining migration and post-migration semantic work. These are **preflight / evidence tasks**, not implementation slices. They may produce durable research, censuses, matrices, benchmark specifications, candidate Worker contracts, and architecture evidence. They do not authorize source-code mutation, migration advancement, S16 implementation, merge, publication, or authority succession.

The five objectives are intentionally split so each receives a **fresh Claude Code session** with a narrow context window and an independently reviewable result.

## Objective sequence

1. **S10 `foundry_common` dependency/preflight map**  
   Plan: `docs/architecture/S10-FOUNDRY-COMMON-PREFLIGHT-PLAN.md`

2. **S16A adversarial card-reading gold suite preflight**  
   Plan: `docs/architecture/S16A-ADVERSARIAL-GOLD-SUITE-PREFLIGHT-PLAN.md`

3. **S16A parser-seam audit preflight**  
   Plan: `docs/architecture/S16A-PARSER-SEAM-AUDIT-PREFLIGHT-PLAN.md`

4. **S15 deletion-readiness preflight**  
   Plan: `docs/architecture/S15-DELETION-READINESS-PREFLIGHT-PLAN.md`

5. **S16B gameplay-DNA thesaurus preflight**  
   Plan: `docs/architecture/S16B-GAMEPLAY-DNA-PREFLIGHT-PLAN.md`

## Fresh-session law

Every objective is run in a fresh Claude Code session. A session must not inherit repository facts from a prior Claude conversation. It must independently recover live state from GitHub/repository evidence.

At the beginning of each session:

1. Read root `CLAUDE.md`.
2. Read GitHub Issue #1 and identify the latest valid Manager checkpoint `K`.
3. Resolve the accepted implementation head `h` and active task `a` from durable state.
4. Verify that the planned objective is still applicable and has not been superseded by later accepted work.
5. Treat any expected hashes/counts in these plans as discovery anchors only; live measured state wins.
6. STOP on unexplained state drift rather than silently rebasing the objective.

## Branch and mutation boundary

These plans are preserved on the cleanup/architecture branch because they are planning evidence and must not perturb the accepted migration chain.

For future objective sessions:

- the **subject under study** is the then-current accepted implementation state unless the plan explicitly requires the cleanup branch;
- source/code analysis is read-only by default;
- no accepted implementation ref may move;
- no active migration PR may be amended by a preflight task;
- no code fix may be smuggled into a research result;
- if a durable result is committed, it must live on a documentation/evidence branch explicitly separated from the accepted implementation branch;
- Worker PASS does not authorize implementation.

## Relationship to S10–S15

The standing migration sequence remains authoritative. At plan creation, Issue #1 records S9 accepted and no active task. The intended remaining sequence is:

- S10 — dissolve `foundry_common` / migrate its live dependency surface;
- S11 — codebook/store/membership move;
- S12 — authority/transport split;
- S13 — operator/CLI/pilot ownership move and command repair;
- S14 — AQ4/evaluation freeze relocation;
- S15 — archive/delete/`.gitignore`/legacy `experiments/` retirement.

Objectives 2, 3, and 5 are **post-S15 product preflights** and may be researched now only because they do not alter implementation. Objective 4 prepares S15 but must be revalidated against the actual accepted pre-S15 head before destructive action.

## Relationship to S16A and S16B

Durable Captain direction separates the future semantic work into:

- **S16A — Oracle semantic parse / card-reading precision**;
- **S16B — functional thesaurus / gameplay DNA**.

S16A must establish trustworthy semantic representation before S16B can treat semantic coordinates as reliable retrieval evidence. Objective 2 and Objective 3 prepare S16A. Objective 5 prepares S16B without bypassing the S16A prerequisite.

## Cross-objective deliverable rules

Every preflight result should contain:

- exact repository head(s) measured;
- exact files/modules/documents inspected;
- method and search/census procedure;
- measured populations, not only examples;
- unresolved cases and explicit uncertainty;
- negative controls or falsification attempts where applicable;
- provenance for external research;
- a clear separation among fact, inference, recommendation, and Captain decision;
- an implementation-neutral acceptance contract draft where useful;
- explicit non-goals and STOP conditions.

No preflight should tune its evidence to make the current implementation look good. Benchmarks and gold cases should be selected independently of current parser/retriever success whenever practical.

## Completion definition for the five-preflight program

The program is complete when five independently reviewable evidence packages exist such that a later Manager can:

1. issue S10 with a mechanically grounded symbol/importer map;
2. issue S16A gold-suite work without inventing adversarial cases during implementation;
3. issue S16A parser consolidation from a measured seam register rather than intuition;
4. issue S15 with a setwise deletion/conservation matrix and explicit blockers;
5. issue S16B with a provenance-bearing external gameplay-DNA benchmark and vocabulary methodology.

None of those later implementation tasks are authorized merely by completing these preflights.
