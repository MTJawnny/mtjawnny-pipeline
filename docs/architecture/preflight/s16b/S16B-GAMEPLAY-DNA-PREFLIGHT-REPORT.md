# S16B Gameplay-DNA Preflight Research

**Status:** OBJECTIVE 5 RESEARCH EVIDENCE COMPLETE / S16B IMPLEMENTATION **NOT AUTHORIZED**  
**Date:** 2026-09-12  
**Accepted implementation head intentionally unchanged:** `9f92039eb9c7132a351576c31472eb30a2957a67`  
**Evidence branch:** `preflight/objective5-s16b-gameplay-dna-2026-09-12`  
**Dependency:** S16A lossless semantic parse must be accepted before S16B implementation may begin.  
**Authority boundary:** Oracle/CR mechanical truth remains separate from derived functional jobs and community strategy vocabulary.

## Executive result

Objective 5 supports the product thesis that a useful MTG thesaurus needs a **derived functional layer above mechanical facts**. The current S9 system is intentionally narrower: it can only retrieve a card when anchor and candidate share at least one ACTIVE axis, then orders by shared-axis count and axis specificity. That is a valid mechanical baseline, but it cannot represent a relationship whose shared parent is a gameplay job rather than an existing shared axis.

The strongest seed example is Grand Abolisher and Defense Grid. Their current Oracle text implements different mechanisms: Grand Abolisher prohibits opposing spells and selected activated abilities during its controller's turn, while Defense Grid taxes spells cast outside each spell controller's turn. Community sources nevertheless compare Defense Grid directly to Grand Abolisher when the desired job is protecting a proactive turn from opposing interaction. The functional parent is therefore useful, but the child mechanics remain essential because their coverage and failure modes differ.

The second seed, Plunge into Darkness and Dig Through Time, shows the same architecture from another direction. Both can perform deep selective library access, yet their payment resource, selection depth, retained quantity, and rejected-card destination differ. A functional parent can make them discoverable together without pretending they are mechanically equivalent.

The research also finds a necessary counterexample to naive community-tag ingestion: **ramp** is widely used but not uniformly scoped. EDHREC's current guide deliberately defines ramp broadly enough to include multiple permanent types, cost reducers, and other accelerants; Commander discussions disagree about whether one-shot rituals belong under the same term. The correct architecture is to keep the objective coordinate `temporary vs repeatable mana acceleration` and preserve the vocabulary dispute, not force Dark Ritual into a universal true/false `ramp` fact.

The preflight therefore recommends:

1. preserve S16A/Foundry mechanical truth as the lower substrate;
2. derive functional job memberships downstream with explicit rules and provenance;
3. model functional jobs as a multi-parent DAG/lattice rather than a single role tag;
4. keep context-free similarity separate from deck/archetype/metagame similarity;
5. benchmark candidate discovery, ordering, and explanation separately;
6. make `UNKNOWN / INSUFFICIENT_EVIDENCE` a first-class result;
7. freeze open labels and a blind holdout before any S16B implementation.

No parser, runtime package, codebook, authority selector, migration state, accepted head, AQ4 state, Bridge v0 state, or production data was changed by this objective.

---

# 1. Research methodology and reliability rubric

## 1.1 Evidence classes

The preflight used five evidence classes and did not allow a lower class to override a higher-class mechanical fact.

| Class | Intended use | Reliability rule |
|---|---|---|
| **A. Oracle / Comprehensive Rules** | What a card or game object actually does | Highest authority for mechanics. Production must use the pinned local corpus and current CR, not a web paraphrase. |
| **B. Current card-text mirror** | Convenient preflight cross-check of current Oracle wording | High for transcription when consistent, but must be rederived from pinned Scryfall bulk before benchmark freeze. This research used `mtg.wtf` for many card-text checks. |
| **C. Established editorial / strategy source** | Community vocabulary, role definitions, archetype practice | Useful for how players categorize cards. Never canonical mechanical truth. EDHREC guides are the main source in this class. |
| **D. Deck primer / direct comparison** | Evidence that players intentionally substitute or compare two different mechanisms for a job | Stronger for a specific functional relation than a generic tag. Must still be Oracle-cross-checked. Cross-posted primers count as one lineage, not multiple independent corroborations. |
| **E. Forum / Reddit discussion** | Vocabulary usage, disagreement, edge cases, lived substitution experience | Useful to detect ambiguity and terminology conflicts. Never sufficient alone for a load-bearing semantic rule. |
| **P. Project precommit / measurement** | Existing human-frozen relevance panels and measured S9 behavior | High for project history and baseline behavior. Explicitly not semantic authority for new S16B labels. |

