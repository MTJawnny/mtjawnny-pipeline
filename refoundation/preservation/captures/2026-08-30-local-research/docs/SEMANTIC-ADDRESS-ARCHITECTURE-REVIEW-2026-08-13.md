# SEMANTIC ADDRESSES — architecture review and verdict

**2026-08-13.** Read-only. Nothing implemented, no schema field added, no
codebook mutation, no DET pass, no API calls, no vocabulary created. Gate 2
green (14 gates, 13 pass, 1 known-excused).

**Shipped artifact that would change if this were later implemented: NONE**,
and that stays true after implementation. `foundry_reachability.py` reports
**0 of 5** foundry artifacts reaching a shipped card. This is substrate work.

---

# A. VERDICT — **RATIFY WITH AMENDMENTS**

The concept is correct and is the right next step. **Four amendments**, all
forced by live measurement, one of which corrects a number I published in the
previous packet.

| # | amendment | why |
|---|---|---|
| **A1** | **Drop the mode-path component.** Face + paragraph is already sufficient to separate modes. | Measured: **1,791 paragraphs hold exactly one bullet; ZERO hold two or more.** The brief's §6 premise — *"one paragraph with a modal header and several mutually exclusive bullets"* — **does not occur in this corpus.** |
| **A2** | **The address must permit a contiguous SPAN**, not only a single unit. | **39 quoted assertions legitimately cover a whole modal block** (header + bullets). Active Volcano — one of the 41 flattening cards — is one of them. Under a single-unit-only rule these become "unresolvable" and the motivating card cannot be addressed. |
| **A3** | **Derivation must try BOTH text representations** (verbatim and CARDNAME-canonicalized). | Human quotes are verbatim; DET quotes are canonicalized. Matching one only: raw-only **98.6%**, canonical-only **93.7%**, either **99.44%**. Canonical-only would wrongly orphan **423 human assertions**. |
| **A4** | **Exclusivity is DERIVED, never stored on the address.** | The owning header is the nearest preceding non-bullet paragraph on the same face: **1,783 of 1,791 bullets** resolve deterministically. The 8 exceptions are Celebr-8000's CR 706.3b die table, which the repository already rules is **not** modal. |

With those, ratify. Without A2 and A3 the ruling would be measurably wrong.

---

# B. PLAIN ENGLISH — what the engine learns that it does not know today

Today Foundry knows *"Active Volcano can destroy a permanent"* and *"Active
Volcano can bounce a land."* Both true. It does not know they are two options
you **choose between**.

The address is a note on each piece of evidence saying **which line of which
side of the card it came from**. That is all. From that one note the engine can
work out that two facts came from different bullets under the same "Choose
one —" header, and therefore cannot both happen.

It does not decide what a card *does* for a deck. It does not create roles,
magnitude or timing. It stops the engine claiming a card does two things at once
when the card makes you pick.

---

# C. WHAT REMAINS UNCHANGED

Axes · memberships · assertion provenance (`class`, `source_ref`,
`corpus_ref`, `evidence_status`) · evidence quotes · parent law S1–S7 ·
card-level feature union · mutation law (`foundry_membership_move.py`, backup
law, Captain ratification) · every current consumer, which can ignore the field
entirely.

---

# D. THE ADDRESS — minimum information

Three components, names deliberately provisional:

1. **card** — the existing `oracle_id`. No change.
2. **face** — index into `tier_engine.get_raw_faces`, the single shared face reader.
3. **paragraph** — index of the non-empty line within that face.

Optionally, per A2, **an end paragraph** so the address can name a contiguous
span.

**No parallel indexing is invented.** `tier_engine.build_card_doc` already
produces per-face / per-paragraph / per-clause structure and `emit_viewer.py`
already carries `face_index`, `paragraph_index`, `clause_index` for Searcher A.
This is that coordinate, written down next to the evidence.

**Clause index is deliberately excluded.** No measured defect requires
sub-paragraph granularity, and CR 113.2c makes the paragraph the ability
boundary.

---

# E. MODAL / SUBUNIT — face + paragraph IS sufficient

