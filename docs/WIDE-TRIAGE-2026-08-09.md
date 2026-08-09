# TRIAGE OF THE 201 — what opening positive correctness actually found

**2026-08-09. Nothing fixed here; this is the partition and the verdicts.**

`foundry_ground_truth.py --wide` grades 1,276 assignments instead of 488 and
reports **201 mismatches + 55 unanchored**. The headline number was never the
finding — the partition is.

**One confirmed pipeline defect, 136 corpus lines. Everything else is fixture
or naming.**

---

## THE PARTITION

| # | class | cases | what it is | verdict |
|---|---|--:|---|---|
| 1 | **`landfall` claims a land's OWN etb** | 15 seeds → **136 corpus lines** | **REAL EXTRACTOR DEFECT** | ✅ **FIXED** |
| 2 | `etb` axis, `replacement` delivery | 60 | naming: `etb` used colloquially | ruling |
| 3 | quote anchored to the WRONG line | ~50 | fixture defect | fix the fixture |
| 4 | §2a prefix imprecision | 13 | `death-trigger` vs `any-death-trigger` | naming |
| 5 | spell ability on an `activated-` axis | 13 | membership vs §1 | read |

---

## 1. THE ONE REAL DEFECT — `landfall` is eating land ETBs

```python
re.search(r"\bland (you control )?enters\b", clause)
```

*"When **this land enters**"* matches `land enters`. So a land's **own** ETB
trigger is classified as **landfall**.

The CR keeps these apart cleanly:

- **Landfall** (CR 207.2c ability word) — *"Whenever a land you control
  enters"*. Fires on **every** land, repeatedly, including other lands.
- **`When this land enters`** — an ETB trigger of that permanent (CR 603.6a).
  Fires **once**, for itself.

Khalni Garden triggers once when it enters. Lotus Cobra triggers every time any
land enters. They are not the same mechanism, and 136 lines currently say they
are.

| `landfall` population | lines |
|---|--:|
| **SELF etb, misrouted** | **136 (40%)** |
| real landfall | 204 |

Sample misrouted: A.I.M. Labs, Abraded Bluffs, Adventurer's Inn, Aether Hub,
Akoum Refuge, Archway Commons — the entire "gain 1 life when it enters"
dual-land cycle.

**This is the payoff of the whole exercise.** No routing diff could see it (the
lines have carried a ratified token since before the first snapshot), no
conservation or visibility audit could see it, and `--strict` scores it as
settled. Only positive correctness finds a token that has been wrong from the
beginning.

**The fix is DET and small** — exclude the self-reference subject, which the
extractor already canonicalizes to `~`. It needs the full recipe: routing diff
`--strict --lines`, read all 136 moved lines, four audits.

---

## 2. `etb` MEANS TWO THINGS (60 cases) — naming, not routing

`rule:etb-copy-your-permanent`, `rule:etb-plus1-counter-on-target-creature`,
`rule:etb-with-counters`. Their lines read:

> *"You may have this creature **enter as a copy** of an artifact or creature"*
> *"Mikaeus **enters with** X +1/+1 counters on it"*

Those are **CR 614.1c replacement effects**, and the extractor routes them to
`replacement` — **correctly**. The axis name uses `etb` in the colloquial sense
*"on entering"*, while §2's `etb` is a DELIVERY token meaning *an ETB
triggered ability*.

**Same shape as the synonym collisions**: one string, two meanings. It is the
mirror of `lifegain`/`gain-life` — there, two names for one mechanic; here, one
name for two.

Not a defect in either the axis or the extractor. It is a **ratification**:
either the token or the prefix has to give.

---

## 3. THE QUOTE ANCHORED TO THE WRONG LINE (~50) — fixture, not pipeline

The seeds carry a card + an axis + a quote, and `anchor_line` takes the first
ability line containing the quote. On multi-ability cards that is often not the
line the axis is about:

| card | axis claims | quote landed on |
|---|---|---|
| Monk Class | `etb-bounce-target-creature` | *"When this Class becomes level 2…"* |
| Yotia Declares War | `etb-create-token` | a Saga chapter, *"I — Create a 0/2…"* |
| Kavaron, Memorial World | `etb-create-token` | an activated ability |
| Tempt with Bunnies | `etb-create-token-creature` | a modal mode line |

**The pipeline is right in every one.** The fixture picked the wrong line.

**Fix is mechanical:** when several lines contain the quote, prefer the one
whose delivery matches the axis's claim, and report the ambiguity rather than
silently taking the first. That is a fixture change, not a routing change — and
it must be reported, because "prefer the line that agrees with me" is a
grading rule that can hide a real mismatch if applied carelessly.

---

## 4 & 5. TWO SMALL NAMING/MEMBERSHIP CLASSES

