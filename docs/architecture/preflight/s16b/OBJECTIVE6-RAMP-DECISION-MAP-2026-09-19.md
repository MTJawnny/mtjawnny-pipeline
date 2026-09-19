# Objective 6 — Ramp Decision Map

**Date:** 2026-09-19  
**Status:** Captain-approved Ramp trunk structure with working mechanism map; remaining adversarial boundaries explicitly open before S16B freeze.  
**Authority boundary:** Documentation only. This does not accept implementation, freeze S16B, merge PR #70, move the accepted implementation head, resume AQ4, activate Bridge v0, authorize Step6, or move `main`.

## 1. Core structural decision

**Ramp is a TRUNK.**

Ramp membership is determined by the functional outcome of increasing mana availability, mana-producing capacity, or access to mana earlier or beyond normal resource development. Ramp is **not** restricted to permanent sources.

A permanent/temporary distinction is therefore not a Ramp boundary. It is a lower-level mechanical property.

Working plain-English definition:

> **Ramp** — a card or effect that increases the controller's usable mana or mana-producing capacity beyond ordinary resource development.

Examples intentionally inside the Ramp trunk include:

- Rampant Growth — land acquisition/deployment;
- Llanowar Elves — independent reusable mana source;
- Sol Ring — independent reusable mana source and Fast Mana;
- Dark Ritual — one-shot/burst mana and Fast Mana;
- Exploration / Burgeoning — conditional additional-land deployment;
- Mana doublers/triplers — multiplicative scaling of existing production;
- Treasonous Ogre / Skirge Familiar — repeatable resource-to-mana conversion.

## 2. General semantic rule

**Membership says what functional job the card can perform. Qualifiers say what setup, dependency, timing, infrastructure, and resource expenditure are required to realize that function.**

Do not exclude a card from Ramp merely because the Ramp is conditional, temporary, resource-intensive, mediated through another object, or dependent on existing infrastructure.

Avoid a broad catch-all public class called `Conditional Ramp`. Instead, represent the mechanical reason realization is conditional.

Examples of useful realization/dependency facts:

- requires another land in hand;
- requires existing mana-producing infrastructure;
- requires a host permanent;
- requires an opponent event;
- requires a game event such as a land entering or creature dying;
- consumes life/cards/creatures/objects;
- creates stored mana capacity rather than immediate mana;
- delayed by timing restrictions;
- scales with repeated use of a host/source.

## 3. Fast Mana — approved child concept

**Fast Mana is a named Ramp subclass.**

Fast Mana is not defined by permanence. Both one-shot and persistent sources may qualify.

Working hard rule:

> **Fast Mana** — Ramp whose casting, activation, or initial relevant use can produce a strictly positive net amount of usable mana during that same turn after subtracting the mana required to deploy/use the relevant mana-producing effect.

The calculation is based on **incremental mana attributable to the accelerant**, not total output of an already-existing source it modifies.

Positive anchors:

- Dark Ritual — spend `{B}`, receive `{BBB}`; immediate positive mana delta;
- Sol Ring — spend `{1}`, can immediately tap for `{CC}`; positive same-turn mana delta;
- Elvish Spirit Guide — exile from hand for `{G}` with no mana deployment cost;
- Lotus Petal — zero-mana deployment, sacrifice for one mana;
- Mana Vault — deployment cost lower than immediate mana output.

Negative/boundary anchors:

- Llanowar Elves — Ramp, ordinarily not Fast Mana because normal deployment does not provide a positive same-turn mana delta;
- Rampant Growth — Ramp, not Fast Mana; fetched land enters tapped and immediate mana delta is not positive;
- Utopia Sprawl — Ramp/source augmentation, not Fast Mana under the incremental-delta rule;
- Exploration — conditional land-deployment Ramp, not Fast Mana because it enables use of an externally supplied land rather than intrinsically supplying the immediate positive mana delta;
- Burgeoning — same broad additional-land-deployment family, with opponent-event dependency.

### Fast Mana vs repeated Engine operation

A reusable converter does **not** become Fast Mana merely because repeated activations during the deployment turn eventually cross break-even.

Treasonous Ogre is the key adversarial anchor:

- deployment cost: `{3}{R}`;
- repeatable conversion: pay 3 life -> add `{R}`;
- it can eventually produce more mana than was spent if activated repeatedly;
- that positive delta emerges from repeated Engine operation, not the initial deployment/use cycle.

Therefore Treasonous Ogre is working-classified as **Ramp + Mana Engine + Resource-to-Mana Conversion**, but **not Fast Mana**.

