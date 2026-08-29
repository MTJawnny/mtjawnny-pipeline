"""Conservation primitives v0 — deterministic, read-only, exact bytes.

## What this is for

The refoundation may not move or delete legacy material until it can prove what
was there. P0.2 correction C8 puts a conservation harness BEFORE migration, and
C7 requires that authority identity be preserved as *exact bytes*, not as a hash
of some canonicalized re-serialization.

So v0 measures three things and nothing else:

    path  ·  sha256 of the exact file bytes  ·  size in bytes

## What this deliberately does NOT do

**Semantic equivalence is deferred**, by task constraint
(`semantic_equivalence_logic: defer`). Nothing here decides whether two files
*mean* the same thing. A byte digest answers "did these bytes survive"; it cannot
answer "is this the same ruling", and pretending otherwise is how a conservation
check starts passing for the wrong reason. C7.3 makes the same point from the
other side: byte-identity is the right test only where bytes are themselves
contracted.

Everything here is READ-ONLY: no function writes, moves, or creates a path.

## The path domain

A declared path is a **canonical repository-relative POSIX path**: `/`-separated,
no leading `/`, no drive letter, no `..`, no empty or `.` segment, and unique
within one declaration set. `canonical_relpath` is the only admission gate and it
REFUSES anything else rather than repairing it.

This is narrower than "a path that happens to work", on purpose:

- an **absolute** declaration is not repository-relative, so a manifest containing
  one describes one operator's machine and cannot be compared against another;
- a **traversal** (`..`) can address bytes outside the root, so a set that claims
  to conserve a repository could silently include, or exclude, something outside it;
- a **duplicate** canonical path would be digested twice, and `entry_count` and
  `total_bytes` would then double-count it while the set is unchanged — a manifest
  that miscounts itself is worse than no manifest;
- an **empty or root** declaration names no file.

Emitted labels always use `/`, so a manifest produced on one platform compares
against one produced on another. The previous version recorded platform-native
labels while its own docstring claimed cross-machine comparability; that claim is
now backed by the domain rather than asserted.

## Determinism

Entries are sorted by path with a fixed key, the manifest is emitted as JSON with
sorted keys and fixed separators, and the digest is taken over those exact bytes.
Repeated runs over unchanged inputs produce a byte-identical manifest and an
identical digest — which is what makes a later comparison meaningful.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import ntpath
import os
import posixpath
from pathlib import Path, PurePath
from typing import Iterable

__all__ = [
    "MANIFEST_SCHEMA",
    "FileDigest",
    "PathDomainError",
    "canonical_relpath",
    "posix_label",
    "digest_bytes",
    "digest_file",
    "digest_paths",
    "manifest",
    "manifest_json",
    "manifest_digest",
]

MANIFEST_SCHEMA = "mtj-conservation-manifest/1"

# Read in chunks: a codebook snapshot is ~5 MB and later inputs may be far larger.
_CHUNK_BYTES = 1 << 20


class PathDomainError(ValueError):
    """A declared path is outside the canonical repository-relative POSIX domain.

    Always fatal. A conservation set that quietly dropped or rewrote a declaration
    would report conservation of a set nobody declared.
    """


def canonical_relpath(declared: str | os.PathLike[str]) -> str:
    """Admit one declaration into the canonical domain, or raise.

    Returns the canonical `/`-joined form. Refuses rather than repairs: silently
    normalising `../x` or a duplicate would make the manifest disagree with what the
    caller wrote, and the caller is the one making the conservation claim.
    """
    raw = os.fspath(declared)
    if not isinstance(raw, str):  # pragma: no cover - defensive
        raise PathDomainError(f"declared path must be a string, got {type(raw).__name__}")
    if not raw.strip():
        raise PathDomainError("declared path is empty")
    if "\\" in raw:
        raise PathDomainError(
            f"declared path {raw!r} contains a backslash; declarations are POSIX-style "
            "and '/' is the only separator"
        )
    if raw.startswith("/") or ntpath.isabs(raw) or posixpath.isabs(raw):
        raise PathDomainError(
            f"declared path {raw!r} is absolute; declarations are repository-relative so "
            "a manifest does not describe one operator's machine"
        )
    parts = [seg for seg in raw.split("/") if seg not in ("", ".")]
    if any(seg == ".." for seg in parts):
        raise PathDomainError(
            f"declared path {raw!r} contains a parent traversal; a conservation set may "
            "not address bytes outside the root it claims to conserve"
        )
    if not parts:
        raise PathDomainError(
            f"declared path {raw!r} names the root, not a file"
        )
    return "/".join(parts)


@dataclasses.dataclass(frozen=True, order=True)
class FileDigest:
    """One file's conservation identity. `path` is repository-relative."""

    path: str
    sha256: str = dataclasses.field(compare=False)
    size_bytes: int = dataclasses.field(compare=False)

    def as_dict(self) -> dict:
        return {"path": self.path, "sha256": self.sha256, "size_bytes": self.size_bytes}


