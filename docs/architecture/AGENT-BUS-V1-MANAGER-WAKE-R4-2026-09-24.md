# Agent Bus v1 — R4 autonomous publisher (GitHub Actions + Codex)

Status: **CANDIDATE, NOT DEPLOYED.** This is the evidence record for wave
`INFRA.AGENT-BUS-V1.MANAGER-WAKE-CODEX-ACTION.R4.R1`:

| field | value |
| --- | --- |
| task comment | 5821223577 |
| checkpoint | 5824275832 |
| accepted head | `58c8345c56667f6776e941f85b79de0766cf22ff` (unchanged) |
| repair of | R3 `53071e55564bbdd372bd77f80259b9d7a2269d6b` |
| verdict | 5821212657 |
| Captain decision | 5821208878 |

It records what was built and measured. It is not authority. The contract is
`refoundation/AGENT-BUS-MANAGER-TRIGGER.md`.

## 1. What exists

| piece | where | commit |
| --- | --- | --- |
| strict ledger reading, publisher role law, transition law, publisher, decision boundary, gate transaction law, static policy | `agent_bus/{ledger,trust,transition,publisher,decision,manager_gate,machine,issue,workflow_policy}.py` | AP1 `e9bb3a4` |
| R3-D1..D7, NC1..NC15 red/green/rig suite | `tests/refoundation/test_agent_bus_publisher.py` | AP1 `e9bb3a4` |
| contract | `refoundation/AGENT-BUS-MANAGER-TRIGGER.md`, `refoundation/AGENT-BUS.md` | AP2 `07ecc4f` |
| workflow candidate, pipeline tests, this record | `.github/workflows/agent-bus-manager-wake.yml`, `tests/refoundation/test_agent_bus_wake_workflow.py` | AP2, this record's commit |

`BUS_REF` is `07ecc4fbd55c055fb9ba3719885f0f11bfc4e7d1`. That commit carries the
AP1 code and the AP2 contract, so a woken model reads the R4 contract, not R3's.

## 2. Trust matrix

| identity | Issue #1 | PR 76 |
| --- | --- | --- |
| trusted speaker (`MTJawnny`, operator-configured) | any checkpoint is a `K` | any bus message its actor may speak |
| `github-actions[bot]` (`trust.PUBLISHER`) | `mtj-verdict/0` and `mtj-checkpoint/2`, **only** in the publisher's exact rendered form. A `K` counts only as the exact next link: it names the `K` before it as `prior_checkpoint`, and it is what `transition` derives from that `K`, the Worker message it binds to, and its `V`. | `MANAGER` `WAVE_REVIEW` with id `mgr-review-<txn>`, and `MANAGER` `WAVE_COMMAND` with id `mgr-repair-<txn>` (or, since R4.R2 AC1, `mgr-next-<txn>`), exactly the successor the live publisher `K` derives. Nothing else (`trust.PUBLISHER_ROLES`). |
| anyone else | reported as an untrusted candidate, never a `K` | reported, never counted as handled |

The bot cannot be declared a speaker (`BUS_TRUST_NOT_CONFIGURED`). Its login is
compared exactly, never case-folded. It can never:
- write a WORKER or CAPTAIN message, an abort, a task, or a Captain decision;
- set `a` to anything but the prior `a`, 0, or (since R4.R2 AC1) the task of the
  bound Captain goal plan's `next` wave.

## 3. Transaction states

Transaction id: `mtx-<cited checkpoint>-<result comment id>`.

| state | durable records | a rerun does |
| --- | --- | --- |
| P0 | none | review, V, K (and the successor, for R), each after a fresh revalidation |
| P1 | review | reads the decision from the review (the model is not asked), then writes V, K… |
| P2 | review, V | writes K… |
| COMMITTED | review, V, K on the chain | REPAIR only: posts the successor, if its `K` is still the live authority. Otherwise it stops with `BUS_TXN_SUPERSEDED`, exit 5. |
| COMPLETE | all | writes nothing; the gate answers `BUS_GATE_ALREADY_HANDLED` |
| LOST | a `K` for this transaction that is not a link | `BUS_TXN_RACE_LOST`, exit 5, nothing more |

Before commit, any failed revalidation is exit 4 and no authority moved. These
are the codes:
- BUS_STALE_AUTHORITY, BUS_GATE_COMMENT_MISMATCH;
- BUS_WAVE_ABORTED, BUS_WAVE_SUPERSEDED, BUS_GATE_QUEUED;
- BUS_BRANCH_TIP_MISMATCH, BUS_TRANSITION_REFUSED, BUS_TXN_CONFLICT.

## 4. Queue and concurrency — the design and why

Three layers, each tested:

