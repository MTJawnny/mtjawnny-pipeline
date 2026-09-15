"""S10 — `foundry_common` dissolution: the lifted card-text owners, their
facades, the S7 call-time substitution law, and the caller topology.

WHAT S10 MOVED, AND WHERE
-------------------------
* `full_oracle_text`                         -> `mtj_foundry.corpus`
* DET-compatible self-reference contract     -> `mtj_foundry.oracle_text`
  (`DET_CARDNAME_TOKEN`, `det_self_name_candidates`,
  `det_canonicalize_self_reference`) — a SEPARATE contract from neutral N2
* neutral modal / roll / results-row / Level-Class recognition
                                             -> `mtj_foundry.oracle_text`

`det_scan_texts` / `expand_modal_bullets` (DET synthetic representation) did NOT
move: they stay a declared legacy composition boundary in `foundry_common` and
now CONSUME the owners. Delivery/grouping consequences stay in
`mtj_foundry.mtg.shapes.delivery`.

THE FOUR THINGS PROVED HERE
---------------------------
1. **The owners' contracts**, on fixtures chosen to go red under the S10
   falsification catalog (root-only text, face order, join separator, N2 standing
   in for DET, pawprint/Spree/modal, die rows, Level/Class markers).
2. **Conservation over the selected corpus.** Every digest below was MEASURED
   FROM THE LEGACY `foundry_common` IMPLEMENTATIONS at accepted base
   `a77e679f561f96959824b5fcea4be03dfcdaaa35` by running `corpus_digests` with the
   legacy callables, then pinned. The same function over the permanent owners must
   reproduce them. Skips without the gitignored corpus; FAILS if a corpus is
   present but is not the selected content.
3. **The S7 law.** A run-time replacement of the permanent self-reference owner,
   made AFTER the shells have installed their providers, reaches delivery,
   locality and the DET scan text. A provider that CAPTURED the owner function
   instead is shown not to — the check detects capture, it does not just pass.
4. **Topology.** The live `foundry_common` caller set, recomputed from
   `git ls-files` + AST, is exactly the reviewed one, the archive importer is not
   counted as live, and every retired name has no live reference.
"""

from __future__ import annotations

import ast
import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT, SRC

from mtj_foundry import corpus, oracle_text
from mtj_foundry.paths import ProjectPaths

EXPERIMENTS = REPO_ROOT / "experiments"
PROVIDER = EXPERIMENTS / "foundry_common.py"
CORPUS_FILE = ProjectPaths.for_root(REPO_ROOT).legacy_oracle_cards

# The decompressed-content identity of the selected corpus. The container digest
# is deliberately not pinned here: two gzip containers of these exact bytes that
# differ only in the header MTIME field are both in use (see
# `refoundation/path-e/input-lock.json`), and every observable below is a
# function of the decompressed records.
SELECTED_CONTENT_SHA256 = "5e47e1325a3987db745a941307080830696cbac2f6aa80d8f88f8a6dad90723c"


def _ensure_experiments_on_path() -> None:
    if str(EXPERIMENTS) not in sys.path:
        sys.path.insert(0, str(EXPERIMENTS))


# ===========================================================================
# 1. owner contracts
# ===========================================================================

TRANSFORM = {
    "name": "Front // Back", "oracle_text": "",
    "card_faces": [
        {"name": "Front", "oracle_text": "When Front enters, draw a card.",
         "type_line": "Creature"},
        {"name": "Back", "oracle_text": "", "type_line": "Creature"},
        {"name": "Back", "oracle_text": "Back can't be blocked.",
         "type_line": "Creature"},
    ],
}


class TestFullOracleTextOwner(unittest.TestCase):

    def test_all_faces_in_order_single_newline_empty_faces_skipped(self):
        self.assertEqual(corpus.full_oracle_text(TRANSFORM),
                         "When Front enters, draw a card.\nBack can't be blocked.")

    def test_single_face_reads_the_root_field_through_card_faces(self):
        self.assertEqual(corpus.full_oracle_text({"name": "X", "oracle_text": "Flying"}),
                         "Flying")

    def test_no_text_anywhere_is_the_empty_string(self):
        self.assertEqual(corpus.full_oracle_text({"name": "X"}), "")
        self.assertEqual(corpus.full_oracle_text(
            {"name": "X // Y", "card_faces": [{"name": "X"}, {"name": "Y"}]}), "")

    def test_it_reads_faces_through_the_owner_at_call_time(self):
        real = corpus.card_faces
        corpus.card_faces = lambda card: [{"oracle_text": "a"}, {"oracle_text": "b"}]
        try:
            self.assertEqual(corpus.full_oracle_text({}), "a\nb")
        finally:
            corpus.card_faces = real


LEGENDARY_SUBTITLE = {"name": "Sharuum the Hegemon",
                      "type_line": "Legendary Artifact Creature — Sphinx"}
