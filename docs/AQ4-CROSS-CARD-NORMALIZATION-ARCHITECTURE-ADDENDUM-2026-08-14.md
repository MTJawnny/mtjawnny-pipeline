# AQ4 — CROSS-CARD NORMALIZATION ARCHITECTURE ADDENDUM

**2026-08-14. Read-only.** Challenges and revises
`docs/AQ4-BENCHMARK-PRECOMMIT-ARCHITECTURE-ADDENDUM-2026-08-14.md` (which it
does **not** overwrite) ahead of benchmark implementation authority. No code
changed, no codebook mutation, no Gate 2 change, no P3/C6 change, no
vocabulary minted, no decision ID created, nothing implemented.

**What survives from the prior addendum, in one line:** the ladder framing,
the shared relational normal form, the extraction taxonomy, and the
pre-registration discipline all survive; the occurrence-identity design, the
"irreducible MIN-IR advantage" claim, the 5% threshold, the asymmetric
false-precision veto, and the no-compound-slug bundling are amended or
withdrawn — each itemized in §P.

---

# A. CORRECTED CURRENT-STATE NOTE

**The locality reversion incident is CLOSED, and this was verified live this
session, not recalled:**

- `experiments/out/foundry/codebook.json` — SHA-256
  `6aa6193f8a457ae4c7884e364f519749a9d68b96f7ecedf3fa903bfa4677426c`,
  **5,066,147 bytes**, **7,808** stored `locality` fields present
  (re-counted directly from the file this session).
- Gate 2: **16 rows, 15 passed, 1 known-excused (`family_sweep`, exact
  authorized W6 fingerprint), 0 unexpected — GREEN.**

The prior addendum's standing-state caveat ("Gate 2 is RED… the backfill
must be re-applied") and its recommendation M.2 are **withdrawn as moot**.
The incident remains citable as *historical* architecture evidence — a
stored field vanished silently and only a per-machine ratchet noticed, which
is real data about derived-vs-stored state and about why C6's
manifest-selected authority matters — but no operational statement in this
document depends on it, and nothing here says or implies the operational
codebook is `b4197e94…`.

---

# B. STRONGEST OCC-FACET — WITH LOCALITY LEFT LITERALLY UNTOUCHED

## B.1 The challenge, accepted

The prior addendum extended the ratified `locality: [face, paragraph]` to a
three-element form. That was the wrong steelman, for four reasons:

1. **It mutates a ratified field** (§11 of `B-MIGRATION-DISCOVERY.md`,
   amendments A1–A4) to answer a question that ruling deliberately did not
   ask. Locality answers *"which semantic owner holds this assertion's
   evidence"*; occurrence identity answers *"which clause inside that owner
   does a subordinate fact attach to."* Different questions, and the ruling
   is scoped to the first.
2. **It would degrade addressability, measurably.** The backfill resolves a
   quote to a paragraph; many quotes cover a whole ability — cost plus
   effect, several clauses. Forcing the address down to clause granularity
   turns clean `OWNER` results into SPAN-shaped ones. The conservative
   candidate must not buy a regression in its own ratified metric to gain a
   coordinate that only *new subordinate facts* need.
3. **It re-derives 7,808 stored values** whose meaning would silently
   change — the second-source-of-truth shape A1 exists to prevent.
4. **It was an artificial gift to MIN-IR**, letting the typed candidate
   claim "the conservative model must amend ratified law too."

## B.2 The amended design (options evaluated: A third coordinate · B
subordinate coordinate · C derived object · D other)

**Recommendation: C, with B's attachment style — a derived occurrence layer,
referenced by subordinate rows; the assertion schema untouched.**

```
assertion  (UNCHANGED — all 8,982 rows, all 4,233 human, byte-identical)
  locality: [face, paragraph]                # ratified; never extended

occurrence table  (GENERATED, snapshot-local, deterministic ×2, gitignored
                   like every derived artifact; never stored in the codebook)
  [oracle_id, face, paragraph, clause]       # §C defines this

facet / relation rows  (NEW, born only from forward emission)
  occ:  [face, paragraph, clause]            # full address on the row
  dim / value  |  kind / to
```

- **Can `[face, paragraph]` remain literally unchanged?** Yes — it is not
  touched, extended, re-derived, or reinterpreted.
- **Can all 4,233 human assertions remain structurally untouched?** Yes —
  they neither gain nor need occurrence awareness; they remain valid
  paragraph-level evidence, exactly as the locality ratification says.
- **Can occurrence-aware DET facts coexist with legacy paragraph-level human
  assertions?** Yes, and the uncertainty model (§H) gives the coexistence
  precise semantics: a fact with no facet rows is *unrefined*, not
  *unrestricted*.
- **Conceptually cleaner?** Yes: semantic ownership and clause attachment
  stop sharing one field, so neither question's law constrains the other's.
- **Migration and guard reduction?** The `locality` gate is untouched. All
  additions are additive rows plus additive gates.
- **A dangerous second addressing system?** The danger is two *independent*
  schemes. Avoided by the **prefix invariant**: an occurrence address is an
  extension path of a paragraph owner — one hierarchical scheme at two
  depths — and it is enforced:

  > **INV-1 (prefix consistency):** every facet/relation row's
  > `occ[face, paragraph]` prefix must equal the `locality` of the assertion
  > it refines, and every occurrence address must resolve to a live clause
  > in the pinned snapshot. Violation halts (the locality halt law, one
  > coordinate down).

  Character spans stay **evidence-only, never identity** — the ratified
  "span is derived, never stored" rule (§13) generalizes unchanged.

