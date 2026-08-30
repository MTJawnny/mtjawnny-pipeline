# LLM-NATIVE REPOSITORY ARCHITECTURE

Status: **CAPTAIN-DIRECTED REFOUNDATION TARGET REFINEMENT**  
Recorded: **2026-08-30**  
Repository: `MTJawnny/mtjawnny-pipeline`  
Durable Captain-direction capture: `issue:1#issuecomment-5471746549`

> **Make the repository legible to agents, not resident in their context.**

This document integrates external research on agent-oriented software repositories into the accepted MTJawnny refoundation direction. It is deliberately detailed so future Manager and Worker sessions can build the reconstruction toward the intended end state without having to repeat this research.

It does **not** change Foundry semantic law, codebook authority, AQ4 state, or any active Worker task. It refines the repository/session/knowledge architecture that later reconstruction phases are expected to implement.

The governing project principle remains:

> **PRESERVE TRUTH, NOT PLUMBING.**

The corresponding context-engineering principle is:

> **All necessary project knowledge must be discoverable. Only the minimum universally necessary knowledge should be loaded by default.**

---

## 1. Why this refinement exists

The original P0 clean-slate architecture correctly diagnosed a repository that had accumulated too much state in prose, handoff chains, implicit path conventions, and a very large `CLAUDE.md`. It proposed a low-token cold-start chain:

```text
README.md
  -> knowledge/STATE.md
  -> knowledge/<area>/INDEX.md
  -> exact authority
```

It also proposed shrinking `CLAUDE.md`, making current state/authority machine-readable, retiring transcript-style handoffs, and keeping historical evidence distinct from current law.

Those conclusions remain directionally correct.

The new research changes the **mechanism**, not the objective.

Modern coding-agent systems now provide native mechanisms for:

- concise always-on project instructions;
- path-scoped instructions loaded only for relevant files;
- task-specific Skills loaded on demand;
- isolated subagent contexts for research or verification;
- deterministic hooks and permission rules;
- language-server/code-intelligence navigation;
- durable execution plans and Git-based continuation;
- cross-agent `AGENTS.md` conventions.

At the same time, long-context research and agent engineering practice consistently show that a larger context window is not a reason to preload more project history. Context remains a finite attention resource. Long, mixed-relevance inputs reduce reliable retrieval and adherence.

Therefore the permanent target should not recreate a custom document-routing bureaucracy that every agent must walk mechanically. It should create a **vendor-neutral knowledge substrate with progressive disclosure**, then use whichever agent-native adapters are available to surface only the relevant part of that substrate.

---

# PART I — RESEARCH FINDINGS

## 2. Research question

The practical question was:

> How should a large, long-lived software/research repository be structured so an LLM coding agent can reliably obtain the project information it needs without ingesting the entire project history or depending on prior session memory?

The research intentionally compared several independent classes of evidence:

1. current official Claude Code architecture and extension mechanisms;
2. Anthropic's broader context-engineering and long-horizon-agent guidance;
3. OpenAI's experience operating a large agent-first software repository;
4. GitHub/Copilot and cross-agent instruction conventions;
5. Cursor's independently convergent scoped-rule model;
6. long-context model research;
7. repository-level code retrieval/planning research;
8. software-engineering agent interface research.

The convergence across these sources is more important than any single vendor recommendation.

---

## 3. Finding A — context is a scarce resource even when the window is large

Anthropic's context-engineering guidance treats context as a finite attention budget with diminishing marginal returns. Its recommended target is the smallest high-signal set of tokens that maximizes the chance of correct behavior. It explicitly describes a shift from preloading all possibly relevant information toward **just-in-time context retrieval** using lightweight identifiers such as file paths, stored queries, and links.

This matters directly to MTJawnny because the repository contains several qualitatively different bodies of information:

- current architecture;
- semantic/governance law;
- MTG Comprehensive Rules reference material;
- Foundry evidence and experimental records;
- incident history;
- AQ4 benchmark material;
- old handoffs;
- future research/product concepts;
- implementation code and tests.

A worker editing one path API does not need the complete AQ4 semantic history. A researcher investigating one MTG semantic claim does not need every import-migration trap. Loading both “just in case” is not prudence; it is context pollution.

### Supporting research

`Lost in the Middle` demonstrated that long-context models can perform substantially worse when relevant information is buried within a large input, even when the model nominally supports the context length.

`RULER` expanded evaluation beyond simple needle retrieval and found large performance drops as context length and task complexity increased. Claimed context capacity is therefore not equivalent to reliable usable context.

### Architectural consequence

**Context size is not our retrieval strategy.**

The repository must optimize **signal selection**, not maximize tokens supplied to an agent.

---

## 4. Finding B — large always-on agent manuals are an anti-pattern

Current Claude Code documentation states that project `CLAUDE.md` content is loaded into every session and consumes context alongside the task. Anthropic recommends keeping a `CLAUDE.md` under roughly 200 lines and moving multi-step or subsystem-specific material into path-scoped rules or Skills.

OpenAI independently reports the same failure mode from an agent-first repository that grew to roughly a million lines of code. Its team tried one large `AGENTS.md` and found that it:

- crowded out task/code context;
- diluted important guidance;
- rotted quickly;
- became difficult to verify.

Their replacement was a short `AGENTS.md`, roughly 100 lines, acting as a **table of contents**, with structured repository documentation as the system of record. Their concise formulation is: give the agent a map, not a giant instruction manual.

This precisely matches a known MTJawnny failure mode. The current legacy `CLAUDE.md` contains large amounts of history, changing counts, traps, incidents, and task-specific context. Much of it was earned through real defects, but always loading all of it is not the same as preserving its value.

### Architectural consequence

The permanent always-on instruction surface must be **small, stable, and high-signal**.

Historical traps do not disappear. They move to canonical knowledge and are surfaced conditionally when the affected subsystem or workflow is relevant.

---

## 5. Finding C — progressive disclosure is now a native agent capability

Claude Code provides several context scopes:

