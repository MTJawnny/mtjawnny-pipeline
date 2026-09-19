# Objective 6 — Card Advantage, Engine, and Stored-Capacity Refinement

**Date:** 2026-09-19  
**Status:** Captain-approved working semantic model; adversarial validation still required before S16B freeze.  
**Authority boundary:** This is a semantic decision record only. It does not accept implementation, freeze S16B, merge a PR, move the accepted implementation head, resume AQ4, activate Bridge v0, authorize Step6, or move `main`.

## Purpose

Preserve the Captain/Manager adjudication that refined three related but distinct ideas:

1. how Foundry should reason about **Card Advantage** without collapsing all conditional draw into one undifferentiated label;
2. what should qualify as a reusable **Engine**, and therefore a **Card Engine** when the output is card resources;
3. how to distinguish an engine from a finite **stored-capacity** mechanism such as Dawn of a New Age.

The central lesson is that a rules-text condition cannot be judged only by the number of prerequisites it mentions. Foundry must preserve the mechanical structure of how a condition is established, how often the game exposes an opportunity to satisfy it, whether satisfying it preserves or degrades future eligibility, and whether additional qualifying inputs can actually increase throughput.

---

# 1. Multiplayer Card Advantage: MIXED accounting result

## 1.1 Captain decision

For multiplayer Card Advantage accounting, preserve the per-opponent relative differential vector rather than forcing all multiplayer outcomes into only Advantage / Parity / Disadvantage.

A fourth accounting result is accepted:

- **MIXED** — at least one opponent-relative differential is positive and at least one is negative.

This is an **accounting result/state**, not a new semantic trunk or a rider term such as `Mixed Card Advantage`.

The working reduction is:

- **Advantage** — every opponent-relative differential is `>= 0`, with at least one `> 0`;
- **Parity** — all opponent-relative differentials are `0`;
- **Disadvantage** — every opponent-relative differential is `<= 0`, with at least one `< 0`;
- **Mixed** — at least one differential is positive and at least one is negative.

An average, range, or other aggregate may be shown as a secondary factual statistic, but should not erase the underlying vector.

### Anchor: Mind Rot

If casting Mind Rot costs the controller one card, the targeted opponent loses two cards, and untouched opponents lose zero:

- versus the targeted opponent: relative differential `+1`;
- versus each untouched opponent: relative differential `-1`.

Therefore a multiplayer result can be **MIXED** even though the same card is straightforward Card Advantage in 1v1.

---

# 2. Card Advantage: classification is not the same as realized game accounting

Foundry must distinguish:

- **semantic function membership** — whether a card intrinsically contains a mechanism that qualifies as Card Advantage under the working semantic model; and
- **realized Card Advantage** — how much relative card-resource advantage that mechanism actually produced in a particular game state or sequence.

A Card Advantage source does not lose semantic membership merely because it was destroyed before generating value, because an opponent paid an optional tax, or because a required event never occurred.

Conversely, a card should not receive Card Advantage membership merely because a contrived game state could eventually make it draw cards. The normal realization burden of its mechanism matters.

---

# 3. Retained-object credit requires independent residual utility

The earlier shorthand `a permanent remains, therefore it counts as an additional card resource` is too broad.

## 3.1 Working rule

A retained card-origin permanent can contribute to Card Advantage only when, after the original card expenditure has been compensated, the retained object still represents **independently useful game functionality beyond the same card-resource-producing operation currently being counted**.

The same resource-generation mechanism should not be counted twice: once as the produced card resource and again merely because the source remains capable of producing more of that same resource.

## 3.2 Elvish Visionary

Elvish Visionary remains a positive anchor.

Its draw replaces the card expenditure while the 1/1 creature remains as independently functional material: it can attack, block, be sacrificed, carry Equipment, and participate in other creature interactions. The retained body is mechanically distinct from the replacement draw.

## 3.3 Chivalric Alliance

An enchantment does not receive retained-object credit merely for continuing to exist.

For Chivalric Alliance, the separate activated ability — `{2}, Discard a card: Create a 2/2 white and blue Knight creature token with vigilance.` — is relevant independent utility. That utility is distinct from the attack-triggered draw mechanism.

Whether that independent utility is sufficient to make Chivalric Alliance a Card Advantage card under the final hard predicate remains **OPEN**. The important ruling here is that the draw ability itself must not serve circularly as both the card-resource output and the reason the retained enchantment counts as additional material.

---

# 4. Realization burden must be mechanically decomposed

`Conditional` is too coarse by itself. Different conditions have radically different realization structures.

Foundry should preserve hard/mechanically grounded properties rather than minting rider names such as `potential card advantage` or `conditional card advantage`.

