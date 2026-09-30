# C03 — H-REGION falsification result under interface/2

Wave `C03R.ORACLE-COMPILER-H-REGION-FALSIFICATION-I2`, Issue #1 checkpoint
5917886579, task 5900504363, command r3
(`c03r-oracle-compiler-h-region-falsification-i2-command-r3`). Accepted head
(base) `53f64ffbd772b52fd65e62ecd8c468ddb3b0aa59`; candidate base
`5ce079f` (C03-TESTS), on top of `baa6089` (C03-REGIONS) and `e2d2788`
(C03-KILL), after the interface/2 ratification commit `9efbbe1`. Interface:
`oracle-compiler-interface/2`, `oracle_compiler/INTERFACES.md` blob
`4ac4d856b651edde05b15c7065aa593f59561dcf` (Captain ratification 5900431196),
checked at the checked-out HEAD with `git rev-parse HEAD:oracle_compiler/INTERFACES.md`.
The commits after `5ce079f` on this branch touch only Agent Bus code; none
touches `experiments/`, `oracle_compiler/` or `tests/oracle_ingest/`.

This is a measurement: evidence, not authority. It ratifies nothing and makes
nothing production truth. No Oracle text appears here. Clauses are named by
their four-coordinate occurrence address `<oracle_id>:<face>:<paragraph>:<clause>`
and, where one exists, their census key `(stem, occurrence)`.

The interface/1 result `oracle_compiler/measurement/C03-H-REGION-RESULT.md`
(at `5078219`) stays on record untouched. It is the evidence interface/2's
rules R1-R3 answer; this document does not rewrite it.

## History on record

- Interface/1 C03 result at `5078219`: K3 and K4 killed, verdict CAPTAIN
  5898473142. Captain decision 5899825420 (option B) gave rulings R1-R3;
  interface/2 ratified them (5900431196, commit `9efbbe1`).
- First interface/2 run (C03R): C03-RESULT STOPPED (Worker evidence
  5900762579); C03R verdict CAPTAIN 5900868186; checkpoint 5900871681.
- Captain decision 5917475675 ordered a recovery re-run of C03-RESULT only
  (not a repair; repair budget used 0) and ruled on the R3 gap-test
  interpretation (below).
- Command r2 (5917500558) named `5ce079f` as its candidate base in error, and
  its Worker correctly stopped (result 5917528277, superseded). Command r3
  names `9efbbe1`, so the landed units `baa6089`, `e2d2788` and `5ce079f`
  count as done. Only C03-RESULT ran in this invocation. C03-REGIONS, C03-KILL
  and C03-TESTS were not re-run or edited.

### Correction to the prior partial draft (R3 reach)

The prior partial draft said that the literal reading of R3's gap test gives
R3 reach 0 and restores a K3 KILL. **That is wrong.** Measured, R3 reach is
**1 under both readings**.

- The implemented reading (`r3_list` / `_has_boundary_word` in
  `experiments/oracle_ingest/h_region_kill.py` at `5ce079f`) requires each gap
  to hold exactly one coordinator. Apart from that coordinator, no word the
  frozen `_BOUNDARY_WORD` treats as a boundary may appear anywhere in the gap,
  tested at every word end.
- Captain decision 5917475675 ruled this the interpretation and recorded
  corpus reach of 1 clause under both readings.
- On the population this run measures R3 reach 1:
  `bac0fcee-9c1a-46b7-86c8-ffbfcc1e96de:0:0:0`. No KILL is restored.

## Result

These are interface/2's words, by RESULT PRECEDENCE:

1. A KILL on a fixture or on a relevant population clause means "killed" for
   that condition.
2. Otherwise the result is "not killed on the P2 population".

The result is never "confirmed", because the population covers only three
object-lattice actions. UNRESOLVED is a finding for M04, not a verdict (I3).

