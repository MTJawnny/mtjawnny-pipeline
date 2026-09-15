"""S14.R2.R1 — the ratchet baseline has a genesis AND a succession.

Stdlib only, like the rest of this tree.

WHY THIS EXISTS
---------------
`config/baselines/foundry-audit-baseline.json` is the live acceptance control:
`mtj_foundry.infra.ratchet.compare(..., update=True)` exists so a reviewed change
can advance it, visibly, in a diff. But five migration-era guards pinned its bytes
to the P0.3A capture (`51fca151…`, 4324 B) as if it could never move. Those pins
were right for their slices — P0.3D/C8.5J were forbidden to change a value — and
wrong as a permanent law: the first authorized re-pin (S14's AQ4 freeze) turned
all five red. Rewriting the P0.3A capture record to absorb that would be
rewriting history.

So two truths are separated here and each gets its own witness:

1. GENESIS is immutable history. The P0.3A bytes are materialized at
   `refoundation/conservation/P0-3A-FOUNDRY-AUDIT-BASELINE.json`, must equal the
   capture record, and are what C7.7 (`RATCHET_BASELINE_BYTES`) now binds.
2. The LIVE control is selected by `RATCHET-BASELINE-SUCCESSION.json`: an ordered,
   predecessor-linked chain whose LATEST entry is the exact sha256/size the live
   baseline must have. A future reviewed update appends one entry; nothing
   rewrites genesis.

The record authorizes nothing. Every non-genesis entry must name the sections it
changed, a reason and an external durable authorization — a record that could
write its own successor would be the self-created authority C5 refuses.

Both history files the capture lives in are pinned byte-exact below: they are
records of what was measured, and a guard that let them be re-edited to agree with
new bytes would conserve nothing.

The validator is a pure function over a parsed document, so every chain rule has
an in-memory negative control; the physical rigs (flipping a real byte, rebinding
the real contract) are exercised against disposable copies.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT, block, scalars

from mtj_foundry.paths import ProjectPaths

PATHS = ProjectPaths.for_root(REPO_ROOT)

SCHEMA = "mtj-ratchet-baseline-succession/1"
LIVE_BASELINE_REL = "config/baselines/foundry-audit-baseline.json"
GENESIS_SNAPSHOT_REL = "refoundation/conservation/P0-3A-FOUNDRY-AUDIT-BASELINE.json"
SUCCESSION_REL = "refoundation/conservation/RATCHET-BASELINE-SUCCESSION.json"
CAPTURE_RECORD_REL = "refoundation/conservation/BASELINE-INPUTS.yaml"
CAPTURE_BLOCK = "ignored_ratchet_baseline"
OUTPUT_CENSUS_REL = "refoundation/conservation/OUTPUT-EXCEPTION-CENSUS.yaml"
CONTRACT_REL = "refoundation/conservation/CONSERVATION-CONTRACT.json"
IGNORED_SOURCE_REL = "experiments/out/foundry/audit-baseline.json"

LIVE_BASELINE = REPO_ROOT / LIVE_BASELINE_REL
GENESIS_SNAPSHOT = REPO_ROOT / GENESIS_SNAPSHOT_REL
SUCCESSION = REPO_ROOT / SUCCESSION_REL

# The P0.3A genesis identity. Stated independently of the capture record so the
# record and the snapshot are each checked against something they cannot edit.
GENESIS_SHA256 = "51fca1518813760108ac44cb553e4bd8c2bcff48a2312b9054b3af1f5ad07601"
GENESIS_SIZE = 4324

# History, pinned byte-exact. These are READ-ONLY measurement records; a later
# task that needs different numbers appends evidence elsewhere, it does not
# re-edit what P0.3A measured.
HISTORY_SHA256 = {
    CAPTURE_RECORD_REL: "8a4a1347779b92b3d7efbdb3f72badb5c8543ce3cd82c2e2c33c678385141029",
    OUTPUT_CENSUS_REL: "89a3f831ebce2001c1e5d809b389f081c957649c80e9b21daf9f9508237607e6",
}

ENTRY_FIELDS = ("authorization", "changed_sections", "ordinal", "predecessor_sha256",
                "reason", "sha256", "size_bytes")
TOP_FIELDS = ("authority", "entries", "genesis", "live_baseline_path", "schema")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_identity(path: Path) -> tuple[str, int]:
    data = path.read_bytes()
    return sha256_bytes(data), len(data)


def canonical_bytes(doc: dict) -> bytes:
    return (json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def load_succession(path: Path = SUCCESSION) -> dict:
    """Halts loudly on an unreadable or non-object record — never an empty chain."""
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise AssertionError(f"ratchet succession record unreadable at {path}: {exc}")
    if not isinstance(doc, dict):
        raise AssertionError(f"ratchet succession record at {path} is not a JSON object")
    return doc


def recorded_genesis(root: Path = REPO_ROOT) -> dict[str, str]:
    """The P0.3A capture, read from the unchanged history record."""
    return scalars(block((root / CAPTURE_RECORD_REL).read_text(encoding="utf-8"),
                         CAPTURE_BLOCK))


def census_ignored_source(root: Path = REPO_ROOT) -> dict[str, str]:
    """The output census's own measurement of the ignored ratchet source."""
    text = (root / OUTPUT_CENSUS_REL).read_text(encoding="utf-8")
    head = f"    - path: {IGNORED_SOURCE_REL}\n"
    body = text.split(head, 1)[1].split("\n    - path: ", 1)[0]
    return scalars(body)


