"""The Worker operating contract must stay compact, current, and self-routing.

A fresh session loads `CLAUDE.md` and nothing else by default. That makes the
startup document set a control plane, and a control plane that silently
re-accumulates chronology, re-points at a superseded bootstrap branch, or loses
the exact human return contract fails in the one way nobody notices: the next
session simply behaves slightly wrong and reports success.

DESIGN RULE, and it is the whole reason this file is shaped the way it is:
every check below is a pure function of TEXT. Nothing takes a path, nothing
reads a file except at the top, and nothing writes. That is what lets the
negative-control class feed a deliberately broken document to the SAME function
the positive class uses — rather than to a re-implementation of it, which is the
defect class this repository has hit most often. `CLAUDE.md` itself is not read
as data by any production module (checked: every reference to it in
`experiments/`, `src/` and `pipeline/` is a comment), so this file is the only
thing standing between the contract and silent rot.
"""

from __future__ import annotations

import re
import unittest

from tests.refoundation.helpers import REPO_ROOT

CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
WORKER_START = REPO_ROOT / "refoundation" / "WORKER-START.md"
SESSION_PROTOCOL = REPO_ROOT / "refoundation" / "SESSION-PROTOCOL.md"
ACTIVE_PHASE = REPO_ROOT / "refoundation" / "ACTIVE-PHASE.yaml"
BOOTSTRAP_STATE = REPO_ROOT / "refoundation" / "BOOTSTRAP-STATE.yaml"

# The startup document set. "Active" means a fresh session can reach it without
# being told to; that is what makes stale routing inside it dangerous.
STARTUP_DOCS = {
    "CLAUDE.md": CLAUDE_MD,
    "refoundation/WORKER-START.md": WORKER_START,
    "refoundation/SESSION-PROTOCOL.md": SESSION_PROTOCOL,
    "refoundation/ACTIVE-PHASE.yaml": ACTIVE_PHASE,
    "refoundation/BOOTSTRAP-STATE.yaml": BOOTSTRAP_STATE,
}

# Budgets, from the C8.5W task contract.
CLAUDE_MAX_LINES, CLAUDE_MAX_BYTES = 180, 8000
WORKER_START_MAX_LINES = 35
SESSION_PROTOCOL_MAX_LINES = 140
ACTIVE_PHASE_MAX_BYTES = 2000
BOOTSTRAP_STATE_MAX_BYTES = 1000

PHASE_IMPORT = "refoundation/ACTIVE-PHASE.yaml"

# A Claude Code import is `@` immediately followed by a path. Requiring at least
# one `/` is what keeps prose like an email or a decorator out of the match; a
# startup import of a manual is always a path.
IMPORT_RE = re.compile(r"@([A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]+)+)")

# Routing through superseded state. These match ROUTING FORMS -- a branch name,
# a document filename -- deliberately NOT the words "handoff" or "bootstrap",
# because the current docs must be able to SAY that those read steps were
# removed. A word-level ban would forbid the sentence that records the removal.
HISTORICAL_ROUTING = (
    r"refoundation-manager-bootstrap-\d{4}-\d{2}-\d{2}",
    r"origin/refoundation-manager-bootstrap",
    r"SESSION-HANDOFF[A-Za-z0-9-]*\.md",
    r"MASTER-HANDOFF\.md",
    r"PICK-UP-HERE\.md",
    r"SESSION-START-PROCEDURE\.md",
)

# The superseded human completion contract. Each alternative carries its own
# boundary; a trailing `\b` outside the alternation can NEVER match after `>`,
# since `>` and a following space are both non-word characters. That exact bug
# was in the first draft of this regex and a negative control caught it, which
# is what negative controls are for. It is recorded here rather than quietly
# repaired.
STALE_HUMAN_CONTRACT = (
    r"\bDONE\s+<",
    r"\bDONE\s+[A-Z0-9][A-Z0-9.]*\.[A-Z0-9-]+\b",
    r"details\s*:\s*Issue\s*#",
    r"<\s*P\s*\|\s*S\s*\|\s*F\s*>",
)

EXACT_HUMAN_CONTRACT = "Claude done"

# A 40-hex object name. Task SHAs are task state and must not enter phase state.
SHA40_RE = re.compile(r"\b[0-9a-f]{40}\b")

