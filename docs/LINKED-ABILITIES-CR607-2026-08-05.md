# READING PAST PUNCTUATION — ONE PARAGRAPH, SEVERAL ABILITIES (2026-08-05)

**Captain: *"portions are separated by punctuation. but cards can have multiple
effects that are separated by punctuation. we must account for that."***

**37 ability lines carry a second (and in one case a third) ability that the
one-delivery-per-line model could not see.** Now split, with **zero
regressions** and zero lines lost.

The claim is right, and the CR draws the boundary far more precisely than "split
on punctuation" — which is why the first cut of this fired on **137** lines and
the correct one fires on **37**.

---

## 1. CR 113.2c — a PERIOD is not an ability boundary; a PARAGRAPH is

> **CR 113.2c** — *"An object may have multiple abilities. If the object is
> represented by a card, then aside from certain defined abilities that may be
> strung together on a single line (see rule 702), **each PARAGRAPH BREAK in a
> card's text marks a separate ability**."*

So `ability_lines`, which splits on newlines, is **right** that one line is one
paragraph — and a period inside a line is **not** automatically a second
ability. A blanket split on punctuation would have been wrong.

**But a paragraph may still hold more than one ability, and the CR says so
outright:**

> **CR 603.11** — *"Some objects have a **static ability that's LINKED to one or
> more TRIGGERED abilities**. These objects combine the abilities into **one
> paragraph**, with the static ability first, followed by each triggered
> ability that's linked to it."*
> **CR 607.2h** — the same rule from the linkage side.

## 2. CR 603.12 IS THE DISCRIMINATOR, and it is why this is not a blanket split

Measured first: **516 lines** have a later sentence opening `When` / `Whenever` /
`At the beginning`. Splitting all of them would have been wrong on **479**.

> **CR 603.12** — *"A **RESOLVING** spell or ability may allow or instruct a
> player to take an action and **CREATE a triggered ability** that triggers
> 'when [a player] [does or doesn't]' take that action… These **reflexive
> triggered abilities follow the rules for delayed triggered abilities**."*

A reflexive trigger is **created**, and §2's created-ability rule plus §2d (both
Captain-ratified) give a created ability's delivery to its **creator**. CR
603.12's own example — Heart-Piercer Manticore, *"When this creature enters, you
may sacrifice another creature. **When you do**, …"* — is an `etb` card, and one
delivery is the correct answer for it.

**A static ability does not resolve.** So the cut is:

| first ability in the paragraph | later trigger is | deliveries |
|---|---|--:|
| spell / activated / triggered / loyalty — it **RESOLVES** | CR 603.12 **reflexive**, or CR 603.7a **delayed** — created | **1** |
| **STATIC** | CR 607.2h **linked**, a separate ability the object HAS | **2+** |

**CR 701.43d names the shape outright**, which is what makes this a derivation
rather than a judgement:

> *"'You may exert [this creature] as it attacks' is an optional cost to attack.
> Some objects with **this static ability** have a **triggered ability** that
> triggers 'when you do' **printed in the same paragraph**. These abilities are
> **linked**. (See rule 607.2h.)"*

## 3. The population — 37 lines, 24 of them exert

| shape | n | example |
|---|--:|---|
| **exert** (CR 701.43d) | 24 | Nef-Crop Entangler, Glorybringer, Watchful Naga |
| **reveal-your-draw statics** | 5 | **Keranos, God of Storms** — one static, **TWO** linked triggers, so a paragraph can hold **three** abilities. Also God-Eternal Kefnet, Primitive Etchings, Rowen, Inquisitor Eisenhorn |
| **prevention statics + linked trigger** | 3 | Magma Pummeler, Outfitted Jouster, Phyrexian Vindicator |
| other statics | 5 | Galea Kindler of Hope (→ `cast-trigger`), Mystic Doom Sandwich (→ `blocks-or-becomes-blocked-trigger`), Pharika's Spawn (→ `any-etb`), Predatory Sludge (→ `any-death-trigger`) |

4 of the 37 second-abilities land on a **ratified** token immediately; the other
33 are reported under `linked:<descriptor>` — visible for the first time instead
of silently absent.

## 4. THE FALSE POSITIVES, and each one's own CR rule

The first cut fired on 137 lines. Every exclusion below is a CR rule, not a
tweak.

### 4a. 95 spell abilities — CR 113.3a again

`spell-or-static` is reached by an instant's line too, and a trigger in **its**
later sentence is a **delayed** trigger created during resolution (CR 603.7a),
belonging to the spell (§2d). The same CR 113.3a cut that carried the
self-statement pass applies here: **a spell ability exists only on an instant or
sorcery.** 137 → 42.

### 4b. "Reached spell-or-static" ≠ "is static" — 5 lines

The proxy fails exactly when the first ability is a trigger that went unrouted
for an **unrelated** reason:

```
Ace, Fearless Rebel   Nitro-9 — Whenever Ace attacks, ...
Spider-Man            No One Dies! — When Spider-Man enters, ...
```

`ABILITY_WORD` accepts only `[A-Za-z'’\- ]`, so a prefix carrying a **digit**
("Nitro-9") or **punctuation** ("No One Dies!") is never stripped, the line
never reaches its trigger branch, and it arrives looking static. Their "When you
do" is then exactly the CR 603.12 reflexive case. **The first sentence must be
positively static** — it must not open a trigger and must carry no activation
colon (CR 113.3b).

**And the prefix must be stripped BEFORE the sentence split, not after** —
`No One Dies!` ends in "!", so the splitter cut the *prefix* into its own
sentence and hid the trigger in sentence two.

### 4c. Attractions — CR 702.159a

> *"'**Visit — [Effect]**' means '**Whenever** you roll to visit your
> Attractions, … [effect].'"*

So a `Visit —` paragraph's first ability is **triggered**, and a later trigger
in it is delayed. 702.159b puts `Prize —` inside that same visit ability.
Swinging Ship and Storybook Ride. This is the **b7 Pick-a-Beeble ruling**
(*"an Attraction's Visit/Prize are triggered, not activated"*) reaching a second
classifier.

### 4d. Die-roll result tables — CR 706.3b

> *"An instruction to roll one or more dice, any instructions to modify that
> roll printed in the same paragraph, any additional instructions based on the
> result of the roll, and the associated results table are **all part of one
> ability**."*

The Deck of Many Things: `20 | Put a creature card … When that creature dies, …`

### 4e. Quoted created abilities — §2

A granted ability carries its own periods:

```
Spare Dagger   Equipped creature gets +1/+0 and has "Whenever this creature
               attacks, you may sacrifice Spare Dagger. When you do, ..."
```

`sentence_spans` blanks punctuation inside quoted spans before splitting, so a
granted ability's sentences are never handed to the card. 3 of the 45.

## 5. THE COMMA LOGIC — `trigger_condition()`, from earlier this session

The condition side of the same problem, and the project had been bitten from
**both** directions:

| | failure |
|---|---|
| too **EARLY** | `split(",")[0]` truncates an enumeration — *"one or more Scouts, Pirates, **and/or** Rogues you control deal combat damage"* loses its own verb |
| too **LATE** | `trigger_clause` walks past a condition whose verb is unlisted — Heart of Bogardan's *"doesn't **pay** … cumulative upkeep, this enchantment **deals** X damage"* moved off `upkeep-trigger` |

**The cut needs no verb list**, which is why it survives a verb the CR does not
enumerate: CR 113.3c gives the template `[condition], [effect]`, and English
gives the boundary — an enumeration closes with a coordinating conjunction on
its final element, so a comma is a list separator exactly while some **later**
segment still opens with `and` / `or` / `and/or`. **Periods end it
unconditionally**: a trigger condition never spans sentences.

## 6. RESULT

| | before | after |
|---|--:|--:|
| lines carrying a second ability | 0 (invisible) | **37** |
| deliveries emitted | 61,907 | **61,945** (+38 — Keranos contributes 2) |
| second abilities on a **ratified** token | — | **4** |
| second abilities reported under `linked:` | — | **33** |
| regressions (ratified → None) | — | **0** |
| lines lost / appeared | — | **0 / 0** |

## 7. Verification

| gate | result |
|---|---|
| routing diff `--strict` | **0 regressions**; the harness correctly flagged `ROW COUNT CHANGED` and fell back to a key-based diff — the pass **does** alter how lines are produced, and the guard said so |
| all 42 candidates read individually | **yes** — 5 false positives found by reading, each traced to its own CR rule (§4b–4d) |
| determinism ×2 | **byte-identical** |
| name-invariance | **1** — the known Storm of Memories artifact |
| Clue/investigate ground truth | **unchanged** from the previous pass |
| lint · family sweep · drift | clean · 6 blocking, the same 6 · 35 unchanged |

## 8. WHAT THIS PASS PROVES

**"Split on punctuation" was right as an instinct and wrong as an
implementation, by a factor of 3.7.** 137 lines on the first cut, 37 correct.
Every one of the 100 exclusions is a CR rule — 113.3a, 603.12, 702.159a, 706.3b
— and not one of them is a heuristic. **The CR does not just permit the
distinction, it names every case.**

**A paragraph can hold three abilities.** Keranos, God of Storms is one static
followed by two linked triggers. Any model that assumes "one line, one delivery"
or even "one line, at most two" is wrong on the corpus as printed.

**The row-count guard earned its keep.** This is the first pass in the series to
change *how many* deliveries exist rather than only *which* ones, and the
harness detected it and switched diff strategies unprompted. A pass that changes
row counts silently would make every family pin meaningless.
