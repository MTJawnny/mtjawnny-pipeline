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
import pathlib
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
ID_FOLD = "77777777-0000-0000-0000-000000000007"   # M3.R1: casefold != lower

#: A name whose Python `.casefold()` differs from its `.lower()`. U+00DF folds to
#: "ss" -- a case-fold EXPANSION, so the normalized key is two characters longer
#: than the printed name is. `.lower()` leaves the sharp s alone, so a browser
#: normalizing with `toLowerCase()` produces a key that is not in the index and
#: the card becomes unreachable by its own printed name. The selected corpus
#: happens to contain no such name today, which is exactly why the FIXTURE must.
FOLD_NAME = "Stra\u00dfburg Ritual"
FOLD_KEY = "strassburg ritual"        # == FOLD_NAME.strip().casefold()
FOLD_LOWER = "stra\u00dfburg ritual"  # == FOLD_NAME.strip().lower(), NOT a key


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
        # M3.R1: the normalization witness. Unassigned and eligible, so it moves
        # no retrieval or tie-block expectation -- only the name space.
        (ID_FOLD, FOLD_NAME, True, [_face(FOLD_NAME, "Gain 1 life.")], []),
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
        # The base fixture's own share, DERIVED here rather than typed, so adding
        # a card to the fixture moves the expectation with it instead of failing.
        coverage = self.index["conservation"]["coverage"]
        covered = coverage["corpus_ids_covered"]
        total = coverage["corpus_ids_total"]
        expected = ("a majority" if covered * 2 > total else
                    "a minority" if covered * 2 < total else "exactly half")
        self.assertIn(expected, " ".join(self.disclosure["points"]))
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


# ===========================================================================
# M3.R1 REPAIR A -- the browser reproduces `str.strip().casefold()`
# ===========================================================================

#: Built with `chr()` rather than pasted. A literal C0 control character in a
#: source file is invisible, survives no copy/paste reliably, and is exactly the
#: kind of thing an editor silently "fixes" -- so the witnesses that matter most
#: are the ones least safe to write literally.
_PY_STRIPS_JS_KEEPS = tuple(chr(c) for c in (0x1C, 0x1D, 0x1E, 0x1F, 0x85))
_JS_TRIMS_PY_KEEPS = "﻿"


