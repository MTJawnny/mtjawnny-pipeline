"""Conservation v0: deterministic, read-only, exact bytes."""

from __future__ import annotations

import hashlib
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT  # noqa: F401  (sets sys.path)

from mtj_foundry.conservation import (MANIFEST_SCHEMA, FileDigest, PathDomainError,
                                      canonical_relpath, digest_bytes, digest_file,
                                      digest_paths, manifest, manifest_digest,
                                      manifest_json, posix_label)


class ConservationTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "a").mkdir()
        (self.root / "a" / "one.txt").write_bytes(b"one\n")
        (self.root / "two.bin").write_bytes(bytes(range(256)))


class TestExactBytes(ConservationTestCase):
    def test_the_digest_is_sha256_of_the_exact_file_bytes(self):
        entry = digest_file(self.root / "two.bin", relative_to=self.root)
        self.assertEqual(entry.sha256, hashlib.sha256(bytes(range(256))).hexdigest())
        self.assertEqual(entry.size_bytes, 256)
        self.assertEqual(entry.path, "two.bin")

    def test_size_is_recorded_alongside_the_hash(self):
        """C7.1 asks for sha256 AND byte size; a hash alone is not the identity."""
        entry = digest_file(self.root / "a" / "one.txt", relative_to=self.root)
        self.assertEqual(entry.size_bytes, 4)
        self.assertIn("size_bytes", entry.as_dict())

    def test_one_flipped_byte_changes_the_digest(self):
        """Negative control: the digest must actually be sensitive to content."""
        target = self.root / "a" / "one.txt"
        before = digest_file(target, relative_to=self.root).sha256
        target.write_bytes(b"onE\n")
        self.assertNotEqual(before, digest_file(target, relative_to=self.root).sha256)

    def test_recorded_paths_are_relative_so_manifests_compare_across_machines(self):
        entry = digest_file(self.root / "a" / "one.txt", relative_to=self.root)
        self.assertEqual(entry.path, "a/one.txt")
        self.assertNotIn(str(self.root), entry.path)


class TestTheDomainIsStructural(ConservationTestCase):
    """F3: no PUBLIC construction path can produce a non-canonical manifest label.

    The domain used to be a property of `digest_paths` alone, so three exported
    routes went around it: `digest_file` with no `relative_to` (absolute label), a
    direct `FileDigest(...)`, and entries handed straight to `manifest()`. A rule
    only one function enforces is a rule only that function's callers obey.
    """

    def test_a_file_digest_cannot_hold_an_absolute_label(self):
        with self.assertRaises(PathDomainError):
            FileDigest("/etc/passwd", "0" * 64, 1)

    def test_a_file_digest_cannot_hold_a_noncanonical_label(self):
        for bad in ("../x", "./a", "a//b", "a/../b", "a/b/", ""):
            with self.subTest(bad=bad), self.assertRaises(PathDomainError):
                FileDigest(bad, "0" * 64, 1)

    def test_a_canonical_file_digest_is_still_constructible(self):
        """Negative control: the guard is aimed at the domain, not at construction."""
        self.assertEqual(FileDigest("a/one.txt", "0" * 64, 4).path, "a/one.txt")

    def test_dataclasses_replace_cannot_smuggle_a_bad_label(self):
        import dataclasses

        good = FileDigest("a/one.txt", "0" * 64, 4)
        with self.assertRaises(PathDomainError):
            dataclasses.replace(good, path="/abs/x")

    def test_digest_file_requires_a_base_so_no_absolute_label_is_reachable(self):
        with self.assertRaises(TypeError):
            digest_file(self.root / "a" / "one.txt")  # type: ignore[call-arg]

    def test_posix_label_requires_a_base(self):
        from pathlib import PureWindowsPath

        with self.assertRaises(TypeError):
            posix_label(PureWindowsPath(r"C:\a\b"))  # type: ignore[call-arg]

    def test_manifest_refuses_duplicate_entries_it_did_not_build(self):
        """Entries can reach manifest() without passing through digest_paths."""
        entries = [FileDigest("a/one.txt", "0" * 64, 1),
                   FileDigest("a/one.txt", "1" * 64, 2)]
        for fn in (manifest, manifest_json, manifest_digest):
            with self.subTest(fn=fn.__name__), self.assertRaises(PathDomainError):
                fn(entries)

    def test_manifest_still_accepts_a_distinct_set(self):
        entries = [FileDigest("a/one.txt", "0" * 64, 1), FileDigest("two.bin", "1" * 64, 2)]
        self.assertEqual(manifest(entries)["entry_count"], 2)


