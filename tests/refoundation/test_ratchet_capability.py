"""C8 step 5: the standing RATCHET, cleanly reimplemented in the permanent package.

Stdlib only, like the rest of this tree.

`experiments/foundry_audit_baseline.py` decides whether a standing audit degraded.
C8.5J moves that capability to `mtj_foundry.ratchet` and repoints all eight
consumers. The legacy module stays BYTE-IDENTICAL and is the executable ORACLE:
every value below is compared against it rather than against a table written by
the same hand that wrote the new code.

## Two things change on purpose, and neither is semantic

* **The baseline is a PARAMETER.** The legacy module derives a repository root at
  import time and keeps the result in a module global. That is layout knowledge
  stated outside the layout owner — and, because a global is writable, it doubled
  as the seam two negative controls monkeypatched to redirect a write. The
  permanent module takes the baseline as the first argument of every entry point,
  and `ProjectPaths.foundry_audit_baseline` is where the one repository-relative
  fact now lives.
* **`direction()` is public.** It was `_direction` and was imported through the
  underscore anyway, by `foundry_locality.assert_ratchet_directions()`. A consumer
  that must cross an underscore to do its job is the surface telling you it is
  wrong. The function is unchanged.

## What must NOT change

DIFFERENTIAL EQUALITY PROVES CONSERVATION, NOT CORRECTNESS. Equality with the
oracle is necessary and is not sufficient, so three properties are asserted
DIRECTLY as well:

  1. the marker tables' exact membership, cardinality and order — they are
     incident-derived evidence, and several entries record a collision avoided on
     purpose (`ambiguous` deliberately absent; `addressable_missing` deliberately
     a full metric name rather than the bare word `missing`);
  2. fail-closed behaviour on a missing, unreadable, malformed or non-object
     baseline — a ratchet that reported success because it could not find its
     control input would be worse than no ratchet at all;
  3. that all eight consumers actually route through the new module and none
     restates the baseline path.
"""

from __future__ import annotations

import ast
import contextlib
import hashlib
import importlib.util
import inspect
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT

from mtj_foundry import ratchet
from mtj_foundry.paths import ProjectPaths

PATHS = ProjectPaths.for_root(REPO_ROOT)
EXPERIMENTS = PATHS.legacy_experiments
LEGACY_PATH = EXPERIMENTS / "foundry_audit_baseline.py"
TRACKED = PATHS.foundry_audit_baseline

# The bytes P0.3A captured and P0.3D cut over to. C8.5J must not move them.
CAPTURED_SHA256 = "51fca1518813760108ac44cb553e4bd8c2bcff48a2312b9054b3af1f5ad07601"
CAPTURED_SIZE = 4324

# The exact eight consumers C8.5J migrates, and the ratchet section each pins.
CONSUMERS = {
    "foundry_definition_drift": "definition_drift",
    "foundry_ground_truth": "ground_truth_wide",
    "foundry_locality": "locality",
    "foundry_punctuation_audit": "conservation",
    "foundry_visibility_audit": "visibility",
    "foundry_object_lattice": "object_lattice",
    "foundry_ruling_registry": "ruling_registry",
    "foundry_reachability": "reachability",
}

BASELINE_FILENAME = "foundry-audit-baseline.json"

# The consumers authorized to bind ONE `ProjectPaths` view rather than stating
# `ProjectPaths.for_root(fc.REPO_ROOT)` inline (C8.5K). A consumer earns this by
# owning MORE THAN ONE path on the view: `foundry_ruling_registry` owns the
# ratchet baseline and its generated JSON, and constructing the view twice would
# add a second boundary load and move the delegation census. The set is pinned
# so a consumer cannot drift into the bound form without a reason.
ONE_VIEW_CONSUMERS = {"foundry_ruling_registry"}


