# Objective 6 — Functional Vocabulary and Deck Functional Health Architecture

**Status:** CAPTAIN DRAFTING / NON-EXECUTING / NOT RATIFIED  
**Date:** 2026-09-13  
**Objective:** 6 — `FOUNDRY_FUNCTIONAL_VOCABULARY_SPECIFICATION`  
**Base evidence branch:** `preflight/objective5-s16b-gameplay-dna-2026-09-12`  
**Base evidence head when this draft was created:** `034ee0459c5048e0fb3be3d717abd39bb4cbc05e`  
**S16 relationship:** S16A semantic card-reading is the lower prerequisite; S16B gameplay-DNA is the downstream consumer.  
**Implementation authorization:** NONE. This document does not authorize S16A, S16B, S10–S15, AQ4, Bridge v0, merge, deployment, parser changes, codebook changes, or production-tag assignment.

---

## 1. Purpose

This document captures the architecture that emerged from the Captain's Objective 6 vocabulary review after Objective 5 closed its S16B preflight research.

Objective 5 established that a useful MTG thesaurus needs a functional layer above literal mechanics, but deliberately left community vocabulary non-authoritative. Objective 6 exists to define Foundry-owned functional language precisely enough that later systems can assign, search, compare, count, and explain those functions deterministically.

The central product insight is now broader than Searcher B alone:

> **Foundry should distinguish the general functions that make decks operate from the much larger future vocabulary describing what a specific strategy is trying to do.**

A Reanimator deck, Artifact deck, Tokens deck, Voltron deck, typal deck, or unrelated Commander deck may pursue very different strategies, but all can still need broadly useful functions such as mana acceleration, card access, card advantage, interaction, removal, protection, recursion, and graveyard/artifact/enchantment coverage.

These cross-strategy functions can become:

- user-facing search/filter buttons;
- Searcher B retrieval parents;
- inputs to deck-composition summaries;
- inputs to deck functional-health diagnostics;
- inputs to replacement recommendations;
- a neutral substrate that later strategy-specific tags can re-rank without redefining the underlying function.

This document records both **Captain directions already stated** and **Manager re-audit proposals**. The latter are explicitly marked as proposals and are not Captain-ratified merely because they appear here.

---

## 2. Core product model

Foundry should ultimately expose at least three conceptually separate layers.

### 2.1 Layer A — General functional capability

Question:

> **What useful jobs can this card or effect perform independent of a particular deck strategy?**

Examples include:

- Ramp
- Mana Acceleration
- Mana Fixing
- Card Access
- Draw
- Card Advantage
- Potential Card Advantage
- Card Filtering
- Card Parity
- Spot Removal
- Multi-removal
- Board Wipe
- Counterspell
- Protection
- Graveyard Interaction
- Artifact Interaction
- Enchantment Interaction
- Recursion
- Reanimation
- Blink

This is the primary subject of Objective 6.

### 2.2 Layer B — Deck functional health

Question:

> **Does this deck have enough breadth, density, redundancy, and usable timing among the general functions that decks commonly rely on?**

This is a downstream consumer of the Objective 6/S16B capability layer. It is not itself semantic authority.

Possible outputs include:

- function presence or absence;
- raw count of cards able to perform a function;
- percentage/density of deck slots providing a function;
- target/resource coverage breadth;
- unique-source redundancy;
- timing/cost/availability shape;
- conditional versus self-contained access to a function;
- blind spots such as no graveyard, artifact, or enchantment interaction;
- imbalances such as many filtering/parity effects but little or no actual card advantage.

### 2.3 Layer C — Strategy-specific alignment

Question:

> **Of the cards that perform useful general functions, which ones also advance this particular deck's strategy?**

This is intentionally later and can become very large. A Reanimator deck may prefer removal on creatures it can recur; an Artifact deck may prefer artifact-based removal; a Tokens deck may prefer interaction that also creates or exploits tokens.

The strategy layer should re-rank or refine candidates. It should not redefine what `SPOT_REMOVAL`, `RAMP`, or `CARD_ADVANTAGE` mean.

This separation prevents an explosion of combined labels such as `REANIMATOR_SPOT_REMOVAL`, `TOKEN_RAMP`, `ARTIFACT_CARD_ADVANTAGE`, etc. The general function and strategy alignment should remain independently queryable dimensions.

---

## 3. Relationship to S16

The existing S16 architecture states:

