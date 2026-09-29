"""C03 unit tests: H-REGION derivation, every applicable arm of the seven
interface/2 I3 kill tests, every R1-R3 arm and non-arm named in interface/2
§I3a, and --check-not-killed / --check-decided.

Inline SYNTHETIC clauses only -- generic templating, no card, no card name, no
oracle_id and no Oracle text -- except `PromptingClauses`: the clauses that
prompted R1-R3, named ONLY by four-coordinate address and read from the pinned
corpus at run time. A missing or differing corpus is a loud failure there,
never a skip.

    python3 -m unittest discover -s tests/oracle_ingest -t .
"""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "oracle_ingest"))

import h_region as hr            # noqa: E402
import h_region_kill as hk       # noqa: E402

KILL, UNRESOLVED, PASS = hk.KILL, hk.UNRESOLVED, hk.PASS
RULES = list(hr.RULES)
NAMES = ["Synthetic Widget"]

TWO = "Exile target artifact you control, then return that card to the battlefield."
TWO_HEADS = "Destroy target artifact, then proliferate."
COST = "{T}: Exile target artifact, then return it to the battlefield."
NO_HEAD = "Put target artifact on top of its owner's library."
# A standalone `If ..., <operation>` with no trigger word: not an R1 shape, so
# its prefix span keeps the interface/1 multiple attachment (K4 KILL).
STANDALONE = ("If you control an enchantment, exile target artifact, then return it "
              "to the battlefield.")
PAYMENT = "Destroy target artifact if {G} was spent to cast this widget."
R3_TWO = ("Exile target artifact and target enchantment, then return them to the "
          "battlefield.")


def rig(text, **kw):
    return hk._rig(text, **kw)


def pop(text, stem="exile", **kw):
    return rig(text, census=(stem, 0), population=True, **kw)


def run(records, rules=None):
    return hk.evaluate(records, RULES if rules is None else rules, NAMES)


def outcome(record, k, rules=None):
    return run([record], rules)["clauses"][0]["tests"][k]["outcome"]


def k3_rels(record):
    return run([record])["clauses"][0]["tests"]["K3"]["relations"]


def r3_hits(record):
    return [x for x in k3_rels(record) if x.get("r3")]


def span_of(record, role):
    return next(s for s in record["role_spans"] if s["role"] == role)


def halts(fn):
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            fn()
    except SystemExit:
        return True
    return False


# ------------------------------------------------------------ region derivation

class RegionDerivation(unittest.TestCase):

    def test_one_region_per_head_cut_at_the_printed_connector(self):
        c = rig(TWO)
        self.assertEqual([r["head"] for r in c["regions"]], ["exile", "return"])
        r0, r1 = c["regions"]
        self.assertEqual(TWO[slice(*r0["span"])], "Exile target artifact you control")
        self.assertEqual(TWO[slice(*r1["span"])],
                         "return that card to the battlefield")
        self.assertEqual(r0["end_rule"], "region-end-next-connector")
        self.assertEqual(r1["end_rule"], "region-end-scope")
        self.assertEqual(r1["head_span"][0], TWO.index("return"))
        self.assertEqual({r["owner"] for r in c["regions"]}, {"rig:0:0:0"})

    def test_regions_are_offsets_into_the_clause_and_start_at_heads(self):
        c = rig(COST, lo=5)
        self.assertEqual(c["regions"][0]["span"][0], 5)
        for r, h in zip(c["regions"], c["heads_region"]):
            self.assertEqual(r["span"][0], h["start"])

    def test_no_legacy_head_means_no_region(self):
        c = rig(NO_HEAD)
        self.assertEqual(c["regions"], [])
        self.assertEqual([s["outcome"] for s in c["role_spans"]], ["no_region"])

    def test_head_positions_equal_the_frozen_detectors(self):
        self.assertEqual([h["head"] for h in hr.head_positions(TWO)],
                         hr.aq.effect_heads(TWO))
        bullet = "• Destroy target artifact."
        self.assertEqual([h["head"] for h in hr.head_positions(bullet, corrected=True)],
                         hr.aq.semantic_action_heads(bullet))

    def test_corrected_detector_reported_never_substituted(self):
        c = rig("• Destroy target artifact.")
        self.assertEqual(c["regions"], [])
        self.assertTrue(c["detector_diff"]["differs"])
        self.assertEqual(c["detector_diff"]["only_corrected"], [["destroy", 2]])

    def test_regions_never_overlap_or_nest(self):
        c = rig(TWO)
        self.assertEqual((c["overlaps"], c["nestings"]), ([], []))

    def test_repeated_heads_are_counted(self):
        c = rig("Destroy target artifact, then destroy target enchantment.")
        self.assertEqual(c["repeated_heads"], ["destroy"])


