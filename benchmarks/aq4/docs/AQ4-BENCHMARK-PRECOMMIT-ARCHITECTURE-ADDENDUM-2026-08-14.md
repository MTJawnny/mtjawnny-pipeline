# AQ4 BENCHMARK — PRE-COMMIT ARCHITECTURE ADDENDUM

**2026-08-14. Read-only.** No code changed, no codebook mutation, no
vocabulary minted, no decision ID created, no benchmark implementation begun.
Companion to `docs/SEMANTIC-IR-PROPOSAL-REVIEW-2026-08-14.md`; this addendum
exists to make the eventual AQ4 experiment hard to bias, by steelmanning both
candidates and pre-registering the decision rules **before** any encoding
happens.

**Standing-state caveat carried from the prior review:** Gate 2 is RED on the
`locality` row this session — the working codebook was reverted to its
pre-backfill bytes (`b4197e94…`) at 15:00 on 2026-08-14 and carries zero
stored `locality` fields. Statements below about locality describe the
**ratified design** (`B-MIGRATION-DISCOVERY.md` §11), which is law regardless
of the working copy's current state. The reversion must be understood and the
backfill re-applied (Captain's word; documented $0 re-derivation) before any
benchmark consumes stored addresses.

**Two facts verified live this session that this addendum leans on:**

1. `foundry_locality.resolve()` returns exactly four dispositions — `OWNER` /
   `SPAN` / `AMBIGUOUS` / `UNRESOLVED` — and AMBIGUOUS arises when a *quote*
   matches multiple units (the backfill direction), not because the address
   space cannot separate them.
2. `foundry_qualifier_census.py` already keys clauses by
   `(oracle_id, stem, occurrence index)` via `finditer` over the canonical
   text. **The occurrence primitive this addendum discusses is not
   hypothetical — it exists in probe form and reproduced independently.**

---

## THE FRAMING THAT GOVERNS EVERYTHING BELOW — AQ4 IS A LADDER, NOT A FORK

Both candidate architectures are points on one ladder of coordinates:

```
paragraph owner            [face, paragraph]              ← RATIFIED (FL-2/A1–A4)
  └ clause occurrence      [face, paragraph, occurrence]  ← exists in probe form
      └ typed facet rows   {dimension, value} on an occurrence
          └ argument index which participant of the clause a facet restricts
              └ relation edges   occurrence ↔ occurrence (coreference, linkage, condition)
                  └ nested unit  the typed IR's serialization of all of the above
```

Every rung is justified — or not — by a measurable corpus population. The
conservative model is "stop at rung 3 unless forced"; the typed IR is "the
corpus will force rungs 4–5, so build the shape that carries them natively."
**The benchmark's real job is to measure how far down the ladder Foundry's
actual consumers force us**, and the decision rules in §J are written in
those terms. This reframing matters because it converts AQ4 from a
taste-shaped binary into a measured stopping point.

---

# A. STRONGEST CONSERVATIVE ARCHITECTURE — **OCC-FACET**

*(neutral benchmark name: **OCC-FACET**; the typed candidate in §B is
**MIN-IR**. Names chosen to carry no halo either way.)*

## A.1 The design

Everything that exists stays exactly as it is. Three additions, all inside
the existing assertion object:

1. **Third locality coordinate.** `locality: [face, paragraph]` extends to
   `[face, paragraph, occurrence]`, where `occurrence` is the ordinal of the
   classified clause within the paragraph's canonical text — the census's
   existing key, promoted from probe to schema. Snapshot-local, re-derived
   per refresh, halt on unresolved: **D-4's ratified identity law applies
   unchanged, one coordinate down.**

2. **Facet rows inside the assertion.** An optional
   `facets: [{dim, value, evidence_span?}]` array on the assertion. A facet
   inherits its assertion's occurrence address — attachment is by
   containment, so there is no new top-level object, no second artifact, and
   no join to get wrong. Dimensions come from the census's measured
   inventory: colour, subtype, supertype, negated-type, state,
   numeric-threshold, controller/owner, zone (origin/destination); later
   magnitude, timing, duration, condition. **Each dimension's value
   vocabulary is CR-closed** (CR 105.1 colours, CR 205 types/subtypes,
   CR 702 keywords) and parsed at run time — never a hand-list.

3. **One relation row type, used sparingly.** `rel: {kind, to: occurrence}`
   for the small set of cross-occurrence facts the CR itself defines
   statically: linked abilities (CR 607 — the repo already carries
   `LINKED-ABILITIES-CR607-2026-08-05.md`), same-card coreference ("that
   card"), and effect-conditional-on-effect (Kalitas's "If that creature
   dies this way").

Forward emission closes the ambiguity class: the DET matcher knows where it
matched, so **new facts are born with a full occurrence address** and
AMBIGUOUS remains what it is today — a legacy-backfill disposition for quotes
that appear verbatim in two units (Seize the Soul), reported and never
guessed.

## A.2 The checklist, answered without strawmanning

- **Active Volcano?** Yes, completely. Base facts on paragraphs 1 and 2 with
  addresses; `{dim: colour, value: blue}` on the destroy assertion;
  `{dim: subtype, value: Island}` + `{dim: zone-dest, value: hand,
  relation: owner-of-target}` on the bounce; exclusivity derived from the
  header per ratified A4.
- **Seize the Soul / identical clauses?** Yes, for everything emitted
  forward (the matcher knows its paragraph and ordinal). The legacy 39
  AMBIGUOUS assertions stay ambiguous — correctly, because *their evidence
  genuinely cannot say which unit it came from*, and no architecture can
  conjure that information. MIN-IR has the identical residue.
- **Multiple effects in one paragraph?** Yes — the occurrence ordinal
  separates Kalitas's destroy clause from its create-token clause;
  paragraph-level context (the `{B}{B}{B}, {T}` cost, delivery `activated`)
  governs both by paragraph containment.
- **Destination, magnitude, timing, condition, duration later?** Yes — each
  is a new facet dimension, each a ratification, none a schema change. The
  census's §C inventory is literally the roadmap.
- **Broad axes unchanged?** Yes, byte-for-byte. Facets refine assertions;
  axes never learn facets exist.
- **Human assertions without migration?** Yes. Facets are optional; the
  4,233 human assertions are untouched and gain facets only if a
  deterministic pass derives them from their own quotes.
- **Guard survival?** Nearly total: every Gate 2 row survives; the locality
  gate gains one coordinate; ratchets gain facet-coverage metrics.
- **New invariants required:** (i) facet-address conservation — every facet's
  occurrence must resolve to a live clause, same halt law as locality;
  (ii) facet-vocabulary closure per dimension, CR-derived, halt-guarded on
  content not cardinality; (iii) determinism ×2 on the occurrence
  derivation; (iv) a **no-compound-slug law** — once a facet dimension is
  ratified, minting a compound axis it can express is forbidden (this is a
  new grammar law and needs its own ratification; without it the ×9.7
  explosion continues in parallel with the fix).

## A.3 Where it strains — stated honestly, because this is the steelman's edge

Two shapes force additions that begin to re-derive the IR skeleton:

1. **Two restricted participants in one clause.** Prey Upon: *"Target
   creature you control fights target creature you don't control."* One
   clause, two targets, two controller facets — and
   `facets: [{controller: you}, {controller: not-you}]` on one occurrence
   cannot say which restricts which. OCC-FACET needs an argument coordinate
   (`arg: 0/1`) — rung 4.
2. **Cross-occurrence relations beyond the enumerable CR-defined set.** If
   the corpus forces many relation kinds, the single `rel` row grows into a
   typed edge vocabulary — rung 5.

**Does it become a semantic IR in disguise?** Once occurrence + facets +
argument index + relation edges all exist: structurally yes — it is the IR
in adjacency-list (relational) form rather than nested form. That is not a
defeat; it is the finding. At that point the remaining differences are
(a) where canonical truth lives, (b) migration blast radius, (c) guard
conservation — which §K quantifies — and *not* expressive power.

---

# B. MINIMAL TYPED-IR ARCHITECTURE — **MIN-IR**

## B.1 The design

A generated, snapshot-local artifact of semantic units; the codebook's axes
become derived indexes over it; assertions/evidence law unchanged in form.
Strictly two levels of nesting, no recursion:

```
unit:
  owner:        [face, paragraph, occurrence]     # same address space as OCC-FACET
  delivery:     §2 token (closed, existing)
  action:       §4 verb (CR-derived)
  participants: [ { object_class: §5,             # one entry per argument
                    restrictions: [{dim, value}], # same CR-closed facet vocab
                    role: target|affected|self } ]
  zones:        {origin?, destination?, relation?}
  quantity / optionality / duration / condition
  refs:         [{kind, to: unit-or-participant}] # static coreference only
  evidence:     quote (unchanged law)
  provenance:   class + source_ref + corpus_ref (unchanged law)
  disposition:  parsed | partial | ambiguous | unresolved | out-of-contract
```

Everything stops before: priority, state-based actions, layers, APNAP,
legal-action generation, replacement-loop execution, object-state mutation,
combat. A `prevent/replace` clause is *classified* (CR 614.1a–c template
family) and never *resolved*.

## B.2 The smallest capability OCC-FACET cannot represent cleanly

**Argument identity within one clause** — §A.3 item 1. That is the whole of
MIN-IR's irreducible structural advantage. Every other claimed advantage
(qualifier attachment, exclusivity, coreference, zones) is representable in
OCC-FACET with flat rows on the shared address space. MIN-IR carries argument
identity natively because `restrictions` live inside `participants`;
OCC-FACET carries it only by bolting an `arg` coordinate onto facets.

This means the benchmark's single most load-bearing number is:

> **What fraction of qualifier-bearing clauses have 2+ restricted
> participants?**

That is a cheap corpus-wide DET probe (fight templates, exile-and-return,
pump-then-fight, "attach … to …", two-target spells), and it should be run
**before** any hand-encoding, because it decides half the argument for the
cost of one probe. A second probe measures relation-edge pressure (rung 5):
how many cards need cross-occurrence edges, and of what kinds.

---

# C. IS THERE A GENUINE THIRD ARCHITECTURE?

**Candidate examined: the occurrence-keyed relational fact table** — a flat
store of `(occurrence, predicate, value)` triples plus
`(occurrence, relation, occurrence)` edges, axes as saved queries.

**Verdict: it is not a third architecture. It is the common normal form of
the other two.** OCC-FACET *is* this table sharded into assertion-contained
rows; MIN-IR *is* this table serialized as nested records. A relation/fact
graph, "typed relation rows without nesting", and the audit's §6.6 predicate
table all collapse into it. There is no third point that dominates — the
genuine decision axes are canonical-truth ownership, migration blast radius,
and guard conservation, and those have exactly two interesting settings.

**But the normal form earns its place methodologically:** the benchmark
should require both candidates' encodings of every card to be **mechanically
projected into the shared triple form**, and information-conservation scored
by diffing the projections. That turns "did architecture X lose the
restriction?" from a judgment call into a set difference — the same move
the conservation audits already made for text.

---

# D. EVIDENCE-BOUNDARY RULING RECOMMENDATION

**Adopt Captain's formulation, with two riders.**

My prior formulation — *provable by Oracle quote + CR rule number, without
game state* — is too narrow, and the extractor already violates it in
ratified ways:

- The CR 113.3a cut ("no instant/sorcery face → static") is decided by a
  **face characteristic**, not a quote.
- The DFC rule (`card_faces[0].image_uris`), layout identity, meld parts —
  characteristics.
- 340 vanilla cards have no oracle text on any face; their (non-)facts are
  characteristic-only.
- Type-line consumption (CR 205 parsing) is characteristic-based and
  load-bearing today.

Counterexample against Captain's formulation, which the riders close:
"immutable/canonical characteristics" can smuggle in **computed** fields. A
Scryfall `colors` field already incorporates characteristic-defining
abilities (Devoid, "~ is colorless") — it is the *output* of a rules
computation, i.e., a generated artifact, and *"a generated artifact is not
the CR."* Unbounded, the clause could also admit legalities, prices, rarity —
non-mechanical characteristics.

**Recommended boundary:**

> A canonical semantic fact belongs iff it is deterministically derivable
> from (a) the pinned corpus snapshot's **enumerated admissible
> characteristic fields**, and/or (b) Oracle text, plus the CR — without
> evaluating dynamic game state.
>
> **Rider 1 (closed field list):** the admissible characteristic fields are a
> ratified, enumerated schema contract (name, mana cost, type line, faces/
> layout, P/T, loyalty, colours, colour identity), each named with whether it
> is printed or snapshot-computed. Adding a field is a ratification.
>
> **Rider 2 (evidence law extended, not weakened):** a characteristic-derived
> fact cites its field and value as evidence, exactly as a text-derived fact
> cites its quote. Evidence-or-discard survives with two evidence kinds
> instead of one.

This is strictly better than both original formulations: mine excluded
ratified practice; Captain's unguarded admits derived artifacts as truth.

---

# E. STATIC-COREFERENCE RECOMMENDATION

**Accept Captain's distinction. It is necessary, it is CR-grounded, and it
is not creep — with the scope stated below.**

**Necessary — the blink test proves it with a consumer, not an aesthetic:**
Cloudshift reads *"Exile target creature you control, then return that card
to the battlefield…"*. Without the static edge "that card → the exiled
target", exile-and-return is indistinguishable from exile — and a Budget
Swapper asked for removal will offer a blink spell, which is a false
substitution as severe as Active Volcano's. Same structure: Kalitas's token
is conditional on *that creature* dying; delayed returns ("at the beginning
of the next end step, return it") are the flicker family. Strict replacement
and honest explanation **cannot** work without this; similarity merely
degrades without it.

**CR-grounded:** linked abilities are a static CR concept (CR 607), already
the subject of a repo ruling — the reference structure exists in the rules
text itself, independent of any game.

**Not creep, given three scope locks:** (i) same-card references only;
(ii) the edge names a participant/occurrence, never a game object — the
representation may say *"refers to the creature targeted by occurrence 0"*
and may never answer *"which creature is that now"*; (iii) an unresolvable
reference gets disposition `unresolved`, never a guess. The creep line is
crisp: **the moment any consumer question requires evaluating the reference
against a game state, that question is out of contract.**

**Consequence for the benchmark:** static coreference is a **shared
requirement of both candidates**, not a discriminator — OCC-FACET carries it
as its `rel` row, MIN-IR as `refs`. The blink cohort (Cloudshift, Oblivion
Ring's linked exile/return pair, a delayed-return card) is mandatory in EXT-2′.

---

# F. MODAL-STRUCTURE RECOMMENDATION

**Derived only — and materialized in generated artifacts, never stored in
the canonical codebook.** Engaging A1 directly:

A1's measurement — 1,791 paragraphs hold exactly one modal bullet, **zero**
hold two or more — established that the paragraph coordinate already
separates modes, so a stored **per-assertion** mode field would duplicate
information the address already carries. That measurement is untouched by
Captain's proposal, because a `ChoiceGroup → [paragraph A, paragraph B]`
relation is a **different object**: it lives at the header, not on the
assertion, and A4 already ratified its content (*"exclusivity is derived
from the owning header"*). Captain's structure is A4 given a shape, not A1
overturned.

The remaining question is storage vs. derivation, and the repo has already
run this experiment twice, with instructive opposite lessons: *"do not quote
the census as storage"* (a derived value reproduces itself even when the
stored field is stripped — measured when deleting all 7,808 addresses left
every gate green), and — today — a stored field silently vanished from the
working codebook and only a per-machine ratchet noticed. Both lessons point
the same way for exclusivity: **since ChoiceGroup is a pure function of
oracle text (header wording + CR 700.2), storing it in the codebook adds a
drift surface and no information.** Derive it at artifact-build time, where
units/occurrence tables are generated anyway; gate it with determinism ×2.

Selection cardinality must be part of the derivation — `{min, max}` parsed
from the header (*"Choose one"*, *"Choose two"*, *"Choose one or both"*,
*"Choose one or more"*) — with the known adversaries in the fixture set:
**Spree** (additive costs whose reminder text says "choose one or more" —
the reminder-strip law applies *before* the modality test, the recorded
trap), pawprint modes, and Escalate/Entwine (modal-with-rider shapes).

So: not "not represented" (consumers need it — the 41 cards), not
"canonical-stored" (A1's logic and today's reversion argue against), but
**derived-and-materialized**, in both candidate architectures identically —
which removes it as a discriminator and as a bias surface.

---

# G. "SEMANTIC OCCURRENCE IDENTITY" — THE SERIOUS ALTERNATIVE

**Finding: occurrence identity is the missing primitive for the measured
problem set. It is necessary under both candidates, and it is sufficient for
strictly more of the problem than the typed IR's marketing implies — but not
for all of it.**

The evidence that it is the right primitive:

- The qualifier census — the strongest pro-IR measurement in the repository —
  already **keys on it** (`(oracle_id, stem, occurrence index)`, verified
  live in the code this session). The number that motivates the IR was
  *produced by* the occurrence address.
- The locality arc's own trajectory: each measured failure fell to one more
  coordinate. Card-level bag → face (DFC cases) → paragraph (modes, A1) →
  occurrence (multi-clause paragraphs, identical-clause disambiguation for
  forward-emitted facts).
- Identity law already fits: snapshot-local, re-derived per refresh, halt on
  unresolved (D-4). An occurrence ordinal is exactly as fragile as a
  paragraph ordinal, and the ratified answer to that fragility already
  exists.
- What it buys without touching canonical truth ownership: qualifier
  attachment for every single-restricted-participant clause (the measured
  majority), Seize-the-Soul disambiguation for all forward-emitted facts, a
  home for zone/magnitude/timing facets, and the anchor for coreference
  edges.

What it does **not** buy — the two honest residuals from §A.3/§B.2:

1. argument identity inside a clause (Prey Upon);
2. a typed relation vocabulary, if the corpus forces one beyond CR 607 +
   coreference + conditionality.

**Therefore the benchmark's sharpest question is not "IR or not" but "who
owns the occurrence table":** in OCC-FACET the occurrence is a coordinate on
assertions in the existing codebook; in MIN-IR it is the spine of a new
canonical artifact. Same primitive, two ownership models. The two corpus
probes named in §B.2 — multi-participant rate and relation-edge pressure —
decide whether anything above the occurrence rung is load-bearing, and they
should run **first**, before any card is hand-encoded, because they are
cheap, deterministic, and settle the largest open question either way.

---

# H. EXTRACTION SCORING MODEL

Every populated field/facet/edge in every encoding carries exactly one
derivation class:

| class | meaning | precedent |
|---|---|---|
| **EXTRACT-0 STRUCTURAL** | from face/paragraph/clause machinery that exists (`get_raw_faces`, `sentence_spans`, occurrence finditer) | conservation-law territory |
| **EXTRACT-1 CR-CLOSED** | value from a closed CR enumeration parsed at run time (CR 105, 205, 702) | the CR-derivation law |
| **EXTRACT-2 TEMPLATE** | Oracle template with a CR anchor (`put into ‹DEST› from ‹ORIGIN›`; `target <class>`) | the determiner-slot lesson |
| **EXTRACT-3 FOUNDRY-PRIMITIVE** | existing ratified machinery (delivery classifier, object lattice, locality resolver) | reuse over re-derivation |
| **EXTRACT-4 COMPOSED** | pure function of EXTRACT-0–EXTRACT-3 outputs | |
| **H1 HUMAN** | per-card or per-axis human judgment | ratification law |
| **H2 HAND-LIST** | an open list a human typed that no CR rule closes | *"a defect with a delay"* — permitted only under the CR 207.2d exemption, cited |
| **U UNRESOLVED** | field deliberately carries an unresolved disposition | honesty requirement |

**Published outputs per architecture (no single weighted score — that would
be a tuning knob):**

1. **The fill matrix** — fields × derivation classes, per card and
   aggregated.
2. **H2 inventory** — every hand-list named, with size and **growth
   exposure** (does a new set release grow it? a growing hand-list is a
   recurring defect; a static one is a one-time risk). Headline number, not
   a weight.
3. **Anchor-free heuristic count** — derivation steps with no CR citation
   and no CR 207.2d exemption. Target 0; each one is named.
4. **Trap-replay score** — mechanical, not judged: run each proposed
   derivation against the benchmark's trap cohort (reminder-text inversion,
   ability-word prefixes, striations, voice/inflection sweeps, coordination
   splits) and count misparses. This is where "elegant but hard to extract"
   becomes a number.
5. **Negative-control obligation** — every S-class claim demonstrates one
   deliberately broken input that changes the output (the guard law; a
   derivation never shown to fail is not known to be a derivation).
6. **U-rate** — fraction of consumer-relevant fields left unresolved. High
   U with honest dispositions beats low U with confident wrong values;
   pair this metric with the false-precision check (a wrong confidently
   filled field found by the pre-committed answers counts 10× an
   unresolved one in §J's comparisons — the one place a multiplier is
   justified, because the repo's whole history says silent wrongness is the
   expensive class).

The comparison between architectures is then **lexicographic, not
weighted**: information-conservation vetoes first (§J), then H2/anchor-free
counts, then trap-replay, then U-rate, then complexity (distinct record
types + coordinates + relation kinds — a countable schema-size proxy).

---

# I. CONSUMER-QUESTION SET (pre-committed, 12 questions)

Answers for every benchmark card are written **before** any encoding — the
WIRE-RESULT discipline. Rules-engine-only questions are deliberately absent.

**Budget Swapper (strict) — PREQ-1–PREQ-7:**

1. What action does unit/occurrence U perform, on what object class?
   *(baseline; both must answer trivially)*
2. What eligibility restrictions apply to the affected object of U, with
   evidence for each? *(facet retrieval + attachment)*
3. Which restriction belongs to which participant, where U has more than
   one? *(the argument-identity discriminator — Prey Upon cohort)*
4. Is card B's eligibility for role R **broader, narrower, or incomparable**
   vs. card A's? *(the strictness partial order — requires value semantics:
   colour-set inclusion, numeric ≤, and subtype→type subsumption, the last
   already existing in the object lattice's CR 205.3g–q machinery)*
5. Which single fact prevents B from strictly replacing A? *(explanation of
   the failed constraint, with evidence)*
6. Are U1 and U2 alternatives, cumulative, or independent? *(ChoiceGroup —
   the 41-card cohort + Spree)*
7. Is this exile/removal linked to a return, and to what? *(static
   coreference — the blink cohort; the question that catches Cloudshift)*

**Similarity / discovery — PREQ-8–PREQ-10:**

8. What cost, timing, or activation restriction governs U? *(the Nicol
   Bolas "Activate only as a sorcery" binding; NC-C's deleted-cost shape)*
9. Which broad facts do A and B share, ignoring restrictions? *(broad
   retrieval must stay cheap — tests that OCC-FACET's untouched axes and
   MIN-IR's derived indexes both answer without assembling full structure)*
10. Which unit of A creates the similarity to B? *(ability isolation)*

**Explanation / honesty — PREQ-11–PREQ-12:**

11. Why did A match query Q? — every fact used, each with quote/field
    evidence and address. *(auditability end-to-end)*
12. Which clauses of A carry facts in no dimension, and with what
    disposition? *(the "not modeled yet vs. not present" distinction —
    information-conservation made queryable)*

PREQ-3, PREQ-4, PREQ-6, PREQ-7 are the discriminators; PREQ-1–PREQ-2, PREQ-8–PREQ-12 are shared floors an
architecture can only lose. Any question either architecture cannot answer
*without guessing* is scored as an information-loss event, not a style
point.

---

# J. PRE-COMMITTED DECISION RULES

Named before the benchmark runs, so results cannot be narrated into a
preferred outcome. The two corpus probes (§B.2: multi-participant rate MPR,
relation-pressure RP) run first and feed the rules.

**Choose A — OCC-FACET (current model + conservative extension) — if ALL
hold:**

- zero information-loss vetoes across PREQ-1–PREQ-12 on the full benchmark;
- **MPR < 5%** of qualifier-bearing clauses corpus-wide (i.e., argument
  identity is a bolt-on for a small cohort, not a spine), AND RP confined to
  the three CR-groundable kinds (CR 607 linkage, coreference,
  conditionality);
- H2 + anchor-free counts ≤ MIN-IR's;
- guard conservation strictly better (per §K, expected).

**Choose B — MIN-IR hybrid (typed units canonical, axes derived) — if ALL
hold:**

- ≥1 information-loss veto against OCC-FACET on a question MIN-IR answers,
  occurring in a population that matters (≥1% of corpus, or a named
  consumer-critical family — measured, not asserted); **or** MPR/RP high
  enough that OCC-FACET needs the argument coordinate *and* a typed relation
  vocabulary, at which point its schema complexity (record types +
  coordinates + relation kinds) measures ≥ MIN-IR's — the dichotomy has
  collapsed and MIN-IR is the cleaner spelling of the same structure;
- MIN-IR's H2 + anchor-free counts ≤ OCC-FACET's + 2 (extraction not
  materially worse);
- MIN-IR demonstrates, on the benchmark slice: (i) regeneration of the
  existing axes as derived indexes **matching current memberships exactly**
  for the covered cards, and (ii) mechanical mapping of every existing human
  assertion on those cards with zero provenance loss (explicit `unresolved`
  allowed, silent drops not);
- false-precision events (confidently wrong fields caught by pre-committed
  answers) = 0. **One confidently wrong canonical field is an absolute veto**
  — the repo's entire history says silent wrongness, not missing structure,
  is the expensive class.

**Choose C — INSUFFICIENT EVIDENCE — only if:**

- the corpus probes cannot be built deterministically, or the benchmark
  cannot discriminate *because the extraction stories of both candidates are
  indeterminate* (high U on both). **A tie on the merits is not outcome C —
  a tie is outcome A**, by the reversibility precedent (D-1…D-5: when
  evidence does not force the larger change, take the smaller reversible
  one).

**Absolute vetoes, either direction:** any card-specific production
exception (≥1 loses the point; ≥3 disqualifies the architecture — the ban is
law); any architecture unable to express `unresolved` without contaminating
exact consumers; any answer to PREQ-1–PREQ-12 that requires evaluating game state.

---

# K. MIGRATION / GUARD CONSERVATION COMPARISON

Per the "ask the runner" law, no fixed gate count is quoted; rows are
classified by category. The measured fact that frames this: **7 Gate 2 rows
read the codebook** (measured 2026-08-14 by moving it aside — `lint`,
`family_sweep`, `definition_drift`, `ground_truth`, `ground_truth_wide`,
`recorded_numbers`, `locality`); the text-pipeline rows (conservation,
visibility, punctuation, routing regression, reachability, gate audit,
qualifier census, probe guards, object-lattice gate) sit upstream of the
representation and survive **any** outcome.

## K.1 OCC-FACET

- **Literally applicable, unchanged:** the naming grammar §1–§13, S1–S7,
  every batch ruling, M8, A1–A4, D-1…D-5, evidence law, backup law, the
  ratification law. All 7 codebook-reading gate rows unchanged except
  `locality` (gains a coordinate).
- **New rulings needed:** facet-dimension vocabulary (one ratification per
  dimension), the occurrence-coordinate amendment (extends the locality
  ruling), the no-compound-slug law, the relation-row law.
- **New gates:** facet-address conservation, facet-vocabulary closure,
  occurrence determinism ×2, facet ground-truth seeds.
- **New failure classes (honestly stated):** facet mis-attachment (wrong
  occurrence — invisible to card-level diffs; the reason facet ground truth
  must ship with the first facet family, not after); the coordination-
  splitter traps recurring one level down (a facet claimed from inside a
  quantity phrase); stale facets after errata (covered by the existing halt
  law, but the *reporting* is new).
- **Rulings made obsolete:** none.

## K.2 MIN-IR

- **Literally applicable:** evidence law (extended per §D), the delivery §2
  token list (becomes a unit field's closed vocabulary), CR-derivation law,
  determinism/backup/durability law (P3/C6 transfers whole — the authority
  architecture was deliberately representation-agnostic), A1 (satisfied by
  derivation, remains binding on the canonical store), S1–S7 (parents over
  *derived* axes — applicable after re-scoping).
- **Become projection rulings:** the naming grammar — axes are now views, so
  §1–§13 governs the *projection function*, not the canonical store. Still
  needed, re-keyed. The slug-dossier machinery must gain a projection layer
  or the 77-rulings-under-former-names problem recurs at full corpus scale.
- **Obsolete in current form:** compound-axis anti-explosion pressure
  (structural under MIN-IR); M8's per-class instantiation (satisfied by
  construction — the ruling's *intent* is preserved, its mechanism retired).
- **Adapted (rewritten against new keys):** `definition_drift` (C-checks key
  on slug grammar today), `recorded_numbers` (re-derives §2 counts),
  `ground_truth` (seeds survive as data; the grader re-targets),
  `family_sweep`, `lint`, `locality` (absorbed into unit ownership). That is
  **the majority of the codebook-reading half of Gate 2 rewritten**, and the
  measured base rate for new guards is 3-of-8 negative controls mis-aimed on
  first pass.
- **New gates required:** derived-index regeneration equivalence (axes
  rebuilt from units must match ratified memberships — a large,
  permanently-running gate), unit-boundary stability across extractor
  versions (the recertification-pressure guard), disposition honesty
  (false-precision detector).
- **New failure classes:** unit identity churn on refresh; false precision;
  projection drift (axes silently diverge from units); and — importantly —
  **"a ratified token with no emitter" is NOT eliminated**, it transforms
  into "a unit field with no extractor," same failure in new clothes. *"More
  typed" is not "fewer bugs"; it is a different bug inventory*, and the
  benchmark's §H trap-replay is where that inventory gets priced.

## K.3 The asymmetry, in one sentence

OCC-FACET conserves essentially the entire ruling corpus and guard stack and
adds ~4 gate rows; MIN-IR conserves the laws-as-principles and the upstream
text guards but rewrites most codebook-keyed gates and adds a standing
regeneration-equivalence obligation — and that difference is a *measurable
line item* in the benchmark (§J), not an argument to wave at.

---

# L. WHAT WOULD FALSIFY MY CURRENT HYBRID-IR PREFERENCE

My prior review named the hybrid the "current leading hypothesis." I abandon
it if:

1. **The corpus probes come back low** — MPR < 5% and RP confined to the
   three CR-groundable kinds. Then argument identity is a bolt-on for a
   cohort, not a spine, and §30's *"if the improvement is marginal, keep the
   current architecture"* rules directly.
2. **OCC-FACET clears PREQ-1–PREQ-12 with zero information-loss vetoes**, including
   PREQ-3/PREQ-4/PREQ-6/PREQ-7 — the discriminators — with H2/anchor-free counts no worse
   than MIN-IR's.
3. **MIN-IR's extraction profile is materially worse** — nesting demands
   slot-filling the corpus cannot support deterministically, showing up as
   high U rates or hand-list dependence on the fill matrix.
4. **MIN-IR fails the regeneration-equivalence demonstration** on the
   benchmark slice — if it cannot reproduce today's ratified memberships as
   derived indexes even at 35-card scale, migration risk is unbounded.
5. **Any false-precision event in MIN-IR's canonical layer** during the
   benchmark. One confidently wrong typed field, caught by a pre-committed
   answer, is the failure mode the entire repository is built to prevent,
   and it weighs more than every elegance argument combined.

Symmetrically, what would harden the preference: MPR high, relation kinds
multiplying, OCC-FACET needing three bolt-on coordinates to pass PREQ-3/PREQ-7, and
the two fill matrices coming out equivalent — at which point MIN-IR is the
same structure spelled once instead of accreted.

---

# M. FINAL RECOMMENDATION FOR THE AQ4 BENCHMARK DESIGN

1. **Run the two corpus probes first** (multi-participant rate; relation
   pressure). Deterministic, $0, probe-library-built (`import foundry_probe
   as p`), and they settle the largest structural question before a single
   card is hand-encoded. Their numbers slot directly into §J's thresholds.
2. **Re-apply the locality backfill before benchmark work consumes
   addresses** (Captain's word; it is the documented deterministic
   re-derivation) — and understand today's reversion first; the benchmark
   must not be built on a working copy whose ratified field is absent.
3. **Encode both named candidates** — OCC-FACET and MIN-IR — over the EXT-2′
   card set from the prior review (traps-seeded, ~35 cards, now plus the
   Prey Upon multi-participant cohort and the Cloudshift blink cohort),
   every card carrying pre-committed answers to PREQ-1–PREQ-12 written before
   encoding.
4. **Project both encodings into the shared triple normal form** (§C) and
   score information conservation by mechanical diff.
5. **Publish the §H fill matrix, H2 inventory, trap-replay scores, and
   negative controls** for both; no single weighted score.
6. **Apply §J's pre-committed rules**; a tie is outcome A by the
   reversibility precedent.
7. **File the whole thing as AQ4's evidence packet with one decision
   sheet.** Captain rules. Nothing here ratifies anything; the boundary
   recommendations in §D/§E/§F are proposals to be ruled on that sheet, and
   the three amendments Captain proposed are — per this addendum's
   adjudication — accepted (D, with two riders), accepted (E, with three
   scope locks), and accepted-as-derived-not-stored (F).

---

*One paragraph, for the record: both candidates are points on one ladder of
coordinates over the same occurrence primitive — a primitive the qualifier
census already uses and the locality arc already half-built. The benchmark's
job is not to pick a philosophy; it is to measure how far down the ladder
the consumers force us, with the decision rules written before the first
card is encoded so that neither elegance nor sunk cost gets a vote.*
