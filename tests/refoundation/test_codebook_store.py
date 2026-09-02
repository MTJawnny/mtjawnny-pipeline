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

EXPECTED_ALL = [
    "CodebookStoreError",
    "PostWriteDigestError",
    "SerializationMismatchError",
    "serialize",
    "write_atomic",
]

# The exact dependency set C8.5N allows the store to reach.
ALLOWED_IMPORTS = {"__future__", "hashlib", "json", "os", "pathlib", "mtj_foundry"}

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

    def test_the_public_api_is_exactly_the_contracted_five(self):
        self.assertEqual(sorted(codebook_store.__all__), EXPECTED_ALL)
        self.assertEqual(len(codebook_store.__all__), 5)
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

    def test_it_exposes_no_loader_default_path_backup_or_generic_hash(self):
        """The four capabilities C8.5N deliberately did NOT take."""
        for absent in ("load", "load_codebook", "read", "CODEBOOK_PATH",
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
        imported = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imported |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertEqual(imported, ALLOWED_IMPORTS)

    def test_its_only_permanent_dependency_is_the_codebook_model(self):
        reached = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ImportFrom) and node.module == "mtj_foundry":
                reached |= {a.name for a in node.names}
        self.assertEqual(reached, {"codebook"})

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
        self.assertEqual(sorted(self.closure),
                         ["mtj_foundry.codebook", "mtj_foundry.codebook_store"])

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
        for name, src in self.closure.items():
            tree = ast.parse(src)
            imported = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported |= {a.name.split(".")[0] for a in node.names}
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".")[0])
            with self.subTest(module=name):
                for banned in ("subprocess", "socket", "ssl", "http", "urllib",
                               "requests", "foundry_authority", "foundry_common"):
                    self.assertNotIn(banned, imported)

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
        imported = set()
        for node in ast.walk(ast.parse(self.closure["mtj_foundry.codebook"])):
            if isinstance(node, ast.Import):
                imported |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertEqual(imported, {"__future__", "re"})


if __name__ == "__main__":
    unittest.main()
