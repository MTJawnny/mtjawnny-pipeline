# Objective 6 — Session Handoff: Weird-Card Research, Adversarial Audit, Naming

**Date:** 2026-09-19  
**Status:** HANDOFF / NO FREEZE  
**Repository:** `MTJawnny/mtjawnny-pipeline`  
**Working PR:** #70, draft and unmerged.  
**Branch:** `docs/foundry-product-interaction-model-2026-09-18`  
**Authority boundary:** Durable repository/GitHub state is authority. This handoff preserves current semantic direction and unresolved questions only. It does not freeze S16B, accept implementation, merge PR #70, move the accepted implementation head, resume AQ4, activate Bridge v0, authorize Step6, or move `main`.

> **PRESERVE TRUTH, NOT PLUMBING.**

## Why this handoff exists

The current conversation has accumulated enough local momentum that the next phase should begin in a fresh ChatGPT session. The next session must not preserve a concept merely because a prior ChatGPT proposed it, the Captain tentatively accepted it, or a prior semantic note described it as settled. The upcoming work is intentionally adversarial.

The Captain explicitly called out a failure mode in the current session: ChatGPT can become overly agreeable and accept additional concepts too readily. A concrete example was the temporary suggestion of a new `Card Access Differential` term, which was unnecessary because the intended facts should already be represented through existing Card Access mechanics and, where appropriate, **Card Resource Differential**. That extra term is **not accepted** and must not be introduced unless future evidence genuinely forces it.

## Current late-session semantic state that must survive the handoff

### Top-Library Access

Top-Library Access is a real surfaced tag/facet because players should be able to explicitly include or exclude it in Foundry queries and comparisons.

It applies to effects that grant permission to use the current top card of a library, such as play/cast access, subject to eligibility restrictions.

It must **not** be conflated with effects that merely interact with the top of the library.

Examples of the distinction:

- an Enlightened Tutor-style effect is **Tutor** with `destination = library_top`; it is not Top-Library Access merely because the searched card is put on top;
- a Future Sight / Mystic Forge / Oracle of Mul Daya / Bolas's Citadel-style effect is Top-Library Access because it grants permission to use the card currently occupying the top position.

Shared zone interaction does not imply shared function.

`PLAY` and `CAST` remain hard-distinct permission facts. `PLAY` may include land play where normal rules permit it; `CAST` does not.

### Top-Library Access and Card Resource Differential — unresolved accounting edge

The Captain's intended intuition is that a legally usable top card can function as an additional usable card-origin resource even though it never moved to hand. This is plausibly within **Card Resource Differential**, whose working scope concerns usable card-origin resources rather than only physical hand count.

However, the exact accounting rule is **not fully settled and must be attacked in the adversarial audit**.

Questions the audit must answer include:

1. Does a continuous top-library permission count as +1 current usable card-origin resource only when the current top card is actually eligible under the permission?
2. Does `CAST` access fail to create a usable resource when the top card is a land while `PLAY` access may still create one?
3. Does present legal permission require present ability to pay/deploy, or is legal availability sufficient for resource accounting?
4. How should continuous refresh work after the top card is played/cast? The likely direction is that refreshability/throughput is distinct from simultaneous resource count, so the effect should not be treated as unbounded or "infinite" Card Resource Differential.
5. How do we avoid double-counting the source permanent merely because it remains on the battlefield while granting access to another card-origin resource?
6. How should hidden/revealed information, restrictions, access horizon, and payment modification affect the accounting?

Do not create a new metric merely to avoid solving these questions cleanly.

### Card Filtering / Bounded Extraction candidate consolidation

Current candidate direction:

- **Card Filtering** may serve as the broader family;
- **Bounded Extraction** remains a required, independently searchable qualifier/signature rather than necessarily a peer ontology branch.

Gold-standard Bounded Extraction anchors include:

- Dig Through Time;
- Collected Company;
- Plunge into Darkness;
- Impulse and similar finite-sample selectors.

Plunge into Darkness is especially important because it demonstrates that "bounded" does not mean fixed small N. Its selection depth is variable and player-controlled through life payment.

The future audit must specifically test whether this consolidation damages retrieval or semantic similarity. It must be willing to split Bounded Extraction back out if qualifiers cannot prevent cards such as Dig Through Time from becoming misleadingly close to ordinary turnover/filtering effects such as Faithless Looting.

### High-value retrieval-substitution direction

Bounded Extraction is strategically interesting because it can provide Tutor-adjacent access without full-library determinism. This may later support users who want strong functional substitutions for Tutors while preserving greater game-to-game variation.

This strategic usefulness is a **research hypothesis**, not canonical semantic truth. Canonical Foundry should preserve factual dimensions such as:

- retrieval scope;
- selection/exposure depth;
- fixed vs variable depth;
- resource-controlled depth;
- number selected;
- eligibility/domain restriction;
- destination;
- disposition of unselected cards;
- broad-search vs finite-sample behavior;
- access horizon;
- play vs cast permission;
- ownership/provenance;
- payment modification.

### Accepted recent substrate components, all names provisional

The following structures are currently accepted as useful substrate components, but every name remains subject to the final naming/cool-name audit, including machine-facing names:

- Access Horizon;
- Alternate-Zone Play/Cast Access;
- Sequential Library Traversal;
- Repeat-Use / Additional Execution;
- Resource-Type Separation;
- Card Resource Differential;
- Top-Library Access;
- Card Filtering;
- Bounded Extraction qualifier/signature.

Resource-Type Separation means Foundry should preserve different resource kinds separately instead of flattening them into one generic value score: card-origin resources, generated board objects, mana resources, temporary access, repeat-use opportunities, life/counters/other resource facts, etc.

