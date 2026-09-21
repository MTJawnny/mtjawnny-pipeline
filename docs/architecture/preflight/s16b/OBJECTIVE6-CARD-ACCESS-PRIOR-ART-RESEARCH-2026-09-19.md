# Objective 6 — Card Access Prior-Art Research

**Date:** 2026-09-19  
**Status:** **RESEARCH / ADVERSARIAL INPUT — NO SEMANTIC RATIFICATION**  
**Scope:** Breadth-first review of established Magic terminology and mechanics around drawing, filtering, card selection, tutoring, alternate-zone access, recursion, and card-advantage theory. This compares external terminology with the current Foundry Card Access model but does not itself change Captain-approved semantics.

## 1. Research question

The Captain requested a Ramp-style prior-art pass for **Card Access** before finalizing the semantic foundation.

The research asks:

1. What terms do Wizards and players already use for getting, seeing, selecting, replacing, recovering, or temporarily accessing cards?
2. Which distinctions have real rules/mechanical consequences?
3. Which Foundry distinctions are useful internally but unnecessarily confusing as public nouns?
4. What is missing from the current Foundry Card Access surface?
5. Which current Foundry names or predicates conflict with established Magic usage?

## 2. External terminology map

### 2.1 Card draw

Wizards treats **card draw** as the literal operation of drawing cards. This is mechanically distinct from merely gaining access to cards in other zones.

Important consequence for Foundry: `draw` should remain an explicit primitive/event signature because many cards care specifically about drawing, and alternate access such as exile-play permission does not count as drawing.

### 2.2 Card advantage

Established Magic theory defines Card Advantage relationally: obtaining effectively more card resources than an opponent. Wizards' Level One material also distinguishes raw/technical card counts from **virtual card advantage**, where game-state relevance and card quality matter.

Foundry's current relative Card Advantage direction is broadly aligned with the established definition. The main Foundry extension is explicit multiplayer pairwise accounting.

**Important boundary:** `virtual card advantage` and `card quality` depend on context and evaluative game relevance. They belong in a later strategic/deck-context layer, not canonical mechanical truth.

### 2.3 Card filtering / smoothing / card flow

Wizards uses **card filtering** broadly. Their examples include looking at the top N cards, choosing a subset to keep/use, and disposing of the rest. Wizards also uses broader design terms such as **smoothing** and **card flow** for mechanics that reduce draw variance.

This is broader than Foundry's current public boundary between `Card Filtering` and `Card Prospecting`.

Wizards' set-design vocabulary groups under smoothing/card flow mechanisms such as:

- scry;
- surveil;
- looting;
- rummaging;
- cycling;
- card draw;
- top-N selection (sometimes called `impulsing` internally by R&D);
- tutoring.

This supports a common lower-level card-access substrate rather than multiple near-synonymous mechanical trees.

### 2.4 Looting and rummaging

Established R&D vocabulary:

- **Looting** — draw, then discard.
- **Rummaging** — discard, then draw.

These have real rules consequences and should be preserved as distinct mechanical patterns/aliases beneath broader Filtering rather than as separate top-level trunks.

### 2.5 Scry and surveil

Both are smoothing/filtering operations over the top of the library.

Surveil additionally moves unwanted cards to the graveyard, creating graveyard-loading consequences that scry does not.

Foundry's existing primitive/composition approach is well suited to this:

- Filtering;
- plus graveyard movement/loading for surveil.

### 2.6 Cantrip

This is the clearest terminology mismatch discovered.

Wizards consistently uses **cantrip** for a spell/card that draws a single card or has a `draw a card` rider, historically understood as replacing itself. Wizards does **not** impose a universal mana-value-2-or-less requirement, and established usage does not require the card to have an additional distinct function beyond the replacement draw.

Therefore Foundry's current Cantrip predicate — MV <= 2 plus replacement plus a separate additional function — uses a familiar Magic word for a materially narrower custom class.

**Research recommendation:** before S16B freeze, either:

1. realign `Cantrip` with established Magic usage and represent mana value / additional function separately; or
2. preserve the custom predicate under a different Foundry-specific name.

Do not silently keep the current narrow definition under the public word `Cantrip` without explicit Captain adjudication.

### 2.7 Tutoring

Established use of **Tutor** matches Foundry well: targeted retrieval from the library for a particular card or a card satisfying criteria.

Tutor destination is not inherently restricted to hand. Official discussion readily includes cards that search and put a card directly onto the battlefield.

Foundry's current dimensions — eligibility/domain, destination, quantity, reveal/visibility, and costs/dependencies — are appropriate.

### 2.8 Bounded top-N extraction

Foundry currently calls this **Card Prospecting**:

- inspect a bounded library sample;
- select one or more cards;
- grant selected cards privileged access/use.

External terminology is inconsistent:

- Wizards often simply calls this **card filtering**;
- R&D has also used **impulsing** for `look at top N, take one` patterns;
- players often say **dig**, **digging**, or **card selection**.

