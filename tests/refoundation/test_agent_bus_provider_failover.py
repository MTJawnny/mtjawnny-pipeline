"""Local Worker provider failover: move to the next provider only when it is PROVEN safe.

The one positive path is narrow on purpose: a classified quota/capacity failure,
from a structured shape in stdout or stderr, after which git proves the attempt
left no commit and a clean tree on the same branch, and a live re-read proves
the command is still the selected one. Then, and only then, the SAME unit goes
once to the next provider, in that provider's own fresh session, and the normal
unit enforcement runs on whatever it did.

Everything else in this module is a negative control. No network, no model, no
`~/.claude`: the subprocess boundary is a faithful git model plus a script of
what each provider invocation did.
"""

from __future__ import annotations

import dataclasses
import inspect as pyinspect
import json
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from tests.refoundation.agent_bus_fixtures import (
    BASE, CHECKPOINT, TASK, TRUSTED, WAVE, comment_body,
)
from tests.refoundation.agent_bus_repo_fake import FakeRepo

from agent_bus import errors as E
from agent_bus import providers as P
from agent_bus.errors import BusError
from agent_bus.git_evidence import trailers
from agent_bus.shell import Completed
from agent_bus.supervisor import Supervisor
from agent_bus.transport import session_id
from agent_bus.watcher import QUOTA_RE

REPO = "MTJawnny/mtjawnny-pipeline"
REPO_PATH = "/tmp/repo"
COMMAND = dict(kind="WAVE_COMMAND", actor="MANAGER", message_id="m-command-0001")
CHECKPOINT_COMMENT = (
    "```yaml\nschema: mtj-checkpoint/2\n"
    f"h: {BASE}\na: {TASK}\nnext: CLAUDE_EXECUTE_SELECTED_ONLY\n```\n"
)

CLAUDE_OK = json.dumps({"type": "result", "subtype": "success", "is_error": False,
                        "result": "done"})
CODEX_OK = ('{"type": "thread.started", "thread_id": "th-codex-1"}\n'
            '{"type": "turn.completed", "usage": {}}\n')


def claude_result(text: str, **extra) -> str:
    return json.dumps({"type": "result", "subtype": "success", "is_error": True,
                       "result": text, **extra})


def api_error(status: int, kind: str) -> str:
    return f"API Error: {status} " + json.dumps(
        {"type": "error", "error": {"type": kind, "message": "try later"}})


def codex_failed(message: str, event: str = "turn.failed") -> str:
    failure = ({"type": "turn.failed", "error": {"message": message}} if event == "turn.failed"
               else {"type": "error", "message": message})
    return ('{"type": "thread.started", "thread_id": "th-codex-9"}\n'
            + json.dumps(failure) + "\n")


def done_message(unit: str) -> str:
    return f"{unit}: work\n\n" + trailers(WAVE, unit)


@dataclass
class Step:
    """What one provider invocation did, and what it printed."""

    provider: str
    rc: int = 0
    stdout: str | None = None
    stderr: str = ""
    message: str | None = None
    paths: tuple[str, ...] = ()
    dirty: tuple[str, ...] = ()
    raises: str | None = None
    then: Callable | None = None


def ok(provider: str, unit: str = "U1", *paths: str) -> Step:
    return Step(provider, message=done_message(unit), paths=paths or ("agent_bus/x.py",))


def claude_quota(**kw) -> Step:
    return Step("claude", rc=1,
                stdout=claude_result("Claude AI usage limit reached|1790000000"), **kw)


def codex_quota(**kw) -> Step:
    return Step("codex", rc=1, stdout=codex_failed("You've hit your usage limit. Try later."),
                **kw)


