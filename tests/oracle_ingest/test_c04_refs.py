"""C04 unit tests: reference resolution (oracle-compiler-interface/5 §I5).

Through c04_refs.py's pure functions on inline SYNTHETIC paragraphs only --
generic templating, no card, no card name, no oracle_id and no Oracle text,
with synthetic regions -- one case per arm and non-arm of every §I5.3 rule,
E1-E6, overlap and residue, the §I5.7 discovery covered/uncovered test, and
each C04-RESOLVE negative control.

`Regression` alone reads the pinned corpus at run time: the outcome of every
card INTERFACES.md §I5.3, §I5.5, §I5.6 and §I5.7 names, recorded ONLY as row_id
(four-coordinate address, character offset, the printed phrase P4 matched) or
address and offset. A missing or differing corpus is a loud failure, never a
skip. An outcome that differs from what §I5 states is a STOP to the Captain:
neither the test nor the rule is adapted.

    python3 -m unittest discover -s tests/oracle_ingest -t .
"""
import contextlib
import copy
import io
import json
import re
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "oracle_ingest"))

import c04_refs as c            # noqa: E402

hr, aq = c.hr, c.aq
NAMES = ["Synthetic Widget"]


def halts(fn):
    try:
        with contextlib.redirect_stderr(io.StringIO()), \
                contextlib.redirect_stdout(io.StringIO()):
            fn()
    except SystemExit:
        return True
    return False


def reg(clause, head, start, end=None):
    """A synthetic region of `head` whose head word opens `start` in the clause
    and which runs to the end of `end` (or of the clause)."""
    a = clause.index(start)
    b = len(clause) if end is None else clause.index(end, a) + len(end)
    return {"head": head, "head_span": [a, a + len(start.split()[0])], "span": [a, b]}


def para(*items):
    """A synthetic paragraph: each item a clause, or (clause, [regions])."""
    clauses = [x if isinstance(x, str) else x[0] for x in items]
    regions = [[] if isinstance(x, str) else x[1] for x in items]
    return {"text": " ".join(clauses), "clauses": clauses, "regions": regions}


def at(clause, phrase, n=0):
    """The n-th whole-word, case-insensitive occurrence of `phrase`."""
    return [m.start() for m in re.finditer(r"(?<![\w'])" + re.escape(phrase)
                                           + r"(?![\w])", clause, re.I)][n]


# ------------------------------------------------------------------ E1

def e1(*items, ci=-1, phrase="this way"):
    p = para(*items)
    ci = ci % len(p["clauses"])
    return c.e1(p["clauses"], ci, at(p["clauses"][ci], phrase), p["regions"])


EX = "Exile target artifact."
EX_R = (EX, [reg(EX, "exile", "Exile")])


class Participle(unittest.TestCase):
    """§I5.3 E1's participle of a single-word frozen head; never the bare word."""

    def test_d_and_ed(self):
        self.assertEqual(c.participle_head("exiled"), ("exile", False))      # -d
        self.assertEqual(c.participle_head("returned"), ("return", False))   # -ed
        self.assertEqual(c.participle_head("Destroyed"), ("destroy", False))

    def test_ied_and_doubled_consonant(self):
        with mock.patch.object(c, "_SINGLE_HEADS", ("copy", "tap")):
            self.assertEqual(c.participle_head("copied"), ("copy", False))
            self.assertEqual(c.participle_head("tapped"), ("tap", False))
        self.assertEqual(c.participle_head("tapped"), (None, False))         # no head

    def test_irreg(self):
        self.assertEqual(len(c.IRREG), 19)
        self.assertEqual(c.participle_head("drawn"), ("draw", True))
        for w in ("dealt", "put", "chosen", "paid", "found", "shown"):
            self.assertEqual(c.participle_head(w), (None, True), w)

    def test_bare_word_is_never_a_participle(self):
        for w in ("exile", "draw", "return", "sacrifice"):
            self.assertEqual(c.participle_head(w), (None, False), w)


class E1(unittest.TestCase):

    def resolved(self, got, head, clause):
        self.assertEqual((got["outcome"], got["reason"], got["class"]),
                         ("RESOLVED", None, f"E1:{head}"), got)
        self.assertEqual((got["endpoint"]["kind"], got["endpoint"]["clause"]),
                         ("EVENT", clause))

    def unresolved(self, got, reason, cls):
        self.assertEqual((got["outcome"], got["reason"], got["class"]),
                         ("UNRESOLVED", reason, cls), got)
        self.assertNotIn("endpoint", got)

    # -- the governing verb
    def test_participle_governs(self):
        got = e1(EX_R, "Draw a card for each card exiled this way.")
        self.resolved(got, "exile", 0)
        self.assertEqual(got["endpoint"]["region_span"], [0, len(EX)])

    def test_irregular_participle_with_a_head_governs(self):
        d = "Draw two cards."
        self.resolved(e1((d, [reg(d, "draw", "Draw")]),
                         "Gain 1 life for each card drawn this way."), "draw", 0)

    def test_bare_head_not_after_preps_governs(self):
        s = "Search your library for a card."
        r = "If you search your library this way, shuffle."
        self.resolved(e1((s, [reg(s, "search", "Search")]),
                         (r, [reg(r, "search", "search", "this way")])), "search", 0)

    def test_bare_head_after_preps_is_not_a_verb(self):
        # "to cast this way" never governs: the scan passes it and reaches the
        # start of the clause.
        self.unresolved(e1("You may pay {1} to cast it this way."), "no-candidate", None)
        for prep in c.PREPS:
            got = e1(f"Draw {prep} exile this way.")
            self.assertNotEqual(got["class"], "E1:exile", prep)

    # -- DETS adjectives
    def test_dets_participle_is_skipped(self):
        for det in c.DETS:
            got = e1(EX_R, f"Return {det} exiled artifact this way.")
            self.unresolved(got, "no-candidate", "E1:return")
        self.unresolved(e1("Return the tapped artifact this way."), "no-candidate",
                        "E1:return")

    def test_dets_irregular_participle_stops(self):
        self.unresolved(e1(EX_R, "Return the chosen artifact this way."),
                        "detector-reach", None)

    def test_that_is_not_in_dets(self):
        self.assertNotIn("that", c.DETS)
        self.unresolved(e1("Draw a card for each creature that died this way."),
                        "detector-reach", None)
        self.resolved(e1(EX_R, "Draw a card for each artifact that exiled this way."),
                      "exile", 0)

    # -- coordination (§I5.8 ruling 13)
    def test_coordinated_verb_is_ambiguous(self):
        self.unresolved(e1(EX_R, "Draw a card for each card destroyed or exiled this way."),
                        "ambiguous", "E1:exile")
        self.unresolved(e1(EX_R, "Draw a card for each card destroyed and exiled this way."),
                        "ambiguous", "E1:exile")
        self.unresolved(e1("Tap an artifact or exile a card this way."), "ambiguous",
                        "E1:exile")

    def test_coordination_needs_the_word_directly_before(self):
        self.resolved(e1(EX_R, "Draw a card or two for each card exiled this way."),
                      "exile", 0)

    # -- the stop
    def test_other_participle_stops(self):
        self.unresolved(e1(EX_R, "Draw a card for each creature tapped this way."),
                        "detector-reach", None)

    def test_irregular_participle_without_a_head_stops(self):
        self.unresolved(e1(EX_R, "Gain life for each damage dealt this way."),
                        "detector-reach", None)

    # -- the endpoint
    def test_own_region_is_excluded(self):
        s = "You may sacrifice any number of artifacts this way."
        own = (s, [reg(s, "sacrifice", "sacrifice")])
        self.unresolved(e1(own), "no-candidate", "E1:sacrifice")
        e = "Sacrifice an artifact."
        self.resolved(e1((e, [reg(e, "sacrifice", "Sacrifice")]), own), "sacrifice", 0)

    def test_same_clause_region_starting_before_the_offset(self):
        s = "Exile target artifact, then return each card exiled this way."
        got = e1((s, [reg(s, "exile", "Exile", ","), reg(s, "return", "return")]))
        self.resolved(got, "exile", 0)
        self.assertEqual(got["endpoint"]["region_span"], [0, s.index(",") + 1])

    def test_same_clause_region_starting_after_the_offset(self):
        s = "For each card exiled this way, exile target artifact."
        self.unresolved(e1((s, [reg(s, "exile", "exile target")])), "no-candidate",
                        "E1:exile")

    def test_region_directly_after_preps_is_no_event(self):
        p = "You may pay {1} to exile target artifact."
        self.unresolved(e1((p, [reg(p, "exile", "exile")]),
                           "Draw a card for each card exiled this way."),
                        "no-candidate", "E1:exile")

    def test_region_after_preps_with_a_word_between_is_an_event(self):
        p = "For each Aura attached to ~, exile target artifact."
        self.resolved(e1((p, [reg(p, "exile", "exile")]),
                         "Draw a card for each card exiled this way."), "exile", 0)

    def test_several_regions_are_ambiguous(self):
        e = "Exile target enchantment."
        self.unresolved(e1(EX_R, (e, [reg(e, "exile", "Exile")]),
                           "Draw a card for each card exiled this way."),
                        "ambiguous", "E1:exile")

    def test_no_region_with_the_head(self):
        self.unresolved(e1("Draw a card for each card exiled this way."),
                        "no-candidate", "E1:exile")

    def test_scan_reaching_the_start(self):
        self.unresolved(e1("Spend mana this way."), "no-candidate", None)


