"""State law: correlation, idempotency, staleness, and the authority boundary.

The single most important assertion in this file is the one that says the bus
cannot move the accepted head. Everything else protects the loop; that one
protects the project, because a transport that can promote itself to authority
is exactly the failure the checkpoint discipline exists to prevent.
"""

from __future__ import annotations

import unittest

from tests.refoundation.agent_bus_fixtures import (
    AUTHORITY, BASE, CHECKPOINT, NOBODY_TRUSTED, OTHER_SHA, TASK, TRUSTED, WAVE,
    human, raw, unit,
)

from agent_bus import errors as E
from agent_bus.errors import BusError
from agent_bus.machine import ACCEPTED, INERT, REJECTED, Envelope, fold
from agent_bus.protocol import parse
from agent_bus.wave import execution_order, plan_from_command, remaining_after
from tests.refoundation.agent_bus_fixtures import envelope as env_dict
import json


def codes(state) -> list[str]:
    return [r.code for r in state.records if r.status == REJECTED]


COMMAND = dict(kind="WAVE_COMMAND", actor="MANAGER", message_id="m-command-0001")
RESULT = dict(kind="WAVE_RESULT", actor="WORKER", message_id="w-result-0001",
              parent="m-command-0001")
REVIEW = dict(kind="WAVE_REVIEW", actor="MANAGER", message_id="m-review-0001",
              parent="w-result-0001")


class TestHappyPath(unittest.TestCase):
    def test_a_valid_command_is_accepted_once_and_wakes_the_worker(self):
        state = fold([raw(10, **COMMAND)], AUTHORITY, TRUSTED)
        self.assertEqual([r.status for r in state.records], [ACCEPTED])
        self.assertEqual([e.message_id for e in state.pending_for("WORKER")],
                         ["m-command-0001"])
        self.assertEqual(state.pending_for("MANAGER"), [])

    def test_a_result_correlates_to_its_command_and_wakes_the_manager(self):
        state = fold([raw(10, **COMMAND), raw(11, **RESULT)], AUTHORITY, TRUSTED)
        self.assertEqual(codes(state), [])
        self.assertEqual([e.message_id for e in state.pending_for("MANAGER")],
                         ["w-result-0001"])
        # The command is answered, so it no longer wakes the Worker.
        self.assertEqual(state.pending_for("WORKER"), [])

    def test_a_review_closes_the_manager_side(self):
        state = fold([raw(10, **COMMAND), raw(11, **RESULT), raw(12, **REVIEW)], AUTHORITY, TRUSTED)
        self.assertEqual(codes(state), [])
        self.assertEqual(state.pending_for("MANAGER"), [])
        self.assertEqual(state.waves[WAVE].review.body["verdict"], "ACCEPT")

    def test_progress_records_units_without_waking_anyone(self):
        progress = dict(kind="WAVE_PROGRESS", actor="WORKER",
                        message_id="w-progress-0001", parent="m-command-0001")
        state = fold([raw(10, **COMMAND), raw(11, **progress)], AUTHORITY, TRUSTED)
        self.assertEqual(codes(state), [])
        self.assertEqual(state.waves[WAVE].completed_units(), ["U1"])
        self.assertEqual(state.pending_for("MANAGER"), [])


class TestIdempotency(unittest.TestCase):
    def test_a_redelivered_command_is_a_deterministic_no_op(self):
        state = fold([raw(10, **COMMAND), raw(11, **COMMAND)], AUTHORITY, TRUSTED)
        self.assertEqual(codes(state), [E.DUPLICATE_MESSAGE_ID])
        self.assertEqual(len(state.pending_for("WORKER")), 1)

    def test_a_redelivered_result_is_a_deterministic_no_op(self):
        state = fold([raw(10, **COMMAND), raw(11, **RESULT), raw(12, **RESULT)], AUTHORITY, TRUSTED)
        self.assertEqual(codes(state), [E.DUPLICATE_MESSAGE_ID])
        self.assertEqual(len(state.pending_for("MANAGER")), 1)

    def test_a_second_command_for_the_same_wave_cannot_re_authorize_it(self):
        second = dict(COMMAND, message_id="m-command-0002")
        state = fold([raw(10, **COMMAND), raw(11, **second)], AUTHORITY, TRUSTED)
        self.assertEqual(codes(state), [E.WAVE_ALREADY_COMMANDED])

    def test_a_claimed_command_is_still_pending_but_marked_claimed(self):
        # The machine reports the fact; refusing to run it twice is the
        # supervisor's decision, made once, with the evidence in hand.
        progress = dict(kind="WAVE_PROGRESS", actor="WORKER",
                        message_id="w-progress-0001", parent="m-command-0001")
        state = fold([raw(10, **COMMAND), raw(11, **progress)], AUTHORITY, TRUSTED)
        self.assertEqual([e.message_id for e in state.pending_for("WORKER")],
                         ["m-command-0001"])
        self.assertTrue(state.waves[WAVE].claimed)

    def test_an_aborted_wave_stops_waking_the_worker_with_its_command(self):
        abort = dict(kind="WAVE_ABORT", actor="MANAGER", message_id="m-abort-0001")
        state = fold([raw(10, **COMMAND), raw(11, **abort)], AUTHORITY, TRUSTED)
        self.assertEqual([e.message_id for e in state.pending_for("WORKER")],
                         ["m-abort-0001"])


