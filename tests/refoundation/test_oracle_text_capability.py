"""C8.5I — the oracle-text capability, its oracle, and the ratified N2 rule.

`experiments/tier_engine.py` is untouched and remains the ORACLE. The two
implementations coexist; these tests are what makes "equivalent" measured.

TWO KINDS OF CLAIM, kept apart:

* **Successful values are VALUE_EXACT** against the engine, over the whole
  corpus where the behavior is corpus-dependent.
* **N2 is Captain-ratified authority** (2026-08-30), not merely inherited legacy
  behavior. It is asserted directly against its named witness, so a future
  reimplementation cannot quietly drop it and still pass a differential against
  an engine that happens to implement it.

THE FULL-CORPUS DIFFERENTIAL SKIPS WITHOUT THE CORPUS — `data/raw/` is
gitignored card data. The fixtures below are not a substitute for it and it is
not a substitute for them; C8.5I required both and the Worker result records the
full-corpus run.
"""

from __future__ import annotations

import ast
import subprocess
import sys
import unittest
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT, SRC

from mtj_foundry import oracle_text as ot
from mtj_foundry.paths import ProjectPaths

EXPERIMENTS = REPO_ROOT / "experiments"
CORPUS_FILE = ProjectPaths.for_root(REPO_ROOT).legacy_oracle_cards
MODULE = SRC / "mtj_foundry" / "oracle_text.py"
TIER_ENGINE_SHA = "54c3d189e015889ac28f304a58e3e06f5f9ceff9e0ac4586d4edf4dd77aab2e8"
PIPELINE_EMBED_SHA = "56d44e55e5c8c5a4d908ab3d250af531b226c15518010ba356567d6b912b37e8"


def engine():
    """The ORACLE, reached exactly as legacy callers reach it."""
    if str(EXPERIMENTS) not in sys.path:
        sys.path.insert(0, str(EXPERIMENTS))
    import tier_engine
    return tier_engine


# ---------------------------------------------------------------------------
# ADVERSARIAL FIXTURES
# ---------------------------------------------------------------------------

# GENUINELY NESTED — a reminder that itself contains a parenthetical. This is
# the shape the legacy flat regex corrupted; the corpus case is Devoted Mardu.
NESTED = ("create X Mardudes (tapped and attacking 1/1 red Warrior creature "
          "tokens (they attack this turn)). Sacrifice them")
MULTI_SPAN = "Flying (It can't be blocked.) Vigilance (It doesn't tap.)"
COMMA_REMINDER = "Ward {2} (Whenever this becomes a target, counter it unless...)"


