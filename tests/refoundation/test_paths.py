"""ProjectPaths: one layout owner, explicit roots, no discovery by accident."""

from __future__ import annotations

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
