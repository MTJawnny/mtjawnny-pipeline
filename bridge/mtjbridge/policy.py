"""Deterministic autonomy policy.

This module is the safety boundary. No model output reaches a GitHub mutation
without passing through `decide()`, and `decide()` contains no model call.

The central invariant, which `test_policy.py` pins with a negative control:

    A model verdict can only ever make the outcome MORE restrictive.
    It can never unlock an action that the deterministic layer withheld.

So a compromised, confused, or prompt-injected Manager can at worst halt the
automation. It cannot authorize a Captain-reserved change by saying PASS.
"""

from __future__ import annotations

import dataclasses
import fnmatch
import re
from typing import Iterable

from .protocol import Review, Result, Task

__all__ = [
    "PolicyError",
    "ValidationCommandRefused",
    "UnknownValidationID",
    "check_validation_commands",
    "check_task_validation",
    "refuse_raw_validation_commands",
    "require_validation_ids",
    "resolve_validation_ids",
    "require_machine_readable_scope",
    "VALIDATION_REGISTRY",
    "VALIDATION_EXECUTABLE_ALLOWLIST",
    "Decision",
    "Action",
    "CAPTAIN_PATHS",
    "PROTECTED_BRANCHES",
    "FORBIDDEN_ACTIONS",
    "decide",
    "classify_paths",
    "check_paths_against_task",
]


class PolicyError(RuntimeError):
    """The policy layer refuses to proceed. Always fatal; never caught to 'try anyway'."""


# Actions the state machine may take. Anything not listed cannot be requested.
class Action:
    POST_REVIEW = "post_review"
    CREATE_NEXT_TASK = "create_next_task"
    CREATE_REPAIR_TASK = "create_repair_task"
    POST_DECISION_PACKET = "post_decision_packet"
    HALT = "halt"


# Never available to the automation in v0, at any verdict, from any source.
FORBIDDEN_ACTIONS = frozenset(
    {"merge_pr", "enable_auto_merge", "close_issue_1", "push_protected", "force_push", "delete_branch"}
)

PROTECTED_BRANCHES = (
    "main",
    "master",
    "refoundation-baseline-2026-08-28",
)

# Touching any of these is a Captain decision by construction, whatever a model says.
# Each entry pairs a glob with the reserved category from the task contract.
CAPTAIN_PATHS: tuple[tuple[str, str], ...] = (
    ("**/codebook.json", "authoritative codebook content"),
    ("experiments/moves/*.json", "authoritative codebook content"),
    ("docs/CODEBOOK-NAMING-GRAMMAR.md", "new semantic vocabulary/law"),
    ("docs/RATIFIED-RULINGS-REGISTRY.md", "Foundry semantic truth"),
    ("docs/*RATIFIED*", "Foundry semantic truth"),
    ("docs/AQ4-*", "frozen AQ4 benchmark truth"),
    ("docs/SEMANTIC-IR-*", "frozen AQ4 benchmark truth"),
    ("docs/TRIAGE-BATCH-*.md", "Foundry semantic truth"),
    ("docs/MASTER-HANDOFF.md", "authority succession"),
    ("refoundation/CAPTAIN-DIRECTION.md", "authority succession"),
    ("refoundation/BOOTSTRAP-STATE.yaml", "authority succession"),
    ("CLAUDE.md", "authority succession"),
    (".github/workflows/*", "product architecture choice not already ratified"),
    ("**/grammars.json", "new semantic vocabulary/law"),
)

# Text signals in a Worker result that force a Captain halt even on a model PASS.
_CAPTAIN_TEXT_SIGNALS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bweaken(ed|ing)?\b.{0,40}\b(gate|test|assertion|conservation)", re.I),
     "weakening or removing a conservation/validation gate"),
    (re.compile(r"\b(removed|deleted|disabled)\b.{0,40}\b(gate|conservation|validation)", re.I),
     "weakening or removing a conservation/validation gate"),
    (re.compile(r"\bratif(y|ies|ied|ication)\b", re.I),
     "ratification is Captain-only"),
    (re.compile(r"\bD[1-9]\b.{0,30}\barchitecture\b", re.I),
     "P0.1 D1-D9 architecture choice"),
    (re.compile(r"\bconflict\b.{0,40}\bauthorit(y|ies)\b", re.I),
     "conflict between durable authorities"),
)


