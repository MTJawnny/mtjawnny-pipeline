"""Path E milestone 2 — the STABLE PRODUCT PROPERTIES of the evidence layer.

These test what the index and the retrieval must always be true of, not the
history of how they got here. Each class below names one property the milestone
was authorized to guarantee:

* the full population is retained and eligibility only PARTITIONS it;
* every face and every text survives;
* assertion / evidence / locality data is preserved exactly, not flattened;
* `UNASSIGNED` is explicit and means one thing;
* only ACTIVE axes are indexed;
* index bytes do not depend on the working directory or the root's absolute path;
* duplicate oracle_id and shared-name behaviour is conserved;
* candidate generation is POSITIVE ONLY, and a missing membership cannot lower
  another candidate's rank;
* an ambiguous name halts instead of collapsing identities;
* an unassigned anchor fabricates nothing;
* a query works from the artifact alone, with no repository;
* the frozen panel fixture is source-pinned;
* the evaluation keeps candidate recall and top-k presentation apart.

The milestone-1 fixture builders are REUSED rather than duplicated: a second
repository-shaped fixture would be a second place for the layout to drift, and
the accepted suite already proves that one builds a root the runtime accepts.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT, SRC
from tests.refoundation.test_readonly_runtime import (
    DFC_CARD, ID_A, ID_B, ID_C, ILLEGAL_CARD, LEGAL_CARD, RuntimeFixtureCase,
    assertion, axis, build_fixture_root, fixture_codebook, lock_for)

from mtj_foundry import (evaluation, evidence_cli, evidence_index, retrieval,
                         runtime)
from mtj_foundry.paths import ProjectPaths

CLEAN_ENV = {"PATH": "/usr/bin:/bin"}   # deliberately no PYTHONPATH
PANEL_PATH = REPO_ROOT / "refoundation" / "path-e" / "m2-evaluation.json"
FROZEN_SOURCE = REPO_ROOT / "docs" / "WIRE-PREDICTIONS-2026-08-09.md"
FROZEN_RESULT = REPO_ROOT / "docs" / "WIRE-RESULT-2026-08-09.md"


# The milestone-1 fixture pairs a codebook holding ID_C with a corpus that does
# NOT contain it -- deliberately, to exercise the absent-member accounting. That
# is the wrong shape for a RETRIEVAL test, where a candidate has to be a real
# index row, so the retrieval classes below use an ALIGNED pair instead: every
# member id is also a corpus record, and nothing is absent.
CARD_C = dict(LEGAL_CARD, oracle_id=ID_C, name="Fixture Third")
ALIGNED_CORPUS = [LEGAL_CARD, ILLEGAL_CARD, CARD_C]


class IndexFixtureCase(RuntimeFixtureCase):
    """A fixture root plus the index built over it."""

    def index(self, root=None, **kwargs) -> dict:
        root = root if root is not None else self.build(**kwargs)
        return evidence_index.generate(root, lock_path=str(lock_for(root)))

    def aligned(self, axes: dict, corpus_records=None) -> dict:
        """An index whose codebook and corpus name the same ids.

        `axes` is `{axis_id: (status, [oracle_id, ...])}`, which keeps each test's
        membership shape readable on one line instead of hidden inside a nested
        literal.
        """
        document = {"schema": fixture_codebook()["schema"],
                    "axes": {axis_id: axis(status, *ids)
                             for axis_id, (status, ids) in axes.items()}}
        return self.index(codebook_document=document,
                          corpus_records=corpus_records or ALIGNED_CORPUS)

    def row(self, index: dict, oracle_id: str) -> dict:
        return next(r for r in index["cards"] if r["oracle_id"] == oracle_id)


# ===========================================================================
# 1. FULL POPULATION, AND ELIGIBILITY ONLY PARTITIONS IT
# ===========================================================================

class TestTheIndexHoldsTheWholePopulation(IndexFixtureCase):

    def test_every_corpus_card_is_a_row_including_the_ineligible_one(self):
        index = self.index()
        ids = [r["oracle_id"] for r in index["cards"]]
        self.assertEqual(len(ids), 3)
        self.assertIn(ILLEGAL_CARD["oracle_id"], ids)

    def test_eligibility_is_a_field_on_the_row_not_a_filter_over_rows(self):
        index = self.index()
        self.assertTrue(self.row(index, ID_A)["gate0_eligible"])
        self.assertFalse(self.row(index, ID_B)["gate0_eligible"])
        self.assertEqual(
            index["conservation"]["eligibility"]["eligible_unique_ids"]
            + index["conservation"]["eligibility"]["ineligible_unique_ids"],
            len(index["cards"]))

    def test_an_uncovered_card_is_still_a_row_with_its_text(self):
        """The whole milestone rests on this: 31,958 of 38,233 real corpus ids are
        uncovered, and an index that dropped them would be an index of the review
        backlog rather than of the corpus."""
        index = self.index()
        row = self.row(index, DFC_CARD["oracle_id"])
        self.assertEqual(row["evidence_state"],
                         evidence_index.EVIDENCE_STATE_UNASSIGNED)
        self.assertEqual([f["oracle_text"] for f in row["faces"]],
                         ["Front text.", "Back text."])

    def test_rows_are_ordered_by_oracle_id_and_by_nothing_else(self):
        index = self.index()
        ids = [r["oracle_id"] for r in index["cards"]]
        self.assertEqual(ids, sorted(ids))

    def test_NEGATIVE_CONTROL_a_dropped_row_fails_conservation(self):
        """A guard never shown to fail is not known to be a guard."""
        root = self.build()
        inputs = runtime.resolve_inputs(root, lock_path=str(lock_for(root)))
        document, stats, cb_id, selector = runtime.load_verified_codebook(inputs)
        cards, corpus_id, content = runtime.load_verified_corpus(inputs)
        report = runtime.build_report(document, stats, cb_id, selector, cards,
                                      corpus_id, content, inputs.corpus, inputs)
        cards.pop(ID_B)   # exactly the filtering this milestone forbids
        with self.assertRaises(evidence_index.EvidenceIndexConservationError) as cm:
            evidence_index.build_index(document, cards, report)
        self.assertIn("unique_oracle_ids", str(cm.exception))


# ===========================================================================
# 2. ALL FACES AND ALL TEXT SURVIVE
# ===========================================================================

class TestFaceAndTextPreservation(IndexFixtureCase):

    def test_faces_come_from_the_capability_not_the_raw_field(self):
        """A split/adventure layout has `card_faces` AND a root-level text, so the
        raw field describes a structure the Foundry's readers do not see."""
        split = dict(LEGAL_CARD, oracle_id=ID_C, name="Front // Back",
                     oracle_text="Root level text.",
                     card_faces=[{"name": "Front", "oracle_text": "F."},
                                 {"name": "Back", "oracle_text": "B."}])
        index = self.index(corpus_records=[split])
        row = self.row(index, ID_C)
        self.assertEqual(len(row["faces"]), 2)
        self.assertEqual([f["oracle_text"] for f in row["faces"]], ["F.", "B."])

    def test_every_declared_face_field_is_carried(self):
        index = self.index()
        for face in self.row(index, ID_A)["faces"]:
            self.assertEqual(set(face), {"name", "oracle_text", "mana_cost",
                                         "type_line", "power", "toughness"})

    def test_the_face_count_reconciles_with_the_accepted_report(self):
        index = self.index()
        self.assertEqual(
            sum(len(r["faces"]) for r in index["cards"]),
            index["conservation"]["corpus_population"]["faces_total"])


