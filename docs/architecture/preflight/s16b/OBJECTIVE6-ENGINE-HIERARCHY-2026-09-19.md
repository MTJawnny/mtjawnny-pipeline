# Objective 6 — Engine Hierarchy Ruling

**Date:** 2026-09-19  
**Status:** Captain-approved working semantic structure; hard predicates for specific engine families remain subject to validation before S16B freeze.  
**Authority boundary:** Documentation only. This does not accept implementation, freeze S16B, merge PR #70, move the accepted implementation head, resume AQ4, activate Bridge v0, authorize Step6, or move `main`.

## 1. Structural ruling

**Engine is the parent concept.**

The term `Engine` should describe the reusable/scalable processing structure itself, independent of what resource, event, zone transition, or gameplay output the mechanism operates on.

Domain-specific engine terms should descend from this parent only when they earn a mechanically meaningful and independently testable definition.

Working hierarchy:

- **Engine** — parent structural concept.
  - **Card Engine** — an Engine whose relevant scalable output is usable card-resource access.
  - **Mana Engine** — an Engine whose relevant scalable output or conversion is mana.
  - **Blink Engine** — an Engine whose repeated processing performs exile/return operations.
  - **Death-Trigger Engine** — an Engine whose repeated processing converts deaths into triggers or downstream effects.
  - **Sacrifice Engine** — candidate child for Engines that repeatedly process sacrifice inputs; exact boundary against `Sacrifice Outlet` remains to be adjudicated.
  - Other domain-specific engine families may be added only after their own hard predicates are established.

The examples above are not an exhaustive ontology.

## 2. Parent membership comes first

A card should not receive a domain-specific `... Engine` label merely because community language commonly uses that phrase.

The correct order is:

1. determine whether the mechanism satisfies the parent **Engine** predicate;
2. if yes, determine which domain-specific engine family or families its operation satisfies;
3. describe additional mechanics through coordinates/facets rather than creating unnecessary child names.

Therefore a card colloquially called a `blink engine`, `mana engine`, or `draw engine` may still fail Foundry Engine membership if the mechanism is intrinsically hard-capped, self-exhausting, or otherwise fails the eventual parent predicate.

A mechanism being usable only during, or triggered only within, a particular phase/step/combat window does **not by itself** disqualify it from Engine membership. The harder question is whether additional qualifying inputs available within the relevant opportunity can produce additional outputs, or whether the processor collapses them into a single output and requires another discrete turn-structure opportunity before it can produce again.

## 3. Input supply, opportunity windows, and processor throughput — CAPTAIN-APPROVED REFINEMENT

Engine classification must separate three different mechanical questions:

1. **Input supply** — are additional qualifying objects/events/resources available?
2. **Opportunity window** — when can the mechanism process those inputs?
3. **Processor throughput** — if multiple qualifying inputs are available in that opportunity, can they produce additional processor firings/outputs?

External fuel dependence is normal for an Engine. Running out of fuel is not the same as the processor imposing a throughput ceiling.

Likewise, merely being combat-gated, phase-gated, or step-gated is not automatically a throughput ceiling.

### 3.1 `turn_structure_bound`

The working hard meaning of `turn_structure_bound` is now narrower:

> **turn_structure_bound** — after one qualifying output opportunity occurs, additional otherwise-qualifying inputs within that same ordinary opportunity cannot produce additional processor outputs; obtaining another output requires another discrete turn-structure opportunity such as another combat/attack declaration, upkeep, end step, phase, or turn.

The important question is therefore not simply **where in the turn the ability operates**, but whether **input multiplicity is preserved as output multiplicity inside that opportunity**.

A processor may be window-gated yet still be an Engine if additional qualifying inputs within that window independently produce additional outputs.

### 3.2 Toski versus Chivalric Alliance

**Toski, Bearer of Secrets — Card Engine: YES under the current working model.**

Toski's card-draw trigger is keyed to each creature the controller controls dealing combat damage to a player. If several creatures connect in one combat-damage step, those creature inputs can produce several draw triggers. The combat window constrains when the inputs can occur, but Toski does not collapse all successful creatures into a single draw opportunity.

This is input-scalable processing inside one combat opportunity.

**Chivalric Alliance — Card Engine: NO under the current working model.**

