# Objective 6 — Functional Vocabulary and Deck Functional Health Architecture

**Status:** CAPTAIN DRAFTING / NON-EXECUTING / NOT RATIFIED  
**Date:** 2026-09-13  
**Objective:** 6 — `FOUNDRY_FUNCTIONAL_VOCABULARY_SPECIFICATION`  
**Base evidence branch:** `preflight/objective5-s16b-gameplay-dna-2026-09-12`  
**Base evidence head when drafted:** `034ee0459c5048e0fb3be3d717abd39bb4cbc05e`  
**S16 relationship:** S16A is the lower semantic prerequisite; S16B is the downstream gameplay-DNA consumer.  
**Implementation authorization:** **NONE**. This document does not authorize S16A, S16B, S10–S15, AQ4, Bridge v0, merge, deployment, parser changes, codebook changes, or production tag assignment.

---

## 1. Executive thesis

Objective 5 established that a useful MTG thesaurus needs a **derived functional layer above literal mechanics**, while community vocabulary must remain discovery evidence rather than semantic authority.

Objective 6 now has a clearer product purpose:

> **Define the general, cross-strategy functions that make decks operate, separately from the much larger future vocabulary describing what a particular deck strategy is trying to do.**

A Reanimator deck, Artifact deck, Tokens deck, Voltron deck, typal deck, or unrelated Commander deck can all need broadly useful functions such as:

- mana acceleration;
- mana fixing;
- card access;
- card filtering;
- card advantage;
- interaction;
- spot removal;
- multi-removal;
- board wipes;
- graveyard/artifact/enchantment interaction;
- protection;
- recursion;
- tutors.

Those concepts can serve several products at once:

1. **Searcher/filter surface** — user-facing buttons for the job a player needs.
2. **S16B gameplay-DNA** — functional parents linking different mechanisms that accomplish related jobs.
3. **Deck Functional Health** — count and diagnose what useful functions a deck contains or lacks.
4. **Recommendations** — suggest additions or, preferably when possible, replacements that preserve an existing job while filling another gap.
5. **Later strategic alignment** — re-rank general-function cards according to a deck's specific strategy without redefining the function itself.

The desired end state is **not one enormous flat tag list**. It is a layered, explainable capability system.

---

## 2. Authority boundary for this draft

This document deliberately distinguishes three classes of content.

### 2.1 Captain draft directions

These are decisions or working definitions explicitly stated by the Captain during the current Objective 6 pass. They are preserved here so they are not lost, but Objective 6 as a whole is still `CAPTAIN_DRAFTING_NOT_RATIFIED`.

### 2.2 Existing S16 / Objective 5 architecture

Repository S16 architecture already establishes:

- S16A must preserve a lossless, provenance-bearing semantic representation of Oracle instructions;
- S16B is a downstream functional/gameplay-DNA consumer;
- S16B retrieval, ordering, and explanation are separate concerns;
- community vocabulary cannot overwrite Oracle/CR truth;
- the functional layer should support a DAG/lattice with multiple parents rather than one primary role;
- `UNKNOWN / INSUFFICIENT_EVIDENCE` is preferable to false certainty.

Relevant repository prior art includes:

- `docs/architecture/CARD-READING-PRECISION-ACCEPTANCE.md`;
- `docs/architecture/S16B-GAMEPLAY-DNA-PREFLIGHT-PLAN.md`;
- `docs/architecture/preflight/s16b/S16B-GAMEPLAY-DNA-PREFLIGHT-REPORT.md`;
- `docs/architecture/preflight/s16b/vocabulary-v0.json`;
- `docs/DERIVED-TAG-LAYER-SPEC.md`;
- preserved fact-layer/locality architecture under `refoundation/preservation/`.

The older derived-tag/fact-layer documents are prior art, not authority over newer Objective 6 decisions. They are useful because they already exposed two durable design lessons: derived semantics need provenance, and flattening effects/modal structure produces false equivalence.

### 2.3 Manager re-audit proposals

Some architecture below is a Manager proposal derived from the Captain's product direction and the S16 contracts. These proposals are explicitly labeled and must not silently become Captain rulings merely because this file records them.

---

## 3. Product layers

### 3.1 Layer A — General functional capability

Question:

> **What useful job can this card/effect perform independent of a particular deck strategy?**

Examples:

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

This is the primary Objective 6 surface.

### 3.2 Layer B — Deck Functional Health

Question:

> **What general functions does this deck contain, where are its blind spots, and what is the shape/reliability of its coverage?**

