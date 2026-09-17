"""S15.D5 -- the seven retired codebook-CONTENT transforms, and their owner.

WHY THIS FILE EXISTS
--------------------
S15.D5 moved seven one-shot codebook-content transformation artifacts out of
`experiments/` into `archive/research/codebook-transforms/` byte-for-byte. The
move is plumbing; four separate truths are not, and each is guarded here:

1.  CONSERVATION -- the seven archived blobs are the exact objects the base
    commit held at the old live paths: same object id, same digest, same byte
    count, same mode. No source edit is permitted by the task and none happened.
2.  OWNERSHIP -- the owner is CLOSED at exactly seven Python files, with one
    `ProjectPaths` property pointing at it, and the neighbouring `/1 -> /2`
    schema-migration owner is not widened to absorb them.
3.  PROVENANCE -- the S10 caller sidecar records the transfer truthfully, each
    row's `foundry_common` symbol set matching BOTH the archived source and the
    pre-move live source. A move that silently rewrote a file is caught.
4.  DISCOVERY -- the prior-art reader registers this owner exactly once, under
    its own label, so the strict refusal that the seven contributed while live
    never lapsed. That lapse, in D4, is the whole reason this line of guards
    exists.

THE R2 STOP, AND WHY THIS FILE IS PART OF THE ANSWER
----------------------------------------------------
The first execution attempt (S15.D5.R2) stopped rather than finishing: adding
the one ratified `ProjectPaths` owner necessarily breaks a THIRD exhaustive
public-property pin, `test_no_other_public_property_was_added`, which lives in
`test_layout_delegation.py` and was outside that task's allowlist. R3 was given
exactly one further authorization -- advance that pin, do not relax it -- and
the guard below re-asserts, from this file, that the advanced pin still names
this owner. A pin that is re-aimed is a guard; a pin that is deleted or made
dynamic is not, and the difference is checked rather than asserted in prose.

MEASUREMENT HONESTY
-------------------
Expected identities are derived at run time from GIT OBJECTS at the recorded
base commit -- never copied out of the working tree the move was made in. A
worktree that agrees with itself proves nothing. The archived files are read as
TEXT; nothing here imports, executes or compiles one, which is the same rule the
reader itself is held to.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT
from tests.refoundation.test_s10_card_text_owners import (
    RETIRED, caller_census, provider_names)

EXPERIMENTS = REPO_ROOT / "experiments"
PROVIDER_PATH = EXPERIMENTS / "foundry_common.py"
PRIOR_ART_PATH = EXPERIMENTS / "foundry_prior_art.py"
LAYOUT_TEST_PATH = REPO_ROOT / "tests" / "refoundation" / "test_layout_delegation.py"
SIDECAR_REL = "tests/refoundation/s10_foundry_common_callers.json"

TRANSFORMS_REL = "archive/research/codebook-transforms"
MUTATIONS_REL = "archive/research/mutations"
TRANSFORMS_PROPERTY = "archive_research_codebook_transforms"
TRANSFORMS_LABEL = "archived codebook-transforms set"

# CONTROL-PLANE LAW, not measurement. The D5 direction, task and selecting
# checkpoint all name this commit; it is written here so a drifted repository
# FAILS rather than quietly re-deriving a new expectation.
D5_BASE = "f429776fb5fa461b9d44425bf40e858d4527a17b"

# The authorized subject set, exactly seven, as the Captain direction names it.
# Cross-checked against the archive tree below rather than derived from it: a
# list read out of the tree it is meant to police cannot police it.
SEVEN = (
    "foundry_any_damage_split.py",
    "foundry_axis_merge_pointer_correction.py",
    "foundry_batch7_pay_life_scrub.py",
    "foundry_cdr09_derive.py",
    "foundry_cdr09_walk.py",
    "foundry_gate0_scrub.py",
    "foundry_locality_backfill.py",
)

# The CDR-09 evidence pair, which the direction requires to move atomically.
CDR09_PAIR = ("foundry_cdr09_derive.py", "foundry_cdr09_walk.py")

# Six of the seven are C8.5V nominees. `batch7_pay_life_scrub` is NOT one, and
# that asymmetry is asserted rather than assumed -- a retarget map that quietly
# gained a seventh member would be changing the pinned nomination set.
C8_5V_SIX = tuple(n for n in SEVEN if n != "foundry_batch7_pay_life_scrub.py")

# The accepted S10 population transition recorded by the D5 amendment.
LIVE_BEFORE, LIVE_AFTER = 70, 63
ARCHIVE_BEFORE, ARCHIVE_AFTER = 19, 26


# ===========================================================================
# git, as an evidence source
# ===========================================================================

def git(*argv: str, binary: bool = False):
    r = subprocess.run(["git", "-C", str(REPO_ROOT), *argv], capture_output=True)
    if r.returncode != 0:
        raise AssertionError(
            f"git {' '.join(argv)} failed: {r.stderr.decode().strip()}")
    return r.stdout if binary else r.stdout.decode()


def have_object(ref: str) -> bool:
    return subprocess.run(["git", "-C", str(REPO_ROOT), "cat-file", "-e", ref],
                          capture_output=True).returncode == 0


def blob_identity(commit: str, path: str) -> dict:
    """`{blob, sha256, size, mode}` for one path at one commit, from the object
    database. Independent of whatever the working tree currently holds."""
    entry = git("ls-tree", commit, "--", path).strip()
    if not entry:
        raise AssertionError(f"{path} absent at {commit}")
    meta, _tab, _name = entry.partition("\t")
    mode, _kind, blob = meta.split()
    content = git("cat-file", "blob", blob, binary=True)
    return {"blob": blob, "sha256": hashlib.sha256(content).hexdigest(),
            "size": len(content), "mode": mode}


def index_identity(path: str) -> dict:
    """`{blob, sha256, size, mode}` for one path as the INDEX holds it.

    Deliberately not `HEAD`: this module must give the same answer before the
    move is committed and after, and the index is the state that becomes HEAD.
    Reading HEAD instead would make the guard vacuously unrunnable in the very
    commit it exists to police."""
    entry = git("ls-files", "-s", "--", path).strip()
    if not entry:
        raise AssertionError(f"{path} is not tracked")
    meta, _tab, _name = entry.partition("\t")
    mode, blob, _stage = meta.split()
    content = git("cat-file", "blob", blob, binary=True)
    return {"blob": blob, "sha256": hashlib.sha256(content).hexdigest(),
            "size": len(content), "mode": mode}


requires_history = unittest.skipUnless(
    (REPO_ROOT / ".git").exists() and have_object(D5_BASE),
    "the D5 base commit is needed as the independent identity source")


def load_prior_art():
    """Import the READER by path, the way Gate 2 reaches a legacy module. The
    archived programs themselves are never imported anywhere in this file."""
    if str(EXPERIMENTS) not in sys.path:
        sys.path.insert(0, str(EXPERIMENTS))
    spec = importlib.util.spec_from_file_location(
        "legacy_foundry_prior_art_d5", PRIOR_ART_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def measured_archived_symbols() -> dict:
    """`{archived path: sorted foundry_common names}`, measured from the archived
    SOURCE TEXT by the same census the S10 test uses. Read, never executed."""
    provider = PROVIDER_PATH.read_text(encoding="utf-8")
    sources = {f"{TRANSFORMS_REL}/{n}":
               (REPO_ROOT / TRANSFORMS_REL / n).read_text(encoding="utf-8")
               for n in SEVEN}
    return caller_census(sources, provider, known_names=RETIRED)


# ===========================================================================
# 1. the seven archived files are byte-exact
# ===========================================================================

@requires_history
class TestTheSevenArchivedFilesAreByteIdentical(unittest.TestCase):
    """Conservation, proven against the BASE commit rather than against the
    worktree the move was made in."""

    def test_exactly_seven_tracked_python_files_are_in_the_owner(self):
        listed = sorted(p for p in git(
            "ls-files", "--full-name", "--", TRANSFORMS_REL).split()
            if p.endswith(".py"))
        self.assertEqual(listed, sorted(f"{TRANSFORMS_REL}/{n}" for n in SEVEN))

    def test_there_is_no_eighth_python_file(self):
        """A closed population. An eighth file is a different owner, silently."""
        on_disk = sorted(p.name for p in (REPO_ROOT / TRANSFORMS_REL).glob("*.py"))
        self.assertEqual(on_disk, sorted(SEVEN))

    def test_every_old_live_path_is_absent(self):
        for name in SEVEN:
            with self.subTest(name=name):
                self.assertFalse((EXPERIMENTS / name).exists(),
                                 f"experiments/{name} was resurrected")
        tracked = git("ls-files", "--full-name", "--", "experiments").split()
        for name in SEVEN:
            self.assertNotIn(f"experiments/{name}", tracked)

    def test_every_destination_is_tracked(self):
        tracked = set(git("ls-files", "--full-name", "--", TRANSFORMS_REL).split())
        for name in SEVEN:
            with self.subTest(name=name):
                self.assertIn(f"{TRANSFORMS_REL}/{name}", tracked)

    def test_each_destination_reproduces_its_base_source_object_exactly(self):
        """Blob id, SHA-256, byte count and mode, all four, against the object
        the base commit held at the OLD path."""
        for name in SEVEN:
            with self.subTest(name=name):
                source = blob_identity(D5_BASE, f"experiments/{name}")
                dest = index_identity(f"{TRANSFORMS_REL}/{name}")
                self.assertEqual(dest["blob"], source["blob"])
                self.assertEqual(dest["sha256"], source["sha256"])
                self.assertEqual(dest["size"], source["size"])
                self.assertEqual(dest["mode"], source["mode"])
                self.assertEqual(dest["mode"], "100644")

    def test_the_bytes_a_reader_actually_opens_match_the_base_source(self):
        """The object database agreeing with itself says nothing about the file
        on disk. Hash what a reader would open."""
        for name in SEVEN:
            with self.subTest(name=name):
                source = blob_identity(D5_BASE, f"experiments/{name}")
                on_disk = (REPO_ROOT / TRANSFORMS_REL / name).read_bytes()
                self.assertEqual(hashlib.sha256(on_disk).hexdigest(),
                                 source["sha256"])
                self.assertEqual(len(on_disk), source["size"])


@requires_history
class TestTheCDR09PairMovedAtomically(unittest.TestCase):
    """The walk imports the derivation and uses its sense table. Archiving one
    without the other retains the record of a rename without the derivation that
    decided it -- and, whenever an external bootstrap supplies `experiments/`,
    leaves the archived walk binding to a still-live sibling."""

    def test_both_halves_are_in_the_same_owner(self):
        for name in CDR09_PAIR:
            with self.subTest(name=name):
                self.assertTrue((REPO_ROOT / TRANSFORMS_REL / name).is_file())

    def test_neither_half_was_left_behind(self):
        for name in CDR09_PAIR:
            with self.subTest(name=name):
                self.assertFalse((EXPERIMENTS / name).exists())

    def test_the_walk_still_names_its_sibling_and_was_not_edited(self):
        """R100 means the import line is untouched. Read as text."""
        walk = (REPO_ROOT / TRANSFORMS_REL / "foundry_cdr09_walk.py").read_text(
            encoding="utf-8")
        self.assertIn("import foundry_cdr09_derive as derive", walk)
        source = blob_identity(D5_BASE, "experiments/foundry_cdr09_walk.py")
        self.assertEqual(
            hashlib.sha256(walk.encode()).hexdigest(), source["sha256"])

    def test_sibling_resolution_lands_inside_the_archive(self):
        """With the archive directory as the import root -- the root the walk's
        own `Path(__file__).resolve().parent` bootstrap produces -- the sibling
        resolves to the ARCHIVED derivation. Resolution only; nothing is run."""
        import importlib.machinery
        owner = str((REPO_ROOT / TRANSFORMS_REL).resolve())
        spec = importlib.machinery.PathFinder().find_spec(
            "foundry_cdr09_derive", [owner])
        self.assertIsNotNone(spec)
        self.assertEqual(Path(spec.origin).resolve(),
                         (REPO_ROOT / TRANSFORMS_REL
                          / "foundry_cdr09_derive.py").resolve())

    def test_no_live_experiments_path_can_satisfy_the_sibling_any_more(self):
        """The half-move failure mode, proven absent: there is no live
        `experiments/foundry_cdr09_derive.py` left for a supplied bootstrap to
        bind to."""
        import importlib.machinery
        spec = importlib.machinery.PathFinder().find_spec(
            "foundry_cdr09_derive", [str(EXPERIMENTS.resolve())])
        self.assertIsNone(spec)


# ===========================================================================
# 2. the owner, its pins, and the neighbours it must not absorb
# ===========================================================================

class TestTheOwnerIsNamedAndClosed(unittest.TestCase):

    def test_project_paths_points_at_exactly_this_directory(self):
        from mtj_foundry.paths import ProjectPaths
        layout = ProjectPaths.for_root(REPO_ROOT)
        self.assertEqual(layout.archive_research_codebook_transforms,
                         REPO_ROOT / TRANSFORMS_REL)

    def test_the_owner_derives_from_archive_research(self):
        from mtj_foundry.paths import ProjectPaths
        layout = ProjectPaths.for_root("/r")
        self.assertEqual(layout.archive_research_codebook_transforms,
                         layout.archive_research / "codebook-transforms")

    def test_the_owner_has_a_readme(self):
        readme = REPO_ROOT / TRANSFORMS_REL / "README.md"
        self.assertTrue(readme.is_file())
        body = readme.read_text(encoding="utf-8")
        for name in SEVEN:
            with self.subTest(name=name):
                self.assertIn(name, body)

    def test_the_readme_records_every_identity_it_claims(self):
        """A README that names files without pinning them is decoration. Each
        row's blob, digest and byte count must be the measured ones."""
        body = (REPO_ROOT / TRANSFORMS_REL / "README.md").read_text(
            encoding="utf-8")
        for name in SEVEN:
            with self.subTest(name=name):
                identity = index_identity(f"{TRANSFORMS_REL}/{name}")
                self.assertIn(identity["blob"], body)
                self.assertIn(identity["sha256"], body)
                self.assertIn(f"{identity['size']:,}", body)

    def test_the_readme_states_the_boundary_against_its_neighbours(self):
        body = (REPO_ROOT / TRANSFORMS_REL / "README.md").read_text(
            encoding="utf-8")
        self.assertIn(MUTATIONS_REL, body)
        self.assertIn("archive/research/triage", body)
        self.assertIn("archive/research/batch8", body)
        self.assertIn("CLOSED", body)

    def test_the_migration_pair_owner_kept_exactly_its_two_files(self):
        """`/1 -> /2` is a SCHEMA migration and stays its own closed owner. D5
        must not fold it in, and must not take anything out of it."""
        on_disk = sorted(p.name for p in
                         (REPO_ROOT / MUTATIONS_REL).glob("*.py"))
        self.assertEqual(on_disk, ["foundry_migrate_codebook_v2.py",
                                   "foundry_verify_migration.py"])
        for name in SEVEN:
            with self.subTest(name=name):
                self.assertFalse((REPO_ROOT / MUTATIONS_REL / name).exists())

    def test_no_transform_landed_in_a_neighbouring_owner(self):
        for neighbour in (MUTATIONS_REL, "archive/research/triage",
                          "archive/research/batch8"):
            for name in SEVEN:
                with self.subTest(neighbour=neighbour, name=name):
                    self.assertFalse((REPO_ROOT / neighbour / name).exists())


