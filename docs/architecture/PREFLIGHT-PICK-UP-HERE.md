# PREFLIGHT PICK UP HERE

Status: CURRENT PLANNING POINTER
Updated: 2026-09-11
Repository: MTJawnny/mtjawnny-pipeline

This file exists so a fresh Claude Code / Manager session can recover the five-objective preflight state even if root `CLAUDE.md` is not read automatically. It is a routing record, not implementation authority. Durable GitHub/repository state still wins; GitHub Issue #1 remains the Manager/Worker control plane.

## Current durable implementation anchor

At this planning update, the latest accepted implementation head remains:

`9f92039eb9c7132a351576c31472eb30a2957a67`

Standing controls remain:

`{AQ4: PAUSED, BRIDGE0: UNUSED, STEP6: NOT_STARTED, MERGE: NO}`

Re-resolve Issue #1 before acting. Do not assume these anchors are still current if later durable state exists.

## Five-objective preflight program

Master index:

`docs/architecture/PREFLIGHT-OBJECTIVES-1-5-2026-09-11.md`

### Objective 1 — S10 foundry_common dependency/preflight map

State: OWNERSHIP STOP EXPLAINED; ARCHITECTURE DIRECTION RECORDED; FULL CENSUS STILL TO RESUME

Initial STOP evidence:

- branch: `preflight/s10-foundry-common-map-2026-09-11`
- commit: `b360bced4ccd2ce250d283d665b4df08b30256c2`
- Issue #1 STOP comment: `5642641036`
- result: `docs/architecture/preflight/S10-FOUNDRY-COMMON-PREFLIGHT-RESULT.md`

Captain-approved ownership direction and S7 conservation record:

- branch: `architecture/s10-card-text-ownership-2026-09-11`
- decision: `docs/architecture/S10-CARD-TEXT-OWNERSHIP-DECISION-2026-09-11.md`
- Objective-1 resume prompt: `docs/architecture/OBJECTIVE-1-RESUME-PROMPT-AFTER-CARD-TEXT-OWNERSHIP.md`
- Issue #1 direction comment: `5644313159`

Important S7 distinction:

- the by-value CardTextRules injection was an INTERMEDIATE S7 defect, not accepted final S7 behavior;
- accepted S7 repaired it by resolving provider attributes at call time;
- future S10 may replace the injection plumbing, but MUST preserve the observable substitution property that WB4 protects;
- do not "fix S7" by editing accepted S7 code before the S10 replacement path is designed and proved.

Approved ownership direction:

- whole-card / face projection belongs to `mtj_foundry.corpus`;
- neutral printed Oracle-text structure and DET self-reference canonicalization belong to the Oracle-text capability, preserving non-equivalent policies until measured;
- `mtj_foundry.mtg.shapes.delivery` owns delivery/ability-shape consequences, not the shared recognition primitives merely because it consumes them;
- DET preprocessing owns DET-specific synthetic scan representations;
- one shared semantic observation gets one lowest sensible owner; consumers must not rederive it independently.

Objective 1 is NOT implementation-authorized. Its next Worker action is to resume the full accepted-head symbol/importer census and complete the remaining A-H preflight deliverables using this ownership law.

### Objective 2 — S16A adversarial card-reading gold-suite preflight

State: NEXT PRE-FLIGHT OBJECTIVE

Plan:

`docs/architecture/S16A-ADVERSARIAL-GOLD-SUITE-PREFLIGHT-PLAN.md`

Mission: create an implementation-independent, provenance-bearing adversarial card-reading benchmark before S16A parser implementation. It must measure structural families in the accepted corpus, select representative/adversarial witnesses independently of current parser success, define machine-readable semantic truth, include mutation-based negative controls, and reserve a holdout where practical.

Do not implement S16A parser code. Do not tune the gold suite to the current implementation.

### Objective 3 — S16A parser-seam audit

Plan:

`docs/architecture/S16A-PARSER-SEAM-AUDIT-PREFLIGHT-PLAN.md`

This is where the broader ownership-bloat/parser-duplication question is systematically audited. The known reminder-parser seam is a seed, not the whole scope.

### Objective 4 — S15 deletion-readiness preflight

Plan:

`docs/architecture/S15-DELETION-READINESS-PREFLIGHT-PLAN.md`

### Objective 5 — S16B gameplay-DNA thesaurus preflight

Plan:

`docs/architecture/S16B-GAMEPLAY-DNA-PREFLIGHT-PLAN.md`

## Startup rule even if CLAUDE.md was skipped

Before executing any objective:

1. Read this file and the named objective plan.
2. Read GitHub Issue #1 and resolve latest valid `K`, accepted head `h`, and active task `a`.
3. Verify the objective is still applicable and not superseded.
4. Inspect the exact accepted implementation state relevant to the objective.
5. Treat hashes/counts in planning docs as discovery anchors only.
6. STOP on unexplained drift or a requirement that would change semantic truth.
7. Preflight/evidence work never self-authorizes implementation or merge.

Root `CLAUDE.md` remains repository operating law and should be read. This file exists as redundant recovery routing, not as a replacement for it.
