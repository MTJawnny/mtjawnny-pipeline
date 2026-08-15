# AQ4 — PRE-IMPLEMENTATION ADVERSARIAL CORRECTIONS

**2026-08-14. Read-only.** Narrow adversarial review of three load-bearing
claims in `docs/AQ4-CROSS-CARD-NORMALIZATION-ARCHITECTURE-ADDENDUM-2026-08-14.md`
(plus two related checks), before they become benchmark assumptions. Neither
prior AQ4 addendum is overwritten. No code changed, no codebook mutation, no
Gate 2 / P3 / C6 change, no vocabulary minted, no decision ID created,
nothing implemented, nothing ratified.

**Scorecard up front:** of the five challenged conclusions — one **survives**,
one **survives with qualification**, two are **amended**, one is
**withdrawn**. Two of the attacks land because they are recorded repository
traps aimed at my own design, which is exactly what an adversarial pass is
for.

---

# A. SCOPE AND CURRENT-STATE CONFIRMATION

Operational state is healthy and **not under review**: codebook SHA-256
`6aa6193f8a457ae4c7884e364f519749a9d68b96f7ecedf3fa903bfa4677426c`,
5,066,147 bytes, 7,808 stored locality fields, Gate 2 GREEN (16 rows / 15
pass / 1 known-excused `family_sweep` on the exact W6 fingerprint / 0
unexpected). Verified live earlier this same session by direct hash, size,
and field count; the locality incident is closed and appears below only
where it is historical evidence.

Scope: Challenge 1 (complement normalization), Challenge 2 (ABSENT-PROVEN),
Challenge 3 (holdout redraw), Challenge 4 (entity context), Challenge 5
(ownership neutrality). Everything else in the two prior addenda is out of
scope and unchanged.

---

# B. CHALLENGE 1 — COMPLEMENT/NEGATION NORMALIZATION

## B.1 Verdict: the attack lands. The prior formulation conflated two
semantics on multivalued dimensions.

The prior addendum wrote: *"`nonland` = the CR 205.2a type list minus
`land`,"* a complement-valued set, with comparison by set inclusion. That
formulation never stated its satisfaction semantics, and on a
**multivalued** dimension the two candidate readings diverge exactly as the
challenge predicts:

- **NOT_HAS(land):** `land ∉ types(object)`.
- **HAS-some-of-complement:** `types(object) ∩ (ALL ∖ {land}) ≠ ∅`.

Worked through the mandated cases, with the printed rule as referee:

| restriction | object | NOT_HAS | HAS-complement | correct |
|---|---|:--:|:--:|---|
| nonland permanent | Darksteel Citadel (artifact **land**) | excluded ✓ | **included ✗** | excluded — an artifact land *is* a land |
| nonblack creature | white-**black** creature | excluded ✓ | **included ✗** (has white) | excluded — its colour set contains black |
| noncreature permanent | uncrewed Vehicle (artifact) | included ✓ | included ✓ | included |
| nonartifact permanent | artifact creature | excluded ✓ | **included ✗** (has creature) | excluded |

**HAS-complement is wrong on every multivalued case; NOT_HAS is right on
all of them.** If my complement set is read with subset semantics
(`types(object) ⊆ complement`) it is equivalent to NOT_HAS and correct —
but a formulation whose correctness depends on an unstated membership mode
is the defect, not a defense.

## B.2 A second, independent reason to drop the complement encoding

A stored complement is materialized over a **growing** vocabulary. CR
205.2a gained `battle` in 2023; any complement set stored before that day
silently became wrong the day after — no text changed, no card changed,
and no diff would fire. **A stored complement over an open-ended-in-time
vocabulary is a carried-forward count wearing set clothing** — the exact
trap class this repository has now recorded against itself three times.
`FORBIDS(land)` stores what the card says — one value, one atom — and is
stable across every CR vocabulary refresh.

## B.3 The minimum correction: three constraint atoms, no formula negation

Constraints on a dimension are typed atoms with explicit semantics over the
object's **value set**:

```
REQUIRES(dim, v)      v ∈ values(object, dim)       "blue permanent", "artifact creature"
FORBIDS(dim, v)       v ∉ values(object, dim)       "nonland", "nonblack", "another" (excludes self)
CARD(dim, op, n)      |values(object, dim)| op n    "monocolored"(=1), "multicolored"(≥2), "colorless"(=0)
```

plus the already-specified interval atoms for numeric thresholds and
relation atoms for controller/owner. The mandated cases, restated:

- `nonland permanent` → base `permanent` ∧ `FORBIDS(type, land)`
- `nonblack creature` → `REQUIRES(type, creature)` ∧ `FORBIDS(colour, black)`
- `artifact creature` → `REQUIRES(type, artifact)` ∧ `REQUIRES(type, creature)` (CR 300.2)
- `monocolored` → `CARD(colour, =, 1)` — genuinely needs cardinality; no
  REQUIRES/FORBIDS combination expresses it
- `colorless` → `CARD(colour, =, 0)` (equivalent to five FORBIDS only
  because the colour vocabulary is closed; CARD is the evidence-faithful
  canonical form)

**Negation is thereby confined to the atom** — `FORBIDS` asserts
non-membership of one named value and can never negate a formula. The
algebra keeps its "small and closed" property: entailment and disjointness
remain per-dimension rules —

- `REQUIRES(v)` entails `REQUIRES(v)`; `FORBIDS(v)` entails `FORBIDS(v)`;
  adding any atom narrows (monotonicity unchanged).
- `REQUIRES(v)` vs `FORBIDS(v)`, same dimension → **disjoint**.
- `REQUIRES(v₁)` vs `REQUIRES(v₂)`, v₁≠v₂ → disjoint **iff the dimension's
  contract says single-valued** (controller: yes; type, colour: no — CR
  300.2, multicolour).
- Hierarchy: `REQUIRES(subtype, Island)` entails `REQUIRES(type, land)`
  upward, and `FORBIDS(type, land)` entails `FORBIDS(subtype, Island)`
  downward — both from the existing CR 205.3 subtype→type map (EXTRACT-3),
  applied in opposite directions.

**Answers to the challenge's three questions:** (1) as previously described
— not safely correct; correct only under an unstated subset reading.
(2) n/a. (3) the atom model above, which also repairs the CR-growth
fragility the challenge did not raise.

---

# C. DIMENSION SEMANTIC CONTRACTS

The challenge's closing question — is the dimension-exclusivity registry
sufficient? — **No.** A single exclusive/non-exclusive bit cannot drive the
entailment rules in §B.3. The registry is superseded by a **per-dimension
semantic contract**, still ~10 rows, still one-time ratified, still zero
growth exposure, but with richer columns:

| dimension | value vocab (CR source) | valued | exhaustive? | hierarchy | CARD atoms allowed | applicable entity contexts (§G) |
|---|---|---|---|---|---|---|
| type | CR 205.2a | **multi** (CR 300.2) | yes (≥1 type) | via subtype map | rarely | all kinds |
| subtype | CR 205.3g–q | multi | no | → type | no | all kinds |
| supertype | CR 205.4a | multi | no | none | no | all kinds |
| colour | CR 105.1 | **multi** | **no** (colourless exists) | none | **yes** | all kinds |
| controller | — (relational) | **single** | yes on battlefield/stack | none | no | **permanent, spell only** |
| owner | — (relational) | single | yes | none | no | all kinds |
| tapped/untapped | CR 110.5-family | single, binary | yes | none | no | permanent only |
| token/nontoken | CR 111 | single, binary | yes | none | no | permanent only |
| numeric (power/toughness/MV) | intervals | single per stat | varies | none | n/a | per stat's context |

*(Row content is illustrative of the contract **shape**; every cell is an
implementation-time CR verification, and the sheet is a Captain
ratification — as the prior addendum already required for the registry it
replaces.)*

