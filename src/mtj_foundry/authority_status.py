"""Codebook authority status — classification and candidate reporting, READ ONLY.

## What this is

The six authority states and the one function that decides between them, moved
out of the legacy `foundry_authority` shell under conservation. It reads the
tracked selector at an explicit path, describes the local codebook at an
explicit path, and -- only when a transport is supplied -- confirms that the
SELECTED object exists at its exact key.

It sits above both `authority` and `authority_transport` for one reason: it is
the only reader of the kernel that must classify a transport failure, and it
does so as `AUTHORITY_UNVERIFIABLE` rather than as anything stronger.

## What this is NOT

* **Not a repairer.** A local/authority mismatch is REPORTED. The local copy is
  never overwritten, never published, and being newer never makes it authority.
* **Not a discoverer.** An invalid or unparseable selector is `MANIFEST_INVALID`
  and the transport is never consulted; a selected object that is missing is
  `AUTHORITY_UNVERIFIABLE` and is never resolved by looking for another one.
* **Not a promoter.** A candidate is reported beside the state, stamped
  `authoritative: False` unconditionally, and the state is computed before it is
  looked at, so an existing remote object cannot move the state.
* **Not a layout owner.** Both paths are required arguments.
"""

from __future__ import annotations

from mtj_foundry import authority, authority_transport

__all__ = [
    "STATE_LOCAL_MATCHES",
    "STATE_MANIFEST_INVALID",
    "STATE_MISMATCH",
    "STATE_NOT_INITIALIZED",
    "STATE_NO_LOCAL",
    "STATE_UNVERIFIABLE",
    "describe_candidate",
    "status",
]

STATE_NOT_INITIALIZED = "AUTHORITY_NOT_INITIALIZED"
STATE_LOCAL_MATCHES = "LOCAL_MATCHES_AUTHORITY"
STATE_MISMATCH = "LOCAL_CANDIDATE_AUTHORITY_MISMATCH"
STATE_MANIFEST_INVALID = "MANIFEST_INVALID"
STATE_UNVERIFIABLE = "AUTHORITY_UNVERIFIABLE"
STATE_NO_LOCAL = "NO_LOCAL_CODEBOOK"


def describe_candidate(candidate: dict, transport=None) -> dict:
    """Report an UNSELECTED snapshot without ever making it authority.

    A candidate is a manifest a human handed us, describing an object that may
    exist remotely. It becomes authority when — and only when — a manifest in
    the tracked Git revision selects it. So this function:

      * takes the candidate as an ARGUMENT; it cannot discover one,
      * never lists, never sorts, never takes "the only object present",
      * and stamps `authoritative: False` unconditionally, with the reason.

    It is deliberately NOT a second source of truth: `status()` calls it for
    reporting only, and no branch of authority resolution reads its output."""
    out = {
        "authoritative": False,
        "classification": "ORPHAN_CANDIDATE",
        "why_not_authority": (
            "no manifest in the tracked Git revision selects this object. Uploading does "
            "not confer authority; Git selects and R2 stores (P3-1)."),
        "bucket": candidate.get("bucket"),
        "object_path": candidate.get("object_path"),
        "sha256": candidate.get("sha256"),
        "byte_size": candidate.get("byte_size"),
        "violations": authority.validate_manifest(candidate, "candidate manifest"),
    }
    if transport is not None:
        try:
            meta = transport.stat(candidate["object_path"])
        except authority_transport.TransportError as e:
            out["remote"] = f"unreachable: {e}"
        else:
            out["remote"] = "absent" if meta is None else f"present, size={meta.get('size')}"
    return out


def status(manifest_path, codebook_path, transport=None, candidate: dict = None) -> dict:
    """Read-only. Distinguishes the authority states and NEVER repairs,
    publishes, overwrites or falls back to a listing."""
    manifest, violations = authority.load_manifest(manifest_path)
    local = authority.describe_local(codebook_path)

    if manifest is None and violations:
        return {"state": STATE_MANIFEST_INVALID, "violations": violations, "local": local,
                "detail": "the tracked manifest exists but is not parseable — this "
                          "NEVER degrades to selecting the newest remote object"}
    if manifest is None:
        out = {"state": STATE_NOT_INITIALIZED, "local": local,
               "detail": "no tracked authority manifest in this Git revision. The local "
                         "codebook is the operational source and is NOT an authority; "
                         "any remote object is orphan until a manifest selects it."}
        # A published candidate is REPORTED here and changes nothing: the state
        # above is computed before this line and is not revisited. An existing
        # remote object must not be able to move the state, or "upload equals
        # authority" would be true in the one place it is most tempting.
        if candidate is not None:
            out["candidate"] = describe_candidate(candidate, transport)
        return out
    if violations:
        return {"state": STATE_MANIFEST_INVALID, "violations": violations, "local": local,
                "manifest": manifest,
                "detail": "invalid manifest — refusing to interpret it, and refusing to "
                          "fall back to remote listing"}
    if not local.get("present"):
        return {"state": STATE_NO_LOCAL, "manifest": manifest, "local": local,
                "detail": "manifest selects an authority but there is no local codebook "
                          "to compare — restore from the selected snapshot"}

    result = {"manifest": manifest, "local": local,
              "selected": {"bucket": manifest["bucket"], "object_path": manifest["object_path"],
                           "sha256": manifest["sha256"], "byte_size": manifest["byte_size"]}}

    if transport is not None:
        try:
            meta = transport.stat(manifest["object_path"])
        except authority_transport.TransportError as e:
            result["state"] = STATE_UNVERIFIABLE
            result["detail"] = f"selected object could not be checked: {e}"
            return result
        if meta is None:
            result["state"] = STATE_UNVERIFIABLE
            result["detail"] = (f"the manifest selects {manifest['object_path']} but no such "
                                f"object exists. NOT resolved by looking for another one.")
            return result
        if meta.get("size") != manifest["byte_size"]:
            result["state"] = STATE_UNVERIFIABLE
            result["detail"] = (f"selected object size {meta.get('size')} != manifest "
                                f"{manifest['byte_size']}")
            return result

    if local["sha256"] == manifest["sha256"] and local["byte_size"] == manifest["byte_size"]:
        result["state"] = STATE_LOCAL_MATCHES
        result["detail"] = "local codebook is byte-identical to the selected authority"
    else:
        result["state"] = STATE_MISMATCH
        result["detail"] = (
            f"local sha {local['sha256']} != authority sha {manifest['sha256']}. "
            f"This is REPORTED, not repaired: the local copy is not automatically "
            f"overwritten, is not automatically published, and being newer does not "
            f"make it authority.")
    return result
