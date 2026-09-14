#!/usr/bin/env python3
"""C6 AUTHORITY — the legacy compatibility and operator shell.

THE LAW (P3-1, ruled 2026-08-14):

    The authoritative codebook is the exact immutable R2 snapshot selected by
    the tracked manifest in the current Git revision.

S12 MOVED THE LAW OUT OF THIS FILE. It is owned, with its rationale, by the
permanent package:

    mtj_foundry.authority            manifest law, succession, exact-byte
                                     verification, derived manifest facts
    mtj_foundry.authority_transport  immutable content-addressed R2 transport and
                                     its measured laws (A/B/C, If-None-Match,
                                     --ignore-times, --retries 1, single-PUT only)
    mtj_foundry.authority_status     the six authority states, candidate/orphan
                                     reporting
    mtj_foundry.authority_restore    staging -> verify -> validate -> atomic
                                     install, in that order, asserted

WHAT STAYS HERE, AND WHY. This file is the composition and process boundary:

  * LAYOUT. Where the tracked selector and the operational codebook live is a
    layout fact the permanent library may not know. `MANIFEST_PATH`,
    `OPERATIONAL_CODEBOOK_PATH` and the immovable forbidden-destination arm are
    bound here and passed down; every default path is resolved here.
  * THE PROCESS BOUNDARY. The permanent owners raise typed errors. Every call
    into an owner goes through `_stop_on_refusal`, which catches exactly
    `mtj_foundry.authority.AuthorityRefusal` -- whose message is the legacy halt
    body verbatim -- and calls `fc.halt`, so every function that used to `STOP`
    still does. `TransportError` and `RestoreError` are the permanent classes
    themselves and propagate exactly as before.
  * BACKUP POLICY for a replacing restore, which writes under the legacy
    backups directory.
  * The remote-nickname configuration, the offline selftest with its
    `FakeRunner`, and the context the CLI operator runs in. S13 moved the CLI
    itself -- parser, commands, printed reports -- to
    `mtj_foundry.authority_cli`; this file builds its context and delegates.

Every name below delegates AT CALL TIME: a wrapper looks the permanent owner up
when it is called, so the permanent object is what runs. No rule is restated.

    python3 experiments/foundry_authority.py status
    python3 experiments/foundry_authority.py verify <file> --sha <hex> --size <n>
    python3 experiments/foundry_authority.py selftest
    python3 experiments/foundry_authority.py describe-local
"""
import os
import sys
import json
import functools
import ast
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402
import foundry_codebook as fcb  # noqa: E402

# `foundry_common` is what puts `src` on `sys.path`, so the permanent owners are
# importable only after the line above. No new bootstrap is added.
from mtj_foundry import authority as _authority  # noqa: E402
from mtj_foundry import authority_restore as _restore  # noqa: E402
from mtj_foundry import authority_status as _status  # noqa: E402
from mtj_foundry import authority_transport as _transport  # noqa: E402
from mtj_foundry import authority_cli as _cli  # noqa: E402

SCHEMA = _authority.SCHEMA

# The tracked selector. DELIBERATELY ABSENT until Captain authorizes the first
# candidate cutover -- its absence is the AUTHORITY_NOT_INITIALIZED state, not
# an error, and a bootstrap file asserting an authority that does not exist
# would be a lie the tooling would then believe (P3 §18).
MANIFEST_PATH = fc.CONFIG_SELECTORS / "codebook-authority.json"

AUTHORITY_BUCKET = _authority.AUTHORITY_BUCKET

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

SINGLE_PUT_CUTOFF = _transport.SINGLE_PUT_CUTOFF
SINGLE_PUT_LIMIT_BYTES = _transport.SINGLE_PUT_LIMIT_BYTES
CONDITIONAL_CREATE_HEADER = _transport.CONDITIONAL_CREATE_HEADER
MEASURED_412_STDERR = _transport.MEASURED_412_STDERR
MEASURED_SKIP_STDOUT = _transport.MEASURED_SKIP_STDOUT

