"""Guards for the compact Manager/Worker control plane.

Current task state lives on GitHub Issue #1, not in a mirrored phase file.
These tests therefore protect the STATIC laws that must survive cleanup and
assert that the stale startup surfaces removed by the context-cleanup pass stay
absent.

Every checker below is a pure function of text so negative controls exercise the
same logic as positive checks.
"""

from __future__ import annotations

import re
import unittest

from tests.refoundation.helpers import REPO_ROOT


CLAUDE = REPO_ROOT / "CLAUDE.md"
ROOT_README = REPO_ROOT / "README.md"
REFOUNDATION_README = REPO_ROOT / "refoundation" / "README.md"
SESSION_PROTOCOL = REPO_ROOT / "refoundation" / "SESSION-PROTOCOL.md"
CAPTAIN_DIRECTION = REPO_ROOT / "refoundation" / "CAPTAIN-DIRECTION.md"
BOOTSTRAP_STATE = REPO_ROOT / "refoundation" / "BOOTSTRAP-STATE.yaml"

REMOVED_CONTEXT = (
    REPO_ROOT / "refoundation" / "ACTIVE-PHASE.yaml",
    REPO_ROOT / "refoundation" / "MANAGER-START.md",
    REPO_ROOT / "refoundation" / "WORKER-START.md",
    REPO_ROOT / "refoundation" / "ROADMAP.md",
    REPO_ROOT / "refoundation" / "PATH-E-RUNTIME.md",
    REPO_ROOT / "refoundation" / "PATH-E-M2.md",
    REPO_ROOT / "refoundation" / "PATH-E-M3.md",
    REPO_ROOT / ".claude" / "commands" / "triage-alpha.md",
    REPO_ROOT / ".claude" / "commands" / "triage-beta.md",
    REPO_ROOT / ".claude" / "commands" / "triage-emit.md",
)

PROTOCOL_FORM = "M:T -> W:X -> M:V -> M:T|K"
SELECTOR = "latest K -> active T"
HUMAN_CONTRACT = "Claude done"

IMPORT_RE = re.compile(r"@([A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]+)+)")
SHA40_RE = re.compile(r"\b[0-9a-f]{40}\b")

STALE_ROUTING = (
    r"SESSION-HANDOFF[A-Za-z0-9-]*\.md",
    r"MASTER-HANDOFF(?:-ADDENDUM-\d+)?\.md",
    r"PICK-UP-HERE\.md",
    r"SESSION-START-PROCEDURE\.md",
    r"refoundation-manager-bootstrap-\d{4}-\d{2}-\d{2}",
)
STALE_SELECTOR_RE = re.compile(r"latest\s+accepted\s+K", re.I)
K_AS_ACCEPTANCE_RE = re.compile(
    r"(?:K\s*=\s*acceptance|K is the acceptance arm|acceptance token K)",
    re.I,
)

EVERY_SESSION_INVARIANTS = (
    "PRESERVE TRUTH, NOT PLUMBING",
    "Issue #1",
    "No self-authorized successor",
    "Never merge",
    "STOP",
    "transitive",
    "Negative-control",
    "No card data in git",
    "oracle_id",
    "Halt loudly",
    "Determinism",
    "Captain",
    "Manager",
    "Worker",
)

AUTHORITY_PHRASES = (
    "evidence, not authority",
    "never self-authorizes",
    "STOP and report the conflict",
)


def flat(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("`", "").replace("*", ""))


def selector_problems(text: str) -> list[str]:
    f = flat(text)
    problems = [] if SELECTOR in f else [f"missing {SELECTOR!r}"]
    problems += [f"stale selector {m.group(0)!r}"
                 for m in STALE_SELECTOR_RE.finditer(f)]
    return problems


def routing_problems(text: str) -> list[str]:
    return [f"historical routing {m.group(0)!r}"
            for pattern in STALE_ROUTING
            for m in re.finditer(pattern, text)]


def authority_problems(text: str) -> list[str]:
    f = flat(text)
    problems = [f"missing authority phrase {phrase!r}"
                for phrase in AUTHORITY_PHRASES if phrase not in f]
    if "believe the measurement" in f.lower():
        problems.append("promotes evidence to authority")
    return problems


def checkpoint_problems(text: str) -> list[str]:
    f = flat(text)
    problems = []
    for phrase in ("K is a CHECKPOINT", "accepted_head", "active_task"):
        if phrase not in f:
            problems.append(f"missing checkpoint phrase {phrase!r}")
    problems += [f"equates K with acceptance: {m.group(0)!r}"
                 for m in K_AS_ACCEPTANCE_RE.finditer(f)]
    return problems


def human_contract_problems(text: str) -> list[str]:
    f = flat(text)
    problems = [] if HUMAN_CONTRACT in f else ["missing exact human contract"]
    if re.search(r"\bDONE\s+(?:<|[A-Z0-9])", f):
        problems.append("superseded DONE completion contract")
    return problems


