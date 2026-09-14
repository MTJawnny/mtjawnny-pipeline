# Objective 6 — Canonical Term Registry Amendment 1

**Status:** CAPTAIN REVIEW / NON-EXECUTING / NOT RATIFIED  
**Date:** 2026-09-14  
**Applies to:** `OBJECTIVE6-CANONICAL-TERM-REGISTRY-DRAFT.md`

This amendment records corrections found by adversarially rereading the registry after the second external terminology pass. It takes precedence over the specific registry language identified below, but neither document is ratified semantic authority.

---

## A1 — Durable Mana Acceleration persistence belongs to the resulting resource, not the originating card

The registry wording for `DURABLE_MANA_ACCELERATION` could be misread as requiring the spell/permanent that causes the acceleration to remain in play. That would contradict intended inclusion of effects such as Rampant Growth or Sakura-Tribe Elder.

Replace the persistence concept with:

> **`DURABLE_MANA_ACCELERATION`** — a Mana Acceleration path whose successful resolution establishes or advances mana-producing capacity that can remain available across later turns under ordinary game progression, even if the spell/permanent that created that capacity is itself expended.

Examples:

- Rampant Growth: qualifying candidate — the spell is expended, the fetched land persists.
- Sakura-Tribe Elder: qualifying candidate — the creature is sacrificed, the fetched land persists.
- Mana Rock: qualifying candidate — the mana-producing permanent persists.
- Dark Ritual: not durable — burst mana disappears as mana empties and no continuing source is established.
- Treasure used once for mana: not durable under this definition merely because the Treasure could have waited before use; the qualifying mana production consumes the source and does not establish continuing capacity.

This is the intended internal concept behind the Captain's current **Ramp = durable acceleration** direction.

---

## A2 — Mana Fixing must distinguish ordinary color production from flexible/improved color access

A basic land that produces its normal single color is a `COLOR_SOURCE`, but should not become `MANA_FIXING` merely because that color happens to be required by the deck.

Refined proposed contract:

> **`MANA_FIXING`** — a card/path broadens, converts, selects, or otherwise improves the controller's access among mana colors relative to a single fixed-color source, or deliberately acquires a source of a required color, without requiring a net increase in mana quantity.

Qualifying mechanism classes can include:

- a source capable of producing among multiple colors;
- conversion/filtering from one mana/resource color into another;
- land search that deliberately acquires an eligible required-color source;
- effects that make existing sources produce additional colors.

A fixed mono-color basic land is a `COLOR_SOURCE`, not fixing by itself.

Acceleration and fixing remain independent dimensions and may overlap.

---

## A3 — Extra Land Play and Put-a-Land effects are distinct mechanisms

`EXTRA_LAND_PLAY` only covers permission to make additional land plays. It must not absorb effects such as Growth Spiral that **put** a land from hand onto the battlefield without using the land-play action.

Add:

### `LAND_FROM_HAND_TO_BATTLEFIELD`

- **Kind:** `MECHANICAL_FAMILY`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** a path puts a land card from the controller's hand onto the battlefield without that movement itself being a normal land play.
- **Dependency:** requires an eligible land in hand.
- **Distinct from:** `EXTRA_LAND_PLAY`, `LAND_RAMP` (library -> battlefield), and ordinary land play.
- **Parent relationship to `MANA_ACCELERATION`:** remains subject to the final Mana Acceleration baseline but is mechanically represented independently regardless.

This prevents different land-development mechanisms from being conflated merely because both can result in an additional land on the battlefield.

---

## A4 — Treasure and other consumable mana objects require their own persistence facet

Do not force consumable mana objects into either Mana Rock or durable Ramp.

Add/retain the facet:

```text
mana_source_persistence:
  REPEATABLE_PERSISTENT
  CONSUMABLE_ONE_USE
  TEMPORARY_OBJECT
  ONE_SHOT_EFFECT
  OTHER
```

A Treasure token is normally:

- `MANA_SOURCE = true`;
- often `MANA_FIXING = true` because it can produce one of multiple colors;
- `mana_source_persistence = CONSUMABLE_ONE_USE`;
- not `ARTIFACT_MANA_SOURCE` if that canonical family remains restricted to repeatably usable nonland artifact sources;
- not automatically `DURABLE_MANA_ACCELERATION` merely because it can sit on the battlefield before being consumed.

Whether Treasure generation belongs to broad `MANA_ACCELERATION` is controlled by the eventual Mana Acceleration contract, not by the Mana Rock or Ramp aliases.

---

## A5 — “Protection” has three distinct meanings that must never share one primitive

The word **protection** collides among:

1. the Magic keyword ability `protection`;
2. a general deckbuilding function that preserves your resources;
3. broader defensive interaction such as taxes, pillowfort effects, generic counters, and deterrence.

Use separate concepts:

### `KEYWORD_PROTECTION`

- exact rules/keyword fact only;
- stores the protected qualities/classes as represented by S16A/CR semantics.

### `PROTECTIVE_EFFECT`

- proposed canonical replacement for broad internal `PROTECTION_FUNCTION`;
- a path is intrinsically structured to preserve the controller/player or their object(s) from a specified harmful event/state or directly grants a defensive status that prevents/invalidates that harm;
- examples can include granting hexproof, indestructible, ward, keyword protection, phasing out an allied object, damage prevention, regeneration/replacement survival, and other explicitly scoped rescue mechanisms once individually ratified.

### `DEFENSIVE_INTERACTION`

- `AGGREGATE_VIEW`, not primitive semantic membership;
- may include `PROTECTIVE_EFFECT`, pillowfort/tax effects, generic counterspells used defensively, combat restrictions, and other opponent-deterrence mechanisms according to product/report policy.

