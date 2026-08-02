# TRIAGE — Batch 6 (SUP judgment pass)

Reviewed against `docs/SUP-TRIAGE-PROTOCOL.md`, `experiments/out/foundry/review/digest-batch-6.md`
(192 axes: 165 existing-codebook confirmations + 27 new candidates; 1239 OTHER-lane rows;
1343 token groups), and codebook v0.5 (241 active axes). Also cross-checked against
`docs/MASTER-HANDOFF-ADDENDUM-3.md` per its §9 standing task (compounds-authored/atomics-derived
rule, ratified depth-3 etb scheme, M8 mixed-target-class rule).

**Nothing in this document is load-bearing until Captain ratifies it.** Untouched entries
are ratified as proposed per the protocol's parsing convention — Captain annotates only
what needs to change, then runs `/triage-emit 6`.

## Methodology note on OTHER-lane coverage

Read all 165 existing-codebook confirmations, all 27 new candidates, and all 81 OTHER-lane
token groups with n>=10 (the full large-group tier) in full. Above n>=3 (roughly 250 groups
spanning n=70 down to n=3), coverage was also complete. Below that, coverage was a large
but not literally exhaustive sample of the n=2 tier (roughly 120 of ~560 groups read in
full alphabetical sequence before stopping). This is a deliberate deviation from batch 5's
literal 100%-of-1,248-groups standard, made because the signal had already flatlined hard:
every group read from n=6 down through the sampled n=2 slice was an incidental 2-token
collision between mechanically unrelated cards (e.g. "attack" + "land" pairing an
attack-trigger card with an unrelated land-destruction card), with zero coherent multi-card
families surfaced beyond the single real hit documented below — consistent with batch 5's
own finding of "no residue left to reinforce" at this tier. I flag this explicitly rather
than silently claim full coverage; Captain should treat the n=2 tier as spot-checked, not
exhaustively cleared, and the batch-7 assembly script's `no_other_lane_reinforcement_reason`
should say so honestly rather than repeat batch 6's assembly script's claim.

---

## 1. Axis verdicts — existing codebook confirmations (165)

