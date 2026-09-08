# MANAGER / WORKER SESSION PROTOCOL

Status: **CURRENT CONTROL-PLANE RULES**

Purpose: make ChatGPT and Claude Code sessions disposable, so that losing one
loses no truth.

## 1. Core rule

> **No important state may exist only inside a ChatGPT conversation or a Claude
> Code session.**

A session may reason, investigate, propose or execute a bounded task. The moment
information matters to future work, it must be durable in GitHub/repository
state.

## 2. Durable state classes

Seven kinds, deliberately not collapsed. Confusing them is how evidence gets
promoted to law by accident.

- **STATE** — what is true right now: current phase, active task, controls,
  authority pointers. Lives in `refoundation/ACTIVE-PHASE.yaml`. Replaced, never
  appended.
- **TASK** — what exactly one Worker is authorized to do. A `T` on Issue #1,
  pinning base, objective, allow/deny scope, required validation, STOP
  conditions, delivery form, and successor authorization (normally `NONE`).
- **RESULT** — what happened. An `X` on Issue #1: status `P`/`S`/`F`, exact
  mutations, evidence, refs, discrepancies, decision required.
- **IMPLEMENTATION** — the technical state actually proposed: a commit, branch
  or PR diff. Never a prose claim alone.
- **DECISION** — what Captain (or another explicit authority) decided. Must be
  durable and referenceable, never buried in chat.
- **EVIDENCE** — why a law is believed. Evidence supports authority; it is not
  automatically authority.
- **HISTORY** — what happened before. May be true and useful without being
  current state or current law.

## 3. The loop

```text
M:T -> W:X -> M:V -> M:T|K
```

- `T` — Manager issues one bounded task.
- `X` — Worker posts one durable, detailed result.
- `V` — Manager audits it. **The Worker never self-accepts.**
- `M:T|K` — **the audit branches, and both arms are normal.** `V` may return a
  repair `T` against the unaccepted work, or carry an accept. A repair `T` is
  not a failure of the loop; it is the loop. Nothing may assume `V` accepts.

**`K` is a CHECKPOINT, not the acceptance arm.** It is posted either way and
carries two independent fields: `h`, the **accepted_head**, and `a`, the
**active_task** pointer. A `K` whose `h` is unchanged while `a` selects a repair
`T` is the normal repair path, not an anomaly. **The acceptance verdict lives in
`V`; `K` records where the project stands and what runs next.** Task selection
and implementation acceptance are separate dimensions; never collapse them.

**Canonical Worker selector: latest `K` -> active `T`.** A `T` becomes
executable only once the latest `K` names it as `a`; being posted is not enough.

Captain's decisions enter the loop directly as `D` and outrank all of it.

## 4. Manager startup

1. Read `refoundation/ACTIVE-PHASE.yaml` for current phase.
2. Read Issue #1: the latest `K`, its active `T`, and the `X` under review.
3. Verify recorded refs against live GitHub state.
4. Inspect only the repository evidence that result needs.
5. Mutate nothing until current state is understood.
6. Issue at most one next task unless Captain says otherwise.

Status, hashes and PR numbers are **read from the Worker's `X`** by the Manager
directly. Captain is not a courier and must not be asked to relay them.

## 5. Worker startup

Governed by root `CLAUDE.md`, which is auto-loaded. In short: inspect local
state, read Issue #1's latest `K` -> active `T`, verify the exact base
and scope, execute exactly that one task.

There is no bootstrap-branch read step and no handoff-document read step. Those
are removed, not relocated.

## 6. Worker session end

A Worker session must not end with completed work living only in scrollback.

Before finishing:

- post the detailed `X` to Issue #1;
- push any authorized branch/PR and name the exact commit;
- include validation, conservation and every discrepancy — including ones that
  make the result look worse;
- state `next: NONE` unless a successor was authorized externally.

The human-facing reply is then exactly `Claude done`, and nothing else,
whatever the `X` status is. The detail is already durable; repeating it to the
human is noise, and summarizing it invites a summary to be trusted over the
record.

If the session dies mid-task, Issue #1 plus Git state must be enough for a new
Worker to determine what was and was not completed.

## 7. Task sizing

Split at **durable verification boundaries**, never merely because work is
technical.

```text
bounded change -> deterministic validation -> durable result -> review -> next
```

Not: refactor the engine and hope one long session survives.

## 8. Drift detection

Tasks pin the base commit, and pin state/version or frozen-input identity where
it matters.

If expected state differs from measured state in an unexplained way, **STOP**
and report the mismatch. Do not silently adapt. The point is to convert context
drift from a reasoning hazard into an explicit, visible state mismatch.

A task that cannot be satisfied inside its own declared scope is the same event:
report the exact conflict and return it. Routine is not the same as authorized.

## 9. Capability asymmetry

Different sessions expose different tools. A Manager session doing repository
work needs live GitHub access; one without it may reason about supplied evidence
but must not claim to have inspected live state.

## 10. No uncontrolled autonomy

The GitHub bridge is a control plane, not authorization for an autonomous loop:
one task, one execution, one durable result, one review, Captain decisions when
needed, explicit next authorization. Automation of the loop itself waits until
the state machine is trustworthy.
