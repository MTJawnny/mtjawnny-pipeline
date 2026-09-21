# Objective 6 — Card Advantage Prior-Art and Adversarial Review

**Date:** 2026-09-19  
**Status:** **RESEARCH / ADVERSARIAL INPUT — NO SEMANTIC RATIFICATION**  
**Scope:** Dedicated breadth-first research pass for Card Advantage, analogous to the earlier Ramp prior-art pass. This file compares established Magic theory and Commander usage against the current Foundry Card Advantage model. It does not freeze S16B, accept implementation, or supersede Captain rulings by itself.

## 1. Research question

Card Advantage is currently one of the load-bearing Card Access concepts. The purpose of this pass is to determine:

1. whether Card Advantage should remain a semantic family/trunk or instead be treated as a derived accounting property;
2. what resource units should count in technical Card Advantage;
3. how Card Advantage should differ from Card Filtering, Card Quality, Tempo, mana/payment advantage, and later strategic evaluation;
4. how alternate-zone access, recursion, retained permanents, tokens, sweepers, discard, Cascade/Discover, and multiplayer exchanges should be represented;
5. which parts of the current Foundry model align with established Magic theory and which require explicit Captain adjudication.

## 2. External baseline

### 2.1 Established definition

Wizards/Level One uses the long-standing definition:

> Card advantage is any process by which a player effectively obtains more cards than an opponent.

The central idea is **relative resource differential**, not merely cards drawn or hand size.

This strongly supports Foundry's existing rejection of `draw = card advantage` as a definition.

### 2.2 Two-for-ones and X-for-ones

Established theory treats a two-for-one as one card/resource trading for two opposing cards/resources. This includes:

- drawing multiple cards with one card;
- forcing multiple discards;
- removing multiple opposing permanents;
- leaving behind a useful permanent while answering another card;
- board-state exchanges where one card causes multiple opposing cards to be lost.

Therefore Card Advantage is inherently **cross-mechanism**. It can arise through Draw, Removal, Hand Disruption, recursion, retained permanents, token/material creation, or other mechanisms.

### 2.3 Card quantity vs card quality

Wizards' glossary distinguishes:

- **Card Quantity** — gross number of cards/resources available;
- **Card Quality** — ability of those cards to influence the outcome.

This distinction maps well onto Foundry's architectural split:

- canonical semantic layer: measurable access/resource facts;
- later strategic/deck-context layer: whether those resources are useful, dead, redundant, or high-impact.

### 2.4 Virtual Card Advantage

Established Magic theory uses `Virtual Card Advantage` for several related but importantly different phenomena:

- blanking opposing cards;
- turning dead cards into useful cards through filtering;
- low-impact vs high-impact card quality;
- token or repeat-use effects that function like additional cards;
- flashback/aftermath-style repeat spell use.

This category is too broad for Foundry to import wholesale into canonical semantics.

The context/evaluation portions — dead cards, blanking, card quality, relevance to the current game — belong in the future strategic layer.

Mechanically deterministic portions — extra independently usable objects, repeat casting permissions, alternate-zone access — should instead be represented as hard facts.

### 2.5 Tempo and mana are separate resources

Wizards explicitly treats Tempo and Card Advantage as different resources that often trade against one another.

The same principle applies to mana/payment advantage:

- casting without paying a mana cost can preserve mana;
- that is not, by itself, Card Advantage;
- a mechanic can simultaneously produce Card Advantage and mana/payment advantage.

This validates the recent Cascade/Discover distinction.

## 3. Strong alignments with current Foundry

### 3.1 Relative accounting

Foundry's premise that Card Advantage is relative is strongly supported.

### 3.2 Multiplayer pairwise vector

Commander/cEDH community analysis explicitly notes that a one-for-one interaction is parity against the targeted opponent but leaves the caster down a card relative to uninvolved opponents.

This strongly supports Foundry's current pairwise multiplayer vector and the accepted `ADVANTAGE / PARITY / DISADVANTAGE / MIXED` accounting result.

Example:

- controller spends one card;
- targeted opponent loses one card;
- two other opponents lose nothing.

Relative to the target: parity.
Relative to each untouched opponent: controller is down one resource.

A single aggregate should not erase that vector.

### 3.3 Semantic membership vs realized accounting