This is the steelman the benchmark should carry as OCC-FACET. It preserves
strictly more existing architecture than the prior version and loses no
capability: attachment lives on the subordinate rows, where the new
information actually is.

---

# C. RECOMMENDED SEMANTIC OCCURRENCE IDENTITY

## C.1 The census key is evidence, not a design — the challenge, accepted

The prior addendum leaned on the live census key
`(oracle_id, stem, occurrence index)`. As **evidence that occurrence
counting is deterministic and reproducible**, it stands. As a **production
identity**, it fails a basic requirement: the ordinal is scoped per *stem*
— per classifier pattern — so the same clause receives different identities
from different extractors, and the four facts one clause supports
(`action=destroy`, `object=permanent`, `targeted=true`,
`restriction=blue`) would land on up to four "occurrences." An identity
minted by whoever matched is a classifier artifact, not a semantic address.

**The rule that fixes it:** *two derived facts belong to the same occurrence
iff they were derived from the same segment of the canonical text* — so
identity must come from the **segmentation**, which is extractor-independent
and already conservation-gated (`sentence_spans` reassembles
character-for-character), and extractors must **resolve** their match
position into that segmentation rather than mint ordinals.

## C.2 The recommended minimal identity

```
occurrence := [oracle_id, face, paragraph, clause]
```

- `clause` = ordinal of the segment within the paragraph's canonical text,
  from the existing segmentation machinery. Snapshot-local; re-derived per
  refresh; halts on unresolved; rebuilt with zero human judgment — D-4's
  ratified identity law, one level down.
- **`effect` (sub-clause ordinal) is RESERVED, not adopted.** One sentence
  can hold two effects ("Draw a card, then discard a card"), so the slot is
  real — but sub-sentence effect-splitting is the single highest-defect-rate
  operation in this repository's measured history (the coordination-splitter
  family: fragments discarded, triggers invented, tokens lost — three
  defects pointing opposite ways). Coupling *identity* to the most fragile
  machinery on day one would make every splitter bug an identity bug. The
  reserved-coordinate move is the ratified pattern (A1 reserved child
  effects the same way). The benchmark measures the cost of deferral via
  the **MEC probe** (multi-effect-per-clause rate, §R) before anyone pays
  it.
- **Spans participate in evidence only, never identity** — fragile under
  canonicalization, and the ratified span rule already decides this.
- Repeated identical clauses: distinguished by ordinal path (different
  paragraph → different address; same paragraph twice → different clause
  ordinal). Seize the Soul's two identical clauses get distinct addresses;
  the *legacy backfill* direction (quote → address) stays AMBIGUOUS for
  them, correctly — their stored evidence genuinely cannot say which unit
  it came from, and no architecture can conjure that.
- Modal paragraphs: already separated at the paragraph coordinate (A1's
  measurement: 1,791 bullet paragraphs, zero holding two bullets).
- Linked abilities: two paragraphs joined by a CR 607 relation edge —
  identity untouched.
