# Objective 6 — Global Naming Audit / Semantic Freeze Candidate

**Date:** 2026-09-19  
**Status:** **NAMING PROPOSAL AFTER STRUCTURAL AUDIT — FREEZE CANDIDATE, NOT A FREEZE**  
**Required predecessors:** Weird-card adversarial corpus hunt -> whole-vocabulary adversarial semantic audit -> structural corrections.

## 1. Naming principles

Names were evaluated for:

- mechanical faithfulness;
- immediate comprehension;
- consistency;
- player recognition;
- brevity;
- memorability;
- distinction from neighboring concepts;
- avoidance of Comprehensive Rules collisions;
- avoidance of misleading established community meanings;
- usefulness in UI/search;
- clean machine-facing semantics.

A name does not rescue a structurally weak concept. The structural audit has already demoted/collapsed concepts that do not deserve their own canonical noun.

## 2. Proposed naming crosswalk

| Old / working name | Proposed final name | Structural type | Rationale |
|---|---|---|---|
| Card Access | **Card Access** | UI/navigation umbrella | Already clear, player-readable, broad enough for navigation without pretending to be one hard family. |
| Card Sifting | **Card Filtering** | UI/search umbrella / derived tag | Existing correction is better player language. `Sifting` should remain retired. |
| Card Prospecting | **Sample Selection** | surfaced facet/signature | `Prospecting` is invented jargon; `Selection` alone is too broad. `Sample Selection` states the actual finite-sample operation without implying hand-only output. |
| Bounded Extraction | **Sample Selection** | surfaced facet/signature | `Bounded` sounds fixed/small and `Extraction` implies removal/hand gain. Plunge/Company/Genesis Wave prove both implications wrong. |
| Top-Library Access | **Top-Library Access** | surfaced facet | Mechanically explicit and avoids `topdeck`, which commonly means drawing from the top. |
| Alternate-Zone Play/Cast Access | **Card Use Permission** | primitive permission assertion | The hard structure is permission + source zone + action. A new family per zone is unnecessary. |
| PLAY / CAST | **PLAY / CAST** | permission action values | Preserve Magic's hard distinction exactly. |
| Access Horizon | **Permission Window** | coordinate | Says what it actually measures: how long/under what condition a permission remains usable. Less abstract than `horizon`. |
| Sequential Library Traversal | **Library Traversal** | event/output signature | Shorter and clearer. Definition itself states that cards are processed in library order until a stop rule; `sequential` is redundant jargon. |
| Repeat-Use / Additional Execution | **Additional Execution** | event/output signature | Covers same-card recasts and extra executions without falsely implying another card resource. Copy provenance remains a separate coordinate. |
| Resource-Type Separation | **Typed Resources** | substrate invariant | Positive, compact architecture name. Describes the model rather than a separation procedure. |
| Card Resource Differential | **Card Resource Delta** | derived accounting fact | Same useful CRD acronym, shorter, and more accurately describes before/after change. Pairwise opponent-relative deltas remain explicit beneath it. |
| Card Access Differential | **RETIRED — no replacement** | retired | Later Captain correction explicitly rejected the extra metric. Do not rename it back into existence. |
| Card Replacement | **Self-Replacing** only when derived | derived accounting property | The family is retired; `self-replacing` is clear player language for parity without colliding with Magic's formal `replacement effect`. |
| literal draw | **Draw** | primitive/event | Use the Comprehensive Rules term. |
| Cantrip | **Cantrip** | surfaced derived/community tag | Established player vocabulary; no need to invent a Foundry-specific replacement. |
| Tutor | **Tutor** | surfaced functional family | Established, concise, high retrieval value. Underlying machine facts remain library SEARCH + eligibility + chooser + destination. |
| Temporary Exile Access | **Exile Access** | surfaced zone/use facet | Duration is already in Permission Window; `temporary` is redundant in the concept name. `Impulsive Draw` remains alias only. |
| Impulsive Draw | **Impulsive Draw** | community alias | Keep established player/Wizards language as an alias; do not treat it as literal Draw. |
| Graveyard Access | **Graveyard Access** | surfaced zone/use view | Clear user-facing handle. Exact operation/destination remains underneath. |
| Recursion | **Recursion** | community/search alias | Established but broad; resolve to graveyard/zone-change/use facts. |
| Reanimation | **Reanimation** | surfaced/community alias | Useful narrow graveyard-to-battlefield creature pattern; Direct Placement remains the mechanical operation. |
| Deployment Bypass | **Direct Placement** | event signature + surfaced facet | Clear description of what the effect does. Avoids architecture jargon and the misleading implication that every free deployment bypasses casting. |
| Cost Reduction | **Cost Reduction** | primitive/surfaced tag | Exact and familiar. |
| Alternate Payment | **RETIRED as umbrella** | retired | Collides with Magic's formal alternative-cost concept and wrongly groups Convoke/Delve/Improvise with true alternative costs. |
| Payment Substitution | **Payment Method** | primitive/coordinate | Neutral and accurate: describes how a determined cost/symbol is satisfied without implying formal alternative cost. |
| Formal Alternative Cost | **Alternative Cost** | CR-grounded primitive | Use the official CR term with its official meaning. `formal` is needed only in explanatory prose when contrasting categories. |
| Additional Cost | **Additional Cost** | CR-grounded primitive/coordinate | Official, accurate term. |
| Ramp | **Ramp** | surfaced functional family | Established player language with a robust functional boundary. |
| Fast Mana | **Fast Mana** | surfaced community-derived tag | Established player search term. Canonical facts are the measured same-turn acceleration profile, not a brittle custom threshold. |
| Ritual | **Ritual** | community/search alias | Established shorthand over burst/one-shot mana; no need to redefine it as a formal family. |
| One-Shot / Burst Mana | **Burst Mana** | mechanism signature | Short, descriptive, does not imply a specific card type. |
| Independent Mana Source | **Independent Mana Source** | explanatory mechanism view | Already clear. Primarily rendered from source/output coordinates. |
| Additional Land Deployment | **Additional Land Play** | mechanism/permission view | Matches the actual permission granted by Exploration-like effects. Distinguishes it from putting a land directly onto battlefield. |
| Mana-Source Augmentation | **Mana Source Augmentation** | mechanism view | Clear fixed-additive modification of an existing source. |
| Mana Multiplier | **Mana Multiplier** | mechanism view | Clear proportional scaling term. |
| Resource-to-Mana Conversion | **Resource Conversion → Mana** | machine/explanation pattern | Treat conversion as typed input/output rather than minting a family for every input resource. UI can say `Life → Mana`, `Card → Mana`, etc. |
| Mana-Source Creation | **Mana Source Creation** | event/output signature | Clear. |
| Mana-Source Granting | **Mana Ability Grant** | event/static signature | More exact: grants mana-producing ability/capability to an existing object. |
| Event-to-Mana Conversion | **Event-Driven Mana** | mechanism view | Player-readable label over listener/event -> mana output facts. |
| Board/State-Scaled Mana | **State-Scaled Mana** | coordinate/view | Shorter; scaling basis remains explicit. |
| Mana-Source Reuse | **Mana Source Reuse** | mechanism view | Clear for untap/reuse patterns. |
| Mana preservation | **Mana Persistence** | resource-state coordinate | States the actual property: mana persists across windows where it would normally empty. |
| Engine | **Engine** | derived/search/community label | Keep the familiar word, but do not make it a canonical hard family. The correction is structural, not lexical. |
| Card Engine | **Card Engine** | derived search label | Familiar query rendered from processor facts + card-resource output. Not a canonical child. |
| Mana Engine | **Mana Engine** | derived search label | Familiar query rendered from processor facts + mana output/Ramp. Not a canonical child. |
| Blink Engine / Death-Trigger Engine / Sacrifice Engine | **keep as search phrases only** | derived aliases | Their canonical structure is processor facts + operation/event domain, not a heterogeneous Engine ontology. |
| turn_structure_bound | **requires_new_opportunity** | machine coordinate | States the hard fact directly. UI should explain the actual gate, e.g. `Needs another combat` or `Once each upkeep`. |
| Stored Capacity | **Stored Capacity** | coordinate/pattern | Clear cross-resource pattern; no better name is needed. |
| Role Compression | **Role Compression** | derived product/accounting term | The term is already used in TCG/MTG deckbuilding for one card filling multiple roles. Keep it outside canonical card mechanics and derive it from function composition. |
| Interaction | **Interaction** | UI/navigation umbrella | Standard player language; children/mechanisms carry actual semantics. |
| Removal | **Removal** | surfaced functional family | Established and useful. |
| Taxation | **Taxation** | surfaced functional family | Clear contrast with prohibition/denial. |
| Permission Denial | **Permission Denial** | surfaced functional family | Precise without overloading `counter` or `lock`. |
| Lockdown | **Lockdown** | OPEN search/community label | Keep the familiar phrase searchable, but do not freeze a hard family until a dedicated boundary audit proves one. |
| Graveyard Denial | **Graveyard Denial** | surfaced zone/interaction view | Clear user handle over exact denial/removal/replacement operations. |
| Counterspell | **Counterspell** | surfaced mechanical tag/search term | Highly recognizable; machine action remains `counter spell/ability`. |
| Hand Disruption | **Hand Disruption** | surfaced functional/search concept | Established and broader than discard alone. |
| Sweeper / Board Wipe | **Mass Removal** | surfaced tag | Mechanically descriptive canonical label; keep `Sweeper` and `Board Wipe` as search aliases. |
| Edict | **Edict** | community/search alias | Keep player term but resolve to sacrifice-based Removal + affected-player selection. |
| Burn | **Burn** | community/strategic alias | Keep search term; canonical facts are damage/life loss/recipient/amount. |
| Stax | **Stax** | community/search alias only | Familiar but mechanically heterogeneous; canonical family remains retired. |
| Card Advantage | **Card Advantage** | community/theory/strategic term | Preserve established Magic meaning without redefining it as Foundry's typed resource accounting. |
| Virtual Card Advantage | **Virtual Card Advantage** | strategic term | Established theory term; context-sensitive by nature. |
| Card Quality | **Card Quality** | strategic term | Context/deck/state dependent; not canonical card mechanics. |
| Keyword Consequence Registry | **Keyword Consequence Registry** | derivation infrastructure | Accurate and already clear. |
| producer event signatures | **Producer Signatures** | event/output infrastructure | Shorter without losing meaning. |
| consumer/listener signatures | **Consumer Signatures** | event/listener infrastructure | Shorter; `listener` can remain explanatory text. |
| token generation | **Token Creation** | primitive/event signature | Align with Magic's `create` wording; object characteristics remain typed separately. |