NONLEGENDARY_OF = {"name": "Destroy the Evidence", "type_line": "Sorcery"}


class TestDetSelfReferenceContract(unittest.TestCase):

    def test_token(self):
        self.assertEqual(oracle_text.DET_CARDNAME_TOKEN, "~")

    def test_cr_201_5c_legendary_subtitle_short_name(self):
        self.assertEqual(
            oracle_text.det_canonicalize_self_reference(
                "When Sharuum enters, return target artifact card.", LEGENDARY_SUBTITLE),
            "When ~ enters, return target artifact card.")

    def test_subtitle_short_name_is_legendary_only(self):
        self.assertEqual(
            oracle_text.det_canonicalize_self_reference(
                "Destroy target land.", NONLEGENDARY_OF),
            "Destroy target land.")

    def test_comma_short_form_alchemy_base_and_faces(self):
        card = {"name": "A-Willie Lumpkin, Postman", "type_line": "Creature"}
        self.assertEqual(oracle_text.det_self_name_candidates(card),
                         ["Willie Lumpkin, Postman", "Willie Lumpkin"])
        self.assertEqual(oracle_text.det_canonicalize_self_reference(
            "Willie Lumpkin, Postman attacks. Willie Lumpkin draws.", card),
            "~ attacks. ~ draws.")
        self.assertEqual(sorted(oracle_text.det_self_name_candidates(TRANSFORM)),
                         ["Back", "Front"])

    def test_it_is_NOT_neutral_N2(self):
        """The witness pair for "ownership consolidation is not semantic
        consolidation": N2 keeps a keyword-action verb literal and knows no
        CR 201.5c short form; the DET contract does the opposite on both."""
        regenerate = {"name": "Regenerate", "type_line": "Instant",
                      "keywords": ["Regenerate"]}
        text = "Regenerate target creature."
        self.assertEqual(oracle_text.normalize_self_references(
            text, oracle_text.self_name_candidates("Regenerate"), ["Regenerate"]), text)
        self.assertEqual(oracle_text.det_canonicalize_self_reference(text, regenerate),
                         "~ target creature.")
        sharuum = "When Sharuum enters, return target artifact card."
        self.assertEqual(oracle_text.normalize_self_references(
            sharuum, oracle_text.self_name_candidates("Sharuum the Hegemon")), sharuum)

    def test_longest_candidate_first(self):
        card = {"name": "Rosie Cotton of South Lane", "type_line": "Legendary Creature"}
        self.assertEqual(oracle_text.det_canonicalize_self_reference(
            "Rosie Cotton of South Lane and Rosie Cotton", card), "~ and ~")


class TestNeutralStructureRecognition(unittest.TestCase):

    def test_mode_lines_bullet_pawprint_spree(self):
        for line in ("• Destroy target creature.", "  • indented bullet",
                     "{P} — Draw a card.", "{P}{P}{P} — Each opponent loses 3 life.",
                     "+ {2}{B} — Destroy target creature.",
                     "• Galian Beast — {0} — 3/2."):
            with self.subTest(line=line):
                self.assertTrue(oracle_text.is_mode_line(line))
        for line in ("Destroy target creature.", "{P}: Draw a card.",
                     "+1: Draw a card.", "9+ | Flying"):
            with self.subTest(line=line):
                self.assertFalse(oracle_text.is_mode_line(line))

    def test_modal_header_needs_a_number_not_an_em_dash(self):
        for text in ("Choose one —", "Choose three. You may choose the same mode more than once.",
                     "An opponent chooses one —", "choose up to that many.",
                     "Choose X —", "Choose any number —"):
            with self.subTest(text=text):
                self.assertTrue(oracle_text.is_modal_header(text))
        for text in ("As this enchantment enters, choose Khans or Dragons.",
                     "Choose a creature type."):
            with self.subTest(text=text):
                self.assertFalse(oracle_text.is_modal_header(text))

    def test_roll_instruction(self):
        for text in ("Roll a d20.", "roll two six-sided dice", "rolls a die"):
            with self.subTest(text=text):
                self.assertTrue(oracle_text.is_roll_instruction(text))
        self.assertFalse(oracle_text.is_roll_instruction("Whenever you roll, draw."))

    def test_die_rows_every_printed_form(self):
        for line in ("1—9 | A", "1-9 | A", "10–19 | A", "20 | A", "10+ | A",
                     "9 or less | A"):
            with self.subTest(line=line):
                self.assertTrue(oracle_text.is_die_row(line))
                self.assertTrue(oracle_text.is_die_result_row(line))
        self.assertFalse(oracle_text.is_die_row("• 2 — menace"))
        self.assertTrue(oracle_text.is_die_result_row("• 2 — menace"))
        self.assertFalse(oracle_text.is_die_row("Draw a card | discard"))

    def test_level_and_class_striation_markers(self):
        self.assertTrue(oracle_text.is_level_band("LEVEL 2-6"))
        self.assertTrue(oracle_text.is_level_band("LEVEL 7+"))
        self.assertFalse(oracle_text.is_level_band("Level up {W}"))
        self.assertTrue(oracle_text.is_class_level_bar("{1}{R}: Level 2"))
        self.assertFalse(oracle_text.is_class_level_bar("{1}{R}: Draw a card."))
        self.assertFalse(oracle_text.is_level_band("  LEVEL 2-6"))
        self.assertTrue(oracle_text.is_striation_marker("  LEVEL 2-6  "))
        self.assertTrue(oracle_text.is_striation_marker("{2}{R}: Level 3"))
        self.assertFalse(oracle_text.is_striation_marker(
            "Whenever you roll one or more dice, target creature gets +2/+0."))