This is a downstream consumer of Objective 6 and S16B. It should measure and explain; it should not redefine semantic membership.

### 3.3 Layer C — Strategy-specific alignment

Question:

> **Of the cards that perform the needed general function, which ones also advance this particular deck's strategy?**

This later layer may eventually contain a very large number of strategy-specific tags and relations.

Examples:

- Reanimator
- Aristocrats
- Voltron
- Tokens
- Spellslinger
- Artifacts-matter
- Graveyard-matters
- Lands-matter
- Superfriends
- Typal/Tribal
- Group Hug
- Group Slug
- Prison

The strategy layer should re-rank or refine general-function candidates. It should not redefine `SPOT_REMOVAL`, `RAMP`, `CARD_ADVANTAGE`, etc.

### 3.4 Avoid combined-tag explosion

Do **not** create a new canonical tag for every strategy/function combination such as:

- `REANIMATOR_SPOT_REMOVAL`;
- `TOKEN_RAMP`;
- `ARTIFACT_CARD_ADVANTAGE`.

Instead retain independent dimensions:

```text
GENERAL FUNCTION + STRATEGIC ALIGNMENT
```

This lets one definition of Spot Removal support every deck while allowing later strategy-aware ranking.

---

## 4. S16 integration

The existing S16 architecture can now be stated as a complete pipeline:

```text
Oracle / Comprehensive Rules
        ↓
S16A — lossless structured semantic parse
        ↓
Objective 6 — deterministic functional vocabulary contracts
        ↓
S16B — gameplay-DNA capability graph / retrieval / ordering / explanation
        ↓
Deck Functional Health — composition / coverage / recommendation consumer
        ↓
Later Strategy Layer — strategy-specific alignment / re-ranking
```

### 4.1 S16A responsibility

S16A determines **what the card says and how its instructions relate**. It should preserve, when present:

- card / face / paragraph / ability / mode / instruction ownership;
- costs separately from effects;
- actor/controller/owner/opponent scope;
- targeting versus choosing versus affect-all;
- exact or symbolic quantities/cardinality;
- source and destination zones;
- immediate/delayed timing;
- duration;
- delivery type;
- conditions and restrictions;
- linked/dependent instructions;
- modal exclusivity and co-availability;
- object identity across linked instructions;
- repeatability and rate limits;
- payments/resources consumed;
- exact Oracle provenance.

S16A should not need to decide that a set of those facts is called `RAMP`, `BLINK`, `MULTI_REMOVAL`, or `CARD_ADVANTAGE`.

### 4.2 Objective 6 responsibility

Objective 6 determines **what general functional concept those facts satisfy**.

Example:

```text
S16A facts:
  exile permanent X
  linked return of same X to battlefield
  return timing = same resolving sequence

Objective 6 result:
  BLINK = true
  BLINK_NOW = true
```

Example:

```text
S16A facts:
  controller individually selects X creature objects
  X >= 2 is a legal value/path
  selected objects are removed/neutralized

Objective 6 result:
  MULTI_REMOVAL = true
```

### 4.3 S16B responsibility

S16B consumes the derived functional/capability layer and performs its intended jobs:

1. **Retrieval** — surface functional neighbors.
2. **Ordering** — rank closer substitutes above loose broad-category overlaps.
3. **Explanation** — state both the shared job and mechanically relevant differences.

S16B should not silently invent the definition of a functional term during ranking.

---

## 5. Vocabulary/ontology laws

### 5.1 Parent/child means logical implication

**Manager proposal strongly supported by the current Captain model.**

Use `IS_A` parenthood only when the implication always holds:

> **If X is a child of Y, every X must also be Y.**

Current examples that fit:

```text
BLINK_NOW     → BLINK
BLINK_DELAYED → BLINK
MANA_ROCK     → RAMP → MANA_ACCELERATION
MANA_DORK     → RAMP → MANA_ACCELERATION
LAND_RAMP     → RAMP → MANA_ACCELERATION
HARD_COUNTER  → COUNTERSPELL
SOFT_COUNTER  → COUNTERSPELL
```

Parenthood should not be used merely because two concepts are related.

### 5.2 Use a DAG/lattice, not a rigid tree

A card/effect can legitimately have several memberships/parents.

Example:

```text
Sol Ring
  MANA_ACCELERATION
  RAMP
  MANA_ROCK
  FAST_MANA
```

No forced single primary role is necessary.

