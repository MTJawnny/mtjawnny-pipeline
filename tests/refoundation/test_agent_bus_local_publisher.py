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

from tests.refoundation import test_agent_bus_goal as G
from tests.refoundation import test_agent_bus_publisher as T

from agent_bus import errors as E
from agent_bus import issue as I
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
            k = [c for c in fake.issue if I.is_publisher_checkpoint(c["body"])][-1]
            fields = dict(L.parse_record(k["body"]).fields)
            fields["h"] = fields["accepted_head"] = "e" * 40      # a forged head
            forged = L.render_checkpoint(fields)
            self.assertTrue(I.is_publisher_checkpoint(forged))
            before = T.authority(fake).authority
            forged_id = fake.add(1, forged, T.AUTHOR)
            after = T.authority(fake)
            self.assertEqual(after.authority, before)               # not obeyed
            self.assertIn(forged_id, [cid for cid, _, _ in after.refused_candidates])

    def test_a_human_checkpoint_from_a_speaker_is_still_law(self):
        human = "```yaml\nschema: mtj-checkpoint/2\nh: " + "f" * 40 + "\na: 0\n```\n"
        self.assertFalse(I.is_publisher_checkpoint(human))

    def test_the_ledger_and_the_transition_agree_on_the_publisher_signature(self):
        self.assertEqual(I.PUBLISHER_RECORDED_BY, X.RECORDED_BY)


class TestLocalAcceptWithSuccessor(unittest.TestCase):
    def test_a_local_accept_issues_the_successor_and_reruns_write_nothing(self):
        with Writer(T.AUTHOR):
            plan = G.two_wave_body()
            fake = G.world(plan=plan)
            report = G.accept(fake, plan=plan)
            self.assertEqual(report["exit"], P.EXIT_COMPLETE, report)
            self.assertEqual(written(fake), {"WAVE_REVIEW": 1, "V": 1, "K": 1, "WAVE_COMMAND": 1})
            first = list(fake.writes)
            for _ in range(3):
                self.assertEqual(T.publish(fake, None)["exit"], P.EXIT_COMPLETE)
            self.assertEqual(fake.writes, first)
            resolved = T.authority(fake)
            self.assertEqual(resolved.authority.successor.wave, G.NEXT_WAVE)


class TestLocalDispositionLoopEnds(unittest.TestCase):
    def test_a_displaced_message_is_disposed_once_however_often_the_pass_repeats(self):
        with Writer(T.AUTHOR):
            fake = T.two_results()
            self.assertEqual(T.publish(fake, T.ACCEPT)["exit"], P.EXIT_COMPLETE)
            self.assertEqual(written(fake).get("D"), 1)
            first = list(fake.writes)
            for _ in range(5):                       # the 166-post loop, run five times
                report = T.publish(fake, None, comment_id=T.RESULT_COMMENT + 1)
                self.assertEqual(report["exit"], P.EXIT_COMPLETE, report)
            self.assertEqual(fake.writes, first)


class TestEachRecordFromAStrangerCountsForNothing(unittest.TestCase):
    """Rig: flip ONE record's author to a stranger; the publisher must not count it."""

    def completed(self):
        fake = T.two_results()
        self.assertEqual(T.publish(fake, T.ACCEPT)["exit"], P.EXIT_COMPLETE)
        return fake

    def flip(self, fake, schema):
        for c in fake.issue:
            record = L.parse_record(c["body"]) if c["body"].startswith("```yaml") else None
            if record is not None and record.schema == schema and c["user"]["login"] == T.AUTHOR \
                    and "agent-bus-publisher" in c["body"]:
                c["user"]["login"] = STRANGER
                return c["id"]
        self.fail(f"no {schema} to flip")

    def test_NC_a_strangers_verdict_does_not_count(self):
        with Writer(T.AUTHOR):
            fake = self.completed()
            self.flip(fake, L.VERDICT)
            world = P.observe(T.TARGET, fake)
            tid = X.txn_id(T.K0, T.RESULT_COMMENT)
            self.assertEqual(P.find_records(world, T.TARGET, tid, T.RESULT_ID).verdicts, [])

    def test_NC_a_strangers_checkpoint_selects_nothing(self):
        with Writer(T.AUTHOR):
            fake = self.completed()
            k = self.flip(fake, L.CHECKPOINT)
            resolved = T.authority(fake)
            self.assertNotIn(k, resolved.chain)
            self.assertIn((k, STRANGER), resolved.untrusted_candidates)

    def test_NC_a_strangers_disposition_is_not_a_disposition(self):
        with Writer(T.AUTHOR):
            fake = self.completed()
            self.flip(fake, L.DISPOSITION)
            before = written(fake).get("D")
            report = T.publish(fake, None, comment_id=T.RESULT_COMMENT + 1)
            self.assertEqual(report["exit"], P.EXIT_COMPLETE, report)
            self.assertEqual(written(fake).get("D"), before + 1)   # written again, once


class TestSameMachineLock(unittest.TestCase):
    def test_a_second_publisher_on_this_machine_stops_and_one_k_links(self):
        with Writer(T.AUTHOR):
            fake = T.FakeGitHub()
            seen = []
            fake.before_write[3] = lambda f: seen.append(T.publish(f, None))
            self.assertEqual(T.publish(fake, T.ACCEPT)["exit"], P.EXIT_COMPLETE)
            self.assertEqual((seen[0]["exit"], seen[0]["code"]), (P.EXIT_REFUSED, E.TXN_RACE_LOST))
            self.assertEqual(written(fake)["K"], 1)
            self.assertEqual(len([c for c in T.authority(fake).chain if c != T.K0]), 1)


if __name__ == "__main__":
    unittest.main()
