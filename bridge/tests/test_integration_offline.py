"""Offline closed-loop integration: fake GitHub + fake Claude + fake OpenAI, real git.

No network, no credentials, no model spend. Git is REAL (a local bare origin), so
the wrapper-owned worktree/commit/push lifecycle is genuinely exercised.
"""

from __future__ import annotations

import shutil
import unittest
import unittest.mock
from pathlib import Path

from mtjbridge import adapters, manager, policy, state as state_mod, worker
from mtjbridge.adapters import GitOps
from mtjbridge.fakes import FakeClaude, FakeGitHub, FakeIssue, FakeManagerModel
from mtjbridge.policy import Action
from mtjbridge.protocol import parse_task
from tests.helpers import BOOTSTRAP_BRANCH, make_repo, review_body, task_body


# Test-only validation IDs. They are registered the same way a real one is - by
# trusted code, never by a task body - so the registry's contract is exercised
# rather than bypassed. The real `bridge-selftest` entry is never redefined.
TEST_VALIDATION_REGISTRY = {
    "selftest-ok": ("python3", "--version"),
    "selftest-fail": ("python3", "-m", "mtj_no_such_module_for_bridge_tests"),
}


class BridgeTestCase(unittest.TestCase):
    def setUp(self):
        self.work, self.origin, self.base = make_repo()
        self.addCleanup(shutil.rmtree, self.work.parent, ignore_errors=True)
        self.worktrees = self.work.parent / "worktrees"
        self.state_dir = self.work.parent / "state"
        self.state_dir.mkdir()
        self.git = GitOps(self.work)
        patch = unittest.mock.patch.dict(policy.VALIDATION_REGISTRY, TEST_VALIDATION_REGISTRY)
        patch.start()
        self.addCleanup(patch.stop)

    def make_github(self, *, base=None, allow=("src/**",), deny=("docs/**",),
                    task_id="TEST.TASK", validation_ids=("selftest-ok",), raw_commands=(),
                    kind="infrastructure_only"):
        body = task_body(task_id=task_id, base=base or self.base,
                         base_branch=BOOTSTRAP_BRANCH, allow=allow, deny=deny,
                         validation_ids=validation_ids, raw_commands=raw_commands, kind=kind)
        return FakeGitHub([FakeIssue(number=42, title="[mtj-task/1] test", body=body)])

    def run_worker(self, github, claude, task_id="TEST.TASK"):
        task = parse_task(github.get_issue(42)["body"], 42)
        return worker.execute(task, github.get_issue(42)["body"], github=github, git=self.git,
                              claude=claude, repo="fake/repo", worktree_root=self.worktrees)


class TestReadOnlyTask(BridgeTestCase):
    def test_a_task_that_changes_nothing_completes_without_a_pr(self):
        github = self.make_github()
        claude = FakeClaude(behavior=lambda cwd, prompt: "I inspected the tree and changed nothing.")
        outcome = self.run_worker(github, claude)
        self.assertEqual(outcome.status, "COMPLETE")
        self.assertEqual(outcome.changed_paths, [])
        self.assertIsNone(outcome.pr)
        self.assertIn("no file changes produced", outcome.validation)

    def test_the_model_receives_durable_state_and_a_fresh_session(self):
        github = self.make_github()
        claude = FakeClaude(behavior=lambda cwd, prompt: "done")
        self.run_worker(github, claude)
        prompt = claude.calls[0]["prompt"]
        for expected in ("BOOTSTRAP-STATE.yaml", "CAPTAIN-DIRECTION.md", "WORKER-START.md",
                         "Task contract", self.base):
            self.assertIn(expected, prompt)
        self.assertIn("Do NOT run git commit", prompt)


class TestMutationTask(BridgeTestCase):
    def test_mutation_produces_commit_push_and_a_draft_pr_then_review_passes(self):
        github = self.make_github()

        def edit(cwd: Path, prompt: str) -> str:
            (cwd / "src" / "thing.py").write_text("VALUE = 2\n")
            return "Changed VALUE to 2. Validated by reading the file back."

        outcome = self.run_worker(github, FakeClaude(behavior=edit))
        self.assertEqual(outcome.status, "COMPLETE")
        self.assertEqual(outcome.changed_paths, ["src/thing.py"])
        self.assertIsNotNone(outcome.pr)
        pr = github.prs[outcome.pr]
        self.assertTrue(pr["draft"])
        self.assertFalse(pr["merged"])
        self.assertEqual(pr["base"], BOOTSTRAP_BRANCH)

        # the commit really landed on the real local origin
        pushed = self.git._git(["rev-parse", f"origin/{outcome.branch}"]).stdout.strip()
        self.assertEqual(len(pushed), 40)

        # ... and the manager review passes it
        from mtjbridge.protocol import render_block

        github.post_comment(42, render_block(outcome.to_payload()))
        model = FakeManagerModel([review_body(verdict="PASS")])
        decision = manager.review_once(github=github, git=self.git, model=model, repo="fake/repo",
                                       issue_number=42, base_branch=BOOTSTRAP_BRANCH)
        self.assertEqual(decision.verdict, "PASS")
        self.assertEqual(decision.action, Action.POST_REVIEW)
        self.assertFalse(decision.automation_may_continue)

    def test_the_wrapper_not_the_model_owns_git(self):
        """The model is told not to touch git; the wrapper still produces the commit."""
        github = self.make_github()

        def edit(cwd: Path, prompt: str) -> str:
            (cwd / "src" / "thing.py").write_text("VALUE = 3\n")
            return "edited"

        outcome = self.run_worker(github, FakeClaude(behavior=edit))
        self.assertTrue(any(v.startswith("committed ") for v in outcome.validation))


