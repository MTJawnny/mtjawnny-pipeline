"""C8 step 3, third slice: a VERIFICATION NEGATIVE CONTROL may not touch tracked state.

Stdlib only, like the rest of this tree.

P0.3E made a normal Gate 2 run pure. It left one thing open, and the P0.3E review
named it: `foundry_reachability.py --selftest` proved its negative control by
writing a synthetic section into the ratchet baseline with `baseline.save()` and
deleting it again in a `finally`.

That was tolerable while the baseline was an ignored local file. **P0.3D made it a
TRACKED control input**, and the arrangement then had two defects that a green run
could not show:

  1. The tracked file that decides whether a standing audit degraded was rewritten
     TWICE by a verification run — once to inject the synthetic pin, once to remove
     it. Verification mutated its own acceptance input.
  2. The removal is a CLEANUP WRITE, so the guarantee was only as good as the
     process surviving to run it. An interrupt between the two writes leaves the
     tracked ratchet carrying a `reachability_selftest` section that nobody put
     there on purpose.

The fix is a different WRITE TARGET, not a more careful cleanup: the synthetic pin
now goes to a temporary control input outside the repository, and
`foundry_audit_baseline.BASELINE` is rebound at it BEFORE anything is written. The
tracked baseline is never the write target at any instant, so there is no window
for an interrupt to land in.

**What must NOT change is what the control PROVES.** `save()` and `compare()` are
still the real ones, so `WORSE_IF_DOWN` and `_direction()` still decide whether the
synthetic lost wire is fatal. A control that reimplemented that comparison would be
a copy of the comparator instead of a test of it.
"""

from __future__ import annotations

import ast
import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT
from tests.refoundation.test_gate2_purity import (
    PurityGuard,
    gate_rows,
    load_legacy,
    snapshot,
)

from mtj_foundry.paths import ProjectPaths

PATHS = ProjectPaths.for_root(REPO_ROOT)
EXPERIMENTS = PATHS.legacy_experiments
RATCHET = PATHS.baselines / "foundry-audit-baseline.json"
REACHABILITY = EXPERIMENTS / "foundry_reachability.py"

SELFTEST_SECTION = "reachability_selftest"


def selftest_ast() -> ast.FunctionDef:
    """The `selftest` function, read WITHOUT importing the module."""
    tree = ast.parse(REACHABILITY.read_text(encoding="utf-8"))
    return next(n for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name == "selftest")


# ---------------------------------------------------------------------------
# The structural property, expressed once so a negative control can aim at it
# ---------------------------------------------------------------------------


def purity_violations(source: str) -> list[str]:
    """Ways `selftest` could still reach the TRACKED ratchet, as findings.

    A checker, not an assertion, so the tests below can run it against a
    deliberately reverted source and require it to FIRE. "A guard that has never
    been shown to fail is not known to be a guard."
    """
    tree = ast.parse(source)
    fn = next((n for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef) and n.name == "selftest"), None)
    if fn is None:
        return ["selftest is not defined"]

    findings = []

    # 1. A direct write through the module attribute, whatever it is bound to.
    for node in ast.walk(fn):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("write_text", "write_bytes", "open")
                and "BASELINE" in ast.unparse(node.func.value)):
            findings.append(f"line {node.lineno}: direct write to baseline.BASELINE")

    # 2. The rebind must exist, and must LEXICALLY PRECEDE every call that
    #    writes through the comparator. A rebind that happens after the first
    #    `save()` would put the tracked file back in the line of fire, which is
    #    exactly the state this slice removes.
    rebinds = [n.lineno for n in ast.walk(fn)
               if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Attribute) and t.attr == "BASELINE"
                       for t in n.targets)]
    writes = [n.lineno for n in ast.walk(fn)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
              and n.func.attr == "save"]
    if writes and not rebinds:
        findings.append("baseline.save() is called and BASELINE is never rebound")
    elif writes and min(rebinds) > min(writes):
        findings.append("baseline.save() is reached before BASELINE is rebound")

    # 3. The rebind must be RESTORED on every path, including a raised one.
    if rebinds and not any(isinstance(n, ast.Try) and n.finalbody
                           for n in ast.walk(fn)):
        findings.append("BASELINE is rebound without a finally that restores it")

    return findings


