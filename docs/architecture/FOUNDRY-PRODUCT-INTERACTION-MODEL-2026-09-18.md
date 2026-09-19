# Foundry Product Interaction Model

**Date:** 2026-09-18  
**Status:** Captain product direction — documentation only; not semantic authority and not implementation acceptance  
**Base accepted implementation head:** `fdb66e659d81f4efa373ab8e86329485c0205966`

## Purpose

This document records the current intended user interaction model for Foundry so semantic, UI, and later implementation work share the same product target.

Foundry is not currently intended to act as an AI advisor that tells a player what they should play. The core product is a deterministic semantic engine, browser, measurement surface, and reversible deck-editing workspace.

Governing product principle:

> **Foundry reports semantic composition and change; it does not prescribe desired composition.**

Recommendations are intentionally deferred to the future **Complete My Deck** layer.

---

## 1. One semantic engine, multiple user surfaces

Foundry should expose the same underlying semantic representation through several entry points rather than building separate semantic systems for each feature.

### 1.1 Card Thesaurus / seeded card view

The user starts from one card.

The card page should allow the user to move through increasingly broad relationships such as:

1. **Same / near-exact card language** — cards with the same or closely corresponding Oracle-language structure.
2. **Same game function** — cards that accomplish substantially the same gameplay job despite different wording.
3. **Similar game function** — cards that share important functional dimensions but differ in mechanism, scope, timing, dependency, cost, or other coordinates.

The user is browsing a semantic neighborhood. Foundry is not selecting a preferred replacement.

### 1.2 Deck workspace

The same engine should accept a list ranging from a few cards to an entire deck.

An uploaded deck is not primarily treated as one opaque semantic object. Instead:

- every card remains an individual entry point into the MTG Thesaurus;
- the deck supplies aggregate context and hard counts;
- the user may click any card and inspect same-language, same-function, and similar-function alternatives;
- selecting an alternative replaces the selected card in the working deck;
- replacement is a reversible transaction with Undo/Redo support;
- final output can be exported as a plain-text list for external deck sites such as Moxfield, Archidekt, ManaBox, or similar tools.

### 1.3 Foundry Explorer / advanced search

The unseeded search surface is separate from the card/deck workflow even though it uses the same semantic substrate.

Explorer should work as progressive faceted browsing: the user adds or removes functional and mechanical filters and the result set narrows to cards satisfying the active intersection.

Conceptually:

- Function: Card Advantage
- Repeatability: Recurring
- Dependency: Opponent action
- Access: Hand
- Mana value: <= 3
- Card type: Enchantment

The vocabulary provides recognizable handles; semantic coordinates provide most of the granularity.

---

## 2. Budget is a mode, not a separate semantic product

The previously discussed “Budget Swapper” should be understood primarily as a user-facing workflow over the same thesaurus/deck engine.

When **Budget mode is OFF**:

- price need not dominate the interface;
- semantic function remains primary.

When **Budget mode is ON**:

- card prices become visible;
- an uploaded deck can automatically sort from most expensive to least expensive;
- replacement candidates can show price and price delta;
- users may constrain results to cheaper alternatives or other price ranges;
- deck total and replacement deltas can update as edits are made.

Budget must not create a second definition of card similarity. It is a constraint/filter layered over semantic equivalence and similarity.

---

## 3. No recommendation behavior in the current Foundry core

The current product should not tell players:

- “you need more removal”;
- “your deck has too little card advantage”;
- “this is the best replacement”;
- “you should cut this card”;
- or any equivalent strategic prescription.

Instead, Foundry reports measurable facts.

Preferred language includes:

- `Removal sources: 9`
- `Graveyard removal: 0 represented`
- `Card advantage sources: 12`
- `Token-generation sources: 5`

Avoid normative wording such as “missing,” “too few,” “too many,” “better,” or “worse” in the core product when it implies a desired deck composition.

The future **Complete My Deck** system may add an explicitly separate strategic/recommendation layer using Foundry as its substrate.

---

## 4. Deck functionality dashboard

When a full or partial deck is loaded, Foundry should aggregate the semantic assertions on its cards and expose them as hard counts and drill-downs.

Examples of top-level functional counts may include:

