"""C8.5N — local codebook persistence as a permanent capability.

Three claims:

1. `mtj_foundry.codebook_store` is a **local, explicit-path, non-exiting**
   library: five stdlib-and-model imports, no repository root, no default
   codebook path, no backup, no network, no subprocess, no print, no exit.
2. The **A13 protocol** — temp write, fsync, readback, second lint,
   re-serialize identity, atomic replace, post-install digest — is preserved
   step for step, and each step is asserted by the failure it must produce.
3. `experiments/foundry_codebook.py` still behaves exactly as it did: one
   object-identical alias and one thin translation wrapper, with `OSError`
   still escaping raw.

The third claim carries the load. A13's whole point is that a mutation is not
trusted because the writer says so, and the two controls that enforce that —
`foundry_verify_migration`'s independence and its `os.replace` interruption rig
— must still be able to fail after this cut. Both are asserted here, one
structurally and one by the shape of the exception that escapes.

Every write in this file lands in an OS temp directory. No repository path is
constructed, no root is derived, and the operational codebook is never a target.
"""

from __future__ import annotations

import ast
import contextlib
import hashlib
import inspect
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT
from tests.refoundation.test_gate2_purity import EXPERIMENTS, load_legacy

from mtj_foundry import codebook, codebook_store

# C8.5P: 5 -> 9. Written out rather than derived from `codebook_store.__all__`;
# a guard that reads its subject's own answer back to it proves nothing.
EXPECTED_ALL = [
    "CodebookNotFoundError",
    "CodebookReadError",
    "CodebookStoreError",
    "PostWriteDigestError",
    "SchemaMismatchError",
    "SerializationMismatchError",
    "read",
    "serialize",
    "write_atomic",
]

# The exact dependency set C8.5N allows each permanent module to reach, keyed on
# FULL normalized module identity.
#
# C8.5N.R2 REPLACED A TOP-LEVEL SET WITH THIS ONE. The first version reduced
# every import to `name.split(".")[0]`, so `mtj_foundry` was the allowed entry
# and `import mtj_foundry.paths` — the layout capability this store is
# explicitly denied — scored as allowed, while the `from mtj_foundry import
# paths` spelling of the SAME edge was caught. A set that cannot tell two
# members of a package apart cannot express "only the model"
# (Manager review issue:1#issuecomment-5561128789).
STORE_IMPORTS = {"__future__", "hashlib", "json", "os", "pathlib",
                 "mtj_foundry.codebook"}
MODEL_IMPORTS = {"__future__", "re"}

# The permanent closure at this slice, and it is exact: a third permanent module
# is a W5 failure until a contract widens it.
EXPECTED_CLOSURE = {"mtj_foundry.codebook_store", "mtj_foundry.codebook"}


def normalized_imports(source: str) -> set:
    """Direct dependencies of `source` as full module identities.

    Written out here rather than imported from `foundry_authority`: a guard that
    asks its subject to grade itself proves nothing, and this rule is exactly
    what the shipped one got wrong. `test_the_shipped_normalizer_agrees` then
    compares the two, so the duplication is the control.
    """
    found = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            found |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            if node.level:                       # relative: never resolves away
                found.add("." * node.level + (node.module or ""))
            elif node.module == "mtj_foundry":
                found |= {f"mtj_foundry.{a.name}" for a in node.names}
            elif node.module:
                found.add(node.module)
    return found

# Reachable from `os`, and rejected by name rather than by banning the module —
# `os.fsync` and `os.replace` are the protocol.
PROCESS_SPAWNING = ("os.system", "os.popen", "os.spawn", "os.exec", "os.fork",
                    "os.posix_spawn")

OID = "00000001-0000-4000-8000-000000000001"


def document(status="active", version="0.7", quote="t"):
    return {"schema": codebook.SCHEMA_V2, "version": version, "axes": {
        "rule:a": {"status": status, "members": [
            {"oracle_id": OID, "assertions": [
                {"class": "human", "source_ref": "batch-1", "quote": quote,
                 "corpus_ref": "2026-07-04", "evidence_status": "quoted"}]}]}}}


class TempTargetTestCase(unittest.TestCase):
    """Every write goes to a throwaway directory. Nothing here can name a
    repository path, so nothing here can reach the operational codebook."""

    def setUp(self):
        self._dir = tempfile.TemporaryDirectory(prefix="c85n-test-")
        self.addCleanup(self._dir.cleanup)
        self.tmp = Path(self._dir.name)
        self.target = self.tmp / "cb.json"
        self.leftover = self.target.with_suffix(self.target.suffix + ".tmp")


# ===========================================================================
# 1. THE PERMANENT STORE IS A LOCAL LIBRARY
# ===========================================================================

class TestTheStoreSurface(unittest.TestCase):

    def test_the_public_api_is_exactly_the_contracted_nine(self):
        self.assertEqual(sorted(codebook_store.__all__), EXPECTED_ALL)
        self.assertEqual(len(codebook_store.__all__), 9)
        for name in EXPECTED_ALL:
            with self.subTest(name=name):
                self.assertTrue(hasattr(codebook_store, name))

    def test_the_two_integrity_errors_share_one_base_and_are_distinct(self):
        self.assertTrue(issubclass(codebook_store.CodebookStoreError, RuntimeError))
        for leaf in ("SerializationMismatchError", "PostWriteDigestError"):
            with self.subTest(leaf=leaf):
                self.assertTrue(issubclass(getattr(codebook_store, leaf),
                                           codebook_store.CodebookStoreError))
        self.assertIsNot(codebook_store.SerializationMismatchError,
                         codebook_store.PostWriteDigestError)

    def test_a_lint_failure_is_the_MODELS_error_not_a_store_error(self):
        """`LintError` propagates from the model. Re-wrapping it would give the
        same fact two names and break `except fcb.LintError` at the facade."""
        self.assertFalse(issubclass(codebook.LintError,
                                    codebook_store.CodebookStoreError))

    def test_it_exposes_no_default_path_backup_or_generic_hash(self):
        """The capabilities still NOT taken.

        C8.5P RE-AIM, NOT RELAXATION. `read` and `load` left this list because
        the read capability was added by contract; every other name stays, and
        the two that matter most stay for the same reason they were listed:
        `CODEBOOK_PATH` would make the store a second layout authority, and
        `sha256_of`/`digest_file` would turn one caller's private helper into a
        digest service."""
        for absent in ("load_codebook", "CODEBOOK_PATH",
                       "BACKUPS_DIR", "LATEST_ARTIFACT_PATH", "backup",
                       "backup_codebook", "sha256_of", "digest_file",
                       "corpus_ref_current"):
            with self.subTest(name=absent):
                self.assertFalse(hasattr(codebook_store, absent))

    def test_the_post_install_digest_helper_is_private(self):
        """It exists — but as one caller's helper, not a digest service."""
        self.assertTrue(hasattr(codebook_store, "_digest_file"))
        self.assertNotIn("_digest_file", codebook_store.__all__)


class TestTheStoreIsLocalOnly(unittest.TestCase):
    """Structural, on the AST — never on the prose. The module's docstring names
    `sys.exit`, `subprocess` and the network to explain what it is not, and a
    textual guard would forbid the explanation."""

    @classmethod
    def setUpClass(cls):
        cls.source = inspect.getsource(codebook_store)
        cls.tree = ast.parse(cls.source)

    def test_it_imports_only_the_allowed_set(self):
        self.assertEqual(normalized_imports(self.source), STORE_IMPORTS)

    def test_its_only_permanent_dependency_is_the_codebook_model(self):
        """Full identity, so a sibling of the model is not the model. Both
        spellings of a permanent import normalize into this set, which is what
        makes `mtj_foundry.paths` visible here in either form."""
        permanent = {i for i in normalized_imports(self.source)
                     if i.split(".")[0] == "mtj_foundry"}
        self.assertEqual(permanent, {"mtj_foundry.codebook"})

    def test_the_model_keeps_its_accepted_two_import_boundary(self):
        """C8.5M's `{__future__, re}` purity is the other half of the closure and
        is re-asserted through the SAME normalizer, so neither half can be
        widened by a spelling the other half's guard cannot see."""
        self.assertEqual(normalized_imports(inspect.getsource(codebook)),
                         MODEL_IMPORTS)

    def test_it_never_prints_exits_or_spawns_a_process(self):
        calls = [ast.unparse(n.func) for n in ast.walk(self.tree)
                 if isinstance(n, ast.Call)]
        for banned in ("print", "exit", "sys.exit", "fc.halt", "subprocess.run",
                       "subprocess.Popen"):
            with self.subTest(call=banned):
                self.assertNotIn(banned, calls)
        for family in PROCESS_SPAWNING:
            with self.subTest(family=family):
                self.assertFalse([c for c in calls if c.startswith(family)])

    def test_it_states_no_repository_layout_and_no_default_path(self):
        for node in self.tree.body:
            if not isinstance(node, ast.Assign):
                continue
            text = ast.unparse(node)
            for banned in ("REPO_ROOT", "__file__", "ProjectPaths",
                           "experiments/", "docs/", "data/", "codebook.json"):
                with self.subTest(binding=text.split("=")[0].strip(), banned=banned):
                    self.assertNotIn(banned, text)

    def test_write_atomic_has_no_default_target(self):
        signature = inspect.signature(codebook_store.write_atomic)
        self.assertIs(signature.parameters["path"].default,
                      inspect.Parameter.empty)
        self.assertIsNone(signature.parameters["path_label"].default)

    def test_os_replace_json_load_and_fsync_stay_LATE_BOUND(self):
        """`from os import replace` is equivalent Python and would silently
        disarm the ratified interruption control, which patches the shared `os`
        module. The same holds for `os.fsync` and `json.load`, which the failure
        rigs reach the same way. Asserted as attribute access on the module."""
        calls = [ast.unparse(n.func) for n in ast.walk(self.tree)
                 if isinstance(n, ast.Call)]
        for required in ("os.replace", "os.fsync", "json.load", "json.dumps"):
            with self.subTest(call=required):
                self.assertIn(required, calls)
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ImportFrom):
                with self.subTest(module=node.module):
                    self.assertNotIn(node.module, ("os", "json"))


class TestTheTwoErrorHierarchiesStaySeparate(unittest.TestCase):
    """C8.5P.V correction C1. Read failures are NOT integrity failures.

    `CodebookStoreError`'s accepted definition is "the store's own INTEGRITY
    failures, and only those". A missing file or a /1 document is neither, so
    hanging them under it would widen an accepted definition by stealth and make
    one `except` clause catch two different kinds of fact."""

    def test_read_errors_are_NOT_under_the_integrity_base(self):
        self.assertFalse(issubclass(codebook_store.CodebookReadError,
                                    codebook_store.CodebookStoreError))
        for leaf in ("CodebookNotFoundError", "SchemaMismatchError"):
            with self.subTest(leaf=leaf):
                self.assertFalse(issubclass(getattr(codebook_store, leaf),
                                            codebook_store.CodebookStoreError))

    def test_integrity_errors_are_NOT_under_the_read_base(self):
        for leaf in ("SerializationMismatchError", "PostWriteDigestError"):
            with self.subTest(leaf=leaf):
                self.assertFalse(issubclass(getattr(codebook_store, leaf),
                                            codebook_store.CodebookReadError))

    def test_each_hierarchy_is_rooted_and_populated_as_contracted(self):
        self.assertTrue(issubclass(codebook_store.CodebookReadError, RuntimeError))
        self.assertTrue(issubclass(codebook_store.CodebookStoreError, RuntimeError))
        for leaf in ("CodebookNotFoundError", "SchemaMismatchError"):
            self.assertTrue(issubclass(getattr(codebook_store, leaf),
                                       codebook_store.CodebookReadError))
        for leaf in ("SerializationMismatchError", "PostWriteDigestError"):
            self.assertTrue(issubclass(getattr(codebook_store, leaf),
                                       codebook_store.CodebookStoreError))

    def test_a_lint_failure_is_still_neither(self):
        self.assertFalse(issubclass(codebook.LintError, codebook_store.CodebookStoreError))
        self.assertFalse(issubclass(codebook.LintError, codebook_store.CodebookReadError))


class TestRead(unittest.TestCase):
    """Explicit path in, document out — and everything the legacy loader did not
    translate still arrives raw."""

    def setUp(self):
        self._d = tempfile.TemporaryDirectory(prefix="c85p-read-")
        self.addCleanup(self._d.cleanup)
        self.tmp = Path(self._d.name)

    def write(self, name, payload):
        p = self.tmp / name
        p.write_text(payload if isinstance(payload, str) else json.dumps(payload),
                     encoding="utf-8")
        return p

    def test_a_valid_v2_document_round_trips(self):
        doc = document(quote="C’tan 日本語")
        p = self.write("cb.json", doc)
        self.assertEqual(codebook_store.read(p), doc)
        self.assertEqual(codebook_store.read(p),
                         json.loads(p.read_text(encoding="utf-8")))

    def test_it_accepts_a_string_path_as_well_as_a_Path(self):
        p = self.write("cb.json", document())
        self.assertEqual(codebook_store.read(str(p)), codebook_store.read(p))

    def test_read_has_NO_default_path(self):
        """The whole reason ProjectPaths gained `legacy_codebook_json`."""
        params = inspect.signature(codebook_store.read).parameters
        self.assertIs(params["path"].default, inspect.Parameter.empty)
        with self.assertRaises(TypeError):
            codebook_store.read()

    def test_a_missing_file_raises_CodebookNotFoundError_carrying_the_path(self):
        target = self.tmp / "absent.json"
        with self.assertRaises(codebook_store.CodebookNotFoundError) as raised:
            codebook_store.read(target)
        self.assertEqual(raised.exception.path, Path(target))
        self.assertEqual(str(raised.exception), f"{target} not found")

    def test_a_v1_document_raises_SchemaMismatchError_with_structured_facts(self):
        p = self.write("v1.json", {"schema": codebook.SCHEMA_V1, "axes": {}})
        with self.assertRaises(codebook_store.SchemaMismatchError) as raised:
            codebook_store.read(p)
        e = raised.exception
        self.assertEqual((e.path, e.actual, e.expected),
                         (Path(p), codebook.SCHEMA_V1, codebook.SCHEMA_V2))

    def test_any_other_schema_raises_the_same_type(self):
        for bad in ("wat/9", None, 7):
            with self.subTest(schema=bad):
                p = self.write("o.json", {"schema": bad, "axes": {}} if bad is not None
                               else {"axes": {}})
                with self.assertRaises(codebook_store.SchemaMismatchError) as raised:
                    codebook_store.read(p)
                self.assertEqual(
                    str(raised.exception),
                    f"{p}: unexpected schema {bad!r}, expected {codebook.SCHEMA_V2!r}")

    def test_the_permanent_message_carries_NO_legacy_repository_guidance(self):
        """C8.5P.V correction C3. The `/1` sentence names two `experiments/`
        scripts; a permanent library may not. The facade owns that text."""
        p = self.write("v1.json", {"schema": codebook.SCHEMA_V1, "axes": {}})
        with self.assertRaises(codebook_store.SchemaMismatchError) as raised:
            codebook_store.read(p)
        text = str(raised.exception)
        for leaked in ("experiments/", "foundry_migrate_codebook_v2",
                       "foundry_reconcile", "pre-migration", ".py"):
            with self.subTest(leaked=leaked):
                self.assertNotIn(leaked, text)
        # ON THE AST, AND DOCSTRINGS EXCLUDED. The module's prose names these
        # very strings to explain why it must not carry them — the first draft
        # of this guard scanned raw source and went red on its own explanation,
        # which is the trap this repository already has a name for. What matters
        # is that no RUNTIME string literal carries the guidance.
        tree = ast.parse(inspect.getsource(codebook_store))
        docstrings = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                                 ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node, clean=False)
                if doc is not None:
                    docstrings.add(doc)
        literals = [n.value for n in ast.walk(tree)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str)
                    and n.value not in docstrings]
        for leaked in ("experiments/", "foundry_migrate_codebook_v2",
                       "foundry_reconcile", "codebook.json", "REPO_ROOT",
                       "pre-migration"):
            with self.subTest(literal=leaked):
                self.assertFalse([x for x in literals if leaked in x])
        # ProjectPaths must not be reachable at all, in any form.
        self.assertNotIn("mtj_foundry.paths",
                         {i for i in normalized_imports(inspect.getsource(codebook_store))})

    def test_malformed_json_propagates_RAW(self):
        p = self.write("bad.json", "{not json")
        with self.assertRaises(json.JSONDecodeError) as raised:
            codebook_store.read(p)
        self.assertNotIsInstance(raised.exception, codebook_store.CodebookReadError)

    def test_an_os_level_failure_propagates_RAW(self):
        d = self.tmp / "adir"
        d.mkdir()
        with self.assertRaises(OSError) as raised:
            codebook_store.read(d)
        self.assertNotIsInstance(raised.exception, codebook_store.CodebookReadError)

    def test_a_non_mapping_document_propagates_RAW(self):
        p = self.write("list.json", [1, 2, 3])
        with self.assertRaises(AttributeError):
            codebook_store.read(p)


