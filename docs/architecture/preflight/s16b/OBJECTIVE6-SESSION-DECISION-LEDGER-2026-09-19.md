# Objective 6 — Session Decision Ledger — 2026-09-19

**Date:** 2026-09-19  
**Status:** Consolidated Captain decision ledger for the current S16B semantic-design session.  
**Scope:** Records decisions and working structures reached during the 2026-09-19 Objective 6 session so they are not stranded in chat history.  
**Authority boundary:** Documentation only. This file does not freeze S16B, accept implementation, merge PR #70, move the accepted implementation head, resume AQ4, activate Bridge v0, authorize Step6, or move `main`.

The governing principle remains:

> **PRESERVE TRUTH, NOT PLUMBING.**

---

## 1. Status vocabulary used in this ledger

- **CAPTAIN-APPROVED** — the Captain explicitly accepted the structural decision.
- **WORKING** — sufficiently useful to preserve and test, but not frozen.
- **OPEN** — intentionally unresolved; future adversarial testing is required.

This ledger is a consolidation artifact. More detailed reasoning remains in the dedicated semantic documents and Issue #1 checkpoints.

---

## 2. Product/UI semantic-explanation rule — CAPTAIN-APPROVED

Foundry's internal semantic representation may use hard predicates, coordinates, dependencies, and accounting fields, but the user-facing UI should explain membership in plain English.

Core presentation rule:

> **Hard predicate -> matched qualifiers -> simple human-readable explanation.**

For every trunk/branch/subclass, the UI should be able to answer:

> **Why does this card count as this?**

The explanation should be generated from the same facts that caused semantic membership rather than from opaque recommendation text.

Examples:

- Rampant Growth / Tutor: `Basic Land`, `To Battlefield`, `Ramp` -> "Searches your library for a basic land and puts it onto the battlefield tapped."
- Rhystic Study / Card Engine -> "Can repeatedly turn opponents casting spells into card draw unless they pay."
- Utopia Sprawl / source augmentation -> "Adds another mana each time the enchanted Forest is tapped for mana."

Advanced machine-facing facts need not be shown by default. They may be exposed through drill-down UI where useful.

The website may separately provide educational guidance about concepts such as Card Advantage, Sifting, Prospecting, Ramp, Fast Mana, Engines, and deckbuilding context. That educational layer must not silently turn Foundry core into a prescriptive recommendation engine.

---

## 3. Tutor — CAPTAIN-APPROVED TRUNK DIRECTION

### 3.1 Trunk decision

**Tutor should be a TRUNK.**

The earlier attempt to exclude basic-land search from Tutor was rejected as an artificial semantic boundary.

Working trunk concept:

> **Tutor** — targeted retrieval from the broader library that lets the player select a specific card or a card satisfying stated criteria and move it to a privileged destination or use.

This means cards such as Rampant Growth are legitimately a form of Tutor even if the community would usually describe them more specifically as basic-land tutors or ramp spells.

### 3.2 Tutor dimensions

Tutor should not be represented as a Cartesian explosion of names. Important dimensions should be stored independently.

Useful dimensions include:

- **search domain / eligibility** — any card, land, basic land, creature, artifact, enchantment, legendary card, named card, subtype, mana-value restriction, color restriction, etc.;
- **destination** — hand, battlefield, top of library, graveyard, exile/access, or another defined destination;
- **quantity** — one, multiple, variable;
- **reveal requirement / visibility**;
- **additional cost or dependency** where mechanically relevant.

Domain-specific family labels such as `Basic Land Tutor`, `Land Tutor`, or `Creature Tutor` may be useful where they earn clear gameplay meaning.

Destination is strategically important and should be highly visible in UI, but should generally be represented as a hard coordinate rather than forcing a separate ontology branch for every combination.

### 3.3 Tutor vs Prospecting

The working distinction remains:

- **Tutor** — targeted retrieval from the broader library;
- **Card Prospecting** — selection from a bounded exposed sample of the library.

Therefore cards such as Impulse or Collected Company remain Prospecting rather than Tutor even though they select among cards.

---

## 4. Engine hierarchy — CAPTAIN-APPROVED WORKING STRUCTURE

Detailed artifact:

`docs/architecture/preflight/s16b/OBJECTIVE6-ENGINE-HIERARCHY-2026-09-19.md`

### 4.1 Parent ruling

**Engine is the parent semantic concept.**

Domain-specific engines descend from the parent only where they satisfy the Engine predicate and earn a hard domain-specific definition.

Examples under consideration/working use include:

- Card Engine;
- Mana Engine;
- Blink Engine;
- Death-Trigger Engine;
- Sacrifice Engine (candidate; exact boundary with Sacrifice Outlet remains open);
- other future validated engine families.

Not every community phrase ending in "engine" should become canonical automatically.

### 4.2 Working Engine structure

An Engine is a reusable/scalable processing mechanism. Current working tests include:

1. **Reusable processor** — after processing one qualifying input/event, can the mechanism process another?
2. **Input scalability** — do additional qualifying inputs/events produce additional outputs?
3. **No intrinsic throughput ceiling** — does the mechanism itself avoid a once-per-turn, once-per-phase, or equivalent internal ceiling?
4. **Processor preservation** — does processing one input leave the processor able to process the next unless an explicit input/outside effect removes it?
5. **Turn-structure freedom** — can additional qualifying inputs be processed without having to manufacture another normally discrete game opportunity such as another combat, upkeep, end step, or turn?

External fuel dependence does **not** disqualify Engine membership.

Examples:

- Carrion Feeder needs creatures;
- Skirge Familiar needs cards in hand;
- Treasonous Ogre needs life;
- Sram needs qualifying Auras/Equipment/Vehicles;
- Lotus Cobra needs land-entry events;
- Rhystic Study needs opponents casting spells.

The relevant question is what the mechanism does when additional qualifying inputs exist.

### 4.3 Input supply vs processor throughput

A finite or deck-dependent supply of inputs is not the same as an intrinsic processor cap.

Examples:

- Carrion Feeder can run out of creatures, but the sacrifice ability itself is not capped once per turn.
- Sram can run out of qualifying cards, but its trigger itself does not impose a per-turn cap.
- Lotus Cobra may see only one ordinary land play, but its trigger processes every land-entry event supplied to it.

### 4.4 Turn-structure-bound qualifier — CAPTAIN-APPROVED

A new hard qualifier should capture mechanisms where repeated output requires creation of another normally discrete game opportunity.

Working name:

`turn_structure_bound`

Examples:

- **Chivalric Alliance** — more creatures in one attack do not create more card-draw triggers; another output generally requires another qualifying attack event / combat opportunity. Current working result: recurring Card Advantage potential, **not Card Engine**.
- **Phyrexian Arena** — output is scheduled by upkeep; recurring Card Advantage, **not Card Engine**.
- **Lotus Cobra** — not turn-structure-bound in this sense because additional land-entry events can be supplied during the same ordinary turn through fetches, ramp, land tokens, put-onto-battlefield effects, etc. Current working result: **Mana Engine**.
- **Sram, Senior Edificer** — additional qualifying spells can be cast in ordinary playable windows; current working result: **Card Engine**.

The distinction should be mechanical, not based on how many support cards happen to exist in the format.

---

## 5. Card Advantage / Card Engine refinements preserved today

Detailed artifact:

`docs/architecture/preflight/s16b/OBJECTIVE6-CARD-ADVANTAGE-ENGINE-REFINEMENT-2026-09-19.md`

Today's session reaffirmed that the Card Advantage work should later receive the same breadth-first adversarial research treatment now applied to Ramp.

Existing working principles preserved:

- Card Advantage is relative rather than synonymous with cards drawn or hand size.
- Multiplayer accounting uses pairwise opponent-relative differentials and may yield Advantage, Parity, Disadvantage, or Mixed.
- Semantic function membership is distinct from realized game-state accounting.
- A retained card-origin permanent contributes retained-object value only when it has independent useful functionality beyond the same card-resource-producing operation already being counted.
- Setup dependency and operating dependency should be mechanically decomposed rather than collapsed into a vague `conditional` label.
- Chivalric Alliance remains an important boundary example because its repeated output is constrained by combat opportunity structure and prerequisite sustainability.
- Sram and Rhystic Study remain positive Card Engine anchors under the current working model.
- Stored Capacity remains a mechanical pattern/coordinate rather than a ratified named trunk; Dawn of a New Age remains the primary anchor.