# ------------------------------------------------------------------ E2

def face(*paras, type_line="Artifact"):
    return {"type_line": type_line, "paragraphs": list(paras)}


def e2(phrase, f, pi=-1, ci=-1):
    pi = pi % len(f["paragraphs"])
    p = f["paragraphs"][pi]
    ci = ci % len(p["clauses"])
    return c.e2(phrase, f, pi, ci, at(p["clauses"][ci], phrase))


def ex(clause):
    """A clause with one exile region from its first 'exile'."""
    m = re.search(r"(?<!\w)exile(?!\w)", clause, re.I)
    return (clause, [reg(clause, "exile", clause[m.start():])])


class E2(unittest.TestCase):

    def resolved(self, got, kind, para_clause, cls):
        self.assertEqual((got["outcome"], got["reason"], got["class"]),
                         ("RESOLVED", None, cls), got)
        self.assertEqual((got["endpoint"]["kind"], got["endpoint"]["paragraph"],
                          got["endpoint"]["clause"]), (kind, *para_clause))

    def unresolved(self, got, reason, cls):
        self.assertEqual((got["outcome"], got["reason"], got["class"]),
                         ("UNRESOLVED", reason, cls), got)

    REF = "Return the exiled card to its owner's hand."

    # -- only the exiled and chosen forms
    def test_other_cr607_phrase_is_no_rule(self):
        f = face(para("As ~ entered, draw a card."))
        self.unresolved(c.e2("as ~ entered", f, 0, 0, 0), "no-rule", None)

    def test_chosen_and_exiled_is_a_chosen_form(self):
        f = face(para("{T}: Choose a color."),
                 para("Draw a card for each card of the chosen color exiled this way."))
        self.resolved(e2("the chosen color exiled", f), "LINKED", (0, 0), "E2:chosen")

    # -- the exiled forms: scope
    def test_exiled_same_ability_earlier_clause(self):
        f = face(para(ex("Exile target card."), self.REF))
        self.resolved(e2("the exiled card", f), "COREFERENT", (0, 0), "E2:exiled")

    def test_exiled_own_clause_region_before_the_reference(self):
        f = face(para(ex("{1}, Exile a card from your graveyard: Return the exiled card "
                         "to the battlefield.")))
        self.resolved(e2("the exiled card", f), "COREFERENT", (0, 0), "E2:exiled")

    def test_exiled_own_clause_region_after_the_reference(self):
        f = face(para(("Return the exiled card, then exile target card.",
                       [reg("Return the exiled card, then exile target card.", "exile",
                            "exile")])))
        self.unresolved(e2("the exiled card", f), "no-candidate", "E2:exiled")

    def test_exiled_spell_ability_is_coreference(self):
        f = face(para(ex("Exile target card."), self.REF), type_line="Sorcery")
        self.resolved(e2("the exiled card", f), "COREFERENT", (0, 0), "E2:exiled")

    def test_exiled_other_ability_activated(self):
        f = face(para(ex("{1}: Exile target card.")), para(self.REF))
        self.resolved(e2("the exiled card", f), "LINKED", (0, 0), "E2:exiled")

    def test_exiled_other_ability_triggered(self):
        for opener in ("When this artifact enters, exile target card.",
                       "Whenever you draw a card, exile target card.",
                       "At the beginning of your upkeep, exile target card.",
                       "Synthetic Label — When this artifact enters, exile target card."):
            f = face(para(ex(opener)), para(self.REF))
            self.resolved(e2("the exiled card", f), "LINKED", (0, 0), "E2:exiled")

    def test_exiled_other_ability_replacement(self):
        for opener in ("If a card would be put into a graveyard, exile it instead.",
                       "As ~ enters, exile a card from your hand.",
                       "As this artifact enters, exile a card from your hand."):
            f = face(para(ex(opener)), para(self.REF))
            self.resolved(e2("the exiled card", f), "LINKED", (0, 0), "E2:exiled")

    def test_exiled_other_static_ability_is_no_candidate(self):
        f = face(para(ex("You may exile cards from your hand.")), para(self.REF))
        self.unresolved(e2("the exiled card", f), "no-candidate", "E2:exiled")

    def test_exiled_same_and_other_is_ambiguous(self):
        # §I5.8 ruling 11: the reference's own ability and another both hold one.
        f = face(para(ex("{1}: Exile target card.")),
                 para(ex("{2}, Exile a card from your hand: Return the exiled card.")))
        self.unresolved(e2("the exiled card", f), "ambiguous", "E2:exiled")

    def test_exiled_two_in_the_same_ability_is_ambiguous(self):
        f = face(para(ex("Exile target card."), ex("Exile target artifact."), self.REF))
        self.unresolved(e2("the exiled card", f), "ambiguous", "E2:exiled")

    def test_exiled_order_is_not_checked_across_abilities(self):
        f = face(para(self.REF), para(ex("{1}: Exile target card.")))
        self.resolved(e2("the exiled card", f, pi=0), "LINKED", (1, 0), "E2:exiled")

    # -- one ability
    def test_bullet_modes_join_their_paragraph(self):
        f = face(para("Choose one —"), para(ex("• Exile target card.")),
                 para("• " + self.REF))
        self.resolved(e2("the exiled card", f), "COREFERENT", (1, 0), "E2:exiled")
        g = face(para("Choose one —"), para(ex("Exile target card.")), para(self.REF))
        self.unresolved(e2("the exiled card", g), "no-candidate", "E2:exiled")

    def test_additional_cost_joins_on_an_instant_or_sorcery(self):
        cost = ex("As an additional cost to cast this spell, exile a card from your hand.")
        ref = "Draw cards equal to the exiled card's mana value."
        for tl in ("Instant", "Sorcery", "Legendary Sorcery"):
            f = face(para(cost), para(ref), type_line=tl)
            self.resolved(e2("the exiled card", f), "COREFERENT", (0, 0), "E2:exiled")
        f = face(para(cost), para(ref), type_line="Artifact")
        self.unresolved(e2("the exiled card", f), "no-candidate", "E2:exiled")

    # -- the chosen forms
    COLOR = "This artifact has protection from the chosen color."

    def test_chosen_other_ability_is_linked(self):
        f = face(para("As this artifact enters, choose a color."), para(self.COLOR))
        self.resolved(e2("the chosen color", f), "LINKED", (0, 0), "E2:chosen")

    def test_chosen_same_ability_earlier_clause(self):
        f = face(para("Choose a color.",
                      "Target creature gains protection from the chosen color."))
        self.resolved(e2("the chosen color", f), "COREFERENT", (0, 0), "E2:chosen")

    def test_chosen_own_clause_before_and_after_the_reference(self):
        f = face(para("Choose a color, then draw a card for each permanent of the chosen "
                      "color."))
        self.resolved(e2("the chosen color", f), "COREFERENT", (0, 0), "E2:chosen")
        g = face(para("Tap each permanent of the chosen color, then choose a color."))
        self.unresolved(e2("the chosen color", g), "no-candidate", "E2:chosen")

    def test_chosen_two_choices_are_ambiguous(self):
        f = face(para("{T}: Choose a color."), para("{1}: Choose a color."),
                 para(self.COLOR))
        self.unresolved(e2("the chosen color", f), "ambiguous", "E2:chosen")

    def test_chosen_without_a_noun(self):
        f = face(para("{T}: Choose a color."), para("Draw a card for the chosen."))
        self.unresolved(e2("the chosen", f), "no-candidate", "E2:chosen")

    def test_noun_phrase_window(self):
        ok = face(para("{T}: Choose a nonbasic land card name."),
                  para("Spells with the chosen name cost {1} more."))
        self.resolved(e2("the chosen name", ok), "LINKED", (0, 0), "E2:chosen")
        far = face(para("{T}: Choose a big nonbasic land card name."),
                   para("Spells with the chosen name cost {1} more."))
        self.unresolved(e2("the chosen name", far), "no-candidate", "E2:chosen")
        tilde = face(para("{T}: Choose a ~ card name."),
                     para("Spells with the chosen name cost {1} more."))
        self.resolved(e2("the chosen name", tilde), "LINKED", (0, 0), "E2:chosen")

    def test_words_after_the_noun_do_not_matter(self):
        f = face(para("{T}: Choose a creature type."),
                 para("Tap the chosen creature type."))
        self.resolved(e2("the chosen creature", f), "LINKED", (0, 0), "E2:chosen")

    def test_noun_may_carry_a_plural_s(self):
        f = face(para("Whenever this creature attacks, choose one of those creatures.",
                      "Tap the chosen creature."))
        self.resolved(e2("the chosen creature", f), "COREFERENT", (0, 0), "E2:chosen")

    def test_noun_is_a_whole_word(self):
        f = face(para("{T}: Choose a colorless artifact."), para(self.COLOR))
        self.unresolved(e2("the chosen color", f), "no-candidate", "E2:chosen")

    def test_negated_choose_is_no_choice(self):
        for neg in ("can't", "don't", "cannot"):
            f = face(para(f"Players {neg} choose a color."), para(self.COLOR))
            self.unresolved(e2("the chosen color", f), "no-candidate", "E2:chosen")

    def test_chosen_by_you(self):
        for opener in ("Choose a color.",                         # opens its sentence
                       "When this artifact enters, choose a color.",  # after a comma
                       "Draw a card. You choose a color.",
                       "Draw a card. You may choose a color.",
                       "Draw a card then choose a color.",
                       "Draw a card and choose a color.",
                       "• Choose a color.",                       # CR 700.2
                       "Synthetic Label — Choose a color.",       # §I3a R4 label
                       "{T}: Choose a color.",                    # CR 602.1a
                       "+1: Choose a color."):
            f = face(para(*fx_clauses(opener)), para(self.COLOR))
            self.resolved(e2("the chosen color", f), "LINKED", (0, len(fx_clauses(opener)) - 1),
                          "E2:chosen")

    # -- another chooser (§I5.8 ruling 10)
    def test_another_choose_is_other_chooser(self):
        for other in ("Draw a card. Target opponent may secretly choose a color.",
                      "If this spell was kicked, instead choose a color.",
                      "Target opponent chooses a color."):
            f = face(para("{T}: Choose a color."), para(*fx_clauses(other)),
                     para(self.COLOR))
            self.unresolved(e2("the chosen color", f), "other-chooser", "E2:chosen")

    def test_chooses_or_chose_earlier_in_the_ability(self):
        for verb in ("chooses", "chose"):
            f = face(para("Choose a color.", f"Each opponent {verb} a number.",
                          "Tap each creature of the chosen color."))
            self.unresolved(e2("the chosen color", f), "other-chooser", "E2:chosen")

    def test_you_chose_in_the_own_clause(self):
        f = face(para("Choose a color.",
                      "If you chose a color, tap each creature of the chosen color."))
        self.unresolved(e2("the chosen color", f), "other-chooser", "E2:chosen")
        g = face(para("Choose a color.",
                      "Tap each creature of the chosen color if you chose a color."))
        self.resolved(e2("the chosen color", g), "COREFERENT", (0, 0), "E2:chosen")

    def test_chose_in_another_ability_of_another_noun_is_not_counted(self):
        f = face(para("{T}: Choose a color."),
                 para("Whenever an opponent chooses a number, draw a card."),
                 para(self.COLOR))
        self.resolved(e2("the chosen color", f), "LINKED", (0, 0), "E2:chosen")