class TestTheOwnersStayPermanent(unittest.TestCase):
    """No legacy import, no process behaviour, no root derivation, importable
    with nothing but `src` on the path from an unrelated working directory."""

    OWNERS = (SRC / "mtj_foundry" / "corpus.py", SRC / "mtj_foundry" / "oracle_text.py")

    def test_no_experiments_import_no_sys_path_no_root(self):
        for path in self.OWNERS:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            with self.subTest(module=path.name):
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        names = ([a.name for a in node.names] if isinstance(node, ast.Import)
                                 else [node.module or ""])
                        for name in names:
                            self.assertIn(name.split(".")[0],
                                          sys.stdlib_module_names | {"__future__"},
                                          f"{path.name} imports {name}")
                    if isinstance(node, ast.Name):
                        self.assertNotIn(node.id, {"__file__"}, path.name)
                    if isinstance(node, ast.Attribute):
                        self.assertNotIn(node.attr, {"parents", "cwd", "path"},
                                         f"{path.name} uses .{node.attr}")

    def test_import_and_call_with_only_src_on_the_path(self):
        code = ("from mtj_foundry import corpus, oracle_text as o\n"
                "c = {'name': 'Sharuum the Hegemon', 'type_line': 'Legendary Creature',"
                " 'oracle_text': 'When Sharuum enters, choose one —\\n• a'}\n"
                "t = corpus.full_oracle_text(c)\n"
                "print(o.det_canonicalize_self_reference(t, c).split(chr(10))[0],"
                " o.is_mode_line('• a'), o.is_modal_header(t))\n"
                "import sys; assert not any('experiments' in m for m in sys.modules)\n")
        with tempfile.TemporaryDirectory() as tmp:
            res = subprocess.run([sys.executable, "-c", code], cwd=tmp,
                                 capture_output=True, text=True,
                                 env={"PYTHONPATH": str(SRC), "PATH": "/usr/bin:/bin"})
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(res.stdout.strip(), "When ~ enters, choose one — True True")


# ===========================================================================
# 2. the legacy boundary is facades, not definitions
# ===========================================================================

RETIRED = ("_is_die_row", "_is_legendary")
FUNCTION_FACADES = {
    "full_oracle_text": (corpus, "full_oracle_text", ({"name": "X"},)),
    "gate_passes": (corpus, "is_gate0_eligible", ({"legalities": {}},)),
    "canonicalize_self_reference": (oracle_text, "det_canonicalize_self_reference",
                                    ("t", {"name": "X"})),
    "is_mode_line": (oracle_text, "is_mode_line", ("• x",)),
    "_is_band_marker": (oracle_text, "is_striation_marker", ("LEVEL 1+",)),
    "_cardname_candidates": (oracle_text, "det_self_name_candidates", ({"name": "X"},)),
}
ALIASES = {"CARDNAME_TOKEN": "DET_CARDNAME_TOKEN", "_MODAL_HEADER_RE": "MODAL_HEADER_RE",
           "_DIE_ROW_RE": "DIE_ROW_RE", "_ROLL_INSTRUCTION_RE": "ROLL_INSTRUCTION_RE",
           "_LEVEL_BAND_RE": "LEVEL_BAND_RE", "_CLASS_LEVEL_RE": "CLASS_LEVEL_RE"}


