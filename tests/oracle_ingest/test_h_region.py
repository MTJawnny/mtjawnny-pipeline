"""C03 unit tests: H-REGION derivation, every applicable arm of the seven
interface/1 I3 kill tests, and --check-not-killed / --check-decided.

Inline SYNTHETIC clauses only -- generic templating, no card, no card name, no
oracle_id and no Oracle text. Nothing here reads the corpus.

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


def rig(text, **kw):
    return hk._rig(text, **kw)


def run(records, rules=None):
    return hk.evaluate(records, RULES if rules is None else rules, NAMES)


def outcome(record, k, rules=None):
    return run([record], rules)["clauses"][0]["tests"][k]["outcome"]


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
        for r, h in zip(c["regions"], c["heads_legacy"]):
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

    def test_ability_prefix_cost_governs_every_region(self):
        c = rig(COST, lo=5)
        cost = next(s for s in c["role_spans"] if s["role"] == "cost")
        self.assertEqual((cost["outcome"], cost["attached"], cost["rule"]),
                         ("multiple", [0, 1], "attach-ability-prefix"))

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
        cond = next(s for s in c["role_spans"] if s["role"] == "condition")
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


# --------------------------------------------------------------- the kill tests

class KillArms(unittest.TestCase):
    """KILL and UNRESOLVED for K1-K6, KILL for K7, plus the PASS arm."""

    def test_k1(self):
        self.assertEqual(outcome(rig(TWO, census=("exile", 0), population=True), "K1"), PASS)
        merged = rig(TWO, census=("exile", 0), population=True)
        merged["regions"] = [dict(merged["regions"][0], span=[0, len(TWO) - 1])]
        self.assertEqual(outcome(merged, "K1"), KILL)
        self.assertEqual(outcome(rig(TWO_HEADS, census=("destroy", 0), population=True),
                                 "K1"), UNRESOLVED)

    def test_k1_corrected_only_head_is_an_extraction_failure(self):
        c = rig(TWO, census=("exile", 0), population=True)
        ret = c["heads_legacy"].pop()
        c["heads_corrected"] = [h for h in c["heads_corrected"]]
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
        self.assertEqual(outcome(rig(same, census=("destroy", 0), population=True), "K2"),
                         UNRESOLVED)

    def test_k3(self):
        self.assertEqual(outcome(rig(TWO, census=("exile", 0), population=True), "K3"), PASS)
        two_objects = ("Exile target artifact and target enchantment, then return that "
                       "card to the battlefield.")
        self.assertEqual(outcome(rig(two_objects, census=("exile", 0), population=True),
                                 "K3"), KILL)
        self.assertEqual(outcome(rig("Return it to its owner's hand.", census=("bounce", 0),
                                     population=True), "K3"), UNRESOLVED)
        self.assertEqual(outcome(rig(NO_HEAD), "K3"), UNRESOLVED)

    def test_k3_a_pronoun_beside_a_participant_is_not_a_second_referent(self):
        text = ("Exile target artifact that has a counter on it, then return it to the "
                "battlefield.")
        self.assertEqual(outcome(rig(text, census=("exile", 0), population=True), "K3"),
                         UNRESOLVED)

    def test_k4(self):
        self.assertEqual(outcome(rig(TWO), "K4"), PASS)
        self.assertEqual(outcome(rig(COST, lo=5, census=("exile", 0), population=True),
                                 "K4"), KILL)
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
        self.assertEqual(outcome(rig(TWO, census=("exile", 0), population=True), "K6"), PASS)
        split = rig("Return target artifact to its owner's hand and target enchantment to "
                    "the battlefield.", census=("bounce", 0), roles=[hk.ROLE_SPLIT])
        self.assertEqual(outcome(split, "K6"), KILL)
        self.assertEqual(outcome(rig(NO_HEAD), "K6"), UNRESOLVED)

    def test_k6_does_not_fire_where_k1_to_k5_fire(self):
        row = run([rig(COST, lo=5, census=("exile", 0), population=True)])["clauses"][0]
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


class Relevance(unittest.TestCase):

    def row(self, record):
        return run([record])["clauses"][0]

    def test_questions(self):
        self.assertEqual(self.row(rig(TWO, census=("exile", 0), population=True))["questions"],
                         ["ATTACH-1", "C2", "ATTACH-3"])
        self.assertEqual(self.row(rig(TWO_HEADS, population=True))["questions"], [])

    def test_fixtures_are_always_relevant(self):
        t = self.row(rig(TWO_HEADS, roles=["rig-role"]))["tests"]
        self.assertTrue(all(t[k]["relevant"] for k in hk.CONDITIONS))

    def test_k7_is_relevant_everywhere(self):
        self.assertTrue(self.row(rig(TWO_HEADS, population=True))["tests"]["K7"]["relevant"])

    def test_k5_needs_an_overlap(self):
        self.assertFalse(self.row(rig(TWO, census=("exile", 0),
                                      population=True))["tests"]["K5"]["relevant"])


# -------------------------------------------------------- the result checks

class Checks(unittest.TestCase):

    def test_a_relevant_kill_fails_not_killed(self):
        rep = run([rig(COST, lo=5, census=("exile", 0), population=True)])
        self.assertIn(["K4", "rig:0:0:0"], hk.not_killed_failures(rep))
        self.assertEqual(rep["conditions"]["K4"]["result"], hk.RESULT_KILLED)

    def test_a_control_only_kill_passes_not_killed(self):
        rep = run([rig("Destroy target artifact.", census=("destroy", 0), population=True)])
        rep["negative_controls"] = run([rig(COST, lo=5, census=("exile", 0),
                                            population=True)])["conditions"]
        self.assertEqual(hk.not_killed_failures(rep), [])

    def test_a_kill_on_an_irrelevant_population_clause_passes(self):
        rep = run([rig(TWO_HEADS, population=True)])
        rep["clauses"][0]["tests"]["K1"]["outcome"] = KILL
        rep["conditions"] = hk.summarize(rep["clauses"])
        self.assertEqual(hk.not_killed_failures(rep), [])
        self.assertEqual(rep["conditions"]["K1"]["result"], hk.RESULT_NOT_KILLED)

    def test_attach3_only_clause_is_relevant_to_k4(self):
        rep = run([rig("{T}: Destroy target artifact, then proliferate.", lo=5,
                       population=True)])
        row = rep["clauses"][0]
        self.assertEqual(row["questions"], ["ATTACH-3"])
        self.assertTrue(row["tests"]["K4"]["relevant"])
        self.assertIn(["K4", "rig:0:0:0"], hk.not_killed_failures(rep))

    def test_decided(self):
        fixture = rig(NO_HEAD, roles=["rig-role"])
        self.assertIn("K1", hk.undecided(run([fixture])))
        both = run([fixture, rig(TWO, census=("exile", 0), population=True, ci=1)])
        self.assertNotIn("K1", hk.undecided(both))
        self.assertEqual(both["conditions"]["K1"]["pass_coverage"], "sufficient")

    def test_mixed(self):
        rep = run([rig(COST, lo=5, census=("exile", 0), population=True)])
        self.assertEqual(rep["conditions"]["K4"]["result"], hk.RESULT_KILLED)
        self.assertTrue(hk.not_killed_failures(rep))
        self.assertIn("K5", hk.undecided(rep))
        self.assertEqual(rep["conditions"]["K5"]["pass_coverage"], hk.COVERAGE_FLAG)
        self.assertEqual(rep["conditions"]["K5"]["result"], hk.RESULT_NOT_KILLED)

    def test_never_confirmed(self):
        rep = run([rig(TWO, census=("exile", 0), population=True)])
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
        killed = run([rig(COST, lo=5, census=("exile", 0), population=True)])
        clean = run([rig(TWO, census=("exile", 0), population=True)])
        clean["negative_controls"] = killed["conditions"]
        self.assertNotEqual(self.cli(killed, "--check-not-killed"), 0)
        self.assertEqual(self.cli(clean, "--check-not-killed"), 0)

    def test_cli_check_decided_exit_codes(self):
        fixture = rig(NO_HEAD, roles=["rig-role"])
        self.assertNotEqual(self.cli(run([fixture]), "--check-decided"), 0)
        rep = run([fixture, rig(TWO, census=("exile", 0), population=True, ci=1)])
        for k in hk.CONDITIONS:          # one relevant PASS for every condition
            if not rep["conditions"][k]["relevant"][PASS]["count"]:
                self.skipTest(f"{k} has no PASS in this rig")
        self.assertEqual(self.cli(rep, "--check-decided"), 0)

    def test_the_scripts_own_negative_controls_all_fire(self):
        self.assertEqual(len(hk.negative_controls(RULES)), 21)


if __name__ == "__main__":
    unittest.main()
