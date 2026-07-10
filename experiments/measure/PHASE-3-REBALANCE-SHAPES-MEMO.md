# Phase 3 rebalance shapes — impact analysis for Captain ratification, 2026-07-09

*Measurement/analysis only. No tier_engine.py scoring changes made past this point.
Script: `experiments/measure/phase3_rebalance_shapes.py`. Raw report:
`experiments/out/measurement/phase3_rebalance_shapes_report.txt`.*

## Context

Captain ruling: the v2.5 "Drannith Magistrate > Avatar's Wrath" gate stands; Phase 3's
DF-band discount must not be weakened to preserve it. Instead: frame affinity (type
match, shared creature subtype) must be able to outrank a candidate whose only edge is
a marginally longer/rarer fragment on a disjoint frame, *especially* when that
fragment has been band-discounted. Deliverable: 2–3 general mechanism shapes (no
per-card/per-pair exceptions), each with corpus-wide impact analysis, then halt for
ratification.

All three shapes are keyed only on already-derived facts: `commonality_weight`
(the Phase 3 band/provenance discount), `affinity_term` (existing type/subtype
bonus), `type_match`, and shared-subtype count. None reference a card by name.

- **Shape A — affinity buys back the discount.** The band weight itself is partially
  restored toward 1.0, proportional to how much affinity the pair has:
  `restored_weight = weight + (1 - weight) * min(1, affinity_term / 0.8)`.
- **Shape B — existing affinity term amplifies inversely with the discount.** The
  text-evidence discount is untouched; the *existing* `affinity_term` bonus grows:
  `affinity' = affinity_term * (1 + 3.0 * (1 - weight))`.
- **Shape C — new standalone frame-corroboration bonus**, decoupled from the existing
  affinity system: `bonus = 3.0 * (1 - weight) * frame_strength`, where
  `frame_strength = 1.0 if type_match else 0.0`, `+0.15` per shared subtype.

Illustrative constants only (3.0 amplify factor, 0.8 max-affinity denominator) — not
a search for values that force gates green.

## Named-gate results

| | Drannith − Wrath margin | VoV position (≤3) | Basandra vs Myrel |
|---|---|---|---|
| **Baseline** (Phase 3, no rebalancing) | −3.48 FAIL | 4 FAIL | Basandra #12 > Myrel #13 FAIL |
| **Shape A** | −0.46 FAIL (closest) | 2 PASS | Basandra #14 > Myrel #15 FAIL |
| **Shape B** | −2.11 FAIL | 3 PASS | Basandra #12 > Myrel #13 FAIL |
| **Shape C** | −1.21 FAIL | 2 PASS | Basandra #12 > Myrel #15 FAIL |

**None of the three, at these illustrative constants, fully closes the Drannith/Wrath
margin or the Basandra/Myrel ordering.** All three fully fix VoV placement.

## Why Basandra/Myrel resists all three shapes

