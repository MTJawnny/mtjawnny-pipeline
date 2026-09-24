"""Read the ONE authority: GitHub Issue #1, latest `K` -> active `T`.

This module deliberately does the smallest possible amount of parsing on the
existing human-authored checkpoint format, and it halts loudly on any shape it
does not recognise. It is not a YAML parser and does not pretend to be one; it
reads the three scalars a checkpoint must carry and refuses everything else.

The selector spelling is the repository's, unchanged: the latest `K` is selected
because it is the LATEST, never because it accepted anything.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Sequence

from agent_bus.machine import Authority, RawComment
from agent_bus.shell import Completed, Runner
from agent_bus.trust import Trust

CHECKPOINT_RE = re.compile(r"^\s*schema:\s*mtj-checkpoint/(\d+)\s*$", re.MULTILINE)
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class AuthorityError(RuntimeError):
    """The authority could not be resolved. Never guessed around."""


def _scalar(text: str, key: str) -> str | None:
    match = re.search(rf"^\s*{re.escape(key)}:\s*(\S+)\s*(?:#.*)?$", text, re.MULTILINE)
    return match.group(1) if match else None


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

    def as_dict(self) -> dict:
        out = self.authority.as_dict()
        out["checkpoint_author"] = self.checkpoint_author
        out["untrusted_checkpoint_candidates"] = [
            {"comment_id": cid, "author": author}
            for cid, author in self.untrusted_candidates
        ]
        return out


def resolve_authority(comments: Sequence[RawComment], issue: int,
                      trust: Trust) -> Resolution:
    """Latest TRUSTED `K` -> active `T`. Anything ambiguous is an error, not a guess.

    The repository is public, so "the latest comment that looks like a checkpoint"
    is a selector anyone can write. Only a checkpoint from a trusted speaker can
    select anything.

    An untrusted checkpoint-shaped comment is SKIPPED rather than fatal, and it is
    REPORTED. Halting on it would hand any passer-by a way to stop the Worker by
    posting one; obeying it would hand them the Worker. Skipping it silently would
    be the third mistake, so every one that was refused is named in the result.
    """
    trust.require()
    shaped = [c for c in comments if CHECKPOINT_RE.search(c.body)]
    untrusted = tuple((c.comment_id, c.author) for c in shaped if not trust.trusts(c.author))
    checkpoints = [c for c in shaped if trust.trusts(c.author)]
    if not checkpoints:
        raise AuthorityError(
            f"issue {issue} carries no mtj-checkpoint comment from a trusted speaker "
            f"({len(untrusted)} checkpoint-shaped comments were refused)")
    latest = checkpoints[-1]

    head = _scalar(latest.body, "h") or _scalar(latest.body, "accepted_head")
    active = _scalar(latest.body, "a") or _scalar(latest.body, "active_task")
    if head is None or active is None:
        raise AuthorityError(
            f"checkpoint {latest.comment_id} is missing h/a; it cannot select anything")
    if not SHA_RE.match(head):
        raise AuthorityError(f"checkpoint {latest.comment_id} h={head!r} is not a 40-hex sha")
    if not re.fullmatch(r"\d+", active):
        raise AuthorityError(f"checkpoint {latest.comment_id} a={active!r} is not a comment id")

    return Resolution(
        authority=Authority(issue=issue, checkpoint=latest.comment_id,
                            task=int(active), accepted_head=head),
        checkpoint_author=latest.author,
        untrusted_candidates=untrusted,
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
