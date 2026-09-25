"""Deterministic Manager transitions: one admitted Worker message in, exact records out.

This is the law the publisher writes by and the law every reader checks the
publisher's records against -- one module, so the two cannot drift.

**One transaction per admitted Worker message.** Its id is derived from the
checkpoint the message cites and the comment that carries it, so every write and
every rerun of the same transaction names the same records:

    WAVE_REVIEW   PR     `mgr-review-<txn>`       prefix, not authority
    V             issue  `transaction: <txn>`     prefix, not authority
    K             issue  `transaction: <txn>`     THE COMMIT POINT
    WAVE_COMMAND  PR     `mgr-repair-<txn>`       REPAIR successor, after the commit
    WAVE_COMMAND  PR     `mgr-next-<txn>`         planned successor, after the commit

**What a verdict may do.** Nothing here reads a head, a task, a budget or a
successor from the model or the Worker. Each comes from the prior checkpoint, the
Worker's message, and the Captain goal plan the origin command is bound to
(`agent_bus.goal`):

    ACCEPT   h -> the result head. Needs status P, every unit DONE, the head
             independently tested green, AND independent evidence that every
             check the plan requires for this wave passed on that same head.
             a -> the task of the plan's `next` wave, whose exact command is the
             one successor; or a -> 0 when this wave is the plan's terminal.
    REPAIR   h unchanged, a unchanged, and exactly one successor: the SAME units,
             branch and review boundary as the origin command, built on the result
             head as `<origin wave>.AR<n>`. Past the plan's `repair_budget`, a
             REPAIR is recorded as CAPTAIN with `override: REPAIR_BUDGET_EXHAUSTED`.
    CAPTAIN  h unchanged, a -> 0. Autonomy stops; nothing is selected.

**No plan, no autonomy.** When the origin command is not bound to a live
Captain goal plan, there is no budget, no successor and no required checks to
read, so an ACCEPT or a REPAIR is recorded as CAPTAIN with `override:
GOAL_PLAN_UNBOUND`. Missing or malformed policy fails closed to the Captain.

A publisher record is trusted only if it is byte-for-byte what `Transition`
renders from the same inputs. That is the whole of the machine identity's role:
it can say what this module would have said, and nothing else.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from typing import Callable

from agent_bus import SCHEMA
from agent_bus import errors as E
from agent_bus import goal
from agent_bus.decision import Decision, from_mapping
from agent_bus.errors import BusError
from agent_bus.goal import Binding, Evidence
from agent_bus.ledger import (
    CHECKPOINT_KEYS, VERDICT, VERDICT_KEYS, LedgerError, Record, parse_record,
    render_checkpoint, render_verdict,
)
from agent_bus.protocol import WAVE_RE, Envelope

RECORDED_BY = "agent-bus-publisher"
LETTER = {"ACCEPT": "A", "REPAIR": "R", "CAPTAIN": "C"}
WORD = {v: k for k, v in LETTER.items()}
NEXT = {"R": "WORKER_EXECUTE_REPAIR", "C": "CAPTAIN_REQUIRED"}
NEXT_SUCCESSOR, NEXT_COMPLETE = "WORKER_EXECUTE_SUCCESSOR", "GOAL_COMPLETE"
NONE = "NONE"
BUDGET_EXHAUSTED = "REPAIR_BUDGET_EXHAUSTED"
PLAN_UNBOUND = "GOAL_PLAN_UNBOUND"
MANAGER_ANSWERS = ("WAVE_RESULT", "CAPTAIN_REQUIRED")
# A derived successor is compared with `same_message`, which ignores the send time.
UNSENT = "1970-01-01T00:00:00Z"


def txn_id(checkpoint: int, result_comment: int) -> str:
    return f"mtx-{checkpoint}-{result_comment}"


def review_id(txn: str) -> str:
    return f"mgr-review-{txn}"


def command_id(txn: str) -> str:
    return f"mgr-repair-{txn}"


def next_id(txn: str) -> str:
    return f"mgr-next-{txn}"


def digest(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def refuse(detail: str) -> BusError:
    return BusError(E.TRANSITION_REFUSED, detail)


@dataclass(frozen=True)
class Prior:
    """The checkpoint a transition starts from, and the lineage it carries."""

    issue: int
    checkpoint: int
    head: str
    active: int
    origin_command: str | None = None  # set only after a publisher REPAIR or planned ACCEPT
    repair_round: int = 0
    successor_command: str | None = None
    # The origin and successor commands themselves, as the chain derived them.
    # A planned successor is a publisher command, so it can be the origin of the
    # next lineage only as derived here -- never by looking its id up.
    origin: Envelope | None = None
    successor: Envelope | None = None


@dataclass(frozen=True)
class Subject:
    """The admitted Worker message: where it is, what it said, and its exact bytes."""

    comment_id: int
    digest: str
    envelope: Envelope


def lineage(prior: Prior, subject: Subject) -> tuple[str, int]:
    """(origin command, repair rounds already spent) for this message.

    A result answering the prior checkpoint's own successor continues that
    lineage. Anything else starts a new one at the command it answers.
    """
    parent = subject.envelope.parent
    if parent is None:
        return NONE, 0
    if prior.successor_command is not None and parent == prior.successor_command:
        return prior.origin_command or NONE, prior.repair_round
    return parent, 0


def resolve_origin(prior: Prior, origin_id: str,
                   lookup: Callable[[str], Envelope | None]) -> Envelope | None:
    """The origin as the chain derived it, else a trusted speaker's command by id."""
    if origin_id == NONE:
        return None
    if prior.origin is not None and prior.origin.message_id == origin_id:
        return prior.origin
    return lookup(origin_id)


