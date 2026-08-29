"""In-memory fakes for every external dependency.

These let the whole Manager/Worker state machine run offline, with no network,
no credentials and no model spend. The integration harness in
`tests/test_integration_offline.py` drives complete cycles through them.
"""

from __future__ import annotations

import dataclasses
import itertools
from pathlib import Path
from typing import Callable


@dataclasses.dataclass
class FakeIssue:
    number: int
    title: str
    body: str
    state: str = "OPEN"
    comments: list[dict] = dataclasses.field(default_factory=list)
    labels: list[dict] = dataclasses.field(default_factory=list)


class FakeGitHub:
    """A GitHub that lives in a dict. Records every write for assertions."""

    def __init__(self, issues: list[FakeIssue] | None = None):
        self.issues: dict[int, FakeIssue] = {i.number: i for i in (issues or [])}
        self.prs: dict[int, dict] = {}
        self.writes: list[tuple[str, dict]] = []
        self._issue_counter = itertools.count(max(self.issues, default=0) + 1)
        self._pr_counter = itertools.count(1000)
        self.fail_next_post = False

    # ---- reads -----------------------------------------------------------
    def list_issues(self, state: str = "open") -> list[dict]:
        return [
            {"number": i.number, "title": i.title, "state": i.state,
             "updatedAt": "2026-08-29T00:00:00Z", "labels": i.labels}
            for i in self.issues.values()
            if state == "all" or i.state.lower() == state.lower()
        ]

    def get_issue(self, number: int) -> dict:
        i = self.issues[number]
        return {"number": i.number, "title": i.title, "state": i.state, "body": i.body,
                "updatedAt": "2026-08-29T00:00:00Z", "labels": i.labels,
                "author": {"login": "manager"}}

    def list_comments(self, number: int) -> list[dict]:
        return list(self.issues[number].comments)

    def pr_changed_paths(self, number: int) -> list[str]:
        return list(self.prs.get(number, {}).get("files", []))

    # ---- writes ----------------------------------------------------------
    def post_comment(self, number: int, body: str, idempotency_key: str = "") -> dict:
        if self.fail_next_post:
            self.fail_next_post = False
            raise RuntimeError("simulated GitHub failure mid-cycle")
        if idempotency_key:
            marker = f"<!-- mtj-idem:{idempotency_key} -->"
            if any(marker in (c.get("body") or "") for c in self.issues[number].comments):
                return {"skipped": True, "reason": "idempotent-duplicate"}
            body = f"{body}\n\n{marker}"
        self.issues[number].comments.append({"body": body, "author": {"login": "worker"},
                                             "createdAt": "2026-08-29T00:00:00Z"})
        self.writes.append(("comment", {"issue": number, "body": body}))
        return {"posted": True}

    def create_issue(self, title: str, body: str) -> int:
        number = next(self._issue_counter)
        self.issues[number] = FakeIssue(number=number, title=title, body=body)
        self.writes.append(("issue", {"number": number, "title": title}))
        return number

    def create_draft_pr(self, title: str, body: str, head: str, base: str) -> int:
        number = next(self._pr_counter)
        self.prs[number] = {"title": title, "body": body, "head": head, "base": base,
                            "draft": True, "files": [], "merged": False}
        self.writes.append(("pr", {"number": number, "head": head, "base": base}))
        return number


class FakeClaude:
    """A Claude that runs a python callable instead of a model.

    `behavior(cwd, prompt)` may write files into cwd, exactly as a real Worker
    invocation would, so the wrapper's git lifecycle is exercised for real.
    """

    def __init__(self, behavior: Callable[[Path, str], str] | None = None,
                 is_error: bool = False):
        self.behavior = behavior
        self.is_error = is_error
        self.calls: list[dict] = []

    def run_task(self, prompt: str, cwd, allowed_tools=None) -> dict:
        cwd = Path(cwd)
        text = ""
        if self.behavior:
            text = self.behavior(cwd, prompt) or ""
        session_id = f"fake-session-{len(self.calls)}"
        self.calls.append({"prompt": prompt, "cwd": str(cwd), "session_id": session_id,
                           "allowed_tools": allowed_tools})
        return {"result": text, "is_error": self.is_error, "session_id": session_id,
                "num_turns": 1, "permission_denials": [], "total_cost_usd": 0.0,
                "subtype": "error" if self.is_error else "success"}

    @property
    def session_ids(self) -> list[str]:
        return [c["session_id"] for c in self.calls]


class FakeManagerModel:
    """A Manager model that returns canned mtj-review/1 blocks, in order."""

    def __init__(self, reviews: list[str]):
        self.reviews = list(reviews)
        self.prompts: list[str] = []

    def review(self, prompt: str, schema_hint: str = "") -> str:
        self.prompts.append(prompt)
        if not self.reviews:
            raise AssertionError("FakeManagerModel ran out of canned reviews")
        return self.reviews.pop(0)