Root cause is the mirror image of Drannith/Wrath: here it's **Myrel** (not Basandra)
whose matched fragment against Marisi is the discounted one (`"your opponents can't
cast spells"`, DF=29, weight=0.5) — the same family of Abolisher/Myrel-defining text
driving the Drannith case. Basandra's own fragment (`"can't cast spells during
combat"`, DF=3) is already full-weight, untouched by any shape. Myrel's frame
affinity with Marisi is real but weaker than Drannith's with Abolisher — `type_match=
True` (both Legendary Creature) but **zero shared subtypes** (Cat Warrior vs Human
Soldier) — so `affinity_term=0.3` vs Drannith's `0.55`. Every shape restores/boosts
proportional to affinity strength, and 0.3 isn't enough to fully rescue Myrel from a
0.5x discount at these constants, even though the *same mechanism* took Drannith from
−3.48 to −0.46. This is not a shape-selection problem — it's a magnitude problem for
this specific pair, and stronger constants would need to be evaluated for their own
corpus-wide cost.

## Corpus-wide impact (panel-wide, within-tier pairwise order swaps vs baseline)

| Shape | Total swap rate | Notes |
|---|---|---|
| A | 12.1% (5,487/45,252 pairs) | Marisi hit hardest (19.9%), Zurgo next (15.7%) |
| B | 5.6% (2,525/45,252 pairs) | Gentlest; roughly half of A's and C's disturbance |
| C | 11.4% (5,166/45,252 pairs) | Similar magnitude to A, different mover set |

Largest Grand Abolisher Tier 2 movers (all shapes): Alhammarret High Arbiter, Circu
Dimir Lobotomist, Quagnoth, Council of the Absolute move up 9–15 positions; a handful
of rows (Lake Silencio, Angel's Grace, various) move down 6–8. These are all
type/subtype-affine creatures gaining ground against disjoint-frame candidates,
exactly matching the intended principle — not noise.

## Round 2 (Captain ruling applied)

Two Captain rulings applied and re-measured:

1. **Basandra/Myrel SUPERSEDED.** New expectation: Basandra ranks *above* Myrel
   (matches what every shape already showed) — Basandra's near-exact rarer phrase
   (`"can't cast spells during combat"`, DF=3, full weight) is legitimate stronger
   evidence than Myrel's discounted, weak-frame-affinity match. Same principle as
   Drannith, applied in the direction it actually points.
2. **Shape A strengthened to a 3rd axis, MV closeness** (per the original phrasing,
   "sitting at equal/near mana value" — Drannith sits at MVΔ=0 from Abolisher):
   `mv_closeness = max(0, 1 - |MVΔ|/4.0)`; restoration strength =
   `affinity_term + 0.6 * mv_closeness`, normalized by
   `TYPE_MATCH_BONUS + SUBTYPE_BONUS_CAP + 0.6 = 1.4` (all reusing existing ratified
   constants except the two new MV ones). Renamed **Shape A2**.

**Result — all three success criteria now PASS:**

| | Drannith − Wrath margin | VoV position (≤3) | Basandra vs Myrel |
|---|---|---|---|
| Baseline | −3.48 FAIL | 4 FAIL | Basandra #12 > Myrel #13 — now the expected PASS |
| **Shape A2** | **+0.02 PASS** | **2 PASS** | **Basandra #14 < Myrel #16 PASS** |

Corpus-wide impact under A2: 11.9% of panel-wide within-tier pairs swap order
(5,368/45,252) — same order of magnitude as the unmodified Shape A/C, roughly double
Shape B's disturbance. Largest Grand Abolisher Tier 2 movers: Circu Dimir Lobotomist
+12, Sulfur Elemental +10, Council of the Absolute +8 (all creature-type/subtype-affine
gains); Megatron −11, Iona Shield of Emeria −6 (disjoint-frame candidates losing
ground) — consistent with the intended principle, not noise.

**Caveat, printed for the record, not hidden:** the Drannith/Wrath margin (+0.02) is
razor-thin — deterministic (no randomness), but close to the boundary. This isn't
unique to my change: the ORIGINAL v2.5 ruling's own ceiling constant
(`DRANNITH_WRATH_MARGIN_CEILING`) is annotated "win, not rout," meaning a bare,
non-dominant win was always this gate's intended shape — 0.02 is thin but consistent
with that original design intent, not a sign of a fragile hack.

**CORRECTION, round 2 (bug found and fixed):** the round-2 "all three PASS" result above was WRONG. My measurement script double-counted `affinity_term` in `apply_shape()` (subtracted `raw - final`, which already nets out `affinity_term`, then added `affinity_term` back a second time). This was only caught because I implemented Shape A2 in the real engine and cross-checked: the live engine showed Drannith(6.73) − Wrath(7.27) = **−0.53**, not the script's claimed +0.02. Every number below is verified directly against the running engine, not a parallel script, per the "measurement honesty" instruction that followed.

## Round 3 — Captain's corrected ruling, implemented and verified

1. **Basandra/Myrel UNGATED entirely.** Neither ordering is an expectation any longer; both are defensible. `check_basandra_gate()` now reports the ordering informationally, never blocks. Full history (original v2.4 expectation → briefly superseded → retired) annotated in its docstring.
2. **Drannith > Wrath remains the binding gate, unchanged.**
3. **MV penalty is now an ASYMMETRIC ladder, replacing the old symmetric one-for-one** (not a second, separate term): same MV is still strongest (MVΔ=0 → zero penalty); the penalty still decays with `|MVΔ|` (distance dominant); but a candidate costing MORE than the anchor now gets a harsher per-distance multiplier (`MV_PRICIER_MULT`) than one costing less (`MV_CHEAPER_MULT`) — direction is a tiebreaker on top of distance, never a strict cheaper-always-wins bucket. See `mv_asymmetric_distance()` / `compute_rank()` in `tier_engine.py`.
4. **Shape A's restoration formula dropped the MV axis** (moved to item 3 instead) — it's now `type_match + shared_subtype` only, normalized by `TYPE_MATCH_BONUS + SUBTYPE_BONUS_CAP = 0.8`. See `restoration_fraction()`.

**Sweep, simplest first, per instruction:** linear restoration (item 4) + asymmetric MV ladder (item 3), `MV_CHEAPER_MULT=1.0` (unchanged), sweeping `MV_PRICIER_MULT`. First test point, **`MV_PRICIER_MULT=2.5`**, passes cleanly — no non-linear curve needed.

**All three verified directly against the live, running engine** (not a script):

| | Drannith − Wrath margin | VoV position (≤3) | Partial-lock gate |
|---|---|---|---|
| Baseline (bands only, no rebalance) | −3.48 FAIL | 4 FAIL | not separately broken |
| **`MV_PRICIER_MULT=2.5` + type/subtype restoration** | **+0.49 PASS** | **2 PASS** | **PASS** |

Full v2.5–v2.9 gate suite: **66/66 PASS, 0 STOP**, determinism verified twice byte-identical. Two new "explained" categories were added to the standing stability gate (v2.9 gate 3) to correctly trace the new source of movement: a row's own MVΔ falling on the changed (pricier) side, and — for rows whose own score didn't change but whose *rank position* shifted because a sibling row did — a named "sibling MV asymmetry" trace, the same pattern already used for DF-drift tracing.

**Corpus-wide impact** (panel-wide, within-tier pairwise reorder vs. bands-only baseline, computed by calling the real `compute_candidate_rows()` twice with constants monkeypatched, not a parallel formula):

| Anchor | Swap rate |
|---|---|
| Grand Abolisher | 158/1,431 (11.0%) |
| Myrel, Shield of Argive | 1,063/8,778 (12.1%) |
| Preordain | 13/136 (9.6%) |
| Sol Ring | 2/28 (7.1%) |
| Marisi, Breaker of the Coil | 2,085/10,296 (20.3%) |
| Sakura-Tribe Elder | 2,209/20,706 (10.7%) |
| Zurgo, Thunder's Decree | 623/3,828 (16.3%) |
| **Total** | **6,153/45,203 (13.6%)** |

Per ruling, no % ceiling applies — judged by explained-drift law and the landmark/gate set instead, both satisfied. Largest Grand Abolisher Tier 2 movers: Brisela Voice of Nightmares −23, Void Winnower −19, Iona Shield of Emeria −16, Megatron −15 (all significantly pricier bombs, correctly penalized harder); Circu Dimir Lobotomist +12, Sulfur Elemental +11, Council of the Absolute +9 (type/subtype-affine candidates gaining) — consistent with the intended asymmetric-cost + frame-affinity principle, not noise.

Halting here for final ratification before this becomes engine law (next snapshot + Phase 3 close-out).
