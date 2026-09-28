"""One injectable subprocess boundary for the whole package.

Every external command -- `gh`, `git`, `claude` -- goes through `Runner`. Tests
substitute a recorded runner, so the state machine, the supervisor and the
transports are all exercised without a network, a token or a model call. A
package whose only test path is "run it against real GitHub" has no negative
controls, because you cannot make real GitHub misbehave on demand.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from typing import Callable, Sequence

from agent_bus import errors as E
from agent_bus.errors import BusError


# The host runs git over a checkout a model provider has just edited, with the
# host's own credentials. Git reads config from the system file, the user's
# global/XDG file, the repository and any file those include, and several keys
# make git itself execute a program (`core.fsmonitor` on status, `gpg.program`
# on a signed commit, a credential helper on push) or quietly redirect a remote
# (`url.*.insteadOf`, which rewrites the push AND the re-read that proves it).
# The repository's own config is snapshotted and compared by the host; the
# system and global files are outside the checkout, where a provider with broad
# filesystem rights could still write them. So host git never reads them, and
# the keys that execute or redirect are pinned last, at command-line precedence,
# above anything the repository says.
HOST_GIT_CONFIG = (
    ("core.fsmonitor", "false"),
    ("core.hooksPath", os.devnull),
    ("commit.gpgsign", "false"),
    ("tag.gpgsign", "false"),
    ("protocol.ext.allow", "never"),
    ("credential.helper", ""),
    ("credential.helper", "!gh auth git-credential"),
)


def host_git_env(inherited: dict[str, str] | None = None) -> dict[str, str]:
    """The only environment host git runs in: no ambient GIT_*, no system or
    global config, no prompt, and HOST_GIT_CONFIG pinned via GIT_CONFIG_COUNT."""
    base = os.environ if inherited is None else inherited
    env = {key: value for key, value in base.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_TERMINAL_PROMPT="0", GIT_CONFIG_COUNT=str(len(HOST_GIT_CONFIG)))
    for index, (key, value) in enumerate(HOST_GIT_CONFIG):
        env[f"GIT_CONFIG_KEY_{index}"] = key
        env[f"GIT_CONFIG_VALUE_{index}"] = value
    return env


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

    Every `git` it runs runs in `host_git_env()`; no call site can forget to.
    """

    def __call__(self, argv: Sequence[str], stdin: str | None = None,
                 timeout: int | None = 900) -> Completed:
        try:
            proc = subprocess.run(
                list(argv),
                input=stdin,
                env=host_git_env() if argv[0] == "git" else None,
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
