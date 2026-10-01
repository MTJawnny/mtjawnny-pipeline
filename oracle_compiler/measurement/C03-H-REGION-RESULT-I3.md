# C03 — H-REGION falsification result under interface/3

Wave `C03R3.ORACLE-COMPILER-H-REGION-FALSIFICATION-I3`, Issue #1 checkpoint
5938520316, task 5938513841 (`c03r3-oracle-compiler-h-region-falsification-i3-command`).
Accepted head (base) `8cfd3f156ebafbfb63da7e95d1d3658460f5fa79`; candidate
base `aebc9ba` (the interface/3 ratification landing, record 5925482946). This
wave's units landed as `08d7cb1` (C03-REGIONS), `e1a96ee` (C03-KILL) and
`9f2160f` (C03-TESTS). Interface: `oracle-compiler-interface/3`,
`oracle_compiler/INTERFACES.md` blob `119778a68c0e4e8378f0a117b7c22884ec5eda4b`
(Captain decisions 5925134485 and 5925371124), checked at the checked-out HEAD
with `git rev-parse HEAD:oracle_compiler/INTERFACES.md`.

This is a measurement: evidence, not authority. It ratifies nothing and makes
nothing production truth. Clauses are named by their four-coordinate
occurrence address `<oracle_id>:<face>:<paragraph>:<clause>` and, where one
exists, their census key `(stem, occurrence)`. The only Oracle text here is R4
label text, written as the canonical chain text prints it; no card is named as
a card.

The interface/1 result (`C03-H-REGION-RESULT.md`) and the interface/2 result
(`C03-H-REGION-RESULT-I2.md`) stay on record untouched. So does the M04 review
(`oracle_compiler/analysis/M04-H-REGION-REVIEW.md`), whose finding FS-2 R4
answers.

## History on record

- Interface/1 C03 result: K3 and K4 killed, verdict CAPTAIN 5898473142.
  Captain decision 5899825420 gave rulings R1-R3; interface/2 ratified them
  (5900431196).
- Interface/2 C03 result: not killed on the P2 population for K1-K7.
- M04 review found FS-1 (a region started by a token that is not an operation)
  and FS-2 (a trigger condition behind a label is never marked). FS-2 was
  RULED by Captain decision 5925134485, and decision 5925371124 ruled flavor
  labels ignored. Interface/3 adds rule R4 `ability-label` for them, reads R1's
  scope start after an R4 label, and names R4 in the K7 row.
- This wave re-runs C03 under interface/3. Its only change to the derivation,
  the kill tests and their tests is pinning interface/3 and implementing R4.

## Result

These are interface/3's words, by RESULT PRECEDENCE:

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
| K4 qualifier attachment | 89 | 79 | 10 | 0 | not killed on the P2 population | sufficient |
| K5 overlap / nesting | 29 | 29 | 0 | 0 | not killed on the P2 population | sufficient |
| K6 stronger identity needed | 94 | 83 | 11 | 0 | not killed on the P2 population | sufficient |
| K7 guesses or exceptions | 94 | 94 | 0 | 0 | not killed on the P2 population | sufficient |

**Under interface/3, H-REGION is not killed on the P2 population for any of
K1-K7.**

- No test KILLs on a fixture or on a relevant population clause, and KILL is 0
  over all 94 clauses for every condition.
- `h_region_kill.py --check-not-killed` exits 0.
- No condition has zero PASS over its relevant clauses and fixtures, so none
  is flagged "PASS coverage insufficient". `--check-decided` exits 0. PASS
  coverage is reported separately and does not redefine the result.

R4 changes three outcomes and one relevance, all on FS-1 / FS-2 rows (BEFORE /
AFTER below). Two outcomes move from PASS to UNRESOLVED; none becomes a KILL.

## Artifacts

Both artifacts are ignored experimental output, portable (repo-relative paths
only), byte-identical on regeneration (`--check-determinism`), and
`--verify`-current when this document was written.

| artifact | sha256 |
|---|---|
| `experiments/out/oracle_ingest/c03/regions.json` | `95b680b1a9d36d7243c4cc90e30ebc4fbc9fd86b63d25290604eb89153f90f8a` |
| `experiments/out/oracle_ingest/c03/kill.json` | `fdb3a2d756b3e5d574cdfa313cf043dbee534a64197967b091afa2daf619a0f2` |
| script `experiments/oracle_ingest/h_region.py` | `c6baffbdfbf1e54c5b9d885ad6936dd1421f020119d5a13a16c50ff1d451df6e` |
| script `experiments/oracle_ingest/h_region_kill.py` | `4b94e90288b4902393229e28cddc3f3b18743b1d3e8c5680daaf7c0b5f8bad8a` |

