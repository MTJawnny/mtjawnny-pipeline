"""C8.5G — the CORPUS_ACCESS_AND_CARD_HELPERS capability, and its oracle.

This is a CLEAN REIMPLEMENTATION, not a move. `experiments/tier_engine.py` is
untouched and keeps its own copies for its ten other consumers; the two
implementations coexist, and these tests are what makes "equivalent" a measured
claim instead of an impression.

TWO KINDS OF EQUIVALENCE, on purpose:

* **Successful values are VALUE_EXACT.** Same corpus in, identical results out —
  key set, key ORDER, records, per-face output, normalized names, and the name
  index including the order of ids under a shared name.
* **Error behavior is deliberately NOT identical at the library boundary.** The
  legacy loader prints and calls `sys.exit(1)`. A library may not end the
  process, so `mtj_foundry.corpus` raises `CorpusLoadError` and the transitional
  `foundry_common` facade turns that back into the old `halt()`. Legacy callers
  keep the behavior they had; the permanent library does not inherit it.

THE FULL-CORPUS DIFFERENTIAL SKIPS WITHOUT THE CORPUS. `data/raw/` is gitignored
card data, so a clean checkout cannot run it. It is not a substitute for the
fixtures below and the fixtures are not a substitute for it — C8.5G required
both, and the Worker result records the full-corpus run.
"""

from __future__ import annotations

import gzip
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT, SRC

from mtj_foundry import corpus
from mtj_foundry.paths import ProjectPaths

EXPERIMENTS = REPO_ROOT / "experiments"
CORPUS_FILE = ProjectPaths.for_root(REPO_ROOT).legacy_oracle_cards


def legacy_engine():
    """The ORACLE: tier_engine, imported exactly as legacy callers reach it."""
    if str(EXPERIMENTS) not in sys.path:
        sys.path.insert(0, str(EXPERIMENTS))
    import tier_engine
    return tier_engine


def write_corpus(directory: Path, records) -> Path:
    """A gzip JSONL corpus. `records` may be dicts or raw lines."""
    path = directory / "corpus.jsonl.gz"
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        for record in records:
            handle.write(record if isinstance(record, str)
                         else json.dumps(record))
            handle.write("\n")
    return path


MULTI_FACE = {
    "oracle_id": "m1", "name": "Delver of Secrets // Insectile Aberration",
    "card_faces": [
        {"name": "Delver of Secrets", "oracle_text": "At the beginning of your upkeep, look at the top card.",
         "mana_cost": "{U}", "type_line": "Creature — Human Wizard", "power": "1", "toughness": "1"},
        {"name": "Insectile Aberration", "oracle_text": "Flying",
         "mana_cost": None, "type_line": "Creature — Human Insect", "power": "3", "toughness": "2"},
    ],
    "oracle_text": "",
}
SINGLE_FACE = {"oracle_id": "s1", "name": "Storm Crow", "oracle_text": "Flying",
               "mana_cost": "{1}{U}", "type_line": "Creature — Bird", "power": "1", "toughness": "2"}
# A face whose oracle_text and type_line are absent, and one where they are
# empty: the fallbacks are `""` for text, `None` for mana/power/toughness.
SPARSE_FACES = {"oracle_id": "p1", "name": "Sparse", "card_faces": [
    {"name": "Front"},
    {"name": "", "oracle_text": "", "mana_cost": None, "type_line": "", "power": None, "toughness": None},
]}
NO_TEXT_SINGLE = {"oracle_id": "n1", "name": "Vanilla Bear", "type_line": "Creature — Bear"}
DUP_A = {"oracle_id": "d1", "name": "Storm Crow", "oracle_text": "Flying"}
DUP_B = {"oracle_id": "d2", "name": "  STORM CROW  ", "oracle_text": "Flying"}

FIXTURE_CARDS = [MULTI_FACE, SINGLE_FACE, SPARSE_FACES, NO_TEXT_SINGLE, DUP_A, DUP_B]


