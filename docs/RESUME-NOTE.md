# RESUME-NOTE — full-corpus SYNTH pass, run 1 (submitted 2026-08-01)

If you are picking this up cold: this note plus `docs/CORPUS-PASS-PLAN.md`'s
EMERGENCY COST STOP section is everything you need. Read both before doing
anything else.

## What was submitted

**Batch ID: `msgbatch_01Pk4qWUz28TCwC8nspLAJ2c`**
Submitted 2026-08-01 via `experiments/foundry_corpus_pass_run1.py submit`.
Status at submission: `in_progress`.

- Model: `claude-sonnet-5`
- Architecture: packed requests, N=40 cards/request, 814 pack-requests
  covering all 32,557 Gate #0-passing cards (shuffle seed 20260731,
  `foundry_stage1b.pack_oracle_ids`)
- Full untrimmed schema on every lane (the output-trim proposal stayed
  REJECTED — `docs/OUTPUT-TRIM-PROPOSAL.md`)
- System prompt: three-lane (codebook / codebook-grammar / free), embedding
  268 non-DET-owned active codebook axes (codebook v0.7) + ratified grammar
  families (`docs/grammars.json`) + killed-slug list; the 39 DET-owned axes
  are stripped per `foundry_stage1b.load_det_owned_slugs()` reading
  `docs/det-patterns-v2.json`
- This is **run 1 only**. A second run (corroboration wave / M=2 lane-aware
  consensus) is **NOT authorized** — future trigger only, per Captain's
  2026-08-01 directive.

## How to resume

1. **Check status**: `GET /v1/messages/batches/msgbatch_01Pk4qWUz28TCwC8nspLAJ2c`
   (or just run step 2 below — it checks status itself and halts cleanly if
   not yet `ended`).
2. **Fetch results once ended**:
   `python3 experiments/foundry_corpus_pass_run1.py fetch-results`
   → writes `experiments/out/foundry/corpus_pass_run1_raw_results.jsonl`
3. **Check for errored/canceled/expired requests** — `fetch-results` prints
   a NOTE if `request_counts` shows any non-`succeeded` outcomes. Halt and
   report to Captain if so; do not silently proceed to consolidation with a
   partial result set.
