"""C03b unit tests: the trace renderer, --verify and --check-complete, with both
negative controls (a record missing its owning occurrence halts; a dropped
trace or an outcome mismatch fails --check-complete) and a stale kill.json;
exact fixture coverage (unrelated trace keys, incorrect member identities,
duplicate fixture roles and entries are refused) and a null population census
key reported as malformed, never a TypeError; a malformed C03 census key (e.g.
['exile']) halts the renderer with its diagnostic, never an IndexError.
interface/3 §I3a R4: every R4 label and every value R4 changed is rendered
beside its interface/2 value, and --check-complete fails on a trace that drops
one R4 label or one R4-changed outcome (or misstates or duplicates one).

Inline SYNTHETIC clauses only -- generic templating, no card, no card name, no
oracle_id and no Oracle text. Never reads or writes c03/ or c03b/ output.

    python3 -m unittest discover -s tests/oracle_ingest -t .
"""
import contextlib
import copy
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "oracle_ingest"))

import c03_trace as ct           # noqa: E402
import h_region as hr            # noqa: E402
import h_region_kill as hk       # noqa: E402

KILL, UNRESOLVED, PASS = hk.KILL, hk.UNRESOLVED, hk.PASS
NAMES = ["Synthetic Widget"]

TWO = "Exile target artifact you control, then return that card to the battlefield."
TWO_HEADS = "Destroy target artifact, then proliferate."
TRIGGER = ("When this widget enters, exile target artifact, then return it to the "
           "battlefield.")
NO_HEAD = "Put target artifact on top of its owner's library."


def docs():
    """(regions_doc, kill_doc): three population clauses and one fixture clause."""
    a = hk._rig(TWO, census=("exile", 0), population=True)
    b = hk._rig(TRIGGER, census=("exile", 1), population=True, ci=1)
    c = hk._rig(TWO_HEADS, census=("destroy", 0), population=True, ci=2)
    d = hk._rig(NO_HEAD, roles=["synthetic-role"], ci=3)
    recs = [a, b, c, d]
    return ct.rig_docs(
        recs, [["rig", "exile", 0], ["rig", "exile", 1], ["rig", "destroy", 0]],
        [{"role": "synthetic-role", "member_status": "synthetic",
          "members": [{"oracle_id": "rig", "census_key": None,
                       "clauses": [d["address"]["id"]]}]}], NAMES)


def halts(fn):
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            fn()
    except SystemExit:
        return True
    return False


class Renderer(unittest.TestCase):
    def setUp(self):
        self.regions, self.kill = docs()
        self.doc = ct.render_traces(self.regions, self.kill)

    def test_one_trace_per_record_in_order(self):
        keys = [t["key"] for t in self.doc["traces"]]
        self.assertEqual(keys, [[c["address"]["id"], c["census_key"]]
                                for c in self.regions["clauses"]])

    def test_owning_occurrence_is_four_coordinates(self):
        t = self.doc["traces"][1]
        self.assertEqual(t["occurrence"], {"oracle_id": "rig", "face": 0, "paragraph": 0,
                                           "clause": 1, "id": "rig:0:0:1"})

    def test_regions_carry_spans_and_their_excerpt(self):
        rec, t = self.regions["clauses"][0], self.doc["traces"][0]
        self.assertEqual([r["head"] for r in t["regions"]], ["exile", "return"])
        for got, want in zip(t["regions"], rec["regions"]):
            self.assertEqual(got["span"], want["span"])
            self.assertEqual(got["head_span"], want["head_span"])
            self.assertEqual(got["text"], TWO[want["span"][0]:want["span"][1]])
        line = next(x for x in t["lines"] if x.startswith("  region 0"))
        a, b = t["regions"][0]["span"]
        self.assertIn(f"span [{a}, {b})", line)

    def test_role_marks_copied_with_attachment(self):
        t = self.doc["traces"][1]
        r1 = [m for m in t["role_marks"] if m["r1_shape"]]
        self.assertEqual([(m["role"], m["r1_shape"], m["outcome"]) for m in r1],
                         [("condition", "condition-trigger", "attached")])
        self.assertTrue(any("R1 condition-trigger" in x for x in t["lines"]))

    def test_every_kill_outcome_copied(self):
        for t, row in zip(self.doc["traces"], self.kill["clauses"]):
            for k in hk.CONDITIONS:
                self.assertEqual(t["tests"][k]["outcome"], row["tests"][k]["outcome"])
                self.assertEqual(t["tests"][k]["relevant"], row["tests"][k]["relevant"])
                self.assertTrue(any(x.startswith(f"  {k} {row['tests'][k]['outcome']}")
                                    for x in t["lines"]))

    def test_clause_without_region_is_shown_as_none(self):
        self.assertIn("  region: none derived", self.doc["traces"][3]["lines"])

    def test_fixture_index_points_at_its_trace(self):
        f = self.doc["fixtures"][0]
        self.assertEqual(f["members"][0]["traces"], [["rig:0:0:3", None]])

    def test_renderer_does_not_mutate_its_inputs(self):
        before = copy.deepcopy((self.regions, self.kill))
        ct.render_traces(self.regions, self.kill)
        self.assertEqual((self.regions, self.kill), before)

    def test_rendered_bytes_are_portable(self):
        self.assertEqual(hr.portability_violations(ct.render(self.doc)), [])