Both artifacts carry `oracle-compiler-interface/3`, blob `119778a6…`.

## Identities (interface/3 I1, unchanged from interface/1): all four match

| input | sha256 |
|---|---|
| frozen probe `benchmarks/aq4/experiments/foundry_aq4_probes.py` | `eec9a4e2aea4c27d74dfffc6d4b82fdcd6f7292bd777aadc2c8625215c7c48f6` |
| corpus `data/raw/oracle-cards.jsonl.gz` | `2be88ba86da7ecbbb541094f28439c4888c5585c9ca8155e097f1cd0b548d872` |
| CR `config/cr/MTG_Comprehensive_Rules_2026-08-07_LLM.md` | `ca904dc900ce8e06c240960f937590df431aa2d97ec1569140cc910c56202d8b` |
| accepted C02 output `experiments/out/oracle_ingest/c02/all-run1.json` | `74e3559d785dc3ac47d14823ac1fec96dd446ae446d82a3ee45b03ef3f818dfd` |

`regions.json` also embeds, and `--verify` rechecks, the sha256 of:

- `oracle_compiler/FIXTURES.json` (`7bfc36b5…`)
- `oracle_compiler/INTERFACES.md` (file sha256 `8cebf20d…`, which is git blob `119778a6…`)
- the AQ4 contract (`e1aa1b91…`)
- `f0_select.py` (`1dc9175e…`)
- the census module (`42244743…`)
- `locality.py` (`16ebbabb…`)
- `delivery.py` (`f02641b4…`)

## Reconciliation (interface/3 I2, unchanged): every figure matches

The population is defined on the frozen legacy heads and does not change under
§I3a: R2 and R4 change which heads start a region, never which clauses are
members.

| figure | re-derived | interface/3 and C02 |
|---|---|---|
| census rows | 2,110 | 2,110 |
| multi-head clauses (the C03 population) | 66 | 66 |
| head-count distribution | {1: 2044, 2: 65, 3: 1} | same |
| exile + return | 53 | 53 |
| multi-head by family | exile 60, destroy 6, bounce 0 | same |
| C02 examples that are members | 25 of 25 | 25 |

Fixtures come from `oracle_compiler/FIXTURES.json`; none was added, dropped or
swapped. Two fixture slots contribute no clause, as under interface/2:
`replacement-event-lineage` (a V1_NAMED_PRESSURE_SET member that matches 0
cards by exact card or face name, recorded, not guessed) and
`conditional-second-operation` (F0_REVIEWED_NULL, no member).

### The R4-off view reproduces interface/2 (a STOP on any difference)

`kill.json` evaluates every clause twice: the R4-on view (interface/3) and the
R4-off view, which is the interface/2 derivation exactly (no label located;
scope start, role marks, regions and heads as interface/2 computes them). The
R4-off view reproduces every accepted interface/2 figure:

- Per condition, all 94 / relevant, PASS-UNRESOLVED-KILL: K1 56-38-0 /
  56-26-0; K2 56-38-0 / 56-26-0; K3 76-18-0 / 74-18-0; K4 85-9-0 / 79-9-0; K5
  94-0-0 / 29-0-0; K6 84-10-0 / 84-10-0; K7 94-0-0 / 94-0-0.
- The interface/1-to-interface/2 change rows: exactly 32 (K4 KILL -> PASS by
  R1: 27; by R2: 2; K3 KILL -> UNRESOLVED by R2: 2; by R3: 1).
- R1-R3 reach: population 27 / 3 / 1, fixtures 3 / 0 / 0.

These figures, the 32 rows and the R1-R3 reach are equal to the accepted
interface/2 `kill.json`, as are all 94 R4-off clause records to the accepted
interface/2 `regions.json`. Every interface/1-versus-interface/2 record is
computed on the R4-off view only. A rigged R4-on mark fed into the R1-R3
records changes them, and the reconciliation catches it (a recorded control).