class TestTheCapabilityMatchesItsOracleOnFixtures(unittest.TestCase):
    """VALUE_EXACT against tier_engine on shapes chosen to break a careless port."""

    @classmethod
    def setUpClass(cls):
        cls.engine = legacy_engine()

    def test_load_cards_agrees_including_key_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_corpus(Path(tmp), FIXTURE_CARDS)
            legacy = self.engine.load_cards(path)
            new = corpus.load_cards(path)
        self.assertEqual(list(legacy), list(new))
        self.assertEqual(legacy, new)

    def test_card_faces_agrees_on_every_fixture_shape(self):
        for card in FIXTURE_CARDS:
            with self.subTest(card=card["name"]):
                self.assertEqual(self.engine.get_raw_faces(card),
                                 corpus.card_faces(card))

    def test_a_multi_face_card_is_split_not_joined(self):
        faces = corpus.card_faces(MULTI_FACE)
        self.assertEqual(len(faces), 2)
        self.assertEqual([f["oracle_text"] for f in faces],
                         ["At the beginning of your upkeep, look at the top card.",
                          "Flying"])
        self.assertEqual(faces, self.engine.get_raw_faces(MULTI_FACE))

    def test_a_single_face_card_falls_back_to_the_root_fields(self):
        self.assertEqual(corpus.card_faces(SINGLE_FACE),
                         self.engine.get_raw_faces(SINGLE_FACE))
        self.assertEqual(corpus.card_faces(SINGLE_FACE)[0]["oracle_text"], "Flying")

    def test_absent_and_empty_face_fields_take_the_documented_fallbacks(self):
        faces = corpus.card_faces(SPARSE_FACES)
        self.assertEqual(faces, self.engine.get_raw_faces(SPARSE_FACES))
        self.assertEqual(faces[0]["oracle_text"], "")
        self.assertEqual(faces[0]["type_line"], "")
        self.assertIsNone(faces[0]["mana_cost"])
        # an EMPTY face name falls back to the card name, exactly as legacy
        self.assertEqual(faces[1]["name"], "Sparse")

    def test_a_single_face_card_with_no_oracle_text_yields_empty_string(self):
        self.assertEqual(corpus.card_faces(NO_TEXT_SINGLE),
                         self.engine.get_raw_faces(NO_TEXT_SINGLE))
        self.assertEqual(corpus.card_faces(NO_TEXT_SINGLE)[0]["oracle_text"], "")

    def test_normalize_name_agrees(self):
        for name in ("Storm Crow", "  STORM CROW  ", "Æther Vial", "ﬁ ligature",
                     "Jötun Grunt", ""):
            with self.subTest(name=name):
                self.assertEqual(self.engine.normalize_name(name),
                                 corpus.normalize_name(name))

    def test_a_duplicate_normalized_name_keeps_EVERY_id_in_order(self):
        """Two different cards genuinely share a normalized name. Collapsing
        them to one id is a silent data loss that a spot check would miss."""
        cards = {"d1": DUP_A, "d2": DUP_B}
        index = corpus.build_name_index(cards)
        self.assertEqual(index["storm crow"], ["d1", "d2"])
        self.assertEqual(index, self.engine.build_name_index(cards))

    def test_a_duplicate_oracle_id_is_last_write_wins(self):
        """The OTHER duplicate rule, and it points the opposite way. The loader
        assigns by key, so a repeated oracle_id overwrites. Preserved on
        purpose rather than 'fixed' into first-wins or a collision error."""
        first = {"oracle_id": "x", "name": "First"}
        second = {"oracle_id": "x", "name": "Second"}
        with tempfile.TemporaryDirectory() as tmp:
            path = write_corpus(Path(tmp), [first, second])
            legacy = self.engine.load_cards(path)
            new = corpus.load_cards(path)
        self.assertEqual(new["x"]["name"], "Second")
        self.assertEqual(legacy, new)

    def test_blank_lines_are_skipped_by_both(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_corpus(Path(tmp), [SINGLE_FACE, "", "   ", DUP_A])
            self.assertEqual(self.engine.load_cards(path), corpus.load_cards(path))
            self.assertEqual(len(corpus.load_cards(path)), 2)


class TestTheFullCorpusDifferential(unittest.TestCase):
    """The real thing, when the gitignored corpus is present locally."""

    @classmethod
    def setUpClass(cls):
        if not CORPUS_FILE.exists():
            raise unittest.SkipTest(
                f"the local corpus {CORPUS_FILE} is absent; the fixture "
                "differential above still runs, and C8.5G's Worker result "
                "records the full-corpus outcome")
        cls.engine = legacy_engine()
        cls.legacy = cls.engine.load_cards(CORPUS_FILE)
        cls.new = corpus.load_cards(CORPUS_FILE)

    def test_key_set_and_order_are_identical(self):
        self.assertEqual(list(self.legacy), list(self.new))

    def test_every_record_is_identical(self):
        self.assertEqual(self.legacy, self.new)

    def test_card_faces_is_VALUE_EXACT_for_every_card(self):
        bad = [k for k in self.legacy
               if self.engine.get_raw_faces(self.legacy[k]) != corpus.card_faces(self.new[k])]
        self.assertEqual(bad, [])

    def test_multi_face_cards_were_actually_exercised(self):
        """Otherwise the sweep above could pass on single-face cards alone."""
        multi = sum(1 for c in self.legacy.values() if c.get("card_faces"))
        self.assertGreater(multi, 1000, multi)

    def test_the_name_index_is_identical_including_duplicate_groups(self):
        legacy_index = self.engine.build_name_index(self.legacy)
        new_index = corpus.build_name_index(self.new)
        self.assertEqual(list(legacy_index), list(new_index))
        self.assertEqual(legacy_index, new_index)
        duplicates = {k: v for k, v in legacy_index.items() if len(v) > 1}
        self.assertGreater(len(duplicates), 0, "no shared normalized names found")


class TestTheLibraryErrorBoundary(unittest.TestCase):
    """The permanent library raises. It does not print and it does not exit."""

    def test_a_missing_file_raises_CorpusLoadError(self):
        with self.assertRaises(corpus.CorpusLoadError) as caught:
            corpus.load_cards(Path("/definitely/not/here/corpus.jsonl.gz"))
        self.assertIn("not found", str(caught.exception))

    def test_malformed_json_raises_CorpusLoadError_naming_the_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_corpus(Path(tmp), [SINGLE_FACE, "{not json", DUP_A])
            with self.assertRaises(corpus.CorpusLoadError) as caught:
                corpus.load_cards(path)
        self.assertIn("line 2", str(caught.exception))
        self.assertIn("JSON parse failure", str(caught.exception))

    def test_a_missing_oracle_id_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_corpus(Path(tmp), [{"name": "No Id"}])
            with self.assertRaises(corpus.CorpusLoadError) as caught:
                corpus.load_cards(path)
        self.assertIn("missing oracle_id", str(caught.exception))

    def test_an_EMPTY_oracle_id_raises_too(self):
        """`not card["oracle_id"]`, not just absence — an empty string would key
        the dict on "" and silently merge every such record."""
        with tempfile.TemporaryDirectory() as tmp:
            path = write_corpus(Path(tmp), [{"oracle_id": "", "name": "Empty Id"}])
            with self.assertRaises(corpus.CorpusLoadError):
                corpus.load_cards(path)

    def test_the_library_neither_prints_nor_exits_on_any_of_them(self):
        """Run in a subprocess so a SystemExit or a stray write would be visible
        rather than caught by this process's own machinery."""
        code = (
            "import sys, gzip, json, tempfile, pathlib\n"
            f"sys.path.insert(0, {str(SRC)!r})\n"
            "from mtj_foundry import corpus\n"
            "tmp = tempfile.mkdtemp(); p = pathlib.Path(tmp) / 'c.jsonl.gz'\n"
            "gzip.open(p, 'wt').write('{not json\\n')\n"
            "try:\n"
            "    corpus.load_cards(p)\n"
            "except corpus.CorpusLoadError:\n"
            "    print('raised')\n"
            "corpus.load_cards(pathlib.Path('/nope/x.gz')) if False else None\n"
            "try:\n"
            "    corpus.load_cards(pathlib.Path('/nope/x.gz'))\n"
            "except corpus.CorpusLoadError:\n"
            "    print('raised')\n")
        proc = subprocess.run([sys.executable, "-c", code], capture_output=True,
                              text=True, env={"PATH": "/usr/bin:/bin"})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.count("raised"), 2, proc.stdout)
        self.assertEqual(proc.stderr, "", "the library wrote to stderr")