# Remote NICKNAMES are local configuration, never authority (P3 §9).
ENV_READ_REMOTE = "MTJ_FOUNDRY_READ_REMOTE"
ENV_WRITE_REMOTE = "MTJ_FOUNDRY_WRITE_REMOTE"
DEFAULT_READ_REMOTE = "r2foundry-ro"
DEFAULT_WRITE_REMOTE = "r2foundry-rw"

MANIFEST_FIELDS = _authority.MANIFEST_FIELDS
COUNT_FIELDS = _authority.COUNT_FIELDS
DERIVED_FIELDS = _authority.DERIVED_FIELDS
OBJECT_KEY_PREFIX = _authority.OBJECT_KEY_PREFIX
OBJECT_KEY_FILENAME = _authority.OBJECT_KEY_FILENAME

# The permanent classes themselves, not copies: `except TransportError` and
# `except RestoreError` keep catching exactly what the owners raise.
TransportError = _transport.TransportError
RestoreError = _restore.RestoreError

STATE_NOT_INITIALIZED = _status.STATE_NOT_INITIALIZED
STATE_LOCAL_MATCHES = _status.STATE_LOCAL_MATCHES
STATE_MISMATCH = _status.STATE_MISMATCH
STATE_MANIFEST_INVALID = _status.STATE_MANIFEST_INVALID
STATE_UNVERIFIABLE = _status.STATE_UNVERIFIABLE
STATE_NO_LOCAL = _status.STATE_NO_LOCAL

RESTORE_STEPS = _restore.RESTORE_STEPS


def _stop_on_refusal(owner_call, *args, **kwargs):
    """THE PROCESS BOUNDARY, stated once, and every call from this shell into a
    permanent owner crosses it. A typed `AuthorityRefusal` becomes the historic
    `STOP — <message>` and exit 1; every other exception -- `TransportError`,
    `RestoreError`, `OSError` -- propagates exactly as it always did. An owner
    that never refused before still never raises one, so routing it here changes
    nothing observable. `owner_call` is read off the owner module by the caller
    at call time, so the permanent object is what runs."""
    try:
        return owner_call(*args, **kwargs)
    except _authority.AuthorityRefusal as error:
        fc.halt(str(error))


def object_key_for(sha256: str) -> str:
    return _stop_on_refusal(_authority.object_key_for, sha256)


def read_remote(explicit: str = None) -> str:
    return explicit or os.environ.get(ENV_READ_REMOTE) or DEFAULT_READ_REMOTE


def write_remote(explicit: str = None) -> str:
    return explicit or os.environ.get(ENV_WRITE_REMOTE) or DEFAULT_WRITE_REMOTE


# ---------------------------------------------------------------------------
# manifest law -- delegated to mtj_foundry.authority
# ---------------------------------------------------------------------------

def serialize_manifest(manifest: dict) -> str:
    return _stop_on_refusal(_authority.serialize_manifest, manifest)


def validate_manifest(manifest, label: str = "manifest") -> list:
    return _stop_on_refusal(_authority.validate_manifest, manifest, label)


def validate_or_halt(manifest, label: str = "manifest") -> dict:
    return _stop_on_refusal(_authority.validate_or_raise, manifest, label)


def validate_succession(candidate: dict, prior: dict = None, label: str = "candidate") -> list:
    return _stop_on_refusal(_authority.validate_succession, candidate, prior, label)


def load_manifest(path: Path = None):
    return _stop_on_refusal(_authority.load_manifest,
                            path if path is not None else MANIFEST_PATH)


def sha256_of_bytes(data: bytes) -> str:
    return _stop_on_refusal(_authority.sha256_of_bytes, data)


def sha256_of_file(path: Path) -> str:
    return _stop_on_refusal(_authority.sha256_of_file, path)


def verify_exact(expected_sha: str, expected_size: int, target) -> tuple:
    return _stop_on_refusal(_authority.verify_exact, expected_sha, expected_size, target)


def verify_or_halt(expected_sha: str, expected_size: int, target) -> None:
    return _stop_on_refusal(_authority.verify_or_raise, expected_sha, expected_size, target)


