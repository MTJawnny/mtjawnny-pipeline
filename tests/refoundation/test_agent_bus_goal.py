"""R4.R2 AC1: Captain-rooted goal continuation, and task-specific validation.

The numbering binds to wave INFRA.AGENT-BUS-V1.MANAGER-WAKE-CODEX-ACTION.R4.R2.AR1,
unit AC1, `validation`, in order:

* `V1` negative: bus selftest green, one task-specific required check red -> no ACCEPT.
* `V2` negative: task-specific checks run on a different head -> no ACCEPT.
* `V3` negative: model output, a Worker result, queued task prose, or an unplanned
  task id cannot create or alter a successor.
* `V4` positive: a nonterminal ACCEPT advances h, selects the exact pre-authorized
  next task, and derives its exact WAVE_COMMAND without a human K.
* `V5` positive: a terminal ACCEPT advances h and selects no task.
* `V6` positive: a fixture of the already-authorized C00-next edge continues
  automatically, and no compiler work is executed.
* `V7` repair exhaustion is read from the Captain goal plan; missing or malformed
  policy fails closed to CAPTAIN.
* `V8` every R4 trust, parser, transition and idempotency control stays green: the
  R4 suites run unchanged in intent in the same selftest (`test_agent_bus_publisher`,
  `test_agent_bus_wake_workflow`, `test_agent_bus_manager_wake`).

Every guard a negative control relies on is also rigged weak in
`TestRiggedGoalProtections` and shown to let its control through, so no guard
here is trusted without having been seen to fail. No network, model or compiler.
"""

from __future__ import annotations

import contextlib
import dataclasses
import io
import json
import os
import subprocess
import tempfile
import unittest
from unittest import mock

from tests.refoundation.test_agent_bus_publisher import (
    ACCEPT, AUTHOR, BRANCH, BUDGET, CHECKS, CMD_COMMENT, CMD_ID,
    DECISION_BODY, H0, H1, H_OTHER, K0, PLAN_BODY, PLAN_COMMENT, PR, REPAIR,
    REPO, RESULT_COMMENT, TARGET, TASK, WAVE, Crash, FakeGitHub, authority, body_of,
    command, gate, gh, green, human_k, plan_body, planned, publish, ref, result, template,
    worker_view,
)
from tests.refoundation.agent_bus_fixtures import comment_body, unit

from agent_bus import decision as D
from agent_bus import errors as E
from agent_bus import goal as GP
from agent_bus import ledger as L
from agent_bus import machine as M
from agent_bus import publisher as P
from agent_bus import transition as X
from agent_bus.errors import BusError
from agent_bus.protocol import extract, parse_comment
from agent_bus.trust import PUBLISHER

H2 = "e" * 40
NEXT_WAVE = WAVE + ".NEXT"
NEXT_TASK = 5830000077
NEXT_CHECKS = [{"id": "NEXT-CHECK", "argv": ["python3", "-m", "unittest", "tests.next"]}]


def next_template() -> dict:
    return {"branch": BRANCH, "review_boundary": "after N1",
            "units": [unit("N1", allow=("docs/**",))]}


def two_wave_body(budget=BUDGET) -> str:
    """WAVE -> NEXT_WAVE (terminal). The Captain-authorized edge under test."""
    return plan_body(waves=[planned(nxt=NEXT_WAVE),
                            planned(wave=NEXT_WAVE, task=NEXT_TASK, command_=next_template(),
                                    checks=NEXT_CHECKS)],
                     terminal=NEXT_WAVE, budget=budget)


def world(plan: str = PLAN_BODY, **kw) -> FakeGitHub:
    return FakeGitHub(plan=plan, **kw)


def publisher_records(fake: FakeGitHub, schema: str) -> list[dict]:
    out = []
    for c in fake.by_publisher(fake.issue):
        record = L.parse_record(c["body"])
        if record is not None and record.schema == schema:
            out.append(dict(record.fields))
    return out


def last_k(fake: FakeGitHub) -> dict:
    return publisher_records(fake, L.CHECKPOINT)[-1]


def last_v(fake: FakeGitHub) -> dict:
    return publisher_records(fake, L.VERDICT)[-1]


def publisher_commands(fake: FakeGitHub) -> list:
    return [parse_comment(c["body"]) for c in fake.by_publisher(fake.pr)
            if parse_comment(c["body"]).kind == "WAVE_COMMAND"]


