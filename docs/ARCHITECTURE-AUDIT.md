# T3 AXIS FOUNDRY — ARCHITECTURE AUDIT (PARTIAL)

**Scope: sections 4 and 5 of `ARCHITECTURE-AUDIT-DIRECTIVE.md` only**, at
Captain's instruction 2026-08-12. Consumer requirements derived backward, and
level analysis. Phase One inventory, Phase Four options and Phase Five direct
answers are NOT in this document.

Zero mutation: nothing was created, edited or deleted except this file.
No API calls. Codebook sha256 `b4197e94…`, unchanged.

**Note on the directive's stated state (§2).** Three of its six "believed true"
items are already false and a session running the full directive would spend
tokens rediscovering that: the codebook is 403 active / 615 total rather than
"roughly 455"; `det-patterns-v1.json` was superseded by v2 on 2026-08-01; and
B-MIGRATION is described as "queued, not executed" but executed 2026-08-01,
which is why the codebook is schema `foundry-codebook/2`. Spend at roughly $90
of $140 is correct.

---

## HEADLINE FOR THESE TWO SECTIONS

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

## WHAT I COULD NOT DETERMINE

- Whether the 77% reproducibility figure decomposes by level. Nothing records a
  level, so the figure cannot be split without first labelling a sample. The
  experiment that would settle it is small: label 100 SYNTH-produced axes L0 to
  L3 by hand, then compute reproducibility per level.
- The true level distribution. The rubric is roughly 53% accurate on a
  hand-scored 30 and no better number exists without hand-labelling.
- Retry and correction spend, which is not instrumented anywhere I could find.
  Absence of that instrument is itself a finding, as the directive says.
