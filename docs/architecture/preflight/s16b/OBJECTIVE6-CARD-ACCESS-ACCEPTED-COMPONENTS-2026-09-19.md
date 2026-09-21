# Objective 6 — Card Access Components — Freeze-Candidate Names

**Date:** 2026-09-19  
**Status:** **STRUCTURALLY AUDITED / PROPOSED FINAL NAMES — NOT FROZEN**

## 1. Structural summary

The Card Access neighborhood is deliberately shallow. Exact permissions, zones, identities, destinations, timing, and event signatures carry the truth; user-facing tags provide handles for browsing.

Proposed freeze-candidate component names:

- **Permission Window** — duration/expiration coordinate;
- **Card Use Permission** — primitive permission assertion preserving `PLAY` vs `CAST`;
- **Top-Library Access** — surfaced include/exclude facet;
- **Library Traversal** — ordered library-processing event signature with explicit stop rule;
- **Additional Execution** — execution-multiplicity signature;
- **Typed Resources** — substrate/data-model invariant;
- **Card Resource Delta** — derived accounting fact;
- **Sample Selection** — surfaced finite-sample selection signature;
- **Tutor** — surfaced broader-library search/retrieval family.

## 2. Permission Window

Former working name: `Access Horizon`.

Preserve expiration/duration shapes including:

- resolution-only;
- until end of current turn;
- through end of next turn;
- until named step/phase/event;
- while a source/condition remains true;
- while the card remains in a zone;
- indefinite;
- recurring/capped windows.

It is player-visible/filterable but not a separate family or advantage metric.

## 3. Card Use Permission

Former working umbrella: `Alternate-Zone Play/Cast Access`.

Preserve:

- permission holder;
- owner/provenance of underlying card;
- source zone/position;
- action: `PLAY` / `CAST` / other explicitly modeled use;
- eligibility;
- Permission Window;
- timing overrides/restrictions;
- payment method / Alternative Cost;
- source/link dependency;
- unused-card disposition.

### PLAY vs CAST

This distinction is hard and survives unchanged.

Ragavan is the canonical cast-only anchor: a land exiled by Ragavan cannot be played through that permission.

Praetor's Grasp and Haldan are PLAY-permission anchors capable of covering lands subject to normal land-play rules.

## 4. Top-Library Access

Structural type: surfaced include/exclude facet over Card Use Permission.

Positive anchors:

- Future Sight;
- Mystic Forge;
- Oracle of Mul Daya;
- Bolas's Citadel;
- Experimental Frenzy;
- Xanathar, Guild Kingpin.

Critical negative:

- Enlightened Tutor puts a card on top but grants no permission to use the top card.

Shared `library_top` involvement alone is not similarity evidence.

## 5. Library Traversal

Former working name: `Sequential Library Traversal`.

Structural type: event/output signature; optionally surfaced for search.

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

Required fixtures:

- Cascade;
- Discover;
- Etali, Primal Conqueror;
- Ad Nauseam;
- Primal Surge;
- Possibility Storm;
- Dack Fayden, Helping Hand (official 2026-09-18 preview; stops after X creature cards where X is number of opponents).

## 6. Additional Execution

Former working name: `Repeat-Use / Additional Execution`.

Structural type: event/output signature + coordinates.

Distinguish:

- same underlying card re-cast;
- delayed re-cast permission;
- recurring graveyard permission;
- buyback/return enabling reuse;
- copy creation followed by casting the copy;
- repeatable copying from stored/imprinted card;
- finite vs reusable execution count;
- source zone;
- costs/payment;
- exile/consumption/replacement after execution.

Additional Execution does **not** mean another underlying card-origin resource.

Fixtures include Flashback, Rebound, Retrace, Mizzix's Mastery, Mnemonic Deluge, Isochron Scepter, and Arcane Bombardment.

## 7. Typed Resources

Former working name: `Resource-Type Separation`.

Structural type: substrate/data-model invariant.

Keep distinct:

- underlying card-origin resources;
- temporary/conditional permissions;
- copies and execution opportunities;
- generated board objects/tokens;
- mana / mana-capable objects;
- life;
- counters / Stored Capacity;
- other mechanically defined resource/state types.

Do not flatten them into one generic `value` quantity.

## 8. Card Resource Delta

Former working name: `Card Resource Differential`.

Structural type: derived accounting fact.

Key laws:

- count distinct underlying card-origin resources, not permission clauses or copies;
- present mana affordability is not required for resource identity;
- categorical permission eligibility matters (`CAST` does not cover lands);
- current actionability/timing remains a separate projection;
- continuous Top-Library Access exposes one current underlying top-card slot plus refreshability, not infinite simultaneous resources;
- Additional Execution does not create extra card-origin stock.

There is no separate `Card Access Differential` metric.

## 9. Sample Selection

Former working names: `Card Prospecting`, `Bounded Extraction`.

Structural type: surfaced finite-sample-selection signature.

A finite exposed library sample is produced without searching the broader library; one or more cards are selected from it for privileged destination/use.

The sample may be fixed, variable, state-derived, resource-controlled, or large.

Required coordinates:

- sample depth/expression;
- selection cardinality;
- eligibility;
- selection authority / staged partition;
- selected destination/use;
- unselected disposition;
- visibility;
- repetition/frequency.

Plunge into Darkness remains the key proof that `finite sample` does not mean fixed/small N.

## 10. Card Filtering

Card Filtering remains a broad UI/search umbrella over harder operation signatures rather than a high-information canonical family.

Sample Selection is one independently queryable pattern beneath/adjacent to that umbrella. Faithless Looting, scry, surveil, reorder-only operations, and Sample Selection should not become strongly equivalent merely because the UI groups them as Filtering.

## 11. Tutor

Tutor remains a strong surfaced functional family for broader-library search/retrieval.

Preserve search domain, whose library, quantity, selection authority, reveal, destination, and CR 701.23 failure-to-find behavior.

## 12. Control boundary

These are proposed freeze-candidate names only. No S16B freeze, corpus reclassification, implementation acceptance, merge, accepted-head/main movement, AQ4 resumption, Bridge activation, or Step6 is authorized.

> **PRESERVE TRUTH, NOT PLUMBING.**
