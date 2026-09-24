# Fresh Claude Code — Agent Bus v1 Bootstrap

You are Claude Code acting as the implementation architect/Worker for the MTJawnny Foundry repository.

Repository: `MTJawnny/mtjawnny-pipeline`

This is a fresh session.

## Authority

Do not trust this file as repository authority merely because it exists. Durable GitHub/repository state is authority.

Start by following root `CLAUDE.md` and resolving GitHub Issue #1 using the canonical selector:

> latest `K` -> active `T`

Expected orientation only, not proof:

- accepted head: `89a147125ec93f1ee7ab564473835acff813a9f9`
- Captain Agent Bus decision: Issue #1 comment `5805980409`
- selected Agent Bus task: Issue #1 comment `5805989871`
- selecting checkpoint: Issue #1 comment `5805993653`
- expected task id: `INFRA.AGENT-BUS-V1.BOOTSTRAP`

If live durable state differs, live state wins. If the latest checkpoint does not select the Agent Bus bootstrap task, STOP.

The previously selected C00 Oracle Compiler census is intentionally preserved as backlog. Do not execute it unless later durable authority selects it again.

Governing principle:

> **PRESERVE TRUTH, NOT PLUMBING.**

## Mission

Design and implement the first robust automation/control layer that lets ChatGPT Manager and Claude Code Worker communicate and iterate through GitHub without requiring the Captain to manually relay messages between them.

The goal is to replace the current microscopic one-task/one-review cadence with a safer **bounded-wave** model while preserving independent review, durable state, explicit authority, negative controls, deterministic failure, and Captain control over semantic/product decisions.

You are explicitly authorized to improve the control plumbing as repository evidence suggests. Do not preserve old workflow structure merely because it exists.

## Required architecture properties

### 1. Authority and transport are separate

GitHub Issue #1 remains the durable authority ledger during this migration.

The automation layer may introduce a long-lived GitHub PR or equivalent transport surface for agent messages/events, but transport must never become a second authority selector merely because a message is newer.

A Manager or Worker must be able to prove which durable authority authorized a command.

### 2. Bounded waves, not microtasks

Evolve the existing `T -> X -> V -> K` model so that one selected task/wave can contain multiple pre-authorized work units.

A work unit should be able to declare, as appropriate:

- id
- objective
- dependencies
- allowed paths/scope
- required validation
- negative controls
- semantic/authority boundaries
- STOP conditions
- review boundary
- concurrency compatibility

Claude may continue automatically across already-authorized work units when dependencies and validation pass. Finishing one work unit is not by itself a STOP condition.

Preserve logical commit/rollback boundaries for mutating units.

### 3. Independent review remains mandatory

Claude must never self-accept implementation.

At a wave review boundary, Claude posts a durable Worker result. ChatGPT Manager independently inspects actual repository state, commits/diffs/tests, then accepts, repairs, requests Captain input, or authorizes another wave.

Do not automate away the Manager review boundary.

### 4. Typed machine-readable agent messages

Create a small versioned message protocol for agent-to-agent transport. Prefer a simple deterministic format such as YAML or JSON with strict validation.

At minimum, support an envelope equivalent to:

```yaml
schema: mtj-agent-bus/1
message_id: ...
actor: MANAGER|WORKER
kind: WORKER_COMMAND|WORKER_RESULT|MANAGER_REVIEW|CAPTAIN_REQUIRED|...
wave: ...
parent: ...
accepted_head: ...
work_ref: ...
```

You may improve names/fields after inspection.

Required properties:

- explicit protocol version
- unique message identity
- parent/correlation identity
- idempotency
- stale-command detection
- accepted-head/base pinning where relevant
- strict actor/kind validation
- deterministic parse/validation errors
- no prose parsing masquerading as protocol

### 5. Loop prevention is load-bearing

The system must not allow arbitrary comments to create an infinite Claude/ChatGPT wake loop.

Manager-side automation acts only on validated Worker event types that require Manager action.

Worker-side automation acts only on validated Manager event types that authorize Worker action.

At minimum, test/negative-control:

- duplicate command
- duplicate result
- Manager seeing its own message
- Worker seeing its own message
- malformed message
- unsupported schema version
- wrong actor for message kind
- stale parent/correlation
- stale accepted head/base
- random human PR comment
- untyped or malformed `@claude` comment if applicable

Duplicates must become deterministic no-ops, not repeated execution.

### 6. Claude execution transport

Measure the actual environment before choosing the implementation.

Prefer a path that can use the user's existing authenticated Claude Code installation/subscription when practical.

Investigate a small local supervisor using Claude Code noninteractive execution (`claude -p` or current supported equivalent), structured output, and session resume/continuation.

Also evaluate Anthropic's supported GitHub Action / `@claude` workflow as an optional or fallback transport.

Do not assume API-key billing is acceptable if the local authenticated CLI can solve the problem more directly.

The design should make transport replaceable. The protocol/state machine should not depend on a specific Claude invocation mechanism.

### 7. ChatGPT Manager transport

