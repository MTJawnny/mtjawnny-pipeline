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
import os
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
        """Purity is before == after across real row runs. S14.R2.R1 replaced the
        slice-era hardcoded P0.3A digest: the bytes a row must leave alone are
        whatever the latest ratchet succession entry selects."""
        import hashlib
        from tests.refoundation.test_ratchet_baseline_succession import (
            latest_entry, load_succession)
        before = RATCHET.read_bytes()
        for row in ("ruling_registry", "definition_drift"):
            with self.subTest(row=row):
                self.run_row(row)
                self.assertEqual(RATCHET.read_bytes(), before)
        latest = latest_entry(load_succession())
        self.assertEqual(hashlib.sha256(before).hexdigest(), latest["sha256"])
        self.assertEqual(len(before), latest["size_bytes"])


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
            "benchmarks/aq4/experiments/aq4_benchmark/aq4_compare.py",
            "benchmarks/aq4/experiments/aq4_benchmark/aq4_population.py",
            "benchmarks/aq4/experiments/foundry_aq4_probes.py",
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


# ---------------------------------------------------------------------------
# S15.R2 — the ruling registry's tracked artifact must be CURRENT
# ---------------------------------------------------------------------------
#
# P0.3E (above) made `--check-only` stop WRITING. It did not make it start
# COMPARING. So the row went green while `docs/RATIFIED-RULINGS-REGISTRY.md` --
# the tracked deletion gate -- drifted away from the documents Git tracks:
# measured at this task's base, the committed artifact claimed 142 documents /
# 684 references against a live 138 / 660, still listed AQ4 addenda that had
# moved to `benchmarks/aq4/docs/`, and OMITTED the sole home of `R8.3`.
#
# The five ratchet metrics could not see any of it, and that is not bad luck --
# it is the `len() >= 15` trap this very module was built around. The audit's
# sharpest rig is NC4 below: replace a genuine ruling with an absent synthetic
# one in its sole home and all five numbers -- documents, ids, references,
# corroborated, sole-home -- hold at 138/127/660/86/41 while the registry's
# truth changes underneath them. A count cannot see a substitution.
#
# So `--check-only` now asserts BYTE EQUALITY between the tracked artifact and
# the in-memory rendering of the current population, and stays read-only while
# doing it. Everything below exists to prove that the enforcement is real,
# that it is the CLI's and not a helper's, and that it writes nothing.

REGISTRY_REL = "tests/guards/gate2/foundry_ruling_registry.py"
REGISTRY_MD_REL = "docs/RATIFIED-RULINGS-REGISTRY.md"
REGISTRY_JSON_REL = "experiments/out/foundry/ruling_registry.json"
BASELINE_REL = "config/baselines/foundry-audit-baseline.json"

# The accepted population at this task's base, re-derived rather than restated:
# every fixture starts as an exact copy of it, so these are what a control must
# hold fixed while it changes something else.
ACCEPTED_METRICS = {"documents": 138, "ruling_ids": 127, "total_references": 660,
                    "corroborated": 86, "sole_home": 41}
R8_3_HOME = "ACTIVATED-REGENERATE-SELF-DET-LAW.md"
AG_CLI_01_HOME = "MEMBER-ADD-MUTATION-LAW.md"

# A WRITE SPY, not just a hash. An identical-byte rewrite leaves every digest
# equal, and `definition_drift` proved that is not hypothetical -- it rewrote
# its report byte-identically on every green run for weeks. `snapshot()` above
# catches that with mtime; this catches it at the call, inside the real CLI
# process, and also catches a write to a path no snapshot thought to watch.
_WRITE_SPY = '''
import atexit, builtins, io, os, pathlib

_LOG = os.environ["REGISTRY_WRITE_SPY"]
_ORIG_OPEN = builtins.open
_seen = []


def _note(kind, target):
    try:
        _seen.append(kind + "\\t" + os.fspath(target))
    except Exception:
        _seen.append(kind + "\\t<unfspathable>")


def _spy_open(file, mode="r", *a, **k):
    if any(c in mode for c in "wxa+"):
        _note("open", file)
    return _ORIG_OPEN(file, mode, *a, **k)


builtins.open = _spy_open
io.open = _spy_open

for _n in ("write_text", "write_bytes", "touch", "mkdir", "unlink", "rmdir"):
    def _wrap_path(_n=_n, _orig=getattr(pathlib.Path, _n)):
        def _f(self, *a, **k):
            _note(_n, self)
            return _orig(self, *a, **k)
        return _f
    setattr(pathlib.Path, _n, _wrap_path())

for _n in ("remove", "unlink", "rename", "replace", "mkdir", "makedirs"):
    def _wrap_os(_n=_n, _orig=getattr(os, _n)):
        def _f(path, *a, **k):
            _note(_n, path)
            return _orig(path, *a, **k)
        return _f
    setattr(os, _n, _wrap_os())


@atexit.register
def _dump():
    with _ORIG_OPEN(_LOG, "w", encoding="utf-8") as fh:
        fh.write("\\n".join(_seen))
'''


