# Objective 6 — Card Filtering / Sample Selection — Freeze Candidate

**Date:** 2026-09-19  
**Former working names:** `Card Prospecting`, `Bounded Extraction`  
**Status:** **STRUCTURALLY AUDITED / PROPOSED FINAL NAME — NOT FROZEN**

## 1. Final candidate structure

The whole-vocabulary audit reaches this structure:

- **Card Filtering** — broad UI/search umbrella and derived player-facing tag over several harder card-flow operations;
- **Sample Selection** — independently surfaced finite-sample-selection signature;
- **Tutor** — broader-library search/retrieval family.

Generic Filtering overlap should not carry strong Searcher B similarity by itself.

## 2. Sample Selection definition

> **Sample Selection** — an effect exposes a finite sample from a library without searching the broader library, then one or more cards are selected from that sample for a privileged destination or use.

The sample may be:

- fixed-size;
- variable-size;
- resource-controlled;
- state-derived;
- large;
- repeated by separate triggers.

`Finite sample` does **not** mean a fixed or small number.

Plunge into Darkness remains the gold-standard proof: paid life sets an arbitrary finite sample depth.

## 3. Positive anchors

- Impulse — top four, one to hand.
- Dig Through Time — top seven, two to hand.
- Collected Company — top six, up to two eligible creatures to battlefield.
- Plunge into Darkness — variable life-controlled depth, one to hand, rest exiled.
- Fact or Fiction — top five, opponent partitions, controller chooses one pile.
- Genesis Wave — top X, any number of eligible permanents to battlefield.
- Winota, Joiner of Forces — repeated top-six samples, optional eligible Human to battlefield.
- Gonti / Thief of Sanity — opponent-library sample, selected card receives exile/cast access.

## 4. Critical near misses

- Faithless Looting — draw/discard turnover, not Sample Selection.
- Index — inspection/reorder without privileged selected acquisition.
- Lim-Dûl's Vault — repeated finite inspection windows, but no selected card receives privileged destination/use.
- Enlightened Tutor — broader-library search, therefore Tutor.
- Ad Nauseam — Library Traversal with player-controlled continuation.
- Cascade / Discover — Library Traversal to a stopping condition.

## 5. Required coordinates

Store at minimum:

- source library/player;
- sample depth expression;
- fixed / variable / resource-controlled / state-derived depth;
- exposure mechanism;
- selection cardinality;
- eligibility;
- selection authority;
- staged partition/choice where present;
- selected destination/use;
- unselected disposition;
- visibility;
- repetition/frequency;
- Direct Placement or Card Use Permission when selected output uses those operations.

## 6. Why `Sample Selection`

The naming audit rejects both prior labels:

### Card Prospecting

Invented metaphor. It obscures rather than clarifies the operation and risks implying a distinct strategic family.

### Bounded Extraction

`Bounded` is mathematically defensible but reads like a fixed/small-N threshold. `Extraction` suggests removing/acquiring a card into hand, which Collected Company and Genesis Wave disprove.

### Sample Selection

States the invariant directly: an exposed finite sample is produced, then cards are selected from that sample for privileged treatment.

## 7. Card Filtering umbrella

Player-facing Filtering may group:

- looting/rummaging;
- scry/surveil;
- cycling/self-replacement;
- Brainstorm/Index-like reorder/disposition;
- self-mill where used as a flow/search view;
- Sample Selection.

But the machine must compare the hard operation signatures first.

Dig Through Time and Collected Company share stronger semantic DNA with each other through Sample Selection than either shares with Faithless Looting merely because all can be called Filtering.

## 8. Tutor boundary

The distinction is not a magic numeric threshold.

- **Sample Selection:** choice is limited to the finite sample exposed by the effect.
- **Tutor:** searches a broader library domain for matching card(s) under CR search rules.

Chooser, quantity, destination, reveal, and failure-to-find behavior remain orthogonal coordinates.

## 9. Control boundary

`Sample Selection` is a freeze-candidate name only. No S16B freeze, corpus reclassification, implementation acceptance, merge, accepted-head/main movement, AQ4 resumption, Bridge activation, or Step6 is authorized.

> **PRESERVE TRUTH, NOT PLUMBING.**