1. **Chain compare-and-swap (correctness).** A publisher `K` is law only if its
   `prior_checkpoint` is the `K` immediately before it. Two publishers racing
   from one prior can both post, but only the first GitHub ordered is a link,
   for every reader. Tests: NC11, and `test_rig_D6_NC11` removes it and shows two
   links.
2. **Queue head (ordering).** Only the oldest pending Manager message under a
   `K` is admitted. Aborted and superseded waves are excluded, so they cannot
   starve it. Every other message is `BUS_GATE_QUEUED`. The committing `K` names
   them in `unanswered`, so none is dropped silently.
3. **`concurrency: agent-bus-publisher` on the publish job (efficiency).**
   Writers take turns, so they rarely reach layer 1's lost-race stop.

A global concurrency group alone was rejected. GitHub keeps one running and one
pending run per group and cancels older pending ones. So on its own it can
drop a run, and it does nothing about a second admitted message that is valid
under a stale reading. Layers 1 and 2 hold even when the group is absent (NC11
passes with the queue check removed).

What this does not do: a message refused as `BUS_GATE_QUEUED` is not re-woken
automatically. It is named in the next `K`'s `unanswered` list, and after that
`K` it cites a stale checkpoint. Answering it is Manager or Captain work.

## 5. Workflow shape

| job | model | secret | token | runs when |
| --- | --- | --- | --- | --- |
| gate | no | no | contents, issues, pull-requests: read | the PR 76 / MTJawnny / `mtj-bus` prefilter |
| evidence | no | no | contents, issues, pull-requests: read | `wake == 'true'` |
| manager | Codex | `OPENAI_API_KEY`, as the action input only | read only | `wake == 'true' && mode == 'review'` |
| publish | no | no | contents: read, issues: write | wake, not cancelled, evidence succeeded, and resume or manager succeeded |

- **Top-level permissions** are `{}`. No job holds `contents`, `actions`,
  `pull-requests`, `deployments`, `packages`, `id-token`, `checks`, `statuses`
  or `security-events` write. So nothing can push, move a ref, merge, deploy or
  manage secrets.
