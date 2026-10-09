refs.json sha256: 497d399005cefd631922aa62ce3298a98a0eb7b4863aae9000e2385502f67e7d

# M05 summary -- the C04 reference audit

Wave M05.ORACLE-COMPILER-REFERENCE-SEMANTIC-AUDIT, unit M05-SUMMARY, base e70c47d77d559ad816c833af2a26f9e73412a775 (M05-FIX landed on top as 158e2dd), issue 1 checkpoint 6078322895 task 6051725880. Revised in wave M05.ORACLE-COMPILER-REFERENCE-SEMANTIC-AUDIT.AR1 (issue 1 checkpoint 6078583171, reviewer verdict 6078576859) after the AR1 M05-FIX repair landed as c2037e4: the fixture document's blob is updated, and the candidate-label discrepancy that repair recorded is carried below. No count or verdict changed.

This summary re-judges no row. Every count and verdict below is what `m05_check.py --rule` aggregates from the accepted part documents, or what the fixture document's ledger gives. Every finding is quoted from the document that records it.

## Inputs checked

- `python3 experiments/oracle_ingest/c04_refs.py --verify`: every embedded hash current (19 files); refs.json was not regenerated. Its sha256 is the one above, and every read document cites the same one. The operator's read-only copy refs-497d3990.json has the same sha256.
- `m05_check.py --protocol` output sha256 66e13172e565b21189008995b936a1b5a931dff205ae2f794bca04eb57835873, the planned protocol.
- INTERFACES.md at HEAD is blob 282c295c03f2a4b43e723d01710baaf479aa716c. c04_refs.py, h_region.py, h_region_kill.py and m05_check.py are at the C04 accepted head's blobs (bfacfa9dfa868da8077eb444954157ea6ea5d9da, 2e1f9a7a320ac042df424b3d119f3c3922fdf2f0, cd3d8b1c85b3a32ef0200fe285dbd822ce8103eb, 6df718a07d8feeba94ff4409d9d44d5ff174b6d3).
- `m05_check.py --rule` exits 0 for each of the five rules: the part documents partition every rule's rows exactly.

## Read documents (git blob at HEAD)

| document | blob | rows | endpoint-no | kind-no | duplicate-no | cannot-judge |
|---|---|---|---|---|---|---|
| M05-E1-P1-READ.md | 577af0a27ae8276a7e2d1fa6a59aef82b5a88586 | 132 | 0 | 0 | 0 | 0 |
| M05-E1-P2-READ.md | 5d455885c22ee7abe231487b8e48dce7f89caac6 | 132 | 0 | 0 | 0 | 2 |
| M05-E1-P3-READ.md | d33bafac3430b20c5aa4fbcee36edf528f4dd023 | 132 | 0 | 0 | 0 | 0 |
| M05-E1-P4-READ.md | 37b37a8c0c8e94bb602619d314dc5f3c11d07b83 | 133 | 0 | 0 | 0 | 0 |
| M05-E2-P1-READ.md | f1b4b9a648aa1d7f19d83acc77f67bc60ab09af2 | 124 | 0 | 0 | 0 | 0 |
| M05-E2-P2-READ.md | b15f020d6809e3dae0cc78388a13d27eddf304c3 | 125 | 0 | 0 | 0 | 0 |
| M05-E2-P3-READ.md | 7d1a2d0ccfafcf52a3edb92f3179b84fc5b661d7 | 124 | 0 | 0 | 0 | 0 |
| M05-E2-P4-READ.md | 9e015d0d5d7fd3ff840bac7f2aca731bc62ca3cb | 125 | 0 | 3 | 0 | 0 |
| M05-E3-P1-READ.md | 8c51fb8b33c823b42cf157a3b8d96444b8ee1dfb | 98 | 0 | 0 | 0 | 0 |
| M05-E3-P2-READ.md | 0d1db23d517a7af20cd765d4eb8f28037ec20f55 | 98 | 0 | 0 | 0 | 0 |
| M05-E4-P1-READ.md | 625d1dce0027fc40751f32bb4f7cfb684f63477e | 112 | 0 | 0 | 0 | 0 |
| M05-E4-P2-READ.md | 7a47bd7095915bca47f59efb7905df63104797c3 | 112 | 0 | 0 | 0 | 0 |
| M05-E4-P3-READ.md | f596892a52e70af9a93322b38dd33a11fe50ebcd | 112 | 0 | 0 | 0 | 0 |
| M05-E4-P4-READ.md | 3f2dada5ea8c3bce6bf446adc98ac0028ce0b77e | 112 | 0 | 0 | 0 | 0 |
| M05-E4-P5-READ.md | 1fe86acd95c0c02ffe96fb5f36ffc14e59272429 | 113 | 0 | 0 | 0 | 0 |
| M05-E5-P1-READ.md | e7023be0ccb73a700b7e550341e4f0f215e0efd5 | 119 | 0 | 0 | 0 | 0 |
| M05-FIXTURES-READ.md | 284590d681e5c7241e49c31b77594e40eb3d6453 | 10 | 0 | 0 | 2 | 0 |