def fx_clauses(text):
    return c.fx.sentence_spans(text)


# ------------------------------------------------------------------ E3

def e3(*clauses, ci=-1, n=0):
    clauses = list(clauses)
    ci = ci % len(clauses)
    return c.e3(clauses, ci, at(clauses[ci], "the copy", n))


class E3(unittest.TestCase):
    REF = "You may choose new targets for the copy."

    def product(self, got, clause):
        self.assertEqual((got["outcome"], got["reason"], got["class"]),
                         ("RESOLVED", None, "E3"), got)
        self.assertEqual(got["endpoint"], {"kind": "PRODUCT", "clause": clause})

    def unresolved(self, got, reason):
        self.assertEqual((got["outcome"], got["reason"], got["class"]),
                         ("UNRESOLVED", reason, "E3"), got)

    def test_earlier_clause(self):
        for w in c.E3_FOLLOW:
            self.product(e3(f"Copy {w} spell.", self.REF), 0)

    def test_earlier_in_the_same_clause(self):
        self.product(e3("Copy that spell and you may choose new targets for the copy."), 0)

    def test_later_in_the_same_clause_is_not_counted(self):
        self.unresolved(e3("Choose new targets for the copy, then copy target spell."),
                        "no-candidate")

    def test_copy_not_followed_by_a_listed_word(self):
        self.unresolved(e3("Create a copy of target spell.", self.REF), "no-candidate")

    def test_open_condition(self):
        for cond in ("When you copy a spell", "Whenever you copy a spell",
                     "If you copy a spell", "As long as you copy a spell",
                     "Unless you copy a spell"):
            self.unresolved(e3(f"{cond} draw a card.", self.REF), "no-candidate")

    def test_closed_condition_then_copy(self):
        for s in ("If you do, copy that spell.", "When you cast a spell, copy it.",
                  "If you do, then copy that spell.",
                  "Whenever you cast a spell, you may copy it."):
            self.product(e3(s, self.REF), 0)

    def test_closed_condition_with_other_words_before_the_copy(self):
        self.unresolved(e3("If you do, draw a card and copy that spell.", self.REF),
                        "no-candidate")

    def test_two_instructions_are_ambiguous(self):
        self.unresolved(e3("Copy target spell.", "Copy target spell.", self.REF),
                        "ambiguous")

    def test_nothing_printed(self):
        self.unresolved(e3(self.REF), "no-candidate")


# ------------------------------------------------------------------ E4

GETS = "Target creature gets +2/+2 until end of turn."
FLY = "It gains flying until end of turn."


def e4(phrase, *items, ci=-1, n=0):
    p = para(*items)
    ci = ci % len(p["clauses"])
    return c.e4(phrase, p["clauses"], ci, at(p["clauses"][ci], phrase, n), p["regions"])