def fixture_sources() -> list[str]:
    """The tracked paths a standalone registry fixture needs, from the index.

    Not a hand-list of files: the docs population is whatever Git tracks
    directly under `docs/`, which is the same rule the tool itself applies.
    """
    out = subprocess.run(["git", "-C", str(REPO_ROOT), "ls-files", "-z"],
                         capture_output=True, text=True, check=True)
    wanted = []
    for name in (n for n in out.stdout.split("\0") if n):
        path = Path(name)
        if path.parent == Path("docs") and path.suffix == ".md":
            wanted.append(name)
        elif name.startswith("src/") or name.startswith("config/baselines/"):
            wanted.append(name)
        elif name in (REGISTRY_REL, GATE2_REL, "experiments/foundry_common.py",
                      ".gitignore"):
            wanted.append(name)
    return sorted(wanted)


class RegistryFixtureCase(unittest.TestCase):
    """Every control runs the REAL CLI against a private copy of the repository.

    The copy is a real Git repository at a real absolute path, carrying the
    CANDIDATE guard (working-tree bytes, not a HEAD blob) at the same relative
    depth, the real `foundry_common` bootstrap, the real `ProjectPaths` package,
    the real ratchet baseline and the real 138-document population. So these are
    not tests of a correct-but-unused helper: they are tests of the command Gate
    2 runs, and a rig that makes the CLI green makes them red (NC14).

    Nothing here touches the Captain's worktree. That is the point of the copy,
    not a nicety -- a control that stages a synthetic ruling into the real index
    to prove staging works has left the repository as its own side effect.
    """

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="registry-freshness-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        for name in fixture_sources():
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO_ROOT / name, target)
        for argv in (["init", "-q"], ["config", "user.email", "fixture@localhost"],
                     ["config", "user.name", "fixture"], ["add", "-A"],
                     ["commit", "-qm", "fixture"]):
            subprocess.run(["git", "-C", str(self.root)] + argv, check=True,
                           capture_output=True, text=True)
        self.md = self.root / REGISTRY_MD_REL
        self.json_out = self.root / REGISTRY_JSON_REL
        self.baseline = self.root / BASELINE_REL

    # -- running the real command ------------------------------------------

    def run_cli(self, *args, spy: bool = False, source: Path | None = None):
        """Invoke the fixture's own guard, exactly as Gate 2 invokes the real one."""
        env = dict(os.environ)
        log = None
        if spy:
            # OUTSIDE the fixture, deliberately: a spy that lives in the tree it
            # is watching shows up as untracked state and becomes a difference
            # the purity assertion then has to be taught to ignore.
            spy_dir = Path(tempfile.mkdtemp(prefix="registry-write-spy-"))
            self.addCleanup(shutil.rmtree, spy_dir, ignore_errors=True)
            (spy_dir / "sitecustomize.py").write_text(_WRITE_SPY, encoding="utf-8")
            log = spy_dir / "log.txt"
            env["REGISTRY_WRITE_SPY"] = str(log)
            env["PYTHONPATH"] = os.pathsep.join(
                [str(spy_dir)] + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else []))
        result = subprocess.run(
            [sys.executable, str(source or (self.root / REGISTRY_REL))] + list(args),
            cwd=self.root, capture_output=True, text=True, env=env)
        result.writes = []
        if log is not None and log.exists():
            result.writes = [line.split("\t", 1)[1]
                             for line in log.read_text(encoding="utf-8").splitlines()
                             if "\t" in line]
        return result

    def run_gate2(self, *args):
        return subprocess.run([sys.executable, str(self.root / GATE2_REL)] + list(args),
                              cwd=self.root, capture_output=True, text=True)

    def registry(self) -> dict:
        """`build()` as the fixture's own guard computes it, in a child process.

        A child, deliberately: importing the module into THIS process would bind
        its `REPO_ROOT` to the real repository, and every population assertion
        below would then be about the wrong tree.
        """
        probe = ("import json,sys;"
                 "sys.path.insert(0,'experiments');"
                 "import importlib.util as u;"
                 f"s=u.spec_from_file_location('rr','{self.root / REGISTRY_REL}');"
                 "m=u.module_from_spec(s);s.loader.exec_module(m);"
                 "r=m.build();"
                 "print(json.dumps({'metrics':{'documents':len(r['per_doc']),"
                 "'ruling_ids':r['distinct_rulings'],"
                 "'total_references':r['total_references'],"
                 "'corroborated':r['corroborated'],'sole_home':r['sole_home']},"
                 "'ids':sorted(r['rulings']),"
                 "'homes':{k:sorted({o['doc'] for o in v}) for k,v in r['rulings'].items()},"
                 "'render':m.render_markdown(r)}))")
        out = subprocess.run([sys.executable, "-c", probe], cwd=self.root,
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr[-2000:])
        return json.loads(out.stdout)

    def canonical(self) -> bytes:
        return self.registry()["render"].encode("utf-8")

    def regenerate(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout[-2000:] + result.stderr[-2000:])

    # -- fixture state -----------------------------------------------------

    def watched(self) -> list[Path]:
        """Every output, the ratchet, and every SOURCE document.

        The sources are watched too because "read-only" has to mean the tool did
        not quietly repair its own inputs either.
        """
        return ([self.md, self.json_out, self.baseline]
                + sorted((self.root / "docs").glob("*.md")))

    def index_state(self) -> str:
        out = subprocess.run(["git", "-C", str(self.root), "ls-files", "-s"],
                             capture_output=True, text=True, check=True)
        status = subprocess.run(["git", "-C", str(self.root), "status", "--porcelain"],
                                capture_output=True, text=True, check=True)
        return out.stdout + "\0" + status.stdout

    def stage(self, relative: str):
        subprocess.run(["git", "-C", str(self.root), "add", "--", relative],
                       check=True, capture_output=True, text=True)

    def stage_removal(self, relative: str):
        subprocess.run(["git", "-C", str(self.root), "rm", "-q", "--", relative],
                       check=True, capture_output=True, text=True)

    def assertFreshnessFailed(self, result):
        self.assertEqual(result.returncode, 1,
                         f"expected a red --check-only\n{result.stdout[-1500:]}\n"
                         f"{result.stderr[-1500:]}")
        self.assertIn("STALE REGISTRY", result.stderr)
        self.assertIn(REGISTRY_REL, result.stderr,
                      "the diagnostic must name the real regeneration command")

    def assertFreshnessPassed(self, result):
        self.assertNotIn("STALE REGISTRY", result.stderr)