class TestTheLegacyFacadeStillHaltsLoudly(unittest.TestCase):
    """Compatibility-equivalent at the legacy boundary, which is the whole point
    of catching CorpusLoadError in foundry_common rather than letting it fly."""

    def test_foundry_common_still_exits_with_the_STOP_line(self):
        code = (
            "import sys\n"
            f"sys.path.insert(0, {str(EXPERIMENTS)!r})\n"
            "import foundry_common as fc\n"
            "from pathlib import Path\n"
            "fc._PATHS = type(fc._PATHS).for_root('/definitely/not/a/repo')\n"
            "fc.load_corpus()\n")
        proc = subprocess.run([sys.executable, "-c", code], capture_output=True,
                              text=True, env={"PATH": "/usr/bin:/bin"})
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertTrue(proc.stderr.startswith("STOP — "), proc.stderr)
        self.assertIn("not found", proc.stderr)
        self.assertIn("run pipeline/fetch.py", proc.stderr)

    def test_the_legacy_halt_shape_is_unchanged(self):
        source = (EXPERIMENTS / "foundry_common.py").read_text(encoding="utf-8")
        self.assertIn('print(f"STOP — {message}", file=sys.stderr)', source)
        self.assertIn("sys.exit(1)", source)


# ---------------------------------------------------------------------------
# STRUCTURE
# ---------------------------------------------------------------------------

