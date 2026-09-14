# Objective 6 — Canonical Term Registry Draft

**Status:** CAPTAIN REVIEW / NON-EXECUTING / NOT RATIFIED  
**Date:** 2026-09-14  
**Objective:** 6 — `FOUNDRY_FUNCTIONAL_VOCABULARY_SPECIFICATION`  
**Companions:**
- `OBJECTIVE6-FUNCTIONAL-VOCABULARY-AND-DECK-HEALTH-DRAFT.md`
- `OBJECTIVE6-DECKBUILDING-TERMINOLOGY-CENSUS-AND-CANONICALIZATION.md`

**Implementation authorization:** **NONE.** This registry is a terminology proposal. A term marked `OPEN` is explicitly non-executable. Nothing here authorizes S16A/S16B implementation, parser/codebook mutation, merge, deployment, AQ4, or Bridge v0.

---

## 1. Registry purpose

The product may use familiar Magic language. The engine must not depend on familiar language being precise.

This registry therefore separates:

```text
USER-FACING ALIAS
    from
CANONICAL FOUNDRY CONCEPT
    from
LOWER MECHANICAL FACT / FACET
    from
DECK-LEVEL METRIC OR RELATION
```

A term is ready for ratification only when:

1. it has exactly one semantic kind;
2. its membership boundary is deterministic;
3. its required context is explicit;
4. its aliases cannot silently broaden it;
5. its exclusions are explicit;
6. any numeric/accounting window is explicit;
7. gold positives and hard negatives exist;
8. required S16A facts can be represented without approximation.

If any of those are unresolved, status must remain `OPEN`, not guessed.

---

## 2. Semantic kinds

| Kind | Meaning |
|---|---|
| `DECK_STRUCTURE` | Composition/shape of a deck, not a card function. |
| `GENERAL_FUNCTION` | Cross-strategy job an effect/card can perform. |
| `MECHANICAL_FAMILY` | Objective implementation family with recognizable mechanical form. |
| `ACCOUNTING_FUNCTION` | Function requiring an explicit resource accounting domain/window. |
| `AGGREGATE_VIEW` | User/report grouping computed from more exact concepts; not primitive semantic truth. |
| `DECK_ROLE_RELATIONAL` | Role that only exists relative to a deck/plan/package/metagame/game state. |
| `DECK_METRIC` | Measured/derived property of a deck or package. |
| `CARD_METRIC` | Measured/derived property of a card/path rather than categorical function. |
| `STRATEGY` | Deck/archetype plan. |
| `FACET` | Orthogonal property used to refine a function without creating a new function label. |

---

## 3. Status vocabulary

| Status | Meaning |
|---|---|
| `PROPOSED-CLEAR` | Manager believes the boundary is now unambiguous enough for Captain review. |
| `OPEN` | A material boundary still needs a Captain ruling or adversarial fixture pass. |
| `ALIAS-ONLY` | Familiar term may be displayed, but should not be its own executable semantic predicate. |
| `METRIC-ONLY` | Derived measurement; do not assign as intrinsic card tag. |
| `RELATIONAL-ONLY` | Requires deck/package/game context; do not assign globally to card. |
| `DEFERRED` | Useful later, deliberately outside initial general-function freeze. |
| `REJECT-AS-PRIMITIVE` | Too vague/contextual to become semantic primitive. |

---

# PART I — DECK STRUCTURE AND MANA

## 4. `MANA_BASE`

- **Kind:** `DECK_STRUCTURE`
- **Status:** `PROPOSED-CLEAR`
- **Aliases:** mana package
- **Canonical meaning:** the deck-level collection of land-capable slots and supplemental mana-producing sources relied upon to produce the mana needed to execute the deck.
- **Does not mean:** lands only; ramp only; color fixing only.
- **Required decomposition:** land-capable slots, nonland mana sources, color-source coverage, source conditionality.

### 4.1 `LAND_BASE`

- **Kind:** `DECK_STRUCTURE`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** the subset of deck slots with a legal land face/play mode under the declared deck-analysis policy.
- **Open implementation policy:** MDFCs/modal land-capable cards require an explicit denominator/counting policy. Do not silently count them as identical to unconditional lands.

## 5. `MANA_CURVE`

- **Kind:** `DECK_METRIC`
- **Status:** `METRIC-ONLY`
- **Meaning:** distribution of relevant mana costs across deck slots under an explicitly declared cost-selection policy.
- **Not a card tag.**
- **Policy must state:** treatment of X costs, alternative costs, split/modal cards, commander tax, cost reducers, free/alternate cast modes, lands.

## 6. `MANA_SOURCE`

- **Kind:** `GENERAL_FUNCTION` / lower capability
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** a card/object/path can produce mana under represented legal conditions.
- **Required facets:** amount, colors, activation/payment cost, tap/sacrifice requirement, timing, repeatability, condition, controller dependency.

## 7. `COLOR_SOURCE`

- **Kind:** `DECK_METRIC` over `MANA_SOURCE`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** a mana source can produce a specified required color under the declared availability assumptions.
- **Example:** Sol Ring is a mana source but not a colored mana source.

## 8. `MANA_FIXING`

- **Kind:** `GENERAL_FUNCTION`
- **Status:** `PROPOSED-CLEAR`
- **Aliases:** color fixing
- **Meaning:** a source/path improves the controller's access to required mana colors or converts available mana/resources into a more useful color distribution without requiring an increase in total mana quantity.
- **Does not imply:** acceleration.
- **May overlap with:** acceleration when one source does both.

## 9. `MANA_ACCELERATION`

- **Kind:** `GENERAL_FUNCTION`
- **Status:** `OPEN`
- **Working meaning:** a source/path creates a route to greater usable mana-producing capacity earlier than the ordinary one-land-play-per-turn baseline would provide.
- **Why OPEN:** the exact baseline for conditional extra-land effects, sacrifice sources, land opportunity cost, and temporary mana must be frozen.
- **Required facets:** durable/temporary, conditionality, timing, opportunity cost, net same-turn mana delta.

## 10. `DURABLE_MANA_ACCELERATION`

