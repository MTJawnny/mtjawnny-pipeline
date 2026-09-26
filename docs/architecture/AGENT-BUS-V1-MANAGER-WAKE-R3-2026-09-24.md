# Agent Bus v1 — R3 Manager wake candidate (GitHub Actions + Codex)

Status: **CANDIDATE, NOT DEPLOYED.** Evidence record for wave
`INFRA.AGENT-BUS-V1.MANAGER-WAKE-CODEX-ACTION.R3`, task comment 5808823791,
checkpoint 5820150646, accepted head `58c8345c56667f6776e941f85b79de0766cf22ff`.
It records what was built and measured. It is not authority.

## 1. What exists

| piece | where | commit |
| --- | --- | --- |
| abort / supersession repair | `agent_bus/machine.py`, `agent_bus/supervisor.py` | MW1 `78ff9604bfaeea548f0d712234369887e72cfc8a` |
| deterministic pre-gate | `agent_bus/manager_gate.py` | MW1 `78ff9604bfaeea548f0d712234369887e72cfc8a` |
| durable contract | `refoundation/AGENT-BUS-MANAGER-TRIGGER.md`, `refoundation/AGENT-BUS.md` | MW2 `3490e5dd73ef959538dfffaef48b963f8f6f8aa0` |
| workflow candidate | `.github/workflows/agent-bus-manager-wake.yml` | MW2, this record's commit |

The workflow checks out bus code at `BUS_REF = 3490e5dd73ef959538dfffaef48b963f8f6f8aa0`,
a commit, not a branch tip. That commit carries both the MW1 gate and the MW2
contract. A later Worker commit cannot change what the deployed gate runs;
changing it means changing the workflow, which means another review.

## 2. Upstream facts, measured on 2026-09-24

**`openai/codex-action`.** Tag `v1.12` is annotated, and it peels to commit
`86365089eb2b84e0a8fb0717b304f8bdcb13b20e`. GitHub marks that commit verified,
and it is identical to upstream `main` (compare: `identical`). The inputs this
workflow uses exist at that commit's `action.yml`: `openai-api-key`,
`prompt-file`, `output-schema-file`, `permission-profile`, `safety-strategy`,
`allow-users`, plus the `final-message` output. From the upstream README and
`docs/security.md` at that commit:

- `permission-profile` is preferred over the legacy `sandbox`, and the two are
  mutually exclusive. The README says to use `:read-only` for read-only
  workflows.
- The `read-only` sandbox cannot write or reach the network. But with
  passwordless `sudo`, which GitHub-hosted runners have by default, Codex could
  read the key from memory. So `drop-sudo` (the default) or `unprivileged-user`
  is required to protect the key.
- Upstream recommends running Codex as the last step of its job, and handing its
  output to a fresh job.
- Untrusted values must reach shell steps through `env:`, never spliced into
  `run:`.
- `allow-users` adds users on top of those with write access. With
  `allow-users: MTJawnny`, the check approves that login without an API call, so
  no extra token scope is needed (`src/checkActorPermissions.ts`).

**`actions/checkout`.** Tag `v7.0.1` resolves to commit
`3d3c42e5aac5ba805825da76410c181273ba90b1`.

**GitHub `issue_comment`.** From the `github/docs` source
(`events-that-trigger-workflows.md` and the reusable it includes):

- "This event will only trigger a workflow run if the workflow file exists on
  the default branch."
- `GITHUB_SHA` is the last commit on the default branch.
- A comment on a pull request is told apart from one on an issue by
  `github.event.issue.pull_request`.
- From the `GITHUB_TOKEN` reference: "events triggered by the `GITHUB_TOKEN`
  will not create a new workflow run". The exceptions are dispatch events and
  pull request open/sync; a comment is neither.

`main` (`3a2db848329cfcd54846a6ef6b4f3e1a4bc606b3`) contains neither `agent_bus/`
nor `refoundation/`. That is why the workflow pins its own bus checkout rather
than using the default-branch tree the event would give it.

## 3. The shape

| job | model | secret | token | what it does |
| --- | --- | --- | --- | --- |
| gate | no | no | contents, issues, pull-requests: read | `python3 -m agent_bus.manager_gate`, then an "already answered by any author" check |
| evidence | no | no | contents, issues: read | `python3 -m agent_bus selftest` on the result's `head` |
| manager | Codex | `OPENAI_API_KEY`, to the action only | contents, issues, pull-requests: read | reviews a context snapshot gathered before the model starts |
| publish | no | no | contents: read, issues: write | validates the model's JSON, then posts review, V, K |

The top-level permissions are `{}`, and no job holds `contents: write`. Pushing a
commit, moving a ref and merging a pull request all need `contents: write`.
Commenting on an issue or a pull request needs `issues: write`, which only
`publish` has. `publish` holds no secret and runs no model.