# PR-shaped only, ON PURPOSE. A bare `#\d+` would also flag `Issue #1`, which is
# the legitimate authority pointer this file exists to protect.
PR_STATE_RE = re.compile(r"(?i)\b(?:PR|pull[\s_-]?request)[\s_-]*#?\s*\d+")

ACTIVE_PHASE_REQUIRED = (
    "schema: mtj-active-phase/1",
    "phase:",
    "principle: PRESERVE_TRUTH_NOT_PLUMBING",
    "permanent_namespace: mtj_foundry",
    "layout_owner:",
    "task_authority:",
    "phase_update_rule:",
    "safe_reasoning_unit:",
    "required_axes:",
)
ACTIVE_PHASE_CONTROLS = ("AQ4", "BRIDGE0", "STEP6", "MERGE")

# C8.5W.R2 -- three laws the R1 rewrite got wrong. Each is asserted BOTH ways:
# the correct form must be present AND the rejected form must be absent, because
# a document can carry both and a presence-only check would pass it.

# The contracted protocol form. The final arm is `T|K` and it is a BRANCH: an
# audit may return a repair `T` against unaccepted work, or record `K`. R1
# collapsed it to mandatory `K`, which writes "every review ends in acceptance"
# into the control plane -- and this very slice is the counter-example.
PROTOCOL_FORM = "M:T -> W:X -> M:V -> M:T|K"
MANDATORY_K_RE = re.compile(r"M:V\s*->\s*M:K")

# Measurement is evidence. R1 instructed the Worker to "believe the measurement"
# when a document and a measurement disagree, which promotes evidence to
# authority silently -- contradicting SESSION-PROTOCOL's own EVIDENCE class.
REJECTED_AUTHORITY_INSTRUCTION = "believe the measurement"
AUTHORITY_LAW_PHRASES = (
    "evidence, not authority",
    "never self-authorizes",
    "STOP and report the conflict",
)

# The standing rank law keeps its standing exception. R1 dropped the parenthesis
# and thereby stated a BROADER law than the ratified one -- a semantic change
# nothing authorized.
RANK_RULE = "Rank buries, never excludes"
RANK_LAW = "Rank buries, never excludes (sole exception: corroboration gate)."


def flat(text: str) -> str:
    """Whitespace- and emphasis-insensitive view, for prose that line-wraps.

    A law that wraps across two source lines is the same law. Matching raw text
    would make the guard depend on where the paragraph happened to break, which
    is exactly the kind of accidental-plumbing dependency it exists to prevent.
    """
    return re.sub(r"\s+", " ", text.replace("*", "").replace("`", ""))


def protocol_form_problems(text: str):
    problems = []
    if PROTOCOL_FORM not in text:
        problems.append(f"missing exact protocol form {PROTOCOL_FORM!r}")
    for m in MANDATORY_K_RE.finditer(text):
        problems.append(f"collapses the T|K branch into mandatory K: {m.group(0)!r}")
    return problems


def authority_law_problems(text: str):
    flattened = flat(text)
    problems = [f"missing authority law phrase {phrase!r}"
                for phrase in AUTHORITY_LAW_PHRASES if phrase not in flattened]
    if REJECTED_AUTHORITY_INSTRUCTION in flattened.lower():
        problems.append("promotes evidence to authority: "
                        f"{REJECTED_AUTHORITY_INSTRUCTION!r}")
    return problems


def rank_law_problems(text: str):
    """Conditional by contract: only binding if the rank rule is retained."""
    flattened = flat(text)
    if RANK_RULE not in flattened:
        return []
    if RANK_LAW not in flattened:
        return ["rank rule retained without its standing corroboration-gate "
                "exception; this states a BROADER law than the ratified one"]
    return []