- One effect spanning multiple clauses ("Exile target creature. Return it…
  at the beginning of the next end step"): multiple occurrences joined by
  relation edges; the *effect-as-a-whole* is a derived grouping, not an
  identity-bearing object — same move as ChoiceGroup (§F of the prior
  addendum, surviving).
- Wording changes: identity does **not** survive them, per existing law;
  cross-snapshot continuity is a diff problem (§J), not an identity problem.

---

# D. CROSS-CARD NORMALIZATION — THE REQUIREMENTS

This is the section the prior addendum under-served. Occurrence identity
solves *within-card attachment*. Budget Swapper's contract is *cross-card
comparison*, and labels cannot answer it — `"blue permanent"` and
`"permanent"` as strings have no subset relation.

**The requirement, worked through the concrete predicates:**

Eligibility is a **conjunction of typed constraints over independent
dimensions** on a base object class:

```
target blue permanent          = object ∈ permanent ∧ colour ⊇ {blue}
target nonland permanent       = object ∈ permanent ∧ type ∈ COMPLEMENT({land})
target creature you control    = object ∈ creature  ∧ controller = you
target creature power ≤ 2      = object ∈ creature  ∧ power ∈ (-∞, 2]
target artifact or creature    = object ∈ (artifact ∪ creature)
another target creature        = object ∈ creature  ∧ excludes = self
```

Then the comparisons Foundry needs are all **per-dimension operations
composed conjunctively**:

- `blue permanent ⊂ permanent` — adding a constraint narrows
  (monotonicity); derivable, never stored.
- `nonland permanent ⊂ permanent` — same rule.
- `blue permanent` vs `nonland permanent` — neither entails the other
  (blue lands exist), and they **overlap** because no dimension pair is
  contradictory. Overlap/disjointness require **dimension exclusivity
  facts**, which are CR-anchored per dimension and *not* guessable from
  intuition: controller is single-valued (a permanent has one controller),
  tapped/untapped is binary — but **card types are NOT mutually exclusive**
  (CR 300.2 conjunctive types; artifact creatures; Dryad Arbor is a land
  creature) and **colours are not exclusive** (multicolour). Getting these
  from the CR rather than from a hand impression is exactly the repo's
  standing law, and the type case is the trap that proves why.
- Type/subtype/supertype: CR 205.3g–q subtype→type subsumption is already
  parsed and consumed (`foundry_cr702_classes`, the object lattice); CR
  110.4 gives `permanent ⊇ {artifact, creature, enchantment, land,
  planeswalker, battle}`; supertypes (CR 205.4) are an orthogonal dimension.
- Negation (`non-X`): over a **CR-closed vocabulary**, negation normalizes
  to a **complement-valued set** at extraction time (`nonland` = the CR
  205.2a type list minus `land`), so the comparison algebra never needs a
  negation operator — set inclusion carries everything. This single move
  keeps the algebra decidable and tiny.
- Union classes (`artifact or creature`): eligibility becomes a union of
  conjunctions — DNF with disjunct counts of 2–4 as printed. Comparing tiny
  DNFs is cheap and closed. (The printed-`or` parse sits in the measured
  coordination-trap zone; that is an *extraction* risk, priced in §I, not
  an algebra problem.)
- Zones and origin/destination: closed CR vocabulary; comparison is
  componentwise equality plus the destination *relation* (owner's hand vs
  your hand differ by a relation, not a zone).
- Numeric thresholds: normalize to intervals; comparison is interval
  containment.

**Verdict: yes, Foundry needs a normalized semantic system in which these
relationships are mechanically derivable — and no, it does not need to be
large.** Everything above reduces to set/interval operations over CR-closed
vocabularies, conjunctions, and small unions. The governing principle
survives contact with every worked example:

> **Store the smallest canonical facts. Derive every relationship.**
> `blue permanent ⊂ permanent` is never a row anywhere; it is a two-line
> consequence of monotonicity over stored constraints.

---

# E. THE MINIMUM PREDICATE ALGEBRA

Each operation, against the nine mandated questions. Legend: *canonical* =
stored as fact shape; *derived* = computed at comparison time; *consumer* =
policy outside canonical semantics.

| operation | consumer question requiring it | where it lives | source of the relationship | closed? | if unknown |
|---|---|---|---|---|---|
| conjunction of constraints | all strictness questions | **canonical fact shape** (constraint set) | oracle template (EXTRACT-2) | yes | n/a |
| small union (DNF ≤ ~4) | printed `or` classes | **canonical fact shape** | EXTRACT-2 | yes | n/a |
| complement-valued sets | `non-X` | **canonical value form** | EXTRACT-4 over EXTRACT-1 vocab | yes | halt at extraction |
| per-dimension entailment (⊆) | "is B broader/narrower than A" | derived | set/interval math over EXTRACT-1 vocab | yes | verdict UNKNOWN |
| equality | "mechanically equivalent" | derived (mutual entailment) | — | yes | UNKNOWN |
| overlap / disjointness | "incomparable but overlapping" / filtering | derived | **dimension-exclusivity registry** (EXTRACT-1 per entry; see below) | yes | UNKNOWN |
| type/subtype subsumption | class comparisons | derived | CR 205.3g–q / 110.4 — **exists** (EXTRACT-3) | yes | halt (CR-LAG register) |
| numeric inequality | power/toughness/mana-value thresholds | derived | interval math (EXTRACT-4) | yes | UNKNOWN |
| quantity comparison | "up to N" vs "exactly N" vs "any number" | derived over normalized `{min,max}` | EXTRACT-2 template normalization | yes | UNKNOWN |
| zone / origin-destination comparison | bounce vs tuck vs exile paths | derived, componentwise | EXTRACT-1 zones + relation facts | yes | UNKNOWN |
| optionality comparison | "may" vs mandatory | **consumer policy** — capability vs guarantee is the consumer's call; canonical stores the flag only | EXTRACT-2 | yes | n/a |
| timing/duration comparison | flash-window, until-end-of-turn | equality-only in v1; entailment deferred | EXTRACT-2 | partial | UNKNOWN |
| condition comparison | conditional effects | equality-only in v1 | — | no | UNKNOWN |
| alternative-vs-cumulative | the 41-card family | derived (ChoiceGroup, prior addendum §F — survives) | CR 700.2 header | yes | halt |

**Explicitly NOT in the algebra:** general negation as an operator,
quantified reasoning, theorem proving, "for each" *resolution* (the scaling
fact is stored; its value is never computed), replacement-loop semantics,
any operation without a named consumer question.

**Three-valued results are mandatory.** Every derived comparison returns
`PROVEN`, `PROVEN-NOT`, or `UNKNOWN` — and strict replacement acts only on
`PROVEN`. This is where the algebra and the honesty model (§H) lock
together: an algebra that collapses UNKNOWN into either pole is how a
strict swapper lies.

**The one new knowledge object:** the dimension-exclusivity registry
(~10 rows: controller single-valued, tapped binary, types NOT exclusive per
CR 300.2, colours NOT exclusive, …), each row carrying its CR anchor,
ratified once, with **zero growth exposure** — it grows only if Magic adds a
dimension, not when it adds a set. That is the acceptable end of the
hand-list spectrum, and it must be ratified, not typed casually.

---

# F. PARTICIPANT IDENTITY — THE PRIOR CLAIM, WITHDRAWN

The prior addendum called argument identity "MIN-IR's one irreducible
structural advantage." **Withdrawn.** The flat form:

```
(occ=U1, participant=0, object=creature, controller=you)
(occ=U1, participant=1, object=creature, controller=not-you)
```

carries Prey Upon completely, adds one integer coordinate, and is not
meaningfully more complex than MIN-IR's nested `participants[]` — it is the
same information in adjacency-list form. Participant identity is therefore
**a coordinate on the shared normalized model, available identically to both
candidates**, not an IR discriminator. What was true in the prior addendum's
own §A.3 ("the IR in adjacency-list form") is now applied to its §B.2
conclusion, which should have followed then.

Consequence: the participant coordinate is simply **in scope for both
candidates** in the benchmark — the Prey Upon and blink cohorts already
require it to answer the pre-registered questions — and it stops being a
decision variable. The MPR probe survives as a *prevalence* measurement
(useful for extraction prioritization), not as an architecture threshold
(§N, §P).

---

# G. RELATIONS AND NESTING — WHERE THE FLAT MODEL ACTUALLY ENDS

Mandate: try hard to find structure that
`occurrence + participant + predicate + relation` cannot carry without
nested units. The candidates, each attempted:

| structure | flat representation | forces nesting? |
|---|---|---|
| several actions in one clause | reserved `effect` ordinal (§C) or relation `then` between fact rows | no |
| one effect, several participants | participant coordinate | no |
| later effect referencing an earlier participant | relation edge `refers-to → (occ, participant)` | no |
| conditional dependency | relation edge `conditional-on` with polarity | no |
| delayed effects | relation edge `delayed` + timing fact | no |
| linked abilities | CR 607 relation edge | no |
| replacement effects | fact rows with sort `event-pattern` + `substitute` action; classified, never resolved | no |
| variable quantities (X) | quantity fact `{min,max,definition-ref}` | no |
| "for each" scaling | quantity = `per(P)` where P is a **predicate-valued field** — a reference to another predicate row | no — *but see below* |
| bound choices ("choose a creature type… destroy all creatures of that type") | relation edge `same-choice-as` between predicate rows | no |

**The honest boundary:** the flat model holds until **predicate-valued
fields** appear — `per(P)`, event patterns, choice bindings — at which point
rows reference rows and the representation contains recursive structure *by
reference*. That is the exact coordinate where "flat facets" collapses into
"IR in relational form." It does not force nesting — references carry it
cleanly — but past that point the two candidates are **provably the same
semantics with different serialization**, and any benchmark scoring that
pretends otherwise is measuring syntax.

**Conclusion: after occurrence, participant, typed predicates, relation
edges, and predicate-valued fields are admitted, nested MIN-IR has no
irreducible expressive advantage.** What remains genuinely architectural is
listed in §Q.7: canonical ownership, migration blast radius, guard
conservation, provenance mechanics, extraction surface, refresh behavior,
and projection/index policy.

---

# H. UNCERTAINTY AND NEGATIVE KNOWLEDGE

The failure to prevent: *"we did not extract a restriction"* silently read
as *"there is no restriction"* — absence-by-omission, the exact shape that
makes a strict swapper confidently wrong.

## H.1 The mechanism that makes honest absence CHEAP — residual exhaustion

The repository already owns the right machinery: the residual method (the
lattice's residual, the census's residual, conservation's
partition-and-reassemble law). Promote it to the semantic layer:

> **Semantic conservation law: every clause's canonical text is partitioned
> into spans claimed by extracted facts and unclaimed residue.**
>
> - Residue empty → unclaimed dimensions are **ABSENT-PROVEN** — *proven by
>   text exhaustion*, not by extractor silence. `Destroy target permanent.`
>   fully consumed by the template ⇒ the colour restriction is provably
>   absent.
> - Residue non-empty → unclaimed dimensions are **UNRESOLVED** — the
>   residue may or may not restrict them, and nothing may claim otherwise.

This turns "confidently absent" from an assertion someone forgot to doubt
into a mechanically checkable property, and it is the single most important
requirement this addendum adds to both candidates.

## H.2 The disposition taxonomy (per dimension, per participant, per occurrence)

| state | meaning |
|---|---|
| **PRESENT(value)** | extracted, with evidence span |
| **ABSENT-PROVEN** | dimension provably unrestricted, by residual exhaustion |
| **UNRESOLVED** | residue unclaimed; unknown either way |
| **AMBIGUOUS** | multiple deterministic readings; no choice made (the locality precedent) |
| **HUMAN-RESOLVED(value \| absent)** | Captain ruling; carries provenance `human` |

Granularity answers the mandated questions directly: one participant can be
PRESENT while another is UNRESOLVED; one facet known while a second stays
open — because the state attaches at
(occurrence, participant, dimension), not at the card or clause.

## H.3 Consumer policy (outside canonical semantics, stated here so it is
pre-registered)

