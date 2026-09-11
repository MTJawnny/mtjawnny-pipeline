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
# S9: the runner moved to the Gate-2 guard owner. `GATE2_REL` is the
# canonical command CLAUDE.md now names, spelled once.
GATE2_REL = "tests/guards/gate2/foundry_gate2.py"
GATE2 = REPO_ROOT / GATE2_REL
GATE2_GUARDS = REPO_ROOT / "tests" / "guards" / "gate2"

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


def load_moved_guard(relative: str):
    """Import a Gate-2 guard that has been MIGRATED out of `experiments/`.

    S4 moved `foundry_ground_truth.py` to `tests/guards/gate2/test_ground_truth.py`.
    It still imports loose legacy siblings by bare name, so `experiments/` stays
    on `sys.path` exactly as `load_legacy` puts it there -- the difference is only
    WHERE the module file itself is read from. Same mechanism, explicit path.
    """
    if str(EXPERIMENTS) not in sys.path:
        sys.path.insert(0, str(EXPERIMENTS))
    target = REPO_ROOT / relative
    spec = importlib.util.spec_from_file_location(
        f"guard_{target.stem}", target)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def gate_rows() -> list[tuple[str, list[str], str]]:
    """Gate 2's row table, read WITHOUT importing it.

    Parsed from the source so that reading the table cannot run it. The list is
    a literal, so `ast.literal_eval` on the assignment is the whole job — except
    that the argv entries are f-strings, which are not literals; the interpolated
    directory names are substituted the way the module defines them.

    S4: the substitution now RESOLVES THE NAME each f-string actually
    interpolates, from the module's own module-level string assignments, instead
    of assuming every hole is `EXP`. Migration slice 4 moved the ground-truth
    guard out of `experiments/`, so Gate 2 gained a second directory name
    (`GATE2_GUARDS`) — and the old code would have silently rendered it as `EXP`,
    reporting a command path that Gate 2 does not run. That is the
    "a generated view is not the source" failure, so the parser is made to read
    what is there rather than what it expected.
    """
    tree = ast.parse(GATE2.read_text(encoding="utf-8"))
    names = {n.targets[0].id: n.value.value for n in tree.body
             if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
             and isinstance(n.value, ast.Constant)
             and isinstance(n.value.value, str)}
    gates = next(n.value for n in tree.body
                 if isinstance(n, ast.Assign) and n.targets[0].id == "GATES")
    rows = []
    for row in gates.elts:
        name = row.elts[0].value
        argv = []
        for part in row.elts[1].elts:
            if isinstance(part, ast.Constant):
                argv.append(part.value)
            else:  # JoinedStr: f"{EXP}/tool.py" or f"{GATE2_GUARDS}/tool.py"
                argv.append("".join(
                    v.value if isinstance(v, ast.Constant)
                    else names[v.value.id]
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
        self.assertEqual(
            self.argv["definition_drift"],
            ["tests/guards/gate2/foundry_definition_drift.py", "--check-only"])
        self.assertEqual(
            self.argv["ruling_registry"],
            ["tests/guards/gate2/foundry_ruling_registry.py", "--check-only"])

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
        cls.module = load_moved_guard(
            "tests/guards/gate2/foundry_definition_drift.py")

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
        source = (GATE2_GUARDS / "foundry_definition_drift.py").read_text(encoding="utf-8")
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
            [sys.executable, "tests/guards/gate2/foundry_definition_drift.py",
             "--check-only", "--update-baseline"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        guard()
        self.assertEqual(result.returncode, 2)
        self.assertIn("contradict", result.stderr)


class TestRulingRegistryEmitSplit(EmitSplitTestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_moved_guard(
            "tests/guards/gate2/foundry_ruling_registry.py")
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
        source = (GATE2_GUARDS / "foundry_ruling_registry.py").read_text(encoding="utf-8")
        metrics = source.split('metrics = {"documents"', 1)[1].split("}", 1)[0]
        self.assertNotIn("read_text", metrics)
        for field in ("distinct_rulings", "total_references", "corroborated",
                      "sole_home"):
            self.assertIn(field, metrics)

    def test_the_existing_check_doc_mode_is_untouched(self):
        result = subprocess.run(
            [sys.executable, "tests/guards/gate2/foundry_ruling_registry.py",
             "--check", "docs/OUT-OF-SCOPE.md"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("SAFE:", result.stdout)

    def test_an_untracked_document_still_halts_with_status_2(self):
        result = subprocess.run(
            [sys.executable, "tests/guards/gate2/foundry_ruling_registry.py",
             "--check", "docs/no-such-document.md"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("not a TRACKED document", result.stderr)

    def test_check_only_and_update_baseline_contradict_each_other(self):
        guard = PurityGuard.expect_untouched(self, [RATCHET])
        result = subprocess.run(
            [sys.executable, "tests/guards/gate2/foundry_ruling_registry.py",
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
        tree = ast.parse((GATE2_GUARDS / f"{module_name}.py").read_text(encoding="utf-8"))
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
        tree = ast.parse((GATE2_GUARDS / "foundry_ruling_registry.py")
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
            [sys.executable, "tests/guards/gate2/foundry_ruling_registry.py",
             "--selftest"],
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
            [sys.executable, GATE2_REL, "--only", row],
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


# ---------------------------------------------------------------------------
# S9 — the migration's own standing guards
# ---------------------------------------------------------------------------


class TestTheGate2OwnerIsTheTestGuard(Gate2TestCase):
    """K6, as a committed assertion rather than a claim in a result comment."""

    def test_the_runner_is_no_longer_in_the_experiments_tree(self):
        self.assertTrue(GATE2.is_file(), GATE2)
        self.assertFalse((EXPERIMENTS / "foundry_gate2.py").exists(),
                         "the old runner owner must be ABSENT, not shadowed")

    def test_the_table_is_sixteen_rows_over_fifteen_scripts(self):
        self.assertEqual(len(self.rows), 16)
        self.assertEqual(len({argv[0] for _, argv, _ in self.rows}), 15)

    def test_every_row_points_at_a_file_that_exists(self):
        """A row naming a path nothing owns would fail as a child error rather
        than as a missing guard, which reads as the guard finding something."""
        for name, argv, _ in self.rows:
            with self.subTest(row=name):
                self.assertTrue((REPO_ROOT / argv[0]).is_file(), argv[0])

    def test_only_the_codebook_row_still_shells_into_experiments(self):
        """The lint row is `foundry_codebook`'s and the codebook is a later
        slice's to move. Everything else is test-owned now, and that is asserted
        by PARTITION so a thirteenth straggler cannot hide."""
        legacy = {name for name, argv, _ in self.rows
                  if argv[0].startswith("experiments/")}
        self.assertEqual(legacy, {"lint"})
        for name, argv, _ in self.rows:
            if name != "lint":
                with self.subTest(row=name):
                    self.assertTrue(argv[0].startswith("tests/guards/"), argv[0])

    def test_the_two_extracted_guards_are_the_test_owners(self):
        self.assertEqual(self.argv["locality"],
                         ["tests/guards/gate2/test_locality.py", "--gate"])
        self.assertEqual(self.argv["object_lattice"],
                         ["tests/guards/gate2/test_object_lattice.py", "--gate"])

    def test_no_row_runs_the_cr_edition_guard(self):
        """The R5 debt is discharged on the refoundation surface, NOT as a
        seventeenth row. Asserted so a later slice cannot quietly add one and
        call K6 satisfied because the count still looks like a count."""
        for _, argv, _ in self.rows:
            self.assertNotIn("test_cr_edition.py", argv[0])


class TestTheProbeHasExactlyOneOwner(unittest.TestCase):
    """S9's single-owner guard for `foundry_probe`.

    The failure this exists for is a compatibility second implementation left at
    the old address, which would pass every other check in this file: Gate 2
    would run the new one and four legacy consumers would import the old one.
    """

    PROBE_REL = "tests/guards/probe/foundry_probe.py"

    def test_the_probe_lives_at_its_test_owner(self):
        self.assertTrue((REPO_ROOT / self.PROBE_REL).is_file())

    def test_no_second_implementation_remains_at_the_old_root(self):
        self.assertFalse((EXPERIMENTS / "foundry_probe.py").exists())

    def test_no_active_non_frozen_consumer_imports_the_removed_owner(self):
        """AST, over every tracked Python file OUTSIDE the frozen AQ4 scope.

        AQ4 is PAUSED and its historical import is deliberately untouched, so it
        is excluded BY SCOPE and named here rather than silently skipped -- the
        exclusion is the thing a reader has to be able to see.
        """
        from tests.refoundation import layout_census
        offenders, frozen = [], []
        for rel in layout_census.tracked_python(REPO_ROOT):
            source = (REPO_ROOT / rel).read_text(encoding="utf-8")
            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue
            imports = {a.name for n in ast.walk(tree)
                       if isinstance(n, ast.Import) for a in n.names}
            if "foundry_probe" not in imports:
                continue
            if layout_census.scope_of(rel) == "aq4_PAUSED":
                frozen.append(rel.as_posix())
                continue
            # An ACTIVE consumer is fine -- provided it can actually resolve
            # the name, which means one of its OWN `sys.path` calls names the
            # probe's new directory. Asked of the call node, not of the file's
            # text: a mention in a comment is not a bootstrap.
            inserts = [ast.unparse(n) for n in ast.walk(tree)
                       if isinstance(n, ast.Call)
                       and isinstance(n.func, ast.Attribute)
                       and n.func.attr in ("insert", "append")
                       and isinstance(n.func.value, ast.Attribute)
                       and n.func.value.attr == "path"]
            if not any("probe" in call for call in inserts):
                offenders.append(rel.as_posix())
        self.assertEqual(offenders, [], "active consumers still reach the "
                                        "removed old owner")
        self.assertEqual(sorted(frozen), [
            "experiments/aq4_benchmark/aq4_compare.py",
            "experiments/aq4_benchmark/aq4_population.py",
            "experiments/foundry_aq4_probes.py",
        ])

    def test_the_probe_guards_row_runs_the_new_owner(self):
        argv = {name: a for name, a, _ in gate_rows()}
        self.assertEqual(argv["probe_guards"], [self.PROBE_REL])


class TestTheCrEditionGuardIsRegisteredAndRedCapable(unittest.TestCase):
    """R5. The debt was an ORPHAN, so registration is the whole point.

    `experiments/foundry_cr.py --selftest` existed for months and nothing ran
    it: no Gate-2 row, no test, no workflow. Moving it without running it would
    have re-created the orphan at a new address, so this is what makes the
    standing suite invoke it -- and prove it can go red.
    """

    GUARD_REL = "tests/guards/cr/test_cr_edition.py"

    def guard(self, source_override=None, cwd=None):
        return subprocess.run([sys.executable, self.GUARD_REL],
                              cwd=REPO_ROOT, capture_output=True, text=True)

    def test_the_guard_runs_green_against_the_live_edition(self):
        result = self.guard()
        self.assertEqual(result.returncode, 0, result.stdout[-3000:])
        self.assertIn("all guards behaved", result.stdout)

    def test_it_still_carries_the_ten_legacy_cases(self):
        tree = ast.parse((REPO_ROOT / self.GUARD_REL).read_text(encoding="utf-8"))
        cases = next(n.value for n in tree.body
                     if isinstance(n, ast.Assign)
                     and isinstance(n.targets[0], ast.Name)
                     and n.targets[0].id == "_CASES")
        self.assertEqual(len(cases.elts), 10)

    def test_the_legacy_shell_kept_no_copy(self):
        source = (EXPERIMENTS / "foundry_cr.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        names = {n.targets[0].id for n in tree.body if isinstance(n, ast.Assign)
                 and isinstance(n.targets[0], ast.Name)}
        self.assertNotIn("_CASES", names)
        self.assertNotIn("_selftest", {n.name for n in ast.walk(tree)
                                       if isinstance(n, ast.FunctionDef)})

    def test_the_report_half_stayed_in_the_legacy_shell(self):
        """The other direction. A responsibility DELETED rather than left is a
        truth change, so the retained half is asserted too."""
        tree = ast.parse((EXPERIMENTS / "foundry_cr.py").read_text(encoding="utf-8"))
        funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
        self.assertIn("_report", funcs)
        self.assertIn("main", funcs)

    def test_the_permanent_cr_package_has_no_process_entrypoint(self):
        pkg = REPO_ROOT / "src" / "mtj_foundry" / "mtg" / "cr"
        for path in sorted(pkg.glob("*.py")):
            with self.subTest(module=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertNotIn('if __name__ == "__main__"', source)
                self.assertNotIn("sys.exit(", source)

    def test_the_guard_goes_RED_when_the_law_it_tests_is_broken(self):
        """The negative control, on a DISPOSABLE copy of the repository's CR
        semantics -- the tracked module is never written. A guard that has never
        been shown to fail is not known to be a guard.
        """
        import shutil
        edition = (REPO_ROOT / "src" / "mtj_foundry" / "mtg" / "cr" / "edition.py")
        original = edition.read_bytes()
        rigged = original.replace(
            b'head = num if num[-1].isalpha() else num + "."',
            b'head = num + "."')
        self.assertNotEqual(rigged, original,
                            "the rig anchor is gone -- this control is no "
                            "longer aimed at anything")
        try:
            edition.write_bytes(rigged)
            result = self.guard()
        finally:
            edition.write_bytes(original)
        self.assertEqual(edition.read_bytes(), original, "restore failed")
        self.assertEqual(result.returncode, 1)
        self.assertIn("[FAIL] bold subrule drops its period", result.stdout)


if __name__ == "__main__":
    unittest.main()
