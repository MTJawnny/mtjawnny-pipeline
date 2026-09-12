# Objective 2 — Fresh Claude Code Preflight Prompt

Status: DRAFT / READY FOR FRESH WORKER SESSION / NOT AN ACTIVE T
Objective: 2 of 5
Subject: S16A adversarial card-reading gold-suite preflight
Implementation authorization: NONE

This prompt is deliberately self-routing because recent Claude Code sessions have not always auto-read root `CLAUDE.md`. Do not assume any startup file was loaded automatically.

## Mandatory startup before analysis

1. Explicitly read `docs/architecture/PREFLIGHT-PICK-UP-HERE.md`.
2. Explicitly read root `CLAUDE.md` even if the client claims repository instructions were already loaded.
3. Read GitHub Issue #1 and resolve the latest valid Manager checkpoint `K`.
4. From that `K`, resolve accepted implementation head `h` and active task `a`.
5. Verify Objective 2 has not been superseded or activated under a different contract.
6. Read:
   - `docs/architecture/PREFLIGHT-OBJECTIVES-1-5-2026-09-11.md`
   - `docs/architecture/S16A-ADVERSARIAL-GOLD-SUITE-PREFLIGHT-PLAN.md`
   - `docs/architecture/CARD-READING-PRECISION-ACCEPTANCE.md`
   - `docs/architecture/S10-CARD-TEXT-OWNERSHIP-DECISION-2026-09-11.md` only as architectural context; it MUST NOT define benchmark labels
7. Inspect the exact accepted corpus/input identity available to the accepted implementation. Do not treat planning hashes or historical corpus counts as present truth.
8. STOP on unexplained durable-state drift, missing required source material, or any need to mutate semantic/runtime source.

## Mission

Produce a durable, implementation-independent adversarial benchmark design and populated preflight evidence package for S16A card-reading precision.

The benchmark must test whether Foundry preserves Magic's executable semantic relationships: ownership, delivery, costs, modes, target attachment, conditions, sequencing/dependency, cardinality, zones, actor/chooser scope, and provenance.

It is NOT a test of whether all Oracle characters remain somewhere in memory.

## Independence law — binding for this preflight

The gold truth must be derived from Oracle text + rules authority, not from what the current parser emits.

Before using current parser behavior as evidence:

1. mechanically identify structural populations from raw accepted corpus material or other implementation-neutral input;
2. select and annotate the gold witnesses;
3. record provenance and uncertainty;
4. precommit the labeled benchmark/holdout split and any deterministic sampling seed;
5. only then may current parser output be compared as a later measurement.

Do not choose witnesses because the current parser passes or fails them. Do not modify labels after observing parser performance unless a provenance error in the gold annotation itself is demonstrated and recorded as such.

## Input requirements

Use the then-current accepted corpus identity and record it exactly. Card data must not be committed to git.

If the accepted local corpus needed for a mechanical family census is absent, STOP with the exact missing input and the expected acquisition/identity path. Do not replace the corpus census with card-name handlists or internet anecdotes.

Use source evidence in this order where practical:

1. accepted Oracle corpus;
2. applicable Comprehensive Rules edition;
3. official Wizards card-specific release notes/rulings where necessary;
4. qualified secondary/community sources only if official material is genuinely insufficient.

A community interpretation never silently becomes benchmark truth.

## Required two-pass census method

### Pass A — broad mechanical discovery

Search the accepted corpus directly for candidate structural families without relying on the current semantic parser's classification.

At minimum census the families named in `S16A-ADVERSARIAL-GOLD-SUITE-PREFLIGHT-PLAN.md`, including modal instructions, selection cardinality variants, stateful mode restrictions, nonmodal bullets, die/level/Class/Room/Saga structures, costs, reflexive/linked/delayed triggers, target relations, quantities, zones, quoted/granted abilities, nested reminders, multi-face/component layouts, repeated text, and punctuation-bearing structures.

Record for every family:

- mechanical discovery rule/query;
- population size;
- overlap with other families;
- known false-positive/false-negative risk in the discovery rule;
- whether population enumeration is exhaustive or candidate-generating;
- corpus identity used.

### Pass B — semantic stratification

Within each mechanically discovered population, stratify by materially different rules templates before selecting witnesses. Do not let the biggest lexical template crowd out rare structural variants.

Examples: `choose two` with distinctness, repeatable modes, stateful exclusions, chooser not controller, continuation sentence after modal header, cost-before-effect mode, shared target vs mode-local target.

## Gold witness selection

Start from but do not limit the suite to:

- Cryptic Command
- Zuko, Conflicted
- Monument to Endurance

