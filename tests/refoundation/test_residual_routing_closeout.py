"""Negative-controlled guard for the residual cold-start routing closeout."""
from __future__ import annotations

import hashlib
import subprocess
import unittest

from tests.refoundation.helpers import REPO_ROOT

SELECTOR = "latest `K` -> active `T`"

ARCHIVED = {
    "archive/routing/docs/T3-BUILDOUT-PLAYBOOK.md": "d4cffd89edddc15deb9a13c875365c4e019c492b",
    "archive/routing/docs/T3-AXIS-FOUNDRY-v3.md": "2b89ea43fa371945ee9f8b487758d4dddb2d60cc",
    "archive/routing/docs/WORK-PACKETS-2026-08-07.md": "e1bab565d6da493016d65fdef298eb4412f96e4a",
    "archive/routing/docs/AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md": "92e254b222c76f4570d0870b371bfd371093a4c0",
    "archive/routing/docs/B-MIGRATION-DIRECTIVE.md": "213206b6560d9f097ae86af1673b4630a1c1a64a",
    "archive/routing/docs/B-CONSOLIDATION-REAUDIT-PACKET.md": "3f57d5cd9909aed5e8d9de6a8fbfa9c096f0ab44",
    "archive/routing/experiments/foundry_build_reaudit_packet.py": "3a1fd7019c8c4d9f37054f5f1fc91e2b13bc41d0",
}

INERT = {
    "docs/T3-BUILDOUT-PLAYBOOK.md": "archive/routing/docs/T3-BUILDOUT-PLAYBOOK.md",
    "docs/T3-AXIS-FOUNDRY-v3.md": "archive/routing/docs/T3-AXIS-FOUNDRY-v3.md",
    "docs/WORK-PACKETS-2026-08-07.md": "archive/routing/docs/WORK-PACKETS-2026-08-07.md",
    "docs/B-MIGRATION-DIRECTIVE.md": "archive/routing/docs/B-MIGRATION-DIRECTIVE.md",
    "docs/B-CONSOLIDATION-REAUDIT-PACKET.md": "archive/routing/docs/B-CONSOLIDATION-REAUDIT-PACKET.md",
}


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def inert_problems(text: str, archive: str) -> list[str]:
    out = []
    if not text.startswith("# ARCHIVED — DO NOT FOLLOW"):
        out.append("missing inert heading")
    if SELECTOR not in text:
        out.append("missing durable selector")
    if archive not in text:
        out.append("missing archive pointer")
    return out


class TestResidualRoutingCloseout(unittest.TestCase):
    def test_archived_payloads_are_exact_original_git_blobs(self):
        for rel, expected in ARCHIVED.items():
            with self.subTest(path=rel):
                data = (REPO_ROOT / rel).read_bytes()
                self.assertEqual(git_blob_sha(data), expected)

    def test_live_historical_paths_are_inert(self):
        for rel, archive in INERT.items():
            with self.subTest(path=rel):
                self.assertEqual(inert_problems((REPO_ROOT / rel).read_text(encoding="utf-8"), archive), [])

    def test_aq4_is_frozen_not_current_routing(self):
        text = (REPO_ROOT / "docs/AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# AQ4 PAUSED — NOT CURRENT ROUTING"))
        self.assertIn(SELECTOR, text)
        self.assertIn("AQ4 is PAUSED", text)
        self.assertIn("archive/routing/docs/AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md", text)
        self.assertNotIn("CURRENT AQ4 ENTRY POINT", text)

    def test_ag_cli_01_has_one_canonical_live_statement(self):
        law = (REPO_ROOT / "docs/MEMBER-ADD-MUTATION-LAW.md").read_text(encoding="utf-8")
        self.assertIn("Member-add CLI (AG-CLI-01): validates schema/target status/UUID/evidence, backs up, MERGES an assertion (never overwrites), appends history, lints, writes atomically, prints final sha256, halts on DET-axis operations other than assertion-merge of non-DET classes.", law)
        self.assertNotIn("AG-CLI-01", (REPO_ROOT / "docs/B-MIGRATION-DIRECTIVE.md").read_text(encoding="utf-8"))

    def test_r8_3_has_one_canonical_live_statement(self):
        law = (REPO_ROOT / "docs/ACTIVATED-REGENERATE-SELF-DET-LAW.md").read_text(encoding="utf-8")
        self.assertIn("R8.3 — ratified that this axis is being AUTHORED properly via the DET path", law)
        self.assertNotIn("R8.3", (REPO_ROOT / "docs/B-CONSOLIDATION-REAUDIT-PACKET.md").read_text(encoding="utf-8"))

    def test_retired_reaudit_generator_fails_loudly(self):
        p = subprocess.run(
            ["python3", str(REPO_ROOT / "experiments/foundry_build_reaudit_packet.py")],
            cwd=REPO_ROOT, capture_output=True, text=True,
        )
        self.assertEqual(p.returncode, 2)
        self.assertIn("HALT: the B-consolidation re-audit packet generator is retired", p.stderr)

    def test_negative_control_reactivated_stub_is_red(self):
        text = (REPO_ROOT / "docs/T3-BUILDOUT-PLAYBOOK.md").read_text(encoding="utf-8")
        rigged = text.replace("# ARCHIVED — DO NOT FOLLOW", "# T3-BUILDOUT-PLAYBOOK — EXECUTE NEXT")
        self.assertTrue(inert_problems(rigged, "archive/routing/docs/T3-BUILDOUT-PLAYBOOK.md"))


if __name__ == "__main__":
    unittest.main()
