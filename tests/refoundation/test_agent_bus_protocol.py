"""Envelope law: extraction, strict validation, actor/kind, and who may be woken.

Every rejection here is asserted BY CODE, not by "it raised something". A test
that only asserts an exception cannot tell a schema rejection from a typo in the
test, and this package's whole claim is that its failures are deterministic.
"""

from __future__ import annotations

import json
import unittest

from tests.refoundation.agent_bus_fixtures import (
    BASE, OTHER_SHA, WAVE, comment_body, envelope, payload, unit,
)

from agent_bus import SCHEMA
from agent_bus import errors as E
from agent_bus.errors import BusError
from agent_bus.protocol import (
    ACTOR_KIND, ACTORS, KINDS, WAKES, extract, parse, parse_comment,
)


def code_of(callable_, *args, **kwargs) -> str:
    try:
        callable_(*args, **kwargs)
    except BusError as exc:
        return exc.code
    raise AssertionError("expected a BusError, got a success")


class TestExtraction(unittest.TestCase):
    def test_an_ordinary_human_comment_carries_no_message(self):
        self.assertIsNone(extract("Nice work. Ship it."))

    def test_an_at_claude_mention_is_not_a_message(self):
        self.assertIsNone(parse_comment("@claude please run the gate and push"))

    def test_a_yaml_task_comment_from_the_old_protocol_is_not_a_bus_message(self):
        old = "```yaml\nschema: mtj-task/0\nid: C00\n```"
        self.assertIsNone(parse_comment(old))

    def test_a_plain_json_block_is_not_a_bus_message(self):
        self.assertIsNone(parse_comment("```json\n" + payload() + "\n```"))

    def test_the_bus_block_is_found_inside_ordinary_prose(self):
        self.assertIsNotNone(parse_comment(comment_body()))

    def test_two_bus_blocks_in_one_comment_are_ambiguous_not_first_wins(self):
        doubled = comment_body() + comment_body(message_id="m-command-0002")
        self.assertEqual(code_of(parse_comment, doubled), E.AMBIGUOUS_ENVELOPE)

    def test_tildes_and_indented_fences_do_not_open_a_bus_block(self):
        for body in ("~~~mtj-bus\n{}\n~~~", "  ```mtj-bus\n{}\n  ```"):
            with self.subTest(body=body):
                self.assertIsNone(extract(body))


class TestEnvelopeShape(unittest.TestCase):
    def test_the_reference_message_validates(self):
        env = parse(payload())
        self.assertEqual(env.schema, SCHEMA)
        self.assertEqual(env.wave, WAVE)
        self.assertEqual(env.base, BASE)

    def test_render_round_trips_through_extraction(self):
        env = parse(payload())
        self.assertEqual(parse_comment(env.render()), env)

    def test_malformed_json_is_a_parse_rejection(self):
        self.assertEqual(code_of(parse, "{not json"), E.MALFORMED_JSON)

    def test_a_json_array_is_not_an_envelope(self):
        self.assertEqual(code_of(parse, "[]"), E.NOT_AN_OBJECT)

    def test_a_duplicated_json_key_is_rejected_rather_than_last_wins(self):
        doubled = '{"schema": "x", "schema": "' + SCHEMA + '"}'
        self.assertEqual(code_of(parse, doubled), E.DUPLICATE_JSON_KEY)

    def test_every_envelope_field_is_required(self):
        for field in ("message_id", "actor", "kind", "wave", "parent",
                      "authority", "base", "created_at", "body"):
            raw = envelope()
            del raw[field]
            with self.subTest(field=field):
                self.assertEqual(code_of(parse, json.dumps(raw)), E.MISSING_FIELD)

    def test_an_unknown_envelope_field_is_rejected_not_ignored(self):
        raw = envelope()
        raw["priority"] = "URGENT"
        self.assertEqual(code_of(parse, json.dumps(raw)), E.UNKNOWN_FIELD)

    def test_an_unsupported_schema_version_is_its_own_rejection(self):
        self.assertEqual(code_of(parse, payload(schema="mtj-agent-bus/2")),
                         E.SCHEMA_UNSUPPORTED)

    def test_a_missing_schema_is_reported_before_any_other_field_law(self):
        raw = envelope()
        del raw["schema"]
        del raw["actor"]
        self.assertEqual(code_of(parse, json.dumps(raw)), E.MISSING_FIELD)

    def test_a_base_that_is_not_a_sha_is_rejected(self):
        self.assertEqual(code_of(parse, payload(base="HEAD")), E.BAD_VALUE)

    def test_a_non_utc_timestamp_is_rejected(self):
        self.assertEqual(code_of(parse, payload(created_at="2026-09-23 20:00:00")),
                         E.BAD_VALUE)

    def test_authority_ids_must_be_positive_integers(self):
        self.assertEqual(code_of(parse, payload(checkpoint=0)), E.BAD_VALUE)
        raw = envelope()
        raw["authority"]["task"] = "5805989871"
        self.assertEqual(code_of(parse, json.dumps(raw)), E.BAD_VALUE)


