"""S11 — the codebook-facing semantic kernel: owners, laws, conservation, layering.

WHAT S11 MOVED, AND WHERE
-------------------------
* DET record roles (`is_prefilter_pattern`, `is_lattice_pattern`, `pattern_slug`)
  and the enters-tapped quote base          -> `mtj_foundry.codebook_det_patterns`
* pattern -> ACTIVE-axis resolution         -> `mtj_foundry.codebook_det_resolution`
* lattice identity / instantiation / floor  -> `mtj_foundry.codebook_lattice`
* codebook / CR coverage                    -> `mtj_foundry.codebook_coverage`
* codebook-facing locality binding          -> `mtj_foundry.codebook_locality`
* pure DET application (A8)                 -> `mtj_foundry.codebook_det_apply`
* membership spec ops, conservation, Gate#0 -> `mtj_foundry.codebook_membership`
* slug grammar validator + vocabularies     -> `mtj_foundry.codebook_slug`

The model (`mtj_foundry.codebook`) and store (`mtj_foundry.codebook_store`) were
already permanent and correct; S11 reuses them unchanged. Every legacy shell kept
its I/O, prints, CLI, backups, writes and `STOP — …` boundary.

WHAT IS PROVED HERE
-------------------
1. The owners' semantics, including every refusal the kernel must keep refusing.
2. `pattern_role` has ONE definition across tracked Python, and a duplicate --
   a second `def`, a non-delegating facade, or a new inline copy -- is caught.
3. The S7 late-binding law through S11 consumers: a provider replaced at run
   time reaches the S11 consumer at call time; a CAPTURED provider does not, and
   the check detects that.
4. Layering: the kernel imports no `experiments`, no AQ4, no operator shell, no
   file I/O; `mtg/**` imports no codebook module; the package import graph is
   acyclic -- each guard negative-controlled.
5. Membership conservation over the SELECTED codebook, as a fingerprint (not a
   count), pinned from the accepted base's LEGACY callables; ×2 determinism.
"""

from __future__ import annotations

import ast
import copy
import hashlib
import io
import json
import subprocess
import sys
import contextlib
import unittest
from pathlib import Path
from types import SimpleNamespace

from tests.refoundation.helpers import REPO_ROOT, SRC
from tests.refoundation import s11_conservation as cons

from mtj_foundry import (codebook, codebook_coverage, codebook_det_apply,
                         codebook_det_patterns, codebook_det_resolution,
                         codebook_lattice, codebook_locality,
                         codebook_membership, codebook_slug, corpus)
from mtj_foundry.mtg import text_match
from mtj_foundry.mtg.shapes import locality as s7_locality
from mtj_foundry.mtg.shapes import target_classes
from mtj_foundry.paths import ProjectPaths

EXPERIMENTS = REPO_ROOT / "experiments"
PKG = SRC / "mtj_foundry"
S11_MODULES = {
    "codebook_det_patterns": set(),
    "codebook_det_resolution": {"mtj_foundry.codebook_det_patterns"},
    "codebook_lattice": {"mtj_foundry.codebook_det_patterns",
                         "mtj_foundry.mtg.shapes.target_classes"},
    "codebook_coverage": set(),
    "codebook_locality": {"mtj_foundry.mtg.shapes.locality"},
    "codebook_det_apply": {"mtj_foundry.codebook", "mtj_foundry.codebook_lattice",
                           "mtj_foundry.mtg.text_match"},
    "codebook_membership": set(),
    "codebook_slug": set(),
}
STDLIB_OK = {"__future__", "copy", "re", "typing"}


def _ensure_experiments_on_path() -> None:
    if str(EXPERIMENTS) not in sys.path:
        sys.path.insert(0, str(EXPERIMENTS))


def _halted(fn, *args, **kwargs):
    err = io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
        try:
            fn(*args, **kwargs)
        except SystemExit as exc:
            return exc.code, err.getvalue()
    return None, err.getvalue()


def _imports(tree: ast.AST) -> set:
    """Every imported module name, module-level AND function-local."""
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            out.add(mod)
            if mod == "mtj_foundry" or mod.startswith("mtj_foundry."):
                out |= {f"{mod}.{a.name}" for a in node.names}
    return out


# ===========================================================================
# 1. owner semantics
# ===========================================================================

class TestDetPatternRoles(unittest.TestCase):

    def test_roles_and_slug(self):
        p = codebook_det_patterns
        self.assertTrue(p.is_prefilter_pattern({"slug": "rule:energy-x pre-filter (spends {E})"}))
        self.assertFalse(p.is_prefilter_pattern({"slug": "rule:x"}))
        self.assertTrue(p.is_lattice_pattern({"slug": "rule:t-<a>", "lattice": {}}))
        self.assertFalse(p.is_lattice_pattern({"slug": "rule:t", "lattice": None}))
        self.assertFalse(p.is_lattice_pattern({"slug": "rule:t", "lattice": []}))
        self.assertEqual(p.pattern_slug({"slug": "rule:a-b (lattice) x"}), "rule:a-b")
        self.assertEqual(p.pattern_slug({"slug": "rule:a b"}), "rule:a")
        with self.assertRaises(KeyError):
            p.is_prefilter_pattern({})

    def test_quote_base_is_injected_and_only_called_when_needed(self):
        seen = []

        def base(key):
            seen.append(key)
            return "BASE"
        p = codebook_det_patterns
        self.assertEqual(p.quote_pattern_src({"resolved_slug": "rule:x", "pattern": "P"}, base), "P")
        self.assertEqual(seen, [])
        self.assertEqual(p.quote_pattern_src(
            {"resolved_slug": "rule:imposes-enters-tapped", "pattern": "doc"}, base), "BASE")
        self.assertEqual(seen, [p.ENTERS_TAPPED_BASE_SLUG])


