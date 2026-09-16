"""S15.D4.R2 -- the D4 triage archive, and the ability to still find it.

WHY THIS FILE EXISTS
--------------------
S15.D4 moved thirteen batch triage scripts out of `experiments/` into
`archive/research/triage/` byte-for-byte, and was accepted. An independent audit
then measured, in isolated checkouts:

    foundry_prior_art.py resolve_removed_members --strict

    D6 base b55294bc...   7 code artifacts, exit 1
    D4 head 739dcf2b...   0 code artifacts, exit 0

The prior-art reader was not edited by D4 -- its blob is identical at both
commits -- but its code-evidence population is the single directory
`experiments/`, so the archive move carried seven real definition sites out of
scan range. A STRICT REFUSAL BECAME A SILENT SUCCESS. That is the one conversion
this repository's governing principle never permits: relocating history is
plumbing, the refusal is truth.

Two independent things are therefore guarded here, and they are deliberately not
collapsed:

1.  DISCOVERY -- archived history is still reachable by a topic query, and still
    participates in the strict decision.
2.  CONSERVATION -- the thirteen archived files, and the S10 caller sidecar that
    records their move, are byte-exact and internally true.

WHAT THE EXISTING S10 TEST DOES NOT COVER
-----------------------------------------
`test_s10_card_text_owners` compares the live caller set as `{path: symbols}`
but the archive set as PATHS ONLY (`EXPECTED_ARCHIVE` is a list). The D4
amendment's thirteen `foundry_common_names` sets are therefore compared to
nothing at all: an amendment recording a WRONG archived symbol set passes that
test today. The amendment checks below are aimed exactly at that hole, and at
the stale-count, stale-base, wrong-owner and duplicate/omitted-mapping holes
beside it.

MEASUREMENT HONESTY
-------------------
Expected identities are derived at run time from GIT OBJECTS at the two recorded
commits -- the D6 source paths and the D4 destination paths -- never copied out
of the working tree the repair was built in. A worktree that agrees with itself
proves nothing. A fixture is an evidence pin, not new law, and nothing here
regenerates one to bless a drift.

COST DISCLOSURE
---------------
`test_the_real_regression_command_refuses_again` runs the actual command. The
live half of that command greps the `experiments/` DIRECTORY, which on a
developer checkout also contains the multi-gigabyte ignored `experiments/out/`
tree, so the run costs ~80s there and ~1s in a clean checkout. That cost is a
PRE-EXISTING property of the live search and is reported, not silently worked
around; the historical half added by this repair is tracked-file based and
enumerates thirteen files.
"""
from __future__ import annotations

import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT
from tests.refoundation.test_s10_card_text_owners import (
    RETIRED, caller_census, provider_names, tracked_python_sources)

EXPERIMENTS = REPO_ROOT / "experiments"
PROVIDER_PATH = EXPERIMENTS / "foundry_common.py"
PRIOR_ART_PATH = EXPERIMENTS / "foundry_prior_art.py"
SIDECAR_REL = "tests/refoundation/s10_foundry_common_callers.json"
ARCHIVE_TRIAGE_REL = "archive/research/triage"

# CONTROL-PLANE LAW, not measurement. The D4 direction, task, result and
# acceptance checkpoint all name these two commits; they are written here so a
# drifted repository FAILS rather than quietly re-deriving a new expectation.
D6_HEAD = "b55294bc4b87ae0e761d223f6321872cc46f39f2"
D4_HEAD = "739dcf2b2590c8ff95bf047d11cfc908487173f2"
# S15.D5.R1's base: the accepted D4.R2 implementation, whose reader covered the
# triage family ONLY. It is the reversion control for the repair below.
ACCEPTED_HEAD = "3b73b044ea0f1b7b810b39c91bf205a551525231"

# The authorized subject set, exactly thirteen, as the Captain direction names
# it. Cross-checked against the archive tree below rather than derived from it:
# a list read out of the tree it is meant to police cannot police it.
THIRTEEN = (
    "foundry_adapt_batch1_decisions.py",
    "foundry_adapt_batch2_decisions.py",
    "foundry_adapt_batch3_decisions.py",
    "foundry_adapt_batch4_decisions.py",
    "foundry_adapt_batch5_decisions.py",
    "foundry_adapt_batch6_decisions.py",
    "foundry_adapt_batch7_decisions.py",
    "foundry_assemble_batch2.py",
    "foundry_assemble_batch3.py",
    "foundry_assemble_batch4.py",
    "foundry_assemble_batch5.py",
    "foundry_assemble_batch6.py",
    "foundry_assemble_batch7.py",
)

# The accepted S10 population transition recorded by the D4 amendment.
LIVE_BEFORE, LIVE_AFTER = 83, 70
ARCHIVE_BEFORE, ARCHIVE_AFTER = 6, 19

REGRESSION_TOPIC = "resolve_removed_members"
REGRESSION_HITS = 7


# ===========================================================================
# git, as an evidence source
# ===========================================================================

def git(*argv: str, cwd: Path = REPO_ROOT, binary: bool = False):
    r = subprocess.run(["git", "-C", str(cwd), *argv], capture_output=True)
    if r.returncode != 0:
        raise AssertionError(
            f"git {' '.join(argv)} failed in {cwd}: {r.stderr.decode().strip()}")
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


requires_history = unittest.skipUnless(
    (REPO_ROOT / ".git").exists() and have_object(D6_HEAD) and have_object(D4_HEAD),
    "the D4/D6 commits are needed as the independent identity source")


# ===========================================================================
# 1. the thirteen archived files are byte-exact
# ===========================================================================