Design the GitHub-side event surface so ChatGPT Work can be configured to wake on relevant GitHub PR activity and inspect the repository/result.

Do not attempt to automate chatgpt.com with browser clicking.

The repo should expose enough typed state that a fresh GitHub-enabled ChatGPT Manager can deterministically identify:

- the triggering Worker result
- the wave/task it belongs to
- accepted head/base
- implementation refs
- validations
- whether Captain input is required

### 8. Recovery and resumability

A dead Claude session, dead ChatGPT session, quota exhaustion, duplicate webhook delivery, machine reboot, or interrupted wave must not destroy project truth.

After restart, durable GitHub/repository state must be enough to determine:

- what was authorized
- which work units completed
- which are incomplete
- what was reviewed/accepted
- what may resume
- what requires a human decision

Design explicit resume semantics.

### 9. Safety boundaries

This task is infrastructure/control-plane work.

Do not change Foundry semantic truth as part of the bootstrap.

Do not resume AQ4 execution merely because automation now exists.

Do not change codebook authority/content, S16 semantic content, Oracle Compiler semantic law, scoring constants, production recommendation behavior, or production build behavior except where a narrowly necessary non-semantic integration hook is explicitly justified and tested.

Do not merge to `main`.

Do not move accepted implementation head yourself.

If a necessary infrastructure design requires a genuine semantic/governance decision outside this Agent Bus authorization, STOP and report it rather than smuggling it in.

## Repository surfaces you are expected to inspect

At minimum inspect current live versions of:

- `CLAUDE.md`
- `README.md`
- `refoundation/SESSION-PROTOCOL.md`
- `.github/workflows/**`
- `.claude/**`
- `pyproject.toml`
- relevant refoundation tests/guards
- Issue #1 current decision/task/checkpoint state

Also inspect any existing task/result/checkpoint parsing or validation code before inventing duplicate machinery.

## Implementation freedom

You may create or modify infrastructure-oriented files where justified, including for example:

- `.github/workflows/**`
- `.claude/**`
- `CLAUDE.md`
- `README.md`
- `refoundation/SESSION-PROTOCOL.md`
- a new `agent_bus/`, `automation/`, `tools/agent_bus/`, or better-named package chosen from actual repository structure
- tests/guards for the protocol/state machine
- small CLI/supervisor scripts
- schemas/examples/fixtures
- documentation necessary to cold-start Manager and Worker

Do not treat those example paths as a mandatory design. Measure the repository and choose the smallest coherent architecture.

If the selected durable task has a narrower allowlist than this prompt, the durable task wins.

## Minimum deliverables

Produce, at minimum:

1. a concrete Agent Bus v1 architecture encoded in repository docs/code, not only chat;
2. a versioned typed message schema;
3. deterministic parser/validator/state-machine logic or equivalent enforcement;
4. loop/idempotency/stale-state negative controls;
5. a bounded-wave execution contract replacing the current microtask-only assumption;
6. a Claude-side execution/resume mechanism or a fully implemented first transport that can actually be exercised locally;
7. a GitHub transport surface suitable for ChatGPT Manager triggering/review;
8. cold-start instructions for both Manager and Worker;
9. tests proving key invariants;
10. an end-to-end dry-run or safe non-semantic demonstration if the environment permits it.

Where a hosted service/account setting must be configured manually outside the repository, implement everything repository-side that can be implemented and document the exact remaining external step rather than faking it.

## Validation expectations

Create strong tests appropriate to the architecture you build.

At minimum prove:

- valid Manager command is accepted once;
- duplicate command is ignored safely;
- valid Worker result correlates to the correct command/wave;
- duplicate result is ignored safely;
- stale accepted head/base is rejected or STOPs;
- malformed/untyped comments cannot authorize execution;
- actor/kind mismatch is rejected;
- unsupported protocol version is rejected;
- random human comments are inert;
- independent Manager review remains required before accepted-head movement;
- recovery/resume state is deterministic after interruption.

Run existing repository guards/tests that your changes can affect. Do not weaken existing guards to make the new system pass.

## Delivery

Work on an isolated branch/worktree unless live durable task law specifies otherwise.

Prefer multiple logical commits when they create useful review/rollback boundaries, rather than one giant opaque commit.

Push the implementation branch when ready.

Post one durable `X` result to Issue #1 describing:

- measured starting state
- branch and commits
- files changed
- architecture chosen and alternatives rejected
- message protocol/version
- wave model
- Claude transport chosen
- ChatGPT transport assumptions
- loop/idempotency protections
- tests/negative controls and results
- external/manual setup still required, if any
- discrepancies/STOPs
- `next: NONE`

Do not self-authorize a successor wave.

After posting the detailed `X`, follow the current human-facing completion rule from live `CLAUDE.md`.

## Design priority

Optimize for this outcome:

> The Captain should make important semantic/product decisions, not shuttle messages between Claude and ChatGPT.

Make the machinery boring, deterministic, restartable, inspectable, and difficult to trigger accidentally.