**This is the amendment that most changes the proposal, and it simplifies it.**

| measurement | result |
|---|--:|
| paragraphs containing exactly one bullet | 1,791 |
| paragraphs containing 2+ bullets | **0** |
| bullets whose owning header is the nearest preceding non-bullet paragraph | 1,783 |
| exceptions | 8 — all Celebr-8000, a CR 706.3b die table, already ruled non-modal |

Scryfall's Oracle formatting puts every mode on its own line. The paragraph
index *is* the mode path. Adding a separate mode component would encode
information the paragraph index already carries — a second source of truth for
the same fact.

**Exclusivity is a derived relationship, not part of the address** (A4).

---

# F. UNADDRESSED-ASSERTION RULE — endorsed as written

> An unaddressed assertion may still prove that the card has the fact.
> It may not prove that this fact co-occurs with another fact in the same
> semantic unit.

This is the correct conservative behaviour and it is repository-native: it is
the same shape as `--gaps` reporting inside a bucket it cannot decide, and the
same shape as *"zero members is a hypothesis, not an absence."* It lets
migration be partial without licensing a guess.

**One addition:** the *count* of unaddressed assertions should be ratcheted, so
coverage cannot silently decay. Precedent: `foundry_audit_baseline`.

---

# G. CHILD EFFECTS — correctly deferred

Not required now. The measured consumer defect is **between** units (modal
exclusivity), not **within** one.

Tested against the hardest live case — **Kalitas, Bloodchief of Ghet**:
`{B}{B}{B}, {T}: Destroy target creature. If that creature dies this way, create
a black Vampire creature token. Its power is equal to that creature's power…`
Three sequential actions, one shared target, one shared cost, an "if you do"
dependency and a characteristic-setting rider. Splitting this now would require
*happens-after*, *conditional-on*, *shares-target-with* and *refers-to-object-from*
edges immediately — four relationship types, to solve zero measured defects.

**The exact future signal that should reopen it:** a consumer needs to
distinguish two facts *inside one paragraph* — the concrete case being a Budget
Swapper that must tell "destroys a creature and its controller draws" from
"destroys a creature and **you** draw." Until a consumer actually asks that,
unit-level grouping is sufficient.

---

# H. MIGRATION — measured at HEAD, with denominators

**Correcting my own prior number.** The packet's 98.6% was computed by matching
quotes against **raw** paragraphs only. That undercounts, because DET quotes are
canonicalized. Correct method (A3), matching either representation:

| | count | of quoted (7,891) | of all (7,930) |
|---|--:|--:|--:|
| addressable to exactly one unit | **7,808** | 98.95% | 98.46% |
| addressable to a contiguous span | 39 | 0.49% | 0.49% |
| **addressable total** | **7,847** | **99.44%** | **98.95%** |
| ambiguous (quote appears in 2+ units) | 40 | 0.51% | — |
| unresolved | 4 | 0.05% | — |
| quoteless | 39 | — | 0.49% |
| **unaddressed after migration** | **83** | — | **1.05%** |

Provenance of the addressable: 4,164 `human`, 3,644 `rule-derived`.
Totals reproduce at HEAD: 7,930 assertions, 403 active axes, 0 `llm`.

**Method sensitivity, stated because it is large:** raw-only 98.6%,
canonical-only 93.7%, either 99.44%. A five-point swing from a preprocessing
choice — the repository's recorded *"a probe must consume the same preprocessing
as the classifier"* trap, here with **two producer classes using two different
preprocessings**.

---

# I. LOCALITY ≠ SEMANTIC CORRECTNESS

An address says *where the evidence came from*. It says nothing about whether
the axis membership is right. A perfectly addressed assertion can still sit on
the wrong axis — `foundry_definition_drift` C4 measured 93 memberships across 22
active axes contradicting their axis's scope/targeting claim.

**The address must not be treated as a correctness signal**, and no existing
guard should be relaxed because coverage is high. Locality guards and semantic
guards are independent.

---

# J. PARENT COMPATIBILITY — unchanged, verified