class TestDeterminism(ConservationTestCase):
    """Acceptance criterion: "conservation digest output stable across repeated runs"."""

    def test_repeated_runs_produce_byte_identical_manifests(self):
        rels = ["a/one.txt", "two.bin"]
        first = manifest_json(digest_paths(self.root, rels))
        for _ in range(4):
            self.assertEqual(manifest_json(digest_paths(self.root, rels)), first)

    def test_input_order_does_not_change_the_digest(self):
        forward = manifest_digest(digest_paths(self.root, ["a/one.txt", "two.bin"]))
        reverse = manifest_digest(digest_paths(self.root, ["two.bin", "a/one.txt"]))
        self.assertEqual(forward, reverse)

    def test_the_manifest_embeds_no_clock(self):
        """A manifest carrying `generated_at` can never be compared to a later run."""
        text = manifest_json(digest_paths(self.root, ["a/one.txt"]))
        for stamp in ("generated_at", "timestamp", "created", "20"):
            if stamp == "20":
                continue
            self.assertNotIn(stamp, text)
        self.assertEqual(manifest(digest_paths(self.root, ["a/one.txt"]))["schema"],
                         MANIFEST_SCHEMA)

    def test_a_changed_file_changes_the_manifest_digest(self):
        """Negative control for the stability assertions above."""
        rels = ["a/one.txt", "two.bin"]
        before = manifest_digest(digest_paths(self.root, rels))
        (self.root / "two.bin").write_bytes(b"different")
        self.assertNotEqual(before, manifest_digest(digest_paths(self.root, rels)))

    def test_totals_are_reported(self):
        m = manifest(digest_paths(self.root, ["a/one.txt", "two.bin"]))
        self.assertEqual(m["entry_count"], 2)
        self.assertEqual(m["total_bytes"], 260)


class TestReadOnly(ConservationTestCase):
    def test_digesting_creates_moves_and_deletes_nothing(self):
        before = sorted(p.relative_to(self.root).as_posix()
                        for p in self.root.rglob("*"))
        stats = {p: p.stat().st_mtime_ns for p in self.root.rglob("*") if p.is_file()}
        digest_paths(self.root, ["a/one.txt", "two.bin"])
        after = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*"))
        self.assertEqual(before, after)
        for path, mtime in stats.items():
            self.assertEqual(path.stat().st_mtime_ns, mtime, f"{path} was written")

    def test_a_missing_declared_path_halts_rather_than_being_skipped(self):
        """Silently dropping an absent file would report conservation of a smaller set."""
        with self.assertRaises(FileNotFoundError):
            digest_paths(self.root, ["a/one.txt", "not-there.txt"])


