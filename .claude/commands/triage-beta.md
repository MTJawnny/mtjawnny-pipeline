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
   **EXCEPTION (batch-4 D6, precedent reversal):** cost-shape riders
   (additional-cost-*, alt-cost-*, activation-cost-shape candidates) are
   NOT auto-KILL anymore -- the b2/b3 "cost-shape riders are not axes"
   precedent is overturned; cost-side axes are legitimate wide-net axes.
   Judge them the same as any other candidate on their own merits.
   **STANDING RULE (batch-4 D4):** any `grants-temporary-<keyword>`
   candidate (any keyword) folds into `rule:temporary-keyword-grant` on
   sight -- do not raise it as a question or propose a fresh merge.
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
6a. MEMBER ROSTER section — STRUCTURALLY MANDATORY (batch-5 spec change per
   batch-4 punch list; made mandatory batch-6 D6 after batch-6's first
   draft shipped without it). Every axis, full member card names only (no
   oracle text) — audit membership directly, not just the verdict logic.
   Generate it mechanically (parse the digest / re-derive member lists in
   code, apply every correction from sections 1-3 as code) rather than
   re-typing lists by hand — batch 6 found this catches real duplicate/
   stranded-member bugs the prose verdicts miss. The verification step
   (7) below HALTS if this section is absent; do not treat it as optional
   even when the batch feels routine.
6b. Parent flags: whenever a verdict or note implies a parent/hierarchy
   relationship, APPEND it to docs/PARENT-TREE-CANDIDATES.md under
   "Proposed parents" (one line, cite the batch) — never restructure
   axes around it now; the schema pass ratifies parents.
6c. STANDING RULE (batch-6 D5, remove-and-rehome): every member_removal
   must answer "where does this card actually belong?" — an existing axis
   (member_addition), a convention-consistent new sibling (propose as a
   captain-authored candidate for Captain to rule on), or an explicit "no
   home; ledger-flagged" entry in PARENT-TREE-CANDIDATES.md. Silent
   stranding (removing a card from an axis and never saying where it
   goes) is a protocol violation, not a shortcut.
7. Verify: verdict count == axis count, no duplicates, every MERGE target
   named, MEMBER ROSTER section present and covering every axis (halt and
   fix rather than skip if missing). Then STOP — print the file path and
   tell Captain to annotate per the protocol convention and run
   /triage-emit $ARGUMENTS when done.

Do not commit. Do not emit decisions. Nothing you write is load-bearing
until Captain ratifies.