- **S16A = understand the card precisely.**
- **S16B = compare what those understood instructions accomplish in gameplay.**

Objective 6 provides the missing semantic contract between them.

```text
Oracle / Comprehensive Rules
        ↓
S16A — lossless structured semantic parse
        ↓
Objective 6 — deterministic functional vocabulary contracts
        ↓
S16B — derived gameplay-DNA capability graph, retrieval, ordering, explanation
        ↓
Deck Functional Health — composition / coverage / recommendation consumer
        ↓
Later Strategy Layer — strategy-specific alignment and re-ranking
```

### 3.1 S16A responsibilities

S16A should preserve objective facts such as:

- semantic owner and exact Oracle span;
- face / paragraph / ability / mode / instruction structure;
- cost versus effect;
- actor/controller/owner/opponent scope;
- target versus choose versus affect-all;
- exact or symbolic cardinality;
- source and destination zones;
- immediate versus delayed timing;
- duration;
- trigger / activation / spell / static / replacement delivery;
- modal exclusivity and co-availability;
- conditions and restrictions;
- linked instructions and object identity;
- repeatability;
- payments and resources consumed;
- provenance.

S16A should not need to decide whether those facts constitute community/product concepts such as `RAMP` or `MULTI_REMOVAL`.

### 3.2 Objective 6 responsibilities

Objective 6 should define exact Foundry membership law for functional concepts.

Example:

```text
S16A facts:
  exile permanent X
  linked return of same X to battlefield
  timing = same resolving sequence

Objective 6 derivation:
  BLINK = true
  BLINK_NOW = true
```

or:

```text
S16A facts:
  effect individually selects X creature objects
  X >= 2 is legal
  action neutralizes/removes selected objects

Objective 6 derivation:
  MULTI_REMOVAL = true
```

### 3.3 S16B responsibilities

S16B should consume those derived capabilities and do the work it was designed for:

1. **Retrieval** — surface cards sharing materially useful gameplay functions.
2. **Ordering** — rank closer functional substitutes above loose category neighbors.
3. **Explanation** — explain the shared job and mechanically relevant differences using traceable facts.

S16B should not silently invent or redefine Objective 6 terminology during ranking.

---

## 4. Vocabulary representation laws

### 4.1 Parent/child means logical implication

Use `IS_A` parenthood only where the implication is always true:

> If X is a child of Y, every X is also Y.

Examples that can fit this law under current Captain directions:

```text
BLINK_NOW    → BLINK
BLINK_DELAYED → BLINK
MANA_ROCK    → RAMP → MANA_ACCELERATION
MANA_DORK    → RAMP → MANA_ACCELERATION
LAND_RAMP    → RAMP → MANA_ACCELERATION
RITUAL       → FAST_MANA → MANA_ACCELERATION
HARD_COUNTER → COUNTERSPELL
SOFT_COUNTER → COUNTERSPELL
```

Parenthood should not be used merely because two concepts are related.

### 4.2 Use a DAG/lattice, not a rigid tree

A card/effect can legitimately have several parents or several functional memberships simultaneously.

Example:

```text
Sol Ring
  MANA_ACCELERATION
  RAMP
  MANA_ROCK
  FAST_MANA
```

No forced single “primary role” is required.

### 4.3 Siblings do not need to exhaust a parent

A parent category can contain members that do not yet have a narrower child.

Do not invent a child solely to force a complete partition.

### 4.4 Classify effect/choice paths before card-level capability

Complex or modal cards should not be flattened into one card-level bag of effects.

Preferred conceptual order:

```text
semantic effect / mode / legal choice path
        ↓
functional capability of that path
        ↓
card CAN_PERFORM(function)
```

This matters for cards such as Cryptic Command, where several functions can be available through modes without all four modes occurring together.

### 4.5 Multi-label membership is expected

A card can support many functions at once. Percentages based on those labels are coverage percentages, not exclusive partitions, and therefore need not sum to 100%.

### 4.6 Domain-specific accounting must stay domain-specific

`MANA_PARITY` does not mean the card is “overall parity.” A card may be mana-parity while gaining a creature, card, life, or another resource.

Likewise card-resource accounting should not silently include unrelated battlefield value.

### 4.7 Unknown is preferable to invented certainty

If Foundry cannot prove a functional label from the available semantic representation and ratified contract, the result should remain `UNKNOWN` / `INSUFFICIENT_EVIDENCE`, not a guessed boolean.

