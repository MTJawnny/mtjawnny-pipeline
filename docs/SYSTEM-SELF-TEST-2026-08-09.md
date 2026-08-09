# DOES THE SYSTEM ACTUALLY WORK?

**A plain-English report. 2026-08-09.**

Captain asked a question that turned out to be the right one:

> *"If the same cure resolves all 21 probe defects, why do issues continue to
> arise? I think we need to figure out if the system works as it stands now
> before analyzing more cards."*

Four things were planned. **All four are done.** Items 3 and 4 were added in a
second pass; §5 and §6 cover them.

---

## THE SHORT ANSWER

**The safety net is real, but it has two holes and one wrong assumption.**

1. **Six of the eight gates genuinely work.** They were broken on purpose and
   they caught it and failed. That is now proven, not assumed.
2. ~~**Two of the eight cannot fail at all.**~~ **FIXED — see §7.** They were
   *reporters* listed as *gates*; both now ratchet and both are
   negative-controlled. **All eight of the original gates can now fail.**
3. **"The same cure" was wrong.** The 21 probe defects have at least four
   different causes, and one slogan cannot prevent four things — which is
   exactly why they keep happening.
4. **The verification hole was much easier to close than anyone thought.**
   Ground truth covered 6.7% of the codebook. The missing 93% was already
   sitting inside the codebook itself.
5. **Probe defects now have a tool** (`foundry_probe.py`, 10/10 negative-
   controlled), and its sibling immediately found **two wrong counts inside
   ratified §2 law** — both written this session, both from my own probes.

---

## 1. THE EIGHT GATES — broken on purpose, one at a time

Every gate was fed a realistic, deliberately injected defect. The question was
not "does it run" but **"can it fail?"**

| gate | injected defect | did it NOTICE? | did it FAIL? |
|---|---|---|---|
| `codebook lint` | blanked a member's assertions; duplicated a member | ✅ named both exactly | ✅ exit 1 |
| `family_sweep` | deleted a live axis a ratified family needs | ✅ blocking 6 → 7 | ✅ exit 1 |
| `conservation` | made the reminder-strip delete text mid-line | ✅ **2,836 violations** | ✅ exit 1 |
| `visibility` | dropped modal bullets | ✅ uncontexted 31 → 1,963 | ✅ exit 1 |
| `ground_truth` | broke keyword recognition | ✅ 304 seeds failed by name | ✅ exit 1 |
| `gate_audit` | made the extractor raise on a card | ✅ stopped loudly | ✅ exit 1 |
| `definition_drift` | definition contradicting its own axis name | ✅ findings 35 → 36 | ✅ **exit 1** — *fixed, see §7* |
| `ruling_registry` | hid a ruling document | ✅ 3 metrics moved | ✅ **exit 1** — *fixed, see §7* |

### The good news is better than expected

`conservation` deserves a specific mention. CLAUDE.md claims its test A *"would
have caught the 2026-08-04 hyphen disaster without knowing what an ability word
is."* **That claim is now verified** — the injected mid-line deletion produced
2,836 conservation violations from the law itself, not merely a moved baseline
number.

### The two holes

**`definition_drift` detects and does not gate.** Contradict an axis definition
and findings go 35 → 36 — and the tool exits 0. In CI, a brand-new drift finding
passes silently. There is also no pinned baseline on the findings count, unlike
conservation and visibility, so nothing at all reacts to 35 → 36.

**`ruling_registry` does not react.** Hiding a sole-home ruling document moved
its own numbers (sole-home 43 → 44) and produced no complaint and no failure. A
ruling document could be deleted and nothing would say so.

**Neither is broken.** Both do useful work. They are simply *listed in Gate 2
as though they were gates*, and they are not. Two of the eight commands a
session runs to "verify live state" cannot report a failure.

### The finding that answers Captain's question

**Three of the eight negative controls were aimed at the wrong thing, and all
three initially read as "this gate is broken."**