| condition | relevant | PASS | UNRESOLVED | KILL | result | PASS coverage |
|---|---|---|---|---|---|---|
| K1 distinct ownership | 82 | 56 | 26 | 0 | not killed on the P2 population | sufficient |
| K2 repeated operations | 82 | 56 | 26 | 0 | not killed on the P2 population | sufficient |
| K3 relation endpoint | 92 | 74 | 18 | 0 | not killed on the P2 population | sufficient |
| K4 qualifier attachment | 88 | 79 | 9 | 0 | not killed on the P2 population | sufficient |
| K5 overlap / nesting | 29 | 29 | 0 | 0 | not killed on the P2 population | sufficient |
| K6 stronger identity needed | 94 | 84 | 10 | 0 | not killed on the P2 population | sufficient |
| K7 guesses or exceptions | 94 | 94 | 0 | 0 | not killed on the P2 population | sufficient |

**Under interface/2, H-REGION is not killed on the P2 population for any of
K1-K7.**

- No test KILLs on a fixture or on a relevant population clause.
- No test KILLs on an irrelevant population clause either: KILL is 0 over all
  94 clauses for every condition.
- `h_region_kill.py --check-not-killed` exits 0.
- No condition has zero PASS over its relevant clauses and fixtures, so none
  is flagged "PASS coverage insufficient". `--check-decided` exits 0.
- PASS coverage is reported separately and does not redefine the result.

All 32 interface/1 kills are changed by exactly one of R1-R3, as the Captain's
reach report predicted (table below). The 3 former K3 kills become UNRESOLVED,
never PASS: R3 names the endpoint, and R2 removes the payment head, which
leaves an unresolved back-reference. Those UNRESOLVED results are M04's
finding.

## Artifacts

Both artifacts are ignored experimental output. Each is portable (repo-relative
paths only) and was `--verify`-current when this document was written. Both
scripts are at their `5ce079f` bytes.

| artifact | sha256 |
|---|---|
| `experiments/out/oracle_ingest/c03/regions.json` | `e68eae465b4ee905dde7f2f87cd8d5143542a306243416ed649040de6a0f9be2` |
| `experiments/out/oracle_ingest/c03/kill.json` | `8af3175fc745d72a37c02914bd69921fe403b6dd697c5cb9099ab96fc2535632` |
| script `experiments/oracle_ingest/h_region.py` | `3c190461f8f7bf362a8e012ec0454add4a46c69cf7c31d31be7a6a5ea47c27c3` |
| script `experiments/oracle_ingest/h_region_kill.py` | `c7efeb7b0195cddbba1913bf0611b0a77b0ec4569940369bc36790b828098b90` |

Both artifacts carry `oracle-compiler-interface/2`, blob `4ac4d856…`.

## Identities (interface/2 I1, unchanged from interface/1): all four match

| input | sha256 |
|---|---|
| frozen probe `benchmarks/aq4/experiments/foundry_aq4_probes.py` | `eec9a4e2aea4c27d74dfffc6d4b82fdcd6f7292bd777aadc2c8625215c7c48f6` |
| corpus `data/raw/oracle-cards.jsonl.gz` | `2be88ba86da7ecbbb541094f28439c4888c5585c9ca8155e097f1cd0b548d872` |
| CR `config/cr/MTG_Comprehensive_Rules_2026-08-07_LLM.md` | `ca904dc900ce8e06c240960f937590df431aa2d97ec1569140cc910c56202d8b` |
| accepted C02 output `experiments/out/oracle_ingest/c02/all-run1.json` | `74e3559d785dc3ac47d14823ac1fec96dd446ae446d82a3ee45b03ef3f818dfd` |

`regions.json` also embeds, and `--verify` rechecks, the sha256 of:

- `oracle_compiler/FIXTURES.json` (`7bfc36b5…`)
- `oracle_compiler/INTERFACES.md` (file sha256 `6832983a…`, which is git blob `4ac4d856…`)
- the AQ4 contract (`e1aa1b91…`)
- `f0_select.py` (`1dc9175e…`)
- the census module (`42244743…`)
- `locality.py` (`16ebbabb…`)
- `delivery.py` (`f02641b4…`)

