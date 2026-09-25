"""The deterministic Manager publisher: one typed decision in, one checkpoint transition out.

The model decides; this module writes. Given an admitted Worker message and a
`agent_bus.decision.Decision`, it derives every record with
`agent_bus.transition`, and writes them in a fixed order:

    1  WAVE_REVIEW   transport PR   prefix
    2  V             Issue #1       prefix
    3  K             Issue #1       COMMIT POINT -- authority moves here, once
    4  WAVE_COMMAND  transport PR   the owed successor, only after the commit:
                                    a REPAIR's re-issue, or an ACCEPT's planned next wave

**Live revalidation.** Immediately before EVERY write the whole world is read
again and every check in `PRE_COMMIT` (or `POST_COMMIT`) runs against it: the
authority has not moved, the message is still there and byte-identical, it is
still the head of the Manager queue, its wave was not aborted or superseded, and
the branch tip is still the head the Worker reported. A write happens only on
the answer to that read, never on an earlier one.

**Idempotent recovery.** Every run starts from nothing but durable state. The
transaction id is derived, so a rerun finds its own earlier records; each record
already present must be EXACTLY what this run would write (else
`BUS_TXN_CONFLICT`, and nothing more is written); each missing one is written.
Before the commit, a durable review fixes the decision and the check evidence,
so a rerun never needs the model or the checks again and can never contradict
them. After the commit, only the successor can be missing, and it is posted only
while the committed K is still the live authority -- exactly as the chain
derives it.

**Untrusted records are data.** A review, verdict or checkpoint that claims this
transaction or answers this message, from anyone the role law does not allow,
never counts as handled and never blocks a write. It is listed in the report.

Exit codes: 0 the transaction is complete; 4 refused before the commit (no
authority moved); 5 stopped after the commit (authority moved, the successor
could not be posted, or the commit lost the chain); 2 bad input.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from typing import Callable, Sequence

import dataclasses

from agent_bus import compose
from agent_bus import decision as decision_module
from agent_bus import errors as E
from agent_bus import goal, ledger
from agent_bus.decision import Decision
from agent_bus.errors import BusError
from agent_bus.goal import Binding, Evidence
from agent_bus.issue import AuthorityError, Resolution, post_comment, read_comments, resolve_authority
from agent_bus.machine import ACCEPTED, BusState, RawComment, fold
from agent_bus.protocol import Envelope, parse_comment
from agent_bus.shell import Runner
from agent_bus.transition import (
    NONE, Prior, Subject, Transition, build, command_id, digest, lineage, next_id,
    resolve_origin, review_id, same_message, txn_id,
)
from agent_bus.trust import Trust

EXIT_COMPLETE, EXIT_BAD_INPUT, EXIT_REFUSED, EXIT_AFTER_COMMIT = 0, 2, 4, 5


@dataclass(frozen=True)
class Target:
    """Where the bus lives, and who may speak on it."""

    repo: str
    issue: int
    transport_pr: int
    trust: Trust


@dataclass
class World:
    """One live read of both surfaces, folded. Never reused across a write."""

    issue_comments: list[RawComment]
    pr_comments: list[RawComment]
    resolution: Resolution
    state: BusState
    branch_tips: dict[str, str] = field(default_factory=dict)

    @property
    def authority(self):
        return self.resolution.authority


def observe(target: Target, run: Runner) -> World:
    issue = read_comments(target.issue, target.repo, run)
    pr = read_comments(target.transport_pr, target.repo, run, source=f"pr:{target.transport_pr}")
    resolution = resolve_authority(issue, target.issue, target.trust, transport=pr,
                                   transport_pr=target.transport_pr)
    state = fold(sorted(issue + pr, key=lambda c: c.comment_id), resolution.authority,
                 target.trust)
    return World(issue, pr, resolution, state)


def branch_tip(target: Target, branch: str, run: Runner) -> str:
    """The branch's live tip, read from GitHub. Never a local ref."""
    result = run(["gh", "api", f"repos/{target.repo}/git/ref/heads/{branch}",
                  "--jq", ".object.sha"])
    tip = result.stdout.strip()
    if result.returncode != 0 or not ledger.SHA_RE.match(tip):
        raise BusError(E.BRANCH_TIP_MISMATCH, f"cannot read the tip of {branch}: "
                       f"{result.stderr.strip() or tip!r}")
    return tip