def digest_bytes(data: bytes) -> str:
    """sha256 of exact bytes, lowercase hex."""
    return hashlib.sha256(data).hexdigest()


def posix_label(target: PurePath,
                relative_to: str | os.PathLike[str] | None = None) -> str:
    """The `/`-separated label a manifest records for `target`.

    Split out so it is testable against a pure Windows path: on POSIX,
    `str(p)` and `p.as_posix()` are identical, so a test running only here cannot
    tell the two apart and a regression to platform-native labels would pass
    unnoticed on this machine while breaking cross-platform comparison.
    """
    relative = target.relative_to(relative_to) if relative_to is not None else target
    return relative.as_posix()


def digest_file(path: str | os.PathLike[str], *,
                relative_to: str | os.PathLike[str] | None = None) -> FileDigest:
    """Digest one file by its EXACT bytes. Opens read-only, binary, never writes.

    `relative_to` only controls the recorded label, never what is read: a manifest
    that records absolute operator paths is not comparable across machines.
    """
    target = Path(path)
    digest = hashlib.sha256()
    size = 0
    with open(target, "rb") as handle:
        while True:
            chunk = handle.read(_CHUNK_BYTES)
            if not chunk:
                break
            digest.update(chunk)
            size += len(chunk)
    label = posix_label(Path(target), relative_to)
    return FileDigest(path=label, sha256=digest.hexdigest(), size_bytes=size)


def digest_paths(root: str | os.PathLike[str],
                 relpaths: Iterable[str]) -> tuple[FileDigest, ...]:
    """Digest an EXPLICIT list of declared paths, sorted deterministically.

    Takes a list rather than walking a tree on purpose: a tree walk silently
    changes what it measures when the tree changes, which makes it useless as a
    stable conservation input. The caller declares what is being conserved.

    Every declaration must be in the canonical repository-relative POSIX domain and
    must be unique within the set. Both are checked BEFORE any file is opened, so a
    malformed set fails without having half-measured itself.
    """
    base = Path(root)
    seen: dict[str, str] = {}
    canonical: list[str] = []
    for declared in relpaths:
        canon = canonical_relpath(declared)
        if canon in seen:
            raise PathDomainError(
                f"duplicate declaration: {declared!r} and {seen[canon]!r} are both "
                f"{canon!r}. A repeated path would be digested twice and double-count "
                "itself in entry_count and total_bytes."
            )
        seen[canon] = str(declared)
        canonical.append(canon)
    entries = [digest_file(base.joinpath(*canon.split("/")), relative_to=base)
               for canon in canonical]
    return tuple(sorted(entries, key=lambda e: e.path))


def manifest(entries: Iterable[FileDigest]) -> dict:
    """Assemble a manifest mapping. Sorted, schema-tagged, no timestamps.

    No clock is read: a manifest that embeds `generated_at` can never be compared
    byte-for-byte against a later run, which is the entire point of the artifact.
    """
    ordered = sorted(entries, key=lambda e: e.path)
    return {
        "schema": MANIFEST_SCHEMA,
        "entry_count": len(ordered),
        "total_bytes": sum(e.size_bytes for e in ordered),
        "entries": [e.as_dict() for e in ordered],
    }


def manifest_json(entries: Iterable[FileDigest]) -> str:
    """The manifest's canonical serialization. Stable across runs and platforms."""
    return json.dumps(manifest(entries), sort_keys=True, indent=2,
                      separators=(",", ": "), ensure_ascii=True) + "\n"


def manifest_digest(entries: Iterable[FileDigest]) -> str:
    """One digest standing for a whole declared set of files."""
    return digest_bytes(manifest_json(entries).encode("utf-8"))
