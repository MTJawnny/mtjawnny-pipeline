# FACT GRANULARITY CENSUS — independent verification

**2026-08-13.** Read-only. No locality, no qualifier fields, no codebook
mutation, no axes, no DET apply, no API calls, no vocabulary. The published
census is **not edited**; corrections are recorded here. Gate 2 green
(14 gates, 13 pass, 1 known-excused).

Verifies `docs/FACT-GRANULARITY-CORPUS-CENSUS-2026-08-13.md`.

---

# A. VERDICT — **VERIFIED WITH CORRECTIONS**

The architecture conclusion survives. **Three of the five headline numbers are
wrong, and all three are wrong in the same direction — the census
UNDER-stated how qualified the corpus is.**

- The denominator was inflated **11.8%** by a preprocessing-variant double count.
- The qualifier rate was under-counted because the detector had **no keyword-restriction category at all**.
- The combinatorial explosion was under-counted by a third.

Corpus denominators and the era trend **reproduce exactly**.

---

# B. EXECUTIVE SUMMARY

The census said 41.5% of object-lattice clauses carry a qualifier. A second,
differently-constructed measurement says **48.0%**, on a denominator of
**2,106** rather than 2,389. Both of the census's own self-corrected probe
defects were genuinely fixed — but a **third** defect survived, and a fourth
(the double count) was never detected.

Every correction makes the case for compositional qualifiers **stronger**, not
weaker. **Nothing found changes the locality-first sequence.**

---

# C. INDEPENDENCE METHOD

**Reused** (unavoidable, and stated as required): the same gated corpus, the
same `tier_engine.get_raw_faces` reader, and the same object-lattice
classifier. There is no second implementation of the lattice, so
*"which clauses are classified"* **cannot be independently verified** — only
what is measured about them.

**Independent:** the qualifier detector. The census asked *"does category regex
X match the eligibility expression?"* This verification instead **strips the
template scaffolding and the base-class words and asks what content tokens
remain** — a residual-token diff. A remaining token is a restriction by
construction, so the method is structurally immune to the census's
base-class-confusion and category-overlap failure modes, and it surfaces
restrictions no category was written for.

Clause enumeration was additionally **deduplicated by (card, stem, clause
text)**, which the census did not do.

---

# D. DENOMINATOR VERIFICATION — **REPRODUCED**

| metric | census | independent | status |
|---|--:|--:|---|
| gated cards | 32,557 | **32,557** | REPRODUCED |
| cards with oracle text | 32,217 | **32,217** | REPRODUCED |
| cards without oracle text | 340 | **340** | REPRODUCED |
| total faces | — | 33,393 | new |
| non-empty paragraphs | — | 61,948 | new |

## D1. THE DOUBLE COUNT — a defect the census never detected

`clauses_for` iterates **every variant** returned by `det_scan_texts`, which is
`[canonical full text, *modal-bullet expansions]`. A clause inside a modal
bullet is therefore yielded **twice** — once from the full text, once from its
own expansion.

```
clauses_for total yields      : 3,213
distinct clause strings       : 2,843
duplicate yields              :   370
```

Within the census's classified population this inflated the denominator:

> **2,389 → 2,106 after dedupe. The census over-counted by 283 clauses (11.8%).**

This is the recorded *"a probe must consume the same preprocessing as the
classifier"* trap in its other direction: the census consumed a preprocessing
pipeline designed for **matching** (where duplicates are harmless, because
`classes_for_card` unions) and used it for **counting** (where they are not).

---

# E. OBJECT-LATTICE QUALIFIER RATE — **REFUTED as exact, DIRECTIONALLY CONFIRMED**

| | census | independent |
|---|--:|--:|
| classified clauses | 2,389 | **2,106** |
| carrying ≥1 qualifier | 992 | **1,010** |
| rate | **41.5%** | **48.0%** |

Denominator definition: one row per **distinct (card, action stem, clause
text)** whose `classify_clause` returns ≥1 object class. Base-class words are
removed before qualifier detection, so `nonland` on `nonland-permanent` cannot
count. Non-eligibility residue (duration, riders) is excluded: only **13**
clauses had exclusively such residue, so the upper bound (any residual token,
48.6%) and the eligibility-only figure (48.0%) nearly coincide.

**Corrected value: 48.0% of 2,106.**

## E1. A THIRD PROBE DEFECT — 110 false negatives

The census self-corrected two defects (base-class double-count, overlapping
`relative` class). Both are **confirmed genuinely fixed**. A third survived:

| missed token | count | why |
|---|--:|---|
| `flying` | 36 | **no keyword-restriction category existed** |
| `was` | 12 | participle state — *"that was dealt damage this turn"* |
| `controls` | 11 | controller templates outside the census's alternation |
| `name` / `same` | 9 / 9 | name-matching restrictions |
| `defending` / `defender` | 9 / 5 | combat role and the Defender keyword |
| `colors` | 5 | *"shares a color"* |
| `suspended`, `crewed` | — | states no regex named |

`destroy target creature with flying` (Oran-Rief Recluse, Stingerfling Spider,
Pistus Strike) was scored **unrestricted**. This is the recorded
**INFLECTION / VOICE sweep-class** trap: the state detector matched `tapped`
and `attacking` but not `was dealt`.

**False positives: 3**, and all three are defensible — *"with a counter on it"*
is a genuine state restriction and *"creature token"* a genuine one. Effective
FP rate ≈ 0; the detector was **under**-inclusive, never over-inclusive.

---

# F. CREATURE-REMOVAL RATES — **DIRECTIONALLY CONFIRMED, both understated**

| broad fact | census | independent | Δ |
|---|--:|--:|--:|
| `targeted-destroy-creature` | 56.1% | **68.0%** | +11.9 |
| `targeted-exile-creature` | 63.1% | **68.3%** | +5.2 |
| `targeted-destroy-artifact` | 17.1% | **24.3%** | +7.2 |
| `targeted-destroy-enchantment` | 15.3% | **23.1%** | +7.8 |
| `targeted-bounce-creature` | 39.4% | **40.3%** | +0.9 |
| `targeted-destroy-land` | 31.7% | **33.1%** | +1.4 |

**The published contrast holds and widens.** Creature removal (68%) is roughly
**three times** as qualified as artifact/enchantment removal (23–24%). The
census's qualitative claim — that false-equivalence pressure concentrates in
creature removal — is confirmed on an independent detector.

---

# G. CORPUS-WIDE PREVALENCE — **REPRODUCED, but the headline needs its definition attached**

| view | cards | % |
|---|--:|--:|
| original-definition reproduction | 29,087 / 32,217 | **90.3%** (census 90.4%) |
| **narrow mechanical-eligibility** | 21,761 / 32,217 | **67.5%** |

The 0.1-point gap is regex-wording drift, not a defect: **REPRODUCED**.

**But the 90.4% headline is definition-sensitive and should never be quoted
bare.** It counts any `if` / `may` / `until end of turn`, which are conditions
and durations rather than eligibility restrictions. Restricted to things that
narrow *what qualifies, when, where, how many, whose, or in what state*, the
figure is **67.5%**. Both support the architecture; only the second supports a
claim about *eligibility*.

---

# H. COMPOUND-AXIS EXPLOSION — **DIRECTIONALLY CONFIRMED, understated**

| | census | independent |
|---|--:|--:|
| base class axes | 23 | **23** |
| distinct class × qualifier-combination | 166 | **211** |
| multiplier | ×7.2 | **×9.2** |

Combinations are order-normalised (`frozenset`), so ordering cannot duplicate a
shape, and a clause mapping to several class axes contributes one pair per axis
— the same rule the census used, verified rather than assumed. The higher count
follows directly from E1: more detected categories, more observed combinations.

**The conclusion strengthens.** ×9.2 in one family on a handful of categories.

---

# I. ERA TREND — **REPRODUCED**

| cohort | cards | mean | median |
|---|--:|--:|--:|
| 1993–2003 | 3,780 | **0.85** | 1.0 |
| 2004–2013 | 5,111 | **0.95** | 1.0 |
| 2014–2020 | 7,547 | **1.02** | 1.0 |
| 2021+ | 15,779 | **1.39** | 1.0 |

Exact reproduction, monotonic. Cohort boundaries and the `released_at` field
match the census.

**Two caveats the census did not state.** (1) The **median is flat at 1.0 in
every cohort** — the trend lives in the tail, so modern sets contain more
heavily-qualified cards rather than uniformly more-qualified cards. (2) The
corpus is keyed by `oracle_id`, one row per card, so reprints cannot inflate a
cohort; but `released_at` on an oracle-level record is a **printing** date, so
an old card reprinted into a modern set may sit in a later cohort. The
direction is robust; the exact means are **directional, not exact law**.

---

# J. SAME-PARAGRAPH LOCALITY — **CONFIRMED with a bounded exception**

Every qualifier measured in §E is printed inside the clause it restricts, hence
inside one paragraph — true by construction of the residual method.

