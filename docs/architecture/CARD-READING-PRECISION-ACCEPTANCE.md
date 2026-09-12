# Card-Reading Precision Acceptance Architecture

Status: **PARKED / NON-EXECUTING**  
Candidate phase: **S16A**  
Follow-on consumer: **S16B — gameplay-DNA thesaurus**  
Captain direction: `CAPTAIN-CARD-READING-PRECISION-20260911`  
Issue #1 durable record: comment `5642308591`  
Accepted repository state observed when this direction was captured: `9f92039eb9c7132a351576c31472eb30a2957a67`  
Migration S10–S15: **UNCHANGED**

## 1. Purpose

Before Foundry is allowed to infer card similarity by gameplay function, it must prove that it can read and represent a Magic card **precisely enough that no relevant gameplay relationship is lost, invented, flattened, or attached to the wrong instruction**.

The original similarity/thesaurus work was vulnerable whenever a model or parser effectively read a card as one undifferentiated block of text. Complex cards can defeat that approach even when every character is present. Examples include:

- modal spells such as **Cryptic Command**;
- stateful modal cards such as **Zuko, Conflicted**;
- per-turn mode-memory cards such as **Monument to Endurance**;
- cards whose meaning depends on periods, semicolons, colons, bullets, em dashes, parentheses, quotation marks, and other templating punctuation;
- multi-face cards, Sagas, Classes, Rooms, Adventures, split cards, and cards that grant or quote abilities;
- cards where costs, conditions, restrictions, timing, targets, and payloads occupy different syntactic pieces of one ability.

The required end state is stronger than “the whole Oracle text was read.” Foundry must be able to produce a **lossless semantic representation of the card’s executable game instructions**.

## 2. What is already strong

The repository already contains substantial evidence that **information conservation** is much better than in the first iteration.

`refoundation/preservation/captures/2026-08-30-local-research/docs/FULL-CARD-INFORMATION-CONSERVATION-2026-08-13.md` measured the gated corpus and found, among other things:

- no card-text truncation by classifying producers;
- no dropped faces under the shared face reader;
- zero paragraph-count mismatches in the measured corpus;
- negative controls for losing later abilities and whole faces were detected;
- modal and contextual representation remained the important unresolved risk.

`docs/PUNCTUATION-RESCAN-2026-08-06.md` measured punctuation conservation across the then-current ability-line corpus and found:

- zero text-conservation violations;
- zero sentence-reassembly violations;
- zero ability lines producing no delivery solely because of the punctuation rewrite;
- specific known gaps and punctuation-sensitive populations were surfaced rather than silently ignored.

This is important: the historical catastrophic failure class “part of the card was never read” has largely been engineered away.

That is **not** the same as proving semantic understanding.

## 3. The real remaining problem: structure and context

The full-card conservation audit demonstrated two failure classes that are directly dangerous to Searcher B.

### 3.1 Context can be removed while a payload fact survives

A negative control removed the activation cost/context from an ability while leaving its payload text intact. Delivery classification changed, but the object fact remained.

That proves a fact can survive after losing the structural context that owns it.

For a gameplay thesaurus, that is unacceptable. “Destroy a creature” as an activated ability with a sacrifice cost is not semantically interchangeable with “destroy a creature” as an unconditional spell effect, even if the payload phrase is identical.

### 3.2 Mutually exclusive modes can flatten into a card-level bag

The same audit found cards where mutually exclusive modal effects can appear as a bag of facts at card scope. The representation can therefore make:

- “choose one: do A or B”

look too similar to:

- “do A, then do B.”

This is precisely the kind of false composition that would corrupt a similarity engine, a Budget Swapper, or deck-completion logic.

## 4. Current structural foundation

`src/mtj_foundry/mtg/shapes/locality.py` is a strong substrate because it already distinguishes:

- semantic owner versus wider evidence span;
- `(face, paragraph)` coordinates;
- modal header ownership;
- derived modal exclusivity for `Choose one` groups;
- raw and canonical text representations without punctuation stripping in quote resolution.

Its own contract is explicit, however: **locality does not certify correctness**, and it does not perform child-effect decomposition or higher-level semantic-role analysis.

That boundary should be preserved.

## 5. Current parser seam that S16A must explicitly audit

The permanent code currently contains two different reminder-parenthesis strategies.

`src/mtj_foundry/oracle_text.py` has a depth-aware `paren_spans()` scanner that correctly treats nested parentheses as one outer reminder span. Its tests include an adversarial nested-parenthesis witness and explicitly demonstrate why a flat regex is corrupting.

But `src/mtj_foundry/mtg/shapes/delivery.py` still defines a flat reminder regex and `ability_lines()` applies reminder stripping before line decomposition.

