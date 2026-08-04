# IN-CARD SEPARATION — IS THE TEXT AFTER THE SEPARATOR READ? (2026-08-06)

Captain, 2026-08-06:

> *"Double check that other modal bullet points are not stopping the rest of the
> card from being read. Reference the CR. I want modal spells and abilities
> checked for game significant effects."*
> *"…and spaceships, and classes, and level ups. Basically anything that has
> in-card separation."*

**Every construct that divides a card's text box, measured against its own CR
rule.** Four were stopping. Three are fixed; two remain, one of which needs
Captain's word because it needs vocabulary.

---

## 1. The CR says the same sentence three times

This is the unifying rule, and it is worth seeing together:

| rule | *"…is a keyword ability that represents a …"* | *"Any abilities printed within the same text box striation…"* |
|---|---|---|
| **CR 711.2** level symbol | **static** ability | *"…are part of its static ability."* |
| **CR 721.2** station symbol | **static** ability | *"…are part of its static ability."* |
| **CR 716.2** class level bar | **activated *and* static** ability | *"…are part of its static ability."* |

And twice more, verbatim in both places:

> **CR 711.3 / 721.3** — *"The text box striations have **no game significance
> other than clearly demarcating** which abilities and which power/toughness
> box are associated with which symbol."*

**So a separator is scaffolding — like a flavor word — but unlike a flavor word
the symbol itself is an ability, and the CR names its class outright.** No new
vocabulary was needed for any of this; `static` is already ratified and is what
these rules say.

## 2. The census

| construct | CR | lines | unrouted **before** | **after** | verdict |
|---|---|--:|--:|--:|---|
| Saga chapter `III —` | 714.2 | 576 | **0%** | 0% | ✔ was always correct |
| **Planeswalker loyalty** `+1:` `−X:` | 606.2 | **909** | **0%** | 0% | ✔ **was always correct** |
| Class level bar `{3}{U}: Level 2` | 716.2 | 76 | **0%** | 0% | ✔ a cost and a colon — the activated branch had it right |
| **Leveler** `LEVEL 1-2` | 711.2 | 50 | **100%** | **0%** | **fixed** |
| **Station** `9+ \| Flying, first strike` | 721.2 | 49 | **86%** | **20%** | **fixed** |
| **Pawprint mode** `{P} —` | 700.2i | 15 | 100% | 100% | **fixed as a MODE** (see §4) |
| Modal bullet `• …` | 700.2 | 1,791 | 71% | **66%** | fixed (`c2bd5d9`), remainder explained |
| Die-roll row `1—9 \| …` | 706.3b | 101 | **98%** | 98% | **open — §5** |
| Attraction `Visit —` | 702.159a | 23 | **100%** | 100% | **open — needs vocabulary, §6** |
| `{TK} —` sticker cost | — | 192 | 88% | 88% | **not a separator at all — §7** |

### Planeswalkers, specifically

