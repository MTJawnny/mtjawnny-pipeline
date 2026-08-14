# SEMANTIC ADDRESSES — final pre-implementation check

**2026-08-13.** Read-only. Nothing implemented, no field added, no migration, no
codebook mutation, no DET pass, no API calls, no vocabulary. Gate 2 green
(14 gates, 13 pass, 1 known-excused).

**Shipped artifact changed by this task: NONE.** And if implementation later
proceeds: still none — `foundry_reachability.py` reports **0 of 5** foundry
artifacts reaching a shipped card. This is substrate work.

---

# VERDICT — **PASS TO IMPLEMENTATION**

Both remaining uncertainties resolve, and neither requires a guess.

**Question 1 resolves in an unexpected way: no span assertion ever needs to be
narrowed to one owner.** Of the 39 multi-paragraph quotes, **zero** are cases
where a fact belongs to one bullet inside a wider quote. 17 are facts that
genuinely describe the whole modal structure, 13 are misfiled memberships
belonging to the correctness path, and 9 stay unaddressed. The
"broad quote forces a broad owner" failure the brief was built to prevent
**does not occur in this corpus.**

**Question 2 resolves to a rule with no tie to break.** Raw and canonical
matching **never disagree**: Case F (each resolving to a *different* single
unit) is **0**, and neither representation ever narrows the other (Cases D and
E are both **0**). So union-of-representations, accept-iff-exactly-one is
deterministic, is not first-match-wins, and privileges no producer class.

---

# 1. CURRENT HEAD COUNTS

403 active axes · **7,930** assertions · 4,233 `human` · 3,697 `rule-derived` ·
0 `llm` · **7,891** quoted · 39 quoteless.

---

# 2. RAW / CANONICAL RESOLUTION MATRIX

| case | meaning | count |
|---|---|--:|
| **A** | both representations agree on one unit | **7,364** |
| **B** | raw resolves one, canonical none | 418 |
| **C** | canonical resolves one, raw none | 26 |
| **D** | canonical narrows a multi-hit raw | **0** |
| **E** | raw narrows a multi-hit canonical | **0** |
| **F** | each resolves one, **different** units | **0** |
| **G** | multiple / ambiguous | 40 |
| **span** | quote crosses unit boundaries | 39 |
| **H** | neither resolves | 4 |
| — | quoteless | 39 |

Single deterministic owner = A + B + C = **7,808**.

**Cases B and C are why A3 was required.** Raw-only orphans the 26 canonical
DET quotes; canonical-only orphans the 418 verbatim human quotes. Neither
producer class may be privileged, and the matrix shows neither needs to be.

---

# 3. QUESTION ONE — the 39 multi-paragraph quotes, fully enumerated

| outcome | meaning | count |
|---|---|--:|
| **A** | one deterministic owner inside a wider span | **0** |
| **B** | the fact genuinely owns the whole span | **17** |
| **C** | several owners possible, no deterministic rule | **9** |
| **D** | membership semantically suspect — not a locality problem | **13** |

**Outcome B (17)** — every one is `rule:modal` (13) or `rule:etb-modal-choice`
(4). The asserted fact *is* the CR 700.2 modal structure. Whole-span ownership
is semantically correct here, not a flattening failure, and §14's warning
("do not solve difficult rows by widening the owner") does not apply: the fact
is multi-unit **by nature**.

**Outcome D (13)** — all on `rule:grants-trample-to-creatures-with-counters`,
defined as *"grants a keyword ability to whichever creatures happen to have a
+1/+1 counter on them."* Avatar of the Resolute prints `Reach, trample` and
simply **has** trample; Bioessence Hydra likewise. These members contradict
their axis's own definition. **Routed to the semantic-correctness path
(`foundry_definition_drift`), not forced into an address** — live proof of §10's
separation.

**Outcome C (9)** — one each on `rhystic-tax`, `mass-damage-creatures-and-players`,
`fixed-lifegain`, `conditional-buff-by-color`, `landfall-self-pump`,
`draw-cards-with-life-loss-cost`, `aura-locks-enchanted-creature-tapped`,
`activated-loot`, and one more. They stay unaddressed. **No guessing.**

