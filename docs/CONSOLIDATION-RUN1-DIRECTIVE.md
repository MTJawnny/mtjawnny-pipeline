# CONSOLIDATION-RUN1-DIRECTIVE — M=1 consolidation of full-corpus SYNTH run 1 (2026-08-01)

Captain-triggered. ZERO API SPEND this session — no Batch API, no synchronous
calls, no count_tokens against the live API. Everything here is local compute.
If any step appears to require spend, that is a HALT, not a judgment call.

## 0. Orientation reads (in order, before touching anything)

1. docs/MASTER-HANDOFF.md
2. docs/MASTER-HANDOFF-ADDENDUM-2.md
3. docs/MASTER-HANDOFF-ADDENDUM-3.md
4. docs/MASTER-HANDOFF-ADDENDUM-4.md (§2 resume point, §4 lane-aware consensus
   ruling, §6 punch list, §7 discipline)
5. docs/CORPUS-PASS-PLAN.md (lanes, steps 7–8, EMERGENCY COST STOP section
   incl. the run-1 ACTUAL entry)
6. docs/RESUME-NOTE.md (run-1 mechanics, resume steps 5–7)
7. docs/CODEBOOK-NAMING-GRAMMAR.md (validator rules, sec.11 downgrade rule)

Print a state-check first: codebook.json version + active axis count, raw
results file present y/n, git status clean y/n. Then proceed.

## 1. Scope

Consolidate run 1's SYNTH output (M=1, single run) into codebook.json per
CORPUS-PASS-PLAN steps 7–8 under the ratified lane-aware consensus ruling
(2026-08-01, ADDENDUM-4 §4). Also: verify the batch-8 lane-aware recompute
was reported (punch item), update the stale CORPUS-PASS-PLAN status table,
and log the new punch items listed in §8 below.

OUT OF SCOPE — do not do any of these even if they look adjacent:
- No corroboration run, no M=2, no wave targeting execution (future trigger).
- No schema pass work (parents, facets, S1–S7, T1). Ledger appends only if a
  step below explicitly says so.
- No ratification of free-lane discovery candidates into new axes. Discovery
  output is an ARTIFACT for Captain review, not codebook truth.
- No engine/scoring changes. G1: ratified constants untouchable
  (DERIVED_WEIGHT=0.5, DERIVED_QUALIFY_DF_CEILING=172, MV mults, bands).
- No renames, no naming-audit execution (132-slug backlog stays backlog).

## 2. Inputs and pre-flight verification

- `experiments/out/foundry/corpus_pass_run1_raw_results.jsonl` — main batch
  results, PLUS the two remediation result sets (pack-198's two N=20
  sub-packs; the 164-card recovery's 17 sub-packs). Verify all three sources
  are ingested into one result set before consolidation. If the remediation
  results live in separate files, locate them from the run-1 session's
  commits (afa320b, 6ca0db3) — do not assume they were merged into the main
  JSONL. HALT if they cannot be located.
- Verify total distinct oracle_ids covered = 32,557 exactly, matching the
  gate-passing set (foundry_common.load_corpus_gated()). Any shortfall or
  surplus is a HALT row.
- Verify the 24 malformed/hallucinated oracle_id strings (fabricated
  -duplicate-skip / -DUP / -placeholder suffixes) are excluded from the
  consolidation input. Print the count excluded (expect 24; a different
  number is a report row, not a silent fix).
- Gate #0: every oracle_id in the input must pass gate_passes(). Expect zero
  failures since the submission set was pre-gated; any failure is a HALT row.
- `experiments/out/foundry/codebook.json` — current v0.7-post-walk state
  including the full-corpus DET pass membership (source="DET" on the 39
  DET-owned axes, applied 2026-08-01 per RESUME-NOTE). Verify the DET-pass
  state is present (spot-check one DET-owned axis has full-corpus-scale
  membership, not sampling-era counts) before consolidating on top of it.
- `docs/det-patterns-v2.json` — the authoritative DET set for this arc.
- `docs/grammars.json` — ratified grammar families.

## 3. Backup law (before any mutation)

Timestamped pre-mutation backups of codebook.json AND grammars.json to
`experiments/out/foundry/backups/`, named per the existing convention
(cf. codebook.v0.7.pre-det-pass.20260801-013346.json). No mutation of either
file before both backups exist and are printed in the transcript.

## 4. Lane handling (the core of the session)

**Codebook lane (16,195 labels expected):** each label is a membership
confirmation for an existing active axis. Union the card into that axis's
membership — union only, never removal, never overwrite. Provenance on every
SYNTH-added membership: source=SYNTH, consensus tier=provisional, runs=[run1].
No corroborated tier exists at M=1 — the schema must carry this explicitly
(tier field present, value "provisional"), not omit it. If the codebook.json
membership schema has no provenance/tier field shape to carry this, HALT and
propose a shape — do not invent one silently.

- A codebook-lane label naming a killed or merged slug is a report row
  (count + list), routed per the existing reconcile conventions, never
  silently written.
- A codebook-lane label naming a DET-owned slug should be impossible (strip
  verified, 0 structural violations in the run-1 check). If any appears at
  consolidation time anyway, HALT — that contradicts the run-1 report.

**Codebook-grammar lane (2,561 labels expected):** every label passes through
validate_slug.py. Valid composition against a ratified grammar family →
treated as codebook-lane membership (instantiating the virtual node on first
quote-verified member per the lattice-grammar ruling, lane recorded as
codebook-grammar). Validation failure → downgrade to lane=free per
CODEBOOK-NAMING-GRAMMAR.md sec.11, counted and reported. Any
activation-restriction-family label under ANY lane → reject outright (D-4),
counted and reported. This is the first live full-scale exercise of the
stage1b/consolidate wiring: per ADDENDUM-4 punch item 6, treat anomalies as
HALT rows, not curiosities. Print downgrade and rejection counts.

- Virtual-node instantiation requires the quote-verified member condition:
  the SYNTH output's evidence quote must be present for the instantiating
  member. A grammar-valid slug arriving with no evidence quote does not
  instantiate a node — report row.

**Free lane (28,243 labels expected + any downgrades from above):** NEVER
written to codebook.json as membership. Per the lane-aware ruling, free-lane
output is UNIONED into consolidation as discovery candidates only. Build:

`experiments/out/foundry/corpus_pass_run1_discovery.json` — canonicalized
(canonicalize_label(), the permanent reconcile infra with the mass→mas
stemming fix) label clusters: canonical form, raw variant strings, member
oracle_id count, DF, and a sample of up to 10 member card NAMES (names only —
transcript hygiene applies to the file's console handling, and NO raw oracle
text or SYNTH evidence blobs printed to console at any point; quotes may
live in the artifact file itself).

- The 111 soft DET-convergence flags (free-lane labels matching DET-owned
  pattern names on cards already DET-members): log them in the discovery
  artifact tagged det-convergent. They are corroboration signal for the
  future wave, not membership, not contradiction.
- Free-lane labels matching an ACTIVE codebook slug's exact string (SYNTH
  reinventing a known axis in the free lane): count and report as a
  near-miss metric (this is the lattice-grammar kill-switch metric's
  denominator context), and treat as codebook-lane confirmation ONLY if the
  slug string is an exact match post-canonicalization — anything fuzzier
  stays discovery. Report the count either way.