Independently searching for the counter-case: **127 cards (0.4%)** carry a
paragraph that is *only* a restriction, therefore governing something else —
`Cast this spell only if you control two or more Doctors`,
`You may cast this card from your graveyard as long as…`.

**This does not amend the owner design.** Such a paragraph is itself a valid
owner; what is missing is the **link** to what it restricts — a relationship,
already deferred with child effects. The earlier-recorded Nicol Bolas case
(`Activate only as a sorcery` binding to no ability) is the same shape.

**Upper bound on the exception: 127 cards.** Reported, not fixed.

---

# K. TRUST TABLE

| claim | original | independent | status | architecture impact |
|---|--:|--:|---|---|
| gated corpus | 32,557 | 32,557 | **REPRODUCED** | none |
| oracle-text cards | 32,217 | 32,217 | **REPRODUCED** | none |
| lattice clause denominator | 2,389 | **2,106** | **REFUTED** | none |
| lattice qualifier rate | 41.5% | **48.0%** | **REFUTED / directionally confirmed** | strengthens |
| destroy-creature restricted | 56.1% | **68.0%** | **DIRECTIONALLY CONFIRMED** | strengthens |
| exile-creature restricted | 63.1% | **68.3%** | **DIRECTIONALLY CONFIRMED** | strengthens |
| artifact/enchantment contrast | much lower | **confirmed, 23–24%** | **REPRODUCED** | none |
| corpus prevalence | 90.4% | 90.3% / **67.5% narrow** | **REPRODUCED, needs definition** | none |
| combination expansion | 166 / ×7.2 | **211 / ×9.2** | **DIRECTIONALLY CONFIRMED** | strengthens |
| era trend | 0.85→1.39 | **identical** | **REPRODUCED** | none |
| same-paragraph locality | "every qualifier" | confirmed; **127-card exception** | **VERIFIED WITH CAVEAT** | none |
| deterministic extractability | all 12 shapes | see §L | **PARTIALLY VERIFIED** | none |

---

# L. DETERMINISTIC EXTRACTABILITY — **PARTIALLY VERIFIED**

The census claimed all twelve calibration shapes are deterministic without a
model. Verified as **true for the shapes as written**, with two qualifications
the census did not state:

- **Robust:** controller, colour, tapped/untapped, mana value, power/toughness, token/nontoken, legendary, nonland/noncreature, zone-origin. Explicit adjectives or printed CR terms; low false-positive risk.
- **Needs CR lookup, still deterministic:** subtype restrictions (CR 205.3g–q, already consumed by the lattice) and keyword restrictions (CR 702 — the category the census's own detector lacked).
- **Requires structural linking, NOT a simple regex:** *"that was dealt damage this turn"*, *"that attacked this turn"*, *"shares a color with"* — these reference prior events or another object. Deterministic in principle, but not from a single pattern.

**Corrected claim:** every measured dimension is deterministic; **not all are
extractable by pattern alone**, and "regex found examples" was not sufficient
evidence for the strongest reading.

---

# M. ACTIVE VOLCANO + CALIBRATION — verified

Independently confirmed: destroy fact is broad class `permanent`; eligibility
further restricted by **blue**; bounce targets an **Island**; the two modes are
separate paragraphs `(0,1)` and `(0,2)`; the broad axis does **not** encode
blue; and the qualifier sits in the same paragraph as its action.

Five further cards, same shape, different qualifier types — all found by the
independent detector, none by the census's:

| card | broad fact | missing qualifier | type |
|---|---|---|---|
| Oran-Rief Recluse | destroy-creature | `with flying` | keyword |
| Clear a Path | destroy-creature | `with defender` | keyword |
| Ogre Siegebreaker | destroy-creature | `that was dealt damage this turn` | past state |
| Getaway Car | bounce-creature | `that crewed it this turn` | event state |
| Obelisk of Undoing | bounce-permanent | `you both own and control` | dual ownership |

---

# N. THE TWELVE QUESTIONS

1. **Yes**, with corrections — the scan is sound, the counting was not.
2. Corpus denominators and the era trend reproduce **exactly**.
3. Clause denominator (−283), qualifier rate (+6.5pts), explosion (+45 combos), creature rates (+5 to +12pts).
4. **Yes** — both self-corrected defects are genuinely gone.
5. **Yes, two more**: the preprocessing-variant double count, and the missing keyword-restriction category (110 false negatives).
6. **No** — 41.5% is refuted. Use **48.0% of 2,106**.
7. Directionally yes, numerically no — **68.0% / 68.3%**.
8. Reproduces at 90.3%, but **only under its own broad definition**; the eligibility-strict figure is **67.5%**.
9. **Yes, more strongly** — ×9.2.
10. **Yes** — monotonic; but the median is flat, so it is a tail effect.
11. **Yes** — the exception is bounded at 127 cards (0.4%) and is a missing *link*, not a wrong owner.
12. **No.**

---

# O. WHAT CAN BE RATIFIED EXACTLY

- gated corpus **32,557**; oracle-text cards **32,217**; no-text **340**
- faces **33,393**; non-empty paragraphs **61,948**
- deduped lattice clause population **2,106**
- lattice base class axes **23**
- era cohort sizes 3,780 / 5,111 / 7,547 / 15,779

# P. DIRECTIONAL ONLY — architecture-safe, not exact law

- lattice qualifier rate **≈48%** (detector-definition sensitive)
- creature-removal restriction **≈68%**; artifact/enchantment **≈23–24%**
- combination expansion **≈×9** (grows with detector coverage)
- era means 0.85→1.39 (printing-date caveat)
- corpus prevalence **90.3% broad / 67.5% narrow** — never quote without the definition

# Q. EXPLORATORY — not ratifiable yet

- the 127-card cross-paragraph restriction population (upper bound, uncharacterised)
- per-category prevalence within the lattice (moves with every detector improvement)

---

# R. CORRECTIONS REQUIRED

The census is **not edited** (the brief forbids it). For any future citation:

1. lattice denominator **2,389 → 2,106**
2. qualifier rate **41.5% → 48.0%**
3. expansion **166 / ×7.2 → 211 / ×9.2**
4. destroy-creature **56.1% → 68.0%**; exile-creature **63.1% → 68.3%**
5. attach the definition whenever 90.4% is quoted, and prefer **67.5%** for eligibility claims
6. soften "all deterministically extractable" to "deterministic, but three shapes need structural linking rather than a single pattern"

---

# S. ARCHITECTURE IMPACT — **NONE. Locality-first stands.**

Asked as the brief requires — *could any plausible correction make
paragraph-level locality the wrong first foundation?*

**No, and the reason is structural rather than numerical.** Locality would be
wrong only if qualifiers commonly attached somewhere a paragraph owner cannot
reach. Every correction found here moves the qualifier **rate** while leaving
the qualifier **position** unchanged: the restrictions the census missed
(`with flying`, `that was dealt damage this turn`) are printed *inside the very
clause they restrict*, which is the most local case possible.

Every correction increases the qualifier population, which strengthens the case
for compositional facts attached to a safe owner. **The measurement moved; the
architecture did not.**

# T. RECOMMENDED NEXT STEP

Proceed with semantic-locality implementation exactly as ratified. Carry §R's
corrected numbers into the later qualifier-vocabulary packet, and add a
**keyword-restriction category (CR 702)** to its scope — the census's detector
lacked it, and it is the single largest missed dimension.

# U. GATE 2

14 gates run, 13 pass, 1 known-excused (`family_sweep`), 0 unexpected. No CI
change; Gate 2 still runs in no CI.

# V. FILES CHANGED

This report only. The published census is unmodified. Verification code was
run from the session scratchpad and is not added to the repository.

# W. GIT STATE

```
 M docs/PICK-UP-HERE.md
 M docs/RATIFIED-RULINGS-REGISTRY.md
 M docs/det-patterns-v2.json
 M experiments/foundry_audit_baseline.py
 M experiments/foundry_det_pass.py
 M experiments/foundry_gate2.py
 M experiments/foundry_object_lattice.py
?? docs/CANONICAL-SEMANTIC-UNIT-DECISION-PACKET-2026-08-13.md
?? docs/FACT-GRANULARITY-CENSUS-INDEPENDENT-VERIFICATION-2026-08-13.md
?? docs/FACT-GRANULARITY-CORPUS-CENSUS-2026-08-13.md
?? docs/FULL-CARD-INFORMATION-CONSERVATION-2026-08-13.md
?? docs/OBJECT-LATTICE-RESIDUAL-RULING-2026-08-13.md
?? docs/SEMANTIC-ADDRESS-ARCHITECTURE-REVIEW-2026-08-13.md
?? docs/SEMANTIC-ADDRESS-PREIMPLEMENTATION-CHECK-2026-08-13.md
?? docs/THESAURUS-FACT-LAYER-ARCHITECTURE-2026-08-13.md
```

No commit.
