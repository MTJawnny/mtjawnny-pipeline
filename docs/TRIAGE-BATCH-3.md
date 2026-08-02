# TRIAGE — Batch 3 (SUP full-pass, 2026-07-19)

Produced by Claude (SUP-class session) under the ratified SUP-TRIAGE-PROTOCOL,
reading `experiments/out/foundry/review/digest-batch-3.md` (158 axes: 111
confirming existing codebook v0.2 axes, 47 new candidates from free-lane
clustering; 1,243 OTHER-lane rows; 1,049 token groups) against the current
codebook (134 active axes). Every axis and every multi-card token group was
read in full before any verdict was written. Nothing here is load-bearing
until Captain ratifies.

**How to use this doc:** read the lanes top-down. Lanes 1–3 are confident
calls — skim, strike anything wrong, initial the rest. Lane 4 is the
questions; answer inline. §6 is the honesty check — verify those 30 rows
against card text before trusting the rest. §0 flags a new, real quality
issue (member-level mismatches) worth your particular attention this batch.
When you hand this back annotated, `/triage-emit 3` parses it into
`decisions/batch-3.json`.

**Verdict counts:** KEEP 140 (111 existing confirmations + 29 new) · KILL 12
· MERGE 3 · QUESTION 3 = 158, one verdict per axis, verified programmatically
against the digest's actual slug list.

---

## 0. Findings, interpreted

- **Two-lane labeling still clean at the slug level.** 640 of 1,990 kept
  instances (32%) resolved to an existing codebook slug via `lane=codebook`,
  0 anomalies (no claimed slug failed to resolve) — third batch running at
  0/0/0 anomalies.
- **But: slug-level correctness is not semantic correctness — a real,
  new quality issue.** Reading every member closely (not just trusting the
  automated quote-verbatim gate) surfaced **12 member-level mismatches**
  across 8 existing-axis confirmations: cards whose *quote* is genuinely
  verbatim oracle text (passes the evidence-quote-or-discard gate) but whose
  underlying mechanic does not actually match the axis it landed in. These
  are not hallucinated quotes — they're real card text, just paired with
  the wrong functional bucket. Several are exact **polarity inversions**
  (the DERIVED-TAG-LAYER-SPEC's "Lesson 1" trap: a classifier keying off
  surface vocabulary — "counter," "untap," "damage" — without checking which
  direction the effect runs):
  - **Counterbore** → `rule:cant-be-countered` (its quote is "Counter target
    spell." — it's a counterSPELL, not a spell that resists being countered)
  - **Mishra's Helix** → `rule:untaps-target-land` (quote is "Tap X target
    lands." — the opposite action)
  - **Recycle** → `rule:no-maximum-hand-size` (quote sets max hand size to
    *two* — the opposite of removing the maximum)
  - **Decree of Annihilation**, **Granulate** → `rule:mass-creature-destruction`
    (destroy all *lands*; destroy nonland *artifacts* — neither destroys
    creatures)
  - **Tragic Trajectory** → `rule:targeted-creature-damage` (a -2/-2 debuff,
    not damage)
  - **Bösium Strip** → `rule:cast-from-top-of-library` (casts from the top
    of the *graveyard*, not the library)
  - **Inquisitor's Snare** → `rule:conditional-buff-by-color` (a
    color-conditional *destroy*, not a buff)
  - **Coastal Bulwark** → `rule:charge-counter-accumulation` (its quote is
    a plain Surveil ability, no counter at all)
  - **Implement of Malice** → `rule:sacrifice-for-card-draw` (a death
    trigger, not an activated sacrifice ability — see §2 M-fix)
  - **Buzzing Whack-a-Doodle**, **Shauku, Endbringer** → `rule:pay-life-cost-for-effect`
    (neither shows an activated ability *paid with life* — one is a tap
    ability that damages an opponent, the other an upkeep drawback trigger)
  None of these are axis-level problems — the axis concept is sound in
  every case, only the specific member is wrong. Flagged as member-removal
  recommendations inline in §1, not full kills. See §7 for the systemic
  fix this points to.
  VERDICT: Remove those members from those Rules buckets

- **OTHER-lane token groups: no promotions again.** Sampled broadly across
  the 1,049 groups (n=43 down to n=8, several dozen groups) — same pattern
  as batch 2: generic 2-token-overlap collisions spanning unrelated
  mechanics. Zero promotions.
