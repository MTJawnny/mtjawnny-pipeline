"""PATH E MILESTONE 3 — the static diagnostic pilot.

Every test here is about a STABLE PRODUCT PROPERTY, not about the numbers the
selected pilot inputs happen to produce. The fixture is synthetic and tiny, and
it is built to contain, on purpose, every shape the real corpus contains that a
naive builder loses: a Gate-#0-ineligible card, an unassigned card, a two-faced
card, two cards sharing a normalized name, a card on two axes and a card on one.

Where a number IS asserted it is re-derived from the fixture in the same test,
so a fixture change moves the expectation with it. The one thing deliberately
NOT asserted anywhere is a count from the real selected corpus: those live in
the artifacts, the manifest and the `X`, and pinning one here would be the
carried-forward-count trap aimed at the test suite.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tests.refoundation.helpers import REPO_ROOT  # noqa: F401  (sys.path bootstrap)

from mtj_foundry import evaluation, evidence_index, pilot, pilot_cli, retrieval


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

def _member(oracle_id: str, quote: str) -> dict:
    """A codebook member shaped like the real one: an id and a list of assertions."""
    return {"oracle_id": oracle_id,
            "assertions": [{"class": "human", "source_ref": "fixture",
                            "quote": quote, "corpus_ref": "2026-07-04",
                            "evidence_status": "quoted", "locality": [0, 0]}]}


def _face(name: str, text: str) -> dict:
    return {"name": name, "oracle_text": text, "mana_cost": "{1}",
            "type_line": "Sorcery", "power": None, "toughness": None}


#: Six cards. `ID_*` are ordered so `sorted()` matches the index's row order.
ID_ALPHA = "11111111-0000-0000-0000-000000000001"
ID_BETA = "22222222-0000-0000-0000-000000000002"
ID_GAMMA = "33333333-0000-0000-0000-000000000003"
ID_LONE = "44444444-0000-0000-0000-000000000004"   # unassigned
ID_TWIN_A = "55555555-0000-0000-0000-000000000005"  # shares a name with TWIN_B
ID_TWIN_B = "66666666-0000-0000-0000-000000000006"  # ...and is gate0-ineligible


def build_fixture_index() -> dict:
    """A whole `mtj-foundry-evidence-index/1`, small enough to reason about.

    Written as a literal rather than generated through the milestone-1 loaders:
    this milestone's unit under test consumes an ARTIFACT, so the fixture should
    be an artifact, and running the real loaders here would make these tests
    depend on a codebook and a corpus they have no business needing.
    """
    axes = {
        "rule:broad": {"axis_id": "rule:broad", "status": "active",
                       "definition": "a broad axis", "scope": "self",
                       "source": "fixture", "parameterized": False,
                       "active_member_count": 3,
                       "active_member_count_is": "cardinality"},
        "rule:sharp": {"axis_id": "rule:sharp", "status": "active",
                       "definition": "a sharp axis", "scope": "self",
                       "source": "fixture", "parameterized": False,
                       "active_member_count": 2,
                       "active_member_count_is": "cardinality"},
    }
    rows = [
        # ALPHA is on BOTH axes -> it is the anchor with a real tie structure.
        (ID_ALPHA, "Alpha Rite", True, [_face("Alpha Rite", "Destroy target permanent.")],
         [("rule:broad", "Destroy target permanent."),
          ("rule:sharp", "Destroy target permanent.")]),
        # BETA shares both with ALPHA -> its own block, ahead of the broad-only cards.
        (ID_BETA, "Beta Rite", True, [_face("Beta Rite", "Destroy target permanent.")],
         [("rule:broad", "Destroy target permanent."),
          ("rule:sharp", "Destroy target permanent.")]),
        # GAMMA shares only the broad axis. TWO FACES, so face loss is detectable.
        (ID_GAMMA, "Gamma Front // Gamma Back", True,
         [_face("Gamma Front", "Destroy target creature."),
          _face("Gamma Back", "Whenever this creature attacks, draw a card.")],
         [("rule:broad", "Destroy target creature.")]),
        # LONE is on nothing: the UNASSIGNED case.
        (ID_LONE, "Lone Wanderer", True, [_face("Lone Wanderer", "Gain 3 life.")], []),
        # TWIN_A / TWIN_B share a normalized name; TWIN_B is gate0-INELIGIBLE.
        (ID_TWIN_A, "Twin Card", True, [_face("Twin Card", "Draw a card.")], []),
        (ID_TWIN_B, "twin card", False, [_face("twin card", "Draw a card.")], []),
    ]
    cards = []
    for oracle_id, name, eligible, faces, memberships in rows:
        cards.append({
            "oracle_id": oracle_id, "name": name,
            "normalized_name": name.strip().casefold(),
            "gate0_eligible": eligible, "faces": faces,
            "evidence_state": (evidence_index.EVIDENCE_STATE_ASSIGNED if memberships
                               else evidence_index.EVIDENCE_STATE_UNASSIGNED),
            "memberships": [{"axis_id": axis_id,
                             "member": _member(oracle_id, quote)}
                            for axis_id, quote in memberships],
        })
    name_index: dict = {}
    for card in cards:
        name_index.setdefault(card["normalized_name"], []).append(card["oracle_id"])
    covered = sum(1 for c in cards if c["memberships"])
    return {
        "schema": evidence_index.INDEX_SCHEMA,
        "generator": {"package": "mtj_foundry", "version": "test",
                      "capability": "full_population_evidence_index"},
        "artifact_is": "DERIVED_EVIDENCE_NOT_AUTHORITY",
        "evidence_state_semantics": {
            evidence_index.EVIDENCE_STATE_ASSIGNED: "has active evidence",
            evidence_index.EVIDENCE_STATE_UNASSIGNED:
                "the selected codebook records NO membership for this card",
            "UNASSIGNED_IS_NOT": ["not a judgement that the card is dissimilar",
                                  "not negative evidence of any kind"],
            "absent_membership_is": "UNKNOWN, never FALSE",
        },
        "selected_inputs": {
            "authority_selector": {"path": "docs/codebook-authority.json"},
            "codebook": {"path": "codebook.json", "measured_sha256": "c" * 64,
                         "measured_byte_size": 11},
            "corpus": {"path": "corpus.jsonl.gz", "measured_sha256": "f" * 64,
                       "measured_byte_size": 22, "measured_content_sha256": "e" * 64,
                       "identity_status": "FIXTURE"},
        },
        "conservation": {
            "corpus_population": {"unique_oracle_ids": len(cards)},
            "eligibility": {
                "eligible_unique_ids": sum(1 for c in cards if c["gate0_eligible"]),
                "ineligible_unique_ids": sum(1 for c in cards
                                             if not c["gate0_eligible"])},
            "coverage": {"corpus_ids_total": len(cards),
                         "corpus_ids_covered": covered,
                         "corpus_ids_uncovered": len(cards) - covered},
            "codebook_structure": {"axes_by_status": {"active": len(axes)}},
            "codebook_lint": {},
            "codebook_evidence_fields_present_on_active_axes": {},
        },
        "axes": axes,
        "name_index": name_index,
        "cards": cards,
    }


def build_fixture_evaluation(index: dict) -> dict:
    """An `mtj-foundry-m2-evaluation/1` that agrees with the fixture index."""
    coverage = index["conservation"]["coverage"]
    return {
        "schema": evaluation.EVALUATION_SCHEMA,
        "generator": {"package": "mtj_foundry", "version": "test",
                      "capability": "frozen_panel_retrieval_evaluation"},
        "evaluation_is": "A MEASUREMENT",
        "panel": {"id": "fixture-panel", "source_document": "fixture.md"},
        "index": {"schema": index["schema"],
                  "selected_codebook_sha256":
                      index["selected_inputs"]["codebook"]["measured_sha256"],
                  "selected_corpus_sha256":
                      index["selected_inputs"]["corpus"]["measured_sha256"],
                  "corpus_ids_total": coverage["corpus_ids_total"],
                  "corpus_ids_covered": coverage["corpus_ids_covered"],
                  "corpus_ids_uncovered": coverage["corpus_ids_uncovered"]},
        "ordering": retrieval.ORDERING_RULE,
        "aggregate_candidate_discovery": {"named_correct_total": 4,
                                          "discoverable": 1, "not_discoverable": 3,
                                          "recall": 0.25},
        "aggregate_presentation": {"measured_over": "discoverable only",
                                   "discoverable_total": 1, "in_top_10": 1,
                                   "in_top_25": 1,
                                   "in_a_tie_block_larger_than_one": 1},
        "anchors": [], "controls": [],
        "known_failure_probes": {"probes": []},
        "what_this_does_not_prove": ["that the selected evidence is sufficient"],
    }


class PilotFixture(unittest.TestCase):
    """Writes the two source artifacts once, builds the bundle once."""

    @classmethod
    def setUpClass(cls):
        cls.index = build_fixture_index()
        cls.evaluation = build_fixture_evaluation(cls.index)
        cls._tmp = TemporaryDirectory()
        root = Path(cls._tmp.name)
        cls.index_path = root / "index.json"
        cls.evaluation_path = root / "evaluation.json"
        cls.index_path.write_text(
            evidence_index.render_index(cls.index), encoding="utf-8")
        cls.evaluation_path.write_text(
            evaluation.render_evaluation(cls.evaluation), encoding="utf-8")
        cls.output = root / "bundle"
        cls.manifest = pilot.build(cls.index_path, cls.evaluation_path, cls.output)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def emitted(self, relative: str) -> dict:
        with open(self.output / relative, "r", encoding="utf-8") as handle:
            return json.load(handle)


# ---------------------------------------------------------------------------
# Input gates
# ---------------------------------------------------------------------------

class TestTheSourceArtifactsAreGated(PilotFixture):

    def test_a_wrong_index_schema_is_refused(self):
        with TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            document = dict(self.index, schema="something-else/1")
            bad.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaises(retrieval.IndexSchemaError):
                pilot.build(bad, self.evaluation_path, Path(tmp) / "out")

    def test_a_wrong_evaluation_schema_is_refused(self):
        with TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text(json.dumps(dict(self.evaluation, schema="nope/1")),
                           encoding="utf-8")
            with self.assertRaises(pilot.PilotInputError):
                pilot.build(self.index_path, bad, Path(tmp) / "out")

    def test_an_unreadable_evaluation_is_refused(self):
        with TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text("{not json", encoding="utf-8")
            with self.assertRaises(pilot.PilotInputError):
                pilot.build(self.index_path, bad, Path(tmp) / "out")

    def test_an_evaluation_graded_from_a_different_index_is_refused(self):
        """THE CHECK WITH NO OTHER REPORTER. Both artifacts are individually
        valid and every number in the resulting bundle would look right; only
        comparing them can see that they describe two different runs."""
        for field, value in [("selected_codebook_sha256", "a" * 64),
                             ("selected_corpus_sha256", "b" * 64),
                             ("corpus_ids_total", 999),
                             ("corpus_ids_covered", 999),
                             ("corpus_ids_uncovered", 999)]:
            with self.subTest(field=field):
                document = json.loads(json.dumps(self.evaluation))
                document["index"][field] = value
                with self.assertRaises(pilot.PilotInputError) as caught:
                    pilot.reconcile_selected_inputs(self.index, document)
                self.assertIn(str(value), str(caught.exception))

    def test_matching_artifacts_reconcile(self):
        agreed = pilot.reconcile_selected_inputs(self.index, self.evaluation)
        self.assertEqual(agreed["selected corpus sha256"],
                         self.index["selected_inputs"]["corpus"]["measured_sha256"])


# ---------------------------------------------------------------------------
# The output boundary
# ---------------------------------------------------------------------------

class TestWritesStayUnderTheDeclaredOutputRoot(PilotFixture):

    def test_every_emitted_path_is_inside_the_output_directory(self):
        for path in self.output.rglob("*"):
            with self.subTest(path=path):
                path.resolve().relative_to(self.output.resolve())

    def test_nothing_was_written_beside_the_output_directory(self):
        siblings = {entry.name for entry in self.output.parent.iterdir()}
        self.assertEqual(siblings, {"index.json", "evaluation.json", "bundle"})

    def test_a_traversing_relative_path_is_refused(self):
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            out.mkdir()
            with self.assertRaises(pilot.PilotOutputError):
                pilot.write_bundle({"../escaped.json": b"{}"}, out)
            self.assertFalse((Path(tmp) / "escaped.json").exists())

    def test_an_absolute_path_in_the_file_map_is_refused(self):
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            out.mkdir()
            with self.assertRaises(pilot.PilotOutputError):
                pilot.write_bundle({"/tmp/escaped-by-pilot.json": b"{}"}, out)

    def test_an_unrecognised_non_empty_directory_is_refused(self):
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            out.mkdir()
            keep = out / "someones-notes.txt"
            keep.write_text("do not delete me", encoding="utf-8")
            with self.assertRaises(pilot.PilotOutputError):
                pilot.build(self.index_path, self.evaluation_path, out)
            self.assertEqual(keep.read_text(encoding="utf-8"), "do not delete me")

    def test_a_directory_holding_this_builders_manifest_is_replaced(self):
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            first = pilot.build(self.index_path, self.evaluation_path, out)
            stale = out / "data" / "text" / "zz.json"
            stale.write_text("{}", encoding="utf-8")
            second = pilot.build(self.index_path, self.evaluation_path, out)
            self.assertEqual(first["files"], second["files"])
            # The stray file is NOT deleted -- only recorded files are removed --
            # and `verify_manifest` reports it rather than the build hiding it.
            self.assertTrue(stale.exists())
            with self.assertRaises(pilot.PilotConservationError):
                pilot.verify_manifest(out)

    def test_a_path_that_is_not_a_directory_is_refused(self):
        with TemporaryDirectory() as tmp:
            blocker = Path(tmp) / "blocker"
            blocker.write_text("", encoding="utf-8")
            with self.assertRaises(pilot.PilotOutputError):
                pilot.build(self.index_path, self.evaluation_path, blocker)

    def test_the_builder_never_recursively_deletes(self):
        """A structural check, because the failure mode of the alternative is
        unbounded: a recursive delete of a caller-supplied path cannot be made
        safe by being careful, only by not being there.

        Aimed at the CODE PATH and not at the module's text -- the first draft of
        this test grepped for the word and failed on the docstring that explains
        the rule, which is the same defect as a negative control aimed at a
        tool's name instead of its branch.
        """
        import ast

        tree = ast.parse(Path(pilot.__file__).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotEqual(alias.name.split(".")[0], "shutil")
            if isinstance(node, ast.ImportFrom) and node.module:
                self.assertNotEqual(node.module.split(".")[0], "shutil")
            if isinstance(node, ast.Attribute):
                self.assertNotIn(node.attr, {"rmtree", "removedirs"})
            if isinstance(node, ast.Name):
                self.assertNotIn(node.id, {"rmtree", "removedirs"})


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

class TestTheBundleIsDeterministic(PilotFixture):

    def test_two_builds_into_unrelated_roots_are_byte_identical(self):
        with TemporaryDirectory() as one, TemporaryDirectory() as two:
            first = Path(one) / "deep" / "alpha"
            second = Path(two) / "beta"
            pilot.build(self.index_path, self.evaluation_path, first)
            pilot.build(self.index_path, self.evaluation_path, second)
            left = {str(p.relative_to(first)): p.read_bytes()
                    for p in first.rglob("*") if p.is_file()}
            right = {str(p.relative_to(second)): p.read_bytes()
                     for p in second.rglob("*") if p.is_file()}
            self.assertEqual(sorted(left), sorted(right))
            for name in sorted(left):
                with self.subTest(file=name):
                    self.assertEqual(left[name], right[name])

    def test_the_manifest_does_not_depend_on_where_the_sources_live(self):
        """The source PATH is not recorded, only the digest -- so the same bytes
        fed from two directories produce the same manifest. A path would have
        made this fail while every other determinism check still passed."""
        with TemporaryDirectory() as elsewhere, TemporaryDirectory() as out:
            moved_index = Path(elsewhere) / "renamed-index.json"
            moved_eval = Path(elsewhere) / "renamed-eval.json"
            moved_index.write_bytes(self.index_path.read_bytes())
            moved_eval.write_bytes(self.evaluation_path.read_bytes())
            other = pilot.build(moved_index, moved_eval, Path(out) / "bundle")
            self.assertEqual(other, self.manifest)


# ---------------------------------------------------------------------------
# The manifest
# ---------------------------------------------------------------------------

class TestTheManifest(PilotFixture):

    def test_it_records_the_exact_source_artifact_identities(self):
        import hashlib

        for role, path in [("index", self.index_path),
                           ("evaluation", self.evaluation_path)]:
            with self.subTest(role=role):
                payload = path.read_bytes()
                recorded = self.manifest["source_artifacts"][role]
                self.assertEqual(recorded["sha256"], hashlib.sha256(payload).hexdigest())
                self.assertEqual(recorded["byte_size"], len(payload))

    def test_it_declares_the_diagnostic_status(self):
        self.assertEqual(self.manifest["status"], pilot.PILOT_STATUS)
        self.assertEqual(self.manifest["status"], "DIAGNOSTIC_NOT_PRODUCT_QUALIFIED")
        self.assertEqual(self.manifest["pilot_schema"], pilot.PILOT_SCHEMA)

    def test_it_covers_every_emitted_file_except_itself(self):
        verified = pilot.verify_manifest(self.output)
        self.assertEqual(verified["self_excluded"], pilot.MANIFEST_NAME)
        recorded = {entry["path"] for entry in verified["files"]}
        self.assertNotIn(pilot.MANIFEST_NAME, recorded)
        on_disk = {str(p.relative_to(self.output)) for p in self.output.rglob("*")
                   if p.is_file()}
        self.assertEqual(recorded, on_disk - {pilot.MANIFEST_NAME})

    def test_a_tampered_file_fails_verification(self):
        """The negative control for the check above. Without it, `verify_manifest`
        is a function that has never been shown to fail."""
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "bundle"
            pilot.build(self.index_path, self.evaluation_path, out)
            pilot.verify_manifest(out)
            victim = out / "data" / "cards.json"
            victim.write_bytes(victim.read_bytes() + b" ")
            with self.assertRaises(pilot.PilotConservationError):
                pilot.verify_manifest(out)

    def test_its_population_counts_come_from_the_source_artifact(self):
        coverage = self.index["conservation"]["coverage"]
        self.assertEqual(self.manifest["population"]["corpus_ids_total"],
                         coverage["corpus_ids_total"])
        self.assertEqual(self.manifest["population"]["corpus_ids_covered"],
                         coverage["corpus_ids_covered"])
        self.assertEqual(self.manifest["population"]["corpus_ids_uncovered"],
                         coverage["corpus_ids_uncovered"])

    def test_its_frozen_metrics_come_from_the_evaluation_artifact(self):
        self.assertEqual(self.manifest["frozen_evaluation"]
                         ["aggregate_candidate_discovery"],
                         self.evaluation["aggregate_candidate_discovery"])
        self.assertEqual(self.manifest["frozen_evaluation"]["aggregate_presentation"],
                         self.evaluation["aggregate_presentation"])


# ---------------------------------------------------------------------------
# Population — the whole corpus reaches the browser
# ---------------------------------------------------------------------------

class TestEveryCardIsPresentAndSelectable(PilotFixture):

    def test_the_card_directory_holds_every_oracle_id_in_source_order(self):
        cards = self.emitted("data/cards.json")
        self.assertEqual(cards["oracle_id"],
                         [row["oracle_id"] for row in self.index["cards"]])
        self.assertEqual(cards["count"], len(self.index["cards"]))

    def test_ineligible_and_unassigned_cards_are_present(self):
        """The two states most likely to be quietly filtered, asserted by NAME
        rather than by count: a count cannot see a substitution."""
        cards = self.emitted("data/cards.json")
        by_id = dict(zip(cards["oracle_id"], range(cards["count"])))
        self.assertIn(ID_TWIN_B, by_id)
        self.assertEqual(cards["gate0_eligible"][by_id[ID_TWIN_B]], 0)
        self.assertIn(ID_LONE, by_id)
        self.assertEqual(cards["assigned"][by_id[ID_LONE]], 0)

    def test_no_emitted_file_was_built_by_dropping_rows(self):
        report = pilot.verify_population(self.output, self.index)
        self.assertEqual(report["cards"], len(self.index["cards"]))
        self.assertEqual(report["faces_verified"], len(self.index["cards"]))

    def test_a_dropped_row_fails_the_population_check(self):
        """Negative control. `verify_population` is aimed at the SHAPE a filter
        leaves behind, so it is shown a bundle missing exactly one row."""
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "bundle"
            pilot.build(self.index_path, self.evaluation_path, out)
            cards = json.loads((out / "data" / "cards.json").read_text(encoding="utf-8"))
            cards["oracle_id"] = cards["oracle_id"][:-1]
            (out / "data" / "cards.json").write_text(json.dumps(cards), encoding="utf-8")
            with self.assertRaises(pilot.PilotConservationError):
                pilot.verify_population(out, self.index)

    def test_multi_face_text_survives_verbatim(self):
        gamma = next(row for row in self.index["cards"]
                     if row["oracle_id"] == ID_GAMMA)
        self.assertEqual(len(gamma["faces"]), 2)
        shard = self.emitted(f"data/text/{ID_GAMMA[:2]}.json")
        emitted = dict(shard["rows"])
        position = [row["oracle_id"] for row in self.index["cards"]].index(ID_GAMMA)
        self.assertEqual(emitted[position], gamma["faces"])
        self.assertEqual([face["oracle_text"] for face in emitted[position]],
                         ["Destroy target creature.",
                          "Whenever this creature attacks, draw a card."])

    def test_an_ambiguous_normalized_name_keeps_every_identity_in_order(self):
        names = self.emitted("data/names.json")
        positions = [row["oracle_id"] for row in self.index["cards"]]
        emitted = names["names"]["twin card"]
        self.assertEqual([positions[i] for i in emitted], [ID_TWIN_A, ID_TWIN_B])
        self.assertEqual(names["ambiguous_names"], 1)

    def test_the_name_index_is_the_artifacts_own_not_a_rebuild(self):
        """Rebuilding from the oracle_id-sorted rows would silently reorder every
        ambiguous name's identities. The bundle's lists must be the artifact's."""
        names = self.emitted("data/names.json")["names"]
        positions = [row["oracle_id"] for row in self.index["cards"]]
        self.assertEqual(sorted(names), sorted(self.index["name_index"]))
        for key, ids in self.index["name_index"].items():
            with self.subTest(name=key):
                self.assertEqual([positions[i] for i in names[key]], ids)


