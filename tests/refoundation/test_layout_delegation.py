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

COVERING_GATE2_ROWS = ("ground_truth", "ground_truth_wide", "probe_guards")


# ---------------------------------------------------------------------------
# The property, expressed once so a negative control can aim at it
# ---------------------------------------------------------------------------


def independent_codebook_constructions(source: str) -> list[str]:
    """Sites that rebuild the foundry-out path instead of delegating to it.

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


def delegating_expressions(source: str) -> list[str]:
    """Occurrences of `fc.FOUNDRY_OUT_DIR / "codebook.json"`."""
    found = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Div):
            continue
        if not (isinstance(node.right, ast.Constant)
                and node.right.value == "codebook.json"):
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
                    independent_codebook_constructions(path.read_text(encoding="utf-8")),
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
                findings = independent_codebook_constructions(reverted)
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
        """`GRAMMAR` sits on the line after the migrated `CODEBOOK` and is a
        root-relative docs path. It is a real ownership site and it is
        deliberately NOT in this slice."""
        source = PROBE.read_text(encoding="utf-8")
        self.assertIn('GRAMMAR = REPO_ROOT.parent / "docs" / '
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


if __name__ == "__main__":
    unittest.main()
