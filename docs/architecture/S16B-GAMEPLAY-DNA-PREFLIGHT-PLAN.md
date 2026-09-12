# S16B Gameplay-DNA Thesaurus Preflight Plan

Status: **PLANNED / NON-EXECUTING**  
Objective: **5 of 5**  
Fresh Claude session: **REQUIRED**  
Candidate phase: **S16B**  
Prerequisite: **S16A semantic card-reading acceptance**  
Implementation authorization: **NONE**

## Mission

Prepare the evidence, vocabulary, benchmark, and functional-coordinate design needed for a true MTG gameplay thesaurus: cards that may use different words and different rules mechanisms but materially perform the same gameplay job.

This is explicitly the **S16B preflight**. It may gather and structure external knowledge now, but S16B implementation must not bypass S16A. The functional thesaurus is only as trustworthy as the semantic card representation it consumes.

## Product question

Searcher B is not “what cards contain similar text?” It is:

> What other cards produce materially similar gameplay outcomes or fill the same functional job, even when Oracle wording, costs, zones, timing, or rules mechanisms differ?

Canonical seed relationships include:

- **Grand Abolisher ↔ Defense Grid** — different mechanisms, overlapping gameplay job of constraining opponents’ ability to interact on your turn.
- **Plunge into Darkness ↔ Dig Through Time** — different resource/payment and selection mechanics, overlapping library-selection/card-access job.

Seeds are not enough. The preflight must independently discover many additional relationships and difficult negatives.

## Epistemic separation

The preflight must preserve four different evidence layers:

1. **Literal Oracle/CR fact** — what the card/rules explicitly say.
2. **Normalized mechanical fact** — structured action, object, zone, quantity, timing, cost, restriction, etc.
3. **Derived functional job** — what those mechanics accomplish in play.
4. **Community/strategic role judgment** — how players describe or use that function in decks/metagames.

These layers must not be flattened into one authority status. External community language can enrich functional understanding; it cannot overwrite Oracle/CR truth.

## Research program

The fresh session should treat this as substantial research, not a quick search scrape.

### Source classes

Research should span, where useful:

- official card/rules material for mechanical verification;
- established strategy articles and primers;
- Commander/deckbuilding resources;
- forum and community discussions;
- card-comparison discussions;
- archetype/role discussions;
- decklists and primer explanations that explicitly state why one card substitutes for another;
- historical terminology sources when a community term has stable usage.

Community sources are evidence of vocabulary and strategic judgment, not infallible truth.

### Claim-level provenance

Every external functional claim should record:

- source URL/title/provider;
- publication/update date when available;
- access date;
- source class;
- exact claim paraphrased at claim level;
- card(s)/role(s) implicated;
- confidence/reliability note;
- corroborating or conflicting sources;
- whether the claim is mechanical, functional, strategic, or vocabulary-only;
- cross-check against Oracle/CR/Foundry fact layer.

Do not import unattributed “community consensus.”

## Vocabulary-mining objective

The preflight should discover how players naturally name gameplay jobs and distinguish:

- widely used community terms;
- terms used only within a narrow archetype;
- overloaded terms whose meanings conflict;
- mechanically precise terms;
- useful functional concepts with no stable community label.

Preferred rule:

- use an accurate, stable community term when one exists;
- do not force a popular term if it collapses important mechanical distinctions;
- when no good term exists, the project may coin a concise term, but it must be explicitly marked **PROJECT-AUTHORED**, defined, and linked to supporting mechanical coordinates.

Labels are navigation aids, not evidence substitutes.

## Functional-coordinate hypothesis

The preflight should test and refine a candidate coordinate system including at least:

- gameplay job / role;
- action/effect;
- source zone;
- destination zone;
- search/selection depth;
- quantity retained/moved/created/affected;
- magnitude;
- scope/target class;
- actor/controller/opponent scope;
- timing/delivery;
- duration;
- conditions/restrictions;
- resource/cost mechanism;
- payment timing;
- residual disposition;
- repeatability / once-per-turn or stateful limits;
- modal/choice structure;
- interaction window created or denied;
- dependency on board/deck state;
- further dimensions discovered by evidence.

The preflight should not assume these dimensions are complete. It should report dimensions that recur in researched comparisons and dimensions needed to distinguish false friends.

## Job-parent / mechanism-child model

Preserve the architectural principle:

> **Children are defined by mechanism; parents are defined by job.**

The result is a lattice/DAG, not a single taxonomy tree:

- a card/effect may have multiple functional parents;
- no forced primary parent is required;
- role relevance may depend on deck context;
- mechanism should remain mechanically grounded;
- functional parenthood may be derived downstream from multiple facts and research evidence.

The preflight should test this model against real researched card clusters and identify cases where the parent/child distinction breaks down or needs another relation type.

## Positive-pair discovery

Build a research-derived candidate gold set that includes:

- seed pairs from Captain direction;
- independently discovered pairs from multiple source types;
- pairs with near-identical job but very different mechanism;
- pairs with same mechanism but meaningfully different job;
- pairs whose similarity is strongly deck-context dependent;
- budget/substitution examples;
- role-equivalent effects across card types or zones;
- cases where community explicitly recommends one as an alternative to another.

