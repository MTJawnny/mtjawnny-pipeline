"""Claude-side execution transports. The protocol does not depend on any of them.

Two transports are defined, and the choice between them is a measurement, not a
preference:

* `LocalClaudeTransport` -- runs the operator's already-authenticated Claude Code
  CLI non-interactively (`claude -p`). It needs no Anthropic API key, no secret
  in the repository and no hosted runner, which is why it is the default.
* `HostedActionTransport` -- records that a hosted GitHub-Actions path was asked
  for, and refuses to pretend it is armed. Arming it requires repository-side
  configuration the Worker is not authorized to perform (a secret, and a workflow
  on the DEFAULT branch), so this transport reports the exact missing step
  instead of failing silently or faking a dispatch.

Every transport supports `dry_run`, and dry run is the default everywhere.
"""

from __future__ import annotations

import json

import uuid
from dataclasses import dataclass
from typing import Sequence

from agent_bus import errors as E
from agent_bus.worker_evidence import (
    FOOTER_FENCE, MAX_EVIDENCE_BYTES, failure_detail, footer_block,
)

FOOTER_EXAMPLE = footer_block(
    "DONE", ["agent_bus/example.py"],
    [("python3 -m unittest tests.refoundation.test_agent_bus_worker_evidence", 0)])
from agent_bus.errors import BusError
from agent_bus.protocol import Envelope
from agent_bus.shell import Completed, Runner
from agent_bus.wave import WavePlan

# A stable namespace so one wave always maps to one Claude session id. Resuming
# after a crash therefore continues the SAME conversation rather than starting a
# fresh one that has to rediscover the wave.
SESSION_NAMESPACE = uuid.UUID("6f1b0f6a-3f0a-5d21-9d24-0f5f6a1b2c3d")


def session_id(wave: str) -> str:
    return str(uuid.uuid5(SESSION_NAMESPACE, wave))


@dataclass(frozen=True)
class Dispatch:
    argv: tuple[str, ...]
    prompt: str
    session: str
    resumed: bool
    executed: bool
    result: Completed | None = None
    provider: str = "claude"
    # Every provider tried for this unit before `provider`, with the classified
    # evidence that let the next one run. Empty when the first provider answered.
    attempts: tuple[dict, ...] = ()

    def as_dict(self) -> dict:
        return {
            "argv": list(self.argv),
            "session": self.session,
            "resumed": self.resumed,
            "executed": self.executed,
            "returncode": None if self.result is None else self.result.returncode,
            "provider": self.provider,
            "attempts": [dict(a) for a in self.attempts],
        }


def worker_brief(envelope: Envelope, plan: WavePlan, remaining: Sequence[str],
                 repo: str, queue: Sequence[str] = ()) -> str:
    """The exact text handed to the Worker session. Deterministic, no chat state.

    It carries the command verbatim. It does not summarise the command, because a
    summary is a second source of truth and the whole point of the bus is that
    there is one.
    """
    units = "\n".join(
        f"  - {uid}: {plan.unit(uid).objective}\n"
        f"      allow: {', '.join(plan.unit(uid).allow_paths) or '(read-only)'}\n"
        f"      validation: {'; '.join(plan.unit(uid).validation)}"
        for uid in remaining
    )
    return (
        "Agent Bus wave execution.\n\n"
        "Root CLAUDE.md is your contract and GitHub Issue #1 remains the only task\n"
        "authority. This brief transports an already-authorized command; it is not\n"
        "itself authority. If it disagrees with Issue #1, STOP and report it.\n\n"
        f"repository: {repo}\n"
        f"wave: {envelope.wave}\n"
        f"branch: {plan.branch}\n"
        f"base (accepted head): {envelope.base}\n"
        f"authority: issue {envelope.authority['issue']} "
        f"checkpoint {envelope.authority['checkpoint']} task {envelope.authority['task']}\n"
        f"review boundary: {plan.review_boundary}\n\n"
        f"Units to execute in THIS invocation, in order:\n{units}\n\n"
        + (f"Still queued after this invocation: {', '.join(queue)}\n\n" if queue else "")
        +
        "Rules for this wave:\n"
        "  - Finishing a unit is NOT a stop condition; continue to the next one.\n"
        "  - Edit and test files only. Never commit, push, reset, stash, clean,\n"
        "    checkout, rebase, stage, or otherwise mutate Git metadata. The trusted\n"
        "    Agent Bus host proves scope, then commits each mutating unit with the\n"
        "    Agent-Bus-Wave / Agent-Bus-Unit trailers and pushes it after you finish.\n"
        "    Any Git mutation by you fails the unit.\n"
        "  - Do not accept your own work, do not move the accepted head, do not merge.\n"
        "  - STOP at the wave review boundary, or on any declared STOP condition.\n"
        "  - This is a headless Agent Bus invocation. Your final response is\n"
        "    machine-captured Worker evidence for the supervisor, not a human-facing\n"
        "    reply, so the direct interactive 'Claude done' convention does not apply.\n"
        "    It must be substantive: state concisely what changed and what validation\n"
        "    ran, with its outcome. A final response that is only 'Claude done',\n"
        "    'done' or 'ok' is refused as evidence and the unit fails. Do not post the\n"
        "    detailed X/result yourself; the supervisor publishes your evidence.\n"
        f"  - Keep the whole final response under {MAX_EVIDENCE_BYTES} UTF-8 bytes; a\n"
        "    longer one is refused, never truncated.\n"
        f"  - End the final response with exactly one ```{FOOTER_FENCE} fenced JSON\n"
        "    footer and nothing after it. `changed` lists every path you added,\n"
        "    modified or deleted (the host checks it against Git; [] for a read-only\n"
        "    unit); `validation` lists each check you ran with its exit code; `status`\n"
        "    is DONE, or STOP if you could not complete the unit (say why above the\n"
        "    footer). Example:\n"
        + FOOTER_EXAMPLE + "\n\n"
        "The authorizing command, verbatim:\n\n" + envelope.render()
    )


