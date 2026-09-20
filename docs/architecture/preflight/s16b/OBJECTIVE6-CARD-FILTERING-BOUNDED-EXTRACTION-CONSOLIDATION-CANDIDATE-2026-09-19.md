# Objective 6 — Card Filtering / Bounded Extraction Consolidation Candidate

**Date:** 2026-09-19  
**Status:** Captain-approved provisional semantic consolidation; mandatory re-audit before S16B freeze.  
**Authority boundary:** This records a semantic candidate only. It does not freeze S16B, accept implementation, merge PR #70, move the accepted implementation head, resume AQ4, activate Bridge v0, authorize Step6, or move `main`.

## Decision under test

For the current working model, treat **Card Filtering** as the broader semantic family that may include both ordinary filtering and limited-sample extraction effects.

Effects such as:

- Dig Through Time;
- Collected Company;
- Plunge into Darkness;
- Impulse;

may therefore receive **Card Filtering** family membership while also carrying an explicit **Bounded Extraction** qualifier/signature.

This is a deliberate change from the earlier working direction that kept Bounded Extraction / Card Prospecting as a separate family from Card Filtering.

The change is provisional because the Captain wants the later whole-vocabulary audit to test whether this consolidation was actually beneficial.

## Why this may be the better model

The common mechanical idea is that the card improves access to useful cards by constraining or transforming the set of available options rather than performing a broad, deterministic library search.

Within that broader family, the **Bounded Extraction** qualifier preserves the materially important distinction:

> expose a finite sample from the library, then choose one or more cards from only that sample for privileged access or destination.

This lets Foundry group these cards with Card Filtering for broad retrieval while still surfacing their tutor-adjacent behavior precisely.

## Bounded Extraction must remain explicit

The consolidation is acceptable only if Bounded Extraction remains independently queryable/taggable.

Required anchors include at minimum:

- **Dig Through Time** — finite sample, choose two;
- **Collected Company** — finite sample, eligibility restricted, up to two cards, battlefield destination;
- **Plunge into Darkness** — variable finite sample chosen through life payment, choose one, remainder exiled;
- **Impulse** — finite sample, choose one, remainder repositioned.

The qualifier should support coordinates such as:

- sample / exposure depth;
- fixed versus variable depth;
- resource-controlled depth;
- selection count;
- eligibility/domain restriction;
- selected destination;
- unselected-card disposition;
- selection authority;
- retrieval determinism / search scope.

`Bounded` must not be interpreted as `small fixed N`. Plunge into Darkness is the key adversarial anchor proving that the sample may be variable and potentially deep while remaining finite and non-tutor-like.

## Tutor boundary

The intended distinction remains:

- **Tutor** — targeted retrieval from the broader qualifying contents of the library;
- **Bounded Extraction** — selection is restricted to a finite exposed sample.

This distinction is valuable even if both live under a broader Card Access / Card Filtering presentation layer.

Bounded Extraction is especially important for later substitution tools because it can preserve strong card-selection value while giving up full-library determinism. This may support players who want tutor-adjacent functionality without making every game converge on the same deterministic line.

That strategic preference is not part of the canonical predicate. Foundry should expose the factual tradeoffs; downstream strategic systems may later reason about deck-to-deck implications.

## Mandatory future audit questions

The whole-vocabulary / semantic audit must explicitly revisit this consolidation and answer:

1. **Retrieval quality:** Does putting Dig Through Time, Faithless Looting, Brainstorm, Collected Company, and Plunge into Darkness in one broader Card Filtering family improve recall without destroying precision?
2. **Similarity behavior:** Does the broader family cause mechanically dissimilar cards to rank too closely unless the Bounded Extraction qualifier is strongly weighted?
3. **Explanation quality:** Can the UI clearly explain why Faithless Looting and Dig Through Time share the broader family while still emphasizing that their operations are materially different?
4. **Searcher B utility:** Does this structure help users discover meaningful substitutes and adjacent cards, especially tutor-adjacent non-tutors?
5. **Qualifier sufficiency:** Is Bounded Extraction as a qualifier/signature enough, or does corpus behavior demonstrate that it deserves a separate family after all?
6. **Threshold risk:** Does any arbitrary minimum sample-size rule create false boundaries? The model should prefer mechanical structure over a magic-number threshold unless corpus evidence proves otherwise.
7. **Naming:** Are `Card Filtering` and `Bounded Extraction` still the best names after the final clarity/consistency/player-recognition/cool-name audit?

## Failure conditions

The consolidation should be reversed during the audit if it causes any of the following without a clean coordinate-level remedy:

- bounded-extraction cards become hard to retrieve distinctly;
- similarity ranking overweights generic filtering membership;
- user-facing explanations flatten materially different mechanisms;
- the qualifier requires extensive exceptions or bespoke patches;
- corpus classification becomes less stable or less intuitive;
- Tutor-adjacent substitution behavior becomes harder rather than easier to express.

If those failures do not occur, the broader-family-plus-qualifier model is preferred because it reduces unnecessary ontology branching while preserving the high-value mechanical distinction.

## Product note

The Captain specifically wants cards such as Dig Through Time, Collected Company, and Plunge into Darkness to be easy to surface because they can act as substantive, less deterministic alternatives to Tutors. Foundry should make this mechanical distinction visible without turning that preference into a canonical strategic judgment.

## Naming audit boundary

All names in this record, including `Card Filtering`, `Bounded Extraction`, `retrieval determinism`, and `search scope`, are provisional and subject to the later whole-system naming / cool-name audit, whether or not they remain player-facing.

## Governing principle

> **PRESERVE TRUTH, NOT PLUMBING.**
