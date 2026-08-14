# T3 AXIS FOUNDRY — ARCHITECTURE AUDIT

**Scope, as extended 2026-08-12.** Sections 4 and 5 were written and committed
first (`02a9799`), at Captain's instruction. This pass appends the directive's
sections 6 (options), 7 (direct answers), 8 (both adversarial cases), 12
(recoverable assets) and 13 (open questions). The directive's Phase One
inventory (§3) and its §2.1 observed-behavior confirmation are still NOT in this
document, and §3.4 guard archaeology and §3.5 spend accounting are covered only
where sections 6 and 7 needed them.

Zero mutation: nothing in the repository was created, edited or deleted except
this file. No API calls. Codebook sha256 `b4197e94…`, unchanged. Gate 2 was run
green at the start and the end of this pass (13 gates, 12 pass, 1 known-excused
`family_sweep`, 0 unexpected failures).

**Note on the directive's stated state (§2).** Three of its six "believed true"
items are already false and a session running the full directive would spend
tokens rediscovering that: the codebook is 403 active / 615 total rather than
"roughly 455"; `det-patterns-v1.json` was superseded by v2 on 2026-08-01; and
B-MIGRATION is described as "queued, not executed" but executed 2026-08-01,
which is why the codebook is schema `foundry-codebook/2`. Spend at roughly $90
of $140 is correct.

---

## HEADLINE FINDING

The architecture is sound in its parts and unsound in its sequencing: every
component this project built to a ratified standard works, and the one
irreversible choice it made was to run a $56.94 open-vocabulary pass over the
whole corpus before any consumer interface existed to receive it, before the
codebook was fixed, and before anything measured whether a derived tag reaches
a shipped card. The measurement this session owes says the parser ceiling is far
higher than the shipped lattice suggests: CR-derived templated frames reach
**21,691 of 32,557 cards, 66.6%**, against the object lattice's shipped 6.5%, at
$0.00 and 100% reproducibility by construction. The corrective is therefore not
to abandon the model but to demote it from author to adjudicator of a measured
33.4% residual, and to fix the interface before spending the remaining budget,
because `docs/WIRE-RESULT-2026-08-09.md` already showed that a correctly plumbed
codebook does not rank, it partitions.

## SUB-HEADLINE FOR SECTIONS 4 AND 5 (written in the first pass)

The tag layer exposes the predicates a similarity tool needs and is missing the
two a Budget Swapper needs, magnitude and role, where magnitude is absent from
every one of the 403 active axes. Separately, the axis space contains at least
four distinct kinds of description and **records which kind an axis is
nowhere**, so no consumer can select the subset it needs without a human
reading all 403. That second finding is structural, it is measurable, and it is
the most plausible single cause of the session token cost Captain is asking
about.

---

## 4. CONSUMER REQUIREMENTS, DERIVED BACKWARD

Built from each tool's job inward. What the tags currently do was measured only
after the requirement was written.

### 4.1 The four consumers and the predicates their job requires

**Magic Thesaurus** (similarity, "same job different words"). Given card X,
return cards doing the same job in different words. Requires: effect verb,
target object class, deck role. Magnitude and cost band are secondary, since
"same job" tolerates a different rate.

**Budget Swapper** (functional equivalent, lower price). Given X, return Y
performing the same action on the same object class at comparable magnitude and
speed, cheaper. Requires: effect verb, target object class, **magnitude**,
timing, cost band, price.

**Deck Analyzer** (role gap, replacement). Given a decklist, name the missing
roles and suggest fills. Requires: **deck role** at a deliberately coarse
grain (ramp, draw, spot removal, wipe, tutor, recursion, protection, wincon),
plus cost band. It does not require, and is actively harmed by, fine grain: a
gap in "spot removal" is not answered by 47 sibling axes.

**Similar Cards** (already shipping on embeddings; tags as explanation layer).
Requires whatever predicate can be rendered as a human-readable reason. It does
not need completeness, since the ranking already exists. It needs the tag it
shows to be **correct**, because a visible wrong reason discredits a correct
ranking.

### 4.2 What the codebook exposes, measured

Slot occupancy across the 403 active axes, by tokenizing each slug against the
ratified vocabularies in `experiments/validate_slug.py:137-147` and the
DELIVERY, EFFECT, SCOPE and QUALIFIER sets in the same file:

| grammar slot | axes carrying it | share |
|---|--:|--:|
| DELIVERY | 291 | 72% |
| EFFECT | 278 | 69% |
| OBJECT | 203 | 50% |
| SCOPE | 131 | 33% |
| QUALIFIER | 63 | 16% |

**Magnitude is absent.** Zero of 403 active axes carry a numeric magnitude in
the slug. 27 carry the `-scales-with-` connective, which names the variable a
magnitude depends on but not the magnitude.

Card metadata covers several predicates without the tag layer at all. Price is
present (`pipeline/build_db.py:135` `price_usd`, `pipeline/trim_merge.py:63`),
as are `cmc`, `type_line`, `legalities` and `rarity`
(`pipeline/build_db.py:42`), and `game_changer` is already a column on the same
line. Budget Swapper's cost band and price are therefore served by the
pipeline, not by the foundry.

**Deck role has no field.** Role is expressible only as words inside a slug
(loot, tutor, recursion, reanimate, drain, taxes, regrowth), and a query for
"all spot removal" has to union a slug set nobody maintains.

### 4.3 Granularity against requirement

Median members per active axis is **4**. **205 of 403 axes, 51%, have fewer
than 5 members** and **87 have exactly one**. One axis,
`rule:targeted-battle-damage`, is active with **zero** members, which the
grammar's own lattice rule forbids ("empty axes never authored",
`docs/MASTER-HANDOFF-ADDENDUM-4.md` §4).

Set against §4.1: Deck Analyzer wants roughly 8 to 12 coarse roles. The
codebook offers 403 axes at median 4 members. **The granularity is one to two
orders of magnitude finer than the consumer that most needs role information
can use**, and the directive's own test applies: granularity beyond consumer
requirement is cost without return.

`INFERENCE`: the fine grain is driven by the design's internal logic rather
than by a downstream requirement. The evidence is that no consumer spec in this
repository names an axis, and `docs/PRODUCT-REALITY-AUDIT-2026-08-09.md` §10
measured 0 of 5 foundry artifacts reaching a shipped card while `codebook.json`
carries 26 `experiments/` consumers.

### 4.4 Precision tolerance

`INFERENCE` throughout this subsection, since no tool in this repository
records an error budget.

| consumer | error cost | tolerance | does 77% same-harness reproducibility clear it |
|---|---|---|---|
| Similar Cards | a wrong reason next to a right ranking | moderate | no, a visibly wrong reason is worse than none |
| Magic Thesaurus | a wrong neighbour in a list | high tolerance | probably |
| Deck Analyzer | a suggestion the user can reject | moderate | marginal |
| **Budget Swapper** | **user buys a card that does not do the job** | **low** | **no** |

Budget Swapper is the consumer with the lowest tolerance and it is also the one
whose required predicates are least served. That pairing is the sharpest result
in this section.

### 4.5 Predicate by consumer

Served = exposed cleanly and queryably today. Partial = present but requires
unioning an unstable slug set. No = absent.

| predicate | Thesaurus | Budget Swapper | Deck Analyzer | Similar Cards |
|---|---|---|---|---|
| effect verb | partial (69%) | partial (69%) | partial | partial |
| target object class | partial (50%) | partial (50%) | partial | partial |
| **magnitude** | n/a | **no (0 of 403)** | n/a | no |
| timing / speed | partial (DELIVERY 72%) | partial | partial | partial |
| cost band | served (metadata) | served (metadata) | served | served |
| price | n/a | served (metadata) | n/a | n/a |
| **deck role** | **no (no field)** | n/a | **no (no field)** | no |
| scope | partial (33%) | partial | n/a | partial |
| duration | no | no | n/a | no |

Nothing in the table is "served" by the foundry. Every served cell is card
metadata the pipeline already carries.

---

## 5. LEVEL ANALYSIS

### 5.1 Method, and its measured error rate

All 403 active axes were classified by a rubric built from the ratified
vocabularies in `experiments/validate_slug.py` rather than from opinion: L0 if
the slug's tokens are CR keyword or restriction vocabulary, L1 if it pairs an
EFFECT token with an OBJECT or counter/token token or carries `scales`, L2 if
it carries a deck-role word, L3 otherwise. The role word list is the one
hand-built element and is flagged as such.