def accept(fake: FakeGitHub, comment_id=RESULT_COMMENT, head=H1, evidence="green",
           plan: str | None = None, wave=WAVE, checks=None, **kw) -> dict:
    if evidence == "green":
        evidence = green(head, wave=wave, body=plan or PLAN_BODY, checks=checks)
    return P.publish(TARGET, comment_id, X.digest(body_of(fake, comment_id)), ACCEPT, fake,
                     measured_head=head, selftest_exit=0, validation=evidence, **kw)


def next_result(fake: FakeGitHub, head=H2, message_id="w-next-result", status="P") -> int:
    """The Worker's answer to the planned successor, under the live checkpoint."""
    view = worker_view(fake)
    successor = view.state.pending_for("WORKER")[0]
    fake.tips[BRANCH] = head
    return fake.add(PR, result(message_id=message_id, head=head, parent=successor.message_id,
                               wave=successor.wave, checkpoint=view.authority.checkpoint,
                               task=view.authority.task, base=view.authority.accepted_head,
                               status=status, units=[{"id": "N1", "status": "DONE"}]))


# ============================================================ V1, V2: the checks gate ACCEPT

class TestV1RequiredChecksGateAccept(unittest.TestCase):
    def test_V1_selftest_green_but_one_required_check_red_cannot_accept(self):
        fake = world()
        report = accept(fake, evidence=green(red=("TASK-CHECK",)))
        self.assertEqual((report["exit"], report["code"]), (P.EXIT_REFUSED, E.TRANSITION_REFUSED))
        self.assertIn("TASK-CHECK", report["detail"])
        self.assertEqual(fake.writes, [])
        self.assertEqual(authority(fake).authority.accepted_head, H0)

    def test_V1_no_evidence_at_all_cannot_accept(self):
        fake = world()
        report = accept(fake, evidence=None)
        self.assertEqual(report["code"], E.TRANSITION_REFUSED)
        self.assertEqual(fake.writes, [])

    def test_V1_the_same_world_with_every_check_green_accepts(self):
        fake = world()
        self.assertEqual(accept(fake)["exit"], P.EXIT_COMPLETE)
        v = last_v(fake)
        self.assertEqual(json.loads(v["validation"]), green().as_dict())  # recorded
        self.assertEqual(v["goal_plan"], str(PLAN_COMMENT))

    def test_V1_a_recorded_accept_over_red_checks_is_not_authority(self):
        fake = world()
        accept(fake)
        v = next(c for c in fake.by_publisher(fake.issue)
                 if L.parse_record(c["body"]).schema == L.VERDICT)
        fields = dict(L.parse_record(v["body"]).fields)
        fields["validation"] = L.compact_json(green(red=("TASK-CHECK",)).as_dict())
        fake.edit(v["id"], L.render_verdict(fields))
        resolved = authority(fake)
        self.assertEqual(resolved.authority.checkpoint, K0)
        self.assertTrue(any("red" in r[2] for r in resolved.refused_candidates))

    def test_V1_a_rerun_takes_the_durable_evidence_not_a_new_run(self):
        fake = world()
        fake.crash_after = 1
        with self.assertRaises(Crash):
            accept(fake)
        # The second run's checks came back red; the durable review already fixed green.
        report = accept(fake, evidence=green(red=("TASK-CHECK",)))
        self.assertEqual(report["exit"], P.EXIT_COMPLETE, report)
        self.assertEqual(fake.kinds(), {"WAVE_REVIEW": 1, "V": 1, "K": 1, "WAVE_COMMAND": 0})