Relevant dimensions include:

- whether output is autonomous after resolution;
- whether an outside event/input is required;
- whether that event is ambient to normal gameplay or must be deliberately established;
- whether the controller must maintain a prerequisite board state;
- whether the game exposes the opportunity only during a specific phase/step/event;
- whether an opponent can prevent the output;
- whether using the mechanism preserves, consumes, risks, or degrades the state required to use it again;
- whether additional qualifying inputs can increase throughput immediately or whether the mechanism itself imposes a rate ceiling.

These are coordinates/facets, not automatically new nouns.

---

# 5. Setup dependency and operating dependency are different

A mechanism may require substantial setup but little or no continuing support after that setup is converted into internal capacity.

Conversely, a mechanism may have to recreate or preserve its prerequisite state every time it is used.

Foundry should therefore distinguish at least:

- **setup dependency** — what must be true when the mechanism is established or charged;
- **operating dependency** — what must continue to be true for each later operation;
- **future-eligibility effect** — whether satisfying the current operation preserves or degrades the prerequisites needed for the next operation.

---

# 6. Card Advantage anchors under the refined model

## 6.1 Phyrexian Arena

Phyrexian Arena is a Card Advantage source whose output is substantially autonomous after resolution.

Its recurring draw is scheduled by the controller's upkeep. No separate board-state construction, attack sequence, or opponent spell is needed to create each opportunity. Its output remains time-gated, but the trigger opportunity is supplied automatically by normal turn progression while the permanent remains.

This makes it a useful contrast to Card Engines: recurring Card Advantage does not automatically imply Engine.

## 6.2 Rhystic Study

Rhystic Study is a Card Advantage source and a strong positive anchor for **Card Engine**.

Its operation depends on an outside event — opponents casting spells — and an opponent may prevent an individual draw by paying the required mana. Nevertheless, opponent spellcasting is an ambient and repeatedly occurring game action rather than a prerequisite board state the controller must rebuild for each trigger.

Additional opponent spell casts create additional opportunities. One trigger does not intrinsically impair the Study's ability to process the next qualifying event.

Therefore its conditionality should be represented through coordinates such as opponent-event dependency and opponent-choice gating, not by removing Card Advantage membership or minting a separate `Potential Card Advantage` class.

## 6.3 Sram, Senior Edificer

Sram is a positive Card Engine anchor.

Its card output depends on qualifying casts, but additional qualifying spells can continue to generate additional draws without a once-per-turn or phase-based ceiling imposed by Sram itself. The available input supply, not Sram's own throughput limit, is the principal cap.

## 6.4 Chivalric Alliance

Chivalric Alliance is an important negative/boundary anchor for **Engine**.

Its draw requires a recurring qualifying board state and a game-window-specific action: attacking with two or more creatures.

The key issue is not merely that attacking might be strategically undesirable. The deeper mechanical problem is that satisfying the draw condition exposes the very creatures required for future eligibility to combat. A creature can die in that combat, leaving the controller unable to meet the two-attacker requirement on the next turn unless the prerequisite state is rebuilt.

In addition, normal turn structure ordinarily gives a bounded number of combat opportunities. Merely supplying more creatures during the same ordinary combat does not let Chivalric Alliance process them into additional draws.

Extra-combat effects can increase its output, but that additional throughput comes from another effect changing the opportunity structure. Chivalric Alliance does not intrinsically supply unbounded or input-scalable processing capacity.

Current Captain direction:

- **Card Engine:** NO under the working Engine model.
- **Card Advantage:** still requires final hard-predicate adjudication; its separate token-producing activated ability is relevant independent residual utility.

---

# 7. Engine

## 7.1 Status

**CAPTAIN-APPROVED WORKING CONCEPT — validation pending.**

Engine should exist independently of Card Advantage. A card may be an Engine even when its output is not cards.

## 7.2 Working definition

> **Engine** — a reusable game mechanism whose throughput can scale with additional qualifying inputs/events without an intrinsic per-turn, per-phase, per-step, or equivalent opportunity ceiling imposed by that mechanism, and whose operation leaves the mechanism capable of processing subsequent qualifying inputs unless an explicit input or outside effect removes it.

The important idea is that **input supply may be finite without the processor itself being rate-capped**.

## 7.3 Required mechanical questions

For candidate Engine effects, Foundry should preserve facts such as:

- `input_required` — whether an outside object/event/resource is needed;
- `input_consumed` — whether operation consumes that input;
- `intrinsic_throughput_cap` — whether the mechanism itself imposes a per-turn/per-phase/per-event ceiling;
- `opportunity_window` — whether operation is restricted to a particular phase/step/timing structure;
- `immediately_reusable` — whether the mechanism can process another qualifying input immediately after one operation;
- `future_eligibility_effect` — whether using it preserves, degrades, or destroys the state required for later operation.

