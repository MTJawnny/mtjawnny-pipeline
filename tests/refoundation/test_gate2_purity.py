"""C8 step 3, second slice: a normal Gate 2 run may not mutate tracked state.

Stdlib only, like the rest of this tree.

Gate 2 is the verification command. Two of its rows shelled out to tools that
**write into `docs/`**, which is tracked — so verifying the repository changed
the repository. Measured on a full green run in an isolated worktree:

    definition_drift  ->  docs/DEFINITION-DRIFT-AUDIT-2026-08-02.md   rewritten,
                          byte-identically. The write still happened.
    ruling_registry   ->  docs/RATIFIED-RULINGS-REGISTRY.md           rewritten,
                          leaving the worktree MODIFIED.

The second is the sharper one: `refoundation/BOOTSTRAP-STATE.yaml` records that
the regenerated registry carries a KNOWN FALSE-POSITIVE S1 namespace collision
and must not be accepted merely to clean the tree. So every green Gate 2 run
produced a diff that nobody is allowed to commit.

The fix is a **check/emit split**, not a semantic change: each tool gains an
explicit `--check-only` that suppresses the WRITE and nothing else. Every check
still runs, the same metrics are derived, the same ratchet comparison is applied,
and the row's verdict is unchanged. Standalone invocation still emits by default,
because emitting the report is what those commands are for.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT

from mtj_foundry.paths import ProjectPaths

PATHS = ProjectPaths.for_root(REPO_ROOT)
EXPERIMENTS = PATHS.legacy_experiments
GATE2 = EXPERIMENTS / "foundry_gate2.py"

CHECK_ONLY_ROWS = ("definition_drift", "ruling_registry")

# The tracked documents the two rows used to write.
DRIFT_REPORT = PATHS.legacy_docs / "DEFINITION-DRIFT-AUDIT-2026-08-02.md"
REGISTRY_REPORT = PATHS.legacy_docs / "RATIFIED-RULINGS-REGISTRY.md"
RATCHET = PATHS.baselines / "foundry-audit-baseline.json"


def load_legacy(name: str):
    """Import a legacy `experiments/` module by path.

    `sys.path` is extended because these modules import each other by bare name,
    exactly as they do when Gate 2 shells out to them — so importing one any other
    way would test a module the gate never runs.
    """
    if str(EXPERIMENTS) not in sys.path:
        sys.path.insert(0, str(EXPERIMENTS))
    spec = importlib.util.spec_from_file_location(
        f"legacy_{name}", EXPERIMENTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def gate_rows() -> list[tuple[str, list[str], str]]:
    """Gate 2's row table, read WITHOUT importing it.

    Parsed from the source so that reading the table cannot run it. The list is
    a literal, so `ast.literal_eval` on the assignment is the whole job — except
    that the argv entries are f-strings, which are not literals; `EXP` is
    substituted the way the module defines it.
    """
    tree = ast.parse(GATE2.read_text(encoding="utf-8"))
    exp = next(n.value.value for n in tree.body
               if isinstance(n, ast.Assign) and n.targets[0].id == "EXP")
    gates = next(n.value for n in tree.body
                 if isinstance(n, ast.Assign) and n.targets[0].id == "GATES")
    rows = []
    for row in gates.elts:
        name = row.elts[0].value
        argv = []
        for part in row.elts[1].elts:
            if isinstance(part, ast.Constant):
                argv.append(part.value)
            else:  # JoinedStr: f"{EXP}/tool.py"
                argv.append("".join(
                    v.value if isinstance(v, ast.Constant) else exp
                    for v in part.values))
        rows.append((name, argv, row.elts[2].value))
    return rows


def snapshot(paths) -> dict:
    """Bytes AND mtime for each path. Both, on purpose.

    A byte comparison alone would call an idempotent rewrite clean, and that is
    precisely what `definition_drift` did: same content, new mtime, a write that
    happened. Byte-identical output is a property of today's inputs, not of the
    code.
    """
    return {str(p): (p.read_bytes() if p.exists() else None,
                     p.stat().st_mtime_ns if p.exists() else None)
            for p in paths}


class PurityGuard(unittest.TestCase):
    """A base class for tests that run the real tools against the real repository.

    `expect_untouched` RESTORES what it finds changed, and only then fails.

    That is not tidiness, it is a lesson paid for: while negative-controlling this
    slice, a control that disabled the `--check-only` / `--update-baseline` halt
    let the very test asserting that halt proceed — and it wrote the tracked
    ratchet baseline, moving `ruling_registry.documents` 141 -> 143 while the file
    SIZE stayed 4,324 (a count cannot see a substitution). A test that provokes a
    write to prove it is refused must be able to survive the refusal being gone.
    """

    def expect_untouched(self, paths):
        """Context-manager-free guard: returns a callable to invoke afterwards."""
        before = snapshot(paths)

        def check():
            after = snapshot(paths)
            damaged = [name for name in before if before[name] != after[name]]
            for name in damaged:
                data = before[name][0]
                if data is not None:
                    Path(name).write_bytes(data)
            self.assertEqual(damaged, [], f"tracked state was mutated: {damaged} "
                                          "(restored from the pre-run snapshot)")
        return check


class Gate2TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = gate_rows()
        cls.argv = {name: argv for name, argv, _ in cls.rows}


# ---------------------------------------------------------------------------
# The runner's table
# ---------------------------------------------------------------------------


class TestTheTwoWritingRowsRunReadOnly(Gate2TestCase):
    def test_both_writer_rows_pass_check_only(self):
        for name in CHECK_ONLY_ROWS:
            with self.subTest(row=name):
                self.assertIn("--check-only", self.argv[name])

    def test_no_other_row_was_given_the_flag(self):
        """Scope: this slice touches two rows. A flag sprayed across the table
        would be a different change wearing this one's name."""
        for name, argv, _ in self.rows:
            if name not in CHECK_ONLY_ROWS:
                with self.subTest(row=name):
                    self.assertNotIn("--check-only", argv)

    def test_the_row_names_and_their_order_are_unchanged(self):
        self.assertEqual([name for name, _, _ in self.rows], [
            "lint", "family_sweep", "definition_drift", "ruling_registry",
            "conservation", "visibility", "ground_truth", "ground_truth_wide",
            "gate_audit", "probe_guards", "recorded_numbers", "invariance",
            "reachability", "object_lattice", "locality", "qualifier_census",
        ])

    def test_only_the_flag_was_added_to_those_two_rows(self):
        """Everything else about the row — the tool it shells out to, and the
        meaning of a failure — must be untouched."""
        self.assertEqual(self.argv["definition_drift"],
                         ["experiments/foundry_definition_drift.py", "--check-only"])
        self.assertEqual(self.argv["ruling_registry"],
                         ["experiments/foundry_ruling_registry.py", "--check-only"])

    def test_the_known_debt_waiver_is_unchanged(self):
        """One row may declare one authorized exit status. Still exactly one."""
        source = GATE2.read_text(encoding="utf-8")
        known = next(n.value for n in ast.parse(source).body
                     if isinstance(n, ast.Assign) and n.targets[0].id == "KNOWN_EXIT")
        self.assertEqual([k.value for k in known.keys], ["family_sweep"])
        self.assertEqual(known.values[0].elts[0].value, 3)


