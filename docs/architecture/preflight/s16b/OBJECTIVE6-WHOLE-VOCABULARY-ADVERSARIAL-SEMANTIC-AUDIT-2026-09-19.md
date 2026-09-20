# Objective 6 — Whole-Vocabulary Adversarial Semantic Audit

**Date:** 2026-09-19  
**Status:** AUDIT VERDICT / STRUCTURAL CORRECTION CANDIDATE — NOT A FREEZE  
**Evidence input:** `OBJECTIVE6-WEIRD-CARD-ADVERSARIAL-CORPUS-HUNT-2026-09-19.md`  
**Authority boundary:** S16B semantic documentation only. No implementation acceptance, merge, accepted-head movement, AQ4 resumption, Bridge activation, Step6, `main` movement, or semantic freeze.

> **If this concept did not already exist, would the evidence force us to create it?**

That question is applied here even to Captain-approved working concepts. Prior approval preserves history; it does not make a weak abstraction true.

## 1. Audit verdict

The current Objective 6 direction is strongest where it preserves **events, permissions, participants, zones, costs, resources, quantities, timing, and output signatures** and weakest where it converts those facts too early into broad nouns.

The weird-card evidence therefore supports a shallower semantic surface than the current working documentation.

### High-level verdict

1. **Keep a small set of strong player-facing functional families** where the term has stable retrieval value and a defensible mechanical boundary: e.g. Ramp, Tutor, Removal, Taxation, Permission Denial.
2. **Keep surfaced include/exclude facets** when players genuinely need direct control even if the fact is derivable: e.g. Top-Library Access, finite-sample selection, Direct Placement.
3. **Move most mechanism detail downward** into primitives, event/output signatures, qualifiers, coordinates, and keyword-consequence expansions.
4. **Treat resource/accounting outputs as derived facts**, not semantic trees.
5. **Treat broad community theory terms as aliases/strategic projections** when established usage is wider or fuzzier than a canonical hard predicate.
6. **Do not create a second Card Access metric.** The durable Captain correction is correct; the old `Card Access Differential` document is superseded.
7. **Correct payment terminology.** Convoke/Delve/Improvise are payment methods/substitutions, not Magic alternative costs.
8. **Demote Engine from a canonical parent tree.** Preserve the hard processor facts; expose `engine` as a derived/search/community label rather than using a strict ontology gate that conflicts with ordinary player usage.

This is a structural correction, not merely a naming pass.

---

## 2. Classification vocabulary used in this audit

- **FAMILY** — stable player-facing functional concept with meaningful membership and retrieval value.
- **SURFACED FACET** — independently queryable include/exclude fact, but not a major ontology branch.
- **COORDINATE** — typed property attached to an assertion/event/resource.
- **PRIMITIVE** — direct mechanical operation/fact.
- **EVENT/OUTPUT SIGNATURE** — mechanically observable producer/consumer structure.
- **DERIVED ACCOUNTING** — computed from more primitive facts/state; not canonical family membership.
- **KEYWORD CONSEQUENCE** — CR-derived expansion reused by cards carrying a compact construct.
- **COMMUNITY ALIAS** — useful search/player term resolving to harder semantic facts.
- **STRATEGIC LAYER** — context/evaluation term that should not be asserted as canonical card truth.
- **OPEN** — evidence is insufficient for final placement.
- **RETIRED/COLLAPSED** — should not remain a distinct canonical concept.

---

## 3. Card Access cluster

### 3.1 Card Access

**Outcome: UI/navigation umbrella, not a canonical family.**

Evidence does not force one hard `Card Access` predicate. Draw, Tutor, graveyard return, temporary exile permission, top-library permission, finite-sample selection, and direct placement are mechanically different operations.

`Card Access` remains useful as a user-facing navigation neighborhood and Explorer grouping. It should not itself add strong Searcher B similarity.

### 3.2 Literal Draw

**Outcome: PRIMITIVE / event signature. RETAIN.**

CR 121.1 gives draw a precise operation. Effects that move or expose cards elsewhere must not inherit `draw` merely because they increase usable options.

### 3.3 Cantrip

**Outcome: SURFACED DERIVED TAG + COMMUNITY ALIAS. RETAIN, not a trunk.**

The later realignment to established usage survives attack. Canonically store the draw/self-replacement facts; derive `Cantrip` for player search/explanation.

