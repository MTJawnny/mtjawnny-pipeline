"""The permanent CR substrate: what it owns, and the edge it may never have.

S6 created `mtj_foundry.mtg.cr` and moved the reusable CR semantics into it.
Two properties matter more than the move itself.

**B10 — the CR half may never reach the shapes half.** The accepted permanent
direction is `shapes -> cr -> edition -> infra`. The cycle R6 removed was carried
by exactly ONE reusable function, and every edge in that seam was a
FUNCTION-LOCAL import -- a scan that only reads module headers would have seen
none of them. So the check below walks the whole AST, not the import block.

**L2 stays domain-free.** No codebook, axis, membership, authority or operator
residue may live under `mtg/`, and `checks.py` in particular must not acquire
`coverage()` or a codebook import: a generator in the MTG substrate that read the
live codebook would put a codebook dependency underneath L2.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT  # noqa: F401  (sets sys.path)

CR_PKG = REPO_ROOT / "src" / "mtj_foundry" / "mtg" / "cr"
MTG_PKG = REPO_ROOT / "src" / "mtj_foundry" / "mtg"


def modules(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.py"))


def referenced_modules(source: str) -> set[str]:
    """Every module named by an import ANYWHERE in the file, including inside a
    function body. The seam's real edges were all deferred imports."""
    out = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            out |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom) and not node.level:
            out.add(node.module or "")
            out |= {f"{node.module}.{a.name}" for a in node.names}
    return out


class TestB10CrNeverReachesShapes(unittest.TestCase):

    def test_no_cr_module_imports_shapes_anywhere_including_function_bodies(self):
        offenders = []
        for path in modules(CR_PKG):
            for mod in referenced_modules(path.read_text(encoding="utf-8")):
                if "mtg.shapes" in mod or mod.endswith(".shapes"):
                    offenders.append(f"{path.name}: {mod}")
        self.assertEqual(offenders, [], f"B10 violated: {offenders}")

    def test_no_cr_module_names_a_shapes_symbol_in_code(self):
        """Names, not just imports -- a deferred import binds a NAME, and the
        call site is what makes the edge real."""
        forbidden = {"parse_delivery", "ratified_delivery_tokens",
                     "build_self_noun_rx", "build_keyword_homes",
                     "keyword_homes", "find_home"}
        offenders = []
        for path in modules(CR_PKG):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id in forbidden:
                    offenders.append(f"{path.name}:{node.lineno} {node.id}")
                if isinstance(node, ast.Attribute) and node.attr in forbidden:
                    offenders.append(f"{path.name}:{node.lineno} .{node.attr}")
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                        and node.name in forbidden:
                    offenders.append(f"{path.name}:{node.lineno} def {node.name}")
        self.assertEqual(offenders, [], f"shapes symbol in CR half: {offenders}")

    def test_find_home_and_keyword_homes_are_absent_from_permanent_cr(self):
        """R6's override, asserted as an absence. They arrive with S7's
        `mtg/shapes/delivery.py`, because they consume delivery parsing."""
        from mtj_foundry.mtg.cr import keywords, edition, checks, keyword_buckets
        for module in (keywords, edition, checks, keyword_buckets):
            for name in ("find_home", "keyword_homes"):
                with self.subTest(module=module.__name__, symbol=name):
                    self.assertFalse(hasattr(module, name))


class TestL2Purity(unittest.TestCase):

    def test_no_permanent_mtg_module_imports_legacy_or_operator_code(self):
        offenders = []
        for path in modules(MTG_PKG):
            for mod in referenced_modules(path.read_text(encoding="utf-8")):
                top = mod.split(".")[0]
                if top in {"experiments", "tier_engine", "pipeline"} \
                        or top.startswith("foundry_"):
                    offenders.append(f"{path.name}: {mod}")
        self.assertEqual(offenders, [], f"upward import from L2: {offenders}")

    def test_the_cr_substrate_imports_only_stdlib_paths_and_itself(self):
        import sys
        allowed_prefix = ("mtj_foundry.mtg.cr", "mtj_foundry.paths")
        for path in modules(CR_PKG):
            for mod in referenced_modules(path.read_text(encoding="utf-8")):
                if not mod:
                    continue
                with self.subTest(module=path.name, imports=mod):
                    self.assertTrue(
                        mod.split(".")[0] in sys.stdlib_module_names
                        or mod.startswith(allowed_prefix), mod)

    def test_checks_has_no_coverage_and_no_codebook_dependency(self):
        """R4 assigns active-axis coverage to a later `codebook/coverage.py`."""
        from mtj_foundry.mtg.cr import checks
        self.assertFalse(hasattr(checks, "coverage"))
        source = (CR_PKG / "checks.py").read_text(encoding="utf-8")
        for mod in referenced_modules(source):
            self.assertNotIn("codebook", mod)

    def test_no_cr_module_carries_a_process_entrypoint(self):
        """`sys.exit`, `argparse` and `__main__` are operator concerns. A library
        may not exit a process it does not own -- the halt boundary is
        re-established by the legacy shell instead."""
        for path in modules(CR_PKG):
            source = path.read_text(encoding="utf-8")
            with self.subTest(module=path.name):
                self.assertNotIn("argparse", referenced_modules(source))
                self.assertNotIn('if __name__ ==', source)
                tree = ast.parse(source)
                exits = [n.lineno for n in ast.walk(tree)
                         if isinstance(n, ast.Attribute) and n.attr == "exit"]
                self.assertEqual(exits, [])

    def test_edition_diff_was_not_migrated_as_substrate(self):
        """R4 rebucketed the whole file to later operator diagnostics."""
        self.assertEqual(
            [p.name for p in modules(CR_PKG)],
            ["__init__.py", "checks.py", "edition.py", "keyword_buckets.py",
             "keywords.py"])
        self.assertTrue(
            (REPO_ROOT / "experiments" / "foundry_cr_edition_diff.py").is_file())


