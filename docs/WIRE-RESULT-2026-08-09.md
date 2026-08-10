# WIRE RESULT — 2026-08-09

**The measurement `PRODUCT-REALITY-AUDIT-2026-08-09.md` §9.1 asked for.**
Predictions: `docs/WIRE-PREDICTIONS-2026-08-09.md`, committed `d48eb4a`
**before** the harness existed. Harness: `experiments/foundry_wire_experiment.py`
(`88ef26f`). Capability probe: `experiments/foundry_wire_capability.py`.

**Nothing shipped. `tier_engine.py` was not edited.**

---

## 1. THE ANSWER IN ONE PARAGRAPH

**The join is not a no-op, and it is not an improvement. It is a re-rank by
codebook MEMBERSHIP, and at 19.3% coverage membership is not similarity.**
Every predicted-correct neighbour that sits **on** its anchor's axis was
promoted — Farseek +108 places, Corpse Dance +339, Animate Dead into the
displayed list at #2. Every predicted-correct neighbour **not** on the axis was
demoted, **without a single exception across 33 graded cards**. That is not a
coincidence to be tuned away; it is what `tagger_coverage + 0.5 ×
derived_agreement` computes. Since an axis's absent members are the ones nobody
has reviewed yet rather than the ones that don't belong, the join currently
promotes *reviewed* over *similar*.

**It does not meet the bar §5 of the predictions set, and I am not moving the
bar.** Recommendation: **do not land the wire yet** — and the reason is now a
number rather than a hunch, which makes it §9.2's argument, not a dead end.

## 2. WHAT WAS MEASURED

| | |
|---|--:|
| derived index, base | 731 cards, **1** slug (`rule:turn-scoped`) |
| derived index, joined | 6,788 cards, **400** slugs |
| memberships joined | **7,930**, 0 dropped as out-of-corpus |
| axes ≤ `DERIVED_QUALIFY_DF_CEILING` (172) | **390 of 399** — may solo-qualify |

### The two controls came back byte-identical, as predicted

* **Sol Ring** — 0 memberships → identical tiers, identical top-10.
* **Grand Abolisher** — 0 memberships but carries `rule:turn-scoped` today →
  identical. The join does not disturb the one derived tag that already ships.

### The structural prediction held exactly

**Zurgo, Thunder's Decree** sits on `rule:created-token-enters-tapped`, **195
members > the 172 ceiling** → **0 new Tier 3 members**, rank movement only.
`derived_solo_qualifies` was not bypassed.

## 3. THE PER-ANCHOR RESULT, GRADED AGAINST §3

| anchor | axis (DF) | T3 rows | predicted neighbours promoted / demoted |
|---|---|--:|---|
| Rampant Growth | `land-fetch-to-battlefield` (23) | 821 → 823 | **1 / 5** |
| Beast Within | `targeted-destruction` (172) + `compensates-controller-with-token` (17) | 1,616 → 1,664 | **0 / 2** |
| Reanimate | `reanimate-from-graveyard` (62) | 1,225 → 1,229 | **2 / 4** |
| Reliquary Tower | `no-maximum-hand-size` (43) | 378 → 378 | **0 / 0** |
| Zurgo | `created-token-enters-tapped` (195) | 604 → 604 | — |
| Sol Ring · Grand Abolisher | — | unchanged | **controls: identical** |

### 3a. Rampant Growth — the join's best structural moment

The base displayed top-10 was **an alphabetical slice of a 44-row score tie**
(`A-Navigation Orb, Beamsaw Prospector, Bioengineered Future, Biomechan
Engineer, Biotech Specialist, …`). Tier 3 sorts `(-score, name)`, so with one
distinct score in the head the product was showing the alphabet.

The join broke the tie with real signal — 1 → 5 distinct scores — and
**Farseek went T3#114 → T3#6**, into the display. That is a genuine product
improvement and the clearest single win on the panel.

**But the tie was the base engine's defect, not the codebook's achievement.**
Any signal at all would have broken it. And five predicted-correct neighbours
(Three Visits, Into the North, Skyshroud Claim, Explosive Vegetation, Harrow)
were demoted 5–7 places for the sole reason that the 23-member axis does not
list them.

### 3b. Beast Within — a REGRESSION, and the sharpest finding on the page

48 cards entered Tier 3 and the displayed top-10 turned over almost entirely.
Reading every moved row against its oracle text, the base list was **better**:

| left the display | oracle text |
|---|---|
| Emergency Eject | *Destroy target nonland permanent. Its controller creates a Lander token.* |
| Excavation Technique | *Destroy target nonland permanent. Its controller creates two Treasure tokens.* |
| Stroke of Midnight | *Destroy target nonland permanent. Its controller creates a 1/1 white Human token.* |

