# Agent Bus v1 R1 — making unattended execution safe enough to arm

Status: implementation record for `INFRA.AGENT-BUS-V1.R1-UNATTENDED-SAFETY-AND-WAKE`.
Not authority. The durable transport contract is `refoundation/AGENT-BUS.md`;
the Manager's wake contract is `refoundation/AGENT-BUS-MANAGER-TRIGGER.md`;
task selection remains GitHub Issue #1.

## 1. What the review found, and what it means

The bootstrap built a protocol and a state machine. Both hold. What it did not
build was the difference between **a correct message** and **a safe action**, and
every one of the five repairs below lives in that gap.

The sharpest example is trust. v1 had a speaker check, and it was correct as
written — and its default was empty, and an empty set meant *no restriction*. On
a public repository that is not a small bug. Anyone could have posted a
perfectly current `WAVE_COMMAND` and had it accepted, because every other field
would have been right.

The lesson generalises: a control whose safe state is "configured" fails open,
and a control plane may only fail closed.

## 2. Fail-closed trust

- Trust is REQUIRED by `fold()` and by authority resolution. There is no default
  parameter to forget.
- Nothing configured means nobody is trusted, everywhere, including read-only
  inspection. The error names the three ways to configure it.
- Trust is resolved from a flag, an environment variable, or a file **outside the
  working tree** — never from repository data. A wave runs inside the checkout;
  a trust list kept there would be one scope escape away from choosing who
  commands the next wave.
- A trust file that cannot be parsed raises. Falling back to "nobody" would look
  identical to a correctly locked-down bus, which is the failure mode this whole
  repair exists to remove.

Authority resolution gets the same rule, with one deliberate asymmetry: an
untrusted checkpoint-shaped comment is **skipped and reported**, not fatal.
Obeying it would hand over the Worker; halting on it would hand any passer-by a
way to stop the Worker by posting one. Both are refused; the attempt is named in
the report.

## 3. Preflight — ask git, not the brief

A Worker brief that says "branch X" is a claim. Before any model invocation the
supervisor measures the checkout and refuses on any disagreement: wrong worktree,
wrong branch, base not an ancestor of HEAD, uncommitted changes, or a unit the
bus calls done that this checkout has no commit for.

Problems are collected rather than short-circuited, because an operator woken by
a failed preflight should see everything that is wrong at once.

Preflight runs on a dry run too. A dry run whose preflight was skipped would
report a dispatch that could not legally have happened.

**One protocol addition.** A repair wave builds on an unaccepted candidate — this
very task does. `base` must keep meaning "the accepted head" or stale-command
detection dies, so the candidate gets its own optional field, `candidate_base`,
and preflight checks that the accepted head is an ancestor of it. Two ideas, two
fields, rather than one quietly standing in for the other.

## 4. Enforcement — measure the unit, not the intention

`allow_paths`, `deny_paths`, commit boundaries and trailers were text handed to a
model. Now every unit is re-measured against the repository before the next one
may start: a mutating unit must commit, every commit must carry this wave's and
this unit's trailers, nothing may change outside the allowlist or inside the
denylist, the tree must be clean again, and a read-only unit must have changed
nothing.

The glob matcher is written out rather than delegated to `fnmatch`, whose `*`
crosses `/` — which would silently make `agent_bus/*` an allowlist for the whole
repository.

A failing unit stops the wave where it stands. Nothing is reverted, reset or
cleaned: a scope escape is evidence, and tidying it away would destroy the only
record of what happened.

## 5. Autonomous waves, one unit at a time

The supervisor now runs the whole wave: one Claude invocation per unit, the first
opening a session derived from the wave id and every later one resuming it, a
durable `WAVE_PROGRESS` after each unit, and exactly one `WAVE_RESULT` at the
end. No Manager review happens between units — that was the point of bounded
waves — but the repository has to agree after every one of them.

Worker message ids are DERIVED from wave, unit and kind rather than generated, so
re-posting after a crash is a duplicate the state machine already ignores. A
random id would turn every retry into a new fact.

## 6. The watcher, and why it is boring

`poll --execute` was one shot. A Worker that exists only while somebody is typing
is not a wake mechanism.

- **One instance, ever**: an exclusive `flock` outside the repository. A pid file
  was rejected — it survives `kill -9` and then locks the watcher out of its own
  machine forever.
- **No hot loop**: every cycle sleeps, successes included. Failures back off
  exponentially to an hour; a quota or rate-limit refusal starts at fifteen
  minutes and backs off to six hours, because retrying a quota wall every minute
  is how an account gets itself throttled for a day.
- **Clean shutdown**: a signal sets a flag, the cycle finishes, the loop returns
  its log.
- **Injected time and no randomness**: the backoff schedule is asserted in tests
  rather than waited for.

The macOS service is a launchd agent under the operator's own
`~/Library/LaunchAgents`, with `KeepAlive`, `RunAtLoad` and a restart throttle.
Its logs and lock live under `~/.local/state/mtj-agent-bus`. Nothing reads or
writes `~/.claude`. Every service verb — install, status, start, stop, uninstall
— changes nothing without an explicit `--apply`, and this task did not apply any
of them: arming the service on the operator's machine is the Captain's call.

## 7. Manager wake contract

`refoundation/AGENT-BUS-MANAGER-TRIGGER.md` is the standing instruction for a
ChatGPT Work GitHub task: wake only on PR 76 activity, act only on a valid
`WAVE_RESULT` or `CAPTAIN_REQUIRED` from a trusted Worker, verify against live
repository state before believing any claim, answer with a `WAVE_REVIEW` on the
transport surface and then `V` and `K` on Issue #1, and authorize a successor
wave only where the live authority permits.

Creating that Work task is the one external step. It is named in the document
rather than implied, and the manual fallback — a human reading PR 76 and
following the same sections — is the design, not a workaround.

## 8. What is still not armed

Unattended execution is **built and not started**. No launchd agent was
installed, no watcher was left running, and no wave has ever been executed by the
supervisor against the real repository. The controls above are what would have to
be true for arming it to be reasonable; whether to arm it is a decision with an
owner, and that owner is not the Worker.