## 3. Names deliberately *not* made cooler

Several names survive unchanged because a more stylish label would lose precision:

- Tutor;
- Ramp;
- Top-Library Access;
- Cost Reduction;
- Alternative Cost;
- Additional Cost;
- Removal;
- Taxation;
- Permission Denial;
- Stored Capacity.

Objective 6 should not optimize novelty. A boring exact name is better than an evocative misleading one.

## 4. The key renamed concepts

The largest naming improvements are:

### `Bounded Extraction` -> **Sample Selection**

Why:

- Plunge into Darkness proves the sample may be arbitrarily large but finite;
- Collected Company / Genesis Wave prove selection need not `extract` to hand;
- the name focuses on the invariant: choose from an exposed finite sample.

### `Access Horizon` -> **Permission Window**

Why:

- duration belongs to a permission;
- `window` reads naturally for resolution-only, EOT, next-turn, while-exiled, and indefinite conditions;
- `horizon` sounds like architecture jargon.

### `Sequential Library Traversal` -> **Library Traversal**

Why:

- the definition already carries order/stop rule;
- handles first-match, Xth-match, repeat-while, and player-controlled stop cases;
- shorter without becoming vague.

### `Resource-Type Separation` -> **Typed Resources**

Why:

- positive model description rather than a procedure;
- clearly architecture-level, not a card ability.

