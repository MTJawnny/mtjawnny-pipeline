"""The Manager wake pre-gate: decide, deterministically, whether a GitHub comment
may wake the Manager -- before any model, and before any model credential, exists
in the run.

`python3 -m agent_bus.manager_gate` reads one `issue_comment` event and answers
`wake=true` for exactly one shape: a NEW comment on the transport pull request,
by the trusted author, carrying exactly one `mtj-bus` envelope that the ordinary
parser accepts, spoken by the WORKER, of a kind addressed to the Manager, citing
the latest `K` and its accepted head, and folding into live bus state as the
HEAD of the Manager queue -- not answered, not aborted, not superseded, and not
waiting behind an older message. Everything else answers `wake=false` with one
stable code.

"Answered" is decided by the transaction law (`agent_bus.publisher`), never by
whoever posted something review-shaped: only a trusted speaker's review, or the
publisher's committed checkpoint for this message's transaction, answers it.
Anything else that claims to is reported in `ignored` and changes nothing.

`mode` says what the admitted run is for. `review` needs the model. `resume`
does not: the decision is already durable (a publisher review exists) or the
transaction already committed and only its successor is owed, so the model is
not asked again and cannot contradict what is already written.

There is no second parser here. Envelope law is `agent_bus.protocol`; authority
is `agent_bus.issue.resolve_authority`; correlation, duplicates and staleness are
`agent_bus.machine.fold`, reached through the same `Supervisor.observe` the Worker
uses. This module only adds the event-shaped checks that come before them, and
insists on each of them in order.

Exit codes, read by the workflow step and by a human alike:

    0  a decision was made -- `wake` is true or false
    3  the durable authority could not be resolved (`wake=false` is still written)

Anything else is a crash, and a crash writes nothing -- so the step fails and the
model step, which requires `wake == 'true'`, cannot run. The comment body is
never copied into the step outputs: only validated tokens are, because an output
file is line-oriented and a body is attacker-shaped text.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Mapping, Sequence

from agent_bus import errors as E
from agent_bus.errors import BusError
from agent_bus.issue import AuthorityError
from agent_bus.ledger import parse_record
from agent_bus.machine import ACCEPTED
from agent_bus.protocol import WAKES, Envelope, parse_comment
from agent_bus.publisher import Target, World, find_records
from agent_bus.shell import Runner
from agent_bus.supervisor import Observation, Supervisor
from agent_bus.transition import digest, txn_id
from agent_bus.trust import Trust

EVENT_NAME = "issue_comment"
EVENT_ACTION = "created"
MANAGER = "MANAGER"
WORKER = "WORKER"


@dataclass
class Context:
    """One event under examination. Stages read it and fill it in, in order."""

    event: Mapping
    event_name: str
    repo: str
    transport_pr: int
    trusted_author: str
    issue: int
    run: Runner
    envelope: Envelope | None = None
    observation: Observation | None = None
    notes: dict = field(default_factory=dict)
    mode: str = "review"
    committed: bool = False
    ignored: list = field(default_factory=list)

    @property
    def comment(self) -> Mapping:
        return self.event["comment"]

    @property
    def trust(self) -> Trust:
        return Trust(frozenset({self.trusted_author.lower()}), "manager-gate")


@dataclass(frozen=True)
class Decision:
    wake: bool
    code: str | None
    detail: str
    comment_id: int | None = None
    message_id: str | None = None
    kind: str | None = None
    wave: str | None = None
    authority: dict | None = None
    stage: str | None = None  # the stage that refused; None when admitted
    mode: str | None = None  # review | resume, when admitted
    digest: str | None = None  # sha256 of the admitted body, when admitted
    ignored: tuple = ()  # records that claimed to answer, from nobody allowed to

    def as_dict(self) -> dict:
        return {"wake": self.wake, "code": self.code, "detail": self.detail,
                "stage": self.stage, "comment_id": self.comment_id,
                "message_id": self.message_id, "kind": self.kind, "wave": self.wave,
                "authority": self.authority, "mode": self.mode, "digest": self.digest,
                "ignored": list(self.ignored)}

    def output_lines(self) -> list[str]:
        """What goes to `$GITHUB_OUTPUT`. Validated tokens only, never free text."""
        lines = [f"wake={'true' if self.wake else 'false'}"]
        if self.code is not None:
            lines.append(f"code={self.code}")
        if self.wake:
            lines.append(f"mode={self.mode}")
            lines.append(f"comment_id={self.comment_id}")
            lines.append(f"message_id={self.message_id}")
            lines.append(f"digest={self.digest}")
        return lines


def _shape(value, kind, what: str):
    if not isinstance(value, kind) or isinstance(value, bool):
        raise BusError(E.GATE_WRONG_EVENT, f"event {what} is not a {kind.__name__}")
    return value


def _envelope(ctx: Context) -> Envelope:
    """What an earlier stage established -- or a refusal, never a crash."""
    if ctx.envelope is None:
        raise BusError(E.GATE_NO_ENVELOPE, "no envelope was established")
    return ctx.envelope


def _observe(ctx: Context) -> Observation:
    """Read Issue #1 and the transport PR once, through the Worker's own observer."""
    if ctx.observation is None:
        supervisor = Supervisor(repo_path=".", repo_slug=ctx.repo, trust=ctx.trust,
                                actor=MANAGER, issue=ctx.issue,
                                transport_pr=ctx.transport_pr, run=ctx.run)
        ctx.observation = supervisor.observe()
    return ctx.observation


