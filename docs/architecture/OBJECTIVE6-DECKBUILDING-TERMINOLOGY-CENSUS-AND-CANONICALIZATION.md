# Objective 6 — General Deckbuilding Terminology Census and Canonicalization Audit

**Status:** RESEARCH / CAPTAIN REVIEW / NON-EXECUTING / NOT RATIFIED  
**Date:** 2026-09-14  
**Objective:** 6 — `FOUNDRY_FUNCTIONAL_VOCABULARY_SPECIFICATION`  
**Companion:** `docs/architecture/OBJECTIVE6-FUNCTIONAL-VOCABULARY-AND-DECK-HEALTH-DRAFT.md`  
**Branch:** `architecture/objective6-functional-vocabulary-2026-09-13`  
**Implementation authorization:** **NONE.** This document is terminology research and a proposed canonicalization pass. It does not authorize S16A/S16B implementation, codebook mutation, parser changes, merge, deployment, AQ4, Bridge v0, or semantic production writes.

---

## 1. Why this audit exists

The first Objective 6 pass produced a useful functional architecture, but familiar Magic words are not automatically precise enough to become Foundry law.

The goal of this pass is therefore not merely to find more labels. It is to answer four different questions:

1. Which terms repeatedly appear as **general deckbuilding components** across independent Commander sources?
2. Which terms are useful to players but too ambiguous to serve as executable semantic predicates?
3. Which current Objective 6 terms collide with established Magic usage?
4. What exact internal vocabulary would let Foundry preserve familiar user-facing language without inheriting its ambiguity?

The governing rule is:

> **Community terminology is discovery evidence. Foundry canonical terms must have one meaning, one boundary, and an explicit relationship to lower S16A facts.**

A familiar label may be kept as a UI alias even when a more explicit internal canonical name is needed.

---

## 2. Research basis

This pass sampled several independent kinds of sources rather than adopting one deckbuilding template.

### 2.1 Current deck-skeleton data

Playgroup.gg currently reports a measured Commander deck template over more than 122,000 tracked full decks. Its ten recurring categories are:

- Lands
- Ramp
- Card draw
- Targeted removal
- Board wipes
- Counterspells
- Protection
- Tutors
- Recursion
- Graveyard hate

Source: https://playgroup.gg/commander/deck-template

The important evidence is the **category convergence**, not the recommended quantities. Objective 6 should not turn population averages into semantic law.

### 2.2 EDHREC general deckbuilding guide

EDHREC's current general guide organizes deck construction around:

- Win Conditions
- Mana Acceleration / Ramp
- Card Velocity / Card Draw
- Interaction
- Lands
- Recursion
- Tutors
- Hate cards

It further separates point/targeted removal, wraths/board wipes, protection, and counterspells inside interaction.

Source: https://edhrec.com/guides/how-to-build-a-commander-deck

### 2.3 Deckbuilder/community category convergence

Archidekt decklists, TappedOut guides, current community templates, and other deckbuilding tools repeatedly use combinations of:

- lands / mana base;
- ramp;
- draw;
- removal;
- wipes;
- counters;
- protection;
- tutors;
- recursion;
- graveyard hate;
- win conditions / finishers;
- strategy/theme slots.

One useful TappedOut deckbuilding guide explicitly identifies the original generic categories as strategy, lands, ramp, draw, and removal, then notes common additions including board wipes, targeted removal, recursion, graveyard hate, protection, utility, value, and win conditions.

Source: https://tappedout.net/mtg-articles/2020/apr/25/edh-deck-building-process-5-cutting-cards/

### 2.4 Wizards / established Magic terminology

Wizards and established Magic terminology provide useful collision checks:

- **Cantrip**: Wizards describes cantrips as small spell effects with card draw attached; established usage centers on a spell replacing itself with a drawn card.
  - https://magic.wizards.com/en/news/making-magic/drawing-attention-2013-10-14
  - https://magic.wizards.com/en/news/making-magic/cantrip-down-memory-lane-2006-07-31
- **Tutor**: Wizards uses tutoring for library search/retrieval effects and also discusses limited-depth top-N tutoring.
  - https://magic.wizards.com/en/news/making-magic/mechanical-color-pie-2017-2017-06-05
  - https://magic.wizards.com/en/news/making-magic/building-foundations-something-old
- **Mana acceleration versus mana fixing**: established jargon distinguishes getting ahead on available mana from obtaining the correct colors.
  - https://blog.cardkingdom.com/mtg-definitions-community-jargon/
- **Graveyard recursion**: Wizards repeatedly uses recursion for getting resources back from graveyards.
  - https://magic.wizards.com/en/news/making-magic/cmon-innistrad-part-2-2011-09-11
- **Reanimation**: established usage centers on moving cards, especially creatures/permanents, directly from graveyard to battlefield.
- **Spot removal**: Wizards glossary usage is targeted removal of one opposing creature; broader community usage extends the object class but retains the one-selected-object idea.
  - https://magic.wizards.com/en/news/feature/glossary-of-terms
- **Hate card**: Wizards defines a hate card by its relationship to stopping a particular card/mechanic/strategy, which makes `HATE` intrinsically contextual rather than a clean mechanical predicate.
  - https://magic.wizards.com/en/news/making-magic/few-more-words-rd-2016-11-07

### 2.5 Research conclusion

The external evidence strongly supports a stable **general deck skeleton**, but it also confirms that many labels collapse multiple meanings.

The right architecture is therefore:

```text
FAMILIAR USER TERM
        ↓ alias / presentation
FOUNDRY CANONICAL CONCEPT
        ↓ exact contract
S16A FACTS + FACETS + PROVENANCE
```

---

## 3. Proposed semantic-kind registry

Every candidate term should first be assigned a kind. This prevents a deck property, a card function, a strategy, and a slang label from being treated as equivalent tags.

### 3.1 `DECK_STRUCTURE`

A property of deck construction rather than a card's functional job.

Examples:

- mana base;
- land count;
- color-source count;
- mana curve;
- average mana value;
- commander slot;
- library-bound versus command-zone-accessible source.

### 3.2 `GENERAL_FUNCTION`

A cross-strategy job a card/effect can perform.

Examples:

- mana fixing;
- mana acceleration;
- removal;
- protection;
- tutoring;
- card selection;
- graveyard denial.

### 3.3 `MECHANICAL_FAMILY`

A recognizable implementation family with objective mechanical boundaries.

Examples:

- mana rock;
- mana creature / mana dork;
- ritual;
- blink;
- reanimation;
- looting;
- rummaging.

### 3.4 `ACCOUNTING_FUNCTION`

A functional label requiring a declared resource domain and accounting window.

Examples:

- mana parity;
- card-resource parity;
- personal card-resource advantage.