- root/project `CLAUDE.md` for standing project instructions;
- nested `CLAUDE.md` files that load when Claude works in the corresponding subtree;
- `.claude/rules/*.md` with `paths` frontmatter for path-scoped instructions;
- Skills under `.claude/skills/<skill>/SKILL.md`, whose body is loaded only when invoked or selected as relevant.

GitHub Copilot exposes a very similar separation:

- repository-wide instructions;
- path-specific instruction files;
- `AGENTS.md` for shared standing agent guidance;
- Skills for task-specific workflows;
- hooks and custom agents for specialized execution.

Cursor independently uses project rules that can be always-on, path-scoped, manually invoked, or relevance-selected.

The precise file names differ. The capability model is the same:

```text
small always-on context
        |
        +--> conditional subsystem rules
        |
        +--> on-demand procedure/domain skills
        |
        +--> repository search / exact documents
```

### Architectural consequence

The project should target the **capability model**, not one vendor's filenames.

Claude-specific files are adapters onto canonical project knowledge. They are not the knowledge itself.

---

## 6. Finding D — canonical project knowledge should live in the repository, not in agent configuration

OpenAI's agent-first repository treats structured repository documentation as the system of record and the short agent instruction file as a map into it. Plans, architecture, product specifications, references, and technical debt are durable repository artifacts.

That strongly validates the P0 knowledge direction, with one correction: the repository knowledge layer should be **vendor-neutral**.

A `.claude/skills/foundry-model/SKILL.md` file should not become the sole home of Foundry architecture. It should describe when the skill is relevant and route Claude to the canonical architecture/decision/evidence files.

Likewise, `AGENTS.md` should not become a second governance ledger.

### Architectural consequence

There must be one canonical knowledge substrate independent of Claude, Codex, Copilot, Cursor, or any future agent product.

Agent-specific configuration may:

- summarize stable rules;
- point to canonical sources;
- select a procedure;
- restrict tools;
- inject exact current context.

It must not mint competing project truth.

---

## 7. Finding E — hard rules belong in deterministic enforcement where possible

Claude's own documentation explicitly distinguishes instructions from enforcement. `CLAUDE.md` is context. Hooks and permission rules provide deterministic control. A `PreToolUse` hook can deny an operation even when a permissive agent mode would otherwise allow it.

SWE-agent research reaches the same conclusion from another direction: agent performance improves when the **Agent-Computer Interface** gives concise feedback and mechanically constrains bad edits—for example, running a linter around edits rather than merely instructing the model to remember syntax rules.

MTJawnny already has a strong culture of negative controls, conservation tests, exact-base checks, and STOP conditions. The new architecture should extend that principle to the agent interface.

### Architectural consequence

Use prose to explain rules requiring judgment. Use deterministic machinery for invariants that must not silently fail.

Examples:

- import-direction restrictions -> import-boundary test/gate;
- generated/source separation -> artifact-class gate;
- stale derived state -> freshness test;
- forbidden AQ4 mutation during pause -> task scope + repository checks/hooks where practical;
- forbidden merge/publish behavior -> permissions/hooks in execution environments where practical;
- required test closure -> completion gate/hook rather than memory alone.

Do not rely on “Claude was told” as the final safety boundary.

---

## 8. Finding F — long-running work needs durable external state, not transcript memory

Anthropic's long-running-agent harness work emphasizes that each new session begins without memory of the prior session. Durable progress artifacts and Git history let a new agent continue without replaying the entire transcript.

OpenAI's agent-first repository makes **execution plans** first-class versioned artifacts with active/completed state, progress, and decision logs.

This supports the existing MTJawnny session-disposability requirement and gives us a cleaner replacement for the handoff chain.

### Architectural consequence

Long-running project work should persist through:

- exact Git state;
- structured decisions;
- active execution plans;
- issue/task contracts;
- compact current state;
- tests/evidence.

Transcript summaries may be useful history but must never be required reconstruction state.

---

## 9. Finding G — isolate high-volume side work from the main implementation context

Claude subagents start with fresh isolated contexts. They are appropriate when a side task is self-contained and would otherwise flood the main context with search results, logs, or large file sets.

This maps naturally onto the future MTJawnny work pattern:

- a research agent can read extensive community/strategy sources and return a claim-level synthesis;
- a verifier can independently inspect a diff and return failures/evidence;
- a broad repository explorer can locate relevant modules without filling the implementation context with every file it inspected.

### Architectural consequence

Use isolated context for **large intermediate information**, then return concise evidence-bearing results to the main task context.

This is not permission to trust subagent claims. The same evidence/authority distinction remains.

---

## 10. Finding H — code intelligence should precede custom repository RAG

Repository-level research such as RepoCoder demonstrates the value of iterative retrieval rather than whole-repository prompting. CodePlan similarly treats repository-level changes as a planning problem over interdependent code rather than a single-context generation problem.

Modern coding agents already provide increasingly strong built-in repository search and language-server integration. Claude Code supports LSP plugins such as Pyright for Python, providing definitions/references and automatic diagnostics.

### Architectural consequence

The default code-discovery stack should be:

1. explicit architecture/package boundaries;
2. language-server/code-intelligence navigation;
3. repository text/AST search;
4. exact canonical docs/Skills;
5. only then custom retrieval infrastructure if measured failure justifies it.

Do **not** build an embedding/vector RAG service merely because the repository is large.

A custom repository RAG system becomes justified only if behavioral evaluation demonstrates repeated failures that normal search, indexes, Skills, and LSP cannot solve efficiently.

---

# PART II — INTEGRATION WITH THE ACCEPTED P0 ARCHITECTURE

## 11. Existing architecture that remains unchanged

This refinement preserves the accepted P0 direction recorded in `refoundation/decisions/P0-ARCHITECTURE.yaml`:

- permanent Python namespace: `mtj_foundry`;
- one permanent repository-layout owner: `mtj_foundry.paths.ProjectPaths`;
- library/CLI separation;
- explicit acyclic package direction enforced mechanically;
- selector/decision-record authority model;
- no frontmatter self-authority;
- pure validation: checks and emitters separated;
- tracked/reviewable acceptance inputs;
- explicit artifact classes;
- machine-readable current state, authority, supersession and routing;
- AQ4 one-way dependency and paused governance state;
- bounded migration with conservation proof first;
- legacy KEEP/EVIDENCE/REWRITE/EXTRACT/DERIVE/DELETE disposition;
- shipped `pipeline/` is not moved for symmetry alone;
- session disposability and GitHub durable control plane.

