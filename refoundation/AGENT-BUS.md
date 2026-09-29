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
  **The trusted host makes that commit, never the model** (section 7a).
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
  speaker can be the latest `K`, with one exception, the publisher, below.
  A checkpoint-shaped comment from anyone else is skipped and REPORTED. Obeying
  it would hand over the Worker, and halting on it would hand anyone a way to
  stop the Worker by posting one.
- **A checkpoint is a record that opens its comment.** Only its top-level `h`
  and `a` are read. Checkpoint text quoted in a verdict, or indented under
  another key, is a lookalike: it selects nothing and is reported.
- **The publisher is trusted by role, not as a speaker.** The Manager wake
  workflow posts as `github-actions[bot]`. That identity may write only four
  things:
  - the review of one transaction;
  - that transaction's `V`;
  - its `K`, and the dispositions that `K` owes on Issue #1 (one per other
    Manager-bound message it displaced);
  - the one successor that `K` names: a REPAIR's re-issue, or the next wave of
    the Captain goal plan the accepted wave is bound to.

  Each must be exactly what `agent_bus.transition` derives. Its `K` counts only
  as the exact next link after the `K` before it, so two racing publishers
  cannot both be the latest. It cannot be declared a speaker. The contract is
  `refoundation/AGENT-BUS-MANAGER-TRIGGER.md`.

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
| a mutating unit changed something the host could commit | BUS_UNIT_NO_COMMIT |
| every commit carries this wave's and unit's trailers | BUS_UNIT_TRAILER_MISSING |
| nothing changed outside allow_paths, or inside deny_paths | BUS_UNIT_SCOPE_ESCAPE |
| the tree is clean again | BUS_UNIT_UNCOMMITTED |
| a read-only unit changed nothing | BUS_READONLY_UNIT_MUTATED |

A failing unit stops the wave where it stands. Nothing is reverted, reset or
cleaned: a scope escape is evidence, and tidying it away would destroy the only
record of what happened.

## 7a. The host owns Git; a provider edits and tests

A Worker provider — Claude, Codex, any provider — **edits and tests files only**.
It never commits, pushes, stages, resets, stashes, cleans, checks out, rebases or
otherwise mutates Git metadata. Codex stays in its workspace-write sandbox; no
provider is given a wider one to make Git writable. Provider identity never
changes this law.

After a successful provider response the trusted Agent Bus host
(`agent_bus.finalize`), in this order and no other:

1. extracts the provider's bounded Worker evidence and parses its required
   trailing `mtj-evidence` footer — invalid, missing, ambiguous, oversized or
   footer-less evidence (BUS_WORKER_EVIDENCE_INVALID) creates no commit; a footer
   whose `status` is STOP is BUS_WORKER_STOPPED; after the metadata proof of
   step 2, a footer whose `changed` list is not exactly the measured change set
   is BUS_WORKER_EVIDENCE_MISMATCH, before anything is staged;
2. proves HEAD, the branch, every ref, the local Git config and the index are
   exactly what they were before dispatch — a provider commit, ref move, branch
   change, config change or staging is BUS_PROVIDER_GIT_MUTATION;
3. measures every added, modified and deleted path and proves each is inside
   `allow_paths` and outside `deny_paths` BEFORE staging — otherwise
   BUS_UNIT_SCOPE_ESCAPE, nothing is staged, and the dirty tree stays as evidence;
4. refuses a commit-boundary mutating unit that changed nothing (BUS_UNIT_NO_COMMIT);
5. stages exactly the measured paths, additions and deletions included, and
   creates one commit with a deterministic message ending in the two trailers
   (BUS_HOST_COMMIT_FAILED otherwise);
6. pushes that commit to the commanded branch with ordinary non-force
   fast-forward semantics and re-reads the remote to prove it landed — a
   rejection, a race or a failure is BUS_HOST_PUSH_FAILED;
7. runs the ordinary unit verification of section 7 on the resulting commit and
   requires a clean tree;
8. publishes the durable Worker evidence on Issue #1 (BUS_WORKER_EVIDENCE_POST_FAILED
   when GitHub does not acknowledge it);
9. only then posts `WAVE_PROGRESS`, and a `P` `WAVE_RESULT` only when every unit
   got here.

A read-only unit is never staged or committed. Any failure above stops the wave
before PASS. A failed unit's extractable evidence is still published on Issue #1
before its FAILED progress, marked `"outcome": "F"` with its problem codes, so
the reviewer can read why the Worker stopped; such evidence never satisfies
resume. When nothing could be extracted, the FAILED progress and `F` result are
still posted: they claim the command, so a redelivery never dispatches it again. Host Git commands run with hooks disabled, so nothing a provider
wrote into the checkout runs with the host's credentials.