- `rule:activated-ability-costs-self-sacrifice` (scope=self, n=36) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:activated-draw-a-card` (scope=self, n=9) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:activated-exile-graveyard-creature-card` (scope=opponent-stuff, n=7) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:activated-tap-target-creature` (scope=opponent-stuff, n=9) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:activation-restricted-only-during-your-turn` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:activation-restricted-to-own-upkeep` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:activation-restricted-to-sorcery-speed` (scope=self, n=14) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:additional-cost-discard-a-card` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:additional-cost-sacrifice-permanent` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:alt-cost-sacrifice-lands` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:animates-land-into-creature` (scope=your-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:attack-trigger-create-token` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:attack-trigger-loot` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:attack-trigger-mass-pump-attackers` (scope=your-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:attack-trigger-pump-any-creature` (scope=any-creature, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:attack-trigger-untap-attacker` (scope=any-permanent, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:buff-scales-with-land-type-count` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:burst-draw` (scope=self, n=13) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:cannot-block-restriction` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:cant-be-blocked-by-color` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:cant-be-countered` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:cantrip` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:cast-from-exile-trigger` (scope=all-players, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:cast-from-top-of-library` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:changes-color-creature` (scope=any-creature, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:charge-counter-accumulation` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:cheat-creature-into-play` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:choose-creature-type-on-etb` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:combat-damage-to-player-draws-card` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:combat-damage-triggers-discard` (scope=opponent-stuff, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:combat-damage-triggers-loot` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:combat-trick-pump-own-creature` (scope=self, n=16) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:combat-trigger-auto-attach-equipment` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:compensates-controller-with-token` (scope=opponent-stuff, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:conditional-creature-status` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:copies-cast-spell` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:copy-creature-token` (scope=any-creature, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:cost-reduction` (scope=self, n=10) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:counter-removal-as-activation-cost` (scope=self, n=8) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:counters-noncreature-spell` (scope=opponent-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:counters-target-spell` (scope=opponent-stuff, n=6) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:create-token-creature` (scope=your-stuff, n=14) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:create-token-mana-producing-artifact` (scope=self, n=1) -- KEEP; member_addition(Stone Retrieval Unit) -- "create a tapped Powerstone token" is a genuine mana-producing-artifact-token match on its own oracle text; stands independent of any prior example. [CORRECTED 2026-07-30 per D1 precedent rescan: the original draft of this line cited a "Peel Out/Banana precedent" that does not exist -- Peel Out was never a ratified member of this axis (it was this batch's own fresh SYNTH hit, not yet reconciled when the citation was written), and Peel Out itself fails Gate #0 (set=unk, Unknown Event, not_legal everywhere) and will not be added. Citation struck; Stone Retrieval Unit's membership is unaffected.] Surfaced via an OTHER-lane labeling bug: SYNTH free-labeled it "rule:etb-create-token-mana-producing-artifact", a slug that does not exist in the codebook (the real axis has no etb- prefix) -- batch-feedback item below.
- `rule:create-token-treasure` (scope=self, n=10) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:damage-divided-among-multiple-targets` (scope=opponent-stuff, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:death-of-your-permanents-grows-this-creature` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:death-trigger-counter-transfer` (scope=your-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:death-trigger-scroll-regrowth` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:death-trigger-token-creation` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:delayed-draw-next-upkeep` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:direct-damage-any-target` (scope=opponent-stuff, n=13) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:doubles-counter-placement` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:drain-life` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:drain-on-creature-death` (scope=opponent-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:draw-cards-with-life-loss-cost` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:draw-second-card-trigger-plus1-counter` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:draw-trigger-self-counter-growth` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:enters-tapped` (scope=self, n=26) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:enters-tapped-conditional` (scope=self, n=5) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-and-attack-trigger` (scope=self, n=6) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-auto-attach-to-own-creature` (scope=your-stuff, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-bounce-other-creature` (scope=opponent-stuff, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-counter-on-other-creature` (scope=self, n=9) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-create-token` (scope=self, n=6) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-create-token-creature` (scope=self, n=23) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-create-token-creature-conditional` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-create-token-food` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-create-token-mutagen` (scope=self, n=5) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-destroy-target-enchantment` (scope=opponent-stuff, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-draw-card` (scope=self, n=7) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-exile-graveyard-card` (scope=opponent-stuff, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-gain-life` (scope=self, n=7) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-loot` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-mass-pump-your-creatures` (scope=your-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-modal-choice` (scope=self, n=6) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-scry` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-tutor-to-hand` (scope=self, n=5) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-with-counters` (scope=self, n=13) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:evasion-vs-low-power-blockers` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:exile-until-source-leaves` (scope=opponent-stuff, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:fixed-lifegain` (scope=self, n=10) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:forced-attack-each-combat` (scope=self, n=5) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:forced-hand-reveal` (scope=opponent-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:forces-creature-to-attack` (scope=opponent-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:forces-opponent-sacrifice` (scope=opponent-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:free-cast` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:free-sacrifice-outlet` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:gives-energy-counters-immediately` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:grants-ability-at-threshold-board` (scope=your-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:grants-ability-at-threshold-self` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:grants-additional-combat-phase` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:grants-creature-type` (scope=your-stuff, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:grants-extra-turn` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:grants-haste-to-created-tokens` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:grants-haste-to-your-creatures` (scope=your-stuff, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:grants-trample-to-other-creatures` (scope=your-stuff, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:grants-unblockable-target` (scope=any-creature, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:graveyard-to-hand-recursion` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:graveyard-to-library-shuffle-in` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:graveyard-to-library-top-recursion` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:individual-cost-reduction` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:innate-unblockable` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:kicker-conditional-bonus-effect` (scope=self, n=8) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:land-fetch-to-battlefield` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:landfall-gain-life` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:landfall-self-pump` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:leaves-battlefield-trigger-create-token-creature` (scope=self, n=2) -- KEEP but corrected -- member_removal(Zoo Escapees): its LTB trigger creates a Mutagen token, which the corpus text explicitly types as "an artifact," not a creature token; this axis's own definition (and the D10 parent scheme) requires a creature token. Zoo Escapees has no home in the current codebook (the non-creature-token-scoped parent, rule:leaves-battlefield-trigger-create-token, was never authored -- only its -creature child exists per D10's conservative-reclassification precedent). Flagged to PARENT-TREE-CANDIDATES.md rather than force a bad fit.
- `rule:level-up-scaling-stats-abilities` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:library-dig-put-onto-battlefield` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:library-dig-to-hand` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:library-top-visibility` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:life-total-reset` (scope=all-players, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:lifegain-triggered-counter` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mana-activated-pump-self` (scope=self, n=8) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mass-counter-distribution` (scope=your-stuff, n=5) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mass-creature-destruction` (scope=all-players, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mass-damage-creatures-and-players` (scope=all-players, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mass-damage-opponent-creatures-only` (scope=opponent-stuff, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mass-debuff-opponent-creatures` (scope=opponent-stuff, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mass-graveyard-exile` (scope=all-players, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mass-pump-your-creatures` (scope=your-stuff, n=5) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mass-untap-and-haste-stolen-creatures` (scope=all-players, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mass-untap-your-creatures` (scope=your-stuff, n=5) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mill-self-cards` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:modal` (scope=self, n=9) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:no-maximum-hand-size` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:partner-with-tutor` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:pay-life-cost-for-effect` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:plus1-counters-matter` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:populate-copy-creature-token` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:power-scales-with-creature-count` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:prevent-fixed-damage-any-target` (scope=all-players, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:prevents-damage-prevention` (scope=all-players, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:prevents-damage-to-self` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:prevents-regeneration` (scope=opponent-stuff, n=5) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:prevents-target-blocking` (scope=opponent-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:reanimate-from-graveyard` (scope=your-stuff, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:redirect-targets-of-spell-or-ability` (scope=opponent-stuff, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:restricted-purpose-mana` (scope=self, n=5) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:restricts-blocking-to-flying-only` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:rhystic-tax` (scope=opponent-stuff, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:sacrifice-for-creature-token` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:scales-mana-by-count` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:scales-token-count-with-x` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:self-bounce-activated` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:self-recursion-from-graveyard` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:sets-base-power-or-toughness` (scope=any-creature, n=5) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:skips-controller-draw-step` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:stun-counter` (scope=opponent-stuff, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:targeted-bounce-creature` (scope=opponent-stuff, n=5) -- KEEP -- narrow bounce-target-creature family is real and useful; member_removal(Otawara, Soaring City) -- its quote ("Return target artifact, creature, enchantment, or planeswalker to its owner's hand") is a multi-type bounce, not creature-scoped, contradicts the axis's own opponent-stuff/creature scope.
- `rule:targeted-creature-damage` (scope=opponent-stuff, n=16) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:targeted-destruction` (scope=opponent-stuff, n=27) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:targeted-discard` (scope=all-players, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:targeted-exile` (scope=any-permanent, n=5) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:targeted-planeswalker-damage` (scope=opponent-stuff, n=4) -- KEEP; member_addition(Insult // Injury, Injury face) -- "2 damage to target creature and 2 damage to target player or planeswalker" is a mixed-object-class-target card per the ratified M8 damage-target family ruling (multiple tags, never a combination tag); it was already correctly tagged onto targeted-creature-damage and targeted-player-damage but missing from this sibling.
- `rule:targeted-player-damage` (scope=opponent-stuff, n=6) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:taxes-opponent-spell-cost` (scope=opponent-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:temporary-control-theft` (scope=opponent-stuff, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:temporary-keyword-grant` (scope=your-stuff, n=5) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:the-ring-tempts-you` (scope=self, n=6) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:tribal-anthem-buff` (scope=your-stuff, n=10) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:triggers-on-cast-instant-sorcery` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:tutor-from-outside-game-to-hand` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:untaps-target-land` (scope=your-stuff, n=3) -- KEEP but corrected -- member_removal(High Alert), member_removal(Staff of Domination): both quotes read "Untap target creature," not land, leaving Ley Weaver ("Untap two target lands") as the axis's only genuine member. n=3->1 after correction; still worth keeping as a real, narrow pattern rather than killing on a post-correction thin count.
- `rule:x-scales-with-permanent-count` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.

## 2. Axis verdicts — new candidates (27)

- `rule:draw-scaled-by-creature-count` (scope=self, n=4) -- KEEP; member_removal(Culling Dais) -- "Draw a card for each charge counter on this artifact" scales by charge counters on itself, not creature count; Biomantic Mastery / Camaraderie / Winged Portent are all genuine creature-count scaling and remain.
- `rule:self-exile-after-resolution` (scope=self, n=4) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.5.
- `rule:leaves-battlefield-returns-exiled-card` (scope=self, n=3) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.5.
- `rule:lifegain-scaled-by-creature-count` (scope=self, n=3) -- KEEP; member_removal(Joraga Peach) -- "You gain 1 life for each counter on this artifact" scales by counters on itself, the same charge-counter confusion as the Culling Dais case above (same card family, same SYNTH miss pattern -- worth a batch-feedback note). Camaraderie and Depose // Deploy remain genuine.
- `rule:token-count-scales-with-graveyard-creature-count` (scope=self, n=3) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.5.
- `rule:token-sacrifice-for-mana` (scope=your-stuff, n=3) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.5.
- `rule:activated-destroy-target-land` (scope=opponent-stuff, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.5.
- `rule:activated-exile-graveyard-creature-for-token` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.5.
- `rule:activated-loot` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.5.
- `rule:activated-sacrifice-any-permanent-for-self-counter` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.5.
- `rule:activated-tap-or-untap-any-creature` (scope=any-creature, n=2) -- QUESTION -- Fatestitcher's quote ("tap or untap another target permanent") is broader than the axis's any-creature scope; Puppet Strings ("tap or untap target creature") fits as declared. Lean: broaden the axis's scope/definition to any-permanent rather than remove Fatestitcher -- a creature is a permanent, so Puppet Strings still satisfies a broadened definition, and losing Fatestitcher would leave a thin n=1 for no real gain. Captain's call on scope wording.
- `rule:activated-untap-another-permanent` (scope=any-permanent, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.5.
- `rule:aura-locks-enchanted-creature-tapped` (scope=opponent-stuff, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.5.
- `rule:cast-trigger-transforms-into-creature` (scope=self, n=2) -- KEEP; member_removal(Village Ironsmith // Ironfang) -- its trigger is "At the beginning of each upkeep, if no spells were cast last turn, transform," an upkeep trigger keyed on the ABSENCE of casting, not a cast-trigger at all; contradicts this axis's own definition. Veiled Serpent (opponent-casts trigger) remains the sole genuine member.
- `rule:changes-creature-type-text` (scope=any-permanent-or-spell, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.5.
- `rule:conditional-attack-restriction-by-opponent-land-type` (scope=opponent-stuff, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.5.
- `rule:created-token-enters-tapped` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.5.
- `rule:creates-token-with-x-scaled-counters` (scope=self, n=2) -- KEEP; member_removal(Forth Eorlingas!) -- "Create X 2/2 red Human Knight creature tokens" scales the TOKEN COUNT by X, not counters placed on a token; it belongs under rule:token-count-scales-with-x instead (member_addition there). Wild Hypothesis ("Create a 0/0 ... token. Put X +1/+1 counters on it.") is the axis's only genuine member.
- `rule:etb-pump-target-creature` (scope=any-creature, n=2) -- QUESTION -- Herald of the Fair's quote ("target creature you control gets +1/+1") is restricted to own creatures, contradicting the axis's own "not restricted to the controller's own creatures" definition clause; Yeva's Forcemage ("target creature gets +2/+2", no restriction) fits as declared. Lean: drop the "not restricted" clause from the definition and keep both -- the axis is really just "ETB pump a target creature," ownership-restricted or not; splitting into two 1-member axes over an ownership qualifier is not worth the codebook growth given the current cost-vs-effect concern. Captain's call.
- `rule:etb-with-negative-counters` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.5.
- `rule:etb-with-oil-counters` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.5.
- `rule:evasion-vs-high-power-blockers` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.5.
- `rule:forces-creature-to-be-blocked` (scope=opponent-stuff, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.5.
- `rule:lifegain-scaled-by-permanent-color-count` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.5.
- `rule:postcombat-main-phase-trigger` (scope=all-players, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.5.
- `rule:prevent-all-combat-damage-this-turn` (scope=all-players, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.5.
- `rule:token-count-scales-with-x` (scope=self, n=2) -- KEEP; member_addition(Forth Eorlingas!) -- see rule:creates-token-with-x-scaled-counters's member_removal note; this is its correct home.

---

## 3. QUESTIONS (2 of max 8)

Both are genuine either/ors on a definition/scope wording, not on membership fact — the
evidence is unambiguous in both cases, the judgment call is how to word the axis afterward.

**Q1 — `rule:activated-tap-or-untap-any-creature` scope.** Fatestitcher's actual text is
"{T}: You may tap or untap another target permanent" — broader than the axis's declared
any-creature scope. Puppet Strings ("You may tap or untap target creature") fits as
declared. Two ways to resolve:
  - (a) Broaden the axis to any-permanent (rename definition only, keep both members;
    Puppet Strings' creature is a permanent, so it still satisfies a broadened definition).
  - (b) Split: remove Fatestitcher, leave the axis creature-scoped at n=1, and either
    captain-author a sibling `rule:activated-tap-or-untap-any-permanent` for Fatestitcher
    or punch-list it (flagged to PARENT-TREE-CANDIDATES.md either way).
  - **Lean: (a).** A thin n=1 post-split buys nothing; broadening the definition is the
    lower-churn fix and doesn't lose precision anyone was relying on (no other axis
    currently claims the any-permanent tap-or-untap space).

**Q2 — `rule:etb-pump-target-creature` ownership restriction.** Herald of the Fair's text
("target creature you control gets +1/+1") is restricted to own creatures; the axis's own
definition claims "not restricted to the controller's own creatures," which Yeva's Forcemage
satisfies but Herald of the Fair contradicts. Two ways to resolve:
  - (a) Drop the "not restricted" clause from the definition, keep both members — the
    axis becomes simply "ETB pump a target creature," ownership-restricted or not.
  - (b) Split by ownership scope into two 1-member axes (self vs any-creature).
  - **Lean: (a).** Per the codebook-growth cost-vs-effect concern flagged in
    MASTER-HANDOFF-ADDENDUM-3.md's punch list, splitting a 2-member axis into two
    1-member axes over an ownership qualifier that doesn't change deck-building
    relevance (an ETB combat-trick pump reads the same to a deckbuilder whether it can
    target only your own creatures or any creature) isn't worth the growth.

---

## 4. OTHER-lane promotions and corrections

No new coherent multi-card families were found beyond what full coverage of the n>=3 tier
(and a large sample of n=2) surfaced — consistent with batch 5's "no residue" finding. Two
items did surface, both folded into the axis verdicts above rather than listed as fresh
promotions:

- **`rule:create-token-mana-producing-artifact` gains a member** (Stone Retrieval Unit —
  see its verdict line above). This was reached via an OTHER-lane labeling bug, not a
  genuinely novel family: SYNTH free-labeled the card `rule:etb-create-token-mana-producing-artifact`,
  a slug that doesn't exist in the codebook (likely confusing the `create-token-<type>`
  family, which has no etb- prefix, with the etb-create-token-<type> family, which does).
  Batch-feedback item below.
- **`rule:equipment-static-pt-buff` / `rule:equipment-grants-stat-buff` — considered and
  rejected.** SYNTH used the "rule:" prefix (reserved for lane=codebook exact matches) on
  two near-synonymous invented slugs for Rosethorn Halberd and Maul of the Skyclaves,
  neither of which exists in the codebook. On inspection the underlying pattern
  ("Equipped creature gets +X/+Y[, keywords]") is the templated baseline function of the
  Equipment card type — it would match the overwhelming majority of combat-buff Equipment
  corpus-wide, making it a generic/procedural pattern rather than a differentiating one
  (batch-1 standard: "procedural riders and templating -> KILL"). Not promoted. Flagged
  to PARENT-TREE-CANDIDATES.md so a future batch doesn't re-propose it from scratch.

---

## 5. Override sample (30 rows, seed=20260724, confident calls only)

Drawn uniformly at random (Python `random.Random(20260724).sample`) from all 752 member
rows across the 190 non-QUESTION axes (165 existing + 25 of 27 new candidates, excluding
Q1/Q2's axes). Every quote below was checked against the digest transcription; the six
cards already known to be mismatches from the axis-verdict pass above were separately
corpus-verified via `foundry_common.load_corpus()` + direct oracle-text lookup (not just
the digest's truncated quote) — see their axis verdicts in sections 1-2 for the full
citation. One of the 30 sampled rows below (Zoo Escapees) turned up an additional,
previously-unflagged mismatch during this verification pass itself.

| Axis | Card | Quote (as transcribed) | Check |
|---|---|---|---|
| rule:activated-ability-costs-self-sacrifice | Pick-a-Beeble | "Create two Treasure tokens, then sacrifice Pick-a-Beeble and open an Attraction." | OK |
| rule:activated-ability-costs-self-sacrifice | Potatoes | "{2}, {T}, Sacrifice Potatoes: Choose one —" | OK |
| rule:activated-exile-graveyard-creature-for-token | Havengul Runebinder | "{2}{U}, {T}, Exile a creature card from your graveyard: Create a 2/2 black Zomb…" | OK |
| rule:copies-cast-spell | Rowan, Scholar of Sparks Emblem | "If you do, copy that spell. You may choose new targets for the copy." | OK |
| rule:counter-removal-as-activation-cost | Academy Elite | "{2}{U}, Remove a +1/+1 counter from this creature: Draw a card, then discard a …" | OK |
| rule:create-token-creature | Elemental Eruption | "Create a 4/4 red Dragon Elemental creature token with flying and prowess." | OK |
| rule:create-token-creature | Wild Hypothesis | "Create a 0/0 green and blue Fractal creature token." | OK |
| rule:death-trigger-token-creation | Chasm Skulker | "When this creature dies, create X 1/1 blue Squid creature tokens with islandwal…" | OK |
| rule:direct-damage-any-target | Jaya's Immolating Inferno | "Jaya's Immolating Inferno deals X damage to each of up to three targets." | OK |
| rule:direct-damage-any-target | Potatoes | "Boil — Potatoes deals 1 damage to any target." | OK |
| rule:etb-auto-attach-to-own-creature | Maul of the Skyclaves | "When this Equipment enters, attach it to target creature you control." | OK |
| rule:etb-create-token-creature | Falcon Abomination | "When this creature enters, create a 2/2 black Zombie creature token with decaye…" | OK |
| rule:etb-create-token-creature | Huatli, Poet of Unity // Roar of the Fifth People | "I — Create two 3/3 green Dinosaur creature tokens." | OK |
| rule:etb-draw-card | Heart of a Duelist | "When Heart of a Duelist enters the battlefield, draw a card." | OK |
| rule:etb-gain-life | Arborback Stomper | "When this creature enters, you gain 5 life." | OK |
| rule:etb-with-counters | Molly Hayes, Runaway | "Put two +1/+1 counters on Molly Hayes." | OK |
| rule:etb-with-counters | Retrofitted Transmogrant | "Return this card from your graveyard to the battlefield tapped with two +1/+1 c…" | OK |
| rule:forces-creature-to-be-blocked | Irresistible Prey | "Target creature must be blocked this turn if able." | OK |
| rule:grants-haste-to-your-creatures | Gimli's Reckless Might | "Creatures you control have haste." | OK |
| rule:graveyard-to-library-top-recursion | Treason of Isengard | "Put up to one target instant or sorcery card from your graveyard on top of your…" | OK |
| rule:leaves-battlefield-trigger-create-token-creature | Zoo Escapees | "When this creature leaves the battlefield, create a Mutagen token." | **MISMATCH — see section 1's member_removal(Zoo Escapees); Mutagen is corpus-verified as "an artifact," not a creature token** |
| rule:level-up-scaling-stats-abilities | Monk Class | "{W}{U}: Level 2" | OK |
| rule:prevents-regeneration | Nekrataal | "That creature can't be regenerated." | OK |
| rule:restricted-purpose-mana | Herd Heirloom | "{T}: Add one mana of any color. Spend this mana only to cast a creature spell." | OK |
| rule:restricted-purpose-mana | Wizard | "{T}: Add {R}. Spend this mana only to cast a planeswalker spell." | OK |
| rule:targeted-destruction | Seal of Primordium | "Sacrifice this enchantment: Destroy target artifact or enchantment." | OK |
| rule:targeted-destruction | Torch Fiend | "Destroy target artifact." | OK |
| rule:targeted-exile | Buy Your Silence | "Exile target nonland permanent." | OK |
| rule:targeted-planeswalker-damage | Burning Fields | "Burning Fields deals 5 damage to target opponent or planeswalker." | OK |
| rule:tribal-anthem-buff | Lifecraft Engine | "Each creature you control of the chosen type other than this Vehicle gets +1/+1." | OK |

**29 of 30 confirmed clean; 1 of 30 (Zoo Escapees) surfaced a real member mismatch not
found during the primary read** — folded into `rule:leaves-battlefield-trigger-create-token-creature`'s
verdict in section 1 (member_removal, plus a PARENT-TREE-CANDIDATES.md flag since the
correct home for it doesn't exist yet). This validates the sampling process is catching
real errors, not just rubber-stamping.

---

## 6. Full member-correction summary (for /triage-emit 6's reconcile step)

member_removals:
- `rule:targeted-bounce-creature` — Otawara, Soaring City
- `rule:untaps-target-land` — High Alert, Staff of Domination
- `rule:leaves-battlefield-trigger-create-token-creature` — Zoo Escapees
- `rule:draw-scaled-by-creature-count` — Culling Dais
- `rule:lifegain-scaled-by-creature-count` — Joraga Peach
- `rule:cast-trigger-transforms-into-creature` — Village Ironsmith // Ironfang
- `rule:creates-token-with-x-scaled-counters` — Forth Eorlingas!

member_additions:
- `rule:targeted-planeswalker-damage` — Insult // Injury (Injury face), per the ratified M8
  mixed-object-class-target rule (already correctly present on targeted-creature-damage and
  targeted-player-damage; this batch adds the missing third leg of the same card).
- `rule:create-token-mana-producing-artifact` — Stone Retrieval Unit
- `rule:token-count-scales-with-x` — Forth Eorlingas! (moved here from the member_removal above)

No KILLs, no MERGEs this batch — all 192 axes are real, evidence-backed, non-duplicate
patterns; the only issues found were per-member evidence-fit mismatches, not axis-level
problems. This is a meaningfully different shape from batches 1-4 (which had real KILL/MERGE
volume) and consistent with batch 5's own finding that the SYNTH prompt has matured enough
that most churn now is member-level, not axis-level.

---

## 7. Batch-feedback for the batch-7 SYNTH prompt

1. **Charge/resource-counter vs. creature-count confusion (2 independent hits this batch:
   Culling Dais on draw-scaled-by-creature-count, Joraga Peach on
   lifegain-scaled-by-creature-count).** Both cards scale an effect by counters accumulated
   ON THE SOURCE ITSELF (charge counters), but SYNTH filed them under a "scales by number
   of creatures you control" axis. Add an explicit prompt rule: before labeling anything
   "scaled-by-creature-count" / "scaled-by-X-count," re-read the quote and confirm the
   counted noun phrase is actually creatures/permanents in play, not counters on the source
   permanent itself — these are easy to conflate because both read as "count something and
   scale an effect."
2. **Token-count-scaling vs. counter-placement-on-token confusion (Forth Eorlingas! on
   creates-token-with-x-scaled-counters).** "Create X tokens" (X scales how MANY tokens)
   and "create a token, put X counters on it" (X scales counters on ONE token) are
   different mechanics that got merged into one axis's membership. Add a prompt rule
   distinguishing "X scales token count" from "X scales counters-per-token."
3. **"rule:" prefix / lane=codebook discipline.** Two cases this batch (Stone Retrieval
   Unit, and the Maul of the Skyclaves/Rosethorn Halberd pair) used the "rule:" prefix on
   slugs that don't exact-match anything in the codebook — one was a near-miss on a real
   axis name (missing the etb- prefix convention it doesn't actually have), the other
   invented two synonymous slugs for a pattern that was never in the codebook at all.
   Reinforce: lane=codebook is ONLY for an exact string match against the supplied codebook
   axis list; anything else, even a very close paraphrase, is lane=free.
4. **Cast-trigger vs. no-spells-cast-trigger (Village Ironsmith // Ironfang).** A card whose
   trigger condition is the ABSENCE of a cast ("if no spells were cast last turn") got
   filed under a cast-trigger axis. Add a prompt rule: "triggers on X" requires X to be the
   actual trigger event, not a condition checked by a different trigger (here, the trigger
   is upkeep; "no spells cast" is a condition, and its polarity is inverted from what the
   axis name implies).
5. **Restriction-wording specificity holding up well.** Zero new instances this batch of
   the batch-5-flagged "restriction qualifier dropped from the quote" pattern — the
   evidence-quote rules added to the batch-6 prompt (restriction-wording specificity,
   cost-vs-effect distinction, effect-suffix precision) appear to be working; keep them
   as-is for batch 7.

---

## 8. Parent flags

Appended to `mtjawnny.github.io/docs/PARENT-TREE-CANDIDATES.md` under "Proposed parents"
(batch-6 subsection): the not-yet-built `rule:leaves-battlefield-trigger-create-token`
parent (needed for Zoo Escapees), the equipment-static-pt-buff rejection note (so it isn't
re-proposed from scratch), and a conditional `rule:activated-tap-or-untap-any-permanent`
parent flag contingent on Captain's Q1 ruling.

---

## 9. Verification

- Verdict count: 165 (existing) + 27 (new) = 192, matches the digest's stated axis count. ✓
- No duplicate axis entries. ✓
- Every MERGE target named: N/A this batch (zero MERGEs). ✓
- Every member_removal / member_addition names an exact card (and face, where relevant). ✓
- QUESTIONS: 2, both under the max-8 cap, both genuine either/ors on wording (not on the
  underlying evidence, which is unambiguous in both cases). ✓

## 10. CAPTAIN RATIFICATION — PARSED DIRECTIVES (2026-07-30)

**AUTHORITATIVE FOR PARSING.** Translated from the 2026-07-30 chat review session
(independent card-by-card audit of this document + Captain's direct rulings). Where this
section conflicts with anything above, THIS SECTION GOVERNS. All card-text claims were
verified against live oracle text in the review session; emit re-verifies against the
corpus (verify-or-drop) as always. Several directives below instruct Claude Code to
FIND-AND-CONFIRM before acting — those are marked; halt loudly if confirmation fails.

### D1 — LEGALITY GATE (new standing ruling, brand-wide; EXPLICIT PARTIAL REVERSAL)
**A card must be legal in at least one format to be a valid target for the engine, the
scan, and every MTJawnny tool.** Stated as brand fact: the corpus may retain non-legal
rows for reference, but no non-legal card is ever tagged, offered to SYNTH, counted in
an axis, surfaced by a tool, or spent tokens on. Un-sets, joke sets, playtest cards
(CMB1/CMB2/MB2 test cards), Unknown Event promos, prototype/event cards — out.
- Implementation: gate on the Scryfall `legalities` object. PASS iff any format value is
  `legal` or `restricted`. Everything else (all `not_legal`/`banned`) FAILS the gate.
  This is GATE #0 — it runs at dataset level before every downstream stage (DET pass,
  batch assembly, SYNTH, tools).
- REVERSAL LOG (rulings registry): this partially overturns the earlier
  "legality is display-layer only; joke/playtest cards stay in corpus; rank buries,
  never excludes" posture. New form of the ruling: Alchemy-only and format-narrow cards
  still pass (they are legal somewhere; paper-over-Alchemy display rules unchanged);
  nowhere-legal cards are excluded outright — the corroboration gate is no longer the
  sole exclusion. Logged Captain-explicit, D6-style.
- **Retroactive membership scrub (Code task):** rescan every member of every codebook
  axis (all versions ≥ current) against Gate #0; emit a scrub report and remove gated
  members. Known hits from this session's audit: Potatoes and Joraga Peach (Unknown
  Event), Heart of a Duelist and Taiga Stadium (playtest — note Taiga Stadium was
  ratified into rule:enters-tapped-conditional in batch 5 §10; the gate removes it
  retroactively, that is intended), and "Wizard" in rule:restricted-purpose-mana
  (unverifiable via web this session — confirm via corpus name index; if playtest/
  Unknown Event, gate it). Pick-a-Beeble: apply the gate mechanically (Attraction
  Commander legality is disputed across sources); its member_removal in D3 stands on
  independent grounds regardless.
- **Batch assembly + full-corpus pass now draw only from gate-passing cards.** Report
  the gated-out count so the full-corpus card total and cost estimate get restated.
- **Precedent rescan (Code task, FIND-AND-CONFIRM):** walk every ratified
  ruling/precedent in the registry, decisions/*.json rationales, and SUP standards;
  identify any derived from now-gated cards; trash those unless independently useful on
  legal-card evidence, and log each disposition. Named suspect: the "Peel Out/Banana
  precedent" cited in this document's Stone Retrieval Unit verdict — it appears in no
  handoff or registry visible to the review session; locate its origin, and strike the
  citation if it cannot be sourced or derives from gated cards (Stone Retrieval Unit's
  membership stands on its Powerstone quote alone either way).

### D2 — Q1 ruled: (b), expand — with the lattice grammar noted in §11
rule:activated-tap-or-untap-any-creature KEEPS its creature scope; sole member Puppet
Strings. NEW captain-authored sibling rule:activated-tap-or-untap-any-permanent; member
Fatestitcher ("{T}: You may tap or untap another target permanent."). The ledgered
rule:activated-tap-target parent unifies them for browsing. Per "don't absorb, expand"
and "small n — kill for fake, never for rare."

### D3 — Q2 ruled: (a), plus member surgery from the independent audit
- rule:etb-pump-target-creature: drop the "not restricted to the controller's own
  creatures" definition clause; keep Herald of the Fair and Yeva's Forcemage; scope
  field reads any-creature (widest member); ownership-scope logged as a facet dimension
  for the schema pass.
- **rule:activated-ability-costs-self-sacrifice: member_removal(Pick-a-Beeble).**
  Verified: it is an Attraction; Visit and Prize are TRIGGERED abilities and "sacrifice
  Pick-a-Beeble" sits inside the Prize EFFECT — fails the axis on both the activated
  requirement and the cost requirement (batch-4 D1 conflation class). Note for the
  record: the section-5 override sample marked this row OK; the true sample result is at
  best 28/30. Roster-based membership audit (D6) exists precisely for this.
- **member_removal(Otawara, Soaring City) is REVERSED — Otawara STAYS in
  rule:targeted-bounce-creature.** Ruled: **M8 GENERALIZES from damage to every
  targeted-<action> family** (registry update): a card targeting multiple object
  classes (AND or OR shape) receives every applicable per-class tag; never a combo tag;
  removal for multi-type text is wrong when the class in question is among the targets.
  The missing per-class bounce siblings (targeted-bounce-artifact / -enchantment /
  -planeswalker) go to the parent-tree ledger as a lattice family, instantiated when
  members arrive (§11 rules; do not author empty).
- rule:leaves-battlefield-trigger-create-token-creature: member_removal(Zoo Escapees)
  stands, but Zoo Escapees is NOT homeless — NEW captain-authored
  rule:leaves-battlefield-trigger-create-token-mutagen (n=1: Zoo Escapees), per the D10
  (batch 5) sibling convention. Withdraw the "no home exists" ledger flag.
- NEW captain-authored rule:activated-untap-target-creature; members High Alert and
  Staff of Domination (both verified "Untap target creature"), rehomed from their
  rule:untaps-target-land removals. Ledger: flag the tap/untap activated family for
  consolidation review at schema pass (it now spans tap-target-creature,
  untap-target-creature, untap-another-permanent, tap-or-untap-any-creature,
  tap-or-untap-any-permanent, untaps-target-land, plus mass variants).
- rule:charge-counter-accumulation: member_addition(Culling Dais) — "{1}, {T}: Put a
  charge counter on Culling Dais" (rehome from its removal above). Joraga Peach's
  candidate rehomes are MOOT — gated by D1.
- All other SUP corrections stand as written: Village Ironsmith // Ironfang removal,
  Forth Eorlingas! move to rule:token-count-scales-with-x, Insult // Injury (Injury)
  addition to targeted-planeswalker-damage, Stone Retrieval Unit addition to
  create-token-mana-producing-artifact (citation caveat per D1).

### D4 — All remaining verdicts stand
All 165 confirmations and 27 new-candidate KEEPs stand as proposed except as modified by
D1–D3. Zero KILLs, zero MERGEs remains true at axis level. New captain-authored axes
this batch: activated-tap-or-untap-any-permanent, activated-untap-target-creature,
leaves-battlefield-trigger-create-token-mutagen (3).

### D5 — STANDING PROTOCOL RULE: remove-and-rehome
Every member_removal must answer "where does this card actually belong?" — an existing
axis (member_addition), a convention-consistent new sibling (captain-author candidate),
or an explicit "no home; ledger-flagged." Silent stranding is a protocol violation.
Batch-5 set the pattern; batch 6 missed it three times (High Alert/Staff, Culling Dais,
Zoo Escapees). Bake into SUP-TRIAGE-PROTOCOL.md and triage-beta.

### D6 — MEMBER ROSTER regression (Code task, FIND-AND-CONFIRM)
This document omitted the MEMBER ROSTER section required since batch 4's punch list and
delivered in batch 5. Regenerate the roster for all 192 axes (names only, no oracle
text) and append it to this file BEFORE reconcile; Captain audits it before batch 7
assembly. Fix triage-beta so the roster is structurally mandatory. While regenerating,
if the roster surfaces additional members that obviously belong in different existing
buckets (per the D5 rule and this session's patterns), Code may reorganize —
member-level moves only, quote-verified, every move listed in the emit report for
Captain's post-hoc review; anything judgment-ambiguous halts loudly instead.

### D7 — Recently-killed appendix (Code task, FIND-AND-CONFIRM)
Equipment-static-buff was re-invented by SYNTH for the third consecutive batch. Confirm
whether the recently-killed appendix (escalated at batch 5) was actually built into the
batch-6 SYNTH prompt. If unbuilt: BUILD IT NOW; it blocks batch-7 submission. If built:
it failed — diagnose and fix before batch 7.

### D8 — Batch-7 feedback additions (beyond section 7)
1. Effect-POSITION check joins the ability-type check: a cost-axis member must show the
   named action on the cost side of the colon; an effect inside resolution text never
   satisfies a cost axis (Pick-a-Beeble class).
2. M8-generalized: multi-class targeted-<action> cards get every applicable per-class
   tag; never removed for breadth.
3. n=2 OTHER-lane tier: the assembly script's no_other_lane_reinforcement_reason must
   state "spot-checked, not exhaustively cleared" per this document's own methodology
   note — carry that honesty forward.
4. All section-7 items stand.

---

## 11. CORPUS-WIDE PROCESSING PLAN (ratified direction — record in docs/, execute per sequencing)

Captain has ratified the three-lane design for the full-corpus pass, plus a lattice
grammar layer. Claude Code: persist this section into the protocol docs (new
docs/CORPUS-PASS-PLAN.md or equivalent), wire the sequencing, and treat the lattice
grammar as a naming-discipline change effective immediately.

### 11.1 Three lanes
- **Lane 1 — DET pre-tag pass (runs first, token-free, re-runs on every Scryfall
  refresh).** Every codebook axis gets classified DET-able or SYNTH-only. DET-able =
  membership decidable by an anchored oracle-text pattern with polarity
  canonicalization and no judgment (enters-tapped, the three activation-restriction
  strings, "can't be regenerated", no-maximum-hand-size, stun counters, energy, the
  Ring, landfall—, kicker, etc.). Each pattern is proposed with a measured corpus
  hit-list, sampled and RATIFIED by Captain like a scoring constant, versioned, never
  silently tuned. Provenance: rule-derived (full weight). Gate #0 applies.
- **Lane 2 — SYNTH judgment pass.** DET-owned axes are STRIPPED from the embedded
  codebook (this is the codebook condensation's biggest lever). SYNTH hunts judgment
  territory: jobs, rhystic shapes, cheat-into-play, Tier-3 same-job-different-words.
  Runs only on gate-passing cards; restate the card count and cost estimate after the
  gate + strip land.
- **Lane 3 — Reconcile with halt-loudly.** SYNTH never sees DET pre-tags (no
  anchoring). At reconcile: SYNTH free-lane output matching a DET-owned axis =
  corroboration; contradiction of a DET pattern = halt-loudly review row.

### 11.2 Lattice grammars ("prebuilt buckets," done safely)
Captain's intent: game concepts derive families — once
activated-tap-or-untap-any-permanent exists, the whole
`activated-tap-or-untap-<scope>` family is enumerable a priori (any/own/opponent ×
creature/artifact/permanent, etc.). Ratified mechanism:
- For a family, Captain ratifies a GRAMMAR: an action stem plus ordered facet slots
  with closed vocabularies (e.g. `activated-tap-or-untap-<ownership?><class>`;
  `targeted-bounce-<class>`; `<trigger>-create-token-<type>`). The grammar, not a list
  of empty axes, is the prebuilt bucket.
- **Virtual nodes:** unpopulated lattice slugs are NOT authored into the codebook (an
  axis with zero members is a hypothesis, not a ruling, and empty axes bloat the
  embedded codebook — the cost driver). A node INSTANTIATES the moment a
  quote-verified member arrives, no fresh ratification needed because the grammar was
  ratified.
- **Labeling discipline upgrade (fixes section-7 item 3 for good):** SYNTH may compose
  a slug from a ratified grammar and have it count as lane=codebook-grammar (new lane
  value) rather than lane=free — eliminating the near-miss invented-slug problem
  (etb-prefix confusion, synonymous equipment slugs) by making the composition rule
  deterministic. Anything not exact-codebook and not grammar-composable stays
  lane=free.
- Emit derives parents from grammar structure for free (stem = parent, facets =
  children), feeding the ratified derived-parents scheme. Existing seeded grammars:
  create-token-<type> (batch-5 D14), etb-create-token-<type> and
  leaves-battlefield-trigger-create-token-<type> (batch-5 D10 + this batch),
  targeted-<action>-<class> (M8 generalized, D3), activated-tap-or-untap-<scope> (D2),
  draw-second/cast-second prefix scheme (batch-5 D12). Code drafts the formal grammar
  file; Captain ratifies before the full pass.
- If lattice grammars prove not to help agent efficiency in practice, they get scraped
  per Captain — measure: rate of lane=free near-miss slugs per batch, before vs after.

### 11.3 Sequencing (amends batch-5 D17; registry update)
1. GATE #0 — legality gate implemented + retroactive scrub + precedent rescan (D1).
2. Keyword-bucket extraction (already ratified, unchanged).
3. COMBINED per-axis walk: naming audit + agent-legible definition rewrite +
   DET-ability classification + grammar drafting (one walk, four columns).
4. DET rule authoring + ratification + full-corpus DET pass (gate-passing cards).
5. Codebook condensation (largely automatic via DET strip).
6. SYNTH full-corpus pass (~$100 budget re-estimated post-gate/strip; explicit Captain
   trigger still required).
7. SCHEMA PASS (unchanged agenda + tap/untap consolidation + ownership facet + lattice
   formalization).
8. Display build per READY-TO-SHIP contract.

### 11.4 Language standard (Captain's stated goal)
Every rule name and definition must be understandable and reproducible by an agent with
no session context: grammar-composed slugs, closed facet vocabularies, glossary for
shorthand (scroll, regrowth), definitions that state trigger/cost/effect position
explicitly. This is the same standard as batch-5 D17's agent-legibility directive, now
extended: the naming audit is load-bearing for lattice derivation, DET patterns, and
parent derivation alike.

---

**STOP.** Sections 10–11 are the authoritative record for batch 6. Claude Code: execute
the FIND-AND-CONFIRM tasks (D1 scrub + precedent rescan, D6 roster, D7 appendix) and the
D1 gate BEFORE running `/triage-emit 6`; reorganization latitude per D6; halt loudly on
any ambiguity, failed gate, or unspecified decision. Then emit: parse §10, verify
every quote and member against the gate-passing corpus, write decisions/batch-6.json,
reconcile to codebook v0.6, restate the full-corpus count/cost post-gate, assemble
batch 7 from gate-passing cards only, and STOP for go-ahead.

---

## 12. Gate #0 execution report (D1, run 2026-07-30, before this document's emit)

**Implementation.** `foundry_common.gate_passes(card)` / `load_corpus_gated()` added to
`experiments/foundry_common.py`: a card passes iff any Scryfall `legalities` value is
`legal` or `restricted`. Scoped to the T3 Axis Foundry pipeline only (`foundry_common.py`'s
consumers) — `tier_engine.py`'s own `load_cards()`/`CARDS_PATH` path, used by production
tier scoring outside the foundry, is untouched. This is a scope decision I made rather than
silently guessed broad; flagging it explicitly so Captain can correct it if D1's "every
MTJawnny tool" was meant to reach the live tier engine too.

**Retroactive scrub** (`experiments/foundry_gate0_scrub.py`, run against codebook v0.5):
checked 3,085 member rows across all 362 axes (every status, not just active); removed
173 gated-out rows spanning 92 axes. Zero missing-from-corpus rows (no data-drift halt).
Determinism verified x2 byte-identical on the resulting member sets. Full report:
`experiments/out/foundry/gate0_scrub_report.json`. Named suspects from D1 confirmed:
Taiga Stadium (removed from rule:enters-tapped-conditional, as D1 anticipated) plus 91
other axes' gated members surfaced by the same mechanical rule (Cyclopean Titan, Gnome-Made
Engine, Item Crate, and 170 others — none previously flagged, all caught by the same
single mechanical check). Batch-6's own new candidates (Potatoes, Joraga Peach, Heart of a
Duelist, "Wizard") are handled separately at decisions/batch-6.json build time, per below —
they were never in codebook.json to begin with, since batch 6 hasn't been reconciled yet.

**"Wizard" resolved** (D1's specific ask): the corpus has exactly one card named "Wizard"
with the quoted restricted-purpose-mana ability — oracle_id `e2402676-...`, a Commander
Masters token (`set=tcmm`, `layout=token`), not_legal in every format. Gated. This is a
genuine token-card corpus row (not a data error) that will be dropped from
rule:restricted-purpose-mana's batch-6 confirmation when decisions/batch-6.json is built.

**Precedent rescan** (D1's second ask): walked every string value in `decisions/batch-1.json`
through `batch-5.json` and grepped `MASTER-HANDOFF.md`, `MASTER-HANDOFF-ADDENDUM-3.md`,
`SUP-TRIAGE-PROTOCOL.md`, `KEYWORD-LEDGER-CANDIDATES.md` for exact card-name matches,
checking every hit against Gate #0. Found 6 real card citations that fail the gate
(Exit Through the Grift Shop, Buzzing Whack-a-Doodle, Cyclopean Titan, Gnome-Made Engine,
Item Crate, Taiga Stadium) — all were already either historical member_removals (no live
effect) or live codebook members already caught and fixed by the retroactive scrub above.
**No dangling ratified rule turned out to rest solely on a now-gated card's evidence** —
the scrub and the rescan agree, which is the result I'd want to see, not one I'm assuming.
One real citation problem found and fixed: this document's own "Peel Out/Banana precedent"
line (struck above) — Peel Out was never a ratified precedent and is itself gated.

---

## 13. Batch-6 decisions/emit-time exclusions from Gate #0 [SUPERSEDED — see below]

The paragraph originally here (identifying 4 gated cards: Potatoes, Joraga Peach, Heart of
a Duelist, "Wizard") was **incomplete**. It was written before `decisions/batch-6.json` was
actually built. When `foundry_adapt_batch6_decisions.py` ran its belt-and-suspenders Gate
#0 re-check (checking every one of this batch's 756 confirmed member rows directly against
`foundry_common.gate_passes()`, not just the 4 named suspects), it HALTED on the very first
mismatch (**Everythingamajig**, an Unstable/`ust` card nobody had flagged). That halt was
correct behavior, not a bug — it caught that the manual 4-card list was a undercount.

**Full mechanical recheck result: 53 gated member-rows across 39 axes, 29 unique cards.**
The gated cards break cleanly into Scryfall `set_type` categories — all mechanically
nowhere-legal per Gate #0's literal rule, including categories D1's illustrative examples
didn't name explicitly (emblem, planar, memorabilia) but which are definitionally never
legal in any constructed format for the same underlying reason as the named categories:

- **funny** (Un-sets/joke sets — D1-named): Everythingamajig, Faerie Aerie, Fifth Stage of
  Magic Design, Heroes of Kamigawa, Joraga Peach, Peel Out, Photo Op, Potatoes, Save Point,
  Side to Side, Surprise Party, The Joiner of Cats, The Strixhaven-Lorwyn Rover, Timmy
  Power Gamer, Trivia Contest, Drive to Work, Voracious Vacuum
- **token** (bare token printings — D1-named): Bushy Bodyguard, Event: Rat King's
  Revolution, Map, "Wizard"
- **masters** (Mystery Booster playtest — D1-named): Heart of a Duelist, Lich's Duel Mastery
- **emblem** (not named by D1, but never deck-includable, same non-legal status): Mordenkainen
  Emblem, Rowan, Scholar of Sparks Emblem
- **planar** (Planechase plane cards, not named by D1, same non-legal status): Game
  Knights Live, The Lux Foundation Library
- **memorabilia** (not named by D1, promotional/non-tournament): Phoberos Reaver, The
  Vanquisher
- **alchemy** (Viconia, Disciple of Violence — this specific `hbg` printing's own
  legalities show it not_legal in every format including alchemy itself; does not
  contradict D1's "Alchemy-only cards still pass" clause, since that clause requires the
  card to actually BE alchemy-legal, which this printing isn't)

I flagged this scope question (does Gate #0's mechanical rule reach categories D1 didn't
explicitly name?) rather than silently deciding either way — concluded yes, apply the rule
literally as stated ("PASS iff any format value is legal or restricted... Everything else
FAILS"), since D1's named examples are illustrative, not an exhaustive closed list, and
narrowing the mechanical check to only the named categories would require inventing a
distinction D1's own text doesn't draw. Full list and per-axis breakdown in
`decisions/batch-6.json`'s `note_to_reconcile` field and each affected axis's `notes`.

Pick-a-Beeble (set=unf, Unfinity) passes Gate #0 mechanically, exactly as D1 anticipated;
it's removed from rule:activated-ability-costs-self-sacrifice on the independent D3 grounds
instead (Attraction Visit/Prize are triggered, not activated; the sacrifice sits inside the
Prize effect, not the cost).


---

## 14. MEMBER ROSTER — batch-6 contribution, post-corrections (D6, regenerated 2026-07-30)

Names only, no oracle text, per D6. Covers all 192 batch-6 axes plus the 3 new
captain-authored axes from D2/D3 (activated-tap-or-untap-any-permanent,
activated-untap-target-creature, leaves-battlefield-trigger-create-token-mutagen) = 195
rows. This is batch 6's OWN confirmation/new-candidate contribution after applying every
correction in sections 1-3, 12-13 (member_removals, member_additions, Gate #0 exclusions,
D2/D3 rehomes) — not each axis's total cumulative codebook membership (existing axes carry
additional members from batches 1-5 already in codebook.json; a "(n=0)" row below means
this batch's own example got fully excluded, not that the axis is empty in the codebook).

Generated by re-parsing the digest mechanically and applying every correction as code,
rather than re-typing 195 lists by hand — this caught two real bugs the prose sections
above didn't (both fixed before this roster was finalized, not left for Captain to catch):

1. **`rule:charge-counter-accumulation` double-count.** D3 said "member_addition(Culling
   Dais) — rehome from its removal above," but Culling Dais was already an independent
   batch-6-confirmed member of this axis on its own distinct quote ("Put a charge counter
   on this artifact," separate from the "draw a card for each charge counter" quote that
   got it removed from rule:draw-scaled-by-creature-count). No rehome was needed — D3's
   instruction and the pre-existing confirmation were about the SAME fact stated two ways.
   Fixed to avoid a duplicate member row; net effect on the axis is unchanged (Culling
   Dais was always going to end up here either way).
2. **`rule:death-trigger-counter-transfer` empties to n=0 this batch.** Joraga Peach was
   this axis's only batch-6 confirmation hit, and Joraga Peach is fully gated (Gate #0).
   Checked codebook.json directly: the axis already has 3 real members from batch 3, so
   this is not an orphaned/dying axis — it simply gets zero reinforcement from batch 6.
   Noted inline rather than silently dropped from the roster.

No other reorganization-worthy misfiles surfaced during roster generation beyond what
sections 1-3 already found and fixed; this list is mechanical, so anything already
corrected upstream propagates through cleanly.

- `rule:activated-ability-costs-self-sacrifice` (n=33): A-Skemfar Elderhall, Ark of Blight, Bad River, Booby Trap, Brittle Effigy, Burnished Hart, Cathar Commando, Culling Dais, Emberwilde Augur, Everythingamajig, Expert-Level Safe, Fanatical Firebrand, From Beyond, Kithkin Armor, Lawbringer, Lord of Tresserhorn, Map, Misty Palms Oasis, Moonsilver Key, Navigation Orb, Papalymo Totolymo, Pictures of Spider-Man, Racers' Ring, Relic of Progenitus, Save Point, Seal of Primordium, The Book of Vile Darkness, The Surgical Bay, Torch Fiend, Trivia Contest, Unyaro Griffin, Vexing Bauble, Witching Well
- `rule:activated-destroy-target-land` (n=2): Ark of Blight, Keldon Arsonist
- `rule:activated-draw-a-card` (n=9): A-Spell Satchel, Fungal Plots, Greed, Misty Palms Oasis, Racers' Ring, Relic of Progenitus, Staff of Domination, The Surgical Bay, Vexing Bauble
- `rule:activated-exile-graveyard-creature-card` (n=7): Abyssal Harvester, Conversion Chamber, Rag Dealer, Sibsig's Artisan, The Ooze, The Scarab God, Viconia, Disciple of Violence
- `rule:activated-exile-graveyard-creature-for-token` (n=2): Fungal Plots, Havengul Runebinder
- `rule:activated-loot` (n=2): Furtive Analyst, Strix Lookout
- `rule:activated-sacrifice-any-permanent-for-self-counter` (n=2): Dreadmobile, Sawblade Skinripper
- `rule:activated-tap-or-untap-any-creature` (n=1): Puppet Strings
- `rule:activated-tap-or-untap-any-permanent` (n=1): Fatestitcher
- `rule:activated-tap-target-creature` (n=9): Akroan Jailer, Burden of Guilt, Pacification Array, Silkbind Faerie, Staff of Domination, Steam Catapult, Thornscape Apprentice, Vengeful Villagers, Weakstone's Subjugation
- `rule:activated-untap-another-permanent` (n=2): Kelpie Guide, Vizier of Tumbling Sands
- `rule:activated-untap-target-creature` (n=2): High Alert, Staff of Domination
- `rule:activation-restricted-only-during-your-turn` (n=3): Circle of Elders, Gutterbones, Rag Man
- `rule:activation-restricted-to-own-upkeep` (n=1): Emberwilde Augur
- `rule:activation-restricted-to-sorcery-speed` (n=13): A-Skemfar Elderhall, Beetle, Legacy Criminal, Birthing Pod, Champion of the Weird, Endbringer's Revel, Gollum's Bite, Inside Source, Map, Najeela, the Blade-Blossom, Predation Steward, Scavenged Brawler, Sibsig's Artisan, Sultai Monument
- `rule:additional-cost-discard-a-card` (n=2): Big Score, Unexpected Windfall
- `rule:additional-cost-sacrifice-permanent` (n=1): Final Vengeance
- `rule:alt-cost-sacrifice-lands` (n=1): Dwarven Landslide
- `rule:animates-land-into-creature` (n=1): Creeping Tar Pit
- `rule:attack-trigger-create-token` (n=3): Sentinel of the Nameless City, Silverwing Squadron, The Spear of Leonidas
- `rule:attack-trigger-loot` (n=1): Vaultbreaker
- `rule:attack-trigger-mass-pump-attackers` (n=1): Ultra Magnus, Tactician // Ultra Magnus, Armored Carrier
- `rule:attack-trigger-pump-any-creature` (n=1): Yotian Frontliner
- `rule:attack-trigger-untap-attacker` (n=1): Tadeas, Juniper Ascendant
- `rule:aura-locks-enchanted-creature-tapped` (n=2): Frozen in Ice, Unquenchable Thirst
- `rule:buff-scales-with-land-type-count` (n=1): Lashwrithe
- `rule:burst-draw` (n=13): Aetherflux Conduit, Big Score, Birthday Escape, Blood Pact, Brokers Charm, Distant Memories, Dream Cache, Scatter Arc, Tragic Lesson, Unexpected Conversion, Unexpected Windfall, Weight of Memory, Witching Well
- `rule:cannot-block-restriction` (n=4): Dirty Wererat, Razorlash Transmogrant, Skrelv, Defector Mite, Visions of Brutality
- `rule:cant-be-blocked-by-color` (n=2): Lightning Mare, Vine Mare
- `rule:cant-be-countered` (n=3): Kavu Chameleon, Lightning Mare, Tyrranax Rex
- `rule:cantrip` (n=2): Provoke, Uncomfortable Chill
- `rule:cast-from-exile-trigger` (n=1): Fire Lord Zuko
- `rule:cast-from-top-of-library` (n=1): Into the Pit
- `rule:cast-trigger-transforms-into-creature` (n=1): Veiled Serpent
- `rule:changes-color-creature` (n=3): Distorting Lens, Possessed Nomad, Prismwake Merrow
- `rule:changes-creature-type-text` (n=2): Artificial Evolution, New Blood
- `rule:charge-counter-accumulation` (n=4): Conversion Chamber, Culling Dais, Private Research, Tidal Influence
- `rule:cheat-creature-into-play` (n=3): Cryptic Gateway, Ghalta, Stampede Tyrant, Timmy, Power Gamer
- `rule:choose-creature-type-on-etb` (n=2): Cover of Darkness, Lifecraft Engine
- `rule:combat-damage-to-player-draws-card` (n=2): Tadeas, Juniper Ascendant, The Lux Foundation Library
- `rule:combat-damage-triggers-discard` (n=2): Rakdos Ringleader, Zhang Liao, Hero of Hefei
- `rule:combat-damage-triggers-loot` (n=1): Prowler, Misguided Mentor
- `rule:combat-trick-pump-own-creature` (n=16): Aspirant's Ascent, Brokers Charm, Burrog Barrage, Enshrouding Mist, Fists of the Anvil, Gift of the Viper, Heroic Teamwork, Karametra's Blessing, Magic Damper, Predation Steward, Predator's Strike, Simic Charm, Staggering Size, Stonewood Invocation, Strength in Numbers, Temur Charm
- `rule:combat-trigger-auto-attach-equipment` (n=1): Ria Ivor, Bane of Bladehold
- `rule:compensates-controller-with-token` (n=2): Buy Your Silence, Hunted Bonebrute
- `rule:conditional-attack-restriction-by-opponent-land-type` (n=2): Red Cliffs Armada, Serpent of the Endless Sea
- `rule:conditional-creature-status` (n=1): Athreos, Shroud-Veiled
- `rule:copies-cast-spell` (n=4): Curse of Echoes, Mica, Reader of Ruins, Rowan, Scholar of Sparks Emblem, The Strixhaven-Lorwyn Rover
- `rule:copy-creature-token` (n=2): Aggressive Biomancy, Gigantoplasm
- `rule:cost-reduction` (n=10): Artist's Talent, Gargos, Vicious Watcher, Heroes of Kamigawa, Mana Matrix, Rhonas's Monument, The Destined Warrior, The Wind Crystal, Undead Warchief, Voyager Quickwelder, Zirda, the Dawnwaker
- `rule:counter-removal-as-activation-cost` (n=8): A-Spell Satchel, Academy Elite, Conversion Chamber, Fertilid, Glistener Seer, Grasping Shadows // Shadows' Lair, Noble's Purse, Predation Steward
- `rule:counters-noncreature-spell` (n=1): Scatter Arc
- `rule:counters-target-spell` (n=6): Glorious Gale, Horribly Awry, Sinister Sabotage, Statute of Denial, Thought Collapse, Unravel
- `rule:create-token-creature` (n=14): A-Skemfar Elderhall, Chatterstorm, Conversion Chamber, Depose // Deploy, Elemental Eruption, Fertile Imagination, Goblin Rally, Havengul Runebinder, Huatli, Warrior Poet, Side to Side, Sorin, Lord of Innistrad, Spirit Summoning, Wild Hypothesis, Wrangler of the Damned
- `rule:create-token-mana-producing-artifact` (n=2): Peel Out, Stone Retrieval Unit
- `rule:create-token-treasure` (n=10): Big Score, Bill Ferny, Bree Swindler, Buy Your Silence, Cindercone Smite, Depths of Desire, Guild Artisan, Noble's Purse, Pick-a-Beeble, Pictures of Spider-Man, Unexpected Windfall
- `rule:created-token-enters-tapped` (n=2): Illustrious Historian, The Final Days
- `rule:creates-token-with-x-scaled-counters` (n=1): Wild Hypothesis
- `rule:damage-divided-among-multiple-targets` (n=4): Huatli, Warrior Poet, Jaya's Immolating Inferno, Meteor Shower, Ureni, the Song Unending
- `rule:death-of-your-permanents-grows-this-creature` (n=1): Haruspex
- `rule:death-trigger-counter-transfer` (n=0): (none)  [Gate #0 emptied this batch's contribution; axis retains prior-batch members in codebook.json]
- `rule:death-trigger-scroll-regrowth` (n=1): Living Lightning
- `rule:death-trigger-token-creation` (n=2): Chasm Skulker, Hallowed Spiritkeeper
- `rule:delayed-draw-next-upkeep` (n=2): Gravebind, Heal
- `rule:direct-damage-any-target` (n=12): Banefire, Boilerbilges Ripper, Chandra, Heart of Fire, Fanatical Firebrand, Goblin Bangchuckers, Irencrag Pyromancer, Jaya's Immolating Inferno, Mudbutton Torchrunner, Prophetic Bolt, Seismic Wave, Spider-Man 2099, Staggershock
- `rule:doubles-counter-placement` (n=1): Michelangelo, Weirdness to 11
- `rule:drain-life` (n=4): Acolyte of Aclazotz, Dakmor Ghoul, Mind Drain, Triumphant Getaway
- `rule:drain-on-creature-death` (n=1): Bastion of Remembrance
- `rule:draw-cards-with-life-loss-cost` (n=4): Bitter Revelation, Blood Pact, Grasping Shadows // Shadows' Lair, Sanguimancy
- `rule:draw-scaled-by-creature-count` (n=3): Biomantic Mastery, Camaraderie, Winged Portent
- `rule:draw-second-card-trigger-plus1-counter` (n=1): Codespell Cleric
- `rule:draw-trigger-self-counter-growth` (n=2): Agent Maria Hill, Chasm Skulker
- `rule:enters-tapped` (n=26): A-Skemfar Elderhall, Alirios, Enraptured, Bad River, Caldera Lake, Carrion Crow, Creeping Tar Pit, Elvish Rejuvenator, Forgotten Sentinel, Gutterbones, Highland Weald, Memorial to War, Mistvault Bridge, Misty Palms Oasis, Mountain Valley, Noble's Purse, Nomad Outpost, Path to the Festival, Racers' Ring, Retrofitted Transmogrant, Revenge of the Rats, Swiftwater Cliffs, The Falcon, Airship Restored, The Surgical Bay, Thornglint Bridge, Woodland Stream, Xander's Lounge
- `rule:enters-tapped-conditional` (n=5): Arena of Glory, Frostboil Snarl, Minas Tirith, Shattered Sanctum, Wild Roads
- `rule:etb-and-attack-trigger` (n=6): Borborygmos and Fblthp, Kami of Transmutation, Omo, Queen of Vesuva, Sentinel of the Nameless City, Sidisi, Brood Tyrant, Vengeful Ancestor
- `rule:etb-auto-attach-to-own-creature` (n=4): Maul of the Skyclaves, Piston Sledge, Rosethorn Halberd, Thunder Lasso
- `rule:etb-bounce-other-creature` (n=2): Monk Class, Separatist Voidmage
- `rule:etb-counter-on-other-creature` (n=9): Aerie Auxiliary, Ascendant Dustspeaker, Clay Champion, Grafted Growth, Inspired Inventor, Restorative Technique, Sandskitter Outrider, Trufflesnout, Voracious Vacuum
- `rule:etb-create-token` (n=6): Gilded Goose, Glacier Godmaw, Niko, Light of Hope, Overencumbered, Sentinel of the Nameless City, Welcome to . . . // Jurassic Park
- `rule:etb-create-token-creature` (n=23): Alirios, Enraptured, Bastion of Remembrance, Brood Butcher, Charforger, Clarion Cathars, Edgewall Pack, Faerie Aerie, Falcon Abomination, Farmer Cotton, Firebender Ascension, Ghired, Conclave Exile, Hero of the Nyxborn, Huatli, Poet of Unity // Roar of the Fifth People, Illustrious Historian, Inside Source, Inspired Inventor, Okoye, Dora Milaje Leader, Scion Summoner, Scurry of Gremlins, Secure Detention, Spiked Corridor // Torture Pit, Tempt with Bunnies, Whirler Rogue
- `rule:etb-create-token-creature-conditional` (n=3): Nightsquad Commando, Venser, Corpse Puppet, Verix Bladewing
- `rule:etb-create-token-food` (n=2): Farmer Cotton, Samwise Gamgee
- `rule:etb-create-token-mutagen` (n=5): Genghis Frog, Michelangelo, Weirdness to 11, Raphael, the Muscle, The Ooze, Zoo Escapees
- `rule:etb-destroy-target-enchantment` (n=3): Brokers Charm, War Priest of Thune, Wispmare
- `rule:etb-draw-card` (n=6): Elvish Visionary, Rune of Flight, Save Point, Spirited Companion, Stupefying Touch, Woodland Acolyte // Mend the Wilds
- `rule:etb-exile-graveyard-card` (n=2): Lich's Duel Mastery, Mastermind Plum
- `rule:etb-gain-life` (n=7): Arborback Stomper, Dawning Angel, Shu Grain Caravan, Swiftwater Cliffs, Thragtusk, Trufflesnout, Windgrace Acolyte
- `rule:etb-loot` (n=3): Quicksilver Fisher, Statute of Denial, Viashino Racketeer
- `rule:etb-mass-pump-your-creatures` (n=1): Moonshaker Cavalry
- `rule:etb-modal-choice` (n=6): Coliseum Behemoth, Inspired Inventor, Primaris Eliminator, Sandskitter Outrider, Trufflesnout, Wingbane Vantasaur
- `rule:etb-pump-target-creature` (n=2): Herald of the Fair, Yeva's Forcemage
- `rule:etb-scry` (n=2): Lazav, the Multifarious, Witching Well
- `rule:etb-tutor-to-hand` (n=5): Farfinder, Fierce Empath, Huatli, Poet of Unity // Roar of the Fifth People, Spellseeker, Sphinx Summoner
- `rule:etb-with-counters` (n=13): Aether Figment, Bushy Bodyguard, Fertilid, Fifth Stage of Magic Design, Frontier Mastodon, Molly Hayes, Runaway, Morlun, Devourer of Spiders, Noble's Purse, Phantom Flock, Razorlash Transmogrant, Retrofitted Transmogrant, Tidal Influence, Zoanthrope
- `rule:etb-with-negative-counters` (n=2): Bristlebane Battler, Morselhoarder
- `rule:etb-with-oil-counters` (n=2): Glistener Seer, Predation Steward
- `rule:evasion-vs-high-power-blockers` (n=2): Kithkin Armor, Tadeas, Juniper Ascendant
- `rule:evasion-vs-low-power-blockers` (n=2): Hierophant Bio-Titan, Prowler, Misguided Mentor
- `rule:exile-until-source-leaves` (n=4): Chained to the Rocks, Constricting Sliver, Drive to Work, Lumbering Battlement
- `rule:fixed-lifegain` (n=9): Ivory Crane Netsuke, Last Kiss, Path of Peace, Ray of Dissolution, Recumbent Bliss, Soul Shred, Staff of the Sun Magus, Swallowing Plague, Vengeant Vampire
- `rule:forced-attack-each-combat` (n=5): Berserkers of Blood Ridge, Curse of the Nightly Hunt, Guise of Fire, Phoberos Reaver, Sprinting Warbrute
- `rule:forced-hand-reveal` (n=1): Struggle for Sanity
- `rule:forces-creature-to-attack` (n=1): Heckling Fiends
- `rule:forces-creature-to-be-blocked` (n=2): Irresistible Prey, Provoke
- `rule:forces-opponent-sacrifice` (n=1): Vindictive Lich
- `rule:free-cast` (n=4): Aetherflux Conduit, Extract Brain, Guff Rewrites History, Spelltwine
- `rule:free-sacrifice-outlet` (n=1): Acolyte of Aclazotz
- `rule:gives-energy-counters-immediately` (n=3): Consulate Surveillance, Inspired Inventor, Servant of the Conduit
- `rule:grants-ability-at-threshold-board` (n=1): Zegana, Utopian Speaker
- `rule:grants-ability-at-threshold-self` (n=3): Dirty Wererat, Possessed Nomad, Swarmborn Giant
- `rule:grants-additional-combat-phase` (n=4): Lightning Runner, Najeela, the Blade-Blossom, Save Point, Scourge of the Throne
- `rule:grants-creature-type` (n=3): Avatar Destiny, Captain's Hook, Samurai's Katana
- `rule:grants-extra-turn` (n=1): Ultimecia, Time Sorceress // Ultimecia, Omnipotent
- `rule:grants-haste-to-created-tokens` (n=2): Lightning Coils, Welcome to . . . // Jurassic Park
- `rule:grants-haste-to-your-creatures` (n=2): Gimli's Reckless Might, Push the Limit
- `rule:grants-trample-to-other-creatures` (n=2): Aggressive Mammoth, Brawn
- `rule:grants-unblockable-target` (n=1): Jailbreak Scheme
- `rule:graveyard-to-hand-recursion` (n=4): Endbringer's Revel, Jared Carthalion, Myr Reservoir, Restock
- `rule:graveyard-to-library-shuffle-in` (n=2): Memory's Journey, Stroke of Luck
- `rule:graveyard-to-library-top-recursion` (n=3): False Mourning, Treason of Isengard, Woodland Acolyte // Mend the Wilds
- `rule:individual-cost-reduction` (n=4): Hollow Marauder, Khalni Hydra, Melek, Reforged Researcher, Writhing Necromass
- `rule:innate-unblockable` (n=3): Aether Figment, Creeping Tar Pit, Vedalken Infiltrator
- `rule:kicker-conditional-bonus-effect` (n=8): Aether Figment, Bog Badger, Dauntless Unity, Dwarven Landslide, Heroic Teamwork, Orim's Chant, Temporal Firestorm, Verix Bladewing
- `rule:land-fetch-to-battlefield` (n=4): Bad River, Cartographer's Survey, Elvish Rejuvenator, Navigation Orb
- `rule:landfall-gain-life` (n=1): Grazing Gladehart
- `rule:landfall-self-pump` (n=1): Glacier Godmaw
- `rule:leaves-battlefield-returns-exiled-card` (n=3): Aurelia's Vindicator, Champion of the Weird, Wormfang Turtle
- `rule:leaves-battlefield-trigger-create-token-creature` (n=1): Thragtusk
- `rule:leaves-battlefield-trigger-create-token-mutagen` (n=1): Zoo Escapees
- `rule:level-up-scaling-stats-abilities` (n=2): Monk Class, Skywatcher Adept
- `rule:library-dig-put-onto-battlefield` (n=1): The Joiner of Cats
- `rule:library-dig-to-hand` (n=3): Anticipate, Militia Bugler, Prophetic Bolt
- `rule:library-top-visibility` (n=1): Into the Pit
- `rule:life-total-reset` (n=1): Form of the Dragon
- `rule:lifegain-scaled-by-creature-count` (n=2): Camaraderie, Depose // Deploy
- `rule:lifegain-scaled-by-permanent-color-count` (n=2): Breathe Your Last, Treva, the Renewer
- `rule:lifegain-triggered-counter` (n=1): Gideon's Company
- `rule:mana-activated-pump-self` (n=8): A-Kargan Intimidator, Cursed Ronin, Freejam Regent, Igneous Cur, Jetmir's Fixer, Lightning Mare, Minotaur Sureshot, Vengeful Firebrand
- `rule:mass-counter-distribution` (n=5): Fire Lord Zuko, Havengul Runebinder, Nykthos Paragon, Silkguard, Vault 12: The Necropolis
- `rule:mass-creature-destruction` (n=3): No Witnesses, Sublime Exhalation, The Nipton Lottery
- `rule:mass-damage-creatures-and-players` (n=1): Temporal Firestorm
- `rule:mass-damage-opponent-creatures-only` (n=2): Cosmotronic Wave, Seismic Wave
- `rule:mass-debuff-opponent-creatures` (n=3): A-Skemfar Elderhall, Primaris Eliminator, Uncomfortable Chill
- `rule:mass-graveyard-exile` (n=3): Erebos's Intervention, Identity Crisis, Relic of Progenitus
- `rule:mass-pump-your-creatures` (n=5): Camaraderie, Dauntless Unity, Esquire of the King, Morale, Rush of Battle
- `rule:mass-untap-and-haste-stolen-creatures` (n=2): Smelt-Ward Gatekeepers, Twisted Fealty
- `rule:mass-untap-your-creatures` (n=5): Lightning Runner, Najeela, the Blade-Blossom, Save Point, Scourge of the Throne, The Nipton Lottery
- `rule:mill-self-cards` (n=4): Avatar Destiny, Founding the Third Path, Grizzled Angler // Grisly Anglerfish, Windgrace Acolyte
- `rule:modal` (n=9): Brokers Charm, Epic Fight, Erebos's Intervention, Heliod's Intervention, Mastermind's Acquisition, Plunge into Darkness, Simic Charm, Temur Charm, Vindictive Lich
- `rule:no-maximum-hand-size` (n=3): Mordenkainen Emblem, The Lux Foundation Library, The Vanquisher
- `rule:partner-with-tutor` (n=2): Khorvath Brightflame, Regna, the Redeemer
- `rule:pay-life-cost-for-effect` (n=4): Everythingamajig, Greed, Living Airship, Shessra, Death's Whisper
- `rule:plus1-counters-matter` (n=4): Craig Boone, Novac Guard, Herald of Secret Streams, Lux Artillery, Sapphire Drake
- `rule:populate-copy-creature-token` (n=2): Ghired, Conclave Exile, Mirror-Sigil Sergeant
- `rule:postcombat-main-phase-trigger` (n=2): Belbe, Corrupted Observer, Florian, Voldaren Scion
- `rule:power-scales-with-creature-count` (n=1): Silverwing Squadron
- `rule:prevent-all-combat-damage-this-turn` (n=2): Peel Out, Respite
- `rule:prevent-fixed-damage-any-target` (n=4): Acolyte's Reward, Heal, Kithkin Armor, Rakalite
- `rule:prevents-damage-prevention` (n=1): Insult // Injury
- `rule:prevents-damage-to-self` (n=2): Inviolability, Solitary Confinement
- `rule:prevents-regeneration` (n=5): Gravebind, Murderous Betrayal, Necrite, Nekrataal, Rage of Purphoros
- `rule:prevents-target-blocking` (n=1): Untimely Malfunction
- `rule:reanimate-from-graveyard` (n=4): Aerith, Last Ancient, Corpse Dance, Heroes of Kamigawa, Timely Hordemate
- `rule:redirect-targets-of-spell-or-ability` (n=3): Rebound, Ricochet Trap, Untimely Malfunction
- `rule:restricted-purpose-mana` (n=4): Herd Heirloom, Myr Reservoir, Nardole, Resourceful Cyborg, Stone Retrieval Unit
- `rule:restricts-blocking-to-flying-only` (n=1): Rishadan Brigand
- `rule:rhystic-tax` (n=3): Crush Dissent, Logic Knot, Stench of Evil
- `rule:sacrifice-for-creature-token` (n=1): Sultai Monument
- `rule:scales-mana-by-count` (n=1): Welcome to . . . // Jurassic Park
- `rule:scales-token-count-with-x` (n=1): Aggressive Biomancy
- `rule:self-bounce-activated` (n=1): Sliptide Serpent
- `rule:self-exile-after-resolution` (n=4): Divergent Equation, Reap the Past, Restock, Spelltwine
- `rule:self-recursion-from-graveyard` (n=4): Gutterbones, Razorlash Transmogrant, Retrofitted Transmogrant, The Falcon, Airship Restored
- `rule:sets-base-power-or-toughness` (n=5): Ascendant Spirit, Oko's Hospitality, Suit Up, Tezzeret the Schemer, Veiled Sentry
- `rule:skips-controller-draw-step` (n=1): Solitary Confinement
- `rule:stun-counter` (n=3): Event: Rat King's Revolution, Twisted Riddlekeeper, Vengeful Villagers
- `rule:targeted-bounce-creature` (n=5): Champion's Victory, Consuming Vortex, Depths of Desire, Otawara, Soaring City, Simic Charm
- `rule:targeted-creature-damage` (n=16): Arrows of Justice, Cindercone Smite, Command the Storm, Corrupt Eunuchs, Devour in Flames, Feed the Flames, Flame Slash, Hamato Ninpō, Helicarrier Strike, Insult // Injury, Last Kiss, Legolas, Master Archer, Puncture Bolt, Rage of Purphoros, Soul Shred, Swallowing Plague
- `rule:targeted-destruction` (n=27): Breathe Your Last, Cathar Commando, Dark Betrayal, Deadly Alliance, Destructive Revelry, Disenchant, Dwarven Landslide, Feed the Cycle, Heliod's Intervention, Icequake, Murderous Betrayal, Neck Snap, Nekrataal, Nissa's Defeat, Path of Peace, Primaris Eliminator, Puncturing Light, Sagittars' Volley, Seal of Primordium, Shoot the Sheriff, Sorin, Lord of Innistrad, Torch Fiend, Untimely Malfunction, Vengeance, Vengeant Vampire, Verdigris, Wild Swing
- `rule:targeted-discard` (n=3): Hollow Marauder, Mind Drain, Vindictive Lich
- `rule:targeted-exile` (n=5): Angel of Deliverance, Brittle Effigy, Buy Your Silence, Final Vengeance, Grip of Desolation
- `rule:targeted-planeswalker-damage` (n=5): Burning Fields, Chandra's Outburst, Devour in Flames, Emberwilde Augur, Insult // Injury (Injury face)
- `rule:targeted-player-damage` (n=6): Burning Fields, Chandra's Outburst, Concert Kaboomist, Emberwilde Augur, Insult // Injury, Morlun, Devourer of Spiders
- `rule:taxes-opponent-spell-cost` (n=1): Chill
- `rule:temporary-control-theft` (n=4): New Blood, Smelt-Ward Gatekeepers, The Nipton Lottery, Twisted Fealty
- `rule:temporary-keyword-grant` (n=5): Beetle, Legacy Criminal, Graviton, Fundamental Force, Rush of Vitality, Staggering Size, Venser, Corpse Puppet
- `rule:the-ring-tempts-you` (n=6): Birthday Escape, Glorious Gale, Gollum's Bite, Horses of the Bruinen, Ravenloft Adventurer, Took Reaper
- `rule:token-count-scales-with-graveyard-creature-count` (n=3): Hallowed Spiritkeeper, Revenge of the Rats, The Final Days
- `rule:token-count-scales-with-x` (n=3): Farmer Cotton, Path of the Ghosthunter, Forth Eorlingas!
- `rule:token-sacrifice-for-mana` (n=3): Brood Butcher, Glimpse the Impossible, Skittering Precursor
- `rule:tribal-anthem-buff` (n=10): Angel of Invention, Banner of Kinship, Chief of the Scale, Game Knights Live, Kargan Warleader, Lifecraft Engine, Quintorius, Field Historian, Stormscale Scion, Surprise Party, Undead Warchief
- `rule:triggers-on-cast-instant-sorcery` (n=3): Glacierwood Siege, Mica, Reader of Ruins, Rowan, Scholar of Sparks Emblem
- `rule:tutor-from-outside-game-to-hand` (n=2): Mastermind's Acquisition, Photo Op
- `rule:untaps-target-land` (n=1): Ley Weaver
- `rule:x-scales-with-permanent-count` (n=1): Khalni Hydra

---

## 15. D7 diagnosis: recently-killed appendix (2026-07-30)

**The appendix mechanism is built and correctly wired** — verified directly against the
actual API request payload sent for batch 6
(`experiments/out/foundry/stage1b_requests_batch6.json`): the system prompt's
`RECENTLY KILLED` block contains all 75 killed slugs verbatim, including both
`rule:equipment-grants-stat-buff` and `rule:equipment-static-pt-buff` — the exact two
strings SYNTH then re-proposed as lane=codebook matches for Rosethorn Halberd and Maul of
the Skyclaves. This is not a missing-plumbing bug; `load_recently_killed_reference()` ran
and its output reached the model.

**Root cause: model compliance, not wiring.** The batch-6 SYNTH call runs with
`"thinking": {"type": "disabled"}` — single-pass generation, no deliberation step. The
killed-slug list is a bare 75-item comma-separated string with no definitions or examples
attached (by design, to control prompt-growth cost — see the docstring in
`foundry_stage1b.py`). Cross-referencing a candidate label against a 75-item list is
exactly the kind of "read the whole list, then check" step that degrades without a
reasoning pass; the model appears to independently reconstruct the same natural vocabulary
for "equipment gives a static P/T buff" (a very obvious slug name) without reliably
checking it against the list before emitting it. This is now 3 batches running (killed
batch 3, resurrected batch 5 — which is why the appendix was built — resurrected again
batch 6 despite the appendix being present and correct).

**Fix implemented now (deterministic, not another prompt tweak):** added a third anomaly
category to `foundry_digest.py`'s `find_anomalies()` — any OTHER-lane row whose label
starts with `"rule:"` is flagged in the digest's Anomalies section (new
"OTHER-lane rows with an invalid 'rule:' prefix" subsection), since a genuine lane=free
label should never carry that prefix. This catches BOTH failure modes (killed-slug
resurrection and near-miss invented slugs like the Stone Retrieval Unit case) mechanically,
every batch, without depending on SYNTH prompt compliance or a reviewer noticing it by
manual grep — which is how all 3 of this batch's instances were actually found. Regenerated
digest-batch-6.md confirms it catches exactly the 3 known instances (Maul of the Skyclaves,
Rosethorn Halberd, Stone Retrieval Unit) and nothing else.

**Recommendation for batch 7+ (not implemented — a prompt/cost tradeoff for Captain, not a
unilateral call):** if this keeps recurring, consider enabling thinking for the SYNTH call
specifically when the killed-list check matters, or restructuring the prompt to require an
explicit "does this candidate label match anything in RECENTLY KILLED — yes/no" line before
the final answer. Both cost more tokens per card; given the digest-side catch now makes
this a zero-cost review-time flag rather than a silent miss, I'd defer that tradeoff to
Captain rather than spend batch-7 budget on it preemptively.