@requires_history
class TestTheThirteenArchivedFilesAreByteIdentical(unittest.TestCase):
    """Conservation, proven against the SOURCE commit rather than against the
    repaired worktree. Each archived destination must reproduce the exact blob
    the D6 tree held at the old live path -- same object id, same digest, same
    byte count, same mode."""

    def test_exactly_thirteen_tracked_files_are_in_the_archive(self):
        listed = sorted(p for p in git(
            "ls-files", "--full-name", "--", ARCHIVE_TRIAGE_REL).split() if p)
        self.assertEqual(listed,
                         sorted(f"{ARCHIVE_TRIAGE_REL}/{n}" for n in THIRTEEN))

    def test_each_destination_reproduces_its_D6_source_object_exactly(self):
        for name in THIRTEEN:
            with self.subTest(name=name):
                source = blob_identity(D6_HEAD, f"experiments/{name}")
                dest = blob_identity(D4_HEAD, f"{ARCHIVE_TRIAGE_REL}/{name}")
                self.assertEqual(dest["blob"], source["blob"])
                self.assertEqual(dest["sha256"], source["sha256"])
                self.assertEqual(dest["size"], source["size"])
                self.assertEqual(dest["mode"], "100644")
                self.assertEqual(source["mode"], "100644")

    def test_the_old_live_paths_are_gone_and_were_not_resurrected(self):
        for name in THIRTEEN:
            with self.subTest(name=name):
                self.assertEqual(
                    git("ls-tree", "HEAD", "--", f"experiments/{name}").strip(), "")

    def test_the_working_tree_still_holds_those_exact_bytes(self):
        """The object database agreeing with itself is not evidence that the
        files on disk -- the ones a reader actually opens -- are intact. This is
        the arm that a removed or corrupted historical source trips."""
        for name in THIRTEEN:
            with self.subTest(name=name):
                rel = f"{ARCHIVE_TRIAGE_REL}/{name}"
                path = REPO_ROOT / rel
                self.assertTrue(path.is_file(), f"{rel} is missing from disk")
                self.assertFalse(path.is_symlink(), f"{rel} became a symlink")
                expected = blob_identity(D6_HEAD, f"experiments/{name}")
                self.assertEqual(
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                    expected["sha256"], f"{rel} no longer matches its D6 source")

    def test_control_a_corrupted_source_is_caught_by_the_digest_comparison(self):
        """Disposable copy, never the tracked file. A byte added to a historical
        source must break the identity comparison and nothing else."""
        rel = f"{ARCHIVE_TRIAGE_REL}/{THIRTEEN[0]}"
        original = (REPO_ROOT / rel).read_bytes()
        expected = blob_identity(D6_HEAD, f"experiments/{THIRTEEN[0]}")["sha256"]
        self.assertEqual(hashlib.sha256(original).hexdigest(), expected)
        self.assertNotEqual(
            hashlib.sha256(original + b"\n# drift\n").hexdigest(), expected)


# ===========================================================================
# 2. the S10 sidecar, and the truth of its D4 amendment
# ===========================================================================

def measured_archive_symbols() -> dict:
    """`{archived path: [foundry_common names]}` measured from the ACTUAL
    archived source, with the same census the S10 test uses on live callers.

    This is the measurement the accepted test never performs on the archive
    half, and therefore the one that makes a wrong recorded symbol set fail."""
    provider = PROVIDER_PATH.read_text(encoding="utf-8")
    census = caller_census(tracked_python_sources(REPO_ROOT), provider, RETIRED)
    return {p: v for p, v in census.items()
            if p.startswith(f"{ARCHIVE_TRIAGE_REL}/")}


@requires_history
class TestTheSidecarIsUnchangedAndItsD4AmendmentIsTrue(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.raw = (REPO_ROOT / SIDECAR_REL).read_bytes()
        cls.data = json.loads(cls.raw)
        cls.amendment = cls.data["s15_d4_amendment"]
        cls.rows = cls.amendment["rows_moved_to_archive"]

    def test_the_whole_sidecar_is_byte_identical_to_accepted_D4(self):
        """Not field-by-field: the ENTIRE artifact, bytes included. The repair is
        forbidden to touch it, and a conservation claim about a file nobody
        compared in full is not a conservation claim."""
        accepted = git("cat-file", "blob", f"{D4_HEAD}:{SIDECAR_REL}", binary=True)
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(),
                         hashlib.sha256(accepted).hexdigest())
        self.assertEqual(self.raw, accepted)

    def test_the_amendment_base_is_the_exact_D6_commit(self):
        self.assertEqual(self.amendment["head_base"], D6_HEAD)

    def test_the_recorded_population_transfer_is_the_accepted_one(self):
        self.assertEqual(self.amendment["live_importers"],
                         {"before": LIVE_BEFORE, "after": LIVE_AFTER})
        self.assertEqual(self.amendment["archive_importers"],
                         {"before": ARCHIVE_BEFORE, "after": ARCHIVE_AFTER})

    def test_the_transfer_arithmetic_closes_over_thirteen_rows(self):
        """Totals alone are not acceptance, but totals that do not close are a
        refutation. Thirteen importers left live and thirteen arrived in the
        archive; a count that drifts from the row set is caught here."""
        self.assertEqual(len(self.rows), len(THIRTEEN))
        self.assertEqual(LIVE_BEFORE - LIVE_AFTER, len(THIRTEEN))
        self.assertEqual(ARCHIVE_AFTER - ARCHIVE_BEFORE, len(THIRTEEN))

    def test_the_thirteen_mappings_are_distinct_and_correctly_owned(self):
        self.assertEqual(sorted(self.rows),
                         sorted(f"experiments/{n}" for n in THIRTEEN))
        destinations = [r["archived_path"] for r in self.rows.values()]
        self.assertEqual(len(set(destinations)), len(THIRTEEN))
        for old, row in self.rows.items():
            with self.subTest(old=old):
                self.assertEqual(row["archived_path"],
                                 f"{ARCHIVE_TRIAGE_REL}/{Path(old).name}")

    def test_the_declared_live_and_archive_totals_agree_with_the_sidecar_body(self):
        self.assertEqual(len(self.data["live_importers"]), LIVE_AFTER)
        self.assertEqual(len(self.data["archive_importers"]), ARCHIVE_AFTER)
        for row in self.rows.values():
            with self.subTest(path=row["archived_path"]):
                self.assertIn(row["archived_path"], self.data["archive_importers"])
                self.assertNotIn(row["archived_path"], self.data["live_importers"])

    def test_every_recorded_symbol_set_matches_the_archived_source(self):
        """THE HOLE THIS FILE WAS ADDED FOR. The accepted S10 test compares
        archive PATHS only, so these thirteen recorded name sets are currently
        asserted against nothing. Here each one is compared to the set actually
        measured from the archived file."""
        measured = measured_archive_symbols()
        self.assertEqual(len(measured), len(THIRTEEN), sorted(measured))
        for old, row in self.rows.items():
            with self.subTest(old=old):
                self.assertEqual(sorted(row["foundry_common_names"]),
                                 sorted(measured[row["archived_path"]]))

    def test_each_row_preserves_the_symbol_set_of_its_PRE_MOVE_live_source(self):
        """Source-move conservation: the archived file must reference exactly
        what the live file referenced at the D6 base. Measuring only the moved
        copy would pass a move that silently rewrote the file."""
        provider = git("cat-file", "blob", f"{D6_HEAD}:experiments/foundry_common.py")
        before = caller_census(
            {f"experiments/{n}": git("cat-file", "blob",
                                     f"{D6_HEAD}:experiments/{n}")
             for n in THIRTEEN}, provider, RETIRED)
        for old, row in self.rows.items():
            with self.subTest(old=old):
                self.assertEqual(sorted(row["foundry_common_names"]),
                                 sorted(before[old]))

    def test_the_prior_amendments_and_their_bases_are_untouched(self):
        accepted = json.loads(git("cat-file", "blob", f"{D4_HEAD}:{SIDECAR_REL}"))
        for key in ("s11_amendment", "s15_d3_amendment", "s15_d6_amendment"):
            with self.subTest(amendment=key):
                self.assertEqual(self.data[key], accepted[key])