class TestStaleness(unittest.TestCase):
    def test_a_command_pinned_to_an_older_checkpoint_is_stale(self):
        state = fold([raw(10, checkpoint=CHECKPOINT - 1, **COMMAND)], AUTHORITY, TRUSTED)
        self.assertEqual(codes(state), [E.STALE_AUTHORITY])
        self.assertEqual(state.pending_for("WORKER"), [])

    def test_a_command_citing_an_unselected_task_cannot_execute(self):
        state = fold([raw(10, task=TASK - 1, **COMMAND)], AUTHORITY, TRUSTED)
        self.assertEqual(codes(state), [E.WAVE_NOT_SELECTED])

    def test_a_command_pinned_to_a_stale_base_cannot_execute(self):
        state = fold([raw(10, base=OTHER_SHA, **COMMAND)], AUTHORITY, TRUSTED)
        self.assertEqual(codes(state), [E.STALE_BASE])

    def test_a_command_on_another_issue_is_not_this_bus(self):
        state = fold([raw(10, issue=2, **COMMAND)], AUTHORITY, TRUSTED)
        self.assertEqual(codes(state), [E.STALE_AUTHORITY])


class TestCorrelation(unittest.TestCase):
    def test_a_result_answering_an_unknown_command_is_rejected(self):
        orphan = dict(RESULT, parent="m-command-9999")
        state = fold([raw(10, **COMMAND), raw(11, **orphan)], AUTHORITY, TRUSTED)
        self.assertEqual(codes(state), [E.UNKNOWN_PARENT])

    def test_a_result_for_an_uncommanded_wave_is_rejected(self):
        state = fold([raw(10, **COMMAND),
                      raw(11, wave="INFRA.OTHER.W9", **RESULT)], AUTHORITY, TRUSTED)
        self.assertEqual(codes(state), [E.PARENT_WAVE_MISMATCH])

    def test_a_review_cannot_answer_a_command_directly(self):
        bad = dict(REVIEW, parent="m-command-0001")
        state = fold([raw(10, **COMMAND), raw(11, **bad)], AUTHORITY, TRUSTED)
        self.assertEqual(codes(state), [E.PARENT_KIND_MISMATCH])

    def test_a_result_reporting_unauthorized_units_is_rejected(self):
        body = {"status": "P", "branch": "b", "head": OTHER_SHA,
                "units": [{"id": "U9", "status": "DONE"}], "next": "NONE"}
        state = fold([raw(10, **COMMAND), raw(11, body=body, **RESULT)], AUTHORITY, TRUSTED)
        self.assertEqual(codes(state), [E.UNKNOWN_DEPENDENCY])

    def test_progress_on_an_unauthorized_unit_is_rejected(self):
        progress = dict(kind="WAVE_PROGRESS", actor="WORKER",
                        message_id="w-progress-0001", parent="m-command-0001")
        state = fold([raw(10, **COMMAND),
                      raw(11, body={"unit": "U9", "status": "DONE"}, **progress)],
                     AUTHORITY, TRUSTED)
        self.assertEqual(codes(state), [E.UNKNOWN_DEPENDENCY])


