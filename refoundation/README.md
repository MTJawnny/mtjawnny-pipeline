# REFOUNDATION BOOTSTRAP CONTROL PLANE

Status: **TEMPORARY BOOTSTRAP ARCHITECTURE**

This directory exists so the MTG Thesaurus / Foundry repository refoundation can survive ChatGPT and Claude Code session resets without reconstructing state from chat transcripts.

It is **not** the final repository architecture. It is scaffolding for the refoundation itself.

## Governing principle

> **PRESERVE TRUTH, NOT PLUMBING.**

The active repository is not a museum. Existing files, APIs, imports, paths, handoffs, and documents may later be rewritten, extracted to a separate research archive, derived from structured data, or deleted if they no longer contribute systematic weight.

Semantic truth and accepted governance state must not change silently as a side effect of infrastructure refactoring.

Two permanent-target consequences now accompany that principle:

> **Make the repository legible to agents, not resident in their context.**

and

> **Rebuild permanent Foundry from explicit capability contracts and preserved truth, not by reproducing the legacy module graph.**

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

These bootstrap read orders are temporary. The permanent target is progressive disclosure through a concise standing map, canonical repository knowledge, scoped/on-demand context, explicit subsystem contracts, and behavioral cold-start verification.

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
- `BEHAVIORAL-REIMPLEMENTATION-STRATEGY.md` — detailed method for reconstructing permanent executable capabilities from contracts rather than mechanically packaging the legacy tree
- `decisions/BEHAVIORAL-REIMPLEMENTATION.yaml` — structured Captain-direction capture for the behavioral reconstruction method

## Permanent agent/knowledge target — read before rebuilding session/knowledge routing

Captain directed on 2026-08-30 that the refoundation incorporate current research on LLM/agent-oriented repository architecture rather than invent a bespoke document-loading protocol.

Durable capture:

`issue:1#issuecomment-5471746549`

Detailed design:

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

## Permanent executable reconstruction method — read before migrating legacy package layers

Captain further directed on 2026-08-30 that the refoundation must not treat the historical Python module graph as the architecture to preserve.

Durable capture:

`issue:1#issuecomment-5471882570`

Detailed strategy:

`refoundation/BEHAVIORAL-REIMPLEMENTATION-STRATEGY.md`

Its core rule is:

> **Legacy code is evidence and, where valid, an executable behavior oracle. The unit of reconstruction is the capability contract, not the old file.**

Every meaningful legacy executable subsystem must eventually receive an explicit implementation disposition:

- **MOVE_ADAPT** — the existing boundary is already good enough to deserve retention;
- **CLEAN_REIMPLEMENT_FROM_CONTRACT** — valuable behavior is entangled with accidental architecture;
- **EXTRACT_EVIDENCE** — lasting value is primarily research/migration/provenance rather than runtime code;
- **DELETE_AFTER_ACCOUNTING** — no unique systematic value remains after behavior/evidence/tests/provenance are accounted for.

Important consequences:

- do **not** aim for a one-for-one `experiments/*.py -> src/mtj_foundry/*.py` migration;
- do not use “preserve the spirit” as a substitute for an explicit behavior contract;
- classify legacy behavior before using it as an oracle: accepted behavior, representative behavior, known defect, obsolete workflow, or unresolved;
- clean reimplementation requires differential/conservation proof at the correct equivalence level;
- known defects must not be reproduced merely to make legacy/new comparison green;
- negative controls must prove the comparison harness can detect a defining regression;
- compatibility facades are allowed during cutover but must carry deletion prerequisites;
- retirement requires runtime, behavior, evidence, authority, validation and history accounting.

### C8 Step-5 interpretation

C8 Step 5 now means:

> **establish the permanent package/execution substrate and reconstruct executable capabilities using the correct per-subsystem method.**

It does **not** mean:

> **mechanically move every legacy Python module into `mtj_foundry`.**

The C8.5D transition study reinforced this distinction. It selected a package import/execution contract as the immediate enabling cut because both MOVE_ADAPT and CLEAN_REIMPLEMENT need a stable package environment. After that foundation lands, the Manager must not automatically move the next leaf module; it should disposition the candidate based on its actual behavior boundary and architectural quality.

## How the two permanent-target documents fit together

The LLM-native architecture answers:

> **How should humans and agents find the correct project knowledge and work safely without loading project history?**

The behavioral-reimplementation strategy answers:

> **How should the permanent executable system be reconstructed without either preserving accidental legacy structure or losing hard-earned behavior?**

Together they define the post-bootstrap destination:

```text
canonical truth / decisions / evidence
              |
              +--> concise agent routing + Skills/rules
              |
              v
      explicit subsystem contracts
              |
              +--> legacy evidence/oracles
              |
              v
       clean mtj_foundry capabilities
              |
              +--> differential + permanent tests
              |
              v
     old runtime plumbing retired safely
```

## Authority warning

This directory is **refoundation governance/scaffolding**, not Foundry semantic law.

It must not be used to answer AQ4 C1–C6, mutate the codebook, change authority succession, alter W6, alter locality, or reinterpret frozen benchmark state.

The decision files in this directory likewise do not self-create authority: they record/select decisions with explicit provenance under the ratified selector/decision-record model.

## Current hard stop

AQ4 feature work remains paused after the Adjudicator-A STOP-breach incident boundary unless Captain separately reauthorizes it.

Repository refoundation remains Priority 0.

No future implementation phase is authorized merely because a design document describes it. Worker mutations still require an exact durable task contract and Manager review under the current governance model.