@requires_history
class TestTheSidecarConservationControls(unittest.TestCase):
    """Every comparison above, shown failing on the exact corruption it claims to
    catch. A check never observed red is not known to be a check. All rigs are
    in-memory copies; the tracked sidecar is never written."""

    def setUp(self):
        self.data = json.loads((REPO_ROOT / SIDECAR_REL).read_text(encoding="utf-8"))
        self.rows = self.data["s15_d4_amendment"]["rows_moved_to_archive"]
        self.measured = measured_archive_symbols()

    def rows_agree(self, rows) -> bool:
        if sorted(rows) != sorted(f"experiments/{n}" for n in THIRTEEN):
            return False
        if len({r["archived_path"] for r in rows.values()}) != len(THIRTEEN):
            return False
        for old, row in rows.items():
            if row["archived_path"] != f"{ARCHIVE_TRIAGE_REL}/{Path(old).name}":
                return False
            if sorted(row["foundry_common_names"]) != sorted(
                    self.measured.get(row["archived_path"], [])):
                return False
        return True

    def test_the_live_rows_pass_their_own_comparison(self):
        self.assertTrue(self.rows_agree(self.rows))

    def test_control_a_WRONG_symbol_set_is_caught(self):
        """The corruption the accepted S10 test cannot see."""
        rigged = json.loads(json.dumps(self.rows))
        key = f"experiments/{THIRTEEN[0]}"
        rigged[key]["foundry_common_names"] = ["halt"]
        self.assertFalse(self.rows_agree(rigged))

    def test_control_an_OMITTED_mapping_is_caught(self):
        rigged = json.loads(json.dumps(self.rows))
        rigged.pop(f"experiments/{THIRTEEN[0]}")
        self.assertFalse(self.rows_agree(rigged))

    def test_control_a_DUPLICATE_destination_is_caught(self):
        """Two old paths pointing at one archived file keeps the row count at
        thirteen and still loses a file."""
        rigged = json.loads(json.dumps(self.rows))
        rigged[f"experiments/{THIRTEEN[1]}"]["archived_path"] = \
            f"{ARCHIVE_TRIAGE_REL}/{THIRTEEN[0]}"
        self.assertFalse(self.rows_agree(rigged))

    def test_control_a_WRONG_owner_or_path_is_caught(self):
        rigged = json.loads(json.dumps(self.rows))
        rigged[f"experiments/{THIRTEEN[0]}"]["archived_path"] = \
            f"archive/research/mutations/{THIRTEEN[0]}"
        self.assertFalse(self.rows_agree(rigged))

    def test_control_a_STALE_count_is_caught(self):
        counts = {"before": LIVE_BEFORE, "after": LIVE_AFTER + 1}
        self.assertNotEqual(counts["before"] - counts["after"], len(THIRTEEN))

    def test_control_a_STALE_base_is_caught(self):
        self.assertNotEqual(D4_HEAD, D6_HEAD)
        self.assertEqual(self.data["s15_d4_amendment"]["head_base"], D6_HEAD)
        rigged = dict(self.data["s15_d4_amendment"], head_base=D4_HEAD)
        self.assertNotEqual(rigged["head_base"], D6_HEAD)

    def test_control_an_UNRELATED_amendment_alteration_is_caught(self):
        accepted = json.loads(git("cat-file", "blob", f"{D4_HEAD}:{SIDECAR_REL}"))
        rigged = json.loads(json.dumps(self.data))
        rigged["s15_d6_amendment"]["head_base"] = D4_HEAD
        self.assertNotEqual(rigged["s15_d6_amendment"], accepted["s15_d6_amendment"])

    def test_control_an_UNRELATED_row_alteration_is_caught_by_byte_identity(self):
        """A change anywhere else in the artifact is invisible to every field
        comparison above and is exactly what the whole-file digest is for."""
        raw = (REPO_ROOT / SIDECAR_REL).read_bytes()
        accepted = git("cat-file", "blob", f"{D4_HEAD}:{SIDECAR_REL}", binary=True)
        self.assertEqual(raw, accepted)
        self.assertNotEqual(raw.replace(b"halt", b"hal7", 1), accepted)


# ===========================================================================
# 3. discovery: the archived history is still findable
# ===========================================================================