The contract is what makes the algebra's per-dimension rules **derivable
instead of intuited** — the CR 300.2 row is the standing proof that
intuition fails here (types feel exclusive and are not), and the
`applicable contexts` column is forced by §G (a card in a graveyard has an
owner and no controller — statically knowable, no game state).

---

# D. CHALLENGE 2 — DOES EMPTY RESIDUE PROVE ABSENCE?

## D.1 Verdict: the attack lands, and it is a recorded repository trap
aimed at my own mechanism.

CLAUDE.md, verbatim: *"CONSERVATION IS STRUCTURAL AND CANNOT SEE CONTENT.
Interleave conservation passes a GREEDY `\(.*\)` that eats every character
between the first `(` and the last `)` — kept + removed still reassembles
perfectly."* My residual-exhaustion rule is that trap rebuilt one layer up:
a template with an open capture — `target <noun-phrase>` — consumes
`target creature with flying` completely, emits `object_class = creature`,
leaves **zero residue**, and the flying restriction is gone. Text was
conserved; meaning was not. Every mandated test case breaks the naive rule
the same way if the object slot is an open capture: `tapped`,
`you control`, `another`, `with power 2 or less`, `card in your graveyard`,
`nonblack`, `that entered this turn`.

**What residual exhaustion actually proves:** that no clause text exists
*outside* claimed spans — there is no additional unparsed material. **What
it cannot prove:** that claimed spans were fully understood. Structural
conservation versus content, exactly as the recorded trap states.

## D.2 The repair: residue-honest claiming

The hole is in what may **claim** text. Close it with one mechanical rule:

> **RESIDUE-HONESTY: only literal template tokens and closed-vocabulary
> matches may claim text. Any text matched by an open capture group is
> residue by definition, even though the template matched.**

Under this rule, `target creature with flying` claims `target` (literal)
and `creature` (closed CR 205 vocabulary); `with flying` is claimed by
nothing → residue non-empty → the keyword dimension is **UNRESOLVED**, and
the strict swapper is blocked — the correct outcome. `Destroy target
permanent.` claims every token literally or from closed vocabulary →
residue empty → absence claims become *eligible*. The rule is checkable at
claiming time, not aspirational.

## D.3 Residue-honesty is necessary but still not sufficient

One gap remains: a semantic element can hide inside **legitimately claimed
literal tokens**. A template hard-coding `to its owner's hand` claims those
words literally; if its emission schema records `destination = hand` and
drops the owner relation, text is honestly claimed and meaning is still
lost. Residue cannot see this, because the failure is in the
template-to-schema mapping, not in coverage of the text.

So the proof obligation has three parts, not one (§E). The second part is
per-template and finite; the third is the repository's own negative-control
law pointed at absence.

---

# E. MINIMUM ABSENCE-PROOF CONTRACT

**`ABSENT-PROVEN(dim, occurrence)` may be asserted iff ALL of:**

1. **Residue-honest exhaustion** — the occurrence's clause has zero
   residue under §D.2's claiming rule (open captures never claim).
2. **Template adequacy** — every template that claimed text in this clause
   is ratified *with its emission schema*, the ratification asserting that
   the semantic content of its literal tokens is fully represented in what
   it emits. This is the existing DET-pattern ratification law with one
   added sentence, not a new mechanism.
3. **Dimension negative control** — dimension `dim` has a passing mutation
   control against this template family: take a matched card, textually
   add a `dim` restriction, and assert the emitted output **changes**
   (a new fact appears or residue appears). A guard never shown to fail is
   not known to be a guard — the standing law, applied to absence.

Plus the standing precondition: `dim` has a ratified semantic contract
(§C); a dimension without one simply never yields ABSENT-PROVEN.

**Direct answers to the challenge:**

1. *What does residual exhaustion prove?* No unclaimed clause material
   exists. 2. *What does it not prove?* That claimed material was fully
   represented. 3. *Can ABSENT-PROVEN follow from empty residue alone?*
   **No.** 4. *Minimum addition?* Obligations 2 and 3 above — and
   obligation 1 itself only counts under the residue-honest claiming rule.

