"""Builders for Agent Bus tests.

Every test below constructs its messages through these helpers so that a test
proving a REJECTION differs from the accepted case in exactly one field. A
negative control built by hand tends to be invalid for three reasons at once,
which proves nothing about the one rule it claims to exercise.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agent_bus import SCHEMA  # noqa: E402
from agent_bus.machine import Authority, RawComment  # noqa: E402
from agent_bus.trust import Trust  # noqa: E402

BASE = "a" * 40
OTHER_SHA = "b" * 40
CHECKPOINT = 5805993653
TASK = 5805989871
WAVE = "INFRA.AGENT-BUS-V1.W1"

AUTHORITY = Authority(issue=1, checkpoint=CHECKPOINT, task=TASK, accepted_head=BASE)

# The speaker set every test folds under. It is stated rather than defaulted,
# because the whole point of the R1 repair is that there is no default.
TRUSTED = Trust(frozenset({"mtjawnny"}), "test-fixture")
NOBODY_TRUSTED = Trust(frozenset(), "test-fixture-empty")


def unit(uid: str, depends_on=(), mutating=True, allow=("agent_bus/**",),
         validation=("python3 -m agent_bus selftest",), **extra) -> dict:
    body = {
        "id": uid,
        "objective": f"do {uid}",
        "depends_on": list(depends_on),
        "allow_paths": list(allow),
        "validation": list(validation),
        "mutating": mutating,
    }
    body.update(extra)
    return body


def envelope(kind="WAVE_COMMAND", actor="MANAGER", message_id="m-command-0001",
             wave=WAVE, parent=None, base=BASE, checkpoint=CHECKPOINT, task=TASK,
             issue=1, schema=SCHEMA, created_at="2026-09-23T20:00:00Z", body=None) -> dict:
    return {
        "schema": schema,
        "message_id": message_id,
        "actor": actor,
        "kind": kind,
        "wave": wave,
        "parent": parent,
        "authority": {"issue": issue, "checkpoint": checkpoint, "task": task},
        "base": base,
        "created_at": created_at,
        "body": default_body(kind) if body is None else body,
    }


def default_body(kind: str) -> dict:
    if kind == "WAVE_COMMAND":
        return {
            "branch": "infra/agent-bus-v1",
            "review_boundary": "one Manager review at the end of the wave",
            "units": [unit("U1"), unit("U2", depends_on=["U1"])],
        }
    if kind == "WAVE_PROGRESS":
        return {"unit": "U1", "status": "DONE", "commit": OTHER_SHA}
    if kind == "WAVE_RESULT":
        return {
            "status": "P",
            "branch": "infra/agent-bus-v1",
            "head": OTHER_SHA,
            "units": [{"id": "U1", "status": "DONE"}, {"id": "U2", "status": "DONE"}],
            "validation": ["selftest green"],
            "discrepancies": [],
            "next": "NONE",
        }
    if kind == "WAVE_REVIEW":
        return {"verdict": "ACCEPT", "accepted_head": OTHER_SHA}
    if kind == "CAPTAIN_REQUIRED":
        return {"question": "ratify the wave vocabulary?", "options": ["yes", "no"]}
    if kind == "WAVE_ABORT":
        return {"reason": "superseded by a newer checkpoint"}
    raise AssertionError(f"no default body for {kind}")


def payload(**kwargs) -> str:
    return json.dumps(envelope(**kwargs), indent=2, sort_keys=True)


def comment_body(**kwargs) -> str:
    return "Some human preamble.\n\n```mtj-bus\n" + payload(**kwargs) + "\n```\n"


def raw(comment_id: int, author="MTJawnny", source="issue:1", **kwargs) -> RawComment:
    return RawComment(source=source, comment_id=comment_id, author=author,
                      body=comment_body(**kwargs))


def human(comment_id: int, text="Looks good to me @claude, please take a look.",
          author="MTJawnny") -> RawComment:
    return RawComment(source="issue:1", comment_id=comment_id, author=author, body=text)