class RoleMarks(unittest.TestCase):

    def roles(self, text, **kw):
        return {(s["role"], s["outcome"]) for s in rig(text, **kw)["role_spans"]}

    def test_destination_inside_a_region_attaches_to_it(self):
        self.assertEqual(self.roles(TWO), {("destination", "attached")})

    def test_ability_prefix_cost_with_one_region_attaches(self):
        self.assertIn(("cost", "attached"), self.roles("{T}: Destroy target artifact.",
                                                       lo=5))

    def test_trigger_condition_is_a_condition_span(self):
        text = "When this widget enters, destroy target artifact."
        self.assertIn(("condition", "attached"), self.roles(text, lo=25))

    def test_duration_marker(self):
        self.assertIn(("duration", "attached"),
                      self.roles("Exile target artifact until end of turn."))

    def test_condition_crossing_a_region_boundary(self):
        text = "Destroy target artifact if it was spent to proliferate."
        c = rig(text)
        cond = span_of(c, "condition")
        self.assertEqual(cond["outcome"], "multiple")
        self.assertEqual(cond["rule"], "attach-contained")

    def test_marks_inside_a_quoted_created_ability_are_excluded(self):
        c = rig('Destroy target artifact. It gains "Until end of turn, draw."')
        self.assertEqual(c["role_marks_in_created_ability"], 1)


class Guards(unittest.TestCase):

    def test_a_text_across_two_chain_clauses_is_refused(self):
        para = "Exile target artifact! Return it to the battlefield."
        segs = [(0, 0, i, s) for i, s in enumerate(hr.fx.sentence_spans(para))]
        with self.assertRaises(hr.Refused):
            hr.locate(segs, "Exile target artifact! Return it to the battlefield")
        self.assertEqual(hr.locate(segs, "Return it")[0][2], 1)

    def test_a_text_in_several_chain_clauses_is_refused(self):
        segs = [(0, 0, 0, "Draw a card."), (0, 1, 0, "Draw a card.")]
        with self.assertRaises(hr.Refused):
            hr.locate(segs, "Draw a card")

    def test_a_region_leaving_its_clause_is_refused(self):
        with self.assertRaises(hr.Refused):
            hr.check_bounds({"ordinal": 0, "span": [0, 9]}, 8)

    def test_the_rule_table_is_not_card_keyed(self):
        self.assertEqual(hr.assert_not_card_keyed(RULES, NAMES), [r["id"] for r in RULES])

    def test_card_keyed_rules_halt(self):
        base = {"id": "rig", "kind": "region", "cr": "CR 608.2c", "pattern": "x"}
        for bad in (dict(base, oracle_id="rig"),
                    dict(base, pattern="00000000-0000-0000-0000-000000000000"),
                    dict(base, pattern=r"\bSynthetic Widget\b"),
                    dict(base, cr="")):
            self.assertTrue(halts(lambda: hr.assert_not_card_keyed(RULES + [bad], NAMES)),
                            bad)

    def test_portability(self):
        self.assertTrue(hr.portability_violations(str(hr.ROOT).encode()))
        self.assertTrue(hr.portability_violations(str(Path.home()).encode()))
        self.assertFalse(hr.portability_violations(b"experiments/out/oracle_ingest"))

    def test_the_interface_pin_is_interface_2(self):
        self.assertEqual(hr.INTERFACE_VERSION, "oracle-compiler-interface/2")
        self.assertEqual(hr.INTERFACES_BLOB, "4ac4d856b651edde05b15c7065aa593f59561dcf")
        self.assertEqual(hr.verify_interface(), hr.INTERFACES_BLOB)


# ------------------------------------------------ interface/2 §I3a: the table