This preserves the Objective 5 anti-folklore and S16A no-silent-approximation principles.

---

## 5. Curated function labels versus orthogonal capability facets

**Manager re-audit proposal — not yet Captain-ratified as architecture law.**

A major risk is combinatorial tag explosion. Foundry should not need separate canonical labels for every combination such as:

- instant-speed artifact spot removal that exiles;
- sorcery-speed creature multi-removal that destroys;
- repeatable enchantment interaction on a creature;
- two-mana conditional graveyard interaction.

Instead, separate two things.

### 5.1 Curated functional labels

These are meaningful concepts users recognize and may click directly:

- Spot Removal
- Multi-removal
- Board Wipe
- Ramp
- Mana Rock
- Card Advantage
- Card Filtering
- Tutor
- Blink
- Recursion

### 5.2 Orthogonal facets

These describe how the function is delivered and what it covers:

- target/object class: creature, artifact, enchantment, planeswalker, land, card, spell, ability, graveyard card, player, etc.;
- scope: one, selected-many, all matching objects, all opponents, symmetric, asymmetric;
- method/action: destroy, exile, bounce, sacrifice, counter, damage, prevention, prohibition, tax, etc.;
- destination zone;
- timing/delivery;
- mana value / activation cost / resource cost;
- immediate versus delayed;
- one-shot versus repeatable;
- conditional versus unconditional;
- self-contained versus dependent on another action/card/state;
- opponent-dependent versus controller-driven;
- modal/optional status;
- co-availability with other functions on the same card;
- compensation or downside.

The UI can combine a curated label with facets without needing a new semantic term for every cross-product.

Example search:

```text
Function: Spot Removal
Target class: Artifact OR Enchantment
Timing: Instant-speed
Destination/method: Exile OR Destroy
Mana value: <= 3
```

This preserves precision while keeping the public vocabulary understandable.

---

## 6. Captain directions captured so far

This section records directions stated by the Captain during the Objective 6 discussion. They remain draft Objective 6 material until formally ratified.

### 6.1 Enabler / Payoff — DEFERRED

`ENABLER` and `PAYOFF` are intentionally deferred for now.

Reason: they are relational concepts (`enabler for what?`, `payoff for what?`) and would force strategy/context modeling before the core general-purpose functional vocabulary is settled.

Reserve the terminology; do not include it in the initial Objective 6 execution surface.

### 6.2 Blink family

`BLINK` is the parent.

```text
BLINK
├─ BLINK_NOW
└─ BLINK_DELAYED
```

Working meanings:

- **Blink** — a permanent is exiled and subsequently returned to the battlefield through a linked effect/instruction.
- **Blink-Now** — the return occurs as part of the same resolving effect/sequence rather than at a later game time.
- **Blink-Delayed** — the exile establishes a later return, such as at the beginning of the next end step.

Underlying facets such as controller, object class, tapped status, or return under a different controller should remain separately represented.

### 6.3 Removal scope family

#### Spot Removal

One card/effect removes, neutralizes, or otherwise interacts with **one individually selected object**. The object must be targeted or otherwise specifically chosen.

#### Multi-removal

One card/effect can remove/neutralize **two or more distinct game objects individually chosen by the caster/controller**.

There is no upper numerical ceiling. The distinction is not “exactly two.”

Gold-positive examples stated by the Captain include:

- **Curse of the Swine** — selected X creatures;
- **Hex** — six selected creatures;
- **Cryptic Command** when a legal choice path independently interacts with more than one chosen object, such as countering a chosen spell and returning a chosen permanent.

A card that merely offers a choice among possible single objects is not Multi-removal. Naturalize can choose which artifact or enchantment it removes, but removes only one object.

#### Board Wipe

A wipe removes/neutralizes the entire matching battlefield scope rather than allowing the caster to individually select the affected objects.

Current Captain distinction:

```text
individually chosen set of >=2 objects → MULTI_REMOVAL
universal matching set               → BOARD_WIPE / ONESIDED_BOARD_WIPE
```

#### One-sided Board Wipe

A universal wipe over the opponent side(s) that excludes the caster/controller's matching board.

**Ruinous Ultimatum** is the Captain's gold-standard example.

### 6.4 Mana family

#### Mana Acceleration

Broad parent for effects/cards that advance mana availability beyond baseline development through the relevant mechanism.

