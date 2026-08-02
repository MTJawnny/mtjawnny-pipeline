# Batch 8 — A/B dress rehearsal spec (packed vs. single-card harness)

Status: **SPEC ONLY. Not assembled, not submitted.** Per Captain's 2026-07-31
directive (point 4). G7 (walk-ratification session) already ruled batch 8
is not to be assembled as an ordinary triage batch — this document defines
it instead as the acceptance-gate experiment for the packed-request
architecture before it's trusted with the full 32,557-card corpus pass.
Submission requires Captain's separate, explicit trigger; this document
authorizes nothing.

## 1. What's being tested

Packing (N cards/request, codebook block sent once) cuts the priced cost of
the full-corpus SYNTH pass by ~90%+ (see the re-pricing table in this
session's report). Before trusting it with 32,557 cards, verify it doesn't
silently degrade SYNTH's judgment quality relative to the harness every
prior batch (1–7) was measured against. This is a QUALITY experiment, not
a cost experiment — the output-trim proposal (`docs/archive/OUTPUT-TRIM-PROPOSAL.md`)
is a SEPARATE, unratified change and is deliberately NOT exercised here;
both harnesses below use the current, full, untrimmed `OUTPUT_SCHEMA` so
packing is the only variable.

## 2. Corpus

**1,200 gate-passing cards**, selected via the same hand-picked-confirmation
+ DET-stratified-random-fill methodology already used for batches 2–7
(`foundry_assemble_batchN.py` pattern) — not hand-picked in this spec
document; card selection is an assembly-time action, out of scope for a
spec. The SAME 1,200 oracle_ids run through both harnesses (this is what
makes the comparison a diff, not two independent samples).

## 3. The two harnesses

- **OLD (single-card)**: `foundry_stage1b.py`'s existing `build_request()` —
  1,200 requests, `custom_id = oracle_id`, one card per request, full
  ~20K-token codebook reference resent every time.
- **PACKED**: `build_packed_request()` (this session) — pack size **N=20**
  recommended (60 requests of 20 cards each; gives 60 samples per pack
  position for §5's tail check — a smaller N would thin the tail-position
  sample, a larger N would leave fewer packs to compare against but
  stronger tail signal if one exists; 20 is a reasonable middle point, not
  asserted as the eventual production N). `custom_id = "pack-<n>"`,
  `pack_oracle_ids()` chunking (deterministic, order-preserving — no
  shuffling, so each card's IN-PACK POSITION is known and stable).

Both harnesses can be submitted as ONE Message Batch (1,260 total requests,
custom_ids prefixed `single-<oid>` / `pack-<n>` to disambiguate at
fetch-results time) for one batch ID to track, or as two separate
submissions — an implementation choice, not a design constraint.

## 4. Acceptance gate — per-card agreement diff

For each of the 1,200 cards, extract its axis set from BOTH harnesses'
results (packed-harness extraction: locate the card's oracle_id key within
its pack's response object) as `{(lane, label), ...}` pairs, then compute:

- **Exact-set match** (boolean): are the two axis sets identical?
- **Jaccard similarity** (soft measure): `|A ∩ B| / |A ∪ B|`, for partial-
  credit cases (e.g. packed harness found 2 of the 3 axes the single-card
  harness found, same 2, no extras).

Aggregate: overall exact-match rate, mean Jaccard, and a listed diff table
of every disagreeing card (which axes appeared in one harness and not the
other) for manual spot review — not just a pass/fail number, since the
INTERESTING failures are the specific patterns packing loses or hallucinates,
not just the count.

**Proposed acceptance threshold** (Captain's call to set the real bar):
**≥90% exact-set-match rate** across the 1,200 cards. Below that, packing
is not yet trustworthy for the full pass at this N — either lower N, or
reject packing and eat the single-card cost.

Caveat to build into the read of this number: SYNTH is not perfectly
deterministic even under identical conditions (no batch has ever re-run
the same card twice to measure that baseline noise floor), so 100%
agreement is not the right bar and shouldn't be expected — some
disagreement is normal model variance, not necessarily packing-caused.
This spec does not currently include a same-harness-twice control to
separate "packing effect" from "baseline model variance"; if the 90%
threshold is a close call, that control is the natural next experiment
before over-reading a borderline result.

## 5. Tail-position quality check

The specific risk packing introduces that single-card requests can't: a
"lost in the middle" effect, where card 18 of 20 in a big request gets
worse attention than card 2 of 20. `pack_oracle_ids()`'s deterministic,
non-shuffled chunking means every card has a known, stable position
(1..20) within its pack.

Bucket the same per-card agreement measurements from §4 **by position**
(60 cards at position 1, 60 at position 2, ..., 60 at position 20 — full
coverage since 1,200 / 20 = 60 exactly) and compute the exact-match rate
per bucket. Look for:

- A monotonic or clearly declining trend as position increases.
- **Proposed secondary guard** (Captain's call): no position bucket's
  agreement rate may fall more than 10 percentage points below the
  average of positions 1–5. A violation here is a real signal even if the
  AGGREGATE §4 gate passes — it means quality is fine on average but
  specifically degrading toward the tail, which would argue for a smaller
  N in production rather than N=20, independent of the aggregate pass/fail.

## 6. Cost estimate (live pricing, same method as the full-pass re-pricing)

Real measured tokens: single-card ≈20,092 tok/request; N=20 pack ≈23,776
tok/pack (≈1,189 tok/card). Output tokens: real batch-6/7-derived estimate
(155 tok/card single, ≈166 tok/card packed incl. the JSON-key wrapper
overhead), full untrimmed schema on both sides (no output-trim in this
experiment, see §1).

| Harness | Requests | Input tokens | Output tokens | Intro batch cost | Standard batch cost |
|---|---:|---:|---:|---:|---:|
| OLD (single-card) | 1,200 | 24,110,160 | 172,658 | $24.97 | $37.46 |
| PACKED (N=20) | 60 | 1,426,560 | 186,158 | $2.36 | $3.54 |
| **Batch 8 total (both harnesses)** | 1,260 | — | — | **$27.33** | **$41.00** |

Expect the intro figure (Sonnet 5 intro pricing runs through Aug 31, 2026;
batches typically complete within an hour).

## 7. What's not built yet

The per-card diff tool (§4) and the position-bucketed aggregator (§5) don't
exist — this is a spec, not an implementation. If Captain ratifies running
batch 8, the next session's scope is: assemble the 1,200-card set, extend
`foundry_stage1b.py`'s `submit`/`fetch-results` for the packed custom_id
shape, and write the diff/aggregation script before results can be read.

## 8. Explicit non-actions

No cards selected, no requests built, no batch submitted, no API spend
incurred by this document. Submission requires Captain's separate,
explicit go-ahead per the standing Batch API cost-estimate rule.
