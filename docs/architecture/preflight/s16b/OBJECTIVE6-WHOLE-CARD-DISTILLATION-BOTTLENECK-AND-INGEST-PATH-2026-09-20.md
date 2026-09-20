# Objective 6 — Whole-Card Distillation Bottleneck and Ingest-Path Test

**Date:** 2026-09-20  
**Status:** **RESEARCH / PRE-AUDIT TRANSLATION TEST — NOT A SEMANTIC RULING, IMPLEMENTATION CONTRACT, OR FREEZE**  
**Repository scope:** S16B Objective 6 semantic design on PR #70 documentation branch  
**Accepted implementation base inspected:** `fdb66e659d81f4efa373ab8e86329485c0205966`  
**Governing principle:** **PRESERVE TRUTH, NOT PLUMBING.**  
**Research principle:** **THOROUGHNESS OVER THROUGHPUT.**

## 1. Question

Before adding more semantic plumbing, test the more basic risk:

> Can a whole Magic card actually be translated into Foundry without losing which facts belong together, which alternatives are mutually exclusive, which object a later clause refers to, or which qualifier belongs to which operation?

A vocabulary can be individually correct and still fail as a system if the translation step cannot organize a card faithfully.

This pass therefore tests two separate questions:

1. **Coverage:** does the current/post-audit semantic foundation appear capable of expressing the meaningful mechanics on difficult cards?
2. **Translation efficiency:** is there a tractable way to get from Oracle text to those facts without asking an annotator or model to assign dozens of independent labels directly from prose?

This is deliberately earlier than the planned next semantic audit. It is a translation/representation stress test, not a decision about Round-2 concepts.

---

## 2. Source basis

This test used:

- project Oracle snapshot `data_snapshots_2026-07-03_oracle-cards.jsonl.gz` — 38,233 Oracle-card rows;
- project Comprehensive Rules effective 2026-08-07;
- project codebook `foundry-codebook/2`, version `3.0.0-r4`;
- current S16B Objective 6 semantic candidate records on PR #70;
- accepted-base AQ4 architecture contract:
  - `benchmarks/aq4/docs/AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md`;
- accepted-base AQ4 structural-probe/benchmark code, including:
  - `benchmarks/aq4/experiments/foundry_aq4_probes.py`;
  - `benchmarks/aq4/experiments/aq4_benchmark/aq4_population.py`.

The AQ4 production architecture remains paused/unratified where the durable controls say it is. Its design and probe artifacts are used here as prior project work, not as authorization to resume AQ4.

---

## 3. Executive result

### No fatal semantic-coverage blocker found

On the tested cards, the post-audit vocabulary plus the already-designed AQ4 relation/predicate machinery appears **capable in principle** of representing the mechanically important facts without inventing a bespoke ontology family for every weird card.

The hard cards generally fail only when the representation becomes too flat.

### The real bottleneck is translation fidelity

The current `foundry-codebook/2` assertion form is excellent for recording that a card has an axis and for preserving quote/locality evidence, but it is too flat to serve by itself as the lossless whole-card semantic representation.

A card can have all of its individual axes present and still be represented incorrectly if the system loses:

- mutual exclusivity between modes;
- sequence/order between operations;
- conditional branches;
- delayed relationships;
- identity of `that card`, `those cards`, or another previously established object/set;
- which participant a restriction applies to;
- which operation a duration/frequency/payment qualifier modifies;
- replacement-event lineage;
- linked-ability scope.

**Therefore the primary pre-corpus requirement is not more labels. It is a structured intermediate card representation that preserves relationships and scope before public concepts are derived.**

### Do not build a second semantic IR from scratch

AQ4 already anticipated much of this machinery. Its contract includes semantic-unit kinds, typed participant roles, predicates such as `frequency_cap`, and relation types including `stores`, `releases`, `replaces`, `prevents`, `inherits_from`, `nested_under`, `when_event_then`, `if_state_then`, `grouped_with`, and `choice_group_id`.