class TestEveryExhaustivePropertyPinNamesTheOwner(unittest.TestCase):
    """S15.D5.R2 stopped because a THIRD exhaustive `ProjectPaths` pin existed
    outside its allowlist. All three are checked here, from one place, so the
    next owner addition cannot discover a fourth the hard way."""

    def test_the_layout_delegation_pin_names_the_owner(self):
        body = LAYOUT_TEST_PATH.read_text(encoding="utf-8")
        block = body.split("def test_no_other_public_property_was_added")[1]
        block = block.split("\n    def ")[0]
        self.assertIn(f'"{TRANSFORMS_PROPERTY}"', block)

    def test_the_layout_delegation_pin_is_still_exhaustive_and_exact(self):
        """REAIM, NOT RELAX. The guard must still compare a literal list against
        every public property -- not a count, not a dynamically derived set, and
        not a subset check."""
        body = LAYOUT_TEST_PATH.read_text(encoding="utf-8")
        block = body.split("def test_no_other_public_property_was_added")[1]
        block = block.split("\n    def ")[0]
        self.assertIn("self.assertEqual(props, [", block)
        self.assertIn("isinstance(getattr(ProjectPaths, n), property)", block)
        for loosened in ("assertIn", "issubset", "assertGreater",
                         "len(props)", "assertLessEqual"):
            with self.subTest(loosened=loosened):
                self.assertNotIn(loosened, block)

    def test_the_test_paths_destination_pin_names_the_owner(self):
        from tests.refoundation.test_paths import S1_DESTINATIONS
        self.assertEqual(S1_DESTINATIONS[TRANSFORMS_PROPERTY], TRANSFORMS_REL)

    def test_the_three_pins_agree_with_the_live_property_set(self):
        """The pins are only worth anything if they describe the same universe."""
        from mtj_foundry.paths import ProjectPaths
        from tests.refoundation.test_paths import (
            PRE_S1_PROPERTIES, S1_DESTINATIONS)
        live = {n for n in dir(ProjectPaths)
                if not n.startswith("_")
                and isinstance(getattr(ProjectPaths, n), property)}
        self.assertIn(TRANSFORMS_PROPERTY, live)
        self.assertEqual(set(PRE_S1_PROPERTIES) | set(S1_DESTINATIONS), live)
        body = LAYOUT_TEST_PATH.read_text(encoding="utf-8")
        block = body.split("def test_no_other_public_property_was_added")[1]
        block = block.split("\n    def ")[0]
        for name in sorted(live):
            with self.subTest(name=name):
                self.assertIn(f'"{name}"', block)