- **Kind:** `GENERAL_FUNCTION`
- **Status:** `PROPOSED-CLEAR`, subject to Captain confirming the existing Ramp direction
- **User-facing alias:** **Ramp**
- **Meaning:** Mana Acceleration that establishes or advances a continuing mana-producing resource capable of providing mana on later turns without the qualifying source/path inherently expending itself in the same use.
- **Includes candidate families:** land ramp, mana rocks, mana creatures, qualifying durable multi-mana lands/permanents.
- **Excludes:** one-shot rituals; extra-land-play permission by itself; ordinary one-mana land development; temporary burst mana.
- **Reason for explicit internal name:** community use of *ramp* often includes broader acceleration. `DURABLE_MANA_ACCELERATION` prevents the engine from silently changing meanings while UI may still say Ramp.

## 11. `LAND_RAMP`

- **Kind:** `MECHANICAL_FAMILY`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** a path obtains/selects a land card from a library and puts that land onto the battlefield.
- **Excludes:** extra land-play permission; land from graveyard to battlefield; land to hand; token generation that merely produces mana.
- **Facets:** tapped/untapped, basic/nonbasic, type restriction, owner library, quantity.

## 12. `EXTRA_LAND_PLAY`

- **Kind:** `GENERAL_FUNCTION`
- **Status:** `PROPOSED-CLEAR`
- **Old working name:** `LAND_ADD`
- **Meaning:** increases the number of land plays the controller is permitted to make during the applicable turn/window.
- **Does not itself:** produce a land card or put one onto the battlefield.
- **Dependency:** requires a playable land resource.
- **Parent relation to Mana Acceleration:** `OPEN` until the Mana Acceleration baseline is ratified.

## 13. `ARTIFACT_MANA_SOURCE`

- **Kind:** `MECHANICAL_FAMILY`
- **Status:** `PROPOSED-CLEAR`
- **User-facing alias:** Mana Rock
- **Meaning:** a nonland artifact permanent has its own repeatably usable mana-producing ability/path.
- **Excludes by default:** artifact lands; one-shot Treasure-like artifacts if the Captain wants Mana Rock to preserve the repeatable community sense.

## 14. `CREATURE_MANA_SOURCE`

- **Kind:** `MECHANICAL_FAMILY`
- **Status:** `PROPOSED-CLEAR`
- **User-facing aliases:** Mana Creature; Mana Dork for narrower familiar subset
- **Meaning:** a creature permanent has an intrinsic mana-producing ability/path.
- **Required facets:** activated/triggered/static production, repeatability, tap requirement, attack/combat dependency, sacrifice requirement.

### 14.1 `MANA_DORK`

- **Status:** `ALIAS-ONLY` unless Captain wants a narrower executable child.
- **Recommended alias target:** repeatable activated `CREATURE_MANA_SOURCE`.
- **Reason:** slang boundaries vary for triggered/combat/sacrifice-based mana creatures.

## 15. `RITUAL`

- **Kind:** `MECHANICAL_FAMILY`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** a one-shot spell/effect produces temporary/burst mana without establishing a durable mana source.
- **May also be:** Fast Mana if the separate Fast Mana contract is satisfied.
- **Is not:** Durable Mana Acceleration/Ramp.

## 16. `FAST_MANA`

- **Kind:** `ACCOUNTING_FUNCTION`
- **Status:** `OPEN`
- **Current Captain candidate rule:** intrinsic deploy/use mana cost <= 2; qualifying mana is immediately available; same-turn mana output exceeds mana spent to deploy/use the source/path; external reducers/doublers do not manufacture membership.
- **Open boundary:** land-play opportunity cost and zero-mana land deployment; Ancient Tomb/Phyrexian Tower-like cases require explicit treatment.

## 17. `MANA_PARITY`

- **Kind:** `ACCOUNTING_FUNCTION`
- **Status:** `OPEN`
- **Meaning goal:** source/path replaces, refunds, or reconfigures mana development without positive net acceleration in the declared accounting window.
- **Open:** baseline and time window.
- **Current boundary fixtures:** Boros Garrison; Priest of Gix.

## 18. `COST_REDUCTION`

- **Kind:** `GENERAL_FUNCTION`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** lowers a represented mana/resource cost required for a defined action class without itself producing that mana/resource.
- **Does not imply:** Mana Source, Mana Fixing, or Mana Acceleration.
- **Required facets:** action class, amount/formula, floor, controller/object scope, conditionality.

## 19. `EXCESS_MANA_OUTLET`

- **Kind:** `GENERAL_FUNCTION`
- **Status:** `PROPOSED-CLEAR`
- **User-facing alias:** **Mana Sink**
- **Meaning:** a card/path offers an optional scalable, repeatable, or additional mana expenditure beyond its minimum access/deployment requirement that converts otherwise excess mana into additional game effect/resource.
- **Includes candidate mechanisms:** repeatable mana-costed activated abilities; X/scalable effects; kicker/multikicker/optional higher-cost modes; repeatable equip/reconfigure-like mana use where it creates additional effect.
- **Does not mean:** merely having a high fixed mana cost.
- **Facets:** repeatable/scalable/one-shot, ceiling, action timing, resource produced.

## 20. `MANA_EFFICIENCY`

- **Kind:** `CARD_METRIC` / `DECK_METRIC`
- **Status:** `METRIC-ONLY`
- **Meaning:** relationship between mana spent and impact/use of available mana under a declared comparison model.
- **Do not tag cards:** `MANA_EFFICIENT=true` without a comparison context.

---

# PART II — CARD ACCESS, SELECTION, AND ACCOUNTING

## 21. `DRAW`

- **Kind:** exact rules-action capability
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** the Magic rules action **draw** occurs.
- **Excludes:** put into hand; exile and play; cast from top; return from graveyard; search/tutor; scry/surveil.
- **Facets:** count, controller/player, immediate/delayed, optionality, trigger/dependency.

## 22. `CARD_SELECTION`

- **Kind:** `GENERAL_FUNCTION`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** a path gives a player meaningful control over which candidate card(s) become accessible, remain accessible, or are encountered next, without requiring net positive card quantity.
- **Includes mechanical children:** loot, rummage, scry, surveil, bounded top-N choice, top-library reordering.
- **Does not imply:** Draw or Card Advantage.