class TestTheTwoKeywordFactsStayDistinct(unittest.TestCase):
    """A derived map is not the list it was derived from. Asking a home map
    "is this a keyword?" answered no for `awaken`, and `Awaken 4—{4}{W}` was
    read as a flavor word."""

    def test_keyword_membership_is_194(self):
        from mtj_foundry.mtg.cr import keywords, edition
        from mtj_foundry.paths import ProjectPaths
        cr = ProjectPaths.for_root(REPO_ROOT).config_cr / edition.CR_EDITION_FILENAME
        self.assertEqual(len(keywords.keyword_rows(cr)), 194)

    def test_the_keyword_derivation_takes_an_explicit_edition(self):
        """S6.R1: no permanent CR entry point may fall back to a default path,
        because a default path means a manufactured root."""
        import inspect
        from mtj_foundry.mtg.cr import keywords, keyword_buckets, checks, edition
        for fn in (keywords.load_702, keywords.type_vocabulary,
                   keywords.keyword_rows, keyword_buckets.cr_text,
                   checks.load_cr, edition.text, edition.lines):
            with self.subTest(fn=f"{fn.__module__}.{fn.__name__}"):
                first = list(inspect.signature(fn).parameters.values())[0]
                self.assertIs(first.default, inspect.Parameter.empty)