Every part document's own verdict is the PART VERDICT its ledger gives, and every one of the 17 documents states the same verdict word as the rule lines below. The read set is 1,903 rule rows (E1 529, E2 498, E3 196, E4 561, E5 119, the §I5.4 figures) plus 10 fixture rows, 3 of which are also E1 or E2 rows.

## Verdict

- E1: PASS (rows 529, endpoint-no 0, kind-no 0, duplicate-no 0, cannot-judge 2); no endpoint-no row, and 2 cannot-judge rows of 529 are within the 5 percent bound (2 x 20 = 40, not more than 529).
- E2: PASS (rows 498, endpoint-no 0, kind-no 3, duplicate-no 0, cannot-judge 0); no endpoint-no row; 3 kind-no rows are findings for the Captain, not a fail.
- E3: PASS (rows 196, endpoint-no 0, kind-no 0, duplicate-no 0, cannot-judge 0); every recorded copy endpoint was judged right.
- E4: PASS (rows 561, endpoint-no 0, kind-no 0, duplicate-no 0, cannot-judge 0); every recorded target-mark endpoint was judged right.
- E5: PASS (rows 119, endpoint-no 0, kind-no 0, duplicate-no 0, cannot-judge 0); every clause prints a printed comparison and records no endpoint.
- FIXTURES: PASS (rows 10, endpoint-no 0, kind-no 0, duplicate-no 2, cannot-judge 0); the 3 RESOLVED fixture endpoints are right and the 7 other outcomes claim nothing false; 2 duplicate-no rows are findings.

## Failing pattern classes

None. No rule and no fixture row has an endpoint-no cell, so no pattern class is withdrawn under §I5.8 ruling 4 and no false RESOLVED goes to the Captain.

## Findings: KIND-no rows

All three are in M05-E2-P4-READ.md, class E2:exiled. The reader judged each endpoint right and the kind wrong. A same-ability "exiled with ~" is labelled COREFERENT, but under CR 607.2a it names the accumulated set of cards exiled with the object over every resolution, so LINKED fits. On the second and third rows the printed threshold cannot be met by one resolution.

- 8c72d54e-97a6-408e-ae77-18d3c96b3bd8:0:1:1@63:exiled with ~
- a656ad7f-133f-4d93-919a-43bcf1f815f3:0:0:1@38:exiled with ~
- c0cbb347-b060-43ce-a9c5-8c835be3cf1b:0:0:1@53:exiled with ~

## Findings: DUPLICATE-no rows

Both are in M05-FIXTURES-READ.md, in clause 008d5896-6fc9-4aaa-8c6f-a44c2feb98bb:0:1:0. Under the protocol's printed test (same clause, spans [char_offset, char_offset + len(phrase)) intersect), the E6 conditionality span [57, 71) contains the E4 pronoun span [60, 62). Neither row is RESOLVED, so no endpoint is claimed twice.

- 008d5896-6fc9-4aaa-8c6f-a44c2feb98bb:0:1:0@57:intervening-if (class none, E6 OUT-OF-SCOPE)
- 008d5896-6fc9-4aaa-8c6f-a44c2feb98bb:0:1:0@60:it (class E4:it, UNRESOLVED continuity)

Context from M05-E4-P2-READ.md: eight E4:it rows of that part share their span with an E6 conditionality candidate (P4 label phrase "intervening-if"; see the label finding below). E6 rows are outside the rule read set, so there they were not duplicates. The fixture read set does hold an E6 row, which is why this pair alone is recorded.

## Cannot-judge reasons

