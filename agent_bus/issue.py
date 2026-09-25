"""Read the ONE authority: GitHub Issue #1, latest `K` -> active `T`.

This module deliberately does the smallest possible amount of parsing on the
existing human-authored checkpoint format, and it halts loudly on any shape it
does not recognise. It is not a YAML parser and does not pretend to be one: a
checkpoint is a record that OPENS its comment, and only its top-level `h`/`a`
scalars are read (`agent_bus.ledger`). Checkpoint-looking text anywhere else --
quoted in a verdict, indented under another key -- is a lookalike and selects
nothing.

The selector spelling is the repository's, unchanged: the latest `K` is selected
because it is the LATEST, never because it accepted anything.

Two identities can write a checkpoint. A trusted human's is law as written. The
publisher's (`agent_bus.trust.PUBLISHER`) is law only as the exact next link of
the chain: it must name the checkpoint immediately before it as its prior, and
it must be byte-for-byte the record the transition law derives from that prior
and the Worker message it answers. So the chain is its own compare-and-swap:
two publisher checkpoints racing from one prior cannot both be links, and the
first one GitHub ordered wins for every reader alike.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Sequence

from agent_bus import goal, ledger
from agent_bus.errors import BusError
from agent_bus.machine import Authority, RawComment
from agent_bus.protocol import Envelope, parse_comment
from agent_bus.shell import Completed, Runner
from agent_bus.transition import (
    MANAGER_ANSWERS, Found, Prior, Subject, digest, validate_publisher_checkpoint,
)
from agent_bus.trust import Trust

SHA_RE = ledger.SHA_RE


class AuthorityError(RuntimeError):
    """The authority could not be resolved. Never guessed around."""


def read_comments(issue: int = 1, repo: str | None = None,
                  run: Runner | None = None, source: str | None = None) -> list[RawComment]:
    """Every comment on an issue OR pull request, in GitHub's own order.

    A pull request's conversation comments live on the issues endpoint, so one
    reader serves both surfaces; `source` only labels where a comment was read,
    and a label has never made anything authoritative.
    """
    run = run or Runner()
    slug = repo or _repo_slug(run)
    result = run(["gh", "api", "--paginate",
                  f"repos/{slug}/issues/{issue}/comments?per_page=100"])
    if result.returncode != 0:
        raise AuthorityError(f"gh api failed reading issue {issue}: {result.stderr.strip()}")
    payload = _json_stream(result.stdout)
    label = source or f"issue:{issue}"
    return [
        RawComment(source=label, comment_id=int(c["id"]),
                   author=str(c["user"]["login"]), body=str(c.get("body") or ""))
        for c in payload
    ]


def _json_stream(text: str) -> list[dict]:
    """`gh api --paginate` concatenates JSON arrays; read them all or halt."""
    decoder = json.JSONDecoder()
    out: list[dict] = []
    index = 0
    body = text.strip()
    while index < len(body):
        chunk, end = decoder.raw_decode(body, index)
        if not isinstance(chunk, list):
            raise AuthorityError(f"expected a JSON array of comments, got {type(chunk).__name__}")
        out.extend(chunk)
        index = end
        while index < len(body) and body[index] in " \r\n\t":
            index += 1
    return out


@dataclass(frozen=True)
class Resolution:
    """The selection, plus what was refused on the way to it."""

    authority: Authority
    checkpoint_author: str
    untrusted_candidates: tuple[tuple[int, str], ...] = ()
    # Publisher checkpoints that are not links of the chain, with the reason.
    refused_candidates: tuple[tuple[int, str, str], ...] = ()
    # Checkpoint-looking text after the selected K that is not a K.
    lookalikes: tuple[tuple[int, str], ...] = ()
    # Every checkpoint that was a link, oldest first; the last is `authority`.
    chain: tuple[int, ...] = ()
    lineage: Prior | None = None

    def as_dict(self) -> dict:
        out = self.authority.as_dict()
        out["checkpoint_author"] = self.checkpoint_author
        out["untrusted_checkpoint_candidates"] = [
            {"comment_id": cid, "author": author}
            for cid, author in self.untrusted_candidates
        ]
        out["refused_checkpoint_candidates"] = [
            {"comment_id": cid, "author": author, "reason": reason}
            for cid, author, reason in self.refused_candidates
        ]
        out["checkpoint_lookalikes"] = [
            {"comment_id": cid, "author": author} for cid, author in self.lookalikes
        ]
        return out


def _prior(comment: RawComment, issue: int) -> Prior:
    """A HUMAN checkpoint as the start of a transition. Strict, or LedgerError."""
    checkpoint = ledger.read_checkpoint(comment.body)
    return Prior(issue=issue, checkpoint=comment.comment_id, head=checkpoint.head,
                 active=checkpoint.active)


class _Transport:
    """Lookups into the transport PR that a publisher checkpoint must bind to."""

    def __init__(self, comments: Sequence[RawComment], issue_comments: Sequence[RawComment],
                 trust: Trust) -> None:
        self.trust = trust
        self.comments = list(comments)
        self.issue_comments = list(issue_comments)

    def _envelope(self, comment: RawComment) -> Envelope | None:
        try:
            return parse_comment(comment.body)
        except BusError:
            return None

    def subject(self, comment_id: int) -> tuple[Subject, str] | None:
        for c in self.comments:
            if c.comment_id != comment_id or not self.trust.trusts(c.author):
                continue
            env = self._envelope(c)
            if env is not None and env.actor == "WORKER" and env.kind in MANAGER_ANSWERS:
                return Subject(c.comment_id, digest(c.body), env), c.author
        return None

    def origin(self, message_id: str) -> Envelope | None:
        for c in self.comments:
            if not self.trust.trusts(c.author):
                continue
            env = self._envelope(c)
            if env is not None and env.kind == "WAVE_COMMAND" and env.message_id == message_id:
                return env
        return None

    def verdict(self, comment_id: int) -> Found | None:
        for c in self.issue_comments:
            if c.comment_id == comment_id and self.trust.is_publisher(c.author):
                return Found(c.comment_id, c.author, c.body)
        return None


def resolve_authority(comments: Sequence[RawComment], issue: int, trust: Trust,
                      transport: Sequence[RawComment] | None = None,
                      transport_pr: int | None = None) -> Resolution:
    """Latest `K` on the chain -> active `T`. Anything ambiguous is an error, not a guess.

    The repository is public, so "the latest comment that looks like a checkpoint"
    is a selector anyone can write. Only a checkpoint from a trusted speaker, or
    a publisher checkpoint that is the exact next link, can select anything.

    An untrusted checkpoint-shaped comment is SKIPPED rather than fatal, and it is
    REPORTED. Halting on it would hand any passer-by a way to stop the Worker by
    posting one; obeying it would hand them the Worker. Skipping it silently would
    be the third mistake, so every one that was refused is named in the result.
    A publisher checkpoint that is not a link is treated the same way.

    A publisher checkpoint binds to a Worker message on the transport PR, so it
    cannot be judged from the issue alone. Reading one without `transport` HALTS:
    quietly falling back to the checkpoint before it would make the machine read
    one authority and a human another.
    """
    trust.require()
    untrusted: list[tuple[int, str]] = []
    refused: list[tuple[int, str, str]] = []
    chain: list[int] = []
    current: RawComment | None = None
    lineage: Prior | None = None
    publisher_fields = None
    lookup = _Transport(transport or (), comments, trust)
    after_latest: list[RawComment] = []

    for c in comments:
        if not ledger.is_checkpoint(c.body):
            after_latest.append(c)
            continue
        if trust.trusts(c.author):
            current, lineage, publisher_fields = c, None, None
            chain.append(c.comment_id)
            after_latest = []
            continue
        if not trust.is_publisher(c.author):
            untrusted.append((c.comment_id, c.author))
            continue
        if transport is None or transport_pr is None:
            raise AuthorityError(
                f"checkpoint {c.comment_id} was written by the publisher and binds to a "
                "Worker message on the transport PR; resolve with the transport PR's "
                "comments (--pr), not the issue alone")
        if current is None:
            refused.append((c.comment_id, c.author, "no checkpoint precedes it"))
            continue
        try:
            prior = lineage if lineage is not None else _prior(current, issue)
        except ledger.LedgerError as exc:
            refused.append((c.comment_id, c.author, f"its prior is malformed: {exc}"))
            continue
        try:
            lineage = validate_publisher_checkpoint(
                Found(c.comment_id, c.author, c.body), prior, transport_pr=transport_pr,
                subject_of=lookup.subject, origin_of=lookup.origin, verdict_of=lookup.verdict,
                plan_of=lambda origin: goal.bind(origin, comments, trust)[0])
        except BusError as exc:
            refused.append((c.comment_id, c.author, exc.detail))
            continue
        current = c
        publisher_fields = dict(ledger.parse_record(c.body).fields)
        chain.append(c.comment_id)
        after_latest = []

    if current is None:
        raise AuthorityError(
            f"issue {issue} carries no mtj-checkpoint comment from a trusted speaker "
            f"({len(untrusted)} untrusted and {len(refused)} refused publisher "
            "checkpoint-shaped comments)")
    if lineage is None:
        try:
            lineage = _prior(current, issue)
        except ledger.LedgerError as exc:
            raise AuthorityError(f"checkpoint {current.comment_id}: {exc}")

    return Resolution(
        authority=Authority(issue=issue, checkpoint=current.comment_id,
                            task=lineage.active, accepted_head=lineage.head,
                            publisher=publisher_fields,
                            successor=lineage.successor if publisher_fields else None),
        checkpoint_author=current.author,
        untrusted_candidates=tuple(untrusted),
        refused_candidates=tuple(refused),
        lookalikes=tuple((c.comment_id, c.author) for c in after_latest
                         if ledger.is_lookalike(c.body)),
        chain=tuple(chain),
        lineage=lineage,
    )


def _repo_slug(run: Runner) -> str:
    result = run(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"])
    if result.returncode != 0:
        raise AuthorityError(f"cannot determine repository: {result.stderr.strip()}")
    return result.stdout.strip()


def post_comment(body: str, issue: int = 1, repo: str | None = None,
                 run: Runner | None = None, dry_run: bool = True) -> Completed | None:
    """Post to the issue. `dry_run` is the DEFAULT: writing is always explicit."""
    run = run or Runner()
    slug = repo or _repo_slug(run)
    argv = ["gh", "api", f"repos/{slug}/issues/{issue}/comments", "-f", f"body={body}"]
    if dry_run:
        return None
    result = run(argv)
    if result.returncode != 0:
        raise AuthorityError(f"failed to post to issue {issue}: {result.stderr.strip()}")
    return result
