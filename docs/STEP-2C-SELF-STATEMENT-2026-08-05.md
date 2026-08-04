# STEP 2, THIRD SLICE — CR 614.1d, AND THE SELF-REFERENCE STATEMENT (2026-08-05)

**1,448 gap lines closed: 35 `replacement` + 1,413 `static`. Zero regressions,
zero re-routes, zero lines appeared or vanished.** Two named shapes, taken in an
order that is load-bearing. **Zero API calls. No new vocabulary.**

Predecessors: `STEP-2A-STATIC-GRANT-2026-08-05.md` (294) ·
`STEP-2B-STATIC-CONDITION-2026-08-05.md` (443).

---

## 0. THE CARRIED-FORWARD NUMBER WAS WRONG, AND THE SHAPE WAS WRONG TOO

`STEP-2B` §8 named *"the 931-line `this creature …` group"* as the next shape.
That number came out of a session-closing summary and existed nowhere else. It
is **not** what is there:

| | |
|---|--:|
| lines whose body opens with a self-reference | **2,185** |
| …of which are BURN SPELLS (`~ deals 3 damage to any target`) | **738** |

**"The `this creature …` group" is not one shape, and routing it as one would
have marked 738 spell abilities `static`** — the blanket-sweep failure
`PRE-STEP-2-AUDIT` §6 stopped step 2 to prevent, arriving under a different
name. Two things had to be true before any of it could be routed: a CR-derived
cut separating spell abilities from statics, and a prior pass for the
replacement effects hiding inside the population.

## 1. SHAPE A first — CR 614.1d, the general case behind 614.1c's three templates

> **CR 614.1d** — *"Continuous effects that read **'[This permanent]
> enters . . .'** or '[Objects] enter [the battlefield] . . .' are replacement
> effects."*

The branch tested 614.1**c**'s three *named* templates (`enters with` /
`enters as` / `enters tapped`) and lost every other way a card writes the same
shape — **35 lines, in three distinct ways**:

| printed | n | why the hand-list missed it |
|---|--:|---|
| `This creature enters **prepared**.` | 24 | CR 722.3's designation; no 614.1c template exists for it |
| `~ enters **the battlefield** tapped.` | 7 | **`\benters? tapped\b` requires ADJACENCY** — the Gates use pre-2024 wording |
| `~ enters **under the control** of an opponent.` | 4 | Xantcha, Captive Audience, Pendant of Prosperity |

The seven Gates are the instructive ones. `enters tapped` is the single most
common replacement template in Magic, and the test for it could not see
`enters **the battlefield** tapped`. **Same defect class as `enters as` being
tested plural-only** (STEP-2A §2) **and as D5's guessed `{0,60}` window** — a
hand-list, or a hand-chosen distance, standing in for what the CR states
generally. Third instance in three passes; CLAUDE.md's rule that a hand-list is
"a defect with a delay" keeps predicting correctly.

The subject test is **`SELF_NOUN_RX`, derived from the corpus's own type lines**,
not a list of permanent types.

### 1a. 614.1d's SECOND template is NOT taken, and the measurement is why

