"""The Worker checkout owns its ref store; stop means stop; install refuses a crash loop.

Incident 2026-09-29 (C03-REGIONS, Issue #1 evidence 5896720246): the watcher ran
in a linked worktree of the operator's repository. The operator committed on a
new branch in a sibling worktree mid-unit; the host's every-ref proof saw the
branch appear and failed the Worker's good unit as BUS_PROVIDER_GIT_MUTATION.
Stopping the service then failed twice: launchd's unconditional KeepAlive undid
`watch stop`, and the stop waited out the idle interval. The service had also
been installed without `--pr`/`--trusted` and crash-looped. Each is pinned here.
"""

from __future__ import annotations

import subprocess
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

from agent_bus import errors as E
from agent_bus import finalize as F
from agent_bus import preflight as PF
from agent_bus import watcher as W
from agent_bus.errors import BusError
from agent_bus.shell import Runner


def git(*argv, cwd):
    return subprocess.run(["git", *argv], cwd=cwd, check=True, capture_output=True,
                          text=True).stdout.strip()


class Repos(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(__import__("shutil").rmtree, self.tmp, True)
        self.main = self.tmp / "main"
        self.main.mkdir()
        git("init", "-q", "-b", "work", cwd=self.main)
        (self.main / "README").write_text("x\n")
        git("add", "README", cwd=self.main)
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "c",
            cwd=self.main)

    def worktree(self, name="side"):
        path = self.tmp / name
        git("worktree", "add", "-q", "-b", name, str(path), cwd=self.main)
        return path

    def clone(self, name="runner"):
        path = self.tmp / name
        git("clone", "-q", "--no-hardlinks", str(self.main), str(path), cwd=self.tmp)
        return path


class TestSharing(Repos):
    def test_a_standalone_repository_or_clone_is_exclusive(self):
        self.assertEqual(PF.sharing(str(self.main), Runner()), [])
        self.assertEqual(PF.sharing(str(self.clone()), Runner()), [])
        PF.require_exclusive(str(self.clone("runner2")), Runner())

    def test_NC_a_linked_worktree_is_shared(self):
        side = self.worktree()
        self.assertTrue(PF.sharing(str(side), Runner()))
        with self.assertRaises(BusError) as caught:
            PF.require_exclusive(str(side), Runner())
        self.assertEqual(caught.exception.code, E.CHECKOUT_SHARED)
        self.assertIn("git clone", caught.exception.detail)

    def test_NC_the_main_checkout_of_a_repo_with_worktrees_is_shared(self):
        self.worktree()
        self.assertTrue(PF.sharing(str(self.main), Runner()))


class TestAttribution(Repos):
    """A ref that moves is the provider's only when nothing else shares the store."""

    def test_the_incident_is_reported_as_unattributable_not_as_the_provider(self):
        runner = Runner()
        side = self.worktree()               # the operator's sibling worktree
        before = F.snapshot(str(self.main), runner)
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
            "--allow-empty", "-m", "operator work", cwd=side)
        after = F.snapshot(str(self.main), runner)
        what = F.git_mutations(before, after, ())
        self.assertTrue(any("refs changed" in w for w in what))
        code, detail = F.mutation_failure(str(self.main), "claude", "U1", what, runner)
        self.assertEqual(code, E.CHECKOUT_SHARED)
        self.assertIn("cannot be attributed to claude", detail)

    def test_NC_in_an_exclusive_clone_a_ref_move_is_still_the_providers(self):
        runner = Runner()
        clone = self.clone()
        before = F.snapshot(str(clone), runner)
        git("branch", "planted", cwd=clone)
        what = F.git_mutations(before, F.snapshot(str(clone), runner), ())
        code, _ = F.mutation_failure(str(clone), "claude", "U1", what, runner)
        self.assertEqual(code, E.PROVIDER_GIT_MUTATION)


class TestStopMeansStop(unittest.TestCase):
    def test_the_service_restarts_only_after_a_crash(self):
        document = W.plist(["python3", "-m", "agent_bus"])
        self.assertIn("<key>KeepAlive</key>\n    <dict>\n      <key>SuccessfulExit</key>\n"
                      "      <false/>", document)
        self.assertNotIn("<key>KeepAlive</key>\n    <true/>", document)
        self.assertIn(f"<key>ExitTimeOut</key>\n    <integer>{W.EXIT_TIMEOUT}</integer>",
                      document)
        self.assertGreaterEqual(W.EXIT_TIMEOUT, 3600)   # a unit or review finishes first

    def test_a_stop_ends_the_idle_wait_at_once(self):
        class Idle:
            polls = 0
            def poll_once(self, execute=False):
                Idle.polls += 1
                return {"action": "NONE"}
        watch = W.Watcher(Idle(), interval=3600, emit=lambda e: None,
                          clock=lambda: "t")
        thread = threading.Thread(target=watch.run, daemon=True)
        thread.start()
        for _ in range(200):
            if Idle.polls:
                break
            threading.Event().wait(0.01)
        watch.request_stop()
        thread.join(timeout=5)
        self.assertFalse(thread.is_alive(), "the stop waited out the interval")
        self.assertEqual(Idle.polls, 1)

    def test_NC_a_stop_never_cuts_a_cycle_short(self):
        events = []
        class Busy:
            def __init__(self, watch_ref):
                self.ref = watch_ref
            def poll_once(self, execute=False):
                self.ref[0].request_stop()         # stop arrives mid-unit
                events.append("unit finished")
                return {"action": "WAVE_RAN"}
        ref = []
        watch = W.Watcher(Busy(ref), interval=60, emit=lambda e: events.append("emitted"),
                          clock=lambda: "t")
        ref.append(watch)
        watch.run()
        self.assertEqual(events, ["unit finished", "emitted"])