### 3.5 `AGGREGATE_VIEW`

A useful UI/report grouping that should not itself substitute for the exact underlying capability.

Examples:

- interaction;
- defensive interaction;
- stack interaction;
- card flow.

### 3.6 `DECK_ROLE_RELATIONAL`

A role that cannot be proven from a card in isolation because it depends on deck plan, other cards, metagame, or game state.

Examples:

- win condition;
- finisher;
- threat;
- engine;
- enabler;
- payoff;
- synergy piece;
- support card.

### 3.7 `DECK_METRIC`

A measured property of a deck or package, not a card function.

Examples:

- consistency;
- redundancy;
- resilience;
- flexibility;
- efficiency;
- density;
- breadth;
- concentration;
- coverage.

### 3.8 `STRATEGY`

A plan/archetype pursued by the deck.

Examples:

- Reanimator;
- Tokens;
- Voltron;
- Aristocrats;
- Spellslinger;
- Lands;
- Stax;
- Burn;
- Combo.

---

## 4. High-confidence general deckbuilding component census

The repeated cross-source skeleton suggests the following broad areas are worth explicit Objective 6 treatment.

### 4.1 Mana infrastructure

- Mana Base — `DECK_STRUCTURE`
- Land / land slot — `DECK_STRUCTURE`
- Mana Source — `GENERAL_FUNCTION` or lower fact/facet
- Color Source — `DECK_STRUCTURE` measurement over sources
- Mana Fixing — `GENERAL_FUNCTION`
- Mana Acceleration — `GENERAL_FUNCTION`
- Ramp / durable acceleration — current Captain-defined `GENERAL_FUNCTION`
- Fast Mana — `GENERAL_FUNCTION` / accounting threshold
- Land Ramp — `MECHANICAL_FAMILY`
- Extra Land Play / current `LAND_ADD` — `GENERAL_FUNCTION`
- Mana Rock — `MECHANICAL_FAMILY`
- Mana Creature / Mana Dork — `MECHANICAL_FAMILY`
- Ritual — `MECHANICAL_FAMILY`
- Cost Reduction — separate `GENERAL_FUNCTION`; not mana production
- Mana Parity — `ACCOUNTING_FUNCTION`

### 4.2 Card-resource and card-selection infrastructure

- Draw — literal rules action / `GENERAL_FUNCTION`
- Immediate Draw
- Delayed Draw
- Card Selection — `GENERAL_FUNCTION`
- Looting — `MECHANICAL_FAMILY`
- Rummaging — `MECHANICAL_FAMILY`
- Scry — rules/mechanical family
- Surveil — rules/mechanical family
- Top-library manipulation — mechanical family / facet
- Impulse Access — temporary exile-to-play access family
- Tutor — `GENERAL_FUNCTION`
- Limited-depth Tutor / Top-N Tutor — child/facet of Tutor
- Card-resource parity — `ACCOUNTING_FUNCTION`
- Personal card-resource advantage — `ACCOUNTING_FUNCTION`
- Conditional card-resource advantage — dependency-qualified accounting function
- Cantrip — established Magic mechanical/slang family; definition must not be broadened casually
- Low-cost card parity/access — separate candidate for the broader product concept previously called Cantrip

### 4.3 Opponent-facing interaction

- Removal — `GENERAL_FUNCTION`
- Spot Removal — one selected battlefield permanent
- Selective Multi-removal — several individually selected battlefield permanents
- Mass Removal — set-based battlefield removal
- Board Wipe / Sweeper / Wrath — familiar presentation aliases for qualifying mass removal
- One-sided Board Wipe — player-scope-qualified mass removal
- Neutralization — disables/locks without removing the object
- Counterspell — spell-stack interaction
- Ability Counter — ability-stack interaction
- Redirect / Retarget — stack interaction mechanism
- Hand Disruption — opponent-hand resource interaction
- Graveyard Denial — canonical umbrella proposed for the mechanically diverse family colloquially called Graveyard Hate
- Land Interaction — coverage domain, usually lower action + object facet
- Cast/Action Restriction — Silence/prohibition family
- Tax / Cost Increase — resource restriction family

### 4.4 Defensive continuity

- Protection — `GENERAL_FUNCTION`
- Damage Prevention — mechanical family
- Defensive keyword granting — hexproof/indestructible/ward/protection, preserved as exact facets/families
- Phasing / temporary evasion from interaction — mechanical family; may satisfy Protection
- Recursion / Recovery — general resilience/reuse family
- Reanimation — graveyard-to-battlefield child

### 4.5 Deck plan / closing category

Community deckbuilders repeatedly use:

- Win Condition / Wincon
- Finisher
- Threat

These are genuinely important deckbuilding concepts, but they **do not belong in the same semantic class as Ramp or Spot Removal** because they usually require deck context.

Recommendation:

- retain them in the Objective 6 terminology registry;
- classify them as `DECK_ROLE_RELATIONAL`;
- do not assign `WINCON=true` to a card globally merely because it often closes games in some decks;
- separately preserve literal mechanical win/loss effects as objective capabilities.

---

## 5. First critical correction: Removal must be separated from generic Interaction

The current Objective 6 draft says Spot Removal can "remove, neutralize, or otherwise interact" with one selected object. That phrase is too broad to be executable without ambiguity.

### 5.1 Proposed canonical parent: `BATTLEFIELD_INTERACTION`

A broad presentation/aggregate family for effects operating on battlefield permanents.

This should not erase the action/result distinction below.

### 5.2 Proposed canonical `REMOVAL`

**Exact proposed meaning:**

> A legal effect/path whose direct or rule-mandated immediate consequence causes a battlefield permanent to cease being a battlefield permanent.

Qualifying result classes can include, when S16A proves the transition:

- destruction;
- exile;
- return to hand;
- return to library;
- sacrifice caused by the effect;
- lethal damage or toughness reduction when departure from battlefield is the immediate rules consequence represented by the semantic path.

Does **not** qualify merely because the permanent is:

- tapped;
- unable to attack/block;
- unable to activate abilities;
- stripped of abilities;
- controlled by another player;
- taxed;
- prevented from untapping;
- phased out temporarily, unless Captain deliberately decides phasing should be treated as temporary removal for a separate product view.

Those are interaction/neutralization mechanisms, not strict `REMOVAL`.

### 5.3 `SPOT_REMOVAL`

**Proposed exact meaning:**

> A qualifying `REMOVAL` path that specifically designates exactly one battlefield permanent for removal.

`designates` can be implemented by target, choice, or another precise S16A selection relation. It need not literally use the rules word "target."

Required:

- object is a battlefield permanent;
- one individually designated affected permanent;
- qualifying removal result.

Hard negatives:

- Counterspell — object is a spell on stack, not a battlefield permanent;
- Pacifism — permanent remains on battlefield;
- Sleep — permanents remain on battlefield;
- Naturalize with multiple legal target types still removes only one object and therefore remains Spot Removal.

### 5.4 `SELECTIVE_MULTI_REMOVAL`

This should replace ambiguous internal use of bare `MULTI_REMOVAL`.

**Proposed exact meaning:**

> A single legal path that can cause two or more distinct, individually designated battlefield permanents to satisfy `REMOVAL`.

Properties:

- threshold is `>= 2`;
- no maximum ceiling;
- affected objects are selected individually rather than solely by belonging to an exhaustive set;
- all counted objects must satisfy strict Removal.

Gold positives:

- Curse of the Swine with a legal X >= 2;
- Hex.

### 5.5 `MULTI_INTERACTION`

New proposed concept needed to preserve the Captain's Cryptic Command intuition without corrupting Removal.

**Proposed exact meaning:**

> One legal path can individually affect/answer two or more distinct game objects/actions, whether or not every affected item is a battlefield permanent or every result is Removal.

Example:

- Cryptic Command choosing counter target spell + return target permanent can qualify as `MULTI_INTERACTION`.
- It should **not** qualify as `SELECTIVE_MULTI_REMOVAL` on that path, because one affected object is a spell on the stack and countering it is not battlefield removal.

This split removes a real ambiguity in the current draft.

### 5.6 `MASS_REMOVAL`

**Proposed exact meaning:**

> A Removal path whose affected battlefield set is defined by a game-state predicate or player scope rather than by individually selecting every affected permanent.

Examples:

- destroy all creatures;
- exile all artifacts;
- return all nonland permanents to their owners' hands;
- destroy all creatures you don't control.

### 5.7 `BOARD_WIPE`

Recommended status: **user-facing familiar alias/subfamily of `MASS_REMOVAL`**, not a second competing rule.

Proposed Foundry contract:

> `BOARD_WIPE` is mass removal over an unbounded matching battlefield class within its declared player scope.

This excludes effects such as "destroy up to three creatures" because those are bounded/selective rather than wipes.

### 5.8 `ONESIDED_BOARD_WIPE`

Child of `BOARD_WIPE` where the affected player/controller scope excludes the source's controller's matching battlefield objects while affecting opposing matching objects.

Ruinous Ultimatum remains the gold-standard example.

### 5.9 `NEUTRALIZATION`

Needed because the old definition was using "neutralizes" as if it were removal.

**Proposed exact meaning:**

> An effect/path materially suppresses a permanent's relevant game functionality while the permanent remains on the battlefield.

Candidate mechanisms include:

- cannot attack/block;
- ability loss;
- activation prohibition;
- cannot untap / sustained tap lock;
- transformation into a materially disabled object where S16A can prove the suppression.

Neutralization should retain duration and scope facets and must not silently count as strict Removal.

---

## 6. Second critical correction: `CANTRIP` cannot carry the current broad Foundry meaning

Wizards' own terminology and broad community usage center **cantrip** on a spell/effect that draws a card while doing something else, thereby replacing the spent card.

The current Objective 6 draft broadens Cantrip to include:

- non-draw card selection into hand;
- Wrenn's Resolve-style temporary exile access;
- qualifying Cycling;
- any immediate usable card resource at cost <= 2 that replaces the expenditure.

That is a useful **product concept**, but it is not a safe canonical meaning for the established term `CANTRIP`.

### 6.1 Proposed `CANTRIP`

**Exact proposed meaning:**

> A spell/effect that includes a qualifying draw-one replacement component in addition to its principal/minor effect, such that the card expenditure is replaced in the card-resource domain.

Preserve:

- literal Draw fact;
- timing (immediate or legacy delayed/slowtrip if retained);
- card parity accounting;
- mana cost as a facet rather than silently redefining the word around one exact cost ceiling unless Captain deliberately wants a product threshold.

### 6.2 Proposed replacement for the broader current concept: `LOW_COST_CARD_PARITY`

Working internal name; Captain should choose final display name.

**Exact intended concept:**

> A card/action with an intrinsic effective printed/deployed cost at or below the ratified threshold whose own path immediately restores at least the card resource spent to use it, regardless of whether that access is implemented by literal draw, selected card-to-hand, Cycling, or bounded temporary play permission.

Under the current Captain threshold, `cost <= 2` remains candidate law.

This broader concept can include:

- Ponder;
- Brainstorm;
- qualifying Cycling;
- Wrenn's Resolve-style access if the accounting contract says the resulting temporary access counts as a usable card resource.

The important change is **not using established `CANTRIP` as the internal name for that broader class**.

---

## 7. Third critical correction: traditional `CARD_ADVANTAGE` and the current Foundry accounting concept are not identical

In general Magic theory, `card advantage` can include both:

- increasing your own card resources; and
- decreasing opponents' card resources efficiently, e.g. a two-for-one removal exchange or board wipe.

The current Objective 6 definition is intentionally focused on a different, useful question:

> Does this source produce net-positive **usable card resources for its controller**?

That is closer to deckbuilding's "draw/resources" package than to every traditional use of the phrase card advantage.

### 7.1 Proposed internal canonical name: `PERSONAL_CARD_RESOURCE_ADVANTAGE`

**Exact proposed meaning:**

> Within the declared accounting window, after charging the source expenditure specified by the contract, the source/path produces a net increase of at least one usable card resource for its controller.

This does not count opponent resource losses.

A UI may still show **Card Advantage** if the product clearly documents that Foundry means personal card-resource generation in this panel.

### 7.2 Proposed `CARD_RESOURCE_PARITY`

> Within the same accounting domain/window, the source restores exactly the usable card resource charged to it, producing net delta 0.

### 7.3 Do not silently use relative card advantage

`RELATIVE_CARD_ADVANTAGE` should be reserved for a future game-state/economic model comparing resource changes across players.

It is not the same fact as personal card-resource generation.

### 7.4 Current `POTENTIAL_CARD_ADVANTAGE` still needs a dependency split

The current examples show the intended distinction, but the word *potential* is too broad by itself.

Recommended representation:

```text
PERSONAL_CARD_RESOURCE_ADVANTAGE capability
+ dependency facets
```

Candidate dependency facets:

- `SELF_STARTING` / automatic scheduled trigger;
- `CONTROLLER_ACTION_DEPENDENT`;
- `OPPONENT_ACTION_DEPENDENT`;
- `BOARD_STATE_DEPENDENT`;
- `COMBAT_DEPENDENT`;
- `PAYMENT_DEPENDENT`;
- `DELAYED`;
- `REPEATABLE`;
- `RATE_LIMITED`.