**No card-specific logic was used.** Narrowing was attempted only through
existing ratified structure — the object-lattice classifier per paragraph, the
axis's grammar slots, and paragraph/modal-header structure.

---

# 4. ACTIVE VOLCANO — required walkthrough

```
(0,0)  Choose one —
(0,1)  • Destroy target blue permanent.
(0,2)  • Return target Island to its owner's hand.
```

**Codebook state today — two assertions, and the bounce is not one of them:**

| axis | class | resolves to |
|---|---|---|
| `rule:modal` | human | **SPAN** (0,0)–(0,2) → Outcome **B** |
| `rule:targeted-destroy` | human | **(0,1)** — single owner, no narrowing needed |

**The bounce fact does not yet exist as an assertion.** It is object-lattice
output that has never been applied (the lattice DET pass has not run). When it
is applied it arrives with its own per-clause quote:

| lattice output | quote | resolves to |
|---|---|---|
| `rule:targeted-destroy-permanent` | `Destroy target blue permanent` | **(0,1)** |
| `rule:targeted-bounce-land` | `Return target Island to its owner's hand` | **(0,2)** |

**Why the two do not prove co-occurrence:** they hold different owners,
`(0,1)` and `(0,2)`. Both are bullets; their owning header is `(0,0)`, the
nearest preceding non-bullet paragraph, which prints `Choose one` — selection
cardinality **1**. Two distinct owners under a cardinality-1 header are
mutually exclusive. **Derived from structure, stored nowhere.**

**The honest part.** The brief asked how *existing axis semantics select the
correct bullet* for a broad quote. On this card they never have to: the destroy
assertion already carries a single-bullet quote, and the only span belongs to
`rule:modal`, where the whole span is the right owner. The demonstration
succeeds, but not by the mechanism the brief anticipated.

---

# 5. CANONICALIZATION COLLISIONS (§11)

**1 card.** `Rahilda, Wanted Cutthroat // Rahilda, Feral Outlaw` — the two faces
print differently-named self-references that both canonicalize to `~`.

- No assertion is affected today.
- **Raw text rescues it**: the raw paragraphs remain distinct, so the union
  resolver still returns one owner.
- The resolver stays deterministic because it takes a **union of coordinates**,
  not a union of texts — two paragraphs collapsing to the same *string* still
  hold different *coordinates*, so the union has 2 elements and the rule returns
  AMBIGUOUS rather than silently merging.

A guard for this belongs in implementation: assert that canonicalization never
changes a face's line count (the resolver already checks this and found 0 skew).

---

# 6. REPEATED-QUOTE COLLISIONS (§12)

**40 assertions** — 35 `rule-derived`, 5 `human`. The dominant shape is a short
rider appearing twice: `"can't be regenerated"` on Kirtar's Wrath, Viscerid
Drone, Suleiman's Legacy, Eye of Singularity.

Raw and canonical both find the same 2+ locations, so no representation
disambiguates. Axis semantics do not narrow them either — the rider is genuinely
printed twice. **They remain unaddressed.** Paragraph ordinal is *not* used as a
tiebreak.

---

# 7. COVERAGE — ownership and location reported separately (§15)

| | count | of quoted (7,891) | of all (7,930) |
|---|--:|--:|--:|
| one deterministic semantic owner | 7,808 | 98.95% | 98.46% |
| span reducing to one owner | 0 | 0% | 0% |
| genuinely whole-span owned (B) | 17 | 0.22% | 0.21% |
| **semantic ownership total** | **7,825** | **99.16%** | **98.68%** |
| ambiguous owner | 40 | 0.51% | — |
| unresolved owner (C + H) | 13 | 0.16% | — |
| semantically suspect (D) | 13 | 0.16% | — |
| quoteless | 39 | — | 0.49% |

