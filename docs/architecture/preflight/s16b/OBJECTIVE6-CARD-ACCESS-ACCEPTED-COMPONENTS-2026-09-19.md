# Objective 6 — Card Access Components — Audit Revision

**Date:** 2026-09-19  
**Status:** **MECHANICAL COMPONENTS RETAINED; STRUCTURAL TYPES REVISED; FINAL NAMES PENDING GLOBAL NAMING AUDIT**

## 1. Purpose

The earlier component review correctly identified several load-bearing Card Access facts. The whole-vocabulary adversarial audit changes **what kind of semantic thing** several of them are.

The project should preserve the facts without turning every useful fact into a family/noun.

## 2. Permission Window (formerly working `Access Horizon`)

**Structural type:** coordinate on a use permission.

Preserve expiration/duration shapes including:

- resolution-only;
- until end of current turn;
- through end of next turn;
- until named step/phase/event;
- while a source/condition remains true;
- while the card remains in a zone;
- indefinite;
- recurring/capped windows.

The duration is player-visible and filterable, but it is not a separate family or independent advantage metric.

## 3. Alternate-zone use permission

**Structural type:** primitive permission assertion.

Preserve at minimum:

- permission holder;
- owner/provenance of the underlying card;
- source zone/position;
- `PLAY` vs `CAST` vs direct-deployment action;
- card/characteristic eligibility;
- permission window;
- timing overrides/restrictions;
- payment method / alternative cost;
- source/link dependency;
- unused-card disposition.

### Hard rule — PLAY vs CAST

`PLAY` and `CAST` remain distinct.

Ragavan is the canonical cast-only anchor: an exiled land cannot be played through its permission.

Praetor's Grasp and Haldan demonstrate `PLAY` permissions that can cover lands when other rules permit land play.

## 4. Top-Library Access

**Structural type:** surfaced include/exclude facet over use-permission assertions.

This remains separately queryable because players need to include/exclude the pattern directly.

Do not infer it from `library_top` involvement alone. Enlightened Tutor remains a hard negative because putting a card on top grants no use permission.

## 5. Ordered Library Traversal (formerly working `Sequential Library Traversal`)

**Structural type:** event/output signature; optionally surfaced facet.

The weird-card audit broadens the stop architecture beyond Cascade/Discover.

Preserve:

- library owner(s);
- ordered traversal direction;
- exposure action;
- continue/stop rule;
- stopping predicate;
- qualifying-card count expression (`first`, `Xth`, etc.);
- player-controlled stop where present;
- disposition of traversed cards;
- action applied to qualifying/result cards.

Anchors now include:

- Cascade;
- Discover;
- Etali, Primal Conqueror;
- Ad Nauseam;
- Primal Surge;
- Possibility Storm;
- official preview **Dack Fayden, Helping Hand**, which stops after X creature cards where X is the number of opponents.

## 6. Additional Execution (formerly `Repeat-Use / Additional Execution`)

**Structural type:** event/output signature + coordinates.

The common fact is that one source/underlying card can generate more than one spell/action execution opportunity. Do not infer that another physical/card-origin resource exists.

Distinguish:

- same underlying card re-cast;
- delayed re-cast permission;
- recurring graveyard permission;
- buyback/return enabling reuse;
- copy creation followed by casting the copy;
- repeatable copying from an imprinted/stored card;
- finite vs reusable execution count;
- source zone;
- costs/payment;
- exile/consumption/replacement after execution.

Flashback, Rebound, Retrace, Mizzix's Mastery, Mnemonic Deluge, Isochron Scepter, and Arcane Bombardment are required adversarial fixtures.

## 7. Typed Resource Model (formerly `Resource-Type Separation`)

**Structural type:** substrate/data-model invariant, not a card concept.

Never flatten unlike resources into one generic value score.

At minimum keep distinct:

- underlying card-origin resources;
- temporary/conditional permissions;
- spell/card copies and execution opportunities;
- generated board objects/tokens;
- mana / mana-capable objects;
- life;
- counters / stored capacity;
- other mechanically defined resource/state types.

Ragavan is a strong fixture because one combat-damage event can produce both a Treasure and temporary opponent-card cast access.

Uldaros Theorix is a stronger modern fixture because one effect can involve underlying grave cards, copies, free spell executions, and resulting permanent tokens.

## 8. Card Resource Differential

**Structural type:** derived accounting fact, not another Card Access family.

It consumes underlying typed resource/access facts; it does not erase their mechanisms.

Important rules now preserved in its dedicated revised record:

- count distinct underlying card-origin resources, not permission clauses or copies;
- present mana affordability is not required for resource identity;
- categorical permission eligibility still matters (`CAST` does not cover lands);
- current actionability/timing remains a separate projection;
- continuous top access is one current underlying top-card slot plus refreshability, not infinite simultaneous resources;
- repeated executions of one card remain execution multiplicity rather than extra card-origin stock.

There is **no separate Card Access Differential metric**.

## 9. Card Filtering / finite-sample selection

Card Filtering is now treated as a broad UI/search umbrella over harder operation signatures.

Finite-sample selection remains a surfaced signature/facet with sample depth, selection authority, selected count, eligibility, destination/use, and unselected disposition.

This keeps Dig Through Time / Collected Company / Plunge into Darkness distinct from Faithless Looting / scry / surveil / reorder-only effects.

## 10. Tutor

Tutor remains a strong player-facing functional concept for broader-library search/retrieval.

Destination, search domain, quantity, chooser, reveal, and CR 701.23 failure-to-find behavior are coordinates beneath the surfaced concept.

## 11. Resource and mechanism composition

One card may legitimately carry several independent facts.

Examples:

- **Ragavan:** temporary cast access + opponent provenance + Treasure creation + combat-damage trigger;
- **Bolas's Citadel:** Top-Library Access + PLAY/CAST + formal alternative life cost for spells;
- **Collected Company:** finite-sample selection + Direct Placement;
- **Etali:** ordered multiplayer traversal + cast permission + formal zero-mana alternative cost;
- **Underworld Breach:** graveyard CAST permission + alternative Escape costs + shared graveyard fuel;
- **Mnemonic Deluge:** graveyard targeting + card-copy generation + multiple free copy executions.

Foundry should preserve the composition rather than choose one exclusive branch.

## 12. Control boundary

No S16B freeze, corpus reclassification, implementation acceptance, merge, accepted-head/main movement, AQ4 resumption, Bridge activation, or Step6 is authorized.

> **PRESERVE TRUTH, NOT PLUMBING.**
