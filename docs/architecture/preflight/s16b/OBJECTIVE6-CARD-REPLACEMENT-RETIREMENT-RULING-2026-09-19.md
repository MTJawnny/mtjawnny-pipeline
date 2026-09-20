# Objective 6 — Card Replacement Retirement Ruling

**Date:** 2026-09-19  
**Status:** **CAPTAIN-APPROVED SEMANTIC SIMPLIFICATION — VALIDATION STILL REQUIRED BEFORE S16B FREEZE**  
**Scope:** Retires `Card Replacement` as a canonical semantic family while preserving self-replacement / card-neutrality as a derived resource-accounting fact.

## 1. Captain ruling

**Card Replacement should not remain a standalone Foundry semantic tree.**

The term describes the **accounting outcome** of an access operation rather than the mechanically meaningful way a card grants access to another card resource.

A card that expends one card resource and gains one usable card resource may be self-replacing / card-neutral, but that fact does not imply that cards producing the same parity result belong to the same semantic family.

## 2. Why the tree is retired

Mechanically different cards can all end at the same one-for-one resource result:

- Shelter — Protection + draw / Cantrip behavior;
- Regrowth — Graveyard Access / Recursion;
- Demonic Tutor — Tutor;
- Impulse — bounded-sample extraction;
- Cycling — Filtering + draw.

Grouping these under `Card Replacement` obscures the actual access mechanism.

The ontology should answer **how the card grants access**, while resource accounting separately reports the resulting card-resource delta.

## 3. Preserved derived facts

Foundry should retain mechanically grounded resource-accounting fields such as:

- card resources expended;
- card resources gained/accessed;
- source retained versus consumed;
- source and destination zones;
- access duration where relevant;
- usable card-resource delta;
- opponent-relative resource delta where Card Advantage accounting applies.

From these facts Foundry may derive and explain states such as:

- self-replacing;
- card-neutral / parity;
- positive card-resource gain;
- negative card-resource result;
- multiplayer Advantage / Parity / Disadvantage / Mixed where applicable.

## 4. UI terminology

`Card Replacement` should not be exposed as a major public branch.

Plain-language statements remain useful, especially:

> **This card replaces itself.**

`Self-replacing` is preferred to `replacement effect` language because Magic uses **replacement effect** as a formal rules term with a different meaning.

## 5. Relationship to Cantrip

Cantrip has now been realigned toward established Magic/player usage rather than the earlier narrow Foundry-specific predicate.

A Cantrip can therefore be **self-replacing** as an accounting property without requiring a separate `Card Replacement` ontology membership.

## 6. Updated Card Access implication

The public Card Access neighborhood should no longer include `Card Replacement` as a peer family.

Current major structures under active adjudication include:

- Card Advantage;
- Card Filtering;
- bounded-sample extraction / former `Card Prospecting` distinction (final name pending);
- Tutor;
- Graveyard Access and other alternate-zone access structures;
- literal draw and other lower-level access modes/patterns.

Self-replacement/parity remains a derived fact across any of these mechanisms.

## 7. Control boundary

This ruling does **not** authorize:

- S16B freeze;
- broad corpus classification/reclassification;
- implementation acceptance;
- merge;
- accepted-head or `main` movement;
- AQ4 resumption;
- Bridge v0 activation;
- Step6.

The governing principle remains:

> **PRESERVE TRUTH, NOT PLUMBING.**
