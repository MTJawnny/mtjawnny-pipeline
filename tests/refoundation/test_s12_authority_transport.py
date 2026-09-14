"""S12 — the authority / transport split: owners, laws, boundaries, negative controls.

WHAT S12 MOVED, AND WHERE
-------------------------
* manifest law, succession, exact-byte verification,
  derived manifest facts                    -> `mtj_foundry.authority`
* immutable content-addressed R2 transport  -> `mtj_foundry.authority_transport`
* the six authority states, candidate/orphan -> `mtj_foundry.authority_status`
* staging -> verify -> validate -> install  -> `mtj_foundry.authority_restore`

`experiments/foundry_authority.py` kept the layout (selector path, operational
codebook path, both forbidden-destination arms), the `STOP — …` process
boundary, the backup policy, the CLI and the offline selftest. Each of its law
names is a call-time delegate.

WHAT IS PROVED HERE
-------------------
1. The owners keep every law and every refusal the task names, each one shown
   RED against a rigged owner, not merely green against the real one.
2. The shell is a boundary and not a second implementation: every law name is
   defined once, the shell's same-named functions are pure delegates, and a
   permanent object replaced at run time is what the shell runs.
3. The typed-refusal translation is byte-exact at the process boundary.
4. Layering: exact import sets, one subprocess owner, one install writer, no
   legacy/AQ4/layout edge, no exit/print/`__file__`, acyclic graph.
5. The tracked selector still selects, still validates as genesis, and the
   selected codebook still matches it.

The rclone double is the legacy selftest's `FakeRunner`, reused rather than
rewritten: it is the one model of the measured R2/rclone behaviour.
"""

from __future__ import annotations

import ast
import contextlib
import hashlib
import inspect
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.refoundation.helpers import REPO_ROOT, SRC
from tests.refoundation.test_gate2_purity import EXPERIMENTS, load_legacy
import tests.refoundation.test_s11_codebook_kernel as s11

from mtj_foundry import (authority, authority_restore, authority_status,
                         authority_transport, codebook)
from mtj_foundry.paths import ProjectPaths

PKG = SRC / "mtj_foundry"
PATHS = ProjectPaths.for_root(REPO_ROOT)
SELECTOR = PATHS.codebook_authority_selector
OPERATIONAL = PATHS.legacy_codebook_json

# Measured at the accepted S11 head 444b4e8 and required unchanged by S12.
SELECTOR_SHA256 = "fa6686e0cb8b09b62ae46484069549d0212dc69b74dfc091f0b14cace77abed0"
SELECTED_SHA256 = "6aa6193f8a457ae4c7884e364f519749a9d68b96f7ecedf3fa903bfa4677426c"
SELECTED_BYTES = 5066147

S12_MODULES = {
    "authority": {"mtj_foundry.codebook", "mtj_foundry.codebook_store"},
    "authority_transport": {"mtj_foundry.authority"},
    "authority_status": {"mtj_foundry.authority", "mtj_foundry.authority_transport"},
    "authority_restore": {"mtj_foundry.authority", "mtj_foundry.codebook"},
}
S12_STDLIB = {
    "authority": {"__future__", "hashlib", "json", "re", "datetime", "pathlib"},
    "authority_transport": {"__future__", "json", "re", "subprocess", "tempfile", "pathlib"},
    "authority_status": {"__future__"},
    "authority_restore": {"__future__", "json", "os", "shutil", "pathlib"},
}

LEGACY = load_legacy("foundry_authority")
FakeRunner = LEGACY.FakeRunner
FIX = LEGACY.FIXTURE_BYTES
FSHA = hashlib.sha256(FIX).hexdigest()
KEY = authority.object_key_for(FSHA)


def _no_forbidden():
    return set()


def transport(runner, forbidden=_no_forbidden, cls=authority_transport.RcloneTransport):
    return cls("fake-remote", runner=runner, forbidden_destinations=forbidden)


def valid_manifest(**overrides):
    m = LEGACY._valid_manifest()
    m.update(overrides)
    return m


def uploads(runner):
    return [c for c in runner.calls if c[1] == "copyto" and ":" in c[3]]


def _halted(fn, *args, **kwargs):
    err = io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
        try:
            fn(*args, **kwargs)
        except SystemExit as exc:
            return exc.code, err.getvalue()
    return None, err.getvalue()


def _imports(path: Path) -> set:
    return s11._imports(ast.parse(path.read_text(encoding="utf-8")))


# ===========================================================================
# 1. manifest law
# ===========================================================================

class TestManifestLaw(unittest.TestCase):

    def assert_rejected(self, manifest, needle=None):
        v = authority.validate_manifest(manifest)
        self.assertTrue(v, f"accepted: {manifest}")
        if needle:
            self.assertTrue(any(needle in x for x in v), v)
        return v

    def test_the_fixture_manifest_is_valid(self):
        self.assertEqual(authority.validate_manifest(valid_manifest()), [])

    def test_unknown_schema_is_fatal_and_does_not_guess(self):
        for schema in ("foundry-authority/2", "", None, "FOUNDRY-AUTHORITY/1"):
            with self.subTest(schema=schema):
                self.assert_rejected(valid_manifest(schema=schema), "unknown schema")

    def test_every_required_field_is_fatal_when_absent(self):
        for field in authority.MANIFEST_FIELDS:
            m = valid_manifest()
            del m[field]
            with self.subTest(field=field):
                self.assert_rejected(m, f"missing required field {field!r}")

    def test_an_unknown_field_is_fatal(self):
        self.assert_rejected(valid_manifest(latest=True), "unknown field")

    def test_object_path_must_embed_its_own_sha(self):
        self.assert_rejected(valid_manifest(object_path=authority.object_key_for("b" * 64)),
                             "disagrees with its own content hash")

    def law_every_mutable_pointer_token_is_refused(self):
        for token in ("latest", "current", "newest", "head", "live"):
            self.assert_rejected(
                valid_manifest(object_path=f"foundry/codebook/{token}/codebook.json"),
                "mutable-pointer")
            self.assert_rejected(
                valid_manifest(object_path=f"foundry/codebook/sha256/{FSHA}/{token.upper()}.json"),
                "mutable-pointer")

    def test_every_mutable_pointer_token_is_refused(self):
        self.law_every_mutable_pointer_token_is_refused()

    def test_key_shape_and_cleanliness(self):
        for path in ("/" + KEY, KEY + " ", "foundry/../codebook.json", "codebook.json", ""):
            with self.subTest(path=path):
                self.assert_rejected(valid_manifest(object_path=path))

    def test_strict_types_never_coerce(self):
        for field, bad in (("byte_size", True), ("byte_size", 0), ("byte_size", "27"),
                           ("sha256", FSHA.upper()), ("created_utc", "2026-02-30T00:00:00Z"),
                           ("assertion_count", False), ("corpus_ref", "2026-7-4"),
                           ("bucket", "  "), ("mutation_review_id", "")):
            with self.subTest(field=field, bad=bad):
                self.assert_rejected(valid_manifest(**{field: bad}))

    def test_genesis_is_null_and_no_sentinel_is_accepted(self):
        self.assertEqual(authority.validate_manifest(valid_manifest(previous_snapshot_hash=None)), [])
        self.assertEqual(authority.validate_manifest(valid_manifest(previous_snapshot_hash="a" * 64)), [])
        self.assert_rejected(valid_manifest(previous_snapshot_hash="0" * 64), "all-zero")
        self.assert_rejected(valid_manifest(previous_snapshot_hash=FSHA), "own predecessor")
        for bad in ("", "null", "None", "A" * 64, 0):
            with self.subTest(bad=bad):
                self.assert_rejected(valid_manifest(previous_snapshot_hash=bad))

    def test_serializer_is_deterministic_order_independent_and_utf8(self):
        m = valid_manifest(mutation_review_id="Urza’s Juzám")
        shuffled = {k: m[k] for k in reversed(list(m))}
        a, b = authority.serialize_manifest(m), authority.serialize_manifest(shuffled)
        self.assertEqual(a, b)
        self.assertEqual(list(json.loads(a)), list(authority.MANIFEST_FIELDS))
        self.assertIn("Urza’s Juzám", a)
        self.assertTrue(a.endswith("}\n") and not a.endswith("\n\n"))

    def test_serializer_refuses_incomplete_or_extra(self):
        m = valid_manifest()
        del m["bucket"]
        with self.assertRaises(authority.ManifestSerializationError):
            authority.serialize_manifest(m)
        with self.assertRaises(authority.ManifestSerializationError):
            authority.serialize_manifest(valid_manifest(extra=1))

    def test_object_key_refuses_a_non_sha(self):
        for bad in ("", None, "A" * 64, "g" * 64, FSHA[:-1]):
            with self.subTest(bad=bad), self.assertRaises(authority.ObjectKeyError):
                authority.object_key_for(bad)

    def test_validate_or_raise_is_typed(self):
        with self.assertRaises(authority.ManifestInvalidError) as ctx:
            authority.validate_or_raise(valid_manifest(sha256="x"), "L")
        self.assertTrue(str(ctx.exception).startswith(
            "invalid authority manifest — refusing to proceed:\n  L: sha256 'x'"))

    def test_CONTROL_a_validator_without_the_mutable_token_rule_is_caught(self):
        with mock.patch.object(authority, "_MUTABLE_KEY_TOKENS", ()):
            with self.assertRaises(AssertionError):
                self.law_every_mutable_pointer_token_is_refused()

    def test_CONTROL_a_validator_without_the_schema_gate_is_caught(self):
        with mock.patch.object(authority, "SCHEMA", None):
            with self.assertRaises(AssertionError):
                self.assert_rejected(valid_manifest(schema=None), "unknown schema")