## 23. `CARD_FILTERING`

- **Status:** `ALIAS-ONLY`
- **Reason:** community/R&D usage spans several different selection operations.
- **Recommended display mapping:** aggregate over relevant `CARD_SELECTION` children.

## 24. `LOOT`

- **Kind:** `MECHANICAL_FAMILY`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** linked operation performs draw N before discard M.
- **Preserve:** N and M independently; discard choice/randomness; same player; timing linkage.

## 25. `RUMMAGE`

- **Kind:** `MECHANICAL_FAMILY`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** linked operation performs discard M before draw N.
- **Distinction from Loot is semantic order, not flavor.**

## 26. `TOP_LIBRARY_MANIPULATION`

- **Kind:** `MECHANICAL_FAMILY`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** changes order/disposition of known/inspected top-library cards without itself necessarily transferring a card into a playable/hand zone.
- **User-facing aliases:** top-deck manipulation; the earlier project word `INDEX` may be UI shorthand only.

## 27. `TOP_N_SELECTION`

- **Kind:** `MECHANICAL_FAMILY` / `GENERAL_FUNCTION`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** a path inspects a bounded top-N library domain and lets the appropriate player select qualifying card(s) from that bounded domain for a declared destination/access state.
- **Does not equal:** Tutor/library search.
- **Reason:** Wizards R&D explicitly distinguishes top-N "impulsing" from tutoring.
- **Facets:** N, selection count, criteria, destination, remainder disposition, reveal/publicity.

## 28. `LIBRARY_SEARCH`

- **Kind:** `GENERAL_FUNCTION` / mechanical access family
- **Status:** `PROPOSED-CLEAR`
- **User-facing alias:** Tutor, when used in the familiar search-and-retrieve sense
- **Meaning:** a path searches a library domain according to explicit criteria and identifies/retrieves qualifying card(s), rather than merely inspecting a bounded top-N subset.
- **Facets:** criteria, selection count, destination, reveal, shuffle, optionality, owner library, public/hidden information handling.

## 29. `LIBRARY_ACCESS`

- **Kind:** `AGGREGATE_VIEW`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** report/query umbrella over distinct library-access mechanisms such as `LIBRARY_SEARCH`, `TOP_N_SELECTION`, reveal-until-hit, top-card permission, etc.
- **Do not treat all children as Tutor.**

## 30. `TUTOR`

- **Status:** `ALIAS-ONLY` unless Captain explicitly ratifies a canonical narrower mapping.
- **Recommended mapping:** user-facing alias for `LIBRARY_SEARCH`/unbounded selective retrieval.
- **Do not use for:** top-N selection merely because it finds a useful card.
- **Old `ALT_TUTOR` / `LIGHT_TUTOR`:** retire as internal names; use exact mechanism such as `TOP_N_SELECTION`.

## 31. `TEMPORARY_EXILE_ACCESS`

- **Kind:** `GENERAL_FUNCTION` / mechanical access family
- **Status:** `PROPOSED-CLEAR`
- **User-facing alias:** Impulse Draw / Impulsive Draw
- **Meaning:** a path exiles/reveals card(s) into exile and grants bounded permission to play and/or cast those specific card(s) during a defined time window.
- **Does not equal:** Draw.
- **Required facets:** source zone/player, count, play versus cast permission, type restrictions, start/end of permission, unused-card disposition, mana-spending permissions.
- **Reason for avoiding internal `IMPULSE`:** Wizards uses *impulsive draw* for this effect but also uses *impulsing* for bounded top-N selection. The internal name must not collide.

## 32. `PLAY_FROM_LIBRARY_TOP`

- **Kind:** `GENERAL_FUNCTION`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** grants permission to play/cast one or more card classes directly from the top of a library while the permission is active.
- **Distinct from:** Draw, Temporary Exile Access, Tutor, Top-N Selection.

## 33. `CARD_RESOURCE_PARITY`

- **Kind:** `ACCOUNTING_FUNCTION`
- **Status:** `OPEN`
- **Meaning goal:** after charging the source expenditure defined by the contract, the path restores exactly the same quantity of usable personal card resources within the declared accounting window; net delta = 0.
- **Open:** exact resource set and treatment of battlefield permanents/temporary access.

## 34. `PERSONAL_CARD_RESOURCE_ADVANTAGE`

- **Kind:** `ACCOUNTING_FUNCTION`
- **Status:** `OPEN`
- **User-facing alias candidate:** Card Advantage in a clearly scoped deck-health panel
- **Meaning goal:** within a declared accounting domain/window, after charging the source expenditure, the source/path creates net positive usable card resources for its controller.
- **Does not include:** opponent card losses merely because they produce traditional relative card advantage.
- **Reason for explicit internal name:** established Magic usage defines Card Advantage relative to the opponent and includes favorable removal/discard exchanges.

## 35. `RELATIVE_CARD_ADVANTAGE`

- **Kind:** future game-state/accounting metric
- **Status:** `DEFERRED`
- **Meaning:** card-resource differential relative to opponent(s), potentially including destroyed/discarded permanents/cards.
- **Not Objective 6 v1 card-global truth.**

## 36. `CONDITIONAL_CARD_RESOURCE_ADVANTAGE`

- **Kind:** `ACCOUNTING_FUNCTION` + dependency facets
- **Status:** `OPEN`
- **Old working name:** Potential Card Advantage
- **Recommendation:** prefer one `PERSONAL_CARD_RESOURCE_ADVANTAGE` capability plus explicit dependency facets where possible rather than a vague second ontology.
- **Candidate dependency facets:** controller-action, opponent-action, combat, board-state, payment, delayed, repeatable, rate-limited.
- **Required fixtures:** Sram, Phyrexian Arena, Rhystic Study, Esper Sentinel, Trouble in Pairs, Aurelia.

## 37. `SELF_REPLACING_DRAW_EFFECT`