# ===========================================================================
# 2. SERIALIZATION — THE BYTE CONTRACT
# ===========================================================================

class TestSerialize(unittest.TestCase):

    def test_it_reproduces_the_legacy_formatting_exactly(self):
        for doc in (document(), document(quote="Æ’lying — “curly” ’quote’ 日本語"),
                    {"schema": codebook.SCHEMA_V2, "version": "0.7", "axes": {}}):
            with self.subTest(doc=sorted(doc)):
                self.assertEqual(
                    codebook_store.serialize(doc),
                    json.dumps(doc, indent=2, ensure_ascii=False) + "\n")

    def test_non_ascii_stays_raw_and_is_not_escaped(self):
        """`ensure_ascii=False` is not cosmetic. The operational codebook carries
        real curly apostrophes and non-ASCII card text, and the tracked authority
        selector pins the sha256 of exactly these bytes."""
        payload = codebook_store.serialize(document(quote="C’tan 日本語"))
        self.assertIn("C’tan 日本語", payload)
        self.assertNotIn("\\u", payload)

    def test_it_ends_in_exactly_one_newline(self):
        payload = codebook_store.serialize(document())
        self.assertTrue(payload.endswith("\n"))
        self.assertFalse(payload.endswith("\n\n"))

    def test_it_is_deterministic_across_repeated_calls(self):
        doc = document()
        self.assertEqual(codebook_store.serialize(doc),
                         codebook_store.serialize(doc))


# ===========================================================================
# 3. THE A13 WRITE PROTOCOL
# ===========================================================================

class TestAValidWrite(TempTargetTestCase):

    def test_the_installed_bytes_are_the_serialized_payload(self):
        doc = document(quote="日本語")
        digest = codebook_store.write_atomic(self.target, doc, "LBL")
        payload = codebook_store.serialize(doc)
        self.assertEqual(self.target.read_text(encoding="utf-8"), payload)
        self.assertEqual(
            digest, hashlib.sha256(payload.encode("utf-8")).hexdigest())

    def test_the_returned_digest_is_the_installed_files_digest(self):
        digest = codebook_store.write_atomic(self.target, document(), "LBL")
        self.assertEqual(
            digest, hashlib.sha256(self.target.read_bytes()).hexdigest())

    def test_the_temp_file_does_not_survive_a_successful_write(self):
        codebook_store.write_atomic(self.target, document(), "LBL")
        self.assertFalse(self.leftover.exists())

    def test_the_temp_suffix_is_the_target_plus_tmp(self):
        """Asserted through the rig rather than by restating the expression: a
        failing write is what leaves the temp behind to be named."""
        real = os.replace

        def boom(src, dst):
            raise OSError("stop before rename")
        os.replace = boom
        try:
            with self.assertRaises(OSError):
                codebook_store.write_atomic(self.target, document(), "LBL")
        finally:
            os.replace = real
        self.assertTrue(self.leftover.exists())
        self.assertEqual(self.leftover.name, "cb.json.tmp")

    def test_missing_parent_directories_are_created(self):
        deep = self.tmp / "a" / "b" / "deep.json"
        codebook_store.write_atomic(deep, document(), "LBL")
        self.assertTrue(deep.exists())

    def test_fsync_is_exercised_on_the_temp_file(self):
        real = os.fsync
        seen = []

        def spy(fd):
            seen.append(fd)
            return real(fd)
        os.fsync = spy
        try:
            codebook_store.write_atomic(self.target, document(), "LBL")
        finally:
            os.fsync = real
        self.assertEqual(len(seen), 1)

    def test_an_existing_target_is_replaced_wholesale(self):
        self.target.write_text("x" * 5000, encoding="utf-8")
        codebook_store.write_atomic(self.target, document(), "LBL")
        self.assertEqual(self.target.read_text(encoding="utf-8"),
                         codebook_store.serialize(document()))


class TestTheProtocolRefusesBeforeInstalling(TempTargetTestCase):

    def test_a_pre_write_lint_failure_never_touches_the_target(self):
        with self.assertRaises(codebook.LintError) as caught:
            codebook_store.write_atomic(self.target, document(status="actve"), "LBL")
        self.assertIn("LBL (pre-write, in memory)", str(caught.exception))
        self.assertFalse(self.target.exists())
        self.assertFalse(self.leftover.exists())

    def test_a_readback_lint_failure_leaves_the_target_uninstalled(self):
        """The TEMP is what gets validated. Rigged through the shared `json`
        module, which both the permanent store and the legacy writer reach
        late-bound — patching the store's own globals would test a copy the
        legacy path never calls."""
        self.target.write_text("PRE-EXISTING\n", encoding="utf-8")
        real = json.load
        json.load = lambda handle, **kw: document(status="actve")
        try:
            with self.assertRaises(codebook.LintError) as caught:
                codebook_store.write_atomic(self.target, document(), "LBL")
        finally:
            json.load = real
        self.assertIn("LBL (readback of temp)", str(caught.exception))
        self.assertEqual(self.target.read_text(encoding="utf-8"), "PRE-EXISTING\n")

    def test_a_reserialization_mismatch_refuses_to_install(self):
        """`version` is not a lint field, so the rigged readback lints CLEAN and
        can only be caught by the byte-identity check."""
        self.target.write_text("PRE-EXISTING\n", encoding="utf-8")
        real = json.load
        json.load = lambda handle, **kw: document(version="0.8")
        try:
            with self.assertRaises(codebook_store.SerializationMismatchError) as caught:
                codebook_store.write_atomic(self.target, document(version="0.7"), "LBL")
        finally:
            json.load = real
        self.assertIn("re-serializing the readback does not reproduce the written bytes",
                      str(caught.exception))
        self.assertEqual(self.target.read_text(encoding="utf-8"), "PRE-EXISTING\n")

    def test_a_post_install_digest_mismatch_is_reported(self):
        """The digest is taken over the payload and RE-TAKEN from the installed
        file, because the bytes crossed a filesystem in between."""
        real = os.replace

        def swap(src, dst):
            real(src, dst)
            Path(dst).write_bytes(b"different bytes entirely\n")
        os.replace = swap
        try:
            with self.assertRaises(codebook_store.PostWriteDigestError) as caught:
                codebook_store.write_atomic(self.target, document(), "LBL")
        finally:
            os.replace = real
        self.assertIn("post-rename sha256 does not match the verified temp",
                      str(caught.exception))

    def test_an_interrupted_rename_raises_a_RAW_OSError(self):
        """THE RATIFIED A13 INTERRUPTION CONTROL, in the store's own terms.
        `foundry_verify_migration.negative_tests` asserts exactly this shape:
        the live file byte-identical, an inert `.tmp` left behind, and a RAW
        `OSError` — not something friendlier — reaching the caller."""
        self.target.write_text("GOOD OLD FILE\n", encoding="utf-8")
        before = hashlib.sha256(self.target.read_bytes()).hexdigest()
        real = os.replace

        def boom(src, dst):
            raise OSError("simulated crash between verify and rename")
        os.replace = boom
        try:
            with self.assertRaises(OSError) as caught:
                codebook_store.write_atomic(self.target, document(), "LBL")
        finally:
            os.replace = real
        self.assertIs(type(caught.exception), OSError)
        self.assertNotIsInstance(caught.exception, codebook_store.CodebookStoreError)
        self.assertEqual(hashlib.sha256(self.target.read_bytes()).hexdigest(), before)
        self.assertTrue(self.leftover.exists())

    def test_the_label_defaults_to_the_path(self):
        with self.assertRaises(codebook.LintError) as caught:
            codebook_store.write_atomic(self.target, document(status="actve"))
        self.assertIn(f"{self.target} (pre-write, in memory)", str(caught.exception))


# ===========================================================================
# 4. THE LEGACY FACADE
# ===========================================================================

class TestTheLegacyLoaderBoundary(unittest.TestCase):
    """C8.5P.V correction C2. THE VERIFIER CANNOT WITNESS THIS.

    `foundry_verify_migration`'s "/2 loader x /1 file" control asserts only that
    the subprocess exit code is non-zero. If `load_codebook` were aliased
    straight to `codebook_store.read`, an UNCAUGHT `SchemaMismatchError` would
    also exit non-zero, so that control would stay green while the legacy
    contract — a `STOP — ` line on stderr and exit 1 — had been silently
    replaced by a traceback. The verifier is a regression witness, not a
    wrapper-shape witness, and its source may not be edited. So the shape is
    asserted HERE, structurally, and the alias is rigged as a negative control."""

    @classmethod
    def setUpClass(cls):
        cls.fcb = load_legacy("foundry_codebook")
        cls.tree = ast.parse(inspect.getsource(cls.fcb))
        # `.get`, not `[...]`. Under the alias rig the name is not a FunctionDef
        # at all, and a KeyError in setUpClass would take the whole class down
        # with an error that names nothing. Every test below then reports the
        # actual defect instead of a fixture crash.
        cls.fn = {n.name: n for n in cls.tree.body
                  if isinstance(n, ast.FunctionDef)}.get("load_codebook")

    def require_wrapper(self):
        if self.fn is None:
            self.fail("`load_codebook` is not a module-level function in the "
                      "facade — it has been aliased or deleted, so the legacy "
                      "`STOP — `/exit-1 contract is gone. The verifier's /1 "
                      "control CANNOT see this: an uncaught typed error also "
                      "exits non-zero.")
        return self.fn

    def test_it_is_a_module_level_function_not_an_alias(self):
        self.assertIsInstance(self.require_wrapper(), ast.FunctionDef)
        self.assertIsNot(self.fcb.load_codebook, codebook_store.read)

    def test_it_keeps_the_exact_legacy_signature(self):
        params = inspect.signature(self.fcb.load_codebook).parameters
        self.assertEqual(list(params), ["path"])
        self.assertIsNone(params["path"].default)

    def test_it_delegates_to_the_permanent_read(self):
        calls = [ast.unparse(n.func) for n in ast.walk(self.require_wrapper())
                 if isinstance(n, ast.Call)]
        self.assertIn("_codebook_store.read", calls)
        for reimplemented in ("json.load", "open", "Path.exists"):
            with self.subTest(call=reimplemented):
                self.assertNotIn(reimplemented, calls)

    def test_it_resolves_the_default_path_here_not_in_the_store(self):
        body = ast.unparse(self.require_wrapper())
        self.assertIn("CODEBOOK_PATH", body)
        self.assertFalse(hasattr(codebook_store, "CODEBOOK_PATH"))

    def test_it_catches_exactly_the_two_contracted_read_errors(self):
        caught = []
        for node in ast.walk(self.require_wrapper()):
            if isinstance(node, ast.ExceptHandler):
                caught += [t.strip().replace("_codebook_store.", "")
                           for t in ast.unparse(node.type).strip("()").split(",")]
        self.assertEqual(sorted(caught),
                         ["CodebookNotFoundError", "SchemaMismatchError"])

    def test_it_MUST_NOT_catch_OSError_or_a_bare_Exception(self):
        """Asserted on handler TYPES, never on text: the docstring names these
        to explain the rule, and a textual guard would forbid its own
        explanation."""
        caught = set()
        for node in ast.walk(self.require_wrapper()):
            if isinstance(node, ast.ExceptHandler) and node.type is not None:
                t = node.type
                for part in (t.elts if isinstance(t, ast.Tuple) else [t]):
                    caught.add(ast.unparse(part).rsplit(".", 1)[-1])
        for banned in ("OSError", "JSONDecodeError", "UnicodeDecodeError",
                       "Exception", "BaseException"):
            with self.subTest(banned=banned):
                self.assertNotIn(banned, caught)

    def test_every_handler_ends_the_process_through_the_legacy_halt(self):
        for node in ast.walk(self.require_wrapper()):
            if isinstance(node, ast.ExceptHandler):
                calls = [ast.unparse(c.func) for c in ast.walk(node)
                         if isinstance(c, ast.Call)]
                self.assertIn("fc.halt", calls)

    def test_the_v1_guidance_text_lives_HERE_and_only_here(self):
        """C3's other half: the facade must still carry the exact legacy
        sentence, rebuilt from the typed error's structured attributes."""
        body = ast.unparse(self.require_wrapper())
        for required in ("experiments/foundry_migrate_codebook_v2.py",
                         "foundry_reconcile.py", "pre-migration",
                         "SCHEMA_V1", "error.actual"):
            with self.subTest(required=required):
                self.assertIn(required, body)


