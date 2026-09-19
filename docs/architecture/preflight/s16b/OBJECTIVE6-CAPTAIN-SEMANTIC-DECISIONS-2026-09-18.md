# Objective 6 — Captain Semantic Decisions

**Date:** 2026-09-18  
**Status:** Captain decision record for ongoing Objective 6 vocabulary work. This document records decisions and unresolved boundaries; it is not implementation acceptance, S16B freeze, or permission to merge.  
**Base accepted implementation head:** `fdb66e659d81f4efa373ab8e86329485c0205966`  
**Related product direction:** `docs/architecture/FOUNDRY-PRODUCT-INTERACTION-MODEL-2026-09-18.md`

## Purpose

Preserve the semantic decisions reached during Captain review so they are not lost between sessions and so later Objective 6/S16B implementation can distinguish:

- settled Captain vocabulary decisions;
- provisional but accepted working definitions;
- unresolved questions that still require adjudication;
- UI/product implications that must not be mistaken for semantic truth.

The governing semantic/product principle remains:

> **Foundry reports semantic composition and change; it does not prescribe desired composition.**

Foundry core is not currently a recommendation engine. Recommendation behavior belongs to the later Complete My Deck layer.

---

# 1. Structural vocabulary model

Captain direction is to avoid uncontrolled rider proliferation such as `potential card advantage`, `delayed card advantage`, `conditional card advantage`, and similar compound labels unless a genuinely separate named concept is necessary.

Candidate semantic concepts should be treated as one of:

- **TRUNK** — broad functional family that can expose dimensions/facets and may have real named children.
- **NAMED_SUBCLASS** — a distinct gameplay family under a broader concept.
- **RIGID_LEAF** — a term with a deterministic membership test that does not need its own naming hierarchy.
- **ALIAS_ONLY** — useful community language resolving to another Foundry concept.
- **RETIRE / DO NOT CANONIZE** — unstable, redundant, or misleading terminology that should not become a Foundry category.

Most granularity should be represented by semantic coordinates/facets rather than new names.

A recurring test is:

> **Does this distinction deserve a noun, or does it deserve a property?**

Similarity does not require category membership. A card may be semantically close to a class while failing that class's hard predicate.

---

# 2. Card Access umbrella

## 2.1 Status

**Captain direction: USE AS UI / NAVIGATION UMBRELLA.**

`Card Access` is currently an umbrella for related card-resource functions. It is not itself intended to force mutually exclusive card membership.

Current working children/functions:

- Card Replacement
- Card Advantage
- Card Sifting
- Card Prospecting
- Tutor (reserved; hard definition not yet completed)

These functions may overlap on one card.

Because of overlap, Foundry should not force them into a mutually exclusive pie chart. Deck UI may instead show overlapping counts/percentages, e.g. number of cards contributing to Card Advantage, Card Sifting, Card Prospecting, etc.

A part-to-whole chart is only appropriate where the underlying categories truly partition the total.

---

# 3. Cantrip

## 3.1 Status

**Captain-approved working definition; treat as a RIGID_LEAF / named subclass.**

Cantrip is not intended to become a trunk with rider names such as `true cantrip`, `pseudo-cantrip`, or `delayed cantrip`. Those distinctions should remain semantic coordinates if needed.

## 3.2 Hard working rule

A card qualifies as a Foundry **Cantrip** when all of the following are true:

1. **Mana value is 2 or less.**
2. Using the card from hand expends a card resource from hand.
3. Through its own normal operation, the card can return its controller to **at least hand-card parity** relative to that expenditure.
4. The card intrinsically provides **at least one additional mechanically identifiable function** beyond merely replacing itself.
5. The replacement need not be a literal `draw` instruction; another intrinsic method of placing a usable card into hand may satisfy replacement.
6. The replacement may be **immediate, delayed, or conditional**.
7. **Any card type may qualify.**
8. Selection/reordering/other card-quality improvement may itself count as the additional function.
9. A permanent left behind by the card counts as an additional function.
10. Built-in reuse such as flashback may count as an additional function.

## 3.3 Positive anchors