# ---------------------------------------------------------------------------
# Evidence — copied, never synthesized
# ---------------------------------------------------------------------------

class TestEvidenceIsCopiedWhole(PilotFixture):

    def test_every_membership_reaches_the_bundle_with_its_member_object_intact(self):
        evidence = self.emitted("data/evidence.json")
        axes = self.emitted("data/axes.json")["order"]
        positions = [row["oracle_id"] for row in self.index["cards"]]
        emitted = {positions[card]: [(axes[a], member) for a, member in rows]
                   for card, rows in evidence["rows"]}
        expected = {row["oracle_id"]: [(m["axis_id"], m["member"])
                                       for m in row["memberships"]]
                    for row in self.index["cards"] if row["memberships"]}
        self.assertEqual(emitted, expected)

    def test_an_unknown_member_field_survives_the_copy(self):
        """The projection trap: a renderer or a transport that enumerates the
        fields it expects drops a field a later codebook schema adds, at the very
        last step. Asserted with a key this milestone has never heard of."""
        document = json.loads(json.dumps(self.index))
        document["cards"][0]["memberships"][0]["member"]["a_field_from_2027"] = \
            {"nested": ["value"]}
        with TemporaryDirectory() as tmp:
            source = Path(tmp) / "index.json"
            source.write_text(evidence_index.render_index(document), encoding="utf-8")
            out = Path(tmp) / "bundle"
            pilot.build(source, self.evaluation_path, out)
            evidence = json.loads((out / "data" / "evidence.json").read_text("utf-8"))
            member = evidence["rows"][0][1][0][1]
            self.assertEqual(member["a_field_from_2027"], {"nested": ["value"]})

    def test_an_unassigned_card_has_no_evidence_row_and_no_retrieval_row(self):
        evidence = self.emitted("data/evidence.json")
        positions = [row["oracle_id"] for row in self.index["cards"]]
        lone = positions.index(ID_LONE)
        self.assertNotIn(lone, {row[0] for row in evidence["rows"]})
        shard_path = self.output / "data" / "retrieval" / f"{ID_LONE[:2]}.json"
        if shard_path.exists():
            rows = json.loads(shard_path.read_text(encoding="utf-8"))["rows"]
            self.assertNotIn(lone, {row[0] for row in rows})

    def test_no_candidate_was_fabricated_for_an_unassigned_card(self):
        """Positively stated: the accepted retrieval returns zero for this anchor
        and the bundle must contain no structure that could render otherwise."""
        result = retrieval.query(self.index, oracle_id=ID_LONE)
        self.assertEqual(result["candidate_count"], 0)
        self.assertEqual(result["result_state"], retrieval.RESULT_STATE_UNASSIGNED)


