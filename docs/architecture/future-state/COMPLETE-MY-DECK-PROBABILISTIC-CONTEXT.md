# Future State — Complete My Deck Probabilistic Context

**Date:** 2026-09-19  
**Status:** **CAPTAIN-DIRECTED FUTURE PRODUCT CONCEPT — TABLED; NO CURRENT IMPLEMENTATION AUTHORIZATION**

## 1. Purpose

This document isolates the future probabilistic/deck-context direction previously recorded inside `docs/architecture/FOUNDRY-PRODUCT-INTERACTION-MODEL-2026-09-18.md`.

It is intentionally separate from the current Foundry core.

Current Foundry canonical semantics should answer:

> **What can this card mechanically do?**

A later Complete My Deck layer may answer:

> **How reliably, how early, and at what practical throughput is this deck likely to realize that function?**

Deck composition must not rewrite canonical card semantics.

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

The future strategic layer consumes canonical truth; it does not replace it.

---

## 3. Why rich corpus extraction matters now

The final semantic corpus should preserve enough detail to support later quantitative reasoning without rereading raw Oracle text from scratch.

Important retained facts include:

- mana value / mana cost;
- color requirements;
- source/host requirements;
- qualifying input identity and quantity;
- zones and destinations;
- timing/windows;
- trigger granularity;
- whether input is consumed;
- whether output is capped/compressed/scalable;
- setup dependency vs operating dependency;
- turn-structure bounds;
- resource conversions;
- Card Access / Tutor / Ramp / Cost Reduction / recursion support;
- producer/consumer event signatures.

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
- conditional models incorporating tutors, draw, recursion, ramp, cost reduction, alternate costs, and mulligans.

The output should expose material assumptions rather than collapse everything into an unexplained score.

Preferred explanation shape:

1. identify the semantic function being evaluated;
2. identify the deck variables that enable/inhibit it;
3. report probability / expected timing / expected throughput where justified;
4. explain which variables materially drove the result.

Avoid opaque `63/100 synergy` style output as the sole explanation.

---

## 5. Explore example

Explore remains canonical Ramp/card-resource functionality even when a particular deck has too few lands to exploit its extra-land permission reliably.

A later Complete My Deck layer could estimate:

- probability of having enough lands to cast Explore on a relevant turn;
- probability another playable land remains after the normal land drop;
- expected turn when the additional-land permission is realizable;
- mulligan effects;
- effect of draw/Card Access on finding lands;
- land-to-hand/tutor effects;
- other ramp changing the practical cast/realization turn.

A raw rule such as `25 lands => Explore bad` is too crude. Other deck variables can materially change realization.

---

## 6. Sram example

Sram, Senior Edificer remains a canonical Card Engine even if placed in a deck with very few Auras, Equipment, or Vehicles.

Future deck-context reasoning asks whether the deck supplies useful fuel.

Raw qualifying-card count is insufficient.

Two decks could each contain 30 qualifying Sram inputs but have very different practical throughput if:

- one set of inputs is mostly cheap;
- the other is mostly expensive;
- color requirements differ;
- ramp/cost reduction differs;
- card access differs;
- recursion differs;
- expected castability differs.

Useful future measures include:

- qualifying input count;
- mana-cost/value distribution;
- color/castability distribution;
- probability of one or more usable inputs when Sram is active;
- expected number of qualifying casts in one turn;
- expected trigger throughput by turn/resource state;
- expected delay until the engine begins generating card resources.

The same pattern applies to sacrifice engines, landfall engines, artifact engines, and other mechanisms where raw support count is not equivalent to usable throughput.

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

Format/player-count context can matter both for strategy and for some derived semantics such as multiplayer Card Advantage accounting.

---

## 8. Separation from current Foundry core

Current Foundry core remains descriptive:

- what functions are represented;
- which cards perform them;
- how cards are mechanically similar/different;
- how a proposed substitution changes factual semantic counts/coordinates.

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
