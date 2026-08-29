"""The output exception census: bounded, provenanced, and dispositive of nothing.

Stdlib only, like the rest of this suite — no YAML parser is available and P0.3A's
constraint forbids migrating or pinning a dependency, so these read the document's
blocks and lines directly.

The census is a claim about what tracked source references. These tests check that
it claims only that, that every candidate is traceable to a tracked source, and that
it does not quietly acquire the authority to delete anything.
"""

from __future__ import annotations

import re
import unittest

from tests.refoundation.helpers import REPO_ROOT, block, scalars

from mtj_foundry.paths import ProjectPaths

PATHS = ProjectPaths.for_root(REPO_ROOT)
CENSUS = PATHS.conservation / "OUTPUT-EXCEPTION-CENSUS.yaml"
INPUTS = PATHS.conservation / "BASELINE-INPUTS.yaml"

MUST_INCLUDE = (
    "experiments/out/foundry/audit-baseline.json",
    "experiments/out/foundry/codebook.json",
    "experiments/out/aq4/triage-deterministic-census.json",
    "experiments/out/aq4/unit-binding-adjudication-s0-a.json",
    "experiments/out/aq4/unit-binding-workqueue.json",
)

RESERVED_ROLES = ("ACCEPTANCE_CONTROL", "AUTHORITY_LOCAL_MIRROR",
                  "GOVERNANCE_OR_INCIDENT_EVIDENCE", "FROZEN_BENCHMARK_INPUT")


def entries(text: str) -> list[tuple[str, str]]:
    """(path, body) for every exact candidate entry."""
    section = text.split("exact_candidates:", 1)[1].split("\npattern_candidates:", 1)[0]
    out = []
    parts = re.split(r"\n    - path: ", section)
    for part in parts[1:]:
        path, _, body = part.partition("\n")
        out.append((path.strip(), body))
    return out


class CensusTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = CENSUS.read_text()
        cls.entries = entries(cls.text)


class TestStructure(CensusTestCase):
    def test_the_required_top_level_fields_are_present(self):
        top = [line.split(":", 1)[0] for line in self.text.splitlines()
               if line and line[0].isalpha() and ":" in line]
        for field in ("base_sha", "method", "scan_coverage", "exact_candidates",
                      "pattern_candidates", "unresolved", "hash_budget", "conclusions"):
            with self.subTest(field=field):
                self.assertIn(field, top)

    def test_the_schema_and_base_are_declared(self):
        recorded = scalars(self.text.split("\nmethod:", 1)[0])
        self.assertEqual(recorded["schema"], "mtj-output-exception-census/1")
        self.assertRegex(recorded["base_sha"], r"^[0-9a-f]{40}$")

    def test_the_declared_entry_count_matches_the_entries_present(self):
        declared = int(re.search(r"exact_candidates:\n  count: (\d+)", self.text).group(1))
        self.assertEqual(declared, len(self.entries))


class TestConclusionsAuthorizeNothing(CensusTestCase):
    """A census is evidence. It must not be able to become permission."""

    def setUp(self):
        self.body = block(self.text, "conclusions")

    def test_deletion_is_not_authorized(self):
        self.assertIn("deletion_authorized: false", self.body)

    def test_the_tree_is_not_classified(self):
        self.assertIn("whole_tree_classified: false", self.body)

    def test_manager_review_is_required(self):
        self.assertIn("manager_review_required: true", self.body)

    def test_no_disposition_was_assigned(self):
        self.assertIn("dispositions_assigned: NONE", self.body)

    def test_exhaustiveness_is_explicitly_disclaimed(self):
        self.assertIn("candidate_list_exhaustive: false", self.body)
        coverage = block(self.text, "scan_coverage")
        self.assertIn("exhaustive_over_output_tree: false", coverage)

    def test_the_derivable_role_is_stated_as_a_hypothesis(self):
        flat = " ".join(self.body.split())
        self.assertIn("HYPOTHESIS from the consumer set", flat)

    def test_non_authoritative_is_not_treated_as_disposable(self):
        flat = " ".join(self.body.split())
        self.assertIn("non_authoritative != disposable", flat)

    def test_the_document_disclaims_its_own_status_field(self):
        flat = " ".join(self.body.split())
        self.assertIn("status field cannot ratify anything", flat)


