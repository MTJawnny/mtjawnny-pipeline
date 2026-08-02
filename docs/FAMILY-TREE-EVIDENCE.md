# FAMILY-TREE EVIDENCE — T3-BUILDOUT-PLAYBOOK.md Step 4

Status: EVIDENCE DOCUMENT, not a ruling. This proposes candidate families
WITH evidence and mandatory counter-arguments per family. It does NOT
propose a final ratified tree — Captain writes that himself, using this as
raw material. Every open question below is phrased as a single yes/no
ruling for Captain, not a recommendation to adopt.

Read alongside: `docs/DERIVED-TAG-LAYER-SPEC.md` (family section, v1
derivation set, Lessons 1-3), `docs/T3-BUILDOUT-STEP4-HANDOFF.md` (where
Steps 1-3 landed), `experiments/POKE-PUNCH-LIST.md`,
`experiments/tier_engine.py`'s `SELF_CHECK_PAIRS` / gate-card constants.

## Methodology and evidence sources

Per the playbook's Step 4 instructions, four evidence sources were used,
each labeled per claim below:

1. **[CORPUS]** — Corpus co-occurrence, computed live this session, never
   recalled. A throwaway measurement script,
   `experiments/measure/family_tree_evidence.py` (mtjawnny-pipeline repo,
   NOT wired into `tier_engine.py` scoring), implements all eight v1
   derivation patterns from `DERIVED-TAG-LAYER-SPEC.md` as regexes over
   `composed_full_text` (the same already-normalized, reminder-stripped,
   self-name-substituted text `rule:turn-scoped` itself searches), prints
   each pattern's corpus DF/idf and a fixed-seed 20-card sample (seed
   `20260717`, same convention as `TURN_SCOPED_SAMPLE_SEED`), then computes
   pairwise co-occurrence/conditional-probability between all derived tags
   and cross-references the Scryfall Tagger dump. Run twice; confirmed
   byte-identical (see "Verification" below — a real nondeterminism bug was
   found and fixed in the process, detailed there). Reproduce with
   `python3 experiments/measure/family_tree_evidence.py` from the pipeline
   repo; full output at `experiments/out/measurement/
   family_tree_evidence_report.txt` (gitignored, regenerate to re-check any
   number below).
2. **[TAGGER]** — Tagger taxonomy cross-reference: which Scryfall Tagger
   tags blanket which derived-tag populations, computed by the same script
   (Part 3/4 of its output).
3. **[HISTORY]** — Repo history: punch-list entries, gate constants, and
   change-order rationales already on file that argued function-similarity
   questions relevant to these families. Cited by file:line and date.
4. **[EXEMPLAR]** — Real card panels (8-12 members spanning different
   templating, 3-5 near-misses), read directly off the script's per-tag
   membership lists, not recalled.

**Anti-laundering guard, applied throughout**: wherever Tagger
co-occurrence and corpus/exemplar behavior disagree, corpus behavior and
exemplar cards win. Every family below has at least one argument grounded
in card behavior alone, independent of what Scryfall's own taxonomy says.

## v1 derivation tags measured this session (corpus DF, idf)

| tag | DF | idf | vs DERIVED_QUALIFY_DF_CEILING (172) |
|---|---:|---:|---|
| rule:turn-scoped (shipped, Step 3) | 731 | 3.96 | common — needs a rare co-qualifier |
| rule:grants-keyword | 626 | 4.11 | common |
| rule:cost-reduction | 501 | 4.33 | common |
| rule:prohibits-block | 424 | 4.50 | common |
| rule:pay-tax | 331 | 4.75 | common |
| rule:prohibits-attack | 309 | 4.82 | common |
| rule:uncounterable-self | 117 | 5.79 | rare enough to solo-qualify |
| rule:restricts-activation | 74 | 6.25 | rare enough to solo-qualify |
| rule:cost-increase | 71 | 6.29 | rare enough to solo-qualify |
| rule:restricts-cast | 60 | 6.46 | rare enough to solo-qualify |
| rule:restricts-opponent-cast | 58 | 6.49 | rare enough to solo-qualify |
| rule:grants-uncounterable | 1 | 10.55 | rare enough to solo-qualify |

