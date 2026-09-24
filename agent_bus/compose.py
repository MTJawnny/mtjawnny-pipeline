"""Build the messages the Worker posts. Deterministic ids, injectable clock.

Message ids are DERIVED from what the message is about -- wave, unit, kind -- and
not from a random value or a timestamp. That is what makes re-posting harmless:
the same progress message twice is the same `message_id` twice, which the state
machine already treats as a recorded no-op. A random id would turn every retry
into a new fact.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Callable, Sequence

from agent_bus import SCHEMA
from agent_bus.protocol import Envelope
from agent_bus.machine import Authority

Clock = Callable[[], datetime]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def stamp(clock: Clock | None = None) -> str:
    return (clock or utc_now)().strftime("%Y-%m-%dT%H:%M:%SZ")


def slug(*parts: str) -> str:
    joined = "-".join(parts)
    cleaned = re.sub(r"[^a-z0-9]+", "-", joined.lower()).strip("-")
    return re.sub(r"-{2,}", "-", cleaned)


def _authority(authority: Authority) -> dict[str, int]:
    return {"issue": authority.issue, "checkpoint": authority.checkpoint,
            "task": authority.task}


def progress(command: Envelope, authority: Authority, unit: str, status: str,
             commit: str | None = None, note: str = "",
             clock: Clock | None = None) -> Envelope:
    body: dict = {"unit": unit, "status": status}
    if commit:
        body["commit"] = commit
    if note:
        body["note"] = note
    return Envelope(
        schema=SCHEMA,
        message_id=slug("w", command.wave, unit, "progress", status),
        actor="WORKER",
        kind="WAVE_PROGRESS",
        wave=command.wave,
        parent=command.message_id,
        authority=_authority(authority),
        base=command.base,
        created_at=stamp(clock),
        body=body,
    )


def result(command: Envelope, authority: Authority, status: str, branch: str,
           head: str, units: Sequence[dict], validation: Sequence[str] = (),
           discrepancies: Sequence[str] = (), note: str = "",
           clock: Clock | None = None) -> Envelope:
    body: dict = {
        "status": status,
        "branch": branch,
        "head": head,
        "units": [dict(u) for u in units],
        "validation": list(validation),
        "discrepancies": list(discrepancies),
        # A Worker never selects what runs next. The field exists so it can say so.
        "next": "NONE",
    }
    if note:
        body["note"] = note
    return Envelope(
        schema=SCHEMA,
        message_id=slug("w", command.wave, "result"),
        actor="WORKER",
        kind="WAVE_RESULT",
        wave=command.wave,
        parent=command.message_id,
        authority=_authority(authority),
        base=command.base,
        created_at=stamp(clock),
        body=body,
    )


def captain_required(command: Envelope, authority: Authority, question: str,
                     options: Sequence[str] = (), blocking: bool = True,
                     clock: Clock | None = None) -> Envelope:
    return Envelope(
        schema=SCHEMA,
        message_id=slug("w", command.wave, "captain", question[:32]),
        actor="WORKER",
        kind="CAPTAIN_REQUIRED",
        wave=command.wave,
        parent=command.message_id,
        authority=_authority(authority),
        base=command.base,
        created_at=stamp(clock),
        body={"question": question, "options": list(options), "blocking": blocking},
    )
