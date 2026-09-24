"""The durable local Worker: a polling watcher, and the macOS service around it.

`poll --execute` is one shot. A Worker that only exists while somebody is typing
is not a wake mechanism, so this module adds the smallest thing that can sit on
an operator's machine for days without becoming a hazard:

* **one instance, ever.** An exclusive lock outside the repository; a second
  process refuses rather than racing the first for the same wave.
* **no hot loop.** Every cycle sleeps, successes included. Failures back off
  exponentially to a cap, and a quota or rate-limit refusal backs off on its own
  much longer schedule, because retrying a quota wall every minute is how an
  account gets itself throttled for a day.
* **clean shutdown.** A signal sets a flag; the current cycle finishes and the
  loop returns its log. Nothing is killed mid-commit.
* **nothing hidden.** Every cycle is a record: what was seen, what was done, how
  long the next sleep is and why.

Time and randomness are injected, so the backoff schedule is asserted in tests
rather than waited for. The service files live under the operator's own
`~/Library/LaunchAgents` and `~/.local/state`; nothing here reads or writes
`~/.claude`.
"""

from __future__ import annotations

import fcntl
import json
import os
import re
import shutil
import signal
import sys
import time
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Mapping, Sequence

from agent_bus import errors as E
from agent_bus.errors import BusError
from agent_bus.issue import AuthorityError
from agent_bus.shell import Runner

LABEL = "com.mtjawnny.agent-bus"
STATE_DIR = Path("~/.local/state/mtj-agent-bus")
LAUNCH_AGENTS = Path("~/Library/LaunchAgents")

# Signals that a retry should wait a long time rather than a short one. Matched
# against the transport's own error text, which is the only place the CLI reports
# them; a wrong guess here costs a longer sleep, never a lost failure.
QUOTA_RE = re.compile(r"(?i)(quota|rate[ _-]?limit|usage limit|429|too many requests|overloaded)")

# What launchd gives a user agent when the plist says nothing. Measured with
# `launchctl getenv PATH`, which is unset -- so this built-in default applies.
LAUNCHD_DEFAULT_PATH = ("/usr/bin", "/bin", "/usr/sbin", "/sbin")

# The executables this package shells out to, and where. They are NAMED here
# rather than located here: the directories come from resolving these names on
# the machine being installed to, so nothing hardcodes one operator's Homebrew.
BASE_EXECUTABLES = ("git", "gh")        # agent_bus.git_evidence, agent_bus.issue
EXECUTE_EXECUTABLES = ("claude",)       # agent_bus.transport, only when arming


def required_executables(program_args: Sequence[str]) -> tuple[str, ...]:
    """`git` and `gh` always; `claude` too when the service may actually run waves.

    A watcher installed without `--execute` never invokes a model, so demanding
    `claude` from it would fail an installation that would have worked.
    """
    names = list(BASE_EXECUTABLES)
    if "--execute" in tuple(program_args):
        names += list(EXECUTE_EXECUTABLES)
    return tuple(names)


def resolve_executables(names: Sequence[str],
                        which: Callable[[str], str | None] = shutil.which
                        ) -> dict[str, str]:
    """Locate every required executable, or refuse loudly naming all of them.

    Loudly, and BEFORE installation. An agent that installs cleanly and then
    cannot find `gh` is indistinguishable, from the outside, from one that is
    running -- launchd will keep restarting it and `launchctl print` will keep
    saying it started.
    """
    found: dict[str, str] = {}
    missing: list[str] = []
    for name in names:
        location = which(name)
        if location:
            found[name] = location
        else:
            missing.append(name)
    if missing:
        raise BusError(
            E.EXECUTABLE_NOT_FOUND,
            "cannot resolve required executable(s) for the service: "
            + ", ".join(missing)
            + " -- install them, or put them on PATH before installing the agent")
    return found


def service_path(resolved: Mapping[str, str],
                 defaults: Sequence[str] = LAUNCHD_DEFAULT_PATH) -> str:
    """The PATH the agent runs with: where the tools actually are, then the defaults.

    Order is the declared order of the executables, then the system defaults,
    each added once. Derived from measurement, so the same call on a machine
    where `gh` lives in /usr/local/bin produces /usr/local/bin.
    """
    directories: list[str] = []
    for name in resolved:
        directory = str(Path(resolved[name]).parent)
        if directory not in directories:
            directories.append(directory)
    for directory in defaults:
        if directory not in directories:
            directories.append(directory)
    return ":".join(directories)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stdout_line(entry: dict) -> None:
    """One JSON line per cycle, flushed.

    Flushed because launchd redirects stdout to a file, Python block-buffers a
    file, and a long-running watcher would otherwise write its first log line
    when it exits -- which for a healthy watcher is never.
    """
    sys.stdout.write(json.dumps(entry, sort_keys=True) + "\n")
    sys.stdout.flush()


