"""C8 step 3, one slice: the ratchet baseline is now a TRACKED control input.

Stdlib only, like the rest of this tree.

`experiments/foundry_audit_baseline.py` decides whether a standing audit
degraded. Its baseline lived at `experiments/out/foundry/audit-baseline.json`,
under a `.gitignore` rule — so the control input governing acceptance had no
version history, and a value could change without appearing in any diff. P0.3A
copied the exact bytes to `config/baselines/` and repointed nothing; this is the
cutover, and it changes **no baseline value**.

Two behaviours change and nothing else:

    the storage path              ignored copy -> tracked copy
    a MISSING baseline FILE       green "nothing pinned" -> fatal

The second is the one worth stating twice. `load()` used to return `None` both
for "this section is not pinned yet" and for "the file is not there", and
`compare()` reads `None` as no regressions. A deleted baseline and a first run
were the same green result. An absent **section** still returns `None` — that
case really is a first run, and it is deliberately untouched.

The module is loaded by explicit path rather than through `sys.path`, so these
tests never depend on which directory a runner happened to start in.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import inspect
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT

from mtj_foundry.paths import ProjectPaths

PATHS = ProjectPaths.for_root(REPO_ROOT)
MODULE_PATH = PATHS.legacy_experiments / "foundry_audit_baseline.py"
TRACKED = PATHS.baselines / "foundry-audit-baseline.json"
IGNORED_LEGACY = "experiments/out/foundry/audit-baseline.json"

# The bytes P0.3A captured. The cutover must not move them.
CAPTURED_SHA256 = "51fca1518813760108ac44cb553e4bd8c2bcff48a2312b9054b3af1f5ad07601"
CAPTURED_SIZE = 4324


def load_module():
    """Load the legacy module by PATH, with no `sys.path` mutation.

    Each call returns a FRESH module object. `BASELINE` is a module global that
    `load`/`save` resolve at call time, so a test that repoints one copy cannot
    leak into another — and patching the object the code under test actually
    reaches is the only patch that means anything.
    """
    spec = importlib.util.spec_from_file_location("legacy_audit_baseline", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RatchetTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fab = load_module()
        cls.pinned = json.loads(TRACKED.read_text(encoding="utf-8"))

    def fixture(self, *, tracked: dict, ignored: dict | None = None) -> tuple[Path, Path]:
        """A root holding a tracked baseline and, optionally, an ignored legacy one.

        The ignored copy is written with DIFFERENT values on purpose. A fixture in
        which both files agree cannot tell whether the module read the right one.
        """
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        tracked_path = root / "config" / "baselines" / "foundry-audit-baseline.json"
        tracked_path.parent.mkdir(parents=True)
        tracked_path.write_text(json.dumps(tracked, indent=2, sort_keys=True) + "\n",
                                encoding="utf-8")
        ignored_path = root.joinpath(*IGNORED_LEGACY.split("/"))
        if ignored is not None:
            ignored_path.parent.mkdir(parents=True)
            ignored_path.write_text(json.dumps(ignored, indent=2, sort_keys=True) + "\n",
                                    encoding="utf-8")
        return tracked_path, ignored_path

    def module_at(self, baseline: Path):
        module = load_module()
        module.BASELINE = baseline
        return module


# ---------------------------------------------------------------------------
# The cutover itself
# ---------------------------------------------------------------------------


class TestTheBaselineIsTheTrackedFile(RatchetTestCase):
    def test_the_module_points_at_the_tracked_control_input(self):
        self.assertEqual(self.fab.BASELINE, TRACKED)
        self.assertTrue(self.fab.BASELINE.is_file())

    def test_the_tracked_path_is_not_ignored_by_git(self):
        """The whole point of the move: a change to this file shows up in a diff."""
        ignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("experiments/out/", [line.strip() for line in ignore])
        relative = TRACKED.relative_to(REPO_ROOT).as_posix()
        self.assertTrue(relative.startswith("config/baselines/"))
        self.assertFalse(relative.startswith("experiments/out/"))

    def test_no_code_path_names_the_ignored_baseline_any_more(self):
        """Asserted over CODE string constants, with docstrings excluded — the module
        explains the move in prose, and a prose mention is not a dependency."""
        import ast

        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        docstrings = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                doc = ast.get_docstring(node, clean=False)
                if doc is not None:
                    docstrings.add(doc)
        constants = {n.value for n in ast.walk(tree)
                     if isinstance(n, ast.Constant) and isinstance(n.value, str)}
        code_strings = constants - docstrings
        for forbidden in ("out", "audit-baseline.json"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, code_strings)
        self.assertIn("foundry-audit-baseline.json", code_strings)

    def test_the_tracked_bytes_are_the_p0_3a_capture(self):
        """The cutover repoints storage. It must not touch one value."""
        self.assertEqual(sha256_of(TRACKED), CAPTURED_SHA256)
        self.assertEqual(TRACKED.stat().st_size, CAPTURED_SIZE)

    def test_the_live_baseline_still_holds_every_pinned_section(self):
        self.assertGreaterEqual(len(self.pinned), 8)
        for section, metrics in self.pinned.items():
            with self.subTest(section=section):
                self.assertEqual(self.fab.load(section), metrics)

    def test_the_live_baseline_compares_clean_against_itself(self):
        """An invariance check on real data: nothing pinned reads as moved."""
        for section, metrics in self.pinned.items():
            regressions, changes, note = self.fab.compare(section, metrics)
            with self.subTest(section=section):
                self.assertEqual((regressions, changes, note), ([], [], None))


class TestTheIgnoredCopyCannotInfluenceAnything(RatchetTestCase):
    def test_a_conflicting_ignored_baseline_changes_no_result(self):
        """The core of the cutover. The ignored file is given wildly different
        numbers; the verdict must come from the tracked file alone."""
        tracked = {"conservation": {"lines": 100, "unrouted": 5}}
        ignored = {"conservation": {"lines": 999999, "unrouted": 0}}
        tracked_path, ignored_path = self.fixture(tracked=tracked, ignored=ignored)
        module = self.module_at(tracked_path)

        self.assertEqual(module.load("conservation"), tracked["conservation"])
        self.assertEqual(module.compare("conservation", tracked["conservation"]),
                         ([], [], None))

        # Positive control, so "clean" cannot be a comparator that does nothing.
        # It must use metrics that move the WORSE way against the TRACKED pin: the
        # first version fed it the ignored file's numbers, which are better on both
        # metrics (more `lines`, less `unrouted`), so it asserted regressions on an
        # improvement and failed for a reason that had nothing to do with the path.
        regressions, _, _ = module.compare("conservation", {"lines": 1, "unrouted": 999})
        self.assertEqual([key for key, *_ in regressions], ["lines", "unrouted"])

    def test_creating_an_ignored_baseline_where_none_existed_changes_nothing(self):
        tracked = {"conservation": {"lines": 100}}
        tracked_path, ignored_path = self.fixture(tracked=tracked)
        module = self.module_at(tracked_path)
        before = module.compare("conservation", {"lines": 100})

        ignored_path.parent.mkdir(parents=True)
        ignored_path.write_text(json.dumps({"conservation": {"lines": 7}}) + "\n",
                                encoding="utf-8")
        self.assertEqual(module.compare("conservation", {"lines": 100}), before)
        self.assertEqual(module.load("conservation"), {"lines": 100})

    def test_a_change_to_the_tracked_file_IS_seen(self):
        """The other arm. A test that only proves the ignored copy is inert would
        also pass if the module read nothing at all."""
        tracked = {"conservation": {"lines": 100}}
        tracked_path, _ = self.fixture(tracked=tracked, ignored={"conservation": {"lines": 100}})
        module = self.module_at(tracked_path)
        self.assertEqual(module.load("conservation"), {"lines": 100})

        tracked_path.write_text(json.dumps({"conservation": {"lines": 42}}) + "\n",
                                encoding="utf-8")
        self.assertEqual(module.load("conservation"), {"lines": 42})
        regressions, _, _ = module.compare("conservation", {"lines": 100})
        self.assertEqual(regressions, [])


class TestSaveWritesTheTrackedFileOnly(RatchetTestCase):
    def test_save_updates_the_tracked_file_and_leaves_the_ignored_one_alone(self):
        tracked = {"conservation": {"lines": 100}, "locality": {"owned": 10}}
        ignored = {"conservation": {"lines": 1}}
        tracked_path, ignored_path = self.fixture(tracked=tracked, ignored=ignored)
        before_ignored = ignored_path.read_bytes()
        module = self.module_at(tracked_path)

        module.save("conservation", {"lines": 111})

        self.assertEqual(json.loads(tracked_path.read_text())["conservation"],
                         {"lines": 111})
        self.assertEqual(ignored_path.read_bytes(), before_ignored)

    def test_save_leaves_every_other_section_untouched(self):
        tracked = {"conservation": {"lines": 100}, "locality": {"owned": 10}}
        tracked_path, _ = self.fixture(tracked=tracked)
        module = self.module_at(tracked_path)

        module.save("conservation", {"lines": 111})
        self.assertEqual(json.loads(tracked_path.read_text())["locality"], {"owned": 10})

    def test_update_through_compare_writes_the_tracked_file(self):
        """`--update-baseline` reaches storage through `compare(update=True)`."""
        tracked = {"conservation": {"lines": 100}}
        tracked_path, ignored_path = self.fixture(tracked=tracked,
                                                  ignored={"conservation": {"lines": 1}})
        before_ignored = ignored_path.read_bytes()
        module = self.module_at(tracked_path)

        regressions, changes, note = module.compare("conservation", {"lines": 55},
                                                    update=True)
        self.assertEqual((regressions, changes), ([], []))
        self.assertIn("PINNED", note)
        self.assertEqual(json.loads(tracked_path.read_text())["conservation"],
                         {"lines": 55})
        self.assertEqual(ignored_path.read_bytes(), before_ignored)

    def test_an_accepted_change_becomes_reviewable(self):
        """The reason the move matters: after a save, the tracked file's bytes have
        changed, so the acceptance shows up in a diff instead of nowhere."""
        tracked_path, _ = self.fixture(tracked={"conservation": {"lines": 100}})
        before = sha256_of(tracked_path)
        self.module_at(tracked_path).save("conservation", {"lines": 101})
        self.assertNotEqual(sha256_of(tracked_path), before)


class TestAMissingBaselineFailsClosed(RatchetTestCase):
    def missing(self):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        return self.module_at(root / "config" / "baselines" / "foundry-audit-baseline.json")

    # NOTE: every assertion below raises against `module.BaselineUnavailable`, not
    # `self.fab.BaselineUnavailable`. `load_module()` returns a FRESH module object
    # each call, so the two carry different class objects for the same name and an
    # `assertRaises` aimed at the wrong one reports the halt as an unhandled error.
    # The first version of this file did exactly that and read as six broken tests.

    def test_load_halts_rather_than_returning_none(self):
        module = self.missing()
        with self.assertRaises(module.BaselineUnavailable):
            module.load("conservation")

    def test_compare_halts_rather_than_reporting_no_regressions(self):
        """The fail-open this cutover closes: a deleted baseline used to read
        exactly like a first run, and a first run is green."""
        module = self.missing()
        with self.assertRaises(module.BaselineUnavailable):
            module.compare("conservation", {"lines": 100})

    def test_report_halts_rather_than_returning_zero(self):
        module = self.missing()
        with self.assertRaises(module.BaselineUnavailable):
            module.report("conservation", {"lines": 100})

    def test_save_refuses_to_create_a_baseline_from_nothing(self):
        """Creating one would drop every other section's pins while looking like an
        update — a single command that silently un-ratchets the whole suite."""
        module = self.missing()
        with self.assertRaises(module.BaselineUnavailable):
            module.save("conservation", {"lines": 1})
        self.assertFalse(module.BASELINE.exists())

    def test_damaged_json_is_not_treated_as_an_empty_baseline(self):
        tracked_path, _ = self.fixture(tracked={"conservation": {"lines": 1}})
        tracked_path.write_text("{ this is not json", encoding="utf-8")
        module = self.module_at(tracked_path)
        with self.assertRaises(module.BaselineUnavailable):
            module.compare("conservation", {"lines": 1})

    def test_a_json_document_that_is_not_an_object_is_refused(self):
        tracked_path, _ = self.fixture(tracked={"conservation": {"lines": 1}})
        tracked_path.write_text("[1, 2, 3]", encoding="utf-8")
        module = self.module_at(tracked_path)
        with self.assertRaises(module.BaselineUnavailable):
            module.load("conservation")

    def test_the_halt_is_the_module_s_own_declared_failure(self):
        """It must be a named, catchable halt rather than whatever the filesystem
        happened to raise, so a caller can tell 'baseline unreadable' from a bug."""
        module = self.missing()
        self.assertTrue(issubclass(module.BaselineUnavailable, RuntimeError))


class TestAnAbsentSectionIsStillAFirstRun(RatchetTestCase):
    """Deliberately unchanged. A section nobody has pinned really is a first run,
    and only the missing FILE was ever the fail-open."""

    def test_an_unpinned_section_returns_none(self):
        tracked_path, _ = self.fixture(tracked={"conservation": {"lines": 1}})
        self.assertIsNone(self.module_at(tracked_path).load("brand_new_audit"))

    def test_an_unpinned_section_reports_the_pin_it_note_and_no_regressions(self):
        tracked_path, _ = self.fixture(tracked={"conservation": {"lines": 1}})
        regressions, changes, note = self.module_at(tracked_path).compare(
            "brand_new_audit", {"lines": 1})
        self.assertEqual((regressions, changes), ([], []))
        self.assertIn("no baseline pinned", note)
        self.assertIn("--update-baseline", note)


# ---------------------------------------------------------------------------
# Nothing else moved
# ---------------------------------------------------------------------------


class TestTheRatchetSemanticsAreUnchanged(RatchetTestCase):
    """Every expectation below was verified equal to the pre-cutover module over
    300 cases built from all 8 pinned sections and all 137 pinned metrics, each
    bumped in both directions, plus a removed metric, an added metric, an absent
    section and an empty metric set. This is the pinned restatement of that run.
    """

    def compare(self, pinned: dict, now: dict):
        tracked_path, _ = self.fixture(tracked={"s": pinned})
        return self.module_at(tracked_path).compare("s", now)

    def test_a_rise_in_a_worse_if_up_metric_is_a_regression(self):
        regressions, changes, _ = self.compare({"unrouted_lines": 10},
                                               {"unrouted_lines": 11})
        self.assertEqual(changes, [])
        self.assertEqual(regressions, [("unrouted_lines", 10, 11,
                                        "+1 in the WORSE direction")])

    def test_a_fall_in_a_worse_if_up_metric_is_a_reported_change(self):
        regressions, changes, _ = self.compare({"uncontexted": 10}, {"uncontexted": 9})
        self.assertEqual(regressions, [])
        self.assertEqual(changes, [("uncontexted", 10, 9, "-1")])

    def test_a_fall_in_a_worse_if_down_metric_is_a_regression(self):
        regressions, changes, _ = self.compare({"lines": 10}, {"lines": 9})
        self.assertEqual(changes, [])
        self.assertEqual(regressions, [("lines", 10, 9, "-1 in the WORSE direction")])

    def test_a_rise_in_a_worse_if_down_metric_is_a_reported_change(self):
        regressions, changes, _ = self.compare({"memberships": 10}, {"memberships": 11})
        self.assertEqual(regressions, [])
        self.assertEqual(changes, [("memberships", 10, 11, "+1")])

    def test_a_neutral_metric_moves_in_either_direction_without_being_fatal(self):
        for delta in (+1, -1):
            with self.subTest(delta=delta):
                regressions, changes, _ = self.compare({"ambiguous": 10},
                                                       {"ambiguous": 10 + delta})
                self.assertEqual(regressions, [])
                self.assertEqual(len(changes), 1)

    def test_direction_resolves_on_the_whole_dotted_key_not_the_leaf(self):
        """The historical defect: judging `class_unrouted.comma` on `comma` made
        every nested metric neutral, and a 621-line regression exited 0."""
        regressions, _, _ = self.compare({"class_unrouted": {"comma": 10}},
                                         {"class_unrouted": {"comma": 11}})
        self.assertEqual(regressions, [("class_unrouted.comma", 10, 11,
                                        "+1 in the WORSE direction")])

    def test_a_disappeared_metric_is_a_regression(self):
        regressions, changes, _ = self.compare({"lines": 10, "ambiguous": 1},
                                               {"ambiguous": 1})
        self.assertEqual(changes, [])
        self.assertEqual(regressions, [("lines", 10, "—", "metric DISAPPEARED")])

    def test_a_new_metric_is_a_reported_change(self):
        regressions, changes, _ = self.compare({"lines": 10},
                                               {"lines": 10, "ambiguous": 3})
        self.assertEqual(regressions, [])
        self.assertEqual(changes, [("ambiguous", "—", 3, "new metric")])

    def test_the_direction_marker_sets_are_untouched(self):
        self.assertIn("unrouted", self.fab.WORSE_IF_UP)
        self.assertIn("addressable_missing", self.fab.WORSE_IF_UP)
        self.assertIn("reaching", self.fab.WORSE_IF_DOWN)
        self.assertIn("memberships", self.fab.WORSE_IF_DOWN)
        self.assertNotIn("ambiguous", self.fab.WORSE_IF_UP + self.fab.WORSE_IF_DOWN)
        self.assertEqual(len(self.fab.WORSE_IF_UP), 14)
        self.assertEqual(len(self.fab.WORSE_IF_DOWN), 15)


class TestThePublicCallShapesAreCompatible(RatchetTestCase):
    """~7 legacy modules import this one. A signature change would be a breakage
    this slice is not allowed to cause."""

    EXPECTED = {
        "load": "(section: str) -> dict",
        "save": "(section: str, metrics: dict) -> None",
        "compare": "(section: str, metrics: dict, update: bool = False)",
        "report": "(section: str, metrics: dict, update: bool = False) -> int",
    }

    def test_every_public_signature_is_unchanged(self):
        for name, expected in self.EXPECTED.items():
            with self.subTest(name=name):
                self.assertEqual(str(inspect.signature(getattr(self.fab, name))),
                                 expected)

    def test_the_baseline_attribute_consumers_reach_for_still_exists(self):
        """`foundry_reachability.py --selftest` reaches for `BASELINE` directly,
        so keeping the NAME is what spares every consumer a change.

        It no longer WRITES through it: P0.3F rebinds this attribute at a
        temporary control input for the duration of the negative control, so the
        tracked baseline stops being the write target. The attribute is load-
        bearing either way, which is why this assertion is unchanged."""
        self.assertIsInstance(self.fab.BASELINE, Path)

    def test_report_still_returns_the_regression_count(self):
        tracked_path, _ = self.fixture(tracked={"s": {"lines": 10, "unrouted": 1}})
        module = self.module_at(tracked_path)
        with contextlib.redirect_stdout(io.StringIO()):
            clean = module.report("s", {"lines": 10, "unrouted": 1})
            regressed = module.report("s", {"lines": 9, "unrouted": 2})
        self.assertEqual(clean, 0)
        self.assertEqual(regressed, 2)

    def test_report_still_prints_the_section_and_both_verdict_markers(self):
        tracked_path, _ = self.fixture(tracked={"s": {"lines": 10, "unrouted": 1}})
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self.module_at(tracked_path).report("s", {"lines": 11, "unrouted": 2})
        printed = buffer.getvalue()
        self.assertIn("BASELINE — s", printed)
        self.assertIn("◐", printed)
        self.assertIn("✗", printed)
        self.assertIn("--update-baseline", printed)


class TestDeterminism(RatchetTestCase):
    def test_two_reads_of_the_live_baseline_agree(self):
        self.assertEqual(load_module().load("conservation"),
                         load_module().load("conservation"))

    def test_saving_the_same_metrics_twice_is_byte_identical(self):
        tracked_path, _ = self.fixture(tracked={"s": {"lines": 1}})
        module = self.module_at(tracked_path)
        module.save("s", {"lines": 2})
        first = tracked_path.read_bytes()
        module.save("s", {"lines": 2})
        self.assertEqual(tracked_path.read_bytes(), first)


if __name__ == "__main__":
    unittest.main()
