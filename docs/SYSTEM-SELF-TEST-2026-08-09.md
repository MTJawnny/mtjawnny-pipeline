# DOES THE SYSTEM ACTUALLY WORK?

**A plain-English report. 2026-08-09.**

Captain asked a question that turned out to be the right one:

> *"If the same cure resolves all 21 probe defects, why do issues continue to
> arise? I think we need to figure out if the system works as it stands now
> before analyzing more cards."*

Four things were planned. **Two are done, two are not.** Status is stated
honestly at the end rather than blurred.

---

## THE SHORT ANSWER

**The safety net is real, but it has two holes and one wrong assumption.**

1. **Six of the eight gates genuinely work.** They were broken on purpose and
   they caught it and failed. That is now proven, not assumed.
2. **Two of the eight cannot fail at all.** `definition_drift` and
   `ruling_registry` notice problems and then exit 0. They are *reporters*
   listed as *gates*.
3. **"The same cure" was wrong.** The 21 probe defects have at least four
   different causes, and one slogan cannot prevent four things — which is
   exactly why they keep happening.
4. **The verification hole was much easier to close than anyone thought.**
   Ground truth covered 6.7% of the codebook. The missing 93% was already
   sitting inside the codebook itself.

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
| **`definition_drift`** | definition contradicting its own axis name | ✅ findings 35 → 36 | ❌ **exit 0** |
| **`ruling_registry`** | hid a ruling document | ⚠️ count moved silently | ❌ **exit 0** |

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
| 2 | Widen ground truth past 6.7% | ✅ **built and measured** (2.6× graded) — the 201-candidate triage is **not** done |
| 3 | Install the four missing mechanisms | ❌ **not started** |
| 4 | Re-run recorded findings through corrected probes | ❌ **not started** |

Items 3 and 4 were not attempted rather than attempted badly. Item 3 is the only
one that stops the bleeding instead of measuring it.

---

## RECOMMENDED NEXT, IN ORDER

1. **Make the two reporters into gates** — or move them out of Gate 2 so the
   list stops implying eight failures are possible when six are. Cheapest fix
   on this page: pin `definition_drift`'s findings count to the existing
   ratchet, exactly as conservation and visibility already are.
2. **Build the probe library (item 3).** Make the right call *shorter to write*
   than the wrong one. All three of this session's own probe defects were
   hand-rolled versions of something that should have been an import.
3. **Triage the 201**, then wire `--wide` into the gate. Coverage goes 6.7% →
   ~53% on human-class evidence alone.
4. **Then** item 4, and only then more card analysis.

## THE ONE-SENTENCE VERSION

The system works better than it could prove — six of eight gates are now
verified capable of failing, the verification hole is one flag away from being
8× smaller, and the recurring defect class is recurring for the ordinary reason
that it is the only one guarded by prose instead of by a tool.
