"""Path E milestone 1 — the read-only runtime composition boundary.

WHAT THIS SUITE IS FOR, AND WHAT IT DELIBERATELY DOES NOT REPEAT.

The capabilities underneath this boundary already have their own suites, and
those suites already prove the properties they own: `test_corpus_capability`
proves the loader is VALUE_EXACT with its oracle including duplicate-id and
all-face behaviour, `test_codebook_store` proves the schema gate and the A13
write protocol, `test_codebook_capability` proves lint. Re-asserting any of that
here would be duplication that feels safer and measures nothing new.

What is NEW at this boundary, and therefore what is tested here:

* that a composition exists at all, is importable, and runs from a working
  directory unrelated to the repository with nothing on the path;
* that every declared-identity check REFUSES rather than reporting;
* that a failure produces no success-shaped report on stdout;
* that eligibility PARTITIONS the population instead of filtering it;
* that duplicate-id and all-face semantics survive the composition, measured at
  the report the boundary actually emits;
* that coverage accounting keeps memberships and cards apart, and accounts for
  member ids the corpus does not contain instead of dropping them.

FIXTURES ARE FOR CONTROLLED FAILURE. Card data is gitignored and stays out of
git, so the acceptance witness against the real selected codebook and the pinned
corpus is a separate, explicit step recorded in the Worker result. The
full-corpus differentials below skip without that data and say so; they are not a
substitute for the acceptance run and it is not a substitute for them.
"""

from __future__ import annotations

import gzip
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT, SRC

from mtj_foundry import cli, codebook_store, corpus, runtime
from mtj_foundry.paths import ProjectPaths

EXPERIMENTS = REPO_ROOT / "experiments"
REAL_PATHS = ProjectPaths.for_root(REPO_ROOT)
REAL_CORPUS = REAL_PATHS.legacy_oracle_cards
REAL_CODEBOOK = REAL_PATHS.legacy_codebook_json
CLEAN_ENV = {"PATH": "/usr/bin:/bin"}   # deliberately no PYTHONPATH


# ---------------------------------------------------------------------------
# A minimal but STRUCTURALLY REAL fixture pair.
#
# The codebook is a genuine `foundry-codebook/2` document that passes the real
# lint -- not a stub shaped like one. A fixture that could not survive lint would
# make every failure test below ambiguous: a refusal could mean the guard fired
# or merely that the fixture was invalid.
# ---------------------------------------------------------------------------

ID_A = "00000000-0000-4000-8000-000000000001"
ID_B = "00000000-0000-4000-8000-000000000002"
ID_C = "00000000-0000-4000-8000-000000000003"   # in the codebook, NOT in the corpus


def assertion(quote: str = "whenever this creature enters, draw a card"):
    """One `class: human` assertion, in ASSERTION_KEY_ORDER, citing a ratified
    `source_ref` family. Built to survive the REAL lint, not merely to look like
    a member: a fixture lint rejects makes every failure test below ambiguous."""
    return {
        "class": "human",
        "source_ref": "batch-1",
        "quote": quote,
        "corpus_ref": "2026-07-04",
        "evidence_status": "quoted",
        "locality": [0, 0],
    }


def axis(status: str, *member_ids: str) -> dict:
    """A /2 axis. Members are sorted by oracle_id and carry NO tier, which is
    what `expected_tier` demands of a stack holding a human assertion."""
    return {
        "status": status,
        "members": [{"oracle_id": oid, "assertions": [assertion()]}
                    for oid in sorted(member_ids)],
    }


def fixture_codebook() -> dict:
    return {
        "schema": codebook_store.codebook.SCHEMA_V2,
        "axes": {
            "rule:alpha": axis("active", ID_A, ID_C),
            "rule:beta": axis("active", ID_A),
            "rule:gamma": axis("killed", ID_B),
        },
    }


LEGAL_CARD = {
    "oracle_id": ID_A,
    "name": "Fixture Legal",
    "oracle_text": "Draw a card.",
    "type_line": "Sorcery",
    "legalities": {"standard": "not_legal", "vintage": "restricted"},
}
ILLEGAL_CARD = {
    "oracle_id": ID_B,
    "name": "Fixture Nowhere Legal",
    "oracle_text": "This card is not legal anywhere.",
    "type_line": "Card",
    "legalities": {"standard": "not_legal", "vintage": "banned"},
}
DFC_CARD = {
    "oracle_id": "00000000-0000-4000-8000-000000000004",
    "name": "Fixture Front // Fixture Back",
    "oracle_text": "",
    "legalities": {"modern": "legal"},
    "card_faces": [
        {"name": "Fixture Front", "oracle_text": "Front text.", "type_line": "Creature"},
        {"name": "Fixture Back", "oracle_text": "Back text.", "type_line": "Creature"},
    ],
}