# ---------------------------------------------------------------------------
# THE BROWSER BOUNDARY
# ---------------------------------------------------------------------------

class TestRetrievalEquivalence(PilotFixture):
    """The emitted blocks equal `mtj_foundry.retrieval.query`, exhaustively."""

    def test_every_assigned_anchor_matches_the_accepted_retrieval(self):
        report = pilot.verify_retrieval_equivalence(self.output, self.index)
        self.assertTrue(report["exhaustive"])
        self.assertEqual(report["anchors_checked"],
                         sum(1 for row in self.index["cards"] if row["memberships"]))

    def test_the_tie_block_structure_matches_the_accepted_ranking(self):
        """Read against a hand-derived expectation, not only against the code
        that produced it: ALPHA shares BOTH axes with BETA and only the broad one
        with GAMMA, so key 1 must put BETA in its own block ahead of GAMMA."""
        positions = [row["oracle_id"] for row in self.index["cards"]]
        rows = dict(self.emitted(f"data/retrieval/{ID_ALPHA[:2]}.json")["rows"])
        anchor = rows[positions.index(ID_ALPHA)]
        self.assertEqual(anchor["candidate_count"], 2)
        self.assertEqual([b["size"] for b in anchor["blocks"]], [1, 1])
        self.assertEqual([b["shared_axis_count"] for b in anchor["blocks"]], [2, 1])
        self.assertEqual([b["shared_axis_cardinalities"] for b in anchor["blocks"]],
                         [[2, 3], [3]])
        first = anchor["blocks"][0]["members"][0][0]
        self.assertEqual(positions[first], ID_BETA)

    def test_a_reordered_block_fails_the_equivalence_check(self):
        """Negative control aimed at the ORDER, which is the thing the browser is
        forbidden to decide. A check that only compared candidate SETS would pass
        against this bundle."""
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "bundle"
            pilot.build(self.index_path, self.evaluation_path, out)
            pilot.verify_retrieval_equivalence(out, self.index)
            shard = out / "data" / "retrieval" / f"{ID_ALPHA[:2]}.json"
            payload = json.loads(shard.read_text(encoding="utf-8"))
            for _, anchor in payload["rows"]:
                anchor["blocks"].reverse()
            shard.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(pilot.PilotConservationError):
                pilot.verify_retrieval_equivalence(out, self.index)

    def test_a_dropped_candidate_fails_the_equivalence_check(self):
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "bundle"
            pilot.build(self.index_path, self.evaluation_path, out)
            shard = out / "data" / "retrieval" / f"{ID_ALPHA[:2]}.json"
            payload = json.loads(shard.read_text(encoding="utf-8"))
            payload["rows"][0][1]["blocks"].pop()
            shard.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(pilot.PilotConservationError):
                pilot.verify_retrieval_equivalence(out, self.index)

    def test_individual_ranks_are_not_written_into_a_block(self):
        """A per-member ordinal would be a number the artifact does not mean:
        within a block, key 3 is oracle_id ascending and carries no semantics."""
        for shard in (self.output / "data" / "retrieval").glob("*.json"):
            payload = json.loads(shard.read_text(encoding="utf-8"))
            for _, anchor in payload["rows"]:
                for block in anchor["blocks"]:
                    for member in block["members"]:
                        with self.subTest(shard=shard.name):
                            self.assertEqual(len(member), 2)
                            self.assertIsInstance(member[0], int)
                            self.assertIsInstance(member[1], list)


