"""The package must be importable, minimal, and free of repository assumptions."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT, SRC


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


# ===========================================================================
# C8.5E — THE EXECUTION CONTEXTS DECLARED BY THE PACKAGE EXECUTION CONTRACT
# ===========================================================================
#
# `refoundation/PACKAGE-EXECUTION-CONTRACT.yaml` names three contexts. These
# tests prove the two that are SUPPORTED, and prove that the third is not
# silently standing in for either.
#
# WHY THE INSTALLED CONTEXT IS BUILT WITHOUT pip. A modern editable install makes
# a package importable by writing a path configuration file into the target
# environment's site-packages; that is the whole of the import mechanism. This
# builds exactly that condition in a throwaway environment, so the proof needs no
# network, no build backend and no repository bytes. MEASURED 2026-08-30: it
# needs to -- this machine has no `setuptools` in the system interpreter and
# Python 3.14's `venv` does not seed one, so `pip install -e .` cannot run
# offline here at all. The contract says so in as many words; a test that shelled
# out to pip would be a test that fails for an environment reason and tells you
# nothing about the contract.

CONTRACT = REPO_ROOT / "refoundation" / "PACKAGE-EXECUTION-CONTRACT.yaml"
CLEAN_ENV = {"PATH": "/usr/bin:/bin"}   # deliberately no PYTHONPATH


class TestTheInstalledPackageContext(unittest.TestCase):
    """Context INSTALLED_PACKAGE — the permanent, supported one."""

    def _installed_env(self, tmp: Path) -> Path:
        """A throwaway environment with the package made importable, no network."""
        env_dir = tmp / "env"
        subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(env_dir)],
                       check=True, capture_output=True)
        sites = list(env_dir.glob("lib/*/site-packages"))
        self.assertEqual(len(sites), 1, sites)
        (sites[0] / "mtj_foundry_editable.pth").write_text(f"{SRC}\n", encoding="utf-8")
        return env_dir / "bin" / "python"

    def test_import_succeeds_from_an_unrelated_cwd_with_no_PYTHONPATH(self):
        code = ("import os, sys, mtj_foundry\n"
                "from mtj_foundry.paths import ProjectPaths\n"
                "assert 'PYTHONPATH' not in os.environ\n"
                "assert ProjectPaths.for_root('/r').baselines.as_posix() == "
                "'/r/config/baselines'\n"
                "print('ok', mtj_foundry.__file__)\n")
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            python = self._installed_env(tmp)
            outside = tmp / "unrelated"
            outside.mkdir()
            self.assertFalse((outside / ".git").exists())
            proc = subprocess.run([str(python), "-c", code], cwd=outside,
                                  capture_output=True, text=True, env=CLEAN_ENV)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("ok", proc.stdout)

    def test_NEGATIVE_CONTROL_without_the_package_the_same_context_fails(self):
        """Same environment, same command, package NOT made importable. If this
        passed, the test above would be proving something about the machine
        rather than about the contract."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            env_dir = tmp / "env"
            subprocess.run([sys.executable, "-m", "venv", "--without-pip",
                            str(env_dir)], check=True, capture_output=True)
            outside = tmp / "unrelated"
            outside.mkdir()
            proc = subprocess.run([str(env_dir / "bin" / "python"), "-c",
                                   "import mtj_foundry"], cwd=outside,
                                  capture_output=True, text=True, env=CLEAN_ENV)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("No module named 'mtj_foundry'", proc.stderr)

    def test_NEGATIVE_CONTROL_a_broken_source_root_fails_loudly(self):
        """If the path configuration points somewhere the package is not, the
        import must fail rather than silently resolve something else."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            env_dir = tmp / "env"
            subprocess.run([sys.executable, "-m", "venv", "--without-pip",
                            str(env_dir)], check=True, capture_output=True)
            sites = list(env_dir.glob("lib/*/site-packages"))[0]
            (sites / "mtj_foundry_editable.pth").write_text(
                f"{REPO_ROOT / 'experiments'}\n", encoding="utf-8")
            outside = tmp / "unrelated"
            outside.mkdir()
            proc = subprocess.run([str(env_dir / "bin" / "python"), "-c",
                                   "import mtj_foundry"], cwd=outside,
                                  capture_output=True, text=True, env=CLEAN_ENV)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("No module named 'mtj_foundry'", proc.stderr)


class TestThePackagingMetadataTheContractDependsOn(unittest.TestCase):
    """The install contract is only as good as the discovery configuration that
    would produce it. C8.5E changes NOTHING here -- C8.5D measured that the
    skeleton already installs -- so these guards exist to make a later silent
    edit visible, not to record a change."""

    @classmethod
    def setUpClass(cls):
        cls.text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")

    def test_the_src_layout_discovery_is_declared(self):
        self.assertIn('package-dir = {"" = "src"}', self.text)
        self.assertIn('where = ["src"]', self.text)
        self.assertIn('include = ["mtj_foundry*"]', self.text)

    def test_only_the_permanent_namespace_is_discoverable(self):
        """Legacy top-level directories are not packages and must not be swept
        in by discovery -- that would package `experiments/` by accident, which
        is exactly the one-for-one copy the Captain's direction rules out."""
        self.assertNotIn('include = ["*"]', self.text)
        for legacy in ("experiments", "pipeline", "docs"):
            self.assertNotIn(f'"{legacy}*"', self.text)

    def test_the_build_backend_and_its_requirement_are_declared(self):
        """The contract names setuptools>=68 as the provisioning prerequisite;
        that claim has to match the file it is about."""
        self.assertIn('requires = ["setuptools>=68"]', self.text)
        self.assertIn('build-backend = "setuptools.build_meta"', self.text)

    def test_runtime_dependencies_remain_deliberately_empty(self):
        """C8.5E may not migrate or pin a legacy runtime dependency."""
        self.assertIn("dependencies = []", self.text)

    def test_the_contract_and_pyproject_agree_about_the_build_requirement(self):
        contract = CONTRACT.read_text(encoding="utf-8")
        self.assertIn("setuptools>=68", contract)
        self.assertIn("[build-system] requires", contract)