def build_fixture_root(tmp: Path, *, codebook_document=None, corpus_records=None,
                       corpus_name: str = "oracle-cards.jsonl.gz",
                       name: str = "root") -> Path:
    """A repository-shaped root carrying exactly the files the runtime reads.

    Built at the LAYOUT OWNER's paths, never at literals of this test's own: a
    fixture that spelled the layout itself would pass while the shipped default
    pointed somewhere else.

    `name` exists because a test may need SEVERAL roots at once, each broken in a
    different way. Reusing one directory silently repaired the earlier roots --
    the last build won, and four deliberate failures reported success.
    """
    root = tmp / name
    paths = ProjectPaths.for_root(root)
    document = fixture_codebook() if codebook_document is None else codebook_document
    payload = codebook_store.serialize(document).encode("utf-8")

    paths.legacy_codebook_json.parent.mkdir(parents=True, exist_ok=True)
    paths.legacy_codebook_json.write_bytes(payload)

    selector = {
        "schema": runtime.AUTHORITY_SCHEMA,
        "snapshot_id": "fixture-snapshot",
        "sha256": __import__("hashlib").sha256(payload).hexdigest(),
        "byte_size": len(payload),
        "codebook_schema": codebook_store.codebook.SCHEMA_V2,
        "corpus_ref": "2026-07-04",
    }
    paths.codebook_authority_selector.parent.mkdir(parents=True, exist_ok=True)
    paths.codebook_authority_selector.write_text(
        json.dumps(selector, indent=2) + "\n", encoding="utf-8")

    records = ([LEGAL_CARD, ILLEGAL_CARD, DFC_CARD] if corpus_records is None
               else corpus_records)
    corpus_path = paths.legacy_oracle_cards.parent / corpus_name
    corpus_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(corpus_path, "wt", encoding="utf-8") as handle:
        for record in records:
            handle.write(record if isinstance(record, str) else json.dumps(record))
            handle.write("\n")
    return root


def lock_for(root: Path, *, corpus_name: str = "oracle-cards.jsonl.gz",
             sha256=None, content_sha256=None, status="PROPOSED_PILOT_INPUT_LOCK",
             provenance=None) -> Path:
    paths = ProjectPaths.for_root(root)
    corpus_path = paths.legacy_oracle_cards.parent / corpus_name
    measured = runtime.measure_file(corpus_path)
    document = {
        "schema": runtime.INPUT_LOCK_SCHEMA,
        "status": status,
        "ratified": False,
        "corpus": {
            "path": corpus_path.relative_to(root).as_posix(),
            "sha256": sha256 or measured.sha256,
            "byte_size": measured.byte_size,
            "content_sha256": content_sha256,
            "provenance": provenance or {"statement": "fixture bytes written by this test"},
        },
    }
    if content_sha256 is None:
        document["corpus"].pop("content_sha256")
    lock_path = root / "refoundation" / "path-e" / "input-lock.json"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return lock_path


class RuntimeFixtureCase(unittest.TestCase):
    """A fresh fixture root per test. Nothing here reads repository data."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self._roots = 0
        self.addCleanup(self._tmp.cleanup)

    def build(self, **kwargs) -> Path:
        kwargs.setdefault("name", f"root{self._roots}")
        self._roots += 1
        return build_fixture_root(self.tmp, **kwargs)

    def report(self, root: Path, **kwargs) -> dict:
        return runtime.run(root, lock_path=str(lock_for(root)), **kwargs)


# ===========================================================================
# 1. THE COMPOSITION EXISTS AND SUCCEEDS
# ===========================================================================

class TestSuccessfulComposition(RuntimeFixtureCase):

    def test_a_verified_run_returns_a_versioned_report(self):
        report = self.report(self.build())
        self.assertEqual(report["schema"], runtime.REPORT_SCHEMA)
        self.assertEqual(report["codebook_lint"]["result"], "PASS")
        self.assertEqual(report["scope"]["report_is"],
                         "DERIVED_EVIDENCE_NOT_AUTHORITY")

    def test_the_report_renders_deterministically(self):
        root = self.build()
        lock = str(lock_for(root))
        first = runtime.render_report(runtime.run(root, lock_path=lock))
        second = runtime.render_report(runtime.run(root, lock_path=lock))
        self.assertEqual(first, second)
        self.assertTrue(first.endswith("}\n"))

    def test_the_report_carries_both_measured_input_identities(self):
        root = self.build()
        report = self.report(root)
        paths = ProjectPaths.for_root(root)
        self.assertEqual(report["inputs"]["codebook"]["measured_sha256"],
                         runtime.measure_file(paths.legacy_codebook_json).sha256)
        self.assertEqual(report["inputs"]["corpus"]["measured_sha256"],
                         runtime.measure_file(paths.legacy_oracle_cards).sha256)
        self.assertTrue(report["inputs"]["codebook"]["matches_selected_authority"])

    def test_local_verification_is_not_reported_as_remote_durability(self):
        """C7.1's distinction, kept visible in the artifact that carries it."""
        report = self.report(self.build())
        self.assertFalse(report["inputs"]["codebook"]["remote_durability_verified"])
        self.assertIn("LOCAL", report["inputs"]["codebook"]["verification"])

    def test_a_proposed_lock_status_is_carried_not_promoted(self):
        root = self.build()
        report = runtime.run(root, lock_path=str(lock_for(root)))
        self.assertEqual(report["inputs"]["corpus"]["identity_status"],
                         "PROPOSED_PILOT_INPUT_LOCK")

    def test_the_content_digest_is_measured_only_when_one_was_declared(self):
        root = self.build()
        without = runtime.run(root, lock_path=str(lock_for(root)))
        self.assertIsNone(without["inputs"]["corpus"]["measured_content_sha256"])

        paths = ProjectPaths.for_root(root)
        content = runtime.measure_gzip_content(paths.legacy_oracle_cards)
        with_declared = runtime.run(
            root, lock_path=str(lock_for(root, content_sha256=content)))
        self.assertEqual(
            with_declared["inputs"]["corpus"]["measured_content_sha256"], content)

    def test_the_payload_carries_no_absolute_machine_path(self):
        """Two runs from different checkouts must be comparable, so the root and
        every path inside it stay repository-relative."""
        root = self.build()
        rendered = runtime.render_report(self.report(root))
        self.assertNotIn(str(root), rendered)
        self.assertNotIn(str(self.tmp), rendered)


