"""A01-CHECK unit tests: the coverage and consistency checker for the three
Round-2 seam audit documents, with every contracted negative control -- a
ledger missing one member (or class), a non-member row, a cell outside the five
cell words, SUFFICES over a NOT-EXPRESSED cell, SUFFICES over all-UNRESOLVED
cells, a SUFFICES line citing AQ4 §16 without 'CANDIDATE benchmark structure',
a '## Reads' list missing a READ POSITION or whose count differs from 'read', a
split part with read 0, a pronoun note without a double-quoted antecedent, a
split whose parts do not partition the class, EXPRESSED A4 with read <
members, EXPRESSED A2 with read < members and one member's supports_A2 false,
a NOT-MEMBER pronoun row with a truth word, a wrong seams.json hash, a stale
seams.json (STOPs), and a document without '## Captain questions' -- and the
repair-round controls: a split part with no READ POSITION whose first member
(seams.json order) is not read, a hash attributed only to another
'*seams.json' (including 'unrelated+seams.json' and 'unrelated@seams.json'),
an audit whose structure sits inside a code fence; and (Captain decision
5987664829) every HTML or comment marker -- '<!--', '-->', '<' followed by an
ASCII letter, '/' or '!' -- failing on any line, code spans and fences
included, with every bypass of the retired HTML/comment handling as a
regression case; and (repair verdict 5988024375) a contradictory duplicate
verdict line in any non-canonical form (indented 1-3 spaces, quoted, another
list marker, an emphasised id) failing instead of being skipped; and (repair
verdict 5988156977) a link-wrapped id, nested list markers, counts wrapped
onto the next line, or a second verdict in a canonical line's tail failing.

Inline SYNTHETIC documents and a synthetic seams.json only -- generic
addresses, no card, no card name, no oracle_id and no Oracle text. Never reads
or writes experiments/out/: the hand-off rule is exercised on a temporary root
with a rigged producer runner.

    python3 -m unittest discover -s tests/oracle_ingest -t .
"""
import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "oracle_ingest"))

import a01_check as ac           # noqa: E402

SHA = ac.SYN_SHA


def line(doc, prefix):
    return next(l for l in doc.splitlines(keepends=True) if l.startswith(prefix))


def cells(row, k, value):
    c = row.split("|")
    c[k] = f" {value} "
    return "|".join(c)


class Base(unittest.TestCase):
    def setUp(self):
        self.seams = ac.synthetic_seams()
        self.docs = ac.synthetic_docs()

    def failures(self, seam, doc=None, seams=None, sha=SHA):
        return ac.document_failures(seam, self.docs[seam] if doc is None else doc,
                                    self.seams if seams is None else seams, sha)

    def assertFails(self, seam, needle, **kw):
        bad = self.failures(seam, **kw)
        self.assertTrue(any(needle in b for b in bad), f"{needle!r} not in {bad}")


class Clean(Base):
    def test_unrigged_documents_pass(self):
        for seam in ac.DOCS:
            self.assertEqual(self.failures(seam), [], seam)

    def test_in_script_negative_controls_hold(self):
        names = ac.negative_controls()
        self.assertEqual(len(names), 2 + len(ac.rigs()))
        self.assertIn("a rigged stale seams.json STOPs the checker", names)

    def test_every_rig_fails_with_its_needle(self):
        for name, (seam, doc, seams, sha, needle) in ac.rigs().items():
            with self.subTest(name):
                bad = ac.document_failures(seam, doc, seams, sha)
                self.assertTrue(any(needle in b for b in bad), f"{needle!r} not in {bad}")

    def test_synthetic_split_part_2_holds_no_read_position(self):
        deal = self.seams["seams"]["R2-A"]["classes"]["deal"]
        self.assertFalse(set(ac.DEAL_PART2) & set(deal["read"]))

    def test_checker_does_not_mutate_its_inputs(self):
        before = copy.deepcopy((self.seams, self.docs))
        for seam in ac.DOCS:
            self.failures(seam)
        self.assertEqual((self.seams, self.docs), before)

    def test_skeleton_fails_until_filled(self):
        for seam in ac.DOCS:
            sk = ac.skeleton(seam, self.seams, SHA)
            bad = self.failures(seam, doc=sk)
            self.assertTrue(bad)
            self.assertFalse([b for b in bad if "omits" in b or "cites" in b
                              or "READ POSITION" in b], bad)

    def test_seam_of(self):
        for seam, rel in ac.DOCS.items():
            self.assertEqual(ac.seam_of(rel), seam)
        self.assertEqual(ac.seam_of("x/A01-R2B-draft.md"), "R2-B")


