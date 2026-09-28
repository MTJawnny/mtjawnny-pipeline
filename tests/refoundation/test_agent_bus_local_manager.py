"""The local cross-review Manager: the hosted wake's composition, no new law.

Captain decisions E/G (Issue #1 comment 5864993788): the Manager runs on the
operator's machine and the reviewer is never the provider that did the work.
Admission, evidence, decision parsing and every write are the existing modules;
these tests pin the composition -- who reviews, what reaches the publisher, and
that a missing reviewer is a wait, never a verdict.

P1.R1 (Issue #1 comment 5877392306) closes Codex findings F1-F7: candidate code
runs confined, the reviewer cannot write, unattributed work is a host CAPTAIN,
contracts come from the watcher's own checkout, nothing touches the operator
checkout, and operator state is never copied through a candidate symlink.
"""

from __future__ import annotations

import hashlib
import json
import os
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from agent_bus import errors as E
from agent_bus import local_manager as L
from agent_bus import manager_gate, publisher, worker_evidence
from agent_bus.errors import BusError
from agent_bus.shell import Completed, Runner

REPO, PR, WHO = "MTJawnny/mtjawnny-pipeline", 76, "MTJawnny"
GOOD = json.dumps({"verdict": "ACCEPT", "reason": "checked the diff and tests",
                   "findings": [], "evidence": ["selftest exit 0"]})
ROOT = Path(__file__).resolve().parents[2]


def admitted(mode="review"):
    return manager_gate.Decision(True, None, "admitted", 1001, "w-result", "WAVE_RESULT",
                                 "W", {}, mode=mode, digest="d" * 64)


COMMENT = {"id": 1001, "user": {"login": WHO},
           "body": '```mtj-bus\n{"parent": "m-command"}\n```'}


class Env:
    parent = "m-command"


def git(*argv, cwd):
    return subprocess.run(["git", *argv], cwd=cwd, check=True, capture_output=True,
                          text=True).stdout.strip()


def make_repo(where: Path) -> tuple[Path, str]:
    repo = where / "operator"
    repo.mkdir()
    git("init", "-q", cwd=repo)
    (repo / "README").write_text("x\n")
    git("add", "README", cwd=repo)
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "c", cwd=repo)
    return repo, git("rev-parse", "HEAD", cwd=repo)


def evidence_comment(command, provider, actor="WORKER"):
    payload = {"schema": "mtj-worker-evidence/1", "actor": actor, "command": command,
               "provider": provider}
    body = worker_evidence.PREFIX + json.dumps(payload) + worker_evidence.SUFFIX
    return SimpleNamespace(author=WHO, body=body)


class TestReviewerChoice(unittest.TestCase):
    def test_the_worker_never_reviews_its_own_wave(self):
        self.assertEqual(L.reviewer_for("claude", ("claude", "codex")), ["codex"])
        self.assertEqual(L.reviewer_for("codex", ("claude", "codex")), ["claude"])

    def test_a_failover_wave_has_no_eligible_reviewer(self):
        self.assertEqual(L.reviewer_for("claude|codex", ("claude", "codex")), [])

    def test_F3_unknown_worker_lets_nobody_review(self):
        # Before P1.R1 this returned ["claude", "codex"]: self-review was possible.
        self.assertEqual(L.reviewer_for(None, ("claude", "codex")), [])
        self.assertEqual(L.reviewer_for("gpt", ("claude", "codex")), [])


class TestAttribution(unittest.TestCase):
    """F3: only validated evidence naming exactly one known provider attributes."""

    def attribute(self, *comments, command="m-command"):
        m = L.LocalManager(REPO, "/nonexistent", PR, WHO)
        world = SimpleNamespace(issue_comments=list(comments))
        with mock.patch.object(L.publisher, "observe", lambda *a: world):
            return m.attribution(command)

    def test_exactly_one_known_provider_attributes(self):
        self.assertEqual(self.attribute(evidence_comment("m-command", "codex")),
                         ("codex", None))

    def test_NC_missing_malformed_unknown_or_several_providers_do_not(self):
        for comments in ((),
                         (evidence_comment("m-other", "codex"),),
                         (evidence_comment("m-command", None),),
                         (evidence_comment("m-command", "gpt"),),
                         (evidence_comment("m-command", "codex", actor="MANAGER"),),
                         (evidence_comment("m-command", "codex"),
                          evidence_comment("m-command", "claude"))):
            provider, problem = self.attribute(*comments)
            self.assertIsNone(provider, comments)
            self.assertTrue(problem, comments)

    def test_NC_untrusted_evidence_does_not_attribute(self):
        c = evidence_comment("m-command", "codex")
        c.author = "someone-else"
        self.assertIsNone(self.attribute(c)[0])

    def test_no_command_is_unattributed(self):
        self.assertIsNone(self.attribute(evidence_comment("m-command", "codex"),
                                         command=None)[0])


