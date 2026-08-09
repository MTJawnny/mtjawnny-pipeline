# SESSION HANDOFF — 2026-08-09

> **STILL CURRENT, with one addition made after it was written.** The **CR
> REFRESH landed later the same day** — `2733326`, `675a58b`, recorded in
> **`docs/CR-REFRESH-2026-08-09.md`**. Nothing on this page is invalidated: the
> codebook was not touched, §2 is still 64 tokens, `unclassified-trigger` is
> still 481, and **0 ability lines moved**. Two numbers on this page are now
> stale by exactly the amount the new CR added — **CR 702 keyword names 193 →
> 194** and **keyword homes 150 → 151** (CR 702.195 Storied). Read §0a of
> `PICK-UP-HERE.md` before touching anything CR-shaped.

Supersedes `SESSION-HANDOFF-2026-08-08.md`. **Zero API calls. Arc spend
unchanged at $90.51 / $140.** 5 commits, `2bcaeb6` .. `1c88930`.

**The session in one line: the audit PICK-UP-HERE §1 demanded was run and
found 4 lines holding a ratified token taken from their EFFECT — then all
five D8a items landed, and every one of the five had a wrong count, a wrong
CR anchor, or a hidden second CR rule in the sheet.**

**D8a IS COMPLETE. §2 goes 58 → 64 tokens. `unclassified-trigger` 534 → 481.
Codebook never mutated.**

---

## 0. START HERE

`docs/SESSION-START-PROCEDURE.md` — five gates, Gate 2 is EIGHT commands.
If no task was given, §6's NEXT WORK ITEM is your instruction. Only two things
need Captain's explicit word: **ratifying new vocabulary** and **mutating the
codebook**.

---

## 1. READING MANIFEST — indexed by TASK

### Always

| | |
|---|---|
| **`python3 experiments/foundry_system_map.py`** | **RUN FIRST.** Generated, cannot go stale |
| **`docs/OUT-OF-SCOPE.md`** | a DECLINE register, not a backlog |
| `docs/SESSION-START-PROCEDURE.md` | five gates |
| `CLAUDE.md` | locked rules + traps — **3 new this session** |
| Gate 2, all eight | live state is measured, never recalled — §3 |

### If you are touching the DELIVERY EXTRACTOR

```
python3 experiments/foundry_prior_art.py <your topic>      # ← FIRST, always
python3 experiments/foundry_routing_regression.py snapshot <before>.json
python3 experiments/foundry_routing_regression.py diff <before> <after> --strict --lines
python3 experiments/foundry_routing_regression.py invariance --strict
python3 experiments/foundry_ground_truth.py                # after EVERY step
```

| read | why |
|---|---|
| **`docs/CODEBOOK-NAMING-GRAMMAR.md` §2** | **six new rows this session.** The DELIVERY law |
| `docs/W3-TRIGGER-VOCABULARY-2026-08-07.md` | the D1–D9 sheet. **D8a is now closed** |
| `docs/W1-W2-RECORD.md` · `docs/AUDIT-5-2026-08-05.md` | the sweep classes |
| `docs/DELIVERY-GAP-CENSUS-2026-08-03.md` | the census |

---

## 2. THE AUDIT — what PICK-UP-HERE §1 asked for, and what it found

**§1's conclusion was right and its stated REASON was wrong.** Measured, not
reasoned:

| | |
|---|--:|
| the six tokens ASSERTED by `foundry_ground_truth.py` | **0 of 6** |
| the six tokens EMITTED on any fixture seed line | **0 of 6** |
| …but `draw-trigger` / `draw-second-card-trigger` head live axes | **4 axes, 16 members** |

So "these tokens have no members" is false for two of six. **The real reason
is narrower and worse: the fixture is only the three seed-bearing move specs
(534 seeds / 15 axes), so a codebook membership without BOTH a `class: human`
seed AND an evidence quote is invisible to ground truth.** 13 of 16 move specs
carry zero seeds. Widening the fixture is a real, cheap, unstarted item.

**All 280 lines were read against their CR rules.** Five of six are clean:

| token | CR | lines | verdict |
|---|---|--:|---|
| `state-trigger` | 603.8 | 50 | **50/50.** CR 603.8's own worked example verified by synthetic test |
| `draw-second-card-trigger` | 121.1 + D3f | 62 | **62/62** |
| `leaves-graveyard-trigger` | 400.1 / 700.4 | 43 | **43/43** |
| `ability-activated-trigger` | 602.1 / 602.2 | 34 | **34/34** |
| `lose-life-trigger` | 119.3 | 20 | **20/20** — no damage line claimed |
| **`draw-trigger`** | 121.1 | 71 | **69/71** |