class Hash(Base):
    def test_wrong_hash_fails(self):
        self.assertFails("R2-A", "does not cite the verified seams.json sha256",
                         sha="0" * 64)

    def test_hash_attributed_only_to_an_unrelated_seams_json_fails(self):
        for other in ("unrelated-seams.json", "other/seams.json", "a01/seams.json.bak",
                      "unrelated+seams.json", "unrelated@seams.json", "x~seams.json",
                      "unrelated=seams.json", "u#seams.json", "a01\\seams.json",
                      "_seams.json", "*seams.json", "[seams.json](other/seams.json)",
                      f"[seams.json]({ac.SEAMS_REL})x", "seams.json+x", "seams.json@x"):
            with self.subTest(other):
                doc = self.docs["R2-C"].replace("seams.json sha256", f"{other} sha256")
                self.assertFails("R2-C", "does not cite the verified seams.json sha256",
                                 doc=doc)

    def test_hash_on_a_line_also_naming_an_unrelated_seams_json_fails(self):
        doc = self.docs["R2-C"].replace("seams.json sha256",
                                        "seams.json (not unrelated-seams.json) sha256")
        self.assertFails("R2-C", "does not cite the verified seams.json sha256", doc=doc)

    def test_exact_artifact_references_pass(self):
        for ref in (ac.SEAMS_REL, f"`{ac.SEAMS_REL}`", "a01/seams.json", f"./{ac.SEAMS_REL}",
                    "seams.json's", "`seams.json`'s", "(seams.json),", "**seams.json**:",
                    "_seams.json_", f"[seams.json]({ac.SEAMS_REL})",
                    f"([`seams.json`]({ac.SEAMS_REL})).", "“seams.json”"):
            with self.subTest(ref):
                doc = self.docs["R2-C"].replace("seams.json sha256", f"{ref} sha256")
                self.assertEqual(self.failures("R2-C", doc=doc), [], ref)

    def test_hash_inside_a_code_fence_is_not_a_citation(self):
        cite = f"seams.json sha256 `{SHA}`"
        doc = self.docs["R2-C"].replace(cite, f"```\n{cite}\n```")
        self.assertFails("R2-C", "does not cite the verified seams.json sha256", doc=doc)

    def test_second_differing_hash_fails(self):
        doc = self.docs["R2-C"].replace(f"`{SHA}`", f"`{SHA}` (was seams.json "
                                        f"{'1' * 64})")
        self.assertFails("R2-C", f"cites seams.json sha256 {'1' * 64}", doc=doc)


class LedgerCoverage(Base):
    def test_missing_member_fails(self):
        for seam, addr in (("R2-B", "rig-b0:0:0:0"), ("R2-C", "rig-c1:0:1:0")):
            doc = self.docs[seam].replace(line(self.docs[seam], f"| `{addr}` |"), "")
            self.assertFails(seam, f"ledger omits member {addr}", doc=doc)

    def test_missing_class_fails(self):
        doc = self.docs["R2-A"].replace(line(self.docs["R2-A"], "| `draw` |"), "")
        self.assertFails("R2-A", "the R2-A ledger omits class 'draw'", doc=doc)

    def test_non_member_row_fails(self):
        d = self.docs["R2-C"]
        row = line(d, "| `rig-c0:0:0:0` |")
        doc = d.replace(row, row + row.replace("rig-c0", "rig-zz"))
        self.assertFails("R2-C", "lists rig-zz:0:0:0, which is not a seams.json member",
                         doc=doc)

    def test_non_class_row_fails(self):
        d = self.docs["R2-A"]
        row = line(d, "| `draw` |")
        self.assertFails("R2-A", "which is not a seams.json class",
                         doc=d.replace(row, row + row.replace("`draw`", "`fly`")))

    def test_duplicate_row_fails(self):
        d = self.docs["R2-C"]
        row = line(d, "| `rig-c0:0:0:0` |")
        self.assertFails("R2-C", "2 times; exactly once", doc=d.replace(row, row + row))

    def test_cell_outside_the_five_words_fails(self):
        d = self.docs["R2-B"]
        row = line(d, "| `rig-b0:0:0:0` |")
        self.assertFails("R2-B", "'SUFFICES' is not one of the five cell words",
                         doc=d.replace(row, cells(row, 2, "SUFFICES")))

    def test_wrong_header_fails(self):
        d = self.docs["R2-C"].replace("| clause | C1 |", "| clause | C-1 |")
        self.assertFails("R2-C", "0 tables headed | clause | C1", doc=d)

    def test_recall_table_must_cover_each_control(self):
        d = self.docs["R2-A"]
        self.assertFails("R2-A", "recall table omits recall control clause rig-d00:0:0:0",
                         doc=d.replace(line(d, "| `rig-d00:0:0:0` |"), ""))

    def test_recall_row_with_wrong_class_fails(self):
        d = self.docs["R2-A"]
        row = line(d, "| `rig-d00:0:0:0` |")
        self.assertFails("R2-A", "R2-A recall rig-d00:0:0:0: class 'deal'",
                         doc=d.replace(row, cells(row, 2, "deal")))


