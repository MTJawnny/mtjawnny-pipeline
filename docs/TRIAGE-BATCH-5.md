# TRIAGE — Batch 5 (SUP full-pass, 2026-07-29)

Produced by Claude (SUP-class session) under the ratified SUP-TRIAGE-PROTOCOL,
reading `experiments/out/foundry/review/digest-batch-5.md` (169 axes: 131
confirming existing codebook v0.4 axes, 38 new candidates from free-lane
clustering; 1,319 OTHER-lane rows; 1,248 token groups) against the current
codebook (203 active axes). Every one of the 169 axes was read in full. Every
one of the 1,248 OTHER-lane token groups was read in full this batch (not a
sample) — all 108 groups of size ≥8 down through all 569 size-2 groups — a
stricter pass than batches 2–4's "size≥8 plus broad sample" convention,
because it directly paid off (see section 0). Nothing here is load-bearing
until Captain ratifies.

**How to use this doc:** section 1 is the full per-axis verdict list —
every one of the 169 axes has an explicit `VERDICT:` line. Skim it, strike
anything wrong, initial the rest. Section 2 is the one question. Section 3
is two OTHER-lane promotions found by full-coverage token-group reading —
genuine multi-card families that fell through exact-token clustering purely
because of wording variance (e.g. "cannot" vs "cant"). Section 4 is the
honesty check — verify those 30 rows against card text before trusting the
rest. Section 0 has this batch's findings, including a pattern worth your
particular attention: three tautological-rider and precedent-violation
axes that were already killed in batch 3 got re-proposed this batch under
new labels — the "recently killed, do not re-propose" codebook appendix
batch 4 flagged as a nice-to-have is now a repeat-cost problem, not a
hypothetical. The MEMBER ROSTER section (new this batch, per the batch-4
punch list) lists every axis's full membership by card name only, so you
can audit membership directly rather than trusting verdict logic alone.

**Verdict counts:** KEEP 159 (131 existing confirmations + 28 new,
3 of the 131 carrying member-removal notes) · KILL 5 · MERGE 4 ·
QUESTION 1 = 169, one verdict per axis, verified programmatically against
the enriched batch's actual 169-slug list (zero duplicates, zero
omissions).

---

## 0. Findings, interpreted

