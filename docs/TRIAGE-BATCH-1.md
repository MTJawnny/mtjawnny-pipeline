# TRIAGE — Batch 1 (SUP full-pass, 2026-07-18)

Produced by Fable 5 under the ratified SUP-triage protocol from
batch-1-enriched.json (105 axes / 1,040 OTHER rows / 476 cards, quote-DF +
full oracle text attached). Every axis was read in full, member cards and
quotes included. Nothing here is load-bearing until you ratify it.

**How to use this doc:** read the lanes top-down. Lanes 1–3 are my confident
calls — skim, strike anything wrong, initial the rest. Lane 4 is the
questions; answer inline. §6 is the honesty check — verify those 30 rows
against card text before trusting the rest. When you hand this back
annotated, I emit `decisions/batch-1.json`.

**Verdict counts:** KILL 30 · MERGE 12 (8 absorbed into 4 targets) ·
QUESTION 15 · KEEP 48 = 105. Plus 12 proposed OTHER-lane promotions (§5).

---

## 0. Enrichment findings, interpreted

- **Discard audit: gate vindicated.** All 4 Stage-1B discards quoted
  non-oracle-text fields (type line ×2, mana cost, card name). Zero
  face-scanning misses. No action needed; batch-2 SYNTH prompt should say
  "quote oracle text only" to prevent the waste.
- **The 79 substring-only reminder flags are the bare-keyword pattern**, not
  restatements — quotes like "Haste" tripping the flag because they occur
  inside some other keyword's reminder text. They aren't false positives for
  our purposes: a bare-keyword quote is exactly the Tagger-redundant shape
  the SUP spot-check flagged at 13%. My KILL lane absorbs them at the axis
  level. The 4 exact restatements are inside those same killed axes.
- **Alchemy leakage:** A-Shipwreck Sifters and A-Cobbled Lancer appear as
  members/rows. Paper-preference belongs in batch-2's sampling and the
  emit resolver. Doesn't invalidate the axes they sit in.

---

## 1. PROPOSED KILL (30)

### 1a. Bare-keyword axes — Tagger-redundant (14)

The axis exists only because members share a printed keyword. The Tagger
layer and the engine's keyword handling already own this signal; a derived
tag adds pure double-counting. This is the SUP's 13% pattern at axis scale.

| Axis | Members' shared content | Max quote-DF |
|---|---|---|
| evasion-flying | "Flying" ×7 | 4,946 |
| grants-evasion-flying | "Flying" variants | 4,946 |
| grants-flying-self | "Flying" + one activated grant | 4,946 |
| evasive-flying-body | "Flying" ×2 (exact dup of evasion-flying) | 4,946 |
| grants-trample | "Trample" ×6 | 1,747 |
| trample-excess-damage | "Trample" + reminder ×2 | 52 |
| flash-cast-timing | "Flash" ×4 | 955 |
| instant-speed-cast | "Flash" ×2 (exact dup of above) | 955 |
| first-strike-combat | "First strike" ×2 | 838 |
| evasion-menace | "Menace" ×2 | 708 |
| deathtouch-grant | "Deathtouch" ×2 | 628 |
| lifelink-grant | "Lifelink" ×3 | 749 |
| grants-lifelink-self | lifelink reminder + one activated grant | 60 |
| grants-vigilance | "Vigilance" ×2 | 1,188 |

### 1b. Keyword-mechanism reminder axes — keyword-ledger territory (3)

Real mechanics, but they're *keywords*: the ratified Phase B keyword ledger
is the governed home for per-keyword surfaces, not the derived-tag layer.

- **equip-cost** ("Equip {2}", DF 266) — equipment-ness is a type-line fact.
- **convoke-cost-reduction** (Convoke reminder, DF 100) — ledger candidate.
- **exploit-sacrifice-trigger** (Exploit reminder, DF 24) — ledger candidate;
  note for Phase B: exploit-as-functional-sac-outlet kinship to non-keyword
  cards is a genuinely good ledger entry.

### 1c. Procedural riders and templating boilerplate (7)

Shared wording that carries no functional kinship — two cards sharing "then
shuffle" are not kin. Several are parameter dimensions, not axes.

- **shuffle-library-after-search** ("then shuffle", DF 1,138)
- **reveal-searched-card** (reveal-then-shuffle rider; members already
  covered by tutor-to-library-top / etb-tutor-to-hand)
