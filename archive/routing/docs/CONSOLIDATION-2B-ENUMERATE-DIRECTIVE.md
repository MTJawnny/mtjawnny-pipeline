# CONSOLIDATION-2B-ENUMERATE-DIRECTIVE — the arithmetic, alone (session 2b of 5)

ZERO API SPEND. ZERO MUTATION of codebook.json or grammars.json: this
session writes exactly one artifact, the full consolidation plan. It makes
NO decisions. Every judgment was made and frozen in session 2a.

Governed by B-MIGRATION-DISCOVERY.md §10 (A1–A15) and §9 where unamended.
Supersedes, with CONSOLIDATION-2A-CLASSIFY-DIRECTIVE.md, the single-session
CONSOLIDATION-PLAN-DIRECTIVE.md.

PRECONDITIONS (verify all in the state-check, else HALT):
- session 1 complete, codebook.json schema `foundry-codebook/2`, lint clean;
- the live codebook sha256 matches the one 2a recorded — if the codebook has
  moved since 2a classified against it, HALT and re-run 2a rather than
  expanding a decision set made against a different state;
- `corpus_pass_run1_classification.json` exists and its sha256 matches the
  one Captain's go names;
- the A12 external re-audit outcome is recorded, or explicitly waived by
  Captain in writing.

## 1. The one rule

**Anything session 2a did not enumerate DOES NOT HAPPEN.** On encountering
any case 2a's artifact does not resolve — an unclassified node, an
unrouted killed-slug hit, an unresolved same-run duplicate, a promotion row
with no recorded validation outcome — HALT and name it. Do not infer, do not
fall back to a default, do not "route the obvious way." A gap in 2a is a
defect in 2a and is fixed by re-running 2a and re-approving, not by
exercising judgment here. This session's whole value is that it has none.

## 2. Build `experiments/out/foundry/corpus_pass_run1_plan.json`

Schema `foundry-consolidation-plan/1`. Deterministic (×2 byte-identical).
Records input hashes, the 2a artifact's sha256, and the live codebook
sha256 as the plan's recorded pre-state (session 3 checks against it).

Expected scale, for sizing: **~18,346 enumerated rows** = 16,088 codebook
pairs (14,255 additions + 1,833 merges) + 1,297 grammar pairs (1,127 + 170)
+ 141 R5 + 607 virtual-node member rows + 213 A15 rows; ~7.8 MB.

1. **member_additions** — codebook lane (recomputed: expect 14,255 across
   257 axes) + grammar-lane existing axes (expect 1,127 across 20) + the
   virtual nodes' 607 member rows + R5's 45 + A15's promoted rows, each as a
   full A1 assertion: `class=llm`, `source_ref="run1"`, `original_lane` /
   `effective_lane` as 2a recorded them, `quote`, `corpus_ref`,
   `evidence_status`.
2. **assertion_merges** — run-1 confirmations of EXISTING members (expect
   1,833 codebook + 170 grammar + R5's 96): llm assertions to be merged onto
   member records that already exist.
3. **new_axes** — the axis records for 2a's `instantiate` classifications:
   definition, scope, `source="B-only"`, grammar-lane history note, each
   exactly as 2a specified.
4. **promotions / routing / taxonomy** — transcribed from 2a, expanded to
   per-row assertions where the row is a membership row.
5. **expected_final_counts** — the exact post-apply numbers session 3 must
   match: axis counts by status, member rows, assertion rows, per-category
   totals. No "~", no tolerances, no drift categories (A14). Computed HERE,
   after the decisions are frozen, which is what makes them trustworthy as
   session 3's gate.

**Dedupe law.** A (slug, oracle_id) arriving via multiple routes appears
EXACTLY ONCE — in `member_additions` with all its assertions listed, or once
in `assertion_merges` if the member already exists. The plan is internally
duplicate-free by construction and lint-checked for it. Same-run duplicates
are resolved by LOOKUP into 2a's `same_run_duplicates`; encountering one 2a
did not resolve is a halt, per §1.

## 3. Gates

- Every 2a `expected_counts` entry matches the expansion EXACTLY, or halt
  and report the divergence per category. This is the closed loop that makes
  an external audit of 2a alone meaningful.
- Plan is internally duplicate-free.
- No (class, source_ref) pair would collide on merge — dry-check every
  planned merge against the live codebook's existing assertions, since
  `merge_assertion` halts on duplicates and session 3 must not discover that
  mid-apply.
- Determinism ×2, byte-identical.

## 4. Reporting and stop

Print counts only; quotes to the artifact (A14). Commit the expander script;
the plan artifact is gitignored output — record its sha256 in the report.

Then STOP. Session 3 (APPLY, CONSOLIDATION-APPLY-DIRECTIVE.md) runs only on
Captain's explicit go naming the plan sha256 it approves.

Spend $0.00 / cumulative $90.51 / headroom $49.49.

## 5. Standing discipline

Zero judgment · zero mutation of codebook.json/grammars.json · halt loudly ·
transcript hygiene · G1 · G4 · determinism ×2 · one session, this work item
only.