class ReadRule(Base):
    def setUp(self):
        super().setUp()
        self.a = self.docs["R2-A"]
        self.draw = line(self.a, "| `draw` |")
        self.pos = self.seams["seams"]["R2-A"]["classes"]["draw"]["read"]

    def test_expressed_a4_with_read_below_members_fails(self):
        self.assertFails("R2-A", "A4 EXPRESSED with read 10 of 12",
                         doc=self.a.replace(self.draw, cells(self.draw, 7, "EXPRESSED")))

    def test_expressed_a2_with_one_unsupported_member_fails(self):
        seams = copy.deepcopy(self.seams)
        seams["seams"]["R2-A"]["members"][3]["supports_A2"] = False
        self.assertFails("R2-A", "A2 EXPRESSED with read 10 of 12 and supports_A2 not "
                                 "true for 1 member(s) (rig-d03:0:0:0", seams=seams)

    def test_expressed_a2_with_every_member_read_needs_no_support(self):
        seams = copy.deepcopy(self.seams)
        for m in seams["seams"]["R2-A"]["members"]:
            if m["class"] == "no-would:if":
                m["supports_A2"] = False
        row = line(self.a, "| `no-would:if` |")
        a2 = line(self.a, "- A2:")
        doc = self.a.replace(row, cells(row, 5, "EXPRESSED")).replace(
            a2, a2.replace("EXPRESSED 1,", "EXPRESSED 2,").replace("UNRESOLVED 3",
                                                                    "UNRESOLVED 2"))
        self.assertEqual(self.failures("R2-A", doc=doc, seams=seams), [])

    def test_missing_inferred_note_fails(self):
        doc = self.a.replace(self.draw, self.draw.replace("inferred from 10 of 12 read",
                                                          "sampled"))
        self.assertFails("R2-A", "does not say 'inferred from 10 of 12 read'", doc=doc)

    def test_reads_missing_a_read_position_fails(self):
        doc = self.a.replace(f"- `{self.pos[3]}`\n", "- `rig-d03:0:0:0`\n", 1)
        self.assertFails("R2-A", f"READ POSITION {self.pos[3]} is not listed", doc=doc)

    def test_reads_count_differs_from_read_fails(self):
        doc = self.a.replace(f"- `{self.pos[3]}`\n",
                             f"- `{self.pos[3]}`\n- `rig-d03:0:0:0`\n", 1)
        self.assertFails("R2-A", "R2-A row draw: read '10', but '## Reads' lists 11",
                         doc=doc)

    def test_extra_read_listed_and_counted_passes(self):
        doc = self.a.replace(f"- `{self.pos[3]}`\n",
                             f"- `{self.pos[3]}`\n- `rig-d03:0:0:0`\n", 1).replace(
            self.draw, cells(self.draw, 3, "11").replace("10 of 12", "11 of 12"))
        self.assertEqual(self.failures("R2-A", doc=doc), [])

    def test_read_of_a_non_member_of_the_row_fails(self):
        head, reads = self.a.split("## Reads\n")
        doc = head + "## Reads\n" + reads.replace("### deal/part-2\n\n- `rig-e02:0:0:0`",
                                                  "### deal/part-2\n\n- `rig-e00:0:0:0`")
        self.assertFails("R2-A", "lists rig-e00:0:0:0, which is not a member of that row",
                         doc=doc)

    def test_split_part_with_read_zero_fails(self):
        p2 = line(self.a, "| `deal/part-2` |")
        doc = self.a.replace("### deal/part-2\n\n- `rig-e02:0:0:0`\n", "### deal/part-2\n")
        doc = doc.replace(p2, cells(p2, 3, "0").replace("1 of 3", "0 of 3"))
        self.assertFails("R2-A", "R2-A row deal/part-2: read 0", doc=doc)

    def test_part_without_read_position_must_read_its_first_member(self):
        head, reads = self.a.split("## Reads\n")
        doc = head + "## Reads\n" + reads.replace("### deal/part-2\n\n- `rig-e02:0:0:0`",
                                                  "### deal/part-2\n\n- `rig-e06:0:0:0`")
        self.assertFails("R2-A", "R2-A row deal/part-2: the row holds no READ POSITION, and "
                                 "its first member in seams.json order, rig-e02:0:0:0, is "
                                 "not listed", doc=doc)

    def test_first_member_is_by_seams_json_order_not_split_list_order(self):
        doc = self.a.replace("### deal/part-2\n\n- `rig-e02:0:0:0`\n- `rig-e06:0:0:0`\n"
                             "- `rig-e10:0:0:0`\n", "### deal/part-2\n\n- `rig-e10:0:0:0`\n"
                             "- `rig-e06:0:0:0`\n- `rig-e02:0:0:0`\n", 1)
        self.assertNotEqual(doc, self.a)
        self.assertEqual(self.failures("R2-A", doc=doc), [])

    def test_part_without_read_position_extra_reads_beyond_first_pass(self):
        p2 = line(self.a, "| `deal/part-2` |")
        head, reads = self.a.split("## Reads\n")
        doc = head + "## Reads\n" + reads.replace(
            "### deal/part-2\n\n- `rig-e02:0:0:0`\n",
            "### deal/part-2\n\n- `rig-e02:0:0:0`\n- `rig-e10:0:0:0`\n")
        doc = doc.replace(p2, cells(p2, 3, "2").replace("1 of 3", "2 of 3"))
        self.assertEqual(self.failures("R2-A", doc=doc), [])

    def test_reads_section_required(self):
        self.assertFails("R2-A", "0 sections headed '## Reads'",
                         doc=self.a.replace("## Reads", "## Read list"))


