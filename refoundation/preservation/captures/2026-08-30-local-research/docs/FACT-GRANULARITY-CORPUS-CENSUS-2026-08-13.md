# FACT GRANULARITY — corpus-wide census before semantic-locality implementation

**2026-08-13.** Read-only. No schema, no locality field, no migration, no axes,
no DET apply, no codebook mutation, no API calls, no vocabulary. Gate 2 green
(14 gates, 13 pass, 1 known-excused).

**Corpus:** `load_corpus_gated()`, **32,557** cards; **32,217** carry oracle
text on some face. All faces, all paragraphs, no truncation, full local scan.

**Shipped artifact changed: NONE.**

---

# A. VERDICT — **PROCEED WITH LOCALITY FIRST**

The corpus is far more qualified than the current fact layer records, and that
is an argument **for** the ratified locality design, not against it. Nothing
measured requires changing the semantic-owner coordinate before implementation.

The owner is precisely where qualifiers will later attach, and the census found
no shape where a qualifier belongs somewhere a paragraph-level owner cannot
reach. Option B (locality + a minimal qualifier substrate now) is **rejected on
evidence**: qualifier vocabulary is itself unratified, and minting it inside a
locality implementation would smuggle a ratification through a plumbing change.

---

# B. EXECUTIVE SUMMARY — how granular the corpus actually is

- **90.4%** of cards carrying oracle text (29,112 / 32,217) carry at least one
  restriction category.
- **30.0%** carry **four or more** independent restriction categories.
- Within the one family Foundry can classify deterministically today — the
  object lattice — **41.5% of classified clauses (992 / 2,389)** carry an
  eligibility qualifier **beyond** the base object class.
- Qualification is **increasing with time**: mean restriction categories per
  card runs **0.85 → 0.95 → 1.02 → 1.39** across four release eras.
- Encoding those qualifiers as compound slugs would multiply the lattice's
  **23** class axes into **166** observed combinations — **×7.2**, measured, on
  seven coarse categories in one family.

**Active Volcano-like incompleteness is common, not rare.** It is the majority
condition for creature removal (56–63% restricted) and the minority-but-large
condition overall.

---

# C. CURRENT REPRESENTATION INVENTORY

| dimension | status today | where |
|---|---|---|
| action / effect | **direct** | §4 EFFECT verbs |
| object class | **direct** | §5 `OBJECT_VOCAB`; object lattice |
| target presence | **direct** | §6a — the printed word `target` is required (CR 601.2c) |
| controller / owner scope | **direct** | §6 `SCOPE_VOCAB` (`you-control`, `you-own`, `opponent`, `each`, `defending-player`, `enchanted-player`) |
| timing / activation restriction | **direct** | §3 + §3a, closed and DET-owned; `RESTRICTION_VOCAB` parsed from §13 |
| delivery / ability kind | **direct** | §2, 52 closed tokens |
| source / destination zone | **compound only** | inside slugs like `to-graveyard-from-library-trigger` |
| scaling | **direct** | §7 `-scales-with-<stat>` |
| counter / token type | **direct** | §8 |
| optionality, cost | **partial** | `QUALIFIER_VOCAB` has `cost`, `activation`, `additional` |
| **magnitude** | **NOT represented** | absent from all 403 active axes (ARCHITECTURE-AUDIT §4) |
| **colour restriction** | **NOT represented** | quote-only |
| **state restriction** (tapped/attacking/counters) | **NOT represented** | quote-only |
| **numeric threshold** (mana value / power / toughness) | **NOT represented** | quote-only |
| **negated type** on the target | **compound only** | `nonland-permanent` is a class, not a qualifier |
| supertype (legendary/basic/snow/token) | **NOT represented** | quote-only |
| deck role | **NOT represented** | AQ5 |
| semantic level | **NOT represented** | AQ5 |

Card metadata (own mana value, colour identity, type line, legality, price,
rarity) lives outside the foundry and is **not** duplicated here. *A card being
blue is a different fact from an effect that only targets blue permanents* —
the census counts only the latter.

---

# D. MISSING DIMENSION INVENTORY

Recoverable **only from the evidence quote** today, in prevalence order within
the lattice: **controller** (17.7% of clauses — partially recoverable via §6
scope on some axes), **numeric threshold** (8.7%), **negated type** (6.6%),
**state** (5.7%), **subtype** (5.7%), **colour** (2.5%), **supertype** (0.4%).

