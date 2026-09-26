# Agent Bus v1 R2 — a service that can actually run, and says so while it does

Status: implementation record for `INFRA.AGENT-BUS-V1.R2-LAUNCHD-RUNTIME-REPAIR`.
Not authority. The durable transport contract is `refoundation/AGENT-BUS.md`;
task selection remains GitHub Issue #1.

## 1. What the arming attempt found

The arming task required a dry-run inspection before installing. That inspection
is the entire reason this document exists: the service the accepted code would
have installed **could not run**, and would not have looked broken.

Two defects, both in the gap between "the code is correct" and "the deployed
thing works".

**The agent could not find its own tools.** `cli._watch` passed no environment to
`watcher.install`, so the plist's `EnvironmentVariables` was empty and the agent
inherited launchd's built-in PATH, `/usr/bin:/bin:/usr/sbin:/sbin`
(`launchctl getenv PATH` is unset, so that default applies). On the operator's
machine `git` is on that PATH; `gh` and `claude` are not. Reproduced under
exactly that environment, the watcher died on cycle 1 with
`FileNotFoundError: [Errno 2] No such file or directory: 'gh'`.

**And it would have died loudly in a way that looks quiet.** `FileNotFoundError`
is not a `BusError`, so the loop's `except BusError` did not catch it. The
process exited, `KeepAlive` restarted it, `ThrottleInterval` made that every
sixty seconds, forever. The transport was never reached, so the carefully
designed backoff never applied. `launchctl print` would have reported a service
that keeps starting, and the log would have held nothing but tracebacks.

**Separately, a healthy watcher was invisible.** The cycle log was returned when
`Watcher.run()` returned, and the installed argv carries no `--cycles`, so the
loop never returns. `watcher.out.log` would have stayed empty for exactly as long
as the service was working.

## 2. The repair

### PATH is derived, not written down

`watch install` now resolves the executables the service will actually invoke and
builds the PATH from where they are:

- `git` and `gh` always — the git helpers and the GitHub reader;
- `claude` as well when `--execute` appears in the program arguments, because an
  idle watcher never invokes a model and demanding `claude` from it would refuse
  an installation that would have worked.

The directories come out in the declared order, then the launchd defaults, each
added once. A missing executable raises `BUS_EXECUTABLE_NOT_FOUND` naming every
one that is missing, **on the dry run** — the dry run exists to discover that a
machine cannot host the service before the service is installed, not after.

Derivation wins over a caller-supplied PATH. A caller may add other variables; it
may not replace the one thing that decides whether the agent can find its tools.

Nothing is hardcoded, and the tests prove it by resolving to directories this
machine does not have: given a `which` that reports `/opt/tools/bin/gh`, the
derived PATH says `/opt/tools/bin`.

### Every cycle writes a line, as it happens

The watcher takes an emitter, defaulting to one JSON object per line on stdout,
**flushed**. Flushed because launchd redirects stdout to a file, Python
block-buffers a file, and an unflushed long-running watcher writes its first line
when it exits — which for a healthy watcher is never.

Each record carries the cycle number, a UTC timestamp, the action and reason, and
on failure the code, the detail, the consecutive-failure count and the next
sleep. It is emitted **before** the sleep, because a record that appears after
the wait is a record of what the watcher was doing two minutes ago. A test rigs
that ordering and watches it go red.

### A launch failure is a failure

`Runner` now converts what `subprocess` raises into the vocabulary the loop
already handles: `BUS_EXECUTABLE_NOT_FOUND` for a missing or unrunnable binary,
`BUS_COMMAND_TIMEOUT` for one that hangs. The git helpers raise `BUS_GIT_FAILED`
instead of `RuntimeError`, and the watcher also catches `AuthorityError` —
GitHub being unreachable is an expected condition of a service that runs for
days, not a bug — logging it as `BUS_AUTHORITY_UNRESOLVED`.

The loop therefore backs off from all of them instead of exiting. It does **not**
give up after N failures: exiting is what hands the restart to `KeepAlive`, and
that is the crash loop this repair removes.

## 3. Demonstrated, not asserted

Under `env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin` — launchd's exact environment —
two bounded cycles now produce:

```text
{"at": "...:53:28Z", "code": "BUS_EXECUTABLE_NOT_FOUND", "cycle": 1, "failures": 1, "outcome": "failed", "sleep": 60.0}
{"at": "...:54:28Z", "code": "BUS_EXECUTABLE_NOT_FOUND", "cycle": 2, "failures": 2, "outcome": "failed", "sleep": 120.0}
```

and exit 0. The sixty seconds between the two timestamps is the backoff actually
sleeping, and the lines appeared as they happened rather than at exit. Before the
repair the same command produced a traceback and exit 1.

Under the derived PATH, in the same otherwise-stripped environment, the same
command polls: `{"action": "NONE", "outcome": "polled", "reason": "BUS_NOTHING_ACTIONABLE"}`.

Nothing was installed, written to `~/Library/LaunchAgents`, or started. That was
prohibited by this task and remains the Captain's decision.

## 4. What is unchanged

Fail-closed trust, the PR 76 transport surface, bounded-wave law, the
single-instance lock, and dry-run-by-default service verbs are all untouched, and
their tests still pass unchanged. No Foundry semantics, no production build
behaviour, no codebook, no S16, no merge, no `main`.