## 4. Ramp mechanism families identified so far

These are mechanically meaningful families/coordinates. Not all are necessarily final public-facing named subclasses.

### 4.1 Independent mana source

The card/permanent itself becomes a reusable source of mana.

Examples:
- Llanowar Elves;
- Sol Ring.

Useful qualifiers:
- card/permanent type;
- tap requirement;
- summoning-sickness exposure;
- persistence;
- color/output restriction;
- activation cost.

### 4.2 Land acquisition / deployment

Moves or creates land resources in a way that increases mana development.

Examples:
- Rampant Growth;
- land tutors that put the chosen land directly onto the battlefield when their normal function accelerates mana development.

Useful qualifiers:
- search domain;
- destination;
- tapped/untapped entry;
- basic/nonbasic restriction;
- whether the card itself supplies access to the land.

### 4.3 Additional land deployment

Increases the number of lands the controller may deploy rather than supplying the land itself.

Positive anchors:
- Exploration;
- Burgeoning.

Key dependency:
- **external land inventory** is required.

Exploration therefore has Ramp membership but can realize zero acceleration when no additional land is available.

Burgeoning adds an additional opponent-event dependency: an opponent must play a land to create the opportunity.

### 4.4 Mana-source augmentation

Adds a fixed amount of mana output to an existing mana-producing source.

Positive anchors:
- Utopia Sprawl;
- Wild Growth.

Utopia Sprawl is a key anchor because it does not create an independent mana source. It augments the enchanted Forest.

Important property:

> **scales with host reuse** — if the enchanted land is untapped and used again, the augmentation applies again.

This property is strategically relevant to land-untap effects without requiring a public ontology term such as `Untap-Synergy Ramp`.

### 4.5 Mana multiplier

Scales existing mana production proportionally rather than adding a fixed amount.

Positive anchors:
- Mana Reflection;
- Nyxbloom Ancient.

Working distinction:

- **Source Augmentation** = fixed additive increase;
- **Mana Multiplier** = proportional scaling of existing production.

Mana multipliers are Ramp even though they require an existing productive base.

### 4.6 Resource-to-Mana Conversion

Converts a non-mana resource into mana or mana capacity.

Positive anchors:

- Treasonous Ogre — `life -> mana`;
- Skirge Familiar — `card in hand -> mana`;
- Warren Soultrader — `life + creature -> Treasure -> mana`.

Useful hard facts:

- input resource type;
- input quantity;
- input consumed?;
- output amount/color;
- direct vs mediated conversion;
- intermediate object/resource;
- immediately reusable?;
- intrinsic throughput cap?;
- one-shot vs persistent converter.

### Direct vs mediated conversion

Examples:

- Treasonous Ogre: `life -> mana`;
- Skirge Familiar: `card -> mana`;
- Warren Soultrader: `life + creature -> Treasure -> mana`.

Warren Soultrader is additionally a strong **Role Compression** anchor because the same mechanism intersects sacrifice, life payment, creature-resource conversion, Treasure generation, stored mana capacity, and potentially Mana Engine behavior.

### 4.7 Mana-source creation

Creates a new permanent/object that carries mana-producing capacity.

Research anchors:

- Overlord of the Hauntwoods — creates tapped Everywhere land tokens;
- Roxanne, Starfall Savant — creates tapped Meteorite artifact tokens that later produce mana;
- Powerstone tokens — persistent artifact mana sources with spending restrictions;
- Treasure tokens — consumable stored mana capacity;
- Gold tokens — consumable mana-capable objects with a different activation structure;
- Eldrazi Spawn/Scion — creature bodies that can be consumed for mana.

Useful qualifiers:

- object type: land/artifact/creature/etc.;
- persistent source vs consumed-for-mana;
- enters tapped?;
- mana spending restriction?;
- color flexibility;
- additional nonmana functionality.

### 4.8 Mana-source granting

Confers mana-producing capability on existing objects that do not necessarily produce mana intrinsically.

Positive anchor:
- Cryptolith Rite — turns creatures into mana sources by granting a tap-for-mana ability.

This is distinct from:

- creating new mana sources;
- augmenting an existing mana source.

Key dependency:
- requires qualifying battlefield objects to grant the ability to.

### 4.9 Event-to-Mana Conversion

Converts recurring game events into mana or mana-capable objects.

Research anchors:

- Lotus Cobra — land-entry event -> mana;
- Birgi, God of Storytelling — spell-cast event -> mana;
- Neheb, the Eternal — opponent life loss -> later mana;
- Pitiless Plunderer — creature death -> Treasure -> mana;
- Smothering Tithe — opponent draw, subject to payment choice -> Treasure -> mana.

