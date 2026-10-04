"""A01 unit tests: the Round-2 seam probe's pure functions -- every membership
arm and non-arm of R2-A, R2-B and R2-C, the pronoun and contrast forms, the
R2-A classes, the read positions, the CR-missing STOPs and each negative
control the probe contracts.

Inline SYNTHETIC clauses only -- generic templating, no card, no card name and
no Oracle text -- except `RecallControls`: regression cases named ONLY by
oracle_id and four-coordinate address and read from the pinned corpus at run
time. A missing or differing corpus is a loud failure there, never a skip.

    python3 -m unittest discover -s tests/oracle_ingest -t .
"""
import contextlib
import io
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "oracle_ingest"))

import a01_seams as s            # noqa: E402

hr = s.h
CORPUS_REL = "data/raw/oracle-cards.jsonl.gz"


def halts(fn) -> bool:
    return hr._halts(fn)


def quiet(fn):
    with contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        return fn()


# ------------------------------------------------------------------- R2-A

class R2AMembership(unittest.TestCase):
    def test_the_member_word_is_read_from_the_cr(self):
        self.assertEqual(s.INSTEAD, "instead")
        self.assertEqual(s.cr_instead_word(s.cr.text()), "instead")

    def test_arms(self):
        for text in ("If a widget would be destroyed, tap it instead.",
                     "Instead, draw two cards.",
                     "If this spell was kicked, it deals 4 damage INSTEAD."):
            self.assertTrue(s.r2a_member(text), text)

    def test_non_arms(self):
        for text in ("If you would draw a card, exile it.",
                     "Skip your next draw step.",
                     "This widget enters with two +1/+1 counters on it.",
                     "Insteadly, draw a card.", ""):
            self.assertFalse(s.r2a_member(text), text)
            self.assertIsNone(s.r2a_class(text), text)
            self.assertIsNone(s.r2a_would(text), text)


class R2AClasses(unittest.TestCase):
    def test_would_class_and_would_verb(self):
        text = "If you would draw a card, exile it instead."
        self.assertEqual(s.r2a_would(text), ("draw", "draw", 13))
        self.assertEqual(text[13:17], "draw")

    def test_be_takes_two_words_and_the_verb_is_the_last(self):
        text = "If a token would be put into your library, mill two cards instead."
        key, verb, off = s.r2a_would(text)
        self.assertEqual((key, verb), ("be put", "put"))
        self.assertEqual(text[off:off + 3], "put")
        self.assertEqual(s.r2a_class("If a widget would be dealt damage, prevent "
                                     "it instead."), "be dealt")

    def test_last_would_before_the_member_word_decides(self):
        self.assertEqual(s.r2a_class("If you would gain life or would draw a card, "
                                     "mill a card instead."), "draw")

    def test_would_after_the_member_word_is_not_read(self):
        self.assertEqual(s.r2a_would("Draw a card instead if a widget would die."),
                         ("no-would:draw", None, None))

    def test_no_would_class_is_the_first_word(self):
        self.assertEqual(s.r2a_would("If this spell was kicked, it deals 4 damage "
                                     "instead."), ("no-would:if", None, None))
        self.assertEqual(s.r2a_class("Threshold — It deals 3 damage instead."),
                         "no-would:threshold")

    def test_class_key_is_lowercased(self):
        self.assertEqual(s.r2a_class("If a widget WOULD Die, exile it instead."), "die")

    def test_would_without_a_following_word_halts(self):
        self.assertTrue(halts(lambda: s.r2a_would("If it would, draw a card instead.")))
        self.assertTrue(halts(lambda: s.r2a_would("If it would be, draw instead.")))


class ReadPositions(unittest.TestCase):
    def test_all_members_when_n_at_most_ten(self):
        for n in range(0, 11):
            self.assertEqual(s.read_positions(n), list(range(n)))

    def test_ten_spread_positions(self):
        self.assertEqual(s.read_positions(11), [0, 1, 2, 3, 4, 6, 7, 8, 9, 10])
        for n in (11, 12, 19, 100, 343):
            pos = s.read_positions(n)
            self.assertEqual(pos, [round(i * (n - 1) / 9) for i in range(10)])
            self.assertEqual((pos[0], pos[-1], len(set(pos))), (0, n - 1, 10))
            self.assertEqual(pos, sorted(pos))