# Headless Claude runs least-privileged, whatever the operator's own Claude
# settings allow interactively. No user, project or local settings file is
# loaded (the operator's global allowlist, and a settings file the provider
# could plant in the checkout, both stay out); these bus-owned settings are the
# only ones. The Bash sandbox confines every write to the checkout and the
# temp dir, so the provider cannot reach the host's git config, credentials or
# the bus itself; nothing can prompt, so anything needing approval is denied;
# and Git metadata commands are denied outright (the host owns them).
HEADLESS_CLAUDE_SETTINGS = {
    # failIfUnavailable: without it a missing sandbox is a warning and commands
    # run unsandboxed; here it is a refusal to start.
    "sandbox": {"enabled": True, "failIfUnavailable": True,
                "autoAllowBashIfSandboxed": True, "allowUnsandboxedCommands": False},
    "permissions": {
        "allow": ["Bash(python3:*)", "Bash(git status:*)", "Bash(git diff:*)",
                  "Bash(git log:*)", "Bash(git show:*)", "Bash(git rev-parse:*)"],
        "deny": [f"Bash(git {verb}:*)" for verb in (
            "add", "commit", "push", "stash", "reset", "checkout", "switch", "restore",
            "rebase", "merge", "cherry-pick", "revert", "clean", "fetch", "pull",
            "tag", "branch", "update-ref", "config", "worktree", "rm", "mv")],
    },
}


class LocalClaudeTransport:
    """The operator's own authenticated Claude Code CLI, run headless."""

    name = "local-claude-cli"

    def __init__(self, repo: str, executable: str = "claude",
                 model: str | None = None,
                 permission_mode: str = "acceptEdits",
                 run: Runner | None = None) -> None:
        self.repo = repo
        self.executable = executable
        self.model = model
        self.permission_mode = permission_mode
        self.run = run or Runner()

    def argv(self, prompt: str, session: str, resumed: bool) -> tuple[str, ...]:
        argv = [self.executable, "-p", prompt, "--output-format", "json",
                "--permission-mode", self.permission_mode, "--add-dir", self.repo,
                "--setting-sources", "", "--permission-prompts", "none",
                "--settings", json.dumps(HEADLESS_CLAUDE_SETTINGS, sort_keys=True)]
        argv += ["--resume", session] if resumed else ["--session-id", session]
        if self.model:
            argv += ["--model", self.model]
        return tuple(argv)

    def dispatch(self, envelope: Envelope, plan: WavePlan, remaining: Sequence[str],
                 resumed: bool = False, dry_run: bool = True,
                 queue: Sequence[str] = ()) -> Dispatch:
        prompt = worker_brief(envelope, plan, remaining, self.repo, queue)
        session = session_id(envelope.wave)
        argv = self.argv(prompt, session, resumed)
        if dry_run:
            return Dispatch(argv, prompt, session, resumed, executed=False)
        # The sandbox's writable root is the working directory: pin it to the
        # checkout, never whatever directory the watcher happened to start in.
        result = self.run(argv, timeout=None, cwd=self.repo)
        if result.returncode != 0:
            raise BusError(E.TRANSPORT_FAILED,
                           f"{self.executable} exited {result.returncode}: "
                           f"{failure_detail('claude', result)}")
        return Dispatch(argv, prompt, session, resumed, executed=True, result=result)


class HostedActionTransport:
    """The hosted GitHub-Actions path -- declared, measured, and NOT armed.

    It stays a named transport rather than a paragraph of prose so that choosing
    it produces a deterministic, actionable refusal naming what is missing.
    """

    name = "hosted-github-action"

    def __init__(self, missing: Sequence[str]) -> None:
        self.missing = tuple(missing)

    def dispatch(self, envelope: Envelope, plan: WavePlan, remaining: Sequence[str],
                 resumed: bool = False, dry_run: bool = True,
                 queue: Sequence[str] = ()) -> Dispatch:
        raise BusError(
            E.TRANSPORT_FAILED,
            "hosted GitHub Action transport is not armed; missing: "
            + ", ".join(self.missing),
        )
