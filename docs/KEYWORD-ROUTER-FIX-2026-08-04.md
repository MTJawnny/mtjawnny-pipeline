# §2b KEYWORD ROUTER — FIXED (2026-08-04)

Step 1 of `SPELL-OR-STATIC-AUDIT-2026-08-04.md` §6, which the 2026-08-04 handoff
§8a lists as the next work item. **No new vocabulary, no ratification required,
no codebook mutation** — §2b already ratified the rule this implements
(*"route a CR 702 keyword to the §2 token its `702.Na` text resolves to"*).
Zero API calls.

**Result: 824 ability lines across 820 cards moved to a correct DELIVERY token.
The audit predicted 757; the extra 67 are one defect the audit did not find and
seven landwalk variants it did not count.**

---

## 1. ROOT CAUSE — the templated text was deciding the SLOT, not just the token

The audit deliberately refused to guess at this. Read, it is one sentence of §2b
being implemented backwards.

> **§2b, verbatim:** *"A keyword's CLASS and its TRIGGER EVENT are separate
> questions. **The class says which slot; the templated text says which token in
> that slot.**"*

`find_home` never read the class. It ran the CR's templated text through
`parse_delivery` and took whatever came back — so the text was deciding both.
That failed in **two opposite directions**, and the second one was invisible.

### 1a. Six keywords DROPPED — the CR prints a placeholder where a card prints a cost

> **CR 702.6a** — *"Equip is an activated ability of Equipment cards. **"Equip
> [cost]" means "[Cost]: Attach this permanent to target creature you control.
> Activate only as a sorcery."**"*

`parse_delivery`'s activated branch requires a recognisable cost left of the
colon — `{mana}`, or one of sacrifice / discard / pay / tap / exile / remove.
The CR's literal `[Cost]` placeholder is none of those, so the head matched
nothing and Equip fell through to `spell-or-static`.

**Cycling routed only by accident.** Its templated text is *"[Cost], **Discard**
this card: Draw a card"* — the word "Discard" happens to sit left of the colon
and is on the verb list. Every keyword whose cost half is the bare placeholder
was lost:

| lost | CR | verified verbatim | lines |
|---|---|---|--:|
| **Equip** | **702.6a** | *"Equip is an activated ability of Equipment cards."* | **567** |
| Ninjutsu | 702.49a | *"Ninjutsu is an activated ability that functions only while the card … is in a player's hand."* | 44 |
| Level Up | 702.87a | *"Level up is an activated ability."* | 25 |
| Fortify | **702.67a** | *"Fortify is an activated ability of Fortification cards."* | 2 |
| Aura Swap | 702.65a | *"Aura swap is an activated ability of some Aura cards."* | 1 |
| Forecast | **702.57a** | *"A forecast ability is an activated ability that can be activated only from a player's hand."* | 0 |

**639 lines — exactly the audit's number.** Forecast contributes 0 because it
prints as `Forecast — [ability]`, never bare.

**Two CR citations in the audit were wrong and are corrected above.** 702.66 is
**Delve** and 702.56 is **Replicate**; Fortify is 702.67a and Forecast is
702.57a. Read from the CR file this session, not recalled.

### 1b. Unearth was MISROUTED — the audit did not find this one

> **CR 702.84a** — *"**Unearth is an activated ability** that functions while the
> card with unearth is in a graveyard. "Unearth [cost]" means "[Cost]: Return
> this card from your graveyard to the battlefield. It gains haste. Exile it at
> the beginning of the next end step. **If it would leave the battlefield, exile
> it instead** of putting it anywhere else. Activate only as a sorcery.""*

`[Cost]` failed the activated branch as above, so the parse walked on and hit
*"would … instead"* — CR 614.1a's replacement template — and returned
`replacement`. **57 lines on 57 cards were filed as replacement effects.**

