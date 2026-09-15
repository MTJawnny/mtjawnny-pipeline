"""S14 — AQ4 is frozen evidence under `benchmarks/aq4`, and stays PAUSED.

Stdlib only, like the rest of this tree.

WHAT S14 DID
------------
The 28-file AQ4 payload (benchmark package, probes, the historical contract and
six AQ4 source/review/incident papers) moved verbatim to the layout owner's
frozen-evidence home, `ProjectPaths.benchmarks_aq4`. `FREEZE-MANIFEST.json` records
every source -> destination pair with its exact SHA-256 and byte size. Six papers
left the top-level `docs/` ruling-registry population, so the live ratchet's
`ruling_registry` section was re-pinned and ONE successor was appended to the
ratchet succession record under this task's durable authorization.

WHAT IS PROVED HERE
-------------------
1. The manifest is canonical, ratifies nothing, and is EXHAUSTIVE: the tracked
   files under `benchmarks/aq4` are exactly its destinations plus its two
   declared non-payload files, and every destination has its recorded bytes.
2. No old source survives (tracked or on disk), and cohort-4/5 stay absent.
3. Frozen Python is `aq4_PAUSED` for the layout census and nothing in
   `src/mtj_foundry` imports or names it.
4. The live PAUSED pointer routes to the frozen contract that actually exists.
5. The ratchet transition is atomic: the live baseline differs from P0.3A
   genesis only in `ruling_registry`, that section equals the registry measured
   now, and the successor carries exactly `["ruling_registry"]` and this task's
   authorization.
6. Deletion safety is still load-bearing: a synthetic sole-home paper is BLOCKED.

No frozen AQ4 code is imported or executed by any of this.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.refoundation import layout_census
from tests.refoundation.helpers import REPO_ROOT
from tests.refoundation.test_ratchet_baseline_succession import (
    GENESIS_SNAPSHOT, LIVE_BASELINE, latest_entry, load_succession)

from mtj_foundry.paths import ProjectPaths

PATHS = ProjectPaths.for_root(REPO_ROOT)
FREEZE_ROOT_REL = "benchmarks/aq4"
MANIFEST = REPO_ROOT / FREEZE_ROOT_REL / "FREEZE-MANIFEST.json"
MANIFEST_REL = f"{FREEZE_ROOT_REL}/FREEZE-MANIFEST.json"
README_REL = f"{FREEZE_ROOT_REL}/README.md"
FREEZE_AUTHORIZATION = "issue:1#issuecomment-5675245200"
SOURCE_ACCEPTED_HEAD = "6c9e1b24ee8d56cfae5bc5617ed0e70925bd47a7"
POINTER_REL = "docs/AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md"
FROZEN_CONTRACT_REL = f"{FREEZE_ROOT_REL}/docs/AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md"
OLD_CONTRACT_REL = "archive/routing/docs/AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md"
MOVED_DOCS = (
    "SEMANTIC-IR-PROPOSAL-REVIEW-2026-08-14.md",
    "AQ4-BENCHMARK-PRECOMMIT-ARCHITECTURE-ADDENDUM-2026-08-14.md",
    "AQ4-CROSS-CARD-NORMALIZATION-ARCHITECTURE-ADDENDUM-2026-08-14.md",
    "AQ4-PREIMPLEMENTATION-ADVERSARIAL-CORRECTIONS-2026-08-14.md",
    "INCIDENT-AQ4-PACKET7-STOP-BREACH-2026-08-17.md",
    "INCIDENT-AQ4-PHASE-A-ADJUDICATOR-A-STOP-BREACH-2026-08-17.md",
)
TOP_FIELDS = ("claims", "classification", "freeze_authorization", "frozen_absences",
              "layout_owner", "non_payload_files", "payload", "payload_count",
              "payload_count_by_classification", "payload_total_bytes", "schema",
              "source_accepted_head", "status", "this_manifest_ratifies")
ENTRY_FIELDS = ("classification", "destination_path", "sha256", "size_bytes", "source_path")
CLASSES = ("ARCHITECTURE_SOURCE_REVIEW", "BENCHMARK_COHORT", "BENCHMARK_PROVENANCE",
           "EXECUTABLE_CODE_FROZEN", "HISTORICAL_CONTRACT", "HOLDOUT_PRECOMMITMENT",
           "INCIDENT_GOVERNANCE_PROVENANCE", "SCHEMA_CONFIG_DATA")
# Names that would only appear in production code that reached for frozen AQ4.
FROZEN_NEEDLES = ("benchmarks/aq4", "aq4_benchmark", "foundry_aq4_probes", "aq4_binding",
                  "aq4_compare", "aq4_pairing", "aq4_population", "aq4_projection")


def tracked(prefix: str) -> list[str]:
    out = subprocess.run(["git", "-C", str(REPO_ROOT), "ls-files", "-z", "--", prefix],
                         capture_output=True, check=True).stdout.decode().split("\0")
    return sorted(p for p in out if p)


def load_manifest(path: Path = MANIFEST) -> dict:
    doc = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise AssertionError(f"freeze manifest at {path} is not a JSON object")
    return doc


def expected_destination(source: str) -> str:
    """The one relocation rule: experiments keep their tree, papers go to docs/."""
    if source.startswith("experiments/"):
        return f"{FREEZE_ROOT_REL}/{source}"
    return f"{FREEZE_ROOT_REL}/docs/{Path(source).name}"


def manifest_problems(doc: dict, root: Path, tracked_under_root: list[str]) -> list[str]:
    """Every freeze-manifest law, against the files as they are on disk."""
    out: list[str] = []
    if sorted(doc) != sorted(TOP_FIELDS):
        return [f"top-level fields {sorted(doc)} != {sorted(TOP_FIELDS)}"]
    fixed = {"schema": "mtj-aq4-freeze-manifest/1", "status": "PAUSED",
             "classification": "FROZEN_EVIDENCE", "this_manifest_ratifies": "NOTHING",
             "claims": "EXACT_BYTES_AND_TOPOLOGY_ONLY",
             "source_accepted_head": SOURCE_ACCEPTED_HEAD,
             "freeze_authorization": FREEZE_AUTHORIZATION,
             "layout_owner": "mtj_foundry.paths.ProjectPaths.benchmarks_aq4",
             "non_payload_files": sorted([MANIFEST_REL, README_REL])}
    for key, value in fixed.items():
        if doc[key] != value:
            out.append(f"{key} is {doc[key]!r}, expected {value!r}")
    payload = doc["payload"]
    if not isinstance(payload, list) or not payload:
        return out + ["payload must be a non-empty list"]
    destinations = []
    counts: dict[str, int] = {}
    for entry in payload:
        if not isinstance(entry, dict) or sorted(entry) != sorted(ENTRY_FIELDS):
            out.append(f"malformed payload entry {entry!r}")
            continue
        src, dst = entry["source_path"], entry["destination_path"]
        destinations.append(dst)
        counts[entry["classification"]] = counts.get(entry["classification"], 0) + 1
        if entry["classification"] not in CLASSES:
            out.append(f"{dst}: unknown classification {entry['classification']!r}")
        if dst != expected_destination(src):
            out.append(f"{src} -> {dst} breaks the relocation rule")
        target = root / dst
        if not target.is_file():
            out.append(f"{dst} is missing")
        else:
            data = target.read_bytes()
            if (hashlib.sha256(data).hexdigest(), len(data)) != (entry["sha256"], entry["size_bytes"]):
                out.append(f"{dst} bytes differ from the manifest")
        if (root / src).exists():
            out.append(f"old source {src} still exists")
    if destinations != sorted(destinations) or len(set(destinations)) != len(destinations):
        out.append("payload is not uniquely ordered by destination_path")
    if doc["payload_count"] != len(payload):
        out.append(f"payload_count {doc['payload_count']} != {len(payload)} entries")
    if doc["payload_total_bytes"] != sum(e.get("size_bytes", 0) for e in payload if isinstance(e, dict)):
        out.append("payload_total_bytes does not sum the entries")
    if doc["payload_count_by_classification"] != dict(sorted(counts.items())):
        out.append("payload_count_by_classification does not match the entries")
    expected_tree = sorted(destinations + [MANIFEST_REL, README_REL])
    if tracked_under_root != expected_tree:
        extra = sorted(set(tracked_under_root) - set(expected_tree))
        missing = sorted(set(expected_tree) - set(tracked_under_root))
        out.append(f"tracked tree != manifest (extra {extra}, untracked {missing})")
    for absent in doc["frozen_absences"]:
        if (root / absent).exists():
            out.append(f"frozen absence violated: {absent} exists")
    if doc["frozen_absences"] != [
            f"{FREEZE_ROOT_REL}/experiments/aq4_benchmark/cohorts/cohort-4.json",
            f"{FREEZE_ROOT_REL}/experiments/aq4_benchmark/cohorts/cohort-5.json"]:
        out.append("frozen_absences must name exactly cohort-4 and cohort-5")
    return out


def production_references(src_root: Path) -> list[str]:
    """Imports of, or string constants naming, frozen AQ4 in `src/mtj_foundry`."""
    hits = []
    for path in sorted(src_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                names = [node.value]
            for name in names:
                if any(needle in name for needle in FROZEN_NEEDLES):
                    hits.append(f"{path.relative_to(src_root.parent.parent)}:{node.lineno}: {name[:60]!r}")
    return hits


def ruling_registry_metrics(root: Path) -> dict:
    """Build the registry read-only in a child process (the tool bootstraps the
    legacy boundary on import, so it is kept out of this test process)."""
    script = (
        "import importlib.util, json, sys\n"
        "spec = importlib.util.spec_from_file_location('rr', sys.argv[1])\n"
        "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
        "reg = m.build()\n"
        "print(json.dumps({'documents': len(reg['per_doc']), 'ruling_ids': reg['distinct_rulings'],"
        " 'total_references': reg['total_references'], 'corroborated': reg['corroborated'],"
        " 'sole_home': reg['sole_home']}, sort_keys=True))\n")
    result = subprocess.run(
        [sys.executable, "-c", script, str(root / "tests/guards/gate2/foundry_ruling_registry.py")],
        cwd=root, capture_output=True, text=True, check=True)
    return json.loads(result.stdout.strip().splitlines()[-1])


# ---------------------------------------------------------------------------
# The freeze itself
# ---------------------------------------------------------------------------


class TestTheFreezeManifest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = load_manifest()
        cls.tree = tracked(FREEZE_ROOT_REL)

    def test_the_real_manifest_satisfies_every_law(self):
        self.assertEqual(manifest_problems(self.doc, REPO_ROOT, self.tree), [])

    def test_the_serialization_is_canonical(self):
        self.assertEqual(MANIFEST.read_bytes(),
                         (json.dumps(self.doc, indent=2, sort_keys=True, ensure_ascii=False)
                          + "\n").encode("utf-8"))

    def test_the_freeze_root_is_the_layout_owner(self):
        self.assertEqual(PATHS.benchmarks_aq4, REPO_ROOT / FREEZE_ROOT_REL)

    def test_the_six_papers_left_the_registry_population(self):
        for name in MOVED_DOCS:
            with self.subTest(doc=name):
                self.assertFalse((REPO_ROOT / "docs" / name).exists())
                self.assertIn(f"{FREEZE_ROOT_REL}/docs/{name}",
                              [e["destination_path"] for e in self.doc["payload"]])

    def test_no_old_source_is_tracked(self):
        olds = [e["source_path"] for e in self.doc["payload"]]
        listed = tracked("experiments") + tracked("docs") + tracked("archive")
        self.assertEqual(sorted(set(olds) & set(listed)), [])
        self.assertEqual(tracked("experiments/aq4_benchmark"), [])

    def test_the_readme_states_the_pause_and_grants_nothing(self):
        text = (REPO_ROOT / README_REL).read_text(encoding="utf-8")
        for needle in ("**AQ4 is PAUSED.**", "Not production code", "Not a ratification",
                       "cohort-4.json", "cohort-5.json", "separate durable authorization"):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)


class TestTheManifestLawsCanFail(unittest.TestCase):
    """In-memory controls on a copy of the real manifest over a disposable tree."""

    def setUp(self):
        self.doc = load_manifest()
        self.tree = tracked(FREEZE_ROOT_REL)
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        for rel in self.tree:
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO_ROOT / rel, target)

    def red(self, needle, doc=None, tree=None):
        problems = manifest_problems(doc or self.doc, self.root, tree or self.tree)
        self.assertTrue(any(needle in p for p in problems), problems)

    def test_the_copy_is_green_before_any_control(self):
        self.assertEqual(manifest_problems(self.doc, self.root, self.tree), [])

    def test_CONTROL_one_destination_byte_flipped(self):
        target = self.root / self.doc["payload"][0]["destination_path"]
        data = bytearray(target.read_bytes())
        data[0] ^= 1
        target.write_bytes(bytes(data))
        self.red("bytes differ")

    def test_CONTROL_payload_entry_omitted(self):
        doc = json.loads(json.dumps(self.doc))
        doc["payload"].pop(3)
        self.red("tracked tree != manifest", doc=doc)

    def test_CONTROL_old_source_left_as_a_duplicate(self):
        entry = next(e for e in self.doc["payload"] if e["source_path"].startswith("docs/"))
        (self.root / "docs").mkdir(exist_ok=True)
        shutil.copyfile(self.root / entry["destination_path"], self.root / entry["source_path"])
        self.red("old source")

    def test_CONTROL_cohort_4_created(self):
        absent = self.root / self.doc["frozen_absences"][0]
        absent.write_text("{}\n", encoding="utf-8")
        self.red("frozen absence violated")

    def test_CONTROL_unmanifested_file_under_the_freeze_root(self):
        self.red("tracked tree != manifest",
                 tree=sorted(self.tree + [f"{FREEZE_ROOT_REL}/experiments/extra.py"]))

    def test_CONTROL_wrong_authorization_or_self_ratification(self):
        for key, value in (("freeze_authorization", "issue:1#issuecomment-1"),
                           ("this_manifest_ratifies", "AQ4"), ("status", "ACTIVE")):
            with self.subTest(key=key):
                doc = dict(self.doc, **{key: value})
                self.red(key, doc=doc)


# ---------------------------------------------------------------------------
# Frozen, not production
# ---------------------------------------------------------------------------


class TestFrozenIsNotProduction(unittest.TestCase):
    def test_every_frozen_python_file_is_aq4_paused(self):
        python = [Path(p) for p in tracked(FREEZE_ROOT_REL) if p.endswith(".py")]
        self.assertEqual(len(python), 6)
        for rel in python:
            with self.subTest(path=rel.as_posix()):
                self.assertEqual(layout_census.scope_of(rel), "aq4_PAUSED")
        self.assertNotIn("aq4_PAUSED", layout_census.LEGACY_PRODUCTION)

    def test_the_census_universe_walks_the_freeze_root(self):
        walked = {p.as_posix() for p in layout_census.walked_python(REPO_ROOT)}
        for rel in tracked(FREEZE_ROOT_REL):
            if rel.endswith(".py"):
                self.assertIn(rel, walked)

    def test_production_neither_imports_nor_names_frozen_aq4(self):
        self.assertEqual(production_references(REPO_ROOT / "src" / "mtj_foundry"), [])

    def test_CONTROL_a_production_reference_is_caught(self):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        pkg = root / "src" / "mtj_foundry"
        pkg.mkdir(parents=True)
        (pkg / "leak.py").write_text("import aq4_projection\nX = 'benchmarks/aq4/x'\n",
                                     encoding="utf-8")
        self.assertEqual(len(production_references(pkg)), 2)

    def test_the_aq4_conservation_invariant_is_still_deferred(self):
        contract = json.loads((PATHS.conservation / "CONSERVATION-CONTRACT.json")
                              .read_text(encoding="utf-8"))
        row = next(i for i in contract["invariants"]
                   if i["invariant_id"] == "AQ4_FROZEN_STATE_AND_GOVERNANCE")
        self.assertEqual(row["status"], "DEFERRED_WITH_REASON")
        self.assertIsNone(row["comparison_kind"])
        self.assertIsNone(row["extractor"])
        self.assertEqual(row["value_fields"], [])
        self.assertEqual(row["blocked_by_task_constraint"], "aq4: PAUSED, aq4_changes: 0")
        for side in contract["sides"]:
            self.assertNotIn("AQ4_FROZEN_STATE_AND_GOVERNANCE",
                             [b["invariant_id"] for b in side["bindings"]])


class TestTheLivePointerRoutesToTheFreeze(unittest.TestCase):
    def test_the_pointer_is_paused_and_routes_to_the_existing_frozen_contract(self):
        text = (REPO_ROOT / POINTER_REL).read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# AQ4 PAUSED — NOT CURRENT ROUTING"))
        self.assertIn("AQ4 is PAUSED", text)
        self.assertIn(f"`{FROZEN_CONTRACT_REL}`", text)
        self.assertNotIn(OLD_CONTRACT_REL, text)
        self.assertTrue((REPO_ROOT / FROZEN_CONTRACT_REL).is_file())
        self.assertFalse((REPO_ROOT / OLD_CONTRACT_REL).exists())


# ---------------------------------------------------------------------------
# The atomic ratchet transition
# ---------------------------------------------------------------------------


class TestTheRatchetTransitionIsAtomic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.live = json.loads(LIVE_BASELINE.read_text(encoding="utf-8"))
        cls.genesis = json.loads(GENESIS_SNAPSHOT.read_text(encoding="utf-8"))
        cls.succession = load_succession()

    def test_only_ruling_registry_differs_from_genesis(self):
        self.assertEqual(sorted(self.live), sorted(self.genesis))
        changed = sorted(k for k in self.live if self.live[k] != self.genesis[k])
        self.assertEqual(changed, ["ruling_registry"])

    def test_the_pinned_section_is_the_registry_measured_now(self):
        self.assertEqual(self.live["ruling_registry"], ruling_registry_metrics(REPO_ROOT))

    def test_the_s14_successor_is_exactly_justified(self):
        s14 = next(e for e in self.succession["entries"]
                   if e["authorization"] == FREEZE_AUTHORIZATION)
        self.assertEqual(s14["changed_sections"], ["ruling_registry"])
        self.assertEqual(s14["predecessor_sha256"],
                         self.succession["entries"][s14["ordinal"] - 1]["sha256"])
        self.assertIn("S14 AQ4 freeze relocation", s14["reason"])
        data = LIVE_BASELINE.read_bytes()
        if s14 is latest_entry(self.succession):
            self.assertEqual((s14["sha256"], s14["size_bytes"]),
                             (hashlib.sha256(data).hexdigest(), len(data)))


class TestDeletionSafetyIsStillLoadBearing(unittest.TestCase):
    """A synthetic sole-home paper must be BLOCKED by the registry's own rule."""

    def test_CONTROL_a_sole_home_paper_is_blocked_and_a_corroborated_one_is_safe(self):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        (root / "docs").mkdir()
        (root / "docs" / "SOLE.md").write_text("- **Q97** — synthetic ruling, sole home.\n"
                                               "- **Q98** — synthetic, corroborated.\n",
                                               encoding="utf-8")
        (root / "docs" / "OTHER.md").write_text("- **Q98** — synthetic, corroborated.\n",
                                                encoding="utf-8")
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull)
        for argv in (["init", "-q"], ["add", "docs"]):
            subprocess.run(["git", "-C", str(root)] + argv, check=True, capture_output=True, env=env)
        script = (
            "import importlib.util, json, sys\nfrom pathlib import Path\n"
            "spec = importlib.util.spec_from_file_location('rr', sys.argv[1])\n"
            "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
            "m.REPO_ROOT = Path(sys.argv[2]); m.DOCS = m.REPO_ROOT / 'docs'\n"
            "reg = m.build()\n"
            "print(json.dumps({k: v['deletion_blocked'] for k, v in reg['per_doc'].items()}))\n")
        result = subprocess.run(
            [sys.executable, "-c", script,
             str(REPO_ROOT / "tests/guards/gate2/foundry_ruling_registry.py"), str(root)],
            cwd=REPO_ROOT, capture_output=True, text=True, check=True)
        blocked = json.loads(result.stdout.strip().splitlines()[-1])
        self.assertEqual(blocked, {"OTHER.md": False, "SOLE.md": True})


if __name__ == "__main__":
    unittest.main()
