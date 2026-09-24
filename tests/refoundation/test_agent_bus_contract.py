"""The documents are an API: guard what the control plane PROMISES.

`refoundation/AGENT-BUS.md` is read by a cold-starting Manager and a cold-starting
Worker, and its kinds table is the same table the parser enforces. A document
that drifts from the code it describes is worse than no document, because both
agents will believe it.

This module also pins the production build workflow by digest. The Agent Bus
authorization is explicit that build behaviour does not change, and "we did not
mean to touch it" is not a measurement.
"""

from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path

from tests.refoundation.agent_bus_fixtures import REPO_ROOT

from agent_bus import SCHEMA
from agent_bus.cli import build_parser, main as cli_main
from agent_bus.protocol import ACTOR_KIND, FENCE_INFO, KINDS, WAKES, parse
from agent_bus.git_evidence import UNIT_TRAILER, WAVE_TRAILER

BUS_DOC = REPO_ROOT / "refoundation" / "AGENT-BUS.md"
ARCH_DOC = (REPO_ROOT / "docs" / "architecture"
            / "AGENT-BUS-V1-ARCHITECTURE-2026-09-23.md")
CLAUDE = REPO_ROOT / "CLAUDE.md"
README = REPO_ROOT / "README.md"
PROTOCOL_DOC = REPO_ROOT / "refoundation" / "SESSION-PROTOCOL.md"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "agent-bus-validate.yml"
BUILD = REPO_ROOT / ".github" / "workflows" / "build.yml"
EXAMPLES = sorted((REPO_ROOT / "agent_bus" / "examples").glob("*.json"))

# The production pipeline as this task found it. Changing this digest is a claim
# that build behaviour changed, and that claim needs its own authorization.
BUILD_DIGEST = "147ddf774f6d5f71cd11363c3ce88e85bb0e081ccd8f625665e227902ffa7800"

SELECTOR = "latest `K` -> active `T`"
ROW_RE = re.compile(r"^\|\s*([A-Z_]+)\s*\|\s*([A-Z, ]+?)\s*\|", re.MULTILINE)


def table_rows(text: str) -> dict[str, frozenset[str]]:
    return {
        kind: frozenset(a.strip() for a in actors.split(","))
        for kind, actors in ROW_RE.findall(text)
        if kind in KINDS
    }


