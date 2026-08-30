"""C8 step 4, first slice: three duplicated layout constructions delegate instead.

Stdlib only, like the rest of this tree.

The P0.4A census (issue:1#issuecomment-5465370033, ledger completed in
#issuecomment-5465413819) enumerated every root/layout ownership site in the
tracked Python set and classified them. Three sites shared one shape: they
rebuild the path to the foundry codebook out of a module-local `REPO_ROOT`,

    REPO_ROOT / "out" / "foundry" / "codebook.json"

while `foundry_common` — which both files ALREADY import — exports exactly that
directory as `FOUNDRY_OUT_DIR`. So the layout fact `experiments/out/foundry` was
stated three more times than it is known.

**This is a delegation, not a re-derivation.** The migrated expression resolves
to the byte-identical path; the census proved the equivalence before the change
and the tests below re-prove it from the live modules. Nothing about what the
tools MEASURE moves, which is why the three Gate 2 rows that cover these files
(`ground_truth`, `ground_truth_wide`, `probe_guards`) keep their argv and their
meaning.

WHY THIS SEAM AND NOT foundry_common ITSELF
-------------------------------------------
`foundry_common` has the highest fan-in in the repository (83 importers) and
imports `tier_engine` at import time; changing it first maximises blast radius.
It is instead the COMPATIBILITY BOUNDARY — the one legacy module that a later
phase re-points at `mtj_foundry.paths.ProjectPaths`, in one place rather than at
N call sites. That later step is blocked on an unauthorized package/sys.path
decision and is deliberately not taken here.
"""

from __future__ import annotations

import ast
import dataclasses
import unittest
from pathlib import Path

from tests.refoundation import layout_census
from tests.refoundation.helpers import REPO_ROOT
from tests.refoundation.test_gate2_purity import gate_rows, load_legacy

from mtj_foundry.paths import ProjectPaths

PATHS = ProjectPaths.for_root(REPO_ROOT)
EXPERIMENTS = PATHS.legacy_experiments

GROUND_TRUTH = EXPERIMENTS / "foundry_ground_truth.py"
PROBE = EXPERIMENTS / "foundry_probe.py"

# The three sites the census selected, as (file, expected delegating expressions).
MIGRATED = {GROUND_TRUTH: 2, PROBE: 1}

# P0.4C, the second slice: the four remaining census-selected foundry-output
# restatements, in the three legacy files that also already import
# foundry_common. Same shape, same compatibility boundary, two more suffixes.
R5 = EXPERIMENTS / "foundry_r5_attribution.py"
SLUG_REPARSE = EXPERIMENTS / "foundry_slug_reparse.py"
WIRE = EXPERIMENTS / "foundry_wire_experiment.py"

SECOND_SLICE = {
    R5: {"backups": 1},
    SLUG_REPARSE: {"codebook.json": 1},
    WIRE: {"codebook.json": 1, "wire": 1},
}

# P0.4E, the third slice: root-relative CONSUMPTIONS delegated to the
# compatibility ROOT rather than to a directory under it. Different provider
# (`fc.REPO_ROOT`), same boundary, and the first slice whose two consumers both
# run GREEN in an isolated worktree -- which is why it can carry byte-identical
# before/after runtime evidence instead of structure-only review.
REACHABILITY = EXPERIMENTS / "foundry_reachability.py"

THIRD_SLICE = {
    REACHABILITY: 2,   # WORKFLOWS, and the inverse_census glob base
    PROBE: 1,          # GRAMMAR
}

# P0.4J, the seventh slice: ONE root-relative consumption in
# `foundry_wire_capability.py` — the tier_engine corpus it reads to build a
# name index. Same provider and boundary as the third/fifth/sixth slices.
#
# `WIRE` above is `foundry_wire_experiment.py`, a DIFFERENT file migrated by
# P0.4C. The name is spelled out here so the two can never be confused.
WIRE_CAPABILITY = EXPERIMENTS / "foundry_wire_capability.py"

# The adjacent `ANCHORS_PATH = REPO / "anchors.txt"` is DELIBERATELY out of this
# slice and is asserted unchanged below.

COVERING_GATE2_ROWS = ("ground_truth", "ground_truth_wide", "probe_guards")


# ---------------------------------------------------------------------------
# The property, expressed once so a negative control can aim at it
# ---------------------------------------------------------------------------


def independent_foundry_out_constructions(source: str) -> list[str]:
    """Sites that rebuild the foundry-out path instead of delegating to it.

    Renamed from `independent_codebook_constructions` when P0.4C added the
    `backups` and `wire` siblings: the shape it matches was never codebook-
    specific, and a name that says otherwise is the kind of quiet untruth the
    census was written to find. Every P0.4B assertion below is unchanged.

    A checker, not an assertion, so the controls below can run it against a
    deliberately reverted source and require it to FIRE.

    Keyed on the SHAPE — a path join carrying the literals `out` and `foundry` —
    rather than on the name `REPO_ROOT`. The census measured that the name is
    unreliable: 53 modules bind `REPO_ROOT` to the experiments directory rather
    than the repository root, so a name-based check would both miss real sites
    and flag correct ones.
    """
    matches = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Div):
            continue
        literals = [n.value for n in ast.walk(node)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        if "out" in literals and "foundry" in literals:
            matches.append(node)
    # OUTERMOST ONLY. `REPO_ROOT / "out" / "foundry" / "codebook.json"` is a
    # left-nested chain, so the inner `REPO_ROOT / "out" / "foundry"` matches the
    # same test and one site scores twice. This is the third recorded instance of
    # the nesting double-count in this arc -- it inflated
    # REPOSITORY_ROOT_DERIVATION 268 -> 174 in the P0.4A census -- so it is fixed
    # the same way here rather than absorbed into an expected count.
    inner = {id(d) for n in matches for d in ast.walk(n) if d is not n}
    return [f"line {n.lineno}: {ast.unparse(n)}"
            for n in matches if id(n) not in inner]


def delegating_expressions(source: str, suffix: str = "codebook.json") -> list[str]:
    """Occurrences of `fc.FOUNDRY_OUT_DIR / <suffix>`.

    `suffix` defaults to `codebook.json` so every P0.4B call site keeps asserting
    exactly what it asserted before P0.4C existed.
    """
    found = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Div):
            continue
        if not (isinstance(node.right, ast.Constant)
                and node.right.value == suffix):
            continue
        left = node.left
        if (isinstance(left, ast.Attribute) and left.attr == "FOUNDRY_OUT_DIR"
                and isinstance(left.value, ast.Name) and left.value.id == "fc"):
            found.append(f"line {node.lineno}: {ast.unparse(node)}")
    return found


class TestTheThreeSitesDelegate(unittest.TestCase):
    def test_each_file_has_the_expected_number_of_delegating_expressions(self):
        for path, expected in MIGRATED.items():
            with self.subTest(file=path.name):
                got = delegating_expressions(path.read_text(encoding="utf-8"))
                self.assertEqual(len(got), expected, got)

    def test_no_independent_construction_remains_in_either_file(self):
        for path in MIGRATED:
            with self.subTest(file=path.name):
                self.assertEqual(
                    independent_foundry_out_constructions(path.read_text(encoding="utf-8")),
                    [])

    def test_both_files_already_imported_the_compatibility_boundary(self):
        """The seam adds NO import. That is what keeps it inside current law —
        no new sys.path mutation, no package-install assumption."""
        for path in MIGRATED:
            with self.subTest(file=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertIn("import foundry_common as fc", source)
                self.assertEqual(source.count("import foundry_common"), 1)


class TestTheCheckerCatchesAReversion(unittest.TestCase):
    """NEGATIVE CONTROL — one per migrated site, derived from the live source.

    Deriving each case by mutating today's file, rather than pasting the old
    text, keeps the control aimed at the property after the files move on.
    """

    CASES = {
        "ground_truth read site": (
            GROUND_TRUTH,
            '        (fc.FOUNDRY_OUT_DIR / "codebook.json").read_text(',
            '        (REPO_ROOT / "out" / "foundry" / "codebook.json").read_text('),
        "ground_truth --wide site": (
            GROUND_TRUTH,
            '        cbp = fc.FOUNDRY_OUT_DIR / "codebook.json"',
            '        cbp = REPO_ROOT / "out" / "foundry" / "codebook.json"'),
        "probe CODEBOOK site": (
            PROBE,
            'CODEBOOK = fc.FOUNDRY_OUT_DIR / "codebook.json"',
            'CODEBOOK = REPO_ROOT / "out" / "foundry" / "codebook.json"'),
    }

    def test_restoring_any_one_construction_is_caught(self):
        for label, (path, now, before) in self.CASES.items():
            with self.subTest(site=label):
                source = path.read_text(encoding="utf-8")
                self.assertIn(now, source, "the live text moved; fix the control")
                reverted = source.replace(now, before, 1)
                self.assertNotEqual(reverted, source)
                findings = independent_foundry_out_constructions(reverted)
                self.assertEqual(len(findings), 1, findings)

    def test_reverting_one_site_also_drops_a_delegating_expression(self):
        """Both arms. A checker that only counts the bad shape would pass a file
        that had neither."""
        for label, (path, now, before) in self.CASES.items():
            with self.subTest(site=label):
                source = path.read_text(encoding="utf-8")
                reverted = source.replace(now, before, 1)
                self.assertEqual(len(delegating_expressions(reverted)),
                                 len(delegating_expressions(source)) - 1)


class TestTheResolvedPathIsByteIdentical(unittest.TestCase):
    """The equivalence the whole seam rests on, re-proved from the live modules.

    Structure says the call site delegates; this says the delegation resolves to
    the same file. Both are needed: a delegation to the WRONG constant would pass
    every structural check above.
    """

    @classmethod
    def setUpClass(cls):
        cls.fc = load_legacy("foundry_common")
        cls.probe = load_legacy("foundry_probe")

    def test_probe_codebook_equals_the_delegated_value(self):
        self.assertEqual(self.probe.CODEBOOK,
                         self.fc.FOUNDRY_OUT_DIR / "codebook.json")

    def test_the_delegated_value_equals_the_pre_change_construction(self):
        """`REPO_ROOT / "out" / "foundry" / "codebook.json"` is what the three
        sites used to build. Recomputed here from the module's own REPO_ROOT, it
        must equal what they now delegate to."""
        pre_change = self.probe.REPO_ROOT / "out" / "foundry" / "codebook.json"
        self.assertEqual(self.probe.CODEBOOK, pre_change)

    def test_the_delegated_value_is_the_experiments_out_foundry_codebook(self):
        self.assertEqual(self.probe.CODEBOOK,
                         PATHS.legacy_foundry_out / "codebook.json")


class TestNothingElseMoved(unittest.TestCase):
    """Scope. A seam that quietly widened would be a different change wearing
    this one's name."""

    @classmethod
    def setUpClass(cls):
        cls.probe = load_legacy("foundry_probe")

    def test_the_neighbouring_layout_sites_are_untouched(self):
        """`GRAMMAR` sits on the line after the migrated `CODEBOOK`.

        SUPERSEDED IN ITS SOURCE-TEXT HALF ONLY, BY P0.4E. P0.4B left `GRAMMAR`
        alone as a root-relative docs path and asserted that old text; P0.4E was
        then authorized to migrate exactly this line to `fc.REPO_ROOT`, so the
        expected text moved with it. What the guard MEANS is unchanged and is the
        assertion below: `CODEBOOK` and `GRAMMAR` stay two distinct paths, and
        `GRAMMAR` still resolves to the grammar in `docs/`. That equality is
        byte-for-byte the one P0.4B wrote.
        """
        source = PROBE.read_text(encoding="utf-8")
        self.assertIn('GRAMMAR = fc.REPO_ROOT / "docs" / '
                      '"CODEBOOK-NAMING-GRAMMAR.md"', source)
        self.assertEqual(self.probe.GRAMMAR,
                         PATHS.legacy_docs / "CODEBOOK-NAMING-GRAMMAR.md")

    def test_moves_was_out_of_slice_for_P0_4B_and_is_migrated_by_P0_4I(self):
        """SUPERSEDED IN ITS SOURCE-TEXT HALF ONLY, BY P0.4I.

        Both statements are true and both are durable. P0.4B did NOT move
        `MOVES`: it was a root-relative fixture path, a real ownership site
        deliberately left out of the foundry-out slice, and this guard existed
        to say so. P0.4I then migrated exactly that line to `fc.REPO_ROOT /
        "experiments" / "moves"`, so the expected TEXT moved with it.

        What the guard MEANS is unchanged and is the equality below: `MOVES`
        still resolves to the tracked fixture directory `experiments/moves`, and
        it is still a different path from the foundry-output sites P0.4B did
        migrate in this same file. The `untouched` name and the pre-P0.4I
        expected text are gone rather than left standing as a claim that is
        false at HEAD.
        """
        self.assertIn('MOVES = fc.REPO_ROOT / "experiments" / "moves"',
                      GROUND_TRUTH.read_text(encoding="utf-8"))
        gt = load_legacy("foundry_ground_truth")
        self.assertEqual(gt.MOVES, PATHS.legacy_experiments / "moves")
        self.assertNotEqual(gt.MOVES.parent, PATHS.legacy_foundry_out)

    def test_the_root_derivation_and_syspath_bootstrap_are_untouched(self):
        """The 45 sys.path-only derivations the census found are blocked on an
        unauthorized package decision. This slice does not touch the mechanism."""
        for path in MIGRATED:
            with self.subTest(file=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertIn('REPO_ROOT = Path(__file__).resolve().parent',
                              source)
                self.assertIn('sys.path.insert(0, str(REPO_ROOT))', source)
                self.assertEqual(source.count("sys.path.insert"), 1)

    def test_foundry_common_is_not_modified_by_this_slice(self):
        """It is the compatibility boundary, and a denied path for this task."""
        source = (EXPERIMENTS / "foundry_common.py").read_text(encoding="utf-8")
        # REPAIRED BY C8.5A -- same claim, structural instead of literal.
        self.assertEqual(len(foundry_common_independent_layout(source)), 1)

    def test_the_three_covering_gate2_rows_are_unchanged(self):
        argv = {name: a for name, a, _ in gate_rows()}
        self.assertEqual(argv["ground_truth"],
                         ["experiments/foundry_ground_truth.py"])
        self.assertEqual(argv["ground_truth_wide"],
                         ["experiments/foundry_ground_truth.py", "--wide"])
        self.assertEqual(argv["probe_guards"], ["experiments/foundry_probe.py"])

    def test_no_gate2_row_gained_or_lost_a_flag(self):
        for name, argv, _ in gate_rows():
            if name in COVERING_GATE2_ROWS:
                with self.subTest(row=name):
                    self.assertNotIn("--check-only", argv)
                    self.assertNotIn("--selftest", argv)

    def test_the_probe_public_surface_is_unchanged(self):
        """~9 modules import this one. The constant keeps its NAME; only what it
        is built from changed."""
        for name in ("CODEBOOK", "GRAMMAR", "REPO_ROOT", "corpus", "rows",
                     "domain", "assert_disjoint", "must_capture"):
            with self.subTest(name=name):
                self.assertTrue(hasattr(self.probe, name), name)


# ---------------------------------------------------------------------------
# P0.4C — the second slice
# ---------------------------------------------------------------------------


class TestTheSecondSliceDelegates(unittest.TestCase):
    """The four remaining census-selected foundry-output restatements.

    Same shape as P0.4B and the same compatibility boundary, with two suffixes
    the first slice did not exercise: `backups` and `wire`. That is the point of
    including them — a delegation guard that only ever saw `codebook.json` would
    not be known to work for anything else.
    """

    def test_each_file_has_the_expected_delegating_expressions_per_suffix(self):
        for path, expected in SECOND_SLICE.items():
            source = path.read_text(encoding="utf-8")
            for suffix, count in expected.items():
                with self.subTest(file=path.name, suffix=suffix):
                    got = delegating_expressions(source, suffix)
                    self.assertEqual(len(got), count, got)

    def test_no_independent_foundry_out_construction_remains(self):
        for path in SECOND_SLICE:
            with self.subTest(file=path.name):
                self.assertEqual(
                    independent_foundry_out_constructions(
                        path.read_text(encoding="utf-8")), [])

    def test_no_file_gained_an_import(self):
        """All three already imported the compatibility boundary. The slice adds
        no import, so it needs no sys.path change and no install assumption."""
        for path in SECOND_SLICE:
            with self.subTest(file=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertIn("import foundry_common as fc", source)
                self.assertEqual(source.count("import foundry_common"), 1)


class TestTheSecondSliceCheckerCatchesAReversion(unittest.TestCase):
    """NEGATIVE CONTROL, one per migrated site, derived from the live source."""

    CASES = {
        "r5_attribution BACKUPS": (
            R5,
            'BACKUPS = fc.FOUNDRY_OUT_DIR / "backups"',
            'BACKUPS = REPO / "out" / "foundry" / "backups"',
            "backups"),
        "slug_reparse CODEBOOK": (
            SLUG_REPARSE,
            'CODEBOOK = fc.FOUNDRY_OUT_DIR / "codebook.json"',
            'CODEBOOK = REPO_ROOT / "out" / "foundry" / "codebook.json"',
            "codebook.json"),
        "wire_experiment CODEBOOK": (
            WIRE,
            'CODEBOOK = fc.FOUNDRY_OUT_DIR / "codebook.json"',
            'CODEBOOK = REPO / "out" / "foundry" / "codebook.json"',
            "codebook.json"),
        "wire_experiment OUT_DIR": (
            WIRE,
            'OUT_DIR = fc.FOUNDRY_OUT_DIR / "wire"',
            'OUT_DIR = REPO / "out" / "foundry" / "wire"',
            "wire"),
    }

    def test_restoring_any_one_construction_is_caught(self):
        for label, (path, now, before, _) in self.CASES.items():
            with self.subTest(site=label):
                source = path.read_text(encoding="utf-8")
                self.assertIn(now, source, "the live text moved; fix the control")
                reverted = source.replace(now, before, 1)
                self.assertNotEqual(reverted, source)
                self.assertEqual(
                    len(independent_foundry_out_constructions(reverted)), 1)

    def test_reverting_one_site_also_drops_a_delegating_expression(self):
        """Both arms, so a file with neither shape cannot pass."""
        for label, (path, now, before, suffix) in self.CASES.items():
            with self.subTest(site=label):
                source = path.read_text(encoding="utf-8")
                reverted = source.replace(now, before, 1)
                self.assertEqual(
                    len(delegating_expressions(reverted, suffix)),
                    len(delegating_expressions(source, suffix)) - 1)


class TestTheSecondSliceResolvedPathsAreByteIdentical(unittest.TestCase):
    """Each delegated constant must equal the construction it replaced.

    Recomputed from each module's OWN root-ish variable rather than compared to a
    hardcoded string, so a delegation to the wrong constant fails here even
    though it would satisfy every structural check above.

    NOTE ON EXECUTION: these modules are imported, never run.
    `foundry_r5_attribution`'s documented replay behaviour SWAPS THE LIVE
    CODEBOOK, so running it as verification would mutate the artifact under the
    thing being verified. Import is safe and was confirmed so before importing:
    each module's only top-level statement is its `sys.path.insert`, and `main`
    sits behind `if __name__ == "__main__"`.
    """

    @classmethod
    def setUpClass(cls):
        cls.fc = load_legacy("foundry_common")
        cls.r5 = load_legacy("foundry_r5_attribution")
        cls.sr = load_legacy("foundry_slug_reparse")
        cls.we = load_legacy("foundry_wire_experiment")

    def test_r5_backups_equals_its_pre_change_construction(self):
        self.assertEqual(self.r5.BACKUPS,
                         self.r5.REPO / "out" / "foundry" / "backups")
        self.assertEqual(self.r5.BACKUPS, self.fc.FOUNDRY_OUT_DIR / "backups")

    def test_slug_reparse_codebook_equals_its_pre_change_construction(self):
        self.assertEqual(self.sr.CODEBOOK,
                         self.sr.REPO_ROOT / "out" / "foundry" / "codebook.json")
        self.assertEqual(self.sr.CODEBOOK,
                         self.fc.FOUNDRY_OUT_DIR / "codebook.json")

    def test_wire_experiment_paths_equal_their_pre_change_constructions(self):
        self.assertEqual(self.we.CODEBOOK,
                         self.we.REPO / "out" / "foundry" / "codebook.json")
        self.assertEqual(self.we.OUT_DIR,
                         self.we.REPO / "out" / "foundry" / "wire")
        self.assertEqual(self.we.CODEBOOK,
                         self.fc.FOUNDRY_OUT_DIR / "codebook.json")
        self.assertEqual(self.we.OUT_DIR, self.fc.FOUNDRY_OUT_DIR / "wire")

    def test_all_four_land_under_the_one_foundry_out_directory(self):
        for name, value in (("r5.BACKUPS", self.r5.BACKUPS),
                            ("sr.CODEBOOK", self.sr.CODEBOOK),
                            ("we.CODEBOOK", self.we.CODEBOOK),
                            ("we.OUT_DIR", self.we.OUT_DIR)):
            with self.subTest(constant=name):
                self.assertEqual(value.parent, PATHS.legacy_foundry_out)


class TestTheSecondSliceChangedNothingElse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sr = load_legacy("foundry_slug_reparse")
        cls.r5 = load_legacy("foundry_r5_attribution")

    def test_slug_reparse_grammar_was_out_of_slice_for_P0_4C_and_is_migrated_by_P0_4M(self):
        """BOTH TRUTHS.

        P0.4C migrated `CODEBOOK` on the line BELOW and deliberately left
        `GRAMMAR` alone, guarding that it stayed a local root-relative docs
        path. That was true of P0.4C and is recorded here still. P0.4M migrates
        exactly that line, so the SOURCE-TEXT half of the original claim is
        genuinely superseded and is updated rather than deleted.

        The half that carried the meaning — GRAMMAR resolves to the ratified
        owner's `docs/CODEBOOK-NAMING-GRAMMAR.md` — is UNCHANGED and still
        asserted below, which is the whole point of a value-preserving
        delegation. Nothing about the ruling document moves (C7.4)."""
        source = SLUG_REPARSE.read_text(encoding="utf-8")
        self.assertIn('GRAMMAR = fc.REPO_ROOT / "docs" / '
                      '"CODEBOOK-NAMING-GRAMMAR.md"', source)
        self.assertNotIn('GRAMMAR = REPO_ROOT.parent / "docs" / '
                         '"CODEBOOK-NAMING-GRAMMAR.md"', source)
        self.assertEqual(self.sr.GRAMMAR,
                         PATHS.legacy_docs / "CODEBOOK-NAMING-GRAMMAR.md")

    def test_r5_live_codebook_still_comes_from_foundry_codebook(self):
        """`LIVE` is the codebook this tool REPLACES during replay. It is
        sourced from `foundry_codebook.CODEBOOK_PATH` and this slice does not
        touch it."""
        self.assertIn("LIVE = fcb.CODEBOOK_PATH",
                      R5.read_text(encoding="utf-8"))
        self.assertEqual(self.r5.LIVE, PATHS.legacy_foundry_out / "codebook.json")

    def test_root_derivations_and_syspath_bootstraps_are_untouched(self):
        for path in SECOND_SLICE:
            with self.subTest(file=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertRegex(
                    source, r"REPO(_ROOT)? = Path\(__file__\).resolve\(\).parent\b")
                self.assertEqual(source.count("sys.path.insert"), 1)

    def test_foundry_common_is_still_not_modified(self):
        # REPAIRED BY C8.5A. This slice still added no layout statement to the
        # boundary -- that claim is unchanged and is what is asserted. The old
        # literal was superseded when C8.5A pointed the boundary at ProjectPaths.
        self.assertEqual(
            len(foundry_common_independent_layout(
                (EXPERIMENTS / "foundry_common.py").read_text(encoding="utf-8"))),
            1)

    def test_the_first_slice_files_are_not_touched_by_this_slice(self):
        """P0.4B's three sites keep delegating; this slice widened the guard,
        not the change."""
        self.assertEqual(
            len(delegating_expressions(GROUND_TRUTH.read_text(encoding="utf-8"))), 2)
        self.assertEqual(
            len(delegating_expressions(PROBE.read_text(encoding="utf-8"))), 1)


# ---------------------------------------------------------------------------
# P0.4E — the third slice: delegating the ROOT itself
# ---------------------------------------------------------------------------


def root_delegating_expressions(source: str) -> list[str]:
    """Occurrences of `fc.REPO_ROOT / ...`.

    A different provider from the first two slices: those delegated to a
    DIRECTORY under the root, this delegates the ROOT. Counted with its own
    helper so a P0.4B/P0.4C count can never absorb a P0.4E site.
    """
    matches = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Div):
            continue
        base = node
        while isinstance(base, ast.BinOp) and isinstance(base.op, ast.Div):
            base = base.left
        if (isinstance(base, ast.Attribute) and base.attr == "REPO_ROOT"
                and isinstance(base.value, ast.Name) and base.value.id == "fc"):
            matches.append(node)
    # OUTERMOST ONLY. `fc.REPO_ROOT / "docs" / "X.md"` is a left-nested chain, so
    # the inner `fc.REPO_ROOT / "docs"` matches too and one site scores twice.
    # FOURTH recorded instance of this nesting double-count in this arc; it is
    # fixed the same way every time rather than absorbed into an expected count.
    inner = {id(d) for n in matches for d in ast.walk(n) if d is not n}
    return [f"line {n.lineno}: {ast.unparse(n)}"
            for n in matches if id(n) not in inner]


TOP_LEVEL_DIRS = {".github", "docs", "data", "config", "tags", "experiments",
                  "pipeline", "src", "tests", "refoundation", "bridge"}


def local_root_relative_constructions(source: str, *, exempt_bootstrap: bool = True,
                                      names=("REPO", "REPO_ROOT")) -> list[str]:
    """Path joins that reach a repository DIRECTORY through a LOCAL root variable.

    This is the shape P0.4E removes: `REPO / ".github" / ...` where `REPO` is
    already the root, and `REPO_ROOT.parent / "docs" / ...` where `REPO_ROOT` is
    the experiments directory and `.parent` climbs to it.

    A LITERAL top-level directory name is required. The first version asked only
    that the base be a root variable, and so flagged `REPO / rel`,
    `REPO / e` and `REPO / d / f"{tail}.py"` — runtime joins that resolve a path
    supplied by the caller rather than restating layout. Those are ordinary I/O
    on an explicit path, which C1 does not forbid.

    `exempt_bootstrap` suppresses the join inside `sys.path.insert(...)`, which
    is a root DECISION and stays out of this slice. It is anchored to that CALL,
    not to the shape `REPO / "experiments"`: a shape-based exemption also
    swallowed the reverted `inverse_census` glob base, so that site's negative
    control could never fire. It is a parameter rather than a hardcoded skip so a
    test can prove the exemption is what silences the bootstrap.
    """
    tree = ast.parse(source)
    bootstrap = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("insert", "append")
                and isinstance(node.func.value, ast.Attribute)
                and node.func.value.attr == "path"):
            for d in ast.walk(node):
                bootstrap.add(id(d))
    matches = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Div):
            continue
        base, _climbed = node, False
        while isinstance(base, ast.BinOp) and isinstance(base.op, ast.Div):
            base = base.left
        if isinstance(base, ast.Attribute) and base.attr == "parent":
            _climbed, base = True, base.value
        if not (isinstance(base, ast.Name) and base.id in names):
            continue
        literals = [n.value for n in ast.walk(node)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        if not any(l in TOP_LEVEL_DIRS for l in literals):
            continue
        if exempt_bootstrap and id(node) in bootstrap:
            continue
        matches.append(node)
    # OUTERMOST ONLY, the same left-nesting rule every checker in this file obeys.
    inner = {id(d) for n in matches for d in ast.walk(n) if d is not n}
    return [f"line {n.lineno}: {ast.unparse(n)}"
            for n in matches if id(n) not in inner]


class TestTheThirdSliceDelegatesTheRoot(unittest.TestCase):
    def test_each_file_has_the_expected_number_of_root_delegations(self):
        for path, expected in THIRD_SLICE.items():
            with self.subTest(file=path.name):
                got = root_delegating_expressions(path.read_text(encoding="utf-8"))
                self.assertEqual(len(got), expected, got)

    def test_the_delegations_are_the_expected_three_sites(self):
        reach = root_delegating_expressions(REACHABILITY.read_text(encoding="utf-8"))
        self.assertTrue(any("'.github' / 'workflows'" in g for g in reach), reach)
        self.assertTrue(any("'experiments'" in g for g in reach), reach)
        probe = root_delegating_expressions(PROBE.read_text(encoding="utf-8"))
        self.assertTrue(any("CODEBOOK-NAMING-GRAMMAR.md" in g for g in probe), probe)

    def test_no_local_root_relative_construction_remains(self):
        for path in THIRD_SLICE:
            with self.subTest(file=path.name):
                self.assertEqual(
                    local_root_relative_constructions(path.read_text(encoding="utf-8")),
                    [])

    def test_neither_file_gained_an_import(self):
        for path in THIRD_SLICE:
            with self.subTest(file=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertIn("import foundry_common as fc", source)
                self.assertEqual(source.count("import foundry_common"), 1)


class TestTheThirdSliceCheckerCatchesAReversion(unittest.TestCase):
    CASES = {
        "reachability WORKFLOWS": (
            REACHABILITY,
            'WORKFLOWS = fc.REPO_ROOT / ".github" / "workflows"',
            'WORKFLOWS = REPO / ".github" / "workflows"'),
        "reachability inverse_census glob base": (
            REACHABILITY,
            '    for py in sorted((fc.REPO_ROOT / "experiments").glob("*.py")):',
            '    for py in sorted((REPO / "experiments").glob("*.py")):'),
        "probe GRAMMAR": (
            PROBE,
            'GRAMMAR = fc.REPO_ROOT / "docs" / "CODEBOOK-NAMING-GRAMMAR.md"',
            'GRAMMAR = REPO_ROOT.parent / "docs" / "CODEBOOK-NAMING-GRAMMAR.md"'),
    }

    def test_restoring_any_one_local_construction_is_caught(self):
        for label, (path, now, before) in self.CASES.items():
            with self.subTest(site=label):
                source = path.read_text(encoding="utf-8")
                self.assertIn(now, source, "the live text moved; fix the control")
                reverted = source.replace(now, before, 1)
                self.assertNotEqual(reverted, source)
                self.assertEqual(
                    len(local_root_relative_constructions(reverted)), 1)

    def test_reverting_one_site_also_drops_a_root_delegation(self):
        for label, (path, now, before) in self.CASES.items():
            with self.subTest(site=label):
                source = path.read_text(encoding="utf-8")
                reverted = source.replace(now, before, 1)
                self.assertEqual(
                    len(root_delegating_expressions(reverted)),
                    len(root_delegating_expressions(source)) - 1)

    def test_the_bootstrap_exemption_is_what_silences_the_bootstrap(self):
        """The checker must stay blind to `sys.path.insert(0, str(REPO /
        "experiments"))` — a root DECISION, out of slice — but blind ON PURPOSE.

        Asserting only "no findings" would pass just as well if the shape never
        matched at all. Turning the exemption off must make exactly that line
        appear, which is what proves the exemption is doing the silencing.
        """
        source = REACHABILITY.read_text(encoding="utf-8")
        self.assertEqual(local_root_relative_constructions(source), [])
        unexempted = local_root_relative_constructions(source, exempt_bootstrap=False)
        self.assertEqual(len(unexempted), 1, unexempted)
        self.assertIn("'experiments'", unexempted[0])
        self.assertIn('sys.path.insert(0, str(REPO / "experiments"))', source)


class TestTheThirdSliceResolvedPathsAreByteIdentical(unittest.TestCase):
    """Each delegated value must equal the construction it replaced, recomputed
    from the module's OWN live root binding."""

    @classmethod
    def setUpClass(cls):
        cls.fc = load_legacy("foundry_common")
        cls.reach = load_legacy("foundry_reachability")
        cls.probe = load_legacy("foundry_probe")

    def test_workflows_equals_its_pre_change_construction(self):
        self.assertEqual(self.reach.WORKFLOWS,
                         self.reach.REPO / ".github" / "workflows")
        self.assertEqual(self.reach.WORKFLOWS,
                         self.fc.REPO_ROOT / ".github" / "workflows")

    def test_grammar_equals_its_pre_change_construction(self):
        self.assertEqual(self.probe.GRAMMAR,
                         self.probe.REPO_ROOT.parent / "docs"
                         / "CODEBOOK-NAMING-GRAMMAR.md")
        self.assertEqual(self.probe.GRAMMAR,
                         PATHS.legacy_docs / "CODEBOOK-NAMING-GRAMMAR.md")

    def test_the_inverse_census_glob_base_is_unchanged(self):
        self.assertEqual(self.fc.REPO_ROOT / "experiments",
                         self.reach.REPO / "experiments")
        self.assertEqual(self.fc.REPO_ROOT / "experiments",
                         PATHS.legacy_experiments)

    def test_the_two_local_root_bindings_still_resolve_as_before(self):
        """The slice delegates CONSUMPTION, not the root DECISION. Both files
        still decide a root of their own, and both still agree with fc."""
        self.assertEqual(self.reach.REPO, self.fc.REPO_ROOT)
        self.assertEqual(self.probe.REPO_ROOT.parent, self.fc.REPO_ROOT)


class TestTheThirdSliceChangedNothingElse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.probe = load_legacy("foundry_probe")
        cls.reach = load_legacy("foundry_reachability")

    def test_the_root_decisions_and_bootstraps_survive(self):
        reach = REACHABILITY.read_text(encoding="utf-8")
        self.assertIn("REPO = Path(__file__).resolve().parent.parent", reach)
        self.assertIn('sys.path.insert(0, str(REPO / "experiments"))', reach)
        probe = PROBE.read_text(encoding="utf-8")
        self.assertIn("REPO_ROOT = Path(__file__).resolve().parent", probe)
        self.assertIn("sys.path.insert(0, str(REPO_ROOT))", probe)
        for path in THIRD_SLICE:
            with self.subTest(file=path.name):
                self.assertEqual(
                    path.read_text(encoding="utf-8").count("sys.path.insert"), 1)

    def test_the_foundry_artifact_identifiers_are_untouched(self):
        """They are artifact IDENTIFIERS, not path construction, and P0.3F
        asserts them exactly."""
        self.assertEqual(sorted(self.reach.FOUNDRY_ARTIFACTS), [
            "docs/CODEBOOK-NAMING-GRAMMAR.md",
            "experiments/out/card-tags.json.gz",
            "experiments/out/foundry/codebook.json",
            "experiments/out/foundry/corpus_pass_run1_classification.json",
            "experiments/out/foundry/det-patterns-v2.json",
        ])

    def test_the_probe_codebook_from_the_first_slice_is_untouched(self):
        self.assertEqual(self.probe.CODEBOOK,
                         PATHS.legacy_foundry_out / "codebook.json")
        self.assertEqual(
            len(delegating_expressions(PROBE.read_text(encoding="utf-8"))), 1)

    def test_foundry_common_is_still_not_modified(self):
        # REPAIRED BY C8.5A. This slice still added no layout statement to the
        # boundary -- that claim is unchanged and is what is asserted. The old
        # literal was superseded when C8.5A pointed the boundary at ProjectPaths.
        self.assertEqual(
            len(foundry_common_independent_layout(
                (EXPERIMENTS / "foundry_common.py").read_text(encoding="utf-8"))),
            1)

    def test_the_two_covering_gate2_rows_are_unchanged(self):
        argv = {name: a for name, a, _ in gate_rows()}
        self.assertEqual(argv["reachability"],
                         ["experiments/foundry_reachability.py"])
        self.assertEqual(argv["probe_guards"], ["experiments/foundry_probe.py"])


# ---------------------------------------------------------------------------
# P0.4F — the fourth slice: the prior-art probe's three root/layout restatements
# ---------------------------------------------------------------------------
#
# THREE INDEPENDENT SHAPES, AND ONLY ONE OF THEM IS THE P0.4E SHAPE.
#
#   64   DOCS = REPO_ROOT.parent / "docs"          a root-relative JOIN  (P0.4E shape)
#   65   CODE = REPO_ROOT                          a bare ALIAS of a local root
#   221  sorted((REPO_ROOT.parent / "docs")...)    the SAME docs path, restated
#                                                  a third time, inside dead code
#
# `local_root_relative_constructions` — the P0.4E checker — sees the first and the
# third and is STRUCTURALLY BLIND to the second: `CODE = REPO_ROOT` is not a
# `BinOp/Div` at all, so no path-join checker in this file can ever match it.
# Reusing the P0.4E checker alone would therefore have given site 65 a negative
# control that could not fire, which is exactly the defect P0.4E disclosed about
# its own bootstrap exemption. The alias gets its own checker below, and the test
# that records the blindness is kept as evidence rather than as an inconvenience.
#
# The third site is delegated to `DOCS` rather than to `fc.REPO_ROOT`, because the
# layout fact it restates is already named one screen above it. That means it does
# NOT raise the `fc.REPO_ROOT` count, so it too needs its own positive arm.
#
# The block containing site 221 is UNREACHABLE — `cmd_orphans` returns at line 212
# and nine statements follow. This task delegates its path and deliberately does
# not remove or repair it, so a guard below proves the dead code is still dead.

PRIOR_ART = EXPERIMENTS / "foundry_prior_art.py"

# DOCS and CODE. The dead docs glob consumes DOCS and is counted separately.
FOURTH_SLICE_ROOT_DELEGATIONS = 2


def local_root_aliases(source: str, names=("REPO", "REPO_ROOT")) -> list[str]:
    """Assignments that BIND a local root variable straight to another name.

    `CODE = REPO_ROOT` states the layout fact "the code lives in the experiments
    directory" without a single path literal, so every checker in this file that
    keys on a path JOIN is blind to it by construction. This one keys on the
    assignment instead.

    Kept a checker rather than an inline assertion so the negative control below
    can run it against a deliberately reverted source and require it to FIRE.
    """
    out = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Assign):
            continue
        if isinstance(node.value, ast.Name) and node.value.id in names:
            out.append(f"line {node.lineno}: {ast.unparse(node)}")
    return out


def glob_call_bases(source: str) -> list[tuple[int, str, str]]:
    """`(lineno, base expression, pattern)` for every `X.glob(...)`/`X.rglob(...)`.

    The third site's migration does not change the `fc.REPO_ROOT` count — it stops
    re-deriving `docs/` and consumes the module's own `DOCS` instead — so its
    positive arm has to read the glob's BASE. Reporting the base as source text
    rather than as a resolved value is deliberate: the resolved values are equal
    before and after, which is the whole point, so only the text can tell the two
    apart.
    """
    out = []
    for node in ast.walk(ast.parse(source)):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("glob", "rglob") and node.args
                and isinstance(node.args[0], ast.Constant)):
            out.append((node.lineno, ast.unparse(node.func.value),
                        node.args[0].value))
    return sorted(out)


def dead_statements(source: str, function: str) -> list:
    """Statements that follow a bare `return` in `function`'s own body.

    Used to prove the unreachable orphan block is STILL unreachable. The task
    delegates that block's path and forbids removing or repairing it, and a diff
    that quietly deleted it would otherwise satisfy every delegation guard above
    by making the site disappear.
    """
    fn = next(n for n in ast.walk(ast.parse(source))
              if isinstance(n, ast.FunctionDef) and n.name == function)
    idx = [i for i, node in enumerate(fn.body)
           if isinstance(node, ast.Return) and node.value is None]
    if not idx:
        return []
    return fn.body[idx[-1] + 1:]


class TestTheFourthSliceDelegates(unittest.TestCase):
    def test_the_two_root_delegations_are_the_expected_sites(self):
        got = root_delegating_expressions(PRIOR_ART.read_text(encoding="utf-8"))
        self.assertEqual(len(got), FOURTH_SLICE_ROOT_DELEGATIONS, got)
        self.assertTrue(any("'docs'" in g for g in got), got)
        self.assertTrue(any("'experiments'" in g for g in got), got)

    def test_the_dead_docs_glob_consumes_DOCS(self):
        bases = glob_call_bases(PRIOR_ART.read_text(encoding="utf-8"))
        json_globs = [b for b in bases if b[2] == "*.json"]
        self.assertEqual(len(json_globs), 1, bases)
        self.assertEqual(json_globs[0][1], "DOCS", json_globs)

    def test_no_glob_base_re_derives_the_docs_path(self):
        """The site could have been 'fixed' by writing `fc.REPO_ROOT / "docs"` a
        second time. That would delegate the ROOT and still restate the LAYOUT."""
        for lineno, base, pattern in glob_call_bases(
                PRIOR_ART.read_text(encoding="utf-8")):
            with self.subTest(line=lineno):
                self.assertNotIn("docs", base)

    def test_no_local_root_relative_construction_remains(self):
        self.assertEqual(
            local_root_relative_constructions(
                PRIOR_ART.read_text(encoding="utf-8")), [])

    def test_no_local_root_alias_remains(self):
        self.assertEqual(
            local_root_aliases(PRIOR_ART.read_text(encoding="utf-8")), [])

    def test_the_file_gained_no_import(self):
        source = PRIOR_ART.read_text(encoding="utf-8")
        self.assertIn("import foundry_common as fc", source)
        self.assertEqual(source.count("import foundry_common"), 1)

    def test_fc_is_imported_before_every_delegating_site(self):
        """A module-level constant built from `fc` above the import would be a
        NameError, not a subtle defect — but the dead glob is inside a function,
        so only the two constants are ordered by the import, and that ordering is
        worth pinning rather than inferring."""
        tree = ast.parse(PRIOR_ART.read_text(encoding="utf-8"))
        imp = next(n.lineno for n in tree.body
                   if isinstance(n, ast.Import)
                   and any(a.name == "foundry_common" for a in n.names))
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id in ("DOCS", "CODE")
                    for t in node.targets):
                with self.subTest(line=node.lineno):
                    self.assertGreater(node.lineno, imp)