class TestTheLegacyWriterBoundary(TempTargetTestCase):

    @classmethod
    def setUpClass(cls):
        cls.fcb = load_legacy("foundry_codebook")
        cls.tree = ast.parse(inspect.getsource(cls.fcb))
        cls.functions = {n.name: n for n in cls.tree.body
                         if isinstance(n, ast.FunctionDef)}

    def test__serialize_is_the_permanent_function_object_itself(self):
        self.assertIs(self.fcb._serialize, codebook_store.serialize)
        self.assertNotIn("_serialize", self.functions)

    def test_the_writer_is_exactly_one_thin_translation_wrapper(self):
        fn = self.functions["write_codebook_atomic"]
        body = [n for n in fn.body if not (isinstance(n, ast.Expr)
                                           and isinstance(n.value, ast.Constant))]
        self.assertEqual(len(body), 1)
        self.assertIsInstance(body[0], ast.Try)
        trunk = body[0]
        self.assertEqual(len(trunk.body), 1)
        self.assertIsInstance(trunk.body[0], ast.Return)
        self.assertEqual(len(trunk.handlers), 1)
        self.assertEqual(len(trunk.handlers[0].body), 1)
        self.assertEqual(ast.unparse(trunk.handlers[0].body[0]),
                         "fc.halt(str(error))")

    def test_the_wrapper_calls_only_the_permanent_writer(self):
        calls = [ast.unparse(n.func) for n in
                 ast.walk(self.functions["write_codebook_atomic"])
                 if isinstance(n, ast.Call)]
        self.assertEqual(sorted(calls),
                         ["_codebook_store.write_atomic", "fc.halt", "str"])

    def test_the_wrapper_holds_no_persistence_logic_of_its_own(self):
        """No serialization, path construction, fsync, json, hashing, rename,
        validation or mutation may reappear here — that is the duplication the
        slice exists to end.

        Asserted on the AST with the DOCSTRING EXCLUDED. The first version of
        this guard scanned `ast.unparse` of the whole function and went red on
        the docstring, which names `os.replace` and `OSError` to explain the
        rule — a textual guard forbidding its own explanation, which is the trap
        this repository already has a ratified name for."""
        fn = self.functions["write_codebook_atomic"]
        body = [n for n in fn.body if not (isinstance(n, ast.Expr)
                                           and isinstance(n.value, ast.Constant))]
        source = "\n".join(ast.unparse(n) for n in body)
        for banned in ("json.", "hashlib", "os.replace", "os.fsync", "open(",
                       "with_suffix", "mkdir", "lint(", "encode", "Path("):
            with self.subTest(banned=banned):
                self.assertNotIn(banned, source)
        forbidden = (ast.If, ast.For, ast.While, ast.Compare, ast.With,
                     ast.Assign, ast.Dict, ast.List, ast.Subscript, ast.Raise)
        for node in body:
            for inner in ast.walk(node):
                self.assertNotIsInstance(inner, forbidden)

    def test_the_wrapper_catches_exactly_the_three_translated_failures(self):
        caught = []
        for node in ast.walk(self.functions["write_codebook_atomic"]):
            if isinstance(node, ast.ExceptHandler):
                caught += [t.strip() for t in
                           ast.unparse(node.type).strip("()").split(",")]
        self.assertEqual(sorted(caught),
                         sorted(["_codebook.LintError",
                                 "_codebook_store.SerializationMismatchError",
                                 "_codebook_store.PostWriteDigestError"]))

    def test_the_wrapper_MUST_NOT_catch_OSError_or_a_bare_Exception(self):
        """Catching either turns the ratified interruption control green while
        deleting what it proves.

        Asserted on the HANDLER TYPES, not on the source text — the docstring
        names `OSError` precisely to say it is not caught, and a text scan would
        make writing that sentence a failure."""
        caught = []
        for node in ast.walk(self.functions["write_codebook_atomic"]):
            if isinstance(node, ast.ExceptHandler):
                self.assertIsNotNone(node.type, "a bare `except:` catches OSError")
                caught += [t.strip() for t in
                           ast.unparse(node.type).strip("()").split(",")]
        for banned in ("OSError", "Exception", "BaseException"):
            with self.subTest(banned=banned):
                self.assertNotIn(banned, caught)

    def test_the_wrapper_keeps_the_legacy_signature(self):
        def shape(fn):
            return [(n, p.kind, p.default)
                    for n, p in inspect.signature(fn).parameters.items()]
        legacy = shape(self.fcb.write_codebook_atomic)
        self.assertEqual([n for n, _, _ in legacy],
                         ["path", "codebook", "path_label"])
        self.assertIsNone(legacy[2][2])

    # ---- runtime parity ---------------------------------------------------

    def halts_with(self, permanent, legacy, expected_error):
        with self.assertRaises(expected_error) as raised:
            permanent()
        buffer = io.StringIO()
        with contextlib.redirect_stderr(buffer):
            with self.assertRaises(SystemExit) as exited:
                legacy()
        self.assertEqual(exited.exception.code, 1)
        self.assertEqual(buffer.getvalue(), f"STOP — {raised.exception}\n")

    def test_a_valid_write_through_the_facade_matches_the_store(self):
        a, b = self.tmp / "a.json", self.tmp / "b.json"
        doc = document(quote="日本語")
        self.assertEqual(codebook_store.write_atomic(a, doc, "L"),
                         self.fcb.write_codebook_atomic(b, doc, "L"))
        self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_a_lint_failure_still_halts_at_the_facade(self):
        bad = document(status="actve")
        self.halts_with(
            lambda: codebook_store.write_atomic(self.tmp / "p.json", bad, "LBL"),
            lambda: self.fcb.write_codebook_atomic(self.tmp / "l.json", bad, "LBL"),
            codebook.LintError)

    def test_a_reserialization_mismatch_still_halts_at_the_facade(self):
        real = json.load
        json.load = lambda handle, **kw: document(version="0.8")
        try:
            self.halts_with(
                lambda: codebook_store.write_atomic(
                    self.tmp / "p.json", document(version="0.7"), "LBL"),
                lambda: self.fcb.write_codebook_atomic(
                    self.tmp / "p.json", document(version="0.7"), "LBL"),
                codebook_store.SerializationMismatchError)
        finally:
            json.load = real

    def test_an_interrupted_rename_still_escapes_the_facade_RAW(self):
        self.target.write_text("GOOD OLD FILE\n", encoding="utf-8")
        before = hashlib.sha256(self.target.read_bytes()).hexdigest()
        real = os.replace

        def boom(src, dst):
            raise OSError("simulated crash between verify and rename")
        os.replace = boom
        try:
            with self.assertRaises(OSError) as caught:
                self.fcb.write_codebook_atomic(self.target, document(), "LBL")
        finally:
            os.replace = real
        self.assertIs(type(caught.exception), OSError)
        self.assertEqual(hashlib.sha256(self.target.read_bytes()).hexdigest(), before)
        self.assertTrue(self.leftover.exists())


# ===========================================================================
# 5. A13 — THE INDEPENDENT VERIFIER STAYS INDEPENDENT
# ===========================================================================

class TestTheVerifierIndependenceBoundary(unittest.TestCase):
    """`foundry_verify_migration.py` is DENIED to this slice. This guards it; it
    does not touch it.

    A13's demand is a verification path on a SEPARATE CODE PATH from the writer.
    The risk this cut creates is not that the verifier breaks — it is that a
    later tidy-up hoists the now-permanent `codebook_store` import to module
    scope for convenience, collapsing the verifier onto the writer's vocabulary
    while every test stays green."""

    WRITER_MODULES = ("foundry_codebook", "foundry_migrate_codebook_v2",
                      "mtj_foundry.codebook", "mtj_foundry.codebook_store")

    @classmethod
    def setUpClass(cls):
        cls.verifier = load_legacy("foundry_verify_migration")
        cls.tree = ast.parse(inspect.getsource(cls.verifier))

    def imports_in(self, node):
        """Every module an import statement REACHES, in all three spellings.

        `from mtj_foundry import codebook_store` binds the same module as
        `import mtj_foundry.codebook_store`, and the first version of this guard
        recorded only `node.module` — so it saw `mtj_foundry` and matched
        nothing. Rigged, it stayed GREEN while the writer sat at the verifier's
        module scope: a guard blind to the one spelling anybody would actually
        write. Both the dotted target and the `from X import Y` join are
        recorded now."""
        found = []
        for child in ast.walk(node):
            if isinstance(child, ast.Import):
                found += [a.name for a in child.names]
            elif isinstance(child, ast.ImportFrom) and child.module:
                found.append(child.module)
                found += [f"{child.module}.{a.name}" for a in child.names]
        return found

    def test_no_writer_or_model_import_reaches_module_scope(self):
        for name in self.imports_in_module_scope():
            with self.subTest(name=name):
                self.assertNotIn(name, self.WRITER_MODULES)

    def imports_in_module_scope(self):
        found = []
        for node in self.tree.body:
            found += self.imports_in(node) if isinstance(
                node, (ast.Import, ast.ImportFrom)) else []
        return found

    def test_the_real_verify_path_imports_none_of_them(self):
        verify = next(n for n in self.tree.body
                      if isinstance(n, ast.FunctionDef) and n.name == "verify")
        for name in self.imports_in(verify):
            with self.subTest(name=name):
                self.assertNotIn(name, self.WRITER_MODULES)

    def test_verify_resolves_no_name_from_the_writer_or_the_model(self):
        """Not just "no import" — no NAME either. An alias bound elsewhere and
        used inside `verify()` would be the same collapse with an extra hop."""
        verify = next(n for n in self.tree.body
                      if isinstance(n, ast.FunctionDef) and n.name == "verify")
        aliases = {"fcb", "codebook_store", "_codebook", "_codebook_store"}
        used = {n.value.id for n in ast.walk(verify)
                if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)}
        self.assertEqual(used & aliases, set())

    def test_the_transitional_import_stays_confined_to_negative_tests(self):
        """It is allowed to exist — the negative tests are TESTING the writer —
        and it is allowed to exist in exactly one place."""
        holders = [n.name for n in self.tree.body
                   if isinstance(n, ast.FunctionDef)
                   and set(self.imports_in(n)) & set(self.WRITER_MODULES)]
        self.assertEqual(holders, ["negative_tests"])

    def test_the_shared_os_replace_interruption_rig_is_still_present(self):
        """The rig patches the SHARED `os` module, which is why the store must
        keep calling `os.replace` late-bound. If this assignment ever leaves the
        verifier, the control it powers has left with it."""
        source = inspect.getsource(self.verifier)
        self.assertIn("os.replace = boom", source)
        self.assertIn("os.replace = real_replace", source)


# ===========================================================================
# 6. W5 — THE AUTHORITY BOUNDARY, RE-AIMED
# ===========================================================================

class TestTheW5LocalWriterBoundary(unittest.TestCase):
    """P3 §17: the component that writes the operational codebook has no
    authority, network or process-spawn capability.

    The invariant is unchanged. Its SUBJECT moved, so the guard moved with it —
    from a source-token grep of a historical filename to the import graph of the
    permanent closure, resolved by module identity."""

    @classmethod
    def setUpClass(cls):
        cls.authority = load_legacy("foundry_authority")
        cls.closure = cls.authority._persistence_closure()

    def test_the_closure_is_the_store_and_the_model_and_nothing_else(self):
        self.assertEqual(set(self.closure), EXPECTED_CLOSURE)

    def test_closure_discovery_follows_BOTH_import_spellings(self):
        """The C8.5N.R2 defect, asserted directly on the shipped discovery rule.

        `_persistence_closure` used to follow only `ast.ImportFrom`, so
        `import mtj_foundry.paths` never entered the closure and the exact-set
        check never saw it. Feeding the shipped normalizer both spellings of the
        same edge must yield one identical identity — and it must be the FULL
        one, because `mtj_foundry` alone is what let a denied sibling through.
        """
        dotted = self.authority.normalized_imports("import mtj_foundry.paths")
        from_form = self.authority.normalized_imports(
            "from mtj_foundry import paths")
        self.assertEqual(dotted, from_form)
        self.assertEqual(dotted, {"mtj_foundry.paths"})
        self.assertNotIn("mtj_foundry", dotted)

        healthy_dotted = self.authority.normalized_imports(
            "import mtj_foundry.codebook")
        healthy_from = self.authority.normalized_imports(
            "from mtj_foundry import codebook")
        self.assertEqual(healthy_dotted, healthy_from, {"mtj_foundry.codebook"})

    def test_a_dotted_import_does_not_collapse_to_its_top_level_package(self):
        """The exact bug, in one line: `a.b.c` must never be scored as `a`."""
        self.assertEqual(self.authority.normalized_imports("import os.path"),
                         {"os.path"})
        self.assertEqual(
            self.authority.normalized_imports("import xml.etree.ElementTree as e"),
            {"xml.etree.ElementTree"})

    def test_a_relative_import_cannot_resolve_to_something_allowed(self):
        """Fails closed: a relative import keeps its dots and so matches no
        allowed identity, rather than silently normalizing to a permitted name."""
        self.assertEqual(self.authority.normalized_imports("from . import paths"),
                         {"."})
        self.assertEqual(
            self.authority.normalized_imports("from ..pkg import thing"),
            {"..pkg"})

    def test_the_shipped_normalizer_agrees_with_this_files_own(self):
        """Two independent implementations of one rule, compared over the real
        closure. If they ever disagree, one of them is the defect."""
        for name, src in self.closure.items():
            with self.subTest(module=name):
                self.assertEqual(self.authority.normalized_imports(src),
                                 normalized_imports(src))

    def test_each_closure_member_matches_its_exact_allowed_identity_set(self):
        expected = {"mtj_foundry.codebook_store": STORE_IMPORTS,
                    "mtj_foundry.codebook": MODEL_IMPORTS}
        self.assertEqual(set(self.closure), set(expected))
        for name, src in self.closure.items():
            with self.subTest(module=name):
                self.assertEqual(normalized_imports(src), expected[name])

    def test_the_closure_is_resolved_by_module_identity_not_a_filename(self):
        """A hardcoded `src/mtj_foundry/codebook_store.py` would be the same
        defect the old check had: a rename disarms it silently."""
        source = inspect.getsource(self.authority._persistence_closure)
        self.assertNotIn("codebook_store.py", source)
        self.assertNotIn("src/", source)
        self.assertIn("__file__", source)

    def test_the_retired_filename_grep_is_gone(self):
        source = inspect.getsource(self.authority)
        self.assertNotIn('"experiments" / "foundry_codebook.py"', source)

    def test_no_forbidden_dependency_is_reachable_from_the_closure(self):
        """Named prohibitions on top of the exact set, kept because they say
        WHY. Matched on the identity's root so `urllib.request` is caught as
        `urllib`, while the exact-set test above is what catches a denied
        sibling inside an allowed package."""
        for name, src in self.closure.items():
            roots = {i.split(".")[0] for i in normalized_imports(src)}
            with self.subTest(module=name):
                for banned in ("subprocess", "socket", "ssl", "http", "urllib",
                               "requests", "foundry_authority", "foundry_common"):
                    self.assertNotIn(banned, roots)

    def test_a_denied_permanent_sibling_is_rejected_in_either_spelling(self):
        """`mtj_foundry.paths` owns ProjectPaths and is denied to this store.
        Both spellings must fail the exact-set test — the root-based check above
        cannot see either, because their root is the ALLOWED `mtj_foundry`."""
        store_src = inspect.getsource(codebook_store)
        for spelling in ("from mtj_foundry import paths",
                         "import mtj_foundry.paths"):
            with self.subTest(spelling=spelling):
                # APPENDED, not substituted. An anchor-and-replace rig silently
                # no-ops the day the anchor's spelling changes -- and this test
                # is precisely about the store having two spellings available,
                # so it would have been the first casualty of its own subject.
                rigged = store_src + "\n" + spelling + "\n"
                identities = normalized_imports(rigged)
                self.assertIn("mtj_foundry.paths", identities)
                self.assertNotEqual(identities, STORE_IMPORTS)
                self.assertEqual(
                    {i.split(".")[0] for i in identities} - {"mtj_foundry"},
                    {i.split(".")[0] for i in STORE_IMPORTS} - {"mtj_foundry"},
                    "the root-only view is blind to this, which is the defect")

    def test_no_process_spawning_call_is_reachable_from_the_closure(self):
        for name, src in self.closure.items():
            calls = [ast.unparse(n.func) for n in ast.walk(ast.parse(src))
                     if isinstance(n, ast.Call)]
            for family in PROCESS_SPAWNING:
                with self.subTest(module=name, family=family):
                    self.assertFalse([c for c in calls if c.startswith(family)])

    def test_the_model_half_keeps_its_accepted_re_only_boundary(self):
        """The store's dependency is not exempt from the purity C8.5M accepted
        for it — the closure is only as local as its weakest member."""
        self.assertEqual(normalized_imports(self.closure["mtj_foundry.codebook"]),
                         MODEL_IMPORTS)