# ===========================================================================
# 3. ASSERTION / EVIDENCE / LOCALITY PRESERVED EXACTLY
# ===========================================================================

class TestEvidenceIsPreservedVerbatim(IndexFixtureCase):

    def test_the_member_object_is_carried_whole_not_projected(self):
        """A projection loses whatever this milestone did not think to name."""
        root = self.build()
        document = json.loads(
            ProjectPaths.for_root(root).legacy_codebook_json.read_text("utf-8"))
        index = self.index(root)
        row = self.row(index, ID_A)
        for membership in row["memberships"]:
            source = next(m for m in document["axes"][membership["axis_id"]]["members"]
                          if m["oracle_id"] == ID_A)
            self.assertEqual(membership["member"], source)

    def test_every_named_evidence_field_survives(self):
        index = self.index()
        stored = self.row(index, ID_A)["memberships"][0]["member"]["assertions"][0]
        for field in ("class", "source_ref", "quote", "corpus_ref",
                      "evidence_status", "locality"):
            with self.subTest(field=field):
                self.assertIn(field, stored)
        self.assertEqual(stored["locality"], [0, 0])

    def test_a_member_level_tier_is_carried_too(self):
        """The copy does not enumerate keys, so a field this milestone never names
        -- the A1 member-level `tier`, present IFF every assertion is llm-class --
        survives without this module being taught about it.

        The member is built to pass the REAL lint: canonical member key order,
        and an llm assertion carrying the lanes lint requires of one. A fixture
        lint would reject makes the result ambiguous.
        """
        document = fixture_codebook()
        document["axes"]["rule:alpha"]["members"] = [{
            "oracle_id": ID_A,
            "tier": "provisional",
            "assertions": [{
                "class": "llm", "source_ref": "run1",
                "original_lane": "codebook", "effective_lane": "codebook",
                "quote": "whenever this creature enters, draw a card",
                "corpus_ref": "2026-07-04", "evidence_status": "quoted",
                "locality": [0, 0],
            }],
        }]
        index = self.index(codebook_document=document)
        member = self.row(index, ID_A)["memberships"][0]["member"]
        self.assertEqual(member["tier"], "provisional")
        self.assertEqual(list(member), ["oracle_id", "tier", "assertions"])

    def test_the_evidence_field_census_reconciles_with_the_report(self):
        """Reconciled on an ALIGNED pair, so the two numbers are comparable at all.

        The report's census counts every assertion on every active membership,
        INCLUDING members the corpus does not contain; the index can only hold
        the ones whose card is a row. On the milestone-1 fixture those differ by
        exactly ID_C, and equating them there would have been a probe defect
        rather than a finding.
        """
        index = self.aligned({"rule:alpha": ("active", [ID_A, ID_C]),
                              "rule:beta": ("active", [ID_A])})
        counted = sum(len(m["member"]["assertions"])
                      for r in index["cards"] for m in r["memberships"])
        census = index["conservation"][
            "codebook_evidence_fields_present_on_active_axes"]
        self.assertEqual(
            index["conservation"]["coverage"][
                "active_member_ids_absent_from_corpus"], 0)
        self.assertEqual(counted, census["assertions"])
        self.assertEqual(census["with_quote"], counted)
        self.assertEqual(census["with_locality"], counted)