def latest_entry(doc: dict) -> dict:
    return doc["entries"][-1]


def chain_problems(doc: dict) -> list[str]:
    """Every rule the record must satisfy, independent of any file on disk."""
    out: list[str] = []
    if sorted(doc) != sorted(TOP_FIELDS):
        out.append(f"top-level fields {sorted(doc)} != {sorted(TOP_FIELDS)}")
    if doc.get("schema") != SCHEMA:
        out.append(f"schema {doc.get('schema')!r} != {SCHEMA!r}")
    if doc.get("live_baseline_path") != LIVE_BASELINE_REL:
        out.append(f"live_baseline_path {doc.get('live_baseline_path')!r}")
    genesis = doc.get("genesis")
    if genesis != {"capture_record_path": CAPTURE_RECORD_REL,
                   "capture_record_block": CAPTURE_BLOCK,
                   "snapshot_path": GENESIS_SNAPSHOT_REL}:
        out.append(f"genesis provenance {genesis!r}")
    if doc.get("authority") != {"this_record_ratifies": "NOTHING",
                                "successor_authorized_by": "EXTERNAL_DURABLE_TASK_ONLY"}:
        out.append(f"authority {doc.get('authority')!r}")
    entries = doc.get("entries")
    if not isinstance(entries, list) or not entries:
        return out + ["entries must be a non-empty list"]

    seen: set[str] = set()
    for index, entry in enumerate(entries):
        where = f"entry[{index}]"
        if not isinstance(entry, dict):
            out.append(f"{where} is not an object")
            continue
        if sorted(entry) != sorted(ENTRY_FIELDS):
            out.append(f"{where} fields {sorted(entry)} != {sorted(ENTRY_FIELDS)}")
            continue
        if type(entry["ordinal"]) is not int or entry["ordinal"] != index:
            out.append(f"{where} ordinal {entry['ordinal']!r} != {index}")
        sha = entry["sha256"]
        if not isinstance(sha, str) or not _SHA256.match(sha):
            out.append(f"{where} sha256 malformed: {sha!r}")
        elif sha in seen:
            out.append(f"{where} duplicates digest {sha}")
        else:
            seen.add(sha)
        size = entry["size_bytes"]
        if type(size) is not int or size <= 0:
            out.append(f"{where} size_bytes must be a positive int: {size!r}")
        sections = entry["changed_sections"]
        if (not isinstance(sections, list)
                or not all(isinstance(s, str) and s for s in sections)
                or len(set(sections)) != len(sections)):
            out.append(f"{where} changed_sections malformed: {sections!r}")
            sections = None
        for field in ("reason", "authorization"):
            if not isinstance(entry[field], str) or not entry[field].strip():
                out.append(f"{where} {field} must be non-empty")
        if index == 0:
            if entry["predecessor_sha256"] is not None:
                out.append("genesis predecessor_sha256 must be null")
            if sections:
                out.append("genesis changed_sections must be empty")
            if (entry["sha256"], entry["size_bytes"]) != (GENESIS_SHA256, GENESIS_SIZE):
                out.append("genesis identity is not the P0.3A capture")
            if isinstance(entry["reason"], str) and "P0.3A" not in entry["reason"]:
                out.append("genesis reason does not name its P0.3A provenance")
        else:
            previous = entries[index - 1]
            if (not isinstance(previous, dict)
                    or entry["predecessor_sha256"] != previous.get("sha256")):
                out.append(f"{where} predecessor does not link to entry[{index - 1}]")
            if sections is not None and not sections:
                out.append(f"{where} names no changed_section")
    return out