Every downstream job requires `needs.gate.outputs.wake == 'true'`. That output
comes from the last gate step, which runs only after the gate itself wrote
`wake=true`. A refusal, a crash or a missing output all leave `manager` skipped,
and `manager` is the only place `secrets.` appears.

## 4. Validation performed

**Static parse** (PyYAML `safe_load`, run from outside the tree; nothing was
committed for it). The intact workflow passes every check:

- the only trigger is `issue_comment` `created`;
- permissions are exactly as in the table above, and `publish` holding
  `issues: write` is the only write;
- every `uses:` is pinned to a 40-hex SHA equal to the tag it names, re-resolved
  live;
- every checkout sets `persist-credentials: false`;
- `secrets.` appears exactly once, as the Codex `openai-api-key` input;
- Codex runs `:read-only` with `drop-sudo` and `allow-users: MTJawnny`, with no
  `sandbox` or `codex-args`, as the last step of its job;
- no `run:` block contains a `${{ … }}` expression;
- the gate job runs `agent_bus.manager_gate`, and `evidence`, `manager` and
  `publish` all require `wake == 'true'`;
- `BUS_REF` is a commit SHA.

**Rigged controls.** 17 single-point weakenings were each applied to the file,
and each turned the checks red:

- permissions: `contents: write` added to `publish`, `pull-requests: write` in
  `manager`, and top-level `write-all`;
- pins: a tag instead of a SHA, and an older SHA;
- gating: `manager` gated on `always()`, a prefilter that no longer checks the
  PR number, and the gate command removed;
- secrets: the secret added to a shell step;
- Codex settings: the `:workspace` profile, the `unsafe` strategy,
  `allow-users: "*"`, and a step after Codex;
- the checkout: `persist-credentials: true`, and a branch tip as `BUS_REF`;
- the trigger: `edited` comments waking the Manager;
- shell injection: the comment body interpolated into `run:`.

**Prefilter** (the gate job's `if`, evaluated per event). A bus-shaped PR 76
comment by MTJawnny starts the job. Issue #1, PR 75, a drive-by author,
`github-actions[bot]` (this workflow's own posts), and prose on PR 76 do not.

**The real gate entry point on live GitHub** (read-only). Each run gave
`wake=false` and exit 0:

| event | code |
| --- | --- |
| the live R3 `WAVE_COMMAND` (comment 5820164568) | BUS_GATE_NOT_FOR_MANAGER |
| a comment on Issue #1 | BUS_GATE_WRONG_SURFACE |
| a comment on PR 75 | BUS_GATE_WRONG_SURFACE |
| an untrusted author | BUS_UNTRUSTED_AUTHOR |
| an edited comment | BUS_GATE_WRONG_EVENT |
| a WORKER result not really on PR 76 | BUS_GATE_COMMENT_MISMATCH |

The full negative and positive matrix, with a rig for every stage, is
`tests/refoundation/test_agent_bus_manager_wake.py` (MW1).

**The publish validator**, executed from the workflow text with posting stubbed
out, against the live authority. It refused every bad answer:

- not JSON;
- an extra key;
- a review answering another message;
- a review citing the superseded checkpoint 5808826592;
- K before V;
- a bus block smuggled into an Issue #1 body;
- only one ledger body.

It passed a valid answer. All three embedded Python blocks compile.

**Selftest.** `python3 -m agent_bus selftest` ran 267 tests; 265 pass. The two
failures predate R3 and are left unrepaired, as the task requires. Both assert
that `~/Library/LaunchAgents/com.mtjawnny.agent-bus.plist` does not exist, and
the armed Worker service installed it on this machine.

**Not measured.** No real OpenAI call was made, no secret exists, and the
workflow has never run. It cannot run until it is on the default branch.

## 5. What must still happen, and who decides

1. **Manager acceptance** of this candidate, then the Captain-authorized
   placement of the exact reviewed workflow blob on `main`.
2. **`OPENAI_API_KEY`** repository secret, created by the Captain.
3. **The posting identity — Captain decision, blocking deployment.** The publish
   job posts as `github-actions[bot]`. The bus trusts only operator-declared
   speakers (today `MTJawnny`), so:
   - its `WAVE_REVIEW` is `BUS_UNTRUSTED_AUTHOR` to the Worker;
   - a `K` it posts cannot select work through `agent_bus`;
   - but a human or a model reading Issue #1 by hand for "the latest `K`" would
     see it.

   Deploying without a decision would split machine-read and hand-read
   authority. The options are to trust the bot as a checkpoint speaker, to have
   the bot post proposals only (review on PR 76, the Captain posts V/K), or to
   post as the Captain's own identity. The last one needs a personal token, which
   is broader than this task's permission ceiling. The candidate implements the
   contract as written, V and K included, and deliberately does not choose.
4. **Re-runs.** A manual re-run of a finished workflow meets the
   already-answered checks before the model (gate job) and before posting
   (publish). Two concurrent runs for one comment are serialized by the
   concurrency group.