class TestNormalizationTableIsDerivedAndFaithful(unittest.TestCase):
    """The table is a MEASUREMENT of Python, and it must agree with Python.

    These tests need no bundle: the table is the unit, and its contract is one
    sentence -- for every string, applying it equals `str.strip().casefold()`.
    """

    @classmethod
    def setUpClass(cls):
        cls.table = pilot.build_normalization_table()

    def test_it_reproduces_python_on_every_single_code_point(self):
        """Exhaustive over the whole scalar space. Cheap, and it is the only
        version of this check that cannot be accused of choosing its examples."""
        bad = []
        for code_point in range(0x110000):
            if 0xD800 <= code_point <= 0xDFFF:
                continue
            char = chr(code_point)
            if (pilot.normalize_with_table(char, self.table)
                    != char.strip().casefold()):
                bad.append(hex(code_point))
        self.assertEqual(bad, [])

    def test_per_code_point_folding_composes_over_multi_character_strings(self):
        """THE ASSUMPTION THE WHOLE DESIGN RESTS ON. Full case folding is
        context-free, so folding a string is folding each of its code points --
        unlike LOWERCASING, which has context rules (Greek final sigma). That is
        asserted here rather than believed, over a seeded sample drawn from the
        ranges where it could fail."""
        import random

        rng = random.Random(20260909)
        pool = [ord(c) for c in self.table["fold"]]
        pool += [ord(c) for c in self.table["strip"]]
        pool += [rng.randrange(0x110000) for _ in range(3000)]
        pool = [c for c in pool if not (0xD800 <= c <= 0xDFFF)]
        for _ in range(20000):
            probe = "".join(chr(rng.choice(pool))
                            for _ in range(rng.randint(1, 6)))
            if (pilot.normalize_with_table(probe, self.table)
                    != probe.strip().casefold()):
                self.fail(f"composition failed on {ascii(probe)}")

    def test_it_differs_from_lowercase_on_a_large_named_population(self):
        """If the table agreed with `lower()` everywhere it would be an elaborate
        no-op, and every other test in this class would still pass."""
        differing = [char for char, folded in self.table["fold"].items()
                     if char.lower() != folded]
        self.assertGreater(len(differing), 100)
        for char in ("ſ", "ß", "ﬁ", "ẞ"):
            with self.subTest(char=ascii(char)):
                self.assertIn(char, self.table["fold"])
                self.assertEqual(self.table["fold"][char], char.casefold())
                self.assertNotEqual(char.casefold(), char.lower())

    def test_the_strip_set_disagrees_with_javascript_trim_in_both_directions(self):
        """Neither strip set contains the other, which is why fixing only the
        case half could never have been the whole repair.

        Python strips U+001C-001F and U+0085, which JS `trim()` keeps; JS trims
        U+FEFF, which Python keeps. The SECOND direction is the one a
        'just strip more characters' fix gets wrong.
        """
        for char in _PY_STRIPS_JS_KEEPS:
            with self.subTest(char=ascii(char), direction="python strips, JS keeps"):
                self.assertIn(char, self.table["strip"])
        self.assertNotIn(_JS_TRIMS_PY_KEEPS, self.table["strip"])
        padded = _JS_TRIMS_PY_KEEPS + "sol ring"
        self.assertEqual(pilot.normalize_with_table(padded, self.table), padded)
        self.assertEqual(padded.strip().casefold(), padded)

    def test_nothing_in_the_table_is_hand_written(self):
        """Every entry must equal what Python says about that code point. A
        hand-added 'helpful' pair fails here, which is the guard against this
        repair quietly degenerating into a substitution list."""
        for char, folded in self.table["fold"].items():
            if folded != char.casefold() or folded == char:
                self.fail(f"fold entry {ascii(char)} is not derived")
        for char in self.table["strip"]:
            if char.strip() != "":
                self.fail(f"strip entry {ascii(char)} is not derived")

    def test_a_corrupted_table_is_caught_by_the_build_guard(self):
        """Negative control for `_verify_normalization`. Without it, the guard is
        a function that has never been shown to fail."""
        index = build_fixture_index()
        wrong_value = pilot.build_normalization_table()
        wrong_value["fold"]["ß"] = "z"
        with self.assertRaises(pilot.PilotError):
            pilot._verify_normalization(wrong_value, index)

        dropped = pilot.build_normalization_table()
        del dropped["fold"]["ß"]
        with self.assertRaises(pilot.PilotError):
            pilot._verify_normalization(dropped, index)

        no_strip = pilot.build_normalization_table()
        no_strip["strip"] = [c for c in no_strip["strip"]
                             if c not in _PY_STRIPS_JS_KEEPS]
        with self.assertRaises(pilot.PilotError):
            pilot._verify_normalization(no_strip, index)

    def test_a_table_that_strips_the_bom_is_caught(self):
        """The 'just use trim()' mistake, aimed at directly: a table that strips
        U+FEFF is closer to JavaScript and further from the accepted semantics,
        and the guard must reject it rather than reward it."""
        wrong = pilot.build_normalization_table()
        wrong["strip"] = list(wrong["strip"]) + [_JS_TRIMS_PY_KEEPS]
        with self.assertRaises(pilot.PilotError):
            pilot._verify_normalization(wrong, build_fixture_index())