class E4(unittest.TestCase):

    def obj(self, got, clause=0, span=(0, 6)):
        self.assertEqual((got["outcome"], got["reason"]), ("RESOLVED", None), got)
        self.assertEqual(got["endpoint"], {"kind": "OBJECT", "clause": clause,
                                           "mark_span": list(span)})

    def unresolved(self, got, reason):
        self.assertEqual((got["outcome"], got["reason"]), ("UNRESOLVED", reason), got)
        self.assertNotIn("endpoint", got)

    def test_base_case_and_class(self):
        got = e4("it", GETS, FLY)
        self.obj(got)
        self.assertEqual(got["class"], "E4:it")
        self.assertEqual(e4("that creature", GETS, "Untap that creature.")["class"],
                         "E4:that creature")

    # -- markers
    def test_expletive(self):
        for tail in ("it's night", "it is day", "it's your turn", "it is not their turn",
                     "it's an opponent's turn", "it’s the first turn"):
            self.unresolved(e4("it", GETS, f"Draw a card if {tail}."), "expletive")
        self.obj(e4("it", GETS, "Scry 1 if it's attacking."))

    def test_possessives_are_no_rule(self):
        for ph in c.POSSESSIVE:
            self.unresolved(e4(ph, GETS, f"Draw a card for {ph}."), "no-rule")
        self.unresolved(e4("that creature", GETS, "Draw cards equal to that creature's "
                                                  "power."), "no-rule")

    def test_it_s_is_not_a_possessive(self):
        self.obj(e4("it", "Target land becomes a 2/2 creature.", "It's still a land."))

    def test_plural_markers(self):
        self.assertEqual(set(c.PLURAL), set(hr.R3_PLURAL_MARKERS))
        for ph in c.PLURAL:
            self.unresolved(e4(ph, GETS, f"Untap {ph}."), "plural-r3")

    def test_unlisted_marker_is_no_rule(self):
        self.unresolved(e4("this", GETS, "Untap this."), "no-rule")

    # -- 1. marks
    def test_marks(self):
        self.unresolved(e4("it", "Creatures get +1/+1.", FLY), "no-candidate")
        self.unresolved(e4("it", GETS, "Target artifact gains flying.", FLY), "ambiguous")

    def test_the_target_of_is_not_a_mark(self):
        self.unresolved(e4("it", "~ can be the target of spells this turn.", FLY),
                        "no-candidate")
        self.obj(e4("it", "~ can be the target of spells.", GETS, FLY), clause=1)

    def test_mark_after_the_reference_is_not_counted(self):
        self.unresolved(e4("it", "Untap it and target creature."), "no-candidate")

    # -- 2. the single object mark
    def test_prefixed_marks(self):
        self.obj(e4("it", "Another target creature gets +1/+1.", FLY),
                 span=(0, len("Another target")))
        for pre in ("each", "all"):
            s = f"Untap {pre} target creature."
            self.obj(e4("it", s, FLY), span=(6, 6 + len(f"{pre} target")))
        s = "Untap up to one target creature."
        self.obj(e4("it", s, FLY), span=(6, 6 + len("up to one target")))

    def test_plural_marks_are_no_candidate(self):
        for pre in ("two", "three", "four", "X", "any number of", "up to two",
                    "up to three"):
            self.unresolved(e4("it", f"Untap {pre} target creatures.", FLY),
                            "no-candidate")

    def test_noun_within_three_words(self):
        self.obj(e4("that creature", "Target attacking or blocking creature gets +4/+0.",
                    "Untap that creature."))
        self.unresolved(e4("that creature", "Target big attacking or blocking creature "
                                            "gets +4/+0.", "Untap that creature."),
                        "no-candidate")

    def test_numbers_and_symbols_are_not_words(self):
        self.obj(e4("it", "Target 1/1 red creature gains flying.", FLY))

    def test_plural_s_and_possessive_are_read_off(self):
        self.assertEqual(c.mark_np("target creatures", 0, 6)["noun"][2], "creature")
        s = "Until end of turn, double target creature's power and it gains first strike."
        self.obj(e4("it", s), span=(s.index("target"), s.index("target") + 6))

    def test_punctuation_ends_the_noun_search(self):
        for ch in c.NOUN_STOP:
            m = c.mark_np(f"Choose any target{ch} creature", 11, 17)
            self.assertIsNone(m["noun"], ch)
        self.unresolved(e4("it", "~ deals 3 damage to any target. If a creature is dealt "
                                 "damage this way, it gets +5/+0."), "no-candidate")

    def test_player_marks_are_no_candidate(self):
        for noun in c.PLAYER_NOUNS:
            self.unresolved(e4("it", f"Target {noun} gains 1 life.", FLY), "no-candidate")

    def test_no_object_noun_is_no_candidate(self):
        self.unresolved(e4("it", "Untap target Mountain.", FLY), "no-candidate")

    # -- 3. agreement
    def test_agreement(self):
        self.unresolved(e4("that spell", GETS, "Untap that spell."), "no-candidate")
        self.obj(e4("that card", "Target permanent gains hexproof.", "That card gains "
                                                                      "flying."))
        self.obj(e4("that permanent", GETS, "That permanent gains flying."))
        self.obj(e4("that creature", GETS, "Untap that creature."))

    # -- the between text and the own governing region
    def test_own_governing_region_is_left_out(self):
        s = "Sacrifice it at the beginning of the next end step."
        self.obj(e4("it", GETS, (s, [reg(s, "sacrifice", "Sacrifice")])))

    def test_own_region_is_not_left_out_in_the_mark_clause(self):
        s = "Target creature gets +2/+2 and you sacrifice it."
        self.unresolved(e4("it", (s, [reg(s, "sacrifice", "sacrifice")])), "continuity")

    def test_own_region_holding_two_heads_is_not_left_out(self):
        s = "Draw a card and sacrifice it."
        self.unresolved(e4("it", GETS, (s, [reg(s, "draw", "Draw")])),
                        "competing-antecedent")

    # -- 4. continuity (CR 400.7)
    def test_mark_region_head_in_zone(self):
        for head in c.ZONE:
            s = f"{head.capitalize()} target creature."
            self.unresolved(e4("it", (s, [reg(s, head, s.split()[0])]), FLY),
                            "continuity")

    def test_zone_word_directly_before_the_mark(self):
        self.unresolved(e4("it", "Synthetic — Exile target creature.", FLY), "continuity")
        self.obj(e4("it", "Synthetic — Untap target creature.", FLY),
                 span=(len("Synthetic — Untap "), len("Synthetic — Untap target")))

    def test_zone_head_between(self):
        r = "Return a land you control to its owner's hand."
        self.unresolved(e4("it", GETS, (r, [reg(r, "return", "Return")]), FLY),
                        "continuity")

    def test_continuity_text_between(self):
        for s in ("You may put a land onto the battlefield.",
                  "Cast spells from your hand this turn.",
                  "Put the top card of your library into your graveyard."):
            self.unresolved(e4("it", GETS, s, FLY), "continuity")

    def test_continuity_text_before_the_mark_within_80(self):
        pre = "Play lands from your graveyard."
        self.unresolved(e4("it", pre, GETS, FLY), "continuity")
        pad = "Creatures you control get +1/+1 and have vigilance, reach and trample."
        far = pre + " " + pad
        self.assertGreater(len(far) + 1, c.CONT_WINDOW)
        self.obj(e4("it", pre, pad, GETS, FLY), clause=2)

    def test_card_noun_phrase_in_a_zone(self):
        for s in ("Untap target creature card in your graveyard.",
                  "Untap target instant or sorcery card in your graveyard.",
                  "Untap target card from exile.",
                  "Untap target creature card you own in a graveyard.",
                  "Untap target creature cards in your hand."):
            self.unresolved(e4("it", s, FLY), "continuity")

    def test_card_noun_phrase_non_arms(self):
        for s in ("Untap target creature card, in your graveyard.",       # comma
                  "Untap target creature card in your own big graveyard.",  # >2 words
                  "Untap target creature card in play."):                # no zone
            self.obj(e4("it", s, FLY), span=(6, 12))

    # -- 5. competing antecedent
    def test_mark_region_head_in_create(self):
        for head in c.CREATE:
            s = f"{head.capitalize()} target creature."
            self.unresolved(e4("it", (s, [reg(s, head, s.split()[0])]), FLY),
                            "competing-antecedent")

    def test_any_frozen_head_between(self):
        s = "Scry 1."
        self.unresolved(e4("it", GETS, (s, [reg(s, "scry", "Scry")]), FLY),
                        "competing-antecedent")

    def test_head_word_without_a_region_is_not_a_frozen_head(self):
        self.obj(e4("it", GETS, "Put a +1/+1 counter on it."))
        self.obj(e4("it", GETS, "Scry 1.", FLY))

    def test_copy_token_create_between(self):
        for w in c.COMPETE_WORDS:
            self.unresolved(e4("it", GETS, f"Untap the {w}.", FLY),
                            "competing-antecedent")

    def test_copy_token_create_within_60_before_the_mark(self):
        self.unresolved(e4("it", "If the copy resolves, target creature gains flying.",
                           FLY), "competing-antecedent")
        pad = "Creatures you control get +1/+1 and have vigilance and reach."
        self.obj(e4("it", "Untap the copy.", pad, GETS, FLY), clause=2)

    def test_mass_noun_between(self):
        for w in c.MASS:
            self.unresolved(e4("it", GETS, f"Untap the {w}.", FLY),
                            "competing-antecedent")

    def test_self_reference_between_for_it(self):
        for s in ("Untap ~.", "Untap this artifact.", "Untap this creature."):
            self.unresolved(e4("it", GETS, s, FLY), "competing-antecedent")
            self.obj(e4("that creature", GETS, s, "Untap that creature."))
        self.obj(e4("it", GETS, "Untap ~'s controller.", FLY))

    def test_indefinite_object_noun_phrase(self):
        for s in ("Untap a creature.", "Untap an artifact.", "Untap another land.",
                  "Untap each nontoken creature.", "Untap any big red creature."):
            self.unresolved(e4("it", GETS, s, FLY), "competing-antecedent")
            self.unresolved(e4("it", s, GETS, FLY), "competing-antecedent")
        self.obj(e4("it", GETS, "Untap a big red tapped creature.", FLY))   # 3 words

    def test_mark_s_own_another_is_not_a_competitor(self):
        self.obj(e4("it", "Put a +1/+1 counter on another target creature you control.",
                    "It gains hexproof until end of turn."),
                 span=(len("Put a +1/+1 counter on "),
                       len("Put a +1/+1 counter on another target")))

    def test_choose_or_chosen(self):
        for s in ("Choose a color.", "Untap the chosen."):
            self.unresolved(e4("it", GETS, s, FLY), "competing-antecedent")
            self.unresolved(e4("it", s, GETS, FLY), "competing-antecedent")


