# CANONICAL SEMANTIC UNIT — decision packet

**2026-08-13.** Read-only. No schema implemented, no codebook mutation, no DET
pass, no API calls. Gate 2 green (14 gates, 13 pass, 1 known-excused).

**Shipped artifact that changes: NONE.** This is a decision packet.

**These are not new questions.** They are `ARCHITECTURE-AUDIT.md` §13 **AQ4**
and **AQ5**, plus **FL-2** from `THESAURUS-FACT-LAYER-ARCHITECTURE-2026-08-13.md`
§8. This packet supplies the evidence and concrete options to *resolve* them.
No new decision IDs are minted.

---

# PART ONE — PLAIN ENGLISH

## The one-paragraph recommendation

Add an optional **address** to each existing tag-assertion saying *which
paragraph of which face of the card this evidence came from*. Change nothing
else. We measured that **98.6% of the 7,891 existing quoted assertions can be
given that address automatically**, with no human review and no guessing,
because the evidence quote already sits inside exactly one paragraph. This is
additive: every current tool keeps working, no tag is rewritten, no vocabulary
is created. It fixes the one thing that is actually broken today — the system
cannot tell that Active Volcano's "destroy" and "bounce" are two modes you
choose *between*, not two things it does. It does **not** solve Grand Abolisher
↔ Defense Grid, and this packet is explicit that nothing about addresses could.

## What is broken, in one example

**Active Volcano** reads:

```
Choose one —
• Destroy target blue permanent.
• Return target Island to its owner's hand.
```

Foundry today knows: *this card destroys permanents* and *this card bounces
lands*. Both true. But stored as a flat card-level bag, a Budget Swapper
looking for a destroy effect will offer this card, and a player who takes it
discovers the destroy comes at the price of not bouncing. **41 cards** measured
in this shape.

The fix is not more tags. Each tag already carries the exact bullet that proves
it. The system simply never wrote down *which bullet*.

## The six questions Captain actually has to answer

1. Do we need to know which ability a tag came from? *(Recommendation: yes.)*
2. Do we need to know which mode it came from? *(Yes — that is the 41 cards.)*
3. Should one ability be allowed to contain several smaller effects?
   *(Not yet. Later, and the design leaves room.)*
4. Should the tag point at the ability, or should the ability own the tags?
   *(Tag points at the ability. It is reversible; the other direction is not.)*
5. Does an effect address need to survive a card's wording being changed?
   *(No. Re-derive it each corpus refresh and halt when it will not re-derive.)*
6. Can old tags stay valid when we cannot locate their ability?
   *(Yes. 109 of 7,891 will not resolve; they keep working, unaddressed.)*

---

# PART TWO — CURRENT STATE

## What Foundry knows today

```
CARD  (oracle_id — the only card key)
 └── AXIS            e.g. rule:targeted-destroy-creature      "a fact"
      └── MEMBER     one card on that axis
           └── ASSERTION   why we believe it
                 class          human | rule-derived | llm
                 source_ref     batch-2 | det-patterns-v2:45
                 quote          "Destroy target creature."
                 corpus_ref     2026-07-04
                 evidence_status quoted
```

| question | answer today |
|---|---|
| What is an axis? | one ratified fact, named by the §1 slot grammar |
| What is a member? | one card holding that fact |
| What is an assertion? | one piece of evidence for it; a member may stack several |
| Where is evidence? | the assertion's `quote` |
| Where is provenance? | the assertion's `class` + `source_ref` |
| Where is corpus versioning? | the assertion's `corpus_ref` |
| How are parents derived? | **S1: derived, never hand-tagged** — union of children at index-build |
| Where is delivery? | in the axis *slug*, not the assertion |
| Where are modes? | nowhere — recoverable only by reading the quote |
| Where is effect locality? | **nowhere** |

**Live measurements:** 403 active axes · 7,930 assertions · 4,233 `human` ·
3,697 `rule-derived` · 0 `llm` · 39 with no quote.

**What is lost in the card-level bag:** which ability a fact came from, whether
two facts are mutually exclusive, and whether a cost/restriction governs a
given effect. Everything else survives.

## What already exists that people may not realise

- **`tier_engine.get_raw_faces`** is a single shared face reader; `foundry_common.full_oracle_text` delegates to it. Faces are already canonical.
- **`tier_engine.build_card_doc`** already produces per-face, per-paragraph, per-clause structure, and `emit_viewer.py` already carries `face_index`, `paragraph_index`, `clause_index` for Searcher A. **The coordinate machinery exists; the foundry just does not use it.**
- **`fx.deliveries_for_lines`** already separates loyalty abilities, Saga chapters, Class levels, modal bullets and both faces — verified live on 11 card shapes.
- **S4 already allows multiple parents**, and **S4a** ratifies that parent edges are unranked and equal. The hierarchy is already a DAG, not a tree — so multiple inheritance needs no new law.

