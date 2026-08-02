# CR VOCABULARY AUDIT — can axis names be audited against the Comprehensive Rules?

Captain's question, 2026-08-01: *is there really no way to audit all current
ruling names against CR vocabulary to build less ambiguous names — and if there
isn't, should we create system-unique naming to differentiate instead?*

**Verdict: `CR-AUDIT-PARTIAL`.** Answered by a Fable 5 census; every headline
number independently re-verified against live state before filing.

---

## 0. The framing was a false either/or

The question presumes CR coverage is the bottleneck. It is not: **~20% of the
live vocabulary is deliberate project coinage the CR can never adjudicate**
(`grants`, `pump`, `tutor`, `bounce`, `loot`), most already Captain-ratified as
EFFECT verbs. So "CR audit **or** system-unique naming" was never the choice.
The answer is both, partitioned: CR audit for the 54% that is CR vocabulary,
the ratified-glossary discipline already in place for the coinages, and a small
homograph ledger where the two worlds collide.

---

## 1. Coverage census — 313 distinct tokens across 307 active axes

Method: parsed the CR (Glossary, 701/702 headings, zone/card-type/step section
headers, CR 111.10 predefined tokens, CR 122 counter kinds, CR 207.2c ability
words), classified all 313 tokens mechanically, hand-adjudicated the residue.

| Class | Tokens | Occurrences | Meaning |
|---|---|---|---|
| **a1 — exact CR term** | 123 (39%) | 674 (51%) | glossary entry / numbered rule / enumerated list |
| **a2 — CR-anchorable indirectly** | 45 (14%) | 111 (8%) | multi-word CR term (`upkeep`→503), morph of a keyword (`destruction`→701.8), CR-enumerated open class (`landfall`→207.2c) |
| **b — structural / generic** | 84 (27%) | 383 (29%) | glue (`to`, `with`), slot machinery (`etb`, `self`, `mass`), ordinary English the CR uses but never defines |
| **c — semantic coinage** | 61 (19%) | 154 (12%) | the ambiguity surface |

**Axis level:** 47 pure CR vocabulary · 129 CR + structural (fully
CR-auditable) · **131 contain at least one coinage.**

**VERIFIED THIS SESSION:** 313 distinct tokens ✓ · 131 coinage-bearing axes ✓ ·
139 `validate_slug` failures ✓.

**One correction to the source analysis.** It read the 131 and the 139 as
nearly the same finding. They are not: **only 63 axes appear in both sets.**
The magnitudes are coincidentally close; the populations differ. Coinage and
validator failure are two distinct problems that happen to be similarly sized.

### The 61 coinages

absence, accumulation, alt, animate, animates, anthem, auto, board, bounce,
buff, burst, cantrip, cheat, compensates, death, debuff, dig, direct, drain,
drop, fetch, forces, free, gives, grant, grants, grows, growth, imposes,
infinite, innate, lifegain, loot, matter, outlet, pump, purpose, reanimate,
recast, recursion, redirect, redirects, refill, regrowth, removal, reset,
rhystic, scroll, stats, stolen, symmetric, tax, taxes, theft, transfer, trick,
tribal, tutor, unblockable, uncounterable, visibility.

Heaviest: `grants` (22 axes), `pump` (13), `death` (10 — ratified D-1, though
the CR word is "dies"), `tutor` (7), `bounce`/`lifegain` (6 each).

Three anchor only to **obsolete** CR terms — `tribal` (current CR term is
Kindred), `unblockable`, `redirect(s)`. Three are abbreviations hiding real CR
terms: `alt` (CR 118.9 "alternative"), `auto`, `vs`.

---

## 2. What is mechanizable

**Decidable mechanically:**
- **Coinage detection** — set complement against the CR lexicon plus the
  ratified glossary. Fully mechanical after a one-time human calibration of the
  a2/b boundary (~50 tokens, done), because the CR does not mark its own
  defined-term boundary outside the Glossary.
- **CR-internal homograph detection** — glossary entries with numbered
  multi-senses (25 single-word terms; live in slugs: **counter, exile, draw,
  play, library, hand, graveyard, color, copy, ability, loyalty, type**) plus
  cross-section anchors (zone vs 701 action; step vs action for `untap`).
- **Obsolete-term drift** — re-parse on each CR update; `tribal`,
  `unblockable`, `redirect` fell out automatically.

**Needs human judgment:** which CR sense a non-conforming slug intends; the
a2/b calibration; whether a coinage should be replaced by CR phrasing at all
(`bounce` is better than `return-to-hand` under this project's full-word
legibility standard).

