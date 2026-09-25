"""The Worker-side supervisor: observe, prove it is safe, act, measure, report.

Design constraints this file exists to satisfy:

* it never decides what is authorized -- it reads Issue #1 and obeys;
* it refuses to speak to a model until git says the checkout is the one the wave
  named, on the right base, clean;
* it acts on at most ONE actionable message per invocation, so a storm of
  redelivered webhooks cannot become a storm of executions;
* it refuses to act on a message its own actor produced, so the loop cannot feed
  itself;
* it re-measures after EVERY unit and refuses to advance when a unit stepped
  outside the scope it was authorized for;
* it crosses unit boundaries by itself and stops at the wave boundary, which is
  the whole point of a bounded wave;
* it is dry-run by default, and executing is an explicit flag at every layer.

Recovery is not a special mode. Every invocation re-derives the whole picture from
GitHub plus git trailers, so "resume after a crash" and "start fresh" are the same
code path with different inputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Sequence

from agent_bus import compose
from agent_bus import errors as E
from agent_bus.enforce import UnitVerdict, verify_unit
from agent_bus.errors import BusError
from agent_bus.git_evidence import completed_units
from agent_bus.issue import Resolution, post_comment, read_comments, resolve_authority
from agent_bus.machine import Authority, BusState, RawComment, fold
from agent_bus.preflight import Checkout, PreflightReport, build_base_of, inspect, preflight
from agent_bus.protocol import Envelope
from agent_bus.shell import Runner
from agent_bus.providers import (
    DEFAULT_ORDER, ProviderFailoverTransport, ProviderOrder, build_providers,
    live_authority_probe,
)
from agent_bus.transport import Dispatch
from agent_bus.trust import NOBODY, Trust
from agent_bus.wave import WavePlan


@dataclass
class Observation:
    resolution: Resolution
    comments: list[RawComment]
    state: BusState

    @property
    def authority(self) -> Authority:
        return self.resolution.authority


@dataclass
class Supervisor:
    repo_path: str
    repo_slug: str
    trust: Trust = NOBODY
    actor: str = "WORKER"
    issue: int = 1
    transport_pr: int | None = None
    run: Runner = field(default_factory=Runner)
    transport: object | None = None
    clock: Callable | None = None
    max_units: int | None = None
    # Operator configuration, resolved by the caller from outside the repository
    # (`agent_bus.providers.resolve_order`). The supervisor never reads it itself,
    # and nothing it observes on the bus can change it.
    providers: ProviderOrder | None = None
    _local: ProviderFailoverTransport | None = field(default=None, init=False, repr=False)

    def local_transport(self) -> ProviderFailoverTransport:
        """The provider-neutral local transport, built once per supervisor.

        Once, so a provider's own session opened for one unit is still resumable
        by that provider for the next unit, across watcher cycles in one process.
        """
        if self._local is None:
            order = self.providers or ProviderOrder(DEFAULT_ORDER, "default")
            self._local = ProviderFailoverTransport(
                self.repo_path, build_providers(order, self.repo_path),
                authority_probe=live_authority_probe(self.observe), run=self.run)
        return self._local

    # ---------------------------------------------------------------- observe
    def observe(self) -> Observation:
        issue_comments = read_comments(self.issue, self.repo_slug, self.run)
        transport = None
        if self.transport_pr:
            transport = read_comments(self.transport_pr, self.repo_slug, self.run,
                                      source=f"pr:{self.transport_pr}")
        # The transport is handed to the resolver too: a publisher checkpoint is
        # judged against the Worker message it answers, by every reader alike.
        resolution = resolve_authority(issue_comments, self.issue, self.trust,
                                       transport=transport, transport_pr=self.transport_pr)
        comments = list(issue_comments) + list(transport or ())
        # GitHub comment ids increase monotonically per repository, so id order is
        # arrival order across both surfaces. A self-reported timestamp is not used
        # for ordering: it is a field the sender controls.
        comments.sort(key=lambda c: c.comment_id)
        state = fold(comments, resolution.authority, self.trust)
        return Observation(resolution, comments, state)

    # ------------------------------------------------------------------- poll
    def poll_once(self, execute: bool = False, resume: bool = False) -> dict:
        if execute:
            # Nothing runs unattended without a declared speaker set. This is the
            # last place the question can still be asked cheaply.
            self.trust.require()
        observation = self.observe()
        state = observation.state
        report: dict = {
            "actor": self.actor,
            "authority": observation.resolution.as_dict(),
            "trust": self.trust.as_dict(),
            "comments_read": len(observation.comments),
            "accepted": len(state.accepted()),
            "rejected": [r.as_dict() for r in state.rejected()],
            "inert": sum(1 for r in state.records if r.status == "INERT"),
            "pending": [e.message_id for e in state.pending_for(self.actor)],
            # Cancellation and supersession are reported, never queued: they are
            # state the Worker obeys by NOT dispatching, not work it can finish.
            "aborted": sorted(w for w, s in state.waves.items() if s.aborted),
            "superseded": state.superseded(),
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
        wave_state = state.waves[envelope.wave]
        plan = wave_state.plan
        assert plan is not None  # a command without a plan cannot be ACCEPTED

        base = build_base_of(envelope)
        from_git = completed_units(self.repo_path, envelope.wave, base, run=self.run)
        resume_plan = state.resume(envelope.wave, from_git)
        report["resume"] = resume_plan

        # PREFLIGHT RUNS BEFORE EVERY DECISION BELOW, dry run included. A dry run
        # whose preflight was skipped would report a dispatch that could not
        # legally have happened.
        check: PreflightReport = preflight(envelope, plan, self.repo_path,
                                           resume_plan["completed"], self.run)
        report["preflight"] = check.as_dict()
        if not check.ok:
            report["action"] = "NONE"
            report["reason"] = E.PREFLIGHT_FAILED
            return report

        if wave_state.claimed and not resume:
            # Durable evidence says somebody already picked this command up. A
            # redelivered event must not become a second execution.
            report["action"] = "NONE"
            report["reason"] = E.ALREADY_CLAIMED
            return report

        runnable: list[str] = list(resume_plan["runnable"])
        if self.max_units is not None:
            runnable = runnable[: self.max_units]
        if not runnable:
            report["action"] = "NONE"
            report["reason"] = E.NOTHING_ACTIONABLE
            return report

        transport = self.transport or self.local_transport()
        report["transport"] = getattr(transport, "name", type(transport).__name__)
        if isinstance(transport, ProviderFailoverTransport):
            source = (self.providers.source if self.providers else "default") \
                if transport is self._local else "injected"
            report["providers"] = ProviderOrder(transport.order, source).as_dict()
        resumed = bool(wave_state.claimed or resume)

        if not execute:
            dispatch: Dispatch = transport.dispatch(
                envelope, plan, runnable[:1], resumed=resumed, dry_run=True,
                queue=runnable[1:])
            report["action"] = "DISPATCH_DRY_RUN"
            report["dispatch"] = dispatch.as_dict()
            report["planned_units"] = runnable
            return report

        return self._run_wave(report, observation, envelope, plan, runnable,
                              transport, resumed, check.checkout)

    # -------------------------------------------------------------- execution
    def _run_wave(self, report: dict, observation: Observation, command: Envelope,
                  plan: WavePlan, runnable: Sequence[str], transport,
                  resumed: bool, checkout: Checkout) -> dict:
        """One unit at a time, each one measured before the next may start.

        Unit completion is NOT a review boundary: nothing here waits for a
        Manager between units. What it does wait for is the repository agreeing
        that the unit did what it was authorized to do.
        """
        authority = observation.authority
        posted: list[dict] = []
        outcomes: list[dict] = []
        dispatches: list[dict] = []
        stopped: tuple[str, str] | None = None

        for index, unit_id in enumerate(runnable):
            unit = plan.unit(unit_id)
            before = self._head()
            dispatch: Dispatch = transport.dispatch(
                command, plan, [unit_id], resumed=resumed or index > 0, dry_run=False,
                queue=list(runnable[index + 1:]))
            dispatches.append(dispatch.as_dict())
            after = self._head()
            dirty = self._dirty()

            verdict: UnitVerdict = verify_unit(self.repo_path, command.wave, unit,
                                               before, after, dirty, self.run)
            outcomes.append(verdict.as_dict())
            status = "DONE" if verdict.ok else "FAILED"
            commit = verdict.commits[-1] if verdict.commits else None
            posted.append(self._post(compose.progress(
                command, authority, unit_id, status, commit,
                note="" if verdict.ok else verdict.problems[0][0], clock=self.clock)))

            if not verdict.ok:
                stopped = (E.UNIT_SCOPE_ESCAPE if any(
                    p[0] == E.UNIT_SCOPE_ESCAPE for p in verdict.problems)
                    else verdict.problems[0][0], unit_id)
                break

        head = self._head()
        unit_rows = [{"id": o["unit"], "status": "DONE" if o["ok"] else "FAILED",
                      **({"commit": o["commits"][-1]} if o["commits"] else {})}
                     for o in outcomes]
        result = compose.result(
            command, authority,
            status="P" if stopped is None else "F",
            branch=checkout.branch, head=head, units=unit_rows,
            validation=[f"{o['unit']}: {'ok' if o['ok'] else 'rejected'}" for o in outcomes],
            discrepancies=[] if stopped is None else [f"{stopped[0]} at {stopped[1]}"],
            clock=self.clock)
        posted.append(self._post(result))

        report["action"] = "WAVE_RAN" if stopped is None else "WAVE_STOPPED"
        report["reason"] = None if stopped is None else stopped[0]
        report["units"] = outcomes
        report["dispatch"] = dispatches[-1] if dispatches else None
        report["dispatches"] = dispatches
        report["posted"] = posted
        return report

    # ----------------------------------------------------------------- git io
    def _head(self) -> str:
        return inspect(self.repo_path, self.run).head

    def _dirty(self) -> list[str]:
        return list(inspect(self.repo_path, self.run).dirty)

    def _post(self, envelope: Envelope) -> dict:
        target = self.transport_pr or self.issue
        post_comment(envelope.render(), target, self.repo_slug, self.run, dry_run=False)
        return {"message_id": envelope.message_id, "kind": envelope.kind,
                "target": f"{'pr' if self.transport_pr else 'issue'}:{target}"}


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