class TestEvent(unittest.TestCase):
    def test_the_synthesized_event_passes_the_gates_shape_stages(self):
        ctx = manager_gate.Context(event=L._event(COMMENT, REPO, PR), event_name="issue_comment",
                                   repo=REPO, transport_pr=PR, trusted_author=WHO, issue=1,
                                   run=None)
        for stage in (manager_gate.check_event, manager_gate.check_surface,
                      manager_gate.check_author):
            stage(ctx)  # raises on any mismatch


class PassHarness(unittest.TestCase):
    """poll_once with admission, attribution, measurement and publishing faked."""

    measured = None

    def manager(self, worker, invoke, problem=None, **kw):
        m = L.LocalManager(REPO, "/tmp/repo", PR, WHO, invoke=invoke, workdir=None, **kw)
        attribution = (None, problem) if problem else (worker, None)
        patches = [
            mock.patch.object(L.LocalManager, "admitted", lambda self: (admitted(), COMMENT, [])),
            mock.patch.object(L, "parse_comment", lambda body: Env()),
            mock.patch.object(L.LocalManager, "attribution", lambda self, c: attribution),
            mock.patch.object(L.publisher, "result_head", lambda *a: "a" * 40),
            mock.patch.object(L.LocalManager, "measure",
                              lambda _, cid, head, ws: self.fake_measure(cid, head, ws)),
            mock.patch.object(L.LocalManager, "_context", lambda self, *a: "prompt"),
            mock.patch.object(L.LocalManager, "_head_of", lambda self, p: "a" * 40),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.published, self.decisions = [], []
        def main(args, run=None):
            args = list(args)
            self.published.append(args)
            if "--decision-file" in args:
                self.decisions.append(json.loads(
                    Path(args[args.index("--decision-file") + 1]).read_text()))
            return 0
        pub = mock.patch.object(L.publisher, "main", main)
        pub.start()
        self.addCleanup(pub.stop)
        return m

    def fake_measure(self, comment_id, head, ws):
        return self.measured or L.Measurement("a" * 40, 0, "OK", None, "no plan")


class TestPass(PassHarness):
    def test_codex_work_is_reviewed_by_claude_and_the_decision_reaches_the_publisher(self):
        calls = []
        def invoke(reviewer, prompt, ws):
            calls.append(reviewer)
            return {"decision": GOOD}
        report = self.manager("codex", invoke).poll_once(execute=True)
        self.assertEqual(calls, ["claude"])
        self.assertEqual(report["reviewer"], "claude")
        self.assertEqual(report["action"], "PUBLISHED")
        [args] = self.published
        self.assertIn("--decision-file", args)
        self.assertEqual(args[args.index("--selftest-exit") + 1], "0")
        self.assertEqual(args[args.index("--measured-head") + 1], "a" * 40)

    def test_F7_the_only_other_reviewer_out_of_capacity_is_a_wait_not_a_verdict(self):
        calls = []
        def invoke(reviewer, prompt, ws):
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

    def test_F3_unattributed_work_is_a_host_captain_and_no_model_runs(self):
        for problem in ("no Worker evidence attributes command m-command to a provider",
                        "command m-command was run by more than one provider (claude, codex)"):
            report = self.manager(None, lambda *a: self.fail("no model may run"),
                                  problem=problem).poll_once(execute=True)
            self.assertEqual(report["action"], "PUBLISHED")
            self.assertEqual(self.decisions[-1]["verdict"], "CAPTAIN")
            self.assertEqual(self.decisions[-1]["findings"], [problem])
            self.assertNotIn("--measured-head", self.published[-1])

    def test_F3_an_order_with_no_other_provider_is_a_host_captain(self):
        report = self.manager("claude", lambda *a: self.fail("no model may run"),
                              order=("claude",)).poll_once(execute=True)
        self.assertEqual((report["action"], self.decisions[-1]["verdict"]),
                         ("PUBLISHED", "CAPTAIN"))

    def test_F3_dry_run_of_unattributed_work_names_no_reviewer(self):
        report = self.manager(None, lambda *a: self.fail("no model"),
                              problem="unattributed").poll_once(execute=False)
        self.assertEqual((report["action"], report["reviewer"]), ("CAPTAIN_DRY_RUN", None))
        self.assertEqual(self.published, [])

    def test_dry_run_runs_no_model_and_writes_nothing(self):
        report = self.manager("codex", lambda *a: self.fail("no model in a dry run")) \
            .poll_once(execute=False)
        self.assertEqual((report["action"], report["reviewer"]), ("REVIEW_DRY_RUN", "claude"))
        self.assertEqual(self.published, [])


class TestEvidenceIsTheHosts(PassHarness):
    """F2: a reviewer that writes anyway changes nothing that is published."""

    def with_evidence(self):
        from agent_bus import goal
        self.measured = L.Measurement("a" * 40, 0, "OK", goal.Evidence(
            7, "e" * 64, "W", "a" * 40, (("c1", 0),)))

    def test_the_validation_file_published_is_the_one_measured(self):
        self.with_evidence()
        seen = []
        def main(args, run=None):
            seen.append(json.loads(Path(args[args.index("--validation-file") + 1]).read_text()))
            return 0
        m = self.manager("codex", lambda *a: {"decision": GOOD})
        with mock.patch.object(L.publisher, "main", main):
            m.poll_once(execute=True)
        self.assertEqual(seen[0]["checks"], [{"id": "c1", "exit": 0}])

    def test_NC_tampered_validation_evidence_publishes_nothing(self):
        self.with_evidence()
        def invoke(reviewer, prompt, ws):
            path = ws.evidence / "validation.json"
            raw = json.loads(path.read_text())
            raw["checks"] = [{"id": "c1", "exit": 0}, {"id": "c2", "exit": 0}]
            path.write_text(json.dumps(raw, sort_keys=True))
            return {"decision": GOOD}
        with self.assertRaises(BusError) as caught:
            self.manager("codex", invoke).poll_once(execute=True)
        self.assertEqual(caught.exception.code, E.TRANSITION_REFUSED)
        self.assertEqual(self.published, [])

    def test_NC_a_moved_review_clone_publishes_nothing(self):
        m = self.manager("codex", lambda *a: {"decision": GOOD})
        with mock.patch.object(L.LocalManager, "_head_of", lambda self, p: "b" * 40):
            with self.assertRaises(BusError) as caught:
                m.poll_once(execute=True)
        self.assertEqual(caught.exception.code, E.TRANSITION_REFUSED)
        self.assertEqual(self.published, [])


class TestNonReviewModes(unittest.TestCase):
    def test_a_disposition_or_resume_goes_to_the_publisher_without_a_model(self):
        published = []
        m = L.LocalManager(REPO, "/tmp/repo", PR, WHO,
                           invoke=lambda *a: self.fail("no model outside review mode"))
        with mock.patch.object(L.LocalManager, "admitted",
                               lambda self: (admitted("dispose"), COMMENT, [])), \
             mock.patch.object(L.LocalManager, "attribution",
                               lambda self, c: self.fail("no attribution outside review")), \
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


def fake_gh(real=Runner()):
    """Real git and cp; `gh` answers an empty list; sandbox-exec is recorded."""
    calls = []
    def run(argv, stdin=None, timeout=None, cwd=None):
        calls.append((list(argv), cwd))
        if argv[0] == "gh":
            return Completed(tuple(argv), 0, "[]", "")
        if argv[0] == L.SANDBOX_EXEC:
            return Completed(tuple(argv), 0, "Ran 1 test\nOK\n", "")
        return real(argv, stdin=stdin, timeout=timeout, cwd=cwd)
    run.calls = calls
    return run


class TestWorkspace(unittest.TestCase):
    """F1/F4/F5/F6 against real clones of a real repository."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(__import__("shutil").rmtree, self.tmp, True)
        self.repo, self.head = make_repo(self.tmp)
        self.work = self.tmp / "work"
        self.work.mkdir()

    def manager(self, run, **kw):
        return L.LocalManager(REPO, str(self.repo), PR, WHO, run=run,
                              workdir=str(self.work), **kw)

    def ws(self):
        root = self.work / "root"
        root.mkdir()
        (root / "evidence").mkdir()
        return L.Workspace(root)

    def test_F1_candidate_code_runs_only_confined_and_the_binding_is_host_read(self):
        run = fake_gh()
        binding = SimpleNamespace(comment_id=7, digest="e" * 64,
                                  entry=SimpleNamespace(wave="W", checks=(
                                      SimpleNamespace(id="c1", argv=("python3", "t.py")),)))
        with mock.patch.object(L.publisher, "binding_for", lambda *a: (binding, None)):
            m = self.manager(run).measure(1001, self.head, self.ws())
        self.assertEqual((m.head, m.selftest_exit), (self.head, 0))
        self.assertEqual(m.evidence.checks, (("c1", 0),))
        executed = [argv for argv, cwd in run.calls if argv[0] not in ("git", "gh", "cp")]
        self.assertEqual(len(executed), 2)          # the selftest and one check
        for argv in executed:
            self.assertEqual(argv[0], L.SANDBOX_EXEC)
            self.assertIn("(deny network*)", argv[2])
            self.assertEqual(argv[3:5], ["/usr/bin/env", "-i"])
        self.assertEqual(executed[0][-4:], ["python3", "-m", "agent_bus", "selftest"])
        self.assertEqual(executed[1][-2:], ["python3", "t.py"])
        # Evidence commands run in the candidate clone; the review clone is pristine.
        cwds = {cwd for argv, cwd in run.calls if argv[0] == L.SANDBOX_EXEC}
        self.assertEqual(cwds, {str(self.work / "root" / "candidate")})

    def test_F1_clones_share_no_object_file_with_the_operator_repository(self):
        ws = self.ws()
        with mock.patch.object(L.publisher, "binding_for", lambda *a: (None, "no plan")):
            self.manager(fake_gh()).measure(1001, self.head, ws)
        def inodes(repo):
            objects = Path(repo) / ".git" / "objects"
            return {p.stat().st_ino for p in objects.rglob("*") if p.is_file()}
        self.assertFalse(inodes(self.repo) & inodes(ws.candidate))
        self.assertFalse(inodes(self.repo) & inodes(ws.review))

    def test_F4_contracts_come_from_the_watchers_checkout_and_are_outside_the_candidate(self):
        ws = self.ws()
        with mock.patch.object(L.publisher, "binding_for", lambda *a: (None, "no plan")):
            m = self.manager(fake_gh())
            m.measure(1001, self.head, ws)
        prompt = m._context(ws, 1001, "w-result", "selftest")
        for rel in L.CONTRACTS:
            self.assertEqual((ws.context / "contracts" / rel).read_bytes(),
                             (L.TRUSTED_ROOT / rel).read_bytes())
        self.assertNotIn(ws.context, [ws.candidate, *ws.candidate.parents])
        self.assertFalse((ws.review / "CLAUDE.md").exists())   # the candidate has its own, or none
        self.assertIn("REVIEW\nMATERIAL", prompt)
        self.assertIn(str(ws.review), prompt)

    def test_F4_reviewers_work_from_the_context_dir_never_the_candidate(self):
        ws = self.ws()
        ws.context.mkdir()
        seen = []
        def run(argv, stdin=None, timeout=None, cwd=None):
            seen.append((list(argv), cwd))
            if argv[0] == "claude":
                return Completed(tuple(argv), 0, json.dumps(
                    {"type": "result", "subtype": "success", "is_error": False,
                     "structured_output": json.loads(GOOD)}), "")
            Path(argv[argv.index("-o") + 1]).write_text(GOOD, encoding="utf-8")
            return Completed(tuple(argv), 0, "", "")
        m = self.manager(run)
        for reviewer in ("codex", "claude"):
            self.assertEqual(json.loads(m._review(reviewer, "p", ws)["decision"])["verdict"],
                             "ACCEPT")
        (codex, codex_cwd), (claude, claude_cwd) = seen
        self.assertEqual((codex_cwd, claude_cwd), (str(ws.context), str(ws.context)))
        self.assertEqual(codex[codex.index("--cd") + 1], str(ws.context))
        self.assertEqual(codex[codex.index("--sandbox") + 1], "read-only")

    def test_F5_a_headless_review_never_touches_the_operator_checkout(self):
        before = git("status", "--porcelain", "--ignored", cwd=self.repo)
        prompts = []
        m = self.manager(fake_gh(), invoke=lambda r, prompt, ws: prompts.append(ws) or
                         {"decision": GOOD})
        with mock.patch.object(L.LocalManager, "admitted",
                               lambda self: (admitted(), COMMENT, [])), \
             mock.patch.object(L, "parse_comment", lambda body: Env()), \
             mock.patch.object(L.LocalManager, "attribution", lambda self, c: ("codex", None)), \
             mock.patch.object(L.publisher, "result_head", lambda *a: ""), \
             mock.patch.object(L.publisher, "main", lambda args, run=None: 0):
            report = m.poll_once(execute=True)
        self.assertEqual(report["action"], "PUBLISHED")
        self.assertEqual(git("status", "--porcelain", "--ignored", cwd=self.repo), before)
        [ws] = prompts
        self.assertEqual(ws.root.parent, self.work)
        self.assertFalse(ws.root.exists())          # the whole workspace is disposed
        self.assertEqual(list(self.work.iterdir()), [])

    def test_F6_operator_state_is_copied_and_copy_failure_is_loud(self):
        state = self.tmp / "state"
        (state / "data").mkdir(parents=True)
        (state / "data" / "cards.jsonl").write_text("{}\n")
        ws = self.ws()
        m = self.manager(fake_gh(), operator_state=str(state))
        m._checkout(self.head, ws.candidate, str(self.repo))
        m._copy_state(ws.candidate)
        self.assertEqual((ws.candidate / "data" / "cards.jsonl").read_text(), "{}\n")
        failing = lambda argv, **kw: Completed(tuple(argv), 1, "", "boom") \
            if argv[0] == "cp" else Runner()(argv, **kw)
        other = self.work / "other"
        m2 = self.manager(failing, operator_state=str(state))
        m2._checkout(self.head, other, str(self.repo))
        with self.assertRaises(BusError) as caught:
            m2._copy_state(other)
        self.assertIn("boom", caught.exception.detail)

    def test_NC_F6_a_candidate_symlink_never_redirects_operator_state(self):
        state = self.tmp / "state"
        (state / "experiments" / "out").mkdir(parents=True)
        outside = self.tmp / "outside"
        outside.mkdir()
        (self.repo / "experiments").symlink_to(outside)
        git("add", "experiments", cwd=self.repo)
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "l",
            cwd=self.repo)
        head = git("rev-parse", "HEAD", cwd=self.repo)
        ws = self.ws()
        m = self.manager(fake_gh(), operator_state=str(state))
        m._checkout(head, ws.candidate, str(self.repo))
        with self.assertRaises(BusError) as caught:
            m._copy_state(ws.candidate)
        self.assertIn("symlink", caught.exception.detail)
        self.assertEqual(list(outside.iterdir()), [])


def _can_sandbox() -> str | None:
    """Why the real sandbox test cannot run here, or None. Only an absent
    sandbox-exec or an already-confined process (sandboxes do not nest) skips."""
    if sys.platform != "darwin" or not Path(L.SANDBOX_EXEC).exists():
        return "sandbox-exec is macOS-only"
    probe = subprocess.run([L.SANDBOX_EXEC, "-p", "(version 1)(allow default)", "/usr/bin/true"],
                           capture_output=True, text=True)
    if probe.returncode == 71 and "sandbox_apply: Operation not permitted" in probe.stderr:
        return "already inside a sandbox; sandboxes do not nest"
    return None


@unittest.skipIf(_can_sandbox(), _can_sandbox() or "")
class TestRealSandbox(unittest.TestCase):
    """F1, measured: a confined command cannot write outside, reach the network,
    read a secret or see a token."""

    def test_NC_an_evidence_command_is_confined(self):
        tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(__import__("shutil").rmtree, tmp, True)
        ws = L.Workspace(tmp)
        for d in (ws.candidate, ws.scratch, ws.evidence):
            d.mkdir()
        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        self.addCleanup(listener.close)
        probe = (
            "import os, socket, sys\n"
            "def attempt(f):\n"
            "    try: f(); return 'ALLOWED'\n"
            "    except OSError: return 'denied'\n"
            f"print('inside', attempt(lambda: open('inside.txt', 'w').write('x')))\n"
            f"print('evidence', attempt(lambda: open({str(ws.evidence / 'v.json')!r}, 'w')"
            ".write('x')))\n"
            f"print('network', attempt(lambda: socket.create_connection("
            f"('127.0.0.1', {listener.getsockname()[1]}), timeout=3)))\n"
            f"print('secret', attempt(lambda: open({str(L.Path.home() / '.ssh' / 'x')!r})))\n"
            "print('token', os.environ.get('GH_TOKEN', 'absent'))\n")
        m = L.LocalManager(REPO, str(tmp), PR, WHO)
        with mock.patch.dict(os.environ, {"GH_TOKEN": "sekrit"}):
            code, out = m._confined_exit([sys.executable, "-c", probe], str(ws.candidate), ws)
        self.assertEqual(code, 0, out)
        lines = dict(line.split(" ", 1) for line in out.splitlines() if " " in line)
        self.assertEqual(lines.get("inside"), "ALLOWED", out)
        self.assertEqual(lines.get("evidence"), "denied", out)
        self.assertEqual(lines.get("network"), "denied", out)
        self.assertEqual(lines.get("token"), "absent", out)
        self.assertNotEqual(lines.get("secret"), "ALLOWED", out)
        self.assertFalse((ws.evidence / "v.json").exists())


class TestClaudeReviewerSettings(unittest.TestCase):
    """F2: the filesystem layer, not the tool list, keeps Claude from writing."""

    def test_the_whole_workspace_is_write_denied_and_secrets_unreadable(self):
        ws = L.Workspace(Path("/private/tmp/agent-bus-manager-x"))
        settings = L.LocalManager(REPO, "/tmp/repo", PR, WHO).claude_settings(ws)
        self.assertEqual(settings["sandbox"]["filesystem"]["denyWrite"], [str(ws.root)])
        self.assertIn(str(Path.home().resolve() / ".config/gh"),
                      settings["sandbox"]["filesystem"]["denyRead"])
        self.assertIs(settings["sandbox"]["enabled"], True)
        self.assertIs(settings["sandbox"]["failIfUnavailable"], True)
        self.assertIs(settings["sandbox"]["allowUnsandboxedCommands"], False)
        for tool in ("Edit", "Write", "NotebookEdit"):
            self.assertIn(tool, settings["permissions"]["deny"])
        # The review clone is readable by Bash, and it lies under the denied root;
        # no rule grants writing anywhere.
        self.assertEqual(settings["permissions"]["additionalDirectories"], [str(ws.review)])
        self.assertIn(ws.root, ws.review.parents)
        self.assertFalse([r for r in settings["permissions"]["allow"]
                          if r.startswith(("Edit", "Write"))])
        self.assertNotIn("allowWrite", settings["sandbox"]["filesystem"])


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
        text = " ".join((ROOT / "CLAUDE.md").read_text(encoding="utf-8").split())
        self.assertIn("whichever model did a task, the OTHER one (Claude Code or Codex) "
                      "reviews it", text)
        self.assertIn("No model accepts its own work.", text)
        self.assertIn("the conflict first goes to the other model for analysis", text)
        self.assertIn("Captain-owned decisions are recorded and batched", text)
        self.assertNotIn("**Manager** — ChatGPT", text)

    def test_F7_agent_bus_md_states_the_reviewer_policy(self):
        text = " ".join((ROOT / "refoundation" / "AGENT-BUS.md")
                        .read_text(encoding="utf-8").split())
        self.assertIn("An eligible reviewer out of capacity is a wait, retried next pass",
                      text)
        self.assertIn("names no provider, an unknown one, or more than one", text)
        self.assertIn("the host publishes a CAPTAIN decision", text)


if __name__ == "__main__":
    unittest.main()
