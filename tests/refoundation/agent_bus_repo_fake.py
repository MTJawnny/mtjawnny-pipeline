"""A small, faithful model of a git checkout, for exercising unattended execution.

It is a MODEL, not a stub: commits are ordered, ranges are real ranges, and a
diff over `before..after` returns what those commits actually touched. Tests that
assert scope escapes and trailer failures are worthless against a fake that
answers whatever was expected of it, so this one is driven by a script of what
each unit DID and then queried exactly like git is queried.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from agent_bus.shell import Completed

REC = "\x1e"
FIELD = "\x1d"


@dataclass
class Effect:
    """What one Claude invocation did to the checkout."""

    message: str | None = None          # None means "produced no commit"
    paths: tuple[str, ...] = ()
    dirty: tuple[str, ...] = ()
    fail: str | None = None             # stderr of a failing `claude`


@dataclass
class FakeRepo:
    comments: list[dict]
    script: list[Effect] = field(default_factory=list)
    toplevel: str = "/tmp/repo"
    branch: str = "infra/agent-bus-v1"
    base: str = "0" * 40
    ancestor: bool = True

    def __post_init__(self) -> None:
        self.commits: list[tuple[str, str, tuple[str, ...]]] = []
        self.dirty: tuple[str, ...] = ()
        self.calls: list[tuple[str, ...]] = []
        self.posted: list[str] = []
        self._next = 0

    # -------------------------------------------------------------- git model
    @property
    def head(self) -> str:
        return self.commits[-1][0] if self.commits else self.base

    def _index(self, sha: str) -> int:
        for position, (commit_sha, _, _) in enumerate(self.commits):
            if commit_sha == sha:
                return position
        return -1

    def _range(self, before: str, after: str):
        start = self._index(before) + 1
        end = self._index(after) + 1
        return self.commits[start:end]

    def _commit(self, effect: Effect) -> None:
        sha = f"{len(self.commits) + 1:040x}"
        self.commits.append((sha, effect.message or "", tuple(effect.paths)))

    # ------------------------------------------------------------ the boundary
    def __call__(self, argv, stdin=None, timeout=None) -> Completed:
        argv = tuple(argv)
        self.calls.append(argv)
        if argv[0] == "gh":
            if any(a.startswith("body=") for a in argv):
                self.posted.append(next(a[5:] for a in argv if a.startswith("body=")))
                return Completed(argv, 0, '{"id": 1}', "")
            return Completed(argv, 0, json.dumps(self.comments), "")
        if argv[0] == "claude":
            return self._claude(argv)
        if argv[0] == "git":
            return self._git(argv)
        raise AssertionError(f"unexpected command {argv}")

    def _claude(self, argv) -> Completed:
        effect = self.script[self._next] if self._next < len(self.script) else Effect()
        self._next += 1
        if effect.fail:
            return Completed(argv, 1, "", effect.fail)
        if effect.message is not None:
            self._commit(effect)
        self.dirty = tuple(effect.dirty)
        return Completed(argv, 0, '{"subtype": "success"}', "")

    def _git(self, argv) -> Completed:
        if "--show-toplevel" in argv:
            return Completed(argv, 0, str(Path(self.toplevel).resolve()) + "\n", "")
        if "--abbrev-ref" in argv:
            return Completed(argv, 0, self.branch + "\n", "")
        if "merge-base" in argv:
            return Completed(argv, 0 if self.ancestor else 1, "", "")
        if "rev-parse" in argv:
            return Completed(argv, 0, self.head + "\n", "")
        if "status" in argv:
            return Completed(argv, 0, "".join(f" M {p}\n" for p in self.dirty), "")
        if "log" in argv:
            fmt = next(a for a in argv if a.startswith("--format="))
            before, after = argv[-1].split("..")
            rows = self._range(before, after)
            if fmt == f"--format=%B{REC}":
                return Completed(argv, 0, "".join(f"{m}{REC}" for _, m, _ in rows), "")
            return Completed(argv, 0,
                             "".join(f"{s}{FIELD}{m}{REC}" for s, m, _ in rows), "")
        if "diff" in argv:
            before, after = argv[-2], argv[-1]
            paths: set[str] = set()
            for _, _, changed in self._range(before, after):
                paths.update(changed)
            return Completed(argv, 0, "\n".join(sorted(paths)) + "\n", "")
        raise AssertionError(f"unexpected git command {argv}")

    # --------------------------------------------------------------- helpers
    @property
    def claude_calls(self):
        return [c for c in self.calls if c[0] == "claude"]

    def posted_kinds(self) -> list[str]:
        from agent_bus.protocol import parse_comment
        return [parse_comment(body).kind for body in self.posted]

    def posted_messages(self):
        from agent_bus.protocol import parse_comment
        return [parse_comment(body) for body in self.posted]