- **Kind:** `MECHANICAL_FAMILY` / accounting-derived family
- **Status:** `PROPOSED-CLEAR`
- **User-facing alias:** Cantrip
- **Meaning:** a spell/effect has its principal/minor effect plus a linked literal draw component that replaces the card expenditure under the declared simple card-resource accounting.
- **Historical delayed variant:** may be separately labeled Slowtrip if product value warrants it.
- **Does not include:** Temporary Exile Access, top-N selection into hand without drawing, or generic low-cost parity solely because they replace the resource.

## 38. `LOW_COST_CARD_PARITY`

- **Kind:** `ACCOUNTING_FUNCTION`
- **Status:** `OPEN`
- **Purpose:** preserve the broader useful product concept formerly overloaded onto Cantrip.
- **Working meaning:** source/path has intrinsic effective use/deploy cost <= Captain threshold and immediately restores at least the charged card resource through any ratified access mechanism.
- **Open:** temporary exile access valuation; Cycling treatment; exact cost basis.

## 39. `DECK_SMOOTHING`

- **Kind:** `AGGREGATE_VIEW` / `DECK_METRIC`
- **Status:** `METRIC-ONLY`
- **Meaning:** deck-level reduction in draw/access variance produced by selection, draw, search, top-N access, filtering, and related tools.
- **Do not assign:** `DECK_SMOOTHING=true` to one card as primitive truth.

## 40. `CARD_VELOCITY`

- **Status:** `REJECT-AS-PRIMITIVE`
- **Reason:** community usage can include draw, temporary access, self-mill, selection, and any mechanism that moves through usable/deck resources faster.
- **Use instead:** exact access/selection facts plus a later deck metric if useful.

## 41. `CARD_QUALITY`

- **Kind:** `CARD_METRIC` / game-context metric
- **Status:** `METRIC-ONLY`
- **Not a semantic function.**

---

# PART III — INTERACTION AND ANSWERS

## 42. `INTERACTION`

- **Kind:** `AGGREGATE_VIEW`
- **Status:** `ALIAS-ONLY`
- **Meaning:** user/report grouping over exact opponent-facing and defensive response mechanisms.
- **Do not assign primitive:** `INTERACTION=true` without retaining exact child capability.
- **Possible members:** permanent removal, neutralization, stack interaction, graveyard denial, hand disruption, cast/action restriction, taxes, defensive protection depending report policy.

## 43. Removal result model

A key distinction is **capability** versus guaranteed game outcome.

External game state can prevent or alter a removal attempt (indestructible, protection, replacement effects, insufficient damage, etc.). Foundry should therefore not pretend that a card globally guarantees a permanent's departure.

Use at least these lower distinctions:

### 43.1 `DIRECT_PERMANENT_REMOVAL`

- **Status:** `PROPOSED-CLEAR`
- **Meaning:** the path directly instructs or causes a battlefield permanent to change out of the battlefield zone or be destroyed/sacrificed, subject to normal rules/replacement effects.
- **Mechanism facets:** destroy, exile, return-to-hand, put/return-to-library, forced sacrifice, other direct zone transition.

### 43.2 `STATE_DEPENDENT_PERMANENT_REMOVAL`

- **Status:** `PROPOSED-CLEAR`
- **Meaning:** the path applies damage, toughness reduction, or another represented mechanism that can cause a permanent to leave the battlefield only when target/object state satisfies explicit conditions.
- **Required facets:** magnitude/formula and qualifying state.
- **Example:** fixed creature damage can be removal-capable for creatures within its lethal range but is not unconditional removal of arbitrary creatures.

## 44. `SPOT_REMOVAL`

- **Kind:** `GENERAL_FUNCTION`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** a removal-capable path lets the source's controller individually designate exactly one battlefield permanent to receive a qualifying direct or state-dependent removal mechanism.
- **Designation may be:** target, choose, or equivalent precise controller selection.
- **Excludes:** opponent-chosen edicts; random removal; set-based mass removal; stack countering; permanent-neutralization that leaves the object on battlefield.
- **Required facets:** object class, mechanism, state dependency, condition, timing, controller restrictions.

## 45. `NONSELECTIVE_SINGLE_REMOVAL`

- **Kind:** `GENERAL_FUNCTION` / mechanical scope family
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** a path removes one battlefield permanent, but the source controller does not individually choose which permanent is removed.
- **Examples:** target opponent sacrifices a creature they choose; random single permanent destruction.
- **Required facet:** selection authority (`AFFECTED_PLAYER`, `RANDOM`, `RULE_DEFINED`, etc.).
- **Reason:** avoids forcing edicts into Spot Removal.

## 46. `SELECTIVE_MULTI_REMOVAL`

- **Kind:** `GENERAL_FUNCTION`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** one legal path lets the source controller individually designate at least two distinct battlefield permanents that each receive a qualifying removal mechanism.
- **Threshold:** >= 2; no maximum.
- **Excludes:** universal/set-based removal; multi-interaction where some affected items are spells/abilities rather than permanents; one chosen object with several legal types.

## 47. `MASS_REMOVAL`

- **Kind:** `GENERAL_FUNCTION`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** a path applies a qualifying removal mechanism to a battlefield set defined by object/property/player predicates rather than individually designating every affected permanent.
- **Examples:** destroy all creatures; exile all artifacts; return all nonland permanents; destroy all creatures you do not control.
- **Required facets:** matching predicate, player/controller scope, mechanism, symmetry, exclusions, state dependency.

## 48. `BOARD_WIPE`

- **Status:** `ALIAS-ONLY` / presentation subfamily of `MASS_REMOVAL`
- **Aliases:** Wrath; Sweeper (with caveat below)
- **Recommended display meaning:** Mass Removal over an unbounded matching battlefield class within its declared scope.
- **Do not use as independent competing membership law.**

### 48.1 `SWEEPER`

- **Status:** `AGGREGATE_VIEW`
- **Reason:** community use may include broad damage/toughness-reduction effects that are removal-capable but state-dependent.
- **Recommendation:** UI/report can aggregate direct Mass Removal plus qualifying broad state-dependent removal mechanisms, with mechanism/reliability exposed.

## 49. `ONESIDED_MASS_REMOVAL`

