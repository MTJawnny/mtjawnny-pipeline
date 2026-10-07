# Oracle Compiler Interfaces

`oracle-compiler-interface/5`

**Status: RATIFIED** by Captain decision 6031676826 (2026-10-07, the Captain: "Proceed with
recommended"), taken under standing approval 5918781674 and reversible by the Captain.
It fixes the readings of the §I5.3 sentences that the C04 Worker (evidence 6011004249)
and an independent fresh-session review found to admit more than one reading, and
replaces the §I5.4 and §I5.5 figures with the figures those readings measure. Every
row whose outcome depends on one of these readings was read on the card. It supersedes
`oracle-compiler-interface/4` (blob `290a713a39bfabc8f9bd8810c96a5ffdab7ba1b1`),
whose status was:

> **Status: RATIFIED** by Captain decision 5971927071 (2026-10-03: every recommendation
> of the §I5 draft accepted), with 5966663066 (isolated Claude review of this text
> and a Claude M05 reader) and the Captain's acceptance of the §I5.7 report and of
> the r13 repair from the Captain-directed adversarial card hunt (Captain, 2026-10-03:
> "Give to a session that is adversarial  to C04. Have it I find tricky cards.
> Once we have a pattern of failure. Let's fix it.";
> recorded with this landing). The §I5 text was reviewed in eleven isolated
> adversarial Claude rounds recorded in its draft, and a twelfth that confirmed the
> r13 repair (ACCEPT; its verdict is quoted in this landing's Issue #1 record). It supersedes `oracle-compiler-interface/3` (blob
> `119778a68c0e4e8378f0a117b7c22884ec5eda4b`), whose status was:
>
> > **Status: RATIFIED** by Captain decisions 5925134485 (FS-2 ruled, "go with
> > interface/3") and 5925371124 (flavor labels ignored; test card Typhoid Mary,
> > Fractured), after Codex cross-reviews of this text and the R4 reach report
> > (§I3a), recorded in 5925277948 and its follow-up. It supersedes `oracle-compiler-interface/2` (blob
> > `4ac4d856b651edde05b15c7065aa593f59561dcf`, ratified 5900431196 from the
> > rulings of 5899825420), which superseded interface/1 (blob
> > `3c34cf5a4e8150e43cbce2ec6a92e30272560f6e`). interface/3 adds rule R4 to §I3a,
> > reads R1's scope start after an R4 label, and names R4 in the K7 row. §I1, §I2
> > and §I4 are unchanged from interface/2.
>
> interface/4 adds §I5 (the C04 reference-resolution measurement) and applies the
> R4 errata (a)-(c) of the C03R3 host check (5939152309) to §I3a. §I1, §I2, §I3
> and §I4 are unchanged from interface/3.

interface/5 changes only §I5.3 (the readings), §I5.4 and §I5.5 (the figures), §I5.8
(ruling 17), and the headings that name the version. §I1, §I2, §I3, §I3a, §I4 and §I5.1, §I5.2,
§I5.6 and §I5.7 are unchanged from interface/4.

Implementation tasks must pin `interface_version` and `interface_sha` in their
Issue #1 `T` once a nonzero interface exists.

This file is not task state and does not select work.

## What interface/5 is

A **measurement interface**. It pins what C03 and C04 read, how C03's
H-REGION result is decided, and when C04 counts a reference as resolved (§I5). It defines no record shape, no occurrence
coordinate, no region identity, no reference type and no vocabulary. It
ratifies nothing in AQ4 beyond its existing benchmark status and makes nothing
production truth. C03 and C04 outputs are ignored experimental output under
`experiments/out/oracle_ingest/`.

interface/2 added three derivation rules (§I3a, R1-R3), each a Captain ruling
stated as card-independent structure, and amended K3 and K4 to read them.
interface/3 adds a fourth, R4 (a label printed before an ability or a mode is
ignored unless the CR gives it rules meaning), from the M04 review's finding FS-2.
Beyond R4's run-time reads of the CR's ability-word list, keyword titles, quoted
label forms and rule 107 symbol inventory, used only to classify a label, the
interface adds no ruling registry document, per-line CR or keyword lookup, and no
model-facing context: those belong to the V1 §3.2 Keyword Consequence Registry
interface and V1 Tier B, and are deferred there.

The interface/1 C03 result (`oracle_compiler/measurement/C03-H-REGION-RESULT.md`
at `5078219`, verdict CAPTAIN 5898473142) stays on record unchanged. It is the
evidence these rules answer, not something they rewrite. So do the interface/2
C03 result (`C03-H-REGION-RESULT-I2.md`) and the M04 review that found FS-2.

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
| K7 guesses or exceptions | a region boundary is not derived from printed tokens and CR-grounded structure, or any rule -- R1-R4 included -- is keyed to a card, name or oracle_id | -- (K7 has no UNRESOLVED outcome) |

**Decision rule.** A KILL on any fixture, or on any population clause whose
consumer question needs the distinction, kills H-REGION for that condition. A
kill is a STOP to the Captain and the AQ4 reserved finer-effect path (V1 §5),
never an ad hoc identifier. UNRESOLVED counts are reported per test and are a
finding for M04, not a verdict. Every APPLICABLE outcome arm of every test --
KILL and UNRESOLVED for K1-K6, KILL for K7, which has no UNRESOLVED outcome -- is
shown to fire on a rigged input (CLAUDE.md: a guard never shown to fail is not a
guard). Every outcome that differs from interface/1 only because of R1, R2
or R3 (a PASS from R1 or R2, an UNRESOLVED from R3), and every outcome that
differs from interface/2 only because of R4, is reported as such, per clause,
beside the outcome it replaces.

## I3a. Ratified derivation rules (R1-R3: 5899825420, 5900431196; R4: 5925134485, 5925371124)

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

Implementing R1-R4 is the one authorized change to the C03 derivation and kill
code (`h_region.py`, `h_region_kill.py` and their tests) under this interface.
Nothing else in the derivation may change to turn a kill green.

**R1 `attach-ability-prefix` -- ability-level qualifiers scope the whole
ability.** CR 602.1a (an activated ability's cost is everything before the
colon), CR 603.1 (a triggered ability is `[When/Whenever/At] [trigger
condition], [effect]`) and CR 603.4 (an intervening "if" clause directly after
the trigger condition). "The start of the clause's scope" below is read after
any R4 label. A span is ability-level ONLY when it is one of:

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

**R4 `ability-label` -- a label printed before an ability or a mode is ignored
unless the CR gives it rules meaning; the ability itself is never dropped.**
Captain rulings 5925134485 and 5925371124 ("mark what the CR calls out and ...
dump/ignore the rest ... be sure not to dump the actual abilities"); test card:
Typhoid Mary, Fractured. A *label* is the text at the start of an ability's
line, or of a mode's line after its bullet (`•`, CR 700.2), up to the first
` — ` (U+2014 with one space on each side) that has text after it on the same
line, holding no `—`, `:`, `;`, `.`, `•` or `"`. It is classified in this order,
from the pinned CR read at run time and the card's own rules text, and the first
match decides:

1. **ticket cost** -- one or more `{TK}` symbols and nothing else. CR 107.17a
   and 123.3c: a sticker's ticket cost is paid to put it on an object and is not
   part of the ability the sticker grants (encoding observed, not from the CR:
   the corpus prints a cost of N tickets as N `{TK}`). IGNORED.
2. **ability word** -- a phrase of the CR 207.2c list. IGNORED.
3. **rules-meaningful, KEPT** in the ability, with its interface/2 outcome:
   - a keyword: a CR 701 or 702 title (a parenthesized alias included, e.g.
     `∞`, 702.186), or a comma list of them, or a 702 title with a parameter
     (`Ward 2`, `Toxic 1`, `Ward {2}`);
   - a CR-defined label form: every quoted `“<form> — [` the CR prints, its
     `[placeholders]` read as wildcards and `N` as a number (`To solve`, 719.3a;
     `[A player] faces a villainous choice`, 701.55a; `Visit`, `Boast`, ...),
     and `Prize` (CR 702.159b gives "Prize —" rules meaning but does not quote
     it in that form; errata b). The forms read are exactly: Awaken N, Boast,
     Companion, Exhaust, Forecast, Impending N, Max speed, Partner, Power-up,
     Reinforce N, Solved, Suspend N, To solve, Visit, [A player] faces a
     villainous choice, [Cost]: Level N, {rN}, {rN1}, {rN2}, the list form
     "{rN1}, {rN2}", ∞, [Anchor word] and Prize: 23. "Creature —" (from the
     CR glossary's Summon entry) is not a label form (errata c);
   - a chapter symbol (CR 714.2a/c: a well-formed Roman numeral, or a list);
   - a number, a range or a list of numbers (a die-result row, CR 706);
   - a label holding a `{...}` symbol or a character outside letters (any
     script), digits, spaces and `' ’ , ! ? - ~` (a spree cost `+ {1}`, any
     symbol the CR does not print included: never assumed droppable);
   - an anchor word (CR 614.12c): a label the card's own rules text names
     elsewhere, outside every label and outside the card's own name (`Khans`
     and `Dragons` after "choose Khans or Dragons"). Reading the card's own text
     this way is structure, not a card key (K7): no card, name or oracle_id
     appears in any rule.
4. **flavor label** -- anything else (CR 207.2d: no rules meaning, not listed
   in the CR), including a label that is the card's own name (`~`). IGNORED.

An IGNORED label is outside the scope: the scope starts at the first token after
its ` — `, so the ability or mode text after it is always kept and derived, and
no frozen-detector head inside the label starts a region (the detector is not
edited; every head a label drops is reported per clause, as R2's are). R1's
scope start is read after it. Every label is reported per clause with its class
and CR citation. A `—` at the end of a line (`Choose one —` before its modes)
has no text after it and is no label. The CR reads are the only lookups R4
makes, through `experiments/foundry_cr.py`; they classify a label and nothing
else (this is not the Keyword Consequence Registry). The parse is checked for
completeness, or the derivation STOPs: the 207.2c sentence is found exactly once,
has the form `<a>, <b>, ..., and <z>.`, re-joins exactly to its source text, and
every raw item is a lowercase phrase (optionally with a number), with no
duplicate; the 701 and 702 headings each form a complete 1..N sequence with a
title on every heading, and every 701.N or 702.N rule has its heading; the CR
107 symbol inventory holds at least `{TK}`, `{W}`, `{U}`, `{B}`, `{R}`, `{G}`,
`{C}`, `{X}`, `{S}`, `{T}`, `{Q}` and `{E}`; and the CR label forms include
`to solve`, `solved`, `visit`, `forecast` and a villainous-choice form. Each
check is rigged to STOP on a tampered CR.

**R4 reach report (interface/4, errata a-c).** Labels are counted only at a line
start (chain clause ordinal 0), as the text above and the implementation locate
them; interface/3's table counted every chain-clause start. Measured with the
implementation's own classifier on the pinned corpus (C03R3 host check,
5939152309; 61 ability words and 264 keyword titles read from the CR), with
errata b applied by construction (one clause, `Prize`, moves from flavor label to
CR label form).
3,099 clauses open with a label:

| class | clauses | effect |
|---|---|---|
| ability word | 1,356 | ignored |
| ticket cost | 192 | ignored |
| flavor label | 624 | ignored |
| keyword (title, list or parameter) | 221 | kept |
| chapter symbol | 576 | kept |
| symbol-bearing | 66 | kept |
| anchor word (`Khans`, `Dragons`, the clans, ...) | 28 | kept |
| CR label form (`To solve`, villainous choice, `Prize`, ...) | 21 | kept |
| number / die-result row | 15 | kept |

Labels are ignored on 2,172 clauses and kept on 927. Against interface/3's
table: the 5 mid-line villainous-choice forms are gone (kept either way);
"Catch" (`7d038055…:0:1:1`) is no label, because its line holds "…"; "Prize"
(`43ce339e…:0:1:0`) is a CR label form. No flavor
label contains a rules word (`each`, `target`, `player`, `opponent`, `you`,
`choice`, ...): every flavor label is a name. The Captain's test card resolves as ruled:
on Typhoid Mary, Fractured the mode labels `Mary`, `Typhoid Mary` (printed as the
card's name, `~`) and `Bloody Mary` are flavor labels and are ignored, while each
mode's effect and "Whenever ~ attacks" are kept. On C03's sets R4 reaches the 5
FS-2 population clauses (`Flurry`, `Converge` ability words; `{TK}{TK}` ticket
cost; `Avoidance`, `Protection Fighting Style` flavor labels: the scope moves
and R1 applies) and the FS-1 fixture (`Search the Room`, flavor: its `search`
no longer starts a region). The C03 re-run under interface/3 records the same
counts and every outcome R4 changes, per clause.

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

## I5. C04 reference resolution (interface/5)

**Vocabulary (measurement labels only, never production vocabulary).**
- 4 outcomes.
- 5 endpoint kinds.
- 10 reason codes.
- Every word, list and numeric window that I5.3 prints. They decide RESOLVED vs UNRESOLVED, so ratifying I5.3 ratifies them (Captain question 9).

### Why §I5 must exist before C04 runs

§I4 says WHAT C04 reads. It does not say WHEN a reference counts as resolved. V1 M2: "An unresolved reference is valid output. A guessed reference is not." The rules decide false success, so they are ratified text, as C03's were.

### I5.1 Unit and address

- **Unit.** A §I4 pressure-set candidate (created-ability candidates excluded).
- **Address.** P4 line k is the k-th `foundry_locality.units` paragraph. The line must equal that paragraph's chain clauses joined by one space (measured equal on every corpus paragraph, 61,383 of them). The P4 sentence index is the clause ordinal.
- **Offset.** The n-th whole-word occurrence of the phrase in the clause, where n is the candidate's rank among the P4 candidates with that phrase in that clause.
- **Overlap.** A candidate whose span lies inside a longer P4 candidate's span in the same clause ("the chosen creatures" inside "the chosen creatures get"), or whose phrase is printed fewer times as a whole word than P4 counts (P4 matched it inside a longer form, such as "the exiled card" in "the exiled cards"), is UNRESOLVED (overlap). Only the longer one is resolved.
- **Regions.** Interface/3 H-REGION regions, from `h_region.py`.

### I5.2 Outcomes, endpoints, reasons

| outcome | meaning |
|---|---|
| RESOLVED | exactly one endpoint, named by the rule |
| UNRESOLVED | a reason code (below), never counted against the representation |
| NOT-COREFERENCE | a printed comparison "the same … as" |
| OUT-OF-SCOPE | conditionality that is in the set only through its delay flag |

**Endpoint kinds:**
- EVENT: an earlier region's operation (V1 M2 #6).
- LINKED: a clause in another ability on the face (M2 #7, CR 607).
- COREFERENT: an earlier clause of the same ability, "Exile … the exiled card" (M2 #2/#3).
- PRODUCT: a copy instruction's clause (M2 #5/#6).
- OBJECT: a printed target mark (M2 #2/#3).

**Reason codes:**
- no-candidate
- ambiguous
- detector-reach
- continuity (CR 400.7)
- competing-antecedent
- plural-r3
- overlap
- no-rule
- expletive ("it" naming the game state: "if it's night", "if it's your turn")
- other-chooser (a "chosen" reference after a choice another player made)

### I5.3 Resolution rules

The rules are a table with `id`, `kind`, `cr` and `pattern`, checked by `assert_not_card_keyed`. The guard is live: in the prototype it halted the draft table itself, because "Exile" and "Delay" are card names. The table therefore names frozen sets by reference.

CR 400.7, 607.2a/b/d, 608.2c and 707.10 are read at run time, and the run STOPs unless each one prints its operative phrase.

**IRREG** (19 genuinely irregular participles, with their frozen head or none): dealt, put, drawn→draw, chosen, paid, lost, won, made, dug, spent, found, kept, left, held, sold, taken, given, seen, shown.

- **E1 `event-this-way`** (P4 "this way"; CR 608.2c).
  - **Governing verb.** Scan back from the offset, inside the clause. The governing verb is the first word that is:
    - a participle of a single-word frozen head (-ed, -d, -ied→y, doubled consonant + -ed, or IRREG; never the bare word); or
    - a bare single-word frozen head not preceded by a word in PREPS (into, in, from, to, of, the, a, an, with, on, onto, by). For example, "if you search … this way" counts, but "to cast this way" does not.
  - **Adjectives.** A non-IRREG participle directly after a word in DETS (the, a, an, each, any, those, all, other, another, this, these) is an adjective ("the revealed card", "an exiled card"). It is skipped: it is never the governing verb and never stops the scan. "that" is deliberately not in DETS ("a creature that died this way" stops at "died").
  - **Coordinated verbs.** If the governing verb directly follows "or" or "and" ("sacrifice a permanent or discard a card this way", "destroyed or exiled this way"), the result is UNRESOLVED (ambiguous).
  - **Stop.** Any other -ed word or IRREG word stops the scan: detector-reach.
  - **Endpoint.** The unique region with that head, among:
    - the earlier clauses of the paragraph, and
    - the regions of the same clause that start before the offset, **excluding the region that contains the governing verb itself**;

    and, in both, never a region whose head word directly follows a word in PREPS, separated only by whitespace ("to cast it" is not an event; in "attached to ~, create" the "~," stands between, so "create" is).

    That is an EVENT. No region with that head is no-candidate, and so is a scan that reaches the start of the clause without finding a verb. Several regions is ambiguous.
- **E2 `cr607-linked`** (P4 cr607-linkage; CR 607.2a/b/d).
  - **Only "exiled" and "chosen" forms are E2.** Any other P4 cr607 phrase ("as ~ entered", "put onto the battlefield with ~") is UNRESOLVED (no-rule).
  - **"exiled" forms.** A clause holding a frozen-exile-head region, on the same face, in a paragraph that is any of:
    - activated (a colon in its first sentence);
    - triggered (When, Whenever or At, after any label);
    - replacement ("instead", or "As ~/this … enters").
  - **"chosen <noun>".** The noun is the word after "chosen" in the P4 phrase. A phrase that holds both "chosen" and "exiled" ("the chosen color exiled") is a "chosen" form. The candidates are the clauses earlier in the same ability, the reference's own clause when the choice is printed before the reference, and the clauses of other abilities on the face, that print "choose" (not "can't", "don't" or "cannot choose") with the noun as a whole word after it, chosen by "you".
    - **The noun phrase.** At most 4 words stand between "choose" and the noun ("choose a nonbasic land card name"); a word here is a run of letters, apostrophes, hyphens or "~". Words after the noun do not matter: "choose a creature type" is a choice of "creature", and "choose a card name" of "card". The noun may carry a plural "s": "choose one of those creatures" is a choice of "creature".
    - **Chosen by "you".** The verb opens its sentence or a comma-separated part, or follows "you", "you may", "then" or "and". A sentence opens at its first word, after a leading "•" (CR 700.2: the bullet only marks a mode), after an ability label (§I3a R4), and directly after a colon ("{T}: Choose a color", "+1: Choose a nonland card name": CR 602.1a, the activation cost is everything before the colon).
    - **Another chooser.** Every other "choose" of the noun ("instead choose target creature", "secretly choose a number"; the negated forms above excepted) counts as a choice by someone other than "you". If the same ability holds any "chooses" or "chose" before the reference (this includes "you chose", and the reference's own clause before the reference), or the face holds a choice of that noun by anyone other than "you", the result is UNRESOLVED (other-chooser). This errs toward UNRESOLVED. Another player's choice is never guessed (Captain question 10).
  - **Scope.** These count: the ability's own clause when an exile region of it starts before the reference (its cost, or an earlier instruction); the earlier clauses of the same ability that hold an exile region (any kind of ability, spells included: this is coreference, not CR 607); and clauses of other abilities on the face that meet the activated, triggered or replacement test above (CR 607.2a/b).
  - **One ability.** For this rule, one ability is: a paragraph; its bullet modes (paragraphs starting "•" join the paragraph that opened them); and, on a face whose own type line (the card's type line for a single-faced card) is instant or sorcery, the paragraph "As an additional cost to cast this spell, …" (Captain question 5).
  - **Outcome.** Exactly one candidate in total: COREFERENT if it is in the same ability, LINKED if in another. Candidates in both places: ambiguous (Storm Elemental, Captain question 11). No ordering check, because CR 607 abilities may be printed in either order.
- **E3 `copy-product`** (P4 "the copy"; CR 707.10). The endpoint is the unique printed copy instruction ("copy" followed by it, that, this, target, the, each, those, them, a or an) in an earlier clause of the paragraph or earlier in the same clause. It must not sit inside a When, Whenever, If, As long as or Unless condition, unless that condition has closed with a comma and the copy follows directly, or after "then" or "you may" ("If you do, copy …"). Anything else is UNRESOLVED, which errs toward UNRESOLVED. Endpoint: PRODUCT, at clause level.
- **E4 `singular-back-reference`** (P4 coreference carrying P4's delay flag). **What the flag is.** P4's flag is a per-line text match (`_DELAYED` in `foundry_aq4_probes.py`: "at the beginning of the next", "when … next", "at the end of this/the next turn", "this turn,", "until end of turn"). Most E4 candidates carry it only because their line says "until end of turn". E4 therefore measures singular back-references in general, not CR 603.7 delayed triggers as such; the delayed-trigger subset is reported separately in I5.5 (Captain question 14). An "it" followed by "'s" or "is", then optionally "not", then night, day, your turn, their turn, an opponent's turn or the <word> turn, is UNRESOLVED (expletive). Possessives are no-rule: "that spell's", "its", "their", "that player". Plural markers (PLURAL: they, them, those cards, those creatures, those permanents, those tokens) are plural-r3, the R3 rule of interface/2: a list is named only when exactly one earlier region holds one coordinated P3 list, and the reference is never resolved. For the singular markers in SINGULAR (it, that artifact, that card, that creature, that enchantment, that land, that object, that permanent, that planeswalker, that spell, that token):
  1. **Marks.** Count the P3 `target` marks before the reference in the paragraph. "the target of" is not a mark. 0 is no-candidate; 2 or more is ambiguous.
  2. **Single object mark.** The mark is the word "target" together with a directly preceding "another", "each", "all" or "up to <word>" (the object lattice's target head: "another target creature" is one mark, and its "another" is part of the mark). The mark must name one object: its noun is the first word after it, with at most three words between ("target attacking or blocking creature", "target instant or sorcery card"), that is in OBJ_NOUNS (creature, card, permanent, spell, token, artifact, enchantment, land, planeswalker, object, ability), "player" or "opponent". A word is a run of letters, apostrophes and hyphens that starts with a letter; numbers and symbols are not words. A plural "s" and a possessive "'s" are read off ("target creature's power" names a creature). A ".", ";", ":", "!", "?", straight quotation mark ("), parenthesis or "—" ends the search ("any target. If a creature" has no noun). The noun must not be "player" or "opponent", and the mark must not be plural ("two", "three", "four", "X" or "any number of" target, or "up to" two or more). Otherwise: no-candidate.
  3. **Agreement.** A noun-bearing marker ("that spell") must agree with the mark's noun. "permanent" and "object" agree with any object noun, on either side ("that card" after "target permanent" agrees). Otherwise: no-candidate.
  **Frozen head.** In steps 4 and 5 a frozen head is a head the frozen detector reports, never a head word read off the text. Between the mark and the reference it is the head of an H-REGION region (§I3a, R2 and R4 applied) whose head word starts in that text. In the left-out text below it is a head `effect_heads` reports there (predicate position). A head word with no region is not a frozen head: the noun "counter" in "a +1/+1 counter on it" is not CR 701.6's counter (CR 122.1: a counter is a marker), and neither is "double" in "double strike" or "cast" in "if you cast this spell".
  **Between.** "Between the mark and the reference" is the text from the end of the mark to the reference. When the reference is in a later clause than the mark, the reference's own governing region (the region containing the reference) is left out of that text for steps 4 and 5's head checks and step 4's zone-text check, provided the left-out text holds exactly one frozen head: the act the reference undergoes ("Sacrifice it", "Destroy that creature") is not an event between the mark and the reference. This is E1's own-verb exclusion applied to E4.
  4. **Continuity (CR 400.7).** The result is continuity when any of these holds:
     - the mark's region head is in ZONE (exile, return, destroy, sacrifice, discard, mill, counter, shuffle, cast), or a ZONE word stands directly before the mark ("— Exile target …", where the frozen detector has no region);
     - such a head appears between the mark and the reference;
     - the text between, or the mark's own noun phrase with up to 80 characters before it, prints "onto the battlefield", "cast/play … from" or "put … into";
     - the mark's noun phrase holds "card" or "cards", with at most three words between the mark and it (here a word is any run of letters, digits, commas, apostrophes or hyphens), followed, before any "." "," or ";", by "in" or "from" and then, with at most two words (no commas) between, graveyard(s), library or libraries, hand(s) or exile ("target creature card in your graveyard"; "target instant or sorcery card in your graveyard"). Archmage's Newt is UNRESOLVED by this, a conservative miss.
  5. **Competing antecedent.** It is competing-antecedent when any of these holds:
     - the mark's region head is in CREATE (create, populate, amass, incubate, manifest, explore, discover, reveal, search, draw, investigate);
     - any frozen head appears between the mark and the reference, whatever its word (the head of the mark's own region included, when it starts there);
     - "copy", "token" or "create" is printed between them (own region included), or in up to 60 characters before the mark;
     - a mass noun (mana, damage, life, energy, loyalty, poison) is printed between them, own region included (Grell Philosopher's "blue mana … it");
     - for "it" only: "~" or "this <OBJ_NOUNS word>", not possessive, is printed between them, own region included (Cyclical Evolution's "Exile ~ with three time counters on it");
     - the paragraph before the reference, outside the mark's own noun phrase (by position: from the mark's first word, "another" in "another target creature", to its noun), prints an indefinite object noun phrase (a, an, another, each or any, then at most two words, then an OBJ_NOUNS word: "a nontoken creature"), or "choose" or "chosen".
  6. **Otherwise:** OBJECT, that mark.
- **E5 `comparison`.** NOT-COREFERENCE only when the clause prints "the same … as". It names no endpoint. Otherwise no-rule.
- **E6.** P4 conditionality with a delay flag: OUT-OF-SCOPE.
- **Residue.** "the last" (14), "the exiled" (11) and "the returned" (2): no-rule. In the pressure set, "that way", "such a" and "such an" are 0.

### I5.4 Pre-committed audit (M05): a complete read, not a sample

- **Pattern classes, defined now (for ruling 4, I5.8).** E1: one class per frozen head. E2: "exiled" and "chosen". E3: one class. E4: one class per marker. E5: one class.
- **Rules frozen first.** C04's rules and lists are frozen (this text plus the implementation at the C04 accepted head) before M05 reads anything. A repair after reading starts a new C04/M05 round. It is never applied to rows already read.
- **Every positive claim is read.** M05 reads every RESOLVED and every NOT-COREFERENCE candidate. On the pinned corpus: E1 529, E2 498, E3 196, E4 561, E5 119, which is 1,903. Each rule is one unit. This is complete by construction, with no sample. The reader is a fresh isolated session, not the C04 Worker and not the author of the rules.
- **C04 acceptance condition.** C04's output (ignored experimental output) carries, per candidate, the reference clause text, the endpoint clause text and the endpoint position, as the prototype does: region span for E1, mark span for E4, clause for E2/E3.
- **Record and verdict.** M05 writes three verdicts per row: endpoint correct, endpoint kind correct, not a duplicate. For E5, "endpoint correct" means the clause is a comparison. Each verdict is yes, no, or cannot judge with the reason. A "cannot judge" is listed and counted, never folded into yes. If more than 5% of a rule's rows are "cannot judge", that rule's audit is INCONCLUSIVE and goes to the Captain.
- **UNRESOLVED.** Never read for false success, because it cannot be one (V1 M2). It is reported as findings, by reason.
- **Fixtures.** Every FIXTURES.json member with a pressure-set candidate (roles delayed-return-same-object, prior-set-complement-reference, replacement-event-lineage, ability-borrowing-inheritance-pressure, two-sequential-operations) gets every candidate read, whatever its outcome.
- **A wrong RESOLVED** is a false success. It goes to the Captain (Captain question 4).

### I5.5 Reach (interface/5 readings, measured 2026-10-07, pinned corpus)

Measured with the C04 Worker's implementation (evidence 6011004249) with only the readings ruling 17 names changed; two builds byte-identical.

| rule | candidates | RESOLVED | UNRESOLVED | NOT-COREFERENCE | OUT-OF-SCOPE |
|---|---|---|---|---|---|
| E1 event-this-way | 1,088 | 529 | 559 | 0 | 0 |
| E2 cr607-linked (LINKED / COREFERENT) | 676 | 498 | 178 | 0 | 0 |
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

E2 RESOLVED by endpoint kind: LINKED 322, COREFERENT 176.

E4 delayed-trigger subset (reference clause prints "at the beginning of the next"): 450 candidates, 25 RESOLVED (Slave of Bolas, Angrath, Puffer Extract, Stone Giant …); the rest are no-candidate 186 (no target mark: tokens, the source itself), no-rule 108, plural-r3 55, continuity 48, competing-antecedent 26, ambiguous 2.

Against the interface/4 figures (prototype r9 `proto11.py`), these readings resolve 78 more rows and none fewer: E4 76 (60 need the frozen-head reading and 17 the mark's own "another"; Arwen, Mortal Queen needs both) and E2 2 (Academic Probation's bulleted choice, Zevlor's own-clause choice). Each was read on the card and found correct. No endpoint of a row RESOLVED under both moves.

The pressure set reconciles with §I4 (1,548 / 741 / 3,774, with overlaps counted once). The E2 row has 676 candidates rather than 741, because 65 CR 607 candidates are overlap duplicates, counted in the residue/overlap row (65 overlaps in all).

### I5.6 Development cards (used to build the rules, not an audit)

| card | reference | r3 outcome |
|---|---|---|
| Necromancer's Covenant; Kaya, Geist Hunter; Multani's Decree; Hermit Druid | "… exiled/destroyed/revealed this way" | E1 EVENT, the right region |
| Visions of Dominance; Nahiri, Forged in Fury | "costs {X} less to cast this way" / "cast Equipment spells this way" | E1 UNRESOLVED. r2 had used the reference's own region as the endpoint |
| Devout Invocation | "creature tapped this way" | E1 UNRESOLVED detector-reach |
| Order of the Stars; Wormfang Behemoth | "the chosen color" / "the exiled cards" | E2 LINKED |
| Pyromancer Ascension | "the copy" / "the same name as" | E3 PRODUCT / E5 NOT-COREFERENCE |
| Turn Against; Soul Sear; Soilshaper; Spider-Man, Peter Parker | "It" / "That permanent" after one single-object target | E4 OBJECT |
| Kiki-Jiki; Feldon; Molten Duplication; Gaze of Pain; Phyrexian Splicer | "it" with a token, copy, other creature or chosen ability in play | E4 UNRESOLVED competing-antecedent / continuity |
| Flickerwisp; Gruesome Encore; Macabre Mockery; Sins of the Past; Ogre Battlecaster | after exile, return, or put/cast from a zone | E4 UNRESOLVED (CR 400.7) |
| Autumn Willow; Livaan; Skyfire Kirin; Triton Tactics | player mark / noun disagreement / plural mark | E4 UNRESOLVED |
| Koth of the Hammer | "Untap target Mountain. It …" | E4 UNRESOLVED. "Mountain" is a subtype, not an OBJ_NOUNS word. A conservative miss, not a false success |

### I5.7 Coverage and discovery report (findings only; Captain 5971927071 card test)

V1 P0.4 lists "reference discovery" among what C04 tests. C04 therefore also writes a report that resolves nothing, claims nothing and is not read by M05. Every figure in it is a count. No row in it is a RESOLVED or NOT-COREFERENCE claim.

- **Coverage.** Every P4 candidate of the I4 extraction (created-ability candidates excluded, as I5.1) is counted by kind, split in vs. out of the pressure set (21,672 coreference, of which 2,844 are in the set; 8,642 conditionality, 723 in; 741 cr607-linkage and 1,548 kind-unclear, all in). The out-of-set coreference candidates are counted by P4 phrase. C04 applies no I5.3 rule to them.
- **Discovery.** For each corpus line, C04 counts every whole-word, case-insensitive occurrence of these back-reference forms: "the rest", "that much", "the other", "the sacrificed", "the discarded", "the revealed", "the milled", "the destroyed", "the returned", "the countered", "the targeted", "the enchanted", "the blocking", "the attacking", "the card", "the cards", "the token", "the tokens", "the spell", "the creature", "the creatures", "the permanent", "the permanents", "he", "him", "his", "she", "her". An occurrence is **covered** when a P4 candidate on the same line (I5.1 line; created-ability candidates excluded) has a lowercased phrase that begins, as a plain string prefix, with the form; it is **uncovered** otherwise. C04 reports covered and uncovered counts per form, with the card names of the first three uncovered occurrences in card-name order (code point), then line, then position in the line; repeated names count as separate occurrences. The list is declared and over-counts (for example, "the creature type" is not a reference). Its counts are a finding about P4's reach, never a defect count. P4 is frozen and is not edited (Captain question 16).
- **Card test.** The report reprints this table. C04 measures only the in/out-of-set status, the I5.3 outcome and endpoint kind of in-set rows, and covered/uncovered; the words in parentheses are explanatory notes, not C04 output:

| card | reference | C04 outcome |
|---|---|---|
| Act of Treason | "Untap that creature. It gains haste" | in set, RESOLVED (OBJECT) |
| Oblivion Ring | "return the exiled card" | in set, RESOLVED (LINKED) |
| Swords to Plowshares | "Its controller …" | out of set (possessive) |
| Rancor | "return it to its owner's hand" | out of set (the card itself) |
| Demonic Tutor | "put that card into your hand" | out of set (found card) |
| Fling | "the sacrificed creature's power" | uncovered (P4 has no candidate) |
| Zuko, Conflicted | "return him" | uncovered (P4 has no candidate) |

Drafting note, not part of C04's report: on 2026-10-03 the r8 prototype, run over the out-of-set coreference candidates as an experiment, resolved 348 of 18,828. Those rows are unaudited and claimed for nothing. The uncovered discovery forms total 1,670 occurrences (covered: 2, both "the returned").

### I5.8 Rulings (Captain 5971927071; 5966663066; Q16 accepted 2026-10-03)

1. E6: the 723 delay-flagged conditionality candidates are OUT-OF-SCOPE. They are conditionality markers, not references; they enter the set only through P4's per-line delay flag.
2. E5: "the same … as" is a comparison, recorded as NOT-COREFERENCE with no endpoint.
3. No reach floor for C04 (V1 M2: an unresolved reference is valid output).
4. A false RESOLVED found by M05 withdraws only the failing pattern class (the I5.4 classes as written); the rule is repaired, C04 re-run and every row of that rule re-read in a new M05 round.
5. Endpoint kinds and "one ability" (I5.3 E2) are measurement only. Same-ability "the exiled card" is COREFERENT, not CR 607 LINKED.
6. Replacement-lineage endpoints (V1 P0.4): C04 does not resolve them until A01 R2-A has reported; C04 then takes R2-A's result as its rule, or records them UNRESOLVED (no-rule) with that result cited.
7. Self-references, expletive "it" and subtype-named marks stay UNRESOLVED under their own reason codes.
8. "deal" and "put" in E1 stay detector-reach: the frozen detector is not edited (§I3a).
9. Every word, list and numeric window I5.3 prints is ratified with it. The implementation uses no word, list or window I5.3 does not print; any change is an interface change.
10. A "chosen" reference after another player's choice is UNRESOLVED (other-chooser).
11. When a reference's own ability and another ability both hold a candidate exile, the result is ambiguous. M05 cannot revisit rules; a change is a new C04 round.
12. (Withdrawn in drafting: no COMPARAND endpoint.)
13. A governing verb directly after "or"/"and" is UNRESOLVED (ambiguous), with no window.
14. C04 reports the delayed-trigger subset ("at the beginning of the next …") separately, as its delayed-link measurement. The CR 603.7 trigger-to-creator link stays UNRESOLVED (no-rule), named as a finding.
15. This text is reviewed by isolated adversarial Claude sessions, and the M05 reader is a fresh isolated Claude session (5966663066).
16. The I5.7 coverage and discovery report is a report only. New rule families ("the card itself", "its/their", the triggering object, a found card) follow one at a time, each as its own interface change after M05. P4 discovery stays frozen.
17. **interface/5 readings (Captain 6031676826, standing approval 5918781674).** The readings §I5.3 prints for E2 ("chosen <noun>": the noun, the noun phrase, chosen by "you", another chooser) and E4 (the mark, the noun search, agreement, frozen head, the card noun phrase, the mark's own noun phrase) are ratified with it, and ruling 9 applies to them. They were found by comparing the C04 Worker's implementation with the prototype row by row, and by checking each §I5.3 term against the CR. Five readings change no outcome on the pinned corpus and are printed so that the text decides them: agreement on either side, the punctuation that ends the noun search, the plural mark noun, the card noun phrase, and "you chose" in the reference's own clause. A second reading of any other §I5.3 sentence that changes an outcome is a STOP to the Captain, as before.

Implementation note: the prototype measures plural references as plural-r3 without naming R3's list, since they are never RESOLVED either way. C04 names the list, and checks R3's precondition, using `h_region_kill.py`'s R3 code.