class TestBoundedness(CensusTestCase):
    """The task forbids enumerating or hashing the 2.9GB tree."""

    def test_the_tree_was_not_enumerated(self):
        method = block(self.text, "method")
        self.assertIn("whole_tree_enumeration: false", method)
        self.assertIn("whole_tree_hash: false", method)

    def test_the_candidate_count_is_far_below_the_tree_size(self):
        """A census of 3321 files would BE the enumeration the task forbids."""
        self.assertLess(len(self.entries), 500)
        self.assertIn("known_total_files_in_tree: 3321", block(self.text, "scan_coverage"))

    def test_pattern_references_claim_no_subtree_cardinality(self):
        body = block(self.text, "pattern_candidates")
        self.assertIn("subtree_enumerated: false", body)
        self.assertIn("subtree_cardinality_claimed: false", body)

    def test_the_hash_budget_was_respected(self):
        body = block(self.text, "hash_budget")
        recorded = scalars(body)
        self.assertLessEqual(int(recorded["bytes_read"]), int(recorded["total_read_cap_bytes"]))
        self.assertEqual(int(recorded["deferred_files_read"]), 0)

    def test_no_reserved_role_was_deferred_for_budget(self):
        """A budget spent on batch output while an authority file went unmeasured
        would be a census that measured the wrong things."""
        deferred = block(self.text, "hash_budget").split("deferred:", 1)[1]
        for role in RESERVED_ROLES:
            with self.subTest(role=role):
                self.assertNotIn(role, deferred)


class TestProvenance(CensusTestCase):
    """Nothing may appear in the census because it looked important."""

    def test_every_candidate_carries_at_least_one_tracked_source(self):
        for path, body in self.entries:
            with self.subTest(path=path):
                self.assertIn("provenance:", body)
                self.assertRegex(body, r"- source: \S+")

    def test_every_candidate_declares_its_roles(self):
        for path, body in self.entries:
            with self.subTest(path=path):
                roles = re.search(r"roles: \[([^\]]+)\]", body)
                self.assertIsNotNone(roles, f"{path} declares no roles")
                for role in roles.group(1).split(", "):
                    self.assertIn(role, RESERVED_ROLES + ("DERIVABLE_OUTPUT_CANDIDATE",
                                                          "UNKNOWN_REVIEW"))

    def test_every_role_states_the_basis_it_was_derived_from(self):
        for path, body in self.entries:
            roles = re.search(r"roles: \[([^\]]+)\]", body).group(1).split(", ")
            for role in roles:
                with self.subTest(path=path, role=role):
                    self.assertIn(f"role_basis_{role.lower()}:", body)

    def test_the_multi_role_path_records_both_roles(self):
        """A single-role classifier would have dropped one consumer silently."""
        body = dict(self.entries)["experiments/out/aq4/unit-binding-workqueue.json"]
        self.assertIn("GOVERNANCE_OR_INCIDENT_EVIDENCE", body)
        self.assertIn("FROZEN_BENCHMARK_INPUT", body)

    def test_role_totals_exceeding_the_count_is_declared_not_accidental(self):
        head = self.text.split("exact_candidates:", 1)[1].split("  entries:", 1)[0]
        assignments = int(re.search(r"role_assignments: (\d+)", head).group(1))
        multi = int(re.search(r"paths_with_multiple_roles: (\d+)", head).group(1))
        self.assertEqual(assignments, len(self.entries) + multi)


class TestMeasurement(CensusTestCase):
    def test_every_must_include_path_is_present(self):
        present = {p for p, _ in self.entries}
        for path in MUST_INCLUDE:
            with self.subTest(path=path):
                self.assertIn(path, present)

    def test_every_must_include_path_was_actually_measured(self):
        for path in MUST_INCLUDE:
            body = dict(self.entries)[path]
            with self.subTest(path=path):
                self.assertIn("hash_status: MEASURED", body)
                self.assertRegex(body, r"sha256_measured: [0-9a-f]{64}")

    def test_existence_and_measurement_are_distinguished(self):
        for path, body in self.entries:
            with self.subTest(path=path):
                self.assertRegex(body, r"exists: (true|false)")
                if "exists: false" in body:
                    self.assertIn("NOT_MEASURED_FILE_ABSENT", body)
                    self.assertNotIn("sha256_measured", body)

    def test_a_deferred_hash_records_that_nothing_was_read(self):
        for path, body in self.entries:
            if "DEFERRED" in body:
                with self.subTest(path=path):
                    self.assertIn("bytes_read: 0", body)
                    self.assertNotIn("sha256_measured", body)

    def test_a_quoted_hash_is_never_presented_as_a_measurement(self):
        """The incident quotes a TRUNCATED prefix; this census computed the full value.

        Recording them as one field would launder a quote into a measurement.
        """
        body = dict(self.entries)["experiments/out/aq4/unit-binding-workqueue.json"]
        self.assertIn("quoted_hash_from_tracked_record:", body)
        self.assertIn("truncated_in_source: true", body)
        quoted = re.search(r"quoted_hash_from_tracked_record:\n\s+value: (\S+)", body).group(1)
        measured = re.search(r"sha256_measured: (\S+)", body).group(1)
        self.assertNotEqual(quoted, measured, "a truncated quote must not equal a measurement")
        self.assertTrue(measured.startswith(quoted))
        self.assertLess(len(quoted), 64)