Do not extend Cantrip to Regrowth, Tutor, exile permission, or other non-draw parity mechanisms merely because they replace a card resource.

### 3.4 Card Replacement

**Outcome: RETIRED/COLLAPSED.**

The existing retirement ruling survives attack. One-for-one parity is an accounting result shared by mechanically unrelated operations. `self_replacing` / parity may be derived; no tree is needed.

### 3.5 Card Filtering

**Outcome: COLLAPSE FROM HARD FAMILY TO UI/SEARCH UMBRELLA + DERIVED TAG.**

The term is useful and established, but its current scope is too broad to support strong canonical family similarity. Faithless Looting, Index, surveil, cycling, self-mill, Brainstorm, and finite-sample selection all affect card flow/quality while performing materially different operations.

Canonical mechanics should instead preserve operation signatures such as:

- draw-then-discard / discard-then-draw;
- inspect + reorder;
- inspect + disposition to graveyard/bottom/top;
- cycle/replace;
- self-mill;
- finite-sample selection for privileged use/destination.

`Card Filtering` may derive from those signatures for UI counts/search, but generic Filtering overlap should be low-information for Searcher B.

### 3.6 Bounded Extraction / former Card Prospecting

**Outcome: PROMOTE AS SURFACED FACET/SIGNATURE; do not restore as a peer trunk.**

The mechanical distinction survives strongly. Dig Through Time, Collected Company, Plunge into Darkness, Impulse, Fact or Fiction, Genesis Wave, Winota, Gonti, and Thief of Sanity all expose a **finite sample** and select from that sample for privileged destination/use.

However `extraction` is too narrow for effects that put cards directly onto the battlefield, and `bounded` sounds like a fixed/small threshold even though Plunge uses arbitrary player-chosen X.

Required coordinates:

- sample source/zone;
- sample depth as literal or expression;
- fixed / variable / resource-controlled depth;
- cards selected / cardinality expression;
- eligibility domain;
- selection authority, including multi-stage/opponent partition;
- selected destination/use;
- unselected disposition;
- visibility;
- whether sample is one-shot or repeated.

**Structural conclusion:** the current `Filtering family + independently surfaced finite-sample signature` consolidation survives, but only after generic Filtering is demoted from a strong similarity family.

### 3.7 Tutor

**Outcome: FAMILY / surfaced functional concept. RETAIN.**

Evidence forces a stable player-facing distinction: selection/search over the broader library domain rather than a finite exposed sample.

Tutor must preserve:

- whose library;
- search domain/eligibility;
- selection authority;
- quantity;
- failure-to-find semantics derived from CR 701.23;
- reveal/visibility;
- destination;
- use permission if destination itself does not create ordinary access.

Gifts Ungiven, Praetor's Grasp, Rampant Growth-style land search, Entomb-like destinations, and library-to-battlefield search should remain comparable as Tutors without pretending their destinations are equivalent.

### 3.8 Top-Library Access

**Outcome: SURFACED FACET. RETAIN.**

This survives the audit cleanly because the positive/negative boundary is permission-based rather than zone-word-based.

- Future Sight/Mystic Forge/Oracle of Mul Daya/Bolas's Citadel/Xanathar: positive.
- Enlightened Tutor/reveal-only/look-only/reorder-only: negative.

`PLAY` and `CAST` remain hard-distinct.

Searcher B rule: shared `library_top` coordinate alone must carry little or no similarity weight across Tutor-to-top and use-permission cards.

### 3.9 Alternate-Zone Play/Cast Access

**Outcome: PRIMITIVE permission assertion + coordinates, not a family.**

Use one generic permission structure:

- permission holder;
- underlying card/resource identity where known;
- source zone/position;
- owner/provenance;
- `PLAY` / `CAST` / direct deployment action;
- eligibility;
- timing override/restrictions;
- permission window;
- payment handling;
- source/link dependency;
- unused-card disposition.

This structure covers exile, graveyard, library top, opponent cards, linked marked cards, and other unusual zones without another noun per zone.

### 3.10 Temporary exile access / Impulsive Draw

**Outcome: SURFACED FACET + COMMUNITY ALIAS.**

`exile + use permission + finite window` is mechanically stable and queryable. `Impulsive Draw` remains a community/Wizards alias, not literal Draw.

### 3.11 Graveyard Access / Recursion

**Outcome: DEMOTE from broad family to SURFACED ZONE/OPERATION FACET + community alias.**