Its draw trigger is keyed to the single event of the controller attacking with two or more creatures. Supplying three, five, or ten attacking creatures in the same attack does not proportionally increase draw throughput. Once the threshold is met, the attack event produces one draw trigger. Another draw generally requires another qualifying attack declaration/combat opportunity.

This is therefore `turn_structure_bound` in the working sense.

The distinction is **not simply game object versus turn phase**. It is the granularity at which the processor recognizes qualifying inputs:

- Toski preserves per-creature multiplicity inside the combat window;
- Chivalric Alliance threshold-compresses many attacking creatures into one attack-event output.

### 3.3 Lotus Cobra parallel

Lotus Cobra supports the same distinction outside combat.

Its processor is keyed to each land entering under the controller's control, not specifically to the controller's normal land play for the turn. The ordinary one-land-play rule constrains only one common source of land-entry inputs. Fetch lands, ramp effects, land tokens, and other put-onto-battlefield effects can supply additional land-entry events in the same turn, and the Cobra mechanism can process those additional inputs.

Therefore Lotus Cobra remains a positive **Mana Engine** anchor under the current working model.

## 4. Children may be organized by different mechanical dimensions

Not every Engine child must be defined solely by output type.

Examples:

- `Card Engine` and `Mana Engine` are naturally output-oriented.
- `Blink Engine` is primarily operation-oriented: repeated exile/return processing.
- `Death-Trigger Engine` is event/trigger-oriented.
- `Sacrifice Engine` may be input/processing-oriented.

This is acceptable because the shared parent predicate establishes the structural fact that all of them are Engines. The child concept identifies the domain of repeated processing.

## 5. Anchors

### Carrion Feeder

Carrion Feeder remains a positive **Engine** anchor because its sacrifice ability can repeatedly process supplied creature inputs without an intrinsic once-per-turn, phase, or tap ceiling.

Its final narrower child classification remains open. It may overlap with concepts such as `Sacrifice Outlet`, `Sacrifice Engine`, or another more precise sacrifice-family term depending on later adjudication.

### Rhystic Study / Sram, Senior Edificer

These remain positive **Card Engine** anchors under the working model because their card-resource output can scale with repeated qualifying external events/inputs rather than a fixed scheduled output window.

### Toski, Bearer of Secrets

Toski is a positive **Card Engine** anchor under the refined throughput test. Multiple creatures dealing combat damage in the same combat opportunity can generate multiple card-draw outputs. Combat gating therefore does not by itself imply `turn_structure_bound`.

### Phyrexian Arena

Phyrexian Arena remains recurring Card Advantage but not a Card Engine under the current working model because its draw production is intrinsically scheduled by upkeep and another draw requires another upkeep opportunity.

### Chivalric Alliance

Chivalric Alliance remains recurring Card Advantage potential but not a Card Engine under the current working model. Additional attacking creatures beyond the two-creature threshold do not increase output in that attack; another draw generally requires another qualifying attack opportunity.

### Lotus Cobra

Lotus Cobra remains a positive **Mana Engine** anchor. Additional land-entry events can produce additional mana outputs without the processor itself imposing a once-per-turn ceiling, and those inputs are not limited to the normal land play for the turn.

## 6. Non-proliferation rule

Foundry should not pre-create a flat list of every community phrase ending in `Engine`.

A proposed child should receive a canonical name only when:

- the parent Engine predicate is satisfied;
- the child identifies a mechanically meaningful repeated-processing domain;
- a hard membership predicate can be stated;
- useful positive anchors and hard near-misses can be identified;
- the distinction is more useful as a noun than as a coordinate/facet.

Otherwise the behavior should remain represented through the parent Engine membership plus underlying semantic coordinates.

## 7. Working hierarchy summary

```text
Engine
|
+-- Card Engine
+-- Mana Engine
+-- Blink Engine
+-- Death-Trigger Engine
+-- Sacrifice Engine (candidate; exact boundary unresolved)
+-- other validated engine families
```

The hierarchy is intentionally extensible but not permissive: new children require adjudication rather than automatic creation.

## 8. Control boundary

This ruling preserves semantic structure only. It does **not** authorize:

- S16A implementation acceptance;
- S16B semantic freeze;
- merge of PR #70 or any other draft PR;
- movement of the accepted implementation head;
- AQ4 resumption;
- Bridge v0 activation;
- Step6;
- main-branch movement.

The governing principle remains:

> **PRESERVE TRUTH, NOT PLUMBING.**
