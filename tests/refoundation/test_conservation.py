"""Conservation v0: deterministic, read-only, exact bytes."""

from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT  # noqa: F401  (sets sys.path)

from mtj_foundry.conservation import (MANIFEST_SCHEMA, digest_bytes, digest_file,
                                      digest_paths, manifest, manifest_digest,
                                      manifest_json)


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
        before = digest_file(self.root / "a" / "one.txt").sha256
        (self.root / "a" / "one.txt").write_bytes(b"onE\n")
        self.assertNotEqual(before, digest_file(self.root / "a" / "one.txt").sha256)

    def test_recorded_paths_are_relative_so_manifests_compare_across_machines(self):
        entry = digest_file(self.root / "a" / "one.txt", relative_to=self.root)
        self.assertEqual(entry.path, "a/one.txt")
        self.assertNotIn(str(self.root), entry.path)


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


class TestDigestBytes(unittest.TestCase):
    def test_empty_input_is_the_known_sha256_of_nothing(self):
        self.assertEqual(
            digest_bytes(b""),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")


if __name__ == "__main__":
    unittest.main()
