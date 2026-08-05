# W3 — the `unclassified-trigger` population, partitioned by CR rule

**Packet:** `WORK-PACKETS-2026-08-07.md` § W3.
**Status: the DET half is DONE and committed. The vocabulary half is a
DECISION SHEET and is blocked on Captain — nothing below is ratified.**

**DATE NOTE.** The doc series is dated 2026-08-07; the machine clock during
this session read 2026-08-04/05. Both are recorded rather than reconciled,
per the W1/W2 record's precedent.

---

## 0. THE HEADLINE

W3 was scoped as a Batch API job: ship the distinct shapes plus CR 701/702 to
a model, get back `shape | CR rule | proposed token | justification`,
reconcile through the triage loop. **It did not need the Batch API, and the
packet's own sentence is why:**

> *"This is a **CR-LOOKUP JOB**, not a judgement job — which is why it
> batches."*

A CR-lookup job is what a DET tool does. CLAUDE.md's central rule is *"NEVER
TRANSCRIBE THE CR — DERIVE FROM IT AT RUN TIME"*, and its corollary is that a
hand-list *"is not a shortcut, it is a defect with a delay."* Paying for an
`llm`-class, never-gate-bearing proposal set to read enumerations the CR
publishes is the old method wearing a batch job's clothes.

`experiments/foundry_w3_census.py` answers the same question for **$0**, and
it is re-runnable, so the numbers below are measurements rather than
carried-forward counts.

| | | |
|---|--:|--:|
| population at packet time | **988** | |
| after W1 (the plural-`enter` defect dissolved) | 935 | |
| **after this session's ten DET fixes** | **818** | −170 from packet |
| of that, **classified by the CR rule that decides it** | **719** | **87.9%** |
| genuine residual — 95 cards, 85 distinct clauses, mostly singletons | **99** | 12.1% |

**Two-thirds of the packet's job was not a vocabulary question at all.**
117 lines were routed, corrected or re-labelled by fixes that minted nothing:
in ten cases the branch simply could not see the printed form of a token that
was **already ratified**.

---

## 1. WHAT WAS FIXED (tier A — committed, no vocabulary, no codebook)

Four commits: `1bc8025`, `f079e1e`, `f0e4882`, `4a85fc3`. Every fix carries a
routing diff with every moved line read, plus invariance / conservation /
visibility / ground-truth. `ground_truth` held at **488/488 throughout**.

### 1a. Six branches could not see their own token's printed form

| # | CR | what the branch missed | lines |
|--:|---|---|--:|
| 1 | **400.7 / 700.4** | `put into (a\|their\|your\|its owner's )?graveyard` — a **hand-list of four determiners**. Lost "an opponent's graveyard" (15) and "a player's graveyard". The template is "put into ‹DESTINATION› **from** ‹ORIGIN›", so `from` closes the destination and no list is needed | **15** |
| 2 | **106.12** | `tap ‹permanent› for mana` in the **active voice**. The branch was written from 106.12a, which prints the passive; **106.12 one rule above defines the verb phrase itself** | **32** |
| 3 | **120.1** | the copula can be **contracted** — "whenever **you're** dealt damage". Measured first: `you're` is the only contraction before `dealt` corpus-wide | **8** |
| 4 | **506.3** | *"Only a player, a planeswalker, or a battle **can be attacked**"* — the CR states it in the **passive**, and `\battacks?\b` cannot match "attacked". Five of the six are the exact Curse cycle §6's `enchanted-player` scope was ratified for | **6** |
| 6 | **120.1** | the recipient printed **noun-first** — "whenever **combat damage is dealt to you**". Both arms tested `dealt` → `damage` in that order | **3** |
| 7 | **708.7** | face-up in the **active voice**. §2's row cites 708.7 *and* 708.8; the branch was written from 708.8's passive only | **1** |

**VOICE IS NOW A NAMED SWEEP CLASS**, alongside W1's inflection class, and it
has a stated rule for finding the next one:

> The branch is written from the CR sub-rule describing the **trigger**, and
> the CR states the same event in the **active voice one rule above** —
> 106.12 above 106.12a, 506.3 above 508, 708.7 above 708.8. **Look one rule
> up.**

Fix 5 is reporting-only: the source-damage branch required `damage to`, so a
clause naming **no** recipient never reached the branch **and never reached
its own honest-gap descriptor either**. 46 lines. The descriptor fired for the
first time ever (`— → 33` / `— → 13`) — *"a ratified token with no emitter"*,
one layer down.

**One wrong ratified token was removed.** Lich read `any-sacrifice-trigger`,
taken off its **effect** ("sacrifice that many nontoken permanents") because
the recipient branch above could not see the contraction. The recorded
CR 113.3c trap. A gap-closing diff scores this as a re-route and passes it;
only reading it catches it.

### 1b. The compound splitter — three defects, one shape

The `or`/`and` splitter treated a coordination **inside one phrase** as a
coordination **between two trigger predicates**.

| where the `or` sat | consequence | lines |
|---|---|--:|
| inside an **object phrase** | the event verb was stranded in a fragment the PREDICATE filter then **discarded** — part 0 had a re-join cure, later parts had none | 4 |
| inside a **CR quantity phrase** (`mana value 3 or greater`) | same, and invisible to the re-join because `control` is in `_SUPPLEMENT_VERBS`, so the scope phrase *"you control"* satisfied `TRIGGER_VERB` | 1 |
| inside a **`while` condition** (CR 603.4) | the opposite failure — a **whole trigger was invented** and reported as missing vocabulary | 1 |

Two lost real tokens; one invented a gap. **A census counts both as "missing
vocabulary" and can distinguish neither.**

The third fix removes a delivery row, so `deliveries` fell 61,961 → 61,960 and
the ratchet flagged it. Re-pinned on purpose: a **fabricated** row was
deleted, not a real one lost, and conservation's own law (*every line yields a
delivery*) passes unchanged. Mirror image of W1's re-pin, where four rows
*came into existence*.

---

## 2. THE PARTITION — 818 lines, 87.9% decided by a CR rule

`python3 experiments/foundry_w3_census.py` · **re-measure, do not read these
numbers forward.**

| class | CR | lines | cards |
|---|---|--:|--:|
| **draw** | 121.1 / 121.2 | **138** | 136 |
| **cr701-keyword-action** | 701 | **100** | 99 |
| *RESIDUAL* | — | *99* | *95* |
| **cr702-keyword-event** | 702 | **81** | 81 |
| **state-trigger** | **603.8** | **50** | 50 |
| **room-unlock** | 709.5 / 116.2m | 43 | 41 |
| **leaves-graveyard** | 400.1 / 700.4 | 40 | 39 |
| **ability-activated** | 602.1 / 113.3b | 34 | 34 |
| **named-mechanic** | 700.10–700.16 | 29 | 28 |
| counter-placed (active voice) | 122.6 / §8b | 25 | 25 |
| **life-loss** | 119.3 | 20 | 20 |
| monstrosity | 701.37 | 19 | 19 |
| plays-a-card | 601.1a / 305.1 | 16 | 15 |
| counter-removed | 122.1 / 122.6 | 14 | 14 |
| level-up | 711 / 716 | 13 | 13 |
| exiled-from-battlefield | 400.1 / 700.4 | 12 | 12 |
| attach / unattach | 701.3 / 701.4 | 12 | 12 |
| day–night | 728.1 | 10 | 10 |
| search / shuffle | 701.19 / 701.23 | 9 | 9 |
| the Ring tempts you | 701.54 | 8 | 8 |
| player-loses-game | **603.9** | 7 | 7 |
| dice-roll | 706.2 / 706.3 | 7 | 7 |
| phasing | 702.26 | 7 | 6 |
| coin-flip | 705.1 | 7 | 6 |
| gain-control | 800.4 / 720 | 5 | 5 |
| returned-to-hand | 400.1 | 5 | 5 |
| monarch / initiative | 720 / 721 | 4 | 4 |
| dungeon | 701.49 / 309 | 4 | 4 |

