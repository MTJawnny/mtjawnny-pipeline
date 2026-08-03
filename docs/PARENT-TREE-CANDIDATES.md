# PARENT-TREE-CANDIDATES — schema-pass ledger

Target path: docs/PARENT-TREE-CANDIDATES.md (pipeline repo).
Purpose: accumulate every parent/hierarchy flag as it arises so the
end-of-bootstrap SCHEMA PASS is a ratification session, not archaeology.
Beta and emit APPEND here; nothing in this file is load-bearing until the
schema pass ratifies it. Design principle (Captain, 2026-07-20):
**children are defined by MECHANISM, parents are defined by JOB.**

## Structural rulings needed at schema pass (decide once, apply to all)

- S1. Parents are DERIVED: union of ratified children computed at
  index-build time, plus an explicit direct-member list for cards no
  child captures. Cards are never hand-tagged with both child and parent.
- S2. Scoring: most-specific-shared-node only. Two cards sharing a child
  score the child; sharing only the parent scores the parent. No
  double-dip up the chain. (IDF weights parents down automatically.)
- S3. Depth is ratified PER FAMILY. Trigger families are depth-3 by
  Captain's design (etb -> etb-create-token -> etb-create-token-creature).
  Default elsewhere: depth-2 unless ratified deeper.
- S4. Multiple parents allowed when earned (stun-counter sits under both
  lockdown and a counters-as-object family); every parent edge is a
  ratified ruling.
- **S4a. PARENT EDGES ARE UNRANKED AND EQUAL (Captain-ratified 2026-08-02).**
  When a card earns two parents, **neither wins.** They apply
  simultaneously, at equal weight, with no primary and no discount.

  > *"Neither one wins, they live both simultaneously — two different rules
  > applied equally. Applied unbiased, it's not more than one or the other.
  > Someone looking to build an enchantment deck that contains red might want
  > Monstrous Rage just as much as a mono-red aggro deck. The distinction is
  > on what a player might need. And they fit both roles equally."*

  Worked case: **Monstrous Rage** is a combat trick (+2/+0 at instant speed,
  composed to +3/+1 with trample via CR 111.10k) *and* an enchantment-deck card
  (it makes a Role, which is an enchantment — Virtuous Role literally scales
  with enchantments you control). Both are true at full strength. Which one
  matters is a property of **the deck being built**, not of the card, so the
  data may not decide it in advance.

  **Binding consequences for the build:**
  - No "primary parent" field. Anything that needs to pick one is wrong.
  - No confidence weight or ordering on parent edges. A card with two parents
    is equally a member of both, exactly as §1 made axis membership
    non-exclusive.
  - **"Parent TREE" is a misnomer.** Unranked multi-parent edges make this a
    lattice/DAG, not a tree. This file's name is historical; do not let it
    imply a single path to a root.
  - S2's most-specific-shared-node rule is unaffected — it selects the
    scoring node for a *pair* of cards, which is a different question from
    ranking one card's parents. But S2 may not be implemented by walking "the"
    parent chain, because there is no single chain.

  This is the §1 multi-axis ruling applied one layer up, and for the same
  reason: member counts are not a partition, and now neither are parent
  populations.
- S5. Implication edges ("counts toward"): a superset-scoped tag counts
  toward its subset siblings (mass-nonland-destruction counts toward
  mass-creature-destruction, mass-artifact-destruction, ...). Damageable/
  destroyable object classes are a closed system, so the edge set is
  finite and enumerable. Needs its own scoring rule (does an implied
  match score like a direct match?). Captain: "we'll need to think this
  out."