class TestDetResolution(unittest.TestCase):
    DET = {"patterns": [
        {"slug": "rule:active-a", "status": "ratified", "pattern_index": 1},
        {"slug": "rule:proposed", "status": "proposed", "pattern_index": 2},
        {"slug": "rule:energy-x pre-filter (y)", "status": "ratified", "pattern_index": 3},
        {"slug": "rule:targeted-<action>-<class> (lattice)", "status": "ratified",
         "pattern_index": 4, "lattice": {"stems": ["destroy"]}},
        {"slug": "rule:deferred-b", "status": "ratified", "pattern_index": 5},
        {"slug": "rule:ruled-c", "status": "ratified", "pattern_index": 6},
    ]}
    CB = {"axes": {"rule:active-a": {"status": "active"},
                   "rule:deferred-b": {"status": "deferred"}}}

    def test_every_outcome_is_distinct(self):
        r = codebook_det_resolution.resolve_axis_patterns(
            self.DET, self.CB, ruled_axisless={"rule:ruled-c": "ruling"})
        self.assertEqual([p["resolved_slug"] for p in r.axis_patterns], ["rule:active-a"])
        self.assertEqual([p["pattern_index"] for p in r.prefilter_patterns], [3, 5, 6])
        self.assertEqual([p["pattern_index"] for p in r.lattice_rows], [4])
        self.assertEqual(r.ruled_gaps, ["rule:ruled-c"])
        self.assertEqual(r.deferred_gaps, [("rule:deferred-b", "deferred")])
        a, b, c = r[:3]
        self.assertIs(a, r.axis_patterns)

    def test_ONE_PATTERN_ONE_AXIS_an_unruled_orphan_is_refused(self):
        with self.assertRaises(codebook_det_resolution.UnresolvedAxisPatternError) as ctx:
            codebook_det_resolution.resolve_axis_patterns(self.DET, self.CB, ruled_axisless={})
        self.assertEqual(ctx.exception.slug, "rule:ruled-c")
        self.assertIn("has no axis in codebook.json at all", str(ctx.exception))

    def test_a_lattice_template_is_NOT_an_orphan(self):
        det = {"patterns": [self.DET["patterns"][3]]}
        r = codebook_det_resolution.resolve_axis_patterns(det, {"axes": {}})
        self.assertEqual(len(r.lattice_rows), 1)

    def test_the_default_register_is_read_at_call_time(self):
        reg = codebook_det_resolution.RULED_AXISLESS_PATTERNS
        reg["rule:ruled-c"] = "temporary"
        try:
            r = codebook_det_resolution.resolve_axis_patterns(self.DET, self.CB)
            self.assertEqual(r.ruled_gaps, ["rule:ruled-c"])
        finally:
            del reg["rule:ruled-c"]

    def test_the_legacy_register_is_the_same_object(self):
        _ensure_experiments_on_path()
        import foundry_det_pass as dp
        self.assertIs(dp.RULED_AXISLESS_PATTERNS, codebook_det_resolution.RULED_AXISLESS_PATTERNS)
        self.assertIs(dp.LATTICE_SCOPE_PARENT, codebook_lattice.LATTICE_SCOPE_PARENT)


class TestLattice(unittest.TestCase):
    L = codebook_lattice

    def test_slug_identity(self):
        self.assertEqual(self.L.slug_for("destroy"), "rule:targeted-destroy")
        self.assertEqual(self.L.slug_for("exile", "nonland-permanent"),
                         "rule:targeted-exile-nonland-permanent")

    def test_ORPHAN_a_child_without_a_scoped_parent_is_refused(self):
        axes = {"rule:targeted-destroy": {"scope": "s"}, "rule:targeted-exile": {"scope": "s"}}
        with self.assertRaises(self.L.LatticeGovernanceError):
            self.L.lattice_parent_scopes(axes)
        axes["rule:targeted-bounce-creature"] = {"scope": ""}
        with self.assertRaises(self.L.LatticeGovernanceError):
            self.L.lattice_parent_scopes(axes)
        axes["rule:targeted-bounce-creature"] = {"scope": "t"}
        self.assertEqual(self.L.lattice_parent_scopes(axes)["bounce"], "t")

    def test_axis_record_and_underivable_slug(self):
        rec = self.L.lattice_axis_record("rule:targeted-exile-nonland-permanent",
                                         {"exile": "any"})
        self.assertEqual((rec["scope"], rec["source"], rec["status"], rec["members"]),
                         ("any", "DET", "active", []))
        self.assertIn("exiles a target nonland permanent", rec["definition"])
        with self.assertRaises(self.L.LatticeGovernanceError):
            self.L.lattice_axis_record("rule:targeted-annihilate-creature", {})

    def test_expansion_refusals_and_late_binding_of_the_substrate(self):
        row = {"lattice": {"stems": ["destroy"]}}
        with self.assertRaises(self.L.LatticeGovernanceError):
            self.L.expand_lattice_pattern({"lattice": {"stems": ["obliterate"]}}, {}, set())
        real = target_classes.classes_for_card
        try:
            target_classes.classes_for_card = lambda card, stem, domain: {
                "classes": {"creature"}, "quotes": {"creature": card["q"]}}
            got = self.L.expand_lattice_pattern(row, {"b": {"q": "Destroy x."}, "a": {"q": "y"}}, set())
            self.assertEqual(got, {"rule:targeted-destroy-creature": {"a": "y", "b": "Destroy x."}})
            target_classes.classes_for_card = lambda card, stem, domain: {
                "classes": {"creature"}, "quotes": {}}
            with self.assertRaises(self.L.LatticeGovernanceError):   # quote-or-discard
                self.L.expand_lattice_pattern(row, {"a": {}}, set())
            target_classes.classes_for_card = lambda card, stem, domain: {
                "classes": set(), "quotes": {}}
            with self.assertRaises(self.L.LatticeGovernanceError):   # zero axes
                self.L.expand_lattice_pattern(row, {"a": {}}, set())
        finally:
            target_classes.classes_for_card = real

    def test_the_floor(self):
        stems = sorted(target_classes.ACTION_VERBS)
        doc = {"patterns": [{"slug": "x"}, {"lattice": {"stems": stems}, "corpus_hits": 10}]}
        self.assertEqual(self.L.ratified_total(doc, "d.json"), 10)
        for bad in ({"patterns": []},
                    {"patterns": [{"lattice": {"stems": ["destroy"]}, "corpus_hits": 1}]},
                    {"patterns": [{"lattice": {"stems": stems}, "corpus_hits": "10"}]}):
            with self.assertRaises(self.L.LatticeGovernanceError):
                self.L.ratified_total(bad, "d.json")
        self.assertEqual(self.L.ratified_total_verdict(10, 10), ([], []))
        fatal, notes = self.L.ratified_total_verdict(10, 9)
        self.assertEqual((len(fatal), notes), (1, []))
        self.assertIn("MEMBERSHIPS WERE LOST", fatal[0])
        fatal, notes = self.L.ratified_total_verdict(10, 11)
        self.assertEqual((fatal, len(notes)), ([], 1))

    def test_vocabulary_agreement_and_residual_message(self):
        self.L.assert_vocabulary_agrees({"a"}, {"a", "b"}, {"a"})
        with self.assertRaises(self.L.LatticeGovernanceError):
            self.L.assert_vocabulary_agrees({"a", "z"}, {"a"}, {"a", "z"})
        with self.assertRaises(self.L.LatticeGovernanceError):
            self.L.assert_vocabulary_agrees({"a"}, {"a"}, set())
        self.assertIsNone(self.L.residual_invariant_failure_message("destroy", []))
        msg = self.L.residual_invariant_failure_message(
            "destroy", [("Card", "arm", "creature", "q")])
        self.assertIn("rule:targeted-destroy-creature", msg)


