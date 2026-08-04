# MAIN PHASE TRIGGERS — RULING (2026-08-04)

Second item in the 2026-08-04 gap pass, at Captain's direction to *"work through
each item one at a time, referencing the CR each time."* **Zero API calls.**

Gate-3 dossier on `main-phase`, `main-phase-trigger`: no prior ruling; neither is
in the codebook.

> **⚠ GATE-3 CORRECTION, same session.** That dossier was **incomplete** — I ran
> it on the bare census name and on `main-phase-trigger`, but **not on the
> qualified forms I was about to propose.** One of them already exists:
>
> **`rule:postcombat-main-phase-trigger` is an ACTIVE axis (n=2, scope=all-players)
> and carries a KEEP ruling** — `docs/archive/TRIAGE-BATCH-6.md:226`, *"genuine
> narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or
> contradiction found"*, recorded again in `RATIFIED-DIRECTIVES-BATCH-4-6.md`.
> Members: Belbe Corrupted Observer, Florian Voldaren Scion.
>
> **Nothing below changes.** The name proposed here is byte-identical to the
> ratified one, and batch-6's KEEP independently corroborates the shape. But the
> axis is **under-populated**: it holds **2 of the 10** cards printing
> "postcombat main phase". Ratification is therefore a *membership* addition to
> an existing axis, **not** a new axis.
>
> The lesson is the one `SESSION-START-PROCEDURE.md` §3 already states and I did
> not fully apply: **dossier the name you are about to write, not the name you
> started from.** All 15 names proposed across the 2026-08-04 pass have now been
> checked against the codebook; this was the only collision.

**STATUS: RULED, NOT RATIFIED.** Three tokens are proposed below. The DET pass
already separates the three shapes and reports each honestly as its own gap —
nothing is approximated onto a neighbour. Ratifying is three §2 rows.

---

## 1. The CR names THREE main phases, not one

> **CR 505.1** — *"There are two main phases in a turn. In each turn, the
> **first main phase** (also known as the **precombat main phase**) and the
> **second main phase** (also known as the **postcombat main phase**) are
> separated by the combat phase. The precombat and postcombat main phases are
> individually and collectively known as the main phase."*
>
> **CR 505.1a** — *"Only the first main phase of the turn is a precombat main
> phase. **All other main phases are postcombat main phases.** This includes the
> second main phase of a turn in which the combat phase has been skipped. It is
> also true of a turn in which an effect has caused an **additional combat phase
> and an additional main phase** to be created."*
>
> **CR 505.1b** — *"Phrases such as 'first main phase,' 'second main phase,' and
> so on **count the number of main phases that have occurred only in the current
> turn** unless that text specifies otherwise."*

### 1a. "second" and "postcombat" are NOT synonyms — 505.1a says so outright

505.1's parenthetical reads like an alias, and taken alone it would justify one
token. **505.1a overrides it.** "Postcombat" is a **category** — *every* main
phase after the first. "Second" is a **count** (505.1b). On a turn with an extra
combat phase, the **third** main phase is postcombat but is **not** the second.

Apply §2's ratified split test (D3f): *does the distinction change WHEN or
WHETHER the effect happens, or only how much?* An extra-combat turn fires the
postcombat trigger and does not fire the second-main-phase trigger. **WHEN.
Split.**

The corpus prints the distinction deliberately: postcombat cards print the
**plural** — *"at the beginning of each of your postcombat main phase**s**"*
(Sphinx of the Second Sun, Neheb the Eternal, Megatron) — which is the
fires-on-every-one reading. "Second main phase" is always singular. This is the
Aggravated Assault / Relentless Assault axis of the format, so the difference is
load-bearing for deck-building, not academic.

### 1b. "first" and "precombat" ARE synonyms — and the corpus prints only one

CR 505.1 makes them the same phase, and 505.1a confirms it. **Measured: 63 of 63
lines print "first main phase"; ZERO print "precombat main phase."** The token is
named for the CR's category word (matching `begin-combat-trigger` /
`end-step-trigger`, which are also category-named) and the parent candidate
already logged as `rule:precombat-setup`.

## 2. RULING — three tokens, §6 scope required

| token | lines | cards | printed | CR |
|---|--:|--:|---|---|
| **`precombat-main-phase-trigger`** | 63 | 55 | "first main phase" | 505.1, 505.1a |
| **`second-main-phase-trigger`** | 29 | 29 | "second main phase" | 505.1b |
| **`postcombat-main-phase-trigger`** | 10 | 10 | "postcombat main phase" | 505.1a |

Scope is **mandatory from day one** (§1: required the moment a scope-sibling
exists) and uses existing §6 tokens — measured `you-control` 97 · `each` 4.
Blinkmoth Urn prints *"each player's first main phase"*; Shadow of the Second Sun
prints *"each of enchanted player's postcombat main phases"*.

**One line is left unqualified and NOT folded:** Carpet of Flowers, *"at the
beginning of each of your main phases"* — CR 505.1's *collective* sense, firing
on **both**. It is a real fourth shape at n=1, and §6b rule 1 says per-shape axes
are free. Reported as `main-phase-unqualified` pending a Captain call on whether
n=1 earns a token here.

## 3. Two DET defects this ruling forced, both fixed

### 3a. The phase tests were singular-only — 10 lines lost to a missing `s`

`\bmain phase\b` does not match "main phase**s**", and `\bupkeep\b` does not
match "upkeep**s**". Every postcombat card prints the plural, so **all 10 fell
through to `phase-trigger-unnamed`** — which is why this shape looked like it
did not exist. Ertai's Meddling (*"each of that player's upkeep**s**"*) was lost
the same way and is now correctly `upkeep-trigger`.

`phase-trigger-unnamed` is now **0**, from 11.

### 3b. §2d was not applied to "at the beginning of the NEXT <phase>"

CR 603.7a makes a *"next"* clause a **delayed** triggered ability, and §2d
ratified that its delivery belongs to whatever **created** it. Two lines opened
with one and were filed as phase triggers anyway:

| card | was | now |
|---|---|---|
| Siren's Call (Instant) | `end-step-trigger` | spell ability, unmarked |
| Vivien's Stampede (Sorcery) | `GAP:main-phase` | spell ability, unmarked |

The other ~332 "next end step" cards were already correct — they carry the
delayed trigger in the **effect** half of a real trigger, so they already
resolved to their creator's delivery. `END-STEP-TRIGGER-RULING`'s count moves
536 → 535 for exactly one card, Siren's Call.

## 4. Verification

| gate | result |
|---|---|
| determinism ×2 | **byte-identical** |
| known-good routings | 9/9 |
| Clue/investigate ground truth | 0 of 139 changed |
| lines changed | 106, each inspected |
| ratified-token movement | `end-step-trigger` 636→635, `upkeep-trigger` 1183→1184 — both intended |

## 5. Parent candidate — logged, not authored

`rule:precombat-setup` (already logged 2026-08-03) is the natural parent of
`precombat-main-phase-trigger`. Its postcombat sibling is a **different job** —
precombat is *setup before attacking*, postcombat is *converting damage into
value* (Neheb the Eternal's whole design). Two parents, not one.
