# Future State — Automated Semantic Ingestion and Corpus Refresh

**Date:** 2026-09-19  
**Status:** **CAPTAIN-DIRECTED FUTURE CONCEPT — TABLED; NO CURRENT IMPLEMENTATION AUTHORIZATION**

## 1. Goal

Foundry should eventually be able to ingest newly released or previewed Magic cards incrementally and derive most of their semantic representation automatically from the stable semantic substrate.

The project should not require another full month-scale corpus reanalysis every time Wizards releases a set.

The future system should exploit the fact that most new cards are composed from recurring Magic structures:

- known keyword abilities/actions;
- known zones and transitions;
- known trigger forms;
- known costs and restrictions;
- known token definitions;
- known producer/consumer event signatures;
- known functional predicates such as Ramp, Removal, Protection, Tutor, Card Advantage, Interaction families, etc.;
- known lower-level semantic DNA such as Edict-like sacrifice/selection structure;
- combinations of already understood primitives.

Novel wording should still receive deep reasoning when necessary. Automation is intended to remove redundant analysis, not reduce semantic depth.

Governing principle:

> **Do the expensive semantic thinking once when possible, encode the result as reusable structure, and make later cards prove that they are genuinely novel before paying the full reasoning cost again.**

---

## 2. Future ingestion pipeline

Conceptual pipeline:

```text
new card evidence
-> card identity / provenance resolution
-> Oracle/rules text normalization
-> keyword consequence expansion
-> mechanical primitive extraction
-> event/output producer signatures
-> consumer/listener signatures
-> costs / restrictions / dependencies / zones / destinations
-> hard semantic predicates
-> cross-concept relationships
-> human-readable explanation
-> deterministic validation
-> ambiguity / novelty scoring
-> automatic acceptance OR bounded adjudication
-> incremental index/site publication
```

The system should prefer deterministic/rules-backed extraction wherever possible and reserve higher-cost model reasoning for semantic ambiguity, novel structures, and cross-card contextual questions.

---

## 3. Reusable semantic distillation layer

The future automation tool should consume the artifacts produced by the current Objective 6 work rather than create a competing ontology.

Important reusable inputs include:

- Keyword Consequence Registry;
- mechanical primitive definitions;
- event/output signature vocabulary;
- token-function definitions;
- zone-transition definitions;
- functional hard predicates;
- qualifiers and dependency coordinates;
- community-term aliases / retrieval DNA;
- positive/negative/near-miss fixtures;
- final whole-vocabulary audit results;
- semantic-definition version identifiers.

Example:

A future card with **Myriad** should not cause a model to rediscover Myriad from scratch. The analyzer should expand the keyword from the canonical registry, then overlay the card's own copied payload, ETB/LTB/combat-damage abilities, restrictions, and other text.

Likewise, if a new card says “target opponent sacrifices a creature,” the extractor should recognize sacrifice-based Removal plus affected-player selection and Edict semantic DNA rather than requiring an unconstrained natural-language invention step.

---

## 4. Novelty / adjudication routing

Not every card should receive the same reasoning budget.

A future analyzer should estimate whether a card is:

1. **Routine** — entirely composed from known patterns and predicates;
2. **Compositional** — known pieces combined in a new way but mechanically straightforward;
3. **Boundary-sensitive** — touches a known hard edge or near-miss;
4. **Novel** — introduces wording/mechanics not represented in the semantic registry;
5. **Ambiguous / rules-sensitive** — needs rules research or human/higher-model adjudication.

Routine cards should be cheap and fast.

Novel/boundary-sensitive cards should receive deeper analysis and produce a STOP/NEEDS-ADJUDICATION state when the system cannot justify a classification confidently.

The automation system must never manufacture certainty merely to keep throughput high.

---

## 5. Individual card image ingestion

The Captain should eventually be able to submit a single card image and request immediate Foundry ingestion.

This is especially useful during preview seasons, when the canonical bulk corpus will necessarily lag newly revealed cards.

### 5.1 Intended flow

```text
uploaded card image
-> visual transcription / card-frame parsing
-> identity + set/collector metadata when visible
-> transcription confidence check
-> source/provenance record
-> authoritative lookup when available
-> semantic ingestion pipeline
-> provisional card page / thesaurus entry
-> later reconciliation with official Oracle data
```

### 5.2 Image text is evidence, not automatically Oracle authority

For a preview card not yet present in an authoritative feed, the image may temporarily be the best available rules-text evidence.

The system should therefore distinguish at least:

- `OFFICIAL_ORACLE` — authoritative current card text resolved from the canonical data source;
- `OFFICIAL_PREVIEW` — officially published preview evidence, not yet reconciled into canonical Oracle feed;
- `THIRD_PARTY_PREVIEW` — lower-confidence preview evidence requiring provenance/caution;
- `USER_IMAGE_TRANSCRIPTION` — user-submitted evidence whose transcription has not yet been externally verified.

A card may be published to a preview/new-card surface immediately while remaining visibly provisional.

When authoritative Oracle data arrives, Foundry should automatically compare:

- name;
- mana cost;
- types/subtypes;
- rules text;
- power/toughness/loyalty/defense where applicable;
- faces/layout;
- semantic assertions derived from the earlier transcription.

Any material difference should trigger reanalysis rather than silently preserving stale preview semantics.

### 5.3 Human correction loop

If image transcription is uncertain, the UI should permit a rapid correction before semantic publication.

The ideal interaction is not a full manual data-entry form. The system should show the extracted card facts, highlight low-confidence fields, and allow the Captain to correct only what is wrong.

---

## 6. Immediate website publication vs semantic authority

“Push it into the website immediately” should not require collapsing provisional and canonical truth.

Recommended future state:

- a preview/newly-ingested card can become searchable quickly;
- the card receives a visible evidence status;
- provisional semantic assertions are versioned and traceable to the exact source text/image;
- official reconciliation can promote the record without changing its stable card identity where possible;
- semantic differences caused by Oracle changes are diffed and re-derived.

This lets Foundry be timely without sacrificing the project-wide truth-preservation discipline.

---

## 7. Incremental corpus refresh

After the initial final clean-room corpus pass, normal corpus maintenance should be incremental.

For each upstream card-data refresh:

1. compare card identities and Oracle/rules-relevant fields against the previous authoritative snapshot;
2. partition into:
   - unchanged cards;
   - new cards;
   - Oracle-changed cards;
   - legality/status changes;
   - rules/keyword changes that may alter derived semantics;
3. reanalyze only affected cards by default;
4. run dependency-aware regressions for cards whose semantics rely on a changed keyword/rule/definition;
5. publish a semantic delta report;
6. retain reproducible version/provenance for every accepted assertion.

A new set should therefore usually mean hundreds of new/changed cards, not a forced re-read of 30,000+ unchanged cards.

---

## 8. Definition changes require affected-corpus reruns

Incremental ingestion cannot mean that old cards become frozen forever.

When a canonical semantic definition changes, Foundry should identify the likely affected population from mechanical facts and rerun that population.

Examples:

- changing the hard predicate for Card Engine should trigger re-evaluation of cards with relevant recurring/card-output processor signatures;
- changing the definition of Board Wipe should re-evaluate mass battlefield/stack/neutralization candidates;
- changing a Keyword Consequence Registry entry should re-evaluate every card invoking that keyword;
- changing a predefined token's rules meaning should re-evaluate generators/consumers of that token type.

The future semantic system therefore needs **dependency tracing from accepted assertion back to the definition/rule/keyword facts that produced it**.

---

## 9. Semantic artifact expected per analyzed card

The future analyzer should produce a rich structured record rather than only a list of labels.

At minimum, preserve:

- exact source evidence and source version;
- card/face/paragraph locality;
- normalized operations;
- keyword expansions invoked;
- mechanical primitives;
- zones and transitions;
- trigger/activation/static/replacement architecture;
- produced events and objects;
- consumed/listened-for events;
- costs and resource conversions;
- targeting/selection authority;
- scope and quantity;
- restrictions and eligibility;
- timing and delayed consequences;
- token definitions/functions;
- functional memberships;
- lower-level semantic DNA;
- positive membership reasons;
- negative/non-event facts where material;
- dependencies/prerequisites;
- confidence / ambiguity status;
- semantic-definition version;
- plain-English explanation.

This rich representation is what permits future deck reasoning without rescanning raw Oracle text from scratch.

---

## 10. Relation to future Complete My Deck

Automated semantic ingestion strengthens the later strategic layer, but the two must remain separate.

The ingestion system answers:

> **What does this card mechanically produce, consume, require, and accomplish?**

The future Complete My Deck layer may then ask:

> **Given this specific deck, how often and how effectively can those functions be realized, and what additions/substitutions satisfy the player's stated goals?**

The second layer may use probability, simulation, deck construction knowledge, external strategic evidence, and recommendation logic.

It must consume rather than overwrite canonical semantic truth.

---

## 11. Future acceptance target

A mature automated ingestion system should be evaluated on more than raw throughput.

Useful metrics include:

- exact mechanical-fact agreement with audited ground truth;
- semantic membership precision/recall by family;
- near-miss false-positive rate;
- missed-function false-negative rate;
- keyword-expansion accuracy;
- producer/consumer event-signature accuracy;
- deterministic rerun stability;
- percentage automatically accepted;
- percentage routed to adjudication;
- correction rate after human audit;
- semantic drift after definition/rules updates;
- time from official preview/new Oracle record to searchable Foundry entry.

The goal is not “zero human review.” The goal is to spend human/higher-model attention only where it adds information.

---

## 12. Control boundary

This document is a tabled future-state design note.

It does **not** authorize:

- implementation of image ingestion;
- website preview publishing;
- automated semantic acceptance;
- live corpus mutation;
- current broad corpus analysis;
- S16B freeze;
- AQ4 resumption;
- Bridge v0 activation;
- Step6;
- merge;
- accepted-head or `main` movement.

Any activation requires a later bounded architecture/implementation contract.