@dataclass(frozen=True)
class Backoff:
    """A pure schedule. `delay(n)` is a function of the failure count, nothing else."""

    base: float = 60.0
    factor: float = 2.0
    cap: float = 3600.0
    quota_base: float = 900.0
    quota_cap: float = 21600.0

    def delay(self, failures: int, quota: bool = False) -> float:
        if failures < 1:
            raise BusError(E.BAD_VALUE, "a backoff delay needs at least one failure")
        base, cap = (self.quota_base, self.quota_cap) if quota else (self.base, self.cap)
        return min(cap, base * (self.factor ** (failures - 1)))


class SingleInstance:
    """An exclusive advisory lock held for the life of the process.

    `flock` is used rather than a pid file because a pid file survives a kill -9
    and then locks the watcher out of its own machine forever. A lock the kernel
    releases cannot leak that way.
    """

    def __init__(self, path: Path):
        self.path = Path(path).expanduser()
        self._fd: int | None = None

    def acquire(self) -> "SingleInstance":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            os.close(fd)
            raise BusError(E.WATCHER_ALREADY_RUNNING,
                           f"another watcher holds {self.path}")
        os.ftruncate(fd, 0)
        os.write(fd, f"{os.getpid()}\n".encode())
        self._fd = fd
        return self

    def release(self) -> None:
        if self._fd is not None:
            fcntl.flock(self._fd, fcntl.LOCK_UN)
            os.close(self._fd)
            self._fd = None

    def __enter__(self) -> "SingleInstance":
        return self.acquire()

    def __exit__(self, *_) -> None:
        self.release()


def lock_path_for(repo_path: str) -> Path:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", str(Path(repo_path).expanduser().resolve())).strip("-")
    return STATE_DIR.expanduser() / f"{slug}.lock"


@dataclass
class Watcher:
    """The loop. It owns no policy beyond when to look again."""

    supervisor: object
    interval: float = 120.0
    backoff: Backoff = field(default_factory=Backoff)
    lock: SingleInstance | None = None
    sleep: Callable[[float], None] = time.sleep
    floor: float = 15.0
    # One record per cycle, written AS THE CYCLE COMPLETES. The returned log is
    # for callers that end the loop; the emitter is for the ones that never do.
    emit: Callable[[dict], None] = _stdout_line
    clock: Callable[[], str] = _utc_now

    def __post_init__(self) -> None:
        self._stop = False
        if self.interval < self.floor:
            raise BusError(E.BAD_VALUE,
                           f"poll interval {self.interval}s is below the {self.floor}s floor")

    def request_stop(self, *_) -> None:
        self._stop = True

    def install_signal_handlers(self) -> None:
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self.request_stop)

    def run(self, cycles: int | None = None, execute: bool = False) -> list[dict]:
        """Poll until asked to stop, or for a bounded number of cycles.

        `cycles` exists so the loop can be exercised. It is not a schedule: the
        sleep after every cycle happens either way, successes included, because a
        loop that only sleeps after failures is a hot loop with good manners.
        """
        log: list[dict] = []
        failures = 0
        held = self.lock.acquire() if self.lock else None
        try:
            count = 0
            while not self._stop and (cycles is None or count < cycles):
                count += 1
                entry: dict = {"cycle": count, "at": self.clock()}
                try:
                    report = self.supervisor.poll_once(execute=execute)
                    entry["action"] = report.get("action")
                    entry["reason"] = report.get("reason")
                    entry["selected"] = report.get("selected")
                    failures = 0
                    delay = max(self.interval, self.floor)
                    entry["outcome"] = "polled"
                # AuthorityError is caught alongside BusError on purpose. GitHub
                # being unreachable is an expected condition of a service that
                # runs for days, not a bug -- and left uncaught it would kill the
                # loop and hand the restart to KeepAlive, which is the crash loop
                # this repair exists to remove.
                except (BusError, AuthorityError) as exc:
                    failures += 1
                    code = getattr(exc, "code", E.AUTHORITY_UNRESOLVED)
                    detail = getattr(exc, "detail", str(exc))
                    quota = bool(QUOTA_RE.search(detail))
                    delay = self.backoff.delay(failures, quota)
                    entry.update({"outcome": "failed", "code": code, "detail": detail,
                                  "quota": quota, "failures": failures})
                entry["sleep"] = delay
                log.append(entry)
                # Emitted BEFORE the sleep. A record that appears only after the
                # wait is a record of what the watcher WAS doing two minutes ago.
                self.emit(entry)
                if self._stop or (cycles is not None and count >= cycles):
                    break
                self.sleep(delay)
        finally:
            if held is not None:
                held.release()
        return log


# ---------------------------------------------------------------------------
# macOS service surfaces. Every one of them is dry-run by default.
# ---------------------------------------------------------------------------


