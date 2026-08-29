# MANAGER / WORKER SESSION PROTOCOL

Status: **BOOTSTRAP CONTROL-PLANE RULES**

Purpose: prevent session drift by making ChatGPT and Claude Code sessions disposable.

## 1. Core rule

> **No important state may exist only inside a ChatGPT conversation or Claude Code session.**

A session may reason, investigate, propose, or execute a bounded task. Once information matters to future work, it must be represented durably in GitHub/repository state.

## 2. Durable state classes

### STATE
What is true about the project right now?

Examples:
- accepted baseline/ref;
- current phase;
- active task;
- blocked work;
- open Captain decisions;
- current authority pointers.

During bootstrap this is `refoundation/BOOTSTRAP-STATE.yaml`.

### TASK
What is one Worker authorized to do?

GitHub Issue using `mtj-task/1` or successor schema.

A task must state at least:
- exact base;
- objective;
- allow/deny scope;
- invariants;
- required validation/evidence;
- STOP conditions;
- delivery form;
- successor authorization (normally `NONE`).

### RESULT
What happened when the task was executed?

Durable issue/PR comment using `mtj-result/1` or successor schema.

A result should distinguish:
- PASS/COMPLETE;
- STOP;
- FAIL;
- mutations;
- tests/evidence;
- commit/PR refs;
- discrepancies;
- decision required.

### IMPLEMENTATION
What technical state is actually proposed or accepted?

Git commit / branch / PR diff, never a prose claim alone.

### DECISION
What did Captain or another explicitly authorized authority decide?

Must become durable and referenceable. Do not leave important decisions buried only in chats, handoffs, or prose chronology.

### EVIDENCE
Why is a law/decision believed?

Evidence supports authority but is not automatically authority.

### HISTORY
What happened before?

Historical truth may remain useful without being current state or current law.

## 3. Manager startup

A fresh GitHub-enabled ChatGPT Manager should:

1. identify the repository and bootstrap/refoundation branch;
2. read `refoundation/BOOTSTRAP-STATE.yaml`;
3. verify the recorded refs against GitHub;
4. read `refoundation/CAPTAIN-DIRECTION.md`;
5. inspect only the active/pending GitHub issue/result;
6. inspect repository evidence needed to review that specific result;
7. make no mutation until it understands current state;
8. issue at most one next task unless Captain explicitly chooses otherwise.

## 4. Worker startup

A fresh Claude Code Worker should:

1. inspect local Git status before mutation;
2. `git fetch` if needed, without altering the working tree;
3. read the bootstrap state from the remote bootstrap branch if it is not in the current local branch;
4. verify the assigned task's `base` against local/relevant Git state;
5. read exactly one READY GitHub task;
6. read only the subsystem files that task requires;
7. execute within scope;
8. post a durable result;
9. stop unless a successor is separately authorized.

## 5. Worker session end

A Worker session must not end with important completed work only in scrollback.

Before declaring success:
- post the task result to GitHub;
- push any authorized branch/PR;
- include the exact commit/ref;
- include validation and discrepancies;
- state `next: NONE` unless a successor was already authorized externally.

If the session dies mid-task, the durable issue and Git state must be sufficient for a new Worker to determine what was and was not completed.

## 6. Manager session end

Before deliberately moving to a fresh Manager session:
- update durable bootstrap/current state if the accepted project state changed;
- ensure pending review/task refs are explicit;
- do not rely on a final chat summary as the sole handoff;
- leave the next Manager with a deterministic read order.

## 7. Task sizing

Do not split work merely because it is technical.

Split at **durable verification boundaries**.

Preferred shape:

```text
bounded change
→ deterministic validation
→ durable result / commit
→ Manager review
→ next bounded change
```

Avoid:

```text
refactor the entire engine
→ hope one long session survives
```

## 8. Drift detection

Task/state schemas should increasingly pin:
- base commit;
- state/version identifier;
- authority manifest identity where relevant;
- required frozen-input hashes where relevant.

If expected state differs from measured state, STOP rather than silently adapting.

The purpose is to convert context drift from a reasoning hazard into an explicit state mismatch.

## 9. Capability asymmetry

Different ChatGPT conversations may expose different tools. A Manager session intended for repository work must have GitHub access.

A non-GitHub Manager session may reason about supplied evidence but should not pretend to have inspected live repository state.

## 10. No uncontrolled autonomy

The GitHub bridge is not authorization for an autonomous development loop.

Initial model:
- one READY task;
- one Worker execution;
- one durable result;
- one Manager review;
- Captain decisions when needed;
- explicit next authorization.

This can be automated later only after the state machine itself is trustworthy.