class TestTheSelftestCannotReachTheTrackedRatchet(unittest.TestCase):
    """Structure. Says where the write can possibly go, before anything runs."""

    def test_the_live_selftest_has_no_purity_violations(self):
        self.assertEqual(purity_violations(REACHABILITY.read_text(encoding="utf-8")),
                         [])

    def test_the_synthetic_pin_goes_to_a_temporary_file(self):
        source = ast.unparse(selftest_ast())
        self.assertIn("tempfile", source)
        self.assertIn("baseline.BASELINE = tmp", source)

    def test_the_rebind_is_restored_in_a_finally(self):
        fn = selftest_ast()
        tries = [n for n in ast.walk(fn) if isinstance(n, ast.Try) and n.finalbody]
        self.assertTrue(tries)
        restored = "\n".join(ast.unparse(s) for t in tries for s in t.finalbody)
        self.assertIn("baseline.BASELINE = real_baseline", restored)

    def test_the_rebind_targets_the_module_the_comparator_reads(self):
        """Not this file's globals.

        "A module run as __main__ is a second, separate copy of itself, and
        monkeypatching the wrong one reads as a passing test." The attribute is
        set on the imported `foundry_audit_baseline` object — which is never
        __main__, so it has exactly one instance — and `_document()` reads
        `BASELINE` at call time.
        """
        source = ast.unparse(selftest_ast())
        self.assertNotIn('globals()["BASELINE"]', source)
        self.assertNotIn("global BASELINE", source)
        assigns = [n for n in ast.walk(selftest_ast())
                   if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Attribute) and t.attr == "BASELINE"
                           for t in n.targets)]
        self.assertEqual(len(assigns), 2)  # rebind, and the restore
        for node in assigns:
            target = node.targets[0]
            self.assertEqual(ast.unparse(target.value), "baseline")

    def test_the_comparison_is_not_reimplemented_here(self):
        """The real comparator must remain the thing that decides.

        The direction sets live in `foundry_audit_baseline` and nowhere else; a
        local copy would let this file pass its own control while the shipped
        ratchet disagreed.

        Asked of the AST, not of the text: the module docstring NAMES the arm it
        rides ("the pinned metric `reaching_product` is `WORSE_IF_DOWN`"), and a
        substring search would read that sentence as a reimplementation. What
        must be absent is a BINDING.
        """
        tree = ast.parse(REACHABILITY.read_text(encoding="utf-8"))
        bound = {t.id for n in ast.walk(tree) if isinstance(n, ast.Assign)
                 for t in n.targets if isinstance(t, ast.Name)}
        self.assertNotIn("WORSE_IF_DOWN", bound)
        self.assertNotIn("WORSE_IF_UP", bound)
        unparsed = ast.unparse(selftest_ast())
        self.assertIn("baseline.save(", unparsed)
        self.assertIn("baseline.compare(", unparsed)


