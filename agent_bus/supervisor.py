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
* it, not the provider, owns Git: a provider edits and tests, and the host
  proves scope, commits the unit and pushes it (`agent_bus.finalize`);
* it crosses unit boundaries by itself and stops at the wave boundary, which is
  the whole point of a bounded wave;
* it is dry-run by default, and executing is an explicit flag at every layer.

Recovery is not a special mode. Every invocation re-derives the whole picture from
GitHub plus git trailers, so "resume after a crash" and "start fresh" are the same
code path with different inputs.
"""

from __future__ import annotations

import json

from dataclasses import dataclass, field
from typing import Callable, Sequence

from agent_bus import compose, finalize, goal, worker_evidence
from agent_bus import errors as E
from agent_bus.enforce import UnitVerdict, verify_unit
from agent_bus.errors import BusError
from agent_bus.git_evidence import completed_units, head_sha
from agent_bus.issue import AuthorityError, Resolution, post_comment, read_comments, resolve_authority
from agent_bus.machine import Authority, BusState, RawComment, fold
from agent_bus.preflight import (Checkout, PreflightReport, build_base_of, inspect, preflight,
                                 require_exclusive)
from agent_bus.protocol import SHA_RE, Envelope, parse_comment
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
    # The remote the host pushes each unit commit to, non-force, on the wave's branch.
    remote: str = "origin"
    # Codex usage gate and Worker handoff store (operator configuration).
    usage: Callable | None = None
    handoff_dir: str | None = None
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
                authority_probe=live_authority_probe(self.observe), run=self.run,
                usage=self.usage, handoff_dir=self.handoff_dir)
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
        if execute:
            # A commit can recover scope progress, never a lost model response.
            # Git-completed units need durable evidence before execute/resume may
            # report anything, BUS_NOTHING_ACTIONABLE included. Dry runs stay inert.
            report["worker_evidence"] = self._prior_evidence(
                observation, envelope, resume_plan["completed"])
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
            # Before every unit, not only the wave: a worktree added mid-wave would
            # make the ref proof below meaningless. Nothing has run; nothing to claim.
            require_exclusive(self.repo_path, self.run)
            before = finalize.snapshot(self.repo_path, self.run)
            unsafe = finalize.unsafe_config(before)
            if unsafe:
                # Before any dispatch: nothing ran, nothing to claim. The
                # operator removes the driver; the bus never guesses around it.
                raise BusError(E.HOST_GIT_UNSAFE,
                               "host git would execute programs named in the checkout's "
                               "config; remove them before any Worker runs: "
                               + "; ".join(unsafe))
            dispatch: Dispatch = transport.dispatch(
                command, plan, [unit_id], resumed=resumed or index > 0, dry_run=False,
                queue=list(runnable[index + 1:]))
            dispatches.append(dispatch.as_dict())

            # The order is the law: evidence and its footer, then the footer's
            # paths against Git, then provider-Git and scope proof, then the
            # host's own commit and push, then ordinary verification, then
            # durable evidence, and only then progress. Evidence that cannot be
            # extracted fails the unit before any commit exists -- and the
            # FAILED progress and F result below still claim the command, so a
            # redelivery never dispatches it a second time.
            text, verdict = self._settle(command, unit, plan, dispatch, before)
            after = self._head()
            outcomes.append(verdict.as_dict())
            if text is not None:
                # A failed unit's evidence is published too (marked F with its
                # problems): the reason a Worker stopped is exactly what the
                # reviewer needs. It never counts as completion evidence.
                try:
                    body = worker_evidence.render(
                        command, unit_id, after, dispatch.provider, text,
                        problems=None if verdict.ok else verdict.problems)
                    reference = self._post_evidence(body)
                except BusError as exc:
                    # No PASS without durable evidence -- and no unclaimed
                    # command either: try to claim it as FAILED, then raise.
                    self._claim_failed(command, authority, unit_id, exc, checkout)
                    raise
                report.setdefault("worker_evidence", []).append(reference)
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
            validation=[f"{o['unit']}: {'ok' if o['ok'] else 'rejected'}" for o in outcomes]
                       + [f"Worker evidence (not acceptance): {ref}" for ref in report.get("worker_evidence", [])],
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

    def _claim_failed(self, command: Envelope, authority, unit_id: str, exc: BusError,
                      checkout: Checkout) -> None:
        """Best effort: FAILED progress and an F result, so a redelivery of this
        command is ALREADY_CLAIMED rather than a second dispatch. A post that
        fails here is swallowed; the original error is what gets raised."""
        try:
            self._post(compose.progress(command, authority, unit_id, "FAILED", None,
                                        note=exc.code, clock=self.clock))
            self._post(compose.result(
                command, authority, status="F", branch=checkout.branch, head=self._head(),
                units=[{"id": unit_id, "status": "FAILED"}],
                validation=[f"{unit_id}: rejected"],
                discrepancies=[f"{exc.code} at {unit_id}"], clock=self.clock))
        except (BusError, AuthorityError, ValueError):
            pass

    def _settle(self, command: Envelope, unit, plan: WavePlan, dispatch: Dispatch,
                before) -> tuple[str | None, UnitVerdict]:
        """(evidence text or None, verdict) for one dispatched unit."""
        failed = lambda code, detail, paths=(): UnitVerdict(unit.id, False, ((code, detail),),
                                                            (), tuple(paths))
        try:
            text = worker_evidence.extract(dispatch.provider, dispatch.result)
            stated = worker_evidence.footer(text)
        except BusError as exc:
            if exc.code != E.WORKER_EVIDENCE_INVALID:
                raise
            return None, failed(exc.code, str(exc).split(": ", 1)[-1])
        try:
            # The wrapper must fit BEFORE anything is committed: a response that
            # passes the raw bound can still escape past the comment limit.
            worker_evidence.render(command, unit.id, "0" * 40, dispatch.provider, text,
                                   problems=[(E.WORKER_EVIDENCE_INVALID, "x" * 2000)])
        except BusError as exc:
            return None, failed(exc.code, str(exc).split(": ", 1)[-1])
        if stated.status == "STOP":
            return text, failed(E.WORKER_STOPPED,
                                f"{dispatch.provider} reported STOP for {unit.id}; "
                                "its reason is in the published Worker evidence")
        # Metadata first, exactly as finalize orders it: `git status` never runs
        # over config or refs the provider changed. Finalize repeats the proof.
        mutated = finalize.git_mutations(before, finalize.snapshot(self.repo_path, self.run), ())
        if mutated:
            return text, failed(*finalize.mutation_failure(self.repo_path, dispatch.provider,
                                                           unit.id, mutated, self.run))
        measured = tuple(sorted({path for _, path in
                                 finalize.worktree_changes(self.repo_path, self.run)}))
        if stated.changed != measured:
            return text, failed(E.WORKER_EVIDENCE_MISMATCH,
                                f"footer says changed {list(stated.changed)}, Git measured "
                                f"{list(measured)} (nothing staged)", measured)
        host = finalize.finalize(self.repo_path, self.remote, plan.branch, command, unit,
                                 dispatch.provider, before, self.run)
        if not host.ok:
            return text, UnitVerdict(unit.id, False, host.problems, (), host.paths)
        return text, verify_unit(self.repo_path, command.wave, unit, before.head,
                                 self._head(), self._dirty(), self.run)

    def _post_evidence(self, body: str) -> str:
        try:
            receipt = post_comment(body, self.issue, self.repo_slug, self.run, dry_run=False)
            payload = json.loads(receipt.stdout) if receipt is not None else None
            comment_id = payload.get("id") if isinstance(payload, dict) else None
            if type(comment_id) is not int or comment_id <= 0:
                raise ValueError("GitHub did not return a positive comment id")
        except (AuthorityError, BusError, ValueError) as exc:
            raise BusError(E.WORKER_EVIDENCE_POST_FAILED,
                           f"Worker evidence was not durably acknowledged on Issue #{self.issue}: {exc}") from exc
        return f"https://github.com/{self.repo_slug}/issues/{self.issue}#issuecomment-{comment_id}"

    def _wave_commands(self, observation: Observation, command: Envelope) -> dict:
        """`command` plus every earlier trusted command it supersedes for the SAME
        work: same wave, same task, and bound to the same goal plan and digest --
        so the same planned units. A superseding command (a corrected base, a
        recovery) may then credit a unit whose durable evidence names the command
        that ran it. Evidence is still required, rendered exactly against the
        command it names; git trailers alone still recover nothing."""
        chain = {command.message_id: command}
        ref = command.body.get("goal")
        if ref is None:
            return chain
        work = goal._canon(goal.template_of(command.body))
        earlier = []
        for comment in observation.comments:
            if not self.trust.trusts(comment.author) or "```mtj-bus" not in comment.body:
                continue
            try:
                env = parse_comment(comment.body)
            except BusError:
                continue
            if env is None or env.kind != "WAVE_COMMAND" or env.actor != "MANAGER":
                continue
            if env.message_id == command.message_id:
                break                 # only commands printed BEFORE the current one
            if (env.wave == command.wave
                    and env.authority.get("task") == command.authority.get("task")
                    and env.authority.get("issue") == command.authority.get("issue")
                    and env.body.get("goal") == ref
                    # the same planned work, not merely the same plan reference
                    and goal._canon(goal.template_of(env.body)) == work):
                earlier.append(env)
        else:
            return chain              # the current command is not on the stream
        for env in earlier:
            chain.setdefault(env.message_id, env)
        return chain

    def _prior_evidence(self, observation: Observation, command: Envelope,
                        completed: Sequence[str]) -> list[str]:
        references = []
        chain = self._wave_commands(observation, command) if completed else {}
        for unit in completed:
            candidates = []
            for comment in observation.comments:
                if (comment.source != f"issue:{self.issue}" or not self.trust.trusts(comment.author)
                        or not comment.body.startswith(worker_evidence.PREFIX)
                        or not comment.body.endswith(worker_evidence.SUFFIX)):
                    continue
                try:
                    payload = json.loads(comment.body[len(worker_evidence.PREFIX):-len(worker_evidence.SUFFIX)])
                    if (not isinstance(payload, dict) or payload.get("command") not in chain
                            or payload.get("unit") != unit or "outcome" in payload):
                        continue
                    expected = worker_evidence.render(chain[payload["command"]], unit,
                                                      payload["head"], payload["provider"],
                                                      payload["response"])
                    if expected != comment.body:
                        continue
                    if not SHA_RE.fullmatch(payload["head"]):
                        continue
                    # Completion evidence must itself be well-formed evidence.
                    if worker_evidence.footer(payload["response"]).status != "DONE":
                        continue
                    check = self.run(["git", "-C", self.repo_path, "merge-base", "--is-ancestor",
                                      payload["head"], "HEAD"])
                    if check.returncode != 0:
                        continue
                    candidates.append((comment.comment_id, comment.body))
                except (ValueError, KeyError, TypeError, BusError):
                    continue
            if not candidates or len({body for _, body in candidates}) != 1:
                raise BusError(E.WORKER_EVIDENCE_INVALID,
                               f"completed unit {unit} lacks unambiguous durable Worker evidence on Issue #{self.issue}; "
                               "git trailers alone cannot recover the provider response")
            references.append(f"https://github.com/{self.repo_slug}/issues/{self.issue}#issuecomment-{candidates[0][0]}")
        return references

    # ----------------------------------------------------------------- git io
    def _head(self) -> str:
        # `rev-parse` only: after a refused unit the host must not run `git status`
        # against metadata a provider may have tampered with.
        return head_sha(self.repo_path, self.run)

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
