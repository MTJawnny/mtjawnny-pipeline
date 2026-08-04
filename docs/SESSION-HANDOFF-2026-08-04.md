# SESSION HANDOFF — 2026-08-04

Supersedes `SESSION-HANDOFF-2026-08-03-EVE.md`. **Zero API calls all session.
Cumulative arc spend unchanged at $90.51 / $140.** Captain's $37 still unspent.

**The session in one line: `discard-trigger` ratified, all eight remaining gap
shapes ruled CR-first, and the parent layer opened — but the day's real result is
a corpus-wide DET defect that had corrupted every trigger family's numbers.**

## 0. START HERE

`docs/SESSION-START-PROCEDURE.md` — five gates. **Gate 3 caught me once this
session and I still under-ran it** (§6 below). Read that first.

---

## 1. Live state — measured at handoff, not recalled

| | |
|---|---|
| codebook | **565 axes · 359 active · 8,740 members** — **UNCHANGED, no mutation this session** |
| sha256 | `5fa27b70fabdce8d40e537907358522449d4ce642d80f6680314c1b2d2e7d93e` |
| lint | clean |
| family sweep | 6 blocking (unchanged) |
| definition drift | 35 findings — C1b 1 · C2 16 · C3 7 · C4a 3 · C4e 5 · C4f 3 (unchanged) |
| ruling registry | 82 docs scanned (was 72) · 126 ruling ids |
| §2 DELIVERY vocabulary | **31 tokens** (was 30) |
| `phase-trigger-unnamed` | **0** (was 11) |
| commits | **0 — nothing committed; awaiting Captain's ask** |

**No codebook mutation, so no backup was required.** All work is grammar, DET and
documents.

## 2. RATIFIED — `discard-trigger`, §2 30 → 31 tokens

`docs/DISCARD-TRIGGER-RULING-2026-08-03.md` carries the ratification banner and
its **superseded numbers**: ruled as 96 lines / 88 cards, ratified at **90 / 82**
(`any-` 76 · source 3 · `other-` 0), because six lines printed "discard" only in
their **effect** half. The §2 row cites three CR rules the original ruling missed
— **702.35a** (madness still discards), **702.29f** (typecycling), **701.9c**.

## 3. THE REAL RESULT — `docs/TRIGGER-VERB-DERIVATION-2026-08-04.md`

`trigger_clause` decides where a trigger CONDITION ends (CR 113.3c). Its verb list
was hand-curated and carried this comment:

> *"a verb missing here only makes the clause end earlier, which is the
> conservative direction."*

**That is backwards.** The loop returns the first comma-prefix carrying a *listed*
verb — so a missing verb makes the clause end **LATER**, running into the effect.
**488 of 13,028 trigger lines** had no listed verb before their first comma.

The verb set is now **derived from the CR's own keyword-action list**, same
principle that parses §2 at run time. Two verbs the CR list does not supply
(`cycle`, filed as a KEYWORD not a keyword-action; and the participles
`tapped`/`untapped`) were dropped by the first derivation and **caught by
regression, not review** — both are now in the halt-guard.

Ninth instance of the CR 113.3c bug class, and the first whose root cause was the
mechanism the previous eight fixes relied on.

## 4. EIGHT SHAPES RULED — all CR-first, all RULED-NOT-RATIFIED

| doc | shapes | note |
|---|---|---|
| `MAIN-PHASE-RULING-2026-08-04.md` | 3 tokens | **CR 505.1a**: "second" ≠ "postcombat" |
| `IS-DEALT-DAMAGE-RULING-2026-08-04.md` | 4 tokens | CR 120.1 closed recipient enum; **120.10** excess |
| `TURNED-FACE-UP-RULING-2026-08-04.md` | 1 token | + **236 invisible replacement effects** |
| `GAIN-LIFE-TRIGGER-RULING-2026-08-04.md` | 1 token | **CR 119.9** vs 701.9b — opposite verdicts |
| `TO-GRAVEYARD-RULING-2026-08-04.md` | 4 tokens | CR 700.4 `dies` is narrow |
| `COUNTER-PLACED-RULING-2026-08-04.md` | §11 grammar family | CR 122.6 |
| `DRAW-STEP-RULING-2026-08-04.md` | 1 token | turn structure now complete |

**Ratifying all of these is ~14 grammar §2 rows.** The DET already separates every
shape and reports each honestly; nothing is approximated onto a neighbour.

### 4a. The finding I would flag hardest

**CR 614.1c names three replacement templates. Only one was matched.** 236 lines
printing *"As [this permanent] enters…"* fell to `spell-or-static` — which the gap
census **excludes**, so the defect was not merely unfixed, it was
**unreportable**. `replacement` moved **1,963 → 2,178 lines**. Nothing in any
census had ever shown this.

**Ask of the next session:** the gap census cannot see anything that lands in
`spell-or-static`. That bucket holds 435 `as long as` statics and 315 additional-cost
clauses. **It deserves its own audit** — it is the one place the tooling is blind
by construction.

