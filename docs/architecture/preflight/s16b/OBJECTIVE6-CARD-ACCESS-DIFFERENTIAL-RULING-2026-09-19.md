# Objective 6 — Card Access Differential Working Metric

**Date:** 2026-09-19  
**Status:** CAPTAIN-APPROVED WORKING METRIC — naming and whole-vocabulary validation still pending.  
**Authority boundary:** This is a semantic decision record only. It does not freeze S16B, accept implementation, merge PR #70, move the accepted implementation head, resume AQ4, activate Bridge v0, authorize Step6, or move `main`.

## Captain direction

Foundry should distinguish **Card Resource Differential** from a separate **Card Access Differential** metric.

The reason is that a player can gain permission to use additional card-origin resources without those cards ever moving into hand or becoming newly owned card resources.

A canonical example is continuous top-library permission. If a permanent lets its controller play or cast the current top card of their library, that player has access to an additional card-origin resource beyond the cards in hand. Even with an empty hand, the currently eligible top card may remain usable.

## Working distinction

- **Card Resource Differential** measures changes in card-origin resources gained, lost, preserved, recovered, or denied.
- **Card Access Differential** measures changes in the number of distinct card-origin resources the player is presently permitted to use, regardless of whether those cards entered hand.

The two metrics may overlap but are not identical.

Examples:

- drawing a card can increase both card resources and presently usable access;
- a top-library permission can increase access without increasing card-origin resource stock;
- temporary exile permission can increase access for a limited horizon without moving the card into hand;
- Enlightened Tutor can move a card to the top of the library without itself increasing present access unless another effect grants permission to use that top card.

## Top-library access

Top-library access is a primary positive anchor for Card Access Differential.

A continuous top-library effect normally creates **one additional currently exposed access slot at a time**, not an unlimited numeric advantage.

If the top card is eligible under the granted permission, the current access differential may increase by one. If the top card is not eligible, the granted permission exists but the currently usable access count may be zero from that effect.

When the top card is used and the next library card becomes the new top card, the access slot may refresh. Foundry should therefore preserve both:

- current accessible-card count; and
- whether the access is continuous / refreshable when the source position changes.

This avoids treating a continuous top-library effect as infinite card advantage while still preserving its substantial mechanical value.

## Distinct cards, not permission clauses

Card Access Differential should count distinct card-origin resources presently usable, not the number of redundant permission effects that point at the same card.

Two permanents that both let the controller cast the same current top card do not automatically produce +2 access. The underlying distinct accessible card count is still one unless the effects expose different additional cards or positions.

## Permission eligibility remains mechanically binding

PLAY and CAST remain distinct.

If an effect only permits `CAST`, a land on top does not become usable through that permission and should not count as presently accessible via that effect.

If an effect permits `PLAY`, a land may become usable subject to the ordinary land-play rules and any additional land-play permissions or restrictions.

Card-type, timing, ownership, payment, horizon, and other restrictions must remain coordinates on the access fact.

## Relationship to other accepted access components

Card Access Differential should consume factual access outputs from mechanisms such as:

- Top-Library Access;
- temporary exile access / impulsive draw patterns;
- alternate-zone play/cast access;
- graveyard cast/play access;
- Sequential Library Traversal when it creates usable card permissions;
- Bounded Extraction when selected cards become usable through a privileged destination or permission;
- Repeat-Use / Additional Execution where the same underlying card-origin resource receives another usable execution opportunity.

The metric must not erase the mechanism that produced the access.

## Resource-type separation

Card Access Differential is one resource dimension among several. It must not absorb:

- generated board objects;
- mana resources;
- life;
- counters/stored capacity;
- generic strategic value;
- Card Resource Differential.

The substrate should report what kind of resource or permission changed rather than flattening everything into one universal advantage score.

## Player-facing interpretation

A player-facing explanation may say that a card effectively gives the player another card they can currently use, even though it is not in hand.

For example, a continuous top-library effect can be explained as:

> You can use the eligible top card of your library as an additional available card. When that card leaves the top, the access slot can refresh to the next eligible top card.

This is an explanatory analogy, not a rules claim that the library card is literally in hand or that hand size changed.

## Audit requirements

The later whole-vocabulary audit must test at minimum:

1. whether Card Access Differential is sufficiently distinct from Card Resource Differential to justify a separate metric;
2. whether temporary exile, top-library, graveyard, and repeat-use access all fit without exception proliferation;
3. how current usability should be represented when timing, mana, land-play, or card-type restrictions make an otherwise permitted card unusable at the present moment;
4. whether continuous refreshability needs its own stable coordinate or can be derived from source-position and permission facts;
5. whether distinct-card counting behaves correctly when multiple permissions point to the same card;
6. whether the metric improves Searcher B, comparison, and substitution explanations without becoming a generic strategic-value score;
7. whether the final name passes the later cool-name audit.

## Control boundary

This ruling preserves semantic direction only. It does not authorize implementation acceptance, semantic freeze, merge, deployment, AQ4 resumption, Bridge activation, Step6, accepted-head movement, or main-branch movement.

> **PRESERVE TRUTH, NOT PLUMBING.**
