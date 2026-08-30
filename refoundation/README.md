# REFOUNDATION BOOTSTRAP CONTROL PLANE

Status: **TEMPORARY BOOTSTRAP ARCHITECTURE**

This directory exists so the MTG Thesaurus / Foundry repository refoundation can survive ChatGPT and Claude Code session resets without reconstructing state from chat transcripts.

It is **not** the final repository architecture. It is scaffolding for the refoundation itself.

## Governing principle

> **PRESERVE TRUTH, NOT PLUMBING.**

The active repository is not a museum. Existing files, APIs, imports, paths, handoffs, and documents may later be rewritten, extracted to a separate research archive, derived from structured data, or deleted if they no longer contribute systematic weight.

Semantic truth and accepted governance state must not change silently as a side effect of infrastructure refactoring.

## Current read order

A fresh Manager or Worker should read only what its role requires.

### ChatGPT Manager

1. `refoundation/BOOTSTRAP-STATE.yaml`
2. `refoundation/CAPTAIN-DIRECTION.md`
3. `refoundation/MANAGER-START.md`
4. GitHub Issue #1 and the latest durable Manager checkpoint/review/task
5. Only then inspect deeper repository evidence as needed

### Claude Code Worker

1. `refoundation/BOOTSTRAP-STATE.yaml`
2. `refoundation/CAPTAIN-DIRECTION.md`
3. `refoundation/WORKER-START.md`
4. The single GitHub issue explicitly assigned for execution
5. Only the subsystem files named or required by that task

These bootstrap read orders are temporary. The permanent target is progressive disclosure through a concise standing map, canonical repository knowledge, scoped/on-demand context, and behavioral cold-start verification.

## Durable control plane

The intended collaboration model is:

```text
Captain
   |
   v
GitHub durable state
   |-- accepted refs / commits
   |-- Issues = task contracts / decisions
   |-- PRs = proposed mutations
   |-- issue / PR comments = results and review
   |
   +--> disposable ChatGPT Manager session
   |
   +--> disposable Claude Code Worker session
```

No important project state should exist only inside one ChatGPT or Claude session.

## What this directory records

- `BOOTSTRAP-STATE.yaml` — small bootstrap checkpoint; older fields may be superseded by later Issue #1 checkpoints
- `CAPTAIN-DIRECTION.md` — early Captain decisions about refoundation scope and philosophy
- `SESSION-PROTOCOL.md` — bootstrap session-drift controls and durable Manager/Worker protocol
- `MANAGER-START.md` — cold-start procedure for a fresh GitHub-enabled ChatGPT Manager during bootstrap/refoundation
- `WORKER-START.md` — cold-start procedure for a fresh Claude Code Worker during bootstrap/refoundation
- `ROADMAP.md` — early high-level refoundation sequence; later Issue #1 checkpoints may supersede its status fields
- `decisions/P0-ARCHITECTURE.yaml` — durable P0 architecture decisions and Manager-accepted direction
- `LLM-NATIVE-REPOSITORY-ARCHITECTURE.md` — detailed researched target for the permanent agent/knowledge/workflow architecture
- `decisions/LLM-NATIVE-REPOSITORY-ARCHITECTURE.yaml` — structured Captain-direction capture for that target

## Permanent agent/knowledge target — read before rebuilding session/knowledge routing

Captain directed on 2026-08-30 that the refoundation incorporate current research on LLM/agent-oriented repository architecture rather than invent a bespoke document-loading protocol.

The durable capture is:

`issue:1#issuecomment-5471746549`

The detailed design is:

`refoundation/LLM-NATIVE-REPOSITORY-ARCHITECTURE.md`

Its core rule is:

> **Make the repository legible to agents, not resident in their context.**

Future work on knowledge migration, `CLAUDE.md`, state/index generation, handoff retirement, Skills/rules, agent tooling, and post-reconstruction workflow acceptance must incorporate that target. In particular:

- canonical project knowledge stays vendor-neutral;
- agent-specific files are thin replaceable adapters;
- default context stays small and high-signal;
- deeper knowledge is loaded progressively/on demand;
- hard invariants use deterministic enforcement where feasible;
- ongoing work persists through Git/plans/tasks/decisions rather than transcript handoffs;
- behavioral fresh-agent evaluations replace a hard read-count proxy as the primary navigability acceptance criterion;
- repository search/LSP/code intelligence precede custom RAG unless measured retrieval failures justify more machinery.

This direction does **not** widen an already-issued Worker task. Integrate it only at separately authorized reconstruction boundaries.

## Authority warning

This directory is **refoundation governance/scaffolding**, not Foundry semantic law.

It must not be used to answer AQ4 C1–C6, mutate the codebook, change authority succession, alter W6, alter locality, or reinterpret frozen benchmark state.

The decision files in this directory likewise do not self-create authority: they record/select decisions with explicit provenance under the ratified selector/decision-record model.

## Current hard stop

AQ4 feature work remains paused after the Adjudicator-A STOP-breach incident boundary unless Captain separately reauthorizes it.

Repository refoundation remains Priority 0.

No future implementation phase is authorized merely because a design document describes it. Worker mutations still require an exact durable task contract and Manager review under the current governance model.