class TestInertTraffic(unittest.TestCase):
    def test_human_comments_are_inert_and_wake_nobody(self):
        state = fold([human(10), human(11, "@claude ship it"), human(12, "+1")], AUTHORITY, TRUSTED)
        self.assertEqual([r.status for r in state.records], [INERT] * 3)
        self.assertEqual(state.pending_for("WORKER"), [])
        self.assertEqual(state.pending_for("MANAGER"), [])

    def test_a_malformed_bus_block_cannot_authorize_anything(self):
        from agent_bus.machine import RawComment
        bad = RawComment("issue:1", 10, "MTJawnny", "```mtj-bus\n{oops\n```")
        state = fold([bad], AUTHORITY, TRUSTED)
        self.assertEqual(codes(state), [E.MALFORMED_JSON])
        self.assertEqual(state.pending_for("WORKER"), [])

    def test_an_untrusted_author_cannot_speak_on_the_bus(self):
        state = fold([raw(10, author="drive-by-contributor", **COMMAND)],
                     AUTHORITY, TRUSTED)
        self.assertEqual(codes(state), [E.UNTRUSTED_AUTHOR])

    def test_the_trusted_author_check_is_case_insensitive(self):
        state = fold([raw(10, author="mtjawnny", **COMMAND)], AUTHORITY, TRUSTED)
        self.assertEqual(codes(state), [])


class TestAuthorityBoundary(unittest.TestCase):
    def test_the_accepted_head_always_comes_from_the_checkpoint(self):
        state = fold([raw(10, **COMMAND), raw(11, **RESULT), raw(12, **REVIEW)], AUTHORITY, TRUSTED)
        self.assertEqual(state.accepted_head, BASE)
        self.assertNotEqual(state.accepted_head, OTHER_SHA)

    def test_an_accept_verdict_is_a_proposal_until_a_checkpoint_ratifies_it(self):
        state = fold([raw(10, **COMMAND), raw(11, **RESULT), raw(12, **REVIEW)], AUTHORITY, TRUSTED)
        pending = state.pending_acceptance()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["proposed_accepted_head"], OTHER_SHA)
        self.assertEqual(pending[0]["checkpoint_accepted_head"], BASE)
        self.assertFalse(pending[0]["ratified"])

    def test_newer_prose_on_the_transport_does_not_become_authority(self):
        chatty = human(13, "Latest state: accepted head is now " + OTHER_SHA)
        state = fold([raw(10, **COMMAND), raw(11, **RESULT), raw(12, **REVIEW), chatty],
                     AUTHORITY, TRUSTED)
        self.assertEqual(state.accepted_head, BASE)

    def test_CONTROL_the_guard_that_stops_a_worker_claiming_an_accepted_head(self):
        # Unreachable through `parse` today -- a WORKER body has no accepted_head
        # key -- so it is exercised directly. A guard nobody has watched go red is
        # not known to be a guard.
        from agent_bus.machine import BusState, RawComment, _correlate
        forged = Envelope(
            schema="mtj-agent-bus/1", message_id="w-result-0001", actor="WORKER",
            kind="WAVE_RESULT", wave=WAVE, parent=None,
            authority={"issue": 1, "checkpoint": CHECKPOINT, "task": TASK},
            base=BASE, created_at="2026-09-23T20:00:00Z",
            body={"accepted_head": OTHER_SHA})
        problem = _correlate(forged, BusState(authority=AUTHORITY, trust=TRUSTED),
                             AUTHORITY, {},
                             RawComment("issue:1", 10, "MTJawnny", ""), TRUSTED)
        self.assertIsInstance(problem, BusError)
        self.assertEqual(problem.code, E.UNAUTHORIZED_ACCEPTED_HEAD)

    def test_a_worker_result_carrying_an_accepted_head_never_parses(self):
        body = {"status": "P", "branch": "b", "head": OTHER_SHA, "units": [],
                "accepted_head": OTHER_SHA}
        state = fold([raw(10, **COMMAND), raw(11, body=body, **RESULT)], AUTHORITY, TRUSTED)
        self.assertEqual(codes(state), [E.UNKNOWN_FIELD])