If Captain wants a named second class, a more explicit internal term such as `CONDITIONAL_CARD_RESOURCE_ADVANTAGE` is safer than bare `POTENTIAL_CARD_ADVANTAGE`.

The exact Sram / Phyrexian Arena / Rhystic Study boundary remains a required adversarial decision before ratification.

---

## 8. Card selection terminology

External terminology consistently distinguishes **card quantity** from **card quality/selection**.

### 8.1 `DRAW`

Keep as literal Magic rules action only.

Do not label exile access, putting a card into hand without drawing, or graveyard retrieval as Draw.

### 8.2 `CARD_SELECTION`

Recommended canonical umbrella.

**Exact proposed meaning:**

> A path gives the controller meaningful choice or deterministic manipulation over which candidate card(s) will become accessible, remain accessible, or be encountered next, without requiring a net increase in card quantity.

This can encompass mechanical families while preserving their differences.

### 8.3 `CARD_FILTERING`

Recommendation: do not use as the only internal umbrella unless Captain gives it a narrower contract.

Community usage varies. It can mean looting/rummaging, scry/surveil, cantrips, or generally improving draw quality.

Safer options:

- use `CARD_SELECTION` as canonical parent;
- keep **Card Filtering** as a user-facing alias/group;
- define narrower children by actual operation.

### 8.4 `LOOT`

Proposed exact mechanical family:

> Draw N, then discard M as part of the linked operation, with draw preceding discard.

Store N/M independently; do not assume equality.

### 8.5 `RUMMAGE`

Proposed exact mechanical family:

> Discard M, then draw N as part of the linked operation, with discard preceding draw.

The order difference must remain semantic, not cosmetic.

### 8.6 `TOP_LIBRARY_MANIPULATION`

Use for reordering/top-bottom manipulation that does not itself transfer a card into a usable zone.

This is a clearer internal family than a project-only word such as `INDEX` unless Captain specifically wants `INDEX` as UI shorthand.

### 8.7 Scry and Surveil

Keep their actual rules identities. They may imply Card Selection but should not be flattened into one operation because destination differs.

---

## 9. Impulse terminology

The external census is unusually consistent here:

> **Impulse draw / impulsive draw** commonly means exiling top card(s) and granting a bounded window in which they may be played/cast.

The phrase is familiar but it is explicitly **not literal Draw**.

### 9.1 Proposed internal canonical term: `IMPULSE_ACCESS`

**Exact proposed meaning:**

> A path moves/reveals candidate card(s), normally from the top of a library into exile, and grants bounded permission to play/cast those card(s) from that zone.

Required facets:

- source library / player;
- destination zone;
- number of cards;
- play versus cast permission;
- allowed card types;
- permission start;
- permission expiration;
- whether unused cards remain exiled or move elsewhere;
- whether mana may be spent as though any color.

### 9.2 Do not create semantic children solely from slang names

Instead of `IMPULSE_DRAW` versus `IMPULSE_SELECT` names whose meanings can drift, encode the timing window explicitly:

```text
IMPULSE_ACCESS
  window_end = END_OF_CURRENT_TURN

IMPULSE_ACCESS
  window_end = END_OF_NEXT_TURN
```

The UI can render friendly distinctions later.

---

## 10. Tutor terminology

### 10.1 `TUTOR`

Wizards itself uses Tutor for library retrieval, including constrained subsets and limited-depth variants.

**Proposed exact meaning:**

> A path deliberately selects one or more card(s) from a library search/inspection domain according to identity or stated criteria and moves or exposes the selected card(s) into a declared destination/access state.

Required facets:

- full library versus top-N/limited-depth domain;
- criteria/object class;
- destination zone;
- reveal requirement;
- shuffle behavior;
- card count;
- optionality;
- whether the selected card becomes immediately usable.

### 10.2 Multi-labeling is correct

A Rampant Growth-like effect may be both:

- `TUTOR` for a land under the broad library-retrieval meaning; and
- `LAND_RAMP` because the selected land enters the battlefield.

Those are different facts and should not compete.

### 10.3 Replace `ALT_TUTOR` / `LIGHT_TUTOR` with explicit mechanics internally

Recommended candidate:

- `LIMITED_DEPTH_TUTOR` or `TOP_N_TUTOR` for searching/choosing only within a bounded top-N domain.

A friendlier UI alias can exist later. The internal contract should say what is bounded rather than imply weaker power with the word "light."

---

## 11. Mana terminology

### 11.1 `MANA_BASE`

Kind: `DECK_STRUCTURE`.

Recommended meaning:

> The collection of deck slots and always/conditionally accessible sources relied upon to satisfy land drops and/or produce the mana/colors required to execute the deck.

For initial reporting, distinguish physical land slots from nonland mana sources instead of forcing one count.

### 11.2 `MANA_SOURCE`

> A card/object/path that can produce mana under its represented legal conditions.

Preserve amount, colors, cost, tap/sacrifice requirements, timing, repeatability, and conditionality.

### 11.3 `COLOR_SOURCE`

Deck-analysis concept over `MANA_SOURCE` facts:

> A source that can produce a specified color under the declared availability assumptions.

`Sol Ring` is a mana source but not a colored source.

### 11.4 `MANA_FIXING`

**Proposed exact meaning:**

> A source/path improves access to required mana colors or converts available resources into a more useful color distribution, without requiring an increase in total mana quantity.

Fixing and acceleration may overlap, but neither implies the other.

### 11.5 `MANA_ACCELERATION`

Current Captain parent can be tightened to:

> A source/path creates a legal route to greater usable mana-producing capacity earlier than the declared ordinary one-land-per-turn baseline would provide, excluding external effects not supplied by the source/path.

The final ratified contract must state whether cost reduction is inside or outside this family. Recommendation: keep **Cost Reduction separate**, because it changes expenditure rather than producing mana/capacity.

### 11.6 `RAMP`

Current Captain direction intentionally differs from some community usage, where Ramp and Mana Acceleration are often synonyms and rituals/temporary mana may be counted as ramp.

To preserve the Captain ruling **without ambiguity**, recommended internal meaning is:

> `RAMP` = durable/repeatable mana acceleration that establishes or advances a continuing mana-producing resource across turns.

Because the community meaning is broader, consider an internal slug such as `DURABLE_RAMP` even if the UI label remains **Ramp**.

### 11.7 `LAND_RAMP`

Keep current exact boundary:

> A path obtains a land from the library and puts that land onto the battlefield.

A land placed from graveyard onto battlefield is recursion/resource recovery, not `LAND_RAMP` under this contract.

### 11.8 `EXTRA_LAND_PLAY`

Recommended canonical internal name for current `LAND_ADD`.