4. **Get the real cost** — sum the `usage` field across all 814 result
   lines (mirrors `foundry_batch8_canon_analysis.py`'s cost-computation
   pattern), price at batch-discounted intro rate (re-verify pricing is
   still live/unchanged first, per the standing rule — don't reuse this
   note's numbers if pricing has since changed). **Update
   `docs/CORPUS-PASS-PLAN.md`'s EMERGENCY COST STOP running total** with the
   real actual (not the $55.05 projection below).
5. **DET-SYNTH contradiction check**: for every card, compare its DET-owned
   axis memberships (in `experiments/out/foundry/codebook.json`, `source ==
   "DET"` axes' `member_oracle_ids`) against what SYNTH emitted for that
   card in this run. A contradiction row is any card where SYNTH's
   lane="codebook" or lane="codebook-grammar" output implies a DIFFERENT
   verdict than the DET-derived ground truth for a DET-owned concept (e.g.
   SYNTH free-labels something that is actually one of the 39 DET-owned
   patterns, or a card is a DET-pattern member but SYNTH's output actively
   contradicts that classification). Flag these as halt-loudly review rows,
   not silent overwrites — DET is rule-derived provenance and wins on
   direct conflict, but a real conflict signals either a DET pattern gap or
   a SYNTH miss worth logging either way.
6. **Consolidate** per `docs/CORPUS-PASS-PLAN.md` steps 7-8 — this run's
   SYNTH output is a SINGLE run (M=1), so the lane-aware consensus scoring
   (corroborated=intersection / provisional=singleton) ratified 2026-08-01
   does NOT apply yet — that requires a second run, which is not
   authorized. For now: codebook-lane/codebook-grammar-lane confirmations
   feed the existing consolidation pipeline as single-run evidence
   (provisional until/unless a corroboration run is later triggered);
   free-lane output is unioned into consolidation as discovery candidates
   per the ratified lane-aware design (never scored as disagreement, there
   being nothing to disagree with yet on a single run).
7. **Report per standing format**: lane-aware corroborated/provisional
   actuals (N/A for corroboration tier on a single run — note this
   explicitly rather than omitting it), DET-SYNTH contradiction rows found,
   and total arc spend against the $140 ceiling.

## Budget state at submission time

- Cumulative arc spend BEFORE this submission: **$32.88** (batch 8 A/B ≈
  $32.73 + this session's N=40 schema pre-flight dry-run $0.15)
- Live-priced projected cost of this submission: **$55.05** (Sonnet 5 intro
  rate through 2026-08-31, Batch API 50% off, using batch 8's real Arm C
  per-pack cache behavior scaled by pack count — see
  `docs/CORPUS-PASS-PLAN.md` for the full computation)
- Projected cumulative total after this submission: **$87.93**
- **$140.00 emergency ceiling**: PASS, $52.07 headroom projected
- The REAL actual cost (from this batch's own `usage` fields, once fetched)
  supersedes the $55.05 projection for all future ceiling checks — update
  `docs/CORPUS-PASS-PLAN.md` immediately upon fetching results, before any
  further submission is even considered.

## What's already done (this session, before submission)

- **Full-corpus DET pass applied** (`foundry_det_pass.py apply`): all 39
  ratified DET patterns' full-corpus hit lists written to
  `codebook.json` as `source="DET"` membership, replacing the
  necessarily-partial sampling-era membership. Zero spend. Backup at
  `experiments/out/foundry/backups/codebook.v0.7.pre-det-pass.20260801-013346.json`.
  Two real bugs found and fixed during the fixed-seed sample-sheet review
  (standing condition), both resolved via `docs/det-patterns-v2.json`
  (supersedes v1 — v1 kept as historical record per the file's own
  versioning discipline):
  1. `rule:grants-unblockable-target`'s restriction-continuation guard
     didn't exclude the "by creatures that/who/\<player\> controls" phrase
     shape, so The Black Gate was still matching despite the B1 ruling
     moving it to `rule:cant-be-blocked-by-controller`. Guard extended,
     verified fixed (35→34 hits, Black Gate confirmed excluded, other 9
     members unaffected).
  2. `rule:grants-double-strike-target`'s def_anchor said "An instant
     grants..." — wording-only fix (delivery-agnostic), no pattern or
     membership change; several real members are activated/triggered, not
     instant.
- **N=40 packed schema pre-flighted**: one real synchronous dry-run call
  (pack 0 of the real shuffle order, real cards, post-DET-pass system
  prompt) confirmed the constant-size array schema still compiles (no
  regression of the "compiled grammar too large" failure from batch 8's
  first submission attempt) and returned all 40 oracle_ids correctly.
  Cost: $0.1489 (non-batch synchronous rate), logged above.
- **$140 ceiling gate check performed and passed** (see Budget state
  above), logged in `docs/CORPUS-PASS-PLAN.md`.

## Key files

- `experiments/foundry_corpus_pass_run1.py` — this run's prepare/submit/
  fetch-results script (distinct from `foundry_stage1b.py`'s per-triage-
  batch workflow, which this run does NOT use)
- `experiments/out/foundry/corpus_pass_run1_batch.json` — batch record
  (batch ID, submission metadata)
- `experiments/out/foundry/corpus_pass_run1_requests.json` — the 814
  submitted pack-requests (58MB, gitignored)
- `docs/det-patterns-v2.json` — the DET pattern set actually used for this
  arc (v1 is historical only from this point forward)
- `docs/CORPUS-PASS-PLAN.md` — EMERGENCY COST STOP section, arc spend
  running total, full plan/sequencing context