§2's own created-ability rule already forbade that: *"a card does not deliver an
ability it CREATES."* The activated ability is what creates the replacement
effect; the delivery belongs to the creator. This is the same principle §2d used
to retire `delayed` from DELIVERY, applied to a keyword.

**This is why the audit's step 1 was worth doing before the bigger step 2.** A
keyword sitting on a *wrong* ratified token is strictly worse than one sitting
in `spell-or-static`, because it is not a gap — nothing reports it.

### 1c. Landwalk — CR 702.14's heading is the one name no card prints

> **CR 702.14a** — *"Landwalk is a generic term that appears within an object's
> rules text as **"[type]walk,"** where [type] is usually a land type, but it can
> also be the card type land plus any combination of land types, card types,
> and/or supertypes."*

`landwalk` was in the keyword map (→ `static`, via **CR 702.14b** *"Landwalk is
an evasion ability"* and the existing CR 509.1b rollup). Every name a card
actually prints was absent.

The audit listed the five basic variants. **CR 702.14a states a grammar, not a
list**, and 702.14c's own examples span three further shapes — *"artifact
landwalk"*, *"nonbasic landwalk"*, *"snow swampwalk"*. So it is derived, from
**CR 205.3i** (17 land types), **205.2a** (15 card types) and **205.4a** (5
supertypes), all parsed at run time with a halt-guard — never enumerated.

| printed | lines |
|---|--:|
| swampwalk · islandwalk · forestwalk · mountainwalk · plainswalk | **120** |
| desertwalk | 2 |
| snow forestwalk · snow swampwalk · snow landwalk · legendary landwalk · nonbasic landwalk | 5 |
| **first strike** (Mirri, Cat Warrior — *"First strike, forestwalk, vigilance"*) | 1 |

**128, not 118.** The audit counted only the five basics, and only as isolated
tokens. Mirri is the multi-keyword case: the whole line was unroutable because
one of its three tokens was, and fixing forestwalk released the line.

**The matcher is strict on purpose.** A naive "ends in `walk`" test claims 31
extra lines that are not keyword lines at all — Quagmire's *"Creatures with
swampwalk can be blocked as though they didn't have swampwalk"*, Volcanic
Strength's *"Enchanted creature gets +2/+2 and has mountainwalk"*, and
`planeswalk` (CR 205.2a's card type is `plane`, not `planes`). All 31 are
correctly rejected.

---

## 2. THE FIX — narrow on purpose, and Gate 4 is why

The obvious generalisation is *"the CR-stated class always decides the slot."*
**That would have destroyed 16 ratified routings.**

`static` keywords whose templated text is a CR 614 replacement — Amplify,
Bloodthirst, Dredge, Madness, Modular, Riot, Tribute and nine more — are routed
to `replacement` by §2b's own ratified table. The CR **chains** those two rules
rather than opposing them:

> **CR 113.3d** — *"Static abilities are written as statements … **Static
> abilities create continuous effects**."*
> **CR 614.1** — *"**Some continuous effects are replacement effects.**"*

So `replacement` is the *more specific* reading of a static keyword, not a
contradiction of it. The check that would have "fixed" all 16 was the wrong one.

**Ruled, therefore, only for the `activated` class**, where CR 113.3b defines the
shape outright (*"Activated abilities have a cost and an effect. They are written
as '[Cost]: [Effect]'"*) and no more specific token exists: **a keyword the CR
states as `activated` and nothing else routes to `activated`, and its templated
text is not consulted.** Every other class is untouched.

Measured: **zero keywords are multi-class with `activated` among the classes**,
so nothing ambiguous rides on this.

| file | change |
|---|---|
| `foundry_cr702_classes.py` | `find_home` reads the CR-stated class first; new `effective_classes` helper (the rollup was duplicated in three places); new `type_vocabulary()` parsing CR 205.2a/3i/4a with a halt-guard |
| `foundry_shape_extractor.py` | `build_landwalk_template` + `landwalk_variant` implement CR 702.14a; `keyword_line_tokens` accepts a variant; halt-guard added — **the map must contain Equip → `activated`**, since §2b quotes CR 702.6a as its worked example |

---

## 3. MEASURED — every moved line read, before/after

Line-by-line snapshot of all 61,858 routed lines, before and after, diffed:
**824 moved, 820 cards, 117 distinct printed lines.** Nothing else moved.

| from | to | lines |
|---|---|--:|
| `spell-or-static` | `activated` (equip 567 · ninjutsu 44 · level up 25 · fortify 2 · aura swap 1) | **639** |
| `replacement` | `activated` (unearth) | **57** |
| `spell-or-static` | `static` (landwalk variants + Mirri's first strike) | **128** |

| | before | after |
|---|--:|--:|
| routed ability lines | 61,858 | 61,858 *(unchanged — no line gained or lost a delivery)* |
| KEYWORD_HOME entries | 138 | **144** |
| `spell-or-static` total | 20,559 | **19,792** |
| …on **permanents** | 9,942 | **9,178** |

**Only seven keyword homes changed** — the six added and Unearth corrected.
Verified by diffing the whole map, not by inspection.

**Gate 2 after: unchanged in every direction.** lint clean · 565 axes / 359
active / 8,740 members · family sweep 6 blocking, the same 6 · definition drift
35, same partition. **No codebook mutation, so no backup was required.**

**Determinism ×2 byte-identical** on the full 61,858-line snapshot
(`8490140432bc7dc8…`).

**Ground truth: the Clue set did not move, and this time that is provable rather
than reassuring.** No `investigate` line appears anywhere in the 824-line diff.
Fifth consecutive session in which it validated only the shapes it contains —
it holds no Equipment, no landwalk creature and no bare-keyword-with-cost line.

---

## 4. FOUND WHILE MEASURING — reported, not fixed

1. **Semicolon-joined keyword lines are still lost. 29 lines.**
   `keyword_line_tokens` splits on commas only, so *"Flying; banding"*,
   *"Defender; reach"*, *"Trample; rampage"* are not keyword lines. Same defect
   class as this one, and a two-character fix — held back so the 824-line diff
   above stays exactly attributable. **Do it as its own measured step.**
2. **The audit's instant/sorcery partition is contaminated by Adventure.**
   Three Equipment//Adventure cards — Ghost Lantern, Two-Handed Axe, Horn of
   Valhalla — carry `Instant`/`Sorcery` in the type line, so their equip lines
   counted as *"CORRECT — §1's unmarked default"* while being permanent-side
   defects. Small (3 of 10,617) but it means **that partition is a lower bound
   on the defect population, not an exact split.** A DFC-aware cut should use
   the face the ability line sits on.
3. **`spell-or-static` on permanents is still 9,178 lines** — step 2 of the
   audit, unchanged in character by this fix.

---

## 5. WHAT THIS SESSION PROVES

**The audit's refusal to guess was correct, and cheap.** The cause was not the
six keywords being absent from a list; it was one sentence of §2b implemented
backwards, and the same defect had *silently misrouted a seventh keyword onto a
ratified token* where no gap census could ever report it. A guessed fix — adding
six names to a list — would have left Unearth wrong forever.

**Gate 4 held again, this time before the code was written.** The clean
generalisation ("the class always decides the slot") disagreed with §2b's
ratified 16-keyword `replacement` table. The ratified list was right and the
generalisation was wrong; the CR chain 113.3d → 614.1 is why. **Second time in
two sessions that the tidier rule was the wrong rule.**

**Deriving beat listing, again.** CR 702.14a states landwalk as a grammar over
CR 205's type lists. Deriving it caught `desertwalk`, `snow landwalk`,
`legendary landwalk`, `nonbasic landwalk` and `snow swampwalk` — ten lines the
five-name list would have left in the sink, and it will catch the next printed
variant with no code change.