This does **not** by itself prove a live corpus misclassification. It does prove that two permanent capabilities do not yet share one canonical structural interpretation of reminder text.

S16A must measure this seam and either:

1. prove the implementations are semantically equivalent for every supported corpus shape, or
2. collapse them onto one authoritative interpretation.

The same standard applies to sentence boundaries, quoted abilities, bullets, em dashes, colons, semicolons, question marks, exclamation points, and any other punctuation class that carries Magic templating structure.

## 6. “Precise understanding” — required representation

A card is not accepted as semantically understood merely because all of its words are recoverable.

At minimum, the canonical representation must preserve the relationships below when they are present.

### 6.1 Structural identity

- card;
- face / component;
- paragraph / printed ability block;
- ability;
- modal group;
- mode;
- sentence;
- clause;
- atomic instruction or effect.

### 6.2 Ability delivery / rules shape

Keep **how an instruction exists** separate from **what it does**:

- spell ability;
- activated ability;
- triggered ability;
- static ability;
- replacement/prevention effect;
- keyword wrapper or granted/quoted ability;
- modal inheritance from a governing header where appropriate.

### 6.3 Costs and payments

Represent costs independently from payloads, including where applicable:

- mana cost;
- additional cost;
- activation cost;
- sacrifice;
- discard;
- life payment;
- tapping/untapping;
- exile-from-zone payment;
- cost reduction or alternate-payment mechanism;
- payment or choice made during resolution rather than as a casting/activation cost.

### 6.4 Conditions, restrictions, and scope

Preserve:

- `if`, `unless`, `only if`, `as long as`, `while`, `during`, `until`, `for as long as`, and similar conditions;
- actor/controller/owner/opponent scope;
- target versus choose versus affect-all distinctions;
- source zone and destination zone;
- temporal restrictions and durations;
- once-per-turn and per-event limits;
- “if you do”, “when you do”, reflexive triggers, and dependent follow-up instructions.

### 6.5 Modal semantics

A modal group must preserve, when present:

- minimum and maximum number of modes selected;
- whether selected modes must be distinct;
- whether the same mode may be selected more than once;
- whether a mode may not be selected again this turn/game/ability instance;
- whether a condition changes the allowed number of selected modes;
- whether the chooser is the controller, opponent, active player, or another actor;
- mode-local targets and shared targets;
- whether different modes are mutually exclusive or may co-occur.

### 6.6 Sequential and dependency semantics

The representation must distinguish:

- independent instructions;
- sequential instructions;
- conditional follow-ups;
- replacement alternatives;
- linked effects;
- instructions that only exist if a prior instruction occurred or succeeded;
- clauses whose target, quantity, or subject is inherited from an earlier clause.

### 6.7 Quantities and cardinality

Preserve exact or symbolic values such as:

- one / two / three / any number / up to N;
- X and other variables;
- “for each” relations;
- fixed versus variable search depth;
- number of cards inspected, chosen, retained, moved, created, destroyed, etc.

### 6.8 Provenance

Every derived semantic fact must remain traceable to the Oracle material that supports it.

A consumer should be able to answer not only:

> What does this card do?

but also:

> Which exact printed instruction caused Foundry to believe that, and what structural context owns that instruction?

## 7. Adversarial seed witnesses

These cards are **seed tests**, not the test suite.

### Cryptic Command

Required semantic properties include:

- one modal spell;
- exactly two distinct modes selected from four;
- each selected mode remains independently identifiable;
- targeting belongs to the selected mode(s), not to the card as an undifferentiated whole;
- the card must not flatten into “counter + bounce + tap + draw all happen.”

### Zuko, Conflicted

Required semantic properties include:

- one governing triggered ability;
- a parent instruction that includes life loss and a modal choice;
- four separately represented outcomes;
- persistent selection memory: a mode that has already been chosen is unavailable under the card’s stated rule;
- no child mode may accidentally inherit another mode’s object, target, or effect;
- movement/control-change instructions in one mode must remain sequenced correctly.

### Monument to Endurance

Required semantic properties include:

- the discard event owns the trigger;
- the triggered ability contains a mode choice;
- modes carry “not previously chosen this turn” state;
- after all available modes have been exhausted under the card’s rule, a later trigger must not be represented as though an arbitrary mode remains available.

## 8. Corpus-wide audit, not a boutique fixture set

S16A should not be considered complete after a handful of famous cards pass.

The corpus should be mined into structural families and adversarial populations, including at least:

- all modal-header templates and all bullet-list variants;
- modal headers whose instructions continue after the selection count;
- “choose one/two/three/one or more/up to N/X” families;
- “same mode more than once” and “hasn’t been chosen” families;
- periods, semicolons, colons, commas, exclamation marks, question marks, ellipses, em dashes, bullets, parentheses, and quotations;
- quoted or granted abilities containing internal punctuation;
- nested reminder text;
- reflexive triggers and linked abilities;
- multi-sentence abilities;
- costs followed by effects containing colons or semicolons;
- Sagas, Classes, Rooms, level/tier structures, Adventures, split cards, MDFCs/DFCs, meld or other multi-component cards represented in the corpus;
- die-roll tables and other bullet-like nonmodal structures;
- ability words and flavor words;
- replacement/prevention text;
- repeated identical phrases in multiple abilities on the same card;
- multiple effects sharing one condition versus effects with separate conditions;
- target-sharing and target-separation cases;
- variable and derived quantities.

The audit must report the population of every recognized family and explicitly list any shape that cannot yet be represented without loss.

## 9. Conservation tests required

S16A should treat semantic parsing as a conservation problem.

At minimum, tests should prove:

1. **Text conservation** — no relevant Oracle material disappears.
2. **Structural conservation** — every face, paragraph, ability, modal group, mode, and atomic instruction remains reachable.
3. **Context conservation** — costs, conditions, restrictions, timing, scope, and ownership cannot be deleted while payload facts remain silently unchanged.
4. **Exclusivity conservation** — mutually exclusive effects cannot become indistinguishable from cumulative effects.
5. **Dependency conservation** — `if you do` / `when you do` / linked and reflexive relationships survive decomposition.
6. **Target conservation** — targets stay attached to the correct instruction or mode.
7. **Cardinality conservation** — exact selection and quantity rules survive decomposition.
8. **Zone conservation** — source and destination zones survive normalization.
9. **Provenance conservation** — every semantic fact can point back to its source text and structural owner.
10. **Round-trip explainability** — the structured form can generate a faithful plain-English explanation of the card’s operative instructions without inventing effects or omitting restrictions.

## 10. Negative controls required

A passing suite must prove that its guards can detect deliberate corruption.

Required negative-control classes include deliberately:

- delete a later ability;
- delete one face;
- delete an activation/casting/additional cost while keeping the payload;
- convert `choose one` into cumulative effects;
- change `choose two` into `choose one`;
- remove “different modes” / “same mode more than once” / “hasn’t been chosen” restrictions;
- move a target from one mode to another;
- move a condition from parent ability to child mode or vice versa;
- split one linked effect into two unrelated effects;
- merge two unrelated effects;
- flatten a mode group into a card-level fact bag;
- mishandle punctuation inside a quoted ability;
- replace the nested-parenthesis reader with a flat regex;
- cross a face boundary with a pattern;
- change a destination zone while preserving the action verb;
- change a resolution payment into a casting/activation cost or vice versa.

A guard that cannot detect its corresponding negative control is not an acceptance guard.

## 11. Relationship to the gameplay-DNA thesaurus

S16A is a prerequisite for, not a replacement for, S16B.

The desired Searcher B asks:

> What cards do the same gameplay job, even when they use different words or rules mechanisms?

That comparison should consume structured semantic facts produced by the card-reading layer.

Example: two cards may both perform top-library card selection into hand, while differing in:

- search depth;
- retained-card count;
- resource or payment mechanism;
- residual-card destination;
- timing;
- restrictions.

Searcher B should compare those semantic coordinates. It should not have to rediscover card grammar from raw Oracle text every time it ranks a neighbor.

Therefore:

**S16A = understand the card precisely.**  
**S16B = compare what those understood instructions accomplish in gameplay.**

## 12. Non-goals

S16A does **not** authorize:

- changing the accepted S10–S15 migration sequence;
- implementing gameplay similarity ranking;
- introducing embeddings as semantic authority;
- collapsing strategy/editorial judgments into Oracle-derived truth;
- adding card-specific hacks merely to make named seed witnesses pass;
- making a model’s free-form interpretation the canonical parser output;
- rewriting existing ratified locality law without separate evidence and authorization.

## 13. Acceptance bar

S16A is complete only when Foundry can take any supported Oracle card record and either:

1. produce a structured semantic parse whose text, structure, context, exclusivity, dependency, cardinality, targeting, zones, and provenance are demonstrably conserved; or
2. explicitly refuse the unsupported shape and identify exactly what could not be represented.

Silent approximation is failure.

The key product invariant is:

> **Before Foundry judges whether two cards share gameplay DNA, it must know exactly what each card says, which instructions belong together, which instructions exclude one another, what conditions and costs govern them, and where every derived fact came from.**

## 14. Execution sequencing

This document is a preserved architecture/acceptance direction only.

- S10–S15 migration work remains first.
- No S16A implementation is authorized by this document.
- After refoundation completion, S16A should begin with a read-only corpus audit and structural-family census before changing parser behavior.
- Only after S16A’s acceptance contract is satisfied should the gameplay-DNA thesaurus become a consumer of the semantic parse.