class TestTheStructuralGuardCatchesAReversion(unittest.TestCase):
    """NEGATIVE CONTROL, aimed at the code path rather than at the tool's name.

    Each case is the live source mutated back toward the pre-P0.3F arrangement.
    Deriving them from today's source rather than pasting the old body is what
    keeps the control aimed at the guard after the file moves on.
    """

    def setUp(self):
        self.source = REACHABILITY.read_text(encoding="utf-8")
        self.assertEqual(purity_violations(self.source), [],
                         "the control needs a clean baseline to break")

    def test_removing_the_rebind_is_caught(self):
        """The save then lands on whatever BASELINE already pointed at — the
        tracked ratchet.

        Note WHICH finding fires: the `finally` still holds
        `baseline.BASELINE = real_baseline`, so a rebind is still lexically
        present and the checker reports the ORDERING violation, not the absence
        one. Asserting the absence wording here would have been a control aimed
        at a message instead of at the code path.
        """
        reverted = self.source.replace("        baseline.BASELINE = tmp\n", "")
        self.assertNotEqual(reverted, self.source)
        findings = purity_violations(reverted)
        self.assertTrue(any("rebound" in f for f in findings), findings)

    def test_a_selftest_with_no_rebind_at_all_is_caught(self):
        """The absence arm of the same finding, which the case above cannot
        reach."""
        reverted = self.source.replace("        baseline.BASELINE = tmp\n", "")
        reverted = reverted.replace(
            "        baseline.BASELINE = real_baseline\n", "")
        self.assertIn("baseline.save() is called and BASELINE is never rebound",
                      purity_violations(reverted))

    def test_restoring_the_direct_cleanup_write_is_caught(self):
        """The exact shape the P0.3E review flagged: a `finally` that writes the
        tracked baseline to undo the synthetic pin."""
        reverted = self.source.replace(
            "        tmp.unlink(missing_ok=True)\n",
            "        baseline.BASELINE.write_text('{}', encoding='utf-8')\n")
        self.assertNotEqual(reverted, self.source)
        findings = purity_violations(reverted)
        self.assertTrue(any("direct write to baseline.BASELINE" in f
                            for f in findings), findings)

    def test_rebinding_only_after_the_save_is_caught(self):
        reverted = self.source.replace(
            "        baseline.BASELINE = tmp\n"
            "        baseline.save(section, pretend)\n",
            "        baseline.save(section, pretend)\n"
            "        baseline.BASELINE = tmp\n")
        self.assertNotEqual(reverted, self.source)
        self.assertIn("baseline.save() is reached before BASELINE is rebound",
                      purity_violations(reverted))

    def test_dropping_the_finally_is_caught(self):
        """A rebind with no restore leaks the temporary path into every later
        consumer in the same process.

        The `try:` is replaced by its ANCHORED two-line form on purpose. A bare
        `"    try:\n"` also matches `scan()`, whose `try` has an `except` — the
        mutation then produced a file that does not parse, and the control
        failed for a reason that had nothing to do with what it tests.
        """
        reverted = self.source.replace(
            "    try:\n        baseline.BASELINE = tmp\n",
            "    if True:\n        baseline.BASELINE = tmp\n")
        reverted = reverted.replace("    finally:\n"
                                    "        baseline.BASELINE = real_baseline\n"
                                    "        tmp.unlink(missing_ok=True)\n", "")
        self.assertNotEqual(reverted, self.source)
        ast.parse(reverted)  # the mutation must still be valid Python
        self.assertIn("BASELINE is rebound without a finally that restores it",
                      purity_violations(reverted))


# ---------------------------------------------------------------------------
# What it did, not only where it points
# ---------------------------------------------------------------------------


class TestTheSelftestRunLeavesTrackedStateAlone(PurityGuard):
    """Behavioural half, run twice — determinism is the house standard.

    `expect_untouched` restores anything it finds changed before failing, so a
    regression here reports itself instead of leaving a dirty tracked ratchet
    behind for the next test to trip over.
    """

    def run_selftest(self) -> subprocess.CompletedProcess:
        guard = self.expect_untouched([RATCHET])
        result = subprocess.run(
            [sys.executable, "experiments/foundry_reachability.py", "--selftest"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        guard()
        return result

    def test_two_runs_pass_and_write_no_tracked_bytes(self):
        for run in (1, 2):
            with self.subTest(run=run):
                result = self.run_selftest()
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("PASS", result.stdout)
                self.assertIn("FATAL", result.stdout)

    def test_no_tracked_file_anywhere_is_modified(self):
        """Wider than the ratchet. The claim is that the selftest writes nothing
        tracked, so `git status` is the honest instrument for it."""
        before = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT,
                                capture_output=True, text=True).stdout
        subprocess.run([sys.executable, "experiments/foundry_reachability.py",
                        "--selftest"], cwd=REPO_ROOT, capture_output=True, text=True)
        after = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT,
                               capture_output=True, text=True).stdout
        self.assertEqual(before, after)

    def test_the_synthetic_section_is_never_left_in_the_tracked_ratchet(self):
        """The interruption-unsafe failure mode, stated as its own assertion.

        Under the old arrangement this section existed in the tracked file for
        the length of the comparison. It must now never appear there at all.
        """
        self.run_selftest()
        self.assertNotIn(SELFTEST_SECTION,
                         json.loads(RATCHET.read_text(encoding="utf-8")))