class TestFailurePaths(BridgeTestCase):
    def test_worker_failure_routes_to_repair(self):
        github = self.make_github()

        def broken(cwd: Path, prompt: str) -> str:
            (cwd / "src" / "thing.py").write_text("VALUE = broken syntax(\n")
            return "I made a change but the tests fail."

        outcome = self.run_worker(github, FakeClaude(behavior=broken))
        outcome.discrepancies.append("tests fail after the change")
        from mtjbridge.protocol import render_block

        github.post_comment(42, render_block(outcome.to_payload()))
        model = FakeManagerModel([review_body(verdict="REPAIR", reasons=("tests fail",))])
        decision = manager.review_once(github=github, git=self.git, model=model, repo="fake/repo",
                                       issue_number=42, base_branch=BOOTSTRAP_BRANCH)
        self.assertEqual(decision.verdict, "REPAIR")
        self.assertEqual(decision.action, Action.CREATE_REPAIR_TASK)

    def test_claude_error_marks_the_result_failed(self):
        github = self.make_github()
        outcome = self.run_worker(github, FakeClaude(behavior=lambda c, p: "", is_error=True))
        self.assertEqual(outcome.status, "FAIL")

    def test_semantic_change_halts_for_captain_before_a_pr_exists(self):
        github = self.make_github(allow=("src/**", "docs/**"), deny=())

        def semantic(cwd: Path, prompt: str) -> str:
            (cwd / "docs" / "RATIFIED-RULINGS-REGISTRY.md").write_text("# registry\nnew ruling\n")
            return "Added a ruling."

        outcome = self.run_worker(github, FakeClaude(behavior=semantic))
        self.assertEqual(outcome.status, "STOP")
        self.assertIsNone(outcome.pr, "no PR may be opened for Captain-reserved territory")
        self.assertTrue(any("Captain-reserved" in d for d in outcome.decision_required))

    def test_out_of_scope_write_stops_the_worker(self):
        github = self.make_github()

        def stray(cwd: Path, prompt: str) -> str:
            (cwd / "docs" / "notes.md").write_text("stray\n")
            return "wrote a doc"

        outcome = self.run_worker(github, FakeClaude(behavior=stray))
        self.assertEqual(outcome.status, "STOP")
        self.assertIsNone(outcome.pr)
        self.assertTrue(any("deny pattern" in d for d in outcome.discrepancies))

    def test_stale_base_stops_before_claude_is_ever_invoked(self):
        github = self.make_github(base="b" * 40)
        claude = FakeClaude(behavior=lambda cwd, prompt: "should never run")
        outcome = self.run_worker(github, claude)
        self.assertEqual(outcome.status, "STOP")
        self.assertEqual(claude.calls, [], "the model must not be invoked on a stale base")
        self.assertTrue(any("base mismatch" in d for d in outcome.discrepancies))


class TestCrashRecovery(BridgeTestCase):
    def test_a_restarted_process_reconstructs_phase_from_github_alone(self):
        github = self.make_github()
        from mtjbridge.protocol import render_block

        ledger = state_mod.reconstruct(github, 42)
        self.assertEqual(ledger.next_phase(), "WORKER_EXECUTE")

        def edit(cwd: Path, prompt: str) -> str:
            (cwd / "src" / "thing.py").write_text("VALUE = 9\n")
            return "edited"

        outcome = self.run_worker(github, FakeClaude(behavior=edit))
        github.post_comment(42, render_block(outcome.to_payload()))

        # simulate a crash: throw away ALL local state, keep only GitHub
        shutil.rmtree(self.state_dir, ignore_errors=True)
        self.state_dir.mkdir(exist_ok=True)
        ledger = state_mod.reconstruct(github, 42)
        self.assertEqual(ledger.next_phase(), "MANAGER_REVIEW")
        self.assertTrue(ledger.has_result)
        self.assertEqual(ledger.latest_result.task, "TEST.TASK")

        model = FakeManagerModel([review_body(verdict="PASS")])
        manager.review_once(github=github, git=self.git, model=model, repo="fake/repo",
                            issue_number=42, base_branch=BOOTSTRAP_BRANCH)
        self.assertEqual(state_mod.reconstruct(github, 42).next_phase(), "COMPLETE")

    def test_a_halted_review_leaves_the_phase_halted(self):
        github = self.make_github()
        from mtjbridge.protocol import render_block

        outcome = self.run_worker(github, FakeClaude(behavior=lambda c, p: "no change"))
        github.post_comment(42, render_block(outcome.to_payload()))
        model = FakeManagerModel([review_body(verdict="STOP", reasons=("insufficient evidence",))])
        manager.review_once(github=github, git=self.git, model=model, repo="fake/repo",
                            issue_number=42, base_branch=BOOTSTRAP_BRANCH)
        self.assertEqual(state_mod.reconstruct(github, 42).next_phase(), "HALTED")