### `Card Resource Differential` -> **Card Resource Delta**

Why:

- preserves CRD acronym;
- shorter;
- `delta` directly communicates change;
- opponent-relative comparisons can be represented as relative/pairwise deltas rather than overloaded into the concept name.

### `Deployment Bypass` -> **Direct Placement**

Why:

- says what happened;
- cleanly contrasts with `CAST`;
- works for hand/graveyard/library/exile origins;
- avoids `cheat` as canonical language while keeping `cheat into play` as a search alias.

### `Payment Substitution` -> **Payment Method**

Why:

- Convoke/Delve/Improvise do not become formal alternative costs;
- avoids implying the payment is always a one-for-one substitute;
- cleanly coexists with Cost Reduction, Alternative Cost, and Additional Cost.

## 5. Search alias policy

Community language should be retained aggressively for retrieval even when it is not canonical ontology.

Examples:

- `impulse draw` -> Exile Access + finite Permission Window;
- `cheat into play` -> Direct Placement;
- `draw engine` -> processor facts + card-resource output;
- `mana engine` -> processor facts + mana output/Ramp;
- `board wipe` / `sweeper` -> Mass Removal;
- `edict` -> sacrifice-based Removal + affected-player selection;
- `burn` -> damage/life-loss semantic DNA;
- `stax` -> multiple interaction mechanisms, never one forced canonical family;
- `recursion` -> graveyard/zone recovery/access facts.