class TestInstallRefusesACrashLoop(Repos):
    def args(self, repo, *argv):
        from agent_bus.cli import build_parser
        return build_parser()[0].parse_args(["--repo-path", str(repo), *argv])

    def install(self, repo, *argv):
        from agent_bus import cli
        with mock.patch.object(cli.watcher_module, "install",
                               lambda *a, **k: {"installed": True}), \
                mock.patch.dict("os.environ", {"MTJ_AGENT_BUS_TRUSTED": "",
                                               "MTJ_AGENT_BUS_CONFIG": str(self.tmp / "none")}):
            return cli._watch(self.args(repo, *argv))

    def test_NC_a_manager_service_without_pr_or_trusted_is_refused(self):
        for extra in ((), ("--pr", "76"), ("--trusted", "MTJawnny")):
            with self.subTest(extra=extra), self.assertRaises(BusError) as caught:
                self.install(self.main, *extra, "watch", "install", "--manager")
            self.assertEqual(caught.exception.code, E.BAD_VALUE)

    def test_NC_an_armed_service_with_no_trusted_speaker_is_refused(self):
        with self.assertRaises(BusError) as caught:
            self.install(self.main, "watch", "install", "--execute")
        self.assertEqual(caught.exception.code, E.TRUST_NOT_CONFIGURED)

    def test_NC_an_armed_service_in_a_linked_worktree_is_refused(self):
        with self.assertRaises(BusError) as caught:
            self.install(self.worktree(), "--trusted", "MTJawnny", "--providers", "claude",
                         "watch", "install", "--execute")
        self.assertEqual(caught.exception.code, E.CHECKOUT_SHARED)

    def test_an_armed_service_in_its_own_clone_installs(self):
        out = self.install(self.clone(), "--trusted", "MTJawnny", "--providers", "claude",
                           "--pr", "76", "watch", "install", "--execute", "--manager")
        self.assertEqual(out, {"installed": True})


if __name__ == "__main__":
    unittest.main()


class TestEveryUnitReprovesExclusivity(unittest.TestCase):
    def test_NC_a_worktree_added_mid_wave_stops_the_next_unit_before_dispatch(self):
        from tests.refoundation.test_agent_bus_provider_failover import armed, ok, repo
        fake = repo(ok("claude", "U1"), ok("claude", "U2"))

        class Grows(list):
            """One worktree until a provider has run; then a sibling appears."""
            def __bool__(self):
                return True
            def __iter__(self):
                return iter(["/tmp/repo"] + (["/tmp/side"] if fake.provider_calls else []))
        fake.worktrees = Grows()
        with self.assertRaises(BusError) as caught:
            armed(fake, order=("claude",)).poll_once(execute=True)
        self.assertEqual(caught.exception.code, E.CHECKOUT_SHARED)
        self.assertEqual(len(fake.provider_calls), 1)      # U2 never dispatched

    def test_NC_wave_preflight_refuses_a_shared_checkout_even_on_a_dry_run(self):
        from tests.refoundation.test_agent_bus_provider_failover import armed, ok, repo
        fake = repo(ok("claude", "U1"))
        fake.worktrees = ["/tmp/repo", "/tmp/side"]
        report = armed(fake, order=("claude",)).poll_once(execute=False)
        codes = [p["code"] for p in report["preflight"]["problems"]]
        self.assertIn(E.CHECKOUT_SHARED, codes)
        self.assertEqual(fake.provider_calls, [])


# ---------------------------------------------------------------------------
# CU1 repair (Codex review 5897267559): the Worker side of the usage budget
# ---------------------------------------------------------------------------
def codex_says(text: str) -> str:
    import json
    return "\n".join(json.dumps(e) for e in (
        {"type": "thread.started", "thread_id": "th-codex-1"},
        {"type": "item.completed", "item": {"id": "final", "type": "agent_message",
                                            "text": text}},
        {"type": "turn.completed", "usage": {}})) + "\n"


HANDOFF_TEXT = ("Stopping for usage before U1.\n\nUSAGE HANDOFF: read the objective; "
                "nothing edited; next step: write agent_bus/x.py.\n\n"
                '```mtj-evidence\n{"changed": [], "status": "STOP", "validation": []}\n```')