def live_problems(doc: dict, live: Path) -> list[str]:
    """The live control must be exactly what the latest entry selects."""
    if not doc.get("entries") or not isinstance(doc["entries"][-1], dict):
        return ["no latest entry to select the live baseline"]
    sha, size = file_identity(live)
    latest = latest_entry(doc)
    if (sha, size) != (latest.get("sha256"), latest.get("size_bytes")):
        return [f"live baseline {sha}/{size} is not the latest succession entry "
                f"{latest.get('sha256')}/{latest.get('size_bytes')}"]
    return []


def c77_binding_problems(contract: dict) -> list[str]:
    """C7.7 must witness immutable genesis, never the mutable live control."""
    out = []
    row = next(i for i in contract["invariants"]
               if i["invariant_id"] == "RATCHET_BASELINE_BYTES")
    if (row["status"], row["comparison_kind"], row["extractor"]) != (
            "ACTIVE_MECHANICAL", "EXACT_BYTES", "exact_file_bytes"):
        out.append(f"C7.7 shape changed: {row['status']}/{row['comparison_kind']}/{row['extractor']}")
    if row["value_fields"] != [{"name": "sha256", "type": "sha256"},
                               {"name": "size_bytes", "type": "byte_size"}]:
        out.append("C7.7 value fields changed")
    bindings = {side["side_id"]: {b["invariant_id"]: b["source_path"] for b in side["bindings"]}
                for side in contract["sides"]}
    if bindings["LEGACY_LOCAL"]["RATCHET_BASELINE_BYTES"] != IGNORED_SOURCE_REL:
        out.append("C7.7 legacy side no longer binds the P0.3A ignored source")
    refoundation = bindings["REFOUNDATION_TRACKED"]["RATCHET_BASELINE_BYTES"]
    if refoundation == LIVE_BASELINE_REL:
        out.append("C7.7 refoundation side binds the MUTABLE live baseline")
    elif refoundation != GENESIS_SNAPSHOT_REL:
        out.append(f"C7.7 refoundation side binds {refoundation!r}, not the genesis snapshot")
    if contract["authority"]["this_document_ratifies"] != "NOTHING":
        out.append("contract claims to ratify something")
    return out


def successor_entry(doc: dict, data: bytes, **overrides) -> dict:
    """A well-formed successor for `data`, for controls. Nothing real uses it."""
    entry = {"ordinal": len(doc["entries"]), "sha256": sha256_bytes(data),
             "size_bytes": len(data), "predecessor_sha256": latest_entry(doc)["sha256"],
             "changed_sections": ["ruling_registry"], "reason": "control",
             "authorization": "control-only"}
    entry.update(overrides)
    return entry


# ---------------------------------------------------------------------------
# Genesis is immutable history
# ---------------------------------------------------------------------------


class TestTheGenesisSnapshotIsTheP03ACapture(unittest.TestCase):
    def test_the_snapshot_has_the_genesis_identity(self):
        self.assertEqual(file_identity(GENESIS_SNAPSHOT), (GENESIS_SHA256, GENESIS_SIZE))

    def test_the_snapshot_agrees_with_the_unchanged_capture_record(self):
        recorded = recorded_genesis()
        sha, size = file_identity(GENESIS_SNAPSHOT)
        self.assertEqual(sha, recorded["source_sha256"])
        self.assertEqual(sha, recorded["tracked_copy_sha256"])
        self.assertEqual(size, int(recorded["source_size_bytes"]))
        self.assertEqual(recorded["byte_identical"], "true")

    def test_the_snapshot_agrees_with_the_output_census_measurement(self):
        measured = census_ignored_source()
        sha, size = file_identity(GENESIS_SNAPSHOT)
        self.assertEqual(sha, measured["sha256_measured"])
        self.assertEqual(size, int(measured["size_bytes"]))

    def test_the_history_records_are_byte_identical(self):
        for rel, expected in HISTORY_SHA256.items():
            with self.subTest(path=rel):
                self.assertEqual(sha256_bytes((REPO_ROOT / rel).read_bytes()), expected)

    def test_the_snapshot_is_not_the_live_control_and_nothing_reads_it_as_one(self):
        """Evidence, never an input: no production, legacy or Gate-2 code names it."""
        self.assertNotEqual(PATHS.foundry_audit_baseline, GENESIS_SNAPSHOT)
        listed = subprocess.run(["git", "-C", str(REPO_ROOT), "ls-files", "-z", "*.py"],
                                capture_output=True, check=True).stdout.decode().split("\0")
        readers = [p for p in listed
                   if p and p.startswith(("src/", "experiments/", "pipeline/", "tests/guards/"))
                   and (REPO_ROOT / p).exists()
                   and Path(GENESIS_SNAPSHOT_REL).name in (REPO_ROOT / p).read_text(encoding="utf-8")]
        self.assertEqual(readers, [])

    def test_the_conservation_root_stays_flat(self):
        """`test_output_census` reads every direct child as text. A subdirectory here
        is an IsADirectoryError there — measured in S14.R2 — so flatness is law."""
        self.assertEqual([p.name for p in PATHS.conservation.iterdir() if p.is_dir()], [])


