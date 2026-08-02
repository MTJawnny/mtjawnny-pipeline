# T3 Buildout — pick up at Step 4

**Paste this to start the next session** (run from `mtjawnny.github.io`,
same as this session — the pipeline work happens cross-repo in
`~/Projects/mtjawnny-pipeline`):

> Read `docs/T3-BUILDOUT-PLAYBOOK.md` and execute Step 4. Read
> `docs/T3-BUILDOUT-STEP4-HANDOFF.md` first for where Steps 1-3 landed.
> Continue through all phases — only stop on genuine ambiguity, a failed
> gate, or an unspecified decision.

## Where things stand

Playbook: `docs/T3-BUILDOUT-PLAYBOOK.md` (Steps 1-9, one step per fresh
session, per its own header).

- **Steps 1-2 — done.** See `docs/T3-BUILDOUT-STEP3-HANDOFF.md` for full
  detail (Step 1 superseded/committed `c53b30d`; Step 2 Phase A change
  order D1/D2/N1/N2 committed `b5d5e3a`).

- **Step 3 — done, NOT YET COMMITTED (awaiting Captain's explicit
  go-ahead).** Task: implement `score = tagger_coverage + DERIVED_WEIGHT *
  derived_agreement` and migrate `rule:turn-scoped` off the old
  merged-index mechanism into it.

  **DERIVED_WEIGHT = 0.5**, ratified by Captain before any code was
  written, per the spec's own proposed value.

  **Mid-implementation finding, ratified as Lesson 3
  (`docs/DERIVED-TAG-LAYER-SPEC.md`):** the naive additive term let a
  SINGLE common derived tag (rule:turn-scoped alone, corpus DF=731) act as
  a full-strength (derived_agreement=1.0) sole Tier 3 qualifier —
  measured live, this flooded Grand Abolisher's Tier 3 from 68 to 814 rows,
  657 of them sharing NOTHING else with the anchor (Legion Warboss, Vivi
  Ornitier, Cosmic Spider-Man). Root cause: a single-member namespace can't
  normalize a common tag down the way multiple members eventually will.
  Captain's ruling: apply the engine's existing T2_RESCUE_CEILING idiom
  (common evidence corroborates, rare evidence qualifies) as a new named
  constant, **DERIVED_QUALIFY_DF_CEILING = 172** — the derived term always
  contributes to score once a candidate qualifies by any means, but may
  only be a candidate's SOLE qualifier (crossing TIER3_COVERAGE_THRESHOLD
  when tagger_coverage alone doesn't) when at least one shared rule:-tag
  has corpus DF ≤ 172. Implemented as `derived_solo_qualifies()` in
  `tier_engine.py`, gating qualification only — never exclusion of a
  candidate that already qualifies via tagger_coverage.

  **Verified result after the ceiling fix:**
  - Grand Abolisher: Tier 3 68 → 98 rows (not 814). 33 entered (all
    non-turn-scoped-carriers — cards whose OWN tagger_coverage was being
    silently suppressed by the OLD mechanism's anchor-wide denominator
    inflation, now fixed). 65 continued with a score increase, zero
    decreases (additive invariant holds). 3 EXITED (Elephant-Mandrill,
    Razorkin Needlehead, Tithe Taker) — each had real but sub-threshold
    tagger_coverage (0.12-0.15) that the OLD merged mechanism happened to
    push over 0.15 via a mediant-inequality artifact; correctly revoked by
    Lesson 3, since their qualification was propped up by exactly one
    common tag.
  - Displayed top-10 validation: Dosan the Falling Leaf and City of
    Solitude (the spec's own Lesson-1 example victims) rose to #1/#2
    (0.30 → 0.74). Defense Grid entered the displayed top 10 for the first
    time (0.24 → 0.67, was buried ~#31). Exactly the outcome Lesson 1/2
    were written to produce.
  - Zurgo, Thunder's Decree, Sol Ring, Preordain, Sakura-Tribe Elder,
    Marisi — none carry `rule:turn-scoped` themselves, so all four are
    **byte-identical** before/after (only the report header's new
    "derived weight=/derived-qualify DF ceiling=" line differs). Verified
    directly by diffing full reports, not just gate PASS lines.
  - Zurgo's v2.10 T3 spot-check (Hero of Bladehold, Caesar Legion's
    Emperor, Gornog the Red Reaper) is **byte-identical** to the true
    pre-migration baseline — confirmed via `emit_viewer.py`'s printed
    spot-check output, matching exactly (same positions, same scores).

  Full gate suite green (94/94 default panel, up from 73 at Step 1 as
  gates have grown across Steps 1-2; Zurgo/Delney extended panel also
  green), determinism ×2 confirmed via `experiments/snapshot.py
  verify-determinism` for both panels (byte-identical stdout + output
  files). Snapshot written: `experiments/out/snapshots/
  derived-additive-term-v1/` (111 constants, 94 gates passing, 75 cached
  output files). BEFORE-panel snapshot (Grand Abolisher, Zurgo, Sol Ring,
  Preordain, Sakura-Tribe Elder — the true pre-migration baseline, for
  historical reference only, see re-baselining note below) preserved at
  `experiments/out/snapshots/derived-additive-term-v1-BEFORE/` in the
  pipeline repo (gitignored, local only — re-derivable by checking out the
  pre-Step-3 commit if ever needed, but kept on disk for now).

  **Step 5 gate re-baselined (Captain's ruling, 2026-07-17) — READ THIS
  BEFORE STARTING STEP 5.** `T3-BUILDOUT-PLAYBOOK.md`'s Step 5 blocking
  gate text reads "Grand Abolisher's T3 must contain Defense Grid, Dosan
  the Falling Leaf, City of Solitude, and Teferi Time Raveler at or above
  their Step 3 BEFORE positions" — that phrase now means the **post-Step-3
  AFTER snapshot** (`experiments/out/snapshots/derived-additive-term-v1/`),
  NOT the pre-migration baseline in the `-BEFORE` snapshot dir. Concretely,
  the new floor each v1 derivation (Step 5) must hold Defense Grid/Dosan/
  City of Solitude/Teferi at or above is:
  - Dosan the Falling Leaf: displayed position **#1** (score 0.74)
  - City of Solitude: displayed position **#2** (score 0.74)
  - Defense Grid: **in the displayed top 10** (position #4, score 0.67) —
    this is a real change from pre-Step-3, where Defense Grid was
    INFORMATIONAL-ONLY and buried at full-list position ~31, never in the
    displayed top 10 at all. Step 5 sessions must not accept Defense Grid
    falling back out of the displayed top 10 as "no worse than before
    Step 3" — before Step 3 it was ALREADY worse (not displayed); the
    floor is now "stays displayed," a strictly higher bar.
  - Teferi, Time Raveler: full-list position 67/68 (score 0.16) BEFORE →
    64/98 (score 0.17) AFTER — present both times, never in the displayed
    top 10 either time (a non-turn-scoped-carrier, small de-dilution-only
    bump, same shape as the other 58 non-carrier common rows). The new
    floor is full-list position 64 or better / score 0.17 or better, not
    "must be displayed" — Step 5 should not treat Teferi's continued
    absence from the displayed top 10 as a regression on its own.
  The BEFORE snapshot remains on disk for historical comparison only (e.g.
  if Step 5 wants to show the full pre-migration-to-final arc), but it is
  NOT the gate's reference point going forward.

  **Files touched** (pipeline repo, uncommitted): `experiments/
  tier_engine.py` (DERIVED_WEIGHT, DERIVED_QUALIFY_DF_CEILING constants;
  `derived_solo_qualifies()`; `build_turn_scoped_tag_index()` rewritten to
  return a rule:-namespace-only index plus a new `df_t3` DF-lookup dict
  instead of merging into base Tagger tags; `compute_candidate_rows()` and
  `_discovery_superset_exhaustive_qualifiers()` updated to the additive +
  ceiling-gated formula; `check_t3_turn_scoped_movement`/
  `check_defense_grid_gate` docstrings/print text corrected to stop
  describing dilution that no longer happens; report header now prints
  `derived weight=`/`derived-qualify DF ceiling=`), `experiments/
  emit_viewer.py` (threaded the new `df_t3` value through unchanged call
  shapes). `docs/DERIVED-TAG-LAYER-SPEC.md` (this repo) has Lesson 3
  recorded in full, plus a Sequencing-and-gates checkbox update.

  **Committed, Captain's go-ahead 2026-07-17** — see the pipeline repo's
  git log for the commit citing both ratified constants and the Lesson 3
  entry. Not pushed (this repo's standing convention: only Captain pushes).

  **Awareness only, no action taken:** the viewer JSON exports under
  `experiments/out/viewer/data/` (gitignored, not part of the commit) were
  regenerated during this session's verification runs and so currently
  reflect the Step 3 scoring change — but they are NOT the authoritative
  "post-Step-3" viewer state Step 7 is responsible for; Step 7's own
  "Regenerate all viewer exports" task still needs to run for real once
  the full derived-layer poke panel exists. Don't treat this session's
  incidental regeneration as satisfying Step 7.

## Step 4 — what's next

Per the playbook: Step 4 is a DOCUMENT, not code —
`docs/FAMILY-TREE-EVIDENCE.md`. Read first: `docs/DERIVED-TAG-LAYER-SPEC.md`
(family section, v1 derivation set — now including Lesson 3),
`experiments/POKE-PUNCH-LIST.md`, `tier_engine.py`'s `SELF_CHECK_PAIRS`/
gate-card constants, `tags/cards.yaml`. Propose candidate families WITH
evidence and counter-arguments — do NOT propose a final ratified tree,
Captain writes that himself. Full instructions in the playbook's Step 4
section (evidence sources, required output structure per family, the five
minimum candidate families, the anti-laundering guard).

## Standing rules (same as every step)

Halt loudly on ambiguity, verify claims against live code/corpus not
memory, nothing committed without an explicit go-ahead, full gate suite +
determinism ×2 + a snapshot after any ruling-affecting change, new scoring
constants are proposed-then-ratified before implementation. See
`docs/T3-BUILDOUT-PLAYBOOK.md`'s own "Standing rules" section for the
complete list.
