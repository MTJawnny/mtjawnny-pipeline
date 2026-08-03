# Tier-2 decision packet — 2026-08-02

Everything needed to rule on the 10 defective axes and 7 unevidenced members
found in the tier-2 re-audit. Evidence is full oracle text, all faces.

Codebook `730f5e062f320f7e9fafa86c…`, 482 axes / 318 active. Nothing below is
executed.

**My recommendation is marked ✅ on each. Where I think the codebook is right
and the card is wrong, I say so; where I think the axis is wrong, I say that
too.**

---

## D1 — The inversion. `activated-plus1-counter-transfer-from-other-creature`

**Current definition:** "An activated ability removes a +1/+1 counter **from
another creature** the controller controls and places it **onto the source**."

**What both members actually do:**

| card | text |
|---|---|
| Spike Hatcher | "{2}, Remove a +1/+1 counter **from this creature**: Put a +1/+1 counter on **target creature**." |
| Spike Rogue | "{2}, Remove a +1/+1 counter **from this creature**: Put a +1/+1 counter on **target creature**." |

Direction is **source → other**. The axis says other → source. Name and
definition are both backwards; the two members are the correct cards for the
mechanic that actually exists.

| option | consequence |
|---|---|
| ✅ **Rename to `activated-plus1-counter-transfer-to-other-creature` + fix the definition** | Axis matches its members. One rename, one definition edit, no member moves. The Spike cycle is a real, coherent family. |
| Keep the name, move both members out | Leaves a 0-member axis asserting a mechanic no card performs — and the tier-1 finding says unevidenced axes shouldn't sit active. |
| Keep both, treat direction as a parameter | Contradicts today's `combat-`-is-a-restriction ruling: direction is exactly the kind of distinction that ruling says is load-bearing. |

## D2 — The duplicate pair

Two axes, one mechanic. **All four members carry identical printed text:**
"This creature can't attack unless defending player controls an Island."

| axis | definition | members |
|---|---|---|
| `conditional-attack-restriction-by-defending-player-land-type` | "cannot attack unless the player it is attacking controls a land of a specified type" | Island Fish Jasconius, Manta Ray |
| `conditional-attack-restriction-by-opponent-land-type` | "prevented from attacking unless the defending player controls a land of a specified type" | Red Cliffs Armada, Serpent of the Endless Sea |

Grammar §1 design goal 1: "**No two slugs may describe the same mechanic.**"

| option | consequence |
|---|---|
| ✅ **Merge into `-by-defending-player-land-type`** (4 members) | `defending-player` is the CR-correct term and matches the printed wording. The `-by-opponent-` slug becomes a `merged` tombstone. |
| Merge into `-by-opponent-` | Keeps the less accurate term; "opponent" is wrong in multiplayer — you attack a *defending player*, who is an opponent, but the restriction is templated on the defender. |

## D3 — Six member misfiles

### D3a · Weathered Bodyguards on `redirects-combat-damage-to-controller-and-self`

- **Axis:** "source deals damage to a creature → additional damage to that creature's controller **and** to the source's controller." That is Bellowing Fiend, precisely.
- **Card:** "As long as this creature is untapped, all combat damage that would be dealt **to you** by unblocked creatures is dealt **to this creature** instead."

This is a *lightning rod* — incoming damage redirected onto the permanent. The
opposite direction from the axis. **No existing axis fits**:
`prevents-damage-to-self` is prevention, not redirection.

✅ **New axis `rule:redirects-damage-from-controller-to-self`** — "A static
ability redirects damage that would be dealt to the controller onto this
permanent instead." Alternative: park the member and leave Bellowing Fiend as
the sole correct member.

### D3b · Mirrorwood Treefolk on `redirect-damage-to-spell-controller`

- **Axis:** redirects an instant/sorcery's damage back at **its controller** (Aegis of Honor).
- **Card:** "{2}{R}{W}: The next time damage would be dealt to **this creature** this turn, that damage is dealt to **any target** instead."

