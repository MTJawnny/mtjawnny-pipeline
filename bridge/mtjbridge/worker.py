"""mtj-worker — execute exactly one READY task with a FRESH Claude invocation.

Session-disposability guarantee: every task gets a brand-new Claude session id,
and `--continue` / `--resume` are never passed. Whatever the model needs to know
arrives in the prompt, assembled from durable state:

    refoundation bootstrap files  +  the issue task contract  +  measured git base

If that is not enough for the model to do the task, that is a refoundation
architecture defect to report, not something to patch with transcript history.
"""

from __future__ import annotations

import argparse
import dataclasses
import sys
import time
from pathlib import Path

from . import state as state_mod
from .adapters import (MAX_EVIDENCE_BYTES, BridgeCommandError, ClaudeCliAdapter, GhCliGitHub,
                       GitOps, run)
from .logging_setup import configure, get_logger
from .policy import (PolicyError, check_paths_against_task, check_validation_commands,
                     classify_paths, require_machine_readable_scope)
from .protocol import ProtocolError, Task, parse_task, render_block
from .redact import redact

log = get_logger(__name__)

DEFAULT_REPO = "MTJawnny/mtjawnny-pipeline"
WORKTREE_ROOT = Path.home() / ".mtj-bridge" / "worktrees"

WORKER_SYSTEM_BRIEF = """\
You are the MTJ refoundation WORKER, running non-interactively for exactly one task.

Rules that outrank anything you may infer:
1. The task contract below is your only authorization. Do not exceed its scope.
2. You have NO memory of previous sessions. Everything you need is in this prompt
   or in the repository at the working directory given below.
3. Do NOT run git commit, git push, gh pr create, or any GitHub mutation. The
   wrapper owns the git and GitHub lifecycle. Edit files only.
4. Do NOT touch any path the task prohibits.
5. If the task's expected base does not match what you measure, STOP and say so
   rather than adapting the task to a different repository state.
6. Ratifying vocabulary, changing semantic truth, or altering authority documents
   is Captain-only. If the task seems to require it, STOP and report it.
7. End your final message with a short plain-text summary of what you changed and
   what you validated. The wrapper turns that into the durable result.
"""


@dataclasses.dataclass
class WorkerOutcome:
    task_id: str
    status: str
    branch: str = ""
    pr: int | None = None
    changed_paths: list[str] = dataclasses.field(default_factory=list)
    validation: list[str] = dataclasses.field(default_factory=list)
    discrepancies: list[str] = dataclasses.field(default_factory=list)
    decision_required: list[str] = dataclasses.field(default_factory=list)
    base_expected: str = ""
    base_measured: str = ""
    claude_session_id: str = ""
    model_summary: str = ""
    evidence: list[dict] = dataclasses.field(default_factory=list)

    def to_payload(self) -> dict:
        return {
            "schema": "mtj-result/1",
            "task": self.task_id,
            "status": self.status,
            "base_expected": self.base_expected,
            "base_measured": self.base_measured,
            "branch": self.branch,
            "pr": self.pr,
            "mutations": self.changed_paths or ["NONE"],
            "validation": self.validation or ["NONE"],
            "discrepancies": self.discrepancies or ["NONE"],
            "decision_required": self.decision_required or ["NONE"],
            "claude_session_id": self.claude_session_id,
            "evidence": self.evidence or [],
            "next": {"authorized": "NONE"},
        }