class RuleTable(unittest.TestCase):
    I3A = ("attach-ability-prefix", "head-not-payment-cast", "group-back-reference")

    def test_every_i3a_rule_is_in_the_table_with_exactly_four_keys(self):
        by_id = {r["id"]: r for r in RULES}
        for rid in self.I3A:
            self.assertIn(rid, by_id)
            self.assertEqual(set(by_id[rid]), {"id", "kind", "cr", "pattern"})
            self.assertTrue(by_id[rid]["cr"].startswith("CR "))

    def test_a_card_keyed_variant_of_each_i3a_rule_halts(self):
        for r in RULES:
            if r["id"] not in self.I3A:
                continue
            for k in ("id", "kind", "cr", "pattern"):
                for key in (NAMES[0], "00000000-0000-0000-0000-000000000000"):
                    bad = dict(r, **{k: f"{r[k]} {key}"})
                    self.assertTrue(halts(lambda: hr.assert_not_card_keyed(
                        RULES + [bad], NAMES)), (r["id"], k, key))

    def test_a_card_keyed_r3_entry_makes_k7_kill(self):
        keyed = [dict(r, pattern=f"{r['pattern']} {NAMES[0]}")
                 if r["id"] == "group-back-reference" else r for r in RULES]
        self.assertEqual(outcome(rig(TWO_HEADS), "K7", keyed), KILL)
        self.assertEqual(outcome(rig(TWO_HEADS), "K7"), PASS)

    def test_r3_plural_markers_are_the_frozen_non_possessive_plurals(self):
        self.assertEqual(set(hr.R3_PLURAL_MARKERS),
                         {"they", "them", "those cards", "those creatures",
                          "those permanents", "those tokens"})
        self.assertTrue(set(hr.R3_PLURAL_MARKERS) <= hr.aq._PRONOUN_MARKERS)
        self.assertNotIn("their", hr.R3_PLURAL_MARKERS)


# ------------------------------------------------- interface/2 §I3a R1 arms

class R1AttachAbilityPrefix(unittest.TestCase):

    def assert_ability(self, text, shape, lo=0):
        c = pop(text, lo=lo)
        hit = [s for s in c["role_spans"] if s.get("r1_shape") == shape]
        self.assertEqual(len(hit), 1, (text, c["role_spans"]))
        s = hit[0]
        self.assertEqual((s["outcome"], s["attached_to"], s["rule"]),
                         ("attached", "ability", "attach-ability-prefix"))
        self.assertEqual(s["attached"], [r["ordinal"] for r in c["regions"]])
        self.assertEqual(s["interface1"]["outcome"], "multiple")
        self.assertEqual(s["interface1"]["changed_by"], ["R1"])
        self.assertEqual(outcome(c, "K4"), PASS)
        return c

    def test_cost_colon(self):
        self.assert_ability(COST, "cost-colon", lo=5)

    def test_loyalty_cost_colon(self):
        self.assert_ability("−2: Exile target artifact, then return it to the "
                            "battlefield.", "cost-colon", lo=4)

    def test_condition_trigger_when_whenever_at(self):
        for word in ("When", "Whenever", "At"):
            lead = {"When": "When this widget enters",
                    "Whenever": "Whenever this widget attacks",
                    "At": "At the beginning of your end step"}[word]
            self.assert_ability(f"{lead}, exile target artifact, then return it to "
                                f"the battlefield.", "condition-trigger")

    def test_intervening_if_after_the_trigger_comma(self):
        c = self.assert_ability("At the beginning of your end step, if you control an "
                                "enchantment, exile target artifact, then return it to "
                                "the battlefield.", "condition-marker")
        self.assertEqual(sorted(s.get("r1_shape") or "" for s in c["role_spans"]
                                if s["role"] == "condition"),
                         ["condition-marker", "condition-trigger"])

    def test_single_region_attachment_is_unchanged(self):
        c = pop("When this widget enters, destroy target artifact.", stem="destroy")
        s = span_of(c, "condition")
        self.assertEqual((s["outcome"], s["r1_shape"]), ("attached", "condition-trigger"))
        self.assertNotIn("interface1", s)


class R1NonArms(unittest.TestCase):
    """Prefix position alone never qualifies; each keeps interface/1."""

    def assert_interface1(self, text, role):
        c = pop(text)
        s = span_of(c, role)
        self.assertIsNone(s.get("r1_shape"))
        self.assertEqual((s["outcome"], s["rule"]), ("multiple", "attach-ability-prefix"))
        self.assertNotIn("interface1", s)
        self.assertEqual(outcome(c, "K4"), KILL)

    def test_standalone_if_with_no_trigger_word(self):
        self.assert_interface1(STANDALONE, "condition")

    def test_duration_prefix(self):
        self.assert_interface1("Until end of turn, exile target artifact, then return "
                               "it to the battlefield.", "duration")

    def test_destination_prefix(self):
        self.assert_interface1("To the battlefield, exile target artifact, then return "
                               "it.", "destination")

    def test_condition_marker_not_right_after_a_trigger_comma(self):
        # A trigger word that does not open the clause scope is no trigger span,
        # so the following `if` is a condition-marker by itself.
        c = pop("Then, if you control an enchantment, exile target artifact, then "
                "return it to the battlefield.")
        s = span_of(c, "condition")
        self.assertIsNone(s.get("r1_shape"))
        self.assertEqual(outcome(c, "K4"), KILL)

    def test_a_condition_inside_the_effect_crossing_regions(self):
        c = pop("Exile target artifact if you control an enchantment, then return it "
                "to the battlefield.")
        s = span_of(c, "condition")
        self.assertIsNone(s.get("r1_shape"))
        self.assertNotEqual(s["rule"], "attach-ability-prefix")