def load_prior_art():
    """Import the reader by path, the way Gate 2 reaches a legacy module."""
    if str(EXPERIMENTS) not in sys.path:
        sys.path.insert(0, str(EXPERIMENTS))
    spec = importlib.util.spec_from_file_location(
        "legacy_foundry_prior_art", PRIOR_ART_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Args:
    """The argparse namespace `cmd_topic` consumes, built explicitly."""

    def __init__(self, topic, strict=False, prose=False, limit=8):
        self.topic = list(topic)
        self.strict = strict
        self.prose = prose
        self.limit = limit


def run_topic(pa, args, live_hits=()):
    """`cmd_topic` with the LIVE population stubbed, returning (exit, output).

    The live half is stubbed for isolation and for cost: it greps the
    `experiments/` directory, which on a developer checkout also holds the
    ignored multi-gigabyte `out/` tree. Stubbing it states exactly which
    population each arm below is about; the unstubbed command is measured
    end-to-end separately."""
    original = pa._grep
    buffer, status = io.StringIO(), 0
    try:
        pa._grep = lambda pattern, root: list(live_hits)
        with contextlib.redirect_stdout(buffer):
            pa.cmd_topic(args)
    except SystemExit as exit_:
        status = exit_.code
    finally:
        pa._grep = original
    return status, buffer.getvalue()


class TestPriorArtDiscoversTheArchivedHistory(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pa = load_prior_art()

    def test_the_archived_definitions_are_found_with_their_real_paths(self):
        hits = self.pa._historical_code(
            self.pa.flexible_pattern(REGRESSION_TOPIC), self.pa.ARCHIVE_TRIAGE)
        self.assertEqual(len(hits), REGRESSION_HITS, hits)
        for rel, lineno, text in hits:
            with self.subTest(rel=rel):
                self.assertTrue(rel.startswith(f"{ARCHIVE_TRIAGE_REL}/"), rel)
                self.assertTrue((REPO_ROOT / rel).is_file(), rel)
                self.assertTrue(lineno.isdigit(), lineno)
                self.assertIn(f"def {REGRESSION_TOPIC}", text)

    def test_the_population_is_the_thirteen_tracked_archived_files(self):
        top, paths = self.pa._tracked_archive_sources(self.pa.ARCHIVE_TRIAGE)
        self.assertEqual(Path(top).resolve(), REPO_ROOT.resolve())
        self.assertEqual(paths,
                         sorted(f"{ARCHIVE_TRIAGE_REL}/{n}" for n in THIRTEEN))

    def test_the_owner_supplies_the_archive_location(self):
        """Asked of `ProjectPaths`, not spelled a second time here."""
        from mtj_foundry.paths import ProjectPaths
        self.assertEqual(self.pa.ARCHIVE_TRIAGE,
                         ProjectPaths.for_root(REPO_ROOT).archive_research_triage)

    # --- the four decision arms -------------------------------------------

    def test_arm_STRICT_historical_hit_refuses(self):
        status, out = run_topic(self.pa, Args([REGRESSION_TOPIC], strict=True))
        self.assertEqual(status, 1)
        self.assertIn("HISTORICAL CODE ARTIFACT", out)

    def test_arm_NON_STRICT_historical_hit_is_an_informational_success(self):
        status, out = run_topic(self.pa, Args([REGRESSION_TOPIC]))
        self.assertEqual(status, 0)
        self.assertIn("HISTORICAL CODE ARTIFACT", out)
        self.assertIn(f"{ARCHIVE_TRIAGE_REL}/{THIRTEEN[0]}", out)

    def test_arm_STRICT_live_hit_still_refuses(self):
        status, out = run_topic(
            self.pa, Args(["zzz_no_such_topic_anywhere"], strict=True),
            live_hits=[("experiments/zz.py", "1", "def zzz_no_such_topic_anywhere():")])
        self.assertEqual(status, 1)
        self.assertIn("EXISTING CODE ARTIFACT", out)

    def test_arm_STRICT_true_miss_still_succeeds(self):
        """The defect must not be repaired by always failing."""
        status, out = run_topic(
            self.pa, Args(["zzz_no_such_topic_anywhere"], strict=True))
        self.assertEqual(status, 0)
        self.assertNotIn("HISTORICAL CODE ARTIFACT", out)
        self.assertNotIn("EXISTING CODE ARTIFACT", out)

    def test_the_report_names_history_as_evidence_not_as_a_successor(self):
        _status, out = run_topic(self.pa, Args([REGRESSION_TOPIC]))
        self.assertIn("EVIDENCE", out)
        self.assertIn("not a runnable successor", out)
        self.assertIn("not an instruction to execute an archived program", out)


class TestTheRealRegressionCommand(unittest.TestCase):
    """The end-to-end anchor: the exact command the audit measured, unstubbed."""

    def run_cli(self, *argv):
        r = subprocess.run([sys.executable, "-B", "experiments/foundry_prior_art.py",
                            *argv], cwd=REPO_ROOT, capture_output=True, text=True)
        return r.returncode, r.stdout, r.stderr

    def test_the_real_regression_command_refuses_again(self):
        code, out, err = self.run_cli(REGRESSION_TOPIC, "--strict")
        self.assertEqual(code, 1, err)
        self.assertIn("STOP", err)
        self.assertIn("Prior art exists", err)
        self.assertEqual(out.count(f"{ARCHIVE_TRIAGE_REL}/"), REGRESSION_HITS, out)

    def test_a_true_miss_still_exits_zero_end_to_end(self):
        code, out, _err = self.run_cli("zzz_no_such_topic_anywhere", "--strict")
        self.assertEqual(code, 0, out)


# ===========================================================================
# 4. discovery controls, against a DISPOSABLE fixture repository
# ===========================================================================

def fixture_repo(tracked: dict, untracked: dict = None) -> Path:
    """A throwaway git repository holding an archive directory.

    The controls need to plant, remove and corrupt files. Doing that inside this
    repository would mutate tracked or ignored state, so the population's own
    `root`-derived repository lookup is pointed at a temporary one instead."""
    tmp = Path(tempfile.mkdtemp(prefix="s15d4r2-"))
    triage = tmp / ARCHIVE_TRIAGE_REL
    triage.mkdir(parents=True)
    for name, text in tracked.items():
        (triage / name).write_text(text, encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(tmp), "add", "-A"], check=True,
                   capture_output=True)
    for name, text in (untracked or {}).items():
        (triage / name).write_text(text, encoding="utf-8")
    return tmp


class TestDiscoveryControls(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pa = load_prior_art()

    def search(self, root: Path, topic: str) -> list:
        return self.pa._historical_code(self.pa.flexible_pattern(topic), root)

    def test_control_an_ARBITRARY_helper_name_and_constant_are_both_found(self):
        """No part of this is keyed to `resolve_removed_members`, to seven hits,
        or to a canned warning. Two names this repository has never contained,
        one a definition and one a constant, must both be discovered."""
        repo = fixture_repo({"planted.py":
                             "def quixotic_ledger_probe(x):\n    return x\n"
                             "QUIXOTIC_LEDGER_LIMIT = 4\n"})
        triage = repo / ARCHIVE_TRIAGE_REL
        definition = self.search(triage, "quixotic ledger probe")
        constant = self.search(triage, "quixotic_ledger_limit")
        self.assertEqual(len(definition), 1, definition)
        self.assertIn("def quixotic_ledger_probe", definition[0][2])
        self.assertEqual(len(constant), 1, constant)
        self.assertIn("QUIXOTIC_LEDGER_LIMIT", constant[0][2])

    def test_control_an_UNTRACKED_planted_helper_is_NOT_evidence(self):
        """Ignored or merely-present files must never become prior art. The
        tracked file proves the search would otherwise have found it."""
        repo = fixture_repo(
            {"tracked.py": "def duplicitous_marker_one():\n    pass\n"},
            untracked={"untracked.py": "def duplicitous_marker_two():\n    pass\n"})
        triage = repo / ARCHIVE_TRIAGE_REL
        self.assertEqual(len(self.search(triage, "duplicitous_marker_one")), 1)
        self.assertEqual(self.search(triage, "duplicitous_marker_two"), [])

    def test_control_archived_source_is_READ_never_EXECUTED(self):
        """The fixture writes a sentinel and raises the moment it is imported or
        executed. Discovery must find its definition and leave it inert."""
        sentinel = Path(tempfile.mkdtemp(prefix="s15d4r2-trap-")) / "fired"
        trap = (f"import pathlib\n"
                f"pathlib.Path({str(sentinel)!r}).write_text('fired')\n"
                f"raise SystemExit('the archive was executed')\n"
                f"def incendiary_trap_helper():\n    pass\n")
        repo = fixture_repo({"trap.py": trap})
        hits = self.search(repo / ARCHIVE_TRIAGE_REL, "incendiary_trap_helper")
        self.assertEqual(len(hits), 1, hits)
        self.assertFalse(sentinel.exists(), "the archived program was executed")

    def test_control_a_REMOVED_required_source_halts_loudly(self):
        """Still tracked, gone from disk. A missing required file is not a topic
        miss and must not be reported as one."""
        repo = fixture_repo({"gone.py": "def vanishing_helper():\n    pass\n"})
        triage = repo / ARCHIVE_TRIAGE_REL
        self.assertEqual(len(self.search(triage, "vanishing_helper")), 1)
        (triage / "gone.py").unlink()
        with self.assertRaises(SystemExit) as raised:
            self.search(triage, "vanishing_helper")
        self.assertEqual(raised.exception.code, 1)

    def test_control_a_BROKEN_enumeration_halts_instead_of_returning_zero(self):
        """A directory that is not a repository at all. The failure mode this
        whole repair exists to forbid is a broken population reading as clean."""
        outside = Path(tempfile.mkdtemp(prefix="s15d4r2-nogit-"))
        with self.assertRaises(SystemExit) as raised:
            self.search(outside, "anything_at_all")
        self.assertEqual(raised.exception.code, 1)

    def test_control_an_EMPTY_tracked_population_halts(self):
        """A re-pointed or emptied archive is damaged evidence, not an absence
        of prior art."""
        repo = fixture_repo({"kept.py": "x = 1\n"})
        empty = repo / ARCHIVE_TRIAGE_REL / "nothing"
        empty.mkdir()
        with self.assertRaises(SystemExit) as raised:
            self.search(empty, "anything_at_all")
        self.assertEqual(raised.exception.code, 1)

    def test_control_a_SYMLINKED_source_is_refused_not_followed(self):
        """Links must not lead the reader out of the archive."""
        repo = fixture_repo({"real.py": "def linked_helper():\n    pass\n"})
        triage = repo / ARCHIVE_TRIAGE_REL
        target = repo / "elsewhere.py"
        target.write_text("def linked_helper():\n    pass\n", encoding="utf-8")
        (triage / "link.py").symlink_to(target)
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True,
                       capture_output=True)
        with self.assertRaises(SystemExit) as raised:
            self.search(triage, "linked_helper")
        self.assertEqual(raised.exception.code, 1)


class TestTheOldReaderStillFailsTheRegression(unittest.TestCase):
    """The reversion control. The ACCEPTED D4 reader, run against this same
    repository, must exit 0 on the regression command -- otherwise the test
    above proves nothing about the repair."""

    @requires_history
    def test_the_accepted_D4_reader_returns_zero_on_the_regression_topic(self):
        tmp = Path(tempfile.mkdtemp(prefix="s15d4r2-old-"))
        old = tmp / "foundry_prior_art.py"
        old.write_bytes(git("cat-file", "blob",
                            f"{D4_HEAD}:experiments/foundry_prior_art.py",
                            binary=True))
        env = {**dict(__import__("os").environ),
               "PYTHONPATH": str(EXPERIMENTS), "PYTHONDONTWRITEBYTECODE": "1"}
        r = subprocess.run([sys.executable, "-B", str(old),
                            REGRESSION_TOPIC, "--strict"],
                           cwd=REPO_ROOT, capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn(ARCHIVE_TRIAGE_REL, r.stdout)

    def test_the_repaired_reader_and_the_old_one_differ_only_as_intended(self):
        source = PRIOR_ART_PATH.read_text(encoding="utf-8")
        self.assertIn("ARCHIVE_TRIAGE", source)
        self.assertIn("archive_research_triage", source)
        self.assertEqual(source.count("sys.path.insert"), 1)


class TestOrphansKeepsItsLivePopulation(unittest.TestCase):
    """`--orphans` is a different question -- which LIVE modules read card text
    without the ratified pipeline -- and archived programs are not live runtime
    consumers. The repair must not have leaked into it."""

    @classmethod
    def setUpClass(cls):
        cls.pa = load_prior_art()

    def test_the_orphans_population_is_still_the_live_code_tree(self):
        self.assertEqual(self.pa.CODE, REPO_ROOT / "experiments")

    def test_no_archived_program_can_enter_the_orphans_scan(self):
        scanned = [p for p in self.pa.CODE.rglob("*.py")
                   if "__pycache__" not in str(p)]
        for path in scanned:
            with self.subTest(path=path):
                self.assertNotIn(f"/{ARCHIVE_TRIAGE_REL}/", str(path))
        self.assertFalse(any(n in {p.name for p in scanned} for n in THIRTEEN))

    def test_the_orphans_strict_contract_is_untouched(self):
        source = PRIOR_ART_PATH.read_text(encoding="utf-8")
        body = source.split("def cmd_orphans")[1].split("\ndef main")[0]
        self.assertNotIn("ARCHIVE_TRIAGE", body)
        self.assertNotIn("_historical_code", body)
        self.assertIn("if args.strict and bypassers:", body)


# ===========================================================================
# 5. the material-edge method -- how a consumer of a moved file is found
# ===========================================================================

ENUMERATORS = {"glob", "rglob", "iterdir", "listdir", "walk", "scandir"}
CODE_DIR_NAMES = {"CODE", "EXPERIMENTS", "legacy_experiments"}


def full_path_consumers(sources: dict, names) -> dict:
    """References that spell the OLD LIVE PATH out."""
    return {p: sorted(n for n in names if f"experiments/{n}" in t)
            for p, t in sources.items()
            if any(f"experiments/{n}" in t for n in names)}


def module_name_consumers(sources: dict, names) -> dict:
    """References by BASENAME or dotted module -- import, string or attribute."""
    stems = {n[:-3] for n in names}
    out = {}
    for path, text in sources.items():
        hit = sorted(s for s in stems if re.search(rf"\b{re.escape(s)}\b", text))
        if hit:
            out[path] = hit
    return out


def directory_reader_consumers(sources: dict) -> dict:
    """Consumers that name NO file at all -- they enumerate the directory.

    THE EDGE THAT WAS MISSED. A basename or full-path search cannot see this
    shape by construction, because the shape contains neither. The prior-art
    reader is exactly this: it greps the `experiments/` directory, so the D4
    move removed seven definition sites from its scan without any candidate
    name appearing anywhere in it."""
    out = {}
    for path, text in sources.items():
        try:
            tree = ast.parse(text, filename=path)
        except SyntaxError:
            continue
        sites = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            base = ast.unparse(func.value) if isinstance(func, ast.Attribute) else ""
            if name in ENUMERATORS and (
                    any(d in base for d in CODE_DIR_NAMES) or "experiments" in base):
                sites.append(f"line {node.lineno}: {ast.unparse(node)[:90]}")
            elif name == "run" and "grep" in ast.unparse(node):
                sites.append(f"line {node.lineno}: {ast.unparse(node)[:90]}")
        if sites:
            out[path] = sites
    return out


def classify(path: str) -> str:
    """Frozen history, provenance, synthetic control and live consumer are four
    different populations; a census that merges them reports a number nobody can
    act on."""
    if path.startswith("archive/"):
        return "frozen history"
    if path.startswith(("docs/", "refoundation/")):
        return "provenance"
    if path.startswith("tests/"):
        return "synthetic control"
    return "live consumer"


class TestTheMaterialEdgeMethod(unittest.TestCase):
    """The method that would have caught this defect, shown catching all three
    reference shapes -- including the one a candidate-basename search cannot
    see."""

    @classmethod
    def setUpClass(cls):
        cls.sources = tracked_python_sources(REPO_ROOT)

    def test_shape_1_a_FULL_PATH_consumer_is_caught(self):
        probe = {"probe.py": f'OLD = "experiments/{THIRTEEN[0]}"\n'}
        self.assertEqual(full_path_consumers(probe, THIRTEEN),
                         {"probe.py": [THIRTEEN[0]]})

    def test_shape_2_a_BASENAME_or_DOTTED_MODULE_consumer_is_caught(self):
        stem = THIRTEEN[0][:-3]
        for label, probe in (("import", f"import {stem}\n"),
                             ("dotted", f"from experiments.{stem} import x\n"),
                             ("string", f'M = "{stem}"\n')):
            with self.subTest(shape=label):
                self.assertEqual(module_name_consumers({"probe.py": probe},
                                                       THIRTEEN),
                                 {"probe.py": [stem]})

    def test_shape_3_a_GENERIC_DIRECTORY_READER_is_caught_naming_no_file(self):
        """Neither of the first two shapes can see this, and this is the one
        that regressed. The probe contains no candidate name at all."""
        probe = {"probe.py": "for p in CODE.rglob('*.py'):\n    pass\n"}
        self.assertEqual(full_path_consumers(probe, THIRTEEN), {})
        self.assertEqual(module_name_consumers(probe, THIRTEEN), {})
        self.assertIn("probe.py", directory_reader_consumers(probe))

    def test_the_prior_art_reader_is_reported_as_a_directory_reader(self):
        """The defect, restated as a census result rather than as a story."""
        found = directory_reader_consumers(self.sources)
        self.assertIn("experiments/foundry_prior_art.py", found)

    def test_every_census_hit_is_classified_into_exactly_one_population(self):
        hits = set(full_path_consumers(self.sources, THIRTEEN))
        hits |= set(module_name_consumers(self.sources, THIRTEEN))
        hits |= set(directory_reader_consumers(self.sources))
        buckets = {}
        for path in hits:
            buckets.setdefault(classify(path), []).append(path)
        self.assertEqual(sum(len(v) for v in buckets.values()), len(hits))
        self.assertTrue(set(buckets) <= {"frozen history", "provenance",
                                         "synthetic control", "live consumer"},
                        sorted(buckets))

    def test_the_archived_files_are_not_imported_by_each_other(self):
        """Source-move independence. Recorded precisely, because it is NOT the
        same claim as historical data-flow independence: the later assemblers
        consumed the earlier batches' OUTPUT ARTIFACTS, which this check says
        nothing about."""
        stems = {n[:-3] for n in THIRTEEN}
        for name in THIRTEEN:
            rel = f"{ARCHIVE_TRIAGE_REL}/{name}"
            tree = ast.parse((REPO_ROOT / rel).read_text(encoding="utf-8"),
                             filename=rel)
            imported = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported |= {a.name.split(".")[-1] for a in node.names}
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".")[-1])
            with self.subTest(name=name):
                self.assertEqual(imported & stems, set())