class OwningOccurrence(unittest.TestCase):
    """Negative control: a C03 record missing its owning occurrence halts."""

    def rigged(self, edit):
        regions, kill = docs()
        edit(regions["clauses"][0])
        return halts(lambda: ct.render_traces(regions, kill))

    def test_unrigged_does_not_halt(self):
        self.assertFalse(self.rigged(lambda c: None))

    def test_missing_address_halts(self):
        self.assertTrue(self.rigged(lambda c: c.pop("address")))

    def test_missing_each_coordinate_halts(self):
        for k in ct.COORDS + ("id",):
            with self.subTest(coordinate=k):
                self.assertTrue(self.rigged(lambda c, k=k: c["address"].pop(k)))

    def test_malformed_coordinate_halts(self):
        for k, v in (("face", True), ("face", "0"), ("paragraph", -1),
                     ("clause", 1.0), ("oracle_id", ""), ("oracle_id", 0), ("id", 0)):
            with self.subTest(coordinate=k, value=v):
                self.assertTrue(self.rigged(lambda c, k=k, v=v: c["address"].update({k: v})))

    def test_clause_text_not_its_hash_halts(self):
        self.assertTrue(self.rigged(lambda c: c.update(clause_text=c["clause_text"] + " ")))

    def test_unreadable_record_halts_not_crashes(self):
        for field in ("regions", "role_spans", "clause_text", "scope"):
            with self.subTest(field=field):
                self.assertTrue(self.rigged(lambda c, f=field: c.pop(f)))

    def test_id_not_its_coordinates_halts(self):
        self.assertTrue(self.rigged(lambda c: c["address"].update(id="rig:0:0:9")))

    def test_region_owned_elsewhere_halts(self):
        self.assertTrue(self.rigged(lambda c: c["regions"][0].update(owner="rig:0:0:9")))

    def test_kill_row_of_another_clause_halts(self):
        regions, kill = docs()
        kill["clauses"][0], kill["clauses"][1] = kill["clauses"][1], kill["clauses"][0]
        self.assertTrue(halts(lambda: ct.render_traces(regions, kill)))

    def test_missing_kill_row_halts(self):
        regions, kill = docs()
        kill["clauses"].pop()
        self.assertTrue(halts(lambda: ct.render_traces(regions, kill)))


class CheckComplete(unittest.TestCase):
    """Negative control: --check-complete fails on a dropped trace and on an
    outcome mismatch."""

    def setUp(self):
        self.regions, self.kill = docs()
        self.doc = ct.render_traces(self.regions, self.kill)

    def failures(self, doc):
        return ct.completeness_failures(doc, self.regions, self.kill)

    def test_clean_is_complete(self):
        self.assertEqual(self.failures(self.doc), [])

    def test_counts_recomputed_equal_kill(self):
        counts = ct.outcome_counts(self.doc["traces"])
        for k in hk.CONDITIONS:
            for o in ct.OUTCOMES:
                self.assertEqual(counts[k]["all"][o],
                                 self.kill["conditions"][k]["all"][o]["count"])
                self.assertEqual(counts[k]["relevant"][o],
                                 self.kill["conditions"][k]["relevant"][o]["count"])

    def test_each_dropped_trace_fails(self):
        for i in range(len(self.doc["traces"])):
            with self.subTest(dropped=i):
                doc = copy.deepcopy(self.doc)
                gone = doc["traces"].pop(i)
                bad = self.failures(doc)
                self.assertTrue(any(json.dumps(gone["key"]) in b for b in bad), bad)

    def test_duplicated_trace_fails(self):
        doc = copy.deepcopy(self.doc)
        doc["traces"].append(copy.deepcopy(doc["traces"][0]))
        self.assertTrue(any(b.startswith("2 traces for") for b in self.failures(doc)))

    def test_foreign_trace_fails(self):
        doc = copy.deepcopy(self.doc)
        doc["traces"][3]["key"] = ["rig:0:0:9", None]           # the fixture trace
        bad = self.failures(doc)
        self.assertIn('trace ["rig:0:0:9", null] is not a C03 clause', bad)
        self.assertIn('no trace for C03 clause ["rig:0:0:3", null]', bad)

    def test_each_outcome_mismatch_fails(self):
        for k in hk.CONDITIONS:
            with self.subTest(condition=k):
                doc = copy.deepcopy(self.doc)
                t = doc["traces"][0]["tests"][k]
                t["outcome"] = KILL if t["outcome"] != KILL else PASS
                self.assertTrue(any(b.startswith(f"{k} all") for b in self.failures(doc)))

    def test_relevance_mismatch_fails(self):
        doc = copy.deepcopy(self.doc)
        t = next(t for t in doc["traces"] if not t["fixture_roles"]
                 and not t["tests"]["K5"]["relevant"])
        t["tests"]["K5"]["relevant"] = True
        self.assertTrue(any(b.startswith("K5 relevant") for b in self.failures(doc)))

    def test_missing_fixture_entry_fails(self):
        doc = copy.deepcopy(self.doc)
        doc["fixtures"] = []
        self.assertTrue(any("fixture synthetic-role" in b for b in self.failures(doc)))

    def test_cli_exit_codes(self):
        """--check-complete exits 0 on a complete trace and 1 on a dropped one,
        with the producers and --verify stubbed and a temporary root."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for rel, body in ((ct.REGIONS_REL, self.regions), (ct.KILL_REL, self.kill)):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text(json.dumps(body))
            out = root / ct.OUT_REL
            out.parent.mkdir(parents=True, exist_ok=True)
            dropped = copy.deepcopy(self.doc)
            dropped["traces"].pop()
            for doc, want in ((self.doc, 0), (dropped, 1)):
                out.write_text(json.dumps(doc))
                with mock.patch.object(ct, "ROOT", root), \
                        mock.patch.object(ct, "OUT", out), \
                        mock.patch.object(ct, "verify", return_value=0), \
                        mock.patch.object(ct, "ensure_inputs"), \
                        contextlib.redirect_stdout(io.StringIO()), \
                        contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(ct.check_complete(), want)

    def _order(self, out_exists, ensure=None):
        """check_complete's hand-off calls, in order, with every effect stubbed."""
        calls = []
        ensure = ensure or (lambda: calls.append("ensure_inputs"))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for rel, body in ((ct.REGIONS_REL, self.regions), (ct.KILL_REL, self.kill)):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text(json.dumps(body))
            out = root / ct.OUT_REL
            out.parent.mkdir(parents=True, exist_ok=True)
            if out_exists:
                out.write_text(json.dumps(self.doc))

            def regenerate(argv):
                calls.append("regenerate")
                out.write_text(json.dumps(self.doc))
                return 0
            with mock.patch.object(ct, "ROOT", root), \
                    mock.patch.object(ct, "OUT", out), \
                    mock.patch.object(ct, "ensure_inputs", side_effect=ensure), \
                    mock.patch.object(ct, "verify",
                                      side_effect=lambda: calls.append("verify") or 0), \
                    mock.patch.object(ct, "main", side_effect=regenerate), \
                    contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                try:
                    rc = ct.check_complete()
                except SystemExit:
                    rc = "halt"
        return calls, rc

    def test_inputs_checked_before_existing_trace_is_verified(self):
        self.assertEqual(self._order(True), (["ensure_inputs", "verify"], 0))

    def test_inputs_checked_before_missing_trace_is_regenerated(self):
        self.assertEqual(self._order(False), (["ensure_inputs", "regenerate"], 0))

    def test_stale_input_stops_before_the_trace_is_touched(self):
        def stale():
            raise SystemExit("stale C03 input")
        calls, rc = self._order(True, ensure=stale)
        self.assertEqual((calls, rc), ([], "halt"))