def describe_local(path: Path = None) -> dict:
    return _stop_on_refusal(_authority.describe_local,
                            path if path is not None else fcb.CODEBOOK_PATH)


def derive_manifest_facts(codebook_path: Path = None) -> dict:
    return _stop_on_refusal(_authority.derive_manifest_facts,
                            codebook_path if codebook_path is not None else fcb.CODEBOOK_PATH)


def build_manifest(snapshot_id: str, created_utc: str, mutation_review_id: str,
                   corpus_ref: str, previous_snapshot_hash, codebook_path: Path = None,
                   prior: dict = None) -> dict:
    return _stop_on_refusal(_authority.build_manifest, snapshot_id, created_utc,
                            mutation_review_id, corpus_ref, previous_snapshot_hash,
                            codebook_path if codebook_path is not None else fcb.CODEBOOK_PATH,
                            prior)


def compare_manifest_to_codebook(manifest: dict, codebook_path: Path = None) -> list:
    return _stop_on_refusal(_authority.compare_manifest_to_codebook, manifest,
                            codebook_path if codebook_path is not None else fcb.CODEBOOK_PATH)


# ---------------------------------------------------------------------------
# transport -- delegated to mtj_foundry.authority_transport
# ---------------------------------------------------------------------------

def _forbidden_fetch_destinations() -> set:
    """Paths a staging fetch may never target. TWO INDEPENDENT ARMS.

    Arm 1 is the rebindable `OPERATIONAL_CODEBOOK_PATH`, which exists so NC20
    can exercise the RULE against a decoy instead of naming the live file.
    Arm 2 is `_IMMOVABLE_FORBIDDEN_DESTINATIONS`, captured at import and
    consulted by nothing else, so the real codebook stays refused even when arm
    1 has been rigged away.

    A guard whose only arm is the one the tests rebind is a guard that is absent
    during exactly the runs that matter -- which is how the 2026-08-14 incident
    happened, and the reason this function exists rather than an `==`.

    S12: this is the LAYOUT half of the staging boundary and stays with the
    layout. The refusal itself is `authority_transport`'s, and the transport
    below consults this function at every fetch."""
    return set(_IMMOVABLE_FORBIDDEN_DESTINATIONS) | {Path(OPERATIONAL_CODEBOOK_PATH).resolve()}


def _refuse_operational_destination(dest: Path) -> None:
    return _stop_on_refusal(_transport.refuse_forbidden_destination, dest,
                            _forbidden_fetch_destinations())


class RcloneTransport(_transport.RcloneTransport):
    """`mtj_foundry.authority_transport.RcloneTransport`, with this boundary's
    forbidden staging destinations declared. Adds no behaviour: the permanent
    transport requires the declaration, and this shell is where the operational
    codebook's location is known. The declaration is a call-time lookup, so a
    rig that rebinds a module global here is seen by the next fetch."""

    def __init__(self, remote: str, bucket: str = AUTHORITY_BUCKET, runner=None):
        super().__init__(remote, bucket, runner,
                         forbidden_destinations=lambda: _forbidden_fetch_destinations())


# ---------------------------------------------------------------------------
# status -- delegated to mtj_foundry.authority_status
# ---------------------------------------------------------------------------

def describe_candidate(candidate: dict, transport: "RcloneTransport" = None) -> dict:
    return _stop_on_refusal(_status.describe_candidate, candidate, transport)


def status(manifest_path: Path = None, codebook_path: Path = None,
           transport: "RcloneTransport" = None, candidate: dict = None) -> dict:
    return _stop_on_refusal(_status.status,
                            manifest_path if manifest_path is not None else MANIFEST_PATH,
                            codebook_path if codebook_path is not None else fcb.CODEBOOK_PATH,
                            transport, candidate)


# ---------------------------------------------------------------------------
# restore -- delegated to mtj_foundry.authority_restore
# ---------------------------------------------------------------------------

def _backup_policy():
    """The pre-install backup a replacing restore requires. Backup location is
    legacy layout, so the policy is injected from here: the readback-verified
    `foundry_codebook.backup_codebook`, tagged exactly as before, looked up when
    the restore is called."""
    return functools.partial(fcb.backup_codebook, "pre-restore-install")