## 1.2 Claim-level evidence law

Every strategic or functional claim intended to influence S16B must carry, at minimum:

- claim id;
- source URL or repository reference;
- source title/provider;
- publication/update date when available;
- access date;
- source class;
- paraphrased claim;
- named cards / roles;
- claim category: mechanical, functional, strategic, vocabulary, benchmark;
- reliability/confidence;
- Oracle/CR/Foundry cross-check status;
- corroborating sources;
- conflicting sources or terminology;
- whether the source is independent or likely derivative/cross-posted.

The machine-readable preflight store is `claims.jsonl` in this directory.

## 1.3 Anti-folklore rules

A statement such as “X is basically Y” is not imported directly. It must be decomposed into:

1. the literal mechanics of X and Y;
2. the stated or observed gameplay job being compared;
3. coordinates on which they agree;
4. coordinates on which they differ;
5. the context in which the comparison is asserted;
6. the provenance and independence of the sources.

If a community label is overloaded, the conflict is retained. If a comparison only works inside an archetype, the relation is contextual rather than context-free. If current Oracle text contradicts a strategy source, Oracle wins and the strategy source is stale or wrong.

## 1.4 Key sources reviewed

Representative sources used in this preflight include:

- Current Comprehensive Rules, effective 2026-08-07, from the project rules reference.
- Grand Abolisher current Oracle mirror: <https://mtg.wtf/card/c14/74/Grand-Abolisher>
- Defense Grid current Oracle mirror: <https://mtg.wtf/card/mps/34/Defense-Grid>
- Plunge into Darkness current Oracle mirror: <https://mtg.wtf/card/5dn/57/Plunge-into-Darkness>
- Dig Through Time current Oracle mirror: <https://mtg.wtf/card/soc/195/Dig-Through-Time>
- EDHREC, “Ramp in Commander”: <https://edhrec.com/guides/the-edhrec-guide-to-ramp-in-commander>
- EDHREC, “How to Build a Commander Deck”: <https://edhrec.com/guides/how-to-build-a-commander-deck>
- EDHREC, “Mechanical Memories - Bored of Board Wipes?”: <https://edhrec.com/articles/mechanical-memories-bored-of-board-wipes>
- EDHREC, cEDH Stax guide: <https://edhrec.com/guides/edhrec-guide-to-cedh-stax>
- EDHREC, “Commander Outlet” sacrifice-outlet article: <https://edhrec.com/articles/too-specific-top-10-commander-outlet>
- EDHREC, cantrip discussion: <https://edhrec.com/articles/technically-playable-tura-kennerud-skyknight>
- EDHREC, Game Changer alternatives / Cyclonic Rift comparison: <https://edhrec.com/articles/top-10-game-changer-alternatives>
- EDHREC, sideboard thought experiment / graveyard-hate alternatives: <https://edhrec.com/articles/what-if-commander-had-sideboards>
- TappedOut, direct Grand Abolisher replacement discussion: <https://tappedout.net/mtg-forum/deck-help/replacement-for-grand-abolisher/>
- MTGGoldfish Food Chain deck primer comparing Plunge into Darkness with Dig Through Time: <https://www.mtggoldfish.com/deck/3927724>
- Accepted repository S9 implementation: `src/mtj_foundry/thesaurus/retrieval.py` at `9f92039...`.
- Frozen M2 evaluation fixture: `refoundation/path-e/m2-evaluation.json`.

