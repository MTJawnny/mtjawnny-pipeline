"""Codebook authority kernel — manifest law, succession, exact-byte verification.

## The law this module owns (P3-1, ruled 2026-08-14)

    The authoritative codebook is the exact immutable R2 snapshot selected by
    the tracked manifest in the current Git revision.

Authority is therefore NEVER derived from the newest object, the latest
timestamp, lexicographic order, a directory listing, a local mtime, a mutable
`latest.json`, or a successful upload. An uploaded object that no tracked
manifest selects is ORPHAN / NON-AUTHORITATIVE.

S12 moved this law out of the legacy `foundry_authority` shell and into
permanent ownership under conservation. The rule text, the refusal text and the
order of every check are the shell's, character for character; what changed is
the failure boundary and the layout knowledge.

## What this module is

* **The manifest contract.** Field order, strict field validation that halts
  rather than coerces, the content-addressed object key, and the deterministic
  serializer.
* **Succession.** A candidate's predecessor link is checked against the PRIOR
  TRACKED MANIFEST, which is an argument. This module has no transport, so "the
  newest remote object" is not merely forbidden here, it is unavailable.
* **Exact-byte verification.** Size AND sha256, both, and nothing else counts.
* **The metadata truth boundary.** The codebook-describing manifest facts are
  derived from the codebook bytes, and a manifest whose facts disagree with its
  own payload is caught.

## What this module is NOT

* **Not a layout owner.** Every path is an explicit argument. Where the tracked
  selector and the operational codebook live is `ProjectPaths`' fact and the
  composition boundary's to supply; there is no default path here.
* **Not a process boundary.** The legacy shell ended the process with `STOP — `
  on a refusal. A library may not exit, so every such refusal raises an
  `AuthorityRefusal` subclass carrying the legacy message body verbatim, and the
  shell translates it back at its own boundary.
* **Not a transport, a status reporter or an installer.** Those are
  `authority_transport`, `authority_status` and `authority_restore`, each above
  this module and none below it.
* **No network, no subprocess, no write.** Stdlib plus the codebook model and the
  codebook byte contract.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

from mtj_foundry import codebook, codebook_store

__all__ = [
    "AUTHORITY_BUCKET",
    "AuthorityRefusal",
    "ByteVerificationError",
    "COUNT_FIELDS",
    "DERIVED_FIELDS",
    "LocalCodebookError",
    "MANIFEST_FIELDS",
    "ManifestInvalidError",
    "ManifestSerializationError",
    "OBJECT_KEY_FILENAME",
    "OBJECT_KEY_PREFIX",
    "ObjectKeyError",
    "SCHEMA",
    "build_manifest",
    "compare_manifest_to_codebook",
    "derive_manifest_facts",
    "describe_local",
    "load_manifest",
    "object_key_for",
    "serialize_manifest",
    "sha256_of_bytes",
    "sha256_of_file",
    "validate_manifest",
    "validate_or_raise",
    "validate_succession",
    "verify_exact",
    "verify_or_raise",
]

SCHEMA = "foundry-authority/1"

# The bucket is part of OBJECT IDENTITY: the same key in another bucket is a
# different object, and if the manifest omits it the identity gets supplied by
# a developer's rclone remote nickname -- which P3 §9 forbids. Not secret.
AUTHORITY_BUCKET = "mtjawnny-foundry"

# Emission order for the manifest. Determinism law: the serializer receives
# facts in a fixed order and invents nothing (P3 §16).
MANIFEST_FIELDS = (
    "schema",
    "snapshot_id",
    "bucket",
    "object_path",
    "sha256",
    "byte_size",
    "created_utc",
    "codebook_schema",
    "codebook_version",
    "corpus_ref",
    "active_axis_count",
    "assertion_count",
    "human_assertion_count",
    "rule_derived_assertion_count",
    "mutation_review_id",
    "previous_snapshot_hash",
)

COUNT_FIELDS = (
    "active_axis_count",
    "assertion_count",
    "human_assertion_count",
    "rule_derived_assertion_count",
)

# Fields that DESCRIBE the codebook and must be derived from it, never typed.
DERIVED_FIELDS = (
    "sha256",
    "byte_size",
    "codebook_schema",
    "codebook_version",
    "active_axis_count",
    "assertion_count",
    "human_assertion_count",
    "rule_derived_assertion_count",
)

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SNAPSHOT_ID_RE = re.compile(r"^[0-9A-Za-z][0-9A-Za-z._-]{0,127}$")
_TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_CORPUS_REF_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Content-addressed immutable key (P3 §6). The hash is IN the key, so new bytes
# get a new key by construction and no two different payloads can intentionally
# share one. The key shape is also a validator: a manifest whose object_path
# does not embed its own sha256 is internally inconsistent.
OBJECT_KEY_PREFIX = "foundry/codebook/sha256"
OBJECT_KEY_FILENAME = "codebook.json"
_OBJECT_KEY_RE = re.compile(
    rf"^{re.escape(OBJECT_KEY_PREFIX)}/([0-9a-f]{{64}})/{re.escape(OBJECT_KEY_FILENAME)}$"
)

# A key shape that implies a MUTABLE pointer is refused outright. There is no
# authoritative latest.json for the codebook and creating one would move
# authority without a commit.
_MUTABLE_KEY_TOKENS = ("latest", "current", "newest", "head", "live")

_CHUNK_BYTES = 1024 * 1024


# ---------------------------------------------------------------------------
# typed refusals
# ---------------------------------------------------------------------------

class AuthorityRefusal(RuntimeError):
    """Base for the refusals the legacy shell rendered as a process STOP.

    Every subclass carries the legacy halt's message body verbatim, so the shell
    can print `STOP — <message>` and exit 1 byte-identically. Transport and
    restore failures are deliberately NOT under this base: the shell always let
    those propagate as catchable errors, and folding them in here would teach a
    translating caller to turn a catchable error into a process exit.
    """


class ObjectKeyError(AuthorityRefusal):
    """A snapshot key was requested for something that is not a sha256."""


class ManifestSerializationError(AuthorityRefusal):
    """An incomplete manifest, or one carrying an unknown field, was serialized."""


class ManifestInvalidError(AuthorityRefusal):
    """A manifest failed validation where the caller required a valid one."""


class ByteVerificationError(AuthorityRefusal):
    """Bytes failed exact verification where the caller required them to pass."""


class LocalCodebookError(AuthorityRefusal):
    """The local codebook is unparseable, or absent where facts were required."""


# ---------------------------------------------------------------------------
# object key
# ---------------------------------------------------------------------------

def object_key_for(sha256: str) -> str:
    """The one place a snapshot key is constructed."""
    if not _SHA256_RE.match(sha256 or ""):
        raise ObjectKeyError(f"object_key_for: {sha256!r} is not a lowercase 64-hex sha256")
    return f"{OBJECT_KEY_PREFIX}/{sha256}/{OBJECT_KEY_FILENAME}"


# ---------------------------------------------------------------------------
# B. deterministic manifest serialization
# ---------------------------------------------------------------------------

def serialize_manifest(manifest: dict) -> str:
    """Fixed key order, house JSON style, trailing newline. PURE: it invents
    nothing -- no clock, no uuid, no environment. Given the same dict it
    returns the same bytes, which is what makes the manifest's own sha
    reproducible (P3 §16).

    The byte policy is not restated here. `indent=2`, `ensure_ascii=False` and
    one trailing newline is exactly `codebook_store.serialize`, the one owner of
    that JSON byte contract in this package, so the manifest is emitted through
    it rather than through a second copy of the same `json.dumps` call."""
    missing = [f for f in MANIFEST_FIELDS if f not in manifest]
    if missing:
        raise ManifestSerializationError(
            f"serialize_manifest: refusing to serialize an incomplete manifest, "
            f"missing {missing} — validate before serializing")
    extra = [k for k in manifest if k not in MANIFEST_FIELDS]
    if extra:
        raise ManifestSerializationError(
            f"serialize_manifest: unknown field(s) {extra} — a field with no "
            f"architectural purpose does not get silently written")
    ordered = {f: manifest[f] for f in MANIFEST_FIELDS}
    return codebook_store.serialize(ordered)


# ---------------------------------------------------------------------------
# A. manifest validator -- REFUSES, never coerces (P3 §5)
# ---------------------------------------------------------------------------

def validate_manifest(manifest, label: str = "manifest") -> list:
    """Return a list of violations. Empty list == valid. Never mutates, never
    coerces, never 'best efforts' a broken manifest."""
    v = []

    if not isinstance(manifest, dict):
        return [f"{label}: top level is {type(manifest).__name__}, expected an object"]

    schema = manifest.get("schema")
    if schema != SCHEMA:
        v.append(f"{label}: schema is {schema!r}, expected {SCHEMA!r} (unknown schema "
                 f"version is fatal — this reader will not guess a layout)")

    for field in MANIFEST_FIELDS:
        if field not in manifest:
            v.append(f"{label}: missing required field {field!r}")
    unknown = [k for k in manifest if k not in MANIFEST_FIELDS]
    if unknown:
        v.append(f"{label}: unknown field(s) {sorted(unknown)}")
    if v and schema != SCHEMA:
        return v

    sha = manifest.get("sha256")
    if not isinstance(sha, str) or not _SHA256_RE.match(sha):
        v.append(f"{label}: sha256 {sha!r} is not a lowercase 64-hex digest")

    size = manifest.get("byte_size")
    # bool is an int subclass; a JSON `true` must not pass as a byte size.
    if isinstance(size, bool) or not isinstance(size, int):
        v.append(f"{label}: byte_size {size!r} is {type(size).__name__}, expected int")
    elif size <= 0:
        v.append(f"{label}: byte_size {size} must be positive — a zero-byte "
                 f"authority snapshot is never valid")

    ts = manifest.get("created_utc")
    if not isinstance(ts, str) or not _TIMESTAMP_RE.match(ts):
        v.append(f"{label}: created_utc {ts!r} is not strict UTC "
                 f"YYYY-MM-DDTHH:MM:SSZ")
    else:
        try:
            datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            v.append(f"{label}: created_utc {ts!r} matches the shape but is not a "
                     f"real instant")

    sid = manifest.get("snapshot_id")
    if not isinstance(sid, str) or not _SNAPSHOT_ID_RE.match(sid):
        v.append(f"{label}: snapshot_id {sid!r} is not a safe identifier")

    bucket = manifest.get("bucket")
    if not isinstance(bucket, str) or not bucket.strip():
        v.append(f"{label}: bucket {bucket!r} is not a non-empty string — the "
                 f"bucket is part of object identity and may not be inferred "
                 f"from a local remote nickname")

    path = manifest.get("object_path")
    if not isinstance(path, str) or not path:
        v.append(f"{label}: object_path {path!r} is not a non-empty string")
    else:
        low = path.lower()
        hit = [t for t in _MUTABLE_KEY_TOKENS if t in low]
        if hit:
            v.append(f"{label}: object_path {path!r} contains mutable-pointer "
                     f"token(s) {hit} — there is no authoritative latest.json for "
                     f"the codebook and a mutable key cannot be an authority")
        elif path != path.strip() or path.startswith("/") or ".." in path.split("/"):
            v.append(f"{label}: object_path {path!r} is not a clean relative key")
        else:
            m = _OBJECT_KEY_RE.match(path)
            if not m:
                v.append(f"{label}: object_path {path!r} is not the content-addressed "
                         f"shape {OBJECT_KEY_PREFIX}/<sha256>/{OBJECT_KEY_FILENAME}")
            elif isinstance(sha, str) and _SHA256_RE.match(sha or "") and m.group(1) != sha:
                v.append(f"{label}: object_path embeds sha {m.group(1)} but sha256 field "
                         f"is {sha} — a content-addressed key that disagrees with its "
                         f"own content hash selects the wrong object")

    for f in COUNT_FIELDS:
        val = manifest.get(f)
        if isinstance(val, bool) or not isinstance(val, int):
            v.append(f"{label}: {f} {val!r} is {type(val).__name__}, expected int")
        elif val < 0:
            v.append(f"{label}: {f} {val} is negative")

    if all(isinstance(manifest.get(f), int) and not isinstance(manifest.get(f), bool)
           for f in COUNT_FIELDS):
        total = manifest["assertion_count"]
        human = manifest["human_assertion_count"]
        derived = manifest["rule_derived_assertion_count"]
        axes = manifest["active_axis_count"]
        if human > total:
            v.append(f"{label}: human_assertion_count {human} exceeds assertion_count {total}")
        if derived > total:
            v.append(f"{label}: rule_derived_assertion_count {derived} exceeds "
                     f"assertion_count {total}")
        if human + derived > total:
            v.append(f"{label}: human {human} + rule-derived {derived} exceeds "
                     f"assertion_count {total} — the class split is impossible")
        if total > 0 and axes == 0:
            v.append(f"{label}: assertion_count {total} with active_axis_count 0 — "
                     f"assertions cannot exist without an axis to hang on")

    # GENESIS SEMANTICS, ruled 2026-08-14: the FIRST authority manifest carries
    # exactly null. Every later one carries the lowercase 64-hex sha256 of the
    # previously selected snapshot. An invented zero-hash or self-hash sentinel
    # is banned -- and the zero hash is 64 valid hex characters, so it is
    # structurally legal and has to be refused on MEANING, not on shape.
    prev = manifest.get("previous_snapshot_hash")
    if prev is None:
        pass                                   # genesis, and the only legal non-hash
    elif not isinstance(prev, str) or not _SHA256_RE.match(prev):
        v.append(f"{label}: previous_snapshot_hash {prev!r} must be null (genesis only) "
                 f"or a lowercase 64-hex digest — no sentinel strings")
    elif prev == "0" * 64:
        v.append(f"{label}: previous_snapshot_hash is the all-zero digest — genesis is "
                 f"expressed as null, never as an invented zero hash")
    elif isinstance(sha, str) and prev == sha:
        v.append(f"{label}: previous_snapshot_hash equals sha256 ({sha}) — a snapshot "
                 f"cannot be its own predecessor")

    mrid = manifest.get("mutation_review_id")
    if not isinstance(mrid, str) or not mrid.strip():
        v.append(f"{label}: mutation_review_id {mrid!r} is not a non-empty string — "
                 f"every snapshot names the ratified mutation that produced it")

    cs = manifest.get("codebook_schema")
    if cs != codebook.SCHEMA_V2:
        v.append(f"{label}: codebook_schema {cs!r}, expected {codebook.SCHEMA_V2!r}")
    cv = manifest.get("codebook_version")
    if not isinstance(cv, str) or not cv.strip():
        v.append(f"{label}: codebook_version {cv!r} is not a non-empty string")
    cr = manifest.get("corpus_ref")
    if not isinstance(cr, str) or not _CORPUS_REF_RE.match(cr or ""):
        v.append(f"{label}: corpus_ref {cr!r} is not a YYYY-MM-DD snapshot date")

    return v


def validate_or_raise(manifest, label: str = "manifest") -> dict:
    """`validate_manifest`, refusing on any violation. Raises
    `ManifestInvalidError`; the legacy shell's `validate_or_halt` prints it."""
    v = validate_manifest(manifest, label)
    if v:
        raise ManifestInvalidError(
            "invalid authority manifest — refusing to proceed:\n  " + "\n  ".join(v))
    return manifest


