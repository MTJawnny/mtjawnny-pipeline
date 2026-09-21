# Objective 6 — Cantrip and Exile Access — Freeze-Candidate Ruling

**Date:** 2026-09-19  
**Revised:** 2026-09-20 after whole-vocabulary and naming audit  
**Status:** **SURFACED/DERIVED TAGS + PERMISSION STRUCTURE — NOT FROZEN**  
**Current routing:** `OBJECTIVE6-POST-AUDIT-CURRENT-STATE-2026-09-19.md`

## 1. Cantrip

Foundry should use the established Magic/community meaning of **Cantrip**, not the prior narrower Foundry-specific rule.

The withdrawn requirements were:

- mana value 2 or less;
- a mandatory second independent function.

Freeze-candidate treatment:

> **Cantrip** is a surfaced derived/community tag for a card whose own normal operation replaces its expenditure by drawing a card, usually through a `draw a card` rider or equivalent literal draw operation.

Canonical facts remain the underlying Draw event, source expenditure, timing, and other operations.

Important consequences:

- no universal mana-value ceiling;
- no mandatory second function;
- permanents and nonpermanents may qualify where their own normal operation self-replaces through Draw;
- Cantrip is not extended to Tutor, Graveyard Access, Sample Selection, Exile Access, or other non-Draw parity mechanisms merely because those operations can be card-neutral;
- self-replacing/parity is derived accounting, not a Card Replacement family.

## 2. Exile Access

Former working phrase: `Temporary Exile Access`.

Freeze-candidate name: **Exile Access**.

Structural type: surfaced zone/use facet over **Card Use Permission**.

Core pattern:

> an underlying card is in exile and a player receives permission to PLAY or CAST it during a defined Permission Window.

`Impulsive Draw` remains a useful Wizards/community alias. It is not literal Draw.

## 3. Permission Window is load-bearing

At minimum preserve:

### Current-turn window

Example shape:

> `You may play that card this turn.`

Facts:

- permission expires at end of current turn;
- normal timing restrictions apply unless separately overridden;
- unused cards may remain exiled after permission expires;
- realization opportunity depends on remaining timing, mana, and land-play state.

### Through-end-of-next-turn window

Example shape:

> `You may play cards exiled this way until the end of your next turn.`

Facts:

- permission survives the current turn and the controller's next turn;
- the player ordinarily receives another untap and normal play windows before expiration;
- this is a longer permission window, not a different canonical resource type.

### Other windows

The model must also support:

- resolution-only permission;
- until a named future step/phase/event;
- while a source/condition remains true;
- while the card remains exiled;
- indefinite permission;
- recurring or capped permissions;
- permissions tied to a linked source/object.

## 4. Required underlying facts

Preserve at least:

- owner/provenance of the underlying card;
- source zone = exile;
- visibility / face-up vs face-down;
- permission holder;
- `permission_action = PLAY | CAST`;
- land eligibility where relevant;
- card-type/other eligibility restrictions;
- Permission Window;
- ordinary timing restrictions and overrides;
- Alternative Cost, Cost Reduction, Additional Cost, or Payment Method facts where applicable;
- whether unused cards remain exiled;
- whether permission depends on a source/link;
- quantity of underlying cards affected;
- current actionability facts separately from permission identity.

## 5. Card Resource Delta boundary

Permission duration alone does not determine Card Resource Delta.

Canonical decomposition should distinguish:

1. which distinct underlying card-origin resources are accessible before and after;
2. source expenditure/loss where relevant;
3. permission eligibility (`PLAY` versus `CAST` matters);
4. Permission Window;
5. current actionability such as timing, targets, payment, and land-play allowance;
6. realized use.

A longer Permission Window generally creates more realization opportunities, but does not by itself create another underlying card resource.

A spell need not be presently affordable to remain an accessible resource under an otherwise valid permission.

## 6. Relationship to Card Advantage language

`Card Advantage` remains established theory/community language rather than a canonical Objective 6 family.

Exile Access may contribute to conventional card-advantage interpretations, but Foundry's canonical substrate should first report the exact access/resource facts and Card Resource Delta inputs.

Do not encode rules such as:

- `this turn` = never Card Advantage;
- `through next turn` = always Card Advantage.

Those are not mechanically defensible definitions.

## 7. Composition with neighboring structures

Exile Access may compose with:

- Sample Selection;
- Tutor;
- Library Traversal;
- Top-Library-origin exile operations;
- Additional Execution;
- copy/execution provenance;
- Alternative Cost / Payment Method;
- Card Resource Delta;
- processor facts used by derived `Engine` searches.

Examples:

- Gonti-style finite selection -> exile -> CAST permission: Sample Selection + Exile Access.
- Praetor's Grasp-style broader-library search -> exile -> PLAY permission: Tutor + Exile Access.
- Ragavan-style opponent top-card exile -> CAST until end of turn plus Treasure creation: Exile Access + typed mana/object output.
- Arcane Bombardment stores cards in exile but later casts copies; underlying stored cards and generated executions must remain distinct.

## 8. Future realization modeling

A later strategic layer may quantify:

- remaining mana when permission is created;
- remaining legal cast/play windows;
- current/next-turn land-play availability;
- probability an exiled card can be used before expiration;
- survival of the permission source where linked;
- expected fraction of granted access actually realized.

Those are downstream realization questions, not canonical membership tests.

## 9. Control boundary

This record does not authorize:

- S16B freeze;
- broad corpus execution/reclassification;
- implementation acceptance;
- merge;
- accepted-head/main movement;
- AQ4 resumption;
- Bridge activation;
- Step6.

> **PRESERVE TRUTH, NOT PLUMBING.**
