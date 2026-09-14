"""S13 (R1) — triage-command retirement and live operator migration.

WHAT S13 CHANGED, AND WHERE
---------------------------
* `.claude/commands/triage-{alpha,beta,emit}.md` -> halt-loud retirement
  tombstones. The SUP batch-triage loop ended at batch 7; its codebook step is
  frozen `/1` provenance tooling (Captain R4/A4) and has no `/2` successor.
* clean-lint report text (Gate 2 row `lint`)  -> `mtj_foundry.lint_report`
* keyword-bucket envelope/report/summary      -> `mtj_foundry.keyword_buckets_job`
  (its artifact is read by three Gate 2 guards)
* CR-checks x2 gate/summary/coverage report   -> `mtj_foundry.cr_checks_job`
  (its tracked artifact is read by the shape extractor Gate 2 guards import)

Each legacy shell kept its reads, writes, output paths, printing, argument
parsing and `STOP — …` boundary, and delegates composition at call time.

WHAT IS PROVED HERE
-------------------
1. The tombstones halt, say what the retirement is, and carry no executable
   route back into the retired loop -- each rigged reintroduction is RED.
2. The frozen `/1` producer is byte-unchanged and still refuses `/2`.
3. No new installed script, and no installed script that can mutate.
4. The migrated operators keep exit status, channels and bytes; an unexpected
   exception is never swallowed into a declared failure; the shell reaches the
   permanent owner at call time; the shell holds no copy of the composition.
5. The new owners are pure composition: exact imports, no I/O, no process
   boundary, no layout or root of their own; the package graph stays acyclic.
"""

from __future__ import annotations

import ast
import contextlib
import hashlib
import io
import json
import re
import subprocess
import sys
import tempfile
import tomllib
import unittest
from argparse import Namespace
from pathlib import Path
from unittest import mock

from tests.refoundation.helpers import REPO_ROOT, SRC
from tests.refoundation.test_gate2_purity import EXPERIMENTS, load_legacy
import tests.refoundation.test_s11_codebook_kernel as s11

from mtj_foundry import codebook, cr_checks_job, keyword_buckets_job, lint_report
from mtj_foundry.mtg.cr import keyword_buckets as _buckets

PKG = SRC / "mtj_foundry"
COMMANDS = REPO_ROOT / ".claude" / "commands"
TRIAGE = ("alpha", "beta", "emit")
RECONCILE = EXPERIMENTS / "foundry_reconcile.py"
# Measured at the accepted S12 head 9d22a8f; S13 must not change it.
RECONCILE_SHA256 = "dfaba058d943c77e498a30c19ca819ce086b3f0b073db2e978b78a075ff86064"

INSTALLED_SCRIPTS = {
    "mtj-foundry-report": "mtj_foundry.cli:main",
    "mtj-foundry-evidence": "mtj_foundry.evidence_cli:main",
    "mtj-foundry-pilot": "mtj_foundry.pilot_cli:main",
}

S13_MODULES = {
    "lint_report": ({"mtj_foundry.codebook"}, {"__future__"}),
    "keyword_buckets_job": ({"mtj_foundry.mtg.cr.keyword_buckets"}, {"__future__"}),
    "cr_checks_job": (set(), {"__future__", "json"}),
}


def _halted(fn, *args, **kwargs):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            fn(*args, **kwargs)
            code = None
        except SystemExit as exc:
            code = exc.code
    return code, out.getvalue(), err.getvalue()


# ===========================================================================
# 1. triage tombstones
# ===========================================================================

TOMBSTONE_REQUIRED = (
    "# RETIRED COMMAND — HALT",
    "is retired and must not perform any work",
    "The SUP batch-triage loop ended at batch 7.",
    "is frozen `/1` provenance tooling by Captain ruling (R4/A4).",
    "It cannot write the live `/2` codebook.",
    "There is no current `/2` batch-triage successor.",
    "Do not run the historical loop as an operational workflow.",
    "are historical evidence, not a live successor.",
)