class TestTheFourthSliceCheckerCatchesAReversion(unittest.TestCase):
    """NEGATIVE CONTROL — one per site, and each aimed at the checker that can
    actually see that site rather than at the one with the closest name."""

    DOCS_NOW = 'DOCS = fc.REPO_ROOT / "docs"'
    DOCS_BEFORE = 'DOCS = REPO_ROOT.parent / "docs"'
    CODE_NOW = 'CODE = fc.REPO_ROOT / "experiments"'
    CODE_BEFORE = "CODE = REPO_ROOT"
    GLOB_NOW = '    for path in sorted(DOCS.glob("*.json")):'
    GLOB_BEFORE = ('    for path in sorted((REPO_ROOT.parent / "docs")'
                   '.glob("*.json")):')

    def revert(self, now: str, before: str) -> str:
        source = PRIOR_ART.read_text(encoding="utf-8")
        self.assertIn(now, source, "the live text moved; fix the control")
        reverted = source.replace(now, before, 1)
        self.assertNotEqual(reverted, source)
        return reverted

    def test_restoring_the_DOCS_join_is_caught(self):
        found = local_root_relative_constructions(
            self.revert(self.DOCS_NOW, self.DOCS_BEFORE))
        self.assertEqual(len(found), 1, found)

    def test_restoring_the_CODE_alias_is_caught(self):
        found = local_root_aliases(self.revert(self.CODE_NOW, self.CODE_BEFORE))
        self.assertEqual(len(found), 1, found)

    def test_the_join_checker_is_blind_to_the_alias_which_is_why_it_has_its_own(self):
        """Recorded, not worked around. `CODE = REPO_ROOT` is not a path join, so
        the P0.4E checker returns clean on a fully reverted site — and a control
        that could never fire reads exactly like a control that passed."""
        reverted = self.revert(self.CODE_NOW, self.CODE_BEFORE)
        self.assertEqual(local_root_relative_constructions(reverted), [])
        self.assertEqual(len(local_root_aliases(reverted)), 1)

    def test_restoring_the_dead_docs_glob_is_caught(self):
        found = local_root_relative_constructions(
            self.revert(self.GLOB_NOW, self.GLOB_BEFORE))
        self.assertEqual(len(found), 1, found)

    def test_the_root_delegation_count_is_blind_to_the_glob_reversion(self):
        """Same discipline as the alias. The third site never raised the
        `fc.REPO_ROOT` count, so counting root delegations cannot police it and
        the glob BASE has to be read."""
        reverted = self.revert(self.GLOB_NOW, self.GLOB_BEFORE)
        self.assertEqual(len(root_delegating_expressions(reverted)),
                         FOURTH_SLICE_ROOT_DELEGATIONS)
        json_globs = [b for b in glob_call_bases(reverted) if b[2] == "*.json"]
        self.assertEqual(len(json_globs), 1, json_globs)
        self.assertNotEqual(json_globs[0][1], "DOCS")

    def test_each_reversion_also_drops_its_own_positive_arm(self):
        """Both arms per site. A checker that only counts the bad shape would pass
        a file that had neither shape."""
        source = PRIOR_ART.read_text(encoding="utf-8")
        for label, now, before in (
                ("DOCS", self.DOCS_NOW, self.DOCS_BEFORE),
                ("CODE", self.CODE_NOW, self.CODE_BEFORE)):
            with self.subTest(site=label):
                reverted = self.revert(now, before)
                self.assertEqual(len(root_delegating_expressions(reverted)),
                                 len(root_delegating_expressions(source)) - 1)
        with self.subTest(site="dead docs glob"):
            reverted = self.revert(self.GLOB_NOW, self.GLOB_BEFORE)
            before_bases = [b[1] for b in glob_call_bases(source)]
            after_bases = [b[1] for b in glob_call_bases(reverted)]
            self.assertIn("DOCS", before_bases)
            self.assertNotIn("DOCS", after_bases)


class TestTheFourthSliceResolvedPathsAreByteIdentical(unittest.TestCase):
    """Each delegated value must equal the construction it replaced, recomputed
    from the module's OWN live root binding.

    NOTE ON EXECUTION: the module is imported, never run. Its only top-level
    statements are the `sys.path.insert`, the constants and the function
    definitions; `main()` sits behind `if __name__ == "__main__"`. It reads
    `docs/` and `experiments/` and writes nothing.
    """

    @classmethod
    def setUpClass(cls):
        cls.fc = load_legacy("foundry_common")
        cls.pa = load_legacy("foundry_prior_art")

    def test_DOCS_equals_its_pre_change_construction(self):
        self.assertEqual(self.pa.DOCS, self.pa.REPO_ROOT.parent / "docs")
        self.assertEqual(self.pa.DOCS, self.fc.REPO_ROOT / "docs")
        self.assertEqual(self.pa.DOCS, PATHS.legacy_docs)

    def test_CODE_equals_its_pre_change_construction(self):
        self.assertEqual(self.pa.CODE, self.pa.REPO_ROOT)
        self.assertEqual(self.pa.CODE, self.fc.REPO_ROOT / "experiments")
        self.assertEqual(self.pa.CODE, PATHS.legacy_experiments)

    def test_the_dead_globs_base_equals_the_expression_it_replaced(self):
        """The removed expression was `REPO_ROOT.parent / "docs"`; the base it now
        consumes is `DOCS`. The point of the site is that those are the same
        path — which is also why nothing but the source text can distinguish
        them, and why the structural guard above exists."""
        self.assertEqual(self.pa.DOCS, self.pa.REPO_ROOT.parent / "docs")

    def test_the_local_root_binding_still_resolves_as_before(self):
        """This slice delegates CONSUMPTION, not the root DECISION. The module
        still decides a root of its own and it still agrees with fc."""
        self.assertEqual(self.pa.REPO_ROOT.parent, self.fc.REPO_ROOT)
        self.assertEqual(self.pa.REPO_ROOT, PATHS.legacy_experiments)

    def test_the_display_prefixes_still_resolve_to_the_repository_root(self):
        """Four report lines strip `str(DOCS.parent)` or `str(REPO_ROOT.parent)`
        off an absolute path. Both are out of slice, and both must keep meaning
        the repository root or every printed path would gain a prefix."""
        self.assertEqual(self.pa.DOCS.parent, self.fc.REPO_ROOT)
        self.assertEqual(self.pa.REPO_ROOT.parent, self.fc.REPO_ROOT)


class TestTheFourthSliceChangedNothingElse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pa = load_legacy("foundry_prior_art")
        cls.source = PRIOR_ART.read_text(encoding="utf-8")

    def test_the_root_decision_and_bootstrap_survive(self):
        self.assertIn("REPO_ROOT = Path(__file__).resolve().parent\n", self.source)
        self.assertIn("sys.path.insert(0, str(REPO_ROOT))", self.source)
        self.assertEqual(self.source.count("sys.path.insert"), 1)

    def test_the_display_expressions_are_untouched(self):
        """`str(DOCS.parent) + '/'` on three report lines and
        `str(REPO_ROOT.parent) + '/'` on a fourth. Not path CONSTRUCTION and not
        in scope; a fourth production change would show up here."""
        self.assertEqual(self.source.count("str(DOCS.parent)"), 3)
        self.assertEqual(self.source.count("str(REPO_ROOT.parent)"), 1)

    def test_the_two_code_rglobs_still_consume_CODE(self):
        py_globs = [b for b in glob_call_bases(self.source) if b[2] == "*.py"]
        self.assertEqual([b[1] for b in py_globs], ["CODE", "CODE"], py_globs)

    def test_the_unreachable_orphan_block_is_still_unreachable(self):
        """The task delegates this block's path and forbids removing or repairing
        it. Deleting it would satisfy every delegation guard above by making the
        site vanish, so the dead code is pinned as dead."""
        dead = dead_statements(self.source, "cmd_orphans")
        self.assertEqual(len(dead), 9, [d.lineno for d in dead])
        globs = [n.lineno for stmt in dead for n in ast.walk(stmt)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                 and n.func.attr == "glob"]
        self.assertEqual(len(globs), 1, globs)

    def test_the_judgement_vocabulary_is_unchanged(self):
        """`RULED`, `ARTIFACT`, `NOISE` and the pipeline constants decide what the
        probe REPORTS. None is a path, and none is in scope."""
        self.assertIn(r"\bVERDICT\b", self.pa.RULED.pattern)
        self.assertIn(r"\bRATIFIED\b", self.pa.RULED.pattern)
        self.assertEqual(
            self.pa.ARTIFACT.pattern,
            r"`([a-z_][a-z0-9_]{3,}(?:\(\)|\.py|\.json|\.yaml))`")
        self.assertEqual(self.pa.NOISE,
                         ("docs/mtg-comprehensive-rules.md",
                          "docs/RATIFIED-RULINGS-REGISTRY.md"))
        self.assertEqual(self.pa.RATIFIED_PIPELINE, "det_scan_texts")
        self.assertIn("oracle_text", self.pa.READS_CARD_TEXT.pattern)

    def test_the_cli_surface_is_unchanged(self):
        for flag in ('ap.add_argument("topic", nargs="*"',
                     'ap.add_argument("--orphans"',
                     'ap.add_argument("--prose"',
                     'ap.add_argument("--strict"',
                     'ap.add_argument("--limit", type=int, default=8)'):
            with self.subTest(flag=flag):
                self.assertIn(flag, self.source)

    def test_this_module_is_not_a_gate2_row(self):
        """Which is WHY the runtime conservation evidence for this slice is a
        direct CLI run rather than a gate row: no standing gate covers it."""
        self.assertNotIn("foundry_prior_art.py",
                         [a[0] for _, a, _ in gate_rows()])

    def test_foundry_common_is_still_not_modified(self):
        # REPAIRED BY C8.5A. This slice still added no layout statement to the
        # boundary -- that claim is unchanged and is what is asserted. The old
        # literal was superseded when C8.5A pointed the boundary at ProjectPaths.
        self.assertEqual(
            len(foundry_common_independent_layout(
                (EXPERIMENTS / "foundry_common.py").read_text(encoding="utf-8"))),
            1)

    def test_the_earlier_slices_sites_are_not_touched(self):
        """P0.4B/P0.4C/P0.4E keep delegating; this slice widened the guard, not
        the change."""
        self.assertEqual(
            len(delegating_expressions(GROUND_TRUTH.read_text(encoding="utf-8"))), 2)
        self.assertEqual(
            len(delegating_expressions(PROBE.read_text(encoding="utf-8"))), 1)
        self.assertEqual(
            len(root_delegating_expressions(
                REACHABILITY.read_text(encoding="utf-8"))), 2)
        self.assertEqual(
            len(root_delegating_expressions(PROBE.read_text(encoding="utf-8"))), 1)


# ---------------------------------------------------------------------------
# P0.4H — the fifth slice: the CR loader's own read path
# ---------------------------------------------------------------------------
#
# ONE expression, in the module CLAUDE.md names as the single gateway to the
# Comprehensive Rules ("never `path.read_text()` a CR — always `foundry_cr.text()`").
#
#   79  CR_PATH = REPO_ROOT.parent / "docs" / "MTG_..._2026-08-07_LLM.md"
#          ->    fc.REPO_ROOT / "docs" / "MTG_..._2026-08-07_LLM.md"
#
# WHY THIS IS PLUMBING AND NOT TRUTH. The conservation contract
# (refoundation/conservation/CONSERVATION-CONTRACT.json, invariant
# CR_EDITION_CONTENT / C7.5) contracts the CR's exact bytes plus the
# effective_date the document DECLARES ABOUT ITSELF — and states in the same row
# that the edition identity is read from CONTENT, "never from the filename: a
# filename is a source path, and a source path may differ across sides without
# meaning drift." This slice moves only that source path and preserves its value
# exactly, so the contracted invariant is untouched by construction.
#
# TWO THINGS IN THIS FILE ARE DELIBERATELY NOT MOVED, and both are guarded below:
#
#   83  PRIOR_CR_PATH is `Path.home()`-rooted — it points OUTSIDE the repository
#       at the 2026-06-19 edition kept for refresh verification. No provider can
#       supply it and it is not repository layout.
#   92  the `MTJ_CR_PATH` override reassigns CR_PATH and must keep running AFTER
#       the assignment above, or a CR refresh stops being verifiable as a
#       comparison. Its text and its ORDER are both asserted.
#
# No new checker was needed: `local_root_relative_constructions` and
# `root_delegating_expressions` already see this exact shape, and both arms were
# measured against a reverted source before these tests were written.

CR = EXPERIMENTS / "foundry_cr.py"

CR_FILENAME = "MTG_Comprehensive_Rules_2026-08-07_LLM.md"


def outermost_path_joins(source: str) -> list[tuple[int, str]]:
    """Every outermost `/` path chain in a module, as (lineno, source text).

    The fourth-production-change tripwire. A delegation guard counts the sites
    that DID move; this one pins how many path expressions exist at all, so a
    second expression quietly migrating — or appearing — fails here rather than
    passing every check above by not being looked at.
    """
    tree = ast.parse(source)
    joins = [n for n in ast.walk(tree)
             if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div)]
    inner = {id(d) for n in joins for d in ast.walk(n) if d is not n}
    return sorted((n.lineno, ast.unparse(n)) for n in joins if id(n) not in inner)


class TestTheFifthSliceDelegatesTheCRReadPath(unittest.TestCase):
    def test_the_one_root_delegation_is_the_cr_path(self):
        got = root_delegating_expressions(CR.read_text(encoding="utf-8"))
        self.assertEqual(len(got), 1, got)
        self.assertIn(CR_FILENAME, got[0])

    def test_no_local_root_relative_construction_remains(self):
        self.assertEqual(
            local_root_relative_constructions(CR.read_text(encoding="utf-8")), [])

    def test_the_file_gained_no_import(self):
        source = CR.read_text(encoding="utf-8")
        self.assertIn("import foundry_common as fc", source)
        self.assertEqual(source.count("import foundry_common"), 1)

    def test_the_foundry_common_symbol_surface_is_halt_plus_REPO_ROOT(self):
        """The compatibility-boundary surface this slice actually leaves behind.

        Before P0.4H the CR loader consumed exactly one `foundry_common` symbol,
        `fc.halt`. P0.4H INTENTIONALLY adds a second, `fc.REPO_ROOT` — that is
        the delegation. No new import and no new module dependency edge appears
        (`foundry_common` was already imported, and the import count is asserted
        above), but the SYMBOL surface widens from `{halt}` to
        `{halt, REPO_ROOT}`, and this test pins it at exactly that.

        Corrected by P0.4H.R1. The first version of this test asserted both
        symbols while its name and docstring described a single-symbol surface
        that the same slice's production diff visibly widened. Committed prose
        that its own assertion contradicts is the thing
        PRESERVE_TRUTH_NOT_PLUMBING forbids, so the prose moved to the truth
        rather than the assertion moving to the prose. The superseded wording is
        described here rather than reproduced, so that a grep for the mistaken
        claim finds no instance of it in the tree -- the same convention the
        house rule applies to rejected vocabulary.
        """
        tree = ast.parse(CR.read_text(encoding="utf-8"))
        used = {n.attr for n in ast.walk(tree)
                if isinstance(n, ast.Attribute)
                and isinstance(n.value, ast.Name) and n.value.id == "fc"}
        self.assertEqual(used, {"halt", "REPO_ROOT"})


