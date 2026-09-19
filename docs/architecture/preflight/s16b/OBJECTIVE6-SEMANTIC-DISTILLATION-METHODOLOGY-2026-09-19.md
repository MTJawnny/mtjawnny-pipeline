# Objective 6 — Semantic Distillation Methodology

**Date:** 2026-09-19  
**Status:** **CAPTAIN-DIRECTED S16B METHODOLOGY — NOT A FREEZE OR CORPUS EXECUTION AUTHORIZATION**

## 1. Goal

Objective 6 is not trying to preserve every community term as a first-class ontology node.

The goal is:

> **Take useful Magic concepts — including community-derived concepts such as Edict, Burn, Ramp, Card Advantage, and similar gameplay language — and distill them as simply as possible into Foundry's semantic foundation.**

The preferred semantic foundation consists of reusable mechanical primitives, event/output signatures, hard functional predicates, qualifiers/coordinates, dependencies, and retrieval-relevant lower-level patterns.

A community term earns canonical treatment only when its gameplay meaning can be represented cleanly and consistently under those constraints.

## 2. Simplicity is a design criterion

Foundry should not bend the semantic substrate around a familiar term merely because players commonly use that term.

Preferred outcome:

1. identify the gameplay phenomenon the term is pointing at;
2. determine whether it decomposes naturally into existing primitives/predicates/qualifiers/event signatures;
3. preserve the useful retrieval relationship;
4. create a named family only when the distinction has a stable, mechanically defensible boundary.

Examples from the current work:

- **Edict** can be preserved as retrieval-relevant semantic DNA: sacrifice-based Removal + affected-player selection + eligible set + quantity + scope, without requiring Edict to become a top-level Interaction family.
- **Burn** can be represented through Damage/Life Loss primitives plus recipient, amount, targeting, Removal/player-pressure context, and related qualifiers rather than forcing a broad Burn family.
- **Stax** was retired because the community term collapses multiple mechanically different forms of Interaction; the underlying Taxation, Permission Denial, Lockdown, Graveyard Denial, Removal, and other facts remain available.
- **Token Generation** survives as a mechanical primitive while the gameplay significance comes from the token object and its downstream functions.

The objective is not ontology completeness by vocabulary accumulation. It is semantic usefulness through clean decomposition.

## 3. Difficulty is evidence

If a proposed concept cannot be defined cleanly under the established constraints, do not keep adding exceptions merely to save the label.

Difficulty in clean definition is itself useful evidence.

A resistant concept should trigger its own bounded checking question, for example:

- Is this actually several different mechanics hidden behind one community term?
- Is this a mechanical primitive rather than a functional family?
- Is it only a retrieval alias over lower-level semantic DNA?
- Is it a strategic/deck-context concept that belongs above the canonical substrate?
- Is it a role or outcome that depends too heavily on game state to be canonical at card level?
- Does it need a dedicated research/adversarial pass before any decision?

The correct response to semantic resistance is therefore **investigation or demotion**, not increasingly elaborate special pleading.

## 4. Continue breadth-first concept work, then perform a whole-vocabulary audit

The current conversational pass should continue identifying and adjudicating major concepts and hard boundaries.

After the major concept pass, perform an explicit **whole-vocabulary semantic audit** before S16B freeze.

For every proposed concept, test at minimum:

1. **Definition:** Can the concept be stated clearly and mechanically?
2. **Positive anchors:** Do representative cards fit without caveat inflation?
3. **Negative/near-miss anchors:** Can the boundary reject superficially similar cards for a principled reason?
4. **Decomposition:** Can the same information be represented more cleanly by existing primitives, qualifiers, event signatures, or semantic DNA?
5. **Overlap:** Does membership overlap with other concepts in a meaningful way rather than merely duplicate them?
6. **Retrieval value:** Does preserving the concept improve Searcher B or deck explanation?
7. **User explanation:** Can Foundry succinctly explain why the card counts?
8. **Corpus stability:** Is the definition likely to survive broad corpus examples without a proliferation of exceptions?
9. **Community-language mapping:** If the community term is useful but ontologically messy, can it remain as an alias/search concept over cleaner underlying facts?
10. **Strategic-layer boundary:** Is the concept actually deck/game-state reasoning that should be derived later rather than asserted canonically per card?

Possible audit outcomes include:

- canonical functional family/trunk/child;
- mechanical primitive;
- qualifier/coordinate;
- event/output signature;
- retrieval-relevant semantic DNA;
- community/search alias only;
- strategic-layer concept;
- OPEN / dedicated research required;
- RETIRE from canonical vocabulary.

## 5. Research parity requirement

Ramp received a dedicated external research pass to enumerate mechanisms and adversarial boundaries. Other important concepts have not necessarily received equivalent breadth.

Before final semantic freeze, concepts that materially affect the substrate should receive whatever bounded research/audit depth is necessary to establish confidence.

In particular, **Card Advantage should receive a dedicated breadth-first research/adversarial pass comparable in spirit to the Ramp work** before its final hard predicate is accepted.

This does not mean every concept needs identical research volume. Research depth should follow semantic risk and breadth. Simple concepts that distill cleanly may require little additional work; broad or contested concepts should receive more.

## 6. Expected discovery mode

The later audit and corpus work are expected to surface community-derived concepts that were not exhaustively enumerated during the conversational design phase.

That is desirable.

When a concept such as Edict, Burn, Saboteur, Aristocrats-adjacent language, or another established gameplay term appears, the first question should be:

> **Can this be easily and faithfully distilled into the semantic foundation we already have?**

If yes, preserve the semantic relationship at the smallest useful level.

If no, do not force it. Record the ambiguity and launch the smallest bounded check needed to determine whether the concept deserves a new primitive/family, an alias, a strategic-layer treatment, or retirement.

## 7. Relationship to Keyword Consequence Distillation

This methodology complements `OBJECTIVE6-KEYWORD-CONSEQUENCE-DISTILLATION-GATE-2026-09-19.md`.

Keywords and compact rules constructs should first be expanded into their canonical gameplay consequences. Community and strategic concepts should then be evaluated against those already-distilled mechanical facts.

Conceptually:

`Comprehensive Rules / Oracle evidence`

-> `keyword consequence expansion`

-> `mechanical primitives + event/output signatures`

-> `hard functional predicates + qualifiers`

-> `community-concept distillation / retrieval DNA`

-> `whole-vocabulary adversarial audit`

-> `only then broad accepted semantic corpus assertions`

## 8. Governing heuristic

> **Prefer easy, faithful distillation over preserving terminology. If a concept fits cleanly, keep the useful distinction. If it fights the substrate, make the concept prove that it deserves additional structure.**

This heuristic is subordinate to the project-wide principle:

> **PRESERVE TRUTH, NOT PLUMBING.**

## 9. Control boundary

This document does **not** authorize:

- broad corpus classification or reclassification;
- S16B freeze;
- implementation acceptance;
- AQ4 resumption;
- Bridge v0 activation;
- Step6;
- merge;
- movement of the accepted implementation head or `main`.

It records the Captain-directed methodology for completing and auditing the Objective 6 semantic vocabulary.