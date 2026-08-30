# BEHAVIORAL REIMPLEMENTATION STRATEGY

Status: **CAPTAIN-DIRECTED REFOUNDATION METHOD**  
Recorded: **2026-08-30**  
Repository: `MTJawnny/mtjawnny-pipeline`  
Captain-direction capture: `issue:1#issuecomment-5471882570`  
C8.5D evidence: `issue:1#issuecomment-5471856911`  
Manager review: `issue:1#issuecomment-5471880506`

> **Preserve truth and behavior worth keeping. Do not preserve accidental architecture merely because it is executable.**

This document changes the reconstruction method, not Foundry semantic law.

The refoundation does **not** aim to take every Python file currently under `experiments/`, repair its imports, and reproduce it one-for-one under `src/mtj_foundry/`.

The permanent system should be designed from explicit contracts, authoritative inputs, accepted behavior, tests, evidence, and product requirements. Legacy code is an important source of those things, but its module boundaries and dependency graph are not themselves the target architecture.

The governing principle remains:

> **PRESERVE TRUTH, NOT PLUMBING.**

The implementation corollary is:

> **Treat legacy code as evidence and, where valid, as an executable behavior oracle. Rebuild the permanent system from contracts.**

---

# 1. Why this strategy exists

The first stages of the refoundation had to be conservative.

Before making large structural decisions, the project needed to know:

- which bytes and records were authoritative;
- which local-only inputs would otherwise disappear;
- which gates were pure versus mutating;
- which path assumptions were real;
- which historical measurements were wrong;
- which package boundaries were missing;
- which semantic/governance facts could not move silently;
- which legacy tools were one-shot migration machinery rather than permanent product code.

That excavation has substantial value. It has also exposed a risk in the word **migration**.

A migration can mean either:

1. **preserve the valuable behavior while changing its representation**, or
2. **reproduce the old implementation shape in a new directory**.

Only the first is a project goal.

If the second became the default, the refoundation could end with a technically packaged version of the historical system while retaining its accidental module boundaries, mixed script/library roles, upward dependencies, CWD assumptions, deferred import cycles, and research-era organization.

That would preserve plumbing rather than truth.

---

# 2. The target is not a packaged copy of `experiments/`

The anti-target is:

```text
experiments/foo.py      -> src/mtj_foundry/foo.py
experiments/bar.py      -> src/mtj_foundry/bar.py
experiments/baz.py      -> src/mtj_foundry/baz.py
```

with essentially the same responsibilities and dependency graph.

That may be the correct treatment for a few small clean modules. It is not the default architecture.

The desired shape is:

```text
legacy implementation
      |
      +--> authoritative inputs
      +--> accepted behavior
      +--> edge cases
      +--> failure modes
      +--> fixtures
      +--> provenance
      +--> useful algorithms
      |
      v
explicit subsystem contract
      |
      v
clean permanent implementation
      |
      +--> differential/conservation proof
      +--> permanent tests
      +--> explicit public API
      +--> explicit side-effect boundary
      |
      v
legacy implementation retired when its unique value is accounted for
```

The old system is therefore a **source** for reconstruction, not a template that the permanent tree must imitate.

---

# 3. Four permitted subsystem dispositions

Every meaningful legacy subsystem or coherent behavior cluster must eventually receive one of four implementation dispositions.

These are distinct from the broader knowledge/artifact dispositions such as KEEP/EVIDENCE/REWRITE/EXTRACT/DERIVE/DELETE. They answer a narrower question:

> **What should happen to this legacy executable behavior while building the permanent Python system?**

## 3.1 MOVE_ADAPT

Use when the existing implementation is already close to a good permanent boundary.

Typical conditions:

- responsibility is narrow and coherent;
- local dependency direction already fits the permanent layering;
- implementation is understandable without large historical context;
- behavior is well tested;
- little or no script-only bootstrap logic is embedded in the library;
- little or no generated-output/history/probe logic is mixed into the component;
- moving it does not preserve a known architectural defect;
- a clean rewrite would mostly reproduce the same code.

