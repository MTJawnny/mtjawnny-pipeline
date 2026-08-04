# LIFE-GAIN TRIGGERS — RULING (2026-08-04)

Fifth item in the 2026-08-04 gap pass. **Zero API calls.**

Gate-3 dossier: `lifegain-trigger` is **not** in the codebook and carries no
ruling — **but the dossier found what a bare grep would have missed.** An
**active** axis already carries the token: `rule:lifegain-triggered-plus1-counter`
(n=8), itself a CDR-09 walk rename of `rule:lifegain-triggered-counter`. The
census name and a ratified axis name collide, and that changes the answer.

**STATUS: RATIFIED 2026-08-04 (Captain).** `gain-life-trigger` entered
`docs/CODEBOOK-NAMING-GRAMMAR.md` §2 as row 9 of the 14-row sheet, with §14 Q5's
`lifegain` exclusion upheld — the token is `gain-life-trigger`, never
`lifegain-trigger`.

**§3's migration is still LOGGED, not executed.**
`rule:lifegain-triggered-plus1-counter` → `rule:gain-life-trigger-plus1-counter`
is a **codebook mutation** and needs Captain's word plus the backup law; §2 row 9
being ratified does not authorize it. Verified 2026-08-04 that the target name
now validates clean.

---

## 1. CR 119.9 names this exact trigger family

> **CR 119.9** — *"Some triggered abilities are written, **'Whenever [a player]
> gains life, . . . .'** Such abilities are treated as though they are written,
> '**Whenever a source causes** [a player] to gain life, . . . .' If a player
> gains **0 life, no life gain event has occurred**, and these abilities won't
> trigger."*

Two consequences, both load-bearing:

### 1a. "causes you to gain life" is the SAME shape — the exact opposite of discard

CR 119.9 **equates** the two phrasings by rule. So **Firesong and Sunspeaker**
(*"whenever a white instant or sorcery spell **causes you to gain life**"*) is
this token with a source restriction, **not** a separate family.

This is worth stating plainly because the 2026-08-03 discard ruling reached the
**opposite** verdict on an identical-looking surface pattern:

| printed | CR | verdict |
|---|---|---|
| "a spell or ability an opponent controls **causes you to discard**" | 701.9b distinguishes who chooses; fires only on an opponent's effect | **separate shape** — held out |
| "a white instant or sorcery spell **causes you to gain life**" | **119.9 equates it with the base phrasing** | **same shape** — folded in |

Same surface English, opposite rulings, and **the CR states both outright.** This
is §6b's "hard game logic is not up for interpretation" doing real work: the
answer was not guessable from the wording, only from the rule.

### 1b. 0 life is not a life-gain event

CR 119.9's last sentence is a membership rule, not trivia — a card that "gains 0
life" never triggers these. It matters for the `-conditional` question and is
recorded so a later session does not re-derive it.

**Replacement sibling, for the boundary:** CR 119.10 — *"Some replacement effects
are written, 'If [a player] would gain life…'"* Those are `replacement`, not this
token.

## 2. RULING — the token is `gain-life-trigger`, NOT `lifegain-trigger`

**Grammar §14 Q5 explicitly excluded the token `lifegain`:**

> *"Explicitly EXCLUDED despite corpus frequency… `lifegain`
> (**synonym-collision candidate against the ratified `gain-life` EFFECT verb,
> design goal #1**)."*

Design goal #1 is *no two slugs may describe the same mechanic*. Minting
`lifegain-trigger` beside the ratified §4 verb `gain-life` would install exactly
the duplication class the grammar was written to prevent — and would do it in the
DELIVERY slot, where it composes with every §2a prefix and multiplies.

| token | lines | cards | CR |
|---|--:|--:|---|
| **`gain-life-trigger`** | 87 | 86 | 119.3, **119.9** |

Reading is unambiguous by §2's established convention: `sacrifice-trigger` means
*triggers on a sacrifice*, not *a trigger that sacrifices*. `gain-life-trigger`
reads the same way, and uses the §4 D-2 bare verb stem.

**SCOPE measured** — `you-control` 83 · `opponent` 3 · `each` 0. The opponent
form is a real and different card (Kavu Predator, Punishing Fire — the
punish-their-lifegain deck), so scope is required from day one per §1.

## 3. MIGRATION — logged, not executed

`rule:lifegain-triggered-plus1-counter` (n=8, active) carries the excluded token
**and** the retired `-triggered-` connective. Target:
`rule:gain-life-trigger-plus1-counter`.

This is a codebook mutation and rides its own step under the backup law with
determinism ×2, per the standing "no midflight renames" rule (§12a precedent).
**Not executed here.** Note it also closes §14 Q5's open item — the exclusion was
logged *"to the naming audit"* and has been sitting unresolved since 2026-07-31.

## 4. Verification

| gate | result |
|---|---|
| determinism ×2 | byte-identical |
| known-good routings | 9/9 |
| shape homogeneity | 87/87 lines are the `gains life` event; no residual |

## 5. Parent candidate — logged, not authored

`rule:lifegain-payoff` (the Ajani's Pridemate / Voice of the Blessed job) and its
opposite number `rule:punishes-lifegain` (Kavu Predator, Punishing Fire). **These
are two parents, not one** — §6b rule 3: *"each opponent and each player… are
completely different and have real in-game consequences."* A card that rewards
**your** lifegain and one that punishes **theirs** answer different
deck-building questions off the same printed event.