# ===========================================================================
# 2. succession
# ===========================================================================

class TestSuccession(unittest.TestCase):

    PRIOR = valid_manifest(sha256="c" * 64, object_path=authority.object_key_for("c" * 64),
                           snapshot_id="prior-0001")

    def check(self, succession):
        """The succession law, as a reusable guard so a rigged owner can be fed to it."""
        prior = self.PRIOR
        ok = valid_manifest(snapshot_id="next-0002", previous_snapshot_hash="c" * 64)
        assert succession(valid_manifest(), None) == []
        assert any("second genesis" in x for x in succession(valid_manifest(), prior))
        assert succession(ok, prior) == []
        assert any("does not match the sha256 of the prior" in x
                   for x in succession(dict(ok, previous_snapshot_hash="a" * 64), prior))
        assert any("NO prior tracked manifest" in x for x in succession(ok, None))
        assert any("cannot succeed themselves" in x
                   for x in succession(dict(ok, sha256="c" * 64), prior))
        assert any("PRIOR manifest is itself invalid" in x
                   for x in succession(ok, dict(prior, sha256="zz")))
        params = list(inspect.signature(succession).parameters)
        assert params == ["candidate", "prior", "label"], params

    def test_succession_is_checked_against_the_prior_tracked_manifest(self):
        self.check(authority.validate_succession)

    def test_the_kernel_owns_no_transport_at_all(self):
        self.assertEqual(_imports(PKG / "authority.py") & {
            "mtj_foundry.authority_transport", "subprocess", "socket"}, set())

    def test_build_manifest_refuses_a_wrong_link(self):
        with tempfile.TemporaryDirectory() as td:
            cb = Path(td) / "cb.json"
            cb.write_text(json.dumps({"schema": codebook.SCHEMA_V2, "version": "0.7", "axes": {}}),
                          encoding="utf-8")
            with self.assertRaises(authority.ManifestInvalidError):
                authority.build_manifest("s", "2026-08-14T12:00:00Z", "mr", "2026-07-04", None,
                                         cb, prior=self.PRIOR)
            built = authority.build_manifest("s", "2026-08-14T12:00:00Z", "mr", "2026-07-04",
                                             "c" * 64, cb, prior=self.PRIOR)
            self.assertEqual(built["previous_snapshot_hash"], "c" * 64)
            self.assertEqual(built["sha256"], authority.sha256_of_file(cb))

    def test_CONTROL_succession_from_the_newest_remote_is_caught(self):
        newest_remote = {"sha": "a" * 64}

        def rigged(candidate, prior=None, label="candidate", transport=None):
            # "succession" answered from whatever the remote says is newest
            return [] if candidate.get("previous_snapshot_hash") in (None, newest_remote["sha"]) \
                else ["mismatch"]

        with self.assertRaises(AssertionError):
            self.check(rigged)

    def test_CONTROL_succession_that_trusts_the_caller_is_caught(self):
        with self.assertRaises(AssertionError):
            self.check(lambda candidate, prior=None, label="candidate": [])


# ===========================================================================
# 3. exact-byte verification
# ===========================================================================

class TestExactVerification(unittest.TestCase):

    def check(self, verify):
        size = len(FIX)
        assert verify(FSHA, size, FIX)[0]
        flipped = bytes([FIX[0] ^ 1]) + FIX[1:]
        same_size = bytes(b ^ 0xFF for b in FIX)
        assert not verify(FSHA, size, flipped)[0]
        assert not verify(FSHA, size, same_size)[0]
        assert not verify(FSHA, size, FIX[:-1])[0]
        assert not verify(FSHA, size, FIX + b"x")[0]
        assert not verify(FSHA, size, b"")[0]
        with tempfile.TemporaryDirectory() as td:
            ok, why = verify(FSHA, size, Path(td) / "missing")
            assert not ok and "does not exist" in why
            assert not verify(FSHA, size, Path(td))[0]
        assert not verify(FSHA.upper(), size, FIX)[0]
        assert not verify(FSHA, True, FIX)[0]

    def test_size_and_sha_are_both_required(self):
        self.check(authority.verify_exact)

    def test_verify_or_raise_is_typed(self):
        with self.assertRaises(authority.ByteVerificationError):
            authority.verify_or_raise(FSHA, len(FIX), FIX[:-1])

    def test_CONTROL_a_size_only_verifier_is_caught(self):
        def size_only(sha, size, target):
            data = target if isinstance(target, (bytes, bytearray)) else (
                Path(target).read_bytes() if Path(target).is_file() else None)
            if data is None:
                return False, "does not exist"
            return len(data) == size, "size"
        with self.assertRaises(AssertionError):
            self.check(size_only)


# ===========================================================================
# 4. transport laws
# ===========================================================================

class _NoCheckBucketRunner(FakeRunner):
    """LAW B, modelled: a bucket-scoped credential 403s on the CreateBucket
    precheck BEFORE the real operation whenever the flag is absent."""

    def __call__(self, argv):
        if "--s3-no-check-bucket" not in argv:
            self.calls.append(list(argv))
            return 1, "", "operation error S3: CreateBucket, StatusCode: 403, AccessDenied"
        return super().__call__(argv)


