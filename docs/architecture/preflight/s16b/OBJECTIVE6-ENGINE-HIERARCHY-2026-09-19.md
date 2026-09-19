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

Therefore a card colloquially called a `blink engine`, `mana engine`, or `draw engine` may still fail Foundry Engine membership if the mechanism is intrinsically hard-capped, phase-limited, self-exhausting, or otherwise fails the eventual parent predicate.

## 3. Children may be organized by different mechanical dimensions

Not every Engine child must be defined solely by output type.

Examples:

- `Card Engine` and `Mana Engine` are naturally output-oriented.
- `Blink Engine` is primarily operation-oriented: repeated exile/return processing.
- `Death-Trigger Engine` is event/trigger-oriented.
- `Sacrifice Engine` may be input/processing-oriented.

This is acceptable because the shared parent predicate establishes the structural fact that all of them are Engines. The child concept identifies the domain of repeated processing.

## 4. Anchors

### Carrion Feeder

Carrion Feeder remains a positive **Engine** anchor because its sacrifice ability can repeatedly process supplied creature inputs without an intrinsic once-per-turn, phase, or tap ceiling.

Its final narrower child classification remains open. It may overlap with concepts such as `Sacrifice Outlet`, `Sacrifice Engine`, or another more precise sacrifice-family term depending on later adjudication.

### Rhystic Study / Sram, Senior Edificer

These remain positive **Card Engine** anchors under the working model because their card-resource output can scale with repeated qualifying external events/inputs rather than a fixed scheduled output window.

### Phyrexian Arena

Phyrexian Arena remains recurring Card Advantage but not a Card Engine under the current working model because its draw production is intrinsically scheduled rather than input-scalable.

## 5. Non-proliferation rule

Foundry should not pre-create a flat list of every community phrase ending in `Engine`.

A proposed child should receive a canonical name only when:

- the parent Engine predicate is satisfied;
- the child identifies a mechanically meaningful repeated-processing domain;
- a hard membership predicate can be stated;
- useful positive anchors and hard near-misses can be identified;
- the distinction is more useful as a noun than as a coordinate/facet.

Otherwise the behavior should remain represented through the parent Engine membership plus underlying semantic coordinates.

## 6. Working hierarchy summary

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

## 7. Control boundary

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
