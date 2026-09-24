"""The Worker-side supervisor: observe durable state, act at most once, report.

Design constraints this file exists to satisfy:

* it never decides what is authorized -- it reads Issue #1 and obeys;
* it acts on at most ONE actionable message per invocation, so a storm of
  redelivered webhooks cannot become a storm of executions;
* it refuses to act on a message its own actor produced, so the loop cannot
  feed itself;
* it is dry-run by default, and executing is an explicit flag at every layer.

Recovery is not a special mode. Every invocation re-derives the whole picture
from GitHub plus git trailers, so "resume after a crash" and "start fresh" are
the same code path with different inputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from agent_bus import errors as E
from agent_bus.errors import BusError
from agent_bus.git_evidence import branch as git_branch
from agent_bus.git_evidence import completed_units, dirty, head_sha
from agent_bus.issue import read_comments, resolve_authority
from agent_bus.machine import Authority, BusState, RawComment, fold
from agent_bus.protocol import Envelope
from agent_bus.shell import Runner
from agent_bus.transport import Dispatch, LocalClaudeTransport


@dataclass
class Observation:
    authority: Authority
    comments: list[RawComment]
    state: BusState


@dataclass
class Supervisor:
    repo_path: str
    repo_slug: str
    actor: str = "WORKER"
    issue: int = 1
    transport_pr: int | None = None
    trusted_authors: tuple[str, ...] = ()
    run: Runner = field(default_factory=Runner)
    transport: object | None = None

    def observe(self) -> Observation:
        issue_comments = read_comments(self.issue, self.repo_slug, self.run)
        authority = resolve_authority(issue_comments, self.issue)
        comments = list(issue_comments)
        if self.transport_pr:
            comments += read_comments(self.transport_pr, self.repo_slug, self.run,
                                      source=f"pr:{self.transport_pr}")
        # GitHub comment ids increase monotonically per repository, so id order is
        # arrival order across both surfaces. A self-reported timestamp is not used
        # for ordering: it is a field the sender controls.
        comments.sort(key=lambda c: c.comment_id)
        state = fold(comments, authority, self.trusted_authors)
        return Observation(authority, comments, state)

    def poll_once(self, execute: bool = False, resume: bool = False) -> dict:
        observation = self.observe()
        state = observation.state
        report: dict = {
            "actor": self.actor,
            "authority": observation.authority.as_dict(),
            "comments_read": len(observation.comments),
            "accepted": len(state.accepted()),
            "rejected": [r.as_dict() for r in state.rejected()],
            "inert": sum(1 for r in state.records if r.status == "INERT"),
            "pending": [e.message_id for e in state.pending_for(self.actor)],
            "action": None,
            "reason": None,
            "dispatch": None,
        }

        pending = state.pending_for(self.actor)
        if not pending:
            report["action"] = "NONE"
            report["reason"] = E.NOTHING_ACTIONABLE
            return report

        envelope = pending[0]
        report["selected"] = envelope.message_id

        if envelope.kind == "WAVE_ABORT":
            report["action"] = "ABORT"
            report["reason"] = envelope.body["reason"]
            return report

        wave_state = state.waves[envelope.wave]
        plan = wave_state.plan
        assert plan is not None  # a command without a plan cannot be ACCEPTED

        from_git = completed_units(self.repo_path, envelope.wave, envelope.base,
                                   run=self.run)
        resume_plan = state.resume(envelope.wave, from_git)
        report["resume"] = resume_plan
        report["repo"] = {
            "branch": git_branch(self.repo_path, self.run),
            "head": head_sha(self.repo_path, self.run),
            "dirty": list(dirty(self.repo_path, self.run)),
        }

        if wave_state.claimed and not resume:
            # Durable evidence says somebody already picked this command up. A
            # redelivered event must not become a second execution.
            report["action"] = "NONE"
            report["reason"] = E.ALREADY_CLAIMED
            return report

        remaining = resume_plan["runnable"]
        if not remaining:
            report["action"] = "NONE"
            report["reason"] = E.NOTHING_ACTIONABLE
            return report

        transport = self.transport or LocalClaudeTransport(self.repo_path, run=self.run)
        dispatch: Dispatch = transport.dispatch(
            envelope, plan, remaining, resumed=resume, dry_run=not execute)
        report["action"] = "DISPATCH" if execute else "DISPATCH_DRY_RUN"
        report["dispatch"] = dispatch.as_dict()
        report["transport"] = getattr(transport, "name", type(transport).__name__)
        return report


def wake_check(envelope: Envelope, actor: str) -> bool:
    """Would this message wake `actor`? The single question every trigger asks."""
    return envelope.wakes(actor)


def rejected_codes(state: BusState) -> list[str]:
    return sorted({r.code for r in state.rejected() if r.code})


def require_clean_selection(state: BusState, actor: str) -> Envelope:
    pending = state.pending_for(actor)
    if not pending:
        raise BusError(E.NOTHING_ACTIONABLE, f"nothing addressed to {actor}")
    return pending[0]


def summarise(state: BusState, actors: Sequence[str] = ("WORKER", "MANAGER")) -> dict:
    return {actor: [e.message_id for e in state.pending_for(actor)] for actor in actors}