## Adversarial discipline for the next session

The next session must be explicitly skeptical of the current design.

For every concept, ask at minimum:

> **If this concept did not already exist, would the evidence force us to create it?**

> **If two concepts can be collapsed without losing mechanical truth, retrieval power, or player explanation, why are we keeping both?**

> **If a distinction is only useful as a qualifier/coordinate, why is it a family?**

> **If a family improves conceptual neatness but worsens Searcher B, why should it survive?**

Captain approval is evidence of direction, not protection from future correction.

The audit should specifically detect:

- noun proliferation;
- duplicate concepts under different names;
- shared-zone or shared-wording false similarity;
- hidden mechanical distinctions;
- tags that should be coordinates;
- coordinates that need to become surfaced tags because users need include/exclude control;
- context-dependent strategic claims accidentally imported into canonical mechanics;
- double-counting across Card Resource Differential, board objects, mana, and access;
- arbitrary numeric thresholds unsupported by mechanics or retrieval value;
- prior ChatGPT agreement being mistaken for evidence.

## The next three steps

### Step 1 — Weird-card research / adversarial corpus hunt

Before the global audit, deliberately search for strange cards that strain the current model.

Do not limit testing to famous, clean examples. Seek cards with unusual combinations of:

- zone changes;
- top-library use;
- opponent-owned card access;
- temporary and indefinite permissions;
- `PLAY` vs `CAST` distinctions;
- alternative payment;
- multi-player asymmetry;
- variable-depth selection;
- conditional eligibility;
- repeat casting or additional executions;
- replacement-like parity without a dedicated replacement family;
- simultaneous resource types;
- library traversal;
- unusual Tutor destinations;
- direct placement;
- copied spells/cards;
- hidden/revealed information;
- timing windows;
- unusual failure-to-find or partial-selection behavior.

The purpose is to generate evidence that can **break** the model, not to find examples that flatter it.

At minimum retain adversarial anchors already identified in prior work, including Plunge into Darkness, Dig Through Time, Collected Company, Ragavan, Etali, Primal Conqueror, Cascade, Discover, Future Sight-style cards, Mystic Forge, Oracle of Mul Daya, Bolas's Citadel, Enlightened Tutor, Underworld Breach, Eternal Witness, wheels, and flashback/rebound-like cards. Expand well beyond these.

Research may use current Oracle/rules sources and public Magic terminology/community sources where useful, but canonical claims must remain grounded in rules/Oracle-derived facts. Community strategic claims must be labeled as research/strategy rather than imported into the canonical substrate.

Produce a durable weird-card research/adversarial test artifact before advancing.

### Step 2 — Whole-vocabulary adversarial semantic audit

Using the weird-card evidence from Step 1, audit the entire Objective 6 vocabulary against itself.

For each concept decide whether it should be:

- family/trunk;
- child;
- surfaced tag/facet;
- qualifier;
- coordinate;
- primitive;
- derived accounting fact;
- keyword consequence signature;
- community alias;
- strategic-layer concept;
- OPEN/research;
- retired/collapsed.

Test definition clarity, positive anchors, near misses, cross-concept overlap, retrieval value, Searcher B behavior, explanation quality, exception pressure, corpus stability, and whether the concept can be faithfully derived from lower-level facts.

The audit is authorized to recommend structural corrections. It must not preserve prior decisions merely for continuity.

Pay special attention to:

- Card Filtering vs Bounded Extraction;
- Top-Library Access vs Tutor-with-top destination;
- Card Resource Differential with alternate-zone/top-library/repeat-use access;
- access horizon and expiration;
- generated resources vs card-origin resources;
- Sequential Library Traversal vs bounded selection vs Tutor;
- Cantrip after realignment to established Magic usage;
- Engine vs repeatable resource generation;
- any concept whose current name disguises a broader or narrower actual predicate.

Apply corrections to the candidate semantic documentation only where supported. Do not freeze S16B merely because the audit completes.

### Step 3 — Global naming / "cool-name" audit

Only after Steps 1 and 2, and after resulting structural corrections, rename the surviving vocabulary.

Do not optimize names before structural truth is stable enough to justify the effort.

The naming pass should optimize for:

- mechanical faithfulness;
- clarity;
- consistency across the vocabulary;
- player recognition;
- brevity where possible;
- avoiding collisions with formal Magic rules terms;
- avoiding misleading established community meanings;
- distinctiveness across neighboring concepts;
- names that are memorable and, where appropriate, simply sound good/cool.

Every working name is eligible for change, including machine-facing components and names previously Captain-approved as temporary terminology.

After the naming pass, produce a **freeze candidate**, not an automatic freeze. Any actual S16B freeze still requires explicit Captain authorization.

## Suggested stopping discipline

Do not blend the three steps into one agreeable rewrite.

1. First generate the weird-card evidence.
2. Then attack the semantic model with that evidence.
3. Only then name the survivors.

If Step 1 reveals a structural contradiction, record it rather than prematurely patching around it with a new noun.

If Step 2 shows a current Captain-approved concept should be collapsed or split, present the evidence plainly.

The next session should prefer fewer, stronger concepts plus rich qualifiers/coordinates over ontology growth for its own sake — but should surface a tag when users genuinely need to include/exclude that mechanical pattern in queries.

## Standing controls

Unless newer durable GitHub state explicitly supersedes them:

- S15 remains CLOSED;
- S16B is not frozen;
- AQ4 remains paused;
- Bridge v0 remains parked/unused;
- Step6 remains NO;
- merge remains NO;
- main move remains NO;
- PR #70 remains documentation-only, draft, and unmerged.

Any state drift must be investigated from durable GitHub truth before continuing.