class TestReminderParsing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.te = engine()

    def test_NESTED_reminder_parens_are_ONE_outermost_span(self):
        """The shape the legacy flat regex corrupted. Proven against that regex
        directly, so the test states what the scanner buys rather than only that
        two implementations agree."""
        spans = ot.paren_spans(NESTED)
        self.assertEqual(len(spans), 1, spans)
        body = ot.reminder_bodies(NESTED)[0]
        self.assertIn("(they attack this turn)", body)
        self.assertTrue(body.endswith("(they attack this turn)"), body)
        self.assertEqual(spans, self.te.find_paren_spans(NESTED))
        self.assertEqual(ot.strip_reminders(NESTED), self.te.strip_reminder(NESTED))
        self.assertNotIn("(", ot.strip_reminders(NESTED))
        self.assertNotIn(")", ot.strip_reminders(NESTED))

    def test_the_flat_regex_the_scanner_replaced_would_CORRUPT_that_case(self):
        """The counterfactual, so the erratum is demonstrated and not just cited:
        a flat pattern stops at the FIRST `)` and leaves a dangling one."""
        import re as _re
        flat = _re.sub(r"\([^)]*\)", "", NESTED)
        self.assertIn(")", flat, "the flat regex should leave a dangling paren")
        self.assertNotEqual(flat, ot.strip_reminders(NESTED))

    def test_an_unbalanced_LEADING_paren_completes_no_span_and_does_not_raise(self):
        text = "Flying (it can't be blocked"
        self.assertEqual(ot.paren_spans(text), [])
        self.assertEqual(ot.strip_reminders(text), text)
        self.assertEqual(ot.paren_spans(text), self.te.find_paren_spans(text))

    def test_an_unbalanced_TRAILING_paren_is_ignored(self):
        text = "Flying) vigilance"
        self.assertEqual(ot.paren_spans(text), [])
        self.assertEqual(ot.paren_spans(text), self.te.find_paren_spans(text))

    def test_multiple_spans_in_one_paragraph(self):
        self.assertEqual(len(ot.paren_spans(MULTI_SPAN)), 2)
        self.assertEqual(ot.reminder_bodies(MULTI_SPAN),
                         self.te.extract_reminder_spans(MULTI_SPAN))
        self.assertEqual(ot.strip_reminders(MULTI_SPAN),
                         self.te.strip_reminder(MULTI_SPAN))

    def test_a_reminder_body_containing_a_comma(self):
        """Fragment splitting must happen AFTER the strip, or the reminder's own
        comma invents a fragment."""
        self.assertEqual(ot.reminder_bodies(COMMA_REMINDER),
                         self.te.extract_reminder_spans(COMMA_REMINDER))
        self.assertEqual(ot.normalize_clause(COMMA_REMINDER), "ward {2}")

    def test_strip_and_extract_share_one_scanner(self):
        """The invariant the legacy erratum made explicit: the two can never
        disagree about where a span begins."""
        for text in (NESTED, MULTI_SPAN, COMMA_REMINDER, "no parens here", ""):
            with self.subTest(text=text[:24]):
                spans = ot.paren_spans(text)
                self.assertEqual(len(ot.reminder_bodies(text)), len(spans))
                removed = len(text) - len(ot.strip_reminders(text))
                self.assertEqual(removed, sum(e - s for s, e in spans))

    def test_normalize_reminder_does_not_strip_again(self):
        body = "tapped and attacking (1/1 red) tokens"
        self.assertEqual(ot.normalize_reminder(body),
                         self.te.normalize_reminder_body(body))
        self.assertIn("(1/1 red)", ot.normalize_reminder(body))

    def test_curly_quote_and_apostrophe_folding(self):
        text = "“Urza’s” ‘Rage’"
        self.assertEqual(ot.normalize_clause(text), self.te.normalize_clause_text(text))
        self.assertEqual(ot.normalize_clause(text), '"urza\'s" \'rage\'')

    def test_empty_paragraph(self):
        self.assertEqual(ot.normalize_clause(""), "")
        self.assertEqual(ot.paren_spans(""), [])
        self.assertEqual(ot.reminder_bodies(""), [])