> Grants permission/capacity to make additional land play(s) beyond the normal allowance.

This is conditional acceleration potential because it still requires a land to play.

`Land Add` may remain a UI alias if desired.

### 11.9 `MANA_ROCK`

Proposed exact family:

> A nonland artifact permanent with its own repeatably usable mana-producing ability/path.

Exclude artifact lands from the family unless Captain intentionally broadens the term.

Preserve entry/timing constraints and activation costs.

### 11.10 `MANA_CREATURE`

Recommended precise parent:

> A creature permanent with an intrinsic repeatably usable mana-producing ability/path.

### 11.11 `MANA_DORK`

Community alias/narrow child of Mana Creature.

If kept executable, define it explicitly rather than assuming everyone agrees which triggered or attack-based mana creatures count. Recommended v1 restriction:

> A creature whose own activated mana ability can be used repeatedly while it remains a creature permanent.

### 11.12 `RITUAL`

> A one-shot spell/effect that creates temporary/burst mana during its execution without establishing a durable mana source.

A ritual may or may not satisfy Fast Mana depending on the separate Fast Mana threshold.

### 11.13 `FAST_MANA`

Current Captain threshold remains a good candidate but requires one additional accounting clarification.

Working law:

- intrinsic deploy/use cost <= 2 mana;
- qualifying mana is available immediately from the source/path;
- same-turn mana output exceeds the mana spent to deploy/use that source/path;
- external cost reducers/mana doublers do not manufacture membership.

**Open edge case:** a land consumes a land play rather than mana to deploy. The contract must decide whether land-play opportunity cost participates in Fast Mana accounting before cards such as Ancient Tomb/Phyrexian Tower can be graded consistently.

### 11.14 `COST_REDUCTION`

Candidate general function worth preserving separately from mana acceleration.

> Reduces the resource cost required to cast/activate/pay for a defined class of actions without itself producing that mana.

This distinction matters for Searcher B and for deck analysis: a Goblin-spell reducer and a mana rock can both improve cast throughput but are not interchangeable resources.

---

## 12. Interaction terminology

### 12.1 `INTERACTION`

Recommendation: **AGGREGATE VIEW, not primitive executable membership.**

Community sources use Interaction to include various combinations of:

- removal;
- board wipes;
- counters;
- redirects;
- Silence effects;
- protection;
- hate/denial.

Foundry should report an interaction total if useful, but it should always be decomposable into exact mechanisms/domains.

### 12.2 `COUNTERSPELL`

> A path counters a spell on the stack.

Keep facets for:

- spell classes hit;
- unconditional versus conditional;
- payment/tax condition;
- controller restrictions;
- alternative/additional costs.

### 12.3 `HARD_COUNTER` / `SOFT_COUNTER`

If retained:

- Hard Counter — qualifying Counterspell does not require the targeted spell's controller to fail an optional payment/condition and is not restricted to a narrow spell class by the intended contract.
- Soft Counter — success depends on a payment/condition or otherwise has a clearly represented escape clause.

Exact final boundaries need fixtures; community use of "hard" sometimes also means broad target eligibility.

### 12.4 `ABILITY_COUNTER`

> Counters an activated or triggered ability on the stack.

Do not flatten into Counterspell.

### 12.5 `STACK_INTERACTION`

Recommended aggregate over exact stack mechanisms such as:

- Counterspell;
- Ability Counter;
- target redirection;
- copy/control of spell or ability where relevant;
- cast/action restrictions that prevent the stack event from being created.

### 12.6 `HAND_DISRUPTION`

> A path reduces, constrains, reveals-for-selection, or otherwise interferes with an opponent's hand resources.

This umbrella still needs action facets; `DISCARD` should remain the exact removal-from-hand operation.

### 12.7 `GRAVEYARD_DENIAL`

Recommended canonical umbrella replacing executable use of colloquial **Graveyard Hate**.

**Exact proposed meaning:**

> A path prevents or materially reduces another player's ability to retain, enter, target, cast/play, activate, return, or otherwise exploit cards in a graveyard.

Mechanism facets should distinguish:

- targeted graveyard exile;
- whole-graveyard exile;
- all-graveyard exile;
- replacement/exile instead of graveyard entry;
- cast/play prohibition from graveyard;
- activation prohibition in graveyard;
- targeting/access prohibition;
- graveyard shuffle/removal to another zone.

UI alias: **Graveyard Hate**.

This is preferable to `HATE` as semantic law because hate is defined by strategic opposition rather than a single mechanical effect.

### 12.8 Domain interaction belongs mostly in facets

Do not invent a new core label for every object type.

Prefer:

```text
SPOT_REMOVAL
  object_class = artifact

SPOT_REMOVAL
  object_class = enchantment

SPOT_REMOVAL
  object_class = land
```

Then the deck-health UI can render:

- Artifact Interaction
- Enchantment Interaction
- Land Interaction

without duplicating semantic truth.

---

## 13. Protection terminology

`PROTECTION` is another word that can become too broad if every generic counterspell is counted merely because it *can* be used defensively.

### 13.1 Proposed `PROTECTION`

> A source/path is intrinsically structured to preserve the controller/player or their object(s) from a harmful event/state, or directly grants a defensive status that prevents/invalidates such harm.

Candidate mechanisms:

- grant hexproof;
- grant indestructible;
- grant ward;
- grant the Magic keyword protection;
- phase out protected object(s);
- prevent damage;
- regenerate / replacement-like survival where applicable;
- counter a spell/ability **when the counter effect is intrinsically restricted to protecting the controller or their objects**.

### 13.2 Generic Counterspell is not automatically `PROTECTION`

A universal Counterspell can be *used* to protect a permanent, but that use depends on game state and pilot choice.

Recommended rule:

- `COUNTERSPELL = true` from intrinsic capability;
- `PROTECTION = true` only when the card/path itself has protective scope/restriction or directly grants/preserves defensive state;
- downstream strategy/game-state reasoning may later say a generic Counterspell can serve a protective role.

This prevents one broad counterspell from inflating both interaction and protection packages by default.

---

## 14. Recursion / recovery terminology

Community use of `recursion` is broad. Wizards commonly uses graveyard recursion for returning cards/resources from graveyard for reuse, while some community glossaries use recursion for repeated loops.

For Foundry, internal names should describe the zone transition/access rather than rely on the broad word alone.

### 14.1 Proposed parent: `GRAVEYARD_RECOVERY`

> A path restores usable access to a card/resource from a graveyard by moving it to an accessible zone or granting permission to use it from the graveyard.

Required facets:

- whose graveyard;
- object class;
- destination or granted access mode;
- one/many/all;
- immediate/delayed;
- repeatability;
- self-only versus other cards;
- cast/play versus move.

UI alias may remain **Recursion**.

