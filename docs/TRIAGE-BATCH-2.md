# TRIAGE — Batch 2 (SUP full-pass, 2026-07-18)

Produced by Claude (SUP-class session) under the ratified SUP-TRIAGE-PROTOCOL,
reading `experiments/out/foundry/review/digest-batch-2.md` (149 axes: 64
confirming existing codebook v0.1 axes, 85 new candidates from free-lane
clustering; 1,412 OTHER-lane rows; 1,051 token groups) against the current
codebook. Every axis and every multi-card token group was read in full
before any verdict was written. Nothing here is load-bearing until Captain
ratifies.

**How to use this doc:** read the lanes top-down. Lanes 1–3 are confident
calls — skim, strike anything wrong, initial the rest. Lane 4 is the
questions; answer inline. §6 is the honesty check — verify those 30 rows
against card text before trusting the rest. When you hand this back
annotated, `/triage-emit 2` parses it into `decisions/batch-2.json`.

**Verdict counts:** KEEP 112 (64 existing confirmations + 48 new) · KILL 21
· MERGE 12 · QUESTION 4 = 149, one verdict per axis, no double-counting.
Zero contradictions surfaced against the codebook — every `lane=codebook`
two-lane resolution the model made was correct (0/512 anomalies) — a clean
convergence signal.

---

## 0. Findings, interpreted

- **Two-lane labeling worked cleanly.** 512 of 2,122 kept instances
  (24%) resolved to an existing codebook slug via `lane=codebook`, with
  **zero anomalies** (no instance claimed a codebook slug that didn't
  resolve to an active axis). This is the strongest evidence yet that the
  codebook-embedded SYNTH prompt is doing its job — batch 3's prompt
  should keep this shape.
- **All 64 existing-axis confirmations are clean KEEPs.** No batch-2
  evidence contradicts any ratified batch-1 axis. Several grew
  substantially (`rule:creates-creature-token` 7→62, `rule:enters-tapped`
  6→49, `rule:targeted-destruction` 10→32, `rule:modal` 5→22,
  `rule:targeted-exile` 2→21) — flagged per-axis below for the schema
  pass, not restructured now per this session's scope.
- **A real, systemic new-candidate defect: single-card "axes."** At
  least 5 of the 85 new candidates (`conditional-buff-by-color`,
  `mass-damage-to-creature-subset`, `grants-ability-at-counter-threshold`,
  `self-mana-ability-grants-keyword`, `werewolf-daybound-transform-trigger`)
  have `n=2` but **both instances trace to the same physical card** —
  the SYNTH model found two genuinely distinct functional axes on one
  card that happened to free-label identically. `foundry_consolidate.py`'s
  clustering counts raw instances, not distinct cards, so these slipped
  through as if corroborated. All five are KILLed below as insufficient
  evidence (not a real multi-card family) — see §7 for the fix.
- **OTHER-lane token groups: no promotions this batch.** Sampled across
  the full size range (n=38 down to n=4, several hundred groups spanning
  every size tier) — every single one is a generic 2-token-overlap
  collision bucket (e.g. `[count/scal]`, `[combat/damage]`) spanning
  unrelated mechanics that happen to share two label words. This is
  expected and was predicted by the protocol's own convergence-metric
  note: batch 2's genuine multi-card families were already captured
  either as `lane=codebook` hits or as exact-full-label-token-set free
  clusters (the 85 new candidates); the *partial*-overlap residue left in
  OTHER is close to pure noise by construction. Zero promotions proposed
  — see §5.
- **A cluster of KILLs traces to keyword/mechanism territory**, same
  shape as batch 1's lane 1b: Kicker (3 instances), Venture into the
  Dungeon, Daybound/Nightbound (werewolf transform), Saga-transform
  templating. All carry forward to the keyword ledger (§8).
- **Several new candidates are exact duplicates or parameterizations of
  already-ratified axes** and MERGE rather than stand alone — see §2.

VERDICT: All Good
---

## 1. Existing codebook confirmations (64) — all KEEP