---

# 2. Community vocabulary lexicon

The machine-readable lexicon is `vocabulary-v0.json`.

The key methodological finding is that useful vocabulary falls into different epistemic classes. It cannot be treated as one flat tag list.

## 2.1 Stable and useful role terms

Terms with strong community usage and a reasonably understandable functional core include:

- mana dork;
- mana rock;
- board wipe / wrath, with fuzzy scope;
- removal;
- graveyard hate;
- sacrifice outlet;
- cantrip;
- tutor;
- reanimator;
- card advantage / card velocity, provided they remain distinct;
- interaction, as a broad parent rather than a precise mechanic.

These are useful as **derived/index vocabulary**. They are not direct Oracle facts.

## 2.2 Overloaded terms that require a scope contract

### Ramp

EDHREC's current guide gives a broad functional definition: an effect is ramp when it increases mana available in a turn above ordinary on-curve production. It then includes land ramp, creatures, artifacts, enchantments, cost reducers, and other forms of acceleration.

Community discussion, however, is not uniform about rituals. Some players use “ramp” for any net acceleration; others reserve it for durable/repeatable acceleration and call Dark Ritual-style effects rituals, burst mana, or fast mana instead.

**Architecture consequence:** do not create a direct boolean `ramp` truth fact for all uses. Represent objective coordinates such as amount, timing, repeatability, source type, and permanence. The public vocabulary layer may say that a source uses the broad definition or the narrow definition.

### Protection

“Protection” in deckbuilding is broader than the rules keyword **protection**. A deck's protection package may use hexproof, indestructible, phasing, counterspells, recursion, or interaction suppression. Those cards can share a job while answering different threat classes.

**Architecture consequence:** role label and MTG keyword must live in different namespaces.

### Stax / tax / hatebear / prison

These labels describe strategic families with overlapping boundaries. The useful substrate is the actual restriction: which actor, action, resource, timing window, or object class is constrained; whether the effect taxes or prohibits; whether it is symmetric; and how long it persists.

**Architecture consequence:** the label may be a derived parent or presentation term. It must not become the canonical mechanic.

## 2.3 Useful relationships with no stable community label

Two seed relations need a precise project-authored parent even though no single stable community phrase appears universal:

- **`proactive-turn interaction suppression`** for Grand Abolisher / Defense Grid-like jobs;
- **`deep selective library access`** for Plunge into Darkness / Dig Through Time-like jobs.

These names are explicitly marked `PROJECT_AUTHORED`. They are not represented as discovered community terminology.

---

# 3. Functional-coordinate proposal

## 3.1 Design rule

**Children are defined by mechanism; parents are defined by job.**

This does not mean mechanics disappear. Functional similarity is explainable only if the system can say both:

- *why these cards are useful for the same job*, and
- *how their mechanics differ in ways that can matter*.

The lower mechanical layer therefore remains authoritative. S16B adds a derived coordinate/projection layer.

## 3.2 Minimum coordinate families

The preflight found the following coordinate families necessary to distinguish good positives from hard negatives:

### Job/outcome coordinates

- gameplay job / desired outcome;
- affected resource or object family;
- beneficiary / harmed actor;
- interaction window created, denied, or taxed;
- whether the effect advances, protects, answers, resets, enables, or denies.

### Mechanical action coordinates

- action/effect family;
- source zone;
- destination zone;
- search/selection depth;
- quantity inspected, retained, moved, created, or affected;
- magnitude / numeric scale;
- scope / target or participant class;
- controller/owner/opponent relation;
- targeting versus non-targeting;
- replacement versus prevention versus prohibition versus tax;
- symmetry/asymmetry.

### Time/delivery coordinates

- spell, activated, triggered, static, replacement, special permission, alternate mode;
- timing window;
- duration;
- repeatability;
- per-turn / once / continuous limits;
- modal / optional / alternative-cost structure;
- setup latency and delayed availability.

### Resource/cost coordinates

