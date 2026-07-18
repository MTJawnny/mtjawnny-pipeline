---
description: Foundry batch triage, Session ALPHA (DET) — consolidate, enrich, emit digest
argument-hint: [batch-number]
model: claude-haiku-4-5
---

Batch number: $ARGUMENTS

Read docs/SUP-TRIAGE-PROTOCOL.md and docs/MASTER-HANDOFF.md §6 (vocabulary
+ traps). This is a DET-class session: mechanical scripting only, zero
judgment calls. Continue through all phases — only stop on genuine
ambiguity, a failed gate, or an unspecified decision.

1. If batch $ARGUMENTS SYNTH results are not yet consolidated, run the
   consolidate step (evidence-quote-or-discard gate, exact-token-set
   clustering with the min-2-token floor, per foundry_consolidate.py) and
   emit review/batch-$ARGUMENTS.json.
2. Run experiments/foundry_enrich.py against it (card attachment with
   all-faces oracle text, quote-DF, reminder-restatement flag via the
   engine-replayed reminder set, partial-overlap token groups, discard
   audit). Corpus = tier_engine's jsonl loader (38,233 cards), NOT
   cards.sqlite. Paper rows preferred over A- variants. HALT on any
   unresolvable name.
3. Emit the DIGEST per the protocol's artifact contract:
   experiments/out/foundry/review/digest-batch-$ARGUMENTS.md. Include the
   stats block and anomaly list. Target under ~60KB — truncate quotes,
   never omit axes or token groups with 2+ distinct cards.
4. Gates: determinism x2 (byte-identical) on every generated artifact;
   digest covers 100% of axes and 100% of multi-card token groups.
5. Print a completion summary. Do not commit. Do not run triage judgment —
   that is /triage-beta's job.
