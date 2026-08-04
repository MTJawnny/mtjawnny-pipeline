# PUT-INTO-GRAVEYARD TRIGGERS — RULING (2026-08-04)

Sixth item in the 2026-08-04 gap pass. **Zero API calls.**

Gate-3 dossier on `to-graveyard-from-anywhere`: **no prior ruling; not in the
codebook.** One hit, a gap row in the current handoff.

**STATUS: RATIFIED 2026-08-04 (Captain).** All four tokens entered
`docs/CODEBOOK-NAMING-GRAMMAR.md` §2 as rows 10–13 of the 14-row sheet.

**§3's 11 zone-unstated lines stay deliberately unrouted** as
`to-graveyard-zone-unstated`, awaiting per-card ruling. That is the ratified
disposition, not an omission — it is recorded in §2's post-table note.

---

## 1. CR 700.4 defines `dies` NARROWLY — everything else is a different event

> **CR 700.4** — *"The term **dies** means 'is put into a graveyard **from the
> battlefield**.'"*

That is the whole ruling. §2 already calls the dies / leaves-battlefield line *"a
hard boundary both directions"* and D-1 made `death-trigger` the family word on
this exact anchor. The same discipline applies here, one level out:

- *"put into a graveyard **from the battlefield**"* **is** dies →
  `death-trigger`. Already claimed; not part of this ruling.
- *"put into a graveyard **from anywhere**"* is **strictly wider** than dies — it
  includes hand, library, graveyard, exile and stack. A card printing it does
  **not** make a dies claim, and must never take `death-trigger`.
- *"put into your graveyard **from your library**"* is **narrower still** — the
  mill shape.

Collapsing these would repeat exactly the error §2 warns about, and would make
the codebook assert that Dread (*"from anywhere"*) and a mill payoff are the
same mechanism.

## 2. RULING — the printed ZONE is the claim (§6a)

| token | lines | cards | printed |
|---|--:|--:|---|
| **`to-graveyard-from-anywhere-trigger`** | 33 | 33 | "from anywhere" |
| **`to-graveyard-from-library-trigger`** | 12 | 12 | "from your library" |
| **`to-graveyard-from-hand-trigger`** | 2 | 2 | "from your hand" |
| **`to-graveyard-from-other-zone-trigger`** | **0** | **0** | exile / stack — **reserved, NOT instantiated** |

§6a is the governing law: *"Game logic is game logic… All words used purposefully
and not up to interpretation."* The zone is printed, so the zone is the claim.

## 3. ELEVEN LINES ARE REPORTED, NOT ROUTED — and this is deliberate

11 lines print **no zone at all**: Genju of the Realm (*"when enchanted land is
put into a graveyard"*), Aetherworks Marvel (*"whenever a permanent you control
is put into a graveyard"*).

**CR 110.1 makes a *permanent* necessarily on the battlefield**, so
"a permanent … is put into a graveyard" **is** dies by CR 700.4 even with the
zone unstated. But a *card* is not on the battlefield, and the two cannot be
told apart by the printed words alone.

Rather than guess, these are emitted as **`to-graveyard-zone-unstated`** for
per-card ruling. This is the house style — *halt loudly, never best-guess* — and
it is the same call the Clue pass had to undo when it approximated a shape onto
its nearest neighbour.

## 4. Verification

| gate | result |
|---|---|
| determinism ×2 | byte-identical |
| known-good routings | 9/9 |
| 58 residual lines | fully partitioned: 33 + 12 + 2 + **0** + 11 unstated — see §4a |

### 4a. CORRECTION, measured at ratification 2026-08-04

**This document's own arithmetic did not add up, and the ratification pass caught
it.** The line above claimed *"33 + 12 + 2 + 1 + 11"*, which sums to **59**, not
the 58 it reports. The total was right; the per-row `1` was wrong.

| row | as ruled | as measured at ratification |
|---|--:|--:|
| `to-graveyard-from-anywhere-trigger` | 33 | **33** ✓ |
| `to-graveyard-from-library-trigger` | 12 | **12** ✓ |
| `to-graveyard-from-hand-trigger` | 2 | **2** ✓ |
| `to-graveyard-from-other-zone-trigger` | 1 | **0** |
| `to-graveyard-zone-unstated` | 11 | **11** ✓ |
| | 59 (claimed 58) | **58** ✓ |

So `to-graveyard-from-other-zone-trigger` is a **ratified token with zero
members** — the same disposition as `battle` on `is-dealt-damage-trigger`:
reserved by the ruling, **not instantiated**, and per §11 it instantiates the
moment one quote-verified member arrives. Zero members is a hypothesis, not an
absence, so the row stays.

**One line sits outside this partition and is NOT part of the family** —
Dreadhound, *"Whenever a creature **dies or** a creature card is put into a
graveyard **from a library**"*. The `dies` branch claims it first and emits
`to-graveyard-from-nonbattlefield`. It is a genuine **compound two-event
trigger**, which no row here covers. **Logged, not ruled.**

**Third arithmetic drift this project has caught by re-measuring a hand-written
breakdown** (ADD-06, `COUNTER-PLACED-RULING` §3b, now this). Standing lesson
unchanged: *the measurement wins and the document gets corrected.*

## 5. Parent candidate — logged, not authored

`rule:graveyard-fill-payoff` — the shared job of `to-graveyard-from-library`,
`discard-trigger` and `mill`. Already half-named by the logged
`rule:discard-payoff`; under §6b these converge on **one parent** because the job
("my graveyard is a resource") is identical while the printed mechanisms differ.
That is precisely the Tier-3 promise and belongs to the parent pass.