### 14.2 `RETURN_FROM_GRAVEYARD_TO_HAND`

Exact zone-transition child.

### 14.3 `REANIMATION`

Established family:

> A path puts a card from a graveyard directly onto the battlefield.

Because Magic usage sometimes distinguishes creature-only reanimation from any-permanent reanimation, preserve `object_class` rather than forcing that ambiguity into the name.

Possible user-facing distinctions:

- Creature Reanimation
- Permanent Reanimation

### 14.4 `CAST_OR_PLAY_FROM_GRAVEYARD`

Separate access mechanism. A card need not physically move to hand/battlefield before being usable.

### 14.5 Recursion is not Protection

Recovery after loss is resilience/recovery, not prevention of the loss itself. It may contribute to downstream deck resilience but should remain semantically separate from Protection.

---

## 15. Blink / Flicker terminology

External Magic jargon often uses Blink and Flicker interchangeably. Foundry should therefore pick one canonical family and treat the other as alias.

### 15.1 `BLINK`

Keep as canonical if Captain prefers it.

**Proposed exact meaning:**

> A linked path exiles a battlefield permanent/card and later returns that same card from exile to the battlefield under the path's declared timing/control conditions.

Required:

- linked exiled-card identity;
- exile source;
- battlefield return destination;
- return timing;
- return controller;
- any tapped/counter/modified-state conditions.

Does not include:

- phasing;
- bounce to hand followed by an unrelated recast;
- simple exile without linked return;
- reanimation from graveyard.

### 15.2 `BLINK_IMMEDIATE`

Recommended clearer internal name for current `BLINK_NOW`.

> Return is completed in the same resolving semantic sequence/path with no later scheduled game-time event required.

### 15.3 `BLINK_DELAYED`

> Exile establishes a linked later return event.

Keep **Flicker** as alias unless Captain wants a UI distinction; do not invent one mechanically unless the community distinction can be made deterministic.

---

## 16. Win-condition / finisher terminology

Win Conditions clearly belong to general deckbuilding practice, but they are different from global card functions.

### 16.1 `WIN_CONDITION`

Kind: `DECK_ROLE_RELATIONAL`.

> A card/path/package that the specific deck can realistically use as a route to satisfy a game-winning condition.

Context required: `DECK`, usually also strategy/package relationships.

Do not assign globally from the card alone.

Craterhoof Behemoth can be a win condition in a deck that reliably presents a wide creature board; that role is not an intrinsic property of every deck containing Craterhoof.

### 16.2 `FINISHER`

Kind: `DECK_ROLE_RELATIONAL`.

> A card/path expected to convert an already developed favorable resource/board state into a game-ending or near-game-ending state.

This is even more context-sensitive than many general functions.

### 16.3 `THREAT`

Do not make a global functional label in Objective 6.

"Threat" depends on game state, opponent plans, timing, and available answers.

### 16.4 Literal win/loss effects remain objective mechanics

A card that literally states a game-winning or game-losing condition can receive an objective mechanical capability such as:

- `EXPLICIT_WIN_EFFECT`;
- `EXPLICIT_LOSS_EFFECT`;

That is separate from deck-role `WIN_CONDITION`.

---

## 17. Terms that are useful but should NOT become canonical general-function tags

### 17.1 `VALUE`

Reject as executable semantic term.

Reason: can refer to card advantage, mana efficiency, board development, repeated triggers, favorable exchanges, life, tempo, or synergy.

Use exact underlying facts instead.

### 17.2 `UTILITY`

Reject as executable semantic term.

Reason: means "useful in some secondary/situational way" and has no stable mechanical boundary.

### 17.3 `ENGINE`

Defer / relational.

An engine is a system that repeatedly converts inputs/events into resources/effects. Whether a card is an engine often depends on companion pieces or repeated events.

### 17.4 `ENABLER`

Already deferred. Relational: enabler **for what**?

### 17.5 `PAYOFF`

Already deferred. Relational: payoff **for what**?

### 17.6 `SYNERGY PIECE`

Relational and strategy-dependent.

### 17.7 `SUPPORT`

Too broad; usually means "helps the plan."

### 17.8 `GOODSTUFF`

Strategy/deck-construction description, not mechanical function.

### 17.9 `HATE`

Contextual/strategic umbrella. Use exact domain terms such as `GRAVEYARD_DENIAL`, `CAST_RESTRICTION`, `ARTIFACT_REMOVAL`, etc.

### 17.10 `CARD_VELOCITY`

Useful deckbuilding discussion term but not recommended as a canonical Objective 6 card function.

EDHREC uses it broadly enough to include drawing, impulse access, and even self-mill in a graveyard deck. That usefulness depends on what zones the deck can exploit.

Recommendation: treat velocity as a later **deck metric/view over exact access/selection facts**, not one semantic boolean.

### 17.11 `CARD_QUALITY`

Deck/game-state metric, not direct card function.

### 17.12 `CONSISTENCY`

Deck metric produced by density, redundancy, tutors, selection, mana reliability, commander access, curve, and other factors.

### 17.13 `RESILIENCE`

Deck metric. Protection, recursion, redundancy, alternate win paths, and permanent diversity can all contribute.

### 17.14 `REDUNDANCY`

Deck/package metric. Count independent sources rather than tag a card `REDUNDANCY=true`.

### 17.15 `FLEXIBILITY`

Card/deck metric derived from breadth, mode structure, target classes, timing, and opportunity cost.

---

## 18. Terms found in deckbuilding practice but better reserved for strategy/mechanical layers

The following may be valuable to Foundry later but should not be mistaken for universal deck-skeleton requirements:

- Token Generator
- Sacrifice Outlet
- Discard Outlet
- Self-Mill
- Mill
- Evasion
- Haste Granting
- Combat Trick
- Fog
- Lifegain
- Life Drain
- Burn / Direct Damage
- Copy / Clone
- Cheat Into Play
- Cost Reduction
- Untap Engine
- Storm Support
- Proliferate
- Counter Manipulation
- Go-Wide
- Go-Tall
- Anthems
- Theft
- Pillowfort
- Stax
- Prison
- Combo Piece

Some are perfectly objective mechanical families. The point is only that they do not belong in the **minimal general deck-skeleton set** simply because they are familiar deck categories.

`TOKEN_GENERATOR` can therefore remain an Objective 6 candidate mechanical family without being declared a universal general component.

---

## 19. Proposed minimal general deck-skeleton surface

This is the strongest cross-source convergence after removing ambiguous terms.

### 19.1 Structure / mana

