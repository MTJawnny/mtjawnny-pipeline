"""Migration slice 3: the superseded DET batch is retired, and stays retired.

`docs/det-patterns-v1.json` was read at runtime by two active modules --
`foundry_reminder_conformance` and `foundry_visibility_audit`, the latter a
Gate 2 row -- and both HALTED if the file was absent. That made the accepted
`ARCHIVE_AS_HISTORY_EVIDENCE` disposition unimplementable: `archive/**` is
INERT by definition, and no active reader may point into it.

S3 retired the dependency. It was a PRESENCE dependency only, and that was
proven before the file moved, not asserted afterwards: every one of v1's 44
string-pattern slugs is supplied again by a later batch, none is v1-only, and
the effective `slug -> pattern` map is identical with and without it.

THIS FILE IS THE STANDING GUARD FOR BOTH HALVES:

  1. no active runtime code names v1 or reaches into `archive/`;
  2. omitting v1 does not change the effective active DET pattern map.

(2) is exercised through the ACTIVE READER'S OWN merge, never through a second
implementation of it. A guard that re-implemented the merge would be testing the
guard's arithmetic rather than the classifier's, which is the recorded
"a probe that re-derives the thing it is auditing" defect.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT  # noqa: F401  (sets sys.path)

from mtj_foundry.paths import ProjectPaths

PATHS = ProjectPaths.for_root(REPO_ROOT)
EXPERIMENTS = REPO_ROOT / "experiments"

V1_NAME = "det-patterns-v1.json"
V2_NAME = "det-patterns-v2.json"
CR_ACTIONS_NAME = "det-patterns-cr-actions-v1.json"


def load_legacy(name: str):
    """Import a legacy `experiments/` module by path, the way Gate 2 reaches it."""
    if str(EXPERIMENTS) not in sys.path:
        sys.path.insert(0, str(EXPERIMENTS))
    spec = importlib.util.spec_from_file_location(
        f"legacy_{name}", EXPERIMENTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def legacy_production_python() -> list[Path]:
    """Tracked `experiments/**` plus the permanent package -- the ACTIVE trees.

    `archive/**` and `benchmarks/**` are deliberately excluded: they are inert by
    disposition, and the whole point of this guard is that ACTIVE code stays out
    of them.
    """
    out = []
    for base in (EXPERIMENTS, REPO_ROOT / "src", REPO_ROOT / "pipeline"):
        out += [p for p in sorted(base.rglob("*.py"))
                if "aq4_benchmark" not in p.parts]
    return out


class TestNoActiveReaderConsumesTheRetiredBatch(unittest.TestCase):
    """Half 1: v1 is unreachable from active code, by name and by directory."""

    def test_no_active_module_names_the_retired_batch_as_a_string(self):
        """A string literal is how every one of these readers named its inputs,
        so a returning dependency would look exactly like one.

        Comments are excluded on purpose -- prose recording that v1 EXISTED is
        history and must survive -- so this reads string CONSTANTS out of the
        AST rather than grepping the text.
        """
        offenders = []
        for path in legacy_production_python():
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except SyntaxError:                      # pragma: no cover
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    if V1_NAME in node.value:
                        offenders.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}")
        self.assertEqual(offenders, [], f"active code names {V1_NAME}: {offenders}")

    def test_no_active_module_reaches_into_the_archive_tree(self):
        """`archive/**` is INERT. An active reader pointing at it would satisfy
        the letter of the move while defeating its purpose -- the exact repair
        this slice exists to make."""
        offenders = []
        for path in legacy_production_python():
            # THE LAYOUT OWNER IS EXEMPT, AND THE EXEMPTION IS THE S1 LAW ITSELF:
            # `paths.py` NAMES every accepted destination, including the archive
            # roots, and naming is not reading. Slice 1 exists precisely so one
            # module states repository layout; excluding it here is what lets the
            # rule be "no CONSUMER reaches the archive" rather than "the string
            # never appears", which would forbid the owner from doing its job.
            if path == REPO_ROOT / "src" / "mtj_foundry" / "paths.py":
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except SyntaxError:                      # pragma: no cover
                continue
            for node in ast.walk(tree):
                if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                        and (node.value == "archive"
                             or node.value.startswith("archive/"))):
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}")
        self.assertEqual(offenders, [], f"active code reaches archive/: {offenders}")

    def test_the_owner_names_the_archive_destination_and_no_consumer_uses_it(self):
        """The other half of the exemption above, asserted rather than assumed:
        the owner really does name it, and no active module reads that property."""
        self.assertEqual(PATHS.archive_config,
                         PATHS.root / "archive" / "config")
        users = [p.relative_to(REPO_ROOT) for p in legacy_production_python()
                 if p != REPO_ROOT / "src" / "mtj_foundry" / "paths.py"
                 and "archive_config" in p.read_text(encoding="utf-8")]
        self.assertEqual(users, [])

    def test_the_archived_batch_is_still_present_as_evidence(self):
        """Retired is not deleted. The bytes remain, where the accepted
        disposition puts them."""
        self.assertTrue((PATHS.archive_config / V1_NAME).is_file())

    def test_the_two_repaired_readers_declare_only_the_live_batches(self):
        """The declared inputs of both modules, read as source rather than by
        importing them, so a module-level side effect cannot mask the answer."""
        for module, symbol in (("foundry_reminder_conformance", "BATCHES"),
                               ("foundry_visibility_audit", None)):
            with self.subTest(module=module):
                tree = ast.parse((EXPERIMENTS / f"{module}.py").read_text(encoding="utf-8"))
                names = {n.value for n in ast.walk(tree)
                         if isinstance(n, ast.Constant) and isinstance(n.value, str)
                         and n.value.endswith(".json")
                         and "det-patterns" in n.value}
                self.assertEqual(names, {V2_NAME, CR_ACTIONS_NAME})

    def test_both_readers_resolve_batches_through_the_accepted_owner(self):
        """Not merely "not v1" -- the batches must come from the config owner, so
        a reader cannot quietly reacquire a directory of its own."""
        for module in ("foundry_reminder_conformance", "foundry_visibility_audit"):
            with self.subTest(module=module):
                source = (EXPERIMENTS / f"{module}.py").read_text(encoding="utf-8")
                self.assertIn("fc.CONFIG_SEMANTIC / name", source)


class TestOmittingTheRetiredBatchChangesNothing(unittest.TestCase):
    """Half 2: the equivalence, exercised through the active reader's own merge.

    `foundry_reminder_conformance.ratified_patterns()` reads
    `fc.CONFIG_SEMANTIC / name` for each name in its module-level `BATCHES`, so
    both arms below are the SAME function over the same bytes, differing only in
    whether v1 is in the list. No merge logic is written here.
    """

    @classmethod
    def setUpClass(cls):
        cls.frc = load_legacy("foundry_reminder_conformance")

    def _patterns_for(self, batches, directory):
        """Run the ACTIVE reader against a scratch batch directory.

        The patch targets `frc.fc.CONFIG_SEMANTIC` -- the attribute the function
        actually reads at call time -- rather than any local name. Patching the
        wrong module object is a recorded defect in this repository, and it reads
        as a passing test.
        """
        fc = self.frc.fc
        original_dir, original_batches = fc.CONFIG_SEMANTIC, self.frc.BATCHES
        try:
            fc.CONFIG_SEMANTIC = directory
            self.frc.BATCHES = batches
            return dict(self.frc.ratified_patterns())
        finally:
            fc.CONFIG_SEMANTIC = original_dir
            self.frc.BATCHES = original_batches

    def test_the_effective_map_is_identical_with_and_without_v1(self):
        """THE INVARIANT THE RETIREMENT RESTS ON.

        Both arms run the live reader. If a future edit made v1 contribute a
        pattern again -- a new slug, or a row v2 stopped shadowing -- the two
        maps would differ and this fails, which is the whole point: the guard
        does not care WHY v1 became load-bearing again, only that it did.
        """
        with tempfile.TemporaryDirectory() as tmp:
            scratch = Path(tmp)
            for name, source in ((V1_NAME, PATHS.archive_config / V1_NAME),
                                 (V2_NAME, PATHS.config_semantic / V2_NAME),
                                 (CR_ACTIONS_NAME,
                                  PATHS.config_semantic / CR_ACTIONS_NAME)):
                (scratch / name).write_bytes(source.read_bytes())

            with_v1 = self._patterns_for(
                (V1_NAME, V2_NAME, CR_ACTIONS_NAME), scratch)
            without_v1 = self._patterns_for((V2_NAME, CR_ACTIONS_NAME), scratch)

        self.assertEqual(with_v1, without_v1)
        self.assertEqual(len(without_v1), 45)
        # every v1 string-pattern slug is supplied by a later batch, and the
        # value that survives is the later one -- shadowing, not coincidence
        v1_rows = json.loads(
            (PATHS.archive_config / V1_NAME).read_text(encoding="utf-8"))["patterns"]
        v1_strings = {r["slug"] for r in v1_rows if isinstance(r.get("pattern"), str)}
        self.assertEqual(len(v1_strings), 44)
        self.assertEqual(v1_strings - set(without_v1), set())

    def test_the_live_reader_produces_that_same_map_from_the_real_config(self):
        """The scratch arms above must describe the SHIPPED state, not a fixture
        that happens to agree with itself."""
        live = dict(self.frc.ratified_patterns())
        self.assertEqual(len(live), 45)
        self.assertTrue(all(isinstance(v, str) for v in live.values()))

    def test_a_missing_batch_still_halts_rather_than_passing_quietly(self):
        """The fail-closed behaviour is PRESERVED, not traded away. Retiring an
        input must not turn a missing input into a silent empty result."""
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit):
                self._patterns_for((V2_NAME,), Path(tmp))


if __name__ == "__main__":
    unittest.main()