class Verify(unittest.TestCase):
    """--verify recomputes regions.json, kill.json and script hashes."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for rel, body in ((ct.REGIONS_REL, b"{}\n"), (ct.KILL_REL, b"{}\n"),
                          (ct.SCRIPT, b"# synthetic\n")):
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.root / rel).write_bytes(body)
        self.doc = {"inputs": {r: ct._sha_at(self.root, r)
                               for r in (ct.REGIONS_REL, ct.KILL_REL)},
                    "script": {"path": ct.SCRIPT,
                               "sha256": ct._sha_at(self.root, ct.SCRIPT)}}

    def tearDown(self):
        self.tmp.cleanup()

    def test_fresh_is_current(self):
        self.assertEqual(ct.stale_inputs(self.doc, self.root), [])

    def test_stale_kill_json(self):
        (self.root / ct.KILL_REL).write_bytes(b'{"rigged": true}\n')
        self.assertEqual(ct.stale_inputs(self.doc, self.root), [ct.KILL_REL])

    def test_stale_regions_and_script(self):
        (self.root / ct.REGIONS_REL).write_bytes(b"[]\n")
        (self.root / ct.SCRIPT).write_bytes(b"# rigged\n")
        self.assertEqual(ct.stale_inputs(self.doc, self.root),
                         sorted([ct.REGIONS_REL, ct.SCRIPT]))

    def test_missing_input_is_stale(self):
        (self.root / ct.KILL_REL).unlink()
        self.assertEqual(ct.stale_inputs(self.doc, self.root), [ct.KILL_REL])

    def test_unembedded_input_is_stale(self):
        del self.doc["inputs"][ct.KILL_REL]
        self.assertEqual(ct.stale_inputs(self.doc, self.root),
                         [f"{ct.KILL_REL} is not embedded"])

    def write_trace(self, doc=None):
        out = self.root / ct.OUT_REL
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(doc or self.doc))
        return out

    def run_verify(self, *args, producers=()):
        with mock.patch.object(ct, "stale_producers", return_value=list(producers)), \
                contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()) as err:
            rc = ct.verify(*args)
        return rc, err.getvalue().splitlines()

    def test_cli_exits_nonzero_on_stale_kill_hash(self):
        out = self.root / "trace.json"
        doc = dict(self.doc, inputs=dict(self.doc["inputs"], **{ct.KILL_REL: "0" * 64}))
        out.write_text(json.dumps(doc))
        with mock.patch.object(ct, "OUT", out):
            rc, err = self.run_verify()
        self.assertEqual(rc, 1)
        self.assertIn(f"STALE: {ct.KILL_REL}", err)

    def test_cli_exits_nonzero_when_trace_missing(self):
        with mock.patch.object(ct, "OUT", self.root / "absent.json"):
            self.assertEqual(self.run_verify()[0], 1)

    def test_verify_on_a_root_rigged_stale_kill_json(self):
        """Negative control through verify() itself: current, then stale."""
        self.write_trace()
        self.assertEqual(self.run_verify(self.root), (0, []))
        (self.root / ct.KILL_REL).write_bytes(b'{"rigged": true}\n')
        self.assertEqual(self.run_verify(self.root), (1, [f"STALE: {ct.KILL_REL}"]))

    def test_default_root_is_resolved_when_called(self):
        out = self.write_trace()
        with mock.patch.object(ct, "ROOT", self.root), mock.patch.object(ct, "OUT", out):
            self.assertEqual(ct.stale_inputs(self.doc), [])
            self.assertEqual(self.run_verify(), (0, []))
            (self.root / ct.KILL_REL).write_bytes(b'{"rigged": true}\n')
            self.assertEqual(ct.stale_inputs(self.doc), [ct.KILL_REL])
            self.assertEqual(self.run_verify()[0], 1)

    def test_verify_fails_when_a_producer_reports_stale(self):
        out = self.write_trace()
        with mock.patch.object(ct, "ROOT", self.root), mock.patch.object(ct, "OUT", out):
            rc, err = self.run_verify(producers=[f"{ct.KILL_REL} (rigged)"])
        self.assertEqual((rc, err), (1, [f"STALE: {ct.KILL_REL} (rigged)"]))

    def test_rigged_root_never_runs_the_real_producers(self):
        self.write_trace()
        with mock.patch.object(ct, "stale_producers") as sp, \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(ct.verify(self.root), 0)
        sp.assert_not_called()


def fixture_docs():
    """(regions_doc, kill_doc) with two fixtures: `synthetic-role` has one
    member of two chain clauses (d, e); `keyed-role` has one census-keyed
    member whose clause is also a population clause (c)."""
    a = hk._rig(TWO, census=("exile", 0), population=True)
    b = hk._rig(TRIGGER, census=("exile", 1), population=True, ci=1)
    c = hk._rig(TWO_HEADS, census=("destroy", 0), population=True, roles=["keyed-role"],
                ci=2)
    d = hk._rig(NO_HEAD, roles=["synthetic-role"], ci=3)
    e = hk._rig(TWO, roles=["synthetic-role"], ci=4)
    recs = [a, b, c, d, e]
    return ct.rig_docs(
        recs, [["rig", "exile", 0], ["rig", "exile", 1], ["rig", "destroy", 0]],
        [{"role": "synthetic-role", "member_status": "synthetic",
          "members": [{"oracle_id": "rig", "census_key": None,
                       "clauses": [d["address"]["id"], e["address"]["id"]]}]},
         {"role": "keyed-role", "member_status": "synthetic",
          "members": [{"oracle_id": "rig", "census_key": ["destroy", 0],
                       "clauses": [c["address"]["id"]]}]}], NAMES)


class FixtureCoverage(unittest.TestCase):
    """--check-complete validates EXACT fixture coverage: each fixture once,
    each member's identity, and exactly its expected trace keys."""

    def setUp(self):
        self.regions, self.kill = fixture_docs()
        self.doc = ct.render_traces(self.regions, self.kill)

    def failures(self, doc):
        return ct.completeness_failures(doc, self.regions, self.kill)

    def rigged(self, edit):
        doc = copy.deepcopy(self.doc)
        edit(doc)
        return self.failures(doc)

    def member(self, doc, role="synthetic-role"):
        return next(f for f in doc["fixtures"] if f["role"] == role)["members"][0]

    def test_clean_is_complete(self):
        self.assertEqual(self.failures(self.doc), [])

    def test_expected_keys_derived_from_c03(self):
        self.assertEqual(self.member(self.doc)["traces"],
                         [["rig:0:0:3", None], ["rig:0:0:4", None]])
        self.assertEqual(self.member(self.doc, "keyed-role")["traces"],
                         [["rig:0:0:2", ["destroy", 0]]])

    # ------------------------------------------------- unrelated trace keys
    def test_unrelated_existing_trace_key_fails(self):
        """A real trace of the same card, but not the member's clause."""
        bad = self.rigged(lambda d: self.member(d)["traces"].__setitem__(
            0, ["rig:0:0:0", ["exile", 0]]))
        self.assertIn('fixture synthetic-role member 0: trace ["rig:0:0:0", ["exile", 0]] '
                      "is not one of the member's clauses", bad)
        self.assertIn('fixture synthetic-role member 0: expected trace ["rig:0:0:3", null] '
                      "is absent", bad)

    def test_extra_unrelated_trace_key_fails(self):
        bad = self.rigged(lambda d: self.member(d)["traces"].append(
            ["rig:0:0:1", ["exile", 1]]))
        self.assertIn('fixture synthetic-role member 0: trace ["rig:0:0:1", ["exile", 1]] '
                      "is not one of the member's clauses", bad)

    def test_right_clause_wrong_census_key_fails(self):
        bad = self.rigged(lambda d: self.member(d, "keyed-role")["traces"].__setitem__(
            0, ["rig:0:0:2", None]))
        self.assertTrue(any("is not one of the member's clauses" in b for b in bad), bad)
        self.assertTrue(any('expected trace ["rig:0:0:2", ["destroy", 0]] is absent' in b
                            for b in bad), bad)

    def test_nonexistent_trace_key_fails(self):
        bad = self.rigged(lambda d: self.member(d)["traces"].__setitem__(
            1, ["rig:0:0:9", None]))
        self.assertIn('fixture synthetic-role: trace ["rig:0:0:9", null] is missing', bad)

    def test_traces_swapped_between_fixtures_fail(self):
        def edit(d):
            a, b = self.member(d), self.member(d, "keyed-role")
            a["traces"], b["traces"] = b["traces"], a["traces"]
        bad = self.rigged(edit)
        self.assertTrue(any("does not carry the role" in b for b in bad), bad)
        self.assertTrue(any("no member of it references the trace" in b for b in bad), bad)

    def test_dropped_member_trace_fails(self):
        bad = self.rigged(lambda d: self.member(d)["traces"].pop())
        self.assertIn('fixture synthetic-role member 0: expected trace ["rig:0:0:4", null] '
                      "is absent", bad)
        self.assertIn('trace ["rig:0:0:4", null] carries fixture synthetic-role but no '
                      "member of it references the trace", bad)

    def test_reordered_member_traces_fail(self):
        bad = self.rigged(lambda d: self.member(d)["traces"].reverse())
        self.assertEqual(bad, ["fixture synthetic-role member 0: traces are out of C03 "
                               "order"])

    # ------------------------------------------------ member identity
    def test_incorrect_member_identity_fails(self):
        for field, value in (("oracle_id", "not-rig"), ("census_key", ["exile", 0]),
                             ("name_as_recorded", "Synthetic Gadget")):
            with self.subTest(field=field):
                bad = self.rigged(lambda d, f=field, v=value: self.member(d).update({f: v}))
                self.assertTrue(any(b.startswith("fixture synthetic-role member 0: "
                                                 "identity") for b in bad), bad)

    def test_keyed_member_without_its_census_key_fails(self):
        bad = self.rigged(lambda d: self.member(d, "keyed-role").update(census_key=None))
        self.assertTrue(any(b.startswith("fixture keyed-role member 0: identity")
                            for b in bad), bad)

    # ------------------------------------------- duplicate roles / entries
    def test_duplicate_fixture_role_fails(self):
        bad = self.rigged(lambda d: d["fixtures"].append(copy.deepcopy(d["fixtures"][0])))
        self.assertIn("2 trace entries for fixture 'synthetic-role'", bad)

    def test_duplicate_role_with_altered_copy_fails(self):
        """A second entry under the same role cannot shadow the first."""
        def edit(d):
            dup = copy.deepcopy(d["fixtures"][0])
            dup["members"][0]["traces"] = [["rig:0:0:0", ["exile", 0]]]
            d["fixtures"].insert(0, dup)
        bad = self.rigged(edit)
        self.assertIn("2 trace entries for fixture 'synthetic-role'", bad)

    def test_unknown_fixture_role_fails(self):
        def edit(d):
            extra = copy.deepcopy(d["fixtures"][0])
            extra["role"] = "invented-role"
            d["fixtures"].append(extra)
        self.assertIn("trace entry for fixture 'invented-role' is not a C03 fixture",
                      self.rigged(edit))

    def test_renamed_fixture_role_fails(self):
        bad = self.rigged(lambda d: d["fixtures"][0].update(role="invented-role"))
        self.assertIn("no trace entry for fixture synthetic-role", bad)
        self.assertIn("trace entry for fixture 'invented-role' is not a C03 fixture", bad)

    def test_duplicate_member_entry_fails(self):
        def edit(d):
            ms = d["fixtures"][0]["members"]
            ms.append(copy.deepcopy(ms[0]))
        bad = self.rigged(edit)
        self.assertIn("fixture synthetic-role: 2 members traced of 1", bad)
        self.assertTrue(any("is entered 2 times" in b and "member [" in b for b in bad), bad)

    def test_duplicate_trace_entry_fails(self):
        bad = self.rigged(lambda d: self.member(d)["traces"].append(["rig:0:0:3", None]))
        self.assertIn('fixture synthetic-role member 0: trace ["rig:0:0:3", null] is '
                      "entered 2 times", bad)

    def test_duplicate_trace_entry_replacing_another_fails(self):
        bad = self.rigged(lambda d: self.member(d)["traces"].__setitem__(
            1, ["rig:0:0:3", None]))
        self.assertTrue(any("is entered 2 times" in b for b in bad), bad)
        self.assertTrue(any('expected trace ["rig:0:0:4", null] is absent' in b
                            for b in bad), bad)

    def test_trace_roles_disagreeing_with_c03_fail(self):
        def edit(d):
            d["traces"][0]["fixture_roles"] = ["synthetic-role"]
        bad = self.rigged(edit)
        self.assertTrue(any(b.startswith('trace ["rig:0:0:0", ["exile", 0]]: fixture roles')
                            for b in bad), bad)

    def test_trace_population_flag_disagreeing_with_c03_fails(self):
        bad = self.rigged(lambda d: d["traces"][0].update(population=False))
        self.assertIn('trace ["rig:0:0:0", ["exile", 0]]: population False, C03 True', bad)
        self.assertIn("0 population traces for census row ['rig', 'exile', 0]", bad)

    # ------------------------------------------ C03 fixtures the renderer refuses
    def test_duplicate_c03_fixture_role_is_refused(self):
        regions = copy.deepcopy(self.regions)
        regions["fixtures"].append(copy.deepcopy(regions["fixtures"][0]))
        self.assertTrue(halts(lambda: ct.render_traces(regions, self.kill)))
        self.assertIn("C03: C03 lists fixture synthetic-role 2 times",
                      ct.completeness_failures(self.doc, regions, self.kill))

    def test_c03_member_of_another_card_is_refused(self):
        regions = copy.deepcopy(self.regions)
        regions["fixtures"][0]["members"][0]["oracle_id"] = "other"
        self.assertTrue(halts(lambda: ct.render_traces(regions, self.kill)))

    def test_c03_member_clause_without_the_role_is_refused(self):
        regions = copy.deepcopy(self.regions)
        regions["fixtures"][0]["members"][0]["clauses"].append("rig:0:0:0")
        self.assertTrue(halts(lambda: ct.render_traces(regions, self.kill)))


