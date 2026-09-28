"""Trusted-host Git finalization: the provider edits, the host commits.

A Worker provider is a model process. It may edit and test files in the
checkout; it may not write Git metadata. Codex's workspace-write sandbox cannot
write `.git` at all, and widening that sandbox would hand a model the power to
move refs. So the provider-neutral rule is the narrow one, for every provider:
the host -- this module, run by the supervisor -- turns a provider's working-tree
changes into the unit's one commit, and nothing else does.

After a successful provider response, and only after its Worker evidence has
been extracted, the host:

1. proves the provider left HEAD, the branch, every ref, the local config and
   the index exactly as they were before dispatch (BUS_PROVIDER_GIT_MUTATION
   otherwise);
2. measures the working tree and proves every added, modified and deleted path
   is inside `allow_paths` and outside `deny_paths` BEFORE staging anything
   (BUS_UNIT_SCOPE_ESCAPE otherwise, and the dirty tree stays as evidence);
3. refuses a commit-boundary mutating unit that changed nothing
   (BUS_UNIT_NO_COMMIT);
4. stages exactly the measured paths, proves the index holds exactly them, and
   creates one commit with a deterministic message ending in the wave and unit
   trailers (BUS_HOST_COMMIT_FAILED otherwise);
5. pushes that commit to the commanded branch with ordinary non-force
   fast-forward semantics, and re-reads the remote to prove it landed
   (BUS_HOST_PUSH_FAILED otherwise -- a rejection, a race or a failure).

It never repairs, reverts, resets or cleans. A refusal is evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from agent_bus import errors as E
from agent_bus.enforce import changed_paths, commits_between, scope_violations
from agent_bus.errors import BusError
from agent_bus.git_evidence import trailers
from agent_bus.protocol import Envelope
from agent_bus.shell import Runner
from agent_bus.wave import Unit

# Host Git commands run with hooks disabled. A provider that could edit files in
# the checkout must not be able to plant a hook that the HOST then executes with
# the host's credentials; that would be a sandbox escape through the back door.
_NO_HOOKS = ("-c", "core.hooksPath=/dev/null")

# `git status --porcelain=v1` codes a provider's plain edit can produce, with an
# untouched index: modified, type-changed, deleted, untracked.
_WORKTREE_ONLY = {" M": "M", " T": "M", " D": "D", "??": "A"}


@dataclass(frozen=True)
class Snapshot:
    """What Git metadata looked like immediately before the provider ran."""

    head: str
    branch: str
    refs: tuple[str, ...]
    # Local config can make the host's own git execute a command (a planted
    # `core.fsmonitor` runs on `git status`), so it is metadata like any ref.
    config: tuple[str, ...] = ()


@dataclass(frozen=True)
class Finalized:
    """One unit's host finalization. `problems` empty means committed and pushed."""

    problems: tuple[tuple[str, str], ...]
    paths: tuple[str, ...] = ()
    commit: str | None = None

    @property
    def ok(self) -> bool:
        return not self.problems


def _git(run: Runner, repo: str, *args: str, stdin: str | None = None):
    if stdin is None:
        return run(["git", "-C", repo, *args])
    return run(["git", "-C", repo, *args], stdin=stdin)


def _checked(run: Runner, repo: str, *args: str) -> str:
    result = _git(run, repo, *args)
    if result.returncode != 0:
        raise BusError(E.GIT_FAILED, f"git {args[0]} failed in {repo}: {result.stderr.strip()}")
    return result.stdout


def snapshot(repo: str, run: Runner) -> Snapshot:
    head = _checked(run, repo, "rev-parse", "HEAD").strip()
    branch = _checked(run, repo, "rev-parse", "--abbrev-ref", "HEAD").strip()
    refs = _checked(run, repo, "for-each-ref", "--format=%(objectname) %(refname)")
    config = _checked(run, repo, "config", "--local", "--list")
    lines = lambda text: tuple(sorted(line for line in text.splitlines() if line.strip()))
    return Snapshot(head, branch, lines(refs), lines(config))


def worktree_changes(repo: str, run: Runner) -> list[tuple[str, str]]:
    """Every changed path as (XY, path), NUL-separated so no path is ever quoted."""
    out = _checked(run, repo, "status", "--porcelain=v1", "-z", "--untracked-files=all",
                   "--no-renames")
    entries = []
    for record in out.split("\0"):
        if not record:
            continue
        if len(record) < 4 or record[2] != " ":
            raise BusError(E.GIT_FAILED, f"unexpected git status record {record!r}")
        entries.append((record[:2], record[3:]))
    return entries


def git_mutations(before: Snapshot, after: Snapshot,
                  changes: Sequence[tuple[str, str]]) -> list[str]:
    """Every way the provider touched Git metadata. Empty = it only edited files."""
    problems = []
    if after.head != before.head:
        problems.append(f"HEAD moved {before.head} -> {after.head}")
    if after.branch != before.branch:
        problems.append(f"branch changed {before.branch} -> {after.branch}")
    if after.refs != before.refs:
        moved = sorted(set(before.refs) ^ set(after.refs))
        problems.append("refs changed: " + "; ".join(moved[:5]))
    if after.config != before.config:
        problems.append("local git config changed")
    staged = [path for code, path in changes if code not in _WORKTREE_ONLY]
    if staged:
        problems.append("index or merge state changed for: " + "; ".join(staged[:5]))
    return problems


