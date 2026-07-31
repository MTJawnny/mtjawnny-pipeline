# TRIAGE — Batch 7 (SUP judgment pass)

Reviewed against `docs/SUP-TRIAGE-PROTOCOL.md`, `experiments/out/foundry/review/digest-batch-7.md`
(204 axes: 172 existing-codebook confirmations + 32 new candidates; 1373 OTHER-lane rows;
1366 token groups), and codebook v0.6 (271 active axes). Also cross-checked against
`docs/CORPUS-PASS-PLAN.md` and `docs/MASTER-HANDOFF-ADDENDUM-3.md`.

**Nothing in this document is load-bearing until Captain ratifies it.** Untouched entries
are ratified as proposed per the protocol's parsing convention — Captain annotates only
what needs to change, then runs `/triage-emit 7`.

## Methodology note on OTHER-lane coverage

Read all 172 existing-codebook confirmations, all 32 new candidates in full. For the
OTHER-lane (1366 token groups, noticeably richer/more diverse this batch than batch 6's —
top group here is n=66 vs. batch 6's n=70 but the whole upper tier runs much deeper),
read every group with n>=8 in full (roughly 105 groups), then spot-checked a further
sample scattered through n=7 down to n=2 (another ~40 groups) rather than the full n>=3
tier batch 5/6 achieved. This is a real, acknowledged reduction in coverage from the
batch-5/6 standard, made because the signal had already flatlined as hard as it did in
batch 6: every single group read, from the n=66 top group down through the n=2 sample,
was either (a) a thematically-related but mechanically-distinct incidental collision, or
(b) one of the two already-known "invalid rule: prefix" mislabels (see section 3). Zero
new coherent multi-card OTHER-lane families surfaced. Captain should treat groups below
n=8 that weren't in the sample as unread, not cleared.

---

## 1. Axis verdicts — existing codebook confirmations (172)

- `rule:activated-ability-costs-self-sacrifice` (scope=self, n=13) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:activated-destroy-target-land` (scope=opponent-stuff, n=5) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:activated-draw-a-card` (scope=self, n=5) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:activated-exile-graveyard-creature-card` (scope=opponent-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:activated-exile-graveyard-creature-for-token` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:activated-loot` (scope=self, n=7) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:activated-sacrifice-any-permanent-for-self-counter` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:activated-tap-or-untap-any-creature` (scope=any-creature, n=3) -- KEEP; member_removal(Unwilling Recruit) -- corpus-verified: "Gain control of target creature until end of turn. Untap that creature..." is a SPELL effect (no activation cost shown), and even setting that aside it only untaps, no tap-or-untap choice. Already correctly homed under rule:temporary-control-theft and rule:temporary-keyword-grant -- no rehome needed.
- `rule:activated-tap-or-untap-any-permanent` (scope=any-permanent, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:activated-tap-target-creature` (scope=opponent-stuff, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:activated-untap-target-creature` (scope=opponent-stuff, n=10) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:activation-restricted-only-during-your-turn` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:activation-restricted-to-sorcery-speed` (scope=self, n=15) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:additional-cost-discard-a-card` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:additional-cost-sacrifice-permanent` (scope=self, n=7) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:alternate-win-condition` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:animates-land-into-creature` (scope=your-stuff, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:attack-trigger-create-token` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:attack-trigger-pump-any-creature` (scope=any-creature, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:attack-trigger-pump-scaled-by-creature-count` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:attack-trigger-self-counter-growth` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:attack-trigger-untap-attacker` (scope=any-permanent, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:aura-locks-enchanted-creature-tapped` (scope=opponent-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:burst-draw` (scope=self, n=7) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:cannot-block-restriction` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:cant-be-countered` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:cantrip` (scope=self, n=6) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:cast-from-top-of-library` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:cast-trigger-card-draw` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:changes-color-creature` (scope=any-creature, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:charge-counter-accumulation` (scope=self, n=9) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:cheat-creature-into-play` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:choose-color-on-etb` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:choose-creature-type-on-etb` (scope=self, n=6) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:combat-damage-to-creature-triggers-self-counter` (scope=self, n=2) -- KEEP; definition_edit -- both members (Guild Thief, Stromkirk Patrol) read "Whenever this creature deals combat damage to a PLAYER, put a +1/+1 counter on it" (corpus-verified), directly contradicting the axis's own "deals damage to a creature" definition. 2 of 2 members agree on the real pattern; the definition text was wrong at authoring time, not the membership. Corrected definition: "Whenever this creature deals combat damage to a player, it grows itself by adding a +1/+1 counter to itself."
VERDICT: Rename to `rule:combat-damage-to-player-triggers-self-counter`
- `rule:combat-damage-to-player-draws-card` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:combat-damage-triggers-discard` (scope=opponent-stuff, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:combat-damage-triggers-loot` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:combat-trick-pump-own-creature` (scope=self, n=18) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:compensates-controller-with-token` (scope=opponent-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:conditional-buff-by-color` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:copies-cast-spell` (scope=self, n=5) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:copy-creature-token` (scope=any-creature, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:cost-reduction` (scope=self, n=5) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:counter-removal-as-activation-cost` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:counters-noncreature-spell` (scope=opponent-stuff, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:counters-target-spell` (scope=opponent-stuff, n=6) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:create-token-creature` (scope=your-stuff, n=22) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:create-token-mana-producing-artifact` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:create-token-treasure` (scope=self, n=6) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:created-token-enters-tapped` (scope=self, n=9) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:creates-token-with-x-scaled-counters` (scope=self, n=2) -- KEEP; member_removal(Gnarlid Pack) -- corpus-verified: "This creature enters with a +1/+1 counter on it for each time it was kicked" creates no token at all. Proposed member_addition(Gnarlid Pack) to rule:kicker-conditional-bonus-effect instead (multikicker-scaled ETB bonus is exactly that axis's pattern). Fractal Summoning remains the axis's sole genuine member.
VERDICT: This rule continuously has this issue. Is there something we should do or rename to avoid possible corpus wide confusion?
- `rule:damage-divided-among-multiple-targets` (scope=opponent-stuff, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:damage-scales-with-creature-count` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:death-trigger-counter-transfer` (scope=your-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:death-trigger-token-creation` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:direct-damage-any-target` (scope=opponent-stuff, n=18) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:drain-life` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:drain-on-creature-death` (scope=opponent-stuff, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:draw-cards-with-life-loss-cost` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:draw-scaled-by-creature-count` (scope=self, n=1) -- KEEP; member_removal(Promise of Power) -- corpus-verified full text is modal ("Choose one -- draw 5/lose 5 OR create an X/X Demon token, where X is the number of cards in your HAND"): wrong topic (token, not draw) and wrong scaling stat (hand size, not creature count). Already correctly homed under rule:modal. Axis now has 0 members this batch (carries forward from prior-batch membership in codebook.json).
- `rule:draw-trigger-self-counter-growth` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:enters-tapped` (scope=self, n=24) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:enters-tapped-conditional` (scope=self, n=5) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:equipment-etb-creates-and-attaches-token` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-and-attack-trigger` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-auto-attach-to-own-creature` (scope=your-stuff, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-bounce-other-creature` (scope=opponent-stuff, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-counter-on-other-creature` (scope=self, n=7) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-create-token` (scope=self, n=5) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-create-token-creature` (scope=self, n=15) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-create-token-creature-conditional` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-create-token-food` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-draw-card` (scope=self, n=6) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-exile-graveyard-card` (scope=opponent-stuff, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-gain-life` (scope=self, n=10) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-loot` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-mass-pump-your-creatures` (scope=your-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-modal-choice` (scope=self, n=5) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-pump-target-creature` (scope=any-creature, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-scry` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-self-bounce-own-permanent` (scope=your-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-tutor-to-hand` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-with-counters` (scope=self, n=10) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:etb-with-negative-counters` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:evasion-vs-high-power-blockers` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:exile-until-source-leaves` (scope=opponent-stuff, n=6) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:fixed-lifegain` (scope=self, n=9) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:forced-attack-each-combat` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:forced-hand-reveal` (scope=opponent-stuff, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:forces-creature-to-attack` (scope=opponent-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:free-cast` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:free-sacrifice-outlet` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:gives-energy-counters-immediately` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:grants-ability-at-threshold-board` (scope=your-stuff, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:grants-ability-at-threshold-self` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:grants-additional-combat-phase` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:grants-controller-hexproof` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:grants-creature-type` (scope=your-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:grants-double-strike-target` (scope=your-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:grants-extra-land-drop` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:grants-haste-to-your-creatures` (scope=your-stuff, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:grants-unblockable` (scope=your-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:grants-unblockable-target` (scope=any-creature, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:graveyard-to-exile-replacement` (scope=all-players, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:graveyard-to-hand-recursion` (scope=self, n=6) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:graveyard-to-library-top-recursion` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:innate-unblockable` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:kicker-conditional-bonus-effect` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:land-fetch-to-battlefield` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:leaves-battlefield-trigger-create-token-mutagen` (scope=self, n=2) -- KEEP; member_removal(Brandywine Farmer) -- corpus-verified: "When this creature enters or leaves the battlefield, create a Food token" creates a Food token, not Mutagen. Already correctly homed under rule:etb-create-token-food -- no rehome needed (the LTB-triggers-Food-token facet has no sibling axis yet; a rule:leaves-battlefield-trigger-create-token-food child would mirror this batch's own -mutagen precedent -- flagged to PARENT-TREE-CANDIDATES.md). Splinter, the Mentor remains the axis's sole genuine member.
- `rule:level-up-scaling-stats-abilities` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:library-dig-put-onto-battlefield` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:library-dig-to-hand` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:library-top-visibility` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:life-total-reset` (scope=all-players, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mana-activated-pump-self` (scope=self, n=8) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mass-counter-distribution` (scope=your-stuff, n=8) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mass-creature-destruction` (scope=all-players, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mass-damage-creatures-and-players` (scope=all-players, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mass-damage-opponent-creatures-only` (scope=opponent-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mass-debuff-opponent-creatures` (scope=opponent-stuff, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mass-graveyard-exile` (scope=all-players, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mass-pump-your-creatures` (scope=your-stuff, n=6) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mass-untap-and-haste-stolen-creatures` (scope=all-players, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mass-untap-your-creatures` (scope=your-stuff, n=5) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:mill-self-cards` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:modal` (scope=self, n=25) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:no-maximum-hand-size` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:partner-with-tutor` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:pay-life-cost-for-effect` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:plus1-counters-matter` (scope=self, n=6) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:power-scales-with-creature-count` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:prevent-all-combat-damage-this-turn` (scope=all-players, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:prevent-damage-to-your-creatures` (scope=your-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:prevent-fixed-damage-any-target` (scope=all-players, n=7) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:prevents-regeneration` (scope=opponent-stuff, n=6) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:reanimate-from-graveyard` (scope=your-stuff, n=9) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:redirect-targets-of-spell-or-ability` (scope=opponent-stuff, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:restricted-purpose-mana` (scope=self, n=7) -- KEEP; member_removal(Forsaken Crossroads) -- corpus-verified full text has no spend restriction on its mana ability ("{T}: Add one mana of the chosen color", no "spend this mana only to..." clause). No existing axis fits its actual pattern (conditional-color land with ETB choose-color + scry); ledger-flagged, no forced rehome.
- `rule:rhystic-tax` (scope=opponent-stuff, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:sacrifice-for-card-draw` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:sacrifice-for-creature-token` (scope=self, n=2) -- KEEP; member_removal(Ob Nixilis, the Adversary) -- corpus-verified: this is a PLANESWALKER: the token comes from a loyalty ability ("-2: Create a 1/1 red Devil..."), not an activated ability that sacrifices the source permanent. No existing axis captures "planeswalker loyalty ability creates a token"; ledger-flagged, no forced rehome. Idol of Oblivion remains the axis's sole genuine member.
- `rule:scales-mana-by-count` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:scales-token-count-with-x` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:self-bounce-activated` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:self-counter-growth` (scope=self, n=4) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:self-exile-after-resolution` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:self-mana-ability-grants-keyword` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:self-recursion-from-graveyard` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:sets-base-power-or-toughness` (scope=any-creature, n=5) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:stun-counter` (scope=opponent-stuff, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:targeted-bounce-creature` (scope=opponent-stuff, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:targeted-creature-damage` (scope=opponent-stuff, n=15) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:targeted-destruction` (scope=opponent-stuff, n=21) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:targeted-discard` (scope=all-players, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:targeted-exile` (scope=any-permanent, n=7) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:targeted-planeswalker-damage` (scope=opponent-stuff, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:targeted-player-damage` (scope=opponent-stuff, n=10) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:taxes-opponent-spell-cost` (scope=opponent-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:temporary-control-theft` (scope=opponent-stuff, n=12) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:temporary-keyword-grant` (scope=your-stuff, n=13) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:the-ring-tempts-you` (scope=self, n=3) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:token-sacrifice-for-mana` (scope=your-stuff, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:transforms-on-graveyard-threshold` (scope=self, n=2) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:tribal-anthem-buff` (scope=your-stuff, n=14) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:triggers-on-cast-instant-sorcery` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:tutor-basic-land-to-hand` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:tutor-from-outside-game-to-hand` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:tutor-to-library-top` (scope=self, n=1) -- KEEP; member_removal(Library of Lat-Nam) -- corpus-verified: fully modal ("An opponent chooses one -- delayed draw-3 OR search library, put into HAND"), neither mode puts a card on top of the library. No existing axis cleanly fits (not an ETB trigger, so rule:etb-tutor-to-hand doesn't apply); ledger-flagged, no forced rehome. Axis now has 0 members this batch (carries forward from prior-batch membership in codebook.json).
- `rule:untaps-target-land` (scope=your-stuff, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.
- `rule:x-scales-with-permanent-count` (scope=self, n=1) -- KEEP -- reconfirmed; this batch surfaced no new evidence against it.

## 2. Axis verdicts — new candidates (32)

- `rule:attack-trigger-damage-defender` (scope=opponent-stuff, n=3) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
VERDICT: Great Rule, Let's rename to `rule:attack-trigger-damage-defending-player`. I know it's longer. But defender is a keyword and we want to avoid confusion. Also Parent Proposal `rule:defending-player`
- `rule:channel-discard-for-effect` (scope=self, n=3) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:grants-trample-to-countered-creatures` (scope=your-stuff, n=3) -- RENAME to rule:grants-trample-to-creatures-with-counters -- all 3 members (Nev the Practical Dean, Sunbringer's Touch, The Crowd Goes Wild) correctly match the axis's own definition (creatures WITH a +1/+1 counter gain trample); the slug itself is the problem -- "countered creatures" reads as "creatures whose SPELL was Countered" in standard MTG parlance, the opposite of what this axis means. Naming-clarity fix only, per the agent-legibility standard (CORPUS-PASS-PLAN.md section 4).
VERDICT: sounds good. rename.
- `rule:activated-cost-discard-a-card` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:activated-grants-haste-other-creature` (scope=any-creature, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:activated-mill-target-player` (scope=opponent-stuff, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:activated-tax-counter-unless-pays` (scope=opponent-stuff, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:cast-trigger-self-counter-noncreature-spell` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:combat-damage-triggers-proliferate` (scope=all-players, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:combat-damage-triggers-treasure` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:conditional-attack-restriction-by-defender-land-type` (scope=opponent-stuff, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
VERDICT: Good Rule. RENAME to `rule:conditional-attack-restriction-by-defending-player-land-type`. annoying but needed distinction.
- `rule:cost-reduction-scaled-by-attackers` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:cost-reduction-scaled-by-legendary-creature-count` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:counters-spell-or-ability-targeting-your-permanent` (scope=your-stuff, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:death-trigger-card-draw` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:etb-bounce-own-land` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:etb-copy-your-permanent` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:etb-creature-triggers-surveil` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:etb-tap-and-stun-target` (scope=opponent-stuff, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:etb-tutor-specific-named-card-to-hand` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:flashback-recast-from-graveyard` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:forces-all-creatures-attack` (scope=all-players, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:grants-cascade-to-own-spells` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:grants-ward-to-other-creatures` (scope=your-stuff, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:mass-damage-flying-creatures-scaled-by-x` (scope=all-players, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:pump-scaled-by-own-creature-count` (scope=your-stuff, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:pump-two-target-creatures` (scope=any-stuff, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:reveal-hand-then-choose-discard` (scope=opponent-stuff, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:sacrifice-creature-for-self-pump` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:self-sacrifice-on-land-type-absence` (scope=self, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:tax-or-counter-spell` (scope=opponent-stuff, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.
- `rule:token-sacrifice-for-colorless-mana` (scope=your-stuff, n=2) -- KEEP -- genuine narrow SYNTH-derived pattern, evidence-quote-backed, no duplicate or contradiction found against codebook v0.6.

---

## 3. QUESTIONS (0 of max 8)

None this batch. Every issue found during the read resolved to a confident call once
checked against live corpus text — no genuine either/or needed Captain's judgment this
time. (Contrast batch 6's 2 QUESTIONS on scope/definition wording; this batch's problems
were more numerous but all cleanly resolvable with evidence rather than requiring a
policy call.)

---

## 4. OTHER-lane promotions and corrections

No new coherent multi-card families promoted this batch (see the methodology note above).
One correction folded into the axis verdicts in section 1 rather than listed separately:

- **`rule:leaves-battlefield-trigger-create-token-mutagen` loses a member**
  (Brandywine Farmer — see its verdict line above). Reached the same way as three of
  batch 6's findings: a mislabeled/miscategorized member surfaced during the primary
  axis read, not a genuinely novel OTHER-lane family.

Two "invalid `rule:` prefix" OTHER-lane rows were caught automatically by the digest-side
detector added in batch 6 (D7) — see section 5 below; this is exactly the deterministic
catch that fix was built for, now proven across a second batch.

---

## 5. `rule:` prefix anomaly follow-up (batch-6 D7 mechanism, still working)

The digest's automatic anomaly detector (added batch 6, `foundry_digest.py`'s
`find_anomalies()`) flagged 4 OTHER-lane rows with an invalid `rule:` prefix this batch:

- **Sword of Truth and Justice: `rule:equipment-static-pt-buff`** — the SAME killed axis
  (batch 3) that resurfaced twice in batch 6 despite the recently-killed appendix listing
  it verbatim. This is now the 4th consecutive batch. Not re-diagnosing the mechanism here
  (batch 6's D7 finding — correctly wired, ignored by SYNTH under disabled-thinking
  generation — still stands); flagging the recurrence count for Captain, since "fix before
  batch 7 if it recurs a 4th time" was explicitly punch-listed in batch 6.
- **The Cloning of Shredder: `rule:saga-chapter-progression`** — does not exist in the
  codebook (v0.5 or v0.6); a near-miss invented slug, not a killed-axis resurrection.
- **Morbid Bloom: `rule:etb-exile-graveyard-creature-card`** — near-miss invented slug;
  the real axis is `rule:activated-exile-graveyard-creature-card` (this card's actual
  ability is activated, not ETB-triggered, per its corpus text — so this may also be a
  genuine ability-type mismatch beyond just the naming near-miss; not independently
  re-verified this batch since it's already correctly excluded from any real axis by
  virtue of the label matching nothing).
- **Fifty Feet of Rope: `rule:venture-into-dungeon`** — near-miss invented slug; no
  matching codebook axis exists (venture-into-dungeon is a keyword mechanism that would
  fall under the engine's keyword layer per the "bare keyword mechanism -> ledger, not an
  axis" standing rule, not a SYNTH-authored axis at all).

None of these four require action beyond what the detector already provides (visibility);
none are promotable (all either killed, generic/rejected, or keyword-mechanism-owned).

---

## 6. Override sample (30 rows, seed=20260725, confident calls only)

Drawn uniformly at random (Python `random.Random(20260725).sample`) from all 779 member
rows across all 204 axes (no QUESTIONS axes to exclude this batch). Every quote checked
against the digest transcription; spot-verified 26 of the 30 against full corpus oracle
text directly via `foundry_common.full_oracle_text()` (the remaining 4 are the trivially
self-evident "This land enters tapped." rows). One of the 30 sampled rows
(Brandywine Farmer) is the already-known `rule:leaves-battlefield-trigger-create-token-mutagen`
mismatch from section 1 — the sample re-surfaced it rather than missing it, which is the
result you want from a spot-check.

| Axis | Card | Quote (as transcribed) | Check |
|---|---|---|---|
| rule:activated-ability-costs-self-sacrifice | Knights' Charge | "Sacrifice this enchantment: Return all Knight creature cards from your graveyar…" | OK |
| rule:activation-restricted-to-sorcery-speed | Fifty Feet of Rope | "Activate only as a sorcery." | OK |
| rule:activation-restricted-to-sorcery-speed | Geth, Thane of Contracts | "Activate only as a sorcery." | OK |
| rule:additional-cost-sacrifice-permanent | Eviscerator's Insight | "As an additional cost to cast this spell, sacrifice an artifact or creature." | OK |
| rule:attack-trigger-damage-defender | Swathcutter Giant | "Whenever this creature attacks, it deals 1 damage to each creature defending pl…" | OK |
| rule:choose-creature-type-on-etb | Rimefire Torque | "As this artifact enters, choose a creature type." | OK |
| rule:combat-trick-pump-own-creature | Battle Menu | "Target creature gets +0/+4 until end of turn." | OK |
| rule:counter-removal-as-activation-cost | Staff of the Storyteller | "{W}, {T}, Remove a story counter from this artifact: Draw a card." | OK |
| rule:create-token-creature | Predator's Howl | "Create a 2/2 green Wolf creature token." | OK |
| rule:damage-scales-with-creature-count | Ajani, Nacatl Pariah // Ajani, Nacatl Avenger | "he deals damage equal to the number of creatures you control to any target" | OK |
| rule:draw-cards-with-life-loss-cost | Coercive Impetus | "Whenever enchanted creature attacks, you draw a card and lose 1 life." | OK |
| rule:enters-tapped | Blackbloom Rogue // Blackbloom Bog | "This land enters tapped." | OK |
| rule:enters-tapped | Coastal Tower | "This land enters tapped." | OK |
| rule:enters-tapped | Golgari Rot Farm | "This land enters tapped." | OK |
| rule:etb-counter-on-other-creature | Knight of Autumn | "Put two +1/+1 counters on this creature." | OK |
| rule:etb-create-token-creature | Nest Invader | "When this creature enters, create a 0/1 colorless Eldrazi Spawn creature token." | OK |
| rule:fixed-lifegain | Tandem Tactics | "You gain 2 life." | OK |
| rule:forces-all-creatures-attack | Warmonger Hellkite | "All creatures attack each combat if able." | OK |
| rule:leaves-battlefield-trigger-create-token-mutagen | Brandywine Farmer | "When this creature enters or leaves the battlefield, create a Food token." | **MISMATCH — see section 1's member_removal(Brandywine Farmer); creates a Food token, not Mutagen (corpus-verified)** |
| rule:mass-graveyard-exile | Decompose | "Exile up to three target cards from a single graveyard." | OK |
| rule:mass-pump-your-creatures | Three Blind Mice | "IV — Creatures you control get +1/+1 and gain vigilance until end of turn." | OK |
| rule:redirect-targets-of-spell-or-ability | Boltbender | "When this creature is turned face up, you may choose new targets for any number…" | OK |
| rule:rhystic-tax | Quench | "Counter target spell unless its controller pays {2}." | OK |
| rule:scales-mana-by-count | Prismatic Geoscope | "Domain — {T}: Add X mana in any combination of colors, where X is the number of…" | OK |
| rule:targeted-creature-damage | Combustion Technique | "Combustion Technique deals damage equal to 2 plus the number of Lesson cards in…" | OK |
| rule:targeted-discard | Chain of Smog | "Target player discards two cards." | OK |
| rule:targeted-exile | Hurl Through Hell | "Exile target creature." | OK |
| rule:targeted-planeswalker-damage | Shower of Sparks | "1 damage to target player or planeswalker" | OK |
| rule:temporary-keyword-grant | Eidolon of Astral Winds | "Until end of turn, that creature has base power and toughness 4/4 and gains fly…" | OK |
| rule:tribal-anthem-buff | Child of the Pack // Savage Packmate | "Other creatures you control get +1/+0." | OK |

**29 of 30 confirmed clean; 1 of 30 (Brandywine Farmer) re-surfaced an already-known
mismatch** — no new finding from the sample this batch, but a clean validation that the
sampling process and the primary read agree.

---

## 7. Full member-correction summary (for /triage-emit 7's reconcile step)

member_removals:
- `rule:activated-tap-or-untap-any-creature` — Unwilling Recruit
- `rule:combat-damage-to-creature-triggers-self-counter` — none (definition_edit instead, see below)
- `rule:creates-token-with-x-scaled-counters` — Gnarlid Pack
- `rule:leaves-battlefield-trigger-create-token-mutagen` — Brandywine Farmer
- `rule:draw-scaled-by-creature-count` — Promise of Power
- `rule:restricted-purpose-mana` — Forsaken Crossroads
- `rule:sacrifice-for-creature-token` — Ob Nixilis, the Adversary
- `rule:tutor-to-library-top` — Library of Lat-Nam

member_additions:
- `rule:kicker-conditional-bonus-effect` — Gnarlid Pack (rehomed from
  creates-token-with-x-scaled-counters; multikicker-scaled ETB bonus matches this axis's
  pattern exactly).

definition_edits:
- `rule:combat-damage-to-creature-triggers-self-counter` — corrected from "deals damage to
  a creature" to "deals combat damage to a player" (both of the axis's 2 members
  corpus-verified to say "player," never "creature"; the original definition text was
  wrong at authoring time).

renames:
- `rule:grants-trample-to-countered-creatures` -> `rule:grants-trample-to-creatures-with-counters`
  (naming-clarity fix; "countered creatures" reads as "creatures whose spell was
  Countered" in standard MTG terminology, the opposite of this axis's actual meaning —
  creatures that have a +1/+1 counter on them). All 3 members correctly match the intended
  definition; only the slug was wrong.

No KILLs, no MERGEs this batch. This is the second consecutive batch with zero axis-level
churn — batch 6's finding that the SYNTH prompt has matured past axis-level problems into
purely member-level ones continues to hold, though this batch found MORE member-level
issues (8 removals + 1 rename) than batch 6 did (7 removals), all independently
corpus-verified rather than assumed from the digest's truncated quotes.

---

## 8. Batch-feedback for the batch-8 SYNTH prompt

1. **Ability-type-vs-trigger-type still slipping through on ETB-modal and ETB-loot-shaped
   axes (new pattern this batch, related to but distinct from batch-4's activated-vs-triggered
   finding).** `rule:tutor-to-library-top` and `rule:sacrifice-for-creature-token` both
   picked up members whose actual mechanism is a completely different structure than the
   axis names (a fully modal spell mistaken for "puts on top of library"; a planeswalker
   loyalty ability mistaken for "sacrifice the source, an activated ability"). Add a prompt
   rule: before assigning ANY axis, re-confirm the card's ability STRUCTURE (modal spell /
   ETB trigger / activated ability / loyalty ability / static) actually matches what the
   axis definition presupposes, not just that the effect words overlap.
2. **Scaling-stat precision (recurring from batch 6, still not fully fixed).**
   `rule:draw-scaled-by-creature-count` picked up a card whose X is scaled by HAND SIZE,
   not creature count — the same class of error as batch 6's charge-counter-vs-creature-count
   confusion, just a different wrong stat. Strengthen the batch-6 prompt addition (already
   in the system prompt) to explicitly list common scaling stats that get confused with
   each other: creature count, hand size, counters-on-source, graveyard size, mana value —
   confirm the EXACT noun phrase in the quote before matching a "-scaled-by-X" axis.
3. **Definition-text quality control needed at authoring time, not just member-verification
   time.** `rule:combat-damage-to-creature-triggers-self-counter` had a definition that
   contradicted 2 of 2 of its own members from the moment it was authored (prior batch) —
   this isn't a SYNTH labeling error, it's an axis-authoring error that nothing in the
   current pipeline catches until a SUP full-pass reads every member against the
   definition. Not a SYNTH-prompt fix; flagging for the naming-audit item in
   `docs/CORPUS-PASS-PLAN.md` section 3 (per-axis walk) instead.
4. **Naming-clarity misses that don't affect membership correctness are still worth
   catching.** `rule:grants-trample-to-countered-creatures`'s slug was actively misleading
   (reads as spell-countering, means +1/+1-counter-having) despite every member being
   correctly assigned. Add a prompt self-check for free-lane label proposals: does this
   slug, read cold by someone who knows Magic terminology but not this card, suggest the
   RIGHT mechanic? "Countered" is a specific, loaded MTG term (Counterspell) distinct from
   "has a counter" — avoid the bare word "counter/countered" without disambiguating
   "counter (object)" from "counter (verb, negate a spell)" in any proposed slug.
5. **The `rule:` prefix / recently-killed-appendix problem is unchanged from batch 6 (see
   section 5) — 4th consecutive batch for `rule:equipment-static-pt-buff` specifically.**
   Per batch 6's own punch list ("consider enabling thinking for the SYNTH call if this
   recurs a 4th time") — it has now recurred a 4th time. Recommending Captain consider that
   tradeoff for batch 8, rather than deferring again; the digest-side catch (section 5)
   keeps this from being a silent failure, but it's real wasted SYNTH spend every batch
   it recurs.

---

## 9. Parent flags

Appended to `mtjawnny.github.io/docs/PARENT-TREE-CANDIDATES.md` under "Proposed parents"
(batch-7 subsection): a `rule:leaves-battlefield-trigger-create-token-food` sibling flag
(mirrors the batch-6 `-mutagen` precedent, needed for Brandywine Farmer's LTB-Food-token
facet, which currently has no home), and a note on the `rule:etb-modal-choice` /
"fully-modal-but-mislabeled-as-ETB" boundary surfaced by the Analyze the Pollen /
Library of Lat-Nam class of misses this batch (worth a schema-pass check: how many
existing ETB-flavored axes have non-ETB modal spells miscategorized into them).

---

## 10. Verification

- Verdict count: 172 (existing) + 32 (new) = 204, matches the digest's stated axis count. ✓
- No duplicate axis entries. ✓
- Every MERGE target named: N/A this batch (zero MERGEs). Every RENAME target named: ✓
  (1 rename, target given). ✓
- Every member_removal / member_addition names an exact card. ✓
- QUESTIONS: 0, under the max-8 cap. ✓
- MEMBER ROSTER: present below, covers all 204 axes. ✓

**Batch 7 review complete.** File: `docs/TRIAGE-BATCH-7.md`. Captain: annotate per the
protocol convention (untouched entries ratify as proposed), then run `/triage-emit 7`.

---

## 11. MEMBER ROSTER — batch-7 contribution, post-corrections (D6, mandatory)

Names only, no oracle text, per D6. Covers all 204 axes (172 existing confirmations + 32
new candidates, with the 1 rename already reflected under its new slug). This is batch 7's
OWN confirmation/new-candidate contribution after applying every correction in sections 1-2
above — not each axis's total cumulative codebook membership (a "(none)" row below means
this batch's own example(s) got removed, not that the axis is empty in the codebook —
checked directly: rule:draw-scaled-by-creature-count retains 3 prior-batch members,
rule:tutor-to-library-top retains 9).

- `rule:activated-ability-costs-self-sacrifice` (n=13): Aang's Iceberg, Acidic Sliver, Candlestick, Coin of Fate, Dark Sphere, Fugitive Droid, Gaea's Touch, Guac & Marshmallow Pizza, Knights' Charge, Lodestone Bauble, Meditation Pools, Serra's Liturgy, Warped Landscape
- `rule:activated-cost-discard-a-card` (n=2): Avenger en-Dal, Charm Peddler
- `rule:activated-destroy-target-land` (n=5): Gate to Phyrexia, Pooling Venom, Rubble Reading, Seismic Spike, Steam Vines
- `rule:activated-draw-a-card` (n=5): Candlestick, Katara, Bending Prodigy, Meditation Pools, Staff of the Storyteller, Towashi Guide-Bot
- `rule:activated-exile-graveyard-creature-card` (n=1): Dino DNA
- `rule:activated-exile-graveyard-creature-for-token` (n=1): Graveyard Marshal
- `rule:activated-grants-haste-other-creature` (n=2): Boros Guildmage, Paragon of Fierce Defiance
- `rule:activated-loot` (n=7): Anje Falkenrath, Farid, Enterprising Salvager, Geyser Leaper, Ghastly Discovery, Obelisk of Alara, Seeker of Insight, Teferi's Protege
- `rule:activated-mill-target-player` (n=2): Decimator Web, Millstone
- `rule:activated-sacrifice-any-permanent-for-self-counter` (n=3): Kalitas, Traitor of Ghet, Krav, the Unredeemed, Phantom Train
- `rule:activated-tap-or-untap-any-creature` (n=2): Puppeteer, Stonybrook Angler
- `rule:activated-tap-or-untap-any-permanent` (n=1): Captain of the Mists
- `rule:activated-tap-target-creature` (n=3): Goldmeadow Harrier, Inquisitor Greyfax, Octopus Umbra
- `rule:activated-tax-counter-unless-pays` (n=2): Ghost-Lit Warder, Thrull Wizard
- `rule:activated-untap-target-creature` (n=10): Act of Heroism, Awaken the Sleeper, Ebony Horse, Fleeting Reflection, Fyndhorn Brownie, Sauron, the Lidless Eye, Seeker of Skybreak, Spinal Embrace, Witch's Web, Wrangle
- `rule:activation-restricted-only-during-your-turn` (n=1): Eladamri, Korvecdal
- `rule:activation-restricted-to-sorcery-speed` (n=15): Assassin Den, Bound by Moonsilver, Codsworth, Handy Helper, Dino DNA, Dread Wanderer, Eyes Everywhere, Fabrication Foundry, Fifty Feet of Rope, Gaea's Touch, Geth, Thane of Contracts, Grinning Ignus, Kjeldoran Elite Guard, Lodestone Needle // Guidestone Compass, Sagu Pummeler, Veko, Death's Doorkeeper
- `rule:additional-cost-discard-a-card` (n=1): Restless Dreams
- `rule:additional-cost-sacrifice-permanent` (n=7): A-Splitting the Powerstone, Crop Rotation, Eviscerator's Insight, Ritual of the Machine, Stomped by the Foot, Tormented Thoughts, Wickerfolk Indomitable
- `rule:alternate-win-condition` (n=2): Call the Spirit Dragons, Throne of the High City
- `rule:animates-land-into-creature` (n=2): Avalanche Caller, Great Hall of the Biblioplex
- `rule:attack-trigger-create-token` (n=1): Rufus Shinra
- `rule:attack-trigger-damage-defender` (n=3): Purifying Dragon, Scorch Spitter, Swathcutter Giant
- `rule:attack-trigger-pump-any-creature` (n=1): Gravity Negator
- `rule:attack-trigger-pump-scaled-by-creature-count` (n=1): Akroan Hoplite
- `rule:attack-trigger-self-counter-growth` (n=1): Hercules, Olympian Hero
- `rule:attack-trigger-untap-attacker` (n=1): Genji Glove
- `rule:aura-locks-enchanted-creature-tapped` (n=1): Blossombind
- `rule:burst-draw` (n=7): Brilliant Spectrum, Combat Tutorial, Eviscerator's Insight, Lessons from Life, Meditate, Meeting of Minds, Rowdy Research
- `rule:cannot-block-restriction` (n=4): A-Cauldron Familiar, Hulking Cyclops, Hulking Ogre, Maniacal Rage
- `rule:cant-be-countered` (n=4): Carnage Tyrant, Frenzied Baloth, Great Sable Stag, Toski, Bearer of Secrets
- `rule:cantrip` (n=6): A-Splitting the Powerstone, Cremate, Due Respect, Johann's Stopgap, Mind Transfer Protocol, Urza's Command
- `rule:cast-from-top-of-library` (n=1): Eladamri, Korvecdal
- `rule:cast-trigger-card-draw` (n=2): Chulane, Teller of Tales, Valeria Richards, Precocious
- `rule:cast-trigger-self-counter-noncreature-spell` (n=2): Boar-q-pine, Levitating Statue
- `rule:changes-color-creature` (n=1): Touch of Darkness
- `rule:channel-discard-for-effect` (n=3): Eiganjo, Seat of the Empire, Ghost-Lit Warder, Takenuma, Abandoned Mire
- `rule:charge-counter-accumulation` (n=9): Ashling the Pilgrim, Chlorophant, Edifice of Authority, Primal Amulet // Primal Wellspring, Rimefire Torque, Saltcrusted Steppe, Serra's Liturgy, Volcanic Villain, Yisan, the Wanderer Bard
- `rule:cheat-creature-into-play` (n=1): Industrial Advancement
- `rule:choose-color-on-etb` (n=2): Crossroads Village, Forsaken Crossroads
- `rule:choose-creature-type-on-etb` (n=6): Bloodline Pretender, Collective Inferno, Eclipsed Realms, Metamorphic Alteration, Radiant Destiny, Rimefire Torque
- `rule:combat-damage-to-creature-triggers-self-counter` (n=2): Guild Thief, Stromkirk Patrol
- `rule:combat-damage-to-player-draws-card` (n=3): Conclave Evangelist, Mask of Riddles, Toski, Bearer of Secrets
- `rule:combat-damage-triggers-discard` (n=2): Blizzard Specter, Sedraxis Specter
- `rule:combat-damage-triggers-loot` (n=1): Assassin Gauntlet
- `rule:combat-damage-triggers-proliferate` (n=2): Guildpact Informant, Vexing Radgull
- `rule:combat-damage-triggers-treasure` (n=2): Hoard Robber, Kamachal, Ship's Mascot
- `rule:combat-trick-pump-own-creature` (n=18): Act of Heroism, Battle Menu, Brute Strength, Built to Last, Devouring Rage, Enlarge, Enrage, Huatli's Final Strike, Kird Chieftain, Obelisk of Alara, Rabid Gnaw, Seeds of Strength, Show of Valor, Sugar Rush, Sunscape Apprentice, Swift Kick, Terrific Team-Up, You Come to the Gnoll Camp
- `rule:compensates-controller-with-token` (n=1): Introduction to Annihilation
- `rule:conditional-attack-restriction-by-defender-land-type` (n=2): Island Fish Jasconius, Manta Ray
- `rule:conditional-buff-by-color` (n=2): Etali's Favor, Tezzeret's Strider
- `rule:copies-cast-spell` (n=5): Ancestral Communion, Finale of Promise, Geistblast, Insidious Will, Reflective Golem
- `rule:copy-creature-token` (n=1): Irenicus's Vile Duplication
- `rule:cost-reduction` (n=5): Prehistoric Turtlesaurus, Primal Amulet // Primal Wellspring, Stratadon, The Immortal Sun, Valeria Richards, Precocious
- `rule:cost-reduction-scaled-by-attackers` (n=2): Ancient Stone Idol, Rowdy Research
- `rule:cost-reduction-scaled-by-legendary-creature-count` (n=2): Eiganjo, Seat of the Empire, Takenuma, Abandoned Mire
- `rule:counter-removal-as-activation-cost` (n=3): Golem Foundry, Rimefire Torque, Staff of the Storyteller
- `rule:counters-noncreature-spell` (n=3): Stubborn Denial, Unwind, Weave the Nightmare
- `rule:counters-spell-or-ability-targeting-your-permanent` (n=2): Fugitive Droid, Not of This World
- `rule:counters-target-spell` (n=6): Broken Concentration, Change the Equation, Fold into Aether, Insidious Will, Lapse of Certainty, Rewind
- `rule:create-token-creature` (n=22): Battle Menu, Born to Drive, Defend the Rider, Eldrazi Confluence, Feast or Famine, Frontline Rush, Golem Foundry, Growth Spasm, Hive Stirrings, Kayla's Command, Leyline Invocation, Lingering Souls, Lost in the Spirit World, Metrognome, Moonstone Eulogist, Predator's Howl, Retrieve the Esper, Riku of Many Paths, Skittering Invasion, Splicer's Skill, Summon the School, Vivi's Persistence
- `rule:create-token-mana-producing-artifact` (n=4): A-Splitting the Powerstone, Koilos Roc, Urza's Command, Vampire's Kiss
- `rule:create-token-treasure` (n=6): Don Andres, the Renegade, Enterprising Scallywag, Gluntch, the Bestower, Goldspan Dragon, Involuntary Employment, Sword of Wealth and Power
- `rule:created-token-enters-tapped` (n=9): A-Splitting the Powerstone, Don Andres, the Renegade, Drana's Chosen, Graveyard Marshal, Koilos Roc, Owlbear Cub, Sami, Ship's Engineer, Urza's Command, Warped Landscape
- `rule:creates-token-with-x-scaled-counters` (n=1): Fractal Summoning
- `rule:damage-divided-among-multiple-targets` (n=2): Jeska, Thrice Reborn, Volley of Boulders
- `rule:damage-scales-with-creature-count` (n=1): Ajani, Nacatl Pariah // Ajani, Nacatl Avenger
- `rule:death-trigger-card-draw` (n=2): Darkslick Drake, Outlaw Medic
- `rule:death-trigger-counter-transfer` (n=1): Star Pupil
- `rule:death-trigger-token-creation` (n=3): Ancient Stone Idol, Dwarven Castle Guard, Stinging Hivemaster
- `rule:direct-damage-any-target` (n=18): Acidic Sliver, Borborygmos Enraged, Burning-Eye Zubera, Covenant of Blood, Erratic Explosion, Fireblade Charger, Foundry Champion, Geistblast, Lightning Storm, Master the Way, Meteor Storm, Orcish Cannoneers, Realm-Scorcher Hellkite, Searing Meditation, Soul Burn, Spikeshot Elder, Thornwind Faeries, Vengeful Devil
- `rule:drain-life` (n=4): A-Cauldron Familiar, Grave Endeavor, Soul Burn, Vampire's Kiss
- `rule:drain-on-creature-death` (n=4): Accursed Witch // Infectious Curse, Grave Venerations, Ragged Recluse // Odious Witch, Sangromancer
- `rule:draw-cards-with-life-loss-cost` (n=3): Coercive Impetus, Necrodominance, Promise of Power
- `rule:draw-scaled-by-creature-count` (n=0): (none)  [emptied by correction; axis retains prior-batch members in codebook.json]
- `rule:draw-trigger-self-counter-growth` (n=1): Kianne, Corrupted Memory
- `rule:enters-tapped` (n=24): Azorius Chancery, Blackbloom Rogue // Blackbloom Bog, Boseiju, Who Shelters All, Clay Revenant, Cloudpost, Coastal Tower, Command Bridge, Crossroads Village, Dread Wanderer, Forsaken Crossroads, Golgari Rot Farm, Growth Spasm, Jidoor, Aristocratic Capital // Overture, Llanowar Reborn, Meditation Pools, Ominous Asylum, Prismatic Geoscope, Rimewood Falls, Sacred Peaks, Shelob, Dread Weaver, Skyclave Cleric // Skyclave Basilica, Spara's Headquarters, Suppression Ray // Orderly Plaza, Tolaria West
- `rule:enters-tapped-conditional` (n=5): Castle Embereth, Clifftop Retreat, Rootbound Crag, Spectator Seating, Training Center
- `rule:equipment-etb-creates-and-attaches-token` (n=1): Ancestral Blade
- `rule:etb-and-attack-trigger` (n=2): Reputable Merchant, Shredder, Unrelenting
- `rule:etb-auto-attach-to-own-creature` (n=4): Assassin Gauntlet, Cliffhaven Kitesail, Shredder's Armor, Vibranium Strike Gauntlets
- `rule:etb-bounce-other-creature` (n=2): Invasion of Xerex // Vertex Paladin, Man-o'-War
- `rule:etb-bounce-own-land` (n=2): Azorius Chancery, Golgari Rot Farm
- `rule:etb-copy-your-permanent` (n=2): Essence of the Wild, Waxen Shapethief
- `rule:etb-counter-on-other-creature` (n=7): A-Tenured Inkcaster, Blade of the Swarm, Knight of Autumn, Reputable Merchant, Towashi Guide-Bot, Trusty Retriever, World War Hulk
- `rule:etb-create-token` (n=5): Belfry Spirit, Koilos Roc, Nahiri, Heir of the Ancients, Robotics Mastery, Spyglass Siren
- `rule:etb-create-token-creature` (n=15): Ajani, Nacatl Pariah // Ajani, Nacatl Avenger, Aspiring Aeronaut, Dawnhart Mentor, Doctor Doom, Emrakul's Hatcher, Ich-Tekik, Salvage Splicer, Nest Invader, Oath of Eorl, Oath of Eorl, Outlaw Stitcher, Rat King, Verminister, Staff of the Storyteller, Teyo, Geometric Tactician, The Huntsman's Redemption, Three Blind Mice
- `rule:etb-create-token-creature-conditional` (n=1): Saurian Symbiote
- `rule:etb-create-token-food` (n=2): Brandywine Farmer, Unlucky Cabbage Merchant
- `rule:etb-creature-triggers-surveil` (n=2): Gossip's Talent, Naga Oracle
- `rule:etb-draw-card` (n=6): Bomat Bazaar Barge, Brawn, Amadeus Cho, Cloudkin Seer, Grisly Transformation, Merchant of Secrets, Rune of Might
- `rule:etb-exile-graveyard-card` (n=4): Cremate, Necromancer's Covenant, Shadow of the Enemy, Tymaret, Chosen from Death
- `rule:etb-gain-life` (n=10): A-Circuit Mender, Illusions of Grandeur, Inspiring Cleric, Kitchen Finks, Knight of Autumn, Oasis Gardener, Shattered Seraph, Skyclave Cleric // Skyclave Basilica, Soaring Sandwing, Turntimber Ascetic
- `rule:etb-loot` (n=2): Flaring Cinder, Oath of Jace
- `rule:etb-mass-pump-your-creatures` (n=1): Devoted Paladin
- `rule:etb-modal-choice` (n=5): Analyze the Pollen, Blade of the Swarm, Knight of Autumn, Saurian Symbiote, Trusty Retriever
- `rule:etb-pump-target-creature` (n=2): Guac & Marshmallow Pizza, Rubblebelt Boar
- `rule:etb-scry` (n=3): April O'Neil, Kunoichi Trainee, Inga Rune-Eyes, Lizardfolk Librarians
- `rule:etb-self-bounce-own-permanent` (n=1): Rescuer Chwinga
- `rule:etb-tap-and-stun-target` (n=2): Lodestone Needle // Guidestone Compass, Rowdy Snowballers
- `rule:etb-tutor-specific-named-card-to-hand` (n=2): Asmoranomardicadaistinaculdacar, Silver Surfer, Galactus's Herald
- `rule:etb-tutor-to-hand` (n=3): Floriferous Vinewall, Gatecreeper Vine, Marshals' Pathcruiser
- `rule:etb-with-counters` (n=10): Arcbound Hybrid, Crovax the Cursed, Faithful Watchdog, Fierce Invocation, Grave Endeavor, Jade Orb of Dragonkind, Lightning Serpent, Nimbus Swimmer, Rampant Rejuvenator, Star Pupil
- `rule:etb-with-negative-counters` (n=1): Leech Bonder
- `rule:evasion-vs-high-power-blockers` (n=1): April O'Neil, Kunoichi Trainee
- `rule:exile-until-source-leaves` (n=6): Aang's Iceberg, Deputy of Detention, Fiend Hunter, Henchbots, Quarantine Field, Touch the Spirit Realm
- `rule:fixed-lifegain` (n=9): Ajani, the Greathearted, Battle Menu, Covenant of Blood, Feed the Clan, Guac & Marshmallow Pizza, Kayla's Command, Lich's Caress, Noxious Grasp, Tandem Tactics
- `rule:flashback-recast-from-graveyard` (n=2): Eviscerator's Insight, Think Twice
- `rule:forced-attack-each-combat` (n=3): Mishra's Juggernaut, Toski, Bearer of Secrets, Weary Prisoner // Wrathful Jailbreaker
- `rule:forced-hand-reveal` (n=2): Pilfer, Tourach's Canticle
- `rule:forces-all-creatures-attack` (n=2): Grand Melee, Warmonger Hellkite
- `rule:forces-creature-to-attack` (n=1): Silver Surfer, Galactus's Herald
- `rule:free-cast` (n=2): Wondrous Crucible, World War Hulk
- `rule:free-sacrifice-outlet` (n=1): Industrial Advancement
- `rule:gives-energy-counters-immediately` (n=3): Bristling Hydra, Primal Prayers, Thriving Ibex
- `rule:grants-ability-at-threshold-board` (n=2): Radiant Destiny, Squadron Carrier
- `rule:grants-ability-at-threshold-self` (n=4): Backwoods Survivalists, Chlorophant, Grim Flayer, Werebear
- `rule:grants-additional-combat-phase` (n=4): All-Out Assault, Genji Glove, Savage Beating, Seize the Day
- `rule:grants-cascade-to-own-spells` (n=2): Abaddon the Despoiler, Imoti, Celebrant of Bounty
- `rule:grants-controller-hexproof` (n=1): Orbs of Warding
- `rule:grants-creature-type` (n=1): Spider-Suit
- `rule:grants-double-strike-target` (n=1): Kayla's Command
- `rule:grants-extra-land-drop` (n=1): Dryad of the Ilysian Grove
- `rule:grants-haste-to-your-creatures` (n=2): Goro-Goro and Satoru, Karrthus, Tyrant of Jund
- `rule:grants-trample-to-creatures-with-counters` (n=3): Nev, the Practical Dean, Sunbringer's Touch, The Crowd Goes Wild
- `rule:grants-unblockable` (n=1): Guild Thief
- `rule:grants-unblockable-target` (n=1): Taigam's Strike
- `rule:grants-ward-to-other-creatures` (n=2): Star Whale, Wondrous Crucible
- `rule:graveyard-to-exile-replacement` (n=1): Necrodominance
- `rule:graveyard-to-hand-recursion` (n=6): Midnight Scavengers, Misery Charm, Raise Dead, Return to Battle, Verdant Confluence, Wildest Dreams
- `rule:graveyard-to-library-top-recursion` (n=1): Salvage
- `rule:innate-unblockable` (n=1): Ukkima, Stalking Shadow
- `rule:kicker-conditional-bonus-effect` (n=5): Bold Defense, Orim's Touch, Stomped by the Foot, Tourach, Dread Cantor, Gnarlid Pack
- `rule:land-fetch-to-battlefield` (n=4): Beanstalk Giant // Fertile Footsteps, Crop Rotation, Spider-Man, Brooklyn Visionary, Verdant Confluence
- `rule:leaves-battlefield-trigger-create-token-mutagen` (n=1): Splinter, the Mentor
- `rule:level-up-scaling-stats-abilities` (n=1): Brimstone Mage
- `rule:library-dig-put-onto-battlefield` (n=1): Planar Bridge
- `rule:library-dig-to-hand` (n=2): Merchant's Dockhand, Rakshasa's Bargain
- `rule:library-top-visibility` (n=3): Bolas's Citadel, Eladamri, Korvecdal, Vesuvan Drifter
- `rule:life-total-reset` (n=1): Form of the Dinosaur
- `rule:mana-activated-pump-self` (n=8): A-Paragon of Modernity, Fathom Fleet Firebrand, Foundry Champion, Foundry Champion, Immolating Souleater, Perilous Shadow, Savage Knuckleblade, Wyluli Wolf
- `rule:mass-counter-distribution` (n=8): Ajani, Nacatl Pariah // Ajani, Nacatl Avenger, Ajani, the Greathearted, Call the Spirit Dragons, Gluntch, the Bestower, Now for Wrath, Now for Ruin!, Soulblade Renewer, Sunbringer's Touch, The Crowd Goes Wild
- `rule:mass-creature-destruction` (n=4): Blood on the Snow, Kaya's Wrath, Ratchet Bomb, Shatterstorm
- `rule:mass-damage-creatures-and-players` (n=1): Fault Line
- `rule:mass-damage-flying-creatures-scaled-by-x` (n=2): Squall Line, Windstorm
- `rule:mass-damage-opponent-creatures-only` (n=1): Pharagax Giant
- `rule:mass-debuff-opponent-creatures` (n=2): Crovax, Ascendant Hero, Urza's Command
- `rule:mass-graveyard-exile` (n=2): Decompose, Shadow of the Enemy
- `rule:mass-pump-your-creatures` (n=6): Bold Defense, Castle Embereth, Preposterous Proportions, Three Blind Mice, Vitalizing Wind, Warrior's Stand
- `rule:mass-untap-and-haste-stolen-creatures` (n=3): Involuntary Employment, Jeering Instigator, Mass Mutiny
- `rule:mass-untap-your-creatures` (n=5): All-Out Assault, Join Shields, Karrthus, Tyrant of Jund, Rally of Wings, Savage Beating
- `rule:mill-self-cards` (n=3): Dawnhand Eulogist, Roots of Wisdom, Wondrous Crucible
- `rule:modal` (n=25): Battle Menu, Blood on the Snow, Blue Elemental Blast, Change the Equation, Chaos Charm, Clash of the Eikons, Defend the Rider, Eldrazi Confluence, Fascination, Feast or Famine, Frontline Rush, Insidious Will, Kayla's Command, Merciless Eviction, Misery Charm, Profane Command, Promise of Power, Raise the Draugr, Raze the Effigy, Tooth and Nail, Urza's Command, Verdant Confluence, Weave the Nightmare, Winterflame, You Come to the Gnoll Camp
- `rule:no-maximum-hand-size` (n=1): Spellbook
- `rule:partner-with-tutor` (n=1): Soulblade Renewer
- `rule:pay-life-cost-for-effect` (n=4): Crovax, Ascendant Hero, Fountain of Youth, Island Fish Jasconius, Tempest Harvester
- `rule:plus1-counters-matter` (n=6): A-Tenured Inkcaster, Dai Li Agents, Iroh, Dragon of the West, Levitating Statue, Lifecrafter's Gift, Puca's Covenant
- `rule:power-scales-with-creature-count` (n=3): Invasion of Xerex // Vertex Paladin, Reckless One, Shanna, Sisay's Legacy
- `rule:prevent-all-combat-damage-this-turn` (n=1): Spore Cloud
- `rule:prevent-damage-to-your-creatures` (n=1): Glyph of Destruction
- `rule:prevent-fixed-damage-any-target` (n=7): Barrenton Medic, Charm Peddler, Field Surgeon, Orim's Touch, Orim, Samite Healer, Squee's Toy, Story Circle
- `rule:prevents-regeneration` (n=6): Death Pits of Rath, Feast or Famine, Magus of the Abyss, Porphyry Nodes, Retribution of the Meek, Shatterstorm
- `rule:pump-scaled-by-own-creature-count` (n=2): Frontline Rush, Might of the Masses
- `rule:pump-two-target-creatures` (n=2): Allied Assault, Tandem Tactics
- `rule:reanimate-from-graveyard` (n=9): Blood on the Snow, Geth, Thane of Contracts, Grave Endeavor, Life // Death, Profane Command, Tempt with Immortality, Tethmos High Priest, Unhallowed Pact, Wake the Dead
- `rule:redirect-targets-of-spell-or-ability` (n=3): Boltbender, Insidious Will, Lutri, the Spellchaser
- `rule:restricted-purpose-mana` (n=6): A-Base Camp, Codsworth, Handy Helper, Eclipsed Realms, Fabrication Foundry, Great Hall of the Biblioplex, Koilos Roc
- `rule:reveal-hand-then-choose-discard` (n=2): Pilfer, Tourach's Canticle
- `rule:rhystic-tax` (n=4): Nazgûl Battle-Mace, Quench, Seizures, We Say Thee Nay!
- `rule:sacrifice-creature-for-self-pump` (n=2): Prossh, Skyraider of Kher, Slaughter-Priest of Mogis
- `rule:sacrifice-for-card-draw` (n=1): Limestone Golem
- `rule:sacrifice-for-creature-token` (n=1): Idol of Oblivion
- `rule:scales-mana-by-count` (n=3): Cloudpost, Growing Rites of Itlimoc // Itlimoc, Cradle of the Sun, Prismatic Geoscope
- `rule:scales-token-count-with-x` (n=1): White Sun's Zenith
- `rule:self-bounce-activated` (n=1): Savage Knuckleblade
- `rule:self-counter-growth` (n=4): Dawnbringer Charioteers, Memory Worm, Rat King, Verminister, Riku of Many Paths
- `rule:self-exile-after-resolution` (n=3): Harness Infinity, Revival Experiment, Wildest Dreams
- `rule:self-mana-ability-grants-keyword` (n=1): Savage Knuckleblade
- `rule:self-recursion-from-graveyard` (n=2): Clay Revenant, Dread Wanderer
- `rule:self-sacrifice-on-land-type-absence` (n=2): Island Fish Jasconius, Manta Ray
- `rule:sets-base-power-or-toughness` (n=5): Almost Perfect, Eidolon of Astral Winds, Octavia, Living Thesis, Octopus Umbra, Woodlurker Mimic
- `rule:stun-counter` (n=3): Grappling Kraken, Rowdy Snowballers, Suppression Ray // Orderly Plaza
- `rule:targeted-bounce-creature` (n=3): Compelling Deterrence, Johann's Stopgap, Lost in the Spirit World
- `rule:targeted-creature-damage` (n=15): Chandra's Outrage, Chaos Charm, Cinder Strike, Combustion Technique, Conduct Electricity, Form of the Dinosaur, Pigment Storm, Reduce to Ashes, Shower of Sparks, Sizzling Barrage, Spite of Mogis, Strafe, Tower of Calamities, Weave the Nightmare, Winterflame
- `rule:targeted-destruction` (n=21): Audacious Swap, Battle Menu, Bone Shards, Deadly Precision, Feast or Famine, Fell, Get the Point, Gleeful Sabotage, Go for the Throat, Hatut Zeraze Strike Force, Knight of Autumn, Lich's Caress, Nantuko Vigilante, Noxious Grasp, Raze the Effigy, Red Elemental Blast, Serra's Liturgy, Sip of Hemlock, Status // Statue, Tezzeret's Betrayal, Violent Ultimatum
- `rule:targeted-discard` (n=3): Chain of Smog, Devour Intellect, Recoil
- `rule:targeted-exile` (n=7): Aang's Iceberg, Anoint with Affliction, Banish from Edoras, Fiend Hunter, Hurl Through Hell, Introduction to Annihilation, Touch the Spirit Realm
- `rule:targeted-planeswalker-damage` (n=2): Scorching Missile, Shower of Sparks
- `rule:targeted-player-damage` (n=10): Breath of Malfegor, Decimator Web, Memory Worm, Misery Charm, Obelisk of Alara, Power Leak, Profane Command, Scorching Missile, Shower of Sparks, Steam Vines
- `rule:tax-or-counter-spell` (n=2): Bring the Ending, Runeboggle
- `rule:taxes-opponent-spell-cost` (n=1): Reidane, God of the Worthy // Valkmira, Protector's Shield
- `rule:temporary-control-theft` (n=12): Awaken the Sleeper, Confiscate, Involuntary Employment, Jeering Instigator, Karrthus, Tyrant of Jund, Mass Mutiny, Ritual of the Machine, Sauron, the Lidless Eye, Spinal Embrace, Spirit Away, Unwilling Recruit, Wrangle
- `rule:temporary-keyword-grant` (n=13): Brute Strength, Chaos Charm, Efflorescence, Eidolon of Astral Winds, Enlarge, Leyline Axe, Riku of Many Paths, Roughshod Duo, Sauron, the Lidless Eye, Unwilling Recruit, Woodlurker Mimic, World War Hulk, Wrangle
- `rule:the-ring-tempts-you` (n=3): Aarakocra Sneak, Now for Wrath, Now for Ruin!, Rohirrim Lancer
- `rule:token-sacrifice-for-colorless-mana` (n=2): Emrakul's Hatcher, Nest Invader
- `rule:token-sacrifice-for-mana` (n=2): Eldrazi Confluence, Growth Spasm
- `rule:transforms-on-graveyard-threshold` (n=2): Primal Amulet // Primal Wellspring, The Legend of Kyoshi // Avatar Kyoshi
- `rule:tribal-anthem-buff` (n=14): A-Patrician Geist, Aven Brigadier, Aven Brigadier, Balthor the Stout, Bonesplitter Sliver, Child of the Pack // Savage Packmate, Crovax, Ascendant Hero, Cursecloth Wrappings, Doctor Octopus, Master Planner, Inquisitor Greyfax, Paragon of Fierce Defiance, Radiant Destiny, The Immortal Sun, Yotian Tactician
- `rule:triggers-on-cast-instant-sorcery` (n=1): Exhibition Tidecaller
- `rule:tutor-basic-land-to-hand` (n=1): Kayla's Command
- `rule:tutor-from-outside-game-to-hand` (n=1): Research // Development
- `rule:tutor-to-library-top` (n=0): (none)  [emptied by correction; axis retains prior-batch members in codebook.json]
- `rule:untaps-target-land` (n=1): Unwind
- `rule:x-scales-with-permanent-count` (n=1): Exploding Borders

---

## 12. CAPTAIN RATIFICATION — PARSED DIRECTIVES (2026-07-30)

**AUTHORITATIVE FOR PARSING.** Translated from Captain's inline VERDICT
annotations (sections 1–2) plus the A–I review-session rulings, all resolved
per the reviewing session's recommendations by Captain's explicit direction.
Where this conflicts with anything above, THIS SECTION GOVERNS. Card-text
claims were verified against live oracle text in the review session; emit
re-verifies against the gate-passing corpus (verify-or-drop). Companion
document `docs/CODEBOOK-NAMING-GRAMMAR.md` (RATIFIED v1.0) ships with this
batch; directives below reference it as GRAMMAR.

### D1 — Captain's inline verdicts stand, with one expansion
- rule:combat-damage-to-creature-triggers-self-counter → RENAMED
  rule:combat-damage-to-player-triggers-self-counter, definition corrected as
  written in section 1 (family-suffix normalization deferred to the walk).
- rule:grants-trample-to-countered-creatures → RENAMED
  rule:grants-trample-to-creatures-with-counters (and "countered" is now a
  GRAMMAR-banned token).
- rule:conditional-attack-restriction-by-defender-land-type → RENAMED
  rule:conditional-attack-restriction-by-defending-player-land-type.
- rule:attack-trigger-damage-defender → the rename EXPANDS to a three-way
  split (members verified as three distinct target shapes):
  - rule:attack-trigger-damage-defending-player — Scorch Spitter ("deals 1
    damage to defending player").
  - rule:attack-trigger-damage-creature-of-defending-player — Purifying
    Dragon ("1 damage to target creature defending player controls").
  - rule:attack-trigger-mass-damage-defending-players-creatures — Swathcutter
    Giant ("1 damage to each creature defending player controls").
  Ledger: `defending-player` logged as Captain-attributed candidate; parent
  vs. scope-facet classification resolves at schema pass. The bare token
  "defender" is GRAMMAR-banned in slugs.

### D2 — Scaling-axis surgery (answers the section-1 line-84 VERDICT question)
- MERGE rule:scales-token-count-with-x INTO rule:token-count-scales-with-x
  (duplicate synonymous axes admitted in batch 6; White Sun's Zenith joins).
- RENAME rule:creates-token-with-x-scaled-counters →
  rule:create-token-with-x-counters (sole member Fractal Summoning).
- The `-scales-with-` connective standard is ratified via GRAMMAR D-3; the
  walk executes remaining `-scaled-by-` renames — none executed at this emit.

### D3 — Activation-restriction correction + family closure
- rule:activation-restricted-to-sorcery-speed: member_removal(Kjeldoran Elite
  Guard) — verified "Activate only during combat."
- NEW captain-authored rule:activation-restricted-during-combat (n=1:
  Kjeldoran Elite Guard), slug per GRAMMAR §3.
- The full restriction family is enumerated and DET-owned per GRAMMAR §3/D-4;
  batch-8 SYNTH prompt must state the family is off-limits to SYNTH labeling.

### D4 — pay-life-cost-for-effect polarity scrub
- member_removal(Fountain of Youth) — "{2}, {T}: You gain 1 life" is lifegain;
  rehome via member_addition to rule:fixed-lifegain.
- member_removal(Island Fish Jasconius) — its untap payment is mana, not life
  (emit quote-verifies before write).
- Emit performs a full quote-pull on this axis's remaining members (Crovax,
  Tempest Harvester, and all prior-batch members); any member whose quote
  lacks a life payment ON THE COST SIDE (GRAMMAR §9) is removed with the same
  rehome discipline; more than one further failure → halt loudly.

### D5 — Unwind remove-and-rehome
- rule:untaps-target-land: member_removal(Unwind) — "Untap up to three lands"
  has no "target" (GRAMMAR §6 target law; CR 601.2c).
- member_addition(Unwind) to rule:counters-noncreature-spell ("Counter target
  noncreature spell." — restriction present in quote).
- Ledger: free-mechanic untap-lands rider family (CR-adjacent, Urza-block
  shape) as a parent-tree candidate.

### D6 — Forsaken Crossroads rehome (SUP "no axis fits" overturned)
member_additions: rule:choose-color-on-etb, rule:etb-scry, and
rule:enters-tapped-conditional (the "you may untap it instead" replacement is
the conditional gate; quote in evidence). Gate #0 status confirmed clean
(Alchemy card, Historic/Timeless/Brawl legal).

### D7 — Grammar instantiation (standing behavior from this emit forward)
- INSTANTIATE rule:leaves-battlefield-trigger-create-token-food (n=1:
  Brandywine Farmer) — the family grammar was already ratified; the section-1
  ledger flag is withdrawn as superseded.
- Per GRAMMAR §11: SUP and emit instantiate ratified-grammar nodes on first
  quote-verified member; ledger-flagging a grammar-composable home is a
  protocol error from batch 8 onward. Wire lane=codebook-grammar and
  validate_slug.py per GRAMMAR §10–11 (build lands in the walk session; the
  behavioral rule binds now).

### D8 — Slug continuity
NEW candidate rule:death-trigger-card-draw is ADMITTED but under the original
batch-5 slug rule:death-trigger-draw-card (killed for n=0, not fakeness;
revival-with-members annotated on the kill record). GRAMMAR D-1 confirms
`death-trigger` as the family word.

### D9 — All remaining verdicts stand; process items
- All other section 1–2 KEEPs, removals, additions, the definition_edit, and
  ledger flags stand as written (Ob Nixilis loyalty facet noted — `loyalty`
  is now a GRAMMAR delivery value).
- Roster generator: add a dedupe assertion (the tribal-anthem-buff
  "Aven Brigadier, Aven Brigadier" duplicate row).
- Batch-8 SYNTH: thinking mode stays OFF (Captain-ruled); the digest-side
  detector remains the catch for killed-slug resurrection; revisit only on
  dress-rehearsal evidence.
- Batch-8 feedback additions: restriction family DET-owned (D3); the GRAMMAR
  §8 counter/token laws and §9 cost-position law join the prompt's
  evidence-quote rules.

---

**STOP.** Section 12 + docs/CODEBOOK-NAMING-GRAMMAR.md are the authoritative
record for batch 7. Run `/triage-emit 7`: parse §12, verify every quote and
member against the gate-passing corpus, write decisions/batch-7.json,
reconcile to codebook v0.7, and STOP. Do NOT assemble or submit batch 8 —
the combined per-axis walk (CORPUS-PASS-PLAN steps 2–5, using
CODEBOOK-NAMING-GRAMMAR.md as kickoff) runs first; batch 8 is the dress
rehearsal on post-walk machinery.
