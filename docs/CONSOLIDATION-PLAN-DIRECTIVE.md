# CONSOLIDATION-PLAN-DIRECTIVE — run-1 consolidation plan artifact (session 2 of 4)

ZERO MUTATION, ZERO API SPEND. This session computes and writes ONE
artifact — the exact consolidation plan — and STOPS for Captain approval.
Nothing touches codebook.json. Governed by B-MIGRATION-DISCOVERY.md §10
(A1–A15) and §9 where unamended. PRECONDITION: session 1
(B-MIGRATION-DIRECTIVE.md rev 2) completed, all gates passed — verify in
the state-check (schema foundry-codebook/2); else HALT.

## 1. Inputs

corpus_pass_run1_parsed_final.json · corpus_pass_run1_discovery.json ·
corpus_pass_run1_consolidation_dry_run.json (reference only — recompute,
don't trust) · det_synth check artifact · docs/grammars.json ·
validate_slug.py · the /2 codebook (read-only) · gated corpus.

## 2. Build `experiments/out/foundry/corpus_pass_run1_plan.json`

Schema `foundry-consolidation-plan/1`. Deterministic (×2 byte-identical).
Contains input hashes and enumerates EVERY affected slug and oracle_id —
no aggregates without their underlying lists:

1. **member_additions** — codebook lane (recomputed; expect 14,255 across
   257 axes) + grammar lane existing axes (expect 1,127 across 20): each
   as full A1 assertions (class=llm, source_ref="run1", lanes, quote,
   corpus_ref).

   Total enumerated rows across items 1–4, for sizing: **~18,346** =
   16,088 codebook pairs (14,255 additions + 1,833 merges) + 1,297 grammar
   pairs (1,127 + 170) + 141 R5 + 607 virtual-node member rows + 213 A15
   rows. (Corrected 2026-08-01 per re-audit finding F3: an earlier figure
   of 17,526 omitted the 607 and the 213.) At ~425 B/row this artifact is
   ~7.8 MB / ~1.95M tokens — which is why it cannot itself be the external
   audit packet.
2. **assertion_merges** — run-1 confirmations of EXISTING members
   (A1 consequence; expect 1,833 codebook + 170 grammar + R5's 96):
   llm assertions merged onto existing member records.
3. **new_axes** — the 95 virtual-node candidates CLASSIFIED one-by-one
   (AG-COUNT-01; categories: instantiate / join-existing / redirect /
   report-only / collision-killed / collision-renamed; totals must equal
   95). Expected: 93 instantiate (A14), rule:grants-haste →
   redirect-per-D4 (Zidane → rule:temporary-keyword-grant),
   rule:draw-second-card-trigger-token → report-only.
4. **promotions** — R5 (141 exact-match: 45 additions + 96 merges, each
   listed) and A15 (the 213-row set: EACH row re-validated through
   validate_slug as a grammar-lane label; rows failing validation fall
   back to discovery and are listed as such; original_lane/effective_lane
   recorded per assertion; the `<state>` cluster's 10 rows = report-only).
5. **routing artifact** — `foundry-killed-slug-routing/1` (A14/H-02):
   every killed/merged/renamed-slug hit enumerated with a closed action
   (redirect / split / report / discovery / reject) and explicit targets;
   M8-violating labels list their per-class split targets. No "quote
   fits" predicates — every instance is decided IN THE PLAN.
6. **taxonomy items** — revivals as status flips to `deferred` (A2), the
   two kill-note corrections, the whole-slug alias (A6), each stated as
   exact history-entry text.
7. **report_rows** — everything deferred to Captain eyes, with counts.
8. **expected_final_counts** — exact post-apply numbers: axis counts by
   status, member rows, assertion rows, per-category totals. No "~", no
   drift tolerances: session 3 matches these exactly or halts (A14).

Dedupe law: a (slug, oracle_id) arriving via multiple routes appears
EXACTLY ONCE in member_additions with all its assertions listed (or once
in assertion_merges if the member exists); the plan is internally
duplicate-free by construction and lint-checked for it.

**Same-run collapse rule (CAPTAIN-RATIFIED 2026-08-01, re-audit finding
F2).** Dedupe alone is insufficient under multi-assertion /2: `merge_assertion`
halts on a duplicate (class, source_ref), and run 1 is MEASURED to contain
35 codebook-lane + 3 grammar-lane + 6 free-lane intra-run duplicate
emissions — the same card emitting the same label twice, potentially with
different quotes or lanes. Left unruled, session 2b would have to invent a
collapse policy (violating its zero-judgment charter) or session 3 would
halt mid-apply. Therefore:

- Two or more emissions from the SAME run for the same (slug, oracle_id)
  collapse to a SINGLE assertion.
- Lane precedence: `codebook` > `codebook-grammar` > free-promoted.
- Quote tie-break within the winning lane: first in deterministic parse
  order.
- The plan records the collapse count per category so it is auditable;
  discarded duplicates are never silently dropped.

This is a ruling, not a heuristic: 2b applies it mechanically and halts on
any same-run duplicate the rule does not fully resolve.

## 3. Reporting and stop

Print counts and slugs only (quotes stay in the artifact). Produce a
short human summary section INSIDE the plan file (Captain-readable:
category totals, notable rows, the 95-node classification table). Commit
the plan-generator script; the plan artifact itself is gitignored output —
record its sha256 in the report. Then STOP:

1. Captain reviews the plan.
2. Designated external re-audit checkpoint (A12): assemble
   `docs/B-CONSOLIDATION-REAUDIT-PACKET.md` — amended schema (§10 A1) +
   the plan's human summary + the full category enumeration (sized to
   fit) + the same red-team charge/disclosure as the first packet — for
   Captain to run past a different model family.
3. Session 3 (APPLY) runs only on Captain's explicit go with the plan
   hash it approves.

Spend $0.00 / cumulative $90.51 / headroom $49.49.

## 4. Standing discipline

Zero mutation of codebook.json/grammars.json in this session under any
circumstance · halt loudly · verify-or-drop · transcript hygiene ·
determinism ×2 on the plan artifact · one session, this work item only.