### 4b. Two CR rules that decide identical-looking English in opposite directions

| printed | CR | verdict |
|---|---|---|
| "…**causes you to discard** this card" | 701.9b distinguishes who chooses | **separate shape** — held out (11 lines) |
| "…**causes you to gain life**" | **119.9 equates it** with the base phrasing | **same shape** — folded in |

Not guessable from the wording. Only from the rule. This is §6b earning its keep.

## 5. PARENT LAYER — opened, nothing authored

`docs/PARENT-LAYER-OPENING-PACKET-2026-08-04.md`. Four decisions for Captain, each
with its measurement attached, none needing an API call.

**Headline: 3 of the 8 logged candidates cannot be authored yet.**
`punishes-attacking-you`, `saga-payoff` and `end-step-payoff` have **zero child
axes**, because their intended children are DELIVERY tokens and *"delivery-only
slugs are parents, not axes"*. The shape pass produced **vocabulary, not members**.

The five populated candidates: `sacrifice-payoff` (16 children / 132 cards),
`attack-payoff` (23 / 153), `lifegain-payoff` (12 / 171 — **already proposed in
batch-1 Q2**, found by dossier), `discard-payoff` (7 / 56), `precombat-setup`
(5 / 64).

**Child overlap is ~zero, and that is the RIGHT answer** — CLAUDE.md: *"same-card
co-occurrence is the WRONG test for substitute families."* S7's real gate is the
substitute lens in `experiments/measure/family_tree_evidence.py`, which exists,
is fixed-seed, and **has never been run against these candidates. That is the
zero-cost next step.**

## 6. WHAT THIS SESSION PROVES

**Gate 3 caught me, and I still under-ran it.** I dossiered `main-phase` and
`main-phase-trigger` — but not the qualified names I was about to *write*.
**`rule:postcombat-main-phase-trigger` already exists as an active axis with a
KEEP ruling in batch-6.** The ruling's content survived unchanged, and the axis
turns out to be under-populated (2 of 10 cards), so ratification there is a
*membership* addition. All 15 proposed names have since been checked; that was the
only collision. **Dossier the name you are about to write, not the name you
started from.**

**I reproduced the CDR-09 homograph failure in one line.** Grepping children for
`dodges-counterspells` on `counters-` returned `plus1-counters-matter` (NOUN) and
`counters-target-spell` (VERB) as siblings. §8a exists because that misfiled 17 of
33 counter axes. Gate 4 held: the check was wrong, not the codebook.

**The ground-truth set finally moved — by exactly the intended 4.** The 116/139
Clue routings were byte-identical through the whole verb fix (again catching
nothing), then moved on precisely the four lines the new rulings targeted:
Hostile Investigator → `any-discard-trigger`, Innocent Bystander, Lonis,
Unshakable Tail. Each strictly more specific. **Keep it, and keep widening it.**

## 7. HOUSEKEEPING — resolved

`docs/mtg-comprehensive-rules.md` was an **untracked, non-gitignored duplicate**
in this repo (970,852 bytes, mtime 2026-07-16 — pre-existing, not created by that
session). **Captain's call: deleted 2026-08-04.**

Verified safe before removing:

- **sha256 identical** to `~/Projects/mtjawnny.github.io/docs/mtg-comprehensive-rules.md`
  (`0b61b851b8d8…`) — the site copy is a complete replacement, nothing was lost.
- **Every code path already reads the site copy by absolute path** —
  `foundry_cr_checks.py`, `foundry_family_sweep.py`, `foundry_cr702_classes.py`,
  `foundry_keyword_buckets.py`. **Zero references to the local copy.**
- Gate 2 re-run clean afterwards.

This restores CLAUDE.md's stated arrangement exactly: the CR is *"deliberately
site-resident, read by absolute path."* **A manual CR grep from the pipeline repo
must now use the absolute site path** — `~/Projects/mtjawnny.github.io/docs/mtg-comprehensive-rules.md`.
Every CR citation in this session's nine documents was verified against that
byte-identical text.

## 8. NEXT WORK ITEM

1. **Ratify the 14 rows** from §4 — mechanical, one row each, DET already wired.
2. **Audit `spell-or-static`** (§4a) — the census is blind there by construction.
3. **Run `family_tree_evidence.py`** on the five populated parents (§5) — the S7
   gate they have never been through.
4. Four migrations still **logged, not executed** (carried from 2026-08-03), plus
   one new: `rule:lifegain-triggered-plus1-counter` →
   `rule:gain-life-trigger-plus1-counter`, which also closes §14 Q5's open
   `lifegain` exclusion, unresolved since 2026-07-31.
5. `rule:postcombat-main-phase-trigger` is under-populated: **2 of 10**.

**Open §2a question, logged not ruled:** §2a's three-way table does not name the
`~ or another X` compound ("Whenever Giott **or** another Dwarf you control
enters"). Six cards sit on it. `any-` is the defensible reading.
