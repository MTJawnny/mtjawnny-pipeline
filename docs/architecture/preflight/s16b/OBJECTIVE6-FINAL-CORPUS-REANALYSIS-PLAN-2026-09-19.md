# Objective 6 — Final Corpus Reanalysis Plan

**Date:** 2026-09-19  
**Revised:** 2026-09-20 after whole-vocabulary / naming audit and stale cleanup  
**Status:** **CAPTAIN-DIRECTED FUTURE EXECUTION PLAN — NOT AUTHORIZED FOR CORPUS EXECUTION**  
**Current semantic routing:** `OBJECTIVE6-POST-AUDIT-CURRENT-STATE-2026-09-19.md`

## 1. Purpose

After Objective 6 completes its remaining bounded validation and receives an explicit formal semantic freeze, Foundry should perform a **clean-room reanalysis of the entire in-scope playable-card corpus**.

This final pass prioritizes semantic correctness and provenance over throughput.

> **There is no value in spending this much effort on semantic precision and then rushing the one pass that applies it to every card.**

---

## 2. Current readiness state

Already completed:

- broad concept-definition work;
- Card Access prior-art research;
- Card Advantage prior-art/adversarial research;
- weird-card adversarial corpus hunt;
- whole-vocabulary adversarial semantic audit;
- global naming audit;
- structural corrections to key candidate records;
- stale-document cleanup and current-state routing.

Still required before an actual full-corpus run:

1. **Card Resource Delta stateful fixture validation**;
2. **Sample Selection retrieval/UI fixture validation**;
3. **Keyword Consequence Registry census/design gate**;
4. final stale-routing verification;
5. explicit Captain-authorized **formal S16B freeze review and freeze**, if the evidence passes;
6. exact supported-format/card-scope resolution from the execution-time authoritative corpus snapshot;
7. a stratified calibration run under the frozen semantic contract.

Old Foundry assertions may be used as comparison/evidence but must not force preservation of prior classifications.

---

## 3. Corpus scope

Captain direction is to focus the production corpus on cards legal in formats the product supports rather than spend equivalent analytical effort on irrelevant/unplayable cards.

The exact supported-format union must be resolved immediately before execution using current authoritative legality data.

If Commander remains in scope, legality filtering may still leave a population close to the overall Oracle-card corpus. Treat legality filtering as product relevance, not an assumed major workload reduction.

Any corpus-size estimate recorded during planning is provisional until regenerated from the execution snapshot.

---

## 4. Atomic batch size

### Default

**25 cards per deep-analysis batch** remains the recommended starting point.

Rationale:

- limits the blast radius of a semantic defect;
- remains human-reviewable;
- allows per-card evidence/explanations;
- amortizes setup overhead without creating opaque output walls.

### Adaptive sizing

- **10–15 cards** for highly adversarial/complex populations;
- **25 cards** normal default;
- up to **50 cards** only for well-understood/simple populations after measured validation demonstrates stability.

Do not increase batch size merely to meet a calendar target.

---

## 5. Review cadence

Recommended hierarchy:

- **25 cards** — atomic execution/review batch;
- **100 cards** — semantic checkpoint;
- **500 cards** — larger regression epoch;
- corpus-wide milestones only after smaller checkpoints stay stable.

Initial parallelism should remain bounded. A reasonable starting ceiling is approximately four ordinary batches / **100 cards in flight**, with lower concurrency for pathological populations.

The purpose is to prevent one bad predicate or registry expansion from contaminating thousands of cards before detection.

---

## 6. Per-card analytical depth

A final accepted card record should preserve, where applicable:

- exact Oracle/rules evidence and locality;
- face/paragraph ownership;
- Keyword Consequence expansions;
- mechanical primitives;
- Producer Signatures;
- Consumer Signatures;
- zones and transitions;
- trigger/activation/static/replacement architecture;
- targets / selection authority;
- scope / quantity;
- costs, Alternative Costs, Additional Costs, Cost Reduction, and Payment Methods;
- Card Use Permission and Permission Window;
- restrictions and eligibility;
- token identities and functional consequences;
- copied/inherited payload behavior;
- Additional Execution and copy provenance;
- timing / delayed events;
- relevant negative/non-event facts;
- strong functional memberships;
- surfaced facets/tags;
- semantic DNA / community aliases where retrieval-relevant;
- dependencies / realization prerequisites;
- processor input/aggregation/firing/output/retention facts;
- typed resource facts and Card Resource Delta inputs;
- derived Role Compression data where appropriate;
- ambiguity/adjudication state;
- semantic/rules version provenance;
- concise human-readable explanation of important matches.