class TestCanonicalPathDomain(ConservationTestCase):
    """R3: declarations are canonical repository-relative POSIX paths, or they are refused.

    The module claimed cross-machine comparability while emitting platform-native
    labels and accepting anything that happened to join. The domain now backs the
    claim, and it REFUSES rather than repairs: silently normalising a declaration
    would make the manifest disagree with what the caller declared, and the caller is
    the one making the conservation claim.
    """

    def test_a_canonical_path_passes_through_unchanged(self):
        self.assertEqual(canonical_relpath("a/one.txt"), "a/one.txt")

    def test_a_canonical_declaration_round_trips_to_itself(self):
        """F2: this is a VALIDATOR, not a normalizer. Canonical in, identical out."""
        for good in ("a/one.txt", "two.bin", "docs/x/y.md", "a/b/c/d.json"):
            with self.subTest(good=good):
                self.assertEqual(canonical_relpath(good), good)

    def test_noncanonical_input_is_refused_not_repaired(self):
        """The earlier version rewrote './a//b' to 'a/b' while its contract said refuse.

        A gate that quietly edits its input is not a gate: the manifest would then
        record something the caller never declared, and the caller is the one making
        the conservation claim.
        """
        for bad in ("./a/b", "a/./b", "a//b", "./a//b"):
            with self.subTest(bad=bad), self.assertRaises(PathDomainError):
                canonical_relpath(bad)

    def test_leading_and_trailing_separators_are_refused(self):
        for bad in ("a/b/", "/a/b", "a/"):
            with self.subTest(bad=bad), self.assertRaises(PathDomainError):
                canonical_relpath(bad)

    def test_absolute_declarations_are_refused(self):
        for bad in ("/etc/passwd", "/", "//srv/x"):
            with self.subTest(bad=bad), self.assertRaises(PathDomainError):
                canonical_relpath(bad)

    def test_parent_traversal_is_refused_even_when_it_does_not_escape(self):
        """`a/../b` resolves inside the root, and is still refused.

        Accepting it would mean the admission gate has to reason about where a
        declaration lands, which is exactly the judgement a lexical domain avoids.
        """
        for bad in ("../escape", "a/../b", "a/../../x", "a/./../../y"):
            with self.subTest(bad=bad), self.assertRaises(PathDomainError):
                canonical_relpath(bad)

    def test_empty_and_root_declarations_are_refused(self):
        for bad in ("", "   ", ".", "./", "./."):
            with self.subTest(bad=bad), self.assertRaises(PathDomainError):
                canonical_relpath(bad)

    def test_drive_relative_declarations_are_refused(self):
        """F5: a drive component is not absoluteness, and the invariant is the drive.

        `ntpath.isabs("C:foo")` is False — it means "foo, relative to the current
        directory ON DRIVE C" — so an absoluteness test alone admitted `C:foo`, `C:`
        and `Z:dir/file` as though they were ordinary relative paths.
        """
        for bad in ("C:foo", "C:", "Z:dir/file", "C:/abs", "c:x/y"):
            with self.subTest(bad=bad), self.assertRaises(PathDomainError):
                canonical_relpath(bad)

    def test_the_drive_check_is_on_the_drive_not_on_absoluteness(self):
        """The witness that makes the previous test non-vacuous."""
        import ntpath

        self.assertFalse(ntpath.isabs("C:foo"))
        self.assertEqual(ntpath.splitdrive("C:foo")[0], "C:")

    def test_ordinary_posix_labels_are_unaffected_by_the_drive_check(self):
        """Negative control: the guard is aimed at drives, not at colons or letters."""
        for good in ("a/one.txt", "docs/x/y.md", "C/foo", "a/b:c.txt", "Z/dir/file"):
            with self.subTest(good=good):
                self.assertEqual(canonical_relpath(good), good)

    def test_backslash_declarations_are_refused_as_ambiguous(self):
        with self.assertRaises(PathDomainError):
            canonical_relpath("a\\one.txt")

    def test_digest_paths_refuses_an_out_of_domain_declaration(self):
        for bad in ("/etc/passwd", "../outside", ""):
            with self.subTest(bad=bad), self.assertRaises(PathDomainError):
                digest_paths(self.root, ["a/one.txt", bad])

    def test_duplicate_canonical_declarations_are_refused(self):
        """A repeated path would be digested twice and double-count itself."""
        for dupe in (["a/one.txt", "a/one.txt"], ["a/one.txt", "./a/one.txt"],
                     ["a/one.txt", "a//one.txt"]):
            with self.subTest(dupe=dupe), self.assertRaises(PathDomainError):
                digest_paths(self.root, dupe)

    def test_the_domain_is_checked_before_any_file_is_opened(self):
        """A malformed set must fail whole, not half-measured."""
        opened = []
        real_open = open

        def watched(path, *a, **kw):
            opened.append(str(path))
            return real_open(path, *a, **kw)

        import builtins
        with unittest.mock.patch.object(builtins, "open", watched):
            with self.assertRaises(PathDomainError):
                digest_paths(self.root, ["a/one.txt", "two.bin", "/etc/hosts"])
        self.assertEqual(opened, [], "files were read before the set was validated")

    def test_emitted_labels_use_posix_separators(self):
        entries = digest_paths(self.root, ["a/one.txt"])
        self.assertEqual(entries[0].path, "a/one.txt")
        self.assertNotIn("\\", manifest_json(entries))

    def test_the_label_is_posix_even_for_a_windows_style_path(self):
        """Falsifiable on THIS platform, which the assertion above is not.

        On POSIX `str(p)` and `p.as_posix()` are the same string, so a regression to
        platform-native labels passes every test that only runs here. A pure Windows
        path exercises the difference without needing Windows.
        """
        from pathlib import PureWindowsPath

        target = PureWindowsPath(r"C:\repo\a\one.txt")
        base = PureWindowsPath(r"C:\repo")
        self.assertEqual(posix_label(target, base), "a/one.txt")
        # The control: the rejected implementation on the same input.
        self.assertEqual(str(target.relative_to(base)), "a\\one.txt")

    def test_the_domain_did_not_change_exact_byte_or_determinism_semantics(self):
        """Negative control on the repair itself: the core behaviour is untouched."""
        import hashlib

        rels = ["a/one.txt", "two.bin"]
        first = manifest_json(digest_paths(self.root, rels))
        self.assertEqual(manifest_json(digest_paths(self.root, rels)), first)
        entry = digest_paths(self.root, ["two.bin"])[0]
        self.assertEqual(entry.sha256, hashlib.sha256(bytes(range(256))).hexdigest())
        self.assertEqual(entry.size_bytes, 256)