# Rules that must survive the compaction. A byte budget is not a licence to drop
# a live rule, and a LINE COUNT CANNOT SEE ONE GOING MISSING -- which is why this
# is asserted positively rather than inferred from the file still being large.
EVERY_SESSION_INVARIANTS = (
    "PRESERVE TRUTH, NOT PLUMBING",
    "Issue #1",
    "self-authorized successor",
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


# --------------------------------------------------------------------------
# Every check is a pure function of text.
# --------------------------------------------------------------------------

def size_problems(text: str, max_lines: int | None, max_bytes: int | None):
    problems = []
    if max_lines is not None:
        lines = len(text.splitlines())
        if lines > max_lines:
            problems.append(f"{lines} lines > {max_lines}")
    if max_bytes is not None:
        size = len(text.encode("utf-8"))
        if size > max_bytes:
            problems.append(f"{size} bytes > {max_bytes}")
    return problems


def phase_import_problems(text: str):
    """Exactly one startup import, and it is the phase file."""
    imports = IMPORT_RE.findall(text)
    if imports == [PHASE_IMPORT]:
        return []
    if not imports:
        return [f"no startup import; expected exactly {PHASE_IMPORT}"]
    return [f"startup imports are {imports}; expected exactly [{PHASE_IMPORT!r}]"]


def historical_routing_problems(text: str):
    return [f"routes through superseded state: {m.group(0)!r}"
            for pat in HISTORICAL_ROUTING
            for m in re.finditer(pat, text)]


def stale_human_contract_problems(text: str):
    return [f"superseded human completion contract: {m.group(0)!r}"
            for pat in STALE_HUMAN_CONTRACT
            for m in re.finditer(pat, text)]


def exact_human_contract_problems(text: str):
    if EXACT_HUMAN_CONTRACT not in text:
        return [f"missing exact human contract {EXACT_HUMAN_CONTRACT!r}"]
    return []


def active_phase_problems(text: str):
    problems = [f"missing required field {f!r}"
                for f in ACTIVE_PHASE_REQUIRED if f not in text]
    for control in ACTIVE_PHASE_CONTROLS:
        if control not in text:
            problems.append(f"missing standing control {control!r}")
    if "Issue #1" not in text:
        problems.append("missing Issue #1 task-authority pointer")
    problems += [f"carries task SHA {m.group(0)!r}" for m in SHA40_RE.finditer(text)]
    problems += [f"carries PR task state {m.group(0)!r}"
                 for m in PR_STATE_RE.finditer(text)]
    return problems


def bootstrap_state_problems(text: str):
    problems = []
    if not re.search(r"(?m)^status:\s*SUPERSEDED\s*$", text):
        problems.append("status is not SUPERSEDED")
    if re.search(r"(?m)^status:\s*ACTIVE\s*$", text):
        problems.append("status is still ACTIVE")
    if PHASE_IMPORT not in text:
        problems.append(f"does not point forward to {PHASE_IMPORT}")
    if "Issue #1" not in text:
        problems.append("does not point forward to Issue #1")
    for stale in ("pending_review", "next_manager_action", "next_worker_action",
                  "P0.1", "completed:", "captain_decisions_already_made"):
        if stale in text:
            problems.append(f"presents superseded state as current: {stale!r}")
    return problems


def retained_invariant_problems(text: str):
    return [f"every-session rule dropped by the rewrite: {rule!r}"
            for rule in EVERY_SESSION_INVARIANTS if rule not in text]


# --------------------------------------------------------------------------
# POSITIVE CLASS -- the shipped documents.
# --------------------------------------------------------------------------

class TestTheWorkerOperatingContract(unittest.TestCase):

    def setUp(self):
        self.texts = {name: path.read_text(encoding="utf-8")
                      for name, path in STARTUP_DOCS.items()}

    def test_every_startup_document_exists(self):
        for name, path in STARTUP_DOCS.items():
            self.assertTrue(path.exists(), f"missing startup document {name}")

    def test_the_documents_are_within_their_byte_and_line_budgets(self):
        budgets = {
            "CLAUDE.md": (CLAUDE_MAX_LINES, CLAUDE_MAX_BYTES),
            "refoundation/WORKER-START.md": (WORKER_START_MAX_LINES, None),
            "refoundation/SESSION-PROTOCOL.md": (SESSION_PROTOCOL_MAX_LINES, None),
            "refoundation/ACTIVE-PHASE.yaml": (None, ACTIVE_PHASE_MAX_BYTES),
            "refoundation/BOOTSTRAP-STATE.yaml": (None, BOOTSTRAP_STATE_MAX_BYTES),
        }
        for name, (max_lines, max_bytes) in budgets.items():
            with self.subTest(doc=name):
                self.assertEqual(
                    size_problems(self.texts[name], max_lines, max_bytes), [])

    def test_the_root_contract_imports_exactly_the_phase_file(self):
        self.assertEqual(phase_import_problems(self.texts["CLAUDE.md"]), [])

    def test_no_startup_document_routes_through_superseded_state(self):
        for name, text in self.texts.items():
            with self.subTest(doc=name):
                self.assertEqual(historical_routing_problems(text), [])

    def test_the_exact_human_completion_contract_is_stated(self):
        self.assertEqual(exact_human_contract_problems(self.texts["CLAUDE.md"]), [])

    def test_no_startup_document_carries_a_superseded_human_contract(self):
        """It is the ONLY normal terminal contract only if no rival survives."""
        for name, text in self.texts.items():
            with self.subTest(doc=name):
                self.assertEqual(stale_human_contract_problems(text), [])

    def test_the_active_phase_carries_current_state_and_no_task_state(self):
        self.assertEqual(
            active_phase_problems(self.texts["refoundation/ACTIVE-PHASE.yaml"]), [])

    def test_the_bootstrap_state_is_superseded_and_points_forward(self):
        self.assertEqual(
            bootstrap_state_problems(self.texts["refoundation/BOOTSTRAP-STATE.yaml"]),
            [])

    def test_the_compaction_dropped_no_every_session_rule(self):
        self.assertEqual(retained_invariant_problems(self.texts["CLAUDE.md"]), [])

    def test_the_session_protocol_keeps_the_contracted_branching_form(self):
        self.assertEqual(
            protocol_form_problems(self.texts["refoundation/SESSION-PROTOCOL.md"]),
            [])

    def test_measurement_is_evidence_and_never_self_authorizes(self):
        self.assertEqual(authority_law_problems(self.texts["CLAUDE.md"]), [])

    def test_the_retained_rank_rule_keeps_its_standing_exception(self):
        self.assertEqual(rank_law_problems(self.texts["CLAUDE.md"]), [])


# --------------------------------------------------------------------------
# NEGATIVE CONTROLS -- a guard never shown to fail is not known to be a guard.
# Every rig is a non-no-op mutation of a STRING. No file is written.
# --------------------------------------------------------------------------

class TestTheContractGuardCanFail(unittest.TestCase):

    def setUp(self):
        self.claude = CLAUDE_MD.read_text(encoding="utf-8")
        self.phase = ACTIVE_PHASE.read_text(encoding="utf-8")
        self.bootstrap = BOOTSTRAP_STATE.read_text(encoding="utf-8")
        self.protocol = SESSION_PROTOCOL.read_text(encoding="utf-8")

    def test_NC1_an_inflated_root_contract_turns_the_size_guard_red(self):
        rigged = self.claude + "\nfiller\n" * CLAUDE_MAX_LINES
        self.assertNotEqual(rigged, self.claude)
        self.assertNotEqual(
            size_problems(rigged, CLAUDE_MAX_LINES, CLAUDE_MAX_BYTES), [])

    def test_NC2_restoring_the_old_id_shaped_human_contract_turns_it_red(self):
        rigged = self.claude.replace(
            "  `Claude done`",
            "  `DONE <task-id> <P|S|F> details:Issue#1`")
        self.assertNotEqual(rigged, self.claude)
        self.assertNotEqual(stale_human_contract_problems(rigged), [])

    def test_NC3_adding_bootstrap_branch_routing_turns_it_red(self):
        rigged = self.claude + (
            "\nRead bootstrap state from "
            "origin/refoundation-manager-bootstrap-2026-08-28.\n")
        self.assertNotEqual(rigged, self.claude)
        self.assertNotEqual(historical_routing_problems(rigged), [])

    def test_NC3b_routing_through_a_dated_session_handoff_turns_it_red(self):
        rigged = self.claude + "\nStart from docs/SESSION-HANDOFF-2026-08-09.md.\n"
        self.assertNotEqual(rigged, self.claude)
        self.assertNotEqual(historical_routing_problems(rigged), [])

    def test_NC4_a_task_sha_or_pr_number_in_the_phase_file_turns_it_red(self):
        with_sha = self.phase + "\nbase: 9412e9e6236dd6509941b668f0951fdbfc213d29\n"
        self.assertNotEqual(with_sha, self.phase)
        self.assertNotEqual(active_phase_problems(with_sha), [])

        with_pr = self.phase + "\nopen: PR #36\n"
        self.assertNotEqual(with_pr, self.phase)
        self.assertNotEqual(active_phase_problems(with_pr), [])

    def test_NC4b_the_pr_guard_does_not_fire_on_the_issue_1_pointer(self):
        """The authority pointer must survive the PR-state ban. This is the
        control ON the control: a lazier `#\\d+` would fail the shipped file."""
        self.assertEqual(PR_STATE_RE.findall("task_authority: GitHub Issue #1"), [])

    def test_NC5_removing_the_exact_human_contract_turns_it_red(self):
        rigged = self.claude.replace(EXACT_HUMAN_CONTRACT, "all finished")
        self.assertNotEqual(rigged, self.claude)
        self.assertNotEqual(exact_human_contract_problems(rigged), [])

    def test_NC6_making_the_bootstrap_state_current_again_turns_it_red(self):
        rigged = self.bootstrap.replace("status: SUPERSEDED", "status: ACTIVE")
        self.assertNotEqual(rigged, self.bootstrap)
        self.assertNotEqual(bootstrap_state_problems(rigged), [])

    def test_NC6b_restoring_stale_next_action_claims_turns_it_red(self):
        rigged = self.bootstrap + "\nnext_worker_action:\n  authorized: NONE\n"
        self.assertNotEqual(rigged, self.bootstrap)
        self.assertNotEqual(bootstrap_state_problems(rigged), [])

    def test_NC7_dropping_the_phase_import_turns_it_red(self):
        rigged = self.claude.replace("@" + PHASE_IMPORT, "(see the phase file)")
        self.assertNotEqual(rigged, self.claude)
        self.assertNotEqual(phase_import_problems(rigged), [])

    def test_NC8_importing_a_historical_manual_at_startup_turns_it_red(self):
        rigged = self.claude + "\n@docs/MASTER-HANDOFF.md\n"
        self.assertNotEqual(rigged, self.claude)
        self.assertNotEqual(phase_import_problems(rigged), [])
        self.assertNotEqual(historical_routing_problems(rigged), [])

    def test_NC9_silently_dropping_an_every_session_rule_turns_it_red(self):
        rigged = self.claude.replace("PRESERVE TRUTH, NOT PLUMBING", "be careful")
        self.assertNotEqual(rigged, self.claude)
        self.assertNotEqual(retained_invariant_problems(rigged), [])

    def test_NC10_the_mandatory_K_protocol_shape_turns_it_red(self):
        """The exact defect C8.5W.R1.V rejected."""
        rigged = self.protocol.replace(
            "M:T -> W:X -> M:V -> M:T|K",
            "M:T  ->  W:X  ->  M:V  ->  M:K (accept, name next T)")
        self.assertNotEqual(rigged, self.protocol)
        self.assertNotEqual(protocol_form_problems(rigged), [])

    def test_NC11_restoring_believe_the_measurement_turns_it_red(self):
        rigged = self.claude.replace(
            "**A measurement is evidence, not authority, and it never "
            "self-authorizes.**",
            "If a document and a measurement disagree, measure again and "
            "believe the measurement.")
        self.assertNotEqual(rigged, self.claude)
        self.assertNotEqual(authority_law_problems(rigged), [])

    def test_NC12_dropping_only_the_corroboration_gate_exception_turns_it_red(self):
        """The rank RULE survives the rig; only its EXCEPTION is removed. A
        presence-only check on "Rank buries, never excludes" stays green here,
        which is precisely why the check is written against the full law."""
        rigged = self.claude.replace(
            "Rank buries, never excludes (sole exception:\n  corroboration gate).",
            "Rank buries, never excludes.")
        self.assertNotEqual(rigged, self.claude)
        self.assertIn(RANK_RULE, flat(rigged))      # the rule is still there
        self.assertNotEqual(rank_law_problems(rigged), [])

    def test_NC12b_the_rank_check_is_conditional_as_contracted(self):
        """Contract: binding only "if the rank rule remains in CLAUDE.md"."""
        self.assertEqual(rank_law_problems("a contract with no rank rule"), [])

    def test_the_unrigged_documents_are_the_green_control(self):
        """Every rig above is only meaningful because this is clean."""
        self.assertEqual(size_problems(self.claude, CLAUDE_MAX_LINES,
                                       CLAUDE_MAX_BYTES), [])
        self.assertEqual(phase_import_problems(self.claude), [])
        self.assertEqual(historical_routing_problems(self.claude), [])
        self.assertEqual(stale_human_contract_problems(self.claude), [])
        self.assertEqual(active_phase_problems(self.phase), [])
        self.assertEqual(bootstrap_state_problems(self.bootstrap), [])
        self.assertEqual(protocol_form_problems(self.protocol), [])
        self.assertEqual(authority_law_problems(self.claude), [])
        self.assertEqual(rank_law_problems(self.claude), [])


if __name__ == "__main__":
    unittest.main()