class TestTheFifthSliceCheckerCatchesAReversion(unittest.TestCase):
    """NEGATIVE CONTROL. Both arms, measured against a reverted source."""

    NOW = ('CR_PATH = fc.REPO_ROOT / "docs" / '
           '"MTG_Comprehensive_Rules_2026-08-07_LLM.md"')
    BEFORE = ('CR_PATH = REPO_ROOT.parent / "docs" / '
              '"MTG_Comprehensive_Rules_2026-08-07_LLM.md"')

    def reverted(self) -> str:
        source = CR.read_text(encoding="utf-8")
        self.assertIn(self.NOW, source, "the live text moved; fix the control")
        out = source.replace(self.NOW, self.BEFORE, 1)
        self.assertNotEqual(out, source)
        return out

    def test_restoring_the_local_construction_is_caught(self):
        found = local_root_relative_constructions(self.reverted())
        self.assertEqual(len(found), 1, found)
        self.assertIn(CR_FILENAME, found[0])

    def test_reverting_also_drops_the_root_delegation(self):
        self.assertEqual(root_delegating_expressions(self.reverted()), [])

    def test_the_home_rooted_prior_edition_is_invisible_to_both_checkers(self):
        """Aimed at the code path, not at the tool's name. `PRIOR_CR_PATH` is a
        four-component path join sitting four lines below the migrated one, and
        neither checker may react to it in either direction — its base is a CALL
        (`Path.home()`), not a root NAME. Asserting this is what proves the
        controls above fired on the CR path and not on its neighbour."""
        for source in (CR.read_text(encoding="utf-8"), self.reverted()):
            joins = [u for _, u in outermost_path_joins(source)]
            self.assertTrue(any("home()" in u for u in joins), joins)
        self.assertEqual(len(local_root_relative_constructions(self.reverted())), 1)
        self.assertEqual(len(root_delegating_expressions(
            CR.read_text(encoding="utf-8"))), 1)


class TestTheFifthSliceResolvedPathIsByteIdentical(unittest.TestCase):
    """NOTE ON EXECUTION: the module is imported, never run. It contains ZERO
    write or `open` primitives, and it reaches exactly two `foundry_common`
    symbols — `fc.halt`, which it consumed before this slice, and `fc.REPO_ROOT`,
    which this slice adds. Neither is executed by importing the module."""

    @classmethod
    def setUpClass(cls):
        cls.fc = load_legacy("foundry_common")
        cls.cr = load_legacy("foundry_cr")

    def test_cr_path_equals_its_pre_change_construction(self):
        self.assertEqual(self.cr.CR_PATH,
                         self.cr.REPO_ROOT.parent / "docs" / CR_FILENAME)

    def test_cr_path_equals_the_delegated_value(self):
        self.assertEqual(self.cr.CR_PATH,
                         self.fc.REPO_ROOT / "docs" / CR_FILENAME)

    def test_cr_path_equals_the_ratified_owners_docs_directory(self):
        self.assertEqual(self.cr.CR_PATH, PATHS.legacy_docs / CR_FILENAME)

    def test_the_local_root_binding_still_resolves_as_before(self):
        """CONSUMPTION delegated, the root DECISION untouched."""
        self.assertEqual(self.cr.REPO_ROOT.parent, self.fc.REPO_ROOT)
        self.assertEqual(self.cr.REPO_ROOT, PATHS.legacy_experiments)

    def test_the_cr_file_is_the_tracked_edition_the_contract_binds(self):
        """CONSERVATION-CONTRACT.json binds CR_EDITION_CONTENT to this path on
        BOTH sides. The delegation must still land on it."""
        self.assertTrue(self.cr.CR_PATH.is_file())
        self.assertEqual(self.cr.CR_PATH.name, CR_FILENAME)


class TestTheFifthSliceChangedNothingElse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cr = load_legacy("foundry_cr")
        cls.source = CR.read_text(encoding="utf-8")

    def test_exactly_two_path_joins_exist_and_only_one_is_repository_layout(self):
        """The fourth-production-change tripwire."""
        joins = outermost_path_joins(self.source)
        self.assertEqual(len(joins), 2, joins)
        by_line = dict(joins)
        repo = [u for u in by_line.values() if "home()" not in u]
        home = [u for u in by_line.values() if "home()" in u]
        self.assertEqual(len(repo), 1, repo)
        self.assertEqual(len(home), 1, home)
        self.assertIn("fc.REPO_ROOT", repo[0])

    def test_prior_cr_path_is_untouched_and_still_home_rooted(self):
        """It points OUTSIDE the repository at the 2026-06-19 edition, so no
        provider can supply it and it is not repository layout. It is also what
        makes a CR refresh verifiable as a comparison."""
        self.assertIn('PRIOR_CR_PATH = (Path.home() / "Projects" '
                      '/ "mtjawnny.github.io" / "docs"', self.source)
        self.assertIn('/ "mtg-comprehensive-rules.md")', self.source)
        self.assertEqual(self.cr.PRIOR_CR_PATH.name, "mtg-comprehensive-rules.md")
        self.assertNotIn(PATHS.root, self.cr.PRIOR_CR_PATH.parents)

    def test_the_MTJ_CR_PATH_override_text_is_untouched(self):
        self.assertIn('if "MTJ_CR_PATH" in __import__("os").environ:', self.source)
        self.assertIn('CR_PATH = Path(__import__("os").environ["MTJ_CR_PATH"])'
                      '.expanduser()', self.source)

    def test_the_MTJ_CR_PATH_override_still_runs_AFTER_the_migrated_assignment(self):
        """ORDER, not just presence. If the override moved above the delegated
        assignment it would be silently dead, and `MTJ_CR_PATH=<file>` is the one
        mechanism that turns a CR refresh into a measurement instead of a leap."""
        tree = ast.parse(self.source)
        assign = next(n.lineno for n in tree.body
                      if isinstance(n, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == "CR_PATH"
                              for t in n.targets))
        override = next(n.lineno for n in tree.body
                        if isinstance(n, ast.If) and "MTJ_CR_PATH" in ast.unparse(n))
        self.assertLess(assign, override)

    def test_the_root_decision_and_bootstrap_survive(self):
        self.assertIn("REPO_ROOT = Path(__file__).resolve().parent\n", self.source)
        self.assertIn("sys.path.insert(0, str(REPO_ROOT))", self.source)
        self.assertEqual(self.source.count("sys.path.insert"), 1)

    def test_the_module_writes_nothing(self):
        """The runtime conservation evidence for this slice is a direct CLI run,
        because foundry_cr is not a Gate 2 row. This is the static half of that
        claim, kept as a standing guard rather than as a one-off measurement."""
        tree = ast.parse(self.source)
        primitives = {"write_text", "write_bytes", "mkdir", "touch", "unlink",
                      "rmdir", "rename", "rmtree", "copy", "copy2", "move",
                      "makedirs", "open", "dump"}
        found = []
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call):
                continue
            f = n.func
            name = (f.attr if isinstance(f, ast.Attribute)
                    else f.id if isinstance(f, ast.Name) else None)
            if name in primitives:
                found.append(f"line {n.lineno}: {name}")
        self.assertEqual(found, [])

    def test_this_module_is_not_a_gate2_row(self):
        self.assertNotIn("experiments/foundry_cr.py",
                         [a[0] for _, a, _ in gate_rows()])

    def test_the_public_surface_is_unchanged(self):
        """13 modules import this one. The constant keeps its NAME; only what it
        is built from changed."""
        for name in ("CR_PATH", "PRIOR_CR_PATH", "REPO_ROOT", "text",
                     "normalize_line", "effective_date"):
            with self.subTest(name=name):
                self.assertTrue(hasattr(self.cr, name), name)

    def test_foundry_common_is_still_not_modified(self):
        # REPAIRED BY C8.5A. This slice still added no layout statement to the
        # boundary -- that claim is unchanged and is what is asserted. The old
        # literal was superseded when C8.5A pointed the boundary at ProjectPaths.
        self.assertEqual(
            len(foundry_common_independent_layout(
                (EXPERIMENTS / "foundry_common.py").read_text(encoding="utf-8"))),
            1)

    def test_the_earlier_slices_sites_are_not_touched(self):
        """P0.4B/P0.4C/P0.4E/P0.4F keep delegating; this slice widened the guard,
        not the change."""
        self.assertEqual(
            len(delegating_expressions(GROUND_TRUTH.read_text(encoding="utf-8"))), 2)
        self.assertEqual(
            len(delegating_expressions(PROBE.read_text(encoding="utf-8"))), 1)
        self.assertEqual(
            len(root_delegating_expressions(
                REACHABILITY.read_text(encoding="utf-8"))), 2)
        self.assertEqual(
            len(root_delegating_expressions(PROBE.read_text(encoding="utf-8"))), 1)
        self.assertEqual(
            len(root_delegating_expressions(PRIOR_ART.read_text(encoding="utf-8"))),
            FOURTH_SLICE_ROOT_DELEGATIONS)

# ---------------------------------------------------------------------------
# P0.4I — the sixth slice: the ground-truth fixture directory
# ---------------------------------------------------------------------------
#
#   49  MOVES = REPO_ROOT / "moves"  ->  fc.REPO_ROOT / "experiments" / "moves"
#
# `experiments/moves/*.json` are the 534 Captain-ratified `class: human` seeds
# the ground-truth harness grades against — TRACKED evidence, not generated
# output. This slice moves the path that FINDS them and touches no seed byte.
#
# THE P0.4E CHECKER IS BLIND TO THIS SITE, AND THAT IS CORRECT.
# `local_root_relative_constructions` requires a literal TOP-LEVEL directory
# name, and `moves` is not one — it lives under `experiments/`. Measured against
# a reverted source before these tests were written: the P0.4E checker returns
# `[]` for BOTH the live and the reverted text. Reusing it would have given this
# site a negative control that could never fire, which is the P0.4F alias defect
# exactly. `TOP_LEVEL_DIRS` was deliberately NOT widened to include `moves`:
# that constant means "a top-level repository directory", it is shared by every
# prior slice's guards, and editing it to make one new control fire would change
# what those guards mean. A second checker is the honest cost.

MOVES_SUBDIR = "moves"


def local_subdir_constructions(source: str, subdir: str,
                               names=("REPO", "REPO_ROOT")) -> list[str]:
    """Path joins that reach a NESTED repository directory through a LOCAL root.

    `local_root_relative_constructions` keys on a literal TOP-LEVEL directory
    name, so it cannot see `REPO_ROOT / "moves"` — `moves` is nested under
    `experiments/`. This keys on the nested name instead, and is otherwise the
    same shape: outermost `/` chains only, the sys.path bootstrap exempt, and a
    LOCAL root variable required as the base so a delegated
    `fc.REPO_ROOT / "experiments" / "moves"` does not match.

    A checker, not an assertion, so the control below can run it against a
    deliberately reverted source and require it to FIRE.
    """
    tree = ast.parse(source)
    bootstrap = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("insert", "append")
                and isinstance(node.func.value, ast.Attribute)
                and node.func.value.attr == "path"):
            for d in ast.walk(node):
                bootstrap.add(id(d))
    joins = [n for n in ast.walk(tree)
             if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div)]
    # OUTERMOST ONLY, the same left-nesting rule every checker in this file obeys.
    inner = {id(d) for n in joins for d in ast.walk(n) if d is not n}
    found = []
    for node in [j for j in joins if id(j) not in inner and id(j) not in bootstrap]:
        base = node
        while isinstance(base, ast.BinOp) and isinstance(base.op, ast.Div):
            base = base.left
        while isinstance(base, ast.Attribute) and base.attr == "parent":
            base = base.value
        if not (isinstance(base, ast.Name) and base.id in names):
            continue
        literals = [n.value for n in ast.walk(node)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        if subdir in literals:
            found.append(f"line {node.lineno}: {ast.unparse(node)}")
    return found


def moves_uses(source: str) -> list[tuple[int, str]]:
    """Every reference to the `MOVES` name outside its own assignment.

    Used to prove the seeds are READ and never written: the fixture directory is
    tracked Captain-ratified evidence, and a slice that moved the path to it
    must not acquire the ability to touch it.
    """
    tree = ast.parse(source)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "MOVES" for t in node.targets):
            continue
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
                and node.value.id == "MOVES":
            out.append((node.lineno, node.attr))
    return sorted(out)


class TestTheSixthSliceDelegatesTheFixtureDirectory(unittest.TestCase):
    def test_the_one_root_delegation_is_the_moves_directory(self):
        got = root_delegating_expressions(GROUND_TRUTH.read_text(encoding="utf-8"))
        self.assertEqual(len(got), 1, got)
        self.assertIn("'moves'", got[0])
        self.assertIn("'experiments'", got[0])

    def test_no_local_subdir_construction_remains(self):
        self.assertEqual(
            local_subdir_constructions(
                GROUND_TRUTH.read_text(encoding="utf-8"), MOVES_SUBDIR), [])

    def test_the_file_gained_no_import(self):
        source = GROUND_TRUTH.read_text(encoding="utf-8")
        self.assertIn("import foundry_common as fc", source)
        self.assertEqual(source.count("import foundry_common"), 1)


class TestTheSixthSliceCheckerCatchesAReversion(unittest.TestCase):
    """NEGATIVE CONTROL — both arms, and the blindness of the P0.4E checker is
    ASSERTED rather than worked around."""

    NOW = 'MOVES = fc.REPO_ROOT / "experiments" / "moves"'
    BEFORE = 'MOVES = REPO_ROOT / "moves"'

    def reverted(self) -> str:
        source = GROUND_TRUTH.read_text(encoding="utf-8")
        self.assertIn(self.NOW, source, "the live text moved; fix the control")
        out = source.replace(self.NOW, self.BEFORE, 1)
        self.assertNotEqual(out, source)
        return out

    def test_restoring_the_local_construction_is_caught(self):
        """The LOCAL-OWNERSHIP arm."""
        found = local_subdir_constructions(self.reverted(), MOVES_SUBDIR)
        self.assertEqual(len(found), 1, found)

    def test_reverting_also_drops_the_root_delegation(self):
        """The DELEGATION-POSITIVE arm. Both are required: a checker that only
        counts the bad shape would pass a file that had neither."""
        self.assertEqual(root_delegating_expressions(self.reverted()), [])

    def test_the_P0_4E_checker_is_blind_here_which_is_why_this_one_exists(self):
        """Recorded, not worked around. `moves` is not a top-level repository
        directory, so `local_root_relative_constructions` returns clean on a
        FULLY reverted site — and a control that can never fire reads exactly
        like a control that passed."""
        reverted = self.reverted()
        self.assertEqual(local_root_relative_constructions(reverted), [])
        self.assertEqual(len(local_subdir_constructions(reverted, MOVES_SUBDIR)), 1)

    def test_the_TOP_LEVEL_DIRS_constant_was_not_widened_to_force_the_control(self):
        """The cheap fix would have been to add `moves` to the shared constant.
        That constant means "a top-level repository directory" and every earlier
        slice's guards read it, so widening it to make one new control fire
        would silently change what those guards assert."""
        self.assertNotIn("moves", TOP_LEVEL_DIRS)
        self.assertIn("experiments", TOP_LEVEL_DIRS)


class TestTheSixthSliceResolvedPathIsByteIdentical(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fc = load_legacy("foundry_common")
        cls.gt = load_legacy("foundry_ground_truth")

    def test_moves_equals_its_pre_change_construction(self):
        self.assertEqual(self.gt.MOVES, self.gt.REPO_ROOT / "moves")

    def test_moves_equals_the_delegated_value(self):
        self.assertEqual(self.gt.MOVES,
                         self.fc.REPO_ROOT / "experiments" / "moves")

    def test_moves_equals_the_ratified_owners_experiments_directory(self):
        self.assertEqual(self.gt.MOVES, PATHS.legacy_experiments / "moves")

    def test_the_local_root_binding_still_resolves_as_before(self):
        """CONSUMPTION delegated, the root DECISION untouched."""
        self.assertEqual(self.gt.REPO_ROOT, self.fc.REPO_ROOT / "experiments")
        self.assertEqual(self.gt.REPO_ROOT, PATHS.legacy_experiments)

    def test_the_fixture_directory_still_holds_the_tracked_seeds(self):
        """The delegation must still land on the Captain-ratified fixture. An
        empty or missing directory would make `foundry_ground_truth` halt rather
        than pass, but that is the tool's guard, not this one's."""
        self.assertTrue(self.gt.MOVES.is_dir())
        self.assertTrue(sorted(self.gt.MOVES.glob("*.json")))


class TestTheSixthSliceChangedNothingElse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gt = load_legacy("foundry_ground_truth")
        cls.source = GROUND_TRUTH.read_text(encoding="utf-8")

    def test_the_root_decision_and_bootstrap_are_untouched(self):
        self.assertIn("REPO_ROOT = Path(__file__).resolve().parent\n", self.source)
        self.assertIn("sys.path.insert(0, str(REPO_ROOT))", self.source)
        self.assertEqual(self.source.count("sys.path.insert"), 1)

    def test_the_seed_bytes_are_outside_this_slice(self):
        """`MOVES` is READ and never written. Expressed as a standing property
        rather than as a one-off diff check: every use of the name is a `glob`
        or an attribute read, so the tool cannot acquire the ability to touch
        Captain-ratified evidence without failing here."""
        self.assertEqual([attr for _, attr in moves_uses(self.source)], ["glob"])

    def test_the_only_write_in_the_module_is_the_opt_in_json_report(self):
        """Which is what makes both Gate 2 command shapes read-only. Neither
        uses `--json`, and `--update-baseline` is the only other mutating flag."""
        tree = ast.parse(self.source)
        primitives = {"write_text", "write_bytes", "mkdir", "touch", "unlink",
                      "rmdir", "rename", "rmtree", "copy", "copy2", "move",
                      "makedirs", "open"}
        found = []
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call):
                continue
            f = n.func
            name = (f.attr if isinstance(f, ast.Attribute)
                    else f.id if isinstance(f, ast.Name) else None)
            if name in primitives:
                found.append((n.lineno, name, ast.unparse(n)))
        self.assertEqual(len(found), 1, [(l, n) for l, n, _ in found])
        lineno, name, text = found[0]
        self.assertEqual(name, "write_text")
        self.assertIn("args.json", text)

    def test_the_two_covering_gate2_rows_are_unchanged(self):
        argv = {name: a for name, a, _ in gate_rows()}
        self.assertEqual(argv["ground_truth"],
                         ["experiments/foundry_ground_truth.py"])
        self.assertEqual(argv["ground_truth_wide"],
                         ["experiments/foundry_ground_truth.py", "--wide"])

    def test_neither_gate2_row_gained_a_mutating_flag(self):
        for row in ("ground_truth", "ground_truth_wide"):
            argv = {name: a for name, a, _ in gate_rows()}[row]
            with self.subTest(row=row):
                self.assertNotIn("--json", argv)
                self.assertNotIn("--update-baseline", argv)

    def test_the_first_slice_sites_in_this_file_still_delegate(self):
        """P0.4B migrated two `fc.FOUNDRY_OUT_DIR / "codebook.json"` sites in
        this same file. This slice widened the guard, not the change."""
        self.assertEqual(len(delegating_expressions(self.source)), 2)
        self.assertEqual(
            independent_foundry_out_constructions(self.source), [])

    def test_foundry_common_is_still_not_modified(self):
        # REPAIRED BY C8.5A. This slice still added no layout statement to the
        # boundary -- that claim is unchanged and is what is asserted. The old
        # literal was superseded when C8.5A pointed the boundary at ProjectPaths.
        self.assertEqual(
            len(foundry_common_independent_layout(
                (EXPERIMENTS / "foundry_common.py").read_text(encoding="utf-8"))),
            1)

    def test_the_earlier_slices_sites_are_not_touched(self):
        self.assertEqual(
            len(delegating_expressions(PROBE.read_text(encoding="utf-8"))), 1)
        self.assertEqual(
            len(root_delegating_expressions(
                REACHABILITY.read_text(encoding="utf-8"))), 2)
        self.assertEqual(
            len(root_delegating_expressions(PROBE.read_text(encoding="utf-8"))), 1)
        self.assertEqual(
            len(root_delegating_expressions(PRIOR_ART.read_text(encoding="utf-8"))),
            FOURTH_SLICE_ROOT_DELEGATIONS)
        self.assertEqual(
            len(root_delegating_expressions(CR.read_text(encoding="utf-8"))), 1)

# ---------------------------------------------------------------------------
# P0.4J — the seventh slice
# ---------------------------------------------------------------------------
#
# NO NEW CHECKER IS ADDED HERE, AND THAT IS A MEASURED RESULT.
#
# The P0.4I slice needed `local_subdir_constructions` because
# `local_root_relative_constructions` was structurally BLIND to `moves` (a
# nested directory, not a top-level one), so its negative control could never
# have fired. That blindness was measured before the tests were written, not
# assumed — and the same measurement was repeated here BEFORE writing anything,
# because the P0.4F/P0.4I finding is that a control which cannot fire reads
# exactly like a control that passed.
#
# Measured on this file, against real reverted and migrated source text:
#
#   old shape  REPO.parent / "data" / "raw" / "oracle-cards.jsonl.gz"
#       local_root_relative_constructions -> 1 hit     root_delegating -> 0
#   new shape  fc.REPO_ROOT / "data" / "raw" / "oracle-cards.jsonl.gz"
#       local_root_relative_constructions -> 0 hits    root_delegating -> 1
#
# `data` IS in TOP_LEVEL_DIRS and `.parent` climbs from `REPO` to the root, so
# the existing P0.4E checker sees this site natively. Both arms are covered by
# helpers that already exist; adding a replacement would have been duplication,
# and widening TOP_LEVEL_DIRS would have changed what every earlier slice's
# guards assert. The measurement itself is asserted below so a later reader can
# see it was taken rather than assumed.


ANCHORS_FILE = "anchors.txt"
CORPUS_FILE = "oracle-cards.jsonl.gz"


def _outermost_joins(tree: ast.AST) -> list:
    """Outermost `/` chains only — the left-nesting rule every checker here
    obeys — with the sys.path bootstrap excluded."""
    bootstrap = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("insert", "append")
                and isinstance(node.func.value, ast.Attribute)
                and node.func.value.attr == "path"):
            for d in ast.walk(node):
                bootstrap.add(id(d))
    joins = [n for n in ast.walk(tree)
             if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div)]
    inner = {id(d) for n in joins for d in ast.walk(n) if d is not n}
    return [j for j in joins if id(j) not in inner and id(j) not in bootstrap]


def local_file_constructions(source: str, filename: str,
                             names=("REPO", "REPO_ROOT")) -> list[str]:
    """Path joins that reach a repository FILE through a LOCAL root variable.

    THE THIRD CHECKER IN THIS FILE, AND IT EXISTS BECAUSE THE OTHER TWO
    TRUTHFULLY CANNOT SEE THIS SHAPE — measured before it was written, not
    assumed:

      `local_root_relative_constructions` keys on a literal TOP-LEVEL DIRECTORY
      name. `anchors.txt` is a FILE, so it returns [] for BOTH the live text and
      a fully reverted `REPO / "anchors.txt"` — a control that could never fire.

      `local_subdir_constructions` keys on a NESTED DIRECTORY name. Handed the
      string `anchors.txt` its implementation WOULD match, because it scans
      every string literal in the chain — and that is exactly why it is left
      alone. Its documented meaning is "a NESTED repository DIRECTORY", the
      P0.4I guards read it with that meaning, and quietly redefining it to
      "…or a file" is the same defect as widening TOP_LEVEL_DIRS: a constant's
      meaning changed so a new control would fire.

    So this keys on the one thing that actually distinguishes the shape — the
    FINAL component of the chain is the literal filename — which makes it a
    FILE checker rather than a third directory checker with a different list.
    """
    out = []
    for node in _outermost_joins(ast.parse(source)):
        if not (isinstance(node.right, ast.Constant)
                and node.right.value == filename):
            continue
        base = node
        while isinstance(base, ast.BinOp) and isinstance(base.op, ast.Div):
            base = base.left
        while isinstance(base, ast.Attribute) and base.attr == "parent":
            base = base.value
        if isinstance(base, ast.Name) and base.id in names:
            out.append(f"line {node.lineno}: {ast.unparse(node)}")
    return out


def root_delegated_file_constructions(source: str, filename: str) -> list[str]:
    """The delegated counterpart: `fc.REPO_ROOT / ... / <filename>`.

    Keyed on the FILE, so a per-site positive arm can name the site it means.
    `root_delegating_expressions` counts every delegation in a file, which was
    unambiguous while `foundry_wire_capability` had exactly one — it now has
    two, and a bare count can no longer say WHICH one it saw.
    """
    out = []
    for node in _outermost_joins(ast.parse(source)):
        if not (isinstance(node.right, ast.Constant)
                and node.right.value == filename):
            continue
        base = node
        while isinstance(base, ast.BinOp) and isinstance(base.op, ast.Div):
            base = base.left
        if (isinstance(base, ast.Attribute) and base.attr == "REPO_ROOT"
                and isinstance(base.value, ast.Name) and base.value.id == "fc"):
            out.append(f"line {node.lineno}: {ast.unparse(node)}")
    return out


class TestTheSeventhSliceDelegatesTheCorpusPath(unittest.TestCase):
    def test_the_corpus_path_is_a_root_delegation(self):
        """P0.4J asserted this as "the ONE root delegation" in the file, which
        was true when the file had one. P0.4K migrates ANCHORS_PATH, so the
        file now has two and a bare count can no longer say WHICH one it saw.
        Re-keyed to the CORPUS SITE: the claim P0.4J actually made about
        CARDS_PATH is unchanged and still asserted here."""
        source = WIRE_CAPABILITY.read_text(encoding="utf-8")
        got = root_delegated_file_constructions(source, CORPUS_FILE)
        self.assertEqual(len(got), 1, got)
        self.assertIn("'data'", got[0])
        self.assertIn("'raw'", got[0])
        self.assertIn("'oracle-cards.jsonl.gz'", got[0])

    def test_the_file_now_carries_exactly_two_root_delegations(self):
        """The corpus (P0.4J) and the anchors file (P0.4K). Stated so the
        superseded "exactly one" claim is replaced by a real count rather than
        quietly dropped."""
        self.assertEqual(
            len(root_delegating_expressions(
                WIRE_CAPABILITY.read_text(encoding="utf-8"))), 2)

    def test_no_local_root_relative_construction_remains(self):
        self.assertEqual(
            local_root_relative_constructions(
                WIRE_CAPABILITY.read_text(encoding="utf-8")), [])

    def test_the_file_gained_no_import(self):
        source = WIRE_CAPABILITY.read_text(encoding="utf-8")
        self.assertIn("import foundry_common as fc", source)
        self.assertEqual(source.count("import foundry_common"), 1)

    def test_the_provider_is_imported_before_the_site_that_uses_it(self):
        """A module-level constant is evaluated at import time, so `fc` must
        already be bound when line `CARDS_PATH = ...` runs. Asserted on line
        ORDER rather than on mere presence."""
        lines = WIRE_CAPABILITY.read_text(encoding="utf-8").splitlines()
        imp = next(i for i, l in enumerate(lines)
                   if l.startswith("import foundry_common as fc"))
        site = next(i for i, l in enumerate(lines) if l.startswith("CARDS_PATH"))
        self.assertLess(imp, site)


