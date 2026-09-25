# Agent Bus v1 — R4.R2 AC1: Captain goal continuation and task validation

Status: **CANDIDATE, NOT DEPLOYED.** Evidence record for unit AC1 of wave
`INFRA.AGENT-BUS-V1.MANAGER-WAKE-CODEX-ACTION.R4.R2.AR1`:

| field | value |
| --- | --- |
| task comment | 5821223577 |
| checkpoint | 5827051128 |
| accepted head | `58c8345c56667f6776e941f85b79de0766cf22ff` (unchanged) |
| candidate base | `7abbfb633518e6bcbe7d1e799bf12f561a1f2b98` |
| repairs verdict | 5825603412, blockers 1 and 2 and the repair-budget finding |

It records what was built and measured. It is not authority. The contract is
`refoundation/AGENT-BUS-MANAGER-TRIGGER.md` sections 4–6.

## 1. What changed

| piece | where |
| --- | --- |
| goal plan parser, command binding, planned successor, evidence, checks runner | `agent_bus/goal.py` (new) |
| transition law: plan-derived budget, successor and ACCEPT gate | `agent_bus/transition.py` |
| publisher: binding, durable evidence, owed-successor posting, `--validation-file` | `agent_bus/publisher.py` |
| resolver and fold: plan-aware chain validation; the one owed successor | `agent_bus/issue.py`, `agent_bus/machine.py` |
| gate: resume when any successor is owed | `agent_bus/manager_gate.py` |
| `goal` on WAVE_COMMAND, `validation` on WAVE_REVIEW | `agent_bus/protocol.py` |
| V carries `goal_plan` and `validation` | `agent_bus/ledger.py` |
| BUS_GOAL_PLAN_INVALID | `agent_bus/errors.py` |
| AC1 controls V1–V8, with rigs | `tests/refoundation/test_agent_bus_goal.py` (new) |

`MAX_REPAIR_ROUNDS` is gone. No budget, successor or check list is chosen in
repository code any more.

## 2. The goal plan

An Issue #1 comment by a trusted speaker that opens with one fenced `mtj-goal`
JSON block:

```
{"schema": "mtj-goal/1", "goal": "<id>", "captain_decision": <earlier trusted comment>,
 "repair_budget": <int >= 0>, "terminal": "<wave>",
 "waves": [{"wave": "<wave>", "task": <task comment>,
            "command": {"branch", "review_boundary", "units", "stop_conditions"?},
            "validation": [{"id": "<check>", "argv": ["..."]}],
            "next": "<wave>" | null}]}
```

Exactly the terminal wave has a null `next`; every edge exists; no path loops.
A command binds only by naming the plan (`body.goal = {plan, digest}`) and being
exactly its planned wave: wave id, task and command. Anything else is unbound.

## 3. Transition law, as built

| verdict | bound | `h` | `a` | successor | `next` |
| --- | --- | --- | --- | --- | --- |
| ACCEPT, checks all green on the result head | nonterminal | result head | planned `next` task | `mgr-next-<txn>`: the planned command, on the new head, under the new K | WORKER_EXECUTE_SUCCESSOR |
| ACCEPT, checks all green on the result head | terminal | result head | 0 | none | GOAL_COMPLETE |
| ACCEPT, evidence missing, red, other head/plan/wave/checks | yes | refused before any write | | | |
| REPAIR within `repair_budget` | yes | unchanged | unchanged | `mgr-repair-<txn>`, carrying the plan reference | WORKER_EXECUTE_REPAIR |
| REPAIR past `repair_budget` | yes | unchanged | 0 | none (override REPAIR_BUDGET_EXHAUSTED) | CAPTAIN_REQUIRED |
| ACCEPT or REPAIR | no | unchanged | 0 | none (override GOAL_PLAN_UNBOUND) | CAPTAIN_REQUIRED |
| CAPTAIN | any | unchanged | 0 | none | CAPTAIN_REQUIRED |

The budget counts consecutive repairs of one planned wave; a planned successor
starts its own count. A planned successor is a publisher command, so it can be
the origin of the next lineage only as the chain derives it (`Prior.origin`),
never by looking its id up.

## 4. Evidence

