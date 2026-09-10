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

    def test_the_operational_codebook_is_named_here(self):
        """C8.5P. `codebook_store.read` takes an explicit path and owns no
        default, so the default has to come from the layout owner — otherwise
        the only source is the legacy facade's `CODEBOOK_PATH` and no consumer
        can ever stop importing it. Same shape as its registry sibling."""
        paths = ProjectPaths.for_root("/r")
        self.assertEqual(paths.legacy_codebook_json,
                         Path("/r/experiments/out/foundry/codebook.json"))
        self.assertEqual(paths.legacy_codebook_json,
                         paths.legacy_foundry_out / "codebook.json")

    def test_naming_the_codebook_performs_no_io_and_asserts_no_existence(self):
        """NAMING IS NOT CLASSIFYING: the property is pure derivation. Proven on
        a root that cannot exist, so any stat/open would fail or lie."""
        paths = ProjectPaths.for_root("/nonexistent-root-9d2f")
        value = paths.legacy_codebook_json
        self.assertEqual(value, Path("/nonexistent-root-9d2f/experiments/out/foundry/codebook.json"))
        self.assertFalse(value.exists())


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


class TestTheRootInvariantIsStructural(unittest.TestCase):
    """F1: the invariant belongs to the CLASS, not to one constructor.

    `ProjectPaths` is a dataclass, so `ProjectPaths(root=Path("rel"))` is a supported
    construction path. Normalizing only inside `for_root` enforced the rule only for
    callers who happened to use it — a convention wearing an invariant's clothes.
    """

    def test_the_direct_constructor_normalizes_too(self):
        paths = ProjectPaths(root=Path("some/relative/root"))
        self.assertTrue(paths.root.is_absolute(), paths.root)

    def test_the_direct_constructor_is_not_cwd_dependent(self):
        original = os.getcwd()
        self.addCleanup(os.chdir, original)
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            os.chdir(a)
            paths = ProjectPaths(root=Path("rel"))
            before = (paths.root, paths.baselines, paths.legacy_foundry_out)
            os.chdir(b)
            self.assertEqual(before, (paths.root, paths.baselines, paths.legacy_foundry_out))

    def test_the_two_constructors_agree(self):
        self.assertEqual(ProjectPaths(root=Path("a/b")), ProjectPaths.for_root("a/b"))
        self.assertEqual(ProjectPaths(root=Path("/x/../y")), ProjectPaths.for_root("/y"))

    def test_dataclasses_replace_preserves_the_invariant(self):
        import dataclasses

        replaced = dataclasses.replace(ProjectPaths.for_root("/anchor"),
                                       root=Path("relative/after"))
        self.assertTrue(replaced.root.is_absolute(), replaced.root)

    def test_the_invariant_holds_without_touching_the_filesystem(self):
        with unittest.mock.patch.object(Path, "exists",
                                        side_effect=AssertionError("existence checked")), \
             unittest.mock.patch.object(Path, "resolve",
                                        side_effect=AssertionError("resolve() called")), \
             unittest.mock.patch.object(Path, "stat",
                                        side_effect=AssertionError("stat() called")):
            self.assertTrue(ProjectPaths(root=Path("rel/x")).root.is_absolute())


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


# ---------------------------------------------------------------------------
# MIGRATION SLICE 1 — LAYOUT OWNERSHIP
# ---------------------------------------------------------------------------
#
# The accepted experiments-migration master plan (R2/R3/R4/R5 corrected by R6)
# moves configuration, generated output, frozen benchmark evidence and history
# into destinations that DO NOT EXIST at this commit. Slice 1 names them and
# moves nothing, so that no later slice has to restate a repository-relative
# fact the layout owner already knows.
#
# This table IS the slice-1 contract. It is keyed by property name and valued by
# the exact repository-relative destination, because a count cannot see a
# substitution: a completeness check that only compared LENGTHS would stay green
# while a property silently pointed somewhere else.

