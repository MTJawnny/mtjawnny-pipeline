# REFOUNDATION BOOTSTRAP CONTROL PLANE

Status: **TEMPORARY BOOTSTRAP ARCHITECTURE**

This directory exists so the MTG Thesaurus / Foundry repository refoundation can survive ChatGPT and Claude Code session resets without reconstructing state from chat transcripts.

It is **not** the final repository architecture. It does not ratify the clean-slate architecture proposed in GitHub Issue #1. It is scaffolding for the refoundation itself.

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
4. GitHub Issue #1 and its Claude result comment
5. Only then inspect deeper repository evidence as needed

### Claude Code Worker

1. `refoundation/BOOTSTRAP-STATE.yaml`
2. `refoundation/CAPTAIN-DIRECTION.md`
3. `refoundation/WORKER-START.md`
4. The single GitHub issue explicitly assigned for execution
5. Only the subsystem files named by that task

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

- `BOOTSTRAP-STATE.yaml` — small current refoundation checkpoint; manually maintained only during bootstrap
- `CAPTAIN-DIRECTION.md` — decisions already made by Captain about refoundation scope and philosophy
- `SESSION-PROTOCOL.md` — session-drift controls and durable Manager/Worker protocol
- `MANAGER-START.md` — cold-start procedure for a fresh GitHub-enabled ChatGPT Manager
- `WORKER-START.md` — cold-start procedure for a fresh Claude Code Worker
- `ROADMAP.md` — high-level refoundation sequence and current stop point

## Authority warning

This directory is **refoundation governance/scaffolding**, not Foundry semantic law.

It must not be used to answer AQ4 C1–C6, mutate the codebook, change authority succession, alter W6, alter locality, or reinterpret frozen benchmark state.

## Current hard stop

AQ4 feature work remains paused after the Adjudicator-A STOP-breach incident record at commit:

`11d63633919146a9be7a5dcdeb55efa0b8dc058d`

Repository refoundation is Priority 0.

No implementation phase of the clean-slate proposal is authorized merely because Issue #1 produced a recommendation.
