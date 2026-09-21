# Objective 6 — Cost and Payment Structure — Freeze Candidate

**Date:** 2026-09-19  
**Revised:** 2026-09-20 after global naming audit  
**Status:** **AUDIT-REVISED MECHANICAL STRUCTURE / FREEZE-CANDIDATE NAMES — NOT FROZEN**  
**Current routing:** `OBJECTIVE6-POST-AUDIT-CURRENT-STATE-2026-09-19.md`

## 1. Structural correction

The earlier `Alternate Payment / Payment Substitution` umbrella conflated different Comprehensive Rules categories.

Keep these facts distinct:

1. **Cost Reduction** — modifies the total cost.
2. **Alternative Cost** — a cost paid instead of a spell's mana cost under CR 118.9.
3. **Additional Cost** — a cost added to casting/activation.
4. **Payment Method** — how an already-determined cost or symbol is satisfied.

The canonical `Alternate Payment` umbrella is retired.

## 2. Cost Reduction

**Structural type:** primitive / surfaced mechanical tag.

Working operation:

> decrease part of the total cost required for a qualifying spell/action.

Preserve:

- affected action/spell domain;
- generic vs colored/symbol-specific component;
- amount/formula;
- conditionality;
- characteristic/type/color dependency;
- duration;
- floors/minimums;
- attached downside/tradeoff.

**Affinity** is a clean positive anchor for cost reduction.

## 3. Alternative Cost

**Structural type:** CR-grounded primitive.

Use `Alternative Cost` only in the Comprehensive Rules sense.

CR 118.9 defines an alternative cost as a cost paid **rather than** the spell's mana cost. `Cast ... without paying its mana cost` uses an alternative cost.

Examples include:

- Omniscience-style `without paying` permission;
- Cascade / Discover free-cast permission;
- Dream Halls-style `rather than pay` structure;
- Flashback / Escape and other keyword cases whose rules define an alternative cost.

Preserve:

- alternative-cost expression;
- source/effect granting it;
- eligibility;
- X/value constraints;
- other Additional Costs that still apply;
- timing/permission restrictions.

## 4. Additional Cost

**Structural type:** CR-grounded primitive/coordinate.

Examples include sacrifice, discard, life, or other requirements added to a spell/action cost.

Do not confuse Additional Cost with Cost Reduction or Alternative Cost.

## 5. Payment Method

Former working name: `Payment Substitution`.

**Structural type:** primitive/coordinate.

This captures cases where another resource/action satisfies an already-determined payment requirement or mana symbol.

### Hard CR boundary

The current CR explicitly states:

- **Convoke — CR 702.51b:** not an additional or alternative cost; applies after total cost is determined.
- **Delve — CR 702.66b:** not an additional or alternative cost; applies after total cost is determined.
- **Improvise — CR 702.126b:** not an additional or alternative cost; applies after total cost is determined.

Therefore those mechanics must not be canonical children of Alternative Cost.

Their harder facts are payment methods:

- Convoke — tapping creatures can satisfy portions of the cost;
- Delve — exiling graveyard cards can satisfy generic portions;
- Improvise — tapping artifacts can satisfy generic portions.

K'rrik-style Phyrexian-symbol life payment likewise belongs in Payment Method facts.

## 6. Recommended machine decomposition

Illustrative semantic fields:

```text
cost_modifier:
  operation: reduce | increase | set | other
  amount_or_formula: ...

alternative_cost:
  present: true | false
  expression: ...

additional_costs:
  - resource/action + quantity/expression

payment_methods:
  - requirement/symbol satisfied
  - resource/action used
  - conversion rate / restrictions
```

Exact storage syntax remains implementation work.

## 7. Ramp boundary

Ramp remains distinct because it changes usable mana or mana-producing capacity.

Useful contrasts:

- Sol Ring -> Ramp;
- Affinity / Jet Medallion -> Cost Reduction;
- Convoke / Delve / Improvise -> Payment Method;
- Dream Halls / Omniscience -> Alternative Cost;
- Elvish Piper / Reanimate -> Direct Placement, not casting the placed permanent.

These can be strategically adjacent while remaining mechanically different.

## 8. Searcher B consequence

Similarity may recognize a shared downstream outcome such as reducing raw mana demand from mana sources, but canonical explanation must preserve **why**:

- cost became smaller;
- a different Payment Method satisfied it;
- an Alternative Cost replaced the mana cost;
- or the cast transaction was bypassed through Direct Placement.

## 9. Naming verdict

Freeze-candidate names:

- **Cost Reduction**
- **Alternative Cost**
- **Additional Cost**
- **Payment Method**

Retired canonical umbrella:

- `Alternate Payment`

Retired working name:

- `Payment Substitution`

## 10. Control boundary

No S16B freeze, corpus reclassification, implementation acceptance, merge, accepted-head/main movement, AQ4 resumption, Bridge activation, or Step6 is authorized.

> **PRESERVE TRUTH, NOT PLUMBING.**
