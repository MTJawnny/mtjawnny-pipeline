"""Who is allowed to speak on the bus. Fail closed, and configured off-repository.

The repository is PUBLIC. Anyone can open a pull request and leave a comment, so
"is this comment well-formed and current?" is not the same question as "may this
person command a Worker". v1 answered only the first, and an empty trust set meant
everybody -- the wrong direction for a default.

Two rules follow.

**Fail closed.** No configured speaker means NO speaker. An unconfigured bus reads
nothing and runs nothing, and says exactly how to configure itself.

**Off-repository.** Trust is operator configuration, never repository data. A wave
executing inside the checkout can edit files in the checkout; if the trust list
lived there, a single scope escape would rewrite who is allowed to command the
next one. The supervisor therefore reads it from the command line, the
environment, or a file outside the working tree -- in that order, first non-empty
wins, every source explicit.

**The publisher is not a speaker.** The Manager wake workflow posts as the
repository's own GitHub Actions identity. That identity is NOT added to the
speaker set, because every workflow in the repository shares it: identity alone
proves only "some workflow here wrote this". It is instead trusted for exact
ROLES -- `PUBLISHER_ROLES` below -- and within a role, only for a record that is
exactly what the deterministic publisher would have written from Captain-rooted
inputs (`agent_bus.transition`). Anything else it posts is refused and reported,
the same as a stranger's comment. Configuring it as a speaker is an error.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from agent_bus import errors as E
from agent_bus.errors import BusError

PUBLISHER = "github-actions[bot]"

# The whole of the publisher's authority, as data. A surface maps to the record
# shapes the publisher may write there: (actor, kind) bus envelopes on the
# transport pull request, ledger schemas on the authority issue. It may never
# write a WORKER or CAPTAIN message, an abort, a task, or a Captain decision.
PUBLISHER_ROLES = {
    "transport": frozenset({("MANAGER", "WAVE_REVIEW"), ("MANAGER", "WAVE_COMMAND")}),
    "ledger": frozenset({"mtj-verdict", "mtj-checkpoint"}),
}

ENV_VAR = "MTJ_AGENT_BUS_TRUSTED"
CONFIG_ENV_VAR = "MTJ_AGENT_BUS_CONFIG"
DEFAULT_CONFIG = Path("~/.config/mtj-agent-bus/trust.json")

HOW_TO_CONFIGURE = (
    "declare trusted bus speakers with --trusted <login>[,<login>...], "
    f"the {ENV_VAR} environment variable, or a JSON file at "
    f"{DEFAULT_CONFIG} (or {CONFIG_ENV_VAR}) of the form "
    '{"speakers": ["<login>"]}'
)


@dataclass(frozen=True)
class Trust:
    """A resolved speaker set and, for the record, where it came from."""

    speakers: frozenset[str]
    source: str
    publisher: str | None = PUBLISHER

    def __post_init__(self) -> None:
        if self.publisher is not None and self.publisher.lower() in self.speakers:
            raise BusError(E.TRUST_NOT_CONFIGURED,
                           f"{self.publisher} is the publisher, trusted for exact roles "
                           "only; it cannot be declared a speaker")

    def trusts(self, login: str) -> bool:
        """A SPEAKER: may say anything its actor may say. Humans only."""
        return login.lower() in self.speakers

    def is_publisher(self, login: str) -> bool:
        """The machine identity. Exact login, never case-folded, never a speaker."""
        return self.publisher is not None and login == self.publisher

    @property
    def configured(self) -> bool:
        return bool(self.speakers)

    def require(self) -> "Trust":
        """Raise unless somebody is trusted. Every live path calls this."""
        if not self.speakers:
            raise BusError(E.TRUST_NOT_CONFIGURED, HOW_TO_CONFIGURE)
        return self

    def as_dict(self) -> dict:
        return {"speakers": sorted(self.speakers), "source": self.source,
                "configured": self.configured}


def _clean(values: Iterable[str]) -> frozenset[str]:
    return frozenset(v.strip().lower() for v in values if v and v.strip())


NOBODY = Trust(frozenset(), "unconfigured")


def from_flag(value: str | None) -> Trust | None:
    if not value:
        return None
    speakers = _clean(value.split(","))
    return Trust(speakers, "--trusted") if speakers else None


def from_env(environ: dict[str, str] | None = None) -> Trust | None:
    environ = os.environ if environ is None else environ
    speakers = _clean((environ.get(ENV_VAR) or "").split(","))
    return Trust(speakers, ENV_VAR) if speakers else None


def from_file(path: Path | None = None, environ: dict[str, str] | None = None) -> Trust | None:
    environ = os.environ if environ is None else environ
    if path is None:
        configured = environ.get(CONFIG_ENV_VAR)
        path = Path(configured) if configured else DEFAULT_CONFIG
    path = path.expanduser()
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        # A trust file that cannot be read is not an empty trust file. Halting
        # loudly is the whole point: silently falling back to "nobody" would look
        # identical to a correctly locked-down bus.
        raise BusError(E.TRUST_NOT_CONFIGURED, f"{path} is not valid JSON: {exc.msg}")
    if not isinstance(payload, dict) or not isinstance(payload.get("speakers"), list):
        raise BusError(E.TRUST_NOT_CONFIGURED,
                       f'{path} must be an object with a "speakers" list')
    speakers = _clean(payload["speakers"])
    return Trust(speakers, str(path)) if speakers else None


def resolve(flag: str | None = None, environ: dict[str, str] | None = None,
            path: Path | None = None) -> Trust:
    """First non-empty source wins: flag, then environment, then file.

    Returns `NOBODY` when nothing is configured. It is deliberately NOT an error
    to resolve to nobody -- it is an error to ACT on it, which is `require()`,
    so a status command can still report an unconfigured bus instead of crashing.
    """
    for candidate in (from_flag(flag), from_env(environ), from_file(path, environ)):
        if candidate is not None and candidate.configured:
            return candidate
    return NOBODY