These are semantic coordinates, not automatically named subclasses.

---

# 8. Carrion Feeder: Engine anchor and the difference between consuming fuel and degrading the engine

Carrion Feeder is a strong positive **Engine** anchor even though it is not a Card Engine.

Its sacrifice ability needs another creature as input and consumes that creature, but the act of processing one creature does not intrinsically reduce Carrion Feeder's ability to process the next creature.

Working characterization:

- input: creature;
- input consumed: yes;
- intrinsic throughput cap: none from a once-per-turn/phase restriction;
- immediately reusable: yes;
- processor remains available after each operation: yes.

This establishes an important distinction:

> **Consuming fuel is not the same as degrading processing capacity.**

Carrion Feeder may run out of creatures, but that is an input-supply limit. The card itself does not impose a roof on how many supplied creatures it can process through the sacrifice ability.

This is why Carrion Feeder is more engine-like and more loop-enabling than Chivalric Alliance even though both require creature-related external state.

---

# 9. Card Engine

## 9.1 Working relationship

> **Card Engine** — an Engine whose relevant scalable output is usable card-resource access.

Card Engine should therefore be derived from the broader Engine concept rather than independently defined as `a permanent that repeatedly draws cards`.

Positive working anchors:

- Rhystic Study;
- Sram, Senior Edificer.

Negative/boundary working anchors:

- Phyrexian Arena — recurring autonomous Card Advantage, but intrinsically upkeep-scheduled rather than an input-scalable processor;
- Chivalric Alliance — recurring draw potential, but opportunity/board-state constrained and not intrinsically input-scalable under ordinary turn structure.

---

# 10. Stored capacity

## 10.1 Status

**WORKING COORDINATE / MECHANICAL PATTERN — do not yet canonize as a named trunk.**

Some cards convert a setup condition or resource into a finite internal reserve and then discharge that reserve over time or through later abilities.

This should not automatically be treated as Engine behavior.

Working pattern:

> `setup input/state -> convert to stored internal capacity -> later spend/discharge finite capacity`

The defining contrast with an Engine is that new qualifying inputs during operation do not necessarily increase the already-established processing capacity.

Stored-capacity mechanics can apply beyond card draw, including mana storage, charge/counter resources, or ability escalation. The broader family still requires corpus validation before deciding whether it deserves a canonical noun or only shared coordinates.

---

# 11. Dawn of a New Age: stored-capacity anchor

Dawn of a New Age is the primary working anchor distinguishing **stored capacity** from **Engine**.

Its setup cares about how many creatures the controller has when it enters and converts that state into hope counters. Later end steps discharge that finite counter reserve to produce draws.

Once the counters are established, the original creatures do not need to survive for the stored draws to continue. Conversely, playing additional creatures later does not add new hope counters through Dawn's normal operation.

Therefore:

- **Engine:** NO under the working definition;
- setup dependency: yes;
- continuing creature dependency after setup: no;
- internal stored capacity: yes;
- output schedule: end-step gated;
- capacity finite from establishment;
- additional later qualifying inputs do not intrinsically increase capacity.

This can be summarized as:

> **Dawn is charged by setup, then discharges a finite reserve. It does not continue accepting new fuel as an Engine would.**

For Card Advantage accounting, the number of stored draws can determine eventual realized output if the permanent survives long enough, but Engine classification remains separate from total possible value.

---

# 12. Current boundaries and non-decisions

The following are intentionally **not frozen**:

1. the complete hard predicate for Card Advantage;
2. the final Card Advantage classification of Chivalric Alliance;
3. the exact implementation predicate for Engine / Card Engine;
4. whether `stored capacity` deserves a canonical named concept or remains a bundle of coordinates;
5. exact treatment of timing restrictions that are not simple once-per-turn caps;
6. interactions where an Engine has a resource cost that can itself be replenished indefinitely;
7. corpus-wide thresholds for what counts as sufficiently ambient/naturally recurring for Card Advantage membership.

Before S16B freeze, adversarial testing should include at minimum:

- a cumulative-upkeep or self-expiring source;
- a charge-counter / mana-storage permanent;
- an Engine with a mana cost but no tap/turn restriction;
- a `once each turn` processor;
- a processor that sacrifices itself after N uses;
- an effect whose input supply is renewable but whose processing window is phase-gated;
- an effect where using the mechanism directly replenishes its own next input.

The purpose of that pass is to test the semantic boundaries, not to reopen the core distinctions without evidence.

---

# 13. Control boundary

This addendum preserves semantic decisions only. It does **not** authorize:

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