class TestTransportLaws(unittest.TestCase):

    def put(self, runner, size=None, cls=authority_transport.RcloneTransport, src_bytes=FIX):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "payload"
            src.write_bytes(src_bytes)
            t = transport(runner, cls=cls)
            return t.put_immutable(KEY, src, FSHA, len(FIX) if size is None else size)

    # --- the laws, each written as a reusable guard ---------------------------

    def law_every_argv_carries_no_check_bucket(self, cls):
        runner = _NoCheckBucketRunner()
        assert self.put(runner, cls=cls) == "uploaded"
        t = transport(runner, cls=cls)
        t.stat(KEY)
        with tempfile.TemporaryDirectory() as td:
            t.get_verified(KEY, Path(td) / "back", FSHA, len(FIX))
        assert runner.calls and all("--s3-no-check-bucket" in c for c in runner.calls)

    def law_conditional_create(self, cls):
        runner = FakeRunner(race_injects={KEY: b"INTRUDER\n"})
        try:
            out = self.put(runner, cls=cls)
        except authority_transport.TransportError as e:
            assert "IMMUTABLE-KEY COLLISION" in str(e), e
        else:
            raise AssertionError(f"lost race with different bytes returned {out!r}")
        assert runner.objects[KEY] == b"INTRUDER\n", "the occupant was overwritten"
        assert all(authority_transport.CONDITIONAL_CREATE_HEADER in c for c in uploads(runner))

    def law_ignore_times(self, cls):
        runner = FakeRunner(race_injects={KEY: FIX})
        out = self.put(runner, cls=cls)
        assert out == "already-present-raced", out
        assert uploads(runner) and all("--ignore-times" in c for c in uploads(runner))

    def law_retries_one_and_single_put_cutoff(self, cls):
        runner = FakeRunner()
        self.put(runner, cls=cls)
        for c in uploads(runner):
            assert c[c.index("--retries") + 1] == "1", c
            assert c[c.index("--s3-upload-cutoff") + 1] == authority_transport.SINGLE_PUT_CUTOFF

    def law_multipart_refused(self, cls=authority_transport.RcloneTransport):
        # The measured cutoff, stated as a number here so a rigged constant in the
        # owner cannot move the payload along with the limit.
        runner = FakeRunner()
        assert authority_transport.SINGLE_PUT_CUTOFF == "200Mi"
        try:
            self.put(runner, size=200 * 1024 * 1024, cls=cls)
        except authority_transport.TransportError as e:
            assert "UNPROVEN" in str(e), e
        else:
            raise AssertionError("a multipart-sized payload was accepted")
        assert runner.calls == [], runner.calls

    # --- green against the owner ---------------------------------------------

    def test_every_argv_carries_s3_no_check_bucket(self):
        self.law_every_argv_carries_no_check_bucket(authority_transport.RcloneTransport)

    def test_conditional_create_carries_if_none_match(self):
        self.law_conditional_create(authority_transport.RcloneTransport)

    def test_ignore_times_is_on_the_conditional_create(self):
        self.law_ignore_times(authority_transport.RcloneTransport)

    def test_retries_one_and_the_explicit_single_put_cutoff(self):
        self.law_retries_one_and_single_put_cutoff(authority_transport.RcloneTransport)

    def test_multipart_payload_is_refused_before_any_remote_contact(self):
        self.law_multipart_refused()

    def test_absent_key_uploads_and_reads_back(self):
        runner = FakeRunner()
        self.assertEqual(self.put(runner), "uploaded")
        verbs = [(c[1], ":" in c[2]) for c in runner.calls]
        self.assertEqual(verbs, [("lsjson", True), ("copyto", False), ("copyto", True)])

    def test_occupied_identical_is_idempotent_without_an_upload(self):
        runner = FakeRunner(objects={KEY: FIX})
        self.assertEqual(self.put(runner), "already-present")
        self.assertEqual(uploads(runner), [])

    def test_occupied_different_is_refused_and_the_occupant_preserved(self):
        runner = FakeRunner(objects={KEY: b"OTHER\n"})
        with self.assertRaisesRegex(authority_transport.TransportError, "IMMUTABILITY VIOLATION REFUSED"):
            self.put(runner)
        self.assertEqual(runner.objects[KEY], b"OTHER\n")
        self.assertEqual(uploads(runner), [])

    def test_unreadable_occupant_is_unknown_not_a_violation(self):
        runner = FakeRunner(objects={KEY: FIX}, lie_on_get=True)
        with self.assertRaisesRegex(authority_transport.TransportError, "OCCUPANT UNREADABLE"):
            self.put(runner)

    def test_upload_failure_that_is_not_a_412_is_not_a_race(self):
        class Refusing(FakeRunner):
            def __call__(self, argv):
                if argv[1] == "copyto" and ":" in argv[3]:
                    self.calls.append(list(argv))
                    return 1, "", "StatusCode: 403 AccessDenied"
                return super().__call__(argv)
        runner = Refusing()
        with self.assertRaisesRegex(authority_transport.TransportError, r"copyto \(upload\) failed"):
            self.put(runner)
        self.assertEqual([c for c in runner.calls if c[1] == "copyto" and ":" in c[2]], [])

    def test_unverified_local_bytes_are_never_published(self):
        runner = FakeRunner()
        with self.assertRaisesRegex(authority_transport.TransportError, "unverified local bytes"):
            self.put(runner, src_bytes=FIX[:-1] + b"X")
        self.assertEqual(runner.calls, [])

    def test_412_detector_matches_the_verbatim_measured_stderr(self):
        f = authority_transport.RcloneTransport._is_precondition_failure
        self.assertTrue(f(1, authority_transport.MEASURED_412_STDERR))
        self.assertFalse(f(0, authority_transport.MEASURED_412_STDERR))
        self.assertFalse(f(1, "StatusCode: 403 AccessDenied"))
        self.assertFalse(f(0, authority_transport.MEASURED_SKIP_STDOUT))

    def test_exact_key_stat_refuses_ambiguity_and_failure(self):
        class Rows(FakeRunner):
            def __init__(self, out, rc=0):
                super().__init__()
                self.out, self.rc = out, rc

            def __call__(self, argv):
                self.calls.append(list(argv))
                return self.rc, self.out, "boom"
        self.assertIsNone(transport(Rows("[]")).stat(KEY))
        self.assertEqual(transport(Rows(json.dumps([{"Size": 3, "Name": "n"}]))).stat(KEY),
                         {"size": 3, "name": "n"})
        for runner, needle in ((Rows(json.dumps([{}, {}])), "ambiguous"),
                               (Rows("{"), "unparseable"), (Rows("[]", rc=1), "lsjson failed")):
            with self.subTest(needle=needle), self.assertRaisesRegex(
                    authority_transport.TransportError, needle):
                transport(runner).stat(KEY)

    def test_fetch_success_without_a_file_is_not_success(self):
        for runner in (FakeRunner(objects={KEY: FIX}, lie_on_get=True), FakeRunner()):
            with tempfile.TemporaryDirectory() as td, self.subTest(runner=runner.objects):
                dest = Path(td) / "out.json"
                with self.assertRaisesRegex(authority_transport.TransportError, "does not exist"):
                    transport(runner).get_verified(KEY, dest, FSHA, len(FIX))
                self.assertFalse(dest.exists())

    def test_corrupt_truncated_and_same_size_fetches_fail_verification(self):
        for payload in (FIX[:-1], bytes(b ^ 0xFF for b in FIX), FIX + b"!"):
            with tempfile.TemporaryDirectory() as td, self.subTest(payload=payload):
                with self.assertRaisesRegex(authority_transport.TransportError, "verification FAILED"):
                    transport(FakeRunner(objects={KEY: payload})).get_verified(
                        KEY, Path(td) / "out", FSHA, len(FIX))

    def test_a_stale_destination_is_never_mistaken_for_a_fetch(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out"
            dest.write_bytes(FIX)
            with self.assertRaises(authority_transport.TransportError):
                transport(FakeRunner()).get_verified(KEY, dest, FSHA, len(FIX))
            self.assertFalse(dest.exists())

    def test_the_transport_has_no_enumeration_or_mutation_verb(self):
        names = {n for n in dir(authority_transport.RcloneTransport) if not n.startswith("__")}
        for verb in ("list", "ls", "latest", "newest", "discover", "delete", "remove", "purge",
                     "prune", "promote", "overwrite", "sync", "move"):
            self.assertFalse([n for n in names if verb in n.lower()], verb)
        source = (PKG / "authority_transport.py").read_text(encoding="utf-8")
        verbs = {node.args[0].value for node in ast.walk(ast.parse(source))
                 if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                 and node.func.attr == "_argv" and node.args
                 and isinstance(node.args[0], ast.Constant)}
        self.assertEqual(verbs, {"lsjson", "copyto"})

    def test_the_remote_is_a_bare_name_and_the_boundary_is_required(self):
        for bad in ("", "remote:bucket"):
            with self.subTest(bad=bad), self.assertRaises(authority_transport.TransportError):
                authority_transport.RcloneTransport(bad, forbidden_destinations=_no_forbidden)
        with self.assertRaises(TypeError):
            authority_transport.RcloneTransport("fake-remote")
        with self.assertRaises(authority_transport.TransportError):
            authority_transport.RcloneTransport("fake-remote", forbidden_destinations=set())

    # --- controls: each law RED against a transport with it rigged away ------

    def _rigged(self, drop):
        class Rigged(authority_transport.RcloneTransport):
            def _argv(self, *args, conditional_create=False):
                argv = super()._argv(*args, conditional_create=conditional_create)
                out = []
                skip = 0
                for i, a in enumerate(argv):
                    if skip:
                        skip -= 1
                        continue
                    if a == drop:
                        skip = 1 if drop in ("--header-upload", "--retries") else 0
                        continue
                    out.append(a)
                return out
        return Rigged

    def test_CONTROL_missing_s3_no_check_bucket_is_caught(self):
        with self.assertRaises((AssertionError, authority_transport.TransportError)):
            self.law_every_argv_carries_no_check_bucket(self._rigged("--s3-no-check-bucket"))

    def test_CONTROL_missing_if_none_match_is_caught(self):
        with self.assertRaises(AssertionError):
            self.law_conditional_create(self._rigged("--header-upload"))

    def test_CONTROL_missing_ignore_times_is_caught(self):
        with self.assertRaises(AssertionError):
            self.law_ignore_times(self._rigged("--ignore-times"))

    def test_CONTROL_missing_retries_one_is_caught(self):
        with self.assertRaises((AssertionError, ValueError)):
            self.law_retries_one_and_single_put_cutoff(self._rigged("--retries"))

    def test_CONTROL_a_permitted_multipart_payload_is_caught(self):
        with mock.patch.object(authority_transport, "SINGLE_PUT_LIMIT_BYTES", 1 << 62):
            with self.assertRaises(AssertionError):
                self.law_multipart_refused()


# ===========================================================================
# 5. the staging boundary
# ===========================================================================

class TestStagingBoundary(unittest.TestCase):

    def law_refuses_declared_destination(self, make_transport):
        with tempfile.TemporaryDirectory() as td:
            decoy = Path(td) / "pretend-operational-codebook.json"
            decoy.write_text('{"canary": "must survive"}', encoding="utf-8")
            runner = FakeRunner(objects={KEY: FIX})
            t = make_transport(runner, decoy)
            try:
                t.get_verified(KEY, decoy, FSHA, len(FIX))
            except authority_transport.TransportError as e:
                assert "OPERATIONAL codebook" in str(e), e
            else:
                raise AssertionError("the declared operational path was accepted as staging")
            assert decoy.read_text(encoding="utf-8") == '{"canary": "must survive"}'
            assert runner.calls == [], runner.calls

    def test_the_declared_operational_codebook_is_refused_before_any_io(self):
        self.law_refuses_declared_destination(
            lambda runner, decoy: transport(runner, forbidden=lambda: {decoy}))

    def test_the_declaration_is_consulted_at_every_fetch(self):
        with tempfile.TemporaryDirectory() as td:
            decoy = Path(td) / "later.json"
            declared = set()
            t = transport(FakeRunner(objects={KEY: FIX}), forbidden=lambda: set(declared))
            t.get_verified(KEY, decoy, FSHA, len(FIX))       # not yet forbidden
            declared.add(decoy)
            with self.assertRaisesRegex(authority_transport.TransportError, "OPERATIONAL"):
                t.get_verified(KEY, decoy, FSHA, len(FIX))

    def test_restore_cannot_stage_onto_the_declared_operational_codebook(self):
        with tempfile.TemporaryDirectory() as td:
            staging = Path(td) / "staging"
            staged = staging / "codebook.staged.json"
            staging.mkdir()
            staged.write_text("canary", encoding="utf-8")
            runner = FakeRunner(objects={KEY: FIX})
            t = transport(runner, forbidden=lambda: {staged})
            with self.assertRaisesRegex(authority_transport.TransportError, "OPERATIONAL"):
                authority_restore.restore_snapshot(valid_manifest(), t, staging, Path(td) / "dest.json")
            self.assertEqual(staged.read_text(encoding="utf-8"), "canary")
            self.assertEqual(runner.calls, [])

    def test_the_shell_keeps_both_arms_and_the_immovable_one_survives_rigging(self):
        real = LEGACY._IMMOVABLE_FORBIDDEN_DESTINATIONS
        self.assertEqual(real, frozenset({LEGACY.fcb.CODEBOOK_PATH.resolve()}))
        self.law_refuses_declared_destination(self._shell_transport_with_rebound_arm)
        with tempfile.TemporaryDirectory() as td:
            saved = LEGACY.OPERATIONAL_CODEBOOK_PATH
            LEGACY.OPERATIONAL_CODEBOOK_PATH = (Path(td) / "decoy.json").resolve()
            try:
                target = next(iter(real))
                self.assertIn(target, LEGACY._forbidden_fetch_destinations())
                with self.assertRaisesRegex(authority_transport.TransportError, "OPERATIONAL"):
                    LEGACY._refuse_operational_destination(target)   # predicate: no I/O
            finally:
                LEGACY.OPERATIONAL_CODEBOOK_PATH = saved

    @staticmethod
    def _shell_transport_with_rebound_arm(runner, decoy):
        LEGACY.OPERATIONAL_CODEBOOK_PATH = decoy.resolve()
        return LEGACY.RcloneTransport("fake-remote", runner=runner)

    def tearDown(self):
        LEGACY.OPERATIONAL_CODEBOOK_PATH = LEGACY.fcb.CODEBOOK_PATH.resolve()

    def test_CONTROL_a_transport_that_ignores_the_declaration_is_caught(self):
        class Ignoring(authority_transport.RcloneTransport):
            def get_verified(self, key, dest, expected_sha, expected_size):
                self._forbidden_destinations = lambda: set()
                return super().get_verified(key, dest, expected_sha, expected_size)
        with self.assertRaises(AssertionError):
            self.law_refuses_declared_destination(
                lambda runner, decoy: transport(runner, forbidden=lambda: {decoy}, cls=Ignoring))


# ===========================================================================
# 6. authority states
# ===========================================================================

def _small_codebook(path: Path):
    path.write_text(json.dumps({"schema": codebook.SCHEMA_V2, "version": "0.7", "axes": {
        "rule:a": {"status": "active", "members": [
            {"oracle_id": "x", "assertions": [{"class": "human"}, {"class": "rule-derived"}]}]},
        "rule:dead": {"status": "killed", "members": []}}}), encoding="utf-8")


class _Spy:
    """A transport that records what status asked of it, and can be made to fail."""

    def __init__(self, meta=None, fail=False):
        self.meta, self.fail, self.calls = meta, fail, []

    def stat(self, key):
        self.calls.append(("stat", key))
        if self.fail:
            raise authority_transport.TransportError("unreachable")
        return self.meta

    def __getattr__(self, name):
        def forbidden(*a, **k):
            self.calls.append((name, a))
            raise AssertionError(f"status called transport.{name}")
        return forbidden


class TestAuthorityStates(unittest.TestCase):

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.td = Path(self._td.name)
        self.cb = self.td / "codebook.json"
        _small_codebook(self.cb)
        self.match = valid_manifest(sha256=authority.sha256_of_file(self.cb),
                                    byte_size=self.cb.stat().st_size)
        self.match["object_path"] = authority.object_key_for(self.match["sha256"])

    def tearDown(self):
        self._td.cleanup()

    def write(self, name, manifest):
        p = self.td / name
        p.write_text(manifest if isinstance(manifest, str) else authority.serialize_manifest(manifest),
                     encoding="utf-8")
        return p

    def test_all_six_states(self):
        s = authority_status
        absent = self.td / "absent.json"
        self.assertEqual(s.status(absent, self.cb)["state"], "AUTHORITY_NOT_INITIALIZED")
        self.assertEqual(s.status(self.write("m.json", self.match), self.cb)["state"],
                         "LOCAL_MATCHES_AUTHORITY")
        self.assertEqual(s.status(self.write("x.json", valid_manifest()), self.cb)["state"],
                         "LOCAL_CANDIDATE_AUTHORITY_MISMATCH")
        self.assertEqual(s.status(self.write("bad.json", "nope"), self.cb)["state"], "MANIFEST_INVALID")
        self.assertEqual(s.status(self.write("m.json", self.match), self.cb,
                                  _Spy(meta=None))["state"], "AUTHORITY_UNVERIFIABLE")
        self.assertEqual(s.status(self.write("m.json", self.match), self.td / "none.json")["state"],
                         "NO_LOCAL_CODEBOOK")
        self.assertEqual((s.STATE_NOT_INITIALIZED, s.STATE_LOCAL_MATCHES, s.STATE_MISMATCH,
                          s.STATE_MANIFEST_INVALID, s.STATE_UNVERIFIABLE, s.STATE_NO_LOCAL),
                         ("AUTHORITY_NOT_INITIALIZED", "LOCAL_MATCHES_AUTHORITY",
                          "LOCAL_CANDIDATE_AUTHORITY_MISMATCH", "MANIFEST_INVALID",
                          "AUTHORITY_UNVERIFIABLE", "NO_LOCAL_CODEBOOK"))

    def test_unverifiable_is_never_resolved_by_finding_another_object(self):
        m = self.write("m.json", self.match)
        for spy in (_Spy(meta=None), _Spy(fail=True), _Spy(meta={"size": 1})):
            with self.subTest(meta=spy.meta, fail=spy.fail):
                st = authority_status.status(m, self.cb, spy)
                self.assertEqual(st["state"], "AUTHORITY_UNVERIFIABLE")
                self.assertEqual(spy.calls, [("stat", self.match["object_path"])])

    # --- guards written against a status callable -----------------------------

    def law_invalid_manifest_never_consults_the_remote(self, status_fn):
        for name, body in (("bad.json", "{not json"),
                           ("inv.json", json.dumps(dict(self.match, object_path="foundry/latest.json")))):
            spy = _Spy(meta={"size": 1})
            st = status_fn(self.write(name, body), self.cb, spy)
            assert st["state"] == "MANIFEST_INVALID", st["state"]
            assert spy.calls == [], spy.calls

    def law_mismatch_is_reported_not_repaired(self, status_fn):
        before = self.cb.read_bytes()
        spy = _Spy(meta={"size": 27})
        st = status_fn(self.write("x.json", valid_manifest()), self.cb, spy)
        assert st["state"] == "LOCAL_CANDIDATE_AUTHORITY_MISMATCH", st["state"]
        assert self.cb.read_bytes() == before, "the local codebook was modified"
        assert [c[0] for c in spy.calls] == ["stat"], spy.calls

    def law_candidate_is_never_promoted(self, status_fn):
        cand = dict(self.match, snapshot_id="uploaded-candidate")
        spy = _Spy(meta={"size": self.match["byte_size"]})
        absent = self.td / "absent.json"
        without = status_fn(absent, self.cb, spy)
        st = status_fn(absent, self.cb, spy, cand)
        assert st["state"] == without["state"] == "AUTHORITY_NOT_INITIALIZED", st["state"]
        c = st["candidate"]
        assert c["authoritative"] is False and c["classification"] == "ORPHAN_CANDIDATE", c
        assert c["remote"].startswith("present"), c
        assert "selected" not in st

    def test_invalid_manifest_never_consults_the_remote(self):
        self.law_invalid_manifest_never_consults_the_remote(authority_status.status)

    def test_mismatch_is_reported_never_repaired(self):
        self.law_mismatch_is_reported_not_repaired(authority_status.status)

    def test_an_existing_remote_candidate_is_not_authority(self):
        self.law_candidate_is_never_promoted(authority_status.status)

    def test_status_owns_no_mutation_path(self):
        tree = ast.parse((PKG / "authority_status.py").read_text(encoding="utf-8"))
        attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        self.assertEqual(attrs & {"put_immutable", "get_verified", "_fetch_raw", "write_text",
                                  "write_bytes", "replace", "unlink", "install_atomic"}, set())

    def test_CONTROL_a_status_that_falls_back_to_the_remote_is_caught(self):
        def rigged(manifest_path, codebook_path, transport=None, candidate=None):
            st = authority_status.status(manifest_path, codebook_path, transport, candidate)
            if st["state"] == "MANIFEST_INVALID" and transport is not None:
                transport.stat("foundry/codebook/newest")
            return st
        with self.assertRaises(AssertionError):
            self.law_invalid_manifest_never_consults_the_remote(rigged)

    def test_CONTROL_a_status_that_repairs_the_mismatch_is_caught(self):
        def rigged(manifest_path, codebook_path, transport=None, candidate=None):
            st = authority_status.status(manifest_path, codebook_path, transport, candidate)
            if st["state"] == "LOCAL_CANDIDATE_AUTHORITY_MISMATCH":
                Path(codebook_path).write_bytes(FIX)
            return st
        with self.assertRaises(AssertionError):
            self.law_mismatch_is_reported_not_repaired(rigged)

    def test_CONTROL_a_status_that_promotes_a_candidate_is_caught(self):
        def rigged(manifest_path, codebook_path, transport=None, candidate=None):
            st = authority_status.status(manifest_path, codebook_path, transport, candidate)
            if candidate is not None and st.get("candidate", {}).get("remote", "").startswith("present"):
                st["state"] = "LOCAL_MATCHES_AUTHORITY"
            return st
        with self.assertRaises(AssertionError):
            self.law_candidate_is_never_promoted(rigged)


# ===========================================================================
# 7. restore ordering
# ===========================================================================

@unittest.skipUnless(OPERATIONAL.exists(), "restore fixtures derive from the selected codebook")
class TestRestoreOrder(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        live = json.loads(OPERATIONAL.read_text(encoding="utf-8"))
        active = sorted((s, e) for s, e in live["axes"].items() if e.get("status") == "active")
        slug, entry = min(active, key=lambda kv: len(kv[1].get("members") or []))
        mini = {k: v for k, v in live.items() if k != "axes"}
        mini["axes"] = {slug: entry}
        cls.mini = mini

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.td = Path(self._td.name)
        src = self.td / "source.json"
        src.write_text(json.dumps(self.mini, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        self.good = src.read_bytes()
        self.manifest = authority.build_manifest("restore-fixture", "2026-08-14T12:00:00Z",
                                                 "s12", "2026-07-04", None, src)

    def tearDown(self):
        self._td.cleanup()

    def run_restore(self, payload=None, manifest=None, t=None, dest=None, **kw):
        manifest = manifest or self.manifest
        runner = FakeRunner(objects={manifest["object_path"]: self.good if payload is None else payload})
        dest = dest or self.td / "installed" / "codebook.json"
        t = t or transport(runner)
        return authority_restore.restore_snapshot(manifest, t, self.td / "staging", dest, **kw), dest

    def law_install_only_after_verify_and_validate(self, module):
        """Feed every pre-install failure through `module.restore_snapshot` with
        install spied. Install must never be reached, and the destination never
        created."""
        seen = []
        real_install = module.install_atomic

        def spy(*a, **k):
            seen.append("install")
            return real_install(*a, **k)

        class Tamper(authority_transport.RcloneTransport):
            def get_verified(self, key, dest, s, z):
                p = super().get_verified(key, dest, s, z)
                b = bytearray(Path(p).read_bytes())
                b[5] ^= 0xFF
                Path(p).write_bytes(bytes(b))
                return p

        junk = b'{"not": "a codebook"}\n'
        junk_m = valid_manifest(sha256=hashlib.sha256(junk).hexdigest(), byte_size=len(junk))
        junk_m["object_path"] = authority.object_key_for(junk_m["sha256"])
        corrupt = bytearray(self.good)
        corrupt[10] ^= 0xFF
        lying = dict(self.manifest, assertion_count=self.manifest["assertion_count"] + 1)
        cases = {
            "corrupt": dict(payload=bytes(corrupt)),
            "junk": dict(payload=junk, manifest=junk_m),
            "facts": dict(manifest=lying),
            "tamper": dict(t=Tamper("fake-remote", forbidden_destinations=_no_forbidden,
                                    runner=FakeRunner(objects={self.manifest["object_path"]: self.good}))),
        }
        with mock.patch.object(module, "install_atomic", spy):
            for name, kw in cases.items():
                dest = self.td / name / "codebook.json"
                try:
                    self.run_restore(dest=dest, **kw)
                except (authority_transport.TransportError, authority_restore.RestoreError):
                    pass
                else:
                    raise AssertionError(f"{name}: restore completed")
                assert not dest.exists(), f"{name}: destination written"
        assert seen == [], f"install reached: {seen}"

    def test_happy_path_trace_is_exactly_fetch_verify_validate_install(self):
        res, dest = self.run_restore()
        self.assertEqual(res["trace"], ["fetch", "verify", "validate", "install"])
        self.assertEqual(authority.sha256_of_file(dest), self.manifest["sha256"])
        self.assertEqual(authority_restore.RESTORE_STEPS, ("fetch", "verify", "validate", "install"))

    def test_install_is_unreachable_unless_fetch_verify_validate_all_passed(self):
        self.law_install_only_after_verify_and_validate(authority_restore)

    def test_each_pre_install_failure_names_its_own_step(self):
        corrupt = bytearray(self.good)
        corrupt[10] ^= 0xFF
        with self.assertRaisesRegex(authority_transport.TransportError, "verification FAILED"):
            self.run_restore(payload=bytes(corrupt))
        with self.assertRaisesRegex(authority_transport.TransportError, "does not exist"):
            self.run_restore(t=transport(FakeRunner()))
        with self.assertRaisesRegex(authority_restore.RestoreError, "does not match the manifest"):
            self.run_restore(manifest=dict(self.manifest, assertion_count=self.manifest["assertion_count"] + 1))
        with self.assertRaises(authority.ManifestInvalidError):
            self.run_restore(manifest=dict(self.manifest, bucket=""))

    def test_a_staged_file_altered_after_a_good_fetch_halts_at_verify(self):
        """Step 2 earns its place only against bytes changed AFTER the fetch
        verified them; corruption in transit is already caught by the fetch.
        With step 2 removed, validation would catch this one step later, which
        is a different guarantee -- so the halt must name VERIFICATION."""
        class Tamper(authority_transport.RcloneTransport):
            def get_verified(self, key, dest, s, z):
                p = super().get_verified(key, dest, s, z)
                b = bytearray(Path(p).read_bytes())
                b[5] ^= 0xFF
                Path(p).write_bytes(bytes(b))
                return p
        runner = FakeRunner(objects={self.manifest["object_path"]: self.good})
        dest = self.td / "installed" / "codebook.json"
        with self.assertRaisesRegex(authority_restore.RestoreError, "staged bytes failed verification"):
            self.run_restore(t=Tamper("fake-remote", runner=runner, forbidden_destinations=_no_forbidden),
                             dest=dest)
        self.assertFalse(dest.exists())

    def test_staging_cannot_be_the_destination(self):
        with self.assertRaisesRegex(authority_restore.RestoreError, "same file"):
            self.run_restore(dest=self.td / "staging" / "codebook.staged.json")

    def test_existing_destination_is_never_silently_replaced(self):
        dest = self.td / "existing.json"
        dest.write_bytes(b'{"old": true}\n')
        with self.assertRaisesRegex(authority_restore.RestoreError, "explicit instruction"):
            self.run_restore(dest=dest)
        with self.assertRaisesRegex(authority_restore.RestoreError, "no backup"):
            self.run_restore(dest=dest, replace_existing=True)
        self.assertEqual(dest.read_bytes(), b'{"old": true}\n')
        backed = []
        res, _ = self.run_restore(dest=dest, replace_existing=True, backup=backed.append)
        self.assertEqual(backed, [dest])
        self.assertEqual(res["sha256"], self.manifest["sha256"])

    def test_install_refuses_unverified_bytes(self):
        bogus = self.td / "bogus"
        bogus.write_bytes(b"nope\n")
        with self.assertRaisesRegex(authority_restore.RestoreError, "REFUSING TO INSTALL"):
            authority_restore.install_atomic(bogus, self.td / "never.json", self.manifest["sha256"],
                                             self.manifest["byte_size"])
        self.assertFalse((self.td / "never.json").exists())

    def test_CONTROL_a_restore_that_installs_before_validation_is_caught(self):
        with mock.patch.object(authority_restore, "validate_codebook_payload",
                               lambda path, manifest: {"axes": 0, "lint": {}}):
            with self.assertRaises(AssertionError):
                self.law_install_only_after_verify_and_validate(authority_restore)


# ===========================================================================
# 8. the shell is a boundary, not a second implementation
# ===========================================================================

LAW_FUNCTIONS = {
    "authority": ("object_key_for", "serialize_manifest", "validate_manifest", "validate_or_raise",
                  "validate_succession", "load_manifest", "sha256_of_bytes", "sha256_of_file",
                  "verify_exact", "verify_or_raise", "describe_local", "derive_manifest_facts",
                  "build_manifest", "compare_manifest_to_codebook"),
    "authority_transport": ("refuse_forbidden_destination", "default_runner"),
    "authority_status": ("describe_candidate", "status"),
    "authority_restore": ("validate_codebook_payload", "install_atomic", "restore_snapshot"),
}
TRANSPORT_METHODS = ("_argv", "_is_precondition_failure", "_remote_path", "_redact", "stat",
                     "get_verified", "_fetch_raw", "_occupant_state", "put_immutable")
LAW_MARKERS = ("If-None-Match", "--ignore-times", "--s3-no-check-bucket", "--retries",
               "--s3-upload-cutoff", "PreconditionFailed", "StatusCode: 412",
               "foundry/codebook/sha256", "restore-tmp")
SHELL = "experiments/foundry_authority.py"
# Same NAME, different subject, and declared rather than pattern-excused so a new
# homonym still fails: AQ4's frozen surface-projection manifest (S14's to move)
# and the site publisher's artifact manifest. Neither reads or writes a
# `foundry-authority/1` document. May shrink; may not grow.
UNRELATED_HOMONYMS = {
    ("experiments/aq4_benchmark/aq4_projection.py", "build_manifest"),
    ("experiments/aq4_benchmark/aq4_projection.py", "validate_manifest"),
    ("pipeline/upload.py", "build_manifest"),
}
# The shell's test rigs, which reconstruct the laws ON PURPOSE to prove them.
SHELL_RIGS = {"selftest", "FakeRunner"}
SHELL_DELEGATE_MODULES = {"_authority", "_transport", "_status", "_restore"}


def _tracked_production_python():
    listed = subprocess.run(["git", "-C", str(REPO_ROOT), "ls-files", "-z", "*.py"],
                            capture_output=True, check=True).stdout.decode().split("\0")
    return {p: (REPO_ROOT / p).read_text(encoding="utf-8") for p in listed
            if p and p.startswith(("experiments/", "pipeline/", "src/")) and (REPO_ROOT / p).exists()}


def _top_level_defs(tree):
    """(qualname, node) for module-level functions/classes and methods of
    module-level classes. Classes nested inside functions are rigs, not owners."""
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            yield node.name, node
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        yield f"{node.name}.{item.name}", item


def _is_pure_delegate(fn: ast.FunctionDef) -> bool:
    """Body is (docstring?) + `return _stop_on_refusal(<owner>.<same name>, ...)`:
    one call into a permanent owner, read off the owner module at call time and
    crossing the shell's single process boundary. `*_or_halt` maps to the owner's
    `*_or_raise`."""
    body = list(fn.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        body = body[1:]
    if len(body) != 1 or not isinstance(body[0], (ast.Return, ast.Expr)):
        return False
    call = body[0].value
    if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
            and call.func.id == "_stop_on_refusal" and call.args):
        return False
    target = call.args[0]
    return isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) \
        and target.value.id in SHELL_DELEGATE_MODULES \
        and target.attr in {fn.name, fn.name.replace("_or_halt", "_or_raise")}


def _is_the_boundary(fn: ast.FunctionDef) -> bool:
    """`_stop_on_refusal` catches EXACTLY `_authority.AuthorityRefusal` and halts."""
    body = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
    if len(body) != 1 or not isinstance(body[0], ast.Try):
        return False
    t = body[0]
    return (len(t.handlers) == 1 and not t.orelse and not t.finalbody
            and ast.unparse(t.body[0]) == "return owner_call(*args, **kwargs)" and len(t.body) == 1
            and ast.unparse(t.handlers[0].type) == "_authority.AuthorityRefusal"
            and [ast.unparse(x) for x in t.handlers[0].body] == [f"fc.halt(str({t.handlers[0].name}))"])


def law_census(sources: dict) -> dict:
    """Every definition of an S12 law name, and every law marker literal, found
    outside the permanent owners -- the shell's pure delegates and its selftest
    rigs excepted. Empty means one implementation."""
    law_names = {n for fs in LAW_FUNCTIONS.values() for n in fs} | {
        "validate_or_halt", "verify_or_halt"} | {f"RcloneTransport.{m}" for m in TRANSPORT_METHODS}
    found = {"definitions": [], "markers": []}
    for path, text in sorted(sources.items()):
        if path.startswith("src/mtj_foundry/authority"):
            continue
        tree = ast.parse(text)
        rigs = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))
                and path == SHELL and n.name in SHELL_RIGS]
        rig_nodes = {id(x) for r in rigs for x in ast.walk(r)}
        docstrings = {id(n.body[0].value) for n in ast.walk(tree)
                      if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and n.body
                      and isinstance(n.body[0], ast.Expr)}
        for qual, node in _top_level_defs(tree):
            if qual in law_names and id(node) not in rig_nodes:
                if path == SHELL and isinstance(node, ast.FunctionDef) and "." not in qual \
                        and _is_pure_delegate(node):
                    continue
                if (path, qual) not in UNRELATED_HOMONYMS:
                    found["definitions"].append((path, qual))
        for node in ast.walk(tree):
            if id(node) in rig_nodes:
                continue
            if isinstance(node, ast.Constant) and isinstance(node.value, str) \
                    and id(node) not in docstrings:
                for marker in LAW_MARKERS:
                    if marker in node.value:
                        found["markers"].append((path, marker))
    return found


