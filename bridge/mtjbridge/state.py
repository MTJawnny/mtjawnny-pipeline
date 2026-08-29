"""Durable cycle state and the execution claim.

Design rule from the task contract: *no important execution state only in RAM*.

Every fact the state machine needs to resume after a crash is derived by reading
the GitHub issue ledger back. The local file written here is a convenience cache
and a same-host concurrency guard only — deleting it must never change what the
bridge concludes, and `reconstruct()` proves that by taking GitHub alone.
"""

from __future__ import annotations

import dataclasses
import datetime as _dt
import json
import os
import socket
import time
from pathlib import Path

from .protocol import Claim, ProtocolError, parse_claim, parse_result, parse_review, render_block

CLAIM_MARKER = "mtj-claim/1"
RESULT_MARKER = "mtj-result/1"
REVIEW_MARKER = "mtj-review/1"

DEFAULT_STATE_DIR = Path(os.environ.get("MTJ_STATE_DIR", Path.home() / ".mtj-bridge"))


def worker_id() -> str:
    return f"{socket.gethostname()}/{os.getpid()}"


def utcnow() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclasses.dataclass
class IssueLedger:
    """What GitHub alone says has happened on one task issue."""

    number: int
    claims: list[Claim] = dataclasses.field(default_factory=list)
    results: list = dataclasses.field(default_factory=list)
    reviews: list = dataclasses.field(default_factory=list)
    parse_errors: list[str] = dataclasses.field(default_factory=list)

    @property
    def has_result(self) -> bool:
        return bool(self.results)

    @property
    def latest_result(self):
        return self.results[-1] if self.results else None

    @property
    def latest_review(self):
        return self.reviews[-1] if self.reviews else None

    @property
    def repair_count(self) -> int:
        return sum(1 for r in self.reviews if r.verdict == "REPAIR")

    @property
    def active_claim(self) -> Claim | None:
        for claim in reversed(self.claims):
            if not claim.is_expired():
                return claim
        return None

    def next_phase(self) -> str:
        """The one thing that should happen next on this issue, from GitHub alone."""
        if not self.results:
            return "WORKER_EXECUTE"
        if len(self.reviews) < len(self.results):
            return "MANAGER_REVIEW"
        latest = self.latest_review
        if latest is None:
            return "MANAGER_REVIEW"
        if latest.halts_automation:
            return "HALTED"
        return "COMPLETE"


def reconstruct(github, issue_number: int) -> IssueLedger:
    """Rebuild the full state of one task from GitHub comments alone.

    This is the crash-recovery primitive: a brand-new process with an empty
    filesystem calls this and knows exactly what was and was not completed.
    """
    ledger = IssueLedger(number=issue_number)
    for comment in github.list_comments(issue_number):
        body = comment.get("body") or ""
        try:
            if CLAIM_MARKER in body:
                ledger.claims.append(parse_claim(body))
            elif RESULT_MARKER in body:
                ledger.results.append(parse_result(body))
            elif REVIEW_MARKER in body:
                ledger.reviews.append(parse_review(body))
        except ProtocolError as exc:
            ledger.parse_errors.append(f"comment by {comment.get('author', {}).get('login')}: {exc}")
    return ledger


# --------------------------------------------------------------------------
# claim / lock
# --------------------------------------------------------------------------


class ClaimError(RuntimeError):
    """Another worker holds an unexpired claim on this issue."""


def claim_payload(task_id: str, issue: int, lease_seconds: int = 3600) -> dict:
    return {
        "schema": "mtj-claim/1",
        "task": task_id,
        "issue": issue,
        "worker_id": worker_id(),
        "claimed_at": utcnow(),
        "lease_seconds": lease_seconds,
    }


def acquire(github, issue: int, task_id: str, lease_seconds: int = 3600,
            state_dir: Path | None = None, dry_run: bool = False) -> Claim:
    """Take a durable claim on an issue, refusing if another worker holds one.

    Two layers, because they fail differently:
      * a local lockfile catches two processes on THIS host instantly;
      * a GitHub claim comment catches a second host, and survives a crash.
    """
    state_dir = state_dir or DEFAULT_STATE_DIR
    state_dir.mkdir(parents=True, exist_ok=True)
    lock_path = state_dir / f"issue-{issue}.lock"

    ledger = reconstruct(github, issue)
    existing = ledger.active_claim
    me = worker_id()
    if existing and existing.worker_id != me:
        raise ClaimError(
            f"issue #{issue} is claimed by {existing.worker_id} at {existing.claimed_at} "
            f"(lease {existing.lease_seconds}s, not expired). Refusing to double-execute."
        )

    payload = claim_payload(task_id, issue, lease_seconds)
    if not dry_run:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            # Judge staleness by the lease the HOLDER recorded, not by the lease this
            # caller happens to be asking for. Using the caller's lease would let a
            # short-lease holder block a long-lease acquirer and vice versa.
            age = time.time() - lock_path.stat().st_mtime
            try:
                held_lease = int(json.loads(lock_path.read_text()).get("lease_seconds", lease_seconds))
            except (OSError, ValueError, AttributeError):
                held_lease = lease_seconds
            if age < held_lease:
                raise ClaimError(
                    f"local lock {lock_path} held for {age:.0f}s of a {held_lease}s lease "
                    "by another process on this host"
                ) from None
            lock_path.unlink()
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, "w") as handle:
            json.dump(payload, handle)
        github.post_comment(
            issue,
            render_block(payload, "Durable execution claim. A second worker must not execute this issue "
                                  "while this claim is unexpired."),
            idempotency_key=f"claim-{task_id}-{payload['claimed_at']}",
        )
    return parse_claim(render_block(payload))


def release(issue: int, state_dir: Path | None = None) -> None:
    state_dir = state_dir or DEFAULT_STATE_DIR
    lock_path = state_dir / f"issue-{issue}.lock"
    if lock_path.exists():
        lock_path.unlink()
