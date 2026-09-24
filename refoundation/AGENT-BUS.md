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

## 5. Who may speak, and fail closed

The repository is public. Anyone can comment, so "is this message well-formed and
current?" is not the same question as "may this person command a Worker".

- The trusted speaker set is **operator configuration, not repository data**: a
  `--trusted` flag, the `MTJ_AGENT_BUS_TRUSTED` variable, or a JSON file outside
  the working tree. A wave executing inside the checkout can edit files in the
  checkout, so a trust list kept there would be one scope escape away from
  rewriting who may command the next wave.
- **Nothing configured means nobody is trusted.** An unconfigured bus reads
  nothing and runs nothing; it says how to configure itself and stops.
- Authority resolution obeys the same rule: only a checkpoint from a trusted
  speaker can be the latest `K`. A checkpoint-shaped comment from anyone else is
  skipped and REPORTED — obeying it would hand over the Worker, and halting on it
  would hand anyone a way to stop the Worker by posting one.

## 6. Nothing runs until the checkout is measured

A brief that says "branch X" is a claim. Before any model invocation the
supervisor asks git, and every answer must agree:

| check | code when it fails |
| --- | --- |
| the working tree is the one configured | BUS_WRONG_WORKTREE |
| the checked-out branch is the one the wave names | BUS_WRONG_BRANCH |
| the wave's base is an ancestor of HEAD | BUS_BASE_NOT_ANCESTOR |
| no uncommitted changes | BUS_UNEXPECTED_DIRT |
| every unit the bus calls done has a commit here | BUS_PROGRESS_HEAD_MISMATCH |

Problems are collected, not short-circuited, and any one of them stops the
dispatch. A repair wave that builds on an unaccepted commit says so with
`candidate_base`; `base` still names the accepted head, so a stale command stays
detectable.

## 7. Every unit is measured after it runs

Scope and trailers are enforced, not requested. After each unit, and before the
next one may start:

| check | code when it fails |
| --- | --- |
| a mutating unit produced a commit | BUS_UNIT_NO_COMMIT |
| every commit carries this wave's and unit's trailers | BUS_UNIT_TRAILER_MISSING |
| nothing changed outside allow_paths, or inside deny_paths | BUS_UNIT_SCOPE_ESCAPE |
| the tree is clean again | BUS_UNIT_UNCOMMITTED |
| a read-only unit changed nothing | BUS_READONLY_UNIT_MUTATED |

A failing unit stops the wave where it stands. Nothing is reverted, reset or
cleaned: a scope escape is evidence, and tidying it away would destroy the only
record of what happened.

## 8. Loop prevention

- An agent acts only on kinds addressed to it, and only when the speaker is
  somebody else, so no agent can ever wake itself.
- `message_id` is the idempotency key. A redelivered message is a no-op that
  records why, not a second execution.
- A wave already claimed by a Worker message is not dispatched again unless a
  human explicitly resumes it.
- A wave may be commanded once. A second command for the same wave is rejected.
- **An abort cancels; it is never queued.** A `WAVE_ABORT` is applied when it is
  read: its wave's command stops being pending, permanently. It is not itself
  Worker work — nothing ever answers an abort, so a queued abort would sit ahead
  of every later command forever. A redelivered or re-issued command cannot
  un-abort its wave, and an abort that arrives before its command still cancels it.
- **Only the newest command is live.** At most one command is pending: the newest
  accepted under the live checkpoint and task, and only while it is neither
  answered nor aborted. Every older command is superseded, so aborting the newest
  one leaves nothing to run rather than reviving the one before it.
- Malformed, stale, unselected, wrong-actor and unsupported-version messages are
  rejected with stable codes and authorize nothing.
- One supervisor pass acts on at most ONE message.

## 9. Cold start — Worker

