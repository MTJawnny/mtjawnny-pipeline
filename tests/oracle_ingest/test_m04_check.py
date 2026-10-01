"""M04-CHECK unit tests: the coverage and consistency checker for the M04
H-REGION review document, with every contracted negative control -- a ledger
missing one clause, a total mismatch, an UNRESOLVED row without a disposition
(and, per placeholder form -- null/None, JSON null, none, a dash or em-dash,
TBD/TODO, empty, any case -- an UNRESOLVED row or a fixture without a clause
"disposed" by that placeholder), a stale trace.json (STOPs), a wrong trace.json hash, 'not killed' stated over a
relevant KILL, and an omitted PASS-coverage flag -- plus the hand-off rule
(producers' --verify first, missing artifacts regenerated only by their
unchanged producers, in order). interface/3 §I3a R4: an R4 section missing
one R4-changed clause or row, misstating one interface/2 value, or carrying a
row for a clause outside R4 reach fails; a kill.json R4-off outcome that
differs from the interface/2 review's section 6 ledger row fails.

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
        self.regions, self.kill, self.shas, self.doc, self.i2 = mc.synthetic()

    def failures(self, doc=None, kill=None, shas=None, regions=None, i2=None):
        return mc.document_failures(self.doc if doc is None else doc,
                                    self.regions if regions is None else regions,
                                    self.kill if kill is None else kill,
                                    self.shas if shas is None else shas,
                                    self.i2 if i2 is None else i2)

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
                    doc, regions, kill, shas, i2, needle = rigs[name]
                    self.assertFails(needle, doc=doc, regions=regions, kill=kill,
                                     shas=shas, i2=i2)

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
            self.assertNotIn("K1", r.get("interface2_changes") or {})
            for view in (r["tests"], r["r4_off_tests"]):   # R4 left K1 alone
                if view["K1"]["outcome"] == PASS:
                    view["K1"]["outcome"] = UNRESOLVED
        kill["conditions"] = hk.summarize(kill["clauses"])
        self.assertEqual(kill["conditions"]["K1"]["pass_coverage"], hk.COVERAGE_FLAG)
        doc = mc.skeleton(self.regions, kill, self.shas).replace(
            f" | {mc.NONE} |\n", " | reviewed |\n")
        i2 = mc.i2_ledger(kill)
        self.assertEqual(self.failures(doc=doc, kill=kill, i2=i2), [])
        omitted = doc.replace(f"| {hk.COVERAGE_FLAG} |", "| sufficient |")
        self.assertFails("K1 PASS coverage: stated 'sufficient'", doc=omitted, kill=kill,
                         i2=i2)
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
        doc, regions, kill, shas, i2, needle = mc.rigs()[
            "a document stating 'not killed' over a relevant KILL"]
        self.assertEqual(kill["conditions"]["K4"]["result"], hk.RESULT_KILLED)
        i2 = mc.i2_ledger(kill)       # the rigged KILL is R4-off too (no label)
        self.assertFails(needle, doc=doc, kill=kill, i2=i2)
        fixed = doc.replace(f"H-REGION result: {hk.RESULT_NOT_KILLED}",
                            f"H-REGION result: {hk.RESULT_KILLED}")
        self.assertEqual(self.failures(doc=fixed, kill=kill, i2=i2), [])

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


def r4_rows(doc):
    """The synthetic document's R4-table rows (the ledger row shares the prefix)."""
    return [l for l in doc.splitlines(keepends=True)
            if l.startswith(f"| `{mc.R4_CLAUSE}` |") and l.endswith(" | R4 |\n")]