Regrowth, Reanimate, Underworld Breach, Yawgmoth's Will, Snapcaster, and graveyard-to-library effects share a source zone but perform different jobs.

Store `source_zone = graveyard` plus operation/destination/permission. Expose `Graveyard Access` / `Recursion` for user search, but do not let shared graveyard involvement dominate similarity.

### 3.12 Access Horizon

**Outcome: COORDINATE, not a metric/family.**

The underlying fact is a permission's duration/expiration condition. It is load-bearing but does not need ontology membership.

Required value shapes include:

- resolution-only;
- until end of turn;
- through end of next turn;
- next named step/phase/event;
- while source/condition remains true;
- while card remains in zone;
- indefinite;
- recurring/capped windows.

### 3.13 Sequential Library Traversal

**Outcome: EVENT/OUTPUT SIGNATURE; optionally surfaced facet. RETAIN, BROADEN.**

The evidence supports ordered traversal as real structure but falsifies a first-qualifier-only definition.

Store:

- library owner(s);
- order/direction;
- exposed-card action;
- continue/stop rule;
- stopping predicate;
- qualifying-count expression (`first`, `Xth`, etc.);
- player-controlled stop option;
- disposition of skipped/nonselected cards;
- selected/result action.

Cascade, Discover, Etali, Ad Nauseam, Primal Surge, Possibility Storm, and Dack Fayden, Helping Hand then fit without exception nouns.

### 3.14 Repeat-Use / Additional Execution

**Outcome: EVENT/OUTPUT SIGNATURE + coordinates; not a family.**

The common truth is execution multiplicity, not extra physical/card-origin resources.

Required distinctions:

- same underlying card re-cast;
- delayed re-cast permission;
- copy created and cast;
- repeated copy generation from stored imprint;
- finite vs reusable execution count;
- source zone;
- additional/alternative cost;
- consumption/exile/replacement on completion.

Flashback, Rebound, Retrace, Aftermath, Escape, Buyback, Adventure, Isochron Scepter, Mizzix's Mastery, Mnemonic Deluge, and Arcane Bombardment should not be flattened into one `repeat use` boolean.

---

## 4. Resource/accounting cluster

### 4.1 Resource-Type Separation

**Outcome: RETAIN AS ARCHITECTURE/DATA-MODEL INVARIANT; retire as ontology noun.**

The evidence strongly requires typed resources, but `Resource-Type Separation` describes how Foundry should model facts, not a card function.

Canonical resource records should distinguish at minimum:

- underlying card-origin objects/resources;
- generated non-card objects/tokens;
- mana and mana-capable objects;
- permissions;
- execution/copy opportunities;
- life;
- counters/stored capacity;
- other CR-grounded resource/state kinds.

### 4.2 Card Resource Differential

**Outcome: DERIVED ACCOUNTING FACT, not family/trunk. RETAIN WITH HARDER BOUNDARY.**

The current name describes a useful projection, but canonical storage should be the underlying before/after resource facts.

The audit answers the open questions as follows:

1. **Top-card eligibility:** categorical permission eligibility matters. `CAST` does not make a land accessible; `PLAY` can cover a land.
2. **Present mana affordability:** **do not require it for canonical card-resource counting.** A card in hand does not stop being a card resource merely because its controller currently lacks mana. Affordability belongs to realization/actionability, not resource identity.
3. **Timing/land-play availability:** preserve as separate current-actionability facts. They may make the resource unusable *right now* without erasing the underlying permission/resource from the horizon model.
4. **Continuous top access:** at most the current underlying top card occupies the extra accessible slot at a time. Refreshability/throughput is a separate property, not cumulative stock.
5. **Source permanent:** moving a source card from hand to battlefield does not create another card-origin object; it is the same resource in a different zone. Never count it twice merely because it persists.
6. **Temporary exile/graveyard permission:** access to a previously inaccessible underlying card may change the accessible-resource set during its permission window; expiration removes that access if unused.
7. **Repeat use:** another execution opportunity for the same card is not another simultaneous underlying card-origin resource.
8. **Copies:** spell/card copies are not additional card-origin resources for this accounting.
9. **Recovery effects:** `graveyard -> hand` is not automatically `+1` if the same underlying card was already independently usable before the move. Derive from resource identity before/after.
10. **Multiplayer:** retain per-player / pairwise vectors; do not hide Mixed outcomes behind one average.

