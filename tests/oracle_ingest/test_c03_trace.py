"""C03b unit tests: the trace renderer, --verify and --check-complete, with both
negative controls (a record missing its owning occurrence halts; a dropped
trace or an outcome mismatch fails --check-complete) and a stale kill.json.

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
    regions_doc = {
        "clauses": recs,
        "population_keys": [["rig", "exile", 0], ["rig", "exile", 1],
                            ["rig", "destroy", 0]],
        "fixtures": [{"role": "synthetic-role", "member_status": "synthetic",
                      "members": [{"oracle_id": "rig", "census_key": None,
                                   "clauses": [d["address"]["id"]]}]}]}
    return regions_doc, hk.evaluate(recs, list(hr.RULES), NAMES)


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


class EmbeddedControls(unittest.TestCase):
    def test_script_negative_controls_all_fire(self):
        names = ct.negative_controls()
        self.assertEqual(len(names), 5)
        self.assertIn("a C03 record missing its owning occurrence halts the renderer",
                      names)


if __name__ == "__main__":
    unittest.main()