# ---------------------------------------------------------------- the records

@dataclass
class Records:
    """Everything durable that belongs to, or claims, one transaction."""

    reviews: list[tuple[RawComment, Envelope]] = field(default_factory=list)
    verdicts: list[RawComment] = field(default_factory=list)
    checkpoints: list[RawComment] = field(default_factory=list)
    commands: list[tuple[RawComment, Envelope]] = field(default_factory=list)
    human_answers: list[RawComment] = field(default_factory=list)
    ignored: list[dict] = field(default_factory=list)

    def report(self) -> dict:
        return {"reviews": [c.comment_id for c, _ in self.reviews],
                "verdicts": [c.comment_id for c in self.verdicts],
                "checkpoints": [c.comment_id for c in self.checkpoints],
                "commands": [c.comment_id for c, _ in self.commands],
                "human_answers": [c.comment_id for c in self.human_answers],
                "ignored": self.ignored}


def _envelope(comment: RawComment) -> Envelope | None:
    try:
        return parse_comment(comment.body)
    except BusError:
        return None


def _ledger_record(comment: RawComment):
    try:
        return ledger.parse_record(comment.body)
    except ledger.LedgerError:
        return None


def find_records(world: World, target: Target, txn: str, message_id: str) -> Records:
    """Sort every record touching this transaction by whether its author may write it."""
    trust, out = target.trust, Records()
    for c in world.pr_comments:
        env = _envelope(c)
        if env is None:
            continue
        answers = env.kind == "WAVE_REVIEW" and (
            env.parent == message_id or env.message_id == review_id(txn))
        commands = env.kind == "WAVE_COMMAND" and env.message_id in (command_id(txn),
                                                                     next_id(txn))
        if not (answers or commands):
            continue
        if trust.is_publisher(c.author) and answers and env.message_id == review_id(txn) \
                and env.parent == message_id:
            out.reviews.append((c, env))
        elif trust.is_publisher(c.author) and commands:
            out.commands.append((c, env))
        elif trust.trusts(c.author) and answers:
            out.human_answers.append(c)
        else:
            out.ignored.append({"comment_id": c.comment_id, "author": c.author,
                                "why": f"{env.kind} for this transaction from an identity "
                                       "not allowed that role"})
    cited = txn.split("-")[1]
    for c in world.issue_comments:
        record = _ledger_record(c)
        if record is None or record.fields.get("transaction") != txn:
            continue
        # Only a record in the publisher's exact form can be this transaction's.
        # Every workflow in the repository shares the publisher identity, so a
        # malformed one is somebody else's text, reported and never a wedge.
        form = {ledger.VERDICT: (ledger.VERDICT_KEYS, ledger.render_verdict, "selecting_checkpoint"),
                ledger.CHECKPOINT: (ledger.CHECKPOINT_KEYS, ledger.render_checkpoint,
                                    "prior_checkpoint")}.get(record.schema)
        exact = form is not None and tuple(record.fields) == form[0] \
            and _renders(form[1], record.fields, c.body) and record.fields[form[2]] == cited
        if trust.is_publisher(c.author) and exact and record.schema == ledger.VERDICT:
            out.verdicts.append(c)
        elif trust.is_publisher(c.author) and exact:
            out.checkpoints.append(c)
        else:
            out.ignored.append({"comment_id": c.comment_id, "author": c.author,
                                "why": f"{record.schema} naming this transaction, not in the "
                                       "publisher's exact form from the publisher"})
    return out


def _renders(render, fields, body: str) -> bool:
    try:
        return render(fields) == body
    except ledger.LedgerError:
        return False


# ------------------------------------------------------------ live revalidation