# --------------------------------------------------------------------------
# trusted validation registry
# --------------------------------------------------------------------------
#
# A task body is MODEL-authored. An executable allowlist was not enough: `python3`
# and `node` are on any reasonable list, and `python3 -c <payload>` is arbitrary
# host code execution with an allowlisted executable at argv[0]. Constraining the
# EXECUTABLE constrains the wrong half of the command.
#
# So task text may no longer supply argv at all. It may only NAME a validation ID.
# Trusted bridge code owns the argv that ID resolves to; a task cannot append to it,
# reorder it, or substitute one argument. An unknown ID is a deterministic STOP
# before the model is invoked, so the registry is fail-closed: capability arrives
# only through a reviewed change to THIS table, never through an issue body.
#
# Keep it minimal. Every entry added here widens what an unattended mutating task
# can cause to run on the operator's host.
VALIDATION_REGISTRY: dict[str, tuple[str, ...]] = {
    # The one check the bridge's own repair/canary work actually needs.
    "bridge-selftest": ("python3", "bridge/bin/mtj-selftest"),
}

# Executables the TRUSTED registry is permitted to name. This is now an invariant
# assertion over bridge-owned code, not a filter over model input: model input can
# no longer reach argv at all. It is retained because a registry entry is still
# hand-written, and a shell wrapper smuggled into the table would reopen exactly the
# hole the table exists to close.
VALIDATION_EXECUTABLE_ALLOWLIST: frozenset[str] = frozenset({
    "python", "python3", "pytest", "unittest",
    "make", "node", "npm", "npx", "yarn", "pnpm",
    "go", "cargo", "ruff", "mypy", "flake8", "black", "isort",
    "bash", "sh",  # refused below; listed so the refusal is explicit, not incidental
})

# Shells are never allowed, even though they look like ordinary executables: `sh -c`
# reintroduces exactly the arbitrary execution the allowlist exists to prevent.
VALIDATION_EXECUTABLE_DENYLIST: frozenset[str] = frozenset({"bash", "sh", "zsh", "fish",
                                                            "env", "eval", "exec", "sudo"})


class ValidationCommandRefused(PolicyError):
    """A declared acceptance command is not executable authority for this bridge."""


class UnknownValidationID(ValidationCommandRefused):
    """A task named a validation ID that trusted bridge code does not define."""


def check_validation_commands(commands: Iterable[Iterable[str]]) -> list[list[str]]:
    """Assert every command is a bare, non-shell, allowlisted executable. Or raise.

    Applied to REGISTRY-RESOLVED argv only. Never applied to task text as a way of
    admitting it: see `resolve_validation_ids`.
    """
    import os as _os

    checked: list[list[str]] = []
    for command in commands:
        argv = [str(a) for a in command]
        if not argv:
            raise ValidationCommandRefused("empty validation command")
        exe = _os.path.basename(argv[0])
        if exe in VALIDATION_EXECUTABLE_DENYLIST:
            raise ValidationCommandRefused(
                f"validation command '{exe}' is a shell or privilege wrapper and is refused; "
                "declare the real command directly instead of wrapping it"
            )
        if exe not in VALIDATION_EXECUTABLE_ALLOWLIST:
            raise ValidationCommandRefused(
                f"validation executable '{exe}' is not in VALIDATION_EXECUTABLE_ALLOWLIST. "
                "A task body is model-authored; the wrapper will not run an arbitrary program."
            )
        if _os.path.isabs(argv[0]) or ".." in argv[0]:
            raise ValidationCommandRefused(
                f"validation command must be a bare executable name, got '{argv[0]}'"
            )
        checked.append(argv)
    return checked


