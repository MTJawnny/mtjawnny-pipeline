# EXTRACTOR REPAIR — passes 1–2 of the pre-step-2 order (2026-08-04)

Working the order set by `PRE-STEP-2-AUDIT-2026-08-04.md` §4. Captain,
2026-08-04: *"do the recommended order. how do we work without breaking other
things?"* — the answer is §1 below, built before any code changed.

**Done: passes 1, 1b, 2. 1,104 lines corrected, 0 unexplained regressions.**
Remaining: D4, D3, D5/D6/D8, then step 2. Zero API calls. No codebook mutation.

---

## 0. FIRST — nearly none of these were unique errors

Captain asked whether the docs already answered these. They largely did, and
finding that out **changed the plan**:

| defect | what the docs already held |
|---|---|
| **D3 modal bullets** | `det-patterns-v1.json`: *"KNOWN GAP, flagged not silently dropped … modal-bullet handling needs per-mode text splitting, out of scope for this sweep"* — then **solved** by `expand_modal_bullets`, ratified 2026-07-31 |
| **D2 loyalty** | `DEFINITION-DRIFT-AUDIT-2026-08-02` §: *"planeswalker loyalty abilities … have all been absorbed onto ETB axes … ETB is functioning as a default home when delivery is unclear."* The consequence was measured from the codebook side; the extractor-side cause was not |
| **D4 keyword params** | `DELIVERY-VOCABULARY-BATCH-2026-08-03` §6 already ranks **Ward 206 · Cumulative Upkeep 80 · Echo 50** and says *"Ward is already served, because §2 ratified `becomes-targeted-trigger` for exactly that family"* |
| **D9 casting costs** | same doc: *"51 UNSTATED … Flashback, Escape, Bestow, Mutate, Evoke, Dash, Blitz, Plot … reported by name, never assigned"*, and `KEYWORD-LEDGER-CANDIDATES.md` carries the SUP-protocol rule *"bare keywords / reminder text / procedural riders are never axes"* → **Phase B keyword ledger** |
| D1 · D8 | nothing — these are the extractor's own inventions |

**And there is ONE root cause under D1, D3 and D7.**
`foundry_common.det_scan_texts()` **is** the ratified *DET preprocessing
standard v1* (2026-07-31) — cardname canonicalization, modal-bullet splitting,
polarity, templating-era, all-faces. **Six tools call it.
`foundry_shape_extractor.py` does not.** It built a parallel pipeline, and every
transform defect lives in the parallel one.

**Consequence for the plan: D9 needs no Captain ruling.** Its disposition is
already governed — bare keywords are never axes; they belong to the Phase B
keyword ledger. That was the only blocked item on the list.

**A ratified standard with no caller is invisible to every gate.** Nothing
checks that one is wired in. It cost 504 lines here, and there is no reason to
assume this is the only instance.

---

## 1. HOW WE WORK WITHOUT BREAKING THINGS — `experiments/foundry_routing_regression.py`

Encoded, not remembered, so a session changing a classifier cannot skip it.

**The key idea is that moves are ASYMMETRIC:**

| direction | meaning |
|---|---|
| `None → ratified` | a gap closing — the intended direction |
| `ratified → ratified'` | a RE-ROUTE — **always read**, may be a fix or a regression |
| `ratified → None` | **a regression until proven otherwise** — and the one direction nothing else in the toolchain reports |

`diff --strict` **halts** on the third. It halted once (pass 1b), I read both
lines, and accepted them. That is the harness working, not a formality.

Four guards: **(1)** line-by-line diff of all ability lines, every moved line
enumerated; **(2)** ratified-family count pins, so a pass that claims one family
and moves another is caught; **(3)** **name-invariance** — a card's delivery
cannot depend on its NAME, corpus-wide, no ground truth needed; **(4)**
determinism ×2.

---

## 2. PASS 1 — `ABILITY_WORD` restricted to the em-dash (D1)

CR 207.2c ability words print with an **em-dash**. The pattern also allowed a
plain hyphen, and a hyphen is a word character in Magic templating.

**186 lines moved · 184 gaps closed · 2 re-routes · 0 regressions.**

| | |
|---|--:|
| `etb` | +32 |
| `replacement` | +34 |
| `static` | +62 |
| `attack-trigger` · `death-trigger` · `combat-damage-to-player` · 12 more | +58 |