**Evidence-location coverage: 7,847 / 7,891 = 99.44%** (single owner + all 39
spans). **Semantic-ownership coverage: 7,825 / 7,891 = 99.16%.** These are
different numbers and neither substitutes for the other.

---

# 8. NEGATIVE CONTROLS (§16)

| # | control | result |
|---|---|---|
| 1 | broad modal quote (header + both bullets) | **SPAN**, no single owner assigned — **PASS** |
| 2 | correct bullet per fact | destroy → `(0,1)`, bounce → `(0,2)` — distinct owners, co-occurrence disproved — **PASS** |
| 3 | raw/canonical disagreement | **0 live cases**; the union law returns AMBIGUOUS whenever they differ, by construction — **PASS** |
| 4 | canonicalization collision | 1 card; union is over *coordinates*, so collapse cannot silently merge — **PASS** |
| 5 | repeated short quote | `"can't be regenerated"` → AMBIGUOUS `[(0,0),(0,1)]`, stays unaddressed — **PASS** |
| 6 | unaddressed assertion behaviour | card-level fact retained; co-occurrence query cannot be satisfied without two owners — **PASS by rule** |

NC3 and NC6 are established by construction rather than by a live failing case;
that is stated rather than dressed up as a measured catch.

---

# 9. THE DETERMINISTIC RECONCILIATION LAW

> Resolve the quote against **every supported representation** of each unit
> (verbatim and CARDNAME-canonicalized). Collect the set of **unit coordinates**
> matched by any representation.
>
> - exactly one coordinate → **semantic owner**
> - more than one → **AMBIGUOUS**, unaddressed
> - none, but the quote matches the face's joined text → **SPAN**, evidence
>   located, owner unaddressed unless the fact is multi-unit by nature
> - none at all → **UNRESOLVED**
>
> Never first-match-wins. Neither representation may overrule the other.
> Provenance class must not influence resolution.

Answering §10's checklist directly: raw-only and canonical-only are each
accepted because the union has one element, not because a representation was
preferred; agreement is not *required*, only non-conflict; **neither
representation may disambiguate the other** (Cases D/E are 0, so the capability
is unnecessary and would be a tiebreak in disguise); conflicting resolutions
return AMBIGUOUS; canonicalization collisions cannot merge because the union is
over coordinates; repeated quotes return AMBIGUOUS; **source class is recorded
but must not affect resolution.**

---

# 10. EVIDENCE SPAN — DERIVE, DO NOT STORE (§13)

Recommend **Option A**. The span is a pure function of `quote + corpus
snapshot`, and the resolver already computes it. Storing it would duplicate
information that can go stale independently of the quote — the repository's
recorded *"a carried-forward count is not a measurement"* shape, applied to a
coordinate.

Store the **semantic owner** only, plus a status for the unaddressed cases so
the ratchet can count them.

---

# 11. PASS CRITERIA (§17)

| criterion | status |
|---|---|
| multi-paragraph population fully enumerated | ✅ 39, all classified A/B/C/D |
| evidence span and ownership measured separately | ✅ 99.44% vs 99.16% |
| Active Volcano resolves at owner level | ✅ destroy `(0,1)`, bounce `(0,2)` |
| reconciliation deterministic, never first-match-wins | ✅ union; F/D/E all 0 |
| conflicting representations halt/report | ✅ AMBIGUOUS by construction |
| canonicalization collisions cannot reattach | ✅ 1 card, union over coordinates |
| repeated quotes cannot pick arbitrarily | ✅ 40 stay unaddressed |
| unaddressed usable only at card level | ✅ by rule |
| no case requires child effects | ✅ all 39 spans are B/C/D |
| no new vocabulary | ✅ |
| parent law unchanged | ✅ S1–S7 untouched |

**All eleven pass.**

---

# 12. FINAL CAPTAIN RATIFICATION TEXT