class TestV2ChecksMustBeOnTheResultHead(unittest.TestCase):
    def test_V2_checks_run_on_a_different_head_cannot_accept(self):
        fake = world()
        report = accept(fake, evidence=green(head=H_OTHER))
        self.assertEqual((report["exit"], report["code"]), (P.EXIT_REFUSED, E.TRANSITION_REFUSED))
        self.assertIn("not the result head", report["detail"])
        self.assertEqual(fake.writes, [])

    def test_V2_evidence_for_another_plan_wave_or_check_list_cannot_accept(self):
        cases = {
            "another_wave": green(wave=WAVE + ".OTHER"),
            "another_plan": dataclasses.replace(green(), plan=PLAN_COMMENT + 1),
            "another_digest": dataclasses.replace(green(), digest="0" * 64),
            "a_check_missing": dataclasses.replace(green(), checks=green().checks[:1]),
            "checks_reordered": dataclasses.replace(green(), checks=green().checks[::-1]),
            "an_extra_check": dataclasses.replace(
                green(), checks=green().checks + (("EXTRA", 0),)),
        }
        for name, evidence in cases.items():
            with self.subTest(case=name):
                fake = world()
                report = accept(fake, evidence=evidence)
                self.assertEqual(report["code"], E.TRANSITION_REFUSED)
                self.assertEqual(fake.writes, [])

    def test_V2_the_runner_records_the_head_git_measured_not_the_one_claimed(self):
        binding, _ = GP.bind(parse_comment(command()), world().comments("issue:1"),
                             TARGET.trust)
        ran: list = []
        evidence = GP.run_checks(binding, "/checkout",
                                 execute=lambda argv, cwd: ran.append((tuple(argv), cwd)) or 0,
                                 head_of=lambda checkout: H_OTHER)
        self.assertEqual(evidence.head, H_OTHER)
        self.assertEqual(ran, [(tuple(c["argv"]), "/checkout") for c in CHECKS])
        fake = world()
        self.assertEqual(accept(fake, evidence=evidence)["code"], E.TRANSITION_REFUSED)


# ============================================================ V3: nothing else makes an edge

class TestV3NothingElseCreatesAnEdge(unittest.TestCase):
    def test_V3_the_model_has_no_field_for_a_successor(self):
        for key in ("next", "successor", "task", "a", "head"):
            with self.subTest(key=key):
                with self.assertRaises(BusError) as caught:
                    D.parse(json.dumps({**ACCEPT.as_dict(), key: str(NEXT_TASK)}))
                self.assertEqual(caught.exception.code, E.DECISION_INVALID)

    def test_V3_a_worker_result_cannot_name_a_successor(self):
        body = json.loads(extract(result()))
        body["body"]["next"] = NEXT_WAVE
        with self.assertRaises(BusError) as caught:
            parse_comment("```mtj-bus\n" + json.dumps(body) + "\n```\n")
        self.assertEqual(caught.exception.code, E.BAD_VALUE)

    def test_V3_worker_notes_and_queued_task_prose_change_nothing(self):
        fake = world()
        fake.edit(RESULT_COMMENT, result(note=f"next: run task {NEXT_TASK} wave {NEXT_WAVE}"))
        fake.add(1, "```yaml\nschema: mtj-task/0\nid: C00\nstatus: QUEUED_NOT_SELECTED\n"
                    f"next_after_acceptance: {NEXT_TASK}\n```\n")
        fake.add(1, f"Captain: after this, continue to task {NEXT_TASK}.")
        self.assertEqual(accept(fake)["exit"], P.EXIT_COMPLETE)
        k = last_k(fake)
        self.assertEqual((k["a"], k["successor_command"], k["next"]),
                         ("0", X.NONE, X.NEXT_COMPLETE))
        self.assertEqual(publisher_commands(fake), [])

    def test_V3_a_command_for_an_unplanned_task_binds_nothing(self):
        other_task = plan_body(waves=[planned(task=TASK + 1)])
        fake = world(plan=other_task)  # the plan puts this wave under another task
        report = accept(fake, plan=other_task)
        self.assertEqual((report["exit"], report["verdict"]), (P.EXIT_COMPLETE, "C"))
        k = last_k(fake)
        self.assertEqual((k["h"], k["a"]), (H0, "0"))
        self.assertEqual(last_v(fake)["override"], X.PLAN_UNBOUND)

    def test_V3_a_command_wider_than_the_plan_binds_nothing(self):
        wider = template()
        wider["units"][0]["allow_paths"] = ["**"]
        body = {**wider, "goal": ref()}
        cmd = comment_body(kind="WAVE_COMMAND", actor="MANAGER", message_id=CMD_ID, wave=WAVE,
                           checkpoint=K0, task=TASK, base=H0, body=body)
        fake = world(cmd=cmd)
        self.assertEqual(accept(fake)["verdict"], "C")
        self.assertEqual(last_v(fake)["override"], X.PLAN_UNBOUND)

    def test_V3_a_forged_successor_or_k_cannot_select_another_task(self):
        fake = world(plan=two_wave_body())
        self.assertEqual(accept(fake, plan=two_wave_body())["exit"], P.EXIT_COMPLETE)
        successor = fake.pr[-1]
        forged = json.loads(extract(successor["body"]))
        for name, change in {
                "another_task": lambda e: e["authority"].__setitem__("task", NEXT_TASK + 1),
                "more_scope": lambda e: e["body"]["units"][0]["allow_paths"].append("**"),
                "another_wave": lambda e: e.__setitem__("wave", NEXT_WAVE + ".X")}.items():
            with self.subTest(successor=name):
                env = json.loads(json.dumps(forged))
                change(env)
                fake.edit(successor["id"], "```mtj-bus\n" + json.dumps(env) + "\n```\n")
                record = next(r for r in worker_view(fake).state.records
                              if r.comment_id == successor["id"])
                self.assertEqual(record.code, E.ROLE_REFUSED)
        fake.edit(successor["id"], "```mtj-bus\n" + json.dumps(forged) + "\n```\n")
        k = dict(next(c for c in fake.by_publisher(fake.issue)
                      if L.parse_record(c["body"]).schema == L.CHECKPOINT))
        for name, change in {"a_elsewhere": dict(a=str(NEXT_TASK + 1),
                                                 active_task=str(NEXT_TASK + 1)),
                             "terminal_claimed": dict(a="0", active_task="0",
                                                      successor_command=X.NONE,
                                                      next=X.NEXT_COMPLETE)}.items():
            with self.subTest(k=name):
                fields = dict(L.parse_record(k["body"]).fields)
                fields.update(change)
                fake.edit(k["id"], L.render_checkpoint(fields))
                self.assertEqual(authority(fake).authority.checkpoint, K0)
        fake.edit(k["id"], k["body"])
        self.assertEqual(authority(fake).authority.task, NEXT_TASK)