class ProviderRepo(FakeRepo):
    """The git model, plus scripted `claude` and `codex` invocations in strict order."""

    def __call__(self, argv, stdin=None, timeout=None) -> Completed:
        argv = tuple(argv)
        if argv[0] not in P.PROVIDERS:
            return super().__call__(argv, stdin, timeout)
        self.calls.append(argv)
        if self._next >= len(self.script):
            raise AssertionError(f"unscripted {argv[0]} invocation")
        step: Step = self.script[self._next]
        self._next += 1
        if step.provider != argv[0]:
            raise AssertionError(f"expected {step.provider}, {argv[0]} was invoked")
        if step.raises:
            raise BusError(step.raises, f"{argv[0]!r} could not be run")
        if step.message is not None:
            self._commit(step)
        self.dirty = tuple(step.dirty)
        if step.then:
            step.then(self)
        default = CLAUDE_OK if argv[0] == "claude" else CODEX_OK
        return Completed(argv, step.rc, default if step.stdout is None else step.stdout,
                         step.stderr)

    @property
    def provider_calls(self) -> list[tuple[str, ...]]:
        return [c for c in self.calls if c[0] in P.PROVIDERS]

    @property
    def providers_invoked(self) -> list[str]:
        return [c[0] for c in self.provider_calls]


def gh(comment_id: int, body: str) -> dict:
    return {"id": comment_id, "user": {"login": "MTJawnny"}, "body": body}


def stream(*bodies: str) -> list[dict]:
    return [gh(CHECKPOINT, CHECKPOINT_COMMENT)] + [
        gh(CHECKPOINT + i, b) for i, b in enumerate(bodies, start=1)]


def repo(*steps: Step) -> ProviderRepo:
    return ProviderRepo(stream(comment_body(**COMMAND)), script=list(steps))


def armed(fake: ProviderRepo, order=("claude", "codex"), probe: bool = True,
          **kw) -> Supervisor:
    sup = Supervisor(repo_path=REPO_PATH, repo_slug=REPO, trust=TRUSTED, run=fake,
                     clock=lambda: __import__("datetime").datetime(2026, 9, 25, 18, 0, 0),
                     **kw)
    providers = P.build_providers(P.ProviderOrder(tuple(order), "test"), REPO_PATH)
    sup.transport = P.ProviderFailoverTransport(
        REPO_PATH, providers, run=fake,
        authority_probe=P.live_authority_probe(sup.observe) if probe else None)
    return sup


def move_authority(fake: ProviderRepo) -> None:
    """Somebody posts a newer checkpoint that selects a different task."""
    fake.comments.append(gh(CHECKPOINT + 50,
                            CHECKPOINT_COMMENT.replace(f"a: {TASK}", "a: 4242")))


def completed(rc: int, stdout: str = "", stderr: str = "") -> Completed:
    return Completed(("x",), rc, stdout, stderr)


# ---------------------------------------------------------------------------
# 1. Classification: structured shapes only
# ---------------------------------------------------------------------------

class TestClaudeClassification(unittest.TestCase):
    def status(self, rc, stdout="", stderr=""):
        return P.classify_claude(completed(rc, stdout, stderr)).status

    def test_the_usage_limit_marker_in_an_error_result_is_capacity(self):
        self.assertEqual(self.status(1, claude_result("Claude AI usage limit reached|1790000000")),
                         P.CAPACITY)

    def test_an_error_result_with_api_status_429_or_529_is_capacity(self):
        for status in (429, 529):
            self.assertEqual(self.status(1, claude_result("x", api_error_status=status)),
                             P.CAPACITY)

    def test_a_typed_rate_limit_or_overload_api_error_is_capacity(self):
        self.assertEqual(self.status(1, stderr=api_error(429, "rate_limit_error")), P.CAPACITY)
        self.assertEqual(self.status(1, stderr=api_error(529, "overloaded_error")), P.CAPACITY)
        self.assertEqual(self.status(1, claude_result(api_error(429, "rate_limit_error"))),
                         P.CAPACITY)

    def test_NC_a_429_whose_typed_body_is_not_a_capacity_error_is_unclassified(self):
        self.assertEqual(self.status(1, stderr=api_error(429, "invalid_request_error")),
                         P.FAILED)
        self.assertEqual(self.status(1, stderr=api_error(500, "rate_limit_error")), P.FAILED)

    def test_NC_quota_like_prose_on_stderr_is_unclassified(self):
        prose = "quota exhausted: 429 Too Many Requests, rate limit, usage limit reached"
        self.assertEqual(self.status(1, stderr=prose), P.FAILED)

    def test_NC_quota_like_prose_in_a_result_is_unclassified(self):
        self.assertEqual(self.status(1, claude_result("I think we hit a quota (429) limit")),
                         P.FAILED)
        self.assertEqual(self.status(
            1, claude_result("see: Claude AI usage limit reached|1790000000 earlier")), P.FAILED)

    def test_NC_the_marker_in_a_result_that_is_not_an_error_is_unclassified(self):
        body = json.dumps({"type": "result", "is_error": False,
                           "result": "Claude AI usage limit reached|1790000000"})
        self.assertEqual(self.status(1, body), P.FAILED)

    def test_NC_the_marker_outside_a_json_result_is_unclassified(self):
        self.assertEqual(self.status(1, "Claude AI usage limit reached|1790000000\n{}"),
                         P.FAILED)

    def test_NC_a_capacity_result_mixed_into_other_stdout_is_unclassified(self):
        marker = claude_result("Claude AI usage limit reached|1790000000")
        self.assertEqual(self.status(1, "some prose first\n" + marker), P.FAILED)

    def test_NC_a_zero_exit_is_never_a_failure_whatever_it_printed(self):
        self.assertEqual(self.status(0, claude_result("Claude AI usage limit reached|1")),
                         P.OK)


