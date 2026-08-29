# CAPTAIN DIRECTION — REPOSITORY REFOUNDATION

Status: **ACTIVE REFOUNDATION GOVERNANCE**

This file records decisions already made by Captain in the refoundation discussion. It is not Foundry semantic law and does not answer AQ4 semantic questions.

## 1. Priority

Repository / engine refoundation is now Priority 0.

AQ4 and ordinary Foundry feature work may remain stopped until the repository can reliably stand itself up, identify current authority, and support deterministic cold-start operation.

## 2. Preservation rule

> **PRESERVE TRUTH, NOT PLUMBING.**

The project is not required to preserve accidental implementation shape.

Future refoundation work may, when separately authorized in bounded tasks:

- rewrite entire Python modules;
- replace import structures;
- create a real Python package;
- replace path APIs;
- move configuration;
- rebuild validation and Gate 2;
- rewrite routing and session-start behavior;
- consolidate or replace documentation;
- replace prose-derived registries with structured representations;
- remove compatibility code after migration;
- move generated artifacts;
- delete obsolete active files after their unique systematic value is accounted for.

## 3. What must survive

Infrastructure refactoring must not silently change semantic or governance truth.

Unless separately authorized, preserve:

- selected Foundry authority identity and succession law;
- authoritative codebook content;
- current AQ4 frozen inputs and commitments;
- Captain-ratified semantic decisions;
- incident/governance records needed to understand accepted state;
- benchmark evidence needed to reproduce accepted conclusions;
- product/substrate boundaries already deliberately chosen.

Physical paths, imports, APIs, file names, document formats, and generated-output locations are not sacred.

## 4. Active repository standard

The active repository should contain material that still contributes systematic weight to the system being built.

Legacy artifacts should eventually receive a deliberate disposition such as:

- **KEEP** — current required source/authority;
- **EVIDENCE** — needed provenance for current truth;
- **REWRITE** — underlying truth/concept survives, current representation does not;
- **EXTRACT** — belongs to another system, alternate end-state, or future research line;
- **DERIVE** — should become generated from structured source rather than authored directly;
- **DELETE** — no remaining systematic weight after unique content is accounted for.

The exact final taxonomy remains reviewable; this list captures the intended distinction.

## 5. Alternate end states / other systems

If a file originally created during MTG Thesaurus work now describes a materially different tool, architecture, or end state, it should not remain in the active repository merely because it may contain useful ideas.

Potentially useful alternate ideas should be extracted for later analysis, preferably outside the active repository (for example, a future research/archive repository), so they do not compete with current architecture during retrieval.

## 6. Session architecture

Captain should not be the routine courier between ChatGPT and Claude Code.

GitHub is the preferred durable collaboration plane:

- Issues carry task contracts and decision requests;
- branches/PRs carry proposed technical mutations;
- comments carry structured results and review;
- Git refs and repository files carry accepted durable state.

Neither one ChatGPT conversation nor one Claude Code session should be a source of truth.

## 7. Session-disposability requirement

A fresh authorized Manager or Worker should be able to recover state from durable project resources rather than previous conversation context.

If a fresh Claude session needs the previous Claude transcript to know what to do, the project architecture has failed.

If a fresh ChatGPT Manager needs the previous ChatGPT transcript to know what is accepted, blocked, or active, the project architecture has failed.

## 8. Current non-decision

Claude's P0.1 clean-slate architecture proposal on GitHub Issue #1 is **not automatically ratified** by completion of that task.

A fresh Manager session should review that result, identify the actual Captain decision points, and only then authorize implementation phases.

No migration begins from this file alone.
