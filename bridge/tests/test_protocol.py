"""Unit tests: task / result / review / claim parsing and schema validation."""

import unittest

from mtjbridge.protocol import (ProtocolError, parse_claim, parse_result, parse_review,
                                parse_task, render_block)
from tests.helpers import result_body, review_body, task_body


class TestTaskParser(unittest.TestCase):
    def test_parses_a_well_formed_task(self):
        task = parse_task(task_body(base="a" * 40), issue_number=7)
        self.assertEqual(task.task, "TEST.TASK")
        self.assertEqual(task.base, "a" * 40)
        self.assertTrue(task.is_ready)
        self.assertEqual(task.allow_paths, ["src/**"])
        self.assertEqual(task.deny_paths, ["docs/**"])
        self.assertFalse(task.authorizes_successor)
        self.assertEqual(task.issue_number, 7)

    def test_missing_required_field_raises(self):
        body = task_body().replace("status: READY\n", "")
        with self.assertRaises(ProtocolError) as ctx:
            parse_task(body)
        self.assertIn("status", str(ctx.exception))

    def test_status_outside_domain_raises(self):
        with self.assertRaises(ProtocolError) as ctx:
            parse_task(task_body(status="MAYBE"))
        self.assertIn("outside the domain", str(ctx.exception))

    def test_abbreviated_sha_is_refused(self):
        """An abbreviated base could resolve to a different commit later."""
        with self.assertRaises(ProtocolError) as ctx:
            parse_task(task_body(base="ec3eb8f"))
        self.assertIn("40-character", str(ctx.exception))

    def test_read_only_task_is_marked_non_mutating(self):
        self.assertFalse(parse_task(task_body(kind="read_only")).mutating)
        self.assertTrue(parse_task(task_body(kind="infrastructure_only")).mutating)

    def test_wrong_schema_raises(self):
        with self.assertRaises(ProtocolError):
            parse_task(task_body().replace("mtj-task/1", "mtj-result/1"))

    def test_parses_the_live_issue_3_contract(self):
        """The real Manager-authored task must parse, backticks and all."""
        from pathlib import Path

        fixture = Path(__file__).parent / "fixtures" / "issue3.md"
        task = parse_task(fixture.read_text(), 3)
        self.assertEqual(task.task, "BRIDGE.V0.BUILD")
        self.assertEqual(task.base, "ec3eb8f75a1bf889e8998bec353212880228d808")
        self.assertTrue(task.is_ready)
        self.assertFalse(task.authorizes_successor)
        # Issue #3 ships no machine-readable globs; that must be visible, not assumed open.
        self.assertEqual(task.allow_paths, [])
        self.assertEqual(task.deny_paths, [])


class TestResultParser(unittest.TestCase):
    def test_round_trip(self):
        result = parse_result(result_body())
        self.assertEqual(result.status, "COMPLETE")
        self.assertEqual(result.pr, 1000)
        self.assertTrue(result.base_matches)
        self.assertFalse(result.needs_captain)

    def test_base_mismatch_is_visible(self):
        result = parse_result(result_body(base_expected="a" * 40, base_measured="b" * 40))
        self.assertFalse(result.base_matches)

    def test_none_decision_is_not_a_decision(self):
        self.assertEqual(parse_result(result_body(decision=("NONE",))).decision_required, [])
        self.assertTrue(parse_result(result_body(decision=("ratify X",))).needs_captain)

    def test_bad_status_raises(self):
        with self.assertRaises(ProtocolError):
            parse_result(result_body(status="FINISHED"))


class TestReviewParser(unittest.TestCase):
    def test_all_four_verdicts_parse(self):
        for verdict in ("PASS", "REPAIR", "CAPTAIN_DECISION_REQUIRED", "STOP"):
            self.assertEqual(parse_review(review_body(verdict=verdict)).verdict, verdict)

    def test_halts_automation_flag(self):
        self.assertTrue(parse_review(review_body(verdict="STOP")).halts_automation)
        self.assertTrue(parse_review(review_body(verdict="CAPTAIN_DECISION_REQUIRED")).halts_automation)
        self.assertFalse(parse_review(review_body(verdict="PASS")).halts_automation)

    def test_invented_verdict_is_refused(self):
        with self.assertRaises(ProtocolError) as ctx:
            parse_review(review_body(verdict="LOOKS_GOOD_TO_ME"))
        self.assertIn("outside the domain", str(ctx.exception))

    def test_prose_around_the_block_is_tolerated(self):
        body = "Sure! Here is my review:\n\n" + review_body() + "\n\nLet me know if you need more."
        self.assertEqual(parse_review(body).verdict, "PASS")

    def test_model_returning_no_block_raises(self):
        with self.assertRaises(ProtocolError):
            parse_review("I think it looks fine, PASS.")


class TestClaim(unittest.TestCase):
    def test_claim_expiry(self):
        fresh = parse_claim(render_block({
            "schema": "mtj-claim/1", "task": "T", "issue": 1,
            "worker_id": "host/1", "claimed_at": "2026-08-29T00:00:00Z", "lease_seconds": 3600}))
        import datetime as dt
        just_after = dt.datetime(2026, 8, 29, 0, 30, tzinfo=dt.timezone.utc)
        long_after = dt.datetime(2026, 8, 29, 4, 0, tzinfo=dt.timezone.utc)
        self.assertFalse(fresh.is_expired(just_after))
        self.assertTrue(fresh.is_expired(long_after))


if __name__ == "__main__":
    unittest.main()