def validate_succession(candidate: dict, prior: dict = None, label: str = "candidate") -> list:
    """Does `candidate` correctly name its PREDECESSOR? Returns violations.

    `validate_manifest` can only check the SHAPE of `previous_snapshot_hash` —
    null or 64-hex. Shape is not succession: `"a" * 64` is perfectly well-formed
    and names nothing. This is the check that the link points at the snapshot
    the PRIOR TRACKED MANIFEST actually selected.

    THE PREDECESSOR IS AN ARGUMENT, NOT A LOOKUP. This function has no
    transport, does no listing, and cannot reach the network — so "the newest
    remote object" is not merely forbidden here, it is unavailable. `prior` is
    the manifest from the previous Git revision; the caller obtains it from the
    tracked file, which is what P3-1 means by Git selecting and R2 storing.
    Caller prose about which snapshot came first is never consulted.

        prior is None  -> candidate MUST be genesis (previous_snapshot_hash null)
        prior exists   -> candidate MUST carry prior['sha256'], and must not be
                          genesis, and must not re-publish the predecessor's own
                          bytes under a new snapshot_id.
    """
    v = []
    prev = candidate.get("previous_snapshot_hash") if isinstance(candidate, dict) else None

    if prior is None:
        if prev is not None:
            v.append(
                f"{label}: previous_snapshot_hash is {prev!r} but there is NO prior tracked "
                f"manifest to succeed. A first manifest is genesis and carries null; naming "
                f"a predecessor that the repository does not select is unverifiable by "
                f"construction and must never be accepted on the caller's word.")
        return v

    prior_v = validate_manifest(prior, "prior manifest")
    if prior_v:
        v.append(f"{label}: the PRIOR manifest is itself invalid, so succession cannot be "
                 f"established against it ({len(prior_v)} violation(s); first: {prior_v[0]})")
        return v

    if prev is None:
        v.append(
            f"{label}: previous_snapshot_hash is null (genesis) but a prior authority exists "
            f"({prior['sha256']}). A second genesis would silently orphan the existing "
            f"authority history rather than extend it.")
    elif prev != prior.get("sha256"):
        v.append(
            f"{label}: previous_snapshot_hash {prev} does not match the sha256 of the prior "
            f"selected authority {prior.get('sha256')}. The predecessor link is checked "
            f"against the manifest the repository selects, never against a remote listing "
            f"or the caller's assertion.")

    if candidate.get("sha256") == prior.get("sha256"):
        v.append(
            f"{label}: sha256 equals the prior authority's sha256 ({prior.get('sha256')}) — "
            f"the same bytes cannot succeed themselves. Re-selecting an unchanged snapshot "
            f"is a no-op, not a new authority.")

    if candidate.get("snapshot_id") == prior.get("snapshot_id"):
        v.append(
            f"{label}: snapshot_id {candidate.get('snapshot_id')!r} is the prior manifest's "
            f"own id — a successor must be distinguishable from its predecessor.")

    return v