A stratified sample of **30 axes was then hand-scored against the rubric.
Roughly 16 agreed.** The rubric is therefore reported as unreliable, and the
distribution below should be read as indicative only.

Representative disagreements, all in the same direction:

- `rule:modal` (111 members) scored L3. It is CR 700.2, a rules-structure
  fact, so L0.
- `rule:free-cast` (29 members) scored L3. It is cost structure, so L0.
- `rule:etb-plus1-counter-on-target-creature` (23) and
  `rule:mass-plus1-counter-distribution` (41) scored L3. Both are plain
  templated effect tuples, so L1.
- `rule:alternate-win-condition` (16) scored L0. It is a functional role, so L2.
- `rule:evasion-vs-low-power-blockers` scored L0. "low power" is a judgment
  threshold, so L3.

### 5.2 The finding, which is stronger than the distribution

**The rubric fails because the slug does not encode the level, and neither does
anything else in the schema.** The ratified slot grammar is
DELIVERY-EFFECT-OBJECT-SCOPE-QUALIFIER (`docs/MASTER-HANDOFF-ADDENDUM-4.md` §4,
CODEBOOK-NAMING-GRAMMAR v1.1). It records what an axis says. It does not record
what **kind of claim** the axis is making: a closed rules fact, a templated
effect tuple, a coarse deck role, or an editorial judgment.

Consequences that are measurable rather than argued:

1. **A consumer cannot select its level.** Deck Analyzer needs the L2 subset
   and Budget Swapper needs the L0 and L1 subsets. Neither can be queried.
   Producing either list today requires a human to read all 403 axes, which is
   what this section just did, at the accuracy reported above.
2. **Different levels are produced by the same call.** The corpus pass emits a
   label from an open space with one prompt for every card, so a CR 700.2
   structural fact and a "combat trick" judgment come out of the same
   invocation under the same constraint stack.
3. **The levels do not share an error tolerance.** L0 is decidable, so its
   correct error rate is zero. L3 is judgment, so a disagreement rate is
   expected and normal. Holding them to one number produces the 77% figure,
   which is a blend of a population that should be at 100% and a population for
   which 77% may be fine.

### 5.3 Three hard measurements that do not depend on the rubric

**Only 39 of 403 active axes are DET-owned** (`source` field). Those are
decided by a zero-token pattern. The other 364 required either a human batch or
a model.

**Membership provenance across the live codebook is 4,233 `human` assertions
and 3,697 `rule-derived` assertions, and zero `llm` assertions.** The
full-corpus SYNTH pass, at roughly $57.63, has contributed **no membership to
the live codebook**, because its consolidation plan has never been applied
(`docs/CONSOLIDATION-APPLY-HALT-2026-08-09.md`).

**A natural experiment ran on 2026-08-09 and 08-10.** The object lattice
(`experiments/foundry_object_lattice.py`, `docs/OBJECT-LATTICE-2026-08-09.md`)
is pure L0 and L1: it derives its whole vocabulary from CR 110.4, CR 205.2a,
CR 205.3g-q, CR 701.8 and CR 110.1 at run time. It produced **2,653
memberships across 2,131 cards at $0.00**, re-runnable, with reproducibility
that is exactly 100% by construction because it is a parser. The comparison
against 77% same-harness reproducibility on open-vocabulary labels is the
answer to the directive's question about whether levels need different
treatment, measured on this repository's own data rather than reasoned.

### 5.4 Direct answer to the section's question

**Yes.** Axes at different levels require different evidence, different
production methods and different error tolerances, and the evidence is that
when this repository built an L0/L1 family with a parser it cost nothing and
reproduced perfectly, while the same repository's open-vocabulary pass over the
same corpus cost $57.63, measured 77% reproducibility, accumulated the guard
stack that prompted this audit, and has landed zero memberships.

The cost of producing them together is not primarily token spend inside the
model pass. It is that **an undifferentiated axis space cannot be queried by
level, so every downstream question requires a human read**, and every session
that touches the foundry pays that read again.

---

## 6. ARCHITECTURE OPTIONS

### 6.0 The three empirical inputs this phase needed, gathered

The directive names three inputs and forbids guessing them. All three were
measured, with no API calls.

**Update, same day, after Captain asked for the recommended next steps.** The
reach measurement is now committed as `experiments/foundry_reach_census.py` and
every number in 6.0a below is re-derivable by running it. It reproduces this
table exactly. It is a REPORTER and its docstring says so in capitals, because
two of the eight Gate 2 checks were reporters listed as gates and this
repository has already paid for that once. It carries three negative controls,
run with `--selftest`, and all three fire: a truncated CR 701 vocabulary halts,
a vocabulary with one member SUBSTITUTED halts on content while the count still
looks right, and an emptied object domain fails the `must_capture` fixture.
That closes question AQ6 for the reach number only. The prompt economics of
6.0b and the recyclability measurements of 6.0c are still scratchpad work and
still carried-forward counts.

#### 6.0a Templated reach, the measurement Option B's ceiling depends on

**Boundary drawn, stated rather than implied.** A card is TEMPLATE-REACHABLE at
frame T if at least one of its `fc.det_scan_texts()` variants
(`experiments/foundry_common.py:563-573`) matches T, and every slot in T is
filled from a closed vocabulary the CR publishes and this repository already
parses at run time. No hand-typed word list, no judgment threshold. That is
exactly the standard `experiments/foundry_object_lattice.py` met; the frames
below widen its slots and change nothing about its standard.

The frames are nested, not disjoint, so `p.assert_disjoint` does not apply and
summing them would be the overlapping-probe defect. Every number is reported as
incremental reach over the union of the frames above it. Corpus is
`load_corpus_gated()` (`experiments/foundry_common.py:133`), 32,557 cards.

**⚠ THESE NUMBERS MOVED THE SAME DAY, AND THE TOOL IS WHY.** The table below
is the measurement as first taken. Ratifying the object lattice later that day
(AQ1) put its output through the DET standing condition, which found a real
defect in `classify_clause`: the class was read from the whole clause tail
rather than from the target's own noun phrase. Fixing it narrowed the scanning
span, and because this census reuses `classify_clause`, the corrected run reads:

| frame | first taken | corrected | note |
|---|--:|--:|---|
| T1 object lattice | 2,131 | **2,021** | the defect, corrected: 161 memberships were decided by a word outside the target phrase |
| T2b untargeted | 14,364 | **8,229** | NOT the defect. T2b applies `classify_clause` to a frame with no printed `target`, so the narrowed span cuts it hardest. This arm was always the loosest |
| **effect-bearing union** | **21,691 (66.6%)** | **19,298 (59.3%)** | |

**Read the drop as a boundary change, not as a correction of a wrong number.**
Both figures are honest reach under a stated boundary and the boundary moved.
The load-bearing claim survives either way: the parser reaches **59.3%** against
the shipped lattice's **6.2%**, so Option B's ceiling is roughly ten times what
is wired today. What genuinely changed is confidence in the T2b arm, which is
now known to be sensitive to a span decision made for a different frame.

**This is the committed census earning its keep within hours.** Had it stayed a
scratchpad script, the audit would still be quoting 66.6% and nobody could have
known. That is the whole argument of AQ6, demonstrated rather than asserted.

| frame | what fills the slots | cards | share | incremental |
|---|---|--:|--:|--:|
| T1 lattice as shipped | 3 grammar stems x CR 110.4 permanent types | 2,131 | 6.5% | baseline |
| T2 same frame, all CR 701 verbs | 69 keyword actions, `target` required | 2,103 | 6.5% | +358 |
| T2b same verbs, untargeted | `target` not required, CR 205.2a types too | 14,364 | 44.1% | +12,138 |
| T2c same verbs, card objects | object is `<CR type> card`, CR 110.1 | 1,433 | 4.4% | +578 |
| T3 CR 702 keyword printed | `keyword_line_tokens`, no clause parsing | 11,780 | 36.2% | +6,486 |
| **union, effect-bearing** | **T1 to T3** | **21,691** | **66.6%** | **+19,560 over T1** |
| T4 ratified DELIVERY token | timing only, not effect; upper bound | 25,375 | 77.9% | +6,669 |
| union including T4 | | 28,360 | 87.1% | |

