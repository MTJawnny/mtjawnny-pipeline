"""S13.R3 — the candidate-manifest path join stays at the authority boundary.

WHY THIS EXISTS
---------------
R2 bound `candidate_dir=fc.FOUNDRY_OUT_DIR` in the legacy shell and let
`mtj_foundry.authority_cli` build `candidate_dir / f"candidate-manifest.…json"`.
Behaviour was identical, but the layout census stopped seeing a classified
`PATH_JOIN` at that site and recorded an unclassified `OTHER` — hidden behind an
inherited census count assertion that was already failing.

R3 puts the join back where repository layout belongs: the shell supplies
`candidate_out=lambda snapshot_id: fc.FOUNDRY_OUT_DIR / f"candidate-manifest.{snapshot_id}.json"`
and the permanent operator only calls it when `--candidate-out` is absent.

WHAT IS PROVED HERE
-------------------
1. The shell owns the join, as a `PATH_JOIN` on `fc.FOUNDRY_OUT_DIR`, read at
   call time.
2. The operator holds no candidate layout: no directory field, no
   `candidate-manifest` literal, only the injected callback.
3. The layout census finds no `OTHER` form anywhere in legacy production — the
   check does NOT go through the inherited count pins, so it cannot be masked.
4. `cmd_publish` uses the callback only for the default; an explicit
   `--candidate-out` never reaches it; the tracked-selector refusal still STOPs.
Each structural guard has a CONTROL that rigs the R2 spelling and turns it red.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.refoundation import layout_census
from tests.refoundation.helpers import REPO_ROOT, SRC
from tests.refoundation.test_gate2_purity import EXPERIMENTS, load_legacy
from tests.refoundation.test_layout_delegation import _census_inputs

from mtj_foundry import authority, authority_cli

SHELL_REL = Path("experiments/foundry_authority.py")
OPERATOR = SRC / "mtj_foundry" / "authority_cli.py"
R2_BINDING = "        candidate_dir=fc.FOUNDRY_OUT_DIR,\n"


def _shell_source() -> str:
    return (EXPERIMENTS / "foundry_authority.py").read_text(encoding="utf-8")


def _rig_r2_binding(source: str) -> str:
    start = source.index("        candidate_out=lambda snapshot_id: (")
    end = source.index('.json"),\n', start) + len('.json"),\n')
    return source[:start] + R2_BINDING + source[end:]


def shell_join_violations(source: str) -> list[str]:
    """Where `_context` fails to own the candidate-manifest join."""
    tree = ast.parse(source)
    ctx = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_context"]
    if len(ctx) != 1:
        return ["no single _context()"]
    kws = {kw.arg: kw.value for n in ast.walk(ctx[0]) if isinstance(n, ast.Call)
           for kw in n.keywords}
    out = []
    if "candidate_dir" in kws:
        out.append("candidate_dir is bound; the operator would own the join")
    value = kws.get("candidate_out")
    if not isinstance(value, ast.Lambda) or [a.arg for a in value.args.args] != ["snapshot_id"]:
        return out + ["candidate_out is not a one-argument lambda of snapshot_id"]
    body = value.body
    if not (isinstance(body, ast.BinOp) and isinstance(body.op, ast.Div)
            and ast.unparse(body.left) == "fc.FOUNDRY_OUT_DIR"
            and isinstance(body.right, ast.JoinedStr)):
        return out + [f"candidate_out is not a FOUNDRY_OUT_DIR path join: {ast.unparse(body)}"]
    parts = [ast.unparse(v.value) if isinstance(v, ast.FormattedValue) else v.value
             for v in body.right.values]
    if parts != ["candidate-manifest.", "snapshot_id", ".json"]:
        out.append(f"candidate filename changed: {parts}")
    return out


def operator_layout_violations(source: str) -> list[str]:
    """Where the permanent operator regrows candidate layout."""
    tree = ast.parse(source)
    out = []
    if "candidate-manifest" in source:
        out.append("candidate-manifest filename literal in the operator")
    if "candidate_dir" in source:
        out.append("candidate_dir in the operator")
    fields = {n.target.id: ast.unparse(n.annotation) for c in ast.walk(tree)
              if isinstance(c, ast.ClassDef) and c.name == "AuthorityOperatorContext"
              for n in c.body if isinstance(n, ast.AnnAssign)}
    if fields.get("candidate_out") != "Callable[[str], Path]":
        out.append(f"candidate_out field is {fields.get('candidate_out')!r}")
    calls = [ast.unparse(n) for n in ast.walk(tree) if isinstance(n, ast.Call)
             and ast.unparse(n.func) == "ctx.candidate_out"]
    if calls != ["ctx.candidate_out(manifest['snapshot_id'])"]:
        out.append(f"candidate_out call sites: {calls}")
    return out


def census_forms(source: str, rel: Path) -> list[tuple[str, str, str]]:
    _, providers = _census_inputs()
    return [(r.module, r.name, r.form)
            for r in layout_census.delegation_references(source, rel, providers)]


class TestTheShellOwnsTheCandidateJoin(unittest.TestCase):

    def test_the_shell_owns_the_candidate_manifest_join(self):
        self.assertEqual(shell_join_violations(_shell_source()), [])

    def test_CONTROL_the_r2_directory_binding_is_caught(self):
        rigged = _rig_r2_binding(_shell_source())
        self.assertIn(R2_BINDING, rigged)
        self.assertTrue(shell_join_violations(rigged))

    def test_the_join_reads_the_layout_at_call_time(self):
        auth = load_legacy("foundry_authority")
        ctx = auth._context()
        with tempfile.TemporaryDirectory() as td, \
                mock.patch.object(auth.fc, "FOUNDRY_OUT_DIR", Path(td)):
            self.assertEqual(ctx.candidate_out("p3"),
                             Path(td) / "candidate-manifest.p3.json")


class TestTheOperatorHoldsNoCandidateLayout(unittest.TestCase):

    def test_the_operator_consumes_only_the_injected_callback(self):
        self.assertEqual(operator_layout_violations(OPERATOR.read_text(encoding="utf-8")), [])

    def test_CONTROL_a_regrown_operator_join_is_caught(self):
        source = OPERATOR.read_text(encoding="utf-8")
        rigged = source.replace(
            'ctx.candidate_out(manifest["snapshot_id"])',
            'ctx.candidate_dir / f"candidate-manifest.{manifest[\'snapshot_id\']}.json"'
        ).replace("candidate_out: Callable[[str], Path]", "candidate_dir: Path")
        self.assertNotEqual(rigged, source)
        self.assertEqual(len(operator_layout_violations(rigged)), 4)


class TestTheCensusClassifiesTheAuthoritySite(unittest.TestCase):
    """Deliberately independent of the inherited `CENSUS_HEAD` count pins, which
    were already failing and so could not show a new `OTHER`."""

    def test_the_authority_site_is_a_path_join(self):
        forms = census_forms(_shell_source(), SHELL_REL)
        self.assertEqual(
            sorted(f for m, n, f in forms if (m, n) == ("foundry_common", "FOUNDRY_OUT_DIR")),
            ["PATH_JOIN"])

    def test_no_legacy_production_file_has_an_unclassified_form(self):
        others = []
        for rel in layout_census.tracked_python(REPO_ROOT):
            if layout_census.scope_of(rel) not in layout_census.LEGACY_PRODUCTION:
                continue
            source = (REPO_ROOT / rel).read_text(encoding="utf-8")
            others += [(str(rel), m, n) for m, n, f in census_forms(source, rel)
                       if f == "OTHER"]
        self.assertEqual(others, [])

    def test_CONTROL_the_r2_binding_is_an_unclassified_form(self):
        forms = census_forms(_rig_r2_binding(_shell_source()), SHELL_REL)
        self.assertIn(("foundry_common", "FOUNDRY_OUT_DIR", "OTHER"), forms)


class TestPublishUsesTheCallbackOnlyForTheDefault(unittest.TestCase):

    def publish(self, td, candidate_out_arg, callback, manifest_path=None, stop=None):
        calls = []

        def candidate_out(snapshot_id):
            calls.append(snapshot_id)
            return callback(snapshot_id)

        def halt(message):
            raise SystemExit(message)
        stop = stop or halt
        ctx = authority_cli.AuthorityOperatorContext(
            manifest_path=manifest_path or Path(td) / "selector.json",
            codebook_path=lambda: Path(td) / "codebook.json",
            candidate_out=candidate_out,
            read_remote=lambda e: e, write_remote=lambda e: e,
            transport=lambda r, bucket: self.fail("no transport on a dry run"),
            backup_policy=lambda: None, corpus_ref_current=lambda: "2026-07-04",
            stop=stop, selftest=lambda: 0)
        args = argparse.Namespace(
            codebook=None, prior_manifest=None, snapshot_id="s-1", mutation_review_id="mr",
            corpus_ref=None, previous_snapshot_hash=None, candidate_out=candidate_out_arg,
            remote=None, dry_run=True)
        with mock.patch.object(authority, "build_manifest",
                               lambda **kw: {"snapshot_id": kw["snapshot_id"]}), \
                mock.patch.object(authority, "serialize_manifest", lambda m: "{}\n"), \
                contextlib.redirect_stdout(io.StringIO()):
            rc = authority_cli.cmd_publish(args, ctx)
        return rc, calls

    def test_the_default_path_comes_from_the_callback(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "out" / "x.json"
            rc, calls = self.publish(td, None, lambda sid: target)
            self.assertEqual((rc, calls), (0, ["s-1"]))
            self.assertEqual(target.read_text(encoding="utf-8"), "{}\n")

    def test_an_explicit_candidate_out_never_reaches_the_callback(self):
        with tempfile.TemporaryDirectory() as td:
            explicit = Path(td) / "explicit.json"
            rc, calls = self.publish(td, str(explicit), lambda sid: self.fail("called"))
            self.assertEqual((rc, calls), (0, []))
            self.assertTrue(explicit.exists())

    def test_the_tracked_selector_refusal_still_stops(self):
        with tempfile.TemporaryDirectory() as td:
            selector = Path(td) / "selector.json"
            with self.assertRaisesRegex(SystemExit, "TRACKED selector path"):
                self.publish(td, None, lambda sid: selector, manifest_path=selector)
            self.assertFalse(selector.exists())

    def test_CONTROL_a_swallowed_selector_refusal_is_caught(self):
        """The refusal test is only a guard if a stop that returns turns it red."""
        with tempfile.TemporaryDirectory() as td:
            selector = Path(td) / "selector.json"
            with self.assertRaises(AssertionError):
                with self.assertRaisesRegex(SystemExit, "TRACKED selector path"):
                    self.publish(td, None, lambda sid: selector, manifest_path=selector,
                                 stop=lambda message: None)
            self.assertTrue(selector.exists())


if __name__ == "__main__":
    unittest.main()
