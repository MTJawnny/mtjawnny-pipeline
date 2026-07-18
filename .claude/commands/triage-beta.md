---
description: Foundry batch triage, Session BETA (SUP) — full-pass triage, write the annotation doc
argument-hint: [batch-number]
model: claude-fable-5
---

Batch number: $ARGUMENTS

Read docs/SUP-TRIAGE-PROTOCOL.md fully, then
experiments/out/foundry/review/digest-batch-$ARGUMENTS.md, then the
current codebook (latest version under experiments/out/foundry/). This is
a SUP-class session: judgment is the work. Read EVERY axis and every
multi-card token group in the digest before writing any verdict.

Produce docs/TRIAGE-BATCH-$ARGUMENTS.md per the protocol's artifact
contract. Requirements:

1. Every axis gets exactly one prefilled `VERDICT:` line with a one-line
   reason. Verdict standards from batch 1 (precedent, not suggestion):
   bare-keyword / reminder-text axes -> KILL (Tagger-redundant);
   keyword-mechanism axes -> KILL + ledger-candidates carry-forward;
   procedural riders and templating -> KILL; label-driven grab-bags ->
   KILL with member-reassignment notes; same-concept-different-params ->
   MERGE into one parameterized axis; pure keyword-grant axes ->
   KILL (engine granted_keyword redundancy, ratified Q1);
   judge at SYNTH granularity, parents/parameters are notes for the
   schema pass, not restructures.
2. Check each axis against the codebook: exact-duplicate of an existing
   ratified axis -> MERGE into it; contradiction -> QUESTION.
3. QUESTIONS lane: genuine decisions only, tight either/ors with your
   lean stated, max 8. Everything else is a confident call.
4. OTHER-lane promotions: coherent multi-card families from token groups,
   named members with evidence quotes. Cross-check members exist in the
   digest — never from memory.
5. Override sample: 30 rows, seed = 20260718 + $ARGUMENTS, drawn from
   confident calls only (exclude QUESTIONS), rendered as the protocol
   table. Verify each sampled quote appears verbatim in the attached
   oracle text before including it.
6. Batch-feedback section: concrete SYNTH-prompt revisions for batch
   N+1 derived from this batch's failure patterns.
7. Verify: verdict count == axis count, no duplicates, every MERGE target
   named. Then STOP — print the file path and tell Captain to annotate
   per the protocol convention and run /triage-emit $ARGUMENTS when done.

Do not commit. Do not emit decisions. Nothing you write is load-bearing
until Captain ratifies.