class TestTheLegacyBoundaryDelegates(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _ensure_experiments_on_path()
        import foundry_common
        cls.fc = foundry_common
        cls.tree = ast.parse(PROVIDER.read_text(encoding="utf-8"))

    def test_aliases_are_the_owners_objects(self):
        for legacy, owner in ALIASES.items():
            with self.subTest(name=legacy):
                self.assertIs(getattr(self.fc, legacy), getattr(oracle_text, owner))

    def test_function_facades_resolve_the_owner_at_CALL_time(self):
        for legacy, (module, attr, args) in FUNCTION_FACADES.items():
            with self.subTest(name=legacy):
                real = getattr(module, attr)
                sentinel = object()
                setattr(module, attr, lambda *a, **k: sentinel)
                try:
                    self.assertIs(getattr(self.fc, legacy)(*args), sentinel)
                finally:
                    setattr(module, attr, real)

    def test_retired_names_are_gone(self):
        for name in RETIRED:
            with self.subTest(name=name):
                self.assertFalse(hasattr(self.fc, name))

    def test_no_second_definition_of_a_lifted_pattern(self):
        compiled = set()
        for node in self.tree.body:
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) \
                    and isinstance(node.value.func, ast.Attribute) \
                    and node.value.func.attr == "compile":
                compiled |= {t.id for t in node.targets if isinstance(t, ast.Name)}
        self.assertEqual(compiled, {"_CONDENSE_EFFECT_RE"},
                         "foundry_common compiles a pattern other than its own "
                         "prompt-condensation regex")

    def test_det_synthetic_composition_stayed_and_consumes_the_owners(self):
        card = {"name": "Zzyzx", "type_line": "Creature",
                "oracle_text": "When Zzyzx enters, choose one —\n• Zzyzx deals 1.\n• Draw.\n"
                               "Roll a d20.\n1-9 | Gain 1.\n10+ | Gain 2.\n"
                               "{1}{R}: Level 2\nZzyzx has haste."}
        self.assertEqual(self.fc.det_scan_texts(card), [
            "When ~ enters, choose one —\n• ~ deals 1.\n• Draw.\nRoll a d20.\n"
            "1-9 | Gain 1.\n10+ | Gain 2.\n{1}{R}: Level 2\n~ has haste.",
            "When ~ enters, choose one — • ~ deals 1.",
            "When ~ enters, choose one — • Draw.",
            "Roll a d20. 1-9 | Gain 1.",
            "Roll a d20. 10+ | Gain 2.",
            "{1}{R}: Level 2 ~ has haste.",
        ])


class TestRetainedLegacyCompositionContracts(unittest.TestCase):
    """What S10 deliberately LEFT in `foundry_common` still behaves exactly as
    before: the loose-script import precedence, Gate #0 filter-before-index, and
    exact-name resolution with its one sanctioned ambiguity rule. S10 changed
    none of these; they are pinned here because the S10 falsification catalog
    requires each to be shown able to go red."""

    @classmethod
    def setUpClass(cls):
        _ensure_experiments_on_path()
        import foundry_common
        cls.fc = foundry_common

    def test_loose_script_import_precedence(self):
        """A same-named module earlier on the caller's path must lose to the
        legacy sibling, and `mtj_foundry` must resolve to this repository's src."""
        with tempfile.TemporaryDirectory() as tmp:
            shadow = Path(tmp) / "shadow"
            shadow.mkdir()
            (shadow / "foundry_cr.py").write_text("SHADOW = True\n", encoding="utf-8")
            # the real contract: after the provider's bootstrap the legacy
            # sibling sits at index 0 and `src` directly behind it
            code = ("import sys\n"
                    f"sys.path.insert(0, {str(shadow)!r})\n"
                    f"sys.path.append({str(EXPERIMENTS)!r})\n"
                    "import foundry_common as fc\n"
                    "head = list(sys.path[:2])\n"
                    "import foundry_cr, mtj_foundry\n"
                    "print(head[0] == str(fc._PATHS.legacy_experiments),"
                    " head[1] == str(fc._PATHS.root / 'src'),"
                    " hasattr(foundry_cr, 'SHADOW'),"
                    " mtj_foundry.__file__.startswith(str(fc._PATHS.root / 'src')))\n")
            res = subprocess.run([sys.executable, "-c", code], cwd=tmp,
                                 capture_output=True, text=True,
                                 env={"PATH": "/usr/bin:/bin"})
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(res.stdout.split(), ["True", "True", "False", "True"])

    def _with_corpus(self, records):
        import contextlib
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        target = ProjectPaths.for_root(root).legacy_oracle_cards
        target.parent.mkdir(parents=True)
        with gzip.open(target, "wt", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record) + "\n")
        real = self.fc._PATHS
        self.fc._PATHS = ProjectPaths.for_root(root)
        stack = contextlib.ExitStack()
        stack.callback(tmp.cleanup)
        stack.callback(setattr, self.fc, "_PATHS", real)
        return stack

    GATED = [
        {"oracle_id": "a", "name": "Alpha", "set_type": "expansion", "legalities": {"vintage": "legal"}},
        {"oracle_id": "b", "name": "Alpha", "set_type": "token", "legalities": {"vintage": "not_legal"}},
        {"oracle_id": "c", "name": "Beta", "set_type": "expansion", "legalities": {"vintage": "restricted"}},
        {"oracle_id": "d", "name": "Beta", "set_type": "expansion", "legalities": {"vintage": "legal"}},
        {"oracle_id": "e", "name": "Gamma", "set_type": "token", "legalities": {}},
        {"oracle_id": "f", "name": "Gamma", "set_type": "expansion", "legalities": {"legacy": "legal"}},
        {"oracle_id": "g", "name": "Gamma", "set_type": "memorabilia", "legalities": {"legacy": "legal"}},
    ]

    def test_gate0_filters_BEFORE_the_name_index_is_built(self):
        with self._with_corpus(self.GATED):
            cards, index, gated_out = self.fc.load_corpus_gated()
        self.assertEqual(sorted(cards), ["a", "c", "d", "f", "g"])
        self.assertEqual(gated_out, 2)
        self.assertEqual(index, {"alpha": ["a"], "beta": ["c", "d"], "gamma": ["f", "g"]})

    def test_exact_name_resolution_and_its_one_ambiguity_rule(self):
        import contextlib
        import io
        with self._with_corpus(self.GATED):
            cards, index = self.fc.load_corpus()
        self.assertEqual(self.fc.resolve_name("  ALPHA ", cards, index), "a")   # token duplicate
        for name in ("Beta", "Alph", "Delta"):                                  # real ambiguity / no fuzzy
            with self.subTest(name=name):
                err = io.StringIO()
                with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as stop:
                    self.fc.resolve_name(name, cards, index)
                self.assertEqual(stop.exception.code, 1)
                self.assertTrue(err.getvalue().startswith("STOP — "), err.getvalue())