class TestActorKindLaw(unittest.TestCase):
    def test_every_kind_declares_its_speakers(self):
        self.assertEqual(sorted(ACTOR_KIND), sorted(KINDS))
        for kind, actors in ACTOR_KIND.items():
            with self.subTest(kind=kind):
                self.assertTrue(actors <= set(ACTORS))
                self.assertTrue(actors)

    def test_a_worker_cannot_issue_a_command(self):
        self.assertEqual(
            code_of(parse, payload(kind="WAVE_COMMAND", actor="WORKER")),
            E.ACTOR_KIND_MISMATCH)

    def test_a_manager_cannot_post_a_worker_result(self):
        self.assertEqual(
            code_of(parse, payload(kind="WAVE_RESULT", actor="MANAGER",
                                   parent="m-command-0001")),
            E.ACTOR_KIND_MISMATCH)

    def test_a_worker_cannot_post_its_own_review(self):
        self.assertEqual(
            code_of(parse, payload(kind="WAVE_REVIEW", actor="WORKER",
                                   parent="m-result-0001")),
            E.ACTOR_KIND_MISMATCH)

    def test_an_unknown_actor_or_kind_is_rejected(self):
        self.assertEqual(code_of(parse, payload(actor="ROBOT")), E.ACTOR_UNKNOWN)
        self.assertEqual(
            code_of(parse, payload(kind="PLEASE_RUN", body={"reason": "x"})),
            E.KIND_UNKNOWN)


class TestWakeLaw(unittest.TestCase):
    def test_a_command_wakes_only_the_worker(self):
        env = parse(payload())
        self.assertTrue(env.wakes("WORKER"))
        self.assertFalse(env.wakes("MANAGER"))

    def test_a_result_wakes_only_the_manager(self):
        env = parse(payload(kind="WAVE_RESULT", actor="WORKER",
                            message_id="w-result-0001", parent="m-command-0001"))
        self.assertTrue(env.wakes("MANAGER"))
        self.assertFalse(env.wakes("WORKER"))

    def test_no_actor_can_be_woken_by_its_own_message(self):
        for kind, actors in ACTOR_KIND.items():
            for actor in actors:
                parent = None if kind in ("WAVE_COMMAND", "WAVE_ABORT",
                                          "CAPTAIN_REQUIRED") else "m-command-0001"
                env = parse(payload(kind=kind, actor=actor, parent=parent,
                                    message_id="x-" + kind.lower().replace("_", "-")))
                with self.subTest(kind=kind, actor=actor):
                    self.assertFalse(env.wakes(actor))

    def test_progress_wakes_nobody(self):
        env = parse(payload(kind="WAVE_PROGRESS", actor="WORKER",
                            message_id="w-progress-0001", parent="m-command-0001"))
        for actor in ACTORS:
            with self.subTest(actor=actor):
                self.assertFalse(env.wakes(actor))

    def test_the_wake_table_never_lets_an_actor_wake_on_a_kind_it_speaks(self):
        for actor, kinds in WAKES.items():
            for kind in kinds:
                with self.subTest(actor=actor, kind=kind):
                    self.assertNotEqual(ACTOR_KIND[kind], frozenset({actor}))


class TestBodyLaw(unittest.TestCase):
    def test_a_result_must_name_the_command_it_answers(self):
        self.assertEqual(
            code_of(parse, payload(kind="WAVE_RESULT", actor="WORKER",
                                   message_id="w-result-0001", parent=None)),
            E.PARENT_REQUIRED)

    def test_a_worker_result_may_not_select_a_successor(self):
        body = dict(parse(payload(kind="WAVE_RESULT", actor="WORKER",
                                  message_id="w-result-0001",
                                  parent="m-command-0001")).body)
        body["next"] = "C00.ORACLE-COMPILER-MECHANICAL-CENSUS"
        self.assertEqual(
            code_of(parse, payload(kind="WAVE_RESULT", actor="WORKER",
                                   message_id="w-result-0001",
                                   parent="m-command-0001", body=body)),
            E.BAD_VALUE)

    def test_a_mutating_unit_without_scope_is_rejected(self):
        body = {"branch": "b", "review_boundary": "end",
                "units": [unit("U1", allow=())]}
        self.assertEqual(code_of(parse, payload(body=body)), E.UNIT_SCOPE_MISSING)

    def test_a_unit_without_validation_is_rejected(self):
        body = {"branch": "b", "review_boundary": "end",
                "units": [unit("U1", validation=())]}
        self.assertEqual(code_of(parse, payload(body=body)), E.UNIT_VALIDATION_MISSING)

    def test_a_read_only_unit_may_declare_no_write_scope(self):
        body = {"branch": "b", "review_boundary": "end",
                "units": [unit("U1", mutating=False, allow=())]}
        self.assertEqual(len(parse(payload(body=body)).body["units"]), 1)

    def test_an_unknown_unit_field_is_rejected(self):
        body = {"branch": "b", "review_boundary": "end",
                "units": [unit("U1", urgency="high")]}
        self.assertEqual(code_of(parse, payload(body=body)), E.UNKNOWN_FIELD)

    def test_a_result_head_must_be_a_sha(self):
        body = dict(parse(payload(kind="WAVE_RESULT", actor="WORKER",
                                  message_id="w-result-0001",
                                  parent="m-command-0001")).body)
        body["head"] = "the tip of the branch"
        self.assertEqual(
            code_of(parse, payload(kind="WAVE_RESULT", actor="WORKER",
                                   message_id="w-result-0001",
                                   parent="m-command-0001", body=body)),
            E.BAD_VALUE)

    def test_an_unknown_verdict_is_rejected(self):
        self.assertEqual(
            code_of(parse, payload(kind="WAVE_REVIEW", actor="MANAGER",
                                   message_id="m-review-0001", parent="w-result-0001",
                                   body={"verdict": "LGTM"})),
            E.BAD_VALUE)

    def test_a_review_may_propose_an_accepted_head(self):
        env = parse(payload(kind="WAVE_REVIEW", actor="MANAGER",
                            message_id="m-review-0001", parent="w-result-0001",
                            body={"verdict": "ACCEPT", "accepted_head": OTHER_SHA}))
        self.assertEqual(env.body["accepted_head"], OTHER_SHA)


if __name__ == "__main__":
    unittest.main()