**Host Git never reads config a provider could write.** Every `git` the bus runs
goes through `agent_bus.shell.Runner` in `host_git_env()`: no system or global
config file, no ambient `GIT_*`, no prompt, and the keys that execute a program
or redirect a remote (`core.fsmonitor`, `core.hooksPath`, `commit.gpgsign`,
`tag.gpgsign`, `protocol.ext.allow`, `credential.helper`) pinned above anything
the repository says. Credentials come only from `gh auth git-credential`. Before any
dispatch the host refuses (BUS_HOST_GIT_UNSAFE) a checkout whose effective config
names any other program git would run — a filter, textconv or merge driver, an
ssh, askpass, gpg or credential program — because a provider could route a path
to it through `.gitattributes` before any scope check. Step 2 also compares local
config read in order with `--includes --show-origin` and the digests of
`info/attributes`, `info/exclude`, `objects/info/alternates` and
`config.worktree`; the push and its re-read use one resolved URL.

**Headless Claude runs least-privileged.** `claude -p` loads no user, project or
local settings file (`--setting-sources ""`), cannot prompt
(`--permission-prompts none`), and runs with only the bus-owned
`HEADLESS_CLAUDE_SETTINGS`: the Bash sandbox must start (`failIfUnavailable`),
the provider's working directory is pinned to the checkout, writes are confined
to it and the temp dir, and Git metadata commands are denied. The operator's interactive
allowlist never reaches a headless provider. Codex keeps its workspace-write
sandbox.