def at_line():
    return {"status": "HANDOFF", "windows": {"five_hour": {"used_percent": 93.0}}}


class TestWorkerUsage(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(__import__("shutil").rmtree, self.dir, True)

    def armed(self, fake, order, usage=None):
        from tests.refoundation.test_agent_bus_provider_failover import armed
        sup = armed(fake, order=order, max_units=1)    # the fixture wave has U1 and U2
        sup.transport.usage = usage
        sup.transport.handoff_dir = str(self.dir)
        return sup

    def test_a_fallback_codex_at_the_handoff_line_is_never_launched(self):
        from tests.refoundation.test_agent_bus_provider_failover import claude_quota, repo
        fake = repo(claude_quota())
        with self.assertRaises(BusError) as caught:
            self.armed(fake, ("claude", "codex"), at_line).poll_once(execute=True)
        self.assertEqual(caught.exception.code, E.PROVIDERS_EXHAUSTED)
        self.assertEqual(fake.providers_invoked, ["claude"])   # codex never ran
        self.assertIn("handoff line", caught.exception.detail)
        self.assertEqual(fake.posted, [])                      # a wait, nothing claimed

    def test_a_gated_first_codex_hands_the_unit_to_claude(self):
        from tests.refoundation.test_agent_bus_provider_failover import ok, repo
        fake = repo(ok("claude", "U1"))
        report = self.armed(fake, ("codex", "claude"), at_line).poll_once(execute=True)
        self.assertEqual(fake.providers_invoked, ["claude"])
        self.assertEqual(report["dispatches"][0]["provider"], "claude")

    def test_a_clean_usage_handoff_is_a_wait_and_seeds_the_next_session(self):
        from tests.refoundation.test_agent_bus_provider_failover import Step, ok, repo
        fake = repo(Step("codex", stdout=codex_says(HANDOFF_TEXT)))
        with self.assertRaises(BusError) as caught:
            self.armed(fake, ("codex",)).poll_once(execute=True)
        self.assertEqual(caught.exception.code, E.PROVIDERS_EXHAUSTED)
        self.assertEqual(fake.posted, [])                      # not a FAILED unit
        [kept] = list(self.dir.glob("worker-*-U1.md"))
        self.assertIn("next step: write agent_bus/x.py", kept.read_text())
        # Next cycle: a fresh session gets the notes, finishes, and the note retires.
        fake.script.append(ok("codex", "U1"))
        report = self.armed(fake, ("codex",)).poll_once(execute=True)
        self.assertEqual(report["action"], "WAVE_RAN")
        self.assertIn("An earlier session stopped this same unit", fake.provider_calls[-1][-1])
        self.assertIn("next step: write agent_bus/x.py", fake.provider_calls[-1][-1])
        self.assertFalse(kept.exists())
        self.assertTrue((self.dir / "done" / kept.name).exists())

    def test_a_clean_usage_handoff_fails_over_to_claude_with_the_notes(self):
        from tests.refoundation.test_agent_bus_provider_failover import Step, ok, repo
        fake = repo(Step("codex", stdout=codex_says(HANDOFF_TEXT)), ok("claude", "U1"))
        report = self.armed(fake, ("codex", "claude")).poll_once(execute=True)
        self.assertEqual(report["action"], "WAVE_RAN")
        self.assertEqual(fake.providers_invoked, ["codex", "claude"])
        claude = fake.provider_calls[-1]
        brief = claude[claude.index("-p") + 1]
        self.assertIn("An earlier session stopped this same unit", brief)
        self.assertIn("next step: write agent_bus/x.py", brief)
        self.assertEqual(brief.count("USAGE HANDOFF:"), 1)     # notes once, not stacked

    def test_NC_a_handoff_over_a_changed_tree_is_still_a_failed_unit(self):
        from tests.refoundation.test_agent_bus_provider_failover import Step, repo
        fake = repo(Step("codex", stdout=codex_says(HANDOFF_TEXT), dirty=("agent_bus/x.py",)))
        report = self.armed(fake, ("codex", "claude")).poll_once(execute=True)
        self.assertEqual(report["action"], "WAVE_STOPPED")
        self.assertEqual(fake.providers_invoked, ["codex"])    # never handed on
        self.assertEqual(list(self.dir.glob("worker-*")), [])

    def test_NC_a_plain_stop_without_the_marker_is_still_a_failed_unit(self):
        from tests.refoundation.test_agent_bus_provider_failover import Step, repo
        plain = HANDOFF_TEXT.replace("USAGE HANDOFF:", "Reason:")
        fake = repo(Step("codex", stdout=codex_says(plain)))
        report = self.armed(fake, ("codex", "claude")).poll_once(execute=True)
        self.assertEqual(report["action"], "WAVE_STOPPED")
        self.assertEqual(report["reason"], E.WORKER_STOPPED)
