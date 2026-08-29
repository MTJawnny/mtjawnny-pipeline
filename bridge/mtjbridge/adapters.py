"""Adapter interfaces + real implementations for GitHub, git, Claude and OpenAI.

Every outbound effect in the bridge goes through one of these objects, and every
one of them is substitutable, so the offline harness can run a complete
Manager/Worker cycle with no network, no credentials and no model spend.

Credential rule: this module never reads, prints, stores or forwards a token.
`gh` uses its own keyring auth, `claude` uses its own auth, and the OpenAI SDK
reads OPENAI_API_KEY itself. The bridge only ever observes whether auth works.
"""

from __future__ import annotations

import dataclasses
import json
import os
import shlex
import subprocess
import uuid
from pathlib import Path
from typing import Any, Protocol

from .logging_setup import get_logger
from .redact import redact

log = get_logger(__name__)

DEFAULT_MANAGER_MODEL = os.environ.get("MTJ_MANAGER_MODEL", "gpt-5.6-sol")
DEFAULT_WORKER_MODEL = os.environ.get("MTJ_WORKER_MODEL", "opus")
CLAUDE_TIMEOUT_S = int(os.environ.get("MTJ_CLAUDE_TIMEOUT_S", "3600"))


class BridgeCommandError(RuntimeError):
    """A subprocess the bridge owns failed. Message is redacted before it is raised."""


@dataclasses.dataclass(frozen=True)
class CommandRun:
    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def display(self) -> str:
        return redact(" ".join(shlex.quote(a) for a in self.argv))


def run(argv: list[str], cwd: str | Path | None = None, timeout: int = 300,
        check: bool = True, stdin: str | None = None) -> CommandRun:
    """Run a command, capture it, redact it, and halt loudly on failure."""
    proc = subprocess.run(
        argv,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=timeout,
        input=stdin,
    )
    result = CommandRun(
        argv=tuple(argv),
        returncode=proc.returncode,
        stdout=redact(proc.stdout or ""),
        stderr=redact(proc.stderr or ""),
    )
    log.debug("ran command", extra={"argv": result.display(), "rc": result.returncode})
    if check and not result.ok:
        raise BridgeCommandError(
            f"command failed (rc={result.returncode}): {result.display()}\n"
            f"stderr: {result.stderr[:2000]}"
        )
    return result


# ==========================================================================
# GitHub
# ==========================================================================


class GitHubAdapter(Protocol):
    """Everything the bridge needs from GitHub. The fake in `fakes.py` implements it."""

    def list_issues(self, state: str = "open") -> list[dict]: ...
    def get_issue(self, number: int) -> dict: ...
    def list_comments(self, number: int) -> list[dict]: ...
    def post_comment(self, number: int, body: str, idempotency_key: str = "") -> dict: ...
    def create_issue(self, title: str, body: str) -> int: ...
    def create_draft_pr(self, title: str, body: str, head: str, base: str) -> int: ...
    def pr_changed_paths(self, number: int) -> list[str]: ...


class GhCliGitHub:
    """Real GitHub adapter over the `gh` CLI, reusing existing keyring auth.

    No token is ever read, printed or stored by this class: `gh` resolves its own
    credential. Bodies are passed on stdin via --body-file - so nothing sensitive
    can land in a process listing.
    """

    def __init__(self, repo: str, dry_run: bool = False):
        self.repo = repo
        self.dry_run = dry_run

    # ---- reads -----------------------------------------------------------
    def list_issues(self, state: str = "open") -> list[dict]:
        out = run(["gh", "issue", "list", "--repo", self.repo, "--state", state,
                   "--limit", "100", "--json", "number,title,state,updatedAt,labels"])
        return json.loads(out.stdout or "[]")

    def get_issue(self, number: int) -> dict:
        out = run(["gh", "issue", "view", str(number), "--repo", self.repo,
                   "--json", "number,title,state,body,updatedAt,labels,author"])
        return json.loads(out.stdout)

    def list_comments(self, number: int) -> list[dict]:
        out = run(["gh", "issue", "view", str(number), "--repo", self.repo, "--json", "comments"])
        return json.loads(out.stdout).get("comments", [])

    def pr_changed_paths(self, number: int) -> list[str]:
        out = run(["gh", "pr", "view", str(number), "--repo", self.repo, "--json", "files"])
        return [f["path"] for f in json.loads(out.stdout).get("files", [])]

    # ---- writes ----------------------------------------------------------
    def post_comment(self, number: int, body: str, idempotency_key: str = "") -> dict:
        """Post a comment. With an idempotency key, a re-run after a crash is a no-op.

        The key is embedded as an HTML comment, which GitHub renders invisibly, so
        the ledger stays readable while remaining machine-deduplicable.
        """
        body = redact(body)
        if idempotency_key:
            marker = f"<!-- mtj-idem:{idempotency_key} -->"
            if any(marker in (c.get("body") or "") for c in self.list_comments(number)):
                log.info("comment already posted; skipping (idempotent)",
                         extra={"issue": number, "key": idempotency_key})
                return {"skipped": True, "reason": "idempotent-duplicate"}
            body = f"{body}\n\n{marker}"
        if self.dry_run:
            log.info("DRY-RUN would post comment", extra={"issue": number, "bytes": len(body)})
            return {"dry_run": True, "body": body}
        run(["gh", "issue", "comment", str(number), "--repo", self.repo, "--body-file", "-"],
            stdin=body, timeout=120)
        return {"posted": True}

    def create_issue(self, title: str, body: str) -> int:
        if self.dry_run:
            log.info("DRY-RUN would create issue", extra={"title": title})
            return -1
        out = run(["gh", "issue", "create", "--repo", self.repo, "--title", title,
                   "--body-file", "-"], stdin=redact(body), timeout=120)
        return int(out.stdout.strip().rstrip("/").split("/")[-1])

    def create_draft_pr(self, title: str, body: str, head: str, base: str) -> int:
        if self.dry_run:
            log.info("DRY-RUN would open draft PR", extra={"head": head, "base": base})
            return -1
        out = run(["gh", "pr", "create", "--repo", self.repo, "--draft", "--title", title,
                   "--body-file", "-", "--head", head, "--base", base], stdin=redact(body),
                  timeout=180)
        return int(out.stdout.strip().rstrip("/").split("/")[-1])


