# DISCARD TRIGGERS — RULING (2026-08-03)

> **RATIFIED 2026-08-04.** `discard-trigger` is now a §2 DELIVERY token (§2
> table row carries the full CR anchor set). **§2 vocabulary 30 → 31 tokens.**
>
> **⚠ THE NUMBERS BELOW ARE SUPERSEDED.** This document measured **96 lines /
> 88 cards**, split 83 `any-` / 12 source / 1 `other-`. That measurement was
> taken before `docs/TRIGGER-VERB-DERIVATION-2026-08-04.md` fixed the
> trigger-clause verb set. **Live at ratification:**
>
> | | ruled 08-03 | ratified 08-04 |
> |---|--:|--:|
> | lines / cards | 96 / 88 | **90 / 82** |
> | `any-discard-trigger` | 83 | **76** |
> | `discard-trigger` (source) | 12 | **3** |
> | `other-discard-trigger` | 1 | **0** |
> | `caused-to-discard` held out (§2b) | 11 | **11** |
>
> Six lines left the family entirely — Cloudpiercer (mutates), Concealing
> Curtains (transforms), Sauron (the Ring tempts you), Marina Vendrell's
> Grimoire (lose life), Battlefield Scavenger (exert) and Giott (enters) all
> printed "discard" in their **effect** half only. §2b's "caused to discard"
> holdout is implemented and reports as its own gap.
>
> **Three CR rules this document did not cite, now in the §2 row:**
> **702.35a** (madness — *"that player **discards it**, but exiles it instead"*;
> the discard still happens, so madness cards DO fire these),
> **702.29f** (typecycling triggers them too), and **701.9c** (hidden-zone
> discard leaves characteristics undefined). **702.187b** (mayhem) is named as
> the boundary: a static keyed on a past discard is not a trigger.


Ninth ruling in the 2026-08-03 shape series, at Captain's direction: *"take
discard-trigger next"* and *"reference the CR each time."*

Gate-3 dossier on `discard-trigger`, `discards-trigger`: **no prior ruling in
any status; neither is in the codebook.**

**Zero API calls.**

---

## 1. What the CR says discard IS

> **CR 701.9a** — *"To discard a card, move it **from its owner's hand** to that
> player's graveyard."*
>
> **CR 701.9b** — *"**By default, effects that cause a player to discard a card
> allow the affected player to choose** which card to discard. Some effects,
> however, require a **random** discard or allow **another player to choose**
> which card is discarded."*

### 1a. Discarding is NOT dying — the contrast with sacrifice is exact

The sacrifice ruling established that sacrifice moves a permanent *battlefield →
graveyard*, which is CR 700.4's definition of **dies**. Discard moves a card
**hand → graveyard**. Same destination, **different origin**, and CR 700.4 keys
on the origin.

So a discarded creature card **never dies**, and `death-trigger` cannot fire on
it. Two families that look adjacent and share a graveyard are mechanically
disjoint — §6b again, with the CR supplying the boundary both times.

### 1b. Cycling IS discarding — so these triggers overlap by CR construction

> **CR 702.29c** — *"'When you cycle this card' means 'When you **discard this
> card to pay an activation cost of a cycling ability**.'"*

A cycled card is discarded. That is precisely why CR 702.29d names the
**"cycles or discards"** shape, already ratified today as
`cycle-or-discard-trigger`. So `discard-trigger` and `cycled-trigger` are **not
disjoint**: cycling fires both. §1's multi-axis rule, and the reason the CR gave
the compound its own wording.

### 1c. Discard as a COST is not this family

§9's cost law governs, and CR 702.29a makes cycling the worked case: *"'Cycling
[cost]' means '[Cost], **Discard this card**: Draw a card.'"* — the discard is
**left of the colon**. Its delivery is `activated`, and those lines never reach
this bucket. Confirmed in the measurement.

---

## 2. RULING — one base token, §2a applies

| token | lines | cards | CR |
|---|--:|--:|---|
| **`discard-trigger`** (+ §2a subject prefix) | 96 | **88** | 701.9a, 701.9b |

Per §2c the prefix was checked before minting, and it applies:

| §2a form | lines |
|---|--:|
| `any-discard-trigger` | 83 |
| `discard-trigger` (source: "discard **this** card") | 12 |
| `other-discard-trigger` | 1 |

### 2a. Scope — existing §6 tokens

| printed | scope | lines |
|---|---|--:|
| "**you** discard" | `you-control` | 55 |
| "an **opponent** discards" | `opponent` | 16 |
| "a **player** discards" | `each` | 7 |

### 2b. `caused to discard` is a DIFFERENT shape — 11 lines, flagged not folded

Sand Golem, Ajani's Last Stand and Orvar all print *"When **a spell or ability
an opponent controls causes you to discard** this card…"*. The trigger is not
"you discarded" — it is **who caused it**, and it fires only on an opponent's
effect, never on your own.

**CR 701.9b is exactly why this is separate**: it distinguishes discards the
affected player chooses from those *"another player"* directs. The printed
distinction is real and consequential (a madness-adjacent shape). **Not folded
into `discard-trigger`; logged as its own candidate**, because folding it would
assert these fire on a voluntary discard, which they do not.

### 2c. `at random` — zero in triggers, but the vocabulary is CR-reserved

CR 701.9b names random discard as one of three modes. **Measured: zero trigger
clauses use it** — random discard appears only in *effects*. No token minted; the
CR reserves the distinction if a trigger ever prints it.

---

## 3. The systematic fix this ruling forced — CR 113.3c, applied everywhere

Discard was the **seventh** family in a row where the census over-counted for the
same reason: the event test read the whole ability line instead of the trigger
condition. Party Thrasher — *"At the beginning of your first main phase, you may
**discard** a card"* — is a phase trigger, not a discard trigger.

Seven instances was enough. The CR states the structure outright:

> **CR 113.3c** — *"Triggered abilities have a **trigger condition** and an
> **effect**. They are written as **'[Trigger condition], [effect]'**."*

**All 18 event tests in the trigger block now read the condition**, not the
sentence. Verified against the known-good set: Soul Warden `other-etb`, Sharp-Eyed
Rookie `any-etb`, Hero of Bladehold both attack triggers, Flickerwisp `etb`,
Silent Assassin `activated`, Willie Lumpkin `combat-damage-to-player`.

Two follow-on defects the systematic fix exposed, both now fixed:

1. **`trigger_clause` stopped at the first comma**, which breaks on commas
   *inside an object phrase*: *"Whenever a Mutant**,** Ninja, or Turtle you
   control enters"* became "whenever a mutant" — no event, so the line went
   unclassified. It now extends across commas until the condition carries an
   event verb.
2. **A clause opening "at the beginning of …" is a phase trigger, full stop.**
   Falling through let the event branches read the effect half. The phase block
   is now exhaustive and reports the phase honestly.

That second fix made a **previously invisible gap visible**: `main-phase` —
**94 lines / 86 cards** — was hidden inside other buckets and has no token. Plus
10 lines of `phase-trigger-unnamed`. Logged as the next natural target.

---

## 4. Not authored — delivery-only slugs are parents

**Parent candidate, logged not authored:** `rule:discard-payoff` — the madness /
hellbent / graveyard-fill job. Under §6b it is a genuine parent: `discard-trigger`,
`cycled-trigger` and `cycle-or-discard-trigger` converge on it, and §1b above is
why they cannot be merged into one axis.