**OPEN:** perform a dedicated web/research scan for Card Advantage mechanisms and adversarial anchors analogous to the Ramp scan before S16B freeze.

---

## 6. Ramp — CAPTAIN-APPROVED TRUNK

Detailed artifact:

`docs/architecture/preflight/s16b/OBJECTIVE6-RAMP-DECISION-MAP-2026-09-19.md`

### 6.1 Trunk definition

**Ramp is a TRUNK.**

Ramp should be defined by functional outcome rather than by permanent source type.

Working plain-English definition:

> **Ramp** — a card or effect that increases the controller's usable mana or mana-producing capacity beyond ordinary resource development.

Permanent vs temporary is not a Ramp membership boundary. It is a lower-level property.

Examples intentionally included:

- Rampant Growth;
- Llanowar Elves;
- Sol Ring;
- Dark Ritual;
- Exploration;
- Burgeoning;
- mana doublers/triplers;
- Treasonous Ogre;
- Skirge Familiar;
- token/object-based mana production.

### 6.2 Conditionality should be decomposed

Do not create a broad catch-all class called `Conditional Ramp` merely because realization needs setup.

Instead record the actual prerequisite/dependency facts.

Useful facts include:

- requires another land in hand;
- requires existing mana infrastructure;
- requires a host permanent;
- requires an opponent action/event;
- requires a game event;
- consumes life/cards/creatures/objects;
- creates stored mana capacity;
- has delayed timing;
- scales with host/source reuse.

Examples:

- **Exploration** — Ramp through additional-land permission; requires an extra land to realize acceleration.
- **Burgeoning** — same broad family, additionally dependent on opponents playing lands.
- **Mana doublers/triplers** — require existing productive infrastructure, but scale that infrastructure rather than supplying an independent source.

### 6.3 Fast Mana — CAPTAIN-APPROVED CHILD

**Fast Mana is a named child/subclass of Ramp.**

It is not defined by permanence.

Working hard predicate:

> **Fast Mana** — Ramp whose casting, activation, or initial relevant use can produce a strictly positive net amount of usable mana during that same turn after subtracting the mana required to deploy/use the relevant mana-producing effect.

The calculation uses **incremental mana attributable to the accelerant**, not total output of an already-existing source it modifies.

Positive anchors:

- Dark Ritual;
- Sol Ring;
- Elvish Spirit Guide;
- Lotus Petal;
- Mana Vault.

Negative/boundary anchors:

- Llanowar Elves — Ramp, not ordinarily Fast Mana;
- Rampant Growth — Ramp, not Fast Mana;
- Utopia Sprawl — Ramp/source augmentation, not Fast Mana;
- Exploration — conditional/enabling Ramp, not Fast Mana;
- Burgeoning — conditional additional-land deployment, not Fast Mana.

A reusable converter does not become Fast Mana merely because repeated activations eventually cross the deployment-cost break-even point.

Example:

- **Treasonous Ogre** — costs four mana and can repeatedly pay life for red mana. It is Ramp and a Mana Engine, but does not become Fast Mana merely because enough activations can eventually produce more mana than its deployment cost.

### 6.4 Resource-to-Mana Conversion — WORKING MECHANISM/FAMILY

This emerged as a useful Ramp mechanism.

> Convert a non-mana resource into usable mana or into an object that can later supply mana.

Anchors:

- Treasonous Ogre — life -> red mana;
- Skirge Familiar — card in hand -> black mana;
- Warren Soultrader — life + creature -> Treasure -> mana.

Important qualifiers:

- input resource type;
- input quantity;
- input consumed?;
- direct vs mediated conversion;
- output amount/color;
- intermediate object/resource;
- immediate reuse?;
- intrinsic throughput cap?;
- persistent vs one-shot converter.

**Warren Soultrader is also a Captain-recognized Role Compression example** because it participates meaningfully in multiple semantic roles rather than being reducible to only one function.

### 6.5 Mana-source creation — WORKING MECHANISM

Create a new permanent/object that itself carries mana-producing capacity.

Examples identified in the research scan:

- Treasure tokens — consumable stored mana capacity;
- Powerstone tokens — persistent mana sources with spending restrictions;
- Overlord of the Hauntwoods — creates Everywhere land tokens;
- Roxanne, Starfall Savant — creates Meteorite artifact tokens that later produce mana;
- Eldrazi Spawn/Scions — creature bodies that can be consumed for mana.

Useful object qualifiers:

- object type;
- persistent source vs consumable reserve;
- consumed for mana?;
- enters tapped?;
- spending restriction?;
- color flexibility;
- independent nonmana functionality.

### 6.6 Mana-source augmentation — WORKING MECHANISM

Increase the output of an existing mana-producing object by a fixed additive amount.

Primary anchors:

- Utopia Sprawl;
- Wild Growth.

Important property:

`scales_with_host_reuse`

If the host is untapped/reused, the attached augmentation can apply again.

Human UI should explain this plainly, e.g.:

> "Each time the enchanted land produces mana, this adds another mana."

### 6.7 Mana multiplier — WORKING MECHANISM / possible named child

Proportionally scale existing mana production rather than adding a fixed amount.

Anchors:

- Mana Reflection;
- Nyxbloom Ancient.

This is mechanically distinct from fixed source augmentation.

**OPEN:** whether `Mana Multiplier` should be a canonical named child under Ramp or remain a mechanism/facet.

### 6.8 Mana-source granting — WORKING MECHANISM

Give existing objects mana-producing capability they do not intrinsically have.

Primary anchor:

- Cryptolith Rite — creatures become mana sources.

This is distinct from creating a new source and from augmenting an existing mana source.

### 6.9 Event-to-Mana Conversion — WORKING MECHANISM

Convert qualifying game events into immediate mana or mana-capable objects.

Examples:

- Lotus Cobra — land enters -> mana;
- Birgi, God of Storytelling — spell cast -> red mana;
- Neheb, the Eternal — opponent life loss -> postcombat mana;
- Pitiless Plunderer — creature death -> Treasure;
- Smothering Tithe — opponent card draw, subject to payment choice -> Treasure.

Direct and mediated output should remain distinct.

### 6.10 Board/state-scaled mana — WORKING MECHANISM

Mana output scales according to another game-state quantity.

Examples:

- Cabal Coffers — Swamp count;
- Nykthos, Shrine to Nyx — devotion;
- Selvala, Heart of the Wilds — creature power.

Useful qualifier:

`output_scaling_basis`

Potential values may include land/subtype count, devotion, power, creature count, event count, opponent state, or another mechanically defined quantity.

### 6.11 Mana-source reuse — WORKING MECHANISM

Enable an existing mana-producing object to be used additional times.

Primary anchor:

- Earthcraft — turns an available creature into an untap of a basic land, enabling reuse of that mana source.

This mechanism is especially important for interaction with source augmentation such as Utopia Sprawl/Wild Growth.

**OPEN:** exact Ramp membership boundary for pure untap/source-reuse effects.

### 6.12 Mana preservation — adjacent, not automatically Ramp

Effects that preserve already-produced mana do not necessarily increase mana production.

Primary anchor:

- Omnath, Locus of Mana — preserves green mana across steps/phases.

Current direction: mana preservation belongs in the mana-resource semantic neighborhood but is not automatically Ramp.

---

## 7. Lotus Cobra adjudication — CAPTAIN-APPROVED WORKING RESULT

**Lotus Cobra should be treated as Ramp and a Mana Engine under the current Engine model.**

Reasoning:

- input/event = a land enters the battlefield under the controller's control;
- each qualifying land-entry event creates an additional mana output;
- the Cobra mechanism itself does not say once per turn;
- the normal one-land-play rule limits only one common way of supplying land-entry events;
- fetch lands, ramp spells, land tokens, put-onto-battlefield effects, and similar mechanics can supply additional qualifying events within the same turn structure;
- processing one land-entry event does not make the processor less capable of processing the next.

This differs from Chivalric Alliance:

- adding more creatures to one attack does not create more Alliance draw triggers;
- another draw generally requires another qualifying attack event / combat opportunity;
- therefore the Alliance is turn-structure-bound in a way Lotus Cobra is not.

This also resolves the apparent Sram parallel:

- Sram needs a qualifying-card supply;
- Lotus Cobra needs a land-entry-event supply;
- neither external fuel dependency disqualifies Engine membership;
- what matters is that additional supplied qualifying inputs can be processed without an intrinsic throughput ceiling or required new discrete turn-structure window.

---

## 8. Role Compression — additional anchor

Role Compression remains an unresolved concept requiring a hard predicate, but today's Ramp work added a strong anchor:

- **Warren Soultrader** — sacrifice outlet / life payment / creature conversion / Treasure production / mana infrastructure / combo-enabling behavior.

Roxanne, Starfall Savant is another strong multi-function example because it combines mana-source creation, damage, artifact-token interaction, and source augmentation.

Do not canonize Role Compression solely from these examples; retain them as adversarial anchors for the later dedicated definition.

---

## 9. Ramp decision map as of this ledger

The current conceptual map is:

```text
Ramp [TRUNK]
|
+-- Fast Mana [named child]
|
+-- Land Acquisition / Deployment
+-- Additional Land Deployment
+-- Independent Mana Source
+-- Mana-Source Creation
+-- Mana-Source Granting
+-- Mana-Source Augmentation
+-- Mana Multiplier
+-- Resource-to-Mana Conversion
+-- Event-to-Mana Conversion
+-- Board/State-Scaled Mana
+-- Mana-Source Reuse
+-- One-Shot / Burst Mana

Cross-cutting structures / coordinates:
+-- Mana Engine
+-- Stored Capacity
+-- Role Compression
+-- direct vs mediated
+-- persistent vs consumable
+-- immediate vs delayed
+-- input/resource type
+-- input consumed
+-- host required
+-- infrastructure required
+-- opponent/event dependency
+-- output scaling basis
+-- intrinsic throughput cap
+-- turn_structure_bound
+-- spending restrictions
+-- scales_with_host_reuse
```

This diagram is a decision map, **not** a guarantee that every listed mechanism will become a public named branch. The recurring rule remains:

> **Does this distinction deserve a noun, or does it deserve a property?**

---

## 10. Explicit open questions after today's work

The following remain intentionally unresolved:

1. exact final Engine predicate and freeze criteria;
2. exact Ritual boundary beneath Ramp / Fast Mana;
3. whether Mana Multiplier earns a named canonical child;
4. exact Ramp membership rule for pure source-untap/reuse effects;
5. exact Treasure/mana-object boundary where token/resource creation should count as Ramp;
6. cost reduction vs Ramp — current direction keeps supply-side acceleration distinct from price-side reduction, but this has not been fully adversarially tested;
7. final Role Compression predicate;
8. full Card Advantage adversarial research pass;
9. final Card Advantage hard predicate;
10. exact Tutor hard predicate and child/facet canonization after broader adversarial testing;
11. additional Engine boundary tests, including once-each-turn processors, self-expiring processors, phase-gated processors, and processors whose output replenishes their own next input.

---

## 11. Durable companion artifacts / checkpoints

Companion docs on the same draft documentation branch:

- `docs/architecture/preflight/s16b/OBJECTIVE6-CARD-ADVANTAGE-ENGINE-REFINEMENT-2026-09-19.md`
- `docs/architecture/preflight/s16b/OBJECTIVE6-ENGINE-HIERARCHY-2026-09-19.md`
- `docs/architecture/preflight/s16b/OBJECTIVE6-RAMP-DECISION-MAP-2026-09-19.md`

Relevant durable Issue #1 checkpoints from today's session include:

- `5743503394` — Engine parent/child ruling;
- `5743519807` — Engine hierarchy file checkpoint;
- `5744090506` — hard predicates -> plain-English UI explanation rule;
- `5744361495` — Ramp trunk / permanence-is-not-boundary direction;
- `5744633504` — Ramp decision map checkpoint.

This ledger should receive its own Issue #1 checkpoint after creation/read-back.

---

## 12. Control boundary

Nothing in this ledger authorizes implementation or control-state movement.

Standing controls remain:

- S15 CLOSED;
- S16A_ACCEPTED NO;
- S16B_FROZEN NO;
- AQ4 PAUSED;
- Bridge v0 PARKED_UNUSED;
- Step6 NO;
- MERGE NO;
- MAIN_MOVE NO.

PR #70 remains a documentation-only draft unless separately changed by explicit Captain direction.
