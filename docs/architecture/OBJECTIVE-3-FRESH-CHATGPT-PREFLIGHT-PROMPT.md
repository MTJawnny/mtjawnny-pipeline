# Objective 3 — Fresh ChatGPT Preflight Prompt

Status: DRAFT / READY FOR FRESH CHATGPT SESSION / NON-IMPLEMENTING
Objective: 3 of 5
Subject: S16A parser-seam audit preflight
Implementation authorization: NONE

This prompt is designed for a **fresh ChatGPT Manager-side research session** during the Captain-authorized Claude-unavailable preflight window. Durable GitHub/repository state is authority. This prompt is only a bootstrap map. If live durable state differs, live state wins.

## Roles and standing controls

- Captain = user
- Manager = ChatGPT
- Worker = Claude Code, currently not required for Objectives 1–5 during the Captain-authorized ChatGPT preflight window
- Durable control plane = GitHub Issue #1
- Governing principle = **PRESERVE TRUTH, NOT PLUMBING**
- Expected controls unless superseded: `{AQ4:P, BRIDGE0:U, STEP6:N, MERGE:N}`

Do not implement parser/runtime/package/codebook/authority/AQ4 changes. Do not merge, deploy, publish, advance S10–S15, or authorize S16A implementation.

## Mandatory startup

Use GitHub directly.

1. Read GitHub Issue #1 and identify the latest valid `K`.
2. From that `K`, resolve:
   - accepted implementation head `h`;
   - active Objective-3 task/comment `a`;
   - current planning/evidence branch and head.
3. Read root `CLAUDE.md` at accepted `h` as repository operating law, while applying the Captain's later durable direction that Objectives 1–5 may be executed by ChatGPT during the Claude-unavailable window.
4. Read, from the current Objective-3 planning branch:
   - `docs/architecture/PREFLIGHT-PICK-UP-HERE.md`
   - `docs/architecture/PREFLIGHT-OBJECTIVES-1-5-2026-09-11.md`
   - `docs/architecture/S16A-PARSER-SEAM-AUDIT-PREFLIGHT-PLAN.md`
   - `docs/architecture/OBJECTIVE-3-FRESH-CHATGPT-PREFLIGHT-PROMPT.md`
5. Read the completed Objective-2 evidence package before designing probes:
   - `docs/architecture/preflight/s16a/S16A-OBJECTIVE2-RESULT.md`
   - `docs/architecture/preflight/s16a/S16A-STRUCTURAL-CENSUS.json`
   - `docs/architecture/preflight/s16a/S16A-GOLD-SUITE-DEV.json` and its parts
   - `docs/architecture/preflight/s16a/S16A-NEGATIVE-CONTROLS.json`
   - `docs/architecture/preflight/s16a/S16A-HOLDOUT-PRECOMMIT.json`
6. Read architecture context, without treating it as parser truth:
   - `docs/architecture/CARD-READING-PRECISION-ACCEPTANCE.md`
   - `docs/architecture/S10-CARD-TEXT-OWNERSHIP-DECISION-2026-09-11.md`
7. Independently inspect the exact accepted source code at `h` before accepting any named seam from planning prose as still live.
8. STOP on unexplained durable-state drift or if the task would require source mutation.

## Objective-2 evidence boundary

Objective 2 is completed evidence, not implementation law. Use it as a **measurement substrate and adversarial witness source**, not as a list of parser fixes.

Binding facts to preserve unless live durable state supersedes them:

- pinned raw Oracle corpus: 38,233 unique oracle records;
- Foundry Gate #0 benchmark/product population: **32,557** cards;
- excluded nowhere-legal population: **5,676** cards;
- corpus decompressed SHA-256: `5e47e1325a3987db745a941307080830696cbac2f6aa80d8f88f8a6dad90723c`;
- Objective-2 structural census: 66 families;
- certified CR-700.2 modal population: 748 cards;
- development gold: 33 witnesses;
- deterministic unlabeled holdout: 18 cards;
- negative controls: 18;
- current-parser output was not used to choose Objective-2 benchmark membership or labels.

