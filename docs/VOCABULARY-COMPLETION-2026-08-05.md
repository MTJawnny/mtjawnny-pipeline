# VOCABULARY COMPLETION — CR 120.1, CR 400.1, CR 303.4b (2026-08-05)

**Captain: *"complete all incomplete vocabulary."*** Every family that was
incomplete against a **closed CR enumeration** is now complete. **§2 DELIVERY
went 45 → 49 tokens** (plus four more added mid-pass, see §3), §6 SCOPE gained
one, and **31 gap lines closed with 62 re-routes and ZERO regressions**.

The re-route count is the story. **62 lines were sitting on a ratified token
that asserted something the card does not print** — and a gap census cannot
report a single one of them.

---

## 1. CR 120.1 — the source side named 2 of 4 recipients, and DEFAULTED the rest

> **CR 120.1** — *"Objects can deal damage to **battles, creatures,
> planeswalkers, and players**."* Sealed by **120.1a**.

The **recipient** side (`is-dealt-damage-trigger`) was ratified against that
full enumeration on 2026-08-04. **The source side never was** — and it was worse
than unrouted. The `any-` arm ended in a bare fallback:

```python
if re.search(r"\bdeals? damage to\b.{0,24}\bplayer\b", clause): -> any-damage-to-player
if re.search(r"\bdeals? damage to\b", clause):                  -> any-damage-to-creature   # ← everything else
```

**Any recipient that was not literally the word "player" became a creature.**
Hooded Blightfang — *"deals damage to a **planeswalker**"* — asserted a
creature-damage trigger. **A wrong ratified token is the one direction no census
in this toolchain reports.**

### 1a. The CR names its recipients INDIRECTLY far more often than directly

Reading only the four literal nouns left **31 lines "unstated"** — and every one
of them is a CR 120.1 recipient under a rule the CR states elsewhere:

| printed | recipient | CR |
|---|---|---|
| *"deals damage to **you**"* (19 lines — Dread, No Mercy, Michiko Konda) | player | **109.5** — *"The words 'you' and 'your' … refer to the object's controller"*; owner (108.3) and controller are players |
| *"deals damage to a **Dinosaur**"* (6 — Dinosaur Hunter, Vampire Slayer, Spider-Slayer) | creature | **109.2** — *"a description … that includes a card type **or subtype** … means a permanent of that card type or subtype"*, over CR 205.3m's parsed creature types |
| *"deals damage to **~**"* (Rona, Herald of Invasion) | read the card's own type line | 120.1 |

### 1b. Earliest-PRINTED wins, not longest

9 cards print a compound — *"deals combat damage to **a player or battle**"*
(Deeproot Wayfinder, Rankle and Torbran, Invasion of Kamigawa). A longest-first
scan silently swapped all 9 off `combat-damage-to-player`. **§6a: the printed
word is the claim, so the printed ORDER decides.** Length breaks ties only at
the same position, which is what keeps `planeswalker` from being read as
`player`. Bloodfeather Phoenix (*"an **opponent** or battle"*) proved the
indirect names must compete for position too, not be tried afterwards.

## 2. CR 400.1 — the zone branch named 2 of 7 zones

`to-graveyard-from-other-zone-trigger`'s branch tested `exile` and `the stack`.
CR 400.1 names **seven** zones. "Other" is now derived by **subtraction** from
the parsed enumeration — every zone that is not one of the three with its own
token (battlefield → `dies`, library, hand) — so `command` can never again be
omitted by an author's inventory of what came to mind.

**Measured: 0 lines for exile, stack, command and ante alike.** So
`to-graveyard-from-other-zone-trigger` is **a ratified token with zero
members** — reported here rather than hidden. Zero members is a hypothesis (the
`is-attacked-trigger` battle precedent), and it now has correct scaffolding for
all four of its zones.

## 3. FOUND MID-PASS — `noncombat` existed on one side of the family only

The recipient side carries all three of `is-dealt-damage-trigger`,
`-combat-` and `-noncombat-`. The source side had two. `\bcombat\b` does not
match inside "noncombat" (no word boundary after the "n"), which is exactly how
**9 cards printing *"deals NONCOMBAT damage"* came to sit on
`any-combat-damage-to-player`** — a token asserting the precise claim the card
negates. Chandra's Incinerator, Chandra's Pyreling, Niv-Mizzet Visionary, Thor,
Virtue of Courage; plus Taii Wakeen and Crude Abattoir on the creature side.

**Completing a family means mirroring all three restrictions, not two.** Four
`noncombat-damage-to-*` rows added, matching CR 120.1's four recipients.

## 4. READING PAST COMMAS AND PERIODS — `trigger_condition()`

Captain, mid-pass: *"build out logic to read cards past comma's and periods."*
The `--strict` gate had just caught 12 regressions from a naive
`clause.split(",")[0]`, and the project has now been bitten from **both**
directions:

| | failure |
|---|---|
| too **EARLY** | `split(",")[0]` truncates an enumeration — *"Whenever one or more Scouts, Pirates, **and/or** Rogues you control deal combat damage to a player"* loses its own verb. The recorded trap: *"a trigger clause does not end at the first comma."* |
| too **LATE** | `trigger_clause` walks PAST the condition when the condition's verb is unlisted, and picks up a verb from the EFFECT. **Heart of Bogardan** — *"When a player doesn't **pay** … cumulative upkeep, this enchantment **deals** X damage to target player or planeswalker"* — an UPKEEP trigger whose effect deals damage, moved off `upkeep-trigger` |