class MalformedCensusKey(unittest.TestCase):
    """A population trace with a null census key is reported as malformed,
    never a TypeError; a C03 population record with one halts the renderer."""

    def setUp(self):
        self.regions, self.kill = docs()
        self.doc = ct.render_traces(self.regions, self.kill)

    def failures(self, doc):
        return ct.completeness_failures(doc, self.regions, self.kill)

    def test_null_population_census_key_is_reported(self):
        for i, t in enumerate(self.doc["traces"]):
            if not t["population"]:
                continue
            with self.subTest(trace=i):
                doc = copy.deepcopy(self.doc)
                doc["traces"][i]["key"][1] = None
                bad = self.failures(doc)          # must not raise TypeError
                self.assertIn(f"population trace {t['key'][0]!r} is malformed: its "
                              f"census key is null", bad)

    def test_malformed_census_key_shapes_are_reported(self):
        for ck in ("exile", ["exile"], [0, "exile"], ["exile", True], ["exile", 0, 1], {}):
            with self.subTest(census_key=ck):
                doc = copy.deepcopy(self.doc)
                doc["traces"][0]["key"][1] = ck
                bad = self.failures(doc)
                self.assertTrue(any("has a malformed key" in b for b in bad), bad)

    def test_unreadable_trace_is_reported_not_raised(self):
        for edit in (lambda d: d["traces"].__setitem__(0, None),
                     lambda d: d["traces"][0].pop("key"),
                     lambda d: d["fixtures"][0]["members"][0].pop("traces"),
                     lambda d: d.pop("fixtures")):
            doc = copy.deepcopy(self.doc)
            edit(doc)
            self.assertTrue(self.failures(doc))

    def test_cli_exits_1_on_null_census_key(self):
        doc = copy.deepcopy(self.doc)
        doc["traces"][0]["key"][1] = None
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for rel, body in ((ct.REGIONS_REL, self.regions), (ct.KILL_REL, self.kill)):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text(json.dumps(body))
            out = root / ct.OUT_REL
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(doc))
            with mock.patch.object(ct, "ROOT", root), \
                    mock.patch.object(ct, "OUT", out), \
                    mock.patch.object(ct, "verify", return_value=0), \
                    mock.patch.object(ct, "ensure_inputs"), \
                    contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()) as err:
                self.assertEqual(ct.check_complete(), 1)
        self.assertIn("INCOMPLETE: population trace 'rig:0:0:0' is malformed: its census "
                      "key is null", err.getvalue().splitlines())

    def test_null_population_record_halts_renderer(self):
        regions, kill = copy.deepcopy((self.regions, self.kill))
        regions["clauses"][0]["census_key"] = None
        kill["clauses"][0]["census_key"] = None       # only the null key is wrong
        with contextlib.redirect_stderr(io.StringIO()) as err:
            with self.assertRaises(SystemExit) as cm:
                ct.render_traces(regions, kill)
        self.assertIn("census key None is malformed", str(cm.exception) + err.getvalue())

    def test_malformed_c03_census_key_halts_with_diagnostic(self):
        """Regression: ['exile'] was indexed before validation (IndexError)."""
        for i in (0, 3):                              # a population and a fixture record
            for ck in (["exile"], "exile", [0, "exile"], ["exile", True],
                       ["exile", 0, 1], {}, ["exile", None]):
                with self.subTest(record=i, census_key=ck):
                    regions, kill = copy.deepcopy((self.regions, self.kill))
                    regions["clauses"][i]["census_key"] = ck
                    kill["clauses"][i]["census_key"] = ck  # only the key's shape is wrong
                    for fn in (lambda: ct.render_traces(regions, kill),
                               lambda: ct.trace(regions["clauses"][i],
                                                kill["clauses"][i])):
                        with contextlib.redirect_stderr(io.StringIO()) as err:
                            with self.assertRaises(SystemExit):
                                fn()              # never IndexError / TypeError
                        self.assertIn(f"census key {ck!r} is malformed", err.getvalue())

    def test_well_formed_census_keys_still_render(self):
        doc = ct.render_traces(self.regions, self.kill)
        self.assertEqual([t["key"][1] for t in doc["traces"]],
                         [["exile", 0], ["exile", 1], ["destroy", 0], None])


