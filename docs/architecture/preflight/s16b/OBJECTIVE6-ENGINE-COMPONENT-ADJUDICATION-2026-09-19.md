# Objective 6 — Engine Component Adjudication

**Date:** 2026-09-19  
**Status:** **CAPTAIN-APPROVED ENGINE REFINEMENT — VALIDATION STILL REQUIRED BEFORE S16B FREEZE**  
**Scope:** Resolves the previously open Nest of Scarabs adversarial case and distinguishes an Engine from a card that merely participates in a larger engine/combo assembly.

## 1. Captain adjudication

**Nest of Scarabs is NOT an Engine.**

Its relevant Oracle structure can convert one qualifying counter-placement event into a scalable number of creature tokens (`that many`), but scalable **output magnitude** from one trigger does not by itself establish Engine membership.

Nest of Scarabs is better understood as an **engine component / combo component** when placed inside a larger interaction structure that repeatedly supplies and recycles the relevant inputs/events.

The card may participate in Rube-Goldberg-style loops or infinite-combo assemblies when combined with other cards, but those external cards are what provide the reusable processing cycle. The presence of a possible loop around Nest of Scarabs does not make Nest itself the engine.

## 2. Refinement to the Engine predicate

Engine analysis must distinguish at least three ideas:

1. **Scalable output magnitude** — one trigger/event can create a larger output when its input quantity is larger.
2. **Reusable processor throughput** — the card's own mechanism can repeatedly accept additional qualifying inputs/events and produce corresponding outputs without requiring an externally assembled feedback system to recreate the processing cycle.
3. **Combo/engine participation** — the card can serve as one component in a multi-card system whose combined interactions create repeated or infinite processing.

Only the second property is direct evidence of parent **Engine** membership.

Therefore:

> **A card does not become an Engine merely because one of its outputs scales, or because other cards can wrap that effect inside a repeatable/infinite loop. The reusable processing structure must belong meaningfully to the card's own mechanism.**

## 3. Nest of Scarabs as boundary anchor

Nest of Scarabs:

- sees a qualifying event involving one or more -1/-1 counters being put on a creature;
- creates a number of Insect tokens equal to the number of counters involved;
- therefore preserves input quantity in **output magnitude** even though the trigger uses `one or more`;
- does not, by that fact alone, supply the recurring event source, feedback path, or independent processing loop required for Engine membership;
- may become extremely powerful or infinite when combined with other cards that repeatedly create and recycle the relevant counter/death/token events.

Current result:

- **Engine:** NO.
- **Token Generation:** YES.
- **Triggered/event-responsive token production:** YES.
- **Scalable output magnitude:** YES.
- **Engine/combo component:** potentially YES in contextual relationship analysis, but this is not presently promoted to a standalone canonical semantic family.

## 4. Engine component should not automatically become a public ontology noun

`Engine component` is useful descriptive language for a card whose mechanics are often consumed by a larger repeated-processing assembly, but current direction is **not** to create a new canonical top-level family merely from that phrase.

If Foundry later models combo/assembly relationships, it may preserve facts such as:

- what event/resource the card consumes;
- what event/resource it produces;
- whether its output can feed another card's input;
- whether another card can feed its own input back to it;
- whether the assembled graph is finite, repeatable, or infinite;
- which cards are processors, fuel sources, converters, amplifiers, or sinks inside that graph.

That future relationship model should not retroactively label every useful combo piece as an Engine.

## 5. Consequence for the earlier `one or more` question

The Nest of Scarabs case demonstrates why `one or more` cannot be treated as a simple Engine disqualifier.

`one or more` can compress **trigger count** while still preserving input quantity in **output magnitude** through wording such as `that many`.

However, output-magnitude scalability is a different property from reusable processor throughput.

The Engine test should therefore ask both:

- Does additional input increase the size/count of the output?
- Does the card's own mechanism constitute a reusable processor capable of repeatedly accepting supplied inputs/events, rather than merely responding once per externally created event?

Nest answers the first question yes and the second question no under the Captain adjudication.

## 6. Engine membership is independent of infinite-combo potential — CAPTAIN-APPROVED

Infinite-combo potential must **not** be part of the Engine membership predicate.

An infinite combo is a separate relationship/state in which a set of cards can produce an indefinitely repeatable loop or a game-winning outcome under the relevant rules and prerequisites. Whether a card participates in such a loop does not make it more or less of an Engine.

The semantic questions are separate:

- **Engine:** does this card provide a reusable processing mechanism that repeatedly advances resources, actions, or game state when supplied with ordinary qualifying inputs?
- **Combo component:** can this card participate in a multi-card interaction loop?
- **Infinite / deterministic win line:** can an assembled interaction repeat indefinitely or otherwise produce a game-winning state?

An Engine is therefore better understood as **infrastructure that helps drive a game plan forward**, not as a synonym for a win condition.

Positive contrast:

- **Sram, Senior Edificer** can be a Card Engine because ordinary qualifying inputs — casting Auras, Equipment, and Vehicles — repeatedly produce card-resource output. Sram need not form an infinite loop and need not win the game directly.
- **Nest of Scarabs** can be a powerful combo component and may participate in infinite creature/death-trigger assemblies, but that win-line potential does not establish Engine membership.

Accordingly:

> **Never use “can go infinite,” “participates in an infinite combo,” or “forms a game-winning loop” as positive evidence for Engine membership. Engine semantics measure reusable value-processing structure; combo/win-condition semantics are separate.**

This also means a card may be:

- an Engine with no known infinite combo;
- both an Engine and a combo component;
- a combo component but not an Engine;
- neither.

## 7. Control boundary

This document records a semantic refinement only. It does **not** authorize:

- S16B freeze;
- broad corpus classification/reclassification;
- implementation acceptance;
- merge;
- accepted-head or `main` movement;
- AQ4 resumption;
- Bridge v0 activation;
- Step6.

The governing project principle remains:

> **PRESERVE TRUTH, NOT PLUMBING.**
