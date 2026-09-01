"""C8.5M — the codebook SEMANTIC MODEL as a permanent capability.

Two claims, and they are different claims:

1. `mtj_foundry.codebook` is a **pure, stdlib-only, non-exiting** library: one
   import beyond `__future__`, no filesystem, no printing, no process exit, no
   knowledge of where the repository is.
2. `experiments/foundry_codebook.py` still behaves **exactly** as it did, for
   the 30 legacy importers and the two monkeypatch seams that have not moved.

The second is the harder one, because the two are in tension: a library may not
call `sys.exit`, and the legacy callers require that it does. The resolution is
structural and is asserted here — a **direct alias** wherever the failure
behaviour is unchanged, and a **thin translation wrapper** for exactly the three
entry points whose failure used to end the process.

This file states no repository layout. It reaches the legacy module through the
established `load_legacy` helper and the permanent module through an ordinary
import, so it introduces no root derivation, no `ProjectPaths`, no
`Path(__file__)` and no `sys.path` write — and therefore no new census row.
"""

from __future__ import annotations

import ast
import contextlib
import copy
import inspect
import io
import unittest

from tests.refoundation.test_gate2_purity import load_legacy

from mtj_foundry import codebook


# The 18 names the permanent module contracts to expose, written out rather than
# derived from `codebook.__all__` — a guard that reads its subject's own answer
# back to it proves nothing.
EXPECTED_ALL = [
    "ASSERTION_KEY_ORDER",
    "CodebookError",
    "DET_SOURCE_REF_PREFIX",
    "DuplicateAssertionError",
    "InvalidOracleIdError",
    "LintError",
    "LocalityError",
    "SCHEMA_V1",
    "SCHEMA_V2",
    "build_assertion",
    "expected_tier",
    "lint",
    "member_by_id",
    "member_id_set",
    "member_ids",
    "merge_assertion",
    "normalize_locality",
    "remove_det_assertions",
]

# Names the facade must expose as THE SAME OBJECT the permanent module holds.
# Anything on this list that turns into a local definition is a second
# implementation of a migrated semantic fact, which is the one thing this slice
# forbids.
DIRECT_ALIASES = [
    "SCHEMA_V2", "SCHEMA_V1", "CLASSES", "EVIDENCE_STATUSES", "LANES",
    "AXIS_STATUSES", "SCOREABLE_LANES", "TIERS", "ASSERTION_KEY_ORDER",
    "MEMBER_KEY_ORDER", "_UUID_RE", "_SOURCE_REF_RES", "DET_SOURCE_REF_PREFIX",
    "SOURCE_REF_FAMILIES", "_DATE_RE", "AXIS_INVARIANT_EXEMPTIONS", "LintError",
    "member_ids", "member_id_set", "member_by_id", "expected_tier",
    "_reorder_member", "_assertion_sort_key", "remove_det_assertions", "lint",
]

# The exactly-three entry points whose legacy failure ended the process, with the
# permanent errors each is allowed to translate. Not four, not two.
WRAPPERS = {
    "normalize_locality": ("LocalityError",),
    "build_assertion": ("LocalityError",),
    "merge_assertion": ("InvalidOracleIdError", "DuplicateAssertionError"),
}

OID = ["%08x-0000-4000-8000-%012x" % (i, i) for i in range(6)]


def assertion(cls, source_ref, quote="q", corpus_ref="2026-07-04",
              evidence_status="quoted", **kw):
    return codebook.build_assertion(cls, source_ref, quote, corpus_ref,
                                    evidence_status, **kw)


def document(axes):
    return {"schema": codebook.SCHEMA_V2, "version": "0.7", "axes": axes}


# ===========================================================================
# 1. THE PERMANENT MODULE IS A LIBRARY
# ===========================================================================

class TestThePermanentSurface(unittest.TestCase):

    def test_the_public_api_is_exactly_the_contracted_eighteen(self):
        self.assertEqual(sorted(codebook.__all__), EXPECTED_ALL)
        self.assertEqual(len(codebook.__all__), 18)

    def test_every_exported_name_exists(self):
        for name in EXPECTED_ALL:
            with self.subTest(name=name):
                self.assertTrue(hasattr(codebook, name))

    def test_the_error_hierarchy_is_five_types_under_one_base(self):
        self.assertTrue(issubclass(codebook.CodebookError, Exception))
        for leaf in ("LintError", "LocalityError", "InvalidOracleIdError",
                     "DuplicateAssertionError"):
            with self.subTest(leaf=leaf):
                self.assertTrue(issubclass(getattr(codebook, leaf),
                                           codebook.CodebookError))
        # Distinct types, not aliases of one another: three different controls in
        # the legacy tree key on three different failures, and a shared type
        # would let two of them agree for the wrong reason.
        leaves = {codebook.LintError, codebook.LocalityError,
                  codebook.InvalidOracleIdError, codebook.DuplicateAssertionError}
        self.assertEqual(len(leaves), 4)

    def test_the_schema_names_are_the_ratified_strings(self):
        self.assertEqual(codebook.SCHEMA_V2, "foundry-codebook/2")
        self.assertEqual(codebook.SCHEMA_V1, "foundry-codebook/1")


