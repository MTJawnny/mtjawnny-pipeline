# W1 + W2 — the record

# W1 — TRAP SWEEP

**Packet:** `WORK-PACKETS-2026-08-07.md` § W1 · **tier A** (no vocabulary
minted, no codebook mutation).

**DATE NOTE.** The doc series and the handoff are dated **2026-08-07**; the
machine clock during this session read **2026-08-04**. Both are recorded
rather than reconciled, because guessing which is right is exactly the kind
of silent substitution this project keeps paying for. The filename carries
no date for the same reason.

---

## 1. WHAT THE PACKET ASKED FOR

Two known defects (AUDIT-5 findings 3 and 5), then **a sweep for their whole
class** — the sweep being the actual deliverable, the two lines being worked
examples. Three sweep classes were named. All three were run and all three
results are below, including the ones that found nothing.

---

## 2. THE FIXES, IN THE ORDER THEY HAD TO HAPPEN

### 2a. `46c7beb` — the 603.11 split gates on the CR CLASS, not the token

**Not in the packet. Found by fixing finding 3 first and reading the diff.**

Applying finding 3 on its own closed 25 gaps and **destroyed a ratified
`any-death-trigger`** on Predatory Sludge. The line kept a ratified token, so
`diff --strict` scored it a RE-ROUTE and exited 0. Only the delivery-row count
(61952 → 61951) showed the loss.

Cause: `is_static` — the gate on the CR 603.11 / 607.2h linked-ability split —
admitted `static` and `spell-or-static` and refused `replacement`. It was
testing the **token spelling** where CR 603.11 says **static ability**.

The chain closes in three rules:

| rule | text |
|---|---|
| CR 614.1 | *"Some **continuous effects** are replacement effects."* |
| CR 113.3d | *"**Static abilities** create **continuous effects**…"* |
| CR 113.3 | four categories; a permanent's replacement effect is not spell / activated / triggered |

CR 607.2h then applies verbatim: *"If an object has both a **static ability**
and one or more **triggered abilities** printed on it in the **same
paragraph**, each of those triggered abilities is linked to the static
ability."*

`replacement` takes the **same CR 113.3a cut** as `spell-or-static`: on an
instant/sorcery the effect is created by the *resolving* spell, so a later
trigger is DELAYED (CR 603.7a) and belongs to its creator (§2d). Without that
cut the split also claimed **Heroic Sacrifice** and **Semester's End** — the
same "95 of them spells" failure the existing comment already records.

**4 lines, all permanents, all read:** Valentin Dean of the Vein, Nemata
Primeval Warden, Superior Spider-Man, Wall of Stolen Identity. Each is a CR
614 replacement followed by its linked trigger. The new second delivery is
unrouted — an honest gap, and the ability is now *visible*.

**This was a pre-existing defect, not one finding 3 introduced.** Every
`replacement` line had been denied the split since the split was written. The
routing regression compares tokens and the gap census counts vocabulary, so
neither could see it: it is the visibility audit's **layer-1 DROPPED**.

### 2b. `e81c1d7` — AUDIT-5 finding 3: `\b` cannot match next to `~`

`^as (?!an additional cost|long as)\b…`. Canonicalization rewrites the card's
own name to `~`, a **non-word character**, so the boundary between the space
and the `~` never matched.

**26 lines**, all read, all CR 614.1c's own second template
(*"As [this permanent] enters . . ."*): Stenn, Pramikon, Iona, Morophon,
Umori, Talion, Saskia, Throne of Eldraine, Three Tree City, …

The 26th is the proof: Predatory Sludge moves
`[None, any-death-trigger]` → `[replacement, any-death-trigger]` — gap closed
**and** linked trigger kept. **Delivery-row count unchanged**, which is the
evidence that 2a was the required prerequisite.

### 2c. `4b07b77` — AUDIT-5 finding 5: an etb subject can be PLURAL

`\benters\b` → `\benters?\b`. **58 lines**, all gains, none lost — more than
the packet's predicted 43, because the packet's number was measured on an
earlier code state.