- mana cost and color requirement;
- life payment;
- sacrifice/discard/exile/tap costs;
- resource converted into effect;
- whether payment is up-front, on resolution, recurring, or conditional;
- whether the mechanism consumes a permanent or creates a durable resource.

### Residual-disposition coordinates

- where rejected/searched/affected cards end up;
- compensation given to opponents;
- side effects and collateral effects;
- whether the state change is permanent, reversible, or temporary.

### Dependency/context coordinates

- board-state dependency;
- hand/deck/graveyard dependency;
- commander/color-identity dependency;
- archetype dependency;
- metagame dependency;
- follow-up requirement;
- whether the relation is context-free, deck-contextual, or strategic/metagame-contextual.

## 3.3 Why these coordinates are necessary

The benchmark hard negatives are deliberately chosen so a shallow system fails:

- Defense Grid and Sphere of Resistance share a **tax** mechanism, but the former's job is turn-structured interaction suppression while the latter globally taxes spellcasting.
- Demonic Tutor and Entomb share **library search**, but hand versus graveyard destination changes context-free usability. In a reanimator deck, the relation can become contextual-positive.
- Rest in Peace and Grafdigger's Cage share a **graveyard hate** label, but one controls graveyard occupancy while the other blocks specific cast/entry paths.
- Wheel of Fortune and Faithless Looting share draw/discard language, but one resets/refills the table's hands while the other filters its controller's cards.
- Cyclonic Rift's normal and overload modes use the same card and bounce mechanic, yet single-target tempo and mass board reset are different jobs.

A useful representation must preserve these distinctions before ranking.

---

# 4. Gameplay-job DAG / lattice examples

The functional layer should be a DAG with multiple parents, not a single primary role.

## 4.1 Mana acceleration

```text
mana acceleration
├─ repeatable/durable acceleration
│  ├─ land-based acceleration
│  │  ├─ search land to battlefield        [Rampant Growth]
│  │  └─ additional-land permission        [Exploration]
│  ├─ artifact mana source                 [Arcane Signet]
│  ├─ creature mana source                 [Llanowar Elves]
│  └─ enchanted/modified source
└─ temporary/burst acceleration
   └─ ritual mana                           [Dark Ritual]
```

The graph permits both broad and narrow community definitions of “ramp” without rewriting the mechanical tree.

## 4.2 Board preservation

```text
preserve board through hostile interaction
├─ make permanents hard to target/destroy
│  └─ hexproof + indestructible             [Heroic Intervention]
├─ phase permanents out
│  ├─ selective own nonlands                [Clever Concealment]
│  └─ broad own-board + player protection   [Teferi's Protection]
└─ prevent interaction before it happens
   └─ proactive-turn interaction suppression
      ├─ hard prohibition                    [Grand Abolisher]
      └─ out-of-turn spell tax               [Defense Grid]
```

A card may have more than one parent. Grand Abolisher may belong under proactive-line protection and interaction suppression; it should not be forced into one canonical role.

## 4.3 Graveyard denial

```text
graveyard denial
├─ persistent occupancy prevention/replacement  [Rest in Peace]
├─ one-shot bulk purge                          [Soul-Guide Lantern mode]
├─ targeted graveyard removal                   [single-card exile effects]
└─ access-path lock                             [Grafdigger's Cage]
```

The parent is useful for deckbuilding; the children explain why two graveyard-hate cards are not always replacements.

## 4.4 Board reset

```text
board reset / mass threat clearing
├─ symmetric creature sweeper
│  ├─ destroy                                  [Wrath of God]
│  └─ toughness reduction                      [Toxic Deluge]
└─ asymmetric nonland reset
   └─ mass bounce                              [Cyclonic Rift, overload]
```

This is a strong example of a useful functional parent whose children have different answers to indestructible, death triggers, graveyard value, and recastability.

## 4.5 Library access

```text
find / access needed cards
├─ unrestricted search
│  ├─ to hand                                  [Demonic Tutor]
│  └─ to graveyard                             [Entomb]
├─ top-window selective access
│  ├─ variable depth, retain 1, exile rest     [Plunge into Darkness]
│  └─ depth 7, retain 2, bottom rest           [Dig Through Time]
└─ filtering / self-replacement
   └─ draw-discard / cantrip families
```

