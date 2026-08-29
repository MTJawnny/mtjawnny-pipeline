"""mtj-cycle — run exactly ONE complete Worker->Manager cycle, then stop.

This is the operator command the task contract requires before unattended
polling is enabled. It never loops on its own: one worker execution, one manager
review, one durable decision, exit.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import manager, worker
from .adapters import ClaudeCliAdapter, GhCliGitHub, GitOps, OpenAIResponsesAdapter
from .logging_setup import configure, get_logger
from .policy import Action

log = get_logger(__name__)


def run_cycle(*, github, git, claude, model, repo: str, base_branch: str,
              issue_number: int | None = None, dry_run: bool = False) -> int:
    if issue_number is None:
        found = worker.find_ready_task(github)
        if not found:
            log.info("no READY task; cycle is a no-op")
            return 0
        issue_number, task = found
    else:
        body = github.get_issue(issue_number).get("body") or ""
        from .protocol import parse_task

        task = parse_task(body, issue_number)

    ledger_phase = None
    from . import state as state_mod

    ledger = state_mod.reconstruct(github, issue_number)
    ledger_phase = ledger.next_phase()
    log.info("reconstructed phase from GitHub alone", extra={"issue": issue_number,
                                                             "phase": ledger_phase})

    if ledger_phase == "WORKER_EXECUTE":
        issue_body = github.get_issue(issue_number).get("body") or ""
        outcome = worker.execute(task, issue_body, github=github, git=git, claude=claude,
                                 repo=repo, dry_run=dry_run)
        from .protocol import render_block

        note = (f"Worker execution summary (model text, redacted):\n\n{outcome.model_summary}"
                if outcome.model_summary else "")
        if not dry_run:
            github.post_comment(issue_number, render_block(outcome.to_payload(), note),
                                idempotency_key=f"result-{task.task}-{outcome.branch}")
        if outcome.status in ("STOP", "FAIL"):
            log.error("worker halted; not proceeding to review in this cycle",
                      extra={"status": outcome.status})
            return 3
        ledger_phase = "MANAGER_REVIEW"

    if ledger_phase == "MANAGER_REVIEW":
        decision = manager.review_once(github=github, git=git, model=model, repo=repo,
                                       issue_number=issue_number, base_branch=base_branch,
                                       dry_run=dry_run)
        if decision.action == Action.HALT or decision.verdict != "PASS":
            return 3
        return 0

    log.info("nothing to do", extra={"phase": ledger_phase})
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mtj-cycle", description=__doc__)
    parser.add_argument("--repo", default=worker.DEFAULT_REPO)
    parser.add_argument("--issue", type=int, default=None)
    parser.add_argument("--base-branch", default="refoundation-manager-bootstrap-2026-08-28")
    parser.add_argument("--once", action="store_true", default=True,
                        help="always on in v0; there is no loop mode yet")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--repo-root", default=str(Path.cwd()))
    parser.add_argument("--log-level", default=None)
    args = parser.parse_args(argv)

    configure(args.log_level)
    return run_cycle(
        github=GhCliGitHub(args.repo, dry_run=args.dry_run),
        git=GitOps(args.repo_root, dry_run=args.dry_run),
        claude=ClaudeCliAdapter(dry_run=args.dry_run),
        model=OpenAIResponsesAdapter(dry_run=args.dry_run),
        repo=args.repo, base_branch=args.base_branch,
        issue_number=args.issue, dry_run=args.dry_run,
    )


if __name__ == "__main__":
    sys.exit(main())