# ------------------------------------------------------------------- R2-B

class R2BClassify(unittest.TestCase):
    def test_every_verb_with_every_player_term_is_a_member(self):
        for verb in ("control", "controls", "gain control of", "gains control of"):
            for term in s.PLAYER_TERMS:
                text = f"Then you {verb} {term} until your next upkeep."
                self.assertEqual(s.r2b_classify(text), "member", text)

    def test_pronoun_forms_are_candidates_not_members(self):
        for verb in ("control", "controls", "gain control of", "gains control of"):
            for form in s.PRONOUN_FORMS:
                text = f"Tap two widgets, then {verb} {form} until end of turn."
                self.assertEqual(s.r2b_classify(text), "pronoun", text)

    def test_contrast_forms(self):
        for text in ("Gain control of target creature.",
                     "An opponent gains control of each widget you own.",
                     "Exchange control of two target widgets.",
                     "Its owner exchanges control of this widget and target land.",
                     "You control enchanted creature.",
                     "Its controller controls equipped creature."):
            self.assertEqual(s.r2b_classify(text), "contrast", text)

    def test_non_arms(self):
        for text in ("For each land you control, target player draws a card.",
                     "Exchange control of target player.",
                     "Exchange control of them.",
                     "Its controller targets each opponent.",
                     "You control target, player.",
                     "Widgets you controlled enchanted nothing.",
                     "Under target opponent's control, draw a card.",
                     "Draw a card."):
            self.assertEqual(s.r2b_classify(text), "none", text)

    def test_precedence_member_over_pronoun_over_contrast(self):
        self.assertEqual(s.r2b_classify("Gain control of target widget and control "
                                        "them, then you control that player."),
                         "member")
        self.assertEqual(s.r2b_classify("Gain control of target widget, then gain "
                                        "control of them."), "pronoun")

    def test_matches_report_each_form(self):
        got = s.r2b_matches("You control enchanted creature and gain control of them.")
        self.assertEqual(len(got["contrast"]), 1)
        self.assertEqual(len(got["pronoun"]), 1)
        self.assertEqual(got["member"], [])


# ------------------------------------------------------------------- R2-C

class R2CClassify(unittest.TestCase):
    def test_every_verb_with_both_phrases_is_a_member(self):
        for verb in ("has", "have", "gains", "gain"):
            for phrase in ("all activated abilities of", "all abilities of"):
                text = f"Each token you control {verb} {phrase} each Wall you own."
                self.assertEqual(s.r2c_classify(text), "member", text)

    def test_contrast_quoted_and_keyword(self):
        self.assertIn("flying", s.aq._CR702_KEYWORD_NAMES)
        self.assertIn("first strike", s.aq._CR702_KEYWORD_NAMES)
        for text in ('Target creature gains "{T}: Draw a card."',
                     "Target creature gains flying.",
                     "Widgets you control have first strike until end of turn.",
                     "Equipped creature has “{1}: Scry 1.”"):
            self.assertEqual(s.r2c_classify(text), "contrast", text)
        got = s.r2c_matches("Target creature gains first strike.")["contrast"]
        self.assertEqual([m[2] for m in got], ["keyword:first strike"])

    def test_non_arms(self):
        for text in ("You gain 3 life.",
                     "Target creature gains flyingish power.",
                     "This widget has all activated abilities.",
                     "This widget had all abilities of each Wall.",
                     "This widget has all triggered abilities of each Wall.",
                     'Target creature gets +1/+0 and "{T}: Draw a card."',
                     "Draw a card."):
            self.assertEqual(s.r2c_classify(text), "none", text)

    def test_precedence_member_over_contrast(self):
        self.assertEqual(s.r2c_classify("This widget has flying and has all "
                                        "activated abilities of each Wall you own."),
                         "member")


# --------------------------------------------------------------- CR readers