**The answer: beyond the three families the object lattice already covers,
CR-derived templated frames reach a further 19,560 cards, taking effect-bearing
template reach from 6.5% to 66.6% of the corpus.** The residual is 10,866 cards,
33.4%, of which 340 are vanilla with no oracle text at all.

Verb sources are `fx.cr_action_terms()`
(`experiments/foundry_shape_extractor.py:455-465`), reading the 69 terms in
`docs/cr-checks.json` whose `kind` is `keyword-action`. Object sources are
`ol.PERMANENT_TYPES` and `ol.CARD_TYPES`. Keyword presence is
`fx.keyword_line_tokens` (`experiments/foundry_shape_extractor.py:1536-1560`),
which tests membership against `KEYWORD_HOME` built from `load_702`.

**Three caveats, each of which caps the number.**

1. **Reach is not membership.** A frame matching is an upper bound on what a
   parser could decide, not a claim that it decides it correctly. The lattice is
   the evidence that reach converts well inside a family: all 39 subtype-derived
   hits read individually with zero defects
   (`docs/OBJECT-LATTICE-2026-08-09.md:109-123`). It is not evidence that it
   converts equally well across 69 verbs nobody has read.
2. **CR 701 is not an effect-verb vocabulary.** It is a list of 69 *named*
   keyword actions, and it omits `return`, `draw`, `deal`, `gain`, `put`, `tap`
   and `untap`, which are among the commonest effect verbs printed on cards.
   This was found by a fixture failure, not by reasoning: `Raise Dead` was
   asserted as a T2c known-positive and the frame refused it, correctly, because
   `return` is absent from CR 701.
3. **The ratified grammar cannot close that gap without a hand-list.**
   `EFFECT_VOCAB` (`experiments/validate_slug.py:123-135`) holds 38 ratified
   slug tokens, but several of them are stems no card prints (`bounce`, `loot`,
   `tutor`, `reanimate`, `regrowth`, `pump`, `debuff`, `taxes`). The stem to
   printed-form map exists for exactly three of them
   (`experiments/foundry_object_lattice.py:234-247`). Building the other 35 by
   hand is the hand-list the engine rules forbid, so the 66.6% is the honest
   CR-derived ceiling and anything above it needs a derivation nobody has yet.

A second fixture failure is worth recording for the same reason: `Rampant
Growth` was asserted as reachable by the permanent-type frames and is not,
because CR 110.1 makes `basic land card` a card in a library rather than a
permanent, and the lattice refuses it on purpose
(`docs/OBJECT-LATTICE-2026-08-09.md:184-188`). That refusal is what made T2c a
separate frame rather than a widening, and T2c is where every tutor, every
reanimation and every graveyard effect lives.

Residual shapes, from a fixed-seed sample of the 10,866: counterspells
(`Force Spike`), damage with a CR 120.1 recipient rather than a type object
(`D'Avenant Archer`), mana production (`Priest of Urabrask`), scry and library
manipulation (`Crystal Ball`), copy effects (`Renegade Doppelganger`) and
counter placement (`Spontaneous Flight`). None of these is un-templated. They
are templated against a *different* closed list, mostly CR 120.1's four damage
recipients and CR 106's mana. That matters for options B and F: the residual is
not a judgment tail, it is a set of families whose closed list has not been
wired up yet.

#### 6.0b Binary judgment versus synthesis, in tokens at current prompt sizes

Recorded totals for run 1
(`experiments/out/foundry/corpus_pass_run1_cost_actual.json`), 814 packs, 40.0
cards per pack, recorded cost $56.94:

| token class | total | per pack | per card |
|---|--:|--:|--:|
| fresh input | 5,548,180 | 6,816 | 170.4 |
| cache read | 2,962,120 | 3,639 | 91.0 |
| cache write (5m) | 14,017,920 | 17,221 | 430.6 |
| output | 6,714,584 | 8,249 | 206.2 |
| **input-side total** | **22,528,220** | **27,676** | **692.0** |

The static portion is measurable directly from the request bodies
(`experiments/out/foundry/corpus_pass_run1_requests.json`, 814 requests). Every
request carries exactly two blocks, and **the system block is byte-identical
across all 814**, sha256 prefix `75ac5377ff4d`: 57,115 characters, 324 lines,
295 bullets, approximately **14,279 tokens** at 4 characters per token. The user
block holds 40 cards in roughly 13,800 characters, approximately **3,450
tokens**, or 86 tokens per card.

**Instruction to payload ratio is 4.1 to 1.** And the cache did not do its job:
cache write exceeds cache read by **4.73 to 1**, meaning the same unchanging
14,279-token prefix was written at cache-creation rate 814 times and mostly
never re-read, which is consistent with a 5-minute TTL and Batch API pack
scheduling. That single line is **14.0M of the 22.5M input-side tokens, 62%**.

A binary judgment prompt is (small rubric) + (one card) + (K candidate axes),
output yes/no plus a quote. Sizes from live artifacts: median oracle text 150
characters, approximately 38 tokens; median active-axis definition 129
characters plus a 35-character slug, approximately 42 tokens per candidate.

| shape | dynamic input per card | output per card | total |
|---|--:|--:|--:|
| synthesis as run | 692 | 206 | 898 |
| binary, K=8 | ~374 | ~64 | ~438 plus amortized rubric |
| binary, K=16 | ~710 | ~130 | ~840 plus amortized rubric |
| binary, K=32 | ~1,382 | ~260 | ~1,642 plus amortized rubric |

**The honest result is not the one the option assumed.** Binary judgment is
roughly half the cost at K=8, roughly a wash at K=16, and more expensive at
K=32. The crossover sits near K=16. Binary judgment therefore buys precision and
a recoverable failure mode; it does not buy a cost saving unless K stays small,
and K staying small is a retrieval-quality problem, not a prompt problem.

#### 6.0c Can run-1 output be recycled

`experiments/out/foundry/corpus_pass_run1_parsed_final.json` holds **46,999
assertions over 32,557 cards**, 2,352 of which received none. Each row is
`{lane, label, definition, actor_scope, evidence_quote}`.

| lane | rows | distinct labels | rows naming a live active axis |
|---|--:|--:|--:|
| `codebook` | 16,195 | 280 | 13,231 (81.7%) |
| `codebook-grammar` | 2,561 | 259 | 1,358 (53.0%) |
| `free` | 28,243 | 25,066 | 160 (0.6%) |
| **total** | **46,999** | **25,604** | **14,749 (31.4%)** |

Two measurements make the recyclability question answerable rather than
rhetorical.

**100% of rows carry an evidence quote, and 89.2% of those quotes are verbatim
substrings of the card's own `det_scan_texts` output.** The remaining 10.8%,
5,095 rows, are not, under an evidence-quote-or-discard law. That is a measured
defect rate on the $56.94 asset and it separates cleanly by task: the pass was
reliable at *extracting evidence* and unreliable at *naming*.

**The free lane's 28,243 rows produced 25,066 distinct labels, 23,278 of them
used exactly once, 92.9% singletons.** That is the open-vocabulary blowup
measured directly rather than inferred, and it is the single strongest piece of
evidence in this document about what actually went wrong.

Run 1 names **253 of the 403 live active axes** and touches **11,993 distinct
cards, 36.8% of the corpus**, with an active-axis assertion.

### 6.1 Option A, continue the current path

**Argued at full strength.** The pass is complete. 46,999 assertions exist on
disk, produced under an evidence law that held 89.2% of the time, and 31.4% of
them already name a live active axis with a quote attached. The lane-aware
consensus architecture was ratified specifically in response to the 77%
reproducibility measurement, so the known defect already has a ratified
remedy that has not yet been given a chance to work. The guard stack is not
noise: `docs/SYSTEM-SELF-TEST-2026-08-09.md` broke all eight Gate 2 checks on
purpose and six caught it, which is a higher standing-check quality than most
projects reach. Continuing costs the least *design* effort of any option here,
and the codebook is a real asset that no other option produces more cheaply.
The consolidation plan takes coverage to 48.0%
(`docs/OBJECT-LATTICE-2026-08-09.md:166-171`), which is more than double
today's 19.3%, and it is already paid for.

