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
    def __init__(self):
        self.slept: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.slept.append(seconds)


class TestWatcher(unittest.TestCase):
    def test_a_quiet_watcher_sleeps_the_full_interval_every_cycle(self):
        sleeper = Sleeper()
        watcher = W.Watcher(Recorder([{"action": "NONE"}]), interval=120,
                            sleep=sleeper)
        log = watcher.run(cycles=3)
        self.assertEqual([entry["sleep"] for entry in log], [120, 120, 120])
        # The final cycle does not sleep: the loop is leaving, not waiting.
        self.assertEqual(sleeper.slept, [120, 120])

    def test_NC_repeated_failures_back_off_instead_of_hot_looping(self):
        sleeper = Sleeper()
        failing = Recorder([BusError(E.TRANSPORT_FAILED, "claude exited 1")])
        log = W.Watcher(failing, interval=120, sleep=sleeper).run(cycles=4)
        delays = [entry["sleep"] for entry in log]
        self.assertEqual(delays, [60, 120, 240, 480])
        self.assertEqual(delays, sorted(delays))
        self.assertTrue(all(d > 0 for d in delays))

    def test_NC_a_quota_refusal_backs_off_on_its_own_longer_schedule(self):
        sleeper = Sleeper()
        quota = Recorder([BusError(E.TRANSPORT_FAILED, "429 rate limit reached")])
        log = W.Watcher(quota, interval=120, sleep=sleeper).run(cycles=3)
        self.assertEqual([entry["sleep"] for entry in log], [900, 1800, 3600])
        self.assertTrue(all(entry["quota"] for entry in log))

    def test_backoff_is_capped(self):
        backoff = W.Backoff()
        self.assertEqual(backoff.delay(99), backoff.cap)
        self.assertEqual(backoff.delay(99, quota=True), backoff.quota_cap)

    def test_a_success_after_failures_resets_the_schedule(self):
        answers = [BusError(E.TRANSPORT_FAILED, "boom"), {"action": "NONE"}]
        recorder = Recorder(answers)
        log = W.Watcher(recorder, interval=60, sleep=Sleeper()).run(cycles=2)
        self.assertEqual([entry["sleep"] for entry in log], [60, 60])
        self.assertEqual(log[0]["outcome"], "failed")
        self.assertEqual(log[1]["outcome"], "polled")

    def test_NC_an_interval_below_the_floor_is_refused(self):
        with self.assertRaises(BusError) as caught:
            W.Watcher(Recorder([{}]), interval=1)
        self.assertEqual(caught.exception.code, E.BAD_VALUE)

    def test_a_stop_request_ends_the_loop_cleanly(self):
        sleeper = Sleeper()
        watcher = W.Watcher(Recorder([{"action": "NONE"}]), interval=60, sleep=sleeper)
        watcher.request_stop()
        self.assertEqual(watcher.run(cycles=5), [])
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
            W.Watcher(Recorder([{"action": "NONE"}]), interval=60,
                      sleep=Sleeper(), lock=lock).run(cycles=1)
            W.SingleInstance(path).acquire().release()


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
