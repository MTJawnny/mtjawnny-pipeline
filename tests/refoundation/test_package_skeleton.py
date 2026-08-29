"""The package must be importable, minimal, and free of repository assumptions."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.refoundation.helpers import SRC


class TestPackageImportsWithoutARepository(unittest.TestCase):
    """Acceptance criterion: "package imports with no repository present"."""

    def _run_in_isolation(self, code: str) -> subprocess.CompletedProcess:
        """Run `code` from a scratch cwd that is NOT inside any git repository.

        Importing from inside the repo would prove nothing: an import-time root
        search would succeed and the test would pass for the wrong reason.
        """
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / "no-repo-here"
            outside.mkdir()
            self.assertFalse((outside / ".git").exists())
            return subprocess.run([sys.executable, "-c", code], cwd=outside,
                                  capture_output=True, text=True,
                                  env={"PATH": "/usr/bin:/bin",
                                       "PYTHONPATH": str(SRC)})

    def test_the_package_imports_outside_any_repository(self):
        proc = self._run_in_isolation(
            "import mtj_foundry, mtj_foundry.paths, mtj_foundry.conservation; print('ok')")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("ok", proc.stdout)

    def test_importing_paths_performs_no_git_search_and_raises_nothing(self):
        """Constraint: import_time_git_search is forbidden.

        Proven by importing with `Path.exists` poisoned: any import-time marker
        probe would trip it. The negative control at the end confirms the trap is
        live, so a green result cannot mean the trap simply never fired.
        """
        code = (
            "from pathlib import Path\n"
            "Path.exists = lambda self: (_ for _ in ()).throw("
            "AssertionError('filesystem probed at import time'))\n"
            "import mtj_foundry.paths as p\n"
            "assert not hasattr(p, 'ROOT'), 'a global ROOT exists'\n"
            "try:\n"
            "    Path('/x').exists()\n"
            "except AssertionError:\n"
            "    print('ok')\n"
        )
        proc = self._run_in_isolation(code)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("ok", proc.stdout)


class TestMinimalSurface(unittest.TestCase):
    def test_the_top_level_export_surface_stays_minimal(self):
        """C2: the package init is not the API mechanism, so it stays tiny.

        Asserted against what `__init__.py` DEFINES, not against runtime attributes:
        importing `mtj_foundry.paths` always binds `paths` on the parent package, so
        a runtime check would be measuring Python's import machinery rather than the
        module's declared surface.
        """
        import ast

        import mtj_foundry

        self.assertEqual(mtj_foundry.__all__, ["__version__"])
        tree = ast.parse((SRC / "mtj_foundry" / "__init__.py").read_text())
        assigned = [t.id for node in tree.body if isinstance(node, ast.Assign)
                    for t in node.targets if isinstance(t, ast.Name)]
        self.assertEqual(sorted(assigned), ["__all__", "__version__"])

    def test_the_package_init_re_exports_nothing(self):
        """C2: mandatory re-export through __init__ is what recreates import cycles."""
        import ast

        tree = ast.parse((SRC / "mtj_foundry" / "__init__.py").read_text())
        imported = [node for node in tree.body
                    if isinstance(node, (ast.Import, ast.ImportFrom))
                    and not (isinstance(node, ast.ImportFrom)
                             and node.module == "__future__")]
        self.assertEqual(imported, [], "the package init imports a submodule")

    def test_no_module_defines_a_global_root(self):
        """Constraint: global_ROOT is forbidden."""
        from mtj_foundry import conservation, paths

        for module in (paths, conservation):
            with self.subTest(module=module.__name__):
                for name in ("ROOT", "REPO_ROOT", "PROJECT_ROOT", "BASE_DIR"):
                    self.assertFalse(hasattr(module, name),
                                     f"{module.__name__} exposes a global {name}")

    def test_the_package_imports_nothing_from_the_legacy_tree(self):
        """Zero-behavior: the skeleton must not reach into experiments/ or pipeline/."""
        for path in sorted((SRC / "mtj_foundry").rglob("*.py")):
            text = path.read_text()
            with self.subTest(module=path.name):
                for legacy in ("import tier_engine", "import foundry_", "from foundry_",
                               "from tier_engine", "experiments.", "pipeline."):
                    self.assertNotIn(legacy, text,
                                     f"{path.name} references legacy module {legacy!r}")


if __name__ == "__main__":
    unittest.main()
