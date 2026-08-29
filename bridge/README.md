# mtj-bridge v0 — operator guide

Manager/Worker automation for the MTG Thesaurus refoundation, using **GitHub as
the durable control plane**. Captain stops being the message courier; Captain
does not stop being the decision authority.

This is **temporary refoundation infrastructure**. It lives in `bridge/`, imports
nothing from the Foundry/AQ4 codebase, and assumes no P0.1 D1–D9 architecture
choice has been ratified. It is meant to be replaceable.

---

## 1. What it does

```
GitHub issue (mtj-task/1)
        │
        ▼
   mtj-worker ──► FRESH `claude -p` session ──► edits files in an isolated worktree
        │                                        (the model never runs git)
        ├─ wrapper commits, pushes, opens a DRAFT PR
        └─ posts mtj-result/1 back to the issue
        │
        ▼
   mtj-manager ──► FRESH OpenAI Responses call ──► emits mtj-review/1 text
        │
        ▼
   policy.decide()   ← deterministic, no model, no network
        │
        ├─ PASS   → post review (+ next task only if one was already authorized)
        ├─ REPAIR → one bounded repair task, up to the repair limit
        ├─ CAPTAIN_DECISION_REQUIRED → post decision packet, HALT
        └─ STOP   → HALT
```

**Nothing merges.** Bridge v0 has no merge code path at all; `merge_pr` and
`enable_auto_merge` are in `policy.FORBIDDEN_ACTIONS` and have no implementation.

## 2. Install

No install step and no packaging decision — the bridge runs from the repo.

```bash
cd bridge
python3 -m unittest discover -s tests -t .   # must report OK, offline, no credentials
```

**The suite must end in `OK`.** No document in this repository states a test count:
a hard-coded number in prose goes stale the moment a test is added, and three
different stale counts in three documents is what the Manager review caught.
The command and its pass/fail requirement are the durable contract; run
`bridge/bin/mtj-selftest` to print the live count.

Requires Python 3.11+ (developed on 3.14.6). The core has **no third-party
dependencies**: protocol parsing is stdlib-only so the offline tests and the
whole state machine run with nothing installed.

`openai` is needed **only** for a live `mtj-manager` run:

```bash
python3 -m venv .venv && .venv/bin/pip install openai
```

## 3. Credentials

The bridge **never reads, prints, stores, or commits a credential.** Each tool
resolves its own:

| Service | How | Operator action |
|---|---|---|
| GitHub | `gh` CLI keyring auth | already authenticated (`gh auth status`) |
| Claude | Claude Code's own auth | already authenticated |
| OpenAI | `OPENAI_API_KEY` read by the SDK | **not yet set — Captain must provide** |

Export the OpenAI key in the operator shell only, for the duration of a run:

```bash
export OPENAI_API_KEY=...      # never written to a file in this repo
export MTJ_MANAGER_MODEL=gpt-5.6-sol   # model is config, not architecture
```

Every log line and every GitHub body passes through `redact.redact()`, which
scrubs known token shapes *and* the literal values of the secret env vars.

## 4. Commands

All three commands support `--dry-run` and `--once`.

```bash
# See what the worker WOULD do. No model call, no mutation, no GitHub write.
bridge/bin/mtj-worker --dry-run --repo-root /Users/jawnny/Projects/mtjawnny-pipeline

# Execute exactly one READY task.
bridge/bin/mtj-worker --once --repo-root /path/to/repo

# Review one issue's latest result; print the review instead of posting it.
bridge/bin/mtj-manager --issue 3 --dry-run --repo-root /path/to/repo

# One complete Worker→Manager cycle, then stop. Run this before any loop mode.
bridge/bin/mtj-cycle --issue 3 --dry-run --repo-root /path/to/repo
```

`--repo-root` must point at a checkout the bridge may fetch in. **It must never
be the Captain's dirty main worktree** for a mutating run; the bridge creates its
own worktree under `~/.mtj-bridge/worktrees/` for every task.

### Polling mode

**Not built, deliberately.** The task contract allows polling for v0, but
`mtj-cycle` runs one cycle and exits. Enable a loop only after the state machine
has been trusted through several supervised single cycles. When it is added it
must keep `max_cycles` and `max_repairs`, which already exist in `policy.decide()`.

## 4a. Task-body requirements (enforced, not advisory)

A `mtj-task/1` that mutates **must** declare machine-readable path scope, or the
worker STOPs before the model is invoked:

```yaml
scope:
  kind: infrastructure_only
  allow_paths:
    - "bridge/**"
  deny_paths:
    - "docs/**"
validation:
  commands:
    - python3 -m unittest discover -s bridge/tests -t bridge
```

- **Absence of scope is not permission.** A read-only task declares
  `scope.kind: read_only` instead; it is then exempt.
- **`validation.commands` are run by the WRAPPER**, after the model's edits and
  before the commit, with argv captured, rc captured, and output bounded and
  redacted into the result as `evidence:`. A non-zero rc fails the result and no
  PR is opened.
- Commands are run **without a shell** and their executable must be in
  `policy.VALIDATION_EXECUTABLE_ALLOWLIST`. Shell wrappers (`sh -c`, `bash -c`,
  `sudo`, `env`) are refused by name. A task body is model-authored, so an
  unrestricted command list would convert review authority into arbitrary code
  execution on the operator's host.
- Quote backticked scalars in task bodies (the parser tolerates them; strict YAML
  readers do not).

## 5. Captain boundaries

`policy.decide()` halts and posts a decision packet — **whatever the model says** —
when any of these is true:

- a changed path matches `policy.CAPTAIN_PATHS` (codebook, ratified registries,
  naming grammar, AQ4 frozen inputs, authority docs, `CLAUDE.md`, workflows);
- the Worker result text signals gate weakening, ratification, a D1–D9 choice, or
  a conflict between durable authorities;
- the Worker itself declared `decision_required`.

The invariant, pinned by `tests/test_policy.py::TestModelCannotUnlock`:

> **A model verdict can only ever make the outcome more restrictive.**
> A model returning `PASS` cannot unlock a Captain-reserved change, cannot
> advance past a failed Worker result, and cannot override a base mismatch.

A compromised or prompt-injected Manager can, at worst, halt the automation.

### The Worker's git prohibition is structural, not prompt-level

`ClaudeCliAdapter` passes a deny list through **both** `--disallowedTools` and a
per-invocation `--settings` file, covering `git commit/push/reset/rebase/merge/
remote/branch/checkout/worktree/clean/stash/update-ref/config` and `gh`.

Measured against Claude Code 2.1.251: a denied command **does not execute** and is
reported in the invocation's `permission_denials`. Measured in the same run: under
`--permission-mode acceptEdits`, file edits are auto-approved but arbitrary `Bash`
is **not**, which is why acceptance validation is wrapper-owned by construction
rather than delegated to the model.

## 5a. Before a live mutation cycle: run the canary

```bash
export OPENAI_API_KEY=...
bridge/bin/mtj-manager --canary          # read-only; writes nothing anywhere
```

The canary exercises the **real** OpenAI adapter and asserts its output survives
`parse_review` and the schema gate. It proves the credential resolves, the
configured model exists, and the contract holds — none of which the offline suite
can prove. Exit 0 means proceed; exit 4 means blocked.

## 6. Recovery after a crash

Durable state is GitHub. The local `~/.mtj-bridge/` directory is a cache and a
same-host lock, and deleting it must not change any conclusion.

```bash
rm -rf ~/.mtj-bridge          # safe
bridge/bin/mtj-cycle --issue <n> --dry-run
```

`state.reconstruct(github, issue)` reads the issue's comments and returns the
phase — `WORKER_EXECUTE`, `MANAGER_REVIEW`, `HALTED`, or `COMPLETE` — from GitHub
alone. `tests/test_integration_offline.py::TestCrashRecovery` deletes all local
state mid-cycle and asserts the phase is still recovered exactly.

If a worktree was left behind, it is retained on purpose for inspection:

```bash
git -C /path/to/repo worktree list
git -C /path/to/repo worktree remove ~/.mtj-bridge/worktrees/<name>
```

## 7. How a fresh session reconstructs state

**Fresh Claude Worker.** It gets no transcript. `worker.build_prompt()` assembles,
from durable sources only: the four `refoundation/` bootstrap files read out of
the git ref, the measured base SHA, the isolated worktree path, and the issue's
task contract. A fresh `--session-id` is generated per task and `--continue` /
`--resume` are never passed.

**Fresh OpenAI Manager.** `manager.build_review_prompt()` assembles the bootstrap
files, the task contract, the Worker result, and the measured PR diff paths. There
is no thread and no conversation id.

If either prompt is insufficient to do the job, that is a refoundation
architecture defect to report — not something to fix by feeding in old transcripts.

## 8. Known limitations

See `ARCHITECTURE.md` §6 for the full list, including the two deliberate YAML
deviations and the reasons polling and repair-task creation are not automated.