The existing distinction remains useful:

- a card can contain a Card Advantage mechanism;
- actual realized Card Advantage depends on what happened in the game.

However, the dedicated research suggests the first item may be better represented as a **derived source property** rather than membership in an ontological Card Advantage tree.

### 3.4 Alternate-zone access

Established Commander usage routinely treats temporary exile access as a form of card advantage/access even when the permission lasts only until end of turn.

The duration affects realization opportunity, not whether access was granted.

This supports the recent Foundry ruling:

- track `access_duration` explicitly;
- do not use duration alone as an automatic Card Advantage yes/no switch;
- distinguish granted access from realized use.

### 3.5 Recursion and retained permanents

Established two-for-one theory treats cards that answer/recover another card while leaving a useful body behind as Card Advantage sources.

This supports Foundry anchors such as Eternal Witness and Elvish Visionary.

## 4. Major adversarial finding: Card Advantage may not be an ontology tree

Card Advantage behaves differently from mechanisms such as Tutor, Filtering, Removal, or Ramp.

Those mechanisms answer:

> **What does this card do?**

Card Advantage answers:

> **What resource differential results from what this card does?**

Examples:

- Divination: Draw mechanism -> positive card-resource delta.
- Mind Rot: Hand Disruption -> positive 1v1 relative delta.
- Wrath of God: Board Wipe -> state-dependent multi-card exchange.
- Elvish Visionary: retained creature + Draw -> positive resource delta.
- Recruiter of the Guard: retained creature + Tutor -> positive resource delta.
- Regrowth: Graveyard Access -> parity.
- Demonic Tutor: Tutor -> parity.
- Dig Through Time: bounded extraction -> positive card quantity.
- Jeska's Will: temporary exile access + mana production -> temporary card-resource access plus a separate mana advantage axis.

This strongly suggests:

> **Card Advantage should be considered as a cross-cutting derived Card Economy result rather than a sibling mechanism family.**

This is analogous to the recent retirement of `Card Replacement` as an ontology family, but Card Advantage remains far more important as a user-facing metric and deck-analysis property.

This is a research recommendation, not yet a Captain ruling.

## 5. Candidate factual substrate for Card Economy

A future hard accounting layer could preserve at least:

- controller card-resource units before/after;
- per-opponent card-resource units before/after;
- source card retained, transformed, expended, or consumed;
- cards gained to hand;
- cards lost from hand;
- card-origin permanents gained/lost;
- temporary playable access gained/lost;
- access source zone;
- access duration;
- repeat-use/casting permissions;
- generated independent objects;
- affected-player set;
- symmetry;
- quantity fixed/variable/state-dependent;
- realization state vs intrinsic capability;
- mana/payment delta separately;
- timing/opportunity structure separately.

Derived results can then include:

- advantage;
- parity;
- disadvantage;
- mixed (multiplayer);
- X-for-one realized exchange;
- self-replacement/card-neutrality.

## 6. Adversarial examples

### 6.1 Divination

One card is expended; two cards are drawn.

Working result:

- mechanism: Draw;
- raw card-resource delta: +1;
- Card Advantage: yes.

### 6.2 Opt / ordinary Cantrip

One card is expended; one card is drawn.

Working result:

- mechanism: Draw + possibly Filtering;
- raw card-resource delta: 0;
- self-replacing/parity;
- not inherently Card Advantage.

### 6.3 Faithless Looting

From hand, the spell is expended, two cards are drawn, and two cards are discarded.

Raw card quantity is negative even though card quality/access composition improves.

This is a strong anchor that Filtering and Card Advantage must remain independent.

### 6.4 Dig Through Time

One card is expended; two selected cards enter hand.

Working result:

- mechanism: bounded extraction;
- raw card-resource delta: +1;
- Card Advantage: yes.

### 6.5 Demonic Tutor

One card is expended; one card is retrieved to hand.

Working result:

- mechanism: Tutor;
- raw card-resource delta: 0;
- card quality/access precision increases;
- not technical Card Advantage merely because the selected card is better.

### 6.6 Recruiter / Eternal Witness style retained source

The source card becomes a still-usable permanent while another usable card is obtained.

Working result:

- mechanism: Tutor or Graveyard Access;
- source retained as material;
- additional card gained;
- positive Card Advantage.

