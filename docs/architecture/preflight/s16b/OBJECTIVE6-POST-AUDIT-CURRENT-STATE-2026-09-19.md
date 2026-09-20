# Objective 6 — Post-Audit Current State

**Date:** 2026-09-19  
**Revised:** 2026-09-20 after stale-document cleanup  
**Status:** **CURRENT S16B OBJECTIVE 6 SEMANTIC ROUTING / FREEZE CANDIDATE — NOT FROZEN**  
**Scope:** Documentation-only state on PR #70  
**Governing principle:** **PRESERVE TRUTH, NOT PLUMBING.**  
**Research principle:** **THOROUGHNESS OVER THROUGHPUT.**

## 1. Authority and routing

For a cold reader, this file is the current Objective 6 semantic routing layer on PR #70.

Directory landing page:

`README.md`

Cleanup record:

`OBJECTIVE6-POST-AUDIT-CLEANUP-2026-09-20.md`

The earlier pre-audit decision ledger, Captain semantic-decision record, completed audit handoff, rejected Card Access Differential artifact, and superseded Card Advantage/Engine refinement have been removed from the active S16B surface. Their history remains recoverable in Git.

If an older surviving research document contains a recommendation or working term that conflicts with the post-audit evidence chain below, the post-audit evidence/current candidate record controls. Research evidence is not semantic authority by itself.

No content in this file constitutes an actual S16B freeze.

---

## 2. Ordered adversarial program completed

The required order was preserved:

1. **Weird-card adversarial corpus hunt**
   - `OBJECTIVE6-WEIRD-CARD-ADVERSARIAL-CORPUS-HUNT-2026-09-19.md`
   - initial durable commit: `c3407c6`
2. **Whole-vocabulary adversarial semantic audit**
   - `OBJECTIVE6-WHOLE-VOCABULARY-ADVERSARIAL-SEMANTIC-AUDIT-2026-09-19.md`
   - initial durable commit: `1c0883d`
3. **Global naming audit**
   - `OBJECTIVE6-GLOBAL-NAMING-AUDIT-FREEZE-CANDIDATE-2026-09-19.md`
   - initial durable commit: `1b3bc8b`
4. **Stale-document cleanup**
   - `OBJECTIVE6-POST-AUDIT-CLEANUP-2026-09-20.md`

The weird-card evidence came first; structural corrections followed; naming followed structure.

---

## 3. Current structural verdict

### Strong public functional families

Retain:

- Ramp;
- Tutor;
- Removal;
- Taxation;
- Permission Denial;
- Hand Disruption.

These names do not erase lower-level mechanism, participant, scope, timing, restriction, destination, payment, or duration facts.

### Surfaced facets / tags / search views

Retain or promote:

- Top-Library Access;
- Sample Selection;
- Exile Access;
- Graveyard Access;
- Direct Placement;
- Fast Mana as a derived/community tag over measured acceleration facts;
- Counterspell;
- Mass Removal;
- Cantrip.

### Mechanical primitives / event signatures / coordinates

Preserve directly:

- Draw;
- Card Use Permission;
- `PLAY` versus `CAST`;
- Permission Window;
- Library Traversal plus explicit stop rule;
- selection authority and cardinality;
- source/destination/owner/controller/provenance;
- Additional Execution;
- copy/execution provenance;
- Cost Reduction;
- Alternative Cost in the formal Comprehensive Rules sense;
- Additional Cost;
- Payment Method;
- Direct Placement events;
- Typed Resources;
- Stored Capacity;
- processor input/aggregation/firing/output/retention facts;
- Ramp mechanism/resource facts;
- Keyword Consequence Producer / Consumer Signatures.

### Derived accounting / product facts

- Card Resource Delta;
- self-replacing / parity / resource-change states;
- Role Compression;
- processor/throughput profiles.

### Community / theory / strategic / search language

Keep searchable and explainable without forcing canonical hard-family membership:

- Engine / Card Engine / Mana Engine and other Engine phrases;
- Card Advantage / Virtual Card Advantage / Card Quality;
- Ritual;
- Impulsive Draw;
- Recursion / Reanimation;
- Edict;
- Burn;
- Stax;
- Sweeper / Board Wipe;
- Lockdown pending dedicated boundary evidence.

### Retired canonical concepts

- Card Replacement family;
- Card Access Differential;
- Card Sifting as a separate concept;
- Card Prospecting;
- Bounded Extraction;
- Deployment Bypass;
- Alternate Payment as one umbrella;
- canonical Engine parent/child hierarchy;
- Resource-Type Separation as an ontology noun.

---

## 4. Key adversarial corrections

### Engine

The former `Engine is the canonical parent` decision is superseded.

The evidence supports hard processor facts such as:

- input/event kind;
- input aggregation;
- firing multiplicity and cap;
- opportunity window;
- output kind/magnitude/multiplicity;
- processor retention;
- future-eligibility effect;
- external fuel;
- stored capacity;
- feedback dependency.

`Engine` remains a derived/search/community label over those facts.

### Card Filtering / Sample Selection

Generic Card Filtering is a broad UI/search umbrella and low-information similarity signal.

The independently queryable finite-sample pattern is **Sample Selection**.

The sample may be fixed, variable, state-derived, resource-controlled, or large. Plunge into Darkness is the key proof that finite does not mean fixed/small.

### Card Resource Delta

Former working name: Card Resource Differential.

CRD is a **derived accounting fact** over distinct underlying card-origin resources/access, not a semantic family.

Do not count:

- spell/card copies as additional card-origin resources;
- repeated executions as additional underlying cards;
- the same physical card again merely because it moved zones;
- the source permanent twice merely because it persists while granting access.

Present mana affordability belongs to current actionability/realization, not resource identity.

