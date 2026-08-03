# Tier-4 — decision sheet

> ## STATUS after Captain's verdicts, 2026-08-02
>
> | call | verdict | state |
> |---|---|---|
> | 1 | default | **EXECUTED** |
> | 2 | default | **EXECUTED** |
> | 3b, 3d | (unaddressed by the "no", read as standing) | **EXECUTED** |
> | 3a | **OVERRULED** — ownership is axis identity, not a facet | **HELD** — needs a new axis name + a scope answer |
> | 3c | tied to 4c | **HELD** |
> | 4 | new axis for each; Rammas Echor also earns a draw axis | **HELD** — 6 new names await ratification |
> | 5 | default | **EXECUTED** |
> | 6 | default — the rule binds DET | **HELD** — generator change, own pass |
>
> Executed via `experiments/moves/2026-08-02-tier4-part1.json`.
> codebook `c184e76e…` → `5db28942…` · 497 axes · 328 active · 7,875 → 7,871
> members · lint clean · sweep 6 blocking (unchanged) · **drift 25 → 22, and
> C1a is now zero**. Backup `codebook.pre-tier4-part1.20260802-214234.json`,
> verified by readback.
>
> **Two things need you before the rest can move — see §7 at the bottom.**

**6 calls.** Evidence for every line is in
`docs/TIER-4-DECISION-PACKET-2026-08-02.md` (same E-numbers).

To ratify everything as recommended: **"all defaults."**
To vary: **"all defaults except 4 — do X."**
Mark a line by writing `VERDICT: ...` under it; annotations here are
authoritative.

---

## 1. Move 5 members that are on the wrong axis, to an axis that already exists

No new names, no new vocabulary. Pure bookkeeping.

| card | from | to |
|---|---|---|
| Dwarven Landslide | `alt-cost-sacrifice-lands` | `additional-cost-sacrifice-permanent` |
| Gravity Negator | `attack-trigger-pump-any-creature` | `temporary-keyword-grant` |
| Brokers Charm | `etb-destroy-target-enchantment` | `targeted-destruction` |
| Opal-Eye, Konda's Yojimbo | `prevents-damage-to-self` | `prevent-fixed-damage-any-target` |
| Inviolability | `prevents-damage-to-self` | `prevent-damage-to-your-creatures` |

Why they don't belong: a kicker is an *additional* cost, not an alternative
one · granting flying is a keyword grant, not a pump · Brokers Charm is an
instant, not an ETB · Opal-Eye's prevention is activated and fixed-amount, not
static-and-all · Inviolability is an Aura protecting another creature, not
itself.

**DEFAULT: yes, move all five.**

VERDICT: default

---

## 2. Drop 4 members that belong nowhere, and ledger them

Each is genuinely on the wrong axis and no existing axis fits. Under the
remove-and-rehome rule (b6 D5) the honest answer is "no home" rather than a
forced fit.

| card | from | why nothing fits |
|---|---|---|
| Familiar Beeble Mascot | `attack-trigger-untap-attacker` | untaps *any permanent*, not the attacker |
| Arius, Flyby Trawler | `delayed-destroy-trigger` | *discards*, never destroys |
| Research // Development | `tutor-from-outside-game-to-hand` | goes to *library*, not hand |
| Solitary Confinement | `prevents-damage-to-self` | protects the *player*, not the permanent |

**DEFAULT: yes, drop and ledger all four.**
(Alternative for any of them: author a 1-member axis instead. I don't
recommend it — CDR-01 would park them as `deferred` anyway.)

VERDICT: default

---

## 3. Correct 4 definitions that contradict their own members

The members are fine; the definition text is wrong.