- **51 gap closes**: 23 `any-etb`, 19 `etb`, 9 `other-etb`. The §2a subject
  split lands correctly on its own.
- **7 re-routes, and they are why the whole diff was read.** Four are
  `[cast-trigger]` → `[etb, cast-trigger]`, two `[None, attack-trigger]` →
  `[etb, attack-trigger]`: **pair-named legendaries** whose collapsed `~`
  takes a plural verb — *"When The Fantastic Four **enter** and whenever you
  cast …"*, *"Whenever Krang & Shredder **enter** or attack"*. Those lines
  already carried a ratified token, so the missing `etb` half was a silent
  under-count inside the largest trigger family (5,713), not a visible gap.

`TRIGGER_VERB` already carried `enter` (CR 603.6a), so the clause splitter
handled the plural and only this branch did not — **the inflection was tested
in one place and not the next.**

---

## 3. THE SWEEP — all three classes, with results

### Class 1 — `\b` adjacent to `~` · ONE SITE FOUND, and it was dead code

`grep '\b~\|~\b'` found a third site: `PREDICATE`, the test for whether a
later `or`/`and` segment is itself a trigger predicate, carried `~\b`. After
canonicalization a `~` is always followed by a space, `'s` or end-of-string —
**all non-word characters** — so the alternative could never fire. Rewritten
to `~(?:\s|'s|$)`, the shape already used at the two sites fixed earlier.

**0 lines moved, and the reason is measured, not assumed:** across all
**15,335** trigger lines in the gated corpus, **zero** later `or`/`and`
segments begin with `~`. The alternative is unreachable in this corpus
whichever way it is spelled, so the fix is **LATENT** — it makes the regex
mean what it says and closes the trap's third instance, but it does not move a
line today. Stated that way rather than as "no-op", per the standing rule.

**Class 1 is now closed:** `grep '\b~\|~\b'` over the extractor is clean.

### Class 2 — inflected verb tests · THREE SITES FOUND, 8 lines

Every verb test in the extractor was enumerated. **Eleven already carried
`s?`** — `enters?`, `attacks?`, `casts?`, `deals?`, `cycles?`, `discards?`,
`sacrifices?`, `gains?`, `becomes? tapped`/`untapped`, `leaves?|leave`,
`dies|die`. **Three did not**, all in adjacent branches:

| was | now |
|---|---|
| `\bbecomes the target of\b` | `\bbecomes? the target of\b` |
| `\bblocks\b` | `\bblocks?\b` |
| `\bbecomes blocked\b` | `\bbecomes? blocked\b` |

**8 lines moved, all read, all correct.** Two different subjects take the
plural verb and **both** are in the moved set:

1. a plural noun phrase — *"whenever one or more creatures you control
   **become blocked**"* (Hezrou, Professor Hojo, Tide of War);
2. the pronoun `you` — *"whenever **you become the target** of a spell"*
   (Amulet of Safekeeping, Dormant Gomazoa), **singular in sense, plural in
   conjugation**. An `s?` sweep catches both; a "plural subject" heuristic
   would have missed the second.

The re-route is again a pair-named legendary: **Bebop & Rocksteady**'s
*"attack or block"* was `[attack-trigger, None]` and is now fully routed.
Third card class this session whose collapsed `~` takes a plural verb.

One line **gains a row** rather than filling one: *"whenever one or more
creatures you control **fight** or become blocked"* goes `[None]` →
`[None, blocks-or-becomes-blocked-trigger]`. The `fight` half stays an honest
gap; only the half with a token got one.

### Class 3 — separators and symbol variants · NOTHING FOUND

Four sites spell the same separator concept four different ways:

| site | admits | omits |
|---|---|---|
| `_DIE_ROW` (150) | `- – \| or through thru` | em-dash, `+` |
| `CHAPTER` (228) | `— -` | en-dash |
| CR 706.3b refusal (862) | `\| — -` | en-dash, `+` |
| `_KF_DASH_CLAUSE` (1216) | `— –` | hyphen |

**Measured against the corpus, every omission is inert:**

