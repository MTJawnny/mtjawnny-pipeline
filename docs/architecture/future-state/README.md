# Foundry Future-State Index

**Date:** 2026-09-19  
**Revised:** 2026-09-20 after Objective 6 adversarial audit / cleanup  
**Status:** **TABLED FUTURE-STATE INDEX — NO IMPLEMENTATION AUTHORIZATION**  
**Branch:** `docs/foundry-product-interaction-model-2026-09-18`

## Purpose

This directory keeps forward-looking product, automation, strategic-research, and quantitative-model ideas out of the active Objective 6 semantic-definition surface.

Current Objective 6 semantic routing lives at:

`docs/architecture/preflight/s16b/OBJECTIVE6-POST-AUDIT-CURRENT-STATE-2026-09-19.md`

Future-state documents may consume that substrate, but they do not define it.

> **Future-state concepts belong here unless they are an active prerequisite for the current Objective 6 semantic/corpus work.**

Nothing in this directory authorizes implementation, S16B freeze, corpus execution, AQ4 resumption, Bridge v0 activation, Step6, merge, accepted-head movement, or `main` movement.

---

## 1. Current forward-looking programs

### A. Complete My Deck / probabilistic deck-context reasoning

Record:

- `COMPLETE-MY-DECK-PROBABILISTIC-CONTEXT.md`

Direction:

- canonical Foundry semantics answer what a card mechanically can do;
- a later deck-context layer estimates how reliably, how early, and at what throughput a particular deck can realize those functions;
- probability, combinatorics, deterministic state models, or simulation may be used where appropriate;
- strategic interpretation remains downstream;
- recommendations should expose material assumptions rather than emit opaque scores.

The post-audit revision removes reliance on canonical `Card Engine` membership. Processor throughput facts are canonical; `Engine` remains a derived/search/community handle.

### B. External strategic/recommendation enrichment

Record:

- `STRATEGIC-RESEARCH-ENRICHMENT.md`

Direction:

- community strategy knowledge with claim-level provenance;
- CommanderSalt as strategic-system prior art;
- Recommander as behavioral/recommendation prior art;
- broader Commander strategic/deck-construction reasoning;
- conflict tracking and provenance;
- strict separation from Oracle/rules-derived canonical truth.

### C. Automated semantic distillation and continuous corpus refresh

Record:

- `AUTOMATED-SEMANTIC-INGESTION-AND-CORPUS-REFRESH.md`

Direction:

- reuse the stable semantic substrate, Keyword Consequence Registry, Producer / Consumer Signatures, strong functional predicates, surfaced facets, processor facts, and typed resources;
- automate routine/compositional new-card analysis;
- reserve deeper reasoning/adjudication for boundary-sensitive, novel, or ambiguous cards;
- support dependency-aware incremental refresh rather than routine whole-corpus reruns.

### D. Rapid single-card image / preview-card intake

Also recorded in:

- `AUTOMATED-SEMANTIC-INGESTION-AND-CORPUS-REFRESH.md`

Direction:

- accept a card image during preview/release periods;
- transcribe/identify with provenance;
- distinguish preview/user evidence from official Oracle authority;
- derive provisional semantics;
- publish to a clearly marked provisional surface when authorized;
- reconcile automatically when authoritative Oracle data arrives.

### E. Realization, ceiling, and game horizon

Record:

- `REALIZATION-CEILING-AND-GAME-HORIZON.md`

Direction:

- keep canonical capability separate from opportunity count, realization probability/rate, and expected realized output;
- evaluate output over an explicit remaining game horizon;
- treat any Commander turn horizon as a modeling assumption to validate, not canonical truth;
- preserve controller agency/opponent dependency as factual realization coordinates;
- allow measured/modelled results to contradict Captain or community expectations.

---

## 2. Near-term Objective 6 work that does NOT belong here

The following remain active S16B/pre-corpus work under `docs/architecture/preflight/s16b/`:

- post-audit current-state routing;
- Card Resource Delta stateful validation;
- Sample Selection retrieval/UI validation;
- Keyword Consequence Registry census/design gate;
- semantic distillation methodology;
- final clean-room corpus reanalysis planning;
- formal S16B freeze review when explicitly authorized.

The weird-card research, whole-vocabulary audit, and global naming audit have already been completed and are active evidence for the freeze candidate.

---

## 3. Current naming/structure note

The prior broad naming pass is complete. Current freeze-candidate terminology includes, among other changes:

- `Card Prospecting` / `Bounded Extraction` -> **Sample Selection**;
- `Access Horizon` -> **Permission Window**;
- alternate-zone play/cast umbrella -> **Card Use Permission** plus source-zone coordinates;
- `Sequential Library Traversal` -> **Library Traversal**;
- `Repeat-Use / Additional Execution` -> **Additional Execution**;
- `Resource-Type Separation` -> **Typed Resources** as a substrate invariant;
- `Card Resource Differential` -> **Card Resource Delta**;
- `Deployment Bypass` -> **Direct Placement**;
- `Payment Substitution` -> **Payment Method**;
- canonical Engine hierarchy -> retired in favor of processor facts + derived/search `Engine` language.

`Lockdown` remains structurally OPEN as a possible search/community label pending evidence.

This index does not itself freeze any of those names.

---

## 4. Repository hygiene rule

When a substantial idea is explicitly tabled for later:

1. preserve it here or in a clearly linked future-state artifact;
2. mark it `TABLED` / `NO CURRENT IMPLEMENTATION AUTHORIZATION`;
3. identify which current subsystem it would consume;
4. identify what must be true before it can activate;
5. avoid adding present-tense routing language to active preflight documents;
6. keep canonical semantics, product strategy, and speculative reasoning visibly separated;
7. update future-state examples when the canonical substrate changes so obsolete ontology claims do not survive as misleading examples.

If a tabled concept becomes active work, it requires a new bounded contract.

---

## 5. Current future-state files

- `README.md` — this routing/index document.
- `AUTOMATED-SEMANTIC-INGESTION-AND-CORPUS-REFRESH.md` — incremental ingestion, semantic automation, dependency-aware refresh, rapid image/preview intake.
- `COMPLETE-MY-DECK-PROBABILISTIC-CONTEXT.md` — future deck-context probability/simulation layer.
- `REALIZATION-CEILING-AND-GAME-HORIZON.md` — ceiling/opportunity/realization/expected-throughput model.
- `STRATEGIC-RESEARCH-ENRICHMENT.md` — external strategic knowledge/prior-art layer with provenance boundaries.

Near-term final corpus execution planning remains at:

- `docs/architecture/preflight/s16b/OBJECTIVE6-FINAL-CORPUS-REANALYSIS-PLAN-2026-09-19.md`

---

## 6. Control boundary

This directory does **not** authorize:

- implementation of any future-state feature;
- current recommendation behavior;
- broad corpus execution;
- S16B freeze;
- merge;
- movement of accepted implementation head or `main`;
- AQ4 resumption;
- Bridge v0 activation;
- Step6.

> **PRESERVE TRUTH, NOT PLUMBING.**
