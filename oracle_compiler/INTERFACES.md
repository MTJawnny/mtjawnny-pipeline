# Oracle Compiler Interfaces

`oracle-compiler-interface/1`

Proposed by the Wave-1 review (`analysis/WAVE1-REVIEW.md` §5) under Captain
decision H3 (Issue #1 comment 5877426463): ratified when that review is accepted
by cross-review. Before then, the interface in force is
`oracle-compiler-interface/0`: nothing compiler-specific is frozen beyond
Captain-ratified V1 and existing repository law.

Implementation tasks must pin `interface_version` and `interface_sha` in their
Issue #1 `T` once a nonzero interface exists.

This file is not task state and does not select work.

## What interface/1 is

A **measurement interface**. It pins what C03 and C04 read and how C03's
H-REGION result is decided, before either exists. It defines no record shape,
no occurrence coordinate, no region identity, no reference type and no
vocabulary. It ratifies nothing in AQ4 beyond its existing benchmark status and
makes nothing production truth. C03 and C04 outputs are ignored experimental
output under `experiments/out/oracle_ingest/`.

## I1. Pinned inputs

| input | sha256 |
|---|---|
| frozen probe `benchmarks/aq4/experiments/foundry_aq4_probes.py` | `eec9a4e2aea4c27d74dfffc6d4b82fdcd6f7292bd777aadc2c8625215c7c48f6` |
| corpus bulk file (operator `data/raw/oracle-cards.jsonl.gz`, 32,557 cards) | `2be88ba86da7ecbbb541094f28439c4888c5585c9ca8155e097f1cd0b548d872` |
| CR `config/cr/MTG_Comprehensive_Rules_2026-08-07_LLM.md` | `ca904dc900ce8e06c240960f937590df431aa2d97ec1569140cc910c56202d8b` |
| accepted C02 output (`--all --json`) | `74e3559d785dc3ac47d14823ac1fec96dd446ae446d82a3ee45b03ef3f818dfd` |

A differing identity is a STOP, never a silent re-measurement.

## I2. C03 population

The P2 population as C02 measured it: census clause occurrences
(`foundry_qualifier_census.population()`) with more than one head on the frozen
legacy path (`foundry_aq4_probes.effect_heads`, §27a). C03 re-derives it with
those frozen functions and reconciles before any other work:

- 66 clauses of 2,110; head-count distribution {1: 2044, 2: 65, 3: 1};
- 53 "exile + return"; by family exile 60, destroy 6, bounce 0;
- every one of the 25 examples in the C02 output is a member.

Any mismatch is a STOP. The corrected detector (`semantic_action_heads`) may be
reported alongside, per clause, and never substituted.

The COST-region precedent (AQ4 register #27: 113 regions on the frozen open
surface, none crossing a clause boundary, none ambiguous) is the pattern
H-REGION is tested against. C03 cites it and does not re-measure it; importing
AQ4 benchmark code needs its own authorization.

Fixtures: C03 does not start until the fixture selection freeze (Wave-1 review
F2) is accepted. Fixture members are then fixed; C03 may not add, drop or swap
one.

A result on this population is reported as "not killed on the P2 population" or
"killed", never "confirmed": the population is three object-lattice actions
only.

## I3. H-REGION kill-condition tests (V1 §5 M1), pre-committed

Each test runs on every population clause and every fixture, and runs twice
with byte-identical output. The consumer questions are AQ4 §20's within-card set
that bears on operation granularity: ATTACH-1, ATTACH-3 and C2 (the blink test).
C03 adds no question.

**Three outcomes per test per clause, never two.** KILL is reserved for what V1
§5 names. A failure of extraction or resolution -- a head missed, a span not
derived, a reference not resolved -- is **UNRESOLVED** (V1 §10 Tier B), reported
with its count and clause list, and never counted as a kill: V1 kills H-REGION
on what the representation cannot express, not on what an extractor failed to
find. Otherwise the test PASSES.

**Distinct required operations.** Candidate heads alone never establish them
(accepted C02: a candidate head does not prove a distinct effect), and no single
detector is a prerequisite: the legacy detector is deliberately incomplete
(§27a). Two operations of a clause are *distinct required operations* when
independent evidence establishes it -- a fixture whose accepted role asserts
them (`FIXTURES.json`), or a consumer question (ATTACH-1 or C2) that asks about
them separately for that clause, with the printed operations each carrying its
own instruction boundary under either detector path. Where no independent
evidence establishes the distinction, the clause is UNRESOLVED for K1 and K2,
never PASS and never KILL.

| V1 kill condition | KILL when | UNRESOLVED (not a kill) when |
|---|---|---|
| K1 distinct ownership | two distinct required operations get no two distinct, stable, source-spanned regions owned by the clause's occurrence | the heads are not shown to be distinct required operations, or a region is not derived because extraction failed |
| K2 repeated operations | two distinct required operations with the same head cannot be told apart by span where ATTACH-1 or C2 asks which one acts | as K1 |
| K3 relation endpoint | an endpoint of a relation the clause states between its operations or their objects -- a back-reference, a CR 607 link, a conditional dependency or a delayed link among P4's frozen candidate structures, or a printed sequencing link between two of its heads -- cannot be NAMED unambiguously: it maps to no region, to several regions, or to several candidate referent spans inside its region. Endpoint identity is tested directly; a unique region assignment alone does not pass K3 | the endpoint is named, but what it refers to is not resolved (reference resolution is C04's work) |
| K4 qualifier attachment | a cost, condition, duration or destination span (ATTACH-3) is attachable to more than one region, or to none, by the derivation rule | the span itself was not extracted |
| K5 overlap / nesting | two regions overlap or nest so that their identities, or the attachments a consumer question needs, cannot be told apart by any deterministic rule from printed structure. Shared tokens alone are not a kill: nested regions may share tokens while keeping unambiguous identities and attachments, and such an overlap PASSES (reported as a count and list) | a region taking part in the overlap was not derived because extraction failed |
| K6 stronger identity needed | ATTACH-1, ATTACH-3 or C2 cannot be answered for the clause because of identity granularity: K1-K5 do not fire on it, every needed endpoint is named, and the answer still needs to distinguish things its regions plus the existing four-coordinate occurrence cannot | the question fails because of an extraction or resolution failure |
| K7 guesses or exceptions | a region boundary is not derived from printed tokens and CR-grounded structure, or any rule is keyed to a card, name or oracle_id | -- (K7 has no UNRESOLVED outcome) |