class CRReaders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.txt = s.cr.text()

    def test_every_cited_rule_is_read(self):
        got = s.cr_read_cited(self.txt)
        self.assertEqual(set(got), {r for rs in s.CITED.values() for r in rs})
        self.assertTrue(all(got.values()))

    def test_each_missing_cited_rule_stops(self):
        for rule in sorted({r for rs in s.CITED.values() for r in rs}):
            with self.subTest(rule=rule):
                self.assertTrue(halts(lambda: s.cr_read_cited(s._drop_rule(self.txt,
                                                                           rule))))

    def test_instead_word_stops_without_a_single_quoted_word(self):
        self.assertTrue(halts(lambda: s.cr_instead_word(s._drop_rule(self.txt,
                                                                     "614.1a"))))
        self.assertTrue(halts(lambda: s.cr_instead_word(
            "614.1a Effects that use the word “instead” or “rather” are effects.")))
        self.assertTrue(halts(lambda: s.cr_instead_word(
            "614.1a Effects that use the phrase “in place of” are effects.")))
        self.assertEqual(s.cr_instead_word("614.1a Use the word “instead”."), "instead")

    def test_cr_723_2_names_parse(self):
        self.assertEqual(s.cr_723_2_names("723.2. Two cards (Alpha Widget and Beta "
                                          "Widget) allow a player to do a thing."),
                         ["Alpha Widget", "Beta Widget"])
        self.assertEqual(s.cr_723_2_names("723.2. Three cards (A Widget, B Widget, "
                                          "and C Widget) allow it."),
                         ["A Widget", "B Widget", "C Widget"])
        self.assertEqual(len(s.cr_723_2_names(self.txt)), 2)

    def test_cr_723_2_bad_shapes_stop(self):
        for txt in ("723.2. Three cards (Alpha Widget and Beta Widget) allow it.",
                    "723.2. Two cards allow a player to do a thing.",
                    "723.2. Some cards (Alpha Widget and Beta Widget) allow it.",
                    "723.1. Nothing here."):
            self.assertTrue(halts(lambda t=txt: s.cr_723_2_names(t)), txt)

    def test_a_rule_line_is_matched_exactly(self):
        self.assertEqual(s.cr_rule("723.1", "723.1. Body one.\n723.1a Sub."), "Body one.")
        self.assertTrue(halts(lambda: s.cr_rule("723.1", "723.1a Sub only.")))
        self.assertTrue(halts(lambda: s.cr_rule("723.1", "723.1. A.\n723.1. B.")))


# ------------------------------------------------------------- P4 mapping

class P4Paragraphs(unittest.TestCase):
    PARAS = [((0, 0), ["Draw a card.", "Then tap it."]), ((0, 2), ["Untap it."])]
    LINES = ["Draw a card. Then tap it.", "Untap it."]

    def test_equal_lines_map_to_paragraphs(self):
        self.assertEqual(s.p4_paragraphs(self.LINES, self.PARAS, "rig"),
                         [(0, 0), (0, 2)])

    def test_differing_text_halts(self):
        self.assertTrue(halts(lambda: s.p4_paragraphs(
            ["Draw a card. Then tap it!", "Untap it."], self.PARAS, "rig")))

    def test_differing_line_count_halts(self):
        self.assertTrue(halts(lambda: s.p4_paragraphs(self.LINES[:1], self.PARAS, "rig")))

    def test_differing_sentence_count_halts(self):
        self.assertTrue(halts(lambda: s.p4_paragraphs(
            ["Draw a card. Then tap it."], [((0, 0), ["Draw a card. Then tap it."])],
            "rig")))


# ---------------------------------------------------------- rules and rigs

