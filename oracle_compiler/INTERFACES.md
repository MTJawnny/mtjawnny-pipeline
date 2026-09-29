# Oracle Compiler Interfaces

`oracle-compiler-interface/2`

**Status: RATIFIED** by Captain decision 5900431196 (Issue #1), after a Codex
cross-review of the draft (5900323061) and the R1-R3 reach report (§I3a). Its
rulings come from Captain decision 5899825420 (C03 H-REGION kills, option B).
It supersedes `oracle-compiler-interface/1` (blob
`3c34cf5a4e8150e43cbce2ec6a92e30272560f6e`). interface/2 changes §I3 (new §I3a, amended K3 and K4 rows, and the
decision-rule note) and adds one clarifying sentence to §I2. §I1 and §I4 are
unchanged from interface/1.

Implementation tasks must pin `interface_version` and `interface_sha` in their
Issue #1 `T` once a nonzero interface exists.

This file is not task state and does not select work.

## What interface/2 is

A **measurement interface**. It pins what C03 and C04 read and how C03's
H-REGION result is decided. It defines no record shape, no occurrence
coordinate, no region identity, no reference type and no vocabulary. It
ratifies nothing in AQ4 beyond its existing benchmark status and makes nothing
production truth. C03 and C04 outputs are ignored experimental output under
`experiments/out/oracle_ingest/`.

interface/2 adds exactly three derivation rules (§I3a), each a Captain ruling
stated as card-independent structure, and amends K3 and K4 to read them. It
does not add a ruling registry document, per-line CR or keyword lookup, or any
model-facing context: those belong to the V1 §3.2 Keyword Consequence Registry
interface and V1 Tier B, and are deferred there.

The interface/1 C03 result (`oracle_compiler/measurement/C03-H-REGION-RESULT.md`
at `5078219`, verdict CAPTAIN 5898473142) stays on record unchanged. It is the
evidence these rules answer, not something they rewrite.

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

The population is defined on the frozen legacy heads and does not change under
§I3a: R2 changes which candidate heads start a region, never which clauses are
population members.

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
| K3 relation endpoint | an endpoint of a relation the clause states between its operations or their objects -- a back-reference, a CR 607 link, a conditional dependency or a delayed link among P4's frozen candidate structures, or a printed sequencing link between two of its heads -- cannot be NAMED unambiguously: it maps to no region, to several regions, or to several candidate referent spans inside its region. Endpoint identity is tested directly; a unique region assignment alone does not pass K3 | the endpoint is named, but what it refers to is not resolved (reference resolution is C04's work). Under R3 (§I3a) a plural back-reference whose candidates are one printed coordinated list is named (the list) and is UNRESOLVED here -- never PASS: whether it means the whole list or part of it is C04's |
| K4 qualifier attachment | a cost, condition, duration or destination span (ATTACH-3) is attachable to more than one region, or to none, by the derivation rule. Under R1 (§I3a) an ability-level cost or trigger-condition span attached to every region of its ability is ONE attachment (the ability) and passes | the span itself was not extracted |
| K5 overlap / nesting | two regions overlap or nest so that their identities, or the attachments a consumer question needs, cannot be told apart by any deterministic rule from printed structure. Shared tokens alone are not a kill: nested regions may share tokens while keeping unambiguous identities and attachments, and such an overlap PASSES (reported as a count and list) | a region taking part in the overlap was not derived because extraction failed |
| K6 stronger identity needed | ATTACH-1, ATTACH-3 or C2 cannot be answered for the clause because of identity granularity: K1-K5 do not fire on it, every needed endpoint is named, and the answer still needs to distinguish things its regions plus the existing four-coordinate occurrence cannot | the question fails because of an extraction or resolution failure |
| K7 guesses or exceptions | a region boundary is not derived from printed tokens and CR-grounded structure, or any rule -- R1-R3 included -- is keyed to a card, name or oracle_id | -- (K7 has no UNRESOLVED outcome) |

**Decision rule.** A KILL on any fixture, or on any population clause whose
consumer question needs the distinction, kills H-REGION for that condition. A
kill is a STOP to the Captain and the AQ4 reserved finer-effect path (V1 §5),
never an ad hoc identifier. UNRESOLVED counts are reported per test and are a
finding for M04, not a verdict. Every APPLICABLE outcome arm of every test --
KILL and UNRESOLVED for K1-K6, KILL for K7, which has no UNRESOLVED outcome -- is
shown to fire on a rigged input (CLAUDE.md: a guard never shown to fail is not a
guard). Every outcome that differs from interface/1 only because of R1, R2
or R3 (a PASS from R1 or R2, an UNRESOLVED from R3) is reported as such, per
clause, beside the interface/1 outcome it replaces.

## I3a. Ratified derivation rules (Captain decision 5899825420)