class Splits(Base):
    def setUp(self):
        super().setUp()
        self.a = self.docs["R2-A"]

    def test_overlapping_parts_fail(self):
        doc = self.a.replace("### deal/part-2\n\n", "### deal/part-2\n\n- `rig-e00:0:0:0`\n",
                             1)
        self.assertFails("R2-A", "parts are not disjoint; rig-e00:0:0:0", doc=doc)

    def test_parts_missing_a_member_fail(self):
        doc = self.a.replace("- `rig-e10:0:0:0`\n", "", 1)
        self.assertFails("R2-A", "the union of its parts misses 1 member(s)", doc=doc)

    def test_part_listing_a_non_member_fails(self):
        doc = self.a.replace("### deal/part-2\n\n", "### deal/part-2\n\n- `rig-d00:0:0:0`\n",
                             1)
        self.assertFails("R2-A", "lists rig-d00:0:0:0, which is not a member of the class",
                         doc=doc)

    def test_part_row_without_member_list_fails(self):
        doc = self.a.replace("### deal/part-2\n\n- `rig-e02", "### deal/part-9\n\n- `rig-e02",
                             1)
        self.assertFails("R2-A", "R2-A part row deal/part-2: no member list", doc=doc)

    def test_whole_and_part_rows_together_fail(self):
        p1 = line(self.a, "| `deal/part-1` |")
        doc = self.a.replace(p1, p1 + p1.replace("deal/part-1", "deal"))
        self.assertFails("R2-A", "class 'deal' has both a whole-class row and part rows",
                         doc=doc)

    def test_non_address_line_under_a_split_fails(self):
        doc = self.a.replace("### deal/part-2\n\n", "### deal/part-2\n\nsome prose\n", 1)
        self.assertFails("R2-A", "line 'some prose' is not one four-coordinate address",
                         doc=doc)


class Pronouns(Base):
    def setUp(self):
        super().setUp()
        self.b = self.docs["R2-B"]
        self.member = line(self.b, "| `rig-b2:0:0:0` |")
        self.notm = line(self.b, "| `rig-b3:0:0:1` |")

    def test_note_without_double_quoted_antecedent_fails(self):
        for row in (self.member, self.notm):
            doc = self.b.replace(row, row.replace('"', ""))
            self.assertFails("R2-B", "the note holds no double-quoted antecedent span",
                             doc=doc)

    def test_curly_quotes_are_a_double_quoted_span(self):
        doc = self.b.replace('"target player"', "“target player”")
        self.assertEqual(self.failures("R2-B", doc=doc), [])

    def test_not_member_with_a_truth_word_fails(self):
        self.assertFails("R2-B", "NOT-MEMBER carries 'UNRESOLVED' in B1",
                         doc=self.b.replace(self.notm, cells(self.notm, 3, "UNRESOLVED")))

    def test_member_with_a_dash_fails(self):
        self.assertFails("R2-B", "B1 '—' is not one of the five cell words",
                         doc=self.b.replace(self.member, cells(self.member, 3, "—")))

    def test_bad_membership_fails(self):
        self.assertFails("R2-B", "membership 'MAYBE' is not MEMBER or NOT-MEMBER",
                         doc=self.b.replace(self.member, cells(self.member, 2, "MAYBE")))

    def test_missing_pronoun_row_fails(self):
        self.assertFails("R2-B", "pronoun table omits pronoun candidate rig-b3:0:0:1",
                         doc=self.b.replace(self.notm, ""))

    def test_member_rows_count_in_totals_not_member_rows_do_not(self):
        flipped = cells(self.notm, 2, "MEMBER")
        for k in range(3, 7):
            flipped = cells(flipped, k, "UNRESOLVED")
        self.assertFails("R2-B", "verdict B3: UNRESOLVED 3, the ledger has 4",
                         doc=self.b.replace(self.notm, flipped))

    def test_pronoun_table_outside_its_section_fails(self):
        self.assertFails("R2-B", "0 sections headed '## Pronoun candidates'",
                         doc=self.b.replace("## Pronoun candidates", "## Pronouns"))


