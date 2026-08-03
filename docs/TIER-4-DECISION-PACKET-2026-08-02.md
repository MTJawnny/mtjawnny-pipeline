# Tier-4 decision packet — 2026-08-02

Re-audit of every active axis with exactly 4 members. **20 axes, 80
member-reads.** Full oracle text, all faces; every slug grepped across `docs/`
and `docs/archive/` before being called defective. Worklist:
`docs/REAUDIT-TIER-4-4-2026-08-02.md`.

Codebook `c184e76eb2109535114647545ee6e2ba7c79964e5ccd41a829bbb9f83d376e18`,
497 axes / 328 active. **Nothing below is executed.** ✅ marks my
recommendation.

## Summary

| | |
|---|--:|
| axes read | 20 |
| member-reads | 80 |
| axes with a finding | 12 |
| verified clean, no action | 8 |
| hard misfiles (member is on the wrong axis) | 7 |
| unevidenced members (NO QUOTE) | 2 |

**Defect rate: 12 of 20 axes (60%), 15 of 80 member-reads (19%).** Axis rate
holds at tier 3's level; the per-member rate fell (30% → 19%), which fits — a
4-member axis has more evidence holding its definition honest.

Three tier-4 axes came back **clean specifically because of yesterday's and
today's work**: `etb-surveil` (created today, all 4 verified),
`conditional-attack-restriction-by-defending-player-land-type` (tier-2 D2's
merge, all 4 identical text), and `etb-pump-target-creature` (batch-6 D3's
dropped ownership clause is holding at n=4). The re-audit is confirming its
own prior passes.

§S4 is the systemic finding and is not tier-4-specific.

---

## E1 — `rule:alt-cost-sacrifice-lands` / Dwarven Landslide — ALTERNATIVE vs ADDITIONAL cost

**Definition:** "The spell may be cast by sacrificing a specified number of
lands **instead of paying its normal mana cost**."

| member | text | cost type |
|---|---|---|
| Crash | "You may sacrifice a Mountain **rather than pay** this spell's mana cost." | alternative ✓ |
| Fireblast | "You may sacrifice two Mountains **rather than pay** this spell's mana cost." | alternative ✓ |
| Pulverize | "You may sacrifice two Mountains **rather than pay** this spell's mana cost." | alternative ✓ |
| **Dwarven Landslide** | "Kicker—{2}{R}, Sacrifice a land. (You may pay {2}{R} and sacrifice a land **in addition to** any other costs…)" | **additional** ✗ |

Kicker is an *additional* cost (CR 601.2b) — the exact opposite of the axis's
claim, and grammar §9's cost-vs-effect law makes the distinction hard. §2 also
lists `kicker` as its own DELIVERY value.