| what | measured |
|---|--:|
| **EN-DASH U+2013 anywhere in oracle text** | **0** |
| EM-DASH U+2014 in oracle text | 4,253 |
| Saga chapter separator after roman numerals | `—` **576**, nothing else |
| ability-word prefix dash | `—` **3,116**, nothing else |
| die-row *row* separator | `\|` **80**, nothing else |
| die-row *range* separator | `—` 75 · `+` 49 · bare 26 · `-` 5 · `or less` 1 |

- `_DIE_ROW`'s missing em-dash is inert because it is tested **only against
  the pre-em-dash prefix**, which is digits-only in practice (`1—9 \| …` gives
  `pre = "1"`).
- The `+` station rows never reach these sites: `9+ \| Flying` has **no
  em-dash**, so `_DASH_PREFIX` never matches, and line 196 refuses any prefix
  starting `+`.
- Line 862's missing `+` has **no impact**: exactly **one** line in the corpus
  has a die/station first sentence *and* a later trigger sentence — The Deck
  of Many Things — and it is **already refused** (it is the comment's own
  worked case).
- **En-dash is zero corpus-wide**, so every `[—–]` alternation's en-dash is
  dead weight in both directions.

**No code changed for class 3.** The variants were measured and do not exist;
widening by hand against a measurement that says zero would be the hand-list
defect in a new costume.

### Class 3 addendum — the apostrophe, checked because CLAUDE.md names it

| | |
|---|--:|
| STRAIGHT `'` U+0027 in oracle text | **13,175** |
| CURLY `’` U+2019 in oracle text | **0** |

Scryfall is **100% straight**. The four straight-only patterns (610, 1669,
1674, 1792) are therefore correct against corpus data, and the five
curly-tolerant ones (147, 187, 363, 606, 2401) sit exactly where **CR-parsed**
values are compared. **No defect.** The CR/Scryfall apostrophe split is being
handled on the correct side of the boundary.

---

## 4. PROBE DEFECTS THIS SESSION — the standing tally continues

**Two**, both caught by controls rather than by review, which is the point.

1. **`strip_ability_word()[1]`.** The function returns a **string**; the probe
   subscripted it and silently measured **the second character** of every
   line. Every pattern returned 0 — *including the controls*. Caught by
   negative-controlling with `\bblocks\b`, which cannot legitimately be 0.
   (`ability_word_prefix()` is the one returning `(pre, body)`; the two were
   confused.)
2. **`deliveries_for_lines()` yields `(line, [(tok, desc), …])` tuples**, not
   dicts. `row.get('descriptor')` raised rather than silently mis-measuring —
   the loud failure was luck, not design. Same family as the recorded
   `kw in [(tok, desc), …]` defect.

Both are the recorded family: **asking the question again instead of consuming
what the classifier emitted.**

---

## 5. STATE AFTER W1 — measured, not carried forward

```
ability lines scanned        61,961      keyword homes 150 (unchanged throughout)
unclassified-trigger            935      was 988   (−53)
linked:unclassified-trigger      38      was  34   (+4, see §2a — rows that
                                                    came into existence)
INSIDE spell-or-static       14,864      was 14,898
  undecidable (§1 default)   10,413      70.1%     unchanged
  decidably STATIC            4,451      29.9%     was 4,485  (−34)
```

**Gates green after every fix:** `invariance --strict` · `punctuation_audit`
· `visibility_audit` (33 uncontexted, **unchanged throughout**) ·
`ground_truth` (**488/488, unchanged throughout**).

**One deliberate baseline re-pin**, at §2a only:
`descriptor_unrouted.linked:unclassified-trigger` 34 → 38. Re-pinned because
those four rows **came into existence** — previously the linked triggered
ability had no delivery row at all — not because four rows degraded.
Conservation itself never failed: *"no text, sentence or ability was lost"*
held at every step.

---

## 6. W3 RE-MEASURED — the packet told this session to do this

> *"RUN W1 FIRST. The 88-line top shape is the plural-`enter` defect; fixing
> it may dissolve a chunk of this population for free. Re-measure before
> batching."*

**It did dissolve.** `whenever one or more … enter` was the packet's #1 shape
at 88 lines and **is now absent from the census entirely**.

