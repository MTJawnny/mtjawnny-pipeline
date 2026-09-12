# S10 `foundry_common` preflight result — STOP

**Status:** NON-EXECUTING PREFLIGHT STOP  
**Objective:** 1/5  
**Date:** 2026-09-11  
**Implementation authorized:** false  
**S10 implementation performed:** none

## Executive finding

**STOP.** The live accepted tree contains a current compatibility contract in which `experiments/foundry_shape_extractor.py` injects six card-text rules from `experiments/foundry_common.py` into the permanent `mtj_foundry.mtg.shapes.delivery.CardTextRules` substrate. The permanent substrate explicitly states that the permanent home of those shared card-text primitives is to be decided by a **later migration slice**. Four of the six (`is_mode_line`, `_MODAL_HEADER_RE`, `_ROLL_INSTRUCTION_RE`, `_DIE_ROW_RE`) have no ratified permanent owner in the accepted tree. Assigning them to `oracle_text`, `mtg.shapes.delivery`, or a new shared text/preprocessing module would therefore make an architecture/ownership decision rather than report an existing one.

The Objective-1 prompt says to STOP if a live symbol has no defensible owner under current law and not to invent a new service/layer merely to make the ownership table complete. That condition is met. The full 39-symbol / all-importer census was therefore **not continued past this boundary**. No count is claimed for the complete live symbol surface or importer population in this STOP artifact.

## 1. Durable bootstrap facts

- **FACT:** Latest accepted migration checkpoint in GitHub Issue #1 is `K-20260911-EXPERIMENTS-MIGRATION-S9-ACCEPTED-RECOVERY` (Issue #1 comment `5640693531`).
- **FACT:** Accepted implementation head `h` is `9f92039eb9c7132a351576c31472eb30a2957a67`.
- **FACT:** Active task is `a: 0`.
- **FACT:** Strategy remains `MIGRATION_FIRST`.
- **FACT:** Standing controls remain AQ4 paused, Bridge v0 parked/unused, Step6 not started, merge not authorized.
- **FACT:** No later S10 T/X/V/K was found; S10 has not been accepted, superseded, or partially authorized.
- **FACT:** Root `CLAUDE.md` was read from the accepted head before substantive analysis.
- **FACT:** The planning documents were read from `cleanup/obsolete-doc-quarantine-2026-09-11`.
- **FACT:** Planning branch head at evidence-branch creation was `fcb11e19296209aecac4c8b3526be39bcce0196a`.
- **FACT:** `fcb11e1...` is exactly one commit beyond planning checkpoint `9d949fc9d577b4b44240329fc093144f6003280d`; that commit adds only `docs/architecture/OBJECTIVE-1-FRESH-CLAUDE-PREFLIGHT-PROMPT.md`.
- **FACT:** Comparison of accepted `h` to the planning branch showed documentation/planning changes only; no runtime/package source change contaminated the accepted-source census.

## 2. Accepted source measured

Accepted implementation source examined at exact commit:

`9f92039eb9c7132a351576c31472eb30a2957a67`

Key tracked files inspected at that exact ref:

- `CLAUDE.md`
- `refoundation/PACKAGE-EXECUTION-CONTRACT.yaml`
- `refoundation/ROADMAP.md`
- `refoundation/ACTIVE-PHASE.yaml`
- `experiments/foundry_common.py`
- `experiments/foundry_shape_extractor.py`
- `src/mtj_foundry/paths.py`
- `src/mtj_foundry/corpus.py`
- `src/mtj_foundry/oracle_text.py`
- `src/mtj_foundry/infra/artifact.py`
- `src/mtj_foundry/mtg/text_match.py`
- `src/mtj_foundry/mtg/shapes/delivery.py`
- `src/mtj_foundry/mtg/shapes/locality.py`
- `tests/refoundation/test_layout_delegation.py`
- `tests/refoundation/test_oracle_text_capability.py`

Planning documents inspected:

- `docs/architecture/PREFLIGHT-OBJECTIVES-1-5-2026-09-11.md`
- `docs/architecture/S10-FOUNDRY-COMMON-PREFLIGHT-PLAN.md`

## 3. Import/bootstrap facts established before STOP

- **FACT:** Importing `foundry_common` derives `_BOOTSTRAP_ROOT` from `__file__`, prepends `<root>/src` to `sys.path`, constructs `ProjectPaths.for_root(_BOOTSTRAP_ROOT)`, and then prepends the legacy experiments path to `sys.path`.
- **FACT:** Its repository-relative path aliases are derived from the permanent path owner, `mtj_foundry.paths.ProjectPaths`.
- **FACT:** The package execution contract still declares this loose-script bootstrap a transitional compatibility site. Installing `mtj_foundry` alone does not retire legacy sibling-import bootstrap behavior.
- **FACT:** `foundry_common.write_json` already delegates to permanent owner `mtj_foundry.infra.artifact.write_json`; the permanent module documents 43 legacy callers and byte-level compatibility as a contract.
- **FACT:** Corpus loading/gating/face projection in `foundry_common` already delegates substantial work to `mtj_foundry.corpus`, with legacy `halt()` adapting raised library errors to process exit.
- **FACT:** `mtj_foundry.oracle_text` is pure and permanently owns a separate oracle-normalization capability. Its self-reference contract is not identical to the DET canonicalizer in `foundry_common`; the latter implements additional CR 201.5c shortened-name behavior and therefore cannot be declared an exact delegation merely because both concern self-reference.

## 4. Exact blocker boundary

`experiments/foundry_shape_extractor.py` constructs:

```python
_delivery.use_card_text_rules(_delivery.CardTextRules(fc, {
    "full_oracle_text": "full_oracle_text",
    "canonicalize_self_reference": "canonicalize_self_reference",
    "is_mode_line": "is_mode_line",
    "modal_header_re": "_MODAL_HEADER_RE",
    "roll_instruction_re": "_ROLL_INSTRUCTION_RE",
    "die_row_re": "_DIE_ROW_RE",
}))
```

`src/mtj_foundry/mtg/shapes/delivery.py` declares the same six names as `CardTextRules.REQUIRED`, receives them by injection rather than importing legacy code, and says their permanent home is decided by a later migration slice. It also requires lookup from the provider **at call time**, because accepted negative-control behavior replaces the CARDNAME canonicalizer dynamically; snapshotting these values at installation time is a known behavioral defect.

The same legacy boundary states that nineteen legacy callers depend on its no-argument forms. The injected rules are therefore live compatibility surface, not dead implementation detail.

### Ownership result for the blocker cluster

| Live common symbol | Planning result | Reason |
|---|---|---|
| `full_oracle_text` | `PERMANENT_OWNER_NEEDS_LIFT` | corpus owns face projection but no exact permanent full-text facade was established here |
| `canonicalize_self_reference` | `PERMANENT_OWNER_NEEDS_LIFT` | `oracle_text.normalize_self_references` is related but not behaviorally identical to the DET CR-201.5c canonicalizer |
| `is_mode_line` | `BLOCKED_ARCHITECTURE_DECISION_REQUIRED` | shared structural rule used by DET preprocessing and shapes; accepted permanent substrate deliberately declines ownership |
| `_MODAL_HEADER_RE` | `BLOCKED_ARCHITECTURE_DECISION_REQUIRED` | injected structural grammar primitive; no ratified permanent owner |
| `_ROLL_INSTRUCTION_RE` | `BLOCKED_ARCHITECTURE_DECISION_REQUIRED` | injected CR-706 table-structure primitive; no ratified permanent owner |
| `_DIE_ROW_RE` | `BLOCKED_ARCHITECTURE_DECISION_REQUIRED` | injected CR-706 row primitive; no ratified permanent owner |

