# Agent Bus v1 — local Worker provider failover (PF1)

Wave `INFRA.AGENT-BUS-V1.WORKER-PROVIDER-FAILOVER.R1`, unit PF1. Authority: Issue #1
checkpoint 5836695353 → task 5836674938, implementing Captain decision 5828305800.
Base (accepted head) `81978221a8119a6faeaf0873d4aecb94bd833d63`.

PF1 adds the provider-neutral execution layer as a library: `agent_bus/providers.py`.
It does **not** wire that layer into the supervisor, CLI, watcher or launchd
discovery; that is PF2. Until PF2, a supervisor with no injected transport still
runs the Claude-only `LocalClaudeTransport`, unchanged.

## The interface

A provider is three things, and the bus depends on nothing else about it:

| part | Claude | Codex |
|---|---|---|
| invocation | `claude -p … --output-format json --permission-mode acceptEdits` | `codex exec --json --sandbox workspace-write --cd <repo>` |
| classification | `classify_claude` | `classify_codex` |
| session namespace | UUID5 in the pre-existing namespace; resumable by id | thread id Codex assigned, read from its own `thread.started` event |

Both use the operator's already-authenticated local CLI. No repository secret,
API key, PAT or GitHub App is created, read or required.

`ProviderFailoverTransport` has the same `dispatch` signature as every other
transport, so the supervisor's preflight, per-unit git enforcement, progress and
result publication apply unchanged to whichever provider did the unit.

## When a unit moves to the next provider

Only when **all** of the following hold, checked in this order:

1. The provider exited non-zero **and** its output carries a classified capacity
   shape:
   * Claude: stdout is exactly one JSON `result` object with `is_error: true`
     and either `api_error_status` 429/529, a result that is exactly the CLI's
     `Claude AI usage limit reached|<epoch>` marker, or a result or stderr line
     `API Error: 429|529 {json}` whose typed error is `rate_limit_error` /
     `overloaded_error`.
   * Codex: a JSONL `error` or `turn.failed` event (stdout or stderr) whose
     message starts with one of the CLI's fixed capacity messages (usage limit,
     quota exceeded, retry limit at 429, model at capacity).
2. A fresh git measurement shows HEAD, branch and working tree exactly as they
   were before the attempt, and the tree clean (it must also have been clean
   before).
3. A live re-read of Issue #1 and the transport shows the same checkpoint, the
   same task, the same accepted head, and the wave neither aborted nor
   superseded. With no live probe, freshness is unproven and nothing moves.

Prose never classifies: "quota", "429", "rate limit" in stderr text, in a
non-error result, or in an agent message, does not trigger failover. An exit
code of 0 is never a failure, whatever was printed.

| outcome | code | next provider invoked? |
|---|---|---|
| success | — (normal unit enforcement follows) | no |
| unclassified non-zero exit | `BUS_TRANSPORT_FAILED` | no |
| launch failure / timeout | `BUS_EXECUTABLE_NOT_FOUND` / `BUS_COMMAND_TIMEOUT` | no |
| classified, but commit / dirt / branch / stale authority | `BUS_FAILOVER_REFUSED` | no |
| classified on every enabled provider | `BUS_PROVIDERS_EXHAUSTED` | each ran once |
| session handed to a provider that did not open it | `BUS_PROVIDER_SESSION_MISMATCH` | no |
| malformed / in-repository provider order | `BUS_PROVIDER_CONFIG_INVALID` | no |

Each provider is invoked at most once per unit, and a provider may not appear
twice in an order, so "everything is out of capacity" is one bounded failure.
Its detail names the capacity evidence, which the watcher's existing backoff
reads as quota and waits on the long schedule.

## Sessions

* A session belongs to the provider that opened it; `SessionRef.provider` is part
  of its identity and each provider's `argv` refuses any other owner's session.
* A later unit resumes the same provider's session opened in this process.
* A failover target with no session of its own for the wave starts fresh.
* A fresh Claude session after an earlier Claude attempt on the same wave gets a
  new deterministic id (`<wave>#<n>`), never the id a failed attempt may have
  created.
* Codex has no durable session: after a restart it starts fresh, because nothing
  durable names a thread id and guessing one (`--last`) could resume a stranger's
  conversation.

## Provider order

Operator configuration, never repository authority. First configured source wins:

1. a flag value (`--providers`, wired in PF2);
2. `MTJ_AGENT_BUS_PROVIDERS`, e.g. `codex,claude`;
3. a JSON file `{"order": [...]}` at `MTJ_AGENT_BUS_PROVIDER_CONFIG` or
   `~/.config/mtj-agent-bus/providers.json`, refused if it lies inside the checkout;
4. the default `claude,codex`.

Supported orders: `claude,codex`, `codex,claude`, `claude`, `codex`. Unknown,
duplicate or empty entries are refused. The resolver's source is statically
tested to contain no comment reader, envelope, subprocess or model output.

## Controls

`tests/refoundation/test_agent_bus_provider_failover.py`, 58 tests. Each of the
32 new guards in `agent_bus/providers.py` was rigged to its failing variant, shown
red against that module, and restored byte-exact (sha256 checked).

## Known limits

* The Codex argv and its event shapes follow the Codex CLI's documented
  `exec --json` interface; they were not run against a live `codex` binary in
  this unit. A wrong assumption fails closed: an unrecognised shape is
  unclassified and stops the unit instead of failing over.
* After a restart with `--resume`, Claude resumes its deterministic session even
  if an earlier process ran that wave's first unit on Codex. If that session does
  not exist, the CLI error is unclassified and the unit stops. It does not fail over.
* Any change under `agent_bus/` drifts from the wake workflow's pinned
  `BUS_REF` (`2ed4be3`), so the static test
  `test_bus_ref_is_a_commit_that_carries_the_r4_contract` goes red. Re-pinning is
  a workflow change, which this wave forbids. Reported, not repaired.
