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
import unittest
from pathlib import Path

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

    def test_moves_is_untouched(self):
        self.assertIn('MOVES = REPO_ROOT / "moves"',
                      GROUND_TRUTH.read_text(encoding="utf-8"))

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
        self.assertIn('FOUNDRY_OUT_DIR = REPO_ROOT / "experiments" / "out" '
                      '/ "foundry"', source)

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

    def test_slug_reparse_grammar_is_untouched(self):
        """It sits on the line ABOVE the migrated CODEBOOK and is a
        root-relative docs path — a real ownership site, deliberately out of
        slice."""
        self.assertIn('GRAMMAR = REPO_ROOT.parent / "docs" / '
                      '"CODEBOOK-NAMING-GRAMMAR.md"',
                      SLUG_REPARSE.read_text(encoding="utf-8"))
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
        self.assertIn('FOUNDRY_OUT_DIR = REPO_ROOT / "experiments" / "out" '
                      '/ "foundry"',
                      (EXPERIMENTS / "foundry_common.py").read_text(encoding="utf-8"))

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
        self.assertIn('REPO_ROOT = Path(__file__).resolve().parents[1]',
                      (EXPERIMENTS / "foundry_common.py").read_text(encoding="utf-8"))

    def test_the_two_covering_gate2_rows_are_unchanged(self):
        argv = {name: a for name, a, _ in gate_rows()}
        self.assertEqual(argv["reachability"],
                         ["experiments/foundry_reachability.py"])
        self.assertEqual(argv["probe_guards"], ["experiments/foundry_probe.py"])


if __name__ == "__main__":
    unittest.main()
