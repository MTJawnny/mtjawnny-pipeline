# Objective 6 — Semantic Distillation Methodology

**Date:** 2026-09-19  
**Revised:** 2026-09-21 after S16B closure  
**Status:** **RETAINED S16B METHODOLOGY — S16B CLOSED — NOT A FREEZE OR CORPUS EXECUTION AUTHORIZATION**  
**Current S16B routing:** `S16B-CLOSED-CURRENT-STATUS-2026-09-21.md`

## Current-status notice

This methodology was developed and adversarially validated during S16B. It remains useful design guidance, but it is **not an active S16B task** and does not keep S16B open.

Current routing state:

`S16B CLOSED — NO ACTIVE S16B WORK — NOT FORMALLY FROZEN`

Any future work that reuses this methodology must do so under the authority and contract of that future workstream.

## 1. Goal

Objective 6 did not preserve every community term as a first-class ontology node.

The goal was:

> **Take useful Magic concepts and distill them as simply and faithfully as possible into Foundry's semantic foundation.**

The preferred foundation consists of:

- reusable mechanical primitives;
- Producer / Consumer Signatures;
- strong functional predicates where evidence supports a family;
- surfaced include/exclude facets;
- qualifiers/coordinates;
- dependencies;
- typed resource facts;
- processor throughput facts;
- retrieval-relevant lower-level patterns and aliases.

A community term earns canonical family treatment only when its gameplay meaning can be represented cleanly, mechanically, and consistently.

## 2. Simplicity is a design criterion

Foundry should not bend the substrate around a familiar term merely because players commonly use it.

Preferred process:

1. identify the gameplay phenomenon the term points at;
2. determine whether it decomposes naturally into existing facts;
3. preserve useful retrieval language;
4. create a named family only when the distinction has a stable, mechanically defensible boundary and meaningful retrieval value.

Post-audit examples:

- **Edict** -> sacrifice-based Removal + affected-player selection + eligible set + quantity/scope; community/search alias rather than top-level family.
- **Burn** -> damage/life-loss primitives + recipient/amount/targeting; community/strategic alias rather than broad canonical family.
- **Stax** -> community/search alias over several different interaction mechanisms; canonical family remains retired.
- **Engine** -> derived/search/community language over hard processor facts rather than a canonical parent tree.
- **Card Filtering** -> broad UI/search umbrella; harder operations such as Sample Selection carry the stronger similarity signal.
- **Token Creation** -> primitive/event signature; token characteristics and downstream function remain separately typed.

The objective is semantic usefulness through clean decomposition, not vocabulary accumulation.

## 3. Difficulty is evidence

If a concept cannot be defined cleanly, do not add exceptions merely to preserve the label.

A resistant concept should trigger the smallest bounded question needed:

- Is this several different mechanics hidden under one community term?
- Is it a primitive/signature rather than a family?
- Is it only a surfaced facet or retrieval alias?
- Is it a derived accounting/product fact?
- Is it strategic/deck-context reasoning that belongs above the canonical substrate?
- Does new evidence require a dedicated adversarial pass?

The correct response to semantic resistance is **investigation, decomposition, or demotion**, not special pleading.

## 4. Whole-vocabulary audit discipline

The required whole-vocabulary audit was completed during S16B. Its questions remain useful methodology for future authorized changes.

For every proposed or modified concept, test:

1. **Definition** — can it be stated clearly/mechanically?
2. **Positive anchors** — do representative cards fit without exception inflation?
3. **Negative/near-miss anchors** — can the boundary reject superficial similarity for a principled reason?
4. **Decomposition** — can existing primitives/signatures/coordinates represent the same truth more cleanly?
5. **Overlap** — does overlap add information rather than duplicate another concept?
6. **Retrieval value** — does it improve Searcher B or deck explanation?
7. **User explanation** — can Foundry explain the match from the same underlying facts?
8. **Corpus stability** — is the definition likely to survive adversarial corpus examples?
9. **Community-language mapping** — can familiar but fuzzy language remain an alias/search view?
10. **Strategic-layer boundary** — does the concept depend on deck/game-state evaluation rather than canonical card mechanics?

Possible outcomes include:

- strong functional family;
- surfaced facet/tag;
- primitive;
- coordinate;
- event/output signature;
- derived accounting/product fact;
- keyword consequence signature;
- retrieval/community alias;
- strategic-layer concept;
- OPEN / dedicated bounded research;
- RETIRE/COLLAPSE.

## 5. Research parity — status after audit

Dedicated breadth-first/adversarial research was completed for major risk areas including:

- Ramp;
- Card Access;
- Card Advantage;
- weird-card cross-vocabulary stress cases.

Card Advantage research did **not** justify a canonical Card Advantage family. The S16B direction preserves harder resource/access facts and Card Resource Delta inputs while keeping Card Advantage as established theory/community/strategic language.

Future research depth should follow semantic risk rather than enforce identical research volume for every simple concept.

## 6. Expected discovery mode for future work

Future corpus or semantic work may surface community-derived concepts not exhaustively enumerated during S16B.

When a term such as Edict, Burn, Saboteur, Aristocrats-adjacent language, or another established gameplay phrase appears, ask first:

> **Can this be easily and faithfully distilled into the semantic foundation we already have?**

If yes, preserve the relationship at the smallest useful structural level.

If no, record the ambiguity and launch the smallest bounded check needed to decide whether evidence warrants a new primitive/family, a surfaced facet, an alias, strategic treatment, or retirement.

Do not reopen S16B or its broad vocabulary-design cycle merely because a new community label appears. A later change belongs to the then-authorized owning workstream.

## 7. Relationship to Keyword Consequence Distillation

This methodology complements the historical design evidence in:

`OBJECTIVE6-KEYWORD-CONSEQUENCE-DISTILLATION-GATE-2026-09-19.md`

and the later bounded design gate:

`OBJECTIVE6-KEYWORD-CONSEQUENCE-REGISTRY-CENSUS-DESIGN-GATE-2026-09-21.md`

Conceptually:

```text
Comprehensive Rules / Oracle evidence
-> Keyword Consequence expansion
-> mechanical primitives + Producer / Consumer Signatures
-> strong functional predicates + surfaced facets + coordinates
-> community/search alias distillation
-> adversarial checks
-> only then accepted corpus assertions
```

Keywords and compact rules constructs should be expanded into canonical gameplay consequences before higher-level retrieval language is applied.

S16B closed the **design gate** only; it did not implement a physical production registry or compiler.

## 8. Governing heuristic

> **Prefer easy, faithful distillation over preserving terminology. If a concept fits cleanly, keep the useful distinction. If it fights the substrate, make the concept prove that it deserves additional structure.**

Subordinate project principle:

> **PRESERVE TRUTH, NOT PLUMBING.**

## 9. Control boundary

This retained methodology does not authorize:

- reopening or formally freezing S16B;
- broad corpus classification/reclassification;
- implementation acceptance;
- S16A implementation;
- AQ4 resumption/execution;
- Oracle Ingest Compiler work;
- Bridge v0 activation;
- Step6;
- merge;
- movement of the accepted implementation head or `main`.