# ===========================================================================
# 3. the S10 caller sidecar records the transfer truthfully
# ===========================================================================

@requires_history
class TestTheSidecarTransferIsTrue(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((REPO_ROOT / SIDECAR_REL).read_text(encoding="utf-8"))
        cls.amendment = cls.data["s15_d5_amendment"]
        cls.rows = cls.amendment["rows_moved_to_archive"]

    def test_the_amendment_base_is_the_exact_D5_commit(self):
        self.assertEqual(self.amendment["head_base"], D5_BASE)

    def test_the_recorded_population_transfer_is_the_measured_one(self):
        self.assertEqual(self.amendment["live_importers"],
                         {"before": LIVE_BEFORE, "after": LIVE_AFTER})
        self.assertEqual(self.amendment["archive_importers"],
                         {"before": ARCHIVE_BEFORE, "after": ARCHIVE_AFTER})

    def test_the_transfer_arithmetic_closes_over_seven_rows(self):
        """Totals alone are not acceptance, but totals that do not close are a
        refutation."""
        self.assertEqual(len(self.rows), len(SEVEN))
        self.assertEqual(LIVE_BEFORE - LIVE_AFTER, len(SEVEN))
        self.assertEqual(ARCHIVE_AFTER - ARCHIVE_BEFORE, len(SEVEN))

    def test_the_body_totals_agree_with_the_declared_after_values(self):
        self.assertEqual(len(self.data["live_importers"]), LIVE_AFTER)
        self.assertEqual(len(self.data["archive_importers"]), ARCHIVE_AFTER)

    def test_every_moved_row_is_owned_by_this_archive(self):
        self.assertEqual(sorted(self.rows),
                         sorted(f"experiments/{n}" for n in SEVEN))
        for old, row in self.rows.items():
            with self.subTest(old=old):
                self.assertEqual(row["archived_path"],
                                 f"{TRANSFORMS_REL}/{Path(old).name}")

    def test_no_destination_is_recorded_twice(self):
        destinations = [r["archived_path"] for r in self.rows.values()]
        self.assertEqual(len(destinations), len(set(destinations)))
        self.assertEqual(len(self.data["archive_importers"]),
                         len(set(self.data["archive_importers"])))

    def test_no_old_live_path_survives_in_the_live_population(self):
        for name in SEVEN:
            with self.subTest(name=name):
                self.assertNotIn(f"experiments/{name}",
                                 self.data["live_importers"])

    def test_every_destination_is_in_the_archive_population(self):
        for name in SEVEN:
            with self.subTest(name=name):
                self.assertIn(f"{TRANSFORMS_REL}/{name}",
                              self.data["archive_importers"])

    def test_every_recorded_symbol_set_matches_the_archived_source(self):
        """The accepted S10 test compares archive PATHS only, so these seven
        recorded name sets would otherwise be asserted against nothing. Each is
        compared to the set actually measured from the archived file."""
        measured = measured_archived_symbols()
        self.assertEqual(len(measured), len(SEVEN), sorted(measured))
        for old, row in self.rows.items():
            with self.subTest(old=old):
                self.assertEqual(sorted(row["foundry_common_names"]),
                                 sorted(measured[row["archived_path"]]))

    def test_every_recorded_symbol_set_matches_the_PRE_MOVE_live_source(self):
        """A move that silently rewrote a file would still agree with itself
        afterwards. Compare each row to the symbol set of the source as the BASE
        commit held it."""
        provider = git("cat-file", "blob",
                       f"{D5_BASE}:experiments/foundry_common.py")
        for old, row in self.rows.items():
            with self.subTest(old=old):
                before = caller_census(
                    {old: git("cat-file", "blob", f"{D5_BASE}:{old}")},
                    provider, known_names=RETIRED)
                self.assertEqual(sorted(row["foundry_common_names"]),
                                 sorted(before[old]))

    def test_the_provider_still_defines_every_recorded_name(self):
        defined = provider_names(PROVIDER_PATH.read_text(encoding="utf-8"))
        for old, row in self.rows.items():
            for name in row["foundry_common_names"]:
                with self.subTest(old=old, name=name):
                    self.assertIn(name, defined | set(RETIRED))


# ===========================================================================
# 4. the C8.5V source-inspection guard was retargeted, not weakened
# ===========================================================================

@requires_history
class TestTheC8_5VGuardWasRetargetedNotWeakened(unittest.TestCase):
    """The guarded proposition is "each of the fifteen nominees is still measured
    and still carries its accepted verdict". D5 changes six addresses and nothing
    else: same bytes, same population, same verdicts."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(REPO_ROOT))
        from tests.refoundation import test_codebook_store as store
        cls.store = store

    def test_the_nomination_set_is_still_fifteen(self):
        self.assertEqual(len(self.store.C8_5V_FIFTEEN), 15)
        self.assertEqual(len(set(self.store.C8_5V_FIFTEEN)), 15)

    def test_the_six_nominees_point_at_their_archived_paths(self):
        for name in C8_5V_SIX:
            stem = name[len("foundry_"):-len(".py")]
            with self.subTest(stem=stem):
                self.assertEqual(self.store._C8_5V_MOVED[stem],
                                 f"{TRANSFORMS_REL}/{name}")
                self.assertIn(f"{TRANSFORMS_REL}/{name}",
                              self.store.C8_5V_FIFTEEN)

    def test_batch7_pay_life_scrub_is_NOT_a_nominee(self):
        """It moved in the same task and is deliberately absent from the guard.
        A retarget map that gained it would be changing the pinned set."""
        self.assertNotIn("batch7_pay_life_scrub", self.store._C8_5V_MOVED)
        self.assertNotIn(f"{TRANSFORMS_REL}/foundry_batch7_pay_life_scrub.py",
                         self.store.C8_5V_FIFTEEN)

    def test_no_nominee_was_dropped_to_make_the_move_quiet(self):
        """Shrinking a pinned nomination set is how a path change goes silent.
        Every path the guard names must still resolve to a tracked file."""
        tracked = set(git("ls-files", "--full-name").split())
        for path in self.store.C8_5V_FIFTEEN:
            with self.subTest(path=path):
                self.assertIn(path, tracked)

    def test_the_expected_verdict_totals_are_unchanged(self):
        import collections
        totals = collections.Counter(self.store.C8_5V_EXPECTED.values())
        self.assertEqual(totals["SAFE_NO_TRANSITIVE_HANDLER"], 14)
        self.assertEqual(totals["SAFE_NO_FAILURE_CLASS_DELTA"], 1)
        for path in self.store.C8_5V_FIFTEEN:
            if path.startswith(TRANSFORMS_REL):
                with self.subTest(path=path):
                    self.assertEqual(self.store.C8_5V_EXPECTED[path],
                                     "SAFE_NO_TRANSITIVE_HANDLER")


# ===========================================================================
# 5. discovery: the archived transforms are still findable
# ===========================================================================

class TestPriorArtRegistersTheNewOwner(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pa = load_prior_art()

    def test_the_owner_is_registered_exactly_once(self):
        from mtj_foundry.paths import ProjectPaths
        layout = ProjectPaths.for_root(REPO_ROOT)
        owners = [owner for owner, _ in self.pa.HISTORICAL_FAMILIES]
        self.assertEqual(
            owners.count(layout.archive_research_codebook_transforms), 1)

    def test_the_owner_carries_its_own_label(self):
        from mtj_foundry.paths import ProjectPaths
        layout = ProjectPaths.for_root(REPO_ROOT)
        label = dict(self.pa.HISTORICAL_FAMILIES)[
            layout.archive_research_codebook_transforms]
        self.assertEqual(label, TRANSFORMS_LABEL)

    def test_the_family_set_is_exactly_four_and_all_labels_are_distinct(self):
        self.assertEqual(len(self.pa.HISTORICAL_FAMILIES), 4)
        labels = [label for _, label in self.pa.HISTORICAL_FAMILIES]
        self.assertEqual(len(set(labels)), 4)

    def test_no_prior_family_was_removed_to_make_room(self):
        from mtj_foundry.paths import ProjectPaths
        layout = ProjectPaths.for_root(REPO_ROOT)
        owners = [owner for owner, _ in self.pa.HISTORICAL_FAMILIES]
        for earlier in (layout.archive_research_triage,
                        layout.archive_research_batch8,
                        layout.archive_research_mutations):
            with self.subTest(owner=str(earlier)):
                self.assertIn(earlier, owners)

    def test_discovery_over_the_archive_is_not_recursive(self):
        source = PRIOR_ART_PATH.read_text(encoding="utf-8")
        body = source.split("HISTORICAL_FAMILIES = (")[1].split(")\n")[0]
        for enumerator in ("rglob", "glob", "iterdir", "walk", "scandir"):
            with self.subTest(enumerator=enumerator):
                self.assertNotIn(enumerator, body)
        self.assertNotIn("archive_research_consolidation", source)
        self.assertNotIn("archive_research_thesaurus_measurement", source)

    def test_the_population_is_the_seven_tracked_archived_files(self):
        from mtj_foundry.paths import ProjectPaths
        owner = ProjectPaths.for_root(
            REPO_ROOT).archive_research_codebook_transforms
        _top, paths = self.pa._tracked_archive_sources(owner)
        self.assertEqual(
            sorted(p for p in paths if p.endswith(".py")),
            sorted(f"{TRANSFORMS_REL}/{n}" for n in SEVEN))

    def test_each_real_candidate_query_finds_its_archived_definition(self):
        """Real definitions, each measured to live in exactly one archived file
        and nowhere in the live tree. `foundry_gate0_scrub.py` is deliberately
        absent: under the reader's contract it contributes no uniquely reaching
        definition or constant, and inventing one would be a fiction."""
        cases = (
            ("apply split", "foundry_any_damage_split.py", "def apply_split"),
            ("verb conforms", "foundry_cdr09_derive.py", "def verb_conforms"),
            ("rename table", "foundry_cdr09_walk.py", "def build_rename_table"),
            ("stale target", "foundry_axis_merge_pointer_correction.py",
             "EXPECTED_STALE_TARGET"),
            ("remove from pay life", "foundry_batch7_pay_life_scrub.py",
             "REMOVE_FROM_PAY_LIFE"),
            ("strip locality", "foundry_locality_backfill.py",
             "def strip_locality"),
        )
        from mtj_foundry.paths import ProjectPaths
        owner = ProjectPaths.for_root(
            REPO_ROOT).archive_research_codebook_transforms
        for topic, filename, needle in cases:
            with self.subTest(topic=topic):
                hits = self.pa._historical_code(
                    self.pa.flexible_pattern(topic), owner)
                self.assertEqual(len(hits), 1, hits)
                path, lineno, text = hits[0]
                self.assertEqual(path, f"{TRANSFORMS_REL}/{filename}")
                self.assertTrue(lineno.isdigit())
                self.assertIn(needle, text)

    def test_the_archived_transforms_are_read_as_text_never_executed(self):
        """`_historical_code` compiles regexes and reads bytes. Asserted on the
        reader's own source so a future edit that imports or execs is caught."""
        source = PRIOR_ART_PATH.read_text(encoding="utf-8")
        body = source.split("def _historical_code")[1].split("\ndef ")[0]
        for forbidden in ("import_module", "exec(", "eval(", "spec_from_file",
                          "subprocess", "compile(text"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, body)
        self.assertIn("read_text", body)

    def test_this_test_module_never_imports_an_archived_transform(self):
        """The source-inspection rule applied to this file itself."""
        tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
        stems = {n[: -len(".py")] for n in SEVEN}
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported |= {a.name.split(".")[-1] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[-1])
        self.assertEqual(imported & stems, set())


if __name__ == "__main__":
    unittest.main()