---

# E. CORPUS-WIDE RESTRICTION PROFILE — 32,217 cards with oracle text

| category | cards | % |
|---|--:|--:|
| timing | 11,584 | 36.0% |
| zone | 11,015 | 34.2% |
| conditional | 10,923 | 33.9% |
| controller | 9,344 | 29.0% |
| state | 8,763 | 27.2% |
| optional | 7,948 | 24.7% |
| duration | 6,070 | 18.8% |
| cost | 6,034 | 18.7% |
| colour | 4,186 | 13.0% |
| supertype | 4,165 | 12.9% |
| numeric | 3,763 | 11.7% |
| negated type | 2,077 | 6.4% |
| modal | 876 | 2.7% |

Categories per card: 0 → 9.6% · 1 → 16.5% · 2 → 22.9% · 3 → 20.9% ·
**4+ → 30.0%**. **90.4% carry at least one.**

*Card-level counts; a card may appear in several rows. These are broad text
classes, deliberately looser than §F's clause-scoped measurement.*

---

# F. OBJECT-LATTICE QUALIFIER CENSUS — the clause-accurate number

**2,389 classified clauses** (destroy 1,482 · exile 553 · bounce 354).

| qualifiers beyond the base object class | clauses | % |
|---|--:|--:|
| 0 | 1,397 | 58.5% |
| 1 | 859 | 36.0% |
| 2 | 128 | 5.4% |
| 3+ | 5 | 0.2% |

> **992 of 2,389 = 41.5% carry at least one qualifier.**

| category | clauses | % |
|---|--:|--:|
| controller | 424 | 17.7% |
| numeric | 208 | 8.7% |
| negated type | 157 | 6.6% |
| state | 137 | 5.7% |
| subtype | 135 | 5.7% |
| colour | 60 | 2.5% |
| supertype | 9 | 0.4% |

Top combinations: controller 316 · numeric 157 · negated-type 120 · state 109 ·
subtype 96 · colour 54 · controller+numeric 36 · controller+subtype 31.

**Two probe defects were found and corrected before these numbers were
believed.** A first pass reported 47.1% because (1) it counted `nonland` as a
qualifier on `nonland-permanent`, where it **is the base class** — inflating
that row to a false 100% — and (2) a `relative` class matching `with \w+`
double-counted 126 `numeric` clauses. The class's own words are now stripped
before matching, and the overlapping class was removed. Both are the recorded
overlapping-class and denominator defect families.

---

# G. FALSE-EQUIVALENCE PRESSURE

| broad fact | total | unrestricted | restricted | % |
|---|--:|--:|--:|--:|
| `targeted-exile-creature` | 355 | 131 | 224 | **63.1%** |
| `targeted-destroy-creature` | 659 | 289 | 370 | **56.1%** |
| `targeted-exile-nonland-permanent` | 81 | 36 | 45 | 55.6% |
| `targeted-bounce-creature` | 193 | 117 | 76 | 39.4% |
| `targeted-exile-artifact` | 88 | 55 | 33 | 37.5% |
| `targeted-destroy-land` | 164 | 112 | 52 | 31.7% |
| `targeted-exile-enchantment` | 69 | 48 | 21 | 30.4% |
| `targeted-bounce-permanent` | 56 | 40 | 16 | 28.6% |
| `targeted-destroy-planeswalker` | 67 | 49 | 18 | 26.9% |
| `targeted-bounce-nonland-permanent` | 85 | 65 | 20 | 23.5% |
| `targeted-destroy-artifact` | 461 | 382 | 79 | 17.1% |
| `targeted-destroy-enchantment` | 333 | 282 | 51 | 15.3% |

**Creature removal is where the danger concentrates.** A Budget Swapper
comparing only `targeted-destroy-creature` would treat 370 restricted cards as
interchangeable with 289 unrestricted ones. Artifact and enchantment removal are
comparatively safe (15–17%), because those effects are usually printed
unconditionally.

---

# H. CONSTRAINT-COUNT DISTRIBUTION

