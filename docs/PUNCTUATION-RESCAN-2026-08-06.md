# PUNCTUATION RESCAN — DID ANYTHING GET LOST? (2026-08-06)

Captain, 2026-08-06: *"we'll need to rescan the corpus with the new punctuation
rulings to make sure nothing got lost."*

**Answer: nothing was lost. Zero conservation violations across 61,383 ability
lines.** The rescan also found **two recall gaps**, both **pre-existing** and
neither caused by the ability-word pass (`98af57a`), and it corrected **two
carried-forward numbers**, one of which was my own probe's.

Tool: `experiments/foundry_punctuation_audit.py` — DET, zero tokens, exits 1 on
any violation. Safe to gate on.

---

## 1. Why a gap census could not answer this question

A census reports shapes with **no ratified token**. A line that was silently
truncated, dropped, or never emitted looks to a census exactly like a shape the
corpus does not contain. So every test here is a **conservation** test — it
asserts that what went in came back out — plus one recall inversion, which is
the only method that sees an absence.

The rulings under test all cut a line on punctuation, and each can lose an
ability by cutting in the wrong place:

| ruling | the cut | how it loses |
|---|---|---|
| CR 207.2c / 207.2d | the em-dash prefix | strips into the ability |
| CR 113.2c | paragraph = ability | merges two abilities |
| CR 603.11 / 607.2h | sentence split on `.` `!` | drops the second ability |
| CR 603.12 | reflexive "when you do" | splits one ability into two |
| CR 700.2 | modal header + bullets | modes inherit nothing |

## 2. Conservation — the result

| test | asserts | result |
|---|---|--:|
| **A — text** | the strip removes a **prefix or nothing**; the body is always a *suffix* of the input | **0 violations** / 61,383 lines |
| **B — sentence** | `sentence_spans` reassembles to its input, character for character | **0 violations** |
| **C — ability** | every ability line yields **≥1** delivery | **0 lines yielding zero** |

Test A is the one that matters most, and it is deliberately **ignorant of
ability words**: a strip that deletes from the *middle* of a line is wrong
whatever its regex intended. It would have caught the 2026-08-04 hyphen
disaster (`"When Spider-Ham enters"` → `"Ham enters"`, 556 lines mutilated) on
the day it landed, without knowing what an ability word is.

Live totals: **61,383** ability lines · **2,306** prefixes stripped · **61,946**
deliveries emitted · **561** lines yielding >1 · **38** linked abilities.

## 3. Recall inversion — what is over-represented among UNROUTED lines

Corpus unrouted rate **16,153 / 61,383 = 0.263**. Ratio > 1 means the class is
worse than the corpus.

| class | lines | unrouted | rate | ratio | verdict |
|---|--:|--:|--:|--:|---|
| bullet (modal mode) | 1,791 | 1,269 | 0.709 | **2.69** | §4 — 1,011 explained, 258 a known gap |
| terminal `!` | 86 | 53 | 0.616 | **2.34** | §5 — **real defect**, 46 lines |
| terminal `?` | 2 | 1 | 0.500 | 1.90 | n=2 |
| multi-sentence | 10,202 | 3,656 | 0.358 | 1.36 | spells; composition |
| em-dash prefix | 4,037 | 1,423 | 0.352 | 1.34 | §6 — **fully explained** |
| ellipsis | 3 | 1 | 0.333 | 1.27 | n=3 |
| digit | 25,372 | 6,989 | 0.275 | 1.05 | at base rate |
| non-ASCII letter | 33 | 7 | 0.212 | 0.81 | §7 — my probe was wrong |
| quote | 1,297 | 227 | 0.175 | 0.67 | better than base |
| comma | 27,144 | 4,672 | 0.172 | 0.65 | better than base |
| colon | 11,041 | 52 | 0.005 | 0.02 | activated; near-total recall |
| semicolon | 34 | 0 | 0.000 | 0.00 | D8 closed it |

## 4. The bullet class — 1,011 explained, 258 a known gap RE-MEASURED

**1,011 of the 1,269** unrouted bullets sit under a modal header that is itself
unrouted — a modal **instant or sorcery**, whose header is a spell ability and
correctly reaches `spell-or-static` by CR 113.3a. A mode inherits its header's
delivery (D3); inheriting "no ratified token" is the right answer, not a loss.

The other **258** sit under a header `_MODAL_HEADER_RE` does not detect.

### The cause is one anchor

```
_MODAL_HEADER_RE = choose (?:one|two|three|one or more|up to \w+)\b.*—\s*$
```

It requires the line to **end** in an em-dash. **CR 700.2 does not:**

> *"A spell or ability is modal if it has two or more options in a bulleted
> list preceded by instructions for a player to **choose a number of those
> options**."*

Modality is defined by the bulleted list plus the choose instruction. Every miss
is a header whose **sentence continues** past the mode count:

| header | n |
|---|--:|
| `Choose three. You may choose the same mode more than once.` | 13 |
| `Choose one. If you control a commander as you cast this spell, you may choose both…` | 13 |
| `Choose one. If this spell was cast using teamwork, choose both instead.` | 5 |
| `Choose one. If this spell was kicked, choose any number instead.` | 3 |
| `An opponent chooses one —` | 3 |
| `Choose X.` · `Choose five.` · `Choose one. If an opponent has eight or more cards…` | 1 each |

