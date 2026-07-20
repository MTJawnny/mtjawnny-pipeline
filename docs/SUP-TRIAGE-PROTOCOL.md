# SUP-TRIAGE-PROTOCOL — foundry batch review loop (ratified 2026-07-18)

Target path: docs/SUP-TRIAGE-PROTOCOL.md (pipeline repo).
Supersedes row-level review in foundry_review.html for batch verdicts.
Ratified deviation from T3-AXIS-FOUNDRY-v3: SUP performs full-pass triage;
Captain ratifies at proposal level. The review tool remains available for
ad-hoc inspection. Batch-1 precedent: 0 reversals on a fixed-seed 30-row
override check.

BATCH-1 PROVENANCE NOTE: batch 1 predates the annotation convention; its
ratification happened in chat (SUP-triage session, 2026-07-18) and its
authoritative record is decisions/batch-1.json itself. TRIAGE-BATCH-1.md
carries no written annotations by design. The written convention applies
from batch 2 onward.

## The loop (per batch N)

1. `/triage-alpha N` — cheap model. Consolidate + enrich + emit DIGEST.
2. `/triage-beta N` — top model. Read digest, write TRIAGE-BATCH-N.md
   with prefilled verdicts + questions + override sample. STOP.
3. Captain edits TRIAGE-BATCH-N.md in place (see annotation convention),
   checks the override sample against card text.
4. `/triage-emit N` — cheap model. Parse annotations -> decisions ->
   reconcile -> codebook vN -> assemble batch N+1 -> cost estimate -> STOP
   for Captain's Batch API go-ahead.

Chat (Fable 5) is reserved for: protocol changes, ruling disputes,
step-back audits, and periodic spot-audits of beta's triage quality.
No data files shuttle through chat.

## Artifact contracts

**DIGEST** (`experiments/out/foundry/review/digest-batch-N.md`, target
under ~60KB): per axis one header line
`slug | scope | n | quote-DF min/med/max | reminder-count` + definition +
one line per member (card name, quote-DF, reminder flag, quote <=80ch);
token groups sorted by size with member labels AND card names; stats
block (instance distribution, discard audit, reminder-flag split
exact-vs-substring); Alchemy-row and layout anomalies listed.
Generated deterministically (x2 byte-identical).

**TRIAGE-BATCH-N.md** (`docs/`): lanes KILL / MERGE / KEEP each entry
prefilled `VERDICT: <verdict>` with a one-line reason; QUESTIONS lane,
each `Q<i>` a tight either/or ending `-> RULE: ______`, max 8;
OTHER-lane promotions with named members; override sample: 30 rows,
fixed seed = 20260718 + N, drawn from confident calls only, table of
axis | verdict | sample member | quote; batch-feedback section for the
next SYNTH prompt.

**Decisions** (`experiments/out/foundry/decisions/batch-N.json`,
schema sup-triage-decisions-v1): per-axis verdicts
KEEP/KILL/MERGE(merge_into)/RENAME(rename_to, params, member_removals,
notes), other_lane promotions, captain_authored_axes (provenance human,
corpus-validated), ledger_candidates_carry_forward, new_rulings,
punch_list, override_spotcheck record (seed, n, reversals, result).

## Captain annotation convention (inside TRIAGE-BATCH-N.md)

- Change a verdict: edit the word after `VERDICT:` (KEEP/KILL/MERGE/RENAME).
  For MERGE add `INTO: rule:<slug>`; for RENAME add `TO: rule:<slug>`.
- Answer a question: fill the `-> RULE:` blank in place.
- Anything else: add a line starting `NOTE:` under the entry.
- New axis from Captain: add a block under `## CAPTAIN-AUTHORED` with
  slug, definition, example cards (emit will corpus-validate, provenance
  human, full weight, skips model pipeline per standing ruling).
- Untouched entries = ratified as proposed.

## Standing rules (bind every session in this loop)

- Vocabulary: "tier" = card tiers only; worker classes DET/BULK/SYNTH/SUP.
- Evidence-quote-or-discard on every per-card assignment; oracle text only.
- All-paragraph / all-faces scanning everywhere.
- Determinism: fixed seeds, explicit sort keys, x2 byte-identical gates.
- Paper rows preferred over A- Alchemy variants in sampling and emit.
- Rank buries, never excludes; DERIVED_QUALIFY_DF_CEILING = 172;
  DERIVED_WEIGHT = 0.5.
- Bare keywords / reminder text / procedural riders are never axes;
  killed keyword mechanics go to docs/KEYWORD-LEDGER-CANDIDATES.md in the
  same commit set.
- Nothing model-generated is load-bearing without Captain ratification.
  HALT LOUDLY on ambiguity; never lossy-map, never guess.
- Every Batch API submission: cost estimate from CURRENT pricing docs +
  Captain go-ahead. Never remembered prices.

## Convergence metrics (report both, every batch)

(a) Spec metrics: OTHER-lane rate and kill/merge/rename rate — annotated
that raw OTHER rate is method-inflated under exact-match clustering and
deflated once two-lane codebook labeling starts; read trend, not level.
(b) Ratified primary: OVERRIDE RATE — Captain reversals / beta's
confident calls, plus the fixed-seed spot-check result. The bootstrap
gate question is whether the pipeline's judgment converges on Captain's.