# interface/3 §I3a R4: synthetic labels (a flavor label, one holding a head
# word, and a keyword label R4 keeps), each opening its own paragraph.
DRILL = ("Synthetic Drill — When this widget enters, if you control an artifact, exile "
         "target artifact, then return it to the battlefield.")
RETURN_DRILL = ("Return Drill — Exile target artifact you control, then return that "
                "card to the battlefield.")
KEPT = ("Flying — When this widget enters, exile target artifact, then return it to "
        "the battlefield.")


def r4_docs():
    """(regions_doc, kill_doc): three labelled population clauses and one
    unlabelled fixture clause."""
    a = ct.rig_paragraph(DRILL, 0, census=("exile", 0), population=True)
    b = ct.rig_paragraph(RETURN_DRILL, 1, census=("exile", 1), population=True)
    c = ct.rig_paragraph(KEPT, 2, census=("exile", 2), population=True)
    d = hk._rig(TWO, roles=["synthetic-role"], ci=1)
    return ct.rig_docs(
        [a, b, c, d], [["rig", "exile", 0], ["rig", "exile", 1], ["rig", "exile", 2]],
        [{"role": "synthetic-role", "member_status": "synthetic",
          "members": [{"oracle_id": "rig", "census_key": None,
                       "clauses": [d["address"]["id"]]}]}], NAMES)


