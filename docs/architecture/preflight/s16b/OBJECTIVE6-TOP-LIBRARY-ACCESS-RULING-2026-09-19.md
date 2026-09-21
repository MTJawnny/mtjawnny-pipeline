# Objective 6 — Top-Library Access — Freeze-Candidate Ruling

**Date:** 2026-09-19  
**Revised:** 2026-09-20 after whole-vocabulary and naming audit  
**Status:** **SURFACED SEMANTIC FACET — FREEZE CANDIDATE, NOT FROZEN**  
**Current routing:** `OBJECTIVE6-POST-AUDIT-CURRENT-STATE-2026-09-19.md`

## 1. Structural decision

**Top-Library Access** survives the adversarial audit as a surfaced include/exclude facet.

It is not merely a hidden zone coordinate because players need to explicitly search for or exclude cards that grant permission to use the current top card of a library.

The name survives the global naming audit.

## 2. Hard boundary

Top-Library Access means an effect grants meaningful permission to **play, cast, or otherwise use the card currently occupying the top position of a library**, subject to eligibility restrictions.

The facet is permission-based, not word/zone-based.

The following do **not** qualify by themselves:

- searching a library and putting a found card on top;
- tutoring to the top of a library;
- rearranging or filtering top cards;
- revealing the top card;
- looking at the top card;
- moving a known card onto the top of a library.

Those operations may involve the same position without granting use permission.

### Critical negative anchor — Enlightened Tutor

**Enlightened Tutor is not Top-Library Access.**

Its function is Tutor with `destination = library_top`. It changes which card occupies the top position but grants no permission to use that card from the library.

Shared `library_top` involvement must therefore contribute little or no direct similarity between Tutor-to-top and top-use-permission effects.

## 3. Positive anchors

- **Future Sight** — continuous top-card use permission.
- **Mystic Forge** — restricted top-card CAST permission.
- **Oracle of Mul Daya** — top-card land PLAY permission plus additional-land-play capacity.
- **Bolas's Citadel** — top-card spell casting with an Alternative Cost using life.
- **Experimental Frenzy** — top-card permission paired with denial of ordinary hand play/cast.
- **Xanathar, Guild Kingpin** — opponent-library top-card access during a defined Permission Window.

## 4. Required underlying facts

Top-Library Access must be backed by Card Use Permission and related coordinates, including:

- `source_zone = library_top`;
- whose library is accessed;
- owner/provenance of the current top card;
- visibility/reveal state;
- `permission_action = PLAY | CAST | other explicit use`;
- eligibility restrictions;
- Permission Window;
- ordinary timing restrictions and any overrides;
- ordinary payment, Alternative Cost, Cost Reduction, or Payment Method facts;
- additional land-play allowance where relevant;
- continuous versus capped access;
- whether removal of the current top card refreshes access to the new top card;
- source/link dependency where permission depends on another object.

Visibility alone is not membership.

## 5. PLAY vs CAST

The distinction is hard and must survive.

- `PLAY` can include a land play when ordinary land-play rules permit it.
- `CAST` does not permit playing a land.

A land on top under Mystic Forge may be visible but is not usable through the Forge's CAST permission. Oracle of Mul Daya's PLAY permission can cover a land subject to ordinary land-play constraints.

## 6. Card Resource Delta interaction

Top-Library Access can affect **Card Resource Delta** when it newly makes an underlying card-origin resource accessible.

Current freeze-candidate accounting rules:

1. categorical eligibility matters (`CAST` does not cover a land);
2. present mana affordability is not required for resource identity;
3. timing/land-play availability remains a separate current-actionability projection;
4. the current top position normally exposes one underlying card at a time;
5. refreshability after that card leaves is throughput/access structure, not infinite simultaneous stock;
6. merely revealing the top card creates no card-resource access;
7. Tutor-to-top creates no Top-Library Access absent a separate permission.

Do not create a separate Card Access Differential metric to handle these cases.

## 7. Relationship to neighboring structures

Top-Library Access may compose with:

- Card Use Permission;
- Permission Window;
- Draw/inspection/reveal facts;
- Card Filtering;
- Sample Selection;
- Tutor;
- Library Traversal;
- Alternative Cost / Payment Method / Cost Reduction;
- Additional Land Play;
- Permission Denial;
- Card Resource Delta.

Composition does not make these structures synonymous.

## 8. Searcher B / UI consequence

Players should be able to:

- include/exclude Top-Library Access;
- require PLAY or CAST permission;
- distinguish own-library from opponent-library access;
- restrict by eligibility;
- restrict by Permission Window;
- distinguish continuous access from resolution-only opportunities;
- distinguish top-use permission from Tutor-to-top, reveal-only, filtering, or traversal.

The broad Card Access umbrella may group these for navigation, but similarity should be driven by the harder permission/operation facts.

## 9. Remaining validation

Top-Library membership itself is considered structurally strong after the whole-vocabulary audit.

Remaining validation belongs primarily to the bounded Card Resource Delta stateful fixture set, especially:

- CAST access with a land on top;
- PLAY access with/without remaining land-play allowance;
- continuous refresh after a top card leaves;
- temporary source-dependent permission;
- opponent-owned top-card access;
- simultaneous loss of access elsewhere, as with Experimental Frenzy-like restrictions.

## 10. Control boundary

This record does not authorize:

- S16B freeze;
- broad corpus reclassification;
- implementation acceptance;
- merge;
- accepted-head/main movement;
- AQ4 resumption;
- Bridge activation;
- Step6.

> **PRESERVE TRUTH, NOT PLUMBING.**