# ============================================================ V4, V5, V6: continuation

class TestV4NonterminalAcceptContinues(unittest.TestCase):
    def test_V4_accept_advances_h_selects_the_planned_task_and_posts_its_command(self):
        plan = two_wave_body()
        fake = world(plan=plan)
        report = accept(fake, plan=plan)
        self.assertEqual(report["exit"], P.EXIT_COMPLETE, report)
        self.assertEqual([w["record"] for w in report["writes"]],
                         ["WAVE_REVIEW", "V", "K", "WAVE_COMMAND"])
        live = authority(fake).authority
        self.assertEqual((live.accepted_head, live.task), (H1, NEXT_TASK))
        k = last_k(fake)
        txn = X.txn_id(K0, RESULT_COMMENT)
        self.assertEqual((k["verdict"], k["successor_command"], k["next"]),
                         ("A", X.next_id(txn), X.NEXT_SUCCESSOR))
        # Exactly the planned command, built by the plan, on the new head, under the new K.
        pending = worker_view(fake).state.pending_for("WORKER")
        self.assertEqual(len(pending), 1)
        cmd = pending[0]
        self.assertEqual((cmd.wave, cmd.base, cmd.authority),
                         (NEXT_WAVE, H1, {"issue": 1, "checkpoint": live.checkpoint,
                                          "task": NEXT_TASK}))
        self.assertEqual(GP.template_of(cmd.body), next_template())
        self.assertEqual(cmd.body["goal"], ref(plan))
        self.assertEqual(fake.pr[-1]["user"]["login"], PUBLISHER)
        # No human K anywhere after K0.
        self.assertEqual([c["id"] for c in fake.issue
                          if L.is_checkpoint(c["body"]) and c["user"]["login"] == AUTHOR], [K0])

    def test_V4_the_successor_lineage_repairs_then_reaches_the_terminal(self):
        plan = two_wave_body()
        fake = world(plan=plan)
        accept(fake, plan=plan)
        first = next_result(fake, message_id="w-next-result-1")
        report = P.publish(TARGET, first, X.digest(body_of(fake, first)), REPAIR, fake,
                           measured_head=H2, selftest_exit=0,
                           validation=green(H2, wave=NEXT_WAVE, body=plan, checks=NEXT_CHECKS))
        self.assertEqual((report["exit"], report["verdict"]), (P.EXIT_COMPLETE, "R"), report)
        repair = worker_view(fake).state.pending_for("WORKER")[0]
        self.assertEqual((repair.wave, repair.body["goal"]), (NEXT_WAVE + ".AR1", ref(plan)))
        self.assertEqual(authority(fake).authority.task, NEXT_TASK)
        second = next_result(fake, message_id="w-next-result-2")
        report = accept(fake, comment_id=second, head=H2, plan=plan, wave=NEXT_WAVE,
                        checks=NEXT_CHECKS)
        self.assertEqual(report["exit"], P.EXIT_COMPLETE, report)
        live = authority(fake).authority
        self.assertEqual((live.accepted_head, live.task), (H2, 0))
        self.assertEqual(last_k(fake)["next"], X.NEXT_COMPLETE)
        self.assertEqual(worker_view(fake).state.pending_for("WORKER"), [])

    def test_V4_a_crash_after_each_write_resumes_to_exactly_one_successor(self):
        plan = two_wave_body()
        for after in (1, 2, 3, 4):
            with self.subTest(crash_after=after):
                fake = world(plan=plan)
                fake.crash_after = after
                with self.assertRaises(Crash):
                    accept(fake, plan=plan)
                admitted = gate(fake)
                self.assertEqual(admitted.mode if admitted.wake else None,
                                 None if after == 4 else "resume", admitted.detail)
                for _ in range(2):
                    self.assertEqual(accept(fake, plan=plan, evidence=None)["exit"],
                                     P.EXIT_COMPLETE)
                self.assertEqual(fake.kinds(),
                                 {"WAVE_REVIEW": 1, "V": 1, "K": 1, "WAVE_COMMAND": 1})
                self.assertEqual(authority(fake).authority.task, NEXT_TASK)

    def test_V4_authority_moving_after_the_commit_posts_no_successor(self):
        plan = two_wave_body()
        fake = world(plan=plan)
        fake.crash_after = 3
        with self.assertRaises(Crash):
            accept(fake, plan=plan)
        fake.add(1, human_k(H1, 111))
        report = accept(fake, plan=plan, evidence=None)
        self.assertEqual((report["exit"], report["code"]), (P.EXIT_AFTER_COMMIT, E.TXN_SUPERSEDED))
        self.assertEqual(fake.kinds()["WAVE_COMMAND"], 0)