@dataclass(frozen=True)
class Transition:
    txn: str
    prior: Prior
    subject: Subject
    decision: Decision
    letter: str  # A | R | C -- after any override
    override: str
    head: str
    active: int
    origin: str
    repair_round: int
    transport_pr: int
    origin_env: Envelope | None = None
    binding: Binding | None = None
    evidence: Evidence | None = None

    @property
    def successor_id(self) -> str:
        if self.letter == "R":
            return command_id(self.txn)
        if self.letter == "A" and self.binding is not None and self.binding.successor:
            return next_id(self.txn)
        return NONE

    @property
    def result_head(self) -> str:
        env = self.subject.envelope
        return env.body["head"] if env.kind == "WAVE_RESULT" else NONE

    @property
    def next(self) -> str:
        if self.letter == "A":
            return NEXT_SUCCESSOR if self.successor_id != NONE else NEXT_COMPLETE
        return NEXT[self.letter]

    # ------------------------------------------------------------- the records
    def review(self, created_at: str) -> Envelope:
        env = self.subject.envelope
        body: dict = {"verdict": WORD[self.letter], "transaction": self.txn,
                      "decision": self.decision.as_dict()}
        if self.letter == "A":
            body["accepted_head"] = self.head
        if self.evidence is not None:
            body["validation"] = self.evidence.as_dict()
        return Envelope(schema=SCHEMA, message_id=review_id(self.txn), actor="MANAGER",
                        kind="WAVE_REVIEW", wave=env.wave, parent=env.message_id,
                        authority=dict(env.authority), base=self.prior.head,
                        created_at=created_at, body=body)

    def verdict_fields(self) -> dict:
        env = self.subject.envelope
        return {
            "recorded_by": RECORDED_BY, "transaction": self.txn,
            "task_comment": self.prior.active, "selecting_checkpoint": self.prior.checkpoint,
            "transport_pr": self.transport_pr, "result_comment": self.subject.comment_id,
            "result_message": env.message_id, "result_digest": self.subject.digest,
            "wave": env.wave, "verdict": self.letter, "candidate_head": self.result_head,
            "accepted_head": self.prior.head, "next_accepted_head": self.head,
            "next_active_task": self.active, "review_message": review_id(self.txn),
            "override": self.override,
            "goal_plan": self.binding.comment_id if self.binding else NONE,
            "validation": self.evidence.as_dict() if self.evidence else NONE,
            "decision": self.decision.as_dict(),
        }

    def verdict_body(self) -> str:
        return render_verdict(self.verdict_fields())

    def checkpoint_fields(self, verdict_comment: int, unanswered=()) -> dict:
        env = self.subject.envelope
        return {
            "h": self.head, "a": self.active, "accepted_head": self.head,
            "active_task": self.active, "recorded_by": RECORDED_BY, "transaction": self.txn,
            "prior_checkpoint": self.prior.checkpoint,
            "latest_manager_verdict": verdict_comment, "verdict": self.letter,
            "transport_pr": self.transport_pr, "result_comment": self.subject.comment_id,
            "result_message": env.message_id, "result_head": self.result_head,
            "origin_command": self.origin, "repair_round": self.repair_round,
            "successor_command": self.successor_id, "unanswered": sorted(unanswered),
            "next": self.next,
        }

    def checkpoint_body(self, verdict_comment: int, unanswered=()) -> str:
        return render_checkpoint(self.checkpoint_fields(verdict_comment, unanswered))

    def successor(self, checkpoint: int, verdict_comment: int,
                  created_at: str = UNSENT) -> Envelope | None:
        """The one command the checkpoint `checkpoint` owes, or None."""
        if self.successor_id == NONE:
            return None
        if self.letter == "R":
            return successor_command(origin=self.origin_env, issue=self.prior.issue,
                                     checkpoint=checkpoint, task=self.active, head=self.head,
                                     result_head=self.result_head,
                                     repair_round=self.repair_round,
                                     verdict_comment=verdict_comment, txn=self.txn,
                                     created_at=created_at)
        return goal.next_command(self.binding, message_id=self.successor_id,
                                 issue=self.prior.issue, checkpoint=checkpoint,
                                 head=self.head, created_at=created_at)

    def after(self, checkpoint: int, verdict_comment: int) -> Prior:
        """The Prior the committed checkpoint `checkpoint` establishes."""
        successor = self.successor(checkpoint, verdict_comment)
        if self.letter == "R":
            return Prior(self.prior.issue, checkpoint, self.head, self.active,
                         origin_command=self.origin, repair_round=self.repair_round,
                         successor_command=self.successor_id, origin=self.origin_env,
                         successor=successor)
        if successor is not None:  # a planned ACCEPT: the successor starts a lineage
            return Prior(self.prior.issue, checkpoint, self.head, self.active,
                         origin_command=successor.message_id, repair_round=0,
                         successor_command=successor.message_id, origin=successor,
                         successor=successor)
        return Prior(self.prior.issue, checkpoint, self.head, self.active)