## Reconciliation (interface/2 I2): every figure matches

The population is defined on the frozen legacy heads. Under §I3a it does not
change: R2 changes which heads start a region, never which clauses are members.

| figure | re-derived | interface/2 and C02 |
|---|---|---|
| census rows | 2,110 | 2,110 |
| multi-head clauses (the C03 population) | 66 | 66 |
| head-count distribution | {1: 2044, 2: 65, 3: 1} | same |
| exile + return | 53 | 53 |
| multi-head by family | exile 60, destroy 6, bounce 0 | same |
| C02 examples that are members | 25 of 25 | 25 |

Fixtures come from `oracle_compiler/FIXTURES.json`; none was added, dropped or
swapped. Two fixture slots contribute no clause:

- `replacement-event-lineage` member "Tomorrow" (V1_NAMED_PRESSURE_SET)
  matches 0 cards by exact card or face name. It is recorded, not guessed.
- `conditional-second-operation` is F0_REVIEWED_NULL and has no member.

## Region derivation

This is interface/1's derivation, with only §I3a added.

- **Regions.** There is one region per legacy head, running from that head to
  the connector printed before the next head (CR 608.2c), or to the end of
  the clause scope.
- **Owner.** Each region's owner is the four-coordinate occurrence from the
  AQ4 register #29 chain. All 66 population clauses resolved.
- **Role marks.** Role marks are the ATTACH-3 categories, used as measurement
  labels only.
- **Rule table.** The table has 14 rules, all passing
  `assert_not_card_keyed`, including `attach-ability-prefix` (R1),
  `head-not-payment-cast` (R2) and `group-back-reference` (R3). Each carries
  only `id`, `kind`, `cr` and `pattern`.

## Per-rule reach (this run: the population and the fixtures)

| rule | population clauses | fixture clauses |
|---|---|---|
| R1 `attach-ability-prefix` | 27 | 3 |
| R2 `head-not-payment-cast` | 3 | 0 |
| R3 `group-back-reference` | 1 | 0 |

**R1 population (27 clauses, 28 spans).** By shape: cost-colon 11,
condition-trigger 16, intervening condition-marker 1. The one clause with two
R1 spans is `c4d2fdf9…:0:2:0`, which has a trigger and its intervening "if".

The 27 clauses are exactly the 27 R1 rows of the kill table below.

**R1 fixtures (3 clauses).** By shape: cost-colon 1, condition-trigger 2.

- `008d5896-6fc9-4aaa-8c6f-a44c2feb98bb:0:1:0`
- `00af96af-5eae-4044-a2f7-a08cd0699d1e:0:0:0`
- `c259e16f-2a44-4552-8678-815f757a02e8:0:2:0`

Each of these clauses has one region, so its interface/1 attachment was
already single and no outcome changes.

One fixture prefix span has no R1 shape: `eccc9a54…:0:0:0`, a condition. It
keeps its interface/1 outcome (attached). The population has no prefix span
without an R1 shape.

**R2 (3 population clauses).** Each dropped a legacy `cast` head. The frozen
detector is not edited. Each clause is reported below as address, head, and
character offset in the frozen clause.

- `16da72a3-d980-4dd8-99f2-8191cce00978:0:0:0`: `cast` @78
- `2cb98ca9-d7bb-416b-a17e-ee5f8e4d78f2:0:0:0`: `cast` @123
- `b095526e-94a4-416b-83de-d6271804ccf3:0:0:0`: `cast` @166

In `16da72a3…` and `2cb98ca9…`, the condition span that contained the
discounted head now attaches to one region under the ordinary rules.
`b095526e…` changes no kill outcome: it stays UNRESOLVED on K1 and K2, where
it is irrelevant.