- removal;
- card advantage;
- ramp / mana acceleration;
- token generation;
- protection / board preservation;
- graveyard interaction;
- tutors / library access;
- sweepers;
- sacrifice infrastructure;
- and other ratified functional concepts.

These are descriptive measurements only.

### 4.1 Drill-downs may overlap

A single card may contribute to multiple counts and subcounts. Counts do not need to form mutually exclusive buckets.

For example, a Removal tab could later expose overlapping coordinates such as:

- creature interaction;
- artifact interaction;
- enchantment interaction;
- planeswalker interaction;
- graveyard interaction;
- targeted;
- mass/sweeper;
- destroy;
- exile;
- bounce;
- sacrifice-based;
- temporary vs persistent;
- other mechanically justified distinctions.

The exact semantic vocabulary remains subject to Objective 6 ratification.

---

## 5. Counterfactual replacement preview

A core deck-workspace capability is to show the factual semantic delta that would occur if one card were replaced by another **before the user commits the change**.

Example shape only:

```text
If Card A is replaced by Card B:
Removal sources:       9 -> 8
Token generation:      4 -> 5
Card advantage:       12 -> 12
Recurring CA sources:  3 -> 3
Deck price:          $614 -> $597
```

Foundry does not append a judgment that the resulting deck is healthier, weaker, more balanced, or preferable.

After replacement:

- deck-level counts recalculate;
- the working deck updates;
- Undo reverses the transaction;
- Redo may restore it;
- price totals update when Budget mode is active.

---

## 6. Vocabulary design follows the product

Semantic vocabulary must support both card-level similarity and deck-level measurement.

For each ratified functional concept, distinguish:

1. **Membership** — whether the card contributes to the concept's deck-level count.
2. **Coordinates / facets** — how the card performs that function.

This supports a shallow, understandable vocabulary with deep semantic detail underneath.

### 6.1 Avoid naming-rider explosion

Foundry should not automatically create ontology nodes for every adjective combination.

For example, distinctions corresponding informally to:

- hard card advantage;
- potential card advantage;
- recurring card advantage;
- conditional card advantage;
- delayed card advantage;

should normally be modeled as coordinates/facets of a single **Card Advantage** concept unless evidence shows a separate named class is actually necessary.

A user can still filter those properties in Explorer and inspect them in deck/card views without requiring a public noun phrase for every combination.

### 6.2 Hard predicates remain required

Community-sourced terms should receive deterministic Foundry definitions before becoming semantic authority.

A ratified term should eventually specify:

- positive membership predicate;
- exclusions;
- edge cases;
- structural role;
- parent/child/alias relationships when justified;
- useful facets;
- positive examples;
- hard near-misses.

Similarity does not require categorical membership.

---

## 7. Role compression — new semantic concept queued for definition

**Role compression** is now an explicit semantic concept to investigate and define.

Motivating case: **Untimely Malfunction** and similar cards that can perform multiple materially distinct deck functions from a single card slot.

The intended product value is not to praise such a card or recommend it. Foundry should be able to factually expose that one card contributes to multiple functional counters and that replacing it may change several deck-level measurements at once.

Example conceptual behavior:

```text
Card X contributes to:
- Function A
- Function B
- Function C

Replacing Card X with Card Y would change:
- Function A: -1
- Function B: -1
- Function C: unchanged/+1/etc.
```

### 7.1 Definition intentionally unresolved

This document does **not** yet define the hard predicate for `ROLE_COMPRESSION`.

Questions reserved for the semantic pass include:

- Must the functions be available through explicit modal choices, or can one effect satisfy multiple functions simultaneously?
- Must the functions be materially distinct top-level functions rather than closely related facets of one function?
- Does a permanent that accumulates several abilities count differently from a one-shot modal spell?
- Should role compression be a card-level boolean, a count of distinct functional roles, or both?
- How should mutually exclusive modes compare with simultaneous multi-role effects?
- What minimum granularity is required before two capabilities count as separate roles?

Until those are resolved, **role compression is a queued concept, not semantic authority**.

---

## 8. Product architecture summary

The current product model is:

