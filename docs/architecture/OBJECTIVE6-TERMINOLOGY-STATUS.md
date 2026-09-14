# Objective 6 — Terminology Status / Read Order

**Status:** NON-EXECUTING / NOT RATIFIED  
**Date:** 2026-09-14

This file exists to prevent terminology drift across the Objective 6 drafting documents.

## Read order

For **current proposed terminology and ambiguity handling**, read in this order:

1. `OBJECTIVE6-CANONICAL-TERM-REGISTRY-DRAFT.md` — latest proposed canonical names, kinds, aliases, exclusions, and explicit OPEN rulings.
2. `OBJECTIVE6-DECKBUILDING-TERMINOLOGY-CENSUS-AND-CANONICALIZATION.md` — research basis and broader terminology census.
3. `OBJECTIVE6-FUNCTIONAL-VOCABULARY-AND-DECK-HEALTH-DRAFT.md` — original architecture/product model and Captain draft directions.

## Conflict rule

None of these files is ratified semantic authority yet.

If terminology differs between them, the **latest registry is the current Manager proposal**, while any earlier Captain direction remains a Captain direction until the Captain explicitly revises it. The registry does not silently overrule Captain decisions merely by using a newer proposed name.

Known drafting-name refinements include:

- broad internal `RAMP` -> proposed explicit `DURABLE_MANA_ACCELERATION`, with **Ramp** retained as player-facing alias if Captain confirms;
- broad `MULTI_REMOVAL` -> `SELECTIVE_MULTI_REMOVAL` plus separate `MULTI_INTERACTION`;
- broad project `CANTRIP` -> established cantrip semantics represented as `SELF_REPLACING_DRAW_EFFECT`, with the broader low-cost parity concept separated;
- `IMPULSE_ACCESS` / ambiguous impulse naming -> `TEMPORARY_EXILE_ACCESS` internally; **Impulse Draw** may remain user-facing alias;
- broad internal `RECURSION` -> proposed `GRAVEYARD_ACCESS`, with exact movement/access mechanisms retained and **Recursion** treated as user-facing aggregate;
- broad `REANIMATION` -> `GRAVEYARD_TO_BATTLEFIELD` parent plus creature-specific `CREATURE_REANIMATION`;
- loose `CARD_ADVANTAGE` -> proposed explicitly scoped `PERSONAL_CARD_RESOURCE_ADVANTAGE`, with traditional relative card advantage kept separate;
- `LAND_ADD` -> proposed clearer internal `EXTRA_LAND_PLAY`;
- `Mana Rock` -> proposed exact `ARTIFACT_MANA_SOURCE` mechanical family with the familiar term retained as alias;
- `Mana Dork` -> proposed exact `CREATURE_MANA_SOURCE` family with slang handled as alias/narrower child only if explicitly ratified.

## Freeze law

Objective 6 terminology is **not frozen** while a v1 term remains `OPEN` in the canonical registry.

Before execution, every v1 term must have either:

- a Captain-ratified deterministic contract plus adversarial fixtures; or
- an explicit defer/remove decision.

The working standard remains:

> One canonical concept -> one exact meaning -> explicit context -> explicit exclusions -> explicit facets -> explicit provenance -> reproducible membership.
