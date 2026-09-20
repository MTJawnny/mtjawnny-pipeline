# Foundry Future-State Index

**Date:** 2026-09-19  
**Status:** **TABLED FUTURE-STATE INDEX — NO IMPLEMENTATION AUTHORIZATION**  
**Branch:** `docs/foundry-product-interaction-model-2026-09-18`

## Purpose

This directory exists to keep forward-looking product, automation, and strategic ideas out of the active Objective 6 semantic-definition surface.

The repository has already undergone substantial cleanup to reduce stale or misleading routing. Future ideas should therefore be preserved deliberately rather than allowed to accumulate as present-tense instructions inside active semantic documents.

Governing rule:

> **Future-state concepts belong here unless they are an active prerequisite for the current Objective 6 semantic/corpus work.**

Nothing in this directory authorizes implementation, S16B freeze, corpus execution, AQ4 resumption, Bridge v0 activation, Step6, merge, accepted-head movement, or `main` movement.

---

## 1. Audit result — current forward-looking material

The 2026-09-18/19 product and semantic conversations contain several distinct forward-looking programs. They should not be conflated.

### A. Complete My Deck / probabilistic deck-context reasoning — FUTURE PRODUCT LAYER

Dedicated future-state record:

- `COMPLETE-MY-DECK-PROBABILISTIC-CONTEXT.md`

Original source record remains:

- `docs/architecture/FOUNDRY-PRODUCT-INTERACTION-MODEL-2026-09-18.md`, especially Section 9, **Tabled future state — probabilistic deck-context reasoning for Complete My Deck**.

Core direction:

- canonical Foundry semantics answer what a card mechanically can do;
- a later deck-context layer estimates how reliably, how early, and at what throughput a particular deck can realize those functions;
- exact probability, combinatorics, deterministic state models, or simulation may be used where appropriate;
- strategic interpretation remains downstream of canonical semantics;
- recommendations must explain material assumptions rather than emit opaque scores.

This remains future product work and should not become present-tense S16B semantic authority.

### B. External strategic/recommendation enrichment — FUTURE STRATEGIC LAYER

Dedicated future-state record:

- `STRATEGIC-RESEARCH-ENRICHMENT.md`

Captain-directed future program discussed during S16 planning:

- community strategy knowledge and claim-level provenance;
- CommanderSalt as strategic-system prior art;
- Recommander as behavioral/recommendation prior art;
- broader Commander strategic/deck-construction reasoning;
- conflict tracking and provenance;
- strict separation from canonical Oracle/rules-derived truth.

This belongs above Foundry's semantic substrate. It must not be imported into canonical mechanical truth merely because a community source describes a card in strategic language.

### C. Automated semantic distillation and continuous corpus refresh — FUTURE RUNTIME/PIPELINE CAPABILITY

Dedicated record:

- `AUTOMATED-SEMANTIC-INGESTION-AND-CORPUS-REFRESH.md`

Goal:

- use the stable semantic foundation, keyword consequence registry, event signatures, hard predicates, and learned recurring structures to automate much of the mechanical/semantic analysis of newly printed cards;
- reserve expensive reasoning/adjudication for genuinely ambiguous or novel cards;
- support incremental corpus updates rather than requiring another month-scale whole-corpus run for every new set.

### D. Rapid single-card image ingestion / preview-card intake — FUTURE PRODUCT + PIPELINE CAPABILITY

Also preserved in:

- `AUTOMATED-SEMANTIC-INGESTION-AND-CORPUS-REFRESH.md`

Goal:

- allow the Captain to submit an individual card image when a new card is previewed/released;
- identify/transcribe the card;
- distinguish preview evidence from official Oracle truth;
- derive provisional semantics immediately;
- publish rapidly to a clearly marked preview/provisional channel when desired;
- reconcile automatically when authoritative Oracle data becomes available.

### E. Final clean-room corpus reanalysis — REQUIRED PRE-CORPUS EXECUTION, NOT A SPECULATIVE PRODUCT FEATURE

This is near-term project work after the semantic foundation is audited/frozen, not merely a future product wish.

Preserved separately in:

- `docs/architecture/preflight/s16b/OBJECTIVE6-FINAL-CORPUS-REANALYSIS-PLAN-2026-09-19.md`

It includes the current working execution shape:

- whole-vocabulary semantic audit first;
- keyword consequence distillation first;
- broad/contested concepts such as Card Advantage receive appropriate adversarial research;
- 200-card stratified calibration;
- approximately 25 cards per atomic deep-analysis batch by default;
- approximately 100 cards per review checkpoint;
- approximately 500 cards per larger regression epoch;
- smaller batches for pathological cards;
- deliberate STOP/NEEDS-ADJUDICATION rather than forced classification;
- final corpus truth built from the new semantic contract rather than preserving old assertions by inertia.

### F. Final vocabulary/naming pass — REQUIRED BEFORE PUBLIC SEMANTIC PRESENTATION

Captain direction already recorded during Objective 6:

- inspect the full tapestry of names after the semantic distinctions are broadly complete;
- improve clarity, consistency, and aesthetic quality without reopening sound underlying distinctions merely because a label changes;
- examples already flagged for later naming review include `Card Prospecting` and the working `Graveyard Access` name;
- names such as `Permission Denial` and `Lockdown` are positive style anchors.

This is not implementation authorization; it is a later semantic/presentation audit.

### G. Realization, ceiling, and game horizon — FUTURE QUANTITATIVE STRATEGIC MODEL

Dedicated record:

- `REALIZATION-CEILING-AND-GAME-HORIZON.md`

Core direction:

- keep canonical capability separate from opportunity count, realization probability/rate, and expected realized output;
- evaluate usefulness over an explicit remaining game horizon rather than assuming a permanent remains relevant indefinitely;
- treat the Captain's current roughly turn-7-to-8 Commander horizon as a hypothesis/modeling assumption to validate empirically rather than a hard-coded truth;
- preserve controller agency/opponent dependency as factual realization coordinates;
- use Explore as a prerequisite-realization fixture and Smuggler's Share as a repeated-opportunity-versus-realized-output fixture;
- allow measured/modelled results to contradict Captain or community expectations.

---

## 2. What does NOT belong in this future-state directory

Some work may sound forward-looking but is an active prerequisite for Objective 6 and should remain in `docs/architecture/preflight/s16b/`.

Examples:

- Keyword Consequence Distillation Gate;
- Semantic Distillation Methodology;
- Card Advantage adversarial research required before freeze;
- current hard-predicate adjudication;
- current Engine/Ramp/Interaction semantic decisions;
- final corpus reanalysis readiness requirements.

Those are part of making the current semantic substrate correct.

---

## 3. Repository hygiene rule

Going forward, when a conversation produces a substantial idea that is explicitly tabled for later:

1. preserve it in this directory or a clearly linked future-state artifact;
2. mark it `TABLED` / `NO CURRENT IMPLEMENTATION AUTHORIZATION`;
3. identify which current subsystem it will eventually consume;
4. identify what must be true before it can activate;
5. avoid adding present-tense routing language to current architecture/preflight documents;
6. keep canonical semantic truth, product strategy, and speculative future reasoning visibly separated.

If a future-state idea becomes active work, it should receive a new bounded contract rather than silently becoming executable because this directory exists.

---

## 4. Current future-state files

- `README.md` — this index/audit and repository-hygiene rule.
- `AUTOMATED-SEMANTIC-INGESTION-AND-CORPUS-REFRESH.md` — continuous card ingestion, semantic automation, dependency-aware refresh, and rapid image/preview intake.
- `COMPLETE-MY-DECK-PROBABILISTIC-CONTEXT.md` — future deck-context probability/simulation layer.
- `REALIZATION-CEILING-AND-GAME-HORIZON.md` — future quantitative distinction between ceiling, opportunity, realization, and expected throughput over an explicit game horizon.
- `STRATEGIC-RESEARCH-ENRICHMENT.md` — future community/prior-art/strategic knowledge layer with provenance boundaries.

Near-term final corpus execution planning remains under S16B preflight rather than this directory:

- `docs/architecture/preflight/s16b/OBJECTIVE6-FINAL-CORPUS-REANALYSIS-PLAN-2026-09-19.md`

Existing source material still located elsewhere remains authoritative as a historical source until deliberately migrated. This index does not silently supersede or delete those records.

---

## 5. Control boundary

This directory is documentation only.

It does **not** authorize:

- implementation of any future-state feature;
- current recommendation behavior;
- broad corpus execution;
- S16B freeze;
- merge;
- movement of accepted implementation head or `main`;
- AQ4 resumption;
- Bridge v0 activation;
- Step6.

The governing project principle remains:

> **PRESERVE TRUTH, NOT PLUMBING.**