Gold-standard / accepted positives discussed by the Captain:

- Ponder
- Preordain
- Brainstorm
- Opt
- Thought Scour
- Portent
- Omen of the Sea
- Elvish Visionary
- Think Twice

`Think Twice` qualifies because the first use replaces the card and flashback is an intrinsic additional function.

## 3.4 Boundary

A mana-value-2-or-less card whose only function is simply replacing itself, with no additional mechanically identifiable function, does not qualify under the current Cantrip rule.

Cantrip is expected to sit under / overlap with Card Replacement.

---

# 4. Card Sifting

## 4.1 Status

**CAPTAIN RATIFIED — TRUNK.**

Former working labels such as `card velocity` / `library sifting` are superseded for canonical Foundry vocabulary by **Card Sifting**.

## 4.2 Functional meaning

Card Sifting covers effects that change which cards a player moves through, exposes, filters, reorders, discards, mills, cycles through, or otherwise changes the accessibility/order of, without requiring positive card advantage.

The concept is intentionally broader than literal library-top manipulation.

## 4.3 Included families / anchors

Accepted inclusions include:

- Ponder
- Preordain
- Brainstorm
- Faithless Looting
- surveil
- cycling
- pure self-mill
- looting
- rummaging
- Index and similar effects

## 4.4 Boundary against Card Prospecting

Effects such as **Dig Through Time** and the relevant mode of **Plunge into Darkness** are not classified as Card Sifting merely because they inspect multiple cards. Their defining operation is selecting one or more cards from a bounded exposed sample for privileged access; that is **Card Prospecting**.

A card may still legitimately satisfy more than one function if it independently performs both operations.

---

# 5. Card Prospecting

## 5.1 Status

**CAPTAIN RATIFIED — TRUNK.**

`Selection` was rejected as the canonical name because Tutor also involves selection and the term does not capture the bounded-sample distinction.

## 5.2 Hard rule

A card/effect qualifies as **Card Prospecting** when:

1. it examines, reveals, looks at, exiles, or otherwise exposes a **bounded sample of 3 or more cards** from a library;
2. the player is allowed to choose one or more cards from that exposed sample; and
3. the chosen card(s) receive **privileged access or a privileged destination/use**.

The privileged result does **not** have to be literal card draw.

Qualifying destinations/uses may include:

- put into hand;
- draw chosen card(s);
- exile with permission to cast/play;
- put onto the battlefield;
- another explicitly usable privileged destination to be adjudicated consistently.

## 5.3 Positive anchors

- Dig Through Time
- Plunge into Darkness (relevant mode)
- Elven Farsight
- Impulse
- Collected Company

## 5.4 Exclusions / boundaries

- Pure draw with no choice among a bounded exposed sample is not Prospecting.
- Looking at only 1–2 cards does not satisfy the current Prospecting threshold.
- Mere disposition choice over exposed cards (e.g. deciding top/bottom/graveyard placement) is Sifting unless the effect also chooses card(s) for privileged access.
- Searching the broader/entire library for a qualifying card is reserved for **Tutor**, not Prospecting.

## 5.5 Overlap

Overlap is permitted. Example: **Dig Through Time** may be both Card Prospecting and Card Advantage.

---

# 6. Card Replacement

## 6.1 Status

**CAPTAIN APPROVED — TRUNK; hard implementation predicate still to be formalized.**

## 6.2 Core meaning

Card Replacement is the function where a card/effect compensates for the card resource expended to use it by granting access to another usable card resource, producing baseline card-resource parity rather than inherently positive advantage.

## 6.3 Zone-agnostic ruling

Card Replacement is **zone-agnostic**. The replacement card/resource does not have to originate from the library.

Source zone should be represented as a coordinate/facet rather than a new rider term.

Examples:

- Shelter — Card Replacement + Cantrip + Protection.
- Regrowth — Card Replacement + Recursion.
- Eternal Witness — Card Replacement overlaps with Recursion and, because the Witness remains as a card-origin permanent while another card is recovered, may also satisfy Card Advantage.

## 6.4 Relationship to Cantrip

Current working relationship:

> **Every Cantrip is expected to satisfy Card Replacement, but not every Card Replacement card is a Cantrip.**

For example, a 4-mana card that replaces itself may satisfy Card Replacement but fail the Cantrip mana-value ceiling.

## 6.5 Card Parity

`Card Parity` should currently be treated as an **accounting result/state**, not automatically promoted to a separate semantic trunk.

---

# 7. Card Advantage

## 7.1 Status

**PARTIALLY RESOLVED — TRUNK INTENT ACCEPTED; multiplayer aggregation and exact hard predicate remain OPEN.**

The discussion established that Card Advantage cannot be defined purely as `cards drawn` or `hand size increased`.

It is fundamentally about **relative access to usable card-origin resources compared with opponents**.

## 7.2 Accepted principles

1. **Card Advantage is relative**, not merely a self-count.
2. It concerns the ability to obtain or preserve more usable card-origin resources / spell access over the course of the game than an opponent.
3. Positive advantage may come from gaining resources yourself **or** causing an opponent to lose more card resources than you expend.
4. Symmetrical gain does not automatically constitute Card Advantage merely because the controller gained cards.
5. A source may remain as a usable card-origin permanent while also generating another card resource; that retained source matters.
6. Tokens / generated game objects are not automatically Card Advantage merely because one physical card created multiple objects.
7. Temporary / alternative-zone playable access is expected to be capable of contributing to Card Advantage; exact accounting remains to be formalized.

## 7.3 Accepted examples / direction

### Elvish Visionary

Captain direction: **counts as Card Advantage.**

Reasoning: the original card becomes a usable permanent while the draw supplies another usable card resource.

### Eternal Witness

Captain direction: **counts as Card Advantage** in addition to Card Replacement / Recursion because the Witness remains as a usable card-origin permanent while another actual card is recovered.

### Regrowth

Captain direction: **Card Replacement / Recursion, not inherently Card Advantage.** One card is expended to recover one card.

### Solemn Simulacrum

Captain direction: **counts as Card Advantage.** It remains as a body, acquires another actual card-origin resource from the deck (basic land to battlefield), and can later draw another card when it dies. It may also overlap with Ramp.

### Planeswalkers / permanents that draw cards

A planeswalker or other retained permanent that generates additional card access may produce Card Advantage because the source remains while additional card resources are gained.

### Temple Bell

Captain correction: a fully symmetrical draw effect should **not** be labeled Card Advantage merely because the controller also draws. If all players receive equal additional card access, the controller has not gained relative advantage from that operation.

This is better understood as parity/symmetrical resource change, with exact accounting kept as underlying data.

### Discard effects

A one-card effect that makes an opponent discard two cards can produce Card Advantage in a 1v1 context because the controller expends one resource while the opponent loses two.

This established that Card Advantage can arise from **denial/removal of opponent card resources**, not only from drawing/accessing more of one's own cards.

---

# 8. Format / player-count context for Card Advantage

## 8.1 Status

**CAPTAIN RATIFIED PRINCIPLE; aggregate multiplayer display remains unresolved.**

Foundry should expose a **Format** control. The format/player-count context can change the derived Card Advantage classification.

Mechanical/card facts remain format-neutral. Card Advantage is derived from those facts under the selected game context.

## 8.2 Mind Rot direction

- **1v1:** Mind Rot is Card Advantage: one card expended to remove two opposing cards.
- **Multiplayer:** the same exchange is not automatically positive table-wide Card Advantage because only one opponent loses cards while other opponents are unaffected. It may be parity or card-negative under the eventual multiplayer aggregation method.

Exact multiplayer reduction to a single displayed number is **OPEN**.

## 8.3 Ms. Bumbleflower direction

Captain direction:

- **1v1:** Ms. Bumbleflower's relevant draw distribution can resolve to **Card Parity** where both players receive equal card access.
- **Multiplayer:** Ms. Bumbleflower can create Card Advantage depending on how opponent draw triggers are distributed. Giving different opponents one card each while the controller gains two can produce positive relative card position against those players and a larger advantage against an untouched opponent.

