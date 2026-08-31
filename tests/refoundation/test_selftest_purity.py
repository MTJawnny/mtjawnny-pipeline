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

The fix is a different WRITE TARGET, not a more careful cleanup.

## WHAT C8.5J CHANGED, AND WHY THIS FILE IS STRONGER FOR IT

P0.3F expressed that different write target as a REBINDING: the temporary path was
assigned onto `foundry_audit_baseline.BASELINE`, a mutable module global, and
restored in a `finally`. This file's guards therefore asserted the MECHANISM —
that a rebind exists, that it precedes the first `save()`, that a `finally`
restores it, that it targets the module object the comparator reads rather than
this file's globals.

C8.5J removed the mechanism by removing the global. The permanent ratchet
(`mtj_foundry.ratchet`) takes its baseline as the FIRST ARGUMENT of `load`,
`save`, `compare` and `report`, so redirecting a control is now passing a
different value, not mutating shared process state.

**The protected invariant is unchanged and is now asserted directly instead of
through a proxy.** What the rebind guards were really protecting was: *the
tracked ratchet is never the thing this control reads or writes.* Under the old
seam that could only be checked indirectly, by policing the global. Under the new
seam it is checkable head-on — every ratchet call in `selftest` is examined and
its baseline argument must be the locally created temporary file.

That is a strictly stronger property than the rebind guards could express. A
rebind could be present, ordered correctly, and restored in a `finally`, and the
control would still have been rigged if some other call had reached the tracked
file; the argument check cannot be satisfied that way.

**What must NOT change is what the control PROVES.** `save()` and `compare()` are
still the real ones, so the shipped direction tables still decide whether the
synthetic lost wire is fatal. A control that reimplemented that comparison would
be a copy of the comparator instead of a test of it.
"""

from __future__ import annotations

import ast
import contextlib
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
# C8.5J: the tracked control input now has a NAME on the layout owner, so this
# test states it the same way production does instead of re-joining the filename.
RATCHET = PATHS.foundry_audit_baseline
REACHABILITY = EXPERIMENTS / "foundry_reachability.py"

SELFTEST_SECTION = "reachability_selftest"

# The module-level constant in `foundry_reachability` that holds the TRACKED
# baseline. Naming it once here is what lets the checker below say "the selftest
# must not reach for this" without hardcoding a path.
TRACKED_CONST = "RATCHET_BASELINE"

# The ratchet entry points that take a baseline as their FIRST argument.
BASELINE_ARG_CALLS = ("load", "save", "compare", "report")


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
    deliberately rigged source and require it to FIRE. "A guard that has never
    been shown to fail is not known to be a guard."

    Under the C8.5J seam the question is answered by reading ARGUMENTS rather
    than by policing a global: a ratchet call is pure exactly when the baseline
    it is handed is the temporary file this function created.
    """
    tree = ast.parse(source)
    fn = next((n for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef) and n.name == "selftest"), None)
    if fn is None:
        return ["selftest is not defined"]

    findings = []

    # 1. A direct write through the tracked-baseline constant, whatever it is
    #    bound to.
    for node in ast.walk(fn):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("write_text", "write_bytes", "open")
                and TRACKED_CONST in ast.unparse(node.func.value)):
            findings.append(
                f"line {node.lineno}: direct write to {TRACKED_CONST}")

    # 2. THE CORE CHECK. Every ratchet call must be handed the temporary
    #    baseline. The temporary is identified as the name bound from
    #    `tempfile.NamedTemporaryFile`, so renaming the local cannot silently
    #    disarm this, and hardcoding "tmp" cannot either.
    # The temporary is whatever local is bound FROM a `tempfile` construction --
    # `tmp = Path(fh.name)` under `with tempfile.NamedTemporaryFile(...) as fh`
    # is the live spelling. Derived rather than hardcoded as "tmp", so renaming
    # the local cannot silently disarm the check and a local merely NAMED `tmp`
    # cannot satisfy it.
    handles = {w.optional_vars.id
               for node in ast.walk(fn) if isinstance(node, ast.With)
               for w in node.items
               if "tempfile." in ast.unparse(w.context_expr)
               and isinstance(w.optional_vars, ast.Name)}
    temporaries = set()
    for node in ast.walk(fn):
        if not isinstance(node, ast.Assign):
            continue
        src = ast.unparse(node.value)
        if ("tempfile." in src
                or any(f"{h}.name" in src for h in handles)):
            temporaries |= {t.id for t in node.targets if isinstance(t, ast.Name)}

    calls = [n for n in ast.walk(fn)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr in BASELINE_ARG_CALLS]
    if not calls:
        findings.append("selftest makes no ratchet call at all")
    for node in calls:
        if not node.args:
            findings.append(
                f"line {node.lineno}: {node.func.attr}() is called with no "
                f"baseline argument")
            continue
        first = ast.unparse(node.args[0])
        if first in temporaries:
            continue
        findings.append(
            f"line {node.lineno}: {node.func.attr}() is handed {first!r} "
            f"instead of the temporary baseline")

    # 3. The temporary must be CREATED before any ratchet call writes through
    #    it, and removed on every path including a raised one.
    creations = [n.lineno for n in ast.walk(fn) if isinstance(n, ast.With)
                 and any("NamedTemporaryFile" in ast.unparse(w.context_expr)
                         for w in n.items)]
    writes = [n.lineno for n in calls if n.func.attr in ("save", "report")]
    if writes and not creations:
        findings.append("a ratchet write happens and no temporary baseline is created")
    elif writes and creations and min(creations) > min(writes):
        findings.append("a ratchet write is reached before the temporary baseline exists")
    if creations and not any(isinstance(n, ast.Try) and n.finalbody
                             for n in ast.walk(fn)):
        findings.append("the temporary baseline is created without a finally that removes it")

    return findings


