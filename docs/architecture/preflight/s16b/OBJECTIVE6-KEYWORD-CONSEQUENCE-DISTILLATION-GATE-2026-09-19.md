# Objective 6 — Keyword Consequence Distillation Gate

Status: **CAPTAIN-DIRECTED PRE-CORPUS SEMANTIC REQUIREMENT — NOT A CORPUS EXECUTION AUTHORIZATION**

Date: 2026-09-19

## 1. Purpose

Before broad corpus semantic analysis, Foundry must perform a dedicated distillation pass over Magic keyword abilities, keyword actions, ability words where relevant, and other compact rules constructs whose printed name or reminder text expands into multiple gameplay events.

The purpose is to define those consequences **once, upstream**, rather than forcing card-by-card analysis to rediscover the same rules expansion repeatedly.

Governing principle:

> **Distill compound rules constructs before corpus classification. A keyword is not merely a label; it may be a producer of multiple independently searchable game events.**

This requirement exists because downstream cards may independently care about any event emitted by a keyword. Searcher B must therefore be able to surface relationships through the keyword's constituent gameplay consequences, not only through shared keyword names.

## 2. Why this must precede broad corpus analysis

A flat assertion such as `myriad = true` or `mobilize = true` is semantically insufficient.

A single compact keyword can imply several distinct facts, for example:

- an attack-triggered ability occurs;
- tokens are created;
- permanents enter the battlefield;
- creatures enter tapped and attacking;
- copies are created;
- delayed triggered abilities are established;
- permanents later leave the battlefield;
- the departure may be exile or sacrifice;
- sacrifice can ordinarily produce death events;
- exile can satisfy effects that care about permanents being exiled;
- created copies may carry ETB, LTB, combat-damage, static, activated, and other copied abilities;
- creatures that enter attacking were not declared as attackers and therefore do not themselves satisfy ordinary `when/whenever this creature attacks` trigger conditions.

Cards elsewhere in the corpus may care about each of those facts independently.

Therefore the semantic substrate must preserve the expanded event/output structure so that a search for one card can surface cards related through any relevant emitted event or consumed event.

## 3. Required pre-corpus deliverable

Create a **Keyword Consequence Registry** before broad corpus semantic derivation.

For every in-scope compact rules construct, record at minimum:

1. **Canonical rules identity**
   - keyword/ability-word/action name;
   - rules reference/version;
   - whether the construct has independent Comprehensive Rules meaning.

2. **Trigger or activation architecture**
   - trigger condition;
   - activated/static/replacement/triggered classification;
   - source object requirements;
   - whether the event is optional or mandatory.

3. **Immediate operations**
   - objects/cards/permanents affected;
   - tokens created;
   - copies produced;
   - zones changed;
   - counters/resources created or consumed;
   - damage, life change, draw, discard, sacrifice, exile, etc.

4. **Produced event signatures**
   - attack event;
   - token-created event;
   - permanent/creature ETB;
   - combat-damage event;
   - LTB event;
   - dies event;
   - exile event;
   - sacrifice event;
   - spell/ability-copy event;
   - other mechanically observable consequences.

5. **Delayed or scheduled consequences**
   - delayed trigger creation;
   - timing of cleanup or later action;
   - exact destination/mechanism of departure.

6. **Negative facts / non-events**
   - facts that look superficially similar but do **not** occur;
   - example: a creature that enters tapped and attacking was not declared as an attacker and does not thereby generate its own attack trigger.

7. **Inheritance / payload propagation**
   - whether created copies inherit abilities;
   - whether those abilities can independently trigger or activate;
   - ETB/LTB/death/combat-damage consequences of the copied object.

8. **Downstream semantic projections**
   - mechanical primitives implicated;
   - functional families that may be derived from the actual payload;
   - producer signatures exposed to synergy search;
   - consumer signatures other cards may listen for.

9. **Context-sensitive caveats**
   - replacement effects;
   - multiplayer cardinality;
   - optionality;
   - token-vs-card distinctions;
   - player/permanent/card distinctions;
   - destination-specific trigger behavior.

## 4. Producer/consumer event-signature requirement

Foundry should model semantic relationships in both directions:

> **Producer:** what events, objects, resources, and state transitions can this card/effect cause?