**Cost to a shippable state.** The blocking cost is not tokens. The
consolidation plan is unappliable as written: 189 rows target 2 axes it never
creates (`docs/CONSOLIDATION-APPLY-HALT-2026-08-09.md`), and 2,923 redirect rows
create no membership at all (`docs/OBJECT-LATTICE-2026-08-09.md:281-285`). A
consensus second pass over the contested 23% would be roughly 7,490 cards, which
at run-1's $0.00175 per card is approximately **$13**, plus adjudication, so
call it **$15 to $35** against roughly $50 remaining. Expected precision is the
measured 77% same-harness reproducibility. Expected reproducibility is the same
figure by definition.

**What is discarded.** Nothing.

**The $57.63 SYNTH run-1 output:** retained in full and is the input to the
consolidation apply, once the 189-row halt is resolved.
**The 403-axis codebook and its 4,233 human assertions:** retained and grown;
A8 protects human rows from any DET refresh
(`docs/OBJECT-LATTICE-2026-08-09.md:276-278`).

**Risk.** Every measurement in this document says the bottleneck is not
coverage of the codebook but the absence of a consumer that reads it. Spending
the last $50 on making a closed loop larger is the risk, and it is not
hypothetical: routing 1,012 lines on 2026-08-09 passed twelve green gates and
moved nothing a user can see.

**Strongest argument against continuing:** the pass already ran once, and its
free lane produced 23,278 single-use labels, so a second pass under the same
task definition has no measured reason to produce a smaller label space.

### 6.2 Option B, deterministic-first, decision rather than generation

**Argued at full strength.** This is the only option with a natural experiment
already run in this repository, and the experiment came out unambiguously. The
object lattice derives its whole vocabulary from CR 110.4, CR 205.2a, CR
205.3g-q, CR 701.8 and CR 110.1 at run time and produced **2,653 memberships
across 2,131 cards at $0.00**, re-runnable, at 100% reproducibility by
construction, against 77% for the open-vocabulary pass on the same corpus
(`docs/OBJECT-LATTICE-2026-08-09.md:132-176`). It also caught a real defect on
its first sample run and the correction validated the CR reasoning rather than
merely passing: destroy did not move by a single row, because CR 701.8a says
only a permanent can be destroyed (`docs/OBJECT-LATTICE-2026-08-09.md:190-198`).

Section 6.0a is the new evidence and it is the strongest available for this
option: the parser ceiling is **66.6%**, not the 6.5% the shipped lattice
suggests. That is 19,560 cards beyond the current three families, at $0.00, with
a residual of 10,866 for the model. And section 6.0c says the model's residual
work is already half-specified: run 1 was 89.2% reliable at extracting evidence
quotes, which is exactly the sub-task a binary judgment asks for.

**Cost to a shippable state, arithmetic shown.** Parser work on the 21,691
reachable cards is $0.00 in tokens; the cost is engineering, and the lattice is
the calibration point for how much (one module, built and negative-controlled in
a single session). Residual pass on 10,866 cards at K=8 binary judgment, from
6.0b: 10,866 x 438 tokens = **4.76M tokens**, against run 1's 29.2M total for
32,557 cards. That is **16.3%** of run 1's token volume, so roughly **$9**,
call it **$8 to $14** allowing for retrieval overhead. Expected precision on the
parser fraction is whatever a read-verified family achieves, which the lattice
measured at zero defects on 39 hand-read hits. Expected reproducibility on the
parser fraction is 100% by construction and unmeasured on the residual.

**What is discarded.** The free lane's naming, 25,066 distinct labels, is
discarded as vocabulary. It is retained as a candidate pool via the discovery
file's 24,834 clusters.

**The $57.63 SYNTH run-1 output:** repurposed, not discarded, and this is the
option under which it is worth the most. The 18,756 codebook-lane rows are
already binary-judgment shaped, card to existing axis plus a quote, and 14,749
name a live active axis. They become (a) the retrieval training and evaluation
set, (b) a held-out test set for the parser, since they were produced blind to
it, and (c) the prior that decides K. The 5,095 non-verbatim quotes become the
negative control.
**The 403-axis codebook and its 4,233 human assertions:** promoted from output
to input. This is the option's defining move and it is the one that makes the
4,233 Captain-ratified assertions most valuable, because they become the
retrieval target rather than one contributor among many.

**Risk.** The 66.6% is a reach measurement, not a precision measurement, and
nobody has read a sample of the 19,560 newly reachable cards. If precision
outside the destroy family is materially worse than inside it, the number
shrinks and the engineering is already spent.

**Strongest argument against Option B:** its headline ceiling of 66.6% rests on
69 CR 701 verbs of which only three have ever been read against the corpus, and
the two verbs whose fixtures failed this session both failed for reasons nobody
predicted in advance.

### 6.3 Option C, compartmentalized consumer-first slice

**Argued at full strength.** This is the only option that directly attacks the
finding the whole audit keeps returning to. `docs/PRODUCT-REALITY-AUDIT-2026-08-09.md`
§10 and `experiments/foundry_reachability.py` measure **0 of 5 foundry artifacts
reaching a shipped card** while `codebook.json` carries 26 `experiments/`
consumers and 0 `pipeline/` ones. Section 4.5 of this document found that every
"served" cell in the predicate table is card metadata the pipeline already
carries. A vertical slice is the only proposal here that would change that
number on its first delivery rather than on its third. It is also the option
that discovers requirements instead of assuming them, which matters because
section 4 had to derive four consumer specs from tool descriptions, since no
consumer spec in this repository names an axis.

**Cost to a shippable state.** Smallest of the three named options. A Budget
Swapper slice over the object lattice's 2,131 removal cards needs magnitude,
which is absent from all 403 axes but is printed as a literal number on damage
and counter effects and is therefore parseable, and needs price and cost band,
which `pipeline/build_db.py:42,135` already ships. Estimated model spend under
**$5**, possibly $0. Expected precision is high because the slice is chosen to
be decidable. Expected reproducibility on a parsed slice is 100% by
construction.

**What is discarded.** Nothing is discarded; a great deal is deferred, which is
a different thing and a real cost when 3,358 decidably-static lines and a
15,371-row consolidation plan are already waiting.

**The $57.63 SYNTH run-1 output:** neither used nor discarded under C, which is
the honest answer and also the weakest thing about the option. If the slice is
removal, run 1's rows for those 2,131 cards are usable as a test set, but the
other 30,426 cards' assertions sit untouched for however long the slice takes.
**The 403-axis codebook and its 4,233 human assertions:** frozen, not discarded.
The slice reads whichever axes it needs. Under C the codebook stops growing.

**Risk.** A slice proves the pipeline on the shapes the slice contains, and this
repository has already recorded that exact failure: "a ground-truth set only
validates the shapes it contains." Proving Budget Swapper on removal says
nothing about whether the architecture serves Deck Analyzer, whose required
predicate, deck role, has no field at all.

**Strongest argument against Option C:** it answers "can we ship one thing" and
the open question is "is the substrate right", and a slice chosen to be
decidable is chosen to avoid exactly the cases that would answer the second.

### 6.4 Option D, add a `level` field to the axis schema

This is one of the two candidates the directive does not name. It belongs here.

**Argued at full strength.** Section 5.2 found that the schema records what an
axis says and never what kind of claim it is, so no consumer can select the
subset it needs without a human reading all 403 axes. That is a structural
defect with a one-field fix. Deck Analyzer needs the L2 subset; Budget Swapper
needs L0 and L1; Similar Cards needs whichever subset is safe to display. None
is queryable today. The field also unblocks section 4's predicate table from
being a hand-read exercise, and it gives the 77% reproducibility figure a
denominator, since section 5.2's third consequence is that L0 and L3 are being
held to one error number when L0's correct rate is zero and L3's is not.

**Cost.** Zero tokens. The engineering is trivial. The real cost is *assigning*
the value, and section 5.1 measured that: a rubric built from ratified
vocabularies agreed with hand-scoring on roughly 16 of 30 axes, so
auto-assignment is not credible at 53%.

**There is a free and honest variant, and it is better than the rubric.**
Assign level from the `source` field, which already exists and is already
trusted. DET-owned is L0 or L1 by construction, 39 of 403. Human-asserted is L2
or L3. That is not the full four-way split, but it is derived rather than
guessed, it costs nothing, and it is correct by provenance rather than by
opinion. The four-way split can then be refined per axis as consumers ask for it.