class R4Table(Base):
    """interface/3 §I3a R4: one row per (clause, item) R4 changed, each value
    the artifacts', and no row outside R4 reach."""

    def test_skeleton_prints_the_r4_header_and_every_row(self):
        sk = mc.skeleton(self.regions, self.kill, self.shas)
        self.assertIn("| clause | item | interface/2 | interface/3 | rule |\n|---|---|---|---|---|\n",
                      sk)
        want = mc.r4_expected(self.regions, self.kill)
        self.assertEqual(len(r4_rows(sk)), len(want))
        items = [r[1] for r in want]
        self.assertIn("scope", items)
        self.assertTrue(any(i.startswith("mark ") for i in items))
        self.assertTrue(any(i in mc.CONDITIONS for i in items))
        self.assertEqual({r[0] for r in want}, {mc.R4_CLAUSE})

    def test_r4_values_are_the_renderers(self):
        for clause, item, was, now, rule in mc.r4_expected(self.regions, self.kill):
            line_ = next(l for l in r4_rows(self.doc) if f"| {item} |" in l)
            self.assertIn(f"| `{was}` | `{now}` | {rule} |", line_)
            self.assertEqual(rule, "R4")

    def test_each_missing_row_fails(self):
        for row in r4_rows(self.doc):
            with self.subTest(row=row):
                self.assertFails(f"the R4 table omits clause {mc.R4_CLAUSE} item",
                                 doc=self.doc.replace(row, ""))

    def test_missing_clause_fails(self):
        doc = "".join(l for l in self.doc.splitlines(keepends=True)
                      if l not in r4_rows(self.doc))
        self.assertFails(f"the R4 table omits clause {mc.R4_CLAUSE}", doc=doc)

    def test_duplicate_row_fails(self):
        row = r4_rows(self.doc)[0]
        self.assertFails("2 times; exactly once", doc=self.doc.replace(row, row + row))

    def test_each_misstated_value_fails(self):
        for row in r4_rows(self.doc):
            for col, name in ((3, "interface/2"), (4, "interface/3"), (5, "rule")):
                with self.subTest(row=row, column=name):
                    cells = row.split("|")
                    cells[col] = " `misstated` "
                    self.assertFails(f"{name} 'misstated', artifacts",
                                     doc=self.doc.replace(row, "|".join(cells)))

    def test_row_r4_did_not_change_fails(self):
        row = r4_rows(self.doc)[0]
        extra = f"| `{mc.R4_CLAUSE}` | K7 | `{PASS}` | `{PASS}` | R4 |\n"
        self.assertFails(f"clause {mc.R4_CLAUSE} item K7, which R4 did not change",
                         doc=self.doc.replace(row, row + extra))

    def test_row_outside_r4_reach_fails(self):
        doc, regions, kill, shas, i2, needle = mc.rigs()[
            "an R4-table row for a clause outside R4 reach"]
        self.assertFails(needle, doc=doc)
        self.assertNotIn("rig:0:0:0", mc._ignored_clauses(self.regions))

    def test_kept_label_is_outside_r4_reach(self):
        regions = copy.deepcopy(self.regions)
        rec = next(c for c in regions["clauses"] if c["address"]["id"] == mc.R4_CLAUSE)
        rec["r4_label"]["effect"] = "kept"
        self.assertNotIn(mc.R4_CLAUSE, mc._ignored_clauses(regions))

    def test_missing_r4_table_fails(self):
        head = mc._row(mc.R4_HEAD)
        self.assertFails("0 tables headed | clause | item |",
                         doc=self.doc.replace(head, head.replace("item", "change")))

    def test_contracted_r4_rigs_fail(self):
        for name in ("a document whose R4 section misses one R4-changed clause",
                     "a document misstating one interface/2 value in its R4 section",
                     "an R4-off outcome that differs from the interface/2 review's "
                     "ledger row",
                     "an R4-table row for a clause outside R4 reach"):
            with self.subTest(rig=name):
                doc, regions, kill, shas, i2, needle = mc.rigs()[name]
                self.assertFails(needle, doc=doc, regions=regions, kill=kill, shas=shas,
                                 i2=i2)


class R4OffLedger(Base):
    """kill.json's R4-off K1-K7 outcomes equal the interface/2 review's
    section 6 ledger row, per clause."""

    def i2_row(self, clause="rig:0:0:0"):
        return line(self.i2, f"| `{clause}` |")

    def test_clean_r4_off_matches(self):
        self.assertEqual(mc.r4_off_failures(self.i2, self.kill), [])

    def test_rigged_kill_r4_off_outcome_fails(self):
        kill = mc._r4_off_rigged(self.kill)
        self.assertFails(f"R4-off K1 of clause {mc.R4_CLAUSE} census exile#1: kill.json",
                         kill=kill)

    def test_each_rigged_ledger_cell_fails(self):
        for clause in ("rig:0:0:0", "rig:0:0:1", mc.R4_CLAUSE):
            for k in mc.CONDITIONS:
                with self.subTest(clause=clause, condition=k):
                    row = self.i2_row(clause)
                    cells = row.split("|")
                    col = 5 + mc.CONDITIONS.index(k)
                    cells[col] = f" {KILL if cells[col].strip() != KILL else PASS} "
                    self.assertFails(f"R4-off {k} of clause {clause}",
                                     i2=self.i2.replace(row, "|".join(cells)))

    def test_ledger_missing_a_clause_fails(self):
        self.assertFails("the interface/2 ledger has 0 rows for clause rig:0:0:1",
                         i2=self.i2.replace(self.i2_row("rig:0:0:1"), ""))

    def test_ledger_foreign_row_fails(self):
        row = self.i2_row()
        self.assertFails("the interface/2 ledger lists rig:0:0:9",
                         i2=self.i2.replace(row, row + row.replace("rig:0:0:0",
                                                                   "rig:0:0:9")))

    def test_ledger_outside_section_6_is_not_read(self):
        moved = self.i2.replace("## 6. Coverage ledger", "## 5. Something else")
        self.assertFails("has 0 section 6", i2=moved)
        empty = self.i2.replace("## 7. Totals", "## 7. Totals\n\n" + "\n".join(
            l for l in self.i2.splitlines() if l.startswith("|")))
        sec6 = empty.split("## 7.")[0].replace(self.i2_row(), "")
        self.assertFails("0 rows for clause rig:0:0:0",
                         i2=sec6 + "## 7." + empty.split("## 7.")[1])

    def test_kill_row_without_r4_off_outcomes_fails(self):
        kill = copy.deepcopy(self.kill)
        del kill["clauses"][1]["r4_off_tests"]
        self.assertTrue(any("carries no R4-off outcomes" in b
                            for b in mc.r4_off_failures(self.i2, kill)))

    def test_interface2_review_read_only_at_its_blob(self):
        self.assertEqual(mc.git_blob(b""), "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391")
        self.assertIn("## 6. Coverage ledger", mc.read_i2_review())
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / mc.I2_REVIEW_REL).parent.mkdir(parents=True)
            (root / mc.I2_REVIEW_REL).write_bytes(
                (mc.ROOT / mc.I2_REVIEW_REL).read_bytes() + b"\nrigged\n")
            self.assertTrue(halts(lambda: mc.read_i2_review(root),
                                  "not the interface/2 review on record"))

    def test_default_document_is_the_interface3_review(self):
        self.assertEqual(mc.DOC_REL, "oracle_compiler/analysis/M04-H-REGION-REVIEW-I3.md")
        self.assertNotEqual(mc.DOC_REL, mc.I2_REVIEW_REL)


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