**S1** parents are DERIVED (union of children at index-build, never hand-tagged
alongside a child) · **S2** most-specific-shared-node, no double-dip · **S3**
depth ratified per family · **S4** multiple parents allowed · **S4a**
(Captain-ratified 2026-08-02) parent edges are **unranked and equal** · **S5**
implication edges · **S6** parent names are user-facing · **S7** family-tree
evidence check.

The address touches none of it. **Parent derivation stays card-level.**
Effect-local parent derivation is a clean extension point and is not needed:
S4/S4a already make the graph a DAG, so multiple inheritance requires no new law.

---

# K. CONSUMER IMPLICATIONS

**Gameplay-outcome similarity.** Stage 1 candidate generation keeps using the
card-level union unchanged; stage 2 uses addresses to reject false combinations.
Sparse and explainable — no dense all-pairs matrix. **Creates no new roles or
outcomes.**

**Budget replacement.** The main beneficiary. Can finally require action, object
and cost to come from the same unit, and can see that destroy/bounce are
exclusive. **Still blocked on magnitude and timing**, which do not exist as
dimensions (AQ4/AQ5).

**Deck completion.** Foundational only. Needs role and synergy, which are AQ5.
**The address does not solve deck completion.**

**Grand Abolisher ↔ Defense Grid — unchanged and worth repeating.** Both are
single-paragraph statics: one unit each. Addresses do nothing for them. Relating
them needs *who is restricted, when, which action classes, prohibition vs tax,
asymmetry* — none of which exists. Anyone reading this ratification as progress
toward Searcher B's headline example has misread it.

---

# L. FALSIFICATION — five real cards, classified

| # | card / shape | finding | classification |
|---|---|---|---|
| 1 | **Erase** — `Exile target enchantment.` | one unit, one fact, address trivial | **solved / baseline** |
| 2 | **Active Volcano** — `Choose one — • Destroy target blue permanent. • Return target Island…` | bullets are separate paragraphs, so modes separate cleanly — **but its own human quote spans the whole block** | **requires refinement A2** |
| 3 | **Kalitas** — cost + destroy + token + P/T rider in one paragraph | one unit; facts inside it genuinely co-occur and share a cost | **acceptable known limitation** → future child-effect signal |
| 4 | **Kirtar's Wrath** — quote `"can't be regenerated"` appears in **2** paragraphs | short rider fragments cannot be localized; 40 assertions total | **acceptable known limitation** (0.51%) |
| 5 | **Nicol Bolas, Planeswalker** — `Activate only as a sorcery` binds to no ability | a restriction whose quote names no effect; addressing it points at a paragraph that is not the thing it restricts | **semantic-correctness problem, not locality** |
| 6 | **Celebr-8000** — 8 bullets under a die-roll header | bullets with no CHOOSE header; CR 706.3b, one ability | **acceptable — already ruled non-modal** |

**Nothing found was fatal.** Two limitations are acceptable and bounded; one
needs amendment A2; one is a pre-existing semantic-correctness issue the address
neither causes nor fixes.

---

# M. GUARD PLAN (not implemented)

| guard | reuses |
|---|---|
| address derivation is deterministic, ×2 identical | the standing determinism ×2 gate |
| every addressed quote still resolves to the same unit | `foundry_ground_truth`'s fatal **unanchored-seed** check — the exact mechanism, one field wider |
| no silent reattachment after Oracle errata | halt-loudly house style; `corpus_ref` already versions the snapshot |
| coverage ratchet on addressed / unaddressed counts, with exact denominators | `foundry_audit_baseline` (`WORSE_IF_DOWN`) |
| modal negative control: two facts under one header must read exclusive | object-lattice `--fixtures` / class-anchor precedent |
| face/component negative control | the existing face-drop control (NC-B) |
| ambiguous-quote negative control | new, but same inline-fixture shape |
| unaddressed assertion still valid at card level, and cannot prove co-occurrence | assertion-level unit test |

All belong in **Gate 2**, and Gate 2 still runs in **no CI** — every guard here
inherits that.

---

# N. CAPTAIN RULINGS REQUIRED — this resolves FL-2