**What is discarded.** Nothing.
**The $57.63 SYNTH run-1 output:** untouched. D says nothing about it, which is
D's honest limit: it is a schema fix, not an architecture.
**The 403-axis codebook and its 4,233 human assertions:** untouched and made
more queryable. D is the only option that increases the value of the existing
codebook without changing how anything is produced.

**Risk.** D is cheap enough to be a distraction. It improves queryability of a
codebook that currently has no `pipeline/` consumer, so it can be completed in
full and still move zero shipped artifacts, which is the exact failure §0 of
`CLAUDE.md` warns about.

**Strongest argument against Option D:** a `level` field makes a closed loop
easier to query without making it less closed.

### 6.5 Option E, freeze axis production, card metadata as substrate

The second unnamed candidate. It also belongs here, and it is stronger than it
first sounds.

**Argued at full strength.** Section 4.5's table has exactly one column of
"served" cells and every one of them is card metadata: `price_usd`, `cmc`,
`type_line`, `legalities`, `rarity`, `game_changer`, all at
`pipeline/build_db.py:42,135`. Similar Cards already ships on embeddings and
does not need tag completeness, only tag correctness, because a visible wrong
reason discredits a correct ranking. `docs/WIRE-RESULT-2026-08-09.md` measured
what happens when the codebook is joined to the ranking engine properly: it does
not rank, it partitions into reviewed and not-yet-reviewed, and axis recall
against hand-named correct neighbours was 13 of 33, 39%. The one axis at 100%
recall moved nothing because the engine already reached those cards at Tier 2
for free. On that evidence, the substrate that is actually carrying the product
today is metadata plus embeddings, and tags are an explanation layer. E proposes
to say so out loud and resource accordingly.

**Cost.** Zero tokens. Negative engineering cost, since it stops work.
Expected precision and reproducibility are those of the metadata, which is
Scryfall's and is not in question.

**What is discarded.** Axis production stops. Under a strict reading, the
foundry's forward work is discarded, though not its output.
**The $57.63 SYNTH run-1 output:** discarded as a production input. It survives
only as an explanation corpus, and specifically as its 41,896 verbatim-quoted
rows, which are exactly what an explanation layer needs: a human-readable reason
with a quote from the card. This is the one option where the free lane's 25,066
idiosyncratic labels are an asset rather than a liability, because an
explanation does not need a controlled vocabulary.
**The 403-axis codebook and its 4,233 human assertions:** frozen as a
read-only explanation dictionary. Not discarded, but no longer extended.

**Risk.** E optimizes for the product that exists and forecloses the two that
do not. Budget Swapper's lowest-tolerance predicate is magnitude and Deck
Analyzer's is role; metadata carries neither, so E ships Similar Cards well and
concedes the other two tools permanently.

**Strongest argument against Option E:** it treats the absence of a wire as
proof that no wire is possible, when the wire has been attempted exactly once
and its failure was diagnosed as a coverage problem rather than a plumbing one.

### 6.6 Option F, mine: the predicate table, with axes as saved queries

**None of A through E changes what the primary object is.** A, B and C all
produce axes with memberships; D annotates them; E freezes them. Every finding
in sections 4 and 5 is a symptom of the axis being the primary object:

- Magnitude is absent from all 403 axes because a slug has no numeric slot.
- Deck role has no field because a slug is not a schema.
- Level is unrecorded because an axis records a claim, not a claim's kind.
- Median membership is 4 and 87 axes have one member because a compositional
  slug grammar multiplies slots, and each combination becomes its own object.

**The proposal.** Make the primary object a per-card predicate row:
`(oracle_id, verb, object_class, magnitude, scope, timing, source,
evidence_quote)`. Each column is filled by whichever producer can decide it: the
CR-derived parser fills verb, object class, timing and scope for the measured
66.6%; card metadata fills cost band and price for 100%; magnitude comes from
the literal number where one is printed; the model adjudicates only cells the
parser leaves empty, as a binary judgment. **An axis becomes a saved query over
that table rather than a curated membership list.**

This fixes the four findings above simultaneously rather than one at a time.
Magnitude gets a column instead of a missing slug slot. Deck role becomes a
coarse saved query, which is what section 4.1 says Deck Analyzer wants, 8 to 12
roles rather than 403 axes. Level stops being a missing field and becomes a
property of the *column's producer*, which is the honest version of Option D:
per-column provenance is already how this repository thinks, and per-column
error tolerance is what section 5.2's third consequence asks for. And the
one-member axis problem dissolves, because a query returning one row is not a
governance object requiring ratification.

**Cost to a shippable state.** Parser columns are $0.00 and reuse the lattice
directly. Model spend equals Option B's residual, approximately **$8 to $14**,
because F and B share a production method and differ in what they write to. The
extra cost over B is schema and migration work on 403 axes and roughly 8,000
memberships, which is engineering, not tokens. Expected precision per column
rather than per card, which is the point. Expected reproducibility 100% on
parser columns.

**What is discarded.** The axis as a governance object is demoted. That is a
large conceptual discard and it touches ratified law: `PARENT-TREE-CANDIDATES.md`
S1–S7 and the naming grammar are both organized around axes.

**The $57.63 SYNTH run-1 output:** worth more under F than under any other
option, because a predicate row wants exactly what run 1 produced. 46,999 rows
carrying `label`, `definition`, `actor_scope` and `evidence_quote` decompose
into predicate cells far more naturally than they consolidate into axes, and the
consolidation plan's failure mode, 2,923 redirect rows creating no membership,
is a symptom of forcing rows into axes.
**The 403-axis codebook and its 4,233 human assertions:** preserved in full and
migrated, not rewritten. Each human assertion becomes a predicate row with
`source: human` and its existing evidence quote; each axis becomes a saved query
whose result set is checked against its former membership, which is a
conservation test of exactly the kind this repository already runs. Any axis
whose query does not reproduce its ratified membership is a finding, not a
silent loss.

**Risk.** F is the largest change proposed here and it asks Captain to
re-open ratified structural law, S1–S7 and the naming grammar, on the strength
of an audit rather than a shipped tool.

**Strongest argument against Option F:** it proposes a migration of the one
asset the project cannot rebuild, 4,233 Captain-ratified human assertions, on
the authority of a document that has not shipped a single tag to a single card.

### 6.7 Summary table

| | token spend to shippable | expected precision | expected reproducibility | discards | headline risk |
|---|---|---|---|---|---|
| A continue | $15 to $35 | 77% measured | 77% measured | nothing | grows a closed loop |
| B DET-first | $8 to $14 | high on 66.6%, unmeasured on residual | 100% on parser fraction | free-lane naming | 66.6% is reach, not precision |
| C slice | under $5 | high by selection | 100% on parsed slice | nothing, defers much | validates only its own shapes |
| D level field | $0 | n/a, schema only | n/a | nothing | queryable closed loop |
| E metadata | $0 | metadata-grade | n/a | forward axis work | concedes 2 of 4 consumers |
| F predicate table | $8 to $14 | per column | 100% on parser columns | axis as governance object | reopens ratified law |

### 6.8 Which is strongest, stated plainly

**F is the strongest destination and B is the strongest next step, and they are
compatible because they share a production method.** B is F executed against the
existing schema. Nothing in B has to be undone to reach F, and B produces the
measurement that would tell Captain whether F is worth its migration risk:
if the parser's precision across 69 verbs holds up the way it held up across
three, the predicate table has columns worth having; if it does not, F is a
schema change in service of data that is not there.

**C is the strongest risk-adjusted choice** and I am not going to pretend
otherwise merely because F is mine. C is the only option that changes the 0 of 5
reachability number on its first delivery.

**D should be taken regardless of which of the others Captain rules for**, in
its free provenance-derived variant, because it costs nothing and it is a
prerequisite for reading any of the other options' results by level.

---

## 7. DIRECT ANSWERS

**1. Is the reference-material burden necessary, or does the pipeline ship
context the task does not consume? Quantify.**

It ships context the task does not consume, and the quantity is exact. The
system block is byte-identical across all 814 requests, 57,115 characters and
approximately 14,279 tokens, against a payload of approximately 3,450 tokens for
40 cards. **The ratio is 4.1 to 1.** More sharply: cache write exceeded cache
read by 4.73 to 1, so 14.0M of the 22.5M input-side tokens, **62% of all input**,
was spent re-writing one unchanging block 814 times. Whether the *content* is
necessary is a separate question this audit did not test, since it would require
an ablation and therefore API calls. The *delivery* of it demonstrably was not.