Full list, growth notes only where the axis size now warrants a schema-pass
flag. No contradictions, no reversals proposed against batch 1.

`rule:alt-win-empty-library` (n=1), `rule:alternate-win-condition` (n=4),
`rule:burst-draw` (n=12), `rule:cant-be-countered` (n=6), `rule:cantrip`
(n=5), `rule:cast-from-top-of-library` (n=4), `rule:cast-trigger-card-draw`
(n=6), `rule:cheat-creature-into-play` (n=5), `rule:choose-creature-type-on-etb`
(n=1), `rule:compensates-controller-with-token` (n=3),
`rule:conditional-creature-status` (n=4), `rule:copy-creature-token` (n=6),
`rule:cost-reduction` (n=7),
**`rule:creates-creature-token` (n=62 — VERDICT: KEEP — note: grew from 7 in
batch 1; genuinely coherent (every member creates a token as a byproduct)
but now large enough to warrant the already-flagged `token-creation(trigger)`
parent split at the schema pass, per batch-1's Q4 ruling. Not restructured
now.)**,
`rule:death-trigger-draw-card` (n=1), `rule:death-trigger-token-creation` (n=3),
**`rule:direct-damage-any-target` (n=30 — VERDICT: KEEP — growth note only,
same schema-pass flag)**,
`rule:doubles-counter-placement` (n=4), `rule:doubles-etb-triggers` (n=1),
`rule:doubles-token-creation` (n=2), `rule:drain-life` (n=11),
**`rule:enters-tapped` (n=49 — VERDICT: KEEP — growth note: schema pass
should confirm the existing `scope: self | fetched-object` param actually
covers all 49 members; do not split now)**,
`rule:etb-counter-on-other-creature` (n=6), `rule:etb-create-token` (n=12),
`rule:etb-destroy-artifact-enchantment` (n=3), `rule:etb-exile-graveyard-card`
(n=2), `rule:etb-loot` (n=4), `rule:etb-tutor-to-hand` (n=6),
`rule:exile-until-source-leaves` (n=6), `rule:forced-hand-reveal` (n=7),
`rule:forces-opponent-sacrifice` (n=1), `rule:free-cast` (n=16, +1 more via
merge — see §2), `rule:free-sacrifice-outlet` (n=5, +1 via merge),
`rule:grants-extra-land-drop` (n=5), `rule:grants-extra-turn` (n=2),
`rule:graveyard-to-hand-recursion` (n=7), `rule:land-fetch-to-battlefield`
(n=3), `rule:library-top-visibility` (n=6), `rule:life-total-reset` (n=6),
`rule:lifegain-triggered-counter` (n=5), `rule:limits-card-draws` (n=1),
`rule:mass-counter-distribution` (n=4), `rule:mass-graveyard-exile` (n=4),
`rule:mass-untap-your-creatures` (n=4),
**`rule:modal` (n=22 — VERDICT: KEEP — growth note, same schema-pass flag)**,
`rule:power-scales-with-creature-count` (n=6), `rule:prevents-regeneration`
(n=3), `rule:reanimate-from-graveyard` (n=14), `rule:restricts-opponent-search`
(n=2), `rule:rhystic-tax` (n=5), `rule:scales-mana-by-count` (n=5, +1 via
merge), `rule:self-counter-growth` (n=1 — Q5 confirmation target succeeded),
`rule:symmetric-hand-refill` (n=5),
**`rule:targeted-destruction` (n=32 — VERDICT: KEEP — growth note, same
schema-pass flag)**,
`rule:targeted-discard` (n=9),
**`rule:targeted-exile` (n=21 — VERDICT: KEEP — growth note, same
schema-pass flag; also absorbs `targeted-creature-damage`'s sibling
`direct-damage-any-target` merge, see §2)**,
`rule:targets-a-player` (n=1), `rule:taxes-opponent-spell-cost` (n=3),
`rule:temporary-control-theft` (n=4), `rule:the-ring-tempts-you` (n=6),
`rule:tribal-anthem-buff` (n=15), `rule:triggers-on-cast-instant-sorcery`
(n=4, +1 via merge), `rule:tutor-to-library-top` (n=3),
`rule:x-scales-with-permanent-count` (n=9, +2 via merge — Captain-flagged
confirmation target succeeded).