The accepted AQ4 benchmark/probe code also explicitly measures structural-adversary populations such as:

- multi-effect clauses;
- multiple participants;
- CR 607 linkage;
- delayed effects;
- cross-unit coreference;
- modal cards;
- repeated identical clauses;
- `this way` and other unresolved reference forms.

That is strong evidence that the project already identified the correct class of problem.

**The economical path is to reuse/finish the existing richer graph direction, not to create a parallel Objective-6 graph system.**

What remains unproven in this pass is whether every relation promised by the AQ4 contract is already persisted by current implementation outputs. The probe code is explicitly read-only and says it does not implement production occurrence identities or relation edges. The benchmark code consumes structural candidates, but this pass does not establish full lossless graph persistence. That must be verified before corpus execution.

---

## 4. Why the flat assertion model is insufficient

A concrete example is **Knight of Autumn**.

Oracle structure:

```text
When this creature enters, choose one —
• put counters on this creature;
• destroy an artifact or enchantment;
• gain life.
```

The existing codebook can independently record the three outcomes and the fact that the card has an ETB modal choice. That is not enough.

A consumer must also know:

```text
one ETB trigger
  -> choose exactly one branch
       -> branch A: counters
       -> branch B: removal
       -> branch C: life gain
```

Without that relationship, a downstream product can accidentally treat Knight as producing all three effects from one ETB.

The same defect becomes more serious on:

- choose-two cards;
- nested `if ... otherwise ...` branches;
- delayed returns;
- cards that store an object and later refer to it;
- cards that replace an event with another event that itself creates a new event;
- repeated copies of the same printed sentence that are distinct semantic occurrences.

The assertion vocabulary is not wrong. The missing information is **structure between assertions**.

---

## 5. Adversarial whole-card sample

This pass deliberately used cards that stress different organizational problems rather than trying to estimate ordinary-card prevalence from a hand sample.

