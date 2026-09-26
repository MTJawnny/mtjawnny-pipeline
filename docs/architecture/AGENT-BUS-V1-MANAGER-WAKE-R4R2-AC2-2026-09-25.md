# Agent Bus v1 — R4.R2 AC2: queue dispositions and no-model recovery

Status: **CANDIDATE, NOT DEPLOYED.** Evidence record for unit AC2 of wave
`INFRA.AGENT-BUS-V1.MANAGER-WAKE-CODEX-ACTION.R4.R2.AR1` (task 5821223577,
checkpoint 5827051128, accepted head `58c8345c…` unchanged). It repairs blockers
3 and 4 of verdict 5825603412. It is not authority; the contract is
`refoundation/AGENT-BUS-MANAGER-TRIGGER.md` sections 3, 5 and 7.

## 1. What changed

| piece | where |
| --- | --- |
| `CAPTAIN_REQUIRED` ahead of `WAVE_RESULT` in the Manager queue | `agent_bus/machine.py` |
| per-link authority state on the chain | `agent_bus/issue.py` (`Resolution.links`, `authority_at`) |
| `mtj-disposition/0`: derived, written once, checked exactly; the dispose path; `owed` | `agent_bus/publisher.py`, `agent_bus/ledger.py`, `agent_bus/trust.py` |
| `mode=dispose`; resume whenever a committed `K` owes anything; the `workflow_run` recovery sweep | `agent_bus/manager_gate.py` |
| a review records the digest it reviewed | `agent_bus/transition.py`, `agent_bus/protocol.py` |
| triggers: `issue_comment` created + `workflow_run` of this workflow only | `agent_bus/workflow_policy.py` |
| recovery trigger; the goal plan's checks in the evidence job, handed to publish; `BUS_REF` | `.github/workflows/agent-bus-manager-wake.yml` |
| AC2 controls Q1–R8, with rigs | `tests/refoundation/test_agent_bus_recovery.py` (new) |

Two commits: the code, contract and workflow wiring (`2ed4be3`), then `BUS_REF`
moved to `2ed4be3` with the tests and this record. A test checks that the bus code
and contract at `BUS_REF` are byte-identical to the candidate's, so the workflow
runs exactly what is reviewed.

## 2. Queue: every message ends somewhere

- Under one `K` only the queue head is reviewed. A Worker `CAPTAIN_REQUIRED` is
  always ahead of a `WAVE_RESULT`, so a result's checkpoint can never displace a
  question. A result already mid-transaction yields: its next revalidation sees
  it is no longer the head (BUS_GATE_QUEUED, exit 4, no `K`).
- When a `K` commits, every other valid Manager-bound message under the replaced
  checkpoint gets one `mtj-disposition/0` on Issue #1. The record names the
  message, the link that superseded it and the deciding transaction. For a
  Worker question it carries `captain_attention: YES` and `next:
  CAPTAIN_REQUIRED`.
- "Valid" is decided by folding under the authority as it stood at that link.
  The record is derived from the message and the chain only. A publisher record
  counts only if it is byte-identical to that derivation.
- A message that arrives citing an already-replaced checkpoint (a race with a
  commit, or a hand-moved `K`) is admitted as `mode=dispose` by its own event and
  gets the same record, with no model and no `K`.
- `K.unanswered` is kept as the list at commit time. The dispositions are what
  make it terminal.

## 3. Recovery: once, automatically, without the model

GitHub creates no workflow run for a comment posted with `GITHUB_TOKEN`, so no
bot comment, recovery-shaped or otherwise, can wake anything. That is also why
the requested "issue-comment recovery event" is impossible without a PAT or an
App. The equivalent that needs no new credential or permission is `workflow_run`:
- the workflow also runs when a comment-triggered run of itself completes
  `failure`, `cancelled` or `timed_out`;
- the gate (`manager_gate.recover`) reads no comment body as input;
- it sweeps role-validated durable state for the one transaction owing a write:
  a publisher `K` still owing a disposition or its successor, or a publisher
  review with no `K` yet for the live queue head;