- `definition_drift` — aimed twice at axes where the relevant check (`C1a`)
  structurally cannot fire. Only reading the source showed why.
- `family_sweep` — aimed at an arbitrary axis instead of one a ratified family
  actually references.

Had the report been written after the first run, it would have claimed two
working gates were dead. **Even a session deliberately being careful, whose
entire assignment was rigour, mis-aimed 37% of its probes.**

---

## 2. THE VERIFICATION HOLE — and it was mostly self-inflicted

`foundry_ground_truth.py` is the only check that asks *"is this token RIGHT?"*
Everything else asks did-it-change, did-it-get-lost, does-it-depend-on-the-name.

It graded **534 of 7,930 active members — 6.7%.**

**The other 93% was already there.** `moves/*.json` carries 534 quoted seeds,
but only 3 of its 16 spec files contain a `seeds` block at all — the rest are
renames, merges and scope edits. Meanwhile `codebook.json` carries the *same
evidence shape* on its own members:

> **4,194 `class: human` assertions with a verbatim quote, across 355 active
> axes.**

Those are Captain-ratified assignments with exactly the two properties the
checker needs. Grading them requires **no new ratification — only reading them.**

| | seeds | graded |
|---|--:|--:|
| narrow (unchanged, still the gate) | 534 | 488 |
| `--wide` | 4,210 | **1,276** — 2.6× |

`--wide` is behind a flag on purpose: the pinned 488 must stay comparable, and a
fixture 8× larger must not silently redefine "green."

### What it found, stated carefully

`--wide` reports **201 mismatches and 55 unanchored quotes**. These are **triage
candidates, not 201 defects** — and the shape says so. `rule:etb-with-counters`
scores 0/61, which is the known signature of a systematic mis-grade (`rule:cycling`
scored 0/304 and `rule:typecycling` 0/91 for exactly that reason; both were
fixture defects, both recorded in that file).

Three distinct causes are already visible:

| cause | example |
|---|---|
| **Anchoring** | Booby Trap's quote matched a *different* ability line than its axis claims |
| **Boundary B1** | Acidic Sliver *grants* `{2}, Sacrifice: …` to all Slivers — the line is a `static` grant, the axis claims `activated`. B1 is implemented for KEYWORD claims and not for DELIVERY claims |
| **Naming** | Seismic Spike (*"Destroy target land. Add {R}{R}"*) is a **sorcery** sitting on `rule:activated-destroy-target-land`. Per §1 a spell ability omits DELIVERY, so either the membership or the slug head is over-read |

Opening positive correctness for the first time is *supposed* to produce a
queue. This is that queue.

---

## 3. WHY THE "CURE" NEVER CURED ANYTHING

**Because it was never one cure, and it was never a mechanism.**

The 21 probe defects have at least **four** distinct causes:

| cause | what actually happened | what would prevent it |
|---|---|---|
| **A. Re-implementation** | wrote a private version of something the pipeline already computes | call a shared function |
| **B. Assumed vocabulary** | guessed `retired`/`dropped`; the live values are `renamed`/`killed`/`merged` | halt when a value isn't in the live domain |
| **C. Overlapping classes** | a `non-ASCII` class silently re-measured em-dash, bullet and apostrophe | assert class disjointness |
| **D. Over-narrow filter** | required a line to start with `when`, losing an ability-word prefix and a compound | a known-positive fixture the probe must capture |

Compressing four causes into one memorable sentence is *itself* the failure. A
cure stated at the wrong altitude is a label applied after the fact.

### And the pattern across the whole project is unambiguous

| defect class | what it got | still recurring? |
|---|---|---|
| re-deciding a ruled slug | a tool (Gate 3) | no |
| rediscovering prior art | a tool (Gate 3b) | no |
| silent text loss | a tool (conservation) | no |
| unreachable options | a tool (visibility) | no |
| wrong-since-forever tokens | a tool (ground truth) | no |
| baseline drift | a tool (the ratchet) | no |
| **probe defects** | **a paragraph** | **21 and counting** |