```text
Foundry semantic substrate
|
+-- Card Thesaurus / seeded card view
|   +-- same / near-exact language
|   +-- same function
|   +-- similar function
|   +-- semantic facets
|
+-- Foundry Explorer
|   +-- unseeded faceted search
|   +-- progressive filter intersection
|
+-- Deck Workspace
    +-- card-by-card thesaurus access
    +-- aggregate functionality counts
    +-- drill-down tabs
    +-- counterfactual replacement deltas
    +-- reversible substitutions
    +-- plain-text export
    |
    +-- optional Budget mode
        +-- prices
        +-- price sorting
        +-- price deltas
        +-- economic constraints

Future separate layer:
Complete My Deck
+-- strategic interpretation
+-- recommendations
+-- desired-composition reasoning
```

The same canonical semantic facts and coordinates should power all current surfaces. UI differences must not create competing semantic truth.

---

## 9. Tabled future state — probabilistic deck-context reasoning for Complete My Deck

**Status: CAPTAIN-DIRECTED FUTURE PRODUCT CONCEPT — TABLED. NO CURRENT IMPLEMENTATION AUTHORIZATION.**

This section preserves a future direction for the separate **Complete My Deck** layer. It is not part of current Foundry-core recommendation behavior and does not authorize implementation during Objective 6 / S16B.

### 9.1 Canonical semantics and deck-context evaluation remain separate

Foundry should continue to answer the canonical question:

> **What can this card mechanically do?**

A later deck-context layer may answer a different question:

> **How reliably, how early, and at what practical throughput is this deck likely to realize that function?**

Deck composition must not rewrite canonical card semantics. For example:

- **Explore** remains Ramp even in a deck with too few lands to exploit its additional-land permission reliably;
- **Sram, Senior Edificer** remains a Card Engine even in a deck with very few qualifying Auras, Equipment, or Vehicles.

The future strategic layer may evaluate whether the deck actually supplies the prerequisites needed to realize those functions efficiently.

### 9.2 Deck/format context may be inferred, but not from deck size alone

A supplied list may contain a few cards, a partial deck, or a complete deck. Deck size and singleton structure can provide evidence about likely format context, but heuristics such as `100 cards => Commander` must not become an unquestioned hard rule.

Where possible, future context inference should combine deck size with legality, duplicate structure, commander designation/eligibility, sideboard information, and other available evidence.

### 9.3 Realization prerequisites become quantitative inputs

The semantic substrate should preserve enough mechanical detail that a later layer can convert card requirements into measurable deck-context variables.

Conceptual future pipeline:

```text
canonical Oracle/rules facts
-> semantic function + mechanical prerequisites
-> deck ability to supply those prerequisites
-> probability/timing of realization
-> expected functional output / throughput
-> plain-English explanation of the result
```

Examples of relevant prerequisite dimensions include:

- card/resource type required;
- quantity required;
- mana value and mana cost;
- color requirements;
- timing/window restrictions;
- whether the input must be cast, enter, attack, deal damage, die, be discarded, be sacrificed, etc.;
- whether the input is consumed;
- whether multiple inputs can be processed in one turn/opportunity;
- whether output is capped, compressed, delayed, or scalable;
- whether other Card Access, tutoring, ramp, cost reduction, recursion, or mana production changes the availability of the required inputs.

### 9.4 Explore as a future probabilistic-realization example

Explore's canonical semantics include card replacement/card access plus permission to play an additional land that turn. The additional-land component has a realization prerequisite: the player must actually have another playable land available.

A future Complete My Deck layer could therefore estimate quantities such as:

- probability of having sufficient lands to cast Explore on a relevant turn;
- probability of still having an additional land available after the normal land drop;
- expected turn on which the additional-land permission is realizable;
- effect of mulligans;
- effect of card draw / Card Access on seeing additional lands;
- effect of land tutors or land-to-hand effects;
- effect of mana creatures or other ramp on when Explore can be cast.

A raw statement such as `25 lands = Explore is bad` would be too crude. A low land count may be partly offset by unusually high card throughput or other ways of putting lands into hand. The future layer should model those interactions rather than apply a fixed land-count threshold.

### 9.5 Sram demonstrates why raw qualifying-card count is insufficient

