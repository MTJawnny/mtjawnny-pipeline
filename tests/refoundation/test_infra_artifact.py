"""The generated-artifact byte format, pinned to the bytes it inherited.

S5 promoted `write_json` out of `experiments/foundry_common.py` into
`mtj_foundry.infra.artifact` as its single permanent owner. Forty-three legacy
tools call it across 58 sites, so its output is a real contract with every
tracked artifact those tools have written.

THIS FILE PINS BYTES, NOT JSON. That distinction is the whole point:

    json.dump(..., ensure_ascii=False)   {"name": "Juzám"}
    json.dump(..., ensure_ascii=True)    {"name": "Juzám"}

Both are valid JSON, both parse to the same object, and BOTH ARE PERFECTLY
DETERMINISTIC -- the same input yields the same wrong file every time. A
determinism check compares a run against another run, so it cannot see this at
all. Only a comparison against the CONTRACTED bytes can, which is why the golden
digests below are recorded rather than the documents being compared as JSON.

The digests were taken from the legacy implementation at the S5 base commit
`1cb8d31474180f4863e84b3a8390e5b142a03a95`, not invented here.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT  # noqa: F401  (sets sys.path)

from mtj_foundry.infra.artifact import write_json

# fixture -> (payload, sha256 of the bytes the BASE implementation emitted)
CONTRACT = {
    "ascii": (
        {"b": 2, "a": [1, 2, 3], "n": None, "t": True},
        "8b6ada521b4a3aa1"),
    "non_ascii": (
        {"name": "Juzám Djinn", "quote": "Urza’s Saga",
         "cr": "“curly” — em dash", "jp": "日本語", "emoji": "\U0001f5ff"},
        "0faeffed889ccc35"),
    "nested_empty": (
        {"deep": {"deeper": {"deepest": []}}, "": ""},
        "4ccd0e87dd023ea2"),
    "floats_ints": (
        {"f": 1.5, "i": 10, "neg": -0.0, "big": 12345678901234567890},
        "98ae8b5c2d4485ec"),
    "unicode_keys": (
        {"Juzám": 1, "’": 2},
        "17245a52b74e3455"),
}


def emit(data, *, nested: bool = True) -> bytes:
    """Write through the permanent owner and return the exact bytes.

    `nested` exercises the parent-creation half of the contract: the
    destination's parent does not exist until `write_json` makes it.
    """
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / ("a/b/c/out.json" if nested else "out.json")
        if nested:
            assert not path.parent.exists()
        write_json(path, data)
        assert path.parent.is_dir(), "write_json did not create parents"
        return path.read_bytes()


class TestTheByteContractIsTheInheritedOne(unittest.TestCase):

    def test_every_fixture_matches_the_base_contracted_bytes(self):
        """THE GUARD THE `ensure_ascii` NEGATIVE CONTROL AIMS AT.

        Flipping `ensure_ascii` leaves every document valid, equivalent and
        deterministic, and turns this red on `non_ascii` and `unicode_keys`.
        """
        for name, (data, digest) in sorted(CONTRACT.items()):
            with self.subTest(fixture=name):
                self.assertEqual(
                    hashlib.sha256(emit(data)).hexdigest()[:16], digest)

    def test_non_ascii_is_emitted_raw_and_never_escaped(self):
        """Stated as its own property so the failure names the cause. The
        corpus's own vocabulary is non-ASCII -- `Juzám`, `Urza’s`, the CR's
        curly apostrophe -- so escaping is not a cosmetic difference."""
        raw = emit(CONTRACT["non_ascii"][0])
        self.assertNotIn(b"\\u", raw)
        self.assertIn("Juzám".encode("utf-8"), raw)
        self.assertIn("Urza’s".encode("utf-8"), raw)

    def test_exactly_one_trailing_newline(self):
        for name, (data, _) in sorted(CONTRACT.items()):
            with self.subTest(fixture=name):
                raw = emit(data)
                self.assertTrue(raw.endswith(b"\n"))
                self.assertFalse(raw.endswith(b"\n\n"))

    def test_the_indent_is_two_and_keys_keep_insertion_order(self):
        """`indent=2` and NO `sort_keys`. Adding sorting would be a
        canonicalization the base contract does not perform."""
        raw = emit({"b": 1, "a": 2}).decode("utf-8")
        self.assertIn('\n  "b": 1', raw)
        self.assertLess(raw.index('"b"'), raw.index('"a"'))

    def test_writing_the_same_payload_twice_is_byte_identical(self):
        """Determinism -- necessary, and on its own NOT sufficient. This passes
        unchanged under a wrong `ensure_ascii`, which is exactly why the digest
        pin above exists beside it."""
        for name, (data, _) in sorted(CONTRACT.items()):
            with self.subTest(fixture=name):
                self.assertEqual(emit(data), emit(data))

    def test_the_payload_still_round_trips(self):
        for name, (data, _) in sorted(CONTRACT.items()):
            with self.subTest(fixture=name):
                self.assertEqual(json.loads(emit(data).decode("utf-8")), data)


class TestTheLegacyFacadeHoldsNoSecondCopy(unittest.TestCase):
    """Two implementations of a byte contract is how one of them drifts."""

    SOURCE = REPO_ROOT / "experiments" / "foundry_common.py"

    def test_the_facade_delegates_and_serializes_nothing_itself(self):
        import ast
        tree = ast.parse(self.SOURCE.read_text(encoding="utf-8"))
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "write_json")
        body = ast.dump(fn)
        self.assertNotIn("json", body.replace("write_json", ""))
        self.assertNotIn("ensure_ascii", body)
        self.assertIn("_artifact", body)

    def test_the_write_json_policy_moved_rather_than_multiplied(self):
        """Scoped to the capability S5 owns, and stated as a DELTA.

        Seven package modules already carried their own `ensure_ascii` for their
        own writers before S5 -- `codebook_store`, `conservation`,
        `conservation_contract`, `evaluation`, `evidence_index`, `pilot`,
        `retrieval`, `runtime`. Those predate this slice, are untouched by it,
        and consolidating them would be a redesign S5 does not authorize.

        So the assertion is the one S5 is responsible for: the legacy copy is
        GONE, `infra/artifact.py` is the one place that gained it, and the count
        did not grow anywhere else. A bare "exactly once in the package" would
        have been false about the repository rather than true about the move.
        """
        import ast

        def policy_sites(path: Path) -> int:
            """`ensure_ascii=` passed to a CALL. Counted from the AST, because
            this module's own docstring explains the flag twice and a substring
            count would score documentation as policy."""
            tree = ast.parse(path.read_text(encoding="utf-8"))
            return sum(1 for c in ast.walk(tree) if isinstance(c, ast.Call)
                       for k in c.keywords if k.arg == "ensure_ascii")

        pkg = REPO_ROOT / "src" / "mtj_foundry"
        live = {p.name: policy_sites(p) for p in sorted(pkg.rglob("*.py"))
                if policy_sites(p)}
        self.assertEqual(live, {
            # unchanged, pre-existing owners of their own output. S8 moved the
            # evidence owner to `evidence/index.py`; this map is keyed by
            # BASENAME, so its key is now `index.py`. The policy site itself did
            # not move, multiply or change -- only the file it lives in.
            "codebook_store.py": 1, "evaluation.py": 1, "index.py": 1,
            "pilot.py": 1, "retrieval.py": 1, "runtime.py": 1,
            "conservation.py": 1, "conservation_contract.py": 1,
            # the one S5 adds -- the promoted write_json policy
            "artifact.py": 1,
        })
        # and the legacy facade kept no copy of it
        self.assertEqual(policy_sites(self.SOURCE), 0)


if __name__ == "__main__":
    unittest.main()