### 5.3 Siblings do not need to exhaust a parent

Do not invent a narrow child merely to force every parent member into a partition.

A future card may be `MANA_ACCELERATION` without belonging to any currently named child.

### 5.4 Multi-label membership is expected

One card can legitimately satisfy many functions. Deck percentages based on these labels are therefore coverage percentages and need not sum to 100%.

### 5.5 Domain-specific accounting stays domain-specific

`MANA_PARITY` means parity in the mana-development dimension, not overall card value.

Likewise card-resource parity/advantage should not silently absorb creature, life, board, or tempo value.

### 5.6 Unknown is a valid result

If the ratified contract cannot be proven from S16A facts, return `UNKNOWN / INSUFFICIENT_EVIDENCE` rather than guessing.

---

## 6. Effect/path-first semantics

**Manager re-audit proposal; strongly aligned with S16A modal conservation.**

Functional membership should first attach to the smallest meaningful executable semantic path/effect, then roll up to card capability.

```text
semantic effect / mode / legal choice path
        ↓
functional membership of that path
        ↓
card CAN_PERFORM(function)
```

This prevents a modal card from being treated as though mutually exclusive effects all occur simultaneously.

Example: Cryptic Command can expose several capabilities, but the representation must retain which selected modes can coexist in one cast.

This law becomes especially important for deck-health counting: a modal card can cover several categories without becoming several independent physical sources.

---

## 7. Curated function labels versus orthogonal facets

**Manager re-audit proposal — recommended for Captain consideration.**

A major risk is combinatorial tag explosion.

Foundry should not require a unique canonical tag for every combination such as:

- instant-speed artifact Spot Removal that exiles;
- repeatable creature-based enchantment interaction;
- sorcery-speed selected-many creature destruction;
- delayed two-mana conditional card access.

Instead distinguish:

### 7.1 Curated function labels

These are concepts worth naming and exposing directly to users:

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

### 7.2 Orthogonal capability facets

These preserve the important mechanical differences:

- object/target class: creature, artifact, enchantment, planeswalker, land, card, spell, ability, graveyard card, player, etc.;
- scope: one, selected-many, all matching objects, all opponents, symmetric, asymmetric;
- action/method: destroy, exile, bounce, sacrifice, counter, damage, prevent, prohibit, tax, etc.;
- source/destination zone;
- mana/resource cost;
- timing/delivery;
- immediate versus delayed;
- duration;
- one-shot versus repeatable;
- conditional versus unconditional;
- self-contained versus external dependency;
- controller-driven versus opponent-dependent;
- modal/optional status;
- co-availability with other functions on the card;
- compensation/downside;
- numeric magnitude.

The UI can combine a function with facets without creating another semantic tag.

Example:

```text
Function: Spot Removal
Target: Artifact OR Enchantment
Timing: Instant-speed
Method: Exile OR Destroy
Mana value: <= 3
```

---

## 8. Functional membership provenance

**Manager re-audit addition supported by historical Foundry prior art.**

A derived function should never become an opaque boolean detached from the facts that justified it.

For every derived functional membership, Foundry should be able to recover at least:

- canonical functional term/version;
- derivation contract/rule version;
- semantic owner/effect/choice path that qualified;
- exact S16A fact identifiers/coordinates used;
- relevant Oracle evidence span(s);
- result state: true / false if explicitly evaluated / unknown;
- any facets used to establish the result;
- any dependency/conditionality classification;
- derivation/build version.

Conceptually:

```text
membership:
  card: <oracle_id>
  function: MULTI_REMOVAL
  function_version: objective6/<version>
  semantic_path: <S16A owner/path>
  evidence:
    - quantity = X, with legal X >= 2
    - selection = individually chosen creatures
    - action = exile
  oracle_provenance: <span refs>
  result: true
```

This enables:

- auditability;
- deterministic rebuilds;
- explanation to the user;
- safe contract revisions;
- diffing when Oracle text or definitions change;
- debugging false positives/negatives;
- keeping strategy/community judgments separate from mechanical evidence.

The historical `DERIVED-TAG-LAYER-SPEC.md` and fact-layer work already treated provenance class/evidence as important. Objective 6 should preserve that lesson while using the newer S16A semantic substrate rather than reviving old plumbing.

---

## 9. Captain draft directions captured so far

### 9.1 Enabler / Payoff — DEFERRED

Forget/defer `ENABLER` and `PAYOFF` for the initial Objective 6 surface.