For Sram, merely counting qualifying Auras, Equipment, and Vehicles is not enough to estimate practical Card Engine output.

Two decks can each contain 30 qualifying Sram inputs while producing radically different practical throughput:

- a deck whose qualifying inputs are mostly low-cost can begin triggering Sram earlier and may cast several qualifying cards in one turn;
- a deck whose qualifying inputs are mostly six mana or more may not begin producing Sram card output until much later and may process only one qualifying card in a turn;
- ramp, cost reduction, alternate costs, mana production, and Card Access can materially change those expectations.

The future model therefore needs both **input density** and **input usability/distribution**.

Useful future measurements may include:

- count of qualifying inputs;
- mana-value / mana-cost distribution of those inputs;
- color requirements and expected castability;
- expected turn each class of input becomes castable;
- probability of having one or more qualifying inputs available when Sram is active;
- expected number of qualifying inputs that can be cast in the same turn;
- expected trigger throughput by turn or mana-development state;
- effects of ramp, cost reduction, tutors, general Card Access, and recursion;
- expected delay before the engine begins producing card resources.

This generalizes beyond Sram. A sacrifice engine with many expensive creature inputs, a landfall engine with many lands but few ways to create multiple land entries, or an artifact engine whose artifacts are too costly to chain can all have high raw support counts but low practical throughput.

### 9.6 Preserve rich mechanical truth during future corpus scans

A future deck-context model depends on the corpus scan retaining more than binary semantic labels such as `CARD_ENGINE = true`.

The scan should preserve the mechanical facts needed later to reconstruct:

- timing;
- cost;
- dependency;
- qualifying input identity;
- input quantity and aggregation;
- throughput/caps;
- setup versus operating requirements;
- relevant zones and destinations;
- resource conversion;
- and other mechanically justified coordinates.

The governing design principle is:

> **Extract rich mechanical truth now; derive strategic usefulness later.**

Raw semantic-role counts should remain useful, but they must not become the only retained information if doing so would prevent later probabilistic reasoning.

### 9.7 Mathematics and simulation

Many future questions can be expressed directly with probability distributions such as hypergeometric calculations for cards seen by a particular point in the game.

More complicated cases may require deterministic state models or simulation when mulligans, variable cast turns, tutors, draw engines, cost reduction, alternate mana, recursion, or interacting resources make a single closed-form equation impractical.

The implementation method may vary by question. The output should remain explainable and should expose material assumptions rather than collapsing everything into an opaque synergy score.

Preferred future explanation style:

- identify the card function being evaluated;
- identify the deck variables that support or inhibit realization;
- report the relevant probability/expected timing/throughput where justified;
- explain which variables materially drove the result.

Avoid an unexplained `63/100 synergy` style score as the sole output.

### 9.8 Architectural boundary

This future layer should consume canonical Foundry semantics rather than redefining them.

Conceptually:

```text
Foundry canonical semantic substrate
-> mechanical prerequisites / qualifiers
-> deck-context measurements
-> probabilistic or simulated realization model
-> strategic interpretation / recommendation
```

This preserves the current separation between deterministic semantic truth and later strategic judgment.

Nothing in this section authorizes implementation now.

---

## 10. Immediate consequence for Objective 6

When semantic review resumes, evaluate each vocabulary term with two product questions in addition to its hard definition:

1. **Does this deserve a named functional counter/category?**
2. **Which distinctions underneath it are useful user-facing facets rather than additional named terms?**

The current vocabulary inventory is not presumed exhaustive. Missing identifiers discovered through this process should be captured and evaluated deliberately.

Current examples already under discussion include `cantrip`, `card advantage`, mana/ramp families, removal/interaction, board wipes/wraths, tutors/library access, protection, stax/hatebear, and the newly queued `role compression` concept.

---

## 11. Control boundary

This document records product direction only.

It does not:

- accept S16A implementation;
- freeze S16B semantics;
- change the accepted implementation head;
- authorize merge or main movement;
- resume AQ4;
- authorize Step6;
- implement the tabled Complete My Deck probabilistic/deck-context layer;
- or make the examples above canonical semantic definitions.

Semantic terms continue through the bounded Objective 6 / S16 review and Captain-ratification process.
