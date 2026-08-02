# T3-AXIS-FOUNDRY v3 — Corpus-Wide Derivation Buildout with Iterative Codebook Review

Status: session spec for Claude Code. SUPERSEDES v1 and v2. Extends
T3-BUILDOUT-PLAYBOOK.md between Steps 5 and 6; inherits every standing
rule there. Read DERIVED-TAG-LAYER-SPEC.md (Lessons 1–3) and
FAMILY-TREE-EVIDENCE.md first.

## v3 changes, and why (Captain's rulings)

1. **Naming: "Tier" is reserved project vocabulary for card tiers
   (Tier 0 = same card, different name). Worker levels are now WORKER
   CLASSES:** DET (deterministic, zero tokens), BULK (small model,
   Message Batches API), SYNTH (mid model, per-axis work), SUP
   (supervisor — prompts, fixed-seed spot-checks, adjudication, packet
   review, never bulk work). Any doc or code comment saying "tier" about
   workers is wrong and gets fixed on sight.
2. **The codebook is built by ITERATIVE BATCH REVIEW, not one monolithic
   review.** Captain reviews small batches in a purpose-built static
   review tool (full card data inline, own-tag entry, exportable
   decisions), the codebook re-converges after each batch, and the
   full-corpus pass launches only after a measured convergence gate.
3. **Captain's review surface is a tool, not a document.** Naked tag
   lists are not reviewable; every axis is reviewed against its actual
   member cards with raw card info one click away — zero Scryfall
   cross-referencing.

## Mining architecture (unchanged from v2 in substance)

Two sources, reconciled: **Source A** — template mining from
clause_df/ngram_df (DET, free; catches the templated spine). **Source B**
— per-card functional decomposition, the Delney treatment industrialized
(BULK/SYNTH; catches phrasing-variant and clause-combination axes A is
blind to). A∩B = highest confidence; B-only = the gap this foundry
exists to close; A-only = supervisor-reviewed before discard. No model
output is ever load-bearing: models propose, Captain-ratified
deterministic patterns dispose. Evidence-quote-or-discard stands: every
per-card axis assignment must quote the card text it rests on, enforced
by DET automatically.

## The bootstrap loop (replaces v2 Stages 1B–1C)

Repeat until the convergence gate passes. Batch sizes: batch 1 = 500
cards (fast first lap), subsequent batches = 1,000–1,500. Stratified
sampling throughout (card type × color × text-length band × era, fixed
seed, strata printed), never resampling a previously reviewed card.

**Per batch:**

1. **Decompose (SYNTH for batch 1; BULK from batch 2 on, once a codebook
   exists to assign from).** Batch 1 is free-form open coding: 1–5 axes
   per card as {label, one-line definition, actor-scope, evidence quote}.
   Batch 2+ is closed coding against the current codebook + `OTHER:`
   escape lane, two passes, disagreement → uncertain bucket.
2. **Consolidate (DET + SUP).** Cluster labels, merge into codebook
   candidates, compute per-axis member counts, attach every member's
   evidence quote. SUP spot-checks 30 fixed-seed assignments against
   card text before anything reaches Captain.
3. **Emit the review batch** (`experiments/out/foundry/review/batch-N.json`,
   schema below) and open it in the REVIEW TOOL.
4. **Captain reviews** (tool workflow below), exports
   `decisions/batch-N.json`, drops it in the repo.
5. **Reconcile (DET).** Apply decisions: axis keeps/kills/merges/renames/
   definition edits; card-level removals; Captain's own new axes and
   per-card tags ingested (see provenance note). Produce codebook vN+1
   plus a one-page diff report: what changed, current axis count, and
   the convergence metrics.

**Convergence gate (measured, Captain calls it):** across two consecutive
batches — OTHER-lane rate below ~5% of assignments, Captain's
kill/merge/rename rate visibly declining, and no new axis exceeding a
handful of members. When the gate passes, the codebook freezes at
v1.0 and the full-corpus pass launches.

**Captain's own tags:** anything Captain enters in the tool — a new axis,
or a tag on a specific card — is HUMAN-provenance-class data
(DERIVED-TAG-LAYER-SPEC provenance table): full weight, ingested into the
codebook (axes) or queued for tags/cards.yaml (per-card tags) with a
`captain-review batch-N` provenance note. Captain's axes skip the model
pipeline entirely and go straight into the codebook.

## THE REVIEW TOOL (built in Session A, house patterns throughout)

`experiments/foundry_review.html` — ONE static file, emit_viewer's
architecture: load a batch JSON, render, no backend, no build step.
Serve via the existing local port-8000 pattern. DOM XSS law applies:
textContent always, innerHTML banned for any data-derived string.
Internal tool — plain styling is fine; house palette optional.

**Layout, three panes:**

- **Left — axis list**, ranked by member count. Each row: slug,
  member count, scope badge, source badge (A∩B / B-only / A-only /
  CAPTAIN), review-status dot (pending / decided).
- **Center — selected axis.** Definition, actor-scope, parameterization
  note, then the FULL member list (never truncated): card name + the
  evidence quote for that assignment. Decision controls: KEEP / KILL /
  MERGE INTO → (picker) / RENAME / EDIT DEFINITION / EDIT SCOPE, plus a
  notes field. Per-member row control: REMOVE FROM AXIS (with optional
  reason).