def repair_wave(origin_wave: str, repair_round: int) -> str:
    wave = f"{origin_wave}.AR{repair_round}"
    if not WAVE_RE.match(wave):
        raise refuse(f"repair wave {wave!r} is not a valid wave id")
    return wave


def successor_command(*, origin: Envelope, issue: int, checkpoint: int, task: int, head: str,
                      result_head: str, repair_round: int, verdict_comment: int, txn: str,
                      created_at: str) -> Envelope:
    """The ONE successor a REPAIR may select: the origin's units, again, on the result."""
    body = {
        "branch": origin.body["branch"],
        "review_boundary": origin.body["review_boundary"],
        "units": copy.deepcopy(origin.body["units"]),
        "candidate_base": result_head,
        "note": (f"autonomous repair round {repair_round} of {origin.message_id}; "
                 f"the findings are in Issue #{issue} verdict {verdict_comment}"),
    }
    if "stop_conditions" in origin.body:
        body["stop_conditions"] = list(origin.body["stop_conditions"])
    if "goal" in origin.body:
        body["goal"] = dict(origin.body["goal"])
    return Envelope(schema=SCHEMA, message_id=command_id(txn), actor="MANAGER",
                    kind="WAVE_COMMAND", wave=repair_wave(origin.wave, repair_round),
                    parent=None, authority={"issue": issue, "checkpoint": checkpoint,
                                            "task": task},
                    base=head, created_at=created_at, body=body)


def same_message(a: Envelope, b: Envelope) -> bool:
    """Equal in every field but the send time."""
    def canon(env: Envelope) -> str:
        return json.dumps({**json.loads(env.to_json()), "created_at": ""}, sort_keys=True)
    return canon(a) == canon(b)