class TestTheBundleCarriesTheNormalizationBoundary(PilotFixture):

    def test_the_emitted_table_matches_the_derived_one(self):
        emitted = self.emitted("data/normalization.json")
        derived = pilot.build_normalization_table()
        self.assertEqual(emitted["schema"], pilot.NORMALIZATION_SCHEMA)
        self.assertEqual(emitted["fold"], derived["fold"])
        self.assertEqual(emitted["strip"], derived["strip"])

    def test_the_emitted_table_resolves_the_fixtures_casefold_name(self):
        """END TO END over the bundle's own bytes: the printed name normalizes,
        through the EMITTED table, to a key that is in the EMITTED name index --
        and the `lower()` form is not a key at all."""
        emitted = self.emitted("data/normalization.json")
        names = self.emitted("data/names.json")["names"]
        self.assertNotEqual(FOLD_KEY, FOLD_LOWER)
        self.assertEqual(pilot.normalize_with_table(FOLD_NAME, emitted), FOLD_KEY)
        self.assertIn(FOLD_KEY, names)
        self.assertNotIn(FOLD_LOWER, names)
        positions = [row["oracle_id"] for row in self.index["cards"]]
        self.assertEqual([positions[i] for i in names[FOLD_KEY]], [ID_FOLD])

    def test_the_already_expanded_spelling_reaches_the_same_key(self):
        """`Strassburg Ritual` and the sharp-s spelling fold to ONE key, so both
        resolve to the same oracle_id. That is the accepted semantics reproduced,
        not a similarity feature: the two strings have the same normalized form,
        and the lookup that follows is still exact."""
        emitted = self.emitted("data/normalization.json")
        self.assertEqual(pilot.normalize_with_table("Strassburg Ritual", emitted),
                         pilot.normalize_with_table(FOLD_NAME, emitted))

    def test_the_browser_no_longer_uses_the_rejected_approximation(self):
        """`toLowerCase` and `trim` must be gone from the EXECUTABLE text.
        Comments explaining why they were removed are fine and are stripped
        first -- the same code-not-prose aim as the other controls here."""
        code = _javascript_code_only(
            (self.output / "assets" / "pilot.js").read_text(encoding="utf-8"))
        for forbidden in ("toLowerCase", ".trim(", "toUpperCase", "localeCompare"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, code)
        self.assertIn("normalization.strip", code)
        self.assertIn("normalization.fold", code)

    def test_the_browser_normalizer_mirrors_the_reference_algorithm(self):
        """A structural check that the two implementations were not allowed to
        drift into different algorithms. NOT a substitute for the headless-Chrome
        witness, which is what actually proves the browser behaves."""
        code = _javascript_code_only(
            (self.output / "assets" / "pilot.js").read_text(encoding="utf-8"))
        normalizer = code.split("function normalizeQuery")[1].split("\n}")[0]
        self.assertIn("Array.from", normalizer)       # code points, not UTF-16
        self.assertIn("table.strip.has", normalizer)
        self.assertIn("table.fold.get", normalizer)
        for forbidden in ("sort", "score", "includes("):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, normalizer)

    def test_normalization_stayed_a_lookup_boundary(self):
        """Ambiguity, prefix and substring behaviour are unchanged by the repair:
        still exact key lookup against the artifact's own list, in its order."""
        names = self.emitted("data/names.json")
        positions = [row["oracle_id"] for row in self.index["cards"]]
        self.assertEqual([positions[i] for i in names["names"]["twin card"]],
                         [ID_TWIN_A, ID_TWIN_B])
        self.assertEqual(names["ambiguous_names"], 1)
        for key, ids in self.index["name_index"].items():
            with self.subTest(name=key):
                self.assertEqual([positions[i] for i in names["names"][key]], ids)

    def test_the_table_is_emitted_as_a_manifest_covered_bundle_file(self):
        recorded = {entry["path"] for entry in self.manifest["files"]}
        self.assertIn("data/normalization.json", recorded)


# ===========================================================================
# M3.R1 REPAIR B -- a malformed prior manifest fails closed, deleting nothing
# ===========================================================================

