# Agent Bus v1 — architecture, measurements, and what is still manual

Status: implementation record for the `INFRA.AGENT-BUS-V1.BOOTSTRAP` task.
Not authority. The durable transport contract is `refoundation/AGENT-BUS.md`;
task selection remains GitHub Issue #1.

## 1. What was measured before anything was designed

Every choice below follows from these, taken on 2026-09-23 on the operator's
machine and against the live repository.

| measurement | value |
| --- | --- |
| Claude Code CLI | 2.1.281, at a user-local path, authenticated from the operator's own keychain session |
| headless flags present | "-p", "--output-format json", "--session-id", "--resume", "--permission-mode", "--add-dir" |
| Anthropic API key in the environment or repository | none; repository secrets are the three R2 build secrets only |
| GitHub CLI | 2.95.0, logged in as the repository owner, scopes gist / read:org / repo / workflow |
| repository visibility | public |
| default branch | "main", last moved 2026-08-09, containing exactly one workflow |
| accepted base of this task | not an ancestor of the default branch |
| historical Issue #1 traffic | 833 comments |

Two of those decide the whole design.

**No API key, but a working authenticated CLI.** So the primary Claude-side
transport is the operator's own `claude -p`, and nothing in this change requires
separate API billing.

**The accepted base is not on the default branch.** GitHub runs
"issue_comment", "issues" and "schedule" workflows *only* from the default
branch. A hosted wake-on-comment workflow therefore CANNOT be armed from this
branch, and arming it would require a merge to "main" — which this task forbids
and which is Captain's decision anyway. The hosted path is therefore documented
and declared, never faked. "pull_request" workflows do run from the pull
request's own branch, which is why the validation workflow added here is real
and runs on the implementation pull request.

## 2. The shape

```text
             Issue #1  (latest K -> active T)          <-- the only authority
                  |  read, never written by the bus
                  v
   MANAGER  --WAVE_COMMAND-->  [ transport surface ]  --> supervisor --> claude -p
  (ChatGPT)                      GitHub comments                          (Worker)
       ^                                                                     |
       +----------------------- WAVE_RESULT -------------------------------- +
```

Three separations are load-bearing.

**Authority / transport.** `Authority` is an input to the state machine, read
from Issue #1's latest checkpoint. No message can produce one. A Manager
`ACCEPT` verdict is recorded as a proposal and reported as unratified until a
checkpoint carries the head. This is asserted directly by tests.

**Command / execution.** The state machine decides what is actionable; the
supervisor decides whether to act, at most once per pass. A redelivered event
reaches a machine that has already recorded the message id, so it is a no-op
with a code rather than a second run.

**Protocol / transport mechanism.** The envelope, the machine and the wave model
know nothing about Claude. Transports are objects with one `dispatch` method,
and swapping one changes no protocol law.

## 3. Message format, and why it is JSON

A message is a fenced block whose info string is exactly `mtj-bus`, containing
JSON. Prose is not parsed anywhere.

Rejected alternatives:

- **YAML envelopes.** The repository is stdlib-only by standing constraint, so
  YAML would mean either a new dependency or a hand-rolled reader — and a
  hand-rolled reader over human-authored text is prose parsing with better
  manners. JSON is in the standard library and fails loudly.
- **Reusing the existing `mtj-task/0` and `mtj-checkpoint/2` YAML blocks.** That
  would collapse authority and transport into one format and make every one of
  833 historical comments a candidate event. The bus uses a different fence on
  purpose, and the live measurement below shows why it matters.
- **Free-form "at-claude" comments.** Any comment could then authorize work,
  which is the loop hazard this task exists to remove.

Strictness is deliberate: unknown fields, duplicate JSON keys, wrong types,
unsupported versions and actor/kind mismatches are rejections with stable codes.
A message that does not validate authorizes nothing.

## 4. Bounded waves

A `WAVE_COMMAND` carries units with `id`, `objective`, `depends_on`,
`allow_paths`, `validation` and `mutating`, plus optional `deny_paths`,
`negative_controls`, `stop_conditions`, `commit_boundary` and `concurrency`.

Order is topological with ties broken by declared position, so it is identical
on every machine and across restarts. A mutating unit with no scope, or any unit
with no validation, is rejected at parse time rather than discovered later.

Unit completion is recorded twice, on purpose: as a posted progress message, and
as commit trailers on the unit's own commit. A lost comment cannot erase a real
commit, and resume arithmetic can be re-derived from the branch alone.

## 5. Loop prevention

- An actor acts only on kinds addressed to it AND spoken by somebody else, so
  self-waking is impossible by construction, not by convention.
- `message_id` is the idempotency key; duplicates are recorded and dropped.
- A wave may be commanded once.
- A claimed wave is not re-dispatched without an explicit human resume.
- One supervisor pass acts on at most one message.

**Live negative control.** Folding all 833 existing Issue #1 comments under the
live authority yields 833 inert records, zero accepted messages and zero pending
actions for either agent. The bus cannot be woken by anything already said.

## 6. Claude-side transport

`LocalClaudeTransport` builds the argv for the operator's authenticated CLI:
`claude -p <brief> --output-format json --permission-mode acceptEdits --add-dir
<repo>`, plus `--session-id <uuid>` on first dispatch and `--resume <uuid>` when
continuing. The session id is derived from the wave id, so a resumed wave
continues the same conversation rather than starting a stranger.

Dry run is the default everywhere, and it returns the argv without executing it.

`HostedActionTransport` exists as a named, declared transport that refuses with
the exact missing prerequisites rather than pretending to dispatch. Rejected as
the primary path because it needs an API-key secret the repository does not have
and a default-branch merge this task forbids.

## 7. ChatGPT Manager transport

ChatGPT Work triggers on GitHub pull request activity, so the Worker posts
`WAVE_RESULT` messages where a pull request event is produced, and the Manager
inspects live repository state before believing any claim in them. The Manager
answers with `WAVE_REVIEW`, and then posts `V` and `K` on Issue #1 — the bus
records the verdict, the checkpoint is what makes it true.

Browser-driving chatgpt.com was rejected outright: it is not durable, not
inspectable, and not recoverable.

## 8. What a human must still do outside this repository

1. **Configure the ChatGPT Work GitHub connector** to watch this repository and
   wake on pull request comment activity. No repository code can create that
   task; claiming otherwise would be the exact kind of fake this task forbids.
2. **Decide whether the transport pull request is the event surface** and keep it
   open, unmerged and clearly labelled.
3. **Only if the hosted path is ever wanted:** merge a wake workflow to the
   default branch and add an Anthropic API key secret. Both are Captain
   decisions with billing and blast-radius consequences, and neither is required
   for the local transport to work.

## 9. Operator commands

```text
python3 -m agent_bus authority          # latest K -> active T, machine-read
python3 -m agent_bus state              # fold the live comment stream
python3 -m agent_bus resume --wave <id> # what is left, from durable evidence
python3 -m agent_bus validate <file>    # strict validation, stable exit codes
python3 -m agent_bus plan <file>        # deterministic unit order
python3 -m agent_bus render <file>      # wrap a validated message for posting
python3 -m agent_bus poll               # dry run: what would be dispatched
python3 -m agent_bus poll --execute     # the only line that spends anything
python3 -m agent_bus selftest           # the bus suite
```

Exit codes: 0 answered, 2 a bus rejection with its code, 3 authority unresolved.