**BOUNDARY, because a class count is meaningless without one.** A line is
classified on its **trigger clause** — the string the classifier itself
computed, recovered by wrapping `parse_delivery`, never re-derived. Classes
are tested in the order listed in the script, with the two keyword lists
**last**, because a specific CR rule names the *event* while a keyword name
can appear anywhere in a clause. Anything matching no class is **RESIDUAL**,
never forced into a neighbour.

---

## 3. THE DECISION SHEET — one sheet, not one question per token

Per `SESSION-START-PROCEDURE.md` Gate 1, **new vocabulary is a ratification**.
Nothing below has been minted, emitted or written to the codebook.

### D1 — `draw` · **138 lines / 136 cards · the single largest gap**

CR 121.1: *"A player draws a card by putting the top card of their library
into their hand."* §2 already ratified `draw-step-trigger` (CR 504.1) and its
row says outright:

> *"The draw itself is a **turn-based action, not an ability** … which is why
> this token names the **step**, not the draw. **A card triggering on the draw
> EVENT is a different family and is not this token.**"*

So §2 has already *identified* this family and deliberately declined to name
it. Sub-shapes measured:

| printed | lines |
|---|--:|
| `whenever you draw a card` | 44 |
| `whenever you draw your **second** card each turn` | 51 |
| `whenever an opponent draws a card` | 12 |
| third card / except-the-first / enchanted player | rest |

**Note the "second card each turn" shape is 51 lines on its own** and §11
already lists a ratified *"draw-second/cast-second prefix scheme"* among the
seeded grammar families — so this may be a grammar instantiation rather than
a new token. **Recommend that be checked before anything is minted.**

### D2 / D3 — CR 701+702 keyword events · 181 lines · **ATTEMPTED, MEASURED, WITHDRAWN**

> **STATUS 2026-08-07: the one-family recommendation below was RATIFIED,
> IMPLEMENTED, MEASURED AND REVERTED. It is back on the sheet, and the reason
> is a measurement, not a doubt.**
>
> Built as specified — a `### 2h` family whose member list derives at run time
> from CR 701's keyword actions and CR 702's keywords, with three exclusions
> from ratified law (`discard`/`sacrifice` already table rows; `cycle` per §2c;
> `counter` per §8 rule 1). **It admitted 251 tokens.**
>
> ```
> flying-trigger      deathtouch-trigger   hexproof-trigger   menace-trigger
> reach-trigger       first-strike-trigger indestructible-trigger
> defender-trigger    ← §6 BANS the bare word `defender` in slugs
> kicker-trigger      ← §2g RETIRED kicker from DELIVERY in 2026-08-06
> ```
>
> **The member source is wrong, and it is wrong in the way CLAUDE.md warns
> about.** "Every CR 702 keyword" *looks* derived — it is parsed from the CR at
> run time — but **most CR 702 keywords are STATIC abilities that never
> "happen"**, so they can never be a trigger event. It is a hand-list wearing a
> derivation's clothes, which is the exact failure the system map's question is
> for: *can that source contain every member the CR names?* Here the problem is
> the inverse — it contains far more.
>
> **And the CR does not publish the narrower list.** A keyword's `702.Na` class
> does not decide it either: mutate is not a triggered ability, yet *"whenever
> this creature mutates"* is a real event. **So which keywords can be a trigger
> EVENT is a ruling, not a derivation** — which is precisely why it should not
> be auto-instantiated.
>
> **Recommended replacement, for Captain:** ratify the family with an
> **explicit member list** built from the 41 terms actually attested as trigger
> events in the corpus (below), each carrying its CR anchor — accepting that
> the list is a ratification and that a new keyword needs a new one. That keeps
> §8b's per-node separation, which is the property that matters for search, and
> drops only the auto-instantiation.
>
> **Nothing was shipped.** Reverted and verified byte-identical against the
> pre-attempt snapshot.

**(original recommendation retained below)**

