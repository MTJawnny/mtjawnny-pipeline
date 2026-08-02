# TRIAGE — Batch 4 (SUP full-pass, 2026-07-19)

Produced by Claude (SUP-class session) under the ratified SUP-TRIAGE-PROTOCOL,
reading `experiments/out/foundry/review/digest-batch-4.md` (166 axes: 131
confirming existing codebook v0.3 axes, 35 new candidates from free-lane
clustering; 1,225 OTHER-lane rows; 1,164 token groups) against the current
codebook (174 active axes). Every one of the 131+35 axes was read in full,
along with every OTHER-lane token group of size >= 8 (83 groups, spanning
every size tier from 8 up to 60 members) plus a further sample across the
remaining 2-7-member groups, before any verdict was written. Nothing here is
load-bearing until Captain ratifies.

**How to use this doc:** section 1 is the full per-axis verdict list --
every one of the 166 axes has an explicit `VERDICT:` line (per this batch's
instructions, a stricter convention than batches 2-3's "untouched = KEEP"
default). Skim it, strike anything wrong, initial the rest. Section 2 is the
one question. Section 4 is the honesty check -- verify those 30 rows against
card text before trusting the rest. Section 0 has two new, real findings
this batch worth your particular attention (a category-confusion pattern
distinct from batch 3's polarity inversions, and a data-completeness bug).
When you hand this back annotated, `/triage-emit 4` parses it into
`decisions/batch-4.json`.

**Verdict counts:** KEEP 158 (131 existing confirmations + 27 new) · KILL 2
· MERGE 5 · QUESTION 1 = 166, one verdict per axis, verified
programmatically against the enriched batch's actual 166-slug list (zero
duplicates, zero omissions).

---

## 0. Findings, interpreted