**Dimension-specific treatment, as the challenge invited:** yes — this is
naturally per-dimension. Dimensions with closed vocabularies, contracts,
and passing controls (colour, type, controller, tapped) can support strong
absence proofs; dimensions without them (open-ended conditions, timing
subtleties) simply stay UNRESOLVED forever until they earn the contract.
No universal mechanism is forced; strict Budget Swapper concludes
"restriction NOT PRESENT" only where all three obligations hold, and
treats everything else as UNKNOWN — which, per the standing rule, never
reads as ABSENT.

The proposed shape in the challenge ("residual exhaustion +
dimension-specific coverage proof") is close but under-specified: a
"coverage proof" that means *"the extractor recognizes all corpus
realizations of dim"* is an unfalsifiable universal claim — a hand-list
assertion in disguise. The negative control replaces it with something a
gate can actually run.

---

# F. CHALLENGE 3 — HOLDOUT INTEGRITY

## F.1 Verdict: the attack lands cleanly. The redraw rule is withdrawn.

The prior protocol allowed *"holdout error > 2× open-cohort error →
benchmark invalid → redraw with fresh seed."* That conflates two things the
challenge correctly separates, and as written it permits exactly the
degenerate loop it warns about: draw, score, dislike, redraw — holdout
shopping until a friendly population appears. Once the holdout is opened,
poor performance **is evidence**, and a protocol that can discard
inconvenient evidence is not an anti-bias protocol.

## F.2 The corrected protocol

**Class A — results-based outcomes (never a redraw):**

- Poor generalization by **one** candidate = discriminating evidence
  against that candidate's extraction story, scored at tier THIRD.
- Poor generalization by **both** = evidence that extraction is harder
  than the open cohorts suggested; feeds the verdict (and, via tier SIX,
  leans "smallest reversible architecture; do not migrate on unproven
  extraction"). It is a finding, possibly the most important one the
  benchmark produces.
- In neither case is the holdout redrawn. **No performance number, however
  bad, is grounds for redraw.**

**Class B — procedural invalidation (the only redraw path), closed list:**

1. revealed seed does not match the committed `sha256(seed₂)`;
2. sampling script deviates from the pre-registered design (diff against
   the committed script);
3. wrong corpus snapshot sampled (snapshot sha mismatch);
4. leakage: holdout ∩ development set non-empty, or a holdout card was
   demonstrably inspected before freeze;
5. cohort construction violated its own pre-committed rules;
6. answer-key failure **above the pre-registered rate** (see below).

**Temporal firewall:** the holdout opens in two stages. **Stage 1** —
reveal the seed, regenerate the population, run the procedural audit
(items 1–5; every check deterministic), and record the pass/fail
**in writing, before any candidate is scored**. **Stage 2** — scoring.
After stage 2 begins, items 1–5 can no longer be raised except on evidence
that existed at stage 1 and was falsified — because any later
"procedural" objection is informationally contaminated by scores.

**Answer-key errors** are the one class discoverable only during scoring,
so they get per-card treatment: a *demonstrated* key error (demonstration
logged, append-only) voids that card **for both candidates
symmetrically** — never the holdout. Pre-registered cap: if demonstrated
key errors exceed **10% of holdout cards**, the answer-writing process
itself failed; that is a Class B invalidation — and it is symmetric by
construction, since the key is shared.

**Anti-shopping guarantees:** every draw's commitment, seed, audit record,
and result — including invalidated ones — stays in the evidence packet
permanently, labeled (the repository's preserve-history convention);
each redraw requires a fresh commitment recorded in the packet; and
Captain sees the full sequence of draws, so a packet with three redraws
reads as exactly what it is.

**The challenge's six questions:** (1) never; (2) as Class A evidence,
scored, possibly decisive; (3) Class B's closed list only; (4) items 1–5
before scoring begins, in writing — the key-error cap being the sole
post-scoring exception, per-card and symmetric; (5) yes, always, labeled;
(6) the temporal firewall + closed list + permanent full-sequence
disclosure.

---

# G. ENTITY-CONTEXT NORMALIZATION

## G.1 Verdict: the challenge is correct — and the repository has already
ratified the underlying rule at the lattice level.

`creature ⊂ permanent` as a context-free axiom proves false subsumptions:
a creature **card** in a graveyard is not a permanent; a creature **spell**
on the stack is not a permanent. The CR decides this statically —
**CR 109.2**: a description using only a type word means a permanent of
that type on the battlefield; adding "card" means a card in the named
zone; "spell" means on the stack. And the object lattice already enforces
one arm of it: the Auriok Salvagers defect (*"Return target artifact CARD
from your graveyard"* claimed for bounce) was fixed by **CR 110.1** —
"`<type> card` is not a permanent" — recorded in PICK-UP-HERE §0AA. My
cross-card addendum's subsumption table simply failed to carry the rule
its own lattice already obeys.

## G.2 The correction

The normalized object gains two context coordinates, both EXTRACT-1-derivable
from CR 109.2's closed template rule:

```
entity-kind:  permanent | card | spell        (+ token/nontoken as a flag, CR 111)
zone:         battlefield (default per CR 109.2) | named zone (+ owner relation)
```

- `target creature` → kind=permanent, zone=battlefield,
  `REQUIRES(type, creature)` — `⊂ target permanent` **valid** ✓
- `target creature spell` → kind=spell, zone=stack — **no** subset
  relation to any permanent predicate ✓
- `target creature card in your graveyard` → kind=card,
  zone=graveyard(owner=you) ✓
- `artifact creature permanent` → kind=permanent, both REQUIRES ✓
- `artifact card` / `artifact spell` → kind card / spell ✓

**The subsumption rules themselves do not change; their application is
guarded:** type/subtype subsumption (and every §B.3 entailment) operates
only **within equal entity-kind and compatible zone context**; across
kinds, predicates are incomparable-by-kind (not "disjoint" as a semantic
claim — simply outside each other's comparison domain, which is what a
strict swapper needs: destroy-creature and exile-creature-card-from-
graveyard are different consumer roles). The §C contracts gain their
`applicable contexts` column from this section — controller exists for
permanents and spells, owner for everything, tapped only on the
battlefield — all static classification, no game state anywhere.

---

# H. OWNERSHIP-NEUTRAL BENCHMARK DESIGN

The challenge: does the benchmark silently assume the ownership answer my
hypothesis prefers? Audit of the design against Models A–D:

**What is shared and therefore decides nothing about ownership** (all
pre-registered identically for both candidates): the occurrence address
scheme (§C of the cross-card addendum), the constraint-atom vocabulary
(§B.3 here), the dimension contracts (§C here), the entity-context model
(§G here), the disposition taxonomy, the comparison algebra, and the
absence-proof contract (§E here). None of these is a storage-shape or
ownership choice.

**The shared normalized fact table is an EVALUATION PROJECTION only** —
neither candidate's native store. Two guards make that real rather than
stated:

1. **Symmetric exporters with a self-consistency check:** each candidate
   projects its native representation into the table, and each candidate's
   *native* answers to the §M consumer questions must match the answers
   computed from its own projection. A candidate whose projection
   disagrees with itself has a lossy exporter, caught before any
   cross-candidate comparison.
2. **Home-field acknowledgment:** the flat table is nearer OCC-FACET's
   native shape than MIN-IR's. Mitigation: the projection is defined by
   its **content contract** (fact rows + dispositions + provenance), not
   by any storage idiom; MIN-IR's nesting flattens mechanically (its own
   design already commits to two-level structure); and exporter
   implementation cost is **excluded from scoring** — only a *lossy*
   projection is scoreable evidence (it already was, per the first
   addendum).

**Which measurements discriminate ownership rather than serialization:**
tiers FIRST–FOURTH run entirely on the projection and are
**ownership-blind by construction**. Ownership is discriminated only by
tier FIVE (migration blast radius, ruling/guard conservation, refresh and
identity churn, mutation/ratification pathways, durability surface) and
tier SIX (reversibility). That separation — correctness and sufficiency
scored where ownership cannot be seen; ownership scored only where it
actually differs — is what keeps Models A/B/C/D all reachable by the
verdict, including hybrid boundaries (Model D), which the verdict
expresses by naming which row kinds are canonical.

**One leak found and closed:** pre-committed answers must be written in
**projection vocabulary** (occurrence addresses + atoms + verdicts), never
in either candidate's native terms — otherwise the answer key itself
carries a home-field bias. Added to §J.

---

# I. DISPOSITION OF THE FIVE PRIOR CONCLUSIONS

| # | conclusion | disposition | smallest reason |
|---|---|---|---|
| 1 | "negation can be normalized away into complement-valued sets" | **AMENDED** | conflates NOT_HAS with HAS-complement on multivalued dimensions (artifact land; white-black creature), and a stored complement goes stale when the CR vocabulary grows (`battle`). Replaced by REQUIRES / FORBIDS / CARD atoms — negation still confined to atoms, no formula negation. |
| 2 | "residual exhaustion makes ABSENT-PROVEN cheap" | **AMENDED** | textual conservation cannot see content — the recorded greedy-`\(.*\)` trap rebuilt one layer up. Corrected to residue-honest claiming + template adequacy + dimension negative controls (§E). Still mechanical; "cheap" now qualified. |
| 3 | "the holdout may be redrawn after sufficiently divergent performance" | **WITHDRAWN** | results-based redraw is holdout shopping. Replaced by the two-class protocol with a temporal firewall (§F). |
| 4 | "the comparison algebra remains tiny and closed" | **SURVIVES WITH QUALIFICATION** | still closed and decidable, but the atom set grew (FORBIDS, CARD), contracts got richer (§C), and every entailment is now context-guarded (§G). Small, no longer minimal-as-first-stated. |
| 5 | "occurrence/participant/predicate/relation is the strongest pre-benchmark hypothesis" | **SURVIVES** | every correction in this document lands at the predicate/proof/protocol layer and applies to both candidates identically; none favors nesting or moves ownership. |

---

# J. EXACT BENCHMARK CORRECTIONS

Folded into the design before implementation authority:

1. Replace complement-valued sets with the **REQUIRES / FORBIDS / CARD**
   atom model (§B.3); no complement is ever materialized.
2. Replace the dimension-exclusivity registry with **per-dimension
   semantic contracts** (§C), one Captain-ratified sheet, every cell
   CR-anchored at implementation time.
3. Adopt **residue-honest claiming** (§D.2) as a defining rule of the
   claiming grammar: open captures never claim.
4. Adopt the three-part **absence-proof contract** (§E); ABSENT-PROVEN is
   ineligible on any dimension lacking a contract or a passing negative
   control.
5. **Delete the results-based holdout redraw**; adopt the two-class
   protocol with the stage-1 procedural audit recorded in writing before
   scoring, the 10% answer-key cap, and permanent full-sequence
   disclosure (§F).
6. Add **entity-kind and zone context** to the normalized object; guard
   all subsumption and entailment by context equality (§G). Add the
   corresponding cohort cards (`creature spell`, `creature card in
   graveyard`) to the population's structural adversaries.
7. Pre-committed answers are written in **projection vocabulary only**
   (§H).
8. Add negative-control fixtures for §B's multivalued cases (artifact
   land vs `nonland`; white-black creature vs `nonblack`) and §D's
   zero-residue-loss case (`target creature with flying` under an
   open-capture template must yield UNRESOLVED, never ABSENT-PROVEN).

---

# K. REMAINING UNRESOLVED QUESTIONS

Enumerated, none a design blocker; each is benchmark-answerable or a named
Captain-sheet item:

1. The CR anchor for cardinality-word normalization (`up to N`, `one or
   more`) — flagged U until verified; an unconfirmed anchor is not an
   anchor.
2. Timing/duration/condition comparison remains equality-only in v1
   (already scoped in the cross-card addendum §E).
3. Predicate-valued field semantics (`per(P)`, event patterns) remain
   reserved; the collapse-point analysis stands.
4. The dimension-contract sheet (§C) is drafted here and needs Captain
   ratification before any absence claim rests on it.
5. The 10% answer-key cap is a pre-registered number chosen for symmetry
   and auditability, not derived; if Captain prefers a different cap, it
   must be set **before** the first holdout opens — after that it is
   frozen.

---

# L. FINAL READINESS VERDICT — AND DIRECT ANSWERS

**Verdict: READY TO IMPLEMENT, with §J folded in. No further whole-design
pass is warranted.** The adversarial passes are now hitting
implementation-grade specifics (claiming-grammar rules, audit ordering,
atom semantics) rather than architecture, which is the signal that the
next unit of insight costs less to buy with evidence than with another
paper round — and the anti-bias machinery (pre-registration, symmetric
one-wrong-fact veto, sealed holdout with a temporal firewall, projection-
vocabulary answers) is now strong enough to make the evidence trustworthy.

The twelve questions, directly:

1. **`nonblack creature`** = `REQUIRES(type, creature) ∧ FORBIDS(colour,
   black)` — non-membership of the named value in the object's colour
   set. Never a complement set.
2. The algebra needs the **FORBIDS atom** — negation confined to atomic
   non-membership — and needs **no formula-level negation**. The "more
   precise set model" is precisely the typed-atom model; complement
   *encoding* is eliminated, negation *semantics* is kept where the cards
   put it.
3. Minimum valid proof of ABSENT-PROVEN: residue-honest exhaustion **+**
   ratified template adequacy **+** a passing dimension negative control,
   on a contract-registered dimension (§E).
4. **No** — textual residual exhaustion alone is not sufficient; it
   proves coverage of text, not representation of meaning.
5. What must be added: the claiming restriction (open captures never
   claim), the template-adequacy ratification sentence, and the
   per-dimension mutation control.
6. **Never.** Bad performance on a valid holdout is evidence, and may be
   the benchmark's most important finding.
7. Only the closed procedural list: seed-commitment mismatch, script
   deviation, wrong snapshot, leakage, cohort-rule violation — all
   auditable and recorded before scoring — plus the symmetric,
   pre-capped answer-key failure class.
8. **Yes**: subsumption and all entailments are now guarded by
   entity-kind/zone context per CR 109.2 — `creature ⊂ permanent` holds
   only among permanents on the battlefield, which the lattice's own
   CR 110.1 fix already knew.
9. **Yes** — the occurrence/participant/predicate/relation model remains
   the strongest pre-benchmark hypothesis; all five challenges corrected
   its predicate semantics, proof obligations, and protocol, and none
   touched its structure or ownership.
10. **No new reason** to believe nested MIN-IR has an expressive
    advantage: every correction here applies to both candidates
    identically. The atoms, contracts, contexts, and absence proofs are
    serialization-independent.
11. The single most important assumption to change before implementation:
    **that empty residue licenses absence.** It licenses nothing by
    itself; §E's contract is what licenses absence, and building the
    claiming grammar residue-honest from day one is the difference
    between an honest strict swapper and a confidently wrong one.
12. Ready — per the verdict above. The five §K items ride the existing
    sheets; none justifies another design pass, and the benchmark itself
    is now the cheapest source of the next correction.

---

*For the record: two of five challenged conclusions could not be defended,
and one was already a recorded trap in this repository's own CLAUDE.md
aimed back at its author. That is the adversarial process working, and it
is worth one sentence of generalization: the two failures shared a shape —
a mechanism defined by what it CONSUMES (text spans, complement sets)
rather than by what it REPRESENTS — and the two fixes shared one too:
type the claim, not the leftovers.*