**Do not reveal, infer, or manufacture holdout labels.** The holdout file may be used only to preserve membership isolation and to prevent accidental development-set contamination. Objective 3 is a parser ownership/divergence audit, not holdout evaluation.

## Mission

Map every live place where the accepted Foundry stack independently interprets Oracle text or Oracle-derived structure, then **measure where those interpretations are equivalent, intentionally different, unproven, or divergent**.

The end product must let a future S16A implementation contract say:

- which parser responsibilities already have a single canonical owner;
- which duplicate implementations are compatibility plumbing;
- which duplicates are independently correct but intentional;
- which duplicates are unproved;
- which implementations materially disagree on the Gate #0 corpus;
- which disagreements can silently lose, invent, detach, or flatten semantic relationships.

This is an audit, not a refactor.

## Audit universe

### Code universe

Mechanically census tracked code at accepted `h`, including:

- `src/mtj_foundry/**`;
- remaining live `experiments/**` parser/semantic paths;
- tests/guards that implement their own interpretation rather than merely asserting expected output;
- command/composition layers that preprocess Oracle material before calling permanent capabilities.

Do not assume a permanent implementation means the legacy route is dead. Prove caller/liveness state.

### Card universe

For card-level differential measurement, use the **32,557-card Gate #0 population**, not all 38,233 raw Scryfall Oracle rows. The 5,676 nowhere-legal records remain available only as historical/synthetic regression inspiration where explicitly appropriate; they do not define live product correctness.

### Objective-2 witnesses

Use the 33 development witnesses and the named negative controls to stress seams after mechanical inventory. Do not let the witness list substitute for full-population discovery or differential measurement.

## Required concept-owner map

At minimum audit these concepts:

1. full-card / face extraction;
2. face boundaries;
3. paragraph boundaries;
4. reminder-parenthesis recognition;
5. quotation recognition;
6. self-reference normalization;
7. ability-line splitting;
8. sentence splitting;
9. clause splitting;
10. modal-header detection;
11. modal-bullet detection;
12. mode ownership;
13. modal selection cardinality / distinctness / repetition / state-memory;
14. die/result-table structure;
15. Saga/Class/level/Room/Station/other structural grouping;
16. ability delivery classification;
17. target detection and target attachment;
18. top-level activation/cost-effect colon boundary;
19. additional/alternative/resolution payment interpretation;
20. conditions and restrictions;
21. linked/reflexive/delayed dependency recognition;
22. locality / semantic owner / evidence span;
23. source/destination zone extraction;
24. quantity/cardinality extraction;
25. quoted/granted ability ownership;
26. DET preprocessing that changes text or structure before classification;
27. any other independently rederived Oracle-text structure discovered mechanically.

For every concept record:

- semantic concept name;
- candidate/current owner;
- every implementing function/class/regex/helper;
- file + stable line/function anchor;
- direct callers and meaningful transitive caller families;
- whether the implementation is permanent, compatibility, test-owned, validator-only, or legacy product path;
- algorithm shape;
- shared-helper relation vs independent derivation;
- applicable Captain/ratified ownership law;
- relevant historical incidents;
- compared population if overlap exists;
- equal/divergent counts;
- representative divergence IDs/names where allowed;
- downstream consequence class;
- severity S0–S5;
- confidence and unresolved contract ambiguity.

## Mechanical interpreter inventory

Do not rely on filenames or the known reminder-text seam. Search tracked source mechanically for at least:

- direct `oracle_text` reads;
- direct `card_faces` reads;
- `split("\n")`, paragraph/line splitting and rejoining;
- sentence-boundary regexes / `.`, `!`, `?`, semicolon logic;
- parenthesis regexes/scanners;
- quote scanners or string-literal punctuation handling;
- self-name replacement / CARDNAME-token logic;
- bullet prefix recognition;
- `choose ...` modal regexes;
- pawprint / Spree / Tiered / die / level / Class / Room / Station recognizers;
- colon splitting and activation-cost detection;
- target regexes / target-boundary helpers;
- zone/action/quantity extraction;
- `if you do`, `when you do`, delayed/linked effect logic;
- local copies of semantic constants or CR-derived pattern sets;
- synthetic DET scan-text builders and modal expansion.

