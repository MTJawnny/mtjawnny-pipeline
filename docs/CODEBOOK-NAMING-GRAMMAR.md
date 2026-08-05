# CODEBOOK NAMING GRAMMAR v1.0 (RATIFIED 2026-07-30)

Status: RATIFIED by Captain, 2026-07-30 (decisions D-1 through D-5 resolved per
recommendation; see section 13). Law: every axis slug —
authored, grammar-instantiated, or renamed at the audit walk — must validate
against this document. Versioned alongside the codebook. Every vocabulary claim
below is anchored to the local `mtg-comprehensive-rules.md` (June 19, 2026);
CR citations were verified against that file on 2026-07-30, not recalled.

Design goals, in priority order:
1. **No two slugs may describe the same mechanic** (the
   scales-token-count-with-x / token-count-scales-with-x duplication class).
2. **No slug may be readable as two different mechanics** (the
   grants-trample-to-countered-creatures class).
3. **Every closed mechanical family is enumerated in advance** so cards cannot
   fall between siblings (the sorcery-speed vs during-combat class).
4. **Slugs are machine-decomposable** so parents, facets, and DET patterns
   derive from names without human interpretation.

---

## 1. The slot grammar

Every axis slug is a hyphen-joined sequence of slots in this fixed order:

```
[DELIVERY]-[EFFECT]-[OBJECT]-[SCOPE]-[QUALIFIER...]
```

- **DELIVERY** — how the ability happens (ability class / trigger family).
  OMITTED for spell abilities (CR 113.3a): an instant/sorcery's resolution
  effect is the unmarked default. `burst-draw`, `targeted-destruction`,
  `counters-target-spell` are spell-delivery slugs. Everything non-spell is
  MARKED.
- **EFFECT** — the standardized verb phrase (section 4).
- **OBJECT** — what the effect acts on (section 5). Omitted when the effect
  verb already binds it (`loot`, `scry`, `mill-self`).
- **SCOPE** — ownership/breadth (section 6). Omitted when the axis's scope=
  field carries it and no sibling differs only by scope; REQUIRED the moment a
  scope-sibling exists (the Q1/Q2 lesson: scope moved into the name for
  tap-or-untap because siblings differ there).
- **QUALIFIER** — closed modifiers: `-conditional`, **`delayed`** (the effect
  happens at a later stated timing point rather than on resolution — CR 603.7;
  moved here from DELIVERY by §2d, because the delivery of a card that creates a
  delayed trigger is whatever *created* it), `-mass` (see 6),
  `-scales-with-<stat>` (see 7), token/counter types (see 8), cost qualifiers
  ("Free must be Free" — cost words in names are binding, ratified b2).

Compounds remain the only authored thing (addendum-3 §3): one slug asserts one
ability doing one thing. Multi-ability cards get multiple tags, never fused
slugs (M8, generalized batch-6 D3).

**Membership is not exclusive (Captain-ratified 2026-08-02).** A card holds
membership on **every axis it genuinely satisfies**. Modal modes each earn
their axis — Blizzard Specter is a member of both its discard axis and its
bounce axis. A single ability decomposes onto its compound slug *and* the
facet axes it is built from — Riptide Entrancer is a member of
`combat-damage-to-player-permanent-control-theft`, `permanent-control-theft`
and `optional-self-sacrifice-in-trigger`. This extends the rule above: §1
already covered multiple *abilities*, this covers multiple *axes per ability*.

This ratifies existing practice rather than changing it — measured
2026-08-02, **1,236 of 5,844 carded cards (21.1%) already sat on more than
one active axis**, up to 5. Consequence to respect: member counts are NOT a
partition of the corpus, and any consumer assuming one-card-one-home is
wrong. Record: `docs/MEMBERSHIP-RATIFICATION-PACKET-2026-08-02.md`.

Formatting law: lowercase ASCII, hyphens only, no articles ("a", "the"), no
plurals except where the mechanic is inherently plural (`-two-target-creatures`,
mass effects), `plus1`/`minus1` for counter polarity (ratified), `x` for the
variable.

---

## 2. DELIVERY slot — closed vocabulary (CR-anchored)

