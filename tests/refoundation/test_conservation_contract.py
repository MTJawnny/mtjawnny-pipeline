"""C8 step 2: the invariant harness, and every way it must refuse to answer.

Stdlib only, like the rest of this tree.

Two properties carry the phase, and they pull in opposite directions, which is why
both are tested from both sides:

    the same truth read from two different paths is CONSERVED
    a changed truth is DRIFTED wherever it was read from

Everything else here is a negative control. A harness that reported a verdict when
it should have stopped would turn its own misconfiguration into a finding about the
repository, so each fail-closed rule is exercised by breaking it on purpose.
"""

from __future__ import annotations

import copy
import dataclasses
import hashlib
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT, block, scalars

import mtj_foundry.conservation_contract as cc
from mtj_foundry.conservation import PathDomainError
from mtj_foundry.paths import ProjectPaths

PATHS = ProjectPaths.for_root(REPO_ROOT)
CONTRACT_PATH = PATHS.conservation / "CONSERVATION-CONTRACT.json"
INPUTS_PATH = PATHS.conservation / "BASELINE-INPUTS.yaml"

ACTIVE_EXPECTED = ("CODEBOOK_AUTHORITY_IDENTITY", "CR_EDITION_CONTENT",
                   "RATCHET_BASELINE_BYTES")
DEFERRED_EXPECTED = ("GATE2_INVARIANTS_AND_KNOWN_DEBT", "ROUTING_RELATION",
                     "RULING_DECISIONS", "AQ4_FROZEN_STATE_AND_GOVERNANCE")


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ContractTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.contract = cc.load_contract(CONTRACT_PATH)

    def load_variant(self, mutate) -> cc.Contract:
        """Load a deliberately broken copy of the real contract.

        Built by mutating the shipped document rather than by hand-writing a minimal
        one: a control written from scratch tests the checker against a fixture, and
        the fixture is the thing most likely to be wrong.
        """
        doc = copy.deepcopy(self.document)
        mutate(doc)
        tmp = Path(tempfile.mkdtemp()) / "CONTRACT.json"
        tmp.write_text(json.dumps(doc), encoding="utf-8")
        self.addCleanup(shutil.rmtree, tmp.parent, ignore_errors=True)
        return cc.load_contract(tmp)


# ---------------------------------------------------------------------------
# The document
# ---------------------------------------------------------------------------


class TestTheC7InventoryIsStatedInFull(ContractTestCase):
    def test_every_c7_item_is_present_exactly_once(self):
        ids = [i["invariant_id"] for i in self.document["invariants"]]
        self.assertEqual(sorted(ids), sorted(cc.C7_INVENTORY))
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_item_is_active_or_deferred_with_a_reason(self):
        for invariant in self.contract.invariants.values():
            with self.subTest(invariant=invariant.invariant_id):
                self.assertIn(invariant.status,
                              (cc.ACTIVE_MECHANICAL, cc.DEFERRED_WITH_REASON))

    def test_the_active_and_deferred_sets_are_the_ones_the_task_named(self):
        self.assertEqual(set(self.contract.active_ids), set(ACTIVE_EXPECTED))
        self.assertEqual(set(self.contract.deferred_ids), set(DEFERRED_EXPECTED))

    def test_every_deferred_item_names_the_work_it_is_missing(self):
        """'Deferred' with no reason is indistinguishable from forgotten."""
        for invariant_id in self.contract.deferred_ids:
            invariant = self.contract.invariants[invariant_id]
            with self.subTest(invariant=invariant_id):
                self.assertTrue(invariant.deferred_reason.strip())
                self.assertGreaterEqual(len(invariant.what_a_comparator_would_require), 1)

    def test_no_deferred_item_carries_half_a_comparator(self):
        for invariant_id in self.contract.deferred_ids:
            invariant = self.contract.invariants[invariant_id]
            with self.subTest(invariant=invariant_id):
                self.assertIsNone(invariant.comparison_kind)
                self.assertIsNone(invariant.extractor)
                self.assertEqual(invariant.value_fields, ())

    def test_every_active_item_declares_a_kind_an_extractor_and_typed_fields(self):
        for invariant_id in self.contract.active_ids:
            invariant = self.contract.invariants[invariant_id]
            with self.subTest(invariant=invariant_id):
                self.assertIn(invariant.comparison_kind, cc.COMPARISON_KINDS)
                self.assertIn(invariant.extractor, cc._EXTRACTORS)
                self.assertTrue(invariant.value_fields)
                for field in invariant.value_fields:
                    self.assertIn(field.type, cc.VALUE_FIELD_TYPES)

    def test_the_contract_ratifies_nothing(self):
        self.assertEqual(self.document["authority"]["this_document_ratifies"], "NOTHING")
        self.assertEqual(self.document["authority"]["ratified_by"], "NONE")

    def test_no_deferred_invariant_is_bound_to_a_source_on_any_side(self):
        """A binding is a comparator. Giving a deferred item one is the back door."""
        for side in self.contract.sides.values():
            for invariant_id in side.bindings:
                with self.subTest(side=side.side_id, invariant=invariant_id):
                    self.assertTrue(self.contract.invariants[invariant_id].is_active)

    def test_every_side_binds_every_active_invariant(self):
        for side in self.contract.sides.values():
            with self.subTest(side=side.side_id):
                self.assertEqual(set(side.bindings), set(self.contract.active_ids))

    def test_the_ratchet_is_the_worked_case_and_is_bound_to_two_different_paths(self):
        """C7.7 is the one truth that has actually moved, so it is the real witness
        that source path is not identity."""
        paths = {side.side_id: side.bindings["RATCHET_BASELINE_BYTES"].source_path
                 for side in self.contract.sides.values()}
        self.assertEqual(len(set(paths.values())), 2, paths)
        self.assertEqual(paths["LEGACY_LOCAL"],
                         "experiments/out/foundry/audit-baseline.json")
        self.assertEqual(paths["REFOUNDATION_TRACKED"],
                         "config/baselines/foundry-audit-baseline.json")

    def test_the_gitignored_binding_is_declared_as_such(self):
        binding = self.contract.sides["LEGACY_LOCAL"].bindings["RATCHET_BASELINE_BYTES"]
        self.assertEqual(binding.availability, "LOCAL_ONLY_GITIGNORED")

    def test_the_cr_row_does_not_claim_the_interpretation_contract(self):
        """C7.5 names edition content AND an interpretation contract. Only one is here,
        and quietly conserving the row would misreport the other as done."""
        row = next(i for i in self.document["invariants"]
                   if i["invariant_id"] == "CR_EDITION_CONTENT")
        self.assertEqual(row["interpretation_contract_status"], "NOT_INCLUDED_HERE")