**Still OPEN:** whether UI should expose a separate `currently actionable` count alongside the broader resource accounting. If added later, it must be a projection from existing permission/timing/payment facts, not a resurrected `Card Access Differential` ontology concept.

### 4.3 Card Advantage

**Outcome: COMMUNITY/THEORY TERM + STRATEGIC PROJECTION, not canonical mechanical family.**

Use `Card Advantage` educationally and in later strategy reasoning. Canonical Foundry should report the typed resource changes / Card Resource Differential facts from which conventional card-advantage interpretations can be explained.

`Virtual Card Advantage` and `Card Quality` remain downstream strategic/game-state concepts.

### 4.4 Stored Capacity

**Outcome: COORDINATE/PATTERN. RETAIN.**

`setup/input -> stored finite reserve -> later discharge` is a real mechanical pattern across cards, mana, counters, and other resources. Dawn of a New Age and Arcane Bombardment-style stored repertoires show why it should remain cross-domain rather than become a Card Access family.

### 4.5 Role Compression

**Outcome: DERIVED ACCOUNTING/PRODUCT FACT; do not make a canonical card family.**

Foundry already stores a card's multiple independent functions. `Role Compression` is derivable from that composition and is most useful in deck/workspace deltas.

Preserve additionally:

- whether functions are simultaneous or mutually exclusive modes;
- whether they arise from the same semantic unit or separate abilities;
- number/list of materially distinct surfaced functions.

Do not create a subjective `good role compression` score in canonical truth.

---

## 5. Mana / cost / payment cluster

### 5.1 Ramp

**Outcome: FAMILY / public functional trunk. RETAIN.**

Ramp has durable player recognition, deck-level measurement value, and a coherent functional outcome: increasing usable mana or mana-producing capacity beyond ordinary development.

The audit **does not** support promoting every mechanism beneath Ramp into a named child.

Mechanisms such as source creation, source augmentation, multiplier, granting, event-to-mana conversion, state-scaled output, reuse, additional-land deployment, and resource-to-mana conversion should primarily be event signatures/coordinates that the UI can explain in plain language.

### 5.2 Fast Mana

**Outcome: DEMOTE from hard child family to SURFACED COMMUNITY TAG derived from measurable same-turn acceleration facts.**

The current `initial relevant use` rule is arbitrary at the margin. Treasonous Ogre demonstrates the problem: same-turn net positive mana can arise after multiple uncapped activations, but the existing rule refuses to recognize it because the first activation does not cross deployment break-even.

Store instead:

- deployment mana cost;
- immediate mana output;
- same-turn net mana after first use;
- activations required for break-even/positive delta where finite;
- external nonmana resource cost;
- persistence;
- timing/summoning-sickness constraints.

`Fast Mana` remains an excellent search alias/tag for conventional use, but should not distort the canonical Ramp tree around a fragile threshold.

### 5.3 Ritual

**Outcome: COMMUNITY ALIAS / surfaced tag over one-shot burst mana.**

Do not make Ritual synonymous with Fast Mana or Ramp. One-shot/burst production is the harder mechanical fact.

### 5.4 Cost Reduction

**Outcome: PRIMITIVE / surfaced mechanical tag. RETAIN.**

Represent as a cost-modification operation (`reduce`) with affected action/spell domain, amount/formula, symbols, conditions, duration, and floor/minimum rules.

Affinity is a clean positive anchor.

No separate large ontology tree is required.

### 5.5 Formal Alternative Cost

**Outcome: PRIMITIVE / exact rules category. PROMOTE explicitly.**

Use the CR 118.9 meaning. Examples include `without paying its mana cost` and other costs paid instead of mana cost, plus keywords whose CR defines an alternative cost (e.g. Flashback/Escape where applicable).

Do not use this term for Convoke/Delve/Improvise.

### 5.6 Payment Substitution / payment method

**Outcome: PRIMITIVE/COORDINATE distinct from formal Alternative Cost.**

Convoke, Delve, Improvise, Phyrexian-symbol life payment, and similar structures alter **how an already-determined cost is satisfied**.

Recommended structure:

- `cost_total_modifier`: reduce/increase/set/etc.;
- `formal_alternative_cost`: yes/no + cost expression;
- `additional_cost`: yes/no + expression;
- `payment_method`: mana / tap creature / tap artifact / exile grave card / life-for-symbol / other;
- payment restrictions/conversion rate.

This split preserves CR truth and Searcher B similarity without a misleading `Alternate Payment` parent.

