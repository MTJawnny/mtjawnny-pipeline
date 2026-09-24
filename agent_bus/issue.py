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
from typing import Sequence

from agent_bus.machine import Authority, RawComment
from agent_bus.shell import Completed, Runner

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


def resolve_authority(comments: Sequence[RawComment], issue: int = 1) -> Authority:
    """Latest `K` -> active `T`. Anything ambiguous is an error, not a guess."""
    checkpoints = [c for c in comments if CHECKPOINT_RE.search(c.body)]
    if not checkpoints:
        raise AuthorityError(f"issue {issue} carries no mtj-checkpoint comment")
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

    return Authority(issue=issue, checkpoint=latest.comment_id,
                     task=int(active), accepted_head=head)


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
