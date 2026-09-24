"""Supervisor law: one action per pass, never self-driven, never silently live.

The supervisor is the only component that can spend money or change a
repository, so every test here is about restraint: what it refuses to do, how
few times it does anything, and how loudly it fails when a transport does.

Nothing in this module touches the network or invokes a model. The subprocess
boundary is injected, which is also the only way to prove that the dry run truly
does not launch Claude -- observing "no charge appeared" would not be proof.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.refoundation.agent_bus_fixtures import (
    AUTHORITY, BASE, CHECKPOINT, OTHER_SHA, TASK, TRUSTED, WAVE, comment_body, human,
)

from agent_bus import errors as E
from agent_bus.errors import BusError
from agent_bus.git_evidence import completed_units, trailers, units_in_message
from agent_bus.issue import AuthorityError, resolve_authority
from agent_bus.machine import RawComment
from agent_bus.shell import Completed
from agent_bus.supervisor import Supervisor, summarise
from agent_bus.transport import (
    HostedActionTransport, LocalClaudeTransport, session_id, worker_brief,
)

REPO = "MTJawnny/mtjawnny-pipeline"
REPO_PATH = "/tmp/repo"
RESOLVED_REPO = str(Path(REPO_PATH).resolve())
BRANCH = "infra/agent-bus-v1"
COMMAND = dict(kind="WAVE_COMMAND", actor="MANAGER", message_id="m-command-0001")
RESULT = dict(kind="WAVE_RESULT", actor="WORKER", message_id="w-result-0001",
              parent="m-command-0001")
PROGRESS = dict(kind="WAVE_PROGRESS", actor="WORKER", message_id="w-progress-0001",
                parent="m-command-0001")

CHECKPOINT_COMMENT = (
    "```yaml\n"
    "schema: mtj-checkpoint/2\n"
    f"h: {BASE}\n"
    f"a: {TASK}\n"
    "next: CLAUDE_EXECUTE_SELECTED_ONLY\n"
    "```\n"
)


def gh_comment(comment_id: int, body: str, author: str = "MTJawnny") -> dict:
    return {"id": comment_id, "user": {"login": author}, "body": body}


class FakeRunner:
    """A recorded subprocess boundary with just enough git and gh to be honest."""

    def __init__(self, comments, log: str = "", dirty: str = "",
                 claude: Completed | None = None, branch: str = BRANCH,
                 toplevel: str = RESOLVED_REPO, ancestor: bool = True,
                 head: str = OTHER_SHA, diff: str = ""):
        self.comments = comments
        self.log = log
        self.dirty_out = dirty
        self.claude = claude
        self.branch = branch
        self.toplevel = toplevel
        self.ancestor = ancestor
        self.head = head
        self.diff = diff
        self.calls: list[tuple[str, ...]] = []
        self.posted: list[str] = []

    def __call__(self, argv, stdin=None, timeout=None) -> Completed:
        argv = tuple(argv)
        self.calls.append(argv)
        if argv[0] == "gh":
            if any(a.startswith("body=") for a in argv):
                self.posted.append(next(a[5:] for a in argv if a.startswith("body=")))
                return Completed(argv, 0, '{"id": 1}', "")
            return Completed(argv, 0, json.dumps(self.comments), "")
        if argv[0] == "git":
            if "log" in argv:
                return Completed(argv, 0, self.log, "")
            if "diff" in argv:
                return Completed(argv, 0, self.diff, "")
            if "merge-base" in argv:
                return Completed(argv, 0 if self.ancestor else 1, "", "")
            if "--show-toplevel" in argv:
                return Completed(argv, 0, self.toplevel + "\n", "")
            if "--abbrev-ref" in argv:
                return Completed(argv, 0, self.branch + "\n", "")
            if "rev-parse" in argv:
                return Completed(argv, 0, self.head + "\n", "")
            if "status" in argv:
                return Completed(argv, 0, self.dirty_out, "")
        if argv[0] == "claude":
            if self.claude is None:
                raise AssertionError("claude was invoked during a dry run")
            return self.claude
        raise AssertionError(f"unexpected command {argv}")

    @property
    def claude_calls(self):
        return [c for c in self.calls if c[0] == "claude"]


def supervisor(runner, actor="WORKER", pr=None, trust=TRUSTED, **kw) -> Supervisor:
    return Supervisor(repo_path=REPO_PATH, repo_slug=REPO, actor=actor,
                      transport_pr=pr, trust=trust, run=runner, **kw)


def stream(*bodies) -> list[dict]:
    """A whole issue: the checkpoint that IS the authority, then the traffic.

    The checkpoint comment carries the id the fixtures pin, because a message
    citing a different checkpoint is stale by construction -- which is the point
    of the staleness tests, not an accident of the fake.
    """
    out = [gh_comment(CHECKPOINT, CHECKPOINT_COMMENT)]
    for index, body in enumerate(bodies, start=1):
        out.append(gh_comment(CHECKPOINT + index, body))
    return out


class TestAuthorityReading(unittest.TestCase):
    def test_the_latest_checkpoint_selects_the_active_task(self):
        comments = [
            RawComment("issue:1", 1, "MTJawnny", "prose"),
            RawComment("issue:1", 2, "MTJawnny",
                       CHECKPOINT_COMMENT.replace(f"a: {TASK}", "a: 111")),
            RawComment("issue:1", 3, "MTJawnny", CHECKPOINT_COMMENT),
        ]
        authority = resolve_authority(comments, 1, TRUSTED).authority
        self.assertEqual(authority.checkpoint, 3)
        self.assertEqual(authority.task, TASK)
        self.assertEqual(authority.accepted_head, BASE)

    def test_a_checkpoint_is_latest_not_most_accepting(self):
        # The later checkpoint leaves the head UNCHANGED and selects a repair
        # task. It still wins, because it is the latest.
        repair = CHECKPOINT_COMMENT.replace(f"a: {TASK}", "a: 999")
        comments = [RawComment("issue:1", 2, "MTJawnny", CHECKPOINT_COMMENT),
                    RawComment("issue:1", 5, "MTJawnny", repair)]
        self.assertEqual(resolve_authority(comments, 1, TRUSTED).authority.task, 999)

    def test_an_issue_with_no_checkpoint_halts_loudly(self):
        with self.assertRaises(AuthorityError):
            resolve_authority([RawComment("issue:1", 1, "MTJawnny", "no checkpoint here")],
                              1, TRUSTED)

    def test_a_checkpoint_missing_h_or_a_halts_loudly(self):
        broken = "```yaml\nschema: mtj-checkpoint/2\nnext: SOMETHING\n```"
        with self.assertRaises(AuthorityError):
            resolve_authority([RawComment("issue:1", 1, "MTJawnny", broken)], 1, TRUSTED)

    def test_a_checkpoint_whose_head_is_not_a_sha_halts_loudly(self):
        broken = CHECKPOINT_COMMENT.replace(BASE, "the-latest-commit")
        with self.assertRaises(AuthorityError):
            resolve_authority([RawComment("issue:1", 1, "MTJawnny", broken)], 1, TRUSTED)


class TestPollingRestraint(unittest.TestCase):
    def test_a_stream_of_human_comments_produces_no_action(self):
        runner = FakeRunner(stream("looks good", "@claude can you rerun the gate?"))
        report = supervisor(runner).poll_once()
        self.assertEqual(report["action"], "NONE")
        self.assertEqual(report["reason"], E.NOTHING_ACTIONABLE)
        self.assertEqual(runner.claude_calls, [])

    def test_a_valid_command_produces_exactly_one_dry_run_dispatch(self):
        runner = FakeRunner(stream(comment_body(**COMMAND)))
        report = supervisor(runner).poll_once()
        self.assertEqual(report["action"], "DISPATCH_DRY_RUN")
        self.assertEqual(report["selected"], "m-command-0001")
        self.assertEqual(report["resume"]["runnable"], ["U1", "U2"])
        self.assertEqual(report["planned_units"], ["U1", "U2"])
        self.assertEqual(runner.claude_calls, [])
        self.assertFalse(report["dispatch"]["executed"])

    def test_a_redelivered_command_dispatches_nothing_the_second_time(self):
        body = comment_body(**COMMAND)
        runner = FakeRunner(stream(body, body))
        report = supervisor(runner).poll_once()
        self.assertEqual(report["action"], "DISPATCH_DRY_RUN")
        self.assertEqual([r["code"] for r in report["rejected"]],
                         [E.DUPLICATE_MESSAGE_ID])

    def test_a_command_already_claimed_is_not_dispatched_again(self):
        runner = FakeRunner(stream(comment_body(**COMMAND), comment_body(**PROGRESS)),
                            log="u1\n\n" + trailers(WAVE, "U1") + "\n\x1e")
        report = supervisor(runner).poll_once()
        self.assertEqual(report["action"], "NONE")
        self.assertEqual(report["reason"], E.ALREADY_CLAIMED)

    def test_an_explicit_resume_may_continue_a_claimed_wave(self):
        runner = FakeRunner(stream(comment_body(**COMMAND), comment_body(**PROGRESS)),
                            log="u1\n\n" + trailers(WAVE, "U1") + "\n\x1e")
        report = supervisor(runner).poll_once(resume=True)
        self.assertEqual(report["action"], "DISPATCH_DRY_RUN")
        self.assertEqual(report["resume"]["completed"], ["U1"])
        self.assertEqual(report["resume"]["runnable"], ["U2"])
        self.assertTrue(report["dispatch"]["resumed"])

    def test_the_worker_is_never_woken_by_its_own_result(self):
        runner = FakeRunner(stream(comment_body(**COMMAND), comment_body(**RESULT)))
        report = supervisor(runner).poll_once()
        self.assertEqual(report["action"], "NONE")
        self.assertEqual(report["pending"], [])

    def test_the_manager_is_never_woken_by_its_own_command(self):
        runner = FakeRunner(stream(comment_body(**COMMAND)))
        report = supervisor(runner, actor="MANAGER").poll_once()
        self.assertEqual(report["action"], "NONE")
        self.assertEqual(report["pending"], [])

    def test_the_manager_is_woken_by_a_worker_result(self):
        runner = FakeRunner(stream(comment_body(**COMMAND), comment_body(**RESULT)))
        report = supervisor(runner, actor="MANAGER").poll_once()
        self.assertEqual(report["pending"], ["w-result-0001"])

    def test_the_two_agents_never_see_the_same_thing_to_do(self):
        runner = FakeRunner(stream(comment_body(**COMMAND), comment_body(**RESULT)))
        state = supervisor(runner).observe().state
        pending = summarise(state)
        self.assertEqual(set(pending["WORKER"]) & set(pending["MANAGER"]), set())

    def test_an_abort_is_reported_and_never_dispatched(self):
        abort = dict(kind="WAVE_ABORT", actor="MANAGER", message_id="m-abort-0001")
        runner = FakeRunner(stream(comment_body(**COMMAND), comment_body(**abort)))
        report = supervisor(runner).poll_once()
        self.assertEqual(report["action"], "NONE")
        self.assertEqual(report["reason"], E.NOTHING_ACTIONABLE)
        self.assertEqual(report["aborted"], [WAVE])
        self.assertEqual(report["pending"], [])
        self.assertEqual(runner.claude_calls, [])

    def test_a_stale_command_is_rejected_and_nothing_runs(self):
        runner = FakeRunner(stream(comment_body(checkpoint=CHECKPOINT - 5, **COMMAND)))
        report = supervisor(runner).poll_once()
        self.assertEqual(report["action"], "NONE")
        self.assertEqual([r["code"] for r in report["rejected"]], [E.STALE_AUTHORITY])

    def test_durable_git_evidence_shrinks_the_remaining_work(self):
        runner = FakeRunner(stream(comment_body(**COMMAND)),
                            log="U1 done\n\n" + trailers(WAVE, "U1") + "\n\x1e")
        report = supervisor(runner).poll_once()
        self.assertEqual(report["resume"]["completed"], ["U1"])
        self.assertEqual(report["resume"]["runnable"], ["U2"])


class TestTransport(unittest.TestCase):
    def runner(self, **kw):
        return FakeRunner(stream(comment_body(**COMMAND)), **kw)

    def test_a_dry_run_builds_the_argv_without_running_it(self):
        runner = self.runner()
        report = supervisor(runner).poll_once()
        argv = report["dispatch"]["argv"]
        self.assertEqual(argv[0], "claude")
        self.assertIn("-p", argv)
        self.assertIn("--session-id", argv)
        self.assertNotIn("--resume", argv)
        self.assertEqual(runner.claude_calls, [])

    def test_resuming_uses_the_same_session_id_as_the_first_dispatch(self):
        transport = LocalClaudeTransport(REPO_PATH)
        first = transport.argv("p", session_id(WAVE), resumed=False)
        again = transport.argv("p", session_id(WAVE), resumed=True)
        self.assertIn(session_id(WAVE), first)
        self.assertIn(session_id(WAVE), again)
        self.assertIn("--resume", again)

    def test_the_session_id_is_derived_from_the_wave_and_is_stable(self):
        self.assertEqual(session_id(WAVE), session_id(WAVE))
        self.assertNotEqual(session_id(WAVE), session_id(WAVE + ".W2"))

    def test_a_failing_transport_is_a_hard_failure_not_a_quiet_success(self):
        runner = self.runner(claude=Completed(("claude",), 7, "", "quota exhausted"))
        with self.assertRaises(BusError) as caught:
            supervisor(runner).poll_once(execute=True)
        self.assertEqual(caught.exception.code, E.TRANSPORT_FAILED)

    def test_the_hosted_action_transport_refuses_instead_of_pretending(self):
        transport = HostedActionTransport(missing=("ANTHROPIC_API_KEY", "default-branch workflow"))
        sup = supervisor(self.runner())
        sup.transport = transport
        with self.assertRaises(BusError) as caught:
            sup.poll_once()
        self.assertEqual(caught.exception.code, E.TRANSPORT_FAILED)
        self.assertIn("ANTHROPIC_API_KEY", caught.exception.detail)

    def test_the_brief_carries_the_command_verbatim_not_a_summary(self):
        observation = supervisor(self.runner()).observe()
        envelope = observation.state.pending_for("WORKER")[0]
        plan = observation.state.waves[WAVE].plan
        brief = worker_brief(envelope, plan, ["U1"], REPO_PATH, queue=["U2"])
        self.assertIn(envelope.render().strip(), brief)
        self.assertIn("Issue #1 remains the only task", brief)
        self.assertIn("Finishing a unit is NOT a stop condition", brief)
        self.assertIn("Still queued after this invocation: U2", brief)


class TestGitEvidence(unittest.TestCase):
    def test_a_trailer_names_one_unit_of_one_wave(self):
        message = "S1: do the thing\n\n" + trailers(WAVE, "U1")
        self.assertEqual(units_in_message(message, WAVE), ["U1"])

    def test_a_trailer_for_another_wave_is_not_counted(self):
        message = "S1\n\n" + trailers("INFRA.OTHER.W2", "U1")
        self.assertEqual(units_in_message(message, WAVE), [])

    def test_units_are_deduplicated_across_commits_in_order(self):
        runner = FakeRunner([], log="a\n\n" + trailers(WAVE, "U1") + "\n\x1e"
                                    "b\n\n" + trailers(WAVE, "U1") + "\n\x1e"
                                    "c\n\n" + trailers(WAVE, "U2") + "\n\x1e")
        self.assertEqual(completed_units(REPO_PATH, WAVE, BASE, run=runner),
                         ["U1", "U2"])

    def test_prose_that_merely_mentions_a_unit_is_not_a_claim(self):
        self.assertEqual(units_in_message(f"I finished U1 of {WAVE}, honest", WAVE), [])


if __name__ == "__main__":
    unittest.main()