def resolve_validation_ids(ids: Iterable[str]) -> list[list[str]]:
    """Map task-declared validation IDs to the fixed argv trusted code assigns them.

    The returned argv comes from `VALIDATION_REGISTRY` and from nowhere else. The
    task supplies a key; it never supplies, extends or reorders a value. An ID that
    is not in the table raises, and every caller treats that as a STOP *before* the
    model is invoked.
    """
    resolved: list[list[str]] = []
    for raw in ids:
        vid = str(raw).strip()
        if vid not in VALIDATION_REGISTRY:
            raise UnknownValidationID(
                f"validation id '{vid}' is not registered. A task body may only NAME a "
                f"pre-registered check; it cannot supply a command. Known ids: "
                f"{sorted(VALIDATION_REGISTRY)}"
            )
        resolved.append([str(a) for a in VALIDATION_REGISTRY[vid]])
    # Invariant on the trusted table itself, not on the task.
    return check_validation_commands(resolved)


def refuse_raw_validation_commands(task: Task) -> str | None:
    """Return a STOP reason when a task body carries raw argv instead of IDs.

    Fail-closed for read-only tasks too: raw argv in a task body is a malformed
    contract under this schema, and silently ignoring it would leave the author
    believing a check ran.
    """
    if not task.raw_validation_commands:
        return None
    shown = "; ".join(" ".join(c) for c in task.raw_validation_commands[:3])
    return (
        "task body declares raw validation/acceptance COMMANDS. Raw argv is not "
        "executable authority for this bridge: a model-authored command line is "
        f"arbitrary host code execution ({shown!r}). Declare validation.ids naming "
        f"pre-registered checks instead. Known ids: {sorted(VALIDATION_REGISTRY)}"
    )


def require_validation_ids(task: Task) -> str | None:
    """Return a STOP reason when a MUTATING task declares no trusted validation.

    A mutation nobody checked is not evidence of anything. Recording that as a
    discrepancy was not enough: the worker still committed, pushed and opened a PR,
    and an automated Manager could PASS it. Read-only tasks are exempt by
    declaration, not by omission.
    """
    if not task.mutating:
        return None
    if task.validation_ids:
        return None
    return (
        "task is mutating but declares no trusted validation.ids. A mutating task "
        "must name at least one pre-registered check, or declare scope.kind: read_only. "
        f"Known ids: {sorted(VALIDATION_REGISTRY)}"
    )


def check_task_validation(task: Task) -> str | None:
    """The whole validation gate as one deterministic answer: a STOP reason, or None."""
    reason = refuse_raw_validation_commands(task)
    if reason:
        return reason
    reason = require_validation_ids(task)
    if reason:
        return reason
    try:
        resolve_validation_ids(task.validation_ids)
    except ValidationCommandRefused as exc:
        return str(exc)
    return None


@dataclasses.dataclass(frozen=True)
class Decision:
    """What the automation is permitted to do next. Produced only by `decide()`."""

    action: str
    verdict: str
    reasons: tuple[str, ...] = ()
    captain_categories: tuple[str, ...] = ()
    automation_may_continue: bool = False

    @property
    def halts(self) -> bool:
        return not self.automation_may_continue


# --------------------------------------------------------------------------
# path classification
# --------------------------------------------------------------------------


def _match(path: str, pattern: str) -> bool:
    if fnmatch.fnmatch(path, pattern):
        return True
    # fnmatch does not give '**' recursive semantics; approximate it explicitly.
    if pattern.startswith("**/"):
        return fnmatch.fnmatch(path, pattern[3:]) or path.endswith("/" + pattern[3:]) or fnmatch.fnmatch(
            path, "*/" + pattern[3:]
        )
    return False


def classify_paths(paths: Iterable[str]) -> list[tuple[str, str]]:
    """Return (path, captain_category) for every path in Captain-reserved territory."""
    hits: list[tuple[str, str]] = []
    for path in paths:
        for pattern, category in CAPTAIN_PATHS:
            if _match(path, pattern):
                hits.append((path, category))
                break
    return hits


