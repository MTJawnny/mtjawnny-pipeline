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
from .adapters import BridgeCommandError, GhCliGitHub, GitOps, OpenAIResponsesAdapter
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


CANARY_PROMPT = """\
This is a READ-ONLY connectivity and contract canary for the MTJ refoundation bridge.

No repository work is being reviewed. Confirm you can produce a schema-valid review
block and nothing else.

Return exactly one fenced yaml block:

```yaml
schema: mtj-review/1
task: BRIDGE.CANARY
verdict: PASS
reasons:
  - canary reached the manager model and returned a valid review block
findings:
  - NONE
```
"""


def run_canary(model, *, dry_run: bool = False) -> tuple[bool, str]:
    """Exercise the REAL manager model end to end, read-only, writing nothing.

    Proves three things the offline suite cannot: the credential resolves, the
    configured model exists, and its output survives `parse_review` + the policy
    schema gate. Run this before any live mutation cycle.
    """
    if dry_run:
        return True, "DRY-RUN: canary not sent"
    text = model.review(CANARY_PROMPT, REVIEW_SCHEMA_HINT)
    if not text.strip():
        return False, "manager model returned empty text"
    try:
        review = parse_review(text)
    except ProtocolError as exc:
        return False, f"manager model output did not validate as mtj-review/1: {exc}"
    if review.verdict not in ("PASS", "REPAIR", "CAPTAIN_DECISION_REQUIRED", "STOP"):
        return False, f"verdict out of domain: {review.verdict}"
    return True, f"canary OK: model returned a valid mtj-review/1 with verdict {review.verdict}"