> **SEMANTIC LOCALITY FOR FOUNDRY ASSERTIONS** — resolves FL-2.
>
> Existing axes, members and assertion stacks remain authoritative for direct
> card facts. Nothing currently stored changes meaning.
>
> An assertion may optionally carry deterministic **semantic locality**: the one
> structured card location that owns the fact the assertion proves, expressed
> against the existing card key and the face/paragraph structure already
> produced by the shared face reader.
>
> **No separate mode identifier is stored.** Measured 2026-08-13: every modal
> bullet occupies its own paragraph (1,791 paragraphs with exactly one bullet,
> zero with two or more), so the paragraph coordinate already separates modes.
>
> **Evidence location and semantic ownership are distinct.** A quote may cover
> more text than the fact owns. Evidence span is **derived** from the quote and
> the corpus snapshot, never stored.
>
> **Modal grouping and selection cardinality are derived** from the card's
> printed structure — the owning header is the nearest preceding non-bullet
> paragraph on the same face — and are never copied onto an assertion.
>
> **Representations are reconciled, not raced.** A quote resolves against every
> supported text representation; the owner is accepted only when the combined
> result identifies exactly one location. Conflict or multiplicity yields
> unaddressed. Provenance class must not influence resolution.
>
> **Unaddressed assertions remain fully valid card-level evidence** and may not
> establish that their fact co-occurs in the same semantic unit with another
> fact.
>
> **Atomic child-effect decomposition remains deferred.** Reconsider only when a
> consumer must distinguish two facts inside one paragraph.
>
> **Semantic locality does not certify semantic correctness**, and no existing
> correctness guard is relaxed by it. Where locality analysis finds a membership
> contradicting its axis definition, it is routed to the correctness path.
>
> **Addresses are snapshot-relative**, re-derived after corpus changes;
> unresolved changes are reported, never silently reattached.
>
> **Parent law S1–S7 is unchanged.** Parent derivation remains card-level.
>
> Field names, serialization and helper names follow repository precedent at
> implementation and are not fixed by this ruling.

---

# 13. IMPLEMENTATION ROADMAP (not implemented)

| # | step | likely surface |
|---|---|---|
| 1 | locality helper: unit enumeration + the union resolver, consuming `tier_engine.get_raw_faces` — **no parallel indexing** | new helper beside `foundry_common` |
| 2 | schema extension point: optional field on the assertion, `foundry-codebook/2` → `/3` only if the reader requires it | `experiments/foundry_codebook.py` |
| 3 | emit locality on **new** rule-derived output first | `foundry_object_lattice.py`, `foundry_det_pass.py` |
| 4 | backfill only where the resolver returns one owner; report the rest | one-shot migration under the backup law |
| 5 | ambiguity/unresolved reporting with exact denominators | new reporter |
| 6 | coverage ratchet (`WORSE_IF_DOWN` on owned counts) | `foundry_audit_baseline.py` |
| 7 | write-boundary behaviour: locality never blocks a write; only its own guards do | `foundry_det_pass.py` |
| 8 | Gate 2 row, one runner one exit code | `foundry_gate2.py` |
| 9 | the six negative controls as inline fixtures | the locality helper, `foundry_probe.py` precedent |
| 10 | documentation: this ruling, `PICK-UP-HERE.md`, FL-2 marked resolved | `docs/` |
| 11 | deterministic regeneration: ×2 identical | standing determinism gate |

**Not in scope:** AQ4's predicate row, AQ5's `level` field, child effects, global
stable IDs, roles, magnitude, scope, ranking, CI.

**First families to backfill** (100% clean at ≥20 assertions, 59 such axes):
`rule:cycling` 304 · `created-token-enters-tapped` 195 ·
`create-token-creature` 184 · `targeted-destroy` 172 ·
`enters-tapped-conditional` 168 · `direct-damage-any-target` 112.

---

# 14. SIDE FINDING, ROUTED NOT FIXED

**13 memberships on `rule:grants-trample-to-creatures-with-counters` contradict
its own definition.** The axis claims the card *grants* trample to
counter-bearing creatures; Avatar of the Resolute and Bioessence Hydra simply
*have* trample. Found by locality analysis, but it is a correctness defect and
belongs to `foundry_definition_drift` / a membership ruling — **not** to this
architecture, and not fixed here.