VERDICT: All Good
---

## 2. PROPOSED MERGE (12 new candidates → 11 targets: 9 existing codebook
axes + 2 sibling new-candidate axes)

**M1 → existing `rule:animates-land-into-creature`**
Absorb `rule:land-becomes-creature` (5 members: Faerie Conclave, Hall of
Storm Giants, Hive of the Eye Tyrant, Lavaclaw Reaches, Spawning Pool).
Same concept (a land becomes a creature) — the only difference is the
trigger mechanism (spell/ETB-effect vs. the land's own activated ability,
i.e. classic manlands). Param: `trigger: spell-effect | activated-ability`.
JAWNNY-VERDICT: Good. Lets rename to rule:animate-land. there are cards that animate other card types. such as animate-artifact, animate-enchantment, etc. Planswalkers also have loyalty abilites that animate themselves. animate-planswalker. let's keep these names similar. for the whole rules corpus we'll want to audit the final rules names once they're all complete to create a standardization. let's not rename midflight for fear of confusion now. it will be a final audit. log it. 

**M2 → new `rule:tutor-basic-land-to-hand`** (params: `trigger: etb | cast`)
Merge `rule:etb-tutor-basic-land-to-hand` (3: Case of the Shattered Pact,
Ecologist's Terrarium, Temur Monument) with `rule:tutor-basic-land-to-hand`
(2: Flower // Flourish, Thirsting Roots) into one 5-member axis. Both are
"search for a basic land, put it in hand" — land-type specificity is the
real signal here (relevant to manabase-smoothing analysis), worth its own
promoted axis rather than folding into the much broader existing
`rule:etb-tutor-to-hand`.
JAWNNY-VERDICT:All good

**M3 → existing `rule:free-sacrifice-outlet`**
Absorb `rule:sacrifice-for-card-draw` (3: Izzet Locket, Manhole Cover,
Pendulum of Patterns — "Sacrifice this artifact: Draw..."). Same payoff
shape the existing axis's own `payoff` param already anticipates
(currently `[mana, scry, other]` — add `draw`).
JAWNNY-VERDICT: this is not a clean absorb. "rule:free-sacrifice-outlet" demands free sacrifice outlets. Izzet Locket and Manhole Cover require mana to sac. ideologically against the tag name. Do not merge. Free must be Free.

**M4 → existing `rule:grants-unblockable`**
Absorb `rule:activated-grants-self-unblockable` (2: Daring Saboteur,
Harbor Bandit) and `rule:grants-unblockable-target` (2: Veil of Secrecy,
Wormhole Serpent). Same core payoff (a creature becomes unblockable this
turn); target-scope (self vs. other) is a parameter, not a separate axis.
JAWNNY-VERDICT: Do not merge. These two rulings "rule:activated-grants-self-unblockable" and "rule:grants-unblockable-target" all have mechanically different utilizations. 

**M5 → existing `rule:cost-reduction`**
Absorb `rule:cost-reduction-by-graveyard-lands` (2: Igneous Elemental,
Rumbleweed). Fits the existing `filter: condition` param exactly.
JAWNNY-VERDICT: Let's refit/discuss this family of ruling. For cards such as Igneous Elemental,
Rumbleweed that have "This spell costs {N} less to cast~" Lets place them in rules bucket - "rule:individual-cost-reduction" - for cards that reduce their own cost given a condition or some other means. Then "rule:spell-cost-reduction" will be reserved for cards like Etherium Sculptor, Helm of Awakening, Nightscape Familiar. So we may need to open up this rule rather than absorb.

**M6 → existing `rule:x-scales-with-permanent-count`**
Absorb `rule:damage-scales-with-creature-count` (2: Harsh Sustenance, Slash
of Light). "Damage scales with creature count" is a direct instance of the
already-broadened "output scales with permanent count" definition.
JAWNNY-VERDICT: I may have given inaccurate information for the previous round. We do not want to conflate 'rule:x-scales-with-permanent-count' with every instance the game counts an the amount of something, if we do. it must be a parent. regardless. I believe last time the scaling determination was based on MANA, and cards that care about an amount of a Permanent or keyword to base that MANA on. 'rule:damage-scales-with-creature-count' is mechanically different enough to warrant it's own ruling. same as any card type. so 'rule:damage-scales-with-N-count' is the sub parent ruling. the parent ruling being 'rule:N-scales-with-N-count'. So 'draw-scales-with-shrine-count', 'life-scales-with-ally-count', may eventually be rules we employ. another instance of 'don't absorb, expand'.

**M7 → existing `rule:scales-mana-by-count`**
Absorb `rule:mana-output-scales-with-removed-counters` (2: Red Mana
Battery, White Mana Battery). Fits the Captain-ratified broadening
("any count basis... surfaced by co-occurring tags, not sub-axes") exactly
— counters-removed is just another count basis.
JAWNNY-VERDICT: sound logic. The reason we want this as aposed to my verdict above is mana is one vector of the game. allowing one rule to absorb one vector of the game is good logic. absorbing what could be many multiples of mechanics and game logics as above into one rule is bad logic.

**M8 → existing `rule:direct-damage-any-target`**
Absorb `rule:targeted-creature-damage` (2: Electrify, Spit Flame). This
axis's own batch-1 KEEP note literally anticipated this exact split
("param: any-target vs creature-only") — this is that param's second shoe.
JAWNNY-VERDICT: Absolutely not. I was wrong previously. Or did not read with enough care. "Any Target" and "Target Creature" are completely different realms of methodology. Do not absorb these two rulings. we will audit ruling names afer the fact. but these are two different concepts. Planswalker, player, and battles deserve their own ruling. even if rare/nonexistant. rather than absorb. open up. `rule:direct-damage-any-target`, `rule:targeted-creature-damage`, `rule:targeted-player-damage`, `rule:targeted-planswalker-damage`, `rule:targeted-battle-damage` getting their own ruling. If a card targets a special mix. like creature and/or battle, creature and/or player, ect. they recieve multiple tags. rather than their own unique tag. This can be done because the amount of object within magic is a closed system. only so many objects can recieve damage.

**M9 → new `rule:mana-activated-pump-self`** (rename-carrier: larger member
count between the two source clusters)
Merge `rule:activated-pump-ability` (2: Petradon, Vildin-Pack Outcast) with
`rule:mana-activated-pump-self` (2: Andradite Leech, Unyaro Bees) — same
concept from two differently-worded free clusters (4 members total).
JAWNNY-VERDICT: Agreed

**M10 → existing `rule:triggers-on-cast-instant-sorcery`**
Absorb `rule:copies-cast-instant-sorcery` (2: Invasion of Arcavios,
The Mirari Conjecture). The existing axis is deliberately payoff-agnostic
(draw/mill/scry/token-creation already coexist as members) — "copy" is
just another payoff value, not a new trigger-condition axis.
JAWNNY-VERDICT: Agreed. Let's just be vigilant not to conflate the copying of a spell as a cast of a spell. a common mtg misunderstanding.

**M11 → existing `rule:free-cast`**
Absorb `rule:random-card-copy-free-cast` (2: Happy Yargle Day!, Mysterious
Confluence). Same "cast a copy without paying its cost" payoff; the random
*selection* mechanism is a `source` parameter value, not a new axis.
JAWNNY-VERDICT: Do not absorb. these are bullshit cards that are not legal in any format.
---

## 3. PROPOSED KILL (21)

### 3a. Insufficient corroboration — single card, not a real family (4)
Both instances of each trace to the *same* card (the SYNTH model found two
genuinely distinct axes on one card that happened to free-label
identically). Not a multi-card kinship signal.
- `rule:conditional-buff-by-color` (Clout of the Dominus ×2)
- `rule:mass-damage-to-creature-subset` (Caught in the Crossfire ×2)
- `rule:grants-ability-at-counter-threshold` (Voice of the Blessed ×2)
- `rule:self-mana-ability-grants-keyword` (Seraph of the Scales ×2)
JAWNNY_VERDICT: rule:conditional-buff-by-color - Keep; There's an entire cycle of Lorwyn cards that care about a particular color for buffing. rule:mass-damage-to-creature-subset - kill; magic may eventually gain more subsets, for now we can kill, may need to build out later. rule:grants-ability-at-counter-threshold - Change; there are a handfull of cards that do care about how many counters a creature has in the entire corpus. But. Proposition. Let's add it to a new rule `rule:grants-ability-at-threshold-self`. This should be it's own ruling that grabs all cards that grant an ability or additional power to the card once a condition is met. Threshold and Coven are themselves keywords that will be grabbed, but also cards like Crash of Rhino Beetles and Dhund Operative that buff themselves. Voice of the Blessed should have an additional rule specifically describing +1/+1 counters matters. in addition to having "rule:grants-ability-at-threshold-self". The natural next rule is "rule:grants-ability-at-threshold-board". For cards like Hallowed Haunting and cards with the keyword Lieutenant — as they typically grant keywords/abilities/other things to your board once a conditions is met. rule:self-mana-ability-grants-keyword - Keep; lots of cards give themselves keywords based on spending mana. keep.

(`rule:werewolf-daybound-transform-trigger` is *also* single-card
evidence — Lambholt Pacifist // Lambholt Butcher ×2 — but is grouped under
3e below since its primary kill reason is keyword-adjacency; counted once,
not twice.)
JAWNNY-VERDICT: Agreed

### 3b. Procedural riders / cost-shape templating, not identity (6)
Same shape as batch 1's lane 1c: the *mechanism* used to pay a cost, or a
timing restriction, isn't itself a kinship axis — the actual identity is
whatever effect it's attached to (already captured elsewhere).
- `rule:restricted-cast-timing-window` (cast-only-during-X-step; same
  shape as batch-1-killed `sorcery-speed-restriction`)
- `rule:sacrifice-creature-as-additional-cost`
- `rule:discard-as-additional-cost`
- `rule:sacrifice-land-activation-cost`
- `rule:sacrifice-self-as-activation-cost`
- `rule:once-per-turn-trigger-limit` (a limiting clause on some other
  trigger, not an identity of its own)
JAWNNY-VERDICT: Agreed

### 3c. Bare mechanical fact, zero variation (1)
- `rule:no-maximum-hand-size` (both members restate the identical clause
  verbatim — "You have no maximum hand size." — same shape as batch-1's
  bare-keyword-style kills.)
JAWNNY-VERDICT: keep. we want this as a card tag.

### 3d. Generic tautological rider (1)
- `rule:aura-static-pt-buff` ("an Aura gives a static P/T buff" is close
  to a tautological restatement of what most combat-buff Auras do;
  doesn't distinguish a functional family. Same shape as batch-1-killed
  `grants-stat-buff`.)
JAWNNY-VERDICT: Agreed

### 3e. Generic single-clause rider restating existing predicate territory (1)
- `rule:unconditional-single-card-draw` (bare "Draw a card.", DF=2,473 —
  identical shape/DF to batch-1-killed `card-draw-payoff`; the real
  concept already lives in `rule:cantrip`'s ratified predicate.)
JAWNNY-VERDICT: Agreed

### 3f. Keyword/mechanism territory — ledger candidates (8)
Real mechanics, but the *keyword itself* is the shared surface, not a
derived functional pattern — same standing as batch-1 lane 1b.
- `rule:kicked-conditional-etb-bonus`, `rule:kicker-scales-effect`,
  `rule:kicker-scales-effect-magnitude` (Kicker, 3 instances → one ledger
  entry)
- `rule:venture-into-dungeon` (Venture into the Dungeon)
- `rule:saga-transform-into-creature` (Saga-chapter templating — same
  precedent as batch-1-killed `saga-chapter-progression`)
- `rule:grants-haste-to-reanimated-creature` (pure haste grant —
  engine-redundant, Q1 precedent; the reanimation context doesn't change
  what `granted_keyword` already sees)
- `rule:grants-shroud` (pure shroud grant — Q1 engine-redundant, same
  precedent as batch-1-killed `grants-hexproof`/`grants-indestructible`)
- `rule:werewolf-daybound-transform-trigger` (Daybound/Nightbound; also
  single-card evidence per 3a)
JAWNNY-VERDICT: Agreed

(3a 4 + 3b 6 + 3c 1 + 3d 1 + 3e 1 + 3f 8 = 21.)

---

## 4. QUESTIONS (4)

**Q1 — `rule:gain-fixed-life` / `rule:fixed-lifegain` (same concept, two
labels from different free-clusters, DF up to 326).**
Both are bare "You gain N life" restatements with no functional
specificity beyond the rider itself — genericness parallels the
batch-1-killed `card-draw-payoff`. But batch 1 also *kept*
`rule:burst-draw` despite similar genericness ("a real deckbuilding
concept; watch it in batch 2"). Is plain fixed lifegain the same kind of
real, trackable archetype (keep, dedupe the two labels into one axis), or
noise that should follow the `card-draw-payoff` precedent instead (kill
both)?
→ RULE: keep-as-one-axis / kill-both: Merge them

**Q2 — `rule:sacrifice-for-creature-token` vs. existing
`rule:free-sacrifice-outlet`.**
Members (Canonized in Blood, Temur Monument) pay real mana costs alongside
the sacrifice — they don't fit the existing axis's definition, which is
explicitly scoped to *free* (no-mana-cost) sac outlets. Redefine
`free-sacrifice-outlet` to drop the "free" qualifier and absorb this (one
broader axis), or keep this as its own sibling axis (respects the ratified
"at no mana cost" boundary as written)?
→ RULE: broaden-and-merge / keep-separate: keep-separate

**Q3 — `rule:draft-from-spellbook` (2: Key to the Archive, March Toward
Perfection).**
"Spellbook" drafting is a defined, recurring game-rules concept tied to
specific cards, but it isn't a CR-defined keyword with its own reminder
text the way Kicker/Venture are. Is this keyword/mechanism-adjacent
territory (kill + ledger, same as Kicker/Venture above), or a real,
useful archetype tag (deckbuilding-relevant: "these grant bonus card
selection via a spellbook")?
→ RULE: keep / kill-and-ledger: kill-and-ledger

**Q4 — `rule:grants-controller-hexproof` (2): mixed coherence within the
axis itself.**
Sigarda, Font of Blessings' member ("Other permanents you control have
hexproof") is arguably Q1 engine-redundant territory (mass permanent-level
keyword grant, same as batch-1-killed `grants-hexproof`). Teyo, the
Shieldmage's member ("You have hexproof") is genuinely different —
*player*-level hexproof, which the engine's `granted_keyword` dimension
(permanent-scoped) can't see at all. Narrow the axis to player-level only
(reassign Sigarda's instance to Q1-kill territory), or keep both under one
axis as written?
→ RULE: narrow-to-player-only / keep-as-is: narrow-to-player-only

---Stop

## 5. OTHER-LANE PROMOTIONS

**None proposed this batch.** Sampled the full size range of the 1,051
token groups (n=38 down to n=4, several hundred groups) — every one
inspected is a generic 2-token-overlap collision spanning unrelated
mechanics (e.g. `[count/scal]` groups Green Mana Battery's mana-counter
conversion with Zaxara's token-scaling with Armageddon Clock's damage
counters — three unrelated payoffs sharing only the words "count" and
"scal[e]"). This matches the protocol's own prediction that raw OTHER-lane
rate is method-inflated; batch 2's real multi-card families were already
captured via `lane=codebook` hits (512 instances) and exact-full-label-set
free clustering (the 85 new candidates). See §7 for a tooling
recommendation.

---

## 6. OVERRIDE SPOT-CHECK — verify these 30 before trusting the rest

Fixed seed 20260720 (= 20260718 + batch 2), drawn from the 145 confident
calls (KEEP/KILL/MERGE; the 4 QUESTIONs excluded), via
`random.seed(20260720); random.sample(confident_calls, 30)`. Every quote
below is verbatim from the card's attached oracle text in
`review/batch-2-enriched.json` (already passed the automated
evidence-quote-or-discard gate; spot-checked again here by inspection).
Check each verdict against the card text. If more than ~1 is wrong,
distrust the lanes and tell me — loudly.

| Axis | Verdict | Sample member | Evidence quote |
|---|---|---|---|
| rule:land-fetch-to-battlefield | KEEP | Scampering Surveyor | "When this creature enters, search your library for a basic land card or Cave ca…" |
| rule:cleanup-counters-on-leaving-battlefield | KEEP | Corrosion | "When this enchantment leaves the battlefield, remove all rust counters from all…" |
| rule:cast-trigger-tutor-to-battlefield | KEEP | Garruk, Caller of Beasts | "Whenever you cast a creature spell, you may search your library for a creature …" |
| rule:restricted-cast-timing-window | KILL | Blood Frenzy | "Cast this spell only before the combat damage step." |
| rule:mill-self-cards | KEEP | Cathartic Adept | "{T}: Target player mills a card." |
| rule:death-trigger-mass-debuff | KEEP | Death's-Head Buzzard | "When this creature dies, all creatures get -1/-1 until end of turn." |
| rule:untaps-target-land | KEEP | Fiery Gambit | "untap all lands you control" |
| rule:enters-tapped | KEEP | Adagia, Windswept Bastion | "This land enters tapped." |
| rule:mass-untap-and-haste-stolen-creatures | KEEP | Rowan, Fearless Sparkmage | "Untap them. They gain haste until end of turn." |
| rule:targeted-destruction | KEEP | Active Volcano | "Destroy target blue permanent." |
| rule:etb-destroy-artifact-enchantment | KEEP | Harmonic Sliver | "When this permanent enters, destroy target artifact or enchantment." |
| rule:life-total-reset | KEEP | Beyond Booster Blitz | "Players start at 5 life" |
| rule:doubles-etb-triggers | KEEP | Echoes of Eternity | "that ability triggers an additional time" |
| rule:aura-static-pt-buff | KILL | Aquitect's Defenses | "Enchanted creature gets +1/+2." |
| rule:transforms-on-graveyard-threshold | KEEP | Exdeath, Void Warlock // Neo Exdeath, Dimension's End | "At the beginning of your end step, if there are six or more permanent cards in …" |
| rule:alternate-win-condition | KEEP | Battle of Wits | "if you have 200 or more cards in your library, you win the game." |
| rule:copies-cast-instant-sorcery | MERGE → rule:triggers-on-cast-instant-sorcery | Invasion of Arcavios // Invocation of the Founders | "Whenever you cast an instant or sorcery spell from your hand, you may copy that…" |
| rule:land-becomes-creature | MERGE → rule:animates-land-into-creature | Faerie Conclave | "{1}{U}: This land becomes a 2/1 blue Faerie creature with flying until end of t…" |
| rule:doubles-counter-placement | KEEP | Aragorn, Hornburg Hero | "Whenever a renowned creature you control deals combat damage to a player, doubl…" |
| rule:grants-extra-turn | KEEP | The Legend of Kuruk // Avatar Kuruk | "Exhaust — Waterbend {20}: Take an extra turn after this one." |
| rule:etb-scry | KEEP | Elrond, Lord of Rivendell | "Whenever Elrond or another creature you control enters, scry 1." |
| rule:rhystic-tax | KEEP | Brine Seer | "Counter target spell unless its controller pays {1} for each card revealed thi…" |
| rule:power-scales-with-creature-count | KEEP | Exdeath, Void Warlock // Neo Exdeath, Dimension's End | "Neo Exdeath's power is equal to the number of permanent cards in your graveyard." |
| rule:copies-cast-spell | KEEP | Taigam, Master Opportunist | "Whenever you cast your second spell each turn, copy it" |
| rule:burst-draw | KEEP | A-Wizard Class | "When this Class becomes level 2, draw two cards." |
| rule:cast-trigger-card-draw | KEEP | Archmage Emeritus | "Magecraft — Whenever you cast or copy an instant or sorcery spell, draw a card." |
| rule:activated-grants-self-unblockable | MERGE → rule:grants-unblockable | Daring Saboteur | "{2}{U}: This creature can't be blocked this turn." |
| rule:etb-with-counters | KEEP | Lattice Library | "This enchantment enters with X study counters on it." |
| rule:death-trigger-token-creation | KEEP | Golgari Germination | "Whenever a nontoken creature you control dies, create a 1/1 green Saproling cre…" |
| rule:targeted-exile | KEEP | Astral Confrontation | "Exile target creature." |

**Result: 0 reversals expected (self-check; Captain's actual check
governs).**

---

## 7. Batch-3 feedback (fold into consolidation tooling + SYNTH prompt)

1. **Fix the single-card-corroboration gap.** `foundry_consolidate.py`
   should track distinct `oracle_id` count per cluster, not just instance
   count, and flag (or auto-route to a lower-confidence review lane)
   any free-lane cluster where `n >= 2` but `distinct_cards == 1`. Five
   batch-2 candidates slipped through as if corroborated when they were
   really one card's two abilities.
2. **OTHER-lane token grouping (partial 2-token overlap) is producing
   near-zero signal now that two-lane labeling is live** — consider
   dropping it from the digest artifact (or shrinking it to just a count)
   in batches where `lane=codebook` hit rate is already high, freeing
   digest space for the axes themselves.
3. **SYNTH prompt: two-lane labeling worked well (0/512 anomalies) — keep
   as-is.** No prompt-shape changes needed from this batch's evidence.
4. Batch-3 hand-picked targeting: the four QUESTION axes (once ruled),
   `rule:sacrifice-for-creature-token` if kept separate (Q2), and continued
   confirmation of the newly-grown large axes (`creates-creature-token`,
   `enters-tapped`, `modal`, `targeted-destruction`, `targeted-exile`) to
   validate they stay coherent as they keep growing toward the schema
   pass.

---

## 8. Ledger candidates carried forward

Kicker (3 instances), Venture into the Dungeon, Daybound/Nightbound (2
instances), Saga-chapter-transform templating. Draft-from-spellbook
pending Q3's ruling — add if Captain rules kill-and-ledger.

---

## 9. Verification

- Verdict count vs. axis count: 149 axes total = KEEP 112 (64 existing
  confirmations + 48 new candidates, where `rule:tutor-basic-land-to-hand`
  and `rule:mana-activated-pump-self` count as KEEP since they are the
  surviving/receiving slug in M2 and M9 respectively) + KILL 21 + MERGE 12
  (source axes being absorbed away) + QUESTION 4 = 149. Verified
  programmatically against the full 149-slug list, one verdict per slug,
  zero duplicates, zero omissions.
- Every MERGE target is named: 10 source slugs merge into 9 pre-existing
  codebook axes (M1 → `animates-land-into-creature`; M3 → `free-sacrifice-outlet`;
  M4 → `grants-unblockable`, 2 source slugs; M5 → `cost-reduction`;
  M6 → `x-scales-with-permanent-count`; M7 → `scales-mana-by-count`;
  M8 → `direct-damage-any-target`; M10 → `triggers-on-cast-instant-sorcery`;
  M11 → `free-cast`); 2 source slugs merge into a sibling new-candidate
  slug that itself carries a KEEP verdict (M2's `etb-tutor-basic-land-to-hand`
  → `tutor-basic-land-to-hand`; M9's `activated-pump-ability` →
  `mana-activated-pump-self`). 10 + 2 = 12 total MERGE source slugs.

---

**STOP.** File written to `docs/TRIAGE-BATCH-2.md`. Captain: annotate per
the protocol convention (edit `VERDICT:` lines, fill `-> RULE:` blanks for
Q1–Q4, add `## CAPTAIN-AUTHORED` blocks for any new axes), then run
`/triage-emit 2` when done.