- Strict replacement claims may rest **only** on PRESENT and ABSENT-PROVEN.
- UNRESOLVED on a consumer-critical dimension **blocks the strict claim**
  for that comparison — it does not disqualify the card from fuzzy
  discovery, ranking, or being *shown with the caveat*. Unresolved is a
  missing proof, not a defect.
- Canonical data carries the dispositions; audit metadata carries the
  coverage *rates* (ratchet material, per existing law).

Both candidates can carry this identically; the discriminating requirement
is that **residual accounting itself is canonical** in either one.

---

# I. EXTRACTION STORY FOR THE NORMALIZATION LAYER

Using the established classes (EXTRACT-0 structural · EXTRACT-1 CR-closed · EXTRACT-2
oracle-template · EXTRACT-3 existing-Foundry-primitive · EXTRACT-4 composed · H1 human ·
H2 hand-list · U unresolved):

| relationship / value form | class | source |
|---|---|---|
| creature ⊂ permanent (and the six types) | EXTRACT-1 | CR 110.4 |
| Island → land (all subtype→type) | EXTRACT-3 | CR 205.3g–q, already consumed via `foundry_cr702_classes` |
| colour sets | EXTRACT-1 | CR 105.1 |
| `nonland` and all `non-X` | EXTRACT-4 | complement over the EXTRACT-1 type vocabulary |
| `another` | EXTRACT-2 → relation | self-exclusion template; `{X} ∧ excludes-self ⊂ {X}` by monotonicity |
| `you control` / `an opponent controls` | EXTRACT-3 | §6 `SCOPE_VOCAB`, ratified |
| numeric thresholds → intervals | EXTRACT-2+EXTRACT-4 | template normalization |
| `up to N` / `exactly` / `one or more` / `any number` → `{min,max}` | EXTRACT-2 | CR anchor to be confirmed at implementation; **U until it is** — an unconfirmed anchor is not an anchor |
| zones, origin/destination | EXTRACT-1 | CR 4xx closed list |
| union classes (printed `or`) | EXTRACT-2 | flagged: sits in the measured coordination-trap zone — trap-replay (§H of the prior addendum, surviving) prices it |
| dimension-exclusivity registry (~10 rows) | EXTRACT-1 per entry, ratified once | per-dimension CR anchors; **zero growth exposure** |
| keyword-possession restrictions | EXTRACT-1 | CR 702 names via `load_702` (the census already does this) |