# ===========================================================================
# 5. THE FIRST REPOINTED CONSUMER (C8.5R)
# ===========================================================================

OBJECT_LATTICE = EXPERIMENTS / "foundry_object_lattice.py"


def read_call_sites(tree: ast.AST, dotted: str) -> list:
    """Every `ast.Call` whose unparsed func is exactly `dotted`."""
    return [n for n in ast.walk(tree)
            if isinstance(n, ast.Call) and ast.unparse(n.func) == dotted]


def enclosing_try(tree: ast.AST, node: ast.AST):
    """The innermost `ast.Try` whose BODY -- not its handlers -- contains `node`.

    Written on the body deliberately. A read moved into an `except` or a
    `finally` is still lexically "inside a try" and would pass a containment
    test that did not say which arm; `finally` in particular would run the read
    on the very failure path it is supposed to be protected from.
    """
    for candidate in ast.walk(tree):
        if not isinstance(candidate, ast.Try):
            continue
        if any(node is d for stmt in candidate.body for d in ast.walk(stmt)):
            return candidate
    return None


def handler_types(try_node) -> set:
    caught = set()
    for handler in try_node.handlers:
        if handler.type is None:
            caught.add("BARE")
            continue
        t = handler.type
        for part in (t.elts if isinstance(t, ast.Tuple) else [t]):
            caught.add(ast.unparse(part).rsplit(".", 1)[-1])
    return caught


def imported_module_names(tree: ast.AST) -> set:
    """Modules a file imports, by the name the import statement writes.

    Deliberately NOT `normalized_imports`: that one answers the permanent
    closure's question about `mtj_foundry.<sibling>` identity, and this one has
    to see a bare legacy `import foundry_codebook` as well.
    """
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
            names |= {f"{node.module}.{a.name}" for a in node.names}
    return names


def paths_view_bindings(tree: ast.AST) -> list:
    """`<name> = ProjectPaths.for_root(...)` assignments, as target names.

    The invariant is stated on the BINDING as well as on the call, because they
    are not the same claim: a second call bound to a second name is what moves
    the delegation census, and a second call that is never bound would still
    state the repository root twice.
    """
    bound = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) \
                and ast.unparse(node.value.func) == "ProjectPaths.for_root":
            bound += [ast.unparse(t) for t in node.targets]
    return bound


def attribute_reads(tree: ast.AST, base: str) -> set:
    return {n.attr for n in ast.walk(tree)
            if isinstance(n, ast.Attribute) and ast.unparse(n.value) == base}


class ObjectLatticeConsumer:
    """The C8.5R properties, derived from SOURCE so the rigs can be graded.

    A negative control has to be able to feed this a broken file. Asserting
    against the live module object instead would make four of the five rigs
    inexpressible, and the fifth would need an import that runs the module's
    whole CR parse.
    """

    def __init__(self, source: str):
        self.source = source
        self.tree = ast.parse(source)
        self.imports = imported_module_names(self.tree)
        self.views = paths_view_bindings(self.tree)
        self.for_root_calls = read_call_sites(self.tree, "ProjectPaths.for_root")
        self.reads = read_call_sites(self.tree, "codebook_store.read")
        self.legacy_loads = read_call_sites(self.tree, "fcb.load_codebook")

    @property
    def view(self):
        return self.views[0] if len(self.views) == 1 else None

    def write_report(self):
        return next(n for n in ast.walk(self.tree)
                    if isinstance(n, ast.FunctionDef) and n.name == "write_report")

    def protected_read(self):
        if len(self.reads) != 1:
            return None
        return enclosing_try(self.tree, self.reads[0])


class TestTheFirstRepointedConsumer(unittest.TestCase):
    """C8.5R. `experiments/foundry_object_lattice.py` reads the codebook through
    the permanent store, at the layout owner's explicit path.

    C8.5Q measured why this file could move and the other five could not.
    `fc.halt` raises `SystemExit`, which `except Exception` does NOT catch;
    `codebook_store` raises a `RuntimeError`, which it does. So the repoint
    changes the CLASS of the failure, and what that costs is decided entirely by
    the enclosing handler. The six seed consumers fall into THREE groups, not
    two, and the difference between the second and the third is the whole reason
    the other five are out of scope:

        except BaseException   this consumer               no delta -- both
                               (foundry_object_lattice)    classes are caught
                                                           and discarded alike

        except Exception       foundry_shape_extractor     a hard exit becomes a
                               foundry_system_map          SILENT FALLBACK; in
                                                           `codebook_covered_actions`
                                                           an empty set, which is a
                                                           wrong answer that reads
                                                           as clean

        no handler             foundry_cr_checks           exit 1 EITHER WAY. Not a
                               foundry_slug_dossier        fallback: the process
                               foundry_consolidate_run1    still dies, but a clean
                                                           `STOP -- ` line becomes a
                                                           traceback, and restoring
                                                           it would need the
                                                           consumer-local `fc.halt`
                                                           translation the
                                                           architecture forbids

    THE HANDLER IS THEREFORE THE SAFETY PROPERTY, NOT AN INCIDENTAL DETAIL, and
    it is asserted as one: the first negative control narrows it to `Exception`
    and this class must go red. Without that, a later tidy-up could delete the
    reason this slice was allowed to happen and nothing would notice.
    """

    @classmethod
    def setUpClass(cls):
        cls.source = OBJECT_LATTICE.read_text(encoding="utf-8")
        cls.c = ObjectLatticeConsumer(cls.source)

    # -- 1. the facade import is gone, not split -----------------------------

    def test_it_imports_the_permanent_store(self):
        self.assertIn("mtj_foundry.codebook_store", self.c.imports)

    def test_the_legacy_facade_is_referenced_nowhere_in_the_file(self):
        """`load_codebook` was this file's ONLY facade symbol, so the import
        goes entirely -- this is not a split import. Checked on identifiers as
        well as on import statements, because the call this replaced was itself
        a FUNCTION-SCOPED `import foundry_codebook as fcb`, and a guard reading
        only module-level imports would not have seen the thing it replaced."""
        self.assertNotIn("foundry_codebook", self.c.imports)
        self.assertEqual(self.c.legacy_loads, [])
        for node in ast.walk(self.c.tree):
            if isinstance(node, ast.Name):
                self.assertNotEqual(node.id, "foundry_codebook")
            if isinstance(node, ast.Attribute):
                self.assertNotEqual(node.attr, "load_codebook")

    # -- 2. exactly one layout view, feeding both facts ----------------------

    def test_there_is_exactly_one_ProjectPaths_view_and_one_for_root_call(self):
        self.assertEqual(len(self.c.for_root_calls), 1)
        self.assertEqual(len(self.c.views), 1)

    def test_the_one_view_is_built_from_the_delegated_root(self):
        call = self.c.for_root_calls[0]
        self.assertEqual([ast.unparse(a) for a in call.args], ["fc.REPO_ROOT"])

    def test_the_same_view_feeds_the_ratchet_and_the_codebook_path(self):
        """The C8.5Q census finding, asserted rather than restated: reading both
        properties off ONE view is what holds `delegations_by_provider` at
        126/22/1. A second view moves three counts while changing nothing."""
        self.assertIsNotNone(self.c.view, "not exactly one ProjectPaths view")
        self.assertEqual(attribute_reads(self.c.tree, self.c.view),
                         {"foundry_audit_baseline", "legacy_codebook_json"})

    def test_the_read_takes_its_path_from_that_view(self):
        self.assertEqual(len(self.c.reads), 1)
        self.assertEqual([ast.unparse(a) for a in self.c.reads[0].args],
                         [f"{self.c.view}.legacy_codebook_json"])

    def test_the_store_still_offers_no_default_path_to_fall_back_on(self):
        self.assertFalse(hasattr(codebook_store, "CODEBOOK_PATH"))

    # -- 3. the read stays inside the BaseException boundary -----------------

    def test_the_read_is_inside_a_try_body(self):
        self.assertIsNotNone(
            self.c.protected_read(),
            "the codebook read is not in the BODY of any try -- an unprotected "
            "read turns a swallowed failure into a crash")

    def test_that_try_catches_BaseException_and_nothing_narrower(self):
        self.assertEqual(handler_types(self.c.protected_read()), {"BaseException"})

    def test_the_failure_path_leaves_cb_axes_None(self):
        """Both halves. `cb_axes = None` is established BEFORE the try, and the
        handler assigns nothing. Either half alone permits a defect: a handler
        that re-raised, or a pre-set that a handler then overwrote."""
        try_node = self.c.protected_read()
        function = self.c.write_report()
        before = function.body[:function.body.index(try_node)]
        presets = [ast.unparse(n.value) for n in before
                   if isinstance(n, ast.Assign)
                   and [ast.unparse(t) for t in n.targets] == ["cb_axes"]]
        self.assertEqual(presets, ["None"])
        for handler in try_node.handlers:
            self.assertEqual([type(n).__name__ for n in handler.body], ["Pass"])

    def test_the_downstream_read_is_still_written_for_None(self):
        self.assertIn("if cb_axes else None", self.source)

    # -- 4. no consumer-local translation ------------------------------------

    def test_the_consumer_translates_nothing(self):
        """`no_duplicate_legacy_translation_in_consumers`. The three handler-less
        consumers were excluded from this slice precisely because they WOULD
        need an `except CodebookReadError: fc.halt(...)` of their own. This one
        must not grow one either, and it does not need to."""
        calls = [ast.unparse(n.func) for n in ast.walk(self.c.write_report())
                 if isinstance(n, ast.Call)]
        for translation in ("fc.halt", "sys.exit"):
            with self.subTest(call=translation):
                self.assertNotIn(translation, calls)
        caught = handler_types(self.c.protected_read())
        for typed in ("CodebookReadError", "CodebookNotFoundError",
                      "SchemaMismatchError", "CodebookStoreError"):
            with self.subTest(caught=typed):
                self.assertNotIn(typed, caught)

    def test_the_module_adds_no_bootstrap_and_no_second_root(self):
        """The permanent imports ride the bootstrap that is ALREADY THERE.

        Stated as a count, not as an absence. THE FIRST VERSION OF THIS TEST
        ASSERTED `sys.path` WAS NEVER TOUCHED AND WENT RED ON THE UNMODIFIED
        FILE: this module has carried its own legacy `sys.path.insert` since
        long before the refoundation, and that line is what lets the bare
        `import foundry_common` below it resolve at all. The C8.5R claim is that
        the count did not change and that the permanent imports sit AFTER the
        `foundry_common` line, which is what establishes the C8.5A package
        bootstrap -- not that this file has no bootstrap.
        """
        order = [ast.unparse(n) for n in self.c.tree.body
                 if isinstance(n, (ast.Import, ast.ImportFrom))]
        fc_at = next(i for i, line in enumerate(order) if "foundry_common" in line)
        for permanent in ("from mtj_foundry import codebook_store",
                          "from mtj_foundry.paths import ProjectPaths"):
            with self.subTest(imp=permanent):
                self.assertGreater(order.index(permanent), fc_at)

        mutations = [n for n in ast.walk(self.c.tree)
                     if isinstance(n, ast.Call)
                     and ast.unparse(n.func) in ("sys.path.insert",
                                                 "sys.path.append")]
        self.assertEqual(len(mutations), 1, "C8.5R must add no bootstrap")
        fc_import = next(n for n in self.c.tree.body
                         if isinstance(n, ast.Import)
                         and any(a.name == "foundry_common" for a in n.names))
        self.assertLess(mutations[0].lineno, fc_import.lineno)


