# Objective 6 — Top-Library Access Ruling

**Date:** 2026-09-19  
**Status:** CAPTAIN-APPROVED SEMANTIC TAG/FACET — naming and final whole-vocabulary validation still pending.  
**Authority boundary:** This is a semantic decision record only. It does not freeze S16B, accept implementation, merge PR #70, move the accepted implementation head, resume AQ4, activate Bridge v0, authorize Step6, or move `main`.

## Captain decision

**Top-Library Access** is a real surfaced semantic tag/facet in Foundry.

It must not exist only as a hidden low-level coordinate.

Primary product reason: players should be able to explicitly **include or exclude** cards that grant access to the top of a library in search, Thesaurus, Explorer, Deck Workspace, and later substitution/recommendation workflows.

The current name is provisional and must be reconsidered during the later cool-name audit, even if the concept remains machine-facing or tag-facing rather than a top-level public tree.

## Hard boundary

Top-Library Access means that an effect grants meaningful permission to **use, play, cast, or otherwise directly deploy the current top card of a library** while it remains the top card or top-position candidate.

The tag is about **ongoing or conditional access to the current top card**, not merely about interacting with the top of the library.

The following do **not** qualify by themselves:

- searching a library and putting a found card on top;
- tutoring to the top of a library;
- rearranging or filtering top cards;
- revealing the top card;
- looking at the top card;
- moving a known card onto the top of the library.

Those operations may overlap with Tutor, Card Filtering, library inspection/visibility, or destination coordinates, but they are not Top-Library Access unless the effect also grants permission to use the top card.

### Critical negative anchor — Enlightened Tutor

**Enlightened Tutor is not Top-Library Access.**

Its relevant function is targeted library retrieval with `destination = library_top`. The fact that the retrieved card becomes the top card does not grant permission to play or cast that card from the library.

Therefore Foundry must not treat `Tutor -> library top` as semantically equivalent or near-equivalent to continuous top-library access.

### Positive contrast

An effect of the form "keep/reveal the top card of your library; if it is an eligible card, you may cast/play it" is Top-Library Access because it grants direct permission to use the current top card from the library.

The reveal component is only a visibility fact. The **permission** is what makes it Top-Library Access.

## Canonical anchors

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
- `permission = PLAY` versus `permission = CAST` versus other direct deployment permission;
- card-type or other eligibility restrictions;
- ordinary payment versus alternate/modified payment;
- access horizon / duration;
- continuous versus capped access;
- whether changing the top card refreshes access to a new candidate;
- any additional land-play permission or other deployment constraints;
- ownership/provenance of the accessible card.

Visibility alone is not sufficient for membership. `look` / `reveal` without use permission belongs in separate inspection/visibility facts.

## Important distinction: PLAY vs CAST

Foundry must preserve `PLAY` and `CAST` as distinct permissions.

`PLAY` may permit a land to be played when normal land-play rules allow it. `CAST` does not permit land play.

This is the same hard distinction already accepted for alternate-zone access generally and must remain visible for top-library access as well.

## Relationship to Tutor

Tutor and Top-Library Access are wholly different mechanisms even when a Tutor's destination is the top of the library.

- **Tutor** changes which card occupies or reaches a destination by searching a broader library domain.
- **Top-Library Access** changes what the player is allowed to do with the card that currently occupies the top position.

A card may theoretically contain both mechanisms, but neither implies the other.

Similarity and substitution systems must not infer strong functional equivalence merely from shared `library_top` coordinates.

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
7. Tutor-to-top cards such as Enlightened Tutor do not receive Top-Library Access absent an actual use permission;
8. reveal/look-only effects do not receive the tag absent an actual use permission;
9. similarity ranking does not over-weight the shared `library_top` location across otherwise unrelated mechanisms;
10. the chosen final name is clear, concise, player-recognizable, and passes the cool-name audit.

## Control boundary

This ruling preserves semantic direction only. It does not authorize implementation acceptance, semantic freeze, merge, deployment, AQ4 resumption, Bridge activation, Step6, accepted-head movement, or main-branch movement.

> **PRESERVE TRUTH, NOT PLUMBING.**