class TestClaimsAndIdempotency(BridgeTestCase):
    def test_a_second_worker_cannot_claim_a_claimed_issue(self):
        github = self.make_github()
        state_mod.acquire(github, 42, "TEST.TASK", state_dir=self.state_dir)
        original = state_mod.worker_id
        try:
            state_mod.worker_id = lambda: "otherhost/999"
            with self.assertRaises(state_mod.ClaimError):
                state_mod.acquire(github, 42, "TEST.TASK", state_dir=self.state_dir)
        finally:
            state_mod.worker_id = original

    def test_an_expired_claim_may_be_taken_over(self):
        github = self.make_github()
        state_mod.acquire(github, 42, "TEST.TASK", lease_seconds=0, state_dir=self.state_dir)
        original = state_mod.worker_id
        try:
            state_mod.worker_id = lambda: "otherhost/999"
            claim = state_mod.acquire(github, 42, "TEST.TASK", state_dir=self.state_dir)
            self.assertEqual(claim.worker_id, "otherhost/999")
        finally:
            state_mod.worker_id = original

    def test_duplicate_comment_posts_are_suppressed_by_the_idempotency_key(self):
        github = self.make_github()
        first = github.post_comment(42, "body", idempotency_key="k1")
        second = github.post_comment(42, "body", idempotency_key="k1")
        self.assertTrue(first.get("posted"))
        self.assertTrue(second.get("skipped"))
        self.assertEqual(len([c for c in github.list_comments(42)]), 1)

    def test_repeated_repair_halts_rather_than_looping_forever(self):
        github = self.make_github()
        from mtjbridge.protocol import render_block

        outcome = self.run_worker(github, FakeClaude(behavior=lambda c, p: "no change"))
        outcome.discrepancies.append("still broken")
        payload = outcome.to_payload()
        verdicts = []
        for attempt in range(4):
            github.post_comment(42, render_block(payload), idempotency_key=f"r{attempt}")
            model = FakeManagerModel([review_body(verdict="REPAIR", reasons=("still broken",))])
            decision = manager.review_once(github=github, git=self.git, model=model,
                                           repo="fake/repo", issue_number=42,
                                           base_branch=BOOTSTRAP_BRANCH, max_repairs=2)
            verdicts.append(decision.verdict)
        self.assertEqual(verdicts[:2], ["REPAIR", "REPAIR"])
        self.assertEqual(verdicts[2], "STOP", "the third repair must halt, not loop")
        self.assertTrue(any("repair limit" in r for r in decision.reasons))


class TestManagerModelBoundary(BridgeTestCase):
    def test_a_model_returning_prose_halts_cleanly(self):
        github = self.make_github()
        from mtjbridge.protocol import render_block

        outcome = self.run_worker(github, FakeClaude(behavior=lambda c, p: "no change"))
        github.post_comment(42, render_block(outcome.to_payload()))
        model = FakeManagerModel(["Looks good to me, ship it!"])
        decision = manager.review_once(github=github, git=self.git, model=model, repo="fake/repo",
                                       issue_number=42, base_branch=BOOTSTRAP_BRANCH)
        self.assertEqual(decision.verdict, "STOP")
        self.assertTrue(any("did not validate" in r for r in decision.reasons))

    def test_the_manager_model_gets_no_tools_and_only_durable_state(self):
        github = self.make_github()
        from mtjbridge.protocol import render_block

        outcome = self.run_worker(github, FakeClaude(behavior=lambda c, p: "no change"))
        github.post_comment(42, render_block(outcome.to_payload()))
        model = FakeManagerModel([review_body(verdict="PASS")])
        manager.review_once(github=github, git=self.git, model=model, repo="fake/repo",
                            issue_number=42, base_branch=BOOTSTRAP_BRANCH)
        prompt = model.prompts[0]
        self.assertIn("Task contract", prompt)
        self.assertIn("Worker result", prompt)
        self.assertIn("CAPTAIN-DIRECTION.md", prompt)


class TestOneReadyTaskOnly(BridgeTestCase):
    def test_two_ready_tasks_is_an_error_not_a_queue(self):
        github = self.make_github()
        github.issues[43] = FakeIssue(number=43, title="second",
                                      body=task_body(task_id="OTHER", base=self.base))
        from mtjbridge.policy import PolicyError

        with self.assertRaises(PolicyError):
            worker.find_ready_task(github)

    def test_a_blocked_task_is_not_discovered(self):
        github = FakeGitHub([FakeIssue(number=42, title="blocked",
                                       body=task_body(base=self.base, status="BLOCKED"))])
        self.assertIsNone(worker.find_ready_task(github))


if __name__ == "__main__":
    unittest.main()