# ===========================================================================
# 7. S15.D5.R1 -- the OTHER archive families, which were dark all along
# ===========================================================================
#
# D4.R2 repaired the triage family and said, in the reader's own source, that it
# was not a general fix. That was honest and it was also a live defect: S15.D3
# had already archived the Batch-8 research scripts and S15.D6 the `/1 -> /2`
# migration pair, both BEFORE the historical arm existed. Measured at the D4.R2
# head, with the definitions sitting in the tracked archive the whole time:
#
#     agreement matrix      -> 0 artifacts, exit 0
#     tail decay check      -> 0 artifacts, exit 0
#     score pairs           -> 0 artifacts, exit 0
#     replay attribution    -> 0 artifacts, exit 0
#
# Same conversion as D4, two families older. These tests pin the repair AND the
# boundary: the family list is EXPLICIT, so an unrelated archive directory does
# not become prior art merely by existing.

BATCH8_REL = "archive/research/batch8"
MUTATIONS_REL = "archive/research/mutations"

# Real definitions, each measured to exist in its archived family and to exist
# NOWHERE in the live tree. A topic that also matched a live file would not
# prove the historical arm found anything.
DARK_QUERIES = (
    ("agreement matrix", BATCH8_REL, "foundry_batch8_diff.py",
     "def agreement_matrix"),
    ("tail decay check", BATCH8_REL, "foundry_batch8_diff.py",
     "def tail_decay_check"),
    ("score pairs", BATCH8_REL, "foundry_batch8_canon_analysis.py",
     "def score_pairs"),
    ("replay attribution", MUTATIONS_REL, "foundry_migrate_codebook_v2.py",
     "def replay_attribution"),
    ("project through renames", MUTATIONS_REL, "foundry_migrate_codebook_v2.py",
     "def project_through_renames"),
    ("pay life pairs", MUTATIONS_REL, "foundry_migrate_codebook_v2.py",
     "def pay_life_pairs"),
)