class Verdicts(Base):
    def setUp(self):
        super().setUp()
        self.a = self.docs["R2-A"]

    def v(self, doc, i):
        return line(doc, f"- {i}:")

    def test_suffices_over_not_expressed_fails(self):
        a3 = self.v(self.a, "A3")
        doc = self.a.replace(a3, a3.replace("GENUINELY_MISSING", "SUFFICES").rstrip("\n")
                             + f"; {ac.I3A_LINE}\n")
        self.assertFails("R2-A", "verdict A3: SUFFICES, but VERDICT RULE over the ledger "
                                 "gives GENUINELY_MISSING", doc=doc)

    def test_suffices_over_all_unresolved_fails(self):
        a1 = self.v(self.a, "A1")
        doc = self.a.replace(a1, a1.replace("UNDETERMINED", "SUFFICES").rstrip("\n")
                             + f"; {ac.I3A_LINE}\n")
        self.assertFails("R2-A", "verdict A1: SUFFICES, but VERDICT RULE over the ledger "
                                 "gives UNDETERMINED", doc=doc)

    def test_partial_forces_genuinely_missing(self):
        b2 = self.v(self.docs["R2-B"], "B2")
        doc = self.docs["R2-B"].replace(b2, b2.replace("GENUINELY_MISSING", "UNDETERMINED"))
        self.assertFails("R2-B", "gives GENUINELY_MISSING", doc=doc)

    def test_suffices_citing_s16_without_candidate_fails(self):
        a2 = self.v(self.a, "A2")
        doc = self.a.replace(a2, a2.rstrip("\n") + "; edges per AQ4 §16\n")
        self.assertFails("R2-A", "a SUFFICES line citing AQ4 §9 rungs 2-5, §12, §13 or "
                                 "§16 does not say 'CANDIDATE benchmark structure'", doc=doc)

    def test_suffices_citing_a_rung_range_without_candidate_fails(self):
        a2 = self.v(self.a, "A2")
        for cite in ("AQ4 §9 rungs 1-5", "§9 rung 3", "§12"):
            doc = self.a.replace(a2, a2.rstrip("\n") + f"; {cite}\n")
            self.assertFails("R2-A", "does not say 'CANDIDATE benchmark structure'", doc=doc)

    def test_suffices_citing_rung_1_or_rung_6_needs_no_candidate(self):
        a2 = self.v(self.a, "A2")
        for cite in (ac.RUNG1, "would force RUNG-6 (adoption trigger is a holdout card, "
                               "§9/§22)"):
            doc = self.a.replace(a2, a2.rstrip("\n") + f"; {cite}\n")
            self.assertEqual(self.failures("R2-A", doc=doc), [], cite)

    def test_suffices_without_any_status_phrase_fails(self):
        a2 = self.v(self.a, "A2")
        doc = self.a.replace(a2, a2.split(";")[0] + "\n")
        self.assertFails("R2-A", "a SUFFICES line carries no status phrase", doc=doc)

    def test_count_mismatch_fails(self):
        doc = self.docs["R2-C"].replace("UNRESOLVED 2", "UNRESOLVED 3", 1)
        self.assertFails("R2-C", "verdict C1: UNRESOLVED 3, the ledger has 2", doc=doc)

    def test_recall_rows_are_not_counted(self):
        a2 = self.v(self.a, "A2")
        doc = self.a.replace(a2, a2.replace("EXPRESSED 1,", "EXPRESSED 2,"))
        self.assertFails("R2-A", "verdict A2: EXPRESSED 2, the ledger has 1", doc=doc)

    def test_missing_and_foreign_and_malformed_lines_fail(self):
        c1 = self.v(self.docs["R2-C"], "C1")
        self.assertFails("R2-C", "'## Verdict' has no line for truth item C1",
                         doc=self.docs["R2-C"].replace(c1, ""))
        self.assertFails("R2-C", "'## Verdict' states A1, which is not a R2-C truth item",
                         doc=self.docs["R2-C"].replace(c1, c1 + c1.replace("C1", "A1")))
        self.assertFails("R2-C", "verdict C1: '- C1: UNDETERMINED' is not",
                         doc=self.docs["R2-C"].replace(c1, "- C1: UNDETERMINED\n"))

    def test_noncanonical_duplicate_verdict_fails(self):
        # repair verdict 5988024375: a contradictory duplicate C2 SUFFICES line
        # (two NOT-EXPRESSED cells) indented 1-3 spaces, or in any other
        # non-canonical verdict-like form, is rejected, never skipped.
        c = self.docs["R2-C"]
        c2 = self.v(c, "C2")
        dup = c2.replace("GENUINELY_MISSING", "SUFFICES").rstrip("\n") + f"; {ac.I3A_LINE}"
        body = dup[len("- C2:"):]
        forms = [" " * k + dup for k in (1, 2, 3)] + [
            "\t" + dup, "> " + dup, "* C2:" + body, "+ C2:" + body, "1. C2:" + body,
            "- **C2**:" + body, "- `C2`:" + body, "- C2 :" + body, "-  C2:" + body,
            "C2:" + body, "| C2 | SUFFICES (EXPRESSED 0, PARTIAL 0, NOT-EXPRESSED 2, "
            "UNRESOLVED 0, OUT-OF-CONTRACT 0) |"]
        for form in forms:
            for at in (c2 + form + "\n", form + "\n" + c2):
                bad = self.failures("R2-C", doc=c.replace(c2, at))
                self.assertTrue(any("reads as a verdict but is not in the form" in b
                                    for b in bad), (form, bad))

    def test_wrapped_or_linked_duplicate_verdict_fails(self):
        # repair verdict 5988156977: a duplicate '- [C2](#c2): SUFFICES' whose
        # counts continue on the next line, nested list markers with wrapped
        # counts, and other link or marker wrappings are rejected.
        c = self.docs["R2-C"]
        c2 = self.v(c, "C2")
        counts = ("(EXPRESSED 0, PARTIAL 0, NOT-EXPRESSED 2, UNRESOLVED 0, "
                  "OUT-OF-CONTRACT 0); " + ac.I3A_LINE)
        heads = ["- [C2](#c2): SUFFICES", "- [C2][c2]: SUFFICES", "- [**C2**](#c2): SUFFICES",
                 "- - C2: SUFFICES", "  - - C2: SUFFICES", "  * > C2: SUFFICES",
                 "- 1. C2: SUFFICES", "> > - C2: SUFFICES", "- C2 — SUFFICES",
                 "C2 SUFFICES", "- C2: SUFFICES"]
        for head in heads:
            for sep in ("\n", "\n  ", "\n    ", "\n> "):
                form = head + sep + counts
                for at in (c2 + form + "\n", form + "\n" + c2):
                    bad = self.failures("R2-C", doc=c.replace(c2, at))
                    self.assertTrue(bad, (form, bad))
                    if head != "- C2: SUFFICES":
                        self.assertTrue(any("reads as a verdict but is not in the form" in b
                                            for b in bad), (form, bad))

    def test_linked_id_without_counts_fails(self):
        c = self.docs["R2-C"]
        c2 = self.v(c, "C2")
        for form in ("- [C2](#c2): SUFFICES", "- - C2: SUFFICES", "- [C2][x]：SUFFICES"):
            bad = self.failures("R2-C", doc=c.replace(c2, c2 + form + "\n"))
            self.assertTrue(any("reads as a verdict but is not in the form" in b
                                for b in bad), (form, bad))

    def test_second_verdict_in_a_canonical_line_tail_fails(self):
        c = self.docs["R2-C"]
        c1 = self.v(c, "C1")
        for tail in ("; C2: SUFFICES (EXPRESSED 1, PARTIAL 0, NOT-EXPRESSED 0, "
                     "UNRESOLVED 0, OUT-OF-CONTRACT 0)", "; also NOT-EXPRESSED 2"):
            doc = c.replace(c1, c1.rstrip("\n") + tail + "\n")
            self.assertFails("R2-C", "states another verdict or count", doc=doc)

    def test_verdict_prose_naming_a_verdict_word_passes(self):
        c = self.docs["R2-C"]
        prose = ("M03's classification (GENUINELY_MISSING) still holds for C2; C2 is "
                 "forced by both members.\n")
        doc = c.replace("## Captain questions", prose + "\n## Captain questions")
        self.assertEqual(self.failures("R2-C", doc=doc), [])

    def test_verdict_section_required(self):
        self.assertFails("R2-C", "0 sections headed '## Verdict'",
                         doc=self.docs["R2-C"].replace("## Verdict", "## Verdicts"))

    def test_verdict_rule(self):
        z = dict.fromkeys(ac.WORDS, 0)
        self.assertEqual(ac.verdict_word(z), ac.UNDETERMINED)
        self.assertEqual(ac.verdict_word(dict(z, EXPRESSED=3, UNRESOLVED=2)), ac.SUFFICES)
        self.assertEqual(ac.verdict_word(dict(z, EXPRESSED=3, PARTIAL=1)), ac.MISSING)
        self.assertEqual(ac.verdict_word(dict(z, **{"OUT-OF-CONTRACT": 2})),
                         ac.UNDETERMINED)