# ===========================================================================
# 3. S7 call-time substitution law
# ===========================================================================

S7_CARD = {"name": "Zzyzx Quorbin", "type_line": "Legendary Creature — Horror",
           "legalities": {"commander": "legal"},
           "oracle_text": "Whenever Zzyzx Quorbin attacks, destroy target artifact.\n"
                          "Zzyzx Quorbin can't be blocked."}


def _replacement(text, card):
    """Neither canonicalises the name NOR leaves the destroy clause intact, so
    every consumer's output moves if -- and only if -- the replacement reaches it."""
    return text.replace("destroy target artifact", "draw a card")


class TestS7CallTimeSubstitutionReachesEveryConsumer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _ensure_experiments_on_path()
        import foundry_common
        import foundry_locality
        import foundry_object_lattice
        import foundry_shape_extractor
        from mtj_foundry.mtg.shapes import delivery, locality, target_classes
        cls.fc, cls.fse = foundry_common, foundry_shape_extractor
        cls.floc, cls.fol = foundry_locality, foundry_object_lattice
        cls.delivery, cls.locality, cls.tc = delivery, locality, target_classes
        # The three-stage build every consumer performs, over the one card this
        # law is observed on -- no corpus needed.
        foundry_shape_extractor.build_self_noun_rx({"s7": S7_CARD})
        cls.ratified = foundry_shape_extractor.ratified_delivery_tokens()
        foundry_shape_extractor.build_keyword_homes(cls.ratified)

    def observe(self):
        return {
            "delivery": list(self.fse.deliveries_for_lines(S7_CARD, self.ratified)),
            "locality": self.floc.units(S7_CARD, strict=False),
            "det_scan_texts": self.fc.det_scan_texts(S7_CARD),
            "target_classes": list(self.fol.clauses_for(S7_CARD, "destroy")),
        }

    def reached(self) -> dict:
        """Replace the PERMANENT owner after the shells installed their
        providers; report, per consumer, whether its output moved."""
        before = self.observe()
        real = oracle_text.det_canonicalize_self_reference
        oracle_text.det_canonicalize_self_reference = _replacement
        try:
            after = self.observe()
        finally:
            oracle_text.det_canonicalize_self_reference = real
        self.assertEqual(self.observe(), before, "restoration failed")
        return {k: before[k] != after[k] for k in before}

    def test_the_live_route_reaches_every_consumer(self):
        self.assertEqual(self.reached(), {"delivery": True, "locality": True,
                                          "det_scan_texts": True, "target_classes": True})

    def test_a_CAPTURED_owner_is_detected_not_passed(self):
        """The negative control. Providers built from the owner function captured
        BEFORE the replacement must make `reached()` report False -- proving the
        check above can fail, and fails for exactly the S7 defect."""
        captured = oracle_text.det_canonicalize_self_reference
        snapshot = types.SimpleNamespace(
            full_oracle_text=self.fc.full_oracle_text,
            canonicalize_self_reference=captured,
            is_mode_line=self.fc.is_mode_line,
            _MODAL_HEADER_RE=self.fc._MODAL_HEADER_RE,
            _ROLL_INSTRUCTION_RE=self.fc._ROLL_INSTRUCTION_RE,
            _DIE_ROW_RE=self.fc._DIE_ROW_RE,
            raw_faces=self.fc.raw_faces)
        saved = (self.delivery._CARD_TEXT_RULES, self.locality._CARD_FACE_RULES)
        self.delivery.use_card_text_rules(self.delivery.CardTextRules(snapshot, {
            "full_oracle_text": "full_oracle_text",
            "canonicalize_self_reference": "canonicalize_self_reference",
            "is_mode_line": "is_mode_line", "modal_header_re": "_MODAL_HEADER_RE",
            "roll_instruction_re": "_ROLL_INSTRUCTION_RE", "die_row_re": "_DIE_ROW_RE"}))
        self.locality.use_card_face_rules(self.locality.CardFaceRules(snapshot, {
            "raw_faces": "raw_faces",
            "canonicalize_self_reference": "canonicalize_self_reference"}))
        try:
            reached = self.reached()
        finally:
            self.delivery._CARD_TEXT_RULES, self.locality._CARD_FACE_RULES = saved
        self.assertFalse(reached["delivery"])
        self.assertFalse(reached["locality"])
        # the untouched fc route still reaches the DET consumers
        self.assertTrue(reached["det_scan_texts"])
        self.assertTrue(reached["target_classes"])

    def test_the_legacy_facade_route_still_reaches_too(self):
        """WB4 replaces `fc.canonicalize_self_reference` rather than the owner.
        That spelling must keep reaching the injected substrates."""
        before = self.observe()
        real = self.fc.canonicalize_self_reference
        self.fc.canonicalize_self_reference = _replacement
        try:
            after = self.observe()
        finally:
            self.fc.canonicalize_self_reference = real
        self.assertEqual({k: before[k] != after[k] for k in before},
                         {"delivery": True, "locality": True,
                          "det_scan_texts": True, "target_classes": True})


