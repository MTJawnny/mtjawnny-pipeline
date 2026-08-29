"""The captured baseline and the recorded decisions must agree with the bytes.

These are the tests that would catch a capture that LOOKED done: a truncated copy,
a hash typed rather than derived, or a decision record that drifted from what
Captain actually ratified.
"""

from __future__ import annotations

import unittest

from tests.refoundation.helpers import REPO_ROOT, scalars, top_level_keys

from mtj_foundry.conservation import digest_file
from mtj_foundry.paths import ProjectPaths

PATHS = ProjectPaths.for_root(REPO_ROOT)
BASELINE_COPY = PATHS.baselines / "foundry-audit-baseline.json"
INPUTS = PATHS.conservation / "BASELINE-INPUTS.yaml"
DECISIONS = PATHS.decisions / "P0-ARCHITECTURE.yaml"


class TestCapturedRatchetBaseline(unittest.TestCase):
    """Acceptance criterion: "copied baseline sha256 == source baseline sha256".

    The source is gitignored and lives outside this worktree, so the durable form
    of that criterion is: the copy still hashes to the value recorded at capture
    time. A later drift in either the bytes or the record fails here.
    """

    def test_the_tracked_copy_exists_and_is_not_empty(self):
        self.assertTrue(BASELINE_COPY.exists(), f"missing {BASELINE_COPY}")
        self.assertGreater(BASELINE_COPY.stat().st_size, 0)

    def test_the_copy_still_hashes_to_the_recorded_source_digest(self):
        recorded = scalars(INPUTS.read_text())
        actual = digest_file(BASELINE_COPY)
        self.assertEqual(actual.sha256, recorded["source_sha256"])
        self.assertEqual(actual.sha256, recorded["tracked_copy_sha256"])
        self.assertEqual(actual.size_bytes, int(recorded["source_size_bytes"]))
        self.assertEqual(recorded["byte_identical"], "true")

    def test_the_copy_is_valid_json_and_carries_the_ratchet_sections(self):
        import json

        data = json.loads(BASELINE_COPY.read_text())
        self.assertIsInstance(data, dict)
        self.assertIn("conservation", data,
                      "the captured file is not the audit ratchet baseline")

    def test_no_consumer_was_repointed_at_the_copy(self):
        """Zero legacy behavior change: capturing bytes must not move a read path."""
        recorded = scalars(INPUTS.read_text())
        self.assertEqual(recorded["consumers_repointed"], "NONE")
        self.assertEqual(recorded["values_changed"], "NONE")


class TestBaselineInputsInventory(unittest.TestCase):
    def test_the_inventory_declares_its_schema_and_read_only_capture(self):
        text = INPUTS.read_text()
        recorded = scalars(text)
        self.assertEqual(recorded["schema"], "mtj-conservation-baseline-inputs/1")
        self.assertEqual(recorded["mutations_to_inventoried_sources"], "NONE")
        self.assertEqual(recorded["read_only"], "true")

    def test_the_declared_local_only_set_matches_the_bootstrap_declaration(self):
        """BOOTSTRAP-STATE declares 1 modified tracked + 9 untracked."""
        recorded = scalars(INPUTS.read_text())
        self.assertEqual(int(recorded["untracked_count"]), 9)
        self.assertEqual(int(recorded["entry_count"]), 10)

    def test_every_inventoried_entry_carries_a_hash_and_a_size(self):
        """A path list is not conservation; the pair is the identity."""
        import re

        text = INPUTS.read_text()
        blocks = re.findall(r"^\s+- path: (\S+)\n((?:\s+\w+:.*\n)+)", text, re.M)
        self.assertGreaterEqual(len(blocks), 10)
        for path, body in blocks:
            with self.subTest(path=path):
                self.assertRegex(body, r"sha256: [0-9a-f]{64}")
                self.assertRegex(body, r"size_bytes: \d+")

    def test_the_selected_codebook_authority_is_pinned_by_hash_and_size(self):
        """C7.1: exact sha256 AND byte size, never a canonicalized re-serialization."""
        recorded = scalars(INPUTS.read_text())
        self.assertRegex(recorded["selected_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(int(recorded["selected_byte_size"]), 5066147)
        self.assertEqual(recorded["local_matches_selected_authority"], "true")
        self.assertEqual(recorded["copied_into_repository"], "false",
                         "codebook content must never enter git")

    def test_what_was_not_inventoried_is_stated_explicitly(self):
        text = INPUTS.read_text()
        self.assertIn("not_inventoried:", text)
        self.assertIn("EPHEMERAL_OUTPUT", text)


class TestP0ArchitectureDecisionRecord(unittest.TestCase):
    def test_the_record_declares_the_selector_decision_schema(self):
        recorded = scalars(DECISIONS.read_text())
        self.assertEqual(recorded["schema"], "mtj-decision-record/1")
        self.assertEqual(recorded["set"], "P0.ARCHITECTURE")

    def test_the_two_captain_decisions_are_recorded_verbatim(self):
        text = DECISIONS.read_text()
        self.assertIn("decision: mtj_foundry", text)
        self.assertIn("decision: selector_decision_record", text)

    def test_the_ratified_constraints_are_recorded(self):
        text = DECISIONS.read_text()
        for constraint, value in (("frontmatter_self_authority", "false"),
                                  ("aq4", "PAUSED"),
                                  ("bridge_v0", "PARKED_UNUSED"),
                                  ("p0_reconstruction", "AUTHORIZED")):
            with self.subTest(constraint=constraint):
                self.assertRegex(text, rf"constraint: {constraint}\n\s+value: {value}")

    def test_every_ratified_record_names_captain_and_a_durable_source(self):
        """C5: nothing is binding merely because a field says RATIFIED."""
        import re

        text = DECISIONS.read_text()
        ratified = text.split("ratified:", 1)[1].split("accepted_direction:", 1)[0]
        ids = re.findall(r"- id: (\S+)", ratified)
        self.assertGreaterEqual(len(ids), 6)
        self.assertEqual(len(ids), ratified.count("authority: CAPTAIN"))
        self.assertEqual(len(ids), ratified.count("status: RATIFIED"))
        self.assertEqual(len(ids), ratified.count("source: issue:1#issuecomment-5463518042"))

    def test_manager_direction_is_not_recorded_as_ratified(self):
        """Direction must not be able to pass itself off as law."""
        text = DECISIONS.read_text()
        direction = text.split("accepted_direction:", 1)[1].split("measurements:", 1)[0]
        self.assertIn("status: ACCEPTED_MANAGER_REVIEW", direction)
        self.assertIn("authority: MANAGER", direction)
        self.assertNotIn("status: RATIFIED", direction)

    def test_worker_measurements_are_marked_evidence_not_targets(self):
        text = DECISIONS.read_text()
        measurements = text.split("measurements:", 1)[1]
        self.assertIn("status: EVIDENCE", measurements)
        self.assertIn("authority: WORKER", measurements)
        # The warning is prose and wraps, so normalise whitespace before matching.
        flat = " ".join(measurements.split())
        self.assertIn("must not become new ratchets", flat)

    def test_the_record_states_what_this_phase_did_not_decide(self):
        self.assertIn("not_decided_by_this_phase", top_level_keys(DECISIONS.read_text()))


if __name__ == "__main__":
    unittest.main()