class TestTheSeventhSliceCheckerCatchesAReversion(unittest.TestCase):
    """NEGATIVE CONTROL — both arms, aimed at the existing P0.4E helpers."""

    NOW = 'CARDS_PATH = fc.REPO_ROOT / "data" / "raw" / "oracle-cards.jsonl.gz"'
    BEFORE = 'CARDS_PATH = REPO.parent / "data" / "raw" / "oracle-cards.jsonl.gz"'

    def reverted(self) -> str:
        source = WIRE_CAPABILITY.read_text(encoding="utf-8")
        self.assertIn(self.NOW, source, "the live text moved; fix the control")
        out = source.replace(self.NOW, self.BEFORE, 1)
        self.assertNotEqual(out, source)
        return out

    def test_restoring_the_local_construction_is_caught(self):
        """The LOCAL-OWNERSHIP arm."""
        found = local_root_relative_constructions(self.reverted())
        self.assertEqual(len(found), 1, found)
        self.assertIn("REPO.parent", found[0])

    def test_reverting_also_drops_the_corpus_root_delegation(self):
        """The DELEGATION-POSITIVE arm. Both are required: a checker that only
        counts the bad shape would pass a file that had neither.

        Re-keyed to the corpus FILE by P0.4K. Reverting CARDS_PATH no longer
        empties the file's delegation list — the P0.4K anchors delegation
        survives it — so a bare emptiness check would now assert the wrong
        thing, and would PASS for the wrong reason if anchors were reverted
        too."""
        reverted = self.reverted()
        self.assertEqual(
            root_delegated_file_constructions(reverted, CORPUS_FILE), [])
        self.assertEqual(
            len(root_delegated_file_constructions(reverted, ANCHORS_FILE)), 1,
            "reverting the corpus site must not disturb the anchors site")

    def test_the_existing_checkers_cover_both_arms_so_none_was_added(self):
        """The measurement that decided this slice adds no helper. Stated as a
        test so the decision is re-checked on every run rather than trusted
        from a commit message."""
        live = WIRE_CAPABILITY.read_text(encoding="utf-8")
        reverted = self.reverted()
        self.assertEqual(len(local_root_relative_constructions(reverted)), 1)
        self.assertEqual(
            len(root_delegated_file_constructions(reverted, CORPUS_FILE)), 0)
        self.assertEqual(len(local_root_relative_constructions(live)), 0)
        self.assertEqual(
            len(root_delegated_file_constructions(live, CORPUS_FILE)), 1)

    def test_the_TOP_LEVEL_DIRS_constant_was_not_widened(self):
        """`data` was ALREADY in the shared constant — this slice relies on
        that rather than editing it. Every earlier slice's guards read this
        set, so a widening here would silently change what they assert."""
        self.assertIn("data", TOP_LEVEL_DIRS)
        self.assertNotIn("raw", TOP_LEVEL_DIRS)
        self.assertNotIn("anchors.txt", TOP_LEVEL_DIRS)


class TestTheSeventhSliceResolvedPathIsByteIdentical(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fc = load_legacy("foundry_common")
        cls.wc = load_legacy("foundry_wire_capability")

    def test_cards_path_equals_its_pre_change_construction(self):
        """Against the module's OWN local root, exactly as it read before."""
        self.assertEqual(self.wc.CARDS_PATH,
                         self.wc.REPO.parent / "data" / "raw" / "oracle-cards.jsonl.gz")

    def test_cards_path_equals_the_delegated_value(self):
        self.assertEqual(self.wc.CARDS_PATH,
                         self.fc.REPO_ROOT / "data" / "raw" / "oracle-cards.jsonl.gz")

    def test_cards_path_equals_the_ratified_owners_layout(self):
        self.assertEqual(self.wc.CARDS_PATH,
                         PATHS.root / "data" / "raw" / "oracle-cards.jsonl.gz")

    def test_the_equality_holds_as_strings_too(self):
        """Path equality is normalized; string equality catches a divergence
        that compares equal but prints differently."""
        self.assertEqual(
            str(self.wc.CARDS_PATH),
            str(self.wc.REPO.parent / "data" / "raw" / "oracle-cards.jsonl.gz"))

    def test_the_local_root_binding_still_resolves_as_before(self):
        """CONSUMPTION delegated, the root DECISION untouched."""
        self.assertEqual(self.wc.REPO, self.fc.REPO_ROOT / "experiments")
        self.assertEqual(self.wc.REPO, PATHS.legacy_experiments)


class TestTheAnchorsSiteWasOutOfSliceForP0_4J_AndIsMigratedByP0_4K(unittest.TestCase):
    """BOTH TRUTHS, STATED TOGETHER.

    P0.4J deliberately left `ANCHORS_PATH = REPO / "anchors.txt"` alone — it was
    out of scope by contract — and guarded that fact, including the honest note
    that `local_root_relative_constructions` returns clean for this file whether
    or not the anchors site is delegated, because `anchors.txt` is a FILE and
    that checker keys on top-level DIRECTORY names.

    P0.4K migrates exactly that site. So P0.4J's source-text claims here are
    genuinely superseded and are rewritten rather than deleted: what P0.4J
    asserted about its OWN slice (it changed nothing here) stays true of P0.4J,
    and the class now asserts the post-P0.4K state. The path VALUE the class
    always guarded — the tracked `experiments/anchors.txt` — is unchanged and
    still asserted, which is the whole point of a value-preserving delegation.
    """

    @classmethod
    def setUpClass(cls):
        cls.fc = load_legacy("foundry_common")
        cls.wc = load_legacy("foundry_wire_capability")
        cls.source = WIRE_CAPABILITY.read_text(encoding="utf-8")

    def test_the_anchors_site_is_now_delegated(self):
        self.assertIn(
            'ANCHORS_PATH = fc.REPO_ROOT / "experiments" / "anchors.txt"',
            self.source)
        self.assertEqual(self.source.count("ANCHORS_PATH = "), 1)

    def test_the_local_construction_is_gone(self):
        self.assertNotIn('ANCHORS_PATH = REPO / "anchors.txt"', self.source)
        self.assertEqual(
            local_file_constructions(self.source, ANCHORS_FILE), [])

    def test_anchors_still_resolves_to_the_tracked_file(self):
        """Unchanged from P0.4J, and it is the assertion that makes this a
        delegation rather than a change."""
        self.assertEqual(self.wc.ANCHORS_PATH,
                         PATHS.legacy_experiments / "anchors.txt")
        self.assertTrue(self.wc.ANCHORS_PATH.is_file())

    def test_the_P0_4E_checker_is_still_blind_here_which_is_why_a_file_checker_exists(self):
        """P0.4J recorded this blindness; P0.4K is the slice that needed a
        checker because of it. Asserted on a REVERTED source so the statement
        is about the checker, not about the current text happening to be clean.
        """
        reverted = self.source.replace(
            'ANCHORS_PATH = fc.REPO_ROOT / "experiments" / "anchors.txt"',
            'ANCHORS_PATH = REPO / "anchors.txt"', 1)
        self.assertNotEqual(reverted, self.source)
        self.assertEqual(local_root_relative_constructions(reverted), [])
        self.assertEqual(len(local_file_constructions(reverted, ANCHORS_FILE)), 1)


class TestTheSeventhSliceChangedNothingElse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wc = load_legacy("foundry_wire_capability")
        cls.source = WIRE_CAPABILITY.read_text(encoding="utf-8")

    def test_the_root_decision_and_bootstrap_are_untouched(self):
        self.assertIn("REPO = Path(__file__).resolve().parent\n", self.source)
        self.assertIn("sys.path.insert(0, str(REPO))", self.source)
        self.assertEqual(self.source.count("sys.path.insert"), 1)

    def test_the_corpus_path_is_consumed_READ_ONLY(self):
        """The exact current read behaviour, asserted as the call it is:
        `gzip.open(CARDS_PATH, "rt", encoding="utf-8")`. Text-READ mode. This
        is a source-text property, not an invented semantic claim about what
        the tool means."""
        tree = ast.parse(self.source)
        opens = []
        for n in ast.walk(tree):
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr == "open"
                    and isinstance(n.func.value, ast.Name)
                    and n.func.value.id == "gzip"):
                opens.append(n)
        self.assertEqual(len(opens), 1)
        call = opens[0]
        self.assertEqual(ast.unparse(call.args[0]), "CARDS_PATH")
        self.assertEqual(call.args[1].value, "rt")

    def test_the_module_has_no_write_primitive_at_all(self):
        """Stronger than the P0.4I equivalent, and true of this module: there
        is no flag-gated report either, so the runtime command cannot mutate
        the project under any argv."""
        tree = ast.parse(self.source)
        primitives = {"write_text", "write_bytes", "mkdir", "touch", "unlink",
                      "rmdir", "rename", "rmtree", "copy", "copy2", "move",
                      "makedirs"}
        found = []
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call):
                continue
            f = n.func
            name = (f.attr if isinstance(f, ast.Attribute)
                    else f.id if isinstance(f, ast.Name) else None)
            if name in primitives:
                found.append((n.lineno, name))
        self.assertEqual(found, [])

    def test_the_public_surface_is_unchanged(self):
        """Module-level names and the CLI shape. `main()` takes no arguments
        and the module parses no argv, so there is no flag surface to move."""
        tree = ast.parse(self.source)
        funcs = [n.name for n in tree.body
                 if isinstance(n, ast.FunctionDef)]
        self.assertEqual(funcs, ["anchor_names", "name_index", "main"])
        consts = [t.id for n in tree.body if isinstance(n, ast.Assign)
                  for t in n.targets if isinstance(t, ast.Name)]
        self.assertEqual(consts, ["REPO", "CARDS_PATH", "ANCHORS_PATH"])
        self.assertNotIn("argparse", self.source)
        self.assertNotIn("sys.argv", self.source)
        self.assertEqual(
            [a.arg for a in
             next(n for n in tree.body
                  if isinstance(n, ast.FunctionDef) and n.name == "main").args.args],
            [])

    def test_the_migrated_constant_is_actually_consumed(self):
        """A delegation that nothing reads would be untestable at runtime. The
        name is used exactly once outside its own assignment, in the gzip read
        that builds the name index."""
        tree = ast.parse(self.source)
        uses = [n.lineno for n in ast.walk(tree)
                if isinstance(n, ast.Name) and n.id == "CARDS_PATH"
                and isinstance(n.ctx, ast.Load)]
        self.assertEqual(len(uses), 1)

    def test_no_gate2_row_covers_this_module(self):
        """Recorded so the runtime evidence is read for what it is: this file
        is exercised by its own direct command, not by a Gate 2 row. A later
        slice must not assume gate coverage it never had."""
        for name, argv, _ in gate_rows():
            self.assertNotIn("experiments/foundry_wire_capability.py", argv)

    def test_foundry_common_is_still_not_modified(self):
        # REPAIRED BY C8.5A. This slice still added no layout statement to the
        # boundary -- that claim is unchanged and is what is asserted. The old
        # literal was superseded when C8.5A pointed the boundary at ProjectPaths.
        self.assertEqual(
            len(foundry_common_independent_layout(
                (EXPERIMENTS / "foundry_common.py").read_text(encoding="utf-8"))),
            1)

    def test_the_earlier_slices_sites_are_not_touched(self):
        self.assertEqual(
            len(delegating_expressions(PROBE.read_text(encoding="utf-8"))), 1)
        self.assertEqual(
            len(root_delegating_expressions(
                REACHABILITY.read_text(encoding="utf-8"))), 2)
        self.assertEqual(
            len(root_delegating_expressions(PROBE.read_text(encoding="utf-8"))), 1)
        self.assertEqual(
            len(root_delegating_expressions(PRIOR_ART.read_text(encoding="utf-8"))),
            FOURTH_SLICE_ROOT_DELEGATIONS)
        self.assertEqual(
            len(root_delegating_expressions(CR.read_text(encoding="utf-8"))), 1)
        self.assertEqual(
            len(root_delegating_expressions(
                GROUND_TRUTH.read_text(encoding="utf-8"))), 1)

    def test_the_sibling_wire_experiment_file_is_a_different_file(self):
        """`WIRE` (P0.4C) and `WIRE_CAPABILITY` (this slice) have confusable
        names. Asserted so a later edit cannot silently retarget one at the
        other."""
        self.assertNotEqual(WIRE, WIRE_CAPABILITY)
        self.assertEqual(len(delegating_expressions(
            WIRE.read_text(encoding="utf-8"), "codebook.json")), 1)


# ---------------------------------------------------------------------------
# P0.4K — the eighth slice
# ---------------------------------------------------------------------------
#
# The second and LAST layout consumption in `foundry_wire_capability.py`:
#
#     ANCHORS_PATH = REPO / "anchors.txt"
#         ->         fc.REPO_ROOT / "experiments" / "anchors.txt"
#
# WHICH HELPERS SEE THIS SHAPE — MEASURED BEFORE ANY TEST WAS WRITTEN:
#
#   local_root_relative_constructions   BLIND  (keys on TOP-LEVEL dir names;
#                                              returns [] for live AND reverted)
#   local_subdir_constructions          would match if handed "anchors.txt",
#                                       but its documented meaning is a NESTED
#                                       DIRECTORY and the P0.4I guards read it
#                                       that way — NOT repurposed
#   root_delegating_expressions         sees the NEW shape, but counts BOTH
#                                       sites in this file, so it cannot serve
#                                       as an anchors-SPECIFIC positive arm
#
# So the ownership arm had no truthful existing checker, and the positive arm
# had no site-specific one. `local_file_constructions` and
# `root_delegated_file_constructions` are the smallest pair that fixes exactly
# that, keyed on the FINAL path component being a literal filename. Neither
# TOP_LEVEL_DIRS nor any earlier helper's meaning was touched.


class TestTheEighthSliceDelegatesTheAnchorsFile(unittest.TestCase):
    def test_the_anchors_delegation_is_present_and_singular(self):
        got = root_delegated_file_constructions(
            WIRE_CAPABILITY.read_text(encoding="utf-8"), ANCHORS_FILE)
        self.assertEqual(len(got), 1, got)
        self.assertIn("'experiments'", got[0])
        self.assertIn("'anchors.txt'", got[0])

    def test_no_local_file_construction_remains(self):
        self.assertEqual(
            local_file_constructions(
                WIRE_CAPABILITY.read_text(encoding="utf-8"), ANCHORS_FILE), [])

    def test_the_file_gained_no_import(self):
        source = WIRE_CAPABILITY.read_text(encoding="utf-8")
        self.assertIn("import foundry_common as fc", source)
        self.assertEqual(source.count("import foundry_common"), 1)

    def test_the_provider_is_imported_before_the_site_that_uses_it(self):
        lines = WIRE_CAPABILITY.read_text(encoding="utf-8").splitlines()
        imp = next(i for i, l in enumerate(lines)
                   if l.startswith("import foundry_common as fc"))
        site = next(i for i, l in enumerate(lines) if l.startswith("ANCHORS_PATH"))
        self.assertLess(imp, site)


class TestTheEighthSliceCheckerCatchesAReversion(unittest.TestCase):
    """NEGATIVE CONTROL — both arms, aimed at the code path, not the name."""

    NOW = 'ANCHORS_PATH = fc.REPO_ROOT / "experiments" / "anchors.txt"'
    BEFORE = 'ANCHORS_PATH = REPO / "anchors.txt"'

    def reverted(self) -> str:
        source = WIRE_CAPABILITY.read_text(encoding="utf-8")
        self.assertIn(self.NOW, source, "the live text moved; fix the control")
        out = source.replace(self.NOW, self.BEFORE, 1)
        self.assertNotEqual(out, source)
        return out

    def test_restoring_the_local_construction_is_caught(self):
        """The LOCAL-OWNERSHIP arm."""
        found = local_file_constructions(self.reverted(), ANCHORS_FILE)
        self.assertEqual(len(found), 1, found)
        self.assertIn("REPO / 'anchors.txt'", found[0])

    def test_reverting_also_drops_the_anchors_delegation(self):
        """The DELEGATION-POSITIVE arm, keyed to the anchors FILE so it cannot
        be satisfied by the P0.4J corpus delegation sitting one line above."""
        reverted = self.reverted()
        self.assertEqual(
            root_delegated_file_constructions(reverted, ANCHORS_FILE), [])
        self.assertEqual(
            len(root_delegated_file_constructions(reverted, CORPUS_FILE)), 1,
            "reverting the anchors site must not disturb the corpus site")

    def test_the_new_checker_was_needed_because_the_old_ones_are_not_truthful_here(self):
        """The measurement that justified adding a helper, re-checked on every
        run rather than trusted from a commit message."""
        live = WIRE_CAPABILITY.read_text(encoding="utf-8")
        reverted = self.reverted()
        # the P0.4E checker cannot tell the two states apart at all
        self.assertEqual(local_root_relative_constructions(live), [])
        self.assertEqual(local_root_relative_constructions(reverted), [])
        # the new one can
        self.assertEqual(len(local_file_constructions(reverted, ANCHORS_FILE)), 1)
        self.assertEqual(len(local_file_constructions(live, ANCHORS_FILE)), 0)

    def test_TOP_LEVEL_DIRS_was_not_widened_and_holds_no_filename(self):
        self.assertNotIn("anchors.txt", TOP_LEVEL_DIRS)
        self.assertNotIn("oracle-cards.jsonl.gz", TOP_LEVEL_DIRS)
        self.assertIn("experiments", TOP_LEVEL_DIRS)
        self.assertIn("data", TOP_LEVEL_DIRS)

    def test_local_subdir_constructions_keeps_its_nested_directory_meaning(self):
        """It was NOT repurposed as a file checker. Its P0.4I meaning is that a
        NESTED DIRECTORY is reached through a local root; `moves` still is and
        this file still has none."""
        self.assertEqual(
            local_subdir_constructions(
                WIRE_CAPABILITY.read_text(encoding="utf-8"), MOVES_SUBDIR), [])
        self.assertEqual(
            len(local_subdir_constructions(
                GROUND_TRUTH.read_text(encoding="utf-8"), MOVES_SUBDIR)), 0)


class TestTheEighthSliceResolvedPathIsByteIdentical(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fc = load_legacy("foundry_common")
        cls.wc = load_legacy("foundry_wire_capability")

    def test_anchors_equals_its_pre_change_construction(self):
        self.assertEqual(self.wc.ANCHORS_PATH, self.wc.REPO / "anchors.txt")

    def test_anchors_equals_the_delegated_value(self):
        self.assertEqual(self.wc.ANCHORS_PATH,
                         self.fc.REPO_ROOT / "experiments" / "anchors.txt")

    def test_anchors_equals_the_ratified_owners_layout(self):
        self.assertEqual(self.wc.ANCHORS_PATH,
                         PATHS.legacy_experiments / "anchors.txt")

    def test_the_equality_holds_as_strings_too(self):
        self.assertEqual(str(self.wc.ANCHORS_PATH),
                         str(self.wc.REPO / "anchors.txt"))

    def test_the_local_root_binding_still_resolves_as_before(self):
        self.assertEqual(self.wc.REPO, self.fc.REPO_ROOT / "experiments")
        self.assertEqual(self.wc.REPO, PATHS.legacy_experiments)


class TestTheEighthSliceLeftTheTrackedAnchorsFileAlone(unittest.TestCase):
    """`experiments/anchors.txt` is a DENY path. The delegation must move the
    expression, never the evidence it points at."""

    @classmethod
    def setUpClass(cls):
        cls.wc = load_legacy("foundry_wire_capability")

    def test_the_anchors_file_is_tracked(self):
        self.assertTrue((PATHS.legacy_experiments / "anchors.txt").is_file())

    def test_the_anchors_file_still_yields_its_names(self):
        """A delegation that silently pointed somewhere empty would make
        `anchor_names()` halt, not fail quietly — but the tool's guard is not
        this one's, so the content is asserted here directly."""
        names = [l.strip() for l
                 in self.wc.ANCHORS_PATH.read_text(encoding="utf-8").splitlines()
                 if l.strip() and not l.strip().startswith("#")]
        self.assertEqual(len(names), 9)
        self.assertIn("Sol Ring", names)

    def test_anchors_is_acquired_by_a_READ_and_never_by_a_write(self):
        """The only primitive applied to the name is `read_text`. Asserted as
        the attribute access it is, so the module cannot acquire the ability to
        write over Captain-tracked anchors without failing here."""
        tree = ast.parse(WIRE_CAPABILITY.read_text(encoding="utf-8"))
        attrs = sorted(
            n.attr for n in ast.walk(tree)
            if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
            and n.value.id == "ANCHORS_PATH")
        self.assertEqual(attrs, ["read_text"])


class TestTheEighthSliceChangedNothingElse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wc = load_legacy("foundry_wire_capability")
        cls.source = WIRE_CAPABILITY.read_text(encoding="utf-8")

    def test_the_P0_4J_corpus_delegation_is_untouched(self):
        self.assertIn(
            'CARDS_PATH = fc.REPO_ROOT / "data" / "raw" / "oracle-cards.jsonl.gz"',
            self.source)
        self.assertEqual(
            len(root_delegated_file_constructions(self.source, CORPUS_FILE)), 1)

    def test_the_P0_4J_read_mode_guard_is_still_truthful(self):
        """P0.4J asserted the corpus is opened `"rt"`. Re-asserted here so this
        slice cannot be the one that quietly invalidates it."""
        tree = ast.parse(self.source)
        opens = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                 and n.func.attr == "open"
                 and isinstance(n.func.value, ast.Name)
                 and n.func.value.id == "gzip"]
        self.assertEqual(len(opens), 1)
        self.assertEqual(ast.unparse(opens[0].args[0]), "CARDS_PATH")
        self.assertEqual(opens[0].args[1].value, "rt")

    def test_the_root_decision_and_bootstrap_are_untouched(self):
        self.assertIn("REPO = Path(__file__).resolve().parent\n", self.source)
        self.assertIn("sys.path.insert(0, str(REPO))", self.source)
        self.assertEqual(self.source.count("sys.path.insert"), 1)

    def test_the_module_still_has_no_write_primitive_at_all(self):
        tree = ast.parse(self.source)
        primitives = {"write_text", "write_bytes", "mkdir", "touch", "unlink",
                      "rmdir", "rename", "rmtree", "copy", "copy2", "move",
                      "makedirs"}
        found = [(n.lineno, n.func.attr if isinstance(n.func, ast.Attribute)
                  else n.func.id)
                 for n in ast.walk(tree) if isinstance(n, ast.Call)
                 and (isinstance(n.func, ast.Attribute) or isinstance(n.func, ast.Name))
                 and (n.func.attr if isinstance(n.func, ast.Attribute)
                      else n.func.id) in primitives]
        self.assertEqual(found, [])

    def test_the_public_surface_is_unchanged(self):
        tree = ast.parse(self.source)
        self.assertEqual(
            [n.name for n in tree.body if isinstance(n, ast.FunctionDef)],
            ["anchor_names", "name_index", "main"])
        self.assertEqual(
            [t.id for n in tree.body if isinstance(n, ast.Assign)
             for t in n.targets if isinstance(t, ast.Name)],
            ["REPO", "CARDS_PATH", "ANCHORS_PATH"])
        self.assertNotIn("argparse", self.source)
        self.assertNotIn("sys.argv", self.source)

    def test_no_gate2_row_covers_this_module(self):
        for _name, argv, _ in gate_rows():
            self.assertNotIn("experiments/foundry_wire_capability.py", argv)

    def test_foundry_common_is_still_not_modified(self):
        # REPAIRED BY C8.5A. This slice still added no layout statement to the
        # boundary -- that claim is unchanged and is what is asserted. The old
        # literal was superseded when C8.5A pointed the boundary at ProjectPaths.
        self.assertEqual(
            len(foundry_common_independent_layout(
                (EXPERIMENTS / "foundry_common.py").read_text(encoding="utf-8"))),
            1)

    def test_the_earlier_slices_sites_are_not_touched(self):
        self.assertEqual(
            len(delegating_expressions(PROBE.read_text(encoding="utf-8"))), 1)
        self.assertEqual(
            len(root_delegating_expressions(
                REACHABILITY.read_text(encoding="utf-8"))), 2)
        self.assertEqual(
            len(root_delegating_expressions(PROBE.read_text(encoding="utf-8"))), 1)
        self.assertEqual(
            len(root_delegating_expressions(PRIOR_ART.read_text(encoding="utf-8"))),
            FOURTH_SLICE_ROOT_DELEGATIONS)
        self.assertEqual(
            len(root_delegating_expressions(CR.read_text(encoding="utf-8"))), 1)
        self.assertEqual(
            len(root_delegating_expressions(
                GROUND_TRUTH.read_text(encoding="utf-8"))), 1)

    def test_this_file_is_now_fully_delegated_and_that_is_asserted_positively(self):
        """With both sites migrated the module states no repository layout of
        its own beyond its root DECISION. Asserted with the FILE checker, not
        with the directory checker whose silence here means nothing."""
        self.assertEqual(local_file_constructions(self.source, ANCHORS_FILE), [])
        self.assertEqual(local_file_constructions(self.source, CORPUS_FILE), [])
        self.assertEqual(local_root_relative_constructions(self.source), [])
        self.assertEqual(
            len(root_delegating_expressions(self.source)), 2)


# ---------------------------------------------------------------------------
# P0.4M — the ninth slice
# ---------------------------------------------------------------------------
#
#     experiments/foundry_slug_reparse.py:50
#       GRAMMAR = REPO_ROOT.parent / "docs" / "CODEBOOK-NAMING-GRAMMAR.md"
#           ->    fc.REPO_ROOT / "docs" / "CODEBOOK-NAMING-GRAMMAR.md"
#
# C7.4 BOUNDARY, STATED SO IT CANNOT BE STRETCHED LATER: the value is a binding
# RULING document, and C7.4 preserves "ruling ids/content/provenance, NOT old
# document paths" — the same clause shape that authorized the CR read-path
# migration in P0.4H under C7.5. This slice moves the EXPRESSION that computes
# the path and nothing else: the document's bytes, ids, content and provenance
# are untouched and asserted so. It is NOT precedent for touching generated
# artifacts, authority selectors, known-debt controls, write targets, or peer
# providers.
#
# HELPER COVERAGE WAS MEASURED FIRST, ON REAL OLD/NEW SOURCE, BEFORE ANY TEST
# WAS WRITTEN — the P0.4L.R1 prediction was NOT assumed:
#
#   local_root_relative_constructions    1 -> 0   (ownership, shared helper)
#   root_delegating_expressions          0 -> 1   (delegation, shared helper)
#   local_file_constructions(GRAMMAR)    1 -> 0   (ownership, GRAMMAR-SPECIFIC)
#   root_delegated_file_constructions    0 -> 1   (delegation, GRAMMAR-SPECIFIC)
#
# `docs` is already in TOP_LEVEL_DIRS, so the shared P0.4E pair sees this site
# natively, and the P0.4K filename-keyed pair supplies the site-specific arms
# the task requires. NO new checker was added and NO shared helper or constant
# was widened.

GRAMMAR_FILE = "CODEBOOK-NAMING-GRAMMAR.md"


class TestTheNinthSliceDelegatesTheGrammarReadPath(unittest.TestCase):
    def test_the_grammar_delegation_is_present_and_singular(self):
        got = root_delegated_file_constructions(
            SLUG_REPARSE.read_text(encoding="utf-8"), GRAMMAR_FILE)
        self.assertEqual(len(got), 1, got)
        self.assertIn("'docs'", got[0])

    def test_no_local_construction_remains_on_either_checker(self):
        source = SLUG_REPARSE.read_text(encoding="utf-8")
        self.assertEqual(local_root_relative_constructions(source), [])
        self.assertEqual(local_file_constructions(source, GRAMMAR_FILE), [])

    def test_the_file_gained_no_import(self):
        source = SLUG_REPARSE.read_text(encoding="utf-8")
        self.assertIn("import foundry_common as fc", source)
        self.assertEqual(source.count("import foundry_common"), 1)

    def test_the_provider_is_imported_before_the_site_that_uses_it(self):
        lines = SLUG_REPARSE.read_text(encoding="utf-8").splitlines()
        imp = next(i for i, l in enumerate(lines)
                   if l.startswith("import foundry_common as fc"))
        site = next(i for i, l in enumerate(lines) if l.startswith("GRAMMAR"))
        self.assertLess(imp, site)

    def test_no_peer_provider_was_introduced(self):
        """`foundry_shape_extractor` is imported as `fx` and exports its OWN
        GRAMMAR constant, which would have been an exact-match peer provider.
        It was NOT used: the delegation goes directly to the ratified
        compatibility boundary."""
        source = SLUG_REPARSE.read_text(encoding="utf-8")
        self.assertNotIn("fx.GRAMMAR", source)
        self.assertNotIn("p.GRAMMAR", source)