#### Ramp

`RAMP` is reserved for durable/permanent forms of mana acceleration that can continue to provide mana across turns.

Current inclusions include:

- Mana Dorks;
- Mana Rocks;
- Land Ramp;
- other qualifying permanents that repeatedly produce more useful mana capacity.

Current exclusions include:

- ordinary lands that produce only one mana;
- bounce lands such as Boros Garrison;
- cards that merely permit additional land plays;
- one-shot rituals.

A land that durably produces more than one mana without sacrificing/leaving the battlefield to do so can qualify as Ramp under the current direction. **Phyrexian Tower** was given as an example.

#### Land Ramp

Cards that obtain a land from the library and put that land onto the battlefield.

Additional-land permission is not Land Ramp.

#### Land Add

Cards that allow additional lands to be played. `LAND_ADD` is Mana Acceleration but explicitly **not Ramp**, because it still depends on having lands available to play.

#### Mana Dork

Creature mana source in the familiar Mana Dork functional family.

#### Mana Rock

Artifact mana source in the familiar Mana Rock functional family.

#### Fast Mana

Current Captain rule:

- qualifying card/effect costs two mana or less;
- can produce its qualifying mana immediately;
- produces more mana than its casting cost.

Examples:

- Sol Ring: cost 1, can immediately produce 2 → Fast Mana.
- A two-mana qualifying source would need to immediately produce at least 3 mana.

#### Ritual

Keep Ritual as the one-shot temporary-burst family and a child/member under Fast Mana where the Fast Mana contract is satisfied.

#### Mana-Parity

`MANA_PARITY` evaluates the **mana-development transaction**, not the overall value of the card.

Captain examples:

- **Boros Garrison** — uses the land play, enters tapped, returns an existing land, and only later taps for two. Under normal development it reconfigures mana production but does not independently put the player ahead of ordinary mana development.
- **Priest of Gix** — costs mana and refunds an equivalent amount through its own effect; the mana transaction can be parity even though the player also obtains a creature body.

Working principle:

> A Mana-Parity card/effect replaces, refunds, or reconfigures mana-producing development without itself creating net acceleration over the baseline development/resources it displaced or consumed.

This requires further gold/negative testing before ratification because the baseline accounting window must be made exact.

### 6.5 Card-resource family

#### Draw

`DRAW` remains literal rules-action draw and is the parent of draw-specific child labels because some cards specifically care about drawing.

#### Draw-Now

A card/effect produces the qualifying draw immediately rather than establishing a future draw condition/window.

#### Draw-Delay

The card/effect establishes draw that occurs later. **Mishra's Bauble** and **Arcane Denial** were given as examples.

Implementation language should ultimately key off semantic timing/dependency rather than merely the English phrase “upon resolution.”

#### Card Advantage

Current Captain direction:

- casting/using the source itself counts as an expenditure;
- the card's own functionality must eventually produce net-positive usable card resources;
- literal draw is not the only mechanism;
- temporary playable exile/impulse access may count;
- access to opponents' cards that the controller can use may count;
- the qualifying advantage need not be immediate;
- the source must not require a separate external outlet/action to begin producing the advantage under the intended distinction.

Examples stated by the Captain:

- Brainstealer Dragon → Card Advantage;
- Phyrexian Arena → Card Advantage;
- Sram, Senior Edificer → **not** Card Advantage under this specific label because Sram requires qualifying external casts before drawing.

#### Potential Card Advantage

A card whose own text contains machinery that can produce true card advantage if qualifying conditions/events/actions occur.

Captain examples include:

- Sram, Senior Edificer;
- Rhystic Study;
- Esper Sentinel;
- Aurelia, the Law Above;
- Trouble in Pairs.

The exact line between self-contained `CARD_ADVANTAGE` and `POTENTIAL_CARD_ADVANTAGE` requires a deterministic dependency contract.

#### Card-Parity

Provides enough usable card resource to replace the expended card/resource but does not create net positive card quantity under the defined accounting window.

#### Card Filtering

Parent for effects that improve card quality/selection without requiring net card gain, including Looting, Rummaging, Scry, Surveil, and related selection/reorganization families.

The Captain also wants an `INDEX`-like child/family for cards that reorganize top-library order without card parity or card advantage.

#### Cantrip

Current Captain contract direction:

- qualifying action costs two mana or less;
- a card's own printed cost-reduction/payment mechanics count toward determining that cost;
- external unrelated reducers do not make a nonqualifying action a cantrip;
- the action grants immediate access to at least one usable card resource;
- literal `DRAW` is not required;
- a card selected/put into hand can qualify;
- Wrenn's Resolve-style temporary playable access can qualify;
- the action must at least replace the card/resource spent on the action;
- card type does not matter;
- Cycling qualifies only if the Cycling activation cost is two or less;
- multi-label membership is expected.

Ponder and Brainstorm are Captain gold-standard examples.

---

## 7. General function layer versus strategy vocabulary

Objective 6 should primarily settle **general deck-function vocabulary**.

Strategy/archetype labels such as the following should generally remain a separate future layer unless a specific card-level functional action is being defined:

- Reanimator
- Aristocrats
- Voltron
- Tokens as an archetype
- Spellslinger
- Superfriends
- Group Hug
- Group Slug
- Prison as an archetype
- Typal/Tribal deck identity
- Lands Matter
- Graveyard Matters
- Goodstuff
- Battlecruiser

A useful naming distinction is:

```text
REANIMATE       = card/effect function
REANIMATOR      = deck strategy

TOKEN_GENERATOR = card/effect function
TOKENS          = deck strategy

DIRECT_DAMAGE / BURN_EFFECT = function
BURN_ARCHETYPE              = strategy
```

This allows the later strategy layer to become extremely rich without polluting the general utility vocabulary.

---

## 8. Deck Functional Health — downstream consumer concept

**Working product concept, not Objective 6 semantic authority.**

A deck-health analyzer should consume deterministic function memberships and objective facets. It should not define them.

### 8.1 Report dimensions

For each function, useful measurements include:

1. **Presence** — does the deck have at least one source?
2. **Count** — how many unique cards/slots can perform the function?
3. **Density** — what fraction of relevant deck slots provide the function?
4. **Breadth** — how many different object/resource/problem classes can the deck address?
5. **Redundancy** — how many independent sources cover the same important need?
6. **Timing profile** — instant/sorcery/static/activated, immediate/delayed, early/late availability.
7. **Cost profile** — mana/resource costs and distribution.
8. **Reliability / dependency** — self-contained, conditional, opponent-dependent, setup-dependent, mode-limited, trigger-dependent.
9. **Co-availability** — can multiple claimed functions on one card be used together, or are they mutually exclusive modes/paths?
10. **Strategic alignment** — later layer: how many general-purpose function sources also reinforce the deck's strategy?

### 8.2 Percentages are coverage, not partitions

A card can count in several categories, so function-density percentages do not need to sum to 100%.

Example:

```text
Ramp:               9 cards
Mana Fixing:         7 cards
Card Filtering:     11 cards
Card Parity:         7 cards
Card Advantage:      2 cards
Potential Advantage: 1 card
```

The same card may contribute to multiple rows.

### 8.3 Do not create an arbitrary overall “deck quality” score yet

A single score would require subjective weighting among functions and strategies.

Initial deck health should report observable composition and clearly scoped diagnostics instead of laundering weights into semantic truth.

### 8.4 Avoid universal threshold dogma

Foundry can factually report:

> “This deck contains zero enchantment interaction.”

It can also report:

> “This deck contains eleven filtering/parity sources and zero direct card-advantage sources.”

But a rule such as “every Commander deck must contain exactly ten removal spells” is a strategic heuristic, not Oracle/Objective 6 truth.

Any later recommended target ranges should be:

- explicitly downstream;
- configurable by format/strategy/power target;
- evidence-backed where practical;
- kept distinct from semantic membership.

---

## 9. Interaction coverage matrix

A raw number of “interaction cards” is not enough.

A deck can have eight removal cards and still be unable to answer artifacts, enchantments, graveyards, or spells on the stack.

The functional-health consumer should therefore be able to summarize interaction coverage by problem domain.

Candidate coverage dimensions include:

| Problem/resource domain | Example capability source |
|---|---|
| Creatures | creature spot/multi/mass removal |
| Artifacts | artifact removal/neutralization |
| Enchantments | enchantment removal/neutralization |
| Planeswalkers | planeswalker-capable interaction |
| Lands | land interaction/destruction where applicable |
| Graveyards | graveyard exile, denial, purge, access lock |
| Stack — spells | Counterspell / spell interaction |
| Stack — abilities | ability counters or other applicable interaction |
| Hands | discard / hand disruption |
| Combat | Fog, combat manipulation, deterrence where relevant |
| Player actions | Silence, tax, prohibition/restriction families |