| Card | Principal structural requirement | Current substrate verdict | Bottleneck |
|---|---|---|---|
| **Lightning Bolt** | one effect, one target, one amount | straightforward | none material |
| **Cultivate** | one broader-library search selecting multiple cards with split destinations | expressible by Tutor/search + quantities + destinations | selected-set members must retain separate destinations |
| **Knight of Autumn** | one trigger, choose-one, three branch effects | expressible | explicit choice group/cardinality required |
| **Kolaghan's Command** | choose two of four, effects may target different objects/players | expressible | mode group + choose-N + per-branch participant scope |
| **Charming Prince** | modal trigger; exile selected object; delayed return of that same object | expressible | object identity/coreference + delayed link must survive |
| **Scavenger's Talent** | level-gated abilities, trigger frequency, sacrifice cost, conditional later action | expressible | nested scope and cap attachment are essential |
| **Fisher's Talent** | level progression plus chained replacement behavior | probably expressible | replacement lineage must be explicit rather than a loose `replaces` tag |
| **Necropotence** | skip draw step; discard listener; activated face-down exile; delayed move to hand | expressible | future acquisition must not be mislabeled current use permission; hidden object identity required |
| **Chains of Mephistopheles** | draw replacement, branch on whether discard occurred, then draw or mill | probably expressible | original event -> replacement -> nested branch/result lineage |
| **Memory Jar** | save an entire hand set, create temporary hand, then discard and restore stored set | expressible with set identity | requires entity-set identity and a state/snapshot boundary for accounting |
| **Mairsil, the Pretender** | exile marked donor cards; inherit their activated abilities; cap each inherited ability once/turn | expressible | donor-set linkage + inheritance + cap scoped per inherited ability |
| **Mindslaver** | another player makes decisions under your control for a turn | Round-2 pressure | current participant roles do not obviously distinguish decision controller from object controller |
| **Fires of Invention** | timing restriction; <=2 casts/turn; free-cast permission under MV predicate | expressible | `frequency_cap` and payment permission must attach to the correct action |
| **Panglacial Wurm** | cast this card during another search process | expressible | process-bound permission window/link |
| **Knowledge Pool** | shared linked exile pool; triggering spell moves; cast a different linked card free | expressible | pool identity, trigger source, replacement-like sequence, permission link |
| **Opposition Agent** | control opponents' decisions while they search; redirect found cards; grant play permission | partially expressible | decision-control role is the clearest apparent gap |
| **Necromancy** | cast-history/timing state; changing behavior; delayed sacrifice relationship | expressible but complex | occurrence/link/state scope |
| **Tombstone Stairwell** | upkeep cost, per-player graveyard scaling, tokens with linked cleanup | expressible | generated-object set/link and delayed cleanup |
| **Sea-Dasher Octopus** | alternate deployment/cast context plus mutate consequences | keyword expansion required | Keyword Consequence Registry must emit the actual mechanical consequences |
| **Bonecrusher Giant** | Adventure: one physical card, spell-half execution, exile permission for creature later | expressible | same underlying card identity across execution opportunities |
| **Bala Ged Recovery** | modal double-faced card with mutually exclusive land/spell use | expressible | face/layout normalization must occur before semantics |
| **Fable of the Mirror-Breaker** | Saga chapter sequence, token creation, transform, new-face ability, delayed sacrifice | expressible | multi-face + chapter/time sequence + copy provenance |
| **Humility** | continuous ability removal plus characteristic setting | expressible for retrieval | do not turn Foundry into a full layer engine; preserve the operations and affected domain |
| **Abundance** | replace draw with choice + ordered traversal + move selected card | expressible | replacement-event lineage + traversal must remain distinct |
| **Fact or Fiction** | expose sample, opponent partitions, controller selects pile, split destinations | expressible | staged selection authority/partition relationship |
| **Ad Nauseam** | repeated reveal/move/life-loss sequence with player-controlled stopping | expressible | repeated composite event + explicit stop rule |

### Sample verdict

The sample did **not** expose a card whose mechanics require abandoning the current shallow-family / rich-mechanical-substrate direction.

The failures are relational:

- what is nested under what;
- what refers to what;
- what replaces what;
- what happens only in one mode/branch;
- what is delayed;
- who is making a decision;
- which operation owns a qualifier.

That is a much more tractable problem than a missing ontology.

---

## 6. Hard-sample structural pressure

A manual structural pass over the 26-card adversarial sample found:

- **19 / 26** require meaningful nested/control-flow structure;
- **21 / 26** require object/entity/linkage information;
- **7 / 26** require keyword or Comprehensive-Rules consequence expansion;
- **11 / 26** directly touch Round-2 pressure areas.

These are **not prevalence estimates**. The sample was chosen to be difficult.

They do show that any ingestion method based on:

> `read card -> assign flat list of semantic labels`

will fail on exactly the cards most important for validating Foundry's generality.

---

## 7. Broad corpus triage

Broad lexical/structural triage over the 38,233-row Oracle snapshot was used to estimate how often the translation layer will encounter difficult shapes. These are deliberately rough detector counts and **must not be treated as semantic-membership counts**.

Approximate full-snapshot triage populations included:

- modal / choose / bullet structures: ~1,724 rows;
- broad conditionals: ~5,623;
- replacement-like language: ~1,085;
- delayed/time-window language: ~7,247;
- linked-reference language: ~4,459;
- repeat/loop language: ~563;
- action/rate caps: ~850;
- broad ability-borrowing language: ~15;
- object-copy language: ~738;
- control-another-player language: ~10;
- multi-face rows: ~3,672.

Within a rough Commander-legal/non-digital slice, triage suggested approximately:

- 12.5% multi-face;
- 17.2% linked-reference;
- 25.6% conditional;
- 10.2% modal;
- 3.3% replacement-like;
- 22.0% keyword-bearing;
- 18.8% with Oracle text longer than 300 characters.

