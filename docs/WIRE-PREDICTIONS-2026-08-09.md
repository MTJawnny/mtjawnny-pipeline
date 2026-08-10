# WIRE EXPERIMENT — PREDICTIONS, WRITTEN BEFORE THE RUN

**This file is committed BEFORE the measurement harness runs, on purpose.**
The instruction it satisfies: *"Pick anchors whose correct neighbours you can
state in advance and write them down BEFORE running, or you will grade the
result on whatever it produces."*

Nothing in this file may be edited after the first run of
`experiments/foundry_wire_experiment.py`. Corrections go in the RESULT
document, quoting the prediction they overturn.

---

## 0. WHAT IS BEING TESTED

`PRODUCT-REALITY-AUDIT-2026-08-09.md` §9.1: wire `codebook.json`'s memberships
into `tier_engine`'s `rule:`-namespace-only derived index, and measure whether
the 7,930 memberships improve neighbours.

**The wire point is exactly one call**, `tier_engine.py:8018`:

```python
card_tags_t3, idf_t3, df_t3 = build_turn_scoped_tag_index(...)
```

whose own docstring already names this as the intended growth path:

> *"Step 5 grows this SAME dict with more `rule:`-tag members as new
> derivations land; nothing else about this function's shape changes when that
> happens."*

**The join is measured OFFLINE.** No shipped artifact changes in this step, and
`tier_engine.py` is not edited.

## 1. WHAT THE JOIN CAN AND CANNOT REACH — structural, before any anchor

Three properties of the existing scoring function bound the result. They are
read out of the code, not assumed:

1. **`derived_agreement` is ANCHOR-DIRECTIONAL** (`tier3_score`). An anchor
   carrying zero `rule:` tags gives every candidate `derived_agreement == 0.0`.
   *The join cannot move an uncovered anchor's list at all.*
2. **The derived term is Tier-3-only.** The module docstring: injected into
   *"Tier 3's anchor-directional tag-overlap computation ONLY … deliberately
   NOT fed into Tier 1/2's rank `tag_score` term."* So the join can only change
   **Tier 3 membership and Tier 3 order** — never Tier 0/1/2.
3. **`DERIVED_QUALIFY_DF_CEILING = 172`** (`derived_solo_qualifies`, ratified
   2026-07-17). A shared `rule:` tag whose corpus DF exceeds 172 may contribute
   to score but may **not** solo-qualify a candidate into Tier 3.

## 2. MEASURED BEFORE THE PREDICTIONS — capability, not grade

`experiments/foundry_wire_capability.py`, re-derived this session:

| | |
|---|--:|
| active axes | 403 |
| memberships | 7,930 |
| distinct cards covered | 6,275 of 32,557 gated — **19.3%** |
| **median axis size** | **4 members** |
| axes with ≤4 members | **205 of 403**, holding 376 memberships |
| axes with ≥100 members | 15, holding 3,641 memberships |

**Of the 9 anchors in `experiments/anchors.txt`, 8 carry zero memberships** —
including all six Captain-approved calibration anchors. Verified against
*every* axis status, not just `active`. So the panel the engine is calibrated
on cannot be moved by this join in either direction.

That is a capability fact about the scoring function, so measuring it first
does not contaminate what follows. It is also the reason the anchors below are
drawn from the covered 6,275 rather than from `anchors.txt`.

## 3. THE ANCHORS AND THEIR PREDICTED CORRECT NEIGHBOURS

Neighbours named from Magic knowledge, before any run. "Correct" means: a
player asking *"what plays like this?"* should be shown this card.

### A. Rampant Growth — `rule:land-fetch-to-battlefield`
Correct: **Farseek · Nature's Lore · Three Visits · Into the North · Search for
Tomorrow · Wood Elves · Sakura-Tribe Elder · Skyshroud Claim · Explosive
Vegetation · Harrow · Solemn Simulacrum.**
*Prediction:* the spell half of that list shares the literal string *"Search
your library for a basic land card"*, so **tier_engine already reaches them at
Tier 1/2 without the codebook**. The join's only unique contribution would be
the differently-worded ones — Wood Elves, Sakura-Tribe Elder, Solemn Simulacrum.

### B. Beast Within — `rule:targeted-destruction` + `rule:compensates-controller-with-token`
Correct: **Generous Gift · Rapid Hybridization · Pongify · Chaos Warp ·
Reality Shift.**
*Prediction:* Generous Gift is near-verbatim and is already Tier 1/2.
`rule:targeted-destruction` holds **172 members** — exactly at the ceiling — so
it is the sharpest available test of `derived_solo_qualifies`.

### C. Reanimate — `rule:reanimate-from-graveyard`
Correct: **Animate Dead · Necromancy · Exhume · Dance of the Dead · Stitch
Together · Victimize · Corpse Dance · Life // Death.**
*Prediction:* **this is the join's best case on the whole panel.** Animate Dead
and Necromancy are Auras and share almost no verbatim text with Reanimate's
sorcery template, so Tier 1/2 cannot reach them. If the codebook is worth
wiring, it shows up here.

### D. Reliquary Tower — `rule:no-maximum-hand-size`
Correct: **Thought Vessel · Venser's Journal · Spellbook · Kruphix, God of
Horizons.**
*Prediction:* every one prints the identical sentence *"You have no maximum
hand size"* → already Tier 1. Join adds nothing. Included as a **redundancy
probe**, not because I expect a gain.

### E. Zurgo, Thunder's Decree — `rule:created-token-enters-tapped` (195 members)
*Prediction, structural and falsifiable:* **195 > 172, so no candidate may
solo-qualify on this axis.** Expect **zero new Tier 3 members** and rank
movement only among candidates that already qualified. If new members appear,
the harness has bypassed `derived_solo_qualifies` and is wrong.

### F. Sol Ring — CONTROL, 0 memberships
*Prediction:* **byte-identical output.** Any change means the harness is broken.

### G. Grand Abolisher — CONTROL 2, 0 memberships but **carries `rule:turn-scoped` today**
*Prediction:* **byte-identical output.** Isolates that the join does not
disturb the one derived tag that already ships.

## 4. THE PREDICTION I EXPECT TO BE GRADED ON

Stated plainly so it cannot be retrofitted:

> **I expect the join to be close to a no-op on neighbour quality, and I expect
> the reason to be REDUNDANCY, not sparseness** — that the codebook's axes
> mostly group cards which share templated verbatim text, which `tier_engine`
> already reaches at Tier 1/2 for free. Anchor C (Reanimate) is the case where
> I expect a genuine, visible gain, and D is where I expect a measurable
> zero.

If the measurement disagrees with this, **the measurement wins** and the result
document says so in those words.

## 5. WHAT WOULD MAKE THIS WIRE WORTH LANDING

Decided in advance, so the bar is not moved afterwards:

1. At least one anchor gains a **correct** Tier 3 neighbour it could not reach
   before, named in §3 above — not merely "a new row appeared".
2. No anchor **loses** a correct neighbour.
3. The controls (F, G) come back byte-identical.

Failing (1) is the honest negative result the audit says is worth a session,
and it gets written up exactly as loudly as a success would be.
