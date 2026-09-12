# S16A Parser-Seam Audit Preflight Plan

Status: **READY / NON-IMPLEMENTING**  
Objective: **3 of 5**  
Fresh ChatGPT session: **REQUIRED FOR CURRENT CAPTAIN WINDOW**  
Candidate phase: **S16A**  
Implementation authorization: **NONE**

## Mission

Map every live place where the accepted Foundry stack independently interprets Oracle text or Oracle-derived structure, then measure whether those interpretations agree.

The purpose is to find semantic seams before S16A implementation. The result should tell a future Manager which parser responsibilities already have a canonical owner, which are duplicated, which are compatibility wrappers, which are intentionally different, which are merely unproven, and which materially disagree.

This is a **measurement and ownership audit, not a refactor**.

## Execution context

The original five-objective plan expected a fresh Claude Code session. The Captain later superseded that executor assumption for the current Claude-unavailable window: Objective 3 is to be executed by a **fresh ChatGPT Manager-side research session** under the same non-implementation boundaries.

Fresh-session bootstrap:

`docs/architecture/OBJECTIVE-3-FRESH-CHATGPT-PREFLIGHT-PROMPT.md`

Live GitHub/repository state remains authority. The prompt and this plan are routing/specification artifacts only.

## Objective-2 dependency and boundary

Objective 2 is complete evidence and is an input to this audit.

Read the package under:

`docs/architecture/preflight/s16a/`

especially:

- `S16A-OBJECTIVE2-RESULT.md`
- `S16A-STRUCTURAL-CENSUS.json`
- `S16A-GOLD-SUITE-DEV.json` and its parts
- `S16A-NEGATIVE-CONTROLS.json`
- `S16A-HOLDOUT-PRECOMMIT.json`

Expected Objective-2 anchors, subject to live durable verification:

- raw pinned corpus: 38,233 unique oracle records;
- Foundry Gate #0 product/benchmark universe: **32,557** cards;
- excluded nowhere-legal population: **5,676**;
- decompressed corpus SHA-256: `5e47e1325a3987db745a941307080830696cbac2f6aa80d8f88f8a6dad90723c`;
- 66 measured structural families;
- 33 development gold witnesses;
- 18-card deterministic **unlabeled** holdout;
- 18 negative controls.

Use Objective-2 development witnesses and structural populations to stress parser seams **after** mechanical interpreter discovery. Do not let the witness list replace full-source census or full-population differentials.

The holdout must remain unlabeled. Objective 3 may preserve membership isolation and avoid accidental contamination, but it must not infer, create, or reveal holdout labels.

## Card-level measurement universe

Use the **32,557-card Gate #0 population** for present-tense product/benchmark differential claims. Do not use all 38,233 raw Oracle rows as the primary denominator.

Nowhere-legal/playtest/event/prototype-style records may be referenced only as historical/synthetic regression evidence where explicitly useful. They must not redefine live product correctness.

## Known seed seam

At plan creation, one concrete seam was documented:

- `src/mtj_foundry/oracle_text.py` uses a depth-aware parenthesis scanner for reminder text;
- prior accepted code/planning reported a flat reminder regex in `src/mtj_foundry/mtg/shapes/delivery.py`.

This is a **seed to verify**, not a present-tense conclusion. The fresh session must independently confirm whether both paths are live at accepted head `h`, identify callers, and measure actual divergence.

Objective 2 measured **zero Gate #0 cards with nested parenthesis depth >= 2**. Therefore historical Devoted Mardu must not be presented as a live Gate #0 product failure. It remains useful as a synthetic algorithmic negative control.

## Scope of interpretation

Audit tracked code that does one or more of the following:

- extracts card faces or full Oracle text;
- normalizes whitespace/case/punctuation;
- strips or interprets reminder text;
- canonicalizes self-reference;
- splits paragraphs, lines, sentences, clauses, bullets, or modes;
- recognizes modal headers or mode lines;
- recognizes pawprint, Spree, Tiered, die/roll, Saga, Class, level, Room, Station, or other structured blocks;
- distinguishes quoted/granted text from owning text;
- classifies delivery: spell / activated / triggered / static / replacement/prevention;
- resolves locality or semantic owner;
- interprets costs, payments, or colon boundaries;
- interprets conditions, restrictions, targets, quantities, zones, timing, linked/reflexive/delayed instructions;
- performs DET preprocessing that changes text/structure before classification;
- creates semantic facts whose correctness depends on text decomposition.

Search permanent package code, remaining live legacy `experiments/` code, tests/guards that independently interpret source material, and command/composition layers. A permanent implementation does not prove a legacy interpretation is dead; caller/liveness state must be measured.

## Required concept-owner map

Build one row per semantic concept, including at minimum:

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
17. target detection/attachment;
18. cost/effect boundary;
19. additional/alternative/resolution payment interpretation;
20. conditions and restrictions;
21. linked/reflexive/delayed dependency recognition;
22. locality/evidence spans;
23. source/destination zone extraction;
24. quantity/cardinality extraction;
25. granted/quoted ability ownership;
26. DET text/structure preprocessing;
27. additional independently rederived Oracle structure discovered mechanically.

For every concept record:

- every implementing module/function/regex/helper;
- current direct callers and meaningful caller families;
- permanent/legacy/compatibility/test-owned/validator status;
- whether one owner is Captain-approved or ratified;
- algorithm shape;
- whether implementations share a helper or independently derive the same concept;
- historical incidents relevant to the concept;
- candidate permanent owner;
- current evidence of equivalence/divergence;
- compared population and count where overlap exists;
- downstream semantic consequence;
- severity S0–S5;
- confidence / unresolved contract ambiguity.

## Mechanical interpreter inventory

Do not rely only on known filenames. Mechanically search tracked source for at least:

- direct `oracle_text` access;
- direct `card_faces` access;
- `split("\n")`, newline/paragraph decomposition and reassembly;
- sentence-boundary regexes and `.`, `!`, `?`, semicolon logic;
- parenthesis regexes/scanners;
- quote scanners;
- self-reference replacement / CARDNAME-token logic;
- bullet recognition;
- independent modal patterns;
- pawprint / Spree / Tiered / roll / die / level / Class / Room / Station recognizers;
- colon splitting / activation boundary code;
- independent target/cost parsing;
- condition/dependency parsing (`if you do`, `when you do`, delayed/linked structures);
- zone/action/quantity extraction;
- local copies of constants or CR-template patterns;
- synthetic DET scan-text/modal expansion builders.

Classify hits as:

- `DOMAIN_INTERPRETER`;
- `COMPATIBILITY_WRAPPER`;
- `VALIDATOR_INTERPRETER`;
- `TEST_FIXTURE_OR_NEGATIVE_CONTROL`;
- `BENIGN_FORMATTING`;
- `UNRELATED`.

The inventory must be broad enough that future S16A implementation does not discover another parser by accident.

## Differential measurement

Where two live implementations purport to interpret the same concept, compare them over the **full applicable Gate #0 population** or a mechanically complete relevant subpopulation.

For each seam report:

- mechanical population construction rule;
- population size;
- exact implementations compared;
- equal-result count;
- divergent-result count;
- divergence signatures/categories;
- representative cards selected only after measuring the divergence population;
- whether divergence is expected by contract;
- whether one path is compatibility only;
- whether difference can alter semantic facts, ownership, delivery, locality, routing, or provenance;
- whether divergence is merely formatting;
- severity S0–S5.

Do not infer equivalence from a small fixture set when the full applicable population can be measured.

## Historical-evidence reconciliation

Read preserved audits/incidents relevant to:

- full-card information conservation;
- punctuation rescans;
- modal handling;
- locality/ownership;
- CR-class/delivery routing;
- self-reference mistakes;
- cross-face hazards;
- sentence continuation;
- quoted/granted abilities.