### 5.7 Mana preservation

**Outcome: COORDINATE / adjacent resource mechanic, not automatically Ramp.**

Preserving already-produced mana across steps/phases changes resource persistence without inherently increasing production.

---

## 6. Deployment / zone-change cluster

### 6.1 Direct Placement (formerly working `Deployment Bypass`)

**Outcome: EVENT/OUTPUT SIGNATURE + SURFACED FACET. RETAIN DISTINCTION.**

The evidence forces the cast-vs-put distinction. Elvish Piper, Reanimate, Show and Tell, Sneak Attack, Genesis Wave, and Winota bypass the spell-casting procedure for the placed object. Omniscience does not.

Preserve source/destination, object eligibility, controller, simultaneity, temporary cleanup, timing, and whether a cast event occurs.

### 6.2 Recursion / Reanimation

**Outcome: COMMUNITY/SURFACED aliases over zone + operation facts.**

- `Reanimation` is useful when a creature card is put from graveyard to battlefield.
- `Recursion` is broader player language for recovering/reusing graveyard resources.

Neither should erase exact source/destination/use mechanism.

---

## 7. Engine / repeatability cluster

### 7.1 Engine

**Outcome: COLLAPSE FROM CANONICAL FAMILY TREE TO DERIVED STRUCTURAL/COMMUNITY TAG.**

The current documents discovered useful hard facts but overfit the word `Engine` to a narrower definition than players ordinarily use.

The One Ring, Phyrexian Arena, Chivalric Alliance, Grazilaxx, Toski, Well of Lost Dreams, Sram, Rhystic Study, Lotus Cobra, Carrion Feeder, and Nest of Scarabs establish the more durable substrate:

- input/event kind;
- input availability/dependency;
- input aggregation (`one or more`, threshold, per-object, per-player);
- trigger/firing multiplicity;
- output magnitude/multiplicity;
- intrinsic frequency cap;
- opportunity window;
- processor retention after firing;
- input consumption;
- stored capacity/repertoire;
- feedback dependency;
- external fuel requirement.

These facts are mechanically useful even when reasonable players disagree over whether a card is an `engine`.

**Why demote:** a strict Engine gate would harm Searcher B by separating mechanically adjacent recurring-value cards primarily because of a project-specific definition of a community term. The hard processor coordinates already provide better similarity.

UI/search may still expose `Engine` as a derived/community handle and explain the matched processor facts.

### 7.2 Card Engine / Mana Engine / Blink Engine / Death-Trigger Engine / Sacrifice Engine

**Outcome: COLLAPSE as canonical children. Preserve as derived aliases/search views.**

Query shape should instead be approximately:

`repeatable/scalable processor facts + output/resource/operation domain`.

This produces the same discoverability without maintaining a heterogeneous child tree whose members are variously output-, operation-, event-, or input-oriented.

### 7.3 turn_structure_bound

**Outcome: COORDINATE, rename later.**

The useful fact is an intrinsic firing/opportunity cap, not a noun. Preserve whether another output requires another discrete combat/upkeep/end-step/turn opportunity.

### 7.4 Engine component / combo component

**Outcome: RELATIONSHIP-LAYER fact, not canonical family.**

Producer/consumer graphs can later show that one card feeds another or participates in a loop. Infinite-combo potential remains separate from processor mechanics.

---

## 8. Interaction cluster

### 8.1 Interaction

**Outcome: UI/navigation umbrella, not a hard family.**

The umbrella is useful for deck counts and browsing; its children must be mechanically explicit.

### 8.2 Removal

**Outcome: FAMILY / public functional concept. RETAIN.**

Removal earns a noun because players search and count the job directly, while lower-level coordinates preserve action (destroy/exile/bounce/sacrifice/direct damage where lethal is structurally guaranteed), object class, targeting, scope, duration, and restrictions.

Do not force all shared `Removal` membership to imply high similarity; object/action/duration matter.

### 8.3 Taxation

**Outcome: FAMILY / surfaced functional concept. RETAIN.**

Mechanically increases the cost/requirement to take an action without making it impossible. This remains distinct from Permission Denial.

### 8.4 Permission Denial

**Outcome: FAMILY / surfaced functional concept. RETAIN.**

Mechanically prohibits an action/permission. Grand Abolisher-style prohibition and Defense Grid-style taxation may be outcome-adjacent for Searcher B while remaining mechanically distinct.