MARKUP = "HTML tags and HTML comments are not allowed anywhere in an audit document"


class ForbiddenMarkup(Base):
    """Captain decision 5987664829: '<!--', '-->' and '<' followed by an ASCII
    letter, '/' or '!' fail on any line, code spans and fences included, and the
    offending line is reported by number. Every bypass of the retired HTML and
    comment handling is a regression case here."""

    def assertMarkup(self, seam, doc, lineno, marker):
        bad = self.failures(seam, doc=doc)
        want = f"line {lineno} contains {marker!r}"
        self.assertTrue(any(b.startswith(want) and MARKUP in b for b in bad),
                        f"{want!r} not in {bad}")

    def test_wrapped_audit_fails_on_its_opening_line(self):
        wraps = ("<pre>\n", "<PRE class=\"x\">\n", "<script type=\"text/markdown\">\n",
                 "<textarea>\n", "<style>\n", "<pre>", "<div>\n", "<details open>\n",
                 "<span>\n", "<x-y a=\"1\">\n", "</div>\n", "<!X\n", "<![CDATA[\n",
                 "<!--\n", "<!-->\n")
        for seam in ac.DOCS:
            for open_ in wraps:
                with self.subTest((seam, open_)):
                    doc = open_ + self.docs[seam] + "\n"
                    self.assertMarkup(seam, doc, 1, ac.FORBIDDEN.search(open_).group())

    def test_every_marker_fails_anywhere(self):
        # (inserted line, marker reported): block and inline comments, a
        # comment opener or closer alone, comments in code spans and in table
        # cells, '-->' promoting text to a heading, escapes, autolinks, raw
        # HTML attributes holding '<!--', and closing tags.
        cases = (("<!-- ## Captain questions -->", "<!--"),
                 ("text <!-- hidden", "<!--"), ("-->## Captain questions", "-->"),
                 ("a --> b", "-->"), ("see `<!--` here", "<!--"),
                 ("``a `<!--` b``", "<!--"), ("` --> `", "-->"),
                 ("| a <!-- b --> |", "<!--"), ("## V <!-- x -->", "<!--"),
                 ("a \\<!-- b", "<!--"), ("a <http://x/y> b", "<h"),
                 ('a <span title="<!--">b</span>', "<s"), ("x </pre> y", "</"),
                 ("would <verb>", "<v"), ("x <!DOCTYPE>", "<!"),
                 ("`<b>`", "<b"), ("<A>", "<A"), ("<Z", "<Z"))
        for seam in ac.DOCS:
            for text, marker in cases:
                with self.subTest((seam, text)):
                    doc = self.docs[seam] + "\n" + text + "\n"
                    n = doc.count("\n", 0, doc.index("\n" + text + "\n")) + 2
                    self.assertMarkup(seam, doc, n, marker)

    def test_markers_inside_code_fences_and_indented_code_fail(self):
        for body in ("```\n<!--\n```", "~~~\n-->\n~~~", "```markdown\n<pre>\n```",
                     "    <!-- indented -->", "```\n## Captain questions <!-- x\n```"):
            with self.subTest(body):
                doc = self.docs["R2-C"] + "\n\n" + body + "\n"
                self.assertTrue(any(MARKUP in b for b in self.failures("R2-C", doc=doc)))

    def test_duplicate_heading_after_a_comment_opener_is_counted_and_fails(self):
        # Regression: an open '<!--' (bare, in a code span, or inline) once hid a
        # duplicate heading; now the marker fails and the heading still counts.
        for opener in ("<!--", "see `<!--`", "text <!--", "``a `<!--` b``"):
            with self.subTest(opener):
                doc = self.docs["R2-B"] + f"\n{opener}\n## Captain questions\n-->\n"
                bad = self.failures("R2-B", doc=doc)
                self.assertTrue(any(MARKUP in b for b in bad), bad)
                self.assertTrue(any("2 sections headed '## Captain questions'" in b
                                    for b in bad), bad)

    def test_closed_comment_before_a_valid_audit_still_fails(self):
        for block in ("<!--\n<pre>\n-->\n", "<!-- <pre> -->\n", "x <!-- <pre> -->\n",
                      "<!-->\n", "<!--\n```\n-->\n", "<pre>x</pre>\n"):
            with self.subTest(block):
                doc = block + "\n" + self.docs["R2-A"]
                self.assertMarkup("R2-A", doc, 1, ac.FORBIDDEN.search(block).group())

    def test_each_offending_line_is_reported_once_by_number(self):
        doc = "<!-- a -->\nfine\nx --> y <b>\n" + self.docs["R2-C"]
        bad = [b for b in self.failures("R2-C", doc=doc) if MARKUP in b]
        self.assertEqual([b.split(" contains")[0] for b in bad], ["line 1", "line 3"], bad)
        self.assertTrue(bad[0].startswith("line 1 contains '<!--' and '-->'"), bad)
        self.assertTrue(bad[1].startswith("line 3 contains '-->' and '<b'"), bad)

    def test_harmless_angle_brackets_pass(self):
        for text in ("a < b", "x <= y", "a <- b", "<3", "1 <2>", "a <- -> b", "--",
                     "a -> b", "a <<", "`a < b`", "- > quote"):
            with self.subTest(text):
                doc = self.docs["R2-C"] + "\n" + text + "\n"
                self.assertEqual(self.failures("R2-C", doc=doc), [], text)

    def test_markup_check_reads_raw_lines(self):
        self.assertEqual(ac.markup_failures("a\n```\n<!--\n```"), [
            f"line 3 contains '<!--': {MARKUP}, not even inside code spans or code "
            f"fences; rewrite the line without them (for a placeholder write e.g. "
            f"'VERB' or '[verb]', not '<verb>')"])
        self.assertEqual(ac.markup_failures("a < b\nc <= d"), [])