class TestTheNinthSliceCheckerCatchesAReversion(unittest.TestCase):
    NOW = 'GRAMMAR = fc.REPO_ROOT / "docs" / "CODEBOOK-NAMING-GRAMMAR.md"'
    BEFORE = 'GRAMMAR = REPO_ROOT.parent / "docs" / "CODEBOOK-NAMING-GRAMMAR.md"'

    def reverted(self) -> str:
        source = SLUG_REPARSE.read_text(encoding="utf-8")
        self.assertIn(self.NOW, source, "the live text moved; fix the control")
        out = source.replace(self.NOW, self.BEFORE, 1)
        self.assertNotEqual(out, source)
        return out

    def test_restoring_the_local_construction_is_caught(self):
        """The LOCAL-OWNERSHIP arm, on both checkers that see this shape."""
        reverted = self.reverted()
        self.assertEqual(len(local_root_relative_constructions(reverted)), 1)
        self.assertEqual(len(local_file_constructions(reverted, GRAMMAR_FILE)), 1)

    def test_reverting_also_drops_the_grammar_delegation(self):
        """The GRAMMAR-SPECIFIC delegation-positive arm. Keyed on the filename
        so it cannot be satisfied by the P0.4C `codebook.json` delegation
        sitting on the very next line."""
        reverted = self.reverted()
        self.assertEqual(
            root_delegated_file_constructions(reverted, GRAMMAR_FILE), [])
        self.assertEqual(
            len(delegating_expressions(reverted, "codebook.json")), 1,
            "reverting GRAMMAR must not disturb the P0.4C CODEBOOK delegation")

    def test_the_measured_helper_coverage_is_what_decided_no_new_checker(self):
        """Re-checked every run rather than trusted from a commit message."""
        live, reverted = SLUG_REPARSE.read_text(encoding="utf-8"), self.reverted()
        self.assertEqual(len(local_root_relative_constructions(reverted)), 1)
        self.assertEqual(len(root_delegated_file_constructions(reverted, GRAMMAR_FILE)), 0)
        self.assertEqual(len(local_root_relative_constructions(live)), 0)
        self.assertEqual(len(root_delegated_file_constructions(live, GRAMMAR_FILE)), 1)

    def test_no_shared_helper_constant_was_widened(self):
        self.assertIn("docs", TOP_LEVEL_DIRS)
        self.assertNotIn(GRAMMAR_FILE, TOP_LEVEL_DIRS)
        self.assertNotIn("codebook.json", TOP_LEVEL_DIRS)


class TestTheNinthSliceResolvedPathIsByteIdentical(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fc = load_legacy("foundry_common")
        cls.sr = load_legacy("foundry_slug_reparse")

    def test_grammar_equals_its_pre_change_construction(self):
        self.assertEqual(self.sr.GRAMMAR,
                         self.sr.REPO_ROOT.parent / "docs" / GRAMMAR_FILE)

    def test_grammar_equals_the_delegated_value(self):
        self.assertEqual(self.sr.GRAMMAR,
                         self.fc.REPO_ROOT / "docs" / GRAMMAR_FILE)

    def test_grammar_equals_the_ratified_owners_legacy_docs_path(self):
        self.assertEqual(self.sr.GRAMMAR, PATHS.legacy_docs / GRAMMAR_FILE)

    def test_the_equality_holds_as_strings_too(self):
        self.assertEqual(str(self.sr.GRAMMAR),
                         str(self.sr.REPO_ROOT.parent / "docs" / GRAMMAR_FILE))
        self.assertEqual(str(self.sr.GRAMMAR), str(PATHS.legacy_docs / GRAMMAR_FILE))

    def test_the_local_root_binding_still_resolves_as_before(self):
        """CONSUMPTION delegated, the root DECISION untouched."""
        self.assertEqual(self.sr.REPO_ROOT, self.fc.REPO_ROOT / "experiments")
        self.assertEqual(self.sr.REPO_ROOT, PATHS.legacy_experiments)


class TestTheNinthSliceLeftTheRulingDocumentAlone(unittest.TestCase):
    """C7.4: the PATH is plumbing, the DOCUMENT is truth. This class guards the
    truth half."""

    @classmethod
    def setUpClass(cls):
        cls.sr = load_legacy("foundry_slug_reparse")

    def test_the_grammar_document_is_tracked_and_present(self):
        self.assertTrue((PATHS.legacy_docs / GRAMMAR_FILE).is_file())
        self.assertEqual(self.sr.GRAMMAR, PATHS.legacy_docs / GRAMMAR_FILE)

    def test_the_grammar_document_still_carries_the_sections_this_probe_reads(self):
        """Content, not cardinality: the five sections `section_tokens` is
        called with must each still be present, or the probe would halt."""
        text = (PATHS.legacy_docs / GRAMMAR_FILE).read_text(encoding="utf-8")
        for num in ("3", "4", "5", "6", "8"):
            with self.subTest(section=num):
                self.assertRegex(text, rf"(?m)^## {num}\.")

    def test_grammar_is_acquired_by_a_READ_and_never_by_a_write(self):
        """The only primitive applied to the name is `read_text`."""
        tree = ast.parse(SLUG_REPARSE.read_text(encoding="utf-8"))
        attrs = sorted(n.attr for n in ast.walk(tree)
                       if isinstance(n, ast.Attribute)
                       and isinstance(n.value, ast.Name)
                       and n.value.id == "GRAMMAR")
        self.assertEqual(attrs, ["read_text"])

    def test_the_read_feeds_section_parsing(self):
        """`text = GRAMMAR.read_text(...)` is what every `section_tokens` call
        consumes, so the migrated constant is load-bearing for the printed
        vocabulary rather than merely present."""
        source = SLUG_REPARSE.read_text(encoding="utf-8")
        self.assertIn('text = GRAMMAR.read_text(encoding="utf-8")', source)
        self.assertEqual(source.count("section_tokens(text,"), 5)


class TestTheNinthSliceChangedNothingElse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fc = load_legacy("foundry_common")
        cls.sr = load_legacy("foundry_slug_reparse")
        cls.source = SLUG_REPARSE.read_text(encoding="utf-8")

    def test_the_P0_4C_codebook_delegation_is_untouched(self):
        self.assertIn('CODEBOOK = fc.FOUNDRY_OUT_DIR / "codebook.json"', self.source)
        self.assertEqual(self.sr.CODEBOOK, PATHS.legacy_foundry_out / "codebook.json")
        self.assertEqual(len(delegating_expressions(self.source, "codebook.json")), 1)

    def test_the_root_decision_and_bootstrap_are_untouched(self):
        self.assertIn("REPO_ROOT = Path(__file__).resolve().parent\n", self.source)
        self.assertIn("sys.path.insert(0, str(REPO_ROOT))", self.source)
        self.assertEqual(self.source.count("sys.path.insert"), 1)

    def test_the_one_write_primitive_stays_flag_gated(self):
        """`Path(args.json).write_text(...)` must remain inside `if args.json:`,
        and `--json` must keep NO default — that pair is what makes the bare
        command's read-only conservation evidence valid."""
        tree = ast.parse(self.source)
        writes = [n for n in ast.walk(tree)
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                  and n.func.attr == "write_text"]
        self.assertEqual(len(writes), 1)
        gated = [n for n in ast.walk(tree)
                 if isinstance(n, ast.If) and ast.unparse(n.test) == "args.json"
                 and any(w is d for d in ast.walk(n) for w in writes)]
        self.assertEqual(len(gated), 1, "the only write is no longer gated on args.json")
        json_arg = [n for n in ast.walk(tree)
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr == "add_argument"
                    and any(isinstance(a, ast.Constant) and a.value == "--json"
                            for a in n.args)]
        self.assertEqual(len(json_arg), 1)
        self.assertEqual([k.arg for k in json_arg[0].keywords], [],
                         "--json gained a default; bare execution could now write")

    def test_the_module_has_no_other_write_primitive(self):
        tree = ast.parse(self.source)
        primitives = {"write_bytes", "mkdir", "touch", "unlink", "rmdir",
                      "rename", "rmtree", "copy", "copy2", "move", "makedirs",
                      "write_json"}
        found = [(n.lineno, n.func.attr) for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                 and n.func.attr in primitives]
        self.assertEqual(found, [])

    def test_the_public_and_CLI_surface_is_unchanged(self):
        tree = ast.parse(self.source)
        self.assertEqual(
            [t.id for n in tree.body if isinstance(n, ast.Assign)
             for t in n.targets if isinstance(t, ast.Name)],
            ["REPO_ROOT", "GRAMMAR", "CODEBOOK"])
        flags = [a.value for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                 and n.func.attr == "add_argument"
                 for a in n.args if isinstance(a, ast.Constant)]
        self.assertEqual(flags, ["--show-unknown", "--show-ambiguous", "--json"])

    def test_no_gate2_row_covers_this_module(self):
        """Measured, not assumed: the runtime evidence for this slice is the
        direct bare command, and a later slice must not inherit a coverage
        claim this file never had."""
        for _name, argv, _ in gate_rows():
            self.assertNotIn("experiments/foundry_slug_reparse.py", argv)

    def test_the_sibling_grammar_site_was_out_of_slice_for_P0_4M_and_is_migrated_by_P0_4N(self):
        """`foundry_shape_extractor.py:52` held the SAME expression and was
        explicitly deny-listed for P0.4M, asserted so THAT slice could not
        quietly become two. P0.4M's scope claim is still true and is restated
        here as the thing it always was — a SCOPE boundary, never a permanent
        prohibition — and the site is now migrated by P0.4N.

        The original guard's live claim ("the old text is still there") is
        genuinely superseded. Its MEANING is kept: the sibling that must not
        move with it is now `CR_CHECKS` on the next line, and P0.4N asserts
        that directly. What survives unchanged here is the P0.4M fact that
        matters — this file's own GRAMMAR delegation is still singular and
        still the only one this slice produced."""
        sibling = (EXPERIMENTS / "foundry_shape_extractor.py").read_text(encoding="utf-8")
        self.assertNotIn('GRAMMAR = REPO_ROOT.parent / "docs" / '
                         '"CODEBOOK-NAMING-GRAMMAR.md"', sibling)
        self.assertIn('GRAMMAR = fc.REPO_ROOT / "docs" / '
                      '"CODEBOOK-NAMING-GRAMMAR.md"', sibling)
        self.assertEqual(
            len(root_delegated_file_constructions(self.source, GRAMMAR_FILE)), 1)

    def test_foundry_common_is_still_not_modified(self):
        # REPAIRED BY C8.5A. This slice still added no layout statement to the
        # boundary -- that claim is unchanged and is what is asserted. The old
        # literal was superseded when C8.5A pointed the boundary at ProjectPaths.
        self.assertEqual(
            len(foundry_common_independent_layout(
                (EXPERIMENTS / "foundry_common.py").read_text(encoding="utf-8"))),
            1)

    def test_the_earlier_slices_sites_are_not_touched(self):
        self.assertEqual(
            len(delegating_expressions(PROBE.read_text(encoding="utf-8"))), 1)
        self.assertEqual(
            len(root_delegating_expressions(REACHABILITY.read_text(encoding="utf-8"))), 2)
        self.assertEqual(
            len(root_delegating_expressions(PROBE.read_text(encoding="utf-8"))), 1)
        self.assertEqual(
            len(root_delegating_expressions(PRIOR_ART.read_text(encoding="utf-8"))),
            FOURTH_SLICE_ROOT_DELEGATIONS)
        self.assertEqual(
            len(root_delegating_expressions(CR.read_text(encoding="utf-8"))), 1)
        self.assertEqual(
            len(root_delegating_expressions(GROUND_TRUTH.read_text(encoding="utf-8"))), 1)
        self.assertEqual(
            len(root_delegating_expressions(
                WIRE_CAPABILITY.read_text(encoding="utf-8"))), 2)


# ---------------------------------------------------------------------------
# P0.4N — the tenth slice
# ---------------------------------------------------------------------------
#
#     experiments/foundry_shape_extractor.py:52
#       GRAMMAR = REPO_ROOT.parent / "docs" / "CODEBOOK-NAMING-GRAMMAR.md"
#           ->    fc.REPO_ROOT / "docs" / "CODEBOOK-NAMING-GRAMMAR.md"
#
# Same clause, same document and same provider as P0.4M, one file over. C7.4
# preserves "ruling ids/content/provenance, NOT old document paths"; this slice
# moves the EXPRESSION and nothing else. It is NOT precedent for generated
# artifacts, authority selectors, known-debt controls, write targets or peer
# providers — and the generated-artifact case is not hypothetical here, because
# `CR_CHECKS` (line 53) reads `docs/cr-checks.json`, sits one line below, and is
# DELIBERATELY LEFT LOCAL. Its survival is asserted below.
#
# WHAT IS DIFFERENT FROM P0.4M, AND IT MATTERS FOR THE OWNERSHIP ARM:
# this module has TWO local `REPO_ROOT.parent / "docs" / ...` sites, so the
# shared ownership checker goes 2 -> 1, not 1 -> 0. A test that asserted `== []`
# here would be asserting that the deliberately-out-of-scope sibling had ALSO
# moved. The residual is named explicitly instead.
#
# HELPER COVERAGE WAS MEASURED FIRST, ON REAL OLD/NEW SOURCE, BEFORE ANY TEST
# WAS WRITTEN — the task's preferred candidate was re-derived, not assumed:
#
#   local_root_relative_constructions       2 -> 1   (residual = CR_CHECKS)
#   root_delegating_expressions             0 -> 1
#   local_file_constructions(GRAMMAR)       1 -> 0   (GRAMMAR-SPECIFIC)
#   root_delegated_file_constructions       0 -> 1   (GRAMMAR-SPECIFIC)
#   local_file_constructions("cr-checks.json") 1 -> 1  (unmoved, by design)
#
# NO new checker was added and NO shared helper or constant was widened.
#
# FAN-IN: 19 importers, the largest of any slice in this arc, and three of them
# are PAUSED AQ4 benchmark modules. The change is value-preserving — proved as
# Path AND str against the pre-change construction, `fc.REPO_ROOT` and
# `ProjectPaths.legacy_docs` — so the blast radius is zero by construction. No
# AQ4 file is touched, and no production module reads `fx.GRAMMAR` as an
# attribute at all; that is asserted rather than assumed.

SHAPE_EXTRACTOR = EXPERIMENTS / "foundry_shape_extractor.py"
CR_CHECKS_FILE = "cr-checks.json"


class TestTheTenthSliceDelegatesTheGrammarReadPath(unittest.TestCase):
    def test_the_grammar_delegation_is_present_and_singular(self):
        got = root_delegated_file_constructions(
            SHAPE_EXTRACTOR.read_text(encoding="utf-8"), GRAMMAR_FILE)
        self.assertEqual(len(got), 1, got)
        self.assertIn("'docs'", got[0])

    def test_no_local_grammar_construction_remains(self):
        source = SHAPE_EXTRACTOR.read_text(encoding="utf-8")
        self.assertEqual(local_file_constructions(source, GRAMMAR_FILE), [])

    def test_the_ownership_residual_is_exactly_the_out_of_scope_sibling(self):
        """The shared checker goes 2 -> 1 here, not 2 -> 0. Asserting `== []`
        would silently demand that CR_CHECKS moved too."""
        got = local_root_relative_constructions(
            SHAPE_EXTRACTOR.read_text(encoding="utf-8"))
        self.assertEqual(len(got), 1, got)
        self.assertIn(CR_CHECKS_FILE, got[0])

    def test_the_file_gained_no_import(self):
        source = SHAPE_EXTRACTOR.read_text(encoding="utf-8")
        self.assertIn("import foundry_common as fc", source)
        self.assertEqual(source.count("import foundry_common"), 1)

    def test_the_provider_is_imported_before_the_site_that_uses_it(self):
        lines = SHAPE_EXTRACTOR.read_text(encoding="utf-8").splitlines()
        imp = next(i for i, l in enumerate(lines)
                   if l.startswith("import foundry_common as fc"))
        site = next(i for i, l in enumerate(lines) if l.startswith("GRAMMAR"))
        self.assertLess(imp, site)

    def test_no_peer_provider_was_introduced(self):
        """`foundry_probe` exports an exact-match `GRAMMAR`; it was not used,
        and this module does not import it. The delegation goes straight to the
        ratified compatibility boundary."""
        source = SHAPE_EXTRACTOR.read_text(encoding="utf-8")
        self.assertNotIn("p.GRAMMAR", source)
        self.assertNotIn("import foundry_probe", source)


class TestTheTenthSliceCheckerCatchesAReversion(unittest.TestCase):
    NOW = 'GRAMMAR = fc.REPO_ROOT / "docs" / "CODEBOOK-NAMING-GRAMMAR.md"'
    BEFORE = 'GRAMMAR = REPO_ROOT.parent / "docs" / "CODEBOOK-NAMING-GRAMMAR.md"'

    def reverted(self) -> str:
        source = SHAPE_EXTRACTOR.read_text(encoding="utf-8")
        self.assertIn(self.NOW, source, "the live text moved; fix the control")
        out = source.replace(self.NOW, self.BEFORE, 1)
        self.assertNotEqual(out, source)
        return out

    def test_restoring_the_local_construction_is_caught(self):
        """The LOCAL-OWNERSHIP arm. The shared checker returns to 2, and the
        GRAMMAR-keyed checker — which cannot be satisfied by the CR_CHECKS
        sibling — returns to 1."""
        reverted = self.reverted()
        self.assertEqual(len(local_root_relative_constructions(reverted)), 2)
        self.assertEqual(len(local_file_constructions(reverted, GRAMMAR_FILE)), 1)

    def test_reverting_also_drops_the_grammar_delegation(self):
        """The GRAMMAR-SPECIFIC delegation-positive arm."""
        reverted = self.reverted()
        self.assertEqual(
            root_delegated_file_constructions(reverted, GRAMMAR_FILE), [])
        self.assertEqual(len(root_delegating_expressions(reverted)), 0)

    def test_reverting_does_not_disturb_the_out_of_scope_sibling(self):
        """A control that also moved CR_CHECKS would prove nothing about which
        site the guards are aimed at."""
        reverted = self.reverted()
        self.assertEqual(
            len(local_file_constructions(reverted, CR_CHECKS_FILE)), 1)

    def test_the_measured_helper_coverage_is_what_decided_no_new_checker(self):
        """Re-checked every run rather than trusted from a commit message."""
        live, reverted = SHAPE_EXTRACTOR.read_text(encoding="utf-8"), self.reverted()
        self.assertEqual(len(local_root_relative_constructions(reverted)), 2)
        self.assertEqual(len(root_delegated_file_constructions(reverted, GRAMMAR_FILE)), 0)
        self.assertEqual(len(local_root_relative_constructions(live)), 1)
        self.assertEqual(len(root_delegated_file_constructions(live, GRAMMAR_FILE)), 1)

    def test_no_shared_helper_constant_was_widened(self):
        self.assertIn("docs", TOP_LEVEL_DIRS)
        self.assertNotIn(GRAMMAR_FILE, TOP_LEVEL_DIRS)
        self.assertNotIn(CR_CHECKS_FILE, TOP_LEVEL_DIRS)


class TestTheTenthSliceResolvedPathIsByteIdentical(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fc = load_legacy("foundry_common")
        cls.fx = load_legacy("foundry_shape_extractor")

    def test_grammar_equals_its_pre_change_construction(self):
        self.assertEqual(self.fx.GRAMMAR,
                         self.fx.REPO_ROOT.parent / "docs" / GRAMMAR_FILE)

    def test_grammar_equals_the_delegated_value(self):
        self.assertEqual(self.fx.GRAMMAR,
                         self.fc.REPO_ROOT / "docs" / GRAMMAR_FILE)

    def test_grammar_equals_the_ratified_owners_legacy_docs_path(self):
        self.assertEqual(self.fx.GRAMMAR, PATHS.legacy_docs / GRAMMAR_FILE)

    def test_the_equality_holds_as_strings_too(self):
        self.assertEqual(str(self.fx.GRAMMAR),
                         str(self.fx.REPO_ROOT.parent / "docs" / GRAMMAR_FILE))
        self.assertEqual(str(self.fx.GRAMMAR), str(PATHS.legacy_docs / GRAMMAR_FILE))

    def test_the_local_root_binding_still_resolves_as_before(self):
        """CONSUMPTION delegated, the root DECISION untouched."""
        self.assertEqual(self.fx.REPO_ROOT, self.fc.REPO_ROOT / "experiments")
        self.assertEqual(self.fx.REPO_ROOT, PATHS.legacy_experiments)

    def test_the_out_of_scope_sibling_still_resolves_locally_to_the_same_file(self):
        self.assertEqual(self.fx.CR_CHECKS,
                         self.fx.REPO_ROOT.parent / "docs" / CR_CHECKS_FILE)
        self.assertEqual(self.fx.CR_CHECKS, PATHS.legacy_docs / CR_CHECKS_FILE)


class TestTheTenthSliceLeftTheRulingDocumentAlone(unittest.TestCase):
    """C7.4: the PATH is plumbing, the DOCUMENT is truth. This guards the truth
    half, and the read-only premise the runtime evidence rests on."""

    @classmethod
    def setUpClass(cls):
        cls.fx = load_legacy("foundry_shape_extractor")
        cls.source = SHAPE_EXTRACTOR.read_text(encoding="utf-8")

    def test_the_grammar_document_is_tracked_and_present(self):
        self.assertTrue((PATHS.legacy_docs / GRAMMAR_FILE).is_file())
        self.assertEqual(self.fx.GRAMMAR, PATHS.legacy_docs / GRAMMAR_FILE)

    def test_the_document_still_carries_the_section_this_module_parses(self):
        """Content, not cardinality. This module reads §2's DELIVERY table, and
        `ratified_delivery_tokens` halts loudly if it cannot locate it."""
        text = (PATHS.legacy_docs / GRAMMAR_FILE).read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^## 2\.")

    def test_grammar_is_acquired_by_a_READ_and_never_by_a_write(self):
        """The only primitives applied to the name are `exists` and `read_text`."""
        tree = ast.parse(self.source)
        attrs = sorted(n.attr for n in ast.walk(tree)
                       if isinstance(n, ast.Attribute)
                       and isinstance(n.value, ast.Name)
                       and n.value.id == "GRAMMAR")
        self.assertEqual(attrs, ["exists", "read_text"])

    def test_the_read_feeds_the_delivery_vocabulary(self):
        """The migrated constant is load-bearing for the printed vocabulary
        rather than merely present."""
        self.assertIn('text = GRAMMAR.read_text(encoding="utf-8")', self.source)

    def test_every_write_in_this_module_stays_flag_gated(self):
        """The read-only premise of the runtime evidence, asserted so it cannot
        rot silently: both write primitives are `Path(args.json).write_text`,
        and both sit under `if args.json:`."""
        tree = ast.parse(self.source)
        writes = [n for n in ast.walk(tree)
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                  and n.func.attr in ("write_text", "write_bytes", "mkdir",
                                      "unlink", "rename", "touch")]
        self.assertEqual(len(writes), 2, [ast.unparse(w)[:60] for w in writes])
        for w in writes:
            self.assertTrue(ast.unparse(w).startswith("Path(args.json).write_text"))
        guarded = [n for n in ast.walk(tree)
                   if isinstance(n, ast.If) and ast.unparse(n.test) == "args.json"]
        self.assertEqual(len(guarded), 2)
        for branch in guarded:
            self.assertEqual(
                sum(1 for d in ast.walk(branch)
                    if isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                    and d.func.attr == "write_text"), 1)

    def test_the_json_flag_cannot_gain_a_default_silently(self):
        """`--json` declares NO argparse keywords, so its default is None and
        the bare command cannot reach either write."""
        tree = ast.parse(self.source)
        decls = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                 and n.func.attr == "add_argument"
                 and any(isinstance(a, ast.Constant) and a.value == "--json"
                         for a in n.args)]
        self.assertEqual(len(decls), 1)
        self.assertEqual(decls[0].keywords, [])


class TestTheTenthSliceChangedNothingElse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fx = load_legacy("foundry_shape_extractor")
        cls.source = SHAPE_EXTRACTOR.read_text(encoding="utf-8")

    def test_the_generated_artifact_sibling_is_deliberately_untouched(self):
        """`docs/cr-checks.json` is a GENERATED artifact, explicitly ineligible
        in this tranche. It sits on the very next line, so this is the guard
        that stops one slice from quietly becoming two."""
        self.assertIn('CR_CHECKS = REPO_ROOT.parent / "docs" / "cr-checks.json"',
                      self.source)
        self.assertEqual(len(local_file_constructions(self.source, CR_CHECKS_FILE)), 1)
        self.assertEqual(
            root_delegated_file_constructions(self.source, CR_CHECKS_FILE), [])

    def test_the_root_decision_and_bootstrap_are_unchanged(self):
        self.assertIn("REPO_ROOT = Path(__file__).resolve().parent", self.source)
        self.assertEqual(self.source.count("sys.path.insert"), 1)
        self.assertIn("sys.path.insert(0, str(REPO_ROOT))", self.source)

    def test_the_module_constant_surface_is_unchanged(self):
        tree = ast.parse(self.source)
        self.assertEqual(
            [t.id for n in tree.body if isinstance(n, ast.Assign)
             for t in n.targets if isinstance(t, ast.Name)][:3],
            ["REPO_ROOT", "GRAMMAR", "CR_CHECKS"])

    def test_the_cli_surface_is_unchanged(self):
        tree = ast.parse(self.source)
        flags = [a.value for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                 and n.func.attr == "add_argument"
                 for a in n.args if isinstance(a, ast.Constant)]
        self.assertEqual(flags, ["--gaps", "--action", "--rank", "--limit", "--json"])

    def test_foundry_common_is_still_not_modified(self):
        # REPAIRED BY C8.5A. This slice still added no layout statement to the
        # boundary -- that claim is unchanged and is what is asserted. The old
        # literal was superseded when C8.5A pointed the boundary at ProjectPaths.
        self.assertEqual(
            len(foundry_common_independent_layout(
                (EXPERIMENTS / "foundry_common.py").read_text(encoding="utf-8"))),
            1)

    def test_no_gate2_row_covers_this_module(self):
        """Measured, not assumed: like P0.4M, the runtime evidence for this
        slice is the direct bare command, not gate coverage."""
        for _name, argv, _ in gate_rows():
            self.assertNotIn("experiments/foundry_shape_extractor.py", argv)

    def test_no_production_module_reads_fx_GRAMMAR_as_an_attribute(self):
        """The fan-in fact, measured rather than assumed. 19 modules import this
        one; none reads its GRAMMAR constant, so value preservation is the only
        contract the migration has to keep — and it is proved separately."""
        offenders = []
        for path in sorted(EXPERIMENTS.rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            for alias in ("fx.GRAMMAR", "shape_extractor.GRAMMAR"):
                if alias in text:
                    offenders.append(f"{path.name}: {alias}")
        self.assertEqual(offenders, [])

    def test_the_earlier_slices_sites_are_not_touched(self):
        self.assertEqual(
            len(delegating_expressions(PROBE.read_text(encoding="utf-8"))), 1)
        self.assertEqual(
            len(root_delegating_expressions(REACHABILITY.read_text(encoding="utf-8"))), 2)
        self.assertEqual(
            len(root_delegating_expressions(PROBE.read_text(encoding="utf-8"))), 1)
        self.assertEqual(
            len(root_delegated_file_constructions(
                SLUG_REPARSE.read_text(encoding="utf-8"), GRAMMAR_FILE)), 1)
        self.assertEqual(
            len(delegating_expressions(
                SLUG_REPARSE.read_text(encoding="utf-8"), "codebook.json")), 1)


# ---------------------------------------------------------------------------
# C8.5A — the compatibility boundary itself
# ---------------------------------------------------------------------------
#
#     experiments/foundry_common.py
#       REPO_ROOT       = Path(__file__).resolve().parents[1]  ->  _PATHS.root
#       FOUNDRY_OUT_DIR = REPO_ROOT / "experiments" / "out" / "foundry"
#                                                     ->  _PATHS.legacy_foundry_out
#       REVIEW_DIR      = FOUNDRY_OUT_DIR / "review"  ->  _PATHS.legacy_foundry_review
#
# This is the FIRST C8 step-5 migration and it is a different KIND of change from
# every P0.4 slice. Those routed legacy consumption TO this boundary; this one
# routes the boundary itself to the ratified permanent owner. All 134 downstream
# delegating expressions are untouched and inherit the new source for free.
#
# WHY TEN EARLIER GUARDS WERE REPAIRED RATHER THAN DELETED. Nine P0.4 slice
# blocks each asserted `foundry_common` still held a specific literal -- that was
# how each slice proved IT had not touched the boundary. That claim is still true
# of each of those slices; C8.5A is the task that legitimately changes the text.
# They are re-pointed at `foundry_common_independent_layout()`, which expresses
# the same "the boundary gained no independent layout statement" meaning as a
# STRUCTURAL invariant that survives the migration instead of a string that does
# not. No slice lost a guard, and the replacement is strictly stronger: it would
# also catch a NEW literal the old string match could never have seen.


def foundry_common_independent_layout(source: str) -> list[str]:
    """Repository-relative layout the boundary states INDEPENDENTLY of ProjectPaths.

    After C8.5A this must be exactly ONE entry: the bootstrap `... / "src"` join
    that locates the package. Nothing can ask the layout owner where it lives
    before importing it, so that single literal is irreducible -- and naming it
    here is what stops it quietly growing into a second layout API.
    """
    matches = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Div):
            continue
        base = node
        while isinstance(base, ast.BinOp) and isinstance(base.op, ast.Div):
            base = base.left
        if isinstance(base, ast.Attribute) and base.attr == "parent":
            base = base.value
        if not (isinstance(base, ast.Name)
                and base.id in ("REPO_ROOT", "_BOOTSTRAP_ROOT")):
            continue
        matches.append(node)
    inner = {id(d) for n in matches for d in ast.walk(n) if d is not n}
    return [f"line {n.lineno}: {ast.unparse(n)}"
            for n in matches if id(n) not in inner]


FOUNDRY_COMMON = EXPERIMENTS / "foundry_common.py"


class TestTheBoundaryDelegatesToTheRatifiedOwner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fc = load_legacy("foundry_common")
        cls.source = FOUNDRY_COMMON.read_text(encoding="utf-8")

    def test_it_imports_the_permanent_owner(self):
        self.assertIn("from mtj_foundry.paths import ProjectPaths", self.source)

    def test_the_three_values_come_from_ProjectPaths_not_from_literals(self):
        self.assertIn("REPO_ROOT = _PATHS.root", self.source)
        self.assertIn("FOUNDRY_OUT_DIR = _PATHS.legacy_foundry_out", self.source)
        self.assertIn("REVIEW_DIR = _PATHS.legacy_foundry_review", self.source)

    def test_the_live_values_are_the_owners_values(self):
        self.assertEqual(self.fc.REPO_ROOT, self.fc._PATHS.root)
        self.assertEqual(self.fc.FOUNDRY_OUT_DIR, self.fc._PATHS.legacy_foundry_out)
        self.assertEqual(self.fc.REVIEW_DIR, self.fc._PATHS.legacy_foundry_review)

    def test_the_values_equal_their_pre_change_constructions(self):
        """The whole point: 134 downstream expressions must not move."""
        root = Path(self.fc.__file__).resolve().parents[1]
        self.assertEqual(self.fc.REPO_ROOT, root)
        self.assertEqual(self.fc.FOUNDRY_OUT_DIR,
                         root / "experiments" / "out" / "foundry")
        self.assertEqual(self.fc.REVIEW_DIR,
                         root / "experiments" / "out" / "foundry" / "review")

    def test_the_equalities_hold_as_strings_too(self):
        root = Path(self.fc.__file__).resolve().parents[1]
        self.assertEqual(str(self.fc.REPO_ROOT), str(root))
        self.assertEqual(str(self.fc.FOUNDRY_OUT_DIR),
                         str(root / "experiments" / "out" / "foundry"))
        self.assertEqual(str(self.fc.REVIEW_DIR),
                         str(root / "experiments" / "out" / "foundry" / "review"))

    def test_they_equal_a_ProjectPaths_built_independently_of_the_module(self):
        """Built from scratch here, so this is not the module agreeing with
        itself."""
        paths = ProjectPaths.for_root(Path(self.fc.__file__).resolve().parents[1])
        self.assertEqual(self.fc.REPO_ROOT, paths.root)
        self.assertEqual(self.fc.FOUNDRY_OUT_DIR, paths.legacy_foundry_out)
        self.assertEqual(self.fc.REVIEW_DIR, paths.legacy_foundry_review)


class TestTheBootstrapStaysCompatibilityOnly(unittest.TestCase):
    """The bootstrap is the one thing here that could rot into a second layout
    API. These guards are what stop that happening quietly."""

    @classmethod
    def setUpClass(cls):
        cls.source = FOUNDRY_COMMON.read_text(encoding="utf-8")

    def test_the_only_independent_layout_left_is_the_src_bootstrap(self):
        got = foundry_common_independent_layout(self.source)
        self.assertEqual(len(got), 1, got)
        self.assertIn("'src'", got[0])
        self.assertIn("_BOOTSTRAP_ROOT", got[0])

    def test_the_bootstrap_root_is_used_for_exactly_two_things(self):
        """Not a line-distance heuristic -- the actual invariant. The private
        root may ONLY locate `src` and construct the ProjectPaths instance. Any
        third use would be it becoming a general-purpose root, which is exactly
        the failure mode this bootstrap must not drift into."""
        tree = ast.parse(self.source)
        loads = []
        for stmt in tree.body:
            for n in ast.walk(stmt):
                if (isinstance(n, ast.Name) and n.id == "_BOOTSTRAP_ROOT"
                        and isinstance(n.ctx, ast.Load)):
                    loads.append(ast.unparse(stmt))
                    break
        self.assertEqual(sorted(loads), [
            '_BOOTSTRAP_SRC = _BOOTSTRAP_ROOT / \'src\'',
            '_PATHS = ProjectPaths.for_root(_BOOTSTRAP_ROOT)',
        ], loads)

    def test_the_bootstrap_names_are_private(self):
        for name in ("_BOOTSTRAP_ROOT", "_BOOTSTRAP_SRC", "_PATHS"):
            with self.subTest(name=name):
                self.assertTrue(name.startswith("_"))
                self.assertIn(name, self.source)

    def test_no_new_filesystem_discovery_was_introduced(self):
        """The task forbids strengthening import-time assumptions."""
        head = self.source.split("def halt")[0]
        # `discover_root` is NAMED in the comment that explains why it is not
        # used; asserting on the word would forbid the explanation. Assert on a
        # CALL instead -- which is the thing that would actually probe the disk.
        calls = [ast.unparse(n.func) for n in ast.walk(ast.parse(self.source))
                 if isinstance(n, ast.Call)]
        self.assertNotIn("discover_root", calls)
        self.assertNotIn(".exists()", head)
        self.assertNotIn(".glob(", head)
        self.assertNotIn(".iterdir(", head)

    def test_the_derivation_is_the_same_pure_lexical_one_as_before(self):
        self.assertIn("_BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]",
                      self.source)

    def test_the_bootstrap_insert_is_idempotent(self):
        self.assertIn("if str(_BOOTSTRAP_SRC) not in sys.path:", self.source)
        self.assertIn('_BOOTSTRAP_SRC = _BOOTSTRAP_ROOT / "src"', self.source)

    def test_it_is_labelled_temporary_and_non_authoritative(self):
        """The comment is load-bearing: it tells the next session this block is
        scheduled for deletion, not for reuse."""
        head = self.source.split("def halt")[0]
        self.assertIn("C8.5A COMPATIBILITY BOOTSTRAP", head)
        self.assertIn("TEMPORARY", head)
        self.assertIn("NOT A LAYOUT API", head)


class TestTheTierEngineEdgeIsUnchanged(unittest.TestCase):
    """Explicitly NOT this task's problem, and asserted so a later reader cannot
    mistake C8.5A for having solved the upward engine dependency."""

    @classmethod
    def setUpClass(cls):
        cls.source = FOUNDRY_COMMON.read_text(encoding="utf-8")

    def test_the_engine_is_still_imported_at_module_import_time(self):
        tree = ast.parse(self.source)
        top = [n for n in tree.body if isinstance(n, ast.Import)
               and any(a.name == "tier_engine" for a in n.names)]
        self.assertEqual(len(top), 1)

    def test_the_experiments_path_compatibility_is_preserved(self):
        self.assertIn("sys.path.insert(0, str(_PATHS.legacy_experiments))",
                      self.source)

    def test_experiments_is_inserted_after_the_bootstrap_so_it_keeps_precedence(self):
        lines = self.source.splitlines()
        src_line = next(i for i, l in enumerate(lines) if "not in sys.path" in l)
        exp_line = next(i for i, l in enumerate(lines)
                        if "sys.path.insert(0, str(_PATHS.legacy_experiments))" in l)
        self.assertLess(src_line, exp_line)


class TestProjectPathsGainedOnlyTheSmallestProperty(unittest.TestCase):
    def test_legacy_foundry_review_is_pure_and_correct(self):
        paths = ProjectPaths.for_root("/nonexistent-root-for-purity")
        self.assertEqual(paths.legacy_foundry_review,
                         Path("/nonexistent-root-for-purity")
                         / "experiments" / "out" / "foundry" / "review")

    def test_it_is_derived_from_its_sibling_not_restated(self):
        self.assertEqual(ProjectPaths.for_root("/r").legacy_foundry_review,
                         ProjectPaths.for_root("/r").legacy_foundry_out / "review")

    def test_it_touches_no_filesystem(self):
        paths = ProjectPaths.for_root("/definitely/not/a/real/path")
        self.assertFalse(paths.legacy_foundry_review.exists())
        self.assertTrue(str(paths.legacy_foundry_review).startswith("/definitely"))

    def test_no_other_public_property_was_added(self):
        """C8.5C adds exactly one: `legacy_data_artifacts`. The list is pinned
        in full rather than counted, because a count cannot see a substitution."""
        props = sorted(n for n in dir(ProjectPaths)
                       if not n.startswith("_")
                       and isinstance(getattr(ProjectPaths, n), property))
        self.assertEqual(props, [
            "baselines", "config", "conservation", "decisions",
            "legacy_data_artifacts",
            "legacy_docs", "legacy_experiments", "legacy_experiments_out",
            "legacy_foundry_out", "legacy_foundry_review", "legacy_pipeline",
            "refoundation", "src", "tests"])


class TestTheDownstreamDelegationsAreUntouched(unittest.TestCase):
    """134 legacy expressions delegate to this boundary. C8.5A changes where the
    boundary GETS its values, never what any consumer says."""

    def test_the_arc_added_delegation_sites_still_read_as_before(self):
        self.assertEqual(
            len(delegating_expressions(PROBE.read_text(encoding="utf-8"))), 1)
        self.assertEqual(len(root_delegating_expressions(
            REACHABILITY.read_text(encoding="utf-8"))), 2)
        self.assertEqual(len(root_delegated_file_constructions(
            SLUG_REPARSE.read_text(encoding="utf-8"), GRAMMAR_FILE)), 1)
        self.assertEqual(len(root_delegated_file_constructions(
            SHAPE_EXTRACTOR.read_text(encoding="utf-8"), GRAMMAR_FILE)), 1)
        self.assertEqual(len(delegating_expressions(
            SLUG_REPARSE.read_text(encoding="utf-8"), "codebook.json")), 1)

    def test_a_downstream_consumer_resolves_to_the_same_place_as_before(self):
        sr = load_legacy("foundry_slug_reparse")
        root = Path(load_legacy("foundry_common").__file__).resolve().parents[1]
        self.assertEqual(sr.CODEBOOK,
                         root / "experiments" / "out" / "foundry" / "codebook.json")
        self.assertEqual(sr.GRAMMAR, root / "docs" / GRAMMAR_FILE)



# ===========================================================================
# C8.5B — THE STEP-5 MEASUREMENT REBASE
# ===========================================================================
#
# C8.5A moved the compatibility boundary's three layout values onto
# ProjectPaths. It changed no consumer -- GitHub verifies the diff is three
# files -- and yet the P0.4-era census stopped being able to count the
# consumers, because that census discovered a PROVIDER by following a
# module-level `Path(__file__)` chain and `_PATHS.legacy_foundry_out` is not
# one. The Manager blocked further census-driven Step-5 selection on repairing
# it (issue:1#issuecomment-5471350993).
#
# `tests/refoundation/layout_census.py` is the repair. What follows pins the
# fresh numbers at this head, proves the reconciliation leaves no unexplained
# remainder, and runs the negative controls -- including the two that matter
# most here: that a ProjectPaths-backed provider RESOLVES, and that a provider
# resolving to the WRONG place turns a guard red rather than passing quietly.
#
# THE COUNTS BELOW ARE MEASUREMENTS, NOT RATCHETS. A later slice that migrates
# a delegation is SUPPOSED to move them. They are pinned so that movement is
# stated in a diff instead of discovered later as drift.

PATHS_SOURCE = (REPO_ROOT / "src" / "mtj_foundry" / "paths.py")
FOUNDRY_CODEBOOK = EXPERIMENTS / "foundry_codebook.py"

# Measured fresh from the AST of every tracked Python file. Re-measured at the
# C8.5C head: the migration moved 23 of these numbers in exactly the direction
# the Manager pre-committed (issue:1#issuecomment-5471648752), with zero
# unexplained differences. The C8.5B values are kept beside each moved row so a
# later reader can see the movement rather than a fresh unexplained constant.
CENSUS_HEAD = {
    # 126 tracked files at the C8.5A head be52961, plus this task's own new
    # census helper, which lands in the `tests` bucket and in no measured scope.
    "tracked_python": 127,
    "files_by_scope": {"experiments": 87, "experiments_measure": 6,
                       "aq4_PAUSED": 6, "pipeline": 11, "src": 4, "tests": 13},
    "delegations_total": 141,                      # C8.5B: 140
    "delegations_by_provider": {
        "foundry_common.FOUNDRY_OUT_DIR": 126,     # unchanged
        "foundry_common.REPO_ROOT": 14,            # C8.5B: 12 (+2 re-pointed)
        "foundry_common.DATA_ARTIFACTS_DIR": 1,    # C8.5B: name did not exist
        # `foundry_codebook.REPO_ROOT` was 2 and is GONE: the peer provider no
        # longer exists, so the key is absent rather than zero.
    },
    "delegations_by_form": {
        "PATH_JOIN": 136,                          # C8.5B: 135
        "DIRECT_BIND": 3, "ATTRIBUTE_NAV": 1, "CALL_ARG": 1,
    },
    "delegation_files": 52,                        # unchanged
    "local_sites_total": 88,                       # C8.5B: 89
    "local_sites_bootstrap": 28,                   # unchanged
    "local_sites_consumption": 60,                 # C8.5B: 61
    "consumption_origin": {"hop1": 44, "hop2": 14, "inline": 2},   # hop1 was 45
    "consumption_scope": {"module": 43, "function": 17},           # module was 44
    "consumption_files": 29,                       # C8.5B: 30
    "sys_path_calls": {"experiments": 83, "experiments_measure": 6},
}

# The one live site in legacy production whose LINE carries the text
# `sys.path.insert` while the module makes no such call: the text is inside an
# f-string that builds a shell command for `os.system`. P0.4N classified it by a
# text match and put it in the bootstrap bucket; P0.4P corrected it. The
# correction is kept here as a test rather than as a sentence.
TEXT_ONLY_SYS_PATH = ("experiments/foundry_verify_migration.py", 571)


def _census_inputs():
    paths_layout = layout_census.project_paths_layout(
        PATHS_SOURCE.read_text(encoding="utf-8"))
    providers = {}
    for module in layout_census.PROVIDER_MODULES:
        rel = Path("experiments") / f"{module}.py"
        providers[module] = layout_census.provider_layout(
            (REPO_ROOT / rel).read_text(encoding="utf-8"), rel, paths_layout)
    return paths_layout, providers


class TestTheCensusUniverseIsWhatItClaims(unittest.TestCase):
    """A census silently narrowed by an ignore rule reports a smaller world and
    looks healthy. Two independent enumerations must agree."""

    def test_tracked_and_walked_python_agree(self):
        tracked = layout_census.tracked_python(REPO_ROOT)
        self.assertEqual(tracked, layout_census.walked_python(REPO_ROOT))
        self.assertEqual(len(tracked), CENSUS_HEAD["tracked_python"])

    def test_every_file_lands_in_exactly_one_named_scope(self):
        """`other` is the unclassified bucket. A non-empty `other` would mean the
        census has a population it is not reporting on either side."""
        counts = {}
        for rel in layout_census.tracked_python(REPO_ROOT):
            scope = layout_census.scope_of(rel)
            counts[scope] = counts.get(scope, 0) + 1
        self.assertEqual(counts, CENSUS_HEAD["files_by_scope"])
        self.assertEqual(sum(counts.values()), CENSUS_HEAD["tracked_python"])
        self.assertNotIn("other", counts)

    def test_aq4_is_excluded_from_legacy_production_in_both_of_its_homes(self):
        """AQ4 is PAUSED. It lives in a package AND in one loose file, so a
        directory test alone leaves one AQ4 module inside the production scope."""
        self.assertEqual(
            layout_census.scope_of(Path("experiments/aq4_benchmark/aq4_binding.py")),
            "aq4_PAUSED")
        self.assertEqual(
            layout_census.scope_of(Path("experiments/foundry_aq4_probes.py")),
            "aq4_PAUSED")
        self.assertNotIn("aq4_PAUSED", layout_census.LEGACY_PRODUCTION)

    def test_a_non_foundry_filename_is_still_in_scope(self):
        """`experiments/validate_slug.py` carries 4 delegations and does not
        begin with `foundry_`. A filename prefix is not a scope."""
        self.assertEqual(layout_census.scope_of(Path("experiments/validate_slug.py")),
                         "experiments")


class TestProjectPathsResolvesStatically(unittest.TestCase):
    """The census learns the owner's layout by PARSING it. Importing the package
    to ask it for a path would be executing project code to learn a fact the
    source states, which is the habit this arc removes."""

    @classmethod
    def setUpClass(cls):
        cls.layout = layout_census.project_paths_layout(
            PATHS_SOURCE.read_text(encoding="utf-8"))

    def test_every_property_resolves_to_repository_relative_components(self):
        self.assertEqual(self.layout["root"], ())
        self.assertEqual(self.layout["legacy_experiments"], ("experiments",))
        self.assertEqual(self.layout["legacy_foundry_out"],
                         ("experiments", "out", "foundry"))
        self.assertEqual(self.layout["legacy_foundry_review"],
                         ("experiments", "out", "foundry", "review"))
        self.assertEqual(self.layout["baselines"], ("config", "baselines"))

    def test_the_static_resolution_agrees_with_the_live_class(self):
        """Parsed and executed must not disagree. The census uses the parse; this
        is the one place the two are compared, and it is a test, not a source."""
        paths = ProjectPaths.for_root("/r")
        for name, parts in self.layout.items():
            with self.subTest(name=name):
                self.assertEqual(getattr(paths, name), Path("/r").joinpath(*parts))

    def test_it_covers_every_public_property_and_the_root_field(self):
        """`root` is the dataclass FIELD, not a property, so a property-only
        comparison would silently exclude the one name every other resolves
        against."""
        live = {n for n in dir(ProjectPaths) if not n.startswith("_")
                and isinstance(getattr(ProjectPaths, n), property)}
        self.assertEqual(set(self.layout) - {"root"}, live)
        self.assertIn("root", {f.name for f in
                               dataclasses.fields(ProjectPaths)})


# ---------------------------------------------------------------------------
# C8.5B.R1 — FILE-CHAIN ASCENT SEMANTICS
# ---------------------------------------------------------------------------
#
# `pathlib` numbers `parents` from 1: `p.parents[0]` IS `p.parent`. C8.5B's
# helper counted `.parent` as one hop and `parents[N]` as N, so the two
# spellings of the same directory disagreed by one, in BOTH directions:
#
#     .parent        resolved to the repository ROOT (it means `experiments/`)
#     .parent.parent resolved to None                (it means the root)
#
# No accepted count moved -- every chain-backed provider in the corpus is
# spelled `parents[1]`, and the local-site scan only asks whether a chain
# exists -- but `.parent` produced a WRONG TUPLE rather than a missing one, and
# a wrong value that looks plausible is the failure mode this census exists to
# stop. Repaired under C8.5B.R1 (issue:1#issuecomment-5471544666).
#
# The controls below assert EXACT COMPONENTS, not "a chain was detected", and
# they check the census against `pathlib` itself rather than against a table
# written by the same hand that wrote the code.

# `Path(__file__)` is always the module's own file, so the ascent arithmetic
# depends on how deep that file sits. Both depths are exercised.
ASCENT_FILES = (Path("experiments/foundry_common.py"),
                Path("experiments/measure/axis_foundry.py"))

# (source spelling, the pathlib expression that MUST denote the same directory)
ASCENT_SPELLINGS = (
    ("Path(__file__).resolve().parent", lambda f: f.parent),
    ("Path(__file__).resolve().parents[0]", lambda f: f.parents[0]),
    ("Path(__file__).resolve().parent.parent", lambda f: f.parent.parent),
    ("Path(__file__).resolve().parents[1]", lambda f: f.parents[1]),
    ("Path(__file__).resolve().parent.parent.parent", lambda f: f.parent.parent.parent),
    ("Path(__file__).resolve().parents[2]", lambda f: f.parents[2]),
)

EQUIVALENT_PAIRS = (
    ("Path(__file__).resolve().parent",
     "Path(__file__).resolve().parents[0]"),
    ("Path(__file__).resolve().parent.parent",
     "Path(__file__).resolve().parents[1]"),
    ("Path(__file__).resolve().parent.parent.parent",
     "Path(__file__).resolve().parents[2]"),
)


def _pre_r1_file_chain_hops(expr):
    """The C8.5B implementation, kept so the defect stays reproducible.

    Identical to the repaired version except that `parents[N]` contributes N
    instead of N + 1.

    IT IS ONLY HALF THE PRE-R1 BEHAVIOUR. C8.5B measured ascent from the file
    but subtracted it from the file's DIRECTORY, so the defect lived in the
    PAIR of functions; `_pre_r1_root_relative` below is the other half. A first
    draft of the control patched this one alone and the equivalence came out
    accidentally CORRECT -- the two halves had been cancelling. A negative
    control must restore the whole broken state, or it measures something else.
    """
    if not any(isinstance(n, ast.Name) and n.id == "__file__"
               for n in ast.walk(expr)):
        return None
    ups = 0
    node = expr
    while True:
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute) \
                and node.value.attr == "parents" \
                and isinstance(node.slice, ast.Constant) \
                and isinstance(node.slice.value, int):
            ups += node.slice.value
            node = node.value.value
            continue
        if isinstance(node, ast.Attribute) and node.attr == "parent":
            ups += 1
            node = node.value
            continue
        if isinstance(node, ast.Attribute) and node.attr == "resolve":
            node = node.value
            continue
        if isinstance(node, ast.Call):
            node = node.func
            continue
        if isinstance(node, ast.Attribute):
            node = node.value
            continue
        break
    return ups


