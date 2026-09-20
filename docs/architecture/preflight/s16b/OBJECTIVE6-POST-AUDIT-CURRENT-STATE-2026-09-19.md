# Objective 6 — Post-Audit Current State

**Date:** 2026-09-19  
**Status:** **CURRENT S16B OBJECTIVE 6 SEMANTIC ROUTING / FREEZE CANDIDATE — NOT FROZEN**  
**Scope:** Documentation-only state on PR #70.  
**Governing principle:** **PRESERVE TRUTH, NOT PLUMBING.**

## 1. Why this file exists

The 2026-09-19 Objective 6 session deliberately invalidated several earlier working decisions after a weird-card corpus attack and whole-vocabulary adversarial audit.

Older session ledgers, handoffs, and working rulings remain useful historical evidence, but some of them contain statements that are no longer current, including the former canonical Engine hierarchy and pre-audit Card Filtering / Bounded Extraction structure.

For a cold reader, **this file is the current routing layer for Objective 6 semantic design on PR #70.**

If an older Objective 6 document conflicts with the post-audit artifacts listed below, the post-audit artifact wins as the current candidate direction. This does not convert the candidate into a frozen architecture.

## 2. Ordered adversarial program completed

The required order was preserved:

1. **Weird-card research / adversarial corpus hunt**
   - `OBJECTIVE6-WEIRD-CARD-ADVERSARIAL-CORPUS-HUNT-2026-09-19.md`
   - initial durable commit: `c3407c6`
2. **Whole-vocabulary adversarial semantic audit**
   - `OBJECTIVE6-WHOLE-VOCABULARY-ADVERSARIAL-SEMANTIC-AUDIT-2026-09-19.md`
   - initial durable commit: `1c0883d`
3. **Global naming audit**
   - `OBJECTIVE6-GLOBAL-NAMING-AUDIT-FREEZE-CANDIDATE-2026-09-19.md`
   - initial durable commit: `1b3bc8b`

Subsequent commits applied the structural and naming conclusions back into the key candidate records.

## 3. Current structural verdict

### Strong public functional families

Retain:

- Ramp;
- Tutor;
- Removal;
- Taxation;
- Permission Denial;
- Hand Disruption.

These names do not by themselves erase their lower-level mechanism, object, scope, duration, eligibility, or destination facts.

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
- Card Use Permission with `PLAY` vs `CAST`;
- Permission Window;
- Library Traversal + explicit stop rule;
- selection authority and cardinality;
- source/destination/owner/controller/provenance;
- Additional Execution;
- copy/execution provenance;
- Cost Reduction;
- Alternative Cost in the formal CR sense;
- Additional Cost;
- Payment Method;
- Direct Placement events;
- Typed Resources;
- Stored Capacity;
- processor throughput/firing-cap facts;
- Ramp mechanism/resource facts;
- keyword-consequence Producer / Consumer Signatures.

### Derived accounting / product facts

- Card Resource Delta;
- self-replacing / parity / resource-change states;
- Role Compression;
- processor/throughput profiles.

### Community / theory / strategic terms

Keep searchable and explainable without asserting them as canonical hard families where inappropriate:

- Engine / Card Engine / Mana Engine and other Engine phrases;
- Card Advantage / Virtual Card Advantage / Card Quality;
- Ritual;
- Impulsive Draw;
- Recursion / Reanimation;
- Edict;
- Burn;
- Stax;
- Sweeper / Board Wipe;
- Lockdown pending a dedicated hard-boundary audit.

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

## 4. Key adversarial corrections

### Engine

The prior `Engine is the canonical parent` decision is superseded.

The evidence supports hard processor facts such as input aggregation, firing multiplicity/cap, opportunity window, output magnitude/multiplicity, retention, external fuel, and feedback dependency. The word `Engine` is broader in player usage than the former Foundry predicate.

Therefore Engine remains a derived/search/community label over harder facts rather than a boolean ontology gate.

### Card Filtering / Sample Selection

Generic Card Filtering is now a broad UI/search umbrella, not high-information semantic membership.

The independently queryable finite-sample pattern is **Sample Selection**. Plunge into Darkness proves the sample depth may be variable/player-controlled rather than a fixed small N.

### Card Resource Delta

Former working name: Card Resource Differential.

CRD is a **derived accounting fact** over distinct underlying card-origin resources and access, not a family.

Do not count spell copies, repeated executions, or the same physical card in a new zone as newly created card-origin resources.