class TestThePermanentModuleIsPure(unittest.TestCase):
    """Structural, on the AST — never on the prose. The module's own docstring
    names `fc.halt`, `sys.exit` and the filesystem to explain what it is not,
    and a textual guard would forbid the explanation. Same shape as this
    repository's ratified 'a rejected term in backticks is ingested as
    vocabulary' trap."""

    @classmethod
    def setUpClass(cls):
        cls.tree = ast.parse(inspect.getsource(codebook))

    def test_it_imports_only_future_and_re(self):
        imported = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imported |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertEqual(imported, {"__future__", "re"})

    def test_it_never_prints_exits_or_halts(self):
        calls = [ast.unparse(n.func) for n in ast.walk(self.tree)
                 if isinstance(n, ast.Call)]
        for banned in ("print", "exit", "sys.exit", "fc.halt", "open"):
            with self.subTest(call=banned):
                self.assertNotIn(banned, calls)

    def test_it_never_touches_sys_path_or_the_filesystem(self):
        attributes = [ast.unparse(n) for n in ast.walk(self.tree)
                      if isinstance(n, ast.Attribute)]
        for banned in ("sys.path", "os.path", "Path", "pathlib"):
            with self.subTest(name=banned):
                self.assertFalse([a for a in attributes if a.startswith(banned)])

    def test_it_states_no_repository_layout(self):
        """No module-level constant may name a repository path or a root."""
        for node in self.tree.body:
            if not isinstance(node, ast.Assign):
                continue
            text = ast.unparse(node)
            for banned in ("REPO_ROOT", "__file__", "ProjectPaths",
                           "experiments/", "docs/", "data/", "codebook.json"):
                with self.subTest(binding=text.split("=")[0].strip(), banned=banned):
                    self.assertNotIn(banned, text)

    def test_the_internally_owned_semantic_state_is_present_here(self):
        """These are not exported, but they must LIVE here — a migrated
        definition that stayed behind in the legacy file would be the
        duplication this slice exists to end."""
        for name in ("CLASSES", "EVIDENCE_STATUSES", "LANES", "AXIS_STATUSES",
                     "SCOREABLE_LANES", "TIERS", "MEMBER_KEY_ORDER", "_UUID_RE",
                     "_SOURCE_REF_RES", "SOURCE_REF_FAMILIES", "_DATE_RE",
                     "AXIS_INVARIANT_EXEMPTIONS", "_reorder_member",
                     "_assertion_sort_key"):
            with self.subTest(name=name):
                self.assertTrue(hasattr(codebook, name))

    def test_the_declared_debt_register_is_still_empty(self):
        """`AXIS_INVARIANT_EXEMPTIONS` is a Captain-visible debt register, not a
        vocabulary. Its one historical entry was ruled on 2026-08-01 and
        corrected, so the invariant holds outright; a silent refill would be a
        lint exemption nobody ratified."""
        self.assertEqual(codebook.AXIS_INVARIANT_EXEMPTIONS, {})


# ===========================================================================
# 2. THE PERMANENT MODEL'S BEHAVIOUR
# ===========================================================================

class TestBuildAssertion(unittest.TestCase):

    def test_optional_keys_are_omitted_entirely_never_emitted_as_null(self):
        a = assertion("human", "batch-3")
        self.assertEqual(list(a), ["class", "source_ref", "quote", "corpus_ref",
                                   "evidence_status"])
        for absent in ("original_lane", "effective_lane", "promotion_reason",
                       "locality"):
            self.assertNotIn(absent, a)

    def test_present_keys_follow_ASSERTION_KEY_ORDER_with_locality_last(self):
        a = assertion("llm", "run1", original_lane="free",
                      effective_lane="codebook", promotion_reason="p",
                      locality=(1, 2))
        self.assertEqual(list(a), [k for k in codebook.ASSERTION_KEY_ORDER
                                   if k in a])
        self.assertEqual(list(a)[-1], "locality")

    def test_a_tuple_locality_is_stored_as_a_list_of_ints(self):
        self.assertEqual(assertion("human", "batch-1", locality=(0, 3))["locality"],
                         [0, 3])
        self.assertEqual(codebook.normalize_locality([2, 5]), [2, 5])

    def test_a_malformed_locality_raises_LocalityError_and_does_not_exit(self):
        for bad in ("(0, 1)", [1, -1], [True, 0], [1, 2, 3], [1], None or 7, 1.0):
            with self.subTest(bad=bad):
                with self.assertRaises(codebook.LocalityError):
                    codebook.normalize_locality(bad)
        with self.assertRaises(codebook.LocalityError):
            assertion("human", "batch-1", locality="(0, 1)")