No external term is both universally player-friendly and mechanically exclusive.

**Research recommendation:** the mechanical distinction may be worth preserving internally, but a separate public `Card Prospecting` trunk is probably unnecessary. Consider representing bounded extraction as a Filtering subtype/pattern with coordinates such as sample size, eligibility, quantity selected, destination, and disposition of unselected cards.

This would also remove a weak placeholder name already flagged for the final naming pass.

### 2.9 Impulsive draw / temporary exile access

Wizards uses **impulsive draw** for effects that exile cards and permit them to be played/cast for a limited duration.

Rules-wise this is **not drawing**. It creates temporary usable access from exile.

Foundry currently anticipates alternative-zone playable access in Card Advantage accounting, but this deserves explicit lower-level representation because duration, play-vs-cast permission, land permission, visibility, and expiration all matter.

Candidate mechanical facts:

- source zone;
- access zone = exile;
- cast vs play permission;
- duration / expiration;
- card-type restriction;
- whether unused cards remain exiled;
- whether mana cost is paid normally;
- visibility.

`Impulsive Draw` can remain a community/Wizards alias mapping to this mechanical pattern.

### 2.10 Top-of-library access

Cards such as Future Sight, Oracle of Mul Daya, Mystic Forge, and Bolas's Citadel expose or allow play/casting from the top of the library without drawing the card first.

This is mechanically distinct from:

- drawing;
- tutoring;
- bounded filtering;
- impulsive exile access.

Foundry should preserve **top-library access** as an access mode / source-zone pattern. Whether it deserves a public noun can wait for the naming audit.

Important coordinates include:

- look/reveal top card;
- cast vs play;
- eligible card types;
- cost/payment modification;
- once-per-turn vs continuous access;
- information visibility.

### 2.11 Graveyard access / regrowth / recursion

Wizards uses design terms such as **regrowing** for returning graveyard cards to hand, while the broader player term **recursion** is common.

Foundry already has a broader Graveyard Access parent. That is useful and should remain cross-linked to Card Access rather than duplicated inside it.

Examples can then decompose into:

- graveyard -> hand;
- graveyard -> battlefield (reanimation / deployment bypass);
- cast/play from graveyard;
- graveyard -> library.

### 2.12 Wheels

Wizards recognizes **wheeling** as the pattern where players discard hands and draw replacement hands/cards.

Foundry should continue treating Wheel effects compositionally:

- Hand Disruption against opponents;
- draw / hand replacement for affected players;
- Filtering/refill implications;
- Card Advantage determined by actual player-relative resource deltas.

Wheel does not need to displace those primitives, but the familiar term is useful as a named pattern/alias.

### 2.13 Cycling and connive

Both reinforce the compositional model.

- Cycling: discard/consume the cycling card -> draw a card; normally Card Replacement/card-neutral and Filtering/smoothing.
- Connive: draw -> discard, plus a counter consequence depending on the discarded card.

These should be distilled through the Keyword Consequence Registry rather than requiring new Card Access trunks.

### 2.14 Cascade and discover

These are important adversarial cases because they provide card/spell access from the library without fitting ordinary draw, Tutor, or player-selected bounded Filtering.

They sequentially traverse/exile library cards until a qualifying card is found, then provide privileged use:

- Cascade: optional cast without paying mana cost under its rules restrictions;
- Discover: cast without paying mana cost or put the discovered card into hand.

These should be represented as library-access event structures in the keyword registry, with their free-cast/payment consequences separately represented.

They are evidence that Foundry needs a generic lower-level **access operation** rather than relying entirely on named public Card Access families.

## 3. Comparison with current Foundry model

Current working public Card Access vocabulary is approximately:

- Card Replacement;
- Card Advantage;
- Card Filtering (recently renamed from Card Sifting);
- Card Prospecting (working name);
- Tutor;
- Cantrip as a narrower rigid leaf.

Related concepts exist elsewhere:

- Graveyard Access;
- Mill;
- Hand Disruption / Wheels;
- Engine / Card Engine;
- future realization / strategic evaluation.

### 3.1 Strongly aligned parts

- **Card Advantage is not synonymous with draw.** Correct and supported by established theory.
- **Tutor vs bounded sample selection.** The mechanical distinction is real.
- **Filtering as the broad player-facing term.** Strongly supported by Wizards terminology.
- **Looting/rummaging/surveil/cycling as compositional mechanics.** Strong.
- **Alternative-zone access can contribute usable card resources.** Correct direction.
- **Strategic judgment separated from canonical facts.** Strong; especially important for virtual card advantage/card quality.

### 3.2 Likely over-modeled public distinctions

#### Card Prospecting

The internal predicate is useful, but external vocabulary usually treats this territory as filtering/card selection/digging. A separate public trunk risks explaining a distinction to players that Wizards itself usually does not expose as a separate family.

