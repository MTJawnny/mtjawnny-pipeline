"""M05-CHECK unit tests: the M05 read-document checker and the READING PROTOCOL.

Inline SYNTHETIC rows and documents only -- generic templating, no card, no
card name, no oracle_id of a real card and no Oracle text. Every negative
control the M05-CHECK unit lists is rigged here and must fail.

    python3 -m unittest tests.oracle_ingest.test_m05_check
"""
import contextlib
import copy
import hashlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "oracle_ingest"))

import m05_check as m            # noqa: E402

SHA = "a" * 64
OTHER_SHA = "b" * 64
PARA = "Untap target artifact. It gains flying until end of turn."
FACE = PARA + "\nThis artifact has vigilance."


def row(i, rule="E4", outcome="RESOLVED", cls="E4:it", phrase="it", role=None,
        endpoint_text="Untap target artifact."):
    return {"row_id": f"00000000-0000-4000-8000-{i:012d}:0:0:1@0:{phrase}",
            "rule": rule, "outcome": outcome, "class": cls, "phrase": phrase,
            "fixture_role": role, "paragraph_text": PARA, "endpoint_text": endpoint_text,
            "face_text": FACE}


def counts_of(cells):
    return {"rows": len(cells), "endpoint-no": sum(c[0] == "no" for c in cells),
            "kind-no": sum(c[1] == "no" for c in cells),
            "duplicate-no": sum(c[2] == "no" for c in cells),
            "cannot-judge": sum("cannot-judge" in c for c in cells)}


def vline(label, word, counts, text="read in full"):
    return (f"- {label}: {word} (" + ", ".join(f"{k} {counts[k]}" for k in m.COUNTS)
            + f"); {text}")


def doc(label, rows, cells=None, sha=SHA, word=None, counts=None, verdict=None,
        notes=None, extra="", failing=None, captain="## Captain questions\n\nNone yet.\n"):
    """A well-formed synthetic read document; every part can be overridden."""
    cells = cells or [("yes", "yes", "yes")] * len(rows)
    lines = ["# M05 synthetic read", "", f"refs.json sha256: {sha}", "",
             "| row | class | endpoint | kind | duplicate | note |", "|---|---|---|---|---|---|"]
    for k, (r, c) in enumerate(zip(rows, cells)):
        note = (notes or {}).get(k)
        if note is None:
            note = '"target artifact" is the mark'
            if "no" in c or "cannot-judge" in c:
                note += ", but the reader found a second candidate"
        cls = r["class"] if r["class"] is not None else "none"
        lines.append(f"| {r['row_id']} | {cls} | {c[0]} | {c[1]} | {c[2]} | {note} |")
    cnt = counts or counts_of(cells)
    w = word or m.verdict_of(counts_of(cells))
    lines += ["", "## Verdict", "", verdict if verdict is not None else vline(label, w, cnt), ""]
    if w == m.FAIL and failing is None:
        bad = [(r, c) for r, c in zip(rows, cells) if c[0] == "no"]
        failing = "\n".join(f"- {r['class'] or 'none'}: {r['row_id']}" for r, _ in bad)
    if failing:
        lines += ["## Failing classes", "", failing, ""]
    lines += [captain, extra]
    return "\n".join(lines)


ROWS = [row(i) for i in range(1, 5)]
LABEL = "E4/P1"


def fails(text, rows=ROWS, sha=SHA, label=LABEL):
    return m.document_failures(text, rows, sha, label)