Reason: they are relational (`enabler for what?`, `payoff for what?`) and would force strategy/context modeling before the core cross-strategy vocabulary is settled.

Reserve the terms for later; do not make initial S16B depend on them.

### 9.2 Blink family

`BLINK` is the parent.

```text
BLINK
├─ BLINK_NOW
└─ BLINK_DELAYED
```

Working meanings:

- **Blink** — a permanent is exiled and subsequently returned to the battlefield through linked instructions/effects.
- **Blink-Now** — the return occurs as part of the same resolving effect/sequence rather than at a later game time.
- **Blink-Delayed** — the exile establishes a later return, such as at the beginning of the next end step.

Object class, controller, tapped status, return-control changes, etc. should remain lower facets rather than creating unnecessary child terms immediately.

### 9.3 Removal scope family

#### Spot Removal

One card/effect removes, neutralizes, or otherwise interacts with **one individually selected object**. The object must be targeted or otherwise specifically chosen.

#### Multi-removal

One card/effect can remove/neutralize **two or more distinct game objects individually chosen by the caster/controller**.

There is no upper numerical ceiling.

Captain examples:

- Curse of the Swine — selected X creatures;
- Hex — six selected creatures;
- Cryptic Command can qualify through a legal path that interacts with multiple distinct chosen objects, e.g. a chosen spell plus chosen permanent.

Naturalize is not Multi-removal merely because the caster can choose what single object it removes.

#### Board Wipe

A wipe affects the **entire matching battlefield scope** rather than individually selecting affected permanents.

Current dividing law:

```text
individual selection of >=2 objects → MULTI_REMOVAL
universal matching battlefield set  → BOARD_WIPE / ONESIDED_BOARD_WIPE
```

#### One-sided Board Wipe

Universal matching removal/neutralization over opponent side(s) while excluding the caster/controller's matching side.

Ruinous Ultimatum is the Captain's gold-standard example.

### 9.4 Mana family

#### Mana Acceleration

Broad parent for qualifying effects/cards that advance usable mana availability beyond the relevant baseline.

#### Ramp

`RAMP` is reserved for durable/permanent forms of mana acceleration capable of continuing to provide mana across turns.

Current inclusion families:

- Mana Dorks;
- Mana Rocks;
- Land Ramp;
- other qualifying durable mana-producing permanents.

Current exclusions:

- normal one-mana-producing lands;
- bounce lands such as Boros Garrison;
- additional-land-play permission;
- one-shot rituals.

A land that durably produces more than one mana and does not sacrifice/leave the battlefield to do so can qualify; Phyrexian Tower was given as an example.

#### Land Ramp

Cards that obtain a land from the library and put it onto the battlefield.

#### Land Add

Cards that allow additional land plays. This is Mana Acceleration but explicitly **not Ramp**, because the player still needs lands available to play.

#### Mana Dork

Keep familiar creature mana-source family.

#### Mana Rock

Keep familiar artifact mana-source family.

#### Fast Mana

Current Captain rule:

- qualifying card/effect costs two mana or less;
- can produce the qualifying mana immediately;
- produces more mana than its casting cost.

Examples:

- Sol Ring: costs 1, immediately can make 2 → Fast Mana.
- A two-mana card would need to immediately make at least 3 mana.

#### Ritual

Keep Ritual as one-shot temporary/burst mana. It participates under Fast Mana where the Fast Mana contract is satisfied.

#### Mana-Parity

`MANA_PARITY` evaluates the **mana-development transaction**, not the overall value of the card.

Captain examples:

- **Boros Garrison** — consumes the land play, enters tapped, returns a land, and later taps for two. It reconfigures mana production but normally does not put the player ahead of ordinary development simply by being played.
- **Priest of Gix** — spends mana and refunds an equivalent amount through its own effect; the mana transaction may be parity even though the player also receives a creature body.

Working principle:

> A Mana-Parity card/effect replaces, refunds, or reconfigures mana-producing development without itself creating net acceleration over the baseline development/resources it displaced or consumed.

The exact baseline/accounting window still needs hard edge-case tests before ratification.

### 9.5 Card-resource family

#### Draw

`DRAW` remains literal rules-action draw and is a parent for draw-specific children because some cards specifically care about drawing.

#### Draw-Now

Qualifying draw is produced immediately rather than establishing a future draw event.

#### Draw-Delay

The source establishes a later draw event. Mishra's Bauble and Arcane Denial were given as examples.

Final implementation should depend on semantic timing/dependency rather than a literal “upon resolution” wording test.