def check_paths_against_task(task: Task, paths: Iterable[str]) -> list[str]:
    """Enforce a task's machine-readable allow/deny globs.

    Returns the list of violations. An empty allow list means the task did not
    supply machine-readable scope: that is reported by the caller as
    'not machine-checkable', never silently treated as 'everything allowed'.
    """
    paths = list(paths)
    violations: list[str] = []
    for path in paths:
        for pattern in task.deny_paths:
            if _match(path, pattern) or fnmatch.fnmatch(path, pattern):
                violations.append(f"{path}: matches deny pattern '{pattern}'")
    if task.allow_paths:
        for path in paths:
            if not any(_match(path, p) or fnmatch.fnmatch(path, p) for p in task.allow_paths):
                violations.append(f"{path}: outside every allow pattern {task.allow_paths}")
    return violations


def captain_signals_in_result(result: Result) -> list[str]:
    """Deterministic scan of a Worker result for Captain-reserved categories."""
    found: list[str] = []
    haystack = "\n".join(
        [*result.mutations, *result.discrepancies, *result.validation, *result.decision_required]
    )
    for pattern, category in _CAPTAIN_TEXT_SIGNALS:
        if pattern.search(haystack) and category not in found:
            found.append(category)
    return found


# --------------------------------------------------------------------------
# the decision
# --------------------------------------------------------------------------


def require_machine_readable_scope(task: Task) -> str | None:
    """Return a STOP reason when a MUTATING task lacks machine-readable path scope.

    Report-only scope was acceptable while a human watched every run. It is not
    acceptable for unattended mutation: without globs there is nothing to enforce,
    and 'no globs' must never read as 'every path permitted'.
    """
    if not task.mutating:
        return None
    if task.declares_scope:
        return None
    return (
        "task is mutating but declares no machine-readable scope.allow_paths / "
        "scope.deny_paths. Absence of scope is not permission: refusing to execute. "
        "Either declare path globs, or declare scope.kind: read_only."
    )