class TestTheRepointGuardCanFail(unittest.TestCase):
    """Five negative controls, each aimed at the CODE PATH rather than at a
    tool's name.

    Every rig asserts its own substitution actually landed before grading the
    result. An anchor-and-replace rig that silently no-ops reads as a passing
    negative control, which is the worst available outcome for a test whose
    entire job is to be able to fail.
    """

    @classmethod
    def setUpClass(cls):
        cls.source = OBJECT_LATTICE.read_text(encoding="utf-8")

    def rig(self, old, new):
        self.assertIn(old, self.source,
                      "the rig anchor is gone -- this negative control is no "
                      "longer aimed at anything")
        rigged = self.source.replace(old, new)
        self.assertNotEqual(rigged, self.source)
        return ObjectLatticeConsumer(rigged)

    def test_narrowing_the_handler_to_Exception_is_caught(self):
        """The safety property itself. `except Exception` would not have caught
        today's `SystemExit`, so this narrowing is exactly the edit that makes
        the failure-class change observable."""
        c = self.rig("    except BaseException:", "    except Exception:")
        self.assertEqual(handler_types(c.protected_read()), {"Exception"})

    def test_reintroducing_the_legacy_facade_is_caught(self):
        c = self.rig("        cb_axes = codebook_store.read(",
                     "        import foundry_codebook as fcb\n"
                     "        cb_axes = codebook_store.read(")
        self.assertIn("foundry_codebook", c.imports)

    def test_a_second_ProjectPaths_view_is_caught(self):
        c = self.rig("RATCHET_BASELINE = PATHS.foundry_audit_baseline",
                     "_OTHER = ProjectPaths.for_root(fc.REPO_ROOT)\n"
                     "RATCHET_BASELINE = _OTHER.foundry_audit_baseline")
        self.assertEqual(len(c.for_root_calls), 2)
        self.assertEqual(len(c.views), 2)
        self.assertIsNone(c.view)

    def test_moving_the_read_out_of_the_protected_try_is_caught(self):
        """Dedented out of the `try` entirely, which is what a tidy-up that
        "simplifies away the pointless wrapper" would produce."""
        c = self.rig(
            "    cb_axes = None\n    try:\n",
            "    cb_axes = None\n"
            "    cb_axes = codebook_store.read(PATHS.legacy_codebook_json)['axes']\n"
            "    try:\n")
        self.assertEqual(len(c.reads), 2)
        self.assertIsNone(c.protected_read())

    def test_moving_the_read_into_the_handler_is_caught(self):
        """`enclosing_try` reads the BODY, not the whole statement. A read in
        the `except` arm is lexically inside a try and would pass a containment
        test that did not say which arm."""
        c = self.rig(
            "        cb_axes = codebook_store.read(PATHS.legacy_codebook_json)[\"axes\"]\n"
            "    except BaseException:\n"
            "        pass\n",
            "        pass\n"
            "    except BaseException:\n"
            "        cb_axes = codebook_store.read(PATHS.legacy_codebook_json)[\"axes\"]\n")
        self.assertEqual(len(c.reads), 1)
        self.assertIsNone(c.protected_read())


# ===========================================================================
# 6. THE SECOND REPOINTED CONSUMER (C8.5U)
# ===========================================================================

CR_CHECKS = EXPERIMENTS / "foundry_cr_checks.py"


def sys_path_mutations(tree: ast.AST) -> list:
    return [n for n in ast.walk(tree)
            if isinstance(n, ast.Call)
            and ast.unparse(n.func) in ("sys.path.insert", "sys.path.append")]


class CrChecksConsumer:
    """The C8.5U properties, derived from SOURCE so the rigs can be graded.

    Same reason as `ObjectLatticeConsumer` above: a negative control has to be
    able to feed this a broken file, and asserting against the imported module
    instead would make every rig inexpressible -- importing this one runs a full
    CR parse.
    """

    def __init__(self, source: str):
        self.source = source
        self.tree = ast.parse(source)
        self.imports = imported_module_names(self.tree)
        self.views = paths_view_bindings(self.tree)
        self.for_root_calls = read_call_sites(self.tree, "ProjectPaths.for_root")
        self.reads = read_call_sites(self.tree, "codebook_store.read")
        self.legacy_loads = (read_call_sites(self.tree, "fcb.load_codebook")
                             + read_call_sites(self.tree, "foundry_codebook.load_codebook"))
        self.inserts = sys_path_mutations(self.tree)

    @property
    def view(self):
        return self.views[0] if len(self.views) == 1 else None

    def coverage(self):
        return next((n for n in ast.walk(self.tree)
                     if isinstance(n, ast.FunctionDef) and n.name == "coverage"), None)


class TestTheSecondRepointedConsumer(unittest.TestCase):
    """C8.5U. `experiments/foundry_cr_checks.py` reads the codebook through the
    permanent store, at the layout owner's explicit path.

    WHY THIS CONSUMER MOVES WITHOUT A HANDLER ARGUMENT AT ALL. C8.5R could only
    move `foundry_object_lattice` because its `except BaseException` made the
    failure-class change unobservable. This file has NO enclosing handler --
    and, measured in C8.5T, no enclosing handler ANYWHERE: nothing in the
    repository imports `foundry_cr_checks`, so it is a pure CLI script. That is
    what makes C8.5S.V's `DISCARD_LEGACY_STOP_FORMAT` apply cleanly here: the
    process still dies nonzero on a missing or wrong-schema codebook, and only
    the stderr SHAPE changes.

    IT IS ALSO WHY `foundry_consolidate_run1` DID NOT SHIP IN THIS COHORT.
    C8.5T measured it as the second half of the same slice and found it is NOT a
    no-handler consumer: `foundry_r5_attribution` imports it and wraps the
    per-backup replay in `except SystemExit`, which the permanent
    `RuntimeError` escapes. A tolerated "HALTED" row became an aborted
    attribution run, so the cohort was cut to this one file.

    THE WRITE ORDERING IS PART OF THE SAFETY ARGUMENT, not a side note.
    `main()` writes `docs/cr-checks.json` before it calls `coverage()`, and
    calls it only under `--coverage`. The artifact is therefore already complete
    when the read can first fail, and the default invocation never reads the
    codebook at all.
    """

    @classmethod
    def setUpClass(cls):
        cls.source = CR_CHECKS.read_text(encoding="utf-8")
        cls.c = CrChecksConsumer(cls.source)

    # -- 1. the facade is gone entirely, not split ---------------------------

    def test_it_imports_the_permanent_store(self):
        self.assertIn("mtj_foundry.codebook_store", self.c.imports)

    def test_the_legacy_facade_is_referenced_nowhere_in_the_file(self):
        """`load_codebook` was this file's ONLY facade symbol -- measured in
        C8.5T as `fcb.<attr> == ['load_codebook']` with one call site -- so the
        import goes entirely. Checked on identifiers as well as on import
        statements, so an alias or a function-scoped re-import cannot slip back
        in under a different spelling."""
        self.assertNotIn("foundry_codebook", self.c.imports)
        self.assertEqual(self.c.legacy_loads, [])
        for node in ast.walk(self.c.tree):
            if isinstance(node, ast.Name):
                self.assertNotEqual(node.id, "foundry_codebook")
                self.assertNotEqual(node.id, "fcb")
            if isinstance(node, ast.Attribute):
                self.assertNotEqual(node.attr, "load_codebook")

    # -- 2. exactly one view, built from the RIGHT root ----------------------

    def test_there_is_exactly_one_ProjectPaths_view_and_one_for_root_call(self):
        self.assertEqual(len(self.c.for_root_calls), 1)
        self.assertEqual(len(self.c.views), 1)

    def test_the_one_view_is_built_from_the_boundary_root_and_not_the_local_one(self):
        """THE ARGUMENT IS THE ASSERTION, and it is not pedantry.

        This module's own module-level `REPO_ROOT` is
        `Path(__file__).resolve().parent` -- the `experiments` DIRECTORY, not
        the repository root; `OUT` compensates with `.parent`. Measured in
        C8.5T: building the view from it yields
        `experiments/experiments/out/foundry/codebook.json`. Both names are in
        scope on the same lines, so a guard that only counted views would pass
        on the wrong one.
        """
        call = self.c.for_root_calls[0]
        self.assertEqual([ast.unparse(a) for a in call.args], ["fc.REPO_ROOT"])

    def test_the_local_REPO_ROOT_is_still_the_experiments_bootstrap_path(self):
        """The trap above is only real while this stays true, so it is pinned
        rather than described. If the local name is ever corrected to the real
        root, this test fails and the comment gets re-read."""
        self.assertIn("REPO_ROOT = Path(__file__).resolve().parent\n", self.source)

    def test_the_read_takes_its_path_from_that_view(self):
        self.assertEqual(len(self.c.reads), 1)
        self.assertEqual([ast.unparse(a) for a in self.c.reads[0].args],
                         [f"{self.c.view}.legacy_codebook_json"])

    def test_no_local_codebook_path_derivation_survives(self):
        """The path comes from the owner or it does not come at all. A
        `fc.FOUNDRY_OUT_DIR / "codebook.json"` here would be a repository-
        relative layout fact restated outside the layout owner -- exactly the
        local site C8.5T required be retired rather than replaced."""
        self.assertNotIn("FOUNDRY_OUT_DIR", self.source)
        self.assertNotIn("CODEBOOK_PATH", self.source)

    def test_the_store_still_offers_no_default_path_to_fall_back_on(self):
        self.assertFalse(hasattr(codebook_store, "CODEBOOK_PATH"))

    # -- 3. no consumer-local translation ------------------------------------

    def test_the_consumer_translates_nothing_around_the_read(self):
        """`no_duplicate_legacy_translation_in_consumers`. Restoring the facade's
        `STOP -- ` line would need an `except CodebookReadError: fc.halt(...)`
        of its own, which is the architecture's forbidden shape -- and C8.5S.V
        ruled the line itself discardable precisely so that nobody would build
        it. The read is deliberately NOT inside any try."""
        self.assertIsNone(enclosing_try(self.c.tree, self.c.reads[0]),
                          "the permanent read has been wrapped in a try -- a "
                          "handler here is the local translation this slice "
                          "exists to avoid")
        calls = [ast.unparse(n.func) for n in ast.walk(self.c.coverage())
                 if isinstance(n, ast.Call)]
        for translation in ("fc.halt", "sys.exit"):
            with self.subTest(call=translation):
                self.assertNotIn(translation, calls)

    def test_no_typed_read_error_is_named_anywhere_in_the_file(self):
        for typed in ("CodebookReadError", "CodebookNotFoundError",
                      "SchemaMismatchError", "CodebookStoreError"):
            with self.subTest(caught=typed):
                self.assertNotIn(typed, self.source)

    # -- 4. no new bootstrap -------------------------------------------------

    def test_the_module_adds_no_bootstrap_and_rides_the_existing_one(self):
        """STATED AS A COUNT, NOT AS AN ABSENCE. C8.5R records that the absence
        form went red on an unmodified file: these legacy scripts have carried
        their own `sys.path.insert` since long before the refoundation, and that
        line is what lets the bare `import foundry_common` resolve at all. The
        C8.5U claim is that the count did not change and that the permanent
        imports sit AFTER the `foundry_common` line, which is what establishes
        the C8.5A package bootstrap."""
        self.assertEqual(len(self.c.inserts), 1, "C8.5U must add no bootstrap")
        order = [ast.unparse(n) for n in self.c.tree.body
                 if isinstance(n, (ast.Import, ast.ImportFrom))]
        fc_at = next(i for i, line in enumerate(order) if "foundry_common" in line)
        for permanent in ("from mtj_foundry import codebook_store",
                          "from mtj_foundry.paths import ProjectPaths"):
            with self.subTest(imp=permanent):
                self.assertGreater(order.index(permanent), fc_at)
        fc_import = next(n for n in self.c.tree.body
                         if isinstance(n, ast.Import)
                         and any(a.name == "foundry_common" for a in n.names))
        self.assertLess(self.c.inserts[0].lineno, fc_import.lineno)

    # -- 5. the write ordering that makes the discard safe -------------------

    def test_the_artifact_is_written_before_the_coverage_read_is_reachable(self):
        """The safety property behind C8.5S.V applying here at all, asserted
        structurally rather than trusted: in `main()`, the `OUT.write_text` call
        precedes the `coverage(...)` call, and `coverage` is reached only under
        `args.coverage`. So `docs/cr-checks.json` is complete on disk before the
        codebook read can fail, and the default invocation never reads it."""
        main = next(n for n in ast.walk(self.c.tree)
                    if isinstance(n, ast.FunctionDef) and n.name == "main")
        write = next(n for n in ast.walk(main) if isinstance(n, ast.Call)
                     and ast.unparse(n.func) == "OUT.write_text")
        call = next(n for n in ast.walk(main) if isinstance(n, ast.Call)
                    and ast.unparse(n.func) == "coverage")
        self.assertLess(write.lineno, call.lineno)
        guard = next(n for n in ast.walk(main) if isinstance(n, ast.If)
                     and ast.unparse(n.test) == "args.coverage")
        self.assertTrue(any(call is d for stmt in guard.body
                            for d in ast.walk(stmt)),
                        "coverage() is no longer gated behind --coverage")


class TestTheCrChecksRepointGuardCanFail(unittest.TestCase):
    """Six negative controls, each aimed at a CODE PATH rather than at a name.

    Every rig asserts its own substitution landed before grading the result: an
    anchor-and-replace that silently no-ops reads as a passing negative control,
    which is the worst available outcome for a test whose whole job is to be
    able to fail. Each rig also restores nothing -- it works on a STRING, so the
    file on disk is never touched.
    """

    @classmethod
    def setUpClass(cls):
        cls.source = CR_CHECKS.read_text(encoding="utf-8")

    def rig(self, old, new):
        self.assertIn(old, self.source,
                      "the rig anchor is gone -- this negative control is no "
                      "longer aimed at anything")
        rigged = self.source.replace(old, new)
        self.assertNotEqual(rigged, self.source)
        return CrChecksConsumer(rigged)

    def test_NC1_reintroducing_the_facade_import_is_caught(self):
        c = self.rig("from mtj_foundry import codebook_store       # noqa: E402",
                     "import foundry_codebook as fcb  # noqa: E402\n"
                     "from mtj_foundry import codebook_store       # noqa: E402")
        self.assertIn("foundry_codebook", c.imports)

    def test_NC2_replacing_the_permanent_read_with_the_facade_load_is_caught(self):
        c = self.rig("    cb = codebook_store.read(PATHS.legacy_codebook_json)",
                     "    cb = fcb.load_codebook()")
        self.assertEqual(c.reads, [])
        self.assertEqual(len(c.legacy_loads), 1)

    def test_NC3_a_local_codebook_path_derivation_is_caught(self):
        """The path-owner control. This is the edit that would reintroduce the
        retired local layout site under a new name."""
        c = self.rig("    cb = codebook_store.read(PATHS.legacy_codebook_json)",
                     '    cb = codebook_store.read(fc.FOUNDRY_OUT_DIR / "codebook.json")')
        self.assertEqual(len(c.reads), 1)
        self.assertNotEqual([ast.unparse(a) for a in c.reads[0].args],
                            ["PATHS.legacy_codebook_json"])
        self.assertIn("FOUNDRY_OUT_DIR", c.source)

    def test_NC4_a_local_fc_halt_translation_is_caught(self):
        """The exact shape the architecture forbids and C8.5S.V made
        unnecessary: catching the typed error to rebuild the legacy STOP line."""
        c = self.rig(
            "    cb = codebook_store.read(PATHS.legacy_codebook_json)",
            "    try:\n"
            "        cb = codebook_store.read(PATHS.legacy_codebook_json)\n"
            "    except codebook_store.CodebookReadError as error:\n"
            "        fc.halt(str(error))")
        self.assertEqual(len(c.reads), 1)
        self.assertIsNotNone(enclosing_try(c.tree, c.reads[0]))
        self.assertIn("CodebookReadError", handler_types(
            enclosing_try(c.tree, c.reads[0])))
        calls = [ast.unparse(n.func) for n in ast.walk(c.coverage())
                 if isinstance(n, ast.Call)]
        self.assertIn("fc.halt", calls)

    def test_NC5a_a_second_ProjectPaths_view_is_caught(self):
        c = self.rig("PATHS = ProjectPaths.for_root(fc.REPO_ROOT)",
                     "PATHS = ProjectPaths.for_root(fc.REPO_ROOT)\n"
                     "_OTHER = ProjectPaths.for_root(fc.REPO_ROOT)")
        self.assertEqual(len(c.for_root_calls), 2)
        self.assertEqual(len(c.views), 2)
        self.assertIsNone(c.view)

    def test_NC5b_a_second_sys_path_insert_is_caught(self):
        c = self.rig("sys.path.insert(0, str(REPO_ROOT))",
                     "sys.path.insert(0, str(REPO_ROOT))\n"
                     "sys.path.insert(0, str(REPO_ROOT.parent))")
        self.assertEqual(len(c.inserts), 2)

    def test_NC6_building_the_view_from_the_local_REPO_ROOT_is_caught(self):
        """The control that separates the two roots. Without it, every other
        assertion in the class still passes while the module reads
        `experiments/experiments/out/foundry/codebook.json` -- one view, one
        read, no facade, no translation, and the wrong file."""
        c = self.rig("PATHS = ProjectPaths.for_root(fc.REPO_ROOT)",
                     "PATHS = ProjectPaths.for_root(REPO_ROOT)")
        self.assertEqual(len(c.for_root_calls), 1)
        self.assertEqual([ast.unparse(a) for a in c.for_root_calls[0].args],
                         ["REPO_ROOT"])


