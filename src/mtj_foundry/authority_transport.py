"""Immutable content-addressed codebook transport — exact keys, measured laws.

## What this is

The one permanent module that spawns a process. `RcloneTransport` fetches an
EXACT key to a staging destination and proves the bytes, and publishes an EXACT
key with an atomic create-only precondition and a readback. S12 moved it out of
the legacy `foundry_authority` shell under conservation: every argv, every
refusal and every outcome string is the shell's.

Nothing here lists to decide. This class has no enumeration verb at all,
`stat`/`get_verified` take an EXACT key, and `stat` refuses a result that matched
more than one row. There is no prune, delete, overwrite, promotion or mutable
pointer write, so authority selection cannot accidentally reach one.

## The three transport laws (measured 2026-08-14, PART ELEVEN of the P3 packet)

LAW A — EXIT STATUS IS NOT OBJECT INTEGRITY. `rclone mkdir` returned exit 0
        while CreateBucket was denied; `rclone copyto` of a MISSING object
        returns exit 0 and creates no file; `lsjson` of a missing key returns
        `[]` at exit 0. So every fetch asserts the destination exists and
        verifies bytes against the manifest. A transport return code is never
        evidence.
LAW B — THE BUCKET PRECHECK MUST NOT MASK THE REAL OPERATION. Bucket-scoped
        credentials 403 on rclone's CreateBucket precheck BEFORE the intended
        operation, which reads exactly like "this credential cannot write".
        Every argv this module builds carries `--s3-no-check-bucket`.
LAW C — THE PUBLISHER CREDENTIAL DOES NOT GUARANTEE IMMUTABILITY. R2's Object
        Read & Write includes DeleteObject and there is nothing narrower, so
        immutability is enforced HERE: `put_immutable` creates with an ATOMIC
        create-only precondition, refuses a key occupied by different bytes,
        and proves identity by remote readback.

## Why the create is conditional and not just checked

A check-then-act publish (stat -> PUT) is a TOCTOU race: A sees the key absent,
B creates different bytes, A uploads and destroys B's object. The pre-read
cannot close that window -- only the remote can. Measured against live R2 with
the installed rclone (v1.74.3): `--header-upload "If-None-Match: *"` makes the
create ATOMIC, and a PUT to an occupied key is rejected by the SERVER with
`412 PreconditionFailed` at `PutObject`, leaving the occupant byte-identical.
The installed binary has no conditional-write flag (`rclone help flags` matches
nothing for condition / if-none / if-match / precondition), so the generic
`--header-upload` is the only primitive, which is why it was proven live rather
than adopted.

`If-None-Match` is a REQUEST PRECONDITION consumed by the server at request
time and never stored. That is a different mechanism from stored object metadata
(cache-control), where R2 ignores `--header-upload` and `-M --metadata-set` is
required -- which is why it was proven live (412 plus a same-bytes/fresh-key
control) rather than assumed from either rule.

## And `rc == 0` does not prove a create happened -- LAW A, one level deeper

Measured 2026-08-14: a conditional PUT of IDENTICAL bytes onto an OCCUPIED key
returned exit 0 with no 412, because rclone compared size+modtime itself and
logged `Unchanged skipping` -- no PutObject was ever issued, so the server
precondition never ran. `--ignore-times` is therefore MANDATORY on the
conditional create: the SERVER decides existence, and rclone is never allowed to
answer that question from a local mtime. `--retries 1` rides with it, because a
412 is a terminal answer.

SINGLE-PUT ONLY. The 412 was proven for `PutObject`. A payload at or above the
multipart cutoff takes a different code path (CreateMultipartUpload) whose
precondition behaviour was NOT measured, so publication REFUSES at that size
rather than assuming the proof carries over. The cutoff is passed explicitly so a
differently-configured rclone cannot switch paths behind us.

The pre-read is KEPT, for idempotency semantics only. The conditional is what
provides safety; the pre-read turns a re-publish of identical bytes into
`already-present` instead of an error.

## The staging boundary

`get_verified` DELETES its destination before fetching, so aiming it at the
operational codebook would destroy that file before any remote byte was
verified (the 2026-08-14 incident). This module does not know where the
operational codebook is -- that is a layout fact -- so the constructor REQUIRES
the composition boundary to declare the forbidden destinations, and the refusal
runs before any unlink and before any process is spawned. The declaration is
consulted at every fetch, not captured once, so a boundary that keeps two
independent arms (one rebindable for its negative controls, one no rig touches)
keeps both of them live here.
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

from mtj_foundry import authority

__all__ = [
    "CONDITIONAL_CREATE_HEADER",
    "MEASURED_412_STDERR",
    "MEASURED_SKIP_STDOUT",
    "RcloneTransport",
    "SINGLE_PUT_CUTOFF",
    "SINGLE_PUT_LIMIT_BYTES",
    "TransportError",
    "default_runner",
    "refuse_forbidden_destination",
]

# Publication is proven for single-part PutObject only (see the docstring).
# Passed explicitly rather than inherited, so the code path cannot change under
# a different rclone config; 200Mi is the measured default of v1.74.3 and the
# operational codebook is ~5MB, three orders of magnitude below it.
SINGLE_PUT_CUTOFF = "200Mi"
SINGLE_PUT_LIMIT_BYTES = 200 * 1024 * 1024

# The atomic create-only precondition. Established from the INSTALLED binary
# (rclone v1.74.3 `--header-upload`; `rclone help flags` offers no conditional
# -write flag at all) and proven live against R2 by a 412, not chosen from
# documentation.
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


class TransportError(RuntimeError):
    pass


def refuse_forbidden_destination(dest, forbidden) -> None:
    """Raise if `dest` resolves to any path in `forbidden`. A PREDICATE: it
    never opens, unlinks or writes anything, which is what lets a negative
    control name the real operational path safely."""
    if Path(dest).resolve() in {Path(p).resolve() for p in forbidden}:
        raise TransportError(
            f"REFUSED: {dest} is the OPERATIONAL codebook. get_verified stages and "
            f"verifies; it does not install. Fetch to a temporary path, verify, "
            f"validate, then install atomically (P3 §7).")


def default_runner(argv: list) -> tuple:
    """(returncode, stdout, stderr). The ONLY place a subprocess is spawned."""
    proc = subprocess.run(argv, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


class RcloneTransport:
    """Exact-key object transport. No list-newest, no discover-latest, no
    prune, no delete, no overwrite, no mutable-pointer write -- those verbs do
    not exist on this class, so authority selection cannot accidentally reach
    one.

    `runner` is injectable so every failure mode below is testable offline.

    `forbidden_destinations` is REQUIRED and keyword-only: a zero-argument
    callable returning the paths a staging fetch may never target, consulted at
    every fetch. There is no default, because a default would be either a layout
    fact this library may not know or an empty set that silently disarms the
    staging boundary."""

    def __init__(self, remote: str, bucket: str = authority.AUTHORITY_BUCKET,
                 runner=None, *, forbidden_destinations):
        if not remote or ":" in remote:
            raise TransportError(
                f"remote {remote!r} must be a bare rclone remote NAME (no colon); "
                f"it is local configuration, never part of authority identity")
        if not callable(forbidden_destinations):
            raise TransportError(
                "forbidden_destinations must be a zero-argument callable consulted at "
                "every fetch — a set captured once cannot keep a rebindable arm live")
        self.remote = remote
        self.bucket = bucket
        self._run = runner or default_runner
        self._forbidden_destinations = forbidden_destinations

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
        verified -- exactly the failure it must not enable. A restore
        therefore: fetch to staging -> verify exact bytes -> validate the
        codebook -> only then install atomically over the live file.
        Never returns on failure."""
        dest = Path(dest)
        refuse_forbidden_destination(dest, self._forbidden_destinations())
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            dest.unlink()  # a stale file must not be mistaken for a fetch
        self._fetch_raw(key, dest)
        ok, reason = authority.verify_exact(expected_sha, expected_size, dest)
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
            ok, reason = authority.verify_exact(expected_sha, expected_size, probe)
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

        ok, reason = authority.verify_exact(expected_sha, expected_size, src)
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