class TestV5TerminalAcceptStops(unittest.TestCase):
    def test_V5_terminal_accept_advances_h_and_selects_nothing(self):
        fake = world()
        report = accept(fake)
        self.assertEqual([w["record"] for w in report["writes"]], ["WAVE_REVIEW", "V", "K"])
        live = authority(fake).authority
        self.assertEqual((live.accepted_head, live.task), (H1, 0))
        k = last_k(fake)
        self.assertEqual((k["successor_command"], k["next"]), (X.NONE, X.NEXT_COMPLETE))
        self.assertEqual(worker_view(fake).state.pending_for("WORKER"), [])


C00_WAVE = "COMPILER.C00.W1"
C00_TASK = 5830000100  # fixture id: the queued C00 task, as a Captain plan would name it
C00_CHECKS = [{"id": "C00-GATE", "argv": ["python3", "-m", "compiler.c00", "--verify"]}]


class TestV6TheC00Edge(unittest.TestCase):
    def test_V6_the_c00_next_edge_continues_automatically_and_runs_no_compiler(self):
        c00 = {"branch": "compiler/c00", "review_boundary": "after C00-1",
               "units": [unit("C00-1", allow=("compiler/**",),
                              validation=("python3 -m compiler.c00 --verify",))]}
        plan = plan_body(waves=[planned(nxt=C00_WAVE),
                                planned(wave=C00_WAVE, task=C00_TASK, command_=c00,
                                        checks=C00_CHECKS)],
                         terminal=C00_WAVE)
        fake = world(plan=plan)
        executed: list = []
        with mock.patch.object(GP, "_execute", lambda argv, cwd: executed.append(argv) or 0):
            report = accept(fake, plan=plan)
        self.assertEqual(report["exit"], P.EXIT_COMPLETE, report)
        live = authority(fake).authority
        self.assertEqual((live.accepted_head, live.task), (H1, C00_TASK))
        pending = worker_view(fake).state.pending_for("WORKER")
        self.assertEqual([(c.wave, c.authority["task"]) for c in pending], [(C00_WAVE, C00_TASK)])
        self.assertEqual(GP.template_of(pending[0].body), c00)
        # Continuing selected the C00 work; nothing ran it. Every call was GitHub.
        self.assertEqual(executed, [])
        self.assertTrue(all(call[:2] == ("gh", "api") for call in fake.calls))
        self.assertFalse(any("compiler" in " ".join(call) for call in fake.calls
                             if "-f" not in call))


# ============================================================ V7: policy is the plan's