A deliberately broad structural-complexity heuristic marked roughly 42% of that slice, rising above 50% when generic conditional language was included.

Again: these are routing/triage estimates only. Their implication is operational, not ontological:

> a complex-card path is not a rare exception path; it should be designed deliberately.

---

## 8. Existing AQ4 work already addresses much of the problem

The AQ4 architecture contract's intended occurrence identity is based on:

- oracle card;
- face ordinal;
- clause ordinal;
- semantic unit kind;
- unit family/value;
- occurrence index.

It defines semantic unit kinds including:

- effect;
- trigger;
- cost;
- condition;
- restriction.

It also defines/anticipates:

### Participant roles

- actor;
- recipient;
- controller;
- owner;
- beneficiary;
- harmed player;
- self/opponent application.

### Predicates / conditions

- positive/negative/state conditions;
- activation/event conditions;
- state dependencies;
- `frequency_cap`;
- `applies_while`;
- `applies_until`;
- `suppressed_while`;
- bounded counts.

### Relations

- self-reference;
- creates / produces / consumes;
- pays-for / converts-to;
- stores / releases;
- amplifies / enables / disables;
- replaces / prevents;
- inherits-from;
- nested-under;
- when-event-then;
- if-state-then / unless-state-then;
- transforms-from / transforms-to;
- grouped-with;
- `choice_group_id`.

This is very close to the relationship grammar the current test independently finds necessary.

The accepted AQ4 benchmark code also explicitly constructs a `structural adversaries` cohort around real failure modes: multi-effect sentences, repeated clauses, CR 607 linkage, delayed effects, cross-unit coreference, modal headers, multiple participant contexts, and unresolved reference forms.

### Important limitation

The AQ4 probe code explicitly says it is a read-only measurement and **does not implement production occurrence identity, participant records, relation edges, or ABSENT-PROVEN**.

Therefore this test does **not** conclude that the current implementation already persists the full graph. It concludes that the project already designed much of the right graph and measured many of the right hazards.

Before broad corpus ingestion, the actual candidate/persistence path must prove that these relationships survive end-to-end.

---

## 9. Bottlenecks ranked by severity

### B1 — Relationship/scope loss — **BLOCKING if unresolved**

A qualifier/relation must attach to a specific semantic occurrence or edge, not merely to the card or paragraph.

Examples:

- Knight's mode exclusivity;
- Fires' two-spells-per-turn cap;
- Mairsil's once-per-turn cap on **each borrowed ability**;
- Charming Prince's delayed return of **the exiled object**;
- Chains' branch conditions inside a replacement sequence.

If this cannot be represented, the card is not faithfully distilled even if every noun appears somewhere in the record.

### B2 — Semantic-unit granularity inside one Oracle clause — **BLOCKING / likely amendment point**

One printed sentence can contain multiple semantic operations.

Examples:

- exile **and** later return;
- discard **then** draw;
- search for multiple cards with different destinations;
- cast-trigger exiles original spell and grants permission for another.

AQ4 explicitly measured multi-effect-per-clause pressure and reserved finer effect identity for later work. A production translator needs a legal way to identify multiple operation occurrences inside one clause without accidentally merging them.

This does **not** necessarily require changing the frozen AQ4 occurrence key immediately; the audit should choose the smallest compatible mechanism. But some equivalent operation-local identity is required before broad ingestion.

### B3 — Entity / object / set identity and coreference — **BLOCKING**

The translator needs stable references for:

- `that card`;
- `those cards`;
- `it` where mechanically unambiguous;
- cards exiled `with` a source;
- Memory Jar's stored old-hand set;
- Mairsil's cage-counter donor set;
- created token sets with later cleanup;
- transformed/returned objects where CR identity rules matter.

CR 607 linkage is only one subset. General cross-operation entity references are required.

