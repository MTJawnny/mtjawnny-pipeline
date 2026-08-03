# DELIVERY VOCABULARY BATCH — DECISION PACKET (2026-08-03)

The batch `BECOMES-TAPPED-RULING-2026-08-03.md` §6 and
`END-STEP-TRIGGER-RULING-2026-08-03.md` §5 both asked for. Assembled at
Captain's direction: *"take the vocabulary batch."*

**Nothing here is ratified and no axis was authored.** New vocabulary is a
Captain ratification (§10.3). Every number was measured this session; none is
carried from a handoff.

**Zero API calls.** Two new DET tools, both zero-token, both determinism-×2
byte-identical.

---

## 0. How to rule this

Seven numbered questions, **Q1–Q7**. Q1 is the big one (1,558 cards) and the
other six are small or mechanical. Each carries a recommendation and the
evidence behind it. Annotate in place — your annotations are authoritative.

---

## 1. GATE 3 FINDING — `end-step-trigger` was already ruled, and the ruling was missed

`END-STEP-TRIGGER-RULING-2026-08-03.md` §0 states:

> Gate-3 dossier: `end-step-trigger`, `end-of-turn-trigger` — **no prior ruling,
> in any status.**

**That is wrong.** `rule:end-step-trigger` is in the codebook right now as
`status: killed, n=0`, and `TRIAGE-BATCH-1.md` §1c killed it by name:

> ### 1c. Procedural riders and templating boilerplate (7)
> Shared wording that carries no functional kinship — two cards sharing "then
> shuffle" are not kin.
> - **end-step-trigger** (timing boilerplate. NOTE: member Wilderness
>   Reclamation's quote "untap all lands you control" belongs to the untap
>   family)

The dossier prints `status killed · n=0` in its header and reports "0 carry a
RULING", because a KILL recorded in a bucket heading is not in its verdict
grammar. The status line was there to read.

### Does the kill govern the new proposal? **No — and the precedent is exact.**

Batch-1 killed an **axis**. This batch proposes **DELIVERY vocabulary**. The
distinction is not a dodge, because the mirror case settles it:

| | axis in codebook? | §2 vocabulary? |
|---|---|---|
| `upkeep-trigger` | **no** (dossier: NOT IN CODEBOOK) | **yes**, ratified |
| `end-step-trigger` | **yes, killed** as boilerplate | proposed here |

`upkeep-trigger` — the exact mirror — has been ratified §2 delivery vocabulary
all along and has never been an axis. Batch-1's reasoning ("shared wording
carries no functional kinship") is an argument against a bare delivery-only
**axis**, and it is *correct*: two cards that share only "at the beginning of
your end step" are not kin. The end-step ruling already concedes this — §3:
*"No axes authored — delivery-only slugs are parents."*

**Q1 is unaffected. But the record needs a line, so this is not re-derived a
third time:**

> **Q7 (mechanical).** Confirm: `end-step-trigger` is ratified as §2 DELIVERY
> vocabulary; the **killed axis stays killed**; batch-1 §1c is upheld, not
> reversed. Recommend **yes**.

---

## 2. THE NUMBERS ARE WRONG — corrected, with the boundary stated (Gate 4)

The batch's headline was **~2,700 cards** and self-vs-other's was **1,921**.
Measured this session, self-vs-other is **1,558**. The census overstated it by
**363 cards (18.9%)**, from three separate defects — none in the data, all in
the encoding.

| defect | cards | why |
|---|--:|---|
| census summed **per-family** counts | −52 | 51 cards sit in two families; the sum double-counts them. Distinct ≠ sum |
| **self-triggers read as other-triggers** | −265 | see below |
| **phase triggers read as event triggers** | −45 | see below |
| | **1,921 → 1,558** | |

### 2a. `this <noun>` — 170 lines

The extractor's self-reference test listed the nouns by hand:
`creature|permanent|artifact|enchantment|land|vehicle|card|aura|case|token`.

It missed **equipment (104) · siege (36) · spacecraft (16) · class (13) ·
door (1)**. So "When **this Equipment** enters" — an ETB on the source — was
counted as a trigger on *another* permanent.