**R3 (1 population clause).** `bac0fcee-9c1a-46b7-86c8-ffbfcc1e96de:0:0:0`
(exile, 0). "Those cards" names one printed coordinated list of 2 P3 marks in
region 0: a `target` mark at [6, 12) and a `second-object` mark at [39, 46).
The result is K3 UNRESOLVED for that relation, never PASS. R3 has no fixture
reach.

### Corpus-wide reach (Captain decision 5900431196, cited, not re-measured)

- **Whole corpus.** The whole pinned corpus is 32,557 cards / 74,106 clauses,
  with 0 derivation halts.
- **R1, ability-level qualifiers.** 892 clauses / 877 cards: cost-colon 249,
  trigger 643, intervening-if 47 spans.
- **Prefix spans of other shapes** keep their interface/1 outcomes:
  standalone condition-marker 118, condition-trigger not at scope start 2,
  duration 27, destination 13.
- **R2, "spent to cast".** 244 clauses / 221 cards. On 144 of them `cast` was
  the only legacy head, so they become no-region (UNRESOLVED), never PASS.
- **R3, plural reference to one printed list.** 1 clause (Become Anonymous),
  which becomes UNRESOLVED, never PASS. 9 plural multi-candidate references
  are not one list and keep their interface/1 outcomes.
- **Recorded kills.** All 32 recorded C03 kills fall inside the reach: K4 has
  27 R1 + 2 R2, and K3 has 2 R2 + 1 R3.

This run's population and fixture reach agrees with that split.

## The 32 interface/1 kills under interface/2

Every row was relevant under interface/1 and stays relevant. "Rule" is the rule
whose effect alone changes the outcome (`kill.json` `changed_from_interface1`).