MOVE_ADAPT can include:

- namespace changes;
- import cleanup;
- dependency injection;
- type/interface cleanup;
- removal of temporary compatibility wrappers;
- small extraction of CLI shell from library behavior.

MOVE_ADAPT does **not** mean blind copy.

The resulting module still has to satisfy the permanent package architecture.

---

## 3.2 CLEAN_REIMPLEMENT_FROM_CONTRACT

Use when the behavior is valuable but the current implementation shape is not.

Typical signals:

- script and library responsibilities are mixed;
- module is large because years of experiments accumulated inside it;
- module-level imports point upward through the architecture;
- behavior participates in import cycles;
- path/CWD assumptions are entangled with logic;
- one file contains multiple conceptual services;
- one service is spread across unrelated historical files;
- deprecated experiment code surrounds a small production-relevant core;
- the module depends on broad compatibility shims only to reach a few simple capabilities;
- known bugs or obsolete workflows would be preserved by a mechanical move;
- the permanent API should be materially different from the legacy API.

The replacement must be implemented from a written behavior contract and protected by differential/conservation tests.

The legacy implementation remains available during the comparison period, but it does not dictate the new internal structure.

---

## 3.3 EXTRACT_EVIDENCE

Use when the code's lasting value is primarily historical, forensic, research, migration, or provenance value rather than ongoing runtime behavior.

Examples include:

- completed schema migration scripts;
- one-time repair/verifier pairs;
- probes created to answer a historical research question;
- abandoned experiments whose conclusions remain relevant but whose executable path is not part of the product;
- scripts whose unique value has already become a decision/evidence record;
- tools used to establish a ratified invariant but no longer needed once a permanent test implements that invariant.

The required work is not to beautify the code.

It is to identify and preserve its unique systematic value in the appropriate durable form:

- evidence record;
- fixture;
- incident record;
- decision provenance;
- permanent regression test;
- archived source if executable detail still matters.

After that accounting, the executable legacy code may leave the active runtime tree.

---

## 3.4 DELETE_AFTER_ACCOUNTING

Use when no unique systematic value remains.

Deletion is allowed only after proving that the file/component contributes no unpreserved:

- current runtime behavior;
- authoritative input;
- accepted semantic/governance meaning;
- test/negative-control coverage;
- unique fixture;
- reproducibility evidence;
- incident explanation;
- migration provenance;
- useful research result.

The standard is not "old" or "unused recently."

The standard is:

> **its unique value has been accounted for elsewhere or is intentionally abandoned.**

---

# 4. Legacy behavior is evidence, not automatic law

A critical rule:

> **Differential equality against legacy behavior is a conservation technique, not a declaration that every legacy behavior is correct.**

The repository already contains examples of historical behavior that was later measured to be wrong:

- false-positive registry classification;
- incorrect path/layout censuses;
- probes whose shape tests misidentified behavior;
- ratchet-direction or nested-key defects;
- incomplete semantic extraction;
- CWD-sensitive path assumptions;
- documented historical product disconnects.

Therefore every legacy behavior used as an oracle must first be classified.

## 4.1 Oracle classes

### ACCEPTED_BEHAVIOR

Behavior already selected by law, contract, accepted test, explicit decision, or strong conservation requirement.

New implementation should match unless separately authorized to change.

### REPRESENTATIVE_BEHAVIOR

Behavior observed in the legacy implementation and useful as a compatibility baseline, but not independently authoritative.

Divergence requires explanation, not automatic rejection.

### KNOWN_DEFECT

Behavior known to be wrong.

The replacement **must not** reproduce it merely to make a differential test green.

The differential harness should mark the case as an expected legacy failure and require the new implementation to satisfy the corrected contract.

### OBSOLETE_WORKFLOW

Behavior that belonged to a historical process no longer part of the target system.

Do not reproduce it without a new reason.

### UNRESOLVED

Behavior whose status is unclear.

Unexplained divergence is a STOP condition until evidence or authority resolves it.

---

# 5. The unit of reconstruction is the behavior contract, not the old file