def build_review_prompt(*, bootstrap: dict[str, str], issue_body: str, result_body: str,
                        changed_paths: list[str], pr_number: int | None,
                        diff_text: str = "", diff_truncated: bool = False,
                        evidence: list[dict] | None = None) -> str:
    """Assemble everything a cold reviewer needs to judge IMPLEMENTATION TRUTH.

    A path list says what was touched; only the patch says what was done. The task
    contract required reconstruction from task + result + PR diff + evidence, so the
    actual diff and the wrapper-captured validation output both belong here.
    """
    parts = ["## Durable refoundation control plane\n"]
    for name, text in bootstrap.items():
        parts.append(f"### {name}\n\n```\n{text.strip()}\n```\n")
    parts.append(f"## Task contract\n\n{issue_body}\n")
    parts.append(f"## Worker result\n\n{result_body}\n")
    parts.append(
        "## Measured changed paths\n\n"
        + (f"PR #{pr_number}\n" if pr_number else "no PR opened\n")
        + ("\n".join(f"- {p}" for p in changed_paths) if changed_paths else "- (no files changed)")
        + "\n"
    )

    ev = evidence or []
    if ev:
        lines = ["## Wrapper-captured acceptance evidence\n",
                 "These commands were run by the WRAPPER, not by the worker model.\n"]
        for item in ev:
            lines.append(f"### `{' '.join(item.get('command', []))}` -> rc={item.get('rc')}"
                         + (" (output truncated)" if item.get("truncated") else ""))
            lines.append(f"```\n{(item.get('output_tail') or '').strip()}\n```\n")
        parts.append("\n".join(lines))
    else:
        parts.append("## Wrapper-captured acceptance evidence\n\n"
                     "NONE. A MUTATING task cannot reach this state - it is refused before "
                     "execution and again at publication - so this is either a read-only task "
                     "or a result produced outside the wrapper. The only account of correctness "
                     "is then model prose. Weigh it accordingly.\n")

    # A partial diff must never reach the model. Asking it not to PASS on one was
    # prompt wording, and prompt wording is the model's own restraint standing in for
    # a structural guarantee - the exact inversion of "model output may only ever make
    # the outcome MORE restrictive". Refusing here makes it unreachable by construction,
    # so a future caller that forgets the check in `review_once` still cannot bypass it.
    if diff_truncated:
        raise PolicyError(
            "refusing to build a review prompt around a TRUNCATED diff: a partial patch "
            "is not implementation truth, and no instruction to the model can make it one"
        )
    if diff_text:
        parts.append(f"## Actual PR diff\n\n```diff\n{diff_text}\n```\n")
    else:
        parts.append("## Actual PR diff\n\nUNAVAILABLE - no diff could be fetched.\n")

    parts.append(
        "## Your task\n\nReview the Worker result against the task contract, the actual diff, "
        "and the captured evidence. Judge only what the evidence supports. Then return the "
        "review block."
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
    diff_text, diff_truncated = "", False
    if result.pr:
        try:
            changed_paths = github.pr_changed_paths(result.pr)
        except Exception as exc:  # noqa: BLE001 - a diff read failure must not be silent
            log.warning("could not read PR files", extra={"pr": result.pr, "error": str(exc)})
        try:
            diff_text, diff_truncated = github.pr_diff(result.pr)
            log.info("fetched PR diff", extra={"pr": result.pr, "bytes": len(diff_text),
                                               "truncated": diff_truncated})
        except Exception as exc:  # noqa: BLE001
            log.warning("could not read PR diff", extra={"pr": result.pr, "error": str(exc)})
    if not changed_paths:
        changed_paths = [m for m in result.mutations if m not in ("NONE",)]

    # A mutation task the reviewer cannot actually SEE is not reviewable. Both arms
    # halt BEFORE the model is invoked, so the model-call count is zero and there is
    # no verdict for policy to have to override.
    if result.pr and not diff_text:
        return Decision(
            action=Action.HALT, verdict="STOP",
            reasons=(f"PR #{result.pr} exists but its diff could not be fetched; refusing to "
                     "review implementation truth from a path list alone",))
    if result.pr and diff_truncated:
        return Decision(
            action=Action.HALT, verdict="STOP",
            reasons=(f"PR #{result.pr} diff exceeded the size bound and came back TRUNCATED. "
                     "Only a complete bounded diff may reach an automated Manager PASS path in "
                     "v0; split the change, or review it by hand.",))

    from .worker import read_bootstrap

    bootstrap = read_bootstrap(git, f"origin/{base_branch}")
    prompt = build_review_prompt(bootstrap=bootstrap, issue_body=issue_body,
                                 result_body=render_block(result.raw),
                                 changed_paths=changed_paths, pr_number=result.pr,
                                 diff_text=diff_text, diff_truncated=diff_truncated,
                                 evidence=result.evidence)
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
    parser.add_argument("--issue", type=int, default=0)
    parser.add_argument("--base-branch", default="refoundation-manager-bootstrap-2026-08-28")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the review that would be posted; write nothing")
    parser.add_argument("--repo-root", default=str(Path.cwd()))
    parser.add_argument("--model", default=None)
    parser.add_argument("--max-repairs", type=int, default=2)
    parser.add_argument("--max-cycles", type=int, default=8)
    parser.add_argument("--log-level", default=None)
    parser.add_argument("--canary", action="store_true",
                        help="read-only: exercise the real manager model and exit; writes nothing")
    args = parser.parse_args(argv)

    configure(args.log_level)
    if args.canary:
        model = OpenAIResponsesAdapter(dry_run=args.dry_run,
                                       **({"model": args.model} if args.model else {}))
        try:
            ok, message = run_canary(model, dry_run=args.dry_run)
        except BridgeCommandError as exc:
            log.error("canary could not run", extra={"error": str(exc)})
            print(f"CANARY BLOCKED: {exc}")
            return 4
        print(message)
        return 0 if ok else 4
    github = GhCliGitHub(args.repo, dry_run=args.dry_run)
    git = GitOps(args.repo_root, dry_run=args.dry_run)
    if not args.issue:
        parser.error("--issue is required unless --canary is given")
    model = OpenAIResponsesAdapter(dry_run=args.dry_run,
                                   **({"model": args.model} if args.model else {}))
    # The adapter normalises every SDK failure into BridgeCommandError; the review
    # path must then surface it as a controlled exit, exactly as --canary does.
    # Otherwise H5's repair holds for the canary and leaks a traceback here.
    try:
        decision = review_once(github=github, git=git, model=model, repo=args.repo,
                               issue_number=args.issue, base_branch=args.base_branch,
                               dry_run=args.dry_run, max_repairs=args.max_repairs,
                               max_cycles=args.max_cycles)
    except BridgeCommandError as exc:
        log.error("manager review could not run", extra={"error": str(exc)})
        print(f"MANAGER BLOCKED: {exc}")
        return 4
    return 0 if decision.automation_may_continue or decision.verdict == "PASS" else 3


if __name__ == "__main__":
    sys.exit(main())