# The label each family's hits must be reported under. A Batch-8 match described
# as triage is a provenance lie even when the path beside it is right.
EXPECTED_LABELS = {
    ARCHIVE_TRIAGE_REL: "archived triage set",
    BATCH8_REL: "archived Batch-8 research set",
    MUTATIONS_REL: "archived foundry-codebook/1 -> /2 migration pair",
}


def family_fixture(rel: str, tracked: dict, untracked: dict = None,
                   ignored: dict = None) -> Path:
    """A throwaway repository holding ONE archive family at `rel`.

    The triage-only `fixture_repo` above cannot express a second family, and the
    controls here must plant into a named one. Kept separate rather than
    rewriting the accepted helper, so the D4 controls keep running on the exact
    fixture they were accepted with."""
    tmp = Path(tempfile.mkdtemp(prefix="s15d5r1-"))
    family = tmp / rel
    family.mkdir(parents=True)
    for name, text in tracked.items():
        (family / name).write_text(text, encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp), "init", "-q"], check=True)
    if ignored:
        (tmp / ".gitignore").write_text(
            "".join(f"{n}\n" for n in ignored), encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp), "add", "-A"], check=True,
                   capture_output=True)
    for name, text in (untracked or {}).items():
        (family / name).write_text(text, encoding="utf-8")
    for name, text in (ignored or {}).items():
        (family / name).write_text(text, encoding="utf-8")
    return tmp