def _pre_r1_root_relative(rel, ups):
    """The C8.5B counterpart: an ascent subtracted from the file's DIRECTORY."""
    directory = rel.parts[:-1]
    keep = len(directory) - ups
    if keep < 0:
        return None
    return directory[:keep]


def _resolve_spelling(spelling: str, rel: Path):
    """Repository-relative components the census assigns to a chain, or None."""
    expr = ast.parse(spelling, mode="eval").body
    return layout_census._root_relative(rel, layout_census._file_chain_hops(expr))


class TestFileChainAscentSemantics(unittest.TestCase):
    """C8.5B.R1. Exact values, both spellings, checked against pathlib."""

    def test_every_spelling_resolves_to_what_pathlib_says_it_means(self):
        """THE GROUND TRUTH IS THE LIBRARY, not a table in this file. A table
        written beside the implementation can agree with the same mistake."""
        for rel in ASCENT_FILES:
            anchored = Path("/r").joinpath(*rel.parts)
            for spelling, pathlib_form in ASCENT_SPELLINGS:
                with self.subTest(file=rel.as_posix(), spelling=spelling):
                    expected = pathlib_form(anchored)
                    got = _resolve_spelling(spelling, rel)
                    if Path("/r") not in expected.parents and expected != Path("/r"):
                        # The chain ascends above the repository root, which no
                        # repository-relative tuple can express.
                        self.assertIsNone(got)
                    else:
                        self.assertIsNotNone(got)
                        self.assertEqual(Path("/r").joinpath(*got), expected)

    def test_the_equivalent_spellings_resolve_identically(self):
        for rel in ASCENT_FILES:
            for left, right in EQUIVALENT_PAIRS:
                with self.subTest(file=rel.as_posix(), pair=(left, right)):
                    self.assertEqual(_resolve_spelling(left, rel),
                                     _resolve_spelling(right, rel))

    def test_the_exact_components_at_a_depth_one_file(self):
        rel = Path("experiments/foundry_common.py")
        self.assertEqual(_resolve_spelling("Path(__file__).resolve().parent", rel),
                         ("experiments",))
        self.assertEqual(_resolve_spelling("Path(__file__).resolve().parents[0]", rel),
                         ("experiments",))
        self.assertEqual(_resolve_spelling("Path(__file__).resolve().parent.parent", rel),
                         ())
        self.assertEqual(_resolve_spelling("Path(__file__).resolve().parents[1]", rel),
                         ())

    def test_the_exact_components_at_a_depth_two_file(self):
        """The arithmetic must follow the FILE's depth, not a constant."""
        rel = Path("experiments/measure/axis_foundry.py")
        self.assertEqual(_resolve_spelling("Path(__file__).resolve().parent", rel),
                         ("experiments", "measure"))
        self.assertEqual(_resolve_spelling("Path(__file__).resolve().parents[1]", rel),
                         ("experiments",))
        self.assertEqual(_resolve_spelling("Path(__file__).resolve().parents[2]", rel),
                         ())

    def test_ascending_above_the_repository_root_is_None_not_a_wrong_tuple(self):
        rel = Path("experiments/foundry_common.py")
        for spelling in ("Path(__file__).resolve().parents[2]",
                         "Path(__file__).resolve().parent.parent.parent"):
            with self.subTest(spelling=spelling):
                self.assertIsNone(_resolve_spelling(spelling, rel))

    def test_a_provider_resolves_the_same_through_BOTH_spellings(self):
        """The requirement stated as the census actually uses it: a PROVIDER,
        resolved to exact repository-relative components, not a non-None chain.

        Both modules below are the pre-C8.5A `foundry_common` shape, written the
        two different ways. The census must give them the same layout."""
        rel = Path("experiments/foundry_common.py")
        template = ('import sys\n'
                    'from pathlib import Path\n'
                    'REPO_ROOT = {chain}\n'
                    'FOUNDRY_OUT_DIR = REPO_ROOT / "experiments" / "out" / "foundry"\n'
                    'REVIEW_DIR = FOUNDRY_OUT_DIR / "review"\n')
        expected = {"REPO_ROOT": (),
                    "FOUNDRY_OUT_DIR": ("experiments", "out", "foundry"),
                    "REVIEW_DIR": ("experiments", "out", "foundry", "review")}
        resolved = []
        for chain in ("Path(__file__).resolve().parents[1]",
                      "Path(__file__).resolve().parent.parent"):
            with self.subTest(chain=chain):
                got = layout_census.provider_layout(
                    template.format(chain=chain), rel, paths_layout={})
                self.assertEqual(got, expected)
                resolved.append(got)
        self.assertEqual(resolved[0], resolved[1])

    def test_the_same_holds_for_a_ProjectPaths_backed_provider(self):
        """The bootstrap root is a chain too, so the repair must not have made
        the two provider shapes disagree with each other."""
        rel = Path("experiments/foundry_common.py")
        _, providers = _census_inputs()
        for chain in ("Path(__file__).resolve().parents[1]",
                      "Path(__file__).resolve().parent.parent"):
            with self.subTest(chain=chain):
                source = ('from pathlib import Path\n'
                          'from mtj_foundry.paths import ProjectPaths\n'
                          f'_ROOT = {chain}\n'
                          '_PATHS = ProjectPaths.for_root(_ROOT)\n'
                          'FOUNDRY_OUT_DIR = _PATHS.legacy_foundry_out\n')
                got = layout_census.provider_layout(
                    source, rel, _census_inputs()[0])
                self.assertEqual(got["_ROOT"], ())
                self.assertEqual(got["FOUNDRY_OUT_DIR"],
                                 ("experiments", "out", "foundry"))
                self.assertEqual(got["FOUNDRY_OUT_DIR"],
                                 providers["foundry_common"]["FOUNDRY_OUT_DIR"])

    def test_NEGATIVE_CONTROL_the_pre_R1_off_by_one_turns_these_guards_red(self):
        """Break the equivalence and prove the guard sees it.

        The pre-R1 function is substituted into `layout_census` itself -- the
        module `provider_layout` actually reaches -- not into this file's
        globals. Patching the wrong copy is a recorded trap here, and it reads
        as a passing test.
        """
        rel = Path("experiments/foundry_common.py")
        original_hops = layout_census._file_chain_hops
        original_relative = layout_census._root_relative
        try:
            layout_census._file_chain_hops = _pre_r1_file_chain_hops
            layout_census._root_relative = _pre_r1_root_relative

            # 1. the equivalence itself breaks, in both directions
            self.assertNotEqual(
                _resolve_spelling("Path(__file__).resolve().parent", rel),
                _resolve_spelling("Path(__file__).resolve().parents[0]", rel))
            self.assertNotEqual(
                _resolve_spelling("Path(__file__).resolve().parent.parent", rel),
                _resolve_spelling("Path(__file__).resolve().parents[1]", rel))

            # 2. the specific wrong answers, named so this control cannot pass
            #    for some unrelated reason
            self.assertEqual(
                _resolve_spelling("Path(__file__).resolve().parent", rel), (),
                "pre-R1 resolved `.parent` to the repository ROOT")
            self.assertIsNone(
                _resolve_spelling("Path(__file__).resolve().parent.parent", rel),
                "pre-R1 lost `.parent.parent` entirely")

            # 3. and it reaches a PROVIDER: the `.parent.parent` spelling of the
            #    pre-C8.5A boundary loses all three of its layout names.
            source = ('from pathlib import Path\n'
                      'REPO_ROOT = Path(__file__).resolve().parent.parent\n'
                      'FOUNDRY_OUT_DIR = REPO_ROOT / "experiments" / "out" / "foundry"\n')
            self.assertEqual(
                layout_census.provider_layout(source, rel, paths_layout={}), {})
        finally:
            layout_census._file_chain_hops = original_hops
            layout_census._root_relative = original_relative

        # restored, and the guard is green again
        self.assertEqual(
            _resolve_spelling("Path(__file__).resolve().parent", rel),
            _resolve_spelling("Path(__file__).resolve().parents[0]", rel))
        self.assertEqual(
            layout_census._file_chain_hops(
                ast.parse("Path(__file__).resolve().parents[1]", mode="eval").body), 2)

    def test_the_repair_moved_no_accepted_measurement(self):
        """R1 is a semantics fix, not a re-measurement. Every chain-backed
        provider in the corpus is spelled `parents[1]`, which resolved correctly
        before and after -- so the accepted C8.5B counts must be untouched, and
        `CENSUS_HEAD` above is asserted unchanged by the counting tests."""
        _, providers = _census_inputs()
        self.assertEqual(providers["foundry_common"]["_BOOTSTRAP_ROOT"], ())
        # C8.5C made both bootstrap roots private; both are still `parents[1]`
        # chains, which is what this guard is about.
        self.assertEqual(providers["foundry_codebook"]["_BOOTSTRAP_ROOT"], ())
        for rel in (Path("experiments/foundry_common.py"),
                    Path("experiments/foundry_codebook.py")):
            source = (REPO_ROOT / rel).read_text(encoding="utf-8")
            chains = [n for n in ast.walk(ast.parse(source))
                      if isinstance(n, ast.Subscript)
                      and isinstance(n.value, ast.Attribute)
                      and n.value.attr == "parents"]
            self.assertEqual([ast.unparse(c).endswith("parents[1]") for c in chains],
                             [True], rel.as_posix())