class TestCodexClassification(unittest.TestCase):
    def status(self, rc, stdout="", stderr=""):
        return P.classify_codex(completed(rc, stdout, stderr)).status

    def test_a_usage_limit_turn_failure_is_capacity(self):
        self.assertEqual(self.status(1, codex_failed("You've hit your usage limit. Upgrade.")),
                         P.CAPACITY)

    def test_quota_retry_429_and_model_capacity_error_events_are_capacity(self):
        for message in ("Quota exceeded. Check your plan and billing details.",
                        "exceeded retry limit, last status: 429 Too Many Requests",
                        "Selected model is at capacity. Please try a different model."):
            self.assertEqual(self.status(1, codex_failed(message, event="error")), P.CAPACITY)

    def test_a_capacity_event_on_stderr_is_capacity_too(self):
        self.assertEqual(self.status(1, stderr=codex_failed("You've hit your usage limit.")),
                         P.CAPACITY)

    def test_NC_the_same_words_in_an_agent_message_are_not_an_event(self):
        message = json.dumps({"type": "item.completed", "item": {
            "type": "agent_message", "text": "You've hit your usage limit."}})
        self.assertEqual(self.status(1, message), P.FAILED)

    def test_NC_the_same_words_as_plain_stderr_prose_are_unclassified(self):
        self.assertEqual(self.status(1, stderr="You've hit your usage limit."), P.FAILED)

    def test_NC_an_error_event_with_any_other_message_is_unclassified(self):
        self.assertEqual(self.status(1, codex_failed("stream disconnected: we hit a quota")),
                         P.FAILED)

    def test_NC_a_zero_exit_is_never_a_failure(self):
        self.assertEqual(self.status(0, codex_failed("You've hit your usage limit.")), P.OK)

    def test_the_thread_id_is_read_from_codex_own_event(self):
        self.assertEqual(P.codex_thread_id(CODEX_OK), "th-codex-1")
        self.assertIsNone(P.codex_thread_id("thread_id: th-prose"))


# ---------------------------------------------------------------------------
# 2. Sessions are per-provider namespaces
# ---------------------------------------------------------------------------