# ---------------------------------------------------------------------- stages
# Each stage raises one BusError or returns. The order is the order a cheap,
# offline refusal should happen in; network reads come last.


def check_event(ctx: Context) -> None:
    """Only a newly created issue_comment. Edits and deletions never wake anyone."""
    if ctx.event_name != EVENT_NAME:
        raise BusError(E.GATE_WRONG_EVENT, f"event {ctx.event_name!r} is not {EVENT_NAME!r}")
    if ctx.event.get("action") != EVENT_ACTION:
        raise BusError(E.GATE_WRONG_EVENT,
                       f"action {ctx.event.get('action')!r} is not {EVENT_ACTION!r}")
    comment = _shape(ctx.event.get("comment"), dict, "comment")
    _shape(comment.get("id"), int, "comment.id")
    _shape(comment.get("body"), str, "comment.body")
    _shape(_shape(comment.get("user"), dict, "comment.user").get("login"), str,
           "comment.user.login")


def check_surface(ctx: Context) -> None:
    """This repository, a pull request, and that pull request the transport one."""
    repository = _shape(ctx.event.get("repository"), dict, "repository")
    if repository.get("full_name") != ctx.repo:
        raise BusError(E.GATE_WRONG_SURFACE,
                       f"repository {repository.get('full_name')!r} is not {ctx.repo!r}")
    issue = _shape(ctx.event.get("issue"), dict, "issue")
    if not issue.get("pull_request"):
        raise BusError(E.GATE_WRONG_SURFACE,
                       f"#{issue.get('number')} is an issue, not the transport pull request")
    if issue.get("number") != ctx.transport_pr:
        raise BusError(E.GATE_WRONG_SURFACE,
                       f"PR #{issue.get('number')} is not transport PR #{ctx.transport_pr}")


def check_author(ctx: Context) -> None:
    """Exactly the trusted login -- compared as written, not case-folded."""
    login = ctx.comment["user"]["login"]
    if login != ctx.trusted_author:
        raise BusError(E.UNTRUSTED_AUTHOR,
                       f"{login!r} is not the trusted author {ctx.trusted_author!r}")


def check_envelope(ctx: Context) -> None:
    """Exactly one `mtj-bus` block, accepted by the ordinary parser."""
    envelope = parse_comment(ctx.comment["body"])  # raises on 2+ blocks or bad JSON
    if envelope is None:
        raise BusError(E.GATE_NO_ENVELOPE, "the comment carries no mtj-bus block")
    ctx.envelope = envelope


def check_addressee(ctx: Context) -> None:
    """A WORKER message of a kind addressed to the Manager, and nothing else."""
    env = _envelope(ctx)
    if env.actor != WORKER:
        raise BusError(E.GATE_NOT_FOR_MANAGER, f"actor {env.actor} is not {WORKER}")
    if env.kind not in WAKES[MANAGER] or not env.wakes(MANAGER):
        raise BusError(E.GATE_NOT_FOR_MANAGER,
                       f"{env.kind} does not wake the Manager; "
                       f"only {sorted(WAKES[MANAGER])} do")


def _world(ctx: Context) -> World:
    obs = _observe(ctx)
    return World([c for c in obs.comments if c.source == f"issue:{ctx.issue}"],
                 [c for c in obs.comments if c.source == f"pr:{ctx.transport_pr}"],
                 obs.resolution, obs.state)