```text
MANA_BASE                    [DECK_STRUCTURE]
LAND_SLOTS                    [DECK_STRUCTURE]
COLOR_SOURCE_COVERAGE         [DECK_METRIC]
MANA_CURVE                    [DECK_STRUCTURE / METRIC]
MANA_FIXING                   [GENERAL_FUNCTION]
MANA_ACCELERATION             [GENERAL_FUNCTION]
RAMP / DURABLE_RAMP           [GENERAL_FUNCTION]
```

### 19.2 Card resources / access

```text
DRAW                          [GENERAL_FUNCTION / literal action]
CARD_SELECTION                [GENERAL_FUNCTION]
PERSONAL_CARD_RESOURCE_ADVANTAGE [ACCOUNTING_FUNCTION]
CARD_RESOURCE_PARITY          [ACCOUNTING_FUNCTION]
TUTOR                         [GENERAL_FUNCTION]
```

### 19.3 Answers / interaction

```text
SPOT_REMOVAL                  [GENERAL_FUNCTION]
SELECTIVE_MULTI_REMOVAL       [GENERAL_FUNCTION]
MASS_REMOVAL / BOARD_WIPE     [GENERAL_FUNCTION]
COUNTERSPELL                  [GENERAL_FUNCTION]
ABILITY_COUNTER               [GENERAL_FUNCTION]
GRAVEYARD_DENIAL              [GENERAL_FUNCTION]
PROTECTION                    [GENERAL_FUNCTION]
```

Target/object coverage remains facets:

```text
creature
artifact
enchantment
planeswalker
land
spell
ability
graveyard
hand
player action
```

### 19.4 Recovery

```text
GRAVEYARD_RECOVERY            [GENERAL_FUNCTION]
REANIMATION                   [MECHANICAL_FAMILY / child]
```

### 19.5 Closing plan

```text
WIN_CONDITION                 [DECK_ROLE_RELATIONAL]
FINISHER                      [DECK_ROLE_RELATIONAL]
```

These belong in the deckbuilding report but not as context-free card truths.

---

## 20. Alias registry proposal

Foundry can remain friendly without making aliases semantic synonyms internally.

| User/community term | Proposed canonical handling |
|---|---|
| Ramp | UI alias for Captain-defined durable Ramp; internally consider `DURABLE_RAMP` |
| Mana acceleration | `MANA_ACCELERATION` |
| Mana fixing / color fixing | `MANA_FIXING` |
| Draw | literal `DRAW` only |
| Card draw package | UI aggregation over Draw + other approved card-resource mechanisms |
| Card advantage | UI alias for `PERSONAL_CARD_RESOURCE_ADVANTAGE` in deck-health context; document scope |
| Card selection | `CARD_SELECTION` |
| Card filtering | UI/group alias; use exact child operations internally |
| Cantrip | strict established `CANTRIP`; do not use for broad temp-access parity family |
| Impulse draw / impulsive draw | UI alias for `IMPULSE_ACCESS` |
| Tutor | `TUTOR` |
| Light tutor / alt tutor | replace internally with `LIMITED_DEPTH_TUTOR`/`TOP_N_TUTOR` |
| Interaction | aggregate view over exact mechanisms |
| Removal | strict `REMOVAL` |
| Spot / targeted removal | `SPOT_REMOVAL` |
| Multi-removal | deprecate ambiguous internal slug; split `SELECTIVE_MULTI_REMOVAL` and `MULTI_INTERACTION` |
| Mass removal | `MASS_REMOVAL` |
| Board wipe / sweeper / wrath | familiar alias/subfamily of qualifying `MASS_REMOVAL` |
| Counter / countermagic / permission | `COUNTERSPELL` plus facets |
| Protection | `PROTECTION` with intrinsic protective-scope rule |
| Graveyard hate | UI alias for `GRAVEYARD_DENIAL` |
| Recursion | UI alias for `GRAVEYARD_RECOVERY` unless a narrower contract is adopted |
| Reanimation | `REANIMATION` with object-class facet |
| Wincon | `WIN_CONDITION`, deck-context relational |
| Finisher | `FINISHER`, deck-context relational |
| Value | no canonical tag |
| Utility | no canonical tag |
| Engine | relational/deferred |
| Enabler | relational/deferred |
| Payoff | relational/deferred |
| Threat | game-state/deck-context role, not global tag |
| Consistency | deck metric |
| Redundancy | deck metric |
| Resilience | deck metric |
| Flexibility | deck/card metric derived from facts |

---

## 21. Required corrections to the existing Objective 6 draft before ratification

The companion Objective 6 draft is still valuable, but the following terms should not be frozen exactly as currently worded.

### C1 — Split Removal from Neutralization

Current phrase "removes, neutralizes, or otherwise interacts" is too broad.

Required decision:

```text
REMOVAL
NEUTRALIZATION
OTHER INTERACTION
```

must be separately represented.

### C2 — Split Multi-removal from Multi-interaction

Cryptic Command's counter + bounce path demonstrates the collision.

Required decision:

```text
SELECTIVE_MULTI_REMOVAL
MULTI_INTERACTION
```

### C3 — Tighten Board Wipe

Do not let generic mass suppression become a wipe merely because several permanents are affected.

Require a strict mass-removal result, with one-sidedness represented by scope.

### C4 — Rename the broad Cantrip concept

Keep established `CANTRIP` narrow enough to match Magic usage.

Move the useful <=2-mana self-replacement/access concept to a new internal name such as `LOW_COST_CARD_PARITY`.

### C5 — Scope Card Advantage explicitly

Current Objective 6 meaning is personal usable card-resource gain, not all traditional relative card advantage.

Use explicit internal naming/accounting.

### C6 — Replace ambiguous Potential Card Advantage boundary with dependency facets or a more explicit name

Do not ratify until Sram / Arena / Rhystic / Esper Sentinel / opponent-action / controller-action cases are deterministic.

### C7 — Prefer Card Selection over broad Card Filtering as the canonical umbrella

Keep exact families for Loot, Rummage, Scry, Surveil, top manipulation, etc.

### C8 — Use Impulse Access internally

Preserve current-turn versus next-turn windows as data, not confusing child names.

### C9 — Make Mana Fixing a first-class general function

It is independently important and repeatedly distinguished from acceleration across deckbuilding sources.

### C10 — Clarify Ramp's deliberate divergence from community synonymy

Captain's `RAMP = durable acceleration` is coherent, but external sources often call rituals/temporary acceleration Ramp.

Use an explicit internal canonical name or documented alias law so the product never silently switches meanings.

### C11 — Add Graveyard Denial as a core general interaction component

External deck-skeleton data repeatedly treats Graveyard Hate as its own generic category. Use exact mechanics internally rather than the strategic word Hate.

### C12 — Make Win Condition / Finisher deck-context roles, not global card labels

They belong in deckbuilding health, but require deck context.

---

