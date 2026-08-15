#!/usr/bin/env python3
"""C6 AUTHORITY MACHINERY — manifest, byte verifier, transport, status.

THE LAW THIS FILE IMPLEMENTS (P3-1, ruled 2026-08-14):

    The authoritative codebook is the exact immutable R2 snapshot selected by
    the tracked manifest in the current Git revision.

Authority is therefore NEVER derived from the newest object, the latest
timestamp, lexicographic order, a directory listing, a local mtime, a mutable
`latest.json`, or a successful upload. An uploaded object that no tracked
manifest selects is ORPHAN / NON-AUTHORITATIVE. Nothing here lists to decide:
this class has no enumeration verb at all, `stat`/`get` take an EXACT key, and
`stat` refuses a result that matched more than one row.

SUCCESSION IS CHECKED AGAINST THE PRIOR MANIFEST, NEVER AGAINST THE REMOTE.
`validate_succession` compares a candidate's `previous_snapshot_hash` to the
sha256 of the PRIOR TRACKED MANIFEST's selected snapshot. It takes the
predecessor as an argument and has no transport, so "newest remote object" and
"what the caller said in prose" are both structurally unavailable to it.

WHAT THIS FILE DELIBERATELY DOES NOT DO
---------------------------------------
No publication of the real codebook, no promotion, no mutable pointer, no
prune, no delete, no overwrite. `write_codebook_atomic()` stays a local
filesystem primitive in `foundry_codebook.py` and gains no network (P3 §17):
C6 promotion is an explicit separate lifecycle, which is why the publish
primitive lives HERE and refuses on its own.

THE THREE TRANSPORT LAWS (measured 2026-08-14, PART ELEVEN of the P3 packet)
----------------------------------------------------------------------------
LAW A — EXIT STATUS IS NOT OBJECT INTEGRITY. `rclone mkdir` returned exit 0
        while CreateBucket was denied; `rclone copyto` of a MISSING object
        returns exit 0 and creates no file; `lsjson` of a missing key returns
        `[]` at exit 0. So every fetch asserts the destination exists and
        verifies bytes against the manifest. A transport return code is never
        evidence.
LAW B — THE BUCKET PRECHECK MUST NOT MASK THE REAL OPERATION. Bucket-scoped
        credentials 403 on rclone's CreateBucket precheck BEFORE the intended
        operation, which reads exactly like "this credential cannot write".
        Every argv this file builds carries `--s3-no-check-bucket`.
LAW C — THE PUBLISHER CREDENTIAL DOES NOT GUARANTEE IMMUTABILITY. R2's Object
        Read & Write includes DeleteObject and there is nothing narrower, so
        immutability is enforced HERE: `put_immutable` creates with an ATOMIC
        create-only precondition, refuses a key occupied by different bytes,
        and proves identity by remote readback.

WHY THE CREATE IS CONDITIONAL AND NOT JUST CHECKED (2026-08-14)
---------------------------------------------------------------
A check-then-act publish (stat -> PUT) is a TOCTOU race: A sees the key absent,
B creates different bytes, A uploads and destroys B's object. The pre-read
cannot close that window -- only the remote can. Measured against live R2 with
the installed rclone (v1.74.3): `--header-upload "If-None-Match: *"` makes the
create ATOMIC, and a PUT to an occupied key is rejected by the SERVER with
`412 PreconditionFailed` at `PutObject`, leaving the occupant byte-identical.

    THE INSTALLED BINARY HAS NO CONDITIONAL-WRITE FLAG. Measured, not read:
    `rclone help flags` on v1.74.3 matches nothing for condition / if-none /
    if-match / precondition. The generic `--header-upload` is the ONLY
    available primitive, which is why it is used and why it was proven live
    rather than adopted.

AND `rc == 0` DOES NOT PROVE A CREATE HAPPENED -- LAW A, ONE LEVEL DEEPER
-------------------------------------------------------------------------
Measured 2026-08-14, and it defeats the conditional silently: a conditional PUT
of IDENTICAL bytes onto an OCCUPIED key returned **exit 0 with no 412**, because
rclone compared size+modtime itself and logged `Unchanged skipping` -- **no
PutObject was ever issued, so the server precondition never ran.** A local
heuristic had quietly become the decider.

`--ignore-times` is therefore MANDATORY on the conditional create, and with it
the same two cases return 412 with the occupant unchanged: identical bytes onto
an occupied key, and different bytes onto an occupied key. The rule is that the
SERVER decides existence; rclone is never allowed to answer that question from
a local mtime. `FakeRunner` models the skip behaviour exactly, so deleting the
flag turns NC15/NC16/NC21 red instead of silently disarming the precondition.

`--retries 1` rides with it: a 412 is a terminal answer, and retrying it three
times only produces three identical errors to parse.

SINGLE-PUT ONLY. The 412 was proven for `PutObject`. A payload at or above the
multipart cutoff takes a different code path (CreateMultipartUpload), whose
precondition behaviour was NOT measured -- so publication REFUSES at that size
rather than assuming the proof carries over. The cutoff is passed explicitly so
a differently-configured rclone cannot switch paths behind us.

    NOTE, and it is a real distinction, not a hedge: CLAUDE.md's locked rule
    "never --header-upload -- it silently fails to stick the header on R2"
    is about STORED OBJECT METADATA (cache-control), where R2 ignores the
    header and `-M --metadata-set` is required. `If-None-Match` is a REQUEST
    PRECONDITION consumed by the server at request time and never stored, so
    it is a different mechanism -- which is why it was proven live (412 plus a
    same-bytes/fresh-key control) rather than assumed from either rule.

The pre-read is KEPT, for idempotency semantics only. The conditional is what
provides safety; the pre-read is what turns a re-publish of identical bytes
into `already-present` instead of an error.

    python3 experiments/foundry_authority.py status
    python3 experiments/foundry_authority.py verify <file> --sha <hex> --size <n>
    python3 experiments/foundry_authority.py selftest
    python3 experiments/foundry_authority.py describe-local
"""
import os
import re
import sys
import json
import shutil
import hashlib
import argparse
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402
import foundry_codebook as fcb  # noqa: E402

SCHEMA = "foundry-authority/1"

# The tracked selector. DELIBERATELY ABSENT until Captain authorizes the first
# candidate cutover -- its absence is the AUTHORITY_NOT_INITIALIZED state, not
# an error, and a bootstrap file asserting an authority that does not exist
# would be a lie the tooling would then believe (P3 §18).
MANIFEST_PATH = REPO_ROOT / "docs" / "codebook-authority.json"

# The bucket is part of OBJECT IDENTITY: the same key in another bucket is a
# different object, and if the manifest omits it the identity gets supplied by
# a developer's rclone remote nickname -- which P3 §9 forbids. Not secret.
AUTHORITY_BUCKET = "mtjawnny-foundry"

# The live operational codebook. Named here so the transport can REFUSE it as a
# fetch destination (P3 §7): a staging fetch deletes its destination first, so
# pointing one at this path would destroy the operational copy before the
# remote bytes were ever verified.
#
# THIS BINDING IS THE RULE UNDER TEST, and NC20 rebinds it to a decoy so the
# rule can be exercised without naming the real file. That is exactly why it
# cannot be the only arm of the guard -- see `_forbidden_fetch_destinations`.
OPERATIONAL_CODEBOOK_PATH = fcb.CODEBOOK_PATH.resolve()

# THE ARM NO RIG REBINDS. Captured at import, private, and never consulted by
# any test. On 2026-08-14 a rigging run disabled the destination guard and a
# negative control aimed at the real path destroyed the operational codebook
# (docs/INCIDENT-LOCALITY-REVERSION-2026-08-14.md). The lesson taken was that a
# control must be safe when its guard is absent; the lesson taken HERE is the
# structural half of it -- the live codebook is refused as a fetch destination
# even when the rebindable arm has been rigged, monkeypatched or deleted, so
# the safety of the real file never depends on a test being written correctly.
_IMMOVABLE_FORBIDDEN_DESTINATIONS = frozenset({fcb.CODEBOOK_PATH.resolve()})

# Publication is proven for single-part PutObject only (see the docstring).
# Passed explicitly rather than inherited, so the code path cannot change under
# a different rclone config; 200Mi is the measured default of v1.74.3 and the
# operational codebook is ~5MB, three orders of magnitude below it.
SINGLE_PUT_CUTOFF = "200Mi"
SINGLE_PUT_LIMIT_BYTES = 200 * 1024 * 1024

# Remote NICKNAMES are local configuration, never authority (P3 §9).
# The atomic create-only precondition. Established from the INSTALLED binary
# (rclone v1.74.3 `--header-upload`; `rclone help flags` offers no conditional
# -write flag at all) and proven live against R2 by a 412, not chosen from
# documentation. See the module docstring for why this is not the
# `--header-upload` the locked CLAUDE.md rule warns about.
CONDITIONAL_CREATE_HEADER = "If-None-Match: *"

# Measured verbatim from live R2 on 2026-08-14. Kept as a FIXTURE so the
# detector below is tested against what the server actually said, rather than
# against a paraphrase of it written from memory.
MEASURED_412_STDERR = (
    "operation error S3: PutObject, https response error StatusCode: 412, "
    "RequestID: , HostID: , api error PreconditionFailed: At least one of the "
    "pre-conditions you specified did not hold."
)

# Measured verbatim: rclone suppressing the PUT on its own size+modtime check.
# Exit status is 0 and the precondition never reaches the server.
MEASURED_SKIP_STDOUT = "a.txt: Unchanged skipping"

ENV_READ_REMOTE = "MTJ_FOUNDRY_READ_REMOTE"
ENV_WRITE_REMOTE = "MTJ_FOUNDRY_WRITE_REMOTE"
DEFAULT_READ_REMOTE = "r2foundry-ro"
DEFAULT_WRITE_REMOTE = "r2foundry-rw"

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


def object_key_for(sha256: str) -> str:
    """The one place a snapshot key is constructed."""
    if not _SHA256_RE.match(sha256 or ""):
        fc.halt(f"object_key_for: {sha256!r} is not a lowercase 64-hex sha256")
    return f"{OBJECT_KEY_PREFIX}/{sha256}/{OBJECT_KEY_FILENAME}"


def read_remote(explicit: str = None) -> str:
    return explicit or os.environ.get(ENV_READ_REMOTE) or DEFAULT_READ_REMOTE


def write_remote(explicit: str = None) -> str:
    return explicit or os.environ.get(ENV_WRITE_REMOTE) or DEFAULT_WRITE_REMOTE


# ---------------------------------------------------------------------------
# B. deterministic manifest serialization
# ---------------------------------------------------------------------------

def serialize_manifest(manifest: dict) -> str:
    """Fixed key order, house JSON style, trailing newline. PURE: it invents
    nothing -- no clock, no uuid, no environment. Given the same dict it
    returns the same bytes, which is what makes the manifest's own sha
    reproducible (P3 §16)."""
    missing = [f for f in MANIFEST_FIELDS if f not in manifest]
    if missing:
        fc.halt(f"serialize_manifest: refusing to serialize an incomplete manifest, "
                f"missing {missing} — validate before serializing")
    extra = [k for k in manifest if k not in MANIFEST_FIELDS]
    if extra:
        fc.halt(f"serialize_manifest: unknown field(s) {extra} — a field with no "
                f"architectural purpose does not get silently written")
    ordered = {f: manifest[f] for f in MANIFEST_FIELDS}
    return json.dumps(ordered, indent=2, ensure_ascii=False) + "\n"