| # | clause | census key | condition | interface/1 | interface/2 | rule |
|---|---|---|---|---|---|---|
| 1 | `16da72a3-d980-4dd8-99f2-8191cce00978:0:0:0` | (destroy, 0) | K3 | KILL | UNRESOLVED | R2 |
| 2 | `2cb98ca9-d7bb-416b-a17e-ee5f8e4d78f2:0:0:0` | (exile, 0) | K3 | KILL | UNRESOLVED | R2 |
| 3 | `bac0fcee-9c1a-46b7-86c8-ffbfcc1e96de:0:0:0` | (exile, 0) | K3 | KILL | UNRESOLVED | R3 |
| 4 | `14b839ef-80b1-4e7d-b2fd-38e973899cde:0:1:0` | (destroy, 0) | K4 | KILL | PASS | R1 |
| 5 | `169705c3-32c1-4628-b108-c37ca5f27e24:0:0:0` | (exile, 0) | K4 | KILL | PASS | R1 |
| 6 | `16da72a3-d980-4dd8-99f2-8191cce00978:0:0:0` | (destroy, 0) | K4 | KILL | PASS | R2 |
| 7 | `1ca97394-4e8c-4698-bea1-554f9b10927b:0:1:0` | (exile, 0) | K4 | KILL | PASS | R1 |
| 8 | `20194297-f2a4-4473-95bc-7c6835e5b6b3:0:1:0` | (exile, 0) | K4 | KILL | PASS | R1 |
| 9 | `2cb98ca9-d7bb-416b-a17e-ee5f8e4d78f2:0:0:0` | (exile, 0) | K4 | KILL | PASS | R2 |
| 10 | `33869ba6-13e5-4e48-8963-92f7965648fb:0:0:0` | (exile, 0) | K4 | KILL | PASS | R1 |
| 11 | `38a55562-1e2d-4240-9454-219a4a25d38d:0:2:0` | (destroy, 0) | K4 | KILL | PASS | R1 |
| 12 | `3a30089d-cd2d-49be-9b06-7a2454117692:0:1:0` | (exile, 0) | K4 | KILL | PASS | R1 |
| 13 | `4b072fbb-5e61-4009-bcb1-d493eb4a1be4:0:1:1` | (exile, 0) | K4 | KILL | PASS | R1 |
| 14 | `57d02dc8-e22e-4874-9f02-490a2528a28f:0:1:0` | (exile, 0) | K4 | KILL | PASS | R1 |
| 15 | `6df57d67-2fd9-4e7a-b67b-f361fc30e496:0:1:0` | (exile, 0) | K4 | KILL | PASS | R1 |
| 16 | `7c4c556c-b5e3-493a-a7b0-38c55b7809ac:0:1:0` | (exile, 0) | K4 | KILL | PASS | R1 |
| 17 | `913e6182-706a-4872-8c8a-e146b0ae0738:0:1:0` | (exile, 0) | K4 | KILL | PASS | R1 |
| 18 | `92019547-f6db-4ea6-8356-d0a90ace5662:0:1:0` | (exile, 0) | K4 | KILL | PASS | R1 |
| 19 | `9b1f552a-bddc-4fcb-ac67-b4a65b2f48ba:0:1:0` | (exile, 0) | K4 | KILL | PASS | R1 |
| 20 | `a6a7bf77-0560-4572-a826-3bc9df1f78d1:0:0:0` | (exile, 0) | K4 | KILL | PASS | R1 |
| 21 | `b11c250c-f191-4c52-ba02-a9176f163447:0:0:0` | (exile, 0) | K4 | KILL | PASS | R1 |
| 22 | `b1462c82-7702-451b-b612-990353a79ac4:0:2:0` | (exile, 0) | K4 | KILL | PASS | R1 |
| 23 | `bf20bc37-3205-45af-a3be-05d6835c0d87:0:0:0` | (destroy, 0) | K4 | KILL | PASS | R1 |
| 24 | `c4d2fdf9-637d-4e97-ae33-45f2d27bf8cd:0:2:0` | (exile, 0) | K4 | KILL | PASS | R1 |
| 25 | `c786a0aa-d86f-42c3-a7ea-5cb6ab72b5ec:0:0:0` | (exile, 0) | K4 | KILL | PASS | R1 |
| 26 | `cd1eda60-53e4-44d0-9b2c-7a57395e291f:0:0:0` | (exile, 0) | K4 | KILL | PASS | R1 |
| 27 | `dfbd3afc-9905-4cff-a4f4-df08a4d0a7fa:0:2:0` | (exile, 0) | K4 | KILL | PASS | R1 |
| 28 | `e875b468-b475-4573-adf6-312ca4ab6994:0:0:1` | (exile, 0) | K4 | KILL | PASS | R1 |
| 29 | `ef9a5bd1-6ce2-4570-9d42-89d997e2fc6f:0:1:0` | (exile, 0) | K4 | KILL | PASS | R1 |
| 30 | `f8a88521-80e5-419b-ab4e-f4b3aba8afa0:0:1:0` | (exile, 0) | K4 | KILL | PASS | R1 |
| 31 | `f96a2aa6-3259-4bb6-92cd-4d17215d04d0:0:0:0` | (exile, 0) | K4 | KILL | PASS | R1 |
| 32 | `fd09875f-71a1-41c2-b404-ff58f4d4cb6c:0:1:0` | (exile, 0) | K4 | KILL | PASS | R1 |

Totals: K3 3 (2 R2, 1 R3), K4 29 (27 R1, 2 R2). No other clause's outcome
differs from interface/1.

**R2 K3 rows (1, 2).** After R2 each clause has one region. Its conditional
relation now maps to that one region (PASS). Its back-reference is named in
region 0, but its referent is not an earlier operation of the clause, which
is C04's work. That makes the clause UNRESOLVED, not PASS.

## Measurements (C03-REGIONS (c))

| measurement | population (66) | fixtures (29) | all (94) |
|---|---|---|---|
| regions | 130 | 12 | 140 |
| regions per clause | {1: 3, 2: 62, 3: 1} | {0: 19, 1: 8, 2: 2} | {0: 19, 1: 11, 2: 63, 3: 1} |
| crossing clause / paragraph / face | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| overlap pairs / nesting pairs | 0 / 0 | 0 / 0 | 0 / 0 |
| clauses with a repeated operation | 1 | 0 | 1 |
| legacy vs corrected detector differing | 0 | 1 | 1 |

