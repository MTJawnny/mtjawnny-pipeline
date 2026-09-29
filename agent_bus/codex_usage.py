"""Codex usage probe: how much of the operator's Codex quota is left, read from Codex itself.

Codex records the account's rate-limit windows in every `token_count` event of a
session rollout (`$CODEX_HOME/sessions/**/rollout-*.jsonl`): the five-hour
window (`primary`) and the weekly window (`secondary`), each a `used_percent`
and a `resets_at` epoch. The limits are the ACCOUNT's, so the newest reading in
any rollout is the current one; a window whose `resets_at` has passed is reported
as reset (0 %), because it has.

Two callers, one reading:

* the host, before it launches Codex at all (`gate`): a Codex that would start
  over the handoff line is not launched -- the pass is a capacity WAIT;
* Codex itself, mid-task, run as a plain script from inside its sandbox
  (stdlib only, no package imports):

      python3 /abs/path/agent_bus/codex_usage.py

  It prints one JSON object, including `session_spent_percent` -- how many
  five-hour points the newest rollout (normally the running session) has used
  since its first reading -- so the model can judge whether the rest of the work
  fits in what is left.

A probe that finds no reading says so (`status: UNKNOWN`); it never invents one.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

# The advice bands, in used-percent of either window. The host refuses to LAUNCH
# at HANDOFF; a running Codex is told to wrap up at WRAP_UP and hand off at HANDOFF.
WRAP_UP = {"five_hour": 75.0, "weekly": 85.0}
HANDOFF = {"five_hour": 90.0, "weekly": 95.0}
# How many newest rollouts to search for a reading.
SEARCH = 20


def codex_home(environ=None) -> Path:
    environ = os.environ if environ is None else environ
    return Path(environ.get("CODEX_HOME") or Path.home() / ".codex").expanduser()


def _rollouts(home: Path) -> list[Path]:
    root = home / "sessions"
    if not root.is_dir():
        return []
    files = [p for p in root.rglob("rollout-*.jsonl") if p.is_file()]
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:SEARCH]


def _readings(path: Path) -> list[dict]:
    """Every rate_limits object in one rollout, oldest first."""
    out = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return out
    for line in lines:
        if '"rate_limits"' not in line:
            continue
        try:
            payload = json.loads(line).get("payload") or {}
        except (ValueError, AttributeError):
            continue
        limits = payload.get("rate_limits") if isinstance(payload, dict) else None
        if isinstance(limits, dict) and isinstance(limits.get("primary"), dict):
            out.append(limits)
    return out


def _window(raw, now: float) -> dict | None:
    if not isinstance(raw, dict) or not isinstance(raw.get("used_percent"), (int, float)):
        return None
    resets = raw.get("resets_at")
    reset = isinstance(resets, (int, float)) and resets <= now
    return {"used_percent": 0.0 if reset else float(raw["used_percent"]),
            "resets_at": resets, "reset_since_reading": reset,
            "window_minutes": raw.get("window_minutes")}


def _band(windows: dict) -> str:
    for name, lines in (("HANDOFF", HANDOFF), ("WRAP_UP", WRAP_UP)):
        if any(w and w["used_percent"] >= lines[key] for key, w in windows.items()):
            return name
    return "CONTINUE"


def read(home: Path | None = None, now: float | None = None) -> dict:
    """The newest reading, its advice band, and what the newest session has spent."""
    home = codex_home() if home is None else home
    now = time.time() if now is None else now
    for path in _rollouts(home):
        readings = _readings(path)
        if not readings:
            continue
        last = readings[-1]
        windows = {"five_hour": _window(last.get("primary"), now),
                   "weekly": _window(last.get("secondary"), now)}
        first = _window(readings[0].get("primary"), now)
        spent = None
        if first and windows["five_hour"] and not windows["five_hour"]["reset_since_reading"]:
            spent = round(windows["five_hour"]["used_percent"] - first["used_percent"], 1)
        return {"status": _band(windows), "windows": windows,
                "session_spent_percent": spent, "rollout": path.name,
                "thresholds": {"wrap_up": WRAP_UP, "handoff": HANDOFF}}
    return {"status": "UNKNOWN", "windows": {}, "session_spent_percent": None,
            "rollout": None, "thresholds": {"wrap_up": WRAP_UP, "handoff": HANDOFF},
            "detail": f"no rate-limit reading in the newest rollouts under {home / 'sessions'}"}


def gate(reading: dict) -> str | None:
    """Why the host must not launch Codex now, or None. Unknown usage does not block."""
    if reading.get("status") != "HANDOFF":
        return None
    parts = [f"{name} {w['used_percent']:.0f}%" for name, w in reading["windows"].items() if w]
    return "codex usage at the handoff line (" + ", ".join(parts) + ")"


def instruction(script: str | Path, handoff: str) -> str:
    """The usage clause appended to every Codex prompt. `handoff` says how to hand off."""
    return (
        "\nUSAGE BUDGET (your Codex quota is small; this clause is part of your task):\n"
        f"  - Probe: `python3 {script}` prints JSON: status CONTINUE / WRAP_UP /\n"
        "    HANDOFF / UNKNOWN, both windows' used_percent, and session_spent_percent\n"
        "    (five-hour points this session has used so far).\n"
        "  - Run it once before you start, then after each major step and at least\n"
        "    every 10 tool calls.\n"
        "  - Each time, decide whether the rest fits: estimate the fraction of the\n"
        "    work still to do; projected = session_spent_percent x remaining / done.\n"
        "    If status is HANDOFF, or status is WRAP_UP and the projection would\n"
        "    cross the handoff line (five-hour 90%, weekly 95%), stop working now.\n"
        f"  - When you stop for usage: {handoff}\n"
        "  - UNKNOWN is not a reason to stop; keep probing.\n"
    )


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv not in ([], ["--gate"]):
        print("usage: codex_usage.py [--gate]", file=sys.stderr)
        return 2
    reading = read()
    print(json.dumps(reading, sort_keys=True))
    return 3 if argv == ["--gate"] and gate(reading) else 0


if __name__ == "__main__":  # pragma: no cover - script entry point
    sys.exit(main())
