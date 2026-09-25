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
from agent_bus.transition import review_id, same_message, successor_command, txn_id
from agent_bus.trust import PUBLISHER_ROLES, Trust
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
    # The K's own fields when the PUBLISHER wrote it (already validated as the
    # exact next link of the chain); None when a trusted human did.
    publisher: Mapping[str, str] | None = field(default=None, compare=False)

    def as_dict(self) -> dict:
        out = {
            "issue": self.issue,
            "checkpoint": self.checkpoint,
            "task": self.task,
            "accepted_head": self.accepted_head,
        }
        if self.publisher is not None:
            out["publisher_transaction"] = self.publisher["transaction"]
        return out


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

    def newest_command(self) -> Envelope | None:
        """The last WAVE_COMMAND accepted under the live authority, or None.

        Every accepted command already cites the same checkpoint and task, so
        "newest" is the Manager's latest word inside the selected task. It is
        positional, not "newest still runnable": aborting the newest command
        must leave nothing to run, never hand the Worker the one before it.
        """
        commands = [e for e in self.accepted() if e.kind == "WAVE_COMMAND"]
        return commands[-1] if commands else None

    def manager_queue(self) -> list[Envelope]:
        """What the Manager must answer, oldest first. Only the head is due.

        `pending_for("MANAGER")` minus work that was cancelled or replaced. A
        message for an aborted or superseded wave is never reviewed -- cancelled
        work does not resurrect -- and it must not sit at the head of the queue
        either, or it would starve every message behind it: the Worker side's
        abort-starvation defect, on the Manager side.
        """
        superseded = set(self.superseded())
        return [e for e in self.pending_for("MANAGER")
                if not self.waves[e.wave].aborted and e.wave not in superseded]

    def record_of(self, message_id: str) -> Record | None:
        """The ACCEPTED record that carried this message id, if any."""
        for record in self.records:
            if record.status == ACCEPTED and record.envelope is not None \
                    and record.envelope.message_id == message_id:
                return record
        return None

    def superseded(self) -> list[str]:
        """Waves whose command a newer accepted command has replaced, in order."""
        newest = self.newest_command()
        return [e.wave for e in self.accepted()
                if e.kind == "WAVE_COMMAND" and e is not newest]

    def pending_for(self, actor: str) -> list[Envelope]:
        """Messages this actor must act on, oldest first.

        A message wakes an actor only when its KIND is addressed to that actor
        and its ACTOR is somebody else, so no agent can ever wake itself.

        Two things are never Worker work, and that is what keeps the queue from
        starving:

        * a WAVE_ABORT. Cancellation is applied when the abort is folded -- its
          wave's command stops being pending, permanently -- so there is nothing
          left for the Worker to DO. An abort that stayed queued could never be
          answered by anybody, and would sit ahead of every later command forever.
        * a command that a newer accepted command has superseded. At most one
          command is ever pending: the newest, and only while it is neither
          answered nor aborted.
        """
        newest = self.newest_command()
        out: list[Envelope] = []
        for env in self.accepted():
            if not env.wakes(actor):
                continue
            state = self.waves.get(env.wave)
            if state is None:
                continue
            if env.kind == "WAVE_ABORT":
                continue
            # A CLAIMED command stays pending on purpose. Half-finished work is
            # still work; whether to re-enter it is a dispatch decision made once,
            # with durable evidence in hand -- see `Supervisor.poll_once`.
            if env.kind == "WAVE_COMMAND" and (
                    env is not newest or state.answered or state.aborted):
                continue
            if env.kind in ("WAVE_RESULT", "CAPTAIN_REQUIRED") and state.review is not None:
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
        superseded = set(self.superseded())
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
                    "superseded": w in superseded,
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
        if envelope.kind == "WAVE_REVIEW" and trust.is_publisher(comment.author):
            # The publisher's review is the FIRST write of a transaction whose
            # commit point is a checkpoint. Until that checkpoint exists nothing
            # has been answered, so it is recorded and not applied: a review
            # whose transaction died must leave the result pending, where a
            # rerun can find and finish it.
            state.records.append(
                Record(comment.source, comment.comment_id, comment.author, ACCEPTED,
                       None, "publisher review: a transaction prefix, not an answer",
                       envelope))
            continue
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
        if not trust.is_publisher(comment.author):
            return BusError(E.UNTRUSTED_AUTHOR,
                            f"{comment.author} is not a trusted bus speaker")
        problem = _publisher_role(envelope, comment, state, authority, trust, seen_ids)
        if problem is not None:
            return problem

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


def _publisher_role(envelope: Envelope, comment: RawComment, state: BusState,
                    authority: Authority, trust: Trust,
                    seen_ids: Mapping[str, int]) -> BusError | None:
    """The publisher identity may say exactly two things here, each exactly once.

    A review is the prefix of the transaction for the message it answers, so its
    id must be that transaction's review id. A command exists only as the ONE
    successor of the publisher checkpoint that is the live authority, and must be
    exactly the command that checkpoint's transition derives. Anything else the
    identity says -- another kind, actor, surface, id or body -- is refused like
    a stranger's comment.
    """
    def refused(why: str) -> BusError:
        return BusError(E.ROLE_REFUSED, f"{comment.author}: {why}")

    if not comment.source.startswith("pr:"):
        return refused("publisher bus messages belong on the transport pull request")
    # The role table is the law of WHAT the identity may say; the two branches
    # below only correlate each allowed shape to its one transaction.
    if (envelope.actor, envelope.kind) not in PUBLISHER_ROLES["transport"]:
        return refused(f"may not speak {envelope.actor} {envelope.kind}")
    if envelope.kind == "WAVE_REVIEW":
        parent_comment = seen_ids.get(envelope.parent or "")
        if parent_comment is None:
            return refused(f"the review answers unknown {envelope.parent}")
        txn = txn_id(envelope.authority["checkpoint"], parent_comment)
        if envelope.message_id != review_id(txn) or envelope.body.get("transaction") != txn \
                or "decision" not in envelope.body:
            return refused(f"a review of comment {parent_comment} must be {review_id(txn)}")
        return None
    if envelope.kind != "WAVE_COMMAND":
        return None
    pub = authority.publisher
    if pub is None or pub["verdict"] != "R" or envelope.message_id != pub["successor_command"]:
        return refused("a command must be the successor the live publisher checkpoint names")
    origin = next((r.envelope for r in state.records
                   if r.envelope is not None and trust.trusts(r.author)
                   and r.envelope.kind == "WAVE_COMMAND"
                   and r.envelope.message_id == pub["origin_command"]), None)
    if origin is None:
        return refused(f"origin command {pub['origin_command']} is not on the bus")
    try:
        expected = successor_command(
            origin=origin, issue=authority.issue, checkpoint=authority.checkpoint,
            task=authority.task, head=authority.accepted_head,
            result_head=pub["result_head"], repair_round=int(pub["repair_round"]),
            verdict_comment=int(pub["latest_manager_verdict"]), txn=pub["transaction"],
            created_at=envelope.created_at)
    except BusError as exc:
        return refused(exc.detail)
    if not same_message(expected, envelope):
        return refused("the command is not the successor the checkpoint derives")
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