**No growing hand-list was identified anywhere in the normalization layer.**
If implementation finds one, the standing rule prices it as a major
architectural cost against whichever candidate needs it — and if it appears
in both, it is a problem with the *dimension*, to be brought to Captain, not
silently absorbed.

---

# J. ORACLE/CR REFRESH AND SEMANTIC DIFF

Occurrence identities are snapshot-local (existing law; unchanged). The
refresh question is whether two snapshot-local structures can be compared
deterministically enough to preserve human assertions, audit history, shard
certification, consumer stability, and provenance.

**The finding: the comparison algebra of §E pays for itself a second time
here.** Align occurrences across snapshots (paragraph/clause alignment with
quote text as tiebreak — the ratified corpus-refresh behaviour table,
extended one coordinate), then diff the **normalized facts** per aligned
occurrence. The required distinctions fall out of machinery already
specified:

| refresh event | detected by |
|---|---|
| wording-only change | same normalized facts, different text |
| resegmentation | alignment layer (ordinal shift, quote tiebreak — existing behaviour) |
| semantically equivalent rewording | normalized-fact equality despite text change |
| restriction widened / narrowed | **per-dimension entailment between old and new predicates — the §E algebra verbatim** |
| participant / action / zone changed | per-field diff of normalized facts |
| effect added / removed | unmatched occurrence, reported (existing halt-and-report law) |
| newly unresolved / newly resolved | disposition diff (§H states) |

Human assertions survive by the existing quote-re-anchoring machinery;
nothing new is needed for them.

**OCC-FACET vs MIN-IR on this problem: effectively neutral**, because the
diff runs on the shared normalized projection that both must produce. One
real asymmetry: OCC-FACET's canonical store (the codebook) is *not
regenerated* on refresh — only its derived layers are — while MIN-IR's
canonical artifact is rebuilt per snapshot, so MIN-IR's *canonical* identity
churns where OCC-FACET's merely re-derives subordinate rows. That is a
mild, honest edge to OCC-FACET on audit-history continuity, and it should
be scored under tier FIVE of §N, not treated as decisive.

---

# K. BENCHMARK POPULATION AND BLIND-HOLDOUT PROTOCOL

Pre-registered before implementation so the set cannot be tuned around the
failures we already know.

**Cohorts (eight, per the mandate):**

1. **Historical failures** — Active Volcano, the 41 flattened-modal cards
   (sampled), the documented semantic-loss cases. *Open during
   development.*
2. **Structural adversaries** — multi-participant clauses (Prey Upon
   family), multi-effect paragraphs (Kalitas), repeated identical clauses
   (Seize the Soul), linked abilities (CR 607), delayed effects,
   coreference (Cloudshift), modal structures incl. Spree. *Open.*
3. **Simple controls** — ≤5 cards both candidates must parse trivially
   (Erase-class). *Open.*
4. **Stratified random sample** — drawn deterministically from
   `load_corpus_gated()`, stratified by (delivery token × action family),
   seed recorded in the benchmark doc, sampling script committed. *Blind
   until extractor freeze.*
5. **Blind holdout** — second stratified draw. **Commitment scheme:**
   commit `sha256(seed₂)` in the benchmark document now; reveal `seed₂`
   only after both candidates' encoders/extractors are frozen (frozen = a
   named commit). Cheap, tamper-evident, no infrastructure.
6. **Consumer-critical families** — removal, blink/flicker, counterspells,
   ramp: the families where a false strict-substitution is most damaging.
   *Half open, half inside the holdout draw.*
7. **CR/characteristic-derived cases** — vanilla creatures (no oracle
   text), CR 113.3a face-cut cases, DFC layout cases — facts resting on the
   §D evidence-boundary riders of the prior addendum. *Open.*
8. **Negative/unresolved cases** — cards selected because honest
   dispositions should be UNRESOLVED/AMBIGUOUS (heavy residue, known
   splitter territory). Success = refusing to answer. *Open.*

**Rules:**

- Pre-committed answers (§M questions) are written per card **before
  encoding**, and the answer file's sha256 is recorded before any encoder
  runs — append-only thereafter.