# ===========================================================================
# 2. UNRELATED CWD, NO PYTHONPATH, NO REPOSITORY UNDER FOOT
# ===========================================================================

class TestItRunsFromAnUnrelatedWorkingDirectory(RuntimeFixtureCase):
    """EXPLICIT_SOURCE_LAYOUT is what these use, and the contract says so.

    A real INSTALLED_PACKAGE witness cannot run offline in the committed suite
    (`refoundation/PACKAGE-EXECUTION-CONTRACT.yaml`), so what is proven here is
    the CWD INDEPENDENCE of the composition, not the install. The install witness
    is a separate explicit step and is recorded as Worker-local evidence.
    """

    def _run(self, root: Path, cwd: Path, argv):
        env = dict(CLEAN_ENV)
        env["PYTHONPATH"] = str(SRC)
        return subprocess.run([sys.executable, "-m", "mtj_foundry.cli", *argv],
                              cwd=cwd, capture_output=True, text=True, env=env)

    def test_the_command_succeeds_from_a_directory_that_is_not_a_repository(self):
        root = self.build()
        lock = lock_for(root)
        outside = self.tmp / "elsewhere"
        outside.mkdir()
        self.assertFalse((outside / ".git").exists())
        proc = self._run(root, outside,
                         ["--root", str(root), "--input-lock", str(lock)])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["schema"], runtime.REPORT_SCHEMA)

    def test_the_same_command_from_two_different_cwds_is_byte_identical(self):
        """The cwd must not reach any value in the payload."""
        root = self.build()
        lock = lock_for(root)
        one = self.tmp / "cwd-one"
        two = self.tmp / "cwd-two" / "deeper"
        one.mkdir()
        two.mkdir(parents=True)
        argv = ["--root", str(root), "--input-lock", str(lock)]
        first = self._run(root, one, argv)
        second = self._run(root, two, argv)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stdout, second.stdout)

    def test_a_relative_root_is_anchored_at_construction_not_at_read_time(self):
        """`ProjectPaths` normalizes once; the composition must not undo that."""
        root = self.build()
        lock = lock_for(root)
        proc = self._run(root, root.parent,
                         ["--root", root.name, "--input-lock", str(lock)])
        self.assertEqual(proc.returncode, 0, proc.stderr)


# ===========================================================================
# 3. EVERY DECLARED-IDENTITY CHECK REFUSES
# ===========================================================================