class TestMalformedPriorManifestFailsClosed(PilotFixture):
    """A schema-correct manifest is not a well-formed one.

    The rejected candidate checked `schema` and then indexed `entry["path"]`, so
    a prior bundle carrying `"files": [{}]` raised a raw `KeyError` -- which
    escapes `pilot_cli`'s declared contract, because that handler catches
    `FoundryRuntimeError` and nothing else. The operator got a traceback where
    the contract promises one `STOP -- ...` line.

    Every case below asserts BOTH halves: the refusal is a `PilotOutputError`,
    AND nothing was deleted. The second half is the one that matters -- a
    validation that runs inside the delete loop would raise correctly and still
    leave a half-erased bundle behind.
    """

    def _prior_bundle(self, tmp):
        """A real, valid bundle, plus a snapshot of its bytes to compare against."""
        out = pathlib.Path(tmp) / "bundle"
        pilot.build(self.index_path, self.evaluation_path, out)
        before = {str(p.relative_to(out)): p.read_bytes()
                  for p in out.rglob("*") if p.is_file()}
        return out, before

    def _still_intact(self, out, before):
        after = {str(p.relative_to(out)): p.read_bytes()
                 for p in out.rglob("*") if p.is_file()}
        self.assertEqual(sorted(before), sorted(after),
                         "files were deleted before the manifest was validated")
        for name in before:
            self.assertEqual(before[name], after[name], name)

    def _corrupt(self, out, mutate):
        manifest_path = out / pilot.MANIFEST_NAME
        document = json.loads(manifest_path.read_text(encoding="utf-8"))
        mutate(document)
        manifest_path.write_text(json.dumps(document), encoding="utf-8")

    def test_case_1_files_holding_an_empty_object_is_refused(self):
        """Manager V's own example: correct schema, `files: [{}]`."""
        with TemporaryDirectory() as tmp:
            out, before = self._prior_bundle(tmp)
            self._corrupt(out, lambda d: d.__setitem__("files", [{}]))
            before[pilot.MANIFEST_NAME] = (out / pilot.MANIFEST_NAME).read_bytes()
            with self.assertRaises(pilot.PilotOutputError) as caught:
                pilot.build(self.index_path, self.evaluation_path, out)
            self.assertIn("no 'path'", str(caught.exception))
            self._still_intact(out, before)

    def test_case_2_a_non_list_files_value_is_refused(self):
        with TemporaryDirectory() as tmp:
            for value in ({}, "data/cards.json", 7, None):
                out, before = self._prior_bundle(pathlib.Path(tmp) / str(id(value)))
                self._corrupt(out, lambda d, v=value: d.__setitem__("files", v))
                before[pilot.MANIFEST_NAME] = (out / pilot.MANIFEST_NAME).read_bytes()
                with self.subTest(files=value):
                    with self.assertRaises(pilot.PilotOutputError) as caught:
                        pilot.build(self.index_path, self.evaluation_path, out)
                    self.assertIn("not a", str(caught.exception))
                    self._still_intact(out, before)

    def test_an_entry_that_is_not_an_object_is_refused(self):
        with TemporaryDirectory() as tmp:
            out, before = self._prior_bundle(tmp)
            self._corrupt(out, lambda d: d.__setitem__(
                "files", [d["files"][0], "data/cards.json"]))
            before[pilot.MANIFEST_NAME] = (out / pilot.MANIFEST_NAME).read_bytes()
            with self.assertRaises(pilot.PilotOutputError) as caught:
                pilot.build(self.index_path, self.evaluation_path, out)
            self.assertIn("files[1]", str(caught.exception))
            self._still_intact(out, before)

    def test_a_non_string_or_empty_path_is_refused(self):
        for bad in (None, 12, ["data/cards.json"], ""):
            with TemporaryDirectory() as tmp:
                out, before = self._prior_bundle(tmp)
                self._corrupt(out, lambda d, b=bad: d["files"][0].__setitem__("path", b))
                before[pilot.MANIFEST_NAME] = (out / pilot.MANIFEST_NAME).read_bytes()
                with self.subTest(path=bad):
                    with self.assertRaises(pilot.PilotOutputError):
                        pilot.build(self.index_path, self.evaluation_path, out)
                    self._still_intact(out, before)

    def test_a_path_escaping_the_output_root_is_refused_before_any_deletion(self):
        """A prior manifest is caller-controlled data, so it must not be able to
        direct a delete outside the directory it lives in. The containment check
        runs in the SAME validating pass, before the first unlink."""
        with TemporaryDirectory() as tmp:
            out, before = self._prior_bundle(tmp)
            bystander = pathlib.Path(tmp) / "not-mine.txt"
            bystander.write_text("untouched", encoding="utf-8")
            self._corrupt(out, lambda d: d["files"].append(
                {"path": "../not-mine.txt", "sha256": "0" * 64, "byte_size": 9}))
            before[pilot.MANIFEST_NAME] = (out / pilot.MANIFEST_NAME).read_bytes()
            with self.assertRaises(pilot.PilotOutputError):
                pilot.build(self.index_path, self.evaluation_path, out)
            self.assertEqual(bystander.read_text(encoding="utf-8"), "untouched")
            self._still_intact(out, before)

    def test_validation_precedes_deletion_even_when_the_bad_entry_is_last(self):
        """THE ORDERING TEST, and the reason validation is a separate pass. If the
        check ran inside the delete loop, every entry before the malformed one
        would already be gone -- a half-erased bundle whose manifest no longer
        describes it. The malformed entry is put LAST on purpose."""
        with TemporaryDirectory() as tmp:
            out, before = self._prior_bundle(tmp)
            self._corrupt(out, lambda d: d["files"].append({"sha256": "0" * 64}))
            before[pilot.MANIFEST_NAME] = (out / pilot.MANIFEST_NAME).read_bytes()
            with self.assertRaises(pilot.PilotOutputError):
                pilot.build(self.index_path, self.evaluation_path, out)
            self._still_intact(out, before)

    def test_case_3_the_installed_cli_surfaces_it_as_stop_and_exit_1(self):
        """The whole point of the repair: this state must reach the operator
        through the declared contract -- exit 1, exactly one `STOP -- ...` line
        on stderr, nothing on stdout -- and not as a traceback."""
        import contextlib
        import io

        with TemporaryDirectory() as tmp:
            out, before = self._prior_bundle(tmp)
            self._corrupt(out, lambda d: d.__setitem__("files", [{}]))
            before[pilot.MANIFEST_NAME] = (out / pilot.MANIFEST_NAME).read_bytes()
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                status = pilot_cli.main(["--index", str(self.index_path),
                                         "--evaluation", str(self.evaluation_path),
                                         "--output", str(out)])
            self.assertEqual(status, 1)
            self.assertEqual(stdout.getvalue(), "")
            lines = stderr.getvalue().splitlines()
            self.assertEqual(len(lines), 1)
            self.assertTrue(lines[0].startswith("STOP — "))
            self._still_intact(out, before)

    def test_case_4_a_valid_prior_bundle_still_replaces_deterministically(self):
        """The repair must not have made replacement stricter than the documented
        rule. A real prior bundle is still replaced, and the result is byte-equal
        to a build into a fresh directory."""
        with TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp) / "bundle"
            first = pilot.build(self.index_path, self.evaluation_path, out)
            second = pilot.build(self.index_path, self.evaluation_path, out)
            self.assertEqual(first, second)
            fresh = pathlib.Path(tmp) / "fresh"
            pilot.build(self.index_path, self.evaluation_path, fresh)
            replaced = {str(p.relative_to(out)): p.read_bytes()
                        for p in out.rglob("*") if p.is_file()}
            clean = {str(p.relative_to(fresh)): p.read_bytes()
                     for p in fresh.rglob("*") if p.is_file()}
            self.assertEqual(sorted(replaced), sorted(clean))
            for name in sorted(clean):
                with self.subTest(file=name):
                    self.assertEqual(replaced[name], clean[name])
            pilot.verify_manifest(out)

    def test_the_validator_uses_no_generic_catch(self):
        """`except (KeyError, TypeError)` around the consumption would also
        swallow a defect in this module and report it as a malformed input --
        the wrong story, told confidently. Each condition is tested positively,
        and that is checked structurally rather than by reading the prose."""
        import ast

        source = pathlib.Path(pilot.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        target = next(node for node in ast.walk(tree)
                      if isinstance(node, ast.FunctionDef)
                      and node.name == "_validated_replacement_targets")
        self.assertEqual([h for h in ast.walk(target)
                          if isinstance(h, ast.ExceptHandler)], [])

    def test_the_validator_does_not_check_fields_replacement_never_reads(self):
        """Refusing a bundle for a missing `sha256` would reject bundles that are
        fine. The validator's scope is exactly what the deletion consumes."""
        with TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp) / "bundle"
            pilot.build(self.index_path, self.evaluation_path, out)
            def drop_unconsumed_fields(document):
                for entry in document["files"]:
                    entry.pop("sha256", None)
                    entry.pop("byte_size", None)

            self._corrupt(out, drop_unconsumed_fields)
            pilot.build(self.index_path, self.evaluation_path, out)
            pilot.verify_manifest(out)


