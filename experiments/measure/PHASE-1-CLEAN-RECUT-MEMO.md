# Phase 1 — clean-data re-cut (provenance-segregated), 2026-07-09

*Read-only, per RULING-MANIFEST-2026-07-09.md Phase 1. No engine changes. Working
tree verified at Snapshot Zero (tag `tier-engine-v2.9e2-baseline`, commit `8cb70df`)
before this ran. Script: `experiments/measure/clean_recut.py`. Raw tables:
`experiments/out/measurement/clean_recut_report.txt` /
`clean_recut_raw.json` (gitignored, regenerate below). Run twice, byte-identical
stdout and JSON both times.*

```
python3 experiments/measure/clean_recut.py
```

## Method

`df_distributions.py`'s Deliverable 1 (T1 paragraphs) pooled native and
M2-injected paragraph occurrences together into one undifferentiated
population. This pass classifies every one of the corpus's 38,645 distinct
`matchable_paragraph` texts by inspecting **every** corpus-wide occurrence of
that exact text: **native-only** (37,570 texts — zero M2-injected
occurrences anywhere), **M2-injected-only** (1,063 texts), or **mixed** (12
texts — carries both a native occurrence on one card and an M2-injected
occurrence on another; same overlap class as the Hero-of-Bladehold case,
ratified BY DESIGN in the v2.9 erratum note, not a defect). Two fresh tables
are then built from the native-only bucket only, split by R2's length rule:

- **Native-only T1 LONG** (>=5 tok, `ngram_scale_df` — T2's existing scale):
  2,865 distinct texts. p50=4, p90=19, p95=32, p99=72, p99.9=158, p100=308.
- **Native-only T1 SHORT** (<5 tok, `para_exact_df`, own metric): 303
  distinct texts. p50=3, p90=17, p95=38, p99=270, p99.9=451, p100=451.

(The native-only T2 fragment table is already produced by
`df_distributions.py`'s existing native/injected/mixed 5-gram segmentation —
not rebuilt here.)

## Landmark placement (R3 provisional edges: 10/50/172 long, 5/39 short)

**Short boilerplate (native-only short table):**

| Landmark | para_exact_df | Band | Verdict |
|---|---|---|---|
| `draw a card.` | 270 | DEAD | wanted (dead) |
| `this land enters tapped.` | 440 | DEAD | wanted (dead) |
| `choose one —` (Boros Charm) | 330 | DEAD | wanted (dead) |
| `{t}: add {c}.` | 451 | DEAD | wanted (dead) |
| `{t}: add {c}{c}.` (printed for the record, R1 Phase 1 instruction) | **19** | DISCOUNTED | n/a — record only |

**Long M2-injected boilerplate (checked against the long edges; not part of
the native-only population by construction, since these texts exist *only*
as injected reminders):**

| Landmark | ngram_scale_df | Band | Verdict |
|---|---|---|---|
| Swiftfoot Boots equip reminder | 64 | RESCUE ZONE | wanted (buried, not full weight) |
| Faithless Looting flashback reminder | 173 | DEAD | wanted (dead) |
| Mystic Remora cumulative upkeep reminder | 60 | RESCUE ZONE | wanted (buried, not full weight) |
| Vandalblast overload reminder | 26 | DISCOUNTED | wanted (buried, not full weight) |

**Lane 1c six (native, long) — must land in the rescue zone (51–172):**

| Pair | frag_df | Band | Gram provenance (informational) |
|---|---|---|---|
| Growth Spiral vs Eureka Moment | 54 | RESCUE ZONE | native-only |
| Garruk's Uprising vs Elemental Bond | 57 | RESCUE ZONE | mixed/native |
| Cultivate vs Skyshroud Claim | 70 | RESCUE ZONE | native-only |
| Rhystic Study vs Reparations | 77 | RESCUE ZONE | native-only |
| Rampant Growth vs Natural Connection | 119 | RESCUE ZONE | mixed/native |
| Deadly Dispute vs Village Rites | 128 | RESCUE ZONE | mixed/native |

All six match the FINDINGS-MEMO's originally-measured DF exactly (54/57/70/77/119/128)
and all land in the rescue zone as required. Three show `mixed` gram
provenance at the CORPUS level (this exact 5-token string also appears,
elsewhere, inside some unrelated card's M2-injected reminder) — this is **not**
a verdict flip. R1's provenance discount keys on the PAIR's own evidence
(both Growth Spiral's and Eureka Moment's occurrence of the shared text are
native, hand-written oracle text), not on a third-party corpus-wide gram
coincidence. Reported for transparency since it surprised me on first pass;
resolved by re-reading R1's own wording ("evidence is... on BOTH sides"),
which is pair-scoped, not gram-scoped.

## Decision

**DECISION RULE MET — ADOPT.** Every landmark verdict from the manifest
holds unchanged on the native-only, provenance-segregated data: the Lane 1c
six qualify-buried (rescue zone), and the full boilerplate set (choose-one,
equip, flashback, cumulative-upkeep, overload, enters-tapped, draw-a-card,
and the generic mana-skeleton) is dead or buried. Adopting the provisional
edges as ratified constants:

```
LONG_FULL_WEIGHT_CEILING    = 10
LONG_DISCOUNT_CEILING       = 50
LONG_RESCUE_CEILING         = 172   (DEAD above this)
SHORT_FULL_WEIGHT_CEILING   = 5
SHORT_DISCOUNT_CEILING      = 39    (DEAD above this)
```

Header note for Phase 3 report headers: **"confirmed against native-only
distributions."**

No landmark flipped, so per the manifest ("never choose replacement numbers
yourself") there is nothing to bring to Captain at this gate — proceeding to
Phase 2's small independent fixes.