def validate_codebook_payload(path: Path, manifest: dict) -> dict:
    return _stop_on_refusal(_restore.validate_codebook_payload, path, manifest)


def install_atomic(staged: Path, dest: Path, expected_sha: str, expected_size: int,
                   replace_existing: bool = False) -> str:
    return _stop_on_refusal(_restore.install_atomic, staged, dest, expected_sha, expected_size,
                            replace_existing, backup=_backup_policy())


def restore_snapshot(manifest: dict, transport: "RcloneTransport", staging_dir: Path,
                     install_to: Path, replace_existing: bool = False) -> dict:
    return _stop_on_refusal(_restore.restore_snapshot, manifest, transport, staging_dir,
                            install_to, replace_existing, backup=_backup_policy())


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


_PERMANENT_PACKAGE = "mtj_foundry"


def normalized_imports(source: str) -> set:
    """Every direct dependency of `source`, as a FULL module identity.

    C8.5N.R2. THE TWO SPELLINGS OF ONE DEPENDENCY MUST NORMALIZE TO ONE STRING.
    Python writes the same edge two ways, and the first version of this guard
    only understood one of them:

        from mtj_foundry import codebook   ->  mtj_foundry.codebook
        import mtj_foundry.codebook        ->  mtj_foundry.codebook

    The original reduced every import to `name.split(".")[0]`, so
    `import mtj_foundry.paths` was scored as the allowed top-level `mtj_foundry`
    and the forbidden layout capability rode in behind it, while the
    `from ... import paths` spelling was caught. One syntax form guarded and an
    equivalent form open is the guard-aim defect this arc has refused before
    (Manager review issue:1#issuecomment-5561128789).

    The rule, and it FAILS CLOSED:

    * `import a.b.c` / `import a.b.c as x`  -> `a.b.c`, never `a`.
    * `from mtj_foundry import x`           -> `mtj_foundry.x`, because the
      permanent package's members ARE the dependencies worth distinguishing.
    * `from a.b import x`                   -> `a.b`; the alias is a name inside
      an already-identified module, not a module.
    * a RELATIVE import keeps its leading dots and therefore matches no allowed
      identity. It cannot silently resolve to something permitted.
    """
    found = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            found |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                found.add("." * node.level + (node.module or ""))
            elif node.module == _PERMANENT_PACKAGE:
                found |= {f"{_PERMANENT_PACKAGE}.{a.name}" for a in node.names}
            elif node.module:
                found.add(node.module)
    return found


