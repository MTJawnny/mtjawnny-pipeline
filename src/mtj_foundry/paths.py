"""Repository layout and root resolution — the ONE owner of both.

## Why this module exists

Measured in P0.1 and confirmed by the P0.2 Manager review: the legacy shared
foundation derives the repository root itself, mutates `sys.path`, and imports an
engine module at import time, so the foundation depends upward on the engine.
Roughly 97 sites derive a root or hardcode layout independently.

## What this module is NOT

P0.2 correction C1 rejected the stronger P0.1 proposal that one module may touch
the filesystem and that importing it asserts a repository is present. Both are
refused here, deliberately:

- **No global `ROOT`.** There is no module-level root constant to import.
- **No import-time discovery.** Importing this module runs no git search, reads
  no filesystem, and raises nothing. An installed package, a test fixture, a
  detached worktree, an archive, or an arbitrary root must all stay usable.
- **Ordinary libraries are not banned from I/O.** They receive an explicit
  `ProjectPaths` (or a plain `Path`) from the composition boundary; they simply
  do not rediscover the repository or restate its layout.

The invariant this module carries is therefore: *exactly one component defines
repository-relative layout and default root resolution.*

`discover_root()` exists for the CLI/composition boundary and is EXPLICITLY
CALLED. It halts loudly when it cannot find a root, which is house style for an
explicit request — the refused behavior is halting merely because someone
imported a library.
"""

from __future__ import annotations

import dataclasses
import os
from pathlib import Path

__all__ = ["ProjectPaths", "RootNotFound", "discover_root"]

# The marker that identifies a repository root when discovery is explicitly asked
# for. Kept here because layout knowledge lives in exactly one module.
_ROOT_MARKERS: tuple[str, ...] = (".git",)


class RootNotFound(RuntimeError):
    """Explicit root discovery failed. Never raised at import time."""


@dataclasses.dataclass(frozen=True)
class ProjectPaths:
    """An immutable, explicit view of repository layout rooted at `root`.

    Construction touches NO filesystem: no existence check, no resolution against
    the current working directory, no discovery. A caller may build one for a root
    that does not exist — a test fixture, a planned destination, a remote checkout
    — and every derived path is a pure string join.
    """

    root: Path

    # ---- construction ---------------------------------------------------
    @classmethod
    def for_root(cls, root: str | os.PathLike[str]) -> "ProjectPaths":
        """Build paths for an EXPLICIT root. The only supported constructor.

        Deliberately does not verify the root exists. Verification is the caller's
        decision at the point where it matters, not a side effect of describing a
        layout.
        """
        return cls(root=Path(root))

    # ---- refoundation layout (current) ----------------------------------
    @property
    def src(self) -> Path:
        return self.root / "src"

    @property
    def tests(self) -> Path:
        return self.root / "tests"

    @property
    def config(self) -> Path:
        return self.root / "config"

    @property
    def baselines(self) -> Path:
        """Tracked ratchet/control baselines.

        P0.2 accepted that control inputs which govern acceptance must be tracked
        and reviewable; the legacy ratchet baseline was ignored by git and so a
        change to it was not naturally visible in a diff.
        """
        return self.config / "baselines"

    @property
    def refoundation(self) -> Path:
        return self.root / "refoundation"

    @property
    def decisions(self) -> Path:
        return self.refoundation / "decisions"

    @property
    def conservation(self) -> Path:
        return self.refoundation / "conservation"

    # ---- legacy layout (READ-ONLY KNOWLEDGE, nothing here moves it) ------
    # Recorded so that later phases have ONE place that knows where legacy state
    # lives, rather than re-deriving `experiments/out/...` at ~97 more sites.
    # Naming these does not move, read, or change anything.
    @property
    def legacy_docs(self) -> Path:
        return self.root / "docs"

    @property
    def legacy_experiments(self) -> Path:
        return self.root / "experiments"

    @property
    def legacy_experiments_out(self) -> Path:
        return self.legacy_experiments / "out"

    @property
    def legacy_foundry_out(self) -> Path:
        return self.legacy_experiments_out / "foundry"

    @property
    def legacy_pipeline(self) -> Path:
        return self.root / "pipeline"

    # ---- generic ---------------------------------------------------------
    def resolve(self, *parts: str) -> Path:
        """Join repository-relative parts onto the root. No filesystem access."""
        return self.root.joinpath(*parts)


def discover_root(start: str | os.PathLike[str], *,
                  markers: tuple[str, ...] = _ROOT_MARKERS) -> Path:
    """Walk upward from `start` to the nearest directory carrying a root marker.

    EXPLICIT CALL ONLY. Nothing in this package calls it at import time, and no
    library should call it to recover a root it was not given — that is the
    rediscovery habit this module replaces. Intended for a CLI/composition
    boundary that must turn a working directory into a `ProjectPaths`.

    Halts loudly rather than guessing: an unfound root is an error the caller
    asked for, not a silent fallback to the current directory.
    """
    current = Path(start).absolute()
    for candidate in (current, *current.parents):
        if any((candidate / marker).exists() for marker in markers):
            return candidate
    raise RootNotFound(
        f"no repository root found at or above {current}: none of {list(markers)} "
        "is present. Pass an explicit root to ProjectPaths.for_root() instead."
    )