# ------------------------------------------------------------------ E5 / E6 / residue

class E5E6Residue(unittest.TestCase):

    def test_e5(self):
        s = "Untap each creature with the same name as that artifact."
        self.assertEqual(c.e5(s, at(s, "the same")),
                         {"outcome": "NOT-COREFERENCE", "reason": None, "class": "E5"})
        s = "Untap each creature that shares the same."
        self.assertEqual(c.e5(s, at(s, "the same")),
                         {"outcome": "UNRESOLVED", "reason": "no-rule", "class": "E5"})

    def test_e6(self):
        self.assertEqual(c.e6("conditionality", True)["outcome"], "OUT-OF-SCOPE")
        self.assertIsNone(c.e6("conditionality", False))
        for kind in ("coreference", "kind-unclear", "cr607-linkage"):
            self.assertIsNone(c.e6(kind, True), kind)

    def test_residue(self):
        for ph in c.RESIDUE:
            self.assertEqual(c.residue(ph), {"outcome": "UNRESOLVED", "reason": "no-rule",
                                             "class": None})

    def test_overlap_inside_a_longer_candidate(self):
        spans = [(0, 20, "the chosen creatures"), (0, 24, "the chosen creatures get")]
        self.assertEqual(c.overlap(spans, {"the chosen creatures": 1,
                                           "the chosen creatures get": 1}), [True, False])

    def test_overlap_printed_fewer_times(self):
        spans = [(0, 15, "the exiled card")]
        self.assertEqual(c.overlap(spans, {"the exiled card": 0}), [True])
        self.assertEqual(c.overlap(spans, {"the exiled card": 1}), [False])

    def test_no_overlap(self):
        spans = [(0, 2, "it"), (10, 12, "it"), (20, 33, "that creature")]
        self.assertEqual(c.overlap(spans, {"it": 2, "that creature": 1}),
                         [False, False, False])


# ------------------------------------------------------------------ §I5.7 discovery

class Discovery(unittest.TestCase):

    def test_forms(self):
        self.assertEqual(len(c.DISCOVERY), 28)

    def test_covered_and_uncovered(self):
        line = "Return the returned card. He draws. Put the rest into his hand."
        got = c.discovery(line, ["the returned card"])
        self.assertEqual(got, [("the returned", line.index("the returned"), True),
                               ("he", line.index("He"), False),
                               ("the rest", line.index("the rest"), False),
                               ("his", line.index("his"), False)])

    def test_prefix_is_a_plain_string_prefix(self):
        line = "Untap the card."
        self.assertEqual(c.discovery(line, ["The Cards"]),
                         [("the card", 6, True)])
        self.assertEqual(c.discovery(line, ["a card"]), [("the card", 6, False)])

    def test_whole_word_and_case_insensitive(self):
        self.assertEqual(c.discovery("THE CARDS and the herd here, herself, the other.", []),
                         [("the cards", 0, False), ("the other", 38, False)])

    def test_repeated_occurrences_count_separately(self):
        self.assertEqual(len(c.discovery("him and him", [])), 2)


# ------------------------------------------------------------------ negative controls

SYN_CR = "\n".join(f"{rule}. Synthetic rule text: {phrase}, and more."
                   for rule, phrase in c.CR_OPERATIVE.items())


def expected_rep(want=None):
    """A synthetic report measuring exactly the given §I5 figures."""
    want = c.EXPECTED if want is None else want
    reach = {"total": dict(want["total"]), "by_rule": copy.deepcopy(want["by_rule"]),
             "by_rule_reason": [{"rule": r, "reason": s, "candidates": n}
                                for (r, s), n in want["by_rule_reason"].items()],
             "e2_endpoint_kinds": dict(want["e2_endpoint_kinds"]),
             "delayed_trigger_subset": {
                 "candidates": want["delayed_trigger_subset"]["candidates"],
                 "by_outcome_or_reason": {k: v for k, v in
                                          want["delayed_trigger_subset"].items()
                                          if k != "candidates"}}}
    cov = {k: {"total": t, "in_set": i, "out_of_set": t - i}
           for k, (t, i) in want["coverage"].items()}
    disc = {f: {"covered": 0, "uncovered": 0} for f in c.DISCOVERY}
    disc["he"].update(want["discovery"])
    return {"reach": reach, "coverage": {"by_kind": cov, "discovery": disc},
            "candidates": []}


def quiet(fn, *a):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*a)


SYN_CARD = {"name": "Synthetic Widget", "oracle_id": "synthetic", "layout": "normal",
            "type_line": "Artifact",
            "oracle_text": "Exile target artifact. Return it at the beginning of the next "
                           "end step.\n{T}: Draw a card."}

# The C04-RESOLVE synthetic negative controls, restated here (not read from the
# module): (text, type line, rule, phrase, outcome, reason, endpoint kind).
SYNTHETIC = (
    ("Target creature gets +2/+2 until end of turn. Sacrifice it at the beginning of "
     "the next end step.", "Instant", "E4", "it", "RESOLVED", None, "OBJECT"),
    ("+ {1} — Exile target creature. Return it at the beginning of the next end step.",
     "Instant", "E4", "it", "UNRESOLVED", "continuity", None),
    ("Target creature gets +3/+3 until end of turn. Exile ~ with three time counters "
     "on it.", "Instant", "E4", "it", "UNRESOLVED", "competing-antecedent", None),
    ("you may play that card and you may spend mana as though it were mana of any "
     "color to cast it. When you cast a spell this way, draw a card.", "Instant",
     "E1", "this way", "UNRESOLVED", "no-candidate", None),
    ("create a token. For each Aura attached to ~, create a token. Sacrifice all "
     "tokens created this way.", "Instant", "E1", "this way", "UNRESOLVED",
     "ambiguous", None),
    ("sacrifice a permanent or discard a card this way.", "Instant", "E1", "this way",
     "UNRESOLVED", "ambiguous", None),
    ("Target creature gets +2/+2 until end of turn. Put a +1/+1 counter on it.",
     "Instant", "E4", "it", "RESOLVED", None, "OBJECT"),
    ("Put a +1/+1 counter on another target creature you control. It gains hexproof "
     "until end of turn.", "Instant", "E4", "it", "RESOLVED", None, "OBJECT"),
    ("Until end of turn, double target creature's power and it gains first strike.",
     "Instant", "E4", "it", "RESOLVED", None, "OBJECT"),
    ("Target attacking or blocking creature gets +4/+0 until end of turn. Destroy that "
     "creature at the beginning of the next end step.", "Instant", "E4",
     "that creature", "RESOLVED", None, "OBJECT"),
    ("~ deals 3 damage to any target. If a creature is dealt damage this way, it gets "
     "+5/+0 until end of turn.", "Instant", "E4", "it", "UNRESOLVED", "no-candidate",
     None),
    ("{T}: Choose a color. Creatures you control gain protection from the chosen "
     "color until end of turn.", "Artifact", "E2", "the chosen color", "RESOLVED",
     None, "COREFERENT"),
    ("Choose target creature with mana value 3 or less. If this spell was kicked, "
     "instead choose target creature. Exile the chosen creature.", "Sorcery", "E2",
     "the chosen creature", "UNRESOLVED", "other-chooser", None),
    ("Whenever this creature attacks, choose one of those creatures. Tap the chosen "
     "creature.", "Creature", "E2", "the chosen creature", "RESOLVED", None,
     "COREFERENT"),
    ("{X}: Choose a color. Target opponent exiles the top X cards of their library. "
     "For each card of the chosen color exiled this way, draw a card.", "Artifact",
     "E2", "the chosen color exiled", "RESOLVED", None, "COREFERENT"),
)