```
unclassified-trigger    988 → 935 lines   (−53)
```

New top shapes:

| n | shape |
|--:|---|
| 51 | `whenever you draw your second card` |
| 23 | `whenever one or more cards leave` |
| 20 | `whenever you draw a card, put` |
| 19 | `whenever you put one or more` |
| 19 | `when this creature exploits a creature` |
| 16 | `eerie — whenever an enchantment you control` |
| 14 | `whenever an opponent draws a card` |
| 13 | `when you control no islands, sacrifice` |

**BOUNDARY, because a shape count is meaningless without one:** these are
**first-six-word** shape keys — **494 distinct, 364 singletons**. The packet's
"278 distinct shapes / 174 singletons" used a different granularity, so
**278 → 494 is not a movement** and must not be read as one. Only the **935**
line count is comparable to the packet's 988.

**W3 remains unstarted and still needs a fresh price check plus Captain
go-ahead** — a separate wallet from the Claude Code quota.

---

# W2 — CR 706.3b DIE-ROW ROUTING · TIER A · DONE

**The ruling, verbatim (CR 706.3b):** *"An instruction to roll one or more
dice, any instructions to modify that roll printed in the same paragraph, any
additional instructions based on the result of the roll, and **the associated
results table** are **all part of one ability**."*

So a row is **not an ability** and never earns a delivery of its own. D3
inheritance, one rule over from the CR 700.2 modal case. **No vocabulary:** the
token is the header's, unchanged; only the descriptor is annotated `die-row:`.
Delivery-row count 61,961 → 61,961 — pure re-labelling.

## Result

| | |
|---|--:|
| rows inheriting a roll ability's delivery | **119** (was 0) |
| lines moved in the routing diff | **78** |
| uncontexted CR 706.3b rows | **2 → 0** |

Inherited tokens, each verified against its own header: `activated` 25
(`{T}: Roll a d20.`) · `etb` 21 · `attack-trigger` 17 · `begin-combat` 5 ·
`cast` 3 · `upkeep` 3 · `death` 3 · `None` 42.

## The packet predicted zero re-routes. It was wrong, and the two exceptions were the point.

> *"Expect ~99 lines `None → <the roll ability's token>` and **zero**
> re-routes."*

**Two rows already carried a ratified token and BOTH were wrong.** A row's
effect text parses perfectly well on its own and is still not its own ability:

| card | was | why it was wrong |
|---|---|---|
| **Cone of Cold** `20 \| … creatures your opponents control ENTER TAPPED` | `replacement` | Real CR 614.1d shape, but the ability is a **SORCERY's spell ability** (CR 113.3a) — §1's unmarked default. The effect is *created by the resolving spell*, so §2d gives its delivery to the creator. Same cut as `46c7beb`. |
| **Delina, Wild Mage** `1—14 \| … it has "At end of combat, exile this token."` | `static-grant` | read off a **granted ability in quotes** |

Cone of Cold is therefore a **deliberate `ratified → None`** — the one
direction `--strict` halts on. Read and accepted: removing a confidently wrong
token is a correction, not a loss. Delina `static → attack-trigger` is a
correction in the other direction.

**This is why the inheritance is UNCONDITIONAL**, unlike the modal branch,
which falls back to parsing the option alone when the header carries no
ratified token. That fallback is precisely what produced both wrong answers.
**42 rows inherit `spell-or-static` from a spell header and stay unrouted** —
the recorded *"UNROUTED IS NOT STOPPED"* rule; inheriting no token is correct.

## Three defects found while doing it, none of them in the packet

**1. A bar row outranks the modal test; a bullet does not.** `N |` is
typography only a results table uses, so it decides the block alone; a bullet
is shared with CR 700.2, so there the modal header keeps precedence. Gating
both on `not is_modal` suppressed a real table, because `_MODAL_HEADER_RE`
matches *"**CHOOSE UP TO TWO** target permanent cards in your graveyard. Roll
a d20 …"* (Song of Inspiration) on its `up to \w+` arm — a **targeting**
instruction, not a mode list.