### B4 — Coverage ledger — **BLOCKING quality control**

There must be a deterministic way to ask:

> Did every mechanically meaningful part of the Oracle card get accounted for?

For each meaningful source span/token/construct, the output should point to at least one of:

- semantic occurrence;
- participant/entity/reference;
- predicate/qualifier;
- relation edge;
- Keyword/CR registry expansion;
- explicitly justified nonsemantic/scaffolding exclusion.

Unclaimed meaningful residue should route the card to review rather than silently disappear.

This is the most important defense against a fluent model producing an incomplete but plausible-looking annotation.

### B5 — Player decision control — **real apparent field gap; bounded audit required**

`controller` is not sufficient for Mindslaver/Opposition Agent semantics.

A player can control another player's decisions while the controlled player still controls their objects and pays costs from their own resources.

Likely need: a decision-authority relation/role, not a new public family.

### B6 — Visibility / inspection rights — **real apparent coordinate gap**

Face-down exile and hidden zones can depend on who may inspect an object independently of who may play/cast it.

Likely need explicit information-access/visibility facts.

### B7 — Replacement lineage — **probably existing relation machinery plus stronger event identity**

AQ4 already has `replaces` / `prevents`.

What Chains/Abundance/Fisher's Talent stress is not the absence of the relation word; it is whether the system can preserve:

```text
would-be event A
 -> replacement R
 -> result event B
 -> optional/nested event C
```

Do not create a Replacement family merely to solve an event-identity problem.

### B8 — Keyword/rules consequence expansion — **known prerequisite, not a new blocker**

Cards with Mutate, Adventure, Saga, Hideaway, Myriad, etc. cannot be fully distilled from printed reminder-stripped Oracle text alone.

The existing Keyword Consequence Registry gate is therefore correctly placed before broad corpus execution.

### B9 — Full layer/rules-engine simulation — **NOT required for Objective 6 retrieval substrate**

Humility-like interactions demonstrate that Magic game-state resolution can be arbitrarily complex.

Foundry does not need to become a complete runtime rules engine merely to state that a card removes abilities and sets base power/toughness over a specified domain.

The boundary should remain: preserve the card's canonical operations/conditions and enough CR consequence truth for retrieval/explanation; leave arbitrary battlefield-state resolution to a later rules-reasoning layer if needed.

---

## 10. Efficient translation strategy

### Reject: concept-first annotation

Do **not** ask an LLM or human to begin with:

> Which of Foundry's dozens/hundreds of concepts and qualifiers apply to this card?

That strategy creates several problems:

- high cognitive load;
- inconsistent qualifier scope;
- labels selected before relationships are understood;
- missed low-level facts when a familiar community label feels sufficient;
- duplicated information;
- poor auditability;
- expensive re-annotation whenever the vocabulary changes.

### Preferred: structure first, semantics second, concepts last

The tested path is:

```text
Oracle card
  -> normalize faces/layout
  -> segment abilities / sentences / semantic occurrences
  -> construct control-flow + entity/reference graph
  -> extract primitive mechanics + participants + predicates
  -> expand keywords / CR constructs
  -> attach operation-local qualifiers
  -> derive surfaced families/facets/aliases
  -> derive accounting/product facts
  -> coverage + invariant checks
  -> accept or route to review
```

This makes the complex internal representation a machine concern rather than something a human must manually juggle.

---

## 11. Proposed translation pipeline

### Stage 0 — Normalize card and layout

Produce stable card/face/paragraph inputs before semantics.

Handle:

- normal single-face;
- modal double-faced;
- transforming double-faced;
- split;
- Adventure;
- Saga/class/level layouts;
- other supported layouts.

Never drop a face.

### Stage 1 — Deterministic structural segmentation

Cheap parser pass identifies likely:

- ability lines;
- sentences/clauses;
- triggered abilities;
- activated abilities and costs;
- static/continuous abilities;
- modal headers and bullet options;
- chapter/level boundaries;
- replacement markers;
- delayed markers;
- keyword carriers.