class R4Trace(unittest.TestCase):
    """Every R4 label and every value R4 changed is rendered in its clause's
    trace beside its interface/2 value, copied from C03."""

    def setUp(self):
        self.regions, self.kill = r4_docs()
        self.doc = ct.render_traces(self.regions, self.kill)
        self.drill, self.ret, self.kept, self.plain = self.doc["traces"]

    def items(self, t, kind):
        return [i for i in t["r4_changed"] if i["kind"] == kind]

    def test_every_label_rendered_with_offsets_class_cr_effect_and_heads(self):
        for t, rec in zip(self.doc["traces"][:3], self.regions["clauses"]):
            lab = rec["r4_label"]
            with self.subTest(clause=t["key"]):
                for k in ("span", "text", "class", "cr", "effect", "scope_start"):
                    self.assertEqual(t["r4_label"][k], lab[k])
                self.assertEqual(t["r4_label"]["dropped_heads"],
                                 [[h["head"], h["start"]] for h in lab["dropped_heads"]])
                line = next(x for x in t["lines"] if x.startswith("  R4 label"))
                self.assertIn(f"[{lab['span'][0]}, {lab['span'][1]})", line)
                self.assertIn(f"{lab['class']} ({lab['cr']}) {lab['effect'].upper()}", line)

    def test_ignored_and_kept_labels(self):
        self.assertEqual(self.drill["r4_label"]["effect"], "ignored")
        self.assertEqual(self.ret["r4_label"]["dropped_heads"], [["return", 0]])
        self.assertIn("heads dropped: return@0", next(
            x for x in self.ret["lines"] if x.startswith("  R4 label")))
        self.assertEqual((self.kept["r4_label"]["effect"], self.kept["r4_changed"]),
                         ("kept", []))
        self.assertFalse(any(x.startswith("  R4 changed") for x in self.kept["lines"]))

    def test_unlabelled_clause_has_no_r4_record(self):
        self.assertEqual((self.plain["r4_label"], self.plain["r4_changed"]), (None, []))
        self.assertFalse(any(x.startswith("  R4") for x in self.plain["lines"]))

    def test_changed_mark_beside_its_interface2_value(self):
        rec = self.regions["clauses"][0]
        want = [s for s in rec["role_spans"] if "interface2" in s]
        got = self.items(self.drill, "mark")
        self.assertTrue(want)
        self.assertEqual([(i["interface3"]["span"], i["interface2"]) for i in got],
                         [(s["span"], s["interface2"]["span"]) for s in want])
        self.assertTrue(all(i["rule"] == "R4" for i in self.drill["r4_changed"]))

    def test_changed_outcome_beside_its_interface2_value(self):
        k4 = next(i for i in self.items(self.drill, "outcome") if i["item"] == "K4")
        row = self.kill["clauses"][0]
        self.assertEqual(k4["interface2"]["outcome"], row["r4_off_tests"]["K4"]["outcome"])
        self.assertEqual(k4["interface3"]["outcome"], row["tests"]["K4"]["outcome"])
        self.assertNotEqual(k4["interface2"], k4["interface3"])
        self.assertIn(f"  R4 changed K4: interface/2 {k4['interface2']['outcome']}  |  "
                      f"interface/3 {k4['interface3']['outcome']}", self.drill["lines"])

    def test_changed_regions_and_fields(self):
        rec = self.regions["clauses"][1]
        self.assertEqual([i["item"] for i in self.items(self.ret, "field")],
                         [f for f in ct.R4_FIELD_ITEMS
                          if f in rec["r4_interface2"]["changed"]])
        scope = next(i for i in self.ret["r4_changed"] if i["item"] == "scope")
        self.assertEqual((scope["interface2"], scope["interface3"]),
                         (rec["r4_interface2"]["scope"], rec["scope"]))
        regions = self.items(self.ret, "region")
        self.assertIn(None, [i["interface3"] for i in regions])     # the dropped region
        self.assertTrue(any(i["interface2"] and i["interface3"] for i in regions))

    def test_clean_is_complete(self):
        self.assertEqual(ct.completeness_failures(self.doc, self.regions, self.kill), [])