# ------------------------------------------------- interface/2 §I3a R2 arms

class R2HeadNotPaymentCast(unittest.TestCase):

    def test_spent_to_cast_starts_no_region(self):
        c = pop(PAYMENT, stem="destroy")
        self.assertIn("cast", hr.aq.effect_heads(PAYMENT))        # frozen, unedited
        self.assertEqual([h["head"] for h in c["heads_legacy"]], ["destroy", "cast"])
        self.assertEqual([h["head"] for h in c["r2_dropped_heads"]], ["cast"])
        self.assertEqual([r["head"] for r in c["regions"]], ["destroy"])
        self.assertEqual([h["head"] for h in c["heads_region"]], ["destroy"])
        self.assertEqual(c["regions"][0]["end_rule"], "region-end-scope")

    def test_its_condition_span_then_attaches_under_the_ordinary_rules(self):
        c = pop(PAYMENT, stem="destroy")
        s = span_of(c, "condition")
        self.assertEqual((s["outcome"], s["rule"]), ("attached", "attach-contained"))
        self.assertEqual(s["interface1"],
                         {"attached": [0, 1], "outcome": "multiple",
                          "rule": "attach-contained", "changed_by": ["R2"]})
        row = run([c])["clauses"][0]["tests"]
        self.assertEqual((row["K4"]["outcome"], row["K7"]["outcome"]), (PASS, PASS))

    def test_cast_as_an_instruction_or_permission_is_unaffected(self):
        for text in ("Exile target card, then you may cast that card.",
                     "Exile target card, then cast it.",
                     "Exile target card, then cast that card."):
            c = rig(text)
            self.assertEqual(c["r2_dropped_heads"], [], text)
            self.assertIn("cast", [r["head"] for r in c["regions"]], text)

    def test_no_other_head_is_discounted(self):
        c = rig("Destroy target artifact if mana was spent to return it.")
        self.assertEqual(c["r2_dropped_heads"], [])
        self.assertEqual([r["head"] for r in c["regions"]], ["destroy", "return"])

    def test_r2_is_reported_per_clause(self):
        m = hr.measure([pop(PAYMENT, stem="destroy"), rig(TWO)])
        r2 = m["interface2_rules"]["R2_head_not_payment_cast"]
        self.assertEqual(r2["dropped_heads"], [["rig:0:0:0", "cast", PAYMENT.index("cast")]])


# ------------------------------------------------- interface/2 §I3a R3 arms

class R3GroupBackReference(unittest.TestCase):

    def assert_r3(self, text):
        c = pop(text)
        hits = r3_hits(c)
        self.assertEqual(len(hits), 1, k3_rels(c))
        self.assertEqual(hits[0]["outcome"], UNRESOLVED)
        self.assertEqual(outcome(c, "K3"), UNRESOLVED)
        return hits[0]

    def test_a_plural_reference_to_one_target_list_is_named_and_unresolved(self):
        h = self.assert_r3(R3_TWO)
        self.assertEqual([k for _, _, k in h["list_marks"]], ["target", "target"])

    def test_a_second_object_conjunct_is_a_list_member(self):
        h = self.assert_r3("Exile target artifact you control and the top card of your "
                           "library, then return those cards to the battlefield.")
        self.assertEqual([k for _, _, k in h["list_marks"]], ["target", "second-object"])

    def test_comma_and_is_counted_once(self):
        h = self.assert_r3("Exile target artifact, target enchantment, and target widget, "
                           "then return them to the battlefield.")
        self.assertEqual(len(h["list_marks"]), 3)

    def test_every_plural_marker(self):
        for m in hr.R3_PLURAL_MARKERS:
            self.assert_r3(f"Exile target artifact and target enchantment, then return "
                           f"{m} to the battlefield.")

    def test_r3_never_yields_pass(self):
        for x in k3_rels(pop(R3_TWO)):
            if x["kind"] == "back-reference":
                self.assertNotEqual(x["outcome"], PASS)

    def test_r3_is_reported_as_changing_an_interface1_kill(self):
        c = pop(R3_TWO)
        rep = run([c])
        rows = hk.interface1_changes([c], RULES, NAMES, rep)
        self.assertIn(["rig:0:0:0", ["exile", 0], "K3", KILL, UNRESOLVED, ["R3"]], rows)