Do not select only relationships already represented by the current axis/codebook system.

## Hard negatives

A functional benchmark is useless without cards that superficially overlap but should not be ranked as close substitutes.

Mine hard negatives such as:

- same verb, different gameplay job;
- same broad category (“draw”, “removal”, “ramp”) but incompatible timing/scope/resource profile;
- same destination zone but different selection agency;
- similar outcome but radically different deck-context requirement;
- same community label used inconsistently;
- cards sharing an active axis but not a meaningful substitution relationship;
- cards with similar text but opposite strategic purpose.

Each negative should state **why the broad overlap is insufficient**.

## Context-dependence model

The preflight should distinguish:

- context-free mechanical similarity;
- deck-context role similarity;
- commander/color-identity constraints;
- archetype-specific synergy;
- metagame-dependent strategic value;
- budget/substitution equivalence.

S16B’s first implementation may choose a bounded subset, but the preflight should prevent “same gameplay DNA” from becoming an undefined blend of these layers.

## Research reconciliation against Foundry

For each researched pair/cluster:

1. verify the cards’ Oracle facts;
2. identify the normalized mechanical dimensions that plausibly support the claimed job;
3. identify any source claim that contradicts rules or current Oracle text;
4. mark outdated claims;
5. preserve conflicts rather than averaging them away;
6. state which parts of the relationship could be derived from S16A semantic facts and which remain strategic/community judgment.

External research remains downstream from canonical Oracle/CR truth.

## Benchmark design

The preflight should design an acceptance benchmark with at least three outputs:

1. **retrieval** — does the system surface functional neighbors?
2. **ordering** — are closer gameplay substitutes generally above broad-category overlaps?
3. **explanation** — can it explain both shared job and relevant differences using traceable evidence?

Benchmark labels should allow graded relationships rather than forcing every pair into identical/not-identical. However, avoid introducing opaque numeric weights as truth. Any ordinal/graded judgment must have a documented rubric and provenance.

Reserve a holdout set that is not chosen because the current retrieval system already finds it.

## Relationship to existing S9 retrieval

The accepted S9 retrieval is intentionally conservative: shared ACTIVE axis membership generates candidates and ranking is deterministic presentation policy.

The S16B preflight should measure where that substrate succeeds and where it cannot express researched gameplay-DNA relationships. It must not treat S9 misses as automatic evidence that the external claim is correct, nor treat S9 hits as gold truth.

The result should identify the minimum additional semantic/job representation needed beyond shared active-axis overlap.

## Required deliverables

1. **Research methodology and source-reliability rubric**.
2. **Claim-level provenance store/schema**.
3. **Community vocabulary lexicon** with provenance, conflicts, and `COMMUNITY` vs `PROJECT-AUTHORED` status.
4. **Functional-coordinate proposal** revised from real evidence.
5. **Gameplay-job DAG/lattice examples** demonstrating multiple parents and mechanism children.
6. **Positive gold-pair/cluster set**, including independent discoveries.
7. **Hard-negative set** with explicit failure rationale.
8. **Context-dependence classification**.
9. **S9 gap analysis** against the research-derived benchmark.
10. **S16B retrieval/order/explanation acceptance design**.
11. **Holdout/precommitment plan**.
12. **Draft S16B implementation contract**, clearly NOT AUTHORIZED and explicitly gated on S16A acceptance.

Machine-readable pair/claim/vocabulary artifacts should be preferred where they make provenance and later benchmark execution reproducible.

## Research quality requirements

- substantial source breadth;
- multiple independent sources for important non-obvious strategic claims when practical;
- dates and version sensitivity;
- explicit conflicts;
- no folklore laundering;
- no relying on search-result snippets as final evidence;
- no card-specific claim accepted without Oracle/rules cross-check when the claim depends on mechanics;
- no benchmark built only from Captain-provided examples;
- no “top N” or popularity source treated as proof of functional equivalence by itself.

## Non-goals

This preflight must not:

- implement S16B retrieval/ranking;
- modify the codebook or axes to make research pairs fit;
- weaken S16A as a prerequisite;
- make community claims canonical Oracle facts;
- introduce model free-form judgment as an untraceable authority layer;
- choose arbitrary similarity weights;
- begin deck-building/game-theory layers beyond what is needed to classify context dependence;
- alter S10–S15 migration work.

## STOP conditions

STOP or mark unresolved if:

- a claimed relationship cannot be supported beyond one low-quality source;
- sources disagree materially and no principled reconciliation is available;
- a functional term has multiple incompatible meanings and no scoped definition is recorded;
- a pair only appears similar because one source is using outdated Oracle text;
- a proposed coordinate requires semantic facts that S16A cannot yet represent and the dependency is not being acknowledged;
- benchmark labeling starts depending on the output of the system it is meant to evaluate.

## Completion bar

Objective 5 is complete when S16B can later begin with a research-derived, provenance-bearing vocabulary and benchmark that contains independently discovered gameplay-DNA relationships and hard negatives, a tested functional-coordinate model, explicit context boundaries, and a retrieval/explanation acceptance design—while keeping all external strategic knowledge downstream from S16A and canonical Oracle/CR truth.