class TestExpectedTier(unittest.TestCase):
    """A1 + ADDENDUM-4: a tier exists only when EVERY assertion is llm-class,
    and corroboration is counted on the scoreable lanes ONLY."""

    def test_an_empty_stack_has_no_tier(self):
        self.assertIsNone(codebook.expected_tier([]))

    def test_one_scoreable_run_is_provisional(self):
        self.assertEqual(codebook.expected_tier(
            [assertion("llm", "run1", original_lane="free", effective_lane="codebook")]),
            "provisional")

    def test_two_distinct_scoreable_runs_are_corroborated(self):
        self.assertEqual(codebook.expected_tier([
            assertion("llm", "run1", original_lane="free", effective_lane="codebook"),
            assertion("llm", "run2", original_lane="free",
                      effective_lane="codebook-grammar")]),
            "corroborated")

    def test_the_free_lane_is_discovery_and_never_scores(self):
        """The whole point of SCOREABLE_LANES. Two free-lane runs agreeing is
        not agreement."""
        self.assertEqual(codebook.expected_tier([
            assertion("llm", "run1", original_lane="free", effective_lane="free"),
            assertion("llm", "run2", original_lane="free", effective_lane="free")]),
            "provisional")

    def test_any_full_weight_assertion_removes_the_tier_entirely(self):
        for full in (assertion("human", "batch-1"),
                     assertion("rule-derived", "det-patterns-v2:3")):
            with self.subTest(cls=full["class"]):
                self.assertIsNone(codebook.expected_tier(
                    [assertion("llm", "run1", original_lane="free",
                               effective_lane="codebook"), full]))


class TestMergeAssertion(unittest.TestCase):

    def setUp(self):
        self.entry = {"status": "active"}

    def test_a_new_member_is_created_and_inserted_in_oracle_id_order(self):
        self.assertEqual(codebook.merge_assertion(
            self.entry, OID[3], assertion("human", "batch-1")), "created")
        self.assertEqual(codebook.merge_assertion(
            self.entry, OID[1], assertion("human", "batch-1")), "created")
        self.assertEqual(codebook.member_ids(self.entry), [OID[1], OID[3]])
        self.assertEqual(codebook.member_id_set(self.entry), {OID[1], OID[3]})
        self.assertIs(codebook.member_by_id(self.entry, OID[1]),
                      self.entry["members"][0])
        self.assertIsNone(codebook.member_by_id(self.entry, OID[5]))

    def test_a_second_support_event_merges_and_sorts_by_class_source_ref(self):
        codebook.merge_assertion(self.entry, OID[1],
                                 assertion("llm", "run2", original_lane="free",
                                           effective_lane="codebook"))
        self.assertEqual(codebook.merge_assertion(
            self.entry, OID[1], assertion("llm", "run1", original_lane="free",
                                          effective_lane="codebook")), "merged")
        member = self.entry["members"][0]
        self.assertEqual([a["source_ref"] for a in member["assertions"]],
                         ["run1", "run2"])
        self.assertEqual(member["tier"], "corroborated")
        self.assertEqual(list(member), ["oracle_id", "tier", "assertions"])

    def test_a_human_assertion_joining_removes_the_tier(self):
        codebook.merge_assertion(self.entry, OID[1],
                                 assertion("llm", "run1", original_lane="free",
                                           effective_lane="codebook"))
        self.assertEqual(self.entry["members"][0]["tier"], "provisional")
        codebook.merge_assertion(self.entry, OID[1], assertion("human", "batch-2"))
        self.assertNotIn("tier", self.entry["members"][0])
        self.assertEqual(list(self.entry["members"][0]), ["oracle_id", "assertions"])

    def test_an_invalid_oracle_id_raises_InvalidOracleIdError(self):
        # `_UUID_RE` is `[0-9a-f]`, so UPPERCASE hex is a real rejection — and
        # the digits-only OIDs above cannot demonstrate it, since `.upper()`
        # leaves them unchanged. That near-miss is why the case is spelled out.
        upper_hex = "ABCDEF01-0000-4000-8000-000000000001"
        for bad in ("not-a-uuid", "", None, upper_hex, OID[1] + "0"):
            with self.subTest(bad=bad):
                with self.assertRaises(codebook.InvalidOracleIdError):
                    codebook.merge_assertion(self.entry, bad,
                                             assertion("human", "batch-1"))

    def test_a_duplicate_support_event_raises_and_writes_nothing(self):
        codebook.merge_assertion(self.entry, OID[1], assertion("human", "batch-1"))
        before = copy.deepcopy(self.entry)
        with self.assertRaises(codebook.DuplicateAssertionError):
            codebook.merge_assertion(self.entry, OID[1],
                                     assertion("human", "batch-1", quote="other"))
        self.assertEqual(self.entry, before)