You asked. **909 loyalty lines, every one routed to `loyalty`, zero unrouted.**
`LOYALTY_COST` reads the printed symbol as the cost (CR 606.2: *"an activated
ability with a loyalty symbol in its cost is a loyalty ability"*), and it
handles all three printed signs — `+1:`, `−X:` with the CR's U+2212 minus, and a
bare `0:`. Nothing is stopping there.

## 3. What was fixed, and the trap it re-taught

**Leveler** — a bare `LEVEL 1-2` IS the ability (CR 711.2a: *"as long as this
creature has at least N1 level counters … it has base power and toughness [P/T]
and has [abilities]"*), so it is `static` on its own.

**Station** — the symbol prints its striation's abilities on the *same* line, so
the marker is **stripped** and the content classifies itself.

Claiming the whole station line as `static` — my first attempt — cost **7
re-routes**:

```
12+ | {3}{W}, {T}: Create a token that's a copy of …    activated -> static  ✗
2+  | {1}, {T}, Sacrifice a land: Draw two cards. …     activated -> static  ✗
```

Those are **activated** abilities inside a static striation. Calling the line
static is the standing **`Max speed — [Ability]` trap**: *matching the wrapper
overwrites the inner ability's correct delivery.* Stripping instead preserved
all 7 **and** let striation-internal triggers reach their own branches.

**82 gap lines closed, zero re-routes.**

## 4. Pawprint modes — fixed as MODES, and 100% is the right number

> **CR 700.2i** — *"Some modal spells have one or more **pawprint symbols
> ({P}) rather than bullet points**, as well as an instruction to choose up to a
> specified number of {P} 'worth of modes.'"*

Testing only for `•` made all 15 invisible as modes. Both consumers now share
`foundry_common.is_mode_line`, so the extractor and the ratified DET
preprocessing standard cannot drift apart — the D8 semicolon lesson. DET
modal-bullet expansions went **1,755 → 1,770**.

**They are still 100% unrouted, and that is correct.** Season of Loss is a
*sorcery*: its header reaches `spell-or-static` by CR 113.3a, and a mode
inherits its header's delivery. Inheriting "no ratified token" is the right
answer, not a stoppage. The same explains **1,011 of the 1,189** remaining
unrouted bullets, and the spree modes in §5.

**This is why "unrouted" is not "stopped."** A census that reports only the
unrouted rate would call three of these constructs broken. The test is whether
the delivery is *reachable*, not whether it is *ratified*.

## 5. Still open — no vocabulary needed, just a pass

**CR 706.3b die-roll rows — 101 lines, 98% unrouted.**

> *"An instruction to roll one or more dice, any instructions to modify that
> roll printed in the same paragraph, any additional instructions based on the
> result of the roll, and the associated results table are **all part of one
> ability**."*

So the rows are **not separate abilities** — they belong to the roll ability,
exactly as a mode belongs to its header. Earth-Cult Elemental's `1—9 | Each
player sacrifices…` should inherit the delivery of `At the beginning of combat
on your turn, roll two six-sided dice…`. Same mechanism as D3 inheritance,
same rule shape, no new vocabulary. **Next pass.**

**CR 700.2h spree modes — 51 lines, 100% unrouted.** *"Some modal spells have
one or more modes with a cost listed before the effect of that mode."* These are
modes, and their header is a modal **spell**, so inheritance would route them to
`spell-or-static` — no routing gain, but it would make them visible to the DET
modal expansion, which is worth having. Lower priority than the die rows.

Worth noting *why* spree's header is invisible: the choose instruction lives in
**reminder text** (`Spree (Choose one or more additional costs.)`), and §6a
strips reminder text, leaving a bare `Spree`. That is a §6a-vs-CR-700.2 tension
and it is the one place in this census where a ratified rule hides a CR fact.

## 6. BLOCKED ON CAPTAIN — Attractions need vocabulary

**CR 702.159a Visit — 23 lines, 100% unrouted.** The CR gives the template
outright:

> *"'**Visit — [Effect]**' means '**Whenever you roll to visit your
> Attractions**, if the result is equal to a number that is lit up on this
> Attraction, [effect].'"* — and **702.159b** puts `Prize —` inside that same
> visit ability.

So `Visit — Draw a card.` **is a triggered ability** with a CR-stated trigger
condition, and the project already knows this: `linked_abilities` returns early
on `visit`/`prize` citing exactly this rule (the b7 Pick-a-Beeble ruling). But
there is **no ratified §2 token** for "whenever you roll to visit your
Attractions", so the line has nowhere to land.

**This is a ratification, not a typo fix.** One row, one decision sheet entry.
`visit` is also among the 43 CR 702 keywords with no `KEYWORD_HOME` entry, so
ratifying the token closes both at once.

## 7. A correction against my own probe

**192 `{TK} — …` lines are not station striations.** I pattern-matched `{TK}`
as a station symbol and it is the **Unfinity ticket symbol** — sets `unf` /
`sunf`, type line `Stickers`, e.g. `{TK}{TK} — 1/5`. Real station lines are the
49 that print `N+ |`.

Second time this session a probe of mine found a correlation rather than a fact
(the first was the `non-ASCII` class re-measuring the em-dash). **The pattern is
that a shape test looks like a measurement.** Both times the fix was the same
question the system map ends with: *where does this come from, and can that
source contain what I think it contains?*

## 8. Verdict

**Nothing is being lost.** The conservation audit is still at 0 violations
across all three tests, before and after every change today. What was happening
was narrower and more specific: **four separators were not being read past**,
and in every case the CR named both the separator's class and what followed it.

| | |
|---|--:|
| gap lines closed today, all passes | **29 + 22 + 58 + 82 = 191** |
| re-routes | **1**, an improvement (Rankle and Torbran, §2d) |
| regressions | **0** |
| lines appeared / vanished | **0 / 0** |
| codebook | **untouched** — 565 axes, 8,740 members, lint clean |
