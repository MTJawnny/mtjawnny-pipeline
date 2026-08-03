# Tier-3 decision packet — 2026-08-02

Re-audit of every active axis with exactly 3 members. **23 axes, 69
member-reads.** Evidence is full oracle text, all faces. Worklist:
`docs/REAUDIT-TIER-3-3-2026-08-02.md`.

Codebook at audit time `b89487b13925742b109f4cf9c2827c631c426742c97f9465616f9166e0f9649c`,
489 axes / 322 active. My recommendation is marked ✅ on each; where I think
the codebook is right and the card is wrong I say so, and where the axis is
wrong I say that too.

> ## EXECUTED 2026-08-02 — D1–D12 and M
>
> Captain-ratified 2026-08-02: **"D3f stands as written, general — execute
> D1-D12 and M."** D12 therefore executed as recommended (split), and D3f now
> binds every `activated-` axis in future tiers.
>
> | | before | after |
> |---|---|---|
> | codebook sha256 | `b89487b1…` | `c184e76e…` |
> | axes | 489 | 497 |
> | **active** | 322 | **328** |
> | members | 7,871 | 7,875 (−2 drops, +6 rename-tombstone copies) |
> | lint | clean | clean |
> | sweep blocking | 6 | **6** (same six, none new) |
> | drift findings | 27 | **25** (C2 17→16, C3 8→7) |
>
> Specs: `experiments/moves/2026-08-02-tier3-packet.json` +
> `-scope-followup.json`. Executor: `foundry_membership_move.py`.
> Backups: `backups/codebook.pre-tier3-packet.20260802-194532.json` and
> `…pre-tier3-scope-followup.20260802-194632.json`, both verified by readback
> (hash-identical **and** parsed deep-equal).
>
> **D5 delivered what it predicted**: the C2 finding on `rule:upkeep-surveil`
> and the C3 finding on `rule:etb-scry` are both **cleared**. `etb-scry`'s
> remaining C2 (Voyage's End, Falcon Joaquin Torres, Samut's Sprint, Coming In
> Hot — spells with no ETB) is the separate pre-existing delivery finding and
> was never in this packet's scope.
>
> **Two things the execution surfaced that the packet did not anticipate:**
>
> 1. **The executor had no way to edit a scope field.** D1's ratified scope
>    correction (`all-players` → `self`) had no spec key. Added `scope_edits`
>    to `foundry_membership_move.py`, mirroring `definition_edits` exactly and
>    deciding nothing — same precedent as the tier-1 session adding
>    `quote_edits`. It halts on a no-op edit, so a spec that disagrees with
>    live state fails loudly rather than silently passing.
> 2. **A rename carries the old scope forward.** D7's rename to
>    `rule:restricts-library-search` kept `scope: opponent-stuff` — the exact
>    claim D7 ruled false. Caught on post-execution readback, corrected to
>    `all-players` in the follow-up spec. **Generalizable defect: `renames`
>    accepts a `definition` override but not a `scope` one**, so any future
>    rename that broadens scope will carry the contradiction forward silently.
>    Worth fixing in the executor before the next tier.
>
> **New axis status.** All six new axes entered `active`, matching the tier-2
> packet's precedent (its four n=1 axes are all `active`). CDR-01 — which
> recommends n=1 → `deferred` — **is still unruled** and is carried forward
> in `CDR-PROPOSALS.md`; ruling it would retroactively touch five of these six.
>
> **Not executed, and not in scope of this ratification:** D13 (by-power
> family), D14 (A-Social Climber), §S (the 88 Alchemy memberships), and the
> §2 DELIVERY vocabulary gap D2 exposed (`combat-trigger` /
> `begin-combat-trigger`), which was flagged without a ✅ and remains open.

**Correction to the handoff before anything else.** `SESSION-HANDOFF-2026-08-02-PM.md`
§5 states tier 3 is "22 axes / 66 member-reads" and that `foundry_reaudit.py`
applies "the created-ability flag, the verbatim-quote check and the
repeatability test." Measured:

- Live generation returns **23 axes / 69 member-reads** — D3f's haste split
  landed a new axis in the 3-member band after that line was written.
- There is **no repeatability test in the tool.** `foundry_reaudit.py` has
  exactly three auto-flags: NO QUOTE, QUOTE NOT VERBATIM, CREATED-ABILITY
  RISK, plus injected drift findings. The D3f `{T}` test is a judgment test
  and was applied by hand here (D12). Nothing else in the run depended on it,
  but a future session should not expect the tool to catch that class.

---

## Summary

| | |
|---|--:|
| axes read | 23 |
| member-reads | 69 |
| axes with a finding | 14 |
| verified clean, no action | 7 |
| hard misfiles (member is on the wrong axis) | 3 |
| delivery splits needed (§1 unmarked-default) | 3 |
| unevidenced members (NO QUOTE) | 4 |
| new vocabulary needed for ratification | 3 |