Those three are **functional twins of Beast Within** — same verb, same target
class, same compensation clause. They fell **#5/#6/#7 → #19/#20/#21**. What
replaced them included `Red Elemental Blast` (*counter target blue spell / destroy
target blue permanent*), `Active Volcano` (*destroy target blue permanent*),
and an **Alchemy duplicate** (`A-Buy Your Silence` at #4, one row above its own
paper twin at #5). `Chaos Warp`, a predicted-correct neighbour, went **T3#1 →
T3#12** — out of the display.

**The cause is precision, not coverage.** `rule:targeted-destruction` holds 172
members and means "destroys something"; the base engine's verbatim fragment
*"Destroy target nonland permanent. Its controller creates"* is a **finer**
discriminator than the axis that outranked it. A broad axis is a worse signal
than the text it displaces.

**And it qualified by a margin of exactly zero.** DF = **172**, the ceiling is
**172**. One more member and none of this would have happened. The worst-behaved
axis on the panel is the one that passed Lesson 3's gate by nothing at all.

### 3c. Reanimate — a net WIN, and it was the predicted best case

Prediction §3C called this the join's best case because Animate Dead and
Necromancy are Auras sharing almost no verbatim text with Reanimate's sorcery
template. It landed:

* **Animate Dead T3#11 → T3#2** — into the display.
* **Corpse Dance T3#371 → T3#32** — the largest single promotion measured.
* Persist, Helping Hand, Profane Command entered the display; four weak rows
  (Ghastly Conscription, Shadow of the Enemy, Monster Mash-Up, King Narfi's
  Betrayal) left it.

**The loss is the finding.** `Dance of the Dead` went **T3#3 → T3#56** and
`Unearth` / `Recommission` **#10/#9 → #62/#61**. Dance of the Dead is *the
near-twin of Animate Dead* — the two cards print the same Aura template — and:

> **`rule:reanimate-from-graveyard` contains Animate Dead and does NOT contain
> Dance of the Dead.**

The engine ranked the twins #11 and #3. The codebook promoted one to #2 and
buried the other at #56, purely on membership. **This is a concrete codebook
membership defect that only the wire could have exposed** — no audit in the
repo compares the codebook against the delivery classifier or against
similarity, which is §7 of the product audit showing up as a third symptom.

### 3d. Reliquary Tower — the redundancy probe, confirmed exactly

`rule:no-maximum-hand-size` has **4/4 recall** on the predicted neighbours —
the best on the panel — and produced **zero** Tier 3 movement, because all four
print the identical sentence *"You have no maximum hand size"* and the engine
**already reaches every one at Tier 2**.

Which surfaces a different bug entirely: they sit at **T2#313, #447, #618,
#660** of 702 rows. The four most obviously correct answers are buried 300+
rows deep in a tier the join is forbidden to touch. **For this anchor the
product's problem is Tier 2 rank, and no amount of codebook wiring reaches it.**

## 4. THE MECHANISM, STATED SO IT ISN'T RE-DERIVED

Displacement was **uniform**: at Beast Within every non-member fell by exactly
13–14 places; at Reanimate by exactly 52–53. That is the count of members
inserted above them. The derived term does not *rank* — it **partitions**, and
the partition is `is a member` / `is not yet a member`.

Recall of each axis against the hand-named correct families:

| axis | members | predicted-correct on it |
|---|--:|---|
| `land-fetch-to-battlefield` | 23 | **3 / 11** |
| `targeted-destruction` | 172 | **1 / 5** |
| `compensates-controller-with-token` | 17 | **2 / 5** |
| `reanimate-from-graveyard` | 62 | **3 / 8** |
| `no-maximum-hand-size` | 43 | **4 / 4** |
| **total** | | **13 / 33 — 39%** |

**39% recall, and the one axis at 100% is the one whose members already share
verbatim text.** That is the whole result: the join helps where the codebook is
complete, and the codebook is complete exactly where the engine did not need
help.

## 5. GRADED AGAINST THE BAR SET IN ADVANCE (§5 of the predictions)

| criterion | verdict |
|---|---|
| 1. an anchor gains a **named-correct** neighbour it could not reach before | **FAIL.** Every named neighbour was already present in some tier. Animate Dead was promoted (#11 → #2), not gained. |
| 2. no anchor **loses** a correct neighbour | **FAIL.** Chaos Warp #1 → #12; Dance of the Dead #3 → #56; Unearth #10 → #62 — all out of what ships. |
| 3. the controls come back byte-identical | **PASS.** |

**One of three. The wire does not land today.**

And §4's own prediction was **half wrong, so it is recorded as wrong**: I
predicted a near-no-op caused by **redundancy**. Redundancy was real and
exactly located (§3d), but the dominant effect was **displacement**, which I
did not predict at all. The measurement wins.

## 6. WHAT THIS BUYS — three things a foundry session could not have found

1. **The codebook is not wired, and it is also not READY to be wired.** The
   audit assumed one missing wire. There are two problems and only one is a
   wire.
2. **A concrete membership defect** (`Animate Dead` in, `Dance of the Dead`
   out) found by the wire and invisible to all twelve Gate 2 checks.
3. **A ranking defect in the shipped engine, unrelated to the codebook**:
   Rampant Growth's displayed list was an alphabetical slice of a 44-row tie.
   That is a live product bug in `tier_engine` today, at 19.3% coverage or 100%.

## 7. RECOMMENDATION

**Do not land the wire. Take §9.2 next, for a reason that is now measured.**

The blocker is coverage and axis recall, not plumbing — the plumbing is one
call site and it works. `A15-VOCAB-01` gates the full-corpus pass that raises
coverage; this measurement is the argument for unblocking it.

Two things worth doing regardless of the wire, both cheap:

* **The 44-row alphabetical tie is a shipped bug.** It needs a tie-break, and
  that is a ratified-constant question for Captain, not a tuning knob.
* **88 Alchemy (`A-`) memberships sit on 51 active axes, and 48 of them are
  duplicate pairs with their own paper twin on the same axis.** They inflate
  every axis DF — which feeds `idf` *and* the 172 ceiling — and they duplicate
  displayed rows, against the ratified *"paper rows preferred over A- variants
  in sampling, resolution and emit"*.

**Re-run this measurement after coverage moves.** It is one command, it needs no
API spend, and it now has a committed prediction set to be graded against:

```
python3 experiments/foundry_wire_capability.py
python3 experiments/foundry_wire_experiment.py --json
```

## 8. DECISION SHEET — three items, one sheet

Presented together per the standing rule (*"pending ratifications go in ONE
decision sheet, not one question per token"*). **None blocks §9.2**; all three
are consequences of the measurement rather than prerequisites for it.

### D-W-1 — the Tier 3 tie-break *(a scoring constant → Captain)*

Tier 3 sorts `(-score, name)`. Rampant Growth's shipped displayed top-10 is an
alphabetical slice of a **44-row score tie**, headed by an `A-` Alchemy variant.
This is live today at 19.3% coverage and does not improve as coverage rises —
more members produce *more* ties at the same coverage score, not fewer.

**Every scoring constant is a ratified ruling, not a tuning knob**, so I have
not picked one. The candidate tie-breakers already exist as ratified facts
elsewhere in the engine — `ci_relation_step`, `abs(mv_delta)` (already the
Tier 1/2 tie-break), and the ratified paper-over-`A-` preference.
**Recommendation: reuse the Tier 1/2 tie-break rather than mint a new term** —
it is already ratified and already ordering the other tiers.

### D-W-2 — `rule:reanimate-from-graveyard` is missing Dance of the Dead *(a codebook mutation → Captain)*

The axis holds **Animate Dead** and not **Dance of the Dead**, which prints the
same Aura template. The wire promoted the first to #2 and buried the second at
#56 on that difference alone.

**Not proposed as a fix yet, on purpose.** *"Before proposing a mutation,
measure whether the thing is broken"* — one missing member found by one anchor
is a sample of one, and the honest next step is to measure the axis's recall
against its own CR-anchored definition before touching it. It is recorded here
so it is not lost, and because it is evidence for D-W-3's shape: **membership
gaps are the failure mode, and nothing in the repo audits for them.**

### D-W-3 — 88 Alchemy memberships, 48 of them duplicate pairs *(a codebook mutation → Captain)*

`A-` rebalance cards sit on **51 active axes**; in **48 cases both the `A-`
variant and its paper twin are members of the same axis**. They inflate every
affected axis's DF, which feeds `idf` **and** `DERIVED_QUALIFY_DF_CEILING`, and
they duplicate rows in any displayed list (`A-Buy Your Silence` ranked one place
above `Buy Your Silence`).

The ratified rule already exists — *"paper rows preferred over A- (Alchemy)
variants in sampling, resolution, and emit"* — so this is applying a standing
ruling, not making a new one. **But it is still a codebook mutation** and rides
the backup law: `foundry_membership_move.py` with a declared spec, backup →
`--dry-run` → read the conservation line → execute → re-run `foundry_gate2.py`
**expecting it to find something**.

**Measure the blast radius first.** `rule:targeted-destruction` sits at DF=172
against a ceiling of 172; removing Alchemy duplicates *lowers* DFs, which can
push an axis **under** the ceiling and newly enable solo-qualification. A
cleanup that looks like hygiene can change what qualifies.