The output is intentionally richer than a tag list.

`Engine`, `Card Engine`, and similar phrases may be derived/search views over processor facts; they are not canonical family memberships to stamp onto the corpus.

---

## 7. Execution architecture

Do not ask one unconstrained model to rediscover Magic from raw text independently for every card.

Preferred cascade:

```text
Oracle / Comprehensive Rules evidence
-> normalized card/face text
-> canonical Keyword Consequence expansion
-> deterministic mechanical fact extraction where possible
-> Producer / Consumer Signatures
-> strong functional predicates + surfaced facets
-> processor/resource/accounting facts
-> model reasoning for compositional/context-sensitive questions
-> adversarial / ambiguity checks
-> higher-reasoning or human adjudication only where required
-> accepted assertion + explanation + provenance
```

Known structures should be reused deterministically.

A Myriad card should invoke the canonical Myriad consequence map rather than rediscovering Myriad per card.

---

## 8. Calibration before full execution

Before a 30k+-scale run, execute a **200-card stratified calibration** under the frozen contract.

Suggested composition:

- 50 simple / straightforward cards;
- 50 ordinary modern cards;
- 50 complex cards;
- 50 deliberately adversarial/weird cards.

The adversarial stratum should include examples involving:

- compound keywords;
- copies and Additional Execution;
- replacement effects;
- multiplayer scaling;
- MDFCs / multiple faces / unusual layouts;
- death vs LTB vs exile distinctions;
- temporary tokens;
- unusual zones and Permission Windows;
- Alternative Cost versus Payment Method distinctions;
- permission/tax/denial effects;
- multiple overlapping functions;
- processor throughput/firing-cap boundaries;
- Card Resource Delta edge cases;
- Sample Selection vs Tutor vs Library Traversal;
- Top-Library Access and opponent-owned card access.

Measure at minimum:

- median and p90/p95 processing time per card;
- assertions/signatures per card;
- automatic vs adjudication rate;
- human audit time;
- corrected assertion rate;
- false-positive / false-negative rates by family/facet/signature;
- near-miss error rate;
- deterministic rerun stability;
- definition/predicate violations;
- cross-batch semantic consistency.

Only after calibration should card count be converted into a serious duration estimate.

---

## 9. Working time estimate — planning only

Before calibration, any per-card runtime remains an engineering estimate.

Prior planning assumptions remain illustrative only:

- simple card: ~5–15 seconds;
- ordinary card: ~15–40 seconds;
- complex card: ~40–90 seconds;
- genuinely adversarial card: ~1–5+ minutes or explicit adjudication.

A corpus average around 30–60 seconds per card would imply hundreds of compute-hours before review/retries/adjudication for a 30k+-card population.

A calendar envelope of several weeks may therefore be reasonable, but calibration evidence must replace planning estimates before execution scheduling.

---

## 10. STOP / adjudication is a successful outcome

Supported run states should include:

- PASS / accepted;
- NEEDS ADJUDICATION;
- RULE/DEFINITION GAP;
- EVIDENCE GAP;
- NOVEL MECHANIC / REGISTRY GAP;
- other explicit bounded stop states.

A forced classification is worse than an honest unresolved card.

Stopped cards remain isolated from accepted assertions until the underlying issue is resolved and affected populations are rerun where necessary.

---

## 11. Definition drift during execution

If a frozen definition must change after analysis begins:

1. identify affected assertions/cards through dependency/provenance records;
2. stop related downstream batches if continuing would multiply stale semantics;
3. version the change explicitly;
4. rerun the affected population;
5. preserve before/after metrics;
6. confirm unaffected populations remain stable.

`Analyzed` is meaningless without the semantic/rules version that produced the result.

---

## 12. Relationship to continuous future ingestion

The final whole-corpus reanalysis establishes the trustworthy new baseline.

After that baseline exists, ordinary maintenance should move to incremental ingestion rather than repeating the entire corpus run for each release.

Future design:

`docs/architecture/future-state/AUTOMATED-SEMANTIC-INGESTION-AND-CORPUS-REFRESH.md`

New/Oracle-changed cards receive incremental analysis; definition/rules changes trigger targeted dependency-aware reruns.

---

## 13. Control boundary

This plan does **not** authorize the corpus run now.

It does not authorize:

- corpus mutation/reclassification;
- S16B freeze;
- implementation acceptance;
- AQ4 resumption;
- Bridge v0 activation;
- Step6;
- merge;
- movement of accepted implementation head or `main`.

A later explicit Captain direction and bounded execution contract are required.