A legacy file is a storage accident unless evidence shows that its boundary is itself valuable.

The unit of permanent reconstruction should be a **coherent capability**.

Examples of capabilities:

- repository path resolution;
- corpus loading;
- name normalization/indexing;
- raw-face extraction;
- codebook access;
- authority selection;
- locality addressing;
- semantic extraction;
- gate evaluation;
- report generation;
- search/similarity ranking;
- CLI orchestration.

One legacy file may contain several capabilities.

One capability may be spread across several legacy files.

The contract should define the capability independently of either fact.

---

# 6. Required contract before clean reimplementation

A CLEAN_REIMPLEMENT_FROM_CONTRACT task must not begin from a prompt like:

> rewrite `foo.py` cleanly.

It should begin from a contract containing, as applicable:

## 6.1 Purpose

What capability exists and why the permanent system needs it.

## 6.2 Inputs

Exact input types and sources, including authority/selector status where relevant.

Examples:

- card records;
- pinned Comprehensive Rules edition;
- selected codebook snapshot;
- config source;
- explicit paths from `ProjectPaths`;
- caller-provided records rather than implicit global state.

## 6.3 Outputs

Exact return/value/artifact interface.

Where bytes are contracted, say so.

Where only semantic equality is contracted, do **not** accidentally ratchet formatting or incidental ordering.

## 6.4 Errors and halt behavior

Which states are fatal, recoverable, empty, skipped, or known debt.

A rewrite that converts halt-loudly behavior into silent empty output is not a successful rewrite.

## 6.5 Determinism

What must be deterministic and under which fixed inputs.

## 6.6 Side effects

What may read, write, mutate, print, call network/subprocesses, or alter process state.

Prefer pure library behavior plus explicit orchestration shells.

## 6.7 Authority semantics

If the component consumes semantic/governance truth, identify the selector/decision record that determines what is binding.

Never infer authority from file location during a rewrite.

## 6.8 Known defects not to preserve

Name them explicitly.

## 6.9 Historical behavior retained only for compatibility

If a questionable behavior must temporarily remain because consumers rely on it, state that it is a compatibility constraint rather than a permanent design virtue.

## 6.10 Consumer expectations

List the real callers and which parts of the interface they use.

Do not preserve a giant public surface because the legacy module happened to export it.

---

# 7. Differential reconstruction protocol

Clean reimplementation should normally use a legacy/new comparison harness during coexistence.

The harness must compare the dimensions that matter to the contract.

## 7.1 Freeze the comparison environment

Record:

- exact legacy commit/ref;
- exact authoritative selectors/input hashes where required;
- exact fixtures;
- relevant environment/execution mode;
- any local-only inputs intentionally used;
- expected side effects.

## 7.2 Build representative fixtures

Include:

- ordinary cases;
- known edge cases;
- prior incident cases;
- negative controls;
- malformed/absent inputs where the contract defines behavior;
- multi-face/MTG-specific corner cases where relevant;
- cases specifically known to have broken older probes or implementations.

Do not rely only on random samples.

## 7.3 Run legacy and new implementation independently

Avoid a comparison where both paths share the same buggy helper for the property being tested.

If both sides use one shared implementation, equality proves little.

## 7.4 Compare at the correct equivalence level

Possible levels:

### BYTE_EXACT

Use only where exact bytes are part of authority or external contract.

Examples may include selected immutable artifacts or explicitly contracted output.

### VALUE_EXACT

Same structured values, paths, selected identifiers, ordering where ordering is meaningful.

### SEMANTIC_EQUIVALENT

Different internal or serialized representation but same defined meaning.

### INTENTIONAL_DIVERGENCE

Difference is authorized and explained.

### LEGACY_DEFECT_CORRECTED

Difference is required because legacy behavior is a known defect.

The harness must not collapse these into one boolean.

## 7.5 Every divergence gets a disposition

For each difference:

- legacy is correct -> fix new implementation;
- new behavior is an authorized correction -> record the decision/evidence;
- both are valid representations -> compare semantically instead of bytewise;
- test/oracle is wrong -> repair the test and keep a negative control demonstrating the prior defect;
- unclear -> STOP.