### 8.5 Lockdown

**Outcome: OPEN / likely derived search label.**

Current evidence is insufficient here to justify a separate hard family independent from persistent Permission Denial, Taxation, disabling/tapping restrictions, and other underlying interaction facts. Preserve the term for search/strategy pending a bounded dedicated audit.

### 8.6 Graveyard Denial

**Outcome: SURFACED FACET/search view, not necessarily a peer family.**

Graveyard hate can exile cards, prevent entry, replace zone movement, prohibit casting/activation, or remove abilities. Preserve the exact interaction operation + affected zone and expose `Graveyard Denial` as a useful player handle.

### 8.7 Counterspell

**Outcome: SURFACED mechanical tag / event signature.**

`counter spell/ability` is mechanically crisp. Exact target scope and uncounterable interactions remain coordinates.

### 8.8 Hand Disruption / Discard

**Outcome: FAMILY/search view over discard/hand-denial primitives.**

Targeted discard, random discard, whole-hand replacement, and symmetrical Wheels should remain distinguishable. Wheel membership must not imply the same resource differential.

### 8.9 Sweeper / Board Wipe

**Outcome: SURFACED TAG derived from Removal/interaction scope.**

Mass scope is useful to include/exclude; no separate ontology tree is required if affected set/quantity is already represented.

### 8.10 Edict

**Outcome: COMMUNITY ALIAS / retrieval DNA.**

Resolve to sacrifice-based Removal + affected player chooses from eligible set + quantity/scope. Do not create an Edict parent.

### 8.11 Burn

**Outcome: COMMUNITY/STRATEGIC ALIAS.**

Resolve to damage/life-loss primitives + recipient/amount/targeting and any resulting Removal/player-pressure context.

### 8.12 Stax

**Outcome: RETIRED as canonical family; community/search alias only.**

The prior retirement is correct. It conflates taxation, permission denial, lockdown, graveyard denial, resource suppression, and other different mechanisms.

---

## 9. Keyword/event cluster

### 9.1 Keyword Consequence Registry

**Outcome: RETAIN AS PRE-CORPUS DERIVATION INFRASTRUCTURE.**

This survives attack strongly. Myriad/Mobilize demonstrate why a keyword label alone loses ETB, token, attack, delayed cleanup, sacrifice, death, exile, LTB, and non-event facts.

The registry should emit:

- primitives;
- producer event signatures;
- consumer/listener signatures;
- delayed consequences;
- negative/non-event facts;
- copy/inheritance payload;
- context-sensitive caveats.

### 9.2 Token Generation

**Outcome: PRIMITIVE / event signature.**

Token object characteristics and later capabilities are separate facts. Do not convert token count into card-origin-resource count.

### 9.3 Mill, Scry, Surveil, Connive, Cycling, Cascade, Discover, Flashback, Rebound, Retrace, etc.

**Outcome: KEYWORD CONSEQUENCE SIGNATURES + surfaced aliases where players search by name.**

Do not duplicate their full rules consequences as independent card-family trees when the consequence registry can project the mechanically relevant facts.

---

## 10. Searcher B weighting / similarity consequences

A major audit result is that **broad shared nouns should not dominate similarity**.

Recommended information hierarchy for similarity:

1. same operation/event signature + compatible object/resource participants;
2. same functional outcome with mechanically different but outcome-adjacent operations;
3. compatible restrictions/eligibility/scope/destination/duration;
4. same surfaced facet/tag;
5. same broad UI umbrella only — weak evidence;
6. shared word/zone alone — near-zero evidence absent matching operation.

Examples:

- Dig Through Time vs Collected Company: strong finite-sample-selection kinship, destination/eligibility differences visible.
- Dig Through Time vs Faithless Looting: broad Filtering adjacency only; much weaker than their shared public umbrella suggests.
- Enlightened Tutor vs Future Sight: shared library-top involvement should provide almost no direct functional similarity.
- Grand Abolisher vs Defense Grid: different interaction mechanisms, but downstream proactive-turn suppression can be a later outcome projection.
- Flashback vs Mnemonic Deluge: both increase spell executions, but original-card reuse vs copy execution must remain different.

---

## 11. Explicit outcome ledger

### Retained as families / strong player-facing functional concepts

- Ramp
- Tutor
- Removal
- Taxation
- Permission Denial
- Hand Disruption (with discard primitives beneath)

### Retained/promoted as surfaced tags/facets

