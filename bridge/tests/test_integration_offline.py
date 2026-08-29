"""Offline closed-loop integration: fake GitHub + fake Claude + fake OpenAI, real git.

No network, no credentials, no model spend. Git is REAL (a local bare origin), so
the wrapper-owned worktree/commit/push lifecycle is genuinely exercised.
"""

from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from mtjbridge import manager, state as state_mod, worker
from mtjbridge.adapters import GitOps
from mtjbridge.fakes import FakeClaude, FakeGitHub, FakeIssue, FakeManagerModel
from mtjbridge.policy import Action
from mtjbridge.protocol import parse_task
from tests.helpers import BOOTSTRAP_BRANCH, make_repo, review_body, task_body


class BridgeTestCase(unittest.TestCase):
    def setUp(self):
        self.work, self.origin, self.base = make_repo()
        self.addCleanup(shutil.rmtree, self.work.parent, ignore_errors=True)
        self.worktrees = self.work.parent / "worktrees"
        self.state_dir = self.work.parent / "state"
        self.state_dir.mkdir()
        self.git = GitOps(self.work)

    def make_github(self, *, base=None, allow=("src/**",), deny=("docs/**",), task_id="TEST.TASK"):
        body = task_body(task_id=task_id, base=base or self.base,
                         base_branch=BOOTSTRAP_BRANCH, allow=allow, deny=deny)
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