class TestTheBehaviouralGuardCatchesTheOldArrangement(unittest.TestCase):
    """NEGATIVE CONTROL for the behavioural half.

    A test that only ever watches a pure run would also pass if the watching were
    broken. So: run the PRE-P0.3F algorithm against a stand-in baseline and require
    the same snapshot comparison to notice. The stand-in is a temporary file, so
    proving the guard works cannot itself dirty the repository — the failure the
    P0.3E review recorded, one level up.
    """

    def test_a_save_then_delete_cycle_is_visible_to_the_snapshot(self):
        module = load_legacy("foundry_audit_baseline")
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                         encoding="utf-8") as fh:
            json.dump({"reachability": {"artifacts_reaching_product": 0}}, fh)
            stand_in = Path(fh.name)
        self.addCleanup(stand_in.unlink, True)
        module.BASELINE = stand_in

        before = snapshot([stand_in])
        # Exactly what the old selftest did to the TRACKED file.
        module.save(SELFTEST_SECTION, {"artifacts_reaching_product": 1})
        doc = json.loads(stand_in.read_text(encoding="utf-8"))
        doc.pop(SELFTEST_SECTION, None)
        stand_in.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")

        self.assertNotEqual(before, snapshot([stand_in]),
                            "the snapshot cannot see a save-then-delete cycle, so "
                            "the purity assertions above prove nothing")


# ---------------------------------------------------------------------------
# What the control still proves
# ---------------------------------------------------------------------------