class R3NonArms(unittest.TestCase):
    """Fail closed: the interface/1 KILL stands."""

    def assert_kill(self, text):
        c = pop(text)
        self.assertEqual(r3_hits(c), [], k3_rels(c))
        self.assertEqual(outcome(c, "K3"), KILL)

    def test_a_singular_reference_to_coordinated_candidates(self):
        self.assert_kill("Exile target artifact and target enchantment, then return it "
                         "to the battlefield.")
        self.assert_kill("Exile target artifact and target enchantment, then return that "
                         "card to the battlefield.")

    def test_a_possessive_plural(self):
        self.assert_kill("Exile target artifact and target enchantment, then return "
                         "their counters to the battlefield.")

    def test_a_gap_without_a_coordinator(self):
        self.assert_kill("Exile target artifact or target enchantment, then return them "
                         "to the battlefield.")

    def test_a_gap_with_two_coordinators(self):
        self.assert_kill("Exile target artifact, and, target enchantment, then return "
                         "them to the battlefield.")

    def test_a_gap_with_a_boundary_word(self):
        self.assert_kill("Exile target artifact attached to a widget and target "
                         "enchantment, then return them to the battlefield.")

    def test_candidates_in_two_earlier_regions(self):
        self.assert_kill("Exile target artifact, then exile target enchantment, then "
                         "return them to the battlefield.")

    def test_the_gap_test_directly(self):
        self.assertIsNotNone(hk.r3_list("Exile target artifact and target enchantment", 2))
        self.assertIsNone(hk.r3_list("Exile target artifact and target enchantment", 3))
        self.assertIsNone(hk.r3_list("Exile target artifact; target enchantment", 2))
        self.assertIsNone(hk.r3_list("Exile target artifact and destroy target "
                                     "enchantment", 2))
        self.assertIsNone(hk.r3_list("Exile target artifact", 1))


# --------------------------------------------------------------- the kill tests