This proves that multiplayer Card Advantage can depend on **distribution among individual opponents**, not merely total cards granted to the table.

## 8.4 Required underlying data

Foundry should preserve player-relative resource facts such as:

- controller card/resource delta;
- per-opponent card/resource delta;
- affected-player set;
- whether the controller chooses the affected opponent;
- whether an effect applies to target opponent / each opponent / each player;
- source retained or expended;
- repeatability;
- conditionality / dependency;
- access zone and duration.

Derived labels should be computed from this substrate under the selected format/player count.

## 8.5 Open question

How should multiplayer Card Advantage be reduced for a headline UI value?

Possibilities still to adjudicate include:

- per-opponent vector only;
- relative-to-average-opponent;
- another transparent aggregate;
- no single aggregate at all.

Do not freeze this until explicitly decided.

---

# 9. Tutor

## 9.1 Status

**NAME RESERVED; hard definition not yet ratified.**

Captain direction is that **Tutor** should be reserved for effects that search the broader/entire library for a specific or qualifying card, rather than choosing from a bounded sample.

This distinguishes Tutor from Card Prospecting.

The exact hard predicate, restrictions, and destination handling remain to be decided.

---

# 10. Role Compression

## 10.1 Status

**NEW CONCEPT QUEUED — NOT YET HARD-DEFINED.**

Motivated by cards such as **Untimely Malfunction**.

The intended idea is that a single card can contribute to multiple materially distinct deck functions, reducing the number of separate card slots required to cover those functions.

Open questions include:

- whether role compression is simply count-of-distinct-functions or needs a stricter predicate;
- whether mutually exclusive modal choices count differently from simultaneous multi-role effects;
- whether one role must be independently useful outside the others;
- whether compression should be displayed as a count, boolean, weighted value, or combination;
- how to avoid judging whether compression is strategically `good` while still reporting the hard fact of multifunctionality.

Do not implement a semantic predicate until these are decided.

---

# 11. Deck / Thesaurus UI implications

These are product implications of the semantics above, not independent semantic authority.

## 11.1 Counts, not prescriptions

Foundry should report hard counts such as:

- Card Advantage sources;
- Card Replacement sources;
- Card Sifting sources;
- Card Prospecting sources;
- removal functions;
- token generation;
- other semantic roles as they are ratified.

It should **not** currently label those counts as too high, too low, good, bad, sufficient, or deficient.

## 11.2 Counterfactual replacement deltas

When a user considers replacing one deck card with another, Foundry should show factual semantic deltas, e.g.:

- Removal: `11 → 10`
- Token generation: `6 → 7`
- Card Advantage sources: `13 → 12`

No recommendation or judgment is implied.

## 11.3 Budget

Budget is a mode/constraint layered on the same semantic engine, not a separate semantic recommendation engine.

## 11.4 Format

Format/player-count is also semantic context for derived properties such as Card Advantage, not merely a legality filter.

---

# 12. Known unresolved work

The following items are intentionally unresolved:

1. Finish the hard predicate for Card Advantage.
2. Decide multiplayer Card Advantage aggregation/display.
3. Finish Tutor.
4. Decide whether all meaningful card-access effects are adequately covered by Card Replacement / Card Advantage / Card Sifting / Card Prospecting / Tutor or whether additional trunks are necessary.
5. Define Role Compression.
6. Continue Objective 6 term-by-term adjudication for remaining community terms such as Ramp, Fast Mana, Ritual, Removal, Interaction, Protection, Board Wipe, Wrath, Stax, Hatebear, Graveyard Hate, Sac Outlet, Reanimator, and others surfaced by research.
7. Validate Captain definitions against the full card corpus and collect hard near-misses before S16B freeze.

---

# 13. Control boundary

This document preserves Captain semantic decisions. It does **not** by itself authorize:

- S16A implementation acceptance;
- S16B semantic freeze;
- merge of any draft PR;
- movement of accepted head;
- AQ4 resumption;
- Bridge v0 activation;
- Step6;
- main-branch movement.

The accepted implementation head remains unchanged unless separately and explicitly advanced through the project control process.
