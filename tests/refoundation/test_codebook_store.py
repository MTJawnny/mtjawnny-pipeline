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
import tempfile
import unittest
from pathlib import Path

from tests.refoundation.test_gate2_purity import load_legacy

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


if __name__ == "__main__":
    unittest.main()