| Slot value | Means | CR anchor |
|---|---|---|
| *(none)* | spell ability, applies on resolution | 113.3a |
| `activated` | "[Cost]: [Effect]" | 113.3b |
| `static` | written as a statement, continuously true | 113.3d |
| `etb` | triggered, "when ~ enters" | 113.3c |
| `leaves-battlefield-trigger` | triggered, any LTB (superset of death-trigger; a card saying "leaves the battlefield" NEVER takes `death-trigger`) — the `-trigger` suffix is kept to match the live axis family | 700.4 boundary |
| `attack-trigger` | "whenever ~ attacks" | 113.3c |
| `cast-trigger` | "when(ever) [someone] casts" — requires cast verbiage; never an ETB; the trigger EVENT must be the cast itself, not a condition about casting (b6 Village Ironsmith ruling) | 701.5a |
| `combat-damage-to-player` | "deals combat damage to a player" | — |
| `combat-damage-to-creature` | "deals combat damage to a creature" | — |
| `any-damage-to-player` | "deals damage to a player/opponent" with NO combat restriction — fires off pingers, burn, fight effects (Captain-ratified 2026-08-02) | 120.3 |
| `any-damage-to-creature` | "deals damage to a creature" with NO combat restriction (Captain-ratified 2026-08-02) | 120.3 |
| `upkeep-trigger` | "at the beginning of [whose] upkeep" | 113.3c, 503.1 |
| `end-step-trigger` | "at the beginning of [whose] end step" — the mirror of `upkeep-trigger`; REQUIRES a §6 scope (`you-control` 405 / `each` 81 / `active-player` 50). Captain-ratified 2026-08-03 (Q7). Older cards printed this as "at end of turn" and carry Oracle errata (CR 513.1a), so DET patterns must canonicalize both eras. The bare **axis** `rule:end-step-trigger` remains KILLED per `TRIAGE-BATCH-1.md` §1c — delivery-only slugs are parents, not axes | 113.3c, 513.1 |
| `landfall` | the landfall ability word | 207.2c |
| `loyalty` | planeswalker loyalty ability — is activated but always marked `loyalty`, never `activated` (b7 Ob Nixilis crack) | 606.1 |
| `replacement` | "instead" / "skip" / "enters with/as" shapes | 614.1a–c |
| ~~`delayed`~~ | **RETIRED from DELIVERY 2026-08-03 — moved to QUALIFIER (§1). See §2d.** | 603.7 |
| ~~`kicker`~~ | **RETIRED from DELIVERY 2026-08-06 — CR 702.33a makes it a STATIC ability, so §2b already derives its delivery. See §2g.** | 702.33a |
| `death-trigger` | triggered, graveyard from battlefield | 700.4 |
| `becomes-targeted-trigger` | triggered, "becomes the target of a spell or ability" (Ward's family; walk-ratification Q2, 2026-07-31) | 702.21a |
| `becomes-tapped-trigger` | triggered on the STATE CHANGE untapped→tapped. Captain-ratified 2026-08-03. *"doesn't trigger if the permanent enters the battlefield in that state"* — so it is neither `enters-tapped` (a replacement, CR 614) nor a tapped-state check | 603.2e |
| `becomes-untapped-trigger` | triggered on the state change tapped→untapped (the `Inspired` family — an ability WORD, CR 207.2c, with no rules meaning, so the axis takes the printed trigger) | 603.2e |
| `tapped-for-mana-trigger` | triggered *"whenever such a **mana ability resolves and produces mana**"* — strictly NARROWER than becoming tapped: tapping for a non-mana cost fires `becomes-tapped-trigger` and NOT this. Not a synonym | 106.12a |
| `cycled-trigger` | triggered when the card is cycled. CR 702.29c: *"'When you cycle this card' means 'When you **discard this card to pay an activation cost of a cycling ability**'"* — so it fires on paying the COST, and still fires if the draw is replaced or prevented | 702.29c |
| `cycle-or-discard-trigger` | the CR's own named shape, *"whenever a player 'cycles or discards' a card"*, which **fires only ONCE when a card is cycled** — a real distinction from a naive "cycle OR discard" reading | 702.29d |
| `discard-trigger` | "whenever «someone» discards «a card»". Captain-ratified 2026-08-04. Takes the **§2a subject prefix** — `any-` 76 · source 3 · `other-` 0. **CR 701.9a**: *"To discard a card, move it **from its owner's hand** to that player's graveyard."* The origin is the HAND, so a discarded creature card **never dies** — CR 700.4 keys `dies` on the *battlefield* origin, and `death-trigger` cannot fire on a discard. Same destination, different origin, disjoint families. **Cycling IS discarding** (CR 702.29c) and so is **typecycling** (CR 702.29f: *"Any cards that trigger when a player cycles a card **will trigger when a card is discarded to pay an activation cost of a typecycling ability**"*), so this token and `cycled-trigger` are **not disjoint** — §1's multi-axis rule, and why CR 702.29d gives "cycles or discards" its own once-only shape. **Madness does not exempt a card**: CR 702.35a says *"that player **discards it**, but exiles it instead of putting it into their graveyard"* — the discard still happens, only the destination is replaced, so madness cards DO fire discard triggers. **Mayhem is not this** — CR 702.187b is a static ability keyed on a *past* discard (*"As long as you discarded this card this turn"*), not a trigger. Discard as a COST is `activated` per §9 (CR 702.29a puts it left of the colon). CR 701.9c is noted for the hidden-zone case but no member turns on it | 701.9a, 701.9b |
| `sacrifice-trigger` | "whenever you sacrifice «a permanent»". Captain-ratified 2026-08-03. Takes the **§2a subject prefix** — `sacrifice-trigger` (this/~) 7 · `other-` 25 · `any-` 78. **CR 701.21a**: sacrifice moves the permanent *"from the battlefield directly to its owner's graveyard"*, which is CR 700.4's definition of **dies** — so a sacrificed creature DIES and `death-trigger` may also apply (§1 multi-axis); neither subsumes the other. *"Sacrificing a permanent **doesn't destroy it**"* — sacrifice ≠ destroy, §6b. *"A player **can't sacrifice … a permanent they don't control**"* — so the scope records WHO sacrifices and the permanent is always theirs; **no second scope slot for "whose permanent"**. Sacrifice as a COST is `activated` per §9, not this | 701.21a, 700.4 |
| `is-attacked-trigger` | the DEFENDING side of the declaration — "whenever a creature **attacks you**". Captain-ratified 2026-08-03. CR 506.3 is a **closed enumeration**: *"Only a creature can attack or block. **Only a player, a planeswalker, or a battle can be attacked**."* **SCOPE is mandatory from day one** (§1: required the moment a sibling exists) and uses existing §5 objects: `player` 20 · `player-or-planeswalker` 15 · `planeswalker` 1 · `battle` **0 today**, reserved by the CR enumeration but **not instantiated** (zero members is a hypothesis). The compound "you or a planeswalker you control" is ONE trigger with two legal objects, not two abilities; its `or` takes the §14 F4 soft warning | 506.2, 506.3, 508.1b |
| `player-attack-trigger` | "whenever **you attack**" — the trigger subject is the **player's declaration**, not a creature. Captain-ratified 2026-08-03. CR 508.1a: *"**the active player chooses** which creatures … will attack."* Fires **once per combat** regardless of attacker count, and **the source need not attack** — Cosmic Cube (Artifact), Sparring Regimen (Enchantment) and Gideon, the Oathsworn (Planeswalker) all print it and can never attack, so `attack-trigger` would assert something false. The "with «qualifier»" half (53 of 159) is a §1 QUALIFIER, not a second token. Not `you-attack-trigger`: §6d makes a leading `you-` a SCOPE marker | 508.1, 508.1a, 508.1m |
| `begin-combat-trigger` | "at the beginning of combat on [whose] turn". Captain-ratified 2026-08-03. **NOT `combat-trigger`** — CR 506.1 gives combat FIVE steps and §2's combat vocabulary is already step-specific (`attack-trigger` 508, `blocks-or-becomes-blocked-trigger` 509, `combat-damage-to-*` 510), so a token spanning all five is design goal #2. Scope uses existing §6 tokens (`you-control` 300 / `each` 28 / `opponent` 5); no bare "the combat step" form exists, because combat only happens on the active player's turn | 506.1, 507 |
| `end-combat-trigger` | *"Abilities that trigger **'at end of combat'** trigger as the end of combat step begins."* Captain-ratified 2026-08-03. **17 cards, not 111** — see the `delayed` note below: 94 further cards print "at end of combat" as a *duration inside an effect*, which is a delayed trigger belonging to its creator | 506.1, 511.2 |
| `chapter-trigger` | a Saga chapter ability. CR 714.2: *"A chapter symbol is a **keyword ability** that represents a **triggered ability** referred to as a chapter ability."* 714.2b gives the templated text: *"When one or more lore counters are put onto this Saga, if the number … was less than N and became at least N, [effect]."* Captain-ratified 2026-08-03. **N is a PARAMETER** — the final chapter's sacrifice is a STATE-BASED action (714.4), not part of the ability. `-conditional` is deliberately NOT marked: 714.2b makes the intervening-if definitional, so it would tag 100% of members and distinguish nothing. The Saga *progression* is a TURN-BASED ACTION (714.3c) and is not an ability — `rule:saga-chapter-progression` stays KILLED per `TRIAGE-BATCH-1.md` §1c. **Class level bars are NOT this**: CR 716.2 makes them activated + static, and they already take `activated` | 714.2, 714.2b |
| `blocks-or-becomes-blocked-trigger` | triggered, a blocking/being-blocked event (Bushido/Flanking/Rampage/Afflict shape; walk-ratification Q2, 2026-07-31) | 509 |
| `precombat-main-phase-trigger` | "at the beginning of [whose] **first** main phase". Captain-ratified 2026-08-04. **CR 505.1** makes "first" and "precombat" the same phase, and the corpus prints only one of the two — measured **63 of 63 lines print "first main phase"; ZERO print "precombat main phase."** The token is named for the CR's **category** word, matching `begin-combat-trigger` and `end-step-trigger`, which are also category-named. REQUIRES a §6 scope (`you-control` 97 · `each` 4 across the three main-phase tokens); Blinkmoth Urn prints *"each player's first main phase"* | 505.1, 505.1a |
| `second-main-phase-trigger` | "at the beginning of [whose] **second** main phase" — a **COUNT**, not a category. Captain-ratified 2026-08-04. **CR 505.1b**: *"Phrases such as 'first main phase,' 'second main phase,' and so on **count the number of main phases that have occurred only in the current turn** unless that text specifies otherwise."* Always printed **singular** | 505.1b |
| `postcombat-main-phase-trigger` | "at the beginning of each of [whose] **postcombat** main phase**s**" — a **CATEGORY**. Captain-ratified 2026-08-04. **`second-` and `postcombat-` are NOT synonyms, and CR 505.1a says so outright**: *"Only the first main phase of the turn is a precombat main phase. **All other main phases are postcombat main phases.** … an effect has caused an **additional combat phase and an additional main phase** to be created."* On an extra-combat turn the **third** main phase is postcombat but is **not** the second, so the two fire on different turns — §2's ratified D3f test asks *does the distinction change WHEN or WHETHER*, and this one does. **Split.** The corpus prints the distinction deliberately: postcombat cards print the **plural** (Sphinx of the Second Sun, Neheb the Eternal, Megatron — the fires-on-every-one reading) while "second main phase" is always singular. **The axis `rule:postcombat-main-phase-trigger` already existed** with a batch-6 KEEP ruling and is **under-populated at 2 of 10 cards**, so ratification here is a *membership* addition, not a new axis | 505.1a |
| `is-dealt-damage-trigger` | the **RECIPIENT** side of the damage family — *"**X** is dealt damage"* — whose SOURCE side (`combat-damage-to-*`, `any-damage-to-*`, all four reading *"**~** deals damage to X"*) was already ratified, leaving 110 lines with no token. Captain-ratified 2026-08-04. Structurally identical to `is-attacked-trigger`, which named the defending side of a declaration whose attacking side was ratified. Takes the **§2a subject prefix** — source 74 · `any-` 38 · `other-` 0; the source form dominates here (unlike discard) because the archetypal card is *"Whenever **this creature** is dealt damage"* (Trapjaw Tyrant, Hornet Nest, Indoraptor). **CR 120.1 is a CLOSED recipient enumeration** — *"Objects can deal damage to **battles, creatures, planeswalkers, and players**"* — sealed by **120.1a**: *"Damage **can't** be dealt to an object that's not a battle, a creature, or a planeswalker."* Exactly as CR 506.3 sealed the `is-attacked-trigger` object slot. Measured creature 103 · player 6 · planeswalker 3 · **battle 0**, reserved by the enumeration and **not instantiated** (zero members is a hypothesis, per the is-attacked precedent). SCOPE mandatory from day one — Wrathful Red Dragon (*"a Dragon **you control**"*), Kazarov (*"an opponent controls"*), Grievous Wound (*"**enchanted player**"*, which has no §6 token — see `draw-step-trigger`) | 120.1, 120.1a |
| `is-dealt-combat-damage-trigger` | the recipient-side restriction. `DAMAGE-DELIVERY-RULING-2026-08-02` ruled **`combat-` is a RESTRICTION, not decoration**, and it governs this side of the family too. Captain-ratified 2026-08-04 | 120.2a |
| `is-dealt-excess-damage-trigger` | **`excess` is a CR term of art, not prose — the CR names this trigger family in its own sentence.** Captain-ratified 2026-08-04. **CR 120.10**: *"**Some triggered abilities check whether a permanent has been dealt excess damage.** … If those sources together dealt an amount of damage to a creature **greater than lethal damage**, excess damage equal to the difference was dealt to that creature."* Aegar the Freezing Flame, Toralf God of Fury, Fall of Cair Andros. Folding these into the base token would assert they fire on *any* damage, which is false — they fire only past lethal. §6a: the printed word is the claim | 120.10 |
| `is-dealt-noncombat-damage-trigger` | the printed **negation** of the restriction — Chandra's Spitfire, Wildfire Elemental print *"is dealt **noncombat** damage"*. Captain-ratified 2026-08-04. A strictly narrower claim than the base token and a different deck-building mechanism; three separate shapes, never one axis | 120.2a (negation) |
| `turned-face-up-trigger` | triggered when a face-down permanent is turned face up. Captain-ratified 2026-08-04. Takes the **§2a subject prefix** — source 94 · `any-` 18 · **`other-` 9** (Salt Road Ambushers, *"whenever **another** permanent you control is turned face up"*), so unlike discard and is-dealt-damage the `other-` node is **populated**. **Hard-disjoint from `etb` by CR, stated twice** — **708.8** and **702.37e** both read *"Any abilities relating to the permanent entering the battlefield **don't trigger** … because the permanent has already entered the battlefield."* Same kind of boundary as `death-trigger` vs `leaves-battlefield-trigger`, and it holds both directions. **Anchor on CR 708, NOT on morph**: 708.7 — *"The ability or rules that allow a permanent to be face down **may also allow the permanent's controller to turn it face up**"* — is what keeps morph (702.37), megamorph (702.37b), disguise (702.168), manifest (701.40), manifest dread (701.62) and cloak (701.58) in **one** token instead of five near-duplicates. ***"**As** [this permanent] is turned face up…" is NOT this token*** — **CR 708.11** applies it *"**while** that permanent is being turned face up, not afterward"*, which makes it a `replacement`; Hooded Hydra and Bubble Smuggler are therefore not members | 708.7, 708.8, 702.37e |
| `gain-life-trigger` | "whenever [a player] gains life". Captain-ratified 2026-08-04. **NOT `lifegain-trigger`** — §14 Q5 explicitly excluded the token `lifegain` as a *"synonym-collision candidate against the ratified `gain-life` EFFECT verb, design goal #1"*, and minting it in the DELIVERY slot is where it would do the most damage, because DELIVERY composes with every §2a prefix. **CR 119.9 EQUATES the two phrasings by rule**: *"Some triggered abilities are written, 'Whenever [a player] gains life…' Such abilities are treated as though they are written, '**Whenever a source causes** [a player] to gain life…'"* So **Firesong and Sunspeaker** (*"whenever a white instant or sorcery spell **causes you to gain life**"*) is this token with a source restriction, **not** a separate family — **the exact opposite verdict to `discard-trigger`**, where CR 701.9b distinguishes who chooses and the "causes you to discard" shape is held out. Same surface English, opposite rulings, and the CR states both outright; not guessable from the wording, only from the rule. **0 life is not a life-gain event** (119.9's last sentence is a membership rule: *"If a player gains **0 life, no life gain event has occurred**, and these abilities won't trigger"*). Replacement sibling for the boundary — **CR 119.10** *"If [a player] would gain life…"* is `replacement`, not this. SCOPE required from day one: `you-control` 83 · `opponent` 3 (Kavu Predator, Punishing Fire — the punish-their-lifegain deck is a genuinely different card) | 119.3, 119.9 |
| `to-graveyard-from-anywhere-trigger` | "put into a graveyard **from anywhere**". Captain-ratified 2026-08-04. **Strictly WIDER than `dies`, and must never take `death-trigger`** — **CR 700.4** defines the term narrowly (*"The term **dies** means 'is put into a graveyard **from the battlefield**.'"*), so "from anywhere" also covers hand, library, graveyard, exile and stack. Dread is the worked case. §2 already calls the dies / leaves-battlefield line *"a hard boundary both directions"*; this is the same discipline one level out | 700.4 |
| `to-graveyard-from-library-trigger` | "put into your graveyard **from your library**" — **narrower** than dies; the mill shape. Captain-ratified 2026-08-04. §6a governs: the printed ZONE is the claim, so collapsing this into the `-anywhere` token would make the codebook assert that Dread and a mill payoff are the same mechanism | 700.4 |
| `to-graveyard-from-hand-trigger` | "put into your graveyard **from your hand**". Captain-ratified 2026-08-04 | 700.4 |
| `to-graveyard-from-other-zone-trigger` | the printed zone is exile or the stack. Captain-ratified 2026-08-04 | 700.4 |
| `combat-damage-to-planeswalker` | the SOURCE side's third CR 120.1 recipient — *"~ deals **combat** damage to a planeswalker"*. Captain-ratified 2026-08-05 ("complete all incomplete vocabulary"). **The recipient side was ratified against CR 120.1's full enumeration on 2026-08-04 and the source side never was**, so this family named 2 of 4 recipients for a year of sessions. Worse than unrouted: the `any-` arm ended in a **bare fallback** that returned `any-damage-to-creature` for every recipient that was not a player, so Hooded Blightfang (*"deals damage to a **planeswalker**"*) asserted a creature-damage trigger — a **wrong ratified token**, the one direction no gap census reports. `mark`, not `msub`: only the player arm carries a measured §2a split | 120.1, 120.1a |
| `any-damage-to-planeswalker` | the same recipient with **no combat restriction**. `combat-` is a RESTRICTION, not decoration (`DAMAGE-DELIVERY-RULING-2026-08-02`), and that law governs this side of the family exactly as it governs `is-dealt-combat-damage-trigger`. Hooded Blightfang is the worked case. Captain-ratified 2026-08-05 | 120.1, 120.3 |
| `combat-damage-to-battle` | CR 120.1's fourth recipient. Captain-ratified 2026-08-05. **0 lines today** — reserved by the enumeration and **not instantiated**, exactly as `battle` is on `is-attacked-trigger` (CR 506.3) and on `is-dealt-damage-trigger` (CR 120.1). **Zero members is a hypothesis, not an absence**, and the emitter exists, so a printed card routes on day one instead of falling into a fallback | 120.1 |
| `any-damage-to-battle` | as above, without the combat restriction. Captain-ratified 2026-08-05. **0 lines today**, emitter present | 120.1, 120.3 |
| `noncombat-damage-to-player` | the printed **negation** of the combat restriction on the SOURCE side — *"a source you control deals **noncombat** damage to an opponent"*. Captain-ratified 2026-08-05. The recipient side already carried all three (`is-dealt-damage-trigger` / `-combat-` / `-noncombat-`), so completing the source side means mirroring **three**, not two. 9 lines: Chandra's Incinerator, Chandra's Pyreling, Niv-Mizzet Visionary, Thor Guardian of Midgard, Virtue of Courage. They were sitting on `any-combat-damage-to-player` — a token asserting a **combat** claim the card explicitly negates | 120.2a (negation) |
| `noncombat-damage-to-creature` | the same negation with a creature recipient. Captain-ratified 2026-08-05. 2 lines: Taii Wakeen, Crude Abattoir — both were on `combat-damage-to-creature`, again the exact inverse of what they print | 120.2a (negation) |
| `noncombat-damage-to-planeswalker` | the third CR 120.1 recipient under the same negation. Captain-ratified 2026-08-05. **0 lines** — reserved by the enumeration, emitter present. **Written as its own row on purpose:** §2's table is machine-parsed one token per row, and a row naming two tokens in its first cell ratifies NEITHER — caught here by the token count reading 51 instead of 53. Third instance of "a markdown table is an API" | 120.1, 120.2a |
| `noncombat-damage-to-battle` | the fourth, same reasoning. Captain-ratified 2026-08-05. **0 lines**, emitter present | 120.1, 120.2a |
| `draw-step-trigger` | "at the beginning of [whose] draw step". Captain-ratified 2026-08-04. Completes the turn-structure family, which is now closed end to end: untap 502 (no card prints a trigger) · upkeep 503 · **draw 504** · precombat main 505.1 · begin combat 507 · end combat 511 · postcombat main 505.1a · end step 513. **CR 504.1** — *"First, **the active player draws a card**. This turn-based action doesn't use the stack."* The draw itself is a **turn-based action, not an ability** — the same structural note CR 714.3c supplies for Saga progression — which is why this token names the **step**, not the draw. **A card triggering on the draw EVENT is a different family and is not this token.** SCOPE required from day one: `each` 14 · `you-control` 14 · `opponent` 1. **2 lines have no available §6 scope token** — Curse of Obsession and Righteous Authority both key on *"**enchanted player's**"*; `enchanted-player` is PROPOSED §6 vocabulary (CR 303.4, 702.5) and is deliberately **not minted here**, because new vocabulary is a ratification | 504.1 |

| `ability-activated-trigger` | triggers when **an ability is ACTIVATED** — *"whenever you activate an ability that isn't a mana ability"*. Captain-ratified 2026-08-07 (W3 sheet D6). **CR 602.1**: *"Activated abilities have a cost and an effect. They are written as '[Cost]: [Effect.]'"*, and **CR 602.2** makes activating one a distinct game action. **This is NOT §2's `activated`**, and the confusion is the whole reason it needs its own row: `activated` says *"this ability **is** an activated ability"* (a claim about the printed line), while this says *"this ability fires **when someone else activates** one"* (a claim about an event). Folding them would assert something false of all 34 lines and is design goal #2 exactly — one slug readable as two mechanics. Printed in both voices, both matched: active *"whenever you activate an ability"* (30) and passive *"whenever an ability of equipped creature **is activated**"* (4). **The restriction is a §1 QUALIFIER, not a second token** — `that isn't a mana ability` (CR 605.1a) 12 · `loyalty` (CR 606.1) 5 · a named CR 702 keyword's ability (`exhaust`, `ninjutsu`, `boast`, `outlast`, `power-up`) 10 · `of an artifact` 4. Scope is a §6 slot: `you-control` 19 · `opponent` 9 · player 3 | 602.1, 602.2 |
| `lose-life-trigger` | *"whenever you lose life"* — the **mirror of `gain-life-trigger`**, which §2 ratified on CR 119.9 while leaving this side unnamed. **CR 119.3** covers both directions: *"If an effect causes a player to **gain life or lose life**, that player's life total is adjusted accordingly."* Captain-ratified 2026-08-07 (W3 sheet D7). **The name was not an open question** — §4's EFFECT vocabulary already ratified `lose-life` as the standard verb, and §14 Q5's exclusion of `lifegain` (a *"synonym-collision candidate against the ratified `gain-life` EFFECT verb"*) governs this side identically, so `lifeloss` is banned by the same reasoning. `mark`, not `msub`: CR 119.3's subject is a PLAYER, as with `gain-life-trigger`, so scope is a §6 slot. **Damage is not life loss and this token must never claim it** — CR 120.3 makes damage dealt to a player *cause* life loss, but the two are different events and §2's four damage families already name the other one | 119.3 |
| `leaves-graveyard-trigger` | *"whenever one or more cards leave your graveyard"*. Captain-ratified 2026-08-07 (W3 sheet D5). §2 names **four** ways *into* a graveyard (`to-graveyard-from-anywhere` / `-library` / `-hand` / `-other-zone`, all CR 700.4) plus `leaves-battlefield-trigger`, and named **zero** ways out of one — the same CR 400.1 zone change in the other direction. Structurally identical to the `is-attacked-trigger` case, where the defending side of a ratified event had no name. Takes the **§2a subject prefix** where a subject is printed. **NOT `leaves-battlefield-trigger`**: §2 calls the dies/leaves-battlefield line *"a hard boundary both directions"*, and the graveyard is a different CR 400.1 zone, so collapsing them would assert that a recursion payoff and an LTB payoff are one mechanism | 400.1, 700.4 |
| `draw-trigger` | the draw **EVENT** — *"whenever you draw a card"*. **CR 121.1**: *"A player draws a card by putting the top card of their library into their hand."* Captain-ratified 2026-08-07 (W3 sheet D1). **NOT `draw-step-trigger`**, and that row already said so: *"the draw itself is a turn-based action, not an ability … **a card triggering on the draw EVENT is a different family and is not this token**."* This is that family, finally named. **NOT NEW VOCABULARY — it is already in ratified use** and was simply absent from this table: `rule:draw-trigger-self-plus1-counter-growth` is an active axis with 5 members, so the extractor could not emit a name the codebook was already carrying. Same shape as *"a ratified standard with no caller"*, inverted. Takes **no §2a prefix** — CR 121.1's subject is a PLAYER, exactly as CR 119.9's is for `gain-life-trigger`; scope is a §6 slot (`you-control` 45 · `opponent` 18 · `each`/player 5) | 121.1 |
| `draw-second-card-trigger` | *"whenever you draw your **second** card each turn"* — fires **once per turn on the Nth draw**, not on every draw. Captain-ratified 2026-08-07 (W3 sheet D1). **Also already in ratified use**: `rule:draw-second-card-trigger-plus1-counter` is an active axis (4 members) and §11 lists the *"draw-second/cast-second prefix scheme"* among its seeded grammar families. **THE SPLIT FROM `draw-trigger` IS AXIS IDENTITY, ON THE RATIFIED D3f TEST** — *does the distinction change WHEN or WHETHER the effect happens, or only how much?* A threshold trigger does not fire on the first draw at all, so it changes WHETHER. §8b applied that same test to counters and reached the same verdict (`<type>-counter-threshold-trigger` vs `-placed-trigger`). Fusing them would put a 60-line archetype — the deck built on getting a second draw each turn — inside a 68-line generic, which §6b rule 1 forbids by name: *"do not fold a shape into a near neighbour."* **The ORDINAL is a §11 grammar slot**, not part of the token: `draw-<ordinal>-card-trigger` instantiates `draw-third-card-trigger` and `draw-fifth-card-trigger` on their first quote-verified member, and the extractor composes the captured word rather than carrying an ordinal list (the recorded *"recount that omitted `twelfth`"* trap) | 121.1, D3f |
| `state-trigger` | a trigger whose condition is a **game STATE**, not an event. **CR 603.8 names the category and supplies the term verbatim**: *"Some triggered abilities trigger **when a game state** (such as a player controlling no permanents of a particular card type) **is true**, rather than triggering when an event occurs. These abilities trigger as soon as the game state matches the condition. … **These are called state triggers.**"* Captain-ratified 2026-08-07 (W3 sheet D4). The CR's own worked example — *"Whenever you have no cards in hand, draw a card"* — is in this population, and 603.8's *"doesn't trigger again until the ability has resolved"* is what makes it a distinct mechanism rather than a phrasing of an event trigger. **`mark`, not `msub`: there is no trigger SUBJECT for §2a to prefix** — the subject is the game state itself, which is why 603.8 contrasts it with "when an event occurs". The DISCRIMINATOR is that a state is a statement of BEING (`controls no` 20 · `there are no` 5 · `has/have no` · `there are N or more` · `have N or less`), so a quantity inside an EVENT clause is not one: Rendmaw's *"whenever you **play** a card with two or more card types"* and Psychic Battle's *"whenever a player **chooses** one or more targets"* are events and are deliberately excluded. Note CR 603.8's own parenthetical *"(state triggers aren't the same as state-based actions)"* — SBAs are CR 704 and are not abilities at all | 603.8 |

**Ratified 2026-08-04 — the 14 rows above.** Captain's word on the one decision
sheet carried in `SESSION-HANDOFF-2026-08-04.md` §8, whose three flagged
questions were answered first (see §2e). Each row's DET was already wired and
reporting its shape honestly before ratification, so no token is approximated
onto a neighbour. Records: `docs/MAIN-PHASE-RULING-2026-08-04.md` ·
`docs/IS-DEALT-DAMAGE-RULING-2026-08-04.md` ·
`docs/TURNED-FACE-UP-RULING-2026-08-04.md` ·
`docs/GAIN-LIFE-TRIGGER-RULING-2026-08-04.md` ·
`docs/TO-GRAVEYARD-RULING-2026-08-04.md` · `docs/DRAW-STEP-RULING-2026-08-04.md`.

Three shapes from those rulings are deliberately **NOT** routed and stay
reported — see **§2f**, which is a separate subsection **on purpose**: §2's
table is machine-parsed, and an unratified shape listed in a table above the
first `###` would be read as ratified vocabulary.

Rules:
- DELIVERY is determined by ability STRUCTURE, never by effect words (batch-4
  D1 / batch-7 feedback #1 codified). An Attraction's Visit/Prize are
  triggered, not activated (b7 Pick-a-Beeble... b6 finding).
- `dies` vs `leaves-battlefield` is a hard boundary both directions.
- RATIFIED (D-1): `death-trigger` stays the family word for dies-triggers;
  CR 700.4 anchors every definition in the family. No `dies-` slugs.
- `combat-damage-triggers-<effect>` normalizes to
  `combat-damage-to-player-<effect>` / `-to-creature-<effect>` at the walk —
  the b7 Guild Thief definition bug is exactly this slot being unmarked.
- **A card does not deliver an ability it CREATES (Captain-ratified
  2026-08-02).** When a card produces an ability — via an **emblem**, a
  **delayed trigger**, an ability **granted** to another permanent, or a
  **token's** printed text — the delivery belongs to the *creating* ability
  (`loyalty`, `etb`, `activated`, …), never to the created one. **`delayed` is
  NOT in that list** — a delayed trigger is the ability being CREATED, so it can
  never be the creating ability's delivery; that was the inconsistency §2d
  resolves. Garruk, Caller of Beasts
  is not a `cast-trigger-` card because its **−7 emblem** says "whenever you
  cast a creature spell"; Jace, Cunning Castaway is not a
  `combat-damage-to-player-` card because a **+1** made that delayed trigger.
  Membership on the EFFECT axis may still be correct; the DELIVERY axis is not.
  This is the same principle as "DELIVERY is determined by ability STRUCTURE,
  never by effect words", applied one level up: read *whose* ability it is
  before reading what it does. Record:
  `docs/REAUDIT-TIER-1-FINDINGS-2026-08-02.md` §2a.
- **A `{T}` in an activated cost is AXIS IDENTITY (Captain-ratified
  2026-08-02, D3f).** Tapping caps an ability at once per turn; an
  otherwise-identical ability without it goes arbitrarily wide with mana. That
  is a when/whether difference, not a magnitude one, and it separates a combo
  piece from a value creature — so the tapped and untapped forms are siblings,
  never one axis. Worked case: `activated-tap-grants-haste-other-creature-you-control`
  (Paragon of Fierce Defiance) vs `activated-grants-haste-any-creature` (Boros
  Guildmage). Test to apply: does the distinction change WHEN or WHETHER the
  effect can happen (split), or only how much (parameter, per batch-5's
  counter-polarity ruling)? Record:
  `docs/TIER-2-DECISION-PACKET-2026-08-02.md` D3f.
- **`combat-` is a RESTRICTION, not decoration (Captain-ratified 2026-08-02).**
  A card reading "whenever ~ deals damage to an opponent" makes no
  combat claim and takes `any-damage-to-player`. The two are different
  mechanisms for deck-building — an any-damage trigger fires off pingers, burn
  and fight effects — so they never share an axis. Record:
  `docs/DAMAGE-DELIVERY-RULING-2026-08-02.md`.

### 2g. `kicker` is RETIRED from DELIVERY (Captain-ratified 2026-08-06)

Captain, 2026-08-06: *"go forward with … kicker's retirement from §2."*

**The contradiction.** §2 listed `kicker` as a DELIVERY slot value. §2b, ratified
2026-08-03, says a CR 702 keyword's delivery is **derived from its `702.Na`
class** — and the CR states that class outright:

> **CR 702.33a** — *"**Kicker is a static ability** that functions while the
> spell with kicker is on the stack. 'Kicker [cost]' means 'You may pay an
> additional [cost] as you cast this spell.'"*

So `KEYWORD_HOME["kicker"]` is `static`, the router has always been right, and
the `kicker` row predates §2b and was simply never retired.

**Measured 2026-08-05 (`AUDIT-5` §1, emitter census):**

| | |
|---|--:|
| axes using the token | **0** |
| **emitters in the classifier** | **none** — no `mark()` or `msub()` ever produced it |
| corpus lines printing `Kicker …` | **216**, all correctly routed to `static` |

This is the standing trap *"a ratified token with no EMITTER looks exactly like
one with no members"* — the token was unreachable, not merely unused.

**The ruling.**

- **`kicker` is REMOVED from §2's DELIVERY vocabulary**, struck through in the
  table exactly as `delayed` was by §2d. The table is machine-parsed, and the
  strikethrough is what removes it: `ratified_delivery_tokens()` rejects any
  cell that is not `[a-z0-9-]+`, so `~~kicker~~` no longer parses as a token.
- **Kicker is an ADDITIONAL COST (CR 601.2b), not a delivery.** A cost is
  something you pay to cast; a delivery is *how the ability reaches the game*.
  The two were conflated because the printed word looks like a keyword slot.
- **Nothing in the classifier changes**, and that is the point — a retirement
  with a routing diff would mean the token *was* load-bearing.

**§2's DELIVERY vocabulary is 53 → 52 tokens.**

### 2f. Shapes REPORTED, never routed — and why this is not part of §2's table

House style is *halt loudly, never best-guess*, so a shape with no ratified home
is emitted under its own descriptor rather than approximated onto a neighbour.

| emitted as | n | why it is not routed |
|---|--:|---|
| `main-phase-unqualified` | 1 | Carpet of Flowers, *"at the beginning of each of your main phase**s**"* — CR 505.1's **collective** sense, firing on **both** main phases. A real fourth shape at n=1; §6b rule 1 says per-shape axes are free, so this awaits a Captain call rather than being folded into `precombat-` |
| `to-graveyard-zone-unstated` | 11 | Genju of the Realm, Aetherworks Marvel. **CR 110.1 makes a *permanent* necessarily on the battlefield**, so *"a permanent … is put into a graveyard"* **is** dies by CR 700.4 even with the zone unstated — but a *card* is not on the battlefield, and the printed words alone cannot tell the two apart |
| `battle` on `is-dealt-damage-trigger` | 0 | reserved by CR 120.1's closed enumeration, **not instantiated**. Zero members is a hypothesis, not an absence (the `is-attacked-trigger` precedent) |

**This subsection exists because of the trap it documents.** §2's table is parsed
at run time by `foundry_shape_extractor.ratified_delivery_tokens()`, which reads
**every table row between the `## 2.` heading and the first `###`**. The two
descriptors above were first written into a note table directly under §2's
table — and the extractor promptly ratified them, turning the two shapes this
project had deliberately left open into vocabulary. It was caught the same pass
by a routing diff, not by review.

**This is the second instance of the same trap.** The parser's own comment
records the first: reading to `## 3.` instead of to the first `###` ingested
§2a's prefix-table cells and *"silently widening the vocabulary from 19 to 23."*
**Standing rule: any table under `## 2.` that is not ratified DELIVERY
vocabulary belongs in a `###` subsection.** Prose and bullet lists are safe; a
table is not.

### 2e. A static ability that GENERATES a replacement effect takes `replacement` (Captain-ratified 2026-08-04)

The third of the three questions the 14-row sheet flagged, and the one that
governs more than the card that raised it. **§2b says a CR 702 keyword's class
picks its slot. For 16 keywords the CR names the class `static` and then prints
a templated text that CR 614.1c calls a replacement effect.** The two readings
gave opposite answers on 282 lines.

> **CR 702.104a** — *"Tribute is a **static ability** that functions as the
> creature with tribute is entering the battlefield. 'Tribute N' means '**As
> this creature enters**, choose an opponent…'"*
>
> **CR 614.1c** — *"Effects that read '[This permanent] enters with . . . ,'
> **'As [this permanent] enters . . . ,'** or '[This permanent] enters as . . .'
> **are replacement effects**."*

**The CR CHAINS these rather than opposing them, and that is the resolution.**
CR 113.3d: *"Static abilities … **create continuous effects**."* CR 614.1:
*"**Some continuous effects are replacement effects.**"* So "static ability" and
"replacement effect" are not competing classifications of one object — they name
the **ability** and the **effect it creates**, and §2's DELIVERY slot has always
described the effect's shape.

**RATIFIED: `replacement`, and no code change was needed** — the DET already
routed these. Three further grounds, each independent:

- §2's own `replacement` row already claims *"'enters with/as' shapes"* and
  cites 614.1a–c, so the template was spoken for before Tribute was examined.
- A replacement effect is not *"continuously true"*, which is §2's gloss on
  `static` (CR 113.3d).
- The **66** *"enters with"* lines were **already** `replacement`. Leaving
  Tribute on `static` split **one CR template across two tokens** — the failure
  §2 exists to prevent.

**Scope of this ruling: all 16 keywords in that bucket, 282 lines**, not Tribute
alone. This **amends §2b**, which is otherwise unchanged: a keyword's `702.Na`
class still picks the slot, except that where the same sub-rule's templated text
is a CR 614.1a–c replacement template, the template wins. Record:
`docs/TURNED-FACE-UP-RULING-2026-08-04.md` §4.

### 2d. `delayed` is a QUALIFIER, not a DELIVERY (Captain-ratified 2026-08-03)

Captain: *"delayed triggers can be annoying. CR describes it. make sure you
checked."* Checked, and the check found §2 contradicting itself.

**The contradiction.** §2 listed `delayed` as a DELIVERY slot value. But §2's own
created-ability rule says the delivery belongs to the **creating** ability,
never the created one — and a delayed trigger is *definitionally* a created
ability. The two cannot both hold.

**The CR settles it, and it agrees with the created-ability rule:**

> **CR 603.7a** — *"Delayed triggered abilities **are created during the
> resolution of spells or abilities**, as the result of a replacement effect
> being applied, or as a result of a static ability…"*
>
> **CR 603.7d** — *"If a spell creates a delayed triggered ability, **the source
> of that delayed triggered ability is that spell**."*
>
> **CR 603.7e** — *"If an activated or triggered ability creates a delayed
> triggered ability, **the source … is the same as the source of that other
> ability**."*

The CR assigns the **source** to the creator. §2 assigns the **delivery** the
same way. So a card that sets up a delayed trigger has the delivery of whatever
*created* it — a spell ability (unmarked), an `etb`, an `activated` — and
**there is no card left for `delayed` to be the delivery of.** Measured: the
DET extractor never emitted it, and could not.

**RATIFIED:**

- **`delayed` is REMOVED from §2's DELIVERY vocabulary.**
- **`delayed` is ratified as a §1 QUALIFIER** meaning *the effect happens at a
  later, stated timing point rather than on resolution*. Anchor CR 603.7.
- A card's DELIVERY is always its creating ability. Flickerwisp is `etb`;
  Silent Assassin ("{3}{B}: Destroy target blocking creature at end of combat")
  is `activated`. Both create delayed triggers; neither is `delayed`.

**This is what the three live axes already mean.** Every one of their
definitions is written from the creator's side — *"**Sets up** a delayed
triggered ability that…"*:

| axis | n | reading |
|---|--:|---|
| `rule:delayed-destroy-trigger` | 3 | the destroy happens later |
| `rule:delayed-draw-next-upkeep` | 6 | the draw happens later |
| `rule:delayed-cantrip` | 1 | *"the card draw arrives later via a delayed trigger"* |

So no member moves and no definition changes. **§1's slot order puts QUALIFIER
last**, so these three read out of order (`delayed-destroy-trigger` rather than
`destroy-delayed`). That is a **name-only slot-order migration, LOGGED not
executed** — it requires choosing three new names, which is a design call of its
own and not part of resolving this tension.

**No ratified number moves.** `END-STEP-TRIGGER-RULING-2026-08-03.md` §1 sets
aside 333 cards printing "at the beginning of the **next** end step" as already
buildable. They still are — as their creator's delivery rather than as
`delayed`. The end-step family stays **536**.

### 2c. `cycles-a-card-trigger` IS `any-cycled-trigger` — one name, not two

Captain ratified **six** remaining trigger tokens on 2026-08-03. Five entered
§2's table above. The sixth, `cycles-a-card-trigger` (21 cards, "whenever you
cycle **a**/another card"), was **not minted as its own token** — because §2a,
ratified the same day, already names that exact shape:

| printed | token |
|---|---|
| "When you cycle **this card**" (CR 702.29c) | `cycled-trigger` — the source, unmarked |
| "Whenever you cycle **a** card" | **`any-cycled-trigger`** — §2a `any-` |
| "Whenever you cycle **another** card" | **`other-cycled-trigger`** — §2a `other-` |

The **shape is ratified**; it is its slug that comes from §2a rather than from a
new table row. Minting `cycles-a-card-trigger` alongside `any-cycled-trigger`
would give **two slugs for one mechanic**, which design goal #1 forbids by
name — it is the `scales-token-count-with-x` duplication class.

This is the first case of §2a absorbing a token that was proposed before it
existed, and it will not be the last: **any future "self vs a/another"
proposal in a trigger family is already named.** Check §2a before minting.

### 2b. A CR 702 KEYWORD'S DELIVERY IS DERIVED, NOT RULED (Captain-ratified 2026-08-03, Q5)

**A keyword ability never needs a per-keyword delivery ruling.** Its ability
class and its trigger event are both stated by the CR in its own `702.Na`
sub-rule, so its §2 slot is *derivable*:

    702.6a   "Equip is an ACTIVATED ability of Equipment cards."
    702.108a "Prowess is a TRIGGERED ability. 'Prowess' means
              'WHENEVER YOU CAST A NONCREATURE SPELL, ...'"

**CR 702.1** licenses reading it this way: *"the object lists only the name of
the ability as a 'keyword'; sometimes **reminder text summarizes** the game
rule."* The printed keyword is a **pointer**; the CR rule is the definition and
the reminder text is only a summary. That is the same boundary §6a already
draws when it excludes reminder-text parentheticals from a card's claim — the
card's reminder text is discarded, and the CR's own wording supplies the shape.

**RATIFIED:** route a CR 702 keyword to the §2 token its `702.Na` text
resolves to. No new vocabulary; no ruling per keyword.

Derived by `experiments/foundry_cr702_classes.py --homes`, zero tokens:
**138 of 193 keywords route to an ALREADY-RATIFIED token.**

| home | n | keywords |
|---|--:|---|
| `static` | 63 | Flying, Trample, Vigilance, Flash, Kicker, Convoke, Morph … |
| `replacement` | 16 | Amplify, Bloodthirst, Dredge, Madness, Modular, Riot … |
| `activated` | 13 | Cycling, Equip, Crew, Embalm, Level Up … |
| **`attack-trigger`** | **11** | **Annihilator, Battle Cry, Dethrone, Firebending, Frenzy, Melee, Mentor, Mobilize, Myriad, Provoke, Training** |
| `etb` | 9 | Backup, Champion, Exploit, Fabricate, For Mirrodin!, Living Weapon … |
| `cast-trigger` | 8 | Cascade, Demonstrate, Extort, Gravestorm, Prowess, Ripple, Storm … |
| `death-trigger` | 5 | Afterlife, Haunt, Persist, Soulshift, Undying |
| `blocks-or-becomes-blocked-trigger` | 4 | Afflict, Bushido, Flanking, Rampage |
| `combat-damage-to-player` | 3 | Ingest, Poisonous, Renown |
| `upkeep-trigger` | 2 | Cumulative Upkeep, Echo |
| `becomes-targeted-trigger` | 1 | Ward |
| `any-attack-trigger` · `any-etb` · `any-death-trigger` | 3 | Exalted · Evolve · Recover (§2a) |

**55 remain unrouted and are reported, never approximated** — 49 whose
templated text is a cost/static shape, 5 with neither templated text nor a
single class (Companion, Forecast, Foretell, Space Sculptor, Start Your
Engines!), and **Visit**, which genuinely needs new vocabulary ("whenever you
roll to visit your Attractions").

**A keyword's CLASS and its TRIGGER EVENT are separate questions.** The class
says *which slot*; the templated text says *which token in that slot*. Ten
keywords are multi-class (CR 702.62a: *"Suspend is a keyword that represents
**three abilities**"*) and the tool warns rather than collapsing them.

### 2a. TRIGGER SUBJECT — the `other-` / `any-` prefixes (Captain-ratified 2026-08-03)

Every DELIVERY row in §2's table names the SOURCE as the trigger subject: "when
**~** enters", "whenever **~** attacks", "when **~** dies". Read literally, as
§6a demands, **a trigger keyed on any other permanent had no name at all** —
measured corpus-wide at **1,558 cards** across five families.

The gap is not "self vs other". It is three-way, and **CR 603.6a** is the
anchor:

> "Each time an event puts one or more permanents onto the battlefield, **all
> permanents on the battlefield (including the newcomers)** are checked for any
> enters-the-battlefield triggers that match the event."

"Including the newcomers" means a permanent printed "whenever **a** creature
you control enters" **sees its own arrival**. That is exactly why the templating
prints "another" when it wants to stop it — Soul Warden's *"Whenever **another**
creature enters"* uses the word to do a job.

**RATIFIED — a DELIVERY subject prefix, applied to any §2 trigger token:**

| prefix | printed subject | the source | example |
|---|---|---|---|
| *(unmarked)* | "when **~** enters" | **is** the trigger | `etb` |
| `other-` | "whenever **another** creature enters" | **excluded** | `other-etb` |
| `any-` | "whenever **a** creature enters" | **included** | `any-etb` |

Composes with every trigger token in §2 and with every one ratified later —
`other-death-trigger`, `any-attack-trigger`,
`other-leaves-battlefield-trigger`, `any-combat-damage-to-player`, and so on.
Per §11 a node instantiates on its first quote-verified member with no fresh
ratification.

**The worked pair, both creatures, one word apart:**

- **Venom Connoisseur** — "Whenever **another** creature you control enters,
  this creature gains deathtouch." Its own ETB does nothing. → `other-`
- **Sharp-Eyed Rookie** — "Whenever **a** creature you control enters, if its
  power is greater than this creature's power…" Its own ETB **does** trigger
  it. → `any-`

Fusing them would make the codebook assert something false about one of them.
§6a rule 3 already forbade it: *"a slug may not claim `another` of a member
whose printed text can affect itself."*

**`any-` is MARKED, and stays marked (Captain-ratified).** Bare "a" is the
majority shape — 1,183 of 1,594 ability lines — so the marked form is more
common than the unmarked one. That is deliberate and is not to be "corrected"
by a later session: the unmarked form already means *the source*, and
overloading it to also mean *any permanent* would make it readable as two
mechanics, which is design goal #2. **Frequency does not earn the unmarked
slot; only the source does.**

**Opponent-controlled subjects follow the PRINTED word (Q2, ratified).** 62
lines print "a creature **an opponent controls** dies" — mechanically the source
can never be that creature, so `any-` and `other-` are indistinguishable in
play. They still take `any-`, because §6a's premise is that the printed word is
the claim. The redundancy is harmless; a mechanics-based exception would put
the reader back to case-by-case judgement.

**Consequence for SCOPE.** The trigger's CONTROLLER (`you control` /
`an opponent controls`) is a **separate slot** and uses §6's existing tokens —
no new vocabulary. But §1's "SCOPE is REQUIRED the moment a scope-sibling
exists" bites immediately, because controller-siblings exist in nearly every
family.

**Migration — LOGGED, not executed.** No delivery-bearing axis renames, because
the unmarked tokens keep their meaning. Two axes encode a trigger-subject
"other" ad hoc and normalize onto this grammar (6 memberships total):

| axis | n | note |
|---|--:|---|
| `rule:gains-life-on-other-creature-etb` | 3 | Soul Warden's axis |
| `rule:death-of-other-permanents-grows-this-creature` | 3 | |

Execution is a codebook mutation and rides its own step under the backup law
with determinism ×2 — **not executed at ratification**, per the standing
"no midflight renames" rule (§12a precedent).

Record: `docs/DELIVERY-VOCABULARY-BATCH-2026-08-03.md` Q1/Q2, which also carries
the measurement and the three generator defects that put the first number at
1,921 instead of 1,558.

## 3. Activation-restriction family — fully enumerated, DET-owned

The batch 5–7 failure class (own-upkeep collapse, Kjeldoran during-combat).
This family is CLOSED, exact-phrase, and moves entirely to Lane 1 (DET);
SYNTH never assigns these again. Each row is a ratified DET pattern:

| Printed phrase (anchored, both templating eras) | Slug |
|---|---|
| "Activate only as a sorcery" (CR 602.5d) | `activation-restricted-to-sorcery-speed` |
| "Activate only as an instant" (CR 602.5e) | `activation-restricted-to-instant-speed` |
| "Activate only during your turn" | `activation-restricted-only-during-your-turn` |
| "Activate only during your upkeep" | `activation-restricted-to-own-upkeep` |
| "Activate only during combat" | `activation-restricted-during-combat` |
| "Activate only during an opponent's turn" | `activation-restricted-during-opponents-turn` |
| "Activate only once each turn" (CR 602.5b) | `activation-restricted-once-each-turn` |
| "Activate only if ..." (condition-gated) | `activation-condition-gated` (wide net; condition facet to ledger) |

DET patterns must canonicalize "Activate this ability only ..." (older
templating) to the modern phrase (Lesson-1 both-polarity discipline applied to
templating eras). Compound restrictions ("only during combat and only if...")
get EVERY applicable tag (M8 logic applied to restrictions).

The same enumeration discipline applies at the walk to any other closed CR
family the codebook touches: keyword classes (CR 702 first lines — already the
keyword-bucket job), replacement shapes (614.1a/b/c), casting-timing families.

## 4. EFFECT verbs — standardized forms

One verb per mechanic, chosen once, used everywhere:

- `destroy`, `exile`, `bounce` (return to hand), `tuck` (to library),
  `sacrifice`, `discard`, `mill`, `draw`, `loot` (draw-then-discard),
  `scry`, `surveil`, `proliferate`, `tutor` (search library), `reanimate`
  (graveyard → battlefield), `regrowth` (graveyard → hand, ratified b5 vocab),
  `create-token`, `pump` (+P/+T), `debuff` (−P/−T), `damage`, `gain-life`,
  `lose-life`, `drain` (damage/loss + symmetric gain), `tap`, `untap`,
  `tap-or-untap`, `transform`, `copy`, `counters` (verb — see section 8),
  `grants-<keyword>`, `taxes` (cost increase), `cost-reduction`.
- RATIFIED (D-2): bare verb stem everywhere EXCEPT the `counters-` verb
  (section 8) — the b5 D14 `create-token-<type>` standard generalizes.
  All `creates-` slugs normalize at the walk.
- "scroll" = instant-or-sorcery(+interrupt) card (ratified b5 vocab; glossary
  entry required in the embedded codebook).
- "uncounterable" = adjective, "this spell can't be countered" (ratified Q4,
  walk-ratification 2026-07-31 — `rule:cant-be-countered` renames to
  `rule:spell-uncounterable`, replacing the banned `countered` participle).
- "imposes" = verb, an ability forces a state onto something OTHER than its
  own source (ratified 2026-07-31, B3/B4 follow-on — Captain-authored
  `rule:imposes-enters-tapped`, the Root Maze class sibling of
  `rule:enters-tapped`).

## 5. OBJECT vocabulary

`creature`, `artifact`, `enchantment`, `planeswalker`, `battle`, `land`,
`permanent`, `nonland-permanent`, `spell`, `noncreature-spell`,
`creature-spell`, `player`, `opponent`, `any-target` (damage only, = the CR
"any target" shorthand), `card-in-graveyard` families
(`creature-card-graveyard` etc.), token types (section 8).

Per-object-class siblings are the law for every `targeted-<action>` family
(M8 generalized, b6 D3): OR-shaped multi-class targets get every applicable
class tag; the class lattice (`targeted-bounce-<class>`,
`targeted-destruction-<class>`...) is a ratified grammar with virtual nodes.

## 6. SCOPE vocabulary

`self` (the source), `you-control` / `you-own` (see 6d; `own` is RETIRED),
**`active-player`** (the player whose turn it is — **CR 102.1** defines the
term verbatim: *"The active player is the player whose turn it is."*
Captain-ratified 2026-08-03, Q3. Required by "at the beginning of **the** end
step", 50 cards, where `you-control` is wrong (it need not be your turn) and
`each` is wrong (it fires once, not once per player)),
`opponent`, `any`, `each`
(non-targeted, all-covered), `target` (ONLY when the word "target" appears in
the ability per CR 601.2c — the b7 Unwind ruling: "untap up to three lands"
without "target" may NOT sit in a `-target-` slug), `defending-player`
(CR 506.2; the bare word "defender" is BANNED in slugs — it collides with the
Defender keyword, Captain's b7 ruling generalized), `two-target` (fixed
plurality), **`enchanted-player`** (the player an Aura is attached to —
**CR 303.4b** defines the term verbatim: *"The object or **player** an Aura is
attached to is called **enchanted**."* **CR 702.5a** supplies the ability that
makes a player a legal attachment at all: *"Enchant is a static ability,
written 'Enchant [object **or player**].'"* Captain-ratified 2026-08-05. **54 corpus lines**
print it — the Curse cycle (Curse of Oblivion, Cruel Reality, Overwhelming
Splendor, Trespasser's Curse) plus Curse of Obsession and Righteous Authority
on `draw-step-trigger` and Grievous Wound on `is-dealt-damage-trigger`. Before
this row those lines carried **no scope token at all**, because no §6 value
named the player: `opponent` is wrong — an Aura may enchant any player,
including you — and `you-control` / `each` are simply false. It is a SCOPE
value and never a delivery: an Aura's own delivery is `static` per §2e's
sibling reasoning),
`-conditional` (an intervening-if or "unless" gate on the same
ability; the gate must be quoted in evidence).

### 6d. OWNERSHIP vs CONTROL — `you-control` / `you-own` (Captain-ratified 2026-08-03)

The scope token `own` was glossed "(yours)", which does not say **which**.
The CR does.

- **CR 109.5** — *"The words 'you' and 'your' on an object refer to the
  object's **controller**, its would-be controller…, or its **owner (if it has
  no controller)**."*
- **CR 110.2** — *"**Every permanent has a controller.**"*
- **CR 109.4** — *"**Only objects on the stack or on the battlefield have a
  controller.**"* With **CR 108.4a**, a card in hand/library/graveyard/exile/
  command has none, so "you own" is the **only available referent** there.

**RATIFIED — Option B, the printed words:**

| token | means | printed |
|---|---|---|
| `you-control` | the controller (CR 109.5 / 110.2) | "you control" |
| `you-own` | the owner (CR 108.3) | "you own" |

**`own` is RETIRED as a SCOPE token** and renames to `you-control`. Same
reasoning that retired `mass-` in §6c: it is a project coinage sitting on top
of a printed distinction, and here it actively collides with the English word
for the *other* sense.

**`owned` was considered and REJECTED.** A one-letter difference carrying a
load-bearing distinction is the CDR-09 homograph failure — where
`counter`/`counters` sorted by grammatical number instead of by sense and
misfiled 17 of 33 counter axes. `you-control` / `you-own` cannot be confused.
Multi-word stem tokens are already ratified (§14 Q8.5, `cant-be-blocked`), and
`activated-tap-grants-haste-other-creature-you-control` was already using this
form.

**Ownership is not an edge case — 91 battlefield cards.** **Brand** exists
solely because owner ≠ controller ("gain control of all permanents **you
own**"), as do Gruul Charm and Lich's Mirror. The blink family (Yorion,
Charming Prince, Venser, Sword of Hearth and Home) prints "you own" so the
permanent returns to **you**. ~25 are "commander creatures you own".
**Jon Irenicus, Shattered One** prints "a creature **you own but don't
control**" — both senses in opposition on one card.

A further **93 cards** print "«card» you own" in a non-battlefield zone; those
are CR-forced by 109.4 and carry no scope claim, so they take **no** scope
token. Plus 20 cards printing "an opponent owns".

**Placement follows §1's slot order** `[EFFECT]-[OBJECT]-[SCOPE]` — the scope
goes **after** the object, so `pump-own-creature` becomes
`pump-creature-you-control`, which is also how the pre-existing
`activated-tap-grants-haste-other-creature-you-control` already reads. The old
`-own-<object>` form had the scope on the wrong side of the object.

**`own` turned out to carry FOUR senses, not three.** A blind rename produced a
wrong name and was caught by Gate 4 — the transform disagreed with a ratified
list, and the transform was what was wrong:

| sense | where | disposition |
|---|---|---|
| controller of an object | §6 SCOPE | **renames to `you-control`** |
| counters **on the source** | §7 `own-counters` | **excluded** — separate §7 ruling → `self-counters` |
| **whose turn/phase it is** | §3 `activation-restricted-to-own-upkeep` | **excluded** — a RATIFIED §3 table slug (D-4, DET-owned); "Activate only during **your** upkeep" is not an object's controller |
| ownership (CR 108.3) | **new** | **`you-own`** |

**Migration — EXECUTED 2026-08-03.** **20 axes / 169 memberships** renamed;
**3 axes / 54 memberships excluded** for the reasons in the table above, all
recorded in the spec. Name-only: no member moved, no definition changed.

| | |
|---|---|
| spec | `experiments/moves/2026-08-03-own-to-you-control.json` |
| backup | `codebook.v0.7.pre-own-to-you-control.20260803-151959.json`, readback-verified |
| sha256 | `48e36cc7…` → `5fa27b70fabdce8d40e537907358522449d4ce642d80f6680314c1b2d2e7d93e` |
| determinism | ×2 byte-identical (4,128,049 bytes) |
| axes | 545 → 565 · **active 359 → 359** |
| assertions | 8,571 → 8,740 (+169 rename copies — the tombstone retains its members and the new slug carries them, CDR-09 model) |
| Gate 2 after | lint clean · sweep 232 / 6 blocking · drift 35 — all unchanged |

The three excluded axes still carry the bare token `own` and are **correct**:
`activation-restricted-to-own-upkeep` (§3), `cost-reduction-scales-with-own-counters`
and `pump-scales-with-own-creature-count` (both §7). A conformance check that
flags them has not read this section.

Record: `docs/DELIVERY-VOCABULARY-BATCH-2026-08-03.md` §5.

### 6a. THE PRINTED WORD IS THE CLAIM (Captain-ratified 2026-08-02)

> **"Game logic is game logic. It cannot be partially assumed or opened for
> interpretation. If something targets, it targets. If it does not target, it
> does not target. All words used purposefully and not up to interpretation."**

Templating words are CR terms of art chosen deliberately, not English prose.
They are **hardcoded to the mechanic they name** and are **axis identity**,
never a facet deferred to the schema pass.

Binding consequences:

1. **`target`** (CR 115.1, 601.2c) — a slug may contain `target` only where the
   ability prints the word "target". Generalizes the b7 Unwind ruling from one
   card to a law. Burden of Guilt's "{1}: Tap **enchanted** creature" is not a
   targeted tap; Unstable Amulet's "deals 1 damage to **each opponent**" is not
   an any-target damage effect.
2. **`you control` / ownership** — a restriction on the affected object.
   An axis scoped `any-*` asserts it can affect an opponent's permanents; a
   member printed "target creature **you control**" cannot, and does not belong.
   **"Any" must mean any.**
3. **`another` / `other`** — excludes the source. A slug may not claim it of a
   member whose printed text can affect itself. Man-o'-War returns "**target**
   creature", not "another", so it can bounce itself and is not an
   `-other-creature` member.
4. **The scope field and the slug may not make opposite claims.**

**EXPLICIT PARTIAL REVERSAL — batch-6 D3.** That directive ruled, on
`rule:etb-pump-target-creature` by name, that the ownership clause be dropped
and *"ownership-scope logged as a facet dimension for the schema pass."*
Ownership is now axis identity. Logged as a reversal per §13's D6-style
discipline; batch-6 D3's other provisions are untouched.

**Where the reminder-text boundary sits.** A card's claim is its printed
oracle text with reminder-text parentheticals **excluded** — a token-definition
parenthetical states what the *token* does, which §2's created-ability rule
assigns to the token, not the card. This is the tier-4 §S4 boundary and it is
the same one that separates 44 real DET defects from 154 false ones.

**Enforcement.** `foundry_definition_drift.py` check **C4** (a/b/c/d), which
did not exist before this ruling — no gate read scope, targeting or ownership.
First run: **93 memberships across 22 active axes**. That population is the
measured cost of the rule never having been enforced, and it is a decision
packet's worth of rulings, not a mechanical fix.

### 6c. `mass-` is RETIRED from axis names (Captain-ratified 2026-08-02)

> *"'Mass'. What does mass mean in Magic the Gathering? Mass is not game logic
> wording. Mass should only be used for the parent layer to relate two cards
> that affect all players and just your opponents."*

**Measured: the Comprehensive Rules print the word "mass" zero times in 10,060
lines.** It is a project coinage. What the CR prints is `each`, `all`,
`any number of`, `target`. So `mass-` is a **job** word, and §6b puts job words
in the parent layer.

- **BANNED in axis names.** Use the printed scope, composed from the §6 tokens
  above: `each-<class>` symmetric, `each-own-<class>` / `each-opponent-<class>`
  one-sided.
- **RATIFIED as PARENT vocabulary**, for exactly the job Captain names:
  relating "affects everyone" to "affects just your opponents". That
  relationship is real and belongs one layer up.
- Amends §6's own scope list, which had carried `each`/`mass-` as equivalents.
  They are not equivalent: `each` is printed, `mass` is not.

**Why it was not harmless.** "Mass" papered over the symmetric/one-sided
distinction, and three axes came to hold both — `mass-damage-opponent-creatures-only`
said *opponent creatures only* while holding Wildfire Howl, "deals 2 damage to
**each creature**", which hits yours too. A symmetric sweeper and a one-sided
sweeper are different cards for deck-building.

**Executed 2026-08-02:** 12 of 15 renamed (`experiments/moves/2026-08-02-mass-retirement.json`).
The rename also retired `destruction` → `destroy` on `mass-creature-destruction`,
a §4 violation CDR-PROPOSALS §1 had already identified. One axis was found not
to be a mass effect at all: `mass-untap-and-haste-stolen-creatures`' 14 members
all print "Untap **that** creature" — singular. The remaining 3 conflating axes
need SPLITS, not renames, and are open.

### 6b. SHAPE vs JOB — the two layers (Captain-ratified 2026-08-02)

> **"All cards have absolute shapes. Shapes shared among other cards. There's
> no value lost to build per-shape axis. This game ultimately does not contain
> ambiguity whatsoever. Linking the spirit of each card is of course up for
> interpretation. But hard game logic is not."**

Two layers, and confusing them is what produces both false merges and false
splits:

| layer | governed by | ambiguity | lives in |
|---|---|---|---|
| **SHAPE** — what the card literally does | printed text, CR terms of art | **none** | the axis (child) |
| **JOB** — what the card is *for* | play outcome, deck role | genuine, interpretive | the parent |

This sharpens the standing parent-tree principle (*"children are defined by
MECHANISM, parents are defined by JOB"*) by naming the reason: mechanism is
decidable, job is not.

**Three binding consequences:**

1. **Per-shape axes are free. Mint them.** A distinct printed shape earns its
   own axis even at n=1. Do not fold a shape into a near neighbour to avoid
   axis count, and do not treat a printed distinction as a "facet" to defer.
   Thinness of membership is not an argument against a real shape.
2. **Never be allergic to a new ruling** when a legitimate game-logic shape
   demands one.
3. **Adjacent vocabulary is not equivalent vocabulary.** *"Each opponent and
   each player for instance are completely different and have real in-game
   consequences players must accept. These are not equitable."* Same for
   `player` vs `opponent` vs `defending player`, `choose` vs `target`, `may`
   vs mandatory, `each` vs `all`, `another` vs `target`.

**The hard part, stated by Captain as the open challenge:** finding linkage
between cards whose *verbatim game logic differs* but whose *gameplay outcome
converges*. Worked case, ratified as the illustration:

> **The One Ring** and **Grand Abolisher** are semi-related — both protect you
> from outside threats. But The One Ring is **one turn cycle**, and Grand
> Abolisher is **your-turn anchored.** Different shapes; adjacent jobs.

So they are **never one axis** (the durations are printed, hard, and
consequential) and are **candidates for one parent** (the job is the same
answer to "what does this card do for my deck"). That is precisely the Tier-3
promise — *same job, different words* — and it is the parent layer's work, not
the axis layer's.

**Consequence for anyone merging:** two axes may be merged only when their
printed shapes are identical. Similar *outcome* is never grounds for a merge;
it is grounds for a shared parent.

**Parents are UNRANKED (Captain-ratified 2026-08-02).** A card that earns two
jobs holds both at equal weight — *"neither one wins, they live both
simultaneously… applied unbiased."* Monstrous Rage is a combat trick **and** an
enchantment-deck card; which matters is a property of the deck being built, not
of the card. There is no primary parent and no discount on a second one. Full
ruling and its build consequences: `docs/PARENT-TREE-CANDIDATES.md` S4a.

## 7. Scaling standard

One connective, one order, closed stat list — RATIFIED (D-3):
**`<subject>-scales-with-<stat>`** (matches
`x-scales-with-permanent-count` and the ledger's N-scales-with-N scheme;
`-scaled-by-` is retired at the walk).

Closed stat vocabulary (b6/b7 confusion pairs made explicit): `creature-count`,
`hand-size`, `own-counters` (counters ON the source; the charge-counter class),
`graveyard-count`, `graveyard-creature-count`, `land-count`, `land-type-count`,
`permanent-count`, `attacker-count`, `legendary-creature-count`, `mana-value`,
`life-gained`, `x`, `opponent-count`, `target-count` (the Hinata stat),
`token-count`, `color-count`, `target-color-count` (the colors of the TARGET
 itself, not a board count — Captain-ratified 2026-08-02, D3e), `charge-counters` (alias of own-counters where
the type matters), `opponent-tapped-creature-count` (F3, walk-ratification
2026-07-31 — required by the draw-scales-with-opponent-tapped-creature-count
D-3 rename target), `sacrificed-creature-toughness` (the toughness of the
creature sacrificed to pay for the effect — Captain-ratified 2026-08-02,
tier-3 D3; same gap-closing as F3, the slug
`lifegain-scales-with-sacrificed-creature-toughness` was ratified as a D-3
rename target in the walk's §2.2.1 while its stat token was never added here).

**`attacker-count` and `creature-count` are DIFFERENT stats, not one
parameterized stat** (tier-3 D4, Captain-ratified 2026-08-02). Both were
already listed above; the ruling records that the distinction is load-bearing
and splits axes. Worked case: `attack-trigger-pump-scales-with-creature-count`
(Rinoa Heartilly, "for each creature you control") vs
`attack-trigger-self-pump-scales-with-attacker-count` (Akroan Hoplite, "the
number of **attacking** creatures you control"). Same shape as D3e's
board-color-count vs target-color-count split. Record:
`docs/TIER-3-DECISION-PACKET-2026-08-02.md` D3/D4.

The two token axes under this standard (answers b7 line-84):
- X scales HOW MANY tokens → `token-count-scales-with-x` (absorbs the
  duplicate `scales-token-count-with-x` at the walk).
- X scales counters ON one created token → `create-token-with-x-counters`.

## 8. The counter/token disambiguation laws

Hard rules, each anchored:
1. **Noun sense (CR 122.1) is always TYPED:** `plus1-counter`, `minus1-counter`,
   `charge-counter`, `stun-counter`, `loyalty-counter`, `<name>-counter`.
   The bare noun "counter" never appears in a slug. Generic axes use
   `-counters` only with a binding word (`etb-with-counters`,
   `counter-removal-as-activation-cost` → walk-renames to typed or
   `-counters-` forms as feasible).
2. **Verb sense (CR 701.6) is always `counters-<object>`** (`counters-target-spell`,
   `counters-noncreature-spell`). The participle "countered" is BANNED
   (b7 grants-trample ruling generalized).
3. **A counter is not a token and a token is not a counter (CR 122.1,
   verbatim).** Any slug naming one must have evidence quoting that one —
   the b7 Lat-Nam/Gnarlid effect-suffix check, now grammar law.
4. Token types are their predefined names. **The closed vocabulary is CR
   111.10's enumeration in full — all 21 — derived from the CR, not curated
   (Captain-ratified 2026-08-02):**

   `treasure` · `food` · `gold` · `walker` · `shard` · `clue` · `blood` ·
   `powerstone` · `incubator` · `map` · `junk` · `lander` · `mutagen` ·
   `vibranium` · **`role`** (umbrella — see 4a)

   Plus two project umbrellas that are NOT CR types: `creature` (with P/T left
   to evidence) and `mana-producing-artifact` (excludes treasure, which owns
   its own node — S5 semantics at schema pass).

   **Why the full enumeration:** §8 rule 4 previously carried 8 of the 21, and
   the 13 absent ones all have corpus pressure — Incubator 35 cards, Junk 15,
   Map 13, Wicked Role 11, the seven Roles 41 between them. F-E measured the
   consequence: a Map token had no valid slug, so it was absorbed by the
   nearest sibling. A partial enumeration of a closed CR list is a defect, not
   a shortlist.

### 8.4a. `role` is ONE umbrella token type — CDR-11 RESOLVED (Captain-ratified 2026-08-02)

Captain's finding: *"at the moment there are no rules that care about what kind
of role a creature has. just that the roles themselves are either applied, or a
creature having a role, or placing a role."* **Researched against the corpus and
the CR, and confirmed from three independent directions:**

1. **CR 205.3h — `Role` is a single enchantment SUBTYPE.** The seven are token
   *names* ("a colorless Aura Role enchantment token **named Wicked**"), not
   types. The CR itself does not treat them as seven things.
2. **CR 303.7a / 704.5y — the only rule keying off Roles is type-agnostic:**
   *"If a permanent has more than one **Role** controlled by the same player
   attached to it, each of those **Roles** except the one with the most recent
   timestamp is put into its owner's graveyard."* The state-based action reads
   "a Role", never "a Wicked Role".
3. **39 of 39 gate-passing cards printing "Role" only CREATE one.** Every Role
   line is "create a *X* Role token attached to…". Not one card conditions on
   which Role, counts Roles by type, or references a Role except to make it.
   Verified line by line, not sampled.

So the type is named only because a creation instruction must say what it
makes. **`role` is the token type; the specific name is a PARAMETER.**

This follows batch-5's counter-polarity precedent exactly: +1/+1 and -1/-1
counters do *opposite* things and were still ruled a parameter rather than
distinct axes. The Roles likewise differ in effect (Cursed makes the creature
1/1; Wicked gives +1/+1 and drains on death) — that is the honest argument for
splitting, and it is the same argument batch-5 rejected.

**Standing reversal condition, stated so a future session does not have to
re-derive this:** the moment ONE card conditions on a Role's identity — "if
it's enchanted by a Monster Role", "sacrifice a Cursed Role" — this ruling is
void and the seven become vocabulary. The finding is about the current corpus,
not about the mechanic in principle. Re-run the check in §8.4a's evidence
before assuming it still holds.

### 8b. `<type>-counter-placed-trigger` — a §11 grammar family, not a token (Captain-ratified 2026-08-04)

Row 6 of the 14-row §2 sheet. **It is deliberately not a §2 table row**, because
§8 rule 1 is binding: the noun sense is **always typed**, and the bare noun
"counter" never appears in a slug. So the ratified thing is a **grammar** whose
type slot is filled per §8, and per §11 *"a virtual node instantiates the moment
one quote-verified member arrives — no fresh ratification."*

> **CR 122.6** — *"Some spells and abilities refer to **counters being put on an
> object**. This refers to putting counters on that object **while it's on the
> battlefield** and **also to an object that's given counters as it enters the
> battlefield**."*

**That second clause is the non-obvious part and is recorded so a later session
does not "fix" it:** a counter-placed trigger **also fires on counters placed as
the permanent enters**, so it is **not disjoint** from `etb` or from the
CR 614.1c "enters with counters" replacement. §1's multi-axis rule applies — a
card may hold both, and neither subsumes the other.

**These five are DELIVERY nodes, not axes.** `TRIAGE-BATCH-1.md` §1c is binding —
*"delivery-only slugs are parents, not axes"*, the same rule that keeps the bare
axis `rule:end-step-trigger` KILLED while `end-step-trigger` is ratified §2
vocabulary. An axis in this family is a **compound** (delivery + effect), and
none exists yet, so the family record's `instantiated_members` is **empty**.
Listing the five nodes there claimed five axes that do not and should not exist,
and `foundry_family_sweep.py` check A2 reported it BLOCKING. The check was right.

| measured DELIVERY node | lines | cards |
|---|--:|--:|
| `plus1-counter-placed-trigger` | 31 | 31 |
| `plan-counter-placed-trigger` | 9 | 9 |
| **`any-counter-placed-trigger`** | 2 | 2 |
| `loyalty-counter-placed-trigger` | 1 | 1 |
| `hour-counter-placed-trigger` | 1 | 1 |

**`any-` here is §8a's ratified form, not a coinage.** §8a minted it for *"axes
that genuinely span every counter type and therefore cannot be typed"* — Putrid
Hexhag and Stalwart Successor print *"whenever **one or more counters** are put
on"*, with no type word for §8a's left-binding rule to bind to. Naming those
`counter-placed` bare would violate §8 rule 1 **and** §8a's own test.

`plan` and `hour` are `<name>-counter` types per §8 rule 1, verified from **full
oracle text**, not from the trigger line: Political Triumph and Glorious Purpose
both *create* plan counters on themselves; Midnight Clock accrues hour counters.

**The type facet is OPEN, and the family record says so.** §8 rule 1's `<name>`
arm is unbounded — a card may print any counter name — so this family's siblings
are **not enumerable**, and `foundry_family_sweep.py` correctly reports it as
unenumerable rather than manufacturing a product of virtual nodes. Record:
`docs/grammars.json`, family `<type>-counter-placed-trigger`.

**One sibling is PROPOSED and stays RULED-NOT-RATIFIED:
`<type>-counter-threshold-trigger`** — the 11 lines printing an **ordinal**
(Political Triumph, *"the **fourth** plan counter"*; Midnight Clock, *"the
**twelfth** hour counter"*). Its two halves were separated and both answered:
**threshold-vs-every-placement is AXIS IDENTITY** (it fires once at a threshold
rather than on every placement — the ratified D3f WHEN/WHETHER test) while
**which ordinal is a PARAMETER** (magnitude only; batch-5 is a fortiori, having
ruled +1/+1 vs −1/−1 a parameter though they do *opposite* things — and nine of
the eleven lines are one card design, the plan-counter scheme cycle printed with
ordinals 3·4·4·4·4·5·6·7, so treating N as identity would mint five axes for one
mechanic). **It needs zero new vocabulary**: `threshold` was ratified in §14 Q5,
and §8a's position-and-binding principle separates it from the four live axes
using `threshold` in a **static** sense, because `-trigger` is the binder —

| slug | sense |
|---|---|
| `<type>-counter-threshold-trigger` | fires **once**, on the Nth placement |
| `<type>-counter-placed-trigger` | fires on **every** placement |
| `grants-ability-at-threshold` *(no `-trigger`)* | static, continuously true |

**Not ratified here** because the ratification word on the sheet covered the 14
§2 rows and this family; whether that *name* is accepted was carried as its own
question and has not been answered. It is not in `grammars.json`. Record:
`docs/COUNTER-PLACED-RULING-2026-08-04.md` §3a.

### 8a. CDR-09 amendment — sense is carried by POSITION and BINDING, not by grammatical number (Captain-ratified 2026-08-02)

Rules 1–2 above disambiguate by number: singular `counter` = noun, plural
`counters` = verb stem. **That is insufficient, because plural is itself
ambiguous** — `counters` is both the verb stem AND the noun plural.
`rule:etb-with-counters` (noun) and `rule:counters-target-spell` (verb)
carry the identical token. This is the root of the `canonicalize_label`
corruption: `counters` sits in EFFECT_VOCAB and `counter` in the qualifier
sets, so the canonicalizer sorts by grammatical number rather than by
sense.

**Ratified replacement test, enforced across the WHOLE slug — not only in
final-token position, closing the `validate_slug` gap that let
`rule:self-counter-growth` and `rule:etb-with-counters` pass clean:**

1. **VERB sense (CR 701.6)** — the token is `counters` (plural) and is
   **immediately followed by what is countered** (`spell`, `ability`, or a
   restriction word binding to one, e.g. `noncreature-spell`). Never bare,
   never slug-final. Singular `counter` in verb sense is BANNED.
2. **NOUN sense (CR 122.1)** — `counter`/`counters` must be **bound on the
   left**, by either:
   - a counter TYPE word (`plus1`, `minus1`, `charge`, `stun`, `oil`,
     `energy`, `loyalty`, `<name>`), or
   - the preposition `with` (`etb-with-counters`), or
   - **`any`** — newly ratified for axes that genuinely span every counter
     type and therefore cannot be typed. `any-counter` / `any-counters`.

**Why `any-` and not a sense-marker like `counter-object`:** a counter is
**not** an object. CR 109.1 defines *object* as a spell, permanent, card,
token, copy, or emblem; CR 122.1 defines a counter as "a marker placed on
an object or player." The CR's own word for the noun sense is **marker**.
Worse, the VERB sense is the one that genuinely acts on objects (a spell or
ability on the stack IS an object), so a `-object` marker would point at
the wrong sense. `any-` adds no new vocabulary and fills the existing type
slot.

**Consequence for the canonicalizer (ADD-08), measured 2026-08-02.**
`CR-VOCABULARY-AUDIT.md` §4 proposes local adjacency — `counters` is EFFECT
iff followed by an OBJECT token, QUALIFIER iff preceded by a type word or a
`with`-binding — and states it becomes decidable once these renames land.
Tested against all 33 counter-bearing active axes, scored against each
axis's definition-confirmed sense:

| names | misfiles |
|---|---:|
| current | **17 of 33 (52%)** |
| after the §12a renames | **4** |

So the dependency is REAL: 13 of the 17 are fixed by nothing except the
renames, because slugs like `rule:self-counter-growth` have no type word
for the rule to bind to. Implementing position-aware bucketing before the
walk would misfile half the counter axes.

But §4's claim is **too strong** — the renames alone do not finish the job.
Three of the four residuals are defects in the rule as specified, not in
the names, and both must be fixed before ADD-08 is implemented:

1. **The rule must look past SCOPE tokens when hunting the object.** In
   `counters-target-spell` the token after `counters` is `target` (SCOPE,
   §6), not `spell`, so a literal "followed by an OBJECT token" test finds
   nothing. Affects `counters-target-spell`,
   `activated-counters-target-spell`, `-unless-pays`.
2. **Left type-binding must take precedence over right object-adjacency.**
   `cast-trigger-self-plus1-counter-noncreature-spell` is noun sense (the
   card gains a +1/+1 counter when its controller casts a noncreature
   spell) but has a type word on the left AND an object on the right.
   Checking the object first returns verb, which is wrong.

With both corrections applied after the walk, the residual is expected to
be zero. ADD-08 stays blocked on §12a either way.

## 9. Cost-vs-effect law

Anchors: CR 113.3b ("[Cost]: [Effect]") and CR 601.2b (additional costs).
- `-cost-` / `-as-activation-cost` / `additional-cost-` slugs require the
  action LEFT of the colon or inside an "as an additional cost" clause.
- Life/sacrifice/discard occurring in resolution text NEVER satisfies a cost
  slug (b6 Fleshless Gladiator, b7 Fountain of Youth/Pick-a-Beeble class).
- "Free must be Free" (ratified b2) is a special case of this law.

## 10. Slug validator (Lane-1 lint, wire into emit + SUP)

A DET check every proposed slug must pass before entering the codebook or the
grammar lane. Pseudo-spec for `validate_slug.py`:
1. Charset: `^[a-z0-9]+(-[a-z0-9]+)*$`.
2. Banned tokens: `defender`, `countered`, bare `counter` as final noun
   without type, `free` unless the axis definition quotes a zero-cost,
   `creates` (post-D-2), `scaled` (post-D-3), `token` immediately adjacent to
   `counter` without the section-8 shapes.
3. Every hyphen-token must appear in the closed vocabularies (sections 2,
   4–8) or in the ratified glossary; unknown tokens → halt loudly (new
   vocabulary is a Captain ratification, not a typo).
4. Slot order check via greedy match against section 1.
5. Synonym collision check: normalized slug (stem verbs, strip connectives,
   sort scaling pairs) must be unique across the codebook — catches the
   token-count duplication class mechanically.
6. Restriction-family, counter-law, and cost-law special checks.
Validator failures are never auto-fixed; they surface for ruling.

## 11. Grammar instantiation mechanics (wiring, per CORPUS-PASS-PLAN §11.2)

- Ratified grammars live in `docs/grammars.json`: stem + ordered facet slots +
  closed per-slot vocab + CR anchor + instantiation examples.
- A virtual node instantiates the moment one quote-verified member arrives —
  no fresh ratification (the grammar was ratified). The b7 Brandywine Farmer
  case is the model: `leaves-battlefield-create-token-food` should have
  self-instantiated. SUP and emit both gain this behavior; SUP ledger-flagging
  a grammar-composable home is now a protocol error.
- SYNTH labeling: `lane=codebook-grammar` for grammar-composed slugs;
  validator runs on every one; anything neither exact-codebook nor
  grammar-valid stays `lane=free`.
- Seeded grammar families (already ratified across b5–b7): create-token-<type>;
  etb-create-token-<type>; leaves-battlefield-trigger-create-token-<type>;
  targeted-<action>-<class>; activated-tap-or-untap-<scope>;
  draw-second/cast-second prefix scheme; activation-restriction family (§3);
  grants-<keyword> facet scheme (T1 tension still parked for schema pass —
  grammar defines the NAMES, the b1-Q1 engine question stays open).

## 12. Migration ledger (the walk's worklist — logged, executed AT the walk)

Known non-conforming axes as of v0.7-pending (worked examples, not
exhaustive; the walk validates all ~300):
- `scales-token-count-with-x` → MERGE into `token-count-scales-with-x` (dup).
- `creates-token-with-x-scaled-counters` → `create-token-with-x-counters`.
- All `-scaled-by-` slugs → `-scales-with-` (D-3).
- `combat-damage-triggers-loot/-discard/-treasure/-proliferate` →
  `combat-damage-to-player-*` or `-to-creature-*` per member evidence.
- `attack-trigger-damage-defender` → three-way split (b7 §12 pending).
- `death-trigger-card-draw` → reuse original slug `death-trigger-draw-card`
  (registry continuity) — then family-normalize per D-1.
- ~~`counter-removal-as-activation-cost` → keep (verb-adjacent but shielded by
  `-removal-`); revisit under section-8 rule 1 at the walk.~~ **SUPERSEDED
  by the CDR-09 walk below.**

### 12a. CDR-09 counter-homograph walk (Captain-ratified 2026-08-02) — **EXECUTED 2026-08-02**

> **EXECUTED.** All 16 renames applied name-only; codebook sha256
> `61af1a1d7f81504f422feb4d…` → `d0b1183fc155f13e7b1ae025…`. 307 active axes
> before and after. The 33/16/17 partition below was re-derived from live state
> and confirmed **set-identical**, not merely equal in count. Counter-bearing
> active axes now measure **0 non-conforming**. Full record, the applied target
> strings, and two residual items the walk does not touch:
> `docs/CDR-09-WALK-DERIVATION-2026-08-02.md`.
>
> Note for anyone re-running the conformance check: §8a is **not** the only
> ratified law governing a counter token. §7's scaling standard
> (`own-counters`, `charge-counters`, and the verbatim
> `create-token-with-x-counters`), batch-5's polarity-is-a-parameter ruling,
> and batch-5 D12 each govern specific slugs. A checker that knows only §8a
> reports all of them as defects — it did, and two of those false positives
> would have destroyed ratified names. `foundry_cdr09_derive.py` encodes each
> with its citation.

Measured live against codebook v0.7 this session, classified against each
axis's own ratified DEFINITION (not by name-guessing). **33 active axes
carry a counter token; 16 are non-conforming.** Members and definitions are
unchanged by every row below — these are name-only.

Correcting `CDR-PROPOSALS.md` rev 2, which stated 34 axes and "~15 renames
(3 verb-side, 9 noun-side)". Live measurement: **33 axes, 16 renames —
3 verb-side, 10 noun-side, 3 `any-`.** The noun count was off by one and
the axis count by one. Third arithmetic drift caught in rev 2; see ADD-06.

**Verb-side (3)** — singular `counter` in verb sense, banned by 8a rule 1:

| from | to |
|---|---|
| `rule:activated-counter-target-spell` | `rule:activated-counters-target-spell` |
| `rule:activated-tax-counter-unless-pays` | `rule:activated-counters-target-spell-unless-pays` |
| `rule:tax-or-counter-spell` | `rule:counters-spell-unless-pays` |

Note: those last two plus `rule:activated-counter-target-spell` are also a
near-duplicate cluster differing only in delivery — resolve together, see
CDR-05.

**Noun-side, gain `plus1-` (10)** — every one of these definitions says
+1/+1 explicitly, verified this session:

`activated-counter-transfer-from-other-creature` ·
`attack-trigger-buff-other-attacker-counters` ·
`attack-trigger-self-counter-growth` ·
`cast-trigger-self-counter-noncreature-spell` ·
`death-trigger-counter-transfer` · `draw-trigger-self-counter-growth` ·
`etb-counter-on-other-creature` · `lifegain-triggered-counter` ·
`mass-counter-distribution` · `self-counter-growth`

**Type-agnostic, gain `any-` (3)** — definitions confirm each genuinely
spans every counter type:

| from | to |
|---|---|
| `rule:doubles-counter-placement` | `rule:doubles-any-counter-placement` |
| `rule:cleanup-counters-on-leaving-battlefield` | `rule:cleanup-any-counters-on-leaving-battlefield` |
| `rule:counter-removal-as-activation-cost` | `rule:any-counter-removal-as-activation-cost` |

**Already conforming, no action (17):** 3 verb (`counters-target-spell`,
`counters-noncreature-spell`, `counters-spell-or-ability-targeting-your-permanent`)
+ 14 noun (typed or `with`-bound).

Execution is a codebook mutation and rides the walk as its own step, under
the backup law with determinism ×2 — **not executed here**, per the
ratified "no midflight renames" standing rule.
- `untaps-target-land`, `activated-untap-target-creature`,
  `activated-untap-another-permanent`, `activated-tap-target-creature`,
  tap-or-untap pair, mass-untap pair → normalize onto
  `activated-(un)tap[-or-untap]-<scope>-<class>` lattice; consolidation flag
  already ledgered (b6 D3).
- `cannot-block-restriction` vs `cant-be-*`: pick `cant` (matches oracle
  "can't") — walk item.
- `compensates-controller-with-token`, `cheat-creature-into-play`,
  `rhystic-tax`, `the-ring-tempts-you`: idiomatic job-names, EXEMPT as leaves
  (jobs are parent/display vocabulary; grammar governs mechanism slugs) —
  exemption list is Captain-ratified per slug at the walk.
- **Q6 (walk-ratification 2026-07-31):** 7 further idiomatic-leaf exemptions
  ratified, joining the 4 above: `burst-draw`, `cantrip`, `modal`,
  `drain-life`, `combat-trick-pump-own-creature`, `tribal-anthem-buff`,
  `alternate-win-condition`.

## 13. Ratification record (2026-07-30)

All five decisions ratified per recommendation, Captain-explicit:
- **D-1:** `death-trigger-` stays the family word (no `dies-` slugs).
- **D-2:** bare verb stems; `counters-` verb form retained (section 8).
- **D-3:** `-scales-with-` is the sole scaling connective; `-scaled-by-`
  retires at the walk.
- **D-4:** the §3 activation-restriction enumeration is DET-owned; SYNTH is
  banned from assigning that family.
- **D-5:** banned-token list (§10.2) and per-slug idiomatic-leaf exemption
  mechanism (§12) ratified.
Registry: log this document as a ratified ruling set; changes require the same
explicit-reversal discipline as scoring constants (D6-style logging).

## 14. Walk-ratification vocabulary batch (2026-07-31)

Applied per `docs/WALK-RATIFICATION-EXECUTION-HANDOFF.md` section 2 (Q2, Q3,
F3, Q5, F4, Q6, Q8.5); see that document for the full ruling text.

- **Q5 extended structural/descriptive vocabulary** (the ~40-most-common-token
  proposal from `docs/archive/CORPUS-PASS-WALK-RATIFICATION.md` §2.2.2, ratified as
  EXACTLY the named list — the "and similar" backlog remainder is logged to
  the final naming audit, not silently expanded here):
  `creatures`, `other`, `on`, `from`, `library`, `triggers`, `ability`, `and`,
  `by`, `prevents`, `unblockable`, `buff`, `tapped`, `restriction`, `top`,
  `targets`, `doubles`, `energy`, `forces`, `controller`, `prevent`, `into`,
  `growth`, `tribal`, `effect`, `choose`, `enters`, `cards`, `threshold`,
  `recursion`. Explicitly EXCLUDED despite corpus frequency (each has its own
  open reason, logged to the naming audit rather than silently passed):
  `scaled` (banned, D-3), `a`/`the` (banned articles, §1), `targeted` (the
  `targeted-<action>-<class>` grammar family needs a membership check first,
  §2.5 of the walk doc), `lifegain` (synonym-collision candidate against the
  ratified `gain-life` EFFECT verb, design goal #1), `attackers`, `of`,
  `outlet`.
- **F4 soft-warning tier:** `and` is ratified vocabulary (closed-vocab check
  passes) but slugs containing it get a non-blocking VALIDATOR WARNING
  ("grab-bag smell") rather than a silent clean pass — see
  `validate_slug.py`'s `warnings` field.
- **Q8.5 `cant-be-blocked` compound stem token** ratified into vocabulary
  (tokens `cant`, `be`, `blocked`) for the new `cant-be-blocked-<restriction>`
  grammar family (§2.4 of the execution handoff). The `countered` ban (§10.2)
  is unaffected — `rule:cant-be-countered` renames to `rule:spell-uncounterable`
  (Q4, §4 above) rather than sharing this stem. Closed restriction vocab:
  `by-color`, `by-power`, `except-by-count`, `as-long-as-<state>`, and
  **`by-controller`** (B1 ruling, 2026-07-31, post-execution follow-on —
  names WHO may not block, not what the blocker is like; instantiated by
  `rule:cant-be-blocked-by-controller`, seeded by The Black Gate, moved out
  of `rule:grants-unblockable-target` per the terminology law's restriction-
  rider rule).
