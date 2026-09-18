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

## 9. Immediate consequence for Objective 6

When semantic review resumes, evaluate each vocabulary term with two product questions in addition to its hard definition:

1. **Does this deserve a named functional counter/category?**
2. **Which distinctions underneath it are useful user-facing facets rather than additional named terms?**

The current vocabulary inventory is not presumed exhaustive. Missing identifiers discovered through this process should be captured and evaluated deliberately.

Current examples already under discussion include `cantrip`, `card advantage`, mana/ramp families, removal/interaction, board wipes/wraths, tutors/library access, protection, stax/hatebear, and the newly queued `role compression` concept.

---

## 10. Control boundary

This document records product direction only.

It does not:

- accept S16A implementation;
- freeze S16B semantics;
- change the accepted implementation head;
- authorize merge or main movement;
- resume AQ4;
- authorize Step6;
- or make the examples above canonical semantic definitions.

Semantic terms continue through the bounded Objective 6 / S16 review and Captain-ratification process.