# ---------------------------------------------------------------------------
# A. manifest validator -- HALTS, never coerces (P3 §5)
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
    if cs != fcb.SCHEMA_V2:
        v.append(f"{label}: codebook_schema {cs!r}, expected {fcb.SCHEMA_V2!r}")
    cv = manifest.get("codebook_version")
    if not isinstance(cv, str) or not cv.strip():
        v.append(f"{label}: codebook_version {cv!r} is not a non-empty string")
    cr = manifest.get("corpus_ref")
    if not isinstance(cr, str) or not _CORPUS_REF_RE.match(cr or ""):
        v.append(f"{label}: corpus_ref {cr!r} is not a YYYY-MM-DD snapshot date")

    return v


def validate_or_halt(manifest, label: str = "manifest") -> dict:
    v = validate_manifest(manifest, label)
    if v:
        fc.halt("invalid authority manifest — refusing to proceed:\n  " + "\n  ".join(v))
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


def load_manifest(path: Path = None):
    """Returns (manifest_or_None, violations). A MISSING manifest is not an
    error -- it is AUTHORITY_NOT_INITIALIZED. A malformed one is fatal and must
    never degrade into 'go find the newest remote object'."""
    path = Path(path) if path is not None else MANIFEST_PATH
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


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
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


def verify_or_halt(expected_sha: str, expected_size: int, target) -> None:
    ok, reason = verify_exact(expected_sha, expected_size, target)
    if not ok:
        fc.halt(f"byte verification FAILED — {reason}")


# ---------------------------------------------------------------------------
# E. transport -- narrow by design (P3 §8, §11)
# ---------------------------------------------------------------------------

class TransportError(RuntimeError):
    pass


def _forbidden_fetch_destinations() -> set:
    """Paths a staging fetch may never target. TWO INDEPENDENT ARMS.

    Arm 1 is the rebindable `OPERATIONAL_CODEBOOK_PATH`, which exists so NC20
    can exercise the RULE against a decoy instead of naming the live file.
    Arm 2 is `_IMMOVABLE_FORBIDDEN_DESTINATIONS`, captured at import and
    consulted by nothing else, so the real codebook stays refused even when arm
    1 has been rigged away.

    A guard whose only arm is the one the tests rebind is a guard that is absent
    during exactly the runs that matter -- which is how the 2026-08-14 incident
    happened, and the reason this function exists rather than an `==`."""
    return set(_IMMOVABLE_FORBIDDEN_DESTINATIONS) | {Path(OPERATIONAL_CODEBOOK_PATH).resolve()}


def _refuse_operational_destination(dest: Path) -> None:
    if Path(dest).resolve() in _forbidden_fetch_destinations():
        raise TransportError(
            f"REFUSED: {dest} is the OPERATIONAL codebook. get_verified stages and "
            f"verifies; it does not install. Fetch to a temporary path, verify, "
            f"validate, then install atomically (P3 §7).")