**Defect rate: 14 of 23 axes (61%), 21 of 69 member-reads (30%).** Higher than
tier 2's 15% / 6%, and the reason is visible in the findings: at n=3 the axes
are old SYNTH-derived narrow patterns that accumulated a third member from a
later batch without anyone re-reading the definition. Nine of the fourteen are
the definition or the name having drifted away from the members, not a member
being wrong.

One systemic finding (§S) is not tier-3-specific and is the most consequential
thing in this document.

---

## D1 — `rule:cast-from-exile-trigger` / Mirror of Life Trapping — HARD MISFILE

**Definition:** "An ability that triggers specifically when the controller
casts a spell from exile."

**Cited quote, verbatim as filed:** *"Whenever a creature enters, if it was
cast, exile it"*

**Full oracle text:** "Whenever a creature enters, if it was cast, exile it,
then return all other permanent cards exiled with this artifact to the
battlefield under their owners' control."

The trigger **event** is a creature entering. "if it was cast" is an
intervening-if condition *about* casting, and the card never casts from exile —
it exiles *to* somewhere. Grammar §2 rules this class explicitly:

> `cast-trigger` — "requires cast verbiage; **the trigger EVENT must be the
> cast itself, not a condition about casting**" (b6 Village Ironsmith ruling).

The other two members are correct: Fire Lord Zuko ("Whenever you cast a spell
from exile…") and Kami of Celebration ("Whenever you cast a spell from exile,
put a +1/+1 counter on target creature you control").

**Second finding on the same axis:** scope reads `all-players`, but both
correct members are "**whenever you** cast" — controller-scoped. The scope
field is wrong independently of the misfile.

| option | consequence |
|---|---|
| ✅ **Remove Mirror of Life Trapping; ledger-flag it as homeless; correct scope `all-players` → `self`** | Axis becomes a clean 2-member controller-scoped cast-from-exile axis. Per D5 (remove-and-rehome) the honest answer here is "no home exists": Mirror of Life Trapping is an *other-permanent-ETB* exile-and-return replacement, and `etb` in §2 means the source itself entering. No current axis has that shape. |
| Author a new axis for it now | Would need new DELIVERY vocabulary for "another permanent enters" — a §10 rule 3 ratification on n=1 evidence. CDR-01 recommends n=1 → `deferred` anyway. |

*Related, already tracked:* Kami of Celebration is also a member of
`rule:etb-plus1-counter-on-other-creature`, where it is an **open C2 drift
finding**. It is correct here and wrong there — the two findings are
independent and this one does not touch it.

## D2 — `rule:combat-trigger-auto-attach-equipment` / Ria Ivor — HARD MISFILE

**Definition:** "At the start of combat, automatically attaches a target
Equipment the controller owns to this creature without paying the equip cost."

**Ria Ivor, Bane of Bladehold — the cited quote disproves its own axis:**

> *"At the beginning of combat on your turn, the next time target creature
> would deal combat damage to one or more players this combat, prevent that
> damage."*

Full text confirms: battle cry, plus a damage-prevention trigger that creates
Phyrexian Mite tokens. **Nothing about Equipment, nothing about attaching.**
Only the "at the beginning of combat" fragment matches. This is the Keen Sense
class exactly — a quote accurate about *the card* and irrelevant to *the axis*.

The other two members genuinely attach: Sokka, Swordmaster ("attach up to one
target Equipment you control to Sokka") and Blacksmith's Talent ("attach
target Equipment you control to up to one target creature you control").

**Second finding:** the definition says "to **this creature**". Blacksmith's
Talent is a **Class enchantment** — not a creature at all — and attaches to
*another* creature you control. The definition fits Sokka only. (Its level-2
ability is printed on the card, not created, so the created-ability rule does
not bite.)

| option | consequence |
|---|---|
| ✅ **Remove Ria Ivor; broaden the definition to "attaches an Equipment its controller controls to a creature (itself or another)"** | Axis becomes a coherent 2-member begin-combat auto-attach axis. Ria Ivor is a prevent-combat-damage-by-a-creature shape with a token rider; the closest family is `prevent-combat-damage-unblocked-creature`, but Ria Ivor has no unblocked restriction and a begin-combat delivery — **recommend ledger-flag, no forced rehome** (D5's third option, taken explicitly). |
| Keep Ria Ivor and rename the axis to something about begin-combat triggers | Would fuse two unrelated mechanics under one slug — grammar §1 design goal 2. |

**Vocabulary gap this exposes (needs ratification, §10 rule 3):**
`combat-trigger-` is **not in §2's closed DELIVERY vocabulary.** The list has
`upkeep-trigger`, `attack-trigger`, `landfall`, the damage families — but no
beginning-of-combat-step trigger. Three of this tier's cards use that trigger
shape. Proposed: `begin-combat-trigger` (CR 506.1/511), or ratify
`combat-trigger` as-is since it is already in live use on this slug.

## D3 — `rule:lifegain-scales-with-sacrificed-creature-toughness` — THREE DELIVERIES ON ONE UNMARKED SLUG

Grammar §1: DELIVERY is **omitted for spell abilities** — the unmarked slug
*is* the spell. This axis's three members have three different deliveries.

| member | text | delivery | fits the unmarked slug? |
|---|---|---|---|
| **Momentous Fall** | "As an additional cost to cast this spell, sacrifice a creature. You draw cards equal to the sacrificed creature's power, then you gain life equal to its toughness." | spell + additional cost (§9 ✓) | **yes — this is the axis** |
| **Miren, the Moaning Well** | "{3}, {T}, Sacrifice a creature: You gain life equal to the sacrificed creature's toughness." | **activated** (a land) | no — wants `activated-` |
| **Doomgape** | "At the beginning of your upkeep, sacrifice a creature. You gain life equal to that creature's toughness." | **upkeep trigger**, and the sacrifice is in **resolution text**, not a cost (§9) | no — wants `upkeep-trigger-` |

The definition ("…a creature that was sacrificed **to cast the spell**") is
accurate for Momentous Fall and false for the other two.

This is precisely the **D3d precedent** ratified this session on Snag /
Gossamer Chains: the unmarked slug belongs to the spell, and the activated
member is the one that moves.

| option | consequence |
|---|---|
| ✅ **Keep Momentous Fall on the unmarked slug; split Miren to `rule:activated-lifegain-scales-with-sacrificed-creature-toughness`; split Doomgape to `rule:upkeep-trigger-lifegain-scales-with-sacrificed-creature-toughness`** | Follows D3d exactly. Cost: two new axes at n=1 each — CDR-01 recommends n=1 → `deferred`, which applies here. |
| Broaden the definition to cover all three deliveries | Contradicts §1's unmarked-default rule and D3d's precedent one day after it was set. |

**Vocabulary gap (needs ratification):** `sacrificed-creature-toughness` is
**not in §7's closed stat vocabulary**, yet the slug is Captain-ratified — it
came from the walk's §2.2.1 D-3 rename table
(`-scaled-by-sacrificed-creature-toughness` → `-scales-with-…`). This is the
same gap F3 closed for `opponent-tapped-creature-count` and D3e closed for
`target-color-count`: a ratified rename target whose stat token was never
added to §7. ✅ **Recommend adding `sacrificed-creature-toughness` to §7.**

## D4 — `rule:attack-trigger-pump-scales-with-creature-count` / Akroan Hoplite — §7 STAT MISMATCH

| member | scaling stat as printed | §7 stat |
|---|---|---|
| Rinoa Heartilly | "for each creature you control" | `creature-count` ✓ |
| Life of the Party | "where X is the number of creatures you control" | `creature-count` ✓ |
| **Akroan Hoplite** | "where X is the number of **attacking** creatures you control" | **`attacker-count`** ✗ |

§7's closed stat vocabulary lists `creature-count` and `attacker-count` as
**two separate entries**. Akroan Hoplite scales with the attacker count; the
slug claims creature count. Same class as D3e (Breathe Your Last, board
color-count vs the target's own color-count), which you ratified today.

**Second finding — the definition over-specifies the object.** It reads
"grants a boost to **another target creature the controller controls**". Only
Rinoa does that. Life of the Party and Akroan Hoplite both pump **themselves**
("*it* gets +X/+0"). Two of three members contradict the definition.

| option | consequence |
|---|---|
| ✅ **(a) Split Akroan Hoplite to `rule:attack-trigger-self-pump-scales-with-attacker-count`; (b) rewrite the definition to drop "another target creature the controller controls"** | The stat split is the well-grounded half — §7 makes the two stats distinct vocabulary. The definition fix follows D3f's lesson that over-specified definitions manufacture false misfiles. Leaves n=2 (Rinoa + Life of the Party) and a new n=1 (`deferred` per CDR-01). |
| Treat attacker-count as a parameter of creature-count | Contradicts §7's own vocabulary, which enumerates both. |

## D5 — `rule:upkeep-surveil` / Faerie Dreamthief — CONFIRMED, and the rehome clears two open drift findings

This axis carries an **open C2 drift finding**, and the re-audit confirms it:

- Grave Researcher // Reanimate — "At the beginning of your upkeep, surveil 1." ✓ (front face; DFC read in full)
- Mindwhisker — "At the beginning of your upkeep, surveil 1." ✓
- **Faerie Dreamthief — "When this creature enters, surveil 1."** ✗ an ETB

**The valuable part is where it goes.** `rule:etb-surveil` **does not exist.**
The near-miss `rule:etb-creature-triggers-surveil` (n=2) is the wrong shape —
its definition is "Whenever **a creature** the controller controls enters…",
i.e. another creature entering, not the card itself.

And the same missing axis is the answer to **three of the eight open C3
findings**: `rule:etb-scry` currently holds Gallifrey Council Chamber, Lazav
the Multifarious and Watcher in the Mist, all of which **surveil** on their own
ETB, and all flagged by the drift audit as effect mismatches.

| option | consequence |
|---|---|
| ✅ **Ratify `rule:etb-surveil` with 4 quote-verified members: Faerie Dreamthief (from `upkeep-surveil`) + Gallifrey Council Chamber, Lazav, Watcher in the Mist (from `etb-scry`)** | One new axis at n=4 — well above the CDR-01 singleton threshold, so it enters `active`. Clears the whole C2 finding on `upkeep-surveil` **and** the whole C3 finding on `etb-scry`. The highest-leverage single item in this packet. |
| Move Faerie Dreamthief alone and leave the scry members | Leaves the C3 finding open and creates the axis at n=1 anyway. |

*Also queued, not executed:* `B-CONSOLIDATION-REAUDIT-PACKET.md:1348` carries a
pending member-addition of Aminatou, Veil Piercer to `upkeep-surveil`
("At the beginning of your upkeep, surveil 2") — genuinely an upkeep surveil,
and it would take the axis to n=3 after Faerie Dreamthief leaves.

## D6 — `rule:token-count-scales-with-graveyard-creature-count` / Hallowed Spiritkeeper — DELIVERY

Same §1 class as D3. The slug is unmarked, so it claims spell delivery.

- Revenge of the Rats — a sorcery ✓
- The Final Days — a sorcery ✓ (the flashback-from-graveyard clause is a condition, not a delivery)
- **Hallowed Spiritkeeper** — "When this creature **dies**, create X 1/1 white Spirit creature tokens with flying, where X is the number of creature cards in your graveyard." A **death trigger.**

The stat is right in all three (`graveyard-creature-count` is §7 vocabulary ✓).
Only the delivery is wrong.

✅ **Split Hallowed Spiritkeeper to
`rule:death-trigger-token-count-scales-with-graveyard-creature-count`.** Note
the codebook already carries `rule:death-trigger-token-scales-with-power`, so a
death-trigger token-scaling family exists and this is its sibling, not new
territory. Alternative: leave it and accept the unmarked slug as
delivery-agnostic — but that is the reading D3d rejected yesterday.

## D7 — `rule:restricts-opponent-search` — THE NAME MAKES A CLAIM 2 OF 3 MEMBERS CONTRADICT

| member | text | scope as printed |
|---|---|---|
| **Mindlock Orb** | "**Players** can't search libraries." | symmetric — binds you too |
| Ashiok, Dream Render | "Spells and abilities **your opponents** control can't cause their controller to search their library." | opponent ✓ |
| **Shadow of Doubt** | "**Players** can't search libraries this turn." | symmetric — binds you too |

§6 distinguishes `opponent` from `each`/`mass-` (non-targeted, all-covered).
The slug says `opponent`; two of three members are symmetric. This is the C1b
class — member evidence contradicts the name — and it is a real deck-building
distinction: a symmetric lock is a prison card you build around, an
opponent-only lock is a hoser you jam.

(Ashiok's ability is a **printed static**, not created by a loyalty ability, so
it is a correct member and the created-ability rule does not apply.)

| option | consequence |
|---|---|
| ✅ **Rename to `rule:restricts-library-search` + broaden the definition to "prevents or restricts library searching"; ledger the opponent-only reading as a facet, with Ashiok as its seed** | Matches the D1-inversion precedent from tier 2: when the name asserts something its members contradict, the name moves. Keeps all three members. |
| Split: symmetric pair stays under a new name, Ashiok gets `-opponent-` | Two axes at n=2 and n=1. Defensible, more churn. |

## D8 — `rule:death-of-your-permanents-grows-this-creature` — SAME CLASS AS D7

| member | text | "your permanents"? | counter |
|---|---|---|---|
| **Haruspex** | "Whenever **another creature** dies, put a +1/+1 counter on this creature." | **no — any creature** | plus1 |
| Necrosquito | "Whenever another creature or artifact **you control** is put into a graveyard from the battlefield, put an **oil** counter on this creature." | yes ✓ | **oil** |
| **Elenda, the Dusk Rose** | "Whenever **another creature** dies, put a +1/+1 counter on Elenda." | **no — any creature** | plus1 |

The slug says "death of **your** permanents"; two of three trigger on *any*
creature dying, including opponents'. C1b class again.

✅ **Broaden the name and definition to drop the ownership claim** (e.g.
`rule:other-creature-death-grows-this-creature`), or split ownership into
siblings. Recommend broadening: the majority reading is the unrestricted one.

**Flagged, NOT recommended for action:** the counter *type* is heterogeneous
(plus1 ×2, oil ×1) while the parallel family — `rule:self-plus1-counter-growth`,
`rule:attack-trigger-self-plus1-counter-growth`,
`rule:draw-trigger-self-plus1-counter-growth` — is typed, and §8 rule 1 requires
the noun sense to be typed. I am **not** proposing a typed rename here, for two
reasons: this slug contains no counter token at all, so §8a does not bite; and
batch-5's polarity-is-a-parameter ruling shows this project deliberately
declines to split axes on counter kind. Raising it as a rename is exactly the
move that would have destroyed `etb-with-negative-counters`. Recorded for the
schema pass, not proposed.

## D9 — `rule:leaves-battlefield-returns-exiled-card` / Wormfang Turtle — DESTINATION

**Definition:** "…a card it had exiled is returned to its owner's **hand**."

- Champion of the Weird — "return the exiled card to its owner's **hand**" ✓
- Aurelia's Vindicator — "return the exiled cards to their owners' **hands**" ✓
- **Wormfang Turtle** — "return the exiled card **to the battlefield** under its owner's control." ✗

Different destination, and §4 treats destination as verb-defining (`bounce` =
to hand vs `reanimate` = to battlefield).

| option | consequence |
|---|---|
| ✅ **Broaden the definition to "the exiled card is returned to its owner" and log destination as a facet** | All three do the identical *job* — a temporary exile undone when the permanent leaves — and the destination tracks where the card was exiled *from* (Wormfang Turtle exiles a land from the battlefield, so it returns there). Lowest churn, and the job is what the axis is for. |
| Split Wormfang Turtle to a `-to-battlefield` sibling | Honest under §4, but produces an n=1 axis over a difference that follows mechanically from the source zone. |

This is the closest call in the packet and I hold it loosely.

**Not a finding:** the `exiled` participle in the slug is **explicitly ruled
clean** — `CR-VOCABULARY-AUDIT.md` §2 verifies "`leaves-battlefield-returns-exiled-card`
uses the participle, which the ledger rules as zone-resident," with **0 renames**
for the `exile` homograph. Checked before writing.

## D10 — `rule:alt-win-empty-library` / Thassa's Oracle — DIFFERENT MECHANISM

**Definition:** "Wins (or replaces the loss) when **drawing** from an empty
library."

| member | text | mechanism | delivery |
|---|---|---|---|
| Jace, Wielder of Mysteries | "If you would draw a card while your library has no cards in it, you win the game instead." | draw-replacement ✓ | `replacement` (printed static, **not** the −8) |
| Laboratory Maniac | "If you would draw a card while your library has no cards in it, you win the game instead." | draw-replacement ✓ | `replacement` |
| **Thassa's Oracle** | "When this creature enters, look at the top X cards…, where X is your devotion to blue. …**If X is greater than or equal to the number of cards in your library, you win the game.**" | **library-size check on ETB — never mentions drawing** | **`etb`** |

Thassa's Oracle wins by comparing devotion to library size. It is the famous
empty-library win card in practice, but mechanically it neither draws nor
replaces a draw, and its delivery is an ETB trigger, not a replacement effect.

I checked Jace's full text specifically for the created-ability rule: the
win-replacement is a **printed static ability**, not made by the −8 loyalty
ability (which is a separate, additional win clause). Correct member.

| option | consequence |
|---|---|
| ✅ **Broaden the definition to "wins the game on an empty or effectively-empty library, whether by replacing the draw or by an explicit library-size check"** | Keeps the deck-building job intact — these three cards are literally the same combo slot. The axis is CAPTAIN-sourced and declared a child of `alternate-win-condition`, so job-level breadth is its stated intent. |
| Move Thassa's Oracle to `rule:alternate-win-condition` (n=16) | Mechanically purer, but loses the empty-library grouping that is the axis's whole point. |

**All three members are NO QUOTE** — see §M.

## D11 — `rule:draw-scales-with-creature-count` / Biomantic Mastery — THE DEFINITION IS THE DRIFTED ARTIFACT

**Definition:** "…draw a number of cards equal to the number of creatures
**they control** matching a filter."

- Winged Portent — "Draw a card for each creature **you control** [with flying]." ✓
- Camaraderie — "…draw X cards, where X is the number of creatures **you control**." ✓
- **Biomantic Mastery** — "Draw a card for each creature **target player** controls, then draw a card for each creature **another target player** controls." ✗

✅ **Fix the definition, not the membership.** The *slug* is unscoped, and the
codebook marks ownership when it means it — `rule:pump-scales-with-own-creature-count`
carries the `own-` marker explicitly. §6 says SCOPE is omitted until a
scope-sibling exists. So the unscoped slug legitimately spans both, and the
definition's "they control" is the thing that drifted. Alternative: split
Biomantic Mastery to an `-opponent-`/`-target-player-` sibling, which would then
force `-own-` onto this slug per §6's sibling rule.

## D12 — `rule:activated-exile-graveyard-creature-for-token` / Havengul Runebinder — THE D3f `{T}` TEST

Applied by hand; the tool does not check it.

| member | activated cost | capped at once per turn? |
|---|---|---|
| Fungal Plots | "{1}{G}, Exile a creature card from your graveyard:" | no — repeatable with mana |
| Graveyard Marshal | "{2}{B}, Exile a creature card from your graveyard:" | no — repeatable with mana |
| **Havengul Runebinder** | "{2}{U}, **{T}**, Exile a creature card from your graveyard:" | **yes** |

Grammar §2, ratified today: *"A `{T}` in an activated cost is AXIS IDENTITY…
Tapping caps an ability at once per turn; an otherwise-identical ability
without it goes arbitrarily wide with mana. That is a when/whether difference…
so the tapped and untapped forms are siblings, never one axis."*

The test applies cleanly: Fungal Plots and Graveyard Marshal are uncapped
graveyard-to-token engines; Havengul Runebinder is one token per turn. Same
when/whether split D3f ruled on.

**Honest caveat, and it matters.** Batch 6's override spot-check
(`docs/archive/TRIAGE-BATCH-6.md:305`) shows Havengul Runebinder with its **`{T}`
visible in the sampled quote**, marked **OK** — a Captain-reviewed pass. But
that review was 2026-07-30 and D3f was ratified **2026-08-02**. This is a new
law applied to an old approval, not a re-raising of a settled question. If you
read D3f as narrow to the haste case, this finding dissolves and the member
stays.

| option | consequence |
|---|---|
| ✅ **Split Havengul Runebinder to `rule:activated-tap-exile-graveyard-creature-for-token`** | Matches D3f's own naming precedent, `rule:activated-tap-grants-haste-other-creature-you-control`. n=1, so `deferred` per CDR-01. |
| Rule D3f narrow to the haste case; Havengul Runebinder stays | Also coherent — and worth stating explicitly either way, because D3f as written generalizes and will keep firing on every `activated-` axis re-audited from here. |

## D13 — `rule:evasion-vs-high-power-blockers` vs the ratified `cant-be-blocked-<restriction>` grammar

The three members are all genuine by-power blocking restrictions:

- Kithkin Armor — "Enchanted creature can't be blocked by creatures with power 3 or greater."
- April O'Neil, Kunoichi Trainee — "…can't be blocked by creatures with power 3 or greater."
- **Tadeas, Juniper Ascendant** — "…it can't be blocked by creatures with **greater power** this combat" — relative to the attacker, not a fixed threshold. A third shape; the definition says "a specified threshold."

**The finding is the name, and it connects to a blocking sweep item.** Q8
(walk-ratification, 2026-07-31) ratified the grammar
`cant-be-blocked-<restriction>` with closed restriction vocabulary
`by-color`, `by-power`, `except-by-count`, `as-long-as-<state>`, `by-controller`.
Its siblings already conform: `rule:cant-be-blocked-by-color` (n=19, DET) and
`rule:cant-be-blocked-by-controller` (n=2, DET). These two do not:
`rule:evasion-vs-high-power-blockers` (n=3) and
`rule:evasion-vs-low-power-blockers` (n=4).

Meanwhile the family sweep carries **`ratified-pattern-has-no-axis:
rule:cant-be-blocked-by-power` as one of its six BLOCKING findings**, and
ADD-01 (Captain-ruled 2026-08-01) says the by-power axis gets its axis via the
DET path with **57 measured corpus hits**. So the codebook holds 7 by-power
members under a non-conforming name while a blocking gate says the axis does
not exist.

**This is a MERGE question, not a rename** — and that is why I am not
recommending execution:

| option | consequence |
|---|---|
| ✅ **Rule it, do not execute it here.** Recommend: extend the §2.4.5 closed restriction vocabulary with `by-power-at-least` / `by-power-at-most`, rename the two axes onto them, and route Tadeas's relative-power shape to a third value or to the ledger | Preserves the high/low distinction (a real difference — evading small blockers vs evading big ones are opposite deck slots) while conforming to Q8. Clears one of the six blocking sweep findings. |
| Merge both into a single `rule:cant-be-blocked-by-power` | Conforms to the vocabulary as literally ratified, matches the single DET pattern's 57 hits — but collapses two opposite mechanics into one axis, which grammar §1 design goal 2 exists to prevent. |

Either way this **interacts with ADD-01's session-4 DET plan**, which expects
to create the by-power axis fresh. Executing here without ruling that
interaction would produce a collision. Batches 5, 6 and 7 all recorded KEEP on
these two axes, but every one of those predates Q8 (2026-07-31) and ADD-01
(2026-08-01).

## D14 — `rule:gains-life-on-other-creature-etb` / A-Social Climber — ALCHEMY VARIANT

The member is the **Alchemy rebalanced** row. CLAUDE.md: *"Paper rows preferred
over A- (Alchemy) variants in sampling, resolution, and emit."*

| row | oracle_id | text |
|---|---|---|
| **A-Social Climber** (member) | `0d5a023f-c968-4cf7-9875-fefbde082fc0` | "Alliance — Whenever another creature enters under your control, you gain 1 life." |
| Social Climber (paper) | `70af9a03-20d6-44e3-a181-b60e80bff643` | "Alliance — Whenever another creature you control enters, you gain 1 life." |

Functionally identical, templating differs. ✅ **Swap to the paper row.**
The other two members (Lifecreed Duo, Distinguished Conjurer) are correct.

**This one card opened the systemic finding below.**

---

## S — SYSTEMIC: 88 Alchemy-variant memberships, every one with a paper twin

Not tier-3-specific. Measured across all 322 active axes:

| | count |
|---|--:|
| A- variant memberships on active axes | **88** |
| …for which a paper twin exists in the corpus | **88 (100%)** |
| …where the **paper twin is already a member of the same axis** | **48** |
| …where oracle text is byte-identical after name normalization | 2 |
| …where oracle text differs (genuine rebalance or templating change) | 86 |

Two distinct problems inside that number:

1. **48 memberships are duplicate rows for one card.** Both `A-X` and `X` sit
   on the same axis. Under "`oracle_id` is the only card key" they are distinct
   records, so no gate catches it — but they are one card counted twice, and
   they inflate the member counts of 48 axes. This is a **measurement defect**,
   and it is the high-confidence subset.
2. **40 memberships are A--only** — the paper row is absent and the Alchemy row
   stands in for it, against the stated house preference.

**Why this needs a ruling rather than a script.** Gate #0 (batch-6 D1) keeps
these cards deliberately: *"Alchemy-only and format-narrow cards still pass
(they are legal somewhere)."* So this is **not** an exclusion question — it is
the paper-preference rule, which has never been mechanically enforced. And 86
of 88 have non-identical text, so a blind swap is unsafe: an Alchemy rebalance
can change the numbers or the effect the membership rests on. **Every
substitution must be quote-verified per card**, exactly like D5's
remove-and-rehome discipline.

✅ **Recommendation, in this order:**
1. Rule whether the paper-preference binds codebook membership at all, or only
   display/sampling. Everything below depends on it.
2. If it binds: drop the **48 duplicate A- rows** first — no judgment needed,
   the paper row is already there carrying its own evidence.
3. For the **40 A--only rows**, a per-card verified swap: paper row in, A- row
   out, quote re-verified against the paper text, halting on any card where the
   rebalance changed the mechanic the membership rests on.
4. Add the check to the standing gate suite, so it cannot silently regrow.

Full 88-row inventory is reproducible from the codebook and corpus; I have not
written it to a doc pending your ruling on step 1.

---

## M — Mechanical: 4 unevidenced members (no new vocabulary; executable on your word)

All `legacy-captain-seed`, all verified correct against full oracle text.

| axis | card | proposed quote |
|---|---|---|
| `alt-win-empty-library` | Jace, Wielder of Mysteries | "If you would draw a card while your library has no cards in it, you win the game instead." |
| `alt-win-empty-library` | Laboratory Maniac | "If you would draw a card while your library has no cards in it, you win the game instead." |
| `alt-win-empty-library` | Thassa's Oracle | "If X is greater than or equal to the number of cards in your library, you win the game." — **quote is accurate but see D10**; do not land it until D10 is ruled, or it will evidence a definition it contradicts |
| `targets-a-player` | Time Warp | "Target player takes an extra turn after this one." |

---

## Verified correct — no action (7 axes, 21 member-reads)

- **`rule:activated-tap-or-untap-any-creature`** — Puppeteer, Stonybrook Angler, Puppet Strings, all "{cost}, {T}: You may tap or untap target creature." Internally consistent. The name carries no `activated-tap-` cost marker, but **all three members are tapped-form and no untapped sibling exists**, so D3f does not bite; §12 already ledgers this family for the `activated-(un)tap[-or-untap]-<scope>-<class>` lattice consolidation (b6 D3). Not re-raised.
- **`rule:buff-scales-with-land-type-count`** — Lashwrithe, Nightmare Lash, Staff of Titania. `land-type-count` is §7 vocabulary ✓.
- **`rule:channel-discard-for-effect`** — Eiganjo, Takenuma, Ghost-Lit Warder. All Channel, discard on the **cost** side of the colon (§9 ✓). The definition calls Channel an "alternative cost" where CR makes it an activated ability from hand — imprecise but not load-bearing. (`B-CONSOLIDATION-REAUDIT-PACKET.md:1623` has Colossal Skyturtle queued for this axis.)
- **`rule:death-trigger-mass-debuff`** — Death's-Head Buzzard, Havoc Demon, Plague Dogs. Clean: `death-trigger` (D-1) + `mass-` (§6) + `debuff` (§4).
- **`rule:etb-with-negative-counters`** — Leech Bonder, Bristlebane Battler, Morselhoarder, all "enters with N -1/-1 counters" ✓. §8a satisfied by the `with`-binding. **Its existence is already ruled** (batch-5 ordered MERGE; batches 6 and 7 KEPT it; the 2026-08-01 Captain ruling cleared the stale `merged_into` and declared it live) and the CDR-09 walk record explicitly says renaming it to `minus1-` would encode the distinction batch-5 rejected. **Not re-raised.**
- **`rule:leaves-battlefield-trigger-create-token-creature`** — Thragtusk, Grixis Slavedriver, Chittering Dispatcher. All "When this creature leaves the battlefield, create a [creature] token." This also **confirms tier-2 D3c landed correctly** — Chittering Dispatcher was moved here yesterday and reads clean.
- **`rule:prevents-target-blocking`** — Untimely Malfunction, Renegade Tactics, Stun. All "target creature(s) can't block this turn" ✓. Checked against `rule:cannot-block-restriction` (n=21) for the design-goal-1 duplication class: **not duplicates** — that axis is a permanent statically forbidden from blocking *itself*; this one is a spell stopping *a target*. Different mechanics.

**Minor, recorded not proposed:**
- `rule:aura-locks-enchanted-creature-tapped` — all three correct, but the definition names only the narrow form ("doesn't untap during its controller's untap step"), while 2 of 3 print the stronger absolute ("can't become untapped"). Definition-precision item.
- `rule:targets-a-player` — Inquisitor Exarch's is an ETB modal choice on an unmarked (spell) slug. The axis's own Captain-written definition declares it a "layered generic tag, expected rank-only, low priority", so §1's delivery-marking rule looks deliberately waived here. Flagged, not proposed.

---

## Cost summary if every ✅ is ratified

| decision | new axes | renames | merges | member moves | definition edits | vocab |
|---|--:|--:|--:|--:|--:|--:|
| D1 Mirror of Life Trapping | 0 | 0 | 0 | 1 (drop) | 0 (+scope fix) | 0 |
| D2 Ria Ivor | 0 | 0 | 0 | 1 (drop) | 1 | 1 (delivery) |
| D3 lifegain/sac-toughness | 2 | 0 | 0 | 2 | 1 | 1 (§7 stat) |
| D4 Akroan Hoplite | 1 | 0 | 0 | 1 | 1 | 0 |
| D5 etb-surveil | 1 | 0 | 0 | 4 | 0 | 0 |
| D6 Hallowed Spiritkeeper | 1 | 0 | 0 | 1 | 0 | 0 |
| D7 restricts-opponent-search | 0 | 1 | 0 | 0 | 1 | 0 |
| D8 death-of-your-permanents | 0 | 1 | 0 | 0 | 1 | 0 |
| D9 Wormfang Turtle | 0 | 0 | 0 | 0 | 1 | 0 |
| D10 Thassa's Oracle | 0 | 0 | 0 | 0 | 1 | 0 |
| D11 Biomantic Mastery | 0 | 0 | 0 | 0 | 1 | 0 |
| D12 Havengul Runebinder | 1 | 0 | 0 | 1 | 0 | 0 |
| D13 by-power family | 0 | 2 | 0 | 0 | 0 | 2 (restriction vocab) |
| D14 A-Social Climber | 0 | 0 | 0 | 1 (swap) | 0 | 0 |
| M quotes | 0 | 0 | 0 | 0 | 0 (4 quotes) | 0 |
| **total** | **6** | **4** | **0** | **12** | **8** | **4** |

Plus §S, which is its own decision and much larger than the rest combined.

One `foundry_membership_move.py` spec covers D1–D12 and M under the usual
gates: timestamped backup with readback, member conservation derived from the
declared ops, determinism ×2, and lint + sweep + registry + drift either side.
**D13 and §S should not ride that spec** — D13 collides with ADD-01's
session-4 plan, and §S needs its own ruling before any row moves.

## What I'd flag as the judgment calls, not the bookkeeping

- **§S is the real finding.** Everything else in this packet is 20-odd cards.
  §S is 88 memberships across 48 axes with inflated member counts, and no gate
  in the system looks for it. It surfaced from one card in one 3-member axis.
- **D12 tests how wide D3f is.** As written in grammar §2, D3f generalizes to
  every `activated-` axis, and it will keep firing as the re-audit descends
  through the larger tiers. Ruling it narrow-to-haste now is cheaper than
  ruling it twenty axes from now.
- **D13 is where a ratified grammar and a blocking gate disagree with live
  state**, and the fix is a merge-or-extend vocabulary call, not a rename.
- **Six of the fourteen findings are the definition being wrong, not the
  member** (D4b, D8, D9, D10, D11, and half of D2). That ratio is the same
  signal tier 2's D3f/D4 raised: over-specified definitions written at
  n=1 manufacture false misfiles once a second and third member arrive.