Both re-routes read in full. **A-Thousand-Faced Shadow** `replacement → etb` —
correct; its trigger clause was decapitated, and "the token enters tapped" is
effect text describing a *created* token (§2's created-ability rule).
**Benalish Knight-Counselor** `replacement → cast-trigger` — still wrong, and it
exposed the next defect.

## 2b. PASS 1b — a trigger clause may not cross into a created ability

Benalish Knight-Counselor: *"Whenever ~ **enlists** a creature, you get a
one-time boon with **"When you cast a creature spell…"**"* — read as a
cast-trigger off the **boon's** text.

`enlist` and `unlock` are CR **702** keywords, not CR **701** keyword-ACTIONS,
so the verb set derived on 2026-08-04 cannot contain them — and hand-adding them
is exactly what that derivation stopped doing. **So the fix is structural, not
lexical:** §2's ratified created-ability rule already says a card does not
deliver an ability it CREATES, so `trigger_clause` now stops at the first quoted
span. **No verb list involved.** Tenth instance of the CR 113.3c class.

**2 lines moved, both `ratified → None` — and the harness halted on them.**
Read and accepted: both gave up a **wrong** ratified token and became
`unclassified-trigger`, which the gap census **does** report. Trading a wrong
ratified answer for a visible gap is the audit's own principle applied.

## 3. PASS 2 — loyalty hoisted out of the cost gate (D2)

> **CR 606.2** — *"An activated ability with a **loyalty symbol in its cost** is
> a loyalty ability. Normally, only planeswalkers have loyalty abilities."*

The loyalty test was nested *inside* a gate requiring a mana symbol or one of six
verbs left of the colon. A loyalty cost is `+1`. **The branch was unreachable for
exactly the cards it exists for.**

**916 lines moved · 900 gaps closed · 16 re-routes · 0 regressions.**
`loyalty` **7 → 909**.

All 16 re-routes read in full, all correct:

- **7 `loyalty → activated`** — every one a CR 702.184 **Station tier bar**
  (`20+ | {T}: …`, `12+ | …`). These were the 7 lines that reached `loyalty`
  before, and **none of them was a loyalty ability**: `head.strip()[:3]` saw
  `20+` and `^[+\-−]?\d` matched the `2`. The new anchor makes the sign
  mandatory except a bare `0`, which excludes them by construction.
- **9 `replacement → loyalty`** — planeswalkers whose **effect** said
  "would…instead" or "skips": Chandra ×3, Jace Vryn's Prodigy, Serra, Jaya,
  Dovin, Arlinn, Ral Zarek. The delivery is the loyalty ability; the replacement
  sits in the effect half or in a created emblem (§2, §2d).

Corpus-wide the anchor matches **909 lines, 100% on planeswalkers**.

---

## 4. STATE AFTER THREE PASSES

| | before | after |
|---|--:|--:|
| routed ability lines | 61,858 | 61,868 *(+10: lines that regained a second delivery)* |
| lines with **no** ratified token | 21,366 | **20,290** |
| `loyalty` | 7 | **909** |
| `etb` | 4,849 | 4,881 |
| `static` | 11,717 | 11,779 |
| `replacement` | 2,121 | 2,146 |
| **NAME-DEPENDENT deliveries** | **63** | **1** |

The remaining 1 is a **harness artifact, not a defect**: *Storm of Memories* is
a card whose only ability line is the word "Storm", so renaming the card
rewrites the keyword itself.

**Determinism ×2 byte-identical. Gate 2 unchanged** — lint clean · 565 axes /
359 active / 8,740 members · family sweep the same 6 blocking · drift 35, same
partition. **Clue ground truth unmoved at 98/140** — no `investigate` line
appears in any of the three diffs.

Gap census moved only where expected: `unclassified-trigger` 1,006 → 1,018
(+12 — the honest gaps these passes surfaced, including the two from 1b).

---

## 5. REMAINING, IN ORDER

| # | work | lines | note |
|---|---|--:|---|
| 3 | **D4 parameterized keyword lines** | 194 non-static + 1,757 static | **derive the printed form from the CR** — 146 of 193 keywords state it verbatim before "means" (`"Equip [cost]"`, `"Champion an [object]"`, `"Affinity for [text]"`, `"Modular N"`). Do NOT pattern-guess: *"Equip abilities you activate cost {1} less"* is a static cost-reducer, not an equip line |
| 4 | **D3 modal modes** | 504 | wire `expand_modal_bullets` in — the standard is ratified and written |
| 5 | D5 window · D6 colon head · D8 semicolons | 160 + 30 + 29 | |
| 6 | **step 2 proper** | ≈5,647 | against the corrected partition, not the original 7,976 |
| 7 | D9 | ≈1,229 | **no ruling needed** — Phase B keyword ledger, per §0 |

**Re-run `invariance` after every pass.** It went 63 → 1 across these three and
cost nothing.