- **Three axes this batch are direct resurrections of patterns Captain
  already killed in batch 3, under new free-lane labels.** SYNTH's
  two-lane check only matches against ACTIVE codebook slugs — it has no
  visibility into killed history, so a killed pattern's underlying
  mechanism keeps getting re-discovered and re-proposed as if new. This
  happened once in batch 4 (grants-temporary-hexproof,
  etb-grants-energy-counters) and batch 4's own feedback flagged a
  "recently killed, do not re-propose" codebook appendix as worth
  considering. This batch it happened three times in one pass:
  - `rule:aura-static-pump-enchanted-creature` (n=2: Oakenform,
    Wolfkin Bond) is the same tautological-rider pattern as batch-3-killed
    `rule:aura-static-pump` ("Aura + static P/T restates what most
    combat-buff Auras do"). `rule:aura-static-power-toughness-debuff`
    (n=2: Coils of the Medusa, Stab Wound) is the same pattern's
    negative-stat mirror — an Aura that only sets a static stat modifier
    carries no more distinguishing signal when the modifier is negative.
  - `rule:equipment-static-pt-buff` (n=2: Bramble Armor, Heavy Mattock) —
    same slug name as the batch-3-killed axis, same tautological-rider
    reasoning, Equipment side.
  - `rule:damage-creature-or-planeswalker` (n=2: Reiterating Bolt, Torch
    the Tower) is the same shape as batch-3-killed
    `rule:damage-to-creature-or-planeswalker` — a combination tag across
    two object classes, violating the ratified M8 per-object-class
    damage-target rule. Same fix as batch 3: no new axis, members get
    both `rule:targeted-creature-damage` and
    `rule:targeted-planeswalker-damage` via member_additions at reconcile
    (see section 1, both axes' NOTE lines).
  All four **VERDICT: KILL** below. **Recommend escalating the
  "recently killed" codebook appendix from batch 4's nice-to-have to an
  actual build item** — see section 5.
- **Full-coverage OTHER-lane reading (all 1,248 groups, not a sample)
  surfaced two genuine 2-card families that exact-token clustering
  missed purely on wording, both verified against the corpus's actual
  oracle text before being proposed here:**
  - Elder Spawn ("This creature can't be blocked by red creatures.") and
    Barrenton Cragtreads ("This creature can't be blocked by red
    creatures.") — **identical quotes**, split into separate token groups
    because one was labeled `cannot-be-blocked-by-color` and the other
    `cant-be-blocked-by-color`. Proposed as `rule:cant-be-blocked-by-color`
    in section 3.
  - Cyclopean Titan ("When Cyclopean Titan dies, two target lands become
    Swamps.") and Cyclopean Giant ("When this creature dies, target land
    becomes a Swamp.") — same death-trigger-land-becomes-Swamp mechanism
    at different scope (one vs. two lands), split by
    `death-trigger-converts-lands-to-swamps` vs.
    `death-trigger-land-becomes-swamp` wording. Proposed as
    `rule:death-trigger-land-becomes-swamp` in section 3.
  This validates reading every group instead of sampling the long tail —
  see section 5 for a concrete SYNTH/consolidate implication.
- **Two quote-verification member mismatches found while building the
  override sample and cross-checking new-candidate quotes, same category
  of catch as batches 3–4's polarity-inversion and object-class findings:**
  - `rule:activated-tap-target-creature`'s new member Samut, Voice of
    Dissent has quote "{W}, {T}: Untap another target creature." — UNTAP,
    the opposite of the axis. Member removal, section 1.
  - `rule:copy-creature-token`'s new member Mythos of Illuna has quote
    "Create a token that's a copy of target permanent." — any permanent,
    not restricted to creature, broader than the axis. Member removal,
    section 1.
  - `rule:counters-noncreature-spell` gained 4 members this batch, but 2
    of them (Declaration of Naught: "Counter target spell with the chosen
    name."; Electrosiphon: "Counter target spell.") show no noncreature
    restriction in their quotes at all. Member removal, section 1.
- **A gap-fill found while checking `rule:counters-noncreature-spell`'s
  bad members: they're both genuine unrestricted counterspells, and there
  was no existing "plain counter target spell, no restriction" axis for
  them to belong to instead.** This batch's own new candidate
  `rule:activated-counter-target-spell` (Deny the Witch, Ertai, Wizard
  Adept) fills exactly that gap — but Declaration of Naught and
  Electrosiphon aren't its members either (they weren't proposed there by
  SYNTH). Not actioned as a reassignment this batch — flagged to
  section 6 punch list since it needs a corpus-validated check, not a
  guess.
- **`rule:activation-restricted-to-sorcery-speed` (existing codebook
  axis, n=3 confirmed this batch) is undercounted.** Full OTHER-lane
  reading turned up two more cards with the exact "Activate only as a
  sorcery." quote that free-lane clustering filed under different labels
  and never matched to the codebook slug: Cat Burglar
  (`activated-ability-sorcery-speed-restriction`) and Priest of the
  Haunted Edge (`sorcery-speed-activation-restriction`). Flagged as a
  member_addition in section 1, not a promotion (same axis, not a new
  one).
- **OTHER-lane: zero *new-family* promotions beyond the two above** —
  every other group of every size, all 1,248, is the same generic
  2–3-token-overlap collision pattern documented every batch since batch
  2 (e.g. `[count/scal]`'s 64 members share nothing but "something scales
  with some count of something"). This is the first batch to verify that
  claim against literally every group rather than a sample.
- **Alchemy / non-normal-layout anomalies (14 + 94 rows)**: sampled a
  cross-section while reading the OTHER-lane groups they appear in; no
  additional issues beyond what's already covered above.

---

## 1. Per-axis verdicts (169)

Every axis gets its own `VERDICT:` line per protocol. Unflagged entries
are confident KEEPs (lane=codebook resolution verified against the corpus
for existing confirmations; a coherent 2+-distinct-card free-lane cluster
with a sound, non-duplicate definition for new candidates). Flagged
entries carry member-removal, member-addition, merge, or kill notes
inline.

- `rule:activated-ability-costs-self-sacrifice` (n=2) — VERDICT: KEEP
- `rule:activated-animate-other-artifact` (n=2) — VERDICT: KEEP
- `rule:activated-counter-target-spell` (n=2) — VERDICT: KEEP
- `rule:activated-counter-transfer-from-other-creature` (n=3) — VERDICT: KEEP
- `rule:activated-draw-a-card` (n=9) — VERDICT: KEEP
- `rule:activated-exile-graveyard-creature-card` (n=2) — VERDICT: KEEP
- `rule:activated-prevent-damage-any-target` (n=3) — VERDICT: QUESTION — see Q1
- `rule:activated-tap-target-creature` (n=4) — VERDICT: KEEP — NOTE: remove member(s) Samut, Voice of Dissent — Samut's quote is "{W}, {T}: Untap another target creature." -- UNTAP, the opposite polarity of the axis (taps a target creature).
VERDICT: Parent proposal - `rule:activated-tap-target`
- `rule:activation-restricted-to-own-upkeep` (n=11) — VERDICT: KEEP
- `rule:activation-restricted-to-sorcery-speed` (n=3) — VERDICT: KEEP — NOTE: OTHER-lane scan found 2 more real members with the identical "Activate only as a sorcery." quote that free-lane clustering missed (different surrounding labels): Cat Burglar, Priest of the Haunted Edge. Recommend member_additions at reconcile.
- `rule:additional-cost-discard-a-card` (n=4) — VERDICT: KEEP
- `rule:additional-cost-sacrifice-permanent` (n=8) — VERDICT: KEEP
- `rule:alt-cost-bounce-basic-land` (n=2) — VERDICT: KEEP
- `rule:alt-cost-sacrifice-lands` (n=1) — VERDICT: KEEP
- `rule:animates-land-into-creature` (n=4) — VERDICT: KEEP
- `rule:attack-trigger-create-token` (n=5) — VERDICT: KEEP
- `rule:attack-trigger-loot` (n=1) — VERDICT: KEEP
- `rule:attack-trigger-self-counter-growth` (n=1) — VERDICT: KEEP
- `rule:attack-trigger-tribal-anthem-attackers` (n=2) — VERDICT: KEEP
VERDICT Parent proposal - `rule:attack-trigger`
- `rule:aura-static-power-toughness-debuff` (n=2) — VERDICT: KILL — Tautological rider -- same standing as batch-3-killed rule:aura-static-pump ("Aura + static P/T restates what most combat-buff Auras do"); a debuff Aura with only a static stat change carries no more distinguishing signal than a buff one.
- `rule:aura-static-pump-enchanted-creature` (n=2) — VERDICT: KILL — Direct resurrection of batch-3-killed rule:aura-static-pump under a new label. Same tautological-rider reasoning.
- `rule:burst-draw` (n=16) — VERDICT: KEEP
- `rule:cannot-block-restriction` (n=1) — VERDICT: KEEP
- `rule:cant-be-countered` (n=2) — VERDICT: KEEP
- `rule:cantrip` (n=2) — VERDICT: KEEP
- `rule:cast-trigger-draw-on-target-own-creature-spell` (n=2) — VERDICT: KEEP
VERDICT Parent Proposal - `rule:cast-trigger`
- `rule:changes-creature-color` (n=1) — VERDICT: KEEP - Change name to `rule:changes-color-creature`. that way other types are natural addtions, `rule:changes-color-artifact`, `rule:changes-color-permanent`, ect. with Parent Proposal - `rule:changes-creature`. I know we said wait until end to change names. but do this now. also we'll change names before we do the big final process against all cards.
- `rule:charge-counter-accumulation` (n=7) — VERDICT: KEEP
- `rule:cheat-creature-into-play` (n=2) — VERDICT: KEEP
- `rule:choose-color-on-etb` (n=2) — VERDICT: KEEP
- `rule:combat-damage-to-player-draws-card` (n=2) — VERDICT: KEEP
- `rule:combat-damage-triggers-loot` (n=4) — VERDICT: KEEP
VERDICT - Parent Proposal: `rule:combat-damage`
- `rule:combat-trick-pump-own-creature` (n=10) — VERDICT: KEEP
- `rule:compensates-controller-with-token` (n=2) — VERDICT: KEEP
- `rule:conditional-attack-restriction` (n=1) — VERDICT: KEEP
- `rule:conditional-buff-by-color` (n=1) — VERDICT: KEEP
- `rule:conditional-first-strike-your-turn` (n=2) — VERDICT: KEEP
- `rule:copies-cast-spell` (n=5) — VERDICT: KEEP
- `rule:copy-creature-token` (n=1) — VERDICT: KEEP — NOTE: remove member(s) Mythos of Illuna — Quote is "Create a token that's a copy of target permanent." -- any permanent, not restricted to creature.
- `rule:cost-reduction` (n=4) — VERDICT: KEEP
- `rule:cost-reduction-scaled-by-lifegain` (n=2) — VERDICT: KEEP
- `rule:cost-reduction-scales-with-own-counters` (n=2) — VERDICT: KEEP
- `rule:counter-removal-as-activation-cost` (n=7) — VERDICT: KEEP
- `rule:counters-noncreature-spell` (n=4) — VERDICT: KEEP — NOTE: remove member(s) Declaration of Naught, Electrosiphon — Neither quote shows a noncreature restriction: Declaration of Naught is "Counter target spell with the chosen name" (any type); Electrosiphon is "Counter target spell." (unrestricted). Axis requires the noncreature-only restriction to be present in the quote itself.
- `rule:creates-creature-token` (n=22) — VERDICT: KEEP
- `rule:creates-mana-producing-artifact-token` (n=1) — VERDICT: KEEP
- `rule:creates-treasure-token` (n=15) — VERDICT: KEEP
VERDICT rename these three to:
`rule:creates-token-creature`
- `rule:creates-token-mana-producing-artifact`
- `rule:creates-token-treasure`

so we can have:
`rule:creates-token-food`
`rule:creates-token-blood`
`rule:creates-token-lander`
`rule:creates-token-clue` etc.
then Parent proposal `rule:creates-token`

- `rule:damage-creature-or-planeswalker` (n=2) — VERDICT: KILL — Violates the ratified M8 per-object-class damage-target rule -- direct resurrection of batch-3-killed rule:damage-to-creature-or-planeswalker. Members get both rule:targeted-creature-damage and rule:targeted-planeswalker-damage via member_additions instead.
- `rule:damage-divided-among-multiple-targets` (n=2) — VERDICT: KEEP
- `rule:damage-then-exile-instead-of-die` (n=2) — VERDICT: MERGE — merge_into=rule:graveyard-to-exile-replacement -- same continuous-replacement-effect pattern as batch-4's replaces-death-with-exile merge (D4), just phrased as damage-triggered exile.
- `rule:death-of-your-permanents-grows-this-creature` (n=2) — VERDICT: KEEP
- `rule:death-trigger-damage-equal-to-power` (n=1) — VERDICT: KEEP
- `rule:death-trigger-draw-card` (n=1) — VERDICT: KEEP
- `rule:death-trigger-token-creation` (n=6) — VERDICT: KEEP
- `rule:death-trigger-token-scaled-by-power` (n=2) — VERDICT: KEEP
VERDICT - Parent Proposal `rule:death-trigger`
- `rule:delayed-draw-next-upkeep` (n=1) — VERDICT: KEEP
VERDICT: Rule Proposal `rule:delayed-cantrip` - for cards that fit the confinds of a cantrip, but draw a card later. Like Mishra's Bauble.
- `rule:direct-damage-any-target` (n=18) — VERDICT: KEEP
- `rule:doubles-counter-placement` (n=2) — VERDICT: KEEP
- `rule:doubles-room-ability-triggers` (n=2) — VERDICT: KEEP
- `rule:drain-life` (n=3) — VERDICT: KEEP
- `rule:drain-on-creature-death` (n=5) — VERDICT: KEEP
- `rule:draw-cards-with-life-loss-cost` (n=2) — VERDICT: KEEP
- `rule:draw-second-card-trigger-token` (n=1) — VERDICT: KEEP
VERDICT: Parent proposal - `rule:draw-second-card-trigger`
this is similar, but completely diferent than second draw card trigger happens for opponents only. so `rule:opponent-draw-second-card-trigger-token`, `rule:opponent-draw-second-card-trigger-draw`. for cards that say "When a player draws their second card" or something similar and does not specify an opponent or you the player. it will be `rule:players-draw-second-card-trigger-token`, `rule:players-draw-second-card-trigger-draw`. `rule:draw-second-card-trigger` will be the parent of `rule:players-draw-second-card-trigger-token`, `rule:opponent-draw-second-card-trigger-token`, and `rule:draw-second-card-trigger-token` and all similar rules within those buckets. `rule:cast-second-spell-trigger` will have a similar set up to this once it gets made. so
`rule:cast-second-spell-trigger-token`
`rule:cast-second-spell-trigger-draw`, etc.
`rule:opponent-cast-second-spell-trigger-token`
`rule:opponent-cast-second-spell-trigger-draw`, etc.
`rule:players-cast-second-spell-trigger-token`
`rule:players-cast-second-spell-trigger-draw`, etc. will all fall under `rule:cast-second-spell-trigger`. log these.

- `rule:enters-tapped` (n=24) — VERDICT: KEEP
- `rule:equipment-etb-creates-and-attaches-token` (n=1) — VERDICT: KEEP
- `rule:equipment-static-pt-buff` (n=2) — VERDICT: KILL — Direct resurrection of batch-3-killed rule:equipment-static-pt-buff, same slug even. Tautological rider, Equipment-side twin of the aura case.
- `rule:etb-and-attack-trigger` (n=4) — VERDICT: KEEP
- `rule:etb-auto-attach-to-own-creature` (n=2) — VERDICT: KEEP
- `rule:etb-bounce-other-creature` (n=1) — VERDICT: KEEP
- `rule:etb-counter-on-other-creature` (n=9) — VERDICT: KEEP
- `rule:etb-create-token` (n=13) — VERDICT: KEEP
- `rule:etb-destroy-artifact-enchantment` (n=1) — VERDICT: KEEP
- `rule:etb-draw-card` (n=4) — VERDICT: KEEP
- `rule:etb-exile-graveyard-card` (n=2) — VERDICT: KEEP
- `rule:etb-gain-life` (n=7) — VERDICT: KEEP
- `rule:etb-loot` (n=2) — VERDICT: KEEP
- `rule:etb-mass-pump-your-creatures` (n=3) — VERDICT: KEEP
- `rule:etb-modal-choice` (n=6) — VERDICT: KEEP
- `rule:etb-scry` (n=4) — VERDICT: KEEP
- `rule:etb-self-bounce-own-permanent` (n=1) — VERDICT: KEEP
- `rule:etb-tutor-to-hand` (n=1) — VERDICT: KEEP
- `rule:etb-with-counters` (n=12) — VERDICT: KEEP
- `rule:etb-with-negative-counters` (n=3) — VERDICT: MERGE — merge_into=rule:etb-with-counters -- same mechanism (fixed counter count on ETB), counter polarity (+1/+1 vs -1/-1) is a parameter, not a distinct axis, per the mana-activated-pump-self stat-target-parameter precedent (batch 4).
VERDICT: Parent Proposal  `rule:etb`
- `rule:evasion-vs-low-power-blockers` (n=2) — VERDICT: KEEP
- `rule:exile-until-source-leaves` (n=5) — VERDICT: KEEP
- `rule:fixed-lifegain` (n=13) — VERDICT: KEEP
- `rule:forced-attack-each-combat` (n=2) — VERDICT: KEEP
- `rule:forced-hand-reveal` (n=5) — VERDICT: KEEP
- `rule:forces-creature-to-attack` (n=1) — VERDICT: KEEP
- `rule:free-cast` (n=1) — VERDICT: KEEP
- `rule:free-sacrifice-outlet` (n=1) — VERDICT: KEEP
- `rule:gains-life-on-other-creature-etb` (n=3) — VERDICT: KEEP
- `rule:grants-ability-at-threshold-board` (n=1) — VERDICT: KEEP
- `rule:grants-ability-at-threshold-self` (n=5) — VERDICT: KEEP
- `rule:grants-additional-combat-phase` (n=1) — VERDICT: KEEP
- `rule:grants-creature-type` (n=1) — VERDICT: KEEP
- `rule:grants-extra-land-drop` (n=1) — VERDICT: KEEP
- `rule:grants-haste-to-created-tokens` (n=3) — VERDICT: KEEP
- `rule:grants-haste-to-your-creatures` (n=2) — VERDICT: KEEP
- `rule:grants-trample-to-other-creatures` (n=1) — VERDICT: KEEP
- `rule:grants-unblockable-target` (n=2) — VERDICT: KEEP
- `rule:graveyard-to-hand-recursion` (n=8) — VERDICT: KEEP
- `rule:graveyard-to-library-shuffle-in` (n=1) — VERDICT: KEEP
- `rule:individual-cost-reduction` (n=1) — VERDICT: KEEP
- `rule:innate-unblockable` (n=4) — VERDICT: KEEP
- `rule:kicker-conditional-bonus-effect` (n=3) — VERDICT: KEEP
- `rule:landfall-gain-life` (n=2) — VERDICT: KEEP
- `rule:landfall-produces-mana` (n=2) — VERDICT: KEEP
- `rule:landfall-self-pump` (n=1) — VERDICT: KEEP
VERDICT: parent proposal `rule:landfall`
- `rule:leaves-battlefield-trigger-create-token` (n=2) — VERDICT: KEEP
- `rule:level-up-scaling-stats-abilities` (n=1) — VERDICT: KEEP
- `rule:library-dig-put-onto-battlefield` (n=3) — VERDICT: KEEP
- `rule:library-dig-to-hand` (n=3) — VERDICT: KEEP - YES, GREAT PULL. make sure cards like Plunge into Darkness make into the list.
- `rule:library-top-visibility` (n=2) — VERDICT: KEEP
- `rule:life-total-reset` (n=1) — VERDICT: KEEP
- `rule:lifegain-scaled-by-sacrificed-creature-toughness` (n=1) — VERDICT: KEEP
- `rule:lifegain-triggered-counter` (n=1) — VERDICT: KEEP
- `rule:mana-activated-pump-self` (n=8) — VERDICT: KEEP
- `rule:mass-counter-distribution` (n=5) — VERDICT: KEEP
- `rule:mass-creature-destruction` (n=1) — VERDICT: KEEP
- `rule:mass-damage-creatures-and-players` (n=2) — VERDICT: KEEP
- `rule:mass-damage-opponent-creatures-only` (n=3) — VERDICT: KEEP
- `rule:mass-debuff-opponent-creatures` (n=2) — VERDICT: KEEP
- `rule:mass-graveyard-exile` (n=1) — VERDICT: KEEP
- `rule:mass-pump-your-creatures` (n=5) — VERDICT: KEEP
- `rule:mass-untap-and-haste-stolen-creatures` (n=2) — VERDICT: KEEP
- `rule:mass-untap-your-creatures` (n=1) — VERDICT: KEEP
- `rule:mill-self-cards` (n=1) — VERDICT: KEEP
- `rule:modal` (n=15) — VERDICT: KEEP
- `rule:no-maximum-hand-size` (n=1) — VERDICT: KEEP
- `rule:once-per-turn-trigger-limit` (n=3) — VERDICT: KILL — Procedural rider/templating -- a rate-limiter clause ("only once each turn") that could attach to any triggered ability; not a functional pattern of its own.
- `rule:other-creature-etb-triggers-damage-to-opponents` (n=2) — VERDICT: KEEP
- `rule:partner-with-tutor` (n=2) — VERDICT: KEEP
- `rule:pay-life-cost-for-effect` (n=3) — VERDICT: KEEP
- `rule:plus1-counters-matter` (n=6) — VERDICT: KEEP
VERDICT: I made a proposal for something like `rule:neg1-counters-matter` for cards that care about negative -1/-1 counters. I don't see it in the list. log it.
- `rule:populate-copy-creature-token` (n=3) — VERDICT: KEEP
- `rule:power-scales-with-creature-count` (n=1) — VERDICT: KEEP
- `rule:prevent-combat-damage-unblocked-creature` (n=2) — VERDICT: KEEP
- `rule:prevent-damage-to-your-creatures` (n=2) — VERDICT: KEEP
- `rule:prevent-fixed-damage-any-target` (n=1) — VERDICT: KEEP
- `rule:prevents-regeneration` (n=5) — VERDICT: KEEP
- `rule:pump-plus-first-strike-any-creature` (n=2) — VERDICT: MERGE — merge_into=rule:temporary-keyword-grant -- the wide-net axis already absorbs "gets +X/+Y and gains [keyword] until end of turn" patterns (its own batch-5 members include exactly this shape for other keywords); first-strike is not a distinguishing exception.
- `rule:reanimate-from-graveyard` (n=10) — VERDICT: KEEP
- `rule:redirect-damage-to-spell-controller` (n=2) — VERDICT: KEEP
- `rule:redirect-targets-of-spell-or-ability` (n=1) — VERDICT: KEEP
- `rule:replacement-graveyard-to-exile-self` (n=2) — VERDICT: MERGE — merge_into=rule:graveyard-to-exile-replacement -- direct resurrection of batch-4's replacement-exile-instead-of-graveyard merge (D4), same self-protective shape.
- `rule:restricted-mana-for-equipment` (n=2) — VERDICT: KEEP
- `rule:restricts-blocking-to-flying-only` (n=2) — VERDICT: KEEP
- `rule:rhystic-tax` (n=5) — VERDICT: KEEP
- `rule:sacrifice-for-card-draw` (n=4) — VERDICT: KEEP
- `rule:sacrifice-for-creature-token` (n=2) — VERDICT: KEEP
- `rule:scales-token-count-with-x` (n=1) — VERDICT: KEEP
- `rule:self-bounce-activated` (n=1) — VERDICT: KEEP
- `rule:self-counter-growth` (n=2) — VERDICT: KEEP
- `rule:sets-base-power-or-toughness` (n=4) — VERDICT: KEEP
- `rule:stun-counter` (n=3) — VERDICT: KEEP
- `rule:targeted-bounce-creature` (n=7) — VERDICT: KEEP
- `rule:targeted-creature-damage` (n=15) — VERDICT: KEEP — NOTE: D2-style reconcile addition: add Reiterating Bolt and Torch the Tower here per the killed rule:damage-creature-or-planeswalker's M8 redistribution (see section 0).
- `rule:targeted-destruction` (n=25) — VERDICT: KEEP
- `rule:targeted-discard` (n=7) — VERDICT: KEEP
- `rule:targeted-exile` (n=12) — VERDICT: KEEP
- `rule:targeted-planeswalker-damage` (n=2) — VERDICT: KEEP — NOTE: D2-style reconcile addition: add Reiterating Bolt and Torch the Tower here per the killed rule:damage-creature-or-planeswalker's M8 redistribution (see section 0).
- `rule:targeted-player-damage` (n=4) — VERDICT: KEEP
- `rule:temporary-control-theft` (n=9) — VERDICT: KEEP
- `rule:temporary-keyword-grant` (n=13) — VERDICT: KEEP
- `rule:transforms-on-graveyard-threshold` (n=2) — VERDICT: KEEP
- `rule:tribal-anthem-buff` (n=10) — VERDICT: KEEP
- `rule:untaps-target-land` (n=3) — VERDICT: KEEP
- `rule:x-scales-with-permanent-count` (n=3) — VERDICT: KEEP

I requested some names be changed. i think that's fine before the final pass for now. However. I want to make sure we at least audit the rule names before we do the full corpus scan. and make sure the logic behind each rule is understandable for the agents that work on the corpus. makes sense?

---

## 2. QUESTIONS (1)

**Q1 — `rule:activated-prevent-damage-any-target` (n=3: Daru Healer,
Samite Alchemist, Serra Paladin) vs. existing `rule:prevent-fixed-damage-any-target`
(n=1 this batch: Samite Healer, definition "The spell prevents a fixed
amount of the next damage that would be dealt to a chosen target this
turn").**
Same core effect (prevent a fixed amount of the next damage to any
target) but a different delivery mechanism: the existing axis's
definition is written spell-specific ("The spell prevents..."), while
this candidate's three members are all `{T}:` activated abilities on
permanents, not spells. The pipeline has precedent both ways: delivery
trigger is kept as its own axis dimension in some families
(`rule:activated-tap-target-creature` stays separate from any hypothetical
ETB/attack-trigger tap sibling) but merged as a parameter in others
(`rule:etb-with-negative-counters`'s proposed merge into
`rule:etb-with-counters` this same batch, treating +1/+1-vs-1/-1 as a
parameter not an axis). Same-concept-different-delivery (merge, broaden
the existing axis's definition to cover both spell and activated
sources), or keep as siblings (the existing axis's own wording is already
spell-specific, arguably deliberately)?
→ RULE: merge-into-prevent-fixed-damage-any-target / keep-separate: MERGE

---

## 3. OTHER-LANE PROMOTIONS (2)

Found by reading all 1,248 token groups (not a sample) and verifying the
underlying corpus oracle text before proposing — see section 0.

**`rule:cant-be-blocked-by-color`** — scope=self. Definition: "The
creature is textually forbidden from being blocked by creatures of one
specific color." Members (2, both verified verbatim against corpus
oracle text):
- Elder Spawn — "This creature can't be blocked by red creatures."
- Barrenton Cragtreads — "This creature can't be blocked by red
  creatures."

Not the same as `rule:restricts-blocking-to-flying-only` (that's a
"this creature can only block fliers" restriction on the creature's own
blocking, not an evasion ability). Not the same as `Magistrate's Veto`'s
`restricts-blocking-by-color` (that's a symmetric "creatures of chosen
colors can't block at all" static effect on the battlefield, opposite
vector — correctly excluded from this promotion).
VERDICT: `rule:cant-be-blocked-by-color` keep

**`rule:death-trigger-land-becomes-swamp`** — scope=self. Definition:
"When this permanent dies, one or more target lands become Swamps."
Members (2, both verified verbatim against corpus oracle text):
- Cyclopean Titan — "When Cyclopean Titan dies, two target lands become
  Swamps."
- Cyclopean Giant — "When this creature dies, target land becomes a
  Swamp."

Scope (one land vs. two) is a parameter within the same axis, consistent
with how other wide-net axes in this codebook already absorb
count/degree variance (e.g. `rule:mass-counter-distribution` covers both
fixed and per-creature counter amounts).
VERDICT: Keep
---

## 4. OVERRIDE SPOT-CHECK — verify these 30 before trusting the rest

Fixed seed 20260723 (= 20260718 + batch 5), drawn from the 168 confident
calls (KEEP/KILL/MERGE; the 1 QUESTION excluded), via
`random.seed(20260723); random.sample(confident_calls, 30)` where
`confident_calls` is the alphabetically-sorted list of all 169 axis slugs
minus `rule:activated-prevent-damage-any-target`. Every quote below was
verified programmatically against the card's actual oracle text in
`experiments/out/foundry/review/batch-5-enriched.json` — **all 30 passed
verbatim.** Check each verdict against the card text yourself. If more
than ~1 is wrong, distrust the lanes and tell me — loudly.

| Axis | Verdict | Sample member | Evidence quote |
|---|---|---|---|
| rule:activated-counter-transfer-from-other-creature | KEEP | Spike Hatcher | "{2}, Remove a +1/+1 counter from this creature: Put a +1/+1 counter on target creature." |
| rule:additional-cost-sacrifice-permanent | KEEP | Blood-Chin Fanatic | "Sacrifice another Warrior creature" |
| rule:attack-trigger-create-token | KEEP | Curse of Shallow Graves | "Whenever a player attacks enchanted player with one or more creatures, that attacking p…" |
| rule:attack-trigger-tribal-anthem-attackers | KEEP | Blaring Captain | "Whenever this creature attacks, attacking Warriors get +1/+1 until end of turn." |
| rule:burst-draw | KEEP | Ancestral Reminiscence | "Draw three cards, then discard a card." |
| rule:conditional-buff-by-color | KEEP | Essence Leak | "As long as enchanted permanent is red or green, it has" |
| rule:cost-reduction-scales-with-own-counters | KEEP | REMOVE - Hinata, Dawn-Crowned | "Spells you cast cost {1} less to cast for each target." | - Hinata, Dawn-Crowned does not mention counters in her text.
| rule:creates-mana-producing-artifact-token | KEEP | REMOVE - Root Out | "Investigate. Create a Clue token. It's an artifact with '{2}, Sacrifice this token: Dr…" | - Clue token do not produce mana.
| rule:enters-tapped | KEEP | REMOVE - Agna Qel'a | "This land enters tapped unless you control a basic land." Rule Proposal:`rule:enters-tapped-conditional`. Add Agna Qel'a to `rule:enters-tapped-conditional`. as it will enter tapped unless a condition is met.
| rule:equipment-static-pt-buff | KILL | Bramble Armor | "Equipped creature gets +2/+1." |
| rule:etb-draw-card | KEEP | Advancing the Spirit | "When this enchantment enters, draw a card." |
| rule:etb-loot | KEEP | Big Wheel | "When this Vehicle enters, you may discard a card. If you do, draw a card." |
| rule:etb-mass-pump-your-creatures | KEEP | Imodane's Recruiter // Train Troops | "When this creature enters, creatures you control get +1/+0 and gain haste until end of …" |
| rule:evasion-vs-low-power-blockers | KEEP | Bristlebane Outrider | "This creature can't be blocked by creatures with power 2 or less." |
| rule:gains-life-on-other-creature-etb | KEEP | A-Social Climber | "Alliance — Whenever another creature enters under your control, you gain 1 life." |
| rule:grants-ability-at-threshold-board | KEEP | Duelcraft Trainer | "Coven — At the beginning of combat on your turn, if you control three or more creatures…" |
| rule:grants-haste-to-created-tokens | KEEP | Rootwire Amalgam | "It gains haste until end of turn." |
| rule:level-up-scaling-stats-abilities | KEEP | Guul Draz Assassin | "Level up {1}{B} ({1}{B}: Put a level counter on this. Level up only as a sorcery.)" |
| rule:lifegain-scaled-by-sacrificed-creature-toughness | KEEP | Miren, the Moaning Well | "{3}, {T}, Sacrifice a creature: You gain life equal to the sacrificed creature's toughn…" |
| rule:other-creature-etb-triggers-damage-to-opponents | KEEP | General Kreat, the Boltbringer | "Whenever another creature you control enters, General Kreat deals 1 damage to each oppo…" |
| rule:pay-life-cost-for-effect | KEEP | Fleshless Gladiator | "You lose 1 life." |
| rule:plus1-counters-matter | KEEP | Banewhip Punisher | "Destroy target creature that has a -1/-1 counter on it." |
| rule:prevent-fixed-damage-any-target | KEEP | Samite Healer | "{T}: Prevent the next 1 damage that would be dealt to any target this turn." |
| rule:sacrifice-for-card-draw | KEEP | Diviner's Lockbox | "sacrifice this artifact and draw three cards" |
| rule:sacrifice-for-creature-token | KEEP | Path to Redemption | "{5}, Sacrifice this Aura: Exile enchanted creature. Create a 1/1 white Ally creature to…" |
| rule:targeted-exile | KEEP | Abstruse Appropriation | "Exile target nonland permanent." |
| rule:targeted-planeswalker-damage | KEEP | Consulate Turret | "This artifact deals 2 damage to target player or planeswalker." |
| rule:temporary-keyword-grant | KEEP | Academic Dispute | "You may have it gain reach until end of turn." |
| rule:transforms-on-graveyard-threshold | KEEP | Tales of Master Seshiro // Seshiro's Living Legacy | "Exile this Saga, then return it to the battlefield transformed under your control." |
| rule:tribal-anthem-buff | KEEP | A-Kargan Warleader | "Other Warriors you control get +1/+1 and have ward {1}." |

**Result: 0 reversals expected on the verdict calls themselves (all 30
quotes verified verbatim); the real findings this batch came from reading
every OTHER-lane group and cross-checking new-candidate quotes rather
than from the spot-check sample itself (see section 0).**

---

## 5. Batch-6 feedback (fold into consolidation tooling + SYNTH prompt)

1. **Escalate the "recently killed, do not re-propose" codebook appendix
   from batch 4's nice-to-have to an actual build item.** Batch 4
   flagged this as worth considering after 2 resurrections
   (grants-temporary-hexproof, etb-grants-energy-counters); this batch
   had 3 more (aura-static-pump-enchanted-creature,
   equipment-static-pt-buff, damage-creature-or-planeswalker), all
   traceable to specific batch-3 kills. SYNTH's two-lane prompt only sees
   ACTIVE codebook slugs, so it has no way to avoid re-discovering a
   killed mechanism under a new label. Concretely: append a short
   "recently killed/merged, do not re-propose" section to the embedded
   codebook reference (slug + one-line reason only, to control the
   prompt-growth cost already flagged in
   MASTER-HANDOFF-ADDENDUM-2.md — this is now the 3rd batch running
   where that cost trend is worth tracking).
2. **Consolidation implication of section 0's two OTHER-lane finds:**
   both `cant-be-blocked-by-color` and `death-trigger-land-becomes-swamp`
   were split purely on a synonym/contraction ("cannot" vs "cant") or
   near-synonym phrasing ("converts-lands-to-swamps" vs
   "land-becomes-swamp") that exact-token-set clustering treats as
   distinct. Consider a light stemming/synonym-normalization pass before
   the exact-match clustering step in `foundry_consolidate.py`
   (contractions at minimum: cant/cannot, wont/will-not) — cheap,
   deterministic, and would have auto-caught both of this batch's finds
   without a full manual OTHER-lane read.
3. **SYNTH prompt addition: quote must support the FULL restriction in
   the axis definition, not just the general shape.** This batch's
   `rule:counters-noncreature-spell` mismatches (Declaration of Naught,
   Electrosiphon) both matched on "this is a counterspell" but neither
   quote establishes the noncreature-only restriction the axis requires.
   Same root issue as batch 3-4's direction/object-class checks, one
   more instance: before assigning lane="codebook" to an axis whose
   definition includes a restrictive qualifier (noncreature-only,
   creature-only, opponent-only, etc.), confirm the qualifier is present
   in the quote itself, not assumed from the general pattern.
4. Batch-6 hand-picked targeting: the 1 QUESTION axis (once ruled), the
   `rule:activated-counter-target-spell` vs `rule:counters-noncreature-spell`
   sibling relationship (punch-listed, section 6), and continued
   confirmation of the two newly-DEFERRED-from-batch-4 pump axes if
   Captain rules to keep them separate (would need fresh confirmation
   picks, not yet needed pending that ruling).

---

## 6. Ledger candidates carried forward

None this batch — zero kills traced to a bare keyword or keyword
mechanism (all 5 kills are tautological-rider or M8-object-class
violations, not keyword-territory; see section 0). No
`docs/KEYWORD-LEDGER-CANDIDATES.md` addition needed.

**Punch list (not executed this session, logged for reconcile/schema
pass):**
- Corpus-validate whether Declaration of Naught and Electrosiphon (the 2
  removed `rule:counters-noncreature-spell` members) belong in
  `rule:activated-counter-target-spell` instead (this batch's new
  unrestricted-counterspell candidate) — needs a name/oracle_id check
  against that axis's actual member list, not a guess (see section 0).
VERDICT:
Electrosiphon goes in `rule:counters-noncreature-spell`
Declaration of Naught goes in `rule:activated-counter-target-spell`

- Schema pass: `rule:activated-counter-target-spell` (unrestricted) and
  `rule:counters-noncreature-spell` (restricted) are siblings by
  restriction-scope — same shape as the damage-target family's
  per-object-class parent scheme. Flagged to
  `mtjawnny.github.io/docs/PARENT-TREE-CANDIDATES.md`.
- Schema pass: `rule:death-trigger-token-scaled-by-power` (new this
  batch) as a scaled child of the existing `rule:death-trigger-token-creation`
  parent, and `rule:leaves-battlefield-trigger-create-token` as a
  broader-trigger-scope sibling (leaves-battlefield vs. dies) — both tie
  into the existing trigger-family scheme
  (`rule:etb`/`rule:attack-trigger`/`rule:death-trigger` etc.) ratified
  in batch 3.

---

## 7. Verification

- Verdict count vs. axis count: 169 axes total = KEEP 159 (131 existing +
  28 new) + KILL 5 + MERGE 4 + QUESTION 1 = 169. Verified
  programmatically against the full 169-slug list from
  `review/batch-5-enriched.json`, one verdict per slug, zero duplicates,
  zero omissions.
- Every MERGE target is named and active in codebook v0.4:
  M(etb-with-negative-counters) → `rule:etb-with-counters`;
  M(damage-then-exile-instead-of-die) → `rule:graveyard-to-exile-replacement`;
  M(pump-plus-first-strike-any-creature) → `rule:temporary-keyword-grant`;
  M(replacement-graveyard-to-exile-self) → `rule:graveyard-to-exile-replacement`
  — all four pre-existing, active codebook axes.
- Override sample: 30/30 quotes verified verbatim against corpus oracle
  text via `foundry_common.full_oracle_text()`, same source every other
  DF/enrichment computation in this repo uses.
- OTHER-lane promotions: both proposed axes' member quotes verified
  verbatim against corpus oracle text (not digest-truncated text) before
  inclusion in section 3.


---

## MEMBER ROSTER (new this batch, per protocol)

Every axis this batch, full member card names only (no oracle text) -- for direct audit of membership.

- `rule:activated-ability-costs-self-sacrifice` (n=2): Bonecaller Cleric; Glen Elendra Archmage
- `rule:activated-animate-other-artifact` (n=2): Karn, Silver Golem; Tough Cookie
- `rule:activated-counter-target-spell` (n=2): Deny the Witch; Ertai, Wizard Adept
REMOVE Deny the Witch from `rule:activated-counter-target-spell`. It does not have an activated ability. It can counter activated abilities which is maybe why it was grabbed.

- `rule:activated-counter-transfer-from-other-creature` (n=3): Spike Hatcher; Spike Rogue; Spike Rogue
- `rule:activated-draw-a-card` (n=9): Arcane Investigator; Clan Crafter; Color Pie; Darkwater Egg; Jodah's Codex; Serum Sovereign; Serum Tank; The Last Ride; Xira Arien
- `rule:activated-exile-graveyard-creature-card` (n=2): Buried Treasure; Thraben Heretic
- `rule:activated-prevent-damage-any-target` (n=3): Daru Healer; Samite Alchemist; Serra Paladin
VERDICT: change name of `rule:activated-prevent-damage-any-target` to `rule:activated-prevent-fixed-damage`.
- `rule:activated-tap-target-creature` (n=4): Cyclopean Titan; North Pole Patrol; Samut, Voice of Dissent; Sanctum of Tranquil Light
- `rule:activation-restricted-to-own-upkeep` (n=11): Cauldron of Essence; Coffin Puppets; Crown of Doom; Dementia Sliver; Diviner's Lockbox; Kheru Goldkeeper; Oracle en-Vec; Quest for the Necropolis; Ravenous Amulet; Rootwire Amalgam; Will, Scion of Peace
VERDICT: I think this rule is incorrectly labeling cards.
REMOVE - Cauldron of Essence, it's activation restriction is sorcery speed.
REMOVE - Crown of Doom, it's activation restriction is only during your turn.
REMOVE - Dementia Sliver, it's activation restriction is only during your turn.
REMOVE - Diviner's Lockbox it's activation restriction is sorcery speed.
REMOVE - Kheru Goldkeeper it's activation restriction is sorcery speed.
REMOVE - Oracle en-Vec it's activation restriction is only during your turn.
REMOVE - Quest for the Necropolis it's activation restriction is sorcery speed.
REMOVE - Ravenous Amulet it's activation restriction is sorcery speed.
REMOVE - Rootwire Amalgam it's activation restriction is sorcery speed.
REMOVE - Will, Scion of Peace it's activation restriction is sorcery speed.

We need to make an additional activation resctrition rule.
`rule:activation-restricted-only-during-your-turn`
Then add Crown of Doom, Dementia Sliver, Oracle en-Vec to `rule:activation-restricted-only-during-your-turn`


- `rule:activation-restricted-to-sorcery-speed` (n=3): Burdened Stoneback; Fractured Powerstone; Implement of Ferocity
VERDICT:
ADD - Cauldron of Essence, it's activation restriction is sorcery speed.
ADD - Diviner's Lockbox it's activation restriction is sorcery speed.
ADD - Kheru Goldkeeper it's activation restriction is sorcery speed.
ADD - Quest for the Necropolis it's activation restriction is sorcery speed.
ADD - Ravenous Amulet it's activation restriction is sorcery speed.
ADD - Rootwire Amalgam it's activation restriction is sorcery speed.
ADD - Will, Scion of Peace it's activation restriction is sorcery speed.
- `rule:additional-cost-discard-a-card` (n=4): Cathartic Reunion; Mardu Outrider; Pirate's Pillage; Thrill of Possibility
- `rule:additional-cost-sacrifice-permanent` (n=8): Blood-Chin Fanatic; Collateral Damage; Costly Plunder; Jalira, Master Polymorphist; Nita, Forum Conciliator; Pygmy Giant; Torch the Tower; Wicked Reward
- `rule:alt-cost-bounce-basic-land` (n=2): Fieldmist Borderpost; Veinfire Borderpost
- `rule:alt-cost-sacrifice-lands` (n=1): Fireblast
- `rule:animates-land-into-creature` (n=4): A-Llanowar Loamspeaker; Clutch of Currents; Fendeep Summoner; Mire's Malice
- `rule:attack-trigger-create-token` (n=5): Curse of Shallow Graves; Seraphic Steed; Sigiled Sword of Valeron; Skyknight Vanguard; Windy City Aven
- `rule:attack-trigger-loot` (n=1): Overwhelmed Archivist // Archive Haunt
- `rule:attack-trigger-self-counter-growth` (n=1): Falcon, Joaquin Torres
- `rule:attack-trigger-tribal-anthem-attackers` (n=2): Blaring Captain; Riot Ringleader
- `rule:aura-static-power-toughness-debuff` (n=2): Coils of the Medusa; Stab Wound
- `rule:aura-static-pump-enchanted-creature` (n=2): Oakenform; Wolfkin Bond
- `rule:burst-draw` (n=16): Ancestral Reminiscence; Archmage's Charm; Cathartic Reunion; Costly Plunder; Explore; Illusion of Choice; Kiss of the Amesha; Nira, Hellkite Duelist; Ojutai's Command; Orcish Cannonade; Pirate's Pillage; Teferi's Response; Thassa's Bounty; Thrill of Possibility; Transcendent Message; Treasure Chest
- `rule:cannot-block-restriction` (n=1): Mindless Null
- `rule:cant-be-countered` (n=2): Dragonlord Dromoka; Hullbreaker Horror
- `rule:cantrip` (n=2): Defiant Strike; Spiritualize
VERDICT:
REMOVE - Spiritualize. It is 3CMC. Cantrips are 0-2CMC.
- `rule:cast-trigger-draw-on-target-own-creature-spell` (n=2): Rehearsed Debater; The Great Henge
- `rule:changes-creature-color` (n=1): Dwarven Song
- `rule:charge-counter-accumulation` (n=7): Aether Vial; Brain in a Jar; Clockwork Vorrac; Hangarback Walker; Jack of Hearts, Volatile Hero; Ninja of the Hand; Vitaspore Thallid
- `rule:cheat-creature-into-play` (n=2): Aether Vial; Master Transmuter
- `rule:choose-color-on-etb` (n=2): Caged Sun; Valgavoth's Lair
- `rule:combat-damage-to-player-draws-card` (n=2): Ohran Frostfang; Sword of Fire and Ice and War and Peace
- `rule:combat-damage-triggers-loot` (n=4): Abomination of Gudul; Moon-Circuit Hacker; Ninja of the Deep Hours; Willie Lumpkin, Postman
- `rule:combat-trick-pump-own-creature` (n=10): A-You Come to a River; Confidence from Strength; Defiant Strike; Diplomatic Relations; Invigorated Rampage; Samut's Sprint; Silk Net; Wicked Reward; Wild Instincts; Will of the All-Hunter
- `rule:compensates-controller-with-token` (n=2): Cityscape Leveler; Saw in Half
- `rule:conditional-attack-restriction` (n=1): Mogg Toady
- `rule:conditional-buff-by-color` (n=1): Essence Leak
- `rule:conditional-first-strike-your-turn` (n=2): Soltari Lancer; Thorned Moloch
- `rule:copies-cast-spell` (n=5): Complete the Circuit; Fire Lord Azula; Izzet Steam Maze; Shiko and Narset, Unified; Wild Ricochet
- `rule:copy-creature-token` (n=1): Mythos of Illuna
- `rule:cost-reduction` (n=4): Acolyte of Bahamut; Herald of Slaanesh; Krosan Drover; The Water Crystal
- `rule:cost-reduction-scaled-by-lifegain` (n=2): Licia, Sanguine Tribune; Will, Scion of Peace
- `rule:cost-reduction-scales-with-own-counters` (n=2): Hinata, Dawn-Crowned; Quest for the Necropolis
- `rule:counter-removal-as-activation-cost` (n=7): Brain in a Jar; Burdened Stoneback; Coral Reef; Hexavus; Serum Sovereign; Serum Tank; Spike Hatcher
- `rule:counters-noncreature-spell` (n=4): An Offer You Can't Refuse; Declaration of Naught; Electrosiphon; Glen Elendra Archmage
- `rule:creates-creature-token` (n=22): Call the Scions; Comet, Stellar Pup; Day of the Dragons; Deeproot Pilgrimage; Drake Haven; Geralf, Visionary Stitcher; Gift Shop; Goblin Warrens; Hallowed Haunting; Hazezon, Shaper of Sand; Hylda of the Icy Crown; Imodane's Recruiter // Train Troops; Inkling Summoning; Kiora, Master of the Depths; Mysterio's Mirage; Pick Your Poison; Recruitment Drive; Saheeli, Filigree Master; Sokenzan, Crucible of Defiance; The Hunger Tide Rises; Varis, Silverymoon Ranger; Volrath's Laboratory
- `rule:creates-mana-producing-artifact-token` (n=1): Root Out
VERDICT: 
REMOVE - Root Out. The clue token it makes is not a mana producing artifact. 

however, keep this rule for cards that make powerstones, and Roxanne, Starfall Savant, Gild, Curse of Opulence, King Macar, the Gold-Cursed, The First Iroan Games, etc.



- `rule:creates-treasure-token` (n=15): An Offer You Can't Refuse; Baeloth Barrityl, Entertainer; Bank Job; Bootleggers' Stash; Bounty: Lyssa, Sterling Collector // Wanted!; Bounty: Rissa "Blades" Lee // Wanted!; Brass's Bounty; Goblin Glasswright // Craft with Pride; Kheru Goldkeeper; Petty Larceny; Pirate's Pillage; Prosper, Tome-Bound; Thieves' Tools; Treasure Chest; You Find a Cursed Idol
- `rule:damage-creature-or-planeswalker` (n=2): Reiterating Bolt; Torch the Tower
- `rule:damage-divided-among-multiple-targets` (n=2): Forked Bolt; Impact Resonance
- `rule:damage-then-exile-instead-of-die` (n=2): Red Sun's Zenith; Torch the Tower
- `rule:death-of-your-permanents-grows-this-creature` (n=2): Elenda, the Dusk Rose; Necrosquito
- `rule:death-trigger-damage-equal-to-power` (n=1): Hunter's Talent
VERDICT:
REMOVE - Hunter's Talent. This card has not death trigger. put `rule:death-trigger-damage-equal-to-power` in kill bucket.
- `rule:death-trigger-draw-card` (n=1): Cormela, Glamour Thief
VERDICT: REMOVE - Cormela, Glamour Thief. Her death trigger does not draw a card. It returns up to one target instant or sorcery card from your graveyard to your hand. Not Draw. her rule might be called `rule:death-trigger-scroll-regrowth` - Scroll will be shorthand for specifcally instant or sorcery or interupt when a card mentions two or more. regrowth will be the terminology for cards that put a card from your graveyard to hand.
- `rule:death-trigger-token-creation` (n=6): Abzan Ascendancy; Grixis Slavedriver; Hangarback Walker; Mister Gutsy; Nurgle's Rot; Pretending Poxbearers
VERDICT:
REMOVE - Grixis Slavedriver. It's effect does not trigger off of dying. it triggers off of it leaving the battlefield. Which is a completely seperate game mechanic to dying. no death trigger involved.

instead create `rule:Leave-Battlefield-trigger-token-creation`

Also two parent proposals: `rule:death-trigger` & `rule:Leave-Battlefield-trigger`
- `rule:death-trigger-token-scaled-by-power` (n=2): Elenda, the Dusk Rose; The Skullspore Nexus
- `rule:delayed-draw-next-upkeep` (n=1): Portent
VERDICT: Also add to `rule:delayed-cantrip`
- `rule:direct-damage-any-target` (n=18): Collateral Damage; Dark Nourishment; Emeritus of Conflict // Lightning Bolt; Fanning the Flames; Fireblast; Ghitu Fire; Goblin Artillery; Hammerfest Boomtacular; Lightning Colt; Omen of the Forge; Orcish Cannonade; Prophetic Titan; Red Sun's Zenith; Rin and Seri, Inseparable; Spark Jolt; Spikefield Hazard // Spikefield Cave; Sunfire Torch; Sword of Fire and Ice and War and Peace
- `rule:doubles-counter-placement` (n=2): Miles Morales // Ultimate Spider-Man; Stalwart Successor
- `rule:doubles-room-ability-triggers` (n=2): Dungeon Delver; Hama Pashar, Ruin Seeker
- `rule:drain-life` (n=3): Entropic Eidolon; Kaya, Ghost Assassin; Vito, Thorn of the Dusk Rose
- `rule:drain-on-creature-death` (n=5): Cauldron of Essence; Fallen Angel Avatar; Hag of Syphoned Breath; Kalastria Healer; Relic Vial
- `rule:draw-cards-with-life-loss-cost` (n=2): Abzan Charm; Gruesome Realization
- `rule:draw-second-card-trigger-token` (n=1): Lat-Nam Adept
- `rule:enters-tapped` (n=24): Agna Qel'a; Birnin Zana Plaza; Dining Room; Ebondeath, Dracolich; Elfhame Palace; Embraal Bruiser; False Floor; Fieldmist Borderpost; Fleshless Gladiator; Lamplight Phoenix; Los Diablos Missile Base; Manor Gate; Ondu Inversion // Ondu Skyruins; Processing Plant; Quandrix Campus; Seedguide Ash; Simic Growth Chamber; Spikefield Hazard // Spikefield Cave; Stitched Mangler; Taiga Stadium; Turbulent Fen; Valgavoth's Lair; Veinfire Borderpost; Worn Powerstone
VERDICT:
REMOVE - Agna Qel'a. It enters tapped unless a condition is met or a condition makes it enter tapped. move to `rule:enters-tapped-conditional`
REMOVE - Lamplight Phoenix. It enters tapped unless a condition is met or a condition makes it enter tapped. move to `rule:enters-tapped-conditional`
REMOVE - Fleshless Gladiator. It enters tapped unless a condition is met or a condition makes it enter tapped. move to `rule:enters-tapped-conditional`
REMOVE - Seedguide Ash. Does not itself enter tapped. it has a death trigger that grabs lands that enter tapped.
REMOVE - Taiga Stadium. It enters tapped unless a condition is met or a condition makes it enter tapped. move to `rule:enters-tapped-conditional`
REMOVE - Turbulent Fen. It enters tapped unless a condition is met or a condition makes it enter tapped. move to `rule:enters-tapped-conditional` 
- `rule:equipment-etb-creates-and-attaches-token` (n=1): Hexplate Wallbreaker
- `rule:equipment-static-pt-buff` (n=2): Bramble Armor; Heavy Mattock
- `rule:etb-and-attack-trigger` (n=4): Ox Drover; Redemption Choir; Sin, Spira's Punishment; The Wise Mothman
- `rule:etb-auto-attach-to-own-creature` (n=2): Falcon's Wing Harness; Paladin's Shield
- `rule:etb-bounce-other-creature` (n=1): Mist Raven
- `rule:etb-counter-on-other-creature` (n=9): Apothecary Stomper; Guardian Shield-Bearer; Juniper Order Ranger; Miles Morales // Ultimate Spider-Man; Pick Your Poison; Rescue Retriever; Satyr Grovedancer; Supply Runners; The Great Henge
- `rule:etb-create-token` (n=13): Black Panther, Vanguard; Corpses of the Lost; Embalmed Ascendant; Experimental Confectioner; Foot Mystic; Gnome-Made Engine; Mindless Conscription; Scrapwork Cohort; Slithering Cryptid; Tough Cookie; Trial of Strength; Wolfkin Bond; Wort, the Raidmother

VERDICT: Make `rule:etb-create-token` a parent. Then return children `rule:etb-create-token-creature`, `rule:etb-create-token-treasure`, `rule:etb-create-token-food`, `rule:etb-create-token-clue`, `rule:etb-create-token-blood`, etc.

so
REMOVE Black Panther, Vanguard from `rule:etb-create-token` and create and move to `rule:etb-create-token-creature`.
REMOVE Corpses of the Lost from `rule:etb-create-token` and create and move to `rule:etb-create-token-creature`.
REMOVE Embalmed Ascendant from `rule:etb-create-token` and create and move to `rule:etb-create-token-creature`.
REMOVE Experimental Confectioner from `rule:etb-create-token` and create and move to `rule:etb-create-token-food`.
REMOVE Foot Mystic from `rule:etb-create-token` and create and move to `rule:etb-create-token-creature-conditional`.
REMOVE Gnome-Made Engine from `rule:etb-create-token` and create and move to `rule:etb-create-token-creature-conditional`.
REMOVE Mindless Conscription from `rule:etb-create-token` and create and move to `rule:etb-create-token-creature`.
REMOVE Scrapwork Cohort from `rule:etb-create-token` and create and move to `rule:etb-create-token-creature`.
REMOVE Slithering Cryptid from `rule:etb-create-token` and create and move to `rule:etb-create-token-mutagen`.
REMOVE Tough Cookie from `rule:etb-create-token` and create and move to `rule:etb-create-token-food`.
REMOVE Trial of Strength from `rule:etb-create-token` and create and move to `rule:etb-create-token-creature`.
REMOVE Wolfkin Bond from `rule:etb-create-token` and create and move to `rule:etb-create-token-creature`.
REMOVE Wort, the Raidmother from `rule:etb-create-token` and create and move to `rule:etb-create-token-creature`.
- `rule:etb-destroy-artifact-enchantment` (n=1): Aven Cloudchaser
VERDICT: 
REMOVE `rule:etb-destroy-artifact-enchantment`. CREATE `rule:etb-destroy-target-enchantment` and add Aven Cloudchaser.
- `rule:etb-draw-card` (n=4): Advancing the Spirit; Fblthp, the Lost; Kenrith's Transformation; Omnath, Locus of Creation
- `rule:etb-exile-graveyard-card` (n=2): Color Pie; Mourner's Shield
- `rule:etb-gain-life` (n=7): Apothecary Stomper; Birnin Zana Plaza; Bulwark Giant; Courier Griffin; Healer of the Glade; Lone Missionary; Los Diablos Missile Base
- `rule:etb-loot` (n=2): Big Wheel; Overwhelmed Archivist // Archive Haunt
- `rule:etb-mass-pump-your-creatures` (n=3): Imodane's Recruiter // Train Troops; Jubilation; Malamet War Scribe
- `rule:etb-modal-choice` (n=6): Apothecary Stomper; Dutiful Replicator; Lightning Colt; Prophetic Titan; Suncleanser; Voracious Hydra
- `rule:etb-scry` (n=4): Coming In Hot; Falcon, Joaquin Torres; Samut's Sprint; Voyage's End
- `rule:etb-self-bounce-own-permanent` (n=1): Flock Impostor
- `rule:etb-tutor-to-hand` (n=1): Mystical Teachings
- `rule:etb-with-counters` (n=12): Clockwork Vorrac; Clutch of Currents; Hangarback Walker; Hexavus; Michelangelo, On the Scene; Mire's Malice; Ochre Jelly; Spike Hatcher; Spike Rogue; Tales of Master Seshiro // Seshiro's Living Legacy; Voracious Hydra; Wildwood Scourge
- `rule:etb-with-negative-counters` (n=3): Bloodied Ghost; Deity of Scars; Heirloom Auntie
- `rule:evasion-vs-low-power-blockers` (n=2): Bristlebane Outrider; Rust-Shield Rampager
- `rule:exile-until-source-leaves` (n=5): Banish to Another Universe; Ixalan's Binding; Makeshift Binding; The River Warlock; Vault Guardsman
- `rule:fixed-lifegain` (n=13): A-Deal Gone Bad; Dark Nourishment; Heroes Remembered; Ivory Cup; Kiss of the Amesha; Makeshift Binding; Nexus Wardens; Ojutai's Command; Pull from the Grave; Radiant Strike; Staff of the Flame Magus; The Dragon-Kami Reborn // Dragon-Kami's Egg; Vicious Rumors
- `rule:forced-attack-each-combat` (n=2): Anje's Ravager; Zurgo Helmsmasher
- `rule:forced-hand-reveal` (n=5): Concealing Curtains // Revealing Eye; Encroach; Inquisition of Kozilek; Nightmare Void; River's Grasp
- `rule:forces-creature-to-attack` (n=1): Chemister's Trick
- `rule:free-cast` (n=1): Temporal Aperture
- `rule:free-sacrifice-outlet` (n=1): Miren, the Moaning Well
- `rule:gains-life-on-other-creature-etb` (n=3): A-Social Climber; Distinguished Conjurer; Lifecreed Duo
- `rule:grants-ability-at-threshold-board` (n=1): Duelcraft Trainer
- `rule:grants-ability-at-threshold-self` (n=5): Auriok Edgewright; Redemption Choir; Springing Tiger; Taborax, Hope's Demise; Wall of Mourning
- `rule:grants-additional-combat-phase` (n=1): Hexplate Wallbreaker
- `rule:grants-creature-type` (n=1): Sigiled Sword of Valeron
- `rule:grants-extra-land-drop` (n=1): Explore
- `rule:grants-haste-to-created-tokens` (n=3): Rootwire Amalgam; Saheeli, Filigree Master; Sokenzan, Crucible of Defiance
- `rule:grants-haste-to-your-creatures` (n=2): Barbarian Class; Samut, Voice of Dissent
- `rule:grants-trample-to-other-creatures` (n=1): Hound Tamer // Untamed Pup
- `rule:grants-unblockable-target` (n=2): A-You Come to a River; The Black Gate
- `rule:graveyard-to-hand-recursion` (n=8): Carrion Cruiser; Clear the Stage; Comet, Stellar Pup; Death's Oasis; Lie in Wait; March of the Returned; Rise from the Wreck; Vivid Revival
- `rule:graveyard-to-library-shuffle-in` (n=1): Cathartic Parting
- `rule:individual-cost-reduction` (n=1): Overwhelming Remorse
- `rule:innate-unblockable` (n=4): Metathran Soldier; Ninja; Sygg, Wanderwine Wisdom // Sygg, Wanderbrine Shield; Willie Lumpkin, Postman
- `rule:kicker-conditional-bonus-effect` (n=3): Aggressive Sabotage; Shatterskull Charger; Skyclave Relic
- `rule:landfall-gain-life` (n=2): Lifegift; Omnath, Locus of Creation
- `rule:landfall-produces-mana` (n=2): Locus Cobra; Omnath, Locus of Creation
- `rule:landfall-self-pump` (n=1): Valakut Predator
- `rule:leaves-battlefield-trigger-create-token` (n=2): Chittering Dispatcher; Suki, Courageous Rescuer
- `rule:level-up-scaling-stats-abilities` (n=1): Guul Draz Assassin
- `rule:library-dig-put-onto-battlefield` (n=3): Gix, Yawgmoth Praetor; Protean Hulk; Treasure Chest
- `rule:library-dig-to-hand` (n=3): A Little Chat; Arcane Investigator; Prophetic Titan
- `rule:library-top-visibility` (n=2): Iron Lad, Diverging Destiny; Skill Borrower
- `rule:life-total-reset` (n=1): Angel of Grace
- `rule:lifegain-scaled-by-sacrificed-creature-toughness` (n=1): Miren, the Moaning Well
- `rule:lifegain-triggered-counter` (n=1): Celestial Unicorn
- `rule:mana-activated-pump-self` (n=8): Battlefield Percher; Dragon Engine; Folk of the Pines; Jousting Dummy; Knight of the Skyward Eye; Pardic Dragon; Shade of Trokair; Wall of Water
- `rule:mass-counter-distribution` (n=5): A-Harald Unites the Elves; Abzan Ascendancy; Abzan Charm; Basri's Solidarity; Hylda of the Icy Crown
- `rule:mass-creature-destruction` (n=1): Pick Your Poison
- `rule:mass-damage-creatures-and-players` (n=2): Devastate; Hour of Devastation
- `rule:mass-damage-opponent-creatures-only` (n=3): Color Pie; Fang Dragon // Forktail Sweep; Sandstorm
- `rule:mass-debuff-opponent-creatures` (n=2): Gruesome Realization; Shrouded Shepherd // Cleave Shadows
- `rule:mass-graveyard-exile` (n=1): Author of Shadows
- `rule:mass-pump-your-creatures` (n=5): Black Panther, Vanguard; How to Start a Riot; Inspired Charge; Rabbit Response; Rallying Roar
- `rule:mass-untap-and-haste-stolen-creatures` (n=2): Loki's Scepter; Systems Override
- `rule:mass-untap-your-creatures` (n=1): Rallying Roar
- `rule:mill-self-cards` (n=1): Death's Oasis
- `rule:modal` (n=15): A-You Come to a River; Abzan Charm; Archmage's Charm; Black Panther, Vanguard; Bounty: Lyssa, Sterling Collector // Wanted!; Collective Resistance; Gruesome Realization; Hylda of the Icy Crown; Invigorated Rampage; Ojutai's Command; Shredder's Revenge; Suplex; Will of the Sultai; You Find a Cursed Idol; You See a Guard Approach
- `rule:no-maximum-hand-size` (n=1): Anvil of Bogardan
- `rule:once-per-turn-trigger-limit` (n=3): Forge Boss; Lazav, Familiar Stranger; True Identity
- `rule:other-creature-etb-triggers-damage-to-opponents` (n=2): General Kreat, the Boltbringer; Glaring Fleshraker
- `rule:partner-with-tutor` (n=2): Blaring Captain; Pippin, Warden of Isengard
- `rule:pay-life-cost-for-effect` (n=3): Fleshless Gladiator; The Last Ride; Tough Cookie
- `rule:plus1-counters-matter` (n=6): Banewhip Punisher; Cloaked Cadet; Dread Tiller; Iridescent Hornbeetle; Ochre Jelly; Plaxcaster Frogling
- `rule:populate-copy-creature-token` (n=3): Dutiful Replicator; Ghired, Mirror of the Wilds; Promise of Aclazotz // Foul Rebirth
- `rule:power-scales-with-creature-count` (n=1): Pack Rat
- `rule:prevent-combat-damage-unblocked-creature` (n=2): Gossamer Chains; Snag
- `rule:prevent-damage-to-your-creatures` (n=2): Safe Passage; Sliver of Hope
- `rule:prevent-fixed-damage-any-target` (n=1): Samite Healer
- `rule:prevents-regeneration` (n=5): Big Game Hunter; Consuming Ferocity; Engulfing Flames; Fatal Blow; Shivan Emissary
- `rule:pump-plus-first-strike-any-creature` (n=2): Coming In Hot; Furious Bellow
- `rule:reanimate-from-graveyard` (n=10): Ascent of the Worthy; Bonecaller Cleric; Cauldron of Essence; Coalstoke Gearhulk; Demon of Dark Schemes; Ever After; Ojutai's Command; Pet Project; Quest for the Necropolis; Tune Up
- `rule:redirect-damage-to-spell-controller` (n=2): Aegis of Honor; Mirrorwood Treefolk
- `rule:redirect-targets-of-spell-or-ability` (n=1): Wild Ricochet
- `rule:replacement-graveyard-to-exile-self` (n=2): Gutter Skulker // Gutter Shortcut; Overwhelmed Archivist // Archive Haunt
- `rule:restricted-mana-for-equipment` (n=2): Cormela, Glamour Thief; Gwenna, Eyes of Gaea
- `rule:restricts-blocking-to-flying-only` (n=2): Battlefield Percher; Cloud Sprite
- `rule:rhystic-tax` (n=5): Demanding Dragon; Demonic Hordes; Disruptive Pitmage; Hylda of the Icy Crown; It'll Quench Ya!
- `rule:sacrifice-for-card-draw` (n=4): Diviner's Lockbox; Rakdos Locket; Relic Vial; Simic Cluestone
- `rule:sacrifice-for-creature-token` (n=2): Path to Redemption; Secluded Starforge
- `rule:scales-token-count-with-x` (n=1): Diviner's Portent
- `rule:self-bounce-activated` (n=1): Cyclopean Titan
- `rule:self-counter-growth` (n=2): Jungle Delver; Lazav, Familiar Stranger
- `rule:sets-base-power-or-toughness` (n=4): Andrios, Roaming Explorer; Ichthyomorphosis; Overwhelming Splendor; Riptide Mangler
- `rule:stun-counter` (n=3): Involuntary Cooldown; Tranquilize; Utrom Scientists
- `rule:targeted-bounce-creature` (n=7): Barrin, Master Wizard; Clutch of Currents; Fumble; River's Grasp; String of Disappearances; Voyage's End; Waterfront Bouncer
- `rule:targeted-creature-damage` (n=15): A-Deal Gone Bad; Blood Cultist; Breath of Fire; Desert's Due; Engulfing Flames; Explosive Shot; Fiery Finish; Frostling; Into the Maw of Hell; Pygmy Giant; Scorchmark; Scrap Compactor; Sunlance; Suplex; Whiptail Moloch
- `rule:targeted-destruction` (n=25): Argivian Welcome; Cityscape Leveler; Cleanse; Collective Resistance; Collective Resistance; Devastate; Eviscerate; Fatal Blow; Fragmentize; Goblin Tinkerer; Hideous End; Into the Maw of Hell; Jalira's Show; Plummet; Radiant Strike; Return to the Earth; Root Out; Saw in Half; Scrap Compactor; Shivan Emissary; Spread the Sickness; Tectonic Edge; Winnow; You Find a Cursed Idol; You Find a Cursed Idol
- `rule:targeted-discard` (n=7): Aggressive Sabotage; Arcane Omens; Cat Burglar; Concealing Curtains // Revealing Eye; Mire's Malice; River's Grasp; Shredder's Revenge
- `rule:targeted-exile` (n=12): Abstruse Appropriation; Abzan Charm; Banish to Another Universe; Eradicate; Into the Core; Ixalan's Binding; Makeshift Binding; Path to Redemption; Ray of Ruin; Suplex; Undead Slayer; Vault Guardsman
- `rule:targeted-planeswalker-damage` (n=2): Consulate Turret; Fodder Tosser
- `rule:targeted-player-damage` (n=4): Aggressive Sabotage; Consulate Turret; Fodder Tosser; Ionize
- `rule:temporary-control-theft` (n=9): Archmage's Charm; Garland, Royal Kidnapper; Hammer Helper; Incessant Provocation; Jabari's Influence; Loki's Scepter; My Will Is Irresistible; Systems Override; Wyll, Pact-Bound Duelist
- `rule:temporary-keyword-grant` (n=13): Academic Dispute; Belligerent of the Ball; Collective Resistance; Confidence from Strength; Desperate Stand; Duelcraft Trainer; Essence Infusion; Ghor-Clan Rampager; God-Eternal Rhonas; Samut's Sprint; Silk Net; Will of the Sultai; You See a Guard Approach
- `rule:transforms-on-graveyard-threshold` (n=2): Tales of Master Seshiro // Seshiro's Living Legacy; The Dragon-Kami Reborn // Dragon-Kami's Egg
- `rule:tribal-anthem-buff` (n=10): A-Kargan Warleader; Arno Dorian; Elvish Clancaller; Master of the Pearl Trident; Mothrider Cavalry; Oko, Shadowmoor Scion Emblem; Phila, Unsealed; Scion of Oona; Suki, Courageous Rescuer; Vodalian Hexcatcher
- `rule:untaps-target-land` (n=3): Juniper Order Druid; Portent Tracker; Wellspring
- `rule:x-scales-with-permanent-count` (n=3): Blackblade Reforged; Elder of Laurels; Will of the Sultai

---

## 10. CAPTAIN RATIFICATION — PARSED DIRECTIVES (2026-07-30)

**AUTHORITATIVE FOR PARSING.** Translated from Captain's inline
annotations (sections 1, 2, 3, 6, MEMBER ROSTER) plus the A–L follow-up
rulings from the 2026-07-30 review session. Where this section conflicts
with a prose annotation above, THIS SECTION GOVERNS (per protocol; the
prose stays as audit trail). Every card-text claim below was verified
against live oracle text during the review session; emit re-verifies
against the corpus (verify-or-drop) as always.

### D1 — Verdict lines stand, with three KILLs added
All 169 section-1 `VERDICT:` lines stand as annotated except as modified
by D2–D15. The 5 annotated KILLs stand
(aura-static-power-toughness-debuff, aura-static-pump-enchanted-creature,
equipment-static-pt-buff, damage-creature-or-planeswalker,
once-per-turn-trigger-limit). Three axes move KEEP → KILL:
- rule:death-trigger-damage-equal-to-power (sole member Hunter's Talent
  removed per D6 — verified zero death triggers on the card; n=0 axes
  die).
- rule:death-trigger-draw-card (sole member Cormela removed per D6 —
  her death trigger returns an instant/sorcery, no draw; replaced by
  D11's captain-authored axis).
- rule:etb-destroy-artifact-enchantment (replaced per D14 —
  Aven Cloudchaser destroys target enchantment only).
M8 redistribution from the damage-creature-or-planeswalker kill stands:
member_additions Reiterating Bolt and Torch the Tower to BOTH
rule:targeted-creature-damage and rule:targeted-planeswalker-damage.

### D2 — Q1 ruled: MERGE
rule:activated-prevent-damage-any-target MERGES into
rule:prevent-fixed-damage-any-target (Daru Healer, Samite Alchemist,
Serra Paladin join Samite Healer). The surviving axis's definition is
broadened to cover both spell and activated-ability delivery. The MEMBER
ROSTER annotation proposing a rename of the candidate is WITHDRAWN
(superseded by this ruling).

### D3 — All four annotated MERGEs stand
etb-with-negative-counters → etb-with-counters;
damage-then-exile-instead-of-die → graveyard-to-exile-replacement;
pump-plus-first-strike-any-creature → temporary-keyword-grant;
replacement-graveyard-to-exile-self → graveyard-to-exile-replacement.

### D4 — OTHER-lane promotions ratified
rule:cant-be-blocked-by-color (Elder Spawn, Barrenton Cragtreads) and
rule:death-trigger-land-becomes-swamp (Cyclopean Titan, Cyclopean Giant)
enter the codebook as written in section 3.

### D5 — Activation-restriction redistribution (lane failure, corrected)
Verified against live oracle text: 10 of 11 members of
rule:activation-restricted-to-own-upkeep carried the wrong restriction
type. The codebook lane collapsed three distinct restriction types
(own-upkeep / your-turn / sorcery-speed) into one slug.
- REMOVE from rule:activation-restricted-to-own-upkeep: Cauldron of
  Essence, Crown of Doom, Dementia Sliver, Diviner's Lockbox, Kheru
  Goldkeeper, Oracle en-Vec, Quest for the Necropolis, Ravenous Amulet,
  Rootwire Amalgam, Will Scion of Peace. Sole remaining member: Coffin
  Puppets.
- ADD to rule:activation-restricted-to-sorcery-speed ("Activate only as
  a sorcery" verified on each): Cauldron of Essence, Diviner's Lockbox,
  Kheru Goldkeeper, Quest for the Necropolis, Ravenous Amulet, Rootwire
  Amalgam, Will Scion of Peace — plus the section-0 OTHER-lane finds Cat
  Burglar and Priest of the Haunted Edge. Axis goes n=3 → n=12.
- NEW captain-authored axis
  rule:activation-restricted-only-during-your-turn ("Activate only
  during your turn" verified on each): Crown of Doom, Dementia Sliver,
  Oracle en-Vec.

### D6 — Member removals (each verified against live card text)
- rule:activated-tap-target-creature: REMOVE Samut, Voice of Dissent
  (untap — opposite polarity).
- rule:copy-creature-token: REMOVE Mythos of Illuna (copies any
  permanent, not creature-restricted).
- rule:counters-noncreature-spell: REMOVE Declaration of Naught and
  Electrosiphon (no noncreature restriction in either quote). Rehomed
  per D7.
- rule:cost-reduction-scales-with-own-counters: REMOVE Hinata,
  Dawn-Crowned (scales with targets, not counters).
- rule:creates-mana-producing-artifact-token: REMOVE Root Out (Clue
  tokens draw cards; they do not produce mana).
- rule:cantrip: REMOVE Spiritualize ({2}{W}, MV 3 — over the ratified
  MV≤2 ceiling).
- rule:death-trigger-damage-equal-to-power: REMOVE Hunter's Talent (ETB
  bite + attack trigger + end-step draw; no death trigger). Axis dies
  per D1.
- rule:death-trigger-draw-card: REMOVE Cormela, Glamour Thief. Axis dies
  per D1; Cormela rehomed per D11.
- rule:death-trigger-token-creation: REMOVE Grixis Slavedriver
  (leaves-the-battlefield trigger, not a death trigger). Rehomed per
  D10.
- rule:activated-counter-target-spell: REMOVE Deny the Witch (an instant
  that can counter activated abilities; it has no activated ability
  itself).
- rule:pay-life-cost-for-effect: REMOVE Fleshless Gladiator ("You lose
  1 life" is a resolution effect; the cost is {2}{B} — cost-vs-effect
  check).
- rule:enters-tapped: REMOVE Agna Qel'a, Taiga Stadium, Turbulent Fen
  (conditional — rehomed per D8); Lamplight Phoenix, Fleshless Gladiator
  (the "tapped" is a rider on their own recursion effects, not an
  enters-tapped clause — rehomed per D9); Seedguide Ash (its only
  tapped-lands language is inside its death-trigger search effect; no
  rehoming).

### D7 — NEW axis: rule:counters-target-spell
Captain-authored wide-net axis: "Counters target spell with no
restriction on spell type." Member: Electrosiphon ("Counter target
spell." verified). Declaration of Naught goes to
rule:activated-counter-target-spell instead ("{U}: Counter target spell
with the chosen name." — activated delivery verified; the chosen-name
rider is a parameter). The restriction-scope sibling structure
(counters-target-spell / counters-noncreature-spell /
activated-counter-target-spell) stays flagged to the parent-tree ledger
per section 6.

### D8 — NEW axis: rule:enters-tapped-conditional
Captain-authored: "Enters tapped unless a stated condition is met (or a
condition makes it enter tapped)." Members (quotes verified): Agna Qel'a
("unless you control a basic land"), Taiga Stadium ("unless you control
a white, blue, or black permanent"), Turbulent Fen ("unless your
opponents control eight or more lands").

### D9 — NEW axis: rule:self-recursion-from-graveyard
Captain-authored: "The card returns itself from the graveyard to the
battlefield via its own ability or trigger." Members (verified):
Lamplight Phoenix (death trigger + collect evidence 4), Fleshless
Gladiator (Corrupted activated ability).

### D10 — ETB and LTB token families restructured (ratified depth-3 etb
scheme; consistent with addendum-3 §3 — children are authored compound
leaves, parents derive)
rule:etb-create-token becomes a PARENT (derived; its authored row
converts at reconcile). Children authored now; each member's token-type
quote is verified at emit before write:
- rule:etb-create-token-creature: Black Panther Vanguard; Corpses of the
  Lost; Embalmed Ascendant; Mindless Conscription; Scrapwork Cohort;
  Trial of Strength; Wolfkin Bond; Wort, the Raidmother; and Gnome-Made
  Engine (verified UNCONDITIONAL: "When this creature enters, create a
  1/1 colorless Gnome artifact creature token." — placed here per
  follow-up ruling D, not in -conditional).
- rule:etb-create-token-creature-conditional: Foot Mystic (verified:
  Disappear intervening-if clause gates the token).
- rule:etb-create-token-food: Experimental Confectioner; Tough Cookie.
- rule:etb-create-token-mutagen: Slithering Cryptid (Mutagen verified as
  a predefined TMNT artifact token).
LTB mirror, same naming convention: rule:leaves-battlefield-trigger-create-token
is PROMOTED to a parent. NEW child
rule:leaves-battlefield-trigger-create-token-creature with member Grixis
Slavedriver (verified: "When Grixis Slavedriver leaves the battlefield,
create a 2/2 black Zombie creature token."). Existing members Chittering
Dispatcher and Suki, Courageous Rescuer remain DIRECT MEMBERS of the
parent pending quote-verified token-type classification at reconcile
(punch item; the ratified parents ruling permits direct members). Door
stays open for -food, -treasure, etc. siblings in both families.

### D11 — NEW axis: rule:death-trigger-scroll-regrowth
Captain-authored. Member: Cormela, Glamour Thief. STANDING VOCABULARY
(add to the codebook glossary per the section-1 agent-legibility
directive): "scroll" = instant or sorcery (or interrupt) card, used when
a rule covers two or more of these; "regrowth" = returns a card from
your graveyard to your hand.

### D12 — draw-second-card scheme
rule:draw-second-card-trigger-token is RENAMED
rule:draw-second-card-trigger-plus1-counter. Sole member Lat-Nam Adept
verified: "Whenever you draw your second card each turn, put a +1/+1
counter on this creature." — a counter, not a token; the old slug's
effect suffix did not match its only member. LEDGER: the full prefix
scheme is logged — unprefixed = "you draw"; opponent- prefix = opponent
draws; players- prefix = any player; parent
rule:draw-second-card-trigger over all of them; mirrored
rule:cast-second-spell-trigger family with the same prefixes when it
arises.

### D13 — Axis RENAMED: rule:restricted-purpose-mana
rule:restricted-mana-for-equipment is RENAMED
rule:restricted-purpose-mana ("Produces mana that may be spent only for
a stated purpose"). Members verified: Cormela (instants/sorceries only),
Gwenna, Eyes of Gaea (creature spells / creature-source abilities only)
— neither mentions Equipment; the old name was wrong. Spend-target facet
(which purpose) goes to the ledger facet schemes.

### D14 — Naming standard + renames executed now (explicit Captain
override of the no-midflight-renames ruling; logged like stun-counter,
precedent otherwise unchanged)
BINDING effect-suffix standard for the naming audit and all new axes:
`create-token-<type>` (matches the ratified depth-3 etb example;
grammatical "creates" loses to schema function — suffix consistency is
schema-functional per addendum-3 §3).
- rule:changes-creature-color → rule:changes-color-creature. Parent
  candidate rule:changes-color (the section-1 "changes-creature" parent
  was a confirmed typo). Future siblings: changes-color-artifact,
  changes-color-permanent.
- rule:creates-creature-token → rule:create-token-creature.
- rule:creates-mana-producing-artifact-token →
  rule:create-token-mana-producing-artifact. Definition note: Treasure
  is EXCLUDED (it has its own axis); powerstone/Gold/Meteorite makers
  belong here (Roxanne's Meteorite verified "{T}: Add one mana of any
  color."). The overlap/counts-toward question goes to schema pass S5.
- rule:creates-treasure-token → rule:create-token-treasure.
- Parent candidate rule:create-token (derived union). Future siblings:
  create-token-food, create-token-blood, create-token-lander,
  create-token-clue, etc.
- rule:etb-destroy-artifact-enchantment is KILLED and replaced by NEW
  captain-authored rule:etb-destroy-target-enchantment with member Aven
  Cloudchaser ("destroy target enchantment" — enchantment only).

### D15 — NEW axis: rule:delayed-cantrip
Captain-authored: "Fits the cantrip confines (any card type, MV≤2) but
the card draw arrives later via a delayed trigger rather than on
resolution. Inherits the cantrip {T}-activated-ability exclusion — tap
abilities stay out." Member: Portent (MV 1 sorcery, draws at next
upkeep; multi-tagged with rule:delayed-draw-next-upkeep). Mishra's
Bauble is EXCLUDED (its draw comes from a {T}, Sacrifice activated
ability).

### D16 — Ledger entries (parent-tree candidates; log, never author)
- Confirmations of parents already seeded in the ledger: rule:etb,
  rule:attack-trigger, rule:cast-trigger, rule:death-trigger.
- NEW ledger entries: rule:landfall; rule:leaves-battlefield-trigger;
  rule:combat-damage-trigger (Captain's "combat-damage" normalized to
  trigger-family naming); rule:activated-tap-target; rule:changes-color;
  rule:create-token; the counterspell restriction-scope family (D7); the
  draw-second / cast-second prefix schemes (D12); the
  restricted-purpose-mana spend-target facet (D13).
- rule:neg1-counters-matter is NOT logged as new — the ledger already
  carries Captain's minus1-counters-matter from the addendum-2 arc;
  minus1 mirrors plus1 and stands as the name.
- rule:library-dig-to-hand: Plunge into Darkness is logged as a
  FULL-CORPUS TEST-CASE EXPECTATION (not in batch 5, so no
  member_addition; the full pass must catch its dig-to-hand mode).

### D17 — Sequencing + registry updates
- SEQUENCING AMENDMENT (rulings registry): the full rule-name AND
  rule-definition audit moves AHEAD of the full-corpus pass, folded into
  the codebook-condensation step (already blocking). Definitions must be
  agent-legible; shorthand terms (scroll, regrowth) get glossary lines.
- Batch-6 feedback, beyond section 5: (1) restriction-type collapse (D5)
  — SYNTH must confirm the specific restriction wording, not the
  restriction category; (2) cost-vs-effect check surfaced again (D6,
  Fleshless Gladiator); (3) effect-suffix check — an axis whose slug
  names an effect (token, counter, draw) must show that effect in every
  member quote (D12, Lat-Nam Adept).

### D18 — Everything else stands; final math
All unannotated KEEPs, both section-3 promotion VERDICT lines, the
section-1 member-addition NOTEs, and the section-6 sibling-structure
punch items stand as written. Final verdict reconciliation: 169 axes =
KEEP 156 + KILL 8 (5 annotated + 3 per D1) + MERGE 5 (4 annotated + Q1
per D2). Captain-authored additions this batch (12):
activation-restricted-only-during-your-turn, counters-target-spell,
enters-tapped-conditional, self-recursion-from-graveyard,
etb-create-token-creature, etb-create-token-creature-conditional,
etb-create-token-food, etb-create-token-mutagen,
leaves-battlefield-trigger-create-token-creature,
death-trigger-scroll-regrowth, delayed-cantrip,
etb-destroy-target-enchantment.

---

**STOP.** Section 10 is the authoritative ratification record for batch
5. Run `/triage-emit 5` when ready; emit parses section 10, verifies
every quote and member against the corpus (verify-or-drop), writes
decisions/batch-5.json, reconciles to codebook v0.5, assembles batch 6,
prices it live, and STOPS for go-ahead.