**Fixed by derivation, not by extending the list**: the noun set is now built
from the corpus's own type lines at load time. That covers Equipment, Siege,
Spacecraft, Class, Saga, Room, Vehicle and Battle automatically, and it
correctly excludes "this **turn**", "this **combat**", "this **spell**" — which
never appear in a type line. A hand-written list would have missed the next
new permanent type too.

### 2b. Legendary short names and Alchemy prefixes — 133 lines

`canonicalize_self_reference` collapses a card's own name to `~`, and handled
the pre-comma short form ("Willie Lumpkin, Postman" → "Willie Lumpkin"). It did
**not** handle two other Oracle conventions:

- **subtitle without a comma** — Sharuum the Hegemon prints "When **Sharuum**
  enters"; Phage the Untouchable prints "When **Phage** enters"; Rosie Cotton
  of South Lane prints "When **Rosie Cotton** enters"
- **Alchemy `A-` prefix** — the card is named `A-Elderleaf Mentor`, the oracle
  text says "When **Elderleaf Mentor** enters"

Both were read as triggers on some other permanent.

This one is in **ratified** shared code (`foundry_common.py`, "DET preprocessing
standard v1, ratified 2026-07-31"), so it was treated carefully. The standard's
own words are *"the short pre-comma/pre-'//' form **actually used in ability
text**"* — the intent is every form the card uses for itself, so completing it
implements the ruling rather than amending it.

> **Q6 (mechanical).** Confirm the canonicalizer change is a bug fix under the
> existing standard, not an amendment to it. **Blast radius measured: zero** —
> lint clean, definition drift unchanged at 35 with an identical C-partition,
> family sweep unchanged at 232/6 blocking, `DEFINITION-DRIFT-AUDIT` regenerates
> byte-identical. Recommend **yes**.

### 2c. Phase triggers — 45 cards

Family detection scanned the **whole ability line** while self-vs-other was
decided on the **trigger clause**. So Legion Warboss —

> "At the beginning of combat on your turn, create a 1/1 red Goblin ... **that
> attacks** this combat if able"

— was filed as an *other-creature-attacks* trigger. The "attacks" is in the
effect. Also Mathas Fiend Seeker, Curious Obsession, Pest Rescuer, Mad Dog and
40 others.

This is **the same bug the census already recorded and fixed once** — its own
table lists *"self/other decided over the whole line, not the trigger clause"*.
It was fixed for the self/other test and left live for family selection.

Fixed: phase triggers are now claimed first, off the clause.

### 2d. Knock-on corrections to the census table

| row | census doc | measured now |
|---|--:|--:|
| ability lines scanned | 63,019 | **61,804** |
| other-permanent enters | 799 / 792 | **561 / 556** |
| other-creature dies | 451 / 448 | **439 / 436** |
| other-creature attacks | 416 / 413 | **348 / 345** |
| other-creature combat damage to player | 221 / 220 | **203 / 202** |
| other-permanent LTB | 48 / 48 | **43 / 43** |
| **end step** | 606 / 601 | **657 / 652** ⬆ |
| begin combat | 279 / 277 | **333 / 331** ⬆ |
| damage-received | 107 / 106 | **109 / 108** |
| lifegain-trigger | 104 / 102 | **98 / 96** |
| unclassified-trigger | 1,243 / 1,201 | **1,245 / 1,203** |
| to graveyard from anywhere | 233 / 233 | **224 / 224** |
| is attacked | 43 / 42 | **38 / 37** |
| draw step | 28 / 27 | **31 / 30** |

**End-step and begin-combat went UP**, because the 45 misfiled phase triggers
came home. Three further rows (marked in the last three) differed because the
census table was assembled across its own debugging session and predates the
final bug fix.

**This is the seventh instance of the standing lesson** (§S4 154→90→44 · C4f ·
Roles · investigate 132→163 · end-step 601→536 · census line-count · this).
`DELIVERY-GAP-CENSUS-2026-08-03.md` needs a ⚠ banner; not applied without your
say-so, since it is a ratified-adjacent record.

---

## 3. Q1 — SELF vs OTHER: the real question is not self-vs-other

**1,558 cards. This is the ruling the whole batch turns on.**

The census framed it as *self vs other* and proposed one scope-slot convention.
The framing is one dimension short. §6a makes **two** printed distinctions axis
identity, and they are independent:

```
SUBJECT  x  CONTROLLER
```

Measured, all five families pooled (1,594 ability lines / 1,558 cards):

| subject ↓ / controller → | unqualified | you control | opponent controls | each | **total** |
|---|--:|--:|--:|--:|--:|
| **`another`** (excludes source, §6a r3) | 91 | 320 | 0 | 0 | **411** |
| **bare `a`** (**includes** source) | 437 | 683 | 62 | 1 | **1,183** |

### The finding that matters

**75% of this population prints "a", not "another".** A convention named
"self vs other" would label all 1,183 of them *other* — and §6a rule 3 forbids
exactly that:

> "**another / other** — excludes the source. A slug may not claim it of a
> member whose printed text can affect itself."

Soul's Attendant reads "Whenever **another** creature enters" — the source is
excluded. Minion Reflector reads "Whenever **a** nontoken creature you control
enters" — **the Reflector's own arrival triggers it.** Those are different
cards for deck-building, and the difference is printed.

### The recommendation — one prefix pair, zero renames

> **Q1.** Ratify a **DELIVERY subject prefix**, applied to the existing §2
> trigger tokens:
>
> | prefix | printed | means |
> |---|---|---|
> | *(unmarked)* | "when **~** enters" | the source. **Every current token keeps its meaning** |
> | `other-` | "whenever **another** creature enters" | excludes the source |
> | `any-` | "whenever **a** creature enters" | includes the source |
>
> giving `other-etb`, `any-etb`, `other-death-trigger`, `any-attack-trigger`,
> `other-leaves-battlefield-trigger`, `other-combat-damage-to-player`, …
>
> **Recommend ratifying.**

Why this shape:

1. **Zero migration.** The unmarked tokens keep meaning "~", so no existing
   axis is renamed and no membership moves. The 2,700-card unblock costs no
   codebook surgery.
2. **One ruling, five families — and every future one.** It composes with §11's
   grammar-instantiation, so `becomes-tapped-trigger` and the cycling triggers
   inherit it the moment they are ratified, rather than each needing its own
   self/other ruling. That is what makes it one ruling and not five.
3. **`any-` already has a precedent.** §8a ratified `any-` for counters that
   "genuinely span every type and therefore cannot be typed" — the same job:
   a scope word for the case that is deliberately unrestricted.
4. **It does not overload SCOPE.** Putting the trigger's subject in the SCOPE
   slot would collide with the effect's scope: in
   `etb-create-token-clue-own`, `own` would mean both *who controls the
   entering permanent* and *who gets the Clue*. That is design goal #2 —
   "no slug may be readable as two different mechanics".

The **controller** dimension (`you control` / `an opponent controls`) is a
separate slot and already has §6 vocabulary (`own`, `opponent`). It needs no new
token — only the ruling that it is mandatory when a sibling differs on it,
which §1 already says.

### One place where literal reading and mechanics diverge — flagged, not decided

The 62 `bare-a / opponent controls` lines print "a creature **an opponent
controls** dies". Mechanically the source can never be that creature, so
`any-` and `other-` are indistinguishable in play. Printed, it says "a".

> **Q2.** For opponent-controlled subjects, follow the **printed** word (`any-`)
> per §6a, accepting a harmless redundancy? Or use `other-` to reflect the
> mechanical truth? **Recommend the printed word** — §6a's whole point is that
> the printed word is the claim, and an exception would put the reader back to
> case-by-case judgement.

---

## 4. Q3 — the active-player end step has no scope token

Carried from `END-STEP-TRIGGER-RULING-2026-08-03.md` §3, unresolved and still
the honest blocker on the 536.

| printed | cards | §6 token |
|---|--:|---|
| "at the beginning of **your** end step" | 405 | `own` ✓ |
| "at the beginning of **each** end step" | 81 | `each` ✓ |
| "at the beginning of **the** end step" | 50 | **none exists** |

"The end step" means *whoever's turn it is*. `own` is wrong (it is not
necessarily yours) and `each` is wrong (it fires once, not per player).