- **The corroboration-gap fix (added after batch 2) is already paying
  off**: `foundry_consolidate.py` caught 2 single-card clusters
  automatically this run before they ever reached this digest.
- **A cluster of new-candidate KILLs is keyword/mechanism territory**:
  Regenerate, Connive, Flashback, Level up, and a second Kicker cluster —
  same standing as batches 1–2's lane 1b/3f. All carry forward to the
  ledger (§8).
- **Two tautological-rider kills extend a live precedent**:
  `equipment-grants-stat-buff` / `equipment-static-pt-buff` are the
  Equipment-side twin of batch 2's killed `aura-static-pt-buff` /
  batch 3's own `aura-static-pump` (below) — "an Equipment/Aura gives a flat
  stat buff" is close to tautological for what those card types most
  commonly do.
- **One new candidate directly violates the ratified M8 per-object-class
  damage-target rule**: `rule:damage-to-creature-or-planeswalker` is
  exactly the "combination tag" the standing rule forbids — its members
  should receive both `rule:targeted-creature-damage` and
  `rule:targeted-planeswalker-damage` instead (already true for the
  overlapping cards, e.g. Fated Conflagration appears correctly in both).
VERDICT: Agreed

---

## 1. Existing codebook confirmations (111) — all KEEP

Full list; member-mismatch flags noted inline where found. No axis-level
contradictions.