class TestTheCrSubstrateDerivesNoRepositoryRoot(unittest.TestCase):
    """S6.R1 — the defect the first S6 candidate shipped, and its guard.

    That candidate wrote

        _ROOT = Path(__file__).resolve().parents[4]
        _PATHS = ProjectPaths.for_root(_ROOT)

    in `mtg/cr/edition.py`. It passed every source-tree test because
    `<repo>/src/mtj_foundry/mtg/cr/edition.py` really is four parents below the
    repository -- and from a real site-packages install the SAME ancestry lands
    in the Python environment, so the module would compose `config/cr/...` under
    the wrong root. Measured: `.../venv/lib/python3.14`.

    THE OLD GUARD COULD NOT SEE IT. It asserted that `edition.CR_PATH` equalled
    a `ProjectPaths(REPO_ROOT)` result -- true whichever way the root was
    obtained, because both sides sat in the same checkout. So the check below
    distinguishes USING `ProjectPaths` from MANUFACTURING the root fed into it.
    """

    ROOT_NAMES = {"ROOT", "_ROOT", "REPO_ROOT", "PROJECT_ROOT", "BASE_DIR"}

    def test_no_module_walks_file_ancestry_for_a_root(self):
        """`__file__` may not reach `.parent`/`.parents`/`.resolve()` anywhere in
        permanent CR. Read from the AST, so the module's own prose describing the
        rejected shape cannot satisfy or trip it."""
        offenders = []
        for path in modules(CR_PKG):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Attribute):
                    continue
                if node.attr not in {"parent", "parents", "resolve"}:
                    continue
                if "__file__" in ast.unparse(node):
                    offenders.append(f"{path.name}:{node.lineno} {ast.unparse(node)}")
        self.assertEqual(offenders, [], f"__file__-ancestry root derivation: {offenders}")

    def test_no_module_defines_a_repository_root_name(self):
        offenders = []
        for path in modules(CR_PKG):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                targets = (node.targets if isinstance(node, ast.Assign)
                           else [node.target] if isinstance(node, ast.AnnAssign) else [])
                for t in targets:
                    if isinstance(t, ast.Name) and t.id in self.ROOT_NAMES:
                        offenders.append(f"{path.name}:{node.lineno} {t.id}")
        self.assertEqual(offenders, [], f"permanent CR defines a root: {offenders}")

    def test_no_module_searches_the_filesystem_or_cwd_for_a_root(self):
        forbidden = {"getcwd", "cwd", "discover_root", "rglob", "glob"}
        offenders = []
        for path in modules(CR_PKG):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and node.attr in forbidden:
                    offenders.append(f"{path.name}:{node.lineno} .{node.attr}")
                if isinstance(node, ast.Constant) and node.value == ".git":
                    offenders.append(f"{path.name}:{node.lineno} '.git'")
        self.assertEqual(offenders, [], f"root search in permanent CR: {offenders}")

    def test_the_cr_substrate_does_not_import_the_layout_owner_at_all(self):
        """Using `ProjectPaths` is fine ONE LAYER UP. Down here it is how a
        second layout owner sneaks in: the library would still have to invent the
        root it passes."""
        for path in modules(CR_PKG):
            with self.subTest(module=path.name):
                self.assertNotIn("mtj_foundry.paths",
                                 referenced_modules(path.read_text(encoding="utf-8")))

    def test_an_ARBITRARY_root_selects_and_reads_its_own_edition(self):
        """The positive half, and it is deliberately NOT "equals
        ProjectPaths(REPO_ROOT)" -- that passes no matter where the root came
        from. This roots the CR somewhere the repository is not."""
        import tempfile
        from mtj_foundry.mtg.cr import edition
        from mtj_foundry.paths import ProjectPaths

        real = ProjectPaths.for_root(REPO_ROOT).config_cr / edition.CR_EDITION_FILENAME
        with tempfile.TemporaryDirectory() as tmp:
            alt = ProjectPaths.for_root(Path(tmp) / "elsewhere")
            target = alt.config_cr / edition.CR_EDITION_FILENAME
            target.parent.mkdir(parents=True)
            target.write_bytes(real.read_bytes())

            selected = edition.select_cr_path(alt.config_cr)
            self.assertEqual(selected, target)
            self.assertNotIn(str(REPO_ROOT), str(selected))
            self.assertEqual(edition.text(selected), edition.text(real))

    def test_selection_touches_no_filesystem_and_needs_no_existing_root(self):
        """A root that cannot exist still composes: the join is lexical."""
        from mtj_foundry.mtg.cr import edition
        from mtj_foundry.paths import ProjectPaths
        nowhere = ProjectPaths.for_root("/definitely/not/here")
        self.assertEqual(
            edition.select_cr_path(nowhere.config_cr),
            Path("/definitely/not/here/config/cr") / edition.CR_EDITION_FILENAME)

    def test_provenance_takes_an_EXPLICIT_root_from_the_caller(self):
        """`repo_relative_source` must not know where the repository is."""
        import inspect
        from mtj_foundry.mtg.cr import edition
        params = list(inspect.signature(edition.repo_relative_source).parameters)
        self.assertEqual(params, ["path", "root"])
        self.assertEqual(
            edition.repo_relative_source(Path("/r/config/cr/x.md"), Path("/r")),
            "config/cr/x.md")
        # outside the supplied root it degrades to the filename, deterministically
        self.assertEqual(
            edition.repo_relative_source(Path("/elsewhere/x.md"), Path("/r")), "x.md")


class TestTheCompositionBoundarySuppliesTheRoot(unittest.TestCase):
    """The other half: the root must come from a boundary that already owns it."""

    def test_the_legacy_cr_shell_supplies_config_cr_from_the_owner(self):
        source = (REPO_ROOT / "experiments" / "foundry_cr.py").read_text(encoding="utf-8")
        self.assertIn("CR_PATH = _edition.select_cr_path(fc.CONFIG_CR)", source)

    def test_the_default_still_resolves_to_the_S1_S3_owner(self):
        import importlib.util, sys
        experiments = REPO_ROOT / "experiments"
        if str(experiments) not in sys.path:
            sys.path.insert(0, str(experiments))
        spec = importlib.util.spec_from_file_location(
            "legacy_cr_boundary", experiments / "foundry_cr.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        from mtj_foundry.mtg.cr import edition
        from mtj_foundry.paths import ProjectPaths
        paths = ProjectPaths.for_root(REPO_ROOT)
        self.assertEqual(mod.CR_PATH, paths.config_cr / edition.CR_EDITION_FILENAME)
        self.assertNotIn("docs", mod.CR_PATH.parts[-3:-1])


if __name__ == "__main__":
    unittest.main()
