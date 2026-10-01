"""M04-CHECK unit tests: the coverage and consistency checker for the M04
H-REGION review document, with every contracted negative control -- a ledger
missing one clause, a total mismatch, an UNRESOLVED row without a disposition
(and, per placeholder form -- null/None, JSON null, none, a dash or em-dash,
TBD/TODO, empty, any case -- an UNRESOLVED row or a fixture without a clause
"disposed" by that placeholder), a stale trace.json (STOPs), a wrong trace.json hash, 'not killed' stated over a
relevant KILL, and an omitted PASS-coverage flag -- plus the hand-off rule
(producers' --verify first, missing artifacts regenerated only by their
unchanged producers, in order).

Inline SYNTHETIC clauses only -- generic templating, no card, no card name, no
oracle_id and no Oracle text. Never reads or writes c03/ or c03b/ output: the
hand-off rule is exercised on a temporary root with a rigged producer runner.

    python3 -m unittest discover -s tests/oracle_ingest -t .
"""
import contextlib
import copy
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "oracle_ingest"))

import h_region_kill as hk       # noqa: E402
import m04_check as mc           # noqa: E402

KILL, UNRESOLVED, PASS = hk.KILL, hk.UNRESOLVED, hk.PASS


def halts(fn, needle=""):
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            fn()
    except SystemExit:
        return needle in err.getvalue()
    return False


def line(doc, prefix):
    return next(l for l in doc.splitlines(keepends=True) if l.startswith(prefix))


class Base(unittest.TestCase):
    def setUp(self):
        self.regions, self.kill, self.shas, self.doc = mc.synthetic()

    def failures(self, doc=None, kill=None, shas=None, regions=None):
        return mc.document_failures(self.doc if doc is None else doc,
                                    self.regions if regions is None else regions,
                                    self.kill if kill is None else kill,
                                    self.shas if shas is None else shas)

    def assertFails(self, needle, **kw):
        bad = self.failures(**kw)
        self.assertTrue(any(needle in b for b in bad), f"{needle!r} not in {bad}")


class Clean(Base):
    def test_synthetic_has_an_unresolved_population_row_and_an_empty_fixture(self):
        row = self.kill["clauses"][0]
        self.assertTrue(row["population"])
        self.assertEqual(row["tests"]["K1"]["outcome"], UNRESOLVED)
        self.assertEqual([f["role"] for f in self.kill["fixtures_without_clauses"]],
                         ["rig-empty"])

    def test_unrigged_document_passes(self):
        self.assertEqual(self.failures(), [])

    def test_in_script_negative_controls_hold(self):
        names = mc.negative_controls()
        self.assertEqual(len(names), 2 + len(mc.rigs()))
        self.assertIn("a rigged stale trace.json STOPs the checker", names)

    def test_skeleton_alone_fails_only_for_dispositions(self):
        sk = mc.skeleton(self.regions, self.kill, self.shas)
        bad = self.failures(doc=sk)
        self.assertTrue(bad)
        self.assertTrue(all(b.endswith("carries no disposition") for b in bad), bad)

    def test_checker_does_not_mutate_its_inputs(self):
        before = copy.deepcopy((self.regions, self.kill, self.shas))
        self.failures()
        self.assertEqual((self.regions, self.kill, self.shas), before)

    def test_bold_and_backticked_result_line_is_read(self):
        doc = self.doc.replace(f"H-REGION result: {hk.RESULT_NOT_KILLED}",
                               f"**H-REGION result:** `{hk.RESULT_NOT_KILLED}`")
        self.assertEqual(self.failures(doc=doc), [])


