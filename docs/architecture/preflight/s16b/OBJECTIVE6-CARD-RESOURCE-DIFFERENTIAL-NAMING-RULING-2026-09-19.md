# Objective 6 — Card Resource Differential Naming Ruling

**Date:** 2026-09-19  
**Status:** **CAPTAIN-APPROVED NAMING / SEMANTIC-SCOPE CORRECTION — FINAL NAME STILL SUBJECT TO GLOBAL NAMING AUDIT**  
**Scope:** Renames Foundry's narrower factual card-resource accounting concept from `Card Advantage` to `Card Resource Differential`, while preserving `Card Advantage` as established Magic/community theory vocabulary rather than redefining that term.

## 1. Captain ruling

Foundry should not redefine the established Magic term **Card Advantage** to mean only the narrower card-origin accounting model being developed for the canonical semantic substrate.

The Foundry-specific factual accounting concept is therefore renamed:

> **Card Resource Differential**

This name is accepted as the current working canonical term and remains eligible for reconsideration during the later whole-vocabulary naming audit.

## 2. Why the rename is necessary

Established Magic theory uses `Card Advantage` more broadly than Foundry's intended canonical measurement. Official Wizards educational material treats traditional card advantage as including two-for-ones created through several mechanisms and can, in strict technical treatments, count independently usable generated creatures such as the two Soldier tokens from Raise the Alarm or two Goblin tokens from Dragon Fodder as technical card advantage.

Foundry intentionally needs a narrower factual measurement so that token generation, mana resources, temporary objects, repeated-use capability, and other kinds of value do not all collapse into one generic `Card Advantage` label.

Therefore:

- **Card Advantage** remains community/theory vocabulary and may be explained educationally;
- **Card Resource Differential** is Foundry's precise canonical measurement of card-origin resource change.

## 3. Working meaning

> **Card Resource Differential** — the change in distinct usable card-origin resources available to a player, compared with the corresponding card-origin-resource change of one or more opponents.

The substrate should preserve the underlying resource facts rather than relying only on a headline label.

Useful fields include:

- card-origin resources expended;
- card-origin resources gained;
- card-origin resources recovered;
- card-origin resources denied/removed from each opponent;
- source retained versus expended;
- access zone;
- access duration;
- temporary versus persistent usability;
- repeat-use permissions;
- per-player resource delta;
- pairwise opponent-relative differential.

## 4. Relationship to prior Card Advantage decisions

Prior Foundry work concerning relative accounting, multiplayer pairwise vectors, retained card-origin permanents, conditional realization, and the separation of semantic capability from realized game-state output remains useful, but references to the narrower canonical Foundry metric should now be read as **Card Resource Differential** rather than an attempted redefinition of all established Magic `Card Advantage` theory.

The existing multiplayer result states remain useful working accounting outputs:

- Advantage — all opponent-relative differentials are nonnegative and at least one is positive;
- Parity — all opponent-relative differentials are zero;
- Disadvantage — all opponent-relative differentials are nonpositive and at least one is negative;
- Mixed — at least one opponent-relative differential is positive and at least one is negative.

These are accounting states, not separate semantic trees.

## 5. Generated non-card objects remain separate resources

Generated tokens and other non-card objects should not automatically be converted into units of Card Resource Differential merely because they are independently usable.

Examples:

- Dragon Fodder: source card expended; two creature tokens generated. Token/object production is recorded separately from card-origin resource accounting.
- Treasure production: mana-resource production, not card-origin resource gain.
- Food, Clue, Map, Powerstone, creature tokens, and other generated objects retain their own mechanical/resource identities.

This does not claim that traditional Magic theory is wrong to discuss such cases as technical or virtual card advantage. It means Foundry's canonical metric is intentionally narrower and more explicit.

## 6. Retained card-origin permanents

A card moved from hand to the battlefield is still the same card-origin resource rather than a newly created card resource. If it remains as a usable permanent while its ability grants access to another distinct card-origin resource, both resources may be present simultaneously.

Therefore examples such as Elvish Visionary or Eternal Witness can produce positive Card Resource Differential while generated non-card tokens do not automatically do so.

## 7. Chivalric Alliance

The earlier Captain distinction is preserved:

- Chivalric Alliance can have **conditional positive Card Resource Differential capability** when a qualifying attack produces another card while the Alliance remains a usable card-origin permanent;
- Chivalric Alliance is **not a Card Engine** under the current Engine model because its throughput is tied to discrete attack/combat opportunities and is not intrinsically input-scalable.

The actual attack condition should remain represented through hard mechanical facts rather than a named `Conditional Card Resource Differential` subclass.

## 8. Mana/payment advantage remains separate

Avoided mana/payment is not itself Card Resource Differential.

Cascade and discover are important examples:

- library traversal / privileged access may expose another card-origin resource;
- the source plus the accessed card may create positive Card Resource Differential depending on the source and resulting resource state;
- casting without paying the mana cost is separately represented as payment/mana advantage.

Do not collapse these resources into one number at the canonical semantic layer.

## 9. Strategic / virtual Card Advantage remains downstream

`Virtual Card Advantage`, card quality, blanking otherwise technically available cards, and judgments about whether a resource is strategically meaningful depend heavily on game state, deck construction, matchup, timing, and realization.

These belong in later contextual/strategic reasoning such as Complete My Deck, not in canonical Foundry truth.

## 10. Naming-audit boundary

`Card Resource Differential` is accepted now so semantic work can proceed without misusing the established term `Card Advantage`.

The later whole-vocabulary naming audit may replace it with a clearer or more player-friendly name if the underlying meaning remains unchanged.

## 11. Control boundary

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
