"""Verified codebook restore — THE ORDER IS THE SAFETY PROPERTY.

    remote object -> STAGING -> exact sha+size -> codebook validation
                  -> atomic install

and never remote -> operational -> verify afterward. The 2026-08-14 incident was
that second shape executed by accident: a staging fetch was pointed at the live
codebook, and because the fetch unlinks its destination first, the file was
destroyed before any byte was verified. Each step below therefore records itself
in a TRACE, and the trace is asserted -- an ordering that is only documented is
an ordering nobody checks.

S12 moved this orchestration out of the legacy `foundry_authority` shell under
conservation. Two things changed, and both are boundaries, not behaviour:

* **No layout.** The install destination is a required argument, there is no
  default that quietly resolves to the operational codebook, and the transport
  carries its own declared forbidden staging destinations.
* **No backup policy.** Replacing an existing codebook requires a pre-install
  backup, and WHERE backups live is a layout fact this library may not know. So
  the backup is an injected callable. Without one, replacement is REFUSED rather
  than performed unbacked; the legacy shell injects its readback-verified backup.

It depends on the kernel for exact verification and the manifest/codebook fact
comparison, and on the codebook model for lint. It imports no transport: the
transport is an argument, used only through `get_verified`.
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from mtj_foundry import authority, codebook

__all__ = [
    "RESTORE_STEPS",
    "RestoreError",
    "install_atomic",
    "restore_snapshot",
    "validate_codebook_payload",
]

RESTORE_STEPS = ("fetch", "verify", "validate", "install")


class RestoreError(RuntimeError):
    pass


def validate_codebook_payload(path, manifest: dict) -> dict:
    """Is this file a CODEBOOK, and is it the one the manifest describes?

    Byte identity is not structural validity: a truncated-then-repadded file, a
    different artifact of the same length, or a codebook from another schema can
    all hash to whatever their bytes hash to. The manifest's sha proves WHICH
    bytes; this proves the bytes are a codebook, and that its own contents agree
    with what the manifest claims about them. Both are required before install.
    """
    try:
        cb = json.loads(Path(path).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise RestoreError(
            f"staged object is not parseable JSON ({e.__class__.__name__}: {e}) — it "
            f"transported correctly and is still not a codebook. Refusing to install.")
    if not isinstance(cb, dict) or not isinstance(cb.get("axes"), dict):
        raise RestoreError(
            "staged object parses as JSON but has no `axes` object — it is not a codebook. "
            "Refusing to install.")
    if cb.get("schema") != codebook.SCHEMA_V2:
        raise RestoreError(
            f"staged codebook schema is {cb.get('schema')!r}, expected {codebook.SCHEMA_V2!r}. "
            f"Refusing to install an artifact this reader cannot claim to understand.")

    # The repository's own linter, not a second opinion invented here. It RAISES
    # LintError and returns stats on success, and a restore must raise a
    # catchable error its caller can report.
    try:
        stats = codebook.lint(cb, f"restored codebook ({path})")
    except codebook.LintError as e:
        raise RestoreError(f"staged codebook fails lint — {e}")

    mismatches = authority.compare_manifest_to_codebook(manifest, path)
    if mismatches:
        raise RestoreError(
            "staged codebook does not match the manifest that selected it:\n  "
            + "\n  ".join(mismatches) + "\nRefusing to install.")
    return {"axes": len(cb["axes"]), "lint": stats}


def install_atomic(staged, dest, expected_sha: str, expected_size: int,
                   replace_existing: bool = False, *, backup=None) -> str:
    """Install VERIFIED staged bytes at `dest` atomically. Returns dest sha.

    Re-verifies the staged bytes immediately before the rename: this function is
    the last thing between a candidate and an operational file, so it does not
    take a caller's word that verification happened earlier. The write is
    temp+fsync+os.replace within the destination directory, so `dest` is never
    observed half-written and a crash leaves the previous file intact.

    `backup` is a callable taking the existing `dest`, called before an existing
    file with different bytes is replaced. It is required for replacement."""
    staged, dest = Path(staged), Path(dest)
    ok, reason = authority.verify_exact(expected_sha, expected_size, staged)
    if not ok:
        raise RestoreError(f"REFUSING TO INSTALL unverified bytes — {reason}")

    if dest.exists():
        current = authority.sha256_of_file(dest)
        if current == expected_sha:
            return current                      # already installed; idempotent
        if not replace_existing:
            raise RestoreError(
                f"{dest} already exists with different bytes (sha {current}). Refusing to "
                f"replace an existing codebook without an explicit instruction; a restore "
                f"that silently overwrites is the incident shape.")
        if backup is None:
            raise RestoreError(
                f"{dest} already exists with different bytes (sha {current}) and no backup "
                f"was supplied. Refusing to replace an existing codebook without a "
                f"pre-install backup; this library does not know where backups live.")
        backup(dest)

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".restore-tmp")
    shutil.copyfile(staged, tmp)
    with open(tmp, "rb") as f:
        os.fsync(f.fileno())
    ok, reason = authority.verify_exact(expected_sha, expected_size, tmp)
    if not ok:
        tmp.unlink(missing_ok=True)
        raise RestoreError(f"staged->temp copy did not reproduce the bytes — {reason}")
    os.replace(tmp, dest)
    final = authority.sha256_of_file(dest)
    if final != expected_sha:
        raise RestoreError(
            f"post-install sha {final} != expected {expected_sha} — filesystem-level "
            f"corruption; do not trust {dest}")
    return final


def restore_snapshot(manifest: dict, transport, staging_dir, install_to,
                     replace_existing: bool = False, *, backup=None) -> dict:
    """The whole restore law, in order, with the order recorded and asserted.

    `install_to` is REQUIRED and explicit. There is no default that quietly
    resolves to the operational codebook."""
    authority.validate_or_raise(manifest, "restore manifest")
    staging_dir, install_to = Path(staging_dir), Path(install_to)
    staged = staging_dir / "codebook.staged.json"

    if staged.resolve() == install_to.resolve():
        raise RestoreError(
            "staging path and install destination are the same file — the staging step "
            "exists precisely so the destination is not written until the bytes are proven")

    trace = []
    key, sha, size = manifest["object_path"], manifest["sha256"], manifest["byte_size"]

    # 1. FETCH to staging. get_verified categorically refuses the declared
    #    operational codebook as a destination, before any unlink.
    staging_dir.mkdir(parents=True, exist_ok=True)
    transport.get_verified(key, staged, sha, size)
    trace.append("fetch")

    # 2. VERIFY the staged bytes independently of the fetch that produced them.
    ok, reason = authority.verify_exact(sha, size, staged)
    if not ok:
        raise RestoreError(f"staged bytes failed verification — {reason}")
    trace.append("verify")

    # 3. VALIDATE that they are a codebook, and the one the manifest describes.
    payload = validate_codebook_payload(staged, manifest)
    trace.append("validate")

    # 4. INSTALL atomically. Unreachable unless 1-3 all passed, because each of
    #    them raises rather than returning a status nobody reads.
    installed_sha = install_atomic(staged, install_to, sha, size, replace_existing,
                                   backup=backup)
    trace.append("install")

    if trace != list(RESTORE_STEPS):
        raise RestoreError(f"restore executed steps {trace}, expected {list(RESTORE_STEPS)}")
    return {"trace": trace, "installed": str(install_to), "sha256": installed_sha,
            "byte_size": size, "staged": str(staged), "payload": payload}
