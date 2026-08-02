# CONSOLIDATION-RUN1-DIRECTIVE-2 — run-1 consolidation on the /2 schema (session 2 of 2)

Supersedes docs/CONSOLIDATION-RUN1-DIRECTIVE.md §4 onward where they
differ; its §0–§3 orientation, input verification, and backup law carry
over unchanged. Ratified 2026-08-01 (B-MIGRATION-DISCOVERY.md §9, rulings
R1–R13). ZERO API SPEND. PRECONDITION: B-MIGRATION-DIRECTIVE.md completed
with all gates passed (codebook.json is foundry-codebook/2) — verify in
the state-check; if not, HALT.

## 1. Scope

Write run 1's consolidation into the /2 codebook: codebook-lane and
grammar-lane membership, the R5/R6 promotions, the R7 collision handling,
the R8 audit executions, R9 synonym additions, R10 routing, the derived
card-index artifact, and the deferred dry-run-report corrections. Same
out-of-scope list as the original directive (no corroboration run, no
schema pass, no engine changes, no naming-audit execution).

## 2. Lane writes (extends foundry_consolidate_run1.py into the writer)

All SYNTH-added members: `{oracle_id, class:"llm", tier:"provisional",
runs:["run1"], quote:<evidence quote from parsed_final>}` via
foundry_codebook.add_member. Union only — never removal, never overwrite.

- **Codebook lane:** the 14,255 new members across 257 axes (dry-run
  `codebook_lane_would_add`). The 1,833 already-member confirmations stay
  NO-OPS — counted and reported as future corroboration-wave input, NOT
  written into `runs` (R12: no silent policy invention).
- **Grammar lane, existing axes:** the 1,127 new members across 20 axes
  (170 no-ops likewise).
- **Grammar lane, virtual nodes:** add killed/merged/renamed checks to the
  grammar-lane classifier FIRST (R7) — a grammar-valid slug matching a
  non-active record is never silently instantiated or overwritten. Then:
  - 92 clean nodes instantiate (axis record: definition from the dry run,
    source="B-only", lane bookkeeping in history, status active).
  - `rule:grants-haste` (bare, killed): does NOT instantiate (b1-Q1
    stands). Its 1 member (Zidane, Tantalus Thief) routes to
    `rule:temporary-keyword-grant` per D4, with its quote (R7).
  - `rule:draw-second-card-trigger-token` (renamed shell): REPORT ROW —
    print the member's name + quote for Captain; no write.
  - The 12 faceted grants-* nodes are part of the 92 — instantiate
    normally (hexproof precedent, R7).

## 3. Ratified promotions (R5, R6)

- **R5:** the 141 exact-match free-lane reinventions become codebook-lane
  confirmations: 45 new members written (llm/provisional/runs=[run1] +
  quotes), 96 no-ops counted. Axis history notes record
  "free-lane exact-match promotion (R5)".
- **R6:** the 5 reorder clusters / 213 rows promote:
  targeted-destruction-creature (188) instantiates its grammar node;
  cant-be-blocked-except-by-count (21) instantiates;
  activated-tap-opponent-artifact (1) instantiates;
  etb-create-token-blood (2) and etb-create-token-clue (1) join their
  session-2 instantiated nodes. Recompute cluster membership fresh from
  the discovery artifact (do not trust remembered row counts; small
  drift is a report row, large drift is a HALT). The `<state>`-placeholder
  cluster (10 rows) is a REPORT ROW, stays discovery.
- Dedupe: a card arriving via multiple routes (grammar lane + R6, etc.)
  is written once; add_member's duplicate halt enforces it — catch the
  duplicate BEFORE calling (id-set check), count as no-op.

## 4. Audit executions (R8, R9)

1. REVIVE `rule:grants-team-trample` and
   `rule:grants-haste-to-reanimated-creature`: status → active, revival
   history note citing R8 and the hexproof-precedent rationale; membership
   starts at legacy union (both n=0).
2. AUTHOR `rule:activated-regenerate-self` — draft its DET pattern plus
   patterns for the two revived axes above (all three are template-shaped).
   Emit measured hit lists + fixed-seed 20-hit sample sheets to files.
   **STOP for Captain's pattern ratification before any membership from
   these patterns is written** — this session ends with the sheets
   produced, patterns pending; membership lands via a later DET pass run.
3. Kill-note corrections (append-only history entries, R8.4/R8.5):
   sacrifice-self-as-activation-cost and sacrifice-as-additional-cost →
   "duplicate-of-live-axis" (naming the live axis);
   grants-haste-to-token → "duplicate of grants-haste-to-created-tokens".
   Ledger the cost-shape facet children (PARENT-TREE-CANDIDATES.md).
4. R9 synonym additions to the canonicalizer vocabulary (starting
   token→created-tokens), each with a one-line evidence note in the
   report; applied in foundry_consolidate.py's CANONICAL_SYNONYM_MAP.
5. R10 routing table implemented in the killed-slug handler; every routed
   or report-row instance printed as counts + slugs.

## 5. Derived card-index artifact + gamechanger seed (R1)

- `experiments/out/foundry/card_axes_index.json`: oracle_id → {axes:
  [slugs], dfc: bool (card_faces[0].image_uris rule — the locked DFC
  rule, derived fresh from the corpus), gamechanger: bool}. Regenerated
  deterministically; documented as a derived view (never hand-edited,
  never authoritative).
- Seed `tags/gamechangers.yaml` (in git): format spec + empty list for
  Captain to fill; the index reads it if present.

## 6. Integrity, sanity, reporting

- Backup law before mutation; determinism ×2 on the full consolidation
  (byte-identical codebook + artifacts); lint() at the end of every
  mutating step; Gate #0 on any corpus probe.
- Sanity panel: active axis count before/after (delta = instantiated
  nodes + 2 revivals only), membership rows before/after (expect
  ~7,699 → ~23,9xx; print exact), top-10 axes by added members, no-op
  counts, routing/report-row counts.
- Correct the dry-run report file's figures per B-MIGRATION-DISCOVERY.md
  §6 (the deferred correction) and update CORPUS-PASS-PLAN.md step 6 to
  consolidated; RESUME-NOTE.md one line.
- Report per standing format incl. spend $0.00 / cumulative $90.51 /
  headroom $49.49, commit hashes, codebook sha256.

## 7. Standing discipline

Unchanged from the original directive §10: halt loudly on genuine
ambiguity · verify-or-drop · transcript hygiene (quotes in files, never
console) · G1 · G4 · pre-mutation backups · one session, this work item
only. The corroboration wave remains a FUTURE Captain trigger.