def _persistence_closure() -> dict:
    """`{module name: source}` for the permanent local-persistence closure.

    Resolved by MODULE IDENTITY, never by a repository path: the store is
    imported, `__file__` is read off the imported object, and its permanent
    dependencies are discovered from its own import statements rather than
    assumed. That is what makes the guard survive a rename and refuse to be
    satisfied by a file that merely still exists at the old location.

    Discovery walks `normalized_imports`, so BOTH spellings of a permanent
    dependency enter the closure and a dotted one can no longer hide.
    """
    from mtj_foundry import codebook_store
    out = {}
    pending = [codebook_store]
    while pending:
        module = pending.pop()
        if module.__name__ in out:
            continue
        out[module.__name__] = Path(module.__file__).read_text(encoding="utf-8")
        for identity in normalized_imports(out[module.__name__]):
            if identity.startswith(f"{_PERMANENT_PACKAGE}."):
                pending.append(__import__(identity,
                                          fromlist=[identity.rsplit(".", 1)[-1]]))
    return out


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
    #
    # RE-AIMED BY C8.5N, BECAUSE ITS SUBJECT MOVED. This used to read the source
    # of `experiments/foundry_codebook.py` and grep it for network tokens. That
    # was exact while the file WAS the writer; after C8.5N it owns none of the
    # A13 write protocol, so the same check would keep passing while inspecting
    # a file that no longer does the thing being guarded -- a guard that cannot
    # fail, which this repository has measured twice before.
    #
    # The invariant is unchanged and the mechanism is stronger. The subject is
    # now the permanent local-persistence CLOSURE, reached by MODULE IDENTITY
    # (`sys.modules` / `__file__` of the imported object) rather than by a
    # hardcoded repository filename -- so a future rename cannot silently
    # disarm it -- and the test is the IMPORT GRAPH rather than a substring
    # search, so a token inside a docstring is not a finding and an indirect
    # reach is not invisible.
    #
    # `os` is legitimately in the closure (fsync, replace), so the process-
    # spawning families are rejected by NAME instead of banning the module.
    #
    # C8.5N.R2: the dependency test is now an EXACT set per module, keyed on the
    # FULL normalized identity. A top-level allow-list could not tell
    # `mtj_foundry.codebook` from `mtj_foundry.paths`, and the second carries the
    # ProjectPaths/layout capability this store is explicitly denied. Widening
    # either set is a contract change, not a fix.
    _closure = _persistence_closure()
    _expected_imports = {
        "mtj_foundry.codebook_store": {"__future__", "hashlib", "json", "os",
                                       "pathlib", "mtj_foundry.codebook"},
        "mtj_foundry.codebook": {"__future__", "re"},
    }
    _forbidden_call = ("os.system", "os.popen", "os.spawn", "os.exec", "os.fork",
                       "os.posix_spawn")
    leaked = []
    if set(_closure) != set(_expected_imports):
        leaked.append(f"closure is {sorted(_closure)}, expected "
                      f"{sorted(_expected_imports)}")
    for _name, _src in sorted(_closure.items()):
        for _identity in sorted(normalized_imports(_src)
                                - _expected_imports.get(_name, set())):
            leaked.append(f"{_name}: imports {_identity}")
        for _node in ast.walk(ast.parse(_src)):
            if isinstance(_node, ast.Call):
                _callee = ast.unparse(_node.func)
                if _callee.startswith(_forbidden_call):
                    leaked.append(f"{_name}: {_callee}()")
    _check(r, "BOUND the permanent codebook-write closure stays local-only",
           not leaked, f"closure={sorted(_closure)} forbidden={leaked or 'none'}")

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
# CLI -- the operator is `mtj_foundry.authority_cli` (S13)
# ---------------------------------------------------------------------------
#
# The parser, the six commands and every printed line are the permanent
# operator's. What stays here is what only this boundary knows: the tracked
# selector path, the operational codebook path, the disposable candidate
# directory, the remote nicknames, the transport that declares both forbidden
# staging arms, the backup policy, the corpus reference, the historic STOP and
# the offline selftest. They are handed over as call-time callables, and every
# command crosses `_stop_on_refusal`, exactly like every other owner call.

def _context():
    return _cli.AuthorityOperatorContext(
        manifest_path=MANIFEST_PATH,
        codebook_path=lambda: fcb.CODEBOOK_PATH,
        candidate_dir=fc.FOUNDRY_OUT_DIR,
        read_remote=lambda explicit: read_remote(explicit),
        write_remote=lambda explicit: write_remote(explicit),
        transport=lambda remote, bucket: RcloneTransport(remote, bucket=bucket),
        backup_policy=lambda: _backup_policy(),
        corpus_ref_current=lambda: fcb.corpus_ref_current(),
        stop=lambda message: fc.halt(message),
        selftest=lambda: selftest(),
    )


def cmd_status(args) -> int:
    return _stop_on_refusal(_cli.cmd_status, args, _context())


def cmd_publish(args) -> int:
    return _stop_on_refusal(_cli.cmd_publish, args, _context())


def cmd_verify_remote(args) -> int:
    return _stop_on_refusal(_cli.cmd_verify_remote, args, _context())


def cmd_restore(args) -> int:
    return _stop_on_refusal(_cli.cmd_restore, args, _context())


def cmd_verify(args) -> int:
    return _stop_on_refusal(_cli.cmd_verify, args, _context())


def cmd_describe_local(args) -> int:
    return _stop_on_refusal(_cli.cmd_describe_local, args, _context())


def main() -> int:
    return _stop_on_refusal(_cli.run, None, _context())


if __name__ == "__main__":
    sys.exit(main())