# ===========================================================================
# 4. UNASSIGNED IS EXPLICIT AND MEANS ONE THING
# ===========================================================================

class TestUnassignedSemantics(IndexFixtureCase):

    def test_a_card_with_no_active_membership_is_named_unassigned(self):
        index = self.index()
        self.assertEqual(self.row(index, ID_B)["evidence_state"],
                         evidence_index.EVIDENCE_STATE_UNASSIGNED)
        self.assertEqual(self.row(index, ID_B)["memberships"], [])

    def test_the_artifact_states_what_unassigned_does_not_mean(self):
        """A static consumer must not have to find a Python module to learn that
        absence of evidence is not evidence of dissimilarity."""
        index = self.index()
        forbidden = index["evidence_state_semantics"]["UNASSIGNED_IS_NOT"]
        text = " ".join(forbidden).lower()
        for word in ("dissimilar", "rejected", "negative", "semantically empty"):
            with self.subTest(word=word):
                self.assertIn(word, text)

    def test_the_two_states_are_the_only_two_and_they_partition_the_rows(self):
        index = self.index()
        states = {r["evidence_state"] for r in index["cards"]}
        self.assertTrue(states <= {evidence_index.EVIDENCE_STATE_ASSIGNED,
                                   evidence_index.EVIDENCE_STATE_UNASSIGNED})
        self.assertEqual(
            sum(1 for r in index["cards"]
                if r["evidence_state"] == evidence_index.EVIDENCE_STATE_ASSIGNED),
            index["conservation"]["coverage"]["corpus_ids_covered"])


# ===========================================================================
# 5. ONLY ACTIVE AXES ARE INDEXED
# ===========================================================================

class TestActiveOnlyMembership(IndexFixtureCase):

    def test_a_killed_axis_contributes_no_membership_and_no_catalogue_entry(self):
        index = self.index()
        self.assertNotIn("rule:gamma", index["axes"])
        self.assertEqual(self.row(index, ID_B)["memberships"], [])

    def test_a_member_only_on_a_nonactive_axis_reads_unassigned(self):
        """`ID_B` is a member of the killed axis and of nothing else, so the
        correct answer is UNASSIGNED — history is not active evidence."""
        index = self.index()
        self.assertEqual(self.row(index, ID_B)["evidence_state"],
                         evidence_index.EVIDENCE_STATE_UNASSIGNED)

    def test_NEGATIVE_CONTROL_flipping_the_axis_to_active_changes_the_answer(self):
        """Otherwise the test above could pass because nothing was ever indexed."""
        document = fixture_codebook()
        document["axes"]["rule:gamma"]["status"] = "active"
        index = self.index(codebook_document=document)
        self.assertIn("rule:gamma", index["axes"])
        self.assertEqual(self.row(index, ID_B)["evidence_state"],
                         evidence_index.EVIDENCE_STATE_ASSIGNED)

    def test_the_axis_catalogue_cardinality_matches_the_codebook(self):
        index = self.index()
        self.assertEqual(index["axes"]["rule:alpha"]["active_member_count"], 2)
        self.assertEqual(index["axes"]["rule:beta"]["active_member_count"], 1)


# ===========================================================================
# 6. DETERMINISTIC BYTES, INDEPENDENT OF CWD AND OF THE ROOT'S PATH
# ===========================================================================

class TestDeterministicIndexBytes(IndexFixtureCase):

    def test_two_runs_over_one_root_are_byte_identical(self):
        root = self.build()
        first = evidence_index.render_index(self.index(root))
        second = evidence_index.render_index(self.index(root))
        self.assertEqual(first, second)

    def test_the_same_inputs_under_a_DIFFERENT_absolute_root_render_the_same(self):
        """A root path in the bytes would make two checkouts incomparable, which
        is the property a later static consumer depends on."""
        first_root = self.build(name="rootX")
        second_root = self.tmp / "a-completely-different-name"
        shutil.copytree(first_root, second_root)
        self.assertEqual(
            evidence_index.render_index(self.index(first_root)),
            evidence_index.render_index(self.index(second_root)))

    def test_the_payload_carries_no_absolute_machine_path(self):
        root = self.build()
        text = evidence_index.render_index(self.index(root))
        self.assertNotIn(str(root), text)
        self.assertNotIn(str(self.tmp), text)

    def test_running_from_an_unrelated_cwd_renders_the_same_bytes(self):
        root = self.build()
        expected = evidence_index.render_index(self.index(root))
        outside = self.tmp / "unrelated"
        outside.mkdir()
        original = os.getcwd()
        os.chdir(outside)
        try:
            self.assertEqual(evidence_index.render_index(self.index(root)), expected)
        finally:
            os.chdir(original)


# ===========================================================================
# 7. DUPLICATE ORACLE_ID AND SHARED-NAME BEHAVIOUR IS CONSERVED
# ===========================================================================

