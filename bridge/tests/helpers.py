"""Shared fixtures: a real local git origin so offline tests exercise real git."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

BOOTSTRAP_BRANCH = "bootstrap-test"


def _git(args, cwd, check=True):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True,
                          check=check)


def make_repo() -> tuple[Path, Path, str]:
    """Create a bare origin + a working clone containing a refoundation/ control plane.

    Returns (work_dir, origin_dir, base_sha).
    """
    root = Path(tempfile.mkdtemp(prefix="mtj-bridge-test-"))
    origin = root / "origin.git"
    work = root / "work"
    _git(["init", "--bare", "-b", BOOTSTRAP_BRANCH, str(origin)], root)
    _git(["init", "-b", BOOTSTRAP_BRANCH, str(work)], root)
    _git(["config", "user.email", "test@example.invalid"], work)
    _git(["config", "user.name", "bridge-test"], work)
    _git(["config", "commit.gpgsign", "false"], work)

    (work / "refoundation").mkdir()
    (work / "refoundation" / "BOOTSTRAP-STATE.yaml").write_text(
        "schema: mtj-refoundation-bootstrap-state/1\nstatus: ACTIVE\n")
    (work / "refoundation" / "CAPTAIN-DIRECTION.md").write_text("# CAPTAIN DIRECTION\n")
    (work / "refoundation" / "SESSION-PROTOCOL.md").write_text("# PROTOCOL\n")
    (work / "refoundation" / "WORKER-START.md").write_text("# WORKER START\n")
    (work / "src").mkdir()
    (work / "src" / "thing.py").write_text("VALUE = 1\n")
    (work / "docs").mkdir()
    (work / "docs" / "RATIFIED-RULINGS-REGISTRY.md").write_text("# registry\n")

    _git(["add", "-A"], work)
    _git(["commit", "-m", "base"], work)
    _git(["remote", "add", "origin", str(origin)], work)
    _git(["push", "-u", "origin", BOOTSTRAP_BRANCH], work)
    sha = _git(["rev-parse", "HEAD"], work).stdout.strip()
    return work, origin, sha


def task_body(task_id="TEST.TASK", base="0" * 40, base_branch=BOOTSTRAP_BRANCH,
              status="READY", kind="infrastructure_only",
              allow=("src/**",), deny=("docs/**",), validation=()) -> str:
    """Build an mtj-task/1 body. Empty allow/deny omit the key entirely, which is
    how a real task that supplies no machine-readable scope actually looks."""
    lines = [
        "```yaml",
        "schema: mtj-task/1",
        f"task: {task_id}",
        f"base_branch: {base_branch}",
        f"base: {base}",
        f"status: {status}",
        "objective:",
        "  - do the thing",
        "scope:",
        f"  kind: {kind}",
    ]
    if allow:
        lines += ["  allow_paths:", *[f"    - {a}" for a in allow]]
    if deny:
        lines += ["  deny_paths:", *[f"    - {d}" for d in deny]]
    if validation:
        lines += ["validation:", "  commands:", *[f"    - {c}" for c in validation]]
    lines += [
        "prohibited:",
        "  - modifying main",
        "stop:",
        "  - bootstrap base differs",
        "next:",
        "  authorized: NONE",
        "```",
    ]
    return "\n".join(lines)


def result_body(task_id="TEST.TASK", status="COMPLETE", base_expected="0" * 40,
                base_measured=None, mutations=("src/thing.py",), pr=1000,
                discrepancies=("NONE",), decision=("NONE",)) -> str:
    base_measured = base_measured if base_measured is not None else base_expected
    lines = [
        "```yaml",
        "schema: mtj-result/1",
        f"task: {task_id}",
        f"status: {status}",
        f"base_expected: {base_expected}",
        f"base_measured: {base_measured}",
        "branch: mtj/test",
        f"pr: {pr}",
        "mutations:",
        *[f"  - {m}" for m in mutations],
        "validation:",
        "  - tests passed",
        "discrepancies:",
        *[f"  - {d}" for d in discrepancies],
        "decision_required:",
        *[f"  - {d}" for d in decision],
        "next:",
        "  authorized: NONE",
        "```",
    ]
    return "\n".join(lines)


def review_body(task_id="TEST.TASK", verdict="PASS", reasons=("looks correct",),
                findings=("NONE",), captain=(), next_id="") -> str:
    lines = [
        "```yaml",
        "schema: mtj-review/1",
        f"task: {task_id}",
        f"verdict: {verdict}",
        "reasons:",
        *[f"  - {r}" for r in reasons],
        "findings:",
        *[f"  - {f}" for f in findings],
    ]
    if captain:
        lines += ["captain_question:", *[f"  - {c}" for c in captain]]
    if next_id:
        lines += ["next_task:", f"  id: {next_id}"]
    lines.append("```")
    return "\n".join(lines)