1. Obey root `CLAUDE.md`. Resolve Issue #1: latest `K` -> active `T`.
2. Declare the trusted speakers. Without them nothing below answers.
3. `python3 -m agent_bus authority` — the same selection, machine-read.
4. `python3 -m agent_bus state` — what is on the bus and what is pending.
5. `python3 -m agent_bus preflight` — what git says about this checkout.
6. `python3 -m agent_bus poll` — the dry run: what would be dispatched, and why.
7. Execute only a wave the live checkpoint selects. Commit per unit with
   trailers. Post one `WAVE_RESULT` at the review boundary.

The durable Worker is `python3 -m agent_bus watch run`, and the macOS service
around it is `watch install|status|start|stop|uninstall`. One instance holds an
exclusive lock outside the repository; every cycle sleeps, successes included;
failures back off exponentially and a quota refusal backs off far longer.

Three things make the installed service honest rather than merely present:

- **It is proven able to run before it is installed.** `watch install` resolves
  every executable the service will need — `git` and `gh` always, `claude` too
  when the service is armed with `--execute` — and writes a PATH DERIVED from
  where they actually are on that machine, plus the launchd defaults. A missing
  one is BUS_EXECUTABLE_NOT_FOUND, raised on the dry run, naming all of them.
  Nothing is hardcoded: the same call on a machine whose tools live elsewhere
  produces that machine's directories.
- **A healthy watcher is visible while it is healthy.** One JSON record per
  cycle is written and flushed as the cycle completes, carrying the timestamp,
  the action, and on failure the code and detail. A log that filled up only when
  the process exited would stay empty for exactly as long as the service worked.
- **A launch failure is a failure, not a crash.** An executable that cannot be
  found or run, a command that hangs, a git command that fails, GitHub being
  unreachable — each becomes a bus failure the loop backs off from
  (BUS_EXECUTABLE_NOT_FOUND, BUS_COMMAND_TIMEOUT, BUS_GIT_FAILED,
  BUS_AUTHORITY_UNRESOLVED). Escaping the loop would hand the restart to
  launchd's KeepAlive, which is a crash loop at full speed with the backoff
  never reached.

## 10. Cold start — Manager

The Manager's wake contract is `refoundation/AGENT-BUS-MANAGER-TRIGGER.md`. The
automated wake is `.github/workflows/agent-bus-manager-wake.yml`: its first job
runs the deterministic pre-gate `python3 -m agent_bus.manager_gate`, and no model
and no model credential is reached unless that gate answers `wake=true`. A
comment it refuses ends with one stable code (BUS_GATE_WRONG_EVENT,
BUS_GATE_WRONG_SURFACE, BUS_GATE_NO_ENVELOPE, BUS_GATE_NOT_FOR_MANAGER,
BUS_GATE_COMMENT_MISMATCH, BUS_GATE_ALREADY_HANDLED, or the ordinary bus code
for an untrusted, malformed, stale or duplicate message).

1. Read Issue #1 and resolve the latest `K` yourself.
2. Read the Worker result on the transport surface, then inspect the live branch
   — commits, diff, tests — before believing any claim in it.
3. Post `WAVE_REVIEW` with `ACCEPT`, `REPAIR` or `CAPTAIN`.
4. Post `V` and `K` on Issue #1. The bus records the verdict; the checkpoint is
   what makes it true.

## 11. Recovery

Every invocation re-derives state from GitHub plus git. There is no resume mode
and no session memory to lose:

- authorized units come from the `WAVE_COMMAND`;
- completed units come from posted progress AND from commit trailers on the
  branch, so a lost comment cannot erase a real commit;
- remaining and blocked units are recomputed, in the same order, every time.

`python3 -m agent_bus resume --wave <id>` prints exactly that arithmetic.

## 12. What the bus may never do

- run for a speaker nobody declared;
- move the accepted head;
- select a successor task (`next` is `NONE` and validation enforces it);
- merge, or move `main`;
- change Foundry semantics, codebook content or scoring constants;
- carry a credential. No message holds one, and the only credential the Manager
  wake uses — the `OPENAI_API_KEY` repository secret — is handed to the pinned
  Codex action alone, after the gate, never to a shell step or an output.
