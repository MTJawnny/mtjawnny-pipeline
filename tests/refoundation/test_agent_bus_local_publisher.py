"""The local publisher writes with the operator's token (Captain decision A).

Issue #1 comment 5883466222: the local cross-review Manager posts as the
operator (a trusted speaker), but record recognition counted only the hosted
publisher identity, so it never saw its own disposition and re-posted it 166
times. These tests run the real publisher over the shared fake GitHub with every
write authored by the operator, and pin: a full transaction completes, reruns
write nothing, duplicates count once, a stranger's look-alike still counts for
nothing, and a speaker's publisher-form K is validated as a chain link, never
obeyed as written.
"""

from __future__ import annotations

import unittest
from unittest import mock

from tests.refoundation import test_agent_bus_publisher as T

from agent_bus import errors as E
from agent_bus import ledger as L
from agent_bus import publisher as P
from agent_bus import transition as X
from agent_bus.machine import RawComment

STRANGER = "someone-else"


def written(fake) -> dict:
    """What THIS test's writes were, by kind (the pre-existing world is excluded)."""
    out = {"WAVE_REVIEW": 0, "V": 0, "K": 0, "WAVE_COMMAND": 0}
    for number, body in fake.writes:
        if number != 1:
            out[T.parse_comment(body).kind] += 1
            continue
        record = L.parse_record(body)
        if record.schema == L.DISPOSITION:
            out["D"] = out.get("D", 0) + 1
        else:
            out["V" if record.schema == L.VERDICT else "K"] += 1
    return out


class Writer:
    """Author every fake-GitHub write as `login` for the duration."""

    def __init__(self, login: str) -> None:
        self.patch = mock.patch.object(T, "PUBLISHER", login)

    def __enter__(self):
        self.patch.start()

    def __exit__(self, *exc):
        self.patch.stop()


class TestLocalTransactionCompletes(unittest.TestCase):
    def test_a_local_transaction_completes_and_reruns_write_nothing(self):
        with Writer(T.AUTHOR):
            fake = T.FakeGitHub()
            self.assertEqual(T.publish(fake, T.REPAIR)["exit"], P.EXIT_COMPLETE)
            first = list(fake.writes)
            self.assertEqual(written(fake), {"WAVE_REVIEW": 1, "V": 1, "K": 1, "WAVE_COMMAND": 1})
            for _ in range(3):
                self.assertEqual(T.publish(fake, None)["exit"], P.EXIT_COMPLETE)
            self.assertEqual(fake.writes, first)            # a rerun writes nothing
            resolved = T.authority(fake)
            self.assertIsNotNone(resolved.authority.publisher)  # judged as a chain link
            self.assertEqual(len(resolved.chain), 2)

    def test_every_partial_state_resumes_without_duplicates(self):
        for after in (1, 2, 3, 4):
            with self.subTest(crash_after=after), Writer(T.AUTHOR):
                fake = T.FakeGitHub()
                fake.crash_after = after
                with self.assertRaises(T.Crash):
                    T.publish(fake, T.REPAIR)
                for _ in range(3):
                    self.assertEqual(T.publish(fake, None)["exit"], P.EXIT_COMPLETE)
                self.assertEqual(written(fake),
                                 {"WAVE_REVIEW": 1, "V": 1, "K": 1, "WAVE_COMMAND": 1})


class TestStrangersStillCountForNothing(unittest.TestCase):
    def test_NC_a_strangers_records_never_complete_a_transaction(self):
        # Rig: the writes come from an untrusted login. Nothing they write may be
        # recognized, so the transaction cannot complete and nothing chains.
        with Writer(STRANGER):
            fake = T.FakeGitHub()
            report = T.publish(fake, T.REPAIR)
            self.assertNotEqual(report["exit"], P.EXIT_COMPLETE)
            self.assertEqual(len(T.authority(fake).chain), 1)


class TestDuplicatesCountOnce(unittest.TestCase):
    def world(self, author: str, copies: int):
        body = "```yaml\nschema: mtj-disposition/0\nrecorded_by: agent-bus-publisher\n```\n"
        comments = [RawComment("issue:1", 9000 + i, author, body) for i in range(copies)]
        return body, mock.Mock(issue_comments=comments)

    def test_166_identical_speaker_dispositions_count_as_disposed(self):
        body, world = self.world(T.AUTHOR, 166)
        with mock.patch.object(P, "disposition_body", lambda w, item: body):
            self.assertTrue(P.disposed(world, T.TARGET, object()))

    def test_NC_a_strangers_identical_disposition_does_not_count(self):
        body, world = self.world(STRANGER, 3)
        with mock.patch.object(P, "disposition_body", lambda w, item: body):
            self.assertFalse(P.disposed(world, T.TARGET, object()))


class TestIdempotencyGuard(unittest.TestCase):
    def test_a_byte_identical_live_record_is_never_posted_again(self):
        with Writer(T.AUTHOR):
            fake = T.FakeGitHub()
            fake.add(1, "same body", T.AUTHOR)
            txn = P.Txn(T.TARGET, T.RESULT_COMMENT, "d" * 64, fake)
            with self.assertRaises(P.Stop) as caught:
                P._write(txn, 1, "same body", "V")
            self.assertEqual(caught.exception.code, E.TXN_CONFLICT)
            self.assertEqual(fake.writes, [])

    def test_NC_a_strangers_identical_body_does_not_block_a_write(self):
        with Writer(T.AUTHOR):
            fake = T.FakeGitHub()
            fake.add(1, "same body", STRANGER)
            txn = P.Txn(T.TARGET, T.RESULT_COMMENT, "d" * 64, fake)
            P._write(txn, 1, "same body", "V")
            self.assertEqual(len(fake.writes), 1)


class TestSpeakerCheckpointIsALinkNotLaw(unittest.TestCase):
    def test_NC_a_speakers_publisher_form_k_that_is_not_the_link_is_refused(self):
        with Writer(T.AUTHOR):
            fake = T.FakeGitHub()
            self.assertEqual(T.publish(fake, T.REPAIR)["exit"], P.EXIT_COMPLETE)
            k = [c for c in fake.issue if L.is_publisher_checkpoint(c["body"])][-1]
            fields = dict(L.parse_record(k["body"]).fields)
            fields["h"] = fields["accepted_head"] = "e" * 40      # a forged head
            forged = L.render_checkpoint(fields)
            self.assertTrue(L.is_publisher_checkpoint(forged))
            before = T.authority(fake).authority
            forged_id = fake.add(1, forged, T.AUTHOR)
            after = T.authority(fake)
            self.assertEqual(after.authority, before)               # not obeyed
            self.assertIn(forged_id, [cid for cid, _, _ in after.refused_candidates])

    def test_a_human_checkpoint_from_a_speaker_is_still_law(self):
        human = "```yaml\nschema: mtj-checkpoint/2\nh: " + "f" * 40 + "\na: 0\n```\n"
        self.assertFalse(L.is_publisher_checkpoint(human))

    def test_the_ledger_and_the_transition_agree_on_the_publisher_signature(self):
        self.assertEqual(L.PUBLISHER_RECORDED_BY, X.RECORDED_BY)


if __name__ == "__main__":
    unittest.main()