*"[Objects] enter [the battlefield] . . ."* is not decidable by this shape. Of
15 candidate lines, **exactly one** (Vigorous Farming, *"Lands you control enter
the battlefield untapped"*) is a replacement effect:

| | n | what it actually is |
|---|--:|---|
| Landfall / Trap **INSTANTS** — *"If you had a land enter the battlefield … this turn"* | 9 | the "enter" sits inside a CONDITION; §1's unmarked default |
| **"can't enter" PROHIBITIONS** — Grafdigger's Cage, Worms of the Earth | 5 | continuous effects, but not replacement ones |
| genuine 614.1d | 1 | Vigorous Farming |

Reported, not routed.

## 2. SHAPE B — CR 113.3a is the cut, and it is the whole safety margin

CR 113.3 enumerates **four** ability categories. Three of them have already
declined a line by the time it reaches the tail — loyalty (606), activated
(113.3b), every triggered family (113.3c), plus replacement (614). The fourth is
the one that had to be excluded, and CR 113.3a excludes it by **card type**:

> **CR 113.3a** — *"Spell abilities are abilities that are followed as
> instructions **while an instant or sorcery spell is resolving**."*

**A spell ability can exist only on an instant or sorcery.** So on a card with no
instant/sorcery face, the CR's own enumeration is closed and `static` (113.3d) is
what remains. That is a derivation from the CR's category list — **not a verb
list**, which is what a session reaching for "which verbs sound static" would
have built.

**The two sides are indistinguishable by subject, and separable by type:**

```
Chain of Plasma       ~ deals 3 damage to any target.          -> CR 113.3a, unmarked (§1)
Marang River Prowler  This creature can't block and can't be blocked.  -> CR 113.3d, static
```

**Measured after the cut: ZERO `deals` lines survive on the routable side.** All
**91** surviving verb heads are state predicates — `can't` · `can` · `gets` ·
`has` · `is` / `isn't` · `doesn't` · `must` · `'s power` · `'s toughness` ·
`attacks each combat` · `blocks each combat` · `crews` · `saddles` · `assigns`.
Not one instruction among them.

### 2a. 760 lines are left REPORTED because the face problem is real

A card with **any** instant/sorcery face is disqualified whole. `ability_lines`
joins every face's text into one stream, so a line on the creature half of a
`Creature // Sorcery` is indistinguishable here from a line on the sorcery half.
**Attributing a line to a FACE is a different job than attributing it to a
card**, and it is not this pass's job. The test is deliberately pessimistic in
the direction that cannot mark a spell ability `static`.

### 2b. `escapes with` is HELD OUT — 12 lines, and the CR points elsewhere

Phoenix of Ash: *"This creature **escapes with** a +1/+1 counter on it."* CR
702.138 does not classify it, but CR 113.6h chains it into the replacement
section explicitly:

> **CR 113.6h** — *"An object's ability that modifies how that particular object
> enters the battlefield functions as that object is entering the battlefield.
> **See rule 614.12.**"* — and **CR 614.12** opens *"Some **replacement
> effects** modify how a permanent enters the battlefield."*

So its home is probably `replacement`, not `static`. **That is a third shape and
it gets its own pass.** Sweeping it in here would be the lumping this method
exists to avoid, and 12 lines correctly reported beats 12 lines confidently
wrong.

## 3. RESULT

| | shape A | shape B | total |
|---|--:|--:|--:|
| gap lines closed | 35 → `replacement` | 1,413 → `static` | **1,448** |
| regressions (ratified → None) | 0 | 0 | **0** |
| re-routes (ratified → ratified′) | 0 | 0 | **0** |
| lines appeared / vanished | 0 / 0 | 0 / 0 | 0 / 0 |

| | before | after |
|---|--:|--:|
| `static` | 12,911 | **14,324** |
| `replacement` | 2,355 | **2,390** |
| unrouted | 17,719 | **16,271** |
| `spell-or-static` | 16,630 | **15,182** |
| …permanent-side | 6,380 | **4,932** |
| `routed_lines` | 61,907 | 61,907 **UNCHANGED** |
| `keyword_homes` | 150 | 150 **UNCHANGED** |

Snapshots: `p11-cr614-1d.json` (shape A) · `p12-self-statement.json` (shape B).

## 4. Verification

| gate | result |
|---|---|
| routing diff `--strict`, shape A | 35 moved, all `None` → `replacement` |
| routing diff `--strict`, shape B | 1,413 moved, all `None` → `static` |
| every moved line read | **yes** — 123 lines on the 66 tail heads (n≤6) read exhaustively, the 24 larger heads sampled ≥9 each; no instruction verb found on any head |
| determinism ×2 | **byte-identical** (`0f1a9c10…`) |
| name-invariance | **1** — Storm of Memories, the known harness artifact, unchanged |
| Clue/investigate ground truth | **byte-identical** |
| lint | clean — 565 axes · 359 active · 8,740 members |
| family sweep | 6 blocking, the same 6 |
| definition drift | 35, unchanged |
| Gate 3b prior art | `anthem` returns 8 ruling-bearing lines, all on the `rule:tribal-anthem-buff` **axis-naming** family (batches 4–7, KEEP reconfirmed three times). None rules on DELIVERY. |

## 5. WHAT THIS PASS PROVES

**A named shape can still be the wrong shape.** Steps 2a and 2b both worked
because the name and the population matched. Here the name — *"the `this
creature …` group"* — described a **subject**, and delivery is never decided by
the subject. The population it named was 34% burn spells. **Name the shape by
the CR rule that decides it, not by the words that open the line.**

**The order was load-bearing, exactly as in step 2a.** The 35 CR 614.1d lines
sit *inside* the self-reference population. Had shape B gone first, all 35 would
have been marked `static` — a wrong **ratified** token, which no gap census can
report, and the failure mode the keyword-router fix already produced once
(Unearth's 57 lines on `replacement`). Shape A first is not tidiness.

**Three passes, three hand-lists.** D5's `{0,60}` window, STEP-2A's plural-only
`enters as`, and now 614.1c's three templates read as exhaustive. Each was a
short list standing where the CR states a general rule. CLAUDE.md calls this
"a defect with a delay"; the delay is now measurable at roughly one pass.

## 6. What remains of step 2

**15,182 lines in `spell-or-static`, 4,932 of them permanent-side** — down from
6,821 when step 2 opened, a **28%** reduction across three passes with zero
regressions.

Named and waiting, in the order the evidence supports:

1. **`escapes with`** (12) — §2b above; CR 113.6h → 614.12 is written, needs its pass.
2. **The anthem group** — `creatures you control` (179), `other creatures you control` (78), `each creature you control` (61). The `rule:tribal-anthem-buff` axis has a KEEP ruling reconfirmed in batches 4, 6 and 7, but **nothing rules its DELIVERY**.
3. **`this spell costs …` / `this spell can't …`** — now routed via §2's cut, but worth recording that CR **113.6d** (cost modification functions on the stack) and **113.6g** (can't-be-countered functions on the stack) are what make them statics rather than spell abilities.
4. **The face-attribution job** — 760 lines are unroutable today only because `ability_lines` cannot say which face a line came from. That is a tooling gap with a known fix, and it is the largest single block of deliberately-unrouted lines left.