class Protocol(unittest.TestCase):

    def test_sha256(self):
        self.assertEqual(hashlib.sha256(m.PROTOCOL.encode("utf-8")).hexdigest(),
                         "66e13172e565b21189008995b936a1b5a931dff205ae2f794bca04eb57835873")
        self.assertEqual(m.PROTOCOL_SHA256, hashlib.sha256(m.PROTOCOL.encode()).hexdigest())

    def test_protocol_flag_prints_it_without_a_trailing_newline(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(m.main(["--protocol"]), 0)
        self.assertEqual(out.getvalue(), m.PROTOCOL)
        self.assertFalse(out.getvalue().endswith("\n"))
        p = subprocess.run([sys.executable, str(ROOT / m.SCRIPT), "--protocol"],
                           capture_output=True)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(hashlib.sha256(p.stdout).hexdigest(), m.PROTOCOL_SHA256)

    def test_protocol_binds_the_checker(self):
        self.assertIn("P is E1 4, E2 4, E3 2, E4 5, E5 1", m.PROTOCOL)
        self.assertEqual(m.PARTS, {"E1": 4, "E2": 4, "E3": 2, "E4": 5, "E5": 1})
        self.assertIn("| " + " | ".join(m.LEDGER_HEAD) + " |", m.PROTOCOL)
        for role in m.FIXTURE_ROLES:
            self.assertIn(role, "delayed-return-same-object, prior-set-complement-reference, "
                                "replacement-event-lineage, "
                                "ability-borrowing-inheritance-pressure, "
                                "two-sequential-operations")


class ReadSet(unittest.TestCase):

    def setUp(self):
        self.rows = ([row(i, "E1", "RESOLVED", f"E1:{h}", "this way")
                      for i, h in zip(range(10), "exile draw exile cast mill exile draw "
                                                 "cast exile reveal".split())]
                     + [row(20, "E1", "UNRESOLVED", None, "this way"),
                        row(21, "E5", "NOT-COREFERENCE", "E5", "the same"),
                        row(22, "E5", "UNRESOLVED", "E5", "the same"),
                        row(23, "E4", "UNRESOLVED", None, "it", role=m.FIXTURE_ROLES[0]),
                        row(24, "E4", "RESOLVED", "E4:it", "it", role=m.FIXTURE_ROLES[4]),
                        row(25, "E4", "RESOLVED", "E4:it", "it", role="some-other-role")])

    def test_rule_rows_sorted_by_class_then_row_id(self):
        got = m.rule_rows(self.rows, "E1")
        self.assertEqual(len(got), 10)
        self.assertEqual([r["class"] for r in got], sorted(r["class"] for r in got))
        self.assertEqual(got, sorted(got, key=lambda r: (r["class"], r["row_id"])))
        self.assertEqual([r["row_id"] for r in m.rule_rows(self.rows, "E5")],
                         [self.rows[11]["row_id"]])

    def test_parts_are_contiguous_floor_slices(self):
        rr = m.rule_rows(self.rows, "E1")
        parts = [m.part_rows(self.rows, "E1", k) for k in range(1, 5)]
        self.assertEqual([len(p) for p in parts], [2, 3, 2, 3])        # n = 10, P = 4
        self.assertEqual([r for p in parts for r in p], rr)
        self.assertEqual(m.part_rows(self.rows, "E5", 1), m.rule_rows(self.rows, "E5"))
        for bad in (0, 5):
            with self.assertRaises(ValueError):
                m.part_rows(self.rows, "E1", bad)

    def test_fixture_rows_every_outcome_in_the_five_roles(self):
        got = m.fixture_rows(self.rows)
        self.assertEqual([r["row_id"] for r in got],
                         [self.rows[13]["row_id"], self.rows[14]["row_id"]])  # null first

    def test_skeleton(self):
        sk = m.skeleton(m.fixture_rows(self.rows), SHA)
        self.assertIn(f"refs.json sha256: {SHA}", sk)
        self.assertIn(f"| {self.rows[13]['row_id']} | none |  |  |  |  |", sk)

    def test_verdict_precedence(self):
        c = {"rows": 20, "endpoint-no": 0, "kind-no": 3, "duplicate-no": 2, "cannot-judge": 1}
        self.assertEqual(m.verdict_of(c), m.PASS)               # 1 x 20 = 20, not > 20
        self.assertEqual(m.verdict_of(dict(c, **{"cannot-judge": 2})), m.INCONCLUSIVE)
        self.assertEqual(m.verdict_of(dict(c, **{"endpoint-no": 1, "cannot-judge": 9})),
                         m.FAIL)


class Document(unittest.TestCase):

    def ok(self, text, **kw):
        self.assertEqual(fails(text, **kw), [])

    def bad(self, text, *needles, **kw):
        got = fails(text, **kw)
        self.assertTrue(got, "the rigged document passed")
        for nd in needles:
            self.assertTrue(any(nd in b for b in got), (nd, got))
        return got

    # -- well-formed documents
    def test_valid_pass(self):
        self.ok(doc(LABEL, ROWS))

    def test_valid_fail_and_inconclusive(self):
        self.ok(doc(LABEL, ROWS, cells=[("no", "yes", "yes")] + [("yes",) * 3] * 3))
        self.ok(doc(LABEL, ROWS, cells=[("yes", "cannot-judge", "yes")] + [("yes",) * 3] * 3))
        self.ok(doc(LABEL, ROWS, cells=[("yes", "no", "no")] + [("yes",) * 3] * 3))

    def test_label_read_from_the_canonical_line(self):
        self.assertEqual(m.document_failures(doc(LABEL, ROWS), ROWS, SHA), [])

    def test_fixture_document(self):
        rows = [row(1, cls=None, role=m.FIXTURE_ROLES[0]),
                row(2, rule="E1", cls="E1:exile", phrase="this way", role=m.FIXTURE_ROLES[2])]
        self.ok(doc("FIXTURES", rows), rows=rows, label="FIXTURES")
        self.bad(doc("FIXTURES", rows).replace("- FIXTURES:", "- E4/P1:"), "FIXTURES",
                 rows=rows, label="FIXTURES")

    def test_class_lists_are_accepted(self):
        self.ok(doc(LABEL, ROWS, extra="- E4:it is the only class here.\n"))
        self.ok(doc(LABEL, ROWS, extra=f"Row {ROWS[0]['row_id']} was read twice.\n"))
        self.ok(doc(LABEL, ROWS, extra="| question | answer |\n|---|---|\n| why | because |\n"))

    # -- the literal ledger (repair round 1, verdict 6051200664)
    def test_ledger_header_is_literal(self):
        head = "| row | class | endpoint | kind | duplicate | note |"
        for other in ("| `row` | class | endpoint | kind | duplicate | note |",
                      "| row | `class` | endpoint | kind | duplicate | note |",
                      "| **row** | class | endpoint | kind | duplicate | note |",
                      "| Row | class | endpoint | kind | duplicate | note |",
                      "|row|class|endpoint|kind|duplicate|note|",
                      "| row | class | endpoint | kind | duplicate | note | ",
                      " " + head):
            self.bad(doc(LABEL, ROWS).replace(head, other), "ledger header")

    def test_row_class_and_verdict_cells_are_literal(self):
        rid = ROWS[0]["row_id"]
        self.bad(doc(LABEL, ROWS).replace(f"| {rid} |", f"| `{rid}` |"), "markup", "omits row")
        self.bad(doc(LABEL, ROWS).replace(f"| {rid} |", f"| **{rid}** |"), "markup")
        self.bad(doc(LABEL, ROWS).replace(f"{rid} | E4:it |", f"{rid} | `E4:it` |"), "class")
        for w in ("`yes`", "`no`", "`cannot-judge`", "**yes**", "_yes_"):
            self.bad(doc(LABEL, ROWS, cells=[(w, "yes", "yes")] + [("yes",) * 3] * 3),
                     "not exactly yes, no or cannot-judge")
            self.bad(doc(LABEL, ROWS, cells=[("yes", "yes", w)] + [("yes",) * 3] * 3),
                     "not exactly yes, no or cannot-judge")
        rows = [row(1, cls=None)] + ROWS[1:]
        self.bad(doc(LABEL, rows).replace("| none |", "| `none` |"), "written none", rows=rows)

    def test_detached_duplicate_row_after_a_blank_line(self):
        # The reviewer's case: an endpoint-no duplicate after a blank line beside
        # a canonical PASS verdict.
        rid = ROWS[1]["row_id"]
        dup = f'| {rid} | E4:it | no | yes | yes | "target artifact" is wrong, says the reader |'
        lines = doc(LABEL, ROWS).split("\n")
        i = next(k for k, l in enumerate(lines) if l.startswith(f"| {ROWS[-1]['row_id']}"))
        for gap in ([""], ["", "Some prose."], ["", "## Notes", ""]):
            text = "\n".join(lines[:i + 1] + gap + [dup] + lines[i + 1:])
            n = text.split("\n").index(dup) + 1
            self.bad(text, f"line {n}: a ledger row outside the ledger table")

    def test_row_shaped_lines_elsewhere(self):
        rid = ROWS[0]["row_id"]
        addr = rid.split("@")[0]
        for extra in (f"| {rid} | E4:it | no | yes | yes | x |\n",
                      f"| question | answer |\n|---|---|\n| {rid} | no |\n",
                      f"```\n| {rid} | E4:it | no | yes | yes | x |\n```\n",
                      f"> | {rid} | E4:it | no | yes | yes | x |\n",
                      f"{rid} | E4:it | no | yes | yes | x\n",
                      f"| `{addr}@0:it` | no |\n"):
            self.bad(doc(LABEL, ROWS, extra=extra), "outside the ledger table")

    def test_orphan_table_lines(self):
        for extra in ("| stray | cells |\n", "| a | b |\n| c | d |\n", "|---|---|\n"):
            self.bad(doc(LABEL, ROWS, extra=extra), "belongs to no table")

    def test_second_ledger_table(self):
        lines = doc(LABEL, ROWS).split("\n")
        i = lines.index("| row | class | endpoint | kind | duplicate | note |")
        self.bad(doc(LABEL, ROWS, extra="\n".join(lines[i:i + 2 + len(ROWS)]) + "\n"),
                 "2 tables headed")
        self.bad(doc(LABEL, ROWS, extra="| `row` | class | endpoint | kind | duplicate | note |"
                                        "\n|---|---|---|---|---|---|\n"), "2 tables headed")

    # -- strict table shape (repair round 2, verdict 6051464818)
    def test_extra_empty_boundary_cells(self):
        rid = ROWS[0]["row_id"]
        line = next(l for l in doc(LABEL, ROWS).split("\n") if l.startswith(f"| {rid} |"))
        for other in ("|" + line, line + "|", "||" + line[1:], line[:-1] + "||",
                      "| " + line, line + " |"):
            self.bad(doc(LABEL, ROWS).replace(line, other), "7 cells, not 6")
        head = "| row | class | endpoint | kind | duplicate | note |"
        for other in ("|" + head, head + "|", head + " |"):
            self.bad(doc(LABEL, ROWS).replace(head, other), "0 tables headed")

    def test_empty_cells_are_kept(self):
        self.assertEqual(m._split("|| a |"), ["", "a"])
        self.assertEqual(m._split("| a || b |"), ["a", "", "b"])
        self.assertEqual(m._split("| a | b |"), ["a", "b"])
        self.assertEqual(m._split("|a|b|"), ["a", "b"])
        self.assertEqual(m._split("| a |  |"), ["a", ""])

    def test_separator_width_equals_the_header(self):
        sep = "|---|---|---|---|---|---|"
        for other in ("|---|", "|---|---|---|---|---|", "|---|---|---|---|---|---|---|",
                      "|---||---|---|---|---|---|"):
            got = self.bad(doc(LABEL, ROWS).replace(sep, other), "0 tables headed")
            if "||" not in other:
                n = other.count("|") - 1
                self.assertTrue(any(f"separator row under the ledger header has {n} cells"
                                    in b for b in got), got)
        found, orphans = m.tables(["| a | b |", "|---|", "| c | d |"], [False] * 3)
        self.assertEqual(found, [])
        self.assertEqual([n for n, _ in orphans], [1, 2, 3])
        found, _ = m.tables(["| a | b |", "|---|:---:|", "| c | d |"], [False] * 3)
        self.assertEqual(len(found), 1)
        self.bad(doc(LABEL, ROWS, extra="| question | answer |\n|---|\n| why | because |\n"),
                 "belongs to no table")

    # -- rows
    def test_missing_row(self):
        text = "\n".join(l for l in doc(LABEL, ROWS).split("\n")
                         if not l.startswith(f"| {ROWS[2]['row_id']}"))
        self.bad(text, "omits row " + ROWS[2]["row_id"])

    def test_duplicate_row(self):
        lines = doc(LABEL, ROWS).split("\n")
        i = next(k for k, l in enumerate(lines) if l.startswith(f"| {ROWS[1]['row_id']}"))
        lines.insert(i + 1, lines[i])
        self.bad("\n".join(lines), "appears 2 times")

    def test_foreign_row(self):
        foreign = row(99)
        text = doc(LABEL, ROWS + [foreign])
        self.bad(text, "foreign row")

    def test_order(self):
        self.bad(doc(LABEL, list(reversed(ROWS))), "skeleton order")

    def test_class_must_equal_refs(self):
        self.bad(doc(LABEL, ROWS).replace(f"{ROWS[0]['row_id']} | E4:it",
                                          f"{ROWS[0]['row_id']} | E4:that card"), "class")

    def test_null_class_written_other_than_none(self):
        rows = [row(1, cls=None)] + ROWS[1:]
        self.ok(doc(LABEL, rows), rows=rows)
        for other in ("null", "None", "", "-", "n/a"):
            text = doc(LABEL, rows).replace(f"{rows[0]['row_id']} | none |",
                                            f"{rows[0]['row_id']} | {other} |")
            self.bad(text, "written none", rows=rows)

    # -- cells
    def test_verdict_cell_words(self):
        for w in ("Yes", "maybe", "y", "cannot judge", "n/a", ""):
            self.bad(doc(LABEL, ROWS, cells=[(w, "yes", "yes")] + [("yes",) * 3] * 3),
                     "not exactly yes, no or cannot-judge")

    # -- notes
    def test_note_without_a_quote(self):
        self.bad(doc(LABEL, ROWS, notes={0: "the mark is the target artifact"}),
                 "quotes no phrase")

    def test_note_quote_not_in_the_row_texts(self):
        self.bad(doc(LABEL, ROWS, notes={0: '"target enchantment" is the mark'}),
                 "found verbatim")

    def test_note_quote_from_each_text(self):
        for q in ("It gains flying", "Untap target artifact.", "has vigilance"):
            self.ok(doc(LABEL, ROWS, notes={0: f'"{q}" is the evidence'}))

    def test_note_quote_over_twelve_words(self):
        long = "Untap target artifact. It gains flying until end of turn. This artifact"
        rows = [dict(ROWS[0], face_text=FACE + " " + long)] + ROWS[1:]
        self.bad(doc(LABEL, rows, notes={0: f'"{long} has" read'}), "at most 12",
                 rows=rows)

    def test_no_or_cannot_judge_needs_a_reason(self):
        for c in (("no", "yes", "yes"), ("yes", "cannot-judge", "yes"), ("yes", "yes", "no")):
            self.bad(doc(LABEL, ROWS, cells=[c] + [("yes",) * 3] * 3,
                         notes={0: '"target artifact"'}), "reason")

    # -- the verdict line
    def test_pass_with_endpoint_no(self):
        cells = [("no", "yes", "yes")] + [("yes",) * 3] * 3
        self.bad(doc(LABEL, ROWS, cells=cells, word=m.PASS, failing="- E4:it: x"),
                 "precedence")

    def test_count_differing_from_the_ledger(self):
        for k in m.COUNTS:
            c = dict(counts_of([("yes",) * 3] * 4))
            c[k] += 1
            self.bad(doc(LABEL, ROWS, counts=c), f"states {k}")

    def test_pass_with_too_many_cannot_judge(self):
        cells = [("yes", "cannot-judge", "yes")] + [("yes",) * 3] * 3      # 1 x 20 > 4
        self.bad(doc(LABEL, ROWS, cells=cells, word=m.PASS), "precedence")
        rows = [row(i) for i in range(20)]
        cells = [("cannot-judge", "yes", "yes")] + [("yes",) * 3] * 19      # 20 = 20
        self.ok(doc(LABEL, rows, cells=cells, word=m.PASS), rows=rows)

    def test_inconclusive_where_pass_is_due(self):
        self.bad(doc(LABEL, ROWS, word=m.INCONCLUSIVE), "precedence")

    def test_non_canonical_verdict_lines(self):
        good = vline(LABEL, m.PASS, counts_of([("yes",) * 3] * 4))
        for bad in (good.replace("; read in full", ""), good.replace("- ", "* ", 1),
                    "  " + good, good.replace("PASS", "pass"), good.replace("(rows", "(Rows"),
                    "- **E4/P1**: PASS", good.replace("- E4/P1:", "- E4/P1 :")):
            self.bad(doc(LABEL, ROWS, verdict=bad), "")

    def test_missing_verdict_section(self):
        self.bad(doc(LABEL, ROWS).replace("## Verdict", "## Result"), "## Verdict")

    def test_failing_classes(self):
        cells = [("no", "yes", "yes")] + [("yes",) * 3] * 3
        self.bad(doc(LABEL, ROWS, cells=cells, failing="- nothing listed"),
                 "failing class E4:it", "failing row")
        text = doc(LABEL, ROWS, cells=cells).replace("## Failing classes", "## Failures")
        self.bad(text, "Failing classes")

    def test_captain_questions_heading(self):
        self.bad(doc(LABEL, ROWS, captain=""), "Captain questions")
        self.bad(doc(LABEL, ROWS, extra="## Captain questions\n"), "Captain questions")

    # -- sha256
    def test_wrong_sha(self):
        self.bad(doc(LABEL, ROWS, sha=OTHER_SHA), "verified refs.json")

    def test_sha_line_count_and_form(self):
        self.bad(doc(LABEL, ROWS, extra=f"refs.json sha256: {SHA}\n"), "exactly one")
        self.bad(doc(LABEL, ROWS).replace(f"refs.json sha256: {SHA}",
                                          f"refs.json sha256: `{SHA}`"), "")
        self.bad(doc(LABEL, ROWS).replace(f"refs.json sha256: {SHA}", ""), "exactly one")

    # -- threat model (A), (A3)
    def test_html_and_comment_markers_name_the_line(self):
        for marker in ("<!-- hidden -->", "-->", "<b>bold", "</p>", "<!DOCTYPE"):
            text = doc(LABEL, ROWS, extra=f"Note {marker} here.\n")
            n = text.split("\n").index(f"Note {marker} here.") + 1
            self.bad(text, f"line {n} contains")

    def test_link_entity_backslash_markers_name_the_line(self):
        for marker in ("[see](x)", "[x]: y", "a & b", "a \\ b", "&amp;"):
            text = doc(LABEL, ROWS, extra=f"Note {marker} here.\n")
            n = text.split("\n").index(f"Note {marker} here.") + 1
            self.bad(text, f"line {n} contains")

    def test_markers_in_a_table_cell_or_fence(self):
        self.bad(doc(LABEL, ROWS, notes={0: '"target artifact" & more'}), "line 7 contains")
        self.bad(doc(LABEL, ROWS, extra="```\n<!-- x -->\n```\n"), "contains")

    # -- threat model (A2)
    def test_second_contradictory_verdict_anywhere(self):
        for where in ("The reader thinks E4/P1: FAIL overall.",
                      "E4/P1 -- INCONCLUSIVE",
                      "E4 -- FAIL",
                      "```\n- E4/P1: FAIL (rows 4, endpoint-no 0, kind-no 0, duplicate-no 0, "
                      "cannot-judge 0); x\n```",
                      "> - E4/P1: FAIL (rows 4, endpoint-no 0, kind-no 0, duplicate-no 0, "
                      "cannot-judge 0); x",
                      "E4/P1\n: FAIL"):
            self.bad(doc(LABEL, ROWS, extra=where + "\n"), "")

    def test_second_identical_verdict_line_elsewhere(self):
        good = vline(LABEL, m.PASS, counts_of([("yes",) * 3] * 4))
        self.bad(doc(LABEL, ROWS, extra=good + "\n"), "")
        self.bad(doc(LABEL, ROWS, verdict=good + "\n" + good), "second verdict line")

    def test_agreeing_mention_is_allowed(self):
        self.ok(doc(LABEL, ROWS, extra="As stated, E4/P1: PASS.\n"))

    def test_other_rule_part_or_fixtures_label(self):
        for other in ("E2 PASS", "E4/P3: PASS", "FIXTURES: PASS", "e1 -- pass"):
            self.bad(doc(LABEL, ROWS, extra=f"Also {other}.\n"), "carries no verdict")

    def test_row_address_with_a_contradicting_word(self):
        rid = ROWS[0]["row_id"]
        self.bad(doc(LABEL, ROWS, extra=f"Row {rid}: FAIL\n"), "row address")
        addr = rid.split("@")[0]
        self.bad(doc(LABEL, ROWS, extra=f"Row {addr} - FAIL\n"), "row address")
        self.ok(doc(LABEL, ROWS, extra=f"Row {rid}: PASS\n"))


def part(label, rows, cells=None, sha=SHA):
    text = doc(label, rows, cells=cells, sha=sha)
    return m.parse_document(text, rows, label)


class Aggregate(unittest.TestCase):

    def setUp(self):
        self.rows = [row(i, "E3", "RESOLVED", "E3", "the copy") for i in range(7)]
        self.p1 = m.part_rows(self.rows, "E3", 1)
        self.p2 = m.part_rows(self.rows, "E3", 2)

    def test_partition_and_sum(self):
        parts = [part("E3/P1", self.p1), part("E3/P2", self.p2,
                                             cells=[("yes", "no", "yes")] * len(self.p2))]
        bad, agg = m.rule_failures(parts, self.rows, "E3")
        self.assertEqual(bad, [])
        self.assertEqual(agg["counts"], {"rows": 7, "endpoint-no": 0, "kind-no": 4,
                                         "duplicate-no": 0, "cannot-judge": 0})
        self.assertEqual(agg["word"], m.PASS)
        self.assertEqual(m.rule_line("E3", agg),
                         "- E3: PASS (rows 7, endpoint-no 0, kind-no 4, duplicate-no 0, "
                         "cannot-judge 0)")

    def test_rule_verdict_uses_the_same_precedence(self):
        p2 = part("E3/P2", self.p2, cells=[("no", "yes", "yes")] + [("yes",) * 3] * 3)
        self.assertEqual(m.aggregate([part("E3/P1", self.p1), p2])["word"], m.FAIL)
        p2 = part("E3/P2", self.p2, cells=[("cannot-judge", "yes", "yes")] + [("yes",) * 3] * 3)
        self.assertEqual(m.aggregate([part("E3/P1", self.p1), p2])["word"], m.INCONCLUSIVE)

    def test_overlapping_parts(self):
        bad, _ = m.rule_failures([part("E3/P1", self.p1 + self.p2[:1]),
                                  part("E3/P2", self.p2)], self.rows, "E3")
        self.assertTrue(any("must not overlap" in b for b in bad), bad)

    def test_parts_missing_a_row(self):
        bad, _ = m.rule_failures([part("E3/P1", self.p1), part("E3/P2", self.p2[1:])],
                                 self.rows, "E3")
        self.assertTrue(any("no part reads" in b for b in bad), bad)

    def test_missing_part(self):
        bad, _ = m.rule_failures([part("E3/P1", self.p1)], self.rows, "E3")
        self.assertTrue(any("needs exactly" in b for b in bad), bad)

    def test_two_sha_values(self):
        bad, _ = m.rule_failures([part("E3/P1", self.p1),
                                  part("E3/P2", self.p2, sha=OTHER_SHA)], self.rows, "E3")
        self.assertTrue(any("2 refs.json sha256 values" in b for b in bad), bad)


def aggs(sha=SHA):
    out = {}
    for label in list(m.PARTS) + ["FIXTURES"]:
        c = {"rows": 10, "endpoint-no": 0, "kind-no": 1, "duplicate-no": 0, "cannot-judge": 0}
        out[label] = {"counts": c, "word": m.PASS, "sha": sha, "failures": [],
                      "parts": [{"label": f"{label}/P1", "word": m.PASS}]
                      if label != "FIXTURES" else []}
    return out


def summary(a, sha=SHA, extra=""):
    lines = ["# M05 summary", "", f"refs.json sha256: {sha}", "", "## Verdict", ""]
    lines += [vline(k, v["word"], v["counts"], "summed") for k, v in a.items()]
    return "\n".join(lines + ["", "## Captain questions", "", "None yet.", extra])


class Summary(unittest.TestCase):

    def test_valid(self):
        self.assertEqual(m.summary_failures(summary(aggs()), aggs(), SHA), [])

    def test_count_and_word_must_equal_the_aggregate(self):
        a = aggs()
        rigged = copy.deepcopy(a)
        rigged["E2"]["counts"]["kind-no"] = 2
        self.assertTrue(m.summary_failures(summary(rigged), a, SHA))
        rigged = copy.deepcopy(a)
        rigged["E4"]["word"] = m.INCONCLUSIVE
        self.assertTrue(m.summary_failures(summary(rigged), a, SHA))

    def test_every_label_once(self):
        a = aggs()
        text = "\n".join(l for l in summary(a).split("\n") if not l.startswith("- E3:"))
        self.assertTrue(any("E3" in b for b in m.summary_failures(text, a, SHA)))
        text = summary(a, extra=vline("E1", m.PASS, a["E1"]["counts"]) + "\n")
        self.assertTrue(m.summary_failures(text, a, SHA))

    def test_two_sha_values(self):
        a = aggs(sha=OTHER_SHA)
        got = m.summary_failures(summary(a, sha=SHA), a, SHA)
        self.assertTrue(any("cite the same" in b or "every document" in b for b in got), got)
        got = m.summary_failures(summary(aggs(), sha=OTHER_SHA), aggs(), SHA)
        self.assertTrue(any("verified refs.json" in b for b in got), got)

    def test_contradiction_and_markers(self):
        a = aggs()
        self.assertTrue(m.summary_failures(summary(a, extra="E2 -- FAIL\n"), a, SHA))
        self.assertTrue(m.summary_failures(summary(a, extra="E2/P1: FAIL\n"), a, SHA))
        self.assertTrue(m.summary_failures(summary(a, extra="a & b\n"), a, SHA))
        self.assertEqual(m.summary_failures(summary(a, extra="As read, E2/P1: PASS.\n"),
                                            a, SHA), [])
        self.assertTrue(m.summary_failures(summary(a, extra="E2/P1: PASS\n"), a, SHA))


class HandOff(unittest.TestCase):
    """refs.json is never trusted: --verify first (stale STOPs); a missing one
    is regenerated only by --check-determinism."""

    def proc(self, code):
        return subprocess.CompletedProcess([], code, b"", b"stale")

    def test_existing_is_verified_and_stale_stops(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / m.REFS_REL).parent.mkdir(parents=True)
            (root / m.REFS_REL).write_bytes(b"{}")
            calls = []
            sha = m.obtain(root, lambda a: calls.append(a[1:]) or self.proc(0))
            self.assertEqual(calls, [["--verify"]])
            self.assertEqual(sha, hashlib.sha256(b"{}").hexdigest())
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    m.obtain(root, lambda a: self.proc(1))

    def test_missing_is_regenerated_only_by_check_determinism(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            calls = []

            def run(a):
                calls.append(a[1:])
                if a[1:] == ["--check-determinism"]:
                    (root / m.REFS_REL).parent.mkdir(parents=True, exist_ok=True)
                    (root / m.REFS_REL).write_bytes(b"{}")
                return self.proc(0)
            m.obtain(root, run)
            self.assertEqual(calls, [["--check-determinism"], ["--verify"]])
        with tempfile.TemporaryDirectory() as d:
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    m.obtain(Path(d), lambda a: self.proc(0))


if __name__ == "__main__":
    unittest.main()