## 7.6 Cut over callers only after the differential boundary is green

The first production cutover should be small and reversible.

## 7.7 Retire the oracle only after permanent coverage exists

Once callers use the new implementation, the legacy implementation may remain temporarily for differential verification.

Retirement requires that its unique test/evidence value has been transferred or consciously retained elsewhere.

---

# 8. Conservation requirements for a reimplementation

A reimplementation must preserve the right things, not every thing.

The conservation plan should classify each relevant property as:

- **MUST_MATCH_EXACTLY**;
- **MUST_MATCH_SEMANTICALLY**;
- **MAY_CHANGE_WITH_EXPLICIT_DECISION**;
- **MUST_CHANGE_BECAUSE_LEGACY_DEFECT**;
- **OUT_OF_SCOPE_HISTORICAL_BEHAVIOR**.

For Foundry this can include:

- selected codebook identity;
- codebook bytes/size where authority law requires exactness;
- card population identity;
- semantic memberships/assertions;
- routing relation;
- CR interpretation contract;
- gate verdict classes;
- known-debt fingerprints;
- output paths;
- stdout/stderr for legacy CLI compatibility;
- ordering;
- determinism;
- no-write guarantees;
- exit behavior;
- side-effect boundaries.

The existing conservation harness should increasingly be used as the comparison envelope rather than embedding conservation logic into each replacement task ad hoc.

---

# 9. Negative controls are mandatory at the contract boundary

A green differential comparison can be meaningless if the comparison does not actually observe the behavior being replaced.

Each replacement needs at least one mutation/negative control proving the harness turns red when the defining contract property is violated.

Examples:

- wrong path while provider ownership remains structurally valid;
- omitted card face;
- changed authority selector;
- reversed ordering;
- dropped semantic assertion;
- silent empty result instead of fatal missing input;
- old known-defect behavior deliberately reintroduced;
- nondeterministic iteration introduced;
- unintended write side effect added.

The project's repeated experience with mis-aimed probes makes this non-optional.

---

# 10. Choosing MOVE_ADAPT versus CLEAN_REIMPLEMENT

Use a written rubric rather than intuition alone.

Score evidence in these dimensions.

## 10.1 Boundary quality

Questions:

- Does the module represent one coherent capability?
- Would we draw roughly this same API if no legacy file existed?
- Are its imports already downward and acyclic?

Strong yes -> MOVE_ADAPT becomes more attractive.

Strong no -> CLEAN_REIMPLEMENT becomes more attractive.

## 10.2 Incidental infrastructure coupling

Questions:

- Does logic depend on `sys.path` manipulation?
- Does it derive repository paths locally?
- Does it depend on current working directory?
- Does import trigger expensive engine initialization?
- Does it mix reads/writes with computation?

More coupling -> CLEAN_REIMPLEMENT.

## 10.3 Historical sediment

Questions:

- How much of the file exists for old experiments, diagnostics, migrations, or reports?
- Does the active behavior use only a small fraction of the file?
- Is the useful algorithm obscured by years of amendments?

More sediment -> CLEAN_REIMPLEMENT or EXTRACT_EVIDENCE.

## 10.4 Behavioral confidence

Questions:

- Do we know what behavior is intentional?
- Are representative fixtures available?
- Are there accepted tests and negative controls?
- Can we compare legacy and new deterministically?

High confidence permits reimplementation safely.

Low confidence may justify temporary MOVE_ADAPT while contracts are extracted—but low confidence is not a reason to canonize bad architecture forever.

## 10.5 Consumer surface

Questions:

- How many consumers exist?
- Which exported names do they actually use?
- Can a narrow facade support them while internals are rebuilt?

High fan-in favors a compatibility facade around a clean replacement rather than copying a giant legacy API wholesale.

---

# 11. C8.5D as a concrete example

C8.5D is evidence for this method, not a final subsystem ruling.

At accepted head `aa003340f40acba6b13bcb5cb40a384a60de1c1f`, Worker measured:

- 93 legacy production modules in the dependency study scope;
- `foundry_common` fan-in 76;
- `foundry_codebook` fan-in 26;
- `foundry_shape_extractor` fan-in 15;
- `tier_engine` fan-in 12;
- `foundry_audit_baseline` fan-in 8 and zero local imports;
- four pre-existing dependency cycles;
- only one legacy module importing `mtj_foundry`: `foundry_common`;
- 32 remaining Step-5-owned local consumption sites;
- 23 Step-6 knowledge-owned sites;
- 5 Step-8 extract/delete sites.

These are **measurements at one head, not permanent ratchets**.

The Manager independently verified the structural core of the finding:

- `foundry_audit_baseline.py` imports only `json` and `pathlib` and independently constructs the tracked baseline path;
- `foundry_common.py` contains the temporary `src` bootstrap and imports `mtj_foundry.paths.ProjectPaths`;
- the root repository has a `src/mtj_foundry` package but no top-level `mtj_foundry` directory;
- `.gitignore` already covers `.venv/` and `*.egg-info/`;
- `foundry_common` still imports `tier_engine` for corpus/name/face helpers;
- `tier_engine.CARDS_PATH` is a CWD-relative `Path("data/raw/oracle-cards.jsonl.gz")`.

Worker further measured that the notorious `foundry_common -> tier_engine` dependency uses only a small corpus-access surface:

- `load_cards`;
- `CARDS_PATH`;
- `build_name_index`;
- `normalize_name`;
- `get_raw_faces`.

That is important architectural evidence.

It suggests that the permanent system may eventually want a clean corpus service rather than a mechanically migrated 8,000+ line engine dependency.

But it also exposes a behavior trap: changing CWD-relative `CARDS_PATH` to a repository-owned path changes behavior unless explicitly authorized.

Therefore C8.5D correctly selected **PACKAGE_IMPORT_EXECUTION_CONTRACT** as the next cut before attempting either direct migration or clean corpus reimplementation.

The package foundation is shared enabling infrastructure for both reconstruction methods.

---

# 12. Immediate sequencing consequence

The reconstruction sequence is refined as follows.

## 12.1 Establish package execution/import contract

The package must be importable in an explicit supported environment without relying on arbitrary legacy traversal.

This does **not** yet delete compatibility bootstraps.

This does **not** migrate dependencies.

This does **not** imply every legacy module will later import the package directly.

It establishes a stable execution foundation for new permanent code.

## 12.2 Do not automatically migrate the next leaf after that

After the package contract lands, the Manager should not mechanically issue:

> move `foundry_audit_baseline.py` into `src/mtj_foundry`.

Instead, use it as the first candidate for a **subsystem disposition review**.

Ask:

- Is the existing baseline module already a good permanent boundary?
- Is its current API appropriate?
- Is the path behavior the only architectural defect?
- Should it MOVE_ADAPT nearly intact?
- Or should a new ratchet/baseline service be implemented from its behavioral contract?

The answer must come from evidence, not from the file being a leaf.

## 12.3 Apply the same rule upward

For larger components, especially those with historical coupling, the burden increasingly shifts toward clean reimplementation.

The permanent architecture should emerge capability-by-capability, not filename-by-filename.

---

# 13. Compatibility facades are allowed, but temporary

A high-fan-in legacy API may need a compatibility facade during reconstruction.

That facade can:

- preserve legacy function names;
- preserve old return shapes;
- route old callers into new implementation;
- provide deprecation telemetry/tests;
- make differential comparison easier.

It must not become the permanent internal architecture by inertia.

A compatibility layer should declare:

- why it exists;
- which consumers remain;
- what condition allows deletion;
- whether it preserves a behavior intentionally or only temporarily.

This is the same discipline already applied to layout bootstraps.

---

# 14. CLI behavior and library behavior must be separated

Legacy scripts frequently combine:

- argument parsing;
- repository discovery;
- data loading;
- computation;
- validation;
- report printing;
- artifact writing.

A clean replacement should normally split:

```text
library capability
    -> explicit inputs
    -> structured result

CLI/orchestrator
    -> resolve environment/paths
    -> call library
    -> print/write intentionally
```

Differential testing may initially compare the complete CLI surface while permanent unit tests target the library contract underneath it.

This lets the project preserve useful operator behavior without preserving script-shaped architecture.

---

# 15. Research code is not production code merely because it still runs

The Foundry repository grew through a large research program.

Many executable files exist because they answered questions such as:

- what does the corpus contain?
- how many rows match a family?
- did a semantic pattern regress?
- can a migration be verified?
- what did one architecture experiment show?

The fact that such a tool is valid Python does not mean it belongs in the permanent runtime package.

During subsystem disposition, distinguish:

- **production capability**;
- **standing verification capability**;
- **research/evidence tool**;
- **historical migration tool**;
- **obsolete experiment**.

Only the first two presumptively belong in active permanent code.

The others need evidence accounting, not automatic packaging.

---

# 16. How this interacts with the knowledge migration

Knowledge migration and code reconstruction are connected but separate.

A code rewrite must not use document location as a shortcut for authority.

Likewise, knowledge migration must not classify a document as current merely because new code still references it.

The selector/decision-record model remains authoritative.

When a clean reimplementation needs semantic or governance inputs:

1. resolve the selected authority;
2. define the input contract;
3. preserve provenance;
4. test the new implementation against that selected input;
5. avoid embedding historical prose/file paths as new architectural dependencies.

This supports the later LLM-native knowledge architecture because agents can retrieve the contract and authority directly instead of reverse-engineering an old script's imports.

---

# 17. How this interacts with the LLM-native repository architecture

The behavioral-reimplementation strategy and LLM-native architecture reinforce each other.

The permanent repository should eventually expose, per subsystem:

- architecture description;
- public API contract;
- selected authority/decision records;
- behavioral fixtures;
- known defects/history only when relevant;
- validation command;
- active plan;
- appropriate path-scoped rules/Skill.

Then an agent implementing or repairing a subsystem can load the small relevant context rather than the full historical Foundry story.

A future Skill might say, conceptually:

```text
foundry-corpus
  canonical contract: knowledge/architecture/corpus.md
  implementation: src/mtj_foundry/corpus/
  legacy oracle: experiments/tier_engine.py (specific functions only)
  fixtures: tests/fixtures/corpus/
  validation: python -m ...
  known intentional divergences: decision records X/Y
```

That is far more efficient and safer than telling an agent to study all 8,000 lines of `tier_engine.py` before touching corpus loading.

---

# 18. Retirement standard

A legacy component can be retired only when all applicable arms are satisfied.

## 18.1 Runtime arm

No current production/standing validation caller depends on the legacy implementation, or remaining compatibility callers are explicitly accounted for.

## 18.2 Behavior arm

Accepted behavior is covered by permanent tests/contracts or intentionally changed by authority.

## 18.3 Evidence arm

Unique research/provenance/incident value is preserved where still systematic.

## 18.4 Authority arm

No semantic/governance authority is lost or silently reinterpreted.

## 18.5 Negative-control arm

Permanent validation demonstrates that meaningful regressions are detectable.

## 18.6 History arm

Git history is sufficient for implementation archaeology once active unique evidence has been extracted.

Only then is DELETE/EXTRACT a refoundation completion rather than data loss.

---

# 19. Avoid two opposite failure modes

## Failure mode A — archaeology forever

Symptoms:

- every tiny legacy quirk receives a permanent compatibility abstraction;
- tasks spend more effort proving import/path identity than building the final system;
- `experiments/` stays effectively permanent because removal always seems one step later;
- the package becomes a wrapper around the old tree.

Correction:

- identify behavior contract;
- reimplement cleanly;
- compare;
- cut over;
- retire.

## Failure mode B — greenfield amnesia

Symptoms:

- rewrite begins from a prose summary of what the old system "basically did";
- semantic edge cases disappear;
- old incidents are repeated;
- authority selection gets replaced with convenient local files;
- behavior differences are discovered only after product integration.