> **Q3.** Ratify **`active-player`** as new §6 SCOPE vocabulary, anchored to
> **CR 500.1 / 502.1** ("the active player" is the CR's own term)?
> **Recommend yes.** It is a printed, consequential distinction — an Aura keyed
> to someone else's turn is a different card from a your-end-step value engine —
> and §6b says per-shape distinctions are free to mint.

---

## 5. Q4 — `you own` is not `you control`, and §6's `own` is ambiguous

Surfaced by the scope census; small but genuinely unresolved.

Three cards print **ownership**, not control:

- Park Bleater — "whenever another creature **you own** enters"
- Athreos, God of Passage — "whenever another creature **you own** dies"
- Jon Irenicus, Shattered One — "whenever a creature **you own but don't
  control** attacks"

Jon Irenicus is the proof that these are not synonyms: it prints both, in
opposition. CR 108.3 (owner) and CR 109.5 (controller) are different rules.

**§6's scope token `own` is glossed "(yours)" — which does not say which.**

> **Q4.** Does §6's `own` mean *controller*? If so, ratify a distinct token for
> ownership. **Recommend: `own` = controller** (it matches all ~1,000
> "you control" members already using it), **and add `owned` for the
> ownership sense**, n=3 today. §6b: "per-shape axes are free. Mint them."

---

## 6. Q5 — the CR 702 census you asked for: static vs triggered keywords

> Captain: *"also check the CR and how keywords have different properties.
> static versus trigger keywords"*

Measured directly from the CR by `experiments/foundry_cr702_classes.py`.
**193 keywords.** Classes are read from the CR's own "X is a ___ ability"
sentences and validated against **CR 113.3a–d**, which is the CR's
authoritative enumeration of the four ability classes — parsed at run time,
never hand-listed.

| CR ability class | keywords | §2 DELIVERY slot |
|---|--:|---|
| **static** | **71** | `static` — **already ratified** |
| **triggered** | **44** | **each needs a trigger token** |
| **activated** | **19** | `activated` — already ratified |
| static **+** triggered (multi-class) | 7 | both |
| spell + static | 1 | Cipher |
| **UNSTATED** — the CR states no class | **51** | — |

Two CR class words roll up, and the CR says so itself, so neither is my
inference:

- **evasion → static.** CR 509.1b: *"an evasion ability (**a static ability**
  an attacking creature has that restricts what can block it)"* — Flying, Fear,
  Menace, Shadow, Skulk, Intimidate, Landwalk, Horsemanship.