class TestInputVerificationRefuses(RuntimeFixtureCase):

    def test_a_codebook_sha_mismatch_raises_and_names_both_values(self):
        root = self.build()
        selector_path = ProjectPaths.for_root(root).codebook_authority_selector
        selector = json.loads(selector_path.read_text())
        selector["sha256"] = "0" * 64
        selector_path.write_text(json.dumps(selector), encoding="utf-8")
        with self.assertRaises(runtime.InputIdentityError) as caught:
            self.report(root)
        self.assertEqual(caught.exception.field, "sha256")
        self.assertIn("0" * 64, str(caught.exception))

    def test_a_codebook_size_mismatch_raises_before_the_digest_is_compared(self):
        root = self.build()
        selector_path = ProjectPaths.for_root(root).codebook_authority_selector
        selector = json.loads(selector_path.read_text())
        selector["byte_size"] = selector["byte_size"] + 1
        selector_path.write_text(json.dumps(selector), encoding="utf-8")
        with self.assertRaises(runtime.InputIdentityError) as caught:
            self.report(root)
        self.assertEqual(caught.exception.field, "byte_size")

    def test_a_corpus_sha_mismatch_raises(self):
        root = self.build()
        lock = lock_for(root, sha256="f" * 64)
        with self.assertRaises(runtime.InputIdentityError) as caught:
            runtime.run(root, lock_path=str(lock))
        self.assertEqual(caught.exception.what, "selected corpus")

    def test_a_corpus_content_digest_mismatch_raises(self):
        root = self.build()
        lock = lock_for(root, content_sha256="a" * 64)
        with self.assertRaises(runtime.InputIdentityError) as caught:
            runtime.run(root, lock_path=str(lock))
        self.assertEqual(caught.exception.field, "content_sha256")

    def test_a_missing_authority_selector_raises(self):
        root = self.build()
        ProjectPaths.for_root(root).codebook_authority_selector.unlink()
        with self.assertRaises(runtime.AuthoritySelectorError):
            self.report(root)

    def test_a_selector_with_the_wrong_schema_raises(self):
        root = self.build()
        selector_path = ProjectPaths.for_root(root).codebook_authority_selector
        selector = json.loads(selector_path.read_text())
        selector["schema"] = "foundry-authority/99"
        selector_path.write_text(json.dumps(selector), encoding="utf-8")
        with self.assertRaises(runtime.AuthoritySelectorError):
            self.report(root)

    def test_a_selector_naming_no_identity_raises(self):
        root = self.build()
        selector_path = ProjectPaths.for_root(root).codebook_authority_selector
        selector = json.loads(selector_path.read_text())
        del selector["sha256"]
        selector_path.write_text(json.dumps(selector), encoding="utf-8")
        with self.assertRaises(runtime.AuthoritySelectorError):
            self.report(root)

    def test_a_wrong_schema_codebook_is_refused_by_the_store_not_translated(self):
        """The store's own failure must reach the caller UNWRAPPED, so the layer
        that refused stays identifiable."""
        document = fixture_codebook()
        document["schema"] = "foundry-codebook/1"
        root = self.build(codebook_document=document)
        with self.assertRaises(codebook_store.SchemaMismatchError):
            self.report(root)

    def test_a_lint_failure_propagates_as_a_lint_failure(self):
        document = fixture_codebook()
        document["axes"]["rule:alpha"]["members"][0]["assertions"][0]["class"] = "llm"
        root = self.build(codebook_document=document)
        with self.assertRaises(codebook_store.codebook.LintError):
            self.report(root)

    def test_a_corrupt_corpus_line_propagates_as_a_corpus_load_error(self):
        root = self.build(corpus_records=[LEGAL_CARD, "{not json", ILLEGAL_CARD])
        with self.assertRaises(corpus.CorpusLoadError) as caught:
            self.report(root)
        self.assertIn("line 2", str(caught.exception))

    def test_a_missing_corpus_propagates_as_a_corpus_load_error(self):
        root = self.build()
        lock = lock_for(root)
        ProjectPaths.for_root(root).legacy_oracle_cards.unlink()
        with self.assertRaises(FileNotFoundError):
            runtime.run(root, lock_path=str(lock))

    def test_a_run_with_no_declared_corpus_identity_refuses(self):
        root = self.build()
        with self.assertRaises(runtime.InputLockError) as caught:
            runtime.run(root)
        self.assertIn("expected corpus sha256", str(caught.exception))

    def test_a_declared_digest_with_no_provenance_refuses(self):
        root = self.build()
        measured = runtime.measure_file(
            ProjectPaths.for_root(root).legacy_oracle_cards)
        with self.assertRaises(runtime.InputLockError) as caught:
            runtime.run(root, expected_corpus_sha256=measured.sha256)
        self.assertIn("provenance", str(caught.exception))

    def test_a_lock_and_a_flag_that_disagree_refuse_rather_than_pick_one(self):
        root = self.build()
        lock = lock_for(root)
        with self.assertRaises(runtime.InputLockError) as caught:
            runtime.run(root, lock_path=str(lock),
                        expected_corpus_sha256="b" * 64)
        self.assertIn("refusing to pick one", str(caught.exception))

    def test_a_lock_with_the_wrong_schema_refuses(self):
        root = self.build()
        lock = lock_for(root)
        document = json.loads(lock.read_text())
        document["schema"] = "something-else/1"
        lock.write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaises(runtime.InputLockError):
            runtime.run(root, lock_path=str(lock))


# ===========================================================================
# 4. THE SHIPPED CLI BOUNDARY — failures never look like results
# ===========================================================================

