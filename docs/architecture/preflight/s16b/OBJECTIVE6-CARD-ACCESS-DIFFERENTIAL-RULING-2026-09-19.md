# Objective 6 — Card Access Differential — SUPERSEDED

**Date:** 2026-09-19  
**Status:** **SUPERSEDED / DO NOT IMPLEMENT / DO NOT TREAT AS SEMANTIC AUTHORITY**  
**Superseded by:** later Captain correction on Issue #1, the Objective 6 weird-card handoff, and the whole-vocabulary adversarial audit.

## 1. Correction

The earlier version of this file proposed a separate **Card Access Differential** metric.

That proposal was explicitly rejected by the Captain later in the same Objective 6 session.

> **Do not create a separate Card Access Differential metric or ontology concept.**

The intended existing accounting concept is **Card Resource Differential**, itself now classified by the whole-vocabulary audit as a **derived accounting fact** over harder underlying resource/access facts rather than a semantic family.

The previous content remains recoverable from Git history. It is not live semantic direction.

## 2. Facts that survive the rejected proposal

The rejected extra metric surfaced several useful mechanical facts. Those facts remain valid and should be represented without another noun:

- an effect may grant permission to use a card-origin resource without moving it into hand;
- Top-Library Access may expose one current underlying top card at a time;
- a continuous top permission can refresh to a new top card after the old top leaves;
- multiple redundant permissions pointing at the same underlying card do not create multiple card-origin resources;
- `PLAY` and `CAST` are different permissions;
- card type, source zone, provenance, permission duration, timing, and payment handling remain relevant coordinates;
- temporary exile, graveyard, top-library, and other alternate-zone permissions should preserve exact source/permission facts;
- another execution opportunity for the same card and a spell/card copy are not additional underlying card-origin resources.

These belong in permission assertions, resource identity, duration, execution/copy signatures, and the derived Card Resource Differential calculation.

## 3. Top-Library Access relationship

Top-Library Access remains a surfaced include/exclude facet.

When it grants access to an otherwise inaccessible underlying card-origin resource, that fact may affect a derived Card Resource Differential calculation under the relevant state/context.

Important boundaries:

- `CAST` permission does not make a land castable;
- `PLAY` may cover a land subject to normal land-play rules;
- present ability to pay a spell's cost is a realization/actionability fact, not the identity of the card resource itself;
- the top position normally exposes one underlying card at a time;
- refreshability is throughput/access structure, not permission to count an unbounded number of simultaneous resources;
- a Tutor that merely puts a card on top does not grant Top-Library Access.

## 4. No replacement metric

This correction is deliberately reductive.

Do **not** replace `Card Access Differential` with another synonymous metric such as:

- Accessible Card Differential;
- Permission Differential;
- Card Availability Differential;
- Virtual Hand Size;
- or another new headline metric.

If a future UI benefits from a `currently actionable` or similar projection, derive it transparently from existing permission/timing/payment facts after separate validation. Do not turn that projection into new canonical ontology merely to avoid a hard accounting question.

## 5. Control boundary

This supersession does **not** freeze S16B or authorize implementation, corpus reclassification, merge, accepted-head/main movement, AQ4 resumption, Bridge activation, or Step6.

> **PRESERVE TRUTH, NOT PLUMBING.**
