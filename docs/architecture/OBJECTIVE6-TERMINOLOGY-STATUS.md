# Objective 6 — Terminology Status / Read Order

**Status:** NON-EXECUTING / NOT RATIFIED  
**Date:** 2026-09-14

This file exists to prevent terminology drift across the Objective 6 drafting documents.

## Read order

For **current proposed terminology and ambiguity handling**, read in this order:

1. `OBJECTIVE6-CANONICAL-TERM-REGISTRY-AMENDMENT-1.md` — latest adversarial corrections to specific registry terms; takes precedence for the affected wording.
2. `OBJECTIVE6-CANONICAL-TERM-REGISTRY-DRAFT.md` — proposed canonical names, semantic kinds, aliases, exclusions, and explicit OPEN rulings.
3. `OBJECTIVE6-DECKBUILDING-TERMINOLOGY-CENSUS-AND-CANONICALIZATION.md` — research basis and broader terminology census.
4. `OBJECTIVE6-FUNCTIONAL-VOCABULARY-AND-DECK-HEALTH-DRAFT.md` — original architecture/product model and Captain draft directions.

## Conflict rule

None of these files is ratified semantic authority yet.

If terminology differs between them, the **amendment plus registry is the current Manager proposal**, while any earlier Captain direction remains a Captain direction until the Captain explicitly revises it. Newer proposed naming does not silently overrule Captain decisions.

Known drafting-name refinements include:

- broad internal `RAMP` -> proposed explicit `DURABLE_MANA_ACCELERATION`, with **Ramp** retained as player-facing alias if Captain confirms; persistence belongs to the resulting mana capacity, not necessarily the originating spell/permanent;
- `LAND_ADD` -> proposed `EXTRA_LAND_PLAY`, while `LAND_FROM_HAND_TO_BATTLEFIELD` is a separate mechanism;
- `Mana Rock` -> proposed exact repeatable `ARTIFACT_MANA_SOURCE`; consumable Treasure-like sources remain separately represented;
- `Mana Dork` -> proposed exact `CREATURE_MANA_SOURCE` family with slang handled as alias/narrower child only if explicitly ratified;
- broad `MULTI_REMOVAL` -> `SELECTIVE_MULTI_REMOVAL` plus separate `MULTI_INTERACTION`;
- one-object edict/random removal -> `NONSELECTIVE_SINGLE_REMOVAL`, not Spot Removal;
- direct removal and damage/-X/-X/fight lethality -> separate direct versus state-dependent removal mechanisms;
- broad project `CANTRIP` -> established cantrip semantics represented as `SELF_REPLACING_DRAW_EFFECT`, with the broader low-cost parity concept separated;
- `IMPULSE_ACCESS` / ambiguous impulse naming -> `TEMPORARY_EXILE_ACCESS` internally; **Impulse Draw** may remain user-facing alias; bounded top-N selection is `TOP_N_SELECTION` instead;
- broad internal `RECURSION` -> proposed `GRAVEYARD_ACCESS`, with exact movement/access mechanisms retained and **Recursion** treated as user-facing aggregate;
- broad `REANIMATION` -> `GRAVEYARD_TO_BATTLEFIELD` parent plus creature-specific `CREATURE_REANIMATION`;
- loose `CARD_ADVANTAGE` -> proposed explicitly scoped `PERSONAL_CARD_RESOURCE_ADVANTAGE`, with traditional relative card advantage kept separate;
- deckbuilding **Protection** -> proposed `PROTECTIVE_EFFECT`; Magic keyword protection remains `KEYWORD_PROTECTION`; broader defensive interaction is an aggregate view;
- Mana Sink -> proposed exact `EXCESS_MANA_OUTLET`; semantic capability is separate from any recommendation that decks need a fixed quantity.

## Freeze law

Objective 6 terminology is **not frozen** while a v1 term remains `OPEN` in the canonical registry/amendment set.

Before execution, every v1 term must have either:

- a Captain-ratified deterministic contract plus adversarial fixtures; or
- an explicit defer/remove decision.

The working standard remains:

> One canonical concept -> one exact meaning -> explicit context -> explicit exclusions -> explicit facets -> explicit provenance -> reproducible membership.

When Objective 6 is eventually ratified, these draft/amendment documents should be collapsed into one clean authority rather than preserving an amendment chain as production law.