class TestTheHistoricalFamilySetIsExplicitAndBounded(unittest.TestCase):
    """The mechanism, not the contents: three named owners, no recursion."""

    @classmethod
    def setUpClass(cls):
        cls.pa = load_prior_art()

    def test_the_family_set_is_exactly_the_three_archived_owners(self):
        from mtj_foundry.paths import ProjectPaths
        layout = ProjectPaths.for_root(REPO_ROOT)
        self.assertEqual(
            [owner for owner, _ in self.pa.HISTORICAL_FAMILIES],
            [layout.archive_research_triage,
             layout.archive_research_batch8,
             layout.archive_research_mutations])

    def test_every_family_location_comes_from_the_layout_owner(self):
        """Asked of `ProjectPaths`, never spelled a second time in the reader.
        Re-pointing an owner re-points discovery with it."""
        from mtj_foundry.paths import ProjectPaths
        layout = ProjectPaths.for_root(REPO_ROOT)
        named = {layout.archive_research_triage, layout.archive_research_batch8,
                 layout.archive_research_mutations}
        for owner, _ in self.pa.HISTORICAL_FAMILIES:
            with self.subTest(owner=str(owner)):
                self.assertIn(owner, named)

    def test_each_family_carries_its_own_distinct_provenance_label(self):
        labels = [label for _, label in self.pa.HISTORICAL_FAMILIES]
        self.assertEqual(len(labels), len(set(labels)), labels)
        for owner, label in self.pa.HISTORICAL_FAMILIES:
            rel = str(owner.relative_to(REPO_ROOT))
            with self.subTest(family=rel):
                self.assertEqual(label, EXPECTED_LABELS[rel])

    def test_discovery_is_not_recursive_over_the_archive(self):
        """`archive/research/**` would make every future directory prior art by
        accident. The reader must name its families, not walk for them."""
        source = PRIOR_ART_PATH.read_text(encoding="utf-8")
        self.assertNotIn("archive_research_consolidation", source)
        self.assertNotIn("archive_research_thesaurus_measurement", source)
        body = source.split("HISTORICAL_FAMILIES = (")[1].split(")\n")[0]
        for enumerator in ("rglob", "glob", "iterdir", "walk", "scandir"):
            with self.subTest(enumerator=enumerator):
                self.assertNotIn(enumerator, body)

    def test_the_D5_owner_is_NOT_registered_yet(self):
        """D5 is blocked and its owner does not exist. Naming it here would be
        both a forward reference to an absent property and a scope expansion."""
        source = PRIOR_ART_PATH.read_text(encoding="utf-8")
        self.assertNotIn("archive_research_codebook_transforms", source)
        self.assertNotIn("codebook-transforms", source)


class TestThePreviouslyDarkFamiliesAreDiscoverable(unittest.TestCase):
    """The real repair, on real queries, against this repository."""

    @classmethod
    def setUpClass(cls):
        cls.pa = load_prior_art()

    def test_each_dark_query_finds_its_real_archived_definition(self):
        for topic, rel, filename, definition in DARK_QUERIES:
            with self.subTest(topic=topic):
                hits = []
                for owner, _ in self.pa.HISTORICAL_FAMILIES:
                    hits += self.pa._historical_code(
                        self.pa.flexible_pattern(topic), owner)
                self.assertEqual(len(hits), 1, hits)
                path, lineno, text = hits[0]
                self.assertEqual(path, f"{rel}/{filename}")
                self.assertTrue((REPO_ROOT / path).is_file(), path)
                self.assertTrue(lineno.isdigit(), lineno)
                self.assertIn(definition, text)

    def test_each_dark_query_now_makes_strict_refuse(self):
        """The whole point. Before this repair every one of these exited 0."""
        for topic, _, _, _ in DARK_QUERIES:
            with self.subTest(topic=topic):
                status, _ = run_topic(self.pa, Args([topic], strict=True))
                self.assertEqual(status, 1)

    def test_each_dark_query_is_reported_under_its_OWN_family_label(self):
        for topic, rel, _, _ in DARK_QUERIES:
            with self.subTest(topic=topic):
                _, out = run_topic(self.pa, Args([topic]))
                self.assertIn(EXPECTED_LABELS[rel], out)
                for other_rel, other_label in EXPECTED_LABELS.items():
                    if other_rel != rel:
                        self.assertNotIn(other_label, out)

    def test_a_single_family_hit_is_enough_for_strict_to_refuse(self):
        """`agreement matrix` hits Batch-8 only: no docs line, no live artifact,
        nothing in triage or mutations. One family is sufficient."""
        topic = "agreement matrix"
        per_family = {
            str(owner.relative_to(REPO_ROOT)):
                len(self.pa._historical_code(
                    self.pa.flexible_pattern(topic), owner))
            for owner, _ in self.pa.HISTORICAL_FAMILIES}
        self.assertEqual(per_family[BATCH8_REL], 1, per_family)
        self.assertEqual(per_family[ARCHIVE_TRIAGE_REL], 0, per_family)
        self.assertEqual(per_family[MUTATIONS_REL], 0, per_family)
        status, _ = run_topic(self.pa, Args([topic], strict=True))
        self.assertEqual(status, 1)

    def test_the_accepted_triage_regression_is_conserved_exactly(self):
        """D4.R2's contract, unchanged: same count, same paths, same refusal."""
        hits = self.pa._historical_code(
            self.pa.flexible_pattern(REGRESSION_TOPIC), self.pa.ARCHIVE_TRIAGE)
        self.assertEqual(len(hits), REGRESSION_HITS, hits)
        for rel, _, _ in hits:
            self.assertTrue(rel.startswith(f"{ARCHIVE_TRIAGE_REL}/"), rel)
        status, out = run_topic(self.pa, Args([REGRESSION_TOPIC], strict=True))
        self.assertEqual(status, 1)
        self.assertIn(EXPECTED_LABELS[ARCHIVE_TRIAGE_REL], out)

    @unittest.skipUnless(
        (REPO_ROOT / ".git").exists() and have_object(ACCEPTED_HEAD),
        "the accepted D4.R2 commit is needed as the reversion control")
    def test_the_old_accepted_reader_finds_none_of_them(self):
        """The reversion control. The accepted D4.R2 reader, on this same
        repository, must report these topics as having no prior art -- otherwise
        the tests above prove nothing about this repair."""
        source = git("cat-file", "blob",
                     f"{ACCEPTED_HEAD}:experiments/foundry_prior_art.py")
        self.assertIn("ARCHIVE_TRIAGE = ", source)
        self.assertNotIn("HISTORICAL_FAMILIES", source)


