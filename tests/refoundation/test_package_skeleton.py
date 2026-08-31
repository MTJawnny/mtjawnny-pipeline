"""The package must be importable, minimal, and free of repository assumptions."""

from __future__ import annotations

import fnmatch
import shutil
import subprocess
import sys
import tempfile
import tomllib
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


def derive_editable_source(project_root: Path) -> Path | None:
    """Where an editable install of THIS pyproject would map `mtj_foundry` from.

    Returns the directory that must reach the interpreter's path, or None when
    the metadata does not make `mtj_foundry` discoverable at all.

    THE WHOLE POINT IS THE COUPLING. C8.5E's first attempt wrote a path
    configuration file naming the repository's `SRC` constant. That proved only
    that putting `src` on the path makes the package importable — which is
    EXPLICIT_SOURCE_LAYOUT, the context the contract says may never stand in for
    INSTALLED_PACKAGE. Corrupting `package-dir` or `packages.find` left it green.
    Here every value comes from the parsed metadata, so breaking discovery breaks
    the SAME witness (Manager review issue:1#issuecomment-5472076171).

    This is the setuptools src-layout contract, not a general build: the root
    package namespace maps through `package-dir[""]`, and discovery searches
    `packages.find.where` filtered by `include`/`exclude`.
    """
    data = tomllib.loads((project_root / "pyproject.toml").read_text(encoding="utf-8"))
    setuptools_cfg = data.get("tool", {}).get("setuptools", {})
    package_dir = setuptools_cfg.get("package-dir", {})
    find = setuptools_cfg.get("packages", {}).get("find", {})
    where = find.get("where", ["."])
    include = find.get("include", ["*"])
    exclude = find.get("exclude", [])

    discovered = set()
    for location in where:
        search = project_root / location
        if not search.is_dir():
            continue
        for candidate in search.iterdir():
            if not (candidate / "__init__.py").is_file():
                continue
            name = candidate.name
            if not any(fnmatch.fnmatch(name, pattern) for pattern in include):
                continue
            if any(fnmatch.fnmatch(name, pattern) for pattern in exclude):
                continue
            discovered.add(name)
    if "mtj_foundry" not in discovered:
        return None

    mapped = project_root / package_dir.get("", ".")
    if not (mapped / "mtj_foundry" / "__init__.py").is_file():
        # The metadata maps the root namespace somewhere the package is not.
        return None
    return mapped