# ---------------------------------------------------------------------------
# The real repository
# ---------------------------------------------------------------------------


class TestMeasuredAgainstRepositoryBytes(ContractTestCase):
    """Every value below is re-derived here from repository bytes and config, then
    checked against a tracked record. Nothing is transcribed from a task packet."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.measured = {m.invariant_id: m for m in
                        cc.measure_side(cls.contract, "REFOUNDATION_TRACKED", REPO_ROOT)}
        cls.inputs = INPUTS_PATH.read_text()

    def test_every_active_invariant_was_measured(self):
        self.assertEqual(set(self.measured), set(ACTIVE_EXPECTED))

    def test_the_ratchet_bytes_agree_with_the_p0_3a_capture(self):
        recorded = scalars(block(self.inputs, "ignored_ratchet_baseline"))
        value = self.measured["RATCHET_BASELINE_BYTES"].value
        self.assertEqual(value["sha256"], recorded["source_sha256"])
        self.assertEqual(value["size_bytes"], int(recorded["source_size_bytes"]))
        self.assertEqual(value["sha256"], recorded["tracked_copy_sha256"])

    def test_the_ratchet_value_is_the_bytes_of_the_tracked_copy(self):
        """Re-derived independently of the harness, so the test is not the code."""
        target = PATHS.baselines / "foundry-audit-baseline.json"
        self.assertEqual(self.measured["RATCHET_BASELINE_BYTES"].value["sha256"],
                         sha256_of(target))
        self.assertEqual(self.measured["RATCHET_BASELINE_BYTES"].value["size_bytes"],
                         target.stat().st_size)

    def test_the_codebook_identity_is_the_selector_selection(self):
        selector = json.loads((PATHS.legacy_docs / "codebook-authority.json")
                              .read_text(encoding="utf-8"))
        value = self.measured["CODEBOOK_AUTHORITY_IDENTITY"].value
        self.assertEqual(value["selected_sha256"], selector["sha256"])
        self.assertEqual(value["selected_byte_size"], selector["byte_size"])
        self.assertEqual(value["selected_snapshot_id"], selector["snapshot_id"])

    def test_the_codebook_identity_agrees_with_the_p0_3a_capture(self):
        recorded = scalars(block(self.inputs, "selected_codebook_authority"))
        value = self.measured["CODEBOOK_AUTHORITY_IDENTITY"].value
        self.assertEqual(value["selected_sha256"], recorded["selected_sha256"])
        self.assertEqual(value["selected_byte_size"], int(recorded["selected_byte_size"]))

    def test_the_codebook_value_is_not_the_selector_file_bytes(self):
        """The distinction C7.1 turns on. Digesting the selector would pass on a
        reformat that changed the selection, and fail on whitespace that changed
        nothing."""
        measurement = self.measured["CODEBOOK_AUTHORITY_IDENTITY"]
        selector_bytes = sha256_of(PATHS.legacy_docs / "codebook-authority.json")
        self.assertEqual(measurement.evidence.source_sha256, selector_bytes)
        self.assertNotEqual(measurement.value["selected_sha256"], selector_bytes)

    def test_no_codebook_bytes_were_read_to_establish_its_identity(self):
        """5MB of authoritative content stays out of this, and out of R2: the identity
        is read from the tracked selector. The evidence names the selector, not the
        codebook."""
        evidence = self.measured["CODEBOOK_AUTHORITY_IDENTITY"].evidence
        self.assertEqual(evidence.source_path, "docs/codebook-authority.json")
        self.assertLess(evidence.source_size_bytes, 10_000)

    def test_the_cr_edition_is_the_vendored_file_bytes(self):
        target = PATHS.legacy_docs / "MTG_Comprehensive_Rules_2026-08-07_LLM.md"
        value = self.measured["CR_EDITION_CONTENT"].value
        self.assertEqual(value["sha256"], sha256_of(target))
        self.assertEqual(value["size_bytes"], target.stat().st_size)

    def test_the_cr_edition_identity_comes_from_content_and_agrees_with_its_own_prose(self):
        """The front-matter key is read mechanically; the document also states the
        edition in prose. If the two ever disagreed, the metadata block would be stale
        and the mechanical read would be quietly conserving the wrong edition."""
        value = self.measured["CR_EDITION_CONTENT"].value
        self.assertEqual(value["effective_date"], "2026-08-07")
        text = (PATHS.legacy_docs / "MTG_Comprehensive_Rules_2026-08-07_LLM.md"
                ).read_text(encoding="utf-8")[:4000]
        self.assertIn("These rules are effective as of August 7, 2026.", text)

    def test_the_edition_identity_does_not_come_from_the_filename(self):
        """A filename is a source path. Reading identity from it would put plumbing
        back into the truth — the file would 'drift' on a rename and stay put on an
        overwrite. Proved behaviourally: the same bytes under a different name must
        measure to the same value, field for field.
        """
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        (root / "docs").mkdir()
        original = PATHS.legacy_docs / "MTG_Comprehensive_Rules_2026-08-07_LLM.md"
        renamed = root / "docs" / "cr-under-any-other-name.md"
        shutil.copyfile(original, renamed)
        digest, _ = cc._read_source(root, "docs/cr-under-any-other-name.md",
                                    side_id="probe")
        invariant = self.contract.invariants["CR_EDITION_CONTENT"]
        value = cc._EXTRACTORS[invariant.extractor](digest, renamed,
                                                    invariant.extractor_args)
        self.assertEqual(value, self.measured["CR_EDITION_CONTENT"].value)


# ---------------------------------------------------------------------------
# Fixture roots
# ---------------------------------------------------------------------------


class FixtureTestCase(ContractTestCase):
    """Two synthetic roots, so the two sides can be given genuinely different paths.

    Real repository files are copied in rather than invented, so a fixture cannot
    drift into testing a shape the contract does not describe.
    """

    def make_root(self, *, ratchet_at: str, ratchet_bytes: bytes | None = None,
                  selector: dict | None = None) -> Path:
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        real_ratchet = PATHS.baselines / "foundry-audit-baseline.json"
        self.write(root, ratchet_at,
                   real_ratchet.read_bytes() if ratchet_bytes is None else ratchet_bytes)
        selector_doc = selector if selector is not None else json.loads(
            (PATHS.legacy_docs / "codebook-authority.json").read_text(encoding="utf-8"))
        self.write(root, "docs/codebook-authority.json",
                   json.dumps(selector_doc, indent=2).encode("utf-8"))
        self.write(root, "docs/MTG_Comprehensive_Rules_2026-08-07_LLM.md",
                   (PATHS.legacy_docs / "MTG_Comprehensive_Rules_2026-08-07_LLM.md"
                    ).read_bytes())
        return root

    @staticmethod
    def write(root: Path, relpath: str, data: bytes) -> Path:
        target = root.joinpath(*relpath.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return target


class TestPathIsEvidenceNotTruth(FixtureTestCase):
    def test_the_same_value_from_two_different_paths_is_conserved(self):
        legacy_root = self.make_root(ratchet_at="experiments/out/foundry/audit-baseline.json")
        new_root = self.make_root(ratchet_at="config/baselines/foundry-audit-baseline.json")

        left = cc.measure_side(self.contract, "LEGACY_LOCAL", legacy_root)
        right = cc.measure_side(self.contract, "REFOUNDATION_TRACKED", new_root)
        report = cc.compare(self.contract, left, right,
                            left_side="LEGACY_LOCAL", right_side="REFOUNDATION_TRACKED")

        self.assertTrue(report.conserved)
        self.assertEqual(report.drifted_ids, ())
        ratchet = next(v for v in report.verdicts
                       if v.invariant_id == "RATCHET_BASELINE_BYTES")
        self.assertEqual(ratchet.verdict, cc.CONSERVED)
        self.assertNotEqual(ratchet.left.evidence.source_path,
                            ratchet.right.evidence.source_path)

    def test_a_reformatted_selector_does_not_read_as_drift(self):
        """Evidence moves, truth does not. The selector's own bytes differ on both
        sides; the selection it declares does not."""
        selector = json.loads((PATHS.legacy_docs / "codebook-authority.json")
                              .read_text(encoding="utf-8"))
        legacy_root = self.make_root(
            ratchet_at="experiments/out/foundry/audit-baseline.json")
        new_root = self.make_root(
            ratchet_at="config/baselines/foundry-audit-baseline.json", selector=selector)
        # Reformat, changing bytes and key order but not one declared value.
        reformatted = json.dumps(dict(reversed(list(selector.items()))), indent=4)
        (new_root / "docs" / "codebook-authority.json").write_text(reformatted,
                                                                  encoding="utf-8")

        left = cc.measure_side(self.contract, "LEGACY_LOCAL", legacy_root)
        right = cc.measure_side(self.contract, "REFOUNDATION_TRACKED", new_root)
        codebook = {m.invariant_id: m for m in left}["CODEBOOK_AUTHORITY_IDENTITY"]
        other = {m.invariant_id: m for m in right}["CODEBOOK_AUTHORITY_IDENTITY"]
        self.assertNotEqual(codebook.evidence.source_sha256, other.evidence.source_sha256)

        report = cc.compare(self.contract, left, right)
        self.assertTrue(report.conserved)

    def test_a_byte_identical_selector_that_selects_something_else_is_drift(self):
        """The inverse control. Same document, same length, different selection."""
        selector = json.loads((PATHS.legacy_docs / "codebook-authority.json")
                              .read_text(encoding="utf-8"))
        drifted = dict(selector)
        drifted["sha256"] = "0" * 63 + "1"
        legacy_root = self.make_root(
            ratchet_at="experiments/out/foundry/audit-baseline.json")
        new_root = self.make_root(
            ratchet_at="config/baselines/foundry-audit-baseline.json", selector=drifted)

        report = cc.compare(self.contract,
                            cc.measure_side(self.contract, "LEGACY_LOCAL", legacy_root),
                            cc.measure_side(self.contract, "REFOUNDATION_TRACKED",
                                            new_root))
        self.assertFalse(report.conserved)
        self.assertEqual(report.drifted_ids, ("CODEBOOK_AUTHORITY_IDENTITY",))
        verdict = next(v for v in report.verdicts
                       if v.invariant_id == "CODEBOOK_AUTHORITY_IDENTITY")
        self.assertEqual(verdict.differing_fields, ("selected_sha256",))

    def test_one_changed_byte_in_the_ratchet_is_drift(self):
        real = (PATHS.baselines / "foundry-audit-baseline.json").read_bytes()
        legacy_root = self.make_root(
            ratchet_at="experiments/out/foundry/audit-baseline.json")
        new_root = self.make_root(
            ratchet_at="config/baselines/foundry-audit-baseline.json",
            ratchet_bytes=real + b" ")

        report = cc.compare(self.contract,
                            cc.measure_side(self.contract, "LEGACY_LOCAL", legacy_root),
                            cc.measure_side(self.contract, "REFOUNDATION_TRACKED",
                                            new_root))
        self.assertFalse(report.conserved)
        self.assertEqual(report.drifted_ids, ("RATCHET_BASELINE_BYTES",))
        verdict = next(v for v in report.verdicts
                       if v.invariant_id == "RATCHET_BASELINE_BYTES")
        self.assertEqual(verdict.differing_fields, ("sha256", "size_bytes"))


class TestDeferredIsNeverConserved(FixtureTestCase):
    def setUp(self):
        legacy = self.make_root(ratchet_at="experiments/out/foundry/audit-baseline.json")
        new = self.make_root(ratchet_at="config/baselines/foundry-audit-baseline.json")
        self.report = cc.compare(
            self.contract,
            cc.measure_side(self.contract, "LEGACY_LOCAL", legacy),
            cc.measure_side(self.contract, "REFOUNDATION_TRACKED", new))

    def test_every_deferred_item_appears_in_the_report_as_not_compared(self):
        """Absence is the failure mode. A row missing from a report reads exactly like
        a row that passed."""
        self.assertEqual(set(self.report.deferred_ids), set(DEFERRED_EXPECTED))

    def test_no_deferred_item_is_ever_marked_conserved(self):
        for verdict in self.report.verdicts:
            if verdict.invariant_id in DEFERRED_EXPECTED:
                with self.subTest(invariant=verdict.invariant_id):
                    self.assertEqual(verdict.verdict, cc.DEFERRED_NOT_COMPARED)
                    self.assertIsNone(verdict.left)
                    self.assertIsNone(verdict.right)

    def test_a_conserved_report_still_names_what_it_did_not_compare(self):
        self.assertTrue(self.report.conserved)
        self.assertEqual(set(self.report.compared_ids), set(ACTIVE_EXPECTED))
        rendered = self.report.as_dict()
        self.assertEqual(set(rendered["deferred_not_compared"]), set(DEFERRED_EXPECTED))
        for verdict in rendered["verdicts"]:
            if verdict["invariant_id"] in DEFERRED_EXPECTED:
                self.assertIn("deferred_reason", verdict)

    def test_a_report_that_compared_nothing_is_not_conserved(self):
        """`all([])` is True. A contract with every item deferred would otherwise
        announce conservation while having measured nothing — the vacuous case, and
        the one a reader is least likely to picture."""
        def defer_everything(doc):
            for row in doc["invariants"]:
                row["status"] = cc.DEFERRED_WITH_REASON
                row["comparison_kind"] = None
                row["extractor"] = None
                row["value_fields"] = []
                row.setdefault("deferred_reason", "nothing is measurable in this variant")
                row["deferred_reason"] = row["deferred_reason"] or "deferred"
                row.setdefault("what_a_comparator_would_require", ["a ratified comparator"])
                row["what_a_comparator_would_require"] = (
                    row["what_a_comparator_would_require"] or ["a ratified comparator"])
            for side in doc["sides"]:
                side["bindings"] = []
        contract = self.load_variant(defer_everything)
        report = cc.compare(contract, [], [])
        self.assertEqual(report.compared_ids, ())
        self.assertEqual(set(report.deferred_ids), set(cc.C7_INVENTORY))
        self.assertFalse(report.conserved)

    def test_measuring_a_deferred_invariant_is_refused(self):
        """The back door: hand `compare` a value for something with no ratified
        comparator and it must stop, not score it."""
        smuggled = cc.Measurement(
            invariant_id="ROUTING_RELATION", comparison_kind="EXACT_BYTES",
            value={"sha256": "a" * 64, "size_bytes": 1},
            evidence=cc.Evidence(side_id="x", source_path="a/b.json",
                                 source_sha256="b" * 64, source_size_bytes=1))
        with self.assertRaises(cc.ComparisonError):
            cc.compare(self.contract, [smuggled], [smuggled])

    def test_the_harness_never_measures_a_deferred_invariant(self):
        legacy = self.make_root(ratchet_at="experiments/out/foundry/audit-baseline.json")
        measured = {m.invariant_id for m in
                    cc.measure_side(self.contract, "LEGACY_LOCAL", legacy)}
        self.assertEqual(measured & set(DEFERRED_EXPECTED), set())


class TestDeterminism(FixtureTestCase):
    def test_two_runs_produce_a_byte_identical_report(self):
        legacy = self.make_root(ratchet_at="experiments/out/foundry/audit-baseline.json")
        new = self.make_root(ratchet_at="config/baselines/foundry-audit-baseline.json")

        def run() -> str:
            return cc.compare(
                cc.load_contract(CONTRACT_PATH),
                cc.measure_side(self.contract, "LEGACY_LOCAL", legacy),
                cc.measure_side(self.contract, "REFOUNDATION_TRACKED", new),
                left_side="LEGACY_LOCAL", right_side="REFOUNDATION_TRACKED").as_json()

        self.assertEqual(run(), run())

    def test_the_repository_measurement_is_stable_across_runs(self):
        first = cc.measure_side(self.contract, "REFOUNDATION_TRACKED", REPO_ROOT)
        second = cc.measure_side(self.contract, "REFOUNDATION_TRACKED", REPO_ROOT)
        self.assertEqual([m.as_dict() for m in first], [m.as_dict() for m in second])

    def test_the_verdict_order_is_the_c7_inventory_order(self):
        legacy = self.make_root(ratchet_at="experiments/out/foundry/audit-baseline.json")
        new = self.make_root(ratchet_at="config/baselines/foundry-audit-baseline.json")
        report = cc.compare(self.contract,
                            cc.measure_side(self.contract, "LEGACY_LOCAL", legacy),
                            cc.measure_side(self.contract, "REFOUNDATION_TRACKED", new))
        self.assertEqual(tuple(v.invariant_id for v in report.verdicts), cc.C7_INVENTORY)


class TestReadOnlyAndExplicit(FixtureTestCase):
    def test_measurement_writes_nothing_and_touches_nothing(self):
        root = self.make_root(ratchet_at="config/baselines/foundry-audit-baseline.json")

        def snapshot() -> dict[str, tuple[str, int]]:
            return {str(p.relative_to(root)): (sha256_of(p), p.stat().st_mtime_ns)
                    for p in sorted(root.rglob("*")) if p.is_file()}

        before = snapshot()
        cc.compare(self.contract,
                   cc.measure_side(self.contract, "REFOUNDATION_TRACKED", root),
                   cc.measure_side(self.contract, "REFOUNDATION_TRACKED", root))
        self.assertEqual(before, snapshot())

    def test_the_root_is_explicit_and_no_repository_is_discovered(self):
        """Measured from an unrelated working directory. A harness that rediscovered a
        root would answer about whichever tree it happened to be standing in."""
        root = self.make_root(ratchet_at="config/baselines/foundry-audit-baseline.json")
        elsewhere = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, elsewhere, ignore_errors=True)
        here = os.getcwd()
        try:
            os.chdir(elsewhere)
            measured = cc.measure_side(self.contract, "REFOUNDATION_TRACKED", root)
        finally:
            os.chdir(here)
        self.assertEqual({m.invariant_id for m in measured}, set(ACTIVE_EXPECTED))

    def test_only_declared_paths_are_opened_and_no_tree_is_walked(self):
        """A stray file next to a declared source must not enter the measurement —
        this is a contract, not a census."""
        root = self.make_root(ratchet_at="config/baselines/foundry-audit-baseline.json")
        self.write(root, "config/baselines/not-declared.json", b"{}")
        measured = cc.measure_side(self.contract, "REFOUNDATION_TRACKED", root)
        read = {m.evidence.source_path for m in measured}
        self.assertNotIn("config/baselines/not-declared.json", read)
        self.assertEqual(len(read), len(ACTIVE_EXPECTED))


# ---------------------------------------------------------------------------
# Fail-closed: one negative control per rule
# ---------------------------------------------------------------------------


class TestTheContractRefusesToLoad(ContractTestCase):
    def test_a_duplicate_invariant_id_is_refused(self):
        with self.assertRaises(cc.ContractError):
            self.load_variant(lambda d: d["invariants"].append(
                copy.deepcopy(d["invariants"][0])))

    def test_an_omitted_c7_item_is_refused(self):
        """Omission is forbidden: the inventory stops being one the moment it may be
        quietly shortened."""
        with self.assertRaises(cc.ContractError) as caught:
            self.load_variant(lambda d: d["invariants"].pop())
        self.assertIn("missing", str(caught.exception))

    def test_an_invariant_outside_the_c7_inventory_is_refused(self):
        def mutate(d):
            extra = copy.deepcopy(d["invariants"][0])
            extra["invariant_id"] = "SOMETHING_ELSE"
            d["invariants"].append(extra)
        with self.assertRaises(cc.ContractError):
            self.load_variant(mutate)

    def test_an_unknown_status_is_refused(self):
        def mutate(d):
            d["invariants"][0]["status"] = "PROBABLY_FINE"
        with self.assertRaises(cc.ContractError):
            self.load_variant(mutate)

    def test_a_deferred_item_carrying_a_comparison_kind_is_refused(self):
        def mutate(d):
            row = next(i for i in d["invariants"] if i["status"] == "DEFERRED_WITH_REASON")
            row["comparison_kind"] = "EXACT_BYTES"
        with self.assertRaises(cc.ContractError):
            self.load_variant(mutate)

    def test_a_deferred_item_without_a_reason_is_refused(self):
        def mutate(d):
            row = next(i for i in d["invariants"] if i["status"] == "DEFERRED_WITH_REASON")
            row["deferred_reason"] = "   "
        with self.assertRaises(cc.ContractError):
            self.load_variant(mutate)

    def test_a_deferred_item_that_names_no_missing_work_is_refused(self):
        def mutate(d):
            row = next(i for i in d["invariants"] if i["status"] == "DEFERRED_WITH_REASON")
            row["what_a_comparator_would_require"] = []
        with self.assertRaises(cc.ContractError):
            self.load_variant(mutate)

    def test_an_active_item_with_an_unknown_extractor_is_refused(self):
        def mutate(d):
            row = next(i for i in d["invariants"] if i["status"] == "ACTIVE_MECHANICAL")
            row["extractor"] = "guess_it"
        with self.assertRaises(cc.ContractError):
            self.load_variant(mutate)

    def test_an_active_item_with_an_unknown_comparison_kind_is_refused(self):
        def mutate(d):
            row = next(i for i in d["invariants"] if i["status"] == "ACTIVE_MECHANICAL")
            row["comparison_kind"] = "ROUGHLY_THE_SAME"
        with self.assertRaises(cc.ContractError):
            self.load_variant(mutate)

    def test_an_unknown_value_field_type_is_refused(self):
        def mutate(d):
            row = next(i for i in d["invariants"] if i["status"] == "ACTIVE_MECHANICAL")
            row["value_fields"][0]["type"] = "whatever"
        with self.assertRaises(cc.ContractError):
            self.load_variant(mutate)

    def test_binding_a_deferred_invariant_is_refused(self):
        def mutate(d):
            d["sides"][0]["bindings"].append(
                {"invariant_id": "ROUTING_RELATION", "source_path": "docs/x.json",
                 "availability": "TRACKED"})
        with self.assertRaises(cc.ContractError) as caught:
            self.load_variant(mutate)
        self.assertIn("DEFERRED_WITH_REASON", str(caught.exception))

    def test_a_side_missing_a_binding_for_an_active_invariant_is_refused(self):
        with self.assertRaises(cc.ContractError):
            self.load_variant(lambda d: d["sides"][0]["bindings"].pop())

    def test_a_duplicate_binding_is_refused(self):
        def mutate(d):
            d["sides"][0]["bindings"].append(
                copy.deepcopy(d["sides"][0]["bindings"][0]))
        with self.assertRaises(cc.ContractError):
            self.load_variant(mutate)

    def test_a_duplicate_side_id_is_refused(self):
        with self.assertRaises(cc.ContractError):
            self.load_variant(lambda d: d["sides"].append(copy.deepcopy(d["sides"][0])))

    def test_a_non_canonical_source_path_is_refused(self):
        def mutate(d):
            d["sides"][0]["bindings"][0]["source_path"] = "/etc/passwd"
        with self.assertRaises(PathDomainError):
            self.load_variant(mutate)

    def test_a_traversing_source_path_is_refused(self):
        def mutate(d):
            d["sides"][0]["bindings"][0]["source_path"] = "../elsewhere/x.json"
        with self.assertRaises(PathDomainError):
            self.load_variant(mutate)

    def test_a_contract_that_could_ratify_itself_is_refused(self):
        def mutate(d):
            d["authority"]["this_document_ratifies"] = "THE_C7_CONTRACT"
        with self.assertRaises(cc.ContractError):
            self.load_variant(mutate)

    def test_a_contract_with_the_wrong_schema_is_refused(self):
        with self.assertRaises(cc.ContractError):
            self.load_variant(lambda d: d.__setitem__("schema", "something/2"))


class TestMeasurementFailsClosed(FixtureTestCase):
    def test_an_absent_declared_source_stops_the_run(self):
        """Not skipped. A skipped invariant is an unmeasured one, and an unmeasured
        invariant that vanishes from the report looks conserved."""
        root = self.make_root(ratchet_at="config/baselines/foundry-audit-baseline.json")
        with self.assertRaises(cc.SourceUnavailable):
            cc.measure_side(self.contract, "LEGACY_LOCAL", root)

    def test_an_unknown_side_is_refused(self):
        root = self.make_root(ratchet_at="config/baselines/foundry-audit-baseline.json")
        with self.assertRaises(cc.ComparisonError):
            cc.measure_side(self.contract, "SOME_OTHER_SIDE", root)

    def test_a_malformed_digest_in_the_source_stops_the_run(self):
        selector = json.loads((PATHS.legacy_docs / "codebook-authority.json")
                              .read_text(encoding="utf-8"))
        selector["sha256"] = "not-a-digest"
        root = self.make_root(ratchet_at="config/baselines/foundry-audit-baseline.json",
                              selector=selector)
        with self.assertRaises(cc.MeasurementError):
            cc.measure_side(self.contract, "REFOUNDATION_TRACKED", root)

    def test_an_uppercase_digest_is_refused(self):
        """Two spellings of one digest would compare unequal and read as drift."""
        selector = json.loads((PATHS.legacy_docs / "codebook-authority.json")
                              .read_text(encoding="utf-8"))
        selector["sha256"] = selector["sha256"].upper()
        root = self.make_root(ratchet_at="config/baselines/foundry-audit-baseline.json",
                              selector=selector)
        with self.assertRaises(cc.MeasurementError):
            cc.measure_side(self.contract, "REFOUNDATION_TRACKED", root)

    def test_a_byte_size_that_is_not_a_number_stops_the_run(self):
        selector = json.loads((PATHS.legacy_docs / "codebook-authority.json")
                              .read_text(encoding="utf-8"))
        selector["byte_size"] = "5066147"
        root = self.make_root(ratchet_at="config/baselines/foundry-audit-baseline.json",
                              selector=selector)
        with self.assertRaises(cc.MeasurementError):
            cc.measure_side(self.contract, "REFOUNDATION_TRACKED", root)

    def test_a_boolean_is_not_a_byte_size(self):
        """`bool` is an `int` subclass, so True would otherwise measure as size 1."""
        selector = json.loads((PATHS.legacy_docs / "codebook-authority.json")
                              .read_text(encoding="utf-8"))
        selector["byte_size"] = True
        root = self.make_root(ratchet_at="config/baselines/foundry-audit-baseline.json",
                              selector=selector)
        with self.assertRaises(cc.MeasurementError):
            cc.measure_side(self.contract, "REFOUNDATION_TRACKED", root)

    def test_a_missing_key_in_the_source_stops_the_run(self):
        selector = json.loads((PATHS.legacy_docs / "codebook-authority.json")
                              .read_text(encoding="utf-8"))
        del selector["snapshot_id"]
        root = self.make_root(ratchet_at="config/baselines/foundry-audit-baseline.json",
                              selector=selector)
        with self.assertRaises(cc.MeasurementError):
            cc.measure_side(self.contract, "REFOUNDATION_TRACKED", root)

    def test_a_cr_file_with_no_declared_identity_stops_the_run(self):
        root = self.make_root(ratchet_at="config/baselines/foundry-audit-baseline.json")
        self.write(root, "docs/MTG_Comprehensive_Rules_2026-08-07_LLM.md",
                   b"# Rules\n\nno front matter here\n")
        with self.assertRaises(cc.MeasurementError):
            cc.measure_side(self.contract, "REFOUNDATION_TRACKED", root)

    def test_front_matter_without_the_contracted_key_stops_the_run(self):
        root = self.make_root(ratchet_at="config/baselines/foundry-audit-baseline.json")
        self.write(root, "docs/MTG_Comprehensive_Rules_2026-08-07_LLM.md",
                   b"---\ntitle: \"Rules\"\n---\n\nbody\n")
        with self.assertRaises(cc.MeasurementError):
            cc.measure_side(self.contract, "REFOUNDATION_TRACKED", root)

    def test_a_value_missing_a_contracted_field_is_refused(self):
        def mutate(d):
            row = next(i for i in d["invariants"]
                       if i["invariant_id"] == "CODEBOOK_AUTHORITY_IDENTITY")
            row["value_fields"].append({"name": "not_produced", "type": "string"})
        contract = self.load_variant(mutate)
        root = self.make_root(ratchet_at="config/baselines/foundry-audit-baseline.json")
        with self.assertRaises(cc.MeasurementError) as caught:
            cc.measure_side(contract, "REFOUNDATION_TRACKED", root)
        self.assertIn("missing", str(caught.exception))

    def test_a_value_carrying_an_uncontracted_field_is_refused(self):
        """As hard as a missing one: an extra field reads as drift the moment one side
        stops emitting it, and nothing would say why."""
        def mutate(d):
            row = next(i for i in d["invariants"]
                       if i["invariant_id"] == "CODEBOOK_AUTHORITY_IDENTITY")
            row["extractor_args"]["fields"]["bucket"] = "bucket"
        contract = self.load_variant(mutate)
        root = self.make_root(ratchet_at="config/baselines/foundry-audit-baseline.json")
        with self.assertRaises(cc.MeasurementError) as caught:
            cc.measure_side(contract, "REFOUNDATION_TRACKED", root)
        self.assertIn("unexpected", str(caught.exception))


class TestComparisonFailsClosed(FixtureTestCase):
    def setUp(self):
        self.root = self.make_root(
            ratchet_at="config/baselines/foundry-audit-baseline.json")
        self.measured = list(cc.measure_side(self.contract, "REFOUNDATION_TRACKED",
                                             self.root))

    def test_a_duplicate_measurement_id_stops_the_comparison(self):
        with self.assertRaises(cc.ComparisonError) as caught:
            cc.compare(self.contract, self.measured + [self.measured[0]], self.measured)
        self.assertIn("duplicate", str(caught.exception))

    def test_a_missing_active_invariant_stops_the_comparison(self):
        with self.assertRaises(cc.ComparisonError) as caught:
            cc.compare(self.contract, self.measured[:-1], self.measured)
        self.assertIn("not measured", str(caught.exception))

    def test_a_missing_invariant_on_the_right_side_stops_it_too(self):
        """Both arms, because a one-sided check passes whenever the loss is on the
        side nobody looked at."""
        with self.assertRaises(cc.ComparisonError):
            cc.compare(self.contract, self.measured, self.measured[:-1])

    def test_a_comparison_kind_mismatch_stops_the_comparison(self):
        original = self.measured[0]
        other = next(k for k in cc.COMPARISON_KINDS if k != original.comparison_kind)
        wrong = dataclasses.replace(original, comparison_kind=other)
        with self.assertRaises(cc.ComparisonError) as caught:
            cc.compare(self.contract, [wrong] + self.measured[1:], self.measured)
        message = str(caught.exception)
        self.assertIn(other, message)
        self.assertIn(original.comparison_kind, message)
        # Aimed at the PRIMARY guard. `compare` carries a second, redundant kind check
        # between the two sides, and asserting only "some ComparisonError" would let
        # this test pass on the backstop while the check against the contract was gone.
        self.assertIn("the contract says", message)

    def test_an_unknown_invariant_id_stops_the_comparison(self):
        stray = dataclasses.replace(self.measured[0], invariant_id="INVENTED")
        with self.assertRaises(cc.ComparisonError):
            cc.compare(self.contract, [stray] + self.measured[1:], self.measured)

    def test_a_measurement_with_a_malformed_value_stops_the_comparison(self):
        """Validated again at comparison time: a Measurement can be constructed by a
        caller that never went through `measure_side`."""
        broken = dataclasses.replace(self.measured[0],
                                     value=dict(self.measured[0].value,
                                                **{next(iter(self.measured[0].value)):
                                                   "not-a-digest"}))
        with self.assertRaises(cc.MeasurementError):
            cc.compare(self.contract, [broken] + self.measured[1:], self.measured)


if __name__ == "__main__":
    unittest.main()