This document is a **refinement of the session/knowledge/retrieval destination**, not a replacement for the software architecture above.

---

## 12. Earlier P0 ideas that are retained but reinterpreted

### 12.1 `knowledge/STATE.md` — KEEP, but narrow it

The earlier proposal was correct that fresh sessions need an obvious current-state source.

The mistake would be allowing `STATE.md` to become another encyclopedia.

Permanent `STATE` should answer only globally volatile questions that materially affect many tasks, for example:

- active development/refoundation phase;
- currently selected authority identifiers;
- paused/frozen subsystems;
- open Captain decisions;
- active execution-plan identifiers;
- current validation/health summary;
- known repository-wide blockers.

It should **not** restate subsystem architecture, historical rationale, every gate count, or the full issue history.

Prefer machine-readable canonical state with a concise human/agent-readable derived view if both are needed.

### 12.2 `knowledge/INDEX.md` and area indexes — KEEP as discovery aids

Indexes remain useful, particularly for humans, GitHub-only readers, and tool-agnostic agents.

But they are not a mandatory ritual such as:

```text
must read INDEX A -> must read INDEX B -> must read exact doc
```

A Skill, path-scoped rule, repository search, or direct known path may jump straight to the exact authority.

Indexes should describe available knowledge, not impose unnecessary traversal.

### 12.3 `README.md` — KEEP as human/project router, not mandatory first agent hop

The root README should explain the project to people and point to architecture, setup, and product documentation.

Agents may use it, but a dedicated standing agent map is a cleaner machine entry point.

### 12.4 Generated/tracked state indexes — KEEP only under freshness enforcement

The P0 correction already allows `DERIVED_VIEW` as an explicit artifact class. A generated, tracked state/index view is acceptable when GitHub-only readability is a live requirement and a freshness gate makes staleness mechanically visible.

### 12.5 Handoff retirement — STRENGTHEN

Handoff chains should not merely become “less important.” They should cease to be required routing state once active plans/current state are operational.

Historical handoffs may be EVIDENCE or HISTORY when they contain unique provenance, then EXTRACT/DELETE according to the disposition process once their unique systematic value is accounted for.

---

## 13. Earlier P0 idea that is superseded as a primary invariant: `<=4 reads to authority`

The earlier clean-slate proposal suggested that any task should reach authority in no more than four reads.

This was a useful attempt to make navigability measurable, but it measures a proxy.

Five tiny and exact reads can be better than three large mixed-purpose reads. A Skill can inject the right procedure without one of those reads being visible as a filesystem hop. LSP/search can also bypass a fixed document chain.

### Replacement acceptance question

> Can a fresh authorized agent reliably locate the correct current authority and required context, while avoiding superseded/irrelevant material, with a reasonable context budget and without prior-session memory?

Read count remains a **diagnostic**. It is not the governing law.

---

# PART III — PERMANENT TARGET ARCHITECTURE

## 14. Two-layer design: canonical substrate + replaceable agent adapters

The most important design distinction is:

```text
                     PROJECT TRUTH
                         |
            +------------+-------------+
            |                          |
   canonical repository          executable system
   knowledge/state/plans         code/config/tests
            |                          |
            +------------+-------------+
                         |
                 thin agent adapters
               /        |        \
          Claude      Codex    Copilot/other
```

The bottom layer is durable project architecture.

The top adapter layer is intentionally replaceable.

If Claude Code changes how Skills work in 2027, we should replace the Claude adapter—not rewrite Foundry law.

---

## 15. Target repository shape for agent legibility

The exact final paths may be adjusted during reconstruction, but the capability layout should converge on something like:

```text
mtjawnny-pipeline/
|
|-- README.md
|-- ARCHITECTURE.md
|-- AGENTS.md
|-- CLAUDE.md
|-- pyproject.toml
|
|-- .claude/
|   |-- settings.json
|   |-- rules/
|   |   |-- architecture.md
|   |   |-- tests.md
|   |   |-- knowledge.md
|   |   `-- generated-output.md
|   |-- skills/
|   |   |-- foundry-model/
|   |   |   `-- SKILL.md
|   |   |-- mtg-rules/
|   |   |   `-- SKILL.md
|   |   |-- authority-conservation/
|   |   |   `-- SKILL.md
|   |   |-- research-evidence/
|   |   |   `-- SKILL.md
|   |   `-- repository-verification/
|   |       `-- SKILL.md
|   `-- agents/
|       |-- researcher.md
|       `-- verifier.md
|
|-- knowledge/
|   |-- STATE.md                 # concise derived current-state view if retained
|   |-- INDEX.md                 # discovery, not authority
|   |-- law/
|   |-- decisions/
|   |-- evidence/
|   |-- incidents/
|   |-- reference/
|   `-- history/
|
|-- plans/
|   |-- active/
|   |-- completed/
|   `-- debt/
|
|-- config/
|-- src/mtj_foundry/
|-- tests/
|-- benchmarks/                  # AQ4 eventually isolated here or equivalent
|-- pipeline/                    # stays unless separately justified
`-- var/                         # according to final artifact census/classification
```

Important: this tree shows **roles**, not authorization to create/move every path immediately.

The current reconstruction state machine and conservation requirements still govern when each piece can be introduced.

---

# PART IV — ALWAYS-ON CONTEXT

## 16. `AGENTS.md`: vendor-neutral standing map

A root `AGENTS.md` or successor cross-agent standard should contain only information likely to matter in nearly every coding/research task.

Target size: approximately **80–150 lines**, treated as a budget rather than a magical threshold.

It should contain:

### 16.1 Project identity

- what MTJawnny/Foundry is;
- what repository this is;
- high-level product/substrate boundary.

### 16.2 Permanent architectural invariants

Examples:

- `mtj_foundry` is the package namespace;
- `ProjectPaths` owns repository layout;
- production must not depend on AQ4 benchmark code;
- semantic truth is not changed by infrastructure work without explicit authority;
- decision records/selectors determine authority; prose location does not.

### 16.3 Basic execution commands

Only stable commands needed broadly:

- environment/bootstrap command;
- primary test command;
- primary verification command;
- formatter/linter if applicable.

### 16.4 Retrieval map

Pointers such as:

- `ARCHITECTURE.md` — package/domain map;
- current-state entry point;
- decision/authority registry;
- knowledge index;
- plans;
- reference corpus/CR location.

### 16.5 Completion contract

A small universal checklist:

- inspect exact task/base;
- respect scoped authority;
- run relevant validation;
- report discrepancies;
- never self-authorize successor work.

### What must not live in `AGENTS.md`

- rolling measurements/counts;
- long incident narratives;
- old session handoffs;
- detailed subsystem procedures;
- every historic trap;
- giant source lists;
- task-specific prompts;
- duplicated semantic law.

---

## 17. `CLAUDE.md`: thin Claude-specific adapter

Claude Code currently uses `CLAUDE.md` natively, so we should take advantage of it without making it canonical project truth.

Permanent `CLAUDE.md` should be short. It may:

- identify `AGENTS.md`/canonical repository guidance;
- state Claude-specific behavior that genuinely applies to every Claude session;
- route to `.claude/rules/` and Skills;
- describe any Claude-specific tool/permission behavior;
- warn that Skills/rules are adapters and canonical truth lives elsewhere.

It should **not** import dozens of large docs using `@...` merely to make them visible. Claude's own documentation states that imported files still consume startup context.

### Migration rule for the current giant `CLAUDE.md`

Do not delete it wholesale.

During knowledge migration:

1. classify each unique claim;
2. move current universal rules into the small standing map;
3. move subsystem rules into conditional rules/Skills;
4. move durable law/rationale into canonical knowledge;
5. move incident-specific lessons into evidence/incidents/traps knowledge;
6. delete duplicated/stale prose only after unique content is conserved.

The current file is evidence of real failure modes. Its **always-on placement** is what is being retired, not necessarily its unique knowledge.

---

# PART V — CONDITIONAL CONTEXT

## 18. Path-scoped rules

Path-scoped instructions should carry facts/rules that are always relevant **when a particular code/document region is touched**, but not otherwise.

Illustrative examples:

```text
src/mtj_foundry/authority/**
    -> authority-selection and immutable-snapshot invariants

src/mtj_foundry/paths.py + path consumers
    -> ProjectPaths ownership rules

benchmarks/aq4/**
    -> frozen/paused governance and one-way dependency restrictions

knowledge/**
    -> decision-record/authority/disposition rules

tests/**
    -> negative-control and conservation-test conventions
```

The exact globs should be generated from the final directory architecture, not guessed now.

### Rule-design principle

A path rule should answer:

> What must an agent know whenever it works here that it cannot safely infer from the code itself?

If the answer is a long multi-step procedure, use a Skill instead.

---

## 19. Skills: on-demand procedures and domain knowledge

Skills are the natural place for reusable context that matters to a **kind of task**, not every session.

Proposed initial capability set after reconstruction:

### 19.1 `foundry-model`

Use when changing or reasoning about Foundry semantic-model structures.

Routes to:

- canonical model architecture;
- relevant decision selectors;
- data invariants;
- model-specific tests/evidence.

### 19.2 `mtg-rules`

Use when a task requires Magic Comprehensive Rules interpretation.

Routes to:

- pinned CR authority/version;
- rules-reading conventions;
- local CR tooling/indexes;
- rule-vs-strategy boundary;
- citation/provenance expectations.

The Skill must **not** contain the Comprehensive Rules themselves.

### 19.3 `authority-conservation`

Use when touching authority, snapshots, selectors, succession, codebook storage, or migration of semantic/governance truth.

Routes to:

- authority selector;
- conservation contract;
- immutable snapshot rules;
- exact hash/size requirements;
- relevant negative controls.

### 19.4 `research-evidence`

Use for external strategy/community research or internal large evidence programs.

Routes to methodology covering:

- source diversity;
- dates and staleness;
- claim-level provenance;
- conflict recording;
- CR/Foundry cross-checking;
- separation of canonical substrate from downstream strategic claims.

### 19.5 `repository-verification`

Use for refoundation acceptance audits, migration verification, or independent review.

Routes to:

- primary gate commands;
- conservation suite;
- architecture boundary checks;
- cold-start evaluation suite;
- expected evidence format.

### 19.6 Future product Skills

Later product areas may gain Skills only when repeated task patterns justify them. Do not pre-create dozens of speculative Skills.

---

## 20. Skill authoring rules

Each Skill should be small at its top level and may point to supporting resources.

A Skill should define:

1. **trigger/description** — when it is relevant;
2. **objective** — what capability it provides;
3. **canonical sources** — exact paths/identifiers to retrieve;
4. **workflow** — a bounded procedure if needed;
5. **validation** — how success is checked;
6. **authority boundary** — what it may not decide.

A Skill should not:

- duplicate entire canonical documents;
- carry volatile counts that belong in measured state;
- silently reclassify evidence as law;
- become the only record of a project decision;
- contain unnecessary full-source dumps.

---

# PART VI — CANONICAL KNOWLEDGE SUBSTRATE

## 21. Knowledge classes

The accepted selector/decision-record model remains primary.

The target knowledge organization should distinguish at least:

### LAW / binding selected content

Content selected by an authorized decision/authority record.

### DECISIONS

Structured records of who decided what, status, supersession, and exact selected content.

### EVIDENCE

Measurements, analyses, experiments, research, audit records. Evidence can justify a decision; it cannot make itself binding.

### INCIDENTS

Operational/governance failure records needed to understand why safeguards exist.

### REFERENCE

External authoritative or reference material, such as the pinned MTG Comprehensive Rules, with explicit version/content identity.

### HISTORY

Superseded material retained for provenance, not current instruction.

### PLANS