class TestOneImplementation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.sources = _tracked_production_python()

    def test_every_law_name_is_defined_by_its_permanent_owner(self):
        for module, names in LAW_FUNCTIONS.items():
            owner = sys.modules[f"mtj_foundry.{module}"]
            for name in names:
                with self.subTest(owner=module, name=name):
                    self.assertEqual(getattr(owner, name).__module__, owner.__name__)
        for method in TRANSPORT_METHODS:
            self.assertIn(method, vars(authority_transport.RcloneTransport))

    def test_no_second_implementation_outside_the_owners(self):
        self.assertEqual(law_census(self.sources), {"definitions": [], "markers": []})

    def test_the_declared_homonyms_are_real_and_unrelated(self):
        for path, name in sorted(UNRELATED_HOMONYMS):
            with self.subTest(path=path, name=name):
                text = self.sources[path]
                self.assertIn(f"def {name}(", text)
                self.assertNotIn("foundry-authority/1", text)

    def test_the_shell_class_adds_no_transport_behaviour(self):
        tree = ast.parse(self.sources[SHELL])
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "RcloneTransport")
        self.assertEqual([ast.unparse(b) for b in cls.bases], ["_transport.RcloneTransport"])
        self.assertEqual([n.name for n in cls.body if isinstance(n, ast.FunctionDef)], ["__init__"])
        self.assertTrue(issubclass(LEGACY.RcloneTransport, authority_transport.RcloneTransport))

    def test_shell_error_classes_are_the_owner_classes(self):
        self.assertIs(LEGACY.TransportError, authority_transport.TransportError)
        self.assertIs(LEGACY.RestoreError, authority_restore.RestoreError)

    def test_the_shell_reaches_the_owner_at_call_time(self):
        sentinel = ["REPLACED"]
        for module, name, args in ((authority, "validate_manifest", ({},)),
                                   (authority, "validate_succession", ({}, None)),
                                   (authority, "verify_exact", (FSHA, 1, b"")),
                                   (authority_status, "status", (Path("m"), Path("c"))),
                                   (authority_restore, "restore_snapshot", ({}, None, Path("s"), Path("d")))):
            with self.subTest(name=name), mock.patch.object(module, name, lambda *a, **k: sentinel):
                self.assertIs(getattr(LEGACY, name)(*args), sentinel)
        with mock.patch.object(authority_transport.RcloneTransport, "put_immutable",
                               lambda self, *a: "REPLACED"):
            t = LEGACY.RcloneTransport("fake-remote", runner=FakeRunner())
            self.assertEqual(t.put_immutable(KEY, Path("x"), FSHA, 1), "REPLACED")

    def test_CONTROL_a_reintroduced_implementation_is_caught(self):
        sources = dict(self.sources)
        sources[SHELL] += ("\n\ndef validate_manifest(manifest, label='manifest'):\n"
                           "    return [] if isinstance(manifest, dict) else ['x']\n")
        sources["experiments/zz_s12_probe.py"] = (
            "def put(argv):\n    return argv + ['--header-upload', 'If-None-Match: *']\n")
        found = law_census(sources)
        self.assertIn((SHELL, "validate_manifest"), found["definitions"])
        self.assertIn(("experiments/zz_s12_probe.py", "If-None-Match"), found["markers"])

    def test_the_shell_has_exactly_one_process_boundary(self):
        tree = ast.parse(self.sources[SHELL])
        fns = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        self.assertTrue(_is_the_boundary(fns["_stop_on_refusal"]))
        catching = sorted(n.name for n in tree.body if isinstance(n, ast.FunctionDef)
                          and n.name not in SHELL_RIGS and not n.name.startswith("cmd_")
                          and any(isinstance(x, ast.Try) for x in ast.walk(n)))
        self.assertEqual(catching, ["_stop_on_refusal"])

    def test_CONTROL_a_delegate_that_adds_logic_is_not_a_pure_delegate(self):
        for source in ("def verify_exact(a, b, c):\n"
                       "    if a: return (True, 'x')\n"
                       "    return _stop_on_refusal(_authority.verify_exact, a, b, c)\n",
                       "def verify_exact(a, b, c):\n"
                       "    return _stop_on_refusal(_authority.validate_manifest, a)\n",
                       "def verify_exact(a, b, c):\n"
                       "    return _authority.verify_exact(a, b, c)\n"):
            with self.subTest(source=source):
                self.assertFalse(_is_pure_delegate(ast.parse(source).body[0]))
        self.assertTrue(_is_pure_delegate(ast.parse(
            "def verify_or_halt(a, b, c):\n"
            "    return _stop_on_refusal(_authority.verify_or_raise, a, b, c)\n").body[0]))

    def test_CONTROL_a_boundary_that_catches_too_much_is_caught(self):
        for source in ("def _stop_on_refusal(owner_call, *args, **kwargs):\n"
                       "    try:\n        return owner_call(*args, **kwargs)\n"
                       "    except Exception as error:\n        fc.halt(str(error))\n",
                       "def _stop_on_refusal(owner_call, *args, **kwargs):\n"
                       "    try:\n        return owner_call(*args, **kwargs)\n"
                       "    except _authority.AuthorityRefusal as error:\n        return None\n"):
            with self.subTest(source=source):
                self.assertFalse(_is_the_boundary(ast.parse(source).body[0]))