**R4 IS CONFINED.** For every clause and fixture with no IGNORED label (no
label, or a KEPT one), the R4-on record equals the R4-off record: scope,
regions, heads, role marks, attachments and K1-K7 outcomes. Both scripts halt
otherwise, and both checks are shown to fire on rigged input.

## Region derivation

This is interface/2's derivation, with only §I3a R4 added.

- **Regions.** There is one region per legacy head that R2 and R4 do not drop,
  running from that head to the connector printed before the next head
  (CR 608.2c), or to the end of the clause scope.
- **Owner.** Each region's owner is the four-coordinate occurrence from the
  AQ4 register #29 chain. All 66 population clauses resolved.
- **Role marks.** Role marks are the ATTACH-3 categories, used as measurement
  labels only.
- **Rule table.** The table has 15 rules, all passing
  `assert_not_card_keyed`, including `attach-ability-prefix` (R1),
  `head-not-payment-cast` (R2), `group-back-reference` (R3) and
  `ability-label` (R4). Each carries only `id`, `kind`, `cr` and `pattern`.

### R4 `ability-label`, as implemented

- **Locate.** A label sits at the start of a chain clause of clause ordinal 0
  (a line), after a CR 700.2 bullet if the line has one, up to the first ` — `
  with text after it on the line. It holds no `—`, `:`, `;`, `.`, `•` or `"`.
  A dash at the end of a line is no label.
- **Classify**, first match deciding: ticket cost; ability word (CR 207.2c);
  rules-meaningful and KEPT (keyword, CR label form, chapter symbol, number,
  symbol-bearing, anchor word); otherwise flavor label (the card's own name,
  `~`, included). Ticket cost, ability word and flavor label are IGNORED.
- **Effect of an IGNORED label.** The scope starts at the first token after its
  ` — `. A legacy head inside the label starts no region and is reported per
  clause. R1's scope start, and the cost-colon and condition-trigger marks R1
  reads, are read from there. The frozen detector is not edited.
- **CR read.** Only through `experiments/foundry_cr.py`, and only to classify a
  label. Every completeness check of §I3a is implemented and rigged to STOP on
  a tampered CR. The counts read from the CR equal §I3a's: **61 ability words,
  264 keyword titles, 22 CR label forms**.

Two readings in the implementation, recorded for the reviewer:

- **The 22 CR label forms.** The CR's numbered rules print 21 quoted forms
  `“<form> — [` other than `“[Anchor word] — [` (CR 614.12c). That form is
  wholly one placeholder; it is counted (22) and realised by the anchor-word
  class, read from the card's own text, never as a wildcard over every label.
- **A list of numbers** includes the separators `, `, ` or ` and `, or ` (die
  rows printed `1 or 2`). This is the reading that gives §I3a's corpus figures
  (number 15, flavor 625; see below).

## R4 labels on C03's sets

Seven clauses of C03's sets open with a label; all seven labels are IGNORED
and none is KEPT.

| address | census key | set | label | class | CR | effect | heads dropped | M04 |
|---|---|---|---|---|---|---|---|---|
| `0988d2cd-4e1d-47c6-b0db-0ff0335b12e6:0:2:0` | (exile, 0) | population | `Flurry` | ability word | CR 207.2c | ignored | none | FS-2 |
| `b095526e-94a4-416b-83de-d6271804ccf3:0:0:0` | (exile, 0) | population | `Converge` | ability word | CR 207.2c | ignored | none | FS-2 |
| `60a69ddc-3289-4786-944d-27a82c5f0dc8:0:0:0` | (exile, 0) | population | `{TK}{TK}` | ticket cost | CR 107.17a / 123.3c | ignored | none | FS-2 |
| `09ef446c-a13d-49d9-a94c-cd5f5a2d440b:0:0:0` | (exile, 0) | population | `Avoidance` | flavor label | CR 207.2d | ignored | none | FS-2 |
| `9ad12c75-e97d-404a-bfa9-26ff1d0bb506:0:0:0` | (exile, 0) | population | `Protection Fighting Style` | flavor label | CR 207.2d | ignored | none | FS-2 |
| `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:0:0` | none | fixture (prior-set-complement-reference) | `Search the Room` | flavor label | CR 207.2d | ignored | `search` @0 | FS-1 |
| `2cb98ca9-d7bb-416b-a17e-ee5f8e4d78f2:0:0:0` | (exile, 0) | population | `Converge` | ability word | CR 207.2c | ignored | none | — |