Classify every hit as one of:

- `DOMAIN_INTERPRETER`;
- `COMPATIBILITY_WRAPPER`;
- `VALIDATOR_INTERPRETER`;
- `TEST_FIXTURE_OR_NEGATIVE_CONTROL`;
- `BENIGN_FORMATTING`;
- `UNRELATED`.

The inventory must be broad enough that a later S16A refactor does not discover a second parser by accident.

## Differential measurement law

Where two live implementations purport to interpret the same concept, compare them over the **full relevant Gate #0 population**, or over a mechanically complete relevant subpopulation when the concept does not apply corpus-wide.

For every comparison record:

- population construction rule;
- population size;
- side A / side B exact implementations;
- equal count;
- divergent count;
- categorized divergence signatures;
- representative witnesses chosen after the count is known;
- whether divergence is contractually intentional;
- whether the difference reaches accepted semantic facts, delivery, locality, or downstream routing;
- whether the difference is merely formatting;
- severity S0–S5.

Never call two implementations equivalent because a handful of examples agree.

## Severity model

Use exactly:

- **S0 — canonical single owner**: no meaningful duplicate interpretation found.
- **S1 — duplicate but proven equivalent**: multiple live paths, full applicable differential proves equivalence under the current contract.
- **S2 — intentional semantic difference**: different interpretations serve different documented purposes and the boundary is explicit.
- **S3 — unproven duplicate**: multiple paths exist but equivalence is not established.
- **S4 — observed divergence with semantic consequence**: same concept differs and can change facts/ownership/routing.
- **S5 — silent-loss / silent-invention risk**: divergence can preserve a plausible but wrong semantic fact or erase required context.

Severity is evidence classification. It does not authorize repair.

## Known seeds to verify, not assume

1. **Reminder parsing**: `src/mtj_foundry/oracle_text.py` has a depth-aware parenthesis scanner; prior planning says shapes delivery had a flat reminder regex. Verify whether both are still live at accepted `h`, determine callers, and measure current Gate #0 divergence. Objective 2 measured zero live Gate #0 cards with nested parenthesis depth >= 2, so historical Devoted Mardu must not be presented as a live product failure. It remains a valid synthetic negative control for algorithm robustness.
2. **Card-text ownership seam**: Objective 1/S10 recorded ownership directions for full-card projection, self-reference, modal/roll recognition and delivery consequences. Measure duplicates and behavior; do not treat ownership direction as proof of semantic equivalence.
3. **Modal continuation**: Objective 2 measured 81 Gate #0 modal-header-continuation cards. Use that measured population when comparing modal header recognizers.
4. **Colon/cost parsing**: Objective 2 measured large top-level colon / multi-part-cost candidate populations. Ensure quoted/reminder colons are not silently counted as activation boundaries.
5. **Repeated text/provenance**: Objective 2 measured repeated identical paragraphs and includes Hound Tamer as an adversarial provenance witness. Check whether quote-only or string-only owners can attach semantics to the wrong face/paragraph.

## Historical reconciliation

Read preserved audits/incidents relevant to:

- full-card information conservation;
- punctuation rescan;
- modal handling;
- locality/reversion;
- self-reference regressions;
- CR delivery/class routing;
- face-boundary hazards;
- sentence continuation;
- quoted/granted abilities.

Historical counts are discovery evidence only. Re-measure current accepted `h` and current Gate #0 corpus. For each historical incident, classify it as:

- `CLOSED_AND_GUARDED`;
- `CLOSED_BUT_DUPLICATE_REMAINS`;
- `STILL_OBSERVABLE`;
- `SUPERSEDED_BY_SCOPE`;
- `NOT_REPRODUCIBLE_FROM_CURRENT_EVIDENCE`.