class TestCoverage(unittest.TestCase):

    def test_the_two_tokenizations_are_kept_distinct(self):
        axes = {"rule:destroy-target": {"status": "active"},
                "rule:x:rule:y-z": {"status": "active"},
                "rule:exile-dead": {"status": "killed"}}
        a = codebook_coverage.covered_action_tokens(axes)
        b = codebook_coverage.slug_body_tokens(axes)
        self.assertNotIn("exile", a | b)
        self.assertEqual(a & {"destroy", "target"}, {"destroy", "target"})
        self.assertNotEqual(a, b)   # a second colon is where they part

    def test_uncovered_keyword_actions(self):
        reg = {"terms": [{"kind": "keyword-action", "term": "destroy", "cr": "701.8"},
                         {"kind": "keyword-action", "term": "mill", "cr": "701.13"},
                         {"kind": "keyword-action", "term": "scry", "cr": "701.18"},
                         {"kind": "keyword", "term": "flying", "cr": "702.9"}]}
        cards = [{"oracle_text": "Scry 1."},
                 {"oracle_text": "", "card_faces": [{"oracle_text": "Mill two."}, {}]},
                 {"oracle_text": "Mill a card.", "card_faces": [{"oracle_text": "scry"}]}]
        got = codebook_coverage.uncovered_keyword_actions(reg, {"destroy"}, cards)
        self.assertEqual(got, [(2, "mill", "701.13"), (1, "scry", "701.18")])
        self.assertEqual(codebook_coverage.keyword_action_count(reg), 3)


class TestLocalityBinding(unittest.TestCase):

    def _cb(self):
        return {"axes": {
            "rule:a": {"status": "active", "members": [
                {"oracle_id": "o1", "assertions": [
                    {"class": "human", "source_ref": "batch-1", "quote": "Q", "locality": [0, 0]},
                    {"class": "human", "source_ref": "batch-2", "quote": ""}]},
                {"oracle_id": "gone", "assertions": [
                    {"class": "human", "source_ref": "batch-1", "quote": "Q"}]}]},
            "rule:dead": {"status": "killed", "members": [
                {"oracle_id": "o1", "assertions": [{"quote": "Q"}]}]}}}

    def test_the_injected_resolver_is_the_one_used(self):
        calls = []

        def resolve(card, quote):
            calls.append((card["name"], quote))
            return {"status": s7_locality.SPAN, "owner": None, "candidates": [[0, 0], [0, 1]],
                    "reason": "span"}
        m = codebook_locality.census({"o1": {"name": "C"}}, self._cb(), resolve)
        self.assertEqual(calls, [("C", "Q")])
        self.assertEqual((m["assertions"], m["quoted"], m["quoteless"], m["span"],
                          m["unresolved"], m["stored_owned"], m["stored_mismatch"]),
                         (3, 2, 1, 1, 1, 1, 1))
        rows = codebook_locality.unaddressed_rows({"o1": {"name": "C"}}, self._cb(), resolve)
        self.assertEqual([r["reason"] for r in rows], ["QUOTELESS", "SPAN", "UNRESOLVED"])