class TestTheShippedCommandBoundary(RuntimeFixtureCase):

    def _main(self, argv):
        """Run `cli.main` in-process, capturing both streams."""
        import contextlib
        import io
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = cli.main(argv)
        return status, out.getvalue(), err.getvalue()

    def test_a_good_run_exits_zero_and_writes_only_the_report_to_stdout(self):
        root = self.build()
        status, out, err = self._main(
            ["--root", str(root), "--input-lock", str(lock_for(root))])
        self.assertEqual(status, 0)
        self.assertEqual(err, "")
        self.assertEqual(json.loads(out)["schema"], runtime.REPORT_SCHEMA)

    def test_a_deliberate_bad_input_exits_nonzero_and_writes_NOTHING_to_stdout(self):
        """THE control this whole boundary exists for. A redirected report file
        must never be left holding a success-shaped document for a failed run."""
        root = self.build()
        lock = lock_for(root, sha256="c" * 64)
        status, out, err = self._main(
            ["--root", str(root), "--input-lock", str(lock)])
        self.assertEqual(status, 1)
        self.assertEqual(out, "")
        self.assertTrue(err.startswith("STOP — "), err)
        self.assertIn("c" * 64, err)

    def test_every_typed_failure_class_reaches_exit_one_and_empty_stdout(self):
        """Not one representative failure: each layer that can refuse."""
        cases = {}

        root = self.build()
        selector_path = ProjectPaths.for_root(root).codebook_authority_selector
        selector_path.unlink()
        cases["missing selector"] = ["--root", str(root),
                                     "--input-lock", str(lock_for(root))]

        document = fixture_codebook()
        document["schema"] = "foundry-codebook/1"
        wrong_schema = self.build(codebook_document=document)
        cases["wrong codebook schema"] = [
            "--root", str(wrong_schema), "--input-lock", str(lock_for(wrong_schema))]

        bad_lines = self.build(corpus_records=[LEGAL_CARD, "{oops"])
        cases["corrupt corpus"] = [
            "--root", str(bad_lines), "--input-lock", str(lock_for(bad_lines))]

        lint_root = self.build(codebook_document=self._lint_breaking_document())
        cases["lint failure"] = [
            "--root", str(lint_root), "--input-lock", str(lock_for(lint_root))]

        no_identity = self.build()
        cases["no declared identity"] = ["--root", str(no_identity)]

        for name, argv in cases.items():
            with self.subTest(case=name):
                status, out, err = self._main(argv)
                self.assertEqual(status, 1, err)
                self.assertEqual(out, "")
                self.assertTrue(err.startswith("STOP — "), err)

    @staticmethod
    def _lint_breaking_document() -> dict:
        document = fixture_codebook()
        document["axes"]["rule:alpha"]["members"][0]["assertions"] = []
        return document

    def test_bad_usage_is_argparse_status_two_not_a_runtime_failure(self):
        import contextlib
        import io

        with contextlib.redirect_stderr(io.StringIO()) as err:
            with self.assertRaises(SystemExit) as caught:
                cli.main([])
        self.assertEqual(caught.exception.code, 2)
        self.assertIn("--root", err.getvalue())

    def test_the_command_writes_no_file_and_creates_no_directory(self):
        """Measured, not asserted in prose: the whole fixture root is digested
        before and after, and nothing may move."""
        root = self.build()
        lock = lock_for(root)

        def snapshot():
            return {
                p.relative_to(root).as_posix(): runtime.measure_file(p).sha256
                for p in sorted(root.rglob("*")) if p.is_file()}

        before = snapshot()
        status, out, _ = self._main(["--root", str(root), "--input-lock", str(lock)])
        self.assertEqual(status, 0)
        self.assertNotEqual(out, "")
        self.assertEqual(snapshot(), before)


# ===========================================================================
# 5. ELIGIBILITY PARTITIONS; IT DOES NOT FILTER
# ===========================================================================

class TestEligibilityAccounting(RuntimeFixtureCase):

    def test_the_predicate_matches_its_ratified_vocabulary(self):
        self.assertEqual(corpus.GATE0_LEGAL_VALUES, ("legal", "restricted"))
        self.assertTrue(corpus.is_gate0_eligible(LEGAL_CARD))
        self.assertFalse(corpus.is_gate0_eligible(ILLEGAL_CARD))

    def test_an_absent_or_null_legalities_map_is_ineligible_not_an_error(self):
        self.assertFalse(corpus.is_gate0_eligible({"oracle_id": ID_A}))
        self.assertFalse(corpus.is_gate0_eligible({"legalities": None}))
        self.assertFalse(corpus.is_gate0_eligible({"legalities": {}}))

    def test_a_value_outside_the_ratified_set_does_not_qualify(self):
        for value in ("banned", "not_legal", "Legal", "LEGAL", "restricted "):
            with self.subTest(value=value):
                self.assertFalse(
                    corpus.is_gate0_eligible({"legalities": {"vintage": value}}))

    def test_the_full_population_is_reported_alongside_eligibility(self):
        report = self.report(self.build())
        eligibility = report["eligibility"]
        self.assertEqual(eligibility["full_population_unique_ids"], 3)
        self.assertEqual(eligibility["eligible_unique_ids"], 2)
        self.assertEqual(eligibility["ineligible_unique_ids"], 1)
        self.assertEqual(report["corpus_population"]["unique_oracle_ids"], 3)

    def test_the_partition_is_exhaustive_and_the_population_is_never_filtered(self):
        report = self.report(self.build())
        eligibility = report["eligibility"]
        self.assertEqual(
            eligibility["eligible_unique_ids"] + eligibility["ineligible_unique_ids"],
            eligibility["full_population_unique_ids"])
        self.assertEqual(eligibility["full_population_unique_ids"],
                         report["coverage"]["corpus_ids_total"])