S1_DESTINATIONS: dict[str, str] = {
    # config/ — four kinds of tracked input, plus the CR edition and the
    # thesaurus input. `config` and `baselines` are pre-existing and are pinned
    # separately, below, as conserved.
    "config_selectors": "config/selectors",
    "config_semantic": "config/semantic",
    "config_generated": "config/generated",
    "config_registers": "config/registers",
    "config_cr": "config/cr",
    "config_thesaurus": "config/thesaurus",
    # var/ — one ignored root for generated output, ownership visible beneath it.
    "var": "var",
    "var_codebook": "var/codebook",
    "var_mtg": "var/mtg",
    "var_mtg_cr": "var/mtg/cr",
    "var_evidence": "var/evidence",
    "var_thesaurus": "var/thesaurus",
    "var_ops": "var/ops",
    "var_ops_axis_review": "var/ops/axis_review",
    "var_guards": "var/guards",
    "var_benchmarks": "var/benchmarks",
    "var_benchmarks_aq4": "var/benchmarks/aq4",
    "var_archive": "var/archive",
    "var_archive_engine": "var/archive/engine",
    # benchmarks/ — frozen, tracked, byte-pinned research evidence.
    "benchmarks": "benchmarks",
    "benchmarks_aq4": "benchmarks/aq4",
    "benchmarks_path_e": "benchmarks/path_e",
    # archive/ — inert history, kept as evidence.
    "archive": "archive",
    "archive_config": "archive/config",
    "archive_engine": "archive/engine",
    "archive_reports": "archive/reports",
    "archive_research": "archive/research",
    "archive_research_triage": "archive/research/triage",
    "archive_research_consolidation": "archive/research/consolidation",
    "archive_research_mutations": "archive/research/mutations",
    "archive_research_batch8": "archive/research/batch8",
    "archive_research_thesaurus_measurement": "archive/research/thesaurus-measurement",
}

# Every public property that existed BEFORE slice 1, with its exact value. Slice
# 1 adds names; it may not move one. Pinned by value rather than by name so that
# a repointed existing property fails here instead of passing a name-only check.
PRE_S1_PROPERTIES: dict[str, str] = {
    "baselines": "config/baselines",
    # S3 MOVED THIS FILE and the owner moved with it. Bytes, selected
    # snapshot and authority meaning are unchanged; only the location moved.
    "codebook_authority_selector": "config/selectors/codebook-authority.json",
    "config": "config",
    "conservation": "refoundation/conservation",
    "decisions": "refoundation/decisions",
    "foundry_audit_baseline": "config/baselines/foundry-audit-baseline.json",
    "legacy_codebook_json": "experiments/out/foundry/codebook.json",
    "legacy_data_artifacts": "data/artifacts",
    "legacy_docs": "docs",
    "legacy_experiments": "experiments",
    "legacy_experiments_out": "experiments/out",
    "legacy_foundry_out": "experiments/out/foundry",
    "legacy_foundry_review": "experiments/out/foundry/review",
    "legacy_oracle_cards": "data/raw/oracle-cards.jsonl.gz",
    "legacy_pipeline": "pipeline",
    "legacy_ruling_registry_json": "experiments/out/foundry/ruling_registry.json",
    "refoundation": "refoundation",
    "src": "src",
    "tests": "tests",
}


def _public_properties() -> set[str]:
    return {n for n in dir(ProjectPaths)
            if not n.startswith("_")
            and isinstance(getattr(ProjectPaths, n), property)}