Each rule is an entry in the derivation rule table (`RULES` in
`experiments/oracle_ingest/h_region.py`) with exactly the four structural keys
`id`, `kind`, `cr`, `pattern`, guarded by `assert_not_card_keyed` (K7). For each
rule a rigged card-keyed variant is shown to halt. The clauses that prompted a
rule are regression fixtures that must keep passing, never keys: no rule may
name a card, a card name or an oracle_id, and no rule transcribes CR text (the
`cr` value is a citation, read at run time through `experiments/foundry_cr.py`).
The clauses that prompted the rules are regression cases in the C03 test suite
(`tests/oracle_ingest/`); they are not additions to the frozen `FIXTURES.json`
membership, which stays fixed (§I2).

Implementing R1-R3 is the one authorized change to the C03 derivation and kill
code (`h_region.py`, `h_region_kill.py` and their tests) under this interface.
Nothing else in the derivation may change to turn a kill green.

**R1 `attach-ability-prefix` -- ability-level qualifiers scope the whole
ability.** CR 602.1a (an activated ability's cost is everything before the
colon), CR 603.1 (a triggered ability is `[When/Whenever/At] [trigger
condition], [effect]`) and CR 603.4 (an intervening "if" clause directly after
the trigger condition). A span is ability-level ONLY when it is one of:

- a `cost-colon` span that starts at the start of the clause's scope and ends
  at the colon of the activated ability whose effect holds the clause's regions
  (loyalty costs included: they are activation costs before the colon);
- a `condition-trigger` span that starts at the start of the clause's scope
  with `When`, `Whenever` or `At` and ends at the trigger condition's comma;
- a `condition-marker` span beginning `if` that starts immediately after such
  a trigger condition's comma (the intervening "if", CR 603.4).

Such a span governs every region of its ability: one attachment -- to the
ability -- and K4 PASSES. Prefix position alone never qualifies, and neither
does a `condition-marker` by itself. Everything else keeps its interface/1
outcome, including: a standalone `If ..., <operation> ...` with no trigger
word; a condition, delayed or nested trigger printed inside the effect; a
duration or destination span; and any span that crosses a region boundary.
The rule already exists in `RULES`; interface/2 narrows it to these shapes and
makes it law for K4.

**R2 `head-not-payment-cast` -- a payment description is not an operation.**
CR 106.1 and CR 601.2h (mana is spent to pay costs; paying the total cost is a
step of casting a spell). A candidate head `cast` whose printed tokens are
immediately preceded by `spent to` (as in `... was spent to cast this spell`)
describes how the spell's cost was paid, and starts no region. Only that token
sequence qualifies: `cast` as an instruction or permission (`you may cast`,
`cast it`, `cast that card`) is unaffected, and no other head is discounted.
The frozen detector (`effect_heads`) is not edited: the discount is a
derivation rule, and every clause where it drops a legacy head is reported per
clause, as legacy-versus-corrected differences already are. A condition span
that contained the discounted head then attaches under the ordinary rules.

**R3 `group-back-reference` -- a plural back-reference to one printed list is
named, and its meaning is C04's.** CR 608.2c (instructions are followed in
order, and later text may refer to earlier text). Applies when ALL hold:

- the reference is a non-possessive plural form of the frozen
  `_PRONOUN_MARKERS`: `they`, `them`, `those cards`, `those creatures`,
  `those permanents`, `those tokens`;
- exactly one earlier region of the clause holds candidate referent spans,
  and it holds two or more;
- those candidates form ONE printed coordinated list, decided from the frozen
  P3 matches alone (P3 is not edited). The list's members are P3's own marks
  in the region, in printed order: every `_TARGET_TOKEN` match (`target`) and
  the `ol._SECOND_OBJECT` match (an `and <determiner>` conjunct, whose match
  begins with its own `and`). Each gap between consecutive marks -- from the
  end of the earlier mark to the start of the next `target` mark, or to the
  end of a `second-object` match -- contains exactly one coordinator (`and`,
  `,`, or `, and` counted once) and no frozen effect head (`_HEAD_RE`), no
  frozen boundary word (`_BOUNDARY_WORD`), and no `.`, `;` or `:`. Every
  candidate the region holds is a member; one gap failing means no list.

Then the endpoint is NAMED -- the list -- and K3 is UNRESOLVED for that
relation, never PASS: whether the reference means the whole list or part of it
(`those creatures` after `an artifact and two creatures`), and what the group
becomes (a pile a keyword action turns into permanents), is reference
resolution (C04) and keyword consequence (V1 §3.2). If list membership cannot
be established deterministically, the rule does not apply and the interface/1
KILL stands (fail closed). A singular back-reference (`it`, `that card`, ...)
to several candidates, and a plural reference over candidates that are not one
list, keep their interface/1 outcome. The Captain's reading of the prompting
clause (decision 5899825420: the whole three-card pile, then the three
face-down creatures it became) is recorded as the expected C04 resolution for
that case.

**Reach report (precondition of ratification, met: decision 5900431196).**
Before the Captain ratifies interface/2, each rule's trigger is run deterministically over every clause of
the pinned corpus (§I1), not only the population, and the report lists every
clause it fires on, with counts per rule and per interface/1 outcome it would
change. The Captain reviews the reach; an overreach is a STOP back to this
text, never a silent narrowing in code. The C03 re-run under interface/2 records
the same counts for the population and the fixtures.

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