- **Right — card inspector.** Click any card name anywhere → full raw
  card info from the local corpus (name, mana cost, type line, full
  oracle text with the evidence quote highlighted, P/T or loyalty, color
  identity, keywords, layout + all faces for multiface cards, set/rarity
  of the oracle print). No image. Also shows: every OTHER axis this card
  was assigned in this batch, and a free-text **"Captain tag" input** —
  add-your-own tags right there, plus a "propose new axis from this
  card" button that opens a blank axis form pre-seeded with the card as
  first member.

**Persistence + round-trip:** decisions autosave to localStorage as
Captain works (this is Captain's own locally served tool, not a
claude.ai artifact, so localStorage is appropriate here); the EXPORT
button downloads `decisions/batch-N.json`. Import button restores a
previous export. The reconciler treats the exported file as the sole
source of truth.

**Schemas (Claude Code: build to these exactly, version field included):**

batch-N.json:
```json
{
  "schema": "foundry-review/1",
  "batch": 3,
  "codebook_version": "0.3",
  "axes": [{
    "slug": "rule:trigger-doubling",
    "definition": "...",
    "scope": "your-stuff",
    "source": "A∩B",
    "parameterized": false,
    "members": [{"oracle_id": "...", "quote": "triggers an additional time"}]
  }],
  "cards": {"<oracle_id>": {"name": "...", "mana_cost": "...",
    "type_line": "...", "oracle_text": "...", "power": "...",
    "toughness": "...", "color_identity": ["W"], "keywords": [],
    "layout": "normal", "faces": []}},
  "other_lane": [{"oracle_id": "...", "label": "...", "definition": "...",
    "quote": "..."}]
}
```

decisions/batch-N.json:
```json
{
  "schema": "foundry-decisions/1",
  "batch": 3,
  "axes": {"rule:trigger-doubling": {"verdict": "keep|kill|merge|rename",
    "merge_into": null, "new_slug": null, "definition_edit": null,
    "scope_edit": null, "note": "", "removed_members": [{"oracle_id":
    "...", "reason": ""}]}},
  "captain_axes": [{"slug": "...", "definition": "...", "scope": "...",
    "seed_members": ["<oracle_id>"]}],
  "captain_card_tags": [{"oracle_id": "...", "tag": "...", "note": ""}]
}
```

## After convergence (unchanged from v2, worker classes renamed)

- **Full-corpus closed coding** (BULK, the big overnight batch): all
  38,233 cards against codebook v1.0 + OTHER lane, two-pass,
  evidence-quote-or-discard. OTHER recurrence ≥5 → amendment queue for a
  post-run mini review batch in the same tool.
- **Reconciliation + ranking (DET + SUP):** join to Source A, rank for
  ratification by B-support × Tagger-thinness × DF-band fit (prefer
  under DERIVED_QUALIFY_DF_CEILING), A∩B as tiebreak.
- **Axis synthesis (SYNTH):** one ratification packet per axis — pattern
  written to FIT the evidence-quoted member list (card-first inversion),
  both polarities, actor-scope split, parameterized specifics (Delney
  pattern), near-miss panel, Tagger-redundancy note, single open ruling
  question.
- **Verification + widened-net audit (DET + BULK):** pattern implemented
  in `experiments/measure/axis_foundry.py`; every Stage-2 member the
  pattern misses is a known false negative to resolve or document; then
  the widened-net audit (regex hits + synonym templates + uncaught
  Tagger members) → MISSED / OVERCAUGHT / UNCERTAIN. All-paragraph
  scanning mandatory (Vexing Shusher lesson).
- **Deliverables:** AXIS-FOUNDRY-QUEUE.md, docs/axis-packets/ reviewed
  10–15 per round IN THE SAME TOOL (packets get a review mode), coverage
  metric (% corpus with ≥1 rule: tag) printed after every ratified
  round. Ratified axes land via Step 5's normal engine ritual — the
  foundry never lands engine code.

## Session plan

- **Session A:** build foundry_review.html + emit/reconcile scripts +
  axis_foundry.py skeleton; run coverage baseline + Source A mining;
  assemble batch 1 (500 cards, SYNTH, free-form); live-pricing cost
  estimate; Captain go-ahead; submit; END.
- **Session B (repeat per batch):** collect batch N; consolidate; emit
  review JSON; hand to Captain. After decisions return: reconcile, diff
  report, convergence metrics, assemble batch N+1, estimate, go-ahead,
  submit, end. Loop until the gate passes.
- **Session C:** full-corpus batch (estimate + go-ahead), end.
- **Session D:** reconcile, rank, synthesis, audit batch, end.
- **Session E:** finalize packets, deliverables, coverage metric, stop.
The corpus never passes through a session context window. All state
under experiments/out/foundry/, resumable cold. API key via env var,
gitignored.

## Guardrails (unchanged, restated)

Models propose, patterns dispose. Evidence-quote-or-discard.
Axis-first shipping bar: polarity + actor-scope split + near-miss panel.
Closed vocabulary after batch 1 (codebook + OTHER only). Two-pass
agreement at BULK; uncertain escalates. Fixed-seed samples at every
stage boundary; SUP eyeballs before anything feeds forward. Determinism
×2 on every DET artifact. Halt loudly on axis-boundary ambiguity — it
becomes an open question for Captain, never a silent merge or split.