**2. The same bug was live one layer down, in the ratified DET join.**
`expand_modal_bullets` tested `_MODAL_HEADER_RE` first in its if/elif, handing
the table `is_mode_line` as its option test, which no bar row satisfies. Fixed
with the **same rule at both sites** so they cannot drift apart. **0 lines
moved in the routing diff and that was not the measure** — the join is what
makes an option *contexted*, and uncontexted die rows went **2 → 0**.

**3. `_DIE_ROW_RE` knew three range forms; there are five.**

```
20+ | …          Druid of the Emerald Grove, Song of Inspiration (15+ |)
9 or less | …    Druid of the Emerald Grove
```

An **unbounded** roll can exceed the die's face value (*"roll a d20 **and add**
the number of cards in your hand"*), so a table's last row is open and its
first may be too.

**The old census could not have found this.** Its *"three printed forms,
measured across 106 rows"* counted only rows the regex **already matched** — a
recall measurement taken through the filter under test. It reported 106 of 106
and was blind to the two missing forms **by construction**. Same family as the
gap census being blind to `spell-or-static`, and as W1's `\bblocks\b` probe
returning 0 on its own controls.

Druid's table **opened** with `9 or less |`, so **all three** of its rows were
unjoined and unrouted: a first-row form gap costs the whole table, not one row.

**CR 721 safety, verified not assumed.** `9+ | Flying, first strike` is a
station striation — same shape, different rule — and now matches this regex.
It cannot be joined: both consumers test it only **after**
`_ROLL_INSTRUCTION_RE` opens a block, and a station card prints no roll
instruction. Measured live: **0 station rows joined, all 42 correctly left
alone.**

## Baselines

Re-pinned twice, both onto measured improvement, neither reflexively:

- `die-row:spell-or-static` 36 → 42 tripped the ratchet, but those 6 rows moved
  **between two unrouted descriptors**, not from routed to unrouted; total
  `unrouted_lines` **fell** 15,747 → 15,744. The new descriptor is strictly
  more informative — it names *why* the row is unrouted.
- `uncontexted` 33 → 31.

## State after W2

```
unclassified-trigger            935     unchanged by W2
die-row:spell-or-static          42     NEW — rows inheriting a spell header's
                                        §1 default; correct, not a queue
INSIDE spell-or-static       14,747     was 14,864
  undecidable (§1 default)   10,372     70.3%
  decidably STATIC            4,375     29.7%     was 4,451   (−76)
uncontexted                      31     was 33
```

**W4's target is now 4,375.**



---

# W2 ADDENDUM — Captain sent me back to the CR on Cone of Cold

**Verdict: the Cone of Cold ruling STANDS, and the recheck was still worth it
— it caught a defect in my own W2 work and surfaced a finding much larger than
the card.**

## 1. Cone of Cold — confirmed, on a better anchor than I had

I had justified it from CR 706.3b + CR 113.3a + §2d. **CR 706.3a settles it
more directly and I had not read it:**

> *"Each list item or striation includes possible results and an effect
> associated with those results. … **Each one means "If the result was in this
> range, [effect]."**"*

A results-table row **expands to a conditional EFFECT inside the one ability**.
It is not an ability, so it has no delivery slot of its own — the question of
whether the row "is a replacement" never arises. Cone of Cold's `20 |` row
reads `replacement` only because its *effect text* contains "creatures your
opponents control enter tapped" (CR 614.1d). The ability is the sorcery's
spell ability; the replacement effect is **created on resolution**.

`replacement → None` stands.

## 2. What the recheck caught in my own work — CR 706.3a is a CLOSED LIST

> *"The possible results indicated could be **a single number**, a range of
> numbers with two endpoints in the form **"N1–N2,"** or a range with a single
> endpoint in the form **"N+."**"*

**Three forms, enumerated by the CR.** I had widened `_DIE_ROW_RE` from a
corpus census instead of from the rule that publishes the answer — the
**"NEVER TRANSCRIBE THE CR — DERIVE FROM IT AT RUN TIME"** failure, committed
while writing a commit message criticising a census for being blind through
its own filter.