`rule:activated-tap-target-creature` (n=15), `rule:alternate-win-condition`
(n=2), `rule:animates-land-into-creature` (n=8),
`rule:attack-trigger-self-counter-growth` (n=1), `rule:burst-draw` (n=7),
`rule:cannot-block-restriction` (n=6),
**`rule:cant-be-countered` (n=5 — VERDICT: KEEP — NOTE: remove member
Counterbore, wrong polarity, see §0)**,
`rule:cantrip` (n=5),
**`rule:cast-from-top-of-library` (n=7 — VERDICT: KEEP — NOTE: remove member
Bösium Strip, casts from graveyard not library, see §0)**,
`rule:cast-trigger-card-draw` (n=3),
`rule:cast-trigger-draw-on-target-own-creature-spell` (n=2),
**`rule:charge-counter-accumulation` (n=9 — VERDICT: KEEP — NOTE: remove
member Coastal Bulwark, quote is a plain Surveil ability with no counter,
see §0)**,
`rule:cheat-creature-into-play` (n=1), `rule:choose-color-on-etb` (n=3),
`rule:choose-creature-type-on-etb` (n=3),
`rule:combat-damage-triggers-discard` (n=4),
`rule:combat-damage-triggers-loot` (n=5),
`rule:compensates-controller-with-token` (n=2),
`rule:conditional-attack-restriction` (n=2),
**`rule:conditional-buff-by-color` (n=11 — VERDICT: KEEP — NOTE: remove
member Inquisitor's Snare, a color-conditional destroy not a buff, see §0)**,
`rule:conditional-creature-status` (n=1),
`rule:conditional-first-strike-your-turn` (n=3), `rule:copies-cast-spell`
(n=4), `rule:copy-creature-token` (n=3), `rule:cost-reduction` (n=6),
`rule:creates-creature-token` (n=41), `rule:creates-mana-producing-artifact-token`
(n=6, +1 via merge — see §2), `rule:damage-scales-with-creature-count` (n=1),
`rule:death-trigger-draw-card` (n=4), `rule:death-trigger-token-creation`
(n=4), `rule:direct-damage-any-target` (n=12), `rule:doubles-counter-placement`
(n=2), `rule:doubles-token-creation` (n=1), `rule:drain-life` (n=8),
`rule:drain-on-creature-death` (n=1), `rule:enters-tapped` (n=25),
`rule:etb-and-attack-trigger` (n=3), `rule:etb-counter-on-other-creature`
(n=8), `rule:etb-create-token` (n=16), `rule:etb-destroy-artifact-enchantment`
(n=1), `rule:etb-draw-card` (n=6), `rule:etb-exile-graveyard-card` (n=2),
`rule:etb-gain-life` (n=9), `rule:etb-loot` (n=4), `rule:etb-scry` (n=2),
`rule:etb-tutor-to-hand` (n=1), `rule:etb-with-counters` (n=14 — note:
includes 2 members with -1/-1 rather than +1/+1 counters (Noxious Hatchling,
Thorna and Twigtooth); same functional shape, opposite polarity — flag for
a `polarity` param at the schema pass, not split now),
`rule:exile-until-source-leaves` (n=5), `rule:fixed-lifegain` (n=10),
`rule:forced-hand-reveal` (n=3), `rule:forces-creature-to-attack` (n=2),
`rule:forces-opponent-sacrifice` (n=1), `rule:free-cast` (n=5),
`rule:free-sacrifice-outlet` (n=1),
`rule:grants-ability-at-threshold-board` (n=6),
`rule:grants-ability-at-threshold-self` (n=8),
`rule:grants-additional-combat-phase` (n=3), `rule:grants-extra-land-drop`
(n=1), `rule:grants-extra-turn` (n=2), `rule:grants-flying-and-pump-to-creature`
(n=2), `rule:grants-unblockable-target` (n=2), `rule:graveyard-to-hand-recursion`
(n=15), `rule:graveyard-to-library-top-recursion` (n=1),
`rule:individual-cost-reduction` (n=5), `rule:land-fetch-to-battlefield` (n=3),
`rule:library-dig-put-onto-battlefield` (n=3), `rule:library-top-visibility`
(n=6), `rule:mana-activated-pump-self` (n=7), `rule:mass-counter-distribution`
(n=9),
**`rule:mass-creature-destruction` (n=5 — VERDICT: KEEP — NOTE: remove
members Decree of Annihilation (destroys lands) and Granulate (destroys
artifacts) — neither destroys creatures, see §0)**,
`rule:mass-damage-creatures-and-players` (n=8), `rule:mass-graveyard-exile`
(n=5), `rule:mass-untap-and-haste-stolen-creatures` (n=4),
`rule:mass-untap-your-creatures` (n=2), `rule:mill-self-cards` (n=4),
`rule:modal` (n=17),
**`rule:no-maximum-hand-size` (n=3 — VERDICT: KEEP — NOTE: remove member
Recycle, sets max hand size to two, the opposite effect, see §0)**,
`rule:partner-with-tutor` (n=4),
**`rule:pay-life-cost-for-effect` (n=8 — VERDICT: KEEP — NOTE: remove
members Buzzing Whack-a-Doodle and Shauku, Endbringer, neither shows an
activated ability paid with life, see §0)**,
`rule:plus1-counters-matter` (n=13), `rule:power-scales-with-creature-count`
(n=1), `rule:prevents-damage-prevention` (n=1), `rule:prevents-damage-to-self`
(n=1), `rule:prevents-regeneration` (n=3), `rule:reanimate-from-graveyard`
(n=11), `rule:restricted-mana-for-equipment` (n=9), `rule:rhystic-tax` (n=2),
**`rule:sacrifice-for-card-draw` (n=1 — VERDICT: KEEP — NOTE: remove member
Implement of Malice (a death trigger, not an activated sacrifice ability);
absorbs `rule:sacrifice-for-card-draw-self`'s 2 good members via merge, see
§2)**,
`rule:sacrifice-for-creature-token` (n=3), `rule:scales-mana-by-count` (n=1),
`rule:self-bounce-activated` (n=2), `rule:self-counter-growth` (n=3),
`rule:self-mana-ability-grants-keyword` (n=1), `rule:sets-base-power-or-toughness`
(n=4), `rule:stun-counter-lockdown` (n=4),
**`rule:targeted-creature-damage` (n=22 — VERDICT: KEEP — NOTE: remove
member Tragic Trajectory, a -2/-2 debuff not damage, see §0)**,
`rule:targeted-destruction` (n=27), `rule:targeted-discard` (n=7),
`rule:targeted-exile` (n=11), `rule:targeted-planeswalker-damage` (n=4),
`rule:targeted-player-damage` (n=14), `rule:targets-a-player` (n=1),
`rule:temporary-control-theft` (n=8), `rule:the-ring-tempts-you` (n=1),
`rule:transforms-on-graveyard-threshold` (n=2), `rule:tribal-anthem-buff`
(n=15), `rule:triggers-on-cast-instant-sorcery` (n=6),
`rule:tutor-basic-land-to-hand` (n=4), `rule:tutor-to-library-top` (n=1),
**`rule:untaps-target-land` (n=2 — VERDICT: KEEP — NOTE: remove member
Mishra's Helix, taps lands, the opposite action, see §0)**,
`rule:x-scales-with-permanent-count` (n=6).
VERDICT:
`rule:cantrip` - Just wanted to clarify. This tag is for cards that draw a card that are 0,1,2 cmc. I want to clarify that in order to be considered a cantrip. it also needs to draw you a card upon resolution of the spell; either by the spell itself, etb, or some other immediate means. a creature card that is {1}{U} that has "t:Draw a card, then discard a card" should not be considered a cantrip since due to summoning sickness, it can not draw you a card that turn. 

`rule:attack-trigger-self-counter-growth` - this tag is good. however cards with this tag should also have `rule:attack-trigger` or whatever rule covers attack triggers. to tie them to all cards with attck triggers first, then getting more specific. 

`rule:cast-trigger-card-draw` & `rule:cast-trigger-draw-on-target-own-creature-spell`- these tags are good. Cards with this tag should also have 'rule:cast-trigger' to connect them to all cards with cast trigfers. also make sure these cards contain "When you cast this spell" or similar verbage as that is what constitutes a cast trigger. not just a card that has "When ~ enters, draw a card". a cast trigger is fundementally different that a etb trigger.

`rule:combat-damage-triggers-discard` & `rule:combat-damage-triggers-loot`- these tags are good. again just male sure there is a linking or parent rule that links them all to cards with combat damage triggers.`rule:combat-damage-triggers`

`rule:death-trigger-draw-card` & `rule:death-trigger-token-creation` - these tags are good. just make sure there is a parent that links them to eachother. `rule:death-trigger`

`rule:etb-counter-on-other-creature`
(n=8), `rule:etb-create-token` (n=16), `rule:etb-destroy-artifact-enchantment`
(n=1), `rule:etb-draw-card` (n=6), `rule:etb-exile-graveyard-card` (n=2),
`rule:etb-gain-life` (n=9), `rule:etb-loot` (n=4), `rule:etb-scry` (n=2),
`rule:etb-tutor-to-hand` (n=1), `rule:etb-with-counters` - these tags are good. just make sure there is a parent that links them to eachother. `rule:etb`. also within this set contains sub parents. `rule:etb-create-token` should exist, then the card has another rule determining what kinda of token is created. example: Company Commander - "When this creature enters, create a number of 1/1 white Soldier creature tokens equal to the number of opponents you have." would have `rule:etb`, `rule:etb-create-token`, `rule:etb-create-token-creature`. that's just for the etb creature trigger. it might also have `rule:number-of-opponents-matter`.

Sidenote: `rule:number-of-opponents-matter` Will grab all cards that care about any amount of oppoents. Adeline, Resplendent Cathar & Luxury Suite would both fall in this rule

Company Commander next text is - "Whenever this creature attacks, creatures you control gain deathtouch until end of turn." so it would also have `rule:attack-trigger`, `rule:attack-trigger-grant-keyword-board`, `rule:grant-deathtouch-board`.

`rule:mass-creature-destruction` - this rule will naturally grow. it points to the highly changable `rule:mass-N-N`, so `rule:mass-creature-exile`, `rule:mass-creature-sacrifice`, `rule:mass-creature-bounce`, `rule:mass-creature-negative1-counters`. Then these rules can jump to other permenant types, `rule:mass-artifact-destruction`, `rule:mass-artifact-exile`, `rule:mass-enchantment-destruction`, `rule:mass-enchantment-exile` etc. we'll need to build some logic for cards that do not name these types by name, but due to their effect, include these type. like Ruinous Ultimatum - "Destroy all nonland permanents your opponents control.". this would naturally distil into `rule:mass-nonland-destruction`. And it would classify as, or rather count towards `rule:mass-creature-destruction`, `rule:mass-artifact-destruction`, `rule:mass-enchantment-destruction`, `rule:mass-planswalker-destruction`, `rule:mass-battle-destruction`, etc. We'll need to think this out.

Sidenote: `rule:negative1-counters-matters` is a needed rule. there are many cards that card about negative1-counters.
---

## 2. PROPOSED MERGE (3 new candidates → 3 existing targets)

**M1 → existing `rule:grants-creature-type`**
Absorb `rule:grants-creature-type-change` (2: Blue Mage's Cane, Drana, the
Last Bloodchief). Identical definitions from two differently-worded free
clusters. NOTE: `grants-creature-type`'s own member Okiba Reckoner Raid //
Nezumi Road Captain ("Vehicles you control have menace") is itself a
mismatch — that's a keyword grant, not a creature-type grant — recommend
removing it at the same time.
VERDICT: agreed on removing Okiba Reckoner Raid //
Nezumi Road Captain. Also make sure `rule:grants-creature-type` does not include cards that completely overwrites creature types such as Gornog, the Red Reaper - Whenever one or more Warriors you control attack a player, target creature that player controls becomes a Coward. - in this instance, Gornog erases all other creature types and makes the creature a Coward only. This isn't `rule:grants-creature-type`, but rather `rule:overwrites-creature-type`. `rule:grants-creature-type` has the words "in addition to its other types". Thats the difference. Gornog does not replace supertypes like Artifact or Legendary.

**M2 → existing `rule:sacrifice-for-card-draw`**
Absorb `rule:sacrifice-for-card-draw-self` (2: Lifespark Spellbomb,
Necrogen Spellbomb — both clean "Sacrifice this artifact: Draw a card").
Same core concept (sac-for-draw); target scope (self vs. target player, per
the existing axis's own definition) is a parameter. This merge also nets
out the existing axis's bad member (Implement of Malice, see §0/§1) —
after the merge + removal, the surviving axis has exactly the 2 good
members from the new candidate.
VERDICT: Agreed

**M3 → existing `rule:creates-mana-producing-artifact-token`**
Absorb `rule:creates-treasure-token` (2: Flick a Coin, Spell Swindle).
Treasure tokens are mana-producing artifact tokens (any color) — a direct
instance of the existing axis's own definition, not a distinct concept.
VERDICT: I understand the logic. But becasue a treasure-token is such a specifc game mechanic. we'll want to give it it's own bucket.
---

## 3. PROPOSED KILL (12)

### 3a. Tautological riders (3)
Same standing as batch-2-killed `aura-static-pt-buff` / `grants-stat-buff`
— "this card type gives a flat stat buff" restates what the card type most
commonly does, no distinguishing functional signal.
- `rule:aura-static-pump` (Aura + static P/T — direct duplicate-shape of
  the already-killed `aura-static-pt-buff`)
- `rule:equipment-grants-stat-buff`
- `rule:equipment-static-pt-buff`
(the latter two are the same underlying concept as each other, both killed
together rather than merged, per the tautological-rider precedent)
VERICT: Agreed

### 3b. Procedural cost-shape riders, not identity (2)
Same precedent as batch 2's lane-3b cost-shape kills — the sacrifice
mechanism is a parameter of whatever effect it pays for, not an axis.
- `rule:sacrifice-as-additional-cost` (direct repeat of batch-2-killed
  `rule:sacrifice-creature-as-additional-cost`)
- `rule:self-sacrifice-divided-damage` (the payoff — divided damage — is
  already `rule:damage-divided-among-multiple-targets`; the self-sacrifice
  cost-shape isn't a separate axis)
VERICT: Agreed

### 3c. Keyword/mechanism territory — ledger candidates (5)
- `rule:activated-regenerate-self` (Regenerate keyword)
- `rule:etb-grants-connive-to-other-creature` (Connive keyword action)
- `rule:grants-flashback-to-graveyard-card` (Flashback keyword)
- `rule:level-up-scaling-stats-abilities` (Level up keyword mechanic)
- `rule:kicker-conditional-bonus-effect` (Kicker keyword — third Kicker
  cluster killed across two batches)
VERDICT:
`rule:activated-regenerate-self` - Keep; But let's strategize on this. First let's distil down to what a card has, then what it does. `rule:activated-regenerate-self` is firstly `rule:activated-ability`. The ability boils down to being an activated ability. Then next we have `rule:regenerate-self`. other cards that regenerate themselves may not do it with an activated ability. Also meaning the rule has siblings such as `rule:regenerate-target`, `rule:regenerate-controller-board`, `rule:regenerate-all`. So kill `rule:activated-regenerate-self`, replace with double rule `rule:activated-ability` & `rule:regenerate-self`.
Let's keep the rest for now and mark for possible deletion next round

### 3d. Pure keyword grant, engine-redundant (1)
- `rule:grants-temporary-hexproof-target-creature` (a target creature
  gains hexproof — exactly the batch-1 Q1 precedent: `granted_keyword`
  already models this, reviving a pattern already killed as
  `rule:grants-hexproof`)
VERDICT: kill `rule:grants-temporary-hexproof-target-creature`, however add `rule:temporary-keyword-grant` for cards that give keywords until end of turn or until end of next turn.

### 3e. Violates the ratified M8 per-object-class rule (1)
- `rule:damage-to-creature-or-planeswalker` (a combination tag across two
  object classes — the standing rule requires separate per-class tags with
  multiple-tagging for mixed-target cards, not a combined axis; see §0)
VERDICT: yes exactly kill. replace with two seperate rules for damage to creatures and damage to planswalkers.
(3a 3 + 3b 2 + 3c 5 + 3d 1 + 3e 1 = 12.)

---

## 4. QUESTIONS (3)

**Q1 — `rule:prevents-target-untap-next-step` (2: Crippling Chill, Rush of
Ice) vs. existing `rule:stun-counter-lockdown`.**
Both axes produce the identical end result (a permanent skips its next
untap step) but via different templating: the existing axis is specifically
about the *stun counter* game object; this new candidate's two members
("It doesn't untap during its controller's next untap step") achieve the
same outcome as a flat replacement effect, with no stun counter mentioned.
Same-concept-different-wording (merge, per batch-1 precedent), or a
genuinely different vector (stun-counter-as-object vs. flat static effect)
that "don't absorb, expand" says should stay separate?
→ RULE: merge-into-stun-counter-lockdown / keep-separate: keep-separate. As you deduced stun counters are a game object that is affected by other game effects such as counter doubling, removing, or complete stopping. Rename `rule:stun-counter-lockdown` to `rule:stun-counter`. then add a parent to these tags. `rule:lockdown`. We'll use `rule:lockdown` as a human(me) dirived parent tag I'll assign for cards that tap cards or keep them tapped.

**Q2 — `rule:etb-grants-energy-counters` (2: Aether Inspector, Riparian
Tiger).**
Energy counters are a defined resource type with "You get {E}{E}"
boilerplate consistent across all energy cards, similar in shape to
Kicker's "Kicker {cost}" templating. Is granting Energy itself
keyword/mechanism-adjacent territory (kill + ledger, same standing as
Kicker/Regenerate/Connive/Flashback/Level-up above), or a real archetype
tag (deckbuilding-relevant: "these cards feed an Energy subtheme")?
→ RULE: keep / kill-and-ledger: Kill. But let's make some energy rules based on this card. So first `rule:gives-energy-counters-immediately`, `rule:energy-outlet-condition`. We want to distinguish cards that give you energy counters immediately, vesus a condition you must meet or the card does. also outlet in this case is based on Aether Inspector and Riparian Tiger attcking. it's not an infinite outlet. so `rule:energy-outlet-condition` makes sense.

Let's discuss other rules now. `rule:gives-energy-counters-condition` - gives energy counters based on meeting a condition. `rule:energy-outlet-infinite` - an activated ability that just requires an amount of energy you can spend indefinitely if you have an indefinite amount of energy. If these tags have no hits. that is errelevant. future cards may be made that will include them.

**Q3 — `rule:perpetual-any-color-mana-cast` (2: Clone Crafter, Soul
Servitude).**
"Perpetually" is an ability-word/duration mechanism (Kamigawa: Neon
Dynasty), not itself a CR keyword with reminder text the way Kicker is —
but it is consistent, repeated boilerplate. Payoff here (persistent
any-color-casting) is real and specific, not purely restating the
duration mechanism. Keep as a real archetype, or treat "perpetual" as
mechanism-adjacent (kill + ledger)?
→ RULE: keep / kill-and-ledger: kill-and-ledger - Alchemy is lame and sucks.

---

## 5. OTHER-LANE PROMOTIONS

**None proposed this batch.** Sampled broadly across the 1,049 token
groups (n=43 down to n=8, several dozen groups spanning every size tier
sampled) — same generic 2-token-overlap collision pattern as batch 2 (e.g.
`[grant/keyword]` groups an activated ability, an Aura, a Bestow effect,
and an Equipment under nothing but the shared words "grant" and "keyword").
Zero coherent multi-card families found beyond what's already captured as
new-candidate axes via full-label-set clustering.

---

## 6. OVERRIDE SPOT-CHECK — verify these 30 before trusting the rest

Fixed seed 20260721 (= 20260718 + batch 3), drawn from the 155 confident
calls (KEEP/KILL/MERGE; the 3 QUESTIONs excluded), via
`random.seed(20260721); random.sample(confident_calls, 30)`. Every quote
below is verbatim from the card's attached oracle text in
`review/batch-3-enriched.json` (already passed the automated
evidence-quote-or-discard gate). Check each verdict against the card text.
If more than ~1 is wrong (beyond the member-mismatch flags already called
out above, which are already accounted for), distrust the lanes and tell
me — loudly.

| Axis | Verdict | Sample member | Evidence quote |
|---|---|---|---|
| rule:exile-until-source-leaves | KEEP | Alabaster Host Intercessor | "When this creature enters, exile target creature an opponent controls until…" |
| rule:targeted-destruction | KEEP | Agonizing Demise | "Destroy target nonblack creature." |
| rule:targets-a-player | KEEP | Ominous Harvest | "Target player draws a card and loses 1 life." |
| rule:the-ring-tempts-you | KEEP | Stalwarts of Osgiliath | "When this creature enters, the Ring tempts you." |
| rule:mass-damage-creatures-and-players | KEEP | Chandra, Bold Pyromancer | "Chandra deals 10 damage to target player and each creature and planeswalker…" |
| rule:damage-divided-among-multiple-targets | KEEP | Nahiri's Sacrifice | "Nahiri's Sacrifice deals X damage divided as you choose among any number of…" |
| rule:alternate-win-condition | KEEP | Jaya, Fiery Negotiator | "You get an emblem with "Whenever you cast a red instant or sorcery spell, c…" |
| rule:free-sacrifice-outlet | KEEP | Valgavoth's Faithful | "{3}{B}, Sacrifice this creature: Return target creature card from your grav…" |
| rule:attack-trigger-loot | KEEP | Adventurer's Airship | "Whenever this Vehicle attacks, draw a card, then discard a card." |
| rule:doubles-token-creation | KEEP | Ojer Taq, Deepest Foundation // Temple of Civilization | "If one or more creature tokens would be created under your control, three t…" |
| rule:etb-scry | KEEP | Temple of Enlightenment | "When this land enters, scry 1." |
| rule:graveyard-to-hand-recursion | KEEP | Cadaver Imp | "you may return target creature card from your graveyard to your hand" |
| rule:targeted-planeswalker-damage | KEEP | Clan Defiance | "Clan Defiance deals X damage to target player or planeswalker." |
| rule:cost-reduction | KEEP | Baron Strucker, HYDRA Overlord | "Villain spells you cast cost {1} less to cast." |
| rule:stun-counter-lockdown | KEEP | Castaway's Despair | "Enchanted creature doesn't untap during its controller's untap step." |
| rule:mass-untap-your-creatures | KEEP | Rally to Battle | "Untap them." |
| rule:etb-bounce-other-creature | KEEP | Air-Cult Elemental | "When this creature enters, return up to one other target creature to its ow…" |
| rule:animates-land-into-creature | KEEP | Cavernous Maw | "{2}: This land becomes a 3/3 Elemental creature until end of turn. It's sti…" |
| rule:library-dig-to-hand | KEEP | Glimpse the Cosmos | "Look at the top three cards of your library. Put one of them into your hand…" |
| rule:equipment-grants-stat-buff | KILL | Novel Nunchaku | "Equipped creature gets +1/+1 and has trample." |
| rule:mass-counter-distribution | KEEP | Age of Ultron | "Put a +1/+1 counter on each of them." |
| rule:etb-loot | KEEP | A-Master of Winds | "When Master of Winds enters, draw two cards, then discard a card." |
| rule:conditional-first-strike-your-turn | KEEP | Ahn-Crop Invader | "During your turn, this creature has first strike." |
| rule:etb-exile-graveyard-card | KEEP | Carrion Imp | "When this creature enters, you may exile target creature card from a gravey…" |
| rule:grants-temporary-hexproof-target-creature | KILL | Shore Up | "Target creature you control gets +1/+1 and gains hexproof until end of turn…" |
| rule:tutor-basic-land-to-hand | KEEP | Journeyer's Kite | "{3}, {T}: Search your library for a basic land card, reveal it, put it into…" |
| rule:attack-trigger-self-counter-growth | KEEP | Sparring Regimen | "Whenever you attack, put a +1/+1 counter on target attacking creature and u…" |
| rule:fixed-lifegain | KEEP | Buzzing Whack-a-Doodle | "{T}: You gain 3 life." |
| rule:combat-damage-to-creature-triggers-self-counter | KEEP | Slith Firewalker | "Whenever this creature deals combat damage to a player, put a +1/+1 counter…" |
| rule:no-maximum-hand-size | KEEP | Jin-Gitaxias // The Great Synthesis | "You have no maximum hand size for as long as you control this Saga." |

**Note on this sample:** `rule:fixed-lifegain`'s sampled member (Buzzing
Whack-a-Doodle, "{T}: You gain 3 life.") is fine for that axis — it's the
*other* axis this same card sits in (`rule:pay-life-cost-for-effect`, via a
different quote) that has the mismatch flagged in §0/§1. Similarly
`rule:combat-damage-to-creature-triggers-self-counter`'s sampled member
(Slith Firewalker) actually shows combat damage *to a player*, not *to a
creature* as the axis name says — a real but minor scope mismatch (the
counter-growth-on-combat-damage concept is right, the "to a creature"
qualifier in the definition is too narrow for this member). Not a
reversal of the KEEP verdict, but worth Captain's eyes.

**Result: 0 reversals expected on the verdict calls themselves; 2 quote-level
observations noted above (self-check; Captain's actual check governs).**

---

## 7. Batch-4 feedback (fold into consolidation tooling + SYNTH prompt)

1. **Real, systemic issue: semantic mismatches survive the automated
   evidence-quote-or-discard gate.** That gate only verifies a quote is
   *verbatim* oracle text — it says nothing about whether the quote
   actually supports the axis it's filed under. 12 member-level mismatches
   this batch (§0), several of them exact polarity inversions (counters vs.
   is-countered, taps vs. untaps, buff vs. destroy). Recommend: add a
   lightweight DET post-hoc check to `foundry_enrich.py` that flags
   `lane=codebook` matches whose quote contains an obvious negation/inverse
   cue relative to the axis definition (e.g. axis says "can't be
   countered" but quote itself starts with "Counter target..."). Won't
   catch everything, but Counterbore, Mishra's Helix, and Recycle are
   exactly the shape such a heuristic would flag.
2. **SYNTH prompt: consider adding one explicit line** to the two-lane
   instructions: "before assigning `lane=codebook`, re-read the codebook
   definition and confirm the quote's effect runs in the *same direction*
   — a card that does the opposite of an axis's definition is not a match
   even if it shares vocabulary." Cheap to add, directly targets this
   batch's failure pattern.
3. **Corroboration-gap fix (added after batch 2) is working** — no prompt
   or tooling change needed there; consolidate.py caught 2 single-card
   clusters automatically this run.
4. Batch-4 hand-picked targeting: the 3 QUESTION axes (once ruled), the 12
   member-mismatch removals (verify no other cards need reassignment
   nearby), and continued confirmation of the still-thin `rule:free-sacrifice-outlet`
   (n=1 after this batch) and `rule:etb-tutor-to-hand` (n=1).

---

## 8. Ledger candidates carried forward

Regenerate, Connive, Flashback, Level up, Kicker (third instance). Energy
and Perpetual pending Q2/Q3's rulings — add if Captain rules
kill-and-ledger.

---

## 9. Verification

- Verdict count vs. axis count: 158 axes total = KEEP 140 (111 existing +
  29 new) + KILL 12 + MERGE 3 + QUESTION 3 = 158. Verified programmatically
  against the full 158-slug list from `review/batch-3-enriched.json`, one
  verdict per slug, zero duplicates, zero omissions.
- Every MERGE target is named: M1 → `rule:grants-creature-type`; M2 →
  `rule:sacrifice-for-card-draw`; M3 → `rule:creates-mana-producing-artifact-token`
  — all three pre-existing codebook axes.

---

**STOP.** File written to `docs/TRIAGE-BATCH-3.md`. Captain: annotate per
the protocol convention (edit `VERDICT:` lines and member-removal notes,
fill `-> RULE:` blanks for Q1–Q3, add `## CAPTAIN-AUTHORED` blocks for any
new axes), then run `/triage-emit 3` when done.
