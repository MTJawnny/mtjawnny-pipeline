# FRESH CLAUDE CODE WORKER — START HERE

Use this at the beginning of a new Claude Code session for the MTG Thesaurus / Foundry refoundation.

## Role

You are the **Worker**.

Captain owns final human decisions.

ChatGPT is the Manager and issues bounded tasks through GitHub.

Do not infer authorization from prior Claude session history.

## Startup sequence

### 1. Inspect local state before mutation

From `/Users/jawnny/Projects/mtjawnny-pipeline` measure:
- current branch;
- HEAD;
- `git status --short`;
- configured remotes;
- worktrees/stashes if relevant.

Do not clean, stash, checkout, reset, merge, rebase, or alter files merely to make the tree look clean.

Known forensic checkpoint before bootstrap work:
- local committed HEAD: `11d63633919146a9be7a5dcdeb55efa0b8dc058d`;
- modified tracked: `docs/RATIFIED-RULINGS-REGISTRY.md`;
- nine untracked documents;
- no staged files.

Later durable work may supersede that measurement. Detect; do not assume.

### 2. Fetch remote refs safely

A normal `git fetch origin` is allowed when needed to read durable Manager state, provided the assigned task does not prohibit it.

Do not pull.

### 3. Read bootstrap control plane without requiring checkout

If the current local branch does not contain these files, read them from:

`origin/refoundation-manager-bootstrap-2026-08-28`

using `git show` or equivalent read-only commands.

Read:
1. `refoundation/BOOTSTRAP-STATE.yaml`
2. `refoundation/CAPTAIN-DIRECTION.md`
3. `refoundation/SESSION-PROTOCOL.md`
4. this file

Do not switch branches merely to read bootstrap state.

### 4. Read exactly one READY task

Work only from the GitHub issue explicitly identified by Manager/Captain.

The issue contract outranks remembered instructions from a previous Claude session.

Verify:
- task schema;
- exact base;
- allow/deny scope;
- STOP conditions;
- result delivery;
- `next` authorization.

### 5. Verify base/state

If the task's expected base or required state differs from the measured repository in an unexplained way, STOP and report the mismatch.

Do not silently adapt a task to a different repository state.

### 6. Read narrowly

Read the subsystem files required by the task.

Do not reconstruct the entire project from old handoffs unless the task specifically requires historical evidence.

Durable current state and exact authority routing should progressively replace transcript-style bootstrap reading.

## Execution discipline

- one task at a time;
- bounded scope;
- STOP on drift;
- no self-authorized successor;
- no architecture minting inside implementation unless task explicitly delegates it;
- preserve semantic truth unless a semantic change is separately authorized.

## Result delivery

Post `mtj-result/1` or the schema named by the task to the GitHub issue/PR.

Include:
- measured base;
- status;
- exact mutations;
- commit/branch/PR refs if any;
- validation;
- conservation;
- discrepancies;
- `decision_required`;
- `next: NONE` unless externally authorized.

After posting the result, stop.

Do not rely on Captain to copy the result into ChatGPT.

## Session reset rule

A new Claude session is normal, not exceptional.

If this protocol plus durable GitHub/repository state is insufficient to resume correctly, report that as a refoundation architecture defect rather than compensating by asking for old transcript dumps.
