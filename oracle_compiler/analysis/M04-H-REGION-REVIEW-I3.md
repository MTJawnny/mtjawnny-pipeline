# M04 — H-REGION semantic review of the interface/3 C03 re-run

**Wave:** `C03-M04R3.ORACLE-COMPILER-H-REGION-SEMANTIC-REVIEW-I3`, unit
M04-REVIEW-I3 (Issue #1 checkpoint 5939255367, task 5938514142; plan
5938516768).

**Base and interface:**

- Base (accepted head): `c392ef9e7bcee45e2dc8a51dbd4e5d94f18c8cb7`. Written on
  top of `9d164fc` (C03B-TRACE-I3) and `54adcca` (M04-CHECK-I3).
- Interface: `oracle-compiler-interface/3`, `oracle_compiler/INTERFACES.md`
  blob `119778a68c0e4e8378f0a117b7c22884ec5eda4b` (Captain ratification
  5925134485 + 5925371124). This was checked with
  `git rev-parse HEAD:oracle_compiler/INTERFACES.md`.
- The interface/2 review, `oracle_compiler/analysis/M04-H-REGION-REVIEW.md`
  (blob `52630e924ae730af0cd696dab06daa5ef3f94e42`), stays on record
  untouched. It is cited below as **I2** (for example "I2 §3 FS-4").

**Status:** This file is on the Manager surface (OWNERSHIP.md). It was written
by the executing model (Claude). Under the Captain approval this plan cites, it
becomes the M04 result only after cross-review by the other model. It is
analysis, not a selector, and it ratifies nothing.

**Conventions:**

- The only Oracle text here is R4 label text. Each label is written as the
  canonical chain text prints it, as INTERFACES.md does. A label that is the
  card's own name would be written `~`; none of the seven labels is.
- No card is named as a card. Clauses are named by their four-coordinate
  address `<oracle_id>:<face>:<paragraph>:<clause>`, plus their census key
  where one exists.
- Other quoted words are generic structural tokens: effect heads,
  connectors, trigger words and reference markers.

## 1. Inputs, verified

Every artifact was obtained under the hand-off rule. Each existing artifact
passed its producer's `--verify` (`h_region.py`, `h_region_kill.py`,
`c03_trace.py`), and nothing was regenerated. `c03_trace.py --check-complete`
also passed:

- 94 traces, one per C03 clause, and 10 fixtures;
- per-outcome counts equal to kill.json's;
- 7 R4 labels and 13 R4-changed values, each in exactly one trace.

`experiments/oracle_ingest/m04_check.py` checks this document against the
same verified bytes. The same run also confirms, per clause, that kill.json's
R4-off K1-K7 outcomes (the interface/2 derivation) equal that clause's row in
the I2 §6 coverage ledger, read only at its blob on record.

| artifact | sha256 |
|---|---|
| `experiments/out/oracle_ingest/c03/regions.json` | `95b680b1a9d36d7243c4cc90e30ebc4fbc9fd86b63d25290604eb89153f90f8a` |
| `experiments/out/oracle_ingest/c03/kill.json` | `fdb3a2d756b3e5d574cdfa313cf043dbee534a64197967b091afa2daf619a0f2` |
| `experiments/out/oracle_ingest/c03b/trace.json` | `437be9ba4bde87adf89908490e37e3096e7556830a3eda3fe06672ccb6d7b1c1` |

## 2. Method: every clause, not a sample

The review covers 94 C03 clause records: 66 population clauses and 29 fixture
clauses, one of which is also a population clause. It also covers all 10
fixtures.

Each clause falls into exactly one of two groups. kill.json decides which.

1. **R4 clauses (7): re-audited in full.** These are the clauses for which
   kill.json holds an R4 record (an R4 label; for 3 of them, changed
   outcomes too). Six are population clauses and one is a fixture clause.
   For each, the C03b trace was read against its own source line, the
   frozen chain clause carried only in the ignored trace.json. I2's six
   questions were asked again from scratch:
   1. regions and their heads;
   2. missed operations;
   3. ATTACH-3 marks and their attachment;
   4. K3 relation endpoints;
   5. every PASS (false success, V1 §11);
   6. every UNRESOLVED.

   The R4 label, every value R4 changed and its interface/2 value were also
   read against the source.
2. **All other clauses (87): carried forward by citation.** Each carried
   clause meets both conditions:
   - kill.json holds no R4 record for it: no label, and no interface/2
     change;
   - `m04_check.py` confirms that its R4-off outcomes equal its I2 ledger
     row.

   Interface/3's "R4 IS CONFINED" check (kill.json `r4_confined`) further
   guarantees that its interface/3 record and outcomes equal its R4-off ones.
   Its source, regions, marks and outcomes are therefore those I2 audited,
   and its I2 audit verdict is carried with the prefix "carried (I2 §6)".

I2's two deterministic scans were re-run over all 94 source lines under
interface/3:

- **Em-dash labels.** Seven source lines print an em-dash label, and every
  one carries an R4 label in its trace. No label is left unread.
- **Trigger words.** Every printed `When`, `Whenever` and `At the beginning`
  lies inside a condition mark, except one: a trigger inside the quoted
  created ability of `b9432430…:0:0:0`, which the frozen P4 rule excludes
  (I2 FS-3, unchanged).

