# RECIPIENT-SIDE DAMAGE TRIGGERS — RULING (2026-08-04)

Third item in the 2026-08-04 gap pass. **Zero API calls.**

Gate-3 dossier on `damage-received`, `is-dealt-damage-trigger`: **no prior ruling
in any status; neither is in the codebook.** The census name `damage-received`
appears in three decision packets only as a *gap row*, never as a verdict.

**STATUS: RATIFIED 2026-08-04 (Captain).** All four tokens entered
`docs/CODEBOOK-NAMING-GRAMMAR.md` §2 as rows 4–7 of the 14-row sheet. The DET
pass already separated the four shapes and reported each honestly, so
ratification moved no line.

**`battle` stays reserved and uninstantiated** (0 members), per CR 120.1's closed
enumeration and the `is-attacked-trigger` precedent — zero members is a
hypothesis, not an absence. **The `enchanted player` scope gap this document
surfaced (Grievous Wound) is NOT closed**; `enchanted-player` remains PROPOSED §6
vocabulary — see `DRAW-STEP-RULING-2026-08-04.md` §3.

---

## 1. This is the RECIPIENT side of a family whose SOURCE side is already ratified

§2 already carries four source-side damage tokens — `combat-damage-to-player`,
`combat-damage-to-creature`, `any-damage-to-player`, `any-damage-to-creature`.
All four read *"**~** deals damage to X"*. Nothing named *"**X** is dealt
damage"*, so 110 lines had no token.

**This is structurally identical to the `is-attacked-trigger` ruling of
2026-08-03**, which named the defending side of a declaration whose attacking
side (`attack-trigger`) was already ratified. Same argument, same shape, and the
CR supplies the same kind of closed enumeration.

## 2. CR 120.1 is a CLOSED recipient enumeration

> **CR 120.1** — *"Objects can deal damage to **battles, creatures,
> planeswalkers, and players**. This is generally detrimental to the object or
> player that **receives** that damage."*
>
> **CR 120.1a** — *"Damage **can't** be dealt to an object that's not a battle,
> a creature, or a planeswalker."*

So the recipient slot is enumerable and sealed, exactly as CR 506.3 sealed the
`is-attacked-trigger` object slot. Measured: **creature 103 · player 6 ·
planeswalker 3 · battle 0**. `battle` is reserved by the enumeration and **not
instantiated** — zero members is a hypothesis, per the is-attacked precedent.

## 3. RULING — one base token, three CR-defined qualifiers

| token | lines | cards | CR |
|---|--:|--:|---|
| **`is-dealt-damage-trigger`** (+ §2a prefix) | 101 | 100 | 120.1, 120.1a |
| **`is-dealt-combat-damage-trigger`** | 5 | 5 | 120.2a |
| **`is-dealt-excess-damage-trigger`** | 4 | 4 | **120.10** |
| **`is-dealt-noncombat-damage-trigger`** | 2 | 2 | 120.2a (negation) |

### 3a. `excess` is a CR term of art, not prose

> **CR 120.10** — *"**Some triggered abilities check whether a permanent has been
> dealt excess damage.** These abilities check after the permanent has been dealt
> damage by one or more sources. If those sources together dealt an amount of
> damage to a creature **greater than lethal damage**, excess damage equal to the
> difference was dealt to that creature."*

The CR names this trigger family in its own sentence. Aegar the Freezing Flame,
Toralf God of Fury and Fall of Cair Andros all print it. Folding these into the
base token would assert they fire on *any* damage, which is false — they fire
only past lethal. §6a: the printed word is the claim.

### 3b. `combat` / `noncombat` follow the ratified restriction law

`DAMAGE-DELIVERY-RULING-2026-08-02` ruled that **`combat-` is a RESTRICTION, not
decoration**, and the same holds for its printed negation. Chandra's Spitfire and
Wildfire Elemental print *"is dealt **noncombat** damage"* — a strictly narrower
claim than the base token and a different deck-building mechanism. Three
separate shapes, never one axis.

### 3c. §2a applies; `other-` is empty

Measured **source 74 · `any-` 38 · `other-` 0**. The source form dominates here
(unlike discard), because the archetypal card is *"Whenever **this creature** is
dealt damage"* — Trapjaw Tyrant, Hornet Nest, Indoraptor. `other-` at zero is
reported, not asserted absent.

### 3d. SCOPE is mandatory from day one

§1: required the moment a scope-sibling exists, and they exist immediately —
Wrathful Red Dragon (*"a Dragon **you control**"*), Kazarov (*"a creature **an
opponent controls**"*), Grievous Wound (*"**enchanted player**"*). Existing §6
tokens cover all of it; no new scope vocabulary.

## 4. DET defect this ruling fixed

The old test was `\bis dealt\b.{0,30}\bdamage\b` — a 30-character window that
**dropped two lines** carrying a longer qualifier phrase into
`unclassified-trigger`. The window is now `[^,]{0,60}` and, critically, is
bounded by the comma so it cannot cross into the effect half (CR 113.3c).
`unclassified-trigger` 1008 → 1006.

## 5. Verification

| gate | result |
|---|---|
| determinism ×2 | **byte-identical** |
| known-good routings | 9/9 |
| total recipient-side lines | 110 → 112 (+2 recovered from `unclassified`) |

## 6. Parent candidate — logged, not authored

`rule:damage-payoff` / `rule:punishes-damaging-me` — the Hornet Nest / Trapjaw
Tyrant / Wrathful Red Dragon job ("attacking me costs you"). It is a genuine
**job** sibling of the already-logged `rule:punishes-attacking-you`, and under
§6b the two may well be one parent: *same job, different words.* That is
interpretive and belongs to the parent pass, not here.
