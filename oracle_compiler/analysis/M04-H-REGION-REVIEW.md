# M04 — H-REGION semantic review of C03 (interface/2)

**Wave:** `C03-M04.ORACLE-COMPILER-H-REGION-SEMANTIC-REVIEW`, unit M04-REVIEW
(Issue #1 checkpoint 5925109625, task 5900504735; command r2, recovery
decision 5925109323, superseding the origin under checkpoint 5923449551).

**Base and interface:**

- Base (accepted head): `4ff172061c1699079b91a5577d7d2d376a6dd58f`.
- First written on top of `3e08bc9` (M04-CHECK) as `442ef34`. This r2
  revision is written on top of `4337753` (M04-CHECK r2), whose checker
  refuses a placeholder disposition (null/None, JSON null, none, a dash or
  em-dash, TBD/TODO, empty, any case).
- Interface: `oracle-compiler-interface/2`, `oracle_compiler/INTERFACES.md` blob
  `4ac4d856b651edde05b15c7065aa593f59561dcf` (Captain ratification
  5900431196). It was checked with
  `git rev-parse HEAD:oracle_compiler/INTERFACES.md`.

**Status:** This file is on the Manager surface (OWNERSHIP.md). It was written
by the executing model (Claude). Under the Captain approval this plan cites, it
becomes the M04 result only after cross-review by the other model. It is
analysis, not a selector, and it ratifies nothing.

**Conventions:**

- No Oracle text appears here.
- Clauses are named by their four-coordinate address
  `<oracle_id>:<face>:<paragraph>:<clause>`, plus their census key where one
  exists.
- Quoted words below are generic structural tokens: effect heads,
  connectors and reference markers.

## 1. Inputs, verified

Every artifact was obtained under the hand-off rule. Each existing artifact
passed its producer's `--verify` (`h_region.py`, `h_region_kill.py`,
`c03_trace.py`), and nothing was regenerated. `c03_trace.py --check-complete`
also passed: 94 traces, one per C03 clause, 10 fixtures, and per-outcome
counts equal to kill.json's. `experiments/oracle_ingest/m04_check.py` checks
this document against the same verified bytes.

| artifact | sha256 |
|---|---|
| `experiments/out/oracle_ingest/c03/regions.json` | `e68eae465b4ee905dde7f2f87cd8d5143542a306243416ed649040de6a0f9be2` |
| `experiments/out/oracle_ingest/c03/kill.json` | `8af3175fc745d72a37c02914bd69921fe403b6dd697c5cb9099ab96fc2535632` |
| `experiments/out/oracle_ingest/c03b/trace.json` | `47c80bd4db6f886fa8b030c1dc8b54d8332003cc23bcb6251f29af2d7b1b4e50` |

regions.json and kill.json are the same bytes that
`oracle_compiler/measurement/C03-H-REGION-RESULT-I2.md` cites.

## 2. Method: every clause, not a sample

The review covers 94 C03 clause records: 66 population clauses and 29 fixture
clauses, one of which is also a population clause. It also covers all 10
fixtures. For each record, the C03b trace was read against the trace's own
source line, which is the frozen chain clause carried only in the ignored
trace.json. Each record was checked against six questions:

1. **Regions.** Does each region start at a printed effect head and end at the
   printed connector before the next head, or at the clause scope? Is that head
   an operation of the source, or a non-operation token the frozen detector
   matched?
2. **Missed operations.** Does the source print an operation that no region
   carries? These are extraction gaps: Tier B, UNRESOLVED.
3. **ATTACH-3 marks.** Is every cost, condition, duration and destination
   span the source prints present as a mark? Is each mark's attachment the
   one the source's structure gives (CR 602.1a, 603.1, 603.4, 608.2c)?
4. **K3 relations.** For each relation, is the named endpoint the one the
   source means, and is the PASS or UNRESOLVED honest?
5. **PASS outcomes.** For every PASS, does the PASS hold for the reason
   I3/I3a gives, or only because something was not extracted? The second
   case is a **false success** (V1 §11).
