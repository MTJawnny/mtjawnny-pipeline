"""Local codebook persistence — deterministic bytes and the A13 atomic write.

## What this is

Two functions and three error types. Turn a codebook document into its
contracted bytes, and install those bytes at an explicit path in a way that can
never leave a half-written or unvalidated file behind.

`B-MIGRATION-DISCOVERY.md` sec.10 **A13** is the whole specification:

    an independent verifier is REQUIRED before any mutation lands: separate code
    path from the writer, per-member expected-assertion checks derived directly
    from source artifacts, quote-verbatim validation, negative-test suite,
    temp-write + verify + atomic-replace on every mutator.

The last clause is what lives here. The order of the steps is the guarantee, so
it is written out rather than summarised:

    lint in memory -> temp write -> flush -> fsync -> re-read the TEMP ->
    lint the READBACK -> re-serialize and require the exact payload back ->
    digest the payload -> os.replace -> digest the INSTALLED file -> compare

The temp is what gets validated, so a crash between validation and rename leaves
the good old file in place plus an inert `.tmp` for a human to notice. A file
that fails lint never becomes the live file.

## What this is NOT

It is not a move of `experiments/foundry_codebook.py`. That module is the ORACLE
for both behaviours — the bytes and the digest are differentially compared
against it — but its boundary is not the target architecture, and four of its
properties are deliberately not reproduced:

* **No default path.** The legacy writer already took an explicit `path`, but it
  sat beside `CODEBOOK_PATH`, `BACKUPS_DIR` and a loader that defaults to the
  live file. Nothing here knows the repository exists; `path` is the only way in.
* **No process exit.** The legacy writer calls `fc.halt()`, which prints to
  stderr and calls `sys.exit(1)`. A library may not end the process. The two
  integrity failures raise, carrying the legacy message bodies verbatim, and the
  transitional legacy facade translates them back.
* **No loading, no backup, no hashing service.** Reading a codebook, the
  schema-rejection loader, backup policy and the generic `sha256_of(path)`
  helper all stay behind the legacy boundary. `_digest_file` here is PRIVATE and
  exists for exactly one caller: the post-install check three lines below it.
* **No legacy imports, no `sys.path`, no network, no subprocess.** Stdlib plus
  `mtj_foundry.codebook`, and nothing else — which is the property the
  authority boundary (P3 §17) now asserts about this module by name.

## Three things that must not be "tidied"

* **`os.replace` stays late-bound through the `os` module.** `from os import
  replace` would be equivalent Python and would silently disarm the ratified
  interruption control: `foundry_verify_migration.negative_tests` patches
  `os.replace` on the shared module to prove an interrupted write leaves the
  live file byte-identical. Same for `os.fsync` and `json.load`.
* **`OSError` propagates unwrapped.** The interruption control asserts a *raw*
  `OSError` escapes. Catching it here to raise something friendlier would turn
  that control green while removing what it proves.
* **The digest is taken over the PAYLOAD, then re-taken from the INSTALLED
  FILE.** Hashing the payload twice would compare a value with itself; the check
  exists because the bytes crossed a filesystem in between.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from mtj_foundry import codebook

__all__ = [
    "CodebookStoreError",
    "PostWriteDigestError",
    "SerializationMismatchError",
    "serialize",
    "write_atomic",
]

_CHUNK_BYTES = 1 << 20


class CodebookStoreError(RuntimeError):
    """Base for the store's own INTEGRITY failures, and only those.

    A missing directory, a permission error, a full disk or a malformed JSON
    file are not this: the legacy writer never translated them either, and the
    A13 interruption control depends on a raw `OSError` reaching the caller.
    """


class SerializationMismatchError(CodebookStoreError):
    """Re-serializing the readback did not reproduce the written bytes.

    Non-deterministic serialization. The temp file is left where it is and the
    target is not touched.
    """


class PostWriteDigestError(CodebookStoreError):
    """The installed file does not hash to the payload that was verified.

    Filesystem-level corruption between `os.replace` and the read-back digest.
    """


def serialize(codebook_document: dict) -> str:
    """The byte contract: `indent=2`, `ensure_ascii=False`, one trailing newline.

    BYTE_EXACT with the legacy `_serialize`. `ensure_ascii=False` is not
    cosmetic — the operational codebook carries real curly apostrophes and
    non-ASCII card text, and the tracked authority selector pins the sha256 of
    exactly these bytes.
    """
    return json.dumps(codebook_document, indent=2, ensure_ascii=False) + "\n"


def _digest_file(path: Path) -> str:
    """sha256 of a file's exact bytes. PRIVATE, and deliberately so.

    This is not a general digest API and must not become one. `mtj_foundry.
    conservation.digest_file` is the general one, and it is NOT usable here: its
    contract requires a canonical repository-relative label domain, while this
    module writes to arbitrary explicit paths — including the OS temp paths the
    verifier's negative tests use. Widening `conservation` to fit would trade a
    narrow, enforced manifest contract for a shared abstraction neither caller
    actually wants.

    The legacy generic `sha256_of(path)` stays exactly where it is for its own
    callers; this reads the same bytes for one caller, ten lines below.
    """
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(_CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_atomic(path, codebook_document: dict, path_label: str = None) -> str:
    """Install `codebook_document` at `path` under the A13 protocol.

    Returns the sha256 of the file now at `path`.

    Raises `mtj_foundry.codebook.LintError` if the document is invalid either in
    memory or on readback — in both cases nothing is installed.
    `SerializationMismatchError` and `PostWriteDigestError` are the store's own
    two integrity failures. Every other exception — `OSError`, a JSON decode
    error, anything the filesystem raises — propagates unwrapped, exactly as it
    did from the legacy writer.
    """
    path = Path(path)
    label = path_label or str(path)
    codebook.lint(codebook_document, f"{label} (pre-write, in memory)")

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    payload = serialize(codebook_document)
    with open(tmp_path, "w", encoding="utf-8") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())

    with open(tmp_path, "r", encoding="utf-8") as handle:
        readback = json.load(handle)
    codebook.lint(readback, f"{label} (readback of temp)")
    if serialize(readback) != payload:
        raise SerializationMismatchError(
            f"{tmp_path}: re-serializing the readback does not reproduce the written bytes — "
            f"non-deterministic serialization, refusing to install this file")

    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    os.replace(tmp_path, path)
    if _digest_file(path) != digest:
        raise PostWriteDigestError(
            f"{path}: post-rename sha256 does not match the verified temp — filesystem-level "
            f"corruption, do not trust this file")
    return digest