def decide(
    *,
    task: Task,
    result: Result,
    review: Review,
    changed_paths: Iterable[str] = (),
    repair_count: int = 0,
    max_repairs: int = 2,
    cycle_count: int = 0,
    max_cycles: int = 8,
) -> Decision:
    """Map (task, result, model review) to exactly one permitted action.

    Deterministic. Contains no model call and no network access.
    """
    changed_paths = list(changed_paths)
    reasons: list[str] = []
    captain: list[str] = []

    # --- 1. Hard structural halts, evaluated BEFORE the model verdict. ------
    if review.task != result.task:
        raise PolicyError(
            f"review targets task '{review.task}' but the result is for '{result.task}'; "
            "refusing to apply a review to a different task"
        )
    if result.task != task.task:
        raise PolicyError(
            f"result targets task '{result.task}' but the issue defines '{task.task}'"
        )

    if result.base_expected and not result.base_matches:
        return Decision(
            action=Action.HALT,
            verdict="STOP",
            reasons=(
                f"base mismatch: task expected {result.base_expected}, worker measured "
                f"{result.base_measured}. State drift is an explicit STOP, never adapted to.",
            ),
        )

    if cycle_count >= max_cycles:
        return Decision(
            action=Action.HALT,
            verdict="STOP",
            reasons=(f"cycle limit reached ({cycle_count}/{max_cycles}); halting rather than looping",),
        )

    # --- 2. Deterministic Captain triggers, independent of the model. -------
    for path, category in classify_paths(changed_paths):
        entry = f"{path} -> {category}"
        if entry not in captain:
            captain.append(entry)
    for category in captain_signals_in_result(result):
        entry = f"result text -> {category}"
        if entry not in captain:
            captain.append(entry)
    if result.needs_captain:
        for item in result.decision_required:
            captain.append(f"worker declared decision_required -> {item}")

    # --- 3. Task-scope enforcement. -----------------------------------------
    scope_stop = require_machine_readable_scope(task)
    if scope_stop:
        return Decision(action=Action.HALT, verdict="STOP", reasons=(scope_stop,))
    validation_stop = check_task_validation(task)
    if validation_stop:
        return Decision(action=Action.HALT, verdict="STOP", reasons=(validation_stop,))
    if task.mutating and result.pr and not result.evidence:
        return Decision(
            action=Action.HALT,
            verdict="STOP",
            reasons=(
                f"mutating task published PR #{result.pr} with no wrapper-captured validation "
                "evidence. A published mutation must carry the output of a trusted check, not "
                "model prose about one.",
            ),
        )
    if result.validation_failed:
        failed = [f"{' '.join(e.get('command', []))} -> rc={e.get('rc')}"
                  for e in result.evidence if int(e.get("rc", 0)) != 0]
        return Decision(
            action=Action.HALT if review.verdict == "PASS" else Action.CREATE_REPAIR_TASK,
            verdict="STOP" if review.verdict == "PASS" else "REPAIR",
            reasons=tuple(["wrapper-captured acceptance validation failed:"] + failed),
            automation_may_continue=review.verdict == "REPAIR" and repair_count < max_repairs,
        )
    violations = check_paths_against_task(task, changed_paths)
    if violations:
        return Decision(
            action=Action.HALT,
            verdict="STOP",
            reasons=tuple(["task allow/deny scope violated:"] + violations),
        )

    # --- 4. The model verdict may only restrict from here. ------------------
    if captain:
        return Decision(
            action=Action.POST_DECISION_PACKET,
            verdict="CAPTAIN_DECISION_REQUIRED",
            reasons=tuple(
                reasons
                + [
                    "deterministic policy found Captain-reserved territory; "
                    f"model verdict was {review.verdict} and cannot unlock it"
                ]
            ),
            captain_categories=tuple(captain),
        )

    if review.verdict == "STOP":
        return Decision(action=Action.HALT, verdict="STOP",
                        reasons=tuple(reasons + list(review.reasons) or ["model returned STOP"]))

    if review.verdict == "CAPTAIN_DECISION_REQUIRED":
        return Decision(
            action=Action.POST_DECISION_PACKET,
            verdict="CAPTAIN_DECISION_REQUIRED",
            reasons=tuple(reasons + list(review.reasons)),
            captain_categories=tuple(review.captain_question) or ("model-declared",),
        )

    if review.verdict == "REPAIR":
        if result.status == "COMPLETE" and not result.discrepancies:
            reasons.append("model asked for REPAIR on a clean COMPLETE result; allowed but noted")
        if repair_count >= max_repairs:
            return Decision(
                action=Action.HALT,
                verdict="STOP",
                reasons=tuple(
                    reasons
                    + [f"repair limit reached ({repair_count}/{max_repairs}); halting rather than looping"]
                ),
            )
        return Decision(
            action=Action.CREATE_REPAIR_TASK,
            verdict="REPAIR",
            reasons=tuple(reasons + list(review.reasons)),
            automation_may_continue=True,
        )

    # review.verdict == "PASS"
    if result.status in ("STOP", "FAIL"):
        return Decision(
            action=Action.HALT,
            verdict="STOP",
            reasons=tuple(
                reasons
                + [
                    f"model returned PASS on a worker result whose status is {result.status}; "
                    "policy refuses to advance past a failed execution"
                ]
            ),
        )
    if task.authorizes_successor and review.next_task_id:
        return Decision(
            action=Action.CREATE_NEXT_TASK,
            verdict="PASS",
            reasons=tuple(reasons + list(review.reasons)),
            automation_may_continue=True,
        )
    return Decision(
        action=Action.POST_REVIEW,
        verdict="PASS",
        reasons=tuple(
            reasons
            + list(review.reasons)
            + (
                []
                if task.authorizes_successor
                else ["task declared next.authorized=NONE; no successor is created"]
            )
        ),
        automation_may_continue=False,
    )


def assert_action_permitted(action: str) -> None:
    if action in FORBIDDEN_ACTIONS:
        raise PolicyError(f"action '{action}' is forbidden in bridge v0 and has no code path")