**DECISION REQUIRED:** choose and ratify the permanent ownership boundary for the shared DET/shape structural preprocessing primitives, without creating a dependency cycle or pulling later-slice responsibilities forward. Candidate placements were **not** selected by this preflight because doing so would exceed the evidence-only task.

## 5. Why this is a STOP, not a recommendation disguised as fact

The accepted architecture establishes several hard constraints:

- permanent libraries may not rediscover repository root;
- `ProjectPaths` remains the repository-layout owner;
- permanent package code may not import `experiments`;
- process exit/printing belongs at composition/CLI boundaries rather than reusable libraries;
- `mtg.shapes.delivery` receives the unresolved card-text rules by injection specifically to avoid taking accidental ownership;
- no new service/layer should be invented merely to make the preflight table complete.

There is enough evidence to show the unresolved ownership is real, but not enough ratified law to choose among plausible homes without making architecture. Under the task's STOP conditions, continuing to fill an ownership table would be false precision.

## 6. Measurement/census scope actually completed

**FACT:** The six-symbol injection seam above was mechanically read from tracked source at exact accepted `h`.

**FACT:** Historical `tests/refoundation/test_layout_delegation.py` contains an older statement of `83` `foundry_common` importers, but that text predates later migration slices and also describes an import-time `tier_engine` edge that is no longer true. It is therefore **not accepted as the current importer count**.

**FACT:** The planning state's expected `39`-symbol surface is likewise treated only as a discovery anchor. This STOP occurred before an exact accepted-head AST census could be completed, so this artifact does **not** repeat `39` as a measured fact.

**FACT:** No untracked/generated/runtime state was used to make the STOP decision.

## 7. Reproducible repository reads

The evidence boundary was established with read-only GitHub operations against exact refs, equivalent to:

```text
GET Issue #1 comments and resolve latest valid K
GET /git/trees/9f92039eb9c7132a351576c31472eb30a2957a67?recursive=1
GET accepted-h versions of the files listed in §2
GET planning-branch versions of the two planning documents
COMPARE 9f92039eb9c7132a351576c31472eb30a2957a67..cleanup/obsolete-doc-quarantine-2026-09-11
COMPARE 9d949fc9d577b4b44240329fc093144f6003280d..cleanup/obsolete-doc-quarantine-2026-09-11
```

No source file, runtime artifact, baseline, authority object, AQ4 artifact, Bridge v0 state, Step6 state, implementation PR, or accepted ref was mutated.

## 8. What remains unmeasured because STOP fired

The following Objective-1 deliverables are intentionally incomplete and must not be inferred from this partial evidence package:

- complete current live-symbol count;
- complete tracked importer count;
- full importer × symbol matrix;
- complete duplicate/equivalence register;
- complete ownership totals;
- complete risk ranking;
- full S10 conservation/negative-control design;
- candidate S10 Worker implementation contract.

A draft Worker implementation contract is specifically **not** emitted: ownership of a live structural cluster is unresolved, so drafting implementation around an invented placement would violate the stop law.

## 9. Smallest decision needed to resume Objective 1

Ratify the permanent ownership boundary for the shared structural card-text rules consumed by both DET preprocessing and the shapes substrate, at minimum:

- `is_mode_line`
- modal-header recognition (`_MODAL_HEADER_RE` behavior)
- roll-instruction recognition (`_ROLL_INSTRUCTION_RE` behavior)
- die-row recognition (`_DIE_ROW_RE` behavior)

The decision should state whether these belong to an existing permanent capability or authorize a specifically bounded shared capability. It must preserve dependency direction and may not make permanent code import `experiments` or rediscover repository root.

After that decision, Objective 1 can resume its mechanical census and complete the remaining A-H evidence without implementing S10.

---

**Explicit conservation statement:** This preflight performed no S10 implementation and authorizes none. AQ4 remains paused. Bridge v0 remains parked/unused. Step6 remains not started. No merge, authority publication, baseline update, runtime-source change, S11-S16 work, or accepted-ref movement was performed.