| axis | the false claim | corrected to |
|---|---|---|
| `attack-trigger-pump-any-creature` | "not restricted to the controller's own creatures" — but 2 of 4 are own-restricted | drop the clause; ownership becomes a facet |
| `prevents-damage-to-self` | "static … all damage" | narrows to what survives after call 1 |
| `token-count-scales-with-x` | "by an enters-the-battlefield ability" — 3 of 4 are spells | unmarked = spell (§1) |
| `draw-second-card-trigger-plus1-counter` | "producing a creature token" — stale since batch-5 D12 renamed it | +1/+1 counter |

Call 3a for `attack-trigger-pump-any-creature` is **already ratified
precedent** — batch-6 D3 ruled this exact clause on its sibling axis and
ordered it dropped. This just applies it.

**DEFAULT: yes, correct all four.**

VERDICT:no any creature means any creature. ownership is critically important for game logic. remove own restricted members from `attack-trigger-pump-any-creature` and create new axis for them.

---

## 4. Four new axis names (this is the only call that creates vocabulary)

| # | proposed slug | takes | needs fresh ratification? |
|---|---|---|---|
| 4a | `draw-second-card-trigger-create-token-creature` | Thopter Fabricator | **No** — batch-5 D12 ledgered this scheme |
| 4b | `cast-second-spell-trigger-create-token-creature` | Rammas Echor | **No** — same, D12's "mirrored family … when it arises" |
| 4c | `etb-token-count-scales-with-x` | Farmer Cotton | No — standard delivery split |
| 4d | `doubles-triggered-abilities-conditional` | Echoes of Eternity | **Yes** — new name in the `doubles-<thing>` family |

4a and 4b are the interesting ones: they need no new ruling because grammar
§11 says a ratified grammar instantiates the moment a quote-verified member
arrives. This is that mechanism firing for the first time.

Also in this call: **Codespell Cleric → `etb-plus1-counter-on-other-creature`**
(existing axis). Weak link, flagged honestly — its text says "target creature",
which doesn't exclude itself, while the destination says "other". Say no and
I'll ledger it instead.

**DEFAULT: yes to 4a–4d and Codespell Cleric.**

VERDICT: make new axis for each one. Rammas echor should also have `cast-second-spell-trigger-draw` or whatever ruling fits

---

## 5. Two evidence quotes (mechanical)

Aven Cloudchaser on `etb-destroy-target-enchantment`, Forth Eorlingas! on
`token-count-scales-with-x`. Both verified correct, both just missing their
quote. No judgment involved.

**DEFAULT: yes.**

VERDICT: default

---

## 6. §S4 — the one that matters

**44 DET memberships were written off text belonging to tokens the card
creates, not to the card.**

Tireless Provisioner is filed as producing mana and gaining life. It does
neither — it makes Food and Treasure tokens, and the *tokens'* reminder text
says "You gain 3 life" and "Add one mana". 37 more cards sit on
"activate only as a sorcery" because a **Map token** they create says so, and
they have no activated ability at all.

Root cause is known and is a pattern bug, not a judgment error: the F2 walk fix
widened these patterns to paragraph scope, and reminder text lives on the same
line.

This is grammar §2's created-ability rule — *"a card does not deliver an
ability it creates … or a token's printed text"* — which you ratified today
against SYNTH misfiles. It has never been applied to DET patterns.

**The call: does the created-ability rule bind DET patterns too?**

- **Yes (recommended)** → fix the pattern preprocessor to strip token-definition
  reminder text before matching, re-run, and the 44 fall out. Must *preserve*
  keyword reminder text (Unearth, Encore, Cycling) or it destroys ~110 correct
  memberships — that boundary is measured and is why the number is 44 and not
  154.
- **No** → the 44 stay, and DET keeps writing full-weight `rule-derived`
  provenance off token text.

I recommend yes, and separately recommend the fix land in the **producer**, not
the data (G4: generated artifacts get generator fixes).

**DEFAULT: yes — rule that it binds, fix the preprocessor.**

VERDICT:default

---

### If you say "all defaults"