The six clauses §I3a names carry exactly the class §I3a states (checked in the
build; a different class halts). `2cb98ca9…:0:0:0` is a labelled clause §I3a
does not name: its ability-word label is ignored, the census clause already
starts past it, the label holds no head and no trigger opens the scope, so R4
changes nothing there (no region, mark, attachment or outcome).

## BEFORE / AFTER: everything R4 changed

Interface/2 value -> interface/3 value; rule R4 in every row.

**Regions, heads, marks and attachments**

| clause | M04 row | what | interface/2 | interface/3 |
|---|---|---|---|---|
| `0988d2cd…:0:2:0` | FS-2 | condition-trigger mark | none | [9, 54), R1 condition-trigger, attached once, to the ability |
| `b095526e…:0:0:0` | FS-2 | condition-trigger mark | none | [11, 36), R1 condition-trigger, attached once, to the ability |
| `60a69ddc…:0:0:0` | FS-2 | condition-trigger mark | none | [11, 65), R1 condition-trigger, attached once, to the ability |
| `09ef446c…:0:0:0` | FS-2 | condition-trigger mark | none | [12, 49), R1 condition-trigger, attached once, to the ability |
| `9ad12c75…:0:0:0` | FS-2 | condition-trigger mark | none | [28, 53), R1 condition-trigger, attached once, to the ability |
| `19b229c4…:0:0:0` | FS-1 | scope | [0, 37) | [18, 37) |
| `19b229c4…:0:0:0` | FS-1 | regions | region 0 headed `search`, [0, 36) | none (the head `search` lies in the label; the die roll has no legacy head) |
| `19b229c4…:0:0:0` | FS-1 | cost-colon mark | [0, 24), attached to region 0 (`attach-contained`) | [18, 24), no_region |

On the five FS-2 clauses the census scope already started past the label, so
their regions and heads are unchanged; only the trigger condition is now
marked.

**Kill-test outcomes**

| clause | M04 row | condition | interface/2 | interface/3 |
|---|---|---|---|---|
| `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:0:0` | FS-1 | K4 | PASS (relevant) | UNRESOLVED (relevant) |
| `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:0:0` | FS-1 | K6 | PASS (relevant) | UNRESOLVED (relevant) |
| `b095526e-94a4-416b-83de-d6271804ccf3:0:0:0` | FS-2 | K4 | PASS (not relevant) | PASS (relevant: ATTACH-3 now asks about its trigger span) |

No other clause's outcome or relevance differs from interface/2.

- **FS-1 `19b229c4…:0:0:0`.** M04 discounted its K4 PASS (it rested on a
  region the cost lay inside). Under R4 its cost span has no region, which I3
  classes as UNRESOLVED, matching M04's audited reading. K6 follows from that
  same span. K7 stays PASS: the clause now has no region whose boundary could
  be guessed. The second FS-1 clause, `c259e16f-2a44-4552-8678-815f757a02e8:0:0:0`
  (a `to activate` purpose phrase), prints no label; R4 does not reach it, and
  its interface/2 outcomes stand.
- **FS-2, the four two-region clauses.** K4 stays PASS, but the PASS now
  covers the trigger condition as well as the destination: the trigger is
  marked at the scope start after the label and attaches once, to the ability
  (R1), as Captain decision 5925134485 ruled. M04's audited UNRESOLVED (an
  unextracted span) no longer applies, and the latent `multiple` attachment
  M04 described does not arise.
- **FS-2 `b095526e…:0:0:0`.** Its trigger span is now extracted, so ATTACH-3
  applies and K4 becomes relevant; it PASSes.

## Per-rule reach (the population and the fixtures)

| rule | population clauses | fixture clauses |
|---|---|---|
| R1 `attach-ability-prefix` | 27 | 3 |
| R2 `head-not-payment-cast` | 3 | 0 |
| R3 `group-back-reference` | 1 | 0 |
| R4 `ability-label` (IGNORED label) | 6 | 1 |

R1-R3 reach is computed on the R4-off view and is interface/2's, clause for
clause.

- **R1 population (27 clauses, 28 spans).** By shape: cost-colon 11,
  condition-trigger 16, intervening condition-marker 1. These are the 27 R1
  rows of the change table below.
