# Re-audit tier 2 — axes with exactly 2 members. Findings.

**Scope: 68 axes, 136 member-reads** — the largest tier in the codebook.
Worklist: `docs/REAUDIT-TIER-2-2-2026-08-02.md`.

The created-ability rule (Captain-ratified 2026-08-02, grammar §2) is now
encoded in `foundry_reaudit.py` and applied mechanically, along with two new
DET auto-flags. Validation: run against tier 1, the created-ability check
flags **exactly one** member — Garruk, the known instance — and zero NO QUOTE,
since those were fixed. The checks work; tier 2's numbers are real.

---

## 1. Confirmed defects — 10 axes

### 1a. `activated-plus1-counter-transfer-from-other-creature` — the NAME AND DEFINITION ARE INVERTED

> definition: "removes a +1/+1 counter **from another creature** the controller
> controls and places it **onto the source**"

Both members do the exact opposite:

- **Spike Hatcher** — "{2}, Remove a +1/+1 counter **from this creature**: Put a +1/+1 counter on **target creature**."
- **Spike Rogue** — identical shape.

The transfer runs **source → other**, not other → source. The slug says
`-transfer-from-other-creature`; it should say `-to-other-creature`. Both
members are correct cards for the *mechanic*; the axis describes the reverse of
what they do.

Note this axis was renamed by today's CDR-09 walk (from
`activated-counter-transfer-from-other-creature`). The walk was name-only and
correct; the inversion predates it and the walk had no mandate to see it.
**Needs: definition correction + a rename ratification.**

### 1b. Two axes are the SAME MECHANIC — grammar §1 design goal 1

| axis | definition | members |
|---|---|---|
| `conditional-attack-restriction-by-defending-player-land-type` | "cannot attack unless the player it is attacking controls a land of a specified type" | Island Fish Jasconius, Manta Ray |
| `conditional-attack-restriction-by-opponent-land-type` | "prevented from attacking unless the defending player controls a land of a specified type" | Red Cliffs Armada, Serpent of the Endless Sea |

All four members carry the **identical printed text**: "This creature can't
attack unless defending player controls an Island." Grammar §1 design goal 1 is
"**No two slugs may describe the same mechanic**" — this is a direct violation,
and it is the exact duplication class the naming grammar exists to prevent.
**Needs: merge ratification.** `defending-player` is the CR-correct term.

### 1c. Six member misfiles

| axis | member | why it does not belong |
|---|---|---|
| `redirects-combat-damage-to-controller-and-self` | **Weathered Bodyguards** | Definition is "source deals damage to a creature → damage to that creature's controller and to you" (Bellowing Fiend exactly). Weathered Bodyguards does the reverse: "all combat damage that would be dealt **to you** by unblocked creatures is dealt **to this creature** instead" — an incoming-damage redirect, a protective effect. |
| `redirect-damage-to-spell-controller` | **Mirrorwood Treefolk** | Definition is redirecting an instant/sorcery's damage back at **its controller**. Mirrorwood Treefolk redirects damage dealt **to itself** to **any target**, from any source. Neither the source restriction nor the destination matches. |
| `leaves-battlefield-trigger-create-token` | **Chittering Dispatcher** | Definition requires "**another** permanent you control leaves the battlefield during your turn … **limited to once per turn**". Chittering Dispatcher is "When **this** creature leaves the battlefield" — self, no once-per-turn. Belongs on the `-create-token-creature` sibling. |
| `prevent-combat-damage-unblocked-creature` | **Snag** | Definition is "an **activated ability**, paid by **returning the permanent to its owner's hand**". Snag is an instant with an alternative cost (discard a Forest). Gossamer Chains matches; Snag does not. |
| `lifegain-scales-with-color-count` | **Breathe Your Last** | Definition scales with "the number of **permanents of a chosen color** on the battlefield" (Treva exactly). Breathe Your Last gains "1 life for each of **its** colors" — the destroyed creature's own color count. Different stat. |
| `activated-grants-haste-other-creature` | **Boros Guildmage** | Definition requires "paid with mana **and tapping the source**", granting haste to "**another** target creature". Boros Guildmage is "{1}{R}: Target creature gains haste" — no tap, and it can target itself. Either the definition over-specifies or the member is wrong. |

### 1d. Two narrower definition mismatches

- `postcombat-main-phase-trigger` / **Belbe, Corrupted Observer** — definition
  says "each of the **controller's** postcombat main phases"; Belbe triggers at
  "the beginning of **each** postcombat main phase", every player's.
- `combat-damage-to-player-proliferate` / **Guildpact Informant** — definition
  says "**if a condition isn't met**, the controller proliferates instead"
  (Vexing Radgull's shape). Guildpact Informant proliferates unconditionally,
  and triggers on damage to "a player **or planeswalker**".

## 2. Unevidenced — 7 members with no quote

Auto-flagged, all `legacy-captain-seed`. Same class as tier 1's six. These need
quotes before their assignments mean anything.

## 3. False positives I caught before reporting — the all-faces rule earning itself

Three candidates died on verification, and the pattern is worth recording:

- **Kytheon, Hero of Akros** on `planeswalker-becomes-creature` looked like a
  clean inversion — a *creature* on a *planeswalker* axis. But it is a DFC, and
  the **back face** (Gideon, Battle-Forged) has "0: … becomes a 4/4 Human
  Soldier creature … that's still a planeswalker." Correct member. The house
  all-faces scanning rule is what caught it.
- **The Black Gate** on `cant-be-blocked-by-controller` — its third ability is
  "Target creature can't be blocked by creatures that player controls this
  turn." Correct.
- **Corrosion** on `cleanup-any-counters-on-leaving-battlefield` and both
  members of `life-loss-scales-with-mana-value` — all correct once read to the
  end of the text rather than the first 150 characters.

Every one of these would have been a confident wrong finding reported off a
truncated read. Same failure mode as this morning's three false renames.

## 4. Tally

| | tier 1 | tier 2 |
|---|--:|--:|
| axes read | 23 | 68 |
| member-reads | 19 | 136 |
| confirmed defective axes | 3 | 10 |
| unevidenced members | 6 | 7 |
| verified correct | 15 | ~119 |

**Tier 2 defect rate: 10 of 68 axes (15%), 8 of 136 member-reads (6%)** — much
lower than tier 1's 11-of-19, which fits the theory: 1-member axes are where a
single unexamined assignment is the *entire* evidence base.

## 5. Needs ratification before execution

1. `activated-plus1-counter-transfer-from-other-creature` → `-to-other-creature`, plus a corrected definition.
2. Merge the two `conditional-attack-restriction-by-*-land-type` axes; keep `defending-player`.
3. Six member re-homes (§1c) — three need a destination axis that may not exist.
4. Two definition corrections (§1d) — or ruling that the members leave instead.
5. 7 evidence quotes (mechanical, no new vocabulary — can execute on request).