# ===========================================================================
# 7. THE REUSABLE TRANSITIVE CONSUMER ANALYSIS (C8.5X)
# ===========================================================================
#
# C8.5V answered the transitive-handler question for fifteen candidates in
# prose. `codebook_consumer_analysis` answers it as code, and this section is
# what makes that answer gradeable: the live population, the nominated
# candidate's record, the ONE known transitive trap in the repository, and six
# synthetic fixtures whose shapes the live repository does not contain.
#
# The fixtures are not decoration. Five of the six axes below cannot be
# exercised against this repository at all — it has no `from foundry_codebook
# import load_codebook` importer, no try/finally around a reaching call, and no
# unresolvable frontier on a handled path — so a suite that only measured the
# live tree would ship those code paths untested and call the analyzer green.

from tests.refoundation import codebook_consumer_analysis as cca

# Derived once against the head this slice is based on, and asserted rather
# than inherited: C8.5V reported the same three numbers, and a carried-forward
# count is not a measurement.
EXPECTED_FAN_IN_FILES = 28
EXPECTED_READ_CALL_SITES = 25
EXPECTED_READ_OWNING_FILES = 19

REAUDIT_REL = "experiments/foundry_reaudit.py"
SHAPE_EXTRACTOR_REL = "experiments/foundry_shape_extractor.py"

# The fifteen C8.5V measured and nominated from. Written out, because the count
# alone cannot tell this population from a different one of the same size.
C8_5V_FIFTEEN = [f"experiments/foundry_{name}.py" for name in sorted([
    "any_damage_split", "authority", "axis_merge_pointer_correction",
    "cdr09_derive", "cdr09_walk", "consolidate_run1_apply",
    "consolidate_run1_classify", "consolidate_run1_enumerate",
    "definition_drift", "det_pass", "family_sweep", "gate0_scrub",
    "locality_backfill", "membership_move", "reaudit"])]
RUN1_REL = "experiments/foundry_consolidate_run1.py"
RUN1_CLASSIFY_REL = "experiments/foundry_consolidate_run1_classify.py"
R5_REL = "experiments/foundry_r5_attribution.py"

# A minimal legacy universe. Every fixture below is this dictionary with ONE
# thing changed, so a fixture's verdict is attributable to that one thing.
#
# `foundry_common.py` is present because the bootstrap axis is real: without a
# module that puts `src` on `sys.path`, every fixture would answer UNKNOWN on
# bootstrap and no other axis could be observed through it. Its stub also
# spells the insert through a NAME, which is the shape the live boundary uses
# and the shape a literal-only scan missed.
FIXTURE_COMMON = '''\
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
sys.path.insert(0, str(_SRC))


def halt(message):
    print(f"STOP - {message}", file=sys.stderr)
    sys.exit(1)
'''

# THE FIXTURE UNIVERSE CARRIES THE TRANSITION ITSELF (C8.5X.R1). The analyzer
# derives which failure classes change across the repoint by reading the facade
# that translates them and the halt it translates them into; a fixture without
# those two modules would answer UNKNOWN on every catchability question, and the
# eight controls below would grade nothing. So the fixture ships a facade whose
# `load_codebook` catches the store's typed read errors and halts, exactly the
# shape the live one has — which also means a rig can CHANGE that shape and the
# controls must follow it.
FIXTURE_STORE = '''\
class CodebookStoreError(RuntimeError):
    pass


class CodebookReadError(RuntimeError):
    pass


class CodebookNotFoundError(CodebookReadError):
    pass


class SchemaMismatchError(CodebookReadError):
    pass


def read(path):
    if not path.exists():
        raise CodebookNotFoundError(path)
    raise SchemaMismatchError(path)
'''

FIXTURE_FACADE = '''\
import foundry_common as fc
from mtj_foundry import codebook_store as _codebook_store


def load_codebook(path=None):
    try:
        return _codebook_store.read(path)
    except _codebook_store.CodebookNotFoundError as error:
        fc.halt(str(error))
    except _codebook_store.SchemaMismatchError as error:
        fc.halt(str(error))
'''

FIXTURE_CANDIDATE = '''\
import foundry_common as fc
import foundry_codebook as fcb


def owner():
    return fcb.load_codebook()


def entry():
    return owner()


def other():
    return 1
'''


def fixture_repository(files: dict) -> dict:
    """Analyze a synthetic universe written into a temp directory.

    A temp root has no `.git`, which is why `python_files` has a walk mode: a
    control that had to initialise a repository to be graded would be testing
    git as much as the analyzer.
    """
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        for name, source in files.items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source, encoding="utf-8")
        return cca.analyze_repository(root)


def record_for(analysis: dict, name: str) -> dict:
    return next(r for r in analysis["consumers"] if r["module"] == name)