- **Kind:** child/scope refinement of `MASS_REMOVAL`
- **Status:** `PROPOSED-CLEAR`
- **User alias:** One-sided Board Wipe
- **Meaning:** affected player/controller scope excludes the source controller's matching battlefield objects while including opposing matching objects.

## 50. `NEUTRALIZATION`

- **Kind:** `GENERAL_FUNCTION`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** a path materially suppresses relevant functionality of a battlefield permanent while that permanent remains on the battlefield.
- **Mechanism facets:** cannot attack/block; ability loss; activation prohibition; sustained tap/untap lock; transformation; other capability suppression.
- **Excludes:** control theft unless it also suppresses functionality; zone-exit removal; taxes that leave capabilities usable at increased cost unless separately included by explicit child.

## 51. `THEFT`

- **Kind:** `MECHANICAL_FAMILY` / interaction capability
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** changes control of an object from another player to the source controller/another controller.
- **Does not equal:** Removal or Neutralization merely because the opponent loses control.
- **Facets:** temporary/permanent, object class, untap/haste, return condition.

## 52. `MULTI_INTERACTION`

- **Kind:** `GENERAL_FUNCTION` / path property
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** one legal path can individually answer/affect at least two distinct game objects/actions, whether or not all are battlefield permanents or all results are Removal.
- **Gold example:** Cryptic Command counter-spell + bounce-permanent mode pair.
- **Does not imply:** Selective Multi-removal.

## 53. `COUNTERSPELL`

- **Kind:** `GENERAL_FUNCTION`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** a path counters a spell on the stack.
- **Facets:** spell eligibility, conditionality, payment escape, alternative/additional cost, controller restriction.

## 54. `ABILITY_COUNTER`

- **Kind:** `GENERAL_FUNCTION`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** a path counters an activated and/or triggered ability on the stack.
- **Does not equal:** Counterspell.

## 55. `SPELL_OR_ABILITY_REDIRECTION`

- **Kind:** `MECHANICAL_FAMILY`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** changes target(s) of a spell/ability or changes who controls/chooses its target(s) under the represented effect.
- **Do not flatten into:** Counterspell or Removal.

## 56. `STACK_INTERACTION`

- **Kind:** `AGGREGATE_VIEW`
- **Status:** `ALIAS-ONLY`
- **Meaning:** report grouping over Counterspell, Ability Counter, redirection, selected copy/control mechanisms, and other explicit stack-event answers.

## 57. `HAND_DISRUPTION`

- **Kind:** `AGGREGATE_VIEW` / general answer family
- **Status:** `PROPOSED-CLEAR` as aggregate
- **Meaning:** opponent-facing effects that reveal/select/remove/constrain hand resources.
- **Exact children must remain visible:** discard, forced discard, selective discard, hand reveal, hand-size restriction, etc.

## 58. `GRAVEYARD_DENIAL`

- **Kind:** `GENERAL_FUNCTION`
- **Status:** `PROPOSED-CLEAR`
- **User-facing alias:** Graveyard Hate
- **Meaning:** a path prevents or materially reduces an opponent's ability to retain, receive, target, cast/play, activate, return, or otherwise exploit cards/resources in a graveyard.
- **Required mechanism facets:** targeted exile, whole-yard exile, all-yard exile, replacement/exile instead of graveyard entry, cast/play prohibition, activation prohibition, targeting/access prohibition, shuffle/move-out, other.
- **Why not `HATE` internally:** hate is relational to a strategy/card/mechanic, not one mechanical fact.

## 59. `CAST_OR_ACTION_RESTRICTION`

- **Kind:** `GENERAL_FUNCTION`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** changes legality/timing/availability of a defined class of player actions without merely increasing their cost.
- **Includes:** Silence-like prohibitions; timing restrictions; activation restrictions.
- **Facets:** actor scope, action class, timing, duration, exception conditions.

## 60. `TAX_OR_COST_INCREASE`

- **Kind:** `GENERAL_FUNCTION`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** increases required cost/payment for a defined opponent/player action while leaving that action legal if the increased cost can be paid.
- **Separate from:** Cast/Action Restriction.

---

# PART IV — PROTECTION, RECOVERY, AND CONTINUITY

## 61. `PROTECTION_FUNCTION`

- **Kind:** `GENERAL_FUNCTION`
- **Status:** `PROPOSED-CLEAR`
- **User-facing alias:** Protection
- **Meaning:** a path is intrinsically structured to preserve the controller/player or designated allied object(s) from a harmful event/state, or directly grants a defensive status that prevents/invalidates such harm.
- **Candidate mechanisms:** hexproof/shroud/ward granting, indestructible, Magic keyword protection, phasing-out allied objects, damage prevention, regeneration/replacement survival, narrowly protective countering, rescue/bounce of own object where the path is explicitly defensive.
- **Does not include by default:** generic Counterspell simply because a player could choose to use it protectively.
- **Required facets:** protected subject, threat/effect class, duration, cost, timing, self/other scope.

## 62. `DAMAGE_PREVENTION`

- **Kind:** `MECHANICAL_FAMILY`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** prevents a represented amount/class of damage that would otherwise be dealt.
- **May imply Protection Function when scope is protective.**

## 63. `GRAVEYARD_ACCESS`

- **Kind:** `GENERAL_FUNCTION` / aggregate capability parent
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** a path restores or grants usable access to a card/resource in a graveyard through a specified move or permission mechanism.
- **Preferred internal parent over bare `RECURSION` because the mechanism is explicit.**
- **Facets:** whose graveyard, object class, destination/access mode, count, repeatability, self-only/other cards.

## 64. `GRAVEYARD_TO_HAND`

- **Kind:** `MECHANICAL_FAMILY`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** moves qualifying card(s) from graveyard to hand.

## 65. `GRAVEYARD_TO_BATTLEFIELD`

- **Kind:** `MECHANICAL_FAMILY`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** puts qualifying card(s) from graveyard directly onto battlefield.
- **User-facing alias for creature subset:** Reanimation.
- **Reason for explicit parent:** Wizards R&D uses Reanimation specifically for creature cards; Foundry should not make noncreature permanent recovery semantically ambiguous.