**Headless output is evidence, not a human reply.** In a headless Agent Bus
invocation the provider's final response — Claude's `claude -p` result, Codex's
terminal agent message, any provider's — is captured by the supervisor as
machine-consumed Worker evidence; it is never shown to a human as the reply.
The root `CLAUDE.md` two-word "Claude done" convention governs only direct
interactive sessions and does not apply here. The provider returns a concise,
bounded, substantive final result stating what changed and what validation ran,
and does not post the detailed `X`/result itself: the supervisor publishes the
durable evidence (step 8). The response must end with exactly one fenced
`mtj-evidence` JSON footer and nothing after it: `status` (DONE or STOP),
`changed` (every added, modified or deleted path; the host checks it against Git)
and `validation` (each check run, as `{"command", "exit"}`; required for DONE)
(Captain decision D, Issue #1 comment 5864993788). A response without a valid
footer — "Claude done", "done", "ok" in any punctuation or formatting included —
is BUS_WORKER_EVIDENCE_INVALID, exactly like missing evidence. The whole response
stays under `MAX_EVIDENCE_BYTES`; it is refused, never truncated. The Worker
brief (`agent_bus.transport.worker_brief`) states this rule to every provider.

A completed unit whose Worker evidence was lost is not recovered from Git: a
commit proves scope progress, never a model response, so resume and execute
refuse it (BUS_WORKER_EVIDENCE_INVALID) rather than reconstruct one.

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
7. Execute only a wave the live checkpoint selects. The host commits and pushes
   each unit with trailers (section 7a); the provider only edits and tests. Post
   one `WAVE_RESULT` at the review boundary.

The durable Worker is `python3 -m agent_bus watch run`, and the macOS service
around it is `watch install|status|start|stop|uninstall`. One instance holds an
exclusive lock outside the repository; every cycle sleeps, successes included;
failures back off exponentially and a quota refusal backs off far longer.

Three things make the installed service honest rather than merely present:

- **It is proven able to run before it is installed.** `watch install` resolves
  every executable the service will need — `git` and `gh` always, and when the
  service is armed with `--execute`, the CLI of every enabled provider in the
  provider order it writes into the service's own arguments — and writes a PATH DERIVED from
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

**Local Worker providers.** A unit runs through the operator's own authenticated
CLI: Claude (`claude -p`) or Codex (`codex exec`, workspace-write sandbox). No
repository secret is involved, and neither provider writes Git: the host
finalizes every unit (section 7a). The order is operator configuration, never bus
data: `--providers`, then `MTJ_AGENT_BUS_PROVIDERS`, then a provider file outside
the checkout, then the default `claude,codex`; the supported orders are
`claude,codex`, `codex,claude`, `claude` and `codex`. The authority, preflight,
unit enforcement, progress and result rules above do not depend on which provider
ran. A unit moves to the next provider only after a classified quota or capacity
failure from a structured stdout/stderr shape, when git proves the attempt left
no commit and a clean tree on the same branch, and a live re-read proves the
command is still the selected one. Otherwise it stops: BUS_TRANSPORT_FAILED,
BUS_FAILOVER_REFUSED, or — each provider having run once — BUS_PROVIDERS_EXHAUSTED.
A session is resumed only by the provider that opened it
(BUS_PROVIDER_SESSION_MISMATCH); a malformed order is BUS_PROVIDER_CONFIG_INVALID.
`poll` without `--execute` reports the order and the planned invocation and runs
no provider.

## 10. Cold start — Manager

The Manager's wake contract is `refoundation/AGENT-BUS-MANAGER-TRIGGER.md`. The
automated wake is `.github/workflows/agent-bus-manager-wake.yml`: its first job
runs the deterministic pre-gate `python3 -m agent_bus.manager_gate`, and no model
and no model credential is reached unless that gate answers `wake=true`. A
comment it refuses ends with one stable code:
- BUS_GATE_WRONG_EVENT, BUS_GATE_WRONG_SURFACE, BUS_GATE_NO_ENVELOPE;
- BUS_GATE_NOT_FOR_MANAGER, BUS_GATE_COMMENT_MISMATCH, BUS_GATE_ALREADY_HANDLED;
- BUS_GATE_QUEUED, BUS_WAVE_ABORTED, BUS_WAVE_SUPERSEDED, BUS_TXN_RACE_LOST;
- or the ordinary bus code for an untrusted, malformed, stale or duplicate
  message.

The model returns one decision (`ACCEPT`, `REPAIR` or `CAPTAIN`, with short
bounded text). `python3 -m agent_bus.publisher` builds and posts the
`WAVE_REVIEW`, `V`, `K` and the one successor the `K` names. Before every write
it revalidates everything live, and a rerun resumes the same transaction; a run
that dies after a durable write is finished once, automatically, by the
workflow's no-model `workflow_run` recovery. A Worker `CAPTAIN_REQUIRED` is always
reviewed before a `WAVE_RESULT` under the same `K`, and every other message the
`K` displaces gets a durable disposition rather than going stale unexplained. An
ACCEPT needs independent evidence (`python3 -m agent_bus.goal run-checks`) that
every check the wave's Captain goal plan requires passed on the result head.

**The local cross-review Manager** (Captain decisions E and G, Issue #1 comment
5864993788) runs the same four stages on the operator's machine with no API key
and no `main` change: `python3 -m agent_bus ... watch run --manager` makes every
watcher cycle a Manager pass, then a Worker pass (`agent_bus.local_manager`). The
gate is `manager_gate.decide` over a synthesized comment event. Evidence is the
selftest and the goal plan's checks on the claimed head, run by candidate code
under `sandbox-exec`: no network, no credential files, an empty environment, and
writes confined to a throwaway `--no-hardlinks` clone and a scratch dir (the
operator's ignored `data/` and `experiments/out/` are copied in when
`--operator-state` names them, never through a candidate symlink). The goal
binding, the measured head and the evidence are the host's: held in memory, and
re-proven after the review or nothing is published. The model is the provider
that did NOT produce the wave's Worker evidence. It reads a pristine clone taken
before any candidate code ran, works from a context dir outside it, and is
governed by `CLAUDE.md` and both bus contracts as committed at the accepted head
the latest `K` names (never a working tree: the watcher's checkout is also its
Worker's); the candidate's copies are review material only. It runs against the
decision schema with no write access (`codex exec --sandbox read-only
--output-schema`, or `claude -p --json-schema` with no edit tools, no ambient
settings, and the Bash sandbox denying writes to the whole review workspace).
Every write is `agent_bus.publisher`; nothing is written into the operator
checkout. Worker evidence that names no provider, an unknown one, or more than
one (a failover wave), or a provider order with no other provider, is reviewed
by no model: the host publishes a CAPTAIN decision. An eligible reviewer out of
capacity is a wait, retried next pass (delegated-Manager policy under decision
G): capacity recovers, and CAPTAIN would halt the program. Installing it as a
persistent service is the operator's own step. The local Manager publishes with
the operator's token, so a trusted speaker's record in the publisher's exact form
counts as a publisher record (Captain decision A, Issue #1 comment 5883716054);
a speaker's publisher-form checkpoint is validated as a chain link, never obeyed
as written; exact duplicates count once; and the publisher never posts a body
byte-identical to one already live (incident 5883466222). A stranger's record
counts for nothing.

By hand, the Manager does the same:

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
- let a Worker move the accepted head. Only a `K` moves it: a trusted human's,
  or the publisher's exact ACCEPT transition to an independently tested head;
- let a Worker select a successor (`next` is `NONE` and validation enforces it).
  The publisher selects only the one successor its transition derives — a
  REPAIR's re-issue, or the `next` wave of a Captain goal plan — and never a
  task outside that plan. No model text, Worker result or task prose creates an
  edge;
- merge, or move `main`;
- change Foundry semantics, codebook content or scoring constants;
- carry a credential. No message holds one, and the only credential the Manager
  wake uses — the `OPENAI_API_KEY` repository secret — is handed to the pinned
  Codex action alone, after the gate, never to a shell step or an output.