class TestTheInstalledPackageContext(unittest.TestCase):
    """Context INSTALLED_PACKAGE — the permanent, supported one.

    EVIDENCE BOUNDARY, stated because the distinction is the whole repair:

    * REAL_INSTALL_PROVISIONING — an actual `pip install -e .` running the build
      backend. Observed under C8.5D on a scratch copy when setuptools was
      obtainable. It is Worker-local evidence and is NOT what runs here.
    * METADATA_DRIVEN_EDITABLE_IMPORT_PROOF — what these tests are. They build,
      offline, the import condition an editable install produces, deriving it
      from a scratch copy of the real pyproject.toml + src tree. No pip runs, no
      build backend executes, and nothing here claims otherwise.

    MEASURED 2026-08-30: pip cannot run offline in this environment at all —
    `[build-system] requires` names setuptools>=68, the system interpreter has
    none, and Python 3.14's venv seeds none. A committed test that shelled out to
    pip would fail for an environment reason and say nothing about the contract.
    """

    def _scratch_project(self, tmp: Path) -> Path:
        """A copy of the distribution's metadata and sources, outside the repo."""
        project = tmp / "project"
        project.mkdir()
        shutil.copy2(REPO_ROOT / "pyproject.toml", project / "pyproject.toml")
        shutil.copytree(SRC, project / "src",
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        return project

    def _witness(self, project: Path, tmp: Path, *, provision: bool = True):
        """Run the installed-context import against a scratch project.

        The editable mapping is DERIVED from the scratch metadata. If the
        metadata does not make `mtj_foundry` discoverable, there is nothing to
        provision and the witness runs without it — which is exactly how a
        broken package configuration presents.
        """
        env_dir = tmp / f"env{len(list(tmp.iterdir()))}"
        subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(env_dir)],
                       check=True, capture_output=True)
        sites = list(env_dir.glob("lib/*/site-packages"))
        self.assertEqual(len(sites), 1, sites)
        derived = derive_editable_source(project) if provision else None
        if derived is not None:
            self.assertNotEqual(derived.resolve(), SRC.resolve(),
                                "the mapping must come from the SCRATCH copy, "
                                "never from the repository source tree")
            (sites[0] / "mtj_foundry_editable.pth").write_text(
                f"{derived}\n", encoding="utf-8")
        outside = tmp / f"cwd{len(list(tmp.iterdir()))}"
        outside.mkdir()
        self.assertFalse((outside / ".git").exists())
        proc = subprocess.run(
            [str(env_dir / "bin" / "python"), "-c",
             "import os, mtj_foundry\n"
             "from mtj_foundry.paths import ProjectPaths\n"
             "assert 'PYTHONPATH' not in os.environ\n"
             "assert ProjectPaths.for_root('/r').baselines.as_posix() == "
             "'/r/config/baselines'\n"
             "print('ok', mtj_foundry.__file__)\n"],
            cwd=outside, capture_output=True, text=True, env=CLEAN_ENV)
        return derived, proc

    def test_the_derivation_reads_the_real_metadata(self):
        derived = derive_editable_source(REPO_ROOT)
        self.assertIsNotNone(derived, "mtj_foundry is not discoverable")
        self.assertEqual(derived.resolve(), SRC.resolve())

    def test_import_succeeds_from_an_unrelated_cwd_with_no_PYTHONPATH(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            project = self._scratch_project(tmp)
            derived, proc = self._witness(project, tmp)
        self.assertEqual(derived, project / "src")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("ok", proc.stdout)
        self.assertIn(str(project), proc.stdout,
                      "the package must have been imported from the SCRATCH copy")

    def test_NEGATIVE_CONTROL_corrupting_package_dir_reddens_the_SAME_witness(self):
        """The control the Manager found missing. `package-dir` is repointed in
        the scratch metadata; the identical import witness must fail."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            project = self._scratch_project(tmp)
            text = (project / "pyproject.toml").read_text(encoding="utf-8")
            broken = text.replace('package-dir = {"" = "src"}',
                                  'package-dir = {"" = "experiments"}')
            self.assertNotEqual(broken, text)
            (project / "pyproject.toml").write_text(broken, encoding="utf-8")
            derived, proc = self._witness(project, tmp)
        self.assertIsNone(derived, "a mapping was derived from broken metadata")
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("No module named 'mtj_foundry'", proc.stderr)

    def test_NEGATIVE_CONTROL_corrupting_find_where_reddens_the_SAME_witness(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            project = self._scratch_project(tmp)
            text = (project / "pyproject.toml").read_text(encoding="utf-8")
            broken = text.replace('where = ["src"]', 'where = ["experiments"]')
            self.assertNotEqual(broken, text)
            (project / "pyproject.toml").write_text(broken, encoding="utf-8")
            derived, proc = self._witness(project, tmp)
        self.assertIsNone(derived)
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("No module named 'mtj_foundry'", proc.stderr)

    def test_NEGATIVE_CONTROL_excluding_the_package_reddens_the_SAME_witness(self):
        """`include` no longer matches `mtj_foundry`, so discovery yields nothing
        even though the source tree is untouched and sitting right there."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            project = self._scratch_project(tmp)
            text = (project / "pyproject.toml").read_text(encoding="utf-8")
            broken = text.replace('include = ["mtj_foundry*"]',
                                  'include = ["something_else*"]')
            self.assertNotEqual(broken, text)
            (project / "pyproject.toml").write_text(broken, encoding="utf-8")
            self.assertTrue((project / "src" / "mtj_foundry" / "__init__.py").is_file())
            derived, proc = self._witness(project, tmp)
        self.assertIsNone(derived)
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("No module named 'mtj_foundry'", proc.stderr)

    def test_NEGATIVE_CONTROL_without_the_derived_mapping_the_same_command_fails(self):
        """Metadata intact, mapping deliberately not provisioned. Without this,
        the positive test could be proving something about the machine."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            project = self._scratch_project(tmp)
            derived, proc = self._witness(project, tmp, provision=False)
        self.assertIsNone(derived)
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("No module named 'mtj_foundry'", proc.stderr)

    def test_the_witness_never_reaches_the_repository_source_tree(self):
        """Belt and braces on the coupling: with the scratch sources deleted but
        the metadata intact, the derivation must find nothing rather than fall
        back to the repository."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            project = self._scratch_project(tmp)
            shutil.rmtree(project / "src" / "mtj_foundry")
            self.assertIsNone(derive_editable_source(project))


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


class TestTheContractStatesTheEvidenceBoundaryExactly(unittest.TestCase):
    """C8.5E.R1. The contract must keep the two evidence classes apart.

    Blurring them is what the Manager stopped: a committed harness that names the
    repository source tree proves EXPLICIT_SOURCE_LAYOUT, and calling it an
    install proof would let the weakest available evidence carry the strongest
    claim."""

    @classmethod
    def setUpClass(cls):
        cls.text = CONTRACT.read_text(encoding="utf-8")

    def test_both_evidence_classes_are_named(self):
        self.assertIn("REAL_INSTALL_PROVISIONING", self.text)
        self.assertIn("METADATA_DRIVEN_EDITABLE_IMPORT_PROOF", self.text)

    def test_the_real_install_evidence_is_marked_worker_local_and_not_the_test(self):
        self.assertIn("status: OBSERVED_ONCE", self.text)
        self.assertIn("evidence_kind: WORKER_LOCAL", self.text)
        self.assertIn("is_it_what_the_committed_test_does: NO", self.text)
        self.assertIn("C8.5D", self.text)

    def test_the_committed_proof_is_marked_committed_and_metadata_coupled(self):
        self.assertIn("status: COMMITTED_AND_ENFORCED", self.text)
        for term in ("tomllib", "package-dir", "packages.find",
                     "turns the SAME import witness red"):
            with self.subTest(term=term):
                self.assertIn(term, self.text)

    def test_the_contract_denies_that_the_committed_test_runs_pip(self):
        self.assertIn("No committed test runs pip", self.text)

    def test_the_contract_denies_that_it_is_explicit_source_layout_in_disguise(self):
        self.assertIn("it never names the repository source tree", self.text)

    def test_NEGATIVE_CONTROL_dropping_the_boundary_is_caught(self):
        """In memory; no file is written."""
        broken = self.text.replace("METADATA_DRIVEN_EDITABLE_IMPORT_PROOF", "X")
        self.assertNotEqual(broken, self.text)
        self.assertNotIn("METADATA_DRIVEN_EDITABLE_IMPORT_PROOF", broken)

    def test_NEGATIVE_CONTROL_claiming_the_committed_test_installs_is_caught(self):
        broken = self.text.replace("is_it_what_the_committed_test_does: NO",
                                   "is_it_what_the_committed_test_does: YES")
        self.assertNotEqual(broken, self.text)
        self.assertNotIn("is_it_what_the_committed_test_does: NO", broken)


if __name__ == "__main__":
    unittest.main()
