"""Unattended safety: trust, preflight, unit enforcement, and the watcher.

Everything Agent Bus v1 left as an instruction is checked here as a measurement.
The organising question of the module is not "does the happy path work" but
"what happens when it does not", so almost every test is a negative control with
a named code.

Nothing here touches the network, invokes a model, writes a launchd agent, or
reads `~/.claude`.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.refoundation.agent_bus_fixtures import (
    AUTHORITY, BASE, CHECKPOINT, NOBODY_TRUSTED, OTHER_SHA, TASK, TRUSTED, WAVE,
    comment_body, envelope, raw, unit,
)
from tests.refoundation.agent_bus_repo_fake import Effect, FakeRepo

from agent_bus import errors as E
from agent_bus.compose import progress, result, slug
from agent_bus.enforce import glob_to_regex, scope_violations, verify_unit
from agent_bus.errors import BusError
from agent_bus.git_evidence import trailers
from agent_bus.issue import AuthorityError, resolve_authority
from agent_bus.machine import Authority, RawComment, fold
from agent_bus.preflight import build_base_of, inspect, preflight
from agent_bus.protocol import parse
from agent_bus.supervisor import Supervisor
from agent_bus.trust import HOW_TO_CONFIGURE, NOBODY, Trust, from_file, resolve
from agent_bus.wave import Unit, plan_from_command
from agent_bus import watcher as W

REPO = "MTJawnny/mtjawnny-pipeline"
REPO_PATH = "/tmp/repo"
BRANCH = "infra/agent-bus-v1"
COMMAND = dict(kind="WAVE_COMMAND", actor="MANAGER", message_id="m-command-0001")

CHECKPOINT_COMMENT = (
    "```yaml\nschema: mtj-checkpoint/2\n"
    f"h: {BASE}\na: {TASK}\nnext: CLAUDE_EXECUTE_SELECTED_ONLY\n```\n"
)


def gh(comment_id: int, body: str, author: str = "MTJawnny") -> dict:
    return {"id": comment_id, "user": {"login": author}, "body": body}


def stream(*rows) -> list[dict]:
    out = [gh(CHECKPOINT, CHECKPOINT_COMMENT)]
    for index, row in enumerate(rows, start=1):
        body, author = row if isinstance(row, tuple) else (row, "MTJawnny")
        out.append(gh(CHECKPOINT + index, body, author))
    return out


def two_unit_command(**kw) -> str:
    body = {
        "branch": BRANCH,
        "review_boundary": "one review at the end of the wave",
        "units": [unit("U1", allow=("agent_bus/**",)),
                  unit("U2", depends_on=["U1"], allow=("tests/**",))],
    }
    return comment_body(body=body, **dict(COMMAND, **kw))


def supervisor(repo: FakeRepo, trust: Trust = TRUSTED, **kw) -> Supervisor:
    return Supervisor(repo_path=REPO_PATH, repo_slug=REPO, trust=trust,
                      run=repo, clock=lambda: __import__("datetime").datetime(
                          2026, 9, 24, 3, 0, 0), **kw)


def done(unit_id: str, *paths: str) -> Effect:
    return Effect(message=f"{unit_id}: work\n\n" + trailers(WAVE, unit_id), paths=paths)


# ---------------------------------------------------------------------------
# 1. Trust, fail closed
# ---------------------------------------------------------------------------


class TestTrustFailsClosed(unittest.TestCase):
    def test_an_unconfigured_bus_trusts_nobody(self):
        self.assertEqual(resolve(None, {}, Path("/nonexistent/trust.json")), NOBODY)
        self.assertFalse(NOBODY.configured)

    def test_acting_on_an_unconfigured_bus_is_refused_with_instructions(self):
        with self.assertRaises(BusError) as caught:
            NOBODY.require()
        self.assertEqual(caught.exception.code, E.TRUST_NOT_CONFIGURED)
        self.assertEqual(caught.exception.detail, HOW_TO_CONFIGURE)

    def test_an_empty_trust_set_rejects_every_message_rather_than_allowing_them(self):
        # v1's bug, stated as a test: an empty set used to mean "no restriction".
        state = fold([raw(10, **COMMAND)], AUTHORITY, NOBODY_TRUSTED)
        self.assertEqual([r.code for r in state.rejected()], [E.UNTRUSTED_AUTHOR])
        self.assertEqual(state.pending_for("WORKER"), [])

    def test_NC_an_untrusted_public_commenter_with_a_perfectly_current_command(self):
        # Every field is live: right checkpoint, right task, right base, right
        # actor, right kind. The ONLY thing wrong is who said it.
        repo = FakeRepo(stream((two_unit_command(), "drive-by-contributor")))
        report = supervisor(repo).poll_once()
        self.assertEqual(report["action"], "NONE")
        self.assertEqual([r["code"] for r in report["rejected"]], [E.UNTRUSTED_AUTHOR])
        self.assertEqual(repo.claude_calls, [])

    def test_the_same_command_from_a_trusted_speaker_is_actionable(self):
        repo = FakeRepo(stream(two_unit_command()))
        self.assertEqual(supervisor(repo).poll_once()["action"], "DISPATCH_DRY_RUN")

    def test_execution_refuses_before_anything_else_when_trust_is_unconfigured(self):
        repo = FakeRepo(stream(two_unit_command()))
        with self.assertRaises(BusError) as caught:
            supervisor(repo, trust=NOBODY).poll_once(execute=True)
        self.assertEqual(caught.exception.code, E.TRUST_NOT_CONFIGURED)
        self.assertEqual(repo.calls, [])  # not even a read happened

    def test_a_trust_file_that_cannot_be_parsed_halts_instead_of_meaning_nobody(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trust.json"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaises(BusError) as caught:
                from_file(path)
            self.assertEqual(caught.exception.code, E.TRUST_NOT_CONFIGURED)

    def test_the_resolution_order_is_flag_then_environment_then_file(self):
        env = {"MTJ_AGENT_BUS_TRUSTED": "from-env"}
        self.assertEqual(resolve("from-flag", env).speakers, frozenset({"from-flag"}))
        self.assertEqual(resolve(None, env).speakers, frozenset({"from-env"}))


# ---------------------------------------------------------------------------
# 2. Authority: a forged checkpoint
# ---------------------------------------------------------------------------


class TestForgedCheckpoints(unittest.TestCase):
    def comments(self, forger: str = "drive-by-contributor"):
        forged = CHECKPOINT_COMMENT.replace(f"a: {TASK}", "a: 424242")
        return [RawComment("issue:1", CHECKPOINT, "MTJawnny", CHECKPOINT_COMMENT),
                RawComment("issue:1", CHECKPOINT + 9, forger, forged)]

    def test_NC_a_forged_current_looking_K_by_an_untrusted_author_selects_nothing(self):
        resolution = resolve_authority(self.comments(), 1, TRUSTED)
        self.assertEqual(resolution.authority.task, TASK)
        self.assertEqual(resolution.authority.checkpoint, CHECKPOINT)

    def test_the_refused_checkpoint_is_reported_rather_than_silently_dropped(self):
        resolution = resolve_authority(self.comments(), 1, TRUSTED)
        self.assertEqual(resolution.untrusted_candidates,
                         ((CHECKPOINT + 9, "drive-by-contributor"),))
        self.assertEqual(resolution.as_dict()["untrusted_checkpoint_candidates"],
                         [{"comment_id": CHECKPOINT + 9,
                           "author": "drive-by-contributor"}])

    def test_a_forged_checkpoint_cannot_halt_the_bus_either(self):
        # Refusing it must not become a denial of service: the trusted checkpoint
        # is still resolved, so a passer-by can neither steer nor stop the Worker.
        self.assertEqual(resolve_authority(self.comments(), 1, TRUSTED).authority.task,
                         TASK)

    def test_when_every_checkpoint_is_untrusted_the_bus_halts_loudly(self):
        only_forged = [self.comments()[1]]
        with self.assertRaises(AuthorityError) as caught:
            resolve_authority(only_forged, 1, TRUSTED)
        self.assertIn("trusted speaker", str(caught.exception))

    def test_resolving_authority_at_all_requires_configured_trust(self):
        with self.assertRaises(BusError) as caught:
            resolve_authority(self.comments(), 1, NOBODY)
        self.assertEqual(caught.exception.code, E.TRUST_NOT_CONFIGURED)


# ---------------------------------------------------------------------------
# 3. Checkout preflight
# ---------------------------------------------------------------------------


class TestPreflight(unittest.TestCase):
    def setup(self, **kw) -> tuple[FakeRepo, object, object]:
        repo = FakeRepo(stream(two_unit_command()), **kw)
        command = parse(json.dumps(envelope(
            body={"branch": BRANCH, "review_boundary": "end",
                  "units": [unit("U1", allow=("agent_bus/**",))]}, **COMMAND)))
        plan = plan_from_command(WAVE, command.body)
        return repo, command, plan

    def codes(self, report) -> list[str]:
        return [code for code, _ in report.problems]

    def test_a_correct_checkout_passes(self):
        repo, command, plan = self.setup()
        report = preflight(command, plan, REPO_PATH, (), repo)
        self.assertTrue(report.ok, report.problems)

    def test_NC_the_wrong_branch_is_refused(self):
        repo, command, plan = self.setup(branch="some-other-branch")
        report = preflight(command, plan, REPO_PATH, (), repo)
        self.assertIn(E.WRONG_BRANCH, self.codes(report))

    def test_NC_the_wrong_worktree_is_refused(self):
        repo, command, plan = self.setup(toplevel="/tmp/somewhere-else")
        report = preflight(command, plan, REPO_PATH, (), repo)
        self.assertIn(E.WRONG_WORKTREE, self.codes(report))

    def test_NC_a_base_that_is_not_an_ancestor_of_head_is_refused(self):
        repo, command, plan = self.setup(ancestor=False)
        report = preflight(command, plan, REPO_PATH, (), repo)
        self.assertIn(E.BASE_NOT_ANCESTOR, self.codes(report))

    def test_NC_an_unexpectedly_dirty_tree_is_refused(self):
        repo, command, plan = self.setup()
        repo.dirty = ("experiments/scratch.py",)
        report = preflight(command, plan, REPO_PATH, (), repo)
        self.assertIn(E.UNEXPECTED_DIRT, self.codes(report))
        self.assertIn("experiments/scratch.py", dict(report.problems)[E.UNEXPECTED_DIRT])

    def test_NC_a_unit_the_bus_calls_done_with_no_commit_here_is_refused(self):
        repo, command, plan = self.setup()
        report = preflight(command, plan, REPO_PATH, ("U1",), repo)
        self.assertIn(E.PROGRESS_HEAD_MISMATCH, self.codes(report))

    def test_a_unit_the_bus_calls_done_that_this_checkout_has_is_accepted(self):
        repo, command, plan = self.setup()
        repo._commit(done("U1", "agent_bus/x.py"))
        report = preflight(command, plan, REPO_PATH, ("U1",), repo)
        self.assertNotIn(E.PROGRESS_HEAD_MISMATCH, self.codes(report))

    def test_every_problem_is_collected_not_just_the_first(self):
        repo, command, plan = self.setup(branch="wrong", toplevel="/tmp/elsewhere")
        repo.dirty = ("a.py",)
        codes = self.codes(preflight(command, plan, REPO_PATH, (), repo))
        self.assertEqual(sorted(codes),
                         sorted([E.WRONG_WORKTREE, E.WRONG_BRANCH, E.UNEXPECTED_DIRT]))

    def test_a_repair_wave_builds_on_its_candidate_base_not_the_accepted_head(self):
        command = parse(json.dumps(envelope(
            body={"branch": BRANCH, "review_boundary": "end",
                  "candidate_base": OTHER_SHA,
                  "units": [unit("U1", allow=("agent_bus/**",))]}, **COMMAND)))
        self.assertEqual(command.base, BASE)
        self.assertEqual(build_base_of(command), OTHER_SHA)

    def test_a_command_without_a_candidate_base_builds_on_the_accepted_head(self):
        _, command, _ = self.setup()
        self.assertEqual(build_base_of(command), BASE)

    def test_the_supervisor_refuses_to_dispatch_when_preflight_fails(self):
        repo = FakeRepo(stream(two_unit_command()), branch="not-the-wave-branch")
        report = supervisor(repo).poll_once()
        self.assertEqual(report["action"], "NONE")
        self.assertEqual(report["reason"], E.PREFLIGHT_FAILED)
        self.assertEqual(repo.claude_calls, [])

    def test_preflight_runs_even_on_a_dry_run(self):
        repo = FakeRepo(stream(two_unit_command()))
        repo.dirty = ("x.py",)
        report = supervisor(repo).poll_once(execute=False)
        self.assertEqual(report["reason"], E.PREFLIGHT_FAILED)
        self.assertIn(E.UNEXPECTED_DIRT,
                      [p["code"] for p in report["preflight"]["problems"]])


# ---------------------------------------------------------------------------
# 4. Unit boundary enforcement
# ---------------------------------------------------------------------------


class TestGlobs(unittest.TestCase):
    def test_a_single_star_does_not_cross_a_separator(self):
        self.assertTrue(glob_to_regex("agent_bus/*").match("agent_bus/x.py"))
        self.assertFalse(glob_to_regex("agent_bus/*").match("agent_bus/a/b.py"))

    def test_a_double_star_does_cross(self):
        self.assertTrue(glob_to_regex("agent_bus/**").match("agent_bus/a/b.py"))

    def test_deny_beats_allow(self):
        self.assertEqual(scope_violations(["tests/x.py"], ["**"], ["tests/**"]),
                         ["tests/x.py"])

    def test_a_pattern_is_anchored_at_both_ends(self):
        self.assertFalse(glob_to_regex("agent_bus/x.py").match("other/agent_bus/x.py"))
        self.assertFalse(glob_to_regex("agent_bus/x.py").match("agent_bus/x.pyc"))


class TestUnitEnforcement(unittest.TestCase):
    def unit(self, **kw) -> Unit:
        return Unit(id="U1", objective="o", depends_on=(), allow_paths=("agent_bus/**",),
                    validation=("v",), mutating=True, **kw)

    def verify(self, repo: FakeRepo, unit: Unit, before: str, dirty=()):
        return verify_unit(REPO_PATH, WAVE, unit, before, repo.head, dirty, repo)

    def test_a_well_behaved_unit_passes(self):
        repo = FakeRepo([])
        before = repo.head
        repo._commit(done("U1", "agent_bus/x.py"))
        verdict = self.verify(repo, self.unit(), before)
        self.assertTrue(verdict.ok, verdict.problems)
        self.assertEqual(verdict.paths, ("agent_bus/x.py",))

    def test_NC_a_commit_outside_the_allowlist_is_a_scope_escape(self):
        repo = FakeRepo([])
        before = repo.head
        repo._commit(done("U1", "agent_bus/x.py", "pipeline/build_db.py"))
        verdict = self.verify(repo, self.unit(), before)
        self.assertFalse(verdict.ok)
        self.assertIn(E.UNIT_SCOPE_ESCAPE, [c for c, _ in verdict.problems])
        self.assertIn("pipeline/build_db.py", dict(verdict.problems)[E.UNIT_SCOPE_ESCAPE])

    def test_NC_a_denied_path_is_a_scope_escape_even_when_allowed(self):
        repo = FakeRepo([])
        before = repo.head
        repo._commit(done("U1", "agent_bus/secrets.py"))
        verdict = self.verify(repo, self.unit(deny_paths=("**/secrets.py",)), before)
        self.assertIn(E.UNIT_SCOPE_ESCAPE, [c for c, _ in verdict.problems])

    def test_NC_a_missing_trailer_is_refused(self):
        repo = FakeRepo([])
        before = repo.head
        repo._commit(Effect(message="U1: work, no trailers", paths=("agent_bus/x.py",)))
        verdict = self.verify(repo, self.unit(), before)
        self.assertIn(E.UNIT_TRAILER_MISSING, [c for c, _ in verdict.problems])

    def test_NC_a_trailer_naming_another_unit_is_refused(self):
        repo = FakeRepo([])
        before = repo.head
        repo._commit(Effect(message="U1\n\n" + trailers(WAVE, "U2"),
                            paths=("agent_bus/x.py",)))
        verdict = self.verify(repo, self.unit(), before)
        self.assertIn(E.UNIT_TRAILER_MISSING, [c for c, _ in verdict.problems])

    def test_NC_a_trailer_naming_another_wave_is_refused(self):
        repo = FakeRepo([])
        before = repo.head
        repo._commit(Effect(message="U1\n\n" + trailers("OTHER.WAVE", "U1"),
                            paths=("agent_bus/x.py",)))
        verdict = self.verify(repo, self.unit(), before)
        self.assertIn(E.UNIT_TRAILER_MISSING, [c for c, _ in verdict.problems])

    def test_NC_a_mutating_unit_that_committed_nothing_is_refused(self):
        repo = FakeRepo([])
        verdict = self.verify(repo, self.unit(), repo.head)
        self.assertIn(E.UNIT_NO_COMMIT, [c for c, _ in verdict.problems])

    def test_NC_leftover_uncommitted_work_is_refused(self):
        repo = FakeRepo([])
        before = repo.head
        repo._commit(done("U1", "agent_bus/x.py"))
        verdict = self.verify(repo, self.unit(), before, dirty=("agent_bus/y.py",))
        self.assertIn(E.UNIT_UNCOMMITTED, [c for c, _ in verdict.problems])

    def test_NC_a_read_only_unit_that_mutated_is_refused(self):
        repo = FakeRepo([])
        before = repo.head
        repo._commit(done("U1", "agent_bus/x.py"))
        readonly = Unit(id="U1", objective="o", depends_on=(), allow_paths=(),
                        validation=("v",), mutating=False)
        verdict = self.verify(repo, readonly, before)
        self.assertIn(E.READONLY_UNIT_MUTATED, [c for c, _ in verdict.problems])

    def test_a_read_only_unit_that_changed_nothing_passes(self):
        repo = FakeRepo([])
        readonly = Unit(id="U1", objective="o", depends_on=(), allow_paths=(),
                        validation=("v",), mutating=False)
        self.assertTrue(self.verify(repo, readonly, repo.head).ok)


# ---------------------------------------------------------------------------
# 5. Autonomous multi-unit execution
# ---------------------------------------------------------------------------


class TestWaveExecution(unittest.TestCase):
    def repo(self, *effects) -> FakeRepo:
        return FakeRepo(stream(two_unit_command()), script=list(effects))

    def test_a_wave_crosses_unit_boundaries_without_asking_anyone(self):
        repo = self.repo(done("U1", "agent_bus/x.py"), done("U2", "tests/y.py"))
        report = supervisor(repo).poll_once(execute=True)
        self.assertEqual(report["action"], "WAVE_RAN")
        self.assertEqual(len(repo.claude_calls), 2)
        self.assertEqual([o["unit"] for o in report["units"]], ["U1", "U2"])
        self.assertTrue(all(o["ok"] for o in report["units"]))

    def test_the_first_unit_opens_a_session_and_the_second_resumes_it(self):
        repo = self.repo(done("U1", "agent_bus/x.py"), done("U2", "tests/y.py"))
        supervisor(repo).poll_once(execute=True)
        first, second = repo.claude_calls
        self.assertIn("--session-id", first)
        self.assertIn("--resume", second)
        self.assertEqual(first[first.index("--session-id") + 1],
                         second[second.index("--resume") + 1])

    def test_one_progress_message_per_unit_and_exactly_one_result(self):
        repo = self.repo(done("U1", "agent_bus/x.py"), done("U2", "tests/y.py"))
        supervisor(repo).poll_once(execute=True)
        self.assertEqual(repo.posted_kinds(),
                         ["WAVE_PROGRESS", "WAVE_PROGRESS", "WAVE_RESULT"])

    def test_the_result_names_every_unit_and_selects_no_successor(self):
        repo = self.repo(done("U1", "agent_bus/x.py"), done("U2", "tests/y.py"))
        supervisor(repo).poll_once(execute=True)
        final = repo.posted_messages()[-1]
        self.assertEqual([u["id"] for u in final.body["units"]], ["U1", "U2"])
        self.assertEqual(final.body["status"], "P")
        self.assertEqual(final.body["next"], "NONE")

    def test_NC_a_scope_escape_stops_the_wave_before_the_next_unit_runs(self):
        repo = self.repo(done("U1", "agent_bus/x.py", "pipeline/build_db.py"),
                         done("U2", "tests/y.py"))
        report = supervisor(repo).poll_once(execute=True)
        self.assertEqual(report["action"], "WAVE_STOPPED")
        self.assertEqual(report["reason"], E.UNIT_SCOPE_ESCAPE)
        self.assertEqual(len(repo.claude_calls), 1)

    def test_a_stopped_wave_still_posts_a_durable_failing_result(self):
        repo = self.repo(done("U1", "agent_bus/x.py", "pipeline/build_db.py"))
        supervisor(repo).poll_once(execute=True)
        self.assertEqual(repo.posted_kinds(), ["WAVE_PROGRESS", "WAVE_RESULT"])
        final = repo.posted_messages()[-1]
        self.assertEqual(final.body["status"], "F")
        self.assertTrue(final.body["discrepancies"])

    def test_NC_a_unit_that_commits_nothing_stops_the_wave(self):
        repo = self.repo(Effect(), done("U2", "tests/y.py"))
        report = supervisor(repo).poll_once(execute=True)
        self.assertEqual(report["action"], "WAVE_STOPPED")
        self.assertEqual(report["reason"], E.UNIT_NO_COMMIT)
        self.assertEqual(len(repo.claude_calls), 1)

    def test_max_units_bounds_one_invocation(self):
        repo = self.repo(done("U1", "agent_bus/x.py"), done("U2", "tests/y.py"))
        report = supervisor(repo, max_units=1).poll_once(execute=True)
        self.assertEqual(len(repo.claude_calls), 1)
        self.assertEqual([o["unit"] for o in report["units"]], ["U1"])

    def test_posted_message_ids_are_derived_so_a_repost_is_a_duplicate(self):
        repo = self.repo(done("U1", "agent_bus/x.py"), done("U2", "tests/y.py"))
        supervisor(repo).poll_once(execute=True)
        ids = [m.message_id for m in repo.posted_messages()]
        self.assertEqual(ids[0], slug("w", WAVE, "U1", "progress", "DONE"))
        self.assertEqual(len(set(ids)), len(ids))

    def test_nothing_is_posted_and_nothing_runs_on_a_dry_run(self):
        repo = self.repo(done("U1", "agent_bus/x.py"))
        supervisor(repo).poll_once(execute=False)
        self.assertEqual(repo.posted, [])
        self.assertEqual(repo.claude_calls, [])


# ---------------------------------------------------------------------------
# 6. The watcher
# ---------------------------------------------------------------------------


class Recorder:
    """A supervisor stand-in that answers a scripted sequence."""

    def __init__(self, answers):
        self.answers = list(answers)
        self.calls = 0

    def poll_once(self, execute=False, resume=False):
        self.calls += 1
        answer = self.answers[min(self.calls, len(self.answers)) - 1]
        if isinstance(answer, Exception):
            raise answer
        return answer


class Sleeper:
    def __init__(self, journal: list | None = None):
        self.slept: list[float] = []
        self.journal = journal

    def __call__(self, seconds: float) -> None:
        self.slept.append(seconds)
        if self.journal is not None:
            self.journal.append(("slept", seconds))


class Emitter:
    """Stands in for the log line, so tests can see WHEN it was written."""

    def __init__(self, journal: list | None = None):
        self.entries: list[dict] = []
        self.journal = journal

    def __call__(self, entry: dict) -> None:
        self.entries.append(entry)
        if self.journal is not None:
            self.journal.append(("emitted", entry["cycle"]))


def watcher(supervisor, **kw):
    """Every watcher in the tests is silent unless the test asked to hear it."""
    kw.setdefault("emit", Emitter())
    kw.setdefault("clock", lambda: "2026-09-24T00:00:00Z")
    return W.Watcher(supervisor, **kw)


class TestWatcher(unittest.TestCase):
    def test_a_quiet_watcher_sleeps_the_full_interval_every_cycle(self):
        sleeper = Sleeper()
        log = watcher(Recorder([{"action": "NONE"}]), interval=120,
                      sleep=sleeper).run(cycles=3)
        self.assertEqual([entry["sleep"] for entry in log], [120, 120, 120])
        # The final cycle does not sleep: the loop is leaving, not waiting.
        self.assertEqual(sleeper.slept, [120, 120])

    def test_NC_repeated_failures_back_off_instead_of_hot_looping(self):
        sleeper = Sleeper()
        failing = Recorder([BusError(E.TRANSPORT_FAILED, "claude exited 1")])
        log = watcher(failing, interval=120, sleep=sleeper).run(cycles=4)
        delays = [entry["sleep"] for entry in log]
        self.assertEqual(delays, [60, 120, 240, 480])
        self.assertEqual(delays, sorted(delays))
        self.assertTrue(all(d > 0 for d in delays))

    def test_NC_a_quota_refusal_backs_off_on_its_own_longer_schedule(self):
        sleeper = Sleeper()
        quota = Recorder([BusError(E.TRANSPORT_FAILED, "429 rate limit reached")])
        log = watcher(quota, interval=120, sleep=sleeper).run(cycles=3)
        self.assertEqual([entry["sleep"] for entry in log], [900, 1800, 3600])
        self.assertTrue(all(entry["quota"] for entry in log))

    def test_backoff_is_capped(self):
        backoff = W.Backoff()
        self.assertEqual(backoff.delay(99), backoff.cap)
        self.assertEqual(backoff.delay(99, quota=True), backoff.quota_cap)

    def test_a_success_after_failures_resets_the_schedule(self):
        answers = [BusError(E.TRANSPORT_FAILED, "boom"), {"action": "NONE"}]
        recorder = Recorder(answers)
        log = watcher(recorder, interval=60, sleep=Sleeper()).run(cycles=2)
        self.assertEqual([entry["sleep"] for entry in log], [60, 60])
        self.assertEqual(log[0]["outcome"], "failed")
        self.assertEqual(log[1]["outcome"], "polled")

    def test_NC_an_interval_below_the_floor_is_refused(self):
        with self.assertRaises(BusError) as caught:
            watcher(Recorder([{}]), interval=1)
        self.assertEqual(caught.exception.code, E.BAD_VALUE)

    def test_a_stop_request_ends_the_loop_cleanly(self):
        sleeper = Sleeper()
        loop = watcher(Recorder([{"action": "NONE"}]), interval=60, sleep=sleeper)
        loop.request_stop()
        self.assertEqual(loop.run(cycles=5), [])
        self.assertEqual(sleeper.slept, [])

    def test_NC_a_second_watcher_process_refuses_to_start(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "watcher.lock"
            first = W.SingleInstance(path).acquire()
            try:
                with self.assertRaises(BusError) as caught:
                    W.SingleInstance(path).acquire()
                self.assertEqual(caught.exception.code, E.WATCHER_ALREADY_RUNNING)
            finally:
                first.release()

    def test_the_lock_is_released_so_a_later_watcher_can_start(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "watcher.lock"
            W.SingleInstance(path).acquire().release()
            second = W.SingleInstance(path).acquire()
            second.release()

    def test_the_lock_lives_outside_the_repository_and_outside_claude_config(self):
        lock = str(W.lock_path_for(REPO_PATH))
        self.assertNotIn("/.claude", lock)
        self.assertNotIn(str(Path(REPO_PATH).resolve()) + "/", lock)
        self.assertIn(".local/state/mtj-agent-bus", lock)

    def test_the_loop_releases_its_lock_when_it_ends(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "watcher.lock"
            lock = W.SingleInstance(path)
            watcher(Recorder([{"action": "NONE"}]), interval=60,
                    sleep=Sleeper(), lock=lock).run(cycles=1)
            W.SingleInstance(path).acquire().release()


# ---------------------------------------------------------------------------
# 7. R2 -- the service can actually run, and says so while it does
# ---------------------------------------------------------------------------


def fake_which(table: dict[str, str]):
    """A `which` that answers from a table, so PATH derivation is testable.

    Derivation must come from MEASUREMENT. A test that only ever sees this
    machine's Homebrew cannot tell a derived path from a hardcoded one, so every
    assertion below resolves to directories this machine does not have.
    """
    return lambda name: table.get(name)


ELSEWHERE = {"git": "/opt/tools/bin/git", "gh": "/opt/tools/bin/gh",
             "claude": "/home/someone/.local/bin/claude"}
ARGV_IDLE = ["python3", "-m", "agent_bus", "watch", "run"]


def armed_argv(order: str = "claude") -> list[str]:
    """An armed service argv; `watch install --execute` always writes the order."""
    return ["python3", "-m", "agent_bus", "--providers", order, "watch", "run", "--execute"]


ARGV_ARMED = armed_argv("claude")


class TestServiceEnvironmentIsDerived(unittest.TestCase):
    def test_an_idle_service_needs_git_and_gh_but_not_claude(self):
        self.assertEqual(W.required_executables(ARGV_IDLE), ("git", "gh"))

    def test_an_armed_service_also_needs_claude(self):
        self.assertEqual(W.required_executables(ARGV_ARMED), ("git", "gh", "claude"))

    def test_an_armed_service_needs_every_enabled_provider_in_order(self):
        for order, names in (("claude,codex", ("claude", "codex")),
                             ("codex,claude", ("codex", "claude")),
                             ("codex", ("codex",))):
            with self.subTest(order=order):
                self.assertEqual(W.required_executables(armed_argv(order)),
                                 ("git", "gh") + names)
        self.assertEqual(W.required_executables(
            ["--providers=codex", "watch", "run", "--execute"]), ("git", "gh", "codex"))

    def test_NC_an_armed_service_that_names_no_provider_order_is_refused(self):
        with self.assertRaises(BusError) as caught:
            W.required_executables(ARGV_IDLE + ["--execute"])
        self.assertEqual(caught.exception.code, E.PROVIDER_CONFIG_INVALID)

    def test_NC_an_armed_service_with_a_malformed_order_is_refused(self):
        with self.assertRaises(BusError) as caught:
            W.install(armed_argv("claude,gemini"), dry_run=True, which=fake_which(ELSEWHERE))
        self.assertEqual(caught.exception.code, E.PROVIDER_CONFIG_INVALID)

    def test_NC_a_missing_codex_refuses_an_armed_failover_installation_by_name(self):
        with self.assertRaises(BusError) as caught:
            W.install(armed_argv("claude,codex"), dry_run=True, which=fake_which(ELSEWHERE))
        self.assertEqual(caught.exception.code, E.EXECUTABLE_NOT_FOUND)
        self.assertIn("codex", caught.exception.detail)
        self.assertNotIn("claude", caught.exception.detail)

    def test_NC_every_missing_provider_executable_is_named_at_once(self):
        table = {"git": "/usr/bin/git", "gh": "/opt/tools/bin/gh"}
        with self.assertRaises(BusError) as caught:
            W.install(armed_argv("codex,claude"), dry_run=True, which=fake_which(table))
        self.assertIn("codex, claude", caught.exception.detail)

    def test_an_armed_failover_service_carries_both_provider_directories(self):
        table = dict(ELSEWHERE, codex="/opt/codex/bin/codex")
        plan = W.install(armed_argv("claude,codex"), dry_run=True, which=fake_which(table))
        self.assertEqual(sorted(plan["executables"]), ["claude", "codex", "gh", "git"])
        self.assertIn("/opt/codex/bin", plan["path"].split(":"))
        self.assertIn("<string>claude,codex</string>", plan["document"])

    def test_the_path_is_derived_from_where_the_tools_actually_are(self):
        resolved = W.resolve_executables(("git", "gh", "claude"), fake_which(ELSEWHERE))
        path = W.service_path(resolved)
        self.assertEqual(path,
                         "/opt/tools/bin:/home/someone/.local/bin:"
                         "/usr/bin:/bin:/usr/sbin:/sbin")

    def test_the_launchd_defaults_are_always_appended_and_never_duplicated(self):
        resolved = W.resolve_executables(("git",), fake_which({"git": "/usr/bin/git"}))
        self.assertEqual(W.service_path(resolved), "/usr/bin:/bin:/usr/sbin:/sbin")

    def test_the_installed_plist_carries_that_path(self):
        plan = W.install(ARGV_ARMED, dry_run=True, which=fake_which(ELSEWHERE))
        self.assertIn("<key>PATH</key>", plan["document"])
        self.assertIn("/opt/tools/bin", plan["document"])
        self.assertEqual(plan["path"], plan["document"].split(
            "<key>PATH</key>\n      <string>")[1].split("</string>")[0])

    def test_derivation_wins_over_a_caller_supplied_path(self):
        plan = W.install(ARGV_ARMED, dry_run=True, which=fake_which(ELSEWHERE),
                         environment={"PATH": "/nowhere", "TZ": "UTC"})
        self.assertNotIn("/nowhere", plan["document"])
        self.assertIn("<key>TZ</key>", plan["document"])

    def test_NC_a_missing_gh_refuses_the_installation_by_name(self):
        with self.assertRaises(BusError) as caught:
            W.install(ARGV_IDLE, dry_run=True,
                      which=fake_which({"git": "/usr/bin/git"}))
        self.assertEqual(caught.exception.code, E.EXECUTABLE_NOT_FOUND)
        self.assertIn("gh", caught.exception.detail)

    def test_NC_a_missing_claude_refuses_an_ARMED_installation(self):
        table = {"git": "/usr/bin/git", "gh": "/opt/tools/bin/gh"}
        with self.assertRaises(BusError) as caught:
            W.install(ARGV_ARMED, dry_run=True, which=fake_which(table))
        self.assertEqual(caught.exception.code, E.EXECUTABLE_NOT_FOUND)
        self.assertIn("claude", caught.exception.detail)

    def test_the_same_machine_can_still_install_an_IDLE_service(self):
        table = {"git": "/usr/bin/git", "gh": "/opt/tools/bin/gh"}
        plan = W.install(ARGV_IDLE, dry_run=True, which=fake_which(table))
        self.assertEqual(plan["path"], "/usr/bin:/opt/tools/bin:/bin:/usr/sbin:/sbin")

    def test_every_missing_executable_is_named_at_once(self):
        with self.assertRaises(BusError) as caught:
            W.resolve_executables(("git", "gh", "claude"), fake_which({}))
        for name in ("git", "gh", "claude"):
            self.assertIn(name, caught.exception.detail)

    def test_NC_resolution_happens_on_a_DRY_RUN_too(self):
        # The dry run exists to discover that this machine cannot host the
        # service BEFORE the service is installed, not after.
        with self.assertRaises(BusError):
            W.install(ARGV_ARMED, dry_run=True, which=fake_which({}))
        self.assertFalse(Path(W.plist_path()).is_file())

    def test_the_derived_path_can_find_every_required_executable_here(self):
        # The invariant, checked against THIS machine whatever it is: whatever the
        # derivation produces, the tools are findable on it. Asserting instead that
        # some tool is MISSING from launchd's default PATH would encode one
        # machine's layout -- true on the operator's laptop, false on a CI runner
        # that ships `gh` in /usr/bin, and a statement about neither the code nor
        # the repair.
        import shutil
        names = W.required_executables(ARGV_ARMED)
        try:
            resolved = W.resolve_executables(names)
        except BusError:
            self.skipTest("this machine does not have the armed-service tools")
        derived = W.service_path(resolved)
        for name in names:
            with self.subTest(name=name):
                self.assertIsNotNone(shutil.which(name, path=derived))

    def test_NC_a_tool_outside_the_launchd_defaults_is_why_derivation_exists(self):
        # The defect, stated portably: when a required tool lives somewhere
        # launchd's default PATH does not cover, the derived PATH covers it and
        # the defaults alone do not.
        import shutil
        resolved = W.resolve_executables(("git", "gh"), fake_which(
            {"git": "/usr/bin/git", "gh": "/opt/tools/bin/gh"}))
        derived = W.service_path(resolved)
        self.assertIn("/opt/tools/bin", derived.split(":"))
        self.assertNotIn("/opt/tools/bin", W.LAUNCHD_DEFAULT_PATH)


class TestControlledRuntimeFailure(unittest.TestCase):
    """A launch failure is a failure, not a crash."""

    def test_NC_a_missing_executable_is_a_bus_error_not_a_FileNotFoundError(self):
        from agent_bus.shell import Runner
        with self.assertRaises(BusError) as caught:
            Runner()(["definitely-not-a-real-binary-xyz"])
        self.assertEqual(caught.exception.code, E.EXECUTABLE_NOT_FOUND)

    def test_NC_a_missing_executable_backs_off_instead_of_killing_the_loop(self):
        missing = Recorder([BusError(E.EXECUTABLE_NOT_FOUND, "'gh' is not on PATH")])
        log = watcher(missing, interval=120, sleep=Sleeper()).run(cycles=3)
        self.assertEqual([e["outcome"] for e in log], ["failed"] * 3)
        self.assertEqual([e["code"] for e in log], [E.EXECUTABLE_NOT_FOUND] * 3)
        self.assertEqual([e["sleep"] for e in log], [60, 120, 240])

    def test_NC_github_being_unreachable_backs_off_instead_of_killing_the_loop(self):
        unreachable = Recorder([AuthorityError("gh api failed reading issue 1")])
        log = watcher(unreachable, interval=120, sleep=Sleeper()).run(cycles=2)
        self.assertEqual([e["code"] for e in log], [E.AUTHORITY_UNRESOLVED] * 2)
        self.assertEqual([e["sleep"] for e in log], [60, 120])

    def test_a_failed_git_command_speaks_the_bus_vocabulary(self):
        from agent_bus.shell import Completed
        class Failing:
            def __call__(self, argv, stdin=None, timeout=None):
                return Completed(tuple(argv), 128, "", "not a git repository")
        with self.assertRaises(BusError) as caught:
            inspect("/tmp/not-a-repo", Failing())
        self.assertEqual(caught.exception.code, E.GIT_FAILED)

    def test_a_hung_command_becomes_a_timeout_failure(self):
        import subprocess
        from agent_bus.shell import Runner
        with self.assertRaises(BusError) as caught:
            Runner()([sys_executable(), "-c", "import time; time.sleep(5)"], timeout=1)
        self.assertEqual(caught.exception.code, E.COMMAND_TIMEOUT)


def sys_executable() -> str:
    import sys
    return sys.executable


class TestPerCycleLogging(unittest.TestCase):
    """A healthy watcher must be visible while it is healthy."""

    def test_one_record_is_emitted_per_cycle(self):
        emitter = Emitter()
        log = watcher(Recorder([{"action": "NONE"}]), interval=60,
                      sleep=Sleeper(), emit=emitter).run(cycles=3)
        self.assertEqual(len(emitter.entries), 3)
        self.assertEqual(emitter.entries, log)

    def test_NC_the_record_is_emitted_BEFORE_the_sleep_not_after_it(self):
        journal: list = []
        watcher(Recorder([{"action": "NONE"}]), interval=60,
                sleep=Sleeper(journal), emit=Emitter(journal)).run(cycles=2)
        self.assertEqual(journal,
                         [("emitted", 1), ("slept", 60), ("emitted", 2)])

    def test_a_failing_cycle_is_emitted_too_with_its_code_and_detail(self):
        emitter = Emitter()
        watcher(Recorder([BusError(E.TRANSPORT_FAILED, "quota exhausted")]),
                interval=60, sleep=Sleeper(), emit=emitter).run(cycles=1)
        entry = emitter.entries[0]
        self.assertEqual(entry["code"], E.TRANSPORT_FAILED)
        self.assertEqual(entry["detail"], "quota exhausted")
        self.assertTrue(entry["quota"])

    def test_each_record_carries_a_timestamp_and_the_cycle_number(self):
        emitter = Emitter()
        watcher(Recorder([{"action": "NONE"}]), interval=60,
                sleep=Sleeper(), emit=emitter).run(cycles=2)
        self.assertEqual([e["cycle"] for e in emitter.entries], [1, 2])
        self.assertTrue(all(e["at"].endswith("Z") for e in emitter.entries))

    def test_the_default_emitter_writes_one_flushed_json_line(self):
        import io, contextlib, json as _json
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            W._stdout_line({"cycle": 1, "outcome": "polled"})
        line = buffer.getvalue()
        self.assertTrue(line.endswith("\n"))
        self.assertEqual(_json.loads(line), {"cycle": 1, "outcome": "polled"})

    def test_NC_a_watcher_that_only_returned_its_log_would_log_nothing_while_running(self):
        # The returned log is produced when the loop ENDS. For an installed agent
        # the loop never ends, which is why the emitter exists at all.
        emitter = Emitter()
        loop = watcher(Recorder([{"action": "NONE"}]), interval=60,
                       sleep=Sleeper(), emit=emitter)
        loop.request_stop()
        self.assertEqual(loop.run(cycles=3), [])
        self.assertEqual(emitter.entries, [])


class TestServiceSurfaces(unittest.TestCase):
    def test_install_changes_nothing_without_an_explicit_apply(self):
        plan = W.install(["python3", "-m", "agent_bus"], dry_run=True)
        self.assertTrue(plan["dry_run"])
        self.assertIn("<key>Label</key>", plan["document"])
        self.assertFalse(Path(plan["plist"]).is_file())

    def test_the_agent_restarts_itself_and_throttles_its_restarts(self):
        document = W.plist(["python3", "-m", "agent_bus"])
        for key in ("<key>KeepAlive</key>", "<key>RunAtLoad</key>",
                    "<key>ThrottleInterval</key>"):
            self.assertIn(key, document)

    def test_the_service_never_writes_inside_the_claude_configuration(self):
        document = W.plist(["python3", "-m", "agent_bus"])
        self.assertNotIn("/.claude", document)
        self.assertNotIn("/.claude", str(W.plist_path()))

    def test_every_service_verb_exists_and_is_dry_run_by_default(self):
        verbs = {
            "install": W.install(["x"]),
            "uninstall": W.uninstall(),
            "start": W.service_control("start"),
            "stop": W.service_control("stop"),
        }
        for name, plan in verbs.items():
            with self.subTest(verb=name):
                self.assertTrue(plan["dry_run"])
                self.assertEqual(plan["launchctl"][0], "launchctl")

    def test_status_reports_what_is_actually_on_the_machine(self):
        class NotLoaded:
            def __call__(self, argv, stdin=None, timeout=None):
                from agent_bus.shell import Completed
                return Completed(tuple(argv), 1, "", "could not find service")
        report = W.status(REPO_PATH, run=NotLoaded())
        self.assertFalse(report["loaded"])
        self.assertIn("plist_installed", report)
        self.assertIn("lock_present", report)


if __name__ == "__main__":
    unittest.main()