class TestTheTransitionalLegacyBootstrapContext(unittest.TestCase):
    """Context LEGACY_LOOSE_SCRIPT_BOOTSTRAP — still load-bearing, not deleted."""

    def _loose_script(self, code: str) -> subprocess.CompletedProcess:
        """No PYTHONPATH and no installed package: the only route to the owner is
        the compatibility bootstrap itself."""
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / "unrelated"
            outside.mkdir()
            return subprocess.run([sys.executable, "-c", code], cwd=outside,
                                  capture_output=True, text=True, env=CLEAN_ENV)

    def test_the_package_is_genuinely_NOT_installed_in_this_interpreter(self):
        """The premise of every claim below. If the package happened to be
        installed, the bootstrap tests would pass for the wrong reason."""
        proc = self._loose_script("import mtj_foundry")
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("No module named 'mtj_foundry'", proc.stderr)

    def test_the_boundary_reaches_the_owner_through_its_bootstrap(self):
        proc = self._loose_script(
            f"import sys; sys.path.insert(0, {str(REPO_ROOT / 'experiments')!r})\n"
            "import foundry_common as fc\n"
            "assert 'mtj_foundry.paths' in sys.modules, 'the owner was not reached'\n"
            f"assert str(fc.REPO_ROOT) == {str(REPO_ROOT)!r}, fc.REPO_ROOT\n"
            "print('ok')\n")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("ok", proc.stdout)

    def test_a_downstream_legacy_module_resolves_the_same_way(self):
        proc = self._loose_script(
            f"import sys; sys.path.insert(0, {str(REPO_ROOT / 'experiments')!r})\n"
            "import foundry_codebook as fcb\n"
            f"assert str(fcb.CODEBOOK_PATH) == "
            f"{str(REPO_ROOT / 'experiments' / 'out' / 'foundry' / 'codebook.json')!r}\n"
            f"assert str(fcb.LATEST_ARTIFACT_PATH) == "
            f"{str(REPO_ROOT / 'data' / 'artifacts' / 'latest.json')!r}\n"
            "print('ok')\n")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("ok", proc.stdout)

    def test_no_bootstrap_was_deleted_by_this_slice(self):
        """C8.5E deletes nothing. The two named bootstrap statements must both
        still be present, verbatim."""
        common = (REPO_ROOT / "experiments" / "foundry_common.py").read_text(
            encoding="utf-8")
        codebook = (REPO_ROOT / "experiments" / "foundry_codebook.py").read_text(
            encoding="utf-8")
        self.assertIn("sys.path.insert(0, str(_BOOTSTRAP_SRC))", common)
        self.assertIn("from mtj_foundry.paths import ProjectPaths", common)
        self.assertIn('sys.path.insert(0, str(_BOOTSTRAP_ROOT / "experiments"))',
                      codebook)


class TestTheExplicitSourceLayoutContextIsNotTheContract(unittest.TestCase):
    """Context EXPLICIT_SOURCE_LAYOUT — development/diagnostic only.

    This is the one that could quietly masquerade as the install contract,
    because it is how the refoundation suite itself reaches the package."""

    def test_the_suite_reaches_the_package_this_way_and_says_so(self):
        helpers = (REPO_ROOT / "tests" / "refoundation" / "helpers.py").read_text(
            encoding="utf-8")
        self.assertIn("sys.path.insert(0, str(SRC))", helpers)
        text = CONTRACT.read_text(encoding="utf-8")
        self.assertIn("EXPLICIT_SOURCE_LAYOUT", text)
        self.assertIn("DEVELOPMENT_DIAGNOSTIC_ONLY", text)
        self.assertIn("tests/refoundation/helpers.py", text)

    def test_the_contract_forbids_substituting_it_for_the_install_contract(self):
        text = CONTRACT.read_text(encoding="utf-8")
        self.assertIn("MUST NOT be confused with", text)
        self.assertIn("does NOT demonstrate the install contract", text)


if __name__ == "__main__":
    unittest.main()