# ==========================================================================
# git
# ==========================================================================


class GitOps:
    """Wrapper-owned git lifecycle.

    The model never runs git. The wrapper creates the worktree, inspects what
    changed, commits, and pushes. That keeps the model's mutation authority
    scoped to 'edit files inside this directory'.
    """

    def __init__(self, repo_root: str | Path, dry_run: bool = False,
                 protected: tuple[str, ...] = ()):
        from .policy import PROTECTED_BRANCHES

        self.repo_root = Path(repo_root)
        self.dry_run = dry_run
        self.protected = protected or PROTECTED_BRANCHES

    def _git(self, args: list[str], cwd: str | Path | None = None, check: bool = True) -> CommandRun:
        return run(["git", *args], cwd=cwd or self.repo_root, check=check)

    def rev_parse(self, ref: str, cwd: str | Path | None = None) -> str:
        return self._git(["rev-parse", ref], cwd=cwd).stdout.strip()

    def fetch(self, remote: str = "origin", ref: str = "") -> None:
        self._git(["fetch", remote] + ([ref] if ref else []))

    def current_branch(self, cwd: str | Path | None = None) -> str:
        return self._git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd).stdout.strip()

    def is_dirty(self, cwd: str | Path | None = None) -> bool:
        return bool(self._git(["status", "--porcelain"], cwd=cwd).stdout.strip())

    def changed_paths(self, cwd: str | Path) -> list[str]:
        """Every path the working tree differs on, tracked or not."""
        out = self._git(["status", "--porcelain", "--untracked-files=all"], cwd=cwd).stdout
        paths = []
        for line in out.splitlines():
            if not line.strip():
                continue
            path = line[3:].strip()
            if " -> " in path:  # rename
                path = path.split(" -> ", 1)[1]
            paths.append(path.strip('"'))
        return sorted(paths)

    def assert_not_protected(self, branch: str) -> None:
        if branch in self.protected:
            raise BridgeCommandError(
                f"refusing to operate on protected branch '{branch}'. "
                f"Protected: {list(self.protected)}"
            )

    def add_worktree(self, path: str | Path, branch: str, base: str) -> Path:
        self.assert_not_protected(branch)
        path = Path(path)
        if self.dry_run:
            log.info("DRY-RUN would create worktree", extra={"path": str(path), "branch": branch})
            return path
        self._git(["worktree", "add", "-b", branch, str(path), base])
        return path

    def remove_worktree(self, path: str | Path, force: bool = False) -> None:
        if self.dry_run:
            return
        args = ["worktree", "remove", str(path)]
        if force:
            args.append("--force")
        self._git(args, check=False)

    def commit_all(self, cwd: str | Path, message: str) -> str:
        branch = self.current_branch(cwd)
        self.assert_not_protected(branch)
        if self.dry_run:
            log.info("DRY-RUN would commit", extra={"branch": branch})
            return "0" * 40
        self._git(["add", "-A"], cwd=cwd)
        self._git(["commit", "-m", message], cwd=cwd)
        return self.rev_parse("HEAD", cwd=cwd)

    def push_branch(self, cwd: str | Path, branch: str, remote: str = "origin") -> None:
        self.assert_not_protected(branch)
        if self.dry_run:
            log.info("DRY-RUN would push", extra={"branch": branch})
            return
        self._git(["push", "-u", remote, branch], cwd=cwd)


