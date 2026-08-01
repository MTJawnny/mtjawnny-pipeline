# CORPUS-PASS-PLAN — full-corpus processing design (ratified batch-6 §11, 2026-07-30)

Persisted from `docs/TRIAGE-BATCH-6.md` section 11 per Captain's explicit instruction
("Claude Code: persist this section into the protocol docs... and wire the sequencing").
This is **ratified direction, not an executed plan** — only sequencing step 1 (Gate #0) is
done as of this writing. Steps 2-8 are real, dollar-costed work requiring their own
explicit Captain go-ahead per the batch API cost-estimate standing rule; nothing below
authorizes spending on them.

## Why this exists

The batch-by-batch SUP-TRIAGE loop (`docs/SUP-TRIAGE-PROTOCOL.md`) samples ~1,200 cards
per batch and has run 6 rounds against a 38,233-card corpus. It will keep finding new
axes and new member mismatches indefinitely at this sampling rate. The corpus-wide pass is
the eventual full-coverage replacement: apply the now-mature codebook deterministically
(where possible) or via a cheaper SYNTH pass (where judgment is still required) against
every gate-passing card at once, rather than sampling forever.

## 1. Three lanes

- **Lane 1 — DET pre-tag pass** (runs first, token-free, re-runs on every Scryfall
  refresh). Every codebook axis gets classified DET-able or SYNTH-only. DET-able means
  membership is decidable by an anchored oracle-text pattern with polarity
  canonicalization and no judgment call — examples: `rule:enters-tapped`, the three
  activation-restriction axes, `rule:prevents-regeneration` ("can't be regenerated"),
  `rule:no-maximum-hand-size`, `rule:stun-counter`, the energy-counter axes, The Ring
  tempts you, landfall-triggered axes, kicker-conditional axes. Each candidate DET pattern
  is proposed with a measured corpus hit-list, sampled and RATIFIED by Captain like a
  scoring constant — versioned, never silently tuned. Provenance on DET-tagged members:
  rule-derived (full weight). Gate #0 applies to every card DET touches.
- **Lane 2 — SYNTH judgment pass.** Once an axis is DET-owned, it is STRIPPED from the
  embedded codebook reference SYNTH sees — this is the single biggest lever on the
  codebook-growth cost problem flagged since batch 5. SYNTH's full-corpus pass then hunts
  only judgment territory: jobs, rhystic shapes, cheat-into-play, "same job, different
  words" Tier-3 patterns that no anchored regex can safely decide. Runs only on
  gate-passing cards; the card count and cost estimate get restated after the gate filter
  and the DET strip are both applied (the corpus SYNTH actually has to read shrinks twice
  over from the raw 38,233).
- **Lane 3 — Reconcile with halt-loudly.** SYNTH never sees DET pre-tags (no anchoring, to
  avoid contaminating its judgment with a mechanical answer it might rubber-stamp). At
  reconcile time: a SYNTH free-lane hit that matches a DET-owned axis is treated as
  corroboration (two independent methods agreeing); a SYNTH hit that CONTRADICTS a DET
  pattern's verdict for the same card is not silently resolved — it becomes a halt-loudly
  review row, the same discipline the pipeline already applies everywhere else.

## 2. Lattice grammars ("prebuilt buckets," done safely)

Many T3 axis families are enumerable a priori once one member exists — e.g. once
`rule:activated-tap-or-untap-any-permanent` exists (batch-6 D2), the whole
`activated-tap-or-untap-<scope>` family (any/own/opponent × creature/artifact/permanent,
etc.) is a known shape. The mechanism for capturing this without bloating the codebook
with empty hypotheses:

- **Grammar ratification.** For a family, Captain ratifies a GRAMMAR: an action stem plus
  ordered facet slots with closed vocabularies — e.g.
  `activated-tap-or-untap-<ownership?><class>`, `targeted-bounce-<class>`,
  `<trigger>-create-token-<type>`. The grammar itself, not a list of pre-authored empty
  axes, is the "prebuilt bucket."
- **Virtual nodes.** An unpopulated lattice slug is NOT authored into the codebook — an
  axis with zero members is a hypothesis, not a ratified rule, and empty axes are exactly
  the kind of embedded-codebook bloat that's the cost driver. A node instantiates the
  moment a quote-verified member arrives; no fresh per-axis ratification is needed at that
  point because the grammar itself was already ratified.
- **Labeling discipline upgrade.** SYNTH may compose a slug from a ratified grammar and
  have it count as `lane=codebook-grammar` (a new lane value, distinct from `codebook` and
  `free`) rather than `lane=free` — this is meant to eliminate the near-miss invented-slug
  problem batch 6 found twice (the etb-prefix confusion on
  `rule:create-token-mana-producing-artifact`, and the synonymous
  `rule:equipment-static-pt-buff` / `rule:equipment-grants-stat-buff` re-invention of a
  killed axis — see `docs/TRIAGE-BATCH-6.md` sections 4 and 15) by making the composition
  rule deterministic instead of relying on SYNTH recall against a bare keyword list.
  **Not implemented yet** — this requires a `foundry_stage1b.py` prompt change and a
  grammar-validation step in `foundry_consolidate.py`/`foundry_enrich.py`, neither built
  in this session.
- **Free parent derivation.** Emit can derive parents from grammar structure for free
  (stem = parent, facets = children), feeding the ratified derived-parents scheme
  (`mtjawnny.github.io/docs/PARENT-TREE-CANDIDATES.md`, S1-S7).
- **Grammars seeded so far** (drafted informally in triage sessions, not yet in a formal
  grammar file): `create-token-<type>` (batch-5 D14), `etb-create-token-<type>` and
  `leaves-battlefield-trigger-create-token-<type>` (batch-5 D10, extended batch-6 D3 with
  the `-mutagen` child), `targeted-<action>-<class>` (M8, generalized to all
  targeted-<action> families batch-6 D3), `activated-tap-or-untap-<scope>` (batch-6 D2),
  the draw-second/cast-second prefix scheme (batch-5 D12). **Not done:** a formal grammar
  file Code drafts and Captain ratifies before the full pass.
- **Kill switch.** If lattice grammars don't measurably help agent efficiency in practice
  (metric: rate of `lane=free` near-miss slugs per batch, before vs. after), Captain can
  scrap the mechanism. Not a permanent architectural commitment.

## 3. Sequencing (amends batch-5 §11.3/D17)

1. **GATE #0** — legality gate implemented + retroactive scrub + precedent rescan. **DONE**
   2026-07-30 (batch-6 D1). `foundry_common.gate_passes()` / `load_corpus_gated()`;
   retroactive scrub report at `experiments/out/foundry/gate0_scrub_report.json` (173
   members removed across 92 codebook-v0.5 axes); precedent rescan found and fixed one
   dangling citation (this doc's sibling, `docs/TRIAGE-BATCH-6.md` section 4).
2. Keyword-bucket extraction (already ratified in an earlier session, unchanged by this
   plan). **DET job run 2026-07-30** — `experiments/foundry_keyword_buckets.py` walked CR
   702 (194 keyword entries), CR-cited, verify-or-drop. Output:
   `experiments/out/foundry/keyword-buckets.json` + report. Taxonomy corrections and open
   questions logged in `docs/CORPUS-PASS-WALK-RATIFICATION.md` sec.1 — **pending Captain
   ratification**, not yet integrated into SYNTH prompt or tag-tree (per ratified
   sequencing, that's schema pass).
3. COMBINED per-axis walk: naming audit + agent-legible definition rewrite + DET-ability
   classification + grammar drafting — one walk across all ~271 active axes (v0.6),
   four output columns per axis. **Walk run 2026-07-30** against v0.7 (306 active axes) —
   `experiments/foundry_axis_walk.py` + `experiments/validate_slug.py` +
   `docs/grammars.json` + `experiments/foundry_det_patterns_probe.py`. Full proposal set
   (rename list, DET-able axis list with corpus-measured hit-counts, grammar drafts, open
   questions) in `docs/CORPUS-PASS-WALK-RATIFICATION.md` — **pending Captain ratification**;
   codebook.json untouched.
4. DET rule authoring + ratification + full-corpus DET pass (gate-passing cards only).
   **Not started.**
5. Codebook condensation (largely automatic once the DET strip from step 4 lands).
   **Not started.**
6. SYNTH full-corpus pass — budget re-estimated post-gate/strip (batch-6's own per-batch
   cost was on a 1,200-card sample against a 32,557-card gate-passing pool; the
   full-corpus number needs its own explicit estimate once step 4's DET strip is known).
   Explicit Captain trigger required regardless of estimate, same standing rule as every
   other Batch API submission. **Not started.**
7. SCHEMA PASS — the pre-existing schema-pass agenda (parent/child structure, ownership
   facets recorded during batch-6 D3, lattice-grammar formalization from section 2 above,
   the `rule:activated-tap-target` family consolidation flagged in batch-6's punch list).
   **Not started.**
8. Display build per the READY-TO-SHIP contract (site repo). **Not started.**

## 4. Language standard

Every rule name and definition must be understandable and reproducible by an agent with no
session context: grammar-composed slugs, closed facet vocabularies, a glossary for
standing shorthand (e.g. "scroll" = instant/sorcery/interrupt card, "regrowth" = returns a
card from graveyard to hand — both from batch-5 D11), and definitions that state
trigger/cost/effect position explicitly rather than leaving it implicit in word order. This
extends batch-5 D17's agent-legibility directive: the naming audit (sequencing step 3
above) is load-bearing for lattice derivation, DET pattern-matching, and parent derivation
alike — a definition an agent can't mechanically apply is a definition that can't support
any of the three.

## Status summary (as of 2026-07-30, batch-6 emit)

| Step | Status |
|---|---|
| 1. Gate #0 | **Done** |
| 2. Keyword-bucket extraction | **Walk done 2026-07-30, proposals pending ratification** |
| 3. Combined per-axis walk | **Walk done 2026-07-30, proposals pending ratification** (see CORPUS-PASS-WALK-RATIFICATION.md) |
| 4. DET authoring + full-corpus DET pass | Not started (blocked on step-3 DET pattern ratification) |
| 5. Codebook condensation | Not started |
| 6. SYNTH full-corpus pass | Not started (needs cost estimate + Captain trigger) |
| 7. Schema pass | Not started |
| 8. Display build | Not started |
