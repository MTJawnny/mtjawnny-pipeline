"""Deterministic Manager transitions: one admitted Worker message in, exact records out.

This is the law the publisher writes by and the law every reader checks the
publisher's records against -- one module, so the two cannot drift.

**One transaction per admitted Worker message.** Its id is derived from the
checkpoint the message cites and the comment that carries it, so every write and
every rerun of the same transaction names the same records:

    WAVE_REVIEW   PR     `mgr-review-<txn>`       prefix, not authority
    V             issue  `transaction: <txn>`     prefix, not authority
    K             issue  `transaction: <txn>`     THE COMMIT POINT
    WAVE_COMMAND  PR     `mgr-repair-<txn>`       REPAIR only, after the commit

**What a verdict may do.** Nothing here reads a head, a task or a successor
from the model; each is derived from the prior checkpoint and the Worker's
message:

    ACCEPT   h -> the result head (status P, every unit DONE, head independently
             tested), a -> 0. No successor.
    REPAIR   h unchanged, a unchanged, and exactly one successor: the SAME units,
             branch and review boundary as the Captain-rooted origin command, built
             on the result head as `<origin wave>.AR<n>`. After
             `MAX_REPAIR_ROUNDS` consecutive autonomous repairs, a REPAIR is
             recorded as CAPTAIN with `override: REPAIR_BUDGET_EXHAUSTED`.
    CAPTAIN  h unchanged, a -> 0. Autonomy stops; nothing is selected.

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
from agent_bus.decision import Decision, from_mapping
from agent_bus.errors import BusError
from agent_bus.ledger import (
    CHECKPOINT_KEYS, VERDICT, VERDICT_KEYS, LedgerError, Record, parse_record,
    render_checkpoint, render_verdict,
)
from agent_bus.protocol import WAVE_RE, Envelope

RECORDED_BY = "agent-bus-publisher"
MAX_REPAIR_ROUNDS = 3
LETTER = {"ACCEPT": "A", "REPAIR": "R", "CAPTAIN": "C"}
WORD = {v: k for k, v in LETTER.items()}
NEXT = {"A": "NO_ACTIVE_TASK", "R": "WORKER_EXECUTE_REPAIR", "C": "CAPTAIN_REQUIRED"}
NONE = "NONE"
BUDGET_EXHAUSTED = "REPAIR_BUDGET_EXHAUSTED"
MANAGER_ANSWERS = ("WAVE_RESULT", "CAPTAIN_REQUIRED")


def txn_id(checkpoint: int, result_comment: int) -> str:
    return f"mtx-{checkpoint}-{result_comment}"


def review_id(txn: str) -> str:
    return f"mgr-review-{txn}"


def command_id(txn: str) -> str:
    return f"mgr-repair-{txn}"


def digest(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def refuse(detail: str) -> BusError:
    return BusError(E.TRANSITION_REFUSED, detail)


@dataclass(frozen=True)
class Prior:
    """The checkpoint a transition starts from, and the repair lineage it carries."""

    issue: int
    checkpoint: int
    head: str
    active: int
    origin_command: str | None = None  # set only after a publisher REPAIR
    repair_round: int = 0
    successor_command: str | None = None


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

    @property
    def successor_id(self) -> str:
        return command_id(self.txn) if self.letter == "R" else NONE

    @property
    def result_head(self) -> str:
        env = self.subject.envelope
        return env.body["head"] if env.kind == "WAVE_RESULT" else NONE

    # ------------------------------------------------------------- the records
    def review(self, created_at: str) -> Envelope:
        env = self.subject.envelope
        body: dict = {"verdict": WORD[self.letter], "transaction": self.txn,
                      "decision": self.decision.as_dict()}
        if self.letter == "A":
            body["accepted_head"] = self.head
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
            "override": self.override, "decision": self.decision.as_dict(),
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
            "next": NEXT[self.letter],
        }

    def checkpoint_body(self, verdict_comment: int, unanswered=()) -> str:
        return render_checkpoint(self.checkpoint_fields(verdict_comment, unanswered))

    def successor(self, origin: Envelope, checkpoint: int, verdict_comment: int,
                  created_at: str) -> Envelope | None:
        if self.letter != "R":
            return None
        return successor_command(origin=origin, issue=self.prior.issue, checkpoint=checkpoint,
                                 task=self.active, head=self.head,
                                 result_head=self.result_head, repair_round=self.repair_round,
                                 verdict_comment=verdict_comment, txn=self.txn,
                                 created_at=created_at)


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
          origin: Envelope | None, measured_head: str | None = None,
          selftest_exit: int | None = None, law_only: bool = False) -> Transition:
    """The only way a decision becomes a transition. Refuses rather than repairs.

    `law_only` is for READERS re-deriving a durable record: they cannot re-run
    the independent test, so they skip exactly the two checks that need it and
    nothing else. The publisher never sets it.
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

    letter, override = LETTER[decision.verdict], NONE
    head, active, repair_round = prior.head, prior.active, spent

    if letter == "A":
        if env.kind != "WAVE_RESULT":
            raise refuse("only a WAVE_RESULT can be accepted")
        if env.body["status"] != "P" or any(u["status"] != "DONE" for u in env.body["units"]):
            raise refuse("ACCEPT needs status P with every unit DONE")
        if origin is None or {u["id"] for u in env.body["units"]} != \
                {u["id"] for u in origin.body["units"]}:
            raise refuse("ACCEPT needs the result to report exactly the commanded units")
        if not law_only:
            if measured_head != env.body["head"]:
                raise refuse(f"ACCEPT head {env.body['head']} is not the independently "
                             f"tested head {measured_head}")
            if selftest_exit != 0:
                raise refuse(f"ACCEPT needs a green independent selftest, got {selftest_exit}")
        head, active = env.body["head"], 0
    elif letter == "R":
        if env.kind != "WAVE_RESULT":
            raise refuse("a REPAIR must answer a WAVE_RESULT; it builds on the result head")
        if origin is None:
            raise refuse("a REPAIR needs the origin command it repeats")
        if spent + 1 > MAX_REPAIR_ROUNDS:
            letter, override, active = "C", BUDGET_EXHAUSTED, 0
        else:
            repair_round = spent + 1
            repair_wave(origin.wave, repair_round)  # refuse now, not after the commit
    else:
        active = 0

    return Transition(txn=txn_id(prior.checkpoint, subject.comment_id), prior=prior,
                      subject=subject, decision=decision, letter=letter, override=override,
                      head=head, active=active, origin=origin_id, repair_round=repair_round,
                      transport_pr=transport_pr)


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


def validate_publisher_checkpoint(
        comment: Found, prior: Prior, *, transport_pr: int,
        subject_of: Callable[[int], tuple[Subject, str] | None],
        origin_of: Callable[[str], Envelope | None],
        verdict_of: Callable[[int], Found | None]) -> Prior:
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
    origin = origin_of(origin_id) if origin_id != NONE else None
    transition = build(prior, subject, decision, transport_pr=transport_pr, origin=origin,
                       law_only=True)
    exactly(transition.verdict_body(), verdict.body, f"verdict {verdict_comment}")
    exactly(transition.checkpoint_body(verdict_comment, unanswered), comment.body,
            f"checkpoint {comment.comment_id}")
    return Prior(issue=prior.issue, checkpoint=comment.comment_id, head=transition.head,
                 active=transition.active,
                 origin_command=transition.origin if transition.letter == "R" else None,
                 repair_round=transition.repair_round,
                 successor_command=transition.successor_id if transition.letter == "R" else None)