### 6.7 Phyrexian Arena

The source moves from hand to battlefield without ceasing to exist as a card-origin resource. Later triggers add cards without consuming the source.

Working result:

- Card Advantage source: yes;
- Card Engine: no under the current Engine definition;
- scheduled/time-gated output is a realization coordinate, not a reason to deny Card Advantage.

### 6.8 Chivalric Alliance

The existing OPEN status should be revisited.

If its trigger resolves, the permanent remains and the controller draws a card. The attack requirement changes realization burden but does not change the factual resource delta of a successful trigger.

Research direction:

> **Chivalric Alliance should likely count as a Card Advantage source even though it is not a Card Engine.**

Its dependency/opportunity structure should be recorded separately.

### 6.9 Rhystic Study / Sram

Both remain Card Advantage sources and Card Engines under current Engine reasoning.

Opponent-choice gating or qualifying-input supply affects realization, not the existence of the card-access mechanism.

### 6.10 Temporary exile access

A card exiled with permission to play/cast becomes temporarily usable without entering hand.

The permission window is a factual duration coordinate.

A one-shot effect that spends one card to grant access to one card is approximately replacement/parity in raw access quantity.

A one-shot effect that spends one card to grant access to multiple cards can create positive temporary card-resource access.

Whether every granted card is ultimately used belongs to realized accounting.

### 6.11 Future Sight / Mystic Forge

Top-library play/cast permission increases usable card access without drawing.

This is strong evidence that the Card Advantage substrate must count **usable access**, not only hand size.

### 6.12 Cascade / Discover

These mechanics provide library traversal plus privileged use.

They also commonly include `cast without paying its mana cost`, which must be recorded separately as payment/mana advantage.

Cascade/Discover should not automatically be labeled Card Advantage solely because the found spell is cast for free.

Card Advantage depends on the source and resulting resource structure.

### 6.13 Board wipes

A board wipe can exchange one card for multiple opposing card resources, but the realized differential is board-state dependent.

Therefore Card Advantage can arise from Interaction and does not belong exclusively to Card Access mechanisms.

### 6.14 Targeted one-for-one interaction in Commander

In four-player Commander:

- caster spends one;
- target loses one;
- two other opponents lose zero.

This is pairwise parity against one opponent and negative relative position against two others.

This is a strong positive anchor for Foundry's multiplayer vector and `MIXED`/non-single-number design.

### 6.15 Force of Will style alternate costs

Exiling another card plus casting the interaction spell to answer one opposing spell creates card disadvantage in pure card quantity even if it gains substantial tempo.

This is a strong anchor for keeping Card Advantage separate from Tempo and payment efficiency.

## 7. Major unresolved boundary: what counts as one resource unit?

This is the most important open question exposed by research.

### 7.1 Current Foundry direction

Current Foundry language emphasizes **usable card-origin resources** and previously ruled that tokens/generated objects are not automatically Card Advantage merely because one card created multiple objects.

### 7.2 Established theory conflict

Wizards' Level One explicitly treats cards such as Raise the Alarm / Dragon Fodder as technical two-for-ones because one card creates two independently usable creature objects.

Other Wizards writing calls token bodies `virtual cards` and uses them in card-advantage analysis.

This means Foundry's current card-origin restriction is **narrower than established Magic theory**.

### 7.3 Why this cannot be papered over

If only physical/card-origin resources count:

- Dragon Fodder is not Card Advantage;
- flashback/aftermath is not strict Card Advantage;
- Clue/Treasure/token-producing cards may be undercounted;
- a creature that generates an independent token body is treated differently from a creature that draws a card even when both leave two independently usable pieces of material.

If every generated object automatically counts as a full card-equivalent:

- two 1/1 tokens count identically to two large independent permanents in raw Card Advantage;
- Treasure tokens may look like cards even though they are mana resources;
- arbitrary object multiplication can inflate the metric beyond what players intuitively mean by `cards`.

Therefore Foundry likely needs to separate factual components before deciding how the headline Card Advantage metric consumes them.

Candidate factual components:

- `card_origin_resource_delta`;
- `independent_object_delta`;
- `repeat_use_access_delta`;
- `temporary_access_delta`;
- object type/function;
- whether object is independently actionable;
- whether object is consumable;
- whether object represents mana rather than spell/card access.