#### Card Advantage

Current Captain direction:

- spending/casting the source counts as an expenditure;
- the source's own text/functionality must eventually produce net-positive usable card resources;
- literal draw is not required;
- temporary playable exile/impulse access may count;
- usable access to opponents' cards may count;
- the advantage need not be immediate;
- the intended distinction excludes cards that require a separate external outlet/action before their engine can begin producing the advantage.

Examples:

- Brainstealer Dragon → Card Advantage;
- Phyrexian Arena → Card Advantage;
- Sram, Senior Edificer → not this direct Card Advantage label under the current dependency distinction.

#### Potential Card Advantage

A card whose own text contains machinery capable of producing true card advantage if qualifying conditions/events/actions occur.

Captain examples:

- Sram, Senior Edificer;
- Rhystic Study;
- Esper Sentinel;
- Aurelia, the Law Above;
- Trouble in Pairs.

The exact direct-vs-potential dependency predicate needs edge-case testing.

#### Card-Parity

Provides enough usable card resource to replace the expended card/resource but does not create net-positive card quantity under the defined accounting window.

#### Card Filtering

Parent for effects that improve card quality/selection without requiring net card gain, including Looting, Rummaging, Scry, Surveil, and related selection/reorganization families.

The Captain also wants an `INDEX`-like family for top-library reorganization without card parity/advantage.

#### Cantrip

Current Captain contract direction:

- qualifying action costs two mana or less;
- the card's own printed cost-reduction/payment mechanics count;
- unrelated external reducers do not create Cantrip membership;
- action gives immediate access to at least one usable card resource;
- literal Draw is not required;
- selecting/putting a card into hand may qualify;
- Wrenn's Resolve-style temporary playable access may qualify;
- action must at least replace the spent card/resource;
- card type does not matter;
- Cycling qualifies only when the Cycling activation cost is two or less;
- multi-label membership is expected.

Ponder and Brainstorm are gold-standard Captain examples.

---

## 10. Functional versus strategy vocabulary

Objective 6 should primarily settle **general deck-function vocabulary**.

Strategy/archetype vocabulary belongs to the later strategic layer except where a separately named card-level function exists.

Useful naming discipline:

```text
REANIMATE        = card/effect function
REANIMATOR       = strategy

TOKEN_GENERATOR  = card/effect function
TOKENS           = strategy

DIRECT_DAMAGE / BURN_EFFECT = function
BURN_ARCHETYPE              = strategy
```

This allows the future strategy tag surface to become extremely large without corrupting the cross-strategy utility layer.

---

## 11. Deck Functional Health model

**Working downstream product concept — not semantic authority.**

A deck-health analyzer should consume deterministic functional memberships plus objective facets.

### 11.1 Core metrics

For each function, useful measurements include:

1. **Presence** — at least one source or none.
2. **Count** — number of unique cards/slots that can perform the function.
3. **Density** — fraction of relevant deck slots that can perform it.
4. **Breadth** — number of different problem/object/resource classes covered.
5. **Redundancy** — number of independent sources for the same need.
6. **Timing profile** — instant/sorcery/activated/static; immediate/delayed; early/late availability.
7. **Cost profile** — mana/resource cost distribution.
8. **Reliability/dependency** — self-contained, conditional, opponent-dependent, setup-dependent, trigger-dependent, mode-limited.
9. **Co-availability** — whether several capabilities on one card can be used together or are mutually exclusive.
10. **Strategic alignment** — later: how many general-function sources also advance the deck's strategy.

### 11.2 Percentages are coverage, not exclusive partitions

A card can count in several categories, so function percentages need not sum to 100%.

Example:

```text
Ramp:                  9 cards
Mana Fixing:            7 cards
Card Filtering:        11 cards
Card Parity:             7 cards
Card Advantage:          2 cards
Potential Card Advantage:1 card
```

### 11.3 Do not create an overall deck-quality score yet

A single percentage for “how good the deck is” would silently encode subjective weights among functions and strategies.

Initial reports should expose observable composition and scoped diagnostics.

### 11.4 Avoid universal threshold dogma

Foundry can factually say:

> “This deck contains zero enchantment interaction.”

or:

> “This deck contains many filtering/parity sources but no direct Card Advantage.”

A rule such as “every Commander deck must contain exactly N removal spells” is a downstream strategic heuristic, not Objective 6 truth.

Any future target ranges should be configurable, format/strategy-aware, evidence-backed where possible, and clearly separate from semantic membership.