**§2a prefix imprecision (13).** *"Whenever **equipped creature** dies"* routes
to `any-death-trigger` — correctly, since the dying creature is not the source
Equipment. The axis says `death-trigger` (unprefixed = the source itself). The
extractor is right; the slug is imprecise.

**Spell on an `activated-` axis (13).** Seismic Spike — *"Destroy target land.
Add {R}{R}"* — is a **sorcery** on `rule:activated-destroy-target-land`. §1
says a spell ability OMITS delivery (CR 113.3a), so either the membership or
the slug head is wrong. Needs a read, not a rule.

---

## WHAT THIS CHANGES ABOUT `--wide`

**It should not be wired into the gate yet, and 201 was never the number.**
After class 3 is fixed (fixture) and class 1 is fixed (extractor), the residual
is naming work that belongs to Captain, not to a gate.

**Order:** fix class 1 (real defect, 136 lines) → fix class 3 (fixture) →
re-run `--wide` → then decide the gate.


---

## UPDATE — class 1 is FIXED (same day)

136 lines re-routed `landfall` → `etb`. `landfall` 340 → 204; `etb` 5,176 →
5,312. Gate 2 green, all 11 rows.

**The guard is `SELF_NOUN_RX`**, built from CR 205.2a's closed card-type list,
not a hand-written `this land` — so it covers every card type and stays correct
if CR 205 gains one.

### The first version of the fix was WRONG, and reading all 137 lines is what caught it

Version 1 asked *"does the clause contain a self-reference?"* and moved **137**
lines. One of them was **Field of the Dead** — *"Whenever **this land or
another land you control** enters"* — the archetypal landfall payoff card. A
compound subject contains a self-reference **and** a landfall subject, so the
bare test got it exactly backwards and deleted the card the token exists for.

**The routing diff reported that line identically to the 136 correct ones.**
`ratified → ratified'` with no way to tell a fix from a regression. Only reading
them separated the two.

**Version 2 strips the self-reference and asks whether a landfall subject
remains** — derived, not listed:

```
"this land"                              -> ""                              not landfall
"this land or another land you control"  -> "another land you control ..."  landfall
```

### Effect on the fixture

| | before | after |
|---|--:|--:|
| `--wide` mismatches | 201 | **186** |
| passing | 1,075 | **1,090** |

Remaining classes are 2–5: naming rulings and fixture anchoring, none of them a
pipeline defect.


---

## UPDATE 2 — the 55 "broken quotes" were not broken

**Captain authorised repairing all 55. Measuring first showed 54 needed no
repair, so 54 were not touched.**

| where the quote actually lives | |
|---|--:|
| verbatim in RAW oracle text | **54 of 55** |
| …inside parentheses — **CR 207.2a reminder text** | 31 |
| in neither (a real defect) | **1** |

`strip_reminder` removes reminder text — **19.2% of every oracle character** —
so a quote taken from it can never match an ability line. **Mire's Malice** is
the worked case: its ratified quote is the *awaken* reminder, its printed line
is `Awaken 3—{5}{B}`. Quote correct, membership correct, and the two could
never meet because the fixture only ever saw the stripped view.

I had reported this as *"a Captain-ratified evidence quote no longer matches
the corpus"* — i.e. as drift needing 55 repairs. **That was wrong.** It is the
recorded trap *"an audit's boundary is upstream of something"*, aimed at this
file: the fixture's boundary sat downstream of the reminder strip.

**Fix:** `anchor_line` now falls back to the raw oracle paragraph and maps it
back to its ability line **through the extractor's own `strip_reminder`**,
never by index — a line that is pure reminder text strips to nothing and would
shift every index after it. **Unanchored 55 → 1.**

### The one real defect, repaired

**Blizzard Specter.** Its quote transcribed the em-dash as `--` and the bullet
as `*` — the ASCII-for-Unicode trap, same family as the recorded curly-vs-
straight apostrophe. It also spanned two ability lines.

Repaired to the single mode line — `• That player returns a permanent they
control to its owner's hand.` — which inherits `combat-damage-to-player` by D3
and so proves **both** the delivery and the `forced-owner-bounce` effect on one
line, satisfying *"evidence must prove its own axis"*.

Executed through `foundry_membership_move.py` under the backup law: timestamped
backup verified by readback, determinism ×2 byte-identical, member conservation
8,740 → 8,740, active axes 359 → 359.

### Where `--wide` stands

| | at triage | now |
|---|--:|--:|
| unanchored | 55 | **0** |
| mismatches | 201 | **89** |
| passing | 1,075 | **1,092** |

The 89 are real codebook errors (51 triggered abilities on `activated-` axes,
11 Saga chapters, 4 modes). They stay fatal.


---

## UPDATE 3 — `--wide` IS GATED, on a ratchet

