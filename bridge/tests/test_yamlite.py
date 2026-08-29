"""Unit tests: the YAML-subset parser, including its two DELIBERATE deviations."""

import unittest
from pathlib import Path

from mtjbridge import yamlite
from mtjbridge.yamlite import YamlLiteError

FIXTURES = Path(__file__).parent / "fixtures"


class TestParsing(unittest.TestCase):
    def test_nested_mappings_and_sequences(self):
        data = yamlite.parse(
            "a: 1\nb:\n  c: two\n  d:\n    - x\n    - y\ne:\n  - k: 1\n    l: 2\n  - k: 3\n    l: 4\n"
        )
        self.assertEqual(data["a"], 1)
        self.assertEqual(data["b"]["d"], ["x", "y"])
        self.assertEqual(data["e"], [{"k": 1, "l": 2}, {"k": 3, "l": 4}])

    def test_block_scalars(self):
        data = yamlite.parse("folded: >-\n  one\n  two\nliteral: |\n  line1\n  line2\n")
        self.assertEqual(data["folded"], "one two")
        self.assertEqual(data["literal"], "line1\nline2\n")

    def test_comments_and_quotes(self):
        data = yamlite.parse('# lead\na: 1  # trailing\nb: "has # hash"\nc: \'single\'\n')
        self.assertEqual(data, {"a": 1, "b": "has # hash", "c": "single"})

    def test_colon_inside_a_quoted_value(self):
        self.assertEqual(yamlite.parse('a: "x: y"')["a"], "x: y")

    def test_null_and_bool_domain(self):
        data = yamlite.parse("a:\nb: ~\nc: null\nd: true\ne: false\n")
        self.assertEqual(list(data.values()), [None, None, None, True, False])


class TestDeliberateDeviations(unittest.TestCase):
    """Two places yamlite intentionally disagrees with PyYAML. Both are pinned here
    because a silent change to either would corrupt an identifier."""

    def test_a_forty_zero_sha_stays_a_string(self):
        """PyYAML yields int 0. That destroys a git SHA."""
        self.assertEqual(yamlite.parse("base: " + "0" * 40)["base"], "0" * 40)
        self.assertEqual(yamlite.parse("n: 007")["n"], "007")
        self.assertEqual(yamlite.parse("n: 42")["n"], 42)

    def test_a_date_stays_a_string(self):
        """PyYAML yields datetime.date. Protocol fields are compared as text."""
        self.assertEqual(yamlite.parse("updated: 2026-08-28")["updated"], "2026-08-28")

    def test_a_backtick_scalar_parses(self):
        """PyYAML REFUSES this, and the live Issue #3 contract contains it."""
        data = yamlite.parse("items:\n  - `--once` and `--dry-run` modes required\n")
        self.assertEqual(data["items"], ["`--once` and `--dry-run` modes required"])


class TestHaltsLoudly(unittest.TestCase):
    def test_flow_collections_refused(self):
        for src in ("a: [1, 2]", "a: {b: 1}"):
            with self.assertRaises(YamlLiteError):
                yamlite.parse(src)

    def test_anchors_refused(self):
        with self.assertRaises(YamlLiteError):
            yamlite.parse("a: &anchor 1")

    def test_tabs_refused(self):
        with self.assertRaises(YamlLiteError):
            yamlite.parse("a:\n\tb: 1")

    def test_duplicate_key_refused(self):
        with self.assertRaises(YamlLiteError):
            yamlite.parse("a: 1\na: 2")

    def test_error_names_the_line(self):
        with self.assertRaises(YamlLiteError) as ctx:
            yamlite.parse("a: 1\nb: [2]")
        self.assertIn("line 2", str(ctx.exception))


class TestRoundTrip(unittest.TestCase):
    def test_emit_reparse_is_identity_on_the_live_contract(self):
        body = yamlite.find_blocks((FIXTURES / "issue3.md").read_text())[0]
        data = yamlite.parse(body)
        self.assertEqual(yamlite.parse(yamlite.emit(data)), data)

    def test_emit_quotes_values_that_would_otherwise_change_type(self):
        data = {"sha": "0" * 40, "date": "2026-08-28", "flag": "true", "n": "007"}
        self.assertEqual(yamlite.parse(yamlite.emit(data)), data)

    def test_find_blocks_picks_the_yaml_fence_only(self):
        md = "text\n```python\nx=1\n```\n```yaml\na: 1\n```\n"
        self.assertEqual(yamlite.find_blocks(md), ["a: 1"])


if __name__ == "__main__":
    unittest.main()


class TestEmitterParserAgreement(unittest.TestCase):
    """The emitter must never produce a construct its own parser refuses.

    This is pinned as a property, not a sample: an emitter/parser disagreement
    lands on GitHub looking fine and then cannot be read back, which silently
    breaks crash recovery.
    """

    CASES = [
        {"schema": "mtj-review/1", "findings": [], "captain": {}, "n": None},
        {"a": [], "b": {}, "c": [[], {}], "d": [{"x": []}]},
        {"sha": "0" * 40, "date": "2026-08-28", "text": "has: colon", "hash": "a # b"},
        {"deep": {"deeper": {"deepest": ["x", {"y": None}]}}},
        {"quoted": "true", "real": True, "num": "007", "int": 7, "neg": -3},
        {"empty_str": "", "dash": "-", "brackets": "[not a list]"},
    ]

    def test_every_payload_reparses_to_itself(self):
        for case in self.CASES:
            with self.subTest(case=case):
                text = yamlite.emit(case)
                self.assertEqual(yamlite.parse(text), case)

    def test_empty_flow_collections_are_accepted_on_input(self):
        self.assertEqual(yamlite.parse("a: []\nb: {}\n"), {"a": [], "b": {}})

    def test_non_empty_flow_is_still_refused(self):
        with self.assertRaises(YamlLiteError):
            yamlite.parse("a: [1, 2]")

    def test_every_protocol_message_render_reparses(self):
        from mtjbridge.protocol import parse_review, render_block

        payload = {"schema": "mtj-review/1", "task": "T", "verdict": "PASS",
                   "reasons": ["ok"], "findings": [], "captain_categories": []}
        self.assertEqual(parse_review(render_block(payload)).verdict, "PASS")