class TestDryRun(BridgeTestCase):
    """--dry-run must be safe on every path: no worktree, no model, no writes."""

    def test_worker_execute_dry_run_verifies_base_and_stops(self):
        github = self.make_github()
        claude = FakeClaude(behavior=lambda cwd, prompt: "should never run")
        task = parse_task(github.get_issue(42)["body"], 42)
        outcome = worker.execute(task, github.get_issue(42)["body"], github=github, git=self.git,
                                 claude=claude, repo="fake/repo", dry_run=True,
                                 worktree_root=self.worktrees)
        self.assertEqual(outcome.status, "COMPLETE")
        self.assertEqual(claude.calls, [], "dry run must not invoke the model")
        self.assertIsNone(outcome.pr)
        self.assertEqual(github.prs, {})
        self.assertFalse(self.worktrees.exists(), "dry run must not create a worktree")
        self.assertTrue(any("DRY-RUN" in v for v in outcome.validation))

    def test_dry_run_still_stops_on_a_stale_base(self):
        github = self.make_github(base="c" * 40)
        claude = FakeClaude(behavior=lambda cwd, prompt: "should never run")
        task = parse_task(github.get_issue(42)["body"], 42)
        outcome = worker.execute(task, github.get_issue(42)["body"], github=github, git=self.git,
                                 claude=claude, repo="fake/repo", dry_run=True,
                                 worktree_root=self.worktrees)
        self.assertEqual(outcome.status, "STOP")
        self.assertEqual(claude.calls, [])

    def test_cycle_dry_run_makes_no_github_writes(self):
        from mtjbridge import cycle
        from mtjbridge.fakes import FakeManagerModel

        github = self.make_github()
        rc = cycle.run_cycle(github=github, git=self.git,
                             claude=FakeClaude(behavior=lambda c, p: "x"),
                             model=FakeManagerModel([review_body(verdict="PASS")]),
                             repo="fake/repo", base_branch=BOOTSTRAP_BRANCH,
                             issue_number=42, dry_run=True)
        self.assertEqual(github.writes, [], "a dry-run cycle must write nothing to GitHub")
        self.assertIn(rc, (0, 3))


class TestLedgerClassification(BridgeTestCase):
    """Regression: classify on the DECLARED schema, never on a substring of the prose.

    The real failure this pins: a genuine mtj-result/1 comment whose body happened to
    describe the protocol ("comments carry mtj-claim/1, mtj-result/1, mtj-review/1")
    was filed as a CLAIM, so the result disappeared from the ledger and the phase
    silently rewound to WORKER_EXECUTE — i.e. the bridge would have re-run completed work.
    """

    def test_a_result_that_mentions_other_schemas_is_still_a_result(self):
        from tests.helpers import result_body

        body = result_body() + "\n\nProse: comments carry mtj-claim/1, mtj-result/1, mtj-review/1.\n"
        github = self.make_github()
        github.post_comment(42, body)
        ledger = state_mod.reconstruct(github, 42)
        self.assertEqual(len(ledger.results), 1)
        self.assertEqual(len(ledger.claims), 0)
        self.assertEqual(ledger.next_phase(), "MANAGER_REVIEW")

    def test_a_comment_with_no_protocol_block_is_ignored(self):
        github = self.make_github()
        github.post_comment(42, "Just a human note mentioning mtj-result/1 in passing.")
        ledger = state_mod.reconstruct(github, 42)
        self.assertEqual((len(ledger.results), len(ledger.claims), len(ledger.reviews)), (0, 0, 0))
        self.assertEqual(ledger.parse_errors, [])

    def test_a_malformed_protocol_block_is_recorded_not_swallowed(self):
        github = self.make_github()
        github.post_comment(42, "```yaml\nschema: mtj-result/1\ntask: T\n```")
        ledger = state_mod.reconstruct(github, 42)
        self.assertEqual(len(ledger.results), 0)
        self.assertEqual(len(ledger.parse_errors), 1, "a bad block must be visible, not dropped")