- **New failure pattern this batch: activated-vs-triggered / cost-vs-effect
  conflation, concentrated almost entirely in one axis.**
  `rule:activated-tap-target-creature` (n=16) is the worst single-axis
  quality problem found across all four batches so far: **9 of its 16
  members do not fit the axis's own definition** ("an activated ability
  that taps a target creature"). Three distinct sub-mistakes, all variants
  of the same root cause -- the two-lane SYNTH pass matched on "the word
  'tap' appears near 'target creature'" without checking *what kind of
  ability* it is or *what gets tapped*:
  - **Wrong ability type** (triggered, not activated): **Eddymurk Crab**
    and **Glaring Aegis** are ETB triggers ("When this creature/Aura
    enters, tap..."); **Hammers of Moradin** is an attack trigger
    ("Whenever this creature attacks..."); **Summon: Valefor** is a Saga
    chapter trigger. None of the four are things a player chooses to pay a
    cost and activate.
  - **Cost tapped the source, not the target** (**Crossbow Infantry**):
    `"{T}: This creature deals 1 damage to target attacking or blocking
    creature."` -- the `{T}` is the activation cost (tapping ITSELF); the
    *effect* deals damage, it does not tap the target creature at all.
  - **Wrong object class targeted**: **Relic Barrier** ("{T}: Tap target
    artifact.") and **Rishadan Port** ("{1}, {T}: Tap target land.") are
    genuinely activated tap-abilities, just not creature-targeted.
    **Tamiyo, Field Researcher**'s loyalty ability targets "up to two
    target nonland permanents" -- broader than creature.
  - **Arena**'s quote shows no activation cost at all in the enriched text.
  Net: 7 correct members remain (Blinding Mage, Blinding Souleater, Gavony
  Trapper, Loxodon Mystic, Sigardian Priest, Solstice Zealot, Stormscape
  Apprentice). The axis concept is sound and worth keeping -- flagged as a
  member-removal, not a kill (see section 1a). **Batch-5 SYNTH prompt
  recommendation in section 5.**
  VERDICT: looks good
- Two smaller instances of the same "wrong object" pattern, both flagged
  as single-member removals rather than axis-level problems:
    `rule:mass-damage-opponent-creatures-only`'s member **Klothys, God of
    Destiny** actually deals damage to *opponents* ("deals 2 damage to each
  opponent"), not to opponents' creatures; `rule:targeted-creature-damage`'s
  member **Item Crate** deals damage to "any target," not specifically a
  creature (belongs under `rule:direct-damage-any-target`).
  VERDICT:Yes move them. 
- **A real data-completeness bug, found while verifying the override
  sample, not a judgment call.** `foundry_common.py`'s
  `build_review_card_record()` (used by `foundry_emit.py` to build
  `review/batch-4.json`'s top-level `cards` dict) reads `card["oracle_text"]`
  directly off the raw corpus record. For 21 of this batch's 1,016 cards --
  every one of them a multi-face layout (transform, modal_dfc, adventure,
  prepare) -- Scryfall's root-level `oracle_text` field is empty; the real
  text only exists per-face. `foundry_enrich.py`'s own analysis correctly
  does all-faces text assembly elsewhere (that's why the digest's quotes for
  these cards are all correct), but the `cards[oid].oracle_text` field
  shipped in `review/batch-4.json` itself is blank for these 21 entries
  (though the separately-extracted `faces` field on each record does hold
  the per-face text, so it's not unrecoverable). Caught this while verifying
  the override sample's **Faithbound Judge // Sinner's Judgment** quote --
  it failed a naive verbatim check against `cards[oid].oracle_text` (empty
  string) and only passed once I read the same card's face text from the
  per-member enrichment snapshot instead. Flagging for a DET session fix
  (concatenate `card_faces[*].oracle_text` when the root field is empty,
  per this repo's own DFC/all-faces rules) rather than fixing it mid-triage.
  VERDICT: Yes hold until DET session. We may inject our own oracle text for these cards as it's important that every tool we build off this engine is able to surface cards on the back of other cards quickly and clearly
- **Two exact-duplicate / resurrected-pattern candidates, high confidence
  merges.** `rule:grants-temporary-hexproof` (n=2: Mizzium Skin, Plumecreed
  Escort) is a near-verbatim resurrection of the batch-3-killed
  `rule:grants-temporary-hexproof-target-creature`, which was explicitly
  superseded by the broader `rule:temporary-keyword-grant` per Captain's 3d
  ruling that same batch -- both members merge cleanly into that active
  axis. `rule:etb-grants-energy-counters` (n=3) is a duplicate of the
  existing `rule:gives-energy-counters-immediately` (registered batch-3 Q2,
  same "ETB, immediate/unconditional energy counters" definition) --
  absorbing. `rule:replacement-exile-instead-of-graveyard` (n=2) likewise
  duplicates the existing `rule:graveyard-to-exile-replacement`. All three
  are proposed MERGEs in section 1b, not kills -- their members are real,
  they just already have a home.
  VERDICT: Yes for `rule:grants-temporary-hexproof` &  `rule:grants-temporary-hexproof-target-creature` fold into `rule:temporary-keyword-grant`, you can fold any grants-temporary keyword rule into `rule:temporary-keyword-grant`. Then we'll need another mechanism or rule tag that describes what keyword that is given. something like `rule:gives-hexproof`. that way each card that gives a card hexproof is found, and then there's additional rule tags that determine how the keyword is given. either until end of turn, end of next turn, as an anthem style buff, or a hexproof counter. then there's another rule that determines if its only target creature, up to one or more, or all creatures you control, or all creatures in play.

  `rule:etb-grants-energy-counters` merge into `rule:gives-energy-counters-immediately`. yes merge. the card with a etb should have `rule:etb` or something similar to distinguish the idea that it is giving enery counters due to etb.

Yes on `rule:graveyard-to-exile-replacement` merge

- **Two more merges, cost-shape/stat-target parameters of an existing
  axis rather than new mechanisms**: `rule:activated-pump-with-self-damage-cost`
  and `rule:activated-self-toughness-pump` both fold into
  `rule:mana-activated-pump-self`, per the standing cost-shape-rider
  precedent (batch 2/3's sacrifice/discard-as-additional-cost kills) and
  the etb-with-counters polarity-parameter precedent.
  VERDICT: I'll need to see the examples for this to make an accurate verdict 
- **Two kills, third+ occurrence of an already-established pattern.**
  `rule:additional-cost-sacrifice-permanent` and
  `rule:additional-cost-discard-a-card` are both procedural cost-shape
  riders -- the SAME standing precedent that killed
  `rule:sacrifice-creature-as-additional-cost` (batch 2) and
  `rule:sacrifice-as-additional-cost` (batch 3). The payoff effect a card
  gets is the axis; how it pays for that effect (sacrifice vs. discard vs.
  mana) is not, per two prior batches' rulings.
  VERDICT:Whenever we merge broad concepts that connect a card, we must also build out additional rules that signify each card for it's mechanically unique requirenment. `rule:additional-cost-sacrifice-permanent` vs `rule:sacrifice-creature-as-additional-cost`. If we merge all cards in `rule:sacrifice-creature-as-additional-cost` to `rule:additional-cost-sacrifice-permanent`. on the cards that were marked as `rule:sacrifice-creature-as-additional-cost`, we must add a rule like `rule:sacrifice-creature-condition` or `rule:sacrifice-creature-infinite`. based on the fact that it's specifcally a creature being sacrifice, and it is either a one shot sacrifice or an infinites sacrifice outlet. how a card pays for an effect should be an axis. We want to build wide net rulings as well as ganular rulings that distinguish cards within the same theme.
- **M8 per-object-class coverage gap (not a wrong inclusion, a missing
  one).** `rule:targeted-player-damage`'s member **Breya, Etherium Shaper**
  ("deals 3 damage to target player or planeswalker") is a mixed-target
  card that should also carry `rule:targeted-planeswalker-damage` per the
  ratified M8 rule (mixed targets get multiple tags), but currently doesn't.
  Flagged as a reconcile-time addition, not a verdict change.
  VERDICT:Yes rectify. You're exactly right. it should have both.
- **OTHER-lane: zero promotions, same as batches 2 and 3.** Read every
  group of size >= 8 (83 groups spanning the full 8-to-60 range) plus a
  broad sample of smaller groups. Same pattern all three of the last
  batches: generic 2-3-token-overlap collisions across unrelated mechanics
  (e.g. `[count/scal]`'s 60 members share nothing but "something scales
  with some count of something" -- see the strategic question in section 2).
  No coherent multi-card family found beyond what full-label-set free-lane
  clustering and lane=codebook already captured.
  VERDICT: that fine
- **Alchemy / non-normal-layout anomalies (23 + 79 rows)**: sampled a
  cross-section, no additional issues beyond what's already covered above
  (the transform/modal_dfc/adventure cards in the non-normal-layout list
  overlap heavily with the 21-card oracle_text bug list). No axis-level
  action needed beyond that bug report.
  VERDICT: ok

---

## 1. Per-axis verdicts (166)

Every axis gets its own `VERDICT:` line per this batch's instructions.
Unflagged entries are confident KEEPs (lane=codebook resolution verified
against the corpus for existing confirmations; a coherent 2+-distinct-card
free-lane cluster with a sound, non-duplicate definition for new
candidates). Flagged entries carry member-removal or merge/kill/question
notes inline.

### 1a. Existing codebook confirmations (131)

- `rule:activated-draw-a-card` (n=2) — VERDICT: KEEP
- `rule:activated-tap-target-creature` (n=16) — **VERDICT: KEEP** — NOTE: remove member(s) Arena, Crossbow Infantry, Eddymurk Crab, Glaring Aegis, Hammers of Moradin, Relic Barrier, Rishadan Port, Summon: Valefor, Tamiyo, Field Researcher — 9 of 16 members do not fit "activated ability that taps a TARGET creature" (see section 0): Eddymurk Crab / Glaring Aegis are ETB triggers, Hammers of Moradin is an attack trigger, Summon: Valefor is a Saga chapter trigger -- none are player-activated. Crossbow Infantry's {T} is an activation COST (taps the SOURCE); its EFFECT deals damage, not tapping the target. Relic Barrier taps an artifact and Rishadan Port taps a land, not a creature. Tamiyo's ability targets "up to two target nonland permanents" -- broader than creature. Arena's quote shows no activation cost at all.
- `rule:alternate-win-condition` (n=4) — VERDICT: KEEP
- `rule:animates-land-into-creature` (n=5) — VERDICT: KEEP
- `rule:attack-trigger-create-token` (n=4) — VERDICT: KEEP
- `rule:attack-trigger-loot` (n=1) — VERDICT: KEEP
- `rule:attack-trigger-mass-pump-attackers` (n=3) — VERDICT: KEEP
- `rule:attack-trigger-self-counter-growth` (n=2) — VERDICT: KEEP
- `rule:burst-draw` (n=8) — VERDICT: KEEP
- `rule:cannot-block-restriction` (n=6) — VERDICT: KEEP
- `rule:cant-be-countered` (n=5) — VERDICT: KEEP
- `rule:cantrip` (n=13) — VERDICT: KEEP
- `rule:cast-trigger-card-draw` (n=3) — VERDICT: KEEP
- `rule:changes-creature-color` (n=3) — VERDICT: KEEP
- `rule:charge-counter-accumulation` (n=5) — VERDICT: KEEP
- `rule:cheat-creature-into-play` (n=2) — VERDICT: KEEP
- `rule:choose-color-on-etb` (n=3) — VERDICT: KEEP
- `rule:choose-creature-type-on-etb` (n=2) — VERDICT: KEEP
- `rule:combat-damage-to-creature-triggers-self-counter` (n=2) — VERDICT: KEEP
- `rule:combat-damage-triggers-loot` (n=2) — VERDICT: KEEP
- `rule:combat-trick-pump-own-creature` (n=13) — VERDICT: KEEP
- `rule:compensates-controller-with-token` (n=4) — VERDICT: KEEP
- `rule:conditional-buff-by-color` (n=1) — VERDICT: KEEP
- `rule:conditional-creature-status` (n=2) — VERDICT: KEEP
- `rule:conditional-first-strike-your-turn` (n=2) — VERDICT: KEEP
- `rule:copies-cast-spell` (n=7) — VERDICT: KEEP
- `rule:copy-creature-token` (n=9) — VERDICT: KEEP
- `rule:cost-reduction` (n=3) — VERDICT: KEEP
- `rule:creates-creature-token` (n=32) — VERDICT: KEEP
- `rule:creates-mana-producing-artifact-token` (n=5) — VERDICT: KEEP
- `rule:creates-treasure-token` (n=12) — VERDICT: KEEP
- `rule:damage-divided-among-multiple-targets` (n=5) — VERDICT: KEEP
- `rule:damage-scales-with-creature-count` (n=1) — VERDICT: KEEP
- `rule:death-trigger-counter-transfer` (n=1) — VERDICT: KEEP
- `rule:death-trigger-mass-debuff` (n=1) — VERDICT: KEEP
- `rule:death-trigger-token-creation` (n=4) — VERDICT: KEEP
- `rule:delayed-destroy-trigger` (n=2) — VERDICT: KEEP
- `rule:delayed-draw-next-upkeep` (n=1) — VERDICT: KEEP
- `rule:direct-damage-any-target` (n=26) — VERDICT: KEEP
- `rule:doubles-counter-placement` (n=1) — VERDICT: KEEP
- `rule:drain-life` (n=9) — VERDICT: KEEP
- `rule:drain-on-creature-death` (n=2) — VERDICT: KEEP
- `rule:enters-tapped` (n=28) — VERDICT: KEEP
- `rule:equipment-etb-creates-and-attaches-token` (n=3) — VERDICT: KEEP
- `rule:etb-and-attack-trigger` (n=1) — VERDICT: KEEP
- `rule:etb-bounce-other-creature` (n=1) — VERDICT: KEEP
- `rule:etb-counter-on-other-creature` (n=4) — VERDICT: KEEP
- `rule:etb-create-token` (n=15) — VERDICT: KEEP
- `rule:etb-destroy-artifact-enchantment` (n=1) — VERDICT: KEEP
- `rule:etb-draw-card` (n=6) — VERDICT: KEEP
- `rule:etb-exile-graveyard-card` (n=4) — VERDICT: KEEP
- `rule:etb-gain-life` (n=5) — VERDICT: KEEP
- `rule:etb-loot` (n=4) — VERDICT: KEEP
- `rule:etb-modal-choice` (n=3) — VERDICT: KEEP
- `rule:etb-scry` (n=4) — VERDICT: KEEP
- `rule:etb-self-bounce-own-permanent` (n=2) — VERDICT: KEEP
- `rule:etb-tutor-to-hand` (n=1) — VERDICT: KEEP
- `rule:etb-with-counters` (n=14) — VERDICT: KEEP
- `rule:exile-until-source-leaves` (n=4) — VERDICT: KEEP
- `rule:fixed-lifegain` (n=9) — VERDICT: KEEP
- `rule:forced-hand-reveal` (n=4) — VERDICT: KEEP
- `rule:forces-creature-to-attack` (n=1) — VERDICT: KEEP
- `rule:forces-opponent-sacrifice` (n=3) — VERDICT: KEEP
- `rule:free-cast` (n=6) — VERDICT: KEEP
- `rule:free-sacrifice-outlet` (n=1) — VERDICT: KEEP
- `rule:gives-energy-counters-immediately` (n=1) — VERDICT: KEEP
- `rule:grants-ability-at-threshold-board` (n=2) — VERDICT: KEEP
- `rule:grants-ability-at-threshold-self` (n=8) — VERDICT: KEEP
- `rule:grants-controller-hexproof` (n=1) — VERDICT: KEEP
- `rule:grants-creature-type` (n=2) — VERDICT: KEEP
- `rule:grants-extra-land-drop` (n=1) — VERDICT: KEEP
- `rule:grants-trample-to-other-creatures` (n=1) — VERDICT: KEEP
- `rule:grants-unblockable` (n=1) — VERDICT: KEEP
- `rule:grants-unblockable-target` (n=4) — VERDICT: KEEP
- `rule:graveyard-to-exile-replacement` (n=1) — VERDICT: KEEP
- `rule:graveyard-to-hand-recursion` (n=4) — VERDICT: KEEP
- `rule:individual-cost-reduction` (n=4) — VERDICT: KEEP
- `rule:innate-unblockable` (n=3) — VERDICT: KEEP
- `rule:kicker-conditional-bonus-effect` (n=5) — VERDICT: KEEP
- `rule:land-fetch-to-battlefield` (n=6) — VERDICT: KEEP
- `rule:level-up-scaling-stats-abilities` (n=1) — VERDICT: KEEP
- `rule:library-dig-put-onto-battlefield` (n=1) — VERDICT: KEEP
- `rule:library-dig-to-hand` (n=1) — VERDICT: KEEP
- `rule:library-top-visibility` (n=4) — VERDICT: KEEP
- `rule:mana-activated-pump-self` (n=10) — VERDICT: KEEP
- `rule:mass-counter-distribution` (n=8) — VERDICT: KEEP
- `rule:mass-creature-destruction` (n=1) — VERDICT: KEEP
- `rule:mass-damage-creatures-and-players` (n=2) — VERDICT: KEEP
- `rule:mass-damage-opponent-creatures-only` (n=3) — **VERDICT: KEEP** — NOTE: remove member(s) Klothys, God of Destiny — quote is "Klothys deals 2 damage to each opponent" -- player damage, not creature damage; axis requires damage to opponents' creatures
- `rule:mass-graveyard-exile` (n=4) — VERDICT: KEEP
- `rule:mass-untap-and-haste-stolen-creatures` (n=1) — VERDICT: KEEP
- `rule:mass-untap-your-creatures` (n=2) — VERDICT: KEEP
- `rule:mill-self-cards` (n=1) — VERDICT: KEEP
- `rule:modal` (n=21) — VERDICT: KEEP
- `rule:partner-with-tutor` (n=1) — VERDICT: KEEP
- `rule:pay-life-cost-for-effect` (n=4) — VERDICT: KEEP
- `rule:plus1-counters-matter` (n=7) — VERDICT: KEEP
- `rule:power-scales-with-creature-count` (n=1) — VERDICT: KEEP
- `rule:prevent-fixed-damage-any-target` (n=3) — VERDICT: KEEP
- `rule:prevents-regeneration` (n=1) — VERDICT: KEEP
- `rule:prevents-target-untap-next-step` (n=3) — VERDICT: KEEP
- `rule:reanimate-from-graveyard` (n=12) — VERDICT: KEEP
- `rule:restricted-mana-for-equipment` (n=3) — VERDICT: KEEP
- `rule:restricts-opponent-search` (n=1) — VERDICT: KEEP
- `rule:rhystic-tax` (n=4) — VERDICT: KEEP
- `rule:sacrifice-for-card-draw` (n=5) — VERDICT: KEEP
- `rule:sacrifice-for-creature-token` (n=1) — VERDICT: KEEP
- `rule:self-bounce-activated` (n=1) — VERDICT: KEEP
- `rule:self-counter-growth` (n=1) — VERDICT: KEEP
- `rule:self-mana-ability-grants-keyword` (n=2) — VERDICT: KEEP
- `rule:sets-base-power-or-toughness` (n=1) — VERDICT: KEEP
- `rule:stun-counter` (n=3) — VERDICT: KEEP
- `rule:symmetric-hand-refill` (n=2) — VERDICT: KEEP
- `rule:targeted-bounce-creature` (n=4) — VERDICT: KEEP
- `rule:targeted-creature-damage` (n=13) — **VERDICT: KEEP** — NOTE: remove member(s) Item Crate — quote is "It deals 2 damage to any target" -- any-target, not specifically a creature; belongs under rule:direct-damage-any-target instead
- `rule:targeted-destruction` (n=37) — VERDICT: KEEP
- `rule:targeted-discard` (n=4) — VERDICT: KEEP
- `rule:targeted-exile` (n=16) — VERDICT: KEEP
- `rule:targeted-planeswalker-damage` (n=1) — **VERDICT: KEEP** — NOTE: Breya, Etherium Shaper (quote: "Breya deals 3 damage to target player or planeswalker") is a mixed player/planeswalker-target card tagged only under rule:targeted-player-damage this batch. Per the ratified M8 per-object-class rule, mixed-target cards get multiple tags -- add Breya as a member here too at reconcile.
- `rule:targeted-player-damage` (n=3) — VERDICT: KEEP
- `rule:taxes-opponent-spell-cost` (n=1) — VERDICT: KEEP
- `rule:temporary-control-theft` (n=5) — VERDICT: KEEP
- `rule:temporary-keyword-grant` (n=4) — VERDICT: KEEP
- `rule:the-ring-tempts-you` (n=1) — VERDICT: KEEP
- `rule:tribal-anthem-buff` (n=7) — VERDICT: KEEP
- `rule:triggers-on-cast-instant-sorcery` (n=3) — VERDICT: KEEP
- `rule:tutor-basic-land-to-hand` (n=2) — VERDICT: KEEP
- `rule:tutor-to-library-top` (n=2) — VERDICT: KEEP
- `rule:untaps-target-land` (n=2) — VERDICT: KEEP
- `rule:upkeep-surveil` (n=2) — VERDICT: KEEP
- `rule:x-scales-with-permanent-count` (n=2) — VERDICT: KEEP

### 1b. New free-lane candidates (35)

- `rule:activated-pump-with-self-damage-cost` (n=2) — **VERDICT: MERGE INTO `rule:mana-activated-pump-self`** — same core mechanism (activated, mana cost, self-pump); self-damage is a cost-shape/drawback parameter, not a distinct axis, per the established cost-shape-rider precedent
- `rule:activated-self-toughness-pump` (n=2) — **VERDICT: MERGE INTO `rule:mana-activated-pump-self`** — same core mechanism, toughness-only is a stat-target parameter (codebook already keeps such variants merged within one axis, e.g. etb-with-counters's +1/+1 vs -1/-1 members per batch-3 ruling)
- `rule:activation-restricted-to-own-upkeep` (n=2) — VERDICT: KEEP
- `rule:additional-cost-discard-a-card` (n=2) — **VERDICT: KILL** — procedural cost-shape rider, same standing as the b2/b3 sacrifice-as-additional-cost kills
- `rule:additional-cost-sacrifice-permanent` (n=4) — **VERDICT: KILL** — procedural cost-shape rider (3rd occurrence of the sac-as-additional-cost pattern killed in b2/b3, e.g. rule:sacrifice-creature-as-additional-cost, rule:sacrifice-as-additional-cost); the payoff effect is the axis, not how it is paid for
- `rule:alt-cost-exile-card-from-hand` (n=2) — VERDICT: KEEP
- `rule:alt-cost-sacrifice-lands` (n=2) — VERDICT: KEEP
- `rule:attack-trigger-buff-other-attacker-counters` (n=2) — VERDICT: KEEP
- `rule:attack-trigger-pump-any-creature` (n=2) — VERDICT: KEEP
- `rule:attack-trigger-pump-scaled-by-creature-count` (n=2) — VERDICT: KEEP
- `rule:buff-scales-with-land-type-count` (n=2) — VERDICT: KEEP
- `rule:cast-from-exile-trigger` (n=2) — VERDICT: KEEP
- `rule:combat-trigger-auto-attach-equipment` (n=2) — VERDICT: KEEP
- `rule:counter-removal-as-activation-cost` (n=2) — VERDICT: KEEP
- `rule:counters-noncreature-spell` (n=2) — VERDICT: KEEP
- `rule:draw-second-card-trigger-token` (n=2) — VERDICT: KEEP
- `rule:draw-trigger-self-counter-growth` (n=2) — VERDICT: KEEP
- `rule:etb-grants-energy-counters` (n=3) — **VERDICT: MERGE INTO `rule:gives-energy-counters-immediately`** — exact duplicate: both definitions are "ETB, immediate/unconditional energy counters" -- gives-energy-counters-immediately is the Captain-ratified Q2 name (registered batch 3); absorbs this candidate's 3 members
- `rule:etb-mass-pump-your-creatures` (n=2) — VERDICT: KEEP
- `rule:etb-shuffle-graveyard-cards-into-library` (n=2) — VERDICT: KEEP
- `rule:grants-temporary-hexproof` (n=2) — **VERDICT: MERGE INTO `rule:temporary-keyword-grant`** — exact resurrection of the batch-3-killed rule:grants-temporary-hexproof-target-creature, already superseded by this active axis per Captain's 3d ruling; both members (Mizzium Skin, Plumecreed Escort) are temporary-until-EOT hexproof grants
- `rule:graveyard-to-library-shuffle-in` (n=2) — VERDICT: KEEP
- `rule:landfall-self-pump` (n=3) — VERDICT: KEEP
- `rule:lifegain-scaled-by-sacrificed-creature-toughness` (n=2) — VERDICT: KEEP
- `rule:mass-pump-your-creatures` (n=3) — VERDICT: KEEP
- `rule:populate-copy-creature-token` (n=2) — VERDICT: KEEP
- `rule:prevents-target-blocking` (n=2) — VERDICT: KEEP
- `rule:redirect-targets-of-spell-or-ability` (n=2) — VERDICT: KEEP
- `rule:redirects-combat-damage-to-controller-and-self` (n=2) — VERDICT: KEEP
- `rule:replacement-exile-instead-of-graveyard` (n=2) — **VERDICT: MERGE INTO `rule:graveyard-to-exile-replacement`** — same continuous-replacement-effect definition ("would go to a graveyard, exiled instead"); the existing axis's "from anywhere" wording already covers both members
- `rule:replaces-death-with-exile` (n=2) — **VERDICT: QUESTION (Q1, see section 2)**
- `rule:restricts-blocking-to-flying-only` (n=3) — VERDICT: KEEP
- `rule:scales-token-count-with-x` (n=2) — VERDICT: KEEP
- `rule:tribal-death-trigger-condition` (n=2) — VERDICT: KEEP
- `rule:tutor-from-outside-game-to-hand` (n=2) — VERDICT: KEEP

---

## 2. QUESTIONS (1)

**Q1 — `rule:replaces-death-with-exile` (2: Bouncer's Beatdown, Incendiary
Flow) vs. existing `rule:graveyard-to-exile-replacement` (1: Faithbound
Judge // Sinner's Judgment).**
Same underlying replacement-effect text pattern ("would die / go to a
graveyard, exile instead") but arguably a different game vector: the
existing axis's sole member is self-protective (an Aura protecting itself
from graveyard hate), while this candidate's two members are removal-spell
riders that exile the *opponent's* creature instead of destroying it (an
upgrade over plain destruction, relevant against indestructible/recursion).
Same-concept-different-wording (merge, per batch-1 precedent), or a
"don't absorb, expand" case (different function: self-protection vs.
removal upgrade, different scope tag: self vs. opponent-stuff)?
→ RULE: merge-into-graveyard-to-exile-replacement / keep-separate: Merge

*(A second strategic, non-per-axis question -- whether to keep spawning
narrow "scales-with-X-count" siblings or consolidate under
`rule:x-scales-with-permanent-count` as one parameterized family -- is
raised in section 5 rather than counted here, since it's a batch-5 tooling
question, not a batch-4 verdict Captain needs to rule on to unblock emit.)*

---

## 3. OTHER-LANE PROMOTIONS

**None proposed this batch**, matching batches 2 and 3. Read all 83 token
groups with 8+ members (the full size range from 8 up to the largest,
`[count/scal]` at n=60) plus a broad sample of the remaining 2-7-member
groups (1,081 of the 1,164 total). Same pattern every batch running now:
generic 2-3-token-overlap collisions spanning unrelated mechanics (e.g.
`[combat/damage]`'s 49 members share nothing but the words "combat" and
"damage" -- everything from token-creation triggers to toughness-swap
effects to land-fetch triggers). Zero coherent multi-card families found
beyond what full-label-set free-lane clustering and lane=codebook already
captured as this batch's 131+35 axes.

---

## 4. OVERRIDE SPOT-CHECK — verify these 30 before trusting the rest

Fixed seed 20260722 (= 20260718 + batch 4), drawn from the 165 confident
calls (KEEP/KILL/MERGE; the 1 QUESTION excluded), via
`random.seed(20260722); random.sample(confident_calls, 30)` where
`confident_calls` is the alphabetically-sorted list of all 166 axis slugs
minus `rule:replaces-death-with-exile`. Every quote below was verified
programmatically against the card's actual oracle text in
`review/batch-4-enriched.json` (all 30 passed verbatim, after routing
around the section-0 oracle_text bug for the one DFC card in the sample --
see note below the table). Check each verdict against the card text. If
more than ~1 is wrong, distrust the lanes and tell me — loudly.

| Axis | Verdict | Sample member | Evidence quote |
|---|---|---|---|
| rule:self-counter-growth | KEEP | Consumptive Goo | "Put a +1/+1 counter on this creature." |
| rule:landfall-self-pump | KEEP | Grove Rumbler | "Landfall — Whenever a land you control enters, this creature gets +2/+2 until end of turn." |
| rule:attack-trigger-self-counter-growth | KEEP | Ash, Party Crasher | "Whenever Ash attacks, if two or more nonland permanents entered the battlefield under y…" |
| rule:upkeep-surveil | KEEP | Your Favorite Missing Character | "At the beginning of your upkeep, surveil 1." |
| rule:targeted-bounce-creature | KEEP | Eject | "Return target nonland permanent to its owner's hand." |
| rule:attack-trigger-loot | KEEP | Furtive Courier | "Whenever this creature attacks, draw a card, then discard a card." |
| rule:etb-bounce-other-creature | KEEP | Iceridge Serpent | "When this creature enters, return target creature an opponent controls to its owner's h…" |
| rule:choose-creature-type-on-etb | KEEP | Instruments of War | "As this artifact enters, choose a creature type." |
| rule:cannot-block-restriction | KEEP | Veilborn Ghoul | "This creature can't block." |
| rule:lifegain-scaled-by-sacrificed-creature-toughness | KEEP | Momentous Fall | "then you gain life equal to its toughness" |
| rule:targeted-discard | KEEP | Dread Fugue | "You choose a nonland card from it [with mana value 2 or less]. That player discards tha…" |
| rule:triggers-on-cast-instant-sorcery | KEEP | Aziza, Mage Tower Captain | "Whenever you cast an instant or sorcery spell, you may tap three untapped creatures you…" |
| rule:library-dig-to-hand | KEEP | Pillage the Bog | "Put one of them into your hand and the rest on the bottom of your library in a random o…" |
| rule:etb-loot | KEEP | Ox of Agonas | "When this creature enters, discard your hand, then draw three cards." |
| rule:compensates-controller-with-token | KEEP | Harsh Annotation | "Its controller creates a 1/1 white and black Inkling creature token with flying." |
| rule:etb-modal-choice | KEEP | Kin-Tree Nurturer | "When this creature enters, it endures 1. (Put a +1/+1 counter on it or create a 1/1 whi…" |
| rule:redirect-targets-of-spell-or-ability | KEEP | Wyll's Reversal | "You may choose new targets for that spell or ability." |
| rule:graveyard-to-exile-replacement | KEEP | Faithbound Judge // Sinner's Judgment | "If Sinner's Judgment would be put into a graveyard from anywhere, exile it instead." |
| rule:targeted-destruction | KEEP | Harsh Annotation | "Destroy target creature." |
| rule:creates-treasure-token | KEEP | Plundering Pirate | "When this creature enters, create a Treasure token." |
| rule:attack-trigger-buff-other-attacker-counters | KEEP | Sovereign Okinec Ahau | "Whenever Sovereign Okinec Ahau attacks, for each creature you control with power greate…" |
| rule:targeted-player-damage | KEEP | Pia's Revolution | "target opponent has this enchantment deal 3 damage to them" |
| rule:conditional-first-strike-your-turn | KEEP | Javelin of Lightning | "During your turn, equipped creature gets +2/+0 and has first strike." |
| rule:grants-trample-to-other-creatures | KEEP | Roughshod Mentor | "Green creatures you control have trample." |
| rule:graveyard-to-library-shuffle-in | KEEP | Elixir | "Shuffle all nonland cards from your graveyard into your library." |
| rule:mass-untap-and-haste-stolen-creatures | KEEP | Press into Service | "Untap that creature. It gains haste until end of turn." |
| rule:level-up-scaling-stats-abilities | KEEP | Blacksmith's Talent | "{2}{R}: Level 2" |
| rule:mill-self-cards | KEEP | Villainous Syndication | "Mill a card." |
| rule:modal | KEEP | Opera Love Song | "Choose one —" |
| rule:library-dig-put-onto-battlefield | KEEP | Aethermage's Touch | "Reveal the top four cards of your library. You may put a creature card from among them …" |

**Note on this sample:** `rule:graveyard-to-exile-replacement`'s sampled
member (Faithbound Judge // Sinner's Judgment) is a transform card whose
quote does NOT verify against `review/batch-4.json`'s top-level
`cards[oid].oracle_text` field (empty string, see section 0's bug report)
-- it only verifies against the per-member enrichment snapshot, which does
carry the correct all-faces text. The verdict itself is fine; it's the
`cards` dict export that's incomplete for this and 20 other DFC-shaped
cards.

**Result: 0 reversals expected on the verdict calls themselves (all 30
quotes verified verbatim); 1 export-completeness bug surfaced by the
verification process itself, reported in section 0.**

---

## 5. Batch-5 feedback (fold into consolidation tooling + SYNTH prompt)

1. **New systemic issue: activated-vs-triggered / cost-vs-effect
   conflation.** Section 0's headline finding -- `rule:activated-tap-target-creature`
   had a 56% member-mismatch rate (9/16). Recommend adding one explicit
   line to the two-lane SYNTH instructions, parallel to batch-3's
   same-direction check: "before assigning an axis whose definition says
   'activated ability,' confirm the card's ability actually has a
   player-chosen activation cost (a `{cost}:` template) -- 'Whenever X
   happens' and 'When this enters' are triggered abilities, never
   activated ones, even if their effect taps or costs a resource. Also
   confirm WHAT gets tapped/targeted matches the definition's object class
   (creature vs. artifact vs. land vs. any permanent) and that an
   activation cost's own effect on the SOURCE (e.g. `{T}:`) isn't confused
   with the ability's EFFECT on a TARGET."
2. **DET fix needed (not a SYNTH prompt issue):**
   `foundry_common.py:build_review_card_record()` needs to fall back to
   concatenated `card_faces[*].oracle_text` when the root `oracle_text`
   field is empty -- currently affects 21/1016 (2.1%) of this batch's
   `review/batch-4.json` cards dict, all multi-face layouts. See section 0.
3. **Codebook-history surfacing gap.** Two of this batch's 5 merges
   (`rule:grants-temporary-hexproof`, and arguably
   `rule:etb-grants-energy-counters`) are near-exact resurrections of
   concepts already ratified/superseded in prior batches. The embedded
   codebook reference the SYNTH prompt sees presumably lists only ACTIVE
   axis slugs + definitions, not killed/merged history -- consider whether
   a short "recently killed, do not re-propose" appendix (even just slugs,
   no reasons, to control the prompt-growth cost already flagged in
   MASTER-HANDOFF-ADDENDUM-2.md §6) would reduce this category of
   duplicate.
4. **Strategic question, not urgent: the scales-with-count family is
   fragmenting.** The single largest OTHER-lane group this batch
   (`[count/scal]`, n=60) is entirely "effect magnitude scales with a
   count of some game object" labels that never cluster into 2-card
   free-lane families because each card's free-label names a different
   counted object. Meanwhile the active codebook already has
   `rule:x-scales-with-permanent-count` PLUS narrower siblings
   (`damage-scales-with-creature-count`, `power-scales-with-creature-count`,
   and now `buff-scales-with-land-type-count` this batch) that keep
   getting proposed piecemeal. Worth a schema-pass ruling on whether
   "scales with count of X" should lane=codebook-match onto one
   parameterized family by default. See PARENT-TREE-CANDIDATES.md's
   existing N-scales-with-N-count entry (batch-2 M6) -- this reinforces
   rather than introduces the tension.
5. Batch-5 hand-picked targeting: the 1 QUESTION axis (once ruled), the 9
   member-mismatch removals from `rule:activated-tap-target-creature`
   (confirm no other cards need reassignment nearby -- there may be more
   ETB/attack-trigger "taps a creature" cards in the corpus that would
   cluster into the new sibling axes noted in
   PARENT-TREE-CANDIDATES.md), and continued confirmation of thin axes
   (`rule:attack-trigger-loot`, `rule:conditional-buff-by-color`,
   `rule:death-trigger-counter-transfer`, `rule:death-trigger-mass-debuff`,
   and others still at n=1).

---

## 6. Ledger candidates carried forward

None this batch. `rule:kicker-conditional-bonus-effect` (n=5, existing
confirmation) is NOT a new ledger candidate -- Kicker already has an active,
Captain-ratified axis (unlike Regenerate/Connive/Flashback/Level-up, which
were fully killed+ledgered in batches 1-3); this batch's instance is a
routine reconfirmation. Considered and rejected for the ledger:
`rule:populate-copy-creature-token` -- "Populate" is a keyword ACTION with
reminder text, but unlike Kicker/Flashback its axis describes a structurally
distinct mechanism (copies specifically an existing TOKEN, not any
creature) not already covered by the active `rule:copy-creature-token`
(which copies any creature via various templates) -- kept as its own axis
rather than killed, on the same "real archetype pattern, not just a bare
keyword restated" standing as Kicker.

---

## 7. Verification

- Verdict count vs. axis count: 166 axes total = KEEP 158 (131 existing +
  27 new) + KILL 2 + MERGE 5 + QUESTION 1 = 166. Verified programmatically
  against the full 166-slug list from `review/batch-4-enriched.json`, one
  verdict per slug, zero duplicates, zero omissions.
- Every MERGE target is named and active in codebook v0.3: M(activated-pump-with-self-damage-cost)
  and M(activated-self-toughness-pump) → `rule:mana-activated-pump-self`;
  M(etb-grants-energy-counters) → `rule:gives-energy-counters-immediately`;
  M(grants-temporary-hexproof) → `rule:temporary-keyword-grant`;
  M(replacement-exile-instead-of-graveyard) → `rule:graveyard-to-exile-replacement`
  -- all five pre-existing, active codebook axes.
- Parent-tree flags appended to `PARENT-TREE-CANDIDATES.md` (site repo,
  per batch-3 precedent -- this repo's `docs/` is not the durable
  version-controlled location for that ledger): self-counter-growth
  trigger-context family, energy family growth, the graveyard/death exile-
  replacement family, the taps-target-creature trigger-context gap, and
  the mana-activated-pump-self parameter absorptions.

---

**STOP.** File written to `docs/TRIAGE-BATCH-4.md`. Captain: annotate per
the protocol convention (edit `VERDICT:` lines and member-removal notes,
fill the `-> RULE:` blank for Q1, add `## CAPTAIN-AUTHORED` blocks for any
new axes), then run `/triage-emit 4` when done.

---

## 10. CAPTAIN RATIFICATION — PARSED DIRECTIVES

Per SUP-TRIAGE-PROTOCOL.md's §10 convention: this section is the
authoritative, parseable record of Captain's ratification. Sections 0/1's
prose annotations above remain the audit trail explaining *why*; this
section is what `/triage-emit 4` actually parses. Where this section and
the prose above could be read differently, this section governs.

**D1 — `rule:activated-tap-target-creature` (n=16): KEEP, member removals
ratified as proposed, no split.**
Remove 9 members: Arena, Crossbow Infantry, Eddymurk Crab, Glaring Aegis,
Hammers of Moradin, Relic Barrier, Rishadan Port, Summon: Valefor, Tamiyo,
Field Researcher. Surviving 7: Blinding Mage, Blinding Souleater, Gavony
Trapper, Loxodon Mystic, Sigardian Priest, Solstice Zealot, Stormscape
Apprentice. The axis concept stands as originally defined ("an activated
ability that taps a target creature") — Captain declined section 5's
implicit invitation to fork it into sibling ETB/attack-trigger tap axes
this batch; those siblings are schema-pass material, tracked in
PARENT-TREE-CANDIDATES.md's "taps a target creature" trigger-context gap
entry, not built now.

**D2 — Member removals ratified (single-card, no axis-level action).**
- `rule:mass-damage-opponent-creatures-only` (n=3): remove Klothys, God of
  Destiny — deals damage to opponents directly, not their creatures. No
  reassignment target; the axis for "mass damage to opponents, no target"
  does not exist this batch and none is being built for it now.
- `rule:targeted-creature-damage` (n=13): remove Item Crate — "deals 2
  damage to any target" is any-target, not creature-specific. REASSIGN:
  add Item Crate to `rule:direct-damage-any-target` at reconcile (its
  quote is a verbatim fit for that axis's existing definition).

**D3 — `rule:targeted-planeswalker-damage`: add Breya, Etherium Shaper at
reconcile, per the ratified M8 per-object-class mixed-target rule.**
Breya's quote ("deals 3 damage to target player or planeswalker") already
qualifies her for `rule:targeted-player-damage` (in this batch's own
member list); M8 requires the second tag on the planeswalker-damage axis
too, since mixed-target cards get multiple tags rather than one combo tag.
This is a reconcile-time addition to an axis Breya isn't otherwise a
batch-4 member of — not a member-removal, not a new axis.

**D4 — Merges ratified.**
- `rule:grants-temporary-hexproof` (n=2: Mizzium Skin, Plumecreed Escort)
  → MERGE INTO `rule:temporary-keyword-grant`.
- `rule:etb-grants-energy-counters` (n=3: Hightide Hermit, Decoction
  Module, Inventor's Axe) → MERGE INTO `rule:gives-energy-counters-immediately`.
- `rule:replacement-exile-instead-of-graveyard` (n=2: Mission Briefing,
  Covetous Castaway // Ghostly Castigator) → MERGE INTO
  `rule:graveyard-to-exile-replacement`.
- Q1 resolved: `rule:replaces-death-with-exile` (n=2: Bouncer's Beatdown,
  Incendiary Flow) → MERGE INTO `rule:graveyard-to-exile-replacement`
  (Captain: "Merge"). The self-protection-vs-removal-upgrade distinction
  section 2 raised is noted but does not block the merge — same
  continuous-replacement-effect text pattern governs.
- **STANDING RULE (going forward, all future batches):** any
  `grants-temporary-<keyword>` candidate (any keyword, not just hexproof)
  folds into `rule:temporary-keyword-grant` on sight — beta does not need
  to raise it as a question or a fresh merge proposal. The keyword-identity
  facet (which keyword was granted) is deferred to the schema-pass facet
  scheme (§10 STEP 2a below / PARENT-TREE-CANDIDATES.md), not rebuilt as a
  one-off axis per keyword.

**D5 — HELD, not parsed into this emit's codebook build as KEEP/KILL/MERGE.**
`rule:activated-pump-with-self-damage-cost` (n=2: Stormcloud Djinn,
Electric Eel) and `rule:activated-self-toughness-pump` (n=2: Abbey Matron,
Pearl Dragon) do NOT execute section 1b's proposed MERGE INTO
`rule:mana-activated-pump-self` this batch. Verdict for both: **DEFER**.
Both carry into codebook v0.4 as `status: "deferred"` (recorded, inactive,
not offered to SYNTH as an active codebook slug, not merged) pending
Captain's review of their full member lists + evidence quotes, written to
`experiments/out/foundry/review/batch-4-deferred-examples.md` (file only —
transcript hygiene, no oracle text to console).

**D6 — PRECEDENT REVERSAL: cost-shape riders are legitimate wide-net axes.**
The b2/b3 "cost-shape riders are not axes" precedent (which killed
`rule:sacrifice-creature-as-additional-cost`,
`rule:sacrifice-as-additional-cost`, `rule:self-sacrifice-divided-damage`,
etc.) is OVERTURNED. `rule:additional-cost-sacrifice-permanent` (n=4:
Shard Volley, Lethal Throwdown, Bankrupt in Blood, Momentous Fall) and
`rule:additional-cost-discard-a-card` (n=2: Laughing Mad, Sazacap's Brew)
flip **KILL → KEEP**, both entering codebook v0.4 as new active axes with
their batch-4 members. Downstream actions (not executed this emit, logged
as punch list): (a) MASTER-HANDOFF-ADDENDUM-2.md §4 rulings registry
updated with the reversal (STEP 4/6 of this session); (b)
docs/SUP-TRIAGE-PROTOCOL.md's and `.claude/commands/triage-beta.md`'s
standing verdict precedents updated so batch-5 beta does not auto-KILL
cost-shape candidates; (c) punch-list item: evaluate resurrecting the
b2/b3-killed cost-shape axes (`rule:sacrifice-creature-as-additional-cost`,
`rule:sacrifice-as-additional-cost`, `rule:self-sacrifice-divided-damage`)
at reconcile or schema pass — NOT executed now, Captain must explicitly
call it.

**D7 — All other section-1 verdicts stand as written.**
Every axis in sections 1a/1b not named in D1–D6 above ratifies exactly as
SUP proposed (overwhelmingly KEEP, including all 27 new-candidate KEEPs).
No further changes.

### STEP 2 — Parent-tree ledger additions (attributed to Captain, batch-4
ratification; written to `mtjawnny.github.io/docs/PARENT-TREE-CANDIDATES.md`
per the established durable-location precedent, not this repo's `docs/`):

a. **Keyword-grant facet scheme.** Wide-net `rule:temporary-keyword-grant`
   stays the catch-all; granular facet dimensions on top: which keyword
   (e.g. `gives-hexproof`), duration (EOT / next turn / static-anthem /
   keyword counter), scope (target / up-to-N / all-you-control / all),
   delivery trigger (etb / activated / cast). Interacts with the b1-Q1
   keyword-grant engine-redundancy kill — open tension T1, schema pass
   reconciles. Do not author these as axes now.
b. **Cost-shape facet scheme**, per D6: wide-net cost axes
   (`rule:additional-cost-sacrifice-permanent`,
   `rule:additional-cost-discard-a-card`, and the punch-listed b2/b3
   revival candidates) stay wide-net; granular children on top: object
   class sacrificed, one-shot vs. repeatable outlet.
c. **Delivery-facet note**, from the energy merge (D4): merged members of
   `rule:gives-energy-counters-immediately` should be distinguishable by
   delivery trigger (etb vs. other) at schema pass.

### STEP 3 — Punch list additions (logged only, not executed this emit):

- DET fix for `experiments/foundry_common.py`'s `build_review_card_record()`:
  when root `oracle_text` is empty, concatenate `card_faces[*].oracle_text`
  per the repo's all-faces rules (21 multi-face cards affected in batch 4).
  **Correction at emit time:** found already implemented, correctly, but
  uncommitted in the working tree — not written by the emit session, but
  committed as part of it since it directly benefits batch-5's Stage 1B
  prompts. Does not retroactively fix `review/batch-4.json` itself (already
  generated before the fix existed). Captain note carried forward: consider
  a sanctioned oracle-text injection path for multi-face cards — surfacing
  back-face cards quickly is a product requirement for every tool built on
  this engine.
- Batch-5 beta spec change: add a MEMBER ROSTER section to the TRIAGE doc —
  every axis, full member card names (names only, no oracle text) — so
  Captain can audit membership, not just logic.
- Batch-5 SYNTH prompt fix from section 5 (activated-vs-triggered /
  ability-type check) stands — apply it.

**RATIFIED.** §10 supersedes sections 1–2's prefilled verdicts wherever
they conflict. Proceeding to `/triage-emit 4`.