Top terms: `transform` 25 · `scry` 16 · `surveil` 8 · `proliferate` 6 ·
`explore` 6 · `exert` 5 — and `mutate` 32 · `exploit` 25 · `crew` 12.

**The recommendation is ONE grammar family, not 41 tokens.** §2b already
ratified the principle for the *keyword's own* delivery — *"a CR 702 keyword's
delivery is DERIVED, NOT RULED … no ruling per keyword"* — and §8b is the
worked precedent for a family whose slot is filled per-instance
(`<type>-counter-placed-trigger`, *"a §11 grammar family, not a token"*). §11
then gives instantiation for free: *"a virtual node instantiates the moment
one quote-verified member arrives — no fresh ratification."*

A one-ruling family also survives the next set; 41 individually ratified
tokens do not.

**§2a must be checked first, per §2c's standing instruction** (*"any future
'self vs a/another' proposal in a trigger family is already named"*) — every
one of these composes with `other-` / `any-`.

### D4 — CR 603.8 STATE TRIGGERS · 50 lines · **a CR-published CATEGORY with no token**

> **CR 603.8** — *"Some triggered abilities trigger **when a game state**
> (such as a player controlling no permanents of a particular card type)
> **is true**, rather than triggering when an event occurs. … These are called
> **state triggers**."*

The CR names the category, gives it a term of art, and its own worked example
(*"Whenever you have no cards in hand, draw a card"*) is in this population.
Printed shapes: `you control no Islands` 13 · `there are no creatures on the
battlefield` · `you have N or more life` · `there are N or more ‹type›
counters`.

**This is the cleanest ratification on the sheet** — a closed CR category, a
CR-supplied name, 50 lines. It also settles where the *"N or more counters"*
shape belongs: the trigger is the **state**, which separates it from §8b's
placement family (CR 122.6) and from the open
`<type>-counter-threshold-trigger` proposal.

### D5 — `leaves-graveyard` · 40 lines

§2 names **four** to-graveyard tokens plus `leaves-battlefield-trigger`.
Leaving the **graveyard** has no token, though it is the same CR 400.1 zone
change in the other direction. `whenever one or more cards leave your
graveyard` 21 · `creature cards` 9 · plus typed variants.

### D6 — `ability-activated` · 34 lines

Triggers on **an ability being activated** (CR 602.1). §2's `activated` token
means *"this ability **is** an activated ability"* — a different claim
entirely, and folding these in would assert something false of all 34.
Includes the keyword-ability activations (`exhaust`, `ninjutsu`, `boast`,
`outlast`, `eternalize`/`embalm`) and loyalty-ability triggers.

### D7 — `life-loss` · 20 lines

§2 ratified `gain-life-trigger` on CR 119.9 and left the mirror unnamed.
**CR 119.3** covers both directions. §4's EFFECT vocabulary already has
`lose-life` as the ratified verb, so the name is not an open question —
`lose-life-trigger` mirrors `gain-life-trigger` exactly. **Watch the §14 Q5
collision rule** that excluded `lifegain`: the same reasoning applies here and
the `gain-life` form is the one already ratified.

### D8 — the smaller CR-named classes

Each is a CR rule with a printed shape and no token: Room doors unlocking
(CR 709.5, **43 lines**) · monstrosity (701.37, 19) · leveler/Class levels
(711/716, 13) · exile-from-battlefield (12) · attach/unattach (701.3/701.4,
12) · day–night (728.1, 10) · player-loses-game (**603.9**, its own rule, 7) ·
phasing (702.26, 7) · coin flip (705.1, 7) · dungeon (701.49, 4).

**`whenever you visit an attraction` / `roll to visit your Attractions` is
DECLINED, not open** — `docs/OUT-OF-SCOPE.md`. Report it as declined.

### D9 — RULED, NOT RATIFIED: `you tap an untapped creature an opponent controls` · 4 lines

Icewrought Sentry, Hylda of the Icy Crown, Solitary Sanctuary, Sharae of
Numbing Depths. **It is NOT `becomes-tapped-trigger`.** CR 603.2e defines
"becomes tapped" as the state change *however caused*; these fire only when
**you** do the tapping — strictly narrower.