- Development may consult cohorts 1–3, 7–8 and the open half of 6. Cohorts
  4–5 stay uninspected until freeze; 5 until evaluation.
- **Benchmark-invalidation condition, pre-registered:** if either
  candidate's error rate on the holdout exceeds twice its rate on the open
  cohorts, the benchmark was overfit to known failures — outcome is
  INSUFFICIENT EVIDENCE and the population is redrawn with a fresh
  committed seed. Likewise invalidated: any post-hoc edit to cohort
  membership or to a pre-committed answer without a logged correction
  entry.

---

# L. PROVENANCE AND DEBUGGING REQUIREMENTS

Both candidates must support the full trace:

```
characteristic field / Oracle text
  → evidence span or named field           (existing evidence law + §D rider 2)
  → semantic owner [face, paragraph]       (ratified locality)
  → occurrence [.., clause]                (§C; prefix invariant INV-1)
  → participant ordinal                    (§F)
  → canonical predicate row                (dim, value, disposition, extractor
                                            version, derivation class, CR anchors)
  → derived relationship                   (recomputed on demand; carries input
                                            row ids + per-dimension verdicts)
  → axis/index projection                  (regeneration-gated; never a source)
  → consumer answer                        (cites the per-dimension verdicts)
```

Minimum per stage: every canonical fact row carries evidence, extractor
version, derivation class, and CR anchors; every derived relationship
carries its input rows and per-dimension verdicts. **Derived relationships
are never stored canonically** — recomputed, so invalidating one bad
relation means fixing one input fact, never rebuilding unrelated facts.

The mandated questions, answered: an extraction bug localizes to a fact
row's span+extractor; a normalization bug to a per-dimension verdict's CR
anchor; a reviewer can dispute one fact row without discarding the
occurrence (the existing assertion-granularity dispute model, unchanged); a
consumer explains a failed strict replacement by naming the dimension whose
verdict was PROVEN-NOT or UNKNOWN, with the two fact rows behind it. This
is the debugging architecture, and it falls out of the row model in either
candidate — a candidate that cannot produce this trace fails tier FOUR of
§N.

---

# M. REVISED CONSUMER QUESTIONS

PREQ-1–PREQ-12 of the prior addendum survive in substance; regrouped and extended so
cross-card normalization is explicitly tested. Rules-engine questions remain
excluded.