✅ **Move Dwarven Landslide to `rule:additional-cost-sacrifice-permanent`**
(n=19, definition "Requires the caster to sacrifice a permanent of a specified
type as an additional cost to cast the spell" — a verbatim fit). Clean rehome,
no new vocabulary. Dwarven Landslide is already correctly on
`rule:targeted-destruction` for its effect; this is its cost facet.

## E2 — `rule:attack-trigger-pump-any-creature` / Gravity Negator — EFFECT MISFILE

**Gravity Negator:** "Whenever this creature attacks, you may pay {C}. If you
do, another target creature **gains flying** until end of turn."

That is a **keyword grant**, not a pump. §4 lists `pump` (+P/+T) and
`grants-<keyword>` as different EFFECT verbs.

✅ **Move to `rule:temporary-keyword-grant`** (n=40). This is not a judgment
call: batch-4 D4 is a **standing rule** — "any `grants-temporary-<keyword>`
candidate (any keyword, not just hexproof) folds into
`rule:temporary-keyword-grant` on sight."

**Second finding — the definition clause has a ratified precedent.** It reads
"…**not restricted to the controller's own creatures** or the attackers", but
Yotian Frontliner ("another target creature **you control**") and Hazardroot
Herbalist ("target creature **you control**") are both own-restricted. Only
Mayhem Patrol matches as written.

Batch-6 D3 ruled this exact clause on the sibling axis: *"`rule:etb-pump-target-creature`:
**drop the 'not restricted to the controller's own creatures' definition
clause**; keep [both members]; scope field reads any-creature (widest member);
ownership-scope logged as a facet dimension for the schema pass."*

✅ **Apply batch-6 D3's precedent verbatim** — drop the clause, keep all
members, scope stays `any-creature`, ownership to the schema-pass facet ledger.

**Sub-finding, flagged not proposed:** Hazardroot Herbalist reads "Whenever
**you attack**", not "whenever ~ attacks" — an attack-with-creatures trigger,
a different event from §2's `attack-trigger`. Sparring Regimen (E3) has the
same shape. Two cards is thin evidence for new DELIVERY vocabulary; recorded
for the schema pass.

## E3 — `rule:attack-trigger-untap-attacker` / Familiar Beeble Mascot — OBJECT MISMATCH

**Definition:** "…untap a **target attacking creature**."

- Sparring Regimen — "put a +1/+1 counter on target attacking creature **and untap it**" ✓
- Genji Glove — "Whenever equipped creature attacks … **untap it**" ✓
- Tadeas, Juniper Ascendant — "Whenever a creature you control with reach attacks, **untap it**" ✓
- **Familiar Beeble Mascot** — "Whenever this creature attacks, untap **target permanent**." ✗

Untaps *any permanent*, not the attacker — the axis's whole claim. Scope field
already reads `any-permanent`, which is itself evidence the definition and the
scope disagree.

| option | consequence |
|---|---|
| ✅ **Move Familiar Beeble Mascot to `rule:activated-tap-or-untap-any-permanent`?** — no: that axis is *activated*, this is an attack trigger. **Recommend: drop it and ledger-flag as homeless** (D5's third option) | No axis has "attack-trigger untaps any permanent". Authoring one at n=1 on this evidence is thin. |
| Broaden the definition to "untap a target permanent" | Makes the axis name (`-untap-attacker`) false for 1 of 4 rather than the definition false — moves the contradiction rather than fixing it. |

Gate #0 checked: Familiar Beeble Mascot passes legitimately (legal in
commander/paupercommander/tlr), so this is not a legality question.

## E4 — `rule:delayed-destroy-trigger` / Arius, Flyby Trawler — CONFIRMS THE OPEN C3

Carries an open C3 drift finding; the re-audit confirms it.

- Mogg Cannon — "**Destroy** that creature at the beginning of the next end step." ✓
- Blood Frenzy — "**Destroy** that creature at the beginning of the next end step." ✓
- Arcum's Whistle — "at the beginning of the next end step, **destroy** it if it didn't attack this turn" ✓
- **Arius, Flyby Trawler** — "**Discard** that card at the beginning of the next end step." ✗

The delayed-trigger shape is right; the effect verb is wrong (§4).

✅ **Drop and ledger-flag.** Checked every discard axis: `targeted-discard`
(forces a *target player* to discard), `additional-cost-discard-a-card`,
`activated-cost-discard-a-card`, `reveal-hand-then-choose-discard` — none is a
delayed self-discard. `rule:delayed-cantrip` and `rule:delayed-draw-next-upkeep`
show the `delayed-<effect>` family exists, so `rule:delayed-discard` is
grammar-composable, but at n=1 CDR-01 would defer it anyway.

## E5 — `rule:doubles-etb-triggers` / Echoes of Eternity — WRONG BREADTH

**Definition:** "Causes **enter-the-battlefield** triggered abilities … to
trigger an additional time."

| member | text | ETB-specific? |
|---|---|---|
| Elesh Norn, Mother of Machines | "If **a permanent entering** causes a triggered ability of a permanent you control to trigger…" | ✓ |
| Panharmonicon | "If **an artifact or creature entering** causes…" | ✓ |
| Yarok, the Desecrated | "If **a permanent entering** causes…" | ✓ |
| **Echoes of Eternity** | "If **a triggered ability of a colorless spell you control or another colorless permanent you control triggers**, that ability triggers an additional time." | **✗ — every trigger, not just ETB** |

Echoes of Eternity doubles *all* triggered abilities of colorless permanents —
attack triggers, death triggers, upkeep triggers. Filing it as an ETB-doubler
understates it and makes the axis false for the deck-building question it
answers.

✅ **New axis `rule:doubles-triggered-abilities-conditional`** — "A static
ability causes triggered abilities matching a stated filter (not restricted to
enters-the-battlefield triggers) to trigger an additional time." The
`doubles-<thing>` family is a batch-1 ledgered parent candidate and already has
four live siblings (`doubles-etb-triggers`, `doubles-any-counter-placement`,
`doubles-token-creation`, `doubles-room-ability-triggers`), so this is family
extension, not new territory. n=1 → CDR-01 would defer.

## E6 — `rule:draw-second-card-trigger-plus1-counter` — THE 2×2, AND D12 ALREADY RATIFIED THE FIX

Carries **three** open drift findings (C1a, C1b, C2) — the most-flagged axis in
the codebook. CDR-09's walk record §4.1 documented it and left it as out of
scope. Tier 4 is where it surfaces for ruling.

| member | delivery | payoff | on the right axis? |
|---|---|---|---|
| **Lat-Nam Adept** | draw-second ✓ | +1/+1 counter ✓ | **yes — this is the axis** |
| Codespell Cleric | **etb** (with a cast-second intervening-if) | counter ✓ | no |
| Rammas Echor, Ancient Shield | **cast-second** | **token** | no |
| Thopter Fabricator | draw-second ✓ | **token** | no |

The definition still reads "producing a **creature token** as a reward" —
stale from before batch-5 D12 renamed the axis `-token` → `-plus1-counter`
for Lat-Nam Adept. That staleness *is* the C1a finding.

**The fix does not need new ratification.** Batch-5 D12 ledgered the full
scheme: *"the full prefix scheme is logged — unprefixed = 'you draw' … parent
`rule:draw-second-card-trigger` over all of them; mirrored
`rule:cast-second-spell-trigger` family with the same prefixes when it
arises."* Grammar §11 then made instantiation automatic: *"A virtual node
instantiates the moment one quote-verified member arrives — no fresh
ratification (the grammar was ratified)."*

✅ **Instantiate the ratified grammar and correct the stale definition:**

| card | destination | basis |
|---|---|---|
| Lat-Nam Adept | **stays** | the slug's own card |
| Thopter Fabricator | `rule:draw-second-card-trigger-create-token-creature` | D12 scheme, `create-token-<type>` per D14 |
| Rammas Echor | `rule:cast-second-spell-trigger-create-token-creature` | D12's mirrored family, "arises" now |
| Codespell Cleric | `rule:etb-plus1-counter-on-other-creature` (n=42) | trigger EVENT is the ETB; "if it was the second spell" is an intervening-if — the same reading tier-3 D1 applied to Mirror of Life Trapping |

**One caveat on Codespell Cleric**, stated because it is the weak link: its
text is "put a +1/+1 counter on **target creature**", which does not exclude
itself, while the destination axis says "on **other** creature". If you read
that as binding, it needs a different home and I would ledger it instead.

## E7 — `rule:etb-destroy-target-enchantment` / Brokers Charm — CONFIRMS THE OPEN C2

- War Priest of Thune — "When this creature enters, you may destroy target enchantment." ✓
- Wispmare — "When this creature enters, destroy target enchantment." ✓
- Aven Cloudchaser — **NO QUOTE**; text "When this creature enters, destroy target enchantment." ✓ correct, unevidenced
- **Brokers Charm** — "Destroy target enchantment." — an **instant**, modal, no ETB ✗

✅ **Move Brokers Charm to `rule:targeted-destruction`** (n=171, explicitly
"parameterized by type … artifact-or-enchantment"). It is already correctly
multi-axis on `modal`, `burst-draw` and `combat-trick-pump-own-creature` for
its other two modes — so this completes its §1 modal decomposition rather than
stranding it. ✅ **Quote Aven Cloudchaser** (see §M).

## E8 — `rule:landfall-produces-mana` + `rule:landfall-gain-life` / Tireless Provisioner — REMINDER TEXT

**Tireless Provisioner:** "Landfall — Whenever a land you control enters,
create a Food token or a Treasure token. (Food is an artifact with "{2}, {T},
Sacrifice this token: **You gain 3 life**." Treasure is an artifact with "{T},
Sacrifice this token: **Add one mana** of any color.")"

The card produces **no mana** and gains **no life**. It creates tokens. Both
matched strings live in the **token definitions' reminder text** — abilities of
the *tokens*, not of Tireless Provisioner. Grammar §2's created-ability rule,
ratified today, is exactly on point: *"a card does not deliver an ability it
CREATES — via an emblem, a delayed trigger, a granted ability, or **a token's
printed text**."*

Both memberships are `class=rule-derived`, `source_ref=det-patterns-v2:34`
and `:35` — DET, not model error. Root cause below in §S4.

✅ **Drop both memberships.** Rehome: Tireless Provisioner genuinely creates
Food and Treasure tokens, so under §1 multi-axis it belongs on
`rule:create-token-treasure` (n=43) and a Food sibling — but its delivery is
`landfall`, and no `landfall-create-token-<type>` axis exists. The
`<trigger>-create-token-<type>` grammar **is ratified** (batch-5 D10, extended
b6 D3), so under §11 it self-instantiates on this quote-verified member.
Recommend `rule:landfall-create-token-treasure` + `rule:landfall-create-token-food`,
or the simpler `rule:create-token-treasure` membership if you would rather not
open the landfall branch.

## E9 — `rule:prevents-damage-to-self` — 3 OF 4 DEVIATE

**Definition:** "The permanent has a **static** effect that prevents **all**
damage that would otherwise be dealt **to it**."

| member | text | deviation |
|---|---|---|
| Frodo, Determined Hero | "**During your turn**, prevent all damage that would be dealt to Frodo." | conditional, not unconditional — closest fit |
| **Inviolability** | "Prevent all damage that would be dealt to **enchanted creature**." | an Aura protecting **another** permanent, not itself |
| **Solitary Confinement** | "Prevent all damage that would be dealt to **you**." | protects the **player**, not the permanent |
| **Opal-Eye, Konda's Yojimbo** | "{1}{W}: Prevent the **next 1** damage that would be dealt to Opal-Eye this turn." | **activated**, and fixed-amount, not static/all |

Three different failure modes on one 4-member axis. Only Frodo is arguably in
scope, and even that is turn-conditional.

| option | consequence |
|---|---|
| ✅ **Keep Frodo; move Opal-Eye to `rule:prevent-fixed-damage-any-target`** (n=20, "Prevents a fixed amount of the next damage … whether delivered by a spell or an **activated ability**" — a verbatim fit, broadened by batch-5 D2/Q1 for exactly this); **move Inviolability to `rule:prevent-damage-to-your-creatures`** (n=5) if its definition covers an Aura on any creature, else ledger; **Solitary Confinement needs a player-protection axis, which does not exist** — ledger-flag | Leaves a coherent n=1–2 axis. Solitary Confinement is the one genuine gap. |
| Broaden the definition to "prevents damage to itself or what it protects" | Fuses static self-protection, Aura protection, player protection and activated fixed prevention into one slug — grammar §1 design goal 2. |

## E10 — `rule:token-count-scales-with-x` — DEFINITION CLAIMS ETB; 3 OF 4 ARE SPELLS

**Definition:** "The number of tokens created by an **enters-the-battlefield
ability** scales directly with the X value."

| member | delivery |
|---|---|
| Farmer Cotton | "**When this creature enters**, create X …" — ETB ✓ |
| Forth Eorlingas! | sorcery — "Create X 2/2 red Human Knight creature tokens…" (**NO QUOTE**) |
| Path of the Ghosthunter | plane card — "Create X 1/1 white Spirit creature tokens with flying." |
| White Sun's Zenith | instant — "Create X 2/2 white Cat creature tokens." |

The slug is **unmarked**, so under §1 it claims spell delivery — which fits the
three spells and not Farmer Cotton. The definition asserts the opposite.

✅ **Correct the definition to the unmarked-spell reading** (§1, CR 113.3a) and
**split Farmer Cotton to `rule:etb-token-count-scales-with-x`**, the same D3d
treatment tier-3 D3/D6 applied. Alternative: drop the ETB clause and let the
axis span both deliveries — but that is the reading D3d rejected.

Gate #0 checked: Path of the Ghosthunter is a plane card and passes
legitimately (legal in legacy/vintage/commander/oathbreaker/duel), so its
membership is not a gate question. Note the CLAUDE.md trap — `cards.sqlite`
excludes plane layouts, so any consumer reading from there will not see this
member.

## E11 — `rule:tutor-from-outside-game-to-hand` / Research // Development — DESTINATION

**Definition:** "…put it **into hand**."

- Glittering Wish — "put it into your **hand**" ✓
- Mastermind's Acquisition — "Put a card you own from outside the game into your **hand**." ✓
- Living Wish — "put it into your **hand**" ✓
- **Research // Development** — "**Shuffle** up to four cards you own from outside the game **into your library**." ✗

Same outside-the-game zone, different destination — and the slug names the
destination explicitly.

✅ **Drop and ledger-flag** as `rule:tutor-from-outside-game-to-library`, a
grammar-composable sibling with one member. Read all faces: the Development
half is the outside-the-game text, the Research half is unrelated.

## E12 — `rule:death-trigger-plus1-counter-transfer` / Host of the Hereafter — BREADTH

**Definition:** "**When this permanent dies**, it moves its accumulated +1/+1
counters onto another target permanent."

- Star Pupil, Scolding Administrator, Servant of the Scale — "When this creature dies…" ✓
- **Host of the Hereafter** — "Whenever **this creature or another creature you control** dies, if it had counters on it, put its counters on up to one target creature you control."

Host of the Hereafter satisfies the axis for its *own* death, so the membership
is not wrong — but half its ability (other creatures dying) is uncaptured.

✅ **Low severity: note the broader trigger as a facet, no member action.**
Recorded rather than proposed. Also noted: Scolding Administrator's text says
"if it had **counters**" untyped, while the slug says `plus1-` — in practice
its own Repartee ability only ever puts +1/+1 counters on it, so the typed slug
is true of the card. Not proposed as a rename; batch-5's
polarity-is-a-parameter ruling counsels against splitting on counter kind.

---

## §S4 — SYSTEMIC: 44 DET memberships rest only on token-definition reminder text

Not tier-4-specific. Root-caused, and it is a **pattern defect, not a model
error** — every one is `class=rule-derived`.

**Root cause.** The F2 walk fix (walk-ratification §2.1) widened these patterns
from sentence-scoped `[^.]*` to **paragraph-scoped `[^\n]*`**, correctly, so
that Omnath's "add {R}{G}{W}{U}" in a later sentence would match. But oracle
reminder text sits **on the same line** as the ability that spawns it, so the
same widening swept token-definition parentheticals into range. A Map token's
"Activate only as a sorcery" now matches a card that has no activated ability
at all.

**Measured, after two false starts I want to be explicit about.** A naive
"match dies when all parentheses are stripped" test returns **154** — but most
of those are legitimate: Unearth, Encore, Cycling and Forecast reminder text
*restates the card's own keyword ability* (CR 702.140 defines Encore as an
activated ability with "Activate only as a sorcery" in its own rules text), so
the restriction is real. A second attempt keyed on "contains a token" returned
**90** and wrongly swept `rule:created-token-enters-tapped`, an axis *about*
tokens where token reminder text is the correct evidence.

The defensible number keys on **token-definition** parentheticals only — a
parenthetical that says what a created token *is*:

| axis | memberships | what the reminder describes |
|---|--:|---|
| `rule:activation-restricted-to-sorcery-speed` | 37 | Map / Clue / Junk token: "Activate only as a sorcery" |
| `rule:restricted-purpose-mana` | 5 | Powerstone token: mana that can't cast nonartifact spells |
| `rule:landfall-gain-life` | 1 | Food token: "You gain 3 life" |
| `rule:landfall-produces-mana` | 1 | Treasure token: "Add one mana" |
| **total** | **44** | |

Hand-verified instances: Get Lost, Storm Fleet Negotiator, Spyglass Siren,
C.A.M.P., Junk Jet, Zoo Escapees, Tireless Provisioner ×2. Each is an instant,
sorcery or creature with **no activated ability of its own** sitting on an
activation-restriction axis.

**Why this is the created-ability rule, not a new principle.** Grammar §2,
Captain-ratified today: *"a card does not deliver an ability it CREATES … or a
**token's** printed text."* That rule was ratified against SYNTH misfiles; §S4
is the same rule applied to DET patterns, which no one has done.

✅ **Recommendation, in order:**
1. Rule that the created-ability rule binds DET patterns as well as membership
   judgments. Everything else follows.
2. Fix the **producer, not the data** (G4: generated artifacts get generator
   fixes) — DET preprocessing strips token-definition parentheticals before
   matching, exactly as it already canonicalizes CARDNAME. Keyword reminder
   text must be **preserved**, or Unearth/Encore/Cycling members are destroyed.
3. Re-run the affected patterns and diff; the 44 should fall out, and any
   member that *survives* is a member the strip rule got wrong.
4. Each removal takes its D5 remove-and-rehome answer.

This is the third systemic finding the re-audit has produced (tier 3's §S,
88 Alchemy memberships; this). Both were invisible to every existing gate.

---

## §M — Mechanical: 2 unevidenced members

| axis | card | proposed quote |
|---|---|---|
| `etb-destroy-target-enchantment` | Aven Cloudchaser | "When this creature enters, destroy target enchantment." |
| `token-count-scales-with-x` | Forth Eorlingas! | "Create X 2/2 red Human Knight creature tokens with trample and haste." |

Both verified against full oracle text. Aven Cloudchaser is batch-5 D14's
seed member for its axis and the quote was never landed.

---

## Verified clean — no action (8 axes, 32 member-reads)

- **`rule:combat-damage-to-player-triggers-self-plus1-counter`** — all four print the identical trigger. The any-damage split (today's ruling) already moved out what didn't belong.
- **`rule:conditional-attack-restriction-by-defending-player-land-type`** — all four carry identical printed text. **Confirms tier-2 D2's merge landed correctly.**
- **`rule:etb-pump-target-creature`** — all four ETB pumps. **Confirms batch-6 D3's dropped-ownership-clause ruling is holding at n=4.** Guac & Marshmallow Pizza's "Untap it." rider is a multi-facet note only.
- **`rule:etb-surveil`** — all four verified. **Confirms today's D5.**
- **`rule:evasion-vs-low-power-blockers`** — all four "can't be blocked by creatures with power 2 or less" ✓. Its **name** is the open tier-3 D13 question (Q8's ratified `cant-be-blocked-<restriction>` grammar); **not re-raised here.**
- **`rule:prevents-damage-prevention`** — all four "Damage can't be prevented" ✓.
- **`rule:restricts-blocking-to-flying-only`** — all four "can block only creatures with flying" ✓.
- **`rule:skips-controller-draw-step`** — all four "Skip your draw step." ✓.

**Tooling note, not a defect:** `foundry_reaudit.py` and
`foundry_definition_drift.py` both call `load_corpus()` rather than
`load_corpus_gated()`. G6 requires the gated loader for *corpus probes and
hit-counts*; these two tools only read cards already in the codebook (gated at
membership time) and compute no corpus hit-counts, so neither violates G6.
Recorded so a future reader does not re-raise it.

## Cost summary if every ✅ is ratified

| decision | new axes | moves | drops | definition edits | quotes |
|---|--:|--:|--:|--:|--:|
| E1 Dwarven Landslide | 0 | 1 | 0 | 0 | 0 |
| E2 Gravity Negator + clause | 0 | 1 | 0 | 1 | 0 |
| E3 Familiar Beeble Mascot | 0 | 0 | 1 | 0 | 0 |
| E4 Arius | 0 | 0 | 1 | 0 | 0 |
| E5 Echoes of Eternity | 1 | 1 | 0 | 0 | 0 |
| E6 draw-second 2×2 | 2 | 3 | 0 | 1 | 0 |
| E7 Brokers Charm | 0 | 1 | 0 | 0 | 1 |
| E8 Tireless Provisioner | 0–2 | 0–2 | 2 | 0 | 0 |
| E9 prevents-damage-to-self | 0 | 2 | 1 | 1 | 0 |
| E10 token-count-scales-with-x | 1 | 1 | 0 | 1 | 1 |
| E11 Research // Development | 0 | 0 | 1 | 0 | 0 |
| E12 Host of the Hereafter | 0 | 0 | 0 | 0 | 0 |
| **total** | **4–6** | **10–12** | **6** | **4** | **2** |

Plus §S4, which is its own ruling and larger than all of the above combined.

## The judgment calls, not the bookkeeping

- **§S4 is the finding.** A ratified DET pattern set has been writing
  `class=rule-derived` memberships off text that belongs to tokens. It is
  full-weight provenance, so nothing downstream discounts it.
- **E6 needs no new ratification** — batch-5 D12 ledgered the scheme and
  grammar §11 makes instantiation automatic. It is the clearest case yet of the
  grammar doing the work it was built for.
- **Six of twelve findings are again the definition, not the member** (E2b, E9,
  E10, E12, and half of E3 and E6). Same ratio as tier 3.
- **Three tier-4 axes came back clean *because* of earlier rulings.** That is
  the first evidence the re-audit is converging rather than just finding more.
