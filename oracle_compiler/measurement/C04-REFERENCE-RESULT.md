# C04 — reference resolution result under interface/5

Wave `C04.ORACLE-COMPILER-REFERENCE-RESOLUTION`, Issue #1 checkpoint
6050349736, task 6031697537 (`c04-oracle-compiler-reference-resolution-command-r4`).
Accepted head (base) `b64320272e45bec9fcd1f78f6a12cd14a74f77f3`; candidate
base `0390385` (the interface/5 landing, record 6031691630). This wave's units
landed as `f9a9333` (C04-REPIN), `21168cc` (C04-RESOLVE) and `cfccefa`
(C04-TESTS). Interface: `oracle-compiler-interface/5`,
`oracle_compiler/INTERFACES.md` blob `282c295c03f2a4b43e723d01710baaf479aa716c`
(ratified 6031676826 under standing approval 5918781674), checked at the
checked-out HEAD with `git rev-parse HEAD:oracle_compiler/INTERFACES.md`.

This is a measurement: evidence, not authority. It ratifies nothing, makes
nothing production truth, and **claims no row is correct**: correctness is
M05's read (§I5.4). An UNRESOLVED reference is valid output (V1 M2). Every
figure below is read from `refs.json` only. Rows are named only by refs.json's
`row_id` (`<oracle_id>:<face>:<paragraph>:<clause>@<char_offset>:<phrase>`); no
card is named, and card text stays in the ignored `refs.json`.

## Artifact

Hand-off rule followed: `refs.json` existed, so it was not trusted;
`python3 experiments/oracle_ingest/c04_refs.py --verify` was run first and
reported every embedded hash current (19 files). It is ignored experimental
output, portable (repo-relative paths and content hashes only) and
byte-identical on regeneration (`--check-determinism`).

| artifact | sha256 |
|---|---|
| `experiments/out/oracle_ingest/c04/refs.json` | `497d399005cefd631922aa62ce3298a98a0eb7b4863aae9000e2385502f67e7d` |
| `experiments/oracle_ingest/c04_refs.py` (embedded) | `5c151bcc10f3d7b4718048546262c9bf9a8a63dbf5d88d328928173edd60e4af` |

refs.json sha256: 497d399005cefd631922aa62ce3298a98a0eb7b4863aae9000e2385502f67e7d

The I1 identities it embeds (frozen probe, corpus bulk file, CR, accepted C02
output) equal §I1's pins. The CR reads (400.7, 607.2a, 607.2b, 607.2d, 608.2c,
707.10) each printed their operative phrase. The rule table was checked not
card-keyed over every corpus card name. All 39 negative controls embedded in
the build fired.

## §I4 reconciliation

Every §I4 figure equals both the interface literal and the accepted C02 P4
output; the build halts otherwise.

| figure | measured | §I4 |
|---|---|---|
| cards in corpus | 32,557 | 32,557 |
| cards with candidates | 16,245 | 16,245 |
| candidates | 32,603 | 32,603 |
| coreference | 21,672 | 21,672 |
| conditionality | 8,642 | 8,642 |
| cr607-linkage | 741 | 741 |
| kind-unclear | 1,548 | 1,548 |
| delay-marked | 3,774 | 3,774 |
| cross-line | 12,400 | 12,400 |
| excluded inside created abilities | 607 | 607 |

§I5.1 address: every non-empty corpus chain paragraph (61,383) ties to its P4
line; 7,475 of them carry a pressure-set candidate.

Pressure set: 5,856 candidates (kind-unclear 1,548, cr607-linkage 741,
delay-marked 3,774). Pairwise overlaps, each candidate counted once:
kind-unclear and delay-marked 138; cr607-linkage and delay-marked 69;
kind-unclear and cr607-linkage 0.

## Reach (§I5.5)

`python3 experiments/oracle_ingest/c04_refs.py --check-reach` exits 0:
"every §I5.5 and §I5.7 figure equal (5856 candidates)". No figure differs, so
there is no Captain finding from the reach check.

