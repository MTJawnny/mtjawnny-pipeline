# Objective 6 — Normal Deployment Bypass Boundary

**Date:** 2026-09-19  
**Status:** **CAPTAIN-APPROVED SEMANTIC DISTINCTION — NAME DEFERRED / CURRENT LABEL REJECTED**

## 1. Captain adjudication

The semantic distinction between ordinary cost/payment modification and effects that bypass the normal cast/play procedure is approved.

The phrase **`Deployment Bypass` is NOT approved as the eventual public/canonical name**. It is retained here only as descriptive working prose until the later whole-vocabulary naming pass.

The naming pass must be allowed to replace this label without reopening the underlying mechanical distinction.

## 2. Core distinction

Some effects reduce or replace how a spell/action is paid for while preserving the ordinary cast/play transaction.

Other effects move a card/object directly to its functional destination without that ordinary transaction occurring.

These must remain separate semantic structures because they produce different rules consequences.

Working mechanical statement:

> An effect belongs to this working tree when it causes a card/object to enter its relevant game zone through a procedure that bypasses the object's ordinary cast/play transaction, rather than merely reducing or replacing the payment used during that transaction.

## 3. Positive anchors

### Elvish Piper

`{G}, {T}: You may put a creature card from your hand onto the battlefield.`

The creature is put onto the battlefield. It is not cast through the normal spell-casting procedure.

### Reanimate

A creature card moves from a graveyard directly onto the battlefield. The creature is not cast.

### Show and Tell

Eligible permanent cards are put from players' hands directly onto the battlefield. They are not cast.

### Sneak Attack

A creature card is put from hand onto the battlefield temporarily, with a delayed sacrifice consequence. The creature is not cast.

## 4. Hard near-miss: Omniscience

Omniscience allows spells to be **cast** without paying their mana costs.

Therefore it does not belong in this direct-placement tree merely because it avoids ordinary mana expenditure.

Relevant structure instead belongs on the casting/payment side:

- the spell is cast;
- cast timing/rules still apply unless separately modified;
- cast triggers can occur;
- the spell uses the stack normally;
- the payment procedure is modified rather than the cast transaction being bypassed.

This distinction is load-bearing.

## 5. Relationship to adjacent trees

This working tree is distinct from:

- **Ramp** — increases usable mana or mana-producing capacity;
- **Cost Reduction** — decreases the mana price of qualifying actions/spells;
- **Alternate Payment / Payment Substitution** — satisfies all or part of a cost through alternate resources/actions while preserving the relevant payment/casting procedure.

A card may interact strategically with the same goal — deploying expensive objects sooner — without belonging to the same semantic tree.

## 6. Important coordinates / rules consequences

Preserve at minimum:

- source zone: hand / graveyard / library / exile / other;
- destination zone;
- card/object eligibility restrictions;
- enabling cost/payment required by the effect;
- whether the object/spell is actually cast;
- whether cast triggers occur;
- whether the object enters the battlefield and therefore can cause ETB consequences;
- temporary vs persistent deployment;
- delayed sacrifice/exile/return/bounce or other cleanup;
- controller of the deployed object;
- symmetry / affected-player scope;
- timing restriction;
- whether normal timing permissions are bypassed or separately granted.

## 7. Naming direction

The Captain explicitly rejected `Deployment Bypass` as an eventual finished name.

The later naming pass should find a name that is:

- concise;
- recognizable to Magic players;
- mechanically accurate;
- stylistically consistent with names such as `Permission Denial` and `Lockdown`;
- suitable for a user-facing tree without sounding like temporary architecture jargon.

Potential community-language phrases such as `cheat into play` may be useful search aliases even if they are not chosen as the canonical tree name.

## 8. Control boundary

This document records a semantic distinction only. It does **not** authorize:

- S16B freeze;
- broad corpus classification;
- implementation acceptance;
- merge;
- accepted-head or `main` movement;
- AQ4 resumption;
- Bridge v0 activation;
- Step6.

The governing project principle remains:

> **PRESERVE TRUTH, NOT PLUMBING.**