class TestTransportContractDocument(unittest.TestCase):
    def setUp(self):
        self.doc = BUS_DOC.read_text(encoding="utf-8")

    def test_the_contract_exists_and_names_the_one_selector(self):
        self.assertIn(SELECTOR, self.doc)

    def test_it_states_that_the_bus_is_not_authority(self):
        for phrase in ("Authority is not here",
                       "accepted head is an input to the bus, never an output",
                       "never because a comment is newer"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_the_kinds_table_matches_the_parser_exactly(self):
        self.assertEqual(table_rows(self.doc), dict(ACTOR_KIND))

    def test_the_documented_wake_rules_match_the_wake_table(self):
        rows = table_rows(self.doc)
        self.assertEqual(sorted(rows), sorted(KINDS))
        for kind in KINDS:
            wakes = {actor for actor, kinds in WAKES.items() if kind in kinds}
            claims_worker = f"| {kind} |" in self.doc and "wakes the Worker" in \
                self.doc.split(f"| {kind} |")[1].split("\n")[0]
            with self.subTest(kind=kind):
                self.assertEqual(claims_worker, "WORKER" in wakes)

    def test_it_documents_the_fence_and_the_trailers(self):
        self.assertIn(f"`{FENCE_INFO}`", self.doc)
        self.assertIn(WAVE_TRAILER, self.doc)
        self.assertIn(UNIT_TRAILER, self.doc)

    def test_it_states_that_finishing_a_unit_is_not_a_stop(self):
        self.assertIn("Finishing a unit is not a STOP condition", self.doc)

    def test_it_keeps_independent_review_mandatory(self):
        self.assertIn("The Worker never accepts its own work", self.doc)
        self.assertIn("They do not change WHO reviews", self.doc)


class TestRoutingPointsAtTheTransportLayer(unittest.TestCase):
    def test_the_worker_contract_carries_the_wave_law(self):
        claude = CLAUDE.read_text(encoding="utf-8")
        self.assertIn("bounded wave", claude)
        self.assertIn("finishing a unit is **not** a STOP", claude)
        self.assertIn("refoundation/AGENT-BUS.md", claude)

    def test_the_session_protocol_evolved_rather_than_forbidding_automation(self):
        protocol = PROTOCOL_DOC.read_text(encoding="utf-8")
        self.assertIn("bounded WAVE", protocol)
        self.assertIn("refoundation/AGENT-BUS.md", protocol)
        self.assertNotIn("Automation of the loop itself waits", protocol)

    def test_the_generic_router_names_the_transport_without_selecting_work(self):
        readme = README.read_text(encoding="utf-8")
        self.assertIn("refoundation/AGENT-BUS.md", readme)
        self.assertIn("never a second selector", readme)

    def test_the_architecture_record_names_the_remaining_manual_steps(self):
        arch = ARCH_DOC.read_text(encoding="utf-8")
        self.assertIn("What a human must still do outside this repository", arch)
        self.assertIn("ChatGPT Work GitHub connector", arch)


class TestExamplesAreRealMessages(unittest.TestCase):
    def test_there_are_examples(self):
        self.assertTrue(EXAMPLES)

    def test_every_example_parses_under_the_live_protocol(self):
        for path in EXAMPLES:
            with self.subTest(example=path.name):
                envelope = parse(path.read_text(encoding="utf-8"))
                self.assertEqual(envelope.schema, SCHEMA)

    def test_the_example_command_and_result_correlate(self):
        by_kind = {parse(p.read_text()).kind: parse(p.read_text()) for p in EXAMPLES}
        self.assertEqual(by_kind["WAVE_RESULT"].parent,
                         by_kind["WAVE_COMMAND"].message_id)
        self.assertEqual(by_kind["WAVE_REVIEW"].parent,
                         by_kind["WAVE_RESULT"].message_id)


class TestWorkflowSurface(unittest.TestCase):
    def setUp(self):
        self.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_the_production_build_workflow_is_byte_identical_to_its_authorized_state(self):
        digest = hashlib.sha256(BUILD.read_bytes()).hexdigest()
        self.assertEqual(digest, BUILD_DIGEST)

    def test_the_bus_workflow_carries_no_secret_and_needs_none(self):
        self.assertNotIn("secrets.", self.workflow)
        self.assertIn("permissions:\n  contents: read", self.workflow)

    def test_the_bus_workflow_cannot_wake_an_agent(self):
        # "issue_comment" and "issues" would be the wake triggers, and they run
        # only from the default branch. Neither appears here.
        for trigger in ("issue_comment:", "issues:", "schedule:"):
            with self.subTest(trigger=trigger):
                self.assertNotIn(trigger, self.workflow)

    def test_the_bus_workflow_runs_the_suite_and_a_negative_control(self):
        self.assertIn("python3 -m agent_bus selftest", self.workflow)
        self.assertIn("mtj-agent-bus/99", self.workflow)
        self.assertIn("expected exit 2", self.workflow)


class TestOperatorSurface(unittest.TestCase):
    def test_the_documented_commands_are_exactly_the_registered_ones(self):
        arch = ARCH_DOC.read_text(encoding="utf-8")
        documented = set(re.findall(r"python3 -m agent_bus ([a-z]+)", arch))
        self.assertEqual(documented, set(build_parser()[1]))

    def test_an_unknown_command_is_refused(self):
        with self.assertRaises(SystemExit):
            cli_main(["definitely-not-a-command"])


class TestPopulationAccounting(unittest.TestCase):
    """The control plane is a NAMED population, not a file hiding in `other`.

    The layout census exists to stop a live population from disappearing into an
    unnamed bucket. A new top-level package therefore has to be classified, and
    classified as what it is: control plane, not legacy production, so no
    delegation or bootstrap count moves because it exists.
    """

    def setUp(self):
        from tests.refoundation import layout_census
        self.census = layout_census

    def test_the_bus_package_is_a_walked_base(self):
        self.assertIn("agent_bus", self.census.WALK_BASES)

    def test_bus_files_land_in_their_own_named_scope(self):
        self.assertEqual(self.census.scope_of(Path("agent_bus/protocol.py")),
                         "agent_bus")

    def test_the_control_plane_is_not_legacy_production(self):
        self.assertNotIn("agent_bus", self.census.LEGACY_PRODUCTION)

    def test_NC0_an_unnamed_top_level_package_would_still_fall_into_other(self):
        self.assertEqual(self.census.scope_of(Path("some_new_tool/thing.py")), "other")


class TestContractNegativeControls(unittest.TestCase):
    def test_NC1_a_kinds_table_that_drifts_from_the_parser_is_red(self):
        rigged = BUS_DOC.read_text().replace(
            "| WAVE_COMMAND | MANAGER |", "| WAVE_COMMAND | MANAGER, WORKER |")
        self.assertNotEqual(table_rows(rigged), dict(ACTOR_KIND))

    def test_NC2_dropping_the_selector_from_the_contract_is_red(self):
        rigged = BUS_DOC.read_text().replace(SELECTOR, "whatever the newest comment says")
        self.assertNotIn(SELECTOR, rigged)

    def test_NC3_a_changed_build_workflow_is_red(self):
        rigged = BUILD.read_bytes() + b"\n      - run: echo drift\n"
        self.assertNotEqual(hashlib.sha256(rigged).hexdigest(), BUILD_DIGEST)

    def test_NC4_a_wake_trigger_in_the_bus_workflow_is_red(self):
        rigged = WORKFLOW.read_text().replace("  workflow_dispatch: {}",
                                              "  issue_comment:\n    types: [created]")
        self.assertIn("issue_comment:", rigged)

    def test_NC5_a_secret_in_the_bus_workflow_is_red(self):
        rigged = WORKFLOW.read_text().replace(
            "          python-version: \"3.11\"",
            "          python-version: \"3.11\"\n        env:\n"
            "          KEY: ${{ secrets.ANTHROPIC_API_KEY }}")
        self.assertIn("secrets.", rigged)


if __name__ == "__main__":
    unittest.main()