class TestDetApply(unittest.TestCase):
    OID = "11111111-1111-1111-1111-111111111111"

    def _axes(self):
        return {"rule:x": {"members": [{"oracle_id": self.OID, "assertions": [
            codebook.build_assertion("human", "batch-1", "keep me", "2026-07-04"),
            codebook.build_assertion("rule-derived", "det-patterns-v2:7", "old", "2026-07-04")]}],
            "history": []}}

    def test_A8_replaces_only_its_own_rows(self):
        axes = self._axes()
        p = {"resolved_slug": "rule:x", "pattern_index": 7, "seed": 1, "pattern": r"draw \w+"}
        applied = codebook_det_apply.apply_axis_patterns(
            axes, [p], {"rule:x": [self.OID]}, {}, {self.OID: ["Draw cards."]}, "2026-07-04",
            quote_pattern_src=lambda pat: pat["pattern"], resolve_owner=lambda o, c: None)
        self.assertEqual(applied, [("rule:x", 1, 1, 0)])
        asserts = axes["rule:x"]["members"][0]["assertions"]
        self.assertEqual([(a["class"], a["quote"]) for a in asserts],
                         [("human", "keep me"), ("rule-derived", "Draw cards")])
        self.assertNotIn("locality", asserts[1])
        self.assertEqual(axes["rule:x"]["source"], "DET")
        self.assertEqual(axes["rule:x"]["history"][-1]["action"], "det_membership_applied")

    def test_refusals(self):
        p = {"resolved_slug": "rule:x", "pattern_index": 7, "seed": 1, "pattern": "zzz"}
        with self.assertRaises(codebook_det_apply.DetApplyError):
            codebook_det_apply.apply_axis_patterns(
                self._axes(), [p], {"rule:x": ["nope"]}, {}, {}, "2026-07-04",
                quote_pattern_src=lambda pat: pat["pattern"], resolve_owner=lambda o, c: None)
        with self.assertRaises(codebook_det_apply.DetApplyError):
            codebook_det_apply.apply_axis_patterns(
                self._axes(), [p], {"rule:x": [self.OID]}, {}, {self.OID: ["nothing"]},
                "2026-07-04", quote_pattern_src=lambda pat: pat["pattern"],
                resolve_owner=lambda o, c: None)
        self.assertIsNone(codebook_det_apply.lattice_cache_disagreement({"s": {"a": 1}}, {"s": ["a"]}))
        self.assertIn("re-derives 1 hits but the cache from generate-samples holds 0",
                      codebook_det_apply.lattice_cache_disagreement({"s": {"a": 1}}, {}))

    def test_instantiation(self):
        axes = {"rule:targeted-destroy-creature": {"existing": True}}
        got = codebook_det_apply.instantiate_lattice_axes(
            axes, {"rule:targeted-exile-land": {}, "rule:targeted-destroy-creature": {}},
            {"exile": "any"})
        self.assertEqual(got, ["rule:targeted-exile-land"])
        self.assertEqual(axes["rule:targeted-destroy-creature"], {"existing": True})
        self.assertEqual(axes["rule:targeted-exile-land"]["history"][0]["action"], "created")


class TestMembership(unittest.TestCase):
    M = codebook_membership
    A = "aaaaaaaa-0000-0000-0000-000000000000"
    B = "bbbbbbbb-0000-0000-0000-000000000000"

    def _cb(self):
        member = lambda o: {"oracle_id": o, "assertions": [{"class": "human", "source_ref": "batch-1",  # noqa: E731
                                                            "quote": "q", "corpus_ref": "2026-07-04",
                                                            "evidence_status": "quoted"}]}
        return {"schema": codebook.SCHEMA_V2, "axes": {
            "rule:src": {"status": "active", "scope": "self", "members": [member(self.A), member(self.B)]},
            "rule:dst": {"status": "active", "scope": "self", "members": []},
            "rule:dead": {"status": "killed", "members": []}}}

    def test_the_input_is_never_mutated_and_moves_conserve(self):
        cb = self._cb()
        before = json.dumps(cb, sort_keys=True)
        spec = {"batch": "t", "moves": [{"from": "rule:src", "to": "rule:dst", "members": [self.A]}]}
        out = self.M.apply_spec(cb, spec)
        self.assertEqual(json.dumps(cb, sort_keys=True), before)
        self.assertEqual([m["oracle_id"] for m in out["axes"]["rule:dst"]["members"]], [self.A])
        self.assertTrue(self.M.member_conservation(cb, out, spec)["ok"])

    def test_refusals(self):
        for spec in ({"moves": [{"from": "rule:dead", "to": "rule:dst", "members": []}]},
                     {"moves": [{"from": "rule:src", "to": "rule:dst", "members": ["x"]}]},
                     {"adds": [{"from": "rule:src", "to": "rule:dst", "member": self.A}]},
                     {"drops": [{"from": "rule:dst", "member": self.A}]},
                     {"scope_edits": {"rule:src": "self"}}):
            with self.subTest(spec=spec), self.assertRaises(self.M.MembershipSpecError):
                self.M.apply_spec(self._cb(), dict(spec, batch="t"))

    def test_gate0(self):
        cb = self._cb()
        cards = {self.A: {"name": "Legal", "legal": True}, self.B: {"name": "Gone", "set": "x", "legal": False}}
        r = self.M.scrub_gate0_members(cb["axes"], cards, lambda c: c["legal"])
        self.assertEqual((r["total_checked"], r["total_gated"]), (2, 1))
        self.assertEqual([m["oracle_id"] for m in cb["axes"]["rule:src"]["members"]], [self.A])
        cb = self._cb()
        with self.assertRaises(self.M.Gate0ScrubError):
            self.M.scrub_gate0_members(cb["axes"], {self.A: {"legal": True}}, lambda c: c["legal"])
        self.assertEqual(len(cb["axes"]["rule:src"]["members"]), 2)   # unknown card kept