# ---------------------------------------------------------------------------
# The split itself
# ---------------------------------------------------------------------------


class EmitSplitTestCase(unittest.TestCase):
    def temp_targets(self, module, names) -> dict:
        """Repoint a module's output constants at a temp directory.

        Patched on the MODULE the code under test reaches, not on a copy: these
        are module-level constants read at call time, so rebinding them is what
        the emit function actually sees.
        """
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        targets = {}
        for name in names:
            target = root / Path(getattr(module, name)).name
            setattr(module, name, target)
            targets[name] = target
        return targets


class TestDefinitionDriftEmitSplit(EmitSplitTestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_legacy("foundry_definition_drift")

    def test_check_only_writes_nothing_and_reports_nothing_written(self):
        targets = self.temp_targets(self.module, ["REPORT_MD", "REPORT_JSON"])
        written = self.module.emit_reports([], 0, "note", emit=False)
        self.assertEqual(written, [])
        for name, target in targets.items():
            with self.subTest(output=name):
                self.assertFalse(target.exists())

    def test_emitting_writes_both_outputs(self):
        """The other arm. A test that only proves nothing is written would also
        pass if the emit path were broken."""
        targets = self.temp_targets(self.module, ["REPORT_MD", "REPORT_JSON"])
        written = self.module.emit_reports([], 0, "note", emit=True)
        self.assertEqual(len(written), 2)
        for name, target in targets.items():
            with self.subTest(output=name):
                self.assertTrue(target.exists())
        self.assertEqual(json.loads(targets["REPORT_JSON"].read_text()),
                         {"findings": []})

    def test_the_tool_accepts_the_flag_and_defaults_to_emitting(self):
        source = (EXPERIMENTS / "foundry_definition_drift.py").read_text(encoding="utf-8")
        self.assertIn('"--check-only"', source)
        self.assertIn("emit=not args.check_only", source)

    def test_check_only_and_update_baseline_contradict_each_other(self):
        """`--update-baseline` exists to WRITE the ratchet. Silently preferring one
        would make the flag that wins depend on which check ran first.

        Guarded: this invocation is the one that WOULD write if the halt were
        gone, so the ratchet is snapshotted and restored around it.
        """
        guard = PurityGuard.expect_untouched(self, [RATCHET])
        result = subprocess.run(
            [sys.executable, "experiments/foundry_definition_drift.py",
             "--check-only", "--update-baseline"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        guard()
        self.assertEqual(result.returncode, 2)
        self.assertIn("contradict", result.stderr)


class TestRulingRegistryEmitSplit(EmitSplitTestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_legacy("foundry_ruling_registry")
        cls.registry = cls.module.build()

    def test_check_only_writes_nothing_and_reports_nothing_written(self):
        targets = self.temp_targets(self.module, ["OUT_MD", "OUT_JSON"])
        self.assertEqual(self.module.emit_outputs(self.registry, emit=False), [])
        for name, target in targets.items():
            with self.subTest(output=name):
                self.assertFalse(target.exists())

    def test_emitting_writes_both_outputs(self):
        targets = self.temp_targets(self.module, ["OUT_MD", "OUT_JSON"])
        written = self.module.emit_outputs(self.registry, emit=True)
        self.assertEqual(len(written), 2)
        for name, target in targets.items():
            with self.subTest(output=name):
                self.assertTrue(target.exists())

    def test_the_registry_itself_is_built_before_and_independently_of_emitting(self):
        """The split may not touch what the gate MEASURES. `build()` produced a
        full registry here without anything being written."""
        for key in ("per_doc", "rulings", "distinct_rulings", "corroborated",
                    "sole_home", "total_references"):
            with self.subTest(key=key):
                self.assertIn(key, self.registry)
        self.assertGreater(self.registry["distinct_rulings"], 0)

    def test_the_metrics_the_ratchet_pins_come_from_the_registry_not_from_disk(self):
        """So suppressing the write cannot move a pinned number."""
        source = (EXPERIMENTS / "foundry_ruling_registry.py").read_text(encoding="utf-8")
        metrics = source.split('metrics = {"documents"', 1)[1].split("}", 1)[0]
        self.assertNotIn("read_text", metrics)
        for field in ("distinct_rulings", "total_references", "corroborated",
                      "sole_home"):
            self.assertIn(field, metrics)

    def test_the_existing_check_doc_mode_is_untouched(self):
        result = subprocess.run(
            [sys.executable, "experiments/foundry_ruling_registry.py",
             "--check", "docs/OUT-OF-SCOPE.md"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("SAFE:", result.stdout)

    def test_an_untracked_document_still_halts_with_status_2(self):
        result = subprocess.run(
            [sys.executable, "experiments/foundry_ruling_registry.py",
             "--check", "docs/no-such-document.md"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("not a TRACKED document", result.stderr)

    def test_check_only_and_update_baseline_contradict_each_other(self):
        guard = PurityGuard.expect_untouched(self, [RATCHET])
        result = subprocess.run(
            [sys.executable, "experiments/foundry_ruling_registry.py",
             "--check-only", "--update-baseline"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        guard()
        self.assertEqual(result.returncode, 2)
        self.assertIn("contradict", result.stderr)


class TestWritesAreConfinedToTheEmitFunction(unittest.TestCase):
    """Structural, so a future write added elsewhere is caught before it ships.

    Both tools now have exactly one place that writes. That is what makes tracked
    purity a property of one function instead of a claim about a whole file.
    """

    # `_selftest` is on the list and is NOT an exception being waved through: it
    # writes only inside a `tempfile.mkdtemp()` root it creates and removes, never
    # into the repository, and Gate 2's normal path never runs it. Both halves of
    # that claim are asserted below rather than assumed.
    CASES = {
        "foundry_definition_drift": ("emit_reports", "write_markdown"),
        "foundry_ruling_registry": ("emit_outputs", "write_markdown", "_selftest"),
    }

    def writing_functions(self, module_name: str) -> set[str]:
        tree = ast.parse((EXPERIMENTS / f"{module_name}.py").read_text(encoding="utf-8"))
        out = set()
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for inner in ast.walk(node):
                if (isinstance(inner, ast.Call)
                        and isinstance(inner.func, ast.Attribute)
                        and inner.func.attr in ("write_text", "write_bytes", "mkdir")):
                    out.add(node.name)
        return out

    def test_no_function_outside_the_emit_path_writes(self):
        for module_name, allowed in self.CASES.items():
            with self.subTest(module=module_name):
                self.assertEqual(self.writing_functions(module_name), set(allowed))

    def test_the_selftest_isolates_itself_in_a_temporary_repository(self):
        """The one other writer, and the mechanism that makes it safe.

        It builds a throwaway git repo, REBINDS this module's `REPO_ROOT`/`DOCS`
        at it, and restores them in a `finally`. So a first version of this test
        forbidding the names `REPO_ROOT`/`DOCS` was aimed at the isolation itself
        — the very thing that keeps the real worktree out of reach. What must
        stay absent is the two OUTPUT constants: the selftest has no business
        writing the registry's own products anywhere.
        """
        tree = ast.parse((EXPERIMENTS / "foundry_ruling_registry.py")
                         .read_text(encoding="utf-8"))
        selftest = next(n for n in ast.walk(tree)
                        if isinstance(n, ast.FunctionDef) and n.name == "_selftest")
        source = ast.unparse(selftest)
        self.assertIn("tempfile.mkdtemp", source)
        self.assertIn("shutil.rmtree", source)
        self.assertIn("global REPO_ROOT, DOCS", source)
        self.assertIn("finally", source)
        for forbidden in ("OUT_MD", "OUT_JSON"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_the_selftest_leaves_the_repository_untouched(self):
        """Behavioural half. Structure says where it points; this says what it did."""
        watched = (DRIFT_REPORT, REGISTRY_REPORT)
        before = snapshot(watched)
        result = subprocess.run(
            [sys.executable, "experiments/foundry_ruling_registry.py", "--selftest"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(before, snapshot(watched))


# ---------------------------------------------------------------------------
# End to end
# ---------------------------------------------------------------------------


class TestARowRunLeavesTrackedStateAlone(PurityGuard):
    """The property the slice exists for, asserted on real Gate 2 invocations.

    Asserted REGARDLESS of the row's verdict. A gate may legitimately fail — for
    missing local inputs, or because it found something — and it still may not
    write. Tying the assertion to a green run would silently stop testing purity
    on exactly the runs where it matters most.
    """

    WATCHED = (DRIFT_REPORT, REGISTRY_REPORT, RATCHET)

    def run_row(self, row: str) -> subprocess.CompletedProcess:
        guard = self.expect_untouched(self.WATCHED)
        result = subprocess.run(
            [sys.executable, "experiments/foundry_gate2.py", "--only", row],
            cwd=REPO_ROOT, capture_output=True, text=True)
        guard()
        return result

    def test_the_ruling_registry_row_writes_nothing(self):
        result = self.run_row("ruling_registry")
        self.assertIn("ruling_registry", result.stdout)

    def test_the_definition_drift_row_writes_nothing(self):
        result = self.run_row("definition_drift")
        self.assertIn("definition_drift", result.stdout)

    def test_the_ratchet_baseline_is_untouched_by_either_row(self):
        baseline = RATCHET
        import hashlib
        self.assertEqual(hashlib.sha256(baseline.read_bytes()).hexdigest(),
                         "51fca1518813760108ac44cb553e4bd8c2bcff48a2312b9054b3af1f5ad07601")
        self.assertEqual(baseline.stat().st_size, 4324)


if __name__ == "__main__":
    unittest.main()
