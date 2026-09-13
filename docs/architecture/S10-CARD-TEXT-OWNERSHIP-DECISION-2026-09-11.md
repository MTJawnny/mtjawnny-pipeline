# S10 Card-Text Ownership Decision

Status: **CAPTAIN-APPROVED DIRECTION / NON-EXECUTING**  
Date: 2026-09-11  
Recorded by: Manager  
Decision source: Captain approval in the 2026-09-11 Manager session  
Implementation authorization: **NONE**  
Accepted implementation head at decision time: `9f92039eb9c7132a351576c31472eb30a2957a67`  
Preflight STOP evidence: `b360bced4ccd2ce250d283d665b4df08b30256c2`  
Governing principle: **PRESERVE TRUTH, NOT PLUMBING**

## 1. Why this decision exists

Objective 1 of the five-preflight program stopped because the accepted S7 shape substrate receives six live card-text primitives from `experiments/foundry_common.py` through `mtj_foundry.mtg.shapes.delivery.CardTextRules`, while four of those structural primitives had no ratified permanent owner.

The unresolved cluster was:

- `full_oracle_text`
- `canonicalize_self_reference`
- `is_mode_line`
- `_MODAL_HEADER_RE`
- `_ROLL_INSTRUCTION_RE`
- `_DIE_ROW_RE`

The STOP was correct. The permanent shapes substrate explicitly deferred ownership of those rules to a later migration slice. Assigning an owner during an evidence-only preflight would have silently made architecture.

The Captain has now approved the ownership direction below so Objective 1 can resume without inventing ownership during implementation.

## 2. Architectural rule

**A shared semantic observation belongs to the lowest coherent permanent capability that describes what the observation *is*, not to whichever downstream consumer happens to use it most.**

Therefore:

- corpus structure is owned by the corpus capability;
- printed Oracle-text normalization and printed-text structural recognition are owned by the Oracle-text capability;
- ability-shape/delivery code consumes those observations and owns only their routing / delivery consequences;
- DET preprocessing consumes the same observations and owns its synthetic matching representation;
- a downstream consumer must not create a second semantic definition merely to avoid an import.

This corrects the earlier planning tendency to place shared structural rules in `mtg/shapes/delivery.py` merely because delivery is one major consumer.

## 3. Permanent ownership decision

| Legacy/shared responsibility | Permanent ownership direction | Conservation note |
|---|---|---|
| `full_oracle_text(card)` | **`mtj_foundry.corpus`** | Full-card text projection is a consequence of canonical face handling. It must preserve all-face ordering and exact joining behavior. |
| DET-compatible `canonicalize_self_reference(text, card)` | **`mtj_foundry.oracle_text`** | Ownership moves here, but its current DET behavior must remain distinguishable from existing `normalize_self_references` until equivalence is measured and authorized. No silent consolidation. |
| `is_mode_line` | **`mtj_foundry.oracle_text`** | Recognizing a printed mode-option line is Oracle-text structure. |
| `_MODAL_HEADER_RE` behavior | **`mtj_foundry.oracle_text`** | Recognition only. Whether a header causes delivery inheritance remains a shapes concern. |
| `_ROLL_INSTRUCTION_RE` behavior | **`mtj_foundry.oracle_text`** | Recognition only. Table ownership/routing remains with the consumer. |
| `_DIE_ROW_RE` behavior | **`mtj_foundry.oracle_text`** | Recognition only. Delivery inheritance remains with shapes. |

The exact future public function names are **not** ratified by this decision. S10 should choose names that expose behavior rather than compiled-regex implementation details where practical, while preserving frozen provenance traceability for historical names.

## 4. Adjacent structural helpers

The same ownership rule should be applied during the resumed S10 census to adjacent live helpers such as:

- `_LEVEL_BAND_RE`
- `_CLASS_LEVEL_RE`
- `_is_band_marker`

If those helpers remain live at the accepted head, recognition of printed Level/Class structural markers belongs with Oracle-text structure, while semantic consequences remain with their consumers.

This paragraph is an **ownership principle**, not authorization to migrate an unmeasured symbol. The resumed census must still prove liveness and caller population.

## 5. What does *not* move into `oracle_text`

### 5.1 Delivery semantics

`mtj_foundry.mtg.shapes.delivery` continues to own ability-shape and DELIVERY semantics: for example, deciding that a mode or die-result row inherits a delivery classification from a structurally related header.

The shapes layer may consume Oracle-text structural recognizers. It must not own duplicate copies of them.

### 5.2 DET synthetic representations

`det_scan_texts` and modal expansion used specifically to manufacture DET-matchable text are **DET preprocessing policy**, not neutral Oracle-text structure.

They may consume `corpus` and `oracle_text` primitives, but this decision does not assign their final module. The resumed S10 census must classify surviving DET preprocessing and preserve it through an appropriate compatibility or permanent boundary without pulling S11+ work forward.

### 5.3 Existing permanent self-reference behavior

`mtj_foundry.oracle_text.normalize_self_references` already implements Captain-ratified N2 behavior. The legacy DET canonicalizer includes additional behavior, including CR 201.5c shortened-name handling and related compatibility rules.

S10 must preserve both semantic contracts where they differ. **Ownership consolidation is not semantic consolidation.** Any attempt to prove that one implementation can replace the other belongs to measured parser work, especially S16A, unless an earlier task explicitly authorizes the comparison and decision.

## 6. Why `shapes.delivery` is not the owner of all six

`shapes.delivery` is already a large, high-responsibility parser/derivation module. Giving it whole-card projection, self-reference normalization, modal syntax, roll-table syntax, and delivery interpretation would collapse several concept boundaries into one consumer and create avoidable sideways dependencies.