class KillArms(unittest.TestCase):
    """KILL and UNRESOLVED for K1-K6, KILL for K7, plus the PASS arm."""

    def test_k1(self):
        self.assertEqual(outcome(pop(TWO), "K1"), PASS)
        merged = pop(TWO)
        merged["regions"] = [dict(merged["regions"][0], span=[0, len(TWO) - 1])]
        self.assertEqual(outcome(merged, "K1"), KILL)
        self.assertEqual(outcome(pop(TWO_HEADS, stem="destroy"), "K1"), UNRESOLVED)

    def test_k1_corrected_only_head_is_an_extraction_failure(self):
        c = pop(TWO)
        ret = c["heads_legacy"].pop()
        c["regions"] = c["regions"][:1]
        self.assertIn(ret["head"], [h["head"] for h in c["heads_corrected"]])
        self.assertEqual(outcome(c, "K1"), UNRESOLVED)

    def test_k1_fixture_role_is_independent_evidence(self):
        c = rig(TWO_HEADS, census=("destroy", 0), roles=[hk.ROLE_TWO_OPS])
        row = run([c])["clauses"][0]
        self.assertEqual(len(row["distinct_required_operations"]), 2)
        self.assertEqual(row["tests"]["K1"]["outcome"], PASS)

    def test_k2(self):
        same = "Destroy target artifact, then destroy target enchantment."
        ok = rig(same, census=("destroy", 0), roles=[hk.ROLE_TWO_OPS])
        self.assertEqual(outcome(ok, "K2"), PASS)
        bad = rig(same, census=("destroy", 0), roles=[hk.ROLE_TWO_OPS])
        bad["regions"][1]["span"] = list(bad["regions"][0]["span"])
        self.assertEqual(outcome(bad, "K2"), KILL)
        self.assertEqual(outcome(pop(same, stem="destroy"), "K2"), UNRESOLVED)

    def test_k3(self):
        self.assertEqual(outcome(pop(TWO), "K3"), PASS)
        two_objects = ("Exile target artifact and target enchantment, then return that "
                       "card to the battlefield.")
        self.assertEqual(outcome(pop(two_objects), "K3"), KILL)
        self.assertEqual(outcome(pop("Return it to its owner's hand.", stem="bounce"),
                                 "K3"), UNRESOLVED)
        self.assertEqual(outcome(rig(NO_HEAD), "K3"), UNRESOLVED)

    def test_k3_a_pronoun_beside_a_participant_is_not_a_second_referent(self):
        text = ("Exile target artifact that has a counter on it, then return it to the "
                "battlefield.")
        self.assertEqual(outcome(pop(text), "K3"), UNRESOLVED)

    def test_k4(self):
        self.assertEqual(outcome(rig(TWO), "K4"), PASS)
        self.assertEqual(outcome(pop(COST, lo=5), "K4"), PASS)            # R1
        self.assertEqual(outcome(pop(STANDALONE), "K4"), KILL)
        self.assertEqual(outcome(rig(NO_HEAD), "K4"), UNRESOLVED)

    def test_k5(self):
        self.assertEqual(outcome(rig(TWO_HEADS), "K5"), PASS)
        dup = rig("Destroy target artifact, then destroy target enchantment.")
        dup["regions"][1] = dict(dup["regions"][0], ordinal=1)
        dup["overlaps"] = [[0, 1]]
        self.assertEqual(outcome(dup, "K5"), KILL)
        miss = rig(TWO_HEADS)
        miss["detector_diff"]["only_corrected"] = [["counter", 3]]
        self.assertEqual(outcome(miss, "K5"), UNRESOLVED)

    def test_k6(self):
        self.assertEqual(outcome(pop(TWO), "K6"), PASS)
        split = rig("Return target artifact to its owner's hand and target enchantment to "
                    "the battlefield.", census=("bounce", 0), roles=[hk.ROLE_SPLIT])
        self.assertEqual(outcome(split, "K6"), KILL)
        self.assertEqual(outcome(rig(NO_HEAD), "K6"), UNRESOLVED)

    def test_k6_does_not_fire_where_k1_to_k5_fire(self):
        row = run([pop(STANDALONE)])["clauses"][0]
        self.assertEqual(row["tests"]["K4"]["outcome"], KILL)
        self.assertEqual(row["tests"]["K6"]["outcome"], PASS)

    def test_k7(self):
        self.assertEqual(outcome(rig(TWO_HEADS), "K7"), PASS)
        moved = rig(TWO_HEADS)
        moved["regions"][0]["span"][1] -= 3
        self.assertEqual(outcome(moved, "K7"), KILL)
        keyed = RULES + [{"id": "rig", "kind": "region", "cr": "CR 608.2c",
                          "pattern": "x", "oracle_id": "rig"}]
        self.assertEqual(outcome(rig(TWO_HEADS), "K7", keyed), KILL)
        self.assertNotIn(UNRESOLVED, {outcome(rig(NO_HEAD), "K7"),
                                      outcome(moved, "K7")})

    def test_k7_reads_the_heads_that_start_regions(self):
        self.assertEqual(outcome(pop(PAYMENT, stem="destroy"), "K7"), PASS)


class InterfaceOneBeside(unittest.TestCase):

    def test_r1_change_is_recorded_beside_its_interface1_outcome(self):
        c = pop(COST, lo=5)
        rep = run([c])
        rows = hk.interface1_changes([c], RULES, NAMES, rep)
        self.assertIn(["rig:0:0:0", ["exile", 0], "K4", KILL, PASS, ["R1"]], rows)
        ch = rep["clauses"][0]["interface1_changes"]["K4"]
        self.assertEqual((ch["interface1"], ch["interface2"], ch["changed_by"]),
                         (KILL, PASS, ["R1"]))

    def test_r2_change_is_recorded(self):
        c = pop(PAYMENT, stem="destroy")
        rows = hk.interface1_changes([c], RULES, NAMES, run([c]))
        self.assertIn(["rig:0:0:0", ["destroy", 0], "K4", KILL, PASS, ["R2"]], rows)

    def test_no_rule_no_change(self):
        c = pop(STANDALONE)
        self.assertEqual(hk.interface1_changes([c], RULES, NAMES, run([c])), [])

    def test_rule_reach(self):
        recs = [pop(COST, lo=5), pop(PAYMENT, stem="destroy", ci=1), pop(R3_TWO, ci=2)]
        reach = hk.rule_reach(recs, run(recs)["clauses"])
        self.assertEqual({k: v["population"]["clauses"] for k, v in reach.items()},
                         {"R1 attach-ability-prefix": ["rig:0:0:0"],
                          "R2 head-not-payment-cast": ["rig:0:0:1"],
                          "R3 group-back-reference": ["rig:0:0:2"]})