Many of these should be generated by **function + facets**, not by inventing a unique canonical label for every row.

Example diagnostic:

```text
Interaction coverage
  Creature:     strong coverage
  Artifact:     1 source
  Enchantment:  0 sources
  Graveyard:    0 sources
  Stack:        3 sources

Observed blind spots:
  - no enchantment interaction
  - no graveyard interaction
```

Terms such as “strong” or “low” require a downstream threshold policy; the zero/nonzero and counts themselves are factual.

---

## 10. Counting law: one card is not several independent sources

**Manager re-audit proposal — recommended as a downstream counting invariant.**

Multi-role cards create an important accounting risk.

Suppose one modal card can be:

- artifact removal;
- enchantment removal;
- creature removal;
- card draw.

It should contribute capability to every applicable category, but it remains **one physical card slot and one source**.

Therefore deck-health logic should distinguish:

- **capability coverage** — all jobs a card can perform;
- **unique source count** — number of physical cards providing that job;
- **simultaneous/co-available capability** — whether multiple jobs can be used together;
- **modal alternatives** — jobs that are mutually exclusive in a specific cast/activation.

This is especially important for S16A because its modal-exclusivity conservation is intended to prevent false composition.

A deck with one modal charm that can answer artifacts *or* enchantments should not be reported as though it possesses two independent pieces of removal when assessing redundancy.

---

## 11. Reliability and conditionality should be visible

The Captain's `CARD_ADVANTAGE` versus `POTENTIAL_CARD_ADVANTAGE` distinction exposes a broader product need: not all functional coverage has the same dependency structure.

Rather than inventing a separate named tag for every case, Foundry should preserve objective dependency facets where possible:

- self-contained versus requiring another card/action;
- guaranteed versus conditional;
- controller-driven versus opponent-dependent;
- immediate versus delayed;
- repeatable versus one-shot;
- activation required versus passive/static;
- board-state dependency;
- hand/graveyard/library dependency;
- once-per-turn or other rate limits;
- optional/mode-limited access.

These facets can improve search ordering and deck-health explanations without changing the meaning of the parent function.

Example:

> “Your deck has six potential sources of extra cards, but four depend on opponents taking a particular action and only one is self-contained repeatable card advantage.”

That is much more informative than a flat `DRAW = 6` count.

---

## 12. Replacement recommendations should be function-preserving when possible

A powerful downstream use of Searcher B is to recommend **replacements**, not merely more cards.

Example deck observation:

```text
Card Filtering:          high
Card Parity:             high
Card Advantage:          none
Potential Card Advantage: low
```

A useful recommendation is not necessarily:

> Add more cards.

It can instead be:

> Replace one or more filtering/parity slots with cards that preserve the same selection/filtering job while also generating Card Advantage or Potential Card Advantage.

Likewise, if a deck already has creature removal but lacks artifact/enchantment coverage, Searcher B can prefer replacements that preserve interaction density while widening target coverage.

A future recommendation should be able to explain:

1. what deck-health gap was observed;
2. what function the current card provides;
3. what function the proposed replacement preserves;
4. what additional missing capability the replacement adds;
5. important mechanical differences/costs/restrictions;
6. later, whether the replacement also aligns with the deck's strategy.

---

## 13. Strategy alignment is an additive re-ranking layer

Later strategy tags should make the general-function system more useful, not replace it.

Example:

```text
Need: SPOT_REMOVAL
Deck strategy: REANIMATOR
```

General retrieval can first find all qualifying Spot Removal.

The future strategy layer can then prefer candidates that also have traits useful to Reanimator, such as:

- creature-based interaction that can be reanimated;
- self-sacrificing or graveyard-friendly interaction;
- effects that stock or exploit graveyards;
- recursion-compatible permanent types.

The same Spot Removal parent can be re-ranked differently for Artifacts, Tokens, Voltron, or another strategy.

This preserves one semantic definition while allowing strategy-aware recommendations.

---

## 14. Required S16A input contract for every Objective 6 term

Before a term is ratified for executable derivation, its specification should state exactly which lower semantic facts it requires.

Recommended term template:

```text
TERM:
Foundry canonical name:
User-facing aliases:
Status: DRAFT / RATIFIED / DEFERRED

Kind:
- GENERAL_FUNCTION / MECHANICAL_FAMILY / ACCOUNTING_FUNCTION / STRATEGY / RELATIONAL / OTHER

Parent term(s):
Child term(s):

Exact Foundry definition:

Required S16A semantic inputs:
- action/effect
- actor / affected actor
- object/target class
- targeting/selection/universal scope
- quantity/cardinality
- source zone
- destination zone
- timing/duration
- cost/payment
- condition/dependency
- repeatability
- modal/co-availability structure
- linked-object identity
- other as required

Required predicates:
- ...

Disqualifying predicates:
- ...

Numeric/timing thresholds:
- ...

Accounting domain and window:
- ...

Context required:
- NONE / CARD / DECK / COMMANDER / ARCHETYPE / METAGAME / GAME_STATE

Orthogonal facets preserved:
- ...

Gold-positive examples:
- ...

Hard negatives / near misses:
- ...

Known edge cases:
- ...

Explanation contract:
- why the card qualifies
- which exact semantic facts prove membership

Captain ruling date/version:
```

A term should STOP before ratification if S16A cannot represent a fact required to determine membership without approximation.

That stop is useful: it reveals either an incomplete term contract or a missing S16A semantic coordinate.

---

## 15. Acceptance and testing concept

Objective 6 should not ratify terms merely because their prose definition sounds reasonable.

Each important term should include:

- clear positives;
- hard negatives;
- near-misses;
- modal cases;
- multi-face/complex cases when relevant;
- boundary values around numeric thresholds;
- cases using different Oracle wording but same function;
- cases using similar wording but failing the function;
- proof that parent implications hold;
- proof that child membership does not erase lower mechanical distinctions.

Example for the removal family:

```text
Naturalize
  expected: SPOT_REMOVAL
  not: MULTI_REMOVAL

Curse of the Swine with X capable of >=2
  expected: MULTI_REMOVAL
  not: BOARD_WIPE

Hex
  expected: MULTI_REMOVAL
  not: BOARD_WIPE

Destroy all creatures
  expected: BOARD_WIPE
  not: MULTI_REMOVAL

Destroy all creatures you don't control
  expected: ONESIDED_BOARD_WIPE
```

The final executable tests should bind to S16A semantic facts, not to card-name exceptions.

---

## 16. Open / unresolved Objective 6 items

The following should remain visibly unresolved rather than silently decided by this architecture draft.

### 16.1 Impulse naming

The Captain currently distinguishes temporary playable-exile access by duration:

- `Impulse-Select` — playable until end of turn;
- `Impulse-Draw` — playable until end of next turn;
- `Impulse` as parent.

The Objective 5 research also noted that Wizards R&D has used “impulsing” for a different top-N-selection concept. Canonical naming should be re-audited before ratification so Foundry does not create an avoidable terminology collision.

The semantic distinction by duration is still valuable even if the final child names change.

### 16.2 Token Generator

`TOKEN_GENERATOR` appeared in the edited lexicon but had no explicit Captain verdict in the reviewed text. It should remain unratified until addressed.

### 16.3 Alt-Tutor / Light-Tutor

The Captain proposed a friendly tutor-alternative label for deep selective library access because of casual Commander attitudes toward tutors.

The product concept is useful. The canonical/internal name versus user-facing alias remains open.

A possible architecture is to preserve a mechanically explicit internal concept such as `DEEP_SELECTIVE_LIBRARY_ACCESS` while exposing a friendlier user-facing label later, but that is not ratified here.

### 16.4 Mana-Parity accounting window

Boros Garrison and Priest of Gix clarify the intended concept, but the exact baseline and time window need hard boundary tests before the term becomes executable.

### 16.5 Card Advantage versus Potential Card Advantage dependency line

The Captain's distinction is clear at a product level, but the exact predicate for “requires another outlet/action” needs edge-case testing.

### 16.6 Enabler / Payoff

Explicitly deferred.

### 16.7 Strategy/archetype vocabulary

Reserved for later strategy-layer work except where a strategy term has a separately defined card-function counterpart.

---

## 17. Additional useful downstream analyses identified by re-audit

These are promising consumers of the same functional/facet substrate. They should not be promoted to semantic truth automatically.

### 17.1 Functional breadth

How many distinct broad needs can a deck answer?