def commit_message(command: Envelope, unit: Unit, provider: str) -> str:
    """Deterministic: the same command, unit and provider always give the same bytes."""
    return (f"Agent Bus {unit.id}: host-finalized unit of {command.wave}\n\n"
            f"Command: {command.message_id}\n"
            f"Provider: {provider}\n\n"
            + trailers(command.wave, unit.id) + "\n")


def finalize(repo: str, remote: str, branch: str, command: Envelope, unit: Unit,
             provider: str, before: Snapshot, run: Runner) -> Finalized:
    """Prove, stage, commit and push one unit -- or refuse before PASS can exist."""
    # Metadata is re-read BEFORE `git status`: status is the first host command
    # a tampered config could turn into code execution.
    after = snapshot(repo, run)
    if after.config != before.config:
        return Finalized(((E.PROVIDER_GIT_MUTATION,
                           f"{provider} mutated Git metadata during {unit.id}; providers edit "
                           "and test only: local git config changed"),))
    changes = worktree_changes(repo, run)
    mutated = git_mutations(before, after, changes)
    if mutated:
        return Finalized(((E.PROVIDER_GIT_MUTATION,
                           f"{provider} mutated Git metadata during {unit.id}; providers edit "
                           "and test only: " + "; ".join(mutated)),))

    paths = tuple(sorted({path for _, path in changes}))
    if not unit.mutating:
        # Read-only: never staged, never committed. Ordinary verification names
        # any leftover change as BUS_READONLY_UNIT_MUTATED.
        return Finalized((), paths)

    escaped = scope_violations(paths, unit.allow_paths, unit.deny_paths)
    if escaped:
        return Finalized(((E.UNIT_SCOPE_ESCAPE,
                           f"{unit.id} changed paths outside its scope (nothing staged): "
                           + ", ".join(escaped)),), paths)
    if not paths:
        if unit.commit_boundary:
            return Finalized(((E.UNIT_NO_COMMIT,
                               f"{unit.id} declares a commit boundary and changed nothing "
                               "for the host to commit"),))
        return Finalized(())

    added = _git(run, repo, "--literal-pathspecs", "add", "-A", "--", *paths)
    if added.returncode != 0:
        return Finalized(((E.HOST_COMMIT_FAILED,
                           f"git add failed: {added.stderr.strip()[:500]}"),), paths)
    staged = tuple(sorted(p for p in _checked(
        run, repo, "diff", "--cached", "--name-only", "--no-renames", "-z").split("\0") if p))
    if staged != paths:
        return Finalized(((E.HOST_COMMIT_FAILED,
                           f"staged {list(staged)} is not exactly the measured {list(paths)}"),),
                         paths)

    committed = _git(run, repo, *_NO_HOOKS, "commit", "--quiet", "--no-verify",
                     "--cleanup=verbatim", "-F", "-",
                     stdin=commit_message(command, unit, provider))
    if committed.returncode != 0:
        return Finalized(((E.HOST_COMMIT_FAILED,
                           f"git commit failed: {committed.stderr.strip()[:500]}"),), paths)
    head = _checked(run, repo, "rev-parse", "HEAD").strip()
    made = commits_between(repo, before.head, head, run)
    if [c.sha for c in made] != [head] or tuple(changed_paths(repo, before.head, head, run)) != paths:
        return Finalized(((E.HOST_COMMIT_FAILED,
                           f"the host commit {head} is not exactly one commit of exactly "
                           f"{list(paths)} on {before.head}"),), paths)

    # Non-force by construction: no `--force`, no `+` refspec. A remote that moved
    # is a rejection, and a rejection is a stop, never a retry or an overwrite.
    target = f"refs/heads/{branch}"
    pushed = _git(run, repo, *_NO_HOOKS, "push", "--porcelain", "--no-verify", remote,
                  f"{head}:{target}")
    if pushed.returncode != 0:
        return Finalized(((E.HOST_PUSH_FAILED,
                           f"push of {head} to {remote} {target} was refused or failed "
                           f"(local commit kept as evidence): "
                           f"{(pushed.stderr or pushed.stdout).strip()[:500]}"),), paths)
    remote_line = _git(run, repo, "ls-remote", remote, target)
    landed = [line.split("\t") for line in remote_line.stdout.splitlines() if line.strip()]
    if remote_line.returncode != 0 or landed != [[head, target]]:
        return Finalized(((E.HOST_PUSH_FAILED,
                           f"{remote} {target} does not name the pushed commit {head} "
                           f"after the push: {remote_line.stdout.strip()[:200]!r}"),), paths)
    return Finalized((), paths, head)