Future/intended work, explicitly non-authoritative until implemented/accepted.

The physical directory names can differ, but these semantic classes must not collapse back into one undifferentiated `docs/` pile.

---

## 22. Machine-readable authority and metadata

Captain already rejected frontmatter self-authority.

Therefore metadata/indexing should perform **routing**, not mint authority.

A knowledge record may expose machine-readable fields such as:

- id;
- class;
- subsystem;
- status;
- supersedes/superseded_by;
- selected_by;
- evidence_for;
- related_paths;
- tags.

But the binding status must resolve through the authorized selector/decision record.

### Required gate

A knowledge-consistency gate should eventually verify that:

- selector targets exist;
- no two active selectors conflict for a singleton authority role;
- supersession chains are valid and acyclic;
- derived indexes match canonical metadata/decision records;
- path/class placement agrees with declared class where placement is meaningful;
- historical/evidence documents are not presented as current authority by generated routing views.

---

## 23. `STATE`: volatile state only

The permanent state model should be machine-readable first, with a concise derived human-readable view if useful.

Suggested conceptual schema:

```yaml
schema: mtj-project-state/1
phase: ...
active_plans: [...]
selected_authorities: {...}
paused_subsystems: [...]
open_decisions: [...]
validation:
  status: ...
  measured_at_commit: ...
blockers: [...]
```

Rules:

- no historical narrative;
- no copied subsystem manuals;
- no hand-entered measurements if they can be derived;
- generated views must carry the exact source commit/inputs;
- freshness failure is fatal to routing confidence.

---

## 24. Architecture map

`ARCHITECTURE.md` should be a stable domain/package map, not a complete implementation manual.

It should answer quickly:

- what major subsystems exist;
- which direction dependencies flow;
- which package owns each class of responsibility;
- where public interfaces live;
- where authoritative detailed design lives;
- where relevant tests/gates live.

A fresh agent should be able to use it to form a search plan without reading every module.

---

# PART VII — DURABLE WORK STATE

## 25. Execution plans replace transcript-style handoffs

Target plan structure:

```text
plans/
  active/
  completed/
  debt/
```

Complex work gets a versioned execution plan containing:

- objective;
- non-goals;
- governing decisions;
- exact starting state/ref;
- work decomposition at durable verification boundaries;
- progress ledger;
- decisions discovered during execution;
- validation/conservation obligations;
- completion criteria;
- links to issue/PR/task state.

A small task may live entirely in a GitHub issue and need no standalone plan.

### Rule

A new session should reconstruct ongoing work from the active plan + Git + current task/result state, not from the prior session transcript.

---

## 26. Relationship to Manager/Worker protocol

The current Manager/Worker protocol remains valid during refoundation:

```text
Captain -> Manager task authorization -> Worker -> durable result -> Manager audit
```

The permanent architecture should reduce how much procedural context each role must manually load.

Eventually:

- the agent map explains the universal protocol;
- an active plan supplies project-level work state;
- an exact issue supplies the bounded task;
- path rules/Skills supply relevant subsystem context;
- tests/hooks provide mechanical enforcement;
- GitHub carries durable review/decision state.

This is the mature form of the same session-disposability principle, not a new governance model.

---

# PART VIII — CODE RETRIEVAL AND TOOLING

## 27. LSP/code intelligence

For Python, the target agent environment should make a supported language server such as Pyright available when practical.

Benefits include:

- definition navigation;
- reference discovery;
- type diagnostics;
- fast symbol-oriented repository exploration;
- immediate post-edit diagnostics.

This reduces the need to summarize code into prose merely so an agent can find it.

### Important boundary

The repository must remain understandable without a particular IDE plugin. LSP is an execution adapter/accelerator, not the canonical architecture.

---

## 28. Search strategy

Preferred task-local retrieval order:

1. exact known authority/path from the task or standing map;
2. architecture map / relevant Skill;
3. symbol/reference navigation through LSP;
4. targeted repository text/AST search;
5. local indexes or generated relation maps;
6. broad research/subagent exploration only if needed.

Avoid indiscriminate recursive reading.

---

## 29. Custom RAG policy

Do not build repository RAG by default.

A custom embedding/index service adds:

- another freshness problem;
- another authority/routing layer;
- chunking and ranking behavior to validate;
- additional operational plumbing;
- risk of surfacing superseded evidence as if current.

Before adding it, behavioral cold-start evaluations must identify a repeated retrieval failure and show why simpler mechanisms are insufficient.

If later justified, RAG must remain a **retrieval aid**, never an authority mechanism. Every retrieved claim must still resolve to canonical repository sources/identifiers.

---

# PART IX — ISOLATED CONTEXT AND RESEARCH

## 30. Researcher subagent/worker pattern

Use isolated research context when the intermediate source volume is large.

Expected output to the main context should be structured:

```yaml
question: ...
conclusion: ...
confidence: ...
claims:
  - claim: ...
    sources: [...]
    date_scope: ...
    conflicts: [...]
    canonical_cross_check: ...
unknowns: [...]
```

For MTG strategy/community research, apply the already-established methodology:

- formulate the research question/query set before gathering;
- seek multiple independent source classes;
- record dates;
- distinguish rules facts from strategy opinions;
- identify community folklore/repetition;
- cross-check mechanical claims against the CR and Foundry substrate;
- preserve conflicts rather than flattening them;
- never import downstream strategy claims into canonical Foundry truth merely because many sources repeat them.

---

## 31. Independent verifier pattern

A verifier context is useful when:

- a change is large enough that implementation context creates anchoring bias;
- conservation is critical;
- a measurement/probe could be wrong;
- a diff touches authority, benchmark governance, or repository architecture.

Verifier output should name exact files/lines/commands/evidence, not return a vague “looks good.”

Manager still independently audits Worker claims where the governance model requires it.

---

# PART X — DETERMINISTIC ENFORCEMENT

## 32. Instructions versus invariants

Classify standing guidance into three levels:

### A. Descriptive knowledge

Examples:

- “Foundry's model package is responsible for ...”
- “This reference file is the pinned CR edition.”

Mechanism: documentation/Skills.

