# Objective 6 — Engine Structure — Audit Revision

**Date:** 2026-09-19  
**Status:** **EARLIER CANONICAL ENGINE TREE SUPERSEDED BY ADVERSARIAL AUDIT; HARD PROCESSOR FACTS RETAINED**

## 1. Structural correction

The earlier version of this file treated **Engine** as a canonical parent with children such as Card Engine, Mana Engine, Blink Engine, Death-Trigger Engine, and a candidate Sacrifice Engine.

The whole-vocabulary adversarial audit rejects that ontology shape.

> **Engine should not be a canonical hard family tree.**

The investigation that produced the tree was still valuable: it uncovered real mechanical facts about repeatability, input aggregation, throughput, stored capacity, opportunity windows, and processor retention. Those facts survive and should become the canonical substrate.

`Engine` remains useful as a **derived/search/community label** over those harder facts.

## 2. Why the family tree is demoted

The current strict Engine predicate diverges materially from established player usage.

Examples:

- Phyrexian Arena and The One Ring are commonly sought/described as card/draw engines despite scheduled or tap-limited native firing;
- Chivalric Alliance and Grazilaxx produce recurring card flow but fail the prior project-specific scalability gate;
- Toski and Well of Lost Dreams satisfy more open-ended throughput tests;
- Nest of Scarabs scales output magnitude but does not itself provide a feedback loop;
- Carrion Feeder, Sram, Rhystic Study, Lotus Cobra, and Skirge Familiar expose still other processor shapes.

Those distinctions matter. The word `Engine` is the wrong place to make them authoritative.

A strict ontology gate would separate mechanically adjacent recurring-value cards largely because Foundry chose a narrower custom meaning for a broad community term. Searcher B is better served by comparing the actual processor coordinates.

## 3. Canonical processor facts

Preserve at minimum:

- **input/event kind** — what event/object/resource can cause or fuel another operation;
- **input consumed** — whether the input is consumed;
- **input aggregation** — per-object/per-event, threshold, `one or more`, per-player, etc.;
- **trigger/firing multiplicity** — how many processor firings can arise from qualifying inputs;
- **output kind** — card access, mana, tokens, zone changes, counters, damage, etc.;
- **output magnitude** — fixed/variable/state-scaled;
- **output multiplicity** — number of separately produced outputs/executions;
- **intrinsic firing cap** — once per turn/phase/step/combat, first each turn, tap activation, none, other;
- **opportunity window** — when processing may occur;
- **processor retention** — whether firing leaves the mechanism able to fire again;
- **future-eligibility effect** — preserves/degrades/destroys prerequisites;
- **external fuel dependency**;
- **stored capacity/repertoire**;
- **feedback dependency** — whether recurrence comes from the card itself or an assembled multi-card loop;
- **game-structural cardinality bound** where relevant.

These facts are mechanically meaningful whether or not the UI calls the card an Engine.

## 4. Preserved adversarial lessons

### Toski vs Chivalric Alliance

The difference remains real:

- Toski preserves per-creature multiplicity inside one combat-damage opportunity;
- Chivalric Alliance threshold-compresses multiple attackers into one draw trigger per qualifying attack event.

Store that as input aggregation + firing multiplicity/opportunity facts.

### Grazilaxx

`one or more creatures` compresses creature multiplicity for a damaged player. Multiple damaged players can still produce multiple triggers. Preserve both aggregation and player-cardinality structure.

### Nest of Scarabs

`one or more` can compress **trigger count** while `that many` preserves **output magnitude**. Trigger multiplicity and output magnitude are different coordinates.

### Lotus Cobra

Each land-entry event can independently produce mana. The normal one-land-play rule constrains one input source; it is not a processor-intrinsic once-per-turn cap.

### Phyrexian Arena / The One Ring

Scheduled/tap-limited firing is a hard fact. It should not force the cards out of an ordinary player search for `card engine`; the UI can instead show the throughput profile.

## 5. Derived `Engine` search view

Foundry may expose an `Engine` filter/search alias built from processor facts.

The final strategic/search layer may support profiles such as:

- recurring value source;
- input-scalable processor;
- scheduled recurring source;
- repeatable activated processor;
- stored-capacity source;
- event-responsive processor;
- combo/loop component.

Those are search/explanation projections. They should not become mutually exclusive canonical families unless later evidence forces one.

## 6. Former Engine children

The earlier children are demoted as canonical ontology nodes:

- Card Engine;
- Mana Engine;
- Blink Engine;
- Death-Trigger Engine;
- Sacrifice Engine.

Their useful queries remain available compositionally:

- processor facts + `output_resource = card-origin`;
- processor facts + `output_resource = mana`;
- processor facts + `operation = exile/return`;
- processor facts + `input/listener = dies/death event`;
- processor facts + `input/action = sacrifice`.

This is more consistent and avoids a heterogeneous child tree organized by different dimensions.

## 7. `turn_structure_bound`

The old name remains mechanically useful only as a coordinate and is subject to the naming audit.

The surviving fact is approximately:

> after one output opportunity, another output requires another discrete turn-structure opportunity rather than additional supplied inputs within the current opportunity.

This should be represented as a firing/opportunity cap, not as a family.

## 8. Combo relationship

Infinite-combo potential remains separate from processor mechanics.

A card may:

- participate in a loop without being independently repeatable;
- be a repeatable processor without forming a combo;
- be both;
- be neither.

Future combo graph work should use producer/consumer signatures rather than retrofit `Engine` membership.

## 9. Searcher B consequence

Searcher B should compare the canonical processor coordinates directly.

A user searching `engine` can receive a derived view, but similarity should not be dominated by whether two cards cross a custom boolean Engine threshold.

This change preserves the useful discoveries from the earlier Engine work while removing the weakest part: a project-specific redefinition of a broad community noun.

## 10. Control boundary

No S16B freeze, broad corpus reclassification, implementation acceptance, merge, accepted-head/main movement, AQ4 resumption, Bridge activation, or Step6 is authorized.

> **PRESERVE TRUTH, NOT PLUMBING.**