Important distinction:

- `event -> mana` = direct;
- `event -> mana-capable object -> mana` = mediated.

Many event-to-mana cards are candidates for **Mana Engine** membership when they satisfy the parent Engine predicate.

### 4.10 Board/state-scaled mana

Mana output is a function of another battlefield/game-state quantity rather than a fixed output amount.

Research anchors:

- Selvala, Heart of the Wilds — output scales with greatest creature power;
- Cabal Coffers — output scales with number of Swamps;
- Nykthos, Shrine to Nyx — output scales with devotion.

Useful coordinate:

> **output scaling basis** — fixed / land count / subtype count / devotion / creature power / creature count / event count / opponent state / other measurable state.

This is more informative than a simple `produces_multiple_mana` flag.

### 4.11 Mana-source reuse

Enables an existing mana-producing source to be used additional times.

Research anchor:
- Earthcraft — uses an untapped creature to untap a basic land.

Structural form:

`resource/input -> source reuse -> additional mana production`

This is especially important because source reuse inherits source augmentation/multiplication. Untapping a land carrying Utopia Sprawl or another augmentation repeats the augmented output.

### 4.12 One-shot / burst mana

Produces mana once rather than creating persistent capacity.

Positive anchors:
- Dark Ritual;
- Elvish Spirit Guide;
- Lotus Petal.

`Ritual` may deserve a narrower named family, but exact Ritual membership has not yet been separately adjudicated.

## 5. Stored mana capacity and mana preservation

### Stored mana capacity

Some effects create an object/reserve that can later be converted into mana rather than producing mana immediately.

Examples:
- Treasure;
- Gold;
- some counter-based reserves;
- Black Market-like accumulated capacity.

This relates to the broader **Stored Capacity** mechanical pattern already identified elsewhere in Objective 6:

`setup/input -> stored internal or object capacity -> later discharge/use`

Stored Capacity is currently a working coordinate/pattern, **not yet a canonized trunk**.

### Mana preservation is not automatically Ramp

A card may preserve already-produced mana without increasing production.

Anchor:
- Omnath, Locus of Mana — changes mana retention across steps/phases.

Working direction:

> **Mana preservation belongs in the mana-resource semantic neighborhood but is not itself necessarily Ramp.**

## 6. Ramp and Engine interaction

**Ramp** and **Engine** answer different questions.

Ramp asks:

> Does this mechanism increase usable mana or mana-producing capacity?

Engine asks:

> Is this a reusable/scalable processing structure satisfying the parent Engine predicate?

Therefore a card may be:

- Ramp but not Engine;
- Engine but not Ramp;
- both Ramp and Mana Engine;
- Fast Mana but not Mana Engine;
- Mana Engine but not Fast Mana.

Working anchors:

- Dark Ritual — Ramp + Fast Mana; not Engine;
- Sol Ring — Ramp + Fast Mana; not currently an Engine under the scalable-input parent test;
- Treasonous Ogre — Ramp + Mana Engine + Resource-to-Mana Conversion; not Fast Mana;
- Skirge Familiar — strong Ramp + Mana Engine candidate via card-to-mana conversion;
- Lotus Cobra — strong conditional/event-driven Ramp + Mana Engine candidate pending explicit adjudication.

## 7. Role Compression interaction

Ramp mechanisms should be independently represented even when a card performs several strategic jobs.

Key anchors:

### Warren Soultrader

Captain explicitly identified Warren Soultrader as **Role Compression**.

Relevant overlapping functions/mechanics include:

- sacrifice processing;
- life payment;
- creature-resource conversion;
- Treasure creation;
- stored mana capacity;
- Ramp;
- possible Mana Engine behavior.

### Roxanne, Starfall Savant

Research identifies Roxanne as another strong Role Compression test because it combines:

- mana-source creation through Meteorite tokens;
- direct damage associated with those tokens entering;
- artifact-token mana interaction;
- augmentation of artifact-token mana production.

Final Role Compression predicate remains separately unresolved.

## 8. UI / explanation rule

Machine-facing semantics may be detailed; user-facing explanations should be simple.

General product rule:

> **Hard predicate -> matched qualifiers -> plain-English explanation.**

Examples:

### Utopia Sprawl

**Ramp — Mana-source augmentation**  
"Adds another mana whenever the enchanted Forest is tapped for mana. Reusing that land repeats the extra mana."

Possible compact chips:

`Forest Required` · `Persistent` · `Source Augmentation` · `Benefits From Untap`

### Exploration