**2. Is the measured reproducibility a prompt problem, a task-definition
problem, or an inherent property of open-vocabulary labeling? What experiment
distinguishes these?**

The evidence points hard at task definition, and one number carries most of the
weight: **the free lane produced 25,066 distinct labels across 28,243 rows, with
23,278 used exactly once, 92.9% singletons.** A prompt problem does not produce
a label space 62 times larger than the codebook it was extending. Against that,
the same pass was 89.2% reliable at quoting verbatim evidence, so the model was
not failing at reading; it was failing at naming, which is the part the task
definition left open.

The distinguishing experiment is cheap and Captain must authorize it because it
spends money: re-run a sample of the same cards as a **closed-set binary
judgment** against a fixed candidate list, and measure reproducibility. If it
goes to near 100%, the cause is the open vocabulary. If it stays near 77%, the
cause is the judgment itself and Option B's precision claim is wrong. At K=8 on
1,000 cards this is roughly 438,000 tokens, well under $1.

A free proxy already exists and is worth stating: the object lattice is the same
task with a closed vocabulary and it reproduces at 100% by construction. That is
strong but not decisive, because a parser and a model are not the same
instrument.

**3. Do the guards eliminate errors or relocate them? Is there evidence either
way in pass logs?**

There is evidence, and it splits cleanly by guard *kind* rather than by guard.
`docs/SYSTEM-SELF-TEST-2026-08-09.md` measured that every defect class that
received a TOOL stopped recurring, and the one class that received a paragraph
reached 21 instances. So tools eliminate and prose relocates.

But the same self-test found the sharper answer: **two of the eight Gate 2
checks, `foundry_definition_drift.py` and `foundry_ruling_registry.py`, detect a
deliberately introduced fault and exit 0.** They are reporters listed as gates.
And three of the eight negative controls were mis-aimed. So a third of the guard
stack was not known to be a guard until somebody broke it on purpose. That is
error relocation of a specific and dangerous kind: the error moves from the data
into the confidence one has in the check.

This session added a fourth data point in the same family. **Four probe defects
occurred in this audit's own measurement code**, three of which first read as
findings: a dict return value that is always truthy, a `must_capture` predicate
receiving the text element rather than the tuple, a `rule:` prefix mismatch that
scored the codebook lane at 9 live-axis matches when the truth was 13,231, and
two fixture expectations that were wrong about the CR rather than about the code.
The count is not incidental; it is the base rate this repository already
documents, reproduced under audit conditions.

**4. Would retrieving a small candidate axis set per card, instead of carrying
whole-codebook context, change the failure mode? Does the corpus support that
retrieval today?**

Yes to both, with a cost caveat.

**The failure mode changes from unrecoverable to recoverable.** Today the model
invents a label, and 23,278 of those inventions were used once, which cannot be
reconciled after the fact without the 24,834-cluster discovery pass that had to
be built for exactly that reason. Under retrieval the model either picks wrong
from K, which a held-out set detects, or says no to all K, which is an honest
gap and is reportable.

**The corpus supports it today.** 403 active axes carry definitions at median
129 characters, embeddings already ship for Similar Cards, and run 1 is a
working existence proof: its codebook lane made 16,195 assertions against
existing axes and 81.7% named a live active one.

The caveat from 6.0b is real and belongs in the answer: retrieval only saves
tokens if K stays at or below about 16. At K=32 a binary judgment costs more
than the synthesis call it replaces.

**5. Should the codebook have been fixed before the corpus pass rather than
grown during it? Is the answer recoverable from current state, or would it
require a restart?**

Yes, it should have been fixed, and the evidence is the same 92.9% singleton
rate plus the discovery pass's own tally of 141 exact-match reinventions and 18
killed-slug reinventions. A pass allowed to grow its own vocabulary reinvented
names the codebook already had, including names that had been explicitly killed.

**It is recoverable without a restart, and the recovery is already 40% built.**
18,756 codebook-lane and codebook-grammar rows are shaped as card-to-existing-axis
assertions and 14,749 name a live active axis. Those need no re-derivation. The
28,243 free-lane rows are not recoverable as vocabulary but are recoverable as a
candidate pool through the 24,834 discovery clusters. What is genuinely lost is
the naming work, not the evidence work, and since 89.2% of rows carry a verbatim
quote, the expensive part of the pass survives.

**6. Is the current granularity driven by downstream requirement or by the
design's internal logic?**

By internal logic, and section 4.3 already labelled that `INFERENCE`. This
section can now separate the two causes honestly, which the directive asks for.

**The internal cause is compositional.** The ratified slug grammar has five
slots, and a five-slot compositional grammar generates objects at the product of
its slot vocabularies. Median membership of 4, 205 axes under 5 members, 87
singletons and one active axis with zero members are all what a product space
looks like when it is populated by real cards.

**The consumer cause is absent, not weak.** No consumer spec in this repository
names an axis. `foundry_reachability.py` measures 0 of 5 foundry artifacts
reaching a shipped card. Section 4.1 derives that Deck Analyzer wants 8 to 12
coarse roles, which is between one and two orders of magnitude coarser.

There is one honest qualification in the other direction. Fine grain is *correct*
for the parser-decidable layer: `rule:targeted-destroy-artifact` and
`rule:targeted-destroy-creature` are genuinely different facts and Putrefy is
genuinely both. The fine grain is a defect at the *role* layer and a virtue at
the *rules-fact* layer, which is section 5's finding restated: the problem is
that nothing records which layer an axis is on.

**7. What is the highest-leverage change available for under $20 of remaining
budget?**

**The highest-leverage change costs $0, and naming a $20 option first would be
answering a question Captain did not ask.** Ratify the object lattice's DET
pattern. It is built, negative-controlled, and blocked on exactly one approval,
a fixed-seed sample sheet (`docs/OBJECT-LATTICE-2026-08-09.md:246-256`). It
moves corpus coverage from 19.3% to 24.3%, adds 2,653 rule-derived memberships
across 2,131 cards, and does roughly a fifth of what the entire $56.94
consolidation plan would do, at zero marginal cost and re-runnably. It also
needs one structural extension, one matcher to N axes rather than one to one
(`docs/OBJECT-LATTICE-2026-08-09.md:258-263`), which is engineering.

**If money must be spent, the best $1 is the experiment in answer 2**: a
closed-set binary re-run on 1,000 cards, roughly 438,000 tokens, which decides
between Options A and B on measurement rather than on argument. The best
remaining $10 to $14 is Option B's residual pass, and it should not be spent
until that $1 has been.

**And the highest-leverage change of any price is not a tag at all.** It is a
consumer that reads one. 0 of 5 artifacts reach a shipped card; until that is 1,
every number in this document is about the size of a closed loop.

---

## 8. ADVERSARIAL BALANCE

Both cases below were written before the headline finding, as the directive
requires, and neither is a straw man for the other.

### 8.1 THE CASE FOR CONTINUING THE CURRENT ARCHITECTURE

The strongest version of this case does not rest on sunk cost. It rests on the
observation that this project's method is unusually good and its output is
unusually well-guarded, and that both of those are architecture.

Consider what the architecture actually produced. Every classifier derives its
vocabulary from the Comprehensive Rules at run time rather than from a hand-list,
and when a hand-list survives it is tracked as an open defect, which is how D5
and D6 came to be named before they caused damage. Every per-card assignment
carries an evidence quote, and this audit measured that law holding at 89.2%
across 46,999 assertions produced by a model with every incentive to paraphrase.
Every generated artifact is gated on byte-identical determinism. The guard stack
was broken on purpose on 2026-08-09 and six of eight checks caught it, and the
two that did not were identified, named, and written down rather than quietly
left in place. A repository that discovers its own reporters-masquerading-as-gates
is not a repository with an architecture problem.

Consider also that the specific criticisms in this document are criticisms of
sequencing, not of structure. Nothing here says the CR-derived vocabulary is
wrong, that the evidence-quote law is wrong, that the DELIVERY grammar is wrong,
or that the ratified naming rules are wrong. Section 5's central finding is that
a field is *missing*, which is an additive fix to a schema that is otherwise
carrying real information: 291 of 403 axes carry a DELIVERY slot, 278 an EFFECT
slot, 203 an OBJECT slot. Those are not noise; they are the predicates two of the
four consumers need, already extracted, already quoted, already ratified.