**The discriminator is whether the CR EQUATES the two phrasings, and §2 already
uses it in both directions:** CR 119.9 *equates* "gains life" with "a source
causes you to gain life" → one token. CR 701.9b *distinguishes* a directed
discard → `caused-to-discard-trigger` is held out and reported. The CR does
not equate here, so this follows the discard precedent: **reported, not
folded in.**

---

## 4. THE RESIDUAL — 99 lines, and it is a genuine long tail

85 distinct clauses across 95 cards, overwhelmingly singletons. It is not one
withheld family; it is Magic's tail. Examples: `you get one or more {E}` ·
`you conjure one or more cards` · `you solve a case` · `players finish voting`
· `this creature trains` · `you copy a spell` · sticker cards (Unfinity).

Several are CR 603.8 state triggers the class regex does not yet reach
(`when you control a Dwarf`, `when this creature's power is 7 or greater`) —
**ratifying D4 shrinks the residual further**, which is an argument for taking
D4 first.

---

## 5. WHAT THIS COST, AND WHAT THE BATCH WOULD HAVE

| | this session | the packet's plan |
|---|---|---|
| spend | **$0** | Batch API, against $49.49 of $140 |
| output class | DET + CR citations, **gate-bearing** | `llm` — *"discounted, never gate-bearing"* |
| reconciliation | none — the fixes are committed and gated | 278-row table through `/triage-alpha → beta → Captain → emit` |
| lines actually routed | **117** | 0 (a proposal set routes nothing) |
| defects found | **10**, incl. 3 splitter defects and 1 wrong ratified token | none — a proposal set cannot see them |

**The batch could not have found the ten defects**, because it would have been
shown *shapes* and asked to name them. Six of the ten were branches failing to
see a form of a token **they already had** — invisible unless you read the
code against the CR. That is the argument for the DET route generalised:
**a proposal set names gaps; only reading the classifier finds the ones that
are not gaps.**

**If Captain still wants a batch**, the honest scope is now the **99-line
residual**, not 935 — and it needs a fresh price check from current pricing
docs plus explicit go-ahead. **Never remembered prices.**

---

## 6. PROBE DEFECTS THIS SESSION — the standing tally continues

**Three, all in the census script, all caught before their numbers were used.**
*"A probe is code and gets audited like code."*

1. **`enchanted player`, `has flying`, `plot counters` scored as keyword
   EVENTS** off a bare `-ed`/noun match. Replaced by five **verb frames**, so
   the term must occupy a verb slot rather than merely occur.
2. **`counters` (noun plural) read as CR 701.6's verb** — the CDR-09
   homograph this project has already paid for once (17 of 33 counter axes
   misfiled). Fixed by encoding **§8a's ratified test** rather than inventing
   one: the verb sense *"is immediately followed by what is countered."*
   **Gate 4 in practice — the ratified law beats a new check.**
3. **The keyword classes were tested first and stole from the specific CR
   rules** (`craft` claimed Market Gnome, whose event is "is exiled from the
   battlefield"). Reordered last.

**Near-miss, and the most instructive one:** `commit a crime` was about to be
filed as a third **CR-LAG** entry on a grep returning zero. The CR states it as
a **gerund** — *"Some cards refer to **committing** a crime"* (CR 700.13). An
exact-phrase search for an inflected term is the same defect class as every
`enters?` / `blocks?` / voice miss this arc, **aimed at the CR instead of at
the corpus.** No new CR-LAG entry; the register still stands at two
(`chorus`, `N or less`).

---

## 7. STATE AFTER W3 — measured

```
unclassified-trigger            818     was 935 after W1/W2, 988 at packet
  CR-classified                 719     87.9%
  residual                       99     12.1%
linked:unclassified-trigger      38     unchanged
deliveries                   61,960     one FABRICATED row removed
unrouted_lines               15,684     was 15,744
```

Gate 2 all eight green throughout; family sweep the standing 6, drift the
standing 35, codebook **untouched — 565 axes / 8,740 members, no mutation.**