### 65.1 `CREATURE_REANIMATION`

- **Status:** `PROPOSED-CLEAR`
- **Meaning:** `GRAVEYARD_TO_BATTLEFIELD` with `object_class = creature card`.
- **User alias:** Reanimation.

## 66. `CAST_OR_PLAY_FROM_GRAVEYARD`

- **Kind:** `GENERAL_FUNCTION` / mechanical access family
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** grants permission to cast/play qualifying cards directly from graveyard without first moving them to hand/battlefield as a separate retrieval action.

## 67. `RECURSION`

- **Status:** `ALIAS-ONLY`
- **Recommended mapping:** player-facing aggregate over qualifying `GRAVEYARD_ACCESS` mechanisms, with exact mechanism always preserved.
- **Reason:** community usage varies between one-time graveyard recovery and repeatable loops.

## 68. `BLINK`

- **Kind:** `MECHANICAL_FAMILY`
- **Status:** `PROPOSED-CLEAR`
- **Alias:** Flicker
- **Meaning:** a linked semantic path exiles a battlefield permanent/card and later returns that same card from exile to the battlefield under represented timing/control conditions.
- **Required:** linked object identity.
- **Excludes:** phasing; bounce+unrelated recast; simple exile; graveyard reanimation.

### 68.1 `BLINK_IMMEDIATE`

- **Status:** `PROPOSED-CLEAR`
- **Old name:** Blink-Now
- **Meaning:** linked return completes within the same resolving semantic sequence without a later scheduled game-time event.

### 68.2 `BLINK_DELAYED`

- **Status:** `PROPOSED-CLEAR`
- **Meaning:** exile establishes a linked return event scheduled for a later game time/event.

---

# PART V — CLOSING THE GAME AND STRATEGY-DEPENDENT ROLES

## 69. `WIN_CONDITION`

- **Kind:** `DECK_ROLE_RELATIONAL`
- **Status:** `RELATIONAL-ONLY`
- **User alias:** Wincon
- **Meaning:** relative to a specific deck/package, a card/path/package is a realistic route by which that deck can satisfy a game-winning condition.
- **Context required:** deck; often package/strategy.
- **Do not assign globally to card.**

## 70. `FINISHER`

- **Kind:** `DECK_ROLE_RELATIONAL`
- **Status:** `RELATIONAL-ONLY`
- **Meaning:** relative to a deck/state plan, a card/path converts an already developed favorable resource/board position into a game-ending or near-game-ending position.
- **Do not assign globally.**

## 71. `THREAT`

- **Kind:** game-state/deck-role relation
- **Status:** `RELATIONAL-ONLY`
- **Meaning:** an object/path whose unresolved/continued presence materially advances a player toward winning in the relevant matchup/state.
- **Context required:** game state and opponent/deck context.

## 72. `EXPLICIT_WIN_EFFECT`

- **Kind:** objective mechanical capability
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** Oracle/rules instruction directly causes a player to win or lose when its stated condition resolves/is satisfied.
- **Does not imply:** global Win Condition role in every deck.

## 73. `ENGINE`

- **Status:** `RELATIONAL-ONLY` / `DEFERRED`
- **Meaning:** a card or package repeatedly converts qualifying inputs/events/resources into outputs as part of a deck plan.
- **Why not primitive:** engine status can depend on other cards/events and intended plan.

## 74. `ENABLER`

- **Status:** `RELATIONAL-ONLY` / `DEFERRED`
- **Question always required:** enabler **for what relation/strategy/function?**

## 75. `PAYOFF`

- **Status:** `RELATIONAL-ONLY` / `DEFERRED`
- **Question always required:** payoff **for what input/strategy/event?**

## 76. `SYNERGY`

- **Kind:** relation between cards/facts/strategy
- **Status:** `RELATIONAL-ONLY`
- **Do not assign primitive:** `SYNERGY=true` to a card in isolation.

---

# PART VI — USEFUL GENERAL FUNCTIONS THAT ARE NOT UNIVERSAL SKELETON REQUIREMENTS

## 77. `TOKEN_GENERATION`

- **Kind:** `MECHANICAL_FAMILY` / general capability
- **Status:** `PROPOSED-CLEAR` as mechanics; not a universal deck-skeleton requirement
- **Meaning:** creates one or more token objects with represented characteristics.
- **Facets:** token type/object class, quantity, controller, timing, tapped/attacking, duration, copy/reference identity.

## 78. `EVASION`

- **Kind:** `GENERAL_FUNCTION` / combat capability
- **Status:** `PROPOSED-CLEAR` as aggregate if needed later
- **Meaning goal:** makes a creature harder or impossible to block under represented conditions.
- **Not universal deck component.**

## 79. `DIRECT_DAMAGE`

- **Kind:** `MECHANICAL_FAMILY`
- **Status:** `PROPOSED-CLEAR`
- **Meaning:** source/path deals represented damage directly to defined target/object/player classes.
- **User alias:** Burn only where strategy/community context warrants; Burn itself may mean strategy.

## 80. `LIFE_GAIN`, `LIFE_LOSS`, `LIFE_DRAIN`

- **Kind:** mechanical/general capabilities
- **Status:** `PROPOSED-CLEAR` as exact effects; not universal skeleton components.
- **Keep effects separate:** gain life; cause life loss; transfer-style gain+loss linkage.

## 81. `SACRIFICE_OUTLET`

- **Kind:** `DECK_ROLE_RELATIONAL` plus objective sacrifice-cost capability
- **Status:** `DEFERRED`
- **Reason:** "outlet" means a repeatably/voluntarily accessible way for the controller to sacrifice a resource, but strategic value depends on deck plan. Preserve exact sacrifice-as-cost capability first.

## 82. Other later mechanical families

Keep available for later vocabulary without treating them as minimal universal components:

- discard outlet;
- self-mill;
- mill opponent;
- fog/combat prevention;
- haste granting;
- combat tricks;
- copy/clone;
- cheat-into-play;
- untap;
- proliferate;
- counter manipulation;
- theft;
- anthem/stat boost;
- go-wide/go-tall metrics;
- landfall or other strategy-specific event families;
- sacrifice/death triggers;
- stax/prison strategies.