class Ledger(Base):
    def test_missing_clause_fails(self):
        self.assertFails("the ledger omits C03 clause rig:0:0:0",
                         doc=self.doc.replace(line(self.doc, "| `rig:0:0:0`"), ""))

    def test_missing_population_row_is_named(self):
        self.assertFails("population census row ['rig', 'destroy', 0] 0 times",
                         doc=self.doc.replace(line(self.doc, "| `rig:0:0:0`"), ""))

    def test_missing_fixture_clause_fails(self):
        self.assertFails("the ledger omits C03 clause rig:0:0:1",
                         doc=self.doc.replace(line(self.doc, "| `rig:0:0:1`"), ""))

    def test_duplicate_row_fails(self):
        row = line(self.doc, "| `rig:0:0:0`")
        self.assertFails("2 times; exactly once", doc=self.doc.replace(row, row + row))

    def test_foreign_row_fails(self):
        row = line(self.doc, "| `rig:0:0:0`")
        self.assertFails("which is not a C03 clause",
                         doc=self.doc.replace(row, row + row.replace("rig:0:0:0",
                                                                     "rig:0:0:9")))

    def test_wrong_census_key_fails(self):
        row = line(self.doc, "| `rig:0:0:0`")
        self.assertFails("the ledger omits C03 clause rig:0:0:0 census destroy#0",
                         doc=self.doc.replace(row, row.replace("destroy#0", "destroy#1")))

    def test_row_outcome_mismatch_fails(self):
        row = line(self.doc, "| `rig:0:0:1`")
        cells = row.split("|")
        k7 = 4 + mc.CONDITIONS.index("K7") + 1
        self.assertEqual(cells[k7].strip(), PASS)
        cells[k7] = f" {KILL} "
        self.assertFails(f"K7 '{KILL}', kill.json {PASS}",
                         doc=self.doc.replace(row, "|".join(cells)))

    def test_population_and_fixture_columns_are_checked(self):
        row = line(self.doc, "| `rig:0:0:1`")
        self.assertFails("population 'yes', kill.json no",
                         doc=self.doc.replace(row, row.replace("| no |", "| yes |")))
        self.assertFails("fixtures 'none', kill.json 'rig-role'",
                         doc=self.doc.replace(row, row.replace("| rig-role |", "| none |")))

    def test_unresolved_row_without_disposition_fails(self):
        row = line(self.doc, "| `rig:0:0:0`")
        for empty in (mc.NONE, "", "—", "TBD") + mc.PLACEHOLDER_FORMS + (
                "Null", "`None`", "**null**", "\"null\"", "None.", "n/a", "--", "–",
                "ToDo", "  "):
            with self.subTest(disposition=empty):
                rigged = row.rsplit("|", 2)[0] + f"| {empty} |\n"
                self.assertFails("rig:0:0:0 census destroy#0: UNRESOLVED on K1",
                                 doc=self.doc.replace(row, rigged))

    def test_placeholder_forms_cover_the_contracted_ones(self):
        lowered = {f.lower() for f in mc.PLACEHOLDER_FORMS}
        for form in ("null", "none", "`null`", "-", "—", "tbd", "todo", ""):
            self.assertIn(form, lowered)
        for word in ("null", "none", "tbd", "todo"):   # case-insensitively
            self.assertTrue(any(f != word and f.lower() == word
                                for f in mc.PLACEHOLDER_FORMS), word)

    def test_each_placeholder_form_has_its_own_negative_control(self):
        rigs = mc.rigs()
        for form in mc.PLACEHOLDER_FORMS:
            for name in (f"an UNRESOLVED row disposed as {form!r}",
                         f"a fixture without a clause disposed as {form!r}"):
                with self.subTest(control=name):
                    doc, regions, kill, shas, needle = rigs[name]
                    self.assertFails(needle, doc=doc, regions=regions, kill=kill,
                                     shas=shas)

    def test_real_disposition_text_or_code_passes(self):
        row = line(self.doc, "| `rig:0:0:0`")
        for real in ("EXTRACTION-GAP", "`D2`", "deferred to the Captain (FS-2)",
                     "none of K1/K2 apply: a sequence, not a kill", "nullary trigger"):
            with self.subTest(disposition=real):
                rigged = row.rsplit("|", 2)[0] + f"| {real} |\n"
                self.assertEqual(self.failures(doc=self.doc.replace(row, rigged)), [])

    def test_row_with_no_unresolved_needs_no_disposition(self):
        row = line(self.doc, "| `rig:0:0:1`")
        self.assertNotIn(UNRESOLVED, row)
        rigged = row.rsplit("|", 2)[0] + f"| {mc.NONE} |\n"
        self.assertEqual(self.failures(doc=self.doc.replace(row, rigged)), [])

    def test_short_row_is_reported(self):
        row = line(self.doc, "| `rig:0:0:0`")
        self.assertFails("cells, not 12", doc=self.doc.replace(row, row.rsplit("|", 2)[0]
                                                                + "|\n"))

    def test_missing_ledger_table_fails(self):
        head = mc._row(mc.LEDGER_HEAD)
        self.assertFails("0 tables headed | clause |",
                         doc=self.doc.replace(head, head.replace("clause", "row")))


class Fixtures(Base):
    def test_missing_fixture_fails(self):
        self.assertFails("the fixture table omits C03 fixture rig-role",
                         doc=self.doc.replace(line(self.doc, "| rig-role |"), ""))

    def test_duplicate_fixture_fails(self):
        row = line(self.doc, "| rig-empty |")
        self.assertFails("lists rig-empty 2 times", doc=self.doc.replace(row, row + row))

    def test_wrong_clause_count_fails(self):
        row = line(self.doc, "| rig-role |")
        self.assertFails("fixture rig-role: clauses '2', C03 1",
                         doc=self.doc.replace(row, row.replace("| 1 | 1 |", "| 1 | 2 |")))

    def test_fixture_without_clause_needs_a_disposition(self):
        row = line(self.doc, "| rig-empty |")
        for empty in (mc.NONE,) + mc.PLACEHOLDER_FORMS:
            with self.subTest(disposition=empty):
                rigged = row.rsplit("|", 2)[0] + f"| {empty} |\n"
                self.assertFails("fixture rig-empty: a member without a clause",
                                 doc=self.doc.replace(row, rigged))