The same lower node can have different contextual parents. Entomb is not a context-free hand-access substitute for Demonic Tutor, but in a reanimator deck both can serve “find the creature I need for the line.”

---

# 5. Positive gold relations

`benchmark-v0.json` contains the machine-readable preliminary set. The important categories are:

### Strong functional

- Grand Abolisher ↔ Defense Grid: proactive-turn interaction suppression.
- Plunge into Darkness ↔ Dig Through Time: deep selective library access.
- Wrath of God ↔ Toxic Deluge: creature-board reset.
- Reanimate ↔ Animate Dead ↔ Necromancy: reanimation payoff.

### Partial role

- Rampant Growth ↔ Arcane Signet ↔ Llanowar Elves: repeatable mana acceleration, with land/artifact/creature failure-mode differences.
- Cyclonic Rift overload ↔ Wrath of God / Toxic Deluge: board reset, but different scope/symmetry/destination.
- Heroic Intervention ↔ Clever Concealment ↔ Teferi's Protection: board preservation, but different threat coverage.
- Rest in Peace ↔ Soul-Guide Lantern: graveyard denial, persistent versus one-shot.
- Beast Within ↔ Chaos Warp ↔ Reality Shift: flexible removal role with very different destinations/compensation.
- Viscera Seer ↔ Ashnod's Altar ↔ Altar of Dementia: sacrifice outlets with different outputs.
- Swords to Plowshares ↔ Path to Exile ↔ Beast Within ↔ Generous Gift: spot-removal package at a broad parent level.

### Contextual functional

- Demonic Tutor ↔ Entomb inside a reanimator deck: both can find the next needed piece, but only because graveyard destination is valuable in that context.

These labels are preflight research labels. They must be independently Oracle/CR rechecked and frozen before candidate S16B code exists.

---

# 6. Hard negatives and adversarial traps

The hard-negative set is as important as the positives. A functional thesaurus is unsafe if broad labels simply pull everything together.

| Pair / cluster | Trap | Why overlap is insufficient |
|---|---|---|
| Rhystic Study ↔ Smothering Tithe | same opponent-action “pay or I gain” pattern | card access versus mana generation |
| Defense Grid ↔ Sphere of Resistance | same cost-tax mechanism | turn-structured protection versus global spell taxation |
| Wheel of Fortune ↔ Faithless Looting | draw/discard wording | table hand reset versus self filtering |
| Rest in Peace ↔ Grafdigger's Cage | same “graveyard hate” label | occupancy denial versus action/access lock |
| Demonic Tutor ↔ Entomb | same library search action | hand versus graveyard; contextual positive only in named deck contexts |
| Rampant Growth ↔ Exploration | same land/ramp neighborhood | guaranteed library-to-battlefield resource versus permission dependent on land availability |
| Dark Ritual ↔ Arcane Signet | both mana acceleration | vocabulary conflict: one-shot burst versus durable source |
| Cyclonic Rift normal ↔ overload | identical card/verb | spot tempo versus mass reset |
| Counterspell ↔ Stifle | same English “counter” | spell versus activated/triggered ability object class |
| Swords to Plowshares ↔ Rest in Peace | shared exile destination | spot removal versus graveyard denial |
| Smothering Tithe ↔ Propaganda | both tax opponents | resource generation versus attack deterrence |
| Heroic Intervention ↔ Fog | both “defensive” | board protection versus combat-damage prevention |

The design implication is direct: **shared verb, shared destination, shared cost pattern, shared community label, and even shared card text are each insufficient by themselves to prove same gameplay job.**

---

# 7. Context-dependence classification

S16B should not expose one undifferentiated similarity relation.

## C0: context-free mechanical-functional

The job follows from the cards' mechanics without needing a deck archetype. Examples:

- Wrath of God / Toxic Deluge as creature-board resets;
- Grand Abolisher / Defense Grid as proactive-turn interaction suppression, with important coverage differences;
- Reanimate / Animate Dead as reanimation effects.

## C1: deck-context role

The relation requires a deck plan or resource interpretation. Examples:

- Demonic Tutor / Entomb in Reanimator;
- sacrifice outlets in Aristocrats/combo;
- a narrow protection piece that only matters because the commander must survive a specific removal class.

## C2: commander / color-identity context

A mechanically similar card may be unusable or much less useful because of color identity, commander cost/curve, or commander-specific resource requirements. This should be a filter/context layer, not a rewrite of semantic similarity.

## C3: archetype synergy

Cards can be functionally adjacent because a strategy changes the value of destinations or resources: graveyard as a second hand, sacrificing creatures as a benefit, artifacts as combo material, lands in graveyard as fuel.

## C4: metagame strategic value

Hate pieces, protection packages, and removal may be functionally close only against a particular field. This is time-sensitive and must remain downstream of canonical mechanics.

## C5: budget substitution

Budget Swapper needs stricter equivalence than a browse-oriented thesaurus. It should consume the same coordinates but apply a tighter policy: legality/color, cost, target scope, timing, magnitude, side effects, and required context all matter. “Same parent job” alone is not permission to call a card a replacement.

---

# 8. S9 gap analysis

## 8.1 What S9 actually does

At accepted head `9f92039...`, S9:

1. reads ACTIVE axis memberships;
2. requires at least one shared ACTIVE axis between anchor and candidate;
3. ranks candidates by number of shared axes;
4. breaks ties by specificity/cardinality and deterministic identity.

This is deliberately mechanical and provenance-safe. It does not use embeddings, card text similarity, a language model, or community roles at query time.

## 8.2 Measured strengths

- deterministic;
- explainable through concrete shared axes;
- no fabricated evidence for unassigned cards;
- explicit no-evidence result rather than pretending absence means dissimilarity;
- useful where the codebook already contains the shared mechanism.

## 8.3 Measured limitations

The existing frozen M2 panel contains 28 named-correct neighbours across Rampant Growth, Beast Within, Reanimate, and Reliquary Tower. The accepted measurement found only 12 discoverable from selected ACTIVE evidence: 3/11, 2/5, 3/8, and 4/4 respectively. Of those 12 discoverable positives, only 7 landed in the displayed top 25, and all 12 lived inside tie blocks larger than one. Several anchors produced very large pools with little ranking signal.

The controls matter even more for S16B. Grand Abolisher currently has zero ACTIVE memberships in the selected evidence and therefore produces the explicit unassigned/no-evidence state with zero candidates. That behavior is correct for S9. It also proves that a true gameplay-DNA system cannot get Grand Abolisher ↔ Defense Grid merely by adjusting S9's ranking. The anchor is structurally outside S9's candidate graph until additional grounded representation exists.

## 8.4 What must be added beyond S9

The minimum new representation is **not** “more fuzzy scoring.” It is a new derived evidence channel:

```text
S16A mechanical occurrences / facts
        ↓
reviewed functional derivation rules
        ↓
functional job memberships + coordinate profile + provenance
        ↓
candidate union
        ↓
context-sensitive comparison / ordering / explanation
```

S9 remains a valid mechanical-neighbour channel. S16B can union mechanical candidates and functional-job candidates, then explain which channel(s) produced the relationship.

Crucially, the functional memberships should be derived/index state, not silently written back into the canonical mechanical codebook.

---

# 9. Retrieval, ordering, and explanation acceptance design

The benchmark must separate three questions that older experiments tended to conflate.

## 9.1 Candidate discovery

Primary question: **Can the system find the gold relation at all?**

Measure:

- recall of strong functional gold pairs/clusters anywhere in the candidate pool;
- recall of zero-shared-axis positives;
- recall of context-dependent positives when the required context is supplied;
- false candidate creation from hard-negative traps;
- explicit `INSUFFICIENT_EVIDENCE` when derivation is not justified.

A positive that is not generated is a representation/derivation failure, not a ranking failure.