TIER_ENGINE_SHA = "54c3d189e015889ac28f304a58e3e06f5f9ceff9e0ac4586d4edf4dd77aab2e8"

FOUNDRY_COMMON = EXPERIMENTS / "foundry_common.py"
FOUNDRY_LOCALITY = EXPERIMENTS / "foundry_locality.py"
VISIBILITY_AUDIT = EXPERIMENTS / "foundry_visibility_audit.py"
CORPUS_MODULE = SRC / "mtj_foundry" / "corpus.py"


def legacy_aliases(source: str, module: str) -> set[str]:
    """Names bound to `module` by this file's own import statements."""
    import ast
    return {a.asname or a.name
            for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Import)
            for a in n.names if a.name == module}


class TestThePermanentModuleIsALibrary(unittest.TestCase):
    """The behavior is the oracle's. The BOUNDARY deliberately is not."""

    @classmethod
    def setUpClass(cls):
        import ast
        cls.source = CORPUS_MODULE.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_it_imports_only_the_standard_library(self):
        import ast, sys as _sys
        imported = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imported |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertTrue(imported <= set(_sys.stdlib_module_names) | {"__future__"},
                        sorted(imported))

    def test_it_imports_no_legacy_module(self):
        """Asserted on the IMPORT STATEMENTS, not on the text. The module's own
        docstring names `tier_engine` to explain what it deliberately is not,
        and a textual guard would forbid the explanation — the same shape as
        this repository's ratified 'a rejected term in backticks is ingested as
        vocabulary' trap."""
        import ast
        imported = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imported |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        for legacy in ("tier_engine", "foundry_common", "foundry_codebook",
                       "experiments"):
            with self.subTest(legacy=legacy):
                self.assertNotIn(legacy, imported)

    def test_it_never_exits_prints_or_mutates_the_path(self):
        """Structural: real calls and real attribute access, never the prose."""
        import ast
        calls = [ast.unparse(n.func) for n in ast.walk(self.tree)
                 if isinstance(n, ast.Call)]
        self.assertNotIn("print", calls)
        self.assertNotIn("sys.exit", calls)
        self.assertNotIn("exit", calls)
        touches_path = [ast.unparse(n) for n in ast.walk(self.tree)
                        if isinstance(n, ast.Attribute) and n.attr == "path"
                        and isinstance(n.value, ast.Name) and n.value.id == "sys"]
        self.assertEqual(touches_path, [])

    def test_it_writes_nothing(self):
        import ast
        writes = [ast.unparse(n) for n in ast.walk(self.tree)
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                  and n.func.attr in ("write_text", "write_bytes", "mkdir",
                                      "unlink", "rmdir", "touch")]
        self.assertEqual(writes, [])
        # the one `gzip.open` is read mode
        self.assertIn('gzip.open(path, "rt", encoding="utf-8")', self.source)

    def test_it_states_no_repository_relative_layout_fact(self):
        """THE defect this reimplementation exists to not inherit: the engine's
        `CARDS_PATH = Path("data/raw/oracle-cards.jsonl.gz")`, relative and
        therefore cwd-dependent. The path is a PARAMETER here.

        Asserted on STRING CONSTANTS in the code, not on the file text: the
        docstring quotes the legacy constant precisely in order to explain why
        it is not reproduced."""
        import ast
        literals = [n.value for n in ast.walk(self.tree)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        code_literals = [x for x in literals if len(x) < 200]
        for fragment in ("data/raw", "oracle-cards", "experiments"):
            with self.subTest(fragment=fragment):
                self.assertEqual(
                    [x for x in code_literals if fragment in x], [])
        module_constants = [t.id for n in self.tree.body if isinstance(n, ast.Assign)
                            for t in n.targets if isinstance(t, ast.Name)]
        self.assertEqual(module_constants, ["__all__"])

    def test_the_error_type_is_a_typed_exception_not_a_process_exit(self):
        self.assertTrue(issubclass(corpus.CorpusLoadError, Exception))
        self.assertFalse(issubclass(corpus.CorpusLoadError, SystemExit))


class TestTheOwnerNamesTheCorpusFile(unittest.TestCase):
    def test_it_resolves_exactly(self):
        self.assertEqual(ProjectPaths.for_root("/r").legacy_oracle_cards,
                         Path("/r/data/raw/oracle-cards.jsonl.gz"))

    def test_it_is_cwd_stable_and_touches_no_filesystem(self):
        import os
        paths = ProjectPaths.for_root("/definitely/not/real")
        before = paths.legacy_oracle_cards
        cwd = os.getcwd()
        try:
            os.chdir(tempfile.gettempdir())
            self.assertEqual(paths.legacy_oracle_cards, before)
        finally:
            os.chdir(cwd)
        self.assertFalse(before.exists())

    def test_the_static_and_live_resolutions_agree(self):
        from tests.refoundation import layout_census
        layout = layout_census.project_paths_layout(
            (SRC / "mtj_foundry" / "paths.py").read_text(encoding="utf-8"))
        self.assertEqual(layout["legacy_oracle_cards"],
                         ("data", "raw", "oracle-cards.jsonl.gz"))


class TestTheLegacyConsumersLeftTheEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.common = FOUNDRY_COMMON.read_text(encoding="utf-8")
        cls.locality = FOUNDRY_LOCALITY.read_text(encoding="utf-8")
        cls.visibility = VISIBILITY_AUDIT.read_text(encoding="utf-8")

    def test_foundry_common_has_no_tier_engine_import_or_reference(self):
        import ast
        self.assertEqual(legacy_aliases(self.common, "tier_engine"), set())
        live = [ast.unparse(n) for n in ast.walk(ast.parse(self.common))
                if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
                and n.value.id == "te"]
        self.assertEqual(live, [])

    def test_foundry_locality_has_no_tier_engine_import_or_reference(self):
        import ast
        self.assertEqual(legacy_aliases(self.locality, "tier_engine"), set())
        live = [ast.unparse(n) for n in ast.walk(ast.parse(self.locality))
                if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
                and n.value.id == "te"]
        self.assertEqual(live, [])

    def test_the_boundary_reaches_the_package_and_uses_it_for_the_corpus(self):
        self.assertIn("from mtj_foundry import corpus as _corpus", self.common)
        for call in ("_corpus.load_cards(_PATHS.legacy_oracle_cards)",
                     "_corpus.build_name_index(", "_corpus.normalize_name(",
                     "_corpus.card_faces("):
            with self.subTest(call=call):
                self.assertIn(call, self.common)

    def test_the_facade_DELEGATES_and_contains_no_copied_implementation(self):
        """Two face readers is the drift this capability exists to prevent, so
        the facade must be a single delegating return — asserted structurally,
        not by looking for suspicious words."""
        import ast
        fn = next(n for n in ast.walk(ast.parse(self.common))
                  if isinstance(n, ast.FunctionDef) and n.name == "raw_faces")
        body = [x for x in fn.body if not (isinstance(x, ast.Expr)
                                           and isinstance(x.value, ast.Constant))]
        self.assertEqual(len(body), 1, ast.unparse(fn))
        self.assertEqual(ast.unparse(body[0]), "return _corpus.card_faces(card)")

    def test_both_legacy_consumers_use_THE_SAME_facade(self):
        self.assertIn("fc.raw_faces(card)", self.locality)
        self.assertIn("fc.raw_faces(card)", self.visibility)

    def test_the_visibility_audit_added_no_bootstrap_of_its_own(self):
        """WHAT THIS GUARD IS ACTUALLY FOR, restated by C8.5J.

        The C8.5G form of this test asserted `"mtj_foundry" not in the source`.
        That was a proxy: at C8.5G the visibility audit had no business reaching
        the package directly, so "names the package at all" and "carries a
        bootstrap it must not have" were the same sentence. C8.5J separates them
        — the audit now takes the standing ratchet from `mtj_foundry.ratchet`,
        which is a required consumer route — so the proxy is replaced by the
        property it was standing in for.

        The invariant is UNCHANGED and is asserted more directly than before:
        this module may not establish its own path to the package. It must reach
        `mtj_foundry` only after `foundry_common` has run the C8.5A compatibility
        bootstrap, and its own `sys.path` call count must not move.
        """
        import ast
        tree = ast.parse(self.visibility)
        inserts = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                   and isinstance(n.func, ast.Attribute) and n.func.attr in ("insert", "append")
                   and isinstance(n.func.value, ast.Attribute) and n.func.value.attr == "path"]
        self.assertEqual(len(inserts), 1, "the visibility audit's bootstrap count moved")

        # The one insert it is allowed is the pre-existing legacy-sibling one,
        # and it points at `experiments`, never at `src`.
        self.assertNotIn("src", ast.unparse(inserts[0]))

        # ORDER IS THE WHOLE GUARD. `mtj_foundry` is importable from a loose
        # script only because `foundry_common` puts `src` on the path, so a
        # package import placed above it would fail — or, worse, would be
        # "fixed" by adding the second bootstrap this test forbids.
        imports = [(n.lineno, n.module) for n in ast.walk(tree)
                   if isinstance(n, ast.ImportFrom) and n.module]
        imports += [(n.lineno, a.name) for n in ast.walk(tree)
                    if isinstance(n, ast.Import) for a in n.names]
        common = [ln for ln, mod in imports if mod == "foundry_common"]
        package = [ln for ln, mod in imports if mod.split(".")[0] == "mtj_foundry"]
        self.assertEqual(len(common), 1)
        self.assertTrue(package, "the C8.5J ratchet route is missing")
        self.assertLess(common[0], min(package),
                        "foundry_common must establish the bootstrap first")

    def test_the_visibility_audit_reaches_only_the_authorized_package_modules(self):
        """A widened route would be a silent scope expansion. Exactly the two
        C8.5J names, and nothing else from the package."""
        import ast
        tree = ast.parse(self.visibility)
        reached = sorted({n.module for n in ast.walk(tree)
                          if isinstance(n, ast.ImportFrom) and n.module
                          and n.module.split(".")[0] == "mtj_foundry"})
        self.assertEqual(reached, ["mtj_foundry", "mtj_foundry.paths"])
        self.assertIn("from mtj_foundry import ratchet", self.visibility)
        self.assertIn("from mtj_foundry.paths import ProjectPaths", self.visibility)
        # The corpus capability is still reached through the FACADE, not around
        # it — the C8.5G invariant this file exists for.
        self.assertNotIn("mtj_foundry import corpus", self.visibility)

    def test_the_engine_oracle_is_byte_identical(self):
        import hashlib
        digest = hashlib.sha256(
            (EXPERIMENTS / "tier_engine.py").read_bytes()).hexdigest()
        self.assertEqual(digest, TIER_ENGINE_SHA)