class TestKeywordLines(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.te = engine()

    def test_SWIFTFOOT_BOOTS_grant_clause_is_NOT_keyword_only(self):
        """The 2026-07-10 defect: a raw substring prefix let "equipped..." match
        the keyword "Equip" and silently swallow the whole grant clause."""
        para = "equipped creature has hexproof and haste."
        self.assertFalse(ot.is_keyword_only(para, ["Equip"]))
        self.assertEqual(ot.is_keyword_only(para, ["Equip"]),
                         self.te.is_keyword_only_paragraph(para, ["Equip"]))

    def test_a_real_equip_cost_line_IS_keyword_only(self):
        self.assertTrue(ot.is_keyword_only("equip {1}", ["Equip"]))

    def test_HELM_OF_KALDRA_comma_bearing_multi_keyword_grant(self):
        para = "first strike, trample, and haste"
        kws = ["First strike", "Trample", "Haste"]
        self.assertEqual(ot.is_keyword_only(para, kws),
                         self.te.is_keyword_only_paragraph(para, kws))

    def test_where_param_is_positive_and_the_mismatched_variable_negative(self):
        kws = ["Kicker"]
        good = "kicker x, where x is the number of creatures you control."
        bad = "kicker x, where y is the number of creatures you control."
        self.assertTrue(ot.is_keyword_only(good, kws))
        self.assertFalse(ot.is_keyword_only(bad, kws))
        for para in (good, bad):
            with self.subTest(para=para[:20]):
                self.assertEqual(ot.is_keyword_only(para, kws),
                                 self.te.is_keyword_only_paragraph(para, kws))

    def test_an_em_dash_ability_word_line_is_NOT_keyword_only(self):
        """An em dash after the keyword name marks an ability word introducing
        its own sentence, which is definitionally not a bare keyword line."""
        para = "domain — draw a card for each basic land type."
        self.assertFalse(ot.is_keyword_only(para, ["Domain"]))
        self.assertEqual(ot.is_keyword_only(para, ["Domain"]),
                         self.te.is_keyword_only_paragraph(para, ["Domain"]))

    def test_a_keyword_ACTION_with_target_is_NOT_keyword_only(self):
        para = "regenerate target creature."
        self.assertFalse(ot.is_keyword_only(para, ["Regenerate"]))
        self.assertEqual(ot.is_keyword_only(para, ["Regenerate"]),
                         self.te.is_keyword_only_paragraph(para, ["Regenerate"]))

    def test_keyword_instances_longest_first(self):
        """A short name must not prefix-match inside a longer one's fragment.

        The fixture has to DISCRIMINATE: an earlier version used
        ("first strike", ["Strike", "First strike"]), where the short name
        matches under neither ordering — so it passed with the ordering removed
        and proved nothing. Here the short name genuinely matches by prefix, so
        the two orderings give different params."""
        para = "protection from white"
        kws = ["Protection", "Protection from white"]
        self.assertEqual(ot.keyword_instances(para, kws),
                         [{"keyword": "protection from white", "param": None}])
        # shortest-first would have produced param "from white" instead
        self.assertIsNone(ot.keyword_instances(para, kws)[0]["param"])
        self.assertEqual(ot.keyword_instances(para, kws),
                         self.te.parse_keyword_instances(para, kws))

    def test_keyword_instances_param_and_trailing_period(self):
        self.assertEqual(ot.keyword_instances("ward {2}.", ["Ward"]),
                         [{"keyword": "ward", "param": "{2}"}])
        self.assertEqual(ot.keyword_instances("flying", ["Flying"]),
                         [{"keyword": "flying", "param": None}])

    def test_empty_keywords_and_empty_paragraph(self):
        self.assertEqual(ot.keyword_instances("flying", []), [])
        self.assertEqual(ot.keyword_instances("", ["Flying"]), [])
        self.assertFalse(ot.is_keyword_only("flying", []))
        self.assertFalse(ot.is_keyword_only("", ["Flying"]))

    def test_the_carried_forward_generic_keyword_limitation(self):
        """KNOWN LIMITATION, carried forward unchanged: a keyword whose name does
        not literally prefix its templated text is not recognised. Pinned so the
        limitation is visible rather than rediscovered."""
        para = "swampwalk"
        self.assertFalse(ot.is_keyword_only(para, ["Landwalk"]))
        self.assertEqual(ot.is_keyword_only(para, ["Landwalk"]),
                         self.te.is_keyword_only_paragraph(para, ["Landwalk"]))


class TestTheCaptainRatifiedN2Rule(unittest.TestCase):
    """N2, ratified 2026-08-30. Asserted DIRECTLY, not only differentially."""

    @classmethod
    def setUpClass(cls):
        cls.te = engine()

    def test_the_named_witness_regenerate_stays_literal(self):
        text = "Regenerate target creature."
        out = ot.normalize_self_references(text, {"Regenerate"}, ["Regenerate"])
        self.assertEqual(out, "Regenerate target creature.")
        self.assertNotIn(ot.SELF_TOKEN, out)
        self.assertEqual(out.lower(), "regenerate target creature.")

    def test_an_ORDINARY_self_name_occurrence_still_becomes_the_token(self):
        text = "Whenever Regenerate deals combat damage, draw a card."
        out = ot.normalize_self_references(text, {"Regenerate"}, ["Regenerate"])
        self.assertEqual(out, "Whenever ~ deals combat damage, draw a card.")

    def test_a_keyword_action_name_NOT_sentence_initial_follows_the_oracle(self):
        text = "You may regenerate. Regenerate target creature."
        candidates, kws = {"Regenerate"}, ["Regenerate"]
        self.assertEqual(ot.normalize_self_references(text, candidates, kws),
                         self.te.normalize_self_references(text, candidates, kws))

    def test_sentence_initial_but_NOT_followed_by_target_follows_the_oracle(self):
        text = "Regenerate deals 2 damage."
        candidates, kws = {"Regenerate"}, ["Regenerate"]
        out = ot.normalize_self_references(text, candidates, kws)
        self.assertEqual(out, self.te.normalize_self_references(text, candidates, kws))
        self.assertEqual(out, "~ deals 2 damage.")

    def test_the_carve_out_needs_the_name_to_BE_a_keyword(self):
        """A card merely named like a verb, with no such keyword, substitutes."""
        text = "Regenerate target creature."
        self.assertEqual(
            ot.normalize_self_references(text, {"Regenerate"}, []),
            "~ target creature.")

    def test_multi_face_printed_name_candidates(self):
        name = "Delver of Secrets // Insectile Aberration"
        got = ot.self_name_candidates(name)
        self.assertEqual(got, {name, "Delver of Secrets", "Insectile Aberration"})
        self.assertEqual(got, self.te.self_name_candidates(name))

    def test_candidates_are_applied_longest_first(self):
        name = "Delver of Secrets // Insectile Aberration"
        text = "Delver of Secrets // Insectile Aberration transforms."
        self.assertEqual(
            ot.normalize_self_references(text, ot.self_name_candidates(name), []),
            self.te.normalize_self_references(text, self.te.self_name_candidates(name), []))

    def test_this_is_NOT_the_CR205_noun_phrase_mechanism(self):
        """Explicitly guarded: the ratified scope boundary says the printed-name
        rule does not touch "this creature" / "this scheme"."""
        text = "This creature gets +1/+1."
        self.assertEqual(
            ot.normalize_self_references(text, {"Grizzly Bears"}, []), text)
        self.assertNotIn("this creature", ot.__doc__.split("law, not convenience")[0])


class TestFullCorpusDifferential(unittest.TestCase):
    """Every surface, every card, every face, every paragraph."""

    @classmethod
    def setUpClass(cls):
        if not CORPUS_FILE.exists():
            raise unittest.SkipTest(
                f"the local corpus {CORPUS_FILE} is absent; the fixtures above "
                "still run, and C8.5I's Worker result records the full-corpus "
                "outcome")
        from mtj_foundry import corpus
        cls.te = engine()
        cls.cards = corpus.load_cards(CORPUS_FILE)
        cls.card_faces = staticmethod(corpus.card_faces)

    def test_every_surface_is_VALUE_EXACT(self):
        te, bad = self.te, {}
        faces = paras = 0
        for card in self.cards.values():
            name = card.get("name") or ""
            kws = card.get("keywords") or []
            lc_, nc = te.self_name_candidates(name), ot.self_name_candidates(name)
            if lc_ != nc:
                bad["self_name_candidates"] = bad.get("self_name_candidates", 0) + 1
            for face in self.card_faces(card):
                faces += 1
                text = face["oracle_text"] or ""
                for key, a, b in (
                    ("normalize_self_references",
                     te.normalize_self_references(text, lc_, kws),
                     ot.normalize_self_references(text, nc, kws)),
                    ("paren_spans", te.find_paren_spans(text), ot.paren_spans(text)),
                    ("strip_reminders", te.strip_reminder(text), ot.strip_reminders(text)),
                    ("reminder_bodies", te.extract_reminder_spans(text),
                     ot.reminder_bodies(text)),
                    ("collapse_whitespace", te.WS_RE.sub(" ", text).strip(),
                     ot.collapse_whitespace(text)),
                ):
                    if a != b:
                        bad[key] = bad.get(key, 0) + 1
                for body in te.extract_reminder_spans(text):
                    if te.normalize_reminder_body(body) != ot.normalize_reminder(body):
                        bad["normalize_reminder"] = bad.get("normalize_reminder", 0) + 1
                for para in text.split("\n"):
                    if not para.strip():
                        continue
                    paras += 1
                    ln, nn = te.normalize_clause_text(para), ot.normalize_clause(para)
                    if ln != nn:
                        bad["normalize_clause"] = bad.get("normalize_clause", 0) + 1
                    if te.parse_keyword_instances(ln, kws) != ot.keyword_instances(nn, kws):
                        bad["keyword_instances"] = bad.get("keyword_instances", 0) + 1
                    if te.is_keyword_only_paragraph(ln, kws) != ot.is_keyword_only(nn, kws):
                        bad["is_keyword_only"] = bad.get("is_keyword_only", 0) + 1
        self.assertEqual(bad, {})
        self.assertGreater(faces, 40000, faces)
        self.assertGreater(paras, 60000, paras)


class TestThePermanentModuleIsALibrary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = MODULE.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_it_imports_only_the_standard_library(self):
        imported = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imported |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertTrue(imported <= set(sys.stdlib_module_names) | {"__future__"},
                        sorted(imported))

    def test_it_imports_no_legacy_module_and_not_even_the_corpus_capability(self):
        """Face splitting belongs to the corpus capability; this module must not
        reach for it, because a text normaliser that knows about faces has
        quietly absorbed a second capability."""
        imported = {a.name for n in ast.walk(self.tree) if isinstance(n, ast.Import)
                    for a in n.names}
        imported |= {n.module for n in ast.walk(self.tree)
                     if isinstance(n, ast.ImportFrom) and n.module}
        for forbidden in ("tier_engine", "foundry_common", "mtj_foundry.corpus",
                          "experiments"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, imported)

    def test_it_never_prints_exits_or_touches_the_path(self):
        calls = [ast.unparse(n.func) for n in ast.walk(self.tree) if isinstance(n, ast.Call)]
        for banned in ("print", "sys.exit", "exit", "open"):
            with self.subTest(banned=banned):
                self.assertNotIn(banned, calls)
        self.assertEqual([n for n in ast.walk(self.tree) if isinstance(n, ast.Attribute)
                          and n.attr == "path" and isinstance(n.value, ast.Name)
                          and n.value.id == "sys"], [])

    def test_it_states_no_repository_relative_layout_fact(self):
        literals = [n.value for n in ast.walk(self.tree)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str)
                    and len(n.value) < 200]
        for fragment in ("data/raw", "experiments", "/docs", "oracle-cards"):
            with self.subTest(fragment=fragment):
                self.assertEqual([x for x in literals if fragment in x], [])

    def test_the_module_level_names_are_the_declared_surface_only(self):
        assigned = [t.id for n in self.tree.body if isinstance(n, ast.Assign)
                    for t in n.targets if isinstance(t, ast.Name)]
        self.assertEqual(sorted(assigned),
                         ["SELF_TOKEN", "_CURLY_QUOTES", "_WHITESPACE", "__all__"])

    def test_the_public_surface_is_exactly_the_contracted_one(self):
        self.assertEqual(sorted(ot.__all__), [
            "SELF_TOKEN", "collapse_whitespace", "is_keyword_only",
            "keyword_instances", "normalize_clause", "normalize_reminder",
            "normalize_self_references", "paren_spans", "reminder_bodies",
            "self_name_candidates", "strip_reminders"])


class TestTheConsumerLeftTheEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.enrich = (EXPERIMENTS / "foundry_enrich.py").read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.enrich)

    def test_foundry_enrich_has_no_tier_engine_import_or_access(self):
        self.assertEqual([n for n in ast.walk(self.tree) if isinstance(n, ast.Import)
                          and any(a.name == "tier_engine" for a in n.names)], [])
        self.assertEqual([ast.unparse(n) for n in ast.walk(self.tree)
                          if isinstance(n, ast.Attribute)
                          and isinstance(n.value, ast.Name) and n.value.id == "te"], [])

    def test_it_reaches_the_package_only_after_foundry_common(self):
        """foundry_common is what establishes the C8.5A bootstrap; importing the
        package before it would need a bootstrap of this module's own."""
        common = self.enrich.index("import foundry_common as fc")
        package = self.enrich.index("from mtj_foundry import oracle_text as ot")
        self.assertLess(common, package)

    def test_it_added_no_bootstrap(self):
        inserts = [n for n in ast.walk(self.tree) if isinstance(n, ast.Call)
                   and isinstance(n.func, ast.Attribute)
                   and n.func.attr in ("insert", "append")
                   and isinstance(n.func.value, ast.Attribute)
                   and n.func.value.attr == "path"]
        self.assertEqual(len(inserts), 1, "the sys.path call count moved")

    def test_the_residual_corpus_access_goes_through_the_accepted_facade(self):
        self.assertIn("fc.raw_faces(card)", self.enrich)
        self.assertNotIn("get_raw_faces", self.enrich)

    def test_the_oracle_and_the_shipped_pipeline_are_byte_identical(self):
        import hashlib
        for path, expected in ((EXPERIMENTS / "tier_engine.py", TIER_ENGINE_SHA),
                               (REPO_ROOT / "pipeline" / "embed.py", PIPELINE_EMBED_SHA)):
            with self.subTest(path=path.name):
                self.assertEqual(
                    hashlib.sha256(path.read_bytes()).hexdigest(), expected)

    def test_the_pipeline_divergence_is_recorded_not_repaired(self):
        """Captain ruled the same N2 semantics govern pipeline/embed.py, and that
        repairing it is DEFERRED to a separate bounded task. This pins the
        divergence so it cannot be forgotten or silently 'fixed' here."""
        embed = (REPO_ROOT / "pipeline" / "embed.py").read_text(encoding="utf-8")
        self.assertIn("def normalize_self_references(", embed)
        self.assertNotIn("keywords", embed.split(
            "def normalize_self_references(")[1].split("\ndef ")[0])


if __name__ == "__main__":
    unittest.main()
