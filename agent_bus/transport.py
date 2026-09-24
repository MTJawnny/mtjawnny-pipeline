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

import uuid
from dataclasses import dataclass
from typing import Sequence

from agent_bus import errors as E
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

    def as_dict(self) -> dict:
        return {
            "argv": list(self.argv),
            "session": self.session,
            "resumed": self.resumed,
            "executed": self.executed,
            "returncode": None if self.result is None else self.result.returncode,
        }


def worker_brief(envelope: Envelope, plan: WavePlan, remaining: Sequence[str],
                 repo: str) -> str:
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
        f"Remaining pre-authorized units, in order:\n{units}\n\n"
        "Rules for this wave:\n"
        "  - Finishing a unit is NOT a stop condition; continue to the next one.\n"
        "  - Commit each mutating unit separately and end its commit message with\n"
        "    the Agent-Bus-Wave / Agent-Bus-Unit trailers.\n"
        "  - Do not accept your own work, do not move the accepted head, do not merge.\n"
        "  - STOP at the wave review boundary, or on any declared STOP condition.\n\n"
        "The authorizing command, verbatim:\n\n" + envelope.render()
    )


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
                "--permission-mode", self.permission_mode, "--add-dir", self.repo]
        argv += ["--resume", session] if resumed else ["--session-id", session]
        if self.model:
            argv += ["--model", self.model]
        return tuple(argv)

    def dispatch(self, envelope: Envelope, plan: WavePlan, remaining: Sequence[str],
                 resumed: bool = False, dry_run: bool = True) -> Dispatch:
        prompt = worker_brief(envelope, plan, remaining, self.repo)
        session = session_id(envelope.wave)
        argv = self.argv(prompt, session, resumed)
        if dry_run:
            return Dispatch(argv, prompt, session, resumed, executed=False)
        result = self.run(argv, timeout=None)
        if result.returncode != 0:
            raise BusError(E.TRANSPORT_FAILED,
                           f"{self.executable} exited {result.returncode}: "
                           f"{result.stderr.strip()[:400]}")
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
                 resumed: bool = False, dry_run: bool = True) -> Dispatch:
        raise BusError(
            E.TRANSPORT_FAILED,
            "hosted GitHub Action transport is not armed; missing: "
            + ", ".join(self.missing),
        )
