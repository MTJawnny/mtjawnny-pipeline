# B-CONSOLIDATION RE-AUDIT PACKET — A12 external checkpoint (2026-08-01)

## Part 0 — YOUR ROLE (read before everything else)

You are an independent auditor. You have NO access to the repository —
everything you need is in this packet. Your job is to find what is wrong,
missing, or self-serving, not to validate it.

**This is the ratified A12 checkpoint.** A multi-session arc is rewriting a
Magic: The Gathering card-tagging codebook. The session under review made
every consolidation DECISION and wrote them to one artifact; the next
session mechanically expands them into ~18,000 database rows, and the one
after that applies those rows. This is the last point at which a wrong
decision is cheap to fix.

**Disclosure of a conflict you must weight:** every artifact here was
produced by an AI assistant (Claude, in Claude Code) — the classification,
the directives governing it, and this packet. The human operator
("Captain") requires an outside check for exactly that reason. Treat every
decision below as a claim to test.

**Second disclosure:** an earlier re-audit was run past Fable 5 — also a
Claude model, therefore same-family and weak against correlated blind
spots. It found a real 820-row arithmetic error and several gate weaknesses,
all since fixed. You are the different-family check that ruling A12 actually
requires.

**What we want from you:**
1. **Rule on the blocking decision in Part 2.** It is a genuine
   contradiction between two ratified rules and it gates everything
   downstream.
2. Attack the 95-node classification (Part 4). Each node becomes a new
   permanent axis or does not. Are the two collision calls right?
3. Attack the promotions (Part 6). Free-lane model output is being promoted
   into curated membership. Is that sound, or lane-discipline laundering?
4. Attack the same-run collapse (Part 7): 44 cases where the model emitted
   the same tag twice for one card, collapsed by a ratified precedence rule.
   Is the rule right, and is discarding the loser's quote a loss of evidence?
5. What will hurt later — at apply time, at corroboration waves, at the
   future schema pass — that is cheap to fix now?
6. Anything the assistant should have surfaced and did not.
7. Rank by severity. Do not pad. If something is sound, one line and move on.

**Output:** ranked findings (severity, claim, evidence from this packet,
recommended change), then a verdict: GO / GO-WITH-FIXES / NO-GO-AS-WRITTEN.

## Part 1 — PRIMER (cold-start context)

The Magic Thesaurus (mtjawnny.com) is a deterministic MTG card-similarity
engine over ~38,233 cards (32,557 after a legality gate). Tier 0–2
similarity is mature; Tier 3 — "same job, different words" — is the open
problem. The "T3 axis foundry" mines it.

`codebook.json` holds ~455 axis records (`rule:enters-tapped`,
`rule:create-token-treasure`, …), each with a definition, a status
(active / killed / merged / renamed / deferred), and card membership.
Membership provenance is load-bearing and has three classes:
**rule-derived** (a ratified regex matched the oracle text; full weight),
**human** (Captain ratified it in batch triage; full weight), and **llm**
(a model proposed it; discounted, never gate-bearing).

A full-corpus model pass ("run 1", M=1, 32,557 cards, $57.63 spent)
produced output in three lanes: `codebook` (matches an existing axis),
`codebook-grammar` (a valid composition under a ratified naming grammar),
and `free` (anything else — discovery only). None of it has been written
into the codebook yet. Doing so is the work being planned.

House discipline: halt loudly on any unexpected shape, never guess, never
silently skip; evidence-quote-or-discard on every per-card assignment;
deterministic byte-identical regeneration; every constant is a ratified
ruling, not a tuning knob.

## Part 2 — THE BLOCKING DECISION (rule on this first)

### A15-VOCAB-01 — 209 rows affected

Two ratified A15 promotion clusters fail validate_slug purely on closed-vocabulary grounds, so R6 (these clusters PROMOTE) and A15 (rows failing validation fall back to discovery) contradict.

Clusters affected:

| cluster | target slug | rows | validator objection |
|---|---|---|---|
| `targeted-destruction-creature` | `rule:targeted-destruction-creature` | 188 | token(s) ['destruction'] not in the closed vocabulary (sections 2,4-8) or ratified glossary -- new vocabulary requires Captain ratification, not silent pass (se |
| `cant-be-blocked-except-by-count` | `rule:cant-be-blocked-except-by-count` | 21 | token(s) ['except'] not in the closed vocabulary (sections 2,4-8) or ratified glossary -- new vocabulary requires Captain ratification, not silent pass (sec.10. |

The contradiction, precisely: ruling **R6/A15** names these clusters
as PROMOTING into codebook membership. The same amendment says each
row must re-validate through the slug validator "exactly like a
grammar-lane label", and that rows failing validation fall back to
discovery. These two clusters fail — but only because their slug
contains a word outside the closed naming vocabulary. So the ratified
outcome and the ratified mechanism disagree.

Options as the session recorded them:

- **Option A — Ratify the missing vocabulary tokens per R9.** All rows promote as R6 intended; the closed vocabulary grows.
- **Option B — Rename the target slugs to compositions using existing ratified vocabulary, then re-validate.** Rows promote under a different slug; no vocabulary change. The new names need Captain approval like any authored slug.
- **Option C — Let A15's fallback stand.** All affected rows go to discovery; R6's promotion of these two clusters is effectively reversed. Stated explicitly because it is a reversal, not a technicality.

**The session's recommendation:** Option B or A, not C. The clusters are large and Captain-reviewed; letting a vocabulary gap silently reverse a ratified promotion is the failure mode the halt-loudly rule exists to prevent. B is narrower than A: it needs no vocabulary expansion.

Scrutinise this specifically. The assistant chose to BLOCK rather than
follow the fallback rule to the letter, on the grounds that silently
demoting 209 Captain-ratified promotions on a vocabulary technicality
is the failure mode the halt-loudly rule exists to prevent. That
reasoning is itself a judgment call, and it is the one most worth
challenging in this packet.

## Part 3 — THE SCHEMA THE PLAN WRITES INTO (ratified amendment A1)

Each axis's membership is a list of member objects; each member carries a
STACK of assertions, one per support event:

```json
{
  "oracle_id": "<uuid>",
  "tier": "provisional",
  "assertions": [
    {
      "class": "human",
      "source_ref": "batch-3",
      "quote": "...",
      "corpus_ref": "2026-07-18",
      "evidence_status": "quoted"
    },
    {
      "class": "llm",
      "source_ref": "run1",
      "original_lane": "free",
      "effective_lane": "codebook-grammar",
      "promotion_reason": "canonical-form-matches-ratified-grammar",
      "quote": "...",
      "corpus_ref": "2026-07-04",
      "evidence_status": "quoted"
    }
  ]
}
```

Rules: one member record per (axis, oracle_id); assertions append-merge and
are never overwritten; a duplicate `(class, source_ref)` HALTS; member-level
`tier` is present **iff** every assertion is llm-class (any human or
rule-derived assertion means full weight, so a consensus tier is moot).
Deterministic order: members by oracle_id, assertions by (class, source_ref).

The codebook was migrated to this shape in a prior session: 7,699 existing
rows backfilled with one assertion each (3,697 rule-derived, 4,002 human),
membership provably unchanged, independently verified.

## Part 4 — THE 95-NODE CLASSIFICATION (AG-COUNT-01)

Each of these is a grammar-valid composition the model proposed that has no
existing axis. Classifying one `instantiate` creates a new permanent axis.

| category | count |
|---|---|
| instantiate | 93 |
| join-existing | 0 |
| redirect | 0 |
| report-only | 0 |
| collision-killed | 1 |
| collision-renamed | 1 |

The two collisions — the cases where a proposed node hits an axis that
already exists under a non-active status:

**`rule:draw-second-card-trigger-token`** — collision-renamed, action `report-only`, 1 member(s)

> collides with a RENAMED shell (renamed_to='rule:draw-second-card-trigger-plus1-counter') that still holds 2 legacy audit row(s). R7 makes this a REPORT ROW for Captain: the node's payoff sense and the rename target's sense differ, and instantiating would overwrite retained audit rows.

> - `c566317e-cd82-46c1-b506-f41256d815f6` — evidence: 'Flurry — Whenever you cast your second spell each turn, create a 1/1 white Bird creature token with flying.'

**`rule:grants-haste`** — collision-killed, action `redirect`, target `rule:temporary-keyword-grant`, 1 member(s)

> collides with a KILLED axis. R7/A7: bare unscoped grants are engine-redundant and stay killed; the member routes to rule:temporary-keyword-grant per the ratified b4-D4 standing rule (A10).

> - `f267fb54-1881-464c-81af-9e03c3f3b41d` — evidence: 'It gains lifelink and haste until end of turn.'

### All 93 instantiations — summary

| slug | members | definition |
|---|---|---|
| `rule:activated-counter-target-enchantment-spell` | 1 | An activated ability, paid with mana, counters a target enchantment spell specifically. |
| `rule:activated-create-token-creature` | 2 | An activated ability, paid with mana and tapping, creates a creature token. |
| `rule:activated-create-token-treasure` | 3 | An activated ability, paid by tapping, creates a Treasure token. |
| `rule:activated-tap-any-creature` | 5 | An activated ability, paid with mana and removing accumulated counters, taps multiple target creatures. |
| `rule:activated-tap-any-permanent` | 2 | An activated ability taps a target permanent regardless of controller, gated behind a land-count condition. |
| `rule:activated-tap-or-untap-any-artifact` | 5 | An effect untaps all artifacts, not restricted by controller. |
| `rule:activated-tap-or-untap-opponent-artifact` | 1 | An activated ability lets the controller choose to tap or untap a target artifact controlled by an opponent. |
| `rule:activated-tap-or-untap-opponent-creature` | 6 | An activated ability that requires tapping two Humans plus mana to tap a target creature an opponent controls |
| `rule:activated-tap-or-untap-opponent-permanent` | 2 | An ETB effect taps a target artifact or creature an opponent controls. |
| `rule:activated-tap-or-untap-own-artifact` | 2 | A triggered ability lets its controller untap a target artifact. |
| `rule:activated-tap-or-untap-own-creature` | 6 | A loyalty ability untaps up to two target creatures the controller controls. |
| `rule:activated-tap-or-untap-own-land` | 1 | An activated ability untaps target lands the controller controls. |
| `rule:activated-tap-or-untap-own-permanent` | 9 | A loyalty ability untaps up to two target lands, a permanent class beyond creatures. |
| `rule:activated-tap-or-untap-permanent` | 2 | An ability lets the controller untap a target permanent, not restricted to creatures. |
| `rule:activated-tap-target-creature-damage` | 1 | An activated ability taps the source to deal damage to a target creature involved in combat. |
| `rule:activated-tap-target-creature-restricted-flying` | 1 | An activated ability that taps the source to deal damage to a target creature restricted to those with flying. |
| `rule:attack-trigger-create-token-creature` | 1 | Whenever the equipped creature attacks, it creates a creature token as a byproduct of combat. |
| `rule:attack-trigger-create-token-food` | 1 | Whenever qualifying creatures attack a player, create a Food token as a byproduct. |
| `rule:attack-trigger-create-token-lander` | 1 | Whenever the permanent attacks, it creates a Lander token as a byproduct of combat. |
| `rule:attack-trigger-create-token-treasure` | 3 | Whenever a creature with menace the controller controls attacks, create a Treasure token. |
| `rule:attack-trigger-create-token-treasure-conditional` | 1 | An attack trigger conditionally creates Treasure tokens if a power threshold is met. |
| `rule:cant-be-blocked-by-power` | 44 | The creature cannot be blocked by creatures whose power is at or below a specified threshold. |
| `rule:cast-from-exile-restricted-type-and-value` | 1 | Allows casting spells directly from exile without paying mana cost, restricted to a card type and mana value threshold. |
| `rule:cast-second-spell-trigger-create-token` | 1 | An ability triggers when a player casts their second spell in a turn, creating a creature token as the payoff. |
| `rule:combat-damage-to-player-create-token-food` | 1 | Whenever the creature deals combat damage to a player, its controller creates a Food token. |
| `rule:combat-trigger-create-token-creature` | 1 | At the beginning of combat on the controller's turn, create a creature token. |
| `rule:create-token-blood` | 16 | Creates a Blood token as part of the spell's effect. |
| `rule:create-token-clue` | 40 | Creates a Clue token as a byproduct of another triggered action. |
| `rule:create-token-food` | 57 | An attack-triggered ability creates a Food token for each player attacked. |
| `rule:create-token-gold` | 3 | Combat with the enchanted player triggers creation of a Gold token, a mana-fixing artifact reward. |
| `rule:create-token-lander` | 8 | Creates a Lander token as a byproduct of another effect. |
| `rule:create-token-mutagen` | 7 | Whenever this creature deals combat damage to a player, create a Mutagen token. |
| `rule:create-token-powerstone` | 17 | Creates a Powerstone token as an effect. |
| `rule:death-trigger-create-token-clue` | 2 | When this permanent dies, it creates a Clue token. |
| `rule:death-trigger-create-token-creature` | 2 | When this permanent dies, it creates one or more creature tokens. |
| `rule:death-trigger-create-token-treasure` | 2 | When this permanent dies, it creates a Treasure token. |
| `rule:draw-second-card-trigger-pump-vigilance` | 1 | An ability triggers specifically when the controller draws their second card in a turn, granting a temporary buff and keyword. |
| `rule:draw-second-card-trigger-token-flying` | 1 | An ability triggers specifically when the controller casts their second spell each turn, producing a flying creature token as the reward. |
| `rule:etb-create-token-blood` | 6 | When the permanent enters the battlefield, it creates Blood tokens. |
| `rule:etb-create-token-clue` | 9 | When the permanent enters the battlefield, conditional on a stated raid condition, it creates a Clue token. |
| `rule:etb-create-token-conditional` | 1 | When the permanent enters the battlefield, it creates a token only if a stated condition (opponent having more lands) is met. |
| `rule:etb-create-token-food-conditional` | 2 | When the permanent enters the battlefield, it creates a Food token only if a stated condition (failing to find/put a card into hand) is met. |
| `rule:etb-create-token-gold` | 1 | A saga chapter creates a Gold token. |
| `rule:etb-create-token-lander` | 6 | When the permanent enters the battlefield, it creates a Lander token that can be sacrificed to fetch a basic land. |
| `rule:etb-create-token-mana-producing-artifact` | 14 | Whenever the controller discards one or more artifact cards, create a tapped mana-producing artifact token, limited to once per turn. |
| `rule:etb-create-token-powerstone` | 3 | When the permanent enters the battlefield, it creates a Powerstone token |
| `rule:etb-create-token-treasure` | 34 | When the permanent enters the battlefield, it creates a Treasure token. |
| `rule:etb-create-token-treasure-conditional` | 1 | When the permanent enters, it creates a Treasure token only if a stated condition (failure of another effect) is met. |
| `rule:etb-create-token-with-x-counters` | 8 | The permanent enters the battlefield carrying a number of +1/+1 counters equal to X paid when casting. |
| `rule:grants-attack-trigger-create-token-food` | 1 | An Aura grants the enchanted creature a new attack-triggered ability that creates a Food token. |
| `rule:grants-combat-damage-create-token-blood` | 1 | Equipment grants the equipped creature an ability that creates a Blood token whenever it deals combat damage. |
| `rule:grants-counter-tribal-static` | 1 | A triggered ability places +1/+1 counters on all creatures the controller controls sharing a specific creature type. |
| `rule:grants-flying-haste-static-target` | 1 | Equipped creature gains flying and haste along with a stat boost as a static grant from the Equipment. |
| `rule:grants-flying-static-target` | 1 | A static ability grants the flying keyword to the equipped/attached creature. |
| `rule:grants-flying-target-static` | 3 | An Aura grants the enchanted creature flying as a static ability. |
| `rule:grants-haste-static-target` | 1 | An Aura grants the enchanted creature haste as a static ability. |
| `rule:grants-lifelink-equip` | 1 | Equipment grants the equipped creature a permanent stat boost and lifelink while attached. |
| `rule:grants-lifelink-target-creature-token` | 1 | Creates a creature token that has an evergreen keyword ability as part of its creation. |
| `rule:grants-menace-conditional-tribal` | 1 | A static ability grants menace to the equipped creature only while it is a specified creature type. |
| `rule:grants-menace-static-own-tribal-condition` | 1 | Grants itself menace as long as a tribal condition among the controller's board is met. |
| `rule:grants-ward-sacrifice-food-static` | 1 | A static ability grants ward to the source, paid by sacrificing a Food. |
| `rule:leaves-battlefield-trigger-create-token-blood` | 1 | When this creature dies, it creates a Blood token. |
| `rule:leaves-battlefield-trigger-create-token-clue` | 1 | When this permanent dies, it creates a Clue token. |
| `rule:leaves-battlefield-trigger-create-token-treasure` | 1 | Whenever the permanent leaves the battlefield via dying, it creates a Treasure token. |
| `rule:scales-mana-by-count-clue` | 1 | An activated mana ability produces mana scaled by the number of Clue permanents the controller controls. |
| `rule:targeted-bounce-artifact` | 2 | Returns a target artifact to its owner's hand. |
| `rule:targeted-bounce-artifact-or-enchantment` | 1 | When the permanent enters the battlefield, it returns a target artifact or enchantment to its owner's hand. |
| `rule:targeted-bounce-enchantment` | 1 | Returns a target enchantment to the top of its owner's library rather than to hand, functioning as tempo-based removal. |
| `rule:targeted-bounce-nonland` | 1 | Returns a target nonland permanent to its owner's hand. |
| `rule:targeted-bounce-permanent` | 21 | An instant returns a target nonland permanent to its owner's hand. |
| `rule:targeted-counter-sorcery` | 1 | Counters a target sorcery spell specifically. |
| `rule:targeted-counter-spell` | 1 | Counters a target spell restricted by a specific mana-value condition. |
| `rule:targeted-damage-any-target` | 3 | An activated ability that sacrifices the source land to deal a fixed amount of damage to any target, gated by a graveyard-size threshold. |
| `rule:targeted-damage-creature` | 44 | A spell deals damage to a target creature (or planeswalker) as part of its effect. |
| `rule:targeted-damage-player` | 29 | Causes a target player to lose a fixed amount of life, functioning like direct damage to a player. |
| `rule:targeted-debuff-creature` | 1 | An activated ability that costs sacrificing a creature to reduce a target creature's power and toughness until end of turn. |
| `rule:targeted-discard-player` | 9 | Forces a target player to discard a card from their hand. |
| `rule:targeted-exile-artifact` | 7 | The spell exiles two target artifacts. |
| `rule:targeted-exile-artifact-or-creature` | 1 | A loyalty ability exiles a target artifact or creature permanent. |
| `rule:targeted-exile-artifact-or-enchantment` | 11 | Exiles a target artifact or enchantment as removal. |
| `rule:targeted-exile-creature` | 68 | Exiles a target creature as a removal effect. |
| `rule:targeted-exile-enchantment` | 5 | Exiles a target enchantment as a modal choice. |
| `rule:targeted-exile-graveyard-card` | 2 | Exiles a target card from any graveyard. |
| `rule:targeted-exile-land` | 4 | Exiles a target land, removing it from the game. |
| `rule:targeted-exile-nonland-permanent` | 1 | Exiles a target nonland permanent. |
| `rule:targeted-exile-permanent` | 17 | Exiles a target permanent an opponent controls, restricted by a mana value threshold. |
| `rule:targeted-exile-player` | 1 | Exiles a target opponent's entire graveyard as a single instant effect. |
| `rule:targeted-exile-player-graveyard` | 2 | Exiles a target player's entire graveyard as one modal option. |
| `rule:targeted-mill-player` | 1 | An ETB effect mills a target opponent's library for a fixed number of cards. |
| `rule:targeted-tap-artifact-creature` | 1 | A spell taps a target artifact or creature as a removal/disruption effect. |
| `rule:targeted-tap-creature` | 5 | Taps one or more target creatures as a removal or combat disruption effect. |
| `rule:targeted-tutor-library-to-hand-activated` | 1 | An activated ability lets the controller search their library for any card and put it into hand. |
| `rule:targeted-tutor-to-library-top-creature` | 1 | Searches the library for a creature card and places it on top of the library rather than into hand. |

### All 93 instantiations — full member evidence

Every card that would join each new axis, with the oracle-text clause the
model cited. This is the evidence for whether the axis deserves to exist at
all: a node whose members do not share a mechanism is a bad axis regardless
of how well-formed its name is.

**`rule:activated-counter-target-enchantment-spell`** (1 members) — An activated ability, paid with mana, counters a target enchantment spell specifically.

- '{3}{U}{U}: Counter target enchantment spell.'

**`rule:activated-create-token-creature`** (2 members) — An activated ability, paid with mana and tapping, creates a creature token.

- '{2}, {T}: Create a 1/1 red Phyrexian Goblin creature token.'
- '{4}, {T}: Create a 2/2 colorless Shapeshifter creature token with changeling.'

**`rule:activated-create-token-treasure`** (3 members) — An activated ability, paid by tapping, creates a Treasure token.

- '{T}: Create a Treasure token.'
- '{T}: Create a Treasure token.'
- '{T}: Create a Treasure token.'

**`rule:activated-tap-any-creature`** (5 members) — An activated ability, paid with mana and removing accumulated counters, taps multiple target creatures.

- 'When this creature enters, tap up to two target creatures.'
- 'Tap up to two target creatures.'
- 'Tap up to two target creatures.'
- '{1}, Remove X ki counters from this creature: Tap X target creatures.'
- '{4}, {T}: Tap target creature.'

**`rule:activated-tap-any-permanent`** (2 members) — An activated ability taps a target permanent regardless of controller, gated behind a land-count condition.

- '{T}: Tap target artifact, creature, or land.'
- '{T}: Tap target permanent. Activate only if you control eight or more lands.'

**`rule:activated-tap-or-untap-any-artifact`** (5 members) — An effect untaps all artifacts, not restricted by controller.

- '{T}: Create a 2/2 colorless Pincher creature token.'
- 'Untap up to four target artifacts and/or creatures.'
- 'Untap all artifacts.'
- '{X}, {T}: Tap X target noncreature artifacts.\n{X}, {T}: Untap X target noncreature artifacts.'
- '{3}, {T}: Untap target artifact.'

**`rule:activated-tap-or-untap-opponent-artifact`** (1 members) — An activated ability lets the controller choose to tap or untap a target artifact controlled by an opponent.

- '{T}: You may tap or untap target artifact an opponent controls.'

**`rule:activated-tap-or-untap-opponent-creature`** (6 members) — An activated ability that requires tapping two Humans plus mana to tap a target creature an opponent controls

- "Tap target creature you don't control."
- '{2}, Tap two untapped Humans you control: Tap target creature an opponent controls.'
- "Untap target creature you don't control."
- 'Tap one or two target creatures an opponent controls.'
- 'Tap all creatures target opponent controls.'
- 'Tap up to one target creature defending player controls.'

**`rule:activated-tap-or-untap-opponent-permanent`** (2 members) — An ETB effect taps a target artifact or creature an opponent controls.

- 'When Omega enters, for each opponent, tap up to one target nonland permanent that opponent controls.'
- 'When this creature enters, tap target artifact or creature an opponent controls.'

**`rule:activated-tap-or-untap-own-artifact`** (2 members) — A triggered ability lets its controller untap a target artifact.

- 'Whenever this creature or another artifact creature dies, you may untap target artifact.'
- '+1: Untap up to two target artifacts.'

**`rule:activated-tap-or-untap-own-creature`** (6 members) — A loyalty ability untaps up to two target creatures the controller controls.

- '{1}, Sacrifice another creature: Untap this creature.'
- 'Tap an untapped creature you control: Untap target basic land.'
- 'Untap up to two target creatures.'
- '+2: Untap up to two target creatures and up to two target lands.'
- '{T}, Tap an untapped creature you control: Add one mana of any color.'
- '{3}: You may tap or untap equipped creature.'

**`rule:activated-tap-or-untap-own-land`** (1 members) — An activated ability untaps target lands the controller controls.

- '{T}: Untap two target lands.'

**`rule:activated-tap-or-untap-own-permanent`** (9 members) — A loyalty ability untaps up to two target lands, a permanent class beyond creatures.

- 'Check Map — Untap up to two target lands.'
- '{X}, {T}: Untap X target lands.'
- '{T}: Create Voja, a legendary 2/2 green and white Wolf creature token.'
- '{T}: Untap two other target permanents.'
- 'Untap target land you control.'
- '{1}, {T}: Untap another target creature or land you control.'
- '+1: Untap target Mountain.'
- '+2: Untap up to two target creatures and up to two target lands.'
- '{T}: Attach target Aura or Equipment you control to target creature you control.'

**`rule:activated-tap-or-untap-permanent`** (2 members) — An ability lets the controller untap a target permanent, not restricted to creatures.

- 'untap target permanent'
- 'You may tap or untap target permanent.'

**`rule:activated-tap-target-creature-damage`** (1 members) — An activated ability taps the source to deal damage to a target creature involved in combat.

- '{T}: Lady Caleria deals 3 damage to target attacking or blocking creature.'

**`rule:activated-tap-target-creature-restricted-flying`** (1 members) — An activated ability that taps the source to deal damage to a target creature restricted to those with flying.

- '{T}: This creature deals 1 damage to target creature with flying.'

**`rule:attack-trigger-create-token-creature`** (1 members) — Whenever the equipped creature attacks, it creates a creature token as a byproduct of combat.

- 'Whenever equipped creature attacks, create a 1/1 colorless Phyrexian Mite artifact creature token with toxic 1 and "This token can\'t block."'

**`rule:attack-trigger-create-token-food`** (1 members) — Whenever qualifying creatures attack a player, create a Food token as a byproduct.

- 'Whenever one or more Halflings you control attack a player, create a Food token.'

**`rule:attack-trigger-create-token-lander`** (1 members) — Whenever the permanent attacks, it creates a Lander token as a byproduct of combat.

- 'Whenever you attack, create a Lander token.'

**`rule:attack-trigger-create-token-treasure`** (3 members) — Whenever a creature with menace the controller controls attacks, create a Treasure token.

- 'Whenever this Vehicle attacks, create a Treasure token.'
- 'Whenever enchanted creature attacks, you create a Treasure token.'
- 'Whenever a creature you control with menace attacks, create a Treasure token.'

**`rule:attack-trigger-create-token-treasure-conditional`** (1 members) — An attack trigger conditionally creates Treasure tokens if a power threshold is met.

- 'Then if Cloud has power 7 or greater, create two Treasure tokens.'

**`rule:cant-be-blocked-by-power`** (44 members) — The creature cannot be blocked by creatures whose power is at or below a specified threshold.

- "Lydia Frye can't be blocked by creatures with power 3 or greater."
- "Ghost of Ramirez DePietro can't be blocked by creatures with toughness 3 or greater."
- "This creature can't be blocked by creatures with power 2 or less."
- "Creatures with power less than this creature's power can't block it."
- "This creature can't be blocked by creatures with power 2 or less."
- "This creature can't be blocked by creatures with power 2 or less."
- "This creature can't be blocked by creatures with greater power."
- "This Vehicle can't be blocked by creatures with power 2 or less."
- "This creature can't be blocked by creatures with power 2 or less."
- "This creature can't be blocked by creatures with power 2 or less."
- "Enchanted creature can't be blocked by creatures with power 3 or greater."
- "This creature can't be blocked by creatures with power 2 or less."
- "This creature can't be blocked by creatures with power 2 or less."
- "Daxos can't be blocked by creatures with power 3 or greater."
- "Creatures with power less than this creature's power can't block it."
- "This creature can't be blocked by creatures with power 2 or less."
- "This creature can't be blocked by creatures with power 2 or less."
- "This creature can't be blocked by creatures with power 3 or greater."
- "This creature can't be blocked by creatures with power 3 or greater."
- "This creature can't be blocked by creatures with power 2 or greater."
- "Equipped creature can't be blocked as long as its power is 3 or less."
- "This creature can't be blocked by creatures with power 2 or less."
- "This creature can't be blocked by creatures with power 2 or greater as long as defending player controls a snow land."
- "This creature can't be blocked by creatures with power 2 or less."
- "it gets +1/+1 until end of turn and can't be blocked by creatures with power 2 or less this turn"
- "can't be blocked by creatures with power 2 or less"
- "Enchanted creature gets +2/+0 and can't be blocked."
- "This creature can't be blocked by creatures with power 2 or greater."
- "Locke can't be blocked by creatures with greater power."
- "This creature can't be blocked by creatures with power 2 or less."
- "Stature can't be blocked if her power is 1 or less."
- "Legolas can't be blocked by creatures with power 2 or less."
- "Equipped creature can't be blocked by creatures with power 4 or greater."
- "This creature can't be blocked by creatures with power 2 or less."
- "It can't be blocked by creatures with power 3 or greater this turn."
- "This creature can't be blocked by creatures with power 4 or greater."
- "This creature can't be blocked by creatures with power 2 or less."
- "{3}, {T}: Target creature with power 3 or less can't be blocked this turn."
- "This creature can't be blocked by creatures with power 2 or less."
- "Ant-Man can't be blocked by creatures with greater power."
- "Equipped creature gets +3/+3 and can't be blocked by creatures with power 3 or less."
- "That creature can't be blocked by creatures with power 2 or less this turn."
- "This creature can't be blocked by creatures with power 2 or less."
- "This creature can't be blocked by creatures with power 2 or less."

**`rule:cast-from-exile-restricted-type-and-value`** (1 members) — Allows casting spells directly from exile without paying mana cost, restricted to a card type and mana value threshold.

- 'You may cast up to two sorcery spells with mana value 3 or less from among them without paying their mana costs.'

**`rule:cast-second-spell-trigger-create-token`** (1 members) — An ability triggers when a player casts their second spell in a turn, creating a creature token as the payoff.

- 'Whenever a player casts their second spell during their turn, you create a 2/2 white Knight creature token.'

**`rule:combat-damage-to-player-create-token-food`** (1 members) — Whenever the creature deals combat damage to a player, its controller creates a Food token.

- 'Whenever this creature deals combat damage to a player, create a Food token.'

**`rule:combat-trigger-create-token-creature`** (1 members) — At the beginning of combat on the controller's turn, create a creature token.

- 'At the beginning of combat on your turn, create a 1/1 green and white Kithkin creature token.'

**`rule:create-token-blood`** (16 members) — Creates a Blood token as part of the spell's effect.

- 'Create two Blood tokens.'
- 'Whenever Anje and/or one or more other Vampires you control enter, create a Blood token.'
- 'Create a number of Blood tokens equal to the amount of excess damage dealt to that creature this way.'
- 'Create a Blood token.'
- 'Whenever one or more Vampires you control attack, create a Blood token.'
- 'Whenever this creature deals combat damage to a player, create a Blood token.'
- 'Create two Blood tokens.'
- 'Create a Blood token.'
- 'Whenever this creature deals combat damage to a player, create a Blood token.'
- 'Create a Blood token.'
- 'then create a Blood token. (It\'s an artifact with "{1}, {T}, Discard a card, Sacrifice this token: Draw a card.")'
- 'Create a Blood token.'
- 'Whenever a creature an opponent controls dies, you create a Blood token.'
- 'Create a Blood token.'
- 'Create a Blood token.'
- 'Create a Blood token.'

**`rule:create-token-clue`** (40 members) — Creates a Clue token as a byproduct of another triggered action.

- 'Investigate. (Create a Clue token. It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- '{1}, Sacrifice another creature: Create a Clue token.'
- 'Create a Clue token. (It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- 'Investigate, then target creature gets +1/+1 until end of turn for each Clue you control.'
- 'Create a Clue token. (It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- 'If you controlled it, investigate.'
- 'Investigate. (Create a Clue token. It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- "create X Clue tokens, where X is that card's mana value"
- 'You create a Clue token. (It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- 'Draw two cards and create a Map token.'
- 'create a Clue token and a Food token'
- 'Investigate. (Create a Clue token. It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- '{4}, {T}: Investigate. (Create a Clue token. It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- 'If it was tapped, create a Map token.'
- 'Investigate. If this spell was cast from a graveyard, investigate twice instead.'
- 'Create a Clue token. (It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- 'Whenever a nontoken creature you control dies, investigate.'
- 'If it was dealt damage this turn, create a Clue token.'
- '{3}, {T}: Investigate. (Create a Clue token. It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- 'Investigate. (Create a Clue token. It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- '{4}, {T}: Investigate. (Create a Clue token. It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- 'Investigate. (Create a Clue token. It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- '{4}, {T}: Investigate. (Create a Clue token. It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- '{4}, {T}: Investigate. (Create a Clue token. It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- 'Create a Clue token. (It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- '{4}, {T}: Investigate. (Create a Clue token. It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- 'Investigate three times. (To investigate, create a Clue token. It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- 'Investigate. (Create a Clue token. It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- 'Investigate. (Create a Clue token. It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- 'Investigate. (Create a Clue token. It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- 'Investigate. (Create a Clue token.'
- 'create a Clue token'
- 'When this creature dies, create a Clue token.'
- 'Investigate. (Create a Clue token. It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- 'Whenever this creature is dealt 3 or more damage, investigate.'
- 'Investigate.'
- 'Investigate. (Create a Clue token. It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- '{4}, {T}: Investigate. (Create a colorless Clue artifact token with "{2}, Sacrifice this artifact: Draw a card.")'
- 'Whenever you attack, investigate. (Create a Clue token. It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- 'Target player investigates.'

**`rule:create-token-food`** (57 members) — An attack-triggered ability creates a Food token for each player attacked.

- 'If you control a Squirrel or returned a Squirrel card to your hand this way, create a Food token.'
- 'Create a Food token.'
- "If it's your turn, create a Food token."
- 'At the beginning of combat on your turn, create a Food token.'
- 'Whenever you cast a spell with mana value 5 or greater, create a Food token.'
- 'Create a Food token for each creature sacrificed this way.'
- 'II — Draw a card. Create a Food token.'
- 'Create a Food token.'
- 'Create a Food token.'
- 'Adamant — If at least three black mana was spent to cast this spell, create a Food token.'
- 'When this creature dies and when you discard this card, create a Food token.'
- '{T}, Discard a card: Create a Food token.'
- 'Create a Food token.'
- 'Otherwise, create three Food tokens.'
- 'Whenever you cast a Cat, Dog, or Hero spell, create a Food token.'
- 'Create a Food token.'
- '{1}, {T}: Create a Food token.'
- 'create a Clue token and a Food token'
- 'Create a Food token.'
- 'Create a Food token.'
- 'Create a Food token.'
- 'If you do, they create a Food token before its other effects.'
- 'Whenever this creature attacks or blocks, create a Food token.'
- 'If its mana value was 4 or less, create a Food token.'
- '+2: Create a Food token.'
- 'Create a Food token.'
- 'Create a Food token and a 1/1 white Human creature token'
- '{1}, {T}: Create a Food token.'
- 'Create a 1/1 white Human Soldier creature token and a Food token.'
- 'Whenever you attack, you create a Food token for each player being attacked.'
- 'Mill three cards, then create a Food token.'
- 'Whenever this land attacks, create a Food token and exile up to one target card from a graveyard.'
- 'Sacrifice a creature: Create a Food token.'
- 'Create a Food token.'
- '{1}{G}, {T}, Tap an untapped creature you control: Create a Food token.'
- 'Create a Food token.'
- 'Then create a Food token for each creature you control.'
- 'Whenever equipped creature deals combat damage to a creature, create a Food token.'
- 'create a Food token or a Treasure token'
- 'Whenever this creature deals combat damage to a player, create a Food token.'
- 'create a Food token and transform this enchantment'
- 'Create a Food token.'
- 'Create a Food token.'
- 'Create a Food token. (It\'s an artifact with "{2}, {T}, Sacrifice this token: You gain 3 life.")'
- 'Create a 1/1 white Human creature token and a Food token.'
- 'When this creature dies, create a Food token.'
- 'Draw a card, then create a Food token.'
- 'Adamant — If at least three blue mana was spent to cast this spell, create a Food token.'
- 'Create a Food token. (It\'s an artifact with "{2}, {T}, Sacrifice this token: You gain 3 life.")'
- 'Create a Food token.'
- 'Create a Food token.'
- 'Create a Food token.'
- 'Create a Food token.'
- 'Create a Food token.'
- 'You create three Food tokens.'
- 'Fancy Lads Snack Cakes — Create a Food token.'
- 'Create a Food token.'

**`rule:create-token-gold`** (3 members) — Combat with the enchanted player triggers creation of a Gold token, a mana-fixing artifact reward.

- 'create a Gold token. (It\'s an artifact with "Sacrifice this token: Add one mana of any color.")'
- 'Create a Gold token.'
- 'Whenever enchanted player is attacked, create a Gold token.'

**`rule:create-token-lander`** (8 members) — Creates a Lander token as a byproduct of another effect.

- 'Create a Lander token.'
- 'Whenever Landlore Navigator attacks, create a Map token.'
- 'Create a Lander token.'
- 'Then create a Lander token.'
- 'If they do, you create a Lander token.'
- 'Create a Lander token. (It\'s an artifact with "{2}, {T}, Sacrifice this token: Search your library for a basic land card, put it onto the battlefield tapped, then shuffle.")'
- 'When this creature dies, create a Lander token.'
- 'create a Lander token'

**`rule:create-token-mutagen`** (7 members) — Whenever this creature deals combat damage to a player, create a Mutagen token.

- 'Whenever a player casts an artifact, instant, or sorcery spell, you create a Mutagen token.'
- 'Whenever a player casts a creature spell, you create a Mutagen token.'
- 'You create a Mutagen token.'
- 'Create a Mutagen token.'
- 'Whenever this creature deals combat damage to a player, create a Mutagen token.'
- 'Create a Mutagen token.'
- 'You create a Mutagen token for each creature dealt damage this way.'

**`rule:create-token-powerstone`** (17 members) — Creates a Powerstone token as an effect.

- '{3}, {T}: Create a tapped Powerstone token.'
- 'Create a tapped Powerstone token.'
- 'Create two tapped Powerstone tokens.'
- 'Create two tapped Powerstone tokens.'
- 'Create a tapped Powerstone token.'
- 'Create a tapped Powerstone token.'
- 'create a tapped Powerstone token'
- 'Create a tapped Powerstone token.'
- 'Create a tapped Powerstone token.'
- 'At the beginning of your end step, create a tapped Powerstone token.'
- 'Whenever this artifact or another nontoken artifact you control is put into a graveyard from the battlefield or is put into exile from the battlefield, create a tapped Powerstone token.'
- 'Create a tapped Powerstone token.'
- 'Create three tapped Powerstone tokens.'
- 'Create two tapped Powerstone tokens.'
- 'Create a tapped Powerstone token.'
- 'Create a tapped Powerstone token.'
- '{4}, {T}: Create a tapped Powerstone token.'

**`rule:death-trigger-create-token-clue`** (2 members) — When this permanent dies, it creates a Clue token.

- 'When this creature dies, investigate. (Create a Clue token. It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- 'Create a Clue token.'

**`rule:death-trigger-create-token-creature`** (2 members) — When this permanent dies, it creates one or more creature tokens.

- 'When this creature dies, create a 1/1 green Saproling creature token.'
- 'When this creature dies, create two 1/1 black Fungus creature tokens with "This token can\'t block."'

**`rule:death-trigger-create-token-treasure`** (2 members) — When this permanent dies, it creates a Treasure token.

- 'When this creature dies, create a Treasure token.'
- 'When this creature dies, create a Treasure token.'

**`rule:draw-second-card-trigger-pump-vigilance`** (1 members) — An ability triggers specifically when the controller draws their second card in a turn, granting a temporary buff and keyword.

- 'Whenever you draw your second card each turn, this creature gets +1/+1 and gains vigilance until end of turn.'

**`rule:draw-second-card-trigger-token-flying`** (1 members) — An ability triggers specifically when the controller casts their second spell each turn, producing a flying creature token as the reward.

- 'Whenever you cast your second spell each turn, create a 1/1 white Spirit creature token with flying.'

**`rule:etb-create-token-blood`** (6 members) — When the permanent enters the battlefield, it creates Blood tokens.

- 'When this creature enters, create a Blood token.'
- 'When this creature enters, create two Blood tokens.'
- 'When this creature enters, create a Blood token.'
- 'When this creature enters, create a Blood token.'
- 'When Ivora enters and whenever it deals combat damage to a player, create a Blood token.'
- 'When this enchantment enters, create a Blood token for each opponent you have.'

**`rule:etb-create-token-clue`** (9 members) — When the permanent enters the battlefield, conditional on a stated raid condition, it creates a Clue token.

- 'When this creature enters, create a Clue token.'
- 'When this enchantment enters, create a Clue token.'
- 'When this creature enters, investigate. (Create a Clue token.'
- 'When this Aura enters, investigate. (Create a Clue token. It\'s an artifact with "{2}, Sacrifice this token: Draw a card.")'
- 'When this creature enters, create a Clue token.'
- 'Raid — When this creature enters, if you attacked this turn, create a Clue token.'
- 'When this creature enters, investigate. (Create a Clue token.'
- 'When this creature dies, investigate.'
- 'When this artifact enters, investigate twice.'

**`rule:etb-create-token-conditional`** (1 members) — When the permanent enters the battlefield, it creates a token only if a stated condition (opponent having more lands) is met.

- 'When this creature enters, if an opponent controls more lands than you, create a tapped Vibranium token.'

**`rule:etb-create-token-food-conditional`** (2 members) — When the permanent enters the battlefield, it creates a Food token only if a stated condition (failing to find/put a card into hand) is met.

- "If you don't put a card into your hand this way, create a Food token."
- 'When this creature enters, if you cast it from your hand, create three Food tokens.'

**`rule:etb-create-token-gold`** (1 members) — A saga chapter creates a Gold token.

- 'IV — Create a Gold token.'

**`rule:etb-create-token-lander`** (6 members) — When the permanent enters the battlefield, it creates a Lander token that can be sacrificed to fetch a basic land.

- 'When this creature enters, create a Lander token.'
- 'When this creature enters, create a Lander token.'
- 'When this enchantment enters, create a Lander token.'
- 'When this creature enters, create a Lander token.'
- 'When this creature enters, create a Lander token.'
- 'When this creature enters, create a Lander token.'

**`rule:etb-create-token-mana-producing-artifact`** (14 members) — Whenever the controller discards one or more artifact cards, create a tapped mana-producing artifact token, limited to once per turn.

- "When this creature enters, choose target player. You create a tapped Powerstone token for each nonland card in that player's graveyard that was put there from the battlefield this turn."
- 'When this creature enters, create a tapped Powerstone token.'
- 'When this artifact enters, create two tapped Vibranium tokens.'
- 'When this creature enters, create a tapped Powerstone token.'
- 'When this creature enters, create a Map token.'
- 'When this creature enters, create a tapped Powerstone token.'
- "When Hurkyl's Prodigy enters, create a tapped Powerstone token."
- 'When this creature enters, you and target opponent each create a tapped Powerstone token.'
- 'When this creature enters, create a tapped Powerstone token.'
- 'Whenever you discard one or more artifact cards, create a tapped Powerstone token. This ability triggers only once each turn.'
- 'Whenever you discard one or more artifact cards, create a tapped Powerstone token. This ability triggers only once each turn.'
- "Whenever T'Challa enters or attacks, create a tapped Vibranium token."
- 'When this creature enters, create a tapped Powerstone token.'
- 'you may create a 0/1 colorless Eldrazi Spawn creature token. It has "Sacrifice this token: Add {C}."'

**`rule:etb-create-token-powerstone`** (3 members) — When the permanent enters the battlefield, it creates a Powerstone token

- 'When this creature enters, create a tapped Powerstone token for each other creature you control.'
- 'create a tapped Powerstone token'
- 'At the beginning of your end step, create a tapped Powerstone token.'

**`rule:etb-create-token-treasure`** (34 members) — When the permanent enters the battlefield, it creates a Treasure token.

- 'When Beza enters, create a Treasure token if an opponent controls more lands than you.'
- 'When this creature enters, create two Treasure tokens.'
- 'When this creature enters, create a Treasure token.'
- 'When this creature enters, create a Treasure token.'
- 'When this creature enters, create a Treasure token.'
- 'When this creature enters, create a Treasure token.'
- 'When this enchantment enters, create three Treasure tokens.'
- 'When this creature enters, create a Treasure token.'
- 'When this Class enters, create two tapped Treasure tokens.'
- 'When this creature enters, if you control another outlaw, create a Treasure token.'
- 'When this creature enters, create a Treasure token.'
- 'When this creature enters, create a Treasure token.'
- 'When this artifact enters or is put into a graveyard from the battlefield, create a Treasure token.'
- 'Whenever this creature or another Pirate you control enters, create a tapped Treasure token.'
- 'When this creature enters, create X Treasure tokens, where X is the number of artifacts and enchantments your opponents control.'
- 'When Sarkhan enters, you may behold a Dragon. If you do, create a Treasure token.'
- 'Create a Treasure token.'
- 'When this enchantment enters, you take the initiative and create a Treasure token.'
- 'When this Equipment enters, create a Treasure token.'
- 'When this Equipment enters, create a Treasure token.'
- 'When this Equipment enters, create a Treasure token.'
- 'When this creature enters, if an opponent controls more lands than you, you create a Treasure token.'
- 'When this creature enters, create two Treasure tokens.'
- 'When this creature enters, create a Treasure token.'
- 'When this creature enters, create a Treasure token.'
- 'Create a Treasure token.'
- 'When this creature enters, create a Treasure token.'
- 'When this enchantment enters, create two Treasure tokens.'
- 'When this creature enters, create a Treasure token.'
- 'When this creature enters, create a Treasure token.'
- 'When this creature enters, create a Treasure token.'
- 'When this creature enters, create a Treasure token.'
- 'When Stimulus Package enters, create two Treasure tokens.'
- 'When Galazeth Prismari enters, create a Treasure token.'

**`rule:etb-create-token-treasure-conditional`** (1 members) — When the permanent enters, it creates a Treasure token only if a stated condition (failure of another effect) is met.

- "If you can't, create a Treasure token."

**`rule:etb-create-token-with-x-counters`** (8 members) — The permanent enters the battlefield carrying a number of +1/+1 counters equal to X paid when casting.

- 'This creature enters with X +1/+1 counters on it.'
- 'When this enchantment enters, create an X/X green Treefolk creature token.'
- 'That creature enters with an additional +1/+1 counter on it.'
- 'When Mutagen Man enters, create X Mutagen tokens.'
- 'At the beginning of your upkeep, create a colorless artifact token named Land Mine with "{R}, Sacrifice this token: This token deals 2 damage to target attacking creature without flying."'
- 'When Niko Aris enters, create X Shard tokens.'
- 'When this artifact enters, support X. (Put a +1/+1 counter on each of up to X target creatures.)'
- 'When this creature enters, support 2. (Put a +1/+1 counter on each of up to two other target creatures.)'

**`rule:grants-attack-trigger-create-token-food`** (1 members) — An Aura grants the enchanted creature a new attack-triggered ability that creates a Food token.

- 'Enchanted creature gets +0/+3 and has "Whenever this creature attacks, create a Food token."'

**`rule:grants-combat-damage-create-token-blood`** (1 members) — Equipment grants the equipped creature an ability that creates a Blood token whenever it deals combat damage.

- 'Whenever this creature deals combat damage, create a Blood token.'

**`rule:grants-counter-tribal-static`** (1 members) — A triggered ability places +1/+1 counters on all creatures the controller controls sharing a specific creature type.

- 'Whenever the Ring tempts you, put a +1/+1 counter on each Wraith you control.'

**`rule:grants-flying-haste-static-target`** (1 members) — Equipped creature gains flying and haste along with a stat boost as a static grant from the Equipment.

- 'Equipped creature gets +2/+2 and has flying and haste.'

**`rule:grants-flying-static-target`** (1 members) — A static ability grants the flying keyword to the equipped/attached creature.

- 'Equipped creature has flying.'

**`rule:grants-flying-target-static`** (3 members) — An Aura grants the enchanted creature flying as a static ability.

- 'Enchanted creature has flying.'
- 'Enchanted creature has flying.'
- 'Enchanted creature has flying.'

**`rule:grants-haste-static-target`** (1 members) — An Aura grants the enchanted creature haste as a static ability.

- 'Enchanted creature gets +3/+3 and has haste.'

**`rule:grants-lifelink-equip`** (1 members) — Equipment grants the equipped creature a permanent stat boost and lifelink while attached.

- 'Equipped creature gets +1/+1 and has lifelink.'

**`rule:grants-lifelink-target-creature-token`** (1 members) — Creates a creature token that has an evergreen keyword ability as part of its creation.

- 'Create a 1/1 white Soldier creature token with lifelink.'

**`rule:grants-menace-conditional-tribal`** (1 members) — A static ability grants menace to the equipped creature only while it is a specified creature type.

- 'As long as equipped creature is a Human, it has menace.'

**`rule:grants-menace-static-own-tribal-condition`** (1 members) — Grants itself menace as long as a tribal condition among the controller's board is met.

- 'This creature has menace as long as you control another Pirate.'

**`rule:grants-ward-sacrifice-food-static`** (1 members) — A static ability grants ward to the source, paid by sacrificing a Food.

- 'Ward—Sacrifice a Food.'

**`rule:leaves-battlefield-trigger-create-token-blood`** (1 members) — When this creature dies, it creates a Blood token.

- 'When this creature dies, create a Blood token.'

**`rule:leaves-battlefield-trigger-create-token-clue`** (1 members) — When this permanent dies, it creates a Clue token.

- 'When this Vehicle dies, create a Clue token.'

**`rule:leaves-battlefield-trigger-create-token-treasure`** (1 members) — Whenever the permanent leaves the battlefield via dying, it creates a Treasure token.

- 'When this creature dies, create a Treasure token.'

**`rule:scales-mana-by-count-clue`** (1 members) — An activated mana ability produces mana scaled by the number of Clue permanents the controller controls.

- '{T}: Add {U} for each Clue you control.'

**`rule:targeted-bounce-artifact`** (2 members) — Returns a target artifact to its owner's hand.

- "Return target artifact to its owner's hand."
- "Return target artifact to its owner's hand."

**`rule:targeted-bounce-artifact-or-enchantment`** (1 members) — When the permanent enters the battlefield, it returns a target artifact or enchantment to its owner's hand.

- "When this creature enters, return target artifact or enchantment to its owner's hand."

**`rule:targeted-bounce-enchantment`** (1 members) — Returns a target enchantment to the top of its owner's library rather than to hand, functioning as tempo-based removal.

- "Put target enchantment on top of its owner's library."

**`rule:targeted-bounce-nonland`** (1 members) — Returns a target nonland permanent to its owner's hand.

- "Return target nonland permanent with mana value X to its owner's hand."

**`rule:targeted-bounce-permanent`** (21 members) — An instant returns a target nonland permanent to its owner's hand.

- "Return target nonland permanent to its owner's hand."
- "Return target nonland permanent to its owner's hand."
- "Return target nonland permanent to its owner's hand."
- "Return target permanent to its owner's hand."
- "Return target nonland permanent to its owner's hand."
- "Return target nonland permanent to its owner's hand."
- "Return target permanent to its owner's hand."
- "Return target nonland permanent to its owner's hand."
- "Return one or two target nonland permanents to their owners' hands."
- 'The owner of target nonland permanent shuffles it into their library, then draws two cards.'
- "Return target nonland permanent [you control] to its owner's hand."
- "Return target permanent to its owner's hand."
- "Return target nonland permanent to its owner's hand."
- "Return target nonland permanent to its owner's hand."
- "Return target permanent to its owner's hand."
- "Return target permanent to its owner's hand."
- "Return target nonland permanent to its owner's hand."
- "Return target nonland permanent you don't control to its owner's hand."
- "Return target nonland permanent to its owner's hand."
- "Return target nonland permanent to its owner's hand."
- "Return target nonland permanent to its owner's hand."

**`rule:targeted-counter-sorcery`** (1 members) — Counters a target sorcery spell specifically.

- 'Counter target sorcery spell.'

**`rule:targeted-counter-spell`** (1 members) — Counters a target spell restricted by a specific mana-value condition.

- 'Counter target spell with mana value 2.'

**`rule:targeted-damage-any-target`** (3 members) — An activated ability that sacrifices the source land to deal a fixed amount of damage to any target, gated by a graveyard-size threshold.

- 'This enchantment deals X damage to any target.'
- 'Pyre-Sledge Arsonist deals X damage to any target'
- 'Threshold — {R}, {T}, Sacrifice this land: It deals 2 damage to any target.'

**`rule:targeted-damage-creature`** (44 members) — A spell deals damage to a target creature (or planeswalker) as part of its effect.

- 'End-Blaze Epiphany deals X damage to target creature.'
- 'Frost Bite deals 2 damage to target creature or planeswalker.'
- 'Strangle deals 3 damage to target creature or planeswalker.'
- "Narset's Rebuke deals 5 damage to target creature."
- 'Rending Flame deals 5 damage to target creature or planeswalker.'
- '{T}: Jeska deals 1 damage to any target.'
- "{T}: This creature deals 1 damage to target creature and that creature's controller loses 1 life."
- 'Final Flare deals 5 damage to target creature.'
- 'Maestros Charm deals 5 damage to target creature or planeswalker.'
- 'Brittle Blast deals 5 damage to target creature or planeswalker.'
- 'Trial of Agony deals 5 damage to that creature'
- 'Torch the Witness deals twice X damage to target creature.'
- 'Hexgold Slash deals 2 damage to target creature. If that creature has toxic, Hexgold Slash deals 4 damage to that creature instead.'
- 'Obliterating Bolt deals 4 damage to target creature or planeswalker.'
- "Ral's Outburst deals 3 damage to any target."
- 'Strafe deals 3 damage to target nonred creature.'
- 'Focus Fire deals X damage to target attacking or blocking creature'
- 'Brutal Expulsion deals 2 damage to target creature or planeswalker.'
- 'If you win one or more flips, Fiery Gambit deals 3 damage to target creature.'
- 'Molten Exhale deals 4 damage to target creature or planeswalker.'
- 'Mine Collapse deals 5 damage to target creature or planeswalker.'
- 'Osseous Exhale deals 5 damage to target attacking or blocking creature.'
- '{R}, Sacrifice a land: This enchantment deals 1 damage to each creature without flying.'
- "Galvanize deals 3 damage to target creature. If you've drawn two or more cards this turn, Galvanize deals 5 damage to that creature instead."
- 'This sorcery deals 4 damage to target creature or planeswalker.'
- 'Shredding Winds deals 7 damage to target creature with flying.'
- 'Rebel Salvo deals 5 damage to target creature or planeswalker.'
- 'Ravaging Blaze deals X damage to target creature.'
- 'Molten Rebuke deals 5 damage to target creature or planeswalker.'
- 'Cast into the Fire deals 1 damage to each of up to two target creatures.'
- '{T}: This creature deals 4 damage to target attacking creature with flying.'
- 'Fire Prophecy deals 3 damage to target creature.'
- "Carnival deals 1 damage to target creature or planeswalker and 1 damage to that permanent's controller."
- "Light 'Em Up deals 2 damage to target creature or planeswalker."
- 'Burning Oil deals 3 damage to target attacking or blocking creature.'
- 'Unleash the Inferno deals 7 damage to target creature or planeswalker.'
- 'Stomp deals 2 damage to any target.'
- 'Parasitic Grasp deals 3 damage to target [Human] creature.'
- 'Road Rage deals X damage to target creature or planeswalker'
- 'Broadside Barrage deals 5 damage to target creature or planeswalker.'
- 'Take Out the Trash deals 3 damage to target creature or planeswalker.'
- 'Witchstalker Frenzy deals 5 damage to target creature.'
- "Counter target creature spell. Essence Backlash deals damage equal to that spell's power to its controller."
- 'Barbed Lightning deals 3 damage to target creature.'

**`rule:targeted-damage-player`** (29 members) — Causes a target player to lose a fixed amount of life, functioning like direct damage to a player.

- 'it deals 3 damage to target opponent or planeswalker'
- 'When this land enters, it deals 1 damage to target player or planeswalker.'
- 'When this land enters, it deals 1 damage to target opponent.'
- '{T}: This creature deals 1 damage to target player or planeswalker.'
- 'It deals 3 damage to target player or planeswalker.'
- 'Burn deals 2 damage to any target.'
- '{1}, {T}: This artifact deals 1 damage to target opponent or planeswalker.'
- '{T}: This creature deals 1 damage to target player or planeswalker.'
- "Sarkhan's Catharsis deals 5 damage to target player or planeswalker."
- 'Target player loses 5 life.'
- 'Spikefield Hazard deals 1 damage to any target.'
- 'When this creature dies, it deals 3 damage to any target.'
- 'It deals 5 damage to target player or planeswalker.'
- 'Taste of Blood deals 1 damage to target player or planeswalker'
- '{2}{R}: This creature deals 1 damage to target player or planeswalker.'
- 'Blood for the Blood God! deals 8 damage to each opponent.'
- 'Blightning deals 3 damage to target player or planeswalker.'
- 'Clan Defiance deals X damage to target player or planeswalker.'
- 'Burning Fields deals 5 damage to target opponent or planeswalker.'
- 'Quenchable Fire deals 3 damage to target player or planeswalker.'
- 'Start from Scratch deals 1 damage to any target.'
- 'Target opponent loses 3 life.'
- 'It deals 3 damage to target player or planeswalker.'
- "Chandra's Fury deals 4 damage to target player or planeswalker"
- 'When this Siege enters, it deals 3 damage to any other target and you gain 3 life.'
- "Peak Eruption deals 3 damage to that land's controller."
- 'Scrapyard Salvo deals damage to target player or planeswalker equal to the number of artifact cards in your graveyard.'
- 'Wild Slash deals 2 damage to any target.'
- 'This artifact deals 2 damage to target player or planeswalker.'

**`rule:targeted-debuff-creature`** (1 members) — An activated ability that costs sacrificing a creature to reduce a target creature's power and toughness until end of turn.

- '{B}, Sacrifice another creature: Target creature gets -2/-2 until end of turn.'

**`rule:targeted-discard-player`** (9 members) — Forces a target player to discard a card from their hand.

- 'Target opponent discards two cards.'
- 'Target player discards three cards.'
- 'That player discards those cards.'
- 'Target opponent discards two cards.'
- 'Target player discards two cards at random.'
- 'Target opponent discards two cards.'
- 'Target opponent discards a card at random.'
- 'Target player discards a card.'
- 'Target player discards two cards.'

**`rule:targeted-exile-artifact`** (7 members) — The spell exiles two target artifacts.

- 'Exile target artifact.'
- 'When you cast this spell, if it was kicked with its {G} kicker, exile target artifact or enchantment an opponent controls.'
- 'Exile target artifact.'
- 'Exile two target artifacts.'
- 'Exile target artifact.'
- 'Exile target artifact.'
- 'Exile target artifact.'

**`rule:targeted-exile-artifact-or-creature`** (1 members) — A loyalty ability exiles a target artifact or creature permanent.

- '−3: Exile target artifact or creature.'

**`rule:targeted-exile-artifact-or-enchantment`** (11 members) — Exiles a target artifact or enchantment as removal.

- '{T}, Tap two untapped Humans you control: Exile target artifact or enchantment.'
- 'Exile target noncreature artifact or noncreature enchantment.'
- 'Exile target artifact or enchantment.'
- 'Exile target artifact or enchantment.'
- 'Exile target artifact or enchantment.'
- 'Exile target artifact or enchantment.'
- '{1}{G/W}: Exile target artifact or enchantment. Activate only once.'
- 'Exile up to two target artifacts and/or enchantments.'
- 'Impound — Exile target artifact or enchantment.'
- 'When this enchantment enters, you may exile target artifact or enchantment.'
- 'Exile target artifact or enchantment.'

**`rule:targeted-exile-creature`** (68 members) — Exiles a target creature as a removal effect.

- 'Exile target creature with power 3 or less.'
- 'Exile target creature.'
- 'Exile target creature.'
- 'Metalcraft — If you control three or more artifacts, exile that creature.'
- 'Exile target creature or Spacecraft.'
- '{T}, Sacrifice this creature: Exile target red creature.'
- 'Exile target creature.'
- 'Exile target creature or planeswalker.'
- 'exile target tapped creature an opponent controls until this creature leaves the battlefield'
- 'Exile any number of target creatures.'
- 'Exile target creature.'
- 'Exile target artifact, enchantment, or creature with flying.'
- 'Exile target attacking creature.'
- "Exile target creature you don't control."
- 'Exile target attacking creature and all Equipment attached to it.'
- 'Exile target colorless creature.'
- 'Exile target creature.'
- 'Exile target creature or planeswalker.'
- 'Exile any number of target creatures and all Auras attached to them.'
- 'Tap two untapped creatures you control that share a creature type: Exile enchanted creature.'
- 'Exile target creature.'
- 'Exile target attacking creature if its power is less than or equal to the number of Soldiers on the battlefield.'
- "Exile target creature you don't control."
- 'Exile the chosen creature, then its controller gains life equal to its mana value.'
- 'Exile target attacking or blocking creature.'
- 'Exile target tapped creature.'
- 'Exile X target creatures.'
- 'Exile target tapped creature.'
- 'Exile target creature with toughness 4 or greater.'
- 'Exile all creatures.'
- 'Exile target creature.'
- 'Exile target creature.'
- "Exile target creature that's attacking you if it's controlled by the chosen player."
- 'Exile target attacking creature.'
- 'Whenever Captain Marvel enters or attacks, exile up to one target creature.'
- 'When Darkstar Banisher enters, exile target nonland permanent with mana value 4 or less an opponent controls.'
- 'Exile target creature that blocked or was blocked by a Zombie this turn.'
- 'Exile target creature or Vehicle.'
- 'Exile target nonwhite attacking creature.'
- "Exile target creature or planeswalker that's black or red."
- 'Exile two target nonartifact creatures.'
- 'Exile target creature with power 4 or greater.'
- 'Exile enchanted creature.'
- '• Exile target creature with power 5 or greater.'
- 'Exile target tapped creature.'
- 'Exile target creature with power 4 or greater.'
- 'Exile target creature or enchantment.'
- 'Exile target creature.'
- 'Exile target attacking creature.'
- 'Exile target creature.'
- 'Exile target artifact, creature, or enchantment.'
- 'Exile target Spirit, creature with disturb, or enchantment.'
- 'Target opponent exiles a creature they control.'
- 'Exile target creature or planeswalker.'
- 'Exile target attacking creature.'
- 'Exile target creature or planeswalker.'
- 'Exile target creature.'
- 'exile target tapped creature an opponent controls until this enchantment leaves the battlefield'
- 'Exile target creature.'
- 'Exile target artifact or creature.'
- "Exile target white creature that's attacking or blocking."
- 'Exile target creature.'
- 'Exile target attacking creature.'
- 'Exile target creature with mana value 3 or greater.'
- 'Exile target creature or planeswalker.'
- 'Exile target creature with power 3 or less.'
- 'Exile target creature with mana value 3 or less.'
- 'Exile target creature.'

**`rule:targeted-exile-enchantment`** (5 members) — Exiles a target enchantment as a modal choice.

- 'Exile up to three target enchantments.'
- 'Exile target enchantment.'
- 'Exile target enchantment.'
- 'Exile target enchantment.'
- 'Exile target enchantment.'

**`rule:targeted-exile-graveyard-card`** (2 members) — Exiles a target card from any graveyard.

- 'Exile up to one target card from a graveyard.'
- 'Exile target card from a graveyard.'

**`rule:targeted-exile-land`** (4 members) — Exiles a target land, removing it from the game.

- 'Exile target nonbasic land.'
- 'When you cast this spell, if it was kicked, exile target land.'
- 'Exile target land.'
- 'Exile target nonbasic land.'

**`rule:targeted-exile-nonland-permanent`** (1 members) — Exiles a target nonland permanent.

- 'Exile target nonland permanent.'

**`rule:targeted-exile-permanent`** (17 members) — Exiles a target permanent an opponent controls, restricted by a mana value threshold.

- 'Exile target permanent with mana value 3 or greater.'
- 'Exile target artifact, creature, or enchantment an opponent controls.'
- 'Converge — Exile target nonland permanent if its mana value is less than or equal to the number of colors of mana spent to cast this spell.'
- 'Exile target permanent an opponent controls with mana value 3 or greater.'
- 'Exile target monocolored permanent.'
- 'Exile target nonland permanent.'
- 'Exile target white permanent.'
- 'For each player, exile up to one target nonland permanent that player controls.'
- 'Exile target nonland permanent.'
- 'Exile up to one target artifact, up to one target creature, up to one target enchantment, up to one target planeswalker, and/or up to one target land.'
- 'Exile target permanent with mana value 4 or greater.'
- 'Exile target nonland permanent.'
- 'Exile target nonland permanent an opponent controls'
- 'Exile target nonland permanent.'
- 'Exile target black or red permanent.'
- 'Exile target artifact or enchantment.'
- 'Exile target artifact, enchantment, or tapped creature an opponent controls.'

**`rule:targeted-exile-player`** (1 members) — Exiles a target opponent's entire graveyard as a single instant effect.

- "Exile target opponent's graveyard."

**`rule:targeted-exile-player-graveyard`** (2 members) — Exiles a target player's entire graveyard as one modal option.

- "Exile target player's graveyard."
- "If this spell was kicked, instead exile target player's graveyard."

**`rule:targeted-mill-player`** (1 members) — An ETB effect mills a target opponent's library for a fixed number of cards.

- 'When this creature enters, target opponent mills two cards.'

**`rule:targeted-tap-artifact-creature`** (1 members) — A spell taps a target artifact or creature as a removal/disruption effect.

- 'Tap target artifact or creature.'

**`rule:targeted-tap-creature`** (5 members) — Taps one or more target creatures as a removal or combat disruption effect.

- 'Tap target creature.'
- 'Tap up to two target creatures.'
- 'Tap up to one target creature.'
- 'Whenever this creature attacks, you may pay {2}{W}. When you do, tap target creature.'
- "{T}: Tap target creature without flying that's attacking you."

**`rule:targeted-tutor-library-to-hand-activated`** (1 members) — An activated ability lets the controller search their library for any card and put it into hand.

- '{6}, {T}: Search your library for a card, put that card into your hand, then shuffle.'

**`rule:targeted-tutor-to-library-top-creature`** (1 members) — Searches the library for a creature card and places it on top of the library rather than into hand.

- 'Search your library for a creature card, reveal it, then shuffle and put the card on top.'

## Part 5 — WHAT THE NEXT SESSION MUST REPRODUCE EXACTLY

These counts are the closed loop: session 2b expands the decisions above
into full rows and must reproduce every number here or halt. This is what
makes auditing this artifact alone meaningful — a bug in the mechanical
expander is otherwise precisely what you cannot see from here.

| count | value |
|---|---|
| codebook_lane_member_additions | 14255 |
| codebook_lane_assertion_merges | 1833 |
| grammar_lane_member_additions | 1127 |
| grammar_lane_assertion_merges | 170 |
| r5_member_additions | 45 |
| r5_assertion_merges | 96 |
| a15_promoted_rows | 4 |
| a15_blocked_pending_vocabulary | 209 |
| a15_fell_back_to_discovery | 0 |
| new_axes_instantiated | 93 |
| new_axis_member_rows | 605 |
| revivals_to_deferred | 2 |
| kill_note_corrections | 3 |
| whole_slug_aliases | 1 |
| routing_rows | 2 |
| same_run_duplicates_collapsed | 44 |
| total_enumerated_rows | 18135 |

## Part 6 — PROMOTIONS

Free-lane model output being promoted into curated membership. This is the
judgment most worth attacking: the lane system exists to keep unreviewed
model output out of the codebook, and these rulings carve exceptions.

### R5 — free-lane labels literally equal to an existing active axis

45 become new members; 96 are cards already on the axis, so they
merge as an additional llm assertion onto an existing member.

| slug | card | disposition | evidence quote |
|---|---|---|---|
| `rule:activated-cost-discard-a-card` | Ormos, Archive Keeper | member-addition | {1}{U}{U}, Discard three cards with different names: Draw five cards. |
| `rule:activated-cost-discard-a-card` | Chase Stein, Runaway | member-addition | {T}, Discard a card: Exile the top card of your library. Until the end of your next turn, you may play that ca |
| `rule:attack-trigger-loot` | Furtive Courier | assertion-merge | Whenever this creature attacks, draw a card, then discard a card. |
| `rule:changes-creature-type-text` | Lorcan, Warlock Collector | member-addition | It's a Warlock in addition to its other types. |
| `rule:choose-creature-type-on-etb` | From the Rubble | member-addition | As this enchantment enters, choose a creature type. |
| `rule:conditional-attack-restriction-by-defending-player-land-type` | Deep-Sea Serpent | member-addition | This creature can't attack unless defending player controls an Island. |
| `rule:delayed-draw-next-upkeep` | Formation | member-addition | Draw a card at the beginning of the next turn's upkeep. |
| `rule:delayed-draw-next-upkeep` | Astrolabe | member-addition | Draw a card at the beginning of the next turn's upkeep. |
| `rule:delayed-draw-next-upkeep` | Dazzling Beauty | member-addition | Draw a card at the beginning of the next turn's upkeep. |
| `rule:draw-cards-with-life-loss-cost` | Read the Bones | member-addition | You lose 2 life. |
| `rule:draw-scales-with-opponent-tapped-creature-count` | Theft of Dreams | assertion-merge | Draw a card for each tapped creature target opponent controls. |
| `rule:draw-trigger-self-counter-growth` | Kianne, Corrupted Memory | assertion-merge | Whenever you draw a card, put a +1/+1 counter on Kianne. |
| `rule:enters-tapped` | Piranha Fly | assertion-merge | This creature enters tapped. |
| `rule:equipment-etb-create-and-attach-token` | Hexplate Wallbreaker | assertion-merge | For Mirrodin! (When this Equipment enters, create a 2/2 red Rebel creature token, then attach this to it.) |
| `rule:etb-bounce-own-land` | Selesnya Sanctuary | member-addition | When this land enters, return a land you control to its owner's hand. |
| `rule:etb-bounce-own-land` | Simic Growth Chamber | member-addition | When this land enters, return a land you control to its owner's hand. |
| `rule:etb-draw-card` | Blood Sun | member-addition | When this enchantment enters, draw a card. |
| `rule:etb-scry` | Simulacrum Synthesizer | member-addition | When this artifact enters, scry 2. |
| `rule:evasion-vs-low-power-blockers` | Antique Collector | member-addition | This creature can't be blocked by creatures with power 2 or less. |
| `rule:flashback-recast-from-graveyard` | Morgue Theft | member-addition | Flashback {4}{B} (You may cast this card from your graveyard for its flashback cost. Then exile it.) |
| `rule:flashback-recast-from-graveyard` | Isengard Unleashed | member-addition | Flashback {4}{R}{R}{R} |
| `rule:flashback-recast-from-graveyard` | Embolden | member-addition | Flashback {1}{W} (You may cast this card from your graveyard for its flashback cost. Then exile it.) |
| `rule:flashback-recast-from-graveyard` | Shadowbeast Sighting | member-addition | Flashback {6}{G} (You may cast this card from your graveyard for its flashback cost. Then exile it.) |
| `rule:flashback-recast-from-graveyard` | Grizzly Fate | member-addition | Flashback {5}{G}{G} (You may cast this card from your graveyard for its flashback cost. Then exile it.) |
| `rule:forced-attack-each-combat` | Phyrexian Juggernaut | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Bloodrock Cyclops | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Daring Fiendbonder | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Lust for War | member-addition | Enchanted creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Akoum Firebird | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Sabertooth Alley Cat | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Amarant Coral | member-addition | Amarant Coral attacks each combat if able. |
| `rule:forced-attack-each-combat` | Battle-Mad Ronin | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Deathbellow Raider | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Ulamog's Crusher | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Zurgo Helmsmasher | member-addition | Zurgo attacks each combat if able. |
| `rule:forced-attack-each-combat` | Bloodcrazed Neonate | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Alexios, Deimos of Kosmos | member-addition | Alexios attacks each combat if able, can't be sacrificed, and can't attack its owner. |
| `rule:forced-attack-each-combat` | Emberwilde Caliph | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Hanweir Watchkeep // Bane of Hanweir | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Anje's Ravager | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Flamewake Phoenix | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Mage-Ring Bully | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Valley Dasher | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Thran War Machine | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Volatile Rig | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Weary Prisoner // Wrathful Jailbreaker | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Dauthi Slayer | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Cogwork Tracker | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Manticore Eternal | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Kuldotha Ringleader | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Tectonic Fiend | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Red Herring | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Phyrexian Snowcrusher | assertion-merge | This creature attacks each combat if able. |
| `rule:forced-attack-each-combat` | Mishra's Juggernaut | assertion-merge | This creature attacks each combat if able. |
| `rule:forces-creature-to-be-blocked` | Bumper Cars | member-addition | Visit — Target creature must be blocked this turn if able. |
| `rule:grants-additional-combat-phase` | Take the Bait | assertion-merge | After this phase, there is an additional combat phase. |
| `rule:grants-additional-combat-phase` | Swinging Ship | assertion-merge | After the first combat phase this turn, there's an additional combat phase. |
| `rule:grants-additional-combat-phase` | Savage Beating | assertion-merge | After this phase, there is an additional combat phase. |
| `rule:grants-additional-combat-phase` | Breath of Fury | assertion-merge | after this phase, there is an additional combat phase |
| `rule:grants-cascade-to-own-spells` | Zhulodok, Void Gorger | member-addition | Colorless spells you cast from your hand with mana value 7 or greater have "Cascade, cascade." |
| `rule:grants-controller-hexproof` | Crystal Barricade | assertion-merge | You have hexproof. (You can't be the target of spells or abilities your opponents control.) |
| `rule:grants-controller-hexproof` | Keen-Eared Sentry | assertion-merge | You have hexproof. |
| `rule:grants-controller-hexproof` | Metropolis Reformer | assertion-merge | You have hexproof. |
| `rule:grants-controller-hexproof` | Orbs of Warding | assertion-merge | You have hexproof. (You can't be the target of spells or abilities your opponents control.) |
| `rule:grants-double-strike-target` | Team Tactics | assertion-merge | Target creature gains double strike until end of turn. |
| `rule:grants-extra-turn` | Temporal Extortion | assertion-merge | Take an extra turn after this one. |
| `rule:grants-extra-turn` | Temporal Manipulation | assertion-merge | Take an extra turn after this one. |
| `rule:grants-extra-turn` | Rise of the Eldrazi | assertion-merge | Take an extra turn after this one. |
| `rule:grants-extra-turn` | Time Walk | assertion-merge | Take an extra turn after this one. |
| `rule:grants-extra-turn` | Time Warp | assertion-merge | Target player takes an extra turn after this one. |
| `rule:grants-flashback-to-graveyard-card` | Flashback | assertion-merge | Target instant or sorcery card in your graveyard gains flashback until end of turn. The flashback cost is equa |
| `rule:grants-haste-to-your-creatures` | Tuktuk Rubblefort | assertion-merge | Creatures you control have haste. |
| `rule:grants-haste-to-your-creatures` | Fires of Yavimaya | assertion-merge | Creatures you control have haste. |
| `rule:grants-trample-to-other-creatures` | Aggressive Mammoth | assertion-merge | Other creatures you control have trample. |
| `rule:grants-trample-to-other-creatures` | Old One Eye | assertion-merge | Other creatures you control have trample. |
| `rule:grants-ward-to-other-creatures` | Star Whale | assertion-merge | Other creatures you control have ward {2}. |
| `rule:grants-ward-to-other-creatures` | Hexing Squelcher | member-addition | Other creatures you control have "Ward—Pay 2 life." |
| `rule:graveyard-to-library-shuffle-in` | Tamiyo Meets the Story Circle | member-addition | Shuffle up to three target cards from your graveyard into your library. |
| `rule:landfall-gain-life` | Jaddi Offshoot | assertion-merge | Landfall — Whenever a land you control enters, you gain 1 life. |
| `rule:landfall-gain-life` | Kazandu Nectarpot | assertion-merge | Landfall — Whenever a land you control enters, you gain 1 life. |
| `rule:landfall-gain-life` | Courser of Kruphix | assertion-merge | Landfall — Whenever a land you control enters, you gain 1 life. |
| `rule:landfall-gain-life` | A-Druid Class | assertion-merge | Landfall — Whenever a land enters under your control, you gain 1 life. |
| `rule:landfall-produces-mana` | Nissa, Resurgent Animist | assertion-merge | Landfall — Whenever a land you control enters, add one mana of any color. |
| `rule:landfall-self-pump` | Akoum Hellhound | assertion-merge | Landfall — Whenever a land you control enters, this creature gets +2/+2 until end of turn. |
| `rule:landfall-self-pump` | Hedron Scrabbler | assertion-merge | Landfall — Whenever a land you control enters, this creature gets +1/+1 until end of turn. |
| `rule:landfall-self-pump` | Hedron Rover | assertion-merge | Landfall — Whenever a land you control enters, this creature gets +2/+2 until end of turn. |
| `rule:landfall-self-pump` | Makindi Sliderunner | assertion-merge | Landfall — Whenever a land you control enters, this creature gets +1/+1 until end of turn. |
| `rule:landfall-self-pump` | Grove Rumbler | assertion-merge | Landfall — Whenever a land you control enters, this creature gets +2/+2 until end of turn. |
| `rule:landfall-self-pump` | Choco, Seeker of Paradise | assertion-merge | Landfall — Whenever a land you control enters, Choco gets +1/+0 until end of turn. |
| `rule:landfall-self-pump` | Hagra Crocodile | assertion-merge | Landfall — Whenever a land you control enters, this creature gets +2/+2 until end of turn. |
| `rule:landfall-self-pump` | Windrider Eel | assertion-merge | Landfall — Whenever a land you control enters, this creature gets +2/+2 until end of turn. |
| `rule:landfall-self-pump` | Ondu Greathorn | assertion-merge | Landfall — Whenever a land you control enters, this creature gets +2/+2 until end of turn. |
| `rule:landfall-self-pump` | Scythe Leopard | assertion-merge | Landfall — Whenever a land you control enters, this creature gets +1/+1 until end of turn. |
| `rule:landfall-self-pump` | Brushfire Elemental | assertion-merge | Landfall — Whenever a land you control enters, this creature gets +2/+2 until end of turn. |
| `rule:landfall-self-pump` | Valakut Predator | assertion-merge | Landfall — Whenever a land you control enters, this creature gets +2/+2 until end of turn. |
| `rule:landfall-self-pump` | Plated Geopede | assertion-merge | Landfall — Whenever a land you control enters, this creature gets +2/+2 until end of turn. |
| `rule:landfall-self-pump` | Geyserfield Stalker | assertion-merge | Landfall — Whenever a land you control enters, this creature gets +2/+2 until end of turn. |
| `rule:landfall-self-pump` | Skyclave Geopede | assertion-merge | Landfall — Whenever a land you control enters, this creature gets +2/+2 until end of turn. |
| `rule:landfall-self-pump` | Territorial Baloth | assertion-merge | Landfall — Whenever a land you control enters, this creature gets +2/+2 until end of turn. |
| `rule:no-maximum-hand-size` | Nyssa of Traken | assertion-merge | You have no maximum hand size. |
| `rule:no-maximum-hand-size` | Curiosity Crafter | assertion-merge | You have no maximum hand size. |
| `rule:no-maximum-hand-size` | Tishana, Voice of Thunder | assertion-merge | You have no maximum hand size. |
| `rule:no-maximum-hand-size` | Reed Richards, Smartest Man | assertion-merge | You have no maximum hand size. |
| `rule:no-maximum-hand-size` | Vnwxt, Verbose Host | assertion-merge | You have no maximum hand size. |
| `rule:no-maximum-hand-size` | Graceful Adept | assertion-merge | You have no maximum hand size. |
| `rule:no-maximum-hand-size` | Body of Knowledge | assertion-merge | You have no maximum hand size. |
| `rule:no-maximum-hand-size` | Morska, Undersea Sleuth | assertion-merge | You have no maximum hand size. |
| `rule:no-maximum-hand-size` | Spellbook | assertion-merge | You have no maximum hand size. |
| `rule:no-maximum-hand-size` | Decanter of Endless Water | assertion-merge | You have no maximum hand size. |
| `rule:no-maximum-hand-size` | The Magic Mirror | assertion-merge | You have no maximum hand size. |
| `rule:no-maximum-hand-size` | Kruphix, God of Horizons | assertion-merge | You have no maximum hand size. |
| `rule:no-maximum-hand-size` | Proft's Eidetic Memory | assertion-merge | You have no maximum hand size. |
| `rule:no-maximum-hand-size` | Roaring Furnace // Steaming Sauna | assertion-merge | You have no maximum hand size. |
| `rule:prevents-regeneration` | Pongify | assertion-merge | It can't be regenerated. |
| `rule:prevents-regeneration` | Execute | assertion-merge | It can't be regenerated. |
| `rule:prevents-regeneration` | Wrath of God | assertion-merge | They can't be regenerated. |
| `rule:prevents-regeneration` | Putrefy | assertion-merge | It can't be regenerated. |
| `rule:prevents-regeneration` | Fissure | assertion-merge | It can't be regenerated. |
| `rule:prevents-target-untap-next-step` | Chill of the Grave | member-addition | Tap target creature. It doesn't untap during its controller's next untap step. |
| `rule:prevents-target-untap-next-step` | A-Dreamshackle Geist | member-addition | Target creature doesn't untap during its controller's next untap step. |
| `rule:prevents-target-untap-next-step` | Saiba Trespassers | member-addition | Those creatures don't untap during their controller's next untap step. |
| `rule:pump-two-target-creatures` | Synchronized Strike | member-addition | They each get +2/+2 until end of turn. |
| `rule:restricts-blocking-to-flying-only` | Devoted Grafkeeper // Departed Soulkeeper | member-addition | This creature can block only creatures with flying. |
| `rule:restricts-blocking-to-flying-only` | Battlefield Percher | assertion-merge | This creature can block only creatures with flying. |
| `rule:restricts-blocking-to-flying-only` | Soulcipher Board // Cipherbound Spirit | member-addition | This creature can block only creatures with flying. |
| `rule:restricts-blocking-to-flying-only` | Brazen Borrower // Petty Theft | member-addition | This creature can block only creatures with flying. |
| `rule:restricts-blocking-to-flying-only` | Stratus Walk | member-addition | Enchanted creature can block only creatures with flying. |
| `rule:sacrifice-creature-for-self-pump` | Vampire Aristocrat | member-addition | Sacrifice a creature: This creature gets +2/+2 until end of turn. |
| `rule:self-exile-after-resolution` | Perch Protection | member-addition | Exile Perch Protection. |
| `rule:self-exile-after-resolution` | Deliver Unto Evil | member-addition | Exile Deliver Unto Evil. |
| `rule:targeted-destruction` | Reclamation Sage | member-addition | When this creature enters, you may destroy target artifact or enchantment. |
| `rule:targeted-destruction` | Rambunctious Mutt | member-addition | When this creature enters, destroy target artifact or enchantment an opponent controls. |
| `rule:targeted-destruction` | Tempest of Light | member-addition | Destroy all enchantments. |
| `rule:the-ring-tempts-you` | Soothing of Sméagol | assertion-merge | The Ring tempts you. |
| `rule:the-ring-tempts-you` | Birthday Escape | assertion-merge | The Ring tempts you. |
| `rule:the-ring-tempts-you` | Claim the Precious | assertion-merge | The Ring tempts you. |
| `rule:the-ring-tempts-you` | Slip On the Ring | assertion-merge | The Ring tempts you. |
| `rule:token-sacrifice-for-colorless-mana` | Birthing Hulk | member-addition | They have "Sacrifice this token: Add {C}." |
| `rule:token-sacrifice-for-colorless-mana` | Eldrazi Repurposer | member-addition | "Sacrifice this token: Add {C}." |
| `rule:token-sacrifice-for-colorless-mana` | Grave Birthing | member-addition | It has "Sacrifice this token: Add {C}." |
| `rule:upkeep-surveil` | Aminatou, Veil Piercer | member-addition | At the beginning of your upkeep, surveil 2. |

### A15 — free-lane clusters whose canonical form matches a ratified grammar

| cluster | target slug | rows | disposition | validator |
|---|---|---|---|---|
| `targeted-destruction-creature` | `rule:targeted-destruction-creature` | 188 | blocked-pending-vocabulary-ratification | unknown_vocabulary |
| `cant-be-blocked-except-by-count` | `rule:cant-be-blocked-except-by-count` | 21 | blocked-pending-vocabulary-ratification | unknown_vocabulary |
| `etb-create-token-blood` | `rule:etb-create-token-blood` | 2 | join-existing-node | ok |
| `etb-create-token-clue` | `rule:etb-create-token-clue` | 1 | join-existing-node | ok |
| `activated-tap-opponent-artifact` | `rule:activated-tap-opponent-artifact` | 1 | instantiate | ok |

Per-row detail for the clusters that PASSED validation:

| target slug | card | raw model label | evidence quote |
|---|---|---|---|
| `rule:etb-create-token-blood` | Sanguine Statuette | `etb-create-token-blood` | When this artifact enters, create a Blood token. |
| `rule:etb-create-token-blood` | Blood Servitor | `etb-create-token-blood` | When this creature enters, create a Blood token. |
| `rule:etb-create-token-clue` | Case of the Filched Falcon | `etb-create-clue-token` | When this Case enters, investigate. (Create a Clue token. It's an artifact with "{2}, Sacrifice this token: Dr |
| `rule:activated-tap-opponent-artifact` | Touchstone | `activated-tap-opponent-artifact` | {T}: Tap target artifact you don't control. |

Per-row detail for the BLOCKED clusters (the Part 2 decision). Included in
full rather than sampled, so the ruling is not made on a curated excerpt:

| target slug | card | raw model label | evidence quote |
|---|---|---|---|
| `rule:targeted-destruction-creature` | Stand Up for Yourself | `targeted-destruction-creature` | Destroy target creature with power 3 or greater. |
| `rule:targeted-destruction-creature` | Dakmor Lancer | `targeted-destruction-creature` | When this creature enters, destroy target nonblack creature. |
| `rule:targeted-destruction-creature` | Lich's Caress | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Misfortune's Gain | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Summon: Primal Odin | `targeted-destruction-creature` | I — Gungnir — Destroy target creature an opponent controls. |
| `rule:targeted-destruction-creature` | Gallant Strike | `targeted-destruction-creature` | Destroy target creature with toughness 4 or greater. |
| `rule:targeted-destruction-creature` | Fell the Profane // Fell Mire | `targeted-destruction-creature` | Destroy target creature or planeswalker. |
| `rule:targeted-destruction-creature` | Kill! Maim! Burn! | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Bring Down | `targeted-destruction-creature` | Destroy target creature with power 4 or greater. |
| `rule:targeted-destruction-creature` | Rend Flesh | `targeted-destruction-creature` | Destroy target non-Spirit creature. |
| `rule:targeted-destruction-creature` | Bone Splinters | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Dark Banishing | `targeted-destruction-creature` | Destroy target nonblack creature. |
| `rule:targeted-destruction-creature` | Pistus Strike | `targeted-destruction-creature` | Destroy target creature with flying. |
| `rule:targeted-destruction-creature` | Spread the Sickness | `targeted-destruction-creature` | Destroy target creature, then proliferate. |
| `rule:targeted-destruction-creature` | Bitter Downfall | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Assassin's Strike | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Cut Down | `targeted-destruction-creature` | Destroy target creature with total power and toughness 5 or less. |
| `rule:targeted-destruction-creature` | Vengeance | `targeted-destruction-creature` | Destroy target tapped creature. |
| `rule:targeted-destruction-creature` | Certain Death | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Bright Reprisal | `targeted-destruction-creature` | Destroy target attacking creature. |
| `rule:targeted-destruction-creature` | Feed the Cauldron | `targeted-destruction-creature` | Destroy target creature with mana value 3 or less. |
| `rule:targeted-destruction-creature` | Defeat | `targeted-destruction-creature` | Destroy target creature with power 2 or less. |
| `rule:targeted-destruction-creature` | Liliana's Scorn | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Execute | `targeted-destruction-creature` | Destroy target white creature. It can't be regenerated. |
| `rule:targeted-destruction-creature` | Black Hole | `targeted-destruction-creature` | Destroy target creature and up to X other target creatures, where X is the number of Attractions you've visite |
| `rule:targeted-destruction-creature` | A-Knockout Blow | `targeted-destruction-creature` | Destroy target tapped creature. |
| `rule:targeted-destruction-creature` | Severed Strands | `targeted-destruction-creature` | Destroy target creature an opponent controls. |
| `rule:targeted-destruction-creature` | Just Fate | `targeted-destruction-creature` | Destroy target attacking creature. |
| `rule:targeted-destruction-creature` | The Death of Gwen Stacy | `targeted-destruction-creature` | I — Destroy target creature. |
| `rule:targeted-destruction-creature` | Pitfall Trap | `targeted-destruction-creature` | Destroy target attacking creature without flying. |
| `rule:targeted-destruction-creature` | Annihilate | `targeted-destruction-creature` | Destroy target nonblack creature. It can't be regenerated. |
| `rule:targeted-destruction-creature` | Halo Hunter | `targeted-destruction-creature` | When this creature enters, destroy target Angel. |
| `rule:targeted-destruction-creature` | Exorcist | `targeted-destruction-creature` | {1}{W}, {T}: Destroy target black creature. |
| `rule:targeted-destruction-creature` | Gloomlance | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Farm // Market | `targeted-destruction-creature` | Destroy target attacking or blocking creature. |
| `rule:targeted-destruction-creature` | Flesh to Dust | `targeted-destruction-creature` | Destroy target creature. It can't be regenerated. |
| `rule:targeted-destruction-creature` | Settle the Score | `targeted-destruction-creature` | Exile target creature. |
| `rule:targeted-destruction-creature` | Urgent Exorcism | `targeted-destruction-creature` | Destroy target Spirit or enchantment. |
| `rule:targeted-destruction-creature` | Sarkhan's Resolve | `targeted-destruction-creature` | Destroy target creature with flying. |
| `rule:targeted-destruction-creature` | Deadly Embrace | `targeted-destruction-creature` | Destroy target creature an opponent controls. |
| `rule:targeted-destruction-creature` | Murdock's Crusade | `targeted-destruction-creature` | Exile target creature with toughness 4 or greater. |
| `rule:targeted-destruction-creature` | Heartless Act | `targeted-destruction-creature` | Destroy target creature with no counters on it. |
| `rule:targeted-destruction-creature` | Fowl Strike | `targeted-destruction-creature` | Destroy target creature with flying. |
| `rule:targeted-destruction-creature` | Cruel Cut | `targeted-destruction-creature` | Destroy target creature with power 2 or less. |
| `rule:targeted-destruction-creature` | Mass Calcify | `targeted-destruction-creature` | Destroy all nonwhite creatures. |
| `rule:targeted-destruction-creature` | Gloomwidow's Feast | `targeted-destruction-creature` | Destroy target creature with flying. |
| `rule:targeted-destruction-creature` | Ertai Resurrected | `targeted-destruction-creature` | Destroy another target creature or planeswalker. |
| `rule:targeted-destruction-creature` | Notorious Assassin | `targeted-destruction-creature` | Destroy target nonblack creature. It can't be regenerated. |
| `rule:targeted-destruction-creature` | Forced March | `targeted-destruction-creature` | Destroy all creatures with mana value X or less. |
| `rule:targeted-destruction-creature` | Price of Fame | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Lethal Protection | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Vanquish the Weak | `targeted-destruction-creature` | Destroy target creature with power 3 or less. |
| `rule:targeted-destruction-creature` | Lethal Throwdown | `targeted-destruction-creature` | Destroy target creature or planeswalker. |
| `rule:targeted-destruction-creature` | Start // Finish | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Expunge | `targeted-destruction-creature` | Destroy target nonartifact, nonblack creature. |
| `rule:targeted-destruction-creature` | Afterlife | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Dimir Charm | `targeted-destruction-creature` | Destroy target creature with power 2 or less. |
| `rule:targeted-destruction-creature` | Vendetta | `targeted-destruction-creature` | Destroy target nonblack creature. It can't be regenerated. |
| `rule:targeted-destruction-creature` | Cleansing Ray | `targeted-destruction-creature` | Destroy target Vampire. |
| `rule:targeted-destruction-creature` | Grisly Ritual | `targeted-destruction-creature` | Destroy target creature or planeswalker. |
| `rule:targeted-destruction-creature` | Sever Soul | `targeted-destruction-creature` | Destroy target nonblack creature. |
| `rule:targeted-destruction-creature` | Get the Point | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Doom Blade | `targeted-destruction-creature` | Destroy target nonblack creature. |
| `rule:targeted-destruction-creature` | Surge of Righteousness | `targeted-destruction-creature` | Destroy target black or red creature that's attacking or blocking. |
| `rule:targeted-destruction-creature` | Tivadar's Crusade | `targeted-destruction-creature` | Destroy all Goblins. |
| `rule:targeted-destruction-creature` | Vraska's Finisher | `targeted-destruction-creature` | When this creature enters, destroy target creature or planeswalker an opponent controls that was dealt damage  |
| `rule:targeted-destruction-creature` | Public Execution | `targeted-destruction-creature` | Destroy target creature an opponent controls. |
| `rule:targeted-destruction-creature` | Crushing Canopy | `targeted-destruction-creature` | Destroy target creature with flying. |
| `rule:targeted-destruction-creature` | Angrath's Fury | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Terminate | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Final Flourish | `targeted-destruction-creature` | Target creature gets -2/-2 until end of turn. |
| `rule:targeted-destruction-creature` | Slay | `targeted-destruction-creature` | Destroy target green creature. It can't be regenerated. |
| `rule:targeted-destruction-creature` | Predator, Flagship | `targeted-destruction-creature` | {5}, {T}: Destroy target creature with flying. |
| `rule:targeted-destruction-creature` | Airbender's Reversal | `targeted-destruction-creature` | Destroy target attacking creature. |
| `rule:targeted-destruction-creature` | Slingbow Trap | `targeted-destruction-creature` | Destroy target attacking creature with flying. |
| `rule:targeted-destruction-creature` | Minion Missile | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Slaughter Pact | `targeted-destruction-creature` | Destroy target nonblack creature. |
| `rule:targeted-destruction-creature` | Hero's Demise | `targeted-destruction-creature` | Destroy target legendary creature. |
| `rule:targeted-destruction-creature` | Strangling Soot | `targeted-destruction-creature` | Destroy target creature with toughness 3 or less. |
| `rule:targeted-destruction-creature` | Gideon Jura | `targeted-destruction-creature` | Destroy target tapped creature. |
| `rule:targeted-destruction-creature` | Ghostly Visit | `targeted-destruction-creature` | Destroy target nonblack creature. |
| `rule:targeted-destruction-creature` | Yawgmoth's Vile Offering | `targeted-destruction-creature` | Destroy up to one target creature or planeswalker. |
| `rule:targeted-destruction-creature` | Drag to the Underworld | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Inscription of Ruin | `targeted-destruction-creature` | Destroy target creature with mana value 3 or less. |
| `rule:targeted-destruction-creature` | Assassin's Blade | `targeted-destruction-creature` | Destroy target nonblack attacking creature. |
| `rule:targeted-destruction-creature` | Ruinous Path | `targeted-destruction-creature` | Destroy target creature or planeswalker. |
| `rule:targeted-destruction-creature` | Radiant Smite | `targeted-destruction-creature` | Destroy target creature with power 4 or greater. |
| `rule:targeted-destruction-creature` | Sheer Drop | `targeted-destruction-creature` | Destroy target tapped creature. |
| `rule:targeted-destruction-creature` | Molten Frame | `targeted-destruction-creature` | Destroy target artifact creature. |
| `rule:targeted-destruction-creature` | Liliana's Defeat | `targeted-destruction-creature` | Destroy target black creature or black planeswalker. |
| `rule:targeted-destruction-creature` | Primaris Eliminator | `targeted-destruction-creature` | Executioner Round — Destroy target creature. |
| `rule:targeted-destruction-creature` | Shadowborn Demon | `targeted-destruction-creature` | When this creature enters, destroy target non-Demon creature. |
| `rule:targeted-destruction-creature` | Push // Pull | `targeted-destruction-creature` | Destroy target tapped creature. |
| `rule:targeted-destruction-creature` | Vote Out | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Scrap Compactor | `targeted-destruction-creature` | {6}, {T}, Sacrifice this artifact: Destroy target creature or Vehicle. |
| `rule:targeted-destruction-creature` | Soul Rend | `targeted-destruction-creature` | Destroy target creature if it's white. A creature destroyed this way can't be regenerated. |
| `rule:targeted-destruction-creature` | Make Your Move | `targeted-destruction-creature` | Destroy target artifact, enchantment, or creature with power 4 or greater. |
| `rule:targeted-destruction-creature` | Swift Reckoning | `targeted-destruction-creature` | Destroy target tapped creature. |
| `rule:targeted-destruction-creature` | Vraska, Scheming Gorgon | `targeted-destruction-creature` | −3: Destroy target creature. |
| `rule:targeted-destruction-creature` | Fierce Retribution | `targeted-destruction-creature` | Destroy target [attacking] creature. |
| `rule:targeted-destruction-creature` | Venom's Hunger | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Plummet | `targeted-destruction-creature` | Destroy target creature with flying. |
| `rule:targeted-destruction-creature` | Sip of Hemlock | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Silverstrike | `targeted-destruction-creature` | Destroy target attacking creature. |
| `rule:targeted-destruction-creature` | Obscura Charm | `targeted-destruction-creature` | Destroy target creature or planeswalker with mana value 3 or less. |
| `rule:targeted-destruction-creature` | Blood Curdle | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Daring Demolition | `targeted-destruction-creature` | Destroy target creature or Vehicle. |
| `rule:targeted-destruction-creature` | You Cannot Pass! | `targeted-destruction-creature` | Destroy target creature that blocked or was blocked by a legendary creature this turn. |
| `rule:targeted-destruction-creature` | Reave Soul | `targeted-destruction-creature` | Destroy target creature with power 3 or less. |
| `rule:targeted-destruction-creature` | Fell | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Murderous Compulsion | `targeted-destruction-creature` | Destroy target tapped creature. |
| `rule:targeted-destruction-creature` | Walk the Plank | `targeted-destruction-creature` | Destroy target non-Merfolk creature. |
| `rule:targeted-destruction-creature` | Unwanted Remake | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Exterminate! | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Giant Killer // Chop Down | `targeted-destruction-creature` | Destroy target creature with power 4 or greater. |
| `rule:targeted-destruction-creature` | Murder | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Pinion Feast | `targeted-destruction-creature` | Destroy target creature with flying. |
| `rule:targeted-destruction-creature` | Suspended Sentence | `targeted-destruction-creature` | Destroy target creature an opponent controls. |
| `rule:targeted-destruction-creature` | Long Goodbye | `targeted-destruction-creature` | Destroy target creature or planeswalker with mana value 3 or less. |
| `rule:targeted-destruction-creature` | Isildur's Fateful Strike | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Aerial Assault | `targeted-destruction-creature` | Destroy target tapped creature. |
| `rule:targeted-destruction-creature` | Tezzeret's Betrayal | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Assassin's Ink | `targeted-destruction-creature` | Destroy target creature or planeswalker. |
| `rule:targeted-destruction-creature` | Contract Killing | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Cradle to Grave | `targeted-destruction-creature` | Destroy target nonblack creature that entered this turn. |
| `rule:targeted-destruction-creature` | Runic Shot | `targeted-destruction-creature` | Destroy target tapped creature. |
| `rule:targeted-destruction-creature` | Liturgy of Blood | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Dark Withering | `targeted-destruction-creature` | Destroy target nonblack creature. |
| `rule:targeted-destruction-creature` | Smother | `targeted-destruction-creature` | Destroy target creature with mana value 3 or less. It can't be regenerated. |
| `rule:targeted-destruction-creature` | The Witch's Vanity | `targeted-destruction-creature` | Destroy target creature an opponent controls with mana value 2 or less. |
| `rule:targeted-destruction-creature` | Collar the Culprit | `targeted-destruction-creature` | Destroy target creature with toughness 4 or greater. |
| `rule:targeted-destruction-creature` | Cloudchaser Eagle | `targeted-destruction-creature` | When this creature enters, destroy target enchantment. |
| `rule:targeted-destruction-creature` | Death Rattle | `targeted-destruction-creature` | Destroy target nongreen creature. It can't be regenerated. |
| `rule:targeted-destruction-creature` | Mutual Destruction | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Consign to the Pit | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Noxious Grasp | `targeted-destruction-creature` | Destroy target creature or planeswalker that's green or white. |
| `rule:targeted-destruction-creature` | Eastern Paladin | `targeted-destruction-creature` | {B}{B}, {T}: Destroy target green creature. |
| `rule:targeted-destruction-creature` | Chastise | `targeted-destruction-creature` | Destroy target attacking creature. |
| `rule:targeted-destruction-creature` | Easy Prey | `targeted-destruction-creature` | Destroy target creature with mana value 2 or less. |
| `rule:targeted-destruction-creature` | Spite // Malice | `targeted-destruction-creature` | Destroy target nonblack creature. It can't be regenerated. |
| `rule:targeted-destruction-creature` | Neck Snap | `targeted-destruction-creature` | Destroy target attacking or blocking creature. |
| `rule:targeted-destruction-creature` | Desperate Plea | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Threadbind Clique // Rip the Seams | `targeted-destruction-creature` | Destroy target tapped creature. |
| `rule:targeted-destruction-creature` | Human Frailty | `targeted-destruction-creature` | Destroy target Human creature. |
| `rule:targeted-destruction-creature` | Never // Return | `targeted-destruction-creature` | Destroy target creature or planeswalker. |
| `rule:targeted-destruction-creature` | Ajani's Response | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Tivadar of Thorn | `targeted-destruction-creature` | When Tivadar enters, destroy target Goblin. |
| `rule:targeted-destruction-creature` | Feed the Cycle | `targeted-destruction-creature` | Destroy target creature or planeswalker. |
| `rule:targeted-destruction-creature` | Eviscerate | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Deadly Complication | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Take Vengeance | `targeted-destruction-creature` | Destroy target tapped creature. |
| `rule:targeted-destruction-creature` | The Revelations of Ezio | `targeted-destruction-creature` | I — Destroy target tapped creature an opponent controls. |
| `rule:targeted-destruction-creature` | Executioner's Capsule | `targeted-destruction-creature` | Destroy target nonblack creature. |
| `rule:targeted-destruction-creature` | Dwarven Demolition Team | `targeted-destruction-creature` | {T}: Destroy target Wall. |
| `rule:targeted-destruction-creature` | Rend Spirit | `targeted-destruction-creature` | Destroy target Spirit. |
| `rule:targeted-destruction-creature` | Cast Down | `targeted-destruction-creature` | Destroy target nonlegendary creature. |
| `rule:targeted-destruction-creature` | Assassinate | `targeted-destruction-creature` | Destroy target tapped creature. |
| `rule:targeted-destruction-creature` | Deathmark | `targeted-destruction-creature` | Destroy target green or white creature. |
| `rule:targeted-destruction-creature` | Deadly Precision | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Sagittars' Volley | `targeted-destruction-creature` | Destroy target creature with flying. |
| `rule:targeted-destruction-creature` | Soul Reap | `targeted-destruction-creature` | Destroy target nongreen creature. |
| `rule:targeted-destruction-creature` | Hellish Sideswipe | `targeted-destruction-creature` | Destroy target creature or Vehicle. |
| `rule:targeted-destruction-creature` | Victim of Night | `targeted-destruction-creature` | Destroy target non-Vampire, non-Werewolf, non-Zombie creature. |
| `rule:targeted-destruction-creature` | Slayer of the Wicked | `targeted-destruction-creature` | When this creature enters, you may destroy target Vampire, Werewolf, or Zombie. |
| `rule:targeted-destruction-creature` | Luminous Rebuke | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Organic Extinction | `targeted-destruction-creature` | Destroy all nonartifact creatures. |
| `rule:targeted-destruction-creature` | Daraja Griffin | `targeted-destruction-creature` | Destroy target black creature. |
| `rule:targeted-destruction-creature` | Live or Die | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Breathe Your Last | `targeted-destruction-creature` | Destroy target creature or planeswalker. |
| `rule:targeted-destruction-creature` | Hand of Death | `targeted-destruction-creature` | Destroy target nonblack creature. |
| `rule:targeted-destruction-creature` | Perish | `targeted-destruction-creature` | Destroy all green creatures. They can't be regenerated. |
| `rule:targeted-destruction-creature` | Sandbenders' Storm | `targeted-destruction-creature` | Destroy target creature with power 4 or greater. |
| `rule:targeted-destruction-creature` | Reach of Shadows | `targeted-destruction-creature` | Destroy target creature that's one or more colors. |
| `rule:targeted-destruction-creature` | Ettercap // Web Shot | `targeted-destruction-creature` | Destroy target creature with flying. |
| `rule:targeted-destruction-creature` | Kill Shot | `targeted-destruction-creature` | Destroy target attacking creature. |
| `rule:targeted-destruction-creature` | Death Bomb | `targeted-destruction-creature` | Destroy target nonblack creature. It can't be regenerated. |
| `rule:targeted-destruction-creature` | Murderous Spoils | `targeted-destruction-creature` | Destroy target nonblack creature. It can't be regenerated. |
| `rule:targeted-destruction-creature` | Power Word Kill | `targeted-destruction-creature` | Destroy target non-Angel, non-Demon, non-Devil, non-Dragon creature. |
| `rule:targeted-destruction-creature` | Disruptive Stormbrood // Petty Revenge | `targeted-destruction-creature` | Destroy target creature with power 3 or less. |
| `rule:targeted-destruction-creature` | Scout the City | `targeted-destruction-creature` | Destroy target creature with flying. |
| `rule:targeted-destruction-creature` | Powerstone Fracture | `targeted-destruction-creature` | Destroy target creature or planeswalker. |
| `rule:targeted-destruction-creature` | Hideous End | `targeted-destruction-creature` | Destroy target nonblack creature. |
| `rule:targeted-destruction-creature` | Skywhaler's Shot | `targeted-destruction-creature` | Destroy target creature with power 3 or greater. |
| `rule:targeted-destruction-creature` | Launch Party | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Pawpatch Formation | `targeted-destruction-creature` | Destroy target enchantment. |
| `rule:targeted-destruction-creature` | Feast of Blood | `targeted-destruction-creature` | Destroy target creature. |
| `rule:targeted-destruction-creature` | Artistic Refusal | `targeted-destruction-creature` | Counter target spell. |
| `rule:targeted-destruction-creature` | Triumphant Surge | `targeted-destruction-creature` | Destroy target creature with power 4 or greater. |
| `rule:cant-be-blocked-except-by-count` | Relentless X-ATM092 | `cant-be-blocked-except-by-count` | This creature can't be blocked except by three or more creatures. |
| `rule:cant-be-blocked-except-by-count` | Guile | `cant-be-blocked-except-by-count` | This creature can't be blocked except by three or more creatures. |
| `rule:cant-be-blocked-except-by-count` | Silhana Ledgewalker | `cant-be-blocked-except-by-count` | This creature can't be blocked except by creatures with flying. |
| `rule:cant-be-blocked-except-by-count` | Prowler's Helm | `cant-be-blocked-except-by-count` | Equipped creature can't be blocked except by Walls. |
| `rule:cant-be-blocked-except-by-count` | Meltstrider's Resolve | `cant-be-blocked-except-by-count` | Enchanted creature gets +0/+2 and can't be blocked by more than one creature. |
| `rule:cant-be-blocked-except-by-count` | Signal Pest | `cant-be-blocked-except-by-count` | This creature can't be blocked except by creatures with flying or reach. |
| `rule:cant-be-blocked-except-by-count` | Skirk Shaman | `cant-be-blocked-except-by-count` | This creature can't be blocked except by artifact creatures and/or red creatures. |
| `rule:cant-be-blocked-except-by-count` | Become the Pilot | `cant-be-blocked-except-by-count` | can't be blocked unless it's attacking its owner or a permanent its owner controls |
| `rule:cant-be-blocked-except-by-count` | Ghostform | `cant-be-blocked-except-by-count` | Up to two target creatures can't be blocked this turn. |
| `rule:cant-be-blocked-except-by-count` | Rampaging Ceratops | `cant-be-blocked-except-by-count` | This creature can't be blocked except by three or more creatures. |
| `rule:cant-be-blocked-except-by-count` | Tromokratis | `cant-be-blocked-except-by-count` | Tromokratis can't be blocked unless all creatures defending player controls block it. |
| `rule:cant-be-blocked-except-by-count` | Spire Tracer | `cant-be-blocked-except-by-count` | This creature can't be blocked except by creatures with flying or reach. |
| `rule:cant-be-blocked-except-by-count` | Hexmark Destroyer | `cant-be-blocked-except-by-count` | This creature can't be blocked except by six or more creatures. |
| `rule:cant-be-blocked-except-by-count` | Orchard Spirit | `cant-be-blocked-except-by-count` | This creature can't be blocked except by creatures with flying or reach. |
| `rule:cant-be-blocked-except-by-count` | Graxiplon | `cant-be-blocked-except-by-count` | This creature can't be blocked unless defending player controls three or more creatures that share a creature  |
| `rule:cant-be-blocked-except-by-count` | Run for Your Life | `cant-be-blocked-except-by-count` | They can't be blocked this turn except by creatures with haste. |
| `rule:cant-be-blocked-except-by-count` | Phyrexian Colossus | `cant-be-blocked-except-by-count` | This creature can't be blocked except by three or more creatures. |
| `rule:cant-be-blocked-except-by-count` | Gutter Skulker // Gutter Shortcut | `cant-be-blocked-except-by-count` | This creature can't be blocked as long as it's attacking alone. |
| `rule:cant-be-blocked-except-by-count` | Treetop Rangers | `cant-be-blocked-except-by-count` | This creature can't be blocked except by creatures with flying. |
| `rule:cant-be-blocked-except-by-count` | Stalking Tiger | `cant-be-blocked-except-by-count` | This creature can't be blocked by more than one creature. |
| `rule:cant-be-blocked-except-by-count` | Treetop Scout | `cant-be-blocked-except-by-count` | This creature can't be blocked except by creatures with flying. |

## Part 7 — SAME-RUN DUPLICATE COLLAPSE

The model emitted the same (card, label) more than once in 44 cases; 42 of those carry DIFFERENT
evidence quotes across the emissions. The schema cannot hold two assertions
with the same (class, source_ref) — it halts — so a collapse rule was
ratified: collapse to one assertion, lane precedence
`codebook` > `codebook-grammar` > free-promoted, quote tie-break = first in
deterministic parse order.

| card | slug | emissions | lanes | winning lane | quotes differ |
|---|---|---|---|---|---|
| Stone Kavu | `rule:mana-activated-pump-self` | 2 | codebook | codebook | True |
| Voice of the Blessed | `rule:grants-ability-at-threshold-self` | 2 | codebook | codebook | True |
| Nucklavee | `rule:graveyard-to-hand-recursion` | 2 | codebook | codebook | True |
| Fists of the Demigod | `rule:conditional-buff-by-color` | 2 | codebook | codebook | True |
| Creakwood Liege | `rule:tribal-anthem-buff` | 2 | codebook | codebook | True |
| Mishra, Claimed by Gix | `rule:attack-trigger-drain-scales-with-attacker-count` | 2 | free | free | False |
| Aetheric Amplifier | `rule:doubles-counter-placement` | 2 | codebook | codebook | True |
| Wormwood Treefolk | `rule:activated-grant-landwalk-self-damage-cost` | 2 | free | free | True |
| Pyrite Spellbomb | `rule:activated-ability-costs-self-sacrifice` | 2 | codebook | codebook | True |
| Resolute Rider | `rule:self-mana-ability-grants-keyword` | 2 | codebook | codebook | True |
| Greenwarden of Murasa | `rule:graveyard-to-hand-recursion` | 2 | codebook | codebook | True |
| Izzet Guildmage | `rule:copies-cast-spell` | 2 | codebook | codebook | True |
| Reign of Chaos | `rule:destroys-land-and-matching-color-creature` | 2 | free | free | True |
| Infected Vermin | `rule:mass-damage-creatures-and-players` | 2 | codebook | codebook | True |
| Utopia Mycon | `rule:counter-removal-as-activation-cost` | 2 | codebook | codebook | False |
| Scourge of the Nobilis | `rule:conditional-buff-by-color` | 2 | codebook | codebook | True |
| Boartusk Liege | `rule:tribal-anthem-buff` | 2 | codebook | codebook | True |
| The Mirari Conjecture | `rule:graveyard-to-hand-recursion` | 2 | codebook | codebook | True |
| Nemesis of Mortals | `rule:cost-reduction-scales-with-own-graveyard-creatures` | 2 | free | free | True |
| Kjeldoran Knight | `rule:mana-activated-pump-self` | 2 | codebook | codebook | True |
| Helm of the Ghastlord | `rule:conditional-buff-by-color` | 2 | codebook | codebook | True |
| Runes of the Deus | `rule:conditional-buff-by-color` | 2 | codebook | codebook | True |
| Clout of the Dominus | `rule:conditional-buff-by-color` | 2 | codebook | codebook | True |
| Mayor of Avabruck // Howlpack Alpha | `rule:tribal-anthem-buff` | 2 | codebook | codebook | True |
| Victory of the Pyrohammer | `rule:mass-damage-creatures-and-players` | 2 | codebook | codebook | True |
| Death-Hood Cobra | `rule:self-mana-ability-grants-keyword` | 2 | codebook | codebook | True |
| Thistledown Liege | `rule:tribal-anthem-buff` | 2 | codebook | codebook | True |
| Garruk Relentless // Garruk, the Veil-Cursed | `rule:create-token-creature` | 2 | codebook-grammar | codebook-grammar | True |
| Colossal Skyturtle | `rule:channel-discard-for-effect` | 2 | codebook | codebook | True |
| Shark Typhoon | `rule:create-token-creature` | 2 | codebook-grammar | codebook-grammar | True |
| Steel of the Godhead | `rule:conditional-buff-by-color` | 2 | codebook | codebook | True |
| Aven Brigadier | `rule:tribal-anthem-buff` | 2 | codebook | codebook | True |
| Bant Battlemage | `rule:temporary-keyword-grant` | 2 | codebook | codebook | True |
| Shield of the Oversoul | `rule:conditional-buff-by-color` | 2 | codebook | codebook | True |
| Hallowed Healer | `rule:prevent-fixed-damage-any-target` | 2 | codebook | codebook | True |
| Foundry Champion | `rule:mana-activated-pump-self` | 2 | codebook | codebook | True |
| Crosis's Charm | `rule:targeted-destruction` | 2 | codebook | codebook | True |
| Cliffrunner Behemoth | `rule:conditional-buff-by-color` | 2 | codebook | codebook | True |
| Voracious Hatchling | `rule:cast-trigger-removes-negative-counter-by-color` | 2 | free | free | True |
| Balefire Liege | `rule:tribal-anthem-buff` | 2 | codebook | codebook | True |
| Brightcap Badger // Fungus Frolic | `rule:create-token-creature` | 2 | codebook-grammar | codebook-grammar | True |
| Water Servant | `rule:mana-activated-pump-self` | 2 | codebook | codebook | True |
| Helvault | `rule:targeted-exile` | 2 | codebook | codebook | True |
| Cabal Torturer | `rule:activated-debuff-target-creature` | 2 | free | free | True |

## Part 8 — ROUTING, TAXONOMY, AND REPORT ROWS

### Killed/merged/renamed-slug routing (closed action vocabulary)

| card | slug | status | action | reason |
|---|---|---|---|---|
| Nadaar, Selfless Paladin | `rule:venture-into-dungeon` | killed | discovery | R10 mechanism/keyword kill -> discovery + ledger flag. Killed at batch 2 as 'Venture into the Dungeon keyword mechanism, ledger candidate'; the mechanism has no axis home |
| River Boa | `rule:activated-regenerate-self` | killed | report | R8.3 ratified that this axis is being AUTHORED properly via the DET path, with a drafted pattern and a fixed-seed sample sheet, going live only on Captain's pattern ratif |

### Taxonomy items

**revivals_to_deferred**

- `rule:grants-haste-to-reanimated-creature` — R8.2: delivery-context grant, legitimate per R7/A7 (the analogue rule:grants-haste-to-created-tokens is active and DET-owned at n=102). Enters deferred per A2 pending its DET pattern (session 4).
- `rule:grants-team-trample` — R8.1: scope-faceted keyword grant, legitimate per R7/A7 (the analogue rule:grants-haste-to-your-creatures is active and DET-owned). Revival law applies; enters deferred per A2 pending its DET pattern (session 4).

**kill_note_corrections**

- `rule:grants-haste-to-token` — duplicate of rule:grants-haste-to-created-tokens
- `rule:sacrifice-as-additional-cost` — duplicate-of-live-axis (rule:additional-cost-sacrifice-permanent)
- `rule:sacrifice-self-as-activation-cost` — duplicate-of-live-axis (rule:activated-ability-costs-self-sacrifice)

**whole_slug_aliases**

- `rule:grants-haste-to-token → rule:grants-haste-to-created-tokens` — A6: WHOLE-SLUG alias in the routing artifact. Explicitly NOT a global token->created-tokens synonym, which would corrupt the 28 active slugs carrying the bare token `token`.

### Report rows (deferred to Captain, no action planned)

- **node-report-only** — collides with a RENAMED shell (renamed_to='rule:draw-second-card-trigger-plus1-counter') that still holds 2 legacy audit row(s). R7 makes this a REPORT ROW for Captain: the node's payoff sense and the rename target's sense differ, and instantiating would overwrite retained audit rows.
- **node-redirect** — collides with a KILLED axis. R7/A7: bare unscoped grants are engine-redundant and stay killed; the member routes to rule:temporary-keyword-grant per the ratified b4-D4 standing rule (A10).
- **routing-discovery** — R10 mechanism/keyword kill -> discovery + ledger flag. Killed at batch 2 as 'Venture into the Dungeon keyword mechanism, ledger candidate'; the mechanism has no axis home and the ledger is where it is tracked.
- **routing-report** — R8.3 ratified that this axis is being AUTHORED properly via the DET path, with a drafted pattern and a fixed-seed sample sheet, going live only on Captain's pattern ratification in session 4. Routing this hit now would pre-empt that ratification; regeneration currently has no active home, so it is a report row until session 4 gives it one.
- **placeholder-clusters** — A15 names ONE `<state>`-placeholder cluster (10 rows) as report-only. Measurement finds 15 placeholder-bearing clusters totalling 26 rows — SYNTH emitted grammar facet placeholders verbatim more widely than the ratification recorded. All are report-only; none are promoted. Flagged because the ratified text and the measured data differ in scope.
- **det-synth-convergence** — 97 free-lane instances flagged as DET-convergent; discovery-lane only, no action in this plan.

## Part 9 — RATIFIED CONSTRAINTS (prior rulings, not open questions)

Flag it if a decision above violates one of these.

- **A2** — a revived axis enters `deferred`, never active-at-n=0.
- **A5** — class = who made the PER-CARD judgment. Bulk transformation of
  model output is `llm` even when the RULE was Captain-ratified.
- **A6** — the token→created-tokens synonym is a WHOLE-SLUG alias, not a
  global token map (a global map would corrupt 28 active slugs).
- **A8** — a rule-derived refresh replaces only its own assertions and
  never touches a human or llm assertion on the same member.
- **A11** — members hold DIRECT assertions only; parent rollups stay
  derived views.
- **A14** — killed-slug routing is a closed data vocabulary with every
  instance enumerated; no runtime "does the quote fit" judgment. No drift
  tolerances: exact match or halt. Evidence quotes never printed to console.
- **R7** — faceted keyword-grant axes (scope / delivery / context) are
  legitimate; only BARE grant axes are engine-redundant.
- **R9** — vocabulary additions are ratified like any other constant:
  proposed with evidence in the consolidation session, applied on approval.
- **R12 superseded by A1** — run-1 confirmations of cards already on an
  axis were originally to be discarded as no-ops; they now merge as llm
  assertions instead. This reversal is deliberate and worth checking.

## Part 10 — THE GOVERNING DIRECTIVE (verbatim)

<!-- BEGIN VERBATIM 2A -->
# CONSOLIDATION-2A-CLASSIFY-DIRECTIVE — the decisions, alone (session 2a of 5)

ZERO MUTATION, ZERO API SPEND. This session computes and writes ONE
artifact — every consolidation DECISION, and nothing mechanical — then
STOPS. Nothing touches codebook.json or grammars.json.

Governed by B-MIGRATION-DISCOVERY.md §10 (A1–A15) and §9 where unamended.
Supersedes, with CONSOLIDATION-2B-ENUMERATE-DIRECTIVE.md, the single-session
CONSOLIDATION-PLAN-DIRECTIVE.md.

**Why this session exists separately.** The full plan enumerates ~18,346
rows at ~425 B each — ~7.8 MB, ~1.95M tokens — because every row carries an
A1 assertion with a quote. That cannot be externally audited at all, at any
sampling rate that would mean anything. The decisions inside it are ~1,000
rows, ~350 KB, ~88K tokens, and CAN be audited whole. So the judgment is
extracted, audited, and frozen FIRST; the mechanical expansion happens once,
afterwards, against an approved decision set. An adverse audit finding then
invalidates a small artifact instead of a 7.8 MB one.

PRECONDITION (verify in the state-check, else HALT): session 1 complete —
codebook.json schema `foundry-codebook/2`, lint clean, independent verifier
clean. Record the live codebook sha256 in the artifact; 2b and session 3
both check against it.

## 1. Inputs

corpus_pass_run1_parsed_final.json · corpus_pass_run1_discovery.json ·
corpus_pass_run1_consolidation_dry_run.json (reference only — recompute,
never trust) · the det_synth check artifact · docs/grammars.json ·
validate_slug.py · the /2 codebook (READ-ONLY, via
foundry_codebook.load_codebook) · gated corpus.

## 2. Build `experiments/out/foundry/corpus_pass_run1_classification.json`

Schema `foundry-consolidation-classification/1`. Deterministic (×2
byte-identical). Records input hashes and the live codebook sha256. Every
decision is enumerated by slug and, where it is a per-card decision, by
oracle_id. No aggregates without their underlying lists.

1. **node_classification** — the 95 grammar virtual-node candidates
   (AG-COUNT-01), each classified into the closed vocabulary:
   `instantiate` / `join-existing` / `redirect` / `report-only` /
   `collision-killed` / `collision-renamed`. Category totals must sum to
   exactly 95. Expected per A14/R7: 93 instantiate; `rule:grants-haste` →
   redirect-per-D4 (Zidane, Tantalus Thief → `rule:temporary-keyword-grant`);
   `rule:draw-second-card-trigger-token` → report-only. Deviations from that
   expectation are allowed but must be stated and justified in the human
   summary — the expectation is a prior, not a gate.

2. **killed_slug_routing** — the `foundry-killed-slug-routing/1` artifact
   (A14/H-02/R10). Every killed-, merged-, or renamed-slug hit enumerated
   with a closed action — `redirect` / `split` / `report` / `discovery` /
   `reject` — and explicit targets. M8-violating combo labels list their
   per-class split targets. NO runtime predicates: no "if the quote fits",
   no similarity thresholds. Every instance is decided HERE, by name.

3. **promotions** —
   - R5: the 141 exact-match free-lane reinventions, split into the 45 new
     members and the 96 already-member merges, each row listed.
   - A15: the 213 rows, EACH re-validated through `validate_slug` exactly as
     a grammar-lane label would be. Rows that fail validation fall back to
     discovery and are listed as such with the failure reason.
     `original_lane` / `effective_lane` recorded per row. The
     `<state>`-placeholder cluster's 10 rows are report-only.

4. **taxonomy_items** — each stated as the EXACT history-entry text 2b will
   emit: revivals entering `deferred` per A2 (never active-at-n=0), the two
   kill-note corrections (R8.4, R8.5), the whole-slug alias per A6
   (`rule:grants-haste-to-token` → `rule:grants-haste-to-created-tokens`;
   NOT a global token→created-tokens synonym, which would corrupt 28 active
   slugs).

5. **same_run_duplicates** — the measured intra-run duplicate emissions
   (run 1: 35 codebook-lane + 3 grammar-lane + 6 free-lane) enumerated by
   (slug, oracle_id), each RESOLVED here per the Captain-ratified collapse
   rule: same-run emissions collapse to a single assertion; lane precedence
   `codebook` > `codebook-grammar` > free-promoted; quote tie-break = first
   in deterministic parse order. Record the winning lane and quote for each.
   This category exists so 2b performs a LOOKUP, never a policy decision —
   it is the one genuine judgment that would otherwise hide inside 2b's
   "mechanical" expansion. Also enumerate any cross-lane same-run pair
   arising from A15 canonical-form promotion (raw-label overlap measured 0;
   canonical-form overlap has never been computed — compute it).

6. **expected_counts** — the closed-loop contract with 2b. Per category:
   how many member_additions, how many assertion_merges, how many new axes,
   how many rows of each promotion type, how many report rows. 2b's
   expansion must reproduce these EXACTLY or halt. This is what makes an
   audit of 2a alone meaningful: a 2b expander bug is otherwise precisely
   the thing an external reviewer of 2a cannot see.

7. **report_rows** — everything deferred to Captain's eyes, with counts and
   the reason each is deferred.

8. **human_summary** — a Captain-readable section INSIDE the artifact:
   category totals, the full 95-node classification table, notable rows, and
   any deviation from the priors in item 1. This section plus the
   enumerations is what the external reviewer reads.

## 3. Reporting and stop

Print counts and slugs only. Quotes go to the artifact, never to console
(A14). Commit the generator script; the artifact itself is gitignored output
— record its sha256 in the report.

Then STOP. In order:

1. Captain reviews the artifact.
2. **A12 EXTERNAL RE-AUDIT CHECKPOINT.** Assemble
   `docs/B-CONSOLIDATION-REAUDIT-PACKET.md`: the amended schema
   (B-MIGRATION-DISCOVERY.md §10 A1) + this artifact's `human_summary` +
   the FULL enumeration of items 1–5 (they fit — that is the point of this
   split) + `expected_counts` + the same red-team charge and disclosure the
   first packet carried. Captain runs it past a DIFFERENT MODEL FAMILY.
   A same-family check does not discharge this.
3. Session 2b runs only on Captain's explicit go, naming the classification
   artifact's sha256 it approves.

Spend $0.00 / cumulative $90.51 / headroom $49.49.

## 4. Standing discipline

Zero mutation of codebook.json/grammars.json under any circumstance · halt
loudly · verify-or-drop · transcript hygiene (quotes to files only) · G1 ·
G4 · determinism ×2 on the artifact · one session, this work item only.
<!-- END VERBATIM 2A -->

---

Artifact under review: `corpus_pass_run1_classification.json`, sha256
`7f0a83c7e20007a67252d1bf7e33acda8c99e5e6489df9098a39bf7c276792b1`.
Codebook state at classification: sha256
`61af1a1d7f81504f422feb4d35aff14aee890dcc892338e882766def93e66522`.