class TestRemoveDetAssertions(unittest.TestCase):
    """A8: a DET refresh replaces ITS OWN assertion set and nothing else."""

    def setUp(self):
        self.entry = {"status": "active"}
        codebook.merge_assertion(self.entry, OID[0],
                                 assertion("rule-derived", "det-patterns-v2:1"))
        codebook.merge_assertion(self.entry, OID[0], assertion("human", "batch-1"))
        codebook.merge_assertion(self.entry, OID[1],
                                 assertion("rule-derived", "det-patterns-v2:2"))
        codebook.merge_assertion(self.entry, OID[2],
                                 assertion("llm", "run1", original_lane="free",
                                           effective_lane="codebook"))

    def test_a_member_keeps_its_membership_while_any_proof_survives(self):
        result = codebook.remove_det_assertions(self.entry)
        self.assertEqual(result, {"assertions_removed": 2,
                                  "members_dropped": [OID[1]]})
        self.assertEqual(codebook.member_ids(self.entry), [OID[0], OID[2]])
        self.assertEqual([a["class"] for a in self.entry["members"][0]["assertions"]],
                         ["human"])

    def test_a_member_left_with_no_proof_is_dropped(self):
        codebook.remove_det_assertions(self.entry)
        self.assertNotIn(OID[1], codebook.member_id_set(self.entry))

    def test_the_tier_is_recomputed_on_every_surviving_member(self):
        codebook.remove_det_assertions(self.entry)
        llm_member = codebook.member_by_id(self.entry, OID[2])
        self.assertEqual(llm_member["tier"], "provisional")
        self.assertEqual(list(llm_member), ["oracle_id", "tier", "assertions"])

    def test_NEGATIVE_CONTROL_a_human_row_wearing_a_DET_source_ref_survives(self):
        """BOTH halves of the predicate are load-bearing. A human or llm row
        carrying a DET-looking `source_ref` is a provenance defect for lint to
        refuse, never a row for a DET refresh to delete — the CLASS is what says
        whose row it is. Widening the rule to the prefix alone would delete
        Captain-ratified evidence and still return a plausible count."""
        self.entry["members"].append({"oracle_id": OID[4], "assertions": [
            {"class": "human", "source_ref": "det-patterns-v2:5"},
            {"class": "llm", "source_ref": "det-patterns-v2:6"}]})
        self.entry["members"].sort(key=lambda m: m["oracle_id"])
        result = codebook.remove_det_assertions(self.entry)
        survivor = codebook.member_by_id(self.entry, OID[4])
        self.assertIsNotNone(survivor)
        self.assertEqual([a["class"] for a in survivor["assertions"]],
                         ["human", "llm"])
        self.assertEqual(result["assertions_removed"], 2)

    def test_a_narrower_prefix_removes_only_its_own_rows(self):
        result = codebook.remove_det_assertions(self.entry, "det-patterns-v2:2")
        self.assertEqual(result, {"assertions_removed": 1,
                                  "members_dropped": [OID[1]]})
        self.assertIn(OID[0], codebook.member_id_set(self.entry))