class TestV7PolicyIsCaptainRooted(unittest.TestCase):
    def repair_rounds(self, budget: int) -> list[str]:
        plan = plan_body(budget=budget)
        fake = world(plan=plan)
        letters = [publish(fake, REPAIR, validation=None)["verdict"]]
        for round_ in range(2, budget + 3):
            view = worker_view(fake)
            if not view.state.pending_for("WORKER"):
                break
            successor = view.state.pending_for("WORKER")[0]
            cid = fake.add(PR, result(message_id=f"w-result-ar{round_}",
                                      parent=successor.message_id, wave=successor.wave,
                                      checkpoint=view.authority.checkpoint))
            letters.append(publish(fake, REPAIR, comment_id=cid, validation=None)["verdict"])
        self.last = last_v(fake)
        return letters

    def test_V7_the_budget_is_the_plans(self):
        for budget, expected in {0: ["C"], 1: ["R", "C"], 2: ["R", "R", "C"]}.items():
            with self.subTest(budget=budget):
                self.assertEqual(self.repair_rounds(budget), expected)
                self.assertEqual(self.last["override"], X.BUDGET_EXHAUSTED)
        self.assertFalse(hasattr(X, "MAX_REPAIR_ROUNDS"))

    def test_V7_no_plan_fails_closed_to_captain(self):
        for decision in (ACCEPT, REPAIR):
            with self.subTest(decision=decision.verdict):
                fake = world(cmd=command(bound=False))
                report = publish(fake, decision)
                self.assertEqual((report["exit"], report["verdict"]), (P.EXIT_COMPLETE, "C"))
                self.assertEqual(last_v(fake)["override"], X.PLAN_UNBOUND)
                self.assertEqual(last_v(fake)["validation"], X.NONE)
                live = authority(fake).authority
                self.assertEqual((live.accepted_head, live.task), (H0, 0))
                self.assertEqual(fake.kinds()["WAVE_COMMAND"], 0)

    def test_V7_malformed_or_unrooted_policy_fails_closed_to_captain(self):
        good = json.loads(extract_goal(PLAN_BODY))
        broken = {
            "budget_missing": {k: v for k, v in good.items() if k != "repair_budget"},
            "budget_negative": {**good, "repair_budget": -1},
            "budget_not_int": {**good, "repair_budget": "3"},
            "terminal_wrong": {**good, "terminal": WAVE + ".ELSEWHERE"},
            "edge_to_nowhere": {**good, "waves": [{**good["waves"][0], "next": "NOWHERE"}]},
            "unknown_key": {**good, "successor": "ANYTHING"},
            "wrong_schema": {**good, "schema": "mtj-goal/0"},
            "no_checks": {**good, "waves": [{**good["waves"][0], "validation": []}]},
        }
        bodies = {name: "```mtj-goal\n" + json.dumps(plan) + "\n```\n"
                  for name, plan in broken.items()}
        bodies["not_json"] = "```mtj-goal\n{oops\n```\n"
        bodies["duplicate_key"] = "```mtj-goal\n{\"schema\": 1, \"schema\": 2}\n```\n"
        bodies["prose_first"] = "Plan:\n" + PLAN_BODY
        bodies["loop"] = plan_body(waves=[planned(nxt=WAVE + ".B"),
                                          planned(wave=WAVE + ".B", nxt=WAVE),
                                          planned(wave=WAVE + ".T")], terminal=WAVE + ".T")
        for name, body in bodies.items():
            with self.subTest(plan=name):
                with self.assertRaises(BusError) as caught:
                    GP.parse_plan(body)
                self.assertEqual(caught.exception.code, E.GOAL_PLAN_INVALID)
                fake = world(plan=body)
                report = publish(fake, REPAIR)
                self.assertEqual((report["exit"], report["verdict"]), (P.EXIT_COMPLETE, "C"))
                self.assertEqual(last_v(fake)["override"], X.PLAN_UNBOUND)
        unrooted = {
            "plan_by_a_stranger": lambda f: f.issue.__setitem__(
                1, gh(PLAN_COMMENT, PLAN_BODY, "drive-by")),
            "plan_by_the_publisher": lambda f: f.issue.__setitem__(
                1, gh(PLAN_COMMENT, PLAN_BODY, PUBLISHER)),
            "plan_edited_after_binding": lambda f: f.edit(
                PLAN_COMMENT, PLAN_BODY.replace('"repair_budget": 3', '"repair_budget": 9')),
            "decision_missing": lambda f: f.issue.pop(0),
            "decision_after_the_plan": lambda f: f.issue.__setitem__(
                0, gh(PLAN_COMMENT + 5, DECISION_BODY)),
        }
        for name, change in unrooted.items():
            with self.subTest(plan=name):
                fake = world()
                change(fake)
                if name == "decision_after_the_plan":  # the plan cites the later comment
                    body = plan_body(decision=PLAN_COMMENT + 5)
                    fake.issue[1] = gh(PLAN_COMMENT, body)
                    fake.pr[0] = gh(CMD_COMMENT, command(goal=ref(body)))
                report = publish(fake, ACCEPT)
                self.assertEqual((report["exit"], report["verdict"]), (P.EXIT_COMPLETE, "C"))
                self.assertEqual(last_v(fake)["override"], X.PLAN_UNBOUND)
                self.assertEqual(authority(fake).authority.accepted_head, H0)

    def test_V7_a_captain_required_from_the_worker_stays_a_captain_boundary(self):
        fake = world()
        cid = fake.add(PR, comment_body(kind="CAPTAIN_REQUIRED", actor="WORKER",
                                        message_id="w-question", wave=WAVE, parent=CMD_ID,
                                        checkpoint=K0, task=TASK, base=H0))
        fake.pr = [c for c in fake.pr if c["id"] != RESULT_COMMENT]
        self.assertEqual(publish(fake, ACCEPT, comment_id=cid)["code"], E.TRANSITION_REFUSED)
        report = publish(fake, D.parse(json.dumps({"verdict": "CAPTAIN", "reason": "x",
                                                   "findings": [], "evidence": []})),
                         comment_id=cid)
        self.assertEqual((report["exit"], report["verdict"]), (P.EXIT_COMPLETE, "C"))