Historical counts are historical evidence only. Re-measure current accepted code and Gate #0 corpus.

For each historical finding classify current status as:

- `CLOSED_AND_GUARDED`;
- `CLOSED_BUT_DUPLICATE_REMAINS`;
- `STILL_OBSERVABLE`;
- `SUPERSEDED_BY_SCOPE`;
- `NOT_REPRODUCIBLE_FROM_CURRENT_EVIDENCE`.

## Severity model

Use exactly:

- **S0 — canonical single owner**: no meaningful duplicate interpretation found.
- **S1 — duplicate but proven equivalent**: multiple live paths exist; full applicable differential proves current contract equivalence.
- **S2 — intentional semantic difference**: different interpretations serve different documented purposes and the boundary is explicit.
- **S3 — unproven duplicate**: multiple paths exist but equivalence is not established.
- **S4 — observed divergence with semantic consequence**: same concept differs and can change facts/ownership/routing.
- **S5 — silent-loss / silent-invention risk**: divergence can preserve a plausible but wrong semantic fact or erase required context.

Severity is evidence classification, not permission to repair.

## Adversarial checks

For every S3–S5 seam, define a minimal falsifiable negative control. Use Objective-2 development witnesses where applicable, but do not restrict discovery to them.

At minimum consider:

- nested reminder text versus flat regex;
- punctuation inside quoted/granted ability;
- question-mark / exclamation / semicolon sentence boundaries;
- modal header with continuation sentence;
- pawprint, Spree, or Tiered option structure;
- target attachment across mode boundaries;
- identical phrase on different faces/paragraphs;
- self-reference with legendary subtitle/shortened name;
- top-level activation colon versus colon inside quoted/reminder text;
- parent/child condition attachment;
- zone direction swap;
- call-time self-reference substitution accidentally captured by value.

A proposed future guard that has not been shown capable of rejecting a corresponding corruption is incomplete.

## Required deliverables

Produce on a separate Objective-3 documentation/evidence branch:

1. **Tracked interpreter inventory**;
2. **Semantic concept-owner map**;
3. **Duplicate/seam register** with S0–S5 severity;
4. **Full-population/subpopulation differential results**;
5. **Historical incident crosswalk**;
6. **Negative-control catalog** for S3–S5 seams;
7. **Canonicalization/ownership recommendations** for S16A, explicitly recommendations rather than law;
8. **Draft parser-ownership acceptance contract**, clearly NOT AUTHORIZED;
9. **Human-readable Objective-3 result/guide** with exact heads, corpus identity, method, measurements, unresolved cases, and decision boundaries.

Machine-readable JSON is preferred for inventories/registers/differentials where practical. Markdown is appropriate for synthesis/recommendations.

## Non-goals

This preflight must not:

- consolidate parsers;
- replace regexes;
- change Oracle normalization;
- change locality law;
- change delivery classification;
- repair individual cards;
- add card-specific exceptions;
- reveal or manufacture Objective-2 holdout labels;
- start S16B retrieval/ranking;
- modify S10–S15 implementation;
- merge, deploy, publish, or move accepted implementation refs.

## STOP conditions

STOP and report rather than infer if:

- latest durable `K`/`h` does not select this Objective-3 preflight;
- accepted implementation head changes materially enough that the contract needs re-scoping;
- two implementations differ because they intentionally consume different representations and durable contracts do not resolve the boundary;
- a current semantic owner is disputed by Captain/ratified authority;
- a differential comparison cannot be made without changing source or generated authority state;
- explaining a seam requires a new CR interpretation rather than an engineering ownership decision;
- required Gate #0 corpus/input identity cannot be established for card-level differential claims;
- any unplanned durable mutation is discovered.

## Completion bar

Objective 3 is complete when a future S16A implementation contract can state, with evidence, which Oracle-interpretation responsibilities must remain, which implementations should become canonical, which duplicates may be retired, which divergences are intentional, and exactly where semantic divergence exists today—without discovering those seams while refactoring them.
