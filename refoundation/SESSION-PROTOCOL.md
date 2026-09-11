# Manager / Worker session protocol

Status: **CURRENT STATIC CONTROL-PLANE RULES**

Purpose: make ChatGPT Manager and coding-Worker sessions disposable. Losing a
session must lose no project truth.

## 1. Core rule

> **No important state may exist only inside a ChatGPT conversation or a coding
> session.**

Anything that matters to later work must become durable in GitHub/repository
state before the session ends.

## 2. State classes

Do not collapse these:

- **STATE** — accepted implementation head plus active-task selection. The latest
  `K` on GitHub Issue #1 is the canonical live state.
- **TASK** — one bounded Manager `T`, pinning base, objective, allow/deny scope,
  validation, STOP conditions and successor authority.
- **RESULT** — one Worker `X`: status, exact mutations, evidence, refs,
  discrepancies and `next`.
- **IMPLEMENTATION** — commit/branch/PR bytes. Never a prose claim alone.
- **REVIEW** — Manager `V`; acceptance or repair is decided here.
- **DECISION** — durable Captain/authorized-human direction.
- **EVIDENCE** — measurements that support a conclusion but never self-authorize.
- **HISTORY** — prior state/provenance that may remain useful without being current.

There is deliberately no tracked mirror of current phase/task state.

## 3. Loop

```text
M:T -> W:X -> M:V -> M:T|K
```

- `T` — Manager issues one bounded task.
- `X` — Worker posts one durable detailed result.
- `V` — Manager independently audits the result.
- `M:T|K` — review may issue a repair task and checkpoint it, or accept and
  checkpoint the resulting state.

**`K` is a CHECKPOINT, not the acceptance arm.** It carries:

- `h` / **accepted_head**
- `a` / **active_task**

Those are independent. A repair commonly keeps `h` unchanged while selecting a
new `a`. The acceptance verdict lives in `V`.

Canonical Worker selector:

`latest K -> active T`

A posted `T` is not executable until selected by the latest `K`.

Captain decisions may enter directly and outrank Manager/Worker state.

## 4. Manager startup

1. Read Issue #1 latest `K`.
2. Resolve `h` and `a`.
3. If reviewing work, read the selected `T`, Worker `X`, prior `V`/`K` only as
   necessary, and inspect the actual commit/PR/source independently.
4. Verify refs and topology against live GitHub.
5. Mutate nothing until current durable state is understood.
6. Issue at most one next task unless Captain directs otherwise.

No bootstrap branch, dated handoff, pickup file, or mirrored phase document is a
startup step.

## 5. Worker startup

Root `CLAUDE.md` is the canonical always-loaded Worker contract.

The Worker:

1. inspects local Git state;
2. reads Issue #1 latest `K`;
3. follows `a` to the selected `T`;
4. verifies base and scope;
5. executes exactly that task.

If `a: 0`, there is no Worker task.

## 6. Session end

A Worker session must not end with completed work only in scrollback.

Before finishing:

- push only authorized branch/PR mutations;
- post one detailed `X` to Issue #1;
- name exact commit/branch/PR refs;
- include validation, conservation and every discrepancy;
- state `next: NONE` unless successor authority already exists.

Normal Claude human-facing completion is exactly:

`Claude done`

The durable `X`, not a chat summary, carries the details.

If a session dies mid-task, Issue #1 plus Git state must reveal what was and was
not completed.

## 7. Manager review discipline

Worker claims are evidence, not acceptance.

Manager review must independently inspect what matters to the task: source,
diff, topology, guards, history and conservation evidence. Broad validation
cannot be replaced with a convenient narrow check when the task contracted the
broad one.

Unexplained drift, scope expansion or conservation failure => STOP/repair, not
silent adaptation.

## 8. Task sizing

Split work at durable verification boundaries:

```text
bounded change -> deterministic validation -> durable result -> review -> next
```

Do not create a giant task merely to save ceremony.

## 9. Drift detection

Tasks pin bases and important input identities.

If expected and measured state differ unexplainedly, **STOP and report the
conflict**. Measurement is evidence, not authority, and it never self-authorizes.

A task that requires a file outside its allowlist is the same kind of event:
STOP rather than widen scope by judgement.

## 10. Capability asymmetry

Manager and Worker environments expose different tools. A party may only claim
inspection it actually performed.

GitHub connectivity, filesystem access, shell access, browser access and
deployment credentials are capabilities granted by the runtime, not by the
language model itself.

## 11. No uncontrolled autonomy

The durable bridge is a control plane, not authorization for an autonomous
self-extending loop:

one task -> one execution -> one durable result -> one review -> explicit next authority.

Merges, deployment/publication and semantic ratification remain explicit human
authority boundaries unless Captain changes them.