# ===========================================================================
# 2b. full selected-corpus conservation, pinned from the LEGACY implementations
# ===========================================================================

def _digest(rows) -> str:
    h = hashlib.sha256()
    for row in rows:
        h.update(json.dumps(row, ensure_ascii=False, sort_keys=True).encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def corpus_digests(cards: dict, *, full_oracle_text, canonicalize, candidates,
                   predicates, det_scan_texts, gate, n2) -> dict:
    """One streaming pass over EVERY raw record, sorted by oracle_id.

    Every observable is a function of the decompressed records only. Candidate
    lists are digested SORTED: their tie order among equal-length names follows
    set iteration, which varies with PYTHONHASHSEED in the legacy implementation
    too, and no consumer output depends on it (measured: canonicalised text is
    identical across seeds).
    """
    order = sorted(cards)
    fot = {oid: full_oracle_text(cards[oid]) for oid in order}
    counts = {"raw": len(order), "gate0": 0, "n2_vs_det_divergent_gate0": 0,
              "lines": 0, "det_scan_texts": 0}
    counts.update({f"true_{k}": 0 for k in predicates})

    def lines():
        for oid in order:
            row = []
            for line in fot[oid].split("\n"):
                bits = {k: bool(f(line)) for k, f in predicates.items()}
                counts["lines"] += 1
                for k, v in bits.items():
                    counts[f"true_{k}"] += v
                row.append(bits)
            yield [oid, row]

    def det():
        for oid in order:
            texts = det_scan_texts(cards[oid])
            counts["det_scan_texts"] += len(texts)
            yield [oid, texts]

    def canon():
        for oid in order:
            card = cards[oid]
            text = canonicalize(fot[oid], card)
            if gate(card):
                counts["gate0"] += 1
                counts["n2_vs_det_divergent_gate0"] += n2(fot[oid], card) != text
            yield [oid, text]

    out = {
        "full_oracle_text": _digest([oid, fot[oid]] for oid in order),
        "canonicalized": _digest(canon()),
        "candidates_sorted": _digest([oid, sorted(candidates(cards[oid]))] for oid in order),
        "line_structure": _digest(lines()),
        "det_scan_texts": _digest(det()),
    }
    out["counts"] = counts
    return out


def neutral_n2(text, card):
    return oracle_text.normalize_self_references(
        text, oracle_text.self_name_candidates(card["name"]), card.get("keywords"))


OWNER_PREDICATES = {
    "modal_header": oracle_text.is_modal_header,
    "modal_header_stripped": lambda l: oracle_text.is_modal_header(l.strip()),
    "mode_line": oracle_text.is_mode_line,
    "roll_instruction": oracle_text.is_roll_instruction,
    "die_row": oracle_text.is_die_row,
    "die_result_row": oracle_text.is_die_result_row,
    "level_band_stripped": lambda l: oracle_text.is_level_band(l.strip()),
    "class_level_bar_stripped": lambda l: oracle_text.is_class_level_bar(l.strip()),
    "striation_marker": oracle_text.is_striation_marker,
}

# MEASURED FROM THE LEGACY IMPLEMENTATIONS at a77e679f561f96959824b5fcea4be03dfcdaaa35
# (fc.full_oracle_text / fc.canonicalize_self_reference / fc._cardname_candidates /
# fc._MODAL_HEADER_RE, fc.is_mode_line, fc._ROLL_INSTRUCTION_RE, fc._DIE_ROW_RE,
# fc._is_die_row, fc._LEVEL_BAND_RE, fc._CLASS_LEVEL_RE, fc._is_band_marker /
# fc.det_scan_texts / fc.gate_passes), over content sha256 SELECTED_CONTENT_SHA256.
LEGACY_PINNED = {'candidates_sorted': '6426ebc16b7bbc0a6a37286dbafa2ee05ea328d4451f791b4c2b821423d261c7',
 'canonicalized': '1653189d407fb6b80ff93004d8c0e9e136dfed9e689b633692020df0f36fe58f',
 'counts': {'det_scan_texts': 40557,
            'gate0': 32557,
            'lines': 70848,
            'n2_vs_det_divergent_gate0': 1818,
            'raw': 38233,
            'true_class_level_bar_stripped': 76,
            'true_die_result_row': 2303,
            'true_die_row': 157,
            'true_level_band_stripped': 54,
            'true_modal_header': 1177,
            'true_modal_header_stripped': 1177,
            'true_mode_line': 2146,
            'true_roll_instruction': 209,
            'true_striation_marker': 130},
 'det_scan_texts': '75642e08b2b4c4914963822956b797fa5e896b112be329922d24e73d78220578',
 'full_oracle_text': '47702c3a26dfe293aeff2081e272e5bbc273cee23f03a5d322c1caaa9e4a4383',
 'line_structure': 'd3cef470e7a0a09940105654f3d3bb98f12adfb4130eed9a64b73e8b964e577e'}


@unittest.skipUnless(CORPUS_FILE.exists(), "selected corpus is gitignored card data")
class TestConservationOverTheSelectedCorpus(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        h = hashlib.sha256()
        with gzip.open(CORPUS_FILE, "rb") as handle:
            for block in iter(lambda: handle.read(1 << 20), b""):
                h.update(block)
        if h.hexdigest() != SELECTED_CONTENT_SHA256:
            raise AssertionError(f"{CORPUS_FILE} is not the selected corpus content: "
                                 f"{h.hexdigest()} != {SELECTED_CONTENT_SHA256}")
        _ensure_experiments_on_path()
        import foundry_common
        cls.cards = corpus.load_cards(CORPUS_FILE)
        cls.measured = corpus_digests(
            cls.cards, full_oracle_text=corpus.full_oracle_text,
            canonicalize=oracle_text.det_canonicalize_self_reference,
            candidates=oracle_text.det_self_name_candidates,
            predicates=OWNER_PREDICATES, det_scan_texts=foundry_common.det_scan_texts,
            gate=corpus.is_gate0_eligible, n2=neutral_n2)

    def test_every_digest_equals_the_legacy_measurement(self):
        self.assertEqual(self.measured, LEGACY_PINNED)

    def test_the_population_is_the_whole_corpus_and_the_boundaries_are_nontrivial(self):
        counts = self.measured["counts"]
        self.assertEqual(counts["raw"], 38233)
        self.assertEqual(counts["gate0"], 32557)
        # N2 and DET remain DIFFERENT contracts on real cards, not merged.
        self.assertGreater(counts["n2_vs_det_divergent_gate0"], 0)
        for key, value in counts.items():
            if key.startswith("true_"):
                with self.subTest(predicate=key):
                    self.assertGreater(value, 0, "a predicate never fired on real text")


# ===========================================================================
# 4. topology
# ===========================================================================

MODULE = "foundry_common"
ARCHIVE_PREFIX = "archive/"


def provider_names(source: str) -> set:
    names = set()
    for node in ast.parse(source).body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                names |= {n.id for n in ast.walk(target) if isinstance(n, ast.Name)}
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


def caller_census(sources: dict, provider_source: str, known_names=()) -> dict:
    """`{path: sorted referenced names}` for every Python source importing the
    provider -- import / from-import / `experiments.`-qualified / `import_module`
    -- with module-qualified attributes, `getattr`/`setattr`/`hasattr` names, and
    string constants naming a provider responsibility (the S7 string-bound
    injection contract). `known_names` adds names that are no longer defined
    (retired) so a reintroduced attribute/import reference to one is still
    reported; a bare string of a retired name is not a provider contract, since
    an injection naming an absent attribute is refused at install."""
    defined = provider_names(provider_source)
    nameable = defined | set(known_names)

    def is_module(name):
        return name == MODULE or name.endswith("." + MODULE)

    census = {}
    for path, text in sources.items():
        tree = ast.parse(text, filename=path)
        aliases, refs, imported = set(), set(), False
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if is_module(alias.name):
                        imported = True
                        aliases.add(alias.asname or alias.name)
            elif isinstance(node, ast.ImportFrom):
                if is_module(node.module or ""):
                    imported = True
                    refs |= {a.name for a in node.names}
                else:
                    for alias in node.names:
                        if alias.name == MODULE:
                            imported = True
                            aliases.add(alias.asname or alias.name)
            elif isinstance(node, ast.Call):
                fn = node.func
                name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
                if (name in ("import_module", "__import__") and node.args
                        and isinstance(node.args[0], ast.Constant)
                        and isinstance(node.args[0].value, str)
                        and is_module(node.args[0].value)):
                    imported = True
        if not imported:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
                    and node.value.id in aliases:
                refs.add(node.attr)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id in ("getattr", "setattr", "hasattr") \
                    and len(node.args) >= 2 and isinstance(node.args[0], ast.Name) \
                    and node.args[0].id in aliases and isinstance(node.args[1], ast.Constant):
                refs.add(node.args[1].value)
            elif isinstance(node, ast.Constant) and isinstance(node.value, str) \
                    and node.value in defined:
                refs.add(node.value)
        census[path] = sorted(r for r in refs if r in nameable)
    return census


def tracked_python_sources(root: Path) -> dict:
    listed = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "*.py"],
                            capture_output=True, check=True).stdout.decode().split("\0")
    return {p: (root / p).read_text(encoding="utf-8") for p in listed
            if p and p != f"experiments/{MODULE}.py" and (root / p).exists()}