Neither the source restriction (any damage, not spell damage) nor the
destination (any target, not the spell's controller) matches.

✅ **New axis `rule:activated-redirect-damage-from-self-to-any-target`.**

### D3c · Chittering Dispatcher on `leaves-battlefield-trigger-create-token`

- **Axis:** "**another** permanent you control leaves the battlefield **during your turn** … **limited to once per turn**" (Suki, Courageous Rescuer).
- **Card:** "When **this** creature leaves the battlefield, create a 0/1 colorless Eldrazi Spawn creature token."

✅ **Move to `rule:leaves-battlefield-trigger-create-token-creature`** — it
exists, has 2 members, and its definition ("whenever the permanent leaves the
battlefield, it creates a creature token") fits exactly. **Cleanest of the
six — no new vocabulary.**

### D3d · Snag on `prevent-combat-damage-unblocked-creature` — this one inverts

- **Axis:** "An **activated ability**, paid by returning the permanent to its owner's hand, prevents combat damage from an unblocked creature this turn."
- **Gossamer Chains:** "Return this enchantment to its owner's hand: Prevent all combat damage that would be dealt by target unblocked creature this turn." — an activated ability ✓
- **Snag:** an *instant*. "You may discard a Forest card rather than pay this spell's mana cost. Prevent all combat damage that would be dealt by unblocked creatures this turn."

**The slug is unmarked, and grammar §1 says DELIVERY is OMITTED for spell
abilities** — the unmarked default *is* the spell. So the axis name belongs to
**Snag**, and it is **Gossamer Chains** that needs the `activated-` prefix.

| option | consequence |
|---|---|
| ✅ **Keep Snag; move Gossamer Chains to a new `activated-prevent-combat-damage-unblocked-creature`; rewrite the unmarked definition as the spell** | Follows §1's unmarked-default rule exactly. |
| Move Snag out, keep the activated definition | Requires renaming the axis to `activated-…` anyway, so it is the same work with the §1 default left unused. |

### D3e · Breathe Your Last on `lifegain-scales-with-color-count`

- **Axis:** "scales with the number of **permanents of a chosen color** on the battlefield" (Treva, the Renewer).
- **Card:** "Destroy target creature or planeswalker. You gain 1 life for each of **its** colors."

Different stat: the *target's own* color count, not a board count. §7's closed
stat vocabulary has `color-count` meaning the board stat.

✅ **New axis `rule:lifegain-scales-with-target-color-count`**, and add
`target-color-count` to §7's closed stat list.

### D3f · Boros Guildmage on `activated-grants-haste-other-creature`

- **Axis:** "paid with mana **and tapping the source**, grants **another** target creature haste."
- **Paragon of Fierce Defiance:** "{R}, {T}: **Another** target red creature you control gains haste" ✓ matches exactly.
- **Boros Guildmage:** "{1}{R}: **Target creature** gains haste until end of turn." No tap. Can target itself.

**This one I read as the definition being over-specified, not the member being
wrong.** Tapping is a cost detail, and cost details are not axis identity
unless a `-cost-` slug claims them (§9).

| option | consequence |
|---|---|
| ✅ **Broaden the definition**: drop the tap requirement, keep "another or self" open, rename to `activated-grants-haste-target-creature` | Both members fit. Matches how `activated-` axes elsewhere ignore whether {T} is in the cost. |
| Keep the narrow definition, move Boros Guildmage out | Needs a new near-identical axis differing only by a tap symbol — the `name-thin-difference` class the sweep already flags 10 of. |

## D4 — Two definition mismatches

| axis | member | mismatch | ✅ recommendation |
|---|---|---|---|
| `postcombat-main-phase-trigger` | Belbe, Corrupted Observer | Definition says "each of the **controller's** postcombat main phases"; Belbe says "**each** postcombat main phase" (every player's) | **Broaden the definition** to cover both, or split by whose phase. Belbe is genuinely a postcombat-main-phase trigger; only the *whose* differs. |
| `combat-damage-to-player-proliferate` | Guildpact Informant | Definition says "**if a condition isn't met**, proliferate instead" (Vexing Radgull's shape). Guildpact Informant proliferates unconditionally, and triggers on "a player **or planeswalker**" | **Broaden the definition** — the conditional belongs to Vexing Radgull, not the axis. Proliferate-on-combat-damage is the mechanic. |

## D5 — Seven unevidenced members (mechanical; no new vocabulary)

All `legacy-captain-seed`, all verified correct against full oracle text. I can
execute these on your word alone.

| axis | card | proposed quote |
|---|---|---|
| `activated-counters-target-spell` | Declaration of Naught | "{U}: Counter target spell with the chosen name." |
| `activated-tap-or-untap-any-permanent` | Fatestitcher | "{T}: You may tap or untap another target permanent." |
| `death-trigger-scroll-regrowth` | Cormela, Glamour Thief | "When Cormela dies, return up to one target instant or sorcery card from your graveyard to your hand." |
| `energy-outlet-condition` | Aether Inspector | "Whenever this creature attacks, you may pay {E}{E}. If you do, create a 1/1 colorless Servo artifact creature token." |
| `energy-outlet-condition` | Riparian Tiger | "Whenever this creature attacks, you may pay {E}{E}. If you do, it gets +2/+2 until end of turn." |
| `leaves-battlefield-trigger-create-token-creature` | Grixis Slavedriver | "When this creature leaves the battlefield, create a 2/2 black Zombie creature token." |
| `leaves-battlefield-trigger-create-token-mutagen` | Zoo Escapees | "When this creature leaves the battlefield, create a Mutagen token." |

**Related, already known:** Zoo Escapees is *also* on `etb-create-token-mutagen`
— an open C2 drift finding, since its trigger is leaves-the-battlefield, not
ETB. That membership should be dropped when D3/D5 execute.

---

## Cost summary

| decision | new axes | renames | merges | moves | definition edits |
|---|--:|--:|--:|--:|--:|
| D1 inversion | 0 | 1 | 0 | 0 | 1 |
| D2 duplicate | 0 | 0 | 1 | 2 | 1 |
| D3a Weathered Bodyguards | 1 | 0 | 0 | 1 | 0 |
| D3b Mirrorwood Treefolk | 1 | 0 | 0 | 1 | 0 |
| D3c Chittering Dispatcher | 0 | 0 | 0 | 1 | 0 |
| D3d Snag / Gossamer Chains | 1 | 0 | 0 | 1 | 1 |
| D3e Breathe Your Last | 1 | 0 | 0 | 1 | 0 (+§7 vocab) |
| D3f Boros Guildmage | 0 | 1 | 0 | 0 | 1 |
| D4 ×2 | 0 | 0 | 0 | 0 | 2 |
| D5 quotes | 0 | 0 | 0 | 0 | 0 (7 quotes) |
| **total** | **4** | **2** | **1** | **7** | **7** |

One `foundry_membership_move.py` spec covers all of it, under the usual gates:
backup with readback, member conservation, determinism ×2, lint and sweep
either side.

## What I'd flag as the judgment calls, not the bookkeeping

- **D3d is the interesting one.** It looks like "move a bad member" but the
  actual finding is that the *unmarked* slug was given to the activated card,
  against §1's rule that unmarked = spell. Ruling it the way I recommend sets a
  precedent for every unmarked slug in the codebook.
- **D3f is where I disagree with the codebook, not the card.** Two of the six
  "misfiles" (D3f, and arguably D4 ×2) are the axis being too narrow rather
  than the member being wrong. Worth ruling deliberately: over-specified
  definitions manufacture false misfiles, and they are also what produce the
  `name-thin-difference` findings the sweep already carries 10 of.