class TestValidateBeforeRead(ConservationTestCase):
    """F6: an out-of-domain target must cost ZERO file reads.

    The label used to be computed after the read, so a target outside `relative_to`
    was opened and hashed in full before anything rejected it. The domain check ran
    — just after the work it exists to prevent had already happened.
    """

    def _reads(self, fn):
        """Run fn, returning the paths opened. Patches builtins.open, which is the
        call `digest_file` actually makes."""
        import builtins

        opened: list[str] = []
        real_open = builtins.open

        def watched(path, *a, **kw):
            opened.append(str(path))
            return real_open(path, *a, **kw)

        with unittest.mock.patch.object(builtins, "open", watched):
            try:
                fn()
            except PathDomainError:
                pass
        return opened

    def test_a_target_outside_the_base_is_never_opened(self):
        outside = self.root / "two.bin"
        base = self.root / "a"
        self.assertTrue(outside.exists(), "the target must exist, or the test is vacuous")
        self.assertEqual(self._reads(lambda: digest_file(outside, relative_to=base)), [])

    def test_the_rejection_is_a_path_domain_error(self):
        with self.assertRaises(PathDomainError):
            digest_file(self.root / "two.bin", relative_to=self.root / "a")

    def test_a_valid_target_is_still_read_exactly_once(self):
        """Negative control: the reordering must not stop the read happening at all."""
        reads = self._reads(
            lambda: digest_file(self.root / "a" / "one.txt", relative_to=self.root))
        self.assertEqual(len(reads), 1)

    def test_exact_byte_semantics_are_unchanged_by_the_reordering(self):
        import hashlib

        entry = digest_file(self.root / "two.bin", relative_to=self.root)
        self.assertEqual(entry.sha256, hashlib.sha256(bytes(range(256))).hexdigest())
        self.assertEqual(entry.size_bytes, 256)
        self.assertEqual(entry.path, "two.bin")

    def test_the_public_signature_is_unchanged_from_r2(self):
        import inspect

        sig = inspect.signature(digest_file)
        self.assertEqual(list(sig.parameters), ["path", "relative_to"])
        self.assertIs(sig.parameters["relative_to"].default, inspect.Parameter.empty)
        self.assertEqual(sig.parameters["relative_to"].kind,
                         inspect.Parameter.KEYWORD_ONLY)


class TestDigestBytes(unittest.TestCase):
    def test_empty_input_is_the_known_sha256_of_nothing(self):
        self.assertEqual(
            digest_bytes(b""),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")


if __name__ == "__main__":
    unittest.main()