- Free-lane labels matching a KILLED slug: report row, stays discovery,
  flagged killed-slug-reinvention.

## 5. Determinism and integrity

- Determinism ×2: run the full consolidation twice from the backed-up
  pre-state; outputs must be byte-identical (codebook.json and the discovery
  artifact both). Seed anything that needs seeding. Non-identical output is
  a HALT.
- G4 generated-artifacts law: never hand-edit codebook.json or the discovery
  artifact. Fix the producer, re-run, diff.
- All-faces discipline applies to any oracle-text lookup performed for
  quote verification.
- Post-consolidation sanity panel (print, don't just compute): active axis
  count before/after (should change ONLY by grammar virtual-node
  instantiations), total membership rows before/after, count of axes whose
  membership grew, top-10 axes by SYNTH-added members (slugs + counts only).

## 6. Wave-targeting inventory (compute and report, do NOT act)

As a report section only — the corroboration wave is not authorized — emit
the counts the wave targeting will need: cards that are free-lane-heavy
(define: ≥3 free-lane labels and 0 codebook-lane labels; print the threshold
used), validator-downgraded composition count, killed/merged-slug label
count, det-convergent flag count, and how many site-featured cards (the 12
built card pages — resolve their oracle_ids) fall in each category. Numbers
and slugs only. No submission preparation.

## 7. Batch-8 recompute verification (punch item, ADDENDUM-4 §6 #1)

Verify the lane-aware batch-8 agreement recompute (ordered with the run-1
trigger) exists and was reported: locate its output/report in the repo. If
found: quote its headline numbers in this session's report. If not found:
say so plainly — it becomes a punch item, do NOT run the recompute in this
session unless it is zero-spend local re-scoring of already-fetched batch-8
results (it should be; if and only if that is verifiably true, run it and
report).

## 8. Documentation updates (same session, before the report)

1. CORPUS-PASS-PLAN.md status table: step 4 → Done (DET pass applied
   2026-08-01 per RESUME-NOTE, det-patterns-v2), step 6 → Run 1 complete +
   consolidated (M=1, provisional tier; corroboration waves future-trigger),
   add step 6.5 or a note line for this consolidation with date + commit.
2. Punch list additions (wherever the live punch list is maintained):
   - Contradiction-check heuristic gap: true opposite-direction DET-SYNTH
     contradiction detection needs semantic judgment beyond the two shipped
     heuristics; close it during corroboration waves (already a ratified
     wave-targeting category).
   - Batch-8 recompute status per §7's outcome.
3. RESUME-NOTE.md: append one line noting consolidation executed this
   session (date + commit) so the historical record chains cleanly.

## 9. Report (standing format, end of session)

- Lane actuals: codebook / codebook-grammar (valid, downgraded, D-4
  rejected) / free, against the run-1 expected counts (16,195 / 2,561 /
  28,243) — any delta explained.
- Consensus tiers: corroborated N/A (M=1, stated explicitly), provisional
  membership count added, virtual nodes instantiated (list slugs).
- Discovery artifact stats: cluster count, top-20 canonical labels by DF
  (labels + counts only), det-convergent count, killed-slug-reinvention
  count, exact-match reinvention count.
- Sanity panel numbers (§5).
- Wave-targeting inventory (§6).
- Batch-8 recompute status (§7).
- Spend: $0.00 this session; cumulative arc $90.51 unchanged; headroom
  $49.49 against the $140 ceiling.
- Punch list delta.
- Commits made (hashes + one-line messages).

## 10. Standing discipline (binding, unchanged)

Discuss-before-build on anything structurally ambiguous · HALT LOUDLY on
genuine ambiguity, failed gates, unspecified decisions — this doc's HALT
rows are not suggestions · verify-or-drop · transcript hygiene (no raw
oracle text or SYNTH blobs to console; counts/slugs/names/paths only) ·
pre-mutation backups (§3) · determinism ×2 (§5) · G1 constants untouchable ·
G4 no hand-edits · Gate #0 on every corpus probe · one session, this work
item only. Continue through all phases — only stop on genuine ambiguity, a
failed gate, or an unspecified decision.