class TestTheFixtureIsTheAcceptedPopulation(RegistryFixtureCase):
    """NC10 (conservation half). Before any control rigs anything, the fixture
    must BE the accepted state -- otherwise every later assertion is about some
    other repository and proves nothing about this one."""

    def test_the_fixture_reproduces_the_accepted_metrics_and_both_law_homes(self):
        reg = self.registry()
        self.assertEqual(reg["metrics"], ACCEPTED_METRICS)
        self.assertEqual(reg["homes"]["R8.3"], [R8_3_HOME])
        self.assertEqual(reg["homes"]["AG-CLI-01"], [AG_CLI_01_HOME])

    def test_the_tracked_artifact_is_current_and_check_only_is_green(self):
        result = self.run_cli("--check-only")
        self.assertEqual(result.returncode, 0, result.stderr[-2000:])
        self.assertFreshnessPassed(result)
        self.assertEqual(self.md.read_bytes(), self.canonical())


class TestStalenessIsDetected(RegistryFixtureCase):
    def test_NC1_a_manual_artifact_edit_is_caught(self):
        """NC1. No source byte moves, so all five metrics are fixed and the
        ratchet is green -- the ONLY thing that changed is the artifact.

        This is a RENDER-VERSUS-ARTIFACT mismatch, which is a different
        proposition from "two renders disagree" (NC9). Conflating them is how a
        freshness check gets written that only ever tests determinism.
        """
        before = self.canonical()
        self.md.write_bytes(self.md.read_bytes() + b"\nappended by hand\n")
        result = self.run_cli("--check-only")
        self.assertFreshnessFailed(result)
        self.assertIn("all 5 pinned metrics unchanged", result.stdout,
                      "the ratchet must still be GREEN, or this control is "
                      "measuring the ratchet instead of freshness")
        self.assertEqual(self.canonical(), before, "sources must be untouched")
        self.assertEqual(self.canonical(), before)

    def test_NC1_a_single_flipped_byte_is_enough(self):
        data = bytearray(self.md.read_bytes())
        data[len(data) // 2] ^= 0x20
        self.md.write_bytes(bytes(data))
        self.assertFreshnessFailed(self.run_cli("--check-only"))

    def test_NC2_a_newly_staged_sole_home_makes_the_artifact_stale(self):
        """NC2. A real new ruling arrives; nobody regenerates."""
        self.assertNotIn("F99", self.registry()["ids"], "the synthetic id must "
                         "be absent before the rig, or the rig proves nothing")
        (self.root / "docs" / "N10-NEW.md").write_text(
            "# synthetic\n\n- **F99** — synthetic ruling\n", encoding="utf-8")
        self.stage("docs/N10-NEW.md")
        after = self.registry()
        self.assertIn("F99", after["ids"], "staging must ADMIT the document")
        self.assertEqual(after["metrics"]["documents"], 139)
        self.assertEqual(after["metrics"]["sole_home"], 42)
        result = self.run_cli("--check-only")
        self.assertFreshnessFailed(result)

    def test_NC3_a_staged_removal_makes_the_artifact_stale(self):
        """NC3, first half: a corroborating document LEAVES the population."""
        victim = "docs/ARCHITECTURE-AUDIT.md"
        before = self.canonical()
        self.stage_removal(victim)
        self.assertNotEqual(self.canonical(), before,
                            "removing a corroborating document must move the "
                            "canonical rendering, or this rig is inert")
        self.assertFreshnessFailed(self.run_cli("--check-only"))

    def test_NC3_an_unstaged_deletion_still_halts_loudly(self):
        """NC3, second half. The pre-existing halt is a TRUTH guard: skipping an
        absent tracked document would silently drop every ruling it is the sole
        home of. Freshness must not have replaced it with a quiet diff."""
        (self.root / "docs" / R8_3_HOME).unlink()
        result = self.run_cli("--check-only")
        self.assertEqual(result.returncode, 1)
        self.assertIn("HALT: tracked under docs/ but absent", result.stderr)
        self.assertIn(R8_3_HOME, result.stderr)

    def test_NC4_an_all_counts_equal_substitution_is_caught(self):
        """NC4 — the control the ratchet provably cannot pass.

        `R8.3` is replaced, in its own sole-home law, by a grammar-valid id that
        does not exist anywhere in the corpus. One document, one occurrence, one
        sole home before and after: documents, ruling ids, total references,
        corroborated and sole-home ALL hold at 138/127/660/86/41. A genuine
        ratified ruling has silently left the registry and every pinned number
        agrees that nothing happened.
        """
        before = self.registry()
        self.assertEqual(before["metrics"], ACCEPTED_METRICS)
        self.assertNotIn("F99", before["ids"])
        law = self.root / "docs" / R8_3_HOME
        original = law.read_text(encoding="utf-8")
        self.assertIn("R8.3", original, "the rig anchor is gone")
        law.write_text(original.replace("R8.3", "F99"), encoding="utf-8")

        after = self.registry()
        self.assertEqual(after["metrics"], ACCEPTED_METRICS,
                         "the substitution must be INVISIBLE to all five metrics, "
                         "otherwise this is a count-moving rig and not NC4")
        self.assertNotIn("R8.3", after["ids"], "the genuine ruling must be LOST")
        self.assertIn("F99", after["ids"], "the synthetic ruling must be GAINED")
        self.assertEqual(after["homes"]["F99"], [R8_3_HOME])

        result = self.run_cli("--check-only")
        self.assertIn("all 5 pinned metrics unchanged", result.stdout,
                      "the ratchet is blind here -- that is the premise")
        self.assertFreshnessFailed(result)


class TestThePopulationBoundaryIsUnchanged(RegistryFixtureCase):
    def test_NC5_an_untracked_paper_changes_nothing(self):
        """NC5. The 2026-08-14 incident, re-run against the freshness slice:
        an untracked paper must not corroborate a genuine sole home away, must
        not mint an id, and must not move the freshness verdict either."""
        before = self.registry()
        before_bytes = self.md.read_bytes()
        (self.root / "docs" / "N10-UNTRACKED-PAPER.md").write_text(
            f"# untracked\n\n- **R8.3** — restated, which would corroborate it away.\n"
            f"- **F99** — fake id that would become a sole home.\n", encoding="utf-8")
        after = self.registry()
        self.assertEqual(after["metrics"], before["metrics"])
        self.assertEqual(after["ids"], before["ids"])
        self.assertEqual(after["homes"]["R8.3"], [R8_3_HOME])
        self.assertEqual(after["render"], before["render"])
        result = self.run_cli("--check-only")
        self.assertEqual(result.returncode, 0, result.stderr[-2000:])
        self.assertFreshnessPassed(result)
        self.assertEqual(self.md.read_bytes(), before_bytes)

    def test_NC5_an_IGNORED_untracked_paper_changes_nothing_either(self):
        """The same claim for a file Git actively ignores, not merely one it has
        not been told about. Both are outside the index; the tool must not care
        which kind of outside it is."""
        before = self.registry()
        (self.root / ".gitignore").write_text(
            (self.root / ".gitignore").read_text(encoding="utf-8")
            + "\ndocs/N10-IGNORED-*.md\n", encoding="utf-8")
        (self.root / "docs" / "N10-IGNORED-PAPER.md").write_text(
            "# ignored\n\n- **F99** — fake id.\n", encoding="utf-8")
        status = subprocess.run(
            ["git", "-C", str(self.root), "status", "--porcelain", "--ignored",
             "--", "docs/N10-IGNORED-PAPER.md"], capture_output=True, text=True)
        self.assertTrue(status.stdout.startswith("!!"),
                        f"the rig must actually be IGNORED, got {status.stdout!r}")
        self.assertEqual(self.registry()["ids"], before["ids"])
        self.assertEqual(self.run_cli("--check-only").returncode, 0)

    def test_NC6_staging_admits_it_and_worktree_bytes_beat_the_index_blob(self):
        """NC6. Staging is the act of admission, and the SCAN still reads the
        working tree -- so a refreshed candidate is checkable before commit."""
        paper = self.root / "docs" / "N10-STAGED.md"
        paper.write_text("# staged\n\n- **F98** — first content.\n", encoding="utf-8")
        self.stage("docs/N10-STAGED.md")
        staged = self.registry()
        self.assertIn("F98", staged["ids"])
        self.assertEqual(staged["metrics"]["documents"], 139)
        self.assertFreshnessFailed(self.run_cli("--check-only"))

        paper.write_text("# edited after staging\n\n- **F97** — worktree bytes.\n",
                         encoding="utf-8")
        edited = self.registry()
        self.assertIn("F97", edited["ids"], "the scan must read the worktree")
        self.assertNotIn("F98", edited["ids"], "not the index blob")

    def test_NC15_nested_outside_and_self_sources_stay_out_of_the_population(self):
        """NC15. The population is names directly under top-level `docs/`, and
        the registry is never its own source. A recursive widening would make
        every architecture paper a ruling home."""
        before = self.registry()
        nested = self.root / "docs" / "architecture" / "N10-NESTED.md"
        nested.parent.mkdir(parents=True, exist_ok=True)
        nested.write_text("- **F96** — nested fake.\n", encoding="utf-8")
        self.stage("docs/architecture/N10-NESTED.md")
        outside = self.root / "refoundation"
        outside.mkdir(parents=True, exist_ok=True)
        (outside / "N10-OUTSIDE.md").write_text("- **F95** — outside fake.\n",
                                                encoding="utf-8")
        self.stage("refoundation/N10-OUTSIDE.md")
        not_markdown = self.root / "docs" / "N10-NOT-MARKDOWN.txt"
        not_markdown.write_text("- **F94** — wrong suffix.\n", encoding="utf-8")
        self.stage("docs/N10-NOT-MARKDOWN.txt")
        self.md.write_bytes(self.md.read_bytes()
                            + "\n- **F93** — self source.\n".encode("utf-8"))

        after = self.registry()
        for fake in ("F96", "F95", "F94", "F93"):
            with self.subTest(fake=fake):
                self.assertNotIn(fake, after["ids"])
        self.assertEqual(after["metrics"]["documents"],
                         before["metrics"]["documents"])
        # The registry edit is still an edit, so freshness -- and only
        # freshness -- must report it.
        self.assertFreshnessFailed(self.run_cli("--check-only"))


class TestTheCheckIsReadOnly(RegistryFixtureCase):
    def assertWroteNothing(self, result, before_files, before_index, watch=None):
        inside = [w for w in result.writes
                  if str(self.root) in w]
        self.assertEqual(inside, [], f"the CLI wrote inside the fixture: {inside}")
        self.assertEqual(snapshot(watch or self.watched()), before_files,
                         "bytes or mtime moved")
        self.assertEqual(self.index_state(), before_index, "the index moved")

    def test_NC7_check_only_writes_nothing_on_a_CURRENT_artifact(self):
        before_files, before_index = snapshot(self.watched()), self.index_state()
        result = self.run_cli("--check-only", spy=True)
        self.assertEqual(result.returncode, 0, result.stderr[-2000:])
        self.assertWroteNothing(result, before_files, before_index)

    def test_NC7_check_only_writes_nothing_on_a_STALE_artifact(self):
        """The arm that matters. A checker that "helpfully" repairs what it finds
        stale would turn a red gate green by mutating the thing under test."""
        self.md.write_bytes(self.md.read_bytes() + b"\nhand edit\n")
        before_files, before_index = snapshot(self.watched()), self.index_state()
        result = self.run_cli("--check-only", spy=True)
        self.assertFreshnessFailed(result)
        self.assertWroteNothing(result, before_files, before_index)

    def test_NC11_a_MISSING_artifact_fails_and_is_not_recreated(self):
        """NC11. Absence is a failure, never a first run: a deletion gate that
        regenerates itself on demand cannot report that it was deleted."""
        self.md.unlink()
        before_files, before_index = snapshot(self.watched()), self.index_state()
        result = self.run_cli("--check-only", spy=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("is MISSING", result.stderr)
        self.assertIn(REGISTRY_REL, result.stderr)
        self.assertFalse(self.md.exists(), "the checker RECREATED the artifact")
        self.assertWroteNothing(result, before_files, before_index)

    def test_NC11_an_UNREADABLE_artifact_fails_without_being_repaired(self):
        """Unreadability is simulated deterministically by making the artifact a
        DIRECTORY, so the read raises `IsADirectoryError` -- an `OSError` -- on
        every platform. Permission bits are not a rig: this suite is routinely
        run as a user for whom `chmod 000` is advisory."""
        self.md.unlink()
        self.md.mkdir()
        # The artifact itself is excluded from the byte snapshot for the obvious
        # reason: it is unreadable, which is the rig. Its survival is asserted
        # directly instead, and everything else is watched as usual.
        watch = [p for p in self.watched() if p != self.md]
        before_files, before_index = snapshot(watch), self.index_state()
        result = self.run_cli("--check-only", spy=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("could not be read", result.stderr)
        self.assertTrue(self.md.is_dir(), "the rig was replaced rather than reported")
        self.assertEqual(list(self.md.iterdir()), [],
                         "something was written INTO the unreadable path")
        self.assertWroteNothing(result, before_files, before_index, watch=watch)

    def test_NC12_the_ignored_JSON_output_is_not_a_freshness_prerequisite(self):
        """NC12. `ruling_registry.json` is a regenerable IGNORED output. If its
        absence, staleness or corruption could move the verdict, the tracked
        gate would depend on untracked state -- which is blocker N01's shape,
        not a freshness check."""
        self.regenerate()
        self.assertTrue(self.json_out.exists())
        for label, mutate in (
            ("missing", lambda: self.json_out.unlink()),
            ("stale", lambda: self.json_out.write_text('{"schema": "old"}',
                                                       encoding="utf-8")),
            ("corrupt", lambda: self.json_out.write_bytes(b"\x00 not json {")),
        ):
            with self.subTest(json=label):
                mutate()
                found = self.json_out.read_bytes() if self.json_out.exists() else None
                result = self.run_cli("--check-only", spy=True)
                self.assertEqual(result.returncode, 0, result.stderr[-1500:])
                self.assertFreshnessPassed(result)
                after = self.json_out.read_bytes() if self.json_out.exists() else None
                self.assertEqual(after, found, "the ignored JSON was touched")


class TestTheEmitterAndTheCheckerAgree(RegistryFixtureCase):
    def test_NC8_emission_produces_exactly_what_the_checker_expects(self):
        """NC8. One renderer, so a green check is evidence about the artifact the
        emitter actually writes -- not about a second implementation of it."""
        self.md.write_bytes(b"# deliberately wrong\n")
        self.json_out.unlink(missing_ok=True)
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr[-2000:])
        self.assertEqual(self.md.read_bytes(), self.canonical())
        self.assertIn("wrote docs/RATIFIED-RULINGS-REGISTRY.md", result.stdout)
        self.assertIn("wrote experiments/out/foundry/ruling_registry.json",
                      result.stdout)

        emitted = json.loads(self.json_out.read_text(encoding="utf-8"))
        self.assertEqual(emitted["distinct_rulings"], ACCEPTED_METRICS["ruling_ids"])
        self.assertEqual(emitted["total_references"],
                         ACCEPTED_METRICS["total_references"])
        self.assertEqual(len(emitted["per_doc"]), ACCEPTED_METRICS["documents"])

        follow_up = self.run_cli("--check-only")
        self.assertEqual(follow_up.returncode, 0, follow_up.stderr[-2000:])
        self.assertFreshnessPassed(follow_up)

    def test_NC8_emission_writes_exact_UTF8_LF_bytes(self):
        self.regenerate()
        data = self.md.read_bytes()
        self.assertNotIn(b"\r", data, "a platform newline translation crept in")
        self.assertTrue(data.endswith(b"\n"))
        data.decode("utf-8")

    def test_NC9_rendering_is_deterministic_across_processes_and_roots(self):
        """NC9. Twice in separate processes, and from a DIFFERENT absolute root,
        because a path leaking into the output would make every other fixture
        comparison accidentally true."""
        first, second = self.canonical(), self.canonical()
        self.assertEqual(first, second)
        other = Path(tempfile.mkdtemp(prefix="registry-freshness-other-root-"))
        self.addCleanup(shutil.rmtree, other, ignore_errors=True)
        elsewhere = other / "deeper" / "still-deeper"
        shutil.copytree(self.root, elsewhere)
        probe = subprocess.run(
            [sys.executable, "-c",
             "import sys;sys.path.insert(0,'experiments');"
             "import importlib.util as u;"
             f"s=u.spec_from_file_location('rr','{elsewhere / REGISTRY_REL}');"
             "m=u.module_from_spec(s);s.loader.exec_module(m);"
             "sys.stdout.write(m.render_markdown(m.build()))"],
            cwd=elsewhere, capture_output=True, text=True)
        self.assertEqual(probe.returncode, 0, probe.stderr[-2000:])
        self.assertEqual(probe.stdout.encode("utf-8"), first)
        self.assertNotIn(str(self.root), probe.stdout)


class TestFreshnessDoesNotReplaceTheRatchet(RegistryFixtureCase):
    def test_NC13_a_current_artifact_still_fails_a_violated_ratchet(self):
        """NC13. Freshness and safety are different questions. A registry that is
        perfectly up to date with a population that LOST a corroborating home is
        still a regression, and adding a second check may not swallow the first.
        """
        (self.root / "docs" / "N10-NEW.md").write_text(
            "# synthetic\n\n- **F99** — synthetic ruling\n", encoding="utf-8")
        self.stage("docs/N10-NEW.md")
        self.assertEqual(self.registry()["metrics"]["sole_home"], 42,
                         "the rig must actually violate the sole_home ratchet")
        emit = self.run_cli()
        self.assertEqual(emit.returncode, 1, "emission must report the regression")
        self.assertEqual(self.md.read_bytes(), self.canonical(),
                         "the artifact must nonetheless be CURRENT now")

        result = self.run_cli("--check-only")
        self.assertEqual(result.returncode, 1)
        self.assertFreshnessPassed(result)
        self.assertIn("REGRESSION", result.stdout)

    def test_NC13_both_failures_are_reported_together(self):
        (self.root / "docs" / "N10-NEW.md").write_text(
            "# synthetic\n\n- **F99** — synthetic ruling\n", encoding="utf-8")
        self.stage("docs/N10-NEW.md")
        result = self.run_cli("--check-only")
        self.assertEqual(result.returncode, 1)
        self.assertIn("REGRESSION", result.stdout)
        self.assertIn("STALE REGISTRY", result.stderr)


class TestTheEnforcementIsTheCLIs(RegistryFixtureCase):
    """NC14. The control that makes every other control in this section mean
    something: if the CLI stops calling the freshness check, the permanent
    stale-artifact tests must turn RED. A helper-only test would sail through a
    guard that is never invoked, and that is exactly the defect P0.3E left
    behind -- `--check-only` was correct about what it did not write, and silent
    about what it did not compare."""

    ANCHOR = "stale = check_markdown_freshness(reg) if args.check_only else None"

    def rigged_source(self) -> Path:
        original = (self.root / REGISTRY_REL).read_text(encoding="utf-8")
        self.assertIn(self.ANCHOR, original,
                      "the rig anchor is gone -- this control is no longer "
                      "aimed at anything")
        rigged = self.root / "tests" / "guards" / "gate2" / "_rigged_registry.py"
        rigged.write_text(original.replace(self.ANCHOR, "stale = None"),
                          encoding="utf-8")
        return rigged

    def test_the_stale_control_goes_GREEN_once_the_call_is_bypassed(self):
        self.md.write_bytes(self.md.read_bytes() + b"\nhand edit\n")
        honest = self.run_cli("--check-only")
        self.assertFreshnessFailed(honest)
        bypassed = self.run_cli("--check-only", source=self.rigged_source())
        self.assertEqual(bypassed.returncode, 0,
                         "with the freshness call removed the stale artifact "
                         "must sail through -- otherwise the permanent tests "
                         "are not testing the call they claim to test")
        self.assertNotIn("STALE REGISTRY", bypassed.stderr)

    def test_the_bypass_is_the_only_difference(self):
        """The rig must remove the CALL, not the tool. A rig that broke the whole
        command would make the control pass for the wrong reason."""
        rigged = self.rigged_source()
        self.assertEqual(self.run_cli("--check-only", source=rigged).returncode, 0)
        self.assertIn("all 5 pinned metrics unchanged",
                      self.run_cli("--check-only", source=rigged).stdout)


class TestTheOtherOptionModesAreUnchanged(RegistryFixtureCase):
    def test_NC16_standalone_check_doc_keeps_its_three_statuses(self):
        blocked = self.run_cli("--check", R8_3_HOME)
        self.assertEqual(blocked.returncode, 1, blocked.stdout)
        self.assertIn("BLOCKED:", blocked.stdout)
        self.assertIn("R8.3", blocked.stdout)

        safe = self.run_cli("--check", "docs/OUT-OF-SCOPE.md")
        self.assertEqual(safe.returncode, 0, safe.stdout)
        self.assertIn("SAFE:", safe.stdout)

        unknown = self.run_cli("--check", "docs/no-such-document.md")
        self.assertEqual(unknown.returncode, 2)
        self.assertIn("not a TRACKED document", unknown.stderr)

    def test_NC16_check_doc_emits_nothing(self):
        before_files, before_index = snapshot(self.watched()), self.index_state()
        result = self.run_cli("--check", R8_3_HOME, spy=True)
        inside = [w for w in result.writes
                  if str(self.root) in w]
        self.assertEqual(inside, [])
        self.assertEqual(snapshot(self.watched()), before_files)
        self.assertEqual(self.index_state(), before_index)

    def test_NC16_the_selftest_is_still_green_and_still_isolated(self):
        before_files, before_index = snapshot(self.watched()), self.index_state()
        result = self.run_cli("--selftest")
        self.assertEqual(result.returncode, 0, result.stdout[-2500:])
        self.assertIn("SELFTEST GREEN", result.stdout)
        self.assertEqual(snapshot(self.watched()), before_files)
        self.assertEqual(self.index_state(), before_index)

    def test_NC16_check_only_refuses_every_other_mode_with_status_2(self):
        """Refused BEFORE any early return, so the freshness promise cannot be
        bypassed by adding a flag. `--selftest` is the sharp one: it returns
        before the registry is ever built, so a combination accepted here would
        report a green `--check-only` that never looked at the artifact."""
        for extra in (["--update-baseline"], ["--check", R8_3_HOME], ["--selftest"]):
            with self.subTest(combination=extra):
                before_files = snapshot(self.watched())
                before_index = self.index_state()
                result = self.run_cli("--check-only", *extra, spy=True)
                self.assertEqual(result.returncode, 2, result.stdout[-1500:])
                self.assertIn("contradict", result.stderr)
                inside = [w for w in result.writes
                          if str(self.root) in w]
                self.assertEqual(inside, [])
                self.assertEqual(snapshot(self.watched()), before_files)
                self.assertEqual(self.index_state(), before_index)


class TestTheGate2RowEnforcesIt(RegistryFixtureCase):
    """NC17. Through the REAL runner, because the row's verdict is what actually
    gates a session -- an exit code measured by calling the tool directly is not
    evidence about the table that calls it."""

    def test_the_row_is_green_on_a_current_artifact(self):
        result = self.run_gate2("--only", "ruling_registry")
        self.assertEqual(result.returncode, 0, result.stdout[-2500:])
        self.assertIn("UNEXPECTED failures              0", result.stdout)

    def test_a_stale_artifact_makes_the_row_UNEXPECTED(self):
        self.md.write_bytes(self.md.read_bytes() + b"\nhand edit\n")
        result = self.run_gate2("--only", "ruling_registry")
        self.assertEqual(result.returncode, 1, result.stdout[-2500:])
        self.assertIn("UNEXPECTED failures              1", result.stdout)
        self.assertIn("ruling_registry", result.stdout)
        self.assertIn("Gate 2 is RED", result.stdout)

    def test_the_row_carries_no_waiver_that_could_excuse_it(self):
        """A KNOWN_EXIT entry would turn the new red back into a green line, so
        the absence of one is part of the control rather than an assumption."""
        known = next(n.value for n in ast.parse(GATE2.read_text(encoding="utf-8")).body
                     if isinstance(n, ast.Assign) and n.targets[0].id == "KNOWN_EXIT")
        self.assertNotIn("ruling_registry", [k.value for k in known.keys])


if __name__ == "__main__":
    unittest.main()