class TestSlug(unittest.TestCase):
    S = codebook_slug

    def test_parse_guards(self):
        good = "x Closed restriction vocab: `by-color`, `except-by-count`, `as-long-as-<state>` (then `rule:x`)"
        self.assertIn("except", self.S.parse_q85_restriction_vocab(good))
        self.assertNotIn("state", self.S.parse_q85_restriction_vocab(good))
        for bad in ("nothing here",
                    "Closed restriction vocab: `by-color`",
                    "Closed restriction vocab: `except-by-count` `by-<state`",
                    "Closed restriction vocab: `except-by-count` `countered`"):
            with self.subTest(bad=bad), self.assertRaises(self.S.SlugVocabularyError):
                self.S.parse_q85_restriction_vocab(bad)

    def test_closed_vocab_is_required_and_decides(self):
        with self.assertRaises(TypeError):
            self.S.validate_slug("rule:draw")
        small = self.S.compose_closed_vocab(set(), set())
        self.assertFalse(self.S.validate_slug("rule:frobnicate", closed_vocab=small)["ok"])
        self.assertTrue(self.S.validate_slug("rule:frobnicate", closed_vocab=small | {"frobnicate"})["ok"])
        self.assertEqual(self.S.keyword_vocab_from_buckets({"keywords": {"first-strike": {}}}) >= {"first", "strike"}, True)
        self.assertIsNotNone(self.S.q85_live_axis_violation(
            {"by"}, {"axes": {"rule:cant-be-blocked-by-toughness": {"status": "active"}}}))

    def test_the_legacy_boundary_uses_the_owner_objects_and_its_own_vocab_at_call_time(self):
        _ensure_experiments_on_path()
        import validate_slug as vs
        for name in ("OBJECT_VOCAB", "DELIVERY_VOCAB", "EXEMPT_LEAF_SLUGS",
                     "ACTIVATION_RESTRICTION_FAMILY", "normalize_for_collision"):
            with self.subTest(name=name):
                self.assertIs(getattr(vs, name), getattr(self.S, name))
        real = vs.CLOSED_VOCAB
        try:
            vs.CLOSED_VOCAB = set(real) | {"frobnicate"}
            self.assertTrue(vs.validate_slug("rule:frobnicate")["ok"])
        finally:
            vs.CLOSED_VOCAB = real
        self.assertFalse(vs.validate_slug("rule:frobnicate")["ok"])


# ===========================================================================
# 2. pattern_role: ONE definition
# ===========================================================================

ROLE_NAMES = ("is_prefilter_pattern", "is_lattice_pattern", "pattern_slug")
CANONICAL = "src/mtj_foundry/codebook_det_patterns.py"
# The ONE executable inline copy of a role's EXPRESSION that S11 may not edit:
# `foundry_verify_migration.py`, the /1 -> /2 migration's independent verifier.
# S15 preflight classifies it ARCHIVE_MUTATION_PROVENANCE / ARCHIVE_EVIDENCE: the
# executor/verifier provenance set is preserved as-is for archival, so its
# independent re-derivation is historical verification evidence, not a live
# consumer. S11 removed the copies in `foundry_family_sweep.load_stores` and
# `foundry_object_lattice.ratified_total`; S11.R1 removed the one in the live
# executable `foundry_stage1b.load_det_owned_slugs`.
# Source inside a string literal (an NC fixture) is not code and is not counted.
# This set may shrink; it may not grow.
DECLARED_INLINE = {
    ("experiments/foundry_verify_migration.py", "pattern_slug"),
}
INLINE_SHAPES = {
    "pattern_slug": ".split(' (')[0].split(' ')[0]",
    "is_prefilter_pattern": "'pre-filter' in ",
    "is_lattice_pattern": ".get('lattice'), dict)",
}


def role_census(sources: dict) -> dict:
    """{'definitions': [(path, name)], 'bad_facades': [...], 'inline': {(path, name)}}."""
    defs, bad, inline = [], [], set()
    for path, text in sources.items():
        tree = ast.parse(text, filename=path)
        aliases = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "mtj_foundry":
                aliases |= {a.asname or a.name for a in node.names
                            if a.name == "codebook_det_patterns"}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in ROLE_NAMES:
                body = [s for s in node.body
                        if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
                delegate = (path != CANONICAL and len(body) == 1
                            and isinstance(body[0], ast.Return)
                            and isinstance(body[0].value, ast.Call)
                            and isinstance(body[0].value.func, ast.Attribute)
                            and body[0].value.func.attr == node.name
                            and isinstance(body[0].value.func.value, ast.Name)
                            and body[0].value.func.value.id in aliases
                            and [ast.unparse(a) for a in body[0].value.args]
                            == [a.arg for a in node.args.args])
                if path == CANONICAL:
                    defs.append((path, node.name))
                elif not delegate:
                    bad.append((path, node.name))
        if path == CANONICAL:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.Compare, ast.Call, ast.Subscript)):
                src = ast.unparse(node)
                for name, shape in INLINE_SHAPES.items():
                    if shape in src and (name != "is_prefilter_pattern" or "['slug']" in src):
                        inline.add((path, name))
    return {"definitions": sorted(defs), "bad_facades": sorted(bad), "inline": inline}


def tracked_python(root: Path) -> dict:
    # cached AND untracked-not-ignored: a new duplicate is a duplicate before commit.
    listed = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--cached", "--others",
                             "--exclude-standard", "*.py"],
                            capture_output=True, check=True).stdout.decode().split("\0")
    return {p: (root / p).read_text(encoding="utf-8") for p in listed
            if p and (root / p).exists() and not p.startswith("archive/")}


