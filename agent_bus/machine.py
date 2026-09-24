"""Fold an ordered comment stream into bus state, under an external authority.

The load-bearing sentence of this module: **authority is an input, never an
output.** `Authority` is read from GitHub Issue #1 (`latest K -> active T`) and
handed in. No message on the bus can set it, move it, or become it -- a WAVE_REVIEW
that claims a new accepted head records a Manager PROPOSAL, and the accepted head
in this state stays whatever the checkpoint says until a checkpoint says otherwise.

That is what stops the transport surface from quietly becoming a second selector
merely because it contains newer prose.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence

from agent_bus import errors as E
from agent_bus.errors import BusError
from agent_bus.protocol import Envelope, parse_comment
from agent_bus.trust import Trust
from agent_bus.wave import WavePlan, plan_from_command, remaining_after

ACCEPTED = "ACCEPTED"
INERT = "INERT"
REJECTED = "REJECTED"


@dataclass(frozen=True)
class Authority:
    """Durable selection, read from Issue #1. Not derived from the bus."""

    issue: int
    checkpoint: int  # comment id of the latest K
    task: int  # comment id of the active T (`a`)
    accepted_head: str  # `h` from that K

    def as_dict(self) -> dict:
        return {
            "issue": self.issue,
            "checkpoint": self.checkpoint,
            "task": self.task,
            "accepted_head": self.accepted_head,
        }


@dataclass(frozen=True)
class RawComment:
    source: str  # "issue:1", "pr:71" -- where it was read, never why it is law
    comment_id: int
    author: str
    body: str


@dataclass(frozen=True)
class Record:
    source: str
    comment_id: int
    author: str
    status: str  # ACCEPTED | INERT | REJECTED
    code: str | None
    detail: str
    envelope: Envelope | None

    def as_dict(self) -> dict:
        return {
            "source": self.source,
            "comment_id": self.comment_id,
            "author": self.author,
            "status": self.status,
            "code": self.code,
            "detail": self.detail,
            "message_id": self.envelope.message_id if self.envelope else None,
            "kind": self.envelope.kind if self.envelope else None,
            "actor": self.envelope.actor if self.envelope else None,
        }


@dataclass
class WaveState:
    wave: str
    command: Envelope | None = None
    plan: WavePlan | None = None
    progress: list[Envelope] = field(default_factory=list)
    result: Envelope | None = None
    review: Envelope | None = None
    aborted: Envelope | None = None
    captain_required: list[Envelope] = field(default_factory=list)

    @property
    def claimed(self) -> bool:
        """Has the Worker already picked this command up?

        Any durable Worker message parented to the command is a claim. This is
        the idempotency rule for duplicate delivery: a redelivered command whose
        wave is already claimed is a no-op, not a second execution.
        """
        return bool(self.progress or self.result)

    @property
    def answered(self) -> bool:
        """A wave is answered when a durable RESULT exists -- nothing else.

        An abort is not an answer: it cancels the work, and the Worker still has
        to see it. Collapsing the two is how a cancelled wave would silently look
        finished.
        """
        return self.result is not None

    def completed_units(self) -> list[str]:
        done = {p.body["unit"] for p in self.progress if p.body["status"] == "DONE"}
        if self.result:
            done |= {u["id"] for u in self.result.body["units"] if u["status"] == "DONE"}
        return sorted(done)

    def failed_units(self) -> list[str]:
        bad = {p.body["unit"] for p in self.progress if p.body["status"] == "FAILED"}
        if self.result:
            bad |= {u["id"] for u in self.result.body["units"] if u["status"] in ("FAILED", "BLOCKED")}
        return sorted(bad - set(self.completed_units()))