class TestTheStandingLint(unittest.TestCase):
    """R11 / A1, plus the accepted Worker-era hardening that travels with it.

    Every family below is asserted by the violation it must RAISE. A lint whose
    families are only exercised by clean documents is a lint nobody has watched
    fail."""

    def clean_entry(self):
        return {"status": "active", "members": [
            {"oracle_id": OID[1], "assertions": [
                {"class": "human", "source_ref": "batch-1", "quote": "t",
                 "corpus_ref": "2026-07-04", "evidence_status": "quoted"}]}]}

    def refuses(self, mutate):
        doc = document({"rule:a": self.clean_entry(), "rule:z": {"status": "active"}})
        mutate(doc)
        with self.assertRaises(codebook.LintError) as caught:
            codebook.lint(doc, "L")
        return str(caught.exception)

    def test_a_clean_document_returns_the_stats_dict(self):
        stats = codebook.lint(document({"rule:a": self.clean_entry()}), "L")
        self.assertEqual(stats, {"axes": 1, "members": 1, "assertions": 1,
                                 "exemptions_applied": []})

    def test_the_schema_and_axes_shape(self):
        self.assertIn("top-level schema is", self.refuses(
            lambda d: d.__setitem__("schema", "foundry-codebook/9")))
        with self.assertRaises(codebook.LintError):
            codebook.lint({"schema": codebook.SCHEMA_V2, "axes": []}, "L")

    def test_a_v1_member_field_on_a_v2_entry(self):
        self.assertIn("member_oracle_ids", self.refuses(
            lambda d: d["axes"]["rule:a"].__setitem__("member_oracle_ids", [])))

    def test_the_axis_status_and_pointer_hardening(self):
        """Standing hardening (F4), preserved verbatim — a status typo silently
        removes an axis from every status-partitioned consumer with no error
        raised anywhere."""
        cases = {
            "status 'actve' not in":
                lambda d: d["axes"]["rule:a"].__setitem__("status", "actve"),
            "status is 'renamed' but renamed_to is unset":
                lambda d: d["axes"]["rule:a"].__setitem__("status", "renamed"),
            "status is 'merged' but merged_into is unset":
                lambda d: d["axes"]["rule:a"].__setitem__("status", "merged"),
            "a stale":
                lambda d: d["axes"]["rule:a"].__setitem__("merged_into", "rule:z"),
            "names an axis that does not exist":
                lambda d: d["axes"]["rule:a"].update(
                    {"status": "merged", "merged_into": "rule:nope"}),
        }
        for fragment, mutate in cases.items():
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.refuses(mutate))

    def test_the_member_shape_family(self):
        cases = [
            ("'members' is dict, expected list",
             lambda d: d["axes"]["rule:a"].__setitem__("members", {})),
            ("a member is str, expected object",
             lambda d: d["axes"]["rule:a"]["members"].append("bare")),
            ("is not a valid uuid shape",
             lambda d: d["axes"]["rule:a"]["members"][0].__setitem__(
                 "oracle_id", "not-a-uuid")),
            ("are not in canonical order",
             lambda d: d["axes"]["rule:a"]["members"].__setitem__(0, {
                 "assertions": d["axes"]["rule:a"]["members"][0]["assertions"],
                 "oracle_id": OID[1]})),
            ("a member with no proof is not a member",
             lambda d: d["axes"]["rule:a"]["members"][0].__setitem__("assertions", [])),
            ("members are not sorted by oracle_id",
             lambda d: d["axes"]["rule:a"]["members"].insert(0, {
                 "oracle_id": OID[5], "assertions": [
                     {"class": "human", "source_ref": "batch-1", "quote": "t",
                      "corpus_ref": "2026-07-04", "evidence_status": "quoted"}]})),
            ("duplicate member oracle_id(s)",
             lambda d: d["axes"]["rule:a"]["members"].append({
                 "oracle_id": OID[1], "assertions": [
                     {"class": "human", "source_ref": "batch-1", "quote": "t",
                      "corpus_ref": "2026-07-04", "evidence_status": "quoted"}]})),
        ]
        for fragment, mutate in cases:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.refuses(mutate))

    def test_the_provenance_family_including_F4_hardening(self):
        def first(d):
            return d["axes"]["rule:a"]["members"][0]["assertions"][0]
        cases = [
            ("assertion class 'wizard' not in",
             lambda d: first(d).__setitem__("class", "wizard")),
            ("is outside the ratified vocabulary",
             lambda d: first(d).__setitem__("source_ref", "vibes")),
            # F4: without this, class=human/source_ref=det-patterns-v2:3 lints
            # clean, which is exactly the provenance mislabelling the schema
            # exists to prevent.
            ("may not cite source_ref",
             lambda d: first(d).__setitem__("source_ref", "det-patterns-v2:3")),
            ("may not cite source_ref",
             lambda d: first(d).update({"class": "rule-derived",
                                        "source_ref": "batch-1"})),
            ("duplicate assertion (class=",
             lambda d: d["axes"]["rule:a"]["members"][0]["assertions"].append(
                 dict(first(d)))),
            ("carries unknown key(s)",
             lambda d: first(d).__setitem__("vibes", 1)),
            ("evidence_status 'vibes' not in",
             lambda d: first(d).__setitem__("evidence_status", "vibes")),
            ("is missing corpus_ref", lambda d: first(d).pop("corpus_ref")),
            ("is not a YYYY-MM-DD snapshot",
             lambda d: first(d).__setitem__("corpus_ref", "yesterday-ish")),
            ("quote is int, expected string",
             lambda d: first(d).__setitem__("quote", 7)),
            ("empty quote without the legacy-captain-seed exemption (A3)",
             lambda d: first(d).__setitem__("quote", "   ")),
            ("but a quote is",
             lambda d: first(d).__setitem__("evidence_status",
                                            "legacy-captain-seed")),
        ]
        for fragment, mutate in cases:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.refuses(mutate))

    def test_the_lane_family(self):
        def first(d):
            return d["axes"]["rule:a"]["members"][0]["assertions"][0]
        cases = [
            ("not in ('codebook', 'codebook-grammar', 'free')",
             lambda d: first(d).update({"class": "llm", "source_ref": "run1",
                                        "original_lane": "nope",
                                        "effective_lane": "codebook"})),
            ("llm assertion is missing required original_lane",
             lambda d: first(d).update({"class": "llm", "source_ref": "run1"})),
            ("is llm-class only, found on 'human'",
             lambda d: first(d).__setitem__("original_lane", "codebook")),
            ("is llm-class only, found on 'human'",
             lambda d: first(d).__setitem__("promotion_reason", "x")),
        ]
        for fragment, mutate in cases:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.refuses(mutate))

    def test_the_locality_family(self):
        def first(d):
            return d["axes"]["rule:a"]["members"][0]["assertions"][0]
        for bad in ([1, -1], [True, 1], [1, 2, 3], "(0,1)"):
            with self.subTest(bad=bad):
                self.assertIn("pair of non-negative integers",
                              self.refuses(lambda d, b=bad: first(d).__setitem__(
                                  "locality", b)))
        # An address is DERIVED from the quote, so a quoteless assertion cannot
        # own one (sec.11 / A2).
        self.assertIn("carries a locality address but no quote", self.refuses(
            lambda d: first(d).update({"quote": "",
                                       "evidence_status": "legacy-captain-seed",
                                       "locality": [0, 0]})))

    def test_the_ordering_and_tier_family(self):
        def member(d):
            return d["axes"]["rule:a"]["members"][0]
        llm = {"class": "llm", "source_ref": "run%d", "original_lane": "free",
               "effective_lane": "codebook", "quote": "t",
               "corpus_ref": "2026-07-04", "evidence_status": "quoted"}

        def unsorted(d):
            member(d)["assertions"] = [dict(llm, source_ref="run2"),
                                       dict(llm, source_ref="run1")]
            member(d)["tier"] = "corroborated"
        self.assertIn("assertions are not sorted by (class, source_ref)",
                      self.refuses(unsorted))
        self.assertIn("tier 'shiny' not in",
                      self.refuses(lambda d: member(d).__setitem__("tier", "shiny")))
        self.assertIn("but the assertion stack supports",
                      self.refuses(lambda d: member(d).__setitem__(
                          "tier", "corroborated")))

    def test_every_violation_is_reported_in_one_raise_not_one_per_run(self):
        doc = document({"rule:x%02d" % i: {"status": "actve"} for i in range(5)})
        with self.assertRaises(codebook.LintError) as caught:
            codebook.lint(doc, "L")
        self.assertIn("5 lint violation(s)", str(caught.exception))
        self.assertEqual(str(caught.exception).count("not in ('active',"), 5)

    def test_the_fifty_item_truncation_and_its_tail_wording(self):
        doc = document({"rule:x%02d" % i: {"status": "actve"} for i in range(60)})
        with self.assertRaises(codebook.LintError) as caught:
            codebook.lint(doc, "T")
        message = str(caught.exception)
        self.assertIn("T: 60 lint violation(s):", message)
        self.assertTrue(message.endswith("  ... and 10 more"), message[-40:])
        self.assertEqual(message.count("rule:x"), 50)

    def test_A14_a_violation_never_names_the_evidence_text(self):
        """Quote-blind by ratified rule. A lint that echoed the quote would put
        evidence text into every console and every CI log."""
        secret = "ZZQUOTEWITNESSZZ"
        doc = document({"rule:a": {"status": "active", "members": [
            {"oracle_id": OID[1], "tier": "corroborated", "assertions": [
                {"class": "human", "source_ref": "batch-1", "quote": secret,
                 "corpus_ref": "nope", "evidence_status": "vibes"}]}]}})
        with self.assertRaises(codebook.LintError) as caught:
            codebook.lint(doc, "A14")
        message = str(caught.exception)
        self.assertNotIn(secret, message)
        # …and it did find the three real defects, so the absence is not because
        # nothing was checked.
        self.assertIn("3 lint violation(s)", message)