# ==========================================================================
# Claude (Worker execution model)
# ==========================================================================


class ClaudeAdapter(Protocol):
    def run_task(self, prompt: str, cwd: str | Path, allowed_tools: list[str] | None = None) -> dict: ...


@dataclasses.dataclass
class ClaudeCliAdapter:
    """A FRESH noninteractive Claude Code invocation per task.

    Discovered invocation mode (Claude Code 2.1.251):

        claude -p --output-format json --session-id <fresh-uuid>
               --permission-mode acceptEdits --model <model>
               --add-dir <task-worktree>

    `-p/--print` is the noninteractive mode. `--output-format json` returns a
    single JSON object carrying `result`, `is_error`, `session_id`, `num_turns`,
    `permission_denials` and `total_cost_usd`.

    A fresh `--session-id` is generated for every task and `--continue` /
    `--resume` are NEVER passed, which is what makes Worker sessions disposable:
    each task is reconstructed from the durable issue contract, not from a
    previous Claude conversation.
    """

    model: str = DEFAULT_WORKER_MODEL
    timeout_s: int = CLAUDE_TIMEOUT_S
    permission_mode: str = "acceptEdits"
    dry_run: bool = False
    max_budget_usd: float | None = None

    def build_argv(self, cwd: str | Path, session_id: str,
                   allowed_tools: list[str] | None = None) -> list[str]:
        argv = [
            "claude", "-p",
            "--output-format", "json",
            "--session-id", session_id,
            "--permission-mode", self.permission_mode,
            "--model", self.model,
            "--add-dir", str(cwd),
        ]
        if allowed_tools:
            argv += ["--allowedTools", *allowed_tools]
        if self.max_budget_usd:
            argv += ["--max-budget-usd", str(self.max_budget_usd)]
        return argv

    def run_task(self, prompt: str, cwd: str | Path,
                 allowed_tools: list[str] | None = None) -> dict:
        session_id = str(uuid.uuid4())
        argv = self.build_argv(cwd, session_id, allowed_tools)
        if self.dry_run:
            log.info("DRY-RUN would invoke Claude",
                     extra={"argv": " ".join(argv), "prompt_bytes": len(prompt)})
            return {"dry_run": True, "session_id": session_id, "is_error": False,
                    "result": "", "argv": argv}
        proc = run(argv, cwd=cwd, timeout=self.timeout_s, check=False, stdin=prompt)
        if not proc.ok:
            raise BridgeCommandError(
                f"claude invocation failed (rc={proc.returncode}): {proc.stderr[:2000]}"
            )
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise BridgeCommandError(
                f"claude did not return parseable JSON: {exc}; first 500 bytes: "
                f"{proc.stdout[:500]}"
            ) from exc
        payload["argv"] = argv
        return payload


# ==========================================================================
# OpenAI (Manager review model)
# ==========================================================================


class ManagerModelAdapter(Protocol):
    def review(self, prompt: str, schema_hint: str = "") -> str: ...


@dataclasses.dataclass
class OpenAIResponsesAdapter:
    """Manager reviewer over the OpenAI Responses API.

    A FRESH invocation per review: no thread, no conversation id, no stored
    state. Everything the model knows arrives in this one prompt, reconstructed
    from durable GitHub/repo state.

    The model is configurable via MTJ_MANAGER_MODEL so a model upgrade is a
    config change, not an architecture change. The model returns text only; it
    has no tools and cannot execute git, shell or GitHub operations. Its output
    is parsed as `mtj-review/1` and then handed to the deterministic policy
    layer, which is what decides whether anything is written.
    """

    model: str = DEFAULT_MANAGER_MODEL
    dry_run: bool = False
    timeout_s: int = 600

    def review(self, prompt: str, schema_hint: str = "") -> str:
        if self.dry_run:
            log.info("DRY-RUN would call manager model", extra={"model": self.model})
            return ""
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise BridgeCommandError(
                "the openai package is not installed; `pip install openai` in the bridge venv, "
                "or run with a fake adapter (--offline)"
            ) from exc
        if not os.environ.get("OPENAI_API_KEY"):
            raise BridgeCommandError(
                "OPENAI_API_KEY is not set. The bridge never stores this key; export it in the "
                "operator shell for the duration of a live manager run."
            )
        client = OpenAI(timeout=self.timeout_s)
        response = client.responses.create(
            model=self.model,
            instructions=(
                "You are the MTJ refoundation Manager. You review a Worker result and return "
                "ONLY one fenced ```yaml block conforming to mtj-review/1. You have no tools "
                "and no authority to execute anything. A deterministic policy layer validates "
                "your output and decides what, if anything, is written to GitHub."
            ),
            input=prompt + ("\n\n" + schema_hint if schema_hint else ""),
        )
        return redact(response.output_text)