class TestCorpusIdentitySemanticsSurvive(IndexFixtureCase):

    def test_a_duplicate_oracle_id_collapses_last_write_wins(self):
        first = dict(LEGAL_CARD, name="First Write")
        second = dict(LEGAL_CARD, name="Second Write")
        index = self.index(corpus_records=[first, second])
        self.assertEqual(len(index["cards"]), 1)
        self.assertEqual(index["cards"][0]["name"], "Second Write")

    def test_a_shared_normalized_name_keeps_EVERY_id(self):
        twin = dict(LEGAL_CARD, oracle_id=ID_C, name="fixture legal")
        index = self.index(corpus_records=[LEGAL_CARD, twin])
        self.assertEqual(sorted(index["name_index"]["fixture legal"]),
                         sorted([ID_A, ID_C]))

    def test_the_stored_name_index_is_the_capability_s_own(self):
        """Rebuilding it here instead of storing the capability's output would make
        name semantics this module's rather than the corpus layer's."""
        root = self.build()
        index = self.index(root)
        from mtj_foundry import corpus as corpus_capability
        cards = corpus_capability.load_cards(
            ProjectPaths.for_root(root).legacy_oracle_cards)
        self.assertEqual(index["name_index"],
                         corpus_capability.build_name_index(cards))


# ===========================================================================
# 8. RETRIEVAL IS POSITIVE-EVIDENCE ONLY
# ===========================================================================

class TestPositiveEvidenceOnly(IndexFixtureCase):

    def test_a_candidate_must_share_an_active_axis(self):
        index = self.aligned({"rule:alpha": ("active", [ID_A, ID_C]),
                              "rule:gamma": ("killed", [ID_A, ID_B])})
        result = retrieval.query(index, oracle_id=ID_A)
        self.assertEqual([c["oracle_id"] for c in result["candidates"]], [ID_C])

    def test_a_card_sharing_nothing_is_ABSENT_not_ranked_low(self):
        index = self.aligned({"rule:alpha": ("active", [ID_A, ID_C]),
                              "rule:beta": ("active", [ID_B])})
        result = retrieval.query(index, oracle_id=ID_A)
        self.assertNotIn(ID_B, [c["oracle_id"] for c in result["candidates"]])

    def test_PROOF_a_missing_membership_cannot_lower_another_candidates_rank(self):
        """The structural form, not an observation: the ordering key is computed
        from the SHARED axes and the candidate's own id, so no value describing a
        membership a candidate lacks is even in scope.

        Demonstrated by construction — give a candidate an extra membership on an
        axis the anchor is NOT on, and its key must not move — and then by the
        stronger negative control, that REMOVING that same extra membership also
        does not move it. A penalty term would have to change one of the two.
        """
        base = {"rule:alpha": ("active", [ID_A, ID_C])}
        with_extra = self.aligned(dict(base, **{"rule:delta": ("active", [ID_C, ID_B])}))
        without_extra = self.aligned(base)

        def key_of(index):
            result = retrieval.query(index, oracle_id=ID_A)
            candidate = next(c for c in result["candidates"]
                             if c["oracle_id"] == ID_C)
            return (candidate["rank"], candidate["features"]["shared_axis_ids"],
                    candidate["features"]["shared_axis_cardinalities"])

        self.assertEqual(key_of(with_extra), key_of(without_extra))

    def test_the_ordering_key_reads_only_shared_features_and_the_id(self):
        """Direct assertion on the key function itself: mutating a candidate's
        NON-shared facts leaves the key byte-identical."""
        candidate = {"oracle_id": ID_C, "name": "x",
                     "features": {"shared_axis_ids": ["rule:alpha"],
                                  "shared_axis_count": 1,
                                  "shared_axis_cardinalities": [2],
                                  "candidate_total_active_memberships": 1}}
        before = retrieval._sort_key(candidate)
        candidate["features"]["candidate_total_active_memberships"] = 99
        candidate["name"] = "a totally different name"
        self.assertEqual(retrieval._sort_key(candidate), before)

    def test_more_shared_axes_outrank_fewer_and_the_result_says_why(self):
        index = self.aligned({"rule:alpha": ("active", [ID_A, ID_C]),
                              "rule:beta": ("active", [ID_A, ID_C]),
                              "rule:delta": ("active", [ID_A, ID_B])})
        result = retrieval.query(index, oracle_id=ID_A)
        ranked = [(c["oracle_id"], c["features"]["shared_axis_count"])
                  for c in result["candidates"]]
        self.assertEqual(ranked, [(ID_C, 2), (ID_B, 1)])

    def test_every_candidate_exposes_its_raw_features_and_its_evidence(self):
        index = self.aligned({"rule:alpha": ("active", [ID_A, ID_C])})
        candidate = retrieval.query(index, oracle_id=ID_A)["candidates"][0]
        self.assertEqual(candidate["features"]["shared_axis_ids"], ["rule:alpha"])
        self.assertEqual(candidate["features"]["shared_axis_count"], 1)
        self.assertEqual(candidate["features"]["shared_axis_cardinalities"], [2])
        evidence = candidate["evidence"][0]
        self.assertEqual(evidence["anchor_member"]["oracle_id"], ID_A)
        self.assertEqual(evidence["candidate_member"]["oracle_id"], ID_C)
        self.assertIn("quote", evidence["candidate_member"]["assertions"][0])

    def test_a_tie_block_is_reported_as_a_tie_block(self):
        """The 2026-08-09 result's clearest product finding was a displayed top-10
        that was an alphabetical slice of a 44-row tie and read as a ranking."""
        index = self.aligned({"rule:alpha": ("active", [ID_A, ID_B, ID_C])})
        result = retrieval.query(index, oracle_id=ID_A)
        self.assertEqual(result["candidate_count"], 2)
        for candidate in result["candidates"]:
            self.assertEqual(candidate["tie_block_size"], 2)
            self.assertEqual(candidate["tie_block_first_rank"], 1)

    def test_the_declared_ordering_travels_with_every_result(self):
        result = retrieval.query(
            self.aligned({"rule:alpha": ("active", [ID_A, ID_C])}), oracle_id=ID_A)
        self.assertEqual(result["ordering"]["constants"].split(".")[0], "NONE")
        self.assertIn("declared_before", result["ordering"])


