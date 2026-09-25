"""R4 AP2: the Manager wake workflow, statically and as a pipeline.

Two halves.

**Static.** `.github/workflows/agent-bus-manager-wake.yml` is read by the
stdlib reader in `agent_bus.workflow_policy` and must obey two sets of rules:
- the generic policy: permissions, secret placement, pins, trigger;
- the R4 structure below: which job may run the model, what gates the
  publisher, and that no step judges "answered" by itself.

Every rule has a rig: one careless edit, shown red.

**Dynamic.** The workflow's jobs are simulated through the SAME entry points the
YAML runs:
- `python3 -m agent_bus.manager_gate` writes GITHUB_OUTPUT lines;
- `agent_bus.publisher result-head` feeds the evidence job;
- the model is a stub returning a decision;
- the publish job's argv is built exactly as its `run:` block builds it.

These are run against a stateful fake GitHub through each hazard the task names:
partial writes and reruns, competing admitted messages, abort, edit and delete,
a stale branch tip, and authority movement. No network, no model, no OpenAI.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.refoundation.test_agent_bus_publisher import (
    ACCEPT, AUTHOR, BRANCH, CAPTAIN, H0, H1, H_OTHER, K0, PR, REPAIR, REPO, RESULT_COMMENT,
    TASK, WAVE, Crash, FakeGitHub, abort_of, authority, body_of, green, human_k, publisher_k,
    result, two_results, worker_view,
)

from agent_bus import decision as D
from agent_bus import errors as E
from agent_bus import ledger as L
from agent_bus import manager_gate as G
from agent_bus import publisher as P
from agent_bus import transition as X
from agent_bus import workflow_policy as W

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "agent-bus-manager-wake.yml"
TRIGGER_DOC = ROOT / "refoundation" / "AGENT-BUS-MANAGER-TRIGGER.md"

PINS = {
    "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1",  # v7.0.1
    "openai/codex-action": "86365089eb2b84e0a8fb0717b304f8bdcb13b20e",  # v1.12
}
PREFILTER = ("(github.event.issue.pull_request && github.event.issue.number == 76 && "
             "github.event.comment.user.login == 'MTJawnny' && "
             "contains(github.event.comment.body, '```mtj-bus')) || "
             "(github.event_name == 'workflow_run' && "
             "github.event.workflow_run.event == 'issue_comment' && "
             "github.event.workflow_run.conclusion != 'success')")
MODEL_IF = ("github.event_name == 'issue_comment' && needs.gate.outputs.wake == 'true' && "
            "needs.gate.outputs.mode == 'review'")


def text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def structural_problems(source: str) -> list[str]:
    """The R4 shape, beyond the generic policy. Empty means the file obeys."""
    out: list[str] = []
    w = W.load(source)
    jobs = w.get("jobs", {})
    if list(jobs) != ["gate", "evidence", "manager", "publish"]:
        return [f"jobs are {list(jobs)}"]
    gate, evidence, manager, publish = (jobs[k] for k in ("gate", "evidence", "manager",
                                                          "publish"))
    if not re.fullmatch(r"[0-9a-f]{40}", str(w.get("env", {}).get("BUS_REF", ""))):
        out.append("BUS_REF is not a commit")
    if gate.get("if") != PREFILTER:
        out.append("the PR 76 prefilter changed")
    runs = {name: [s.get("run", "") for s in job.get("steps", [])] for name, job in jobs.items()}
    if not any("python3 -m agent_bus.manager_gate" in r for r in runs["gate"]):
        out.append("the gate job does not run agent_bus.manager_gate")
    for name, scripts in runs.items():
        for script in scripts:
            if "${{" in script:
                out.append(f"job {name} splices an expression into run:")
            if "WAVE_REVIEW" in script or "parse_comment" in script:
                out.append(f"job {name} judges bus messages in an inline script")
    for key in ("wake", "mode", "comment_id", "message_id", "digest"):
        if key not in gate.get("outputs", {}):
            out.append(f"gate does not export {key}")
    if "git rev-parse HEAD" not in "".join(runs["evidence"]):
        out.append("the tested head is not measured by git")
    if "python3 -m agent_bus.goal run-checks" not in "".join(runs["evidence"]) \
            or "validation" not in evidence.get("outputs", {}):
        out.append("the goal plan's required checks are not run and exported")
    if manager.get("if") != MODEL_IF:
        out.append("the model can run outside a review-mode comment event")
    codex = manager.get("steps", [])[-1] if manager.get("steps") else {}
    if str(codex.get("uses", "")).split("@")[0] != "openai/codex-action":
        out.append("Codex is not the last step of the model job")
    elif (codex.get("with") or {}).get("allow-users") != "MTJawnny" \
            or (codex.get("with") or {}).get("output-schema-file") != \
            ".agent-bus-context/decision.schema.json":
        out.append("Codex allow-users or its decision schema changed")
    if "python3 -m agent_bus.decision --schema" not in "".join(runs["manager"]):
        out.append("the model's schema is not the parser's schema")
    if re.search(r"wave_review|issue_1", "".join(runs["manager"])):
        out.append("the model is asked for records, not a decision")
    cond = str(publish.get("if", ""))
    for needed in ("needs.gate.outputs.wake == 'true'", "!cancelled()",
                   "needs.evidence.result == 'success'",
                   "(needs.gate.outputs.mode != 'review' || needs.manager.result == 'success')"):
        if needed not in cond:
            out.append(f"publish does not require {needed}")
    if "always()" in cond:
        out.append("publish runs always()")
    if publish.get("concurrency") != {"group": "agent-bus-publisher",
                                      "cancel-in-progress": "false"}:
        out.append("publishers are not serialized")
    script = "".join(runs["publish"])
    if "python3 -m agent_bus.publisher" not in script or 'if [ "$MODE" = "review" ]' not in script:
        out.append("publish does not run the deterministic publisher by mode")
    if "--validation-file" not in script:
        out.append("publish does not hand the checks' evidence to the publisher")
    if "secrets." in json.dumps(publish) or "OPENAI" in json.dumps(publish):
        out.append("the publisher holds a model credential")
    for name, job in jobs.items():
        for step in job.get("steps", []):
            uses = step.get("uses")
            if uses and PINS.get(uses.split("@")[0]) != uses.split("@")[1]:
                out.append(f"job {name} uses {uses}, not the verified pin")
    return out


# ============================================================ static

class TestTheWorkflowStatically(unittest.TestCase):
    def test_it_obeys_the_generic_policy_and_the_r4_structure(self):
        self.assertEqual(W.check_text(text()), [])
        self.assertEqual(structural_problems(text()), [])

    def test_every_action_is_pinned_to_the_verified_commit(self):
        uses = re.findall(r"uses: (\S+)", text())
        self.assertTrue(uses)
        for ref in uses:
            name, sha = ref.split("@")
            self.assertEqual(PINS[name], sha)

    def test_the_model_job_cannot_write_and_the_publisher_holds_no_model_secret(self):
        jobs = W.load(text())["jobs"]
        self.assertEqual(set(jobs["manager"]["permissions"].values()), {"read"})
        self.assertEqual(jobs["publish"]["permissions"], {"contents": "read", "issues": "write"})
        secret_jobs = [n for n, j in jobs.items() if "secrets." in json.dumps(j)]
        self.assertEqual(secret_jobs, ["manager"])

    def test_no_job_can_push_merge_move_a_branch_deploy_or_manage_secrets(self):
        for name, job in W.load(text())["jobs"].items():
            with self.subTest(job=name):
                writes = {k for k, v in job["permissions"].items() if v == "write"}
                self.assertLessEqual(writes, {"issues"})
        code = "\n".join(line for line in text().splitlines()
                         if not line.lstrip().startswith("#"))
        for word in ("git push", "gh pr merge", "gh secret", "git/refs", "deployments",
                     "contents: write", "workflow_dispatch", "pull_request_target"):
            with self.subTest(forbidden=word):
                self.assertNotIn(word, code)

    def test_bus_ref_is_a_commit_that_carries_the_r4_contract(self):
        ref = W.load(text())["env"]["BUS_REF"]
        shown = subprocess.run(["git", "-C", str(ROOT), "show",
                                f"{ref}:refoundation/AGENT-BUS-MANAGER-TRIGGER.md"],
                               capture_output=True, text=True)
        if shown.returncode != 0:
            self.skipTest(f"commit {ref} is not in this clone (shallow checkout)")
        self.assertIn("Decide once; the records are derived", shown.stdout)
        for module in ("agent_bus/publisher.py", "agent_bus/decision.py"):
            with self.subTest(module=module):
                self.assertEqual(subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e",
                                                 f"{ref}:{module}"]).returncode, 0)

    def test_the_contract_names_only_real_codes_and_the_real_repair_budget(self):
        doc = TRIGGER_DOC.read_text(encoding="utf-8")
        self.assertEqual(sorted(set(re.findall(r"\bBUS_[A-Z_]+\b", doc)) - E.CODES), [])
        # The budget is the Captain goal plan's, not a constant in Worker code.
        self.assertIn("After the goal plan's `repair_budget` of consecutive autonomous", doc)
        self.assertFalse(hasattr(X, "MAX_REPAIR_ROUNDS"))
        self.assertIn("python3 -m agent_bus.decision --schema", doc)

    def test_the_schema_handed_to_the_model_is_the_parsers(self):
        schema = D.json_schema()
        self.assertEqual(schema["required"], list(D.KEYS))
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["properties"]["verdict"]["enum"], list(D.VERDICTS))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(D.main(["--schema"]), 0)
        self.assertEqual(json.loads(out.getvalue()), schema)


# Each: (anchor in the workflow, careless edit). Every one must turn a check red.
RIGS = {
    "model_runs_on_resume": ("needs.gate.outputs.wake == 'true' && needs.gate.outputs.mode == 'review'",
                             "needs.gate.outputs.wake == 'true'"),
    "publish_always": ("needs.gate.outputs.wake == 'true' &&\n      !cancelled()",
                       "always() &&\n      !cancelled()"),
    "publish_without_evidence": ("      needs.evidence.result == 'success' &&\n", ""),
    "publishers_not_serialized": ("      group: agent-bus-publisher\n", "      group: x-${{ github.run_id }}\n"),
    "prefilter_any_pr": ("github.event.issue.number == 76 &&", ""),
    "gate_removed": ("python3 -m agent_bus.manager_gate", "true"),
    "inline_any_author_check": ("      - name: Deterministic pre-gate (no model)",
                                "      - name: answered\n        run: python3 -c 'WAVE_REVIEW'\n"
                                "      - name: Deterministic pre-gate (no model)"),
    "body_in_run": ('echo "head=$head" >> "$GITHUB_OUTPUT"',
                    'echo "${{ github.event.comment.body }}"'),
    "head_not_measured": ('run: echo "head=$(git rev-parse HEAD)" >> "$GITHUB_OUTPUT"',
                          'run: echo "head=$HEAD" >> "$GITHUB_OUTPUT"'),
    "model_asked_for_records": ("Then answer with ONE decision", "Then answer wave_review"),
    "schema_not_the_parsers": ("python3 -m agent_bus.decision --schema > ",
                               "echo '{}' > "),
    "codex_allows_anyone": ("allow-users: MTJawnny", 'allow-users: "*"'),
    "older_codex_pin": ("86365089eb2b84e0a8fb0717b304f8bdcb13b20e",
                        "0000000000000000000000000000000000000000"),
    "bus_ref_a_branch": ("BUS_REF: 07ecc4fbd55c055fb9ba3719885f0f11bfc4e7d1",
                         "BUS_REF: infra/agent-bus-v1-bootstrap-2026-09-23"),
    "publisher_gets_the_model_key": ("          GH_TOKEN: ${{ github.token }}\n          MODE:",
                                     "          GH_TOKEN: ${{ github.token }}\n          K: "
                                     "${{ secrets.OPENAI_API_KEY }}\n          MODE:"),
    "model_job_writes": ("    permissions:\n      contents: read\n      issues: read\n"
                         "      pull-requests: read\n    outputs:\n      final_message",
                         "    permissions:\n      contents: read\n      issues: write\n"
                         "      pull-requests: read\n    outputs:\n      final_message"),
    "publish_gets_contents_write": ("      contents: read\n      issues: write",
                                    "      contents: write\n      issues: write"),
    "decision_ignored_by_mode": ('if [ "$MODE" = "review" ]', 'if [ "$MODE" = "never" ]'),
}


class TestEveryStaticRuleIsSeenToFail(unittest.TestCase):
    def test_each_rig_is_red(self):
        source = text()
        for name, (old, new) in RIGS.items():
            with self.subTest(rig=name):
                self.assertIn(old, source)
                rigged = source.replace(old, new, 1)
                self.assertTrue(W.check_text(rigged) + structural_problems(rigged), name)


# ============================================================ dynamic

class Run:
    def __init__(self):
        self.gate: dict = {}
        self.model_calls = 0
        self.publish_exit: int | None = None
        self.report: dict = {}


def _outputs(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return dict(line.split("=", 1) for line in handle.read().splitlines() if line)


def run_workflow(fake: FakeGitHub, comment_id: int = RESULT_COMMENT, model=ACCEPT,
                 selftest: int = 0, before_publish=None, rerun_outputs: Run | None = None,
                 tested_head: str | None = None, validation=None) -> Run:
    """One workflow run, job by job, through the real entry points.

    `rerun_outputs` replays "Re-run failed jobs": GitHub keeps the outputs of the
    jobs that succeeded and runs only publish again.

    `validation` is `agent_bus.goal run-checks` evidence handed to publish as
    `--validation-file`. The workflow at this candidate does not run that step
    yet, so every run that models it as it stands passes None -- and cannot
    ACCEPT (`test_the_workflow_as_it_stands_cannot_accept`).
    """
    run = Run()
    with tempfile.TemporaryDirectory() as tmp:
        if rerun_outputs is None:
            event = {"action": "created", "repository": {"full_name": REPO},
                     "issue": {"number": PR, "pull_request": {"url": "x"}},
                     "comment": {"id": comment_id, "body": body_of(fake, comment_id),
                                 "user": {"login": AUTHOR}}}
            path, out = os.path.join(tmp, "event.json"), os.path.join(tmp, "gate.out")
            with open(path, "w") as handle:
                json.dump(event, handle)
            with contextlib.redirect_stdout(io.StringIO()):
                G.main(["--event", path, "--event-name", "issue_comment", "--repo", REPO,
                        "--pr", str(PR), "--trusted-author", AUTHOR, "--github-output", out],
                       run=fake)
            run.gate = _outputs(out)
            if run.gate.get("wake") != "true":
                return run
            # evidence
            with contextlib.redirect_stdout(io.StringIO()) as head_out:
                P.main(["--repo", REPO, "--pr", str(PR), "--trusted-author", AUTHOR,
                        "result-head", "--comment-id", run.gate["comment_id"]], run=fake)
            head = head_out.getvalue().strip()
            run.gate["measured_head"] = tested_head or head
            # manager
            run.gate["final_message"] = ""
            if run.gate["mode"] == "review":
                run.model_calls = 1
                run.gate["final_message"] = model if isinstance(model, str) \
                    else json.dumps(model.as_dict())
        else:
            run.gate, run.model_calls = dict(rerun_outputs.gate), 0
        if before_publish:
            before_publish(fake)
        # publish: the argv its run: block builds
        argv = ["--repo", REPO, "--pr", str(PR), "--trusted-author", AUTHOR, "publish",
                "--comment-id", run.gate["comment_id"], "--digest", run.gate["digest"]]
        if run.gate["mode"] == "review":
            decision = os.path.join(tmp, "decision.json")
            with open(decision, "w") as handle:
                handle.write(run.gate["final_message"])
            argv += ["--decision-file", decision]
        if run.gate["measured_head"]:
            argv += ["--measured-head", run.gate["measured_head"]]
        argv += ["--selftest-exit", str(selftest)]
        if validation is not None:
            evidence = os.path.join(tmp, "validation.json")
            with open(evidence, "w") as handle:
                json.dump(validation.as_dict(), handle)
            argv += ["--validation-file", evidence]
        with contextlib.redirect_stdout(io.StringIO()) as out:
            run.publish_exit = P.main(argv, run=fake)
        run.report = json.loads(out.getvalue())
    return run


class TestThePipeline(unittest.TestCase):
    def test_a_result_is_reviewed_once_and_published_as_one_transaction(self):
        fake = FakeGitHub()
        run = run_workflow(fake, model=REPAIR)
        self.assertEqual((run.gate["mode"], run.model_calls, run.publish_exit), ("review", 1, 0))
        self.assertEqual(fake.kinds(), {"WAVE_REVIEW": 1, "V": 1, "K": 1, "WAVE_COMMAND": 1})
        self.assertEqual(worker_view(fake).state.pending_for("WORKER")[0].wave, WAVE + ".AR1")
        again = run_workflow(fake, model=ACCEPT)  # the same comment, run again
        self.assertEqual((again.gate["wake"], again.gate["code"]),
                         ("false", E.GATE_ALREADY_HANDLED))
        self.assertEqual(again.model_calls, 0)

    def test_competing_admitted_messages_one_transaction_the_other_named_unanswered(self):
        fake = two_results()
        second = run_workflow(fake, RESULT_COMMENT + 1)  # its event arrives first
        self.assertEqual((second.gate["wake"], second.gate["code"]), ("false", E.GATE_QUEUED))
        self.assertEqual(second.model_calls, 0)
        first = run_workflow(fake, model=REPAIR)
        self.assertEqual(first.publish_exit, 0)
        k = L.parse_record(publisher_k(fake)[0]["body"]).fields
        self.assertEqual(json.loads(k["unanswered"]), [RESULT_COMMENT + 1])
        self.assertEqual(len([c for c in authority(fake).chain if c != K0]), 1)

    def test_a_run_that_dies_after_each_write_is_finished_by_a_rerun(self):
        for after in (1, 2, 3, 4):
            for how in ("re-run all jobs", "re-run failed jobs"):
                with self.subTest(crash_after=after, rerun=how):
                    fake = FakeGitHub()
                    fake.crash_after = after
                    first = Run()
                    with self.assertRaises(Crash):
                        first = run_workflow(fake, model=REPAIR)
                    if how == "re-run all jobs":
                        again = run_workflow(fake, model=CAPTAIN)  # a new model would disagree
                        if after == 4:
                            self.assertEqual(again.gate["code"], E.GATE_ALREADY_HANDLED)
                        else:
                            self.assertEqual((again.gate["mode"], again.model_calls), ("resume", 0))
                    else:
                        replay = run_workflow(FakeGitHub(), model=REPAIR)  # same outputs shape
                        replay.gate["digest"] = X.digest(body_of(fake, RESULT_COMMENT))
                        again = run_workflow(fake, rerun_outputs=replay)
                        self.assertEqual(again.publish_exit, 0, again.report)
                    self.assertEqual(fake.kinds(),
                                     {"WAVE_REVIEW": 1, "V": 1, "K": 1, "WAVE_COMMAND": 1})
                    self.assertEqual(authority(fake).authority.publisher["verdict"], "R")

    def test_changes_between_the_gate_and_the_publisher_are_refused(self):
        hazards = {
            "aborted": (lambda f: f.add(PR, abort_of()), E.WAVE_ABORTED),
            "edited": (lambda f: f.edit(RESULT_COMMENT, result(note="edited")),
                       E.GATE_COMMENT_MISMATCH),
            "deleted": (lambda f: f.delete(RESULT_COMMENT), E.GATE_COMMENT_MISMATCH),
            "branch_moved": (lambda f: f.tips.__setitem__(BRANCH, H_OTHER),
                             E.BRANCH_TIP_MISMATCH),
        }
        for name, (change, code) in hazards.items():
            with self.subTest(hazard=name):
                fake = FakeGitHub()
                run = run_workflow(fake, model=REPAIR, before_publish=change)
                self.assertEqual((run.publish_exit, run.report["code"]), (P.EXIT_REFUSED, code))
                self.assertEqual(fake.writes, [])

    def test_authority_moved_before_publish_disposes_instead_of_orphaning(self):
        # AC2: the message was valid under K0; a human K replaced K0 without
        # answering it. No review, V or K is written -- only its disposition.
        fake = FakeGitHub()
        run = run_workflow(fake, model=REPAIR,
                           before_publish=lambda f: f.add(1, human_k(H0, 111)))
        self.assertEqual(run.publish_exit, 0, run.report)
        self.assertEqual([w["record"] for w in run.report["writes"]], ["DISPOSITION"])
        d = L.parse_record(fake.issue[-1]["body"]).fields
        self.assertEqual((d["message_comment"], d["deciding_transaction"]),
                         (str(RESULT_COMMENT), X.NONE))

    def test_a_red_or_different_tested_head_cannot_be_accepted(self):
        red = run_workflow(FakeGitHub(), model=ACCEPT, selftest=1, validation=green())
        self.assertEqual(red.report["code"], E.TRANSITION_REFUSED)
        self.assertIn("selftest", red.report["detail"])
        other = run_workflow(FakeGitHub(), model=ACCEPT, tested_head=H_OTHER,
                             validation=green())
        self.assertEqual(other.report["code"], E.TRANSITION_REFUSED)
        self.assertIn("independently tested head", other.report["detail"])

    def test_the_workflow_as_it_stands_cannot_accept(self):
        # No `--validation-file`: ACCEPT fails closed and nothing is written.
        fake = FakeGitHub()
        run = run_workflow(fake, model=ACCEPT)
        self.assertEqual((run.publish_exit, run.report["code"]),
                         (P.EXIT_REFUSED, E.TRANSITION_REFUSED))
        self.assertIn("required checks", run.report["detail"])
        self.assertEqual(fake.writes, [])
        # The same run with the checks runner's evidence accepts, through the CLI.
        fake = FakeGitHub()
        run = run_workflow(fake, model=ACCEPT, validation=green())
        self.assertEqual(run.publish_exit, 0, run.report)
        self.assertEqual(authority(fake).authority.accepted_head, H1)

    def test_authority_moving_after_the_commit_stops_the_successor(self):
        fake = FakeGitHub()
        fake.crash_after = 3
        with self.assertRaises(Crash):
            run_workflow(fake, model=REPAIR)
        fake.add(1, human_k(H0, 111))
        again = run_workflow(fake)
        # The message now cites a checkpoint two links back: nothing to resume.
        self.assertEqual(again.gate["wake"], "false")
        replay = run_workflow(FakeGitHub(), model=REPAIR)
        replay.gate["digest"] = X.digest(body_of(fake, RESULT_COMMENT))
        rerun = run_workflow(fake, rerun_outputs=replay)
        self.assertEqual((rerun.publish_exit, rerun.report["code"]),
                         (P.EXIT_AFTER_COMMIT, E.TXN_SUPERSEDED))
        self.assertEqual(fake.kinds()["WAVE_COMMAND"], 0)

    def test_a_record_shaped_model_answer_publishes_nothing(self):
        fake = FakeGitHub()
        answer = json.dumps({"wave_review": "```mtj-bus\n{}\n```", "issue_1": [
            "```yaml\nschema: mtj-verdict/0\n```", "```yaml\nschema: mtj-checkpoint/2\n```"]})
        run = run_workflow(fake, model=answer)
        self.assertEqual(run.publish_exit, P.EXIT_BAD_INPUT)
        self.assertEqual(fake.writes, [])

    def test_the_captain_verdict_stops_autonomy(self):
        fake = FakeGitHub()
        self.assertEqual(run_workflow(fake, model=CAPTAIN).publish_exit, 0)
        self.assertEqual(authority(fake).authority.task, 0)
        self.assertEqual(worker_view(fake).state.pending_for("WORKER"), [])
        self.assertEqual(authority(fake).authority.accepted_head, H0)
        self.assertNotEqual(authority(fake).authority.task, TASK)
        self.assertNotEqual(H1, H0)


if __name__ == "__main__":
    unittest.main()