| form | measured | standing |
|---|--:|---|
| `N1–N2` | 80 | CR 706.3a |
| `N+` | 49 | CR 706.3a |
| single number | 26 | CR 706.3a |
| `N or less` | **1** | **outside CR 706.3a → CR-LAG** |
| `N or more` | **0** | **removed — I invented it** |

- **`or more` removed.** Added on symmetry with `or less`, attested nowhere. A
  member with no evidence is a hand-list defect however plausible it looks.
  0 lines moved, which is the proof it was dead.
- **`or less` kept and registered as CR-LAG** with its evidence, on the same
  footing as `chorus`: Druid of the Emerald Grove, `9 or less | …`. It is that
  table's **first** row, so excluding it costs all three. **Second CR-LAG
  entry; second piece of evidence for W8 item 2 (refresh the CR snapshot).**
- CR 706.3a prints `N1–N2` with an **en-dash** while the corpus prints em-dash
  or hyphen — the CR-vs-Scryfall character split appearing in a **rule** rather
  than a card name.

## 3. THE FINDING — Cone of Cold was one symptom of a class · NOT FIXED, LOGGED

CR 113.3a: *"Any text on an instant or sorcery spell is a spell ability
**unless** it's an activated ability, a triggered ability, or a static ability
that fits the criteria described in rule 113.6."*

**The `replacement` branch has no spell-face gate at all.** W1 added that cut
to `is_static` for the CR 603.11 split; the branch itself never got it.

**147 lines on SINGLE-FACED instants and sorceries route to `replacement`:**

| descriptor | n | verdict |
|---|--:|---|
| `replacement` | **117** | **suspect** — a spell ability that CREATES a replacement effect on resolution |
| `keyword:madness` | 26 | **correct** — CR 702.35a's first ability is a static that functions **in hand** and reads *"…may exile it instead…"*. CR 113.6 exemption applies |
| `keyword:dredge` | 4 | **correct** — CR 702.52a, a static functioning **in the graveyard**, worded *"if you would draw a card, you may instead…"* |

So the keyword 30 are right *because CR 113.3a's own exception names them*,
and the 117 are the real queue. Worked cases, all single-faced spells whose
text describes an effect created on resolution:

```
Heroic Sacrifice   … all damage that would be dealt to you … instead
Yamabushi's Flame  … if a creature dealt damage this way would die … exile it instead
Carom              The next 1 damage that would be dealt … instead
Fatigue            Target player skips their next draw step.
Blood of the Martyr / Mirror Strike / Reflect Damage / Eye for an Eye
Torch the Tower / Puncturing Blow / Narset's Rebuke / Due Respect
```