class DocumentStructure(Base):
    def test_audit_entirely_inside_a_code_fence_fails(self):
        for seam in ac.DOCS:
            for fence in ("```", "~~~", "````markdown"):
                close = fence.rstrip("markdown")
                doc = f"{fence}\n{self.docs[seam]}{close}\n"
                bad = self.failures(seam, doc=doc)
                for needle in ("0 sections headed '## Captain questions'",
                               "0 sections headed '## Verdict'", "0 tables headed",
                               "does not cite the verified seams.json sha256"):
                    self.assertTrue(any(needle in b for b in bad), (seam, fence, needle, bad))

    def test_lines_are_classified_unmodified(self):
        # No HTML or comment handling: every line outside code is kept verbatim.
        for text in ("para\n<span>\n## H\n", "a <!-- b --> c", "text <!--\n-->## H",
                     "## V <!-- x -->\n| a <!-- b --> |"):
            self.assertEqual(ac.structure(text), text)

    def test_unclosed_fence_hides_the_rest(self):
        doc = self.docs["R2-C"].replace("## Verdict", "```\n## Verdict")
        self.assertFails("R2-C", "0 sections headed '## Verdict'", doc=doc)
        self.assertFails("R2-C", "0 sections headed '## Captain questions'", doc=doc)

    def test_ledger_inside_a_fence_fails(self):
        d = self.docs["R2-C"]
        start = d.index("| clause |")
        end = d.index("\n\n", start)
        doc = d[:start] + "```\n" + d[start:end] + "\n```" + d[end:]
        self.assertFails("R2-C", "0 tables headed | clause | C1", doc=doc)

    def test_indented_code_block_is_not_a_table(self):
        d = self.docs["R2-C"]
        start = d.index("| clause |")
        end = d.index("\n\n", start)
        block = "\n".join("    " + l for l in d[start:end].splitlines())
        self.assertFails("R2-C", "0 tables headed | clause | C1",
                         doc=d[:start] + block + d[end:])

    def test_fence_outside_the_structure_is_harmless(self):
        for seam in ac.DOCS:
            doc = self.docs[seam] + "\n```\n## Verdict\n| x |\n```\n"
            self.assertEqual(self.failures(seam, doc=doc), [], seam)

    def test_structure_keeps_line_count(self):
        text = "a\n```\nb\n```\nc\n\n    e\nf"
        self.assertEqual(ac.structure(text).count("\n"), text.count("\n"))
        self.assertEqual([l for l in ac.structure(text).split("\n") if l], ["a", "c", "f"])