class NegativeControls(unittest.TestCase):

    def test_card_keyed_rule_halts(self):
        self.assertEqual(hr.assert_not_card_keyed(c.RULES, NAMES),
                         [r["id"] for r in c.RULES])
        for key in ("id", "kind", "cr", "pattern"):
            for bad in (NAMES[0], "00000000-0000-0000-0000-000000000000"):
                rule = dict(c.RULES[0], **{key: f"{c.RULES[0][key]} {bad}"})
                self.assertTrue(halts(lambda r=rule: hr.assert_not_card_keyed(
                    list(c.RULES) + [r], NAMES)), (key, bad))

    def test_rule_table_shape(self):
        self.assertEqual([r["kind"] for r in c.RULES],
                         ["E1", "E2", "E3", "E4", "E5", "E6", "residue"])
        for r in c.RULES:
            self.assertEqual(set(r), {"id", "kind", "cr", "pattern"})

    def test_cr_missing_an_operative_phrase_stops(self):
        self.assertEqual(c.cr_read(SYN_CR), c.CR_OPERATIVE)
        for rule in ("400.7", "607.2a", "607.2b", "607.2d", "608.2c", "707.10"):
            phrase = c.CR_OPERATIVE[rule]
            self.assertTrue(halts(lambda t=SYN_CR.replace(phrase, "elided"): c.cr_read(t)),
                            rule)
            lines = [ln for ln in SYN_CR.split("\n") if not ln.startswith(rule + ".")]
            self.assertTrue(halts(lambda t="\n".join(lines): c.cr_read(t)), rule)

    def test_rigged_i4_figure_halts(self):
        fig, c02 = copy.deepcopy(c.I4), {"p4": copy.deepcopy(c.I4)}
        self.assertEqual(c.reconcile_i4(fig, c02), c.I4)
        for k in c.I4:
            for side in ("measured", "c02", "stated"):
                f, p, w = copy.deepcopy(fig), copy.deepcopy(c02), copy.deepcopy(c.I4)
                tgt = {"measured": f, "c02": p["p4"], "stated": w}[side]
                tgt[k] = ({kk: v + 1 for kk, v in tgt[k].items()}
                          if isinstance(tgt[k], dict) else tgt[k] + 1)
                self.assertTrue(halts(lambda: c.reconcile_i4(f, p, w)), (k, side))

    def test_rigged_p4_line_halts(self):
        ctx = c.card_context(SYN_CARD)
        self.assertEqual(len(ctx["tied"]), 2)
        real = aq._card_lines
        for rig in (lambda card: [real(card)[0] + " "] + real(card)[1:],
                    lambda card: real(card)[:1]):
            with mock.patch.object(aq, "_card_lines", rig):
                self.assertTrue(halts(lambda: c.card_context(SYN_CARD)))

    def test_rigged_reach_figure_fails_check_reach(self):
        rep = expected_rep()
        self.assertEqual(c.reach_differences(rep), [])
        self.assertEqual(quiet(c.check_reach, rep), 0)
        rigs = []
        r = expected_rep(); r["reach"]["by_rule"]["E1"]["RESOLVED"] += 1; rigs.append(r)
        r = expected_rep(); r["reach"]["total"]["candidates"] -= 1; rigs.append(r)
        r = expected_rep(); r["reach"]["by_rule_reason"][0]["candidates"] += 1; rigs.append(r)
        r = expected_rep()
        r["reach"]["by_rule_reason"].append({"rule": "E3", "reason": "ambiguous",
                                             "candidates": 1})
        rigs.append(r)
        r = expected_rep(); r["reach"]["e2_endpoint_kinds"]["LINKED"] += 1; rigs.append(r)
        r = expected_rep()
        r["reach"]["delayed_trigger_subset"]["by_outcome_or_reason"]["overlap"] = 1
        rigs.append(r)
        r = expected_rep(); r["coverage"]["by_kind"]["coreference"]["in_set"] += 1
        rigs.append(r)
        r = expected_rep(); r["coverage"]["discovery"]["him"]["uncovered"] += 1
        rigs.append(r)
        for i, r in enumerate(rigs):
            self.assertEqual(len(c.reach_differences(r)), 1, i)
            self.assertNotEqual(quiet(c.check_reach, r), 0, i)
        bad = copy.deepcopy(c.EXPECTED["by_rule"]); bad["E1"]["RESOLVED"] += 1
        self.assertNotEqual(quiet(c.check_reach, expected_rep(),
                                  dict(c.EXPECTED, by_rule=bad)), 0)

    def test_expected_is_every_i5_figure(self):
        e = c.EXPECTED
        self.assertEqual(e["total"], {"candidates": 5856, "RESOLVED": 1784,
                                      "UNRESOLVED": 3230, "NOT-COREFERENCE": 119,
                                      "OUT-OF-SCOPE": 723})
        self.assertEqual({k: v["RESOLVED"] for k, v in e["by_rule"].items()},
                         {"E1": 529, "E2": 498, "E3": 196, "E4": 561, "E5": 0, "E6": 0,
                          "residue": 0})
        self.assertEqual(e["by_rule"]["E5"]["NOT-COREFERENCE"], 119)
        self.assertEqual(e["by_rule"]["E6"]["OUT-OF-SCOPE"], 723)
        self.assertEqual(len(e["by_rule_reason"]), 18)
        self.assertEqual(sum(e["by_rule_reason"].values()), 3230)
        self.assertEqual(e["e2_endpoint_kinds"], {"LINKED": 322, "COREFERENT": 176})
        self.assertEqual(e["delayed_trigger_subset"],
                         {"candidates": 450, "RESOLVED": 25, "no-candidate": 186,
                          "no-rule": 108, "plural-r3": 55, "continuity": 48,
                          "competing-antecedent": 26, "ambiguous": 2})
        self.assertEqual(e["coverage"], {"coreference": (21672, 2844),
                                         "conditionality": (8642, 723),
                                         "cr607-linkage": (741, 741),
                                         "kind-unclear": (1548, 1548)})
        self.assertEqual(e["discovery"], {"uncovered": 1670, "covered": 2})

    def test_absolute_root_fails_portability(self):
        self.assertEqual(hr.portability_violations(c.render({"x": "experiments/out"})), [])
        self.assertTrue(hr.portability_violations(c.render({"x": str(c.ROOT)})))
        self.assertTrue(hr.portability_violations(c.render({"x": str(Path.home())})))

    def test_synthetic_controls(self):
        for text, tl, rule, phrase, outcome, reason, kind in SYNTHETIC:
            got = [x for x in c.synthetic(text, tl) if x["rule"] == rule
                   and (x["phrase"] + " ").startswith(phrase + " ")]
            self.assertEqual(len(got), 1, (rule, phrase, text[:30]))
            g = got[0]
            self.assertEqual((g["outcome"], g["reason"],
                              (g.get("endpoint") or {}).get("kind")),
                             (outcome, reason, kind), (rule, phrase, text[:30]))


# ------------------------------------------------------------------ regression (pinned corpus)

CORPUS_REL = "data/raw/oracle-cards.jsonl.gz"

