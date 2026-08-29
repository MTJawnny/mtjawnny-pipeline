"""Unit tests: the autonomy policy — the boundary a model must not be able to cross."""

import unittest

from mtjbridge.policy import (Action, PolicyError, check_paths_against_task, classify_paths,
                              decide)
from mtjbridge.protocol import parse_result, parse_review, parse_task
from tests.helpers import result_body, review_body, task_body

BASE = "a" * 40


def _trio(*, task_kw=None, result_kw=None, review_kw=None):
    task = parse_task(task_body(base=BASE, **(task_kw or {})))
    result = parse_result(result_body(base_expected=BASE, **(result_kw or {})))
    review = parse_review(review_body(**(review_kw or {})))
    return task, result, review


class TestVerdictRouting(unittest.TestCase):
    def test_pass_posts_review_and_stops_when_no_successor_authorized(self):
        task, result, review = _trio()
        decision = decide(task=task, result=result, review=review, changed_paths=["src/thing.py"])
        self.assertEqual(decision.verdict, "PASS")
        self.assertEqual(decision.action, Action.POST_REVIEW)
        self.assertFalse(decision.automation_may_continue)
        self.assertTrue(any("next.authorized=NONE" in r for r in decision.reasons))

    def test_repair_creates_one_bounded_repair_task(self):
        task, result, review = _trio(result_kw={"discrepancies": ("tests fail",)},
                                     review_kw={"verdict": "REPAIR"})
        decision = decide(task=task, result=result, review=review, changed_paths=["src/thing.py"])
        self.assertEqual(decision.action, Action.CREATE_REPAIR_TASK)
        self.assertTrue(decision.automation_may_continue)

    def test_captain_verdict_posts_packet_and_halts(self):
        task, result, review = _trio(review_kw={"verdict": "CAPTAIN_DECISION_REQUIRED",
                                                "captain": ("ratify new token?",)})
        decision = decide(task=task, result=result, review=review, changed_paths=["src/thing.py"])
        self.assertEqual(decision.action, Action.POST_DECISION_PACKET)
        self.assertTrue(decision.halts)

    def test_stop_verdict_halts(self):
        task, result, review = _trio(review_kw={"verdict": "STOP"})
        decision = decide(task=task, result=result, review=review, changed_paths=["src/thing.py"])
        self.assertEqual(decision.action, Action.HALT)
        self.assertTrue(decision.halts)


class TestModelCannotUnlock(unittest.TestCase):
    """The central invariant: a model verdict may only ever RESTRICT."""

    def test_model_pass_cannot_unlock_captain_reserved_paths(self):
        """In-scope for the task, but Captain-reserved: PASS must not unlock it."""
        task, result, review = _trio(task_kw={"allow": ("experiments/**",)},
                                     review_kw={"verdict": "PASS"})
        decision = decide(task=task, result=result, review=review,
                          changed_paths=["experiments/moves/thing.json"])
        self.assertEqual(decision.verdict, "CAPTAIN_DECISION_REQUIRED")
        self.assertTrue(decision.halts)
        self.assertTrue(any("codebook" in c for c in decision.captain_categories))


    def test_scope_violation_outranks_the_captain_packet(self):
        """Deliberate precedence: an out-of-scope change is worker DRIFT (STOP),
        not a decision to hand Captain. Both halt; only the label differs."""
        task, result, review = _trio(review_kw={"verdict": "PASS"})
        decision = decide(task=task, result=result, review=review,
                          changed_paths=["experiments/moves/thing.json"])
        self.assertEqual(decision.verdict, "STOP")
        self.assertTrue(any("outside every allow pattern" in r for r in decision.reasons))

    def test_model_pass_cannot_advance_past_a_failed_worker_result(self):
        task, result, review = _trio(result_kw={"status": "FAIL"}, review_kw={"verdict": "PASS"})
        decision = decide(task=task, result=result, review=review, changed_paths=["src/thing.py"])
        self.assertEqual(decision.verdict, "STOP")
        self.assertTrue(decision.halts)

    def test_model_pass_cannot_override_a_worker_declared_captain_decision(self):
        task, result, review = _trio(result_kw={"decision": ("needs ratification",)},
                                     review_kw={"verdict": "PASS"})
        decision = decide(task=task, result=result, review=review, changed_paths=["src/thing.py"])
        self.assertEqual(decision.verdict, "CAPTAIN_DECISION_REQUIRED")

    def test_negative_control_clean_case_really_does_pass(self):
        """Without this, every assertion above could be passing for the wrong reason."""
        task, result, review = _trio(review_kw={"verdict": "PASS"})
        decision = decide(task=task, result=result, review=review, changed_paths=["src/thing.py"])
        self.assertEqual(decision.verdict, "PASS")
        self.assertEqual(decision.captain_categories, ())

    def test_captain_text_signal_in_result_forces_halt(self):
        task, result, review = _trio(
            result_kw={"mutations": ("src/thing.py",),
                       "discrepancies": ("weakened the conservation gate to pass",)},
            review_kw={"verdict": "PASS"})
        decision = decide(task=task, result=result, review=review, changed_paths=["src/thing.py"])
        self.assertEqual(decision.verdict, "CAPTAIN_DECISION_REQUIRED")
        self.assertTrue(any("conservation" in c for c in decision.captain_categories))