**A recall probe was run too, not just precision** — 23 trigger lines with a
state-shaped condition that routed elsewhere were read, and all 23 are events
with a stative qualifier inside the OBJECT phrase (`whenever another creature
you control with power 2 or less enters`). Zero recall defects. The
`state-trigger` tail placement is what protects them.

---

## 3. GATE 2 — eight commands, all green

```
lint                clean — 565 axes · 8,740 members · NO MUTATION this session
family sweep        the standing 6 blocking
definition drift    the standing 35
ruling registry     clean (regenerated)
conservation        0 violations · baseline re-pinned 4× ON PURPOSE, see §5
visibility          0 dropped · 0 unscanned · 31 uncontexted · 0 face spans
ground truth        488 / 488 — UNCHANGED THROUGH ALL SIX CHANGES
gate audit          5,676 out · 114 CR members attested only outside · 0 crashes
invariance          0
```

---

## 4. LIVE STATE — measured at handoff

| | |
|---|--:|
| ability lines | 61,383 |
| deliveries | 61,960 |
| **`unclassified-trigger`** | **481** (was 534) |
| **§2 DELIVERY vocabulary** | **64 tokens** (was 58) |
| unrouted lines | **15,430** (was 15,401) |
| keyword homes | 150 — never moved |
| codebook | **565 axes / 8,740 members — UNTOUCHED** |

---

## 5. THE FINDINGS, and the one number that could see each

### 5a. FOUR lines held a ratified token taken from their EFFECT — FIXED

`commit` (CR 700.13) and `unlock` (CR 709.5h) are in **neither** closed
keyword list, so `trigger_clause` walked past the condition and the branch
chain matched a verb in the EFFECT. CR 113.3c. Both added to
`_SUPPLEMENT_VERBS` with CR anchors.

> **MEAT LOCKER PROVES IT ON ONE CARD.** Its two faces print the SAME trigger
> condition. The face whose effect says "draw three cards" got `draw-trigger`;
> the face whose effect carries no listed verb got `unclassified-trigger`.
> One event, two answers, decided by the effect.

**THE DIFF FOUND TWO MORE THAN THE AUDIT COULD.** Reading the six tokens can
only ever find defects *in* the six; two further lines had been handed
`cast-trigger` off "you may CAST spells from your graveyard". **A token-scoped
audit is blind to its own neighbours — the diff is not.**

All four are `ratified → None`: a wrong token replaced by an honest gap. That
is the ratchet's "worse" direction and a correctness improvement.

### 5b. STILL OPEN — a row-level loss on `gain or lose life` (2 lines)

Moonstone Harbinger and Wax-Wane Witness print *"Whenever you gain **or** lose
life during your turn"* and emit **only** `lose-life-trigger`.
`gain-life-trigger` is ratified (88 lines) and is silently dropped.

**Diagnosed, deliberately NOT fixed.** The cause is not a missing list entry:
the splitter cuts `["whenever you gain", "lose life during your turn"]`, and
part 0 has lost the OBJECT that both verbs share. `PREDICATE` then discards
part 1 and the whole line falls back to a single parse. **Adding `lose` to
`PREDICATE` would make it worse** — part 0 would become a bare `whenever you
gain`, which `\bgains? life\b` cannot match either.

This is a **new sweep class: a SHARED OBJECT across two coordinated verbs**,
beside INFLECTION, VOICE and WORD ORDER. It needs a re-join like the
`N or greater` one, not a list addition. 2 lines, real, and it is on the queue
rather than lumped into an audit commit.

### 5c. EVERY ONE OF THE FIVE D8a ITEMS HAD A DEFECTIVE SPECIFICATION

Not one was wrong in a way a line count could show:

| item | the sheet said | measured | what was actually wrong |
|---|---|---|---|
| 1 Room doors | 43 lines | **30** | the class is **TWO CR rules** — 709.5h "unlock this door" (30) and 709.5i "**fully** unlock a Room" (17). Different event, different cards |
| 2 day–night | CR **728.1** | **CR 731** | 728 is **Rad Counters** in the vendored snapshot. Wrong anchor, not CR lag |
| 3 coin flip | 7 | **7** ✓ | but 103 of the 110 `flip` lines are the flip as an EFFECT |
| 4 exile from bf | 12 | **3** | the other 23 print `is exiled` in their effect |
| 5 loses the game | 7 | **7** ✓ | my own first probe said 5 — it required the line to start with when/whenever and lost an ability-word prefix and a compound |