class TestTheProviderRepair(unittest.TestCase):
    """NEGATIVE CONTROL 7 and 8, and the reason this task exists."""

    @classmethod
    def setUpClass(cls):
        cls.paths_layout, cls.providers = _census_inputs()
        cls.source = FOUNDRY_COMMON.read_text(encoding="utf-8")
        cls.rel = Path("experiments/foundry_common.py")

    def test_the_ProjectPaths_backed_providers_resolve(self):
        got = self.providers["foundry_common"]
        self.assertEqual(got["REPO_ROOT"], ())
        self.assertEqual(got["FOUNDRY_OUT_DIR"], ("experiments", "out", "foundry"))
        self.assertEqual(got["REVIEW_DIR"],
                         ("experiments", "out", "foundry", "review"))

    def test_a_file_chain_provider_still_resolves_by_its_chain(self):
        """The C8.5B guard's MEANING, kept after its live subject was migrated.

        It asserted that the repaired rule does not trade one blind spot for
        another -- it must still read a `Path(__file__)`-derived provider.
        C8.5C removed the last PUBLIC one (`foundry_codebook.REPO_ROOT`), so the
        claim is now carried by two things instead of a deleted test: the
        surviving private bootstrap root, which is still chain-derived, and a
        FIXTURE, so the capability stays guarded even once no live instance
        remains. That is the "a ratified standard with no caller" shape avoided
        rather than repeated."""
        self.assertEqual(self.providers["foundry_codebook"]["_BOOTSTRAP_ROOT"], ())
        fixture = ('from pathlib import Path\n'
                   'REPO_ROOT = Path(__file__).resolve().parents[1]\n'
                   'DATA = REPO_ROOT / "data" / "artifacts" / "latest.json"\n')
        got = layout_census.provider_layout(
            fixture, Path("experiments/fixture.py"), paths_layout={})
        self.assertEqual(got, {"REPO_ROOT": (),
                               "DATA": ("data", "artifacts", "latest.json")})

    def test_the_pre_repair_rule_cannot_see_the_migrated_providers(self):
        """THE DEFECT, kept demonstrable. The chain-only rule finds only the two
        PRIVATE bootstrap names and none of the three public providers."""
        old = layout_census.legacy_chain_provider_layout(self.source, self.rel)
        self.assertEqual(set(old), {"_BOOTSTRAP_ROOT", "_BOOTSTRAP_SRC"})
        for name in ("REPO_ROOT", "FOUNDRY_OUT_DIR", "REVIEW_DIR"):
            self.assertNotIn(name, old)

    def test_the_pre_repair_rule_collapses_the_delegation_census(self):
        """Reproduces the collapse the Manager reported, now complete.

        C8.5B measured 135 -> 1: the single survivor was an expression on
        `foundry_codebook`, the peer provider a chain rule could still see.
        C8.5C migrated it, so the pre-repair rule now finds NO layout provider
        at all and the surface falls 136 -> 0. The guard is strictly stronger
        than the one it replaces -- zero is only reachable because there is no
        longer any independently derived public provider anywhere in legacy
        production, which is exactly what this migration set out to prove."""
        old_providers = {
            m: layout_census.legacy_chain_provider_layout(
                (EXPERIMENTS / f"{m}.py").read_text(encoding="utf-8"),
                Path("experiments") / f"{m}.py")
            for m in layout_census.PROVIDER_MODULES}
        collapsed = repaired = 0
        for rel in layout_census.tracked_python(REPO_ROOT):
            if layout_census.scope_of(rel) not in layout_census.LEGACY_PRODUCTION:
                continue
            source = (REPO_ROOT / rel).read_text(encoding="utf-8")
            collapsed += sum(1 for r in layout_census.delegation_references(
                source, rel, old_providers) if r.form == "PATH_JOIN")
            repaired += sum(1 for r in layout_census.delegation_references(
                source, rel, self.providers) if r.form == "PATH_JOIN")
        self.assertEqual(collapsed, 0)
        self.assertEqual(repaired, CENSUS_HEAD["delegations_by_form"]["PATH_JOIN"])

    def test_a_wrong_ProjectPaths_property_turns_the_guard_red(self):
        """NEGATIVE CONTROL 8. `legacy_experiments_out` is a REAL property and
        the assignment stays a genuine ProjectPaths delegation, so an
        ownership-only check still passes. Resolving to COMPONENTS is what makes
        the wrong value visible. Applied to a source STRING; no file is written."""
        broken = self.source.replace("FOUNDRY_OUT_DIR = _PATHS.legacy_foundry_out",
                                     "FOUNDRY_OUT_DIR = _PATHS.legacy_experiments_out")
        self.assertNotEqual(broken, self.source)
        got = layout_census.provider_layout(broken, self.rel, self.paths_layout)
        self.assertEqual(got["FOUNDRY_OUT_DIR"], ("experiments", "out"))
        self.assertNotEqual(got["FOUNDRY_OUT_DIR"],
                            ("experiments", "out", "foundry"))

    def test_a_wrong_provider_mapping_is_caught_even_with_a_plausible_name(self):
        """The same control aimed at the OTHER half: a property name that does
        not exist resolves to nothing at all, so the provider disappears rather
        than silently resolving somewhere plausible."""
        broken = self.source.replace("_PATHS.legacy_foundry_out",
                                     "_PATHS.legacy_foundry_output")
        got = layout_census.provider_layout(broken, self.rel, self.paths_layout)
        self.assertNotIn("FOUNDRY_OUT_DIR", got)

    def test_a_matching_attribute_on_a_NON_provider_name_is_not_a_delegation(self):
        """The import-alias check is what stops `anything.FOUNDRY_OUT_DIR`
        counting as a delegation. NO corpus row exercises it today -- a mutation
        drill that deleted the check moved zero tests -- so it is guarded by this
        fixture instead of by nothing, which is the house standard for a rule
        that has never been shown to fail."""
        rel = Path("experiments/fixture.py")
        without = ('from types import SimpleNamespace\n'
                   'cfg = SimpleNamespace()\n'
                   'P = cfg.FOUNDRY_OUT_DIR / "x.json"\n')
        self.assertEqual(
            layout_census.delegation_references(without, rel, self.providers), [])
        with_import = 'import foundry_common as cfg\n' + without.split("\n", 2)[2]
        got = layout_census.delegation_references(with_import, rel, self.providers)
        self.assertEqual([(r.alias, r.module, r.name, r.form) for r in got],
                         [("cfg", "foundry_common", "FOUNDRY_OUT_DIR", "PATH_JOIN")])

    def test_a_provider_module_imported_WITHOUT_an_alias_is_still_followed(self):
        got = layout_census.delegation_references(
            'import foundry_common\nP = foundry_common.REVIEW_DIR / "x"\n',
            Path("experiments/fixture.py"), self.providers)
        self.assertEqual([(r.alias, r.name) for r in got],
                         [("foundry_common", "REVIEW_DIR")])

    def test_the_aliases_are_derived_from_the_imports_not_assumed(self):
        consolidate = (EXPERIMENTS / "foundry_consolidate_run1_apply.py"
                       ).read_text(encoding="utf-8")
        self.assertEqual(layout_census.provider_aliases(consolidate).get("fcb"),
                         "foundry_codebook")
        self.assertEqual(
            layout_census.provider_aliases("import foundry_common as anything")
            .get("anything"), "foundry_common")
        self.assertEqual(layout_census.provider_aliases("import json"), {})


class TestTheBlindSpotShapesAreStillDetected(unittest.TestCase):
    """NEGATIVE CONTROLS 1-4. The P0.4N blind spots, aimed at the repaired
    scanner. Each is asserted against a fixture SOURCE STRING and then against a
    live corpus site, so neither the fixture nor the corpus alone is the proof."""

    def test_nc1_module_level_hop1_derivation(self):
        got = layout_census.local_layout_sites(
            'from pathlib import Path\n'
            'ROOT = Path(__file__).resolve().parents[1]\n'
            'OUT = ROOT / "experiments" / "out"\n',
            Path("experiments/fixture.py"))
        self.assertEqual([(s.origin, s.scope) for s in got], [("hop1", "module")])

    def test_nc2_hop2_derived_constant(self):
        got = layout_census.local_layout_sites(
            'from pathlib import Path\n'
            'ROOT = Path(__file__).resolve().parents[1]\n'
            'OUT = ROOT / "experiments"\n'
            'DEEP = OUT / "out" / "foundry"\n',
            Path("experiments/fixture.py"))
        self.assertEqual(sorted(s.origin for s in got), ["hop1", "hop2"])

    def test_nc3_inline_chain_with_no_named_root(self):
        got = layout_census.local_layout_sites(
            'from pathlib import Path\n'
            'DOCS = Path(__file__).resolve().parent.parent / "docs"\n',
            Path("experiments/fixture.py"))
        self.assertEqual([(s.origin, s.scope) for s in got], [("inline", "module")])

    def test_nc4_function_local_derivation(self):
        got = layout_census.local_layout_sites(
            'from pathlib import Path\n'
            'ROOT = Path(__file__).resolve().parents[1]\n'
            'def load():\n'
            '    return (ROOT / "docs" / "x.md").read_text()\n',
            Path("experiments/fixture.py"))
        self.assertEqual([(s.origin, s.scope) for s in got], [("hop1", "load")])

    def test_all_four_shapes_are_attested_live_in_legacy_production(self):
        sites = []
        for rel in layout_census.tracked_python(REPO_ROOT):
            if layout_census.scope_of(rel) not in layout_census.LEGACY_PRODUCTION:
                continue
            sites += layout_census.local_layout_sites(
                (REPO_ROOT / rel).read_text(encoding="utf-8"), rel)
        consumption = [s for s in sites if not s.bootstrap]
        self.assertEqual({s.origin for s in consumption}, {"hop1", "hop2", "inline"})
        self.assertTrue(any(s.scope != "module" for s in consumption))
        self.assertIn(("experiments/foundry_visibility_audit.py", "inline"),
                      [(s.path, s.origin) for s in consumption
                       if s.scope != "module"])

    def test_a_runtime_component_is_not_a_layout_statement(self):
        """`ROOT / name` joins a value the source does not know. It states no
        repository-relative fact, and the ratified checkers already say so.

        This fixture is the corrected aim of a control that first pointed at
        `sys.path.insert(0, str(REPO_ROOT))` -- which contains no join at all, so
        it exercised a different branch than its name claimed and a mutation
        drill showed it could not fail."""
        got = layout_census.local_layout_sites(
            'from pathlib import Path\n'
            'ROOT = Path(__file__).resolve().parents[1]\n'
            'def read(name):\n'
            '    return (ROOT / name).read_text()\n',
            Path("experiments/fixture.py"))
        self.assertEqual(got, [])

    def test_a_root_used_without_a_join_is_not_a_layout_statement(self):
        """53 modules bind `REPO_ROOT` to `experiments` rather than to the
        repository root and re-add it to `sys.path`. Counting those would fill
        the census with non-facts."""
        got = layout_census.local_layout_sites(
            'import sys\nfrom pathlib import Path\n'
            'REPO_ROOT = Path(__file__).resolve().parent\n'
            'sys.path.insert(0, str(REPO_ROOT))\n',
            Path("experiments/fixture.py"))
        self.assertEqual(got, [])

    def test_nesting_is_not_double_counted(self):
        """`ROOT / "a" / "b"` is left-nested; counting every matching BinOp
        scores one site three times. Recorded four times in this arc."""
        got = layout_census.local_layout_sites(
            'from pathlib import Path\n'
            'ROOT = Path(__file__).resolve().parents[1]\n'
            'P = ROOT / "a" / "b" / "c"\n',
            Path("experiments/fixture.py"))
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0].expr, "ROOT / 'a' / 'b' / 'c'")


class TestRealBootstrapCallsAreSeparatedFromText(unittest.TestCase):
    """NEGATIVE CONTROLS 5 and 6."""

    def test_nc5_a_real_sys_path_call_is_detected_and_separated(self):
        source = ('import sys\nfrom pathlib import Path\n'
                  'ROOT = Path(__file__).resolve().parents[1]\n'
                  'sys.path.insert(0, str(ROOT / "experiments"))\n'
                  'OUT = ROOT / "docs"\n')
        rel = Path("experiments/fixture.py")
        self.assertEqual(len(layout_census.sys_path_call_nodes(ast.parse(source))), 1)
        sites = layout_census.local_layout_sites(source, rel)
        self.assertEqual(sorted((s.bootstrap, s.expr) for s in sites),
                         [(False, "ROOT / 'docs'"), (True, "ROOT / 'experiments'")])

    def test_nc6_the_text_inside_a_shell_command_is_not_this_modules_bootstrap(self):
        source = ('import os, sys\nfrom pathlib import Path\n'
                  'ROOT = Path(__file__).resolve().parents[1]\n'
                  'os.system(f"python3 -c \\"import sys; '
                  'sys.path.insert(0, r\'{ROOT / \'experiments\'}\')\\"")\n')
        self.assertEqual(layout_census.sys_path_call_nodes(ast.parse(source)), [])
        self.assertEqual(len(layout_census.sys_path_text_lines(source)), 1)

    def test_the_live_site_that_proves_it_is_still_there(self):
        """P0.4N put this row in the bootstrap bucket on a text match. It is the
        only legacy-production line where the text and the AST disagree."""
        path, lineno = TEXT_ONLY_SYS_PATH
        source = (REPO_ROOT / path).read_text(encoding="utf-8")
        call_lines = {c.lineno for c in
                      layout_census.sys_path_call_nodes(ast.parse(source))}
        self.assertIn(lineno, layout_census.sys_path_text_lines(source))
        self.assertNotIn(lineno, call_lines)

    def test_it_is_the_only_such_line_in_legacy_production(self):
        disagreements = []
        for rel in layout_census.tracked_python(REPO_ROOT):
            if layout_census.scope_of(rel) not in layout_census.LEGACY_PRODUCTION:
                continue
            source = (REPO_ROOT / rel).read_text(encoding="utf-8")
            call_lines = {c.lineno for c in
                          layout_census.sys_path_call_nodes(ast.parse(source))}
            disagreements += [(rel.as_posix(), n)
                              for n in layout_census.sys_path_text_lines(source)
                              if n not in call_lines]
        self.assertEqual(disagreements, [TEXT_ONLY_SYS_PATH])


class TestTheFreshCountsAndTheirReconciliation(unittest.TestCase):
    """The counts, and the proof that raw and scoped are reconciled rather than
    equated. NOT RATCHETS -- a migration is supposed to move them."""

    @classmethod
    def setUpClass(cls):
        _, cls.providers = _census_inputs()
        cls.refs, cls.sites = [], []
        cls.raw = {name: 0 for name in CENSUS_HEAD["delegations_by_provider"]}
        for rel in layout_census.tracked_python(REPO_ROOT):
            if layout_census.scope_of(rel) not in layout_census.LEGACY_PRODUCTION:
                continue
            source = (REPO_ROOT / rel).read_text(encoding="utf-8")
            cls.refs += layout_census.delegation_references(source, rel, cls.providers)
            cls.sites += layout_census.local_layout_sites(source, rel)
            aliases = layout_census.provider_aliases(source)
            for alias, module in aliases.items():
                for name in cls.providers[module]:
                    key = f"{module}.{name}"
                    if key in cls.raw:
                        cls.raw[key] += layout_census.raw_textual_occurrences(
                            source, f"{alias}.{name}")

    def test_the_scoped_delegation_total(self):
        self.assertEqual(len(self.refs), CENSUS_HEAD["delegations_total"])
        by_provider = {}
        for ref in self.refs:
            by_provider[f"{ref.module}.{ref.name}"] = \
                by_provider.get(f"{ref.module}.{ref.name}", 0) + 1
        self.assertEqual(by_provider, CENSUS_HEAD["delegations_by_provider"])
        self.assertEqual(len({r.path for r in self.refs}),
                         CENSUS_HEAD["delegation_files"])

    def test_the_forms_partition_the_total_with_no_remainder(self):
        by_form = {}
        for ref in self.refs:
            by_form[ref.form] = by_form.get(ref.form, 0) + 1
        self.assertEqual(by_form, CENSUS_HEAD["delegations_by_form"])
        self.assertEqual(sum(by_form.values()), CENSUS_HEAD["delegations_total"])
        self.assertNotIn("OTHER", by_form)

    def test_raw_textual_equals_the_scoped_total_and_is_not_ASSUMED_to(self):
        """Inside legacy production these happen to be equal at this head --
        every textual occurrence is a real AST load, none is in a comment or a
        docstring. That is a MEASURED coincidence of this head, so it is
        asserted, not relied on: the two are computed by different means."""
        self.assertEqual(self.raw, CENSUS_HEAD["delegations_by_provider"])
        self.assertEqual(sum(self.raw.values()), len(self.refs))

    def test_the_delegation_excluded_by_the_aq4_pause_is_named_not_hidden(self):
        """AQ4 is PAUSED, so it is excluded by SCOPE rather than absent. Exactly
        ONE delegation sits behind that exclusion and it is named here, so a
        later reader cannot mistake the pause for a clean surface.

        The `tests` bucket also carries the same text many times over -- this
        file is full of it -- and that count is deliberately NOT pinned: it is a
        property of the test suite's own prose, not a fact about production, and
        pinning it would make every future test edit look like a census change.
        """
        excluded = []
        for rel in layout_census.tracked_python(REPO_ROOT):
            if layout_census.scope_of(rel) != "aq4_PAUSED":
                continue
            source = (REPO_ROOT / rel).read_text(encoding="utf-8")
            excluded += layout_census.delegation_references(
                source, rel, self.providers)
        self.assertEqual([(r.path, r.lineno, r.form) for r in excluded],
                         [("experiments/aq4_benchmark/aq4_binding.py", 74,
                           "ATTRIBUTE_NAV")])

    def test_the_local_layout_sites(self):
        bootstrap = [s for s in self.sites if s.bootstrap]
        consumption = [s for s in self.sites if not s.bootstrap]
        self.assertEqual(len(self.sites), CENSUS_HEAD["local_sites_total"])
        self.assertEqual(len(bootstrap), CENSUS_HEAD["local_sites_bootstrap"])
        self.assertEqual(len(consumption), CENSUS_HEAD["local_sites_consumption"])
        origin, scope = {}, {}
        for site in consumption:
            origin[site.origin] = origin.get(site.origin, 0) + 1
            key = "module" if site.scope == "module" else "function"
            scope[key] = scope.get(key, 0) + 1
        self.assertEqual(origin, CENSUS_HEAD["consumption_origin"])
        self.assertEqual(scope, CENSUS_HEAD["consumption_scope"])
        self.assertEqual(sum(origin.values()), sum(scope.values()))
        self.assertEqual(len({s.path for s in consumption}),
                         CENSUS_HEAD["consumption_files"])

    def test_the_real_sys_path_call_sites(self):
        calls = {}
        for rel in layout_census.tracked_python(REPO_ROOT):
            scope = layout_census.scope_of(rel)
            if scope not in layout_census.LEGACY_PRODUCTION:
                continue
            source = (REPO_ROOT / rel).read_text(encoding="utf-8")
            calls[scope] = calls.get(scope, 0) + len(
                layout_census.sys_path_call_nodes(ast.parse(source)))
        self.assertEqual(calls, CENSUS_HEAD["sys_path_calls"])

    def test_the_compatibility_boundary_states_exactly_one_layout_fact(self):
        """The fifth category, kept separate from the other four: what the
        boundary itself still says. One site, and it is the `src` bootstrap --
        the irreducible knowledge needed to LOCATE the owner."""
        sites = [s for s in self.sites
                 if s.path == "experiments/foundry_common.py"]
        self.assertEqual([(s.origin, s.expr) for s in sites],
                         [("hop1", "_BOOTSTRAP_ROOT / 'src'")])
        self.assertEqual(
            len(foundry_common_independent_layout(
                FOUNDRY_COMMON.read_text(encoding="utf-8"))), 1)

    def test_the_boundary_is_not_counted_as_delegating_to_itself(self):
        self.assertEqual([r for r in self.refs
                          if r.path == "experiments/foundry_common.py"], [])


# ===========================================================================
# C8.5C — THE LAST LEGACY LAYOUT PROVIDER
# ===========================================================================
#
# `foundry_codebook` was the second independently derived layout authority in
# legacy production: it exported `REPO_ROOT = Path(__file__).resolve().parents[1]`
# and built `data/artifacts/latest.json` from it, and two expressions in
# `foundry_consolidate_run1_apply` consumed that peer root. C8.5C ends it.
#
# WHY THE ROOT IS NOT SIMPLY BORROWED FROM THE BOUNDARY. Writing
# `fc.REPO_ROOT / "data" / "artifacts" / "latest.json"` would have removed the
# peer PROVIDER while leaving the layout FACT stated outside the owner — the
# same trade C8.5A already refused. The Manager ruled accordingly
# (issue:1#issuecomment-5471643888): `ProjectPaths` names the existing legacy
# directory, `foundry_common` exposes the owned value, and the consumer appends
# only the filename. NAMING IS NOT MOVING — nothing relocated.
#
# What remains in `foundry_codebook` is a PRIVATE `_BOOTSTRAP_ROOT` whose only
# job is putting `experiments` on `sys.path` so `import foundry_common` can
# resolve at all. That is the same irreducible knowledge as C8.5A's `src`
# bootstrap: nothing can import the boundary before knowing where it is.

FOUNDRY_CODEBOOK = EXPERIMENTS / "foundry_codebook.py"
CONSOLIDATE_APPLY = EXPERIMENTS / "foundry_consolidate_run1_apply.py"


def _module_bindings(source: str) -> dict[str, str]:
    """Module-level `NAME = <expr>` as unparsed text, for structural assertions."""
    out = {}
    for statement in ast.parse(source).body:
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name):
                    out[target.id] = ast.unparse(statement.value)
    return out


class TestTheOwnerNamesTheDataArtifactsDirectory(unittest.TestCase):
    """One new ProjectPaths property, and it is pure."""

    def test_it_resolves_to_the_existing_legacy_location(self):
        self.assertEqual(ProjectPaths.for_root("/r").legacy_data_artifacts,
                         Path("/r") / "data" / "artifacts")

    def test_it_touches_no_filesystem(self):
        paths = ProjectPaths.for_root("/definitely/not/a/real/path")
        self.assertFalse(paths.legacy_data_artifacts.exists())
        self.assertTrue(
            str(paths.legacy_data_artifacts).startswith("/definitely"))

    def test_the_static_and_live_resolutions_agree(self):
        """The census parses this property; the package executes it. If those
        two ever disagreed, every C8.5C count would be measured against a
        different directory than the one the code uses."""
        layout = layout_census.project_paths_layout(
            PATHS_SOURCE.read_text(encoding="utf-8"))
        self.assertEqual(layout["legacy_data_artifacts"], ("data", "artifacts"))
        self.assertEqual(
            Path("/r").joinpath(*layout["legacy_data_artifacts"]),
            ProjectPaths.for_root("/r").legacy_data_artifacts)

    def test_it_did_not_disturb_its_siblings(self):
        paths = ProjectPaths.for_root("/r")
        self.assertEqual(paths.legacy_foundry_out,
                         Path("/r/experiments/out/foundry"))
        self.assertEqual(paths.legacy_experiments_out,
                         Path("/r/experiments/out"))
        self.assertNotEqual(paths.legacy_data_artifacts,
                            paths.legacy_experiments_out)


class TestTheBoundaryExposesTheOwnedDirectory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = FOUNDRY_COMMON.read_text(encoding="utf-8")
        cls.fc = load_legacy("foundry_common")

    def test_the_export_comes_from_the_owner_not_from_a_literal(self):
        self.assertEqual(_module_bindings(self.source)["DATA_ARTIFACTS_DIR"],
                         "_PATHS.legacy_data_artifacts")

    def test_it_is_not_derived_from_the_private_bootstrap_names(self):
        """The bootstrap root locates the OWNER. Using it to build a data path
        would make it a general-purpose root, which is the one thing C8.5A's
        guards exist to prevent."""
        binding = _module_bindings(self.source)["DATA_ARTIFACTS_DIR"]
        self.assertNotIn("_BOOTSTRAP_ROOT", binding)
        self.assertNotIn("_BOOTSTRAP_SRC", binding)

    def test_the_live_value_equals_an_independently_built_ProjectPaths(self):
        root = Path(self.fc.__file__).resolve().parents[1]
        paths = ProjectPaths.for_root(root)
        self.assertEqual(self.fc.DATA_ARTIFACTS_DIR, paths.legacy_data_artifacts)
        self.assertEqual(self.fc.DATA_ARTIFACTS_DIR, root / "data" / "artifacts")
        self.assertEqual(str(self.fc.DATA_ARTIFACTS_DIR),
                         str(root / "data" / "artifacts"))

    def test_the_boundary_still_states_exactly_one_layout_fact_of_its_own(self):
        """C8.5C adds an export, not a layout statement. The count must NOT move."""
        got = foundry_common_independent_layout(self.source)
        self.assertEqual(len(got), 1, got)
        self.assertIn("'src'", got[0])

    def test_the_src_bootstrap_and_the_engine_edge_are_untouched(self):
        self.assertIn("_BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]",
                      self.source)
        self.assertIn("if str(_BOOTSTRAP_SRC) not in sys.path:", self.source)
        self.assertIn("sys.path.insert(0, str(_PATHS.legacy_experiments))",
                      self.source)
        top = [n for n in ast.parse(self.source).body if isinstance(n, ast.Import)
               and any(a.name == "tier_engine" for a in n.names)]
        self.assertEqual(len(top), 1)