class Relevance(unittest.TestCase):

    def row(self, record):
        return run([record])["clauses"][0]

    def test_questions(self):
        self.assertEqual(self.row(pop(TWO))["questions"], ["ATTACH-1", "C2", "ATTACH-3"])
        self.assertEqual(self.row(rig(TWO_HEADS, population=True))["questions"], [])

    def test_fixtures_are_always_relevant(self):
        t = self.row(rig(TWO_HEADS, roles=["rig-role"]))["tests"]
        self.assertTrue(all(t[k]["relevant"] for k in hk.CONDITIONS))

    def test_k7_is_relevant_everywhere(self):
        self.assertTrue(self.row(rig(TWO_HEADS, population=True))["tests"]["K7"]["relevant"])

    def test_k5_needs_an_overlap(self):
        self.assertFalse(self.row(pop(TWO))["tests"]["K5"]["relevant"])


# -------------------------------------------------------- the result checks

class Checks(unittest.TestCase):

    def test_a_relevant_kill_fails_not_killed(self):
        rep = run([pop(STANDALONE)])
        self.assertIn(["K4", "rig:0:0:0"], hk.not_killed_failures(rep))
        self.assertEqual(rep["conditions"]["K4"]["result"], hk.RESULT_KILLED)

    def test_a_control_only_kill_passes_not_killed(self):
        rep = run([pop("Destroy target artifact.", stem="destroy")])
        rep["negative_controls"] = run([pop(STANDALONE)])["conditions"]
        self.assertEqual(hk.not_killed_failures(rep), [])

    def test_a_kill_on_an_irrelevant_population_clause_passes(self):
        rep = run([rig(TWO_HEADS, population=True)])
        rep["clauses"][0]["tests"]["K1"]["outcome"] = KILL
        rep["conditions"] = hk.summarize(rep["clauses"])
        self.assertEqual(hk.not_killed_failures(rep), [])
        self.assertEqual(rep["conditions"]["K1"]["result"], hk.RESULT_NOT_KILLED)

    def test_attach3_only_clause_is_relevant_to_k4(self):
        rep = run([rig("If you control an enchantment, destroy target artifact, then "
                       "proliferate.", population=True)])
        row = rep["clauses"][0]
        self.assertEqual(row["questions"], ["ATTACH-3"])
        self.assertTrue(row["tests"]["K4"]["relevant"])
        self.assertIn(["K4", "rig:0:0:0"], hk.not_killed_failures(rep))

    def test_decided(self):
        fixture = rig(NO_HEAD, roles=["rig-role"])
        self.assertIn("K1", hk.undecided(run([fixture])))
        both = run([fixture, pop(TWO, ci=1)])
        self.assertNotIn("K1", hk.undecided(both))
        self.assertEqual(both["conditions"]["K1"]["pass_coverage"], "sufficient")

    def test_mixed(self):
        rep = run([pop(STANDALONE)])
        self.assertEqual(rep["conditions"]["K4"]["result"], hk.RESULT_KILLED)
        self.assertTrue(hk.not_killed_failures(rep))
        self.assertIn("K5", hk.undecided(rep))
        self.assertEqual(rep["conditions"]["K5"]["pass_coverage"], hk.COVERAGE_FLAG)
        self.assertEqual(rep["conditions"]["K5"]["result"], hk.RESULT_NOT_KILLED)

    def test_never_confirmed(self):
        rep = run([pop(TWO)])
        self.assertTrue(all(d["result"] in (hk.RESULT_KILLED, hk.RESULT_NOT_KILLED)
                            for d in rep["conditions"].values()))
        self.assertNotIn("confirmed", json.dumps(rep["conditions"]))

    def cli(self, rep, flag):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "kill.json"
            path.write_text(json.dumps(rep), encoding="utf-8")
            with mock.patch.object(hk, "OUT", path), \
                    contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                return hk.main([flag])

    def test_cli_check_not_killed_exit_codes(self):
        killed = run([pop(STANDALONE)])
        clean = run([pop(TWO)])
        clean["negative_controls"] = killed["conditions"]
        self.assertNotEqual(self.cli(killed, "--check-not-killed"), 0)
        self.assertEqual(self.cli(clean, "--check-not-killed"), 0)

    def test_cli_check_decided_exit_codes(self):
        fixture = rig(NO_HEAD, roles=["rig-role"])
        self.assertNotEqual(self.cli(run([fixture]), "--check-decided"), 0)
        rep = run([fixture, pop(TWO, ci=1)])
        for k in hk.CONDITIONS:          # one relevant PASS for every condition
            if not rep["conditions"][k]["relevant"][PASS]["count"]:
                self.skipTest(f"{k} has no PASS in this rig")
        self.assertEqual(self.cli(rep, "--check-decided"), 0)

    def test_the_scripts_own_negative_controls_all_fire(self):
        self.assertEqual(len(hk.negative_controls(RULES)), 26)