# Every card §I5.3, §I5.5, §I5.6 and §I5.7 names, by row_id only:
# row_id -> (rule, outcome, reason, endpoint kind, endpoint clause address or None).
REGRESSION = {
    # §I5.3 E4 step 4: the card noun phrase, a conservative miss.
    "75ffebc4-8db9-4de6-a330-e3f41cdccecc:0:0:2@0:that card":
        ("E4", "UNRESOLVED", "continuity", None, None),
    # §I5.3 E2 outcome: both places hold a candidate (Captain question 11).
    "f1fee486-660e-4356-896e-671e8b675ad8:0:2:0@44:the exiled card":
        ("E2", "UNRESOLVED", "ambiguous", None, None),
    # §I5.3 E4 step 5: a mass noun; "~" before "it".
    "d5dc00cb-1510-4ce9-8dd9-0722f65d34b4:0:0:1@34:it":
        ("E4", "UNRESOLVED", "competing-antecedent", None, None),
    "bc8213f9-bef7-4077-a919-4347ec373de7:0:0:1@36:it":
        ("E4", "UNRESOLVED", "competing-antecedent", None, None),
    # §I5.5 delayed-trigger subset, RESOLVED (four named cards).
    "07190a8b-2a59-45b3-9fbf-505161698a9c:0:0:3@10:it":
        ("E4", "RESOLVED", None, "OBJECT", "07190a8b-2a59-45b3-9fbf-505161698a9c:0:0:0"),
    "092ceffb-1ee4-452c-b15e-5b79267d42a6:0:1:3@10:it":
        ("E4", "RESOLVED", None, "OBJECT", "092ceffb-1ee4-452c-b15e-5b79267d42a6:0:1:0"),
    "4f427de6-b551-4699-b78a-44ff668198d8:0:0:1@8:it":
        ("E4", "RESOLVED", None, "OBJECT", "4f427de6-b551-4699-b78a-44ff668198d8:0:0:0"),
    "0b8e3f9b-a4da-49a3-8545-ce7a265e5856:0:0:1@8:that creature":
        ("E4", "RESOLVED", None, "OBJECT", "0b8e3f9b-a4da-49a3-8545-ce7a265e5856:0:0:0"),
    # §I5.5 interface/5 readings: frozen head and the mark's own "another".
    "9519a4ea-c4a0-4127-b06a-aac9ffaf7a32:0:1:1@46:that creature":
        ("E4", "RESOLVED", None, "OBJECT", "9519a4ea-c4a0-4127-b06a-aac9ffaf7a32:0:1:0"),
    # §I5.5 E2 readings: a bulleted choice; an own-clause choice.
    "400b2e17-ee48-4e22-a8a6-a607c215d1a2:0:1:1@33:the chosen name until":
        ("E2", "RESOLVED", None, "COREFERENT",
         "400b2e17-ee48-4e22-a8a6-a607c215d1a2:0:1:0"),
    "0c85a577-db82-4a36-bc42-49644eba1cf2:0:1:0@258:the chosen player or":
        ("E2", "RESOLVED", None, "COREFERENT",
         "0c85a577-db82-4a36-bc42-49644eba1cf2:0:1:0"),
    # §I5.6 row 1: E1 EVENT, the right region.
    "9103f01f-e60b-4cda-9102-edc4aef74cc3:0:0:0@154:this way":
        ("E1", "RESOLVED", None, "EVENT", "9103f01f-e60b-4cda-9102-edc4aef74cc3:0:0:0"),
    "e0edb2fc-2533-407c-85e5-4337f4233f05:0:2:0@120:this way":
        ("E1", "RESOLVED", None, "EVENT", "e0edb2fc-2533-407c-85e5-4337f4233f05:0:2:0"),
    "b233473d-d22b-45e4-9fe7-55d1170a788b:0:0:1@47:this way":
        ("E1", "RESOLVED", None, "EVENT", "b233473d-d22b-45e4-9fe7-55d1170a788b:0:0:0"),
    "16f6438d-2a29-41cb-bf0c-4d02bd66112b:0:0:1@58:this way":
        ("E1", "RESOLVED", None, "EVENT", "16f6438d-2a29-41cb-bf0c-4d02bd66112b:0:0:0"),
    # §I5.6 row 2: E1 UNRESOLVED (never the reference's own region).
    "14290772-ca17-4a55-86b2-7a638929b12d:0:1:1@34:this way":
        ("E1", "UNRESOLVED", "no-candidate", None, None),
    "87966759-206a-4a2d-bf78-86f727c29972:0:1:2@30:this way":
        ("E1", "UNRESOLVED", "no-candidate", None, None),
    # §I5.6 row 3: E1 detector-reach.
    "fab491b0-b820-4027-996f-390c97df1e96:0:0:1@77:this way":
        ("E1", "UNRESOLVED", "detector-reach", None, None),
    # §I5.6 row 4: E2 LINKED.
    "66418c65-a15f-489e-8a2d-6cee1b5d977c:0:2:0@34:the chosen color":
        ("E2", "RESOLVED", None, "LINKED", "66418c65-a15f-489e-8a2d-6cee1b5d977c:0:1:0"),
    "77a000de-76d9-44f8-9789-875aa9f576e7:0:1:0@50:the exiled cards":
        ("E2", "RESOLVED", None, "LINKED", "77a000de-76d9-44f8-9789-875aa9f576e7:0:0:0"),
    # §I5.1 overlap: the shorter form inside it.
    "77a000de-76d9-44f8-9789-875aa9f576e7:0:1:0@50:the exiled card":
        ("residue", "UNRESOLVED", "overlap", None, None),
    # §I5.6 row 5: E3 PRODUCT / E5 NOT-COREFERENCE.
    "85845b6c-abb5-4591-b987-a375972cf25b:0:1:1@31:the copy":
        ("E3", "RESOLVED", None, "PRODUCT", "85845b6c-abb5-4591-b987-a375972cf25b:0:1:0"),
    "85845b6c-abb5-4591-b987-a375972cf25b:0:0:0@55:the same":
        ("E5", "NOT-COREFERENCE", None, None, None),
    # §I5.6 row 6: E4 OBJECT after one single-object target.
    "634d6357-af76-4e25-8c63-81522bc726f5:0:1:2@0:it":
        ("E4", "RESOLVED", None, "OBJECT", "634d6357-af76-4e25-8c63-81522bc726f5:0:1:0"),
    "1ef73b3b-ab4a-494b-b969-dcde995cee34:0:0:1@0:that permanent":
        ("E4", "RESOLVED", None, "OBJECT", "1ef73b3b-ab4a-494b-b969-dcde995cee34:0:0:0"),
    "8c166a06-b056-4a05-ae23-715289e12e36:0:0:1@0:it":
        ("E4", "RESOLVED", None, "OBJECT", "8c166a06-b056-4a05-ae23-715289e12e36:0:0:0"),
    "5be3243a-6840-4601-96c8-ffb756041d49:0:1:1@0:it":
        ("E4", "RESOLVED", None, "OBJECT", "5be3243a-6840-4601-96c8-ffb756041d49:0:1:0"),
    # §I5.6 row 7: a token, copy, other creature or chosen ability in play.
    "a34b7416-cfe3-4a1e-a8c1-a3056b747519:0:1:1@10:it":
        ("E4", "UNRESOLVED", "competing-antecedent", None, None),
    "be094704-5232-4b10-beeb-aa9bbfae063d:0:0:2@10:it":
        ("E4", "UNRESOLVED", "continuity", None, None),
    "92b91910-9b65-4421-8eef-a33793161089:0:0:2@10:it":
        ("E4", "UNRESOLVED", "competing-antecedent", None, None),
    "b3a479d4-3e36-496b-abf8-b83231628d76:0:0:1@11:it":
        ("E4", "UNRESOLVED", "competing-antecedent", None, None),
    "4433a5fd-2daa-440a-b9cc-4ad028358cbc:0:0:0@124:it":
        ("E4", "UNRESOLVED", "competing-antecedent", None, None),
    # §I5.6 row 8: after exile, return, or put/cast from a zone (CR 400.7).
    "b23a3d30-6b8e-4aad-890f-db0c3af43ace:0:1:1@7:that card":
        ("E4", "UNRESOLVED", "continuity", None, None),
    "f87bf51e-6218-4418-ae3e-98055e9601e4:0:0:2@6:it":
        ("E4", "UNRESOLVED", "continuity", None, None),
    "d66f7ee7-e9a1-4714-b79c-8c86c6b6d5dc:0:0:2@10:it":
        ("E4", "UNRESOLVED", "continuity", None, None),
    "9059a940-ac28-4322-a11b-af1d107b2edd:0:0:1@54:it":
        ("E4", "UNRESOLVED", "continuity", None, None),
    "00ba0c24-a671-493e-ba46-13e45d1818f1:0:1:1@51:it":
        ("E4", "UNRESOLVED", "continuity", None, None),
    # §I5.6 row 9: player mark / noun disagreement / plural mark.
    "c8c868f8-19a5-4cc5-b769-aa382f7b97ad:0:1:0@106:it":
        ("E4", "UNRESOLVED", "no-candidate", None, None),
    "ee565d5c-7a3a-481c-91aa-b982cf384220:0:0:0@96:that spell":
        ("E4", "UNRESOLVED", "no-rule", None, None),
    "169c468e-0e17-450b-8954-df47d78ad8f8:0:1:0@89:that spell":
        ("E4", "UNRESOLVED", "no-rule", None, None),
    "55b72176-e428-4d2a-a701-237e8c8de22e:0:0:2@110:it":
        ("E4", "UNRESOLVED", "no-candidate", None, None),
    # §I5.6 row 10: a subtype-named mark.
    "589186e0-3ebe-46a3-a9e7-798b1712fa93:0:0:1@0:it":
        ("E4", "UNRESOLVED", "no-candidate", None, None),
    # §I5.7 card test: in set, RESOLVED (OBJECT); in set, RESOLVED (LINKED).
    "9d08af23-9f4a-4097-9abc-3b17475ab744:0:0:1@6:that creature":
        ("E4", "RESOLVED", None, "OBJECT", "9d08af23-9f4a-4097-9abc-3b17475ab744:0:0:0"),
    "9d08af23-9f4a-4097-9abc-3b17475ab744:0:0:2@0:it":
        ("E4", "RESOLVED", None, "OBJECT", "9d08af23-9f4a-4097-9abc-3b17475ab744:0:0:0"),
    "bd9b9772-f5f9-4c6b-913e-7193bea5d0a7:0:1:0@53:the exiled card":
        ("E2", "RESOLVED", None, "LINKED", "bd9b9772-f5f9-4c6b-913e-7193bea5d0a7:0:0:0"),
}