"All" is 94 rather than 95 because one fixture clause is also a population
clause.

- **Change from interface/1.** The population drops from 133 to 130 regions.
  These are the three R2 drops; those three clauses now have one region each.
- **Zeros by construction.** Crossing, overlap and nesting are 0 by
  construction, as under interface/1. A region is cut inside one chain clause
  at the next head's connector, and a census clause crossing a chain clause is
  refused.
- **Repeated operation.** `bf20bc37-3205-45af-a3be-05d6835c0d87:0:0:0`
  (destroy + destroy).
- **Detector difference.** `c4212ba4-8c43-40ca-aa36-b3b535659fa8:0:2:0`, a
  CR 700.2 mode bullet. This is reported only; the corrected detector is never
  substituted. The R2 drops are reported separately above.
- **Fixture clauses without a region.** 19, because no legacy head was
  extracted.

**ATTACH-3 attachment.** "R1" is the part of "attached" that is one
attachment to the ability.

| category | population spans | attached | of which R1 | multiple | none | no region |
|---|---|---|---|---|---|---|
| cost | 11 | 11 | 11 | 0 | 0 | 0 |
| condition | 19 | 19 | 17 | 0 | 0 | 0 |
| duration | 1 | 1 | 0 | 0 | 0 | 0 |
| destination | 53 | 53 | 0 | 0 | 0 | 0 |

| category | fixture spans | attached | of which R1 | multiple | none | no region |
|---|---|---|---|---|---|---|
| cost | 2 | 2 | 1 | 0 | 0 | 0 |
| condition | 10 | 4 | 2 | 0 | 0 | 6 |
| duration | 1 | 1 | 0 | 0 | 0 | 0 |
| destination | 7 | 1 | 0 | 0 | 0 | 6 |

The 2 population condition spans that attach without R1 are the two former
"crossing" spans in `16da72a3…` and `2cb98ca9…`. They attach after R2.