- **The model's answer** is validated against `python3 -m agent_bus.decision
  --schema`, the same constants the publisher parses with.
- **The tested head** is what `git rev-parse HEAD` reports in the evidence
  job's checkout of the claimed head.
- **Recovery.** The workflow-level group is per comment, so a rerun of one
  comment waits for the run before it. A failed or dead run is finished either
  by "Re-run all jobs" (the gate answers `mode=resume`, and the model is
  skipped) or by "Re-run failed jobs" (only publish runs again). Both are tested.

Pins, re-resolved live on 2026-09-24:
- `openai/codex-action` tag `v1.12`: annotated tag object `cac08775…`, which
  peels to `86365089eb2b84e0a8fb0717b304f8bdcb13b20e`. The commit is verified.
  Every input used (`openai-api-key`, `prompt-file`, `output-schema-file`,
  `permission-profile`, `safety-strategy`, `allow-users`) and the
  `final-message` output exist in its `action.yml`.
- `actions/checkout` tag `v7.0.1`: `3d3c42e5aac5ba805825da76410c181273ba90b1`,
  verified.

## 6. Validation performed

**R3 defects and task controls.**
`tests/refoundation/test_agent_bus_publisher.py`, 70 tests. The numbering binds:
- R3-D1..D7 are verdict 5821212657's defects 1..7;
- NC1..NC15 are task 5821223577's `required_negative_controls`, in order;
- per verdict 5824273947.

Each is shown red against R3 logic frozen in the test, green against the repair,
and red again with its protection rigged weak.

Controls with no R3 weakness are shown green only:
- **NC3.** R3 refused every bot record, legitimate ones included. That was
  defect D3.
- **NC10.** R3 never duplicated a record, only because it never resumed. That
  was D4.
- **NC12.** R3's fence handling was already exact.

**R3's own code, executed.** R3's modules and the two inline scripts of its
workflow were loaded straight from git objects at `53071e5`, with nothing
written to disk, and run against the defect worlds with GitHub faked in memory.
Every result reproduced the defect:

| check | R3 outcome |
| --- | --- |
| D1 | the any-author step answered "answered by comments [1]" for a stranger's review |
| D2, NC4, NC6 | a model K moving `h` to an arbitrary sha and `a` to 424242 was posted |
| D3 | R3's resolver kept the prior `K` after a bot `K`, reporting the bot as untrusted |
| D4, NC9 | after a crash following the review, the rerun was "REFUSED … already answered" |
| D5, NC7 | an abort plus an edited result, and a deleted result, were posted over |
| NC8 | authority moved after the first write, and V and K were still posted |
| D6, NC11 | two admitted results produced two bot `K`s, `h` `cccccccc` and `eeeeeeee` |
| D7, NC13 | a `K` quoted inside a V was selected, and a nested `a: 999` was read |
| NC15 | R3's gate woke on a result for an aborted wave |
| NC14 | no R3 test read `agent-bus-manager-wake.yml`, so no weakening could turn anything red |

**The pipeline.** `tests/refoundation/test_agent_bus_wake_workflow.py`, 16
tests. Static: the generic policy plus the R4 structure, with 18 rigs, each red.
Dynamic: every job simulated through the entry points the YAML runs, against a
stateful fake GitHub:
- a normal REPAIR;
- competing admitted messages;
- a crash after each of the four writes, with both kinds of rerun;
- abort, edit or delete between gate and publish;
- a moved branch;
- authority moved before the commit, and after it;
- a red or different tested head;
- a record-shaped model answer;
- CAPTAIN.

**Live, read-only, against Issue #1 and PR 76:**
- `python3 -m agent_bus --trusted MTJawnny --pr 76 authority` gives
  checkpoint 5824275832, task 5821223577, head `58c8345c…`, with no refused
  candidates and no lookalikes.
- The gate refused:
  - the R4.R1 command (`BUS_GATE_NOT_FOR_MANAGER`);
  - both R4 Worker results (`BUS_STALE_AUTHORITY`);
  - the live `K` delivered as an Issue #1 event (`BUS_GATE_WRONG_SURFACE`).
- `publisher result-head` on comment 5821315792 returned `53071e55…`.
- `workflow_policy` passes on the candidate.

**Selftest.** `python3 -m agent_bus selftest` ran 353 tests; 351 pass. The two
failures predate R4 and are unchanged. Both assert that
`~/Library/LaunchAgents/com.mtjawnny.agent-bus.plist` does not exist, and the
armed local Worker installed it on this machine.

**Not done:**
- no OpenAI call;
- no secret created;
- no workflow run;
- no write to Issue #1 or PR 76 by any publisher code;
- no change to `main`.

## 7. Decisions this candidate makes that need ratifying

Superseded in part by R4.R2 AC1
(`docs/architecture/AGENT-BUS-V1-MANAGER-WAKE-R4R2-AC1-2026-09-25.md`): the repair
budget and the ACCEPT successor now come from the Captain goal plan, and ACCEPT
needs the plan's checks. The bullets below record R4.R1 as built.

- `MAX_REPAIR_ROUNDS = 3`. After three consecutive autonomous repairs of one
  origin command, REPAIR is recorded as CAPTAIN.
- A Worker `CAPTAIN_REQUIRED` can be answered only CAPTAIN. It carries no head,
  so no ACCEPT or REPAIR can be bound to one. A clerical correction like verdict
  5824273947 still needs a human.
- ACCEPT sets `a = 0`. Selecting the next task (for example the C00 backlog)
  stays a human `K`.
- Recovery is manual: re-run the failed run. Nothing retries on its own.

## 8. Known limits

- A write that lands during the moment between the last revalidation and the
  POST is not seen by that revalidation. The chain (commit point) and the next
  rerun (prefix records) catch it. That window is inherent without
  compare-and-swap on GitHub comments.
- Anything that can post as `github-actions[bot]` — any workflow here with
  `issues: write` — could post a record with a transaction's exact ids but other
  content. Such records are:
  - ignored when they are not in the publisher's form;
  - `BUS_TXN_CONFLICT` (fail closed, reported) when they are.

  Only reviewed workflows in this repository hold that identity.

## 9. One-time activation steps (none performed)

In order, each by the Captain unless stated:

1. **Manager acceptance** of this candidate at its head, by independent review.
2. **Create the repository secret** `OPENAI_API_KEY` (Settings → Secrets and
   variables → Actions). No repository code touches it.
3. **Confirm the default `GITHUB_TOKEN` can write comments.** Settings → Actions
   → General → Workflow permissions may stay "Read repository contents". The
   workflow asks for `issues: write` itself, and a job-level `permissions` block
   can raise the default.
4. **Place the exact reviewed blob on `main`.** Copy
   `.github/workflows/agent-bus-manager-wake.yml` at the accepted head
   byte-for-byte, as a Captain-authorized change. Check that its sha-256 equals
   the reviewed blob's. Nothing else on `main` is required: the workflow checks
   out its own bus code at `BUS_REF`.
5. **Keep the local Worker running with `--pr 76`.** A publisher `K` is judged
   against PR 76, so a Worker reading Issue #1 alone halts loudly
   (`BUS_AUTHORITY_UNRESOLVED`) rather than read an older `K`.
6. **Watch the first run.** The Actions page shows:
   - the gate's JSON decision, including `mode` and `ignored`;
   - the publisher's JSON report: writes, records, exit.

   A failed publish job is finished by re-running it.

To withdraw it, delete the workflow file from `main`. Every record already
written stays valid under the same law, and the Manager side can be done by hand
(contract section 7).