def _default_runner(argv: list) -> tuple:
    """(returncode, stdout, stderr). The ONLY place a subprocess is spawned."""
    proc = subprocess.run(argv, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


class RcloneTransport:
    """Exact-key object transport. No list-newest, no discover-latest, no
    prune, no delete, no overwrite, no mutable-pointer write -- those verbs do
    not exist on this class, so authority selection cannot accidentally reach
    one.

    `runner` is injectable so every failure mode below is testable offline; the
    selftests never touch the network."""

    def __init__(self, remote: str, bucket: str = AUTHORITY_BUCKET, runner=None):
        if not remote or ":" in remote:
            raise TransportError(
                f"remote {remote!r} must be a bare rclone remote NAME (no colon); "
                f"it is local configuration, never part of authority identity")
        self.remote = remote
        self.bucket = bucket
        self._run = runner or _default_runner

    # LAW B: every argv carries --s3-no-check-bucket. Without it a bucket-scoped
    # credential 403s on CreateBucket BEFORE the real operation, and the failure
    # reads exactly like "this credential cannot write".
    #
    # `conditional_create` adds the atomic create-only precondition. Proven
    # live against R2 with rclone v1.74.3: a PUT to an occupied key returns
    # 412 PreconditionFailed and does not modify the occupant.
    def _argv(self, *args: str, conditional_create: bool = False) -> list:
        argv = ["rclone", *args, "--s3-no-check-bucket"]
        if conditional_create:
            argv += [
                "--header-upload", CONDITIONAL_CREATE_HEADER,
                # MANDATORY, and measured: without it rclone compares size and
                # modtime itself, logs `Unchanged skipping`, and returns exit 0
                # having issued NO PutObject -- so the server precondition never
                # runs and the "atomic create" is atomic in name only.
                "--ignore-times",
                # A 412 is terminal. Retrying it produces three identical errors
                # and cannot succeed.
                "--retries", "1",
                # Stay on the single-PUT path the 412 was proven for.
                "--s3-upload-cutoff", SINGLE_PUT_CUTOFF,
            ]
        return argv

    @staticmethod
    def _is_precondition_failure(rc: int, stderr: str) -> bool:
        """Did the REMOTE reject this write because the key already existed?
        Keyed on the S3 error name and status, never on prose alone, and tested
        against `MEASURED_412_STDERR` -- the verbatim live response, not a
        remembered paraphrase of it."""
        if rc == 0:
            return False
        blob = stderr or ""
        return ("PreconditionFailed" in blob) or ("StatusCode: 412" in blob)

    def _remote_path(self, key: str) -> str:
        if not key or key.startswith("/") or ".." in key.split("/"):
            raise TransportError(f"refusing unsafe object key {key!r}")
        return f"{self.remote}:{self.bucket}/{key}"

    @staticmethod
    def _redact(text: str) -> str:
        """Keep stderr useful for diagnosis without leaking credentials."""
        if not text:
            return ""
        text = re.sub(r"https://[0-9a-f]{8,}\.r2\.cloudflarestorage\.com",
                      "https://<ACCOUNT-ID>.r2.cloudflarestorage.com", text)
        text = re.sub(r"(?i)(access_key_id|secret_access_key|authorization|x-amz-signature)"
                      r"\s*[:=]\s*\S+", r"\1=<REDACTED>", text)
        return text.strip()[:2000]

    def stat(self, key: str):
        """Exact-key existence/metadata, or None. NOT a listing: it names one
        key and cannot enumerate. `lsjson` of a missing key returns `[]` at
        exit 0 (LAW A), so an empty result is absence, never success."""
        argv = self._argv("lsjson", self._remote_path(key))
        rc, out, err = self._run(argv)
        if rc != 0:
            raise TransportError(f"rclone lsjson failed for {key!r}: {self._redact(err)}")
        try:
            rows = json.loads(out or "[]")
        except json.JSONDecodeError:
            raise TransportError(f"rclone lsjson returned unparseable JSON for {key!r}")
        if not rows:
            return None
        if len(rows) != 1:
            raise TransportError(
                f"exact key {key!r} matched {len(rows)} rows — refusing an ambiguous stat")
        row = rows[0]
        return {"size": row.get("Size"), "name": row.get("Name")}

    def get_verified(self, key: str, dest: Path, expected_sha: str, expected_size: int) -> Path:
        """Fetch an exact key to a STAGING destination and PROVE the bytes.

        RESTORE BOUNDARY (P3 §7): `dest` is scratch/staging, never the live
        codebook. This method DELETES `dest` before fetching, so aiming it at
        the operational copy would destroy it before the remote bytes are
        verified -- exactly the failure it must not enable. A future restore
        command therefore: fetch to staging -> verify exact bytes -> validate
        the codebook -> only then install atomically over the live file.
        Never returns on failure."""
        dest = Path(dest)
        _refuse_operational_destination(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            dest.unlink()  # a stale file must not be mistaken for a fetch
        self._fetch_raw(key, dest)
        ok, reason = verify_exact(expected_sha, expected_size, dest)
        if not ok:
            raise TransportError(f"fetched {key!r} but verification FAILED — {reason}")
        return dest

    def _fetch_raw(self, key: str, dest: Path) -> Path:
        """Transport only: land the object's bytes at `dest` or raise.

        Split out of `get_verified` so a TRANSPORT failure and a CONTENT
        mismatch are distinguishable by the caller. Collapsing them is what made
        `_occupant_matches` report an unreachable remote as an immutability
        violation -- a wrong diagnosis on a correct halt."""
        argv = self._argv("copyto", self._remote_path(key), str(dest))
        rc, out, err = self._run(argv)
        if rc != 0:
            raise TransportError(f"rclone copyto failed for {key!r}: {self._redact(err)}")
        # LAW A: exit 0 proves nothing. copyto of a MISSING object returns 0 and
        # creates no file -- so existence is asserted here, not assumed.
        if not dest.exists():
            raise TransportError(
                f"transport returned 0 but {dest} does not exist — the object {key!r} "
                f"is missing. An exit code is not object integrity (LAW A).")
        return dest

    # Occupant states. THREE, not two: "I could not find out" is a distinct
    # answer from "it differs", and publishing must halt differently on each.
    OCCUPANT_MATCH = "match"
    OCCUPANT_DIFFERS = "differs"
    OCCUPANT_UNREACHABLE = "unreachable"

    def _occupant_state(self, key: str, expected_sha: str, expected_size: int) -> tuple:
        """(state, detail). Does the object at `key` hold exactly the expected
        bytes? Answered by REMOTE READBACK -- never by the listed size, and
        never by an ETag (R2 multipart ETags are not plain MD5)."""
        with tempfile.TemporaryDirectory() as td:
            probe = Path(td) / "occupant"
            try:
                self._fetch_raw(key, probe)
            except TransportError as e:
                return self.OCCUPANT_UNREACHABLE, str(e)
            ok, reason = verify_exact(expected_sha, expected_size, probe)
            return (self.OCCUPANT_MATCH if ok else self.OCCUPANT_DIFFERS), reason

    def put_immutable(self, key: str, src: Path, expected_sha: str, expected_size: int) -> str:
        """Immutable publication (P3 §13, LAW C). The create is ATOMIC.

            destination absent                  -> conditional create-only PUT
            destination holds IDENTICAL bytes   -> 'already-present' (idempotent)
            destination holds DIFFERENT bytes   -> HALT, never overwrite
            lost the create race, same bytes    -> 'already-present-raced'
            lost the create race, other bytes   -> HALT

        The pre-read exists ONLY for idempotency semantics; safety comes from
        the remote precondition, because a pre-read cannot close the window
        between itself and the PUT. There is no unconditional-overwrite path in
        this method -- not as a fallback, not as a retry. An occupant that
        cannot be READ is its own outcome and halts on its own terms: "I could
        not find out" must never be reported as "it differs"."""
        src = Path(src)

        # The 412 was proven for single-part PutObject only. A payload that
        # would take the multipart path leaves the measured ground entirely.
        # Checked FIRST, on the declared size: it is a refusal, so it costs
        # nothing to reach, and it does not require hashing a huge file to
        # decline one. A size that lies small is still caught by verify_exact.
        if isinstance(expected_size, int) and not isinstance(expected_size, bool) \
                and expected_size >= SINGLE_PUT_LIMIT_BYTES:
            raise TransportError(
                f"REFUSED: payload is {expected_size} bytes, at or above the single-PUT "
                f"cutoff {SINGLE_PUT_LIMIT_BYTES} ({SINGLE_PUT_CUTOFF}). The create-only "
                f"precondition was measured against PutObject; its behaviour on "
                f"CreateMultipartUpload is UNPROVEN here, and an unproven atomic create is "
                f"not an atomic create.")

        ok, reason = verify_exact(expected_sha, expected_size, src)
        if not ok:
            raise TransportError(f"refusing to publish unverified local bytes — {reason}")

        # Pre-read: idempotency only.
        if self.stat(key) is not None:
            state, detail = self._occupant_state(key, expected_sha, expected_size)
            if state == self.OCCUPANT_MATCH:
                return "already-present"
            if state == self.OCCUPANT_UNREACHABLE:
                raise TransportError(
                    f"OCCUPANT UNREADABLE: key {key!r} exists but its bytes could not be "
                    f"read back, so whether publishing would overwrite a DIFFERENT object "
                    f"is unknown — {detail}. Refusing to publish on an unknown; this is "
                    f"not the same finding as an immutability violation.")
            raise TransportError(
                f"IMMUTABILITY VIOLATION REFUSED: key {key!r} is already occupied by bytes "
                f"that are NOT the payload being published (expected sha {expected_sha}, "
                f"size {expected_size}). Publishing would overwrite an existing object.")

        # Atomic create-only. If another writer won the race between the stat
        # above and this PUT, the SERVER rejects us with 412 -- we never find
        # out by overwriting them.
        argv = self._argv("copyto", str(src), self._remote_path(key), conditional_create=True)
        rc, out, err = self._run(argv)

        if self._is_precondition_failure(rc, err):
            # Lost the race. Resolve by reading what actually landed. Converging
            # on identical bytes is success; anything else halts.
            state, detail = self._occupant_state(key, expected_sha, expected_size)
            if state == self.OCCUPANT_MATCH:
                return "already-present-raced"
            if state == self.OCCUPANT_UNREACHABLE:
                raise TransportError(
                    f"LOST THE CREATE RACE AND CANNOT READ THE WINNER: the conditional create "
                    f"for {key!r} was rejected (412 PreconditionFailed), and the object now "
                    f"there could not be read back — {detail}. Not retried unconditionally.")
            raise TransportError(
                f"IMMUTABLE-KEY COLLISION: the conditional create for {key!r} was rejected "
                f"(412 PreconditionFailed) because another writer created that key first, "
                f"and the object now there is NOT the payload being published (expected sha "
                f"{expected_sha}, size {expected_size}). Refusing to overwrite; this is not "
                f"retried unconditionally.")
        if rc != 0:
            raise TransportError(f"rclone copyto (upload) failed for {key!r}: {self._redact(err)}")

        # LAW A, one level deeper: rc 0 does not prove a PUT was issued -- rclone
        # can skip on its own size+modtime check. The readback is what proves the
        # remote holds these exact bytes, and it is not optional.
        with tempfile.TemporaryDirectory() as td:
            self.get_verified(key, Path(td) / "readback", expected_sha, expected_size)
        return "uploaded"


# ---------------------------------------------------------------------------
# D. local status (P3 §10) -- READ ONLY, mutates nothing
# ---------------------------------------------------------------------------

STATE_NOT_INITIALIZED = "AUTHORITY_NOT_INITIALIZED"
STATE_LOCAL_MATCHES = "LOCAL_MATCHES_AUTHORITY"
STATE_MISMATCH = "LOCAL_CANDIDATE_AUTHORITY_MISMATCH"
STATE_MANIFEST_INVALID = "MANIFEST_INVALID"
STATE_UNVERIFIABLE = "AUTHORITY_UNVERIFIABLE"
STATE_NO_LOCAL = "NO_LOCAL_CODEBOOK"


def describe_local(path: Path = None) -> dict:
    """Facts about the local codebook. Derived, never carried forward."""
    path = Path(path) if path is not None else fcb.CODEBOOK_PATH
    if not path.exists():
        return {"present": False, "path": str(path)}
    try:
        cb = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        # Halt-loudly: a local codebook that will not parse is a real emergency,
        # and reporting it as "no local codebook" would understate it.
        fc.halt(f"{path}: local codebook is not parseable JSON ({e.__class__.__name__}: {e}) "
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
# manifest selects. A structurally perfect manifest can still lie. These two
# functions are the truth boundary -- the eventual promotion command builds the
# facts with `derive_manifest_facts` (from the candidate bytes) instead of
# accepting caller prose, and `compare_manifest_to_codebook` is the check that
# catches a manifest whose numbers do not describe its own payload.

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


def derive_manifest_facts(codebook_path: Path = None) -> dict:
    """Every codebook-describing manifest field, computed FROM the codebook.

    `corpus_ref` is deliberately not derived here: it comes from
    `foundry_codebook.corpus_ref_current()`, which reads the shipped artifact
    manifest rather than the codebook, and reading it has a halt condition of
    its own. The promotion command supplies it; this function stays pure."""
    local = describe_local(codebook_path)
    if not local.get("present"):
        fc.halt(f"{local.get('path')} not found — cannot derive manifest facts from a "
                f"codebook that does not exist")
    return {f: local[f] for f in DERIVED_FIELDS}


def build_manifest(snapshot_id: str, created_utc: str, mutation_review_id: str,
                   corpus_ref: str, previous_snapshot_hash, codebook_path: Path = None,
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
        fc.halt("build_manifest produced a manifest that does not validate — refusing to "
                "return it:\n  " + "\n  ".join(v))
    return {f: manifest[f] for f in MANIFEST_FIELDS}


def compare_manifest_to_codebook(manifest: dict, codebook_path: Path = None) -> list:
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


def describe_candidate(candidate: dict, transport: "RcloneTransport" = None) -> dict:
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
        "violations": validate_manifest(candidate, "candidate manifest"),
    }
    if transport is not None:
        try:
            meta = transport.stat(candidate["object_path"])
        except TransportError as e:
            out["remote"] = f"unreachable: {e}"
        else:
            out["remote"] = "absent" if meta is None else f"present, size={meta.get('size')}"
    return out


def status(manifest_path: Path = None, codebook_path: Path = None,
           transport: "RcloneTransport" = None, candidate: dict = None) -> dict:
    """Read-only. Distinguishes states A-E and NEVER repairs, publishes,
    overwrites or falls back to a listing."""
    manifest, violations = load_manifest(manifest_path)
    local = describe_local(codebook_path)

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
        except TransportError as e:
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


# ---------------------------------------------------------------------------
# H. restore (P3 §7) -- THE ORDER IS THE SAFETY PROPERTY
# ---------------------------------------------------------------------------
#
#     remote object -> STAGING -> exact sha+size -> codebook validation
#                   -> atomic install
#
# and never remote -> operational -> verify afterward. The 2026-08-14 incident
# was that second shape executed by accident: a staging fetch was pointed at the
# live codebook, and because the fetch unlinks its destination first, the file
# was destroyed before any byte was verified. Each step below therefore records
# itself in a TRACE, and the trace is asserted -- an ordering that is only
# documented is an ordering nobody checks.

RESTORE_STEPS = ("fetch", "verify", "validate", "install")


class RestoreError(RuntimeError):
    pass


def validate_codebook_payload(path: Path, manifest: dict) -> dict:
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
    if cb.get("schema") != fcb.SCHEMA_V2:
        raise RestoreError(
            f"staged codebook schema is {cb.get('schema')!r}, expected {fcb.SCHEMA_V2!r}. "
            f"Refusing to install an artifact this reader cannot claim to understand.")

    # The repository's own linter, not a second opinion invented here. It RAISES
    # LintError and returns stats on success -- and `lint_or_halt` is deliberately
    # not used, because a restore must raise a catchable error its caller can
    # report, not call sys.exit from inside a library path.
    try:
        stats = fcb.lint(cb, f"restored codebook ({path})")
    except fcb.LintError as e:
        raise RestoreError(f"staged codebook fails lint — {e}")

    mismatches = compare_manifest_to_codebook(manifest, path)
    if mismatches:
        raise RestoreError(
            "staged codebook does not match the manifest that selected it:\n  "
            + "\n  ".join(mismatches) + "\nRefusing to install.")
    return {"axes": len(cb["axes"]), "lint": stats}


def install_atomic(staged: Path, dest: Path, expected_sha: str, expected_size: int,
                   replace_existing: bool = False) -> str:
    """Install VERIFIED staged bytes at `dest` atomically. Returns dest sha.

    Re-verifies the staged bytes immediately before the rename: this function is
    the last thing between a candidate and an operational file, so it does not
    take a caller's word that verification happened earlier. The write is
    temp+fsync+os.replace within the destination directory, so `dest` is never
    observed half-written and a crash leaves the previous file intact."""
    staged, dest = Path(staged), Path(dest)
    ok, reason = verify_exact(expected_sha, expected_size, staged)
    if not ok:
        raise RestoreError(f"REFUSING TO INSTALL unverified bytes — {reason}")

    if dest.exists():
        current = sha256_of_file(dest)
        if current == expected_sha:
            return current                      # already installed; idempotent
        if not replace_existing:
            raise RestoreError(
                f"{dest} already exists with different bytes (sha {current}). Refusing to "
                f"replace an existing codebook without an explicit instruction; a restore "
                f"that silently overwrites is the incident shape.")
        fcb.backup_codebook("pre-restore-install", path=dest)

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".restore-tmp")
    shutil.copyfile(staged, tmp)
    with open(tmp, "rb") as f:
        os.fsync(f.fileno())
    ok, reason = verify_exact(expected_sha, expected_size, tmp)
    if not ok:
        tmp.unlink(missing_ok=True)
        raise RestoreError(f"staged->temp copy did not reproduce the bytes — {reason}")
    os.replace(tmp, dest)
    final = sha256_of_file(dest)
    if final != expected_sha:
        raise RestoreError(
            f"post-install sha {final} != expected {expected_sha} — filesystem-level "
            f"corruption; do not trust {dest}")
    return final


def restore_snapshot(manifest: dict, transport: "RcloneTransport", staging_dir: Path,
                     install_to: Path, replace_existing: bool = False) -> dict:
    """The whole restore law, in order, with the order recorded and asserted.

    `install_to` is REQUIRED and explicit. There is no default that quietly
    resolves to the operational codebook."""
    validate_or_halt(manifest, "restore manifest")
    staging_dir, install_to = Path(staging_dir), Path(install_to)
    staged = staging_dir / "codebook.staged.json"

    if staged.resolve() == install_to.resolve():
        raise RestoreError(
            "staging path and install destination are the same file — the staging step "
            "exists precisely so the destination is not written until the bytes are proven")

    trace = []
    key, sha, size = manifest["object_path"], manifest["sha256"], manifest["byte_size"]

    # 1. FETCH to staging. get_verified categorically refuses the operational
    #    codebook as a destination, on an arm no rig can rebind.
    staging_dir.mkdir(parents=True, exist_ok=True)
    transport.get_verified(key, staged, sha, size)
    trace.append("fetch")

    # 2. VERIFY the staged bytes independently of the fetch that produced them.
    ok, reason = verify_exact(sha, size, staged)
    if not ok:
        raise RestoreError(f"staged bytes failed verification — {reason}")
    trace.append("verify")

    # 3. VALIDATE that they are a codebook, and the one the manifest describes.
    payload = validate_codebook_payload(staged, manifest)
    trace.append("validate")

    # 4. INSTALL atomically. Unreachable unless 1-3 all passed, because each of
    #    them raises rather than returning a status nobody reads.
    installed_sha = install_atomic(staged, install_to, sha, size, replace_existing)
    trace.append("install")

    if trace != list(RESTORE_STEPS):
        raise RestoreError(f"restore executed steps {trace}, expected {list(RESTORE_STEPS)}")
    return {"trace": trace, "installed": str(install_to), "sha256": installed_sha,
            "byte_size": size, "staged": str(staged), "payload": payload}


# ---------------------------------------------------------------------------
# F/G. selftests + negative controls (P3 §14)
# ---------------------------------------------------------------------------

FIXTURE_BYTES = b"foundry-authority-selftest\n"


def _valid_manifest(sha: str = None, size: int = None) -> dict:
    sha = sha or sha256_of_bytes(FIXTURE_BYTES)
    size = size if size is not None else len(FIXTURE_BYTES)
    return {
        "schema": SCHEMA,
        "snapshot_id": "selftest-0001",
        "bucket": AUTHORITY_BUCKET,
        "object_path": object_key_for(sha),
        "sha256": sha,
        "byte_size": size,
        "created_utc": "2026-08-14T00:00:00Z",
        "codebook_schema": fcb.SCHEMA_V2,
        "codebook_version": "0.7",
        "corpus_ref": "2026-07-05",
        "active_axis_count": 403,
        "assertion_count": 7930,
        "human_assertion_count": 4233,
        "rule_derived_assertion_count": 3697,
        "mutation_review_id": "selftest-fixture",
        "previous_snapshot_hash": None,
    }


class FakeRunner:
    """An in-memory rclone. Records every argv so command CONSTRUCTION is
    testable (NC12), lies the way real rclone lies (NC7), and honours the
    create-only precondition the way live R2 was measured to (NC15/NC16).

    `race_injects` = {key: bytes}. The bytes appear at that key immediately
    AFTER the first successful `lsjson` of it -- i.e. exactly in the window
    between the pre-read and the PUT, which is the TOCTOU window the
    conditional exists to close."""

    def __init__(self, objects=None, lie_on_get=False, race_injects=None):
        self.objects = dict(objects or {})
        self.calls = []
        self.lie_on_get = lie_on_get
        self.race_injects = dict(race_injects or {})

    def __call__(self, argv):
        self.calls.append(list(argv))
        verb = argv[1]
        if verb == "lsjson":
            key = self._key(argv[2])
            present = key in self.objects
            # The other writer lands here: after we observed absence, before we PUT.
            if key in self.race_injects:
                self.objects[key] = self.race_injects.pop(key)
            if not present:
                return 0, "[]", ""          # LAW A: missing key -> [] at exit 0
            data = self.objects[key]
            return 0, json.dumps([{"Path": key.split("/")[-1], "Name": key.split("/")[-1],
                                   "Size": len(data), "IsDir": False}]), ""
        if verb == "copyto":
            src, dst = argv[2], argv[3]
            if ":" in src:                   # download
                key = self._key(src)
                if self.lie_on_get or key not in self.objects:
                    return 0, "", ""         # LAW A: exit 0, no file created
                Path(dst).write_bytes(self.objects[key])
                return 0, "", ""
            key = self._key(dst)             # upload
            data = Path(src).read_bytes()
            conditional = CONDITIONAL_CREATE_HEADER in argv
            ignore_times = "--ignore-times" in argv
            # MEASURED 2026-08-14, and this branch is why `--ignore-times` is
            # mandatory: rclone compares size+modtime ITSELF, logs `Unchanged
            # skipping`, and returns exit 0 having issued NO PutObject -- so the
            # server precondition never runs. Modelled here so that deleting the
            # flag turns NC16/NC21 red instead of silently disarming the create.
            if key in self.objects and not ignore_times and self.objects[key] == data:
                return 0, MEASURED_SKIP_STDOUT, ""
            if conditional and key in self.objects:
                # Exactly what live R2 returned, measured 2026-08-14.
                return 1, "", MEASURED_412_STDERR
            self.objects[key] = data
            return 0, "", ""
        return 1, "", f"FakeRunner: unsupported verb {verb!r}"

    @staticmethod
    def _key(remote_path: str) -> str:
        return remote_path.split(":", 1)[1].split("/", 1)[1]


def _check(results: list, name: str, passed: bool, detail: str) -> None:
    results.append((name, passed, detail))


def selftest() -> int:
    r = []
    fixture_sha = sha256_of_bytes(FIXTURE_BYTES)
    fixture_size = len(FIXTURE_BYTES)

    # WHOLE-RUN CANARY. Every control below works on temp dirs and fake runners,
    # and that is asserted rather than assumed: the operational codebook's sha is
    # taken before the first control and compared after the last. On 2026-08-14 a
    # selftest run was the thing that destroyed this file; a suite that touches it
    # again fails loudly instead of being discovered by a red Gate 2 later.
    _canary_path = fcb.CODEBOOK_PATH.resolve()
    _canary_before = sha256_of_file(_canary_path) if _canary_path.exists() else "ABSENT"

    # NC1 — a valid manifest is accepted.
    v = validate_manifest(_valid_manifest())
    _check(r, "NC1  valid manifest accepted", v == [], f"violations={v}")

    # NC2 — malformed SHA rejected (four shapes, incl. uppercase and truncated).
    bad_shas = ["", "xyz", fixture_sha.upper(), fixture_sha[:63], fixture_sha + "a", None, 12345]
    nc2 = []
    for bad in bad_shas:
        m = _valid_manifest()
        m["sha256"] = bad
        nc2.append(bool(validate_manifest(m)))
    _check(r, "NC2  malformed sha256 rejected", all(nc2),
           f"{sum(nc2)}/{len(nc2)} rejected (incl. UPPERCASE and off-by-one length)")

    # NC3 — every required field, removed one at a time, is rejected.
    nc3 = []
    for field in MANIFEST_FIELDS:
        m = _valid_manifest()
        del m[field]
        nc3.append(bool(validate_manifest(m)))
    _check(r, "NC3  missing required field rejected", all(nc3),
           f"{sum(nc3)}/{len(MANIFEST_FIELDS)} fields fatal when absent")

    # NC4 — a single corrupted byte fails verification.
    corrupt = bytearray(FIXTURE_BYTES)
    corrupt[0] ^= 0x01
    ok4, why4 = verify_exact(fixture_sha, fixture_size, bytes(corrupt))
    _check(r, "NC4  single corrupted byte fails", not ok4, why4)

    # NC5 — same size, wrong content fails (size alone is never proof).
    same_size = bytes([b ^ 0xFF for b in FIXTURE_BYTES])
    ok5, why5 = verify_exact(fixture_sha, fixture_size, same_size)
    _check(r, "NC5  same-size wrong bytes fail", not ok5 and len(same_size) == fixture_size, why5)

    # NC6 — truncated fails.
    ok6, why6 = verify_exact(fixture_sha, fixture_size, FIXTURE_BYTES[:-1])
    _check(r, "NC6  truncated bytes fail", not ok6, why6)

    # NC6b — empty and missing fail.
    ok6b, _ = verify_exact(fixture_sha, fixture_size, b"")
    with tempfile.TemporaryDirectory() as td:
        ok6c, why6c = verify_exact(fixture_sha, fixture_size, Path(td) / "nope.json")
    _check(r, "NC6b empty and missing file fail", (not ok6b) and (not ok6c), why6c)

    # NC7 — transport returns 0 and creates NO file: must not become success.
    with tempfile.TemporaryDirectory() as td:
        key = object_key_for(fixture_sha)
        runner = FakeRunner(objects={key: FIXTURE_BYTES}, lie_on_get=True)
        t = RcloneTransport("fake-remote", runner=runner)
        try:
            t.get_verified(key, Path(td) / "out.json", fixture_sha, fixture_size)
            nc7, why7 = False, "get_verified RETURNED on a transport that produced no file"
        except TransportError as e:
            nc7, why7 = "does not exist" in str(e), str(e)[:130]
    _check(r, "NC7  exit-0 with no file is not success", nc7, why7)

    # NC8 — local != selected authority is REPORTED, not repaired.
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        mpath = td / "manifest.json"
        cbpath = td / "codebook.json"
        cb = {"schema": fcb.SCHEMA_V2, "version": "0.7",
              "axes": {"rule:x": {"status": "active", "members": [
                  {"oracle_id": "a", "assertions": [{"class": "human"}]}]}}}
        cbpath.write_text(json.dumps(cb), encoding="utf-8")
        local_sha_before = sha256_of_file(cbpath)
        m = _valid_manifest()  # selects the FIXTURE bytes, not this codebook
        mpath.write_text(serialize_manifest(m), encoding="utf-8")
        st = status(manifest_path=mpath, codebook_path=cbpath)
        unchanged = sha256_of_file(cbpath) == local_sha_before
        _check(r, "NC8  local/authority mismatch reported, not repaired",
               st["state"] == STATE_MISMATCH and unchanged,
               f"state={st['state']} local_file_unchanged={unchanged}")

    # NC9 — an invalid manifest never falls back to remote newest/listing.
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        mpath = td / "manifest.json"
        cbpath = td / "codebook.json"
        cbpath.write_text(json.dumps({"schema": fcb.SCHEMA_V2, "version": "0.7", "axes": {}}),
                          encoding="utf-8")
        broken = _valid_manifest()
        broken["sha256"] = "not-a-sha"
        mpath.write_text(json.dumps(broken), encoding="utf-8")
        runner = FakeRunner(objects={"foundry/codebook/sha256/" + ("f" * 64) + "/codebook.json":
                                     b"decoy-newest-object"})
        t = RcloneTransport("fake-remote", runner=runner)
        st = status(manifest_path=mpath, codebook_path=cbpath, transport=t)
        no_remote_calls = len(runner.calls) == 0
        _check(r, "NC9  invalid manifest never consults the remote",
               st["state"] == STATE_MANIFEST_INVALID and no_remote_calls,
               f"state={st['state']} rclone_calls={len(runner.calls)} (must be 0)")

    # NC10 — occupied key + DIFFERENT bytes: refuse to overwrite.
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        src = td / "payload.txt"
        src.write_bytes(FIXTURE_BYTES)
        key = object_key_for(fixture_sha)
        runner = FakeRunner(objects={key: b"SOMETHING ELSE ENTIRELY\n"})
        t = RcloneTransport("fake-remote", runner=runner)
        try:
            t.put_immutable(key, src, fixture_sha, fixture_size)
            nc10, why10 = False, "put_immutable OVERWROTE an occupied key"
        except TransportError as e:
            preserved = runner.objects[key] == b"SOMETHING ELSE ENTIRELY\n"
            nc10 = "IMMUTABILITY VIOLATION REFUSED" in str(e) and preserved
            why10 = f"refused, occupant preserved={preserved}"
    _check(r, "NC10 occupied key, different bytes -> refuse", nc10, why10)

    # NC11 — occupied key + IDENTICAL bytes: idempotent, not corruption.
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        src = td / "payload.txt"
        src.write_bytes(FIXTURE_BYTES)
        key = object_key_for(fixture_sha)
        runner = FakeRunner(objects={key: FIXTURE_BYTES})
        t = RcloneTransport("fake-remote", runner=runner)
        outcome = t.put_immutable(key, src, fixture_sha, fixture_size)
        uploads = [c for c in runner.calls if c[1] == "copyto" and ":" in c[3]]
        _check(r, "NC11 occupied key, identical bytes -> idempotent",
               outcome == "already-present" and not uploads,
               f"outcome={outcome!r} redundant_uploads={len(uploads)}")

    # NC11b — absent key: upload proceeds and is readback-verified.
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "payload.txt"
        src.write_bytes(FIXTURE_BYTES)
        key = object_key_for(fixture_sha)
        runner = FakeRunner()
        t = RcloneTransport("fake-remote", runner=runner)
        outcome = t.put_immutable(key, src, fixture_sha, fixture_size)
        _check(r, "NC11b absent key -> upload + readback", outcome == "uploaded",
               f"outcome={outcome!r} stored={key in runner.objects}")

    # NC15 — LOST THE CREATE RACE, DIFFERENT BYTES: halt, never overwrite.
    # stat says absent -> another writer creates other bytes -> conditional PUT
    # is refused 412 -> readback differs -> HALT.
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "payload.txt"
        src.write_bytes(FIXTURE_BYTES)
        key = object_key_for(fixture_sha)
        intruder = b"ANOTHER WRITER GOT HERE FIRST\n"
        runner = FakeRunner(race_injects={key: intruder})
        t = RcloneTransport("fake-remote", runner=runner)
        try:
            out = t.put_immutable(key, src, fixture_sha, fixture_size)
            nc15, why15 = False, f"returned {out!r} instead of halting on a lost race"
        except TransportError as e:
            preserved = runner.objects.get(key) == intruder
            nc15 = "IMMUTABLE-KEY COLLISION" in str(e) and preserved
            why15 = f"halted; intruder bytes preserved={preserved}"
    _check(r, "NC15 lost create race, different bytes -> HALT", nc15, why15)

    # NC16 — LOST THE CREATE RACE, IDENTICAL BYTES: converge, do not error.
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "payload.txt"
        src.write_bytes(FIXTURE_BYTES)
        key = object_key_for(fixture_sha)
        runner = FakeRunner(race_injects={key: FIXTURE_BYTES})
        t = RcloneTransport("fake-remote", runner=runner)
        outcome = t.put_immutable(key, src, fixture_sha, fixture_size)
        _check(r, "NC16 lost create race, identical bytes -> idempotent",
               outcome == "already-present-raced" and runner.objects[key] == FIXTURE_BYTES,
               f"outcome={outcome!r} (concurrent identical publication converges)")

    # NC17 — the create is CONDITIONAL. Every upload argv must carry the
    # precondition; without it NC15 degrades into a silent overwrite.
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "payload.txt"
        src.write_bytes(FIXTURE_BYTES)
        key = object_key_for(fixture_sha)
        runner = FakeRunner()
        t = RcloneTransport("fake-remote", runner=runner)
        t.put_immutable(key, src, fixture_sha, fixture_size)
        uploads = [c for c in runner.calls if c[1] == "copyto" and ":" in c[3]]
        unconditional = [c for c in uploads if CONDITIONAL_CREATE_HEADER not in c]
        _check(r, "NC17 every upload carries If-None-Match: * (atomic create)",
               uploads and not unconditional,
               f"{len(uploads)} upload(s), {len(unconditional)} unconditional")

    # NC12 — EVERY constructed argv carries --s3-no-check-bucket (LAW B).
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "payload.txt"
        src.write_bytes(FIXTURE_BYTES)
        key = object_key_for(fixture_sha)
        runner = FakeRunner()
        t = RcloneTransport("fake-remote", runner=runner)
        t.put_immutable(key, src, fixture_sha, fixture_size)
        t.stat(key)
        t.get_verified(key, Path(td) / "back.json", fixture_sha, fixture_size)
        missing = [c for c in runner.calls if "--s3-no-check-bucket" not in c]
        _check(r, "NC12 every argv carries --s3-no-check-bucket",
               runner.calls and not missing,
               f"{len(runner.calls)} rclone invocation(s), {len(missing)} without the flag")

    # NC13 — object_path must embed its own sha (content-addressing is checked,
    # not merely shaped) and a mutable-pointer key is refused outright.
    m = _valid_manifest()
    m["object_path"] = object_key_for("b" * 64)
    nc13a = bool(validate_manifest(m))
    m2 = _valid_manifest()
    m2["object_path"] = "foundry/codebook/latest.json"
    nc13b = any("mutable-pointer" in x for x in validate_manifest(m2))
    _check(r, "NC13 key must embed its sha; mutable key refused", nc13a and nc13b,
           f"wrong_hash_rejected={nc13a} latest.json_rejected={nc13b}")

    # NC14 — impossible count relationships rejected.
    m3 = _valid_manifest()
    m3["human_assertion_count"] = 5000
    m3["rule_derived_assertion_count"] = 5000   # 10,000 > 7,930
    nc14a = any("impossible" in x for x in validate_manifest(m3))
    m4 = _valid_manifest()
    m4["byte_size"] = True                      # bool is an int subclass
    nc14b = bool(validate_manifest(m4))
    m5 = _valid_manifest()
    m5["created_utc"] = "2026-13-45T99:99:99Z"
    nc14c = bool(validate_manifest(m5))
    _check(r, "NC14 impossible counts / bool size / bad timestamp rejected",
           nc14a and nc14b and nc14c,
           f"counts={nc14a} bool_size={nc14b} timestamp={nc14c}")

    # NC18 — GENESIS SEMANTICS (Captain ruling, 2026-08-14). The first manifest
    # carries null; every later one carries the previously selected snapshot's
    # sha256. No zero-hash, no self-hash, no empty string, no absent field.
    genesis = _valid_manifest()
    genesis["previous_snapshot_hash"] = None
    nc18_genesis = validate_manifest(genesis) == []

    later = _valid_manifest()
    later["previous_snapshot_hash"] = "a" * 64
    nc18_later = validate_manifest(later) == []

    nc18_bad = []
    for bad in ["0" * 64 + "0", "", "null", "None", ("A" * 64), "0x" + "0" * 62,
                123, ["a" * 64], fixture_sha[:63]]:
        m = _valid_manifest()
        m["previous_snapshot_hash"] = bad
        nc18_bad.append(bool(validate_manifest(m)))
    # A zero hash is 64 valid hex chars, so it is structurally legal and must be
    # rejected on MEANING: it is the invented genesis sentinel the ruling bans.
    m_zero = _valid_manifest()
    m_zero["previous_snapshot_hash"] = "0" * 64
    nc18_zero = any("all-zero" in x for x in validate_manifest(m_zero))
    m_self = _valid_manifest()
    m_self["previous_snapshot_hash"] = m_self["sha256"]
    nc18_self = bool(validate_manifest(m_self))
    _check(r, "NC18 genesis null ok; later hash ok; zero/self/malformed rejected",
           nc18_genesis and nc18_later and all(nc18_bad) and nc18_zero and nc18_self,
           f"genesis={nc18_genesis} later={nc18_later} malformed={sum(nc18_bad)}/{len(nc18_bad)} "
           f"zero_sentinel={nc18_zero} self={nc18_self}")

    # NC19 — METADATA TRUTH BOUNDARY (P3 §6). A manifest can be structurally
    # PERFECT and still lie about the bytes it selects. The structural
    # validator cannot see this; the codebook comparison can.
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        cbpath = td / "codebook.json"
        cb = {"schema": fcb.SCHEMA_V2, "version": "0.7", "axes": {
            "rule:a": {"status": "active", "members": [
                {"oracle_id": "x", "assertions": [{"class": "human"},
                                                  {"class": "rule-derived"}]}]},
            "rule:dead": {"status": "killed", "members": []}}}
        cbpath.write_text(json.dumps(cb), encoding="utf-8")

        honest = _valid_manifest(sha=sha256_of_file(cbpath), size=cbpath.stat().st_size)
        honest.update(derive_manifest_facts(cbpath))
        honest_ok = validate_manifest(honest) == [] and \
            compare_manifest_to_codebook(honest, cbpath) == []

        # Structurally valid, semantically WRONG: 7,930 assertions claimed over
        # a codebook holding 2. Every field is well-formed; the manifest lies.
        liar = dict(honest)
        liar["assertion_count"] = 7930
        liar_structural = validate_manifest(liar)          # must be EMPTY
        liar_semantic = compare_manifest_to_codebook(liar, cbpath)   # must catch it
        _check(r, "NC19 structurally-valid-but-wrong count caught by fact comparison",
               honest_ok and liar_structural == [] and any("assertion_count" in x
                                                           for x in liar_semantic),
               f"derived_manifest_clean={honest_ok} structural_blind={liar_structural == []} "
               f"semantic_caught={len(liar_semantic)}")

    # NC20 — RESTORE STAGING BOUNDARY (P3 §7). A staging fetch DELETES its
    # destination first, so aiming one at the live codebook would destroy the
    # operational copy before the remote bytes were ever verified.
    #
    # THIS CONTROL NEVER NAMES THE REAL FILE. An earlier version passed the
    # true OPERATIONAL_CODEBOOK_PATH, and on 2026-08-14 a rigging run that
    # disabled the guard turned this very control into the thing it guards
    # against: it overwrote the live codebook with fixture bytes. A negative
    # control must be safe when the guard it tests is ABSENT, because that is
    # precisely the condition it is designed to be run under. So the RULE is
    # rebound to a disposable path and the rule is what gets tested.
    with tempfile.TemporaryDirectory() as td:
        decoy = Path(td) / "pretend-operational-codebook.json"
        decoy.write_text('{"canary": "must survive"}', encoding="utf-8")
        real_path = globals()["OPERATIONAL_CODEBOOK_PATH"]
        globals()["OPERATIONAL_CODEBOOK_PATH"] = decoy.resolve()
        try:
            runner = FakeRunner(objects={object_key_for(fixture_sha): FIXTURE_BYTES})
            t = RcloneTransport("fake-remote", runner=runner)
            try:
                t.get_verified(object_key_for(fixture_sha), decoy, fixture_sha, fixture_size)
                nc20, why20 = False, "get_verified accepted the operational path as destination"
            except TransportError as e:
                nc20 = "OPERATIONAL codebook" in str(e)
                why20 = "refused the operational path as a fetch destination"
            survived = decoy.read_text(encoding="utf-8") == '{"canary": "must survive"}'
        finally:
            globals()["OPERATIONAL_CODEBOOK_PATH"] = real_path
    _check(r, "NC20 fetch refuses the operational codebook as destination",
           nc20 and survived and not runner.calls,
           f"{why20}; canary_intact={survived}; rclone_calls={len(runner.calls)} (must be 0)")

    # NC21 — `--ignore-times` IS LOAD-BEARING, and this control rigs it away to
    # prove that. Measured 2026-08-14: without it rclone answers the existence
    # question from a local size+modtime comparison, logs `Unchanged skipping`,
    # returns exit 0, and never issues the PutObject the precondition rides on.
    # Asserting the flag is present is half; the other half is showing that a
    # transport WITHOUT it produces the wrong answer on the same scenario.
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "payload.txt"
        src.write_bytes(FIXTURE_BYTES)
        key = object_key_for(fixture_sha)

        runner = FakeRunner()
        t = RcloneTransport("fake-remote", runner=runner)
        t.put_immutable(key, src, fixture_sha, fixture_size)
        uploads = [c for c in runner.calls if c[1] == "copyto" and ":" in c[3]]
        flagged = uploads and all("--ignore-times" in c for c in uploads)

        class _DisarmedTransport(RcloneTransport):
            """The pre-fix behaviour, reconstructed on purpose."""
            def _argv(self, *args, conditional_create=False):
                argv = ["rclone", *args, "--s3-no-check-bucket"]
                if conditional_create:
                    argv += ["--header-upload", CONDITIONAL_CREATE_HEADER]
                return argv

        disarmed_runner = FakeRunner(race_injects={key: FIXTURE_BYTES})
        d = _DisarmedTransport("fake-remote", runner=disarmed_runner)
        disarmed_outcome = d.put_immutable(key, src, fixture_sha, fixture_size)
        # The armed transport calls this exact scenario a lost race (NC16). The
        # disarmed one never reaches the server at all and reports an upload.
        rigged_red = disarmed_outcome != "already-present-raced"
        _check(r, "NC21 --ignore-times present, and proven load-bearing by rigging it away",
               flagged and rigged_red,
               f"armed_uploads_flagged={flagged}; disarmed transport returned "
               f"{disarmed_outcome!r} instead of 'already-present-raced'")

    # NC22 — THE GUARD SURVIVES ITS OWN RIGGING (the incident's structural half).
    #
    # This control names the REAL codebook path, and it is safe to do so because
    # it exercises the PREDICATE, which performs no I/O: `_refuse_operational_
    # destination` either raises or returns, and never opens, unlinks or writes
    # anything. No fetch is issued with a real path anywhere in this file.
    real_cb = fcb.CODEBOOK_PATH.resolve()
    cb_sha_before_nc22 = sha256_of_file(real_cb) if real_cb.exists() else None
    with tempfile.TemporaryDirectory() as td:
        decoy = Path(td) / "decoy.json"
        decoy.write_text("{}", encoding="utf-8")
        saved = globals()["OPERATIONAL_CODEBOOK_PATH"]
        globals()["OPERATIONAL_CODEBOOK_PATH"] = decoy.resolve()   # rig arm 1 away
        try:
            still_forbidden = real_cb in _forbidden_fetch_destinations()
            try:
                _refuse_operational_destination(real_cb)
                refused = False
            except TransportError:
                refused = True
        finally:
            globals()["OPERATIONAL_CODEBOOK_PATH"] = saved
    cb_sha_after_nc22 = sha256_of_file(real_cb) if real_cb.exists() else None
    _check(r, "NC22 real codebook still refused when the rebindable arm is rigged away",
           still_forbidden and refused and cb_sha_before_nc22 == cb_sha_after_nc22,
           f"in_forbidden_set={still_forbidden} refused={refused} "
           f"codebook_untouched={cb_sha_before_nc22 == cb_sha_after_nc22}")

    # NC23 — "I COULD NOT FIND OUT" IS NOT "IT DIFFERS". An occupied key whose
    # bytes cannot be read back must halt as UNREADABLE, not be reported as an
    # immutability violation: the second is a claim about the object, and the
    # transport does not have the evidence to make it.
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "payload.txt"
        src.write_bytes(FIXTURE_BYTES)
        key = object_key_for(fixture_sha)
        runner = FakeRunner(objects={key: FIXTURE_BYTES}, lie_on_get=True)
        t = RcloneTransport("fake-remote", runner=runner)
        try:
            out = t.put_immutable(key, src, fixture_sha, fixture_size)
            nc23, why23 = False, f"returned {out!r} on an unreadable occupant"
        except TransportError as e:
            nc23 = "OCCUPANT UNREADABLE" in str(e)
            why23 = ("halted as UNREADABLE, not as a violation"
                     if nc23 else f"wrong diagnosis: {str(e)[:90]}")
        preserved = runner.objects[key] == FIXTURE_BYTES
    _check(r, "NC23 unreadable occupant halts as unknown, not as a violation",
           nc23 and preserved, f"{why23}; occupant_preserved={preserved}")

    # NC24 — SUCCESSION IS CHECKED AGAINST THE PRIOR MANIFEST. Shape is not
    # succession: "a"*64 is well-formed and names nothing.
    prior = _valid_manifest(sha="c" * 64, size=999)
    prior["snapshot_id"] = "prior-0001"

    ok_succ = _valid_manifest()
    ok_succ["snapshot_id"] = "next-0002"
    ok_succ["previous_snapshot_hash"] = "c" * 64

    genesis_no_prior = validate_succession(_valid_manifest(), None) == []
    genesis_with_prior = any("second genesis" in x
                             for x in validate_succession(_valid_manifest(), prior))
    correct_link = validate_succession(ok_succ, prior) == []

    wrong_link = _valid_manifest()
    wrong_link["snapshot_id"] = "next-0002"
    wrong_link["previous_snapshot_hash"] = "a" * 64          # well-formed, wrong
    wrong_caught = any("does not match the sha256 of the prior" in x
                       for x in validate_succession(wrong_link, prior))

    claims_prior_without_one = any("NO prior tracked manifest" in x
                                   for x in validate_succession(ok_succ, None))

    same_bytes = dict(ok_succ)
    same_bytes["sha256"] = prior["sha256"]
    same_bytes["object_path"] = object_key_for(prior["sha256"])
    same_caught = any("cannot succeed themselves" in x
                      for x in validate_succession(same_bytes, prior))

    broken_prior = dict(prior)
    broken_prior["sha256"] = "not-a-sha"
    prior_invalid_caught = any("PRIOR manifest is itself invalid" in x
                               for x in validate_succession(ok_succ, broken_prior))
    # It takes the predecessor as an ARGUMENT and owns no transport, so
    # "newest remote object" is unavailable to it rather than merely forbidden.
    no_transport = "transport" not in validate_succession.__code__.co_varnames
    _check(r, "NC24 succession validated against the prior manifest, never prose/newest",
           genesis_no_prior and genesis_with_prior and correct_link and wrong_caught
           and claims_prior_without_one and same_caught and prior_invalid_caught
           and no_transport,
           f"genesis_ok={genesis_no_prior} second_genesis_refused={genesis_with_prior} "
           f"correct={correct_link} wrong_hash_caught={wrong_caught} "
           f"orphan_claim_caught={claims_prior_without_one} self_succession={same_caught} "
           f"invalid_prior={prior_invalid_caught} no_transport_param={no_transport}")

    # NC25 — the 412 was proven for PutObject. A multipart-sized payload is
    # REFUSED rather than assumed, and refused before any remote contact.
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "payload.txt"
        src.write_bytes(FIXTURE_BYTES)
        runner = FakeRunner()
        t = RcloneTransport("fake-remote", runner=runner)
        try:
            t.put_immutable(object_key_for(fixture_sha), src, fixture_sha,
                            SINGLE_PUT_LIMIT_BYTES)
            nc25, why25 = False, "accepted a payload at the multipart cutoff"
        except TransportError as e:
            nc25 = "UNPROVEN" in str(e) and not runner.calls
            why25 = f"refused before any rclone call (calls={len(runner.calls)})"
    _check(r, "NC25 multipart-sized payload refused as unproven", nc25, why25)

    # NC26 — the 412 detector is tested against the VERBATIM live response, not
    # a paraphrase written from memory. Also: rc 0 is never a precondition
    # failure, and an unrelated error is not read as one.
    nc26_real = RcloneTransport._is_precondition_failure(1, MEASURED_412_STDERR)
    nc26_rc0 = not RcloneTransport._is_precondition_failure(0, MEASURED_412_STDERR)
    nc26_other = not RcloneTransport._is_precondition_failure(
        1, "operation error S3: PutObject, https response error StatusCode: 403, "
           "api error AccessDenied")
    nc26_skip = not RcloneTransport._is_precondition_failure(0, MEASURED_SKIP_STDOUT)
    _check(r, "NC26 412 detector matches the verbatim measured stderr",
           nc26_real and nc26_rc0 and nc26_other and nc26_skip,
           f"live_412={nc26_real} rc0_not_412={nc26_rc0} 403_not_412={nc26_other} "
           f"skip_not_412={nc26_skip}")

    # NC27 — build_manifest DERIVES the codebook-describing fields from the
    # candidate bytes. There is no parameter to pass a wrong count through, and
    # the object_path's embedded hash comes from the file rather than a caller.
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        cbpath = td / "codebook.json"
        cb = {"schema": fcb.SCHEMA_V2, "version": "0.7", "axes": {
            "rule:a": {"status": "active", "members": [
                {"oracle_id": "x", "assertions": [{"class": "human"},
                                                  {"class": "rule-derived"}]}]}}}
        cbpath.write_text(json.dumps(cb), encoding="utf-8")
        built = build_manifest(snapshot_id="built-0001",
                               created_utc="2026-08-14T12:00:00Z",
                               mutation_review_id="selftest-build",
                               corpus_ref="2026-07-04",
                               previous_snapshot_hash=None,
                               codebook_path=cbpath)
        real_sha = sha256_of_file(cbpath)
        derived_ok = (built["sha256"] == real_sha
                      and built["byte_size"] == cbpath.stat().st_size
                      and built["object_path"] == object_key_for(real_sha)
                      and built["assertion_count"] == 2
                      and built["human_assertion_count"] == 1
                      and validate_manifest(built) == []
                      and compare_manifest_to_codebook(built, cbpath) == [])
        # No caller-supplied override exists for any derived field.
        import inspect as _inspect
        params = set(_inspect.signature(build_manifest).parameters)
        no_derived_params = not (params & set(DERIVED_FIELDS))
        # And it refuses to return a manifest whose succession is wrong.
        prior_m = _valid_manifest(sha="d" * 64, size=42)
        try:
            build_manifest(snapshot_id="built-0002",
                           created_utc="2026-08-14T12:00:00Z",
                           mutation_review_id="selftest-build",
                           corpus_ref="2026-07-04",
                           previous_snapshot_hash=None,   # genesis despite a prior
                           codebook_path=cbpath, prior=prior_m)
            succ_refused = False
        except SystemExit:
            succ_refused = True
    _check(r, "NC27 manifest facts derived from the bytes; no override, succession enforced",
           derived_ok and no_derived_params and succ_refused,
           f"derived={derived_ok} no_derived_params={no_derived_params} "
           f"bad_succession_halted={succ_refused}")

    # ---- RESTORE CONTROLS (Tranche 2A). The property under test is that
    # ---- INSTALL is unreachable unless fetch, verify and validate all passed.
    # ---- Each control asserts the destination was never created, which is a
    # ---- stronger statement than "an error was raised".
    def _restore_fixture(td):
        """A real little codebook, its manifest, and a runner serving it.

        DERIVED FROM THE RATIFIED ARTIFACT, NEVER HAND-BUILT. A hand-written
        codebook was tried first and could not survive `fcb.lint` -- it was
        missing `source_ref` on its assertions -- which is the house rule
        arriving on schedule: build the fixture from ratified artifacts, because
        a hand-built one encodes what the author remembers of the schema. This
        takes the smallest active axis out of the live codebook, so the fixture
        is schema-correct by construction and stays correct as the schema moves.
        """
        live = fcb.load_codebook()
        active = [(s, e) for s, e in live["axes"].items() if e.get("status") == "active"]
        slug, entry = min(active, key=lambda kv: len(kv[1].get("members") or []))
        mini = {k: v for k, v in live.items() if k != "axes"}
        mini["axes"] = {slug: entry}
        cbpath = Path(td) / "source-codebook.json"
        cbpath.write_text(fcb._serialize(mini), encoding="utf-8")
        m = build_manifest(snapshot_id="restore-fixture",
                           created_utc="2026-08-14T12:00:00Z",
                           mutation_review_id="selftest-restore",
                           corpus_ref="2026-07-04",
                           previous_snapshot_hash=None,
                           codebook_path=cbpath)
        return cbpath, m, cbpath.read_bytes()

    # NC28 — the HAPPY PATH, so the controls below are known to be testing a
    # path that otherwise works. Order is asserted, not described.
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        cbpath, m, good = _restore_fixture(td)
        runner = FakeRunner(objects={m["object_path"]: good})
        t = RcloneTransport("fake-remote", runner=runner)
        dest = td / "installed" / "codebook.json"
        res = restore_snapshot(m, t, td / "staging", dest)
        nc28 = (res["trace"] == list(RESTORE_STEPS) and dest.exists()
                and sha256_of_file(dest) == m["sha256"])
    _check(r, "NC28 restore installs only after fetch->verify->validate", nc28,
           f"trace={res['trace']} installed_sha_matches={dest.name}")

    # NC29 — WRONG BYTES on the wire. Must halt at verify; nothing installed.
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        cbpath, m, good = _restore_fixture(td)
        corrupt = bytearray(good)
        corrupt[10] ^= 0xFF                      # same length, different content
        runner = FakeRunner(objects={m["object_path"]: bytes(corrupt)})
        t = RcloneTransport("fake-remote", runner=runner)
        dest = td / "installed" / "codebook.json"
        try:
            restore_snapshot(m, t, td / "staging", dest)
            nc29, why29 = False, "corrupt bytes reached installation"
        except (TransportError, RestoreError) as e:
            nc29, why29 = not dest.exists(), f"halted; destination created={dest.exists()}"
    _check(r, "NC29 wrong bytes halt before install", nc29, why29)

    # NC29b — THE INDEPENDENT VERIFY STEP, ACTUALLY EXERCISED.
    #
    # NC29 above does NOT test step 2, and rigging step 2 away proved it: bytes
    # corrupted in transit are caught by the FETCH, which verifies before it
    # returns, so NC29 passes whether or not the independent check exists. The
    # step earns its place only against a staged file altered AFTER a successful
    # fetch -- a staging directory is an ordinary file on disk, not a private
    # buffer. That is what this control models, and it asserts the halt names
    # VERIFICATION: with step 2 removed the same tampering is caught one step
    # later by validation, which is a different guarantee at a different stage.
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        cbpath, m, good = _restore_fixture(td)

        class _TamperingTransport(RcloneTransport):
            def get_verified(self, key, dest, expected_sha, expected_size):
                p = super().get_verified(key, dest, expected_sha, expected_size)
                data = bytearray(Path(p).read_bytes())
                data[5] ^= 0xFF                  # same length, different content
                Path(p).write_bytes(bytes(data))
                return p

        runner = FakeRunner(objects={m["object_path"]: good})
        t = _TamperingTransport("fake-remote", runner=runner)
        dest = td / "installed" / "codebook.json"
        try:
            restore_snapshot(m, t, td / "staging", dest)
            nc29b, why29b = False, "post-fetch tampering reached installation"
        except RestoreError as e:
            nc29b = "staged bytes failed verification" in str(e) and not dest.exists()
            why29b = (f"halted at VERIFY; destination created={dest.exists()}"
                      if nc29b else f"halted, but at the wrong step: {str(e)[:70]}")
    _check(r, "NC29b staged file tampered after a good fetch is caught at verify",
           nc29b, why29b)

    # NC30 — WRONG SHA and WRONG SIZE in the manifest, separately. Same-size
    # wrong content is NC29; these are the manifest-side mismatches.
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        cbpath, m, good = _restore_fixture(td)
        runner = FakeRunner(objects={m["object_path"]: good})
        t = RcloneTransport("fake-remote", runner=runner)

        bad_sha = dict(m)
        bad_sha["sha256"] = "e" * 64
        bad_sha["object_path"] = object_key_for("e" * 64)
        d1 = td / "i1" / "codebook.json"
        try:
            restore_snapshot(bad_sha, t, td / "s1", d1)
            a = False
        except (TransportError, RestoreError):
            a = not d1.exists()

        bad_size = dict(m)
        bad_size["byte_size"] = m["byte_size"] + 1
        d2 = td / "i2" / "codebook.json"
        try:
            restore_snapshot(bad_size, t, td / "s2", d2)
            b = False
        except (TransportError, RestoreError):
            b = not d2.exists()
    _check(r, "NC30 wrong sha and wrong byte size each halt before install", a and b,
           f"wrong_sha_halted={a} wrong_size_halted={b}")

    # NC31 — STRUCTURALLY INVALID PAYLOAD that transports perfectly. The bytes
    # match the manifest's sha exactly; they are simply not a codebook. Byte
    # verification CANNOT see this, which is why validation is its own step.
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        junk = b'{"not": "a codebook"}\n'
        junk_path = td / "junk.json"
        junk_path.write_bytes(junk)
        m = _valid_manifest(sha=sha256_of_bytes(junk), size=len(junk))
        runner = FakeRunner(objects={m["object_path"]: junk})
        t = RcloneTransport("fake-remote", runner=runner)
        dest = td / "installed" / "codebook.json"
        try:
            restore_snapshot(m, t, td / "staging", dest)
            nc31, why31 = False, "a non-codebook reached installation"
        except RestoreError as e:
            nc31 = "not a codebook" in str(e) and not dest.exists()
            why31 = f"halted at validation; destination created={dest.exists()}"
        except TransportError as e:
            nc31, why31 = False, f"halted at the WRONG step (transport): {str(e)[:60]}"
    _check(r, "NC31 byte-perfect non-codebook halts at validation, not install", nc31, why31)

    # NC32 — UNREACHABLE REMOTE is reported as transport failure, and is not
    # dressed up as an integrity or immutability finding.
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        cbpath, m, good = _restore_fixture(td)
        runner = FakeRunner(objects={m["object_path"]: good}, lie_on_get=True)
        t = RcloneTransport("fake-remote", runner=runner)
        dest = td / "installed" / "codebook.json"
        try:
            restore_snapshot(m, t, td / "staging", dest)
            nc32, why32 = False, "an unreachable object still installed something"
        except TransportError as e:
            msg = str(e)
            nc32 = ("does not exist" in msg and "IMMUTABILITY" not in msg
                    and "corrupt" not in msg.lower() and not dest.exists())
            why32 = f"transport failure named as such; destination created={dest.exists()}"
        except RestoreError as e:
            nc32, why32 = False, f"misclassified as a restore/integrity failure: {str(e)[:60]}"
    _check(r, "NC32 unreachable remote reported as transport failure", nc32, why32)

    # NC33 — the staging boundary cannot be collapsed. A restore whose staging
    # file IS the destination is refused: the whole point of staging is that the
    # destination is not written until the bytes are proven.
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        cbpath, m, good = _restore_fixture(td)
        runner = FakeRunner(objects={m["object_path"]: good})
        t = RcloneTransport("fake-remote", runner=runner)
        dest = td / "staging" / "codebook.staged.json"     # == the staging file
        try:
            restore_snapshot(m, t, td / "staging", dest)
            nc33a = False
        except RestoreError as e:
            nc33a = "staging path and install destination are the same" in str(e)
        # And install_atomic refuses unverified bytes outright.
        bogus = td / "bogus.json"
        bogus.write_bytes(b"nope\n")
        try:
            install_atomic(bogus, td / "never.json", m["sha256"], m["byte_size"])
            nc33b = False
        except RestoreError as e:
            nc33b = "REFUSING TO INSTALL" in str(e) and not (td / "never.json").exists()
    _check(r, "NC33 staging cannot equal destination; install refuses unverified bytes",
           nc33a and nc33b, f"collapse_refused={nc33a} unverified_install_refused={nc33b}")

    # NC34 — PUBLICATION DOES NOT CONFER AUTHORITY. With no tracked manifest, a
    # candidate that exists remotely must leave the state NOT_INITIALIZED and be
    # classified an orphan — no newest-object, no only-object-present fallback.
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        cbpath = td / "codebook.json"
        cbpath.write_text(json.dumps({"schema": fcb.SCHEMA_V2, "version": "0.7", "axes": {}}),
                          encoding="utf-8")
        cand = _valid_manifest()
        runner = FakeRunner(objects={cand["object_path"]: FIXTURE_BYTES})
        t = RcloneTransport("fake-remote", runner=runner)
        st = status(manifest_path=td / "absent.json", codebook_path=cbpath,
                    transport=t, candidate=cand)
        c = st.get("candidate") or {}
        nc34 = (st["state"] == STATE_NOT_INITIALIZED
                and c.get("authoritative") is False
                and c.get("classification") == "ORPHAN_CANDIDATE"
                and "present" in str(c.get("remote", "")))
    _check(r, "NC34 an existing remote candidate is still NOT authority", nc34,
           f"state={st['state']} authoritative={c.get('authoritative')} "
           f"remote={c.get('remote')!r}")

    # DET — serialization is deterministic and byte-stable.
    m = _valid_manifest()
    a, b = serialize_manifest(m), serialize_manifest(m)
    shuffled = {k: m[k] for k in reversed(list(m.keys()))}
    c = serialize_manifest(shuffled)
    _check(r, "DET  serialize x2 byte-identical, key-order independent",
           a == b == c, f"len={len(a)} sha={sha256_of_bytes(a.encode())[:16]}")

    # STATE A — no manifest at all is a STATE, not a crash, and not a fallback.
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        cbpath = td / "codebook.json"
        cbpath.write_text(json.dumps({"schema": fcb.SCHEMA_V2, "version": "0.7", "axes": {}}),
                          encoding="utf-8")
        st = status(manifest_path=td / "absent.json", codebook_path=cbpath)
        _check(r, "STATE A  absent manifest -> AUTHORITY_NOT_INITIALIZED",
               st["state"] == STATE_NOT_INITIALIZED, f"state={st['state']}")

    # STATE B/E — match, and "selected object missing" is unverifiable, never
    # resolved by finding a different object.
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        cbpath = td / "codebook.json"
        cbpath.write_text(json.dumps({"schema": fcb.SCHEMA_V2, "version": "0.7", "axes": {}}),
                          encoding="utf-8")
        # The manifest must select THESE bytes, so the sha is derived from the
        # file rather than reused from the fixture -- a manifest built from the
        # wrong payload would make STATE B unreachable and the test vacuous.
        m = _valid_manifest(sha=sha256_of_file(cbpath), size=cbpath.stat().st_size)
        mpath = td / "m.json"
        mpath.write_text(serialize_manifest(m), encoding="utf-8")
        st = status(manifest_path=mpath, codebook_path=cbpath)
        stB = st["state"]
        runner = FakeRunner(objects={})   # selected object absent; decoys irrelevant
        t = RcloneTransport("fake-remote", runner=runner)
        stE = status(manifest_path=mpath, codebook_path=cbpath, transport=t)["state"]
        _check(r, "STATE B/E  match detected; missing selected object -> UNVERIFIABLE",
               stB == STATE_LOCAL_MATCHES and stE == STATE_UNVERIFIABLE,
               f"B={stB} E={stE}")

    # BOUNDARY — no networking leaked into the codebook writer (P3 §17).
    writer_src = (REPO_ROOT / "experiments" / "foundry_codebook.py").read_text(encoding="utf-8")
    leaked = [tok for tok in ("rclone", "subprocess", "urllib", "requests", "foundry_authority")
              if tok in writer_src]
    _check(r, "BOUND write_codebook_atomic's module stays local-only",
           not leaked, f"network tokens in foundry_codebook.py: {leaked or 'none'}")

    # CANARY, closing. Nothing above may have touched the live codebook.
    _canary_after = sha256_of_file(_canary_path) if _canary_path.exists() else "ABSENT"
    _check(r, "CANARY operational codebook untouched by the whole suite",
           _canary_before == _canary_after,
           f"{_canary_before[:16]}… -> {_canary_after[:16]}… ({_canary_path})")

    width = max(len(n) for n, _, _ in r)
    print("=" * 78)
    print("FOUNDRY AUTHORITY — SELFTEST (no network, deterministic fixtures)")
    print("=" * 78)
    failed = 0
    for name, ok, detail in r:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name.ljust(width)}  {detail}")
        if not ok:
            failed += 1
    print("-" * 78)
    print(f"  {len(r) - failed}/{len(r)} passed")
    if failed:
        print(f"\n  ✗ {failed} control(s) FAILED.")
        return 1
    print("\n  ✓ every control passed, and each one was rigged red before being "
          "believed.\n    See the tranche evidence packet for the rigging results.")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_status(args) -> int:
    transport = None
    if args.check_remote:
        transport = RcloneTransport(read_remote(args.remote), bucket=args.bucket)
    candidate = None
    if getattr(args, "candidate", None):
        candidate, _ = load_manifest(Path(args.candidate))
    st = status(transport=transport, candidate=candidate)
    if args.json:
        printable = {k: v for k, v in st.items()}
        print(json.dumps(printable, indent=2, ensure_ascii=False))
        return 0
    print("=" * 78)
    print(f"C6 AUTHORITY STATUS — {st['state']}")
    print("=" * 78)
    print(f"  {st.get('detail', '')}")
    local = st.get("local") or {}
    if local.get("present"):
        print(f"\n  local codebook  {local['path']}")
        print(f"    sha256        {local['sha256']}")
        print(f"    byte_size     {local['byte_size']}")
        print(f"    axes/assert   {local['active_axis_count']} active, "
              f"{local['assertion_count']} assertions "
              f"({local['human_assertion_count']} human, "
              f"{local['rule_derived_assertion_count']} rule-derived)")
    else:
        print(f"\n  local codebook  ABSENT ({local.get('path')})")
    sel = st.get("selected")
    if sel:
        print(f"\n  selected authority")
        print(f"    bucket        {sel['bucket']}")
        print(f"    object_path   {sel['object_path']}")
        print(f"    sha256        {sel['sha256']}")
    else:
        print(f"\n  selected authority  NONE — manifest {MANIFEST_PATH} absent")
    cand = st.get("candidate")
    if cand:
        print(f"\n  candidate (REPORTED, never selected)")
        print(f"    classification  {cand['classification']}")
        print(f"    authoritative   {cand['authoritative']}")
        print(f"    object_path     {cand['object_path']}")
        print(f"    sha256          {cand['sha256']}")
        if "remote" in cand:
            print(f"    remote          {cand['remote']}")
        print(f"    why not         {cand['why_not_authority']}")
    for line in st.get("violations") or []:
        print(f"    ! {line}")
    return 0


def cmd_publish(args) -> int:
    """Build a candidate manifest FROM the codebook bytes and publish them
    immutably. Writes the candidate to disposable output space only — creating
    the tracked selector is a separate, Captain-authorised act (P3 §18)."""
    cb_path = Path(args.codebook) if args.codebook else fcb.CODEBOOK_PATH
    prior = None
    if args.prior_manifest:
        prior, pv = load_manifest(Path(args.prior_manifest))
        if prior is None or pv:
            fc.halt(f"--prior-manifest {args.prior_manifest} is missing or invalid: {pv}")

    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = build_manifest(
        snapshot_id=args.snapshot_id,
        created_utc=created,
        mutation_review_id=args.mutation_review_id,
        corpus_ref=args.corpus_ref or fcb.corpus_ref_current(),
        previous_snapshot_hash=args.previous_snapshot_hash,
        codebook_path=cb_path,
        prior=prior,
    )
    out_path = Path(args.candidate_out) if args.candidate_out else (
        fc.FOUNDRY_OUT_DIR / f"candidate-manifest.{manifest['snapshot_id']}.json")
    if MANIFEST_PATH.resolve() == out_path.resolve():
        fc.halt("--candidate-out names the TRACKED selector path. A candidate is not an "
                "authority; creating that file is a separate authorised act.")

    print(f"candidate manifest for {cb_path}")
    print(serialize_manifest(manifest))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(serialize_manifest(manifest), encoding="utf-8")
    print(f"wrote candidate (disposable, gitignored): {out_path}")

    if args.dry_run:
        print("\nDRY RUN — nothing uploaded.")
        return 0

    t = RcloneTransport(write_remote(args.remote), bucket=manifest["bucket"])
    print(f"\npublishing to {t.remote}:{t.bucket}/{manifest['object_path']}")
    outcome = t.put_immutable(manifest["object_path"], cb_path,
                              manifest["sha256"], manifest["byte_size"])
    print(f"result: {outcome}")
    print("\nNOTE: this object is a CANDIDATE. No tracked manifest selects it, so it is "
          "ORPHAN / NON-AUTHORITATIVE until Captain authorises the selector.")
    return 0


def cmd_verify_remote(args) -> int:
    """Consumer-side proof, through the READ-ONLY remote: fetch the exact object
    to staging, verify bytes, and validate that they are the codebook the
    manifest describes. Installs nothing."""
    manifest, v = load_manifest(Path(args.manifest))
    if manifest is None or v:
        fc.halt(f"{args.manifest} is missing or invalid: {v}")
    t = RcloneTransport(read_remote(args.remote), bucket=manifest["bucket"])
    with tempfile.TemporaryDirectory() as td:
        staged = Path(td) / "codebook.staged.json"
        t.get_verified(manifest["object_path"], staged, manifest["sha256"],
                       manifest["byte_size"])
        print(f"reader remote      : {t.remote}:{t.bucket}")
        print(f"object             : {manifest['object_path']}")
        print(f"sha256 (recomputed): {sha256_of_file(staged)}")
        print(f"byte_size          : {staged.stat().st_size}")
        payload = validate_codebook_payload(staged, manifest)
        print(f"codebook validation: OK — {payload['lint']}")
        local = describe_local(staged)
        for f in ("active_axis_count", "assertion_count", "human_assertion_count",
                  "rule_derived_assertion_count"):
            print(f"  {f:32} {local[f]}")
    return 0


def cmd_restore(args) -> int:
    """remote -> staging -> verify -> validate -> atomic install. In that order,
    and the order is asserted rather than described."""
    manifest, v = load_manifest(Path(args.manifest))
    if manifest is None or v:
        fc.halt(f"{args.manifest} is missing or invalid: {v}")
    t = RcloneTransport(read_remote(args.remote), bucket=manifest["bucket"])
    install_to = Path(args.install_to)
    staging = Path(args.staging) if args.staging else install_to.parent / ".restore-staging"
    try:
        result = restore_snapshot(manifest, t, staging, install_to,
                                  replace_existing=args.replace_existing)
    except RestoreError as e:
        print(f"RESTORE HALTED — {e}")
        return 1
    print(f"restore steps      : {' -> '.join(result['trace'])}")
    print(f"staged at          : {result['staged']}")
    print(f"installed          : {result['installed']}")
    print(f"sha256             : {result['sha256']}")
    print(f"byte_size          : {result['byte_size']}")
    return 0


def cmd_verify(args) -> int:
    ok, reason = verify_exact(args.sha, args.size, Path(args.path))
    print(("VERIFIED — " if ok else "FAILED — ") + reason)
    return 0 if ok else 1


def cmd_describe_local(args) -> int:
    print(json.dumps(describe_local(), indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="C6 authority machinery — manifest, verifier, transport, status.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("status", help="read-only authority/candidate state")
    p.add_argument("--check-remote", action="store_true",
                   help="also confirm the SELECTED object exists (never lists)")
    p.add_argument("--remote", default=None, help="rclone remote NAME (local config)")
    p.add_argument("--bucket", default=AUTHORITY_BUCKET)
    p.add_argument("--json", action="store_true")
    p.add_argument("--candidate", default=None,
                   help="report an UNSELECTED candidate manifest; cannot make it authority")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("publish", help="build a candidate manifest and publish immutably")
    p.add_argument("--snapshot-id", required=True)
    p.add_argument("--mutation-review-id", required=True,
                   help="the ratified mutation these bytes came from")
    p.add_argument("--previous-snapshot-hash", default=None,
                   help="omit for genesis (null); otherwise the prior snapshot's sha256")
    p.add_argument("--prior-manifest", default=None,
                   help="the previously SELECTED manifest, for succession validation")
    p.add_argument("--corpus-ref", default=None)
    p.add_argument("--codebook", default=None)
    p.add_argument("--candidate-out", default=None)
    p.add_argument("--remote", default=None, help="rclone WRITE remote NAME")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_publish)

    p = sub.add_parser("verify-remote",
                       help="read-only proof that the published object is exact and valid")
    p.add_argument("--manifest", required=True)
    p.add_argument("--remote", default=None, help="rclone READ remote NAME")
    p.set_defaults(func=cmd_verify_remote)

    p = sub.add_parser("restore",
                       help="remote -> staging -> verify -> validate -> atomic install")
    p.add_argument("--manifest", required=True)
    p.add_argument("--install-to", required=True,
                   help="explicit destination; there is no default that resolves to the "
                        "operational codebook")
    p.add_argument("--staging", default=None)
    p.add_argument("--remote", default=None, help="rclone READ remote NAME")
    p.add_argument("--replace-existing", action="store_true")
    p.set_defaults(func=cmd_restore)

    p = sub.add_parser("verify", help="exact-byte verification of a local file")
    p.add_argument("path")
    p.add_argument("--sha", required=True)
    p.add_argument("--size", required=True, type=int)
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("describe-local", help="facts about the local codebook")
    p.set_defaults(func=cmd_describe_local)

    p = sub.add_parser("selftest", help="every negative control, offline")
    p.set_defaults(func=lambda a: selftest())

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