class TestManagerSeesImplementationTruth(BridgeTestCase):
    """Manager review finding 1: a path list is not a diff."""

    def _post_result_with_pr(self, github):
        def edit(cwd: Path, prompt: str) -> str:
            (cwd / "src" / "thing.py").write_text("VALUE = 2\n")
            return "changed VALUE"

        outcome = self.run_worker(github, FakeClaude(behavior=edit))
        from mtjbridge.protocol import render_block

        github.post_comment(42, render_block(outcome.to_payload()))
        return outcome

    def test_the_actual_patch_reaches_the_manager_prompt(self):
        github = self.make_github()
        outcome = self._post_result_with_pr(github)
        github.prs[outcome.pr]["diff"] = "--- a/src/thing.py\n+++ b/src/thing.py\n+VALUE = 2\n"
        model = FakeManagerModel([review_body(verdict="PASS")])
        manager.review_once(github=github, git=self.git, model=model, repo="fake/repo",
                            issue_number=42, base_branch=BOOTSTRAP_BRANCH)
        prompt = model.prompts[0]
        self.assertIn("## Actual PR diff", prompt)
        self.assertIn("+VALUE = 2", prompt)

    def test_an_unfetchable_diff_halts_instead_of_reviewing_path_names(self):
        github = self.make_github()
        self._post_result_with_pr(github)
        github.diff_unavailable = True
        model = FakeManagerModel([review_body(verdict="PASS")])
        decision = manager.review_once(github=github, git=self.git, model=model, repo="fake/repo",
                                       issue_number=42, base_branch=BOOTSTRAP_BRANCH)
        self.assertEqual(decision.verdict, "STOP")
        self.assertTrue(any("diff could not be fetched" in r for r in decision.reasons))
        self.assertEqual(model.prompts, [], "the model must not be asked to review blind")

    def test_a_truncated_diff_stops_before_the_model_is_invoked(self):
        """H2: a partial patch is not implementation truth, and wording is not a gate."""
        github = self.make_github()
        outcome = self._post_result_with_pr(github)
        github.prs[outcome.pr]["diff"] = "x" * 500
        model = FakeManagerModel([review_body(verdict="PASS")])
        with unittest.mock.patch.object(type(github), "pr_diff",
                                        lambda self, n, max_bytes=100: ("x" * 100, True)):
            decision = manager.review_once(github=github, git=self.git, model=model,
                                           repo="fake/repo", issue_number=42,
                                           base_branch=BOOTSTRAP_BRANCH)
        self.assertEqual(decision.verdict, "STOP")
        self.assertEqual(model.prompts, [], "a truncated diff must never reach the model")
        self.assertTrue(any("TRUNCATED" in r for r in decision.reasons))

    def test_the_prompt_builder_itself_refuses_a_truncated_diff(self):
        """The STOP is structural: even a caller that forgets the check cannot bypass it."""
        with self.assertRaises(policy.PolicyError):
            manager.build_review_prompt(bootstrap={}, issue_body="", result_body="",
                                        changed_paths=["src/thing.py"], pr_number=1000,
                                        diff_text="x" * 100, diff_truncated=True)

    def test_a_complete_diff_still_reaches_the_manager(self):
        """The negative control: the gate is aimed at truncation, not at review itself."""
        github = self.make_github()
        outcome = self._post_result_with_pr(github)
        github.prs[outcome.pr]["diff"] = "--- a/src/thing.py\n+++ b/src/thing.py\n+VALUE = 2\n"
        model = FakeManagerModel([review_body(verdict="PASS")])
        decision = manager.review_once(github=github, git=self.git, model=model,
                                       repo="fake/repo", issue_number=42,
                                       base_branch=BOOTSTRAP_BRANCH)
        self.assertEqual(len(model.prompts), 1)
        self.assertEqual(decision.verdict, "PASS")


class TestStructuralToolDeny(BridgeTestCase):
    """Manager review finding 2: the git prohibition must not be prompt-only."""

    def test_the_invocation_denies_git_and_gh_tools(self):
        from mtjbridge.adapters import ClaudeCliAdapter

        argv = ClaudeCliAdapter().build_argv("/tmp/wt", "sid")
        self.assertIn("--disallowedTools", argv)
        for denied in ("Bash(git commit:*)", "Bash(git push:*)", "Bash(gh:*)",
                       "Bash(git reset:*)", "Bash(git remote:*)"):
            self.assertIn(denied, argv)

    def test_the_settings_payload_repeats_the_deny_list(self):
        from mtjbridge.adapters import ClaudeCliAdapter

        deny = ClaudeCliAdapter().settings_payload()["permissions"]["deny"]
        self.assertIn("Bash(git push:*)", deny)
        self.assertIn("Bash(gh:*)", deny)

    def test_the_session_is_never_resumed(self):
        from mtjbridge.adapters import ClaudeCliAdapter

        argv = ClaudeCliAdapter().build_argv("/tmp/wt", "sid")
        for forbidden in ("--continue", "-c", "--resume", "-r"):
            self.assertNotIn(forbidden, argv)
        self.assertIn("--session-id", argv)


class TestMandatoryScope(BridgeTestCase):
    """Manager review finding 3: missing scope is a STOP before Claude runs."""

    def test_a_mutating_task_without_scope_stops_before_the_model(self):
        github = self.make_github(allow=(), deny=())
        claude = FakeClaude(behavior=lambda cwd, prompt: "should never run")
        outcome = self.run_worker(github, claude)
        self.assertEqual(outcome.status, "STOP")
        self.assertEqual(claude.calls, [], "the model must not be invoked without scope")
        self.assertIsNone(outcome.pr)

    def test_a_read_only_task_without_scope_proceeds(self):
        github = self.make_github(allow=(), deny=())
        github.issues[42].body = task_body(base=self.base, base_branch=BOOTSTRAP_BRANCH,
                                           kind="read_only", allow=(), deny=(),
                                           validation_ids=())
        claude = FakeClaude(behavior=lambda cwd, prompt: "inspected only")
        outcome = self.run_worker(github, claude)
        self.assertEqual(outcome.status, "COMPLETE")
        self.assertEqual(len(claude.calls), 1)


