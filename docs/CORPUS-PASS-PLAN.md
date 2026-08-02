# CORPUS-PASS-PLAN — full-corpus processing design (ratified batch-6 §11, 2026-07-30)

Persisted from `docs/archive/TRIAGE-BATCH-6.md` section 11 per Captain's explicit instruction
("Claude Code: persist this section into the protocol docs... and wire the sequencing").
This is **ratified direction, not an executed plan** — only sequencing step 1 (Gate #0) is
done as of this writing. Steps 2-8 are real, dollar-costed work requiring their own
explicit Captain go-ahead per the batch API cost-estimate standing rule; nothing below
authorizes spending on them.

## EMERGENCY COST STOP (standing rule, ratified 2026-08-01 — binds this and every future
session until Captain explicitly revokes it)

**$140.00 total remaining-arc ceiling**, tracked as CUMULATIVE spend across the whole
corpus-pass arc (not per-submission). Before **ANY** Batch API submission, in this order:

1. Compute actual cumulative spend to date this arc (real, metered numbers from prior
   batches' `usage` fields — never a pre-submission estimate standing in for an actual).
   Running total as of 2026-08-01: **$90.51** — batch 8 A/B ≈ $32.73 + $0.15 (N=40
   schema pre-flight dry-run) + $56.94 (corpus-pass run 1 main batch) + $0.14 (pack-198
   truncation retry) + $0.55 (164-card dropout recovery pass) — see the run-1 ACTUAL
   entry below for the full accounting. Update this line with each new submission's
   actual cost once known.

   **Full-corpus run 1 gate check, 2026-08-01** (pre-submission, per this rule):
   cumulative actual to date = $32.88. Live-priced estimate for the N=40 packed
   full-corpus submission (32,557 gate-passing cards, 814 packs), re-priced fresh via
   WebFetch against platform.claude.com/docs/en/about-claude/pricing (Sonnet 5 intro
   through 2026-08-31 confirmed unchanged: $2/$10 base in/out, 5m cache write
   $2.50/MTok, cache read $0.20/MTok, Batch API 50% off, stacking) and batch 8's real
   Arm C per-pack usage (same N=40 packed architecture, same codebook content, real
   observed batch-level cache-read behavior — not assumed) scaled by pack count
   (814/30): **$55.05 projected**. `projected_total = 32.88 + 55.05 = $87.93` ≤
   $140.00 → **PASS, submission authorized to proceed** (headroom after: $52.07).

   **Full-corpus run 1 ACTUAL, 2026-08-01** (post-fetch): 814/814 pack-requests
   reported `succeeded` at the Batch API transport level, 0 errored/canceled/expired —
   but two DATA-QUALITY issues surfaced on parse, caught by the coverage check before
   any consolidation, not silently absorbed:
   - 1 pack (`corpus-pass-1-pack-0198`, 40 cards) hit `stop_reason=max_tokens` and its
     JSON payload was truncated/unparseable. Fixed by re-splitting the same 40
     oracle_ids into two N=20 sub-packs and resubmitting synchronously — both
     completed cleanly, full coverage recovered. Cost: $0.1446.
   - 30 packs (164 cards total) completed with a valid `end_turn` but the model
     stopped early without processing every card shown — a real instruction-compliance
     miss, not a token-limit issue (two packs returned only 2/40 and 24/40 results
     despite `end_turn`). Fixed by collecting all 164 missing oracle_ids and
     resubmitting them fresh in 17 small (N≤10) synchronous sub-packs — all 164
     recovered on the first retry, 0 still missing. Cost: $0.5472.
   - Final verified coverage: **32,557/32,557** gate-passing cards, 0 missing, 0
     malformed/hallucinated oracle_ids counted (24 such strings appeared across the
     main batch — e.g. real UUIDs with a fabricated `-duplicate-skip`/`-DUP`/
     `-placeholder` suffix — all discarded, never treated as card data).
   - Main batch real cost: $56.94 (vs. $55.05 projected, +3.4%, consistent with a
     slightly lower real batch-level cache-hit ratio than batch 8's Arm C proxy
     predicted). Total run-1 cost including both remediation passes: **$57.63**.
   - New cumulative arc spend: **$90.51**. Headroom remaining against the $140
     ceiling: **$49.49**.
2. Get a **live-priced estimate** for the submission about to happen — fresh
   `count_tokens` measurement (exact or sampled) against CURRENT pricing (re-fetched,
   never recalled/reused from a prior session's fetch even if it "should" be unchanged)
   and the CURRENT request set. A stale estimate (from an earlier prepare step, an earlier
   session, or extrapolated without re-measuring) does not satisfy this requirement — redo
   it immediately before the submission it gates.
3. `projected_total = cumulative_actual_to_date + live_estimate`. If `projected_total >
   $140.00`: **HALT. Report the numbers. Do not submit.** No exceptions, no "slightly
   over," no rounding in the ceiling's favor — a projected total of $140.01 halts exactly
   like $200 would.

This rule exists independently of, and stacks with, the pre-existing standing rule
("Batch API submissions: cost estimate from CURRENT pricing docs + Captain go-ahead
first. Never remembered prices" — CLAUDE.md) — go-ahead for a specific submission does
NOT waive this ceiling check; both gates must pass.

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
  killed axis — see `docs/archive/TRIAGE-BATCH-6.md` sections 4 and 15) by making the composition
  rule deterministic instead of relying on SYNTH recall against a bare keyword list.
  **WIRED 2026-07-31** (walk-ratification session, batch-7 D7): `foundry_stage1b.py`'s
  system prompt now has a three-lane instruction with a ratified-grammar-families
  reference block (excludes the activation-restriction family per D-4) and a
  `lane=codebook-grammar` schema option; `foundry_consolidate.py` validates every
  `lane=codebook-grammar` label through `validate_slug.py` (downgrades to `lane=free` on
  failure, per CODEBOOK-NAMING-GRAMMAR.md sec.11) and rejects any activation-restriction-
  family label outright under any lane (D-4). Not yet exercised against a real batch
  (no batch has run since this landed) — first live use will be the first post-walk
  SYNTH batch.
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
   dangling citation (this doc's sibling, `docs/archive/TRIAGE-BATCH-6.md` section 4).
2. Keyword-bucket extraction (already ratified in an earlier session, unchanged by this
   plan). **DET job run 2026-07-30** — `experiments/foundry_keyword_buckets.py` walked CR
   702 (194 keyword entries), CR-cited, verify-or-drop. Output:
   `experiments/out/foundry/keyword-buckets.json` + report. **RATIFIED 2026-07-31**
   (walk-ratification session, `docs/WALK-RATIFICATION-EXECUTION-HANDOFF.md`): 9-bucket
   taxonomy adopted, casting-modifier demoted to a facet flag, DELIVERY vocab extended
   (becomes-targeted-trigger, blocks-or-becomes-blocked-trigger), F1 multi-class extraction
   bug fixed (Ascend spell->hybrid). Not yet integrated into the SYNTH prompt or tag-tree
   (still correctly deferred to schema pass, per ratified sequencing).
3. COMBINED per-axis walk: naming audit + agent-legible definition rewrite + DET-ability
   classification + grammar drafting — one walk across all ~271 active axes (v0.6),
   four output columns per axis. **Walk run 2026-07-30** against v0.7 (306 active axes) —
   `experiments/foundry_axis_walk.py` + `experiments/validate_slug.py` +
   `docs/grammars.json` + `experiments/foundry_det_patterns_probe.py`. **RATIFIED AND
   APPLIED 2026-07-31** (walk-ratification session, see
   `docs/WALK-RATIFICATION-EXECUTION-HANDOFF.md` for the full ruling set and
   `docs/archive/CORPUS-PASS-WALK-RATIFICATION.md`'s RESOLUTION header): 23 renames applied to
   codebook.json (19 structural + Q10's 4 combat-damage normalizations), 1 kill
   (rule:kicker-conditional-bonus-effect, bare-keyword duplicate), the unblockable/evasion
   family redesigned (Q8: `<delivery>-unblockable-<scope>` rejected, new
   `cant-be-blocked-<restriction>` grammar ratified, 3 grant-axis definitions rewritten as
   facet readings), naming-grammar vocabulary extended (~30 tokens + cant-be-blocked stem +
   uncounterable), validate_slug.py wired into `foundry_stage1b.py`/`foundry_consolidate.py`
   (D7). Codebook now v0.7, 305 active axes. DET pattern set finalized at 42 ratified
   patterns (`docs/det-patterns-v1.json`) — the actual gate-passing full-corpus DET pass
   (step 4 below) is still NOT run.
4. DET rule authoring + ratification + full-corpus DET pass (gate-passing cards only).
   **Done 2026-08-01** — 39 of 44 ratified patterns map to a real codebook axis (the other
   5 are Lane-1 pre-filters); full-corpus hit lists applied to codebook.json as
   `source="DET"` membership via `foundry_det_pass.py apply`, gated by the fixed-seed
   20-hit sample-sheet condition (all 39 passed, 2 root-caused fixes along the way —
   `docs/det-patterns-v2.json` supersedes v1). Zero spend. Backup:
   `experiments/out/foundry/backups/codebook.v0.7.pre-det-pass.20260801-013346.json`.
5. Codebook condensation (largely automatic once the DET strip from step 4 lands).
   **Done** — the 39 DET-owned axes are stripped from the SYNTH-embedded codebook
   reference (`foundry_stage1b.load_det_owned_slugs()`, reading det-patterns-v2.json);
   268 non-DET active axes were what run 1's SYNTH prompt actually embedded.
6. SYNTH full-corpus pass — budget re-estimated post-gate/strip (batch-6's own per-batch
   cost was on a 1,200-card sample against a 32,557-card gate-passing pool; the
   full-corpus number needs its own explicit estimate once step 4's DET strip is known).
   Explicit Captain trigger required regardless of estimate, same standing rule as every
   other Batch API submission. **Run 1 complete 2026-08-01** (M=1, N=40 packed, all
   32,557 gate-passing cards, $57.63 total real spend incl. 2 remediation passes for a
   truncated pack and 30 packs' partial dropout — see EMERGENCY COST STOP section above).
   **Consolidation into codebook.json was BLOCKED**, same date, on the member-provenance
   schema ruling. **That blocker is CLEARED as of 2026-08-01**: codebook.json migrated to
   `foundry-codebook/2`, in which each member carries a stack of assertions
   (class / source_ref / quote / corpus_ref / evidence_status), so a SYNTH confirmation
   now has somewhere true to live. The consolidation write is NOT next: per A12 it is
   session 3 (APPLY), and it executes an approved plan produced by session 2 (PLAN,
   `docs/archive/CONSOLIDATION-PLAN-DIRECTIVE.md`, zero-mutation, also the external re-audit
   checkpoint). Free-lane discovery artifact and full dry-run report remain complete.
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

## Status summary (as of 2026-08-01, consolidation-run1 session)

| Step | Status |
|---|---|
| 1. Gate #0 | **Done** |
| 2. Keyword-bucket extraction | **Ratified 2026-07-31** (9-bucket taxonomy, F1 fix applied); not yet integrated into SYNTH/tag-tree (schema pass) |
| 3. Combined per-axis walk | **Ratified and applied 2026-07-31** (23 renames + 1 kill in codebook.json v0.7/305 active; see WALK-RATIFICATION-EXECUTION-HANDOFF.md and CORPUS-PASS-WALK-RATIFICATION.md's RESOLUTION header) |
| 4. DET authoring + full-corpus DET pass | **Done 2026-08-01** — 39 ratified patterns applied full-corpus (`docs/det-patterns-v2.json`, superseding v1 after 2 sample-gate-caught fixes); see RESUME-NOTE.md and this file's EMERGENCY COST STOP section |
| 5. Codebook condensation | **Done** (byproduct of step 4 — DET-owned axes stripped from the SYNTH-embedded reference; 268 non-DET active axes shown to SYNTH for run 1) |
| 6. SYNTH full-corpus pass | **Run 1 complete 2026-08-01** (M=1, 32,557/32,557 cards, $57.63 total incl. 2 remediation passes — see EMERGENCY COST STOP section). **Consolidation blocker CLEARED 2026-08-01**: the member-provenance schema was ratified and executed — codebook.json is now `foundry-codebook/2`, where `member_oracle_ids` has become `members`, a list of objects each carrying an assertion stack (class / source_ref / quote / corpus_ref / evidence_status, plus a member-level tier iff every assertion is llm-class). CONSOLIDATION-RUN1-DIRECTIVE.md sec.4's HALT-and-propose was honoured: the shape was proposed, externally audited, amended and Captain-ratified before any write. The codebook.json write is now gated on the session-2 PLAN artifact rather than on schema (A12). Free-lane discovery artifact (`corpus_pass_run1_discovery.json`) and the full dry-run report (`corpus_pass_run1_consolidation_dry_run.json`) are complete and committed; only the actual codebook.json write is pending. Corroboration waves remain a future trigger regardless. |
| 7. Schema pass | Not started |
| 8. Display build | Not started |
