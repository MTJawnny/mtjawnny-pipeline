"""Durable, non-repudiable unit completion: git commit trailers.

A wave that records its progress only in comments is one lost comment away from
lying about what was built. A commit trailer is attached to the mutation itself:

    Agent-Bus-Wave: INFRA.AGENT-BUS-V1.W1
    Agent-Bus-Unit: U2-PROTOCOL

So resume arithmetic can be re-derived from the branch alone, with no session,
no ledger and no network. Comments remain the fast path; git is the proof.
"""

from __future__ import annotations

import re
from typing import Sequence

from agent_bus import errors as E
from agent_bus.errors import BusError
from agent_bus.shell import Runner

WAVE_TRAILER = "Agent-Bus-Wave"
UNIT_TRAILER = "Agent-Bus-Unit"
_TRAILER_RE = re.compile(r"^(?P<key>Agent-Bus-(?:Wave|Unit)):[ \t]*(?P<value>\S+)[ \t]*$",
                         re.MULTILINE)
_SEP = "\x1e"


def trailers(wave: str, unit: str) -> str:
    """The exact two lines a unit's commit message ends with."""
    return f"{WAVE_TRAILER}: {wave}\n{UNIT_TRAILER}: {unit}"


def units_in_message(message: str, wave: str) -> list[str]:
    """Units this one commit message claims for `wave`, in order of appearance."""
    found = _TRAILER_RE.findall(message)
    waves = [v for k, v in found if k == WAVE_TRAILER]
    units = [v for k, v in found if k == UNIT_TRAILER]
    if wave not in waves:
        return []
    return units


def completed_units(repo: str, wave: str, base: str, head: str = "HEAD",
                    run: Runner | None = None) -> list[str]:
    """Units committed on `base..head`, deduplicated, in commit order.

    `base` is the accepted head the wave was authorized against, so this reads
    exactly the commits the wave itself added and never inherits a claim from
    history before it.
    """
    run = run or Runner()
    result = run(["git", "-C", repo, "log", "--reverse", f"--format=%B{_SEP}",
                  f"{base}..{head}"])
    if result.returncode != 0:
        raise BusError(E.GIT_FAILED, f"git log failed in {repo}: {result.stderr.strip()}")
    seen: list[str] = []
    for message in result.stdout.split(_SEP):
        for unit in units_in_message(message, wave):
            if unit not in seen:
                seen.append(unit)
    return seen


def head_sha(repo: str, run: Runner | None = None) -> str:
    run = run or Runner()
    result = run(["git", "-C", repo, "rev-parse", "HEAD"])
    if result.returncode != 0:
        raise BusError(E.GIT_FAILED, f"git rev-parse failed in {repo}: {result.stderr.strip()}")
    return result.stdout.strip()


def branch(repo: str, run: Runner | None = None) -> str:
    run = run or Runner()
    result = run(["git", "-C", repo, "rev-parse", "--abbrev-ref", "HEAD"])
    if result.returncode != 0:
        raise BusError(E.GIT_FAILED, f"git rev-parse failed in {repo}: {result.stderr.strip()}")
    return result.stdout.strip()


def dirty(repo: str, run: Runner | None = None) -> Sequence[str]:
    run = run or Runner()
    result = run(["git", "-C", repo, "status", "--short"])
    if result.returncode != 0:
        raise BusError(E.GIT_FAILED, f"git status failed in {repo}: {result.stderr.strip()}")
    return [line for line in result.stdout.splitlines() if line.strip()]