Correction:

- preserve exact evidence;
- use differential harnesses;
- classify legacy oracle status;
- require negative controls;
- STOP on unexplained divergence.

The strategy is intentionally between these extremes.

---

# 20. Task-contract implications

Future implementation tasks should increasingly state the subsystem disposition explicitly.

Example fields:

```yaml
reconstruction_method: CLEAN_REIMPLEMENT_FROM_CONTRACT
legacy_oracle:
  ref: <exact commit>
  surfaces:
    - function_a
    - function_b
contract:
  inputs: ...
  outputs: ...
  errors: ...
  side_effects: ...
known_defects_not_to_preserve:
  - ...
equivalence:
  - property: ...
    level: VALUE_EXACT
intentional_divergences:
  - decision: ...
negative_controls:
  - ...
retirement_condition:
  - ...
```

For MOVE_ADAPT:

```yaml
reconstruction_method: MOVE_ADAPT
why_boundary_is_retained: ...
behavior_change_authorized: false
```

For EXTRACT_EVIDENCE:

```yaml
reconstruction_method: EXTRACT_EVIDENCE
unique_value:
  - ...
preserved_as:
  - ...
runtime_retirement: ...
```

This makes the reconstruction method reviewable rather than implicit.

---

# 21. Full reconstruction audit must test the new architecture, not legacy resemblance

The eventual reconstruction acceptance audit should not ask:

> Did every old module find a new home?

It should ask:

- Are required Foundry capabilities present?
- Are authoritative semantic/governance truths preserved?
- Are package boundaries coherent and acyclic?
- Does each permanent subsystem have an explicit contract?
- Are known legacy defects excluded rather than reproduced?
- Are important old behaviors covered by differential/permanent tests?
- Are remaining legacy components explicitly classified?
- Can unused historical code be removed without losing systematic value?
- Are product-facing outputs correct?
- Can a fresh agent understand and modify the permanent subsystem without reading the historical implementation chain?

A small amount of explicitly retained legacy evidence is acceptable.

A large permanent compatibility dependency on `experiments/` is not the desired endpoint.

---

# 22. Relationship to C8 phases

The original C8 ordering remains useful as a safety sequence, but **Step 5 must not be interpreted as "move every legacy Python module into the package."**

Refined meaning:

### C8 Step 5 — establish permanent code/execution substrate and reconstruct executable capabilities

This may include:

- package import/execution contract;
- permanent low-level services;
- clean reimplementations;
- selected MOVE_ADAPT operations;
- compatibility facades;
- import-boundary enforcement;
- retirement of temporary bootstraps when earned.

### C8 Step 6 — knowledge migration

Still deferred until contamination risks are controlled, but now must implement the LLM-native progressive-disclosure target rather than the earlier bespoke routing model.

### C8 Step 7 — AQ4 physical isolation

Still requires frozen-state conservation and remains separately governed.

### C8 Step 8 — EXTRACT/DELETE

Now receives cleaner inputs because Step 5 explicitly identifies executable components whose runtime value has already been replaced or whose lasting value is evidence only.

---

# 23. What must not be inferred from this direction

This direction does **not** mean:

- rewrite everything immediately;
- discard legacy tests;
- trust a new implementation because it looks cleaner;
- use legacy behavior as semantic authority;
- reproduce known defects for compatibility without a decision;
- delete `experiments/` before evidence accounting;
- unpause AQ4;
- change codebook authority;
- change the Comprehensive Rules interpretation contract;
- weaken conservation gates;
- stop using exact-base bounded tasks during the refoundation;
- merge the architecture sidecar into an active Worker branch casually.

It changes the **default reconstruction objective**:

> from moving implementation units to reconstructing capabilities.

---

# 24. Permanent principle

The repository should remember these two statements together:

> **Legacy code is not garbage. It contains hard-earned behavior, evidence, edge cases, and history.**

and

> **Legacy code is not architecture law. Once its truth is captured, the permanent system is free to be better designed.**

That is the intended meaning of:

> **PRESERVE TRUTH, NOT PLUMBING.**
