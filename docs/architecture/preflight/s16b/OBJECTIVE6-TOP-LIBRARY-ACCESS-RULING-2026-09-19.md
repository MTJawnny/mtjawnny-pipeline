# Objective 6 — Top-Library Access Ruling

**Date:** 2026-09-19  
**Status:** CAPTAIN-APPROVED SEMANTIC TAG/FACET — naming and final whole-vocabulary validation still pending.  
**Authority boundary:** This is a semantic decision record only. It does not freeze S16B, accept implementation, merge PR #70, move the accepted implementation head, resume AQ4, activate Bridge v0, authorize Step6, or move `main`.

## Captain decision

**Top-Library Access** is a real surfaced semantic tag/facet in Foundry.

It must not exist only as a hidden low-level coordinate.

Primary product reason: players should be able to explicitly **include or exclude** cards that grant access to the top of a library in search, Thesaurus, Explorer, Deck Workspace, and later substitution/recommendation workflows.

The current name is provisional and must be reconsidered during the later cool-name audit, even if the concept remains machine-facing or tag-facing rather than a top-level public tree.

## Core mechanical idea

A card qualifies when its rules text grants meaningful access to the current top card or top position of a library through a permission or usable-information mechanism that is materially distinct from simply drawing that card.

Canonical anchors include effects such as:

- **Future Sight**-style continuous permission to play from the top of the controller's library;
- **Mystic Forge**-style restricted top-library casting access;
- **Oracle of Mul Daya**-style top-library land-play access;
- **Bolas's Citadel**-style top-library casting access with alternate life payment.

## Required mechanical coordinates

Top-Library Access must preserve at least:

- `source_zone = library_top`;
- whose library is being accessed;
- visibility/reveal state;
- `permission = PLAY` versus `permission = CAST` versus look/reveal-only information;
- card-type or other eligibility restrictions;
- ordinary payment versus alternate/modified payment;
- access horizon / duration;
- continuous versus capped access;
- whether changing the top card refreshes access to a new candidate;
- any additional land-play permission or other deployment constraints;
- ownership/provenance of the accessible card.

## Important distinction: PLAY vs CAST

Foundry must preserve `PLAY` and `CAST` as distinct permissions.

`PLAY` may permit a land to be played when normal land-play rules allow it. `CAST` does not permit land play.

This is the same hard distinction already accepted for alternate-zone access generally and must remain visible for top-library access as well.

## Relationship to Card Access

Top-Library Access belongs under the broader Card Access navigation/semantic umbrella, but it is primarily a surfaced tag/facet rather than necessarily a large standalone ontology branch.

It may overlap with:

- Alternate-Zone Play/Cast Access;
- Card Resource Differential accounting;
- Cost Reduction / Alternate Payment;
- additional land deployment;
- visibility/reveal information;
- Repeat-Use / Additional Execution where applicable.

The overlap is intentional. Foundry should represent the composition rather than forcing one exclusive family assignment.

## Player-facing search requirement

The concept must be queryable both positively and negatively.

Examples:

- include cards with Top-Library Access;
- exclude cards with Top-Library Access;
- require `permission = PLAY`;
- require `permission = CAST`;
- exclude land-only access;
- restrict to continuous access;
- restrict by access horizon or payment mode.

This is a factual filtering capability, not a strategic recommendation.

## Validation requirements for final audit

The later whole-vocabulary audit must confirm that:

1. Top-Library Access remains retrieval-useful as a surfaced tag;
2. it does not duplicate Alternate-Zone Access in a way that harms Searcher B;
3. PLAY versus CAST remains recoverable and visible;
4. cards with materially different restrictions remain distinguishable through coordinates;
5. the tag improves include/exclude querying without forcing noun proliferation elsewhere;
6. interaction with Card Filtering, Tutor, Bounded Extraction, Sequential Library Traversal, and Graveyard Access remains non-confusing;
7. the chosen final name is clear, concise, player-recognizable, and passes the cool-name audit.

## Control boundary

This ruling preserves semantic direction only. It does not authorize implementation acceptance, semantic freeze, merge, deployment, AQ4 resumption, Bridge activation, Step6, accepted-head movement, or main-branch movement.

> **PRESERVE TRUTH, NOT PLUMBING.**