class TestSliceOneDestinationsAreNamed(unittest.TestCase):
    """Slice 1: the accepted destinations have names before anything moves."""

    def test_every_destination_resolves_to_its_accepted_path(self):
        paths = ProjectPaths.for_root("/r")
        for name, relative in sorted(S1_DESTINATIONS.items()):
            with self.subTest(destination=name):
                self.assertEqual(getattr(paths, name),
                                 Path("/r").joinpath(*relative.split("/")))

    def test_the_destination_set_is_complete(self):
        """THE SLICE-1 NEGATIVE CONTROL.

        Deleting or renaming a required destination property must fail HERE, in
        one focused assertion that names the missing property — not as a count
        that quietly drops by one, and not as an `AttributeError` raised from
        somewhere downstream months later.
        """
        missing = sorted(set(S1_DESTINATIONS) - _public_properties())
        self.assertEqual(missing, [],
                         f"slice-1 destination properties are missing: {missing}")

    def test_a_child_derives_from_its_intermediate_owner(self):
        """Intermediates exist so a group can be re-pointed in ONE place.

        Asserted as a relationship rather than as two independent literals: if a
        child restated its own segments, both would still equal their pinned
        values above while the intermediate had stopped being the owner.
        """
        p = ProjectPaths.for_root("/r")
        for child, owner, segment in [
            (p.config_selectors, p.config, "selectors"),
            (p.config_semantic, p.config, "semantic"),
            (p.config_generated, p.config, "generated"),
            (p.config_registers, p.config, "registers"),
            (p.config_cr, p.config, "cr"),
            (p.config_thesaurus, p.config, "thesaurus"),
            (p.var_codebook, p.var, "codebook"),
            (p.var_mtg, p.var, "mtg"),
            (p.var_mtg_cr, p.var_mtg, "cr"),
            (p.var_evidence, p.var, "evidence"),
            (p.var_thesaurus, p.var, "thesaurus"),
            (p.var_ops, p.var, "ops"),
            (p.var_ops_axis_review, p.var_ops, "axis_review"),
            (p.var_guards, p.var, "guards"),
            (p.var_benchmarks, p.var, "benchmarks"),
            (p.var_benchmarks_aq4, p.var_benchmarks, "aq4"),
            (p.var_archive, p.var, "archive"),
            (p.var_archive_engine, p.var_archive, "engine"),
            (p.benchmarks_aq4, p.benchmarks, "aq4"),
            (p.benchmarks_path_e, p.benchmarks, "path_e"),
            (p.archive_config, p.archive, "config"),
            (p.archive_engine, p.archive, "engine"),
            (p.archive_reports, p.archive, "reports"),
            (p.archive_research, p.archive, "research"),
            (p.archive_research_triage, p.archive_research, "triage"),
            (p.archive_research_consolidation, p.archive_research, "consolidation"),
            (p.archive_research_mutations, p.archive_research, "mutations"),
            (p.archive_research_batch8, p.archive_research, "batch8"),
            (p.archive_research_thesaurus_measurement,
             p.archive_research, "thesaurus-measurement"),
        ]:
            with self.subTest(child=str(child)):
                self.assertEqual(child, owner / segment)

    def test_the_generated_root_and_the_frozen_benchmark_are_different_places(self):
        """`var/benchmarks/aq4` is where a run WOULD write; `benchmarks/aq4` is
        the frozen tracked evidence. Naming an output destination schedules no
        run — AQ4 is PAUSED and produces nothing — but conflating the two would
        put generated output on top of pre-registered benchmark law."""
        p = ProjectPaths.for_root("/r")
        self.assertNotEqual(p.var_benchmarks_aq4, p.benchmarks_aq4)
        self.assertEqual(p.var_benchmarks_aq4, Path("/r/var/benchmarks/aq4"))
        self.assertEqual(p.benchmarks_aq4, Path("/r/benchmarks/aq4"))
        # Same distinction, one root down: archived SOURCE vs archived OUTPUT.
        self.assertNotEqual(p.archive_engine, p.var_archive_engine)
        # And config INPUT vs thesaurus OUTPUT.
        self.assertNotEqual(p.config_thesaurus, p.var_thesaurus)

    def test_naming_a_destination_touches_no_filesystem(self):
        """NAMING IS NOT CREATING. Every destination is derived under patches
        that turn any probe into an immediate failure, on a root that cannot
        exist — so a stat, a resolve or an existence check would have to fail
        or lie rather than pass quietly."""
        with unittest.mock.patch.object(Path, "exists",
                                        side_effect=AssertionError("existence checked")), \
             unittest.mock.patch.object(Path, "resolve",
                                        side_effect=AssertionError("resolve() called")), \
             unittest.mock.patch.object(Path, "stat",
                                        side_effect=AssertionError("stat() called")), \
             unittest.mock.patch.object(Path, "mkdir",
                                        side_effect=AssertionError("mkdir() called")), \
             unittest.mock.patch.object(Path, "iterdir",
                                        side_effect=AssertionError("iterdir() called")):
            paths = ProjectPaths.for_root("/nonexistent-root-4b7e")
            for name in sorted(S1_DESTINATIONS):
                self.assertTrue(str(getattr(paths, name)).startswith("/nonexistent-root-4b7e"))

    def test_no_destination_is_required_to_exist(self):
        """The whole point of naming early: these directories are absent, and
        the property set is fully usable anyway."""
        paths = ProjectPaths.for_root("/nonexistent-root-4b7e")
        for name in sorted(S1_DESTINATIONS):
            with self.subTest(destination=name):
                self.assertFalse(getattr(paths, name).exists())

    def test_destinations_are_cwd_stable_like_every_other_property(self):
        original = os.getcwd()
        self.addCleanup(os.chdir, original)
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            os.chdir(a)
            paths = ProjectPaths.for_root("relative-root")
            before = {n: getattr(paths, n) for n in S1_DESTINATIONS}
            os.chdir(b)
            self.assertEqual(before, {n: getattr(paths, n) for n in S1_DESTINATIONS})

    def test_the_slice_did_not_move_an_existing_property(self):
        """CONSERVATION. Slice 1 adds names; it may not repoint one.

        Pinned by VALUE, not by name: a name-only check stays green when an
        existing property is quietly redirected, which is the exact substitution
        a cardinality guard cannot see.
        """
        paths = ProjectPaths.for_root("/r")
        for name, relative in sorted(PRE_S1_PROPERTIES.items()):
            with self.subTest(preexisting=name):
                self.assertEqual(getattr(paths, name),
                                 Path("/r").joinpath(*relative.split("/")))

    def test_the_two_property_sets_are_disjoint_and_together_are_everything(self):
        """No pre-S1 name was reused for a destination, and nothing else was
        added while the slice was open."""
        self.assertEqual(set(PRE_S1_PROPERTIES) & set(S1_DESTINATIONS), set())
        self.assertEqual(set(PRE_S1_PROPERTIES) | set(S1_DESTINATIONS),
                         _public_properties())