class RulesTable(unittest.TestCase):
    def test_entries_are_exactly_structural(self):
        for r in s.RULES:
            self.assertEqual(set(r), hr._RULE_KEYS, r["id"])
            self.assertTrue(r["cr"].startswith("CR "), r["id"])
        self.assertEqual(len({r["id"] for r in s.RULES}), len(s.RULES))

    def test_one_entry_per_form(self):
        kinds = {r["id"]: r["kind"] for r in s.RULES}
        self.assertEqual(sorted(k for k, v in kinds.items() if v == "member"),
                         ["r2a-member", "r2b-member", "r2c-member"])
        self.assertEqual([k for k, v in kinds.items() if v == "pronoun-candidate"],
                         ["r2b-pronoun"])
        self.assertEqual(sorted(k for k, v in kinds.items() if v == "contrast"),
                         ["r2b-contrast-attached", "r2b-contrast-of",
                          "r2c-contrast-keyword", "r2c-contrast-quoted"])

    def test_keyword_set_is_referenced_never_inline(self):
        kw = next(r for r in s.RULES if r["id"] == "r2c-contrast-keyword")
        self.assertIn("foundry_aq4_probes._CR702_KEYWORD_NAMES", kw["pattern"])
        self.assertNotIn("flying", " ".join(str(v) for r in s.RULES for v in r.values()))

    def test_card_keyed_variants_halt(self):
        name, oid = "Synthetic Widget", "00000000-0000-0000-0000-000000000000"
        variants = s._rig_card_keyed(name, oid)
        self.assertEqual(len(variants), len(s.RULES) * len(hr._RULE_KEYS) * 2)
        for v in variants:
            self.assertTrue(halts(lambda v=v: hr.assert_not_card_keyed((v,) + s.RULES,
                                                                       [name])), v)
        self.assertFalse(halts(lambda: hr.assert_not_card_keyed(s.RULES, [name])))

    def test_recall_check_halts_when_a_control_is_removed(self):
        members = {"a:0:0:0", "b:0:1:2"}
        self.assertEqual(s.check_recall("rig", members, ("a", "b")),
                         {"a": ["a:0:0:0"], "b": ["b:0:1:2"]})
        self.assertTrue(halts(lambda: s.check_recall("rig", {"a:0:0:0"}, ("a", "b"))))

    def test_rigged_identity_hash_halts(self):
        self.assertTrue(halts(lambda: hr.verify_identities(
            dict(hr.I1, **{hr.C02_REL: "0" * 64}))))

    def test_portability_guard_fires(self):
        self.assertTrue(hr.portability_violations(
            b'{"p": "' + str(ROOT).encode() + b'"}'))
        self.assertFalse(hr.portability_violations(b'{"p": "experiments/out"}'))

    def test_brief_rigged_clauses(self):
        self.assertEqual(s.r2b_classify("gain control of target creature"), "contrast")
        self.assertEqual(s.r2b_classify("you control enchanted creature"), "contrast")
        self.assertEqual(s.r2b_classify("gain control of them"), "pronoun")
        self.assertEqual(s.r2b_classify("for each land you control, target player "
                                        "draws a card"), "none")
        self.assertEqual(s.r2c_classify('target creature gains "{T}: Draw a card."'),
                         "contrast")
        self.assertEqual(s.r2c_classify("target creature gains flying"), "contrast")
        self.assertEqual(s.r2a_class("If you would draw a card, exile it instead"),
                         "draw")
        self.assertEqual(s.r2a_class("If this spell was kicked, it deals 4 damage "
                                     "instead"), "no-would:if")


# ------------------------------------------------- pinned-corpus regressions

# Recall controls by oracle_id and four-coordinate address only; the clause
# text is read from the pinned corpus at run time.
RECALL = {
    "R2-A": ("eccc9a54-2b56-4a02-9926-258d5b2e25fb:0:0:0",
             "51d517c9-2812-44ce-ab4d-e5422b5ecf6c:0:0:0",
             "eae87919-6322-4bd2-ae9c-b1ce25d686da:0:0:0",
             "766c644c-04fe-4b01-93dd-09a50d78d01f:0:0:0"),
    "R2-B": ("a806f4ee-f48a-46c3-8772-5aaabebe4c7e:0:0:0",
             "face0a43-6604-4508-b511-81ab0bef7b18:0:0:0",
             "4e7a8817-1a66-45c3-ade9-eac79b40b89f:0:1:0",
             "1f438b8f-fe23-4f3b-ab2e-f6c33676c462:0:1:0"),
    "R2-C": ("c259e16f-2a44-4552-8678-815f757a02e8:0:1:0",
             "2fdeb920-2e48-4308-9517-743eec219c04:0:0:0",
             "93cfa771-067f-44ed-9e29-6caf698ee9aa:0:0:0"),
}
IS_MEMBER = {"R2-A": s.r2a_member,
             "R2-B": lambda t: s.r2b_classify(t) == "member",
             "R2-C": lambda t: s.r2c_classify(t) == "member"}