def check_transaction(ctx: Context) -> None:
    """Has this message's transaction already committed? Decided by role law only.

    Runs BEFORE the authority stage on purpose: once the transaction commits, the
    message cites a checkpoint that is no longer the latest, so the authority
    stage alone would call a finished transaction "stale" -- and would also call
    a committed transaction whose successor is still owed "stale", leaving it
    owed forever. Here the first is ALREADY_HANDLED and the second is a resume.
    """
    env = _envelope(ctx)
    world = _world(ctx)
    tid = txn_id(env.authority["checkpoint"], ctx.comment["id"])
    target = Target(ctx.repo, ctx.issue, ctx.transport_pr, ctx.trust)
    records = find_records(world, target, tid, env.message_id)
    ctx.ignored = records.ignored
    committed = [c for c in records.checkpoints if c.comment_id in world.resolution.chain]
    if committed:
        fields = parse_record(committed[0].body).fields
        live = (world.authority.publisher or {}).get("transaction") == tid
        if fields["verdict"] == "R" and not records.commands and live:
            ctx.mode, ctx.committed = "resume", True
            return
        raise BusError(E.GATE_ALREADY_HANDLED,
                       f"{env.message_id} was answered by checkpoint {committed[0].comment_id}")
    if records.checkpoints:
        raise BusError(E.TXN_RACE_LOST,
                       f"checkpoint(s) {[c.comment_id for c in records.checkpoints]} carry "
                       f"{tid} but are not links of the chain")
    if records.reviews:
        ctx.mode = "resume"


def check_authority(ctx: Context) -> None:
    """Read Issue #1 independently. The message must cite the latest K and its head."""
    if ctx.committed:
        return  # the transaction moved the authority itself; decided above
    env = _envelope(ctx)
    authority = _observe(ctx).authority
    cited = env.authority
    if cited["issue"] != authority.issue or cited["checkpoint"] != authority.checkpoint:
        raise BusError(E.STALE_AUTHORITY,
                       f"cites issue {cited['issue']} checkpoint {cited['checkpoint']}; "
                       f"latest K is {authority.checkpoint} on issue {authority.issue}")
    if cited["task"] != authority.task:
        raise BusError(E.WAVE_NOT_SELECTED,
                       f"cites task {cited['task']}, active T is {authority.task}")
    if env.base != authority.accepted_head:
        raise BusError(E.STALE_BASE,
                       f"base {env.base} is not accepted head {authority.accepted_head}")


def check_live_comment(ctx: Context) -> None:
    """The event must describe a comment that really is on the transport PR, as sent.

    The event payload is what GitHub delivered; the live read is what GitHub holds.
    If they disagree -- the comment is elsewhere, gone, or edited since -- nothing
    is decided on either.
    """
    source = f"pr:{ctx.transport_pr}"
    live = [c for c in _observe(ctx).comments
            if c.source == source and c.comment_id == ctx.comment["id"]]
    if len(live) != 1:
        raise BusError(E.GATE_COMMENT_MISMATCH,
                       f"comment {ctx.comment['id']} is not on PR #{ctx.transport_pr}")
    if live[0].author != ctx.comment["user"]["login"] or live[0].body != ctx.comment["body"]:
        raise BusError(E.GATE_COMMENT_MISMATCH,
                       f"comment {ctx.comment['id']} changed between delivery and reading")


def check_state(ctx: Context) -> None:
    """Fold everything. This comment must be ACCEPTED and the head of the Manager queue.

    This is where a duplicate message id, an unknown parent, a result for a wave
    nobody commanded, a result already reviewed, a result for cancelled work and
    a result queued behind an older one are refused -- by the same state machine
    the Worker obeys, not by a copy of it.
    """
    if ctx.committed:
        return
    env = _envelope(ctx)
    state = _observe(ctx).state
    records = [r for r in state.records
               if r.comment_id == ctx.comment["id"] and r.source == f"pr:{ctx.transport_pr}"]
    if len(records) != 1:
        raise BusError(E.GATE_COMMENT_MISMATCH,
                       f"comment {ctx.comment['id']} folded {len(records)} times")
    record = records[0]
    if record.status != ACCEPTED:
        raise BusError(record.code or E.GATE_NO_ENVELOPE,
                       f"bus state refused this comment: {record.detail}")
    pending = [e.message_id for e in state.pending_for(MANAGER)]
    if env.message_id not in pending:
        raise BusError(E.GATE_ALREADY_HANDLED,
                       f"{env.message_id} is not pending for the Manager")
    if state.waves[env.wave].aborted is not None:
        raise BusError(E.WAVE_ABORTED,
                       f"wave {env.wave} was aborted; cancelled work is never reviewed")
    if env.wave in state.superseded():
        raise BusError(E.WAVE_SUPERSEDED, f"wave {env.wave} was superseded by a newer command")
    queue = [e.message_id for e in state.manager_queue()]
    if queue[0] != env.message_id:
        raise BusError(E.GATE_QUEUED, f"{env.message_id} waits behind {queue[0]}; that "
                       "transaction answers first and names this one as unanswered")