class R4CheckComplete(unittest.TestCase):
    """Negative controls: --check-complete fails on a trace that drops one R4
    label, drops an R4-changed outcome, or misstates or duplicates one."""

    def setUp(self):
        self.regions, self.kill = r4_docs()
        self.doc = ct.render_traces(self.regions, self.kill)

    def failures(self, doc, regions=None, kill=None):
        return ct.completeness_failures(doc, regions or self.regions, kill or self.kill)

    def test_each_dropped_label_fails(self):
        for n in range(3):
            with self.subTest(trace=n):
                doc = copy.deepcopy(self.doc)
                doc["traces"][n]["r4_label"] = None
                bad = self.failures(doc)
                self.assertTrue(any("R4 label" in b and "regions.json" in b for b in bad))
                self.assertTrue(any("R4 label" in b and "kill.json" in b for b in bad))

    def test_dropped_changed_outcome_fails(self):
        doc = copy.deepcopy(self.doc)
        ch = doc["traces"][0]["r4_changed"]
        ch.remove(next(i for i in ch if i["kind"] == "outcome"))
        self.assertTrue(any("R4 changed outcome" in b and "appears in 0 trace(s)" in b
                            for b in self.failures(doc)))

    def test_each_dropped_changed_value_fails(self):
        for n in range(2):
            for j in range(len(self.doc["traces"][n]["r4_changed"])):
                with self.subTest(trace=n, item=j):
                    doc = copy.deepcopy(self.doc)
                    gone = doc["traces"][n]["r4_changed"].pop(j)
                    bad = self.failures(doc)
                    self.assertTrue(any("appears in 0 trace(s)" in b for b in bad),
                                    (gone["item"], bad))

    def test_misstated_interface2_value_fails(self):
        for n in range(2):
            for j, i in enumerate(self.doc["traces"][n]["r4_changed"]):
                with self.subTest(trace=n, item=i["item"]):
                    doc = copy.deepcopy(self.doc)
                    doc["traces"][n]["r4_changed"][j]["interface2"] = "misstated"
                    self.assertTrue(self.failures(doc))

    def test_value_in_two_traces_fails(self):
        doc = copy.deepcopy(self.doc)
        doc["traces"][2]["r4_label"] = copy.deepcopy(doc["traces"][0]["r4_label"])
        doc["traces"][2]["key"] = doc["traces"][0]["key"]
        doc["traces"][2]["occurrence"] = doc["traces"][0]["occurrence"]
        bad = self.failures(doc)
        self.assertTrue(any("R4 label" in b and "appears in 2 trace(s)" in b for b in bad))

    def test_trace_without_r4_fields_fails(self):
        for f in ("r4_label", "r4_changed"):
            doc = copy.deepcopy(self.doc)
            doc["traces"][0].pop(f)
            self.assertIn(f'trace ["rig:0:0:0", ["exile", 0]] carries no {f}',
                          self.failures(doc))

    def test_label_regions_json_records_but_no_trace_carries_fails(self):
        regions = copy.deepcopy(self.regions)
        s = regions["measurements"]["all"]["interface3_rules"]["R4_ability_label"]
        s["labels"].append(dict(s["labels"][0], clause="rig:0:9:0"))
        self.assertTrue(any("is recorded 1 time(s) in regions.json but appears in 0"
                            in b for b in self.failures(self.doc, regions=regions)))

    def test_outcome_kill_json_records_but_no_trace_carries_fails(self):
        kill = copy.deepcopy(self.kill)
        rows = kill["changed_from_interface2"]["rows"]
        rows.append(["rig:0:2:0", ["exile", 2]] + rows[0][2:])
        self.assertTrue(any("R4 changed outcome" in b and "appears in 0" in b
                            for b in self.failures(self.doc, kill=kill)))

    def test_c03_without_r4_measurement_fails(self):
        regions = copy.deepcopy(self.regions)
        del regions["measurements"]
        self.assertTrue(any("C03 carries no interface/3 R4 record" in b
                            for b in self.failures(self.doc, regions=regions)))