# ===========================================================================
# 9. the process boundary translates, byte-exact
# ===========================================================================

class TestProcessBoundary(unittest.TestCase):

    def assert_same_stop(self, shell_call, owner_call, error_type):
        with self.assertRaises(error_type) as ctx:
            owner_call()
        code, stderr = _halted(shell_call)
        self.assertEqual(code, 1)
        self.assertEqual(stderr, f"STOP — {ctx.exception}\n")

    def test_every_refusal_reaches_the_process_boundary_verbatim(self):
        bad = valid_manifest(sha256="x")
        incomplete = valid_manifest()
        del incomplete["schema"]
        with tempfile.TemporaryDirectory() as td:
            broken = Path(td) / "broken.json"
            broken.write_text("{{", encoding="utf-8")
            absent = Path(td) / "absent.json"
            cases = (
                (lambda: LEGACY.object_key_for("X"), lambda: authority.object_key_for("X"),
                 authority.ObjectKeyError),
                (lambda: LEGACY.serialize_manifest(incomplete),
                 lambda: authority.serialize_manifest(incomplete), authority.ManifestSerializationError),
                (lambda: LEGACY.validate_or_halt(bad, "L"), lambda: authority.validate_or_raise(bad, "L"),
                 authority.ManifestInvalidError),
                (lambda: LEGACY.verify_or_halt(FSHA, 1, b""), lambda: authority.verify_or_raise(FSHA, 1, b""),
                 authority.ByteVerificationError),
                (lambda: LEGACY.describe_local(broken), lambda: authority.describe_local(broken),
                 authority.LocalCodebookError),
                (lambda: LEGACY.derive_manifest_facts(absent), lambda: authority.derive_manifest_facts(absent),
                 authority.LocalCodebookError),
                (lambda: LEGACY.status(absent, broken), lambda: authority_status.status(absent, broken),
                 authority.LocalCodebookError),
                (lambda: LEGACY.restore_snapshot(bad, None, td, absent),
                 lambda: authority_restore.restore_snapshot(bad, None, td, absent),
                 authority.ManifestInvalidError),
            )
            for shell_call, owner_call, error_type in cases:
                with self.subTest(error=error_type.__name__):
                    self.assert_same_stop(shell_call, owner_call, error_type)

    def test_transport_and_restore_errors_stay_catchable(self):
        for error in (authority_transport.TransportError, authority_restore.RestoreError):
            self.assertFalse(issubclass(error, authority.AuthorityRefusal))

    def test_the_permanent_owners_never_exit_or_print(self):
        for name in S12_MODULES:
            tree = ast.parse((PKG / f"{name}.py").read_text(encoding="utf-8"))
            calls = {ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)}
            names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
            with self.subTest(module=name):
                self.assertEqual(calls & {"print", "sys.exit", "exit", "quit", "input"}, set())
                self.assertEqual(names & {"__file__", "SystemExit"}, set())

    def test_CONTROL_a_shell_that_swallows_the_refusal_is_caught(self):
        def swallowing():
            try:
                authority.validate_or_raise(valid_manifest(sha256="x"), "L")
            except authority.AuthorityRefusal:
                return None
        with self.assertRaises(AssertionError):
            self.assert_same_stop(swallowing, lambda: authority.validate_or_raise(
                valid_manifest(sha256="x"), "L"), authority.ManifestInvalidError)