No mark in any trace attaches to more than one region except as one R1
attachment to the ability. Every mark that attaches to no region is a D2 or
D7 clause (§6).

## 3. R4 section

R4 (`ability-label`, INTERFACES.md §I3a) found one label on each of seven
clauses. All seven labels are IGNORED, and none is KEPT. The offsets are
character offsets into the chain clause.

| clause | label | class | CR | effect | scope from | heads dropped | R4 changed |
|---|---|---|---|---|---|---|---|
| `0988d2cd-4e1d-47c6-b0db-0ff0335b12e6:0:2:0` | `Flurry` [0, 6) | ability word | CR 207.2c | ignored | 9 | none | role marks |
| `09ef446c-a13d-49d9-a94c-cd5f5a2d440b:0:0:0` | `Avoidance` [0, 9) | flavor label | CR 207.2d | ignored | 12 | none | role marks |
| `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:0:0` | `Search the Room` [0, 15) | flavor label | CR 207.2d | ignored | 18 | `search` at 0 | scope, heads, regions, role marks, K4, K6 |
| `2cb98ca9-d7bb-416b-a17e-ee5f8e4d78f2:0:0:0` | `Converge` [0, 8) | ability word | CR 207.2c | ignored | 11 | none | nothing |
| `60a69ddc-3289-4786-944d-27a82c5f0dc8:0:0:0` | `{TK}{TK}` [0, 8) | ticket cost | CR 107.17a / 123.3c | ignored | 11 | none | role marks |
| `9ad12c75-e97d-404a-bfa9-26ff1d0bb506:0:0:0` | `Protection Fighting Style` [0, 25) | flavor label | CR 207.2d | ignored | 28 | none | role marks |
| `b095526e-94a4-416b-83de-d6271804ccf3:0:0:0` | `Converge` [0, 8) | ability word | CR 207.2c | ignored | 11 | none | role marks, K4 relevance |

This is the reach INTERFACES.md's R4 reach report states: the five FS-2
population clauses and the FS-1 fixture clause. The seventh,
`2cb98ca9…:0:0:0`, is also reached, but R4 changes nothing on it. Its census
scope already began at its first head (offset 11) under interface/2, so moving
the scope start past the label leaves the same scope, regions and marks. It
was re-audited all the same (§4.1), because kill.json records its label.

The table below is the one `m04_check.py` requires: one row per (clause, item)
R4 changed, with the interface/2 value beside the interface/3 one, each
written as `c03_trace.py` renders it. All 13 rows belong to clauses with an
IGNORED label.

| clause | item | interface/2 | interface/3 | rule |
|---|---|---|---|---|
| `0988d2cd-4e1d-47c6-b0db-0ff0335b12e6:0:2:0` | mark condition [9, 54) | `none` | `condition [9, 54)  condition-trigger -> attached [0, 1] (attach-ability-prefix) (R1 condition-trigger, to the ability)` | R4 |
| `09ef446c-a13d-49d9-a94c-cd5f5a2d440b:0:0:0` | mark condition [12, 49) | `none` | `condition [12, 49)  condition-trigger -> attached [0, 1] (attach-ability-prefix) (R1 condition-trigger, to the ability)` | R4 |
| `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:0:0` | scope | `[0, 37]` | `[18, 37]` | R4 |
| `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:0:0` | heads_region | `[{"connector": 0, "end": 6, "head": "search", "start": 0}]` | `[]` | R4 |
| `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:0:0` | r4_dropped_heads | `[]` | `[{"connector": 0, "end": 6, "head": "search", "start": 0}]` | R4 |
| `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:0:0` | region search [0, 6) | `region 0 search  head [0, 6)  span [0, 36)  region-start-head .. region-end-scope` | `none` | R4 |
| `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:0:0` | mark cost [18, 24) | `cost [0, 24)  cost-colon -> attached [0] (attach-contained)` | `cost [18, 24)  cost-colon -> no_region []` | R4 |
| `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:0:0` | K4 | `PASS` | `UNRESOLVED` | R4 |
| `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:0:0` | K6 | `PASS` | `UNRESOLVED` | R4 |
| `60a69ddc-3289-4786-944d-27a82c5f0dc8:0:0:0` | mark condition [11, 65) | `none` | `condition [11, 65)  condition-trigger -> attached [0, 1] (attach-ability-prefix) (R1 condition-trigger, to the ability)` | R4 |
| `9ad12c75-e97d-404a-bfa9-26ff1d0bb506:0:0:0` | mark condition [28, 53) | `none` | `condition [28, 53)  condition-trigger -> attached [0, 1] (attach-ability-prefix) (R1 condition-trigger, to the ability)` | R4 |
| `b095526e-94a4-416b-83de-d6271804ccf3:0:0:0` | mark condition [11, 36) | `none` | `condition [11, 36)  condition-trigger -> attached [0] (attach-ability-prefix) (R1 condition-trigger, to the ability)` | R4 |
| `b095526e-94a4-416b-83de-d6271804ccf3:0:0:0` | K4 | `PASS (not relevant)` | `PASS` | R4 |

What the rows mean:

- **Five FS-2 clauses (one row each, `mark condition`).** Under interface/2
  the trigger condition after the label had no mark at all (I2 FS-2).
  Interface/3 reads the scope start after the label, so the trigger opens the
  scope. It is marked as `condition-trigger` and attached under R1 to every
  region of its ability: one attachment, to the ability. K4's outcome is
  unchanged (PASS) on the four two-region clauses. On `b095526e…` the new mark
  is the clause's only ATTACH-3 span, so K4 becomes relevant (interface/2:
  PASS, not relevant; interface/3: PASS).
