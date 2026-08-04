# DRAW-STEP TRIGGERS + RESIDUAL PHASES — RULING (2026-08-04)

Eighth and final item in the 2026-08-04 shape pass. **Zero API calls.**

Gate-3 dossier on `draw-step`, `draw-step-trigger`: **no prior ruling in any
status; neither is in the codebook.**

**STATUS: RATIFIED 2026-08-04 (Captain).** `draw-step-trigger` entered
`docs/CODEBOOK-NAMING-GRAMMAR.md` §2 as row 14 — the last of the 14-row sheet —
closing the turn-structure family end to end.

**§3's `enchanted-player` scope token is NOT ratified.** New vocabulary is a
ratification, not a typo fix, and Captain's word covered the 14 §2 DELIVERY rows,
not §6. The two affected lines (Curse of Obsession, Righteous Authority) carry
**no** scope token rather than a guessed one. The gap is not draw-step-specific —
it recurs wherever Auras appear, and `IS-DEALT-DAMAGE-RULING-2026-08-04.md`
independently hit it on Grievous Wound. **It is the top item on the next
decision sheet.**

---

## 1. The turn-structure family is now complete

§2 already carries the two bookends. Draw step is the missing middle, and it is
the same shape with a different CR number:

| step | CR | token | status |
|---|---|---|---|
| untap | 502 | — | no triggers print it |
| upkeep | 503 | `upkeep-trigger` | ratified |
| **draw** | **504** | **`draw-step-trigger`** | **this ruling** |
| precombat main | 505.1 | `precombat-main-phase-trigger` | ruled 2026-08-04 |
| begin combat | 507 | `begin-combat-trigger` | ratified |
| end combat | 511 | `end-combat-trigger` | ratified |
| postcombat main | 505.1a | `postcombat-main-phase-trigger` | ruled 2026-08-04 |
| end step | 513 | `end-step-trigger` | ratified |

> **CR 504.1** — *"First, **the active player draws a card**. This turn-based
> action doesn't use the stack."*

The draw itself is a **turn-based action**, not an ability — same structural note
CR 714.3c supplied for Saga progression, and the reason `draw-step-trigger` names
the *step*, not the draw. A card triggering on the **draw event** is a different
family and is not this token.

## 2. RULING

| token | lines | cards | CR |
|---|--:|--:|---|
| **`draw-step-trigger`** | 31 | 30 | 504.1 |

**SCOPE is mandatory from day one** (§1: required the moment a sibling exists) —
siblings exist immediately:

| printed | scope | lines |
|---|---|--:|
| "each player's draw step" | `each` | 14 |
| "your draw step" | `you-control` | 14 |
| "each opponent's draw step" | `opponent` | 1 |
| "**enchanted player's** draw step" | **no §6 token** | 2 |

## 3. A GAP IN §6's SCOPE VOCABULARY — logged, needs ratification

Two lines have **no available scope token**:

- Curse of Obsession — *"at the beginning of **enchanted player's** draw step"*
- Righteous Authority — *"at the beginning of the draw step of **enchanted
  creature's controller**"*

§6's list is `self` · `you-control` · `you-own` · `active-player` · `opponent` ·
`any` · `each` · `target` · `defending-player` · `two-target`. **None of them
names the player an Aura is attached to.** This is not a draw-step problem — it
recurs wherever Auras appear, and it already showed up in the same session's
is-dealt-damage census (Grievous Wound, *"whenever **enchanted player** is dealt
damage"*).

**Proposed:** `enchanted-player` as a §6 scope token, anchored on CR 303.4
(Auras) and CR 702.5 (enchant). **Not minted here** — new vocabulary is a
ratification, not a typo fix.

## 4. `phase-trigger-unnamed` is now ZERO

It stood at 10–11 lines all session and was the residual bucket for phase shapes
with no token. It is now **empty**, because the two causes were found:

1. the singular-only phase regexes (`\bmain phase\b` missing "main phase**s**",
   `\bupkeep\b` missing "upkeep**s**") — see `MAIN-PHASE-RULING-2026-08-04.md` §3a;
2. §2d's delayed-trigger rule not being applied to "at the beginning of the
   **next** …" — same doc, §3b.

**One line remains deliberately unrouted:** Carpet of Flowers,
*"at the beginning of each of your main phases"* — CR 505.1's **collective**
sense, firing on both main phases. Reported as `main-phase-unqualified` (n=1)
pending a Captain call, per §6b rule 1 (*"per-shape axes are free… thinness of
membership is not an argument against a real shape"*).

## 5. Verification

| gate | result |
|---|---|
| determinism ×2 | byte-identical |
| known-good routings | 9/9 |
| `phase-trigger-unnamed` | 11 → **0** |