## Adversarial / negative controls

For each S3–S5 seam, define a falsifiable minimal negative control. Prefer Objective-2 witness families where applicable. At minimum consider:

- depth-aware reminder scanner replaced by flat regex;
- punctuation inside quoted/granted ability;
- modal header continuation ignored;
- pawprint / Spree / Tiered row misclassified as ordinary bullet;
- target moved across mode boundary;
- top-level colon confused with quoted/reminder colon;
- condition parent/child attachment swapped;
- source/destination zone swapped;
- repeated identical text attached to wrong face/paragraph;
- runtime self-reference substitution route captured by value rather than resolved live.

A proposed future guard without a demonstrated corruption it would reject is incomplete.

## Required durable deliverables

Create a **new Objective-3 documentation/evidence branch** from the then-current Objective-3 planning head. Do not write Objective-3 measurements into the accepted implementation chain.

Deliver at minimum:

1. `S16A-PARSER-INTERPRETER-INVENTORY` — tracked interpreter inventory;
2. `S16A-PARSER-CONCEPT-OWNER-MAP`;
3. `S16A-PARSER-SEAM-REGISTER` — every duplicate/seam with S0–S5 severity;
4. `S16A-PARSER-DIFFERENTIALS` — full-population/subpopulation comparisons;
5. `S16A-PARSER-HISTORICAL-CROSSWALK`;
6. `S16A-PARSER-NEGATIVE-CONTROLS`;
7. `S16A-PARSER-OWNERSHIP-RECOMMENDATIONS` — explicitly recommendations, not law;
8. `S16A-PARSER-OWNERSHIP-ACCEPTANCE-DRAFT` — **NOT AUTHORIZED**;
9. one human-readable Objective-3 result/guide containing exact heads, corpus identity, method, measured counts, unresolved cases, and next decision boundaries.

Machine-readable JSON is preferred for inventories/registers/differentials where practical; Markdown is appropriate for the synthesized review and recommendations.

## Mutation boundary

Allowed:

- read repository/source/history;
- read and measure the uploaded/pinned corpus if available to the session;
- run private analysis/probes outside repository tracked paths;
- use web research only when external/current evidence materially helps, and distinguish it from repository/CR authority;
- commit documentation/evidence only to a separate Objective-3 preflight branch;
- post durable Manager-side result/checkpoint comments to Issue #1.

Forbidden:

- modify parser/runtime/package source;
- change tests/guards as implementation;
- change codebook/authority/AQ4 state;
- repair discovered seams;
- add card-specific exceptions;
- change S10–S15 migration ordering;
- reveal or create Objective-2 holdout labels;
- merge, deploy, publish, or move accepted implementation refs.

## STOP conditions

STOP and report exact evidence if:

- latest durable `K`/`h` does not select this Objective-3 preflight;
- accepted source head has materially changed and the task has not been re-scoped;
- a seam's two sides consume intentionally different representations but their contract cannot be resolved from durable law;
- a claimed owner conflicts with Captain/ratified authority;
- differential measurement would require source or generated-authority mutation;
- explaining a divergence requires inventing a new CR interpretation;
- the Gate #0 corpus/input identity cannot be established for card-level differential claims;
- an unplanned durable mutation occurs.

Do not guess through a STOP.

## Completion bar

Objective 3 is complete only when a future S16A implementation can be contracted from a measured parser topology rather than intuition: every live Oracle/structure interpreter is inventoried, overlapping implementations are differentially measured where feasible, every meaningful seam is severity-classified, historical defects are reconciled against current behavior, S3–S5 seams have falsifiable negative controls, and canonicalization recommendations are explicit without being mistaken for authorization.

When complete, post one durable Manager-side Objective-3 evidence result to Issue #1. Do not activate Objective 4 unless the Captain or a later Manager explicitly does so.
