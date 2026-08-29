"""ProjectPaths: one layout owner, explicit roots, no discovery by accident."""

from __future__ import annotations

import os
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT  # noqa: F401  (sets sys.path)

from mtj_foundry.paths import ProjectPaths, RootNotFound, discover_root


class TestExplicitRoot(unittest.TestCase):
    """Acceptance criterion: "ProjectPaths/equivalent accepts explicit arbitrary root"."""

    def test_an_arbitrary_nonexistent_root_is_accepted(self):
        paths = ProjectPaths.for_root("/definitely/not/a/real/place")
        self.assertEqual(paths.root, Path("/definitely/not/a/real/place"))
        self.assertEqual(paths.baselines,
                         Path("/definitely/not/a/real/place/config/baselines"))

    def test_construction_touches_no_filesystem(self):
        """A layout description must not become a filesystem assertion."""
        with unittest.mock.patch.object(Path, "exists",
                                        side_effect=AssertionError("filesystem probed")):
            paths = ProjectPaths.for_root("/anywhere")
            _ = (paths.src, paths.tests, paths.config, paths.baselines,
                 paths.refoundation, paths.decisions, paths.conservation,
                 paths.legacy_docs, paths.legacy_experiments, paths.legacy_experiments_out,
                 paths.legacy_foundry_out, paths.legacy_pipeline, paths.resolve("a", "b"))

    def test_two_roots_do_not_share_state(self):
        a = ProjectPaths.for_root("/root-a")
        b = ProjectPaths.for_root("/root-b")
        self.assertNotEqual(a.baselines, b.baselines)
        self.assertTrue(str(a.baselines).startswith("/root-a"))

    def test_paths_are_immutable(self):
        paths = ProjectPaths.for_root("/x")
        with self.assertRaises(Exception):
            paths.root = Path("/y")  # type: ignore[misc]

    def test_layout_is_owned_here_including_the_legacy_generated_area(self):
        """C1: `experiments/out/...` knowledge must live in ONE place, not ~97."""
        paths = ProjectPaths.for_root("/r")
        self.assertEqual(paths.legacy_foundry_out, Path("/r/experiments/out/foundry"))
        self.assertEqual(paths.legacy_experiments_out, Path("/r/experiments/out"))


class TestExplicitRootIsStable(unittest.TestCase):
    """R2: a constructed ProjectPaths must not depend on the process working directory.

    Storing a relative root verbatim made the object cwd-dependent: the same property
    returned different files before and after a chdir, so it was not the stable layout
    description it claims to be.
    """

    def test_a_relative_root_becomes_absolute_at_construction(self):
        paths = ProjectPaths.for_root("some/relative/root")
        self.assertTrue(paths.root.is_absolute(), paths.root)
        self.assertTrue(str(paths.root).endswith("some/relative/root"))

    def test_a_chdir_after_construction_cannot_change_derived_paths(self):
        original = os.getcwd()
        self.addCleanup(os.chdir, original)
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            os.chdir(a)
            paths = ProjectPaths.for_root("relative-root")
            before = (paths.root, paths.baselines, paths.decisions,
                      paths.legacy_foundry_out, paths.resolve("x", "y"))
            os.chdir(b)
            after = (paths.root, paths.baselines, paths.decisions,
                     paths.legacy_foundry_out, paths.resolve("x", "y"))
            self.assertEqual(before, after)

    def test_dot_means_the_directory_at_construction_time(self):
        """Compared against os.getcwd(), not against the temp dir's logical name.

        On macOS `/var` is a symlink to `/private/var`, and `os.getcwd()` reports the
        PHYSICAL path while tempfile hands back the logical one. That difference comes
        from the OS, not from this module — nothing here resolves a symlink. The
        guarantee under test is that the root is fixed at construction, so the
        expectation is the cwd as the OS reported it at that moment.
        """
        original = os.getcwd()
        self.addCleanup(os.chdir, original)
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            os.chdir(a)
            expected = Path(os.getcwd())
            paths = ProjectPaths.for_root(".")
            os.chdir(b)
            self.assertEqual(paths.root, expected)
            self.assertNotEqual(Path(os.getcwd()), paths.root)

    def test_an_absolute_root_is_stored_unchanged(self):
        self.assertEqual(ProjectPaths.for_root("/already/absolute").root,
                         Path("/already/absolute"))

    def test_parent_segments_are_collapsed_lexically_not_by_resolving(self):
        """normpath is textual; resolve() would touch the filesystem and follow links."""
        self.assertEqual(ProjectPaths.for_root("/a/b/../c").root, Path("/a/c"))

    def test_normalization_calls_neither_exists_nor_resolve(self):
        """The whole point of C1: describing a layout is not asserting one."""
        with unittest.mock.patch.object(Path, "exists",
                                        side_effect=AssertionError("existence checked")), \
             unittest.mock.patch.object(Path, "resolve",
                                        side_effect=AssertionError("resolve() called")), \
             unittest.mock.patch.object(Path, "stat",
                                        side_effect=AssertionError("stat() called")):
            self.assertTrue(ProjectPaths.for_root("relative/x").root.is_absolute())
            self.assertEqual(ProjectPaths.for_root("/abs/x").root, Path("/abs/x"))

    def test_a_nonexistent_relative_root_is_still_accepted(self):
        paths = ProjectPaths.for_root("definitely/not/here")
        self.assertFalse(paths.root.exists())
        self.assertTrue(paths.root.is_absolute())


class TestDiscoveryIsExplicitOnly(unittest.TestCase):
    def test_discovery_finds_a_marked_root_when_asked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            (root / "a" / "b").mkdir(parents=True)
            (root / ".git").mkdir()
            self.assertEqual(discover_root(root / "a" / "b"), root.absolute())

    def test_discovery_halts_loudly_rather_than_guessing(self):
        """Explicitly asked and unable to answer is an error, not a silent fallback."""
        with tempfile.TemporaryDirectory() as tmp:
            deep = Path(tmp) / "x" / "y"
            deep.mkdir(parents=True)
            try:
                found = discover_root(deep)
            except RootNotFound:
                return
            # A temp dir can legitimately sit under a marked ancestor; if so the
            # result must still be a real marked root, never a guess at `deep`.
            self.assertTrue((found / ".git").exists())
            self.assertNotEqual(found, deep)


if __name__ == "__main__":
    unittest.main()