@unittest.skipUnless((REPO_ROOT / ".git").exists(), "measured from git ls-files")
class TestPatternRoleSingleDefinition(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.sources = tracked_python(REPO_ROOT)

    def test_exactly_one_definition_each_and_every_other_def_is_a_pure_delegate(self):
        c = role_census(self.sources)
        self.assertEqual(c["definitions"], sorted((CANONICAL, n) for n in ROLE_NAMES))
        self.assertEqual(c["bad_facades"], [])
        self.assertEqual(c["inline"], DECLARED_INLINE)

    def test_CONTROL_a_second_real_definition_is_caught(self):
        sources = dict(self.sources)
        path = "src/mtj_foundry/codebook_det_resolution.py"
        sources[path] += ('\n\ndef is_prefilter_pattern(pattern):\n'
                          '    return "pre-filter" in pattern["slug"]\n')
        c = role_census(sources)
        self.assertIn((path, "is_prefilter_pattern"), c["bad_facades"])
        self.assertIn((path, "is_prefilter_pattern"), c["inline"])

    def test_CONTROL_a_facade_that_adds_logic_is_caught(self):
        sources = dict(self.sources)
        path = "experiments/foundry_common.py"
        old = "    return _det_patterns.pattern_slug(pattern)\n"
        self.assertEqual(sources[path].count(old), 1)
        sources[path] = sources[path].replace(old, "    return _det_patterns.pattern_slug(pattern).lower()\n")
        self.assertIn((path, "pattern_slug"), role_census(sources)["bad_facades"])

    def test_CONTROL_a_new_inline_copy_is_caught(self):
        sources = dict(self.sources)
        path = "tests/guards/gate2/foundry_family_sweep.py"
        sources[path] += '\nX = {"slug": "a"}["slug"].split(" (")[0].split(" ")[0]\n'
        self.assertNotEqual(role_census(sources)["inline"], DECLARED_INLINE)

    def test_CONTROL_reverting_the_stage1b_repair_is_caught(self):
        """S11.R1: the live executable's inline copy may not come back."""
        sources = dict(self.sources)
        path = "experiments/foundry_stage1b.py"
        old = "        _det_patterns.pattern_slug(p)\n"
        self.assertEqual(sources[path].count(old), 1)
        sources[path] = sources[path].replace(
            old, '        p["slug"].split(" (")[0].split(" ")[0]\n')
        self.assertIn((path, "pattern_slug"), role_census(sources)["inline"])

    def test_stage1b_reads_the_canonical_owner_at_call_time(self):
        _ensure_experiments_on_path()
        import foundry_stage1b
        real = codebook_det_patterns.pattern_slug
        codebook_det_patterns.pattern_slug = lambda p: "SENTINEL"
        try:
            got = foundry_stage1b.load_det_owned_slugs()
        finally:
            codebook_det_patterns.pattern_slug = real
        self.assertEqual(got, {"SENTINEL"})

    def test_legacy_facades_resolve_the_owner_at_CALL_time(self):
        _ensure_experiments_on_path()
        import foundry_common as fc
        import foundry_det_pass as dp
        for holder, name in ((fc, "is_prefilter_pattern"), (fc, "is_lattice_pattern"),
                             (fc, "pattern_slug"), (dp, "is_lattice_pattern")):
            with self.subTest(holder=holder.__name__, name=name):
                real = getattr(codebook_det_patterns, name)
                sentinel = object()
                setattr(codebook_det_patterns, name, lambda *a, **k: sentinel)
                try:
                    self.assertIs(getattr(holder, name)({"slug": "x"}), sentinel)
                finally:
                    setattr(codebook_det_patterns, name, real)


# ===========================================================================
# 3. S7 late binding reaches the S11 consumers
# ===========================================================================

class TestS7LateBindingThroughS11Consumers(unittest.TestCase):
    """The consumer is the legacy locality shell's `census` -> the S11 binding ->
    the shell's `resolve` -> S7 `CardFaceRules(fc)` -> `fc.raw_faces` ->
    `mtj_foundry.corpus.card_faces`. The provider is replaced AFTER every shell
    has installed its rules."""

    CARD = {"name": "Zed", "oracle_text": "Flying\nDraw a card.", "type_line": "Creature"}

    def _cb(self):
        return {"axes": {"rule:a": {"status": "active", "members": [{"oracle_id": "o", "assertions": [
            {"class": "human", "source_ref": "batch-1", "quote": "Draw a card."}]}]}}}

    def _census(self, fl):
        return codebook_locality.census({"o": self.CARD}, self._cb(), fl.resolve)

    def test_a_runtime_replacement_reaches_the_same_consumer(self):
        _ensure_experiments_on_path()
        import foundry_locality as fl
        self.assertEqual(self._census(fl)["owned"], 1)
        real = corpus.card_faces
        corpus.card_faces = lambda card: []
        try:
            m = self._census(fl)
        finally:
            corpus.card_faces = real
        self.assertEqual((m["owned"], m["unresolved"]), (0, 1))
        self.assertEqual(self._census(fl)["owned"], 1)

    def test_CONTROL_a_captured_provider_is_detected(self):
        _ensure_experiments_on_path()
        import foundry_common as fc
        import foundry_locality as fl
        installed = s7_locality._rules()
        # The owner's function OBJECT, captured now -- the rejected S7 shape.
        captured = SimpleNamespace(raw_faces=corpus.card_faces,
                                   canonicalize_self_reference=fc.canonicalize_self_reference)
        s7_locality.use_card_face_rules(s7_locality.CardFaceRules(
            captured, {"raw_faces": "raw_faces",
                       "canonicalize_self_reference": "canonicalize_self_reference"}))
        real = corpus.card_faces
        corpus.card_faces = lambda card: []
        try:
            m = self._census(fl)
        finally:
            corpus.card_faces = real
            s7_locality.use_card_face_rules(installed)
        self.assertEqual(m["owned"], 1, "a captured provider must NOT see the replacement")
        self.assertIs(s7_locality._rules(), installed)

    def test_the_DET_apply_consumer_reads_text_match_at_call_time(self):
        oid = "11111111-1111-1111-1111-111111111111"
        axes = {"rule:x": {"members": [], "history": []}}
        p = {"resolved_slug": "rule:x", "pattern_index": 1, "seed": 1, "pattern": "zzz"}
        real = text_match.matched_clause
        text_match.matched_clause = lambda compiled, texts: "REPLACED"
        try:
            codebook_det_apply.apply_axis_patterns(
                axes, [p], {"rule:x": [oid]}, {}, {oid: ["no match"]}, "2026-07-04",
                quote_pattern_src=lambda pat: pat["pattern"], resolve_owner=lambda o, c: None)
        finally:
            text_match.matched_clause = real
        self.assertEqual(axes["rule:x"]["members"][0]["assertions"][0]["quote"], "REPLACED")


# ===========================================================================
# 4. layering
# ===========================================================================

def package_graph(pkg: Path) -> dict:
    graph = {}
    for path in sorted(pkg.rglob("*.py")):
        rel = path.relative_to(pkg.parent).with_suffix("")
        name = ".".join(rel.parts)
        if name.endswith(".__init__"):
            name = name[: -len(".__init__")]
        graph[name] = {m for m in _imports(ast.parse(path.read_text(encoding="utf-8")))
                       if m.startswith("mtj_foundry")}
    modules = set(graph)
    return {n: {m for m in deps if m in modules and m != n
                and not (n.startswith(m + ".") and m == "mtj_foundry")}
            for n, deps in graph.items()}


def find_cycle(graph: dict):
    """Kahn's algorithm; returns the nodes left in a cycle, or [] when acyclic."""
    indeg = {n: 0 for n in graph}
    for n, deps in graph.items():
        for d in deps:
            indeg[n] += 1
    ready = sorted(n for n, k in indeg.items() if k == 0)
    users = {n: {m for m, deps in graph.items() if n in deps} for n in graph}
    seen = set()
    while ready:
        n = ready.pop(0)
        seen.add(n)
        for u in sorted(users[n]):
            indeg[u] -= 1
            if indeg[u] == 0:
                ready.append(u)
    return sorted(set(graph) - seen)


class TestTheKernelIsLayered(unittest.TestCase):

    def test_each_owner_imports_only_its_declared_lower_layers(self):
        for name, allowed in S11_MODULES.items():
            with self.subTest(module=name):
                tree = ast.parse((PKG / f"{name}.py").read_text(encoding="utf-8"))
                got = _imports(tree)
                internal = {m for m in got if m.startswith("mtj_foundry.")}
                # `from mtj_foundry.mtg.shapes import locality` names the MODULE
                # `mtj_foundry.mtg.shapes.locality`; its parent package is not an edge.
                internal = {m for m in internal if not any(o.startswith(m + ".") for o in internal)}
                self.assertEqual(internal, allowed)
                self.assertEqual({m for m in got if not m.startswith("mtj_foundry")} - STDLIB_OK, set())

    def test_no_io_no_exit_no_print_no_root(self):
        for name in S11_MODULES:
            text = (PKG / f"{name}.py").read_text(encoding="utf-8")
            tree = ast.parse(text)
            calls = {ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)}
            with self.subTest(module=name):
                for forbidden in ("open", "print", "sys.exit", "exit", "Path"):
                    self.assertNotIn(forbidden, calls)
                names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
                self.assertNotIn("__file__", names)
                self.assertNotIn("SystemExit", names)

    def test_no_production_module_imports_experiments_aq4_or_a_shell(self):
        offenders = []
        for path in sorted(PKG.rglob("*.py")):
            for m in _imports(ast.parse(path.read_text(encoding="utf-8"))):
                if m.startswith(("foundry_", "experiments", "aq4", "tier_engine", "validate_slug")):
                    offenders.append((path.name, m))
        self.assertEqual(offenders, [])

    def test_mtg_imports_no_codebook_module(self):
        for path in sorted((PKG / "mtg").rglob("*.py")):
            with self.subTest(module=str(path.relative_to(PKG))):
                bad = {m for m in _imports(ast.parse(path.read_text(encoding="utf-8")))
                       if m.startswith("mtj_foundry.codebook")}
                self.assertEqual(bad, set())

    def test_the_package_graph_is_acyclic(self):
        self.assertEqual(find_cycle(package_graph(PKG)), [])

    def test_CONTROL_an_upward_edge_is_reported_as_a_cycle(self):
        g = package_graph(PKG)
        g["mtj_foundry.codebook_det_patterns"] = set(g["mtj_foundry.codebook_det_patterns"]) | {
            "mtj_foundry.codebook_det_resolution"}
        self.assertIn("mtj_foundry.codebook_det_patterns", find_cycle(g))
        g = package_graph(PKG)
        g["mtj_foundry.mtg.shapes.locality"] = set(g["mtj_foundry.mtg.shapes.locality"]) | {
            "mtj_foundry.codebook_locality"}
        self.assertIn("mtj_foundry.codebook_locality", find_cycle(g))

    def test_import_with_only_src_from_an_unrelated_cwd(self):
        code = ("import sys\n"
                "import mtj_foundry.codebook_det_apply, mtj_foundry.codebook_slug, "
                "mtj_foundry.codebook_membership, mtj_foundry.codebook_coverage, "
                "mtj_foundry.codebook_locality, mtj_foundry.codebook_det_resolution\n"
                "bad = sorted(m for m in sys.modules if m.startswith(('foundry_', 'experiments', 'validate_slug')))\n"
                "print(bad)\n")
        res = subprocess.run([sys.executable, "-c", code], cwd="/", capture_output=True, text=True,
                             env={"PATH": "/usr/bin:/bin", "PYTHONPATH": str(SRC)})
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(res.stdout.strip(), "[]")