def extract_goal(body: str) -> str:
    return GP._OPEN.match(body).group("payload")


# ============================================================ the runner and its CLI

class TestTheChecksRunner(unittest.TestCase):
    def test_a_check_that_cannot_start_is_red_never_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(GP._execute(["/nonexistent/check"], tmp), 127)
            self.assertEqual(GP._execute(["python3", "-c", "raise SystemExit(3)"], tmp), 3)
            self.assertEqual(GP._execute(["python3", "-c", "pass"], tmp), 0)

    def test_an_unmeasurable_head_is_a_failure_not_evidence(self):
        binding, _ = GP.bind(parse_comment(command()), world().comments("issue:1"),
                             TARGET.trust)
        with self.assertRaises(BusError) as caught:
            GP.run_checks(binding, "/x", execute=lambda a, c: 0, head_of=lambda c: "")
        self.assertEqual(caught.exception.code, E.GIT_FAILED)

    def test_run_checks_cli_runs_the_bound_checks_on_a_real_checkout(self):
        checks = [{"id": "PASSES", "argv": ["python3", "-c", "pass"]},
                  {"id": "FAILS", "argv": ["python3", "-c", "raise SystemExit(4)"]}]
        plan = plan_body(waves=[planned(checks=checks)])
        fake = world(plan=plan)
        with tempfile.TemporaryDirectory() as tmp:
            repo = os.path.join(tmp, "candidate")
            os.mkdir(repo)
            git = ["git", "-C", repo, "-c", "user.email=t@t", "-c", "user.name=t"]
            subprocess.run(["git", "init", "-q", repo], check=True)
            subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", "x"], check=True)
            head = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"], check=True,
                                  capture_output=True, text=True).stdout.strip()
            out = os.path.join(tmp, "validation.json")
            with contextlib.redirect_stdout(io.StringIO()):
                code = GP.main(["run-checks", "--repo", REPO, "--pr", str(PR),
                                "--trusted-author", AUTHOR, "--comment-id",
                                str(RESULT_COMMENT), "--checkout", repo, "--out", out],
                               run=fake)
            self.assertEqual(code, 0)
            with open(out) as handle:
                evidence = GP.evidence_from_mapping(json.load(handle))
        self.assertEqual(evidence.head, head)
        self.assertEqual(evidence.checks, (("PASSES", 0), ("FAILS", 4)))
        self.assertEqual((evidence.plan, evidence.wave), (PLAN_COMMENT, WAVE))

    def test_run_checks_cli_writes_nothing_when_no_plan_binds(self):
        fake = world(cmd=command(bound=False))
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "validation.json")
            with contextlib.redirect_stdout(io.StringIO()) as printed:
                code = GP.main(["run-checks", "--repo", REPO, "--pr", str(PR),
                                "--trusted-author", AUTHOR, "--comment-id",
                                str(RESULT_COMMENT), "--checkout", tmp, "--out", out],
                               run=fake)
            self.assertEqual(code, 0)
            self.assertFalse(os.path.exists(out))
        self.assertFalse(json.loads(printed.getvalue())["bound"])

    def test_check_plan_cli_lints_a_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "plan.md")
            with open(path, "w") as handle:
                handle.write(two_wave_body())
            with contextlib.redirect_stdout(io.StringIO()) as printed:
                self.assertEqual(GP.main(["check-plan", path]), 0)
            self.assertEqual(json.loads(printed.getvalue())["waves"], [WAVE, NEXT_WAVE])
            with open(path, "w") as handle:
                handle.write("```mtj-goal\n{}\n```\n")
            with contextlib.redirect_stdout(io.StringIO()) as printed:
                self.assertEqual(GP.main(["check-plan", path]), 2)
            self.assertEqual(json.loads(printed.getvalue())["code"], E.GOAL_PLAN_INVALID)