- **characteristic-defining → static.** CR 604.3: *"**Some static abilities**
  are characteristic-defining abilities"* — Changeling, Devoid.

### What this settles

**The delivery slot of a CR 702 keyword is not a judgement call — it is stated
in the keyword's own sub-rule.** That is exactly how `cycling` was derived
(CR 702.29a → activated → §2's existing `activated` token, no new vocabulary).
The same derivation now covers all 193 at once:

- **90 keywords (71 static + 19 activated) need NO new vocabulary.** They map
  onto §2 tokens that already exist. Flying, trample, vigilance and the rest of
  the uncovered CR 702 population from the cycling ruling §7 are all `static`.
- **44 triggered keywords are the actual gap**, covering **1,099 cards**.
  Ward alone is 206 — and Ward is already served, because §2 ratified
  `becomes-targeted-trigger` for exactly that family.

Ranked by cards: Ward 206 · Prowess 90 · Cumulative Upkeep 80 · Echo 50 ·
Cascade 37 · Bushido 37 · Exalted 36 · Storm 35 · Flanking 29 · Firebending 26 ·
Soulshift 26 · Persist 25 · Backup 25 · Exploit 25 · Undying 24 · Myriad 23 ·
Evolve 23 · Renown 20 · Mentor 20 · Living Weapon 19 …

> **Q5.** Adopt **"a CR 702 keyword's DELIVERY is whatever its `702.Na`
> sub-rule says it is"** as a derivation rule, so keyword axes stop needing a
> per-keyword vocabulary ruling? **Recommend yes** — it is the cycling
> precedent generalized, and it converts 90 keywords from "unruled" to
> "buildable today" at zero cost.

### Two things the tool refused to guess

- **51 UNSTATED.** The CR never calls them "a ___ ability" — Flashback, Escape,
  Bestow, Mutate, Evoke, Dash, Blitz, Companion, Plot, Solved, Visit and 40
  more. Reported by name, never assigned to a nearest class.
- **10 multi-class keywords hinted but unresolved.** CR 702.62a: *"Suspend is a
  keyword that represents **three abilities**"* — one static, two triggered.
  Collapsing that to "static" would be precisely the approximation the tool
  exists to refuse, so it warns instead: Fading, Suspend, Vanishing, Evoke,
  Dash, Awaken, Partner, Blitz, Gift, Offspring.

**`kicker` is worth your eye.** §2 lists it as a DELIVERY token, but **CR
702.33a says "Kicker is a static ability."** It is not a contradiction — §2's
`kicker` names a *cost-condition shape*, not an ability class — but it is the
one §2 token whose basis differs from every other. Logged, not raised as a
defect.

---

## 7. THE BATCH — the tokens to rule

With Q1 ratified, these are the delivery tokens the four 2026-08-03 rulings
asked for. Counts re-measured this session.

| token | cards | CR | status |
|---|--:|---|---|
| **subject prefixes `other-` / `any-`** (Q1) | **1,558** | 113.3c + §6a r3 | proposed |
| `end-step-trigger` + scope (405 own / 81 each / 50 active-player) | 536 | 113.3c, 500.7 | proposed; batch-1 kill addressed in §1 |
| `becomes-tapped-trigger` | 111 | 603.2e | proposed |
| `cycled-trigger` · `cycles-a-card-trigger` · `cycle-or-discard-trigger` | 89 | 702.29c/d | proposed |
| `tapped-for-mana-trigger` | 33 | — | proposed |
| `becomes-untapped-trigger` | 33 | 603.2e | proposed |
| **`active-player`** SCOPE (Q3) | 50 | 500.1 | proposed |
| **`owned`** SCOPE (Q4) | 3 | 108.3 | proposed |

**Corrected batch total: ~2,360 cards** (was stated as ~2,700). Still, by a
wide margin, the largest unblock per unit of your throughput on the board.

---

## 8. Carried, unchanged — not part of this batch

- **Clue §4f `-conditional`** — 9 members placed on the base axis on a stated
  assumption; the member list is the whole worklist, one move spec either way
- **Clue §5 provenance** — 120 model-derived seeds carrying `class: human`
- **Clue §4c** — 7 another-player-creates cards across five printed scopes;
  building them renames `rule:create-token-clue` per §1
- Typecycling split · Tier-4 calls 3a/3c/4 · §S4 preprocessor · D13 · §S
  (88 Alchemy) · CDR-01 · Saga/Class chapter vocabulary (576 lines, 221 cards —
  the largest gap this batch does **not** address)

---

## 9. Code written this session — uncommitted, nothing committed without your ask

| file | what |
|---|---|
| `experiments/foundry_cr702_classes.py` | **new.** CR 702 keyword class census (Q5) |
| `experiments/foundry_selfother_scope.py` | **new.** SUBJECT × CONTROLLER matrix (Q1) |
| `experiments/foundry_shape_extractor.py` | self-noun set derived from type lines (§2a); phase triggers claimed off the clause (§2c) |
| `experiments/foundry_common.py` | canonicalizer: legendary subtitle + Alchemy `A-` short forms (§2b) |

**Regression check on the generator fixes.** The extractor's 116-card
hand-verified Clue ground-truth set was re-run against HEAD and against the
fixed tool: **byte-identical output**, so the "validated 116/116" claim still
holds and none of the three fixes disturbed a verified routing. Worth recording
that the ground-truth set did **not** catch these defects either — no Clue card
is an Equipment, a Siege, or a legendary short-name self-reference. A
ground-truth set validates only the shapes it contains; widening it is the
standing job. `--rank` was also re-run: `regenerate` is unchanged at 397 cards /
72.4% and remains the recommended next action.

Both new tools are zero-token and verified **determinism ×2 byte-identical**.
Gate 2 re-run after every change: **lint clean · drift 35, identical partition ·
sweep 232 / 6 blocking · codebook sha unchanged** — no codebook mutation
occurred this session, and no backup was needed because nothing was written.
