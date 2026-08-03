# BEGINNING / END OF COMBAT TRIGGERS — RULING (2026-08-03)

Fifth ruling in the 2026-08-03 shape series, at Captain's direction: *"then take
begin-combat next."* Every CR claim is quoted from the local file.

**Zero API calls.**

---

## 1. GATE 3 — a prior proposal exists, unruled, and it carries a bad citation

`TIER-3-DECISION-PACKET-2026-08-02.md` raised this gap and offered two names:

> **Vocabulary gap this exposes (needs ratification, §10 rule 3):**
> `combat-trigger-` is **not in §2's closed DELIVERY vocabulary** … Proposed:
> `begin-combat-trigger` (CR 506.1/511), or ratify `combat-trigger` as-is since
> it is already in live use on this slug.

and its own ratification header records it as **still open**:

> *"the §2 DELIVERY vocabulary gap D2 exposed (`combat-trigger` /
> `begin-combat-trigger`), which was **flagged without a ✅ and remains open**."*

So there is **no prior ruling to overturn** — but there is a live axis,
`rule:combat-trigger-auto-attach-equipment` (n=2, active), already using the
losing name.

**⚠ The packet's citation is wrong.** It cites *"CR 506.1/511"* for the
**beginning** of combat. **CR 511 is the END of combat step.** The beginning of
combat step is **CR 507**. Corrected here.

---

## 2. The CR enumerates the combat steps, and three already have tokens

> **CR 506.1** — *"The combat phase has **five steps**, which proceed in order:
> **beginning of combat, declare attackers, declare blockers, combat damage,
> and end of combat**."*

Mapped against §2's live vocabulary:

| CR step | rule | §2 token | status |
|---|---|---|---|
| beginning of combat | 507 | — | **gap, this ruling** |
| declare attackers | 508 | `attack-trigger` | ratified |
| declare blockers | 509 | `blocks-or-becomes-blocked-trigger` | ratified |
| combat damage | 510 | `combat-damage-to-player` / `-to-creature` | ratified |
| end of combat | 511 | — | **gap, this ruling** |

**This is why `combat-trigger` is the wrong name and must not be ratified.**
§2's combat vocabulary is already **step-specific**, by design. A token called
`combat-trigger` would be readable as any of five steps — grammar design goal #2
verbatim: *"No slug may be readable as two different mechanics."* It is the same
error `mass-` was retired for in §6c: a word that spans a distinction the CR
draws sharply.

---

## 3. RULING — two tokens proposed

| token | lines | cards | CR |
|---|--:|--:|---|
| **`begin-combat-trigger`** | 333 | **331** | 506.1, **507** |
| **`end-combat-trigger`** | — | **17** | 506.1, **511.2** |

**CR 511.2** anchors the second: *"Abilities that trigger **'at end of combat'**
trigger as the end of combat step begins."*

Naming is symmetric with the ratified pair `upkeep-trigger` / `end-step-trigger`
and follows §1's formatting law (no articles): the CR's "beginning of combat" and
"end of combat" become `begin-combat` and `end-combat`.

### 3a. Scope uses EXISTING §6 tokens — no new scope vocabulary

Unlike the end step, which needed `active-player` ratified for its bare "the end
step" form, **every begin-combat shape maps onto scope tokens that already
exist**:

| printed | cards | §6 scope |
|---|--:|---|
| "at the beginning of combat **on your turn**" | 300 | `you-control` |
| "at the beginning of **each** combat" | 27 | `each` |
| "at the beginning of combat on **each player's** turn" | 1 | `each` |
| "at the beginning of combat on **each opponent's** turn" | 4 | `opponent` |
| "at the beginning of combat on **enchanted opponent's** turn" | 1 | `opponent` (Aura-attached) |

There is no bare "the combat step" form, because combat only ever happens on the
active player's turn — so the ambiguity that forced `active-player` at the end
step does not arise here.

Two edge members recorded rather than smoothed: **Kitt Kanto, Mayhem Diva**
("each player's turn" — symmetric, so `each`) and **Overencumbered** ("enchanted
opponent's turn" — the opponent is fixed by the Aura's attachment, not by a
scope token).

### 3b. ⚠ THE TRAP: "at end of combat" is USUALLY NOT a trigger

This is the same error class that made the end-step census read 601 when the
answer was 536, and here it is far more lopsided:

| shape | cards |
|---|--:|
| **genuine end-of-combat triggers** (the clause *is* "at end of combat") | **17** |
| **"at end of combat" as a DELAYED duration inside an effect** | **94** |

Silent Assassin is the model: *"{3}{B}: Destroy target blocking creature **at end
of combat**."* That is an **activated** ability creating a **delayed** trigger —
and §2's created-ability rule is explicit that *"a card does not deliver an
ability it CREATES."* `delayed` (CR 603.7) is already ratified vocabulary, so
those 94 need nothing.

**A naive count of the phrase returns 111. The real family is 17.** Stated per
Gate 4: the boundary is whether the trigger *clause* is "at end of combat", not
whether the line contains the phrase.

---

## 4. Migration — one live axis renames

| from | to | n |
|---|---|--:|
| `rule:combat-trigger-auto-attach-equipment` | `rule:begin-combat-trigger-auto-attach-equipment` | 2 |

Its own definition already says *"At the beginning of combat on its controller's
turn…"*, so this is a name-only correction with no definition change. Name-only,
2 memberships. **Logged, not executed** — a codebook mutation rides its own step
under the backup law per the standing no-midflight-renames rule (§12a).

---

## 5. Not authored — delivery-only slugs are parents

Per the cycling ruling §5 and batch-5 D16. The 331 begin-combat cards carry a
very wide effect spread; authoring `begin-combat-trigger-<effect>` children is a
corpus pass, not this ruling.

**Parent candidate, logged not authored:** `rule:precombat-setup` — the job being
*"before I attack, my board improves."* Greasefang, Hot Pursuit and the
auto-attach Equipment family all answer it by different mechanisms, which is
exactly the §6b parent case: same job, different printed shapes.

---

## 6. What this leaves

| shape | cards |
|---|--:|
| `unclassified-trigger` (residual, genuinely unnamed) | 1,000 |
| sacrifice-trigger | 180 |
| player-attacks ("whenever you attack") | 158 |
| turned-face-up | 116 |
| discard-trigger | 111 |
| damage-received ("is dealt N damage") | 108 |

**`player-attacks` is the interesting one next.** "Whenever you attack" is a
different printed shape from "whenever this creature attacks" (`attack-trigger`)
— it triggers once per combat on the *player's* declaration, not per creature.
CR 508 is the anchor.