# An executable route back into the retired loop, a batch submission, a codebook
# write, or archive history offered as a successor. Deliberately lexical: the
# tombstones mention none of these, so a guard that cannot tell an instruction
# from an explanation is never asked to.
TOMBSTONE_FORBIDDEN = (
    r"experiments[/\\]", r"\barchive[/\\]", r"\.py\b", r"reconcil", r"submit", r"batch api",
    r"\$ARGUMENTS", r"codebook\.json", r"decisions[/\\]", r"review[/\\]", r"\bdocs[/\\]",
    r"foundry_", r"tier_engine", r"write_codebook", r"add-member", r"consolidat",
    r"enrich", r"digest", r"stage1b", r"assembl",
)


def _flat(text: str) -> str:
    return re.sub(r"[\s>]+", " ", text)


def tombstone_violations(text: str) -> list:
    v = []
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        v.append("no frontmatter")
    desc = next((line for line in lines if line.startswith("description:")), "")
    if not desc.startswith("description: RETIRED"):
        v.append(f"description does not declare retirement: {desc!r}")
    flat = _flat(text)
    for required in TOMBSTONE_REQUIRED:
        if _flat(required) not in flat:
            v.append(f"missing: {required!r}")
    if not re.search(r"^STOP\. ", text, re.M):
        v.append("no leading STOP instruction")
    for pattern in TOMBSTONE_FORBIDDEN:
        if re.search(pattern, text, re.I):
            v.append(f"forbidden: {pattern}")
    return v


