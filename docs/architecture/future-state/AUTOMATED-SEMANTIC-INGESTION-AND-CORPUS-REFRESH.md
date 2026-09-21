# Future State — Automated Semantic Ingestion and Corpus Refresh

**Date:** 2026-09-19  
**Revised:** 2026-09-20 after Objective 6 adversarial audit  
**Status:** **CAPTAIN-DIRECTED FUTURE CONCEPT — TABLED; NO CURRENT IMPLEMENTATION AUTHORIZATION**  
**Current semantic routing:** `docs/architecture/preflight/s16b/OBJECTIVE6-POST-AUDIT-CURRENT-STATE-2026-09-19.md`

## 1. Goal

Foundry should eventually ingest newly released or previewed Magic cards incrementally and derive most of their semantic representation automatically from a stable semantic substrate.

The project should not require another whole-corpus month-scale analysis every time Wizards releases a set.

The future system should reuse established structures such as:

- keyword abilities/actions and their consequence maps;
- zones and transitions;
- trigger/activation/static/replacement architecture;
- costs, Alternative Costs, Additional Costs, Cost Reduction, and Payment Methods;
- token definitions;
- Producer / Consumer Signatures;
- strong functional families such as Ramp, Tutor, Removal, Taxation, Permission Denial, and Hand Disruption;
- surfaced facets such as Top-Library Access, Sample Selection, Exile Access, Graveyard Access, Direct Placement, Fast Mana, Mass Removal, and Cantrip;
- processor throughput facts underlying derived/community `Engine` searches;
- lower-level semantic DNA such as Edict-like sacrifice/selection structure;
- typed resource facts and derived accounting inputs.

Novel wording should still receive deep reasoning when necessary. Automation removes redundant analysis; it does not reduce semantic depth.

> **Do the expensive semantic thinking once when possible, encode the result as reusable structure, and make later cards prove that they are genuinely novel before paying the full reasoning cost again.**

---

## 2. Future ingestion pipeline

```text
new card evidence
-> card identity / provenance resolution
-> Oracle/rules text normalization
-> keyword consequence expansion
-> mechanical primitive extraction
-> Producer Signatures
-> Consumer Signatures
-> costs / restrictions / dependencies / zones / destinations
-> strong functional predicates + surfaced facets
-> processor/resource/accounting facts
-> cross-concept relationships
-> human-readable explanation
-> deterministic validation
-> ambiguity / novelty routing
-> automatic acceptance OR bounded adjudication
-> incremental index/site publication
```

The pipeline should prefer deterministic/rules-backed extraction wherever possible and reserve higher-cost reasoning for ambiguity, novelty, boundary-sensitive composition, and contextual questions.

---

## 3. Reusable semantic distillation layer

The future automation tool should consume the artifacts produced by Objective 6 rather than create a competing ontology.

Important reusable inputs include:

- Keyword Consequence Registry;
- mechanical primitive definitions;
- Producer / Consumer Signature vocabulary;
- token-function definitions;
- zone-transition definitions;
- strong functional predicates;
- surfaced facets/tags;
- qualifiers and dependency coordinates;
- processor throughput/firing-cap facts;
- typed resource model;
- community/search aliases and retrieval DNA;
- positive/negative/near-miss fixtures;
- whole-vocabulary adversarial audit;
- semantic-definition version identifiers.

Example:

A future card with **Myriad** should invoke the canonical Myriad consequence expansion and overlay the card-specific payload. It should not rediscover Myriad from scratch.

Likewise, `target opponent sacrifices a creature` should resolve into sacrifice-based Removal plus affected-player selection and related Edict retrieval DNA rather than requiring a new family.

---

## 4. Novelty / adjudication routing

A future analyzer should distinguish at least:

1. **Routine** — known patterns and predicates;
2. **Compositional** — known pieces combined in a new but straightforward way;
3. **Boundary-sensitive** — touches a known hard edge or adversarial fixture;
4. **Novel** — introduces structure not represented in the registry;
5. **Ambiguous / rules-sensitive** — needs rules research or human/higher-model adjudication.

Routine cards should be cheap and fast.

Boundary-sensitive, novel, or ambiguous cards should receive deeper analysis and may produce STOP / NEEDS-ADJUDICATION rather than manufactured certainty.

---

## 5. Individual card image ingestion

The Captain should eventually be able to submit a single preview/new-card image for rapid ingestion.

### 5.1 Intended flow

```text
uploaded card image
-> visual transcription / frame parsing
-> identity + set/collector metadata when visible
-> transcription confidence check
-> source/provenance record
-> authoritative lookup when available
-> semantic ingestion pipeline
-> provisional card page / Thesaurus entry
-> later reconciliation with official Oracle data
```