6. **UNRESOLVED outcomes.** For every UNRESOLVED, is it an extraction or
   resolution failure (I3's UNRESOLVED column) rather than a kill hidden as
   one?

The same questions were also run as deterministic scans over all 94 source
lines:

- every printed trigger word (`When`, `Whenever`, `At the beginning`)
  against the condition marks;
- every em-dash label against the region heads.

Those scans found the FS-1 and FS-2 classes below.

The coverage ledger (§6) carries one row per clause. Its last column holds that
clause's audit verdict and, where any outcome is UNRESOLVED, its disposition.

## 3. False-success audit (V1 §11)

The audit found **no false KILL and no hidden KILL under I3's own outcome
table**. It found two classes of false PASS, FS-1 and FS-2. In both, C03
reports PASS where I3 classes the clause as an extraction failure, so the
honest outcome is UNRESOLVED. It also found four observations, FS-3 to FS-6,
that are correct under the interface but bound what each PASS proves.

The ledger keeps kill.json's measured outcomes, because the checker requires
it and this review edits no C03 producer. The audited reading is stated beside
them, and §4 discounts these PASSes.

### FS-1 — a region started by a token that is not an operation (2 fixture clauses)

- `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:0:0` (prior-set-complement-reference):
  - The frozen legacy detector matched `search` as a head. That word opens a
    label printed before an em dash. A flavor or ability word has no rules
    meaning (CR 207.2c, 207.2d).
  - Region 0 therefore runs from the label, through the activation cost and
    its colon, to the end of the effect.
  - The real instruction, a die roll, has no legacy head, and no region
    carries it.
  - The cost mark attaches to region 0 because it lies inside it
    (`attach-contained`), and not under R1's `cost-colon` shape. So K4's
    "attached to one region" PASS rests on a region that contains the
    cost.
  - K7's PASS holds only in form: the boundary is a printed token that the
    detector matched, but it is not a CR 608.2c instruction boundary.
- `c259e16f-2a44-4552-8678-815f757a02e8:0:0:0`
  (ability-borrowing-inheritance-pressure):
  - The legacy detector matched `activate` inside a "spend mana … to
    activate" purpose phrase, so a region starts there.
  - The phrase describes what mana may pay for (CR 106.1 and 602.2b). It is
    the activated-ability analogue of the `spent to cast` payment
    description that R2 discounts.
  - R2 is literal (only `spent to` + `cast`), so R2 does not apply. That is
    correct: R2 must not be widened in code.
  - No consumer question applies to this clause, so only K7's PASS rests on
    the region.

**Audited reading.** Both regions come from an extraction failure (a wrong
head), which is I3's UNRESOLVED class, not a representation the interface
cannot express. A correct region for the first clause would start at the die
roll, with the cost attached once to the ability under R1's `cost-colon` shape.
H-REGION can express that.

- These PASSes are **not credited**: K4 and K7 on the first clause, and K7 on
  the second.
- **Not a KILL:** this is a misidentified head, not a guessed span or a
  card-keyed rule (K7's KILL column).

**Escalation.** Whether the purpose phrase "to activate" should get an R2-like
rule is a semantic-law question for the Captain. This review does not propose
one.

### FS-2 — a trigger condition behind a label is never marked (5 population clauses)

`role_spans` marks `condition-trigger` only when the trigger word opens the
clause, or opens the text right after its first colon. When a label and an em
dash come first (an ability word, a flavor word or a symbol label, CR
207.2c/207.2d), the trigger condition gets no mark at all. These clauses are
affected:

| clause | census key | regions | measured K4 | audited K4 |
|---|---|---|---|---|
| `0988d2cd-4e1d-47c6-b0db-0ff0335b12e6:0:2:0` | exile#0 | 2 | PASS | UNRESOLVED |
| `09ef446c-a13d-49d9-a94c-cd5f5a2d440b:0:0:0` | exile#0 | 2 | PASS | UNRESOLVED |
| `60a69ddc-3289-4786-944d-27a82c5f0dc8:0:0:0` | exile#0 | 2 | PASS | UNRESOLVED |
| `9ad12c75-e97d-404a-bfa9-26ff1d0bb506:0:0:0` | exile#0 | 2 | PASS | UNRESOLVED |
| `b095526e-94a4-416b-83de-d6271804ccf3:0:0:0` | exile#0 | 1 | PASS (not relevant) | UNRESOLVED (not relevant) |

In the first four rows, K4's PASS covers only the destination mark. I3's K4
row classes an unextracted span as UNRESOLVED ("the span itself was not
extracted"), so the audited outcome is UNRESOLVED. On `b095526e…`, ATTACH-3 is
not even asked, because its only ATTACH-3 span is the missing one.

**Latent exposure (the reason this class is escalated).** Suppose the trigger
condition were extracted in the four two-region clauses:

- It would not start "at the start of the clause's scope", the literal R1
  text, because the label comes first.
- So it would not be an R1 shape.
- It would then keep its interface/1 attachment: every region of the clause,
  which is a `multiple` attachment.
- That is the K4 KILL shape that R1 was ratified to answer (27 of the 29
  interface/1 K4 kills).

The interface/2 reach report counted extracted spans only, so the Captain's
R1 reach review never saw these clauses.

**This review does not count a KILL here**, for three reasons:

- I3 classes the measured state as UNRESOLVED.
- The latent KILL depends on an extractor change that C03 does not have.
- It also depends on reading R1 literally. CR 207.2c and 207.2d say the label
  has no rules meaning, so the trigger is structurally the start of the
  ability, and H-REGION can express "one attachment, to the ability".

Whether R1's "start of the clause's scope" reads past such a label is a
semantic-law question (a STOP-class PROGRAM BOUNDARY for any unit), so it goes
to the Captain. **CAPTAIN escalation requested** (batched; see §8).

### FS-3 — operations inside a quoted created ability (1 population clause)

In `b9432430-df01-497d-b025-7576dce830e4:0:0:0`, both regions, the exile and
the return, lie inside a quoted ability that this clause grants. By the frozen
P4 rule (I3's relations and ATTACH-3 marks exclude quoted created abilities),
the back-reference and the destination inside the quotes are not tested. So:

- K3's PASS rests on the printed `then` sequencing alone.
- K4 does not apply to the clause.

This is correct under the interface, and the outcomes are credited. Two things
are only claimed at region level:

- C2 is answered for the granted ability's operations, which are owned by the
  granting clause's occurrence.
- The references inside the quotes remain C04 and M2 work.

### FS-4 — participants told apart within or across regions (2 clauses)

- `05e0a10d-532a-451c-a54e-27e64969fe0e:0:0:0` (participant-role-choreography):
  one destroy region holds two targets with different choosers.
- `bf20bc37-3205-45af-a3be-05d6835c0d87:0:0:0`, the population's one repeated
  operation (destroy + destroy): each destroy gets its own region, with a
  different chooser.

In both clauses, the chooser distinction is a participant and decision-authority
matter (V1 M2 and R2-B), not region identity. K6's PASS ("answerable at region
plus occurrence identity") is credited.

`bf20bc37…` has one census row, (destroy, 0), so no independent evidence makes
its two destroys distinct required operations. K1/K2 UNRESOLVED (not
relevant) is I3's prescribed outcome, not a gap. Even if a consumer asked them
apart, the spans already tell them apart.

### FS-5 — a replacement whose choice is not a head (1 fixture clause)

In `eccc9a54-2b56-4a02-9926-258d5b2e25fb:0:0:0`, the replacement condition
attaches to the clause's one region. The printed choice before the reveal has
no legacy head. A choice made while an effect resolves is not a separate
instruction boundary in the frozen detector (CR 608.2d), and a replacement
condition governs its whole replacement (CR 614.1a). So the single attachment
is defensible, and K4's PASS is credited.

If a future detector made the choice a head, this standalone `if` (not an R1
shape) would attach to two regions. This is recorded as a latent exposure of
lower weight than FS-2. It is not escalated on its own: it comes from the same
R1 question as FS-2.

### FS-6 — K3's PASSes and their reach

The audit checked every PASS-ing back-reference in the exile-then-return
clauses against the source. Each referring phrase (`it`, `that card`,
`those cards`, `its`, `their`) in the return region refers to the target of
the exile region, and K3 names that target's span in region 0.

Four clauses also print a counter phrase ending in `it` inside the return
region:

- `094c4486…:0:0:0`
- `20194297…:0:1:0`
- `5c63a244…:0:0:0`
- `a959a91a…:0:0:0`

That `it` means the returned object. K3 searches earlier regions only, and
reaches region 0's target through the same chain. The named endpoint is right;
object continuity across the zone change (CR 400.7) is C04's.

All six back-references in the first region are UNRESOLVED and not PASS (D3).
No false success was found in K3.

### Clauses credited without exception

Every other PASS was checked against the source and is credited. The audit
found nothing else that changes a credited PASS. The other
rows carry these audit codes:

- **A-BLINK:** the 48 standard exile-then-return clauses. Each has two
  regions cut at `then`, with the destination attached to the return region.
  Any R1 prefix (a cost-colon or a trigger at the clause start) is attached
  once, to the ability.
- **A-SEQ:** clauses whose second head is a different operation (proliferate,
  populate, reveal, search, create, shuffle and cloak, or a return joined by `and`), sequenced by `then` or `and`.
- **A-NONE:** fixture clauses with nothing to attach or relate.

## 4. Per-condition verdict against interface/2 I3 and I3a

The measured result for every condition is kill.json's. **Audited relevant
PASS** subtracts the PASSes that §3 does not credit. Every condition keeps
relevant PASS above zero, so none is flagged "PASS coverage insufficient"
under either count.

| condition | measured relevant PASS / UNRESOLVED / KILL | audited relevant PASS | verdict |
|---|---|---|---|
| K1 distinct ownership | 56 / 26 / 0 | 56 | not killed on the P2 population |
| K2 repeated operations | 56 / 26 / 0 | 56 | not killed on the P2 population |
| K3 relation endpoint | 74 / 18 / 0 | 74 | not killed on the P2 population |
| K4 qualifier attachment | 79 / 9 / 0 | 74 (FS-1: 1, FS-2: 4) | not killed on the P2 population |
| K5 overlap / nesting | 29 / 0 / 0 | 29 | not killed on the P2 population |
| K6 stronger identity needed | 84 / 10 / 0 | 84 | not killed on the P2 population |
| K7 guesses or exceptions | 94 / 0 / 0 | 92 (FS-1: 2) | not killed on the P2 population |

**K1 and K2.**

- All 56 relevant PASSes are clauses whose distinct required operations rest
  on independent evidence: C2's exile and return, or the
  two-sequential-operations and delayed-return roles.
- No PASS is inferred from candidate heads alone, as I3 requires.
- K2's PASSes say "no two required operations share a head". The one
  repeated-head clause, `bf20bc37…`, has no independent distinctness evidence
  (FS-4), so K2 has never been exercised on a real repeated operation that a
  consumer asks apart. **K2 survives, but its kill arm is shown only on rigged
  input.**

**K3.**

- Every relevant UNRESOLVED is a named endpoint whose referent is C04's
  (D3, D4, D5), or a clause with no region (D2).
- R3 applied once (`bac0fcee…`), as recorded.
- R2's two former kills are UNRESOLVED, never PASS.

**K4.**

- R1 attaches every scope-start cost-colon and trigger once, to the ability.
- The audit's limit is FS-2: the R1 question for label-prefixed triggers is
  open.

**K5.**

- Relevance is fixtures only: no population clause has an overlap, and no
  population K5 is non-PASS.
- Overlap and nesting are 0 by construction.
- **Every K5 PASS is vacuous.** The condition is not killed and its PASS
  count is sufficient, but it was never tested on a real overlap.

**K6.**

- Every UNRESOLVED is a fixture clause where an ATTACH-3 span has no region
  (D2), or where the C2 pair is not inside this clause (D6), or a modal
  header (D7).
- No PASS needed an identity beyond region plus the four-coordinate
  occurrence.
- FS-4's chooser distinctions are participant structure, not identity.

**K7.**

- Every region uses a rule in the table, and every rule passes
  `assert_not_card_keyed`.
- FS-1's two regions are extraction failures, not guesses.

**No relevant KILL** exists for any condition, measured or audited. No finding
needs a new identity coordinate.

## 5. Dispositions for every UNRESOLVED

| code | meaning | disposition |
|---|---|---|
| D1 | K1/K2 UNRESOLVED: no FIXTURES role or consumer question shows two distinct required operations | Prescribed by I3 ("never PASS, never KILL"). It includes the one-operation negative-control fixture, where UNRESOLVED is the expected result. No action under this interface. |
| D2 | the clause prints an operation the frozen legacy detector does not extract, so no region exists (a `put` instruction; a replacement's exile or discard; a draw; a mill; a static grant of abilities), so its K3, K4 or K6 UNRESOLVED has no region to read | An extraction gap: V1 §10 Tier B. The frozen detector may not be edited, and the corrected detector is reported, never substituted (I2). Carried to M2/M3 extraction work. Not a kill. |
| D3 | a back-reference named in the clause's first region, or a delayed return's `that card`, whose referent lies in the same region or an earlier clause | The endpoint is named. Resolving it (and CR 400.7 continuity) is C04 reference work. |
| D4 | R3: a plural reference named as one printed list (`bac0fcee…`) | I3a R3: UNRESOLVED, never PASS. The Captain's reading (5899825420) is the expected C04 resolution. |
| D5 | a reference whose referent is outside every region, or for which no candidate span was extracted (a players `they`; a mana `it`) | Reference discovery and resolution, carried to C04. Not a kill. |
| D6 | a fixture clause with no operation of its own (a keyword line) whose role's operations are in its sibling clauses | C2 is answered by the sibling clauses (`008d5896…:0:1:0` and `:0:1:1`, K1/K2 PASS). UNRESOLVED here is honest. |
| D7 | a modal header's trigger condition: the clause has no region, and the operations are in the mode paragraphs (CR 700.2) | Modal and cardinality law is reused, not rebuilt (V1 §4). This crosses paragraphs and is outside within-clause H-REGION. The span is extracted and attachable to no region in this clause. C03's code classes that as no-region, and that classification is on record under interface/1 and interface/2. **Flagged for the cross-reviewer:** a literal reading of K4's "or to none" could call it a KILL. This review reads it as I3's extraction/no-region class, because its operations are not in this clause. |

Fixtures that have a member without a clause carry their disposition in the
fixture table (§6).

## 6. Coverage ledger

Outcomes are kill.json's, unedited. A row's disposition column holds its
audit code (§3) and, for any UNRESOLVED, its disposition code (§5). Every
disposition cell, in this table and in the fixture table, is a §3/§5 code or
disposition text; none is a placeholder. Each of the 41 rows with an UNRESOLVED
names the §5 code (D1-D7) for every UNRESOLVED condition it carries.

| clause | census key | population | fixtures | K1 | K2 | K3 | K4 | K5 | K6 | K7 | disposition |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `008d5896-6fc9-4aaa-8c6f-a44c2feb98bb:0:0:0` | none | no | delayed-return-same-object | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | UNRESOLVED | PASS | A-NONE (keyword line); D1; D6 (K6) |
| `008d5896-6fc9-4aaa-8c6f-a44c2feb98bb:0:1:0` | exile#0 | no | delayed-return-same-object | PASS | PASS | UNRESOLVED | PASS | PASS | PASS | PASS | credited (delayed-return pair; R1 trigger); D3 (K3) |
| `008d5896-6fc9-4aaa-8c6f-a44c2feb98bb:0:1:1` | none | no | delayed-return-same-object | PASS | PASS | UNRESOLVED | PASS | PASS | PASS | PASS | credited (delayed-return pair); D3 (K3) |
| `00af96af-5eae-4044-a2f7-a08cd0699d1e:0:0:0` | destroy#0 | no | simple-one-operation-negative-control | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | credited (one-operation negative control; R1 trigger); D1 |
| `00b36996-43c6-42a5-892c-c7c8864cf973:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `01160cb5-6d83-4317-9522-74083b3a83bb:0:2:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `0214805d-d207-42da-a25f-2a8e1990904e:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `05e0a10d-532a-451c-a54e-27e64969fe0e:0:0:0` | destroy#0 | no | participant-role-choreography | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | FS-4 credited; D1 |
| `05e0a10d-532a-451c-a54e-27e64969fe0e:0:1:0` | none | no | participant-role-choreography | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | A-NONE (no legacy head); D1 |
| `094c4486-6cae-4268-850e-ff0082e5ad10:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `0988d2cd-4e1d-47c6-b0db-0ff0335b12e6:0:2:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | FS-2 (K4 PASS not credited) |
| `09ef446c-a13d-49d9-a94c-cd5f5a2d440b:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | FS-2 (K4 PASS not credited) |
| `0fd57894-b917-41c8-a394-360d1d31b236:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `1167fe30-32b8-4381-8067-a05cd345977b:0:0:0` | none | no | split-destination-selected-set | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | A-NONE; D1 |
| `1167fe30-32b8-4381-8067-a05cd345977b:0:1:0` | none | no | split-destination-selected-set | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | A-NONE; D1 |
| `1167fe30-32b8-4381-8067-a05cd345977b:0:1:1` | none | no | split-destination-selected-set | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | UNRESOLVED | PASS | D1; D2 (K3, K4, K6) |
| `1225bee2-c829-4a93-9f75-3495277c23bc:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `142af8f1-6d6b-4043-8cc4-6632481972c1:0:0:0` | destroy#0 | yes | two-sequential-operations | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-SEQ credited (two-sequential-operations) |
| `14b839ef-80b1-4e7d-b2fd-38e973899cde:0:1:0` | destroy#0 | yes | none | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | A-SEQ credited (R1 trigger); D1 |
| `169705c3-32c1-4628-b108-c37ca5f27e24:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `16da72a3-d980-4dd8-99f2-8191cce00978:0:0:0` | destroy#0 | yes | none | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | credited (R2 drop; condition attached once); D1; D3 (K3) |
| `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:0:0` | none | no | prior-set-complement-reference | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | FS-1 (K4, K7 PASS not credited); D1 |
| `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:1:0` | none | no | prior-set-complement-reference | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | A-NONE; D1 |
| `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:2:0` | none | no | prior-set-complement-reference | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | A-NONE; D1 |
| `19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:2:1` | none | no | prior-set-complement-reference | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | UNRESOLVED | PASS | D1; D2 (K3, K4, K6) |
| `19ea326f-45ff-4bc0-a957-7d3f22dd8c6f:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `1aa1cf50-ee79-4bef-826b-5f1a9e1aa1a5:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `1ca97394-4e8c-4698-bea1-554f9b10927b:0:1:0` | exile#0 | yes | none | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | A-SEQ credited (R1 cost); D1 |
| `20194297-f2a4-4473-95bc-7c6835e5b6b3:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `29b537f5-4d9f-40ed-b38b-e8faa2b5af7d:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `2cb98ca9-d7bb-416b-a17e-ee5f8e4d78f2:0:0:0` | exile#0 | yes | none | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | credited (R2 drop; condition attached once); D1; D3 (K3) |
| `2d72454f-3d87-4acc-9f46-b8c579f44af8:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `2debd9f1-6d3a-4f0a-8488-603447c44490:0:2:0` | exile#1 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `334e2147-5944-4558-b2bc-2f2bfb96dfa5:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `33869ba6-13e5-4e48-8963-92f7965648fb:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `38a55562-1e2d-4240-9454-219a4a25d38d:0:2:0` | destroy#0 | yes | none | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | A-SEQ credited (R1 cost); D1 |
| `3a30089d-cd2d-49be-9b06-7a2454117692:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `46f77c8c-6817-4aea-a80a-d91f508ccbd0:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `4b072fbb-5e61-4009-bcb1-d493eb4a1be4:0:1:1` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `57d02dc8-e22e-4874-9f02-490a2528a28f:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `58a55d14-b03b-4648-b168-ad35ff088b19:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `5c63a244-75d7-4372-baf4-7a3526f240c8:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `60a69ddc-3289-4786-944d-27a82c5f0dc8:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | FS-2 (K4 PASS not credited) |
| `64824ae5-efab-4b55-9d3c-b9c690bad857:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `6879f5ce-7a1b-4606-bad1-885779b0d456:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `6df57d67-2fd9-4e7a-b67b-f361fc30e496:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `766c644c-04fe-4b01-93dd-09a50d78d01f:0:0:0` | none | no | replacement-event-lineage | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | UNRESOLVED | PASS | D1; D2 (K3, K4, K6) |
| `766c644c-04fe-4b01-93dd-09a50d78d01f:0:1:0` | none | no | replacement-event-lineage | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | A-NONE (permission heads); D1; D5 (K3) |
| `788d3cfa-7706-4728-9c48-cf7bc963d002:1:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `7c4c556c-b5e3-493a-a7b0-38c55b7809ac:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `913e6182-706a-4872-8c8a-e146b0ae0738:0:1:0` | exile#0 | yes | none | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | A-SEQ credited (R1 trigger); D1 |
| `92019547-f6db-4ea6-8356-d0a90ace5662:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `97cf544e-ffbf-4730-8cd2-4f1d5be933f2:0:0:0` | exile#0 | yes | none | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | A-SEQ credited; D1 |
| `9ad12c75-e97d-404a-bfa9-26ff1d0bb506:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | FS-2 (K4 PASS not credited) |
| `9b1f552a-bddc-4fcb-ac67-b4a65b2f48ba:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `9f762b9f-7525-4ff8-bc1d-fbab66fd4013:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `a2a380d8-4df7-4357-862c-ed3fb795db6c:0:0:0` | destroy#0 | yes | none | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | A-SEQ credited; D1 |
| `a3ec6b5d-08ec-4ae0-b1db-c4b87a1849c7:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `a6a7bf77-0560-4572-a826-3bc9df1f78d1:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `a6b28298-9624-49d7-ad73-fcd1fd3556d2:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `a959a91a-3e1d-4bd4-9e14-5ee977540146:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `b095526e-94a4-416b-83de-d6271804ccf3:0:0:0` | exile#0 | yes | none | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | FS-2 (unmarked trigger; R2 drop); D1 |
| `b11c250c-f191-4c52-ba02-a9176f163447:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `b1462c82-7702-451b-b612-990353a79ac4:0:2:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `b9432430-df01-497d-b025-7576dce830e4:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | FS-3 credited (quoted created ability) |
| `bac0fcee-9c1a-46b7-86c8-ffbfcc1e96de:0:0:0` | exile#0 | yes | none | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | A-SEQ credited; D1; D4 (K3) |
| `bf20bc37-3205-45af-a3be-05d6835c0d87:0:0:0` | destroy#0 | yes | none | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | FS-4 credited (R1 cost); D1 |
| `c259e16f-2a44-4552-8678-815f757a02e8:0:0:0` | none | no | ability-borrowing-inheritance-pressure | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | FS-1 (K7 PASS not credited); D1; D5 (K3) |
| `c259e16f-2a44-4552-8678-815f757a02e8:0:1:0` | none | no | ability-borrowing-inheritance-pressure | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | D1; D2 (K3) |
| `c259e16f-2a44-4552-8678-815f757a02e8:0:2:0` | none | no | ability-borrowing-inheritance-pressure | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | credited (R1 cost-colon, one region); D1 |
| `c259e16f-2a44-4552-8678-815f757a02e8:0:2:1` | none | no | ability-borrowing-inheritance-pressure | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | UNRESOLVED | PASS | D1; D2 (K3, K4, K6) |
| `c4212ba4-8c43-40ca-aa36-b3b535659fa8:0:0:0` | none | no | modal-regression-control | UNRESOLVED | UNRESOLVED | PASS | UNRESOLVED | PASS | UNRESOLVED | PASS | D1; D7 (K4, K6) |
| `c4212ba4-8c43-40ca-aa36-b3b535659fa8:0:1:0` | none | no | modal-regression-control | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | A-NONE (no legacy head); D1 |
| `c4212ba4-8c43-40ca-aa36-b3b535659fa8:0:2:0` | none | no | modal-regression-control | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | A-NONE (legacy head missed; corrected detector differs); D1 |
| `c4212ba4-8c43-40ca-aa36-b3b535659fa8:0:3:0` | none | no | modal-regression-control | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | A-NONE (no legacy head); D1 |
| `c4d2fdf9-637d-4e97-ae33-45f2d27bf8cd:0:2:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `c786a0aa-d86f-42c3-a7ea-5cb6ab72b5ec:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `cd1eda60-53e4-44d0-9b2c-7a57395e291f:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `d5b9d250-92f5-40d8-b962-4ae4adb466c8:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `d6239ada-c72a-49b2-882c-6dae1dd366e3:0:0:0` | exile#0 | yes | none | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | PASS | A-SEQ credited; D1 |
| `dfbd3afc-9905-4cff-a4f4-df08a4d0a7fa:0:2:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `e1708ad9-35d4-4243-92ca-ddf9d129aa32:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `e71863a7-0de1-4ab5-95e8-c39e6810d899:1:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `e875b468-b475-4573-adf6-312ca4ab6994:0:0:1` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `eae87919-6322-4bd2-ae9c-b1ce25d686da:0:0:0` | none | no | replacement-event-lineage | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | UNRESOLVED | PASS | D1; D2 (K3, K4, K6) |
| `eae87919-6322-4bd2-ae9c-b1ce25d686da:0:0:1` | none | no | replacement-event-lineage | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | UNRESOLVED | PASS | D1; D2 (K3, K4, K6) |
| `eae87919-6322-4bd2-ae9c-b1ce25d686da:0:0:2` | none | no | replacement-event-lineage | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | UNRESOLVED | PASS | D1; D2 (K3, K4, K6) |
| `eccc9a54-2b56-4a02-9926-258d5b2e25fb:0:0:0` | none | no | replacement-event-lineage | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | PASS | PASS | PASS | FS-5 credited; D1; D3 (K3) |
| `eccc9a54-2b56-4a02-9926-258d5b2e25fb:0:0:1` | none | no | replacement-event-lineage | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | PASS | UNRESOLVED | PASS | D1; D2 (K3, K4, K6) |
| `ef9a5bd1-6ce2-4570-9d42-89d997e2fc6f:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `f4a73cde-58bf-4719-8eb0-e039fdde4f62:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `f8a88521-80e5-419b-ab4e-f4b3aba8afa0:0:1:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `f96a2aa6-3259-4bb6-92cd-4d17215d04d0:0:0:0` | exile#0 | yes | none | PASS | PASS | PASS | PASS | PASS | PASS | PASS | A-BLINK credited |
| `fd09875f-71a1-41c2-b404-ff58f4d4cb6c:0:1:0` | exile#0 | yes | none | PASS | PASS | UNRESOLVED | PASS | PASS | PASS | PASS | A-BLINK credited (R1 cost); D3 (K3) |

| fixture | member status | members | clauses | disposition |
|---|---|---|---|---|
| simple-one-operation-negative-control | F0_SELECTED | 1 | 1 | every member clause reviewed (ledger) |
| two-sequential-operations | F0_SELECTED | 1 | 1 | every member clause reviewed (ledger) |
| split-destination-selected-set | F0_SELECTED_PRODUCTION_FIXTURE | 1 | 3 | every member clause reviewed (ledger) |
| delayed-return-same-object | F0_SELECTED | 1 | 3 | every member clause reviewed (ledger) |
| prior-set-complement-reference | F0_SELECTED_PRODUCTION_FIXTURE | 1 | 4 | every member clause reviewed (ledger) |
| conditional-second-operation | F0_REVIEWED_NULL | 0 | 0 | F0_REVIEWED_NULL: FIXTURES.json selects no member, so no clause exists to test; conditional coverage rests on the population condition-marker clauses (16da72a3…, 2cb98ca9…, c4d2fdf9…) |
| replacement-event-lineage | V1_NAMED_PRESSURE_SET | 4 | 7 | one of 4 members matches 0 cards by exact card or face name: recorded, not guessed (I2: no member may be added or swapped); the 7 clauses of its other 3 members are reviewed; a fixture-selection finding, not a C03 outcome |
| modal-regression-control | V1_NAMED_REGRESSION_EVIDENCE | 1 | 4 | every member clause reviewed (ledger) |
| participant-role-choreography | F0_SELECTED | 1 | 2 | every member clause reviewed (ledger) |
| ability-borrowing-inheritance-pressure | CAPTAIN_NAMED | 1 | 4 | every member clause reviewed (ledger) |

## 7. Totals and the H-REGION outcome

Outcome totals and PASS-coverage flags per condition are kill.json's, checked
by `m04_check.py`.

| condition | all PASS | all UNRESOLVED | all KILL | relevant | relevant PASS | relevant UNRESOLVED | relevant KILL | PASS coverage | result |
|---|---|---|---|---|---|---|---|---|---|
| K1 | 56 | 38 | 0 | 82 | 56 | 26 | 0 | sufficient | not killed on the P2 population |
| K2 | 56 | 38 | 0 | 82 | 56 | 26 | 0 | sufficient | not killed on the P2 population |
| K3 | 76 | 18 | 0 | 92 | 74 | 18 | 0 | sufficient | not killed on the P2 population |
| K4 | 85 | 9 | 0 | 88 | 79 | 9 | 0 | sufficient | not killed on the P2 population |
| K5 | 94 | 0 | 0 | 29 | 29 | 0 | 0 | sufficient | not killed on the P2 population |
| K6 | 84 | 10 | 0 | 94 | 84 | 10 | 0 | sufficient | not killed on the P2 population |
| K7 | 94 | 0 | 0 | 94 | 94 | 0 | 0 | sufficient | not killed on the P2 population |

H-REGION result: not killed on the P2 population

In interface/2's words: under interface/2, H-REGION is **not killed on the P2
population** for any of K1-K7, never "confirmed" (the population covers only
three object-lattice actions). No condition is flagged "PASS coverage
insufficient". UNRESOLVED counts are findings for M04 and are disposed of
above; they are not verdicts.

## 8. Escalations and open questions (batched for the Captain)

These do not change the result.

1. **FS-2 (CAPTAIN).** Does R1's "starts at the start of the clause's scope"
   read past a label with no rules meaning (CR 207.2c/207.2d) before a
   trigger? This is a semantic-law ruling.
   - If it does not, extracting those triggers would put four population
     clauses into the K4 `multiple` shape.
   - The reach report did not see them.
   - Any change to extraction or to R1 needs its own authorized task.
   - Status: an **open** Captain escalation, batched in decision 5925109323.
     It is not a KILL.
2. **FS-1 (CAPTAIN, minor).** A head the frozen detector matches inside a
   label, or inside a purpose phrase ("to activate"), starts a region. The
   question is whether an R2-like discount is wanted. R2 stays literal until
   ruled.
3. **D7 (for the cross-reviewer).** The modal header's cross-paragraph
   condition: should the no-region classification stand?
4. **Coverage notes.** K5 is vacuously passed (no real overlap exists). K2's
   kill arm has never met a real consumer-asked repeated operation (FS-4).
   Both are recorded so that "not killed" is not read as more than it is.

No real KILL was found. No condition has zero PASS. No finding needs a new
identity coordinate. Under the review boundary, the review itself does not
force a CAPTAIN answer. This document requests Captain attention for item 1
as a batched Captain-owned decision (5925109323), which remains open.