---

## 12. Interaction coverage should be a matrix, not one count

A deck can contain many removal cards while still being unable to answer artifacts, enchantments, graveyards, or the stack.

Candidate coverage domains:

| Problem/resource domain | Example capability |
|---|---|
| Creatures | creature Spot/Multi/Mass removal |
| Artifacts | artifact removal/neutralization |
| Enchantments | enchantment removal/neutralization |
| Planeswalkers | planeswalker-capable interaction |
| Lands | land interaction/destruction |
| Graveyards | purge, targeted exile, occupancy denial, access lock |
| Stack — spells | Counterspell/spell interaction |
| Stack — abilities | ability counter/interaction |
| Hands | discard/hand disruption |
| Combat | Fog/combat manipulation where relevant |
| Player actions | Silence/tax/prohibition/restriction families |

Many of these should be represented by **function + facets**, not a separately invented canonical tag for every row.

A downstream report could say:

```text
Interaction coverage
  Creature:      8 sources
  Artifact:      1 source
  Enchantment:   0 sources
  Graveyard:     0 sources
  Stack:         3 sources

Observed blind spots
  - no enchantment interaction
  - no graveyard interaction
```

Words such as “strong” or “low” require a downstream threshold policy; counts and zero/nonzero status do not.

---

## 13. Counting law: capability is not independent-source count

**Manager re-audit proposal — important for future deck-health correctness.**

A modal or multi-role card may cover several functions, but it is still one physical source/slot.

Deck analysis should distinguish:

- **capability coverage** — every function a card can perform;
- **unique source count** — number of physical cards providing a function;
- **simultaneous/co-available capability** — functions usable together;
- **modal alternatives** — functions that compete within one cast/activation;
- **capability concentration** — how much apparent deck coverage depends on a small number of multi-role cards.

Example: a charm that can destroy an artifact **or** enchantment contributes to both coverage categories, but does not create two independent removal sources for redundancy calculations.

This directly relies on S16A preserving modal exclusivity rather than flattening cards into fact bags.

---

## 14. Reliability and conditionality should remain visible

The Captain's Card Advantage versus Potential Card Advantage distinction reveals a broader useful dimension: functional coverage can differ in dependency/reliability.

Where possible, preserve facets for:

- self-contained versus requiring another action/card;
- guaranteed versus conditional;
- controller-driven versus opponent-dependent;
- immediate versus delayed;
- one-shot versus repeatable;
- activation required versus passive/static;
- board-state dependency;
- hand/deck/graveyard dependency;
- rate limits such as once-per-turn;
- optional/mode-limited access.

This can produce better explanations without creating a new named tag for every combination.

Example:

> “Your deck has six possible extra-card sources, but four depend on opponents taking a qualifying action and only one is self-contained repeatable Card Advantage.”

---

## 15. Recommendations should prefer function-preserving upgrades

A powerful downstream use of Searcher B is to recommend **replacements**, not merely additions.

Example observation:

```text
Card Filtering:           high density
Card Parity:              high density
Card Advantage:           none
Potential Card Advantage: low
```

Rather than simply telling the player to add more cards, Foundry can seek candidates that:

1. preserve an existing needed function;
2. fill a missing function or coverage domain;
3. maintain acceptable mechanical constraints;
4. later, improve strategic alignment.

Example recommendation logic:

> Replace a filtering/parity slot with a card that still filters but also generates Card Advantage.

Or:

> Replace narrow creature-only interaction with a card that preserves Spot Removal while also covering artifacts/enchantments.

A future recommendation explanation should state:

- what gap was observed;
- what the current card contributes;
- what the replacement preserves;
- what new capability it adds;
- important timing/cost/restriction differences;
- later, why it aligns with the deck strategy.

---

## 16. Strategy alignment should be additive re-ranking

Example:

```text
Need: SPOT_REMOVAL
Strategy: REANIMATOR
```

General functional retrieval first finds qualifying Spot Removal.

The future strategy layer can then prefer cards that also fit Reanimator, such as recursion-friendly creatures or graveyard-synergistic effects.

The same Spot Removal definition remains valid when the deck is Artifacts, Tokens, Voltron, or something else.

This separation lets Foundry answer two different questions:

1. **Does this solve the general deckbuilding need?**
2. **Does it solve that need in a way that reinforces this deck?**

---

## 17. Additional downstream analyses worth preserving

These arose from the re-audit and use the same functional/facet substrate.