## 9.2 Ordering

Only score ordering among discovered candidates.

Before implementation, freeze pairwise expectations such as:

- strong-functional should normally outrank partial-role under context-free browsing;
- contextual-functional should rise only when its named context is supplied;
- a hard negative sharing a mechanism or label must not outrank a grounded same-job positive merely because it shares more surface structure;
- tighter coordinate agreement should break ties within the same job family;
- contradictions in job-defining coordinates must be able to block or demote a candidate.

Do **not** choose numeric weights in this preflight. If S16B eventually uses weights, tune only on the open development set after the relation and metric contracts are frozen, and score once on the blind holdout.

## 9.3 Explanation fidelity

Every surfaced relationship should be able to answer:

1. **Shared job:** what derived functional parent connected these cards?
2. **Mechanical evidence:** which S16A/Foundry facts support each child's membership?
3. **Meaningful differences:** which coordinates differ?
4. **Context:** is the relation context-free or dependent on deck/archetype/metagame?
5. **Provenance:** which rule/source authorized the functional parent and derivation?
6. **Confidence/state:** grounded, contextual, disputed vocabulary, or insufficient evidence?

An explanation that only says “both are protection” or “both are ramp” fails.

## 9.4 Product modes

The same substrate should support different policies:

- **Browse / true thesaurus:** broad parent-job discovery with visible differences.
- **Budget swapper:** strict compatibility gates before suggesting replacement.
- **Complete my deck:** role coverage plus synergy/context, downstream from mechanics.
- **Research/diagnostic:** expose provenance, job DAG path, and disagreement.

The canonical fact layer does not change between these consumers.

---

# 10. Holdout and precommitment plan

S16B is unusually vulnerable to benchmark leakage because its goal is qualitative. The holdout protocol must be frozen before implementation.

## 10.1 Freeze before candidate code

Freeze:

- relation-label definitions;
- context classes;
- coordinate schema;
- source cutoff date;
- pinned corpus / CR edition;
- open benchmark rows;
- hard-negative families;
- ordering questions / metrics;
- explanation acceptance fields;
- derivation provenance requirements;
- the fact that current S9 output may be measured but not used to relabel gold.

## 10.2 Open development set

The current `benchmark-v0.json` is a **preflight seed**, not the final answer key. Before S16B implementation, it should be independently re-adjudicated against pinned Oracle/CR and expanded with additional relationships sampled by mechanical and role families rather than only by famous cards.

The open set should deliberately contain:

- zero-shared-axis functional positives;
- same-axis hard negatives;
- same-mechanism/different-job negatives;
- same-job/different-mechanism positives;
- multi-role cards;
- modal cards;
- repeatable versus one-shot resources;
- persistent versus temporary denial;
- symmetric versus asymmetric effects;
- context-free/contextual label pairs;
- cards across permanent/spell types and zones.

## 10.3 Blind holdout

After strata and rules are frozen:

1. enumerate eligible held-out examples from the pinned corpus without consulting candidate S16B outputs;
2. commit a cryptographic seed hash / manifest outside candidate-code control;
3. deterministically select the holdout;
4. keep identities/labels sealed from the implementation session;
5. adjudicate ground truth independently without viewing candidate outputs;
6. reveal once after implementation and open-set tuning are frozen;
7. score once;
8. do not redraw failed examples.

A reserve seed may exist only for a predeclared procedural failure, never because the result is inconvenient.

## 10.4 Leakage controls

- Current S9 may be measured against the same rows but may not define them.
- Community-source discovery may nominate candidate relations, but final labels require Oracle/CR cross-check.
- A model that generated candidate code may not adjudicate the blind answer key after seeing outputs.
- Cross-posted primer text counts as one evidence lineage.
- Unknown or disputed vocabulary stays unknown/disputed.

---

# 11. Draft S16B implementation contract

> **STATUS: NOT_AUTHORIZED.** This section is an implementation-shape proposal only. Captain authorization and accepted S16A completion are mandatory before execution.

