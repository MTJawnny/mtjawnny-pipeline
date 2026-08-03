# "ATTACKS YOU" — THE DEFENDING MIRROR — RULING (2026-08-03)

Seventh ruling in the 2026-08-03 shape series, at Captain's direction: *"take
is-attacked next."* **36 ability lines / 35 cards.**

Gate-3 dossier on `is-attacked-trigger`, `attacked-trigger`,
`becomes-attacked`: **no prior ruling on any, in any status; none is in the
codebook.** Clean ground.

**Zero API calls.**

---

## 1. The CR enumerates what can be attacked — exactly three things

> **CR 506.3** — *"Only a creature can attack or block. **Only a player, a
> planeswalker, or a battle can be attacked.**"*
>
> **CR 506.2** — *"the nonactive player is the defending player; **that player,
> planeswalkers they control, and battles they protect** may be attacked."*
>
> **CR 508.1b** — *"the active player announces which **player, planeswalker, or
> battle** each of the chosen creatures is attacking."*

That is a **closed CR enumeration**, which §3 says is exactly the shape that
gets enumerated in advance rather than discovered card by card.

---

## 2. This is not `attack-trigger`, and not `player-attack-trigger`

Three distinct subjects, three tokens:

| printed | subject | token |
|---|---|---|
| "whenever **~** attacks" | the source, attacking | `attack-trigger` |
| "whenever **you** attack" | the attacking player's declaration | `player-attack-trigger` (ratified today) |
| "whenever a creature **attacks you**" | **the defending side** | **this ruling** |

The event is the same declaration (CR 508.1m) seen from the other side of the
table. The attacker triggers are keyed to the *attacking* player's action; this
one fires on the **defender**, who is not the active player at all.

---

## 3. The population — measured, zero unclassified

| printed | lines |
|---|--:|
| "attacks **you**" | 20 |
| "attacks **you or a planeswalker you control**" | 15 |
| "attacks **a planeswalker you control**" (only) | 1 |
| a **battle** being attacked | **0** |

Two lines were removed from this bucket during the measurement because they
never belonged — see §5.

---

## 4. RULING — one token, with a scope slot that is REQUIRED

| token | lines | cards | CR |
|---|--:|--:|---|
| **`is-attacked-trigger`** | 36 | **35** | 506.2, 506.3, 508.1b |

**§6 scope is mandatory here from day one**, because §1 says SCOPE is *"REQUIRED
the moment a scope-sibling exists"* — and all three CR-permitted objects are
already siblings in the printed corpus:

| scope | printed | lines |
|---|---|--:|
| `player` | "attacks you" | 20 |
| `player-or-planeswalker` | "attacks you or a planeswalker you control" | 15 |
| `planeswalker` | "attacks a planeswalker you control" | 1 |
| `battle` | — | **0 today** |

`player`, `planeswalker` and `battle` are **already §5 OBJECT vocabulary**; no
new scope words are needed.

### 4a. The `you or a planeswalker` form is ONE shape, not two

15 of 36 print the compound. Under §6a the printed word is the claim, and what
is printed is a **single trigger with two legal objects** — not two abilities.
It fires once when either is attacked. Splitting it would assert two triggers
where the card prints one; folding it into `player` would drop the planeswalker
claim. It earns its own scope value.

### 4b. `battle` is empty today — and that is the reversal condition

CR 506.3 permits battles to be attacked, and **zero cards trigger on it**.
`CORPUS-PASS-PLAN` §2 forbids an axis with no members ("an axis with zero
members is a hypothesis"), so **no `battle` node is instantiated**. The
vocabulary slot is ratified by the CR enumeration; the node arrives with its
first member, per §11.

---

## 5. Two members removed — the fifth whole-line-vs-clause defect

Both lines were in this bucket because their **effect** said "attack you", not
their trigger:

- **Willie Lumpkin, Postman** — *"Whenever Willie Lumpkin **deals combat damage
  to an opponent**, … that player **can't attack you**…"* → its trigger is
  combat damage.
- **Unstable Glyphbridge** — *"Whenever an opponent **casts a spell** during
  their turn, they **can't attack you**…"* → its trigger is a cast.

The `attacks` branch tested the whole line. **Fifth instance of this bug class
in this file** (self/other · phase triggers · graveyard · Snowfall's upkeep ·
now this). Fixed to test the trigger clause.

Fixing it exposed a **second, pre-existing defect**: the combat-damage branch
matched `(a|target)? (player|opponent)` but **not "an opponent"**, so
**17 cards** printing "deals combat damage to **an** opponent" (Kosei, Penitent
Warlord · Strixhaven Stadium · Etrata, Deadly Fugitive · Rampaging Raptor …)
had no delivery. Now routed — Willie Lumpkin to `combat-damage-to-player`,
Strixhaven Stadium to `any-combat-damage-to-player` via §2a.

Neither defect was visible until a ruling made someone look at this bucket.

---

## 6. Not authored — delivery-only slugs are parents

**Parent candidate, logged not authored:** `rule:punishes-attacking-you` — the
job being *"attacking me is a mistake"*. Briar Patch, Reveille Squad and
Sarkhan the Masterless answer it by different mechanisms, which is the §6b
parent case exactly.

---

## 7. Bonus finding this ruling forced — §2b was ratified but never applied

Captain's question about **Hero of Bladehold** exposed it: its `Battle cry` line
carried **no delivery at all**, while its second attack trigger did. §2b
(ratified this morning) makes a keyword's delivery derivable from the CR — but
nothing applied that derivation to the corpus.

**Measured: 12,419 ability lines — 20% of the corpus — were bare keyword lines
falling through to `spell-or-static`.** Now routed from the CR's own text:

| card | line | before | after |
|---|---|---|---|
| Hero of Bladehold | `Battle cry` | — | **`attack-trigger`** |
| Adriana, Captain of the Guard | `Melee` | — | **`attack-trigger`** |
| Brimaz, King of Oreskos | `Vigilance` | — | **`static`** |

**The created-ability boundary held**: Adriana's *"Other creatures you control
have melee."* is still correctly unrouted, because it **grants** the ability and
§2 gives the delivery to the creator, never the created one.

Full detail in the §2b entry of the grammar; recorded here because this ruling
is what surfaced it.