class TestWavePlan(unittest.TestCase):
    def body(self, units):
        return {"branch": "b", "review_boundary": "end of wave", "units": units}

    def test_order_is_topological_and_stable_on_declared_position(self):
        plan = plan_from_command(WAVE, self.body(
            [unit("C", ["A"]), unit("A"), unit("B", ["A"])]))
        self.assertEqual(plan.order, ("A", "C", "B"))
        again = plan_from_command(WAVE, self.body(
            [unit("C", ["A"]), unit("A"), unit("B", ["A"])]))
        self.assertEqual(plan.order, again.order)

    def test_a_dependency_cycle_is_rejected(self):
        with self.assertRaises(BusError) as caught:
            plan_from_command(WAVE, self.body([unit("A", ["B"]), unit("B", ["A"])]))
        self.assertEqual(caught.exception.code, E.DEPENDENCY_CYCLE)

    def test_a_self_dependency_is_rejected(self):
        with self.assertRaises(BusError) as caught:
            plan_from_command(WAVE, self.body([unit("A", ["A"])]))
        self.assertEqual(caught.exception.code, E.DEPENDENCY_CYCLE)

    def test_an_unknown_dependency_is_rejected(self):
        with self.assertRaises(BusError) as caught:
            plan_from_command(WAVE, self.body([unit("A", ["Z"])]))
        self.assertEqual(caught.exception.code, E.UNKNOWN_DEPENDENCY)

    def test_a_duplicate_unit_id_is_rejected(self):
        with self.assertRaises(BusError) as caught:
            plan_from_command(WAVE, self.body([unit("A"), unit("A")]))
        self.assertEqual(caught.exception.code, E.DUPLICATE_UNIT_ID)

    def test_an_empty_wave_authorizes_nothing(self):
        with self.assertRaises(BusError) as caught:
            plan_from_command(WAVE, self.body([]))
        self.assertEqual(caught.exception.code, E.EMPTY_WAVE)

    def test_a_command_whose_plan_is_invalid_is_never_accepted(self):
        body = self.body([unit("A", ["B"]), unit("B", ["A"])])
        state = fold([raw(10, body=body, **COMMAND)], AUTHORITY, TRUSTED)
        self.assertEqual(codes(state), [E.DEPENDENCY_CYCLE])
        self.assertEqual(state.pending_for("WORKER"), [])


class TestResume(unittest.TestCase):
    def plan(self):
        return plan_from_command(WAVE, {
            "branch": "b", "review_boundary": "end",
            "units": [unit("A"), unit("B", ["A"]), unit("C", ["B"]), unit("D")]})

    def test_nothing_done_means_the_whole_order_remains(self):
        out = remaining_after(self.plan(), [])
        self.assertEqual(out["runnable"], ["A", "D", "B", "C"])
        self.assertEqual(out["next"], "A")
        self.assertFalse(out["wave_complete"])

    def test_completed_units_drop_out_and_order_survives(self):
        out = remaining_after(self.plan(), ["A", "D"])
        self.assertEqual(out["runnable"], ["B", "C"])

    def test_a_failed_unit_blocks_only_its_dependents(self):
        out = remaining_after(self.plan(), ["A"], ["B"])
        self.assertEqual(out["runnable"], ["D"])
        self.assertEqual(out["blocked"], {"C": ["B"]})

    def test_a_wave_with_everything_done_is_complete(self):
        out = remaining_after(self.plan(), ["A", "B", "C", "D"])
        self.assertTrue(out["wave_complete"])
        self.assertIsNone(out["next"])

    def test_a_unit_that_is_not_part_of_the_wave_is_a_halt_not_a_shrug(self):
        with self.assertRaises(BusError) as caught:
            remaining_after(self.plan(), ["Z"])
        self.assertEqual(caught.exception.code, E.UNKNOWN_DEPENDENCY)

    def test_resume_merges_durable_git_evidence_with_posted_progress(self):
        progress = dict(kind="WAVE_PROGRESS", actor="WORKER",
                        message_id="w-progress-0001", parent="m-command-0001")
        state = fold([raw(10, **COMMAND), raw(11, **progress)], AUTHORITY, TRUSTED)
        # U1 is known from the posted message; U2 only from a commit trailer.
        out = state.resume(WAVE, ["U2"])
        self.assertEqual(out["completed"], ["U1", "U2"])
        self.assertTrue(out["wave_complete"])

    def test_resume_of_an_unauthorized_wave_halts(self):
        state = fold([raw(10, **COMMAND)], AUTHORITY, TRUSTED)
        with self.assertRaises(BusError) as caught:
            state.resume("INFRA.NOT.A.WAVE")
        self.assertEqual(caught.exception.code, E.WAVE_NOT_SELECTED)


class TestDeterminism(unittest.TestCase):
    def test_the_same_stream_folds_to_the_same_state_dict(self):
        stream = [raw(10, **COMMAND), human(11), raw(12, **RESULT)]
        self.assertEqual(fold(stream, AUTHORITY, TRUSTED).as_dict(),
                         fold(stream, AUTHORITY, TRUSTED).as_dict())

    def test_ordering_is_by_comment_id_not_by_self_reported_time(self):
        late = raw(11, created_at="1999-01-01T00:00:00Z", **RESULT)
        state = fold([raw(10, **COMMAND), late], AUTHORITY, TRUSTED)
        self.assertEqual(codes(state), [])


if __name__ == "__main__":
    unittest.main()