class TestAgreementWithPriorEvidence(CensusTestCase):
    def test_the_ratchet_hash_agrees_with_the_p0_3a_capture(self):
        """Re-derived independently here; it must not have drifted from BASELINE-INPUTS."""
        recorded = scalars(INPUTS.read_text())
        body = dict(self.entries)["experiments/out/foundry/audit-baseline.json"]
        measured = re.search(r"sha256_measured: (\S+)", body).group(1)
        self.assertEqual(measured, recorded["source_sha256"])

    def test_the_codebook_mirror_matches_the_tracked_selector(self):
        import json

        selector = json.loads((PATHS.legacy_docs / "codebook-authority.json").read_text())
        body = dict(self.entries)["experiments/out/foundry/codebook.json"]
        measured = re.search(r"sha256_measured: (\S+)", body).group(1)
        size = int(re.search(r"size_bytes: (\d+)", body).group(1))
        self.assertEqual(measured, selector["sha256"])
        self.assertEqual(size, selector["byte_size"])

    def test_the_ratchet_and_codebook_roles_are_derived_from_their_consumers(self):
        ratchet = dict(self.entries)["experiments/out/foundry/audit-baseline.json"]
        codebook = dict(self.entries)["experiments/out/foundry/codebook.json"]
        self.assertIn("ACCEPTANCE_CONTROL", ratchet)
        self.assertIn("foundry_audit_baseline.py", ratchet)
        self.assertIn("AUTHORITY_LOCAL_MIRROR", codebook)
        self.assertIn("codebook-authority.json", codebook)

    def test_no_codebook_content_was_copied_into_the_repository(self):
        """5MB of authoritative content must stay out of git; identity is the hash.

        Asserted on card RECORDS, not on the word "oracle_id": provenance quotes lines
        from tracked docs, and several of those lines mention the field by name. A
        first version of this test matched the word and fired on a quoted context line
        — a proxy for the property rather than the property. Actual card data would
        carry oracle_id VALUES, which are UUIDs.
        """
        uuid = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
        self.assertLess(CENSUS.stat().st_size, 1_000_000)
        for path in sorted(PATHS.conservation.iterdir()):
            with self.subTest(path=path.name):
                text = path.read_text()
                self.assertIsNone(uuid.search(text), "a card/oracle UUID appears in a "
                                                     "conservation artifact")
                self.assertNotIn('"oracle_id":', text, "a card record was copied in")

    def test_the_codebook_is_pinned_by_identity_rather_than_content(self):
        """The negative control for the test above: identity IS recorded, just not bytes."""
        body = dict(self.entries)["experiments/out/foundry/codebook.json"]
        self.assertRegex(body, r"sha256_measured: [0-9a-f]{64}")
        self.assertIn("size_bytes: 5066147", body)


class TestDeclaredBlindSpot(CensusTestCase):
    """A census that hid its own coverage limits would be the more dangerous artifact."""

    def test_unresolvable_dynamic_constructions_are_recorded(self):
        body = block(self.text, "unresolved")
        count = int(re.search(r"dynamic_construction_shapes: (\d+)", body).group(1))
        self.assertGreater(count, 0)
        self.assertIn("construction:", body)

    def test_the_implication_of_the_blind_spot_is_stated(self):
        flat = " ".join(block(self.text, "unresolved").split())
        self.assertIn("can reach paths this census never names", flat)

    def test_the_constructed_reference_arm_is_documented_with_its_witness(self):
        """The literal grep misses the ratchet: its writer builds the path from __file__."""
        flat = " ".join(block(self.text, "method").split())
        self.assertIn("foundry_audit_baseline.py", flat)
        self.assertIn("literal grep does not find", flat)


# --- P0.3B.R1: the document must be YAML, not YAML-shaped ------------------
#
# The first version of this census carried `sites: 1` with an indented `- source:`
# sequence beneath it. Every test above passed, because every test above reads the
# document as LINES. A line test cannot see that its subject is not parseable, so
# the primary artifact of a conservation census was not a valid document and nothing
# in the suite said so.
#
# No YAML parser is available to this suite and P0.3A forbids pinning one, so this is
# a structural detector for the exact defect class rather than a parse: a key that
# carries a scalar value CANNOT also own a block sequence (YAML 1.2 §8.2.1 — a block
# node is either a scalar or a collection, never both). The repair splits the two
# facts the old shape conflated into `site_count` and `sites`.