**A. Within-card attachment**
1. Which occurrence performs action X, and what object class does it affect?
2. Which participant does each restriction modify? *(Prey Upon)*
3. Which occurrence does each cost, condition, duration, and destination
   belong to? *(Nicol Bolas's `Activate only as a sorcery`; NC-C)*

**B. Cross-card comparison** *(the new core)*
4. Are occurrences U_A and U_B semantically equal under normalization,
   despite different wording?
5. Is A's eligibility predicate **broader / narrower / overlapping /
   disjoint / UNKNOWN** relative to B's — and which per-dimension verdicts
   produce that answer?
6. Are the actions equivalent while eligibility differs? *(Doom Blade vs
   Murder-class pairs)*
7. Is eligibility equal while destination / timing / quantity differs?
   *(destroy vs exile vs tuck; instant vs sorcery)*
8. What exact fact prevents B from strictly replacing A — named dimension,
   named verdict, both evidence rows?
9. Is A's exile linked to a return? *(Cloudshift; the blink veto)*
10. Are U1 and U2 alternatives, cumulative, or independent? *(the 41-card
    family + Spree)*

**C. Broad discovery**
11. Which broad facts remain shared despite narrower restrictions — and can
    that be answered from indexes alone, without assembling full semantic
    structure? *(the cheap-retrieval floor)*

**D. Explanation**
12. Why did these two cards match, and which part of each card produced the
    comparison?

**E. Honesty**
13. Which consumer-relevant dimensions of this occurrence are UNRESOLVED or
    AMBIGUOUS, and does that block a strict-replacement claim it would
    otherwise support?
14. For a fully parsed clause: show that an unrestricted dimension is
    ABSENT-PROVEN by residual exhaustion, not silently absent.

CROSSQ-5, CROSSQ-8, CROSSQ-13, CROSSQ-14 are the questions the prior set could not ask; they are
the cross-card and honesty discriminators.

---

# N. REVISED DECISION RULES — ARCHITECTURE-NEUTRAL, LEXICOGRAPHIC

The outcomes remain conceptually A (axis/assertion model + occurrence/
predicate extension), B (hybrid typed-IR canonical + derived axes), C
(insufficient evidence) — but the rule does not key on labels. **The
decision identifies the smallest architecture that satisfies the consumer
contract.** Tiers are evaluated in order; a tier decides only if the
previous tiers tie.

**FIRST — information correctness (symmetric absolute vetoes).**

> **One confidently wrong CANONICAL semantic fact produced by candidate X is
> an absolute veto against candidate X for this benchmark iteration, unless
> the pre-committed answer is itself proven wrong (logged correction).**

Applies identically to both candidates and to every canonical fact kind:
wrong occurrence attachment, wrong participant binding, wrong normalized
predicate or complement, wrong relation edge, wrong ABSENT-PROVEN claim,
wrong condition/destination, and any *stored* comparison relationship.
UNRESOLVED is never false precision. The prior addendum's MIN-IR-only veto
is superseded by this symmetric form.

**SECOND — completeness and honesty.** UNRESOLVED allowed everywhere;
silent omission read as absence disqualifies (CROSSQ-14 tests it directly);
consumer-critical UNRESOLVED rates are reported per candidate and
per-dimension.

**THIRD — deterministic extraction.** H2/hand-list inventory with growth
exposure; anchor-free heuristic count (target 0); trap-replay misparses;
negative controls demonstrated per derivation class; determinism ×2.

**FOURTH — consumer sufficiency.** All of §M answerable with PROVEN where
the pre-committed answers say PROVEN; broad discovery (CROSSQ-11) answerable from
indexes without full structure assembly; the provenance trace of §L
producible end-to-end.

**FIFTH — architecture cost.** Migration blast radius; human-ruling and
ruling-corpus conservation; guard rows unchanged/adapted/rewritten (counted
against the runner, not a quoted total); schema complexity (record types +
coordinates + relation kinds); projection/regeneration obligations; refresh
and semantic-diff cost (§J).

**SIXTH — reversibility.** If two candidates satisfy the contract
equivalently through tier five, **the smaller reversible extension wins.**
A tie is never outcome C; C is reserved for benchmark invalidation (§K),
indeterminate extraction stories on both sides, or holdout divergence.

**The 5% MPR threshold is not preserved.** Its premise — participant
identity as MIN-IR's discriminator — was withdrawn in §F, so no prevalence
number can select between the candidates on that ground. Prevalence probes
(MPR, MEC, relation-kind diversity, residual-exhaustion rate) now feed
**rung adoption**, each governed by one qualitative gate:

> **Adopt a rung iff some pre-registered consumer question on the
> pre-registered population cannot be answered PROVEN without it.**

That gate is not tunable, does not care whether the enabling population is
2% or 8%, and automatically weighs consumer criticality — because the
questions, not the counts, are what a rung must serve.

---

# O. FALSIFICATION CONDITIONS PER RUNG

**H1 — occurrence identity alone suffices.**
Killed by: any strict-replacement question (CROSSQ-5, CROSSQ-8) requiring restriction
*values* to be compared — untyped attachment cannot rank `blue` against
`nonland`. *Expected to die on the first cross-card card pair; the
benchmark records the kill rather than assumes it.*

**H2 — occurrence identity + typed predicates (no algebra) suffices.**
Killed by: any pre-committed broader/narrower/overlap answer that typed
labels without per-dimension entailment get wrong or must return UNKNOWN —
e.g., failing `blue permanent ⊂ permanent` or wrongly ordering
`blue permanent` vs `nonland permanent`. *Expected to die on CROSSQ-5.*

**H3 — occurrence + typed predicates + derived algebra suffices (flat rows,
participant + relation coordinates included).**
Killed by: a benchmark card whose consumer-needed fact cannot be
represented by occurrence/participant/predicate/relation rows plus
predicate-valued references without nesting; or the algebra needing
operations beyond §E's closed table to answer pre-registered questions
(theorem-prover creep); or a normalization dimension demanding a growing
hand-list in both candidates. *The blind holdout is where this dies if it
dies.*

**H4 — nested minimal typed IR is necessary.**
Killed by: H3 surviving the entire benchmark including the holdout — zero
cards forcing nesting beyond reference-valued fields. Symmetrically,
*confirmed* by any single card that does force it; name the card.

The benchmark's purpose under this section is to find **the minimum rung at
which the kill conditions stop firing** — not to referee two pre-selected
brands.

---

# P. CORRECTIONS TO THE PRIOR ADDENDUM

| # | prior addendum said | this document |
|---|---|---|
| 1 | Standing-state caveat: Gate 2 RED, codebook reverted, backfill must be re-applied (§header, §M.2) | **Withdrawn as moot** — incident closed; state verified live (§A) |
| 2 | OCC-FACET extends `locality` to `[face, paragraph, occurrence]` (§A.1) | **Amended** — locality untouched; separate derived occurrence layer with prefix invariant INV-1 (§B) |
| 3 | Census key `(oracle_id, stem, occurrence)` treated as the primitive-in-waiting (§G) | **Amended** — evidence yes, design no; stem-scoped ordinals are classifier artifacts; segmentation-based `[face, paragraph, clause]`, `effect` reserved (§C) |
| 4 | "Argument identity is MIN-IR's one irreducible structural advantage" (§B.2) | **Withdrawn** — participant identity is a shared coordinate (§F) |
| 5 | "MPR < 5% favors OCC-FACET" (§J) | **Withdrawn** — premise dissolved; replaced by the qualitative rung gate (§N) |
| 6 | False-precision absolute veto stated against MIN-IR only (§J) | **Superseded** by the symmetric veto (§N, tier FIRST) |
| 7 | `no-compound-slug law` listed as a required OCC-FACET invariant (§A.2) | **Moved out of AQ4** — see below |
| 8 | Ladder framing; shared triple normal form; extraction taxonomy EXTRACT-0–U; traps-seeded population; pre-committed answers | **Survive unchanged**, with the normal form promoted to the scoring substrate and the taxonomy extended to the normalization layer (§I) |
| 9 | §D/§E/§F adjudications of Captain's three amendments (evidence boundary + riders; static coreference + scope locks; ChoiceGroup derived-not-stored) | **Survive unchanged** |

**On #7 (challenged per mandate §10):** the no-compound-slug law bundles an
*index/vocabulary policy* into a *canonical-representation benchmark*, and
it burdened only the conservative candidate. It is not needed to test
anything in §M. Recommendation: **option C** — replace it inside AQ4 with
the weaker invariant *"no canonical comparison may depend on compound-axis
membership; derived indexes carry a regeneration gate so they cannot become
a second source of truth"* — and defer the minting policy itself until
after AQ4, where it is an index-policy ruling for Captain. Compound axes
may well remain worth materializing as cheap discovery indexes precisely
*because* they become derivable.

---

# Q. FINAL ARCHITECTURE JUDGMENT

Direct answers, in the mandated order:

1. **Is occurrence identity alone sufficient?** No. It solves within-card
   attachment and nothing about comparison. (H1's expected kill.)
2. **Are typed canonical predicates the next required primitive?** Yes.
   Broader/narrower/incomparable is unanswerable over labels.
3. **Does Foundry need a small predicate algebra?** Yes — the §E table:
   set/interval operations over CR-closed vocabularies, conjunction, small
   unions, complements-as-values, three-valued verdicts. Derived, never
   stored; closed, not growing; and it pays twice, because cross-snapshot
   semantic diff is the same algebra applied to the same card across time.
4. **Is participant identity a separate architectural rung?** No — it is
   another coordinate on the shared model, available identically to both
   serializations. The prior claim is withdrawn.
5. **Do relation edges force nested IR?** No. Flat rows with typed edges
   and predicate-valued references carry every structure attempted in §G.
   The precise collapse point — where "flat" becomes "IR in relational
   form" — is the admission of predicate-valued fields.
6. **Does MIN-IR retain an irreducible expressive advantage?** No. Its
   remaining differences are canonical ownership, migration, guards,
   refresh behavior, and ergonomics — real, but tier-FIVE material, not
   expressiveness.
7. **Is the real question still "axes versus semantic IR"?** No. It is:
   *what is the minimum canonical semantic structure required for
   deterministic cross-card mechanical comparison, while preserving
   existing human rulings, provenance, and guard infrastructure?* This
   addendum adopts that formulation.
8. **Strongest hypothesis before the benchmark:** **(D) the
   occurrence/participant/predicate/relation fact model — with canonical
   ownership retained by the existing assertion/codebook substrate, i.e.,
   OCC-FACET as amended in §B, growing rungs only as §N's gate demands.**
   Options A–E are rungs of one model, not rivals: A ⊂ B ⊂ C ⊂ D, and E is
   D with nested serialization and moved ownership. D-with-codebook-
   ownership is preferred *before evidence* because tiers 1–4 are expected
   to tie via the shared normal form, and tiers 5–6 (cost, reversibility)
   currently favor the candidate that leaves 4,233 human assertions, the
   ruling corpus, and the guard stack untouched. MIN-IR (E) remains the
   falsification target the holdout could still vindicate.
9. **The measurement most likely to change this answer:** the
   **residual-exhaustion rate** — the fraction of qualifier-bearing clauses
   that parse to zero unclaimed residue. If it is low, ABSENT-PROVEN is
   rare, strict replacement starves under *both* candidates, and the whole
   strictness program needs rethinking before any architecture argument
   matters. Second: the **MEC rate + relation-kind diversity** — if
   sub-clause effect identity and proliferating edge kinds are common, the
   fragile-splitter coupling argues for identity living in a rebuilt
   per-snapshot artifact (MIN-IR-style ownership) rather than in ratified
   assertion-adjacent rows.
10. **Build first / keep unimplemented:** see §R.

---

# R. EXACT RECOMMENDATION FOR AQ4 IMPLEMENTATION ORDER

**Build, in order (all read-only against production truth):**

1. **The four prevalence probes**, probe-library-built
   (`import foundry_probe as p`), $0, deterministic:
   residual-exhaustion rate · MEC (multi-effect-per-clause) rate ·
   multi-participant rate · relation-kind diversity. Their outputs slot
   directly into §N's rung gate and §Q.9.
2. **The segmentation-based occurrence address** as a *probe artifact*
   (derived table + INV-1 prefix check), not a schema change.
3. **The benchmark population** per §K: cohorts, committed sampling script
   + seed, `sha256(seed₂)` holdout commitment, pre-committed §M answers
   with the answer-file hash recorded before any encoder exists.
4. **The shared normalized fact-table schema and the §E algebra — on
   paper**, with the dimension-exclusivity registry drafted as a decision
   sheet for Captain (it is ~10 CR-anchored rows and it is a
   ratification).
5. **Both encodings** (OCC-FACET as amended in §B; MIN-IR per the prior
   addendum §B), projected into the shared normal form; fill matrices,
   trap replay, negative controls per candidate.
6. **Evaluation** under §N's tiers and §O's kill conditions; holdout
   opened last; result filed as **AQ4's evidence packet with one decision
   sheet**. Captain rules.

**Must remain unimplemented until the benchmark yields evidence:** any
codebook schema change (including facet rows and the occurrence field on
anything stored); any vocabulary or dimension ratification beyond the
exclusivity-registry *sheet*; any extractor beyond benchmark scope; the
`effect` ordinal; index/minting policy (§P #7); Stage F; any migration
tooling; and — throughout — the existing axis model remains the operational
system, untouched.

---

*One sentence, for the record: the benchmark should no longer referee "flat
facets versus typed IR" — those are one architecture in two serializations
past the predicate-valued-field boundary — but should instead find the
minimum rung of one shared ladder (occurrence → predicate → participant →
relation → reference) at which every pre-committed consumer question is
answered PROVEN, with absence proven by residual exhaustion rather than
extractor silence, correctness protected by a symmetric one-wrong-fact
veto, and ownership decided last, by cost and reversibility, exactly where
a tie belongs.*