class TestTheLastPeerProviderIsGone(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = FOUNDRY_CODEBOOK.read_text(encoding="utf-8")
        cls.fcb = load_legacy("foundry_codebook")
        cls.bindings = _module_bindings(cls.source)

    def test_foundry_codebook_exports_no_public_layout_provider(self):
        _, providers = _census_inputs()
        public = [n for n in providers["foundry_codebook"]
                  if not n.startswith("_")]
        self.assertEqual(public, [])

    def test_the_module_no_longer_defines_a_public_REPO_ROOT(self):
        self.assertNotIn("REPO_ROOT", self.bindings)
        self.assertFalse(hasattr(self.fcb, "REPO_ROOT"))

    def test_the_surviving_root_is_private_and_still_the_same_derivation(self):
        self.assertEqual(self.bindings["_BOOTSTRAP_ROOT"],
                         "Path(__file__).resolve().parents[1]")

    def test_the_private_root_is_used_for_exactly_one_thing(self):
        """Structural, not a line-distance heuristic: every LOAD of the private
        root must occur in the single `sys.path.insert` statement. A second use
        would be it becoming a general-purpose root again."""
        loads = []
        for statement in ast.parse(self.source).body:
            for node in ast.walk(statement):
                if (isinstance(node, ast.Name) and node.id == "_BOOTSTRAP_ROOT"
                        and isinstance(node.ctx, ast.Load)):
                    loads.append(ast.unparse(statement))
                    break
        self.assertEqual(
            loads, ["sys.path.insert(0, str(_BOOTSTRAP_ROOT / 'experiments'))"])

    def test_the_artifact_path_now_delegates_to_the_boundary(self):
        self.assertEqual(self.bindings["LATEST_ARTIFACT_PATH"],
                         "fc.DATA_ARTIFACTS_DIR / 'latest.json'")

    def test_the_consumer_appends_only_the_filename(self):
        """The whole point of the Manager's ruling: no repository-relative
        DIRECTORY literal is restated outside the owner. `latest.json` is a file
        name, not layout."""
        binding = self.bindings["LATEST_ARTIFACT_PATH"]
        for directory in ("'data'", '"data"', "'artifacts'", '"artifacts"'):
            self.assertNotIn(directory, binding)

    def test_the_codebook_paths_still_delegate_as_before(self):
        self.assertEqual(self.bindings["CODEBOOK_PATH"],
                         "fc.FOUNDRY_OUT_DIR / 'codebook.json'")
        self.assertEqual(self.bindings["BACKUPS_DIR"],
                         "fc.FOUNDRY_OUT_DIR / 'backups'")

    def test_every_value_is_byte_identical_to_its_pre_change_construction(self):
        root = Path(load_legacy("foundry_common").__file__).resolve().parents[1]
        expected = {
            "CODEBOOK_PATH": root / "experiments" / "out" / "foundry" / "codebook.json",
            "BACKUPS_DIR": root / "experiments" / "out" / "foundry" / "backups",
            "LATEST_ARTIFACT_PATH": root / "data" / "artifacts" / "latest.json",
        }
        for name, want in expected.items():
            with self.subTest(name=name):
                self.assertEqual(getattr(self.fcb, name), want)
                self.assertEqual(str(getattr(self.fcb, name)), str(want))

    def test_the_sys_path_bootstrap_inserts_the_same_directory_at_the_same_place(self):
        calls = layout_census.sys_path_call_nodes(ast.parse(self.source))
        self.assertEqual(len(calls), 1)
        self.assertEqual(ast.unparse(calls[0]),
                         "sys.path.insert(0, str(_BOOTSTRAP_ROOT / 'experiments'))")
        self.assertEqual(calls[0].args[0].value, 0)

    def test_the_bootstrap_precedes_the_boundary_import(self):
        """It has to: the insert is what makes `import foundry_common` resolve."""
        lines = self.source.splitlines()
        insert = next(i for i, l in enumerate(lines) if "sys.path.insert" in l)
        boundary = next(i for i, l in enumerate(lines)
                        if l.startswith("import foundry_common as fc"))
        self.assertLess(insert, boundary)

    def test_it_is_labelled_temporary_and_non_authoritative(self):
        head = self.source.split("SCHEMA_V2")[0]
        self.assertIn("C8.5C COMPATIBILITY BOOTSTRAP", head)
        self.assertIn("TEMPORARY", head)
        self.assertIn("NOT A LAYOUT API", head)


class TestTheDownstreamPeerConsumersAreGone(unittest.TestCase):
    def test_no_tracked_file_anywhere_consumes_the_peer_root(self):
        """ALL scopes, not just legacy production, and through each file's own
        import aliases rather than a text match."""
        found = []
        for rel in layout_census.tracked_python(REPO_ROOT):
            source = (REPO_ROOT / rel).read_text(encoding="utf-8")
            aliases = {a for n in ast.walk(ast.parse(source))
                       if isinstance(n, ast.Import) for a in
                       [x.asname or x.name for x in n.names
                        if x.name == "foundry_codebook"]}
            for node in ast.walk(ast.parse(source)):
                if (isinstance(node, ast.Attribute) and node.attr == "REPO_ROOT"
                        and isinstance(node.value, ast.Name)
                        and node.value.id in aliases):
                    found.append(f"{rel}:{node.lineno}")
        self.assertEqual(found, [])

    def test_the_two_sites_now_read_from_the_compatibility_boundary(self):
        source = CONSOLIDATE_APPLY.read_text(encoding="utf-8")
        rows = [f"{n.lineno}: {ast.unparse(n)}"
                for n in ast.walk(ast.parse(source))
                if isinstance(n, ast.Attribute) and n.attr == "REPO_ROOT"
                and isinstance(n.value, ast.Name) and n.value.id == "fc"]
        self.assertEqual(len(rows), 2, rows)
        self.assertEqual(_module_bindings(source)["GAMECHANGERS_PATH"],
                         "fc.REPO_ROOT / 'tags' / 'gamechangers.yaml'")

    def test_it_needed_no_new_import(self):
        source = CONSOLIDATE_APPLY.read_text(encoding="utf-8")
        self.assertIn("import foundry_common as fc", source)

    def test_the_relative_to_value_is_unchanged(self):
        """The one delegation that is not a path construction. `relative_to`
        returns a DIFFERENT object depending on the root it is given, so the
        two roots must be equal as Path AND as str, not merely resolve nearby."""
        fc = load_legacy("foundry_common")
        root = Path(fc.__file__).resolve().parents[1]
        stale = root / "experiments" / "out" / "foundry" / \
            "corpus_pass_run1_consolidation_dry_run.json"
        self.assertEqual(fc.REPO_ROOT, root)
        self.assertEqual(str(fc.REPO_ROOT), str(root))
        self.assertEqual(
            str(stale.relative_to(fc.REPO_ROOT)),
            "experiments/out/foundry/corpus_pass_run1_consolidation_dry_run.json")

    def test_every_scoped_delegation_now_terminates_at_one_boundary(self):
        """The transition claim, asserted rather than narrated."""
        _, providers = _census_inputs()
        modules = set()
        for rel in layout_census.tracked_python(REPO_ROOT):
            if layout_census.scope_of(rel) not in layout_census.LEGACY_PRODUCTION:
                continue
            source = (REPO_ROOT / rel).read_text(encoding="utf-8")
            modules |= {r.module for r in layout_census.delegation_references(
                source, rel, providers)}
        self.assertEqual(modules, {"foundry_common"})

    def test_the_remaining_data_artifacts_site_is_named_not_hidden(self):
        """`foundry_verify_migration.py` builds its OWN
        `data/artifacts/latest.json` from a local root. It is outside this
        task's authorized scope — P0.4P assigns that module to step 8 — so it
        is recorded here rather than left to look like absence. It is one of the
        60 remaining local consumption sites."""
        source = (EXPERIMENTS / "foundry_verify_migration.py").read_text(
            encoding="utf-8")
        self.assertIn('LATEST_ARTIFACT_PATH = REPO_ROOT / "data" / "artifacts"'
                      ' / "latest.json"', source)


class TestC85CNegativeControls(unittest.TestCase):
    """The four controls the task requires, aimed at the exact changed property
    rather than at a name. Each mutates a SOURCE STRING in memory; no file is
    written."""

    @classmethod
    def setUpClass(cls):
        cls.paths_source = PATHS_SOURCE.read_text(encoding="utf-8")
        cls.paths_layout = layout_census.project_paths_layout(cls.paths_source)
        cls.codebook = FOUNDRY_CODEBOOK.read_text(encoding="utf-8")
        cls.common = FOUNDRY_COMMON.read_text(encoding="utf-8")
        cls.rel = Path("experiments/foundry_codebook.py")

    def test_NC1_reverting_the_artifact_path_to_a_local_construction_is_caught(self):
        broken = self.codebook.replace(
            'LATEST_ARTIFACT_PATH = fc.DATA_ARTIFACTS_DIR / "latest.json"',
            'LATEST_ARTIFACT_PATH = _BOOTSTRAP_ROOT / "data" / "artifacts"'
            ' / "latest.json"')
        self.assertNotEqual(broken, self.codebook)

        # the module states a repository-relative layout fact again
        sites = layout_census.local_layout_sites(broken, self.rel)
        consumption = [s for s in sites if not s.bootstrap]
        self.assertEqual(len(consumption), 1)
        self.assertEqual(consumption[0].expr,
                         "_BOOTSTRAP_ROOT / 'data' / 'artifacts' / 'latest.json'")
        # and the private root is used for a second thing
        loads = []
        for statement in ast.parse(broken).body:
            for node in ast.walk(statement):
                if (isinstance(node, ast.Name) and node.id == "_BOOTSTRAP_ROOT"
                        and isinstance(node.ctx, ast.Load)):
                    loads.append(ast.unparse(statement))
                    break
        self.assertEqual(len(loads), 2)
        # the true state has neither
        self.assertEqual(
            [s for s in layout_census.local_layout_sites(self.codebook, self.rel)
             if not s.bootstrap], [])

    def test_NC2_a_wrong_but_REAL_directory_is_caught_by_VALUE_not_ownership(self):
        """`data/cache` is a real legacy directory, so the assignment stays a
        genuine ProjectPaths delegation and an ownership-only check is still
        GREEN. Only resolving to components sees it."""
        broken_paths = self.paths_source.replace(
            'return self.root / "data" / "artifacts"',
            'return self.root / "data" / "cache"')
        self.assertNotEqual(broken_paths, self.paths_source)
        broken_layout = layout_census.project_paths_layout(broken_paths)

        # OWNERSHIP arm: unchanged and still satisfied
        self.assertEqual(_module_bindings(self.common)["DATA_ARTIFACTS_DIR"],
                         "_PATHS.legacy_data_artifacts")
        self.assertIn("legacy_data_artifacts", broken_layout)

        # VALUE arm: red
        self.assertEqual(broken_layout["legacy_data_artifacts"], ("data", "cache"))
        self.assertNotEqual(broken_layout["legacy_data_artifacts"],
                            ("data", "artifacts"))
        providers = layout_census.provider_layout(
            self.common, Path("experiments/foundry_common.py"), broken_layout)
        self.assertEqual(providers["DATA_ARTIFACTS_DIR"], ("data", "cache"))
        self.assertNotEqual(providers["DATA_ARTIFACTS_DIR"],
                            self.paths_layout["legacy_data_artifacts"])

    def test_NC3_restoring_a_public_peer_provider_is_caught(self):
        broken = self.codebook.replace(
            "_BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]",
            "REPO_ROOT = Path(__file__).resolve().parents[1]").replace(
            "str(_BOOTSTRAP_ROOT / \"experiments\")", 'str(REPO_ROOT / "experiments")')
        self.assertNotEqual(broken, self.codebook)
        providers = layout_census.provider_layout(
            broken, self.rel, self.paths_layout)
        public = [n for n in providers if not n.startswith("_")]
        self.assertEqual(public, ["REPO_ROOT"])
        self.assertEqual(providers["REPO_ROOT"], ())
        # the true state has no public provider at all
        self.assertEqual(
            [n for n in layout_census.provider_layout(
                self.codebook, self.rel, self.paths_layout)
             if not n.startswith("_")], [])

    def test_NC4_restoring_a_downstream_peer_consumer_is_caught(self):
        """Aimed at the census, not at the text: the restored expression must be
        counted as a delegation to `foundry_codebook` again."""
        rel = Path("experiments/foundry_consolidate_run1_apply.py")
        source = CONSOLIDATE_APPLY.read_text(encoding="utf-8")
        broken = source.replace(
            'GAMECHANGERS_PATH = fc.REPO_ROOT / "tags" / "gamechangers.yaml"',
            'GAMECHANGERS_PATH = fcb.REPO_ROOT / "tags" / "gamechangers.yaml"')
        self.assertNotEqual(broken, source)
        # a peer provider must exist for the reference to resolve, which is the
        # NC3 state; the two failures compose exactly as the real regression would
        peer = layout_census.provider_layout(
            self.codebook.replace(
                "_BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]",
                "REPO_ROOT = Path(__file__).resolve().parents[1]"),
            self.rel, self.paths_layout)
        providers = {"foundry_common": layout_census.provider_layout(
            self.common, Path("experiments/foundry_common.py"), self.paths_layout),
            "foundry_codebook": peer}
        refs = layout_census.delegation_references(broken, rel, providers)
        peers = [r for r in refs if r.module == "foundry_codebook"]
        self.assertEqual([(r.lineno, r.name, r.form) for r in peers],
                         [(697, "REPO_ROOT", "PATH_JOIN")])
        # the true state has none
        self.assertEqual(
            [r for r in layout_census.delegation_references(
                source, rel, providers) if r.module == "foundry_codebook"], [])


# ===========================================================================
# C8.5E — THE PACKAGE EXECUTION CONTRACT, AND ITS PARITY WITH SOURCE
# ===========================================================================
#
# `refoundation/PACKAGE-EXECUTION-CONTRACT.yaml` declares which execution
# contexts may be relied on, and the deletion prerequisite for every temporary
# bootstrap standing in for a real installation. A contract nobody checks is the
# shape this repository has been burned by three times -- a ratified token with
# no emitter, a ratified standard with no caller, a register naming a fix nobody
# did. So the family table is DERIVED FROM SOURCE here and compared against the
# document in BOTH directions: a family in source with no contract entry fails,
# and a contract entry naming no real family fails.
#
# NOTHING HERE DELETES A BOOTSTRAP. The families are pinned so that a later
# slice cannot remove one quietly, and cannot invent one either.

CONTRACT_PATH = REPO_ROOT / "refoundation" / "PACKAGE-EXECUTION-CONTRACT.yaml"

# Pinned at aa003340. Keys are what the sys.path call ADDS, relative to the
# repository root; "" is the root itself. NOT a ratchet -- a later slice that
# legitimately deletes a bootstrap is expected to move these, in a diff.
BOOTSTRAP_FAMILIES = {"src": 1, "experiments": 87, "": 1}
BOOTSTRAP_TOTAL = 89


def _resolve_path_expr(expr, rel, names, paths_instances, paths_layout):
    """Repository-relative components an expression denotes, or None.

    Deliberately small and local to this file: `layout_census` is FROZEN by the
    C8.5E task, and this needs to resolve a `sys.path` ARGUMENT, which the census
    never had to do. It reuses the census's ascent arithmetic rather than
    restating it -- re-implementing that is the exact defect C8.5B.R1 repaired.
    """
    if (isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name)
            and expr.func.id == "str" and expr.args):
        return _resolve_path_expr(expr.args[0], rel, names, paths_instances,
                                  paths_layout)
    if isinstance(expr, ast.Name):
        return names.get(expr.id)
    if (isinstance(expr, ast.Attribute) and isinstance(expr.value, ast.Name)
            and expr.value.id in paths_instances):
        return paths_layout.get(expr.attr)
    hops = layout_census._file_chain_hops(expr)
    if hops is not None:
        return layout_census._root_relative(rel, hops)
    if (isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Div)
            and isinstance(expr.right, ast.Constant)
            and isinstance(expr.right.value, str)):
        base = _resolve_path_expr(expr.left, rel, names, paths_instances,
                                  paths_layout)
        return None if base is None else base + (expr.right.value,)
    return None


def bootstrap_sites(source: str, rel: Path, paths_layout) -> list[tuple[str, str]]:
    """`(what it adds, "path:lineno")` for every REAL sys.path call in a module.

    "What it adds" is the RESOLVED directory, not the spelling. 53 modules bind
    `REPO_ROOT` to their own directory and insert that; others join the literal
    `"experiments"` onto a repository root. Those are the same family and a
    spelling-based census would report two.
    """
    tree = ast.parse(source)
    instances = {t.id for st in tree.body if isinstance(st, ast.Assign)
                 for t in st.targets if isinstance(t, ast.Name)
                 and isinstance(st.value, ast.Call)
                 and isinstance(st.value.func, ast.Attribute)
                 and st.value.func.attr == "for_root"}
    names: dict[str, tuple[str, ...]] = {}
    for _ in range(4):
        for st in ast.walk(tree):
            if not isinstance(st, ast.Assign):
                continue
            value = _resolve_path_expr(st.value, rel, names, instances, paths_layout)
            if value is None:
                continue
            for target in st.targets:
                if isinstance(target, ast.Name):
                    names[target.id] = value
    found = []
    for call in layout_census.sys_path_call_nodes(tree):
        value = _resolve_path_expr(call.args[-1], rel, names, instances, paths_layout)
        found.append((None if value is None else "/".join(value),
                      f"{rel.as_posix()}:{call.lineno}"))
    return found


def source_bootstrap_families():
    """`{what it adds: [sites]}` across all of legacy production."""
    paths_layout = layout_census.project_paths_layout(
        PATHS_SOURCE.read_text(encoding="utf-8"))
    families: dict[str, list[str]] = {}
    for rel in layout_census.tracked_python(REPO_ROOT):
        if layout_census.scope_of(rel) not in layout_census.LEGACY_PRODUCTION:
            continue
        for adds, where in bootstrap_sites(
                (REPO_ROOT / rel).read_text(encoding="utf-8"), rel, paths_layout):
            families.setdefault(adds, []).append(where)
    return families


def contract_bootstrap_families(text: str) -> dict[str, dict]:
    """Read the `bootstrap_families:` block. Stdlib only, by design.

    This tree may not import PyYAML (P0.3A: do not pin a legacy dependency), so
    this is a targeted reader for one known block, not a YAML parser -- the same
    posture as `helpers.scalars`.
    """
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines)
                 if l.startswith("bootstrap_families:"))
    entries: dict[str, dict] = {}
    current = None
    for line in lines[start + 1:]:
        if line and not line[0].isspace() and not line.startswith("#"):
            break
        stripped = line.strip()
        if stripped.startswith("- id:"):
            current = {"id": stripped.split(":", 1)[1].strip(), "site_list": []}
            entries[current["id"]] = current
        elif current is None or not stripped or stripped.startswith("#"):
            continue
        elif stripped.startswith("adds:"):
            current["adds"] = stripped.split(":", 1)[1].strip().strip("'\"")
        elif stripped.startswith("sites:"):
            current["sites"] = int(stripped.split(":", 1)[1].strip())
        elif stripped.startswith("deletion_prerequisite:"):
            current["deletion_prerequisite"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("site_list:"):
            current["site_list_literal"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("- ") and ":" in stripped and current is not None:
            token = stripped[2:].strip()
            if token.rsplit(":", 1)[-1].isdigit():
                current["site_list"].append(token)
    return entries


class TestTheBootstrapFamiliesArePinned(unittest.TestCase):
    """Derived from source, so a deleted or invented bootstrap is visible."""

    @classmethod
    def setUpClass(cls):
        cls.families = source_bootstrap_families()

    def test_every_sys_path_call_resolves_to_a_known_directory(self):
        """No unresolved remainder. An unresolvable argument would be a family
        the contract cannot describe, and it would hide there."""
        self.assertNotIn(None, self.families)
        self.assertEqual(sum(len(v) for v in self.families.values()),
                         BOOTSTRAP_TOTAL)

    def test_the_families_are_exactly_the_pinned_three(self):
        self.assertEqual({k: len(v) for k, v in self.families.items()},
                         BOOTSTRAP_FAMILIES)

    def test_the_package_location_family_is_the_single_C8_5A_bootstrap(self):
        self.assertEqual(self.families["src"], ["experiments/foundry_common.py:34"])

    def test_the_root_dotted_family_is_the_single_deferred_bootstrap(self):
        """The only site that adds the repository root, and the only one inside
        a function. It exists for `import experiments.tier_engine`."""
        self.assertEqual(self.families[""], ["experiments/snapshot.py:111"])
        source = (EXPERIMENTS / "snapshot.py").read_text(encoding="utf-8")
        enclosing = [n.name for n in ast.walk(ast.parse(source))
                     if isinstance(n, ast.FunctionDef)
                     and n.lineno <= 111 <= n.end_lineno]
        self.assertEqual(enclosing, ["collect_ruling_constants"])
        self.assertIn("import experiments.tier_engine", source)

    def test_spelling_does_not_split_a_family(self):
        """The `experiments` family is spelled two ways -- a repository-relative
        join and a module re-adding its own directory -- and both resolve to the
        same directory. A spelling-based census would report two families."""
        sites = self.families["experiments"]
        joined = [s for s in sites if "REPO_ROOT / " in
                  (REPO_ROOT / s.split(":")[0]).read_text(encoding="utf-8")
                  .splitlines()[int(s.split(":")[1]) - 1]]
        self.assertTrue(joined)
        self.assertLess(len(joined), len(sites))


class TestTheContractMatchesSource(unittest.TestCase):
    """Parity in BOTH directions, which is the only version that is a guard."""

    @classmethod
    def setUpClass(cls):
        cls.text = CONTRACT_PATH.read_text(encoding="utf-8")
        cls.contract = contract_bootstrap_families(cls.text)
        cls.families = source_bootstrap_families()

    def test_the_contract_declares_its_schema_and_disclaims_self_authority(self):
        self.assertIn("schema: mtj-package-execution-contract/1", self.text)
        self.assertIn("self_authority: false", self.text)

    def test_every_source_family_has_a_contract_entry(self):
        declared = {e["adds"] for e in self.contract.values()}
        self.assertEqual(declared, set(self.families))

    def test_no_contract_entry_names_a_family_that_does_not_exist(self):
        for entry in self.contract.values():
            with self.subTest(family=entry["id"]):
                self.assertIn(entry["adds"], self.families)

    def test_the_declared_counts_match_the_measured_counts(self):
        for entry in self.contract.values():
            with self.subTest(family=entry["id"]):
                self.assertEqual(entry["sites"], len(self.families[entry["adds"]]))

    def test_an_enumerated_site_list_matches_source_exactly(self):
        for entry in self.contract.values():
            if not entry["site_list"]:
                continue
            with self.subTest(family=entry["id"]):
                self.assertEqual(sorted(entry["site_list"]),
                                 sorted(self.families[entry["adds"]]))

    def test_every_family_carries_a_deletion_prerequisite(self):
        for entry in self.contract.values():
            with self.subTest(family=entry["id"]):
                self.assertTrue(entry.get("deletion_prerequisite"),
                                "a family with no deletion prerequisite is debt "
                                "with no exit")

    def test_the_three_contexts_are_declared_with_distinct_status(self):
        for context, status in (("INSTALLED_PACKAGE", "SUPPORTED_PERMANENT"),
                                ("LEGACY_LOOSE_SCRIPT_BOOTSTRAP",
                                 "SUPPORTED_TRANSITIONAL"),
                                ("EXPLICIT_SOURCE_LAYOUT",
                                 "DEVELOPMENT_DIAGNOSTIC_ONLY")):
            with self.subTest(context=context):
                self.assertIn(f"id: {context}", self.text)
                self.assertIn(f"status: {status}", self.text)

    def test_the_non_claims_are_present(self):
        for claim in ("NOT_A_DEPENDENCY_MIGRATION",
                      "NOT_AUTHORIZATION_TO_MOVE_A_SUBSYSTEM",
                      "NOT_A_BOOTSTRAP_DELETION",
                      "INSTALL_ARTIFACTS_ARE_NOT_SOURCE"):
            with self.subTest(claim=claim):
                self.assertIn(claim, self.text)

    def test_it_records_that_nothing_moved(self):
        for line in ("bootstraps_deleted: 0", "legacy_modules_moved: 0",
                     "production_python_changed: 0",
                     "layout_census_movement: ZERO"):
            self.assertIn(line, self.text)


class TestTheContractParityGuardActuallyFires(unittest.TestCase):
    """NEGATIVE CONTROLS. Each mutates the contract TEXT in memory; no file is
    written. Aimed at the parity computation, not at the words."""

    @classmethod
    def setUpClass(cls):
        cls.text = CONTRACT_PATH.read_text(encoding="utf-8")
        cls.families = source_bootstrap_families()

    def test_omitting_a_real_family_is_caught(self):
        broken = self.text.replace("""  - id: LEGACY_ROOT_DOTTED_IMPORT
    adds: ''
    sites: 1""", "  - id: PLACEHOLDER_REMOVED\n    adds: src\n    sites: 1")
        self.assertNotEqual(broken, self.text)
        declared = {e["adds"] for e in contract_bootstrap_families(broken).values()}
        self.assertNotEqual(declared, set(self.families))
        self.assertNotIn("", declared)

    def test_inventing_a_family_that_does_not_exist_is_caught(self):
        broken = self.text.replace("bootstrap_families:\n", """bootstrap_families:

  - id: INVENTED_FAMILY
    adds: pipeline
    sites: 3
    site_list:
      - experiments/nowhere.py:1
    deletion_prerequisite: 'none — this family does not exist'
""")
        self.assertNotEqual(broken, self.text)
        entries = contract_bootstrap_families(broken)
        self.assertIn("INVENTED_FAMILY", entries)
        self.assertNotIn(entries["INVENTED_FAMILY"]["adds"], self.families)

    def test_a_wrong_site_count_is_caught(self):
        broken = self.text.replace("    adds: experiments\n    sites: 87",
                                   "    adds: experiments\n    sites: 86")
        self.assertNotEqual(broken, self.text)
        entry = next(e for e in contract_bootstrap_families(broken).values()
                     if e["adds"] == "experiments")
        self.assertNotEqual(entry["sites"], len(self.families["experiments"]))

    def test_a_wrong_enumerated_site_is_caught(self):
        broken = self.text.replace("      - experiments/foundry_common.py:34",
                                   "      - experiments/foundry_common.py:35")
        self.assertNotEqual(broken, self.text)
        entry = next(e for e in contract_bootstrap_families(broken).values()
                     if e["adds"] == "src")
        self.assertNotEqual(sorted(entry["site_list"]),
                            sorted(self.families["src"]))

    def test_the_unmutated_contract_passes_every_one_of_those_checks(self):
        """The controls above assert INEQUALITY, so they would all pass against a
        contract that is wrong in some other way. This is the positive arm."""
        entries = contract_bootstrap_families(self.text)
        self.assertEqual({e["adds"] for e in entries.values()}, set(self.families))
        for entry in entries.values():
            self.assertEqual(entry["sites"], len(self.families[entry["adds"]]))
            if entry["site_list"]:
                self.assertEqual(sorted(entry["site_list"]),
                                 sorted(self.families[entry["adds"]]))


if __name__ == "__main__":
    unittest.main()