**Ramp — Additional land deployment**  
"Lets you play an additional land, but you must already have another land available."

Possible compact chips:

`Land In Hand Required` · `Conditional` · `Persistent Permission`

### Treasonous Ogre

**Ramp — Mana Engine**  
"Repeatedly converts 3 life into one red mana."

Possible compact chips:

`Life-to-Mana` · `Reusable` · `No Tap` · `Not Fast Mana`

The UI should explain *why* a card fits a branch rather than expose internal implementation vocabulary unnecessarily.

## 9. Current working tree

```text
Ramp [TRUNK]
|
+-- Fast Mana [named child; hard same-turn positive-delta rule]
|
+-- mechanism families / coordinates
    |
    +-- Independent Mana Source
    +-- Land Acquisition / Deployment
    +-- Additional Land Deployment
    +-- Mana-Source Augmentation
    +-- Mana Multiplier
    +-- Resource-to-Mana Conversion
    +-- Mana-Source Creation
    +-- Mana-Source Granting
    +-- Event-to-Mana Conversion
    +-- Board/State-Scaled Mana
    +-- Mana-Source Reuse
    +-- One-Shot / Burst Mana

Cross-cutting semantic structures:
- Mana Engine
- Stored Capacity
- Role Compression
- dependency / realization qualifiers
```

This tree intentionally does **not** assert that every mechanism family deserves a final public-facing named subclass. Some may remain machine-facing coordinates while the UI renders them in plain English.

## 10. Important hard principles already established

1. **Ramp is not permanent-only.**
2. **Temporary mana can be Ramp.**
3. **Conditional Ramp remains Ramp; the condition should be decomposed mechanically.**
4. **Fast Mana is not synonymous with one-shot mana.**
5. **Fast Mana is not synonymous with Ritual.**
6. **Persistent sources can be Fast Mana (Sol Ring).**
7. **One-shot sources can be Fast Mana (Dark Ritual, Elvish Spirit Guide).**
8. **Repeated Engine operation cannot manufacture Fast Mana classification merely by eventually crossing break-even.**
9. **Source augmentation and source multiplication are distinct.**
10. **Creating a mana-capable object, granting mana capability, and augmenting an existing source are distinct mechanisms.**
11. **Direct conversion and mediated conversion are distinct.**
12. **Resource costs such as life, cards, and creatures must be preserved as explicit qualifiers rather than collapsed into a vague `costly` label.**
13. **Mana preservation is not automatically Ramp.**
14. **Ramp membership and Mana Engine membership are independent semantic questions.**
15. **Role Compression should preserve multiple simultaneous functions rather than force a card into one bucket.**

## 11. Open adversarial questions

These remain intentionally unresolved:

### A. Lotus Cobra

Does Lotus Cobra satisfy Mana Engine membership under the current Engine parent predicate?

Relevant facts to adjudicate:
- qualifying input/event: land entering;
- output: immediate mana;
- additional land entries create additional outputs;
- no intrinsic once-per-turn trigger limit;
- input supply and land-play opportunities can still constrain realization.

### B. Ritual

Should `Ritual` become a rigid named Ramp child/family, and if so, what exact predicate distinguishes it from other one-shot Fast Mana such as Elvish Spirit Guide or Lotus Petal?

### C. Treasure / mana-capable object production

Does creating any mana-capable object automatically establish Ramp membership, or must normal operation increase mana access/capacity relative to inputs/costs?

This requires hard tests across:
- Treasure;
- Gold;
- Powerstone;
- Blood-like or other token types with conversion costs;
- creature tokens that can sacrifice for mana;
- objects whose mana is heavily spending-restricted.

### D. Source reuse

When an effect only untaps a mana source rather than producing mana itself, what hard predicate establishes Ramp membership?

Earthcraft is the primary working anchor.

### E. Cost reduction boundary

Current working direction:
- supply-side increase -> Ramp;
- price-side decrease -> Cost Reduction, not Ramp.

This still requires dedicated adversarial testing because both can produce similar practical acceleration.

### F. Mana multiplier naming

Captain has agreed that multiplicative mana scaling belongs within Ramp. Whether `Mana Multiplier` is a canonical named child or remains a prominent mechanism coordinate still requires explicit naming adjudication.

### G. Card Advantage analog

The Ramp research process revealed that Card Advantage deserves a comparable adversarial mechanism scan later. That future pass should seek card-resource mechanisms that challenge the current Card Advantage / Card Replacement / Card Sifting / Card Prospecting structure rather than merely adding more examples.

## 12. Control boundary

This decision map preserves semantic work only. It does **not** authorize:

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