class RecallControls(unittest.TestCase):
    """Regression cases, never keys: every recall control is a member of its seam."""

    @classmethod
    def setUpClass(cls):
        path = hr.ROOT / CORPUS_REL
        if not path.exists():
            raise AssertionError(f"the pinned corpus {CORPUS_REL} is missing: the "
                                 f"recall-control regressions cannot run (a loud "
                                 f"failure, never a skip)")
        if halts(lambda: hr.verify_identities({CORPUS_REL: hr.I1[CORPUS_REL]})):
            raise AssertionError(f"the corpus at {CORPUS_REL} is not the pinned I1 "
                                 f"identity {hr.I1[CORPUS_REL]}")
        cls.cards, _, _ = quiet(hr.fc.load_corpus_gated)

    def clause(self, address):
        oid, fi, pi, ci = address.split(":")
        self.assertIn(oid, self.cards, f"{oid} is not in the pinned corpus")
        hit = [seg for f, p, c, seg in hr.chain_clauses(self.cards[oid])
               if (f, p, c) == (int(fi), int(pi), int(ci))]
        self.assertEqual(len(hit), 1, f"{address} is not one chain clause")
        return hit[0]

    def test_every_recall_control_is_a_member_at_its_address(self):
        for seam, addrs in RECALL.items():
            for a in addrs:
                with self.subTest(seam=seam, address=a):
                    self.assertTrue(IS_MEMBER[seam](self.clause(a)))

    def test_recall_controls_match_the_probe(self):
        self.assertEqual([a.split(":")[0] for a in RECALL["R2-A"]], list(s.R2A_CONTROLS))
        self.assertEqual([a.split(":")[0] for a in RECALL["R2-B"]], list(s.R2B_CONTROLS))
        self.assertEqual(sorted(a.split(":")[0] for a in RECALL["R2-C"]),
                         sorted(s.R2C_CONTROLS))

    def test_cr_723_2_cards_resolve_once_and_are_members(self):
        names = s.cr_723_2_names(s.cr.text())
        resolved = s.resolve_723_2(names, self.cards)
        self.assertEqual(sorted(resolved), sorted(names))
        for oid in resolved.values():
            with self.subTest(oracle_id=oid):
                self.assertTrue(any(IS_MEMBER["R2-B"](seg) for *_, seg in
                                    hr.chain_clauses(self.cards[oid])))

    def test_unknown_cr_723_2_name_stops(self):
        self.assertTrue(halts(lambda: s.resolve_723_2(["Synthetic Widget Qx"],
                                                      self.cards)))

    def test_fixture_roles_hold_the_controls(self):
        got = quiet(lambda: s.fixture_check(self.cards))
        self.assertEqual(sorted(x["oracle_id"] for x in got[s.R2A_FIXTURE_ROLE]),
                         sorted(s.R2A_CONTROLS))

    def test_correct_rules_pass_the_guard_over_every_corpus_name(self):
        names = s.corpus_names(self.cards)
        self.assertGreater(len(names), 30000)
        self.assertEqual(hr.assert_not_card_keyed(s.RULES, names),
                         [r["id"] for r in s.RULES])

    def test_probe_negative_controls_all_fire(self):
        names = s.corpus_names(self.cards)
        members = set(RECALL["R2-A"])
        view = s.card_view(s.R2A_CONTROLS[0], self.cards[s.R2A_CONTROLS[0]])
        got = s.negative_controls(self.cards, names, members, view)
        self.assertEqual(len(got), 12)

    def test_recall_control_p4_lines_equal_their_chain_paragraphs(self):
        for seam, addrs in RECALL.items():
            for a in addrs:
                oid = a.split(":")[0]
                with self.subTest(oracle_id=oid):
                    s.p4_by_clause(s.card_view(oid, self.cards[oid]))


if __name__ == "__main__":
    unittest.main()