# ===========================================================================
# 3. THE LEGACY FACADE
# ===========================================================================

class TestTheFacadeHoldsNoSemanticImplementation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fcb = load_legacy("foundry_codebook")
        cls.tree = ast.parse(inspect.getsource(cls.fcb))
        cls.functions = {n.name: n for n in cls.tree.body
                         if isinstance(n, ast.FunctionDef)}

    def test_every_direct_alias_is_the_permanent_object_itself(self):
        for name in DIRECT_ALIASES:
            with self.subTest(name=name):
                self.assertIs(getattr(self.fcb, name), getattr(codebook, name))

    def test_LintError_identity_is_preserved_for_except_clauses(self):
        """Three consumers write `except fcb.LintError`. A legacy subclass would
        keep those working and silently break `except codebook.LintError`, so
        identity — not compatibility — is the assertion."""
        self.assertIs(self.fcb.LintError, codebook.LintError)

    def test_no_aliased_name_is_locally_defined(self):
        """A migrated name that came back as a `def` or a `class` would be a
        second implementation wearing the alias's name."""
        for name in DIRECT_ALIASES:
            with self.subTest(name=name):
                self.assertNotIn(name, self.functions)
                self.assertNotIn(name, {n.name for n in self.tree.body
                                        if isinstance(n, ast.ClassDef)})

    def test_each_alias_is_bound_by_a_bare_attribute_read(self):
        bindings = {}
        for node in self.tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                    and isinstance(node.targets[0], ast.Name):
                bindings[node.targets[0].id] = node.value
        for name in DIRECT_ALIASES:
            with self.subTest(name=name):
                value = bindings.get(name)
                self.assertIsInstance(value, ast.Attribute)
                self.assertEqual(ast.unparse(value), f"_codebook.{name}")

    def test_the_migrated_semantic_definitions_are_gone_from_the_facade(self):
        """The regexes and tables specifically: a surviving `re.compile` for a
        migrated vocabulary is the duplication this slice forbids."""
        source = inspect.getsource(self.fcb)
        for gone in ('re.compile(r"^[0-9a-f]{8}', 'SOURCE_REF_FAMILIES = {',
                     'CLASSES = ("human"', 'ASSERTION_KEY_ORDER = (',
                     'class LintError'):
            with self.subTest(gone=gone):
                self.assertNotIn(gone, source)


