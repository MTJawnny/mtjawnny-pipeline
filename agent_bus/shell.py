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


@dataclass(frozen=True)
class Completed:
    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


class Runner:
    """Runs a command for real."""

    def __call__(self, argv: Sequence[str], stdin: str | None = None,
                 timeout: int | None = 900) -> Completed:
        proc = subprocess.run(
            list(argv),
            input=stdin,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
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