**Every class that got a tool stopped. The only class that never got one is the
only one still recurring.**

Harder evidence still: `foundry_prior_art.py --orphans` already measures cause A.
It reported **4 consumers use the ratified preprocessing, 19 bypass it** on
2026-08-04. Re-run today: **still 4 and 19.** Five days, no movement, because it
reports and does not enforce. Its own closing line says *"every such
re-implementation is where the defects lived."*

### The structural reason

A probe is **written once, run once, thrown away.** It never enters CI, gets no
baseline, gets no negative control, is never re-run. Every audit here verifies
the *pipeline*. **Nothing verifies the instrument.**

---

## 4. WHAT IS AND ISN'T DONE

| # | item | status |
|---|---|---|
| 1 | Negative-control the eight gates | ✅ **done** — 6 pass, 2 cannot fail |
| 2 | Widen ground truth past 6.7% | ✅ **built and measured** (2.6× graded) — the 201-candidate triage remains |
| 3 | Install the four missing mechanisms | ✅ **done** — `foundry_probe.py`, 10/10 self-test |
| 4 | Re-run recorded findings through corrected probes | ✅ **done** — and it found 2 wrong counts in ratified law |

---

## 5. ITEM 3 — the mechanism probe defects never had

`experiments/foundry_probe.py`. Four causes, four guards, **each halting rather
than warning** — a warned-about probe defect is the state of the last five
sessions.

| guard | closes | what it does |
|---|---|---|
| `corpus()` / `rows()` / `longest_match()` | **A** re-implementation | one canonical stand-up; yields tokens as *strings*, closing the `kw in [(tok,desc)]` defect that scored a correct family 0/304 |
| `domain()` / `vocab()` / `active_axes()` | **B** assumed vocabulary | halts on a value the live data does not contain |
| `assert_disjoint()` | **C** overlapping classes | halts when two patterns claim the same sample |
| `must_capture()` | **D** over-narrow filter | halts when a known-positive is missed |

**It is negative-controlled against itself** — the finding from §1, applied to
the new tool before anything trusts it. `python3 experiments/foundry_probe.py`
runs 10 cases: every guard is shown to pass on correct input *and* to halt on
the real recorded defect. **10/10.**

Two of this session's own defects are now reproduced and caught by it: the
`^When` filter (guard D) and the guessed `retired`/`dropped` status (guard B).

Verified against the live corpus, not just its own fixture: 61,383 lines,
`door-unlocked-trigger` 30, `state-trigger` 50, active axes 359, §2 tokens 64 —
every number matches the independently measured value.

**The point is not that it exists. It is that it is shorter to use than to
hand-roll**, which is the only thing that has ever worked here.

---

## 6. ITEM 4 — "most were caught before their numbers were used" was false

`experiments/foundry_recorded_numbers.py` re-derives every line/card count that
grammar **§2** claims, from the live corpus. §2 specifically, because a stale
number in a handoff is a note — **a wrong number in §2 is a wrong premise inside
the document the extractor parses its vocabulary from at run time.**

It found two, **both from this session, both mine:**

| §2 row | claimed | live |
|---|---|---|
| `player-loses-game-trigger` | 5 lines / 5 cards | **7 / 7** |
| `coin-flip-won-trigger` | 6 lines / 5 cards | **6 / 6** |

The first is the `^When` filter defect. The routing diff corrected the *routing*
that day — **nobody corrected the number**, and it went into ratified law. That
is the precise failure mode item 4 was hypothesised to catch, caught on the
first run.

Both rows are corrected, and the `player-loses-game-trigger` row now records
*why* it was wrong so the correction cannot be re-derived as a fresh error.

**Coverage stated honestly:** 7 of 64 §2 rows carry a machine-checkable count.
The other 57 assert no count at all — that is a gap in the rows, not a pass.
`--strict` exits 1 on drift, so it is gateable.

---

## RECOMMENDED NEXT, IN ORDER