- **saga-chapter-progression** (saga reminder text, DF 138 — layout fact)
- **sorcery-speed-restriction** ("Activate only as a sorcery", DF 568 —
  a *parameter* on an ability, not an axis)
- **mana-value-restricted-target** (MV threshold — the engine already models
  MV scope as a penalty term; capture as parameter dimension, never as axis)
- **any-number-of-targets** (targeting templating — parameter, not axis)
- **end-step-trigger** (timing boilerplate. NOTE: member Wilderness
  Reclamation's quote "untap all lands you control" belongs to the untap
  family — reassign via §5/P-untap when that lands)

### 1d. Incoherent grab-bags — label-driven clusters (4)

Members share label tokens, not function.

- **tap-ability-activated** — Giver/Mother of Runes (protection grants) +
  Thassa (tapper) + Piper/Stoneforge (cheat/tutor). All members re-covered
  by better axes.
- **restricted-to-card-type** — Dovin's Veto + Scrounge. Nothing in common.
- **counter-removal-on-trigger** — rad counters + time counters. No.
- **grants-stat-buff** — generic aura/equip stat buffs, no coherent kinship.

### 1e. Generic riders with huge DF (2)

- **card-draw-payoff** — one member quote is "draw a card" at DF 3,239. The
  real concept (triggered draw engines) survives properly in
  cast-trigger-card-draw / triggers-on-cast (see KEEP notes).
- **self-buff-counter** — "put a +1/+1 counter on this creature", DF 609.
  Rider, not identity. (Its cousin self-counter-growth is Q5.)

---

## 2. PROPOSED MERGE (8 absorbed → 4 surviving axes)

**M1 → rule:enters-tapped** (param `scope: self | fetched-object`)
Absorb enters-tapped-restriction into enters-tapped-drawback. Also pull in
the OTHER row "enters-tapped" (Time Vault). Same clause, two polarities of
who it's attached to — Lesson 1 shape.

**M2 → rule:targeted-destruction** (params `type`, `scope`)
Absorb unconditional-permanent-removal + targeted-permanent-destruction +
targeted-artifact-removal + unconditional-destroy-effect into ONE
parameterized axis. Evidence they're the same axis: Murder's "Destroy target
creature" and Casualties of War appear across three of the four.
Params: type (creature / artifact / artifact-or-enchantment / permanent /
nonland-MV≤N), scope note for Vandalblast's "you don't control".
unconditional-exile-removal stays SEPARATE — exile vs destroy is a real
functional boundary (indestructible interaction).

**M3 → rule:land-fetch-to-battlefield** (rename of land-tutor-onto-battlefield)
Absorb library-search-shuffle — its members (Wood Elves, Rampant Growth) are
land-fetch-to-battlefield cards; the axis was named after its rider.

**M4 → rule:modal** (param `choose-count: 1 | 2 | N`)
Absorb modal-choose-one into modal-choose-two under one parameterized axis.
Modality was one of your deliberate seed buckets; the choose-count is the
parameter, not two axes.

**M5 → rule:free-sacrifice-outlet** (param `payoff: mana | scry | ...`)
Absorb convert-creature-to-mana — its members (Phyrexian Altar, Ashnod's
Altar) are a strict subset of free-sacrifice-outlet's. Payoff is the param.

---

## 3. CONFIDENT KEEP (48)

Full list, notes only where they earn their line. Everything here keeps its
SYNTH granularity; parent/parameter notes go to the schema pass per the
ratified review procedure.

