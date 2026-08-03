# SACRIFICE TRIGGERS — RULING (2026-08-03)

Eighth ruling in the 2026-08-03 shape series, at Captain's direction: *"take
sacrifice-trigger next. reference CR for sacrifice references."*

Gate-3 dossier on `sacrifice-trigger`, `sacrificed-trigger`, `is-sacrificed`:
**no prior ruling on any, in any status; none is in the codebook.** Clean ground.

**Zero API calls.**

---

## 1. The census number was 39% too high — sixth whole-line-vs-clause defect

The gap census reported **181 lines / 179 cards**. Measured against the trigger
*clause*, the family is **110 lines / 109 cards**.

The `sacrifice` branch tested the whole ability line, so any card whose **effect**
sacrifices something was counted as a sacrifice *trigger*:

- **Afiya Grove** — *"When this enchantment has no +1/+1 counters on it,
  **sacrifice it**."* Trigger: a counter-state condition.
- **Ember Swallower** — *"When this creature **becomes monstrous**, **sacrifice
  three lands**."* Trigger: becoming monstrous.

**Sixth instance of this bug class in this file** (self/other · phase triggers ·
graveyard · Snowfall's upkeep · is-attacked · now sacrifice). Fixed to test the
clause; the residual is now **zero unclassified**.

---

## 2. What the CR says sacrifice IS — three facts, all load-bearing

> **CR 701.21a** — *"To sacrifice a permanent, its controller moves it **from the
> battlefield directly to its owner's graveyard**. A player **can't sacrifice
> something that isn't a permanent, or something that's a permanent they don't
> control**. **Sacrificing a permanent doesn't destroy it**, so regeneration or
> other effects that replace destruction can't affect this action."*

### 2a. A sacrificed creature DIES — so both triggers fire

This is a two-rule derivation, stated as such rather than quoted from one place:

| | |
|---|---|
| CR 701.21a | sacrifice moves the permanent **from the battlefield to the graveyard** |
| **CR 700.4** | *"The term **dies** means 'is put into a graveyard from the battlefield.'"* |

Therefore **sacrificing a creature is dying**, and a card with a death trigger
and a card with a sacrifice trigger both see the same event. §1's multi-axis rule
applies: a card printing *"whenever you sacrifice a creature"* and a card
printing *"when this creature dies"* are **different shapes that overlap in
play** — which is a parent relationship, not a merge (§6b).

**Consequence for membership:** `death-trigger` and `sacrifice-trigger` are not
alternatives. A card may genuinely earn both, and neither subsumes the other —
a sacrifice trigger does not fire on a creature that is destroyed, and a death
trigger fires on both.

### 2b. Sacrifice is NOT destroy — the CR says so outright

*"Sacrificing a permanent **doesn't destroy it**."* Regeneration and
indestructible cannot touch it. This is §6b's "adjacent vocabulary is not
equivalent vocabulary" with the CR supplying the proof, and it is why
`sacrifice` and `destroy` are separate §4 EFFECT verbs and must stay so.

### 2c. Only the controller can sacrifice — which SIMPLIFIES the scope slot

*"A player can't sacrifice … a permanent they don't control."*

So in *"whenever an opponent sacrifices a creature"*, the creature is
**necessarily the opponent's own**. The scope token records **who sacrifices**,
and the sacrificed permanent's controller is always that same player. **No
second scope slot is needed for "whose permanent"** — the CR forecloses the
question. Recorded so a later session does not add one.

### 2d. Sacrifice as a COST is not this family

§9's cost-vs-effect law already governs: *"Sacrifice a creature: [Effect]"* has
the action **left of the colon**, so its delivery is `activated`. Confirmed in
the measurement — those lines are claimed by the cost-colon branch and never
reach this bucket.

---

## 3. RULING — one base token, three names via §2a

| token | lines | CR |
|---|--:|---|
| **`sacrifice-trigger`** (+ §2a subject prefix) | **110** | 701.21a, 700.4 |

**§2c's standing instruction was followed — §2a was checked before minting, and
it applies.** The subject split is real and printed:

| printed | §2a form | lines |
|---|---|--:|
| "when you sacrifice **this** creature / **~**" | `sacrifice-trigger` | 7 |
| "whenever you sacrifice **another** creature" | `other-sacrifice-trigger` | 25 |
| "whenever you sacrifice **a** creature" | `any-sacrifice-trigger` | 78 |

**Measured after wiring: 7 / 25 / 78.** My hand-classification said 8 / 24 —
Kingpin, Wilson Fisk ("whenever you sacrifice **~ or another** creature") is a
compound that I filed under the source and the tool files under `other-`. The
tool's read is the better one, since "another creature" is printed. Gate 4: the
measurement wins.

So **one ratification yields three names**, and no new subject vocabulary. Foul
Emissary ("when you sacrifice **this creature**") and Fleshtaker ("whenever you
sacrifice **another** creature") are different shapes for exactly the reason
§6a rule 3 gives.

### 3a. Scope — existing §6 tokens, no new vocabulary

| printed | scope | lines |
|---|---|--:|
| "**you** sacrifice" | `you-control` | 95 |
| "**a player** sacrifices" / "one or more players sacrifice" | `each` | 9 |
| "**an opponent** sacrifices" | `opponent` | 5 |

### 3b. One compound worth recording

**Mirkwood Bats** — *"Whenever you **create or sacrifice** a token"* — is a
compound of a sacrifice trigger and a **token-creation** trigger. The
create-a-token half has **no ratified delivery token**; it is a distinct shape
sitting inside the `unclassified-trigger` residual. Logged, not bundled.

---

## 4. Not authored — delivery-only slugs are parents

Per the cycling ruling §5 / batch-5 D16.

**Parent candidate, logged not authored:** `rule:sacrifice-payoff` — the
aristocrats job, *"my own permanents dying is the engine."* Under §6b this is
the genuine parent case: `any-sacrifice-trigger`, `death-trigger` and the
Blood-Artist damage families converge on one job by different printed shapes,
and §2a's finding above is precisely why they cannot be merged into one axis.

---

## 5. What this leaves

| shape | cards |
|---|--:|
| `unclassified-trigger` (residual) | ~966 |
| turned-face-up | 116 |
| discard-trigger | 111 |
| damage-received ("is dealt N damage") | 108 |
| lifegain-trigger | 95 |

**`discard-trigger` is the natural next one**, and it should be read with this
ruling's §2d in mind: discard appears constantly as a *cost* (`activated`) and
as an *effect*, so the clause test will matter there more than anywhere.