---

# PART VII — TERMS THAT MUST NOT BECOME PRIMITIVE TAGS

## 83. `VALUE`

- **Status:** `REJECT-AS-PRIMITIVE`
- **Reason:** can mean card gain, mana efficiency, board development, repeated triggers, tempo, life, synergy, favorable trade, or strategic usefulness.

## 84. `UTILITY`

- **Status:** `REJECT-AS-PRIMITIVE`
- **Reason:** means useful secondary/situational function; no stable membership boundary.

## 85. `CONSISTENCY`

- **Kind:** `DECK_METRIC`
- **Status:** `METRIC-ONLY`
- **Inputs may include:** redundancy, access, selection, tutor density, mana reliability, curve, command-zone availability.

## 86. `REDUNDANCY`

- **Kind:** `DECK_METRIC` / package relation
- **Status:** `METRIC-ONLY`
- **Meaning:** number/diversity of independent sources able to satisfy the same declared need.
- **Never tag a card:** `REDUNDANT=true` in isolation.

## 87. `RESILIENCE`

- **Kind:** `DECK_METRIC`
- **Status:** `METRIC-ONLY`
- **Potential contributors:** protection, recovery, redundancy, alternate lines, resource diversity.

## 88. `FLEXIBILITY` / `VERSATILITY`

- **Kind:** `CARD_METRIC` / `DECK_METRIC`
- **Status:** `METRIC-ONLY`
- **Potential inputs:** mode count, co-availability, target-domain breadth, timing, alternative costs, number of distinct functions.
- **Do not replace exact capabilities with a vague flexible tag.**

## 89. `TEMPO`

- **Kind:** game-state/resource metric
- **Status:** `DEFERRED` / not Objective6 primitive
- **Reason:** depends on board position, timing, resource exchange, and opponent state.

## 90. `INEVITABILITY`

- **Kind:** matchup/game-state relation
- **Status:** `RELATIONAL-ONLY`
- **Not a card-global function.**

## 91. `REACH`

- **Kind:** strategy/game-state relation (distinct from the Reach keyword)
- **Status:** `RELATIONAL-ONLY` as strategy jargon
- **Reason:** strategy-jargon meaning is ability to finish a wounded opponent from otherwise stalled position; context-dependent and collides with official keyword `reach`.

## 92. `CARD_FLOW`

- **Kind:** `AGGREGATE_VIEW`
- **Status:** `ALIAS-ONLY`
- **Meaning:** product grouping over exact draw/access/selection/resource-generation mechanisms.

## 93. `BOARD_PRESENCE`

- **Kind:** game-state metric
- **Status:** `METRIC-ONLY`
- **Not a card-global function.**

---

# PART VIII — CORE DECKBUILDING SURFACE AFTER CANONICALIZATION

## 94. Minimal high-confidence deck skeleton

The external census repeatedly converges on the following user-facing areas. Internally they map to exact concepts rather than one loose tag per heading.

### 94.1 Mana / structure

```text
Mana Base                 -> DECK_STRUCTURE
Land Base                 -> DECK_STRUCTURE
Mana Curve                -> DECK_METRIC
Mana Fixing               -> MANA_FIXING
Ramp                      -> DURABLE_MANA_ACCELERATION [Captain direction pending ratification]
Fast Mana                 -> FAST_MANA [OPEN accounting]
Mana Sink                 -> EXCESS_MANA_OUTLET
```

### 94.2 Cards / access

```text
Draw                      -> DRAW
Card Selection            -> CARD_SELECTION
Card Filtering            -> alias/view over selection families
Card Advantage            -> PERSONAL_CARD_RESOURCE_ADVANTAGE [OPEN accounting]
Card Parity               -> CARD_RESOURCE_PARITY [OPEN accounting]
Cantrip                   -> SELF_REPLACING_DRAW_EFFECT
Tutor                     -> alias for LIBRARY_SEARCH
Top-N / deep selection    -> TOP_N_SELECTION
Impulse Draw              -> TEMPORARY_EXILE_ACCESS
```

### 94.3 Answers

```text
Interaction               -> AGGREGATE VIEW
Spot Removal              -> SPOT_REMOVAL
Edict/random single       -> NONSELECTIVE_SINGLE_REMOVAL
Multi-removal             -> SELECTIVE_MULTI_REMOVAL
Mass Removal              -> MASS_REMOVAL
Board Wipe / Wrath        -> alias/view over qualifying MASS_REMOVAL
Neutralization            -> NEUTRALIZATION
Counterspell              -> COUNTERSPELL
Ability Counter           -> ABILITY_COUNTER
Stack Interaction         -> aggregate view
Graveyard Hate            -> GRAVEYARD_DENIAL
Hand Disruption           -> aggregate over exact hand mechanisms
Silence/restrictions      -> CAST_OR_ACTION_RESTRICTION
Taxes                     -> TAX_OR_COST_INCREASE
```

### 94.4 Defense / continuity

```text
Protection                -> PROTECTION_FUNCTION
Recursion                 -> alias/view over GRAVEYARD_ACCESS
Reanimation               -> CREATURE_REANIMATION / GRAVEYARD_TO_BATTLEFIELD
Blink/Flicker             -> BLINK
```

### 94.5 Closing plan

```text
Wincon                    -> WIN_CONDITION [DECK-RELATIONAL]
Finisher                  -> FINISHER [DECK-RELATIONAL]
Threat                    -> THREAT [GAME/DECK-RELATIONAL]
Explicit win text         -> EXPLICIT_WIN_EFFECT [OBJECTIVE MECHANIC]
```

---

# PART IX — AMBIGUITY COLLISIONS THAT ARE NOW EXPLICITLY BLOCKED

## 95. Blocked collision table