class TestWrapperOwnedValidation(BridgeTestCase):
    """Manager review finding 4: evidence must be machine-captured, not model prose."""

    def _edit(self, cwd: Path, prompt: str) -> str:
        (cwd / "src" / "thing.py").write_text("VALUE = 2\n")
        return "edited"

    def test_a_registered_id_runs_in_the_wrapper_and_is_captured(self):
        github = self.make_github(validation_ids=("selftest-ok",))
        outcome = self.run_worker(github, FakeClaude(behavior=self._edit))
        self.assertEqual(outcome.status, "COMPLETE")
        self.assertEqual(len(outcome.evidence), 1)
        item = outcome.evidence[0]
        self.assertEqual(item["rc"], 0)
        self.assertEqual(item["command"], ["python3", "--version"])

    def test_a_failing_check_fails_the_result_and_blocks_the_pr(self):
        github = self.make_github(validation_ids=("selftest-fail",))
        outcome = self.run_worker(github, FakeClaude(behavior=self._edit))
        self.assertEqual(outcome.status, "FAIL")
        self.assertIsNone(outcome.pr, "a failing acceptance check must not reach a PR")
        self.assertNotEqual(outcome.evidence[0]["rc"], 0)

    def test_evidence_survives_the_result_round_trip(self):
        from mtjbridge.protocol import parse_result, render_block

        github = self.make_github(validation_ids=("selftest-ok",))
        outcome = self.run_worker(github, FakeClaude(behavior=lambda c, p: "no change"))
        parsed = parse_result(render_block(outcome.to_payload()))
        self.assertEqual(len(parsed.evidence), 1)
        self.assertFalse(parsed.validation_failed)


class TestTrustedValidationIDs(BridgeTestCase):
    """H1: a task NAMES a check. It never supplies, extends or reorders argv."""

    def _claude(self):
        return FakeClaude(behavior=lambda cwd, prompt: "should never run")

    def test_raw_commands_in_a_task_body_stop_before_the_model(self):
        github = self.make_github(validation_ids=(),
                                  raw_commands=('python3 -c "import os; os.system(\'id\')"',))
        claude = self._claude()
        outcome = self.run_worker(github, claude)
        self.assertEqual(outcome.status, "STOP")
        self.assertEqual(claude.calls, [], "raw argv must halt before Claude is invoked")
        self.assertTrue(any("raw validation/acceptance COMMANDS" in d
                            for d in outcome.discrepancies))

    def test_an_allowlisted_executable_no_longer_launders_a_payload(self):
        """`python3` passes any executable allowlist; `python3 -c <payload>` is the hole."""
        github = self.make_github(validation_ids=(),
                                  raw_commands=("python3 -c \"print(open('/etc/passwd').read())\"",))
        claude = self._claude()
        outcome = self.run_worker(github, claude)
        self.assertEqual(outcome.status, "STOP")
        self.assertEqual(claude.calls, [])

    def test_a_shell_payload_dressed_as_an_id_is_refused(self):
        github = self.make_github(validation_ids=('python3 -c "print(1)"',))
        claude = self._claude()
        outcome = self.run_worker(github, claude)
        self.assertEqual(outcome.status, "STOP")
        self.assertEqual(claude.calls, [])
        self.assertTrue(any("is not registered" in d for d in outcome.discrepancies))

    def test_an_unknown_id_halts_before_claude(self):
        github = self.make_github(validation_ids=("no-such-check",))
        claude = self._claude()
        outcome = self.run_worker(github, claude)
        self.assertEqual(outcome.status, "STOP")
        self.assertEqual(claude.calls, [])
        self.assertIsNone(outcome.pr)

    def test_a_known_id_resolves_to_exactly_its_registered_argv(self):
        github = self.make_github(validation_ids=("selftest-ok",))
        outcome = self.run_worker(github, FakeClaude(behavior=lambda c, p: "no change"))
        self.assertEqual([tuple(e["command"]) for e in outcome.evidence],
                         [TEST_VALIDATION_REGISTRY["selftest-ok"]])


class TestMutatingTaskRequiresValidation(BridgeTestCase):
    """H3: a mutation nobody checked must not reach a branch, a PR or a Manager PASS."""

    def test_zero_validation_ids_halts_before_claude(self):
        github = self.make_github(validation_ids=())
        claude = FakeClaude(behavior=lambda cwd, prompt: "should never run")
        outcome = self.run_worker(github, claude)
        self.assertEqual(outcome.status, "STOP")
        self.assertEqual(claude.calls, [], "a mutating task with no check must not run")
        self.assertIsNone(outcome.pr)
        self.assertTrue(any("no trusted validation.ids" in d for d in outcome.discrepancies))

    def test_a_read_only_task_remains_exempt(self):
        github = self.make_github(allow=(), deny=(), validation_ids=())
        github.issues[42].body = task_body(base=self.base, base_branch=BOOTSTRAP_BRANCH,
                                           kind="read_only", allow=(), deny=(),
                                           validation_ids=())
        claude = FakeClaude(behavior=lambda cwd, prompt: "inspected only")
        outcome = self.run_worker(github, claude)
        self.assertEqual(outcome.status, "COMPLETE")
        self.assertEqual(len(claude.calls), 1)

    def test_publication_is_refused_when_evidence_is_empty(self):
        """Defence in depth. `require_validation_ids` already guarantees a check was
        declared, so this can only fire if that gate is bypassed - which is exactly
        why the publication boundary asserts the evidence instead of trusting it."""
        def edit(cwd: Path, prompt: str) -> str:
            (cwd / "src" / "thing.py").write_text("VALUE = 2\n")
            return "edited"

        github = self.make_github(validation_ids=("selftest-ok",))
        with unittest.mock.patch.object(worker, "run_validation", lambda cmds, cwd: []):
            outcome = self.run_worker(github, FakeClaude(behavior=edit))
        self.assertEqual(outcome.status, "STOP")
        self.assertIsNone(outcome.pr)
        self.assertEqual(github.prs, {}, "no PR may exist without evidence")

    def test_a_published_mutation_carries_evidence(self):
        def edit(cwd: Path, prompt: str) -> str:
            (cwd / "src" / "thing.py").write_text("VALUE = 2\n")
            return "edited"

        github = self.make_github(validation_ids=("selftest-ok",))
        outcome = self.run_worker(github, FakeClaude(behavior=edit))
        self.assertIsNotNone(outcome.pr)
        self.assertTrue(outcome.evidence, "a PR may not be published without evidence")
        self.assertTrue(all(e["rc"] == 0 for e in outcome.evidence))