# §I5.5's named delayed-trigger rows: their reference clause prints the subset phrase.
DELAYED_NAMED = ("07190a8b-2a59-45b3-9fbf-505161698a9c:0:0:3@10:it",
                 "092ceffb-1ee4-452c-b15e-5b79267d42a6:0:1:3@10:it",
                 "4f427de6-b551-4699-b78a-44ff668198d8:0:0:1@8:it",
                 "0b8e3f9b-a4da-49a3-8545-ce7a265e5856:0:0:1@8:that creature")

# §I5.6 rows 7-10: every E4 row of these cards is UNRESOLVED.
E4_UNRESOLVED_CARDS = (
    "a34b7416-cfe3-4a1e-a8c1-a3056b747519", "be094704-5232-4b10-beeb-aa9bbfae063d",
    "92b91910-9b65-4421-8eef-a33793161089", "b3a479d4-3e36-496b-abf8-b83231628d76",
    "4433a5fd-2daa-440a-b9cc-4ad028358cbc", "b23a3d30-6b8e-4aad-890f-db0c3af43ace",
    "f87bf51e-6218-4418-ae3e-98055e9601e4", "d66f7ee7-e9a1-4714-b79c-8c86c6b6d5dc",
    "9059a940-ac28-4322-a11b-af1d107b2edd", "00ba0c24-a671-493e-ba46-13e45d1818f1",
    "c8c868f8-19a5-4cc5-b769-aa382f7b97ad", "ee565d5c-7a3a-481c-91aa-b982cf384220",
    "169c468e-0e17-450b-8954-df47d78ad8f8", "55b72176-e428-4d2a-a701-237e8c8de22e",
    "589186e0-3ebe-46a3-a9e7-798b1712fa93")

# §I5.7 card test, out of set: P4 candidates by address@offset:phrase.
OUT_OF_SET = ("b1544f21-7e98-461b-aed5-e748b0168c52:0:0:1@0:its",
              "9d2d6479-531c-4ce1-b52b-00e36fa63b64:0:2:0@68:it",
              "9d2d6479-531c-4ce1-b52b-00e36fa63b64:0:2:0@74:its",
              "82004860-e589-4e38-8d61-8c0210e4ea39:0:0:0@36:that card")

# §I5.7 card test, uncovered: (oracle_id, P4 line, position in the line, form).
UNCOVERED = (("24227761-b50e-4b9e-93a2-e82d053b3e3d", 1, 24, "the sacrificed"),
             ("b5fd82b9-77de-4358-9ce7-915cc809a889", 4, 23, "him"))


class Regression(unittest.TestCase):
    """The cards §I5 names, measured from the pinned corpus through the C04
    pipeline: an outcome other than §I5's is a STOP to the Captain."""

    @classmethod
    def setUpClass(cls):
        path = hr.ROOT / CORPUS_REL
        if not path.exists():
            raise AssertionError(f"the pinned corpus {CORPUS_REL} is missing: the C04 "
                                 f"regression cases cannot run (a loud failure, never "
                                 f"a skip)")
        if halts(lambda: hr.verify_identities({CORPUS_REL: hr.I1[CORPUS_REL]})):
            raise AssertionError(f"the corpus at {CORPUS_REL} is not the pinned I1 "
                                 f"identity {hr.I1[CORPUS_REL]}")
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            cls.cards, _, _ = c.fc.load_corpus_gated()
        oids = sorted({k.split(":")[0] for k in list(REGRESSION) + list(OUT_OF_SET)}
                      | set(E4_UNRESOLVED_CARDS) | {u[0] for u in UNCOVERED})
        missing = [o for o in oids if o not in cls.cards]
        if missing:
            raise AssertionError(f"the pinned corpus lacks {missing}")
        cls.sub = {o: cls.cards[o] for o in oids}
        order, cls.ctxs, _ = c.extract(cls.sub)
        # Fixture roles are not under test (FIXTURES.json resolves against the
        # whole corpus); every other field comes from C04's own measure().
        with mock.patch.object(c, "_fixture_roles", lambda cards: {}):
            rows, _, _, cls.disc, _ = c.measure(cls.sub, order, cls.ctxs)
        cls.rows = {r["row_id"]: r for r in rows}

    def test_named_outcomes(self):
        for rid, (rule, outcome, reason, kind, clause) in REGRESSION.items():
            r = self.rows.get(rid)
            self.assertIsNotNone(r, f"no C04 row {rid}")
            ep = r["endpoint"] or {}
            self.assertEqual((r["rule"], r["outcome"], r["reason"], ep.get("kind"),
                              ep.get("clause")), (rule, outcome, reason, kind, clause), rid)

    def test_delayed_named_rows_are_in_the_subset(self):
        for rid in DELAYED_NAMED:
            self.assertIn(c.DELAYED_SUBSET, self.rows[rid]["ref_text"].lower(), rid)

    def test_named_e4_cards_resolve_nothing(self):
        for oid in E4_UNRESOLVED_CARDS:
            e4 = [r for r in self.rows.values()
                  if r["address"].startswith(oid + ":") and r["rule"] == "E4"]
            self.assertTrue(e4, oid)
            for r in e4:
                self.assertEqual(r["outcome"], "UNRESOLVED", r["row_id"])

    def test_out_of_set(self):
        for rid in OUT_OF_SET:
            oid = rid.split(":")[0]
            allr, _ = self.ctxs[oid]
            ctx = c.card_context(self.cards[oid])
            hit = []
            for r, loc in zip(allr, c.locate(ctx, allr)):
                p = ctx["tied"][r["line"]]
                if (f"{oid}:{p['face']}:{p['paragraph']}:{r['sentence']}"
                        f"@{loc['char_offset']}:{r['phrase']}") == rid:
                    hit.append(r)
            self.assertEqual(len(hit), 1, rid)
            self.assertEqual(hit[0]["kind"], "coreference", rid)
            self.assertFalse(c.in_set(hit[0]), rid)
            self.assertNotIn(rid, self.rows)

    def test_uncovered(self):
        for oid, li, pos, form in UNCOVERED:
            line = aq._card_lines(self.cards[oid])[li]
            _, refs = self.ctxs.get(oid, ([], []))
            got = c.discovery(line, [r["phrase"] for r in refs if r["line"] == li])
            self.assertIn((form, pos, False), got, oid)

    def test_rules_are_not_keyed_to_any_corpus_card(self):
        names = sorted({card["name"] for card in self.cards.values()})
        self.assertEqual(hr.assert_not_card_keyed(c.RULES, names),
                         [r["id"] for r in c.RULES])

    def test_pinned_cr_prints_every_operative_phrase(self):
        self.assertEqual(c.cr_read(), c.CR_OPERATIVE)
        for rule in c.CR_OPERATIVE:
            self.assertTrue(halts(lambda r=rule: c.cr_read(c._tampered_cr(r))), rule)


if __name__ == "__main__":
    unittest.main()