- it admits only `mode=resume`, and the model job also requires
  `github.event_name == 'issue_comment'`;
- a recovery run's own completion is refused, both in the job `if` and in the
  gate (BUS_GATE_WRONG_EVENT). So the bound is one recovery per comment-triggered
  run.

| interruption after | recovery run does |
| --- | --- |
| review | V, K, disposition, successor |
| V | K, disposition, successor |
| K | disposition, successor |
| disposition | successor |
| successor | nothing owed (BUS_GATE_NOTHING_OWED) |
| before the first write | nothing: no decision is durable, and recovery never asks the model |

## 4. Validation performed

`tests/refoundation/test_agent_bus_recovery.py`, 25 tests, named by the unit's
validation order:

| control | shown | rig shown red |
| --- | --- | --- |
| Q1 no conflict, no orphan | one `K` links; the other message disposed; its late event is ALREADY_HANDLED and a publish of it writes nothing; a late arrival is disposed from its own event; an invalid stale message is refused, not disposed; a forged disposition does not count | no dispositions → the other message is BUS_STALE_AUTHORITY again; exactness bypassed → a stranger's text counts as done |
| Q2 questions first | the question is the head and the result waits; answering it stops autonomy and disposes of the result; a question racing the commit is recorded for the Captain; an in-flight result yields before its `K` | no priority → the result is accepted over the question |
| R3 convergence | a death after each of 5 writes is finished by one recovery run: exactly one review, V, K, disposition and command; a second recovery finds nothing; a planned ACCEPT successor recovers too; an edited message fails closed | no sweep → the command is never posted |
| R4 narrow entry | only a failed comment-run of this workflow in this repository recovers; strangers' reviews and K, bot-authored results and other workflows' reviews cannot enter | recovery-of-recovery admitted; `is_publisher` widened → a stranger's review enters |
| R5 model only on a fresh trusted Worker message | recovery only ever answers `resume`; the model job requires `issue_comment`; the comment gate still refuses Manager and bot messages | recovery forced to `review` → only the job guard is left |
| R6 no new credential | only `publish` writes, and only `issues`; no schedule, dispatch, rerun, PAT, App, push or merge text; one secret job | static rigs: polling trigger, another workflow, model on recovery, recovery of recovery, checks not run, evidence not handed over |

The existing R4 and AC1 suites stay green. Two expectations changed on purpose:
- R3-D6 now also asserts the displaced result's disposition.
- The pipeline test that expected BUS_STALE_AUTHORITY when a human `K` lands
  between gate and publish now expects that message's disposition.

**Selftest.** `python3 -m agent_bus selftest`: 416 tests, 414 pass. The two
failures predate R4 and are unchanged: both assert that the launchd plist does
not exist, and the armed local Worker installed it on this machine.

**Live, read-only.** The authority still resolves `K` 5827051128 → task
5821223577, `h` `58c8345c…`, with no refused candidates and no lookalikes.
`manager_gate.recover` against the live Issue #1 and PR 76 answers
BUS_GATE_NOTHING_OWED. `workflow_policy` passes.

## 5. Limits and decisions to ratify

- **One automatic attempt.** If the recovery run also fails, or a run dies
  before its first durable write, finishing it is still a manual rerun. Chaining
  recoveries would rely on GitHub's own depth cap for loop-freedom; this
  candidate does not.
- **Disposition is not a verdict.** A displaced `WAVE_RESULT` is recorded as
  superseded, never reviewed. A Worker question that races a commit is recorded
  with `captain_attention: YES`. It does not move `a` to 0 by itself: a
  checkpoint that already selected a planned successor stands.
- **Hand-moved checkpoints.** When a human `K` replaces a checkpoint, the
  publisher disposes only of messages whose own event arrives after it. The
  rest are the human Manager's to answer.
- **Nothing is activated.** The workflow still fires only once placed on `main`,
  and there is still no `OPENAI_API_KEY` secret and no goal plan on Issue #1.
