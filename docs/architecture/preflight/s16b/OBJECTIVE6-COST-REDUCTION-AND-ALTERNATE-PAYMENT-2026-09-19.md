# Objective 6 — Cost and Payment Structure — Audit Revision

**Date:** 2026-09-19  
**Status:** **AUDIT-REVISED MECHANICAL STRUCTURE — FINAL NAMES PENDING GLOBAL NAMING AUDIT**

## 1. Structural correction

The earlier version correctly separated Ramp from cost/payment mechanics, but its `Alternate Payment / Payment Substitution` parent conflated two different Comprehensive Rules categories.

The CR requires a sharper structure:

1. **Cost modification** — changes the total cost itself, e.g. Cost Reduction.
2. **Formal alternative cost** — a cost paid instead of the spell's mana cost under CR 118.9.
3. **Additional cost** — a cost added to the cost of casting/activating.
4. **Payment method/substitution** — changes how an already-determined cost or mana symbol can be paid.

These are independent semantic facts. They should not be forced into one `Alternate Payment` tree.

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

### Positive anchor — Affinity

Affinity is cost reduction. Its rules reduce generic cost according to the relevant affinity quantity.

## 3. Formal Alternative Cost

**Structural type:** CR-grounded primitive.

Use `alternative cost` only in the Comprehensive Rules sense.

CR 118.9 defines an alternative cost as a cost paid **rather than** the spell's mana cost. `Cast ... without paying its mana cost` is an alternative cost.

Examples include:

- Omniscience-style `without paying` permission;
- Cascade/Discover free-cast permission;
- Dream Halls-style `rather than pay` structure;
- Flashback/Escape and other keywords whose CR entry establishes an alternative cost.

Preserve:

- alternative-cost expression;
- source/effect granting it;
- eligibility;
- whether value choices such as X are constrained;
- other additional costs that still must be paid;
- timing/permission restrictions.

## 4. Additional Cost

**Structural type:** primitive/coordinate.

Examples include sacrifice/discard/life or other requirements that are added to a spell/action cost.

Do not confuse an additional cost with either reduction or alternative cost.

## 5. Payment Method / Payment Substitution

**Structural type:** primitive/coordinate.

This captures cases where another resource/action satisfies an already-determined payment requirement or mana symbol.

### CR hard boundary

The current CR explicitly states:

- **Convoke — CR 702.51b:** not an additional or alternative cost; applies after total cost is determined.
- **Delve — CR 702.66b:** not an additional or alternative cost; applies after total cost is determined.
- **Improvise — CR 702.126b:** not an additional or alternative cost; applies after total cost is determined.

Therefore those mechanics must **not** be canonical children of `Alternative Cost`.

Their harder fact is how the determined cost can be paid:

- Convoke — tapping creatures can pay portions of the cost;
- Delve — exiling graveyard cards can pay generic portions;
- Improvise — tapping artifacts can pay generic portions.

K'rrik-style Phyrexian-symbol life payment similarly belongs in payment-method facts rather than being mislabeled as a generic alternative-cost tree merely because mana expenditure is avoided.

## 6. Recommended machine structure

Prefer compositional fields such as:

```text
cost_modifier:
  operation: reduce | increase | set | other
  amount_or_formula: ...

formal_alternative_cost:
  present: true | false
  expression: ...

additional_costs:
  - resource/action + quantity/expression

payment_methods:
  - requirement/symbol satisfied
  - substitute resource/action
  - conversion rate / restrictions
```

Exact storage syntax is implementation work, not ratified here. The semantic split is the important part.

## 7. Ramp boundary

Ramp remains a separate functional family because it changes usable mana or mana-producing capacity.

Cost/payment mechanics may let the player deploy more with the same mana, but that does not make them Ramp.

Useful contrast:

- Sol Ring -> mana-side change -> Ramp;
- Affinity / Jet Medallion -> cost-size change -> Cost Reduction;
- Convoke / Delve / Improvise -> payment-method change;
- Dream Halls / Omniscience free casting -> formal Alternative Cost;
- Elvish Piper / Reanimate -> Direct Placement; no spell cast for the placed permanent.

## 8. Searcher B consequence

These mechanisms may be strategically adjacent while remaining mechanically different.

Similarity may use a later shared outcome such as `reduces raw mana needed from sources`, but canonical explanation must preserve *why*:

- cost got smaller;
- another payment method satisfied it;
- an alternative cost replaced mana cost;
- or the cast transaction was bypassed entirely.

## 9. Naming boundary

The final naming pass should prefer Magic's formal `Alternative Cost` only for the CR category.

The working phrase `Payment Substitution` may be renamed if a clearer machine/player term exists, but it must not imply that Convoke/Delve/Improvise are formal alternative costs.

## 10. Control boundary

No S16B freeze, corpus reclassification, implementation acceptance, merge, accepted-head/main movement, AQ4 resumption, Bridge activation, or Step6 is authorized.

> **PRESERVE TRUTH, NOT PLUMBING.**
