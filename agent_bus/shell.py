"""One injectable subprocess boundary for the whole package.

Every external command -- `gh`, `git`, `claude` -- goes through `Runner`. Tests
substitute a recorded runner, so the state machine, the supervisor and the
transports are all exercised without a network, a token or a model call. A
package whose only test path is "run it against real GitHub" has no negative
controls, because you cannot make real GitHub misbehave on demand.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Callable, Sequence

from agent_bus import errors as E
from agent_bus.errors import BusError


@dataclass(frozen=True)
class Completed:
    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


class Runner:
    """Runs a command for real, and turns a LAUNCH failure into a bus failure.

    This matters more than it looks. A watcher started by launchd inherits a
    minimal PATH; if `gh` is not on it, `subprocess.run` raises FileNotFoundError,
    which is not a `BusError`, which means the poll loop dies, which means
    KeepAlive restarts it, which means a crash loop every ThrottleInterval --
    forever, at full speed, with the backoff schedule never reached because the
    transport was never reached.

    So a command that cannot be launched, or that hangs, is reported in the same
    vocabulary as a command that failed: a `BusError` with a stable code, which
    the loop already knows how to back off from.
    """

    def __call__(self, argv: Sequence[str], stdin: str | None = None,
                 timeout: int | None = 900) -> Completed:
        try:
            proc = subprocess.run(
                list(argv),
                input=stdin,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except FileNotFoundError as exc:
            raise BusError(E.EXECUTABLE_NOT_FOUND,
                           f"{argv[0]!r} is not on PATH for this process "
                           f"({exc.strerror})")
        except PermissionError as exc:
            raise BusError(E.EXECUTABLE_NOT_FOUND,
                           f"{argv[0]!r} cannot be executed ({exc.strerror})")
        except subprocess.TimeoutExpired:
            raise BusError(E.COMMAND_TIMEOUT,
                           f"{argv[0]!r} did not finish within {timeout}s")
        return Completed(tuple(argv), proc.returncode, proc.stdout, proc.stderr)


class RecordedRunner:
    """Answers from a table; records every call. For tests and dry runs."""

    def __init__(self, answers: dict[tuple[str, ...], Completed] | None = None,
                 default: Callable[[Sequence[str]], Completed] | None = None) -> None:
        self.answers = answers or {}
        self.default = default
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, argv: Sequence[str], stdin: str | None = None,
                 timeout: int | None = 900) -> Completed:
        key = tuple(argv)
        self.calls.append(key)
        if key in self.answers:
            return self.answers[key]
        if self.default is not None:
            return self.default(argv)
        raise AssertionError(f"unexpected command in a recorded run: {key}")
