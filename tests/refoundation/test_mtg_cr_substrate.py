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
        from mtj_foundry.mtg.cr import keywords
        self.assertEqual(len(keywords.keyword_rows()), 194)

    def test_the_cr_edition_resolves_through_the_layout_owner(self):
        from mtj_foundry.mtg.cr import edition
        from mtj_foundry.paths import ProjectPaths
        paths = ProjectPaths.for_root(REPO_ROOT)
        self.assertEqual(edition.CR_PATH, paths.config_cr / edition.CR_EDITION_FILENAME)
        self.assertNotIn("docs", edition.CR_PATH.parts[-3:-1])

    def test_generated_provenance_is_repository_relative(self):
        """A tracked artifact may not record a developer-specific absolute path."""
        from mtj_foundry.mtg.cr import edition
        source = edition.repo_relative_source()
        self.assertFalse(source.startswith("/"))
        self.assertEqual(source, "config/cr/" + edition.CR_EDITION_FILENAME)


if __name__ == "__main__":
    unittest.main()