def plist_path(label: str = LABEL) -> Path:
    return LAUNCH_AGENTS.expanduser() / f"{label}.plist"


def plist(program_args: Sequence[str], label: str = LABEL,
          workdir: str = ".", environment: dict[str, str] | None = None) -> str:
    """A launchd agent that restarts the watcher and throttles its own restarts."""
    state = STATE_DIR.expanduser()
    env = "".join(
        f"\n      <key>{k}</key>\n      <string>{v}</string>"
        for k, v in sorted((environment or {}).items()))
    args = "".join(f"\n      <string>{a}</string>" for a in program_args)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>{label}</string>
    <key>ProgramArguments</key>
    <array>{args}
    </array>
    <key>WorkingDirectory</key>
    <string>{workdir}</string>
    <key>EnvironmentVariables</key>
    <dict>{env}
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>ThrottleInterval</key>
    <integer>60</integer>
    <key>StandardOutPath</key>
    <string>{state}/watcher.out.log</string>
    <key>StandardErrorPath</key>
    <string>{state}/watcher.err.log</string>
  </dict>
</plist>
"""


def _domain() -> str:
    return f"gui/{os.getuid()}"


def install(program_args: Sequence[str], label: str = LABEL, workdir: str = ".",
            environment: dict[str, str] | None = None, run: Runner | None = None,
            dry_run: bool = True,
            which: Callable[[str], str | None] = shutil.which) -> dict:
    """Write and load the agent -- after proving it could actually run.

    Resolution happens FIRST, and on a dry run too. The point of the dry run is
    to find out that this machine cannot host the service before the service is
    installed, not after.

    PATH is DERIVED, and derivation wins: a caller may add variables through
    `environment`, but not replace the one thing that decides whether the agent
    can find its own tools.
    """
    resolved = resolve_executables(required_executables(program_args), which)
    env = dict(environment or {})
    env["PATH"] = service_path(resolved)
    path = plist_path(label)
    document = plist(program_args, label, workdir, env)
    plan = {"action": "install", "label": label, "plist": str(path),
            "launchctl": ["launchctl", "bootstrap", _domain(), str(path)],
            "executables": resolved, "path": env["PATH"], "dry_run": dry_run}
    if dry_run:
        plan["document"] = document
        return plan
    path.parent.mkdir(parents=True, exist_ok=True)
    STATE_DIR.expanduser().mkdir(parents=True, exist_ok=True)
    path.write_text(document, encoding="utf-8")  # only reached when dry_run is False
    result = (run or Runner())(plan["launchctl"])
    plan["returncode"] = result.returncode
    plan["stderr"] = result.stderr.strip()
    return plan


def uninstall(label: str = LABEL, run: Runner | None = None, dry_run: bool = True) -> dict:
    path = plist_path(label)
    plan = {"action": "uninstall", "label": label, "plist": str(path),
            "launchctl": ["launchctl", "bootout", f"{_domain()}/{label}"],
            "dry_run": dry_run}
    if dry_run:
        return plan
    result = (run or Runner())(plan["launchctl"])
    plan["returncode"] = result.returncode
    plan["stderr"] = result.stderr.strip()
    if path.is_file():
        path.unlink()
        plan["removed"] = True
    return plan


def service_control(action: str, label: str = LABEL, run: Runner | None = None,
                    dry_run: bool = True) -> dict:
    """`start` and `stop` in launchd's own vocabulary."""
    verb = {"start": "kickstart", "stop": "kill"}[action]
    target = f"{_domain()}/{label}"
    argv = (["launchctl", "kickstart", "-k", target] if verb == "kickstart"
            else ["launchctl", "kill", "SIGTERM", target])
    plan = {"action": action, "label": label, "launchctl": argv, "dry_run": dry_run}
    if dry_run:
        return plan
    result = (run or Runner())(argv)
    plan["returncode"] = result.returncode
    plan["stderr"] = result.stderr.strip()
    return plan


def status(repo_path: str, label: str = LABEL, run: Runner | None = None) -> dict:
    """What is actually on this machine: the plist, the lock, and launchd's view."""
    path = plist_path(label)
    lock = lock_path_for(repo_path)
    out: dict = {"label": label, "plist": str(path), "plist_installed": path.is_file(),
                 "lock": str(lock), "lock_present": lock.expanduser().is_file()}
    result = (run or Runner())(["launchctl", "print", f"{_domain()}/{label}"])
    out["loaded"] = result.returncode == 0
    out["state"] = _launchctl_state(result.stdout) if out["loaded"] else None
    return out


def _launchctl_state(text: str) -> str | None:
    match = re.search(r"^\s*state\s*=\s*(\S+)", text, re.MULTILINE)
    return match.group(1) if match else None