1. **Make the two reporters into gates** — or move them out of Gate 2 so the
   list stops implying eight failures are possible when six are. Cheapest fix:
   pin `definition_drift`'s findings count to the existing ratchet, exactly as
   conservation and visibility already are. **Still open.**
2. **Triage the 201 `--wide` candidates**, then wire `--wide` into the gate.
   Coverage goes 6.7% → ~53% on human-class evidence alone. **Still open.**
3. **Add a count to the other 57 §2 rows** so item 4's checker can see them.
   Today it can check 7 of 64.
4. **Then** more card analysis.

## THE ONE-SENTENCE VERSION

The system works better than it could prove — six of eight gates are now
verified capable of failing, the verification hole is one flag away from being
8× smaller, and the one recurring defect class was recurring for the ordinary
reason that it was the only one guarded by prose instead of by a tool. **It now
has a tool, and the first thing that tool's sibling did was find two wrong
numbers inside ratified law.**


---

## 7. THE TWO HOLES ARE CLOSED (added later the same day)

Both former reporters now ride the **existing** ratchet
(`foundry_audit_baseline.py`) — not a second mechanism, and not a tolerance
band, which would be the tuning knob the engine rules forbid. Any movement in
the worse direction is fatal; better-direction movement needs an explicit
`--update-baseline`.

| check | pinned metrics | negative control | result |
|---|--:|---|---|
| `definition_drift` | 8 | a definition contradicting its own axis name | **exit 1** — `findings 35 → 36 in the WORSE direction` |
| `ruling_registry` | 5 | hid a sole-home ruling document | **exit 1** — `documents 120→119`, `corroborated 84→83`, `sole_home 43→44` |

Both pass again once the injection is reverted, which is the half of a negative
control that is easy to skip.

**Two defects were found in the wiring itself, both worth recording:**

- `findings` and `sole_home` were in **no direction set**, so a rise would have
  scored as neutral "change" rather than a regression — the gate would have
  been pinned and still unable to fail. Same shape as the recorded `_direction`
  leaf-key defect, one layer out.
- `ruling_registry`'s `documents` was pinned as a **descriptive string**
  (`"120 documents under docs/"`). Equality worked, but any real change would
  have reached `b - a` on two strings and **raised instead of reporting**.
  Pinned as the integer it was describing.

**Gate 2 is now ten commands and every one of them can fail.**


---

## 8. GATE 2 IS ONE COMMAND, AND EVERY ROW IS NEGATIVE-CONTROLLED

`python3 experiments/foundry_gate2.py` — eleven checks, one exit code.

**Why a runner at all.** Gate 2 was a *list* of shell commands a session was
trusted to run in full. That is the same shape as every failure measured on
this page: **a control that depends on someone remembering is not a control**,
and a skipped gate is indistinguishable from a passing one in a transcript.

It re-implements nothing — each row shells out to the real tool, so there is
one definition of every gate and the runner cannot drift from it.

| verified exit path | |
|---|---|
| rigged failure (`--selftest`) | **1** |
| clean subset | **0** |
| known-failing (`family_sweep`, W6), excused | **0** |
| same, with `--strict-all` | **1** |
| unknown gate name | **2** |

**Every row has now been shown capable of failing**, including the two added
today:

| check | injected defect | result |
|---|---|---|
| `probe_guards` | 11 guard cases, each rigged | halts on all |
| `recorded_numbers` | changed a §2 count 30 → 31 | **exit 1**, names the drifted row, and reports RED through the runner |

The known-failing row is **named, not silently excused** — `family_sweep`'s 6
blocking findings are W6 and predate the runner.

### The scorecard, end of day

| | start of day | now |
|---|---|---|
| gates that can fail | 6 of 8 | **11 of 11** |
| Gate 2 invocation | 8 commands, skippable | **1 command** |
| probe defects with a mechanism | 0 | **4 guards, self-tested** |
| §2 counts machine-checked | 0 | 7 of 64 (and gated) |
| positive-correctness coverage | 6.7% | 6.7% gated, **~53% available behind `--wide`** |