4–6 new axes · 10–12 member moves · 6 drops · 4 definition edits · 2 quotes ·
one preprocessor fix + re-run. Calls 1–5 ride one declared spec under the usual
gates. Call 6 gets its own pass, because it changes a generator and needs its
own before/after diff.

---

## 7. What your verdicts opened — two things I will not guess

### 7a. Call 3a is an explicit partial reversal of batch-6 D3. How far does it reach?

You ruled: *"any creature means any creature. ownership is critically important
for game logic."* Batch-6 D3 ruled the opposite, on a sibling axis, by name:

> `rule:etb-pump-target-creature`: drop the "not restricted to the controller's
> own creatures" definition clause … **ownership-scope logged as a facet
> dimension for the schema pass.**

So this is a reversal, and per the grammar's own discipline it gets logged as
one rather than applied quietly. **Measured blast radius — 6 active axes hold
BOTH own-restricted and unrestricted members under an `any-*` scope:**

| axis | own-restricted | n | in tier 4? |
|---|--:|--:|---|
| `copy-creature-token` | 7 | 21 | no |
| `sets-base-power-or-toughness` | 1 | 19 | no |
| `attack-trigger-pump-any-creature` | 2 | 4 | **yes — your ruling** |
| `attack-trigger-untap-attacker` | 1 (Tadeas) | 4 | yes, called CLEAN |
| `etb-pump-target-creature` | 1 (Herald of the Fair) | 4 | yes, called CLEAN |
| `activated-untap-another-permanent` | 1 | 2 | no |

**The call:** narrow (just `attack-trigger-pump-any-creature`, now) or general
(all 6, and batch-6 D3 is reversed on the record)?

I lean **general** — your reasoning was about game logic, not about one axis,
and leaving the other five is the "one law encoded, others ignored" shape that
produced every drift this project has had. But it reverses a ratified directive
and turns two axes I certified clean into defects, so it is yours.

Note either way: after 3a executes, `attack-trigger-pump-any-creature` is left
holding **Mayhem Patrol alone** (n=1).

### 7b. Six new slug strings, derived from ratified grammar — confirm or correct

You authorised the axes ("make new axis for each one"); these are the strings I
derive from §1 slot order and the ratified vocabularies. New vocabulary is a
ratification, so I am not writing them until you say.

| for | proposed slug | derivation |
|---|---|---|
| Thopter Fabricator | `rule:draw-second-card-trigger-create-token-creature` | D12 prefix scheme × D14 `create-token-<type>` |
| Rammas Echor (token half) | `rule:cast-second-spell-trigger-create-token-creature` | D12's mirrored family, instantiating per §11 |
| **Rammas Echor (draw half)** | `rule:cast-second-spell-trigger-draw` | your addition; §4 verb `draw`. It earns BOTH under §1 multi-axis |
| Farmer Cotton | `rule:etb-token-count-scales-with-x` | standard delivery split (D3d precedent) |
| Echoes of Eternity | `rule:doubles-triggered-abilities-conditional` | `doubles-<thing>` family, batch-1 ledger |
| Codespell Cleric | `rule:etb-plus1-counter-on-target-creature-conditional` | §1 order + §6 `-conditional` for the "if it was the second spell" intervening-if |
| own-restricted attack pumps | `rule:attack-trigger-pump-own-creature` | §6 `own`; takes Yotian Frontliner + Hazardroot Herbalist |

**Two sub-questions inside that table:**

1. **Codespell Cleric's name is the weakest.** Its gate is specifically "the
   second spell you cast this turn", which `-conditional` records but does not
   name. Alternative: `rule:etb-plus1-counter-on-second-spell-cast`. Yours.
2. **Does "another" split from "you control"?** Yotian Frontliner reads
   "**another** target creature you control"; Hazardroot Herbalist reads
   "target creature you control" and can hit itself. By the same logic that
   makes ownership load-bearing, self-inclusion may be too — it is the
   distinction D3f's `-other-creature-you-control` naming already encodes
   elsewhere. I have put both on one axis; say the word and it becomes two.