| rule | candidates | RESOLVED | UNRESOLVED | NOT-COREFERENCE | OUT-OF-SCOPE |
|---|---|---|---|---|---|
| E1 event-this-way | 1,088 | 529 | 559 | 0 | 0 |
| E2 cr607-linked | 676 | 498 | 178 | 0 | 0 |
| E3 copy-product | 208 | 196 | 12 | 0 | 0 |
| E4 singular-back-reference | 2,844 | 561 | 2,283 | 0 | 0 |
| E5 comparison | 225 | 0 | 106 | 119 | 0 |
| E6 conditionality (flagged) | 723 | 0 | 0 | 0 | 723 |
| residue / overlap | 92 | 0 | 92 | 0 | 0 |
| **total** | **5,856** | **1,784** | **3,230** | **119** | **723** |

| rule | reason | candidates |
|---|---|---|
| E4 | no-candidate | 1,174 |
| E4 | no-rule | 488 |
| E1 | detector-reach | 335 |
| E4 | plural-r3 | 302 |
| E1 | no-candidate | 211 |
| E4 | competing-antecedent | 179 |
| E2 | no-candidate | 135 |
| E4 | continuity | 120 |
| E5 | no-rule | 106 |
| residue | overlap | 65 |
| E2 | other-chooser | 31 |
| residue | no-rule | 27 |
| E4 | ambiguous | 14 |
| E1 | ambiguous | 13 |
| E3 | no-candidate | 12 |
| E2 | ambiguous | 10 |
| E4 | expletive | 6 |
| E2 | no-rule | 2 |

UNRESOLVED rows are findings by reason, never read for false success
(§I5.4). Of the 302 plural-r3 rows, R3's precondition (exactly one earlier
region holding one coordinated P3 list, `h_region_kill.py`'s R3 code) names a
list for 0; none is resolved either way (§I5.8 note).

### E2 endpoint kinds

E2 RESOLVED 498 = LINKED 322 + COREFERENT 176 (§I5.8 ruling 5: same-ability
"the exiled card" is COREFERENT, not CR 607 LINKED; measurement labels only).

### Delayed-trigger subset (§I5.8 ruling 14)

E4 candidates whose reference clause prints "at the beginning of the next":
450.

| outcome / reason | candidates |
|---|---|
| RESOLVED | 25 |
| no-candidate | 186 |
| no-rule | 108 |
| plural-r3 | 55 |
| continuity | 48 |
| competing-antecedent | 26 |
| ambiguous | 2 |

**Finding (UNRESOLVED):** the CR 603.7 link from a delayed trigger to the
ability that created it is not resolved by any rule; it stays UNRESOLVED
(no-rule). The 25 RESOLVED rows resolve the singular back-reference to a
target mark, not the trigger-to-creator link. The subset's row_ids are in
refs.json (`delayed_trigger_subset.rows`).

### Replacement lineage (§I5.8 ruling 6)

A01 R2-A has reported (`oracle_compiler/analysis/A01-R2A-REPLACEMENT-LINEAGE.md`,
read at run time): A1, A3 and A4 GENUINELY_MISSING. C04 therefore resolves no
candidate to a replacement-lineage endpoint and cites that verdict; there is
no lineage rule to take.

## Coverage and discovery (§I5.7, a report only)

Resolves nothing, claims nothing, and is not read by M05. Counts only; the
first three uncovered occurrences per form (by card name) stay in refs.json.

| kind | P4 candidates | in set | out of set |
|---|---|---|---|
| coreference | 21,672 | 2,844 | 18,828 |
| conditionality | 8,642 | 723 | 7,919 |
| cr607-linkage | 741 | 741 | 0 |
| kind-unclear | 1,548 | 1,548 | 0 |

Out-of-set coreference by P4 phrase (18,828; no §I5.3 rule applied):