A lightweight prototype on the adversarial sample was able to recover the top-level architecture of Knight of Autumn, Kolaghan's Command, Charming Prince, Scavenger's Talent, Fisher's Talent, Memory Jar, Mairsil, Mindslaver, Fires of Invention, Knowledge Pool, Opposition Agent, Necromancy, and Fable of the Mirror-Breaker without first assigning gameplay concepts.

This is evidence that a large portion of routing can be deterministic/cheap.

### Stage 2 — Build semantic occurrence graph

Create operation/trigger/cost/condition/restriction occurrences and connect them.

Required graph information includes:

- nested-under;
- choice grouping + choose cardinality;
- sequence/order where semantically relevant;
- condition -> consequence;
- delayed relation;
- storage/release;
- replacement/prevention;
- inheritance;
- creation/consumption;
- transformation;
- coreference/linkage.

Use/reconcile with AQ4 rather than inventing a second graph vocabulary.

### Stage 3 — Resolve entities and references

Identify the semantic objects/sets referred to by later operations.

Examples:

- target creature A;
- source permanent;
- selected card set;
- exiled-with-source set;
- `that card`;
- prior temporary-hand set;
- controlled player;
- copied spell/card object.

This step must be CR-aware where zone changes create new objects or where rules explicitly preserve a relation.

### Stage 4 — Extract primitives and participants

Only after structure is known, attach operations such as:

- draw;
- discard;
- search;
- move-zone/direct placement;
- cast/play permission;
- damage;
- destroy/exile/bounce;
- token creation;
- mana production;
- cost/payment operations;
- counters;
- copy/additional execution;
- other ratified primitives.

Attach actor/recipient/owner/controller/beneficiary and relevant target/object domains to the correct occurrence.

### Stage 5 — Attach predicates / qualifiers locally

Examples:

- eligibility;
- quantity;
- source/destination zone;
- timing/window;
- action cap/frequency;
- payment method/alternative cost;
- condition;
- stop rule;
- selection authority;
- visibility;
- owner/provenance;
- decision authority if ratified.

The key rule is:

> qualifiers belong to occurrences/edges/entities, not merely to cards.

### Stage 6 — Expand keyword / compact CR constructs

Use a deterministic Keyword Consequence Registry to inject consequences not faithfully recoverable from the printed card line alone.

Preserve provenance showing that the consequence came from the rules construct rather than literal Oracle wording.

### Stage 7 — Derive user-facing concepts

Only now derive:

- Ramp;
- Tutor;
- Removal;
- Sample Selection;
- Top-Library Access;
- Direct Placement;
- Cantrip;
- Mass Removal;
- community aliases/search views;
- etc.

These are projections of the card graph, not the primary annotation target.

### Stage 8 — Derive accounting / product facts

Compute projections such as:

- Card Resource Delta;
- self-replacing/parity;
- Role Compression;
- processor/throughput profiles.

Do not manually annotate these where they can be deterministically derived from lower facts.

### Stage 9 — Coverage ledger and invariants

Before accepting a card:

1. every meaningful Oracle span is claimed or deliberately excluded;
2. all references resolve or are explicitly unresolved;
3. every qualifier has a scoped owner occurrence/edge/entity;
4. choice branches have cardinality/exclusivity semantics;
5. delayed actions preserve the correct object/set link;
6. copies are not mistaken for underlying card stock;
7. Additional Execution is not mistaken for another physical card;
8. future acquisition is not current access;
9. PLAY and CAST remain distinct;
10. destination and permission belong to the correct operation;
11. replacement chains connect original/result events;
12. multi-face structure remains intact.

Cards failing these checks go to review rather than being partially accepted.

---

## 12. Two-tier ingestion appears efficient

The corpus should not pay maximum reasoning cost for every card.