**The 89 could not be a precondition, and measuring showed why:**
`rule:<actual-delivery>-<same tail>` exists for **0 of 89**. Every one needs a
NEW AXIS or a DROP — a ratification, not a fix. Waiting for that would keep
**1,181 graded assertions ungated indefinitely**.

So `--wide` gates the way the rest of Gate 2 already does: **any rise in
mismatches or unanchored is fatal; any fall is reported and accepted only with
an explicit `--update-baseline`.** The backlog can shrink and cannot grow.

| | |
|---|--:|
| pinned `mismatch` | 89 |
| pinned `unanchored` | **0** |
| pinned `graded` / `passed` | 1,181 / 1,092 |
| pinned `head_ambiguous` (CR 614.1c, needs a ruling) | 60 |

**The narrow gate stays ABSOLUTE-ZERO** — 488 seeds that have reproduced
exactly through every change this session. Loosening a proven invariant into a
ratchet would trade it for a backlog; only the fixture that *carries* a backlog
gates on movement.

Negative-controlled: pinning mismatch at 88 and re-running gives
`88 → 89 in the WORSE direction`, **exit 1**. Gate 2 is now **12 rows**.

---

## STILL NEEDS CAPTAIN — the two that are genuinely ratifications

**1. The 89 memberships.** Cards sitting on an axis whose delivery they do not
have. Verified real by reading: Booby Trap, Entangling Trap, Frostfist Strider,
Summon: Shiva, Nazahn and Dungeon Geists are all on
`rule:activated-…` and **none of them has an activated ability at all** — their
effect arrives by ETB, attack trigger, Saga chapter or clash. `rule:activated-
tap-target-creature` is 25 correct against 7 wrong, so the AXIS is right and
the memberships are not.

Each needs a new axis (`rule:etb-tap-target-creature`, …) or a drop. **35 axes
affected.**

**2. The `etb` prefix (60 seeds, 38 axes).** §2's `etb` is an ETB TRIGGER;
`etb-with-counters` and `etb-copy-your-permanent` mean "on entering" and route
to `replacement` (CR 614.1c). One string, two meanings. Either the token or the
prefix gives.


---

## UPDATE 4 — the 89 re-read. Captain was right: 27 already had homes.

**Captain: *"I read them myself and it would be surprising if they didn't
already have homes."* Correct, and my "0 of 89 have a home" was an
over-narrow-filter defect** — I searched only for the exact string
`rule:<actual-delivery>-<same tail>`. Guard D exists for precisely this and I
did not use it on my own search.

### The honest partition of the 89

| | | |
|---|--:|---|
| **A** | **27** | **§2a PREFIX ONLY — the card is already on the right axis** |
| B | 59 | a genuinely different delivery — needs a home |
| C | 3 | no delivery at all (spell / unrouted) |

### Class A is resolved, by §1's own stated law

§1 already governs this for the SCOPE slot: *"Omitted when the axis's `scope=`
field carries it **and no sibling differs only by scope**; REQUIRED the moment
a scope-sibling exists."* §2a's `any-`/`other-`/`source-` prefix is the same
kind of slot — so an axis omitting it is **not** asserting the SOURCE form, it
is leaving the slot unspecified.

**Measured: for all 27, no prefixed sibling axis exists.** Sigiled Sword of
Valeron (*"whenever EQUIPPED CREATURE attacks, create a 2/2"*) delivers
`any-attack-trigger` on `rule:attack-trigger-create-token`, an axis with no
`any-` sibling. **The card was always on the right axis; the grader was
over-strict.**

The sibling test is what keeps it honest: the moment
`rule:any-attack-trigger-create-token` is ratified, the unprefixed name means
SOURCE-ONLY again and this stops applying.

| | before | after |
|---|--:|--:|
| mismatches | 89 | **62** |
| passing | 1,092 | **1,119** |

Baseline re-pinned onto improvement. Gate 2 green, 12 rows.

### What the remaining 62 are

**59 + 3 that genuinely have no home.** They need 50-odd new axes, most of them
singletons — `rule:etb-tap-target-creature` (2), `rule:chapter-trigger-create-
token` (4), `rule:any-death-trigger-token-creation` (4)… Verified real by
reading: Booby Trap, Frostfist Strider, Summon: Shiva, Nazahn and Dungeon
Geists sit on `rule:activated-…` and **none has an activated ability** — the
effect arrives by ETB, attack trigger, Saga chapter or clash.

**Captain's gain/lose precedent applies to a subset**: a card whose ability
carries two events joins BOTH single-event axes and a new compound axis. That
is membership-is-not-exclusive, already ratified. It does not cover the cards
here whose delivery is simply a different single event.

**This is new vocabulary — ~50 axes — and stays a ratification.**