class TestSessions(unittest.TestCase):
    def setUp(self):
        self.claude = P.ClaudeProvider(REPO_PATH)
        self.codex = P.CodexProvider(REPO_PATH)

    def test_the_claude_namespace_keeps_the_pre_existing_session_ids(self):
        self.assertEqual(self.claude.fresh_session(WAVE, 0).id, session_id(WAVE))
        self.assertEqual(self.claude.durable_session(WAVE).id, session_id(WAVE))

    def test_a_second_fresh_claude_session_never_reuses_the_first_id(self):
        self.assertNotEqual(self.claude.fresh_session(WAVE, 0).id,
                            self.claude.fresh_session(WAVE, 1).id)

    def test_NC_codex_refuses_to_resume_a_claude_session(self):
        with self.assertRaises(BusError) as caught:
            self.codex.argv("p", self.claude.durable_session(WAVE))
        self.assertEqual(caught.exception.code, E.PROVIDER_SESSION_MISMATCH)

    def test_NC_claude_refuses_to_resume_a_codex_session(self):
        with self.assertRaises(BusError) as caught:
            self.claude.argv("p", P.SessionRef("codex", "th-codex-1", True))
        self.assertEqual(caught.exception.code, E.PROVIDER_SESSION_MISMATCH)

    def test_NC_codex_has_no_durable_session_to_guess(self):
        self.assertIsNone(self.codex.durable_session(WAVE))
        with self.assertRaises(BusError) as caught:
            self.codex.argv("p", P.SessionRef("codex", None, True))
        self.assertEqual(caught.exception.code, E.PROVIDER_SESSION_MISMATCH)

    def test_codex_runs_non_interactive_in_the_workspace_write_sandbox_only(self):
        argv = self.codex.argv("brief", self.codex.fresh_session(WAVE, 0))
        self.assertEqual(argv[:2], ("codex", "exec"))
        self.assertEqual(argv[argv.index("--sandbox") + 1], "workspace-write")
        self.assertEqual(argv[argv.index("--cd") + 1], REPO_PATH)
        self.assertIn("--json", argv)
        self.assertNotIn("resume", argv)
        self.assertFalse(any("danger" in a or "bypass" in a for a in argv))
        self.assertEqual(argv[-1], "brief")

    def test_a_codex_resume_names_the_thread_codex_assigned(self):
        argv = self.codex.argv("brief", P.SessionRef("codex", "th-codex-1", True))
        self.assertEqual(argv[argv.index("resume") + 1], "th-codex-1")


# ---------------------------------------------------------------------------
# 3. Provider order is operator configuration, outside the repository
# ---------------------------------------------------------------------------

