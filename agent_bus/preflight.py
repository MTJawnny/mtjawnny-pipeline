"""Measure the checkout BEFORE any model is invoked.

A Worker brief that says "branch X" is a claim, not a fact. Unattended execution
that trusts the claim will happily do branch X's work in branch Y, against the
wrong base, on top of somebody's uncommitted edits. Every check here is a git
measurement of the machine the wave is about to run on, and every failure stops
the dispatch rather than colouring it a warning.

Problems are COLLECTED, not short-circuited: an operator woken by a failed
preflight should see everything that is wrong, not the first thing.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from agent_bus import errors as E
from agent_bus.errors import BusError
from agent_bus.git_evidence import completed_units
from agent_bus.protocol import Envelope
from agent_bus.shell import Runner
from agent_bus.wave import WavePlan


@dataclass(frozen=True)
class Checkout:
    """What git says about the working tree, as opposed to what anyone claims."""

    root: str
    branch: str
    head: str
    dirty: tuple[str, ...]

    def as_dict(self) -> dict:
        return {"root": self.root, "branch": self.branch, "head": self.head,
                "dirty": list(self.dirty)}


@dataclass(frozen=True)
class PreflightReport:
    ok: bool
    problems: tuple[tuple[str, str], ...]
    checkout: Checkout
    build_base: str

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "problems": [{"code": code, "detail": detail} for code, detail in self.problems],
            "checkout": self.checkout.as_dict(),
            "build_base": self.build_base,
        }


def _git(run: Runner, repo: str, *args: str):
    return run(["git", "-C", repo, *args])


def inspect(repo_path: str, run: Runner | None = None) -> Checkout:
    run = run or Runner()
    top = _git(run, repo_path, "rev-parse", "--show-toplevel")
    if top.returncode != 0:
        raise BusError(E.GIT_FAILED,
                       f"{repo_path} is not a git worktree: {top.stderr.strip()}")
    branch = _git(run, repo_path, "rev-parse", "--abbrev-ref", "HEAD")
    head = _git(run, repo_path, "rev-parse", "HEAD")
    status = _git(run, repo_path, "status", "--porcelain")
    for result in (branch, head, status):
        if result.returncode != 0:
            raise BusError(E.GIT_FAILED,
                           f"git failed in {repo_path}: {result.stderr.strip()}")
    return Checkout(
        root=top.stdout.strip(),
        branch=branch.stdout.strip(),
        head=head.stdout.strip(),
        dirty=tuple(line for line in status.stdout.splitlines() if line.strip()),
    )


def is_ancestor(run: Runner, repo: str, ancestor: str, descendant: str) -> bool:
    result = _git(run, repo, "merge-base", "--is-ancestor", ancestor, descendant)
    return result.returncode == 0


def build_base_of(envelope: Envelope) -> str:
    """The commit the wave actually builds on.

    `envelope.base` anchors AUTHORITY: it must equal the checkpoint's accepted
    head, which is what makes a stale command detectable. A repair wave builds on
    an unaccepted candidate instead, and says so with `candidate_base` -- so the
    two ideas stay separate rather than one quietly standing in for the other.
    """
    if envelope.kind != "WAVE_COMMAND":
        return envelope.base
    return envelope.body.get("candidate_base") or envelope.base


def preflight(envelope: Envelope, plan: WavePlan, expected_repo: str,
              completed_from_bus: Iterable[str] = (),
              run: Runner | None = None) -> PreflightReport:
    """Every mechanical precondition for running this wave here, right now."""
    run = run or Runner()
    checkout = inspect(expected_repo, run)
    base = build_base_of(envelope)
    problems: list[tuple[str, str]] = []

    expected_root = str(Path(expected_repo).expanduser().resolve())
    if str(Path(checkout.root).resolve()) != expected_root:
        problems.append((E.WRONG_WORKTREE,
                         f"git root is {checkout.root}, expected {expected_root}"))

    if checkout.branch != plan.branch:
        problems.append((E.WRONG_BRANCH,
                         f"checked out {checkout.branch}, the wave names {plan.branch}"))

    if not is_ancestor(run, expected_repo, base, checkout.head):
        problems.append((E.BASE_NOT_ANCESTOR,
                         f"{base} is not an ancestor of HEAD {checkout.head}"))
    elif envelope.base != base and not is_ancestor(run, expected_repo, envelope.base, base):
        problems.append((E.BASE_NOT_ANCESTOR,
                         f"accepted head {envelope.base} is not an ancestor of "
                         f"candidate base {base}"))

    if checkout.dirty:
        problems.append((E.UNEXPECTED_DIRT,
                         f"{len(checkout.dirty)} uncommitted path(s): "
                         + "; ".join(checkout.dirty[:5])))

    claimed = sorted(set(completed_from_bus))
    if claimed and not any(p[0] == E.BASE_NOT_ANCESTOR for p in problems):
        in_git = set(completed_units(expected_repo, plan.wave, base, checkout.head, run))
        missing = sorted(set(claimed) - in_git)
        if missing:
            problems.append((
                E.PROGRESS_HEAD_MISMATCH,
                "the bus reports units done that this checkout has no commit for: "
                + ", ".join(missing)))

    return PreflightReport(ok=not problems, problems=tuple(problems),
                           checkout=checkout, build_base=base)