Independently discover additional cards, including cards not previously named in Issue #1.

For every represented structural family:

- select representative and adversarial witnesses;
- select more than one witness where materially different templates exist;
- include hard negatives/mutation targets where flattening could look plausible;
- record why the witness was selected and what semantic relation it protects.

There is no arbitrary target card count. Coverage of semantic relationship classes and structural subfamilies controls completeness.

## Required machine-readable gold semantics

Design a schema that describes truth without adopting current parser AST field names. Each witness should support, where relevant:

- stable card identity (`oracle_id` or accepted stable identifier);
- human-readable name;
- accepted corpus/version anchor and Oracle-text hash;
- face/component and paragraph/source coordinates;
- structural family tags;
- parent ability identity;
- delivery/rules shape;
- modal group and selection cardinality;
- distinctness/repetition/state-memory rules;
- mode boundaries;
- cost/payment and timing;
- actor/controller/owner/chooser;
- target attachment and sharing/separation;
- conditions/restrictions/durations;
- sequential and dependency edges;
- source/destination zones;
- exact/symbolic quantities;
- provenance spans;
- explicit `must_not_flatten_into` assertions;
- CR/release-note provenance;
- confidence and unresolved ambiguity.

Do not invent a semantic field simply because the current parser exposes one. The schema should express game truth, not implementation shape.

## Mutation-based negative controls

Define falsifiable corruptions linked to real witnesses. At minimum cover:

- delete cost while retaining payload;
- `choose two` -> `choose one`;
- delete distinct-mode restriction;
- delete repeat-mode permission;
- delete stateful `hasn't been chosen` restriction;
- move a target between modes;
- flatten modes into cumulative instructions;
- split linked/reflexive effects;
- merge independent effects;
- move condition parent <-> child;
- change source/destination zone;
- change resolution payment into casting/activation cost or reverse;
- delete continuation sentence;
- delete a face/component;
- corrupt punctuation inside quoted/granted ability;
- flatten nested reminder parentheses.

For each negative control state exactly which semantic invariant must detect the corruption. A negative control without a named detection property is incomplete.

## Holdout design

Where the measured populations permit it, reserve a holdout subset BEFORE S16A parser implementation sees labels.

Record:

- deterministic selection method;
- seed if randomness is used;
- family stratification constraints;
- visible-development vs holdout membership;
- what metadata, if any, may be visible without exposing labels.

Do not create a holdout that removes the only known witness for a rare structural family from the development acceptance set.

## Historical evidence reconciliation

Read preserved historical audits relevant to full-card conservation, punctuation, modal handling, locality, self-reference, face boundaries, and quoted/granted abilities.

Historical counts are historical evidence only. Re-measure current accepted corpus populations. Use old incidents to design adversarial witnesses and negative controls, not to substitute old measurements for current ones.

## Required durable deliverables

Produce, on a documentation/evidence branch separate from accepted implementation:

1. structural-family census with method + measured populations;
2. machine-readable gold-suite manifest/schema;
3. human-readable benchmark guide;
4. negative-control catalog;
5. semantic relationship coverage matrix;
6. unsupported/unrepresented shape register;
7. provenance register;
8. precommitted holdout record where feasible;
9. draft S16A benchmark acceptance contract marked NOT AUTHORIZED;
10. exact list of files/sources inspected and exact accepted head/input identities.

Post one durable Worker result to Issue #1 when and only when an active Manager task authorizes this preflight. Worker PASS is evidence, not permission to implement S16A.

## Explicit non-goals

Do not:

- modify parser/runtime/package source;
- repair current parser failures;
- tune current parser;
- change `oracle_text.py`, shapes delivery/locality, DET, codebook, authority, or migration state;
- implement S16A;
- implement S16B similarity;
- change S10–S15 ordering;
- commit card corpus bytes;
- convert community strategy opinion into Oracle-derived truth;
- merge or publish anything.

## STOP conditions

STOP rather than guess if:

- latest durable `K` or accepted `h` conflicts with the assumptions above;
- no accepted corpus is available for mechanical census;
- benchmark truth would require unsupported card-name handlisting as the primary population mechanism;
- Oracle/CR/official sources materially conflict and cannot be resolved by authority;
- a label cannot be supported without interpretive guessing;
- completing the task requires parser/source mutation;
- the benchmark cannot be kept independent from current/future parser behavior.

## Completion bar

Objective 2 is complete only when a future S16A implementation can be judged against a precommitted, provenance-bearing benchmark that was selected independently of implementation performance, spans the measured structural families of the accepted corpus, contains falsifiable semantic corruptions, and either represents a shape precisely or explicitly records that the shape is not yet supportable.