### 5.2 Evidence status

Distinguish at least:

- `OFFICIAL_ORACLE`;
- `OFFICIAL_PREVIEW`;
- `THIRD_PARTY_PREVIEW`;
- `USER_IMAGE_TRANSCRIPTION`.

A provisional entry may be searchable quickly while remaining visibly noncanonical.

When authoritative Oracle data arrives, compare rules-relevant fields and rederive semantics if anything material differs.

### 5.3 Human correction loop

Where transcription is uncertain, show extracted facts and highlight low-confidence fields so the user can correct only what is wrong.

---

## 6. Timely publication does not erase authority boundaries

Rapid website publication should not collapse provisional and canonical truth.

A preview/newly-ingested card may become searchable while preserving:

- evidence status;
- exact source text/image provenance;
- semantic-definition version;
- provisional assertions;
- later Oracle reconciliation and semantic diff.

---

## 7. Incremental corpus refresh

After the final clean-room baseline exists, ordinary maintenance should be incremental.

For each upstream card-data refresh:

1. compare card identities and rules-relevant fields with the previous authoritative snapshot;
2. partition into unchanged, new, Oracle-changed, legality/status-changed, and rules/keyword-dependent populations;
3. reanalyze only affected cards by default;
4. run dependency-aware regressions for changed definitions/rules/keywords;
5. publish a semantic delta report;
6. retain reproducible version/provenance for every accepted assertion.

A new set should normally mean analysis of new/changed cards, not a forced reread of every unchanged card.

---

## 8. Definition changes require affected-population reruns

Old cards do not become semantically frozen forever.

When a semantic definition changes, identify and rerun the affected population through dependency/provenance records.

Examples after the Objective 6 audit:

- changing a **Ramp** hard predicate should rerun relevant mana/development candidates;
- changing the **Sample Selection** signature should rerun finite-sample candidates;
- changing **processor throughput** definitions should rerun recurring processor candidates and any derived `Engine` search projection;
- changing the **Mass Removal** derivation should rerun relevant interaction populations;
- changing a Keyword Consequence Registry entry should rerun every card invoking that construct;
- changing a predefined token's rules meaning should rerun generators/consumers of that token type.

Do not key dependency invalidation to obsolete ontology concepts such as canonical `Card Engine` membership.

---

## 9. Semantic artifact expected per analyzed card

Preserve, where applicable:

- exact source evidence and version;
- card/face/paragraph locality;
- normalized operations;
- keyword expansions invoked;
- mechanical primitives;
- zones and transitions;
- trigger/activation/static/replacement architecture;
- Produced events/objects/resources;
- Consumed/listened-for events;
- costs and resource conversions;
- targeting and selection authority;
- scope and quantity;
- restrictions and eligibility;
- permission actions and Permission Windows;
- token identities and consequences;
- copied/inherited payload behavior;
- timing and delayed consequences;
- negative/non-event facts where material;
- strong functional memberships;
- surfaced facets;
- processor facts;
- lower-level retrieval DNA / aliases;
- dependencies/prerequisites;
- typed resource/accounting inputs;
- confidence / ambiguity state;
- semantic-definition version;
- plain-English explanation.

The output should remain richer than a tag list.

---

## 10. Relation to future Complete My Deck

The ingestion system answers:

> **What does this card mechanically produce, consume, require, permit, deny, and accomplish?**

The future Complete My Deck layer may then ask:

> **Given this specific deck, how often and how effectively can those functions be realized, and what additions/substitutions satisfy the player's stated goals?**

Probability, simulation, strategic evidence, and recommendation logic remain downstream.

---

## 11. Future acceptance target

Useful metrics include:

- exact mechanical-fact agreement with audited ground truth;
- family/facet precision and recall where applicable;
- near-miss false-positive rate;
- missed-function false-negative rate;
- keyword-expansion accuracy;
- Producer / Consumer Signature accuracy;
- deterministic rerun stability;
- percentage automatically accepted;
- percentage routed to adjudication;
- correction rate after human audit;
- semantic drift after definition/rules updates;
- time from official preview/new Oracle record to searchable entry.

The goal is not zero human review. The goal is to spend human/higher-model attention only where it adds information.

---

## 12. Control boundary

This document does **not** authorize:

- image-ingestion implementation;
- website preview publishing;
- automated semantic acceptance;
- live corpus mutation;
- broad corpus execution;
- S16B freeze;
- AQ4 resumption;
- Bridge v0 activation;
- Step6;
- merge;
- accepted-head or `main` movement.

Any activation requires a later bounded architecture/implementation contract.
