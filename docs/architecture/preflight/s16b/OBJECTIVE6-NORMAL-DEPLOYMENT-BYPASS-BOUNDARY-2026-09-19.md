# Objective 6 — Direct Placement Boundary — Freeze Candidate

**Date:** 2026-09-19  
**Former rejected working label:** `Normal Deployment Bypass` / `Deployment Bypass`  
**Status:** **SEMANTIC DISTINCTION RETAINED / PROPOSED FINAL NAME — NOT FROZEN**

## 1. Proposed final name

The global naming audit proposes **Direct Placement**.

Working meaning:

> An effect puts an eligible card/object directly into its destination zone, especially the battlefield, without casting/playing that object through the ordinary spell/land-play procedure.

The exact destination is still a coordinate; `Direct Placement` is not battlefield-only in the abstract event model, though the primary surfaced use is direct battlefield placement.

## 2. Why the distinction survives

The weird-card and whole-vocabulary audits confirm a mechanically hard boundary between:

- changing the cost/payment of a spell that is still **cast**; and
- putting the card/permanent directly onto the battlefield without that casting event.

This matters for:

- cast triggers;
- the stack;
- counterspells;
- timing/casting restrictions;
- alternative/additional costs;
- ETB effects;
- control/ownership;
- temporary cleanup.

## 3. Positive anchors

- **Elvish Piper** — card from hand directly to battlefield.
- **Reanimate** — creature card from graveyard directly to battlefield.
- **Show and Tell** — each player may place an eligible hand card directly to battlefield.
- **Sneak Attack** — creature from hand directly to battlefield plus haste/delayed sacrifice.
- **Collected Company** — Sample Selection followed by Direct Placement of selected eligible creatures.
- **Genesis Wave** — variable Sample Selection followed by Direct Placement.
- **Winota, Joiner of Forces** — Sample Selection followed by Direct Placement tapped/attacking.

## 4. Critical negative anchor

**Omniscience is not Direct Placement.**

It changes the cost of spells cast from hand. The spells are still cast, use the stack, produce cast triggers, and can interact with effects that care about casting.

Likewise, Cascade/Discover free casts use an **Alternative Cost** and remain casts.

## 5. Required coordinates

Preserve at minimum:

- source zone;
- destination zone;
- eligible object/card characteristics;
- owner/controller;
- target/selection authority;
- whether the placed object is cast/played (`false` for the Direct Placement event itself);
- timing permission/restriction;
- cost of the effect that performs placement;
- tapped/attacking/face-down/other entry state;
- temporary duration;
- delayed sacrifice/exile/return/cleanup;
- symmetrical/multiplayer scope.

## 6. Relationship to other concepts

Direct Placement may compose with:

- Tutor;
- Sample Selection;
- Graveyard Access;
- Library Traversal;
- token/object creation;
- temporary-control effects;
- Role Compression as a derived product fact.

Do not collapse those mechanisms merely because the final destination is battlefield.

## 7. Search aliases

Player language such as `cheat into play`, `cheat into battlefield`, and `put into play` may map to Direct Placement for retrieval.

Those phrases should remain aliases, not canonical mechanical names.

## 8. Control boundary

`Direct Placement` is a freeze-candidate name only. No S16B freeze, corpus reclassification, implementation acceptance, merge, accepted-head/main movement, AQ4 resumption, Bridge activation, or Step6 is authorized.

> **PRESERVE TRUTH, NOT PLUMBING.**