class TestProviderOrder(unittest.TestCase):
    def test_the_four_supported_orders(self):
        for spec, order in (("claude,codex", ("claude", "codex")),
                            ("codex,claude", ("codex", "claude")),
                            ("claude", ("claude",)), ("codex", ("codex",))):
            self.assertEqual(P.parse_order(spec, "t").order, order)

    def test_NC_unknown_duplicate_and_empty_orders_are_refused(self):
        for spec in ("claude,gemini", "claude,claude", "", "claude,,codex", ["claude", 7], []):
            with self.assertRaises(BusError) as caught:
                P.parse_order(spec, "t")
            self.assertEqual(caught.exception.code, E.PROVIDER_CONFIG_INVALID, spec)

    def test_flag_then_environment_then_file_then_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "providers.json"
            config.write_text('{"order": ["codex"]}', encoding="utf-8")
            env = {P.PROVIDER_ENV_VAR: "codex,claude"}
            self.assertEqual(P.resolve_order("claude", env, config).order, ("claude",))
            self.assertEqual(P.resolve_order(None, env, config).order, ("codex", "claude"))
            self.assertEqual(P.resolve_order(None, {}, config).order, ("codex",))
            missing = Path(tmp) / "absent.json"
            default = P.resolve_order(None, {}, missing)
            self.assertEqual((default.order, default.source), (P.DEFAULT_ORDER, "default"))

    def test_NC_a_provider_file_inside_the_checkout_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "providers.json"
            config.write_text('{"order": ["codex"]}', encoding="utf-8")
            with self.assertRaises(BusError) as caught:
                P.resolve_order(None, {}, config, repo_path=tmp)
            self.assertEqual(caught.exception.code, E.PROVIDER_CONFIG_INVALID)

    def test_NC_a_malformed_provider_file_halts_instead_of_defaulting(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "providers.json"
            for text in ("not json", '{"providers": ["codex"]}', '["codex"]'):
                config.write_text(text, encoding="utf-8")
                with self.assertRaises(BusError) as caught:
                    P.resolve_order(None, {}, config)
                self.assertEqual(caught.exception.code, E.PROVIDER_CONFIG_INVALID, text)

    def test_order_resolution_reads_no_bus_surface_and_no_model_output(self):
        source = pyinspect.getsource(P.resolve_order) + pyinspect.getsource(P.parse_order)
        for forbidden in ("read_comments", "observe", "Envelope", "parse_comment",
                          "stdout", "gh", "issue", "run("):
            self.assertNotIn(forbidden, source, forbidden)

    def test_the_transport_order_is_fixed_at_construction(self):
        transport = armed(repo(), order=("codex", "claude")).transport
        self.assertEqual(transport.order, ("codex", "claude"))
        self.assertEqual(transport.name, "local-provider:codex,claude")


# ---------------------------------------------------------------------------
# 4. Failover through the supervisor, end to end
# ---------------------------------------------------------------------------

class TestFailoverPositive(unittest.TestCase):
    def test_a_classified_claude_quota_hands_the_same_unit_once_to_a_fresh_codex(self):
        fake = repo(claude_quota(), ok("codex", "U1"), ok("claude", "U2"))
        report = armed(fake).poll_once(execute=True)
        self.assertEqual(report["action"], "WAVE_RAN")
        self.assertEqual(fake.providers_invoked, ["claude", "codex", "claude"])
        first = report["dispatches"][0]
        self.assertEqual(first["provider"], "codex")
        self.assertEqual([a["provider"] for a in first["attempts"]], ["claude"])
        self.assertTrue(first["attempts"][0]["classified"])
        codex_argv = fake.provider_calls[1]
        self.assertNotIn("resume", codex_argv)
        self.assertNotIn(session_id(WAVE), codex_argv)
        # The same brief, for the same single unit, went to both providers.
        self.assertEqual(fake.provider_calls[0][2], codex_argv[-1])
        self.assertIn("  - U1:", codex_argv[-1])
        self.assertNotIn("  - U2:", codex_argv[-1])
        self.assertEqual(fake.posted_kinds(),
                         ["WAVE_PROGRESS", "WAVE_PROGRESS", "WAVE_RESULT"])

    def test_the_codex_unit_still_meets_normal_unit_enforcement(self):
        untrailed = Step("codex", message="U1: no trailers", paths=("agent_bus/x.py",))
        fake = repo(claude_quota(), untrailed)
        report = armed(fake).poll_once(execute=True)
        self.assertEqual(report["action"], "WAVE_STOPPED")
        self.assertEqual(report["reason"], E.UNIT_TRAILER_MISSING)
        self.assertEqual(fake.providers_invoked, ["claude", "codex"])

    def test_a_later_unit_resumes_the_same_providers_own_session(self):
        fake = repo(ok("codex", "U1"), ok("codex", "U2"))
        armed(fake, order=("codex", "claude")).poll_once(execute=True)
        first, second = fake.provider_calls
        self.assertNotIn("resume", first)
        self.assertEqual(second[second.index("resume") + 1], "th-codex-1")

    def test_a_later_failover_opens_codex_fresh_instead_of_resuming_claude(self):
        fake = repo(ok("claude", "U1"), claude_quota(), ok("codex", "U2"))
        report = armed(fake).poll_once(execute=True)
        self.assertEqual(report["action"], "WAVE_RAN")
        claude_first, claude_second, codex = fake.provider_calls
        self.assertIn("--session-id", claude_first)
        self.assertIn("--resume", claude_second)
        self.assertNotIn("resume", codex)
        self.assertNotIn(session_id(WAVE), codex)

    def test_after_codex_took_a_unit_claude_opens_a_new_session_not_the_failed_one(self):
        fake = repo(claude_quota(), ok("codex", "U1"), ok("claude", "U2"))
        armed(fake).poll_once(execute=True)
        first_claude, _, second_claude = fake.provider_calls
        opened = first_claude[first_claude.index("--session-id") + 1]
        self.assertIn("--session-id", second_claude)
        self.assertNotEqual(second_claude[second_claude.index("--session-id") + 1], opened)

    def test_the_order_is_obeyed_codex_first(self):
        fake = repo(codex_quota(), ok("claude", "U1"), ok("codex", "U2"))
        report = armed(fake, order=("codex", "claude")).poll_once(execute=True)
        self.assertEqual(report["action"], "WAVE_RAN")
        self.assertEqual(fake.providers_invoked, ["codex", "claude", "codex"])

    def test_a_dry_run_reports_the_order_and_plan_and_invokes_nobody(self):
        fake = repo()
        report = armed(fake).poll_once(execute=False)
        self.assertEqual(report["action"], "DISPATCH_DRY_RUN")
        self.assertEqual(report["transport"], "local-provider:claude,codex")
        self.assertEqual(report["dispatch"]["provider"], "claude")
        self.assertFalse(report["dispatch"]["executed"])
        self.assertEqual(fake.provider_calls, [])
        self.assertEqual(fake.posted, [])


class TestFailoverRefused(unittest.TestCase):
    def refused(self, fake: ProviderRepo, code: str, **kw) -> BusError:
        with self.assertRaises(BusError) as caught:
            armed(fake, **kw).poll_once(execute=True)
        self.assertEqual(caught.exception.code, code, caught.exception.detail)
        return caught.exception

    def test_NC_a_dirty_tree_is_never_handed_over(self):
        fake = repo(claude_quota(dirty=("agent_bus/half.py",)), ok("codex"))
        err = self.refused(fake, E.FAILOVER_REFUSED)
        self.assertIn("uncommitted", err.detail)
        self.assertEqual(fake.providers_invoked, ["claude"])

    def test_NC_a_commit_by_the_failed_provider_is_never_handed_over(self):
        fake = repo(claude_quota(message=done_message("U1"), paths=("agent_bus/x.py",)),
                    ok("codex"))
        err = self.refused(fake, E.FAILOVER_REFUSED)
        self.assertIn("HEAD moved", err.detail)
        self.assertEqual(fake.providers_invoked, ["claude"])

    def test_NC_a_scope_escaping_commit_by_the_failed_provider_is_never_handed_over(self):
        fake = repo(claude_quota(message="stray", paths=("pipeline/build_db.py",)),
                    ok("codex"))
        self.refused(fake, E.FAILOVER_REFUSED)
        self.assertEqual(fake.providers_invoked, ["claude"])

    def test_NC_a_scope_escape_after_a_success_stops_and_reaches_no_provider(self):
        fake = repo(ok("claude", "U1", "agent_bus/x.py", "pipeline/build_db.py"))
        report = armed(fake).poll_once(execute=True)
        self.assertEqual(report["action"], "WAVE_STOPPED")
        self.assertEqual(report["reason"], E.UNIT_SCOPE_ESCAPE)
        self.assertEqual(fake.providers_invoked, ["claude"])

    def test_NC_a_changed_branch_is_never_handed_over(self):
        fake = repo(claude_quota(then=lambda r: setattr(r, "branch", "elsewhere")),
                    ok("codex"))
        err = self.refused(fake, E.FAILOVER_REFUSED)
        self.assertIn("branch changed", err.detail)
        self.assertEqual(fake.providers_invoked, ["claude"])

    def test_NC_authority_moving_during_the_failed_attempt_stops_the_handover(self):
        fake = repo(claude_quota(then=move_authority), ok("codex"))
        err = self.refused(fake, E.FAILOVER_REFUSED)
        self.assertIn("authority moved", err.detail)
        self.assertEqual(fake.providers_invoked, ["claude"])

    def test_NC_without_a_live_authority_probe_nothing_is_handed_over(self):
        fake = repo(claude_quota(), ok("codex"))
        err = self.refused(fake, E.FAILOVER_REFUSED, probe=False)
        self.assertIn("freshness cannot be proven", err.detail)
        self.assertEqual(fake.providers_invoked, ["claude"])

    def test_NC_an_unclassified_error_does_not_fail_over(self):
        fake = repo(Step("claude", rc=1, stderr="Segmentation fault"), ok("codex"))
        self.refused(fake, E.TRANSPORT_FAILED)
        self.assertEqual(fake.providers_invoked, ["claude"])

    def test_NC_quota_like_prose_without_the_classified_shape_does_not_fail_over(self):
        prose = Step("claude", rc=1, stdout=claude_result("we hit a quota / rate limit (429)"),
                     stderr="quota exhausted: 429 Too Many Requests")
        fake = repo(prose, ok("codex"))
        self.refused(fake, E.TRANSPORT_FAILED)
        self.assertEqual(fake.providers_invoked, ["claude"])

    def test_NC_a_launch_failure_or_timeout_is_ambiguous_and_does_not_fail_over(self):
        for code in (E.EXECUTABLE_NOT_FOUND, E.COMMAND_TIMEOUT):
            fake = repo(Step("claude", raises=code), ok("codex"))
            self.refused(fake, code)
            self.assertEqual(fake.providers_invoked, ["claude"])

    def test_NC_both_providers_unavailable_is_one_bounded_failure(self):
        fake = repo(claude_quota(), codex_quota())
        err = self.refused(fake, E.PROVIDERS_EXHAUSTED)
        self.assertEqual(fake.providers_invoked, ["claude", "codex"])
        self.assertEqual(fake.posted, [])
        # The watcher reads this as capacity, so it waits on the long schedule.
        self.assertTrue(QUOTA_RE.search(err.detail))

    def test_NC_a_single_provider_order_never_reaches_the_other(self):
        for order, step in ((("claude",), claude_quota()), (("codex",), codex_quota())):
            fake = repo(step)
            self.refused(fake, E.PROVIDERS_EXHAUSTED, order=order)
            self.assertEqual(fake.providers_invoked, [order[0]])

    def test_NC_the_second_provider_failing_unclassified_is_not_retried(self):
        fake = repo(claude_quota(), Step("codex", rc=2, stderr="boom"))
        self.refused(fake, E.TRANSPORT_FAILED)
        self.assertEqual(fake.providers_invoked, ["claude", "codex"])

    def test_NC_an_accepted_head_move_during_the_attempt_stops_the_handover(self):
        def move_head(fake):
            fake.comments.append(gh(CHECKPOINT + 50,
                                    CHECKPOINT_COMMENT.replace(f"h: {BASE}", "h: " + "c" * 40)))
        fake = repo(claude_quota(then=move_head), ok("codex"))
        err = self.refused(fake, E.FAILOVER_REFUSED)
        self.assertIn("authority moved", err.detail)
        self.assertEqual(fake.providers_invoked, ["claude"])

    def test_NC_an_abort_during_the_attempt_stops_the_handover(self):
        abort = comment_body(kind="WAVE_ABORT", actor="MANAGER", message_id="m-abort-0001")
        fake = repo(claude_quota(then=lambda r: r.comments.append(gh(CHECKPOINT + 60, abort))),
                    ok("codex"))
        err = self.refused(fake, E.FAILOVER_REFUSED)
        self.assertIn("aborted", err.detail)
        self.assertEqual(fake.providers_invoked, ["claude"])

    def test_NC_the_probe_names_an_accepted_head_that_moved_under_the_same_checkpoint(self):
        from agent_bus.machine import Authority
        sup = armed(repo())
        live = sup.observe()
        envelope = live.state.pending_for("WORKER")[0]
        moved = Authority(issue=1, checkpoint=CHECKPOINT, task=TASK, accepted_head="c" * 40)
        live.resolution = dataclasses.replace(live.resolution, authority=moved)
        problems = P.live_authority_probe(lambda: live)(envelope)
        self.assertEqual(len(problems), 1)
        self.assertIn("accepted head moved", problems[0])
        self.assertEqual(P.live_authority_probe(sup.observe)(envelope), [])

    def test_NC_the_gate_refuses_a_tree_that_was_dirty_before_dispatch(self):
        fake = repo()
        before = P.inspect(REPO_PATH, fake)
        dirty_before = before.__class__(before.root, before.branch, before.head, (" M x",))
        problems = P.failover_problems(REPO_PATH, dirty_before, None, lambda e: [], fake)
        self.assertEqual(len(problems), 1)
        self.assertIn("already dirty", problems[0])

    def test_NC_the_gate_refuses_when_git_cannot_be_re_measured(self):
        fake = repo()
        before = P.inspect(REPO_PATH, fake)

        def broken(argv, stdin=None, timeout=None):
            return Completed(tuple(argv), 128, "", "fatal: not a git repository")
        problems = P.failover_problems(REPO_PATH, before, None, lambda e: [], broken)
        self.assertEqual(len(problems), 1)
        self.assertIn("could not be re-measured", problems[0])

    def test_NC_a_duplicate_provider_cannot_be_configured_into_a_loop(self):
        claude = P.ClaudeProvider(REPO_PATH)
        with self.assertRaises(BusError) as caught:
            P.ProviderFailoverTransport(REPO_PATH, [claude, claude])
        self.assertEqual(caught.exception.code, E.PROVIDER_CONFIG_INVALID)


if __name__ == "__main__":
    unittest.main()
