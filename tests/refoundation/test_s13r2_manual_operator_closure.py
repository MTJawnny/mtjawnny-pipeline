"""S13.R2 — manual operator closure: nine operator surfaces, permanent owners, shells.

WHAT MOVED, AND WHERE
---------------------
* `foundry_authority`       CLI, six commands        -> `mtj_foundry.authority_cli`
* `foundry_cr`              edition report + CLI     -> `mtj_foundry.cr_edition_report`
* `foundry_cr_edition_diff` parse/compare/report/CLI -> `mtj_foundry.cr_edition_diff_report`
* `foundry_cr702_classes`   class report, homes, CLI -> `mtj_foundry.cr702_report`
* `validate_slug`           CLI (batch + per-slug)   -> `mtj_foundry.slug_report`
* `foundry_locality`        --report/--census, CLI   -> `mtj_foundry.locality_report`
* `foundry_object_lattice`  modes, audit, packet     -> `mtj_foundry.object_lattice_report`
* `foundry_det_pass`        generate/apply, CLI      -> `mtj_foundry.det_pass_job`
* `foundry_shape_extractor` census aggregation/text  -> `mtj_foundry.shape_report`
  (its argparse surface, both `--json` writes and the coverage read stay in the
  shell because committed guards pin them there)

Every shell keeps what only it knows -- paths, reads, writes, backups, the
corpus load, halting semantic wrappers, the historic `STOP — …` -- and hands it
over as call-time callables.

WHAT IS PROVED HERE
-------------------
1. Each shell entry point reaches its permanent owner at call time.
2. No shell regrows the moved composition (each rigged regrowth is RED).
3. The permanent operators are composition: exact imports; no legacy/AQ4
   import; no `__file__`/root/layout derivation; no process exit; no
   subprocess; no redefinition of an accepted semantic owner's function.
4. Declared refusals still STOP, unexpected errors are not swallowed into one,
   and the `cr702 --unstated` KeyError debt is conserved.
5. The authority operator reaches remotes ONLY through the boundary's
   transport factory; the shell carries no parser and no command logic.
6. No R2 operator is an installed script; the package graph stays acyclic.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import io
import json
import re
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest import mock

from tests.refoundation.helpers import REPO_ROOT, SRC
from tests.refoundation.test_gate2_purity import EXPERIMENTS, load_legacy
import tests.refoundation.test_s11_codebook_kernel as s11

from mtj_foundry import (authority_cli, authority_transport, cr702_report,
                         cr_edition_diff_report, cr_edition_report, det_pass_job,
                         locality_report, object_lattice_report, shape_report,
                         slug_report)

PKG = SRC / "mtj_foundry"

# name -> (permanent imports, stdlib imports), measured at the R2 candidate.
R2_OPERATORS = {
    "authority_cli": ({"mtj_foundry.authority", "mtj_foundry.authority_restore",
                       "mtj_foundry.authority_status", "mtj_foundry.codebook_store"},
                      {"__future__", "argparse", "dataclasses", "datetime", "pathlib",
                       "tempfile", "typing"}),
    "cr_edition_report": ({"mtj_foundry.mtg.cr.edition"},
                          {"__future__", "argparse", "dataclasses", "pathlib", "re", "typing"}),
    "cr_edition_diff_report": (set(), {"__future__", "argparse", "collections", "dataclasses",
                                       "difflib", "pathlib", "re", "typing"}),
    "cr702_report": ({"mtj_foundry.mtg.cr.keywords"},
                     {"__future__", "argparse", "collections", "dataclasses", "json",
                      "pathlib", "typing"}),
    "slug_report": (set(), {"__future__", "dataclasses", "json", "pathlib", "typing"}),
    "locality_report": (set(), {"__future__", "argparse", "collections", "dataclasses",
                                "json", "pathlib", "typing"}),
    "shape_report": (set(), {"__future__", "collections", "re"}),
    "object_lattice_report": (set(), {"__future__", "argparse", "collections", "dataclasses",
                                      "random", "re", "typing"}),
    "det_pass_job": ({"mtj_foundry.codebook_det_apply"},
                     {"__future__", "argparse", "dataclasses", "datetime", "json", "pathlib",
                      "random", "typing"}),
}

# Semantic owners whose function names an operator module may not redefine.
SEMANTIC_OWNER_PREFIXES = ("mtg/", "codebook", "authority.py", "authority_transport.py",
                           "authority_status.py", "authority_restore.py", "corpus.py",
                           "oracle_text.py")


def _captured(fn, *args, **kwargs):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            value, code = fn(*args, **kwargs), None
        except SystemExit as exc:
            value, code = None, exc.code
    return value, code, out.getvalue(), err.getvalue()


# ===========================================================================
# 1. each shell reaches its owner at call time
# ===========================================================================

class TestShellsReachTheirOwnersAtCallTime(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.auth = load_legacy("foundry_authority")
        cls.cr = load_legacy("foundry_cr")
        cls.diff = load_legacy("foundry_cr_edition_diff")
        cls.k702 = load_legacy("foundry_cr702_classes")
        cls.slug = load_legacy("validate_slug")
        cls.loc = load_legacy("foundry_locality")
        cls.lat = load_legacy("foundry_object_lattice")
        cls.det = load_legacy("foundry_det_pass")
        cls.shape = load_legacy("foundry_shape_extractor")

    def sentinel(self, *a, **k):
        return "REPLACED"

    def test_every_main_delegates_to_its_operator_run(self):
        for shell, owner in ((self.auth, authority_cli), (self.cr, cr_edition_report),
                             (self.diff, cr_edition_diff_report), (self.k702, cr702_report),
                             (self.slug, slug_report), (self.loc, locality_report),
                             (self.lat, object_lattice_report), (self.det, det_pass_job)):
            calls = []

            def recorder(argv, ctx, calls=calls):
                calls.append((argv, type(ctx).__name__))
                return 0
            with self.subTest(shell=shell.__name__), \
                    mock.patch.object(owner, "run", recorder), \
                    mock.patch("sys.argv", ["shell"]):
                _captured(shell.main)
                self.assertEqual(len(calls), 1)
                self.assertTrue(calls[0][1].endswith("Context"), calls)

    def test_named_entry_points_delegate(self):
        cases = (
            (authority_cli, "cmd_status", lambda: self.auth.cmd_status(argparse.Namespace())),
            (authority_cli, "cmd_restore", lambda: self.auth.cmd_restore(argparse.Namespace())),
            (cr_edition_diff_report, "parse_rules", lambda: self.diff.parse_rules("x")),
            (locality_report, "cmd_report", lambda: self.loc.cmd_report({})),
            (object_lattice_report, "audit", lambda: self.lat.audit("destroy", set())),
            (object_lattice_report, "exclusivity_report", lambda: self.lat.exclusivity_report({})),
            (det_pass_job, "cmd_apply", lambda: self.det.cmd_apply("v.json")),
            (det_pass_job, "cmd_generate_samples", lambda: self.det.cmd_generate_samples()),
        )
        for owner, name, call in cases:
            with self.subTest(owner=owner.__name__, name=name), \
                    mock.patch.object(owner, name, self.sentinel):
                self.assertEqual(call(), "REPLACED")

    def test_render_and_report_lines_delegate(self):
        with mock.patch.object(locality_report, "render_unaddressed_md",
                               lambda rows, totals, generated_by: generated_by):
            self.assertEqual(self.loc.render_unaddressed_md([], {}),
                             "experiments/foundry_locality.py --report")
        with mock.patch.object(cr_edition_report, "report_lines", lambda ctx: iter(["REPLACED"])):
            _, _, out, _ = _captured(self.cr._report)
        self.assertEqual(out, "REPLACED\n")

    def test_shape_censuses_delegate(self):
        args = argparse.Namespace(action="investigate", limit=3, json=None)
        actions = {"investigate": {"cr": "701.36", "kind": "keyword action", "forms": ["investigate"]}}
        with mock.patch.object(self.shape, "scan", lambda *a: []), \
                mock.patch.object(shape_report, "action_lines", lambda *a: ["REPLACED"]):
            _, code, out, _ = _captured(self.shape.cmd_action, args, {}, {}, actions)
        self.assertEqual((code, out), (None, "REPLACED\n"))
        with mock.patch.object(shape_report, "unknown_action_message", lambda *a: "no such term"):
            _, code, out, err = _captured(self.shape.cmd_action, args, {}, {}, actions)
        self.assertEqual((code, err), (1, "STOP — no such term\n"))


# ===========================================================================
# 2. no shell regrows the composition
# ===========================================================================

REGROWTH_MARKERS = {
    "foundry_authority.py": {"cmd_status": ("C6 AUTHORITY STATUS",), "cmd_publish": ("DRY RUN",),
                             "cmd_restore": ("RESTORE HALTED", "restore_snapshot"),
                             "cmd_verify_remote": ("codebook validation",),
                             "main": ("add_parser", "add_argument", "ArgumentParser")},
    "foundry_cr.py": {"_report": ("DECLARED ENCODING DAMAGE", "rule-numbered"),
                      "main": ("ArgumentParser",)},
    "foundry_cr_edition_diff.py": {"main": ("BYTE-IDENTICAL", "ArgumentParser", "unified_diff"),
                                   "parse_rules": ("RULE_LINE.match", "parsed twice")},
    "foundry_cr702_classes.py": {"main": ("AS THE CR WORDS IT", "UNSTATED --", "ArgumentParser"),
                                 "cmd_homes": ("NOT ROUTED", "home_descriptor")},
    "validate_slug.py": {"main": ("validated ", "--batch", "json.dumps")},
    "foundry_locality.py": {"cmd_report": ("determinism gate FAILED", "reporter disagreement"),
                            "render_unaddressed_md": ("SEMANTIC LOCALITY",),
                            "main": ("locality census", "ArgumentParser")},
    "foundry_object_lattice.py": {"main": ("RESIDUAL INVARIANT FAILED", "ArgumentParser"),
                                  "audit": ("nc1_no_verb",),
                                  "exclusivity_report": ("exclusive_pairs",),
                                  "write_report": ("sample sheet for ratification",
                                                   "proposed_det_patterns")},
    "foundry_det_pass.py": {"cmd_apply": ("sample-sheet gate", "write_codebook_atomic"),
                            "cmd_generate_samples": ("sample-sheet review report",),
                            "det_locality_owner": ("no card",),
                            "main": ("add_parser",)},
    "foundry_shape_extractor.py": {"cmd_gaps": ("spell-or-static",),
                                   "cmd_action": ("buildable now", "UNRATIFIED"),
                                   "cmd_rank": ("NO AXIS", "blocked")},
}


def regrowth_violations(source: str, markers: dict) -> list:
    tree = ast.parse(source)
    defs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    found = []
    for fn, needles in markers.items():
        if fn not in defs:
            found.append(f"{fn} missing")
            continue
        node = defs[fn]
        body = [x for x in node.body if not (isinstance(x, ast.Expr)
                                            and isinstance(x.value, ast.Constant))]
        text = "\n".join(ast.unparse(x) for x in body)
        found += [f"{fn}: {n}" for n in needles if n in text]
    return found


class TestNoShellRegrowsTheComposition(unittest.TestCase):

    def test_every_shell_is_reduced(self):
        for name, markers in REGROWTH_MARKERS.items():
            with self.subTest(shell=name):
                self.assertEqual(regrowth_violations(
                    (EXPERIMENTS / name).read_text(encoding="utf-8"), markers), [])

    def test_the_authority_shell_holds_no_parser_and_only_delegating_commands(self):
        tree = ast.parse((EXPERIMENTS / "foundry_authority.py").read_text(encoding="utf-8"))
        self.assertNotIn("argparse", s11._imports(tree))
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith("cmd_"):
                with self.subTest(command=node.name):
                    self.assertEqual(ast.unparse(node.body[-1]),
                                     f"return _stop_on_refusal(_cli.{node.name}, args, _context())")
                    self.assertEqual(len(node.body), 1)

    def test_CONTROL_a_regrown_report_is_caught(self):
        source = (EXPERIMENTS / "foundry_locality.py").read_text(encoding="utf-8")
        anchor = "    return _report.cmd_report(cards, _context())"
        self.assertIn(anchor, source)
        rigged = source.replace(anchor, '    print("determinism gate FAILED")\n' + anchor)
        self.assertEqual(regrowth_violations(rigged, REGROWTH_MARKERS["foundry_locality.py"]),
                         ["cmd_report: determinism gate FAILED"])

    def test_CONTROL_an_authority_command_with_logic_is_caught(self):
        source = (EXPERIMENTS / "foundry_authority.py").read_text(encoding="utf-8")
        anchor = "def cmd_verify(args) -> int:\n"
        self.assertIn(anchor, source)
        rigged = source.replace(anchor, anchor + "    print('C6 AUTHORITY STATUS')\n")
        tree = ast.parse(rigged)
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "cmd_verify")
        self.assertNotEqual(len(node.body), 1)


# ===========================================================================
# 3. the permanent operators are composition
# ===========================================================================

def _semantic_owner_function_names() -> set:
    names = set()
    for path in PKG.rglob("*.py"):
        if path.relative_to(PKG).as_posix().startswith(SEMANTIC_OWNER_PREFIXES):
            names |= {n.name for n in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
                      if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and not n.name.startswith("_")}
    return names


def operator_violations(name: str, source: str, semantic_names: set) -> list:
    tree = ast.parse(source)
    got = s11._imports(tree)
    internal, stdlib = R2_OPERATORS[name]
    permanent = {m for m in got if m.startswith("mtj_foundry.")}
    permanent = {m for m in permanent if not any(o.startswith(m + ".") for o in permanent)}
    permanent = {m for m in permanent if m.rsplit(".", 1)[0] not in permanent}
    v = []
    if permanent != internal:
        v.append(f"permanent imports {sorted(permanent)}")
    external = {m for m in got if not m.startswith("mtj_foundry")}
    if external != stdlib:
        v.append(f"external imports {sorted(external)}")
    if {m for m in got if m.startswith(("foundry_", "experiments", "aq4", "tier_engine",
                                        "validate_slug", "subprocess"))}:
        v.append("legacy, AQ4 or subprocess import")
    calls = {ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)}
    for forbidden in ("sys.exit", "exit", "quit", "os._exit", "os.system", "RcloneTransport",
                      "default_runner", "Path.home", "Path.cwd"):
        if forbidden in calls:
            v.append(f"calls {forbidden}")
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {
        n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    for forbidden in ("__file__", "SystemExit", "ProjectPaths", "parents"):
        if forbidden in names:
            v.append(f"names {forbidden}")
    docstrings = {id(n.body[0].value) for n in ast.walk(tree)
                  if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and n.body
                  and isinstance(n.body[0], ast.Expr)}
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) \
                and id(node) not in docstrings \
                and re.search(r"experiments[/\\]|\barchive[/\\]|\bout[/\\]foundry", node.value):
            v.append(f"layout literal {node.value[:40]!r}")
    defs = {n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    for clash in sorted(defs & semantic_names):
        v.append(f"redefines semantic owner function {clash}")
    return v


class TestThePermanentOperatorsAreComposition(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.semantic = _semantic_owner_function_names()

    def source(self, name):
        return (PKG / f"{name}.py").read_text(encoding="utf-8")

    def test_every_operator_is_composition_only(self):
        for name in R2_OPERATORS:
            with self.subTest(module=name):
                self.assertEqual(operator_violations(name, self.source(name), self.semantic), [])

    def test_CONTROL_a_root_derivation_is_caught(self):
        rigged = self.source("locality_report").replace(
            "from __future__ import annotations\n",
            "from __future__ import annotations\nfrom pathlib import Path\n"
            "ROOT = Path(__file__).resolve().parents[2]\n"
            "OUT = ROOT / 'experiments/out/foundry'\n")
        v = operator_violations("locality_report", rigged, self.semantic)
        self.assertIn("names __file__", v)
        self.assertTrue(any(x.startswith("layout literal") for x in v))

    def test_CONTROL_a_legacy_import_and_an_exit_are_caught(self):
        rigged = self.source("cr702_report") + (
            "\nimport foundry_common as fc\n\ndef bail():\n    fc.halt('x')\n"
            "    raise SystemExit(1)\n")
        v = operator_violations("cr702_report", rigged, self.semantic)
        self.assertIn("legacy, AQ4 or subprocess import", v)
        self.assertIn("names SystemExit", v)

    def test_CONTROL_a_copied_semantic_function_is_caught(self):
        rigged = self.source("cr702_report") + (
            "\n\ndef keyword_rows(path):\n    return []\n")
        self.assertIn("redefines semantic owner function keyword_rows",
                      operator_violations("cr702_report", rigged, self.semantic))

    def test_CONTROL_a_direct_remote_transport_is_caught(self):
        rigged = self.source("authority_cli") + (
            "\n\ndef leak(ctx):\n    import subprocess\n"
            "    return RcloneTransport('r2foundry-rw', runner=default_runner)\n")
        v = operator_violations("authority_cli", rigged, self.semantic)
        self.assertIn("calls RcloneTransport", v)
        self.assertIn("legacy, AQ4 or subprocess import", v)

    def test_nothing_below_the_operators_imports_them(self):
        operators = {f"mtj_foundry.{n}" for n in R2_OPERATORS}
        for path in sorted(PKG.rglob("*.py")):
            if path.stem in R2_OPERATORS:
                continue
            with self.subTest(module=path.relative_to(PKG).as_posix()):
                self.assertEqual(s11._imports(ast.parse(path.read_text(encoding="utf-8")))
                                 & operators, set())

    def test_the_package_graph_is_acyclic(self):
        self.assertEqual(s11.find_cycle(s11.package_graph(PKG)), [])

    def test_CONTROL_an_operator_import_from_below_is_a_cycle(self):
        g = s11.package_graph(PKG)
        g["mtj_foundry.codebook_det_apply"] = set(g["mtj_foundry.codebook_det_apply"]) | {
            "mtj_foundry.det_pass_job"}
        self.assertIn("mtj_foundry.det_pass_job", s11.find_cycle(g))

    def test_operators_import_with_only_src_from_an_unrelated_cwd(self):
        import subprocess
        import sys
        code = ("import sys\n"
                + "".join(f"import mtj_foundry.{n}\n" for n in sorted(R2_OPERATORS))
                + "print(sorted(m for m in sys.modules if m.startswith(('foundry_', "
                  "'experiments', 'validate_slug', 'tier_engine'))))\n")
        with tempfile.TemporaryDirectory() as td:
            res = subprocess.run([sys.executable, "-c", code], cwd=td, capture_output=True,
                                 text=True, env={"PATH": "/usr/bin:/bin", "PYTHONPATH": str(SRC)})
        self.assertEqual((res.returncode, res.stdout.strip()), (0, "[]"), res.stderr)

    def test_no_operator_is_an_installed_script(self):
        scripts = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
            "project"]["scripts"]
        targets = {t.split(":")[0] for t in scripts.values()}
        self.assertEqual(targets & {f"mtj_foundry.{n}" for n in R2_OPERATORS}, set())


# ===========================================================================
# 4. refusals, unexpected errors, declared debt
# ===========================================================================

class TestRefusalsAndDebtAreConserved(unittest.TestCase):

    @staticmethod
    def law_unstated_debt(module):
        rows = [{"cr": "702.9", "keyword": "Flying", "cr_classes": ["evasion"],
                 "effective_classes": ["static"], "evidence": "x", "multi": False,
                 "multi_hint_unresolved": False, "delivery": ["static"]}]
        ctx = module.Cr702Context(cr_path=Path("/cr.md"), load_702=lambda p: {9: {}},
                                  keyword_rows=lambda p: rows, homes=lambda r, k: None)
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                module.run(["--unstated"], ctx)
        except KeyError as error:
            assert error.args == ("cr_class",), error.args
            assert out.getvalue().rstrip().endswith("=" * 78), out.getvalue()[-200:]
        else:
            raise AssertionError("the declared --unstated KeyError debt no longer raises")

    def test_cr702_unstated_keyerror_debt_is_conserved(self):
        self.law_unstated_debt(cr702_report)

    def test_CONTROL_a_repaired_unstated_is_caught(self):
        import types
        source = (PKG / "cr702_report.py").read_text(encoding="utf-8")
        anchor = '            if r["cr_class"] is None:'
        self.assertIn(anchor, source)
        import sys
        repaired = types.ModuleType("repaired_cr702_report")
        with mock.patch.dict(sys.modules, {"repaired_cr702_report": repaired}):
            exec(compile(source.replace(anchor, '            if not r["cr_classes"]:'),
                         "repaired_cr702_report", "exec"), repaired.__dict__)
            with self.assertRaises(AssertionError):
                self.law_unstated_debt(repaired)

    def test_declared_stops_stay_stops_and_unexpected_errors_propagate(self):
        stops = []

        def stop(message):
            stops.append(message)
            raise SystemExit(1)

        diff_ctx = cr_edition_diff_report.CrEditionDiffContext(
            cr_path=Path("/new.md"), prior_cr_path=Path("/prior.md"),
            prior_exists=lambda: False, text=lambda p: "", effective_date=lambda t: "",
            parse_rules=lambda t: {}, guard_rule_pattern=lambda: None, stop=stop)
        with self.assertRaises(SystemExit):
            cr_edition_diff_report.run([], diff_ctx)
        self.assertIn("cannot be verified as a COMPARISON", stops[-1])

        def broken(p):
            raise ValueError("unexpected")
        broken_ctx = cr_edition_diff_report.CrEditionDiffContext(
            cr_path=Path("/new.md"), prior_cr_path=Path("/prior.md"),
            prior_exists=lambda: True, text=broken, effective_date=lambda t: "",
            parse_rules=lambda t: {}, guard_rule_pattern=lambda: None, stop=stop)
        with self.assertRaises(ValueError):
            cr_edition_diff_report.run([], broken_ctx)

        with self.assertRaisesRegex(cr_edition_diff_report.RuleParseError, "parsed zero rules"):
            cr_edition_diff_report.parse_rules("no rules\n")

    def test_locality_disagreement_stops_before_any_write(self):
        written = []

        def stop(message):
            raise SystemExit(message)
        ctx = locality_report.LocalityReportContext(
            description="", report_help="", generated_by="g", load_cards=lambda: {},
            census=lambda cards: {"assertions": 3, "owned": 1, "span": 0, "ambiguous": 0},
            unaddressed_rows=lambda cards: [], json_path=Path("/j"), md_path=Path("/m"),
            write_json=lambda p, d: written.append(p), write_text=lambda p, t: written.append(p),
            stop=stop)
        with self.assertRaisesRegex(SystemExit, "reporter disagreement"):
            locality_report.cmd_report({}, ctx)
        self.assertEqual(written, [])

    def test_det_apply_without_a_cache_stops_before_reading_anything(self):
        touched = []

        def stop(message):
            raise SystemExit(message)
        fields = {f.name: (lambda *a, **k: touched.append(a)) for f in
                  det_pass_job.DetPassContext.__dataclass_fields__.values()}
        with tempfile.TemporaryDirectory() as td:
            fields.update(description="", samples_report_path=Path(td) / "s.json",
                          samples_report_md_path=Path(td) / "s.md",
                          hits_cache_path=Path(td) / "absent.json",
                          codebook_path=Path(td) / "codebook.json", stop=stop)
            ctx = det_pass_job.DetPassContext(**fields)
            with self.assertRaisesRegex(SystemExit, "run generate-samples first"):
                det_pass_job.cmd_apply(str(Path(td) / "v.json"), ctx)
        self.assertEqual(touched, [])

    def test_CONTROL_a_swallowed_stop_is_caught(self):
        """The guard above is only a guard if a stop that returns is visible."""
        ctx = locality_report.LocalityReportContext(
            description="", report_help="", generated_by="g", load_cards=lambda: {},
            census=lambda cards: {"assertions": 3, "owned": 1, "span": 0, "ambiguous": 0},
            unaddressed_rows=lambda cards: [], json_path=Path("/j"), md_path=Path("/m"),
            write_json=lambda p, d: None, write_text=lambda p, t: None,
            stop=lambda message: None)
        with self.assertRaises(AssertionError):
            with self.assertRaisesRegex(SystemExit, "reporter disagreement"):
                with contextlib.redirect_stdout(io.StringIO()):
                    locality_report.cmd_report({}, ctx)


# ===========================================================================
# 5. the authority operator is offline-safe through its boundary
# ===========================================================================

class TestAuthorityOperatorBoundary(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.auth = load_legacy("foundry_authority")

    def run_cli(self, argv, runner):
        auth = self.auth

        class Fake(auth.RcloneTransport):
            def __init__(self, remote, bucket=auth.AUTHORITY_BUCKET, runner_=None):
                super().__init__(remote, bucket, runner)

        def real_remote(argv_):
            raise AssertionError(f"a real remote was reached: {argv_[:2]}")

        with mock.patch.object(authority_transport, "default_runner", real_remote), \
                mock.patch.object(auth, "RcloneTransport", Fake), \
                mock.patch("sys.argv", ["foundry_authority.py", *argv]):
            return _captured(auth.main)

    def test_check_remote_goes_through_the_boundary_transport(self):
        runner = self.auth.FakeRunner()
        value, code, out, err = self.run_cli(["status", "--check-remote"], runner)
        self.assertEqual((value, code), (0, None), err)
        self.assertIn("AUTHORITY_UNVERIFIABLE", out)
        self.assertEqual([c[1] for c in runner.calls], ["lsjson"])

    def test_CONTROL_a_transport_that_bypasses_the_factory_reaches_the_rigged_remote(self):
        def real_remote(argv_):
            raise AssertionError("a real remote was reached")
        ctx = self.auth._context()
        leaky = authority_cli.AuthorityOperatorContext(**{
            **{f: getattr(ctx, f) for f in ctx.__dataclass_fields__},
            "transport": lambda remote, bucket: authority_transport.RcloneTransport(
                remote, bucket, None, forbidden_destinations=lambda: set())})
        args = argparse.Namespace(check_remote=True, remote=None, bucket="b", json=False,
                                  candidate=None)
        with mock.patch.object(authority_transport, "default_runner", real_remote):
            with self.assertRaisesRegex(AssertionError, "real remote"):
                with contextlib.redirect_stdout(io.StringIO()):
                    authority_cli.cmd_status(args, leaky)

    def test_refusals_reach_the_process_boundary(self):
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "bad.json"
            bad.write_text(json.dumps({"schema": "foundry-authority/1"}), encoding="utf-8")
            value, code, out, err = self.run_cli(["restore", "--manifest", str(bad),
                                                  "--install-to", str(Path(td) / "cb.json")],
                                                 self.auth.FakeRunner())
        self.assertEqual(code, 1)
        self.assertTrue(err.startswith(f"STOP — {bad} is missing or invalid:"), err)
        self.assertFalse((Path(td) / "cb.json").exists())


if __name__ == "__main__":
    unittest.main()
