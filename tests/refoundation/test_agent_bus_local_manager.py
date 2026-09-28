"""The local cross-review Manager: the hosted wake's composition, no new law.

Captain decisions E/G (Issue #1 comment 5864993788): the Manager runs on the
operator's machine and the reviewer is never the provider that did the work.
Admission, evidence, decision parsing and every write are the existing modules;
these tests pin the composition -- who reviews, what reaches the publisher, and
that a missing reviewer is a wait, never a verdict.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest import mock

from agent_bus import errors as E
from agent_bus import local_manager as L
from agent_bus import manager_gate, publisher
from agent_bus.errors import BusError

REPO, PR, WHO = "MTJawnny/mtjawnny-pipeline", 76, "MTJawnny"
GOOD = json.dumps({"verdict": "ACCEPT", "reason": "checked the diff and tests",
                   "findings": [], "evidence": ["selftest exit 0"]})


def admitted(mode="review"):
    return manager_gate.Decision(True, None, "admitted", 1001, "w-result", "WAVE_RESULT",
                                 "W", {}, mode=mode, digest="d" * 64)


COMMENT = {"id": 1001, "user": {"login": WHO},
           "body": '```mtj-bus\n{"parent": "m-command"}\n```'}


class Env:
    parent = "m-command"


class TestReviewerChoice(unittest.TestCase):
    def test_the_worker_never_reviews_its_own_wave(self):
        self.assertEqual(L.reviewer_for("claude", ("claude", "codex")), ["codex"])
        self.assertEqual(L.reviewer_for("codex", ("claude", "codex")), ["claude"])

    def test_a_failover_wave_has_no_eligible_reviewer(self):
        self.assertEqual(L.reviewer_for("claude|codex", ("claude", "codex")), [])

    def test_unknown_worker_lets_either_review(self):
        self.assertEqual(L.reviewer_for(None, ("claude", "codex")), ["claude", "codex"])


class TestEvent(unittest.TestCase):
    def test_the_synthesized_event_passes_the_gates_shape_stages(self):
        ctx = manager_gate.Context(event=L._event(COMMENT, REPO, PR), event_name="issue_comment",
                                   repo=REPO, transport_pr=PR, trusted_author=WHO, issue=1,
                                   run=None)
        for stage in (manager_gate.check_event, manager_gate.check_surface,
                      manager_gate.check_author):
            stage(ctx)  # raises on any mismatch


class TestPass(unittest.TestCase):
    def manager(self, worker, invoke):
        m = L.LocalManager(REPO, "/tmp/repo", PR, WHO, invoke=invoke, workdir=None)
        patches = [
            mock.patch.object(L.LocalManager, "admitted", lambda self: (admitted(), COMMENT, [])),
            mock.patch.object(L, "parse_comment", lambda body: Env()),
            mock.patch.object(L.LocalManager, "worker_provider", lambda self, c: worker),
            mock.patch.object(L.publisher, "result_head", lambda *a: "a" * 40),
            mock.patch.object(L.LocalManager, "measure",
                              lambda self, cid, head, root: ("a" * 40, 0, None)),
            mock.patch.object(L.LocalManager, "_context", lambda self, *a: "prompt"),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.published = []
        pub = mock.patch.object(L.publisher, "main",
                                lambda args, run=None: self.published.append(list(args)) or 0)
        pub.start()
        self.addCleanup(pub.stop)
        return m

    def test_codex_work_is_reviewed_by_claude_and_the_decision_reaches_the_publisher(self):
        calls = []
        def invoke(reviewer, prompt, candidate, root):
            calls.append(reviewer)
            decision = Path(root) / "seen.json"
            return {"decision": GOOD}
        report = self.manager("codex", invoke).poll_once(execute=True)
        self.assertEqual(calls, ["claude"])
        self.assertEqual(report["reviewer"], "claude")
        self.assertEqual(report["action"], "PUBLISHED")
        [args] = self.published
        self.assertIn("--decision-file", args)
        self.assertEqual(args[args.index("--selftest-exit") + 1], "0")
        self.assertEqual(args[args.index("--measured-head") + 1], "a" * 40)

    def test_NC_the_only_other_reviewer_out_of_capacity_is_a_wait_not_a_verdict(self):
        calls = []
        def invoke(reviewer, prompt, candidate, root):
            calls.append(reviewer)
            return {"capacity": True}
        report = self.manager("claude", invoke).poll_once(execute=True)
        self.assertEqual(calls, ["codex"])           # never falls back to the worker
        self.assertEqual(report["action"], "WAIT")
        self.assertEqual(self.published, [])

    def test_NC_a_decision_outside_the_schema_is_refused_before_any_write(self):
        bad = json.dumps({"verdict": "ACCEPT", "reason": "x", "findings": [],
                          "evidence": [], "next": "C03"})
        with self.assertRaises(BusError) as caught:
            self.manager("codex", lambda *a: {"decision": bad}).poll_once(execute=True)
        self.assertEqual(caught.exception.code, E.DECISION_INVALID)
        self.assertEqual(self.published, [])

    def test_a_failover_wave_waits_for_a_human(self):
        report = self.manager("claude|codex", lambda *a: self.fail("no model may run")) \
            .poll_once(execute=True)
        self.assertEqual(report["action"], "WAIT")
        self.assertEqual(self.published, [])

    def test_dry_run_runs_no_model_and_writes_nothing(self):
        report = self.manager("codex", lambda *a: self.fail("no model in a dry run")) \
            .poll_once(execute=False)
        self.assertEqual((report["action"], report["reviewer"]), ("REVIEW_DRY_RUN", "claude"))
        self.assertEqual(self.published, [])


class TestNonReviewModes(unittest.TestCase):
    def test_a_disposition_or_resume_goes_to_the_publisher_without_a_model(self):
        published = []
        m = L.LocalManager(REPO, "/tmp/repo", PR, WHO,
                           invoke=lambda *a: self.fail("no model outside review mode"))
        with mock.patch.object(L.LocalManager, "admitted",
                               lambda self: (admitted("dispose"), COMMENT, [])), \
             mock.patch.object(L, "parse_comment", lambda body: Env()), \
             mock.patch.object(L.LocalManager, "worker_provider", lambda self, c: "codex"), \
             mock.patch.object(L.publisher, "main",
                               lambda args, run=None: published.append(args) or 0):
            report = m.poll_once(execute=True)
        self.assertEqual(report["action"], "PUBLISHED")
        self.assertNotIn("--decision-file", published[0])


class TestNothingPending(unittest.TestCase):
    def test_no_admitted_message_is_nothing_actionable(self):
        m = L.LocalManager(REPO, "/tmp/repo", PR, WHO)
        with mock.patch.object(L.LocalManager, "admitted", lambda self: (None, None, ["9: X"])):
            self.assertEqual(m.poll_once()["reason"], E.NOTHING_ACTIONABLE)


if __name__ == "__main__":
    unittest.main()


class TestReviewerCommands(unittest.TestCase):
    """What actually runs: a read-only Codex, and a Claude with no edit tools."""

    def argv_for(self, reviewer):
        seen = []
        def run(argv, stdin=None, timeout=None, cwd=None):
            seen.append(list(argv))
            from agent_bus.shell import Completed
            if argv[0] == "claude":
                return Completed(tuple(argv), 0, json.dumps(
                    {"type": "result", "subtype": "success", "is_error": False,
                     "structured_output": json.loads(GOOD)}), "")
            Path(argv[argv.index("-o") + 1]).write_text(GOOD, encoding="utf-8")
            return Completed(tuple(argv), 0, "", "")
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            m = L.LocalManager(REPO, "/tmp/repo", PR, WHO, run=run)
            answer = m._review(reviewer, "prompt", Path(d), Path(d))
        return seen[0], answer

    def test_codex_reviews_read_only_against_the_decision_schema(self):
        argv, answer = self.argv_for("codex")
        self.assertEqual(argv[argv.index("--sandbox") + 1], "read-only")
        self.assertIn("--output-schema", argv)
        self.assertEqual(json.loads(answer["decision"])["verdict"], "ACCEPT")

    def test_claude_reviews_with_no_edit_tools_no_ambient_settings_and_the_schema(self):
        argv, answer = self.argv_for("claude")
        self.assertEqual(argv[argv.index("--setting-sources") + 1], "")
        self.assertEqual(argv[argv.index("--tools") + 1], "Read,Grep,Glob,Bash")
        settings = json.loads(argv[argv.index("--settings") + 1])
        for tool in ("Edit", "Write", "NotebookEdit"):
            self.assertIn(tool, settings["permissions"]["deny"])
        self.assertIs(settings["sandbox"]["enabled"], True)
        self.assertIn("--json-schema", argv)
        self.assertEqual(json.loads(answer["decision"])["verdict"], "ACCEPT")


class TestCycle(unittest.TestCase):
    def test_manager_then_worker_and_a_manager_failure_never_starves_the_worker(self):
        order = []
        class Worker:
            trust = None
            def poll_once(self, execute=False):
                order.append("worker")
                return {"action": "NONE"}
        class Manager:
            def poll_once(self, execute=False):
                order.append("manager")
                raise BusError(E.DECISION_INVALID, "bad")
        report = L.WorkerAndManager(Worker(), Manager()).poll_once(execute=True)
        self.assertEqual(order, ["manager", "worker"])
        self.assertEqual(report["manager"]["reason"], E.DECISION_INVALID)


class TestRootContract(unittest.TestCase):
    def test_claude_md_states_cross_review_and_the_decision_f_stop(self):
        root = Path(__file__).resolve().parents[2]
        text = " ".join((root / "CLAUDE.md").read_text(encoding="utf-8").split())
        self.assertIn("whichever model did a task, the OTHER one (Claude Code or Codex) "
                      "reviews it", text)
        self.assertIn("No model accepts its own work.", text)
        self.assertIn("the conflict first goes to the other model for analysis", text)
        self.assertIn("Captain-owned decisions are recorded and batched", text)
        self.assertNotIn("**Manager** — ChatGPT", text)