# ===========================================================================
# 6. DUPLICATE-ID AND ALL-FACE SEMANTICS SURVIVE THE COMPOSITION
# ===========================================================================

class TestCorpusSemanticsSurviveTheBoundary(RuntimeFixtureCase):

    def test_a_duplicate_oracle_id_collapses_last_write_wins_at_the_report(self):
        """The loader's accepted rule, measured where a consumer would see it.

        Three records, two ids. The report must say two -- and the surviving
        record must be the LAST, which is what distinguishes last-write-wins from
        a first-wins or a dropped duplicate.
        """
        first = dict(LEGAL_CARD, name="Fixture First")
        last = dict(LEGAL_CARD, name="Fixture Last")
        root = self.build(corpus_records=[first, ILLEGAL_CARD, last])
        report = self.report(root)
        self.assertEqual(report["corpus_population"]["unique_oracle_ids"], 2)
        self.assertEqual(
            report["corpus_population"]["duplicate_oracle_id_semantics"],
            "last_write_wins")
        cards = corpus.load_cards(ProjectPaths.for_root(root).legacy_oracle_cards)
        self.assertEqual(cards[ID_A]["name"], "Fixture Last")

    def test_a_shared_normalized_name_keeps_every_id(self):
        twin = dict(ILLEGAL_CARD, oracle_id=ID_C, name="fixture LEGAL  ")
        root = self.build(corpus_records=[LEGAL_CARD, twin])
        population = self.report(root)["corpus_population"]
        self.assertEqual(population["unique_oracle_ids"], 2)
        self.assertEqual(population["normalized_names_shared_by_more_than_one_id"], 1)
        self.assertEqual(population["ids_sharing_a_normalized_name"], 2)

    def test_every_face_of_a_multi_face_card_is_counted(self):
        report = self.report(self.build())
        population = report["corpus_population"]
        self.assertEqual(population["multi_face_cards"], 1)
        self.assertEqual(population["single_face_cards"], 2)
        self.assertEqual(population["faces_total"], 4)
        self.assertEqual(population["max_faces_on_one_card"], 2)

    def test_face_counting_goes_through_the_capability_not_the_raw_field(self):
        """A split/adventure card HAS `card_faces` and one root-level text. The
        capability is what makes both shapes read correctly, and a fixture that
        counted the raw list would report this card's structure differently."""
        adventure = {
            "oracle_id": ID_C,
            "name": "Fixture Adventure",
            "oracle_text": "Root level text.",
            "legalities": {"modern": "legal"},
            "card_faces": [
                {"name": "Fixture Adventure", "oracle_text": "Creature half."},
                {"name": "Fixture Quest", "oracle_text": "Adventure half."},
            ],
        }
        self.assertEqual(len(corpus.card_faces(adventure)), 2)
        root = self.build(corpus_records=[adventure])
        self.assertEqual(self.report(root)["corpus_population"]["faces_total"], 2)


# ===========================================================================
# 7. COVERAGE ACCOUNTING
# ===========================================================================