- **FS-1 fixture clause `19b229c4…:0:0:0` (seven rows).**
  - The `search` head inside the label no longer starts a region: it is
    reported as dropped (`r4_dropped_heads`). The scope starts after the
    label (`[0, 37]` becomes `[18, 37]`), and region 0 is gone.
  - The cost-colon mark now starts at the scope start and ends at the colon.
    No region remains for it to attach to (`no_region`).
  - K4 and K6 move from PASS to UNRESOLVED. §4.1 reads this outcome.

## 4. False-success audit (V1 §11)

The audit found **no false KILL and no hidden KILL under interface/3 I3's own
outcome table**, and no false PASS on any R4 clause. Interface/3 removes both
I2 false-PASS classes from R4's reach:

- FS-2 is resolved;
- FS-1's labelled fixture clause no longer rests a PASS on a label head.

FS-1's second clause, the "to activate" purpose phrase, is outside R4's reach.
It is unchanged and stays not credited (§4.3).

### 4.1 Re-done audit, per R4 clause (source versus trace)

- **`0988d2cd-4e1d-47c6-b0db-0ff0335b12e6:0:2:0`** (exile#0; `Flurry`, ability
  word)
  - Regions: two, `exile` then `return`, cut at the printed `then`. Each head
    is an operation of the source, and the source prints no other.
  - Marks:
    - the trigger condition (`Whenever` … comma) is now marked at the scope
      start and attached once, to the ability (R1 `condition-trigger`);
    - the destination attaches to the return region.
  - K3: the back-reference `it` in the return region names the exile
    region's target, and the `then` sequence names both regions.
  - All seven PASSes hold for I3's reasons. **Credited: A-BLINK.**
- **`09ef446c-a13d-49d9-a94c-cd5f5a2d440b:0:0:0`** (exile#0; `Avoidance`,
  flavor label)
  - Same shape: two regions cut at `then`, with a trigger condition marked and
    attached once, to the ability.
  - The destination attaches to the return region.
  - The back-reference `that card` names the exile target.
  - **Credited: A-BLINK.**
- **`60a69ddc-3289-4786-944d-27a82c5f0dc8:0:0:0`** (exile#0; `{TK}{TK}`, ticket
  cost)
  - Same shape.
  - The ticket cost is paid to put the sticker on an object, not to activate
    the ability (CR 107.17a, 123.3c), so ignoring it drops no cost of the
    ability. No ATTACH-3 cost is lost.
  - **Credited: A-BLINK.**