def load_manifest(path) -> tuple:
    """Returns (manifest_or_None, violations) for the manifest at an EXPLICIT
    path. A MISSING manifest is not an error -- it is AUTHORITY_NOT_INITIALIZED.
    A malformed one is fatal and must never degrade into 'go find the newest
    remote object'."""
    path = Path(path)
    if not path.exists():
        return None, []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return None, [f"{path}: not parseable JSON ({e.__class__.__name__}: {e})"]
    return raw, validate_manifest(raw, str(path))


# ---------------------------------------------------------------------------
# C. exact-byte verifier (P3 §7)
# ---------------------------------------------------------------------------

def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_of_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(_CHUNK_BYTES), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_exact(expected_sha: str, expected_size: int, target) -> tuple:
    """(ok, reason). Success requires BOTH exact byte size AND exact sha256.

    Trusts nothing else: not a process exit code, not file existence, not a
    non-empty file, not remote metadata, not the path. `target` is a Path or
    raw bytes."""
    if not isinstance(expected_sha, str) or not _SHA256_RE.match(expected_sha or ""):
        return False, f"expected_sha {expected_sha!r} is not a lowercase 64-hex digest"
    if isinstance(expected_size, bool) or not isinstance(expected_size, int) or expected_size < 0:
        return False, f"expected_size {expected_size!r} is not a non-negative int"

    if isinstance(target, (bytes, bytearray)):
        data = bytes(target)
        actual_size, actual_sha, where = len(data), sha256_of_bytes(data), "<bytes>"
    else:
        p = Path(target)
        if not p.exists():
            return False, f"{p}: does not exist (a transport that returned 0 did not " \
                          f"produce this file — LAW A)"
        if not p.is_file():
            return False, f"{p}: is not a regular file"
        actual_size, actual_sha, where = p.stat().st_size, sha256_of_file(p), str(p)

    if actual_size != expected_size:
        return False, (f"{where}: byte size {actual_size} != expected {expected_size} "
                       f"(truncated, padded or a different object)")
    if actual_sha != expected_sha:
        return False, (f"{where}: sha256 {actual_sha} != expected {expected_sha} "
                       f"(same size, different content — size alone is never proof)")
    return True, f"{where}: verified {actual_size} bytes, sha256 {actual_sha}"