Present mana affordability is a current-actionability fact, not a prerequisite for resource identity.

### Card Access Differential

Retired. No replacement metric.

### Payment semantics

The old Alternate Payment umbrella is retired.

Distinguish:

- Cost Reduction;
- Alternative Cost in the CR 118.9 sense;
- Additional Cost;
- Payment Method.

Convoke, Delve, and Improvise belong to Payment Method facts, not formal Alternative Cost.

### Direct Placement

Former working name: Deployment Bypass.

The cast-vs-put distinction survives strongly. Omniscience is a critical negative: a free spell is still cast; Elvish Piper/Reanimate/Collected Company-style placement is not.

## 5. Current freeze-candidate names

Use the global naming artifact for the full crosswalk. The largest changes are:

- `Bounded Extraction` -> **Sample Selection**;
- `Access Horizon` -> **Permission Window**;
- `Alternate-Zone Play/Cast Access` -> **Card Use Permission**;
- `Sequential Library Traversal` -> **Library Traversal**;
- `Repeat-Use / Additional Execution` -> **Additional Execution**;
- `Resource-Type Separation` -> **Typed Resources**;
- `Card Resource Differential` -> **Card Resource Delta**;
- `Deployment Bypass` -> **Direct Placement**;
- `Payment Substitution` -> **Payment Method**;
- `turn_structure_bound` -> machine candidate **requires_new_opportunity**.

## 6. Current live candidate records

Prefer these revised records over earlier versions where they conflict:

- `OBJECTIVE6-CARD-ACCESS-ACCEPTED-COMPONENTS-2026-09-19.md`;
- `OBJECTIVE6-CARD-RESOURCE-DIFFERENTIAL-NAMING-RULING-2026-09-19.md` (filename historical; content now Card Resource Delta);
- `OBJECTIVE6-CARD-FILTERING-BOUNDED-EXTRACTION-CONSOLIDATION-CANDIDATE-2026-09-19.md` (filename historical; content now Sample Selection);
- `OBJECTIVE6-CARD-FILTERING-NAMING-RULING-2026-09-19.md`;
- `OBJECTIVE6-ENGINE-HIERARCHY-2026-09-19.md` (now explicitly records hierarchy demotion);
- `OBJECTIVE6-ENGINE-COMPONENT-ADJUDICATION-2026-09-19.md`;
- `OBJECTIVE6-COST-REDUCTION-AND-ALTERNATE-PAYMENT-2026-09-19.md` (filename historical; content now split cost/payment model);
- `OBJECTIVE6-NORMAL-DEPLOYMENT-BYPASS-BOUNDARY-2026-09-19.md` (filename historical; content now Direct Placement);
- `OBJECTIVE6-RAMP-DECISION-MAP-2026-09-19.md`;
- `OBJECTIVE6-CARD-ADVANTAGE-ENGINE-REFINEMENT-2026-09-19.md` (explicit historical/superseded marker);
- `OBJECTIVE6-KEYWORD-CONSEQUENCE-DISTILLATION-GATE-2026-09-19.md`.

Historical filenames are intentionally not renamed during this pass so Git/review references remain stable. Their current file bodies state the revised semantics.

## 7. Remaining uncertainties before formal freeze review

Objective 6 is a semantic freeze **candidate**, not yet ready for the actual freeze decision.

Before formal freeze review, complete/verify at least:

1. a bounded **Card Resource Delta stateful fixture set** covering top access, graveyard/exile permission, same-card reuse, copies, recovery, source-retention identity, and multiplayer vectors;
2. a bounded **Sample Selection retrieval/UI fixture set** proving it remains distinct from ordinary Filtering, Tutor, and Library Traversal;
3. the required **Keyword Consequence Registry census/design gate** before any broad corpus run;
4. a final stale-document/routing sweep after this current-state file replaces the pre-audit ledger as the cold-reader entry point;
5. a bounded decision on `Lockdown` only if evidence forces it to become more than a search/community label.

These are validation/freeze-review tasks. They are not permission to invent more families.

## 8. Standing controls

Remain in force unless a newer durable Captain direction explicitly supersedes them:

- S15 CLOSED;
- S16B NOT FROZEN;
- AQ4 PAUSED;
- Bridge v0 PARKED_UNUSED;
- Step6 NO;
- MERGE NO;
- MAIN_MOVE NO;
- PR #70 remains documentation-only, draft, and unmerged.

No semantic freeze is authorized by this file.