def find_ready_task(github, repo_hint: str = "") -> tuple[int, Task] | None:
    """Discover exactly ONE executable task.

    Executable requires BOTH conditions, and the second is the one that was missing:

      1. the issue body declares `status: READY`  (declarative readiness), AND
      2. the durable ledger phase is WORKER_EXECUTE (no result posted yet).

    `status: READY` is a static string in a task body that nobody rewrites after the
    work is done, so condition 1 alone stays true forever. A worker relying on it
    re-executes a completed task - the exact duplicate-execution failure the ledger
    exists to prevent.
    """
    ready: list[tuple[int, Task]] = []
    for issue in github.list_issues(state="open"):
        number = issue["number"]
        body = github.get_issue(number).get("body") or ""
        if "mtj-task/" not in body:
            continue
        try:
            task = parse_task(body, number)
        except ProtocolError as exc:
            log.warning("issue has an mtj-task block that does not validate",
                        extra={"issue": number, "error": str(exc)})
            continue
        if not task.is_ready:
            continue
        phase = state_mod.reconstruct(github, number).next_phase()
        if phase != "WORKER_EXECUTE":
            log.info("task declares READY but the ledger says otherwise; not executable",
                     extra={"issue": number, "task": task.task, "phase": phase})
            continue
        ready.append((number, task))
    if not ready:
        return None
    if len(ready) > 1:
        raise PolicyError(
            "more than one READY task is open: "
            + ", ".join(f"#{n} ({t.task})" for n, t in ready)
            + ". The bridge executes one task at a time; mark the others BLOCKED."
        )
    return ready[0]


def run_validation(commands: list[list[str]], cwd: Path) -> list[dict]:
    """Run each allowlisted acceptance command IN THE WRAPPER and capture the evidence.

    The worker model cannot be the source of this evidence: it is the thing being
    checked. Output is bounded and redacted so a failing test dump cannot blow the
    Manager's context or leak a credential into a GitHub comment.
    """
    evidence: list[dict] = []
    for argv in commands:
        log.info("running wrapper-owned validation", extra={"argv": " ".join(argv)})
        try:
            proc = run(argv, cwd=cwd, timeout=1800, check=False)
            rc, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
        except Exception as exc:  # noqa: BLE001 - a runner failure IS the evidence
            rc, stdout, stderr = 127, "", redact(str(exc))
        tail = (stdout + ("\n" + stderr if stderr else ""))[-MAX_EVIDENCE_BYTES:]
        evidence.append({
            "command": argv,
            "rc": rc,
            "output_tail": redact(tail),
            "truncated": len(stdout) + len(stderr) > MAX_EVIDENCE_BYTES,
        })
    return evidence


def build_prompt(task: Task, bootstrap_files: dict[str, str], worktree: Path,
                 measured_base: str, issue_body: str) -> str:
    """Assemble everything a cold model needs. No transcript, no prior session."""
    sections = [
        WORKER_SYSTEM_BRIEF,
        "## Durable refoundation control plane\n",
    ]
    for name, text in bootstrap_files.items():
        sections.append(f"### {name}\n\n```\n{text.strip()}\n```\n")
    sections.append(
        "## Measured repository state\n\n"
        f"- working directory (isolated worktree, safe to edit): `{worktree}`\n"
        f"- task expected base: `{task.base}`\n"
        f"- measured base: `{measured_base}`\n"
        f"- branch: `{worktree.name}`\n"
    )
    sections.append(f"## Task contract (GitHub issue #{task.issue_number})\n\n{issue_body}\n")
    sections.append(
        "## Your instruction\n\nExecute the task contract above inside the working directory. "
        "Do not commit, push, or touch GitHub. When finished, summarise what you changed and "
        "what you validated."
    )
    return "\n".join(sections)


def read_bootstrap(git: GitOps, branch: str) -> dict[str, str]:
    """Read the control plane from a git ref, without checking anything out."""
    names = ["BOOTSTRAP-STATE.yaml", "CAPTAIN-DIRECTION.md", "SESSION-PROTOCOL.md", "WORKER-START.md"]
    out: dict[str, str] = {}
    for name in names:
        try:
            out[name] = git._git(["show", f"{branch}:refoundation/{name}"], check=True).stdout
        except BridgeCommandError:
            log.warning("bootstrap file missing from ref", extra={"ref": branch, "file": name})
    return out