# ===========================================================================
# 5. membership conservation over the SELECTED codebook
# ===========================================================================

SELECTOR = json.loads((REPO_ROOT / "config" / "selectors" / "codebook-authority.json")
                      .read_text(encoding="utf-8"))
CODEBOOK_FILE = ProjectPaths.for_root(REPO_ROOT).legacy_codebook_json
# Measured by running `s11_conservation` against the LEGACY callables at accepted
# base 8886a86f8a2da90bd9b0bd71fc4b33213abc9250 (foundry_det_pass.load_axis_patterns,
# foundry_membership_move.apply_spec) over the selected codebook.
PIN = {
    "partition": "05bf0a5bd6be73e9c2abf35dd61bca53e2e420ca4ec8c6a33a41722b0f0137f4",
    "partition_sizes": (38, 6, 1),
    "selected_fingerprint": "198c64d3ff72f280a8e871a19d2851423e1b964e88546d838f39d361b77f2b46",
    "spec_result_fingerprint": "71defd26bd343340d85ace0abae4a1d260309b9448282d7ef4fb63b3e5231d4c",
    "spec_result_sha256": "e2a0c733b30fd6fc293303ffdb38318fa02bcb693a98a806de3e7d77c78bddc1",
}


@unittest.skipUnless(CODEBOOK_FILE.exists(), "the selected codebook is gitignored local state")
class TestMembershipConservationOverTheSelectedCodebook(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        raw = CODEBOOK_FILE.read_bytes()
        cls.sha = hashlib.sha256(raw).hexdigest()
        cls.size = len(raw)
        cls.cb = json.loads(raw)

    def test_0_it_IS_the_selected_codebook(self):
        self.assertEqual((self.sha, self.size), (SELECTOR["sha256"], SELECTOR["byte_size"]),
                         "a codebook is present but it is not the selected one")

    def test_the_resolution_partition(self):
        det = json.loads((ProjectPaths.for_root(REPO_ROOT).config_semantic
                          / "det-patterns-v2.json").read_text(encoding="utf-8"))
        r = codebook_det_resolution.resolve_axis_patterns(det, self.cb)
        self.assertEqual(tuple(len(x) for x in r[:3]), PIN["partition_sizes"])
        self.assertEqual(cons.partition_digest(*r[:3]), PIN["partition"])

    def test_spec_application_conserves_membership_x2(self):
        spec = cons.harness_spec(self.cb)
        once = codebook_membership.apply_spec(self.cb, spec)
        twice = codebook_membership.apply_spec(self.cb, spec)
        from mtj_foundry import codebook_store
        a, b = codebook_store.serialize(once), codebook_store.serialize(twice)
        self.assertEqual(a, b)
        self.assertEqual(cons.text_sha256(a), PIN["spec_result_sha256"])
        self.assertEqual(cons.membership_fingerprint(once), PIN["spec_result_fingerprint"])
        self.assertTrue(codebook_membership.member_conservation(self.cb, once, spec)["ok"])
        codebook.lint(once)
        self.assertEqual(cons.membership_fingerprint(self.cb), PIN["selected_fingerprint"])

    def test_gate0_dry_run_changes_no_membership(self):
        if not ProjectPaths.for_root(REPO_ROOT).legacy_oracle_cards.exists():
            self.skipTest("the corpus is gitignored local state")
        _ensure_experiments_on_path()
        import foundry_common as fc
        cards_all, _ = fc.load_corpus()
        work = copy.deepcopy(self.cb)
        r = codebook_membership.scrub_gate0_members(work["axes"], cards_all, corpus.is_gate0_eligible)
        self.assertEqual(r["total_gated"], 0)
        self.assertEqual(cons.membership_fingerprint(work), PIN["selected_fingerprint"])

    def test_CONTROL_one_substituted_member_is_caught_where_a_count_is_not(self):
        spec = cons.harness_spec(self.cb)
        result = codebook_membership.apply_spec(self.cb, spec)
        slug = next(s for s in sorted(result["axes"]) if result["axes"][s].get("members"))
        result["axes"][slug]["members"][0]["oracle_id"] = "00000000-0000-0000-0000-00000000dead"
        self.assertTrue(codebook_membership.member_conservation(self.cb, result, spec)["ok"],
                        "the count-based check is blind to substitution -- that is the point")
        self.assertNotEqual(cons.membership_fingerprint(result), PIN["spec_result_fingerprint"])

    def test_CONTROL_a_perturbed_order_breaks_byte_determinism(self):
        from mtj_foundry import codebook_store
        spec = cons.harness_spec(self.cb)
        once = codebook_membership.apply_spec(self.cb, spec)
        twice = codebook_membership.apply_spec(self.cb, spec)
        slug = next(s for s in sorted(twice["axes"]) if len(twice["axes"][s].get("members", [])) > 1)
        twice["axes"][slug]["members"].reverse()
        self.assertNotEqual(codebook_store.serialize(once), codebook_store.serialize(twice))
        self.assertNotEqual(cons.membership_fingerprint(twice), PIN["spec_result_fingerprint"])


if __name__ == "__main__":
    unittest.main()