A generic Counterspell remains `COUNTERSPELL`. It does not become `PROTECTIVE_EFFECT` solely because a player can choose to use it to save a permanent.

A Ghostly Prison-like card may appear in a Defensive Interaction report without being misclassified as keyword Protection or direct Protective Effect.

---

## A6 — Spot Removal requires selection authority; one-object removal does not always mean Spot Removal

Keep the registry split between:

- `SPOT_REMOVAL` — source controller individually designates the battlefield permanent;
- `NONSELECTIVE_SINGLE_REMOVAL` — exactly one permanent is removed, but affected player/random/rule process determines which one.

Add explicit facet:

```text
selection_authority:
  SOURCE_CONTROLLER
  AFFECTED_PLAYER
  OPPONENT_OTHER_THAN_AFFECTED
  RANDOM
  RULE_DEFINED
  NONE_SET_BASED
```

This is required for edicts, random removal, Council's-dilemma/vote-like effects, and future selection structures.

---

## A7 — Removal must preserve direct versus state-dependent lethality

The user-facing removal package may eventually aggregate both, but semantic truth must preserve:

```text
DIRECT_PERMANENT_REMOVAL
STATE_DEPENDENT_PERMANENT_REMOVAL
```

Examples:

- Swords to Plowshares: direct removal.
- Murder: direct destroy mechanism.
- Lightning Bolt targeting a creature: state-dependent removal-capable damage with magnitude 3.
- -2/-2 until end of turn: state-dependent on toughness/state.
- fight/bite: state-dependent on source characteristics and target state.

Do not label fixed damage as unconditional removal of the entire creature class.

Deck-health UI may count state-dependent removal with reliability/magnitude facets visible; that aggregation policy is separate from semantic membership.

---

## A8 — Sweeper and Board Wipe remain presentation concepts over exact mass mechanisms

A direct `Destroy all creatures` path and a 13-damage-to-all-creatures path are mechanically different even though players may call both board wipes.

Keep exact lower facts:

- `MASS_REMOVAL` for set-based qualifying removal mechanisms;
- broad mass damage/toughness-reduction mechanisms with magnitude/state dependence;
- symmetry/player scope;
- object-class predicate.

Use **Board Wipe / Wrath / Sweeper** only as aliases/views after the exact mechanism remains recoverable.

This avoids arguing semantic truth from slang while still supporting the familiar deckbuilding category.

---

## A9 — Graveyard “Recursion” should be modeled as access/retrieval mechanisms, not one overloaded operation

`GRAVEYARD_ACCESS` remains the proposed parent/view, but exact children should distinguish at least:

- `GRAVEYARD_TO_HAND`;
- `GRAVEYARD_TO_BATTLEFIELD`;
- `CAST_OR_PLAY_FROM_GRAVEYARD`;
- `GRAVEYARD_TO_LIBRARY` where useful;
- self-only permission versus recovering another card;
- one-shot versus repeatable access.

**Recursion** remains user-facing vocabulary, not the sole executable operation.

This also prevents Flashback-like self-use from being treated as mechanically identical to Regrowth or Reanimate.

---

## A10 — Tutor and “dig” must stay separated

Wizards R&D explicitly uses different concepts for:

- **tutoring** — searching the library for a specified/qualifying card;
- bounded top-N **impulsing/digging** — inspecting only a limited top portion and selecting from it.

Therefore:

- internal `LIBRARY_SEARCH` is the exact tutor-like search family;
- `TOP_N_SELECTION` remains separate;
- `TUTOR` is a user-facing alias/group unless Captain explicitly ratifies an exact canonical mapping;
- old `LIGHT_TUTOR` / `ALT_TUTOR` should not become production semantics.

This also prevents a deep top-10 selection effect from becoming indistinguishable from Demonic Tutor merely because both improve access to a desired card.

---

## A11 — “Impulse” is unsafe as an internal root term

Because Wizards uses both **impulsive draw** (temporary exile/play access) and **impulsing** (bounded top-N look/select) in R&D vocabulary, never use bare `IMPULSE` as the canonical internal operation.

Use:

- `TEMPORARY_EXILE_ACCESS` for exile + bounded play/cast permission;
- `TOP_N_SELECTION` for bounded look/select from library.

UI may still say **Impulse Draw** where appropriate.

---

## A12 — Mana Sink is a real general function, but not necessarily a universal skeleton requirement

Wizards repeatedly defines a mana sink as something that lets a player spend excess mana, often through repeatable activated abilities or scalable/additional costs.

The registry's proposed internal `EXCESS_MANA_OUTLET` is retained, with user-facing alias **Mana Sink**.

Keep two claims separate:

1. **semantic claim:** this card/path can absorb optional excess mana;
2. **deckbuilding recommendation:** this deck should or should not contain a certain number of mana sinks.

Only claim 1 belongs to Objective 6 semantic truth.

---

## A13 — Deck smoothing, consistency, flexibility, efficiency, and inevitability remain metrics/views

Do not promote these into primitive card tags merely because they are established Magic strategy terms.

- `DECK_SMOOTHING` — aggregate/metric over draw, selection, search, access, etc.
- `CONSISTENCY` — deck metric.
- `FLEXIBILITY` / `VERSATILITY` — card/deck metric from modes, target breadth, timing, etc.
- `MANA_EFFICIENCY` — comparison metric.
- `INEVITABILITY` — matchup/game-state relation.
- `CARD_QUALITY` — card/game-state metric.
- `TEMPO` — game-state/resource model.

The exact lower facts remain the semantic substrate.

---

## Amendment acceptance condition

If the Captain accepts these corrections, the eventual ratified registry should incorporate them directly rather than carrying an amendment chain into production authority.

Until then, read this amendment before the registry when evaluating the affected terms.