def execute(task: Task, issue_body: str, *, github, git: GitOps, claude,
            repo: str, dry_run: bool = False, worktree_root: Path | None = None) -> WorkerOutcome:
    """Run one task end to end. The wrapper owns every effect."""
    worktree_root = worktree_root or WORKTREE_ROOT
    outcome = WorkerOutcome(task_id=task.task, status="COMPLETE", base_expected=task.base)

    # --- scope must be machine-readable before anything mutates ------------
    scope_stop = require_machine_readable_scope(task)
    if scope_stop:
        outcome.status = "STOP"
        outcome.discrepancies.append(scope_stop)
        log.error("refusing a mutating task with no machine-readable scope",
                  extra={"task": task.task})
        return outcome

    # --- acceptance commands are allowlisted before anything runs ----------
    try:
        validation_commands = check_validation_commands(task.validation_commands)
    except PolicyError as exc:
        outcome.status = "STOP"
        outcome.discrepancies.append(str(exc))
        return outcome

    # --- base verification: drift is a STOP, never an adaptation -----------
    git.fetch("origin", task.base_branch)
    try:
        measured = git.rev_parse(f"origin/{task.base_branch}")
    except BridgeCommandError as exc:
        outcome.status = "STOP"
        outcome.discrepancies.append(f"cannot resolve base branch: {exc}")
        return outcome
    outcome.base_measured = measured
    if measured != task.base:
        outcome.status = "STOP"
        outcome.discrepancies.append(
            f"base mismatch: task pins {task.base} but origin/{task.base_branch} is {measured}. "
            "Halting before invoking Claude, per the task's STOP conditions."
        )
        log.error("base mismatch; refusing to execute", extra={
            "expected": task.base, "measured": measured})
        return outcome

    # A dry run stops here, on purpose: the base check is the whole point of it,
    # and it is the one step that costs nothing. No worktree, no model, no writes.
    if dry_run:
        outcome.validation.append(
            f"DRY-RUN: base verified ({measured}); would create a worktree, invoke a fresh "
            "Claude session, and open a draft PR")
        return outcome

    # --- isolated worktree, never the Captain's dirty tree -----------------
    branch = f"mtj/{task.task.lower().replace('.', '-')}-{int(time.time())}"
    worktree = worktree_root / branch.replace("/", "_")
    worktree.parent.mkdir(parents=True, exist_ok=True)
    git.add_worktree(worktree, branch, task.base)
    outcome.branch = branch

    try:
        bootstrap = read_bootstrap(git, f"origin/{task.base_branch}")
        prompt = build_prompt(task, bootstrap, worktree, measured, issue_body)
        log.info("invoking a FRESH Claude session", extra={
            "task": task.task, "worktree": str(worktree), "prompt_bytes": len(prompt)})
        payload = claude.run_task(prompt, worktree)
        outcome.claude_session_id = payload.get("session_id", "")
        outcome.model_summary = redact(str(payload.get("result", "")))[:4000]
        if payload.get("is_error"):
            outcome.status = "FAIL"
            outcome.discrepancies.append(
                f"claude reported an error: {payload.get('subtype', 'unknown')}")
        denials = payload.get("permission_denials") or []
        if denials:
            outcome.discrepancies.append(f"claude hit {len(denials)} permission denial(s)")

        # --- what actually changed, measured, not claimed ------------------
        changed = git.changed_paths(worktree)
        outcome.changed_paths = changed
        log.info("worker changed paths", extra={"count": len(changed)})

        violations = check_paths_against_task(task, changed)
        if violations:
            outcome.status = "STOP"
            outcome.discrepancies.extend(["task scope violated:"] + violations)
            return outcome
        if changed and not task.allow_paths and not task.deny_paths:
            outcome.validation.append(
                "path scope NOT machine-checked: this task supplied no allow/deny globs")
        captain_hits = classify_paths(changed)
        for path, category in captain_hits:
            outcome.decision_required.append(f"{path} is Captain-reserved ({category})")
        if captain_hits:
            outcome.status = "STOP"
            outcome.discrepancies.append(
                "changed paths enter Captain-reserved territory; not opening a PR")
            return outcome

        # --- wrapper-owned acceptance validation, machine-captured -------
        outcome.evidence = run_validation(validation_commands, worktree)
        for item in outcome.evidence:
            outcome.validation.append(
                f"{' '.join(item['command'])} -> rc={item['rc']}")
        if any(item["rc"] != 0 for item in outcome.evidence):
            outcome.status = "FAIL"
            outcome.discrepancies.append(
                "wrapper-captured acceptance validation failed; not opening a PR")
            return outcome
        if not validation_commands:
            outcome.discrepancies.append(
                "task declared no validation.commands: the only evidence of correctness "
                "is model prose, which the wrapper cannot verify")

        if not changed:
            outcome.validation.append("no file changes produced")
            return outcome

        # --- wrapper-owned commit / push / draft PR ------------------------
        sha = git.commit_all(worktree, f"{task.task}: worker execution\n\nIssue #{task.issue_number}")
        outcome.validation.append(f"committed {sha}")
        git.push_branch(worktree, branch)
        if not dry_run:
            outcome.pr = github.create_draft_pr(
                title=f"[{task.task}] worker execution",
                body=(f"Draft PR for task `{task.task}` (issue #{task.issue_number}).\n\n"
                      f"Base: `{task.base_branch}` @ `{task.base}`\n\n"
                      "**DO NOT MERGE** — bridge v0 never merges its own PRs."),
                head=branch,
                base=task.base_branch,
            )
        return outcome
    finally:
        log.info("worktree retained for inspection", extra={"worktree": str(worktree)})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mtj-worker", description=__doc__)
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--issue", type=int, help="execute this issue instead of discovering one")
    parser.add_argument("--once", action="store_true", help="execute at most one task then exit")
    parser.add_argument("--dry-run", action="store_true",
                        help="discover, verify and plan, but make no mutation and call no model")
    parser.add_argument("--repo-root", default=str(Path.cwd()))
    parser.add_argument("--model", default=None)
    parser.add_argument("--log-level", default=None)
    args = parser.parse_args(argv)

    configure(args.log_level)
    github = GhCliGitHub(args.repo, dry_run=args.dry_run)
    git = GitOps(args.repo_root, dry_run=args.dry_run)
    claude = ClaudeCliAdapter(dry_run=args.dry_run,
                              **({"model": args.model} if args.model else {}))

    if args.issue:
        body = github.get_issue(args.issue).get("body") or ""
        task = parse_task(body, args.issue)
        # An explicit --issue must not become a back door around the ledger: the
        # duplicate-execution guard has to hold on the path an operator actually
        # types when re-running something by hand.
        phase = state_mod.reconstruct(github, args.issue).next_phase()
        if phase != "WORKER_EXECUTE":
            log.error("refusing to execute: the ledger says this task is not awaiting a worker",
                      extra={"issue": args.issue, "phase": phase, "task": task.task})
            return 2
        found = (args.issue, task)
    else:
        found = find_ready_task(github)
    if not found:
        log.info("no READY task found; nothing to do")
        return 0
    issue_number, task = found
    if not task.is_ready:
        log.error("task is not READY", extra={"issue": issue_number, "status": task.status})
        return 2

    log.info("selected task", extra={"issue": issue_number, "task": task.task,
                                     "dry_run": args.dry_run})
    if args.dry_run:
        print(render_block({"schema": "mtj-plan/1", "task": task.task, "issue": issue_number,
                            "base": task.base, "base_branch": task.base_branch,
                            "would_invoke": "claude -p (fresh session)",
                            "would_open": "draft PR", "would_merge": False}))
        return 0

    state_mod.acquire(github, issue_number, task.task)
    try:
        issue_body = github.get_issue(issue_number).get("body") or ""
        outcome = execute(task, issue_body, github=github, git=git, claude=claude, repo=args.repo)
        note = ("Worker execution summary (model text, redacted):\n\n"
                f"{outcome.model_summary}" if outcome.model_summary else "")
        github.post_comment(issue_number, render_block(outcome.to_payload(), note),
                            idempotency_key=f"result-{task.task}-{outcome.branch}")
        log.info("result posted", extra={"issue": issue_number, "status": outcome.status})
    finally:
        state_mod.release(issue_number)
    return 0


if __name__ == "__main__":
    sys.exit(main())
