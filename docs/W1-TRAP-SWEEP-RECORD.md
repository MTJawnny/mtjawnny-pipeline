# W1 — TRAP SWEEP: the record

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