def load_oracle():
    """The legacy module, by PATH, with no `sys.path` mutation.

    Each call returns a FRESH module object, so a test that repoints one copy
    cannot leak into another.
    """
    spec = importlib.util.spec_from_file_location("legacy_audit_baseline", LEGACY_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def document() -> dict:
    return json.loads(TRACKED.read_text(encoding="utf-8"))


def dotted_numeric_keys() -> list[str]:
    """Every dotted numeric key the tracked baseline actually carries."""
    keys = []
    for section, body in sorted(document().items()):
        keys += sorted(ratchet._flatten(body, section + "."))
    return keys


def mutations(metrics: dict):
    """(label, metrics) over the controlled mutation family.

    Clean, then +1 / -1 / removal of every numeric leaf, then one newly appeared
    metric. `+1` and `-1` are both generated for every leaf on purpose: which of
    the two is a regression is exactly what `direction()` decides, so a family
    that moved every metric one way would exercise one arm only.
    """
    yield "clean", dict(metrics)
    for key, value in sorted(metrics.items()):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            continue
        up = dict(metrics); up[key] = value + 1
        yield f"+1 {key}", up
        down = dict(metrics); down[key] = value - 1
        yield f"-1 {key}", down
        gone = dict(metrics); gone.pop(key)
        yield f"removed {key}", gone
    fresh = dict(metrics); fresh["brand_new_metric"] = 7
    yield "new metric", fresh


class RatchetTestCase(unittest.TestCase):
    """Every case works on a COPY. The tracked control input is never written.

    `tearDown` re-asserts that, so a test that accidentally reached the real file
    fails on its own rather than leaving the next one to find the damage.
    """

    def setUp(self):
        self.oracle = load_oracle()
        self.before = sha256_of(TRACKED)

    def tearDown(self):
        self.assertEqual(sha256_of(TRACKED), self.before,
                         "a ratchet test wrote the TRACKED control input")

    def copy_of_tracked(self) -> Path:
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        target = root / BASELINE_FILENAME
        shutil.copy2(TRACKED, target)
        return target

    def fixture(self, document: dict) -> Path:
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        target = root / BASELINE_FILENAME
        target.write_text(json.dumps(document), encoding="utf-8")
        return target

    def oracle_at(self, path: Path):
        """The oracle, pointed at a fixture through its module global."""
        module = load_oracle()
        module.BASELINE = path
        return module


# ---------------------------------------------------------------------------
# The permanent surface
# ---------------------------------------------------------------------------


class TestThePermanentPublicAPI(RatchetTestCase):
    # Annotations are strings: the module carries `from __future__ import
    # annotations`, so `inspect.signature` reports the SOURCE spelling. Pinning
    # the rendered text rather than a normalized form is deliberate — it is the
    # spelling a consumer reads.
    EXPECTED = {
        "load": "(baseline: 'Path', section: 'str') -> 'dict | None'",
        "save": "(baseline: 'Path', section: 'str', metrics: 'dict') -> 'None'",
        "direction": "(key: 'str') -> 'int'",
        "compare": "(baseline: 'Path', section: 'str', metrics: 'dict', update: 'bool' = False)",
        "report": "(baseline: 'Path', section: 'str', metrics: 'dict', update: 'bool' = False) -> 'int'",
    }

    # Every entry point that TOUCHES the baseline takes it as its first
    # positional argument. `direction` is the one that does not, because it
    # reads no file — it is a pure lookup against the marker tables.
    TAKE_A_BASELINE = ("load", "save", "compare", "report")

    def test_the_public_api_is_exactly_the_six_ratified_names(self):
        self.assertEqual(sorted(ratchet.__all__),
                         ["BaselineUnavailable", "compare", "direction", "load",
                          "report", "save"])

    def test_every_public_signature_is_the_ratified_shape(self):
        for name, expected in self.EXPECTED.items():
            with self.subTest(name=name):
                self.assertEqual(str(inspect.signature(getattr(ratchet, name))),
                                 expected)

    def test_the_baseline_is_the_FIRST_POSITIONAL_argument_of_every_reader(self):
        """Asserted structurally as well as textually: the explicit seam is the
        point of the slice, and a keyword-only or defaulted baseline would
        quietly re-admit an implicit one."""
        for name in self.TAKE_A_BASELINE:
            with self.subTest(name=name):
                params = list(inspect.signature(getattr(ratchet, name)).parameters.values())
                self.assertEqual(params[0].name, "baseline")
                self.assertEqual(params[0].kind, inspect.Parameter.POSITIONAL_OR_KEYWORD)
                self.assertIs(params[0].default, inspect.Parameter.empty)
        self.assertNotIn("baseline",
                         inspect.signature(ratchet.direction).parameters)

    def test_there_is_no_public_or_mutable_BASELINE_global(self):
        """The seam C8.5J removes. A module global that a caller can rebind is
        both a layout statement outside the layout owner and a monkeypatch
        target; the argument replaces both jobs.

        Imported NAMES are excluded rather than counted: `json` and `Path` are
        in `vars()` because the module imports them, and a first version of this
        test reported them as public state. A probe is code and gets audited
        like code.
        """
        self.assertFalse(hasattr(ratchet, "BASELINE"))
        imported = {a.asname or a.name.split(".")[0]
                    for n in ast.walk(ast.parse(inspect.getsource(ratchet)))
                    if isinstance(n, ast.Import) for a in n.names}
        imported |= {a.asname or a.name
                     for n in ast.walk(ast.parse(inspect.getsource(ratchet)))
                     if isinstance(n, ast.ImportFrom) for a in n.names}
        public = {n for n in vars(ratchet)
                  if not n.startswith("_") and n not in imported}
        self.assertEqual(public - set(ratchet.__all__), set())

        # And no public name is plain DATA. Everything exported is a function or
        # the error class; a rebindable value would be the old seam returning.
        for name in ratchet.__all__:
            with self.subTest(name=name):
                self.assertTrue(callable(getattr(ratchet, name)))

    def test_the_module_states_no_repository_path_at_module_level(self):
        """Nothing here may know where the repository is. Asserted of the AST,
        so a path built at import time is caught even if nothing reads it."""
        tree = ast.parse((PATHS.src / "mtj_foundry" / "ratchet.py")
                         .read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.Assign):
                src = ast.unparse(node.value)
                with self.subTest(assign=ast.unparse(node.targets[0])):
                    self.assertNotIn("__file__", src)
                    self.assertNotIn("Path(", src)
                    self.assertNotIn(BASELINE_FILENAME, src)

    def test_it_imports_neither_the_legacy_tree_nor_AQ4(self):
        tree = ast.parse((PATHS.src / "mtj_foundry" / "ratchet.py")
                         .read_text(encoding="utf-8"))
        modules = {n.module for n in ast.walk(tree)
                   if isinstance(n, ast.ImportFrom) and n.module}
        modules |= {a.name for n in ast.walk(tree)
                    if isinstance(n, ast.Import) for a in n.names}
        self.assertEqual(modules, {"__future__", "json", "pathlib"})

    def test_it_never_mutates_sys_path(self):
        """Asked of the AST. The module DOCSTRING says it does not touch
        `sys.path`, so a substring search reads that sentence as a violation --
        the same shape as the reachability guard that had to stop grepping for
        `WORSE_IF_DOWN`. What must be absent is a CALL."""
        tree = ast.parse((PATHS.src / "mtj_foundry" / "ratchet.py")
                         .read_text(encoding="utf-8"))
        calls = [ast.unparse(n) for n in ast.walk(tree)
                 if isinstance(n, ast.Call)
                 and "sys.path" in ast.unparse(n)]
        self.assertEqual(calls, [])
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        self.assertNotIn("sys", names)


class TestTheLayoutOwnerOwnsTheBaselinePath(RatchetTestCase):
    def test_the_property_resolves_exactly(self):
        paths = ProjectPaths.for_root("/r")
        self.assertEqual(paths.foundry_audit_baseline,
                         Path("/r") / "config" / "baselines" / BASELINE_FILENAME)

    def test_it_is_derived_from_the_baselines_directory_not_restated(self):
        paths = ProjectPaths.for_root("/r")
        self.assertEqual(paths.foundry_audit_baseline.parent, paths.baselines)

    def test_it_names_the_file_the_legacy_module_already_read(self):
        """The cutover must not move the control input by one character."""
        self.assertEqual(PATHS.foundry_audit_baseline, self.oracle.BASELINE)

    def test_the_tracked_control_input_is_the_captured_bytes(self):
        self.assertEqual(sha256_of(TRACKED), CAPTURED_SHA256)
        self.assertEqual(TRACKED.stat().st_size, CAPTURED_SIZE)


# ---------------------------------------------------------------------------
# The marker tables are EVIDENCE
# ---------------------------------------------------------------------------


class TestTheDirectionMarkersWereCarriedNotRegenerated(RatchetTestCase):
    """Every marker was added by a named incident. Membership, cardinality AND
    ORDER are pinned: order is what makes UP-before-DOWN precedence meaningful,
    and a reordered table would pass a set comparison."""

    def test_the_UP_table_is_identical_to_the_oracle(self):
        self.assertEqual(ratchet._WORSE_IF_UP, tuple(self.oracle.WORSE_IF_UP))
        self.assertEqual(len(ratchet._WORSE_IF_UP), 14)

    def test_the_DOWN_table_is_identical_to_the_oracle(self):
        self.assertEqual(ratchet._WORSE_IF_DOWN, tuple(self.oracle.WORSE_IF_DOWN))
        self.assertEqual(len(ratchet._WORSE_IF_DOWN), 15)

    def test_the_deliberate_absences_are_still_absent(self):
        """`ambiguous` was NOT added because it collides with the pre-existing
        `ground_truth_wide.head_ambiguous`, and flipping that metric from neutral
        to fatal would change another consumer's semantics as a side effect. A
        regenerated table would have "tidied" this in."""
        both = ratchet._WORSE_IF_UP + ratchet._WORSE_IF_DOWN
        self.assertNotIn("ambiguous", both)
        self.assertNotIn("missing", both)

    def test_the_narrow_marker_is_still_the_full_metric_name(self):
        """`addressable_missing`, not `missing`: markers match as substrings of
        the whole dotted key, and a bare `missing` would flip
        `family_sweep.missing_from_ratified` and `batch8_diff.n_missing` from
        neutral to fatal the day anyone pinned them."""
        self.assertIn("addressable_missing", ratchet._WORSE_IF_UP)

    def test_the_provenance_comments_travelled_with_the_memberships(self):
        """A marker without its incident is a constant nobody can re-decide."""
        source = (PATHS.src / "mtj_foundry" / "ratchet.py").read_text(encoding="utf-8")
        for anchor in ("2026-08-13", "2026-08-09", "e780842",
                       "OBJECT-LATTICE-RESIDUAL-RULING-2026-08-13.md",
                       "assert_ratchet_directions", "621 lines"):
            with self.subTest(anchor=anchor):
                self.assertIn(anchor, source)


# ---------------------------------------------------------------------------
# Differential against the oracle
# ---------------------------------------------------------------------------


class TestTheDirectionDifferential(RatchetTestCase):
    def test_every_dotted_numeric_key_in_the_tracked_baseline_agrees(self):
        keys = dotted_numeric_keys()
        self.assertGreater(len(keys), 100)
        mismatches = [k for k in keys
                      if self.oracle._direction(k) != ratchet.direction(k)]
        self.assertEqual(mismatches, [])

    def test_the_public_name_is_the_same_function_the_oracle_kept_private(self):
        self.assertEqual(inspect.getsource(ratchet.direction).count("_WORSE_IF_UP"), 1)
        for key in ("locality.stored_owned", "locality.stored_mismatch",
                    "locality.addressable_missing", "locality.owned"):
            with self.subTest(key=key):
                self.assertEqual(ratchet.direction(key), self.oracle._direction(key))


class TestTheAdversarialDirectionFixtures(RatchetTestCase):
    def test_a_key_carrying_BOTH_markers_resolves_UP_because_UP_IS_CHECKED_FIRST(self):
        """`conservation.unrouted_lines` carries `unrouted` (UP) and `lines`
        (DOWN). PRECEDENCE is the reason it resolves UP — not specificity, not
        ordering within a table, not the leaf. Both markers are asserted present
        so the collision is real and not assumed."""
        key = "conservation.unrouted_lines"
        self.assertIn("unrouted", ratchet._WORSE_IF_UP)
        self.assertIn("lines", ratchet._WORSE_IF_DOWN)
        self.assertTrue(any(m in key for m in ratchet._WORSE_IF_UP))
        self.assertTrue(any(m in key for m in ratchet._WORSE_IF_DOWN))
        self.assertEqual(ratchet.direction(key), 1)
        self.assertEqual(ratchet.direction(key), self.oracle._direction(key))

    def test_an_UP_only_key(self):
        self.assertEqual(ratchet.direction("visibility.uncontexted"), 1)

    def test_a_DOWN_only_key(self):
        self.assertEqual(ratchet.direction("ruling_registry.documents"), -1)

    def test_a_NEUTRAL_key(self):
        self.assertEqual(ratchet.direction("locality.ambiguous"), 0)
        self.assertEqual(ratchet.direction("reachability.entry_points"), 0)

    def test_a_nested_key_whose_LEAF_carries_no_marker(self):
        """`class_unrouted.comma` is the recorded defect: the first version
        matched the leaf only, so this resolved NEUTRAL and a negative control
        that pushed the class 621 lines the wrong way exited 0."""
        self.assertEqual(ratchet.direction("comma"), 0)
        self.assertEqual(ratchet.direction("conservation.class_unrouted.comma"), 1)

    def test_the_reaching_arm_the_product_audit_rides(self):
        self.assertEqual(ratchet.direction("reachability.artifacts_reaching_product"), -1)
        self.assertEqual(ratchet.direction("reachability.artifacts_orphaned"), 1)


class TestTheWholeBaselineLoadDifferential(RatchetTestCase):
    def test_all_eight_sections_load_identically(self):
        sections = sorted(document())
        self.assertEqual(sections, ["conservation", "definition_drift",
                                    "ground_truth_wide", "locality",
                                    "object_lattice", "reachability",
                                    "ruling_registry", "visibility"])
        for section in sections:
            with self.subTest(section=section):
                self.assertEqual(ratchet.load(TRACKED, section),
                                 self.oracle.load(section))

    def test_an_absent_section_is_None_on_both(self):
        self.assertIsNone(ratchet.load(TRACKED, "no_such_section"))
        self.assertIsNone(self.oracle.load("no_such_section"))


class TestTheCompareAndReportDifferential(RatchetTestCase):
    """The mutation family, section by section, through both implementations."""

    def cases(self):
        doc = document()
        for section, metrics in sorted(doc.items()):
            for label, mutated in mutations(metrics):
                yield section, label, mutated

    def test_compare_agrees_on_every_mutation(self):
        oracle = self.oracle_at(self.copy_of_tracked())
        copy = self.copy_of_tracked()
        n = 0
        for section, label, metrics in self.cases():
            n += 1
            with self.subTest(section=section, mutation=label):
                self.assertEqual(ratchet.compare(copy, section, metrics),
                                 oracle.compare(section, metrics))
        self.assertGreater(n, 100)

    def test_report_agrees_on_stdout_AND_return_for_every_mutation(self):
        """Return value alone would miss a formatting change, and printed text
        alone would miss the exit status. Both, on purpose."""
        oracle = self.oracle_at(self.copy_of_tracked())
        copy = self.copy_of_tracked()
        for section, label, metrics in self.cases():
            with self.subTest(section=section, mutation=label):
                a, b = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(a):
                    ra = oracle.report(section, metrics)
                with contextlib.redirect_stdout(b):
                    rb = ratchet.report(copy, section, metrics)
                self.assertEqual((ra, a.getvalue()), (rb, b.getvalue()))

    def test_the_four_representative_verdicts_are_reachable_and_distinct(self):
        """A differential over cases that are all the same shape proves little."""
        path = self.fixture({"s": {"lines": 10, "unrouted": 1}})
        buffers = {}
        for label, metrics in (("clean", {"lines": 10, "unrouted": 1}),
                               ("change", {"lines": 11, "unrouted": 1}),
                               ("regression", {"lines": 10, "unrouted": 2})):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = ratchet.report(path, "s", metrics)
            buffers[label] = (rc, buf.getvalue())
        first_run = io.StringIO()
        with contextlib.redirect_stdout(first_run):
            rc = ratchet.report(path, "unpinned", {"lines": 1})
        buffers["first_run"] = (rc, first_run.getvalue())

        self.assertEqual(buffers["clean"][0], 0)
        self.assertIn("unchanged", buffers["clean"][1])
        self.assertEqual(buffers["change"][0], 0)
        self.assertIn("◐", buffers["change"][1])
        self.assertEqual(buffers["regression"][0], 1)
        self.assertIn("✗", buffers["regression"][1])
        self.assertIn("--update-baseline", buffers["regression"][1])
        self.assertEqual(buffers["first_run"][0], 0)
        self.assertIn("no baseline pinned", buffers["first_run"][1])
        self.assertEqual(len({v[1] for v in buffers.values()}), 4)


class TestTheMovementSemantics(RatchetTestCase):
    def test_a_disappeared_metric_is_a_REGRESSION_whatever_its_direction(self):
        """A number that stops being emitted stops being watched."""
        path = self.fixture({"s": {"lines": 10, "unrouted": 1, "neutral_thing": 5}})
        for key in ("lines", "unrouted", "neutral_thing"):
            with self.subTest(key=key):
                metrics = {"lines": 10, "unrouted": 1, "neutral_thing": 5}
                metrics.pop(key)
                regressions, changes, _ = ratchet.compare(path, "s", metrics)
                self.assertEqual([k for k, *_ in regressions], [key])
                self.assertIn("DISAPPEARED", regressions[0][3])

    def test_a_new_metric_is_a_CHANGE_and_not_a_regression(self):
        path = self.fixture({"s": {"lines": 10}})
        regressions, changes, _ = ratchet.compare(
            path, "s", {"lines": 10, "unrouted": 4})
        self.assertEqual(regressions, [])
        self.assertEqual([k for k, *_ in changes], ["unrouted"])
        self.assertIn("new metric", changes[0][3])

    def test_movement_in_the_better_direction_is_reported_not_fatal(self):
        path = self.fixture({"s": {"unrouted": 10}})
        regressions, changes, _ = ratchet.compare(path, "s", {"unrouted": 9})
        self.assertEqual(regressions, [])
        self.assertEqual([k for k, *_ in changes], ["unrouted"])

    def test_an_empty_section_document_and_empty_metrics(self):
        path = self.fixture({"s": {}})
        self.assertEqual(ratchet.load(path, "s"), {})
        self.assertEqual(ratchet.compare(path, "s", {}), ([], [], None))

    def test_an_empty_metrics_dict_against_a_pinned_section_loses_everything(self):
        path = self.fixture({"s": {"lines": 1, "unrouted": 2}})
        regressions, changes, _ = ratchet.compare(path, "s", {})
        self.assertEqual(sorted(k for k, *_ in regressions), ["lines", "unrouted"])


class TestFlatteningAdmitsOnlyNumbers(RatchetTestCase):
    PROBE = {"an_int": 1, "a_float": 1.5, "a_str": "x", "a_list": [1],
             "a_none": None, "nested": {"an_int": 2, "a_str": "y"}}

    def test_only_numeric_leaves_become_metrics(self):
        self.assertEqual(ratchet._flatten(self.PROBE),
                         {"an_int": 1, "a_float": 1.5, "nested.an_int": 2})

    def test_it_agrees_with_the_oracle(self):
        self.assertEqual(ratchet._flatten(self.PROBE),
                         self.oracle._flatten(self.PROBE))

    def test_a_nonnumeric_leaf_cannot_become_a_regression(self):
        """It cannot move in a direction, so admitting one would produce a key
        `compare()` could only ever call 'changed'."""
        path = self.fixture({"s": {"note": "before", "lines": 1}})
        regressions, changes, _ = ratchet.compare(
            path, "s", {"note": "after", "lines": 1})
        self.assertEqual((regressions, changes), ([], []))


# ---------------------------------------------------------------------------
# Fail-closed
# ---------------------------------------------------------------------------


class TestTheBaselineFailsClosed(RatchetTestCase):
    """A ratchet that reported success because it could not read its control
    input would be worse than no ratchet at all. Both entry points, all four
    damaged states, and the oracle agrees on every one."""

    def damaged(self):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        missing = root / "absent.json"
        invalid = root / "invalid.json"; invalid.write_text("{ not json", encoding="utf-8")
        array = root / "array.json"; array.write_text("[1, 2]", encoding="utf-8")
        scalar = root / "scalar.json"; scalar.write_text("42", encoding="utf-8")
        return {"missing": missing, "invalid_json": invalid,
                "non_object_array": array, "non_object_scalar": scalar}

    def test_load_raises_rather_than_returning_an_empty_document(self):
        for label, path in self.damaged().items():
            with self.subTest(state=label):
                with self.assertRaises(ratchet.BaselineUnavailable):
                    ratchet.load(path, "conservation")

    def test_save_refuses_rather_than_creating_a_fresh_baseline(self):
        """Writing a new file would silently drop every other section's pins and
        leave each reading as 'not pinned yet' — a one-command way to un-ratchet
        the whole suite while looking like an update."""
        for label, path in self.damaged().items():
            with self.subTest(state=label):
                with self.assertRaises(ratchet.BaselineUnavailable):
                    ratchet.save(path, "conservation", {"lines": 1})
        self.assertFalse(self.damaged()["missing"].exists())

    def test_compare_and_report_propagate_the_halt(self):
        missing = self.damaged()["missing"]
        with self.assertRaises(ratchet.BaselineUnavailable):
            ratchet.compare(missing, "conservation", {"lines": 1})
        with self.assertRaises(ratchet.BaselineUnavailable):
            with contextlib.redirect_stdout(io.StringIO()):
                ratchet.report(missing, "conservation", {"lines": 1})

    def test_the_oracle_fails_closed_in_exactly_the_same_states(self):
        for label, path in self.damaged().items():
            with self.subTest(state=label):
                oracle = self.oracle_at(path)
                with self.assertRaises(oracle.BaselineUnavailable):
                    oracle.load("conservation")
                with self.assertRaises(oracle.BaselineUnavailable):
                    oracle.save("conservation", {"lines": 1})

    def test_a_missing_SECTION_is_still_a_first_run_and_is_NOT_fatal(self):
        """The distinction the halt exists to draw. An unpinned section really
        is a first run; a missing FILE is a broken checkout."""
        path = self.copy_of_tracked()
        self.assertIsNone(ratchet.load(path, "never_pinned"))
        regressions, changes, note = ratchet.compare(path, "never_pinned", {"lines": 1})
        self.assertEqual((regressions, changes), ([], []))
        self.assertIn("no baseline pinned", note)


class TestSavePreservesEverythingItWasNotAskedToChange(RatchetTestCase):
    def test_saving_one_section_leaves_the_other_seven_byte_intact(self):
        original = document()
        path = self.copy_of_tracked()
        ratchet.save(path, "conservation", {"lines": 1})
        after = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(sorted(after), sorted(original))
        self.assertEqual(len(after) - 1, 7)
        for section in original:
            if section == "conservation":
                continue
            with self.subTest(section=section):
                self.assertEqual(after[section], original[section])
        self.assertEqual(after["conservation"], {"lines": 1})

    def test_update_True_writes_through_compare_and_preserves_the_rest(self):
        original = document()
        path = self.copy_of_tracked()
        regressions, changes, note = ratchet.compare(
            path, "visibility", {"options": 1}, update=True)
        self.assertEqual((regressions, changes), ([], []))
        self.assertIn("PINNED", note)
        after = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(after["visibility"], {"options": 1})
        self.assertEqual(after["conservation"], original["conservation"])

    def test_saving_the_same_metrics_twice_is_byte_identical(self):
        path = self.copy_of_tracked()
        ratchet.save(path, "s", {"lines": 2})
        first = path.read_bytes()
        ratchet.save(path, "s", {"lines": 2})
        self.assertEqual(path.read_bytes(), first)

    def test_the_serialization_matches_the_oracle_byte_for_byte(self):
        mine, theirs = self.copy_of_tracked(), self.copy_of_tracked()
        ratchet.save(mine, "conservation", {"lines": 3, "unrouted": 4})
        self.oracle_at(theirs).save("conservation", {"lines": 3, "unrouted": 4})
        self.assertEqual(mine.read_bytes(), theirs.read_bytes())


# ---------------------------------------------------------------------------
# The consumers
# ---------------------------------------------------------------------------


class TestAllEightConsumersRouteThroughThePermanentModule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.sources = {name: (EXPERIMENTS / f"{name}.py").read_text(encoding="utf-8")
                       for name in CONSUMERS}

    def test_none_of_them_imports_the_legacy_module_at_runtime(self):
        """Prose may still name it — it is the oracle and the history. What must
        be gone is the IMPORT, so this is asked of the AST."""
        for name, source in self.sources.items():
            with self.subTest(consumer=name):
                tree = ast.parse(source)
                imported = {a.name for n in ast.walk(tree)
                            if isinstance(n, ast.Import) for a in n.names}
                imported |= {n.module for n in ast.walk(tree)
                             if isinstance(n, ast.ImportFrom) and n.module}
                self.assertNotIn("foundry_audit_baseline", imported)

    def test_each_of_them_imports_the_permanent_module(self):
        for name, source in self.sources.items():
            with self.subTest(consumer=name):
                self.assertIn("from mtj_foundry import ratchet", source)

    def test_each_of_them_obtains_the_baseline_from_the_layout_owner(self):
        """All eight reach the baseline through a ProjectPaths view built from
        the boundary's root. Seven state it inline; one binds the view first.

        C8.5K RE-AIMS THIS GUARD WITHOUT WEAKENING IT. The C8.5J form required
        the inline expression LITERALLY in all eight, which was correct while all
        eight owned exactly one path. `foundry_ruling_registry` now owns two --
        the ratchet baseline and its generated JSON -- and building the view
        twice would add a second `fc.REPO_ROOT` load, moving the delegation
        census for no reason. So that one consumer binds the view once and reads
        both properties off it.

        What is asserted is therefore the PROPERTY rather than one spelling of
        it: the baseline comes from `.foundry_audit_baseline` on a ProjectPaths
        made from the boundary root, in every one of the eight. The inline form
        is still required exactly for the seven that have no reason to change.
        """
        for name, source in self.sources.items():
            with self.subTest(consumer=name):
                if name in ONE_VIEW_CONSUMERS:
                    view = self.bound_view_name(source)
                    self.assertIsNotNone(
                        view, f"{name} binds no module-scope ProjectPaths view")
                    self.assertIn(f"RATCHET_BASELINE = {view}.foundry_audit_baseline",
                                  source)
                else:
                    self.assertIn(
                        "RATCHET_BASELINE = ProjectPaths.for_root(fc.REPO_ROOT)"
                        ".foundry_audit_baseline", source)

    def bound_view_name(self, source: str):
        """The name bound to a module-scope `ProjectPaths.for_root(fc.REPO_ROOT)`.

        Exactly one such binding is permitted: two would be two boundary loads
        wearing one name, which is the census movement this arrangement exists to
        avoid. Returns None when there is no binding at all.
        """
        tree = ast.parse(source)
        bindings = [n for n in tree.body if isinstance(n, ast.Assign)
                    and ast.unparse(n.value) == "ProjectPaths.for_root(fc.REPO_ROOT)"]
        if not bindings:
            return None
        self.assertEqual(len(bindings), 1, "more than one bound ProjectPaths view")
        targets = bindings[0].targets
        self.assertEqual(len(targets), 1)
        self.assertIsInstance(targets[0], ast.Name)
        return targets[0].id

    def test_the_one_bound_view_consumer_builds_exactly_one_view(self):
        """The whole reason the bound form is allowed. A second construction
        would be a second `fc.REPO_ROOT` delegation row."""
        for name in ONE_VIEW_CONSUMERS:
            with self.subTest(consumer=name):
                source = self.sources[name]
                self.assertEqual(
                    source.count("ProjectPaths.for_root("), 1,
                    "the bound-view consumer must construct exactly one view")

    def test_none_of_them_restates_the_baseline_filename_or_path(self):
        for name, source in self.sources.items():
            with self.subTest(consumer=name):
                self.assertNotIn(BASELINE_FILENAME, source)
                self.assertNotIn("config/baselines", source)

    def test_none_of_them_reaches_the_boundarys_PRIVATE_paths_instance(self):
        """`fc._PATHS` is a temporary compatibility implementation detail. Using
        it would turn it into a cross-module layout API by accident."""
        for name, source in self.sources.items():
            with self.subTest(consumer=name):
                self.assertNotIn("_PATHS", source)

    def test_none_of_them_added_a_bootstrap(self):
        """The package is reachable because `foundry_common` puts `src` on the
        path. A consumer that added its own would make that invisible."""
        for name, source in self.sources.items():
            with self.subTest(consumer=name):
                tree = ast.parse(source)
                inserts = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                           and isinstance(n.func, ast.Attribute)
                           and n.func.attr in ("insert", "append")
                           and isinstance(n.func.value, ast.Attribute)
                           and n.func.value.attr == "path"]
                self.assertLessEqual(len(inserts), 1)
                for node in inserts:
                    self.assertNotIn("src", ast.unparse(node))

    def test_every_consumer_establishes_foundry_common_before_mtj_foundry(self):
        """ORDER IS LOAD-BEARING IN ALL EIGHT, and it is the whole reason
        `foundry_ruling_registry` grew a `foundry_common` import it never had:
        that module's imports were alphabetical and it reached the package
        through no boundary at all."""
        for name, source in self.sources.items():
            with self.subTest(consumer=name):
                tree = ast.parse(source)
                lines = [(n.lineno, a.name) for n in ast.walk(tree)
                         if isinstance(n, ast.Import) for a in n.names]
                lines += [(n.lineno, n.module) for n in ast.walk(tree)
                          if isinstance(n, ast.ImportFrom) and n.module]
                common = [ln for ln, mod in lines if mod == "foundry_common"]
                package = [ln for ln, mod in lines
                           if mod.split(".")[0] == "mtj_foundry"]
                self.assertEqual(len(common), 1, "foundry_common import count moved")
                self.assertTrue(package)
                self.assertLess(common[0], min(package))

    def test_each_consumer_calls_the_ratchet_with_its_own_section(self):
        for name, section in CONSUMERS.items():
            with self.subTest(consumer=name):
                tree = ast.parse(self.sources[name])
                calls = [ast.unparse(n) for n in ast.walk(tree)
                         if isinstance(n, ast.Call)
                         and isinstance(n.func, ast.Attribute)
                         and isinstance(n.func.value, ast.Name)
                         and n.func.value.id == "ratchet"]
                self.assertTrue(calls, f"{name} makes no ratchet call")
                self.assertTrue(any(repr(section) in c for c in calls), calls)
                for call in calls:
                    if call.startswith("ratchet.direction("):
                        continue      # a pure lookup; it reads no baseline
                    self.assertTrue(
                        "RATCHET_BASELINE" in call or "tmp" in call
                        or "masked_baseline" in call, call)

    def test_each_consumer_keeps_its_update_baseline_flag(self):
        for name, source in self.sources.items():
            with self.subTest(consumer=name):
                self.assertIn('"--update-baseline"', source)

    def test_the_ruling_registry_docs_knowledge_is_untouched(self):
        """The one consumer whose import block had to be restructured. Its
        output-DOCUMENT knowledge is Step-6 scope and stays exactly as it was.

        C8.5K CORRECTS THIS PIN'S AIM. The C8.5J form froze `OUT_JSON` alongside
        the three `docs/` facts, which over-reached by one line: the generated
        JSON is a Step-5 layout site, not Step-6 document knowledge, and C8.5K
        exists to give it an owner. The three genuine Step-6 facts are still
        pinned verbatim -- and `OUT_MD`, which the old form omitted, is added, so
        the frozen set is now complete rather than merely unchanged.
        """
        source = self.sources["foundry_ruling_registry"]
        for line in ('REPO_ROOT = Path(__file__).resolve().parent.parent',
                     'DOCS = REPO_ROOT / "docs"',
                     'OUT_MD = DOCS / "RATIFIED-RULINGS-REGISTRY.md"'):
            with self.subTest(line=line):
                self.assertIn(line, source)

    def test_the_ruling_registry_generated_output_comes_from_the_layout_owner(self):
        """What replaced the obsolete `OUT_JSON` literal pin (C8.5K).

        The old assertion said "this restatement is still here". The Step-5 cut
        makes the opposite true, so the guard now says where the value comes
        from instead -- the same bound view the ratchet baseline uses -- and that
        the restatement is gone.
        """
        source = self.sources["foundry_ruling_registry"]
        view = self.bound_view_name(source)
        self.assertIsNotNone(view)
        self.assertIn(f"OUT_JSON = {view}.legacy_ruling_registry_json", source)
        self.assertNotIn(
            'OUT_JSON = REPO_ROOT / "experiments" / "out" / "foundry" / "ruling_registry.json"',
            source)


