# AGENT BUS v1 — TYPED MANAGER/WORKER TRANSPORT

Status: **CURRENT CONTROL-PLANE RULES (TRANSPORT LAYER)**

Purpose: let the Manager and the Worker exchange durable, machine-readable
commands and results through GitHub, so the Captain decides semantics rather
than carrying messages between two models.

This document governs TRANSPORT. It governs no task, selects no work, and
accepts no implementation.

## 1. Authority is not here

> **GitHub Issue #1 remains the only selector: latest `K` -> active `T`.**

The bus reads that selection and obeys it. Nothing posted on the bus can create
it, move it, or outrank it:

- every message pins the checkpoint and task it was issued under, and a message
  citing a superseded checkpoint is inert;
- every message pins the accepted head as its `base`, and a message pinned to
  anything else is inert;
- a Manager `ACCEPT` verdict on the bus is a **proposal**. The accepted head
  moves when a `K` says it moved, and never because a comment is newer.

A transport surface that could promote itself to authority would be a second
selector wearing a different hat. The state machine refuses it structurally, not
by convention: accepted head is an input to the bus, never an output of it.

## 2. Bounded waves

One selected `T` may authorize a **wave**: several pre-authorized work units.

Each unit declares `id`, `objective`, `depends_on`, `allow_paths`, `validation`
and `mutating`, and may declare `deny_paths`, `negative_controls`,
`stop_conditions`, `commit_boundary` and `concurrency`.

Execution law inside an authorized wave:

- **Finishing a unit is not a STOP condition.** The Worker continues to the next
  runnable unit without asking.
- A unit whose dependency failed is BLOCKED, not attempted.
- Each mutating unit is its own commit, so review and rollback stay per-unit.
- Every unit commit ends with the two trailers that make progress durable:

  ```text
  Agent-Bus-Wave: <wave id>
  Agent-Bus-Unit: <unit id>
  ```

- The Worker STOPs at the wave's **review boundary**, on any declared STOP
  condition, and on the standing STOP rules in root `CLAUDE.md`.

Order is derived, not trusted: dependencies are topologically sorted with ties
broken by declared position, so every machine computes the same sequence.

## 3. Independent review survives

The Worker never accepts its own work. At the review boundary it posts a
`WAVE_RESULT`; the Manager inspects live repository state — commits, diffs,
tests — and answers with `ACCEPT`, `REPAIR` or `CAPTAIN`. What moves the project
is still `V` and then `K` on Issue #1.

Waves change how OFTEN review happens. They do not change WHO reviews.

## 4. Message kinds

| kind | who may speak it | what it does |
| --- | --- | --- |
| WAVE_COMMAND | MANAGER | authorizes one wave; wakes the Worker |
| WAVE_PROGRESS | WORKER | records one unit's outcome; wakes nobody |
| WAVE_RESULT | WORKER | the durable wave result; wakes the Manager |
| WAVE_REVIEW | MANAGER | the verdict on a result; wakes nobody |
| CAPTAIN_REQUIRED | MANAGER, WORKER | a decision only Captain may make |
| WAVE_ABORT | MANAGER, CAPTAIN | cancels a wave; wakes the Worker |

A message lives in one fenced block whose info string is exactly `mtj-bus`, and
its content is JSON. Prose is never parsed. A comment with no such block is
inert — including an "at-claude" mention, a plus-one, or a checkpoint in the
older human YAML form.

## 5. Loop prevention

- An agent acts only on kinds addressed to it, and only when the speaker is
  somebody else, so no agent can ever wake itself.
- `message_id` is the idempotency key. A redelivered message is a no-op that
  records why, not a second execution.
- A wave already claimed by a Worker message is not dispatched again unless a
  human explicitly resumes it.
- A wave may be commanded once. A second command for the same wave is rejected.
- Malformed, stale, unselected, wrong-actor and unsupported-version messages are
  rejected with stable codes and authorize nothing.
- One supervisor pass acts on at most ONE message.

## 6. Cold start — Worker

1. Obey root `CLAUDE.md`. Resolve Issue #1: latest `K` -> active `T`.
2. `python3 -m agent_bus authority` — the same selection, machine-read.
3. `python3 -m agent_bus state` — what is on the bus and what is pending.
4. `python3 -m agent_bus poll` — the dry run: what would be dispatched, and why.
5. Execute only a wave the live checkpoint selects. Commit per unit with
   trailers. Post one `WAVE_RESULT` at the review boundary.

## 7. Cold start — Manager

1. Read Issue #1 and resolve the latest `K` yourself.
2. Read the Worker result on the transport surface, then inspect the live branch
   — commits, diff, tests — before believing any claim in it.
3. Post `WAVE_REVIEW` with `ACCEPT`, `REPAIR` or `CAPTAIN`.
4. Post `V` and `K` on Issue #1. The bus records the verdict; the checkpoint is
   what makes it true.

## 8. Recovery

Every invocation re-derives state from GitHub plus git. There is no resume mode
and no session memory to lose:

- authorized units come from the `WAVE_COMMAND`;
- completed units come from posted progress AND from commit trailers on the
  branch, so a lost comment cannot erase a real commit;
- remaining and blocked units are recomputed, in the same order, every time.

`python3 -m agent_bus resume --wave <id>` prints exactly that arithmetic.

## 9. What the bus may never do

- move the accepted head;
- select a successor task (`next` is `NONE` and validation enforces it);
- merge, or move `main`;
- change Foundry semantics, codebook content or scoring constants;
- carry a credential.