def split_live(census: dict):
    live = {p: v for p, v in census.items() if not p.startswith(ARCHIVE_PREFIX)}
    archive = sorted(p for p in census if p.startswith(ARCHIVE_PREFIX))
    return live, archive


# The reviewed post-S10 live caller set: 86 at accepted base, 86 after S10. S10
# migrated REFERENCES, not whole importers: every live importer still needs the
# provider for at least one retained responsibility (bootstrap, `halt`, the corpus
# loaders, path aliases, DET synthetic composition, pattern policy, review/prompt
# composition) or is frozen/owned by a later slice.
# The pinned sets live in a JSON sidecar, not in this module: this module is
# itself a (test) caller, and a Python literal listing every provider name would
# be counted as string-bound references to all of them.
TOPOLOGY = json.loads((Path(__file__).with_name("s10_foundry_common_callers.json"))
                      .read_text(encoding="utf-8"))
EXPECTED_ARCHIVE = TOPOLOGY["archive_importers"]
EXPECTED_LIVE = TOPOLOGY["live_importers"]


@unittest.skipUnless((REPO_ROOT / ".git").exists(), "topology is measured from git ls-files")
class TestCallerTopology(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.provider = PROVIDER.read_text(encoding="utf-8")
        cls.sources = tracked_python_sources(REPO_ROOT)
        cls.census = caller_census(cls.sources, cls.provider, RETIRED)

    def test_the_live_caller_set_is_exactly_the_reviewed_one(self):
        live, archive = split_live(self.census)
        self.assertEqual(archive, EXPECTED_ARCHIVE)
        self.assertEqual(live, EXPECTED_LIVE)

    def test_no_live_reference_to_a_retired_name(self):
        live, _ = split_live(self.census)
        offenders = {p: sorted(set(v) & set(RETIRED)) for p, v in live.items()
                     if set(v) & set(RETIRED)}
        self.assertEqual(offenders, {})

    def test_frozen_AQ4_callers_keep_their_compatibility_surface(self):
        defined = provider_names(self.provider)
        for path, names in self.census.items():
            if path.startswith("benchmarks/aq4/experiments/aq4_benchmark/"):
                with self.subTest(path=path):
                    self.assertTrue(set(names) <= defined, set(names) - defined)

    # --- the census's own negative controls ------------------------------------

    def test_control_a_reintroduced_live_caller_is_reported(self):
        sources = dict(self.sources)
        sources["experiments/zz_s10_probe.py"] = "import foundry_common as fc\nfc.halt('x')\n"
        live, _ = split_live(caller_census(sources, self.provider, RETIRED))
        self.assertNotEqual(live, EXPECTED_LIVE)
        self.assertEqual(live["experiments/zz_s10_probe.py"], ["halt"])

    def test_control_an_archive_importer_misclassified_as_live_is_reported(self):
        census = dict(self.census)
        moved = census.pop(EXPECTED_ARCHIVE[0])
        census["experiments/foundry_build_reaudit_packet.py"] = moved
        live, archive = split_live(census)
        self.assertNotEqual((live, archive), (EXPECTED_LIVE, EXPECTED_ARCHIVE))

    def test_control_a_retired_name_reference_is_reported(self):
        sources = dict(self.sources)
        path = "tests/guards/gate2/foundry_routing_regression.py"
        sources[path] += "\nfc._is_legendary({})\n"
        live, _ = split_live(caller_census(sources, self.provider, RETIRED))
        self.assertIn("_is_legendary", live[path])

    def test_control_a_string_bound_injection_name_is_counted(self):
        sources = {"experiments/zz.py": "import foundry_common as fc\nX = {'a': 'is_mode_line'}\n"}
        self.assertEqual(caller_census(sources, self.provider)["experiments/zz.py"],
                         ["is_mode_line"])


if __name__ == "__main__":
    unittest.main()
