---
description: Foundry batch triage, EMIT (DET) — parse Captain's annotations, reconcile, assemble next batch
argument-hint: [batch-number]
model: claude-haiku-4-5
---

Batch number: $ARGUMENTS

Read docs/SUP-TRIAGE-PROTOCOL.md, then Captain's annotated
docs/TRIAGE-BATCH-$ARGUMENTS.md. DET-class: mechanical, deterministic.
Continue through all phases — only stop on genuine ambiguity, a failed
gate, or an unspecified decision.

SCOPE GUARD: this command NEVER runs consolidation or enrichment — those
are /triage-alpha's job. If an expected input is missing, HALT and name
it; do not rebuild it. Before doing anything else, print a one-line state
check: which of {review json, enriched json, decisions json, codebook,
ledger doc, batch-N+1 plan} already exist, with timestamps. Skip any step
whose output already exists and is valid — never redo completed work.

BATCH-1 SEAM: batch 1 was ratified via chat before the annotation
convention existed. For $ARGUMENTS = 1 ONLY: decisions/batch-1.json is
the authoritative ratified record; the TRIAGE-BATCH-1.md file has no
annotations by design — skip steps 1–3 and start at step 4 (RECONCILE).

1. PARSE annotations per the protocol convention. HALT LOUDLY on any
   entry that parses to zero or multiple verdicts, any MERGE without
   INTO, any RENAME without TO, or any unfilled `-> RULE:` blank.
   Untouched entries = ratified as proposed.
2. Record the override result: reversals / confident calls, plus
   refinements, into the decisions file's override_spotcheck block.
3. EMIT experiments/out/foundry/decisions/batch-$ARGUMENTS.json
   (schema sup-triage-decisions-v1). Corpus-validate every
   captain-authored example card (paper preferred); HALT on failures.
4. RECONCILE: adapt to foundry_reconcile.py's schema (halt rather than
   lossy-map), run it -> codebook v0.$ARGUMENTS, diff report, both
   convergence metric families per the protocol.
5. LEDGER: append any new ledger candidates to
   docs/KEYWORD-LEDGER-CANDIDATES.md — same commit set as the codebook.
5b. PARENT LEDGER: append any parent/hierarchy rulings or flags from
   Captain's annotations to docs/PARENT-TREE-CANDIDATES.md (ratified
   rulings under "Ratified parent decisions", the rest under "Proposed
   parents") — same commit set. Parents are schema-pass material: record
   them, do not build them.
6. ASSEMBLE batch N+1 per MASTER-HANDOFF §5 with §5.6 targeting:
   thin 2-member KEEPs, batch-flagged confirmation targets, unpromoted
   OTHER clusters, under-covered strata; DET stratified-random fill,
   fixed seed, strata printed, deduped against ALL prior batch cards,
   paper rows preferred. Corpus-validate every hand-picked name.
7. SYNTH PROMPT: apply this batch's batch-feedback section + the standing
   revisions (oracle-text-only quoting; no bare-keyword/reminder axes;
   riders are not axes; two-lane labeling against the new codebook with
   free-labeling of novel patterns explicitly encouraged; ratified
   non-text predicates where they exist).
8. COST: estimate the batch N+1 Batch API cost from CURRENT pricing docs.
   STOP for Captain's go-ahead before any submission.
9. Commit everything above with messages citing the decisions file and
   the SUP-triage protocol. Include any still-untracked loop scripts.