class TestStaticControlPlane(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.claude = CLAUDE.read_text(encoding="utf-8")
        cls.root = ROOT_README.read_text(encoding="utf-8")
        cls.ref = REFOUNDATION_README.read_text(encoding="utf-8")
        cls.protocol = SESSION_PROTOCOL.read_text(encoding="utf-8")
        cls.captain = CAPTAIN_DIRECTION.read_text(encoding="utf-8")
        cls.bootstrap = BOOTSTRAP_STATE.read_text(encoding="utf-8")

    def test_removed_context_surfaces_stay_absent(self):
        existing = [p.relative_to(REPO_ROOT).as_posix()
                    for p in REMOVED_CONTEXT if p.exists()]
        self.assertEqual(existing, [])

    def test_claude_is_compact(self):
        self.assertLessEqual(len(self.claude.splitlines()), 180)
        self.assertLessEqual(len(self.claude.encode("utf-8")), 8000)

    def test_claude_auto_imports_no_second_startup_document(self):
        self.assertEqual(IMPORT_RE.findall(self.claude), [])

    def test_current_state_has_one_canonical_selector(self):
        for name, text in (
            ("CLAUDE.md", self.claude),
            ("refoundation/README.md", self.ref),
            ("refoundation/SESSION-PROTOCOL.md", self.protocol),
            ("refoundation/BOOTSTRAP-STATE.yaml", self.bootstrap),
        ):
            with self.subTest(document=name):
                self.assertEqual(selector_problems(text), [])

    def test_protocol_form_is_exact(self):
        self.assertIn(PROTOCOL_FORM, self.protocol)
        self.assertNotRegex(self.protocol, r"M:V\s*->\s*M:K")

    def test_k_semantics_survive_compaction(self):
        for name, text in (("CLAUDE.md", self.claude),
                           ("SESSION-PROTOCOL.md", self.protocol)):
            with self.subTest(document=name):
                self.assertEqual(checkpoint_problems(text), [])

    def test_evidence_never_becomes_authority(self):
        self.assertEqual(authority_problems(self.claude), [])
        self.assertIn("evidence", self.protocol.lower())
        self.assertIn("never self-authorize", self.protocol)

    def test_exact_human_completion_contract_survives(self):
        self.assertEqual(human_contract_problems(self.claude), [])

    def test_every_session_invariants_survive(self):
        f = flat(self.claude)
        missing = [phrase for phrase in EVERY_SESSION_INVARIANTS if phrase not in f]
        self.assertEqual(missing, [])

    def test_active_startup_docs_do_not_route_through_old_handoffs(self):
        active = {
            "CLAUDE.md": self.claude,
            "README.md": self.root,
            "refoundation/README.md": self.ref,
            "refoundation/SESSION-PROTOCOL.md": self.protocol,
            "refoundation/CAPTAIN-DIRECTION.md": self.captain,
        }
        for name, text in active.items():
            with self.subTest(document=name):
                self.assertEqual(routing_problems(text), [])

    def test_static_docs_do_not_carry_task_shas(self):
        for name, text in (
            ("CLAUDE.md", self.claude),
            ("README.md", self.root),
            ("refoundation/README.md", self.ref),
            ("SESSION-PROTOCOL.md", self.protocol),
            ("CAPTAIN-DIRECTION.md", self.captain),
        ):
            with self.subTest(document=name):
                self.assertEqual(SHA40_RE.findall(text), [])

    def test_bootstrap_state_is_only_a_tombstone(self):
        self.assertRegex(self.bootstrap, r"(?m)^status:\s*SUPERSEDED\s*$")
        self.assertIn("GitHub Issue #1 latest K", self.bootstrap)
        self.assertIn("refoundation/README.md", self.bootstrap)
        self.assertNotIn("ACTIVE-PHASE", self.bootstrap)
        self.assertNotRegex(self.bootstrap, r"(?m)^status:\s*ACTIVE\s*$")

    def test_root_readme_marks_docs_as_non_startup(self):
        self.assertIn("docs/                   semantic evidence/history; NOT current task routing",
                      self.root)
        self.assertIn("It is **not a startup directory**", self.root)

    def test_captain_direction_does_not_restart_old_review_sequence(self):
        self.assertIn("Do not restart old review steps", self.captain)
        self.assertIn("Current operational state is **GitHub Issue #1 latest `K`**",
                      self.captain)


class TestNegativeControls(unittest.TestCase):
    """Each key guard is shown red on the failure shape it claims to detect."""

    def test_selector_rejects_the_old_spelling(self):
        bad = "latest accepted K -> active T"
        self.assertTrue(selector_problems(bad))

    def test_routing_rejects_a_master_handoff(self):
        self.assertTrue(routing_problems("Read docs/MASTER-HANDOFF.md first."))

    def test_authority_rejects_measurement_promotion(self):
        bad = ("evidence, not authority; never self-authorizes; "
               "STOP and report the conflict; believe the measurement")
        self.assertTrue(authority_problems(bad))

    def test_checkpoint_rejects_acceptance_collapse(self):
        bad = "K is a CHECKPOINT; accepted_head active_task; K is the acceptance arm"
        self.assertTrue(checkpoint_problems(bad))

    def test_human_contract_rejects_the_old_DONE_form(self):
        bad = "Claude done\nDONE <P|S|F>"
        self.assertTrue(human_contract_problems(bad))

    def test_startup_import_regex_catches_a_reintroduced_phase_file(self):
        bad = "@refoundation/ACTIVE-PHASE.yaml"
        self.assertEqual(IMPORT_RE.findall(bad), ["refoundation/ACTIVE-PHASE.yaml"])


if __name__ == "__main__":
    unittest.main()