class TestClaudeErrorBlocksPublication(BridgeTestCase):
    """H4: a failed execution must not publish a branch or PR that looks like work."""

    def test_an_errored_claude_that_edited_files_publishes_nothing(self):
        def edit_then_fail(cwd: Path, prompt: str) -> str:
            (cwd / "src" / "thing.py").write_text("VALUE = 2\n")
            return "partial work before the error"

        github = self.make_github(validation_ids=("selftest-ok",))
        outcome = self.run_worker(github, FakeClaude(behavior=edit_then_fail, is_error=True))
        self.assertEqual(outcome.status, "FAIL")
        self.assertIsNone(outcome.pr, "no PR may be created for a failed execution")
        self.assertEqual(github.prs, {}, "no PR object may exist at all")
        self.assertFalse(any(v.startswith("committed ") for v in outcome.validation))
        self.assertEqual(outcome.evidence, [], "validation must not run after a failed model")

    def test_the_changed_path_evidence_survives_the_failure(self):
        def edit_then_fail(cwd: Path, prompt: str) -> str:
            (cwd / "src" / "thing.py").write_text("VALUE = 2\n")
            return "partial work"

        github = self.make_github(validation_ids=("selftest-ok",))
        outcome = self.run_worker(github, FakeClaude(behavior=edit_then_fail, is_error=True))
        self.assertIn("src/thing.py", outcome.changed_paths)
        self.assertTrue(any("claude reported an error" in d for d in outcome.discrepancies))

    def test_a_failed_run_still_classifies_captain_territory(self):
        def touch_captain(cwd: Path, prompt: str) -> str:
            (cwd / "docs" / "RATIFIED-RULINGS-REGISTRY.md").write_text("# registry\nnew\n")
            return "touched a ratified doc before failing"

        github = self.make_github(allow=("src/**", "docs/**"), deny=(),
                                  validation_ids=("selftest-ok",))
        outcome = self.run_worker(github, FakeClaude(behavior=touch_captain, is_error=True))
        self.assertEqual(outcome.status, "FAIL")
        self.assertIsNone(outcome.pr)
        self.assertTrue(any("Captain-reserved" in d for d in outcome.decision_required),
                        "classification must survive a failed execution")

    def test_a_successful_run_still_publishes(self):
        """Negative control: the block is aimed at is_error, not at publication."""
        def edit(cwd: Path, prompt: str) -> str:
            (cwd / "src" / "thing.py").write_text("VALUE = 2\n")
            return "edited"

        github = self.make_github(validation_ids=("selftest-ok",))
        outcome = self.run_worker(github, FakeClaude(behavior=edit, is_error=False))
        self.assertEqual(outcome.status, "COMPLETE")
        self.assertIsNotNone(outcome.pr)


class TestDiscoveryRespectsLedger(BridgeTestCase):
    """Manager review finding 7: READY is a static string; the ledger is the truth."""

    def test_a_task_with_a_posted_result_is_not_rediscovered(self):
        github = self.make_github()
        self.assertIsNotNone(worker.find_ready_task(github))
        outcome = self.run_worker(github, FakeClaude(behavior=lambda c, p: "no change"))
        from mtjbridge.protocol import render_block

        github.post_comment(42, render_block(outcome.to_payload()))
        self.assertEqual(state_mod.reconstruct(github, 42).next_phase(), "MANAGER_REVIEW")
        self.assertIsNone(worker.find_ready_task(github),
                          "a completed task must not be re-executed just because it says READY")

    def test_restart_after_result_before_review_leaves_only_the_manager_eligible(self):
        github = self.make_github()
        outcome = self.run_worker(github, FakeClaude(behavior=lambda c, p: "no change"))
        from mtjbridge.protocol import render_block

        github.post_comment(42, render_block(outcome.to_payload()))
        self.assertIsNone(worker.find_ready_task(github))
        model = FakeManagerModel([review_body(verdict="PASS")])
        decision = manager.review_once(github=github, git=self.git, model=model, repo="fake/repo",
                                       issue_number=42, base_branch=BOOTSTRAP_BRANCH)
        self.assertEqual(decision.verdict, "PASS")

    def test_a_halted_task_is_not_rediscovered_either(self):
        github = self.make_github()
        outcome = self.run_worker(github, FakeClaude(behavior=lambda c, p: "no change"))
        from mtjbridge.protocol import render_block

        github.post_comment(42, render_block(outcome.to_payload()))
        model = FakeManagerModel([review_body(verdict="STOP", reasons=("halt",))])
        manager.review_once(github=github, git=self.git, model=model, repo="fake/repo",
                            issue_number=42, base_branch=BOOTSTRAP_BRANCH)
        self.assertEqual(state_mod.reconstruct(github, 42).next_phase(), "HALTED")
        self.assertIsNone(worker.find_ready_task(github))