class Totals(Base):
    def rig(self, cond, col, value):
        row = line(self.doc, f"| {cond} |")
        cells = row.split("|")
        cells[1 + mc.TOTALS_HEAD.index(col)] = f" {value} "
        return self.doc.replace(row, "|".join(cells))

    def test_total_mismatch_fails(self):
        for col in mc.TOTALS_HEAD[1:8]:
            with self.subTest(column=col):
                self.assertFails(f"K3 {col}: stated '999'", doc=self.rig("K3", col, 999))

    def test_omitted_pass_coverage_flag_fails(self):
        self.assertFails("K1 PASS coverage: stated ''",
                         doc=self.rig("K1", "PASS coverage", ""))

    def test_insufficient_coverage_must_be_flagged(self):
        kill = copy.deepcopy(self.kill)
        for r in kill["clauses"]:
            if r["tests"]["K1"]["outcome"] == PASS:
                r["tests"]["K1"]["outcome"] = UNRESOLVED
        kill["conditions"] = hk.summarize(kill["clauses"])
        self.assertEqual(kill["conditions"]["K1"]["pass_coverage"], hk.COVERAGE_FLAG)
        doc = mc.skeleton(self.regions, kill, self.shas).replace(
            f" | {mc.NONE} |\n", " | reviewed |\n")
        self.assertEqual(self.failures(doc=doc, kill=kill), [])
        omitted = doc.replace(f"| {hk.COVERAGE_FLAG} |", "| sufficient |")
        self.assertFails("K1 PASS coverage: stated 'sufficient'", doc=omitted, kill=kill)
        # A coverage flag never changes the result.
        self.assertIn(f"H-REGION result: {hk.RESULT_NOT_KILLED}", doc)

    def test_missing_condition_row_fails(self):
        self.assertFails("the totals table omits condition K5",
                         doc=self.doc.replace(line(self.doc, "| K5 |"), ""))

    def test_per_condition_result_follows_precedence(self):
        self.assertFails("K2 result: stated 'killed'", doc=self.rig("K2", "result",
                                                                    hk.RESULT_KILLED))

    def test_inconsistent_kill_json_is_reported(self):
        kill = copy.deepcopy(self.kill)
        kill["conditions"]["K6"]["result"] = hk.RESULT_KILLED
        self.assertFails("kill.json K6: result 'killed' does not follow", kill=kill)


class Result(Base):
    def test_not_killed_over_a_relevant_kill_fails(self):
        doc, regions, kill, shas, needle = mc.rigs()[
            "a document stating 'not killed' over a relevant KILL"]
        self.assertEqual(kill["conditions"]["K4"]["result"], hk.RESULT_KILLED)
        self.assertFails(needle, doc=doc, kill=kill)
        fixed = doc.replace(f"H-REGION result: {hk.RESULT_NOT_KILLED}",
                            f"H-REGION result: {hk.RESULT_KILLED}")
        self.assertEqual(self.failures(doc=fixed, kill=kill), [])

    def test_killed_over_no_kill_fails(self):
        self.assertFails("RESULT PRECEDENCE gives 'not killed on the P2 population'",
                         doc=self.doc.replace(hk.RESULT_NOT_KILLED + "\n",
                                              hk.RESULT_KILLED + "\n"))

    def test_confirmed_is_never_a_result(self):
        self.assertFails("stated as 'confirmed'",
                         doc=self.doc.replace(f"H-REGION result: {hk.RESULT_NOT_KILLED}",
                                              "H-REGION result: confirmed"))

    def test_result_stated_zero_or_twice_fails(self):
        stmt = f"H-REGION result: {hk.RESULT_NOT_KILLED}\n"
        self.assertFails("0 times", doc=self.doc.replace(stmt, ""))
        self.assertFails("2 times", doc=self.doc + stmt)


class Citations(Base):
    def test_wrong_hash_fails_for_each_artifact(self):
        for rel in mc.ARTIFACTS:
            with self.subTest(artifact=rel):
                self.assertFails(f"cites {rel} sha256",
                                 shas=dict(self.shas, **{rel: "0" * 64}))

    def test_missing_trace_citation_fails(self):
        self.assertFails(f"cites {mc.TRACE_REL} 0 times",
                         doc=self.doc.replace(line(self.doc, f"| `{mc.TRACE_REL}`"), ""))

    def test_foreign_citation_fails(self):
        row = line(self.doc, f"| `{mc.TRACE_REL}`")
        self.assertFails("is not a C03/C03b artifact",
                         doc=self.doc.replace(row, row + row.replace("trace.json",
                                                                     "other.json")))