def build(prior: Prior, subject: Subject, decision: Decision, *, transport_pr: int,
          origin: Envelope | None, binding: Binding | None = None,
          evidence: Evidence | None = None, measured_head: str | None = None,
          selftest_exit: int | None = None, law_only: bool = False) -> Transition:
    """The only way a decision becomes a transition. Refuses rather than repairs.

    `binding` is `goal.bind(origin, ...)`: the plan the origin command is exactly
    one wave of, or None. `evidence` is the independent runner's measurement.

    `law_only` is for READERS re-deriving a durable record: they cannot re-run
    the independent test, so they skip exactly the two checks that need it and
    nothing else -- the recorded check evidence is still judged. The publisher
    never sets it.
    """
    env = subject.envelope
    if env.actor != "WORKER" or env.kind not in MANAGER_ANSWERS:
        raise refuse(f"{env.kind} from {env.actor} is not a Worker message for the Manager")
    if prior.active == 0:
        raise refuse(f"checkpoint {prior.checkpoint} selects no task; nothing can be reviewed")
    cited = {"issue": prior.issue, "checkpoint": prior.checkpoint, "task": prior.active}
    if env.authority != cited:
        raise refuse(f"the message cites {env.authority}, the prior checkpoint is {cited}")
    if env.base != prior.head:
        raise refuse(f"the message base {env.base} is not accepted head {prior.head}")

    origin_id, spent = lineage(prior, subject)
    if origin_id != NONE:
        if origin is None or origin.message_id != origin_id or origin.kind != "WAVE_COMMAND" \
                or origin.actor != "MANAGER" or origin.authority["task"] != prior.active:
            raise refuse(f"origin command {origin_id} is not a Manager command of task "
                         f"{prior.active}")
    if binding is not None and (origin is None or binding.entry.wave != origin.wave):
        raise refuse("the goal binding is not the origin command's")
    if binding is None or env.kind != "WAVE_RESULT":
        evidence = None  # nothing it could be judged against; recorded as NONE
    if evidence is not None:
        goal.check_evidence(binding, evidence, env.body["head"])

    letter, override = LETTER[decision.verdict], NONE
    head, active, repair_round = prior.head, prior.active, spent

    if letter in ("A", "R"):
        if env.kind != "WAVE_RESULT":
            raise refuse("only a WAVE_RESULT can be accepted or repaired; it carries the head")
        if origin is None:
            raise refuse("an ACCEPT or REPAIR needs the origin command it answers")
        if binding is None:
            letter, override = "C", PLAN_UNBOUND

    if letter == "A":
        if env.body["status"] != "P" or any(u["status"] != "DONE" for u in env.body["units"]):
            raise refuse("ACCEPT needs status P with every unit DONE")
        if {u["id"] for u in env.body["units"]} != {u["id"] for u in origin.body["units"]}:
            raise refuse("ACCEPT needs the result to report exactly the commanded units")
        if not law_only:
            if measured_head != env.body["head"]:
                raise refuse(f"ACCEPT head {env.body['head']} is not the independently "
                             f"tested head {measured_head}")
            if selftest_exit != 0:
                raise refuse(f"ACCEPT needs a green independent selftest, got {selftest_exit}")
        if evidence is None:
            raise refuse("ACCEPT needs independent evidence of the plan's required checks "
                         "on the result head")
        if evidence.red:
            raise refuse(f"ACCEPT needs every required check green; red: {evidence.red}")
        nxt = binding.successor
        head, active = env.body["head"], nxt.task if nxt is not None else 0
    elif letter == "R":
        if spent + 1 > binding.plan.repair_budget:
            letter, override, active = "C", BUDGET_EXHAUSTED, 0
        else:
            repair_round = spent + 1
            repair_wave(origin.wave, repair_round)  # refuse now, not after the commit
    if letter == "C":
        active = 0

    return Transition(txn=txn_id(prior.checkpoint, subject.comment_id), prior=prior,
                      subject=subject, decision=decision, letter=letter, override=override,
                      head=head, active=active, origin=origin_id, repair_round=repair_round,
                      transport_pr=transport_pr, origin_env=origin, binding=binding,
                      evidence=evidence)


# ------------------------------------------------------------------- reading back

@dataclass(frozen=True)
class Found:
    """A comment located by a reader, with who wrote it."""

    comment_id: int
    author: str
    body: str