Do not settle this boundary by importing `virtual card advantage` as a catch-all.

## 8. Flashback / aftermath / repeated-use cards

Wizards describes flashback and aftermath as effects that can function like secretly drawing another card, but commonly frames this as **virtual card advantage**.

The mechanical truth is simpler:

- one card-origin object provides more than one spell-use opportunity;
- the second use may remain available from the graveyard;
- the additional use can be measured without judging strategic quality.

Foundry should preserve repeat-use access as a hard fact.

Whether repeat-use access is included directly in headline Card Advantage or shown as a related card-equivalent/material fact remains open pending the resource-unit ruling.

## 9. Virtual Card Advantage should remain outside canonical judgment

Do not canonically decide that a card is `dead`, `blanked`, `high impact`, `low impact`, or `more useful` merely from rules text.

These require game/deck context.

Future Complete My Deck / strategic reasoning can evaluate:

- dead draws;
- card quality;
- blanked cards;
- matchup relevance;
- probability of realizing temporary access;
- expected number of uses;
- tempo/card-advantage tradeoffs;
- value of specific generated objects.

Canonical Foundry should report the measurable ingredients.

## 10. Proposed architecture after this research

### 10.1 Mechanisms remain mechanisms

Examples:

- Draw;
- Card Filtering;
- bounded extraction;
- Tutor;
- Graveyard Access;
- Temporary Exile Access;
- Top-Library Access;
- Hand Disruption;
- Removal / Board Wipe;
- Token Generation;
- Copy;
- repeat casting/access mechanics.

### 10.2 Card Economy is derived across them

Working conceptual layer:

```text
mechanical events / access facts
        -> resource-unit accounting
        -> per-player deltas
        -> pairwise relative deltas
        -> Advantage / Parity / Disadvantage / Mixed
```

`Card Advantage source` can remain a user-facing deck metric derived from those facts without requiring `Card Advantage` to be an ontology tree.

### 10.3 Separate parallel resources

Never collapse into Card Advantage:

- mana generation;
- cost reduction;
- alternate payment/payment bypass;
- tempo;
- life;
- strategic card quality.

A card may improve several at once.

## 11. Research recommendations requiring Captain adjudication

1. **Consider retiring Card Advantage as an ontology tree while preserving it as a first-class derived Card Economy metric.**
2. **Retain multiplayer pairwise differentials and MIXED.**
3. **Resolve Chivalric Alliance as Card Advantage YES if the accounting model becomes purely factual; keep Engine NO.**
4. **Keep temporary exile duration as a coordinate, not an automatic Card Advantage switch.**
5. **Keep mana/payment advantage separate from Card Advantage for Cascade/Discover and free-cast effects.**
6. **Keep virtual/card-quality judgments in the later strategic layer.**
7. **Explicitly adjudicate the generated-object/token boundary before freezing Card Advantage.** This is the main conflict between Foundry's current card-origin approach and established Magic theory.
8. **Represent repeat-use access (flashback/aftermath/etc.) as hard mechanics even if the headline accounting treatment remains open.**

## 12. Sources reviewed

Primary Wizards sources reviewed include:

- Reid Duke, `The Basics of Card Advantage`;
- Mike Flores, `Card Advantage`;
- Mike Flores, `Card Advantage—Two-for-Ones`;
- Mike Flores, `Virtual Card Advantage`;
- Reid Duke, `Tempo & Card Advantage: A Delicate Balance`;
- Wizards `Glossary of Terms`;
- Gavin Verhey, `Doing the Aftermath`;
- Mark Rosewater, `Mechanical Color Pie 2021` and design discussions of impulsive draw.

Commander-specific adversarial comparison also reviewed current EDHREC/cEDH discussions of multiplayer one-for-one interaction and card-advantage engines.

These sources are prior art and terminology evidence, not authority over Captain semantic decisions.

## 13. Control boundary

This document is research only. It does **not** authorize:

- S16B freeze;
- corpus reclassification;
- implementation acceptance;
- merge of PR #70;
- accepted-head movement;
- `main` movement;
- AQ4 resumption;
- Bridge v0 activation;
- Step6.

The governing principle remains:

> **PRESERVE TRUTH, NOT PLUMBING.**