**No new decision IDs.** This is the resolution of **FL-2**
(`THESAURUS-FACT-LAYER-ARCHITECTURE-2026-08-13.md` §8), which asked whether
`rule-derived` assertions need deterministic effect coordinates. The answer is
yes, and it extends to `human` assertions too.

**One ruling to approve, four amendments inside it:**

> Approve the semantic-address concept as drafted, amended by:
> **A1** no mode-path component — face + paragraph already separates modes;
> **A2** the address may name a contiguous span of paragraphs;
> **A3** derivation matches either verbatim or canonicalized text;
> **A4** modal exclusivity is derived from the owning header, never stored.

**AQ4 and AQ5 remain open and are not touched.** This ruling does not decide
the predicate row, the `level` field, magnitude, role, scope, or any outcome
taxonomy.

---

# O. LINE-BY-LINE VERDICT ON THE DRAFT RULING (§25)

| draft sentence | verdict |
|---|---|
| Axes, members, assertion stacks remain source of truth | **supported** — 403 active axes, 7,930 assertions, S1–S7 built on the axis |
| Assertion may optionally carry a deterministic semantic address | **supported** — 99.44% of quoted derive automatically |
| Address distinguishes face, paragraph/ability boundary, **and a narrower mode/subunit** | **REQUIRES AMENDMENT (A1)** — measured 0 paragraphs with 2+ bullets; the mode/subunit component is redundant |
| The field is additive | **supported** — every consumer can ignore it |
| Unaddressed assertions remain valid card-level evidence | **supported** |
| Unaddressed assertions do not establish same-unit co-occurrence | **supported**, and add a coverage ratchet |
| No child-effect decomposition ratified | **supported** — Kalitas shows the cost of doing it now |
| No new roles/outcomes/magnitude/scoring | **supported** |
| Locality and semantic correctness independently validated | **supported** — `definition_drift` C4 found 93 memberships contradicting their axis |
| Addresses snapshot-local, re-derived, unresolved changes reported not guessed | **supported** — `corpus_ref` + halt-loudly precedent |
| Parent derivation law unchanged | **supported** — S1–S7 untouched |
| *(absent from the draft)* | **REQUIRES NEW RULING (A2)** — spans, for 39 whole-modal-block quotes |
| *(absent from the draft)* | **REQUIRES NEW RULING (A3)** — dual-representation matching; a five-point swing and 423 human assertions |

---

# P. IMPLEMENTATION HANDOFF (roadmap only, after ratification)

1. A derivation helper next to `foundry_common`'s text pipeline, consuming
   `tier_engine.get_raw_faces` — no parallel indexing.
2. Emit addresses in **new** rule-derived output first (the object lattice is
   the natural first family; `rule:cycling` 304, `create-token-creature` 184,
   `targeted-destroy` 172 are the cleanest backfills).
3. Backfill existing assertions only where deterministic; report the rest.
4. Guards from §M, registered in Gate 2 as one runner with one exit code.
5. Consumers tolerate a missing address indefinitely.

**Not in scope:** AQ4's predicate row, AQ5's level field, child effects, global
stable IDs, roles, magnitude, ranking, CI.

---

# Q. GIT STATE

```
 M docs/PICK-UP-HERE.md
 M docs/RATIFIED-RULINGS-REGISTRY.md
 M docs/det-patterns-v2.json
 M experiments/foundry_audit_baseline.py
 M experiments/foundry_det_pass.py
 M experiments/foundry_gate2.py
 M experiments/foundry_object_lattice.py
?? docs/CANONICAL-SEMANTIC-UNIT-DECISION-PACKET-2026-08-13.md
?? docs/FULL-CARD-INFORMATION-CONSERVATION-2026-08-13.md
?? docs/OBJECT-LATTICE-RESIDUAL-RULING-2026-08-13.md
?? docs/SEMANTIC-ADDRESS-ARCHITECTURE-REVIEW-2026-08-13.md
?? docs/THESAURUS-FACT-LAYER-ARCHITECTURE-2026-08-13.md
```

No commit.