| phrase | count | phrase | count |
|---|---|---|---|
| it | 7,803 | that planeswalker | 26 |
| its | 2,984 | that player | 1,320 |
| that artifact | 31 | that spell | 351 |
| that card | 905 | that token | 25 |
| that creature | 878 | their | 1,874 |
| that enchantment | 5 | them | 1,041 |
| that land | 75 | they | 836 |
| that permanent | 142 | those cards | 302 |
| those creatures | 149 | those permanents | 26 |
| those tokens | 55 | | |

Discovery: 1,670 uncovered and 2 covered occurrences of the 28 declared
forms. The list is declared and over-counts; its counts are a finding about
P4's reach, never a defect count (Captain question 16).

| form | covered | uncovered | form | covered | uncovered |
|---|---|---|---|---|---|
| the rest | 0 | 561 | the card | 0 | 50 |
| that much | 0 | 236 | the cards | 0 | 67 |
| the other | 0 | 105 | the token | 0 | 32 |
| the sacrificed | 0 | 133 | the tokens | 0 | 8 |
| the discarded | 0 | 26 | the spell | 0 | 23 |
| the revealed | 0 | 49 | the creature | 0 | 123 |
| the milled | 0 | 20 | the creatures | 0 | 11 |
| the destroyed | 0 | 0 | the permanent | 0 | 13 |
| the returned | 2 | 0 | the permanents | 0 | 7 |
| the countered | 0 | 0 | he | 0 | 60 |
| the targeted | 0 | 2 | him | 0 | 57 |
| the enchanted | 0 | 4 | his | 0 | 26 |
| the blocking | 0 | 3 | she | 0 | 12 |
| the attacking | 0 | 7 | her | 0 | 35 |

Card test (§I5.7 table, rows in its printed order; measured, never claimed
correct):

| §I5.7 row | printed C04 outcome | measured |
|---|---|---|
| 1 | in set, RESOLVED (OBJECT) | 2 in-set candidates, both RESOLVED OBJECT: `9d08af23-9f4a-4097-9abc-3b17475ab744:0:0:1@6:that creature`, `9d08af23-9f4a-4097-9abc-3b17475ab744:0:0:2@0:it` |
| 2 | in set, RESOLVED (LINKED) | 1 in-set candidate, RESOLVED LINKED: `bd9b9772-f5f9-4c6b-913e-7193bea5d0a7:0:1:0@53:the exiled card` |
| 3 | out of set (possessive) | 1 coreference candidate, out of set |
| 4 | out of set (the card itself) | 2 coreference candidates, out of set |
| 5 | out of set (found card) | 1 coreference candidate, out of set |
| 6 | uncovered | no P4 candidate; 1 discovery occurrence ("the sacrificed"), uncovered |
| 7 | uncovered | no P4 candidate; 1 discovery occurrence ("him"), uncovered |

Every row measures as §I5.7 prints it.

## M05 read set (§I5.4)

Every RESOLVED row (E5: every NOT-COREFERENCE row) is read; 1,903 in all.
Parts follow the M05 protocol: a rule's rows sorted by (class, row_id), part k
holding rows [floor((k-1)n/P), floor(kn/P)). Rows are in refs.json; counts
only here.

| rule | rows | P | part sizes |
|---|---|---|---|
| E1 | 529 | 4 | 132, 132, 132, 133 |
| E2 | 498 | 4 | 124, 125, 124, 125 |
| E3 | 196 | 2 | 98, 98 |
| E4 | 561 | 5 | 112, 112, 112, 112, 113 |
| E5 | 119 | 1 | 119 |

Pattern classes (§I5.4, refs.json `class`), with each part's classes:

| rule | classes (rows) | parts |
|---|---|---|
| E1 | cast 47, counter 32, create 1, destroy 49, discard 41, draw 6, exchange 1, exile 111, goad 2, investigate 1, mill 31, play 3, return 12, reveal 98, sacrifice 22, search 71, shuffle 1 | P1 cast..discard (3); P2 discard (38)..exile (87); P3 exile (24)..reveal (59); P4 reveal (39)..shuffle |
| E2 | chosen 315, exiled 183 | P1 chosen 124; P2 chosen 125; P3 chosen 66 + exiled 58; P4 exiled 125 |
| E3 | E3 196 | P1 98; P2 98 |
| E4 | it 361, that artifact 2, that creature 194, that permanent 4 | P1-P3 it 112 each; P4 it 25 + that artifact 2 + that creature 85; P5 that creature 109 + that permanent 4 |
| E5 | E5 119 | P1 119 |

### Fixture read set

Every candidate of a FIXTURES.json member in the five §I5.4 roles, whatever
its outcome: **10 candidates of 4 members**, equal to the operator's
re-measurement (2026-10-07 UTC) and to the C04 r2 Worker's (evidence
6011004249). Plan v8a's 4 was a miscount; it equals the
delayed-return-same-object member's candidates. No member holds two roles.

| role | members (with candidates) | candidates |
|---|---|---|
| delayed-return-same-object | 1 (1) | 4 |
| prior-set-complement-reference | 1 (0) | 0 |
| replacement-event-lineage | 3 (2) | 4 |
| ability-borrowing-inheritance-pressure | 1 (1) | 2 |
| two-sequential-operations | 1 (0) | 0 |

| row_id | role | rule | outcome / reason | class | endpoint kind |
|---|---|---|---|---|---|
| `008d5896-6fc9-4aaa-8c6f-a44c2feb98bb:0:1:0@57:intervening-if` | delayed-return-same-object | E6 | OUT-OF-SCOPE | none | none |
| `008d5896-6fc9-4aaa-8c6f-a44c2feb98bb:0:1:0@60:it` | delayed-return-same-object | E4 | UNRESOLVED continuity | E4:it | none |
| `008d5896-6fc9-4aaa-8c6f-a44c2feb98bb:0:1:1@7:that card` | delayed-return-same-object | E4 | UNRESOLVED no-candidate | E4:that card | none |
| `008d5896-6fc9-4aaa-8c6f-a44c2feb98bb:0:1:1@42:its` | delayed-return-same-object | E4 | UNRESOLVED no-rule | E4:its | none |
| `eae87919-6322-4bd2-ae9c-b1ce25d686da:0:0:1@30:this way` | replacement-event-lineage | E1 | UNRESOLVED no-candidate | none | none |
| `eae87919-6322-4bd2-ae9c-b1ce25d686da:0:0:2@37:this way` | replacement-event-lineage | E1 | UNRESOLVED no-candidate | E1:discard | none |
| `eccc9a54-2b56-4a02-9926-258d5b2e25fb:0:0:1@62:this way` | replacement-event-lineage | E1 | RESOLVED | E1:reveal | EVENT |
| `eccc9a54-2b56-4a02-9926-258d5b2e25fb:0:0:0@138:the chosen kind` | replacement-event-lineage | E2 | UNRESOLVED no-candidate | E2:chosen | none |
| `c259e16f-2a44-4552-8678-815f757a02e8:0:2:1@31:this way` | ability-borrowing-inheritance-pressure | E1 | RESOLVED | E1:exile | EVENT |
| `c259e16f-2a44-4552-8678-815f757a02e8:0:1:0@101:exiled with ~` | ability-borrowing-inheritance-pressure | E2 | RESOLVED | E2:exiled | LINKED |

## What this result does not claim

- No row is claimed correct; M05 reads every RESOLVED and NOT-COREFERENCE row
  and every fixture row, and a wrong RESOLVED goes to the Captain (§I5.8
  ruling 4).
- The reach figures equal §I5.5/§I5.7 by measurement; the rules were not
  tuned to them.
- The §I5.7 report and the delayed-trigger subset are findings, not defects
  and not resolutions.
