# Objective 6 — Card Access Accepted Components

**Date:** 2026-09-19  
**Status:** CAPTAIN-APPROVED semantic components; names are provisional and all are explicitly subject to the later cool-name audit, including machine-facing/internal labels.  
**Control boundary:** Semantic documentation only. This does not freeze S16B, accept implementation, merge PR #70, move accepted head, resume AQ4, activate Bridge v0, authorize Step6, or move `main`.

## Governing naming rule

All accepted components in this record are semantically accepted but **not naming-final**. The later vocabulary/cool-name audit may rename public or internal concepts for clarity, player recognition, consistency, and quality of terminology without reopening the mechanical distinction itself unless new evidence requires it.

## 1. Access Horizon — ACCEPTED METRIC

Foundry must expose how long an accessed card remains usable.

At minimum, preserve mechanically distinct horizons such as:
- this turn / until end of turn;
- through the end of the controller's next turn;
- until a specified next step/end step;
- indefinite;
- while a condition/source remains true;
- one immediate resolution-only opportunity.

This is intended to be visible to players where relevant because two otherwise similar access effects may offer materially different opportunity windows.

Access horizon is not by itself equivalent to Card Resource Differential; it is a separate factual property affecting opportunity for realization.

## 2. Alternate-Zone Play/Cast Access — ACCEPTED

Foundry must distinguish permission to **play** a card from permission to **cast** a card.

- `play` permission can include lands when all other land-play rules are satisfied;
- `cast` permission applies only to cards that can be cast as spells and does not permit land plays.

Required coordinates include at least:
- source zone;
- card ownership/control provenance;
- permission kind: `PLAY` vs `CAST`;
- eligible card types or restrictions;
- access horizon;
- timing restrictions/overrides;
- payment handling: normal cost, alternate cost, without paying mana cost, or other modification;
- unused-card disposition.

### Anchor: Ragavan, Nimble Pilferer

Ragavan exiles the top card of the damaged player's library and permits the controller to **cast** it until end of turn. A land exiled this way cannot be played. Ragavan therefore demonstrates why `CAST` and `PLAY` cannot be collapsed.

Ragavan can simultaneously produce:
- a retained creature source;
- a Treasure mana object;
- temporary access to an opponent-owned card;
- an end-of-turn access horizon.

Those resources must remain separately represented rather than collapsed into one generic advantage value.

## 3. Sequential Library Traversal — ACCEPTED

Foundry needs a mechanical access pattern for operations that traverse cards in library order until a qualifying stopping condition is reached, then grant privileged use/access to one or more resulting cards.

This remains distinct from:
- Tutor/search;
- bounded sample extraction;
- ordinary Filtering;
- literal Draw.

Relevant coordinates include:
- whose library/libraries are traversed;
- traversal direction/order;
- stopping predicate;
- whether the qualifying card is selected or mechanically determined;
- whether multiple players/libraries are traversed;
- result destination/permission;
- cast/play permission;
- payment modification;
- nonqualifying-card disposition.

### Anchors

- Cascade: traverse controller library until the first qualifying nonland card by mana-value restriction, with optional cast permission without paying its mana cost.
- Discover: traverse until the first qualifying nonland card by value threshold, then either cast it without paying its mana cost or put it into hand.
- Etali, Primal Conqueror: independently traverse the top of **each player's** library until that player reveals/exiles a nonland card, then permit casting any number of those nonland cards without paying their mana costs.

Etali is an important multiplayer anchor because Sequential Library Traversal may operate across multiple owners/libraries in one event.

## 4. Repeat-Use / Additional Execution — ACCEPTED

Foundry must represent when one underlying card resource can generate multiple distinct uses/executions over time without pretending that a new physical/card-origin resource was created.

Examples include patterns such as flashback, rebound, aftermath-like second use, retrace-like recasting, and other effects that give an existing card another spell/use opportunity.

Required facts may include:
- underlying card identity/resource;
- first-use zone;
- later-use source zone;
- number/bounds of additional executions;
- alternate/additional costs;
- timing/access horizon;
- whether later use consumes/exiles the card;
- whether the repeated execution is optional or automatic.

This component is distinct from Card Resource Differential, though repeated execution may contribute to broader realized value.

## 5. Resource-Type Separation — ACCEPTED

Foundry must preserve materially different resources as separate dimensions instead of converting all generated value into a single generic advantage score.

Simple governing rule:

> **Say what resource was gained, lost, preserved, or accessed. Do not call unlike resources the same thing merely because all are valuable.**

At minimum, Foundry should be capable of distinguishing:
- card-origin resources / Card Resource Differential inputs;
- temporary card access permissions;
- generated board objects/material such as creature tokens;
- mana resources and mana-producing objects such as Treasure;
- repeat-use/additional-execution opportunities;
- life;
- counters/stored state;
- other mechanically distinct resources when necessary.

### Why this matters

- Divination primarily changes card-origin resources.
- Dragon Fodder consumes one card and creates two creature-token objects; token material is not silently converted into two card-origin resources.
- Big Score can simultaneously change hand/card resources and create Treasure mana objects.
- Ragavan can retain a creature, create Treasure, and grant temporary cast-only access to an opponent-owned card.

The purpose is decomposition, not value judgment. Later strategic systems may reason about how desirable or powerful those resources are in context.

## 6. Card Resource Differential relationship

`Card Resource Differential` remains Foundry's current working name for its narrower factual accounting of distinct usable card-origin resources. It is itself subject to the later naming audit.

Resource-Type Separation protects that metric from swallowing token production, mana generation, repeat-use opportunity, and other unlike resources.

## 7. Naming audit requirement

The later naming audit must review **all** accepted terms here, including internal-only terms:
- Access Horizon;
- Alternate-Zone Play/Cast Access;
- Sequential Library Traversal;
- Repeat-Use / Additional Execution;
- Resource-Type Separation;
- Card Resource Differential.

Semantic acceptance does not imply these are final labels.

## Control reminder

PRESERVE TRUTH, NOT PLUMBING.