**Decision rule.** A KILL on any fixture, or on any population clause whose
consumer question needs the distinction, kills H-REGION for that condition. A
kill is a STOP to the Captain and the AQ4 reserved finer-effect path (V1 §5),
never an ad hoc identifier. UNRESOLVED counts are reported per test and are a
finding for M04, not a verdict. Every APPLICABLE outcome arm of every test --
KILL and UNRESOLVED for K1-K6, KILL for K7, which has no UNRESOLVED outcome -- is
shown to fire on a rigged input (CLAUDE.md: a guard never shown to fail is not a
guard).

## I4. C04 pressure set

The accepted C02 output holds P4's aggregates, not its individual candidates,
so C04 reconstructs them and reconciles before any other work:

- **Extraction:** the frozen `relation_candidates` (default kind rules) over
  every card of `fc.load_corpus_gated()` under the I1 identities, in the frozen
  `p4` card order (by name).
- **Exclusions, as `p4` applies them:** reminder text is stripped by the frozen
  line reader; candidates inside a quoted created ability are excluded and
  counted.
- **Reconciliation, all equal to accepted C02 P4 or STOP:** 32,557 cards;
  16,245 with candidates; 32,603 candidates; by kind coreference 21,672,
  conditionality 8,642, cr607-linkage 741, kind-unclear 1,548; 3,774
  delay-marked; 12,400 cross-line; 607 excluded inside created abilities.
- **Pressure set membership:** a candidate is in the set when its kind is
  kind-unclear or cr607-linkage, or it is delay-marked. Delay marking is a
  per-line flag, so the subsets overlap. Each candidate appears once, carrying
  all its flags, and the pairwise overlap counts are reported.
- **Candidate identity:** (oracle_id, line, sentence, phrase, kind) plus its
  ordinal among identical tuples in extraction order. Candidates are never
  deduplicated beyond that (P4: "every printed occurrence is one candidate").

These are candidate classifications, not established edges. An unresolved
reference is valid output; a guessed one is not.