Working research direction: **collapse the public noun into Filtering while retaining bounded-extraction coordinates/predicate internally.**

#### Card Replacement

`Card Replacement` is mechanically understandable but is not a major established public Magic category. Players more often say that a card **replaces itself** or is **card-neutral**.

Because Foundry already preserves resource deltas, Card Replacement may ultimately be better modeled as a derived access/accounting pattern rather than a major user-facing trunk:

`card resource expended -> one usable card resource gained = parity/replacement`.

This is not yet a semantic ruling; it is a candidate simplification to test.

### 3.3 Clear terminology mismatch

#### Cantrip

Current Foundry usage is narrower than established usage. This should receive explicit Captain adjudication before freeze.

### 3.4 Missing or under-explicit mechanical access modes

Foundry should ensure the lower-level substrate can directly represent:

1. **literal draw**;
2. **temporary exile access / impulsive draw**;
3. **top-of-library play/cast access**;
4. **graveyard access**;
5. **broader-library targeted retrieval / Tutor**;
6. **bounded library filtering/extraction**;
7. **sequential library traversal to first qualifying card** (Cascade/Discover-style);
8. **hand exchange / wheel / loot / rummage**;
9. **reordering/disposition without acquisition** (scry/surveil/Index-style);
10. **direct destination access** such as library -> battlefield.

The public UI does not need ten nouns. The machine substrate does need these distinctions.

## 4. Proposed simplification direction for later Captain adjudication

A cleaner architecture suggested by the research is:

```text
CARD ACCESS [UI/navigation umbrella]
|
+-- Card Filtering [public family]
|   +-- scry / surveil / looting / rummaging / cycling patterns
|   +-- bounded top-N extraction as internal subtype/pattern
|
+-- Tutor [public family]
|
+-- Graveyard Access [existing cross-linked family]
|
+-- alternative-zone / top-library access [access modes; public naming TBD]
|
+-- Card Advantage [derived relative resource property/accounting]
+-- Card Replacement / Card Neutrality [possibly derived parity property]
+
+Underlying mechanics:
+  source zone
+  candidate domain/sample
+  reveal/look/exile/draw/search/traverse
+  selection authority
+  cards seen / chosen / gained
+  destination
+  unchosen disposition
+  access duration
+  play vs cast permission
+  cost/payment modification
+  source expended/retained
+  per-player resource deltas
+```

This is intentionally **not** a ratified replacement tree. It is a research-derived simplification candidate.

## 5. Terms that should probably remain strategic-layer only

The research surfaced several useful established terms that should not become canonical mechanical classes:

- **Card Quality** — depends on a card's ability to influence a particular game.
- **Virtual Card Advantage** — depends on contextual relevance/blanking/effectiveness.
- **Smoother / Refiller / Engine** as deckbuilding buckets — useful strategic grouping, but not a replacement for Foundry's hard mechanical predicates.
- **Good/bad draw**, `gas`, and similar community evaluation language.

These can be consumed later by Complete My Deck / strategic reasoning, using canonical Foundry facts as inputs.

## 6. Highest-priority adversarial questions before S16B freeze

1. **Cantrip:** retain established meaning or rename Foundry's narrow class?
2. **Card Prospecting:** should it remain a public trunk, become a Filtering child/pattern, or disappear as a public noun?
3. **Card Replacement:** public trunk or derived parity/accounting result?
4. **Alternate-zone access:** what public name, if any, should unify impulse draw and other temporary access?
5. **Top-library access:** public concept or machine-facing access mode only?
6. Confirm Card Advantage against burst draw, wheels, temporary exile access, recursion, Cascade/Discover, retained permanents, and multiplayer vectors.

## 7. Source classes reviewed

Primary emphasis was placed on Wizards of the Coast rules/design/Level One material, including:

- Comprehensive Rules / Rules resources;
- Mechanical Color Pie 2021;
- `Drawing Attention`;
- `The Basics of Card Advantage`;
- Level One glossary (`Card Advantage`, `Card Quality`, `Card Quantity`, `Virtual Card Advantage`);
- `Nuts & Bolts: Structural Support` (deck smoothing, impulsing, tutoring, looting/rummaging);
- release/mechanics articles for surveil, cycling, connive, cascade, and discover;
- official R&D terminology articles for rummaging and related slang.

Secondary community evidence included Commander discussions about card selection vs card advantage vs tutors, impulse draw, wheels, and contemporary deckbuilding buckets. Community evidence was used to identify vocabulary and player expectations, not as canonical rules authority.

## 8. Control boundary

This research does **not** authorize:

- changing current Captain-approved semantic decisions without adjudication;
- S16B freeze;
- broad corpus reclassification;
- implementation acceptance;
- merge;
- accepted-head or `main` movement;
- AQ4 resumption;
- Bridge v0 activation;
- Step6.

The governing principle remains:

> **PRESERVE TRUTH, NOT PLUMBING.**
