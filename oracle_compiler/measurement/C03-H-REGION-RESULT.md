# C03 — H-REGION falsification result

Wave `C03.ORACLE-COMPILER-H-REGION-FALSIFICATION`, Issue #1 checkpoint
5897412746, task 5895504393, base `53f64ffbd772b52fd65e62ecd8c468ddb3b0aa59`.
Interface: `oracle-compiler-interface/1` (INTERFACES.md blob
`3c34cf5a4e8150e43cbce2ec6a92e30272560f6e`). This is a measurement: evidence,
not authority. It ratifies nothing and makes nothing production truth. No
Oracle text appears here. Clauses are named by their four-coordinate occurrence
address `<oracle_id>:<face>:<paragraph>:<clause>` and, where one exists, their
census key `(stem, occurrence)`.

## Result

Interface/1's words, by RESULT PRECEDENCE. A KILL on a fixture or on a relevant
population clause means "killed" for that condition. Otherwise the result is
"not killed on the P2 population". The result is never "confirmed", because the
population covers only three object-lattice actions.

| condition | result |
|---|---|
| K1 distinct ownership | not killed on the P2 population |
| K2 repeated operations | not killed on the P2 population |
| K3 relation endpoint | **killed** (3 relevant population clauses) |
| K4 qualifier attachment | **killed** (29 relevant population clauses) |
| K5 overlap / nesting | not killed on the P2 population |
| K6 stronger identity needed | not killed on the P2 population |
| K7 guesses or exceptions | not killed on the P2 population |

**H-REGION is killed for K3 and K4.** By interface/1 I3's decision rule this is
a STOP to the Captain and to the AQ4 reserved finer-effect path (V1 §5). It is
never an ad hoc identifier. `h_region_kill.py --check-not-killed` exits
non-zero, which blocks ACCEPT: the reviewer's verdict is CAPTAIN, never REPAIR.
No unit may edit `h_region.py`, `h_region_kill.py` or their tests to turn this
check green.

No condition has zero PASS over its relevant clauses and fixtures, so none is
flagged "PASS coverage insufficient". Coverage is reported separately and
does not redefine the result. UNRESOLVED counts are findings for M04, not
verdicts (I3).

## Artifacts

Both artifacts are ignored experimental output. Each is x2 byte-identical,
portable (repo-relative paths only) and `--verify`-current.

| artifact | sha256 |
|---|---|
| `experiments/out/oracle_ingest/c03/regions.json` | `787f6ea8e6b556579c29f91c0e4068911666b880d7ce169da731782772468c32` |
| `experiments/out/oracle_ingest/c03/kill.json` | `5541859d7cde9805aa25dcf82d3253e55ad9f320a204e6bcf7b9b4e149e97f06` |
| script `experiments/oracle_ingest/h_region.py` | `24ea5b617136f50e2e33a10afcf79ea652d488715a40c82d465e306a660ee9e5` |
| script `experiments/oracle_ingest/h_region_kill.py` | `a846073bbeaeec70bf059b3fa4ad845c67baf164a40b5825a9671cad4364f8ef` |

## Identities (interface/1 I1): all four match

| input | sha256 |
|---|---|
| frozen probe `benchmarks/aq4/experiments/foundry_aq4_probes.py` | `eec9a4e2aea4c27d74dfffc6d4b82fdcd6f7292bd777aadc2c8625215c7c48f6` |
| corpus `data/raw/oracle-cards.jsonl.gz` | `2be88ba86da7ecbbb541094f28439c4888c5585c9ca8155e097f1cd0b548d872` |
| CR `config/cr/MTG_Comprehensive_Rules_2026-08-07_LLM.md` | `ca904dc900ce8e06c240960f937590df431aa2d97ec1569140cc910c56202d8b` |
| accepted C02 output `experiments/out/oracle_ingest/c02/all-run1.json` | `74e3559d785dc3ac47d14823ac1fec96dd446ae446d82a3ee45b03ef3f818dfd` |

`regions.json` also embeds, and `--verify` rechecks, the sha256 of:

- `oracle_compiler/FIXTURES.json` (`7bfc36b5…`)
- `oracle_compiler/INTERFACES.md` (`78967da5…`)
- the AQ4 contract (`e1aa1b91…`)
- `f0_select.py` (`1dc9175e…`)
- the census module (`42244743…`)
- `locality.py` (`16ebbabb…`)
- `delivery.py` (`f02641b4…`)

## Reconciliation (interface/1 I2): every figure matches

The population was re-derived with the frozen `foundry_qualifier_census.population()`
and `foundry_aq4_probes.effect_heads`. Every figure was checked against both
interface/1's literals and the pinned C02 JSON.

| figure | re-derived | interface/1 and C02 |
|---|---|---|
| census rows | 2,110 | 2,110 |
| multi-head clauses (the C03 population) | 66 | 66 |
| head-count distribution | {1: 2044, 2: 65, 3: 1} | same |
| exile + return | 53 | 53 |
| multi-head by family | exile 60, destroy 6, bounce 0 | same |
| C02 examples that are members | 25 of 25 (the first 25 multi-head rows equal the C02 examples byte-for-byte) | 25 |

Fixtures come from `oracle_compiler/FIXTURES.json`; none was added, dropped or
swapped. Two fixture slots contribute no clause:

- `replacement-event-lineage` member "Tomorrow" (V1_NAMED_PRESSURE_SET) matches
  no card by exact card or face name. It is recorded UNRESOLVED (FIXTURES
  gold_law `unresolved_is_valid`), not guessed. One prefix match,
  `51d517c9-2812-44ce-ab4d-e5422b5ecf6c`, is shown and not used. Resolving
  the member is a Manager/Captain decision.
- `conditional-second-operation` is F0_REVIEWED_NULL and has no member.

## Region derivation (C03-REGIONS (b))