**`trigger_condition()` needs no verb list, which is why it survives a verb the
CR does not enumerate.** CR 113.3c gives the template — *"[Trigger condition],
[effect]"* — and English gives the cut: **an enumeration closes with a
coordinating conjunction on its final element** (`A, B, and C` / `and/or C` /
`or C`), so a comma is a list separator exactly while some *later* segment still
opens with `and` / `or` / `and/or`. The first comma with no such continuation
ahead of it is the condition/effect boundary. **Periods end it
unconditionally** — a trigger condition never spans sentences.

Verified against all four shapes: the three enumerations keep their full
condition; Heart of Bogardan's damage phrase is correctly excluded.

## 5. CR 303.4b — `enchanted-player`, a §6 SCOPE token

> **CR 303.4b** — *"The object or **player** an Aura is attached to is called
> **enchanted**."*
> **CR 702.5a** — *"Enchant is a static ability, written 'Enchant [object **or
> player**].'"*

**54 corpus lines** print it — the Curse cycle, plus Curse of Obsession and
Righteous Authority on `draw-step-trigger` and Grievous Wound on
`is-dealt-damage-trigger`, all three named in §2's own rows as carrying **no
scope token at all**. `opponent` is wrong (an Aura may enchant any player,
including you); `you-control` and `each` are simply false. Ratified into §6.

## 6. RESULT

| | before | after |
|---|--:|--:|
| §2 DELIVERY tokens | 45 | **53** (+8: four CR 120.1 recipients × combat/any, four × noncombat) |
| §6 SCOPE tokens | — | **+1** (`enchanted-player`) |
| gap lines closed | — | **31** |
| **re-routes off a wrong ratified token** | — | **62** |
| regressions (ratified → None) | — | **0** |
| `any-damage-to-creature` | 83 | **30** (−53, the fallback's victims) |
| `any-damage-to-player` | 25 | **79** |
| `any-combat-damage-to-player` | 242 | **259** |
| `combat-damage-to-planeswalker` | 0 | **1** |
| `any-damage-to-planeswalker` | 0 | **2** |
| `noncombat-damage-to-player` | 0 | **8** |
| `noncombat-damage-to-creature` | 0 | **2** |
| `combat-damage-to-battle` · `any-damage-to-battle` · `noncombat-damage-to-*` (pw/battle) | 0 | **0 — reserved, emitters present** |
| unrouted | 16,270 | **16,239** |

## 7. Verification

| gate | result |
|---|---|
| routing diff `--strict` | **0 regressions**, 62 re-routes (all read), 31 closures |
| every re-route read | **yes** — 51 `→ any-damage-to-player` (the "deals damage to you" fallback victims), 9 `→ noncombat-*`, 2 `→ any-damage-to-planeswalker` |
| determinism ×2 | **byte-identical** |
| name-invariance | **1** — the known Storm of Memories artifact |
| Clue/investigate ground truth | **improved by 1, and read.** 102 → 103 buildable: **The Rani**, *"deals combat damage to **one of your opponents**"*, moved `unclassified-trigger` → `any-combat-damage-to-player`. The old regex required a fixed determiner set. **No Clue line lost a token** — the property that matters is intact |
| `routed_lines` · `keyword_homes` | 61,907 · 150 **UNCHANGED** |
| lint · family sweep · drift | clean · 6 blocking, the same 6 · 35 unchanged |

## 8. WHAT THIS PASS PROVES

**A fallback is a wrong answer with a ratified name.** The bare
`deals? damage to` arm had been returning `any-damage-to-creature` for every
recipient it did not recognise. 53 lines. Nothing reported it, because a census
counts what is *missing*, and these were not missing — they were **present and
false**. Every "default to the common case" in a classifier is this waiting to
happen.

**Completing a family means completing BOTH of its sides and ALL of its
restrictions.** CR 120.1's recipient side was ratified in full on 2026-08-04
and the source side was left at two of four for a year of sessions, with
`noncombat` present on one side and absent on the other. **When ratifying one
side of a mirrored family, check the mirror in the same pass.**

**A markdown table is an API — third instance.** I wrote
`noncombat-damage-to-planeswalker · noncombat-damage-to-battle` as ONE row.
§2's table is parsed one token per row, so a row naming two ratifies **neither**;
the token count read 51 instead of 53 and both emitters would have returned
`None`. Same family as the two recorded instances (a note table under `## 2.`
being ingested; reading to `## 3.` instead of the first `###`). **Caught only
because the count was checked against the arithmetic** — nothing gates it.

**Five defects in this pass were mine, and the diff or the count caught every one**: a
doubled `any-any-` prefix from a name collision (`any-` means "no combat
restriction" in the token and "source included" in §2a — **the subject prefix
is only safe on a token whose name does not already begin with one of its
values**), a longest-first scan that swapped 9 compounds, a comma cut that
truncated 3 enumerations, and 9 lines routed to `noncombat-*` rows I had not yet
written. **`--strict` refusing to proceed on 12 regressions is what turned all
of them into corrections instead of a commit.**