class TestNoIndirectReExportConsumerRemains(unittest.TestCase):
    """R1's guard. The defect class that hid this slice's blocker.

    `foundry_visibility_audit` reached the engine as `fc.te.get_raw_faces` —
    through foundry_common's module namespace. No import graph can see that, so
    the topology prediction "modules importing tier_engine 12 -> 10" would have
    been satisfied exactly while a Gate 2 row broke.

    Detected from IMPORT ALIASES and attribute STRUCTURE, so an unrelated `.te`
    spelling anywhere in the tree is not banned."""

    def indirect_consumers(self):
        import ast
        from tests.refoundation import layout_census
        found = []
        for rel in layout_census.tracked_python(REPO_ROOT):
            source = (REPO_ROOT / rel).read_text(encoding="utf-8")
            aliases = legacy_aliases(source, "foundry_common")
            if not aliases:
                continue
            for node in ast.walk(ast.parse(source)):
                if (isinstance(node, ast.Attribute)
                        and isinstance(node.value, ast.Attribute)
                        and isinstance(node.value.value, ast.Name)
                        and node.value.value.id in aliases
                        and node.value.attr == "te"):
                    found.append(f"{rel.as_posix()}:{node.lineno} {ast.unparse(node)}")
        return found

    def test_nothing_reaches_the_engine_through_the_boundary(self):
        self.assertEqual(self.indirect_consumers(), [])

    def test_the_boundary_binds_no_legacy_module_name_at_all(self):
        """The general form: foundry_common must re-export no legacy module, so
        a NEW indirect consumer of some other module cannot appear either."""
        import ast
        source = FOUNDRY_COMMON.read_text(encoding="utf-8")
        bound = {a.asname or a.name
                 for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Import)
                 for a in n.names}
        self.assertEqual(bound & {"tier_engine", "te"}, set())

    def test_NEGATIVE_CONTROL_a_restored_indirect_access_is_detected(self):
        """The guard scans tracked files, so rigging it in memory would not
        exercise it. This proves the DETECTOR fires on the exact shape."""
        import ast
        source = ('import foundry_common as fc\n'
                  'faces = fc.te.get_raw_faces(card)\n')
        aliases = legacy_aliases(source, "foundry_common")
        hits = [ast.unparse(n) for n in ast.walk(ast.parse(source))
                if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Attribute)
                and isinstance(n.value.value, ast.Name)
                and n.value.value.id in aliases and n.value.attr == "te"]
        self.assertEqual(hits, ["fc.te.get_raw_faces"])

    def test_an_unrelated_dot_te_spelling_is_NOT_banned(self):
        """False positives would make the guard unusable — `.te` appears in
        ordinary attribute chains that have nothing to do with the boundary."""
        import ast
        source = ('import foundry_common as fc\n'
                  'x = something.te.value\n'
                  'y = fc.FOUNDRY_OUT_DIR\n')
        aliases = legacy_aliases(source, "foundry_common")
        hits = [n for n in ast.walk(ast.parse(source))
                if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Attribute)
                and isinstance(n.value.value, ast.Name)
                and n.value.value.id in aliases and n.value.attr == "te"]
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
