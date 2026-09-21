# S16B Objective 6 — Keyword Consequence Registry Census / Design Gate

**Date:** 2026-09-21  
**Status:** **BOUNDED DESIGN GATE COMPLETE / S16B NOT FROZEN**  
**Implementation authorization:** **NONE**

> **PRESERVE TRUTH, NOT PLUMBING.**

This is the bounded census/design gate required by current Objective 6 routing. It does **not** implement or populate a production registry, run a full semantic corpus pass, implement S16A, resume AQ4, or implement the Oracle Ingest Compiler.

## 1. Input identity and census

The project-source Oracle snapshot used for this bounded census is the same corpus identity already measured by accepted S16A evidence:

- gzip SHA-256: `b46e0670a8f3fa2d5357ec35ff7f8d58e7c2f9f15db0e27a3b0543672b00c217`;
- gzip size: `22,735,516` bytes;
- decompressed SHA-256: `5e47e1325a3987db745a941307080830696cbac2f6aa80d8f88f8a6dad90723c`;
- raw Oracle records: `38,233`;
- previously certified Gate #0 population: `32,557` cards / `33,393` face records.

For the bounded keyword census, the raw snapshot contains:

- `17,565` records with a nonempty `keywords` field;
- `846` distinct provider keyword labels.

The `846` label count is **not** asserted to be the Comprehensive Rules count of keyword abilities. Provider labels are discovery inputs, not semantic authority.

The attached 2026-08-07 Comprehensive Rules machine-readable source contains:

- `195` rule-section heads under 702 keyword abilities;
- `70` rule-section heads under 701 keyword actions.

CR 207.2c remains an important negative control: **ability words have no rules meaning by themselves**. A registry must not infer a fixed consequence merely from an ability-word label.

Representative raw provider-label counts used only as a coverage census include:

- Cascade: 38
- Discover: 33
- Hideaway: 15
- Myriad: 23
- Mobilize: 16
- Spree: 21
- Ward: 213
- Delve: 30
- Convoke: 105
- Improvise: 24
- Flashback: 209
- Storm: 40
- Dredge: 14
- Suspend: 74
- Foretell: 54
- Plot: 40

These counts are not family membership claims.

## 2. Why a shared consequence registry is justified

Keyword text is compressed rules text. Downstream semantics need the rules-defined consequences, not merely the printed/provider keyword name.

The existing Objective 6 design direction remains correct:

`source term -> normalized parameters -> required/conditional event graph -> required relations/state slots -> shallow family/facet contribution`

The registry is therefore a **mechanical expansion/normalization aid**, not a parallel ontology and not a machine for promoting every keyword into a public family.

## 3. Current-machinery classification

The bounded audit classifies the relevant ownership areas as follows.

| Concern | Gate classification | S16B consequence |
|---|---|---|
| Printed/provider keyword identity | `ALREADY_DERIVABLE` | Useful discovery/provenance input; label alone is not semantics. |
| CR 702 keyword-ability definitions | `ALREADY_DERIVABLE` | Rules source can ground consequence templates. |
| CR 701 keyword-action definitions | `ALREADY_DERIVABLE` | Same design can cover actions while preserving `term_kind`. |
| Parameter extraction/binding (`N`, costs, chosen values, eligibility) | `EXISTS_BUT_FRAGMENTED` | Future shared owner should normalize parameters. |
| Cross-keyword event/relation expansion | `NEEDS_SHARED_REGISTRY` | One typed consequence contract is preferable to repeated local interpretations. |
| Linked-object/state requirements | `NEEDS_SHARED_REGISTRY` | Registry can declare required link/state slots; actual state values remain elsewhere. |
| Live legality/actionability/state resolution | `DEFERRED_TO_RUNTIME_OR_STATE_MODEL` | Registry must not decide current targets, mana, timing, counters, or changing game state. |
| S16B family/facet projection | `ALREADY_DERIVABLE` at design level | Registry may name admissible shallow contributions; it does not mint ontology families. |
| Ability words under CR 207.2c | `OUT_OF_SCOPE_FOR_S16B` as label-driven expansion | Parse their actual rules text instead. |
| Flavor words / non-rules labels | `OUT_OF_SCOPE_FOR_S16B` as label-driven expansion | No fixed semantic consequence without operative rules text. |
| Production registry storage/population | `DEFERRED_TO_RUNTIME_OR_STATE_MODEL` / future compiler work | Not implemented in this closeout. |

## 4. Minimal registry record contract

A future shared owner should preserve at least:

- `source_term`;
- `term_kind` — e.g. keyword ability, keyword action, structured rules construct;
- `cr_rule_refs`;
- `normalized_parameters`;
- `required_events`;
- `conditional_events`;
- `required_relations`;
- `required_state_or_link_slots`;
- `permission_or_expenditure` facts where applicable;
- `visibility` consequences where rules-defined;
- `timing_window` / delayed-event consequence where rules-defined;
- `family_or_facet_projection` only where a lower-mechanical consequence supports it;
- `confidence/provenance`.

Every emitted consequence must further distinguish:

- `must_emit` — entailed by the recognized term plus its parameters;
- `conditional_template` — emitted only with its triggering/eligibility condition preserved;
- `may_emit` — optional consequence whose choice remains explicit;
- `runtime_dependent` — a required slot whose actual value/outcome depends on game state.

This distinction is mandatory to prevent plausible but false over-derivation.

## 5. Representative consequence classes

### 5.1 Cascade — traversal, not Sample Selection

The rules-defined shape includes a trigger, exile-from-top traversal to the qualifying nonland candidate, optional cast without paying mana cost when eligible, and disposition of the rest.

Registry consequence:

- emit Library Traversal mechanics and the optional cast permission/cost fact;
- preserve the content-dependent stopping predicate;
- **do not** emit Sample Selection merely because a qualifying card is ultimately identified.

### 5.2 Discover — traversal with optional hand/cast outcome

The rules-defined shape traverses until a qualifying nonland card is found; the player may put it into hand or cast it without paying mana cost as allowed; the rest is put on the bottom in random order.

Registry consequence:

- traversal + choice of permitted outcome;
- not Sample Selection by default.

### 5.3 Hideaway — finite sample plus linked state

Hideaway's keyword consequence supplies the finite top-four sample, one face-down exile selection, remainder disposition, and the source controller's ability to look at the exiled card while it remains exiled.

Registry consequence:

- Sample Selection child operation;
- visibility/link facts for the exiled object;
- **do not** manufacture every later play permission found on a particular Hideaway card. Those later permissions belong to separately printed linked abilities.

### 5.4 Myriad — trigger/copy tokens/scheduled exile

The rules-defined shape includes an attack trigger, creation of attacking token copies for the other opponents as specified, and their later exile.

Registry consequence:

- emit the trigger, generated-object/copy provenance, attacking placement, and delayed exile template;
- **do not** assert that combat damage will occur;
- **do not** count the token copies as Card Resource Delta card-origin units.

### 5.5 Mobilize N — parameterized generated-object lifecycle

Emit the attack trigger, `N` tapped-and-attacking Warrior token creations, and next-end-step sacrifice schedule. Preserve `N` as a parameter rather than flattening Mobilize to a boolean label.

### 5.6 Spree — modal/additional-cost structure

Emit the requirement to choose one or more modes and the additional costs associated with chosen modes. Spree is not itself a public family.

This consequence relies on future parser ownership correctly preserving modal structure; the accepted S16A evidence shows that modal ownership is not yet a production implementation fact.

### 5.7 Ward [cost] — conditional counter trigger

Emit the opponent-targeting trigger and the conditional counter-unless-cost-paid structure, with the ward cost preserved as a parameter.

Do not flatten Ward into unconditional Permission Denial.

### 5.8 Flashback / other alternate-zone execution

Emit the relevant zone-use/cast permission, alternative-cost/payment facts, and required post-use disposition as the rules define them.

Do not convert repeated/alternate execution into a second Card Resource Delta identity.

### 5.9 Dredge / replacement-lineage stress

Where a keyword replaces a would-be event, the registry must require typed replacement lineage rather than leaving both the original and replacement event as completed siblings.

### 5.10 Suspend / Rebound / delayed-state stress

The registry may specify the counters, delayed triggers, timing windows, and later permission/event templates required by the rules. The actual changing counter values and live game-state satisfaction are runtime/state concerns.

## 6. Structured constructs adjacent to the registry

The same consequence-record shape may be useful for rules-defined constructs outside 702 keyword abilities — for example keyword actions, Saga/chapter machinery, linked abilities, and other syntactically recognizable rules structures — but `term_kind` must remain explicit.

This closeout does **not** declare all such constructs one giant keyword category, and it does not implement them.

## 7. S16B anti-overderivation invariants

A future registry consumer MUST NOT:

1. promote a keyword name directly into a public semantic family;
2. emit a consequence that depends on game state as though it already occurred;
3. discard optionality, eligibility, timing, participant, or replacement lineage;
4. infer likely strategic outcomes such as combat damage or card advantage from a mechanical keyword template;
5. treat ability words as fixed rules-semantic macros;
6. count generated objects or spell copies as card-origin resources merely because a keyword produced them;
7. collapse Library Traversal into Sample Selection;
8. import a later linked ability's permission into the keyword that merely established the linked object.

## 8. Ownership boundary

S16B owns the **design requirement** that rules-compressed constructs expand to typed lower-mechanical consequences before shallow family/facet projection.

S16B does not own production parsing, persistence, state evaluation, or compiler execution. Those future implementation concerns depend on authorized S16A/AQ4/compiler work and must preserve the already-measured parser ownership boundaries.

## 9. Gate verdict

`REGISTRY_DESIGN_SUFFICIENT_FOR_S16B_FREEZE`

Meaning:

- the semantic design requirement is sufficiently specified for an S16B freeze review;
- a physical production registry is **not** required to exist before S16B semantic freeze;
- implementation/population remains a downstream dependency;
- the gate does not authorize that downstream work;
- this token does not itself freeze S16B.

S16B remains **NOT FROZEN**.