### Tier A — deterministic / ordinary path

Use structural parsing + known templates + keyword registry + primitives for cards whose graph closes cleanly.

Expected examples:

- simple damage;
- ordinary removal;
- ordinary draw;
- straightforward mana production;
- ordinary Tutor/ramp templates;
- simple triggered or activated abilities;
- common modal structures once modal parsing is established.

### Tier B — complex-card reasoning path

Escalate when structural detectors find:

- unresolved cross-unit reference;
- multiple effects in one clause that cannot be confidently split;
- replacement chain;
- linked hidden object/set;
- nested modality/condition;
- player-decision control;
- unusual copy/inheritance;
- unexpanded keyword/rules construct;
- nonzero meaningful residue;
- graph/invariant contradiction.

This concentrates expensive model/review work on the cards that actually need it.

### Why this is preferable

The aim is not to make every card simple. Magic is not simple.

The aim is to make the **translator predictable**:

```text
simple structure -> cheap deterministic path
complex structure -> explicit escalation
unknown residue -> review, never silent acceptance
```

That is a scalable architecture.

---

## 13. Minimum pre-plumbing changes recommended

Do **not** implement all Round-2 candidate systems yet.

Before semantic plumbing expands, verify or supply only the structures needed for lossless translation:

1. **operation-local identity / finer within-clause granularity** compatible with the AQ4 occurrence contract;
2. **entity/object/set reference identity** for cross-operation linkage;
3. **relation/qualifier attachment scope** to occurrences/edges/entities;
4. **decision-authority role/relation** if the upcoming audit confirms it is not already representable;
5. **visibility/inspection-right coordinate** if the audit confirms the gap;
6. **explicit replacement-event lineage** if existing `replaces` edges cannot connect original and resulting event occurrences;
7. **coverage ledger + unresolved-residue gate**;
8. **Keyword Consequence Registry** as already planned.

Everything else should be derived or postponed until evidence forces it.

---

## 14. What should *not* be built

This test gives no support for:

- another broad Card Access ontology;
- another Engine tree;
- a separate Objective-6 graph architecture parallel to AQ4;
- a full Magic runtime/layer simulator as a prerequisite to Searcher B;
- hand-annotating every derived user-facing label;
- a giant fixed qualifier checklist that an LLM must fill for every card regardless of relevance.

Those approaches increase complexity without solving the actual translation problem.

---

## 15. Pre-audit decision

### Current confidence

**No fatal whole-card organization blocker has been found.**

The current semantic direction appears viable if and only if the project preserves a richer occurrence/relation/entity graph before projecting to the flatter public concepts and codebook assertions.

### Remaining uncertainty

The following must be tested in the next audit / bounded implementation review:

- whether accepted AQ4 candidate outputs already persist enough of the promised graph to reuse directly;
- the smallest legal mechanism for multiple semantic operations inside one clause;
- exact general entity/reference identity semantics beyond CR 607-linked abilities;
- whether `decision_controller` / equivalent already exists elsewhere before adding it;
- whether visibility/inspection rights already exist elsewhere before adding them;
- whether replacement lineage needs new structure or only stricter use of existing `replaces` edges;
- coverage-ledger representation and acceptance thresholds.

### Recommended next sequence

1. audit these bottlenecks against the whole existing AQ4/Foundry substrate;
2. reuse existing structures wherever possible;
3. build the minimum missing translation plumbing;
4. run another whole-card fixture round through that actual representation;
5. only after the fixtures close losslessly, authorize any broad corpus translation.

The next round should therefore be judged by **lossless card reconstruction/explanation**, not by how many concepts were assigned.

---

## 16. Control boundary

This research does **not** authorize:

- S16B freeze;
- AQ4 resumption;
- broad corpus classification/reclassification;
- implementation acceptance;
- Bridge v0 activation;
- Step6;
- merge;
- accepted-head movement;
- `main` movement.

Standing controls remain unchanged.