Neutral census label, deliberately **not** "level" (that term is AQ5's).
Clause-scoped: §F. Card-scoped: §E. The hypothesis that highly qualified effects
are common rather than exceptional is **supported at card level** (90.4% carry
one, 30% carry 4+) and **partially at clause level** (41.5%) — most single
clauses stay simple; most cards do not.

---

# I. CALIBRATION SHAPES — corpus frequency

| shape | cards | % corpus |
|---|--:|--:|
| "target … you control" | 1,858 | 5.71% |
| "target … an opponent controls" | 693 | 2.13% |
| creature card in a graveyard | 535 | 1.64% |
| target nonland permanent | 297 | 0.91% |
| target attacking/blocking creature | 227 | 0.70% |
| target artifact or enchantment | 178 | 0.55% |
| power/toughness threshold | 91 | 0.28% |
| colour-restricted target | 68 | 0.21% |
| target tapped creature | 64 | 0.20% |
| mana-value-limited removal | 42 | 0.13% |
| token/nontoken restriction | 24 | 0.07% |
| counter-bearing target | 20 | 0.06% |

All twelve are **deterministically extractable from Oracle grammar** — an
explicit adjective, a printed CR term, or a comparison phrase. None needs model
judgment. Controller restrictions are the highest-value target by volume;
mana-value-limited removal is the highest-value per card for a Budget Swapper
despite being rare.

---

# J. ACTIVE VOLCANO — calibration walkthrough

```
(0,0)  Choose one —
(0,1)  • Destroy target blue permanent.
(0,2)  • Return target Island to its owner's hand.
```

| fact | represented today? |
|---|---|
| card is modal, choose one | **yes** — `rule:modal`, whole-span owner |
| destroy targets a permanent | **yes** — `rule:targeted-destroy` at (0,1) |
| **destroy target must be BLUE** | **no** — quote-only; deterministic (colour adjective) |
| bounce targets a land | not yet asserted — lattice output, resolves to (0,2) |
| **bounce target must be an ISLAND** | **no** — quote-only; deterministic (CR 205.3 subtype) |
| destination is owner's hand | **compound only** — inside the `bounce` stem |
| the two modes are mutually exclusive | **derived** from the (0,0) header |

Classification: *blue* and *Island* are **qualifiers** on the target, not object
identity (the object classes are `permanent` and `land`) and not modal
structure. Both are deterministic. Neither exists as ratified vocabulary today,
so both would need Captain ratification before being minted.

---

# K. DETERMINISTIC EXTRACTABILITY

| producer class | dimensions |
|---|---|
| **deterministic from Oracle grammar** | colour, negated type, controller, state, numeric threshold, supertype, zone, duration, optionality |
| **deterministic with CR tables** | subtype → permanent type (CR 205.3g–q, already consumed), keyword meaning, defined game terms |
| **requires structural linking** | "that creature", "if you do", modal-header inheritance, shared target across sentences |
| **requires model judgment** | functional role, gameplay outcome, synergy — **none of the qualifier dimensions measured here** |

**Every qualifier dimension this census measured is deterministic.** No LLM is
required to recover any of them.

---

# L. COMPOUND-AXIS EXPLOSION — measured

| | |
|---|--:|
| lattice broad class axes today | 23 |
| distinct (class × qualifier-combo) **observed in corpus** | **166** |
| multiplier | **×7.2** |

That is one family, seven coarse categories, and only combinations that
**actually occur**. The codebook already shows the strain: of 403 active axes,
**52 carry six or more hyphen segments** and the longest run to nine —
`rule:death-trigger-token-count-scales-with-graveyard-creature-count`.

**Conclusion: high-granularity facts should be compositional, not encoded into
ever-longer compound slugs.** Evidence for AQ4; not its resolution.

---

# M. FUTURE-PROOFING — measured, not asserted

`released_at` is present on all 32,217 carded cards.

| era | cards | mean restriction categories/card |
|---|--:|--:|
| 1993–2003 | 3,780 | 0.85 |
| 2004–2013 | 5,111 | 0.95 |
| 2014–2020 | 7,547 | 1.02 |
| **2021+** | **15,779** | **1.39** |

Modern cards carry **~63% more** restriction dimensions than the oldest cohort,
and the modern cohort is **49% of the corpus**. A minimal fact system becomes
**more** lossy over time, not less.

---

# N. SEMANTIC-LOCALITY COMPATIBILITY

**The ratified owner coordinate can host every dimension measured here.**

Every qualifier found is printed **inside the same paragraph as the effect it
restricts** — "blue" sits in the same bullet as "Destroy target", "you control"
in the same clause as its object. A paragraph-level owner is therefore the
correct attachment point, and no measured shape needs a finer or coarser one.

Two consequences worth stating:

1. **Qualifiers do not force child effects.** They restrict the *target* of an
   effect, not a sub-effect, so they attach to the unit that owns the fact.
2. **Locality is a precondition for qualifiers, not an alternative.** A "blue"
   qualifier on a modal card is only safe once it is bound to bullet (0,1) —
   otherwise it flattens onto the whole card exactly as the facts do today.

**No measured corpus shape requires changing the semantic-owner design.**

---

# O. AQ4 IMPLICATIONS — evidence only

The missing granularity is **mixed, and the mix is measurable**:

- **Axes remain right** for base action + object class (23 lattice axes cover
  2,389 clauses cleanly) and for closed families the grammar already
  enumerates (§3 restrictions, §2 delivery).
- **Predicates/facets look right** for qualifiers: ×7.2 combinatorial growth in
  one family on seven categories, against 52 axes already at 6+ segments.

That is evidence that the eventual answer is **both**, not a wholesale
migration. **AQ4 is not resolved here.**

---

# P. RECOMMENDED IMPLEMENTATION SEQUENCE

1. **Semantic locality**, exactly as ratified — unchanged by this census.
2. **Then** bring a qualifier-vocabulary ratification packet, scoped to the
   deterministic dimensions in §K, ordered by measured prevalence
   (controller → numeric → negated type → state → subtype → colour).
3. **Then** decide AQ4 with §L's explosion number in hand.

Steps 2 and 3 are **not** authorised by this census.

---

# Q. CAPTAIN DECISIONS

**None created by this census.** The one decision it implies — whether
qualifiers become orthogonal facets or more axes — is **AQ4**, already open, now
better evidenced. Minting qualifier vocabulary is a ratification and is
deliberately not requested inside a locality implementation.

---

# R. SIDE FINDINGS, ROUTED

1. **Two probe defects in this census**, found and corrected before publication
   (base-class double-count; overlapping `relative` class). Recorded because the
   first-pass 47.1% would otherwise have entered a document as fact.
2. **Carried forward, still open:** 13 memberships on
   `rule:grants-trample-to-creatures-with-counters` contradict its definition
   (`SEMANTIC-ADDRESS-PREIMPLEMENTATION-CHECK-2026-08-13.md` §14). Correctness
   path, not this one.
3. **Gate 2 runs in no CI.** Unchanged, unfixed, still relevant to every guard.

---

# S. THE TEN QUESTIONS, ANSWERED

1. **Common** — 41.5% of lattice clauses, 90.4% of cards.
2. **41.5%** of classified lattice clauses carry ≥1 qualifier (992/2,389).
3. Controller 17.7% · numeric 8.7% · negated type 6.6% · state 5.7% · subtype 5.7% · colour 2.5%.
4. Action, object class, target presence, controller scope, timing/activation restriction, delivery, scaling, counter/token type.
5. Magnitude, colour, state, numeric thresholds, supertype, deck role, semantic level.
6. **Yes** — every qualifier is printed in the same paragraph as the effect it restricts.
7. **No** — ×7.2 measured in one family; 52 axes already at 6+ segments.
8. **Yes** — orthogonal facets, on §L's evidence.
9. **No.**
10. Locality first, unchanged → qualifier-vocabulary packet → AQ4.

---

# T. GIT STATE

```
 M docs/PICK-UP-HERE.md
 M docs/RATIFIED-RULINGS-REGISTRY.md
 M docs/det-patterns-v2.json
 M experiments/foundry_audit_baseline.py
 M experiments/foundry_det_pass.py
 M experiments/foundry_gate2.py
 M experiments/foundry_object_lattice.py
?? docs/CANONICAL-SEMANTIC-UNIT-DECISION-PACKET-2026-08-13.md
?? docs/FACT-GRANULARITY-CORPUS-CENSUS-2026-08-13.md
?? docs/FULL-CARD-INFORMATION-CONSERVATION-2026-08-13.md
?? docs/OBJECT-LATTICE-RESIDUAL-RULING-2026-08-13.md
?? docs/SEMANTIC-ADDRESS-ARCHITECTURE-REVIEW-2026-08-13.md
?? docs/SEMANTIC-ADDRESS-PREIMPLEMENTATION-CHECK-2026-08-13.md
?? docs/THESAURUS-FACT-LAYER-ARCHITECTURE-2026-08-13.md
```

No commit.
