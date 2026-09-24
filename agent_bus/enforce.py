"""Mechanically check what a unit ACTUALLY did before the next one may run.

`allow_paths`, `deny_paths`, commit boundaries and trailers were instructions in
v1: text handed to a model and hoped for. Unattended execution cannot be built on
hope, so this module re-measures the repository after every unit and refuses to
advance the wave when the measurement disagrees with the authorization.

It never repairs, reverts or cleans. A scope escape is evidence; destroying it to
tidy up would remove the only record of what happened.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Sequence

from agent_bus import errors as E
from agent_bus.git_evidence import UNIT_TRAILER, WAVE_TRAILER, units_in_message
from agent_bus.shell import Runner
from agent_bus.wave import Unit

_REC = "\x1e"
_FIELD = "\x1d"


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Translate one path glob. `**` crosses separators, `*` and `?` do not.

    Written out rather than delegated to `fnmatch`, whose `*` happily crosses `/`
    -- which would make `agent_bus/*` an allowlist for the whole repository.
    """
    out = ["^"]
    index = 0
    while index < len(pattern):
        char = pattern[index]
        if pattern.startswith("**", index):
            out.append(".*")
            index += 2
            continue
        if char == "*":
            out.append("[^/]*")
        elif char == "?":
            out.append("[^/]")
        else:
            out.append(re.escape(char))
        index += 1
    out.append("$")
    return re.compile("".join(out))


def matches_any(path: str, patterns: Iterable[str]) -> bool:
    return any(glob_to_regex(p).match(path) for p in patterns)


def scope_violations(paths: Iterable[str], allow: Sequence[str],
                     deny: Sequence[str] = ()) -> list[str]:
    """Paths that are outside `allow`, or inside `deny`. Deny wins."""
    bad = []
    for path in paths:
        if deny and matches_any(path, deny):
            bad.append(path)
        elif not matches_any(path, allow):
            bad.append(path)
    return sorted(set(bad))


@dataclass(frozen=True)
class Commit:
    sha: str
    message: str


def commits_between(repo: str, base: str, head: str, run: Runner | None = None) -> list[Commit]:
    run = run or Runner()
    result = run(["git", "-C", repo, "log", "--reverse",
                  f"--format=%H{_FIELD}%B{_REC}", f"{base}..{head}"])
    if result.returncode != 0:
        raise RuntimeError(f"git log failed in {repo}: {result.stderr.strip()}")
    out = []
    for chunk in result.stdout.split(_REC):
        if _FIELD not in chunk:
            continue
        sha, message = chunk.split(_FIELD, 1)
        out.append(Commit(sha.strip(), message))
    return out


def changed_paths(repo: str, base: str, head: str, run: Runner | None = None) -> list[str]:
    run = run or Runner()
    result = run(["git", "-C", repo, "diff", "--name-only", "--no-renames", base, head])
    if result.returncode != 0:
        raise RuntimeError(f"git diff failed in {repo}: {result.stderr.strip()}")
    return sorted({line for line in result.stdout.splitlines() if line.strip()})


@dataclass(frozen=True)
class UnitVerdict:
    unit: str
    ok: bool
    problems: tuple[tuple[str, str], ...]
    commits: tuple[str, ...]
    paths: tuple[str, ...]

    def as_dict(self) -> dict:
        return {
            "unit": self.unit,
            "ok": self.ok,
            "problems": [{"code": c, "detail": d} for c, d in self.problems],
            "commits": list(self.commits),
            "paths": list(self.paths),
        }


def verify_unit(repo: str, wave: str, unit: Unit, before: str, after: str,
                dirty: Sequence[str], run: Runner | None = None) -> UnitVerdict:
    """Did this unit stay inside what it was authorized to do?

    Five questions, each its own code:

    * did a mutating unit produce a commit at all;
    * does every commit it produced carry this wave's and this unit's trailers;
    * did anything it changed fall outside `allow_paths`, or inside `deny_paths`;
    * did it leave the tree dirty;
    * did a READ-ONLY unit change anything.
    """
    run = run or Runner()
    commits = commits_between(repo, before, after, run)
    paths = changed_paths(repo, before, after, run) if commits else []
    problems: list[tuple[str, str]] = []

    if not unit.mutating:
        if commits:
            problems.append((E.READONLY_UNIT_MUTATED,
                             f"{unit.id} is not a mutating unit but added "
                             f"{len(commits)} commit(s)"))
        if dirty:
            problems.append((E.READONLY_UNIT_MUTATED,
                             f"{unit.id} is not a mutating unit but left "
                             f"{len(dirty)} uncommitted path(s)"))
        return UnitVerdict(unit.id, not problems, tuple(problems),
                           tuple(c.sha for c in commits), tuple(paths))

    if unit.commit_boundary and not commits:
        problems.append((E.UNIT_NO_COMMIT,
                         f"{unit.id} declares a commit boundary and produced no commit"))

    untrailed = [c.sha for c in commits if unit.id not in units_in_message(c.message, wave)]
    if untrailed:
        problems.append((
            E.UNIT_TRAILER_MISSING,
            f"commit(s) without `{WAVE_TRAILER}: {wave}` and `{UNIT_TRAILER}: {unit.id}`: "
            + ", ".join(sha[:12] for sha in untrailed)))

    escaped = scope_violations(paths, unit.allow_paths, unit.deny_paths)
    if escaped:
        problems.append((E.UNIT_SCOPE_ESCAPE,
                         f"{unit.id} changed paths outside its scope: " + ", ".join(escaped)))

    if dirty:
        problems.append((E.UNIT_UNCOMMITTED,
                         f"{unit.id} left {len(dirty)} uncommitted path(s): "
                         + "; ".join(dirty[:5])))

    return UnitVerdict(unit.id, not problems, tuple(problems),
                       tuple(c.sha for c in commits), tuple(paths))
