"""CR1 -- a Captain-authorized same-provider adversarial review of ONE result.

Captain, 2026-10-02 (Issue #1): the other model was out of weekly capacity, so a
trusted Captain decision may name one high-stakes result to be reviewed by a named
provider -- even the Worker's own -- in 2 or 3 isolated sessions with distinct
adversarial focuses; the host publishes the most severe verdict any session
reached. Everything that is not exactly such a decision authorizes nothing, and
the cross-provider rule of decision E (as amended, 5923072829) then stands.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from agent_bus import decision as D
from agent_bus import local_manager as L
from tests.refoundation.test_agent_bus_local_manager import GOOD, PassHarness, ROOT, WHO

RESULT = 1001          # the admitted result's comment id in the harness
REPAIR = json.dumps({"verdict": "REPAIR", "reason": "a check passes vacuously",
                     "findings": ["m04_check accepts an empty R4 table"], "evidence": ["probe"]})
CAPTAIN = json.dumps({"verdict": "CAPTAIN", "reason": "a real KILL",
                      "findings": ["K4 KILL on a fixture"], "evidence": ["kill.json"]})


def block(result=RESULT, reviewer="claude", sessions=2, **extra):
    raw = {"schema": "mtj-review-override/1", "result_comment": result,
           "reviewer": reviewer, "sessions": sessions, **extra}
    return "## Captain decision\n\n```mtj-review-override\n" + json.dumps(raw) + "\n```\n"


def comment(body, cid=2000, author=WHO):
    return SimpleNamespace(comment_id=cid, author=author, body=body)


class CR1Harness(PassHarness):
    def run_pass(self, issue_comments, answers, worker="claude", **kw):
        """One executed pass; `answers` is consumed one per model call."""
        rc = mock.patch.object(L, "read_comments", lambda *a, **k: list(issue_comments))
        rc.start()
        self.addCleanup(rc.stop)
        self.calls = []
        queue = list(answers)

        def invoke(reviewer, prompt, ws):
            self.calls.append((reviewer, prompt))
            return queue.pop(0) if queue else {"decision": GOOD}
        return self.manager(worker, invoke, **kw).poll_once(execute=True)


class TestOverrideReview(CR1Harness):
    def test_CR1_named_result_is_reviewed_by_claude_in_every_session(self):
        report = self.run_pass([comment(block(sessions=3))],
                               [{"decision": GOOD}] * 3)
        self.assertEqual([r for r, _ in self.calls], ["claude"] * 3)
        prompts = [p for _, p in self.calls]
        for i, p in enumerate(prompts):
            self.assertIn("CAPTAIN OVERRIDE (Issue #1 comment 2000)", p)
            self.assertIn(f"session {i + 1} of 3", p)
        self.assertEqual(len({p.split("FOCUS --")[1][:20] for p in prompts}), 3)
        self.assertEqual(report["action"], "PUBLISHED")
        self.assertEqual(report["override"], 2000)
        self.assertEqual(report["reviewer"], "claude x3 (CR1 override)")
        [decision] = self.decisions
        self.assertEqual(decision["verdict"], "ACCEPT")
        self.assertTrue(decision["reason"].startswith(
            "CR1 override 2000: 3 isolated sessions (s1 ACCEPT, s2 ACCEPT, s3 ACCEPT); "))

    def test_CR1_one_dissenting_session_decides(self):
        self.run_pass([comment(block())], [{"decision": GOOD}, {"decision": REPAIR}])
        [decision] = self.decisions
        self.assertEqual(decision["verdict"], "REPAIR")
        self.assertIn("s1 ACCEPT, s2 REPAIR", decision["reason"])
        self.assertIn("s2: m04_check accepts an empty R4 table", decision["findings"])

    def test_CR1_captain_is_more_severe_than_repair(self):
        self.run_pass([comment(block())], [{"decision": REPAIR}, {"decision": CAPTAIN}])
        self.assertEqual(self.decisions[0]["verdict"], "CAPTAIN")

    def test_NC_CR1_a_session_out_of_capacity_is_a_wait_and_nothing_is_published(self):
        report = self.run_pass([comment(block())], [{"decision": GOOD}, {"capacity": True}])
        self.assertEqual(report["action"], "WAIT")
        self.assertEqual(self.published, [])

    def test_CR1_combined_decision_stays_inside_the_schema(self):
        many = json.dumps({"verdict": "REPAIR", "reason": "r" * D.MAX_REASON,
                           "findings": ["f" * D.MAX_ITEM] * D.MAX_ITEMS,
                           "evidence": ["e" * D.MAX_ITEM] * D.MAX_ITEMS})
        out = L.combine_decisions([D.parse(many), D.parse(many)], 2000)
        self.assertEqual(out.verdict, "REPAIR")
        self.assertLessEqual(len(out.reason), D.MAX_REASON)
        self.assertLessEqual(len(out.findings), D.MAX_ITEMS)
        self.assertTrue(all(len(f) <= D.MAX_ITEM for f in out.findings + out.evidence))


class TestOverrideFailsClosed(CR1Harness):
    """Each rigged decision must leave the cross-provider rule in force: Codex only."""

    def assert_cross_provider(self, issue_comments, worker="claude", **kw):
        report = self.run_pass(issue_comments, [{"decision": GOOD}], worker=worker, **kw)
        self.assertEqual([r for r, _ in self.calls], ["codex"])
        self.assertIsNone(report["override"])
        for _, prompt in self.calls:
            self.assertNotIn("CAPTAIN OVERRIDE", prompt)

    def test_NC_CR1_no_override(self):
        self.assert_cross_provider([])

    def test_NC_CR1_untrusted_author(self):
        self.assert_cross_provider([comment(block(), author="someone-else")])

    def test_NC_CR1_posted_before_or_at_the_result(self):
        self.assert_cross_provider([comment(block(), cid=RESULT - 1)])
        self.assert_cross_provider([comment(block(), cid=RESULT)])

    def test_NC_CR1_names_another_result(self):
        self.assert_cross_provider([comment(block(result=RESULT + 1))])

    def test_NC_CR1_malformed_blocks(self):
        rigs = [
            "```mtj-review-override\n{not json\n```",
            "```mtj-review-override\n[1, 2]\n```",
            block(extra="x"),
            block(sessions=1), block(sessions=4), block(sessions="2"), block(sessions=True),
            block(reviewer="gpt"),
            block(result=str(RESULT)),
            block().replace("mtj-review-override/1", "mtj-review-override/2"),
        ]
        for rig in rigs:
            with self.subTest(rig=rig[:60]):
                self.assert_cross_provider([comment(rig)])

    def test_NC_CR1_reviewer_not_in_the_configured_order(self):
        self.assert_cross_provider([comment(block())], order=("codex", "gemini"))

    def test_NC_CR1_two_valid_overrides_authorize_nothing(self):
        self.assert_cross_provider([comment(block(), cid=2000), comment(block(), cid=2001)])

    def test_NC_CR1_an_invalid_override_beside_a_valid_one_authorizes_nothing(self):
        self.assert_cross_provider([comment(block(), cid=2000),
                                    comment(block(sessions=9), cid=2001)])

    def test_NC_CR1_unreadable_issue_authorizes_nothing(self):
        def boom(*a, **k):
            raise L.AuthorityError("rate limited")
        rc = mock.patch.object(L, "read_comments", boom)
        rc.start()
        self.addCleanup(rc.stop)
        self.calls = []
        m = self.manager("claude", lambda r, p, ws: self.calls.append(r) or {"decision": GOOD})
        report = m.poll_once(execute=True)
        self.assertEqual(self.calls, ["codex"])
        self.assertIsNone(report["override"])


class TestOverrideScope(CR1Harness):
    def test_NC_CR1_an_ordinary_wave_is_unchanged_by_an_override(self):
        self.high_stakes = False
        report = self.run_pass([comment(block())], [{"decision": GOOD}])
        self.assertEqual([r for r, _ in self.calls], ["claude"])
        self.assertNotIn("CAPTAIN OVERRIDE", self.calls[0][1])
        self.assertIsNone(report["override"])

    def test_NC_CR1_unattributed_work_stays_a_host_captain(self):
        rc = mock.patch.object(L, "read_comments", lambda *a, **k: [comment(block())])
        rc.start()
        self.addCleanup(rc.stop)
        report = self.manager(None, lambda *a: self.fail("no model may run"),
                              problem="unattributed").poll_once(execute=True)
        self.assertEqual(self.decisions[-1]["verdict"], "CAPTAIN")
        self.assertIsNone(report["override"])

    def test_CR1_agent_bus_md_states_the_override(self):
        text = " ".join((ROOT / "refoundation" / "AGENT-BUS.md")
                        .read_text(encoding="utf-8").split())
        self.assertIn("`mtj-review-override`", text)
        self.assertIn("the host publishes the most severe verdict any session reached", text)
        self.assertIn("A malformed, untrusted, earlier or duplicate block authorizes nothing",
                      text)


if __name__ == "__main__":
    unittest.main()