class TestTheSelftestCannotReachTheTrackedRatchet(unittest.TestCase):
    """Structure. Says where the write can possibly go, before anything runs."""

    def test_the_live_selftest_has_no_purity_violations(self):
        self.assertEqual(purity_violations(REACHABILITY.read_text(encoding="utf-8")),
                         [])

    def test_the_synthetic_pin_goes_to_a_temporary_file(self):
        source = ast.unparse(selftest_ast())
        self.assertIn("tempfile", source)
        self.assertIn("NamedTemporaryFile", source)

    def test_the_temporary_baseline_is_removed_in_a_finally(self):
        """The old form asserted that a REBIND was restored. There is nothing to
        restore now — nothing shared was mutated — so what must survive is that
        the temporary file does not outlive the control."""
        fn = selftest_ast()
        tries = [n for n in ast.walk(fn) if isinstance(n, ast.Try) and n.finalbody]
        self.assertTrue(tries)
        finalized = "\n".join(ast.unparse(s) for t in tries for s in t.finalbody)
        self.assertIn("unlink", finalized)

    def test_no_mutable_module_global_is_rebound_anywhere_in_the_control(self):
        """The seam C8.5J removed, asserted as ABSENT rather than as required.

        This is the inverse of the P0.3F guard it replaces. A reintroduced
        rebinding would mean the permanent ratchet had grown a mutable baseline
        global again, which the C8.5J contract forbids outright.
        """
        source = ast.unparse(selftest_ast())
        self.assertNotIn('globals()["BASELINE"]', source)
        self.assertNotIn("global BASELINE", source)
        assigns = [n for n in ast.walk(selftest_ast())
                   if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Attribute) and t.attr == "BASELINE"
                           for t in n.targets)]
        self.assertEqual(assigns, [])

    def test_the_tracked_baseline_constant_is_never_named_in_the_control(self):
        """Head-on, and stronger than the rebind guards could be: the control
        cannot read or write the tracked input because it never mentions it."""
        self.assertNotIn(TRACKED_CONST, ast.unparse(selftest_ast()))

    def test_the_comparison_is_not_reimplemented_here(self):
        """The real comparator must remain the thing that decides.

        The direction tables live in `mtj_foundry.ratchet` and nowhere else; a
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
        self.assertNotIn("_WORSE_IF_DOWN", bound)
        self.assertNotIn("_WORSE_IF_UP", bound)
        unparsed = ast.unparse(selftest_ast())
        self.assertIn("ratchet.save(", unparsed)
        self.assertIn("ratchet.compare(", unparsed)


class TestTheStructuralGuardCatchesAReversion(unittest.TestCase):
    """NEGATIVE CONTROL, aimed at the code path rather than at the tool's name.

    Each case rigs the live source toward reaching the tracked baseline again.
    Deriving them from today's source rather than pasting an old body is what
    keeps the control aimed at the guard after the file moves on.
    """

    def setUp(self):
        self.source = REACHABILITY.read_text(encoding="utf-8")
        self.assertEqual(purity_violations(self.source), [],
                         "the control needs a clean baseline to break")

    def test_passing_the_tracked_baseline_to_save_is_caught(self):
        """The exact shape C8.5J's seam makes possible, and the one the task
        names: hand the real control input to the writing call."""
        rigged = self.source.replace(
            "ratchet.save(tmp, section, pretend)",
            f"ratchet.save({TRACKED_CONST}, section, pretend)")
        self.assertNotEqual(rigged, self.source)
        findings = purity_violations(rigged)
        self.assertTrue(any(TRACKED_CONST in f and "save()" in f
                            for f in findings), findings)

    def test_passing_the_tracked_baseline_to_compare_is_caught(self):
        rigged = self.source.replace(
            "ratchet.compare(tmp, section, metrics)",
            f"ratchet.compare({TRACKED_CONST}, section, metrics)")
        self.assertNotEqual(rigged, self.source)
        findings = purity_violations(rigged)
        self.assertTrue(any(TRACKED_CONST in f and "compare()" in f
                            for f in findings), findings)

    def test_a_direct_cleanup_write_to_the_tracked_baseline_is_caught(self):
        """The shape the P0.3E review flagged: a `finally` that writes the
        tracked baseline to undo the synthetic pin."""
        rigged = self.source.replace(
            "        tmp.unlink(missing_ok=True)\n",
            f"        {TRACKED_CONST}.write_text('{{}}', encoding='utf-8')\n")
        self.assertNotEqual(rigged, self.source)
        findings = purity_violations(rigged)
        self.assertTrue(any(f"direct write to {TRACKED_CONST}" in f
                            for f in findings), findings)

    def test_dropping_the_temporary_creation_is_caught(self):
        """The write then lands on whatever the first argument resolves to, and
        the checker reports the missing temporary rather than trusting the name."""
        rigged = self.source.replace(
            "    with tempfile.NamedTemporaryFile(\"w\", suffix=\".json\", delete=False,\n"
            "                                     encoding=\"utf-8\") as fh:\n"
            "        json.dump({}, fh)\n"
            "        tmp = Path(fh.name)\n",
            f"    tmp = {TRACKED_CONST}\n")
        self.assertNotEqual(rigged, self.source)
        findings = purity_violations(rigged)
        self.assertTrue(
            any("no temporary baseline is created" in f for f in findings)
            or any(TRACKED_CONST in f for f in findings), findings)

    def test_dropping_the_finally_is_caught(self):
        """A temporary with no removal leaks a file per run.

        The `try:` is replaced by its ANCHORED two-line form on purpose. A bare
        `"    try:\\n"` also matches `scan()`, whose `try` has an `except` — the
        mutation then produced a file that does not parse, and the control
        failed for a reason that had nothing to do with what it tests.
        """
        rigged = self.source.replace(
            "    try:\n        ratchet.save(tmp, section, pretend)\n",
            "    if True:\n        ratchet.save(tmp, section, pretend)\n")
        rigged = rigged.replace("    finally:\n"
                                "        tmp.unlink(missing_ok=True)\n", "")
        self.assertNotEqual(rigged, self.source)
        ast.parse(rigged)  # the mutation must still be valid Python
        self.assertIn("the temporary baseline is created without a finally that removes it",
                      purity_violations(rigged))

    def test_removing_the_ratchet_calls_entirely_is_caught(self):
        """A control that stopped calling the comparator would be pure and
        worthless. Purity alone was never the property."""
        rigged = self.source.replace("ratchet.save(tmp, section, pretend)",
                                     "pass").replace(
            "regressions, changes, _ = ratchet.compare(tmp, section, metrics)",
            "regressions, changes = [], []")
        self.assertNotEqual(rigged, self.source)
        self.assertIn("selftest makes no ratchet call at all",
                      purity_violations(rigged))


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

        Under the pre-P0.3F arrangement this section existed in the tracked file
        for the length of the comparison. It must never appear there at all.
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
        from mtj_foundry import ratchet
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                         encoding="utf-8") as fh:
            json.dump({"reachability": {"artifacts_reaching_product": 0}}, fh)
            stand_in = Path(fh.name)
        self.addCleanup(stand_in.unlink, True)

        before = snapshot([stand_in])
        # Exactly what the old selftest did to the TRACKED file.
        ratchet.save(stand_in, SELFTEST_SECTION, {"artifacts_reaching_product": 1})
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
        cls.rt = cls.reach.ratchet

    METRICS = {
        "entry_points": 1,
        "closure_modules": 2,
        "artifacts_reaching_product": 0,
        "artifacts_orphaned": 5,
        "consumers": {"codebook_json": 26},
    }

    def test_reaching_is_governed_by_the_real_WORSE_IF_DOWN_arm(self):
        self.assertIn("reaching", self.rt._WORSE_IF_DOWN)
        self.assertEqual(self.rt.direction("artifacts_reaching_product"), -1)

    def test_the_selftest_returns_zero_and_the_real_comparator_saw_the_drop(self):
        seen = {}
        real_compare = self.rt.compare

        def recording(baseline, section, metrics, update=False):
            result = real_compare(baseline, section, metrics, update)
            seen["section"] = section
            seen["target"] = baseline
            seen["regressions"] = result[0]
            return result

        self.rt.compare = recording
        self.addCleanup(setattr, self.rt, "compare", real_compare)
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
        somewhere else.

        C8.5J makes this the DIRECT reading it always wanted to be. It used to
        record a module global and hope that was what the call consumed; it now
        records the argument the call actually received.
        """
        seen = {}
        real_compare = self.rt.compare

        def recording(baseline, section, metrics, update=False):
            seen["target"] = Path(baseline)
            return real_compare(baseline, section, metrics, update)

        self.rt.compare = recording
        self.addCleanup(setattr, self.rt, "compare", real_compare)
        with contextlib.redirect_stdout(io.StringIO()):
            self.reach.selftest(dict(self.METRICS))

        self.assertNotEqual(seen["target"], RATCHET)
        self.assertFalse(seen["target"].exists(),
                         "the temporary control input outlived the selftest")

    def test_the_write_also_went_to_the_temporary_input(self):
        """`compare` only reads. The old file could not ask this question of
        `save` without a second global; the argument seam answers both."""
        seen = {}
        real_save = self.rt.save

        def recording(baseline, section, metrics):
            seen["target"] = Path(baseline)
            return real_save(baseline, section, metrics)

        self.rt.save = recording
        self.addCleanup(setattr, self.rt, "save", real_save)
        with contextlib.redirect_stdout(io.StringIO()):
            self.reach.selftest(dict(self.METRICS))
        self.assertNotEqual(seen["target"], RATCHET)

    def test_a_selftest_that_raises_still_removes_the_temporary(self):
        """The `finally` arm, exercised rather than merely present."""
        seen = {}
        real_save = self.rt.save

        def capturing(baseline, section, metrics):
            seen["target"] = Path(baseline)
            raise RuntimeError("boom")

        self.rt.save = capturing
        self.addCleanup(setattr, self.rt, "save", real_save)
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(RuntimeError):
                self.reach.selftest(dict(self.METRICS))
        self.assertFalse(seen["target"].exists(),
                         "the temporary control input survived a raised selftest")

    def test_the_control_fails_when_the_drop_stops_being_reported(self):
        """The other exit arm. A control that can only return 0 proves nothing."""
        real_compare = self.rt.compare
        self.rt.compare = lambda baseline, section, metrics, update=False: ([], [], None)
        self.addCleanup(setattr, self.rt, "compare", real_compare)
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
        """`main()` still compares against the REAL control input, and
        `--update-baseline` is still how it is re-pinned. This is the positive
        half of the purity guard: the tracked baseline must be unreachable from
        `selftest` and must remain exactly what `main()` uses.
        """
        tree = ast.parse(REACHABILITY.read_text(encoding="utf-8"))
        main = next(n for n in ast.walk(tree)
                    if isinstance(n, ast.FunctionDef) and n.name == "main")
        source = ast.unparse(main)
        self.assertIn(
            f"ratchet.report({TRACKED_CONST}, 'reachability', metrics, args.update_baseline)",
            source)

    def test_the_tracked_constant_comes_from_the_layout_owner(self):
        """And it is not a restated path. C8.5J's consumer rule, asserted here
        because this file is what says the constant is the tracked input."""
        source = REACHABILITY.read_text(encoding="utf-8")
        self.assertIn(
            f"{TRACKED_CONST} = ProjectPaths.for_root(fc.REPO_ROOT).foundry_audit_baseline",
            source)
        self.assertNotIn("foundry-audit-baseline.json", source)
        module = load_legacy("foundry_reachability")
        self.assertEqual(getattr(module, TRACKED_CONST), RATCHET)

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