# ===========================================================================
# 10. layering
# ===========================================================================

class TestLayering(unittest.TestCase):

    def test_each_owner_imports_exactly_its_declared_layers(self):
        for name, internal in S12_MODULES.items():
            got = _imports(PKG / f"{name}.py")
            with self.subTest(module=name):
                permanent = {m for m in got if m.startswith("mtj_foundry.")}
                self.assertEqual(permanent, internal)
                self.assertEqual({m for m in got if not m.startswith("mtj_foundry")}, S12_STDLIB[name])

    def test_one_process_owner_and_one_install_writer(self):
        spawners = {n for n in S12_MODULES if "subprocess" in _imports(PKG / f"{n}.py")}
        writers = {n for n in S12_MODULES if _imports(PKG / f"{n}.py") & {"os", "shutil"}}
        self.assertEqual(spawners, {"authority_transport"})
        self.assertEqual(writers, {"authority_restore"})

    def test_no_owner_reaches_legacy_aq4_layout_or_the_runtime(self):
        for name in S12_MODULES:
            got = _imports(PKG / f"{name}.py")
            with self.subTest(module=name):
                self.assertEqual({m for m in got if m.startswith(
                    ("foundry_", "experiments", "aq4", "tier_engine", "pipeline"))}, set())
                self.assertEqual(got & {"mtj_foundry.paths", "mtj_foundry.runtime",
                                        "mtj_foundry.cli", "mtj_foundry.corpus"}, set())

    def test_nothing_below_the_authority_layer_imports_it(self):
        for path in sorted(PKG.rglob("*.py")):
            rel = path.relative_to(PKG).as_posix()
            if rel.startswith("authority"):
                continue
            with self.subTest(module=rel):
                self.assertEqual({m for m in _imports(path) if m.startswith("mtj_foundry.authority")}, set())

    def test_the_package_graph_is_acyclic(self):
        self.assertEqual(s11.find_cycle(s11.package_graph(PKG)), [])

    def test_CONTROL_an_upward_authority_edge_is_a_cycle(self):
        g = s11.package_graph(PKG)
        g["mtj_foundry.authority"] = set(g["mtj_foundry.authority"]) | {"mtj_foundry.authority_restore"}
        self.assertIn("mtj_foundry.authority", s11.find_cycle(g))

    def test_import_with_only_src_from_an_unrelated_cwd(self):
        code = ("import sys\n"
                "import mtj_foundry.authority_restore, mtj_foundry.authority_status\n"
                "assert not [m for m in sys.modules if m.startswith(('foundry_', 'experiments'))]\n"
                "print('ok')\n")
        with tempfile.TemporaryDirectory() as td:
            out = subprocess.run([sys.executable, "-c", code], cwd=td, capture_output=True,
                                 text=True, env={"PATH": "/usr/bin:/bin", "PYTHONPATH": str(SRC)})
        self.assertEqual((out.returncode, out.stdout.strip()), (0, "ok"), out.stderr)