# ---------------------------------------------------------------------------
# The disclosure — derived, and visible in the page rather than in a doc
# ---------------------------------------------------------------------------

class TestTheDiagnosticDisclosure(PilotFixture):

    def setUp(self):
        self.meta = self.emitted("data/meta.json")
        self.disclosure = self.meta["disclosure"]
        self.prose = " ".join([self.disclosure["headline"], *self.disclosure["points"],
                               self.disclosure["tie_blocks_are"]])

    def test_its_numbers_are_derived_from_the_source_artifacts(self):
        coverage = self.index["conservation"]["coverage"]
        discovery = self.evaluation["aggregate_candidate_discovery"]
        for value in (coverage["corpus_ids_total"], coverage["corpus_ids_covered"],
                      coverage["corpus_ids_uncovered"], discovery["discoverable"],
                      discovery["named_correct_total"]):
            with self.subTest(value=value):
                self.assertIn(f"{value:,}", self.prose)

    def test_a_different_source_artifact_produces_different_disclosure_numbers(self):
        """THE CHECK THAT A HARDCODED COUNT WOULD PASS. The first version of the
        index's own UNASSIGNED clause carried the day's counts as a module-level
        constant and read as a definition; only building from DIFFERENT inputs
        can tell a derived number from a typed one."""
        document = json.loads(json.dumps(self.index))
        document["conservation"]["coverage"]["corpus_ids_total"] = 41000
        document["conservation"]["coverage"]["corpus_ids_covered"] = 40000
        document["conservation"]["coverage"]["corpus_ids_uncovered"] = 1000
        other = json.loads(json.dumps(self.evaluation))
        other["index"]["corpus_ids_total"] = 41000
        other["index"]["corpus_ids_covered"] = 40000
        other["index"]["corpus_ids_uncovered"] = 1000
        moved = pilot._disclosure(document, other)
        prose = " ".join(moved["points"])
        self.assertIn("41,000", prose)
        self.assertIn("40,000", prose)
        # THE QUANTIFIER MOVES TOO. Fixing the digits and leaving the adjective
        # would relocate the same defect one word to the right, where it is
        # harder to see. All three branches are exercised, because a quantifier
        # that is right for two populations and wrong for the third is exactly
        # what a single-case check cannot see.
        self.assertIn("a majority", prose)
        self.assertIn("exactly half", " ".join(self.disclosure["points"]))
        scarce = json.loads(json.dumps(document))
        scarce["conservation"]["coverage"].update(
            {"corpus_ids_total": 100, "corpus_ids_covered": 1,
             "corpus_ids_uncovered": 99})
        thin = json.loads(json.dumps(other))
        thin["index"].update({"corpus_ids_total": 100, "corpus_ids_covered": 1,
                              "corpus_ids_uncovered": 99})
        self.assertIn("a minority",
                      " ".join(pilot._disclosure(scarce, thin)["points"]))

    def test_absence_is_stated_as_unknown_and_never_as_dissimilarity(self):
        self.assertIn("ABSENCE OF EVIDENCE IS UNKNOWN, NOT DISSIMILARITY", self.prose)
        self.assertIn("NEVER a finding that no similar cards exist", self.prose)

    def test_it_says_the_index_holds_the_entire_selected_corpus(self):
        self.assertIn("ENTIRE selected corpus", self.prose)
        self.assertIn("never filters that remove one", self.prose)

    def test_it_reports_the_frozen_limits_rather_than_hiding_them(self):
        self.assertIn("LIMITED DISCOVERY AND LARGE TIE BLOCKS".title().upper()
                      .replace("AND", "AND"), self.prose.upper())
        self.assertIn("tie block larger than", self.prose)

    def test_it_refuses_the_product_claim(self):
        for phrase in ("not a finished thesaurus", "not a production Searcher B",
                       "not a recommendation engine",
                       "not a claim about similarity"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.disclosure["headline"])
        self.assertEqual(self.disclosure["status"], pilot.PILOT_STATUS)

    def test_the_ordering_rule_is_carried_from_the_artifact_not_restated(self):
        self.assertEqual(self.disclosure["ordering"], self.evaluation["ordering"])

    def test_the_page_renders_the_disclosure_rather_than_only_documenting_it(self):
        markup = (self.output / "index.html").read_text(encoding="utf-8")
        script = (self.output / "assets" / "pilot.js").read_text(encoding="utf-8")
        for anchor in ("disclosure-headline", "disclosure-points", "does-not-prove",
                       "ordering-keys", "unassigned-is-not"):
            with self.subTest(anchor=anchor):
                self.assertIn(anchor, markup)
                self.assertIn(anchor, script)
        # It is in the document body, not inside a collapsed <details>.
        body = markup.split("<main>")[0]
        self.assertIn('id="disclosure"', body)