# ---------------------------------------------- the clauses that prompted R1-R3

CORPUS_REL = "data/raw/oracle-cards.jsonl.gz"

# Four-coordinate address (oracle_id, face, paragraph, clause) and census key
# only -- the text is read from the pinned corpus at run time.
R1_CASES = {
    ("169705c3-32c1-4628-b108-c37ca5f27e24", 0, 0, 0, "exile"): ["cost-colon"],
    ("1ca97394-4e8c-4698-bea1-554f9b10927b", 0, 1, 0, "exile"): ["cost-colon"],
    ("4b072fbb-5e61-4009-bcb1-d493eb4a1be4", 0, 1, 1, "exile"): ["condition-trigger"],
    ("14b839ef-80b1-4e7d-b2fd-38e973899cde", 0, 1, 0, "destroy"): ["condition-trigger"],
    ("c4d2fdf9-637d-4e97-ae33-45f2d27bf8cd", 0, 2, 0, "exile"):
        ["condition-marker", "condition-trigger"],
}
R2_CASES = (("16da72a3-d980-4dd8-99f2-8191cce00978", 0, 0, 0, "destroy"),
            ("2cb98ca9-d7bb-416b-a17e-ee5f8e4d78f2", 0, 0, 0, "exile"))
R3_CASES = (("bac0fcee-9c1a-46b7-86c8-ffbfcc1e96de", 0, 0, 0, "exile"),)


class PromptingClauses(unittest.TestCase):
    """Regression cases, never keys: each must keep its interface/2 outcome."""

    @classmethod
    def setUpClass(cls):
        path = hr.ROOT / CORPUS_REL
        if not path.exists():
            raise AssertionError(f"the pinned corpus {CORPUS_REL} is missing: the "
                                 f"R1-R3 regression cases cannot run (a loud failure, "
                                 f"never a skip)")
        if halts(lambda: hr.verify_identities({CORPUS_REL: hr.I1[CORPUS_REL]})):
            raise AssertionError(f"the corpus at {CORPUS_REL} is not the pinned I1 "
                                 f"identity {hr.I1[CORPUS_REL]}")
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            cls.cards, _, _ = hr.fc.load_corpus_gated()
            cls.rows = hr.fqc.population(cls.cards)

    def record(self, oid, fi, pi, ci, stem):
        row = next((r for r in self.rows if (r["oracle_id"], r["stem"], r["occurrence"])
                    == (oid, stem, 0)), None)
        self.assertIsNotNone(row, f"no census row ({oid}, {stem}, 0)")
        got = hr.resolve_census(self.cards[oid], row["clause"])
        self.assertEqual(got[:3], (fi, pi, ci), "the address moved")
        _, _, _, text, off = got
        c = hr.clause_record(oid, fi, pi, ci, text, off, off + len(row["clause"]),
                             "census-clause")
        c.update(census_key=[stem, 0], population=True, fixture_roles=[])
        return c

    def test_r1_prompting_clauses(self):
        for key, shapes in R1_CASES.items():
            c = self.record(*key)
            got = sorted(s["r1_shape"] for s in c["role_spans"] if s.get("r1_shape"))
            self.assertEqual(got, shapes, key)
            self.assertGreater(len(c["regions"]), 1, key)
            self.assertEqual(outcome(c, "K4"), PASS, key)

    def test_r2_prompting_clauses(self):
        for key in R2_CASES:
            c = self.record(*key)
            self.assertEqual([h["head"] for h in c["r2_dropped_heads"]], ["cast"], key)
            self.assertEqual(len(c["regions"]), 1, key)
            t = run([c])["clauses"][0]["tests"]
            self.assertEqual(t["K4"]["outcome"], PASS, key)
            self.assertNotEqual(t["K3"]["outcome"], KILL, key)
            self.assertEqual(t["K7"]["outcome"], PASS, key)

    def test_r3_prompting_clause(self):
        for key in R3_CASES:
            c = self.record(*key)
            hits = r3_hits(c)
            self.assertEqual(len(hits), 1, key)
            self.assertEqual(hits[0]["outcome"], UNRESOLVED, key)
            self.assertEqual([k for _, _, k in hits[0]["list_marks"]],
                             ["target", "second-object"], key)
            self.assertEqual(outcome(c, "K3"), UNRESOLVED, key)


if __name__ == "__main__":
    unittest.main()