## 22. Candidate validation packets

Every retained term should be tested with positive, negative, and collision cases.

### 22.1 Removal packet

```text
Swords to Plowshares
  SPOT_REMOVAL = yes
  SELECTIVE_MULTI_REMOVAL = no

Naturalize
  SPOT_REMOVAL = yes
  object_class = artifact OR enchantment

Pacifism
  SPOT_REMOVAL = no
  NEUTRALIZATION = yes

Curse of the Swine (legal X >= 2)
  SELECTIVE_MULTI_REMOVAL = yes

Hex
  SELECTIVE_MULTI_REMOVAL = yes

Wrath of God
  MASS_REMOVAL = yes
  BOARD_WIPE = yes

Ruinous Ultimatum
  BOARD_WIPE = yes
  ONESIDED_BOARD_WIPE = yes

Cryptic Command: counter + bounce path
  MULTI_INTERACTION = yes
  SELECTIVE_MULTI_REMOVAL = no on that path
```

### 22.2 Card-resource packet

```text
Ponder
  DRAW = yes
  CARD_SELECTION = yes
  CARD_RESOURCE_PARITY = expected yes
  CANTRIP = yes under established contract

Wrenn's Resolve
  DRAW = no
  IMPULSE_ACCESS = yes
  CANTRIP = no under strict established contract
  LOW_COST_CARD_PARITY = candidate yes if temporary access counts

Phyrexian Arena
  DRAW = yes when trigger resolves
  PERSONAL_CARD_RESOURCE_ADVANTAGE = yes over declared window
  dependency = delayed / scheduled

Rhystic Study
  dependency = opponent-action + payment-choice
  exact direct/conditional advantage label = requires Captain ruling
```

### 22.3 Mana packet

```text
Sol Ring
  MANA_SOURCE = yes
  MANA_FIXING = no
  MANA_ACCELERATION = yes
  RAMP = yes under Captain durable rule
  MANA_ROCK = yes
  FAST_MANA = yes

Arcane Signet
  MANA_SOURCE = yes
  MANA_FIXING = yes in multicolor identity where it adds useful colors
  MANA_ACCELERATION = yes
  RAMP = yes
  MANA_ROCK = yes

Dark Ritual
  MANA_ACCELERATION = yes
  RITUAL = yes
  RAMP = no under Captain durable rule
  FAST_MANA = candidate yes under threshold

Boros Garrison
  MANA_SOURCE = yes
  MANA_FIXING = yes
  RAMP = no
  MANA_PARITY = Captain candidate, needs accounting-window test

Exploration
  EXTRA_LAND_PLAY = yes
  RAMP = no under Captain rule
  MANA_ACCELERATION = conditional capability under current direction
```

### 22.4 Recovery packet

```text
Regrowth
  GRAVEYARD_RECOVERY = yes
  REANIMATION = no

Reanimate
  GRAVEYARD_RECOVERY = yes
  REANIMATION = yes
  object_class = creature

Sevinne's Reclamation
  GRAVEYARD_RECOVERY = yes
  REANIMATION = yes
  object restriction preserved

Flashback-like self-cast permission
  GRAVEYARD_RECOVERY = yes if parent includes cast-from-graveyard access
  REANIMATION = no
```

---

## 23. Deck Functional Health vocabulary after this audit

A future deck-health view can use familiar headings while retaining exact internal meaning.

Example presentation:

```text
Mana
  Land slots
  Color sources
  Mana fixing
  Durable ramp
  Fast mana

Cards / Access
  Literal draw
  Card selection
  Personal card-resource advantage
  Card-resource parity
  Tutors
  Impulse access

Interaction
  Spot removal
  Selective multi-removal
  Board wipes
  Counterspells
  Graveyard denial
  Hand disruption
  Coverage by object/resource class

Defense / Recovery
  Protection
  Graveyard recovery
  Reanimation

Closing plan
  Win conditions [deck-context]
  Finishers [deck-context]
```

The UI can still say "Draw," "Ramp," "Removal," "Graveyard Hate," and "Wincons" because those are familiar player words. The engine must not rely on those words alone to define truth.

---

## 24. Terms intentionally NOT treated as universal requirements

This research does **not** support any law that every deck must contain a fixed number of each category.

It supports only that these categories are repeatedly used to reason about decks.

No semantic truth should say:

- every deck must run N ramp;
- every deck must run N draw;
- every deck must run N wipes;
- every deck must have tutors;
- every deck must have graveyard denial;
- every deck must have a separately labeled finisher.

Those are downstream recommendations and may vary by commander, strategy, curve, color identity, power environment, and desired play experience.

---

## 25. Recommended next Objective 6 terminology sequence

1. Captain reviews the twelve required corrections in §21.
2. Freeze semantic kinds (`GENERAL_FUNCTION`, `DECK_STRUCTURE`, etc.).
3. Ratify the strict Removal / Neutralization / Multi-interaction split.
4. Ratify `CANTRIP` versus broader low-cost card-parity terminology.
5. Ratify personal card-resource accounting names and dependency facets.
6. Ratify Card Selection family names.
7. Ratify Impulse Access naming/window representation.
8. Ratify Mana Fixing and the explicit Ramp alias law.
9. Ratify Graveyard Denial / Recursion / Reanimation names.
10. Mark Wincon/Finisher/Threat/Engine/Enabler/Payoff as relational rather than card-global where applicable.
11. Build gold-positive, hard-negative, and collision packets for each ratified term.
12. Only after the names and boundaries survive those packets should Objective 6 become an executable vocabulary specification.

---

## 26. Bottom line

The external search confirms that Foundry is converging on the right general deckbuilding surface. The recurring community skeleton is remarkably stable:

```text
MANA / LANDS
CARD ACCESS / DRAW
INTERACTION / REMOVAL
PROTECTION
RECOVERY / RECURSION
TUTORS
GRAVEYARD ANSWERS
WINNING PLAN
```

But the research also confirms that **the familiar words are not precise enough to be the executable ontology by themselves**.

The strongest Objective 6 approach is therefore:

```text
PLAYER-FAMILIAR LABELS
        ↓
EXACT FOUNDRY CANONICAL CONTRACTS
        ↓
ORTHOGONAL FACETS / ACCOUNTING / DEPENDENCIES
        ↓
S16A SEMANTIC FACTS + PROVENANCE
```

That lets the product remain intuitive to Magic players while ensuring terms such as **Removal, Cantrip, Card Advantage, Ramp, Interaction, Protection, Recursion, Tutor, Graveyard Hate, Wincon, and Finisher never change meaning silently inside Foundry.**

The main corrections are semantic cleanup, not a reversal of the architecture. The architecture remains sound; the vocabulary now needs these sharper boundaries before ratification.
