# SAGA CHAPTER TRIGGERS — RULING (2026-08-03)

Fourth ruling in the 2026-08-03 shape series, at Captain's direction: *"take the
saga chapter triggers next. again reference CR for reference."*

**576 ability lines across 221 cards** — the largest named gap left in the
delivery census after today's ratifications. Every claim below is quoted from
the local CR, not recalled.

**Zero API calls.**

---

## 1. GATE 3 — this family was already ruled, and the ruling was a KILL

`rule:saga-chapter-progression` is in the codebook right now as
`status: killed, n=0`. `TRIAGE-BATCH-1.md` §1c killed it by name:

> ### 1c. Procedural riders and templating boilerplate (7)
> - **saga-chapter-progression** (saga reminder text, DF 138 — layout fact)

**The kill is UPHELD, and the CR gives a better reason than batch-1 had.**
Batch-1 called the progression a "layout fact". The CR is stronger than that:

> **CR 714.3c** — *"As a player's precombat main phase begins, that player puts
> a lore counter on each Saga they control with one or more chapter abilities.
> **This turn-based action doesn't use the stack.**"*

A turn-based action is **not an ability at all** (CR 117.3a governs priority;
turn-based actions happen automatically). So there is nothing to give a DELIVERY
slot to. Batch-1 reached the right verdict from the card layout; the CR reaches
it from the rules.

**But that kill does not touch what this ruling proposes.** The *progression* is
a turn-based action. The *chapter abilities* are something else entirely, and
the CR says so in the very next rule. Same structure as the `end-step-trigger`
case ruled earlier today: a killed **axis** does not bar the **vocabulary**.

---

## 2. What the CR says a chapter ability IS

> **CR 714.2** — *"A chapter symbol is a **keyword ability** that represents a
> **triggered ability** referred to as a **chapter ability**."*

Two consequences land immediately:

1. **It is a keyword ability**, so **§2b applies** — ratified hours ago: a CR
   702-style keyword's delivery is derived from the CR's own statement of it,
   never ruled per keyword. The CR states the class outright: **triggered**.
2. **"Chapter ability" is the CR's own term of art**, which under §6a is
   hardcoded to its mechanic and is axis identity — not a facet, and not a
   project coinage like `mass-` was.

And the CR gives the full templated text:

> **CR 714.2b** — *"'{rN}—[Effect]' means '**When one or more lore counters are
> put onto this Saga, if the number of lore counters on it was less than N and
> became at least N**, [effect].'"*

So the trigger EVENT is *lore counters being put onto the Saga* — a
counter-placement trigger with a threshold gate.

---

## 3. RULING — one token proposed

| token | lines | cards | CR |
|---|--:|--:|---|
| **`chapter-trigger`** | **576** | **221** | 714.2, 714.2b |

**Coverage is total: 221 of 221 Saga cards in the corpus are caught**, verified
card by card rather than sampled.

### 3a. The chapter NUMBER is a parameter, not axis identity

Recommended, with the honest counter-argument stated.

Every chapter ability is the *same trigger event* — lore counters placed —
differing only in the threshold N inside an intervening-if (714.2b). That is
the batch-5 counter-polarity precedent exactly: +1/+1 and −1/−1 counters do
*opposite* things and were still ruled a parameter.

The counter-argument is the final chapter, which looks special because the Saga
goes away after it. **It isn't special, and the CR is explicit about why:**

> **CR 714.4** — *"If the number of lore counters on a Saga permanent … is
> greater than or equal to its final chapter number … that Saga's controller
> sacrifices it. **This state-based action** …"*

The sacrifice is a **state-based action**, not part of any chapter ability. So
the final chapter ability is mechanically an ordinary chapter ability; nothing
in it differs. N stays a parameter.

**Standing reversal condition**, stated so a later session need not re-derive
it: CR 714.2e defines "**final chapter ability**" as a named thing. The moment
one card *keys off* that term — "when this Saga's final chapter ability
resolves" — the final chapter earns its own vocabulary. The finding is about the
current corpus.

### 3b. `-conditional` should NOT be marked, even though every member qualifies

§6 ratifies `-conditional` for "an intervening-if or 'unless' gate on the same
ability", and 714.2b means **every chapter ability has one by definition**.

Marking it would put `-conditional` on 100% of members. **A qualifier true of
every member of a family carries no information** and only lengthens the slug —
it distinguishes nothing. Recommend leaving it unmarked, and recording the
reason here so the omission does not read as an oversight to a conformance
checker.

---

## 4. CLASS CARDS NEED NOTHING — and the extractor's descriptor was lying

The gap census called this shape `saga-or-class-chapter`. **Measured: all 576
lines are Sagas, and ZERO are Classes.** The name implied a fused family that
does not exist.

The CR keeps them apart cleanly:

> **CR 716.2** — *"A class level bar is a keyword ability that represents both
> an **activated** ability and a **static** ability."*
>
> **CR 716.2a** — *"'[Cost]: Level N — [Abilities]' means '[Cost]: This Class's
> level becomes N. Activate only if this Class is level N-1 and only as a
> sorcery' and 'As long as this Class is level N or greater, it has
> [abilities].'"*

A Saga chapter is **triggered**; a Class level bar is **activated + static**.
Different ability classes, so §2b routes them to different slots — and the
activated slot already exists.

**Verified in the corpus: 38 Class cards, 76 level lines, and every one of them
is already routed to `activated`** by the cost-colon branch, which is exactly
right per 716.2a. Class needs **no new vocabulary**.

Descriptor renamed to `saga-chapter` in
`experiments/foundry_shape_extractor.py`, with the measurement recorded at the
site. A fused descriptor invites a fused axis later.

---

## 5. Not authored — delivery-only slugs are parents

Per the cycling ruling §5 and batch-5 D16, a delivery-only slug is a **parent**;
its children are `chapter-trigger-<effect>`. The 576 lines carry a very wide
effect spread, so authoring those is a corpus pass, not this ruling.

**Parent candidate, logged not authored:** `rule:saga-payoff` — the job being
*"this permanent pays me out on a schedule and then leaves."* Under S4a it is
unranked against whatever else the card is.

---

## 6. What this leaves

With `chapter-trigger` ratified, the remaining named gaps in the delivery
census, in order:

| shape | cards |
|---|--:|
| `unclassified-trigger` (residual, genuinely unnamed) | 1,000 |
| begin-combat | 331 |
| sacrifice-trigger | 180 |
| player-attacks ("whenever you attack") | 158 |
| discard-trigger | 111 |
| turned-face-up | 116 |
| damage-received ("is dealt N damage") | 108 |

`begin-combat` is the next single-token target and was already carried as an
open item on the batch's §8 list.