---

# PART THREE — ONTOLOGY VERDICT

**"Effect record" is the wrong name and the wrong object.**

Two of the four cards this product is built around are **static abilities**,
not resolving instructions:

- **Grand Abolisher** — *"During your turn, your opponents can't cast spells or activate abilities of artifacts, creatures, or enchantments."*
- **Defense Grid** — *"Each spell costs {3} more to cast except during its controller's turn."*

Neither "does" an effect in the resolving sense. A record type named for
resolving instructions would exclude the canonical Searcher B example on day
one.

**Recommended object: the ABILITY, and the repository already has its
boundary.** CR 113.2c makes a paragraph an ability boundary, and CLAUDE.md
already records the refinement — *"a PERIOD is not an ability boundary; a
PARAGRAPH is"*, with CR 603.11/607.2h as the known exception where one
paragraph holds a static plus its linked triggers.

**Recommended name: semantic unit**, because CR 700.2 modes and CR 706.3b die
rows are addressable things that are *not* abilities, and the repository has
already ruled *"a mode is not an ability."* "Ability record" would be a
category error on exactly the 41 cards this fixes.

**Child effects: not now.** Kalitas's single ability performs destroy → create
token → set P/T. Splitting that into three peer records would need shared-target
and dependency edges immediately. Keeping it one unit is correct today and
leaves the child layer as a clean extension point.

---

# PART FOUR — THREE DESIGNS

## Design 1 — COORDINATES ONLY (additive)

**Summary.** Each assertion optionally gains an address naming the face and
paragraph (and mode path, where one exists) its quote came from.

| | |
|---|---|
| Authoritative | unchanged — axes, members, assertions |
| Added | one optional field on the assertion |
| Attachment | assertion → unit (tag points at ability) |
| Modal exclusivity | derived: two facts under different mode paths of one `Choose one` header are exclusive |
| Costs/triggers/restrictions | stay in the same paragraph as their effect; the address groups them |
| Parents | unchanged, S1 derived from axes |
| Corpus refresh | re-derive addresses; halt where a quote no longer resolves |
| Migration | **98.6% automatic** (7,782 / 7,891) |
| Reversibility | **total** — delete the field |
| Failure mode | cannot express relationships *within* one paragraph |

## Design 2 — SEMANTIC-UNIT CONTAINER WITH CHILD EFFECTS

**Summary.** A generated per-card artifact of units (and later child effects);
assertions point into it; axes stay the vocabulary.

| | |
|---|---|
| Authoritative | axes remain vocabulary; units become a second generated artifact |
| Added | a real artifact plus its own guards, determinism gate, and refresh reconciliation |
| Modal exclusivity | explicit `choice_group` on the unit |
| Parents | unchanged |
| Migration | same 98.6% backfill, plus building and gating the artifact |
| Reversibility | moderate — consumers start depending on the artifact |
| Failure mode | a second source of truth about the same card |

## Design 3 — PREDICATE-ROW PRIMARY (AQ4's larger arm)

**Summary.** Predicate/effect rows become primary; axes become saved queries
over them.

| | |
|---|---|
| Authoritative | **changes** — the row, not the axis |
| Migration | largest in the repository; 4,233 human assertions are filed under axes; S1–S7 and the whole naming grammar are built on the axis |
| Fixes at once | magnitude, role and level — the three things §4/§5 of the audit measured as missing |
| Reversibility | low |
| Failure mode | a rewrite of a working model before any consumer exists to receive it — the exact sequencing error the audit's headline finding names |

---

# PART FIVE — RECOMMENDATION

**Design 1 now. Design 2 as the named extension point. Design 3 stays AQ4 and
should not be decided by this packet.**

Reasons, in order of weight:

1. **It is measured, not estimated.** 98.6% backfills automatically; 109 assertions do not and stay unaddressed rather than guessed.
2. **It is the only fully reversible option.**
3. **It fixes the measured defect** — 41 flattened cards — and nothing else claims to.
4. **It reuses machinery that already exists** (`get_raw_faces`, `build_card_doc`, `deliveries_for_lines`).
5. **It does not pre-commit AQ4.** Design 2 and Design 3 both remain open on top of it.