**COST-region precedent (AQ4 register #27), cited and not re-measured.** 113
COST regions on the frozen 782-occurrence open surface: 84 CR 113.3b/602.1a,
27 CR 606.2, 2 CR 702.6b. 0 cross a clause, paragraph or face boundary; 0 are
ambiguous; the maximum span is 58 characters.

## Kill tests (interface/2 I3 with the amended K3 and K4)

Each test ran on every population clause (66) and every fixture clause (29),
94 distinct clauses. Distinct required operations and relevance are exactly as
interface/1's result states them. They come from independent evidence and
consumer questions (ATTACH-1, ATTACH-3, C2) and FIXTURES roles, never from a
detector alone. Fixtures are always relevant.

| condition | all: PASS / UNRESOLVED / KILL | relevant | relevant: PASS / UNRESOLVED / KILL |
|---|---|---|---|
| K1 | 56 / 38 / 0 | 82 | 56 / 26 / 0 |
| K2 | 56 / 38 / 0 | 82 | 56 / 26 / 0 |
| K3 | 76 / 18 / 0 | 92 | 74 / 18 / 0 |
| K4 | 85 / 9 / 0 | 88 | 79 / 9 / 0 |
| K5 | 94 / 0 / 0 | 29 | 29 / 0 / 0 |
| K6 | 84 / 10 / 0 | 94 | 84 / 10 / 0 |
| K7 | 94 / 0 / 0 | 94 | 94 / 0 / 0 |

### KILL

None, on any clause.

### UNRESOLVED (findings for M04, not verdicts)

**K1 / K2.** Unchanged from interface/1.

- The 26 relevant UNRESOLVED are fixture clauses where no independent
  evidence establishes two distinct required operations.
- The 12 irrelevant population UNRESOLVED have no evidence either. The same 12
  clauses are listed in the interface/1 result.

**K3 (18, all relevant).** These are interface/1's 15 plus the three former
kills.

The 15 carried over from interface/1:

- `008d5896-6fc9-4aaa-8c6f-a44c2feb98bb:0:1:0` (exile, 0) · `008d5896…:0:1:1`
- `1167fe30-32b8-4381-8067-a05cd345977b:0:1:1`
- `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:2:1`
- `766c644c-04fe-4b01-93dd-09a50d78d01f:0:0:0` · `766c644c…:0:1:0`
- `c259e16f-2a44-4552-8678-815f757a02e8:0:0:0` · `c259e16f…:0:1:0` · `c259e16f…:0:2:1`
- `eae87919-6322-4bd2-ae9c-b1ce25d686da:0:0:0` · `eae87919…:0:0:1` · `eae87919…:0:0:2`
- `eccc9a54-2b56-4a02-9926-258d5b2e25fb:0:0:0` · `eccc9a54…:0:0:1`
- `fd09875f-71a1-41c2-b404-ff58f4d4cb6c:0:1:0` (exile, 0)

The three former kills:

- `16da72a3…:0:0:0` (R2)
- `2cb98ca9…:0:0:0` (R2)
- `bac0fcee…:0:0:0` (R3)

**K4 (9, all fixture clauses).** An ATTACH-3 span sits in a clause with no
region. These are unchanged from interface/1:

- `1167fe30…:0:1:1`
- `19b229c4…:0:2:1`
- `766c644c…:0:0:0`
- `c259e16f…:0:2:1`
- `c4212ba4-8c43-40ca-aa36-b3b535659fa8:0:0:0`
- `eae87919…:0:0:0` · `eae87919…:0:0:1` · `eae87919…:0:0:2`
- `eccc9a54…:0:0:1`

**K6 (10, all fixture clauses).** Unchanged: the nine K4 UNRESOLVED clauses
plus `008d5896…:0:0:0`.

**K5 and K7.** No UNRESOLVED; K7 has no UNRESOLVED outcome.

## Negative controls

KILLs on these rigged inputs are expected and are not kills.

**`regions.json` records 9 controls, all firing:**

- A rigged identity hash halts.
- A rigged reconciliation figure halts.
- A clause crossing the chain clause is refused.
- A card-keyed rule halts.
- An output carrying the repository root fails `--check-determinism`.
- Card-keyed variants of R1, R2 and R3 halt.
- A standalone "If …, exile …, then return it" (no trigger word) keeps a
  multiple attachment under R1.
- A "you may cast" head is not discounted by R2 and still starts a region.
- A trigger and its intervening "if" attach once, to the ability, under R1.

**`kill.json` records 26 controls, all firing:**

- The KILL and UNRESOLVED arms of K1 through K6.
- K7 KILL for a card-keyed rule, for a boundary not at a printed token, and
  for a card-keyed R3 table entry.
- R3 never yields PASS: a plural reference to one coordinated list is
  UNRESOLVED.
- R3 does not apply to a singular "it", nor to a plural reference over
  candidates that fail the gap test. Both keep KILL.
- An ineligible prefix span (duration, destination, standalone
  condition-marker) still KILLs K4.
- An R1 trigger prefix PASSES K4.
- `--check-not-killed` fails on a rigged real kill. It passes on a
  control-only kill and on a KILL on an irrelevant population clause.
- `--check-decided` flags an all-UNRESOLVED condition and clears it with one
  PASS.
- A rigged clause asking only ATTACH-3, with a K4 KILL, is relevant and fails
  `--check-not-killed`.
- A rigged mixed input yields "killed", fails `--check-not-killed`, and is
  flagged by `--check-decided`.

`tests/oracle_ingest/test_h_region.py` (landed at `5ce079f`) has 85 tests on
inline synthetic clauses. The R1-R3 regression clauses are named only by
address and read from the pinned corpus at run time.