**Not all 117 resolve to `None`.** At least one is a CR 113.6 static that is
simply mis-tokened rather than over-tokened — Glimpse the Cosmos (*"As long as
you control a Giant, you may cast this card from your graveyard"*) is a static
ability functioning in the graveyard, so its answer is `static`, not the §1
default. **The 117 needs reading, not a blanket sweep** — the standing
PRE-STEP-2 warning, and the same reason W4 is taken one named shape at a time.

**The 218 figure from the first pass was wrong and is not the number.**
`_has_spell_face` is CARD-level, so an MDFC like *Fell the Profane // Fell Mire*
(Instant // Land) counts as spell-faced while the line belongs to the **land**
face and is a perfectly good permanent replacement effect. Restricting to
single-faced cards gives 147. **A per-FACE cut is what this fix actually
needs**, and that is a real piece of design, not a one-line gate.

**Boundary: this is outside W2** (inheritance only) and outside tier A's
"no new anything" only in the sense that it is a fix worth its own packet.
Logged, not started.


---

# W1 AUDIT — every W1 fix rechecked against its CR entry

Captain's instruction after the Cone of Cold recheck. **One real defect found,
and it was one I introduced.** The other three classes came back clean, each
with the measurement that says so.

## 1. THE DEFECT — my own etb fix handed out a wrong token · FIXED

`\benters?\b` made **Mythweaver Poq** — *"whenever one or more nontoken lands
enter under your control"* — reachable for the **first time**, and it landed on
`any-etb`. The more specific `landfall` branch sits **one line above** it and is
still singular-only, so it could not see the line.

**Before W1 that line was an honest gap; after W1 it carried a confidently
wrong ratified token.** That is the recorded *"improving recall can hand out a
WRONG ratified token"* trap — **which this very record quotes** — and the
gap-close diff scored it as pure profit. I read the line during W1 and accepted
it. Reading was not enough; what caught it was asking *"is there a more
specific branch that should have claimed this?"*

`any-etb` is wrong on **both** dimensions: §6a says `any-` must mean **any**,
and these are lands entering under **your** control. `landfall` is CR 207.2c's
ability word for exactly that shape.

**The plural arm needs its own control scope.** The singular form excludes an
opponent's land by **adjacency** — *"a land AN OPPONENT CONTROLS enters"* puts
words between `land` and `enters`. That trick does not survive the plural, where
the control clause moves **after** the verb. A naive `lands? … enters?` widening
claimed **9** clauses, **8 of them opponent-scoped** (Polluted Bonds, Sire of
Stagnation, Shattered Angel, Archaeomancer's Map, Confounding Conundrum,
Spectrum Sentinel, Nightshade Harvester, Deep Gnome Terramancer) — all correctly
`any-etb`. So the plural arm **names** the scope rather than relying on word
order. **1 line moved, 0 lost.**

## 2. Finding 3's branch vs CR 614.1c / 614.1e · CLEAN

Two things were worth suspecting and both measured clean:

| suspicion | measured |
|---|--:|
| the hand-chosen `{0,40}` window (the file's own comments call a guessed distance a defect class — D5's `{0,60}`) | **0 lines missed** at `{0,200}` |
| `(?:enters\|is turned face up)` is singular-only, exactly finding 5's shape | **0** `As … enter` (plural) lines exist |

CR 614.1c's template is *"[**This permanent**] enters"* — singular by
construction — and CR 614.1d's `[Objects] enter` second template is
**deliberately declined** by the existing code, with its own measurement. So
the singular is correct here rather than merely untested.

## 3. Class 2's block / target branches vs CR 509 and CR 115 · CLEAN

CR 509.3e names a form the branch does not match — *"the ability triggers if the
creature blocks or **is blocked by** that many creatures"* — so I measured every
trigger clause containing `blocked` or `target` that the branches do **not**
claim.

| | n | shapes | verdict |
|---|--:|--:|---|
| `blocked` unmatched | 39 | 8 | **all correct** |
| `target` unmatched | 105 | 15 | **all correct** |

Every one is a clause whose **event** is something else and where the word sits
in a *condition* or a *property* — CR 113.3c's "the event lives in the
condition" rule doing its job:

```
whenever this creature attacks and isn't blocked      -> attack-trigger      (36)
at end of combat, if this vehicle attacked or blocked -> end-combat-trigger
whenever one or more creatures an opponent controls
        attack you and aren't blocked                 -> is-attacked-trigger
whenever you cast a spell that targets this creature  -> cast-trigger        (65)
```

Not matching these is the branch being **correctly scoped**, not a gap.

## 4. Subject prefixes on the newly-reachable plurals · CLEAN

The concern after §1: do the plural forms get the same subject prefix as their
singular twins? Measured pairwise — **they do, exactly.**

| clause | token | n |
|---|---|--:|
| `a creature you control enters` | `any-etb` | 37 |
| `one or more creatures you control enter` | `any-etb` | 1 |
| `another creature you control enters` | `other-etb` | 82 |
| `one or more other creatures you control enter` | `other-etb` | 3 |

## 5. LOGGED, NOT FIXED — `any-` may not mean any

Falling out of §4: **`any-etb` is the token for `a creature YOU CONTROL
enters`** (37 lines), alongside `a creature enters` (16 lines). §6a is explicit
that **`any-` must mean any**, and "you control" is a scope, not "any".

**This is pre-existing and W1 did not create it** — the plurals merely inherited
it. It is an **axis-identity** question under §6a, which makes it **tier C**
(naming), and it is adjacent to W7's C4 findings. Logged for the decision sheet;
**not touched.**