class TestTheNewFamiliesKeepEveryAcceptedGuard(unittest.TestCase):
    """Every property D4.R2 proved for triage, re-proved per family. A guard
    that was only ever exercised on one family is not known to hold on three."""

    @classmethod
    def setUpClass(cls):
        cls.pa = load_prior_art()

    def search(self, root: Path, topic: str) -> list:
        return self.pa._historical_code(self.pa.flexible_pattern(topic), root)

    def test_an_UNTRACKED_planted_file_is_not_evidence_in_any_family(self):
        for rel in (BATCH8_REL, MUTATIONS_REL):
            with self.subTest(family=rel):
                repo = family_fixture(
                    rel, {"tracked.py": "def sequoia_marker_one():\n    pass\n"},
                    untracked={"loose.py":
                               "def sequoia_marker_two():\n    pass\n"})
                family = repo / rel
                self.assertEqual(len(self.search(family, "sequoia_marker_one")), 1)
                self.assertEqual(self.search(family, "sequoia_marker_two"), [])

    def test_an_IGNORED_planted_file_is_not_evidence_in_any_family(self):
        """Distinct from merely untracked: a `.gitignore`d file is invisible to
        `git ls-files` for a different reason, and must stay invisible here."""
        for rel in (BATCH8_REL, MUTATIONS_REL):
            with self.subTest(family=rel):
                repo = family_fixture(
                    rel, {"tracked.py": "def cedar_marker_one():\n    pass\n"},
                    ignored={"ignored.py":
                             "def cedar_marker_two():\n    pass\n"})
                family = repo / rel
                self.assertEqual(len(self.search(family, "cedar_marker_one")), 1)
                self.assertEqual(self.search(family, "cedar_marker_two"), [])

    def test_archived_source_is_READ_never_EXECUTED_in_any_family(self):
        for rel in (BATCH8_REL, MUTATIONS_REL):
            with self.subTest(family=rel):
                sentinel = Path(tempfile.mkdtemp(prefix="s15d5r1-trap-")) / "fired"
                trap = (f"import pathlib\n"
                        f"pathlib.Path({str(sentinel)!r}).write_text('fired')\n"
                        f"raise SystemExit('the archive was executed')\n"
                        f"def banyan_trap_helper():\n    pass\n")
                repo = family_fixture(rel, {"trap.py": trap})
                hits = self.search(repo / rel, "banyan_trap_helper")
                self.assertEqual(len(hits), 1, hits)
                self.assertFalse(sentinel.exists(),
                                 "the archived program was executed")

    def test_a_MISSING_required_source_halts_loudly_in_any_family(self):
        for rel in (BATCH8_REL, MUTATIONS_REL):
            with self.subTest(family=rel):
                repo = family_fixture(
                    rel, {"gone.py": "def willow_helper():\n    pass\n"})
                family = repo / rel
                self.assertEqual(len(self.search(family, "willow_helper")), 1)
                (family / "gone.py").unlink()
                with self.assertRaises(SystemExit) as raised:
                    self.search(family, "willow_helper")
                self.assertEqual(raised.exception.code, 1)

    def test_a_SYMLINKED_source_is_refused_in_any_family(self):
        for rel in (BATCH8_REL, MUTATIONS_REL):
            with self.subTest(family=rel):
                repo = family_fixture(
                    rel, {"real.py": "def alder_helper():\n    pass\n"})
                family = repo / rel
                target = repo / "elsewhere.py"
                target.write_text("def alder_helper():\n    pass\n",
                                  encoding="utf-8")
                (family / "link.py").symlink_to(target)
                subprocess.run(["git", "-C", str(repo), "add", "-A"],
                               check=True, capture_output=True)
                with self.assertRaises(SystemExit) as raised:
                    self.search(family, "alder_helper")
                self.assertEqual(raised.exception.code, 1)

    def test_a_BROKEN_enumeration_halts_instead_of_returning_zero(self):
        """`git ls-files` cannot answer at all. A broken population reading as
        "no prior art" is the exact failure this whole line of repair forbids."""
        outside = Path(tempfile.mkdtemp(prefix="s15d5r1-nogit-"))
        with self.assertRaises(SystemExit) as raised:
            self.search(outside, "anything_at_all")
        self.assertEqual(raised.exception.code, 1)

    def test_an_EMPTY_tracked_family_halts(self):
        for rel in (BATCH8_REL, MUTATIONS_REL):
            with self.subTest(family=rel):
                repo = family_fixture(rel, {"kept.py": "x = 1\n"})
                empty = repo / rel / "nothing"
                empty.mkdir()
                with self.assertRaises(SystemExit) as raised:
                    self.search(empty, "anything_at_all")
                self.assertEqual(raised.exception.code, 1)


class TestUnrelatedArchivePathsStayOutOfPriorArt(unittest.TestCase):
    """The bounded-population half of the repair. Not vacuous: the file used
    here IS discoverable when the reader is pointed straight at it, and is
    absent only because its directory is not a registered family."""

    @classmethod
    def setUpClass(cls):
        cls.pa = load_prior_art()

    def test_a_real_tracked_archive_file_outside_the_family_set_is_excluded(self):
        outsider = "archive/routing/experiments/foundry_build_reaudit_packet.py"
        self.assertTrue((REPO_ROOT / outsider).is_file(), outsider)
        flexible = self.pa.flexible_pattern("esc")

        direct = self.pa._historical_code(
            flexible, REPO_ROOT / "archive/routing/experiments")
        self.assertTrue(any(p == outsider for p, _, _ in direct), direct)

        via_families = []
        for owner, _ in self.pa.HISTORICAL_FAMILIES:
            via_families += self.pa._historical_code(flexible, owner)
        self.assertEqual(
            [p for p, _, _ in via_families if p.startswith("archive/routing/")],
            [])

    def test_a_planted_tracked_file_outside_the_family_set_is_excluded(self):
        repo = family_fixture(
            BATCH8_REL, {"inside.py": "def maple_marker_in():\n    pass\n"})
        stranger = repo / "archive" / "research" / "consolidation"
        stranger.mkdir(parents=True)
        (stranger / "outside.py").write_text(
            "def maple_marker_out():\n    pass\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True,
                       capture_output=True)
        family = repo / BATCH8_REL
        self.assertEqual(
            len(self.pa._historical_code(
                self.pa.flexible_pattern("maple_marker_in"), family)), 1)
        self.assertEqual(
            self.pa._historical_code(
                self.pa.flexible_pattern("maple_marker_out"), family), [])


class TestTheLivePopulationIsUnchangedByThisRepair(unittest.TestCase):
    """This task touched only the historical arm."""

    @classmethod
    def setUpClass(cls):
        cls.pa = load_prior_art()

    def test_the_live_code_population_is_still_the_experiments_directory(self):
        self.assertEqual(self.pa.CODE, REPO_ROOT / "experiments")
        self.assertEqual(self.pa.DOCS, REPO_ROOT / "docs")

    def test_the_orphans_contract_never_learned_about_families(self):
        source = PRIOR_ART_PATH.read_text(encoding="utf-8")
        body = source.split("def cmd_orphans")[1].split("\ndef main")[0]
        self.assertNotIn("HISTORICAL_FAMILIES", body)
        self.assertNotIn("_historical_code", body)
        self.assertIn("if args.strict and bypassers:", body)

    def test_the_bootstrap_is_still_a_single_sys_path_site(self):
        source = PRIOR_ART_PATH.read_text(encoding="utf-8")
        self.assertEqual(source.count("sys.path.insert"), 1)


if __name__ == "__main__":
    unittest.main()