Both are in M05-E1-P2-READ.md, class E1:exile, ENDPOINT cell cannot-judge, KIND and DUPLICATE yes.

- 0179bc62-823e-46b9-b536-342904fedafc:0:0:1@57:this way -- the reference means the effect exile. But the clause's one exile region is headed by the cost exile and also spans the effect, whose verb has no region of its own. The reader could not decide whether a region headed by another operation is the meant event (a region-granularity question).
- 8d4e0866-d8f5-4eb6-a0fd-3fa9d4b9cf4a:0:1:2@70:this way -- the endpoint is the unkicked exile instruction. The kicked "instead" exile has no region and replaces it under CR 614.6, so when kicked the counted cards come from an exile the endpoint does not name. The reader could not decide whether the replaced instruction is the event meant.

## Finding: candidate-label discrepancy (frozen data, not changed)

Recorded by the AR1 repair of M05-FIXTURES-READ.md (reviewer verdict 6078576859, finding 3). The E6 candidate 008d5896-6fc9-4aaa-8c6f-a44c2feb98bb:0:1:0@57:intervening-if carries the P4 label phrase "intervening-if", but under CR 603.4 its "if" is not an intervening "if": that rule applies only to an "if" immediately after a trigger condition, and this one follows the exile instruction. It is an ordinary condition on the exile, checked as the ability resolves (CR 608.2c). The label and row_id are frozen candidate data and stay as they are. No verdict cell depends on the label: E6 OUT-OF-SCOPE rests on the candidate being a delay-flagged conditionality marker (§I5.8 ruling 1), which it is. The same repair corrected the fixture document's citation for the "that card" return in the same paragraph: it is a delayed triggered ability under CR 603.7 and 603.7c, not a CR 610.3 "until" return.

## Other findings from the read documents (no ruling sought by their readers)

- Fixture conservative misses (M05-FIXTURES-READ.md): five UNRESOLVED fixture rows have a referent under the CR that the frozen rules leave unresolved. They are findings about reach, never false success (§I5.4): the two replacement-lineage "this way" rows of member eae87919-6322-4bd2-ae9c-b1ce25d686da, the "chosen kind" row of member eccc9a54-2b56-4a02-9926-258d5b2e25fb, and the "it" and "that card" rows of member 008d5896-6fc9-4aaa-8c6f-a44c2feb98bb.
- M05-E2-P2-READ.md and M05-E2-P3-READ.md each record one observation that the reader judged LINKED and right: a threshold paragraph on an instant or sorcery face, and a saga chapter linking to an earlier chapter's choice.

## Captain questions

These are carried from the read documents unchanged; this summary adds no ruling and changes no rule or row.

1. E1 region granularity (M05-E1-P2-READ.md, row 0179bc62-823e-46b9-b536-342904fedafc:0:0:1@57:this way). The meant operation lies inside a region whose head is another operation. Does such an E1 endpoint count as the right event, or should the row be read as endpoint-no? Either answer changes E1's counts. With endpoint-no, E1 and its class E1:exile would fail under ruling 4.
2. E1 replaced instruction (M05-E1-P2-READ.md, row 8d4e0866-d8f5-4eb6-a0fd-3fa9d4b9cf4a:0:1:2@70:this way). Is an endpoint naming only the instruction that a kicker "instead" replaces what the reference means, or a missed competing antecedent? The same consequence holds for E1:exile.
3. E2 same-ability "exiled with ~" kind label (M05-E2-P4-READ.md, the three KIND-no rows above). Should it carry LINKED rather than COREFERENT? §I5.8 ruling 5 currently says same-ability "the exiled card" is COREFERENT; this is a measurement-label question only.
4. Fixture duplicate test (M05-FIXTURES-READ.md, the two DUPLICATE-no rows above). Should an E6 conditionality marker, whose phrase is a label and which claims no reference, count against an E4 pronoun span under §I4 identity and §I5.1 overlap?
5. P4 conditionality label (M05-FIXTURES-READ.md, row 008d5896-6fc9-4aaa-8c6f-a44c2feb98bb:0:1:0@57:intervening-if). Its "if" follows the exile instruction, so CR 603.4 does not make it an intervening "if", yet P4 labels it so. Should P4 conditionality labelling distinguish an intervening "if" from an "if" inside the effect, and how many of the 723 delay-flagged E6 candidates carry the same mislabel? No verdict here depends on the answer.