**Gold — flagship-quality families:**
- **doubles-token-creation**, **doubles-counter-placement**,
  **doubles-etb-triggers** — the parameterized-doubling super-family, now
  three confirmed siblings (+ Tekuthal's doubles-proliferate in OTHER).
  Note parent `doubles-<thing>` at schema pass.
- **drain-on-creature-death** — Blood Artist / Zulaport / Kokusho. Exactly
  right.
- **forces-opponent-sacrifice** — the edict family (Grave Pact, Dictate).
- **symmetric-hand-refill** — wheels (Wheel of Fortune, Windfall).
- **free-sacrifice-outlet** (M5 target), **land-fetch-to-battlefield** (M3),
  **targeted-destruction** (M2), **enters-tapped** (M1), **modal** (M4).
- **compensates-controller-with-token** — Pongify/Generous Gift/Beast
  Within downside family. Nobody else has this axis.
- **alternate-win-condition**, **life-total-reset**,
  **conditional-creature-status** (Theros gods),
  **grants-extra-turn**, **grants-extra-land-drop**,
  **cheat-creature-into-play**, **reanimate-from-graveyard**,
  **tutor-to-library-top**, **scales-mana-by-permanent-count** (Coffers!).

**Solid keeps:** cant-be-countered, cast-from-top-of-library,
library-top-visibility (note: future-sight pair — parent candidate),
cast-trigger-card-draw + triggers-on-cast-instant-sorcery (note: parent
`triggered-on-cast(filter, payoff)` at schema pass — NOT merged now),
choose-creature-type-on-etb, copy-creature-token, creates-creature-token,
etb-create-token, death-trigger-token-creation (note: token-creation parent
is Q4), death-trigger-draw-card, direct-damage-any-target (param: any-target
vs creature-only), etb-counter-on-other-creature, etb-destroy-artifact-
enchantment, etb-exile-graveyard-card, etb-loot (Alchemy row noted),
etb-tutor-to-hand, forced-hand-reveal, graveyard-to-hand-recursion,
grants-unblockable (non-keyword grant — deliberately NOT in Q1),
lifegain-scaled-by-mana-value, lifegain-triggered-counter,
mass-counter-distribution, mass-untap-your-creatures (your param notes from
the earlier row stand), power-scales-with-creature-count,
prevents-regeneration (low-priority historic rider, coherent),
temporary-control-theft, the-ring-tempts-you (note: check Tagger equivalence
later), tribal-anthem-buff (param: tribe), unconditional-exile-removal.

**Keeps with an edit:**
- **forced-discard** → remove the Wheel of Fortune member (it lives in
  symmetric-hand-refill; its quote here is the mass case) and rename
  **rule:targeted-discard** (param scope: target-player | each-opponent).
- **draw-multiple-cards** → rename **rule:burst-draw** (param: count).
  Generic-adjacent but a real deckbuilding concept; watch it in batch 2.

---

## 4. QUESTIONS — need your ruling (5 questions covering 15 axes)

**Q1 — Keyword-grant axes vs the engine's granted-keyword dimension.**
(covers: grants-haste, grants-hexproof, grants-indestructible,
grant-indestructible-mass, grants-double-strike, grants-team-trample,
grants-protection, grants-keyword-ability, grants-haste-to-token,
protection-from-color)
The engine's T2 kinship machinery ALREADY models keyword grants
(granted_keyword dimension, with scope/duration params). A derived
`rule:grants-haste` tag double-dips the exact signal — same DF-inflation
shape as the duplicate-oracle-rows problem.
**My proposal: KILL all ten as engine-redundant**, with two carve-out notes:
(a) grants-unblockable stays KEEP — "can't be blocked" is not a keyword, the
granted_keyword dimension can't see it; (b) grants-haste-to-token's
archetype (Kiki/Helm token-haste enablers) — verify the engine already links
those two via granted_keyword before killing; if it doesn't, that's an
engine gap worth a punch-list line, not a derived tag.
**Alternative:** keep them with a no-double-dip scoring rule. I think that's
machinery for no gain — the engine's version is strictly richer.
→ RULE: kill-as-redundant / keep-with-rule: ______

**Q2 — Drain/lifegain restructure.** (covers: drain-life-effect,
lifegain-tied-to-drain, opponent-life-loss)
These three are one blurry cloud with generic quotes ("you gain 1 life" DF
498, "you gain 3 life" DF 367). Proposal: MERGE all three →
**rule:drain-life** (opponent loses + you gain, members: Exsanguinate, HYDRA
Infiltration, Treacherous Greed, Exquisite Blood, Zulaport's drain face),
and MOVE Sanguine Bond out — it isn't a drain, it's a *lifegain payoff*
(trigger: you gain life → effect), which makes it kin to Archangel of Thune
and Ajani's Pridemate (lifegain-triggered-counter). Note a
`lifegain-payoff(effect)` parent at schema pass.
→ RULE: ratify restructure / keep as-is: ______

**Q3 — Cantrip.** (cantrip-card-draw, "Draw a card." DF 2,473)
Too generic to ever qualify (DF is 14× the ceiling), but "cantrip" is a
real deckbuilder search concept and DERIVED_QUALIFY_DF_CEILING already
makes it rank-only automatically. Keep as a rank-only archetype tag, or
kill as noise? I lean **KEEP** — the ceiling ruling exists precisely so
generic-but-real signals can contribute without flooding.
→ RULE: keep rank-only / kill: ______

**Q4 — Token-creation super-family.** creates-creature-token,
etb-create-token, death-trigger-token-creation, copy-creature-token are all
KEEP, but they're obviously `token-creation(trigger)` with trigger ∈
{spell-rider, etb, death, copy}. Fold into one parameterized axis NOW, or
keep four siblings and parent them at the schema pass? I lean **schema pass**
— consistent with "judge at SYNTH granularity," and batch 2 will surface
more trigger values (attack triggers, upkeep) that inform the shape.
→ RULE: now / schema pass: ______

**Q5 — self-counter-growth** (A-Shipwreck tap-ability + Mikaeus). Marginal:
"grows itself with counters" is a real archetype (monstrosity/level-up
adjacent) but these members are thin and its cousin self-buff-counter is
KILLed above as a rider. Keep-thin (batch-2 confirmation target) or kill
both? I lean **keep-thin**.
→ RULE: keep-thin / kill: ______

---

## 5. OTHER-LANE PROMOTIONS (12 proposed new axes)

The token groups surfaced coherent multi-card families that exact-match
clustering couldn't merge (different label words, same concept). Each
promotion below has 2+ distinct verified member cards. Long tail (~450
groups) stays in OTHER for batch-2 targeting per the spec.

**P1 — rule:restricts-opponent-cast-timing** — Silence, Teferi Time Raveler,
Grand Abolisher (×2 rows). THIS IS THE FLAGSHIP FAMILY — it corroborates and
extends the shipped turn-scoped derivation. Reconcile with the shipped
rule:turn-scoped tags rather than creating a parallel axis: Teferi's
positive-polarity phrasing is the exact Lesson 1 target the SUP confirmed.

**P2 — rule:restricts-opponent-search** — Stranglehold, Aven Mindcensor.
Search-hate, clean and real.

**P3 — rule:limits-card-draws** — Spirit of the Labyrinth + the
limits-opponent-extra-draws row (draw+opponent group). Notion Thief-family
adjacent; batch-2 confirmation target.

**P4 — rule:rhystic-tax** (pay-or-I-benefit / pay-or-you-can't) — Rhystic
Study, Mystic Remora, Smothering Tithe. Classic named archetype, gorgeous
axis, three members already. Relates to the ratified pay-tax family — note
the polarity difference (tax-as-toll vs tax-as-your-gain) for the family
tree.

**P5 — rule:taxes-opponent-spell-cost** — Aura of Silence (+ pay-tax-cast
family reconciliation; more members certainly in corpus).

**P6 — rule:cost-reduction** (params: filter = tribe/type/color/chosen-type/
condition) — Foundry Inspector, Baral, Sapphire Medallion, Herald's Horn,
Goreclaw, Animar, Blasphemous Act, Arcane Epiphany. Big, real, obviously
parameterized. EXCLUDE the Delve and Affinity rows (keyword mechanisms →
Phase B ledger).

**P7 — rule:free-cast** (params: source, condition) — Omniscience, Fires of
Invention, Etali, free-cast-copy rows. EXCLUDE Cascade row (keyword →
ledger).

**P8 — rule:free-cast-if-commander** — Fierce Guardianship + Flawless
Maneuver: exact two-member family with identical condition clause. Could be
a param of P7; I'd keep it distinct — the "free spells" cycle is a named
archetype.

**P9 — rule:mass-graveyard-exile** — Rest in Peace (ETB face), Farewell,
Soul-Guide Lantern (sac face). One-shot gy-wipe.

**P10 — rule:graveyard-to-exile-replacement** — Rest in Peace (static face),
Leyline of the Void, Dauthi Voidwalker. The REPLACEMENT-effect family,
functionally distinct from P9 (continuous vs one-shot) — keep separate.
Gold axis; nobody else separates these correctly.

**P11 — rule:x-scales-with-permanent-count** (params: counted-thing, output)
— Craterhoof, Krenko, Elvish Archdruid, Coat of Arms, All That Glitters,
Shared Animosity. Broad; promote with batch-2 confirmation flag.

**P12 — Ward rows: do NOT promote.** Roaming Throne / Rimeshield rows are
bare "Ward {N}" — keyword, Tagger-covered, same KILL logic as lane 1a.

---

## 6. OVERRIDE SPOT-CHECK — verify these 30 before trusting the rest

Fixed seed 20260718, drawn from my 90 confident calls (KILL + MERGE + KEEP;
Q-lane excluded). Check each verdict against the card text. If more than ~1
is wrong, distrust the lanes and tell me — loudly.

| Axis | My verdict | Sample member | Evidence quote |
|---|---|---|---|
| forced-hand-reveal | KEEP | Thoughtseize | Target player reveals their hand. |
| choose-creature-type-on-etb | KEEP | Herald's Horn | As this artifact enters, choose a creature type. |
| grants-lifelink-self | KILL | Archangel of Thune | Lifelink (Damage dealt by this creature also causes you |
| etb-loot | KEEP | A-Shipwreck Sifters | When Shipwreck Sifters enters, draw a card, then discar |
| grants-extra-turn | KEEP | Time Warp | Target player takes an extra turn after this one. |
| scales-mana-by-permanent-count | KEEP | Axebane Guardian | {T}: Add X mana in any combination of colors, where X i |
| compensates-controller-with-token | KEEP | Pongify | Its controller creates a 3/3 green Ape creature token. |
| grants-evasion-flying | KILL | Mahamoti Djinn | Flying (This creature can't be blocked except by creatu |
| cheat-creature-into-play | KEEP | Dreamshaper Shaman | Put that card onto the battlefield |
| doubles-token-creation | KEEP | Parallel Lives | If an effect would create one or more tokens under your |
| life-total-reset | KEEP | The Highland Runner | you may have each player's life total become 20 |
| death-trigger-token-creation | KEEP | Thopter Mechanic | When this creature dies, create a 1/1 colorless Thopter |
| power-scales-with-creature-count | KEEP | Assembled Ensemble | Assembled Ensemble's power is equal to the number of Ro |
| cast-from-top-of-library | KEEP | Ranger Class | You may cast creature spells from the top of your libra |
| library-search-shuffle | MERGE | Wood Elves | search your library for a Forest card, put that card on |
| death-trigger-draw-card | KEEP | Solemn Simulacrum | When this creature dies, you may draw a card. |
| grants-unblockable | KEEP | Temmet, Vizier of Naktamun | can't be blocked this turn |
| self-buff-counter | KILL | Tishana's Wayfinder | put a +1/+1 counter on this creature |
| targeted-artifact-removal | MERGE | Vandalblast | Destroy target artifact you don't control. |
| unconditional-destroy-effect | MERGE | Celestial Judgment | Destroy each creature not chosen this way. |
| library-top-visibility | KEEP | Ranger Class | You may look at the top card of your library any time. |
| etb-destroy-artifact-enchantment | KEEP | Reclamation Sage | When this creature enters, you may destroy target artif |
| etb-create-token | KEEP | Living History | When this enchantment enters, create a 2/2 red and whit |
| doubles-etb-triggers | KEEP | Yarok, the Desecrated | If a permanent entering causes a triggered ability of a |
| tap-ability-activated | KILL | Giver of Runes | {T}: Another target creature you control gains protecti |
| cast-trigger-card-draw | KEEP | Vanquisher's Banner | Whenever you cast a creature spell of the chosen type, |
| etb-counter-on-other-creature | KEEP | Walking Ballista | This creature enters with X +1/+1 counters on it. |
| lifegain-scaled-by-mana-value | KEEP | Blood Poet | You gain life equal to its converted mana cost. |
| evasion-flying | KILL | Restoration Angel | Flying |
| etb-exile-graveyard-card | KEEP | Soul-Guide Lantern | When this artifact enters, exile target card from a gra |

---

## 7. Batch-2 feedback (fold into Session C / SYNTH prompt)

1. Quote oracle text only (kills the 4-discard waste).
2. Never propose an axis whose evidence is a bare keyword or its reminder
   text (kills lane 1a at the source).
3. Prefer paper printings over A- Alchemy rows in sampling and emit.
4. Two-lane labeling: use codebook v0.1 label when it genuinely fits, free
   label otherwise (pending your earlier ruling).
5. Riders vs identity: instruct SYNTH that procedural riders ("then
   shuffle", "reveal it", timing templating) are not axes (kills lane 1c).
6. Batch-2 hand-picked targeting: the thin 2-member KEEPs, the promotion
   candidates P3/P11, and Q5 if kept.