class CaptainQuestions(Base):
    def test_missing_section_fails(self):
        for seam in ac.DOCS:
            doc = self.docs[seam].replace("## Captain questions", "## Questions")
            self.assertFails(seam, "0 sections headed '## Captain questions'", doc=doc)


class HandOff(unittest.TestCase):
    def test_stale_seams_stops_and_missing_is_regenerated_by_check_determinism(self):
        self.assertTrue(ac.stale_seams_stops())

    def test_stale_seams_stop_message(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / ac.SEAMS_REL).parent.mkdir(parents=True)
            (root / ac.SEAMS_REL).write_bytes(b"{}\n")
            calls = []

            def run(args):
                calls.append(args[1:])
                return subprocess.CompletedProcess(args, 1, b"", b"STALE: rigged")
            self.assertTrue(ac._halts(lambda: ac.obtain(root, run),
                                      f"stale seams input: {ac.SEAMS_REL}"))
            self.assertEqual(calls, [["--verify"]])

    def test_failed_regeneration_stops(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            run = lambda args: subprocess.CompletedProcess(args, 1, b"", b"")
            self.assertTrue(ac._halts(lambda: ac.obtain(root, run), "could not regenerate"))
            ok = lambda args: subprocess.CompletedProcess(args, 0, b"", b"")
            self.assertTrue(ac._halts(lambda: ac.obtain(root, ok), "did not write"))


if __name__ == "__main__":
    unittest.main()