# ===========================================================================
# 11. conservation of the selected truth
# ===========================================================================

class TestSelectedTruth(unittest.TestCase):

    def test_the_tracked_selector_is_byte_identical_and_still_selects(self):
        self.assertEqual(hashlib.sha256(SELECTOR.read_bytes()).hexdigest(), SELECTOR_SHA256)
        manifest, violations = authority.load_manifest(SELECTOR)
        self.assertEqual(violations, [])
        self.assertEqual(authority.validate_succession(manifest, None), [])
        self.assertEqual((manifest["sha256"], manifest["byte_size"]), (SELECTED_SHA256, SELECTED_BYTES))
        self.assertEqual(authority.serialize_manifest(manifest).encode("utf-8"), SELECTOR.read_bytes())

    @unittest.skipUnless(OPERATIONAL.exists(), "the selected codebook is not staged")
    def test_the_selected_codebook_still_matches_its_selector(self):
        st = authority_status.status(SELECTOR, OPERATIONAL)
        self.assertEqual(st["state"], "LOCAL_MATCHES_AUTHORITY")
        manifest, _ = authority.load_manifest(SELECTOR)
        self.assertEqual(authority.compare_manifest_to_codebook(manifest, OPERATIONAL), [])
        self.assertEqual(LEGACY.status()["state"], "LOCAL_MATCHES_AUTHORITY")

    @unittest.skipUnless(OPERATIONAL.exists(), "the legacy selftest reads the selected codebook")
    def test_the_legacy_selftest_still_passes_every_control(self):
        out = subprocess.run([sys.executable, str(EXPERIMENTS / "foundry_authority.py"), "selftest"],
                             capture_output=True, text=True, cwd=str(REPO_ROOT))
        self.assertEqual(out.returncode, 0, out.stdout[-2000:])
        names = [line.split("]", 1)[1].strip() for line in out.stdout.splitlines()
                 if line.startswith("  [PASS]")]
        self.assertFalse([line for line in out.stdout.splitlines() if line.startswith("  [FAIL]")])
        for control in ("NC9", "NC10", "NC12", "NC15", "NC17", "NC20", "NC21", "NC22", "NC24",
                        "NC25", "NC28", "NC29b", "NC31", "NC34", "CANARY"):
            self.assertTrue(any(n.startswith(control + " ") for n in names), control)


if __name__ == "__main__":
    unittest.main()