**Undecidable in principle:** "is this name unambiguous to a reader" — a
semantic property with no mechanical test. And **CR-vs-slang homographs**,
because slang is not in the CR: `removal` (counter-removal here, kill-spells in
slang), `tax` (cost-increase vs Commander tax), `tribal`. No CR audit can see
these; only a curated list can.

**The enforceable proxy:** *every token is CR-defined with a unique sense, or
ratified-glossary, and every homograph token appears only in a ledger-ruled
form.* That is checkable in the validator today.

### Live homograph inventory

`counter`/`counters` 33 axes (§8 rules exist, ~15 non-conforming — CDR-09) ·
**`exile`/`exiled` 12 axes** · `draw` 14 (all card-sense; game-draw sense never
appears) · `untap` 8 / `tap` 4 (all action-sense) · `play` 1 (exempt leaf) ·
`level` 1 · `loyalty` 0.

**VERIFIED: `exile` needs zero renames.** The corpus already obeys a clean
unratified rule — the only two preposition-bound axes
(`cast-from-exile-trigger`, `graveyard-to-exile-replacement`) are exactly the
two zone-sense ones; every unbound axis is action-sense; and
`leaves-battlefield-returns-exiled-card` uses the participle, which the ledger
rules as zone-resident. The rule needs ratifying, not applying.

---

## 3. Recommendation — the Homograph Form Ledger

Rejected alternatives, with reasons: **mandatory sense-prefix** (`act-exile` /
`zone-exile`) — worst churn, breaks the ratified full-word legibility standard,
reads as code. **Domain namespaces** (`zone:`, `kw:`) — restructures every slug
and makes the canonicalizer *harder*, since the namespace must be inferred
before parsing. **Opaque unique id alongside the name** — zero churn but solves
nothing; the slug already is the unique key, and a second key invites drift.

**Recommended: a Homograph Form Ledger — sense-form rules on homograph tokens
only.** This is §8 generalized. §8 already solved `counter` exactly this way
(noun → typed; verb → `counters-<object>`); the ledger extends the same move to
a small closed set:

| Token | Verb/action form | Other-sense form | Renames |
|---|---|---|---|
| counter | `counters-<object>` | typed `<name>-counter` | ~15 (already ruled, CDR-09) |
| exile | bare `exile` | preposition-bound `from-/to-/in-exile`; participle `exiled` = zone-resident | **0** |
| draw | bare `draw` (card sense) | game-draw sense banned in slugs | 0 |
| tap / untap | bare (action only) | step sense banned (`untap-step` if ever needed) | 0 |
| play | banned outside exempt leaves | — | 0 |
| loyalty | delivery position = ability | `loyalty-counter` = counter | 0 |

**Cost, plainly: ~15 renames total — all already mandated by CDR-09. The ledger
adds ZERO new churn.** Plus one new grammar section, ~40 lines in
`validate_slug.py` to enforce forms in all positions (closing the
final-token-only gap), and one ledger hook in the canonicalizer.

It survives CR terminology changes: a new CR homograph is a new ledger row, and
nothing renames. It stays fully human-legible.

**For the 61 coinages**, the differentiation guarantee is the existing
discipline plus one new mechanical check: *a coinage must not collide with any
current-or-obsolete CR term in a different sense.* That flags exactly 5 tokens
across 11 axes — `tribal`, `unblockable`, `redirect(s)`, `removal`, `alt` — for
walk-time rename rulings.

---

## 4. The canonicalizer

Position-aware bucketing is **feasible and worth building, but only
ledger-deep.** A general slot parse of the ratified order is ambiguous in
principle — all slots are optional and vocabularies overlap (`creature` is both
OBJECT and SCALING_STAT; `damage` is both DELIVERY and EFFECT) — so greedy
parsing would misfile.

What is deterministic is local adjacency keyed on the ledger: `counters` is
EFFECT iff followed by an OBJECT token, QUALIFIER iff preceded by a type-name
or a `with`-binding; `exile` is zone iff preposition-bound. That is ~20 lines
replacing flat first-match-wins, **for ledger tokens only**.

This is decidable *because* the ledger's form rules hold — which is why the
naming fix and the canonicalizer fix are one ruling, not two. The canonicalizer
fix cannot work without the naming fix on the ~15 non-conforming counter axes.

---

## 5. Verdict

**`CR-AUDIT-PARTIAL`.** Mechanically auditable for the 168 CR-anchorable tokens
(54% of vocabulary, 129 axes fully). Homographs are mechanically *detectable
but not resolvable* — resolution needs the ledger ratified. Blind in principle
to the 61 coinages and to CR-vs-slang collisions, which the ratified-glossary
plus collision-check discipline covers instead.

**Total new churn beyond already-ruled renames: zero.**

The census script is re-runnable against any future CR drop, which makes this a
standing check rather than a one-off — the same property that makes sweep pass
E durable.