`rule:restricts-cast` / `rule:restricts-opponent-cast` are Lesson-1
canonicalized (118 total cards: 112 negative-polarity "can't cast..." +
6 positive-polarity "can cast ... only...", zero overlap), then
scope-split via the existing `te.extract_scope()` machinery — no new scope
vocabulary invented. `rule:uncounterable-self` / `rule:grants-uncounterable`
are split by whether the matched sentence says "target spell" (granted) or
not (self). **[CORPUS]**

## Families

---

### Family 1 — cast-interference

**Proposed members**: `rule:restricts-cast`, `rule:restricts-opponent-cast`,
`rule:cost-increase`. (`rule:pay-tax` is evaluated as its own family below,
per the playbook's explicit "tax-effects as distinct from hard restriction"
instruction — see the open question at the end of this family and Family
5's own tension note. `rule:cost-reduction` is excluded by the spec's own
instruction: "reduction is NOT in any interference family.")

**Affirmative argument**: all three axes make it structurally harder for
someone to resolve a spell at all (prevented outright, or priced out of
range) — a Commander player searching "cards that do Grand Abolisher's job"
would reasonably want restriction- and cost-based hosers surfaced together,
even in different words. **[EXEMPLAR]** Dosan the Falling Leaf and City of
Solitude are the spec's own named Lesson-1 victims: they phrase the *same*
restriction as Grand Abolisher positively ("can cast spells only during
their own turns") instead of negatively ("can't cast... during your
turn") — without polarity canonicalization they were invisible to each
other, which is the whole reason this layer exists.

**Counter-argument (mandatory)**: **[CORPUS]** raw co-occurrence between
these three sub-tags is close to zero — `rule:cost-increase` ∩
`rule:restricts-opponent-cast` = 0 cards; `rule:cost-increase` ∩
`rule:restricts-cast` is not even listed in the pairwise table (below the
"any overlap" cutoff). They are near-disjoint *populations*, not just
near-disjoint *text* — the case for merging rests entirely on functional
analogy, not on any corpus signal, which is precisely the situation the
anti-laundering guard warns about. **[TAGGER]** Scryfall's own curators
keep them separate too: `rule:restricts-opponent-cast` is 88% covered by
Tagger's `prevent-cast`, `rule:cost-increase` is 69% covered by
`cost-increaser` — two different Tagger tags with no shared parent found.
**[HISTORY]** `check_godsend_gate` (tier_engine.py:5154, v2.4 gate 1)
already ruled that a card carrying this exact derived tag,
`rule:restricts-opponent-cast` (Godsend: "opponents can't cast spells with
the same name as a card exiled with Godsend"), must NOT rank highly
against Grand Abolisher — its restriction is condition-narrowed
(`CONDITION_PENALTY`), not a real functional peer. An umbrella family
inherits the same laundering risk unless it carries the identical
narrowing discipline.

**Exemplar panel** (8-12, different templating/polarity/scope):
Grand Abolisher (negative, opponent, unconditional, turn-scoped), Dosan
the Falling Leaf (positive, symmetric — the canonicalization flagship),
City of Solitude (positive, symmetric, *also* fires restricts-activation),
Teferi, Time Raveler (positive, "any time they could cast a sorcery" —
functionally single/all_opp), Sphere of Resistance (cost-increase, all
spells, symmetric), Thorn of Amethyst (cost-increase, noncreature-scoped),
Aura of Silence (cost-increase, opponent-scoped, artifact/enchantment
only), Grand Arbiter Augustin IV (cost-increase, opponent-scoped, color
pair), A-Teferi, Time Raveler (the Alchemy rebalance — verified via the
live corpus to carry *different* oracle text than paper Teferi, Time
Raveler: "Your opponents can't cast spells during your turn," an exact
Abolisher-template match paper Teferi does not share).

**Near-miss panel** (3-5, real regex hits Captain may want excluded):
- **Godsend** — condition-narrowed (same-named-card-only); already ruled
  low by `check_godsend_gate`. **[HISTORY]**
- **Good Knight** / **Rock Jockey** — "You can't cast ~ if you're on the
  [team]." fires the negative-polarity regex but is a self-referential
  deckbuilding joke restriction (Un-set-adjacent), not an interference
  effect at all. **[CORPUS]** (verified in the fixed-seed sample)
- **Eidolon of Rhetoric** / **Archon of Emeria** / **High Noon** — "each
  player can't cast more than one spell each turn" is a spell-*count* cap,
  symmetric and self-inclusive, functionally distinct from Grand
  Abolisher's asymmetric turn-lock. Arguably its own
  `rule:spell-count-cap` concept, not this family.
- **Meddling Mage** / **Voidstone Gargoyle** — "Spells with the chosen
  name can't be cast" is a named-card hoser (Pithing-Needle-class), a
  completely different mechanism from a scope/timing restriction despite
  matching the same regex.
- **Trinisphere** — a mana *floor* ("costs less than three... costs
  three"), not an additive increase. **[CORPUS]** Verified: Trinisphere
  fires NONE of the eight v1 derivations (spot-check confirms
  `derived=(none)`) — a genuine miss the current regex doesn't reach, not
  a ruling question, flagged here as a future-amendment candidate per the
  spec's own "grow the set only when a poke shows a concrete miss"
  discipline.

**Open question for Captain**: Scryfall's own taxonomy keeps `prevent-cast`
and `cost-increaser` as separate, unrelated tags, and corpus co-occurrence
between `rule:restricts-cast`/`rule:restricts-opponent-cast` and
`rule:cost-increase` is effectively zero — is `cast-interference`'s basis
purely the functional analogy ("both make casting harder"), and if
ratified, should Tier 3's family-umbrella discount be *lower* for the
cost-increase leg than the restriction legs, to reflect that a cost tax is
almost always payable while a restriction is not?

---

### Family 2 — resolution-protection

**Proposed members** (spec's own draft, `DERIVED-TAG-LAYER-SPEC.md`
Architecture section): `rule:restricts-opponent-cast`, `rule:uncounterable-self`,
with `rule:turn-scoped` as a co-occurring modifier (not a standalone
member — no card in the corpus carries `rule:turn-scoped` as its only
resolution-protection signal; it always rides alongside
`rule:restricts-opponent-cast` for the cards that matter here, e.g. Grand
Abolisher itself).

**Affirmative argument**: both axes serve one Commander-strategic goal —
"my spell resolves as intended, free of opponent interaction" — whether
achieved by denying the opponent the chance to interact at all (Grand
Abolisher) or by making your own key spell immune to their interaction
once cast (Vexing Shusher). A deckbuilder assembling a combo-protection
package plausibly wants both surfaced together. This is the spec's own
named open question: "is rule:uncounterable in the 'protect-your-turn'
family with restricts-opponent-cast — i.e., is Vexing Shusher kin to Grand
Abolisher?"

**Counter-argument (mandatory)**: **[CORPUS]** raw co-occurrence between
`rule:restricts-opponent-cast` and `rule:uncounterable-self` is
essentially zero — 1 shared card out of 58 and 117 members respectively
(jaccard=0.006). **[TAGGER]** confirms the split is real, not an artifact
of the regex: `rule:uncounterable-self` is 100% covered by Tagger's own
`hate-counterspell` tag (117/117) and `rule:restricts-opponent-cast` is
89% covered by Tagger's `silence` tag (via the redundancy table) — two
Scryfall-curated categories with no overlap in each tag's own top-8 Tagger
list. Mechanically the two are asymmetric in relevance: `restricts-
opponent-cast` (Abolisher) is unconditionally live every game, while
`uncounterable-self` (Shusher) only matters if an opponent already holds
a counterspell — a real but narrower, meta-dependent payoff (most
Commander decks run few or no counterspells). **[HISTORY]**
`check_basandra_gate` (tier_engine.py:5213) shows Captain already retired
even the *within-family* Basandra-vs-Myrel ordering question as
"UNGATED... neither ordering is an expectation any longer, both are
defensible" (`RULING-MANIFEST-2026-07-09.md`, Phase 3 rebalance) — a
caution that even confirmed kin can resist a single canonical rank order,
let alone a cross-mechanism merge.

**Exemplar panel**: Grand Abolisher, Myrel, Shield of Argive, Marisi,
Breaker of the Coil (all three `rule:restricts-opponent-cast` +
`rule:turn-scoped`), Silence (`rule:restricts-opponent-cast` only, one-shot
duration — already a known SEPARATE axis: `V22_BASELINE_ABOLISHER_
POSITIONS` / `check_v23_movement_gate` deliberately demote Silence in
Grand Abolisher's Tier 2 ranking despite sharing the tag, because Tier 2's
duration penalty (one-shot vs ongoing) already distinguishes them —
**[HISTORY]** tier_engine.py:922-927 — a distinction Tier 3's tag-only
scoring currently has no equivalent for), Drannith Magistrate, Lavinia,
Azorius Renegade, Vexing Shusher (`rule:uncounterable-self` +
`rule:grants-uncounterable` both — confirmed by this session's own bugfix,
see "Verification" below), Chimil, the Inner Sun, Cavern of Souls
(uncounterable via a granted static ability, not a spell).

**Near-miss panel**:
- **Godsend** — same condition-narrowing issue as Family 1; also fires
  `rule:restricts-opponent-cast`. **[HISTORY]**
- **Void Winnower** — "opponents can't cast spells with even mana values"
  is heavily condition-narrowed (parity-gated); a real member by regex but
  a much softer, deck-composition-dependent restriction than Abolisher's
  unconditional lock.
- **Basandra, Battle Seraph** — fires `rule:restricts-cast` (symmetric,
  NOT opponent-scoped — "Players can't cast spells during combat"), and is
  COMBAT-scoped rather than TURN-scoped (no "turn" phrase, so
  `rule:turn-scoped` never fires on it) — a genuinely different axis the
  v1 set doesn't have its own tag for. **[HISTORY]** its own gate was
  retired from blocking status specifically because both relative
  orderings against Myrel are defensible.
- **Autumn's Veil** — "Spells you control can't be countered *by blue or
  black spells*" is a color-restricted partial protection, not the same
  unconditional self-protection as Vexing Shusher's own first ability.

**Open question for Captain**: is `rule:uncounterable-self` (DF=117,
~0% raw co-occurrence with `rule:restricts-opponent-cast`, 100%
Tagger-redundant with `hate-counterspell`) kin to Grand Abolisher's
resolution-protection family at all, or a functionally distinct axis
(interaction-proofing vs. interaction-prevention) deserving its own
separate family — and if kin, should the family discount differ per leg
to reflect that uncounterable's payoff is conditional on the opponent
holding a counterspell while restricts-opponent-cast's is not?

---

### Family 3 — activation-interference

**Proposed members**: `rule:restricts-activation`. (The spec's draft also
names "activation cost-increase" as a member — **[CORPUS]** measured this
session and found real but very small: a dedicated "costs {N} more to
activate" pattern, distinct from the spell-cost-increase regex, hits only
9 cards corpus-wide — Suppression Field, Eidolon of Obstruction, Gloom's
second ability, Tithe Taker's second clause, and 5 others. This was NOT
built as its own v1 tag this session — it's a genuine, small, measured gap
flagged for a future amendment, not folded in here without its own
ritual.)

**Affirmative argument**: "activated abilities of X can't be activated"
and "players can't activate abilities that aren't mana abilities" both
attack the SAME axis Grand Abolisher's own text explicitly covers
("...or activate abilities of artifacts, creatures, or enchantments") —
this is not an analogy, it's textually adjacent to Abolisher's own
matched fragment.

**Counter-argument (mandatory)**: **[TAGGER]** `rule:restricts-activation`
is 91% covered by Tagger's own `prevent-activation` tag (67/74) — the
highest blanket ratio measured for any v1 tag this session, a strong
redundancy signal. Only 7 of 74 cards (9%) carry the derived tag without
also carrying Tagger's own `prevent-activation` — worth a manual spot
check before ratifying this as a genuinely additive axis rather than a
near-total Tagger reproduction.

**[CORPUS] Cross-family bridge, surfaced by the data, not anticipated by
the spec's draft**: `rule:restricts-activation` co-occurs heavily with
`rule:prohibits-attack` — P(restricts-activation | prohibits-attack) is
only 10%, but P(prohibits-attack | restricts-activation) is 43% (32 of 74
cards) — the classic Pacifism-plus template ("can't attack or block, and
its activated abilities can't be activated": Arrest, Faith's Fetters,
Planar Disruption, Prison Term, Stasis Cocoon, and 27 others). This is a
real, large (32-card) bridge between this family and Family 4
(combat-prohibition) that the spec's draft families don't name — see
Family 4's own near-miss note and the open question below.

**Exemplar panel**: Stony Silence, Cursed Totem, Collector Ouphe
(bare "activated abilities of X can't be activated," no combat clause —
the CLEAN activation-only members), City of Solitude (also
restricts-cast, positive polarity), Interdict (counter-target-ability
shape, not a static lock), Linvala, Keeper of Silence (opponent-scoped:
"activated abilities of creatures your opponents control"), The Immortal
Sun ("Players can't activate planeswalkers' loyalty abilities" — a narrow
sub-type restriction), Word of Command (the only OTHER positive-polarity
hit besides City of Solitude: "can activate mana abilities only if
they're from lands...").

**Near-miss panel**:
- **Arrest, Faith's Fetters, Planar Disruption, Prison Term** (the
  32-card Pacifism-plus bridge above) — these are arguably
  combat-prohibition cards that also happen to shut off activated
  abilities as a secondary clause, not activation-interference cards in
  their own right; membership direction is exactly the open question.
- **Trickbind** — "activated abilities of that permanent can't be
  activated *this turn*" is a one-shot counter-ability effect (Split
  Second-adjacent), not a standing lock like Stony Silence.
- **Black Tulip** / **Djinn of Infinite Deceits** — "You can't activate
  this ability until/during..." is a *self*-restriction on the card's own
  ability, not an interference effect on opponents at all; a clear
  false-positive on the raw regex.

**Open question for Captain**: given the 32-card Pacifism-plus bridge
into `rule:prohibits-attack`, should `activation-interference` and
`combat-prohibition` (Family 4) be siblings under one broader umbrella, or
kept as two families where a card can simply carry both tags
independently (the current, no-umbrella default)?

---

### Family 4 — combat-prohibition

**Proposed members**: `rule:prohibits-attack`, `rule:prohibits-block`.

**Affirmative argument**: both directly answer "how does this card stop a
creature from doing combat math" — the Ghostly Prison / Propaganda /
Pacifism archetype family Commander players already group mentally as
"attack tax and lockdown."

**Counter-argument (mandatory)**: **[CORPUS]** the two sub-tags overlap
only modestly with EACH OTHER (19 of 309/424 cards fire both — e.g.
"can't attack or block" one-line templates), meaning most members are
attack-only OR block-only, not both — a "combat-prohibition" umbrella
would be granting family credit across cards that restrict entirely
different halves of combat. **[TAGGER]** `rule:prohibits-attack`'s top
Tagger tag is `prevent-attack` at only 46% (143/309) — the LOWEST
single-tag coverage of any v1 population measured this session — meaning
the Tagger taxonomy itself doesn't treat "can't attack" as one coherent
bucket either (it splits across `prevent-attack`, `drawback`,
`restricted-attacker`, `removal`, `removal-creature`, `prevent-blocker`,
`pacifism`, none clearing 50%). `rule:prohibits-block` is similarly split
(`prevent-blocker` and `triggered-ability` tied at 46% each).

**[CORPUS] Cross-family bridge, surfaced by the data**: `rule:pay-tax` ∩
`rule:prohibits-attack` = 26 cards (Ghostly Prison, Propaganda, Norn's
Annex, Archangel of Tithes, Windborn Muse, Sphere of Safety, and 20
others) — the "attack tax" archetype is a genuine, clean, real cluster
that currently straddles this family and Family 5 (tax-effects) rather
than belonging cleanly to either. **[TAGGER]** confirms this is a
real Scryfall-recognized shape too: the `tax-attack` Tagger tag (40 cards)
co-fires 55% with `rule:pay-tax` and 68% with `rule:prohibits-attack`;
`tax-block` (7 cards, tiny) co-fires 100% with `rule:pay-tax`.

**Exemplar panel**: Pacifism, Arrest, Encrust (attack+block+activation,
the Family 3 bridge), Ensnaring Bridge (attack-only, power-based
condition, no tax), Bloodghast/Craven Knight-style vanilla "can't block"
downside creatures (block-only, no opponent-facing interference at all —
these are self-restrictions on the card itself, see near-miss below),
Ghostly Prison, Propaganda (the attack-tax hybrid), Champion of Lambholt
("creatures with power less than this creature's power can't block
creatures you control" — a comparative, not absolute, restriction).

**Near-miss panel**:
- **Bloodghast, Craven Knight, Charging Slateback** (and dozens more
  vanilla "This creature can't block.") — a downside on the card ITSELF,
  never an opponent-facing interference effect. **[CORPUS]** These
  dominate `rule:prohibits-block`'s raw DF (424) — a large fraction of the
  population is this self-downside shape, not the Propaganda-style
  opponent-facing lock the family is actually chasing. A real precision
  gap worth flagging, not silently accepted.
- **Ghostly Prison / Propaganda** — arguably tax-effects cards first,
  combat-prohibition second (see Family 5's tension note); listed here
  AND there deliberately, as the concrete case the open question below
  asks about.
- **Rule with an Even Hand** — "You can't attack with an odd number of
  creatures" is a parity/count constraint on the caster's OWN attacks
  (a deckbuilding constraint, self-scoped), not opponent interference.

**Open question for Captain**: should the 26-card "attack tax" cluster
(Ghostly Prison/Propaganda-class, sharing `rule:pay-tax` AND
`rule:prohibits-attack`) be modeled as its own named sub-family bridging
combat-prohibition and tax-effects (a genuine third bucket the corpus
surfaced, not in the spec's original draft), or left to naturally carry
both parent tags with no dedicated umbrella?

---

### Family 5 — tax-effects (as distinct from hard restriction)

**Proposed members**: `rule:pay-tax`, `rule:cost-increase`.

**Affirmative argument**: the playbook explicitly asks this family be
evaluated "as distinct from hard restriction" — i.e., tested against
whether it should be pulled OUT of Family 1's (cast-interference) draft
grouping rather than nested inside it, since a tax is payable and a
restriction is not. Both `rule:pay-tax` (Rhystic Study/Mystic Remora-style
soft counterspells, Ghostly Prison-style attack tax) and
`rule:cost-increase` (Sphere of Resistance-style flat tax) share the
"opponent can still act, just at a cost" shape, structurally softer than
Family 1's restriction axis.

**Counter-argument (mandatory)**: **[CORPUS]** `rule:pay-tax` and
`rule:cost-increase` themselves barely co-occur (1 shared card out of
331/71 members) — **[TAGGER]** confirms these are functionally different
kinds of tax: `rule:pay-tax`'s top Tagger tags are dominated by
`counterspell`/`counterspell-soft` (40%/40%) — i.e. most of this
population is actually the Rhystic-Study soft-counterspell archetype, NOT
the Ghostly-Prison attack-tax archetype the family name evokes at a
glance; only the 26-card intersection with `rule:prohibits-attack`
(Family 4) is the "attack tax" shape. Bundling "counter unless you pay"
and "attack unless you pay" under one flat `tax-effects` label risks
treating two very different Commander-relevant payoffs (card advantage
engine vs. combat lockdown) as one thing.

**Exemplar panel**: Rhystic Study, Mystic Remora (the soft-counterspell
majority shape), Ghostly Prison, Propaganda (the attack-tax minority
shape), Sphere of Resistance, Thorn of Amethyst (flat cost-increase, no
"unless" clause at all — a genuinely different mechanism, opponent has NO
option to avoid the cost, unlike the "pays or X happens" shape), Aura of
Silence (cost-increase, artifact/enchantment-scoped).

**Near-miss panel**:
- **Trinisphere** — mana floor, not additive tax; fires neither v1 tag
  (confirmed `derived=(none)`), a measured miss.
- **Erosion**-style "destroy that land unless that player pays {1} or 1
  life" — an alternative-cost escape hatch on a ONE-SHOT destruction
  effect, not a standing tax; near-miss on the regex's "unless ... pays"
  match.
- **Isolation Cell** — "that player loses 2 life unless they pay {2}" is
  a life-tax variant, not a mana-tax; same regex family, arguably a
  distinct sub-shape.

**Open question for Captain**: `rule:pay-tax`'s own population splits
cleanly by Tagger cross-reference into a soft-counterspell majority
(`counterspell-soft` 97% of a 138-card sub-population) and an attack-tax
minority (the 26-card bridge with Family 4) — should `rule:pay-tax` be
split into two v1 tags (`rule:pay-tax-counter` / `rule:pay-tax-combat`)
before any family ratification, given they clearly do different jobs?

---

## Tagger ↔ rule: redundancy table

Pairwise co-fire rate: for each watched Tagger tag, the count and
percentage of its own membership that also carries each `rule:` tag.
**[CORPUS]/[TAGGER]**, computed by Part 4 of the measurement script.

| Tagger tag | \|Tagger\| | cost-inc | cost-red | grants-kw | pay-tax | proh-atk | proh-blk | restr-act | restr-cast | restr-opp-cast | turn-scoped | uncounter-self |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|
| hate-flash | 19 | 1 (5%) | 0 | 0 | 0 | 0 | 1 (5%) | 2 (11%) | — | 9 (47%) | 12 (63%) | 1 (5%) |
| silence | 27 | 0 | 0 | 0 | 0 | 3 (11%) | 0 | 1 (4%) | 2 (7%) | **24 (89%)** | 9 (33%) | 1 (4%) |
| pacifism | 95 | 0 | 0 | 4 (4%) | 4 (4%) | **78 (82%)** | 5 (5%) | 30 (32%) | 0 | 0 | 1 (1%) | 0 |
| hate-attacker | 366 | 0 | 14 (4%) | 2 (1%) | 3 (1%) | 7 (2%) | 1 (0%) | 0 | 1 (0%) | 2 (1%) | 5 (1%) | 0 |
| hate-counterspell | 156 | 2 (1%) | 5 (3%) | 1 (1%) | 1 (1%) | 0 | 0 | 4 (3%) | 2 (1%) | 2 (1%) | 6 (4%) | **117 (75%)** |
| hate-flashback | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| cost-increaser | 73 | **49 (67%)** | 6 (8%) | 0 | 3 (4%) | 1 (1%) | 0 | 1 (1%) | 0 | 0 | 3 (4%) | 0 |
| tax | 459 | 1 (0%) | 7 (2%) | 0 | 59 (13%) | 3 (1%) | 4 (1%) | 1 (0%) | 1 (0%) | 0 | 14 (3%) | 7 (2%) |
| cast-tax | 17 | 0 | 0 | 0 | **12 (71%)** | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| tax-attack | 40 | 0 | 0 | 0 | 22 (55%) | **27 (68%)** | 1 (2%) | 0 | 0 | 0 | 2 (5%) | 0 |
| tax-block | 7 | 0 | 0 | 0 | **7 (100%)** | 4 (57%) | 3 (43%) | 0 | 0 | 0 | 0 | 0 |
| counterspell | 551 | 4 (1%) | 12 (2%) | 1 (0%) | 134 (24%) | 0 | 1 (0%) | 2 (0%) | 1 (0%) | 4 (1%) | 2 (0%) | 7 (1%) |
| counterspell-soft | 138 | 0 | 4 (3%) | 1 (1%) | **134 (97%)** | 0 | 1 (1%) | 0 | 0 | 0 | 0 | 1 (1%) |

Highest-signal rows (bold): `silence` is 89% redundant with
`restricts-opponent-cast`; `pacifism` is 82% redundant with
`prohibits-attack`; `cost-increaser` is 67% redundant with
`cost-increase`; `hate-counterspell` is 75% redundant with
`uncounterable-self` (and the reverse direction, in Part 3's own table
above, is 100%); `counterspell-soft` is 97% redundant with `pay-tax`
(confirming Family 5's soft-counterspell-majority finding);
`tax-block`'s tiny 7-card population is 100% redundant with `pay-tax`.
None of these numbers alone rules a family in or out — per the guard,
they're inputs to Captain's ruling, weighed against the corpus/exemplar
evidence above wherever the two disagree.

## Verification

Full gate suite / determinism discipline applied to this session's own
new artifact (the measurement script), not to `tier_engine.py` itself —
nothing in this document touches scoring:

- Ran twice; found a real nondeterminism bug on the first diff
  (`Counter.most_common()` tie-breaks depend on Python's per-process
  randomized string-hash set iteration order — two runs produced
  different top-8 Tagger-tag orderings among tied counts). Fixed with an
  explicit `(-count, key)` sort; reran twice more, confirmed byte-identical
  output both times.
- Found and fixed a real classification bug before it could ship: the
  first-match-only paragraph scanner silently dropped a card's SECOND
  qualifying sentence, which mis-classified Vexing Shusher (the spec's own
  named uncounterable-self/granted example) as self-only. Added a
  dedicated all-paragraph scanner for the self/granted split; verified
  Vexing Shusher now correctly carries both `rule:uncounterable-self` AND
  `rule:grants-uncounterable`.
- All card-text claims in this document were read directly from
  `data/raw/oracle-cards.jsonl.gz` this session (via the script's own
  matched-paragraph samples and a separate corpus dump), never recalled.

## What this document does NOT do

Per the playbook: no final family tree is ratified here. Every "proposed
members" list above is a candidate for Captain to accept, reject, split,
or merge. The six open questions (one per family, plus Family 4's
sub-family question) are the concrete rulings this document exists to
solicit.
