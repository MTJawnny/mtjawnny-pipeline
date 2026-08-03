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
- **QUALIFIER** — closed modifiers: `-conditional`, `-mass` (see 6),
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
| `delayed` | delayed triggered ability created on resolution | 603.7 |
| `kicker` | kicked-conditional bonus | 601.2b |
| `death-trigger` | triggered, graveyard from battlefield | 700.4 |
| `becomes-targeted-trigger` | triggered, "becomes the target of a spell or ability" (Ward's family; walk-ratification Q2, 2026-07-31) | 702.21a |
| `becomes-tapped-trigger` | triggered on the STATE CHANGE untapped→tapped. Captain-ratified 2026-08-03. *"doesn't trigger if the permanent enters the battlefield in that state"* — so it is neither `enters-tapped` (a replacement, CR 614) nor a tapped-state check | 603.2e |
| `becomes-untapped-trigger` | triggered on the state change tapped→untapped (the `Inspired` family — an ability WORD, CR 207.2c, with no rules meaning, so the axis takes the printed trigger) | 603.2e |
| `tapped-for-mana-trigger` | triggered *"whenever such a **mana ability resolves and produces mana**"* — strictly NARROWER than becoming tapped: tapping for a non-mana cost fires `becomes-tapped-trigger` and NOT this. Not a synonym | 106.12a |
| `cycled-trigger` | triggered when the card is cycled. CR 702.29c: *"'When you cycle this card' means 'When you **discard this card to pay an activation cost of a cycling ability**'"* — so it fires on paying the COST, and still fires if the draw is replaced or prevented | 702.29c |
| `cycle-or-discard-trigger` | the CR's own named shape, *"whenever a player 'cycles or discards' a card"*, which **fires only ONCE when a card is cycled** — a real distinction from a naive "cycle OR discard" reading | 702.29d |
| `chapter-trigger` | a Saga chapter ability. CR 714.2: *"A chapter symbol is a **keyword ability** that represents a **triggered ability** referred to as a chapter ability."* 714.2b gives the templated text: *"When one or more lore counters are put onto this Saga, if the number … was less than N and became at least N, [effect]."* Captain-ratified 2026-08-03. **N is a PARAMETER** — the final chapter's sacrifice is a STATE-BASED action (714.4), not part of the ability. `-conditional` is deliberately NOT marked: 714.2b makes the intervening-if definitional, so it would tag 100% of members and distinguish nothing. The Saga *progression* is a TURN-BASED ACTION (714.3c) and is not an ability — `rule:saga-chapter-progression` stays KILLED per `TRIAGE-BATCH-1.md` §1c. **Class level bars are NOT this**: CR 716.2 makes them activated + static, and they already take `activated` | 714.2, 714.2b |
| `blocks-or-becomes-blocked-trigger` | triggered, a blocking/being-blocked event (Bushido/Flanking/Rampage/Afflict shape; walk-ratification Q2, 2026-07-31) | 509 |

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
  (`loyalty`, `delayed`, …), never to the created one. Garruk, Caller of Beasts
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
plurality), `-conditional` (an intervening-if or "unless" gate on the same
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
