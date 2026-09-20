# Foundry Product Interaction Model

**Date:** 2026-09-18  
**Revised:** 2026-09-20 after Objective 6 weird-card / whole-vocabulary / naming audit  
**Status:** Captain product direction — documentation only; not semantic freeze or implementation acceptance  
**Base accepted implementation head:** `fdb66e659d81f4efa373ab8e86329485c0205966`  
**Current semantic routing:** `docs/architecture/preflight/s16b/OBJECTIVE6-POST-AUDIT-CURRENT-STATE-2026-09-19.md`

## Purpose

This document records the intended Foundry user interaction model. It is product direction, not an independent semantic authority.

Where an example or term in an older product discussion conflicts with the post-audit Objective 6 semantic records, the post-audit semantic record controls.

Governing product principle:

> **Foundry reports semantic composition and change; it does not prescribe desired composition.**

The current Foundry core is a deterministic semantic engine, browser, measurement surface, and reversible deck-editing workspace. Strategic recommendation behavior belongs to the later **Complete My Deck** layer.

---

## 1. One semantic substrate, multiple user surfaces

Foundry should expose one canonical semantic representation through multiple product views rather than maintain separate definitions of similarity or function.

### 1.1 Card Thesaurus / seeded card view

Starting from one card, a player should be able to browse relationships such as:

1. **Same / near-exact language** — closely corresponding Oracle-language structure.
2. **Same gameplay function** — materially similar job despite different wording/mechanism.
3. **Similar gameplay function** — meaningful overlap with visible differences in mechanism, scope, timing, restrictions, dependency, cost/payment, destination, duration, or other coordinates.

The player is exploring a semantic neighborhood. Foundry is not selecting a preferred replacement.

### 1.2 Deck Workspace

The same engine should accept a few cards, a partial deck, or a complete deck.

Each card remains an individual Thesaurus entry point while the loaded list supplies aggregate context.

The workspace should support:

- click any card and inspect alternatives;
- compare canonical functions and mechanical coordinates;
- preview the factual semantic effect of a substitution;
- replace a selected card in the working deck;
- Undo / Redo;
- update deck-level counts and economic totals;
- export a plain-text deck list for external deck tools.

### 1.3 Foundry Explorer

Explorer is the unseeded faceted-search surface over the same substrate.

A player may progressively intersect or exclude facts such as:

- functional family or surfaced tag;
- exact operation/signature;
- target/object/resource class;
- zone/source/destination;
- `PLAY` versus `CAST` permission;
- Permission Window;
- repeatability/processor profile;
- eligibility/restrictions;
- mana value/type/color and other card facts.

Broad UI umbrellas such as Card Access, Card Filtering, Interaction, or Engine search language must not become stronger semantic evidence than the hard operations underneath them.

---

## 2. Budget is a mode, not a second semantic engine

Budget behavior layers economic constraints over semantic comparison.

When **Budget mode is OFF**:

- price need not dominate the interface;
- semantic function and mechanics remain primary.

When **Budget mode is ON**:

- prices become visible;
- a deck may sort by price;
- replacement candidates may show price and price delta;
- users may constrain alternatives by price;
- deck total updates as edits occur.

Budget must not redefine similarity.

---

## 3. Current Foundry core is descriptive, not prescriptive

The current product should not state conclusions such as:

- `you need more removal`;
- `your deck has too little card advantage`;
- `this is the best replacement`;
- `you should cut this card`.

It should report factual composition and change.

Examples:

- `Removal sources: 9`
- `Top-Library Access sources: 2`
- `Sample Selection sources: 4`
- `Ramp sources: 11`
- `Mass Removal sources: 3`
- `Cards with graveyard-use access: 5`

Derived resource/accounting views may report Card Resource Delta, parity, or pairwise resource changes when the required state/context is available.

`Card Advantage` remains useful established theory/player language, but current Objective 6 does not require it to be a canonical ontology family. Educational or later strategic views may explain Card Advantage from harder resource facts.

---

## 4. Deck functionality dashboard

A loaded deck should aggregate canonical semantic assertions into factual counts and drill-downs.

Likely high-level handles include ratified families and surfaced views such as:

- Removal;
- Ramp;
- Tutor;
- Taxation;
- Permission Denial;
- Hand Disruption;
- Mass Removal;
- Top-Library Access;
- Sample Selection;
- Exile Access;
- Graveyard Access;
- Direct Placement;
- Cantrip;
- other ratified functions and facets.

Counts may overlap. A card can contribute to multiple mechanically distinct functions.

### 4.1 Drill-downs carry the detail

A top-level count should not flatten important distinctions.

A Removal view may expose, for example:

- object class;
- destroy / exile / bounce / sacrifice / damage path;
- target authority;
- targeted versus mass scope;
- temporary versus persistent consequence;
- restrictions and eligibility.

A Card Access view may expose:

- Draw;
- Tutor;
- Sample Selection;
- Top-Library / Exile / Graveyard source views;
- Card Use Permission;
- `PLAY` versus `CAST`;
- Permission Window;
- Library Traversal;
- Additional Execution.

Shared zone vocabulary alone must not imply shared function.

---

## 5. Counterfactual replacement preview

Before the user commits a substitution, Foundry should calculate the factual deck-level delta.

Illustrative shape:

```text
If Card A is replaced by Card B:
Removal sources:          9 -> 8
Sample Selection:         3 -> 4
Top-Library Access:       1 -> 1
Ramp sources:            11 -> 11
Deck price:            $614 -> $597
```

The core should not append a judgment that the resulting deck is better, healthier, weaker, or more balanced.

After replacement, the workspace recalculates the same canonical facts and preserves reversibility through Undo / Redo.

---

## 6. Vocabulary design follows the product without becoming product-owned truth

The post-audit semantic design intentionally distinguishes among:

- strong functional families;
- surfaced include/exclude facets;
- primitives;
- event/output signatures;
- coordinates;
- derived accounting facts;
- community/search aliases;
- strategic-layer concepts.

A product-visible term does not automatically deserve a canonical ontology node.

The UI should be able to answer:

> **Why does this card match this query?**

The explanation should be generated from the same hard facts that produced the match.

Examples:

- `Tutor + Basic Land + Direct Placement` -> “Searches your library for a basic land and puts it onto the battlefield.”
- `Top-Library Access + CAST + artifact/colorless eligibility` -> “Lets you cast eligible cards from the top of your library.”
- `Sample Selection + top six + up to two creatures + Direct Placement` -> “Looks at a six-card sample and can put up to two qualifying creatures directly onto the battlefield.”

The system should preserve familiar search language aggressively while keeping canonical mechanical structure underneath it.

---

## 7. Role Compression is derived product/accounting information

The Objective 6 audit no longer treats Role Compression as a new canonical card family requiring an independent hard ontology predicate.

The underlying facts already exist: a card may satisfy several materially distinct functions.

The product may derive a Role Compression view from those facts and report:

- which independent functions one card contributes;
- whether those functions are simultaneous or mutually exclusive modes;
- whether they arise from one semantic unit or separate abilities;
- how a proposed substitution changes those deck-level functions.

This remains descriptive. Foundry core does not label multifunctionality as inherently good or desirable.

---

## 8. Searcher B product consequence

Similarity should be driven primarily by mechanically informative facts rather than broad shared nouns.

A useful ordering is:

1. same operation/event signature with compatible participants/resources;
2. same functional outcome through mechanically adjacent operations;
3. compatible restrictions, scope, destination, timing and duration;
4. shared surfaced facet/tag;
5. shared broad UI umbrella only — weak evidence;
6. shared word or zone alone — near-zero evidence without matching operation.

Examples:

- Dig Through Time and Collected Company share meaningful Sample Selection structure while differing in eligibility/destination.
- Dig Through Time and Faithless Looting share only broad Card Filtering adjacency.
- Enlightened Tutor and Future Sight both involve the library top but perform fundamentally different functions.
- Flashback and Mnemonic Deluge both increase executions, but original-card reuse and copy execution remain distinct.

---

## 9. Future Complete My Deck layer

A later separate layer may answer questions the current core deliberately does not:

> **Given this deck and objective, how reliably and effectively can these canonical functions be realized, and what additions or substitutions best satisfy the player's stated goals?**

That layer may use:

- deck composition;
- probability and simulation;
- strategic research with provenance;
- game/format context;
- community evidence;
- expected realization/throughput;
- recommendation logic.

It must consume rather than overwrite canonical Foundry facts.

Dedicated future-state records:

- `docs/architecture/future-state/COMPLETE-MY-DECK-PROBABILISTIC-CONTEXT.md`
- `docs/architecture/future-state/REALIZATION-CEILING-AND-GAME-HORIZON.md`
- `docs/architecture/future-state/STRATEGIC-RESEARCH-ENRICHMENT.md`
- `docs/architecture/future-state/AUTOMATED-SEMANTIC-INGESTION-AND-CORPUS-REFRESH.md`

---

## 10. Current Objective 6 semantic authority boundary

For the current S16B semantic freeze candidate, start with:

`docs/architecture/preflight/s16b/OBJECTIVE6-POST-AUDIT-CURRENT-STATE-2026-09-19.md`

That file routes to:

- the weird-card adversarial corpus hunt;
- the whole-vocabulary semantic audit;
- the global naming audit;
- revised per-concept candidate records;
- remaining freeze-review validation work.

The product model does not override those records.

---

## 11. Control boundary

This document does not authorize:

- S16B freeze;
- broad corpus reclassification;
- implementation acceptance;
- AQ4 resumption;
- Bridge v0 activation;
- Step6;
- merge of PR #70;
- movement of the accepted implementation head;
- movement of `main`.

Standing controls remain unchanged until explicitly superseded by the Captain.