- **`9ad12c75-e97d-404a-bfa9-26ff1d0bb506:0:0:0`** (exile#0; `Protection
  Fighting Style`, flavor label)
  - Same shape, with a `When` trigger.
  - The label holds no rules word. The word "Protection" in it is a flavor
    name, not the keyword: a keyword label would be the CR 702 title alone,
    and R4's order classes this one as a flavor label. Nothing the ability
    does is dropped.
  - **Credited: A-BLINK.**
- **`b095526e-94a4-416b-83de-d6271804ccf3:0:0:0`** (exile#0; `Converge`, ability
  word)
  - One region (`exile`) runs to the clause scope.
  - The `spent to` + `cast` payment description inside its target qualifier
    starts no region (R2). The qualifier is a target restriction, not an
    ATTACH-3 condition.
  - The trigger condition is now marked and attached once, to the ability, so
    K4 is relevant and PASSes.
  - K1/K2 UNRESOLVED (not relevant) is D1, and K3 has no relation.
  - **Credited** (R2 drop); D1.
- **`2cb98ca9-d7bb-416b-a17e-ee5f8e4d78f2:0:0:0`** (exile#0; `Converge`, ability
  word)
  - R4 changes nothing: the scope, region, marks and outcomes are the
    interface/2 ones. These were re-read, not carried.
  - One `exile` region runs to the scope end. The `spent to` + `cast` head is
    discounted (R2).
  - The `if` condition-marker is a standalone condition, not an R1 shape. It
    lies inside the one region and attaches to it alone, so K4's PASS is
    honest.
  - K3's two relations name their endpoints, and the back-reference `its`
    lies in the same region: D3.
  - **Credited** (R2 drop; condition attached once); D1; D3 (K3).
- **`19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:0:0`** (fixture
  prior-set-complement-reference; `Search the Room`, flavor label).
  - The source after the label is an activated ability: an activation cost,
    its colon, then a die-roll instruction.
  - Interface/3 ignores the label, so the `search` token no longer starts a
    region. The trace derives **no region**: the die-roll instruction has no
    head in the frozen legacy detector, which may not be edited (I2).
  - The cost-colon span is extracted, starting at the scope start and ending
    at the colon (an R1 shape). It has no region to govern (`no_region`).
  - K4 and K6 are UNRESOLVED; K3 and K5 PASS with nothing to relate or
    overlap; K1/K2 UNRESOLVED is D1.
  - K7's PASS is now honest: no boundary rests on the label, and no region
    is guessed. It is credited, though vacuously.
  - **Not a KILL.** The span lacks a region because a head was missed, which
    is I3's general rule ("a head missed ... is UNRESOLVED ... never counted
    as a kill"). The representation can express the clause: one region at the
    die roll, with the cost attached once, to the ability, under R1's
    `cost-colon` shape.
  - **R4-F; D2 (K4, K6).** Flagged for the cross-reviewer (§9): a literal
    reading of K4's "or to none" could call an extracted span with no region
    a KILL. This review applies the same reading as I2's D7.

### 4.2 Carried audits (87 clauses)

Every other clause's I2 §3 audit verdict is carried forward unchanged under
the two conditions of §2, and the §6 ledger cites it row by row. That includes:

- A-BLINK, A-SEQ and A-NONE;
- FS-3 (`b9432430…:0:0:0`);
- FS-4 (`05e0a10d…:0:0:0`, `bf20bc37…:0:0:0`);
- FS-5 (`eccc9a54…:0:0:0`);
- FS-6 (the K3 PASSes);
- FS-1's second clause (`c259e16f…:0:0:0`).

### 4.3 Disposition of M04 findings FS-1 to FS-6 under interface/3

- **FS-1 — a region started by a token that is not an operation.**
  - *Labelled fixture clause (`19b229c4…:0:0:0`): resolved by R4 as a false
    PASS.* With `Search the Room` ignored, the fixture now derives no region
    from the label. The `search` head is reported dropped, and the cost is
    marked from the scope start to its colon.
  - **An extraction failure remains:** the die-roll instruction has no
    legacy head, so no region exists. K4 and K6 are UNRESOLVED (D2). The I2
    false PASSes on K4 and K7 are gone: K4 is now honestly UNRESOLVED and
    K7's PASS no longer rests on a label head.
  - *Purpose-phrase clause (`c259e16f…:0:0:0`): unchanged.* It holds no label
    and is outside R4's reach. The `activate` head inside the "to activate"
    purpose phrase still starts a region, and its K7 PASS stays not credited.
  - **Open Captain question (not decided here):** whether the purpose phrase
    "to activate" should get an R2-like discount. R2 stays literal until
    ruled.
- **FS-2 — a trigger condition behind a label: resolved.** Each of the five
  trigger conditions is now extracted, once, as a `condition-trigger` mark
  that starts at the scope start after the ignored label. Each is attached
  once, to the ability: to both regions as one R1 attachment on the four
  two-region clauses, and to the one region on `b095526e…`. The I2 latent
  `multiple` exposure did not arise. The audited K4 UNRESOLVED of I2 becomes a
  credited PASS on all five.
- **FS-3 — operations inside a quoted created ability.** Unchanged and
  credited (carried; outside R4 reach). It is the only printed trigger word
  outside a condition mark, as the P4 rule requires.
- **FS-4 — participants told apart within or across regions.** Unchanged and
  credited (carried). K2's kill arm is still shown only on rigged input.
- **FS-5 — a replacement whose choice is not a head.** Unchanged and credited
  (carried). The latent exposure is recorded as in I2; R4 does not bear on
  it.
- **FS-6 — K3's PASSes and their reach.** Unchanged (carried). The five FS-2
  clauses' K3 relations were re-read in §4.1 and are unchanged by R4.

## 5. Per-condition verdict against interface/3 I3 and I3a

The measured result for every condition is kill.json's. **Audited relevant
PASS** subtracts the PASSes this review does not credit. Every condition keeps
relevant PASS above zero, so none is flagged "PASS coverage insufficient"
under either count.

| condition | measured relevant PASS / UNRESOLVED / KILL | audited relevant PASS | verdict |
|---|---|---|---|
| K1 distinct ownership | 56 / 26 / 0 | 56 | not killed on the P2 population |
| K2 repeated operations | 56 / 26 / 0 | 56 | not killed on the P2 population |
| K3 relation endpoint | 74 / 18 / 0 | 74 | not killed on the P2 population |
| K4 qualifier attachment | 79 / 10 / 0 | 79 | not killed on the P2 population |
| K5 overlap / nesting | 29 / 0 / 0 | 29 | not killed on the P2 population |
| K6 stronger identity needed | 83 / 11 / 0 | 83 | not killed on the P2 population |
| K7 guesses or exceptions | 94 / 0 / 0 | 93 (FS-1: 1) | not killed on the P2 population |

**What changed from interface/2.**

- **K4.**
  - Relevant count rises 88 → 89: `b095526e…`'s new trigger mark makes ATTACH-3
    asked.
  - `19b229c4…:0:0:0` moves PASS → UNRESOLVED.
  - Measured relevant PASS stays 79. Audited relevant PASS rises 74 → 79,
    because the four FS-2 PASSes I2 did not credit are now credited, the
    fifth FS-2 clause adds a credited PASS, and FS-1's uncredited PASS is gone.
- **K6.** `19b229c4…:0:0:0` moves PASS → UNRESOLVED (D2), giving 84 → 83
  PASS.
- **K7.** The audited count rises 92 → 93: the labelled FS-1 clause's PASS is
  now credited.
- K1, K2, K3 and K5 are unchanged.

**Per condition under interface/3:**

- **K1, K2.**
  - All 56 relevant PASSes rest on independent evidence (I2 §4, carried). R4
    changes none of them.
  - K2's kill arm is still shown only on rigged input (FS-4).
- **K3.**
  - Every relevant UNRESOLVED is D2-D5, as under I2.
  - R3 applied once (`bac0fcee…`).
  - R4 changes no relation.
- **K4.**
  - R1 attaches every scope-start cost-colon and trigger once, to the
    ability, now including the five label-prefixed triggers (I3a: "the start
    of the clause's scope ... is read after any R4 label").
  - Every relevant UNRESOLVED is a span with no region because extraction
    failed (D2), or the modal header (D7).
  - No span attaches to more than one region except as one R1 attachment.
- **K5.** Every PASS is still vacuous: overlap and nesting are 0 by
  construction (I2 §4, carried).
- **K6.** Every UNRESOLVED is D2, D6 or D7, now including `19b229c4…:0:0:0`
  (D2).
- **K7.**
  - Every region uses a rule in the table, and every rule, R4 included, passes
    `assert_not_card_keyed`.
  - R4 reads only the CR and the card's own rules text, through
    `foundry_cr.py`.
  - One PASS stays not credited: FS-1's purpose phrase (`c259e16f…:0:0:0`),
    an extraction failure, not a guess.

**No relevant KILL** exists for any condition, measured or audited. No finding
needs a new identity coordinate.

## 6. Dispositions for every UNRESOLVED

The codes are I2 §5's, unchanged, and are cited here rather than repeated in
full.

| code | meaning | disposition |
|---|---|---|
| D1 | K1/K2 UNRESOLVED: no FIXTURES role or consumer question shows two distinct required operations | Prescribed by I3 ("never PASS, never KILL"). No action under this interface (I2 §5). |
| D2 | the clause prints an operation the frozen legacy detector does not extract, so no region exists, and its K3, K4 or K6 UNRESOLVED has no region to read | An extraction gap: V1 §10 Tier B, carried to M2/M3 extraction work. Not a kill (I2 §5). Interface/3 adds one clause: `19b229c4…:0:0:0`, whose die-roll instruction has no legacy head once R4 ignores the label (K4, K6). |
| D3 | a back-reference whose referent lies in the same region or an earlier clause | The endpoint is named; resolution is C04 reference work (I2 §5). |
| D4 | R3: a plural reference named as one printed list (`bac0fcee…`) | I3a R3: UNRESOLVED, never PASS (I2 §5). |
| D5 | a reference whose referent is outside every region, or for which no candidate span was extracted | Carried to C04. Not a kill (I2 §5). |
| D6 | a fixture keyword line whose role's operations are in its sibling clauses | C2 is answered by the sibling clauses. UNRESOLVED here is honest (I2 §5). |
| D7 | a modal header's trigger condition with no region in its clause (CR 700.2) | Cross-paragraph modal law, outside within-clause H-REGION. Read as I3's extraction/no-region class and flagged for the cross-reviewer (I2 §5, §8). |

Every ledger row with an UNRESOLVED names the D-code for each UNRESOLVED
condition it carries. Fixtures that have a member without a clause carry their
disposition in the fixture table.

## 7. Coverage ledger

Outcomes are kill.json's (interface/3), unedited. A row's disposition column
holds one of two things:

- for an R4 clause, its re-done audit verdict (§4.1). R4-A means FS-2
  resolved, R4-F means FS-1 resolved with an extraction gap left, and R4-0
  means the label was ignored and nothing changed;
- for every other clause, "carried (I2 §6):" followed by its I2 audit and
  disposition codes.

No disposition cell is a placeholder.

| clause | census key | population | fixtures | K1 | K2 | K3 | K4 | K5 | K6 | K7 | disposition |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `008d5896-6fc9-4aaa-8c6f-a44c2feb98bb:0:0:0` | none | no | delayed-return-same-object | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | UNRESOLVED | PASS | carried (I2 §6): A-NONE (keyword line); D1; D6 (K6) |
| `008d5896-6fc9-4aaa-8c6f-a44c2feb98bb:0:1:0` | exile#0 | no | delayed-return-same-object | PASS | PASS | UNRESOLVED | PASS | PASS | PASS | PASS | carried (I2 §6): credited (delayed-return pair; R1 trigger); D3 (K3) |
| `008d5896-6fc9-4aaa-8c6f-a44c2feb98bb:0:1:1` | none | no | delayed-return-same-object | PASS | PASS | UNRESOLVED | PASS | PASS | PASS | PASS | carried (I2 §6): credited (delayed-return pair); D3 (K3) |
| `00af96af-5eae-4044-a2f7-a08cd0699d1e:0:0:0` | destroy#0 | no | simple-one-operation-negative-control | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): credited (one-operation negative control; R1 trigger); D1 |
| `00b36996-43c6-42a5-892c-c7c8864cf973:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `01160cb5-6d83-4317-9522-74083b3a83bb:0:2:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `0214805d-d207-42da-a25f-2a8e1990904e:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `05e0a10d-532a-451c-a54e-27e64969fe0e:0:0:0` | destroy#0 | no | participant-role-choreography | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): FS-4 credited; D1 |
| `05e0a10d-532a-451c-a54e-27e64969fe0e:0:1:0` | none | no | participant-role-choreography | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-NONE (no legacy head); D1 |
| `094c4486-6cae-4268-850e-ff0082e5ad10:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `0988d2cd-4e1d-47c6-b0db-0ff0335b12e6:0:2:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | R4-A re-audited (FS-2 resolved: trigger attached once, to the ability); A-BLINK credited |
| `09ef446c-a13d-49d9-a94c-cd5f5a2d440b:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | R4-A re-audited (FS-2 resolved: trigger attached once, to the ability); A-BLINK credited |
| `0fd57894-b917-41c8-a394-360d1d31b236:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `1167fe30-32b8-4381-8067-a05cd345977b:0:0:0` | none | no | split-destination-selected-set | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-NONE; D1 |
| `1167fe30-32b8-4381-8067-a05cd345977b:0:1:0` | none | no | split-destination-selected-set | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-NONE; D1 |
| `1167fe30-32b8-4381-8067-a05cd345977b:0:1:1` | none | no | split-destination-selected-set | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | UNRESOLVED | PASS | carried (I2 §6): D1; D2 (K3, K4, K6) |
| `1225bee2-c829-4a93-9f75-3495277c23bc:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `142af8f1-6d6b-4043-8cc4-6632481972c1:0:0:0` | destroy#0 | yes | two-sequential-operations | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-SEQ credited (two-sequential-operations) |
| `14b839ef-80b1-4e7d-b2fd-38e973899cde:0:1:0` | destroy#0 | yes | none | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-SEQ credited (R1 trigger); D1 |
| `169705c3-32c1-4628-b108-c37ca5f27e24:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `16da72a3-d980-4dd8-99f2-8191cce00978:0:0:0` | destroy#0 | yes | none | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | carried (I2 §6): credited (R2 drop; condition attached once); D1; D3 (K3) |
| `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:0:0` | none | no | prior-set-complement-reference | UNRESOLVED | UNRESOLVED | PASS | UNRESOLVED | PASS | UNRESOLVED | PASS | R4-F re-audited (FS-1: label ignored, no region derived; K7 credited); D1; D2 (K4, K6) |
| `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:1:0` | none | no | prior-set-complement-reference | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-NONE; D1 |
| `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:2:0` | none | no | prior-set-complement-reference | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-NONE; D1 |
| `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:2:1` | none | no | prior-set-complement-reference | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | UNRESOLVED | PASS | carried (I2 §6): D1; D2 (K3, K4, K6) |
| `19ea326f-45ff-4bc0-a957-7d3f22dd8c6f:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `1aa1cf50-ee79-4bef-826b-5f1a9e1aa1a5:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `1ca97394-4e8c-4698-bea1-554f9b10927b:0:1:0` | exile#0 | yes | none | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-SEQ credited (R1 cost); D1 |
| `20194297-f2a4-4473-95bc-7c6835e5b6b3:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `29b537f5-4d9f-40ed-b38b-e8faa2b5af7d:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `2cb98ca9-d7bb-416b-a17e-ee5f8e4d78f2:0:0:0` | exile#0 | yes | none | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | R4-0 re-audited (label ignored, nothing changed); credited (R2 drop; condition attached once); D1; D3 (K3) |
| `2d72454f-3d87-4acc-9f46-b8c579f44af8:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `2debd9f1-6d3a-4f0a-8488-603447c44490:0:2:0` | exile#1 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `334e2147-5944-4558-b2bc-2f2bfb96dfa5:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `33869ba6-13e5-4e48-8963-92f7965648fb:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `38a55562-1e2d-4240-9454-219a4a25d38d:0:2:0` | destroy#0 | yes | none | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-SEQ credited (R1 cost); D1 |
| `3a30089d-cd2d-49be-9b06-7a2454117692:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `46f77c8c-6817-4aea-a80a-d91f508ccbd0:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `4b072fbb-5e61-4009-bcb1-d493eb4a1be4:0:1:1` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `57d02dc8-e22e-4874-9f02-490a2528a28f:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `58a55d14-b03b-4648-b168-ad35ff088b19:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `5c63a244-75d7-4372-baf4-7a3526f240c8:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `60a69ddc-3289-4786-944d-27a82c5f0dc8:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | R4-A re-audited (FS-2 resolved: trigger attached once, to the ability); A-BLINK credited |
| `64824ae5-efab-4b55-9d3c-b9c690bad857:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `6879f5ce-7a1b-4606-bad1-885779b0d456:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `6df57d67-2fd9-4e7a-b67b-f361fc30e496:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `766c644c-04fe-4b01-93dd-09a50d78d01f:0:0:0` | none | no | replacement-event-lineage | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | UNRESOLVED | PASS | carried (I2 §6): D1; D2 (K3, K4, K6) |
| `766c644c-04fe-4b01-93dd-09a50d78d01f:0:1:0` | none | no | replacement-event-lineage | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | carried (I2 §6): A-NONE (permission heads); D1; D5 (K3) |
| `788d3cfa-7706-4728-9c48-cf7bc963d002:1:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `7c4c556c-b5e3-493a-a7b0-38c55b7809ac:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `913e6182-706a-4872-8c8a-e146b0ae0738:0:1:0` | exile#0 | yes | none | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-SEQ credited (R1 trigger); D1 |
| `92019547-f6db-4ea6-8356-d0a90ace5662:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `97cf544e-ffbf-4730-8cd2-4f1d5be933f2:0:0:0` | exile#0 | yes | none | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-SEQ credited; D1 |
| `9ad12c75-e97d-404a-bfa9-26ff1d0bb506:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | R4-A re-audited (FS-2 resolved: trigger attached once, to the ability); A-BLINK credited |
| `9b1f552a-bddc-4fcb-ac67-b4a65b2f48ba:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `9f762b9f-7525-4ff8-bc1d-fbab66fd4013:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `a2a380d8-4df7-4357-862c-ed3fb795db6c:0:0:0` | destroy#0 | yes | none | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-SEQ credited; D1 |
| `a3ec6b5d-08ec-4ae0-b1db-c4b87a1849c7:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `a6a7bf77-0560-4572-a826-3bc9df1f78d1:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `a6b28298-9624-49d7-ad73-fcd1fd3556d2:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `a959a91a-3e1d-4bd4-9e14-5ee977540146:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `b095526e-94a4-416b-83de-d6271804ccf3:0:0:0` | exile#0 | yes | none | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | R4-A re-audited (FS-2 resolved: trigger attached once, to the ability; K4 now relevant, credited; R2 drop); D1 |
| `b11c250c-f191-4c52-ba02-a9176f163447:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `b1462c82-7702-451b-b612-990353a79ac4:0:2:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `b9432430-df01-497d-b025-7576dce830e4:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): FS-3 credited (quoted created ability) |
| `bac0fcee-9c1a-46b7-86c8-ffbfcc1e96de:0:0:0` | exile#0 | yes | none | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | carried (I2 §6): A-SEQ credited; D1; D4 (K3) |
| `bf20bc37-3205-45af-a3be-05d6835c0d87:0:0:0` | destroy#0 | yes | none | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): FS-4 credited (R1 cost); D1 |
| `c259e16f-2a44-4552-8678-815f757a02e8:0:0:0` | none | no | ability-borrowing-inheritance-pressure | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | carried (I2 §6): FS-1 (K7 PASS not credited); D1; D5 (K3) |
| `c259e16f-2a44-4552-8678-815f757a02e8:0:1:0` | none | no | ability-borrowing-inheritance-pressure | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | carried (I2 §6): D1; D2 (K3) |
| `c259e16f-2a44-4552-8678-815f757a02e8:0:2:0` | none | no | ability-borrowing-inheritance-pressure | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): credited (R1 cost-colon, one region); D1 |
| `c259e16f-2a44-4552-8678-815f757a02e8:0:2:1` | none | no | ability-borrowing-inheritance-pressure | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | UNRESOLVED | PASS | carried (I2 §6): D1; D2 (K3, K4, K6) |
| `c4212ba4-8c43-40ca-aa36-b3b535659fa8:0:0:0` | none | no | modal-regression-control | UNRESOLVED | UNRESOLVED | PASS | UNRESOLVED | PASS | UNRESOLVED | PASS | carried (I2 §6): D1; D7 (K4, K6) |
| `c4212ba4-8c43-40ca-aa36-b3b535659fa8:0:1:0` | none | no | modal-regression-control | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-NONE (no legacy head); D1 |
| `c4212ba4-8c43-40ca-aa36-b3b535659fa8:0:2:0` | none | no | modal-regression-control | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-NONE (legacy head missed; corrected detector differs); D1 |
| `c4212ba4-8c43-40ca-aa36-b3b535659fa8:0:3:0` | none | no | modal-regression-control | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-NONE (no legacy head); D1 |
| `c4d2fdf9-637d-4e97-ae33-45f2d27bf8cd:0:2:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `c786a0aa-d86f-42c3-a7ea-5cb6ab72b5ec:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `cd1eda60-53e4-44d0-9b2c-7a57395e291f:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `d5b9d250-92f5-40d8-b962-4ae4adb466c8:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `d6239ada-c72a-49b2-882c-6dae1dd366e3:0:0:0` | exile#0 | yes | none | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-SEQ credited; D1 |
| `dfbd3afc-9905-4cff-a4f4-df08a4d0a7fa:0:2:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `e1708ad9-35d4-4243-92ca-ddf9d129aa32:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `e71863a7-0de1-4ab5-95e8-c39e6810d899:1:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `e875b468-b475-4573-adf6-312ca4ab6994:0:0:1` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `eae87919-6322-4bd2-ae9c-b1ce25d686da:0:0:0` | none | no | replacement-event-lineage | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | UNRESOLVED | PASS | carried (I2 §6): D1; D2 (K3, K4, K6) |
| `eae87919-6322-4bd2-ae9c-b1ce25d686da:0:0:1` | none | no | replacement-event-lineage | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | UNRESOLVED | PASS | carried (I2 §6): D1; D2 (K3, K4, K6) |
| `eae87919-6322-4bd2-ae9c-b1ce25d686da:0:0:2` | none | no | replacement-event-lineage | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | UNRESOLVED | PASS | carried (I2 §6): D1; D2 (K3, K4, K6) |
| `eccc9a54-2b56-4a02-9926-258d5b2e25fb:0:0:0` | none | no | replacement-event-lineage | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | carried (I2 §6): FS-5 credited; D1; D3 (K3) |
| `eccc9a54-2b56-4a02-9926-258d5b2e25fb:0:0:1` | none | no | replacement-event-lineage | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | UNRESOLVED | PASS | carried (I2 §6): D1; D2 (K3, K4, K6) |
| `ef9a5bd1-6ce2-4570-9d42-89d997e2fc6f:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `f4a73cde-58bf-4719-8eb0-e039fdde4f62:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `f8a88521-80e5-419b-ab4e-f4b3aba8afa0:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `f96a2aa6-3259-4bb6-92cd-4d17215d04d0:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited |
| `fd09875f-71a1-41c2-b404-ff58f4d4cb6c:0:1:0` | exile#0 | yes | none | PASS | PASS | UNRESOLVED | PASS | PASS | PASS | PASS | carried (I2 §6): A-BLINK credited (R1 cost); D3 (K3) |

| fixture | member status | members | clauses | disposition |
|---|---|---|---|---|
| simple-one-operation-negative-control | F0_SELECTED | 1 | 1 | every member clause reviewed (ledger) |
| two-sequential-operations | F0_SELECTED | 1 | 1 | every member clause reviewed (ledger) |
| split-destination-selected-set | F0_SELECTED_PRODUCTION_FIXTURE | 1 | 3 | every member clause reviewed (ledger) |
| delayed-return-same-object | F0_SELECTED | 1 | 3 | every member clause reviewed (ledger) |
| prior-set-complement-reference | F0_SELECTED_PRODUCTION_FIXTURE | 1 | 4 | every member clause reviewed (ledger); clause 0:0:0 re-audited under R4 (FS-1) |
| conditional-second-operation | F0_REVIEWED_NULL | 0 | 0 | F0_REVIEWED_NULL: FIXTURES.json selects no member, so no clause exists to test; conditional coverage rests on the population condition-marker clauses (16da72a3…, 2cb98ca9…, c4d2fdf9…) |
| replacement-event-lineage | V1_NAMED_PRESSURE_SET | 4 | 7 | one of 4 members matches 0 cards by exact card or face name: recorded, not guessed (I2: no member may be added or swapped); the 7 clauses of its other 3 members are reviewed; a fixture-selection finding, not a C03 outcome |
| modal-regression-control | V1_NAMED_REGRESSION_EVIDENCE | 1 | 4 | every member clause reviewed (ledger) |
| participant-role-choreography | F0_SELECTED | 1 | 2 | every member clause reviewed (ledger) |
| ability-borrowing-inheritance-pressure | CAPTAIN_NAMED | 1 | 4 | every member clause reviewed (ledger) |

## 8. Totals and the H-REGION outcome

Outcome totals and PASS-coverage flags per condition are kill.json's, checked
by `m04_check.py`.

| condition | all PASS | all UNRESOLVED | all KILL | relevant | relevant PASS | relevant UNRESOLVED | relevant KILL | PASS coverage | result |
|---|---|---|---|---|---|---|---|---|---|
| K1 | 56 | 38 | 0 | 82 | 56 | 26 | 0 | sufficient | not killed on the P2 population |
| K2 | 56 | 38 | 0 | 82 | 56 | 26 | 0 | sufficient | not killed on the P2 population |
| K3 | 76 | 18 | 0 | 92 | 74 | 18 | 0 | sufficient | not killed on the P2 population |
| K4 | 84 | 10 | 0 | 89 | 79 | 10 | 0 | sufficient | not killed on the P2 population |
| K5 | 94 | 0 | 0 | 29 | 29 | 0 | 0 | sufficient | not killed on the P2 population |
| K6 | 83 | 11 | 0 | 94 | 83 | 11 | 0 | sufficient | not killed on the P2 population |
| K7 | 94 | 0 | 0 | 94 | 94 | 0 | 0 | sufficient | not killed on the P2 population |

H-REGION result: not killed on the P2 population

In interface/3's words, H-REGION is **not killed on the P2 population** for
any of K1-K7. It is never "confirmed": the population covers only three
object-lattice actions. No condition is flagged "PASS coverage insufficient",
so no condition needs a coverage disposition and none escalates the wave on
that ground. UNRESOLVED counts are findings for M04 and are disposed of above;
they are not verdicts.

## 9. Escalations, rulings and open questions

None of these changes the result.

1. **FS-2: ruled and now implemented.** Captain decision 5925134485, as
   implemented by interface/3 R4 (5925134485 + 5925371124). All five clauses
   are re-measured here, and every trigger is attached once, to the ability.
   Closed.
2. **FS-1 "to activate": open Captain question, not decided here.** Should a
   head that the frozen detector matches inside a purpose phrase ("spend mana
   ... to activate") get an R2-like discount? R2 stays literal until ruled.
   FS-1's labelled clause is resolved by R4 (§4.3). Its remaining die-roll
   extraction gap (D2) is Tier B extraction work, not a semantic-law
   question.
3. **For the cross-reviewer: an extracted span with no region.** This covers
   D7, the modal header, and now `19b229c4…:0:0:0`, whose cost-colon span is
   extracted but no region exists to attach it to. This review classes both
   as extraction or no-region (UNRESOLVED), under I3's rule that a missed head
   is never a kill. A literal reading of K4's "or to none" could call them
   KILLs. Should that reading be preferred, it is a Captain question, not a
   repair.
4. **Coverage notes, carried from I2.**
   - K5 is vacuously passed: no real overlap exists.
   - K2's kill arm has never met a real consumer-asked repeated operation
     (FS-4).

   Both are recorded so that "not killed" is not read as more than it is.

No real KILL was found. No condition has zero PASS. No finding needs a new
identity coordinate. Under the review boundary, the review itself does not
force a CAPTAIN answer. Item 2 is an open Captain question, and item 3 is a
classification for the cross-reviewer. Neither is a KILL or a "PASS coverage
insufficient" flag.
