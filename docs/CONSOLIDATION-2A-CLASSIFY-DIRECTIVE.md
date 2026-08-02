# CONSOLIDATION-2A-CLASSIFY-DIRECTIVE — the decisions, alone (session 2a of 5)

ZERO MUTATION, ZERO API SPEND. This session computes and writes ONE
artifact — every consolidation DECISION, and nothing mechanical — then
STOPS. Nothing touches codebook.json or grammars.json.

Governed by B-MIGRATION-DISCOVERY.md §10 (A1–A15) and §9 where unamended.
Supersedes, with CONSOLIDATION-2B-ENUMERATE-DIRECTIVE.md, the single-session
CONSOLIDATION-PLAN-DIRECTIVE.md.

**Why this session exists separately.** The full plan enumerates ~18,346
rows at ~425 B each — ~7.8 MB, ~1.95M tokens — because every row carries an
A1 assertion with a quote. That cannot be externally audited at all, at any
sampling rate that would mean anything. The decisions inside it are ~1,000
rows, ~350 KB, ~88K tokens, and CAN be audited whole. So the judgment is
extracted, audited, and frozen FIRST; the mechanical expansion happens once,
afterwards, against an approved decision set. An adverse audit finding then
invalidates a small artifact instead of a 7.8 MB one.

PRECONDITION (verify in the state-check, else HALT): session 1 complete —
codebook.json schema `foundry-codebook/2`, lint clean, independent verifier
clean. Record the live codebook sha256 in the artifact; 2b and session 3
both check against it.

## 1. Inputs

corpus_pass_run1_parsed_final.json · corpus_pass_run1_discovery.json ·
corpus_pass_run1_consolidation_dry_run.json (reference only — recompute,
never trust) · the det_synth check artifact · docs/grammars.json ·
validate_slug.py · the /2 codebook (READ-ONLY, via
foundry_codebook.load_codebook) · gated corpus.

## 2. Build `experiments/out/foundry/corpus_pass_run1_classification.json`

Schema `foundry-consolidation-classification/1`. Deterministic (×2
byte-identical). Records input hashes and the live codebook sha256. Every
decision is enumerated by slug and, where it is a per-card decision, by
oracle_id. No aggregates without their underlying lists.

1. **node_classification** — the 95 grammar virtual-node candidates
   (AG-COUNT-01), each classified into the closed vocabulary:
   `instantiate` / `join-existing` / `redirect` / `report-only` /
   `collision-killed` / `collision-renamed`. Category totals must sum to
   exactly 95. Expected per A14/R7: 93 instantiate; `rule:grants-haste` →
   redirect-per-D4 (Zidane, Tantalus Thief → `rule:temporary-keyword-grant`);
   `rule:draw-second-card-trigger-token` → report-only. Deviations from that
   expectation are allowed but must be stated and justified in the human
   summary — the expectation is a prior, not a gate.

2. **killed_slug_routing** — the `foundry-killed-slug-routing/1` artifact
   (A14/H-02/R10). Every killed-, merged-, or renamed-slug hit enumerated
   with a closed action — `redirect` / `split` / `report` / `discovery` /
   `reject` — and explicit targets. M8-violating combo labels list their
   per-class split targets. NO runtime predicates: no "if the quote fits",
   no similarity thresholds. Every instance is decided HERE, by name.

3. **promotions** —
   - R5: the 141 exact-match free-lane reinventions, split into the 45 new
     members and the 96 already-member merges, each row listed.
   - A15: the 213 rows, EACH re-validated through `validate_slug` exactly as
     a grammar-lane label would be. Rows that fail validation fall back to
     discovery and are listed as such with the failure reason.
     `original_lane` / `effective_lane` recorded per row. The
     `<state>`-placeholder cluster's 10 rows are report-only.

4. **taxonomy_items** — each stated as the EXACT history-entry text 2b will
   emit: revivals entering `deferred` per A2 (never active-at-n=0), the two
   kill-note corrections (R8.4, R8.5), the whole-slug alias per A6
   (`rule:grants-haste-to-token` → `rule:grants-haste-to-created-tokens`;
   NOT a global token→created-tokens synonym, which would corrupt 28 active
   slugs).

5. **same_run_duplicates** — the measured intra-run duplicate emissions
   (run 1: 35 codebook-lane + 3 grammar-lane + 6 free-lane) enumerated by
   (slug, oracle_id), each RESOLVED here per the Captain-ratified collapse
   rule: same-run emissions collapse to a single assertion; lane precedence
   `codebook` > `codebook-grammar` > free-promoted; quote tie-break = first
   in deterministic parse order. Record the winning lane and quote for each.
   This category exists so 2b performs a LOOKUP, never a policy decision —
   it is the one genuine judgment that would otherwise hide inside 2b's
   "mechanical" expansion. Also enumerate any cross-lane same-run pair
   arising from A15 canonical-form promotion (raw-label overlap measured 0;
   canonical-form overlap has never been computed — compute it).

6. **expected_counts** — the closed-loop contract with 2b. Per category:
   how many member_additions, how many assertion_merges, how many new axes,
   how many rows of each promotion type, how many report rows. 2b's
   expansion must reproduce these EXACTLY or halt. This is what makes an
   audit of 2a alone meaningful: a 2b expander bug is otherwise precisely
   the thing an external reviewer of 2a cannot see.

7. **report_rows** — everything deferred to Captain's eyes, with counts and
   the reason each is deferred.

8. **human_summary** — a Captain-readable section INSIDE the artifact:
   category totals, the full 95-node classification table, notable rows, and
   any deviation from the priors in item 1. This section plus the
   enumerations is what the external reviewer reads.

## 3. Reporting and stop

Print counts and slugs only. Quotes go to the artifact, never to console
(A14). Commit the generator script; the artifact itself is gitignored output
— record its sha256 in the report.

Then STOP. In order:

1. Captain reviews the artifact.
2. **A12 EXTERNAL RE-AUDIT CHECKPOINT.** Assemble
   `docs/B-CONSOLIDATION-REAUDIT-PACKET.md`: the amended schema
   (B-MIGRATION-DISCOVERY.md §10 A1) + this artifact's `human_summary` +
   the FULL enumeration of items 1–5 (they fit — that is the point of this
   split) + `expected_counts` + the same red-team charge and disclosure the
   first packet carried. Captain runs it past a DIFFERENT MODEL FAMILY.
   A same-family check does not discharge this.
3. Session 2b runs only on Captain's explicit go, naming the classification
   artifact's sha256 it approves.

Spend $0.00 / cumulative $90.51 / headroom $49.49.

## 4. Standing discipline

Zero mutation of codebook.json/grammars.json under any circumstance · halt
loudly · verify-or-drop · transcript hygiene (quotes to files only) · G1 ·
G4 · determinism ×2 on the artifact · one session, this work item only.