**What it explicitly does NOT do — stated plainly because it matters:**
Grand Abolisher and Defense Grid are each a **single paragraph**. They have one
unit apiece. Addresses change nothing for them. Relating those two cards needs
*new fact dimensions* — who is restricted, when, which action classes,
prohibition vs taxation — which is AQ4/AQ5 work and is not unblocked by this
packet. Anyone who reads this recommendation as "this gets us Searcher B" has
misread it.

---

# PART SIX — BEFORE AND AFTER, REAL CARDS

### Case 1 — simple (baseline) · Erase
`Exile target enchantment.`
**Today:** one fact, `targeted-exile-enchantment`. **After:** same fact, address
`face 0 / paragraph 0`. **Prevents:** nothing — this is the baseline showing the
change is free.

### Case 2 — several actions in one ability · Kalitas, Bloodchief of Ghet
`{B}{B}{B}, {T}: Destroy target creature. If that creature dies this way, create a black Vampire creature token…`
**Today:** destroy fact + token fact, no link. **After:** both address the *same*
unit, so a consumer knows the token is part of the removal, and the
`{B}{B}{B}, {T}` cost governs both. **Prevents:** treating the token as a free
second ability. *(Child effects would split these three actions — deferred.)*

### Case 3 — modal exclusivity · Active Volcano
`Choose one — • Destroy target blue permanent. • Return target Island to its owner's hand.`
**Today:** destroys permanents **and** bounces lands. **After:** two units under
one `Choose one` header, marked exclusive. **Prevents:** the Budget Swapper
offering it as removal when the buyer may only get the bounce.

### Case 4 — choose two · Silumgar's Command
Four bullets, choose two. **After:** four units, one choice group, "pick 2" — so
*any two together* is legal but all four is not. **Prevents:** collapsing
"choose two" into "choose one" or into "does everything."

### Case 6 — planeswalker · Nicol Bolas, Planeswalker
`+3: Destroy target noncreature permanent.` / `−2: Gain control of target creature.` / `−9: …deals 7 damage…`
**Today:** 5 assertions, each with a quote that happens to carry its loyalty
cost. **After:** each addressed to its own unit, and the loyalty cost belongs to
the unit. **Prevents:** attaching the `−9` cost to the `+3` effect. *(Live
example of the gap: this card also carries an
`activation-restricted-to-sorcery-speed` assertion whose quote binds to no
ability at all.)*

### Case 7 — Saga · History of Benalia
`I, II — Create a 2/2 white Knight…` / `III — Knights you control get +2/+1…`
**After:** two units, chapter context retained per unit. **Prevents:** believing
the anthem and the token arrive together.

### Case 8 — Adventure · Brazen Borrower // Petty Theft
Flash / Flying / block restriction on face 0; the bounce on face 1.
**After:** the bounce addresses `face 1`. **Prevents:** treating a 3/1 flash
flier as a creature that also bounces on the battlefield — it bounces only when
cast as the Adventure half.

### Cases 9 & 10 — Grand Abolisher vs Defense Grid *(the honest one)*
Both are one paragraph, one unit. **Addresses change nothing.** What a future
functional layer would need: *who* is restricted (opponents vs everyone), *when*
(your turn vs not-controller's turn), *what* (cast + activate, limited to three
permanent types vs all spells), *mechanism* (prohibition vs +{3} tax),
*asymmetry* (asymmetric vs symmetric). **None of those dimensions exists today,
and this packet does not create them.**

---

# PART SEVEN — MIGRATION, MEASURED

| | live |
|---|--:|
| active axes | 403 |
| total assertions | 7,930 |
| `human` / `rule-derived` / `llm` | 4,233 / 3,697 / 0 |
| with an evidence quote | 7,891 |
| **anchor to exactly one unit** | **7,782 (98.6%)** |
| ambiguous across units | 39 |
| quote resolves to no unit | 70 |
| no quote at all | 39 |
| cards with modes | 876 |
| multi-face / multi-component cards | 836 |
| cards with 2+ paragraphs | 20,060 of 32,557 |
| axes ≥20 assertions anchoring 100% cleanly | **59** |

Easiest families first: `rule:cycling` (304), `created-token-enters-tapped`
(195), `create-token-creature` (184), `targeted-destroy` (172),
`enters-tapped-conditional` (168), `direct-damage-any-target` (112).

**Plan the evidence supports:** new rule-derived families emit addresses
immediately; existing quoted assertions backfill only where deterministic; the
109 that do not resolve stay unaddressed and are *reported*, never guessed;
consumers tolerate a missing address.

## Corpus refresh behaviour

