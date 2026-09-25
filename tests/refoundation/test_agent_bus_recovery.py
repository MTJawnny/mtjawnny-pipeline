"""R4.R2 AC2: queue dispositions and no-model interruption recovery.

The numbering binds to wave INFRA.AGENT-BUS-V1.MANAGER-WAKE-CODEX-ACTION.R4.R2.AR1,
unit AC2, `validation`, in order:

* `Q1` two valid Manager-bound messages under one K cannot publish conflicting
  checkpoints, and neither becomes an unexplained stale orphan.
* `Q2` a queued CAPTAIN_REQUIRED cannot be silently lost behind a WAVE_RESULT.
* `R3` interruption after every write boundary converges automatically, with no
  duplicate V, K, review or command, and no human rerun.
* `R4` bot recovery never invokes Codex; arbitrary bot-shaped or public comments
  cannot enter recovery.
* `R5` the model still runs only for a newly created trusted WORKER WAVE_RESULT or
  CAPTAIN_REQUIRED on PR 76.
* `R6` permissions: issues write only in the publisher; no contents/actions write,
  PAT, App, polling, merge, deployment or secret change.
* `R7` pins, drop-sudo read-only model isolation, the strict PR 76 pre-gate, live
  revalidation and the full selftest stay green: `test_agent_bus_wake_workflow`
  and `test_agent_bus_publisher` run unchanged in intent in the same selftest.
* `R8` each new protection is shown red when rigged weak (`TestRiggedAC2`).

The recovery run is simulated through the SAME entry points the workflow's
`workflow_run` path runs: `manager_gate` with `--event-name workflow_run`, the
evidence job's `publisher result-head`, and the publish job's argv. No network,
no model.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from unittest import mock

from tests.refoundation import test_agent_bus_publisher as PT
from tests.refoundation.agent_bus_fixtures import comment_body
from tests.refoundation.test_agent_bus_goal import NEXT_TASK, two_wave_body, world
from tests.refoundation.test_agent_bus_publisher import (
    ACCEPT, AUTHOR, CAPTAIN, CMD_ID, H0, H1, K0, PR, REPAIR, REPO, RESULT_COMMENT, RESULT_ID,
    TASK, TXN, WAVE, Crash, FakeGitHub, authority, body_of,
    forged_review, gate, human_k, publish, publisher_k, result, two_results,
)
from tests.refoundation.test_agent_bus_wake_workflow import WORKFLOW, run_workflow, text

from agent_bus import errors as E
from agent_bus import ledger as L
from agent_bus import machine as M
from agent_bus import manager_gate as G
from agent_bus import publisher as P
from agent_bus import transition as X
from agent_bus import workflow_policy as W
from agent_bus.decision import Decision
from agent_bus.trust import PUBLISHER, Trust

SECOND = RESULT_COMMENT + 1


def question(message_id="w-question", checkpoint=K0) -> str:
    return comment_body(kind="CAPTAIN_REQUIRED", actor="WORKER", message_id=message_id,
                        wave=WAVE, parent=CMD_ID, checkpoint=checkpoint, task=TASK, base=H0,
                        body={"question": "ratify the vocabulary?", "options": ["yes", "no"]})


def dispositions(fake: FakeGitHub) -> list[dict]:
    out = []
    for c in fake.by_publisher(fake.issue):
        record = L.parse_record(c["body"])
        if record is not None and record.schema == L.DISPOSITION:
            out.append({**record.fields, "id": c["id"]})
    return out


def wr_event(conclusion="failure", event="issue_comment", path=G.WORKFLOW_PATH,
             repo=REPO) -> dict:
    return {"action": "completed", "repository": {"full_name": repo},
            "workflow_run": {"event": event, "conclusion": conclusion, "path": path,
                             "repository": {"full_name": repo}}}


class Recovery:
    def __init__(self):
        self.gate: dict = {}
        self.model_calls = 0
        self.publish_exit: int | None = None
        self.report: dict = {}


def run_recovery(fake: FakeGitHub, event: dict | None = None, selftest: int = 0) -> Recovery:
    """The `workflow_run` path, job by job. There is no model step to call."""
    out = Recovery()
    with tempfile.TemporaryDirectory() as tmp:
        path, gate_out = os.path.join(tmp, "event.json"), os.path.join(tmp, "gate.out")
        with open(path, "w") as handle:
            json.dump(event or wr_event(), handle)
        with contextlib.redirect_stdout(io.StringIO()):
            G.main(["--event", path, "--event-name", "workflow_run", "--repo", REPO,
                    "--pr", str(PR), "--trusted-author", AUTHOR, "--github-output", gate_out],
                   run=fake)
        with open(gate_out) as handle:
            out.gate = dict(line.split("=", 1) for line in handle.read().splitlines() if line)
        if out.gate.get("wake") != "true":
            return out
        with contextlib.redirect_stdout(io.StringIO()) as head_out:
            P.main(["--repo", REPO, "--pr", str(PR), "--trusted-author", AUTHOR,
                    "result-head", "--comment-id", out.gate["comment_id"]], run=fake)
        head = head_out.getvalue().strip()
        argv = ["--repo", REPO, "--pr", str(PR), "--trusted-author", AUTHOR, "publish",
                "--comment-id", out.gate["comment_id"], "--digest", out.gate["digest"]]
        if out.gate["mode"] == "review":  # the workflow's model job refuses this event
            out.model_calls = 1
        if head:
            argv += ["--measured-head", head]
        argv += ["--selftest-exit", str(selftest)]
        with contextlib.redirect_stdout(io.StringIO()) as printed:
            out.publish_exit = P.main(argv, run=fake)
        out.report = json.loads(printed.getvalue())
    return out


# ============================================================ Q1: no orphans

class TestQ1NoConflictNoOrphan(unittest.TestCase):
    def test_Q1_one_k_links_and_the_other_message_is_disposed_of(self):
        fake = two_results()
        self.assertEqual(gate(fake, SECOND).code, E.GATE_QUEUED)
        self.assertEqual(publish(fake, REPAIR)["exit"], P.EXIT_COMPLETE)
        self.assertEqual(len([c for c in authority(fake).chain if c != K0]), 1)
        [d] = dispositions(fake)
        k = publisher_k(fake)[0]
        self.assertEqual((d["message_comment"], d["cited_checkpoint"], d["superseded_by"],
                          d["deciding_transaction"], d["disposition"], d["captain_attention"]),
                         (str(SECOND), str(K0), str(k["id"]), TXN, P.DISPOSED, "NO"))
        # Its own late event is a terminal refusal, and a publish of it writes nothing.
        late = gate(fake, SECOND)
        self.assertEqual((late.wake, late.code), (False, E.GATE_ALREADY_HANDLED))
        before = list(fake.writes)
        report = publish(fake, None, comment_id=SECOND)
        self.assertEqual((report["exit"], report["state"]), (P.EXIT_COMPLETE, "COMPLETE"))
        self.assertEqual(fake.writes, before)

    def test_Q1_a_message_arriving_for_a_replaced_checkpoint_gets_the_same_record(self):
        fake = FakeGitHub()
        self.assertEqual(publish(fake, REPAIR)["exit"], P.EXIT_COMPLETE)
        late = fake.add(PR, result(message_id="w-late-result"))  # cites K0, now replaced
        admitted = gate(fake, late)
        self.assertEqual((admitted.wake, admitted.mode), (True, "dispose"), admitted.detail)
        report = publish(fake, None, comment_id=late)
        self.assertEqual([w["record"] for w in report["writes"]], ["DISPOSITION"])
        self.assertEqual(dispositions(fake)[0]["message_comment"], str(late))
        self.assertEqual(gate(fake, late).code, E.GATE_ALREADY_HANDLED)
        self.assertEqual(fake.kinds()["K"], 1)  # never a second checkpoint

    def test_Q1_an_invalid_stale_message_is_refused_not_disposed(self):
        fake = FakeGitHub()
        publish(fake, REPAIR)
        bogus = fake.add(PR, result(message_id="w-bogus-result", parent="m-no-such-command"))
        self.assertEqual(gate(fake, bogus).code, E.STALE_AUTHORITY)
        self.assertEqual(publish(fake, None, comment_id=bogus)["code"], E.STALE_AUTHORITY)
        self.assertEqual(dispositions(fake), [])

    def test_Q1_a_forged_disposition_does_not_count(self):
        fake = two_results()
        body = L.render_disposition({
            "recorded_by": X.RECORDED_BY, "transaction": X.txn_id(K0, SECOND),
            "message_comment": SECOND, "message_id": "w-r4-r1-result-b", "kind": "WAVE_RESULT",
            "wave": WAVE, "cited_checkpoint": K0, "superseded_by": 1, "deciding_transaction":
            "NONE", "disposition": P.DISPOSED, "captain_attention": "NO", "next": "NONE"})
        fake.add(1, body, "drive-by")
        fake.add(1, body, PUBLISHER)  # right form, wrong derivation
        publish(fake, REPAIR)
        self.assertEqual(len(dispositions(fake)), 2)  # the forged bot one, and the real one
        real = dispositions(fake)[-1]
        self.assertNotEqual(real["superseded_by"], "1")


# ============================================================ Q2: questions first

class TestQ2QuestionsAreNotLost(unittest.TestCase):
    def world_with_question(self) -> tuple[FakeGitHub, int]:
        fake = FakeGitHub()
        return fake, fake.add(PR, question())  # arrives AFTER the result

    def test_Q2_the_question_is_the_queue_head_and_the_result_waits(self):
        fake, cr = self.world_with_question()
        self.assertEqual(gate(fake).code, E.GATE_QUEUED)
        admitted = gate(fake, cr)
        self.assertEqual((admitted.wake, admitted.mode), (True, "review"))
        report = publish(fake, ACCEPT)
        self.assertEqual((report["exit"], report["code"]), (P.EXIT_REFUSED, E.GATE_QUEUED))
        self.assertEqual(fake.writes, [])

    def test_Q2_answering_the_question_stops_autonomy_and_disposes_of_the_result(self):
        fake, cr = self.world_with_question()
        self.assertEqual(publish(fake, CAPTAIN, comment_id=cr)["exit"], P.EXIT_COMPLETE)
        live = authority(fake).authority
        self.assertEqual((live.accepted_head, live.task), (H0, 0))
        [d] = dispositions(fake)
        self.assertEqual((d["message_comment"], d["kind"]), (str(RESULT_COMMENT), "WAVE_RESULT"))

    def test_Q2_a_question_that_races_a_commit_is_recorded_for_the_captain(self):
        fake = FakeGitHub()
        publish(fake, ACCEPT)  # K0 replaced by an ACCEPT
        cr = fake.add(PR, question(message_id="w-late-question"))
        self.assertEqual(gate(fake, cr).mode, "dispose")
        publish(fake, None, comment_id=cr)
        [d] = dispositions(fake)
        self.assertEqual((d["kind"], d["captain_attention"], d["next"]),
                         ("CAPTAIN_REQUIRED", "YES", "CAPTAIN_REQUIRED"))

    def test_Q2_an_in_flight_result_yields_to_a_question_before_its_commit(self):
        fake = FakeGitHub()
        report = PT.TestNegativeControls._publish_changing_before(
            fake, 3, lambda f: f.add(PR, question()))  # lands before the K revalidation
        self.assertEqual((report["exit"], report["code"]), (P.EXIT_REFUSED, E.GATE_QUEUED))
        self.assertEqual(publisher_k(fake), [])

    def test_Q2_a_question_landing_inside_the_commit_write_is_still_recorded(self):
        # The window no read can see (contract section 8): the K commits, and the
        # question it displaced is disposed of for the Captain, not dropped.
        fake = FakeGitHub()
        fake.before_write[3] = lambda f: f.add(PR, question())
        self.assertEqual(publish(fake, ACCEPT)["exit"], P.EXIT_COMPLETE)
        [d] = dispositions(fake)
        self.assertEqual((d["kind"], d["captain_attention"]), ("CAPTAIN_REQUIRED", "YES"))


# ============================================================ R3: automatic convergence

WRITES = ["WAVE_REVIEW", "V", "K", "DISPOSITION", "WAVE_COMMAND"]


class TestR3InterruptionConverges(unittest.TestCase):
    def expected(self) -> dict:
        return {"WAVE_REVIEW": 1, "V": 1, "K": 1, "WAVE_COMMAND": 1, "D": 1}

    def test_R3_a_death_after_every_write_is_finished_by_the_recovery_run(self):
        for after in range(1, len(WRITES) + 1):
            with self.subTest(crash_after=WRITES[after - 1]):
                fake = two_results()
                fake.crash_after = after
                with self.assertRaises(Crash):
                    run_workflow(fake, model=REPAIR)
                self.assertEqual(len(fake.writes), after)
                recovered = run_recovery(fake)
                if after == len(WRITES):  # the last write landed: nothing is owed
                    self.assertEqual(recovered.gate["code"], E.GATE_NOTHING_OWED)
                else:
                    self.assertEqual((recovered.gate["mode"], recovered.publish_exit),
                                     ("resume", 0), recovered.report)
                self.assertEqual(recovered.model_calls, 0)
                self.assertEqual(fake.kinds(), self.expected())
                self.assertEqual(authority(fake).authority.publisher["verdict"], "R")
                # And a second recovery event finds nothing: idempotent.
                self.assertEqual(run_recovery(fake).gate["code"], E.GATE_NOTHING_OWED)
                self.assertEqual(fake.kinds(), self.expected())

    def test_R3_a_planned_accept_successor_is_recovered_too(self):
        plan = two_wave_body()
        from tests.refoundation.test_agent_bus_goal import accept
        for after in (1, 2, 3):
            with self.subTest(crash_after=after):
                fake = world(plan=plan)
                fake.crash_after = after
                with self.assertRaises(Crash):
                    accept(fake, plan=plan)
                recovered = run_recovery(fake)
                self.assertEqual(recovered.publish_exit, 0, recovered.report)
                self.assertEqual(fake.kinds(),
                                 {"WAVE_REVIEW": 1, "V": 1, "K": 1, "WAVE_COMMAND": 1})
                self.assertEqual(authority(fake).authority.task, NEXT_TASK)

    def test_R3_a_death_before_the_first_write_is_not_recoverable_without_the_model(self):
        # Nothing durable fixes a decision yet, and recovery never asks the model.
        fake = FakeGitHub()
        recovered = run_recovery(fake)
        self.assertEqual((recovered.gate["wake"], recovered.gate["code"]),
                         ("false", E.GATE_NOTHING_OWED))
        self.assertEqual(fake.writes, [])

    def test_R3_recovery_of_an_edited_message_fails_closed(self):
        fake = FakeGitHub()
        fake.crash_after = 1
        with self.assertRaises(Crash):
            run_workflow(fake, model=REPAIR)
        fake.edit(RESULT_COMMENT, result(note="edited after the review"))
        recovered = run_recovery(fake)
        self.assertEqual((recovered.publish_exit, recovered.report["code"]),
                         (P.EXIT_REFUSED, E.TXN_CONFLICT))
        self.assertEqual(publisher_k(fake), [])


# ============================================================ R4, R5: never the model

class TestR4R5RecoveryIsNarrow(unittest.TestCase):
    def test_R4_only_a_failed_comment_run_of_this_workflow_here_is_recoverable(self):
        fake = FakeGitHub()
        fake.crash_after = 1
        with self.assertRaises(Crash):
            run_workflow(fake, model=REPAIR)
        refused = {
            "a_recovery_runs_own_failure": (wr_event(event="workflow_run"), E.GATE_WRONG_EVENT),
            "another_workflow": (wr_event(path=".github/workflows/other.yml"),
                                 E.GATE_WRONG_EVENT),
            "a_successful_run": (wr_event(conclusion="success"), E.GATE_NOTHING_OWED),
            "another_repository": (wr_event(repo="someone/fork"), E.GATE_WRONG_SURFACE),
            "not_completed": ({**wr_event(), "action": "requested"}, E.GATE_WRONG_EVENT),
        }
        for name, (event, code) in refused.items():
            with self.subTest(event=name):
                out = run_recovery(fake, event)
                self.assertEqual((out.gate["wake"], out.gate["code"]), ("false", code))
        self.assertEqual(len(fake.writes), 1)

    def test_R4_public_and_bot_shaped_comments_cannot_enter_recovery(self):
        fake = FakeGitHub()
        txn = X.txn_id(K0, RESULT_COMMENT)
        fake.add(PR, forged_review(verdict="ACCEPT", review_message=X.review_id(txn)),
                 "drive-by")
        fake.add(PR, forged_review(review_message="m-bot-other-workflow"), PUBLISHER)
        fake.add(1, human_k(H1, 0).replace("next: GO", f"next: GO\ntransaction: {txn}"),
                 "drive-by")
        fake.add(PR, result(message_id="w-bot-result"), PUBLISHER)
        out = run_recovery(fake)
        self.assertEqual((out.gate["wake"], out.gate["code"]), ("false", E.GATE_NOTHING_OWED))
        self.assertEqual(fake.writes, [])

    def test_R5_recovery_never_answers_review_so_the_model_job_cannot_run(self):
        seen = set()
        for after in range(1, 5):
            fake = two_results()
            fake.crash_after = after
            with self.assertRaises(Crash):
                run_workflow(fake, model=REPAIR)
            decision = G.recover(wr_event(), REPO, PR, AUTHOR, fake)
            seen.add(decision.mode)
        self.assertEqual(seen, {"resume"})
        manager_if = W.load(text())["jobs"]["manager"]["if"]
        self.assertTrue(manager_if.startswith("github.event_name == 'issue_comment' && "))
        self.assertIn("needs.gate.outputs.mode == 'review'", manager_if)

    def test_R5_the_comment_gate_still_admits_only_a_trusted_worker_message(self):
        fake = FakeGitHub()
        self.assertEqual(gate(fake).mode, "review")
        manager_msg = fake.add(PR, comment_body(kind="WAVE_ABORT", actor="MANAGER",
                                                message_id="m-abort-x", wave=WAVE,
                                                checkpoint=K0, task=TASK, base=H0))
        self.assertEqual(gate(fake, manager_msg).code, E.GATE_NOT_FOR_MANAGER)
        bot = fake.add(PR, result(message_id="w-by-bot"), PUBLISHER)
        event = {"action": "created", "repository": {"full_name": REPO},
                 "issue": {"number": PR, "pull_request": {"url": "x"}},
                 "comment": {"id": bot, "body": body_of(fake, bot),
                             "user": {"login": PUBLISHER}}}
        refused = G.decide(event, "issue_comment", REPO, PR, AUTHOR, fake)
        self.assertEqual(refused.code, E.UNTRUSTED_AUTHOR)


# ============================================================ R6: no new credential

class TestR6NoNewCredential(unittest.TestCase):
    def test_R6_permissions_and_triggers(self):
        wf = W.load(text())
        self.assertEqual(W.check_text(text()), [])
        self.assertEqual(wf["on"], W.TRIGGERS)
        writers = {name: {k for k, v in job["permissions"].items() if v == "write"}
                   for name, job in wf["jobs"].items()}
        self.assertEqual({n: w for n, w in writers.items() if w}, {"publish": {"issues"}})
        code = "\n".join(line for line in text().splitlines()
                         if not line.lstrip().startswith("#"))
        for word in ("schedule", "cron", "workflow_dispatch", "repository_dispatch",
                     "actions: write", "contents: write", "secrets.GH_PAT", "app-id",
                     "gh workflow run", "gh run rerun", "gh pr merge", "git push"):
            with self.subTest(forbidden=word):
                self.assertNotIn(word, code)
        self.assertEqual([n for n, j in wf["jobs"].items() if "secrets." in json.dumps(j)],
                         ["manager"])


# ============================================================ R8: rigs

class TestRiggedAC2(unittest.TestCase):
    """Each new protection, weakened on purpose, lets its failure through (RED)."""

    def test_rig_Q1_no_dispositions_leaves_an_unexplained_stale_orphan(self):
        fake = two_results()
        with mock.patch.object(P, "displaced", lambda *a: []), \
                mock.patch.object(G, "displaced", lambda *a: []):
            publish(fake, REPAIR)
            late = gate(fake, SECOND)
        self.assertEqual(dispositions(fake), [])
        self.assertEqual(late.code, E.STALE_AUTHORITY)  # R4's orphan, back

    def test_rig_Q1_disposition_exactness(self):
        fake = two_results()
        forged = L.render_disposition({
            "recorded_by": X.RECORDED_BY, "transaction": X.txn_id(K0, SECOND),
            "message_comment": SECOND, "message_id": "w-r4-r1-result-b", "kind": "WAVE_RESULT",
            "wave": WAVE, "cited_checkpoint": K0, "superseded_by": 1, "deciding_transaction":
            "NONE", "disposition": P.DISPOSED, "captain_attention": "NO", "next": "NONE"})
        fake.add(1, forged, "drive-by")
        with mock.patch.object(P, "disposed", lambda world, target, item: True):
            publish(fake, REPAIR)
        self.assertEqual(len(dispositions(fake)), 0)  # a stranger's text was taken as done

    def test_rig_Q2_no_priority_lets_a_result_displace_the_question(self):
        fake = FakeGitHub()
        cr = fake.add(PR, question())
        plain = lambda self: [e for e in self.pending_for("MANAGER")  # noqa: E731
                              if not self.waves[e.wave].aborted
                              and e.wave not in set(self.superseded())]
        with mock.patch.object(M.BusState, "manager_queue", plain):
            self.assertEqual(publish(fake, ACCEPT)["exit"], P.EXIT_COMPLETE)
        self.assertEqual(authority(fake).authority.accepted_head, H1)  # accepted over it
        self.assertEqual(dispositions(fake)[0]["message_comment"], str(cr))

    def test_rig_R3_no_sweep_means_a_human_rerun(self):
        fake = two_results()
        fake.crash_after = 3
        with self.assertRaises(Crash):
            run_workflow(fake, model=REPAIR)
        with mock.patch.object(G, "sweep", lambda world, target: None):
            out = run_recovery(fake)
        self.assertEqual(out.gate["code"], E.GATE_NOTHING_OWED)
        self.assertEqual(fake.kinds()["WAVE_COMMAND"], 0)  # stuck

    def test_rig_R4_recovery_of_recovery_loops(self):
        fake = FakeGitHub()
        fake.crash_after = 1
        with self.assertRaises(Crash):
            run_workflow(fake, model=REPAIR)
        original = G.check_recovery_event

        def lax(event, repo):
            original({**event, "workflow_run": {**event["workflow_run"],
                                                "event": "issue_comment"}}, repo)
        with mock.patch.object(G, "check_recovery_event", lax):
            out = run_recovery(fake, wr_event(event="workflow_run"))
        self.assertEqual(out.gate["wake"], "true")  # a recovery run re-triggered itself

    def test_rig_R4_role_law_is_what_keeps_strangers_out_of_recovery(self):
        fake = FakeGitHub()
        txn = X.txn_id(K0, RESULT_COMMENT)
        from tests.refoundation.test_agent_bus_goal import green
        fake.add(PR, comment_body(
            kind="WAVE_REVIEW", actor="MANAGER", message_id=X.review_id(txn), wave=WAVE,
            parent=RESULT_ID, checkpoint=K0, task=TASK, base=H0,
            body={"verdict": "ACCEPT", "transaction": txn, "accepted_head": H1,
                  "decision": ACCEPT.as_dict(), "validation": green().as_dict(),
                  "result_digest": X.digest(result())}), "drive-by")
        with mock.patch.object(Trust, "is_publisher", lambda self, login: True):
            out = run_recovery(fake)
        self.assertEqual(out.gate["wake"], "true")  # a stranger's review entered recovery

    def test_rig_R5_recovery_answering_review_would_reach_the_model(self):
        fake = FakeGitHub()
        fake.crash_after = 1
        with self.assertRaises(Crash):
            run_workflow(fake, model=REPAIR)
        original = G.recover

        def to_review(*a, **kw):
            import dataclasses
            return dataclasses.replace(original(*a, **kw), mode="review")
        with mock.patch.object(G, "recover", to_review):
            out = run_recovery(fake)
        self.assertEqual(out.model_calls, 1)  # only the workflow's event guard remains
        self.assertIn("github.event_name == 'issue_comment'",
                      W.load(text())["jobs"]["manager"]["if"])


if __name__ == "__main__":
    unittest.main()