### 17.2 Functional redundancy / single points of failure

Does the deck have several independent sources of an important capability, or only one?

Tutors may improve access to a capability but should not automatically be counted as additional independent copies of that capability unless a separate downstream “effective access” model is explicitly designed.

### 17.3 Availability profile

At what mana costs and timings can the deck access a function?

A deck may technically have removal but only at high mana values or sorcery speed.

### 17.4 Coverage overlap

Which cards cover multiple blind spots at once?

This is particularly useful for replacement recommendations and constrained deck slots.

### 17.5 Capability concentration

Are several critical functions concentrated onto one or two cards? Multi-role cards are efficient, but they can create fragility if the deck's apparent coverage depends heavily on a few sources.

### 17.6 Format-aware denominator

Deck-density percentages should use a clearly defined denominator appropriate to the format and product view. In Commander, for example, a UI may choose to report percentages over the 99 noncommander cards separately from always-available commander capabilities.

This is a downstream calculation choice, not an Objective 6 semantic rule.

### 17.7 Always-accessible versus library-bound capability

Commanders, companions where legal/applicable, and other always-accessible resources can change the practical availability of a function. Preserve this for later deck-health modeling rather than baking it into the definition of the function itself.

---

## 18. Non-goals and guardrails

This draft does **not** authorize or assert that Foundry should now:

- implement Objective 6 tags in production;
- modify the codebook or ACTIVE axes;
- change S16A parser behavior;
- begin S16B implementation;
- import community labels as mechanical truth;
- infer archetypes from one card in isolation;
- assign Enabler/Payoff relationships;
- create a universal deck-quality score;
- hard-code universal “correct” quantities of ramp/removal/draw;
- treat one modal card as several independent sources;
- flatten mutually exclusive modes;
- create a canonical tag for every possible combination of function, target class, timing, cost, and strategy;
- let strategy-specific judgments override literal Oracle/CR mechanics;
- silently classify uncertain cards.

---

## 19. Recommended Objective 6 work sequence

1. **Finish the Captain vocabulary pass** over the general-function candidates.
2. **Explicitly separate** each candidate into general function, mechanical family, strategy, relational, accounting, or deferred.
3. For each general function, write the deterministic term contract using the template in this document.
4. Identify the **required S16A semantic inputs** for each contract.
5. STOP on any term whose required semantic facts are not representable by the planned S16A substrate without approximation.
6. Build gold positives, hard negatives, boundary cases, and parent-implication tests.
7. Freeze aliases and parent/child relationships only after those tests survive edge cases.
8. Ratify Objective 6 as a versioned functional-vocabulary contract.
9. Only after **both** S16A acceptance and Objective 6 ratification should S16B semantic implementation derive these functions as trusted gameplay-DNA inputs.
10. Build Deck Functional Health as a downstream consumer, keeping its recommendation thresholds/policies separate from semantic truth.
11. Add the much larger strategy-specific vocabulary later, using it to re-rank and align general-function recommendations rather than redefining them.

---

## 20. Executive conclusion

The emerging architecture is coherent and supports several products at once without making the semantic substrate subjective.

The central separation is:

```text
WHAT THE CARD LITERALLY DOES
  S16A mechanical/semantic facts

WHAT GENERAL JOB THAT CAN PERFORM
  Objective 6 deterministic functional vocabulary

WHAT OTHER CARDS CAN PERFORM A SIMILAR JOB
  S16B gameplay-DNA retrieval / ordering / explanation

WHETHER A DECK HAS THE FUNCTIONS IT NEEDS
  Deck Functional Health consumer

WHICH OF THOSE FUNCTIONAL CARDS BEST FIT THIS STRATEGY
  later strategy-specific tag / alignment layer
```

This lets Foundry tell a player not merely that a deck has “draw” or “removal,” but that it has, for example, abundant filtering and parity with little true card advantage, or plenty of creature removal with no artifact/enchantment/graveyard coverage.

It also lets recommendations preserve what already works: replace a filtering/parity slot with a card that still filters but also generates advantage; replace narrow creature interaction with interaction that retains the same general function while covering a missing permanent class; later, prefer the candidate that also advances the deck's specific strategy.

The intended outcome is not one giant flat tag list. It is a layered, explainable capability system in which mechanical truth remains below functional meaning, functional meaning remains below strategy, and every higher-level recommendation can be traced back to the facts that justified it.
