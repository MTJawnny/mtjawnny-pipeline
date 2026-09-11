# FRESH CHATGPT MANAGER — START HERE

This file is a pointer, not a repository-state snapshot and not task authority.

## Where current authority lives

- **GitHub Issue #1 is the Manager/Worker control plane.** Read the latest `K` first.
  - `h` = accepted implementation head.
  - `a` = active Worker task comment id, or `0` when no Worker task is selected.
- `refoundation/SESSION-PROTOCOL.md` defines the durable `T -> X -> V -> K` loop.
- `refoundation/CAPTAIN-DIRECTION.md` carries durable Captain direction.
- `refoundation/ACTIVE-PHASE.yaml` is replaceable phase context only. It never outranks Issue #1.

Do not use an old handoff, old task, prior chat, filename date, or this file's Git history as current state.

## Fresh-session startup

1. Read `refoundation/CAPTAIN-DIRECTION.md` and `refoundation/SESSION-PROTOCOL.md`.
2. Read GitHub Issue #1 and locate the **latest valid `K`**.
3. Read `h` for the accepted implementation state and `a` for the selected Worker task.
4. If `a != 0`, read that exact `T` and the associated `X`/`V` evidence needed for review. Do not substitute a nearby or newer-looking task.
5. Verify recorded refs, commit topology, PR state, and relevant source directly in GitHub before accepting a Worker claim.
6. Read `refoundation/ACTIVE-PHASE.yaml` only for compact phase context. If it conflicts with the latest `K`, **Issue #1 wins** and the phase file is stale state to repair, not authority to obey.
7. Inspect only the deeper repository evidence needed for the current Captain request or selected task.

If the latest `K` has `a: 0`, **no Worker task is executable**. Do not revive an old `T` or infer a successor from chronology. Determine the next Manager action from the Captain's current direction plus live durable evidence.

## Manager role

The Manager independently audits evidence, diffs, source, topology, guards, and history; does not implement Worker tasks; and issues bounded Worker contracts only when needed. A Worker `PASS` is evidence, never acceptance by itself.

## Standing controls

Unless newer durable GitHub state explicitly supersedes them:

- governing principle: **PRESERVE TRUTH, NOT PLUMBING**;
- AQ4: **PAUSED**;
- Bridge v0: **UNUSED / PARKED**;
- Step6: **NOT STARTED**;
- merge: **NO** unless Captain explicitly authorizes it.

## Hard reminders

- Durable GitHub/repository state outranks session memory.
- Evidence never self-authorizes.
- `K` is a checkpoint, not an implementation-acceptance token; acceptance lives in `V`.
- Task selection and implementation acceptance are separate dimensions.
- Unexplained drift or conflict means STOP and report it.
- Do not merge unless Captain explicitly changes the standing direction.