class R4Renderer(unittest.TestCase):
    """An R4 record the renderer cannot account for halts it."""

    def rigged(self, edit):
        regions, kill = r4_docs()
        edit(regions, kill)
        return halts(lambda: ct.render_traces(regions, kill))

    def test_unrigged_does_not_halt(self):
        self.assertFalse(self.rigged(lambda r, k: None))

    def test_kill_row_without_r4_record_halts(self):
        for f in ("r4_label", "r4_off_tests"):
            with self.subTest(field=f):
                self.assertTrue(self.rigged(lambda r, k, f=f: k["clauses"][0].pop(f)))

    def test_kill_label_disagreeing_with_regions_halts(self):
        self.assertTrue(self.rigged(
            lambda r, k: k["clauses"][0]["r4_label"].update({"class": "ability word"})))
        self.assertTrue(self.rigged(
            lambda r, k: k["clauses"][3].update(r4_label=k["clauses"][0]["r4_label"])))

    def test_unrecorded_outcome_change_halts(self):
        self.assertTrue(self.rigged(lambda r, k: k["clauses"][0].pop("interface2_changes")))

    def test_changed_region_without_interface2_value_halts(self):
        def edit(r, k):
            for x in r["clauses"][1]["regions"]:
                x.pop("interface2", None)
        self.assertTrue(self.rigged(edit))

    def test_changed_mark_without_interface2_value_halts(self):
        def edit(r, k):
            for s in r["clauses"][0]["role_spans"]:
                s.pop("interface2", None)
        self.assertTrue(self.rigged(edit))

    def test_interface2_value_on_a_kept_label_halts(self):
        def edit(r, k):
            r["clauses"][2]["r4_interface2"] = copy.deepcopy(r["clauses"][0]["r4_interface2"])
        self.assertTrue(self.rigged(edit))

    def test_changed_list_disagreeing_halts(self):
        self.assertTrue(self.rigged(
            lambda r, k: r["clauses"][1]["r4_interface2"]["changed"].remove("scope")))


class EmbeddedControls(unittest.TestCase):
    def test_script_negative_controls_all_fire(self):
        names = ct.negative_controls()
        self.assertEqual(len(names), 15)
        for want in ("a C03 record missing its owning occurrence halts the renderer",
                     "--check-complete fails on a rigged dropped trace",
                     "--check-complete fails on a rigged outcome mismatch",
                     "--check-complete fails on a fixture member pointing at an unrelated "
                     "trace",
                     "--check-complete fails on an incorrect fixture member identity",
                     "--check-complete fails on a duplicate fixture role",
                     "--check-complete fails on a duplicate fixture member entry",
                     "--check-complete fails on a duplicate fixture trace entry",
                     "--check-complete reports a null population census key as malformed",
                     "a C03 population record with a null census key halts the renderer",
                     "a C03 record with a malformed census key halts the renderer with "
                     "its diagnostic",
                     "--verify fails on a rigged stale kill.json",
                     "--check-complete fails on a rigged trace that drops one R4 label",
                     "--check-complete fails on a rigged trace that drops an R4-changed "
                     "outcome"):
            self.assertIn(want, names)


if __name__ == "__main__":
    unittest.main()