@dataclass
class Txn:
    """What one run is doing, and what it has seen."""

    target: Target
    comment_id: int
    digest: str
    run: Runner
    clock: Callable | None = None
    measured_head: str | None = None
    selftest_exit: int | None = None
    validation: Evidence | None = None
    subject: Subject | None = None
    tid: str | None = None
    transition: Transition | None = None
    writes: list[dict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _subject_comment(world: World, txn: Txn) -> RawComment | None:
    live = [c for c in world.pr_comments if c.comment_id == txn.comment_id]
    return live[0] if len(live) == 1 else None


def check_message_unchanged(world: World, txn: Txn) -> None:
    """Still on the transport PR, still by a trusted speaker, byte-identical."""
    live = _subject_comment(world, txn)
    if live is None:
        raise BusError(E.GATE_COMMENT_MISMATCH, f"comment {txn.comment_id} is gone")
    if not txn.target.trust.trusts(live.author):
        raise BusError(E.UNTRUSTED_AUTHOR, f"comment {txn.comment_id} is by {live.author}")
    if digest(live.body) != txn.digest:
        raise BusError(E.GATE_COMMENT_MISMATCH, f"comment {txn.comment_id} was edited")


def check_authority_unmoved(world: World, txn: Txn) -> None:
    """The checkpoint the message cites is still the latest link of the chain."""
    cited = txn.subject.envelope.authority["checkpoint"]
    if world.authority.checkpoint != cited:
        raise BusError(E.STALE_AUTHORITY, f"latest K is {world.authority.checkpoint}; the "
                       f"transaction started from {cited}")


def check_queue_head(world: World, txn: Txn) -> None:
    """ACCEPTED, not cancelled, and the ONE message the Manager is due to answer."""
    env = txn.subject.envelope
    record = world.state.record_of(env.message_id)
    if record is None or record.comment_id != txn.comment_id:
        raise BusError(E.GATE_COMMENT_MISMATCH, f"{env.message_id} is not accepted as comment "
                       f"{txn.comment_id}")
    wave = world.state.waves.get(env.wave)
    if wave is not None and wave.aborted is not None:
        raise BusError(E.WAVE_ABORTED, f"wave {env.wave} was aborted by "
                       f"{wave.aborted.message_id}")
    if env.wave in world.state.superseded():
        raise BusError(E.WAVE_SUPERSEDED, f"wave {env.wave} was superseded")
    queue = world.state.manager_queue()
    if not queue or queue[0].message_id != env.message_id:
        head = queue[0].message_id if queue else None
        raise BusError(E.GATE_ALREADY_HANDLED if head is None else E.GATE_QUEUED,
                       f"{env.message_id} is not the head of the Manager queue (head: {head})")


def check_branch_tip(world: World, txn: Txn) -> None:
    """A result is reviewable only while its branch still ends at its head."""
    env = txn.subject.envelope
    if env.kind != "WAVE_RESULT":
        return
    branch = env.body["branch"]
    tip = world.branch_tips.get(branch) or branch_tip(txn.target, branch, txn.run)
    world.branch_tips[branch] = tip
    if tip != env.body["head"]:
        raise BusError(E.BRANCH_TIP_MISMATCH, f"{branch} is at {tip}, the result claims "
                       f"{env.body['head']}")
    if txn.measured_head is not None and txn.measured_head != env.body["head"]:
        raise BusError(E.BRANCH_TIP_MISMATCH, f"the independently tested head "
                       f"{txn.measured_head} is not the result head {env.body['head']}")


Check = Callable[[World, Txn], None]
PRE_COMMIT: tuple[tuple[str, Check], ...] = (
    ("message_unchanged", check_message_unchanged),
    ("authority_unmoved", check_authority_unmoved),
    ("queue_head", check_queue_head),
    ("branch_tip", check_branch_tip),
)


def check_commit_is_live(world: World, txn: Txn) -> None:
    """After the commit, a successor may follow only its own checkpoint."""
    fields = world.authority.publisher
    if fields is None or fields.get("transaction") != txn.tid:
        raise BusError(E.TXN_SUPERSEDED, f"the live checkpoint is {world.authority.checkpoint}, "
                       "not this transaction's")


POST_COMMIT: tuple[tuple[str, Check], ...] = (
    ("commit_is_live", check_commit_is_live),
    ("branch_tip", check_branch_tip),
)


# ----------------------------------------------------------------- the run

class Stop(Exception):
    """End this run with an exit code and a code, after reporting."""

    def __init__(self, exit_code: int, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.exit_code, self.code, self.detail = exit_code, code, detail


def _revalidate(txn: Txn, checks, stage: str) -> World:
    world = observe(txn.target, txn.run)
    for name, check in checks:
        try:
            check(world, txn)
        except BusError as exc:
            raise Stop(EXIT_REFUSED if checks is PRE_COMMIT else EXIT_AFTER_COMMIT,
                       exc.code, f"before the {stage} write, {name}: {exc.detail}")
    return world


def _write(txn: Txn, number: int, body: str, what: str) -> None:
    post_comment(body, number, txn.target.repo, txn.run, dry_run=False)
    txn.writes.append({"record": what, "target": number})


def _origin(world: World, target: Target, message_id: str) -> Envelope | None:
    for c in world.pr_comments:
        if not target.trust.trusts(c.author):
            continue
        env = _envelope(c)
        if env is not None and env.kind == "WAVE_COMMAND" and env.message_id == message_id:
            return env
    return None


def _evidence_of(records: Records, supplied: Evidence | None) -> Evidence | None:
    """A durable review fixes the evidence too: a rerun never re-judges the checks."""
    if not records.reviews:
        return supplied
    raw = records.reviews[0][1].body.get("validation")
    return goal.evidence_from_mapping(raw) if raw is not None else None


def _binding(world: World, target: Target, prior: Prior,
             subject: Subject) -> tuple[Envelope | None, Binding | None, str]:
    """The origin command this message answers, and the goal plan it is bound to."""
    origin_id, _ = lineage(prior, subject)
    origin = resolve_origin(prior, origin_id, lambda mid: _origin(world, target, mid))
    binding, why = goal.bind(origin, world.issue_comments, target.trust)
    return origin, binding, why


def binding_for(target: Target, comment_id: int, run: Runner | None = None):
    """(binding, why) for a Worker message, read live: what the checks runner runs."""
    run = run or Runner()
    world = observe(target, run)
    live = _subject_comment(world, Txn(target, comment_id, "", run))
    env = _envelope(live) if live is not None else None
    if env is None or env.actor != "WORKER" or not target.trust.trusts(live.author):
        raise BusError(E.GATE_COMMENT_MISMATCH, f"comment {comment_id} is not a Worker message")
    prior = world.resolution.lineage
    _, binding, why = _binding(world, target, prior, Subject(comment_id, "", env))
    return binding, why


def _decision_of(records: Records, supplied: Decision | None, txn: Txn) -> Decision:
    """A durable review fixes the decision. Otherwise the supplied one, or nothing."""
    durable = {json.dumps(env.body["decision"], sort_keys=True) for _, env in records.reviews}
    if len(durable) > 1:
        raise Stop(EXIT_REFUSED, E.TXN_CONFLICT, "the transaction's reviews disagree")
    if durable:
        found = decision_module.from_mapping(records.reviews[0][1].body["decision"])
        if supplied is not None and supplied != found:
            txn.notes.append("a durable review already fixed the decision; the supplied "
                             "decision was not used")
        return found
    if supplied is None:
        raise Stop(EXIT_REFUSED, E.TXN_NO_DECISION,
                   "no durable review and no decision was supplied")
    return supplied


def publish(target: Target, comment_id: int, body_digest: str, supplied: Decision | None,
            run: Runner, measured_head: str | None = None, selftest_exit: int | None = None,
            clock: Callable | None = None, validation: Evidence | None = None) -> dict:
    """Drive one transaction to completion, or stop at the first unsafe step."""
    txn = Txn(target, comment_id, body_digest, run, clock, measured_head, selftest_exit,
              validation)
    report: dict = {"comment_id": comment_id, "writes": txn.writes, "notes": txn.notes}
    try:
        report.update(_publish(txn, supplied))
        report["exit"] = EXIT_COMPLETE
    except Stop as stop:
        report.update({"exit": stop.exit_code, "code": stop.code, "detail": stop.detail})
    return report


def _publish(txn: Txn, supplied: Decision | None) -> dict:
    target = txn.target
    world = observe(target, txn.run)
    live = _subject_comment(world, txn)
    env = _envelope(live) if live is not None else None
    if env is None or env.actor != "WORKER":
        raise Stop(EXIT_REFUSED, E.GATE_COMMENT_MISMATCH,
                   f"comment {txn.comment_id} is not a Worker message on the transport PR")
    txn.subject = Subject(txn.comment_id, txn.digest, env)
    tid = txn.tid = txn_id(env.authority["checkpoint"], txn.comment_id)
    records = find_records(world, target, tid, env.message_id)
    out = {"transaction": tid, "records": records.report()}

    committed = [c for c in records.checkpoints if c.comment_id in world.resolution.chain]
    if committed:
        return {**out, **_after_commit(txn, world, committed[0], records)}
    if records.checkpoints:
        raise Stop(EXIT_AFTER_COMMIT, E.TXN_RACE_LOST,
                   f"checkpoint(s) {[c.comment_id for c in records.checkpoints]} carry this "
                   "transaction but are not links of the chain")
    if records.human_answers:
        raise Stop(EXIT_REFUSED, E.GATE_ALREADY_HANDLED,
                   f"a trusted speaker already answered in {records.human_answers[0].comment_id}")

    prior = world.resolution.lineage
    if prior.checkpoint != env.authority["checkpoint"]:
        raise Stop(EXIT_REFUSED, E.STALE_AUTHORITY,
                   f"latest K is {prior.checkpoint}; the message cites "
                   f"{env.authority['checkpoint']}")
    decision = _decision_of(records, supplied, txn)
    try:
        origin, binding, why = _binding(world, target, prior, txn.subject)
        transition = build(prior, txn.subject, decision, transport_pr=target.transport_pr,
                           origin=origin, binding=binding,
                           evidence=_evidence_of(records, txn.validation),
                           measured_head=txn.measured_head, selftest_exit=txn.selftest_exit)
    except BusError as exc:
        raise Stop(EXIT_REFUSED, exc.code, exc.detail)
    txn.transition = transition
    out["verdict"] = transition.letter
    if binding is None:
        txn.notes.append(f"no goal plan binds this wave: {why}")

    # Every record already present must be exactly this transaction's.
    review = transition.review(compose.stamp(txn.clock))
    for comment, found in records.reviews:
        if not same_message(found, review):
            raise Stop(EXIT_REFUSED, E.TXN_CONFLICT, f"review {comment.comment_id} is not "
                       "this transaction's review")
    verdict_body = transition.verdict_body()
    for comment in records.verdicts:
        if comment.body != verdict_body:
            raise Stop(EXIT_REFUSED, E.TXN_CONFLICT, f"verdict {comment.comment_id} is not "
                       "this transaction's verdict")

    if not records.reviews:
        _revalidate(txn, PRE_COMMIT, "review")
        _write(txn, target.transport_pr, review.render(), "WAVE_REVIEW")
    if not records.verdicts:
        _revalidate(txn, PRE_COMMIT, "verdict")
        _write(txn, target.issue, verdict_body, "V")
        world = observe(target, txn.run)
        records = find_records(world, target, tid, env.message_id)
        if not records.verdicts:
            raise Stop(EXIT_REFUSED, E.TXN_CONFLICT, "the verdict write is not visible")
    verdict_comment = records.verdicts[0].comment_id

    # ---- the commit point
    world = _revalidate(txn, PRE_COMMIT, "checkpoint")
    unanswered = [world.state.record_of(e.message_id).comment_id
                  for e in world.state.manager_queue() if e.message_id != env.message_id]
    _write(txn, target.issue, transition.checkpoint_body(verdict_comment, unanswered), "K")

    world = observe(target, txn.run)
    records = find_records(world, target, tid, env.message_id)
    committed = [c for c in records.checkpoints if c.comment_id in world.resolution.chain]
    if not committed:
        raise Stop(EXIT_AFTER_COMMIT, E.TXN_RACE_LOST,
                   f"the checkpoint was written but {world.authority.checkpoint} is the chain")
    return {**out, **_after_commit(txn, world, committed[0], records)}


def _after_commit(txn: Txn, world: World, checkpoint: RawComment, records: Records) -> dict:
    """The commit happened. Only the successor it names can still be owed."""
    fields = ledger.parse_record(checkpoint.body).fields
    out = {"committed": checkpoint.comment_id, "verdict": fields["verdict"]}
    if fields["successor_command"] == NONE:
        return {**out, "state": "COMPLETE"}
    live = world.authority.publisher is not None and \
        world.authority.publisher.get("transaction") == txn.tid
    if records.commands:
        if not live:
            txn.notes.append("the successor was posted; authority has moved on since")
            return {**out, "state": "COMPLETE", "successor": records.commands[0][0].comment_id}
        for comment, _ in records.commands:
            if _accepted(world, comment.comment_id):
                return {**out, "state": "COMPLETE", "successor": comment.comment_id}
        raise Stop(EXIT_AFTER_COMMIT, E.TXN_CONFLICT,
                   f"command(s) {[c.comment_id for c, _ in records.commands]} carry this "
                   "transaction's id but are not its successor")
    world = _revalidate(txn, POST_COMMIT, "successor")
    # Exactly the command the live chain derives -- the same object every reader
    # will compare the posted one against.
    derived = world.authority.successor
    if derived is None or derived.message_id != fields["successor_command"]:
        raise Stop(EXIT_AFTER_COMMIT, E.TXN_CONFLICT,
                   f"the live checkpoint does not derive {fields['successor_command']}")
    successor = dataclasses.replace(derived, created_at=compose.stamp(txn.clock))
    _write(txn, txn.target.transport_pr, successor.render(), "WAVE_COMMAND")
    world = observe(txn.target, txn.run)
    record = world.state.record_of(successor.message_id)
    if record is None:
        raise Stop(EXIT_AFTER_COMMIT, E.TXN_CONFLICT, "the successor is not accepted by the bus")
    return {**out, "state": "COMPLETE", "successor": record.comment_id}


def _accepted(world: World, comment_id: int) -> bool:
    return any(r.comment_id == comment_id and r.status == ACCEPTED for r in world.state.records)


# ------------------------------------------------------------------- entry

def result_head(target: Target, comment_id: int, run: Runner) -> str:
    """The head a Worker message claims, for the evidence job. '' when it has none."""
    world = observe(target, run)
    live = [c for c in world.pr_comments if c.comment_id == comment_id]
    env = _envelope(live[0]) if len(live) == 1 else None
    if env is None or env.actor != "WORKER" or not target.trust.trusts(live[0].author):
        raise BusError(E.GATE_COMMENT_MISMATCH, f"comment {comment_id} is not a Worker message")
    return env.body["head"] if env.kind == "WAVE_RESULT" else ""


def main(argv: Sequence[str] | None = None, run: Runner | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent_bus.publisher",
                                     description="deterministic Manager publisher (no model)")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--issue", type=int, default=1)
    parser.add_argument("--pr", type=int, required=True, help="the transport pull request")
    parser.add_argument("--trusted-author", required=True, help="exact GitHub login")
    sub = parser.add_subparsers(dest="command", required=True)
    p_head = sub.add_parser("result-head", help="print the head a Worker message claims")
    p_head.add_argument("--comment-id", type=int, required=True)
    p_pub = sub.add_parser("publish", help="drive one transaction to completion")
    p_pub.add_argument("--comment-id", type=int, required=True)
    p_pub.add_argument("--digest", required=True, help="sha256 of the admitted body")
    p_pub.add_argument("--decision-file", default=None,
                       help="the model's decision; omit to resume from durable state")
    p_pub.add_argument("--measured-head", default=None)
    p_pub.add_argument("--selftest-exit", type=int, default=None)
    p_pub.add_argument("--validation-file", default=None,
                       help="`agent_bus.goal run-checks` evidence for the result head")
    args = parser.parse_args(argv)
    run = run or Runner()
    target = Target(args.repo, args.issue, args.pr,
                    Trust(frozenset({args.trusted_author.lower()}), "publisher"))
    try:
        if args.command == "result-head":
            print(result_head(target, args.comment_id, run))
            return EXIT_COMPLETE
        supplied = None
        if args.decision_file:
            with open(args.decision_file, encoding="utf-8") as handle:
                supplied = decision_module.parse(handle.read())
        validation = None
        if args.validation_file:
            with open(args.validation_file, encoding="utf-8") as handle:
                validation = goal.evidence_from_mapping(json.load(handle))
        report = publish(target, args.comment_id, args.digest, supplied, run,
                         measured_head=args.measured_head or None,
                         selftest_exit=args.selftest_exit, validation=validation)
    except BusError as exc:
        print(json.dumps({"exit": EXIT_BAD_INPUT, "code": exc.code, "detail": exc.detail},
                         indent=2, sort_keys=True))
        return EXIT_BAD_INPUT
    except AuthorityError as exc:
        print(json.dumps({"exit": EXIT_BAD_INPUT, "code": E.AUTHORITY_UNRESOLVED,
                          "detail": str(exc)}, indent=2, sort_keys=True))
        return EXIT_BAD_INPUT
    print(json.dumps(report, indent=2, sort_keys=True))
    return report["exit"]


if __name__ == "__main__":  # pragma: no cover - module entry point
    raise SystemExit(main())