def exactly(expected: str, actual: str, what: str) -> None:
    """The role law in one line: the publisher may write this record and no other."""
    if actual != expected:
        raise refuse(f"{what} is not what the publisher would have written")


def decision_of_verdict(record: Record) -> Decision:
    raw = record.fields.get("decision")
    try:
        return from_mapping(json.loads(raw or ""))
    except (json.JSONDecodeError, BusError) as exc:
        raise refuse(f"verdict decision field is not a decision: {exc}")


def evidence_of_verdict(record: Record) -> Evidence | None:
    raw = record.fields.get("validation")
    if raw == NONE:
        return None
    try:
        return goal.evidence_from_mapping(json.loads(raw or ""))
    except (json.JSONDecodeError, BusError) as exc:
        raise refuse(f"verdict validation field is not evidence: {exc}")


def validate_publisher_checkpoint(
        comment: Found, prior: Prior, *, transport_pr: int,
        subject_of: Callable[[int], tuple[Subject, str] | None],
        origin_of: Callable[[str], Envelope | None],
        verdict_of: Callable[[int], Found | None],
        plan_of: Callable[[Envelope | None], Binding | None] = lambda origin: None) -> Prior:
    """A publisher K is valid only as the exact next link after `prior`.

    Returns the Prior it establishes. Raises TRANSITION_REFUSED naming the first
    thing that is not what the publisher would have written.
    """
    try:
        record = parse_record(comment.body)
    except LedgerError as exc:
        raise refuse(f"malformed record: {exc}")
    if record is None or record.schema != "mtj-checkpoint" or tuple(record.fields) != CHECKPOINT_KEYS:
        raise refuse("not a publisher checkpoint form")
    f = record.fields
    if f["recorded_by"] != RECORDED_BY:
        raise refuse("not recorded by the publisher")
    if f["prior_checkpoint"] != str(prior.checkpoint):
        raise refuse(f"chains from {f['prior_checkpoint']}, but the checkpoint before it is "
                     f"{prior.checkpoint}")
    if f["transport_pr"] != str(transport_pr):
        raise refuse(f"names transport PR {f['transport_pr']}, not {transport_pr}")
    try:
        result_comment, verdict_comment = int(f["result_comment"]), int(f["latest_manager_verdict"])
        unanswered = json.loads(f["unanswered"])
    except (TypeError, ValueError):
        raise refuse("result, verdict or unanswered is not well-formed")
    if not isinstance(unanswered, list) or any(
            not isinstance(u, int) or isinstance(u, bool) for u in unanswered):
        raise refuse("unanswered must be a list of comment ids")

    located = subject_of(result_comment)
    if located is None:
        raise refuse(f"result comment {result_comment} is not a trusted Worker message on "
                     f"PR {transport_pr}")
    verdict = verdict_of(verdict_comment)
    if verdict is None or verdict.comment_id >= comment.comment_id:
        raise refuse(f"verdict {verdict_comment} is not a publisher V before this checkpoint")
    try:
        v_record = parse_record(verdict.body)
    except LedgerError as exc:
        raise refuse(f"verdict {verdict_comment} is malformed: {exc}")
    if v_record is None or v_record.schema != VERDICT or tuple(v_record.fields) != VERDICT_KEYS:
        raise refuse(f"verdict {verdict_comment} is not a publisher verdict form")
    subject, _ = located
    # The digest is the one recorded at transaction time: the resolver judges
    # the transition, and an edit made after the commit is not a new transition.
    subject = Subject(subject.comment_id, v_record.fields["result_digest"] or "", subject.envelope)
    decision = decision_of_verdict(v_record)
    origin_id, _ = lineage(prior, subject)
    origin = resolve_origin(prior, origin_id, origin_of)
    transition = build(prior, subject, decision, transport_pr=transport_pr, origin=origin,
                       binding=plan_of(origin), evidence=evidence_of_verdict(v_record),
                       law_only=True)
    exactly(transition.verdict_body(), verdict.body, f"verdict {verdict_comment}")
    exactly(transition.checkpoint_body(verdict_comment, unanswered), comment.body,
            f"checkpoint {comment.comment_id}")
    return transition.after(comment.comment_id, verdict_comment)