- Top-Library Access
- finite-sample selection (working former `Bounded Extraction`)
- Temporary Exile Access
- Direct Placement
- Counterspell
- Sweeper / mass-interaction scope
- Graveyard Access/Denial as zone-centric search views
- Fast Mana as community-derived surfaced tag, not hard child

### Retained as primitives / event/output signatures / coordinates

- Literal Draw
- use permission (`PLAY` vs `CAST`)
- permission duration/window
- ordered library traversal + stop rule
- selection authority / partition / selected cardinality
- source/destination/owner/controller/provenance
- repeat/additional execution
- copy/execution provenance
- Cost Reduction
- formal Alternative Cost
- payment method/substitution
- additional cost
- Direct Placement event
- typed resource outputs
- stored capacity
- processor throughput/firing-cap facts
- Ramp mechanism signatures
- keyword consequence producer/consumer signatures

### Derived accounting facts

- Card Resource Differential
- self-replacing / parity / positive / negative resource delta
- multiplayer differential vector / Mixed state
- Role Compression

### Collapsed / demoted

- Card Access as canonical family -> UI umbrella
- Card Filtering as strong canonical family -> UI/search umbrella/derived tag over harder operations
- Bounded Extraction as peer trunk -> surfaced finite-sample signature
- Graveyard Access as mechanism family -> zone+operation surfaced view
- Repeat-Use as family -> execution signature
- Engine parent tree -> derived/community/search label over processor facts
- Card/Mana/Blink/Death-Trigger/Sacrifice Engine children -> derived query views
- Fast Mana hard child -> surfaced community tag over measured acceleration profile
- Resource-Type Separation ontology noun -> substrate invariant
- Cost Reduction tree -> primitive + facets
- Alternate Payment tree -> split into formal Alternative Cost vs payment method

### Retired

- Card Replacement family
- Card Access Differential metric
- Stax canonical family
- narrow pre-realignment Cantrip definition
- old Card Sifting / Card Prospecting names as independent siblings
- `Deployment Bypass` name

### Strategic/community only

- Card Advantage as broad theory term
- Virtual Card Advantage
- Card Quality
- Burn (broad strategic label)
- Stax (search/community alias)
- `Engine` when used in broad deckbuilding language
- `good/bad`, power, desirability, underplayed/overplayed judgments

### OPEN / bounded research still required

- exact player-facing treatment of `Lockdown` independent from Denial/Taxation;
- whether a `currently actionable card resources` UI projection is valuable, without creating a new canonical metric;
- final threshold/derivation for conventional `Fast Mana` search tag;
- exact supported `Hand Disruption` surface hierarchy;
- exact strategy-layer mapping of `Engine` aliases after processor facts are finalized;
- corpus validation of finite-sample-selection edge cases after final naming;
- full keyword-consequence registry census before broad corpus execution.

---

## 12. Structural corrections required before naming

The following documentation changes are justified now, before the naming pass:

1. mark `OBJECTIVE6-CARD-ACCESS-DIFFERENTIAL-RULING-2026-09-19.md` **SUPERSEDED** by the later Captain correction; no separate metric;
2. revise Card Resource Differential to state that it is **derived accounting over distinct underlying card-origin resources**, with copies/execution multiplicity excluded and affordability separated from resource identity;
3. revise Card Filtering / Bounded Extraction candidate to keep generic Filtering low-weight and finite-sample selection surfaced;
4. revise Engine documents to preserve throughput facts while demoting the canonical Engine hierarchy;
5. revise Cost Reduction / Alternate Payment documentation to distinguish formal CR alternative costs from payment methods/substitutions;
6. revise Card Access accepted-components documentation so Access Horizon is a coordinate, Repeat-Use is an execution signature, Resource-Type Separation is a data-model invariant, and Sequential Library Traversal is an event signature;
7. preserve Top-Library Access as surfaced facet and Direct Placement distinction;
8. preserve Keyword Consequence Distillation as a pre-corpus gate.

Only after these structural corrections should final names be selected.

## 13. Audit verdict

**Objective 6 is structurally improved by this audit, but it is not freeze-ready yet.**

The main conceptual risk is no longer missing nouns. It is accidentally allowing public umbrella terms or community language to become stronger semantic evidence than the mechanical facts underneath them.

The next step is the ordered global naming audit **after** the structural documents above are corrected.

No S16B freeze is authorized by this verdict.
