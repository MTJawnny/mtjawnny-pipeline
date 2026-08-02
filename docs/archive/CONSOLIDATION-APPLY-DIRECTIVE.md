# CONSOLIDATION-APPLY-DIRECTIVE — execute the approved plan (session 3 of 4)

ZERO API SPEND. PRECONDITIONS (verify all in the state-check, else HALT):
session 1 gates passed (/2 schema live); session 2's plan artifact exists;
Captain's explicit go names the plan sha256 being executed; external
re-audit checkpoint outcome recorded (done, or explicitly waived by
Captain). Governed by B-MIGRATION-DISCOVERY.md §10 + §9.

## 1. The one rule

This session applies EXACTLY the approved plan — zero judgment, zero
recomputation of decisions. The applier reads corpus_pass_run1_plan.json
(hash-checked against the approved hash) and executes its categories via
foundry_codebook merge_assertion / atomic-write primitives:

1. member_additions and assertion_merges — as enumerated.
2. new_axes — the 93 instantiations (axis records per plan: definition,
   scope, source="B-only", grammar-lane history note), the D4 redirect,
   the report-only rows untouched.
3. promotions (R5 + A15) — as enumerated, with lane fields preserved.
4. routing artifact actions — as enumerated.
5. taxonomy items — revival status flips to `deferred` (A2), kill-note
   history corrections, the whole-slug alias entry (A6).

Anything the plan does not enumerate DOES NOT HAPPEN. If live state
differs from the plan's recorded pre-state (hash of the /2 codebook at
plan time), HALT — regenerate and re-approve the plan instead of
adapting.

## 2. Gates

Backup law + restore drill first. After apply: expected_final_counts
match EXACTLY (any mismatch = restore and halt — no drift categories,
A14); lint clean; independent spot-verifier: sample 500 fixed-seed plan
rows re-checked against the written file 1:1; determinism ×2 (apply twice
from backup, byte-identical). Quotes never printed to console.

## 3. Companion artifacts (same session, after gates)

- `experiments/out/foundry/card_axes_index.json` — derived card-level
  view: oracle_id → {axes, dfc (card_faces[0].image_uris rule, derived
  fresh), gamechanger (from tags/gamechangers.yaml if present)}.
  Deterministic; regenerated after every codebook write; never
  authoritative.
- Seed `tags/gamechangers.yaml` (format spec + empty list, committed).
- Correct corpus_pass_run1_consolidation_dry_run.json's stale figures
  per B-MIGRATION-DISCOVERY.md §6 (the deferred correction — G4: done by
  regenerating via its producer path or superseding it with a corrected
  successor artifact, never hand-edit).
- CORPUS-PASS-PLAN status table: step 6 → consolidated (M=1,
  provisional; corroboration waves remain future-trigger). RESUME-NOTE
  line.

## 4. Report

Standing format: category actuals vs plan (exact), sanity panel (axis
counts by status before/after, member and assertion row totals, top-10
axes by additions), report-row inventory for Captain, new codebook
sha256 + size, spend $0.00 / cumulative $90.51 / headroom $49.49,
commits.

## 5. Standing discipline

Halt loudly · G1 · G4 · determinism ×2 · pre-mutation backups ·
transcript hygiene · one session, this work item only. The corroboration
wave remains a FUTURE Captain trigger.
