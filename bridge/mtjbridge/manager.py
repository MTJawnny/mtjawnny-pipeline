"""mtj-manager — review one Worker result with a FRESH model invocation.

The model reconstructs context from durable state only (bootstrap + task issue +
worker result + PR diff), emits `mtj-review/1`, and touches nothing. Every write
that follows is chosen by `policy.decide()`, which contains no model call.

    model text  ->  parse_review()  ->  policy.decide()  ->  at most one action

A model that returns garbage, or that returns PASS on Captain-reserved territory,
cannot cause a mutation. That is the whole point of the split.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import state as state_mod
from .adapters import GhCliGitHub, GitOps, OpenAIResponsesAdapter
from .logging_setup import configure, get_logger
from .policy import Action, Decision, PolicyError, decide
from .protocol import ProtocolError, Review, parse_review, parse_task, render_block

log = get_logger(__name__)

DEFAULT_REPO = "MTJawnny/mtjawnny-pipeline"

REVIEW_SCHEMA_HINT = """\
Return ONLY one fenced yaml block, nothing else:

```yaml
schema: mtj-review/1
task: <task id exactly as in the result>
verdict: PASS | REPAIR | CAPTAIN_DECISION_REQUIRED | STOP
reasons:
  - <short factual reason>
findings:
  - <specific defect, or NONE>
captain_question:
  - <only when verdict is CAPTAIN_DECISION_REQUIRED>
next_task:
  id: <only when a successor is already defined and authorized, else empty>
```

Verdict meanings:
  PASS   the result satisfies the task contract as written.
  REPAIR a bounded, mechanical fix is needed and NO Captain decision is involved.
  CAPTAIN_DECISION_REQUIRED  semantic truth, authority, ratification, gate
         weakening, ambiguous deletion, or a conflict between durable authorities.
  STOP   drift, base mismatch, scope violation, or anything you cannot adjudicate.

