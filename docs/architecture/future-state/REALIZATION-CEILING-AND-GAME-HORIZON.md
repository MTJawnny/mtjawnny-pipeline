# Future State — Realization, Ceiling, and Game Horizon

**Date:** 2026-09-19  
**Status:** **CAPTAIN-DIRECTED FUTURE STRATEGIC MODEL — TABLED; NO CURRENT IMPLEMENTATION AUTHORIZATION**

## 1. Purpose

Preserve the distinction between a card's canonical mechanical capability, its theoretical ceiling, and the amount of that capability a particular deck/game is likely to realize inside the practical lifetime of a game.

This extends the probabilistic/deck-context direction in `COMPLETE-MY-DECK-PROBABILISTIC-CONTEXT.md`.

Governing distinction:

> **Opportunity is not realization. Ceiling is not expected output. Canonical capability is not contextual usefulness.**

Foundry's canonical substrate should preserve what a card can mechanically do. A later strategic layer may estimate how much of that capability is likely to matter within a specified deck, pod, format, turn horizon, and game state.

## 2. Four quantities that must remain separate

For a card or function, future analysis should distinguish at least:

1. **Canonical capability** — what the card can mechanically produce when its conditions are satisfied.
2. **Opportunity count** — how many qualifying windows/events can occur while the card is expected to be relevant.
3. **Realization probability / rate** — how often those opportunities are expected to satisfy the card's actual conditions.
4. **Realized output / expected throughput** — probability-weighted cards, mana, Treasures, damage, objects, or other value produced over the chosen horizon.

A high ceiling can coexist with low realization. A modest per-trigger effect can become strategically important when it receives many high-probability opportunities.

## 3. Game horizon must be explicit

Strategic usefulness should be evaluated inside a stated game horizon rather than as if every permanent remains in play indefinitely.

The Captain currently proposes roughly **turn 7–8 as a useful Commander working horizon** for future modeling. This is a modeling assumption to validate empirically, not canonical Magic truth and not a hard-coded constant.

Future models should allow the horizon to vary by:

- format;
- pod/game speed;
- power environment;
- play/draw position;
- turn the card is drawn;
- expected cast turn;
- expected survival duration after resolution;
- extra turns or other turn-structure effects where relevant.

The important variable is the **remaining opportunity horizon after the card becomes active**, not simply the nominal length of the game.

## 4. Explore fixture — prerequisite realization

Explore remains canonical Ramp/card-resource functionality regardless of deck composition.

Its contextual usefulness depends on whether the deck can actually satisfy the extra-land prerequisite during the window in which Explore is cast.

Useful future variables include:

- probability of having the mana to cast Explore on the relevant turn;
- probability of having already made the normal land play;
- probability of still holding another playable land;
- opening-hand land distribution;
- cards seen by the cast turn;
- mulligan policy;
- land-to-hand effects and tutors;
- draw/Card Access effects;
- other ramp that changes the relevant cast turn.

The future question is therefore not simply `Is Explore Ramp?` — canonically it is — but:

> **Given this deck and this turn horizon, how often does Explore actually convert its additional-land permission into accelerated mana development?**

## 5. Smuggler's Share fixture — repeated opportunities vs realized output

Current Oracle text for Smuggler's Share:

> At the beginning of each end step, draw a card for each opponent who drew two or more cards this turn, then create a Treasure token for each opponent who had two or more lands enter the battlefield under their control this turn.

The important structural fact is that the card receives a scheduled opportunity at **each end step**, which can produce many evaluation windows during a multiplayer game.

This creates a potentially high ceiling, especially if the permanent resolves early and survives for several turn cycles.

However, the actual output is conditional on opponent behavior/state during each specific turn.

For each end-step opportunity, future modeling should preserve at minimum:

- number of opponents in the game;
- which opponents drew two or more cards during that turn;
- which opponents had two or more lands enter during that turn;
- overlap between those opponent sets;
- whether those events arose from ordinary draw/land development or from deck-specific acceleration/card-access effects;
- whether Smuggler's Share was active for the whole relevant turn;
- whether the enchantment survives to the end step;
- expected cards drawn from the trigger;
- expected Treasures created from the trigger.

The model should therefore separate:

- **opportunity ceiling** — number of end-step trigger windows available while the card is active;
- **per-window ceiling** — maximum opponents satisfying each condition in that window;
- **realization rate** — probability/distribution of opponents actually satisfying each condition;
- **expected throughput** — total expected cards and Treasures over the remaining game horizon.

Captain hypothesis to test, not assume:

> Smuggler's Share may have a legitimately high multiplayer ceiling because it checks every end step, while its practical performance depends on whether opponents actually cross its draw/land thresholds often enough during the card's active horizon.

The future system must be willing to conclude that Smuggler's Share is excellent, mediocre, or highly environment-dependent based on measured/modelled realization. Personal preference or community reputation must not determine the result.

## 6. Controller agency should be a separate dimension

A useful strategic distinction is how much the controller can influence realization.

Examples:

- **Sram, Senior Edificer:** the controller largely supplies qualifying Aura/Equipment/Vehicle casts through deck construction and play decisions.
- **Explore:** the controller supplies the relevant deck composition/land inventory, but realization still depends on draws and timing.
- **Smuggler's Share:** much of the triggering condition is generated by opponents' draw and land-entry behavior.
- **Nest of Scarabs:** requires external -1/-1-counter events; surrounding cards must supply those inputs.

This should not become a value judgment by itself. It is a factual coordinate that helps explain variance and realization burden.

Possible future dimensions:

- controller-controlled;
- jointly controlled;
- opponent-dependent;
- ambient game-event dependent;
- low/medium/high setup burden only if those labels are derived from measurable underlying facts rather than subjective assignment.

## 7. Expected-value architecture

Conceptually, future strategic evaluation can use:

```text
canonical capability
-> activation/cast timing
-> remaining game horizon
-> opportunity windows
-> prerequisite/event probabilities
-> survival probability
-> per-opportunity output distribution
-> expected cumulative realized output
-> uncertainty / sensitivity analysis
-> plain-English explanation
```

The output should expose the drivers of the estimate rather than collapse them into a single unexplained score.

For example, a future explanation might say that a card's ceiling is high because it can trigger many times, but expected output is lower because the qualifying event is uncommon in the supplied deck/pod model. The reverse may also occur: low per-trigger output can become reliable value when the triggering event is nearly guaranteed and repeats frequently.

## 8. Strategic neutrality

This layer should test hypotheses rather than preserve player/community opinions.

Captain opinions, Manager opinions, community reputation, price, popularity, and deck inclusion rate are not substitutes for realization evidence.

If empirical/modelled results contradict the Captain's initial intuition about a card, Foundry should preserve the result.

This is an extension of the project-wide principle:

> **PRESERVE TRUTH, NOT PLUMBING.**

## 9. Control boundary

This document does not authorize:

- probabilistic implementation;
- Commander turn-horizon constants;
- strategic scoring;
- simulation infrastructure;
- recommendations;
- corpus execution;
- semantic changes;
- S16B freeze;
- merge or accepted-head/main movement;
- AQ4 / Bridge v0 / Step6 changes.

Activation requires a later bounded architecture/implementation contract and empirical calibration.