| event | behaviour |
|---|---|
| new card | new units, addresses derived; no action |
| unchanged card | addresses re-derive identically |
| **Oracle errata** | quote no longer resolves → **halt and report**, never silently reattach |
| new mode/ability inserted | paragraph ordinals shift → re-derive; quote is the tiebreak |
| reworded but equivalent | resolves to none → reported for human reconciliation |
| unit disappears | reported |

**Identity recommendation: snapshot-local, deterministic, re-derived each
refresh, tiebroken by the quote — not a globally stable ID.** `corpus_ref`
already records the snapshot, and CLAUDE.md's halt-loudly rule already governs
the failure. A globally stable ID would be new machinery the product has not
been shown to need.

---

# PART EIGHT — CONSUMER FIT

**Searcher B.** Two-stage fits the static-site architecture: stage 1 uses the
card-level union (unchanged, cheap, good for candidate generation); stage 2
inspects addresses to reject false combinations. No dense all-pairs matrix
needed.

**Budget Swapper.** The strictest consumer and the main beneficiary — it can
finally require that action, object and cost come from the *same* unit. Still
blocked on magnitude and timing dimensions (AQ4/AQ5).

**Deck Completion.** Largely unaffected; it wants role, which is AQ5.

**Explainability.** Addresses make three of the six target explanations
truthful — *"these are mutually exclusive modes"*, *"this removal effect also
draws"*, *"the card draws elsewhere but this effect does not"*. The other three
need role/outcome dimensions that do not exist.

**Guards.** Addresses are re-derived and therefore gate-able exactly like the
existing lattice guards: determinism ×2, a resolve-rate ratchet, and a halt on
unresolved quotes. `foundry_ground_truth` already treats an unanchored quote as
fatal — the same mechanism, one field wider.

---

# PART NINE — CAPTAIN DECISION SHEET

Five decisions, each a *resolution* of an existing question, not a new ID.

### D-1 · Do tags need to record which ability they came from? *(resolves FL-2)*
**Why it matters.** Without it, Active Volcano looks like a card that destroys
*and* bounces. 41 cards measured.
**Evidence.** 98.6% of 7,891 quoted assertions anchor automatically.
**A.** Add an optional address. **B.** Leave card-level; consumers re-derive by string-matching quotes at query time.
**Recommend A.** B makes every consumer re-implement the same matching — the repository's most expensive recurring defect class.
**Hard to change later:** nothing. **Reversible:** entirely.
**Example:** Active Volcano stops reading as "destroy + bounce".

### D-2 · What is the addressable thing — ability, or ability plus child effects? *(scopes AQ4)*
**Why it matters.** Decides whether Kalitas is one unit or three.
**Evidence.** Kalitas's one ability performs three sequential actions sharing one target and one cost.
**A.** Unit only (paragraph/mode granularity). **B.** Unit + child effects now.
**Recommend A.** B needs dependency and shared-target edges immediately, and no consumer exists yet that requires them.
**Hard to change later:** little — children hang off units.
**Example:** Kalitas stays one unit; its token stays tied to its removal.

### D-3 · Which direction points at which? *(the reversibility question)*
**A.** Assertion carries the address. **B.** A units artifact lists the facts each unit satisfies.
**Recommend A.** One source of truth stays the codebook; B creates a second artifact describing the same card.
**Hard to change later:** B is hard to undo once consumers read it; A is a field deletion.

### D-4 · Must an address survive Oracle errata?
**A.** No — re-derive per snapshot, halt on unresolved. **B.** Yes — globally stable IDs.
**Recommend A.** `corpus_ref` already versions assertions and halt-loudly is house style.
**Example:** a reworded card reports for reconciliation instead of silently reattaching old evidence to a different ability.

### D-5 · What happens to the 109 assertions that will not resolve?
**A.** Stay valid and unaddressed; reported, ratcheted, never guessed. **B.** Block until every one is hand-resolved.
**Recommend A.** B converts a 98.6% automatic win into 109 hand rulings for 1.4%.
**Hard to change later:** nothing.

**Not asked here, deliberately:** AQ4's predicate-row migration, AQ5's `level`
field, magnitude, role, any functional-outcome taxonomy, controller/ownership
scope, `targeted-destroy-token`.

---

# APPENDIX — MINIMUM CONTEXT AN EXTERNAL REVIEWER NEEDS

*Sufficient to recommend a schema independently, without repository access.*

**A1. Assertion schema** — `experiments/out/foundry/codebook.json`, schema
`foundry-codebook/2`. Axis fields: `definition, history, members, merged_into,
parameterized, renamed_to, scope, source, status`. Member:
`{oracle_id, assertions[]}`. Assertion:
`{class, source_ref, quote, corpus_ref, evidence_status}`. `class` ∈
`human | rule-derived | llm`; `llm` is discounted and never gate-bearing
(CLAUDE.md, "Engine + foundry rules").