class TestBaseAndScope(unittest.TestCase):
    def test_base_mismatch_halts_before_anything_else(self):
        task, _, review = _trio()
        result = parse_result(result_body(base_expected=BASE, base_measured="b" * 40))
        decision = decide(task=task, result=result, review=review, changed_paths=["src/thing.py"])
        self.assertEqual(decision.verdict, "STOP")
        self.assertTrue(any("base mismatch" in r for r in decision.reasons))

    def test_deny_path_violation_halts(self):
        task, result, review = _trio()
        decision = decide(task=task, result=result, review=review,
                          changed_paths=["docs/README.md"])
        self.assertEqual(decision.verdict, "STOP")
        self.assertTrue(any("deny pattern" in r for r in decision.reasons))

    def test_path_outside_allow_list_halts(self):
        task, result, review = _trio()
        decision = decide(task=task, result=result, review=review,
                          changed_paths=["tools/other.py"])
        self.assertEqual(decision.verdict, "STOP")
        self.assertTrue(any("outside every allow pattern" in r for r in decision.reasons))

    def test_absent_globs_are_reported_not_assumed_open(self):
        task = parse_task(task_body(base=BASE, allow=(), deny=()))
        self.assertEqual(task.allow_paths, [])
        _, result, review = _trio()
        decision = decide(task=task, result=result, review=review, changed_paths=["anything/x.py"])
        self.assertEqual(decision.verdict, "PASS")
        self.assertTrue(any("NOT machine-checked" in r for r in decision.reasons))

    def test_mismatched_task_ids_raise(self):
        task, result, _ = _trio()
        review = parse_review(review_body(task_id="OTHER.TASK"))
        with self.assertRaises(PolicyError):
            decide(task=task, result=result, review=review)


class TestLimits(unittest.TestCase):
    def test_repair_limit_halts_rather_than_looping(self):
        task, result, review = _trio(result_kw={"discrepancies": ("still broken",)},
                                     review_kw={"verdict": "REPAIR"})
        decision = decide(task=task, result=result, review=review,
                          changed_paths=["src/thing.py"], repair_count=2, max_repairs=2)
        self.assertEqual(decision.verdict, "STOP")
        self.assertTrue(any("repair limit" in r for r in decision.reasons))

    def test_cycle_limit_halts(self):
        task, result, review = _trio()
        decision = decide(task=task, result=result, review=review,
                          changed_paths=["src/thing.py"], cycle_count=8, max_cycles=8)
        self.assertEqual(decision.verdict, "STOP")
        self.assertTrue(any("cycle limit" in r for r in decision.reasons))


class TestPathClassification(unittest.TestCase):
    def test_captain_paths_are_recognised(self):
        hits = dict(classify_paths([
            "experiments/moves/m.json", "docs/CODEBOOK-NAMING-GRAMMAR.md",
            "refoundation/CAPTAIN-DIRECTION.md", ".github/workflows/build.yml",
            "docs/RATIFIED-RULINGS-REGISTRY.md", "src/ordinary.py",
        ]))
        self.assertNotIn("src/ordinary.py", hits)
        self.assertEqual(len(hits), 5)

    def test_nested_codebook_json_matches_the_recursive_glob(self):
        self.assertTrue(classify_paths(["experiments/foundry/codebook.json"]))
        self.assertTrue(classify_paths(["codebook.json"]))


if __name__ == "__main__":
    unittest.main()