- **One region per head.** Each head of the frozen legacy detector (the
  population's own) gets one region. Head positions are required to equal
  `effect_heads` exactly. A region runs from its head to the connector printed
  before the next head (CR 608.2c), or to the end of the clause scope.
- **Owner.** Each region's owner is the four-coordinate occurrence from the
  AQ4 register #29 chain: `foundry_locality.units` → `strip_reminder` →
  `sentence_spans`. Each census clause is placed by `foundry_locality.resolve`
  into exactly one chain clause. All 66 population clauses resolved.
- **Role marks** are the four ATTACH-3 categories, as measurement labels only:
  - cost: CR 602.1a / 606.2 colon, CR 702.6b keyword dash
  - condition: CR 603.1 trigger, frozen P4 condition markers
  - duration: CR 611.2a/b
  - destination: CR 400.1 zones, plus five declared prepositions (CR 207.2d
    precedent)
- **No card-keyed rule.** No rule is keyed to a card, name or oracle_id. The
  guard halts on a rigged one.
- **Negative controls.** All five fire: a rigged identity hash, a rigged
  reconciliation figure, a clause crossing a chain clause, a card-keyed rule,
  and an output carrying the repository root.

## Measurements (C03-REGIONS (c))

| measurement | population (66) | fixtures (29) | all (94) |
|---|---|---|---|
| regions | 133 | 12 | 143 |
| regions per clause | {2: 65, 3: 1} | {0: 19, 1: 8, 2: 2} | {0: 19, 1: 8, 2: 66, 3: 1} |
| crossing clause / paragraph / face | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| overlap pairs / nesting pairs | 0 / 0 | 0 / 0 | 0 / 0 |
| clauses with a repeated operation | 1 | 0 | 1 |
| legacy vs corrected detector differing | 0 | 1 | 1 |

"All" is 94 rather than 95 because one fixture clause is also a population clause.

- **Zeros by construction.** Crossing, overlap and nesting are 0 by
  construction. A region is cut inside one chain clause at the next head's
  connector, and a census clause crossing a chain clause is refused, not
  measured. This is stated so the zeros are not read as measurements that
  could have come out otherwise.
- **Repeated operation:** `bf20bc37-3205-45af-a3be-05d6835c0d87:0:0:0`
  (destroy, 0), destroy + destroy.
- **Detector difference:** `c4212ba4-8c43-40ca-aa36-b3b535659fa8:0:2:0`. It is
  a CR 700.2 mode bullet: the corrected detector finds destroy and the legacy
  detector does not. This is reported only; regions stay legacy-derived.
- **Fixture clauses without a region:** 19, because no legacy head was
  extracted.

ATTACH-3 attachment. "Multiple (prefix)" means a span printed before the first
operation, a CR 602.1a cost or CR 603.1 trigger condition, governs every region
of its clause. "Multiple (crossing)" means the span crosses a region boundary.

| category | population spans | attached (success) | multiple (prefix) | multiple (crossing) | none | no region (extraction) |
|---|---|---|---|---|---|---|
| cost | 11 | 0 | 11 | 0 | 0 | 0 |
| condition | 19 | 0 | 17 | 2 | 0 | 0 |
| duration | 1 | 1 | 0 | 0 | 0 | 0 |
| destination | 53 | 53 | 0 | 0 | 0 | 0 |

| category | fixture spans | attached | multiple | none | no region |
|---|---|---|---|---|---|
| cost | 2 | 2 | 0 | 0 | 0 |
| condition | 10 | 4 | 0 | 0 | 6 |
| duration | 1 | 1 | 0 | 0 | 0 |
| destination | 7 | 1 | 0 | 0 | 6 |

**COST-region precedent (AQ4 register #27), cited and not re-measured:**

- 113 COST regions on the frozen 782-occurrence open surface: 84 CR
  113.3b/602.1a, 27 CR 606.2, 2 CR 702.6b.
- 0 crossing a clause, paragraph or face boundary; 0 ambiguous; max span 58
  characters.

Every population cost span here is also clause-local. What fails is attaching
it to one operation region of a multi-operation clause, not its ownership by
the occurrence.

## Kill tests (interface/1 I3)

Each test ran on every population clause (66) and every fixture clause (29):
94 distinct clauses.

**Distinct required operations** come only from independent evidence:

- a FIXTURES role that asserts them (`two-sequential-operations`,
  `delayed-return-same-object`);
- C2 asking about an exile and a return separately, each with its own
  instruction boundary under either detector path;
- two census rows owned by one occurrence.

Without such evidence, K1 and K2 are UNRESOLVED.

**Relevance** comes from the consumer questions and FIXTURES roles, never from
a detector alone. Fixtures are always relevant. A question applies as follows:

- ATTACH-1 applies to a clause carrying a census row.
- C2 applies to the frozen P3 exile-and-return form, or to the delayed-return
  fixture.
- ATTACH-3 applies to a clause printing a cost, condition, duration or
  destination span.

| condition | all: PASS / UNRESOLVED / KILL | relevant | relevant: PASS / UNRESOLVED / KILL | PASS coverage |
|---|---|---|---|---|
| K1 | 56 / 38 / 0 | 82 | 56 / 26 / 0 | sufficient |
| K2 | 56 / 38 / 0 | 82 | 56 / 26 / 0 | sufficient |
| K3 | 76 / 15 / 3 | 92 | 74 / 15 / 3 | sufficient |
| K4 | 56 / 9 / 29 | 88 | 50 / 9 / 29 | sufficient |
| K5 | 94 / 0 / 0 | 29 | 29 / 0 / 0 | sufficient |
| K6 | 84 / 10 / 0 | 94 | 84 / 10 / 0 | sufficient |
| K7 | 94 / 0 / 0 | 94 | 94 / 0 / 0 | sufficient |

### Firing clauses: KILL (all on relevant population clauses; none on a fixture)

**K3 (3).**

- `16da72a3-d980-4dd8-99f2-8191cce00978:0:0:0` (destroy, 0): a conditional
  endpoint maps to 2 regions.
- `2cb98ca9-d7bb-416b-a17e-ee5f8e4d78f2:0:0:0` (exile, 0): a conditional
  endpoint maps to 2 regions.
- `bac0fcee-9c1a-46b7-86c8-ffbfcc1e96de:0:0:0` (exile, 0): a plural
  back-reference has 2 candidate referent spans (two frozen P3 participants)
  inside one region. It is relevant because ATTACH-1 names the census action's
  object, and that object is the antecedent endpoint.

**K4 (29).**

In 27 clauses, an ability-prefix span attaches to both regions of the clause:
11 costs and 16 trigger conditions, and one of those clauses also carries an
intervening "if". In the other 2 clauses, a condition span crosses a region
boundary.

| census key | clauses |
|---|---|
| (destroy, 0) | `14b839ef-80b1-4e7d-b2fd-38e973899cde:0:1:0` · `16da72a3-d980-4dd8-99f2-8191cce00978:0:0:0` (crossing) · `38a55562-1e2d-4240-9454-219a4a25d38d:0:2:0` · `bf20bc37-3205-45af-a3be-05d6835c0d87:0:0:0` |
| (exile, 0) | `169705c3-32c1-4628-b108-c37ca5f27e24:0:0:0` · `1ca97394-4e8c-4698-bea1-554f9b10927b:0:1:0` · `20194297-f2a4-4473-95bc-7c6835e5b6b3:0:1:0` · `2cb98ca9-d7bb-416b-a17e-ee5f8e4d78f2:0:0:0` (crossing) · `33869ba6-13e5-4e48-8963-92f7965648fb:0:0:0` · `3a30089d-cd2d-49be-9b06-7a2454117692:0:1:0` · `4b072fbb-5e61-4009-bcb1-d493eb4a1be4:0:1:1` · `57d02dc8-e22e-4874-9f02-490a2528a28f:0:1:0` · `6df57d67-2fd9-4e7a-b67b-f361fc30e496:0:1:0` · `7c4c556c-b5e3-493a-a7b0-38c55b7809ac:0:1:0` · `913e6182-706a-4872-8c8a-e146b0ae0738:0:1:0` · `92019547-f6db-4ea6-8356-d0a90ace5662:0:1:0` · `9b1f552a-bddc-4fcb-ac67-b4a65b2f48ba:0:1:0` · `a6a7bf77-0560-4572-a826-3bc9df1f78d1:0:0:0` · `b11c250c-f191-4c52-ba02-a9176f163447:0:0:0` · `b1462c82-7702-451b-b612-990353a79ac4:0:2:0` · `c4d2fdf9-637d-4e97-ae33-45f2d27bf8cd:0:2:0` · `c786a0aa-d86f-42c3-a7ea-5cb6ab72b5ec:0:0:0` · `cd1eda60-53e4-44d0-9b2c-7a57395e291f:0:0:0` · `dfbd3afc-9905-4cff-a4f4-df08a4d0a7fa:0:2:0` · `e875b468-b475-4573-adf6-312ca4ab6994:0:0:1` · `ef9a5bd1-6ce2-4570-9d42-89d997e2fc6f:0:1:0` · `f8a88521-80e5-419b-ab4e-f4b3aba8afa0:0:1:0` · `f96a2aa6-3259-4bb6-92cd-4d17215d04d0:0:0:0` · `fd09875f-71a1-41c2-b404-ff58f4d4cb6c:0:1:0` |

**Note for review.** In `16da72a3…` and `2cb98ca9…` the second region comes
from the head `cast` inside a CR 601.2 payment condition. F0's reviewed-null
judgment recorded this head as a detector false-positive class, not an
instruction. I3 offers no card-independent rule to discount a candidate head,
so these stay KILL and are written down, not hidden. The other 28 kills do not
depend on that head.

### UNRESOLVED (findings for M04, not verdicts)

**K1 / K2.** The 26 relevant UNRESOLVED are all fixture clauses where no
independent evidence establishes two distinct required operations. The 12
irrelevant population UNRESOLVED have no evidence either:

- (destroy, 0): `14b839ef…:0:1:0`, `16da72a3…:0:0:0`, `38a55562…:0:2:0`,
  `a2a380d8-4df7-4357-862c-ed3fb795db6c:0:0:0`, `bf20bc37…:0:0:0`
- (exile, 0): `1ca97394…:0:1:0`, `2cb98ca9…:0:0:0`, `913e6182…:0:1:0`,
  `97cf544e-ffbf-4730-8cd2-4f1d5be933f2:0:0:0`,
  `b095526e-94a4-416b-83de-d6271804ccf3:0:0:0`, `bac0fcee…:0:0:0`,
  `d6239ada-c72a-49b2-882c-6dae1dd366e3:0:0:0`

**K3 (15, all relevant).** A back-reference whose referent is not an earlier
operation of its clause (reference resolution is C04's work), or a clause with
no derived region:

- `008d5896-6fc9-4aaa-8c6f-a44c2feb98bb:0:1:0` (exile, 0) · `008d5896…:0:1:1`
- `1167fe30-32b8-4381-8067-a05cd345977b:0:1:1`
- `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:2:1`
- `766c644c-04fe-4b01-93dd-09a50d78d01f:0:0:0` · `766c644c…:0:1:0`
- `c259e16f-2a44-4552-8678-815f757a02e8:0:0:0` · `c259e16f…:0:1:0` · `c259e16f…:0:2:1`
- `eae87919-6322-4bd2-ae9c-b1ce25d686da:0:0:0` · `eae87919…:0:0:1` · `eae87919…:0:0:2`
- `eccc9a54-2b56-4a02-9926-258d5b2e25fb:0:0:0` · `eccc9a54…:0:0:1`
- `fd09875f-71a1-41c2-b404-ff58f4d4cb6c:0:1:0` (exile, 0)

**K4 (9, all fixture clauses).** An ATTACH-3 span in a clause with no region
(no legacy head extracted):

- `1167fe30…:0:1:1`
- `19b229c4…:0:2:1`
- `766c644c…:0:0:0`
- `c259e16f…:0:2:1`
- `c4212ba4-8c43-40ca-aa36-b3b535659fa8:0:0:0`
- `eae87919…:0:0:0` · `eae87919…:0:0:1` · `eae87919…:0:0:2`
- `eccc9a54…:0:0:1`

**K6 (10, all fixture clauses).** Nine are the K4 UNRESOLVED clauses above: an
ATTACH-3 span has no region. The tenth, `008d5896…:0:0:0`, is a delayed-return
fixture clause with no exile or return extracted.

**K5 and K7.** No UNRESOLVED; K7 has no UNRESOLVED outcome.

### What held

- **K1 and K2 PASS on 56 clauses.** Every exile + return clause and both
  operation-asserting fixtures give each distinct required operation its own
  source-spanned region, owned by its occurrence. No repeated required
  operation shares a span.
- **K5 PASS everywhere.** No two regions overlap.
- **K6 never KILLs.**
- **K7 PASS on every clause.** Every boundary is a printed head, a printed
  connector or the clause scope. No rule is keyed to a card, name or oracle_id.

## Negative controls (C03-KILL)

All 21 fire on rigged, synthetic inputs, and each run records them in
`kill.json`. KILLs on these inputs are expected and are not kills.

- The KILL and UNRESOLVED arms of K1 through K6, and K7's KILL for both a
  card-keyed rule and a boundary not at a printed token.
- `--check-not-killed` fails on a rigged real kill. It passes on a
  control-only kill and on a KILL on an irrelevant population clause.
- `--check-decided` flags an all-UNRESOLVED condition and clears it with one
  PASS.
- A rigged clause asking only ATTACH-3, with a K4 KILL, is relevant and fails
  `--check-not-killed`.
- A rigged mixed input yields "killed" for K4, fails `--check-not-killed`, and
  is flagged by `--check-decided` for K5.

`tests/oracle_ingest/test_h_region.py` has 45 tests on inline synthetic clauses,
and all pass.