**A2. Scale** — 615 axes / 403 active; 7,930 assertions; 4,233 human, 3,697
rule-derived, 0 llm; 32,557 gated cards.

**A3. Parent law** — `docs/PARENT-TREE-CANDIDATES.md:10-32`. **S1** parents are
DERIVED (union of children at index-build; never hand-tagged with both child and
parent). **S2** most-specific-shared-node scoring, no double-dip. **S3** depth
ratified per family. **S4** multiple parents allowed. **S4a** (Captain-ratified
2026-08-02) parent edges are **unranked and equal**. **S5** implication edges.
**S6** parent names are user-facing vocabulary. **S7** proposed parents take the
family-tree evidence check. *A DAG is already law; multiple inheritance needs no
new ruling.*

**A4. AQ4, verbatim** — `docs/ARCHITECTURE-AUDIT.md` §13: *"Is the axis the
right primary object, or is the predicate row? … the axis is ratified law,
S1–S7 and the naming grammar are built on it, and 4,233 human assertions are
filed under it. The predicate row fixes magnitude, deck role and level in one
change instead of three… Migrating is the largest risk in this document."*

**A5. AQ5, verbatim** — same section: *"Add a `level` field, and if so, derived
from `source` or assigned per axis? … deriving from `source` is free and correct
by provenance but only splits DET-owned from human-owned, 39 against 364 …
per-axis means 403 hand rulings."* The audit's §5.2 finding: **the schema
records an axis's semantic level nowhere.**

**A6. FL-2** — `docs/THESAURUS-FACT-LAYER-ARCHITECTURE-2026-08-13.md` §8: should
`rule-derived` assertions carry a deterministic `face`/`ability`/`mode`
coordinate? Recommended there as a sub-item of AQ4.

**A7. Structured readers that already exist** —
`tier_engine.get_raw_faces` (the single shared face reader;
`foundry_common.full_oracle_text` delegates to it);
`tier_engine.build_card_doc` (per-face `matchable_paragraphs`, `clauses`,
`paragraph_tokens`); `tier_engine.build_indexes` (`paragraph_index`,
`clause_index`); `emit_viewer.py` (`face_index`, `paragraph_index`,
`clause_index`); `foundry_common.det_scan_texts` (canonicalized full text +
modal-bullet expansions); `foundry_shape_extractor.deliveries_for_lines`
(per-line delivery rows with modal inheritance).

**A8. Effect-locality and flattening findings** —
`docs/FULL-CARD-INFORMATION-CONSERVATION-2026-08-13.md`: text conservation
0 mismatches / 32,557; DROPPED 0, UNSCANNED 0, UNCONTEXTED 31 of 3,497; 625 of
836 multi-face cards have a face boundary indistinguishable from a paragraph
boundary in the joined string (guarded — 0 of 45 patterns match across a face);
**41 cards** carry 2+ object-lattice facts from mutually exclusive modes;
deleting an activation cost leaves the object fact unchanged.

**A9. Migration counts (this packet)** — quoted 7,891; anchor to exactly one
`(face, paragraph)` **7,782 = 98.6%**; ambiguous 39; unresolvable 70; quoteless
39; 59 axes with ≥20 assertions anchor 100%; 876 modal cards; 836 multi-face;
20,060 cards with 2+ paragraphs.

**A10. Product/artifact constraints** — `oracle_id` is the only card key; slug
does not exist in this repo. **No card data in git, ever** (`.gitignore`
enforces `data/`, `*.jsonl`, `*.sqlite`); `experiments/out/` is gitignored, so
generated foundry artifacts are local. Artifacts version under `/data/v/<date>/`
with `latest.json` written last. The site is static.

**A11. Mutation/ratification law** — new vocabulary is a ratification, not a
typo fix; codebook mutation requires Captain plus the backup law and runs only
through `foundry_membership_move.py` with a declared spec; DET patterns are
ratified in `docs/det-patterns-v2.json` under a fixed-seed sample gate whose
standing condition halts the pass before provenance writes; every generated
artifact takes a determinism ×2 byte-identical gate; ratchets carry no tolerance
constant. Grammar §5's OBJECT vocabulary bounds any emitted class slug.

**A12. Reachability caveat** — `foundry_reachability.py` reports **0 of 5**
foundry artifacts currently reaching a shipped card, and Gate 2 runs in no CI
(`.github/workflows/` holds only `build.yml`). Any schema recommendation should
assume the fact layer is not yet wired to the product.
