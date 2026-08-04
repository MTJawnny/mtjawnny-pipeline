# SELF-REFERENCE VOCABULARY — DERIVED FROM CR 205.2a (2026-08-05)

**Captain's finding: the self-reference noun set must cover every card type.**
It did not. **Six of CR 205.2a's fifteen were missing**, and the parser that
should have supplied them was itself dropping the last member of every CR 205
list — behind a guard that counted instead of checking content.

**Zero lines moved. This is a correctness and completeness fix, not a routing
change.** Zero API calls, no new vocabulary.

---

## 1. What Captain caught

> *"Chain of Plasma deals 3 damage to any target is not a creature. make sure to
> create self reference for rules for every card type."*

`STEP-2C` §2 used Chain of Plasma — a **Sorcery** — as the worked example under a
shape named for `this creature`. The routing was correct (CR 113.3a excluded it
by card type), but the underlying vocabulary was not: `build_self_noun_rx`
harvested its nouns **from corpus type lines**, and the corpus gate excludes the
very layouts that carry six of the fifteen card types.

## 2. DEFECT 1 — six card types unreachable as a self-reference

| CR 205.2a card type | was in the set? |
|---|---|
| artifact · battle · creature · enchantment · instant · kindred · land · planeswalker · sorcery | present (9) |
| **conspiracy · dungeon · phenomenon · plane · scheme · vanguard** | **MISSING (6)** |

**`scheme` is the one that makes this a defect rather than a gap**, because the
CR names that exact string in its own rule:

> **CR 109.2d** — *"If an ability of a scheme card includes the text **'this
> scheme,'** it means the scheme card in the command zone on which that ability
> is printed."*

The CR publishes a rule about `this scheme`; the classifier could not see it.

**The cause is the one CLAUDE.md predicts, with a data source standing in for
the hand-list.** The set was derived from a population that **structurally
cannot contain** those types — the gate drops plane/scheme/phenomenon layouts —
so the derivation was guaranteed to be incomplete and looked healthy while being
so. Measured today all six are at **zero** corpus lines, which is exactly why
nothing caught it. **Zero members is a hypothesis, not an absence** — the
`is-attacked-trigger` battle-slot precedent — and a widened corpus gate must not
silently fail to see them.

**FIX:** card types are now parsed from **CR 205.2a**, via `type_vocabulary()`
in `foundry_cr702_classes.py` — a helper that **already existed** for CR 702.14a's
landwalk template. Gate 3b's lesson again: the thing was already written.

## 3. DEFECT 2 — the CR 205 parser dropped the LAST member of every list

Found while wiring defect 1, and it is upstream of both.

The CR writes these lists with an **Oxford comma**: *"…, scheme, and vanguard."*
The split was `re.split(r",\s*|\s+and\s+", …)`, which consumes the comma first
and leaves the conjunction attached to the final item:

| CR 205 list | parsed | should be |
|---|---|---|
| card types | `and vanguard` | `vanguard` |
| supertypes | `and world` | `world` |
| land types | `and urza’s` | `urza’s` |

**So `vanguard`, `world` and `urza’s` were absent from every consumer** — and
`urza’s` is a CR 702.14a landwalk base, so the landwalk template has been built
from 16 land types rather than 17.

### 3a. The guard was satisfied by the defect it existed to catch

```
for key, least in (("card_types", 15), ("land_types", 17), ("supertypes", 5)):
    if len(out[key]) < least: halt(...)
```

The junk token **kept the count correct** — 15 card types, of which one was
`and vanguard` and `vanguard` itself absent. **A guard that counts cardinality
cannot see a substitution.** The guard now asserts **content**: the known-last
member of each list must be present, and no member may begin with `and `. Both
are precisely the shape this bug class produces.

This is a new instance of a recorded family — *"a ratified token with no
emitter"*, *"a ratified standard with no caller"*, and now *a halt-guard whose
predicate the defect satisfies*. All three look healthy from outside.

## 4. DEFECT 3 — supertypes and planeswalker names were being harvested as nouns

The old harvest took **every word of the whole type line**, so CR 205.4a's
supertypes (`basic`, `legendary`, `snow`, `world`) and planeswalker subtypes
read as names (`ajani`, `ashiok`, `arlinn`) entered the set. A supertype is an
**adjective** — no card says *"this legendary"*.

**FIX:** subtypes are now harvested only from **after the long dash**, which is
where CR 205.3b says they are printed, with supertypes explicitly excluded.

## 5. The two-source split, and why it is not one rule

| | source | why |
|---|---|---|
| **card types** | **parsed from CR 205.2a** | a CLOSED list, published in one sentence — CLAUDE.md's derivation law applies directly |
| **subtypes** | corpus harvest, after the dash | CR 205.3b makes them open and set-specific (`Equipment`, `Siege`, `Spacecraft`, `Class`, `Case`); the CR does not enumerate them in one place, so harvesting is legitimate *here* |
| **supertypes** | excluded | CR 205.4a; adjectives, never the noun of a self-reference |

The halt-guard now asserts both ends: `equipment` must be present (the subtype
harvest ran) **and** every CR 205.2a card type must be present (the CR parse
ran).

## 6. RESULT

| | before | after |
|---|--:|--:|
| self-reference noun set | 447 | **448** |
| CR 205.2a card types reachable | **9 of 15** | **15 of 15** |
| CR 205 land types parsed | 16 + 1 junk | **17** |
| CR 205 supertypes parsed | 4 + 1 junk | **5** |
| attachment types routed (CR 301.5a / 301.6 / 303.4) | **2 of 3** | **3 of 3** |
| lines moved | — | **1** (Darksteel Garrison, §8a) |
| `static` | 14,324 | **14,325** |
| unrouted | 16,271 | **16,270** |