# ===========================================================================
# M3.R2 -- the last two malformed-prior-manifest shapes
# ===========================================================================

class TestMissingAndSelfListedFilesFailClosed(PilotFixture):
    """Two shapes that escaped R1's first-pass validator, from V `5596543305`.

    Both are the same mistake made twice: a value the replacement CONSUMES was
    accepted on a weaker test than the consumption needs. Neither is a browser,
    retrieval or artifact concern -- they are local shape validation, and the
    proof for each is the same pair of claims R1 established: the refusal is a
    `PilotOutputError`, and NOTHING on disk moved.
    """

    def _prior_bundle(self, tmp):
        out = pathlib.Path(tmp) / "bundle"
        pilot.build(self.index_path, self.evaluation_path, out)
        return out

    def _snapshot(self, out):
        """Every byte under the directory, INCLUDING the corrupted manifest.

        The manifest is deliberately in the snapshot. A refusal that rewrote or
        removed the malformed manifest would be a mutation of caller state on a
        path that is supposed to change nothing, and a snapshot that skipped it
        could not see that.
        """
        return {str(p.relative_to(out)): p.read_bytes()
                for p in out.rglob("*") if p.is_file()}

    def _assert_unchanged(self, out, before):
        after = self._snapshot(out)
        self.assertEqual(sorted(before), sorted(after),
                         "a file was created or deleted by a refusal")
        for name in sorted(before):
            with self.subTest(file=name):
                self.assertEqual(before[name], after[name])

    def _corrupt(self, out, mutate):
        manifest_path = out / pilot.MANIFEST_NAME
        document = json.loads(manifest_path.read_text(encoding="utf-8"))
        mutate(document)
        manifest_path.write_text(json.dumps(document), encoding="utf-8")

    def _cli(self, out):
        import contextlib
        import io

        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = pilot_cli.main(["--index", str(self.index_path),
                                     "--evaluation", str(self.evaluation_path),
                                     "--output", str(out)])
        return status, stdout.getvalue(), stderr.getvalue()

    # ---- Repair A: `files` must be PRESENT -------------------------------

    def test_a_manifest_with_no_files_key_is_refused(self):
        """`previous.get("files", [])` read an ABSENT field as an empty bundle --
        a confident empty answer to a question the document never answered."""
        with TemporaryDirectory() as tmp:
            out = self._prior_bundle(tmp)
            self._corrupt(out, lambda d: d.pop("files"))
            before = self._snapshot(out)
            with self.assertRaises(pilot.PilotOutputError) as caught:
                pilot.build(self.index_path, self.evaluation_path, out)
            self.assertIn("no 'files'", str(caught.exception))
            self._assert_unchanged(out, before)

    def test_the_missing_files_refusal_reaches_the_cli_contract(self):
        with TemporaryDirectory() as tmp:
            out = self._prior_bundle(tmp)
            self._corrupt(out, lambda d: d.pop("files"))
            before = self._snapshot(out)
            status, stdout, stderr = self._cli(out)
            self.assertEqual(status, 1)
            self.assertEqual(stdout, "")
            self.assertEqual(len(stderr.splitlines()), 1)
            self.assertTrue(stderr.startswith("STOP — "))
            self._assert_unchanged(out, before)

    def test_absent_files_and_empty_files_are_not_the_same_state(self):
        """The distinction the defect erased, asserted directly. An EMPTY list is
        a legitimate statement ('this bundle recorded no files') and is accepted;
        an ABSENT field is a manifest that does not describe its directory."""
        with TemporaryDirectory() as tmp:
            out = self._prior_bundle(tmp)
            self._corrupt(out, lambda d: d.__setitem__("files", []))
            manifest_path = out / pilot.MANIFEST_NAME
            document = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(
                pilot._validated_replacement_targets(document, manifest_path, out),
                [])
            del document["files"]
            with self.assertRaises(pilot.PilotOutputError):
                pilot._validated_replacement_targets(document, manifest_path, out)

    def test_the_missing_files_hole_would_have_orphaned_unrecorded_files(self):
        """WHY IT MATTERED, demonstrated rather than argued.

        With `files` absent and the field defaulted to `[]`, replacement deleted
        nothing, removed the manifest, and wrote the new bundle over the top --
        leaving an unrecorded file underneath a manifest that never mentions it,
        and exiting 0. The repaired code refuses instead, so the stray file is
        still there to be reported by `verify_manifest` rather than buried.
        """
        with TemporaryDirectory() as tmp:
            out = self._prior_bundle(tmp)
            orphan = out / "data" / "text" / "zz.json"
            orphan.write_text("{}", encoding="utf-8")
            self._corrupt(out, lambda d: d.pop("files"))
            with self.assertRaises(pilot.PilotOutputError):
                pilot.build(self.index_path, self.evaluation_path, out)
            self.assertTrue(orphan.is_file())

    # ---- Repair B: `files` may not list the manifest ---------------------

    def test_a_manifest_listing_itself_is_refused(self):
        """Containment alone accepts `manifest.json` -- it IS inside the output
        root. The stale loop would unlink it, and the unconditional
        `manifest_path.unlink()` two lines later would raise a raw
        `FileNotFoundError` straight past the CLI's typed boundary."""
        with TemporaryDirectory() as tmp:
            out = self._prior_bundle(tmp)
            self._corrupt(out, lambda d: d["files"].append(
                {"path": pilot.MANIFEST_NAME, "sha256": "0" * 64, "byte_size": 1}))
            before = self._snapshot(out)
            with self.assertRaises(pilot.PilotOutputError) as caught:
                pilot.build(self.index_path, self.evaluation_path, out)
            self.assertIn("resolves to the manifest itself", str(caught.exception))
            self._assert_unchanged(out, before)

    def test_it_is_not_a_raw_filenotfounderror(self):
        """Named explicitly because `PilotOutputError` is not a subclass of it --
        so `assertRaises(PilotOutputError)` above already excludes it -- but the
        review's finding was about the EXCEPTION TYPE reaching the operator, and
        that deserves its own assertion rather than an inference."""
        with TemporaryDirectory() as tmp:
            out = self._prior_bundle(tmp)
            self._corrupt(out, lambda d: d["files"].append(
                {"path": pilot.MANIFEST_NAME}))
            try:
                pilot.build(self.index_path, self.evaluation_path, out)
            except pilot.PilotOutputError:
                pass
            except Exception as error:            # noqa: BLE001 - the assertion
                self.fail(f"raised {type(error).__name__}, not PilotOutputError")
            else:
                self.fail("no refusal was raised")

    def test_an_indirect_spelling_of_the_manifest_is_also_refused(self):
        """The check is on the RESOLVED path, not the string, so a manifest
        cannot smuggle itself in by spelling. A string comparison against
        `"manifest.json"` would pass every one of these."""
        for spelling in ("./manifest.json", "data/../manifest.json",
                         "data/text/../../manifest.json"):
            with TemporaryDirectory() as tmp:
                out = self._prior_bundle(tmp)
                self._corrupt(out, lambda d, s=spelling: d["files"].append(
                    {"path": s}))
                before = self._snapshot(out)
                with self.subTest(spelling=spelling):
                    with self.assertRaises(pilot.PilotOutputError):
                        pilot.build(self.index_path, self.evaluation_path, out)
                    self._assert_unchanged(out, before)

    def test_the_self_listed_refusal_reaches_the_cli_contract(self):
        with TemporaryDirectory() as tmp:
            out = self._prior_bundle(tmp)
            self._corrupt(out, lambda d: d["files"].append(
                {"path": pilot.MANIFEST_NAME}))
            before = self._snapshot(out)
            status, stdout, stderr = self._cli(out)
            self.assertEqual(status, 1)
            self.assertEqual(stdout, "")
            self.assertEqual(len(stderr.splitlines()), 1)
            self.assertTrue(stderr.startswith("STOP — "))
            self._assert_unchanged(out, before)

    def test_a_self_listing_placed_last_still_deletes_nothing(self):
        """The ordering property R1 established, re-asserted for the new rule:
        the malformed entry is LAST, so a check that ran inside the delete loop
        would already have erased every real file before reaching it."""
        with TemporaryDirectory() as tmp:
            out = self._prior_bundle(tmp)
            self._corrupt(out, lambda d: d["files"].append(
                {"path": pilot.MANIFEST_NAME}))
            before = self._snapshot(out)
            recorded = len(json.loads(
                (out / pilot.MANIFEST_NAME).read_text(encoding="utf-8"))["files"])
            with self.assertRaises(pilot.PilotOutputError):
                pilot.build(self.index_path, self.evaluation_path, out)
            self._assert_unchanged(out, before)
            # The property this test needs: the bad entry was preceded by REAL
            # targets, so a lazy check inside the delete loop would have erased
            # them first. Derived from the manifest rather than guessed -- the
            # first draft asserted `len(before) > 100`, which was a guess about
            # the fixture (it has 20 files) and not a statement about ordering.
            self.assertGreater(recorded, 1)

    # ---- nothing that already worked was weakened ------------------------

    def test_the_r1_validations_are_all_still_enforced(self):
        """R2 must not have traded one refusal for another. Every shape R1
        refused is re-checked here against the repaired validator."""
        with TemporaryDirectory() as tmp:
            out = self._prior_bundle(tmp)
            manifest_path = out / pilot.MANIFEST_NAME
            valid = json.loads(manifest_path.read_text(encoding="utf-8"))
            for label, mutate in [
                ("non-list files", lambda d: d.__setitem__("files", {})),
                ("entry not an object",
                 lambda d: d["files"].append("data/cards.json")),
                ("entry without path", lambda d: d["files"].append({})),
                ("path not a string",
                 lambda d: d["files"].append({"path": 7})),
                ("empty path", lambda d: d["files"].append({"path": ""})),
                ("path escaping the root",
                 lambda d: d["files"].append({"path": "../escaped.txt"})),
            ]:
                document = json.loads(json.dumps(valid))
                mutate(document)
                with self.subTest(shape=label):
                    with self.assertRaises(pilot.PilotOutputError):
                        pilot._validated_replacement_targets(
                            document, manifest_path, out)

    def test_a_valid_prior_bundle_still_replaces_deterministically(self):
        """The acceptance case, re-proved after tightening: a real prior bundle
        is still replaced, and the result is byte-equal to a fresh build."""
        with TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp) / "bundle"
            first = pilot.build(self.index_path, self.evaluation_path, out)
            second = pilot.build(self.index_path, self.evaluation_path, out)
            self.assertEqual(first, second)
            fresh = pathlib.Path(tmp) / "fresh"
            pilot.build(self.index_path, self.evaluation_path, fresh)
            replaced = {str(p.relative_to(out)): p.read_bytes()
                        for p in out.rglob("*") if p.is_file()}
            clean = {str(p.relative_to(fresh)): p.read_bytes()
                     for p in fresh.rglob("*") if p.is_file()}
            self.assertEqual(sorted(replaced), sorted(clean))
            for name in sorted(clean):
                with self.subTest(file=name):
                    self.assertEqual(replaced[name], clean[name])
            pilot.verify_manifest(out)

    def test_the_validator_still_has_no_generic_catch(self):
        import ast

        tree = ast.parse(pathlib.Path(pilot.__file__).read_text(encoding="utf-8"))
        target = next(node for node in ast.walk(tree)
                      if isinstance(node, ast.FunctionDef)
                      and node.name == "_validated_replacement_targets")
        self.assertEqual([h for h in ast.walk(target)
                          if isinstance(h, ast.ExceptHandler)], [])


class TestTheR1NormalizationBoundaryIsUntouched(PilotFixture):
    """R2 must not have disturbed the accepted R1 repair.

    Confirmation only, per the active task -- the Unicode design is closed and is
    not re-derived or re-argued here. These assert that the emitted bundle still
    carries the same boundary and that the shipped JavaScript still consumes it.
    """

    def test_the_bundle_still_emits_the_derived_normalization_table(self):
        emitted = self.emitted("data/normalization.json")
        derived = pilot.build_normalization_table()
        self.assertEqual(emitted["schema"], pilot.NORMALIZATION_SCHEMA)
        self.assertEqual(emitted["fold"], derived["fold"])
        self.assertEqual(emitted["strip"], derived["strip"])
        self.assertIn("data/normalization.json",
                      {entry["path"] for entry in self.manifest["files"]})

    def test_the_shipped_javascript_still_consumes_it(self):
        code = _javascript_code_only(
            (self.output / "assets" / "pilot.js").read_text(encoding="utf-8"))
        self.assertIn("normalization.strip", code)
        self.assertIn("normalization.fold", code)
        self.assertNotIn("toLowerCase", code)
        self.assertNotIn(".trim(", code)