`python3 -m agent_bus.goal run-checks` resolves the bound wave from live state,
runs each planned `argv` in a checkout of the result head, records the head
`git rev-parse HEAD` reports and every exit code (a check that cannot start is
127), and writes the evidence file the publisher takes with
`--validation-file`. The first durable review fixes that evidence, so a rerun
never re-judges the checks. Readers re-judge the evidence recorded in `V`, so a
`V`/`K` that records an ACCEPT over a red check is not a link.

## 5. Validation performed

`tests/refoundation/test_agent_bus_goal.py`, named by the unit's validation
order:

| control | tests | rig shown red |
| --- | --- | --- |
| V1 selftest green, one required check red | refused, nothing written; no evidence refused; recorded red ACCEPT is not a link; rerun keeps durable evidence | `Evidence.red` blinded → accepted |
| V2 checks on another head | refused; another plan, digest, wave, missing, reordered or extra check refused; runner records the measured head | head check bypassed → accepted |
| V3 no other edge source | model has no successor field; Worker `next` refused; Worker notes, queued `mtj-task` prose and a Captain-looking remark change nothing; unplanned task and wider command bind nothing; forged successor task, scope or wave and forged `K` `a` refused | task guard, exact-command guard, successor role check each disabled → through |
| V4 nonterminal ACCEPT continues | h→result, a→planned task, exact planned command posted by the publisher, no human K; repair then terminal ACCEPT on the successor; crash after each of 4 writes resumes to one successor; authority moved after commit posts none | — |
| V5 terminal ACCEPT | h→result, a=0, GOAL_COMPLETE, nothing pending | — |
| V6 C00-next edge fixture | continues to the C00 fixture wave and task; no check or compiler command executed; every call was GitHub | — |
| V7 policy from the plan | budgets 0/1/2 give C / R,C / R,R,C; unbound, 8 malformed shapes, prose-first, loop, stranger or publisher plan, edited plan, missing or later decision all fail closed to CAPTAIN | defaulted budget → R; invented binding → R |
| V8 R4 controls | the R4 suites run in the same selftest | the R4 rigs, unchanged in intent |

R4 fixtures now bind the R4 wave to a one-wave plan, so every R4 ACCEPT test runs
through the plan and the evidence gate. Workflow-simulation tests that exercised
revalidation codes via ACCEPT now use REPAIR, because the workflow as it stands
cannot ACCEPT (below).

**Selftest.** `python3 -m agent_bus selftest`: 390 tests, 388 pass. The two
failures predate R4 and are unchanged: both assert that
`~/Library/LaunchAgents/com.mtjawnny.agent-bus.plist` does not exist, and the
armed local Worker installed it on this machine.

**Live, read-only.** `python3 -m agent_bus --trusted MTJawnny --pr 76 authority`
still resolves checkpoint 5827051128, task 5821223577, head `58c8345c…`, with no
refused candidates and no lookalikes. `workflow_policy` passes on the unchanged
workflow.

## 6. Open, and needing a decision

- **The workflow does not run the checks yet.** Its evidence job still runs only
  the bus selftest and passes no `--validation-file`, so an ACCEPT through it is
  refused (`test_the_workflow_as_it_stands_cannot_accept`). Wiring
  `agent_bus.goal run-checks` into the evidence job needs the workflow file,
  which is outside AC1's allowlist.
- **No goal plan exists on Issue #1.** Autonomy starts only when the Captain
  posts one and the Manager commands a planned wave bound to it. The C00 edge is
  tested as a fixture only.
- **A plan is immutable.** Editing a plan comment unbinds it. Every publisher
  `K` derived from it then fails re-derivation and is reported as refused, and
  authority falls back to the last valid link. A change of plan is a new plan
  comment and a new command.
- **"Captain-rooted" is checked as far as identity allows.** The plan and the
  decision it names must be earlier, trusted Issue #1 comments. The Captain and
  the Manager post as the same login, so which of them wrote a plan is not
  mechanically distinguishable.
- **Budget scope.** `repair_budget` is per planned wave, not per goal.
- **Refuse, not override.** An ACCEPT over red or mismatched evidence is refused
  with no write, as a red selftest already was. The message stays at the head of
  the queue until a REPAIR or CAPTAIN decision is published for it.