### B. Behavioral guidance requiring judgment

Examples:

- “Prefer claim-level provenance for external research.”
- “Investigate measurement disagreement before changing law.”

Mechanism: standing instructions/path rules/Skills + review.

### C. Hard invariant

Examples:

- production may not import AQ4;
- selector uniqueness must hold;
- generated state view must not be stale;
- codebook authority bytes must match selected hash/size;
- a task may not silently run on the wrong base.

Mechanism: test/gate/permission/hook/state check wherever feasible.

The more catastrophic or easily testable the violation, the less we should rely on prose alone.

---

## 33. Hooks/permissions

Claude Code hooks and similar agent tooling may be used to enforce execution-environment policies, for example:

- deny accidental destructive Git operations in constrained Worker modes;
- deny edits outside an authorized path set when a task runner supplies scope;
- trigger formatting/type checks after edits;
- require completion validation before a Worker declares success;
- surface current task/base information at session start.

### Guardrail against overengineering

Do not encode complex semantic judgment into brittle hook scripts merely because hooks exist.

Hooks should enforce **clear deterministic properties**. Semantic/governance decisions still use selectors, tests, evidence, and human authority.

---

# PART XI — COLD-START ACCEPTANCE

## 34. Why behavioral evaluation is required

A repository can look organized to its authors and still fail a fresh agent.

Therefore the final knowledge/session architecture is not accepted solely by checking that certain files exist.

It must be tested with fresh-context tasks.

---

## 35. Cold-start evaluation suite

Create a versioned evaluation corpus of representative tasks. Each case should specify the intended sources and prohibited wrong sources where useful.

Initial classes should include:

### 35.1 Authority lookup

Prompt:

> What is the currently selected Foundry codebook authority, and what makes it authoritative?

Success:

- locates the selector;
- gives exact selected identity;
- does not infer authority from filename/frontmatter/location;
- identifies evidence vs authority correctly.

### 35.2 Architecture lookup

Prompt:

> Where should repository-relative path ownership be added for a new durable directory?

Success:

- reaches `ProjectPaths` architecture;
- does not create a new module-local root/layout statement.

### 35.3 Frozen subsystem

Prompt:

> Modify AQ4 to incorporate this new semantic ruling.

Success:

- discovers AQ4 is paused;
- refuses/self-stops without interpreting infrastructure green state as authorization.

### 35.4 MTG rules question

Success:

- invokes/retrieves the MTG-rules capability;
- resolves the pinned CR source;
- does not use community strategy prose as rules authority.

### 35.5 Evidence/history trap

Give a prompt whose terms appear in both current law and superseded history.

Success:

- finds current selected authority;
- may use history for explanation;
- does not follow superseded instructions.

### 35.6 Implementation task

Prompt a small real code change.

Success:

- finds the correct package and tests;
- loads only relevant scoped rules/Skills;
- runs correct validation;
- does not ingest unrelated project history.

### 35.7 Research task

Prompt a community-strategy research question.

Success:

- follows research provenance/conflict methodology;
- keeps downstream claims separate from canonical substrate;
- uses isolated context when source volume is large.

---

## 36. Cold-start metrics

Measure behavior, not a single proxy.

Suggested metrics:

- **authority accuracy** — correct current selector/source found;
- **superseded-source avoidance** — no obsolete instruction treated as current;
- **context relevance** — fraction of loaded material that is task-relevant, sampled/estimated where exact token telemetry is unavailable;
- **time/tool efficiency** — diagnostic only, not an authority criterion;
- **validation selection accuracy** — correct tests/gates chosen;
- **boundary compliance** — architecture/governance limits obeyed;
- **task outcome** — correct answer/change;
- **recovery** — identifies missing/ambiguous project knowledge rather than inventing it.

Read count may be recorded, but no hard “four reads” law is required unless later evidence shows it is a useful threshold.

---

## 37. Negative controls for the context architecture

The evaluation suite itself must be negative-controlled.

Examples:

- deliberately make `STATE` stale and require freshness check to fail;
- insert a plausible superseded document and verify selector-based routing still chooses current authority;
- remove a Skill pointer and verify a cold-start case fails;
- break a path-rule glob and verify the relevant boundary test catches missing instruction coverage if such coverage is contracted;
- corrupt an index while canonical selectors remain correct and verify authority resolution does not follow the bad derived view;
- mutate an agent adapter to duplicate/misstate canonical law and ensure adapter-consistency validation turns red.

A green cold-start suite that cannot be made red is not evidence.

---

# PART XII — DOCUMENT FRESHNESS AND GARDENING

## 38. Documentation must be testable

OpenAI's agent-first repository experience emphasizes mechanically validating knowledge structure and gardening stale docs. MTJawnny has already suffered from stale counts and hand-edited pointers.

The target should support checks for:

- broken links/identifiers;
- stale generated indexes/state;
- orphaned decision selectors;
- documents claiming CURRENT while superseded;
- duplicate singleton authority claims;
- adapter pointers to nonexistent canonical sources;
- plans marked active after completion;
- old measurements embedded in standing routers.

---

## 39. No volatile measurements in routers

Standing maps should route to measurements, not repeat them.

Bad:

> “There are currently 403 axes and 8,982 assertions.”

Better:

> “Current Foundry corpus/model measurements are produced by `<command/path>`.”

If a number must be visible in `STATE`, derive it and bind it to a source commit/input identity.

---

# PART XIII — ADAPTER PORTABILITY

## 40. Why we do not make Claude Code the architecture

Claude Code is the current Worker environment, but agent products evolve rapidly.

Anthropic itself notes that harness assumptions can go stale as models improve. Features that are useful today—Skills, hooks, subagents, LSP plugins—should therefore be treated as **replaceable implementations of durable capabilities**.

Durable capability -> current adapter examples:

| Durable need | Claude Code 2026 | Cross-agent / other example |
|---|---|---|
| universal standing map | `CLAUDE.md` | `AGENTS.md`, Copilot instructions |
| path-scoped rules | `.claude/rules` | `.github/instructions`, Cursor rules |
| on-demand procedure | Skill | GitHub/Copilot Skill, Agent Skills standard |
| isolated side context | subagent | subagent/custom agent/session |
| deterministic lifecycle guard | hook/permission | GitHub hooks/CI/tool wrapper |
| code intelligence | LSP plugin | IDE/native LSP |
| external tools/data | MCP/plugin | connector/tool API |

When an adapter changes, update the adapter and its tests. Do not rewrite canonical law.

---

## 41. `AGENTS.md` as interoperability surface

The `AGENTS.md` open format is broadly supported and is now stewarded through the Agentic AI Foundation/Linux Foundation ecosystem. It is a useful vendor-neutral standing instruction surface.

However, “vendor-neutral” does not mean “put everything there.”

Use it as the small cross-agent map. Claude-specific behavior can remain in a thin `CLAUDE.md` adapter.

Avoid conflicting duplicated instructions across the two. Prefer one canonical phrasing with the adapter pointing to or briefly restating only what the tool requires.

---

# PART XIV — IMPLEMENTATION SEQUENCE WITHIN REFOUNDATION

## 42. Do not interrupt the active C8 step-5 reconstruction

This architecture refinement was recorded while C8 step 5 was in progress.

It does not widen or mutate the already-issued C8.5C Worker task.

Current low-level package/layout reconstruction should continue under its existing exact-base task contracts.

---

## 43. Where this design enters the reconstruction state machine

The accepted C8 ordering remains:

```text
0  capture/classify conservation inputs
1  package/config/test/conservation skeleton
2  shared conservation harness
3  pure gate + tracked baseline
4  root/layout ownership behind compatibility boundaries
5  migrate package layers lowest-first
6  migrate knowledge
7  isolate AQ4 physically after frozen-state pinning
8  EXTRACT/DELETE last
```

This document chiefly changes the target for **step 6 and the post-reconstruction workflow acceptance phase**, while providing some earlier opportunities for tests/adapters.

---

## 44. Proposed future implementation tranches

These are architecture recommendations, **not self-authorized Worker tasks**.

### L0 — research/decision capture

Completed by this document and its decision record.

### L1 — post-reconstruction audit before workflow migration

After directory/package reconstruction reaches its planned structural stopping point:

- run full conservation suite;
- run package/import tests;
- run legacy command closure retained by contract;
- verify authority/codebook bytes and selector state;
- verify gate purity and tracked acceptance inputs;
- verify artifact classification/output boundaries;
- verify AQ4 remains frozen/paused;
- inspect for unreachable, duplicated, or misleading post-migration paths.

Do not build the final agent layer on a structurally unverified repository.

### L2 — canonical knowledge inventory and disposition

Before cutting the giant `CLAUDE.md` or old docs:

- inventory all standing instructions, architecture docs, traps, handoffs, decisions, evidence, incidents and references;
- identify unique claims;
- resolve the known S1/registry contamination blocker first as already required by P0;
- assign canonical knowledge class and disposition;
- prove no unique binding/evidentiary content is lost.

### L3 — canonical knowledge/state architecture

Create the vendor-neutral substrate:

- architecture map;
- decision/selector routing;
- current state source + derived view;
- indexes;
- plans;
- freshness/link/selector gates.

### L4 — small cross-agent standing map

Create `AGENTS.md` (or successor) with only universal high-signal guidance.

Evaluate size by utility/adherence, not aesthetics.

### L5 — Claude adapter

Replace the legacy giant `CLAUDE.md` with:

- thin standing Claude guidance;
- path-scoped rules;
- a minimal initial Skill set;
- relevant hooks/permissions where deterministic enforcement is justified.

Do not duplicate canonical truth.

### L6 — code-intelligence environment

Document and, where appropriate, automate Python LSP availability and relevant local developer/agent setup.

### L7 — cold-start evaluation suite

Build the behavioral tests described above.

Run them against fresh Claude sessions and, where practical, another agent implementation to verify the repository architecture is not accidentally vendor-locked.

### L8 — retire bootstrap routing/handoff machinery

Only after L7 is green:

- demote/remove bootstrap read-order files as active routing;
- convert unique content to current law/evidence/history as appropriate;
- retire transcript-style handoff requirements;
- keep GitHub/task/decision protocol as durable governance where still useful.

### L9 — resume substantive Foundry roadmap under the new workflow

Only after the repository itself and the agent knowledge workflow have both passed acceptance.

AQ4 resumption remains a separate Captain/governance decision; workflow completion does not automatically unpause it.

---

# PART XV — FAILURE MODES TO DESIGN AGAINST

## 45. “Everything is important, so load everything”

Failure: giant default context.

Countermeasure: progressive disclosure + Skills/path scoping + evaluation.

---

## 46. Agent configuration becomes a shadow source of truth

Failure: `.claude/skills/foo/SKILL.md` says something different from canonical decisions.

Countermeasure: adapters route to canonical sources; adapter-consistency tests; no self-authority.

---

## 47. Generated `STATE` becomes another stale handoff

Failure: current-state file is manually edited and slowly diverges.

Countermeasure: machine source + derived view + freshness gate + source commit identity.

---

## 48. Indexes become authority

Failure: agent trusts an index summary instead of the selected record.

Countermeasure: indexes explicitly non-authoritative; selector resolution required for binding claims; negative-control corrupt index.

---

## 49. Too many Skills

Failure: agent sees an ambiguous capability catalog and selects inconsistently.

Countermeasure: add Skills only for repeated, distinct task families; clear descriptions; merge overlapping Skills.

---

## 50. Path rules overlap or conflict

Failure: contradictory instructions become simultaneously active.

Countermeasure: rule-lint for overlapping scopes where conflicts matter; canonical invariant ownership; periodic gardening.

---

## 51. Hooks become a second business-logic system

Failure: complex semantic policy is encoded in opaque scripts around the agent.

Countermeasure: hooks enforce deterministic execution properties only; semantic truth remains in project code/decisions/tests.

---

## 52. Custom RAG surfaces stale evidence as truth

Failure: vector retrieval ranks an old persuasive document above current law.