> **Consumer:** what events, objects, resources, and state transitions does another card/effect listen for, modify, reward, replace, or depend upon?

The MTG Thesaurus must be able to connect cards through these signatures even when their Oracle wording and named mechanics differ.

Example: a card with Myriad should be discoverable not only beside other Myriad cards, but potentially beside cards that care about token creation, creature ETBs, copied permanents, combat damage, permanents leaving the battlefield, or permanents being exiled, where the actual rules relationship supports that connection.

## 5. Pilot fixture A — Myriad

Myriad is a required adversarial fixture for this registry.

Canonical consequence map, subject to exact current Comprehensive Rules wording at implementation time:

1. The source creature is declared as an attacker.
2. Myriad triggers from that attack.
3. For each opponent other than the defending player, the controller may create a token copy of the source creature that is tapped and attacking that opponent or a planeswalker they control, as defined by the current rule.
4. Creating those objects emits token-generation and copy events.
5. The created creature-token permanents enter the battlefield.
6. Their ETB abilities, if any, can trigger.
7. They enter attacking but were not declared as attackers; their own ordinary attack-triggered abilities do not trigger merely from entering attacking.
8. The copies carry the source creature's copied characteristics and abilities, so their combat-damage/Saboteur abilities and other applicable abilities can operate independently.
9. Myriad establishes a delayed cleanup instruction that exiles the generated tokens at end of combat under the current rule.
10. That cleanup causes the tokens to leave the battlefield and be exiled.
11. LTB effects may therefore care about the departure.
12. Effects that care about a permanent being exiled may care about that exile when their exact conditions are satisfied.
13. Normal Myriad cleanup is **not a death event**, because the token permanent moves from battlefield to exile rather than battlefield to graveyard.

Representative event/output signatures include:

- `attack_trigger`
- `copying: token_copy`
- `token_created`
- `creature_token_created`
- `permanent_enters_battlefield`
- `creature_enters_battlefield`
- `enters_tapped`
- `enters_attacking`
- `not_declared_as_attacker`
- `multiplayer_scaled_copy_generation`
- `possible_combat_damage_to_player`
- `possible_copied_saboteur_trigger`
- `delayed_cleanup`
- `permanent_leaves_battlefield`
- `permanent_exiled_from_battlefield`
- `not_dies_from_normal_cleanup`

## 6. Pilot fixture B — Mobilize

Mobilize is a second required adversarial fixture because it resembles Myriad while diverging at important event boundaries.

Canonical consequence map, subject to exact current Comprehensive Rules wording at implementation time:

1. The source creature is declared as an attacker.
2. Mobilize triggers from that attack.
3. Mobilize N creates N 1/1 red Warrior creature tokens.
4. The tokens enter tapped and attacking.
5. Token creation and creature/permanent ETB events occur.
6. The tokens were not declared as attackers, so they do not themselves generate ordinary attack triggers merely by entering attacking.
7. Mobilize establishes a delayed instruction to **sacrifice those tokens at the beginning of the next end step**.
8. Sacrificing the tokens is distinct from Myriad's exile cleanup.
9. Under ordinary resolution absent an applicable replacement effect, sacrificing a creature moves it from the battlefield to its owner's graveyard and therefore produces:
   - a sacrifice event;
   - a creature/permanent leaves-the-battlefield event;
   - a battlefield-to-graveyard zone transition;
   - a dies event.
10. Cards that care about sacrifice, death, LTB, creature ETB, token creation, Warrior creation, or related events may therefore interact with different parts of Mobilize's consequence chain.

Representative event/output signatures include:

- `attack_trigger`
- `token_created`
- `creature_token_created`
- `warrior_token_created`
- `permanent_enters_battlefield`
- `creature_enters_battlefield`
- `enters_tapped`
- `enters_attacking`
- `not_declared_as_attacker`
- `delayed_cleanup`
- `sacrifice_event`
- `permanent_leaves_battlefield`
- `creature_leaves_battlefield`
- `battlefield_to_graveyard`
- `dies_event` under ordinary unmodified resolution

### Myriad vs Mobilize — important contrast

Both can produce attack triggers, creature-token creation, ETBs, tapped-and-attacking creatures, and later LTB events.

Their cleanup semantics materially differ:

- **Myriad:** delayed **exile** at end of combat -> LTB + exile, normally **not death**.
- **Mobilize:** delayed **sacrifice** at the beginning of the next end step -> sacrifice + LTB + ordinarily death/battlefield-to-graveyard.

This difference must survive extraction. It is directly relevant to synergy discovery.

## 7. Candidate families for the distillation pass

The registry should not be limited to Myriad and Mobilize. Before broad corpus analysis, perform a systematic census of compact rules constructs that expand into multiple observable consequences.

Likely candidates include, without prejudging final treatment:

- Myriad
- Mobilize
- Encore
- Blitz
- Unearth
- Dash
- Evoke
- Exploit
- Casualty
- Offspring
- Squad
- Populate
- Connive
- Explore
- Discover
- Cascade
- Demonstrate
- Rebound
- Suspend
- Foretell
- Plot
- Mutate
- Manifest / Manifest Dread
- Cloak
- Craft
- Disturb
- Escape
- Harmonize
- Living weapon / For Mirrodin!
- Amass
- Incubate
- Backup
- Adapt / Monstrosity / Evolve where multi-event consequences matter
- keyword actions or ability words whose expansion exposes independently searchable events.

This list is a **census seed**, not a frozen ontology. The actual pass must derive scope from the current rules corpus rather than assuming this list is complete.

## 8. Distillation methodology

For each candidate construct:

1. read the current Comprehensive Rules entry and current official release/rules notes where needed;
2. write the minimal exact rules expansion;
3. enumerate emitted mechanical events and objects;
4. enumerate delayed events and exact destinations;
5. record relevant non-events;
6. identify which payload abilities propagate through copies/tokens/new objects;
7. identify ordinary downstream triggers without pretending contextual replacement effects are guaranteed;
8. define machine-readable producer signatures;
9. define likely consumer signatures;
10. test with representative positive, negative, and near-miss cards;
11. preserve the resulting canonical expansion in the registry;
12. only then allow card-level semantic derivation to invoke that registry entry.

## 9. Corpus execution rule

Broad corpus extraction should treat a recognized compound keyword as a call to the canonical consequence registry, not as an invitation to independently reinterpret the keyword per card.

Conceptually:

`Oracle/rules evidence`

-> `keyword recognition`

-> `canonical keyword consequence expansion`

-> `card-specific payload/context overlay`

-> `event/output signatures`

-> `functional semantic derivation`

-> `adversarial/ambiguity gate`

-> `accepted assertions`

The registry provides the stable mechanical expansion. The card-specific pass still evaluates the surrounding text, copied payload, quantities, restrictions, replacement effects, and functional consequences.

## 10. User-facing explanation requirement

The same consequence map should power concise player explanations.

A player looking at a Myriad card should not merely see `Myriad`.

Foundry should be able to explain, in compact human language, that attacking can create temporary token copies that enter tapped and attacking, can trigger their own applicable ETB/combat-damage abilities, and are later exiled, thereby creating LTB/exile interactions but not normal death interactions.

Likewise, a Mobilize card should communicate that attacking creates temporary Warrior creature tokens that enter tapped and attacking and are later sacrificed, enabling sacrifice/death/LTB interactions.

The explanation must derive from the same facts that power search and synergy discovery.

## 11. Gate condition

Before broad Objective 6 corpus semantic analysis begins, the Manager/Worker process should be able to demonstrate:

- a current rules-derived census of compound keyword/action/ability-word constructs;
- canonical consequence maps for in-scope constructs;
- machine-facing producer/consumer event signatures;
- explicit distinction between guaranteed events, ordinary/default downstream consequences, and context-dependent consequences;
- negative/non-event facts where rules subtleties matter;
- adversarial fixtures covering at least Myriad and Mobilize;
- deterministic reuse of those definitions by card-level analysis.

Failure to have this layer is a **pre-corpus semantic readiness defect**, because card-by-card analysis would otherwise duplicate rules reasoning and risk inconsistent downstream semantics.

## 12. Control boundary

This document does **not** authorize:

- broad corpus reclassification;
- S16B freeze;
- implementation acceptance;
- AQ4 resumption;
- Bridge v0 activation;
- Step6;
- merge;
- movement of accepted implementation head or `main`.

It records a Captain-directed semantic preparation requirement for Objective 6.
