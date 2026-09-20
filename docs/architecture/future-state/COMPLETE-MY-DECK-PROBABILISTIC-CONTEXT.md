# Future State — Complete My Deck Probabilistic Context

**Date:** 2026-09-19  
**Revised:** 2026-09-20 after Objective 6 adversarial audit  
**Status:** **CAPTAIN-DIRECTED FUTURE PRODUCT CONCEPT — TABLED; NO CURRENT IMPLEMENTATION AUTHORIZATION**  
**Current semantic routing:** `docs/architecture/preflight/s16b/OBJECTIVE6-POST-AUDIT-CURRENT-STATE-2026-09-19.md`

## 1. Purpose

This document isolates the future probabilistic/deck-context direction from the current Foundry core.

Current Foundry canonical semantics should answer:

> **What can this card mechanically do?**

A later Complete My Deck layer may answer:

> **How reliably, how early, and at what practical throughput is this deck likely to realize that function?**

Deck composition must not rewrite canonical card mechanics.

---

## 2. Future reasoning pipeline

Conceptually:

```text
canonical Foundry semantic substrate
-> mechanical prerequisites / dependencies / costs / timing
-> deck supply of those prerequisites
-> probability / timing / throughput model
-> strategic interpretation
-> explainable recommendation or deck-completion suggestion
```

The strategic layer consumes canonical truth; it does not replace it.

---

## 3. Why rich corpus extraction matters now

The final semantic corpus should preserve enough detail to support later quantitative reasoning without rereading raw Oracle text from scratch.

Important retained facts include:

- mana value / mana cost;
- color requirements;
- source/host requirements;
- qualifying input identity and quantity;
- zones and destinations;
- timing / Permission Windows;
- trigger and input aggregation;
- whether input is consumed;
- output magnitude and multiplicity;
- intrinsic firing/opportunity caps;
- setup dependency vs operating dependency;
- resource conversions;
- Card Use Permission and `PLAY`/`CAST` distinction;
- Tutor / Sample Selection / Library Traversal facts;
- Ramp / Cost Reduction / Alternative Cost / Payment Method facts;
- Additional Execution and copy provenance;
- Producer / Consumer Signatures;
- typed resource facts and Card Resource Delta inputs.

Governing maxim:

> **Extract rich mechanical truth now; derive strategic usefulness later.**

---

## 4. Probability and simulation

Future deck-context questions may use different quantitative methods depending on complexity.

Potential methods include:

- exact combinatorics / hypergeometric calculations;
- deterministic state models;
- Monte Carlo simulation;
- turn-by-turn resource simulations;
- conditional models incorporating tutors, draw/access, recursion, ramp, cost/payment mechanics, mulligans, and interaction.

The output should expose material assumptions rather than collapse everything into an unexplained score.

Preferred explanation shape:

1. identify the canonical function or processor behavior being evaluated;
2. identify the deck variables that enable or inhibit it;
3. report probability / expected timing / expected throughput where justified;
4. explain which variables materially drove the result.

Avoid opaque `63/100 synergy` style output as the sole explanation.

---

## 5. Explore fixture

Explore remains canonical Ramp behavior regardless of deck composition because it grants an additional-land-play opportunity in addition to drawing a card.

A later Complete My Deck layer may estimate:

- probability of having enough mana to cast Explore at a relevant time;
- probability an additional playable land remains after the normal land play;
- expected turn when the extra-land permission is realizable;
- mulligan effects;
- Card Access effects on finding lands;
- land-to-hand / Tutor effects;
- other Ramp effects changing the cast/realization turn.

A raw rule such as `25 lands => Explore bad` is too crude. Other deck variables can materially change realization.

---

## 6. Sram fixture — processor throughput without canonical Engine membership

The Objective 6 audit demoted `Engine` and `Card Engine` from canonical ontology membership to derived/search/community labels over harder processor facts.

Sram, Senior Edificer remains a useful throughput fixture because its Oracle-defined behavior listens for qualifying Aura, Equipment, and Vehicle casts and can draw a card for each qualifying event.

Future deck-context reasoning asks whether the deck supplies usable fuel.

Raw qualifying-card count is insufficient.

Two decks could each contain 30 qualifying Sram inputs but have very different practical throughput if:

- one set of inputs is mostly cheap;
- the other is mostly expensive;
- color requirements differ;
- ramp/cost reduction/payment methods differ;
- card access differs;
- recursion differs;
- expected castability differs.

Useful future measures include:

- qualifying input count;
- mana-cost/value distribution;
- color/castability distribution;
- probability of one or more usable inputs while Sram is active;
- expected number of qualifying casts in one turn;
- expected trigger throughput by turn/resource state;
- expected delay until the processor begins generating additional card access.

The same pattern applies to sacrifice processors, landfall processors, artifact processors, scheduled recurring sources, and other mechanisms where raw support count is not equivalent to realized throughput.

The UI may still let a player search for `card engine`; that search is derived from processor facts rather than a canonical `CARD_ENGINE = true` label.

---

## 7. Format inference

A supplied list may be a partial deck or complete deck.

Future context inference should not rely on crude rules such as `100 cards => Commander` alone.

Potential evidence includes:

- deck size;
- singleton/duplicate structure;
- legality;
- commander designation/eligibility;
- sideboard information;
- other available metadata.

Format/player-count context can matter for strategy and for derived multiplayer resource accounting.

---

## 8. Separation from current Foundry core

Current Foundry core remains descriptive:

- what canonical functions and mechanical signatures are represented;
- which cards produce or consume relevant events/resources;
- how cards are mechanically similar/different;
- how a proposed substitution changes factual semantic counts/coordinates;
- how typed resource/accounting facts change when a defined comparison context exists.

Complete My Deck is the later layer allowed to make strategic recommendations.

This separation protects canonical semantic truth from deck-building heuristics and shifting metagame conventions.

---

## 9. Control boundary

This document does not authorize:

- Complete My Deck implementation;
- probabilistic scoring;
- recommendations;
- simulation infrastructure;
- semantic changes;
- corpus execution;
- S16B freeze;
- merge/main movement;
- AQ4 / Bridge v0 / Step6 changes.

Activation requires a later bounded architecture/implementation contract.