def verify_or_raise(expected_sha: str, expected_size: int, target) -> None:
    """`verify_exact`, refusing on failure. Raises `ByteVerificationError`."""
    ok, reason = verify_exact(expected_sha, expected_size, target)
    if not ok:
        raise ByteVerificationError(f"byte verification FAILED — {reason}")


# ---------------------------------------------------------------------------
# D. local facts (P3 §10) -- READ ONLY, mutates nothing
# ---------------------------------------------------------------------------

def describe_local(path) -> dict:
    """Facts about the codebook at an EXPLICIT path. Derived, never carried
    forward."""
    path = Path(path)
    if not path.exists():
        return {"present": False, "path": str(path)}
    try:
        cb = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        # Refuse loudly: a local codebook that will not parse is a real
        # emergency, and reporting it as "no local codebook" would understate it.
        raise LocalCodebookError(
            f"{path}: local codebook is not parseable JSON ({e.__class__.__name__}: {e}) "
            f"— refusing to describe it; restore from a verified backup")
    axes = cb.get("axes") or {}
    active = [a for a in axes.values() if a.get("status") == "active"]
    total = human = derived = 0
    for a in active:
        for m in a.get("members") or []:
            for s in m.get("assertions") or []:
                total += 1
                cls = s.get("class")
                if cls == "human":
                    human += 1
                elif cls == "rule-derived":
                    derived += 1
    return {
        "present": True,
        "path": str(path),
        "sha256": sha256_of_file(path),
        "byte_size": path.stat().st_size,
        "codebook_schema": cb.get("schema"),
        "codebook_version": cb.get("version"),
        "active_axis_count": len(active),
        "assertion_count": total,
        "human_assertion_count": human,
        "rule_derived_assertion_count": derived,
    }