BLOCK_SCALAR = re.compile(r":\s*[|>][-+]?\d*\s*$")
KEY_WITH_SCALAR = re.compile(r"^(\s*)(?:- )?[^\s#][^:]*:\s+(\S.*)$")
SEQUENCE_ITEM = re.compile(r"^(\s*)- ")


def scalar_keys_owning_a_block_sequence(text: str) -> list[tuple[int, str]]:
    """(line number, line) for every key that carries a scalar AND a deeper sequence.

    Content inside a block scalar is skipped: prose there may contain a colon or open
    with a dash without being structure. Reporting those would make the detector a
    stylistic complaint rather than a parse-failure witness.
    """
    lines = text.split("\n")
    found = []
    skip_below = None
    for i, line in enumerate(lines):
        indent = len(line) - len(line.lstrip())
        if skip_below is not None:
            if not line.strip() or indent > skip_below:
                continue
            skip_below = None
        if BLOCK_SCALAR.search(line):
            skip_below = indent
            continue
        match = KEY_WITH_SCALAR.match(line)
        if not match:
            continue
        for nxt in lines[i + 1:]:
            if not nxt.strip():
                continue
            item = SEQUENCE_ITEM.match(nxt)
            if item and len(item.group(1)) > len(match.group(1)):
                found.append((i + 1, line))
            break
    return found


class TestTheDocumentIsParseable(CensusTestCase):
    INVALID_SHAPE = (
        "unresolved:\n"
        "  entries:\n"
        "    - construction: \"FOUNDRY_OUT_DIR / f'stage1b_batch{suffix}.json'\"\n"
        "      sites: 1\n"
        "        - source: experiments/foundry_common.py\n"
        "          line: 126\n"
    )

    def test_no_key_carries_both_a_scalar_and_a_block_sequence(self):
        offenders = scalar_keys_owning_a_block_sequence(self.text)
        self.assertEqual(offenders, [], "\n".join(f"line {n}: {l}" for n, l in offenders))

    def test_the_detector_fires_on_the_shape_that_shipped(self):
        """Negative control. A guard never shown to fail is not known to be a guard."""
        offenders = scalar_keys_owning_a_block_sequence(self.INVALID_SHAPE)
        self.assertEqual(len(offenders), 1)
        self.assertIn("sites: 1", offenders[0][1])

    def test_the_detector_accepts_the_repaired_shape(self):
        """The other half of the control: it must not fire on a key with no scalar."""
        repaired = self.INVALID_SHAPE.replace("      sites: 1\n",
                                              "      site_count: 1\n      sites:\n")
        self.assertEqual(scalar_keys_owning_a_block_sequence(repaired), [])

    def test_block_scalar_prose_is_not_read_as_structure(self):
        """A `>-` body may hold a colon and a dash; that is text, not a mapping."""
        prose = "conclusions:\n  note: >-\n    A finding: it holds.\n    - and a dash\n"
        self.assertEqual(scalar_keys_owning_a_block_sequence(prose), [])


class TestTheBlindSpotSurvivedTheRepair(CensusTestCase):
    """The repair is structural. Every fact the old shape asserted must still be here."""

    def setUp(self):
        self.body = block(self.text, "unresolved")

    def test_every_construction_records_a_site_count_and_a_sites_sequence(self):
        declared = int(re.search(r"dynamic_construction_shapes: (\d+)", self.body).group(1))
        constructions = re.findall(r"\n    - construction: ", self.body)
        self.assertEqual(len(constructions), declared)
        self.assertEqual(len(re.findall(r"\n      site_count: \d+\n", self.body)), declared)
        self.assertEqual(len(re.findall(r"\n      sites:\n", self.body)), declared)

    def test_each_declared_site_count_matches_the_sites_recorded_under_it(self):
        for entry in self.body.split("\n    - construction: ")[1:]:
            construction, _, rest = entry.partition("\n")
            with self.subTest(construction=construction.strip()):
                declared = int(re.search(r"site_count: (\d+)", rest).group(1))
                sites = re.findall(r"\n        - source: ", rest)
                self.assertEqual(declared, len(sites))

    def test_every_site_keeps_its_source_line_and_context(self):
        for entry in self.body.split("\n        - source: ")[1:]:
            source, _, rest = entry.partition("\n")
            with self.subTest(source=source.strip()):
                self.assertRegex(rest, r"^          line: \d+\n          context: ")


if __name__ == "__main__":
    unittest.main()
