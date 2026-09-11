# Refoundation control plane

This directory stores **static governance and conservation contracts** for the
MTJawnny Foundry refoundation.

It deliberately does **not** mirror the current migration phase or task. A
tracked “current phase” file became stale while Issue #1 continued moving, which
created two competing answers to the question “what is happening now.” Current
operational state therefore lives only in durable GitHub control-plane state.

## Manager cold start

For a fresh ChatGPT Manager:

1. Read GitHub Issue #1 and locate the **latest `K`**.
2. Read `h` as the accepted implementation head and `a` as the active task
   pointer.
3. If `a != 0`, read that exact `T` and the relevant `X`/`V` chain.
4. Verify refs, PR topology and repository evidence directly before accepting or
   issuing work.
5. Read static governance below only when the question requires it.

Canonical selector:

`latest K -> active T`

There is no bootstrap-branch read, handoff-document read or phase-file read.

## Worker cold start

Claude Code auto-loads root `CLAUDE.md`.

The Worker then reads Issue #1's latest `K`, follows `a` to the selected `T`,
verifies the exact base and scope, executes exactly that one task and posts one
durable `X`.

If `a: 0`, there is no Worker task.

Old batch-triage command shortcuts are not part of the current control plane.
Historical handoff and triage documents under `docs/` are never startup
authority.

## Durable state classes

Keep these classes separate:

- **STATE** — current accepted head and active task selection. Latest `K` on
  Issue #1.
- **TASK** — one bounded Manager `T`.
- **RESULT** — one Worker `X`.
- **REVIEW** — Manager `V`; implementation acceptance lives here.
- **IMPLEMENTATION** — commit/branch/PR bytes.
- **DECISION** — explicit Captain or other authorized durable decision.
- **EVIDENCE** — measurements supporting a conclusion; never self-authority.
- **HISTORY** — prior state useful for provenance but not current routing.

Protocol:

`M:T -> W:X -> M:V -> M:T|K`

`K` is a checkpoint, not an acceptance token. It independently records
`accepted_head` (`h`) and `active_task` (`a`).

## Static governance files

### `CAPTAIN-DIRECTION.md`

Human-level refoundation direction, including:

- **PRESERVE TRUTH, NOT PLUMBING**;
- session disposability;
- aggressive but evidence-safe legacy disposition;
- preservation of semantic/authority truth.

It does not select the current task.

### `SESSION-PROTOCOL.md`

The Manager/Worker state machine and durable-result discipline.

It does not carry current state.

### `decisions/P0-ARCHITECTURE.yaml`

Structured decision/provenance record for the refoundation architecture. It
persists ratified decisions and Manager-accepted direction but mints no authority
by itself.

### `PACKAGE-EXECUTION-CONTRACT.yaml`

Current package/import execution contract and the measured compatibility
bootstrap families. This is technical state, not startup routing.

### `conservation/`

Pinned preservation inputs and conservation contracts. Treat these as
load-bearing evidence/configuration, not prose to simplify casually.

### `path-e/`

Machine-readable Path-E fixtures/input locks still consumed by permanent
runtime/evaluation capabilities. Operator prose for the installed commands is
consolidated in the root `README.md`.

### `BOOTSTRAP-STATE.yaml`

A tiny **SUPERSEDED tombstone retained only because older durable provenance
points at it**. It is not part of Manager or Worker startup and must never carry
current task state.

## What not to read by default

Do not reconstruct current state by scanning chronology.

In particular, do not use old:

- session handoffs;
- master handoffs/addenda;
- pickup documents;
- triage batches/protocols;
- architecture proposals merely because they are large or recent-looking;
- modification times or filename sorting.

Those may be evidence for a specific investigation, but they do not outrank the
latest durable control-plane state.

## Documentation cleanup rule

A stale-looking file is not automatically deletable.

Top-level `docs/*.md` participates in the ratified-rulings deletion gate. Some
obsolete-looking handoffs still carry sole-home ruling IDs. Deleting or moving
those documents requires a conservation pass that proves every unique ruling has
another durable home and regenerates the derived registry/ratchet state.

This rule is why context cleanup should remove **routing authority first** and
semantic/evidence history only after measured disposition.

## Standing controls

Unless explicitly superseded by a newer Captain decision/latest `K`:

- AQ4 is PAUSED.
- Bridge v0 is PARKED_UNUSED.
- Step6 is NOT_STARTED/NO.
- Merge is NO.
- deployment/publication is unauthorized.

Current state must still be verified from Issue #1 rather than inferred from
these defaults.
