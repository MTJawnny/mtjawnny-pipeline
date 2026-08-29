"""Unit tests: secret redaction. A credential must never reach a log or GitHub."""

import io
import logging
import unittest

from mtjbridge.logging_setup import RedactingJsonFormatter, configure, get_logger
from mtjbridge.redact import REDACTED, assert_clean, redact


class TestRedaction(unittest.TestCase):
    def test_token_shapes(self):
        cases = [
            "gho_16CharactersMinimumABCDEFGH",
            "ghp_16CharactersMinimumABCDEFGH",
            "github_pat_11ABCDEFG0abcdefghijklmnop",
            "sk-abcdefghijklmnopqrstuvwxyz",
            "sk-ant-abcdefghijklmnopqrstuvwxyz",
            "AKIAIOSFODNN7EXAMPLE",
            "xoxb-1234567890-abcdefghij",
        ]
        for secret in cases:
            with self.subTest(secret=secret[:8]):
                out = redact(f"prefix {secret} suffix")
                self.assertNotIn(secret, out)
                self.assertIn(REDACTED, out)
                self.assertIn("prefix", out)

    def test_bearer_header(self):
        out = redact("Authorization: Bearer abcdefghijklmnopqrstuvwxyz")
        self.assertNotIn("abcdefghijklmnop", out)

    def test_private_key_block(self):
        text = "-----BEGIN RSA PRIVATE KEY-----\nMIIabc\n-----END RSA PRIVATE KEY-----"
        self.assertNotIn("MIIabc", redact(text))

    def test_environment_values_are_redacted_whatever_their_shape(self):
        env = {"OPENAI_API_KEY": "an-unusual-value-with-no-recognisable-shape"}
        out = redact("leaked an-unusual-value-with-no-recognisable-shape here", env)
        self.assertNotIn("an-unusual-value", out)

    def test_redaction_is_idempotent(self):
        once = redact("token gho_16CharactersMinimumABCDEFGH")
        self.assertEqual(once, redact(once))

    def test_assert_clean_halts_on_an_unredacted_secret(self):
        env = {"OPENAI_API_KEY": "supersecretvalue123456"}
        with self.assertRaises(RuntimeError):
            assert_clean("body containing supersecretvalue123456", env)

    def test_short_env_values_are_not_redacted(self):
        """Deliberate: a 3-char value would blank out ordinary words everywhere."""
        env = {"OPENAI_API_KEY": "abc"}
        self.assertEqual(redact("abc def", env), "abc def")


class TestLogRedaction(unittest.TestCase):
    def test_secrets_do_not_survive_the_log_handler(self):
        stream = io.StringIO()
        configure("DEBUG", stream=stream)
        log = get_logger("test")
        log.info("running", extra={"argv": "gh auth --token gho_16CharactersMinimumABCDEFGH"})
        output = stream.getvalue()
        self.assertNotIn("gho_16Characters", output)
        self.assertIn(REDACTED, output)

    def test_log_line_is_valid_json_with_structured_fields(self):
        import json

        stream = io.StringIO()
        configure("DEBUG", stream=stream)
        get_logger("test").info("hello", extra={"issue": 3, "task": "T"})
        payload = json.loads(stream.getvalue().strip().splitlines()[-1])
        self.assertEqual(payload["msg"], "hello")
        self.assertEqual(payload["issue"], 3)
        self.assertEqual(payload["level"], "INFO")


if __name__ == "__main__":
    unittest.main()