class TestTheAnalyzerIsItselfReadOnly(unittest.TestCase):
    """The analyzer is code and gets audited like code.

    Its whole claim is that a repointing decision can be derived without running
    the thing being analyzed. A module that imported a legacy module to answer a
    question would be making the measurement by executing the subject — the
    habit this arc removes — and one that wrote a report would make a
    verification mutate tracked state, which C8 step 3 already closed."""

    @classmethod
    def setUpClass(cls):
        cls.source = Path(cca.__file__).read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_it_imports_only_the_standard_library(self):
        imported = {name.split(".")[0] for name in imported_module_names(self.tree)}
        self.assertEqual(imported - set(sys.stdlib_module_names), set())

    def test_it_imports_no_legacy_module_and_no_permanent_sibling(self):
        """Named separately from the stdlib test because they fail differently:
        a legacy import would EXECUTE the subject, and that is the defect."""
        for name in imported_module_names(self.tree):
            self.assertFalse(name.startswith("foundry_"), name)
            self.assertFalse(name.startswith("mtj_foundry"), name)

    def test_its_only_subprocess_is_a_read_only_git_query(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call) and \
                    ast.unparse(node.func).startswith("subprocess."):
                self.assertEqual(ast.unparse(node.func), "subprocess.run")
                self.assertIn("ls-files", ast.unparse(node.args[0]))

    def test_its_only_write_is_the_json_report_into_stdout(self):
        """Asserted with the analyzer's OWN write-call vocabulary, so the guard
        widens whenever that list does rather than drifting behind it — and
        stated as what it IS rather than as an absence. There is exactly one
        write-family call, it is `json.dump`, and its destination is
        `sys.stdout`; a report written to a path would be a verification that
        mutates repository state, which C8 step 3 closed."""
        analyzer = Path(cca.__file__)
        module = cca.Module(analyzer.parent, Path(analyzer.name))
        writes = cca.output_truth_boundary(module)["sites"]
        self.assertEqual([site["expr"] for site in writes], ["json.dump"])
        dumps = [n for n in ast.walk(self.tree) if isinstance(n, ast.Call)
                 and ast.unparse(n.func) == "json.dump"]
        self.assertEqual(len(dumps), 1)
        self.assertEqual(ast.unparse(dumps[0].args[1]), "sys.stdout")

    def test_it_opens_no_file_for_writing(self):
        """The other half, and a separate failure: `output_truth_boundary`
        reports `open(..., "w")` as a write, so a rewrite of the entry point that
        wrote a report through `open` instead of `json.dump` would move the test
        above and this one together, and neither alone would be enough."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                self.assertNotEqual(cca._is_write_call(node), "OPEN_FOR_WRITE")
                self.assertNotEqual(cca._is_write_call(node), "METHOD")


class TestTheLivePopulation(unittest.TestCase):
    """The three numbers C8.5V reported, re-derived by the shipped analyzer."""

    @classmethod
    def setUpClass(cls):
        cls.analysis = cca.analyze_repository(REPO_ROOT)

    def test_the_population_reproduces_the_accepted_C8_5V_arithmetic(self):
        population = self.analysis["population"]
        self.assertEqual(population["facade_fan_in_files"], EXPECTED_FAN_IN_FILES)
        self.assertEqual(population["facade_read_call_sites"],
                         EXPECTED_READ_CALL_SITES)
        self.assertEqual(population["facade_read_owning_files"],
                         EXPECTED_READ_OWNING_FILES)

    def test_the_three_numbers_are_three_different_questions(self):
        """Fan-in, call sites and owning files are not the same count, and the
        arc has already been warned not to equate a population with a yield.
        Every read-owning file is a fan-in file; the converse is false, and 25
        sites live in 19 files because three files read more than once."""
        population = self.analysis["population"]
        self.assertEqual(len(population["facade_fan_in"]),
                         population["facade_fan_in_files"])
        self.assertTrue(set(population["read_owning"])
                        <= set(population["facade_fan_in"]))
        self.assertGreater(population["facade_read_call_sites"],
                           population["facade_read_owning_files"])

    def test_the_two_already_repointed_consumers_are_absent(self):
        """Verified, not assumed. C8.5R and C8.5U moved these two off the
        facade read; if either reappeared, the population would still be 28/25/19
        only by coincidence."""
        for done in ("experiments/foundry_object_lattice.py",
                     "experiments/foundry_cr_checks.py"):
            self.assertNotIn(done, self.analysis["population"]["read_owning"])

    def test_the_analysis_is_byte_identical_on_a_second_run(self):
        again = cca.analyze_repository(REPO_ROOT)
        self.assertEqual(json.dumps(self.analysis, sort_keys=False),
                         json.dumps(again, sort_keys=False))


class TestTheNominatedCandidateRecord(unittest.TestCase):
    """`foundry_reaudit`, the candidate C8.5V nominated and C8.5W repointed's
    predecessor slice measured by hand. Every axis below was stated in that
    result; here the analyzer states it, so the next nomination is a query."""

    @classmethod
    def setUpClass(cls):
        cls.record = cca.analyze_consumer(REPO_ROOT, REAUDIT_REL)

    def test_exactly_one_read_site_and_main_owns_it(self):
        self.assertEqual(len(self.record["read_sites"]), 1)
        self.assertEqual(self.record["read_sites"][0]["owner"], "main")
        self.assertEqual(self.record["read_owner_functions"], ["main"])
        self.assertFalse(self.record["import_time_read"])

    def test_the_read_is_bound_through_the_module_alias(self):
        self.assertEqual(self.record["facade_bindings"]["aliases"], ["fcb"])
        self.assertEqual(self.record["facade_bindings"]["symbols"], {})
        self.assertFalse(self.record["facade_bindings"]["star"])

    def test_it_has_no_in_repository_caller_of_any_kind(self):
        self.assertEqual(self.record["static_importers"], [])
        self.assertEqual(self.record["dynamic_loader_sites"], [])
        self.assertEqual(self.record["reaching_call_paths"], [])

    def test_no_catching_handler_reaches_its_read(self):
        self.assertEqual(self.record["catching_handlers"], [])
        self.assertEqual(self.record["failure_observability"]["status"],
                         "UNOBSERVED_NO_REACHING_HANDLER")

    def test_the_facade_is_a_split_and_the_retained_symbol_is_named(self):
        self.assertIn("lint_or_halt",
                      self.record["facade_symbols_after_read_repoint"])
        self.assertEqual(self.record["facade_disposition"], "SPLIT")
        self.assertIn({"kind": "RETAINED_FACADE_SYMBOL", "detail": "lint_or_halt"},
                      self.record["blockers"])

    def test_the_bootstrap_chain_is_walked_and_not_assumed(self):
        """Two hops of evidence, not a constant: reaudit imports
        `foundry_common`, and `foundry_common` is what inserts `src`."""
        bootstrap = self.record["bootstrap_dependency"]
        self.assertEqual(bootstrap["status"], "SATISFIED_VIA_PROVIDER")
        self.assertEqual(bootstrap["chain"],
                         [REAUDIT_REL, "experiments/foundry_common.py"])

    def test_its_artifact_write_is_ordered_after_the_read(self):
        """The order IS the artifact-truth argument for this file, and it is the
        opposite of `foundry_cr_checks`, which writes first. Reaudit reads first,
        so no artifact is produced on any failure path."""
        boundary = self.record["output_truth_boundary"]
        self.assertEqual(boundary["ordered_after_read"], 1)
        self.assertEqual(boundary["ordered_before_read"], 0)
        self.assertEqual([s["expr"] for s in boundary["sites"]], ["out.write_text"])

    def test_a_string_replace_is_not_scored_as_an_artifact_write(self):
        """The probe defect this file's own quote normalizer would have caused.
        `f.replace(...)` and `q.replace(...)` are `str.replace`; a name-only
        write list scored both as output mutations of the codebook consumer."""
        self.assertIn("_PUNCT.sub", cca.Module(REPO_ROOT, Path(REAUDIT_REL)).source)
        exprs = [s["expr"] for s in self.record["output_truth_boundary"]["sites"]]
        self.assertNotIn("f.replace", exprs)
        self.assertNotIn("q.replace", exprs)


class TestTheKnownTransitiveTrapIsFoundMechanically(unittest.TestCase):
    """THE C8.5T REGRESSION CONTROL, ON THE REAL REPOSITORY.

    C8.5T found by hand that `foundry_r5_attribution` catches `SystemExit`
    across a module boundary, and that finding cut a two-file cohort to one
    AFTER the cohort had been drawn. `foundry_r5_attribution` has NO try around
    its call into `foundry_consolidate_run1` — the handler is in `main`, around a
    call to a function of its own that reaches it — so a file-local or even a
    call-site-local handler scan reports that file as unhandled.

    Both directions are asserted here, because the analyzer's value is entirely
    in telling them apart: the same `except SystemExit` in the same file is a
    BLOCKER for one candidate and NOT ATTRIBUTED for the other."""

    @classmethod
    def setUpClass(cls):
        cls.run1 = cca.analyze_consumer(REPO_ROOT, RUN1_REL)
        cls.classify = cca.analyze_consumer(REPO_ROOT, RUN1_CLASSIFY_REL)

    def test_the_transitive_handler_blocks_consolidate_run1(self):
        self.assertEqual(self.run1["classification"], "BLOCK_SYSTEMEXIT_DEPENDENCY")
        observing = self.run1["failure_observability"]["observing_handlers"]
        self.assertTrue(observing)
        for handler in observing:
            self.assertEqual(handler["caller"], R5_REL)
            self.assertEqual(handler["catches"], ["SystemExit"])
            self.assertEqual(handler["handler_origin"], "TRANSITIVE")
            self.assertIsNotNone(handler["through"])
            self.assertTrue(handler["reaches_read_owner"])
            # C8.5X.R1: the blocker is the CATCHABILITY delta, not the presence
            # of a catch. `except SystemExit` catches the legacy halt and none
            # of the permanent classes, so this row is genuinely old-only.
            catchability = handler["catchability"]
            self.assertEqual(catchability["transition"], "OLD_ONLY")
            self.assertTrue(catchability["legacy_caught"])
            self.assertEqual(catchability["permanent_caught"], "NONE")

    def test_no_handler_lexically_encloses_the_call_that_is_blocked(self):
        """The reason a call-site-local scan misses it, stated as a measurement
        rather than as a claim: every blocking handler here is TRANSITIVE, and
        the file has no DIRECT one around that call at all."""
        origins = {h["handler_origin"] for h in self.run1["catching_handlers"]
                   if h["caller"] == R5_REL and h["entry"] == "classify_run1_instances"}
        self.assertEqual(origins, {"TRANSITIVE"})

    def test_the_same_handler_is_not_charged_against_the_classifier(self):
        """`clf.classify_a15` IS lexically inside the `except SystemExit`, and
        it still cannot observe a read its call graph never reaches. Charging it
        would block a candidate C8.5V measured as safe."""
        self.assertEqual(self.classify["classification"],
                         "SAFE_NO_TRANSITIVE_HANDLER")
        not_reaching = self.classify["failure_observability"][
            "handled_calls_not_reaching_read"]
        self.assertTrue(any(h["caller"] == R5_REL and h["catches"] == ["SystemExit"]
                            for h in not_reaching))

    def test_the_fifteen_C8_5V_candidates_are_named_and_all_still_splits(self):
        """C8.5V's second axis, re-derived: no remaining candidate can DROP the
        facade, so fan-in cannot fall in this slice or a near one. Reported here
        because a record showing only the handler answer reads as 'ready'.

        NAMED, not counted. The first cut of this test asserted `len(...) == 15`
        over the SAFE set, and C8.5X.R1 moved one file out of that set for a
        reason unrelated to these fifteen -- the count stayed 15 and the test
        would have passed while measuring a different population."""
        analysis = cca.analyze_repository(REPO_ROOT)
        by_module = {r["module"]: r for r in analysis["consumers"]}
        for module in C8_5V_FIFTEEN:
            with self.subTest(module=module):
                self.assertEqual(by_module[module]["classification"],
                                 "SAFE_NO_TRANSITIVE_HANDLER")
                self.assertEqual(by_module[module]["facade_disposition"], "SPLIT")
        self.assertEqual(len(C8_5V_FIFTEEN), 15)

    def test_the_one_reclassified_file_is_explained_by_the_corrected_model(self):
        """C8.5X reported `foundry_shape_extractor` UNKNOWN because
        `foundry_gate_audit` calls into it under a catch whose reachability is
        unresolved. The catch is `except (Exception, SystemExit)`, which is
        SYMMETRIC -- it catches the legacy failure and the permanent one alike --
        so it cannot produce a class delta whether or not the call reaches the
        read, and the unresolved reachability stops being load-bearing.

        The reclassification is asserted WITH its cause. It is outside the
        fifteen above, and it is the only classification this repair moves."""
        record = cca.analyze_consumer(REPO_ROOT, SHAPE_EXTRACTOR_REL)
        self.assertEqual(record["classification"], "SAFE_NO_FAILURE_CLASS_DELTA")
        symmetric = record["failure_observability"]["symmetric_handlers"]
        self.assertTrue(symmetric)
        for handler in symmetric:
            self.assertEqual(handler["catchability"]["transition"], "SYMMETRIC_BOTH")
            self.assertTrue(handler["catchability"]["legacy_caught"])
            self.assertEqual(handler["catchability"]["permanent_caught"], "ALL")
        self.assertTrue(any(h["reaches_read_owner"] == "UNKNOWN"
                            for h in symmetric))
        self.assertEqual(record["failure_observability"]["observing_handlers"], [])


class TestTheSyntheticControls(unittest.TestCase):
    """Six fixtures, each a shape the live repository does not contain.

    Every one is graded on the SHIPPED analyzer, and every one is paired with a
    contrast that differs by one construct — so a fixture cannot pass because an
    unrelated assertion fired. The pinned value is the classification or the
    attribution itself, never merely 'something was found'."""

    def analyze(self, **overrides) -> dict:
        files = {"experiments/foundry_common.py": FIXTURE_COMMON,
                 "experiments/foundry_codebook.py": FIXTURE_FACADE,
                 "src/mtj_foundry/codebook_store.py": FIXTURE_STORE,
                 "experiments/candidate.py": FIXTURE_CANDIDATE}
        files.update(overrides)
        return fixture_repository(files)

    # -- TRANSITIVE_SYSTEMEXIT_REACHES_READ ----------------------------------

    TRANSITIVE_CALLER = '''\
import candidate


def replay():
    return candidate.entry()


def main():
    try:
        return replay()
    except SystemExit:
        return None
'''

    def test_TRANSITIVE_SYSTEMEXIT_REACHES_READ_blocks(self):
        """The permanent control for the C8.5T failure mode. The handler is two
        frames above the call into the candidate, and the call it encloses is a
        function of the CALLER."""
        analysis = self.analyze(**{"experiments/caller.py": self.TRANSITIVE_CALLER})
        record = record_for(analysis, "experiments/candidate.py")
        self.assertEqual(record["classification"], "BLOCK_SYSTEMEXIT_DEPENDENCY")
        handlers = record["failure_observability"]["observing_handlers"]
        self.assertEqual([h["handler_origin"] for h in handlers], ["TRANSITIVE"])
        self.assertEqual(handlers[0]["catches"], ["SystemExit"])
        self.assertEqual(handlers[0]["entry"], "entry")
        self.assertEqual(record["reaching_call_paths"][0]["reaching_paths"],
                         ["entry -> owner"])

    def test_the_same_fixture_without_the_handler_is_SAFE(self):
        """The contrast that makes the fixture non-vacuous: one construct
        removed, and the verdict moves. Without it, the BLOCK above could be
        coming from anything else in the fixture."""
        unhandled = self.TRANSITIVE_CALLER.replace(
            "    try:\n        return replay()\n    except SystemExit:\n"
            "        return None\n", "    return replay()\n")
        self.assertNotEqual(unhandled, self.TRANSITIVE_CALLER)
        analysis = self.analyze(**{"experiments/caller.py": unhandled})
        record = record_for(analysis, "experiments/candidate.py")
        self.assertEqual(record["classification"], "SAFE_NO_TRANSITIVE_HANDLER")
        self.assertEqual(record["failure_observability"]["observing_handlers"], [])

    # -- HANDLER_CALL_DOES_NOT_REACH_READ ------------------------------------

    def test_HANDLER_CALL_DOES_NOT_REACH_READ_is_not_attributed(self):
        """The same caller shape, aimed at a function whose call graph does not
        reach the read owner. The handler is real and is reported as real; what
        it may not do is count against this candidate."""
        caller = self.TRANSITIVE_CALLER.replace("candidate.entry()",
                                                "candidate.other()")
        analysis = self.analyze(**{"experiments/caller.py": caller})
        record = record_for(analysis, "experiments/candidate.py")
        self.assertEqual(record["classification"], "SAFE_NO_TRANSITIVE_HANDLER")
        self.assertEqual(record["failure_observability"]["observing_handlers"], [])
        not_reaching = record["failure_observability"][
            "handled_calls_not_reaching_read"]
        self.assertEqual([h["entry"] for h in not_reaching], ["other"])
        self.assertEqual(not_reaching[0]["catches"], ["SystemExit"])

    # -- TRY_FINALLY_IS_NOT_CATCH --------------------------------------------

    FINALLY_CALLER = '''\
import candidate


def main():
    try:
        return candidate.entry()
    finally:
        pass
'''

    def test_TRY_FINALLY_IS_NOT_CATCH(self):
        analysis = self.analyze(**{"experiments/caller.py": self.FINALLY_CALLER})
        record = record_for(analysis, "experiments/candidate.py")
        self.assertEqual(record["classification"], "SAFE_NO_TRANSITIVE_HANDLER")
        self.assertEqual(len(record["catching_handlers"]), 1)
        self.assertEqual(record["catching_handlers"][0]["catches"], [])
        self.assertFalse(record["catching_handlers"][0]["is_catching_handler"])
        self.assertTrue(record["catching_handlers"][0]["reaches_read_owner"])

    def test_the_same_try_with_an_except_arm_does_block(self):
        """One construct different, opposite verdict — and it pins WHICH block,
        so a fixture that merely stopped being SAFE would not pass."""
        catching = self.FINALLY_CALLER.replace("    finally:\n        pass\n",
                                               "    except Exception:\n"
                                               "        return None\n")
        analysis = self.analyze(**{"experiments/caller.py": catching})
        record = record_for(analysis, "experiments/candidate.py")
        self.assertEqual(record["classification"], "BLOCK_EXCEPTION_CATCH")
        self.assertEqual(record["catching_handlers"][0]["catches"], ["Exception"])

    # -- ALIAS_BINDING -------------------------------------------------------

    FROM_IMPORT_CANDIDATE = '''\
import foundry_common as fc
from foundry_codebook import load_codebook as load


def owner():
    return load()


def entry():
    return owner()


def other():
    return 1
'''

    NAME_ONLY_CANDIDATE = '''\
import foundry_common as fc


class Cache:
    def load_codebook(self):
        return {}


def owner(cache):
    # load_codebook() is named here, in a string, and on an unrelated object.
    return cache.load_codebook(), "fcb.load_codebook"


def entry(cache):
    return owner(cache)
'''

    def test_ALIAS_BINDING_resolves_both_import_forms_identically(self):
        """The two spellings are one read. Asserted as an equality between the
        two records' read axes rather than as two separate counts, because the
        claim is that they mean the same thing."""
        alias = record_for(self.analyze(), "experiments/candidate.py")
        other = record_for(
            self.analyze(**{"experiments/candidate.py": self.FROM_IMPORT_CANDIDATE}),
            "experiments/candidate.py")
        for record in (alias, other):
            self.assertEqual(len(record["read_sites"]), 1)
            self.assertEqual(record["read_sites"][0]["owner"], "owner")
            self.assertEqual(record["facade_symbols"], ["load_codebook"])
            self.assertEqual(record["facade_disposition"],
                             "DROP_AFTER_READ_REPOINT")
        self.assertEqual(alias["facade_bindings"]["aliases"], ["fcb"])
        self.assertEqual(other["facade_bindings"]["symbols"],
                         {"load": "load_codebook"})

    def test_the_name_without_a_binding_is_not_a_read(self):
        """The control for the other direction, and it carries the name THREE
        ways: in a comment, inside a string literal, and as a real method call on
        an unrelated object. A text search scores the first two; an AST search
        that skipped binding resolution scores the third. The file binds no
        facade, so it owns no read — `foundry_authority` really does define its
        own same-named helpers, so this collision is not hypothetical."""
        analysis = self.analyze(
            **{"experiments/candidate.py": self.NAME_ONLY_CANDIDATE})
        self.assertEqual(analysis["population"]["facade_read_call_sites"], 0)
        self.assertEqual(analysis["population"]["facade_read_owning_files"], 0)
        self.assertEqual(analysis["consumers"], [])

    # -- DYNAMIC_LOAD_NOT_AUTOMATIC_READ -------------------------------------

    DYNAMIC_CALLER = '''\
def load_legacy(name):
    import importlib
    return importlib.import_module(name)


class Harness:
    @classmethod
    def setUpClass(cls):
        cls.mod = load_legacy("candidate")

    def exercise(self):
        try:
            return self.mod.other()
        except Exception:
            return None
'''

    def test_DYNAMIC_LOAD_NOT_AUTOMATIC_READ(self):
        """The load is REPORTED — a static-import scan is blind to it — and it
        does not become a read-observing caller, because the function it calls
        does not reach the read owner and the read is not at module scope."""
        analysis = self.analyze(**{"tests/harness.py": self.DYNAMIC_CALLER})
        record = record_for(analysis, "experiments/candidate.py")
        self.assertEqual(record["static_importers"], [])
        self.assertEqual(len(record["dynamic_loader_sites"]), 1)
        self.assertEqual(record["dynamic_loader_sites"][0]["bindings"], ["mod"])
        self.assertFalse(record["import_time_read"])
        self.assertEqual(record["classification"], "SAFE_NO_TRANSITIVE_HANDLER")
        self.assertEqual(record["failure_observability"]["observing_handlers"], [])

    def test_the_same_dynamic_caller_reaching_the_read_does_block(self):
        """Reachability governs, not the loading mechanism. One attribute
        different, and the same dynamic load becomes a blocker."""
        reaching = self.DYNAMIC_CALLER.replace("self.mod.other()",
                                               "self.mod.entry()")
        analysis = self.analyze(**{"tests/harness.py": reaching})
        record = record_for(analysis, "experiments/candidate.py")
        self.assertEqual(len(record["dynamic_loader_sites"]), 1)
        self.assertEqual(record["classification"], "BLOCK_EXCEPTION_CATCH")

    # -- UNKNOWN_STAYS_UNKNOWN -----------------------------------------------

    OPAQUE_CANDIDATE = '''\
import foundry_common as fc
import foundry_codebook as fcb


def owner():
    return fcb.load_codebook()


def entry():
    return sorted([1, 2], key=owner)


def other():
    return 1
'''

    def test_UNKNOWN_STAYS_UNKNOWN(self):
        """`entry` hands `owner` to somebody else to call, so the graph cannot
        say the read is unreachable — only that it found no path. A negative
        reachability answer is exactly as good as the graph it was computed on,
        and this one is incomplete on the frontier of the very entry under
        test."""
        analysis = self.analyze(
            **{"experiments/candidate.py": self.OPAQUE_CANDIDATE,
               "experiments/caller.py": self.FINALLY_CALLER.replace(
                   "    finally:\n        pass\n",
                   "    except Exception:\n        return None\n")})
        record = record_for(analysis, "experiments/candidate.py")
        self.assertEqual(record["classification"], "UNKNOWN")
        self.assertEqual(record["reaching_call_paths"][0]["reaches_read_owner"],
                         "UNKNOWN")
        self.assertEqual(record["failure_observability"]["status"], "UNKNOWN")
        self.assertTrue(record["failure_observability"]["undecided_handlers"])
        self.assertNotEqual(record["classification"], "SAFE_NO_TRANSITIVE_HANDLER")

    def test_resolving_that_one_edge_is_what_makes_it_answerable(self):
        """The contrast: the same file with a direct call instead of a callback
        reaches a verdict. UNKNOWN here is a property of the evidence, not a
        blanket refusal — otherwise the axis would be useless in both
        directions."""
        resolved = self.OPAQUE_CANDIDATE.replace("sorted([1, 2], key=owner)",
                                                 "owner()")
        analysis = self.analyze(
            **{"experiments/candidate.py": resolved,
               "experiments/caller.py": self.FINALLY_CALLER.replace(
                   "    finally:\n        pass\n",
                   "    except Exception:\n        return None\n")})
        record = record_for(analysis, "experiments/candidate.py")
        self.assertEqual(record["classification"], "BLOCK_EXCEPTION_CATCH")

    def test_an_unresolved_bootstrap_cannot_be_reported_as_SAFE(self):
        """The second UNKNOWN path, and it is a different one: a universe where
        nothing puts `src` on `sys.path` cannot say the repoint would need no new
        bootstrap. ONE construct is removed — the insert — and the rest of the
        universe stands, so the failure model still derives and the bootstrap is
        the only thing unresolved. (An earlier version of this control dropped
        every other module too, which made it pass for whichever reason fired
        first.)"""
        analysis = self.analyze(**{
            "experiments/foundry_common.py": FIXTURE_COMMON.replace(
                'sys.path.insert(0, str(_SRC))\n', '')})
        record = record_for(analysis, "experiments/candidate.py")
        self.assertEqual(record["bootstrap_dependency"]["status"], "UNKNOWN")
        self.assertEqual(record["classification"], "UNKNOWN")
        self.assertEqual(analysis["failure_model"]["status"], "DERIVED")

# ===========================================================================
# 8. THE FAILURE-CLASS TRANSITION (C8.5X.R1)
# ===========================================================================
#
# C8.5X marked a handler as observing the read failure when it merely HAD a
# catch class, and the Manager rejected that (issue:1#issuecomment-5585684318).
# `except BaseException` catches the legacy `SystemExit` AND the permanent typed
# error, so the repoint changes nothing it observes -- which is precisely what
# C8.5R's accepted result says about `foundry_object_lattice`
# (issue:1#issuecomment-5563058243). The analyzer contradicted an accepted
# finding, and a conservative false blocker is still false.
#
# The repair derives the transition instead of naming it. These controls grade
# that derivation from BOTH ends: the model read out of the live repository, and
# nine catch shapes measured against a fixture universe that carries its own
# facade, store and halt -- eight of which do not exist anywhere in this
# repository, and one of which (`except SystemExit`) is the only one that does.


class TestTheDerivedFailureModel(unittest.TestCase):
    """The transition, read out of the two modules that perform it."""

    @classmethod
    def setUpClass(cls):
        cls.model = cca.analyze_repository(REPO_ROOT)["failure_model"]

    def test_the_model_is_derived_and_not_declared(self):
        self.assertEqual(self.model["status"], "DERIVED")
        self.assertIn("foundry_codebook.py:load_codebook", self.model["evidence"][0])
        self.assertIn("foundry_common.py:halt", self.model["evidence"][1])

    def test_the_legacy_class_comes_from_the_halt(self):
        """`fc.halt` calls `sys.exit`, so the legacy read failure is
        `SystemExit`. Derived through the facade's own import alias, not
        assumed from the name."""
        self.assertEqual(self.model["legacy_class"], "SystemExit")
        self.assertIn("sys.exit", self.model["evidence"][1])

    def test_the_permanent_classes_are_the_ones_the_facade_translates(self):
        """The facade IS the translation table: the classes it catches from the
        store are exactly the failures whose class changes. Everything it does
        not catch — `OSError`, `json.JSONDecodeError`, `UnicodeDecodeError` —
        propagates raw on both sides, which is why no pass-through list is
        needed anywhere in this module."""
        self.assertEqual(self.model["permanent_classes"],
                         ["CodebookNotFoundError", "SchemaMismatchError"])

    def test_the_stderr_side_effect_is_reported_and_not_collapsed(self):
        """The legacy STOP line disappears for a translated failure. That is an
        OUTPUT delta and it is reported here; it is deliberately not folded into
        catchability, because doing so is how a symmetric handler became a false
        SystemExit blocker."""
        self.assertIn("stderr", self.model["legacy_side_effect"])

    def test_the_interpreter_supplies_the_exception_tree(self):
        """`SystemExit` is not an `Exception`, and that single fact separates
        the old-only case from the symmetric one. It comes from the running
        interpreter's `__mro__`, never from a table written here."""
        hierarchy = cca.class_hierarchy({})
        self.assertIn("BaseException", cca.ancestors_of("SystemExit", hierarchy))
        self.assertNotIn("Exception", cca.ancestors_of("SystemExit", hierarchy))
        self.assertIsNone(cca.ancestors_of("NotAnExceptionAnywhere", hierarchy))