# ===========================================================================
# 9. UNASSIGNED ANCHORS AND AMBIGUOUS NAMES
# ===========================================================================

class TestAnchorResolutionRefusals(IndexFixtureCase):

    def test_an_unassigned_anchor_returns_an_explicit_state_and_no_candidates(self):
        index = self.aligned({"rule:alpha": ("active", [ID_A, ID_C])})
        result = retrieval.query(index, oracle_id=ID_B)
        self.assertEqual(result["result_state"], retrieval.RESULT_STATE_UNASSIGNED)
        self.assertEqual(result["candidates"], [])
        self.assertIn("ABSENCE OF EVIDENCE", result["result_state_means"])

    def test_an_unassigned_anchor_makes_no_claim_that_none_exist(self):
        result = retrieval.query(
            self.aligned({"rule:alpha": ("active", [ID_A, ID_C])}), oracle_id=ID_B)
        self.assertIn("not a finding that the card has no similar cards",
                      result["result_state_means"])

    def test_an_ambiguous_name_HALTS_and_names_every_id(self):
        twin = dict(LEGAL_CARD, oracle_id=ID_C, name="Fixture Legal")
        index = self.index(corpus_records=[LEGAL_CARD, twin])
        with self.assertRaises(retrieval.AmbiguousNameError) as cm:
            retrieval.query(index, name="Fixture Legal")
        self.assertEqual(sorted(cm.exception.oracle_ids), sorted([ID_A, ID_C]))

    def test_an_unknown_anchor_is_NOT_the_same_as_an_unassigned_one(self):
        index = self.aligned({"rule:alpha": ("active", [ID_A, ID_C])})
        with self.assertRaises(retrieval.UnknownAnchorError) as cm:
            retrieval.query(index, name="No Such Card")
        self.assertIn("NOT the same as a card with no active evidence",
                      str(cm.exception))

    def test_naming_both_or_neither_anchor_form_refuses(self):
        index = self.aligned({"rule:alpha": ("active", [ID_A, ID_C])})
        for kwargs in ({}, {"oracle_id": ID_A, "name": "Fixture Legal"}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(retrieval.RetrievalError):
                    retrieval.query(index, **kwargs)


# ===========================================================================
# 10. THE ARTIFACT IS THE WHOLE INPUT
# ===========================================================================

class TestQueryNeedsOnlyTheArtifact(IndexFixtureCase):

    def test_a_query_runs_against_a_copy_with_no_repository_in_reach(self):
        """The milestone-3 property, demonstrated rather than asserted: the
        artifact is copied outside every input path and queried there."""
        root = self.build(codebook_document={
            "schema": fixture_codebook()["schema"],
            "axes": {"rule:alpha": axis("active", ID_A, ID_C)}},
            corpus_records=ALIGNED_CORPUS)
        artifact = self.tmp / "elsewhere" / "index.json"
        artifact.parent.mkdir()
        artifact.write_text(
            evidence_index.render_index(
                evidence_index.generate(root, lock_path=str(lock_for(root)))),
            encoding="utf-8")
        shutil.rmtree(root)   # the repository is GONE
        result = retrieval.query(retrieval.load_index(artifact), oracle_id=ID_A)
        self.assertEqual([c["oracle_id"] for c in result["candidates"]], [ID_C])

    def test_a_non_index_document_is_refused_by_schema(self):
        path = self.tmp / "not-an-index.json"
        path.write_text('{"schema": "something-else/1"}', encoding="utf-8")
        with self.assertRaises(retrieval.IndexSchemaError):
            retrieval.load_index(path)

    def test_an_unreadable_artifact_is_a_typed_access_failure(self):
        with self.assertRaises(retrieval.IndexAccessError):
            retrieval.load_index(self.tmp / "does-not-exist.json")

    def test_truncation_never_understates_the_pool(self):
        index = self.aligned({"rule:alpha": ("active", [ID_A, ID_B, ID_C])})
        result = retrieval.query(index, oracle_id=ID_A, top=1)
        self.assertEqual(result["candidate_count"], 2)
        self.assertEqual(len(result["candidates"]), 1)
        self.assertIn("truncated", result["truncation"])


# ===========================================================================
# 11. THE INSTALLED COMMAND SURFACE
# ===========================================================================

class TestTheShippedEvidenceCommand(IndexFixtureCase):

    def run_cli(self, argv):
        import io
        import contextlib
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = evidence_cli.main(argv)
        return status, out.getvalue(), err.getvalue()

    def test_index_writes_the_artifact_to_stdout_and_exits_zero(self):
        root = self.build()
        status, out, err = self.run_cli(
            ["index", "--root", str(root), "--input-lock", str(lock_for(root))])
        self.assertEqual(status, 0)
        self.assertEqual(err, "")
        self.assertEqual(json.loads(out)["schema"], evidence_index.INDEX_SCHEMA)

    def test_an_expected_input_failure_is_STOP_exit_one_and_EMPTY_stdout(self):
        root = self.build()
        status, out, err = self.run_cli(
            ["index", "--root", str(root), "--input-lock", str(lock_for(root)),
             "--corpus-sha256", "0" * 64])
        self.assertEqual(status, 1)
        self.assertEqual(out, "")
        self.assertTrue(err.startswith("STOP — "), err)

    def test_an_ambiguous_query_name_is_STOP_not_a_guess(self):
        twin = dict(LEGAL_CARD, oracle_id=ID_C, name="Fixture Legal")
        root = self.build(corpus_records=[LEGAL_CARD, twin])
        artifact = self.tmp / "index.json"
        artifact.write_text(evidence_index.render_index(
            evidence_index.generate(root, lock_path=str(lock_for(root)))),
            encoding="utf-8")
        status, out, err = self.run_cli(
            ["query", "--index", str(artifact), "--name", "Fixture Legal"])
        self.assertEqual(status, 1)
        self.assertEqual(out, "")
        self.assertIn("refusing to pick one", err)

    def test_the_command_catches_no_broad_exception_class(self):
        """Asserted over the PARSED source, never over its text.

        A string search reads the module's own PROSE about what it does not
        catch, and a docstring saying "there is no broad catch here" would fail a
        test looking for that phrase -- the "a document is an API" trap aimed at a
        test. The AST sees handlers and nothing else, which is also how the
        accepted milestone-1 suite asserts the same property.
        """
        import ast

        for name in ("evidence_cli.py", "evidence_index.py", "retrieval.py",
                     "evaluation.py"):
            tree = ast.parse((SRC / "mtj_foundry" / name).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.ExceptHandler):
                    continue
                named = []
                if isinstance(node.type, ast.Name):
                    named = [node.type.id]
                elif isinstance(node.type, ast.Tuple):
                    named = [e.id for e in node.type.elts if isinstance(e, ast.Name)]
                with self.subTest(module=name, handler=named):
                    self.assertIsNotNone(node.type, "a bare except clause")
                    for banned in ("Exception", "BaseException"):
                        self.assertNotIn(banned, named)

    def test_bad_usage_is_argparse_status_two(self):
        """argparse's own status, untouched. Its usage message is redirected so a
        deliberate bad invocation does not print noise into a passing suite."""
        import contextlib
        import io

        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                evidence_cli.build_parser().parse_args(["index"])   # no --root
        self.assertEqual(cm.exception.code, 2)

    def test_the_new_modules_import_nothing_from_the_legacy_tree(self):
        for name in ("evidence_index.py", "retrieval.py", "evaluation.py",
                     "evidence_cli.py"):
            text = (SRC / "mtj_foundry" / name).read_text(encoding="utf-8")
            with self.subTest(module=name):
                for legacy in ("import tier_engine", "import foundry_",
                               "from foundry_", "from tier_engine",
                               "experiments.", "pipeline.", "aq4"):
                    self.assertNotIn(legacy, text)

    def test_the_new_modules_import_no_third_party_module(self):
        import ast
        allowed = {"mtj_foundry", "__future__", "argparse", "hashlib", "json",
                   "os", "pathlib", "sys"}
        for name in ("evidence_index.py", "retrieval.py", "evaluation.py",
                     "evidence_cli.py"):
            tree = ast.parse((SRC / "mtj_foundry" / name).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                roots = []
                if isinstance(node, ast.Import):
                    roots = [a.name.split(".")[0] for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    roots = [node.module.split(".")[0]]
                for root in roots:
                    with self.subTest(module=name, imports=root):
                        self.assertIn(root, allowed)

    def test_the_command_reaches_no_legacy_module_when_actually_imported(self):
        code = ("import sys, mtj_foundry.evidence_cli\n"
                "banned = [m for m in sys.modules\n"
                "          if m.split('.')[0] in {'experiments','pipeline','tier_engine'}\n"
                "          or m.startswith('foundry_') or 'aq4' in m]\n"
                "assert not banned, banned\nprint('ok')\n")
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / "unrelated"
            outside.mkdir()
            env = dict(CLEAN_ENV, PYTHONPATH=str(SRC))
            proc = subprocess.run([sys.executable, "-c", code], cwd=outside,
                                  capture_output=True, text=True, env=env)
        self.assertEqual(proc.returncode, 0, proc.stderr)


# ===========================================================================
# 12. THE FROZEN PANEL IS SOURCE-PINNED
# ===========================================================================

class TestTheFrozenPanelFixture(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel = evaluation.load_panel(PANEL_PATH)

    def test_the_recorded_source_blob_id_matches_the_tracked_document(self):
        """A fixture whose source id no longer matches has either been re-pointed
        or had its source edited, and both are events a reviewer must SEE."""
        self.assertEqual(evaluation.git_blob_sha(FROZEN_SOURCE),
                         self.panel["source"]["git_blob_sha"])

    def test_the_historical_result_document_is_also_pinned_and_unedited(self):
        self.assertEqual(
            evaluation.git_blob_sha(FROZEN_RESULT),
            self.panel["historical_regression_context"]["git_blob_sha"])

    def test_every_transcribed_name_appears_verbatim_in_the_source(self):
        """The transcription is checked against the bytes, not trusted.

        Whitespace is collapsed before the search because the source is a WRAPPED
        markdown document: `Explosive\nVegetation` and `Kruphix, God of\nHorizons`
        are single names split across a line break, and a raw substring search
        called three correct transcriptions missing. The probe was wrong before
        the fixture was.
        """
        source = " ".join(FROZEN_SOURCE.read_text(encoding="utf-8").split())
        for anchor in self.panel["anchors"]:
            for name in [anchor["name"]] + anchor["named_correct"]:
                with self.subTest(name=name):
                    self.assertIn(" ".join(name.split()), source)
        for control in self.panel["controls"]:
            with self.subTest(name=control["name"]):
                self.assertIn(control["name"], source)

    def test_the_panel_transcribes_the_four_anchors_and_two_controls(self):
        self.assertEqual([a["label"] for a in self.panel["anchors"]],
                         ["A", "B", "C", "D"])
        self.assertEqual([c["label"] for c in self.panel["controls"]], ["F", "G"])

    def test_no_named_correct_name_is_duplicated_within_an_anchor(self):
        for anchor in self.panel["anchors"]:
            with self.subTest(anchor=anchor["label"]):
                self.assertEqual(len(anchor["named_correct"]),
                                 len(set(anchor["named_correct"])))

    def test_NEGATIVE_CONTROL_an_edited_source_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "edited.md"
            fake.write_text(FROZEN_SOURCE.read_text(encoding="utf-8") + "\nedited\n",
                            encoding="utf-8")
            self.assertNotEqual(evaluation.git_blob_sha(fake),
                                self.panel["source"]["git_blob_sha"])

    def test_the_document_axis_annotation_is_recorded_but_not_used_as_a_filter(self):
        """Pre-filtering by the axis the prediction document names would grade the
        evaluation on its own assumption. One of the four annotations is already
        stale — the axis was renamed since 2026-08-09 — which is exactly why."""
        for anchor in self.panel["anchors"]:
            with self.subTest(anchor=anchor["label"]):
                self.assertIn("RECORDED, NOT USED",
                              anchor["document_axis_annotation_is"])


# ===========================================================================
# 13. THE EVALUATION SEPARATES RECALL FROM PRESENTATION
# ===========================================================================

class TestTheEvaluationKeepsItsNumbersApart(IndexFixtureCase):
    """Run over a synthetic panel and a synthetic index, so the SHAPE of the
    report is asserted without depending on gitignored data."""

    def panel(self):
        return {
            "schema": evaluation.PANEL_SCHEMA,
            "id": "fixture-panel",
            "source": {"document": "fixture", "git_blob_sha": "0" * 40},
            "anchors": [{"label": "A", "name": "Fixture Legal",
                         "document_axis_annotation": "rule:alpha",
                         "named_correct": ["Fixture Reachable",
                                           "Fixture Nowhere Legal",
                                           "Fixture Not In Corpus"]}],
            "controls": [{"label": "F", "name": "Fixture Nowhere Legal",
                          "document_statement": "control"}],
            "known_failure_probes": {
                "what_these_are": "fixture probes",
                "probes": [{"name": "Fixture Nowhere Legal",
                            "source_section": "0",
                            "historical_finding": "fixture"}]},
        }

    def built(self):
        reachable = dict(LEGAL_CARD, oracle_id=ID_C, name="Fixture Reachable")
        index = self.index(corpus_records=[LEGAL_CARD, ILLEGAL_CARD, reachable])
        return evaluation.evaluate(index, self.panel())

    def test_discovery_and_presentation_are_separate_blocks(self):
        report = self.built()
        anchor = report["anchors"][0]
        self.assertEqual(anchor["candidate_discovery"]["discoverable"], 1)
        self.assertEqual(anchor["candidate_discovery"]["not_discoverable"], 2)
        self.assertEqual(anchor["presentation"]["measured_over"],
                         "discoverable named-correct cards ONLY")

    def test_a_not_discoverable_card_is_NEVER_scored_negatively(self):
        report = self.built()
        misses = [g for g in report["anchors"][0]["named_correct"]
                  if g["status"] != evaluation.DISCOVERABLE]
        self.assertEqual(len(misses), 2)
        for miss in misses:
            with self.subTest(name=miss["named_correct"]):
                self.assertFalse(miss["scored_negatively"])
                self.assertNotIn("rank", miss)

    def test_a_card_absent_from_the_corpus_is_its_own_verdict(self):
        report = self.built()
        verdicts = {g["named_correct"]: g["status"]
                    for g in report["anchors"][0]["named_correct"]}
        self.assertEqual(verdicts["Fixture Not In Corpus"], evaluation.NOT_IN_CORPUS)
        self.assertEqual(verdicts["Fixture Nowhere Legal"],
                         evaluation.NOT_DISCOVERABLE)

    def test_recall_is_labelled_as_DISCOVERY_recall_only(self):
        report = self.built()
        self.assertIn("candidate DISCOVERY recall only",
                      report["aggregate_candidate_discovery"]["recall_is"])

    def test_a_control_with_no_evidence_returns_empty_and_fabricates_nothing(self):
        report = self.built()
        control = report["controls"][0]
        self.assertTrue(control["unassigned_and_empty"])
        self.assertFalse(control["fabricated_semantic_evidence"])
        self.assertEqual(control["candidate_count"], 0)

    def test_a_probe_is_reported_as_absence_with_its_own_evidence_state(self):
        report = self.built()
        probe = report["known_failure_probes"]["probes"][0]
        self.assertEqual(probe["selected_evidence"]["evidence_state"],
                         evidence_index.EVIDENCE_STATE_UNASSIGNED)
        self.assertEqual(probe["against_panel_anchors"][0]["status"],
                         evaluation.NOT_DISCOVERABLE)
        self.assertIsNone(probe["against_panel_anchors"][0]["rank"])

    def test_the_report_states_what_it_does_not_prove(self):
        report = self.built()
        text = " ".join(report["what_this_does_not_prove"]).lower()
        for claim in ("sufficient for a product", "dissimilar", "authorised"):
            with self.subTest(claim=claim):
                self.assertIn(claim, text)

    def test_the_evaluation_is_deterministic(self):
        self.assertEqual(evaluation.render_evaluation(self.built()),
                         evaluation.render_evaluation(self.built()))

    def test_a_panel_with_the_wrong_schema_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "panel.json"
            path.write_text('{"schema": "wrong/1"}', encoding="utf-8")
            with self.assertRaises(evaluation.PanelError):
                evaluation.load_panel(path)


# ===========================================================================
# 14. THE REAL SELECTED INPUTS — skipped when the gitignored data is absent
# ===========================================================================

class TestAgainstTheRealSelectedInputs(unittest.TestCase):
    """The same composition the acceptance run exercises, so a later change that
    breaks it is caught by the ordinary suite on a machine that has the data.

    This is NOT the acceptance witness; that runs the INSTALLED command from an
    unrelated cwd and is recorded in the Worker result.
    """

    LOCK = REPO_ROOT / "refoundation" / "path-e" / "input-lock.json"
    REAL = ProjectPaths.for_root(REPO_ROOT)

    @classmethod
    def setUpClass(cls):
        missing = [str(p) for p in (cls.REAL.legacy_oracle_cards,
                                    cls.REAL.legacy_codebook_json) if not p.exists()]
        if missing:
            raise unittest.SkipTest(f"gitignored input(s) absent: {missing}")
        cls.index = evidence_index.generate(REPO_ROOT, lock_path=str(cls.LOCK))
        cls.panel = evaluation.load_panel(PANEL_PATH)

    def test_the_index_holds_the_ENTIRE_selected_corpus(self):
        conservation = self.index["conservation"]
        self.assertEqual(len(self.index["cards"]),
                         conservation["corpus_population"]["unique_oracle_ids"])
        self.assertEqual(len(self.index["cards"]),
                         conservation["eligibility"]["full_population_unique_ids"])

    def test_the_uncovered_majority_is_present_and_marked_unassigned(self):
        unassigned = sum(1 for r in self.index["cards"]
                         if r["evidence_state"]
                         == evidence_index.EVIDENCE_STATE_UNASSIGNED)
        self.assertEqual(unassigned,
                         self.index["conservation"]["coverage"]["corpus_ids_uncovered"])
        self.assertGreater(unassigned, len(self.index["cards"]) // 2)

    def test_the_selected_input_identities_are_carried_into_the_artifact(self):
        selected = self.index["selected_inputs"]
        self.assertEqual(
            selected["codebook"]["measured_sha256"],
            json.loads(self.REAL.codebook_authority_selector.read_text("utf-8"))["sha256"])
        self.assertEqual(selected["corpus"]["measured_sha256"],
                         selected["corpus"]["expected_sha256"])
        self.assertEqual(selected["corpus"]["measured_content_sha256"],
                         selected["corpus"]["expected_content_sha256"])

    def test_the_real_index_renders_deterministically(self):
        again = evidence_index.generate(REPO_ROOT, lock_path=str(self.LOCK))
        self.assertEqual(evidence_index.render_index(again),
                         evidence_index.render_index(self.index))

    def test_every_frozen_panel_name_resolves_to_exactly_one_oracle_id(self):
        view = retrieval.EvidenceIndexView(self.index)
        names = [a["name"] for a in self.panel["anchors"]]
        names += [n for a in self.panel["anchors"] for n in a["named_correct"]]
        names += [c["name"] for c in self.panel["controls"]]
        names += [p["name"] for p in self.panel["known_failure_probes"]["probes"]]
        for name in names:
            with self.subTest(name=name):
                self.assertEqual(len(view.resolve_name(name)), 1)

    def test_the_frozen_evaluation_is_deterministic(self):
        first = evaluation.evaluate(self.index, self.panel)
        second = evaluation.evaluate(self.index, self.panel)
        self.assertEqual(evaluation.render_evaluation(first),
                         evaluation.render_evaluation(second))

    def test_the_controls_carry_no_active_evidence_and_return_nothing(self):
        report = evaluation.evaluate(self.index, self.panel)
        for control in report["controls"]:
            with self.subTest(control=control["name"]):
                self.assertEqual(control["candidate_count"], 0)
                self.assertFalse(control["fabricated_semantic_evidence"])


if __name__ == "__main__":
    unittest.main()
