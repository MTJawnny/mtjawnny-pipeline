# S16A Parser-Seam Audit Preflight Plan

Status: **PLANNED / NON-EXECUTING**  
Objective: **3 of 5**  
Fresh Claude session: **REQUIRED**  
Candidate phase: **S16A**  
Implementation authorization: **NONE**

## Mission

Map every live place where the accepted Foundry stack independently interprets Oracle text or Oracle-derived structure, then measure whether those interpretations agree.

The purpose is to find semantic seams before S16A implementation. The result should tell a future Manager which parser responsibilities already have a canonical owner, which are duplicated, which are merely compatibility wrappers, and which materially disagree.

This is a **measurement and ownership audit**, not a refactor.

## Known seed seam

At plan creation, one concrete seam is already documented:

- `src/mtj_foundry/oracle_text.py` uses a depth-aware parenthesis scanner for reminder text;
- `src/mtj_foundry/mtg/shapes/delivery.py` contains a flat reminder regex in its own processing path.

That is an audit seed, not a conclusion that the live corpus is currently wrong. The preflight must measure actual divergence and search for analogous seams elsewhere.

## Scope of interpretation

The audit should include any tracked code that does one or more of the following:

- extracts card faces or full Oracle text;
- normalizes whitespace/case/punctuation;
- strips or interprets reminder text;
- canonicalizes self-reference;
- splits paragraphs, lines, sentences, clauses, bullets, or modes;
- recognizes modal headers or mode lines;
- recognizes die/roll tables, level bands, Class levels, station or other structured blocks;
- distinguishes quoted/granted text from the owning ability;
- classifies delivery: spell / activated / triggered / static / replacement/prevention;
- resolves locality or semantic owner;
- interprets costs or colon boundaries;
- interprets conditions, restrictions, targets, quantities, zones, timing, or linked instructions;
- performs DET preprocessing that changes text/structure before classification;
- creates semantic facts whose correctness depends on text decomposition.

Search permanent package code, remaining legacy `experiments/` code, tests, and command/composition layers. The presence of a permanent implementation does not imply legacy callers no longer run another interpretation.

## Required concept-owner map

Build a table with one row per semantic concept, including at least:

- full-card / face extraction;
- face boundaries;
- paragraph boundaries;
- reminder-parenthesis recognition;
- quotation recognition;
- self-reference normalization;
- ability-line splitting;
- sentence splitting;
- clause splitting;
- modal-header detection;
- modal-bullet detection;
- mode ownership;
- modal selection cardinality;
- die/result-table structure;
- Saga/Class/level/Room/other structural grouping where implemented;
- ability delivery classification;
- target detection/attachment;
- cost/effect boundary;
- conditions and restrictions;
- locality/evidence spans;
- source/destination zone extraction;
- quantity/cardinality extraction;
- granted/quoted ability ownership.

For every concept record:

- every implementing module/function/regex;
- current callers;
- whether one owner is ratified/canonical;
- algorithm shape;
- whether the implementations share a helper or merely resemble each other;
- known historical incidents related to the concept;
- candidate permanent owner;
- current evidence of equivalence or divergence.

## Mechanical duplicate search

Do not rely only on known filenames. Search tracked source for:

- equivalent regex fragments;
- punctuation split patterns;
- direct `oracle_text` access;
- direct `card_faces` access;
- `split("\n")`, sentence-boundary regexes, bullet-prefix tests, colon splitting;
- hand-built reminder stripping;
- self-reference replacement;
- independent modal patterns;
- independent target/cost parsing;
- local copies of constants or CR-template patterns.

Classify each hit as domain interpretation, benign formatting, test fixture, or unrelated.

## Differential measurement

Where two implementations purport to interpret the same concept, compare them over the full accepted corpus or the full mechanically identified relevant population.

For each seam report:

- compared population size;
- equal-result count;
- divergent-result count;
- representative divergent cards;
- whether divergence is expected by contract;
- whether one side is legacy compatibility only;
- whether divergence can alter downstream semantic facts;
- whether the divergence is currently observable in accepted behavior.

Do not fix discrepancies during the audit.

## Historical-evidence reconciliation

Read relevant preserved audits and incident records, especially those concerning:

- full-card information conservation;
- punctuation rescans;
- modal-mode handling;
- locality/ownership;
- CR-class/delivery routing;
- self-reference mistakes;
- cross-face hazards;
- sentence continuation and quoted abilities.

Historical counts must be labeled historical. Re-measure current accepted code rather than carrying counts forward as present truth.

## Severity model

Each seam should receive one planning severity:

- **S0 — canonical single owner**: no meaningful duplicate interpretation found.
- **S1 — duplicate but proven equivalent**: multiple paths exist, equivalence measured and contractually safe for now.
- **S2 — intentional semantic difference**: different interpretations serve different documented purposes.
- **S3 — unproven duplicate**: multiple paths exist but equivalence has not been established.
- **S4 — observed divergence with semantic consequence**: same concept differs and can change facts/ownership/routing.
- **S5 — silent-loss / silent-invention risk**: divergence can preserve a plausible but wrong semantic fact or erase required context.

Severity is evidence classification, not automatic authorization to repair.

## Adversarial checks

For high-risk seams, define a minimal witness and a negative control that would expose an unsafe implementation. Examples:

- nested reminder text versus flat regex;
- punctuation inside quoted abilities;
- question-mark sentence ending;
- semicolon joining independent/dependent clauses;
- modal header with continuation sentence;
- mode bullet using pawprints or cost-before-effect;
- identical phrase on two faces;
- self-reference with legendary subtitle;
- target phrase appearing in one mode but not another;
- colon inside quoted/granted text versus activation colon.

These controls should feed Objective 2’s gold suite where appropriate, but Objective 3 remains an ownership/divergence audit.

## Required deliverables

1. **Semantic concept-owner map**.
2. **Tracked interpreter inventory** — every parser/regex/helper touching Oracle structure.
3. **Duplicate/seam register** with severity.
4. **Full-population differential results** for overlapping implementations where feasible.
5. **Historical incident crosswalk**: old finding -> current measured status.
6. **Canonicalization recommendations** for S16A, clearly marked recommendations rather than law.
7. **Negative-control list** for each S3–S5 seam.
8. **Draft parser-ownership acceptance contract**, NOT AUTHORIZED.

## Non-goals

This preflight must not:

- consolidate parsers;
- replace regexes;
- change Oracle normalization;
- change locality law;
- change delivery classification;
- repair individual cards;
- add card-specific exceptions;
- start S16B retrieval/ranking;
- modify S10–S15 implementation.

## STOP conditions

STOP and report rather than infer if:

- two implementations differ because they intentionally consume different representations and the contract is unclear;
- a current semantic owner is disputed by ratified docs;
- a differential comparison cannot be made without changing source or generated authority state;
- explaining a seam requires a new CR interpretation rather than an engineering ownership decision;
- current accepted head has changed so substantially that this plan’s named seed modules are no longer relevant.

## Completion bar

Objective 3 is complete when a future S16A implementation contract can say, with evidence, which Oracle-interpretation responsibilities must remain, which implementations should become canonical, which duplicates may be retired, and exactly where semantic divergence exists today—without discovering those seams while refactoring them.