class TestCoverageAccounting(RuntimeFixtureCase):

    def test_memberships_and_covered_cards_are_reported_as_different_numbers(self):
        """ID_A sits on two active axes. Two memberships, one covered card."""
        report = self.report(self.build())
        self.assertEqual(report["codebook_structure"]["memberships_active_axes"], 3)
        self.assertEqual(report["coverage"]["corpus_ids_covered"], 1)
        self.assertNotEqual(report["codebook_structure"]["memberships_active_axes"],
                            report["coverage"]["corpus_ids_covered"])

    def test_only_active_axes_contribute_to_coverage(self):
        """ID_B is a member of a KILLED axis and must not be counted covered."""
        report = self.report(self.build())
        self.assertEqual(report["codebook_structure"]["axes_by_status"],
                         {"active": 2, "killed": 1})
        self.assertEqual(report["codebook_structure"]["distinct_member_ids_active_axes"], 2)
        self.assertEqual(report["codebook_structure"]["distinct_member_ids_all_statuses"], 3)
        self.assertEqual(report["coverage"]["corpus_ids_covered"], 1)

    def test_uncovered_ids_are_counted_explicitly_and_add_up(self):
        report = self.report(self.build())
        coverage = report["coverage"]
        self.assertEqual(coverage["corpus_ids_uncovered"], 2)
        self.assertEqual(coverage["corpus_ids_covered"] + coverage["corpus_ids_uncovered"],
                         coverage["corpus_ids_total"])

    def test_member_ids_absent_from_the_corpus_are_accounted_not_discarded(self):
        """ID_C is an active member and is not in the corpus. It must appear as a
        counted fact rather than vanishing into a coverage ratio."""
        report = self.report(self.build())
        coverage = report["coverage"]
        self.assertEqual(coverage["active_member_ids_absent_from_corpus"], 1)
        self.assertEqual(
            coverage["memberships_on_active_member_ids_absent_from_corpus"], 1)
        self.assertEqual(
            report["codebook_structure"]["distinct_member_ids_active_axes"],
            coverage["corpus_ids_covered"] + coverage["active_member_ids_absent_from_corpus"])

    def test_eligible_and_ineligible_coverage_partition_the_covered_set(self):
        report = self.report(self.build())
        coverage = report["coverage"]
        self.assertEqual(coverage["eligible_ids_covered"] + coverage["ineligible_ids_covered"],
                         coverage["corpus_ids_covered"])
        self.assertEqual(coverage["eligible_ids_covered"] + coverage["eligible_ids_uncovered"],
                         report["eligibility"]["eligible_unique_ids"])

    def test_evidence_fields_are_still_present_after_loading(self):
        """Conservation, not semantics: quote / locality / source provenance must
        survive into the loaded document, or every later milestone loses them."""
        present = self.report(self.build())["codebook_evidence_fields_present_on_active_axes"]
        self.assertEqual(present["assertions"], 3)
        for field in ("with_quote", "with_locality", "with_source_ref", "with_corpus_ref"):
            with self.subTest(field=field):
                self.assertEqual(present[field], 3)


# ===========================================================================
# 8. THE PACKAGE STAYS PERMANENT — no legacy runtime edge, one declared command
# ===========================================================================