### 17.1 Functional breadth

How many materially different general needs can the deck answer?

### 17.2 Redundancy / single points of failure

How many independent sources provide each important capability?

A tutor improves access to another card, but should not automatically be counted as an independent copy of every function it can search for unless a separate downstream **effective access** model is explicitly designed.

### 17.3 Availability profile

At what mana costs/timings can the deck actually access a function?

A deck may technically contain removal but only at expensive mana values or sorcery speed.

### 17.4 Coverage overlap

Which cards efficiently cover several blind spots at once?

### 17.5 Capability concentration

Multi-role cards are efficient but can make apparent coverage fragile when many categories depend on one or two cards.

### 17.6 Format-aware density denominator

Percentages must state their denominator. In Commander, a product might report the 99 noncommander slots separately from capabilities available from the commander.

This is a UX/analysis policy, not semantic law.

### 17.7 Always-accessible versus library-bound capability

Commanders and other always-accessible resources can alter practical availability. Preserve this for downstream deck-health logic rather than redefining the function itself.

### 17.8 Replacement opportunity score — later, not semantic truth

A downstream recommender could identify cards occupying a heavily saturated function while failing to cover important missing functions, then prioritize them as possible swap candidates.

Any numeric scoring formula would be product policy and must not become semantic authority.

---

## 18. Objective 6 term contract template

Before a functional term becomes executable, define it with a contract like:

```text
TERM:
Foundry canonical name:
User-facing aliases:
Status: DRAFT / RATIFIED / DEFERRED

Kind:
- GENERAL_FUNCTION
- MECHANICAL_FAMILY
- ACCOUNTING_FUNCTION
- STRATEGY
- RELATIONAL
- OTHER

Parent term(s):
Child term(s):

Exact Foundry definition:

Required S16A semantic inputs:
- action/effect
- actor/affected actor
- object/target class
- target/select/universal scope
- quantity/cardinality
- source zone
- destination zone
- timing/duration
- cost/payment
- condition/dependency
- repeatability/rate limit
- modal/co-availability structure
- linked-object identity
- other

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

Gold positives:
- ...

Hard negatives / near misses:
- ...

Known edge cases:
- ...

Derivation provenance required:
- term/version
- semantic path/owner
- S16A fact refs
- Oracle evidence refs

Explanation contract:
- why membership is true/unknown
- which facts prove it

Captain ruling date/version:
```

If a term needs a fact that S16A cannot represent without approximation, the correct result is **STOP** for that term until either the term contract is changed or S16A is intentionally expanded.

---

## 19. Validation / acceptance concept

A term should not be ratified merely because its prose sounds reasonable.

Each important term should have:

- clear gold positives;
- hard negatives;
- near misses;
- boundary values around thresholds;
- modal cases where relevant;
- different Oracle wordings implementing the same functional result;
- similar Oracle wording that should fail the functional label;
- tests that every declared child implies every declared parent;
- tests that lower mechanical distinctions remain available after functional roll-up;
- provenance checks showing exactly why a result was derived.

Example removal set:

```text
Naturalize
  SPOT_REMOVAL = yes
  MULTI_REMOVAL = no

Curse of the Swine, legal X >= 2
  MULTI_REMOVAL = yes
  BOARD_WIPE = no

Hex
  MULTI_REMOVAL = yes
  BOARD_WIPE = no

“Destroy all creatures.”
  BOARD_WIPE = yes
  MULTI_REMOVAL = no

“Destroy all creatures you don't control.”
  ONESIDED_BOARD_WIPE = yes
```

Executable rules must ultimately bind to semantic facts, not card-name special cases.

---

## 20. Open / unresolved items

Keep these visible rather than silently deciding them.

### 20.1 Impulse naming

Current Captain semantic distinction:

- parent `Impulse`;
- one child for exile/top access playable until end of turn;
- another child for access playable until end of next turn.

Current draft names are `Impulse-Select` and `Impulse-Draw`.

Objective 5 research found a possible terminology collision because Wizards/R&D has used “impulsing” for a different top-N selection concept. Preserve the timing distinction, but re-audit final canonical/user-facing names before ratification.

### 20.2 Token Generator

`TOKEN_GENERATOR` appeared in the edited lexicon without an explicit Captain verdict. Leave unratified until addressed.

### 20.3 Alt-Tutor / Light-Tutor

The Captain proposed a user-friendly tutor-alternative concept for deep selective library access.

