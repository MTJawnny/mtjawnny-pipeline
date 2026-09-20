# Objective 6 — Card Filtering / Finite-Sample Selection — Audit Revision

**Date:** 2026-09-19  
**Status:** **AUDIT-REVISED STRUCTURE — FINAL NAMES PENDING GLOBAL NAMING AUDIT**

## 1. Audit decision

The earlier candidate asked whether `Card Filtering` could remain the broader family while `Bounded Extraction` became a required qualifier/signature.

The weird-card pass supports **part** of that consolidation and rejects part of it.

### Survives

A finite-sample-selection pattern is mechanically real and must remain independently queryable.

### Changes

`Card Filtering` is too broad to function as a strong canonical similarity family. It should be treated as a **UI/search umbrella and derived player-facing tag** over harder operation signatures.

Therefore:

> **Do not restore finite-sample selection as a peer trunk, but do not let generic Filtering membership carry strong semantic similarity either.**

The canonical substrate should store the exact operation; UI/search may group those operations under Filtering.

## 2. Finite-sample selection signature

Working structural meaning:

> A library operation exposes a finite sample whose membership is determined without searching the broader library, then one or more cards are selected from that sample for a privileged destination or use.

The sample may be:

- fixed-size;
- variable-size;
- resource-controlled;
- state-derived;
- large;
- generated repeatedly by separate triggers.

`Finite` does **not** mean `small`, and there is no 3-card minimum.

Plunge into Darkness remains the gold-standard boundary anchor: player-paid life sets an arbitrary finite sample depth.

## 3. Positive anchors

- **Impulse** — top four, one to hand.
- **Dig Through Time** — top seven, two to hand.
- **Collected Company** — top six, up to two eligible creatures to battlefield.
- **Plunge into Darkness** — variable life-controlled depth, one to hand, rest exiled.
- **Fact or Fiction** — top five, opponent partitions, controller chooses a pile.
- **Genesis Wave** — top X, any number of eligible permanents to battlefield.
- **Winota, Joiner of Forces** — repeated top-six samples, optional eligible Human directly to battlefield.
- **Gonti, Lord of Luxury / Thief of Sanity** — samples of an opponent's library with exile/cast access.

## 4. Critical negative/near-miss anchors

- **Faithless Looting** — draw/discard turnover, not finite-sample selection.
- **Index** — inspection/reorder, no privileged selected acquisition.
- **Lim-Dûl's Vault** — repeated five-card inspection windows and reorder, but no selected card gets privileged destination/use.
- **Enlightened Tutor** — broader-library search, not finite exposed sample.
- **Ad Nauseam** — sequential one-card acquisition with player-controlled continuation, better represented as ordered traversal.
- **Cascade / Discover** — ordered traversal to stopping predicate, not finite sample chosen from simultaneously exposed candidates.

## 5. Required coordinates

Store at minimum:

- source library/player;
- sample depth expression;
- fixed / variable / resource-controlled / state-derived depth;
- exposure mechanism (look/reveal/exile/other);
- selection cardinality;
- eligibility restriction;
- selection authority;
- multi-stage selection/partition where present;
- selected destination/use;
- unselected disposition;
- visibility;
- repetition/frequency;
- direct-placement or cast/play permission if the selected result uses those mechanisms.

## 6. Card Filtering umbrella

Player-facing `Card Filtering` can still group operations that improve card flow/selection such as:

- looting/rummaging;
- scry/surveil;
- cycling/self-replacement;
- Brainstorm/Index-like reorder/disposition;
- self-mill where used as a card-flow/search surface;
- finite-sample selection.

But the machine must not treat those cards as strongly equivalent merely because they share the umbrella.

Searcher B should weight the underlying operation signature far more heavily than `Filtering = yes`.

## 7. Tutor boundary

Tutor remains broader-library search/retrieval.

The decisive distinction is not merely `sample size`:

- finite-sample selection is limited to the exposed sample produced by the effect;
- Tutor searches a broader library domain for a matching card or quantity under CR search rules.

Selection authority and destination remain independent dimensions in both structures.

## 8. Naming boundary

`Bounded Extraction` and `Card Filtering` remain eligible for the global naming audit.

The structural concept that must survive naming is **finite-sample selection**. The final label should not imply hand-only extraction or a fixed/small N.

## 9. Control boundary

No S16B freeze, implementation acceptance, corpus reclassification, merge, accepted-head/main movement, AQ4 resumption, Bridge activation, or Step6 is authorized.

> **PRESERVE TRUTH, NOT PLUMBING.**
