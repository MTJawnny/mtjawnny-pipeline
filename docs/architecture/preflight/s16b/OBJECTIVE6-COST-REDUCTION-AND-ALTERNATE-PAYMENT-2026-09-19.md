# Objective 6 — Cost Reduction and Alternate Payment

**Date:** 2026-09-19  
**Status:** **CAPTAIN-APPROVED SEMANTIC STRUCTURE — VALIDATION STILL REQUIRED BEFORE S16B FREEZE**  
**Scope:** Separates Cost Reduction from Ramp and from Alternate Payment / Payment Substitution. These are two distinct semantic trees because they have different rules consequences.

## 1. Captain ruling

Foundry should preserve three different mechanical ideas:

1. **Ramp** — increases the controller's usable mana or mana-producing capacity beyond ordinary resource development.
2. **Cost Reduction** — decreases the mana cost required for a qualifying spell/action.
3. **Alternate Payment / Payment Substitution** — allows another resource, object, zone resource, or game action to satisfy some portion of a mana payment without simply reducing the underlying cost in the same way as Cost Reduction.

**Cost Reduction is not Ramp.**  
**Alternate Payment / Payment Substitution is not Ramp.**  
**Cost Reduction and Alternate Payment are separate semantic trees.**

They may create similar strategic consequences — e.g. allowing a player to deploy more spells with the same amount of available mana — but Foundry should preserve the mechanically different path by which that result is achieved.

---

## 2. Cost Reduction tree

Working parent definition:

> **Cost Reduction** — a card/effect decreases the mana cost required to cast or perform a qualifying spell/action.

Positive anchors:

- **Jet Medallion** — reduces qualifying black-spell costs.
- **Goblin Electromancer** — reduces qualifying instant/sorcery spell costs.
- **Urza's Incubator** — reduces costs of creature spells of the chosen type.
- **Heartless Summoning** — reduces creature-spell costs while also imposing a separate downside.
- **Affinity** — keyword/rules mechanism that reduces generic mana cost according to its stated affinity quantity; therefore belongs under Cost Reduction rather than Alternate Payment.

Useful coordinates/facets to preserve later include:

- affected spell/action class;
- generic vs colored reduction;
- reduction amount / formula;
- conditionality;
- chosen characteristic/type/color;
- static vs temporary/one-shot;
- minimum-cost/floor rules where applicable;
- attached downside or tradeoff;
- source/dependency requirements.

Working tree:

```text
Cost Reduction
|
+-- generic cost reduction
+-- colored / symbol-specific reduction (if rules evidence supports a stable child)
+-- conditional / characteristic-bound reduction
+-- Affinity-style quantity-derived reduction
+-- other validated cost-reduction mechanisms
```

The child names above are working structural descriptions, not a frozen public taxonomy. The important Captain-approved point is the distinct **Cost Reduction parent** and its non-Ramp boundary.

---

## 3. Alternate Payment / Payment Substitution tree

Working parent definition:

> **Alternate Payment / Payment Substitution** — a card/effect permits a nonstandard resource, object, zone resource, or game action to satisfy some portion of a mana payment, rather than merely decreasing the mana cost through a Cost Reduction effect.

Current positive anchors:

- **Convoke** — creatures can be tapped as part of paying the spell's cost, with the rules determining what mana each tapped creature can pay.
- **Improvise** — artifacts can be tapped to help pay generic mana in the spell's cost.
- **Delve** — cards can be exiled from the graveyard to help pay generic mana in the spell's cost.

Working tree:

```text
Alternate Payment / Payment Substitution
|
+-- Convoke
+-- Improvise
+-- Delve
+-- other validated payment-substitution mechanisms
```

These mechanisms are not Cost Reduction merely because they can reduce the amount of mana actually spent from mana sources. The underlying rules operation is different: another resource/action is used to satisfy payment.

### 3.1 Naming remains open

`Alternate Payment` and `Payment Substitution` are both acceptable working labels for the semantic parent. The final public-facing name should be chosen during the later whole-vocabulary naming pass without reopening the approved mechanical distinction.

### 3.2 Boundary to broader alternate costs remains open

This ruling does **not yet** decide whether every Magic mechanic conventionally described as an `alternative cost` belongs inside this same parent.

Examples such as alternate casting costs, life payments, pitch spells, Evoke, Dash, or other rules packages may require their own rules-consequence review before being placed here.

Do not broaden this tree merely because ordinary language calls several different mechanisms "alternate costs."

---

## 4. Why Foundry must keep the trees distinct

The distinction supports both rules precision and retrieval/explanation.

Examples:

- **Jet Medallion:** `Cost Reduction` — the qualifying spell costs less mana.
- **Convoke:** `Alternate Payment` — creatures can help pay the spell's cost.
- **Improvise:** `Alternate Payment` — artifacts can help pay generic mana.
- **Delve:** `Alternate Payment` — graveyard cards can help pay generic mana.
- **Sol Ring:** `Ramp` — produces additional usable mana; it does not reduce or substitute the cost.

These effects can all improve effective spell-deployment capacity, but that strategic similarity must not erase the rules-level distinction.

Foundry should therefore be able to return cards as strategically adjacent while still explaining **why** their semantic mechanism differs.

---

## 5. Explicit non-Ramp rule

Neither Cost Reduction nor Alternate Payment should inflate the Ramp count merely because the card can enable a player to cast a larger spell or more spells than their raw mana production alone would permit.

Ramp remains tied to **usable mana / mana-producing capacity**.

Cost Reduction and Alternate Payment instead modify the **cost/payment side** of the transaction.

This provides a useful accounting split:

```text
mana-side change       -> Ramp
cost-size change       -> Cost Reduction
payment-method change  -> Alternate Payment / Payment Substitution
```

Cards may of course carry more than one of these functions if their actual rules text independently satisfies more than one predicate.

---

## 6. Control boundary

This document records semantic structure only. It does **not** authorize:

- S16B freeze;
- broad corpus classification/reclassification;
- implementation acceptance;
- merge;
- accepted-head or `main` movement;
- AQ4 resumption;
- Bridge v0 activation;
- Step6.

The governing project principle remains:

> **PRESERVE TRUTH, NOT PLUMBING.**
