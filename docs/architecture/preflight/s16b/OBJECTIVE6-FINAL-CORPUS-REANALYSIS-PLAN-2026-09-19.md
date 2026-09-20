# Objective 6 — Final Corpus Reanalysis Plan

**Date:** 2026-09-19  
**Status:** **CAPTAIN-DIRECTED FUTURE EXECUTION PLAN — NOT YET AUTHORIZED FOR CORPUS EXECUTION**

## 1. Purpose

After the Objective 6 semantic vocabulary, keyword consequences, and cross-concept boundaries receive their final audit, Foundry should perform a **clean-room reanalysis of the entire in-scope playable-card corpus**.

This final pass should prioritize semantic correctness and provenance over throughput.

Governing principle:

> **There is no value in spending this much effort on semantic precision and then rushing the one pass that applies it to every card.**

The final pass should take as long as necessary to produce a trustworthy substrate.

---

## 2. Preconditions

Do not begin the final full-corpus reanalysis merely because the current concept-by-concept conversation ends.

Required readiness work includes:

1. finish the broad concept-definition pass;
2. complete the whole-vocabulary semantic audit;
3. complete the canonical naming/tapestry review;
4. perform dedicated adversarial/research passes for broad concepts where warranted, especially Card Advantage;
5. complete the Keyword Consequence Registry / compound-keyword distillation gate;
6. validate primitives, event/output signatures, qualifiers, dependencies, and retrieval-semantic DNA against hard examples and near-misses;
7. freeze/version the semantic contract used by the run;
8. define the exact card legality / format scope from a current authoritative corpus snapshot;
9. complete a stratified calibration run before estimating total duration.

Old Foundry assertions may be used as comparison/evidence, but they must not force preservation of prior classifications.

---

## 3. Corpus scope

Captain direction is to focus the final production corpus on cards legal in formats that are actually being played rather than spend equivalent analytical effort on cards unusable in the supported product context.

The exact supported-format union must be resolved immediately before execution using current authoritative legality data.

Important practical note:

- if Commander remains in scope, the eligible population is expected to remain close to the size of the overall Oracle-card corpus because Commander legality is broad;
- therefore legality filtering should be treated as a product relevance rule, not assumed to create a dramatic workload reduction.

Any numerical corpus-size estimate recorded during planning is provisional until regenerated from the execution snapshot.

---

## 4. Atomic batch size

### Default

**25 cards per deep-analysis batch** is the current recommended default starting point.

Rationale:

- small enough that a semantic defect cannot silently spread across hundreds/thousands of cards before review;
- large enough to amortize pipeline/setup overhead;
- reviewable as a coherent packet;
- permits per-card evidence and explanations without creating an opaque output wall.

### Adaptive sizing

Batch size should respond to complexity:

- **10–15 cards** for highly adversarial/complex populations;
- **25 cards** normal default;
- up to **50 cards** only for well-understood/simple cards after measured validation shows the pipeline is stable.

Do not increase batch size merely to meet a calendar target.

---

## 5. Review cadence

Recommended hierarchy:

- **25 cards** — atomic execution/review batch;
- **100 cards** — semantic checkpoint (four ordinary batches);
- **500 cards** — larger regression epoch;
- corpus-wide milestones only after the smaller checkpoints stay stable.

Initial parallelism should remain bounded. A reasonable starting ceiling is approximately four ordinary batches / **100 cards in flight**, with lower concurrency for difficult families.

The purpose is to limit correlated semantic error. Massive parallelization before stability is demonstrated could make one bad predicate contaminate thousands of cards.

---

## 6. Per-card analytical depth

A final accepted card record should be able to preserve, where applicable:

- exact Oracle/rules evidence and locality;
- face/paragraph ownership;
- keyword consequence expansions;
- mechanical primitives;
- event/output producer signatures;
- consumer/listener signatures;
- zones and transitions;
- trigger/activation/static/replacement architecture;
- targets / selection authority;
- scope / quantity;
- costs and resource conversions;
- restrictions and eligibility;
- token identities and functional consequences;
- copied/inherited payload behavior;
- timing / delayed events;
- relevant non-events / negative facts;
- hard functional memberships;
- functional qualifiers;
- semantic DNA / community aliases where retrieval-relevant;
- dependencies / realization prerequisites;
- Role Compression / Engine / other cross-cutting structure when applicable;
- ambiguity/adjudication state;
- definition/rules version provenance;
- concise human-readable explanation of each important membership.