The product idea is useful; internal canonical name versus user-facing alias remains open. A mechanically explicit internal label such as `DEEP_SELECTIVE_LIBRARY_ACCESS` with a friendlier UI alias is one possible design, not a ruling.

### 20.4 Mana-Parity accounting window

The intended concept is clearer after Boros Garrison/Priest of Gix, but the exact baseline/time window needs adversarial examples.

### 20.5 Card Advantage versus Potential Card Advantage

The intended distinction is clear; the precise dependency predicate needs edge-case testing.

### 20.6 Enabler / Payoff

Explicitly deferred.

### 20.7 Strategy/archetype vocabulary

Reserved for the later strategic layer unless a separate card-level function is being defined.

---

## 21. Non-goals and guardrails

This draft does **not** authorize or imply that Foundry should now:

- implement Objective 6 tags in production;
- modify the codebook/ACTIVE axes;
- change parser behavior;
- begin S16B implementation;
- import community labels as Oracle/CR truth;
- infer whole-deck archetypes from one card in isolation;
- assign Enabler/Payoff relations;
- produce a universal deck-quality percentage;
- hard-code universal quantities of ramp/removal/draw as truth;
- treat one modal card as several independent sources;
- flatten mutually exclusive modes;
- create a tag for every cross-product of function, target, timing, cost, and strategy;
- count a tutor as an independent copy of everything it can fetch without an explicit effective-access model;
- let strategy-specific judgments override mechanical facts;
- silently classify uncertain cards;
- resurrect old derived-tag plumbing merely because older architecture explored similar semantic needs.

The governing principle remains:

> **PRESERVE TRUTH, NOT PLUMBING.**

---

## 22. Recommended Objective 6 sequence

1. Finish the Captain vocabulary pass over general-function candidates.
2. Classify every candidate as general function, mechanical family, accounting function, strategy, relational, or deferred.
3. Ratify the curated-label-versus-facet architecture or replace it with an equally explicit alternative.
4. Write a deterministic contract for each retained general function.
5. Name the exact S16A semantic inputs required by every contract.
6. STOP any term whose required fact cannot be represented without approximation.
7. Build gold positives, hard negatives, boundary cases, modal cases, and parent-implication tests.
8. Define derivation provenance/versioning so memberships remain auditable.
9. Freeze aliases and parent/child relationships only after the boundary tests survive.
10. Ratify Objective 6 as a versioned functional vocabulary specification.
11. Only after **both** S16A acceptance and Objective 6 ratification should S16B derive these functions as trusted gameplay-DNA inputs.
12. Build Deck Functional Health as a downstream consumer, with recommendation thresholds kept separate from semantic truth.
13. Add the much larger strategy-specific vocabulary later and use it to re-rank general-function recommendations rather than redefining them.

---

## 23. Final architecture summary

```text
WHAT THE CARD LITERALLY DOES
  S16A semantic facts + exact provenance

WHAT GENERAL JOB THOSE FACTS CAN PERFORM
  Objective 6 deterministic functional vocabulary

WHY FOUNDRY ASSIGNED THAT JOB
  versioned derivation provenance back to S16A facts / Oracle spans

WHAT OTHER CARDS CAN PERFORM A SIMILAR JOB
  S16B retrieval / ordering / explanation

WHETHER A DECK HAS THE FUNCTIONS IT NEEDS
  Deck Functional Health
  presence / count / density / breadth / redundancy / timing / dependency

WHICH FUNCTIONAL CARDS BEST FIT THIS DECK'S PLAN
  later strategy-specific vocabulary and alignment/re-ranking
```

This architecture lets Foundry say more useful things than “you have X draw spells” or “you have Y removal spells.”

It can eventually say, for example:

> You have substantial Card Filtering and Card-Parity coverage but almost no true Card Advantage or Potential Card Advantage.

or:

> You have eight interaction sources, but nearly all of them only answer creatures. You currently have no enchantment or graveyard interaction.

And instead of always recommending that the player add more cards, Searcher B can look for **function-preserving replacements**:

> Replace a saturated filtering/parity slot with a card that still performs the needed filtering job while also increasing Card Advantage.

Later, the strategy layer can refine that same recommendation:

> Of the cards that solve the general functional gap, prefer the ones that also reinforce this deck's Reanimator / Artifact / Tokens / other strategy.

The result is a layered deckbuilding intelligence system in which mechanical truth remains below functional meaning, functional meaning remains below strategy, and every recommendation can remain explainable back to the facts that justified it.