# ---------------------------------------------------------------------------
# The bundle is self-contained
# ---------------------------------------------------------------------------

def _javascript_code_only(source: str) -> str:
    """`source` with comments and string/template literals removed.

    A small scanner rather than a regex, because a regex that tries to tell a
    quote inside a comment from a comment inside a quote gets one of the two
    wrong, and both mistakes here read as a passing test.
    """
    out = []
    i, n = 0, len(source)
    while i < n:
        char = source[i]
        if char == "/" and i + 1 < n and source[i + 1] == "/":
            i = source.find("\n", i)
            if i < 0:
                break
        elif char == "/" and i + 1 < n and source[i + 1] == "*":
            end = source.find("*/", i + 2)
            i = n if end < 0 else end + 2
        elif char in "\"'`":
            quote, i = char, i + 1
            while i < n and source[i] != quote:
                i += 2 if source[i] == "\\" else 1
            i += 1
        else:
            out.append(char)
            i += 1
    return "".join(out)


class TestNoExternalDependency(PilotFixture):

    def _assets(self) -> dict:
        """Each asset with its COMMENTS removed.

        Aimed at what causes a request, not at what the file says about itself:
        the raw-text version of this check failed on the JavaScript's own comment
        promising "no cdn, no font host, no analytics and no api in this bundle".
        Third time this milestone that a check pointed at prose instead of the
        code path -- the repository's own most-recurring defect class, and the
        reason `foundry_probe` exists on the legacy side.
        """
        out = {}
        for name in ("index.html", "assets/pilot.css", "assets/pilot.js"):
            text = (self.output / name).read_text(encoding="utf-8")
            if name.endswith(".js"):
                text = _javascript_code_only(text)
            elif name.endswith(".css"):
                text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
            else:
                text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
            out[name] = text
        return out

    def test_no_absolute_url_appears_in_any_emitted_asset(self):
        """`data:` is allowed and `http://www.w3.org/2000/svg` inside the inline
        favicon is an XML NAMESPACE, not a fetch -- so the check is aimed at the
        forms that actually cause a request."""
        pattern = re.compile(r'(?:src|href|url\()\s*=?\s*["\']?(https?:)?//', re.I)
        for name, text in self._assets().items():
            with self.subTest(asset=name):
                self.assertIsNone(pattern.search(text), name)

    def test_no_cdn_font_analytics_or_api_host_is_referenced(self):
        for name, text in self._assets().items():
            lowered = text.lower()
            for forbidden in ("cdn.", "googleapis", "gstatic", "unpkg", "jsdelivr",
                              "cloudflare", "analytics", "gtag", "websocket",
                              "new websocket", "xmlhttprequest", "/api/"):
                with self.subTest(asset=name, forbidden=forbidden):
                    self.assertNotIn(forbidden, lowered)

    def test_every_fetch_in_the_page_is_a_relative_bundle_path(self):
        script = (self.output / "assets" / "pilot.js").read_text(encoding="utf-8")
        calls = re.findall(r'fetch\(\s*([^,\)]+)', script)
        self.assertTrue(calls)
        for call in calls:
            with self.subTest(call=call):
                self.assertNotIn("//", call)
                self.assertNotIn("http", call)

    def test_the_page_contains_no_ranking_candidate_or_similarity_logic(self):
        """The browser boundary, asserted against the shipped file.

        AIMED AT CODE, NOT AT TEXT. The first draft searched the raw file and
        failed on the page's own sentence "no text similarity, no embedding, no
        model, no score" -- the prose that PROMISES the property, flagged as a
        violation of it. Comments and string literals are stripped first, so what
        is searched is the executable text: the same correction as the `shutil`
        control above, and the same one the repository's own probe-defect record
        keeps arriving at.
        """
        code = _javascript_code_only(
            (self.output / "assets" / "pilot.js").read_text(encoding="utf-8"))
        for forbidden in (".sort(", "localeCompare", "score", "similarity",
                          "embedding", "weight", "threshold", "tfidf", "idf",
                          "Intl.Collator"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, code)

    def test_the_bundle_is_only_json_html_css_and_js(self):
        suffixes = {path.suffix for path in self.output.rglob("*") if path.is_file()}
        self.assertEqual(suffixes, {".json", ".html", ".css", ".js"})