class TestThePermanentBoundaryHolds(unittest.TestCase):

    NEW_MODULES = ("runtime.py", "cli.py")

    def test_the_new_modules_import_nothing_from_the_legacy_tree(self):
        for name in self.NEW_MODULES:
            text = (SRC / "mtj_foundry" / name).read_text(encoding="utf-8")
            with self.subTest(module=name):
                for legacy in ("import tier_engine", "import foundry_", "from foundry_",
                               "from tier_engine", "experiments.", "pipeline.", "aq4"):
                    self.assertNotIn(legacy, text)

    def test_the_runtime_reaches_no_legacy_module_when_it_is_actually_imported(self):
        """Static text is not the same evidence as a live import graph."""
        code = (
            "import sys, mtj_foundry.cli, mtj_foundry.runtime\n"
            "banned = [m for m in sys.modules\n"
            "          if m.split('.')[0] in {'experiments', 'pipeline', 'tier_engine'}\n"
            "          or m.startswith('foundry_') or 'aq4' in m]\n"
            "assert not banned, banned\n"
            "print('ok')\n")
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / "unrelated"
            outside.mkdir()
            env = dict(CLEAN_ENV)
            env["PYTHONPATH"] = str(SRC)
            proc = subprocess.run([sys.executable, "-c", code], cwd=outside,
                                  capture_output=True, text=True, env=env)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("ok", proc.stdout)

    def test_the_runtime_imports_no_third_party_module(self):
        """`dependencies = []` has to stay TRUE of the code, not only the metadata."""
        import ast

        allowed = {"mtj_foundry", "__future__", "argparse", "dataclasses", "gzip",
                   "hashlib", "json", "os", "pathlib", "sys", "re", "typing"}
        for name in self.NEW_MODULES:
            tree = ast.parse((SRC / "mtj_foundry" / name).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                roots = []
                if isinstance(node, ast.Import):
                    roots = [alias.name.split(".")[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    roots = [node.module.split(".")[0]]
                for root in roots:
                    with self.subTest(module=name, imports=root):
                        self.assertIn(root, allowed)

    def test_the_declared_console_script_resolves_to_the_shipped_callable(self):
        data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        scripts = data["project"]["scripts"]
        self.assertEqual(scripts, {"mtj-foundry-report": "mtj_foundry.cli:main"})
        module, _, attribute = scripts["mtj-foundry-report"].partition(":")
        self.assertEqual(module, cli.__name__)
        self.assertTrue(callable(getattr(cli, attribute)))

    def test_the_metadata_version_and_the_package_version_agree(self):
        import mtj_foundry

        data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(data["project"]["version"], mtj_foundry.__version__)

    def test_runtime_dependencies_are_still_declared_empty(self):
        data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(data["project"]["dependencies"], [])

    def test_generated_installation_artifacts_are_ignored(self):
        ignore = {line.strip() for line in
                  (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()}
        for pattern in ("build/", "dist/", "*.egg-info/"):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, ignore)

    def test_card_data_exclusions_were_not_weakened(self):
        ignore = {line.strip() for line in
                  (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()}
        for pattern in ("data/", "*.jsonl", "*.jsonl.gz", "*.parquet", "*.sqlite",
                        "experiments/out/"):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, ignore)

    def test_the_layout_owner_still_owns_every_path_the_runtime_uses(self):
        """No repository-relative literal may live in the composition boundary."""
        text = (SRC / "mtj_foundry" / "runtime.py").read_text(encoding="utf-8")
        import ast

        constants = {n.value for n in ast.walk(ast.parse(text))
                     if isinstance(n, ast.Constant) and isinstance(n.value, str)}
        docstrings = set()
        for node in ast.walk(ast.parse(text)):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)):
                doc = ast.get_docstring(node, clean=False)
                if doc is not None:
                    docstrings.add(doc)
        schema_ids = {runtime.REPORT_SCHEMA, runtime.INPUT_LOCK_SCHEMA,
                      runtime.AUTHORITY_SCHEMA}
        for value in constants - docstrings - schema_ids:
            with self.subTest(value=value):
                self.assertNotIn(".json", value)
                self.assertNotIn(".gz", value)
                self.assertNotIn("/", value)


# ===========================================================================
# 9. THE REAL SELECTED INPUTS — skipped when the gitignored data is absent
# ===========================================================================

class TestAgainstTheRealSelectedInputs(unittest.TestCase):
    """The acceptance shape, run here when the local data happens to be present.

    This is NOT the acceptance witness: that runs the INSTALLED command from an
    unrelated cwd and is recorded in the Worker result. This is the same
    composition against the same bytes, so a later change that breaks it is
    caught by the ordinary suite on a machine that has the data.
    """

    LOCK = REPO_ROOT / "refoundation" / "path-e" / "input-lock.json"

    @classmethod
    def setUpClass(cls):
        missing = [str(p) for p in (REAL_CORPUS, REAL_CODEBOOK) if not p.exists()]
        if missing:
            raise unittest.SkipTest(
                f"gitignored input(s) absent: {missing}. the fixture suites above "
                "still run, and the Worker result records the real-input outcome")
        cls.report = runtime.run(REPO_ROOT, lock_path=str(cls.LOCK))

    def test_the_selected_codebook_verifies_against_its_tracked_selector(self):
        selector = json.loads(
            REAL_PATHS.codebook_authority_selector.read_text(encoding="utf-8"))
        codebook_input = self.report["inputs"]["codebook"]
        self.assertEqual(codebook_input["measured_sha256"], selector["sha256"])
        self.assertEqual(codebook_input["measured_byte_size"], selector["byte_size"])

    def test_the_reported_active_axis_count_matches_the_tracked_selector(self):
        """An independent cross-check: the selector recorded these two numbers
        when the snapshot was made, and the report re-derives them from bytes."""
        selector = json.loads(
            REAL_PATHS.codebook_authority_selector.read_text(encoding="utf-8"))
        structure = self.report["codebook_structure"]
        self.assertEqual(structure["axes_by_status"]["active"],
                         selector["active_axis_count"])
        self.assertEqual(structure["memberships_active_axes"],
                         selector["assertion_count"])

    def test_eligibility_matches_its_legacy_oracle_card_by_card(self):
        """VALUE_EXACT against `gate_passes`, over the full corpus.

        The oracle is reached the way legacy callers reach it. This is the
        behavioural comparison the capability's correctness rests on; a fixture
        pair cannot make that claim about 38,000 rows.
        """
        if str(EXPERIMENTS) not in sys.path:
            sys.path.insert(0, str(EXPERIMENTS))
        import foundry_common as legacy

        cards = corpus.load_cards(REAL_CORPUS)
        disagreements = [oracle_id for oracle_id, card in cards.items()
                         if legacy.gate_passes(card) != corpus.is_gate0_eligible(card)]
        self.assertEqual(disagreements, [])
        self.assertEqual(
            sum(1 for card in cards.values() if legacy.gate_passes(card)),
            self.report["eligibility"]["eligible_unique_ids"])

    def test_the_full_population_is_larger_than_the_eligible_population(self):
        """Otherwise the differential above could pass with the gate excluding
        nothing, which would prove the predicate was never exercised."""
        eligibility = self.report["eligibility"]
        self.assertGreater(eligibility["ineligible_unique_ids"], 0)
        self.assertEqual(
            eligibility["eligible_unique_ids"] + eligibility["ineligible_unique_ids"],
            eligibility["full_population_unique_ids"])

    def test_the_real_run_is_deterministic(self):
        again = runtime.run(REPO_ROOT, lock_path=str(self.LOCK))
        self.assertEqual(runtime.render_report(again),
                         runtime.render_report(self.report))


if __name__ == "__main__":
    unittest.main()