The output is intentionally richer than a tag list.

---

## 7. Execution architecture

Do not ask one unconstrained model to rediscover Magic from raw text independently for every card.

Preferred cascade:

```text
Oracle / Comprehensive Rules evidence
-> normalized card/face text
-> canonical keyword consequence expansion
-> deterministic mechanical fact extraction where possible
-> event/output signatures
-> hard semantic predicate evaluation
-> model reasoning for contextual/compositional questions
-> adversarial / ambiguity checks
-> higher-reasoning or human adjudication only where required
-> accepted assertion + explanation + provenance
```

Known structures should be reused deterministically.

A Myriad card should invoke the canonical Myriad consequence map; it should not spend a full reasoning cycle rediscovering the rules of Myriad.

---

## 8. Calibration before full execution

Before a 30k+-scale run, execute a **200-card stratified calibration**.

Suggested initial composition:

- 50 simple / straightforward cards;
- 50 ordinary modern cards;
- 50 complex cards;
- 50 deliberately adversarial/weird cards.

The adversarial stratum should intentionally contain examples involving:

- compound keywords;
- copying;
- replacement effects;
- multiplayer scaling;
- MDFCs / multiple faces / unusual layouts;
- death vs LTB vs exile distinctions;
- temporary tokens;
- alternate zones/costs;
- permission/tax/lockdown effects;
- multiple overlapping functional roles;
- Engines / throughput boundaries;
- Card Advantage edge cases.

Measure at minimum:

- median and p90/p95 processing time per card;
- assertions per card;
- event signatures per card;
- automatic vs adjudication rate;
- human audit time;
- corrected assertion rate;
- false-positive / false-negative rates by semantic family;
- near-miss error rate;
- deterministic rerun stability;
- definition/predicate violations;
- cross-batch semantic consistency.

Only after this calibration should the project convert card count into a serious duration estimate.

---

## 9. Working time estimate — planning only

Before calibration, any per-card runtime is an engineering estimate rather than a measured fact.

Current planning assumption for full-depth analysis:

- simple card: approximately 5–15 seconds of automated/deep semantic processing;
- ordinary card: approximately 15–40 seconds;
- complex card: approximately 40–90 seconds;
- genuinely adversarial card: approximately 1–5+ minutes or explicit adjudication.

A corpus-wide average in the rough neighborhood of **30–60 seconds per card** would make a 30k+-card first pass hundreds of compute-hours before review/retries/adjudication.

Therefore a calendar duration on the order of **several weeks (roughly 4–8 weeks as a planning envelope)** is entirely plausible for a deliberately thorough final program.

This is not a deadline and should not be optimized against until real calibration exists.

---

## 10. STOP / adjudication is a successful outcome

The final pass should support:

- PASS / accepted;
- NEEDS ADJUDICATION;
- RULE/DEFINITION GAP;
- EVIDENCE GAP;
- NOVEL MECHANIC / REGISTRY GAP;
- other explicit bounded stop states.

A forced classification is worse than an honest unresolved card.

Cards stopped for adjudication should remain isolated from accepted assertions until the underlying question is resolved and affected populations are rerun where necessary.

---

## 11. Definition drift during the run

If a definition changes after analysis has begun:

1. identify the affected assertions/cards through dependency/provenance records;
2. stop related downstream batches if continuing would multiply stale semantics;
3. rerun the affected population under the new version;
4. preserve before/after metrics;
5. confirm unaffected populations remain stable.

The final pass must be version-aware. “Analyzed” is meaningless without the semantic/rules version that produced the result.

---

## 12. Relationship to continuous future ingestion

The final whole-corpus reanalysis is intended to establish a trustworthy new baseline.

After that baseline exists, ordinary maintenance should move to incremental ingestion rather than repeating the entire whole-corpus program for each release.

Future design is recorded in:

`docs/architecture/future-state/AUTOMATED-SEMANTIC-INGESTION-AND-CORPUS-REFRESH.md`

New/Oracle-changed cards should receive incremental analysis; definition/rules changes should trigger targeted affected-population reruns.

---

## 13. Control boundary

This plan does **not** authorize the final corpus run now.

It does not authorize:

- corpus mutation/reclassification;
- S16B freeze;
- implementation acceptance;
- AQ4 resumption;
- Bridge v0 activation;
- Step6;
- merge;
- movement of accepted implementation head or `main`.

A later explicit Captain execution direction and bounded contract are required.