| Ambiguous familiar term | Problem | Registry resolution |
|---|---|---|
| Ramp | Often means any acceleration; Captain means durable acceleration | Internal `DURABLE_MANA_ACCELERATION`; UI may say Ramp |
| Mana fixing | Often lumped into ramp | Independent `MANA_FIXING` |
| Mana sink | Sometimes means any expensive card | `EXCESS_MANA_OUTLET`: optional/scalable/repeatable extra-mana use |
| Draw | Often used for all card access | `DRAW` only literal draw action |
| Card filtering | Used for many selection mechanisms | Alias/view over exact `CARD_SELECTION` children |
| Card advantage | Established term is relative to opponents; project wants personal resource gain | `PERSONAL_CARD_RESOURCE_ADVANTAGE`; relative model deferred |
| Cantrip | Project had broadened beyond draw | `SELF_REPLACING_DRAW_EFFECT`; broader low-cost parity gets separate term |
| Impulse | Wizards uses both impulsive draw and top-N impulsing | Internal `TEMPORARY_EXILE_ACCESS`; `TOP_N_SELECTION` separate |
| Tutor | Sometimes stretched to top-N digging | Canonical `LIBRARY_SEARCH`; top-N is `TOP_N_SELECTION` |
| Interaction | Covers too many mechanisms | Aggregate view only; exact child mechanisms preserved |
| Removal | Can mean kill, bounce, counter, tap, disable | Battlefield removal mechanisms separated from Neutralization/Stack Interaction |
| Spot removal | Edicts/random effects can remove one but do not let caster pick object | `SPOT_REMOVAL` requires source-controller designation; `NONSELECTIVE_SINGLE_REMOVAL` separate |
| Multi-removal | Cryptic-style multi-answer path collided with true multi-permanent removal | `SELECTIVE_MULTI_REMOVAL` vs `MULTI_INTERACTION` |
| Board wipe / sweeper | Can include direct destroy or state-dependent damage/-X | `MASS_REMOVAL` exact; Sweeper aggregate exposes mechanism |
| Protection | Generic counter can be used protectively | `PROTECTION_FUNCTION` only intrinsic protective structure; generic counters remain Counterspell |
| Graveyard hate | “Hate” is strategic/contextual | `GRAVEYARD_DENIAL` exact mechanisms |
| Recursion | Can mean one-time recovery or repeated loop | `GRAVEYARD_ACCESS` exact mechanisms; Recursion alias only |
| Reanimation | Creature-only in R&D usage; community sometimes broadens | `GRAVEYARD_TO_BATTLEFIELD` parent + `CREATURE_REANIMATION` |
| Win condition | Often treated as intrinsic card property | `WIN_CONDITION` requires deck context |
| Finisher | Depends on deck/state | relational only |
| Engine | Depends on repeated conversion/package | relational/deferred |
| Value | No stable resource domain | rejected as primitive |
| Utility | Means “useful somehow” | rejected as primitive |
| Consistency | Emerges from deck composition/access | metric only |
| Redundancy | Relationship among multiple sources | metric/relation only |
| Resilience | Emergent deck property | metric only |
| Flexibility | Emerges from modes/coverage/timing | metric only |
| Reach | Collides with keyword and strategy jargon | never use bare strategy `REACH` as card-global tag |

---

# PART X — REMAINING CAPTAIN RULINGS BEFORE A ZERO-AMBIGUITY FREEZE

## 96. Rulings still required

The registry has removed terminology ambiguity where possible. The following are genuine semantic choices and must remain `OPEN` rather than being silently decided.

### R1 — Mana Acceleration baseline

Precisely define ordinary baseline and treatment of:

- extra land plays;
- temporary mana;
- sacrifice sources;
- land-play opportunity cost;
- sources that refund their cost;
- sources that enter tapped;
- delayed acceleration.

### R2 — Fast Mana opportunity-cost law

Decide how zero-mana-to-deploy lands are evaluated when they consume a land play.

### R3 — Mana Parity accounting window

Freeze the time horizon and charged resources.

### R4 — Personal Card Resource accounting

Freeze:

- what zones count as usable card resources;
- temporary exile access valuation;
- source expenditure;
- battlefield permanent value, if any;
- time horizon.

### R5 — Conditional/Potential Card Advantage

Decide whether this is:

1. a named child class; or
2. one Advantage capability plus dependency facets.

Recommendation: option 2 unless a benchmark proves a named child materially improves retrieval/UX.

### R6 — Low Cost Card Parity

Decide whether the broader former-Cantrip product concept is worth retaining and, if yes, its cost/resource rules.

### R7 — Removal from damage/toughness modification

Ratify whether deck-health `Spot Removal` should aggregate state-dependent lethal mechanisms (Bolt, -X/-X, fight) or expose them as a separate narrower/removal-capable family.

Recommendation: preserve both lower mechanism classes and let UI aggregate with reliability/magnitude visible.

### R8 — Board Wipe presentation boundary

Decide whether UI Board Wipe includes broad damage/-X/-X sweepers or only direct Mass Removal. Internal representation is already separated either way.

### R9 — Protection rescue mechanisms

Decide whether self-bounce/blink/phasing used to save one's permanent should all imply Protection Function, or remain separate mechanisms aggregated only downstream.

### R10 — Graveyard Access parent

Confirm that `GRAVEYARD_ACCESS` replaces broad internal `RECURSION`, with Recursion as user alias.

### R11 — Reanimation breadth

Confirm creature-specific `CREATURE_REANIMATION` and broader `GRAVEYARD_TO_BATTLEFIELD` rather than using Reanimation for all permanent types.

### R12 — Mana Sink inclusion in initial core surface

It is a stable cross-strategy function and official Magic term, but unlike ramp/draw/removal it is not present in every common Commander skeleton. Decide whether it ships in Objective6 v1 or remains a high-confidence secondary function.

---

## 97. Zero-ambiguity freeze rule

Objective 6 should not be considered terminology-frozen until every `OPEN` item that affects a v1 term is either:

1. ratified with an exact rule and adversarial fixtures; or
2. removed/deferred from v1.

A vague term is never made safe by attaching more prose to it. If two reasonable readers can assign different cards while following the same wording, the contract is not finished.

The final standard should be:

> **One canonical concept → one exact meaning → explicit context → explicit exclusions → explicit facets → explicit provenance → reproducible membership.**

That allows Foundry to retain the language Magic players already understand while preventing community slang, product shorthand, or historical vocabulary drift from becoming hidden semantic debt.