class TestTriageTombstones(unittest.TestCase):

    def text(self, name):
        return (COMMANDS / f"triage-{name}.md").read_text(encoding="utf-8")

    def test_every_triage_command_is_a_halt_loud_tombstone(self):
        for name in TRIAGE:
            with self.subTest(command=name):
                self.assertEqual(tombstone_violations(self.text(name)), [])
                self.assertIn(f"`/triage-{name}` is retired", self.text(name))

    def test_the_command_paths_remain_tracked(self):
        tracked = subprocess.run(["git", "-C", str(REPO_ROOT), "ls-files", ".claude/commands"],
                                 capture_output=True, text=True, check=True).stdout.split()
        self.assertEqual(sorted(tracked), [f".claude/commands/triage-{n}.md" for n in TRIAGE])

    def test_no_command_names_a_legacy_or_archive_operational_path(self):
        for path in sorted(COMMANDS.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            with self.subTest(command=path.name):
                self.assertIsNone(re.search(r"experiments[/\\]|\barchive[/\\]", text))

    def rig(self, old, new):
        text = self.text("emit")
        self.assertIn(old, text, "rig anchor is gone")
        rigged = text.replace(old, new)
        self.assertNotEqual(rigged, text)
        return tombstone_violations(rigged)

    def test_CONTROL_reintroducing_the_batch_loop_is_caught(self):
        v = self.rig("Retirement authority:",
                     "1. Run experiments/foundry_enrich.py --in review/batch-$ARGUMENTS.json\n"
                     "Retirement authority:")
        self.assertTrue(v)

    def test_CONTROL_a_v2_batch_reconcile_instruction_is_caught(self):
        v = self.rig("Retirement authority:",
                     "4. Reconcile the decisions into the live /2 codebook.\nRetirement authority:")
        self.assertIn("forbidden: reconcil", v)

    def test_CONTROL_archive_history_as_a_successor_is_caught(self):
        v = self.rig("There is no current `/2` batch-triage successor.",
                     "The successor is archive/research/triage/; run it from there.")
        self.assertTrue(any("archive" in x for x in v))
        self.assertTrue(any(x.startswith("missing") for x in v))

    def test_CONTROL_a_batch_submission_is_caught(self):
        v = self.rig("Retirement authority:", "Submit the next batch to the Batch API.\nRetirement authority:")
        self.assertIn("forbidden: submit", v)

    def test_CONTROL_weakening_the_halt_is_caught(self):
        for old, new in (("# RETIRED COMMAND — HALT", "# Triage emit"),
                         ("STOP. `/triage-emit`", "Note: `/triage-emit`"),
                         ("description: RETIRED — ", "description: "),
                         ("is retired and must not perform any work", "is mostly retired")):
            with self.subTest(old=old):
                self.assertTrue(self.rig(old, new))


class TestTheFrozenV1ProducerIsUntouched(unittest.TestCase):

    @staticmethod
    def refusal_violations(source: str) -> list:
        v = []
        for needle in ("FROZEN /1 LEGACY PRODUCER",
                       "refuses to write the live",
                       "if Path(path).resolve() == LIVE_CODEBOOK_PATH.resolve():",
                       'SCHEMA_V1 = "foundry-codebook/1"'):
            if needle not in source:
                v.append(needle)
        return v

    def test_reconcile_is_byte_identical_to_the_accepted_head(self):
        self.assertEqual(hashlib.sha256(RECONCILE.read_bytes()).hexdigest(), RECONCILE_SHA256)

    def test_reconcile_still_refuses_the_live_v2_codebook(self):
        self.assertEqual(self.refusal_violations(RECONCILE.read_text(encoding="utf-8")), [])

    def test_CONTROL_a_reconcile_that_accepts_v2_is_caught(self):
        source = RECONCILE.read_text(encoding="utf-8").replace(
            "if Path(path).resolve() == LIVE_CODEBOOK_PATH.resolve():", "if False:")
        self.assertTrue(self.refusal_violations(source))
        self.assertNotEqual(hashlib.sha256(source.encode()).hexdigest(), RECONCILE_SHA256)


# ===========================================================================
# 2. installed command surface
# ===========================================================================

MUTATING_NAMES = ("write_atomic", "write_codebook_atomic", "put_immutable", "restore_snapshot",
                  "install_atomic", "authority_transport", "authority_restore", "merge_assertion",
                  "backup_codebook")


def installed_script_violations(pyproject_text: str) -> list:
    scripts = tomllib.loads(pyproject_text)["project"].get("scripts", {})
    v = []
    if scripts != INSTALLED_SCRIPTS:
        v.append(f"installed scripts changed: {scripts}")
    for name, target in scripts.items():
        module = target.split(":")[0]
        path = SRC / (module.replace(".", "/") + ".py")
        if not path.exists():
            v.append(f"{name}: {module} does not exist")
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        used = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)} | {
            n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | s11._imports(tree)
        hit = sorted(x for x in used for m in MUTATING_NAMES if x.split(".")[-1] == m)
        if hit:
            v.append(f"{name}: reaches a mutating owner {hit}")
    return v


class TestNoNewInstalledMutatingCommand(unittest.TestCase):

    def test_the_installed_scripts_are_the_three_read_only_ones(self):
        self.assertEqual(installed_script_violations(
            (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")), [])

    def test_CONTROL_a_new_installed_mutating_script_is_caught(self):
        text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        rigged = text.replace('mtj-foundry-report = "mtj_foundry.cli:main"',
                              'mtj-foundry-report = "mtj_foundry.cli:main"\n'
                              'mtj-foundry-member-add = "mtj_foundry.codebook_store:write_atomic"')
        self.assertNotEqual(rigged, text)
        self.assertTrue(installed_script_violations(rigged))


# ===========================================================================
# 3. lint report (Gate 2 row `lint`)
# ===========================================================================

CODEBOOK_SHELL = EXPERIMENTS / "foundry_codebook.py"


def _run_lint(*args, cwd=None):
    return subprocess.run([sys.executable, str(CODEBOOK_SHELL), "lint", *args], capture_output=True,
                          text=True, cwd=cwd or tempfile.gettempdir())


class TestLintReport(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fcb = load_legacy("foundry_codebook")

    def test_the_report_lines(self):
        key = ("rule:x", "some-invariant")
        with mock.patch.dict(codebook.AXIS_INVARIANT_EXEMPTIONS, {key: "because ratified"}):
            got = lint_report.lines(Path("/c/codebook.json"),
                                    {"axes": 2, "members": 3, "assertions": 4,
                                     "exemptions_applied": [key]})
        self.assertEqual(got, [
            "lint clean: 2 axes, 3 members, 4 assertions — /c/codebook.json",
            "  DECLARED EXEMPTION APPLIED — rule:x: some-invariant",
            "    because ratified"])

    def test_the_shell_reaches_the_report_owner_at_call_time(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "cb.json"
            path.write_text(json.dumps({"schema": codebook.SCHEMA_V2, "version": "0.7", "axes": {}}),
                            encoding="utf-8")
            with mock.patch.object(lint_report, "lines", lambda p, s: ["REPLACED"]):
                code, out, err = _halted(self.fcb.cmd_lint, Namespace(path=str(path)))
        self.assertEqual((code, out, err), (None, "REPLACED\n", ""))

    def law_process_boundary(self, run):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            good = td / "good.json"
            good.write_text(json.dumps({"schema": codebook.SCHEMA_V2, "version": "0.7", "axes": {}}),
                            encoding="utf-8")
            bad = td / "bad.json"
            bad.write_text(json.dumps({"schema": codebook.SCHEMA_V2, "version": "0.7", "axes": {
                "rule:x": {"status": "bogus", "members": []}}}), encoding="utf-8")
            broken = td / "broken.json"
            broken.write_text("{{", encoding="utf-8")
            ok = run(str(good))
            assert (ok.returncode, ok.stdout, ok.stderr) == (
                0, f"lint clean: 0 axes, 0 members, 0 assertions — {good}\n", ""), ok
            fail = run(str(bad))
            assert fail.returncode == 1 and fail.stdout == "" and fail.stderr.startswith("STOP — "), fail
            unexpected = run(str(broken))
            assert unexpected.returncode == 1 and "JSONDecodeError" in unexpected.stderr, unexpected
            assert "Traceback" in unexpected.stderr and not unexpected.stderr.startswith("STOP"), unexpected
            missing = run(str(td / "absent.json"))
            assert missing.returncode == 1 and missing.stderr == f"STOP — {td / 'absent.json'} not found\n"

    def test_exit_status_channels_and_bytes_are_conserved(self):
        self.law_process_boundary(lambda p: _run_lint("--path", p))

    def test_CONTROL_a_report_on_the_wrong_channel_is_caught(self):
        def rigged(p):
            r = _run_lint("--path", p)
            return subprocess.CompletedProcess(r.args, r.returncode, "", r.stdout + r.stderr)
        with self.assertRaises(AssertionError):
            self.law_process_boundary(rigged)

    def test_CONTROL_an_unexpected_error_swallowed_into_a_stop_is_caught(self):
        def rigged(p):
            r = _run_lint("--path", p)
            if "Traceback" in r.stderr:
                return subprocess.CompletedProcess(r.args, 1, "", "STOP — could not read\n")
            return r
        with self.assertRaises(AssertionError):
            self.law_process_boundary(rigged)


# ===========================================================================
# 4. keyword-bucket job
# ===========================================================================

KB_SHELL = EXPERIMENTS / "foundry_keyword_buckets.py"


class _FrozenDate:
    @staticmethod
    def today():
        return type("D", (), {"isoformat": lambda self: "2026-01-02"})()


class TestKeywordBucketsJob(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.kb = load_legacy("foundry_keyword_buckets")
        cls.registry = cls.kb.build_registry()

    def run_job(self, td, name="out"):
        d = Path(td) / name
        d.mkdir()
        with mock.patch.multiple(self.kb, OUT_PATH=d / "keyword-buckets.json",
                                 REPORT_PATH=d / "keyword-buckets_report.md", date=_FrozenDate):
            code, out, err = _halted(self.kb.main)
        return code, out, err, {p.name: p.read_bytes() for p in sorted(d.iterdir())}

    def test_the_envelope_key_order_and_values(self):
        env = keyword_buckets_job.envelope(self.registry, "2026-01-01", "/cr.md", "2026-01-02")
        self.assertEqual(list(env), ["schema", "cr_version_date", "cr_source_path", "generated",
                                     "ruling_basis", "closed_buckets", "note", "keywords"])
        self.assertEqual(env["schema"], "foundry-keyword-buckets/1")
        self.assertIs(env["keywords"], self.registry["keywords"])

    def law_deterministic_job(self, run):
        with tempfile.TemporaryDirectory() as td:
            first, second = run(td, "a"), run(td, "b")
        assert first[0] is None and first[2] == "", first[:3]
        assert set(first[3]) == {"keyword-buckets.json", "keyword-buckets_report.md"}
        norm = [{k: v.replace(str(Path(td)).encode(), b"") for k, v in r[3].items()} for r in (first, second)]
        assert norm[0]["keyword-buckets_report.md"].replace(b"/a/", b"/") == \
            norm[1]["keyword-buckets_report.md"].replace(b"/b/", b"/")
        assert norm[0]["keyword-buckets.json"] == norm[1]["keyword-buckets.json"]
        return first

    def test_the_job_is_byte_deterministic_and_writes_what_the_owner_renders(self):
        code, out, err, files = self.law_deterministic_job(self.run_job)
        doc = json.loads(files["keyword-buckets.json"])
        self.assertEqual(doc, json.loads(json.dumps(keyword_buckets_job.envelope(
            self.registry, doc["cr_version_date"], str(self.kb.CR_PATH), "2026-01-02"))))
        self.assertEqual(files["keyword-buckets_report.md"].decode(), keyword_buckets_job.report(
            self.registry, doc["cr_version_date"], str(self.kb.CR_PATH), "2026-01-02"))
        self.assertEqual(out.splitlines()[2:], keyword_buckets_job.summary("x", "y", self.registry)[2:])

    def test_CONTROL_a_nondeterministic_report_is_caught(self):
        counter = {"n": 0}
        real = keyword_buckets_job.report

        def drifting(*a, **k):
            counter["n"] += 1
            return real(*a, **k) + ("x" * counter["n"])
        with mock.patch.object(keyword_buckets_job, "report", drifting):
            with self.assertRaises(AssertionError):
                self.law_deterministic_job(self.run_job)

    def test_the_shell_reaches_the_job_owner_at_call_time(self):
        with mock.patch.object(keyword_buckets_job, "summary", lambda *a: ["REPLACED"]), \
                tempfile.TemporaryDirectory() as td:
            code, out, err, files = self.run_job(td)
        self.assertEqual((code, out), (None, "REPLACED\n"))

    def test_a_derivation_failure_is_not_converted(self):
        def boom(*a, **k):
            raise ValueError("unexpected")
        with mock.patch.object(_buckets, "build_registry", boom), tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                self.run_job(td)


# ===========================================================================
# 5. CR-checks job
# ===========================================================================

CR_SHELL = EXPERIMENTS / "foundry_cr_checks.py"
TRACKED_CR_CHECKS = REPO_ROOT / "config" / "generated" / "cr-checks.json"


class TestCrChecksJob(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cc = load_legacy("foundry_cr_checks")

    def test_gated_serialization(self):
        reg = {"b": 1, "a": [2]}
        self.assertEqual(cr_checks_job.gated_serialization(reg, lambda: {"a": [2], "b": 1}),
                         json.dumps(reg, indent=1, sort_keys=True))
        with self.assertRaisesRegex(cr_checks_job.DeterminismError,
                                    "^determinism gate FAILED — two builds of the registry differ$"):
            cr_checks_job.gated_serialization(reg, lambda: {"a": [3], "b": 1})

        def fails():
            raise ValueError("rebuild failed")
        with self.assertRaises(ValueError):
            cr_checks_job.gated_serialization(reg, fails)

    def test_summary_and_coverage_lines(self):
        reg = {"n_terms": 3, "terms": [{"kind": "zeta"}, {"kind": "alpha"}, {"kind": "zeta"}]}
        self.assertEqual(cr_checks_job.summary("OUT", reg), [
            "wrote OUT  (3 terms, determinism x2 OK)", "  alpha            1", "  zeta             2"])
        got = cr_checks_job.coverage_lines(10, [(25, "fight", "701.14"), (19, "exile", "701.5")])
        self.assertEqual(got[:3], ["CR keyword actions        : 10", "  modelled by some axis   : 8",
                                   "  NO axis token           : 2"])
        self.assertIn("        25  fight                        CR 701.14", got)
        self.assertFalse([line for line in got if "exile" in line])

    def run_main(self, td, argv=(), **patches):
        out_path = Path(td) / "cr-checks.json"
        with mock.patch.multiple(self.cc, OUT=out_path, **patches), \
                mock.patch.object(sys, "argv", ["foundry_cr_checks.py", *argv]):
            code, out, err = _halted(self.cc.main)
        return code, out, err, out_path

    def test_the_job_reproduces_the_tracked_registry_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as td:
            code, out, err, path = self.run_main(td)
            self.assertEqual((code, err), (None, ""))
            self.assertEqual(path.read_bytes(), TRACKED_CR_CHECKS.read_bytes())
            self.assertTrue(out.startswith(f"wrote {path}  ("))

    def law_determinism_halt(self, main_result):
        code, out, err, path = main_result
        assert code == 1, code
        assert err == "STOP — determinism gate FAILED — two builds of the registry differ\n", err
        assert not path.exists(), "an ungated artifact was written"

    def test_a_nondeterministic_build_halts_before_writing(self):
        real = self.cc.build
        calls = {"n": 0}

        def drifting(cr):
            calls["n"] += 1
            reg = real(cr)
            reg["n_terms"] += calls["n"]
            return reg
        with tempfile.TemporaryDirectory() as td:
            self.law_determinism_halt(self.run_main(td, build=drifting))

    def test_CONTROL_a_gate_that_lets_drift_through_is_caught(self):
        real = self.cc.build
        calls = {"n": 0}

        def drifting(cr):
            calls["n"] += 1
            reg = real(cr)
            reg["n_terms"] += calls["n"]
            return reg
        with mock.patch.object(cr_checks_job, "gated_serialization",
                               lambda reg, rebuild: json.dumps(reg, indent=1, sort_keys=True)), \
                tempfile.TemporaryDirectory() as td:
            with self.assertRaises(AssertionError):
                self.law_determinism_halt(self.run_main(td, build=drifting))

    def test_a_failed_rebuild_is_not_swallowed_into_the_determinism_stop(self):
        real = self.cc.build
        calls = {"n": 0}

        def second_fails(cr):
            calls["n"] += 1
            if calls["n"] == 2:
                raise ValueError("rebuild failed")
            return real(cr)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                self.run_main(td, build=second_fails)

    def test_the_shell_reaches_the_job_owner_at_call_time(self):
        with mock.patch.object(cr_checks_job, "summary", lambda *a: ["REPLACED"]), \
                tempfile.TemporaryDirectory() as td:
            code, out, err, path = self.run_main(td)
        self.assertEqual((code, out), (None, "REPLACED\n"))


# ===========================================================================
# 6. the shells hold no copy of the composition
# ===========================================================================

SHELL_COPY_MARKERS = {
    CODEBOOK_SHELL: ("cmd_lint", ("lint clean:", "DECLARED EXEMPTION APPLIED")),
    KB_SHELL: ("main", ("foundry-keyword-buckets/1", "## Bucket counts", "Verify-or-drop",
                        "casting_modifier_heuristic hits", "bucket counts:")),
    CR_SHELL: ("main", ("determinism gate FAILED", "determinism x2 OK", "json.dumps")),
}
CR_COVERAGE_MARKERS = ("CR keyword actions", "modelled by some axis", "worklist to verify")


def shell_copy_violations(source: str, function: str, markers) -> list:
    fn = next((n for n in ast.parse(source).body
               if isinstance(n, ast.FunctionDef) and n.name == function), None)
    if fn is None:
        return [f"{function} missing"]
    body = ast.unparse(fn)
    return [m for m in markers if m in body]


class TestTheShellsDelegateComposition(unittest.TestCase):

    def test_no_shell_carries_the_moved_composition(self):
        for path, (function, markers) in SHELL_COPY_MARKERS.items():
            with self.subTest(shell=path.name):
                self.assertEqual(shell_copy_violations(path.read_text(encoding="utf-8"),
                                                       function, markers), [])
        self.assertEqual(shell_copy_violations(CR_SHELL.read_text(encoding="utf-8"), "coverage",
                                               CR_COVERAGE_MARKERS), [])

    def test_CONTROL_a_shell_that_regrows_the_report_is_caught(self):
        source = KB_SHELL.read_text(encoding="utf-8")
        anchor = "    for line in _job.summary(OUT_PATH, REPORT_PATH, reg):"
        self.assertIn(anchor, source)
        rigged = source.replace(anchor, '    print("## Bucket counts")\n' + anchor)
        self.assertEqual(shell_copy_violations(rigged, "main", SHELL_COPY_MARKERS[KB_SHELL][1]),
                         ["## Bucket counts"])


# ===========================================================================
# 7. the new owners are pure composition
# ===========================================================================

def owner_violations(name: str, source: str) -> list:
    tree = ast.parse(source)
    got = s11._imports(tree)
    internal, stdlib = S13_MODULES[name]
    v = []
    permanent = {m for m in got if m.startswith("mtj_foundry.")}
    permanent = {m for m in permanent if not any(o.startswith(m + ".") for o in permanent)}
    permanent = {m for m in permanent if not (m.rsplit(".", 1)[0] in permanent)}
    if permanent != internal:
        v.append(f"permanent imports {sorted(permanent)}")
    if {m for m in got if not m.startswith("mtj_foundry")} != stdlib:
        v.append(f"stdlib imports {sorted(m for m in got if not m.startswith('mtj_foundry'))}")
    calls = {ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)}
    for forbidden in ("open", "print", "exit", "sys.exit", "Path", "Path.cwd", "input"):
        if forbidden in calls:
            v.append(f"calls {forbidden}")
    if any(c.endswith((".write_text", ".write_bytes", ".read_text", ".mkdir", ".unlink")) for c in calls):
        v.append("filesystem call")
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {
        n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    for forbidden in ("__file__", "SystemExit", "ProjectPaths", "parents"):
        if forbidden in names:
            v.append(f"names {forbidden}")
    strings = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    if any(re.search(r"experiments[/\\]|\bout[/\\]foundry|\barchive[/\\]", s) for s in strings):
        v.append("layout literal")
    return v


class TestTheNewOwnersArePureComposition(unittest.TestCase):

    def test_exact_imports_no_io_no_process_boundary_no_layout(self):
        for name in S13_MODULES:
            with self.subTest(module=name):
                self.assertEqual(owner_violations(name, (PKG / f"{name}.py").read_text(encoding="utf-8")), [])

    def test_CONTROL_an_independent_root_derivation_is_caught(self):
        source = (PKG / "keyword_buckets_job.py").read_text(encoding="utf-8")
        rigged = source.replace("from __future__ import annotations\n",
                                "from __future__ import annotations\nfrom pathlib import Path\n"
                                "ROOT = Path(__file__).resolve().parents[2]\n"
                                "OUT = ROOT / 'experiments/out/foundry/keyword-buckets.json'\n")
        v = owner_violations("keyword_buckets_job", rigged)
        self.assertTrue(any("__file__" in x for x in v))
        self.assertIn("layout literal", v)
        self.assertIn("calls Path", v)

    def test_CONTROL_a_writer_or_exit_is_caught(self):
        source = (PKG / "cr_checks_job.py").read_text(encoding="utf-8")
        rigged = source + "\n\ndef write(p, text):\n    p.write_text(text)\n    raise SystemExit(1)\n"
        v = owner_violations("cr_checks_job", rigged)
        self.assertIn("filesystem call", v)
        self.assertIn("names SystemExit", v)

    def test_nothing_in_mtg_or_the_authority_layer_imports_them(self):
        for path in sorted(PKG.rglob("*.py")):
            rel = path.relative_to(PKG).as_posix()
            if rel in {f"{n}.py" for n in S13_MODULES}:
                continue
            with self.subTest(module=rel):
                self.assertEqual({m for m in s11._imports(ast.parse(path.read_text(encoding="utf-8")))
                                  if m.split(".")[1:2] and m.split(".")[1] in S13_MODULES}, set())

    def test_the_package_graph_is_acyclic(self):
        self.assertEqual(s11.find_cycle(s11.package_graph(PKG)), [])

    def test_import_with_only_src_from_an_unrelated_cwd(self):
        code = ("import sys\n"
                "import mtj_foundry.lint_report, mtj_foundry.keyword_buckets_job, mtj_foundry.cr_checks_job\n"
                "print(sorted(m for m in sys.modules if m.startswith(('foundry_', 'experiments'))))\n")
        with tempfile.TemporaryDirectory() as td:
            res = subprocess.run([sys.executable, "-c", code], cwd=td, capture_output=True, text=True,
                                 env={"PATH": "/usr/bin:/bin", "PYTHONPATH": str(SRC)})
        self.assertEqual((res.returncode, res.stdout.strip()), (0, "[]"), res.stderr)


if __name__ == "__main__":
    unittest.main()