```yaml
schema: mtj-s16b-draft-contract/0
status: NOT_AUTHORIZED
phase: S16B
requires:
  - S16A accepted lossless semantic parse
  - Objective-5 benchmark/lexicon/coordinate law reviewed and frozen
  - pinned corpus and CR edition
  - open benchmark frozen
  - blind holdout commitment frozen
objective:
  - derive provenance-bearing functional-job relationships from mechanical facts
  - retrieve cards that can perform the same gameplay job despite different mechanism/wording
  - preserve mechanical differences and contextual boundaries in explanations
must_preserve:
  - Oracle/CR mechanical truth remains lower authority
  - no community claim becomes a direct canonical fact
  - no codebook mutation merely to improve retrieval
  - UNKNOWN / INSUFFICIENT_EVIDENCE remains possible
  - card-level union does not prove same-occurrence co-occurrence
  - current S9 remains a separately explainable mechanical channel
candidate_architecture:
  - S16A semantic occurrence/fact substrate
  - reviewed deterministic functional derivation registry
  - derived job-membership artifact with provenance
  - job DAG / multi-parent index
  - coordinate-aware candidate union
  - context-aware comparison and ordering
  - explanation payload: shared job + evidence + differences + context + provenance
forbidden:
  - LLM-generated truth at query time
  - embedding score as semantic authority
  - unproven negative facts from missing evidence
  - single primary role per card
  - arbitrary community-tag import
  - benchmark relabeling from candidate outputs
  - S10-S15 migration advancement as a side effect
  - AQ4 / Bridge v0 / Step6 changes
  - accepted-head movement without Captain approval
acceptance:
  candidate_discovery:
    - zero-shared-axis gold positives become discoverable when derivation evidence exists
    - hard-negative traps are not promoted solely by shared verb/mechanism/label
    - unsupported cases return insufficient evidence
  ordering:
    - frozen pairwise/open-set expectations pass before blind reveal
    - contextual relationships react only to declared context
  explanation:
    - every result exposes shared job, mechanical evidence, meaningful differences, context, provenance
  conservation:
    - canonical mechanical artifacts byte/hash unchanged unless separately authorized
    - S9 baseline remains reproducible
holdout:
  - one blind reveal after open-set implementation freeze
next:
  authorized: NONE
```

---

# 12. Conclusions and decisions for the Manager/Captain

## 12.1 Findings strong enough to carry forward

1. **S9 cannot be repaired into gameplay-DNA solely by retuning ranking.** Its candidate gate requires shared ACTIVE evidence. Grand Abolisher currently has none, so it correctly produces zero S9 candidates.
2. **A functional parent layer is justified.** Direct comparison sources and role guides repeatedly group different mechanisms by job.
3. **The functional layer must remain derived.** Community categories are valuable but noisy and sometimes contested.
4. **A DAG is preferable to one role label.** Cards routinely serve multiple roles; broad roles have mechanism-specific children.
5. **Context must be explicit.** Demonic Tutor/Entomb is a clean example where reanimator context changes functional relevance without changing mechanics.
6. **Hard negatives are mandatory.** Shared verbs, destinations, taxes, or broad labels can create convincing but wrong similarity.
7. **No numeric scoring law is ready to ratify.** The preflight can freeze relation classes, coordinates, pairwise expectations, and measurement separation without inventing weights.

## 12.2 Open questions deliberately left for the S16B freeze

- final naming of project-authored functional parents;
- exact deterministic derivation grammar from accepted S16A facts;
- whether all useful jobs can be represented by reviewed rules or whether a small curated functional registry is required;
- exact open/holdout counts and stratification after corpus measurement;
- ranking policy/weights, if any, after open-set measurement;
- how much deck-context metadata is available without importing behavioral popularity data into semantic truth;
- how to version community vocabulary as terminology changes.

## 12.3 Stop boundary

This objective stops at research evidence and a draft contract. It does **not** authorize S16A or S16B implementation, accepted-head movement, migration S10-S15 execution, codebook changes, authority selection changes, merge, deployment, or publication.
