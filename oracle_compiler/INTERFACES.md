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

Each test runs on every population clause and every fixture, reports a count
and the list of clauses where it fires, and runs twice with byte-identical
output. The consumer questions are AQ4 §20's within-card set that bears on
operation granularity: ATTACH-1, ATTACH-3 and C2 (the blink test). C03 adds no
question.

| V1 kill condition | fires on a clause when |
|---|---|
| K1 distinct ownership | two candidate heads of the clause get no two distinct, source-spanned regions inside the clause, or either head gets none |
| K2 repeated operations | the same head occurs twice and the two regions cannot be told apart by span, where ATTACH-1 or C2 asks which one acts |
| K3 relation endpoint | a back-reference that links two operations (for example the returned object of an exile-then-return) cannot be assigned to exactly one region |
| K4 qualifier attachment | a cost, condition, duration or destination span (ATTACH-3) is attachable to more than one region, or to none, by the derivation rule |
| K5 overlap / nesting | two regions overlap without containment, or nest so that ownership of a span is not unique |
| K6 stronger identity needed | ATTACH-1, ATTACH-3 or C2 cannot be answered for the clause from its regions plus the existing four-coordinate occurrence |
| K7 guesses or exceptions | a region boundary is not derived from printed tokens and CR-grounded structure, or any rule is keyed to a card, name or oracle_id |

**Decision rule.** Any test firing on a fixture, or on a population clause whose
consumer question needs the distinction, kills H-REGION for that condition. A
kill is a STOP to the Captain and the AQ4 reserved finer-effect path (V1 §5),
never an ad hoc identifier. A condition that never fires is reported with its
negative control shown to fire on a rigged input (CLAUDE.md: a guard never shown
to fail is not a guard).

## I4. C04 pressure set

C04 (V1 P0.4) takes P4's candidate references as recorded in the accepted C02
output: 1,548 kind-unclear ("this way" 1,088, "the same" 225, "the copy" 208),
3,774 delayed-marked, 741 CR 607 linkage candidates. They are candidate
classifications, not established edges. An unresolved reference is valid
output; a guessed one is not.