# --- metadata truth boundary (P3 §6) ---------------------------------------
#
# `validate_manifest` is a LOW-LEVEL STRUCTURAL validator: it proves a manifest
# is well-formed, and it CANNOT know whether the counts describe the bytes the
# manifest selects. A structurally perfect manifest can still lie. These
# functions are the truth boundary -- `build_manifest` builds the facts with
# `derive_manifest_facts` (from the candidate bytes) instead of accepting caller
# prose, and `compare_manifest_to_codebook` is the check that catches a manifest
# whose numbers do not describe its own payload.

def derive_manifest_facts(codebook_path) -> dict:
    """Every codebook-describing manifest field, computed FROM the codebook.

    `corpus_ref` is deliberately not derived here: it comes from the shipped
    artifact manifest rather than the codebook, and reading it has a halt
    condition of its own. The caller supplies it; this function stays pure."""
    local = describe_local(codebook_path)
    if not local.get("present"):
        raise LocalCodebookError(
            f"{local.get('path')} not found — cannot derive manifest facts from a "
            f"codebook that does not exist")
    return {f: local[f] for f in DERIVED_FIELDS}


def build_manifest(snapshot_id: str, created_utc: str, mutation_review_id: str,
                   corpus_ref: str, previous_snapshot_hash, codebook_path,
                   prior: dict = None) -> dict:
    """Assemble a manifest whose codebook-describing fields are DERIVED from the
    candidate bytes, and which the caller cannot override.

    The caller supplies only what the bytes cannot know: an id, an instant, the
    ratified mutation that produced it, the corpus snapshot date, and the
    predecessor link. Everything in DERIVED_FIELDS — including `object_path`,
    whose key embeds the content hash — is computed here from the file itself,
    so "trusting CLI-supplied metadata" is not a discipline to remember but a
    parameter that does not exist.

    Validated before it is returned: structurally, against the codebook it
    claims to describe, and — when a predecessor is supplied — for succession.
    Nothing is written anywhere; this builds an object, and publication is a
    separate lifecycle."""
    facts = derive_manifest_facts(codebook_path)
    manifest = {
        "schema": SCHEMA,
        "snapshot_id": snapshot_id,
        "bucket": AUTHORITY_BUCKET,
        "object_path": object_key_for(facts["sha256"]),
        "created_utc": created_utc,
        "corpus_ref": corpus_ref,
        "mutation_review_id": mutation_review_id,
        "previous_snapshot_hash": previous_snapshot_hash,
    }
    manifest.update(facts)

    v = validate_manifest(manifest, "built manifest")
    v += compare_manifest_to_codebook(manifest, codebook_path)
    v += validate_succession(manifest, prior, "built manifest")
    if v:
        raise ManifestInvalidError(
            "build_manifest produced a manifest that does not validate — refusing to "
            "return it:\n  " + "\n  ".join(v))
    return {f: manifest[f] for f in MANIFEST_FIELDS}


def compare_manifest_to_codebook(manifest: dict, codebook_path) -> list:
    """Do the manifest's codebook-describing fields actually describe this
    codebook? Returns violations. This is the check a structural validator
    cannot make: every field below can be individually well-formed and jointly
    false."""
    facts = derive_manifest_facts(codebook_path)
    v = []
    for field in DERIVED_FIELDS:
        claimed, actual = manifest.get(field), facts[field]
        if claimed != actual:
            v.append(f"{field}: manifest claims {claimed!r} but the codebook is {actual!r}")
    return v
