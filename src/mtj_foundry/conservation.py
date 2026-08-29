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
import os
from pathlib import Path
from typing import Iterable

__all__ = [
    "MANIFEST_SCHEMA",
    "FileDigest",
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
    label = str(Path(target).relative_to(relative_to)) if relative_to else str(target)
    return FileDigest(path=label, sha256=digest.hexdigest(), size_bytes=size)


def digest_paths(root: str | os.PathLike[str],
                 relpaths: Iterable[str]) -> tuple[FileDigest, ...]:
    """Digest an EXPLICIT list of repository-relative paths, sorted deterministically.

    Takes a list rather than walking a tree on purpose: a tree walk silently
    changes what it measures when the tree changes, which makes it useless as a
    stable conservation input. The caller declares what is being conserved.
    """
    base = Path(root)
    entries = [digest_file(base / rel, relative_to=base) for rel in relpaths]
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