# ---------------------------------------------------------------------------
# The installed surface
# ---------------------------------------------------------------------------

class TestTheInstalledCommand(PilotFixture):

    def test_a_successful_run_writes_the_bundle_and_prints_a_summary(self):
        import contextlib
        import io

        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "bundle"
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                status = pilot_cli.main(["--index", str(self.index_path),
                                         "--evaluation", str(self.evaluation_path),
                                         "--output", str(out)])
            self.assertEqual(status, 0)
            self.assertEqual(stderr.getvalue(), "")
            self.assertIn(pilot.PILOT_STATUS, stdout.getvalue())
            self.assertTrue((out / "index.html").is_file())

    def test_a_bad_input_exits_1_with_stop_on_stderr_and_nothing_on_stdout(self):
        import contextlib
        import io

        with TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text("{}", encoding="utf-8")
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                status = pilot_cli.main(["--index", str(bad),
                                         "--evaluation", str(self.evaluation_path),
                                         "--output", str(Path(tmp) / "out")])
            self.assertEqual(status, 1)
            self.assertEqual(stdout.getvalue(), "")
            self.assertTrue(stderr.getvalue().startswith("STOP — "))

    def test_the_milestone_2_command_was_not_given_a_writing_subcommand(self):
        """M2's accepted contract says it writes no file and creates no directory.
        This milestone kept that true by taking its own script instead."""
        from mtj_foundry import evidence_cli

        parser = evidence_cli.build_parser()
        actions = [a for a in parser._actions if hasattr(a, "choices") and a.choices]
        subcommands = set()
        for action in actions:
            if isinstance(action.choices, dict):
                subcommands |= set(action.choices)
        self.assertEqual(subcommands, {"index", "query", "evaluate"})


class TestNoLegacyOrPausedImportClosure(unittest.TestCase):
    """Neither new module may reach `experiments/`, `pipeline/` or AQ4."""

    def test_the_new_modules_import_only_stdlib_and_the_permanent_namespace(self):
        import ast
        import sys

        allowed = set(sys.stdlib_module_names) | {"mtj_foundry"}
        for module in (pilot, pilot_cli):
            tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                roots = []
                if isinstance(node, ast.Import):
                    roots = [alias.name.split(".")[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    roots = [node.module.split(".")[0]]
                for root in roots:
                    with self.subTest(module=module.__name__, imports=root):
                        self.assertIn(root, allowed)

    def test_no_legacy_or_aq4_name_appears_in_the_new_modules(self):
        for module in (pilot, pilot_cli):
            source = Path(module.__file__).read_text(encoding="utf-8")
            for forbidden in ("tier_engine", "foundry_common", "foundry_shape_extractor",
                              "aq4", "AQ4", "experiments.", "pipeline."):
                with self.subTest(module=module.__name__, forbidden=forbidden):
                    self.assertNotIn(forbidden, source)