Alias matching should improve discovery without silently asserting mechanical equivalence.

## 6. Machine-facing naming rule

Internal names should state the fact directly rather than mimic public branding.

Examples:

- `permission_action = PLAY | CAST`;
- `permission_window = resolution | end_of_turn | end_of_next_turn | while_exiled | condition | indefinite | ...`;
- `sample_depth = literal | expression`;
- `selection_authority = controller | opponent | active_player | ...`;
- `traversal_stop_rule = first_match | qualifying_count | player_stop | repeat_while | ...`;
- `requires_new_opportunity = true/false + opportunity_kind`;
- `resource_kind = card_origin | generated_object | mana | permission | execution | life | counter | ...`;
- `execution_provenance = same_card | copied_card | spell_copy | delayed_recast | ...`.

These examples are semantic naming guidance, not a ratified storage schema.

## 7. Freeze-candidate vocabulary surface

### Strong public functional families

- Ramp
- Tutor
- Removal
- Taxation
- Permission Denial
- Hand Disruption

### Surfaced facets/tags/search views

- Top-Library Access
- Sample Selection
- Exile Access
- Graveyard Access
- Direct Placement
- Fast Mana
- Counterspell
- Mass Removal
- Cantrip

### Mechanical primitives/signatures/coordinates

- Draw
- Card Use Permission
- Permission Window
- Library Traversal
- Additional Execution
- Cost Reduction
- Alternative Cost
- Additional Cost
- Payment Method
- Stored Capacity
- Typed Resources
- Producer Signatures
- Consumer Signatures
- Token Creation
- exact Ramp mechanism/resource coordinates
- exact keyword-consequence expansions

### Derived/accounting/product facts

- Card Resource Delta
- self-replacing/parity/resource-change states
- Role Compression
- processor/throughput profiles

### Community/search/strategic terms

- Engine / Card Engine / Mana Engine / other Engine phrases
- Card Advantage / Virtual Card Advantage / Card Quality
- Ritual
- Impulsive Draw
- Recursion / Reanimation
- Edict
- Burn
- Stax
- Sweeper / Board Wipe
- Lockdown (pending dedicated hard-boundary proof)

### Retired canonical concepts/names

- Card Replacement family
- Card Access Differential
- Card Sifting as separate concept
- Card Prospecting
- Bounded Extraction
- Deployment Bypass
- Alternate Payment umbrella
- canonical Engine hierarchy/children
- Resource-Type Separation as an ontology noun

## 8. Remaining naming uncertainty

Only a small number of names remain genuinely unsettled:

1. `Sample Selection` is mechanically strong but should receive one final UI-readability check during formal freeze review.
2. `Permission Denial` is precise but somewhat formal; no clearer candidate found that avoids conflating prohibition with Taxation/Counterspell.
3. `Lockdown` remains structurally OPEN, so its name cannot be finalized as a canonical family.
4. `Card Resource Delta` is proposed as the final public/machine projection name; the underlying accounting contract must still be formally tested on stateful examples before freeze.

These are freeze-review questions, not reasons to add new semantic nouns now.

## 9. Naming verdict

The naming audit supports this vocabulary as a **semantic freeze candidate**, not an actual freeze.

The remaining work before formal freeze review is verification, not another broad invention pass:

- confirm all candidate docs use the revised structural types/names or clearly mark historical supersession;
- run a focused stateful Card Resource Delta fixture set;
- run a focused Sample Selection UI/retrieval fixture set;
- complete the required Keyword Consequence Registry census/design gate;
- verify no stale Objective 6 file still presents superseded concepts as live authority.

No freeze is authorized by this document.