Consider the asset. 4,233 Captain-ratified human assertions with evidence quotes
is the single thing in this repository that cannot be rebuilt by any amount of
compute, and it exists because the architecture insisted on human ratification at
every vocabulary boundary. Every option in section 6 that proposes change also
proposes to preserve that asset, which is a tell: the disputed part of the
architecture is the production method, and the production method is the part
that has already been fixed once, by ratifying lane-aware consensus in direct
response to the 77% measurement. That remedy has not yet been given a single
pass to prove itself, and judging an architecture before its own ratified
correction has run is judging it early.

Finally, consider that the alternative options carry unmeasured risk while the
current path carries a measured one. 77% reproducibility is a known number with
a known remedy. Option B's 66.6% ceiling is a reach figure whose precision
nobody has read a sample of, and two of this session's own fixtures failed in
ways nobody predicted. Option F asks to migrate ratified structural law on the
authority of an audit. The current architecture's worst case is a codebook that
is larger and slower to query than it needs to be; the alternatives' worst case
is a migration that damages the one irreplaceable asset. Between a measured
inefficiency and an unmeasured restructuring, continuing is the conservative and
defensible choice, and conservatism is warranted when 4,233 hand-ratified rows
are on the table.

### 8.2 THE CASE FOR CHANGING THE CURRENT ARCHITECTURE

The strongest version of this case is not that the work is bad. It is that the
architecture optimizes a variable nobody downstream reads.

Start with the number that survives every reframing: **0 of 5 foundry artifacts
reach a shipped card**, measured by `experiments/foundry_reachability.py`, while
`codebook.json` carries 26 `experiments/` consumers and 0 `pipeline/` ones. The
tier engine reads no foundry output at all and emits exactly one `rule:` tag,
which it derives itself. 204 commits since 2026-08-01 touched `pipeline/` zero
times. An architecture is a set of choices about what connects to what, and this
one has produced a component that connects to its own tests.

That is not a sequencing accident, because it has now survived a direct attempt
to fix it. `docs/WIRE-RESULT-2026-08-09.md` built the codebook-to-tier-engine
join, and the join worked on the first try: one call site, both controls
byte-identical, the ceiling prediction exact. It still failed, 1 of 3 criteria,
because the derived term does not rank, it partitions into reviewed and
not-yet-reviewed. Axis recall against 33 hand-named correct neighbours was 39%,
and the single axis at 100% recall changed nothing because the engine already
reached those cards at Tier 2 for free. **The codebook is complete exactly where
the engine did not need help.** That is an architectural result, not a coverage
result: it says the thing being produced is not shaped like the thing being
consumed.

Now the production method, measured this session. The corpus pass shipped a
14,279-token instruction block against a 3,450-token payload, a 4.1 to 1 ratio,
and wrote that identical block 814 times at cache-creation rate, burning 62% of
all input tokens on re-transmitting text that never changed. Its free lane
emitted 25,066 distinct labels across 28,243 rows, **92.9% of them used exactly
once**, and reinvented 141 names the codebook already had plus 18 that had been
explicitly killed. The result was a consolidation plan that cannot be applied:
189 rows target 2 axes it never creates, and 2,923 redirect rows create no
membership at all. Nine months of spend produced **zero `llm` memberships in the
live codebook**. That is not a pass that needs a consensus layer; that is a task
definition that generated a vocabulary faster than any consensus layer can
reconcile it.

Against that, the counter-experiment is already on disk and it is unambiguous.
The object lattice derives everything from the CR at run time, produced 2,653
memberships across 2,131 cards, reproduces at 100% by construction, cost $0.00,
caught a real defect on its first sample run, and does roughly a fifth of the
entire $56.94 consolidation plan's coverage gain by itself. And this session's
measurement says it is running at a small fraction of its own ceiling: CR-derived
templated frames reach **66.6% of the corpus**, 19,560 cards beyond the three
families currently wired. The residual, 10,866 cards, is not a judgment tail;
sampling it shows counterspells, damage against CR 120.1's recipient list, mana
production and scry, all of which are templated against closed lists that have
simply not been connected yet.

So the case for changing is this: the expensive method has a measured 77%
reproducibility, a 92.9% singleton rate and zero landed memberships, while the
free method has 100% reproducibility, zero defects across 39 hand-read hits, and
a ten-fold unexploited ceiling. Continuing spends the last $50 making the
expensive method's output larger. Changing spends nothing making the free
method's output reach ten times as many cards, and reserves the model for the
33.4% where it is the only instrument that works.

---

## 11. WHAT I COULD NOT DETERMINE

- Whether the 77% reproducibility figure decomposes by level. Nothing records a
  level, so the figure cannot be split without first labelling a sample. The
  experiment that would settle it is small: label 100 SYNTH-produced axes L0 to
  L3 by hand, then compute reproducibility per level.
- The true level distribution. The rubric is roughly 53% accurate on a
  hand-scored 30 and no better number exists without hand-labelling.
- Retry and correction spend, which is not instrumented anywhere I could find.
  Absence of that instrument is itself a finding, as the directive says.

Added by the sections 6 to 13 pass:

- **Precision of the newly reachable 19,560 cards.** 66.6% is a reach figure.
  Nobody has read a sample outside the destroy, exile and bounce families, and
  the lattice's zero-defect result on 39 hand-read hits does not transfer to 69
  verbs by assertion. The experiment is small and free: emit a fixed-seed sample
  sheet per verb, the way `foundry_object_lattice.py --samples N` already does,
  and read it.
- **Whether the 14,279-token instruction block is necessary in content.** This
  audit measured its size, its byte-identity across all 814 requests and its
  delivery cost. It did not measure whether the model uses it, because an
  ablation requires API calls.
- **The real dollar figure for Options B and F.** The token arithmetic is
  measured; the conversion to dollars assumes run 1's blended rate, and run 1's
  rate is distorted by the 4.73 to 1 cache-write ratio that Option B would not
  reproduce. The number that would settle it is current pricing at the time of
  the run, which the engine rules forbid me from remembering.
- **Whether $57.63 or $56.94 is the correct run-1 figure.**
  `corpus_pass_run1_cost_actual.json` records `real_cost_usd` 56.9397 and this
  document uses that. The $57.63 in `CLAUDE.md` and the audit brief may include
  `corpus_pass_run1_pack198_retry.json`, which I did not price. The difference
  changes no conclusion here.
- **Whether the four probe defects in this session's own measurement code are
  the whole set.** Four were caught by guards or fixtures. The base rate this
  repository documents says the honest expectation is that there are more.
  Partly closed the same day: the reach probe is now
  `experiments/foundry_reach_census.py` and is re-runnable and
  negative-controlled, so its numbers can be checked by anyone. The 6.0b and
  6.0c measurements remain uncommitted. See AQ6.

---

## 12. RECOVERABLE ASSETS

What survives under each option. The two assets the brief requires an explicit
answer for are marked.

### 12.1 The $56.94 SYNTH run-1 output

46,999 assertions over 32,557 cards, 100% carrying an evidence quote, 89.2% of
those quotes verbatim in the card's own `det_scan_texts` output. Structurally it
is three different assets wearing one filename.

| component | size | condition |
|---|--:|---|
| `codebook` lane | 16,195 rows | 81.7% name a live active axis |
| `codebook-grammar` lane | 2,561 rows | 53.0% name a live active axis |
| `free` lane | 28,243 rows | 25,066 distinct labels, 92.9% singletons |
| verbatim-quoted rows | 41,896 | usable as explanation text as-is |
| non-verbatim rows | 5,095 | a ready-made negative control |
| discovery clusters | 24,834 | the free lane, reconciled |

| option | what happens to it |
|---|---|
| A | retained in full, is the input to the consolidation apply once the 189-row halt clears |
| B | **repurposed and worth the most here**: 18,756 rows are already binary-judgment shaped and become the retrieval evaluation set; the free lane survives as a candidate pool via the 24,834 clusters, not as vocabulary |
| C | unused unless the slice happens to cover it; the honest weak point of C |
| D | untouched; D says nothing about it |
| E | **discarded as a production input**, retained as an explanation corpus, where the 41,896 verbatim rows are the asset and the idiosyncratic labels stop being a liability |
| F | decomposes into predicate cells more naturally than it consolidates into axes; the highest-value use of the four fields it already carries |