You have no tools. You cannot run anything. Do not ask for more context: if the
durable state provided is insufficient to review, that is itself a finding and
you should return STOP saying so.
"""


def build_review_prompt(*, bootstrap: dict[str, str], issue_body: str, result_body: str,
                        changed_paths: list[str], pr_number: int | None) -> str:
    parts = ["## Durable refoundation control plane\n"]
    for name, text in bootstrap.items():
        parts.append(f"### {name}\n\n```\n{text.strip()}\n```\n")
    parts.append(f"## Task contract\n\n{issue_body}\n")
    parts.append(f"## Worker result\n\n{result_body}\n")
    parts.append(
        "## Measured PR diff paths\n\n"
        + (f"PR #{pr_number}\n" if pr_number else "no PR opened\n")
        + ("\n".join(f"- {p}" for p in changed_paths) if changed_paths else "- (no files changed)")
        + "\n"
    )
    parts.append(
        "## Your task\n\nReview the Worker result against the task contract and the durable "
        "control plane. Judge only what the evidence supports. Then return the review block."
    )
    return "\n".join(parts)


def render_decision_comment(decision: Decision, review: Review | None) -> str:
    payload = {
        "schema": "mtj-review/1",
        "task": review.task if review else "unknown",
        "verdict": decision.verdict,
        "model_verdict": review.verdict if review else "none",
        "action": decision.action,
        "automation_may_continue": decision.automation_may_continue,
        "reasons": list(decision.reasons) or ["NONE"],
        "findings": list(review.findings) if review else ["NONE"],
        "captain_categories": list(decision.captain_categories) or ["NONE"],
    }
    note = ""
    if decision.verdict == "CAPTAIN_DECISION_REQUIRED":
        note = (
            "### CAPTAIN DECISION PACKET\n\n"
            "Automation is **halted** and will not resume until Captain rules.\n\n"
            "**Reserved categories triggered**\n"
            + "\n".join(f"- {c}" for c in decision.captain_categories)
            + "\n\n**Why the automation stopped**\n"
            + "\n".join(f"- {r}" for r in decision.reasons)
            + "\n\nNo mutation was made on the strength of the model verdict."
        )
    elif decision.verdict == "STOP":
        note = ("### AUTOMATION HALTED\n\n"
                + "\n".join(f"- {r}" for r in decision.reasons))
    return render_block(payload, note)


def review_once(*, github, git: GitOps, model, repo: str, issue_number: int,
                base_branch: str, dry_run: bool = False,
                max_repairs: int = 2, max_cycles: int = 8) -> Decision:
    """Review the latest Worker result on one issue. Returns the policy Decision."""
    issue_body = github.get_issue(issue_number).get("body") or ""
    task = parse_task(issue_body, issue_number)
    ledger = state_mod.reconstruct(github, issue_number)
    if ledger.parse_errors:
        for err in ledger.parse_errors:
            log.warning("unparseable protocol comment", extra={"detail": err})
    result = ledger.latest_result
    if result is None:
        log.info("no worker result to review yet", extra={"issue": issue_number})
        return Decision(action=Action.HALT, verdict="STOP",
                        reasons=("no mtj-result/1 comment on this issue yet",))

    changed_paths: list[str] = []
    if result.pr:
        try:
            changed_paths = github.pr_changed_paths(result.pr)
        except Exception as exc:  # noqa: BLE001 - a diff read failure must not be silent
            log.warning("could not read PR diff", extra={"pr": result.pr, "error": str(exc)})
            changed_paths = []
    if not changed_paths:
        changed_paths = [m for m in result.mutations if m not in ("NONE",)]

    from .worker import read_bootstrap

    bootstrap = read_bootstrap(git, f"origin/{base_branch}")
    prompt = build_review_prompt(bootstrap=bootstrap, issue_body=issue_body,
                                 result_body=render_block(result.raw),
                                 changed_paths=changed_paths, pr_number=result.pr)
    log.info("invoking a FRESH manager model", extra={"prompt_bytes": len(prompt),
                                                      "issue": issue_number})
    text = model.review(prompt, REVIEW_SCHEMA_HINT)
    if not text.strip():
        return Decision(action=Action.HALT, verdict="STOP",
                        reasons=("manager model returned an empty review",))
    try:
        review = parse_review(text)
    except ProtocolError as exc:
        log.error("model review failed schema validation", extra={"error": str(exc)})
        return Decision(action=Action.HALT, verdict="STOP",
                        reasons=(f"model review did not validate as mtj-review/1: {exc}",))

    decision = decide(task=task, result=result, review=review, changed_paths=changed_paths,
                      repair_count=ledger.repair_count, max_repairs=max_repairs,
                      cycle_count=len(ledger.reviews), max_cycles=max_cycles)
    log.info("policy decision", extra={"model_verdict": review.verdict,
                                       "policy_verdict": decision.verdict,
                                       "action": decision.action})

    body = render_decision_comment(decision, review)
    if dry_run:
        print(body)
        return decision
    github.post_comment(issue_number, body,
                        idempotency_key=f"review-{review.task}-{len(ledger.results)}")

    if decision.action == Action.CREATE_REPAIR_TASK:
        log.info("policy authorizes ONE bounded repair task; not created automatically in v0",
                 extra={"issue": issue_number})
    return decision


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mtj-manager", description=__doc__)
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--issue", type=int, required=True)
    parser.add_argument("--base-branch", default="refoundation-manager-bootstrap-2026-08-28")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the review that would be posted; write nothing")
    parser.add_argument("--repo-root", default=str(Path.cwd()))
    parser.add_argument("--model", default=None)
    parser.add_argument("--max-repairs", type=int, default=2)
    parser.add_argument("--max-cycles", type=int, default=8)
    parser.add_argument("--log-level", default=None)
    args = parser.parse_args(argv)

    configure(args.log_level)
    github = GhCliGitHub(args.repo, dry_run=args.dry_run)
    git = GitOps(args.repo_root, dry_run=args.dry_run)
    model = OpenAIResponsesAdapter(dry_run=args.dry_run,
                                   **({"model": args.model} if args.model else {}))
    decision = review_once(github=github, git=git, model=model, repo=args.repo,
                           issue_number=args.issue, base_branch=args.base_branch,
                           dry_run=args.dry_run, max_repairs=args.max_repairs,
                           max_cycles=args.max_cycles)
    return 0 if decision.automation_may_continue or decision.verdict == "PASS" else 3


if __name__ == "__main__":
    sys.exit(main())