# ---------------------------------------------------------------------------
# The succession record
# ---------------------------------------------------------------------------


class TestTheSuccessionRecord(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = load_succession()

    def test_the_record_satisfies_every_chain_rule(self):
        self.assertEqual(chain_problems(self.doc), [])

    def test_the_live_baseline_is_exactly_the_latest_entry(self):
        self.assertEqual(live_problems(self.doc, LIVE_BASELINE), [])

    def test_the_serialization_is_canonical(self):
        self.assertEqual(SUCCESSION.read_bytes(), canonical_bytes(self.doc))

    def test_genesis_opens_the_chain(self):
        genesis = self.doc["entries"][0]
        self.assertEqual((genesis["sha256"], genesis["size_bytes"]),
                         file_identity(GENESIS_SNAPSHOT))
        self.assertEqual(genesis["changed_sections"], [])
        self.assertIsNone(genesis["predecessor_sha256"])

    def test_a_live_baseline_at_genesis_implies_a_genesis_only_chain(self):
        """Derived, not pinned: digests are unique and the latest selects the live
        bytes, so while live == genesis the chain cannot hold anything else."""
        if file_identity(LIVE_BASELINE) == (GENESIS_SHA256, GENESIS_SIZE):
            self.assertEqual(len(self.doc["entries"]), 1)

    def test_the_record_ratifies_nothing(self):
        self.assertEqual(self.doc["authority"]["this_record_ratifies"], "NOTHING")
        self.assertEqual(self.doc["authority"]["successor_authorized_by"],
                         "EXTERNAL_DURABLE_TASK_ONLY")

    def test_the_record_carries_no_card_data(self):
        text = SUCCESSION.read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-", text))


class TestTheChainRulesCanFail(unittest.TestCase):
    """One control per rule, each on a deep copy of the REAL record."""

    @classmethod
    def setUpClass(cls):
        cls.real = load_succession()

    def variant(self, mutate) -> dict:
        doc = copy.deepcopy(self.real)
        mutate(doc)
        return doc

    def assertRed(self, doc, needle):
        problems = chain_problems(doc)
        self.assertTrue(any(needle in p for p in problems), problems)

    def test_CONTROL_changed_genesis_digest(self):
        self.assertRed(self.variant(lambda d: d["entries"][0].update(sha256="0" * 64)),
                       "genesis identity")

    def test_CONTROL_changed_genesis_size(self):
        self.assertRed(self.variant(lambda d: d["entries"][0].update(size_bytes=4325)),
                       "genesis identity")

    def test_CONTROL_genesis_with_a_predecessor(self):
        self.assertRed(self.variant(lambda d: d["entries"][0].update(predecessor_sha256="a" * 64)),
                       "genesis predecessor")

    def test_CONTROL_genesis_claiming_changed_sections(self):
        self.assertRed(self.variant(lambda d: d["entries"][0].update(changed_sections=["x"])),
                       "genesis changed_sections")

    def test_CONTROL_wrong_predecessor(self):
        def mutate(d):
            d["entries"].append(successor_entry(d, b"{}\n", predecessor_sha256="b" * 64))
        self.assertRed(self.variant(mutate), "predecessor does not link")

    def test_CONTROL_duplicate_entry(self):
        self.assertRed(self.variant(lambda d: d["entries"].append(
            dict(copy.deepcopy(d["entries"][0]), ordinal=1))), "duplicates digest")

    def test_CONTROL_reordered_entries(self):
        def mutate(d):
            d["entries"].append(successor_entry(d, b"{}\n"))
            d["entries"].reverse()
        self.assertRed(self.variant(mutate), "ordinal")

    def test_CONTROL_ordinal_gap(self):
        def mutate(d):
            d["entries"].append(successor_entry(d, b"{}\n", ordinal=len(d["entries"]) + 1))
        self.assertRed(self.variant(mutate), "ordinal")

    def test_CONTROL_successor_without_changed_sections(self):
        self.assertRed(self.variant(lambda d: d["entries"].append(
            successor_entry(d, b"{}\n", changed_sections=[]))), "names no changed_section")

    def test_CONTROL_successor_without_reason(self):
        self.assertRed(self.variant(lambda d: d["entries"].append(
            successor_entry(d, b"{}\n", reason="  "))), "reason must be non-empty")

    def test_CONTROL_successor_without_authorization(self):
        self.assertRed(self.variant(lambda d: d["entries"].append(
            successor_entry(d, b"{}\n", authorization=""))), "authorization must be non-empty")

    def test_CONTROL_missing_field(self):
        self.assertRed(self.variant(lambda d: d["entries"][0].pop("reason")), "fields")

    def test_CONTROL_malformed_digest_and_boolean_size(self):
        def mutate(d):
            d["entries"].append(successor_entry(d, b"{}\n", sha256="A" * 64, size_bytes=True))
        problems = chain_problems(self.variant(mutate))
        self.assertTrue(any("sha256 malformed" in p for p in problems), problems)
        self.assertTrue(any("positive int" in p for p in problems), problems)

    def test_CONTROL_self_ratifying_record(self):
        self.assertRed(self.variant(lambda d: d["authority"].update(this_record_ratifies="S14")),
                       "authority")

    def test_CONTROL_empty_chain(self):
        self.assertRed(self.variant(lambda d: d.update(entries=[])), "non-empty")


class TestTheLiveMatchCanFail(unittest.TestCase):
    def setUp(self):
        self.doc = load_succession()
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.live = tmp / "foundry-audit-baseline.json"
        shutil.copyfile(LIVE_BASELINE, self.live)

    def test_the_copy_matches_before_any_control(self):
        self.assertEqual(live_problems(self.doc, self.live), [])

    def test_CONTROL_fake_successor_while_live_stays_at_genesis(self):
        doc = copy.deepcopy(self.doc)
        doc["entries"].append(successor_entry(doc, b"{}\n"))
        self.assertEqual(chain_problems(doc), [])
        self.assertTrue(live_problems(doc, self.live))

    def test_CONTROL_live_mutated_without_a_successor(self):
        self.live.write_bytes(self.live.read_bytes() + b" ")
        self.assertTrue(live_problems(self.doc, self.live))

    def test_CONTROL_live_matches_a_successor_that_omits_its_justification(self):
        """The live match alone must not launder an unjustified successor."""
        data = self.live.read_bytes() + b" "
        self.live.write_bytes(data)
        for field, empty in (("changed_sections", []), ("reason", ""), ("authorization", "")):
            with self.subTest(field=field):
                doc = copy.deepcopy(self.doc)
                doc["entries"].append(successor_entry(doc, data, **{field: empty}))
                self.assertEqual(live_problems(doc, self.live), [])
                self.assertTrue(chain_problems(doc))

    def test_a_justified_successor_is_accepted(self):
        """The positive arm: the mechanism really can advance the live control."""
        data = self.live.read_bytes() + b" "
        self.live.write_bytes(data)
        doc = copy.deepcopy(self.doc)
        doc["entries"].append(successor_entry(doc, data))
        self.assertEqual(chain_problems(doc) + live_problems(doc, self.live), [])


# ---------------------------------------------------------------------------
# C7.7 witnesses genesis
# ---------------------------------------------------------------------------


class TestC77BindsTheImmutableGenesis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads((REPO_ROOT / CONTRACT_REL).read_text(encoding="utf-8"))

    def test_the_real_contract_binds_genesis(self):
        self.assertEqual(c77_binding_problems(self.contract), [])

    def test_CONTROL_rebinding_to_the_live_baseline_is_caught(self):
        doc = copy.deepcopy(self.contract)
        side = next(s for s in doc["sides"] if s["side_id"] == "REFOUNDATION_TRACKED")
        next(b for b in side["bindings"]
             if b["invariant_id"] == "RATCHET_BASELINE_BYTES")["source_path"] = LIVE_BASELINE_REL
        problems = c77_binding_problems(doc)
        self.assertTrue(any("MUTABLE live baseline" in p for p in problems), problems)

    def test_CONTROL_semantic_comparator_swap_is_caught(self):
        doc = copy.deepcopy(self.contract)
        next(i for i in doc["invariants"]
             if i["invariant_id"] == "RATCHET_BASELINE_BYTES")["comparison_kind"] = "EXACT_VALUE"
        self.assertTrue(c77_binding_problems(doc))


if __name__ == "__main__":
    unittest.main()