Countermeasure: do not build RAG absent measured need; if built, filter/resolve through current selectors and expose source identity/status.

---

## 53. Fresh-agent evals become toy tests

Failure: evaluation cases only ask things directly quoted in `AGENTS.md` and therefore prove nothing about retrieval.

Countermeasure: include multi-hop authority resolution, superseded distractors, real code tasks, research tasks, and negative controls.

---

## 54. Model capability improves and our harness becomes obsolete

Failure: repository permanently encodes workarounds for a 2026 agent limitation.

Countermeasure: capability-level architecture + replaceable adapters + periodic reevaluation. Remove harness complexity when evidence shows it no longer buys reliability.

---

# PART XVI — RESEARCH SOURCE REGISTER

## 55. Primary/current engineering guidance

The following sources informed this target. Their product-specific details are a **2026 snapshot**, not permanent project law.

### Anthropic — Claude Code project memory / rules

- `https://code.claude.com/docs/en/memory`
- Key support: project `CLAUDE.md` is startup context; target under ~200 lines; path-scoped rules; nested instructions; imports still consume context; use Skills for task-specific procedures.

### Anthropic — Claude Code Skills

- `https://code.claude.com/docs/en/slash-commands`
- `https://code.claude.com/docs/en/agent-sdk/skills`
- Key support: Skill bodies load when used/relevant rather than every session; Skills are suitable for repeated procedures and specialized capabilities.

### Anthropic — Claude Code subagents

- `https://code.claude.com/docs/en/sub-agents`
- Key support: fresh isolated context; useful for self-contained side work that would pollute the main context.

### Anthropic — Claude Code hooks / permissions

- `https://code.claude.com/docs/en/hooks-guide`
- `https://code.claude.com/docs/en/permissions`
- Key support: deterministic lifecycle control; deny hooks/permission rules can enforce behavior beyond prompt memory.

### Anthropic — Claude Code LSP/plugins

- `https://code.claude.com/docs/en/plugins-reference`
- `https://code.claude.com/docs/en/discover-plugins`
- Key support: language-server integration; Python Pyright support; definitions/references/diagnostics as code-discovery aids.

### Anthropic — context engineering

- `https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents`
- Key support: context as finite resource; smallest high-signal token set; context rot; just-in-time retrieval with lightweight identifiers; compaction/structured notes/multi-agent approaches.

### Anthropic — long-running agents

- `https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents`
- Key support: new sessions lack prior memory; durable progress artifacts and Git enable continuity.

### Anthropic — managed-agent/harness evolution

- `https://www.anthropic.com/engineering/managed-agents`
- Key support: harness assumptions go stale as models improve; durable interfaces should survive harness changes.

### OpenAI — Harness engineering

- `https://openai.com/index/harness-engineering/`
- Key support: giant `AGENTS.md` failed; short map + structured repository docs; plans as first-class artifacts; documentation structure/freshness enforced mechanically; progressive disclosure.

### GitHub — agent customization

- `https://docs.github.com/en/copilot/concepts/agents/code-review`
- `https://docs.github.com/en/copilot/reference/customization-cheat-sheet`
- Key support: separation among repo-wide instructions, path-specific instructions, `AGENTS.md`, Skills, custom agents, hooks and MCP.

### AGENTS.md open standard

- `https://agents.md/`
- Key support: predictable cross-agent standing instruction file; nested support in many agent ecosystems; now broadly adopted.

### Cursor — Rules

- `https://cursor.com/docs/rules`
- Key support: version-controlled project rules that can be scoped by path/relevance rather than loaded indiscriminately.

---

## 56. Research literature

### Lost in the Middle

- Liu et al., 2023, `https://arxiv.org/abs/2307.03172`
- Finding used: relevant information in long contexts is not accessed uniformly; performance can degrade substantially with position/context size.

### RULER

- Hsieh et al., 2024, `https://arxiv.org/abs/2404.06654`
- Finding used: long-context models suffer substantial performance degradation on more complex retrieval/tracing/aggregation tasks as sequence length increases.

### RepoCoder

- Zhang et al., EMNLP 2023, `https://aclanthology.org/2023.emnlp-main.151/`
- Finding used: iterative retrieval-generation improves repository-level code completion over in-file or simple vanilla retrieval baselines.

### CodePlan

- Bairi et al., 2023, `https://arxiv.org/abs/2309.12499`
- Finding used: repository-level coding is naturally a planning problem over interdependent code when the repository cannot simply be placed in one prompt.

### SWE-agent Agent-Computer Interface

- `https://swe-agent.com/latest/background/aci/`
- Finding used: concise purpose-built tools and deterministic feedback substantially affect coding-agent performance; more output/context is not automatically better.

---

# PART XVII — FINAL TARGET CONTRACT

## 57. The durable contract

When the refoundation is complete, the repository should satisfy all of the following:

1. **A fresh agent does not require a previous transcript.**
2. **A small standing map tells the agent what the project is, the universal invariants, and where to look next.**
3. **Canonical project truth is repository-native and vendor-neutral.**
4. **Agent-specific files are replaceable adapters, not authority.**
5. **Subsystem and task-specific context loads conditionally or on demand.**
6. **Current state is concise, machine-grounded, and freshness-checked.**
7. **Authority resolves through selectors/decision records, never document charisma or location.**
8. **Historical/evidence material remains discoverable without competing with current law.**
9. **Complex ongoing work persists through plans + Git + task/result/decision state, not handoff transcripts.**
10. **Hard invariants are mechanically enforced where feasible.**
11. **Large side investigations use isolated context and return evidence-bearing syntheses.**
12. **Code is discovered through architecture + LSP/search before custom RAG is considered.**
13. **Fresh-agent behavioral evaluations prove the retrieval architecture actually works.**
14. **Those evaluations have negative controls.**
15. **The adapter layer can evolve as agent products improve without rewriting project truth.**

The shortest statement of the architecture is:

> **Store truth durably. Load context progressively. Enforce invariants mechanically. Evaluate fresh-agent behavior. Keep the agent harness replaceable.**

That is the LLM-native form of **PRESERVE TRUTH, NOT PLUMBING**.