### RE-MEASURED, and the standing number is low

Blocked sheet item 5 carries **"49 lines / 19 cards"**.

| | measured 2026-08-06 |
|---|--:|
| undetected headers | **102** |
| bullets beneath them | **259** (258 unrouted) |
| cards affected | **102** |

**Boundary, per Gate 4:** I counted every non-bullet line *immediately followed
by a bullet* that `_MODAL_HEADER_RE` misses. That is an **upper bound on the
shape**, not a claim that all 102 are CR 700.2 modal — `Tiered` (6) and
`As this enchantment enters, choose Khans or Dragons.` (5) are a tier bar and a
choice-on-ETB, not modes. The clearly-modal subset is ~45 headers. The honest
statement is **45 certain, 102 candidate**, against a recorded 49.

**Still Captain's call, unchanged.** `_MODAL_HEADER_RE` is part of the ratified
DET preprocessing standard v1 and is shared with `det_scan_texts()`; widening it
is a change to ratified law, not a DET fix. Nothing here was touched.

## 5. NEW DEFECT — `Start your engines!`, 46 lines, and the CR settles it

The `!` class is 2.34× over-represented, and **46 of its 53 unrouted lines are
one keyword**:

```
Start your engines!        46 lines, all → spell-or-static
```

`start your engines!` **is** in `CR_KEYWORD_NAMES` (CR 702.179) but has **no
entry in `KEYWORD_HOME`**, so §2b never gives it a delivery. The CR states the
class outright:

> **CR 702.179a** — *"**Start your engines! is a static ability.** If a player
> controls a permanent with start your engines! and that player has no speed,
> their speed becomes 1. This is a state-based action."*

### Why the fallback missed it

`build_keyword_homes` falls back to the CR-stated class only when
`effective_classes(kw) == ["static"]`. For 702.179 it returns
**`['static', 'triggered']`**, because the parser swept in CR 702.179d:

> *"There is an inherent triggered ability associated with a player having 1 or
> more speed. **This ability has no source** and is controlled by that player."*

**An ability with NO SOURCE is not the keyword's ability.** 702.179a names the
keyword's class; 702.179d describes a rule of the game that exists whether or
not any permanent has the keyword. The class parse conflated them.

**Not caused by this session** — verified against the pre-change snapshot:
46 lines unrouted before, 46 after.

**Not fixed here, deliberately.** It belongs to the 43-keywords-with-no-home
population (`escape`, `flashback`, `evoke`, `buyback`, `companion`, `partner`,
`visit`, `awaken`, …), most of which are alternative costs where "no single
home" may be correct. It touches `foundry_cr702_classes.effective_classes`,
moves the pinned `keyword_homes = 150` guard, and is a stage-4 vocabulary
question, not a stage-2 punctuation one. **One vector at a time.** Filed as the
next candidate with its CR anchor already established.

## 6. The em-dash class is FULLY explained — every bucket is a correct refusal

1,423 unrouted lines carry an em-dash prefix, and every one is accounted for:

| n | bucket | correct? |
|--:|---|---|
| 416 | modal header (CR 700.2) → `spell-or-static` | ✔ a modal spell's header is a spell ability (CR 113.3a) |
| 268 | **ability word stripped**, body unrouted | ✔ `Addendum — If you cast this spell during your main phase…` is a spell |
| 251 | **flavor word stripped**, body unrouted | ✔ `Animal May-Ham — Other Spiders, Boars…` is the anthem group, step 2's next slice |
| 167 | `{TK}…` tier bars | ✔ refused as a cost (CR 601.2b) |
| 72 | die-roll rows `1—9 \|`, `10—19 \|` | ✔ refused (CR 706.3b) |
| 39 | spree `+ {1} —` | ✔ refused as a cost |
| 7 | `Awaken 4—{4}{W}` | ✔ refused (CR 702.Na) |

The 1.34 ratio is **composition, not recall**: an em-dash prefix is
over-represented on spells and on the un-ratified anthem group. In the two
buckets where the strip *did* fire (519 lines), it fired correctly and the body
is unrouted for reasons that have nothing to do with punctuation.

## 7. My own probe was a finding — a probe that overlaps another probe

The first run scored `non-ASCII letter` at **6,342 lines, ratio 1.55**, and I
nearly reported it. The class was `[^\x00-\x7f]`, which matches the **em-dash**,
the **bullet** and the **curly apostrophe** — so it was silently re-measuring
three classes already in the table and reporting their correlation as its own
finding. Restricted to actual letters: **33 lines, ratio 0.81.**

**New trap: a probe whose class overlaps another class in the same table
reports a correlation as a finding.** Cousin of *"a measurement probe must
consume the same preprocessing as the classifier it measures"* — there the
probe disagreed with the classifier; here it agreed with itself twice.

## 8. Verdict

**Nothing got lost.** Text, sentences and abilities all conserve at 100% across
61,383 lines. The punctuation rulings cut where they say they cut.

| open item | owner | measured |
|---|---|--:|
| `_MODAL_HEADER_RE` widening (CR 700.2) | **Captain** — ratified standard | 45 certain / 102 candidate headers, 258 bullets |
| `start your engines!` has no home (CR 702.179a) | DET, next pass | 46 lines |
| the other 42 homeless CR 702 keywords | needs a ruling | unmeasured |