# ============================================================ rigs

class TestRiggedGoalProtections(unittest.TestCase):
    """Each guard above, weakened on purpose, lets its control through (RED)."""

    def test_rig_V1_the_all_green_requirement(self):
        fake = world()
        with mock.patch.object(GP.Evidence, "red", property(lambda self: [])):
            report = accept(fake, evidence=green(red=("TASK-CHECK",)))
        self.assertEqual(report["exit"], P.EXIT_COMPLETE)  # accepted over a red check

    def test_rig_V2_the_head_binding(self):
        fake = world()
        original = GP.check_evidence

        def headless(binding, evidence, result_head):
            return original(binding, evidence, evidence.head)
        with mock.patch.object(GP, "check_evidence", headless):
            report = accept(fake, evidence=green(head=H_OTHER))
        self.assertEqual(report["exit"], P.EXIT_COMPLETE)  # checks on another head accepted

    def test_rig_V3_the_task_guard(self):
        other_task = plan_body(waves=[planned(task=TASK + 1)])
        fake = world(plan=other_task)
        with mock.patch.object(GP, "_same_task", lambda entry, origin: True):
            report = accept(fake, plan=other_task)
        self.assertEqual(report["verdict"], "A")  # an unplanned task id bound

    def test_rig_V3_the_exact_command_guard(self):
        wider = template()
        wider["units"][0]["allow_paths"] = ["**"]
        fake = world(cmd=comment_body(kind="WAVE_COMMAND", actor="MANAGER", message_id=CMD_ID,
                                      wave=WAVE, checkpoint=K0, task=TASK, base=H0,
                                      body={**wider, "goal": ref()}))
        with mock.patch.object(GP, "_canon", lambda value: ""):
            self.assertEqual(accept(fake)["verdict"], "A")  # wider scope bound

    def test_rig_V3_the_successor_role_check(self):
        fake = world(plan=two_wave_body())
        accept(fake, plan=two_wave_body())
        successor = fake.pr[-1]
        env = json.loads(extract(successor["body"]))
        env["body"]["units"][0]["allow_paths"].append("**")
        fake.edit(successor["id"], "```mtj-bus\n" + json.dumps(env) + "\n```\n")
        with mock.patch.object(M, "same_message", lambda a, b: True):
            record = next(r for r in worker_view(fake).state.records
                          if r.comment_id == successor["id"])
        self.assertEqual(record.status, M.ACCEPTED)  # forged scope reached the Worker

    def test_rig_V7_a_defaulted_budget(self):
        original = GP.plan_from_mapping

        def lenient(raw):  # "missing policy" quietly becomes a default
            return original({"repair_budget": 3, **raw})
        body = "```mtj-goal\n" + json.dumps(
            {k: v for k, v in json.loads(extract_goal(PLAN_BODY)).items()
             if k != "repair_budget"}) + "\n```\n"
        fake = world(plan=body)
        with mock.patch.object(GP, "plan_from_mapping", lenient):
            report = publish(fake, REPAIR, validation=None)
        self.assertEqual(report["verdict"], "R")  # autonomy on no policy

    def test_rig_V7_the_unbound_override(self):
        fake = world(cmd=command(bound=False))
        stand_in = GP.bind(parse_comment(command()), world().comments("issue:1"),
                           TARGET.trust)[0]
        with mock.patch.object(GP, "bind", lambda origin, comments, trust: (stand_in, "")):
            self.assertEqual(publish(fake, REPAIR)["verdict"], "R")  # policy invented


if __name__ == "__main__":
    unittest.main()