@dataclass
class BusState:
    authority: Authority
    trust: Trust
    records: list[Record] = field(default_factory=list)
    waves: dict[str, WaveState] = field(default_factory=dict)

    @property
    def accepted_head(self) -> str:
        """Always the checkpoint's `h`. There is no bus path that writes this."""
        return self.authority.accepted_head

    def accepted(self) -> list[Envelope]:
        return [r.envelope for r in self.records if r.status == ACCEPTED and r.envelope]

    def rejected(self) -> list[Record]:
        return [r for r in self.records if r.status == REJECTED]

    def pending_for(self, actor: str) -> list[Envelope]:
        """Messages this actor must act on, oldest first.

        A message wakes an actor only when its KIND is addressed to that actor
        and its ACTOR is somebody else, so no agent can ever wake itself.
        """
        out: list[Envelope] = []
        for env in self.accepted():
            if not env.wakes(actor):
                continue
            state = self.waves.get(env.wave)
            if state is None:
                continue
            # A CLAIMED command stays pending on purpose. Half-finished work is
            # still work; whether to re-enter it is a dispatch decision made once,
            # with durable evidence in hand -- see `Supervisor.poll_once`.
            if env.kind == "WAVE_COMMAND" and (state.answered or state.aborted):
                continue
            if env.kind in ("WAVE_RESULT", "CAPTAIN_REQUIRED") and state.review is not None:
                continue
            if env.kind == "WAVE_ABORT" and state.answered:
                continue
            out.append(env)
        return out

    def pending_acceptance(self) -> list[dict]:
        """Manager ACCEPT verdicts that no checkpoint has ratified yet.

        A verdict on the bus is a proposal. Until a `K` carries the head, the
        accepted head has not moved, and this list is how that gap stays visible
        instead of being papered over by the newest comment.
        """
        out = []
        for wave, state in sorted(self.waves.items()):
            review = state.review
            if review is None or review.body["verdict"] != "ACCEPT":
                continue
            proposed = review.body.get("accepted_head")
            if proposed and proposed != self.authority.accepted_head:
                out.append(
                    {
                        "wave": wave,
                        "message_id": review.message_id,
                        "proposed_accepted_head": proposed,
                        "checkpoint_accepted_head": self.authority.accepted_head,
                        "ratified": False,
                    }
                )
        return out

    def resume(self, wave: str, completed_from_git: Iterable[str] = ()) -> dict:
        state = self.waves.get(wave)
        if state is None or state.plan is None:
            raise BusError(E.WAVE_NOT_SELECTED, f"no authorized wave {wave} on this bus")
        completed = set(state.completed_units()) | set(completed_from_git)
        plan = remaining_after(state.plan, completed, state.failed_units())
        plan["claimed"] = state.claimed
        plan["answered"] = state.answered
        plan["review_boundary"] = state.plan.review_boundary
        plan["branch"] = state.plan.branch
        plan["accepted_head"] = self.accepted_head
        plan["requires_captain"] = bool(state.captain_required) and state.review is None
        return plan

    def as_dict(self) -> dict:
        return {
            "schema_state": "mtj-agent-bus-state/1",
            "authority": self.authority.as_dict(),
            "trust": self.trust.as_dict(),
            "accepted_head": self.accepted_head,
            # Inert comments are COUNTED, never listed: an ordinary human comment
            # is not an event, and a state dump that drowns in them hides the
            # handful of records that are.
            "inert": sum(1 for r in self.records if r.status == INERT),
            "records": [r.as_dict() for r in self.records if r.status != INERT],
            "waves": {
                w: {
                    "command": s.command.message_id if s.command else None,
                    "units": list(s.plan.order) if s.plan else [],
                    "completed": s.completed_units(),
                    "failed": s.failed_units(),
                    "claimed": s.claimed,
                    "answered": s.answered,
                    "result": s.result.message_id if s.result else None,
                    "review": s.review.body["verdict"] if s.review else None,
                    "aborted": bool(s.aborted),
                }
                for w, s in sorted(self.waves.items())
            },
            "pending_worker": [e.message_id for e in self.pending_for("WORKER")],
            "pending_manager": [e.message_id for e in self.pending_for("MANAGER")],
            "pending_acceptance": self.pending_acceptance(),
        }


def fold(comments: Sequence[RawComment], authority: Authority,
         trust: Trust) -> BusState:
    """Classify every comment in order and build the state it implies.

    Ordering is the caller's: GitHub comment id order. Nothing here re-sorts by
    a timestamp inside a message, because a self-reported time is exactly the
    kind of field a replayed or forged message controls.

    `trust` is REQUIRED and fails closed. An empty speaker set trusts nobody, so
    an unconfigured bus classifies every message as untrusted rather than
    treating "no restriction configured" as "no restriction wanted". The
    repository is public; that default is the difference between a control plane
    and an open command line.
    """
    state = BusState(authority=authority, trust=trust)
    seen_ids: dict[str, int] = {}

    for comment in comments:
        try:
            envelope = parse_comment(comment.body)
        except BusError as exc:
            state.records.append(
                Record(comment.source, comment.comment_id, comment.author, REJECTED,
                       exc.code, exc.detail, None))
            continue

        if envelope is None:
            state.records.append(
                Record(comment.source, comment.comment_id, comment.author, INERT,
                       None, "no bus envelope", None))
            continue

        problem = _correlate(envelope, state, authority, seen_ids, comment, trust)
        if problem is not None:
            state.records.append(
                Record(comment.source, comment.comment_id, comment.author, REJECTED,
                       problem.code, problem.detail, envelope))
            continue

        seen_ids[envelope.message_id] = comment.comment_id
        state.records.append(
            Record(comment.source, comment.comment_id, comment.author, ACCEPTED,
                   None, "", envelope))
        _apply(envelope, state)

    return state