The accepted shapes package already enforces an acyclic direction and previously repaired a real cycle caused by placing derived ownership on the wrong side of the `shapes -> cr` boundary. This decision follows the same lesson: consuming a fact does not confer ownership of that fact.

A future S16A parser-seam audit is expected to search for analogous ownership bloat elsewhere. This decision does not widen S10 into that audit; it establishes one reusable diagnostic question:

> Is this module the semantic owner of the concept, or merely the most visible consumer?

## 7. S7 historical defect and the correct lesson

### 7.1 What happened

The first S7 candidate injected the six card-text rules into `CardTextRules` **by value**. That captured a snapshot of `fc.canonicalize_self_reference`.

The accepted WB4 write-boundary negative control replaces `fc.canonicalize_self_reference` at run time to force a paragraph reflow. With a captured snapshot, that replacement no longer reached the permanent shapes substrate. WB4a/b/c went red even though narrower tests and routing differentials had been green.

This was a real falsification of the first candidate.

### 7.2 What S7 actually accepted

S7 was not accepted with the defect. The repair changed `CardTextRules` so every rule is resolved **on the provider at call time**. That restored the observable substitution behavior, and S7 was later accepted at checkpoint `K-20260910-EXPERIMENTS-MIGRATION-S7-ACCEPTED`.

Therefore there is **no separate S7 implementation repair to make now**.

### 7.3 What must survive S10

The S7 repair is a conservation requirement, not permanent plumbing.

When S10 lifts these rules to permanent owners and eventually removes the `foundry_common -> CardTextRules` compatibility injection, the replacement design must preserve this observable property:

> Replacing the canonical self-reference rule used by the text layer at run time must reach every downstream consumer whose accepted behavior depends on that rule.

S10 may preserve this through module-attribute lookup, explicit dynamic dependency injection, or another acyclic mechanism. It must **not** preserve `CardTextRules` merely because S7 used it, and it must not capture the replacement rule once at module import if that disarms the negative control.

A future S10 acceptance strategy must include an equivalent of WB4 that proves the permanent route is live.

## 8. Diagnostic breadcrumbs for future card-vs-card testing

When later end-to-end card testing exposes a semantic defect, ownership should make the first investigation cheap:

| Symptom | First owner to inspect | Then inspect |
|---|---|---|
| a face is absent, reordered, or whole-card text is incomplete | `corpus` | caller composition |
| a printed card name / shortened legendary name is normalized incorrectly | `oracle_text` self-reference policy | DET preprocessing if the defect appears only in DET |
| a bullet is or is not recognized as a mode line | `oracle_text` structural recognition | DET preprocessing / shapes consumer |
| a `choose one/two/...` instruction is recognized incorrectly | `oracle_text` modal-header recognition | shapes delivery inheritance |
| a die-result row or roll instruction is grouped incorrectly | `oracle_text` roll/table recognition | shapes delivery or DET synthetic grouping |
| Oracle structure is correct but delivery token/inheritance is wrong | `mtg.shapes.delivery` | CR-derived delivery inputs |
| shapes output is correct but a DET regex sees the wrong synthetic text | DET preprocessing | `mtg.text_match` only after representation is verified |
| a runtime substitution/negative control no longer changes downstream behavior | S10 call-time dependency route | test/fixture itself only after the route is disproven |

This table is not a promise that future bugs can only occur in those places. Its purpose is to make the ownership architecture falsifiable: if a concept repeatedly has to be repaired outside its declared owner, that is evidence the ownership decision itself should be revisited.

## 9. S10 consequences

This decision resolves the architecture STOP that blocked Objective 1, but it does **not** authorize S10 implementation.

The resumed Objective-1 preflight must still:

1. mechanically complete the live `foundry_common` symbol census at the then-current accepted head;
2. mechanically complete the importer × symbol matrix;
3. classify bootstrap/import side effects;
4. compare legacy/permanent duplicates behaviorally;
5. apply this ownership decision to the six-rule seam and any mechanically adjacent live structural helpers;
6. identify any *other* symbols whose ownership remains genuinely unresolved;
7. produce the complete risk register and conservation/negative-control design;
8. produce a draft, bounded S10 Worker implementation contract marked NOT AUTHORIZED.

If another live symbol has no defensible owner even after applying existing architecture plus this decision, the preflight must still STOP rather than inventing a destination.

## 10. Expected implementation ordering after preflight acceptance

This is trajectory, not current authorization. A future S10 implementation contract should normally prefer:

1. establish/lift permanent owner APIs with differential conservation proof;
2. keep legacy facades delegating so old callers still behave identically;
3. make `shapes.delivery` consume the permanent text owners while preserving the S7 call-time substitution property;
4. migrate other caller families using the completed importer matrix;
5. prove no permanent module imports `experiments` and no second semantic owner was introduced;
6. retire `CardTextRules` compatibility injection only after its consumers no longer require it;
7. retire `foundry_common` pieces only when the complete census says they have zero live callers and the bootstrap contract permits it;
8. run the full contracted conservation and negative-control suite before any acceptance claim.

## 11. Explicit non-decisions

This decision does not:

- implement S10;
- modify accepted S7 source;
- change any current card semantics;
- merge the existing N2 and DET self-reference policies;
- define the final S16A parser topology;
- create a new `text_structure`/parser service;
- authorize S11–S16 work;
- resume AQ4;
- use Bridge v0;
- start Step6;
- authorize a merge.

The earlier Objective-1 STOP artifact remains historically correct: at the time of that preflight, these owners had not yet been decided. This document records the later Captain-approved direction that resolves that specific decision boundary rather than rewriting the STOP out of history.