class TestHandlerCatchabilityAcrossTheTransition(unittest.TestCase):
    """Nine catch shapes, one construct apart, on the shipped analyzer.

    Every case below is the SAME fixture universe with the same reaching call,
    differing only in the `except` arm — so each is the others' contrast and no
    verdict can come from anything else. The intended `(legacy, permanent,
    transition, classification)` tuple is pinned in every case, not merely
    "something was found"."""

    def record_for_catch(self, arm: str, **overrides) -> dict:
        caller = ("import candidate\n\n\n"
                  "def main():\n"
                  "    try:\n"
                  "        return candidate.entry()\n"
                  f"    {arm}:\n"
                  "        return None\n")
        files = {"experiments/foundry_common.py": FIXTURE_COMMON,
                 "experiments/foundry_codebook.py": FIXTURE_FACADE,
                 "src/mtj_foundry/codebook_store.py": FIXTURE_STORE,
                 "experiments/candidate.py": FIXTURE_CANDIDATE,
                 "experiments/caller.py": caller}
        files.update(overrides)
        analysis = fixture_repository(files)
        self.assertEqual(analysis["failure_model"]["status"], "DERIVED")
        return record_for(analysis, "experiments/candidate.py")

    def assertCase(self, arm, legacy, permanent, transition, classification,
                   **overrides):
        record = self.record_for_catch(arm, **overrides)
        handlers = [h for h in record["catching_handlers"]
                    if h["is_catching_handler"]]
        self.assertEqual(len(handlers), 1)
        catchability = handlers[0]["catchability"]
        self.assertEqual(catchability["legacy_caught"], legacy)
        self.assertEqual(catchability["permanent_caught"], permanent)
        self.assertEqual(catchability["transition"], transition)
        self.assertTrue(handlers[0]["reaches_read_owner"])
        self.assertEqual(record["classification"], classification)
        return record

    def test_OLD_ONLY_SYSTEMEXIT(self):
        self.assertCase("except SystemExit", True, "NONE", "OLD_ONLY",
                        "BLOCK_SYSTEMEXIT_DEPENDENCY")

    def test_NEW_ONLY_EXCEPTION(self):
        """`except Exception` never caught the legacy halt and does catch the
        permanent error, so the repoint hands it a failure it now swallows."""
        self.assertCase("except Exception", False, "ALL", "NEW_ONLY",
                        "BLOCK_EXCEPTION_CATCH")

    def test_BOTH_BASEEXCEPTION(self):
        """THE C8.5R PRECEDENT, and the case C8.5X got wrong. Both sides are
        caught, so there is no catchability delta and neither asymmetric blocker
        may fire."""
        record = self.assertCase("except BaseException", True, "ALL",
                                 "SYMMETRIC_BOTH", "SAFE_NO_FAILURE_CLASS_DELTA")
        self.assertNotEqual(record["classification"], "BLOCK_SYSTEMEXIT_DEPENDENCY")
        self.assertNotEqual(record["classification"], "BLOCK_EXCEPTION_CATCH")
        self.assertEqual(record["failure_observability"]["status"],
                         "SYMMETRIC_CATCH_NO_CLASS_DELTA")
        self.assertEqual(record["failure_observability"]["observing_handlers"], [])
        self.assertTrue(record["failure_observability"]["symmetric_handlers"])

    def test_BOTH_BARE(self):
        record = self.assertCase("except", True, "ALL", "SYMMETRIC_BOTH",
                                 "SAFE_NO_FAILURE_CLASS_DELTA")
        self.assertEqual(record["catching_handlers"][0]["catches"], ["BARE"])

    def test_BOTH_TUPLE(self):
        self.assertCase("except (SystemExit, Exception)", True, "ALL",
                        "SYMMETRIC_BOTH", "SAFE_NO_FAILURE_CLASS_DELTA")

    def test_NEITHER_CODEBOOKSTOREERROR(self):
        """The store's read errors descend from `RuntimeError` DIRECTLY, not
        from `CodebookStoreError` — accepted store law — so this handler sees
        neither side. C8.5X had `CodebookStoreError` in a frozen catcher set and
        called it a permanent-read catcher."""
        self.assertCase("except _codebook_store.CodebookStoreError",
                        False, "NONE", "NEITHER", "SAFE_NO_TRANSITIVE_HANDLER")

    def test_NEW_ONLY_CODEBOOKREADERROR(self):
        self.assertCase("except CodebookReadError", False, "ALL", "NEW_ONLY",
                        "BLOCK_EXCEPTION_CATCH")

    def test_SAME_PASSTHROUGH(self):
        """`OSError` is raised identically on both sides — the facade translates
        it on neither — so catching it is not a transition. No pass-through list
        states this; it falls out of the ancestry test."""
        self.assertCase("except OSError", False, "NONE", "NEITHER",
                        "SAFE_NO_TRANSITIVE_HANDLER")

    def test_PARTIAL_OLD_ONLY_IS_STILL_A_CHANGE(self):
        """Catching the legacy class and only ONE of the two permanent classes
        is a change for the other, and the uncaught one is named rather than
        averaged away."""
        record = self.assertCase("except (SystemExit, CodebookNotFoundError)",
                                 True, "SOME", "PARTIAL_OLD_ONLY",
                                 "BLOCK_SYSTEMEXIT_DEPENDENCY")
        catchability = record["catching_handlers"][0]["catchability"]
        self.assertEqual(catchability["permanent_caught_classes"],
                         ["CodebookNotFoundError"])
        self.assertEqual(catchability["permanent_uncaught_classes"],
                         ["SchemaMismatchError"])

    def test_an_UNRESOLVABLE_handler_class_is_UNKNOWN_not_no(self):
        """A handler naming a class defined nowhere in the universe cannot be
        ruled out as an ancestor of either side, so its catchability is UNKNOWN
        and the candidate follows it. Answering "no" here is the same error as
        answering "unreachable" from an incomplete call graph: an absence of
        evidence read as evidence."""
        record = self.record_for_catch("except SomeClassDefinedNowhere")
        catchability = record["catching_handlers"][0]["catchability"]
        self.assertEqual(catchability["transition"], "UNKNOWN")
        self.assertEqual(record["classification"], "UNKNOWN")
        self.assertNotEqual(record["classification"], "SAFE_NO_TRANSITIVE_HANDLER")

    def test_a_definitely_catching_class_is_not_made_uncertain_by_a_second_name(self):
        """The contrast, and it is the reason `catches` returns on the first
        True. `except (BaseException, SomeClassDefinedNowhere)` already catches
        both sides whatever the second name turns out to be; reporting UNKNOWN
        there would make every handler with a project-specific class unreadable."""
        self.assertCase("except (BaseException, SomeClassDefinedNowhere)",
                        True, "ALL", "SYMMETRIC_BOTH", "SAFE_NO_FAILURE_CLASS_DELTA")

    # -- the two rigs that prove the model is READ, not assumed --------------

    def test_the_class_hierarchy_is_parsed_from_the_store_source(self):
        """One base class changed in the fixture store, and `CodebookStoreError`
        flips from catching NEITHER side to catching the permanent one. Nothing
        else in the universe moves. A hardcoded hierarchy could not follow it."""
        rigged = FIXTURE_STORE.replace("class CodebookReadError(RuntimeError):",
                                       "class CodebookReadError(CodebookStoreError):")
        self.assertNotEqual(rigged, FIXTURE_STORE)
        self.assertCase("except _codebook_store.CodebookStoreError",
                        False, "ALL", "NEW_ONLY", "BLOCK_EXCEPTION_CATCH",
                        **{"src/mtj_foundry/codebook_store.py": rigged})

    def test_a_facade_that_translates_nothing_makes_catchability_UNKNOWN(self):
        """The transition is derived FROM the facade, so a facade that no longer
        halts leaves the model unable to say what changes — and UNKNOWN is the
        answer, never SAFE and never a blocker. This is the rig that proves the
        eight cases above are reading the fixture rather than a constant."""
        rigged = FIXTURE_FACADE.replace("        fc.halt(str(error))",
                                        "        raise")
        self.assertNotEqual(rigged, FIXTURE_FACADE)
        caller = ("import candidate\n\n\n"
                  "def main():\n"
                  "    try:\n"
                  "        return candidate.entry()\n"
                  "    except SystemExit:\n"
                  "        return None\n")
        analysis = fixture_repository({
            "experiments/foundry_common.py": FIXTURE_COMMON,
            "experiments/foundry_codebook.py": rigged,
            "src/mtj_foundry/codebook_store.py": FIXTURE_STORE,
            "experiments/candidate.py": FIXTURE_CANDIDATE,
            "experiments/caller.py": caller})
        self.assertEqual(analysis["failure_model"]["status"], "UNKNOWN")
        record = record_for(analysis, "experiments/candidate.py")
        self.assertEqual(record["catching_handlers"][0]["catchability"]["transition"],
                         "UNKNOWN")
        self.assertEqual(record["classification"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