**The component that is unrecoverable under every option is the free lane's
naming**, 25,066 labels of which 23,278 appear once. No option in this document
proposes to reconcile them into vocabulary, because the discovery pass already
tried and produced 24,834 clusters, which is not a reconciliation.

### 12.2 The 403-axis codebook and its 4,233 human assertions

Live membership provenance is 4,233 `human` plus 3,697 `rule-derived` plus zero
`llm`. The human rows are the only thing here that compute cannot rebuild.

| option | what happens to it |
|---|---|
| A | retained and grown; A8 already protects human rows from any DET refresh |
| B | **promoted from output to input**, becoming the retrieval target; this is the option under which the 4,233 are worth the most, because every one of them becomes a candidate the model is asked to confirm rather than one contributor among many |
| C | frozen, read by the slice, not extended |
| D | untouched and made queryable by level, which is the only thing D does and the only option that improves the existing codebook without changing production |
| E | frozen as a read-only explanation dictionary |
| F | **migrated, not rewritten**: each human assertion becomes a predicate row with `source: human` and its existing quote, and each axis becomes a saved query whose result set must reproduce its ratified membership or be reported as a finding |

**No option discards the 4,233.** That unanimity is itself a result: the disputed
question is the production method, not the ratified record.

### 12.3 Assets nobody has counted as assets

- **The guard stack.** 13 gates, negative-controlled on 2026-08-09, survives
  every option unchanged, and is the reason an architecture change is safe to
  attempt at all. Under B and F it gains a job: the conservation and determinism
  gates are exactly the instruments a migration needs.
- **`experiments/foundry_probe.py`.** Four probe defects occurred in this
  session's own code and the module's guards caught two of them outright. It is
  the cheapest asset here and the most reused.
- **The object lattice module.** Built, negative-controlled, blocked on one
  approval. Under A it is a nice addition; under B, C and F it is the
  calibration point for the entire production method.
- **The 89.2% verbatim rate itself.** It is the measurement that separates what
  the model is good at, reading and quoting, from what it is bad at, naming, and
  it was free.

---

## 13. OPEN QUESTIONS FOR CAPTAIN

Labelled "AQ1" to "AQ9" rather than plain "Q" numbers on purpose. The first
draft used the bare letter, and `foundry_ruling_registry.py` ingested all nine
as ruling identifiers, making this document the sole home of a ruling that does
not exist (`experiments/foundry_ruling_registry.py:55`, `SHORT_ID` matches one
of "ADQSTMRFG" followed by digits). That is the house's own "a markdown document
is an API" trap, caught by a gate rather than by review.

**And the first sentence written to explain it re-introduced it**, because the
illustrative identifier was typed in backticks and the registry harvests
backticked identifiers from prose. Rejected and illustrative terms go in
quotes, never in backticks. Second instance of that specific correction in the
repository's record, and the first one outside grammar §2.

Every one of these needs a ruling. Options and tradeoffs are laid out; none
carries a recommendation, and where this document argued a position elsewhere,
that argument is not repeated here.

**AQ1. Ratify the object lattice DET pattern, or hold it?**
It is blocked on one fixed-seed sample sheet. Ratifying moves coverage 19.3% to
24.3% at $0.00 and adds 2,653 rule-derived memberships.
*Tradeoff:* it also requires the schema extension at
`docs/OBJECT-LATTICE-2026-08-09.md:258-263`, one matcher to N axes, which is new
DET machinery and therefore new surface. Holding keeps the machinery simple and
leaves 1,637 cards untagged that nothing else tags.

**AQ2. Does the model author labels, or adjudicate candidates?**
This is the architecture question underneath Options A and B.
*Tradeoff:* authoring covers the residual with no retrieval infrastructure and
has a measured 92.9% singleton rate. Adjudicating has a recoverable failure mode
and 100% reproducibility on the parser fraction, but its cost advantage
disappears above about K=16 candidates, and its 66.6% ceiling has never been
precision-checked outside three verb families.

**AQ3. Spend roughly $1 on the discriminating experiment before ruling AQ2?**
A closed-set binary re-run on 1,000 already-labelled cards, approximately
438,000 tokens, would show whether reproducibility rises from 77% toward 100%
when the vocabulary is closed.
*Tradeoff:* it delays the ruling by one session and spends real budget on a
measurement rather than on output. Against that, ruling AQ2 without it means
choosing between a measured 77% and an unmeasured claim.

> **NOTE ADDED 2026-08-13 — FL-2 IS RESOLVED AND DID NOT DECIDE AQ4 OR AQ5.**
> Semantic locality was ratified and implemented (canonical ruling:
> `docs/B-MIGRATION-DISCOVERY.md` §11). An assertion may now carry an optional
> `locality: [face, paragraph]` address. **AQ4 and AQ5 below remain open and
> are not pre-committed by it** — FL-2 addresses *where a fact lives*, AQ4
> addresses *what a fact asserts*. The FL-2 packet had recommended folding the
> two together for exactly that reason; ratification separated them instead,
> which leaves AQ4 as open as it was. Nothing in AQ4's tradeoff below has
> changed: the axis is still the primary object, S1–S7 still holds, and the
> human assertions are still filed under it.

**AQ4. Is the axis the right primary object, or is the predicate row?**
Option F versus everything else.
*Tradeoff:* the axis is ratified law, S1–S7 and the naming grammar are built on
it, and 4,233 human assertions are filed under it. The predicate row fixes
magnitude, deck role and level in one change instead of three, and dissolves the
87 single-member axes. Migrating is the largest risk in this document; not
migrating means magnitude and role stay absent, and section 4.4 measured that
Budget Swapper is both the lowest-tolerance consumer and the worst-served one.

**AQ5. Add a `level` field, and if so, derived from `source` or assigned per
axis?**
*Tradeoff:* deriving from `source` is free and correct by provenance but only
splits DET-owned from human-owned, 39 against 364, not the full four-way split.
Assigning per axis gives consumers the subset they need but the rubric this
audit built agreed with hand-scoring on roughly 16 of 30, so per-axis means 403
hand rulings.

**AQ6. Should this session's measurement scripts be committed?**
**Partly answered by Captain's instruction to proceed, and acted on.** The reach
probe is committed as `experiments/foundry_reach_census.py`, reproduces 6.0a
exactly, and passes three negative controls. It is deliberately NOT wired into
`foundry_gate2.py`.
*What is still open:* whether it should be RATCHETED. It emits `--json` for
`foundry_audit_baseline.py`, and pinning it would make it a real gate rather
than a reporter, which is the only thing that stops the 66.6% decaying into
another carried-forward count.
*Tradeoff:* a ratchet on reach makes any change that narrows a frame fatal,
which is correct when the frames are right and obstructive while they are still
being widened. Left unpinned it is one more tool in a repository whose §0
finding is that it has too many tools that reach no card.
*Also still open:* the 6.0b prompt-economics and 6.0c recyclability probes are
uncommitted, and their numbers are carried-forward counts today.

**AQ7. Which consumer is first, and does that ruling come before or after AQ2?**
Section 4 derived four consumer specs from tool descriptions because no consumer
spec in this repository names an axis.
*Tradeoff:* ruling the consumer first makes Option C available and gives every
other option a target, but it commits the project to one tool's predicate needs
before the substrate exists. Ruling AQ2 first keeps the substrate general, and
repeats the sequencing that produced 0 of 5 reachability.

**AQ8. What is the disposition of the unappliable consolidation plan?**
189 rows target 2 axes it never creates and 2,923 redirect rows create no
membership.
*Tradeoff:* repairing it recovers a path to 48.0% coverage from spend already
made. Retiring it writes off the $56.94 as a production input and makes run 1 a
test set instead, which is the assumption Options B and F are costed under. This
document did not attempt the repair and does not know its size.

**AQ9. Does the 4.1 to 1 instruction-to-payload ratio get an ablation?**
The delivery waste is proven, 62% of input tokens re-writing an identical block.
The content necessity is not tested.
*Tradeoff:* an ablation costs API calls and would tell us how much of the
14,279-token block any future pass needs to carry. Skipping it means any new
pass inherits the block by default, because nobody can say which part is
load-bearing.