- **R1 fixtures (3).** `008d5896-6fc9-4aaa-8c6f-a44c2feb98bb:0:1:0`,
  `00af96af-5eae-4044-a2f7-a08cd0699d1e:0:0:0`,
  `c259e16f-2a44-4552-8678-815f757a02e8:0:2:0`. One fixture prefix span has no
  R1 shape (`eccc9a54…:0:0:0`, a condition) and keeps its outcome (attached).
- **R2 (3 population).** `16da72a3-d980-4dd8-99f2-8191cce00978:0:0:0` `cast`
  @78; `2cb98ca9-d7bb-416b-a17e-ee5f8e4d78f2:0:0:0` `cast` @123;
  `b095526e-94a4-416b-83de-d6271804ccf3:0:0:0` `cast` @166.
- **R3 (1 population).** `bac0fcee-9c1a-46b7-86c8-ffbfcc1e96de:0:0:0`:
  K3 UNRESOLVED for that relation, never PASS.
- **R4 population (6).** Ability word 3: `0988d2cd…:0:2:0`, `2cb98ca9…:0:0:0`,
  `b095526e…:0:0:0`. Ticket cost 1: `60a69ddc…:0:0:0`. Flavor label 2:
  `09ef446c…:0:0:0`, `9ad12c75…:0:0:0`.
- **R4 fixtures (1).** Flavor label: `19b229c4…:0:0:0`.
- **R4 KEPT labels.** None on C03's sets.

Under the R4-on view, R1 additionally attaches the five FS-2 trigger spans
(population condition spans attached with R1: 17 -> 22). That is R4's change,
reported above; it is not counted in R1's interface/1-to-interface/2 reach.

### Corpus-wide reach (cited, not re-measured)

- **R1-R3** (Captain decision 5900431196, as the interface/2 result cites it):
  32,557 cards / 74,106 clauses, 0 halts; R1 892 clauses / 877 cards; R2 244
  clauses / 221 cards; R3 1 clause. All 32 interface/1 kills fall inside that
  reach.
- **R4** (INTERFACES.md §I3a reach report, measured 2026-10-01): 32,557 cards,
  74,106 clauses, 0 halts; 61 ability words, 264 keyword titles and 22 CR
  label forms read from the CR; 3,105 clauses open with a label.

| class | clauses | effect |
|---|---|---|
| ability word | 1,356 | ignored |
| ticket cost | 192 | ignored |
| flavor label | 625 | ignored |
| keyword (title, list or parameter) | 221 | kept |
| chapter symbol | 576 | kept |
| symbol-bearing | 66 | kept |
| anchor word | 29 | kept |
| CR label form | 25 | kept |
| number / die-result row | 15 | kept |

Labels are ignored on 2,173 clauses (1,892 cards) and kept on 932 (§I3a).