**Gained:** `conspiracy`, `dungeon`, `phenomenon`, `plane`, `scheme`, `vanguard`.
**Dropped:** `basic`, `legendary`, `snow`, `world` (CR 205.4a supertypes) and
`stickers` — the last being a **Scryfall type line that is not a CR card type**
at all (48 sticker-sheet cards print a bare `Stickers` type line). All five
verified inert: **zero** corpus lines use any of them as `this <word>`.

## 7. Verification

| gate | result |
|---|---|
| routing diff `--strict` | **0 lines moved**, 0 appeared, 0 vanished |
| determinism ×2 | **byte-identical** (`0f1a9c10…`) |
| name-invariance | **1** — the known Storm of Memories artifact, unchanged |
| Clue/investigate ground truth | **byte-identical** |
| `routed_lines` · `keyword_homes` | 61,907 · 150 **UNCHANGED** |
| lint | clean — 565 axes · 359 active · 8,740 members |
| family sweep | 6 blocking, the same 6 |
| definition drift | 35, unchanged |
| CR 205 parse | all three lists complete, content-guarded |

## 8. THE SWEEP — same shape, elsewhere (Captain's follow-on)

> *"look for similar situations, where a rule does not have scaffolding for the
> other card types. but also check the CR if those card types can be part of the
> rules."*

Both halves applied: every hard-coded card type in the classifiers, then the CR
asked whether the omitted types can participate. **Four candidates, two real.**

### 8a. CONFIRMED — the attachment vocabulary had two of its three members

The static-attachment branch read `^(enchant|equipped creature|enchanted )` —
Auras (CR 303.4) and Equipment (CR 301.5a) — and omitted Fortifications. The CR
does not leave this to inference; it states the analogy outright:

> **CR 301.6** — *"Some artifacts have the subtype 'Fortification.' A
> Fortification can be attached to a **land**. … **Rules 301.5a–f apply to
> Fortifications in relation to lands just as they apply to Equipment in
> relation to creatures**."*

So CR 301.5a's *"equipped creature"* has an exact CR-stated analog, *"fortified
land"*. **1 line** — Darksteel Garrison, *"Fortified land has indestructible"* —
fully unrouted. **FIXED**, routing to already-ratified `static` under its own
descriptor `static-fortification`, so §6a's printed-word census keeps reporting
the distinction rather than hiding it inside the Aura bucket.

### 8b. CONFIRMED, but it is VOCABULARY — the damage family covers 2 of CR 120.1's 4 recipients

> **CR 120.1** — *"Objects can deal damage to **battles, creatures,
> planeswalkers, and players**."*

§2's **recipient** side was ratified against that full enumeration on 2026-08-04
(`is-dealt-damage-trigger`, with `battle` reserved at 0). **The SOURCE side never
was.** Measured on trigger conditions:

| CR 120.1 recipient | source-side lines | ratified §2 token |
|---|--:|---|
| player | 762 | `combat-damage-to-player` · `any-damage-to-player` |
| creature | 59 | `combat-damage-to-creature` · `any-damage-to-creature` |
| **planeswalker** | **2** | **none** — Zagras, Thief of Heartbeats is unrouted |
| **battle** | **0** | **none** — reserved by the enumeration |

**NOT fixed — minting `combat-damage-to-planeswalker` is new vocabulary and
needs Captain's word.** On the decision sheet. The asymmetry is the finding: one
side of a family was enumerated from a closed CR list and the other was not.

### 8c. CHECKED AND CLEARED — "attacks a battle" (CR 506.3)

CR 506.3's closed enumeration is *"Only a player, a planeswalker, or a battle can
be attacked"*, and `is-attacked-trigger`'s regex names only player and
planeswalker. **Not a defect.** The 2 corpus lines (War-Trained Slasher,
Thrashing Frontliner) print *"Whenever this creature **attacks** a battle"* —
that is the **attacking** side, and both already route to `attack-trigger`
correctly. `is-attacked-trigger` is the defending side, whose `battle` slot §2
already documents as reserved-not-instantiated.

### 8d. CHECKED AND CLEARED — `\ba creature\b` in the §2a subject test

The `other` flag names one card type where CR 205.2a gives fifteen. Measured the
**exact** defect condition — `selfish` true, a non-creature card type named, and
the current test missing it: **5 lines, all correctly routed.** Three are
`cast-trigger`, which uses `mark()` and never consults the subject prefix; the
other two are unrouted for unrelated reasons. `other` is read only when
`selfish` is true, which is why the broader-looking gap (312 lines naming
`an instant` / `an artifact` / `a land`) never reaches it. **Gate 4 held: I
suspected the check, measured it, and the check was right.**

## 9. WHAT THIS PROVES

**A data source can be a hand-list wearing better clothes.** CLAUDE.md's rule is
*"if the CR enumerates it, parse the CR"*, and the failure it names is a curated
list. This was not curated — it was derived, from live corpus data, and it was
**still** incomplete, because the population it derived from is gated. The test
is not "did a human type this list", it is **"can the source contain every member
the CR names?"**

**A halt-guard must assert content, not cardinality.** Counting caught nothing
because the defect substituted rather than removed. Every guard in this codebase
that checks `len(...)` is now suspect by the same argument — the `least` counts
in `type_vocabulary` were the only ones found this pass, and they had been
passing green over a three-item loss the whole time.

**Zero lines moved and it was still worth doing.** Nothing in the routing diff
would ever have reported this; the six missing card types produce zero lines
because the corpus cannot hold them. That is the same shape as the standing
trap *"a ratified token with no emitter looks exactly like one with no
members"* — an absence that is indistinguishable from correctness until you ask
the CR instead of the data.