Top-library access exposes the current eligible top card plus refreshability, not infinite simultaneous stock.

### Card Access Differential

Retired. No replacement metric.

A future `currently actionable` UI projection, if proven useful, must derive from existing permission/timing/land-play/payment/state facts.

### Payment semantics

The old `Alternate Payment` umbrella is retired.

Keep distinct:

- Cost Reduction;
- Alternative Cost under CR 118.9;
- Additional Cost;
- Payment Method.

Convoke, Delve, and Improvise are Payment Method facts, not formal Alternative Costs.

### Direct Placement

Former working name: Deployment Bypass.

The cast-versus-put distinction survives strongly.

- Omniscience / Cascade / Discover free casts are still casts.
- Elvish Piper / Reanimate / Collected Company-style battlefield placement is not a cast of the placed card.

### Top-Library Access

Retains surfaced include/exclude value.

Positive examples grant actual use permission for the current top card. Tutor-to-top, reveal-only, and reorder-only effects remain negative unless they independently grant use permission.

`PLAY` and `CAST` remain hard-distinct.

---

## 5. Freeze-candidate naming crosswalk — key changes

- `Card Prospecting` / `Bounded Extraction` -> **Sample Selection**;
- `Access Horizon` -> **Permission Window**;
- alternate-zone play/cast umbrella -> **Card Use Permission** + source-zone facts;
- `Sequential Library Traversal` -> **Library Traversal**;
- `Repeat-Use / Additional Execution` -> **Additional Execution**;
- `Resource-Type Separation` -> **Typed Resources**;
- `Card Resource Differential` -> **Card Resource Delta**;
- `Deployment Bypass` -> **Direct Placement**;
- `Payment Substitution` -> **Payment Method**;
- `turn_structure_bound` -> machine candidate **requires_new_opportunity**.

The global naming artifact contains the full crosswalk.

---

## 6. Current live candidate records

Use these current/revised records where applicable:

- `OBJECTIVE6-CARD-ACCESS-ACCEPTED-COMPONENTS-2026-09-19.md`;
- `OBJECTIVE6-CARD-RESOURCE-DIFFERENTIAL-NAMING-RULING-2026-09-19.md` — historical filename; content is Card Resource Delta;
- `OBJECTIVE6-CARD-FILTERING-BOUNDED-EXTRACTION-CONSOLIDATION-CANDIDATE-2026-09-19.md` — historical filename; content is Sample Selection;
- `OBJECTIVE6-CARD-FILTERING-NAMING-RULING-2026-09-19.md`;
- `OBJECTIVE6-ENGINE-HIERARCHY-2026-09-19.md` — now records Engine hierarchy demotion;
- `OBJECTIVE6-ENGINE-COMPONENT-ADJUDICATION-2026-09-19.md`;
- `OBJECTIVE6-COST-REDUCTION-AND-ALTERNATE-PAYMENT-2026-09-19.md` — historical filename; content is the final split cost/payment model;
- `OBJECTIVE6-NORMAL-DEPLOYMENT-BYPASS-BOUNDARY-2026-09-19.md` — historical filename; content is Direct Placement;
- `OBJECTIVE6-RAMP-DECISION-MAP-2026-09-19.md`;
- `OBJECTIVE6-TOP-LIBRARY-ACCESS-RULING-2026-09-19.md`;
- `OBJECTIVE6-CANTRIP-AND-TEMPORARY-EXILE-ACCESS-RULING-2026-09-19.md` — historical filename; content is Cantrip + Exile Access;
- `OBJECTIVE6-CARD-REPLACEMENT-RETIREMENT-RULING-2026-09-19.md`;
- `OBJECTIVE6-KEYWORD-CONSEQUENCE-DISTILLATION-GATE-2026-09-19.md`;
- `OBJECTIVE6-SEMANTIC-DISTILLATION-METHODOLOGY-2026-09-19.md`;
- `OBJECTIVE6-FINAL-CORPUS-REANALYSIS-PLAN-2026-09-19.md`.

Research/adversarial records remain evidence inputs, not independent current semantic authority.

Historical filenames have not been cosmetically renamed where doing so would add churn without changing truth. Their file bodies state the revised semantics.

---

## 7. Remaining bounded work before formal freeze review

Objective 6 is a semantic freeze **candidate**, not an actual freeze.

Remaining validation work:

1. **Card Resource Delta stateful fixtures**
   - top-library access;
   - graveyard/exile permission;
   - same-card reuse;
   - copies;
   - recovery of already-usable cards;
   - source identity / no double counting;
   - multiplayer vectors.

2. **Sample Selection retrieval/UI fixtures**
   - prove strong distinction from ordinary Filtering;
   - distinguish Tutor;
   - distinguish Library Traversal;
   - cover variable/resource-controlled depth and staged selection authority.

3. **Keyword Consequence Registry census/design gate**
   - current CR-derived construct census;
   - canonical consequence maps;
   - Producer / Consumer Signatures;
   - delayed consequences;
   - negative/non-events;
   - deterministic reuse during later corpus analysis.

4. **Final stale-routing verification**
   - confirm remaining active docs do not present superseded semantics as current truth.

5. **Lockdown**
   - run a dedicated hard-boundary audit only if evidence requires more than a search/community label.

The broad design/invention pass should not be restarted without new evidence.

---

## 8. Standing controls

Remain in force unless explicitly superseded by a newer Captain direction:

- S15 CLOSED;
- S16B NOT FROZEN;
- AQ4 PAUSED;
- Bridge v0 PARKED_UNUSED;
- Step6 NO;
- MERGE NO;
- MAIN_MOVE NO;
- PR #70 documentation-only, draft, unmerged.

No semantic freeze is authorized by this file.