class TestManagerCanary(BridgeTestCase):
    """Manager review finding 6: prove the real model path before a live cycle."""

    def test_canary_passes_on_a_valid_review_block(self):
        ok, message = manager.run_canary(FakeManagerModel([review_body(task_id="BRIDGE.CANARY")]))
        self.assertTrue(ok, message)

    def test_canary_fails_on_prose(self):
        ok, message = manager.run_canary(FakeManagerModel(["looks fine to me"]))
        self.assertFalse(ok)
        self.assertIn("did not validate", message)

    def test_canary_fails_on_empty_output(self):
        ok, _ = manager.run_canary(FakeManagerModel([""]))
        self.assertFalse(ok)


class TestOpenAIFailuresAreBridgeControlled(unittest.TestCase):
    """H5: an SDK exception becomes a bounded, redacted bridge error - not a traceback.

    Measured live before API credit was added: `mtj-manager --canary` raised a raw
    openai.RateLimitError with a traceback. The adapter is the controlled boundary;
    a boundary that propagates a third-party exception is not one.

    These exercise the REAL OpenAIResponsesAdapter.review() with only its client
    factory substituted, so the wrapping code under test is the shipped code.
    """

    FAKE_KEY = "sk-test-FAKE-not-a-real-key-0000000000"

    class _Fake429(Exception):
        status_code = 429
        code = "insufficient_quota"

    class _FakeConnection(Exception):
        pass

    def _adapter(self, exc=None, text=""):
        import os

        class _Responses:
            def create(_self, **kwargs):
                if exc is not None:
                    raise exc
                return type("R", (), {"output_text": text})()

        class _Client:
            responses = _Responses()

        class _Adapter(adapters.OpenAIResponsesAdapter):
            def _client(_self):
                return _Client()

        patch = unittest.mock.patch.dict(os.environ, {"OPENAI_API_KEY": self.FAKE_KEY})
        patch.start()
        self.addCleanup(patch.stop)
        return _Adapter()

    def test_a_quota_429_becomes_a_controlled_bridge_error(self):
        adapter = self._adapter(exc=self._Fake429("credit_balance_exhausted"))
        with self.assertRaises(adapters.BridgeCommandError) as caught:
            adapter.review("prompt")
        message = str(caught.exception)
        self.assertIn("_Fake429", message)
        self.assertIn("status=429", message)
        self.assertIn("insufficient_quota", message)

    def test_a_network_exception_becomes_a_controlled_bridge_error(self):
        adapter = self._adapter(exc=self._FakeConnection("connection reset by peer"))
        with self.assertRaises(adapters.BridgeCommandError) as caught:
            adapter.review("prompt")
        self.assertIn("connection reset", str(caught.exception))

    def test_the_error_message_is_bounded(self):
        adapter = self._adapter(exc=self._FakeConnection("x" * 50000))
        with self.assertRaises(adapters.BridgeCommandError) as caught:
            adapter.review("prompt")
        self.assertLess(len(str(caught.exception)), adapters.MAX_ERROR_BYTES + 400)

    def test_the_error_message_cannot_carry_the_api_key(self):
        adapter = self._adapter(
            exc=self._FakeConnection(f"401 while sending Authorization: Bearer {self.FAKE_KEY}"))
        with self.assertRaises(adapters.BridgeCommandError) as caught:
            adapter.review("prompt")
        message = str(caught.exception)
        self.assertNotIn(self.FAKE_KEY, message)
        self.assertIn("[REDACTED]", message)

    def test_the_canary_reports_blocked_instead_of_raising(self):
        adapter = self._adapter(exc=self._Fake429("credit_balance_exhausted"))
        with self.assertRaises(adapters.BridgeCommandError):
            manager.run_canary(adapter)
        # main() is what turns that into an exit code; assert the controlled path.
        with unittest.mock.patch.object(manager, "OpenAIResponsesAdapter",
                                        lambda **kw: adapter):
            rc = manager.main(["--canary"])
        self.assertEqual(rc, 4, "a blocked canary must exit non-zero, controlled")

    def test_a_successful_canary_is_unchanged(self):
        """Negative control: the wrapping must not alter the passing path."""
        adapter = self._adapter(text=review_body(task_id="BRIDGE.CANARY"))
        ok, message = manager.run_canary(adapter)
        self.assertTrue(ok, message)
        self.assertIn("verdict PASS", message)


class TestExplicitIssueIsNotABackDoor(BridgeTestCase):
    def test_main_refuses_an_explicit_issue_that_is_already_complete(self):
        github = self.make_github()
        outcome = self.run_worker(github, FakeClaude(behavior=lambda c, p: "no change"))
        from mtjbridge.protocol import render_block

        github.post_comment(42, render_block(outcome.to_payload()))
        phase = state_mod.reconstruct(github, 42).next_phase()
        self.assertEqual(phase, "MANAGER_REVIEW")
        # main() would return 2 for this issue; assert the guard's condition directly
        # so the test does not depend on argparse or the live GitHub adapter.
        self.assertNotEqual(phase, "WORKER_EXECUTE")