class TestTheLegacyOracleIsUntouched(RatchetTestCase):
    def test_it_still_carries_its_own_module_global_and_still_works(self):
        """It is kept as the executable oracle until a separately authorized
        retirement slice, so it must remain runnable, not merely present."""
        self.assertIsInstance(self.oracle.BASELINE, Path)
        self.assertEqual(self.oracle.load("conservation"),
                         ratchet.load(TRACKED, "conservation"))

    def test_nothing_in_the_package_imports_it(self):
        """IMPORTS, not text. `paths.py` legitimately contains the string as the
        name of its new PROPERTY, and `ratchet.py` names the oracle in prose --
        a text search would report both as edges. The package-to-legacy edge
        count is what must be zero."""
        for module in sorted((PATHS.src / "mtj_foundry").glob("*.py")):
            with self.subTest(module=module.name):
                tree = ast.parse(module.read_text(encoding="utf-8"))
                imported = {a.name for n in ast.walk(tree)
                            if isinstance(n, ast.Import) for a in n.names}
                imported |= {n.module for n in ast.walk(tree)
                             if isinstance(n, ast.ImportFrom) and n.module}
                # The invariant is package -> LEGACY TREE, so it is decided by
                # asking whether the imported name IS a legacy module, not by
                # keeping a stdlib allow-list. A first version kept the list and
                # reported `posixpath`/`ntpath` as legacy edges.
                legacy = {m for m in imported
                          if (EXPERIMENTS / f"{m.split('.')[0]}.py").exists()
                          or (EXPERIMENTS / m.split('.')[0]).is_dir()}
                self.assertEqual(legacy, set())
                self.assertNotIn("foundry_audit_baseline", imported)
                self.assertFalse(any("aq4" in m.lower() for m in imported))


if __name__ == "__main__":
    unittest.main()