Stage = Callable[[Context], None]
STAGES: tuple[tuple[str, Stage], ...] = (
    ("event", check_event),
    ("surface", check_surface),
    ("author", check_author),
    ("envelope", check_envelope),
    ("addressee", check_addressee),
    ("transaction", check_transaction),
    ("authority", check_authority),
    ("live_comment", check_live_comment),
    ("state", check_state),
)


def decide(event: Mapping, event_name: str, repo: str, transport_pr: int,
           trusted_author: str, run: Runner, issue: int = 1,
           stages: Sequence[tuple[str, Stage]] = STAGES) -> Decision:
    """Run every stage in order. The first refusal is the answer.

    `stages` is injectable ONLY so tests can remove one stage and prove the gate
    then admits what it refused; the entry point always passes the full tuple.
    """
    if not trusted_author:
        raise BusError(E.TRUST_NOT_CONFIGURED, "the gate needs a trusted author")
    ctx = Context(event=event, event_name=event_name, repo=repo,
                  transport_pr=transport_pr, trusted_author=trusted_author,
                  issue=issue, run=run)
    comment = event.get("comment") if isinstance(event.get("comment"), dict) else {}
    cid = comment.get("id")
    comment_id = cid if isinstance(cid, int) and not isinstance(cid, bool) else None
    name = None
    try:
        for name, stage in stages:
            stage(ctx)
    except BusError as exc:
        return Decision(False, exc.code, exc.detail, comment_id,
                        ctx.envelope.message_id if ctx.envelope else None,
                        ctx.envelope.kind if ctx.envelope else None,
                        ctx.envelope.wave if ctx.envelope else None,
                        ctx.observation.authority.as_dict() if ctx.observation else None,
                        stage=name, ignored=tuple(ctx.ignored))
    env = ctx.envelope
    if env is None or ctx.observation is None:
        # Only reachable with stages removed. Fail closed, never admit a blank.
        return Decision(False, E.GATE_NO_ENVELOPE, "no envelope was established",
                        comment_id, stage="decide")
    return Decision(True, None, "admitted", comment_id, env.message_id, env.kind, env.wave,
                    ctx.observation.authority.as_dict(), mode=ctx.mode,
                    digest=digest(ctx.comment["body"]), ignored=tuple(ctx.ignored))


def write_outputs(decision: Decision, path: str | None) -> None:
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        handle.write("\n".join(decision.output_lines()) + "\n")


def main(argv: list[str] | None = None, run: Runner | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent_bus.manager_gate",
                                     description="Manager wake pre-gate (no model)")
    parser.add_argument("--event", required=True, help="path to the GitHub event JSON")
    parser.add_argument("--event-name", required=True, help="GITHUB_EVENT_NAME")
    parser.add_argument("--repo", required=True, help="owner/name")
    parser.add_argument("--pr", type=int, required=True, help="the transport pull request")
    parser.add_argument("--trusted-author", required=True, help="exact GitHub login")
    parser.add_argument("--issue", type=int, default=1, help="the authority issue")
    parser.add_argument("--github-output", default=None, help="GITHUB_OUTPUT path")
    args = parser.parse_args(argv)

    event = json.loads(Path(args.event).read_text(encoding="utf-8"))
    if not isinstance(event, dict):
        raise BusError(E.GATE_WRONG_EVENT, "the event payload is not an object")
    try:
        decision = decide(event, args.event_name, args.repo, args.pr,
                          args.trusted_author, run or Runner(), args.issue)
        code = 0
    except AuthorityError as exc:
        decision = Decision(False, E.AUTHORITY_UNRESOLVED, str(exc))
        code = 3
    write_outputs(decision, args.github_output)
    print(json.dumps(decision.as_dict(), indent=2, sort_keys=True))
    return code


if __name__ == "__main__":  # pragma: no cover - module entry point
    raise SystemExit(main())