class HandOff(unittest.TestCase):
    """obtain() on a temporary root with a rigged producer runner."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.calls = []

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, *rels):
        for rel in rels:
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.root / rel).write_bytes(b"{}\n")

    def runner(self, stale=(), broken=(), writes=True):
        def run(args):
            script = args[0].split(str(self.root) + "/")[1]
            self.calls.append([script] + args[1:])
            art = dict(mc.PRODUCERS)[script]
            if args[1:] == ["--verify"]:
                bad = script in stale
                return subprocess.CompletedProcess(args, int(bad), b"",
                                                   b"STALE: rigged" if bad else b"")
            if script in broken:
                return subprocess.CompletedProcess(args, 1, b"", b"rigged failure")
            if writes:
                self.put(art)
            return subprocess.CompletedProcess(args, 0, b"", b"")
        return run

    def obtain(self, **kw):
        with contextlib.redirect_stderr(io.StringIO()):
            return mc.obtain(self.root, self.runner(**kw))

    def scripts(self):
        return [s for s, _ in mc.PRODUCERS]

    def test_existing_artifacts_are_verified_in_order(self):
        self.put(*mc.ARTIFACTS)
        got = self.obtain()
        self.assertEqual(self.calls, [[s, "--verify"] for s in self.scripts()])
        self.assertEqual(sorted(got), sorted(mc.ARTIFACTS))

    def test_stale_trace_stops_the_checker(self):
        self.put(*mc.ARTIFACTS)
        self.assertTrue(halts(lambda: mc.obtain(self.root, self.runner(
            stale=[mc.ct.SCRIPT])), f"stale C03 input: {mc.TRACE_REL}"))
        self.assertTrue(mc.stale_trace_stops())

    def test_stale_regions_stops_before_any_other_producer(self):
        self.put(*mc.ARTIFACTS)
        self.assertTrue(halts(lambda: mc.obtain(self.root, self.runner(
            stale=[mc.hr.SCRIPT])), f"stale C03 input: {mc.REGIONS_REL}"))
        self.assertEqual(self.calls, [[mc.hr.SCRIPT, "--verify"]])

    def test_missing_artifacts_are_regenerated_by_their_producers_in_order(self):
        self.put(mc.REGIONS_REL)
        self.obtain()
        self.assertEqual(self.calls, [[mc.hr.SCRIPT, "--verify"], [mc.hk.SCRIPT],
                                      [mc.hk.SCRIPT, "--verify"], [mc.ct.SCRIPT],
                                      [mc.ct.SCRIPT, "--verify"]])
        written = sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*")
                         if p.is_file())
        self.assertEqual(written, sorted(mc.ARTIFACTS))

    def test_failed_regeneration_halts(self):
        self.assertTrue(halts(lambda: mc.obtain(self.root, self.runner(
            broken=[mc.hr.SCRIPT])), "could not regenerate the missing"))

    def test_producer_that_writes_nothing_halts(self):
        self.assertTrue(halts(lambda: mc.obtain(self.root, self.runner(writes=False)),
                              "did not write"))

    def test_regenerated_artifact_that_is_stale_halts(self):
        self.put(mc.REGIONS_REL, mc.KILL_REL)
        self.assertTrue(halts(lambda: mc.obtain(self.root, self.runner(
            stale=[mc.ct.SCRIPT])), "regenerated"))

    def test_hashes_are_of_the_verified_bytes(self):
        self.put(*mc.ARTIFACTS)
        (self.root / mc.TRACE_REL).write_bytes(b"rigged\n")
        got = self.obtain()
        import hashlib
        self.assertEqual(got[mc.TRACE_REL], hashlib.sha256(b"rigged\n").hexdigest())


class Parsing(unittest.TestCase):
    def test_tables_strip_backticks_and_need_a_separator(self):
        text = "| a | `b` |\n|---|---|\n| `x` | y |\n\n| c |\n| d |\n"
        self.assertEqual(mc.tables(text), [[["a", "b"], [["x", "y"]]]])

    def test_census_and_roles_text(self):
        self.assertEqual(mc.census_text(None), "none")
        self.assertEqual(mc.census_text(["exile", 0]), "exile#0")
        self.assertEqual(mc.roles_text([]), "none")
        self.assertEqual(mc.roles_text(["a", "b"]), "a, b")


if __name__ == "__main__":
    unittest.main()