class TestTheSyntheticLostWireIsStillFatalThroughTheRealComparator(unittest.TestCase):
    """The meaning of the control, asserted directly rather than inferred from
    an exit code."""

    @classmethod
    def setUpClass(cls):
        cls.reach = load_legacy("foundry_reachability")
        cls.fab = cls.reach.baseline

    METRICS = {
        "entry_points": 1,
        "closure_modules": 2,
        "artifacts_reaching_product": 0,
        "artifacts_orphaned": 5,
        "consumers": {"codebook_json": 26},
    }

    def test_reaching_is_governed_by_the_real_WORSE_IF_DOWN_arm(self):
        self.assertIn("reaching", self.fab.WORSE_IF_DOWN)
        self.assertEqual(self.fab._direction("artifacts_reaching_product"), -1)

    def test_the_selftest_returns_zero_and_the_real_comparator_saw_the_drop(self):
        seen = {}
        real_compare = self.fab.compare

        def recording(section, metrics, update=False):
            result = real_compare(section, metrics, update)
            seen["section"] = section
            seen["target"] = self.fab.BASELINE
            seen["regressions"] = result[0]
            return result

        self.fab.compare = recording
        self.addCleanup(setattr, self.fab, "compare", real_compare)
        with contextlib.redirect_stdout(io.StringIO()):
            rc = self.reach.selftest(dict(self.METRICS))

        self.assertEqual(rc, 0)
        self.assertEqual(seen["section"], SELFTEST_SECTION)
        self.assertEqual([k for k, *_ in seen["regressions"]],
                         ["artifacts_reaching_product"])
        _, was, now, why = seen["regressions"][0]
        self.assertEqual((was, now), (1, 0))
        self.assertIn("WORSE", why)

    def test_the_comparison_ran_against_the_temporary_input_not_the_tracked_one(self):
        """Same run, the other half: the comparator was real AND it was pointed
        somewhere else."""
        seen = {}
        real_compare = self.fab.compare

        def recording(section, metrics, update=False):
            seen["target"] = self.fab.BASELINE
            return real_compare(section, metrics, update)

        self.fab.compare = recording
        self.addCleanup(setattr, self.fab, "compare", real_compare)
        with contextlib.redirect_stdout(io.StringIO()):
            self.reach.selftest(dict(self.METRICS))

        self.assertNotEqual(seen["target"], RATCHET)
        self.assertFalse(seen["target"].exists(),
                         "the temporary control input outlived the selftest")

    def test_the_module_attribute_is_restored_afterwards(self):
        before = self.fab.BASELINE
        with contextlib.redirect_stdout(io.StringIO()):
            self.reach.selftest(dict(self.METRICS))
        self.assertEqual(self.fab.BASELINE, before)

    def test_a_selftest_that_raises_still_restores_the_attribute(self):
        """The `finally` arm, exercised rather than merely present."""
        before = self.fab.BASELINE
        real_compare = self.fab.compare

        def exploding(*a, **kw):
            raise RuntimeError("boom")

        self.fab.compare = exploding
        self.addCleanup(setattr, self.fab, "compare", real_compare)
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(RuntimeError):
                self.reach.selftest(dict(self.METRICS))
        self.assertEqual(self.fab.BASELINE, before)

    def test_the_control_fails_when_the_drop_stops_being_reported(self):
        """The other exit arm. A control that can only return 0 proves nothing."""
        real_compare = self.fab.compare
        self.fab.compare = lambda section, metrics, update=False: ([], [], None)
        self.addCleanup(setattr, self.fab, "compare", real_compare)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = self.reach.selftest(dict(self.METRICS))
        self.assertEqual(rc, 1)
        self.assertIn("INVISIBLE", out.getvalue())


# ---------------------------------------------------------------------------
# Nothing else moved
# ---------------------------------------------------------------------------


class TestNormalExecutionIsUnchanged(unittest.TestCase):
    def test_the_gate2_reachability_row_is_unchanged(self):
        argv = {name: a for name, a, _ in gate_rows()}
        self.assertEqual(argv["reachability"],
                         ["experiments/foundry_reachability.py"])

    def test_no_gate2_row_runs_a_selftest(self):
        for name, argv, _ in gate_rows():
            with self.subTest(row=name):
                self.assertNotIn("--selftest", argv)

    def test_the_normal_path_still_reports_against_the_tracked_baseline(self):
        """`main()` is untouched: the real ratchet is still what a normal run
        compares against, and `--update-baseline` is still how it is re-pinned."""
        tree = ast.parse(REACHABILITY.read_text(encoding="utf-8"))
        main = next(n for n in ast.walk(tree)
                    if isinstance(n, ast.FunctionDef) and n.name == "main")
        source = ast.unparse(main)
        self.assertIn("baseline.report('reachability', metrics, args.update_baseline)",
                      source)
        self.assertNotIn("BASELINE", source)

    def test_the_tool_still_accepts_all_three_invocations(self):
        source = REACHABILITY.read_text(encoding="utf-8")
        for flag in ("--update-baseline", "--selftest"):
            with self.subTest(flag=flag):
                self.assertIn(f'"{flag}"', source)

    def test_the_foundry_artifact_set_is_untouched(self):
        """This slice is about the write target, not about what is measured."""
        module = load_legacy("foundry_reachability")
        self.assertEqual(sorted(module.FOUNDRY_ARTIFACTS), [
            "docs/CODEBOOK-NAMING-GRAMMAR.md",
            "experiments/out/card-tags.json.gz",
            "experiments/out/foundry/codebook.json",
            "experiments/out/foundry/corpus_pass_run1_classification.json",
            "experiments/out/foundry/det-patterns-v2.json",
        ])


if __name__ == "__main__":
    unittest.main()