**The pattern: every wrong number came from counting the PHRASE instead of the
EVENT.** CR 113.3c is the cut, and it carried almost the whole population in
three of the five.

### 5d. CR 709.5i IS LEFT AS AN HONEST GAP ON PURPOSE

The 17 "fully unlock a Room" lines are all `Eerie` ability-word cards whose
other half already routes to `any-etb`. CR 709.5i fires on the **second** door
and on **any** Room, not this one. Folding it into `door-unlocked-trigger`
would assert that a Room's own door and a board-wide second-door payoff are
one mechanism — §6b rule 1 forbids it by name. **Whether it earns its own
token is a ratification, on the sheet, not something to mint by widening a
regex.**

**Baseline re-pinned four times, every one deliberate and stated:** once onto
a correctness improvement that reads as degradation (§5a), three times onto
plain improvement as D8a landed.

---

## 6. NEXT WORK ITEM

### A. W4 — the anthem group · 4,375 lines · the biggest remaining slice

`python3 experiments/foundry_shape_extractor.py --gaps`, read the section
headed `INSIDE spell-or-static`. Prior art: `STEP-2A-STATIC-GRANT-2026-08-05.md`,
`-2B-`, `-2C-`. **Named shapes, one at a time. Never a blanket sweep** — but
re-measure the warning first: `foundry_blanket_risk.py` put the 1,883 at 4.

### B. The residual after D8a — `foundry_w3_census.py`, 481 lines

Ranked by DECK-BUILDING RELEVANCE, not line count:

| class | CR | lines | note |
|---|---|--:|---|
| **room-unlock (`fully unlock`)** | 709.5i | 17 | §5d. A ratification, and the case is written |
| plays-a-card | 601.1a / 305.1 | 16 | |
| ring-tempts | 701.54 | 8 | |
| counter-placed / -removed | 122.6 / §8b | 38 | check §8b first — it may already govern |
| **cr701-keyword-action** | 701 | 100 | **belongs to WITHDRAWN D2/D3** |
| **cr702-keyword-event** | 702 | 81 | **belongs to WITHDRAWN D2/D3** |
| **monstrosity · level-up · attach** | — | 44 | **D8b — still BLOCKED** |
| RESIDUAL | — | 95 | genuinely unpartitioned |

### C. Widen the ground-truth fixture — cheap, and §2 is the reason

13 of 16 move specs carry **zero** seeds, so 8,740 codebook members are
graded through 534. Every token ratified since 2026-08-04 sits outside it.

### Then, in order

W5 `escapes with` (12) · W6 family sweep (the standing 6) · W7 definition
drift (the standing 35). **W9 parent layer** is blocked on W8; **W10** on W9.

---

## 7. BLOCKED ON CAPTAIN

**W8, now ten items** — unchanged from 2026-08-08, plus two from this session:

- **CR 709.5i `fully unlock a Room`** (17 lines) — the case is written in §5d.
- **The `gain or lose life` shared-object splitter** (§5b) — a DET fix, but a
  structural one; flagged so it is not attempted as a list addition.

**No new CR-LAG entry.** The day–night anchor was a WRONG SHEET NUMBER, not a
stale snapshot — CR 731 is present and correct. The register still stands at
two: `chorus`, `N or less`.

---

## 8. WHAT THIS SESSION PROVES

**A TOKEN-SCOPED AUDIT IS BLIND TO ITS OWN NEIGHBOURS.** Reading all 280 lines
of the six tokens found 2 defects. The routing diff on the fix found **4** —
the other two had been handed `cast-trigger`, a token outside the audit's
scope, by the identical cause. Read the population; then run the diff and read
that too.

**A SPECIFICATION IS A CARRIED-FORWARD COUNT WITH A CR NUMBER ATTACHED.** All
five D8a items had a defective spec — three wrong counts, one wrong CR rule,
one hidden second CR rule. The rule already in CLAUDE.md ("a carried-forward
count is not a measurement") extends to **the CR anchor and the partition**,
not just the number.

**THE SAME TEST GAVE OPPOSITE ANSWERS AND THAT IS THE TEST WORKING.** D3f
produced ONE token for day–night (every line prints both directions, so a
split yields two axes with identical membership) and TWO for coin flip
(Karplusan Minotaur prints both as separate abilities that do different
things). Decided by the corpus, not by taste.

**A PROBE DEFECT IS STILL THE DEFAULT OUTCOME — one more, mine.** My
`player-loses-game` probe required the line to start with `when`, and so lost
an ability-word prefix ("Burning Chains — When the chosen player…") and a
compound. It reported 5; the truth was 7. Nineteen across five sessions, and
the cure was the same as always: consume what the classifier emits.