- S6. Parent names are the USER-FACING vocabulary (lockdown, ramp,
  wheels, edicts, gy-hate); the final naming audit is ruthless on parents,
  lenient on children. Viewer sections group by parent ("Same Job,
  Different Words" made literal).
- S7. Validation: proposed parents get the family-tree evidence check
  (co-occurrence via the substitute lens) before ratification. Cheap;
  run per candidate.

## Ratified parent decisions (already Captain-ruled, pending build)

- rule:lockdown — "taps and/or keeps things tapped." Children:
  rule:stun-counter (RENAMED from stun-counter-lockdown, batch-3 Q1),
  rule:prevents-target-untap-next-step. Direct-member candidates until
  children exist: Hokori Dust Drinker, Queen of Ice, Icy Manipulator,
  Stasis. Substitute family (decks run Stasis OR stun packages).
- Trigger families (batch-3 §1, Captain): rule:etb, rule:attack-trigger,
  rule:cast-trigger, rule:combat-damage-triggers, rule:death-trigger.
  All existing leaf axes with these prefixes become children. etb is
  depth-3 (see S3). Derivation law rider: cast trigger requires
  "when you cast" verbiage — a cast trigger is NEVER an ETB trigger.
- rule:N-scales-with-N-count — parent scheme over all scaling axes
  (batch-2 M6 ruling): damage-scales-with-creature-count,
  scales-mana-by-count, x-scales-with-permanent-count,
  power-scales-with-creature-count, lifegain-scaled-by-mana-value; future
  draw-scales-with-shrine-count etc. x-scales-with-permanent-count is NOT
  a catch-all.
- Damage-target family (batch-2 M8): direct-damage-any-target,
  targeted-creature-damage, targeted-player-damage,
  targeted-planeswalker-damage, targeted-battle-damage. Mixed targets =
  multiple tags, never combo tags.
- mass-N-N scheme (batch-3 §1): mass-<type>-<disposal> lattice
  (destruction / exile / sacrifice / bounce / minus1-counters ×
  creature / artifact / enchantment / planeswalker / battle / nonland /
  permanent). Ruinous Ultimatum -> mass-nonland-destruction, counts
  toward per-type siblings via S5.
- Naming families logged for final audit (no midflight renames):
  animate-land (+ animate-artifact / animate-enchantment /
  animate-planeswalker); cost-reduction -> spell-cost-reduction beside
  individual-cost-reduction; grants-player-hexproof; the unblockable
  trio scope review.
- rule:activated-ability / rule:regenerate-self (batch-3 3c, Captain):
  killed rule:activated-regenerate-self, decomposed job-first ("what a
  card has, then what it does"): rule:activated-ability is the mechanism
  parent, rule:regenerate-self the specific effect child, with siblings
  rule:regenerate-target, rule:regenerate-controller-board,
  rule:regenerate-all for non-activated regeneration sources. Regenerate
  keyword itself stays on the keyword ledger regardless of this scheme's
  eventual build. Direct-member candidates until children exist: Manor
  Skeleton, Cinderbones.
- **Depth-3 etb scheme, EXECUTED (batch-5 D10, Captain, per
  MASTER-HANDOFF-ADDENDUM-3.md §3 -- compounds authored, atomics/broader
  tags derived).** This is the first parent scheme actually built as
  codebook structure rather than left as a ledger note, using the
  already-ratified illustrative example (addendum-2 §5: etb ->
  etb-create-token -> etb-create-token-creature).
  - rule:etb-create-token is now a parent over 4 new type-specific
    children: rule:etb-create-token-creature, rule:etb-create-token-creature-conditional
    (gated by an intervening-if clause, e.g. Foot Mystic's Disappear),
    rule:etb-create-token-food, rule:etb-create-token-mutagen. Batch-5's
    own 13 members were reclassified into these children (quote-verified
    per member). **Open scope note:** rule:etb-create-token's 46
    PRE-EXISTING members (batches 1-4) were deliberately left
    unreclassified this batch -- reclassifying them needs their quotes
    re-fetched and re-verified, out of scope for a single emit session.
    They remain direct members of the parent pending future
    classification. Punch-listed in decisions/batch-5.json.
  - rule:leaves-battlefield-trigger-create-token (new axis, batch-5) is
    simultaneously a parent AND keeps 2 direct members (Chittering
    Dispatcher, Suki, Courageous Rescuer) pending their own
    classification -- the ratified parents ruling explicitly permits
    direct members alongside children. New child:
    rule:leaves-battlefield-trigger-create-token-creature (Grixis
    Slavedriver, rehomed from the killed rule:death-trigger-token-creation
    member -- verified as a leaves-the-battlefield trigger, not a death
    trigger).
  - Future siblings left open on both families: -treasure, -blood,
    -lander, -clue, etc.

## Proposed parents (flagged in triage docs, not yet ruled)

- doubles-<thing>: doubles-token-creation, doubles-counter-placement,
  doubles-etb-triggers, doubles-proliferate. (batch-1)
- token-creation(trigger): creates-creature-token, etb-create-token,
  death-trigger-token-creation, copy-creature-token — now intersects the
  trigger families; schema pass decides which axis is primary parent.
  (batch-1 Q4)
- triggered-on-cast(filter, payoff): cast-trigger-card-draw,
  triggers-on-cast-instant-sorcery, copies-cast-instant-sorcery-as-payoff.
  (batch-1; subsumed by rule:cast-trigger? decide at schema pass)
- lifegain-payoff(effect): Sanguine Bond, lifegain-triggered-counter,
  Archangel-of-Thune shapes. (batch-1 Q2)
- Exile family: targeted-exile + exile-until-source-leaves (layered) +
  mass-graveyard-exile vs graveyard-to-exile-replacement (one-shot vs
  continuous). (batch-1)
- Untap family: mass-untap-your-creatures with scope/type/cadence params
  -> possible rule:mass-untap parent; opposite-polarity pair with
  lockdown noted (Mishra's Helix taps lands). (batch-1, batch-3 §0)
- enters-tapped polarity parent (self vs fetched-object). (batch-1 M1)
- Library-top family: library-top-visibility + cast-from-top-of-library
  (future-sight pair). (batch-1)
- Threshold family: grants-ability-at-threshold-self /
  grants-ability-at-threshold-board (captain-authored, batch-2) —
  possible parent rule:threshold-matters.
- Counters-matter family: plus1-counters-matter (batch-2),
  minus1-counters-matter (batch-3, Captain: "needed rule"),
  stun-counter (batch-3) -> possible parent rule:counters-matter or
  counters-as-object.
- rule:number-of-opponents-matter (batch-3, Captain): grabs all cards
  scaling off opponent count (Adeline, Luxury Suite). Standalone tag;
  possible member of a broader count-matters family.
- Discard family: targeted-discard vs symmetric-hand-refill (wheels) —
  scope parent. (batch-1)
- Drain family: drain-life, drain-on-creature-death — job parent
  candidate rule:drain. (batch-1 Q2)
- Self-counter-growth family (batch-4): three trigger-context siblings now
  exist -- rule:self-counter-growth (tap/activated),
  rule:attack-trigger-self-counter-growth, rule:draw-trigger-self-counter-growth
  (new this batch) -- candidate for the counters-matter family above, or its
  own rule:self-counter-growth parent under the trigger-family scheme.
- Energy family growth (batch-4): rule:gives-energy-counters-immediately
  absorbed a duplicate free-lane candidate (rule:etb-grants-energy-counters)
  this batch, confirming the family is live. Existing siblings:
  rule:gives-energy-counters-condition, rule:energy-outlet-condition,
  rule:energy-outlet-infinite (all seeded batch-3 Q2). Schema pass: possible
  rule:energy parent.
- "Would go to graveyard, exile instead" replacement family (batch-4):
  rule:graveyard-to-exile-replacement absorbed a duplicate free-lane
  candidate this batch (rule:replacement-exile-instead-of-graveyard); a
  second candidate (rule:replaces-death-with-exile, self-protective Aura
  vs. removal-spell exile-rider) is a batch-4 QUESTION on whether it merges
  in or stays a sibling by function (defense vs. offense) -- ties into the
  Exile family entry above (batch-1).
- "Taps a target creature" trigger-context gap (batch-4): closely reading
  rule:activated-tap-target-creature's members surfaced 9 of 16 that tap a
  creature via an ETB trigger, an attack trigger, or a Saga chapter trigger
  rather than a player-activated ability (removed as member-mismatches, see
  TRIAGE-BATCH-4.md section 0). No axis currently exists to hold the
  non-activated ones. Once the trigger-family children exist per the
  ratified etb/attack-trigger scheme above, "taps target creature" is a
  candidate leaf under each (rule:etb-tap-target-creature,
  rule:attack-trigger-tap-target-creature), parallel to
  rule:activated-tap-target-creature.
- rule:mana-activated-pump-self absorbed two batch-4 free-lane candidates
  (activated-pump-with-self-damage-cost: self-damage cost-shape;
  activated-self-toughness-pump: toughness-only stat target) as merges --
  flagging both as future schema-pass parameters (cost-shape, stat-target)
  rather than separate axes, consistent with the etb-with-counters
  polarity-parameter precedent (batch-3).
- rule:overwrites-creature-type (batch-3 M1, Captain): sibling boundary
  to rule:grants-creature-type, not a parent/child — the RATIFIED
  boundary rule itself (not just the flag) is: rule:grants-creature-type
  requires "in addition to its other types" phrasing; effects that
  overwrite/replace a creature's types entirely (e.g. Gornog, the Red
  Reaper — "target creature ... becomes a Coward") are a different axis.
  No members confirmed yet; needs a corpus scan before it's built.

- Keyword-grant facet scheme (batch-4, Captain, §10 STEP 2a): wide-net
  rule:temporary-keyword-grant stays the catch-all (and per the batch-4 D4
  standing rule, absorbs every future grants-temporary-<keyword> candidate
  on sight, no fresh merge question needed). Granular facet dimensions
  proposed on top: which keyword (e.g. gives-hexproof), duration (EOT /
  next turn / static-anthem / keyword counter), scope (target / up-to-N /
  all-you-control / all), delivery trigger (etb / activated / cast).
  Interacts directly with open tension T1 below (keyword-identity leaves
  vs. the b1-Q1 engine-redundancy kill) — schema pass reconciles, do not
  author these as axes now.
- Cost-shape facet scheme (batch-4, Captain, §10 STEP 2b, per the D6
  precedent reversal below): wide-net cost axes
  (rule:additional-cost-sacrifice-permanent, rule:additional-cost-discard-a-card,
  plus the punch-listed b2/b3 revival candidates) stay wide-net; granular
  children proposed on top: object class sacrificed, one-shot vs.
  repeatable outlet.
- Delivery-facet note (batch-4, §10 STEP 2c): rule:gives-energy-counters-immediately's
  batch-4 merge (absorbing rule:etb-grants-energy-counters, 3 members —
  Hightide Hermit, Decoction Module, Inventor's Axe) should be
  distinguishable by delivery trigger (etb vs. other) at schema pass —
  same delivery-trigger facet idea as the keyword-grant scheme above,
  flagged here as its own note since it surfaced from a different merge.
- **Precedent reversal (batch-4 D6, Captain): "cost-shape riders are not
  axes" is OVERTURNED for cost-side axes.** The b2/b3 standing (which
  killed rule:sacrifice-creature-as-additional-cost,
  rule:sacrifice-as-additional-cost, rule:self-sacrifice-divided-damage)
  no longer applies to cost-shape axes generically — they are legitimate
  wide-net axes (see the cost-shape facet scheme entry above). Punch-list,
  not executed: evaluate resurrecting the three b2/b3-killed cost-shape
  axes named above at reconcile or schema pass.

- Counterspell restriction-scope family (batch-5, RESOLVED per D7):
  rule:activated-counter-target-spell (unrestricted-by-type, activated
  delivery) and rule:counters-noncreature-spell (noncreature-restricted)
  are siblings by restriction-scope — same shape as the damage-target
  family's per-object-class parent scheme (M8). The two removed
  counters-noncreature-spell members were individually rehomed rather than
  both landing in one place: Declaration of Naught -> rule:activated-counter-target-spell
  (activated delivery, "{U}: Counter target spell with the chosen name.");
  Electrosiphon -> NEW rule:counters-target-spell (unrestricted, no
  activation-cost pattern, "Counter target spell."). Three-way sibling
  family now: counters-target-spell (unrestricted) /
  counters-noncreature-spell (type-restricted) /
  activated-counter-target-spell (delivery-restricted) — schema pass
  decides the actual parent/facet shape (restriction-type vs.
  delivery-mechanism may be two different facet dimensions, not one).
- Death-trigger token-creation scaling (batch-5): rule:death-trigger-token-scaled-by-power
  (new, n=2: Elenda the Dusk Rose, The Skullspore Nexus) is a scaled child
  of the existing rule:death-trigger-token-creation parent — same
  N-scales-with-N-count shape as the existing scaling family (batch-2 M6).
- Leaves-battlefield vs. dies trigger scope (batch-5):
  rule:leaves-battlefield-trigger-create-token (new, n=2: Chittering
  Dispatcher, Suki, Courageous Rescuer) triggers on ANY leave-the-battlefield
  event, broader than rule:death-trigger-token-creation's "dies" scope —
  ties into the ratified trigger-family scheme (rule:etb/attack-trigger/
  cast-trigger/death-trigger, batch-3) as a sibling built on a wider
  trigger condition, not a duplicate.
- Tautological-rider recurrence (batch-5, flag not a parent): three
  batch-5 candidates (rule:aura-static-pump-enchanted-creature,
  rule:aura-static-power-toughness-debuff, rule:equipment-static-pt-buff)
  independently re-derived the exact tautological Aura/Equipment-static-buff
  pattern batch 3 already killed (rule:aura-static-pump,
  rule:equipment-static-pt-buff). Not a parent/hierarchy question — flagged
  here because it's the same underlying "static stat modifier on an
  Aura/Equipment restates what the permanent type already implies" shape
  recurring for the third time; if a schema-pass "recently killed" registry
  gets built, this pattern is the strongest evidence for prioritizing it.
- **D16 new ledger entries (batch-5, Captain, logged per §10 — not
  authored as axes now):**
  - rule:landfall — parent over rule:landfall-gain-life,
    rule:landfall-produces-mana, rule:landfall-self-pump (all batch-5).
  - rule:leaves-battlefield-trigger — parent over
    rule:leaves-battlefield-trigger-create-token (and its own new child,
    see the depth-3 etb entry above under Ratified). Sixth trigger-family
    member alongside etb/attack-trigger/cast-trigger/combat-damage-trigger/death-trigger.
  - rule:combat-damage-trigger — Captain's "combat-damage" normalized to
    the standing trigger-family naming convention; parent over
    rule:combat-damage-triggers-loot, rule:combat-damage-to-player-draws-card,
    and existing combat-damage-* leaves.
  - rule:activated-tap-target — mechanism parent over
    rule:activated-tap-target-creature (and any future
    activated-tap-target-<object-class> siblings — see batch-4's
    "taps a target creature" trigger-context gap entry above, still open).
  - rule:changes-color — parent over rule:changes-color-creature (renamed
    D14) and future rule:changes-color-artifact / rule:changes-color-permanent
    siblings.
  - rule:create-token — parent over the whole create-token-<type> family
    (rule:create-token-creature, rule:create-token-treasure,
    rule:create-token-mana-producing-artifact, and the etb-create-token-<type>
    / leaves-battlefield-trigger-create-token-<type> children above).
    Cross-cuts the trigger-family parents by suffix (addendum-3 §3's
    "second parent dimension... derived from compound SUFFIXES").
  - Draw-second/cast-second prefix scheme (D12): rule:draw-second-card-trigger
    is parent over unprefixed (you draw), opponent- (opponent draws), and
    players- (any player draws) variants, each further split by effect
    suffix (e.g. rule:draw-second-card-trigger-plus1-counter, renamed
    batch-5). rule:cast-second-spell-trigger will mirror the exact same
    prefix × suffix scheme once members exist for it.
  - Restricted-purpose-mana spend-target facet (D13): rule:restricted-purpose-mana
    (renamed from rule:restricted-mana-for-equipment — neither verified
    member actually mentioned Equipment) needs a spend-target facet at
    schema pass: instants/sorceries only (Cormela), creature
    spells/abilities only (Gwenna), and future purposes as members
    accumulate.

- Batch-6 flags:
  - rule:leaves-battlefield-trigger-create-token — the non-creature-token
    parent for rule:leaves-battlefield-trigger-create-token-creature was
    never authored (only the -creature child exists, per D10's
    conservative-reclassification precedent). Zoo Escapees ("When this
    creature leaves the battlefield, create a Mutagen token" — Mutagen is
    explicitly an artifact, not a creature token) currently has no home
    in the codebook; belongs under this not-yet-built parent once it
    exists, mirroring the ratified depth-3 etb scheme.
  - rule:equipment-static-pt-buff / rule:equipment-grants-stat-buff —
    SYNTH free-labeled Rosethorn Halberd and Maul of the Skyclaves with
    these two near-synonymous "rule:"-prefixed slugs even though neither
    exists in the codebook (both cards' auto-attach ETB is already
    correctly captured by rule:etb-auto-attach-to-own-creature). The
    underlying pattern ("Equipped creature gets +X/+Y") is the templated
    baseline function of the Equipment card type, not a differentiating
    mechanic — NOT recommended for promotion even as a parent; flagged
    here only so a future batch doesn't re-propose it from scratch.
  - rule:activated-tap-or-untap — batch-6 QUESTION (see
    TRIAGE-BATCH-6.md): Fatestitcher's "tap or untap another target
    permanent" is broader than rule:activated-tap-or-untap-any-creature's
    declared any-creature scope. If Captain rules to keep the axis
    creature-scoped rather than broaden it in place, this would want a
    rule:activated-tap-or-untap-any-permanent parent to catch
    Fatestitcher and any future non-creature-scoped siblings.

- Batch-7 flags:
  - rule:leaves-battlefield-trigger-create-token-food — **RESOLVED/INSTANTIATED**
    2026-07-30 (section 12 D7): grammar-composable homes are now built
    immediately on first quote-verified member rather than ledger-flagged
    (CODEBOOK-NAMING-GRAMMAR.md section 11 standing rule). Captain-authored
    directly into codebook v0.7 with Brandywine Farmer as its sole member.
    This entry kept for history; not an open item.
  - `defending-player` (CR 506.2) — Captain-attributed parent candidate
    (section 12 D1). The bare token "defender" is now GRAMMAR-banned in
    slugs (collides with the Defender keyword). Parent vs. scope-facet
    classification resolves at the schema pass / CORPUS-PASS-PLAN walk.
    Children as of batch 7: rule:attack-trigger-damage-defending-player,
    rule:attack-trigger-damage-creature-of-defending-player,
    rule:attack-trigger-mass-damage-defending-players-creatures,
    rule:conditional-attack-restriction-by-defending-player-land-type.
  - Free-mechanic untap-lands rider family (CR-adjacent, Urza-block shape)
    — flagged section 12 D5, surfaced by Unwind's "Untap up to three
    lands" (no "target" word, so it doesn't sit in rule:untaps-target-land
    per the CR 601.2c target law). No home built yet; parent-tree
    candidate for the walk.
  - ETB-modal-choice / fully-modal-non-ETB boundary — batch 7 found two
    cards (Analyze the Pollen, Library of Lat-Nam) miscategorized into
    ETB-flavored axes (rule:etb-modal-choice, rule:tutor-to-library-top)
    despite being fully modal SPELLS with no "when this permanent enters"
    trigger at all. Worth a schema-pass check of how many other
    etb-*-flavored axes have non-ETB modal spells miscategorized in the
    same way — this may be a systematic SYNTH confusion between "modal"
    and "ETB-triggered," not a one-off.
  - D4 GRAMMAR-SS9 quote-pull on rule:pay-life-cost-for-effect
    (post-emit, Captain-approved 2026-07-30 in chat;
    experiments/foundry_batch7_pay_life_scrub.py), two members with no
    existing home:
    - Living Airship ("{2}{G}: Regenerate this creature.") — no life
      payment or reference anywhere on the card; likely a stale/erroneous
      original SYNTH match with no salvageable facet. No family proposed.
    - Sangrophage ("At the beginning of your upkeep, tap this creature
      unless you pay 2 life.") — an upkeep-triggered "unless you pay X"
      self-tax shape, not an activated ability. No existing axis covers
      "triggered ability, self-imposed unless-you-pay tax" (rule:rhystic-tax
      is the opponent-facing sibling of this shape); candidate new family
      for the walk: upkeep-trigger-self-tax-unless-paid.
    - Tempest Harvester ("{T}, Pay {E}: Draw a card, then discard a
      card.") — its loot facet is now a real rule:activated-loot member;
      the energy-cost-as-activation-cost facet has no exact home.
      rule:energy-outlet-infinite is the closest existing candidate but
      wasn't confirmed to match precisely — check at the walk rather than
      force it now.
- **rule:evasion parent (Q8.7, walk-ratification 2026-07-31)** — CR
  509.1b–c anchor (a creature can't be declared as a blocker if it can't
  legally block the attacker; blocking restrictions are checked here).
  Job: "this creature is harder to block than a vanilla creature."
  Children = mechanism, parent = job (file header principle): spans the
  Q8 unblockable redesign's families 3–6 --
  rule:innate-unblockable (absolute-innate, self, static); the 3
  unblockable-grant axes (rule:activated-grants-self-unblockable,
  rule:grants-unblockable, rule:grants-unblockable-target -- the
  grants-<keyword> scheme's "unblockable" pseudo-keyword facet, see
  pipeline-repo docs/grammars.json); the new
  rule:cant-be-blocked-<restriction> family (by-color/by-power/
  except-by-count/as-long-as-<state>); and keyword-buckets.json's
  8-keyword evasion bucket (Flying, Menace, Skulk, Fear, Intimidate,
  Shadow, Horsemanship, Landwalk) -- those 8 get NO rule: axis of their
  own (Q8.6, b1 bare-keyword kills), so at schema-pass build time their
  membership comes from the keyword layer directly, not from a
  rule:-namespace child. Not built yet -- ledger entry only, per this
  file's own "nothing here is load-bearing until schema pass" discipline.

## Open tensions (flag, do not silently resolve)

- T1. Company Commander example (batch-3 §1) assigns
  rule:grant-deathtouch-board / rule:attack-trigger-grant-keyword-board —
  but batch-1 Q1 KILLED pure keyword-grant axes as engine-redundant
  (granted_keyword dimension). Schema pass must reconcile: does the
  trigger-context leaf (attack-trigger-grant-keyword-board) escape the
  Q1 redundancy ruling because the engine indexes the grant but not the
  trigger context, or does Q1 stand and the leaf reduces to
  rule:attack-trigger only? Captain rules at schema pass.
- T2. Cantrip predicate refined again (batch-3 §1): draw must occur upon
  resolution (spell effect, ETB, or other immediate means) — activated
  tap-abilities excluded (summoning sickness). Deterministic encoding
  needed in the derivation. CAPTURED in decisions/batch-3.json's
  new_rulings; still needs the actual DET encoding in the derivation
  layer (open, not a doc-tracking gap anymore).