def _correlate(envelope: Envelope, state: BusState, authority: Authority,
               seen_ids: Mapping[str, int], comment: RawComment,
               trust: Trust) -> BusError | None:
    """Return the rejection for this envelope, or None if it is live and correlated."""
    # Speaker trust is checked FIRST and unconditionally. A message from someone
    # who may not command is not "a valid message from the wrong person"; it is
    # not read for meaning at all.
    if not trust.trusts(comment.author):
        return BusError(E.UNTRUSTED_AUTHOR,
                        f"{comment.author} is not a trusted bus speaker")

    if envelope.message_id in seen_ids:
        return BusError(E.DUPLICATE_MESSAGE_ID,
                        f"{envelope.message_id} already delivered as comment "
                        f"{seen_ids[envelope.message_id]}")

    if envelope.authority["issue"] != authority.issue:
        return BusError(E.STALE_AUTHORITY,
                        f"cites issue {envelope.authority['issue']}, live issue is {authority.issue}")
    if envelope.authority["checkpoint"] != authority.checkpoint:
        return BusError(E.STALE_AUTHORITY,
                        f"cites checkpoint {envelope.authority['checkpoint']}, "
                        f"latest K is {authority.checkpoint}")
    if envelope.authority["task"] != authority.task:
        return BusError(E.WAVE_NOT_SELECTED,
                        f"cites task {envelope.authority['task']}, active T is {authority.task}")
    if envelope.base != authority.accepted_head:
        return BusError(E.STALE_BASE,
                        f"pinned base {envelope.base} is not accepted head {authority.accepted_head}")

    # A Worker message may never carry an accepted-head claim.
    if envelope.actor == "WORKER" and "accepted_head" in envelope.body:
        return BusError(E.UNAUTHORIZED_ACCEPTED_HEAD, "a Worker cannot move the accepted head")

    existing = state.waves.get(envelope.wave)

    if envelope.kind == "WAVE_COMMAND":
        if existing is not None and existing.command is not None:
            return BusError(E.WAVE_ALREADY_COMMANDED,
                            f"wave {envelope.wave} was already commanded by "
                            f"{existing.command.message_id}")
        try:
            plan_from_command(envelope.wave, envelope.body)
        except BusError as exc:
            return exc
        return None

    if envelope.parent is not None:
        if envelope.parent not in seen_ids:
            return BusError(E.UNKNOWN_PARENT,
                            f"{envelope.message_id} answers unknown {envelope.parent}")
        parent_env = _envelope_by_id(state, envelope.parent)
        if parent_env is None:
            return BusError(E.UNKNOWN_PARENT, f"parent {envelope.parent} was not accepted")
        if parent_env.wave != envelope.wave:
            return BusError(E.PARENT_WAVE_MISMATCH,
                            f"parent {envelope.parent} belongs to wave {parent_env.wave}")
        expected = {
            "WAVE_PROGRESS": {"WAVE_COMMAND"},
            "WAVE_RESULT": {"WAVE_COMMAND"},
            "WAVE_REVIEW": {"WAVE_RESULT", "CAPTAIN_REQUIRED"},
        }.get(envelope.kind)
        if expected and parent_env.kind not in expected:
            return BusError(E.PARENT_KIND_MISMATCH,
                            f"{envelope.kind} cannot answer a {parent_env.kind}")

    if envelope.kind in ("WAVE_PROGRESS", "WAVE_RESULT") and (
            existing is None or existing.command is None):
        return BusError(E.WAVE_NOT_SELECTED, f"no authorized command for wave {envelope.wave}")

    if envelope.kind == "WAVE_PROGRESS":
        unit = envelope.body["unit"]
        if existing.plan is None or unit not in existing.plan.order:
            return BusError(E.UNKNOWN_DEPENDENCY,
                            f"unit {unit} is not authorized in wave {envelope.wave}")

    if envelope.kind == "WAVE_RESULT":
        authorized = set(existing.plan.order) if existing.plan else set()
        claimed = {u["id"] for u in envelope.body["units"]}
        extra = sorted(claimed - authorized)
        if extra:
            return BusError(E.UNKNOWN_DEPENDENCY,
                            f"result reports unauthorized units: {', '.join(extra)}")

    return None


def _envelope_by_id(state: BusState, message_id: str) -> Envelope | None:
    for record in state.records:
        if record.status == ACCEPTED and record.envelope and record.envelope.message_id == message_id:
            return record.envelope
    return None


def _apply(envelope: Envelope, state: BusState) -> None:
    wave_state = state.waves.setdefault(envelope.wave, WaveState(wave=envelope.wave))
    if envelope.kind == "WAVE_COMMAND":
        wave_state.command = envelope
        wave_state.plan = plan_from_command(envelope.wave, envelope.body)
    elif envelope.kind == "WAVE_PROGRESS":
        wave_state.progress.append(envelope)
    elif envelope.kind == "WAVE_RESULT":
        wave_state.result = envelope
    elif envelope.kind == "WAVE_REVIEW":
        wave_state.review = envelope
    elif envelope.kind == "WAVE_ABORT":
        wave_state.aborted = envelope
    elif envelope.kind == "CAPTAIN_REQUIRED":
        wave_state.captain_required.append(envelope)