**Observation for the reviewer (not a re-measurement, recorded in the
C03-REGIONS Worker evidence).** A private corpus check during C03-REGIONS,
written to no artifact, agreed with every IGNORED figure (1,356 / 192 / 625;
2,173 clauses on 1,892 cards) and with the keyword, chapter and symbol-bearing
figures. It counted 3,099 labelled clauses, not 3,105. The six it did not
count are all KEPT: 5 villainous-choice CR label forms and 1 anchor word, each
on a chain clause of ordinal 1 or 2. The commanded rule ("only a chain clause
with clause ordinal 0 can open with a label") excludes them. Being KEPT, they
cannot change any outcome either way.

## The 32 interface/1 kills under interface/2 (R4-off view, unchanged)

Computed on the R4-off view and equal to the accepted interface/2 table. Every
row was relevant under interface/1 and stays relevant; R4 changes none of
these rows.

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

Totals: K3 3 (2 R2, 1 R3), K4 29 (27 R1, 2 R2).

## Measurements (C03-REGIONS (c), R4-on view)

| measurement | population (66) | fixtures (29) | all (94) |
|---|---|---|---|
| regions | 130 | 11 | 139 |
| regions per clause | {1: 3, 2: 62, 3: 1} | {0: 20, 1: 7, 2: 2} | {0: 20, 1: 10, 2: 63, 3: 1} |
| crossing clause / paragraph / face | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| overlap pairs / nesting pairs | 0 / 0 | 0 / 0 | 0 / 0 |
| clauses with a repeated operation | 1 | 0 | 1 |
| legacy vs corrected detector differing | 0 | 1 | 1 |

"All" is 94 rather than 95 because one fixture clause is also a population
clause.

- **Change from interface/2.** The fixtures drop from 12 to 11 regions and
  fixture clauses without a region rise from 19 to 20: the FS-1 clause's
  `search` region. The population is unchanged at 130.
- **Zeros by construction.** Crossing, overlap and nesting are 0 by
  construction, as before.
- **Repeated operation.** `bf20bc37-3205-45af-a3be-05d6835c0d87:0:0:0`
  (destroy + destroy).
- **Detector difference.** `c4212ba4-8c43-40ca-aa36-b3b535659fa8:0:2:0`, a
  CR 700.2 mode bullet. Reported only; the corrected detector is never
  substituted. R2 and R4 drops are reported separately above.

**ATTACH-3 attachment.** "R1" is the part of "attached" that is one
attachment to the ability.

| category | population spans | attached | of which R1 | multiple | none | no region |
|---|---|---|---|---|---|---|
| cost | 11 | 11 | 11 | 0 | 0 | 0 |
| condition | 24 | 24 | 22 | 0 | 0 | 0 |
| duration | 1 | 1 | 0 | 0 | 0 | 0 |
| destination | 53 | 53 | 0 | 0 | 0 | 0 |

| category | fixture spans | attached | of which R1 | multiple | none | no region |
|---|---|---|---|---|---|---|
| cost | 2 | 1 | 1 | 0 | 0 | 1 |
| condition | 10 | 4 | 2 | 0 | 0 | 6 |
| duration | 1 | 1 | 0 | 0 | 0 | 0 |
| destination | 7 | 1 | 0 | 0 | 0 | 6 |

Against interface/2: population condition spans 19 -> 24 (the five FS-2
trigger spans, each attached once under R1); fixture cost attached 2 -> 1 and
no region 0 -> 1 (FS-1).

**COST-region precedent (AQ4 register #27), cited and not re-measured.** 113
COST regions on the frozen 782-occurrence open surface: 84 CR 113.3b/602.1a,
27 CR 606.2, 2 CR 702.6b. 0 cross a clause, paragraph or face boundary; 0 are
ambiguous; the maximum span is 58 characters.

## Kill tests (interface/3 I3)

Each test ran on every population clause (66) and every fixture clause (29),
94 distinct clauses. Distinct required operations and relevance come from
independent evidence and the consumer questions (ATTACH-1, ATTACH-3, C2) and
FIXTURES roles, never from a detector alone. Fixtures are always relevant.

| condition | all: PASS / UNRESOLVED / KILL | relevant | relevant: PASS / UNRESOLVED / KILL |
|---|---|---|---|
| K1 | 56 / 38 / 0 | 82 | 56 / 26 / 0 |
| K2 | 56 / 38 / 0 | 82 | 56 / 26 / 0 |
| K3 | 76 / 18 / 0 | 92 | 74 / 18 / 0 |
| K4 | 84 / 10 / 0 | 89 | 79 / 10 / 0 |
| K5 | 94 / 0 / 0 | 29 | 29 / 0 / 0 |
| K6 | 83 / 11 / 0 | 94 | 83 / 11 / 0 |
| K7 | 94 / 0 / 0 | 94 | 94 / 0 / 0 |

### KILL

None, on any clause.

### UNRESOLVED (findings for M04, not verdicts)

**K1 / K2.** Unchanged from interface/2: the 26 relevant UNRESOLVED are
fixture clauses where no independent evidence establishes two distinct
required operations; the 12 irrelevant population UNRESOLVED have no evidence
either.

**K3 (18, all relevant).** Unchanged from interface/2:

- `008d5896-6fc9-4aaa-8c6f-a44c2feb98bb:0:1:0` (exile, 0) · `008d5896…:0:1:1`
- `1167fe30-32b8-4381-8067-a05cd345977b:0:1:1`
- `16da72a3-d980-4dd8-99f2-8191cce00978:0:0:0` (R2)
- `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:2:1`
- `2cb98ca9-d7bb-416b-a17e-ee5f8e4d78f2:0:0:0` (R2)
- `766c644c-04fe-4b01-93dd-09a50d78d01f:0:0:0` · `766c644c…:0:1:0`
- `bac0fcee-9c1a-46b7-86c8-ffbfcc1e96de:0:0:0` (R3)
- `c259e16f-2a44-4552-8678-815f757a02e8:0:0:0` · `c259e16f…:0:1:0` · `c259e16f…:0:2:1`
- `eae87919-6322-4bd2-ae9c-b1ce25d686da:0:0:0` · `eae87919…:0:0:1` · `eae87919…:0:0:2`
- `eccc9a54-2b56-4a02-9926-258d5b2e25fb:0:0:0` · `eccc9a54…:0:0:1`
- `fd09875f-71a1-41c2-b404-ff58f4d4cb6c:0:1:0` (exile, 0)

**K4 (10, all fixture clauses).** An ATTACH-3 span sits in a clause with no
region. Interface/2's nine plus the FS-1 clause (R4):

- `1167fe30…:0:1:1`
- `19b229c4…:0:0:0` (R4, FS-1)
- `19b229c4…:0:2:1`
- `766c644c…:0:0:0`
- `c259e16f…:0:2:1`
- `c4212ba4-8c43-40ca-aa36-b3b535659fa8:0:0:0`
- `eae87919…:0:0:0` · `eae87919…:0:0:1` · `eae87919…:0:0:2`
- `eccc9a54…:0:0:1`

**K6 (11, all fixture clauses).** The ten K4 UNRESOLVED clauses plus
`008d5896…:0:0:0`.

**K5 and K7.** No UNRESOLVED; K7 has no UNRESOLVED outcome.

## Negative controls

KILLs on these rigged inputs are expected and are not kills.

**`regions.json` records 17 controls, all firing:** the nine of interface/2
(the card-keyed-variant control now covers R1, R2, R3 and R4), plus eight for
R4:

- A tampered CR STOPs the derivation for each completeness check: the 207.2c
  sentence missing, or not re-joining its source; a gap in the 701 or 702
  heading sequence; a CR 107 inventory missing `{TK}`; the label forms missing
  "to solve".
- A flavor label holding a frozen effect head starts no region from that head,
  and the dropped head is reported.
- An ability-word or flavor label before "Whenever …, exile …, then return it"
  yields a condition-trigger mark at the new scope start that R1 attaches once,
  to the ability; the same clause with a KEPT keyword label keeps its
  interface/2 outcome.
- An end-of-line "Choose one —" and labels holding `.` or `:` are no label.
- A label the card's own text names elsewhere is KEPT (anchor word); the same
  label not named elsewhere, and a label equal to the card's own name, are
  flavor labels.
- The classification order holds on labels that match two classes.
- An R4-on change on an unlabelled clause, and on a KEPT-label clause, each
  STOP (R4 IS CONFINED).
- A CR read whose ability-word, keyword-title or label-form count differs from
  61 / 264 / 22 STOPs.

**`kill.json` records 29 controls plus 2 record controls, all firing:** the 26
of interface/2, plus K7 KILL for a card-keyed R4 table entry; a clause whose
K4 outcome R4 changes records its interface/2 outcome beside the interface/3
one, with rule R4; and an R4-on change on an unlabelled and on a KEPT-label
clause each STOP (record and K1-K7 outcomes). On the real records, a rigged
R4-off figure STOPs, and R4-on marks fed into the R1-R3 records change them
and are caught by the reconciliation.

## Tests

`tests/oracle_ingest/test_h_region.py` (landed at `9f2160f`) runs 243 tests,
all green: interface/2's tests, R4 tests on inline synthetic clauses (every
label class and the classification order, the no-label shapes, the scope move
and dropped label heads, R1 read after an ignored label, KEPT labels keeping
the interface/2 outcome, each CR completeness STOP), and regression cases
named only by address and read from the pinned corpus at run time: the five
FS-2 clauses, the FS-1 clause, the Captain's R4 test card
(`867b3923-692c-4444-a071-518a290e43d8`, modes `:0:1:0`, `:0:2:0`, `:0:3:0`
flavor and ignored; `:0:0:0`, `:0:0:1` unlabelled and unchanged), one KEPT
case per kept class, and one further ticket-cost case. Every one classifies as
the command states.

Existing tests changed, because the interface/3 pin or R4 itself changes what
they assert:

1. `Guards.test_the_interface_pin_is_interface_2` became
   `test_the_interface_pin_is_interface_3`: it asserts interface/3, blob
   `119778a6…`, and that the kill module carries the same pin.
2. `Checks.test_the_scripts_own_negative_controls_all_fire` asserts 29 kill
   controls instead of 26 (the three R4 controls above).

No other existing test changed.