class TestTheThreeTranslationWrappers(unittest.TestCase):
    """Exactly three, and each one may translate — never decide."""

    @classmethod
    def setUpClass(cls):
        cls.fcb = load_legacy("foundry_codebook")
        cls.tree = ast.parse(inspect.getsource(cls.fcb))
        cls.functions = {n.name: n for n in cls.tree.body
                         if isinstance(n, ast.FunctionDef)}

    def test_exactly_the_three_contracted_wrappers_exist(self):
        defined_semantics = [name for name in self.functions
                             if name in set(WRAPPERS) | set(DIRECT_ALIASES)]
        self.assertEqual(sorted(defined_semantics), sorted(WRAPPERS))

    def test_a_wrapper_calls_only_its_own_permanent_counterpart(self):
        for name in WRAPPERS:
            with self.subTest(name=name):
                calls = [ast.unparse(n.func) for n in ast.walk(self.functions[name])
                         if isinstance(n, ast.Call)]
                self.assertEqual(sorted(calls),
                                 sorted([f"_codebook.{name}", "fc.halt", "str"]))

    def test_a_wrapper_catches_exactly_its_contracted_errors(self):
        for name, expected in WRAPPERS.items():
            with self.subTest(name=name):
                caught = []
                for node in ast.walk(self.functions[name]):
                    if isinstance(node, ast.ExceptHandler):
                        text = ast.unparse(node.type)
                        caught += [t.strip().replace("_codebook.", "")
                                   for t in text.strip("()").split(",")]
                self.assertEqual(sorted(caught), sorted(expected))

    def test_a_wrapper_body_is_translation_and_nothing_else(self):
        """Structural: the body is one `try`, the try block is a single return of
        the permanent call, and every handler is a single `fc.halt(str(error))`.
        No branch, no comparison, no literal container, no subscript — a wrapper
        that grew any of those would be re-deciding something the model decides."""
        forbidden = (ast.If, ast.For, ast.While, ast.Compare, ast.BinOp,
                     ast.BoolOp, ast.Dict, ast.List, ast.Subscript, ast.Assign,
                     ast.Raise, ast.ListComp, ast.DictComp, ast.Lambda)
        for name, expected in WRAPPERS.items():
            with self.subTest(name=name):
                fn = self.functions[name]
                body = [n for n in fn.body if not (
                    isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
                self.assertEqual(len(body), 1)
                self.assertIsInstance(body[0], ast.Try)
                trunk = body[0]
                self.assertEqual(len(trunk.body), 1)
                self.assertIsInstance(trunk.body[0], ast.Return)
                self.assertEqual(len(trunk.handlers), 1)
                self.assertEqual(len(trunk.handlers[0].body), 1)
                self.assertEqual(ast.unparse(trunk.handlers[0].body[0]),
                                 "fc.halt(str(error))")
                for node in ast.walk(fn):
                    self.assertNotIsInstance(node, forbidden)

    def test_each_wrapper_keeps_its_exact_legacy_signature(self):
        """Parameter NAMES, ORDER and DEFAULTS, not the annotation objects: the
        permanent module carries `from __future__ import annotations` and the
        legacy one does not, so the same annotation is a string in one and a
        type in the other. Comparing the raw `Parameter` objects would compare
        that difference and call a correct wrapper broken."""
        def shape(fn):
            return [(name, p.kind, p.default) for name, p
                    in inspect.signature(fn).parameters.items()]
        for name in WRAPPERS:
            with self.subTest(name=name):
                self.assertEqual(shape(getattr(self.fcb, name)),
                                 shape(getattr(codebook, name)))


class TestLegacyFailureParity(unittest.TestCase):
    """The permanent library raises; the facade must still end the process with
    the byte-identical stderr line every legacy caller and control expects.

    The expected message is DERIVED from the permanent error rather than typed
    out, so this asserts the translation rather than re-stating the prose — and
    a message change in one place cannot pass by being copied into two."""

    @classmethod
    def setUpClass(cls):
        cls.fcb = load_legacy("foundry_codebook")

    def halts_like(self, permanent, legacy, expected_error):
        with self.assertRaises(expected_error) as raised:
            permanent()
        buffer = io.StringIO()
        with contextlib.redirect_stderr(buffer):
            with self.assertRaises(SystemExit) as exited:
                legacy()
        self.assertEqual(exited.exception.code, 1)
        self.assertEqual(buffer.getvalue(), f"STOP — {raised.exception}\n")

    def test_normalize_locality(self):
        self.halts_like(lambda: codebook.normalize_locality("(0, 1)"),
                        lambda: self.fcb.normalize_locality("(0, 1)"),
                        codebook.LocalityError)

    def test_build_assertion_SC8_the_foundry_locality_fixture(self):
        """`foundry_locality.schema_fixtures()` SC8 calls exactly this and
        requires SystemExit. A bare alias would have turned a green ratified
        control red while the library was behaving correctly — which is why
        these three are wrappers and not aliases."""
        self.halts_like(
            lambda: codebook.build_assertion("human", "batch-1", "q",
                                             "2026-07-04", locality="(0, 1)"),
            lambda: self.fcb.build_assertion("human", "batch-1", "q",
                                             "2026-07-04", locality="(0, 1)"),
            codebook.LocalityError)

    def test_merge_assertion_invalid_oracle_id(self):
        self.halts_like(
            lambda: codebook.merge_assertion(
                {"status": "active"}, "not-a-uuid",
                codebook.build_assertion("human", "batch-1", "q", "2026-07-04")),
            lambda: self.fcb.merge_assertion(
                {"status": "active"}, "not-a-uuid",
                self.fcb.build_assertion("human", "batch-1", "q", "2026-07-04")),
            codebook.InvalidOracleIdError)

    def test_merge_assertion_duplicate_support_event(self):
        def build(module):
            entry = {"status": "active"}
            module.merge_assertion(entry, OID[1], module.build_assertion(
                "human", "batch-1", "q", "2026-07-04"))
            return lambda: module.merge_assertion(entry, OID[1], module.build_assertion(
                "human", "batch-1", "z", "2026-07-04"))
        self.halts_like(build(codebook), build(self.fcb),
                        codebook.DuplicateAssertionError)

    def test_lint_still_raises_rather_than_halting_at_the_facade(self):
        """`lint` is an ALIAS, not a wrapper: its failure behaviour never ended
        the process. `lint_or_halt` is the legacy translation boundary and is
        deferred, unchanged, by C8.5M amendment 1."""
        with self.assertRaises(self.fcb.LintError):
            self.fcb.lint({"schema": "wrong", "axes": {}}, "L")
        buffer = io.StringIO()
        with contextlib.redirect_stderr(buffer):
            with self.assertRaises(SystemExit):
                self.fcb.lint_or_halt({"schema": "wrong", "axes": {}}, "L")
        self.assertTrue(buffer.getvalue().startswith("STOP — "))


class TestTheDeferredLegacyBoundariesAreUntouched(unittest.TestCase):
    """C8.5M amendment 1. These still exist, still live in the legacy file, and
    are explicitly NOT part of this slice — their presence is the intended
    transitional boundary, not leftover duplication."""

    @classmethod
    def setUpClass(cls):
        cls.fcb = load_legacy("foundry_codebook")
        cls.functions = {n.name for n in ast.parse(
            inspect.getsource(cls.fcb)).body if isinstance(n, ast.FunctionDef)}

    def test_the_deferred_surfaces_are_still_legacy_definitions(self):
        for name in ("corpus_ref_current", "load_codebook", "lint_or_halt",
                     "_serialize", "sha256_of", "write_codebook_atomic",
                     "backup_codebook", "cmd_add_member", "cmd_lint", "main"):
            with self.subTest(name=name):
                self.assertIn(name, self.functions)

    def test_the_paths_and_bootstrap_are_still_legacy(self):
        for name in ("CODEBOOK_PATH", "BACKUPS_DIR", "LATEST_ARTIFACT_PATH",
                     "_BOOTSTRAP_ROOT"):
            with self.subTest(name=name):
                self.assertTrue(hasattr(self.fcb, name))
        self.assertFalse(hasattr(codebook, "CODEBOOK_PATH"))

    def test_the_permanent_module_learned_none_of_it(self):
        for name in ("corpus_ref_current", "load_codebook", "lint_or_halt",
                     "_serialize", "sha256_of", "write_codebook_atomic",
                     "backup_codebook", "main"):
            with self.subTest(name=name):
                self.assertFalse(hasattr(codebook, name))


if __name__ == "__main__":
    unittest.main()
