# MTJawnny Temporary Agent Communication Protocol

**Status:** TEMPORARY / PRE-ORCHESTRATOR  
**Purpose:** Reduce token-heavy English relay between ChatGPT and Claude Code while preserving Captain control, repository safety, and stop-on-drift behavior.  
**Applies now:** AQ4 benchmark packets and other bounded Foundry work until the dedicated agent bridge/orchestrator is designed and ratified.

---

## 1. Why this exists

The current manual workflow is functional but inefficient:

```text
Captain
  -> ChatGPT reasoning
  -> long English Claude prompt
  -> manual copy/paste
  -> Claude Code execution
  -> long English checkpoint
  -> manual copy/paste
  -> ChatGPT review
```

The temporary replacement is:

```text
Captain
  -> ChatGPT decides intent / architecture
  -> compact TASK CONTRACT
  -> Claude Code executes against live repo
  -> compact TASK RESULT
  -> ChatGPT reviews result / evidence
  -> Captain only when a real ruling is needed
```

Human language remains appropriate for:
- architecture discussion;
- ambiguous reasoning;
- Captain rulings;
- explanations of unusual findings.

Structured data is preferred for:
- task identity;
- expected base commit;
- allowed/forbidden mutation;
- invariants;
- stop conditions;
- measured results;
- commit scope;
- next-state authorization.

---

## 2. Roles

### Captain — User

The Captain remains the final authority for architecture-affecting decisions, governance changes, authority/data changes, baseline acceptance where policy is involved, destructive/external publication, and any decision explicitly escalated by ChatGPT or Claude.

The automation protocol must never silently replace Captain authority.

### Manager — ChatGPT

ChatGPT is responsible for project trajectory, architecture reasoning, reviewing Claude's structured result, issuing the next bounded task contract, distinguishing measured fact from architecture implication, escalating true decision boundaries to Captain, and preventing work from drifting into unauthorized next stages.

ChatGPT should not waste tokens re-describing deterministic repository state when that state can be expressed in fields or checked mechanically.

### Worker — Claude Code

Claude Code is responsible for reading the live repository, inspecting exact implementation details, modifying permitted files, running tests, discovering local defects, producing machine-structured results, and stopping when the task contract or repository reality diverges.

Claude Code should not invent architecture policy, continue into the next packet without authorization, absorb unrelated worktree changes, reinterpret a STOP condition to keep moving, or narrate every shell command unless it is evidence for a discrepancy.

### Deterministic Controller — future

A future local bridge/orchestrator should eventually take over HEAD checks, file-scope checks, SHA checks, Gate 2 invocation, authority checks, staged-file checks, working-tree collision detection, task/result storage, and handoff between Manager and Worker.

That orchestrator is **not being built yet**. The current protocol is a manual prototype of the future API.

---

## 3. Temporary operating principle

Starting now:

> Prefer compact structured contracts/results over long English prompts/checkpoints.

Do not eliminate prose entirely. Use prose only where the task requires interpretation.

The goal is not a secret AI language. The goal is a typed, low-ambiguity coordination language shared by humans and models.

---

## 4. TASK CONTRACT — temporary schema

Use YAML by default because it is compact and human-readable.

Recommended shape:

```yaml
schema: mtj-task/0
task: AQ4.P2.RAMP-CORRECTION
base: 9cb214a

objective:
  - complete benchmark-only Cohort 6 ramp coverage

context:
  packet: 2
  architecture_status: UNRATIFIED

allow:
  - experiments/aq4_benchmark/**

deny:
  - production_semantics
  - authority
  - baseline
  - packet3
  - holdout_reveal

invariants:
  gate2: "15/1/0"
  authority: LOCAL_MATCHES_AUTHORITY
  codebook_sha256: 6aa6193f8a457ae4c7884e364f519749a9d68b96f7ecedf3fa903bfa4677426c
  codebook_bytes: 5066147

rulings:
  cohort4_size: KEEP_795
  benchmark_oracle_id_in_git: ALLOWED_NARROWLY
  production_ramp_vocabulary: FORBIDDEN

required:
  - derive objective land-to-battlefield ramp arm
  - preserve existing deterministic split
  - add negative controls
  - prove cohort4 unchanged

stop:
  - architecture_decision_required
  - cohort4_changes
  - cohort5_revealed
  - production_mutation
  - invariant_failure
  - unrelated_worktree_drift

commit:
  allowed: true
  subject: "AQ4: complete consumer-critical ramp cohort"
  scope:
    - experiments/aq4_benchmark/**

next:
  authorized: NONE

return:
  schema: mtj-result/0
```

---

## 5. TASK CONTRACT field meanings

### `schema`
Current temporary schema:

```text
mtj-task/0
```

Do not pretend this is stable API law. It is a prototype.

### `task`
Unique conceptual task identifier.

Examples:

```text
AQ4.P2.RAMP-CORRECTION
AQ4.P3.HOLDOUT-COMMITMENT
C6.2B2.AUTHORITY-CUTOVER
REGISTRY.TRACKED-DOC-HYGIENE
```

### `base`
Expected starting Git revision. Claude must verify it. If live HEAD differs and no newer Captain-authorized state explains it: **STOP**.

### `objective`
Short statements of desired outcome. Do not encode implementation details here unless they are actually part of the contract.

### `allow`
Paths or mutation classes Claude may change. Prefer explicit paths.

### `deny`
Files, state classes, or next-stage work that must not change. This can include conceptual boundaries such as `authority`, `baseline`, `production_semantics`, `packet3`, `holdout_reveal`, and `stage_f`.

Claude must interpret these against repository law.

### `invariants`
Machine facts that must remain true, such as codebook hash, byte size, Gate 2 status, selected authority state, registry metrics, W6 identity, and known deterministic output hashes.

These should eventually be checked by software, not LLM reasoning. For now Claude may verify them.

### `rulings`
Captain decisions already made. This avoids re-explaining them in prose.

Claude may implement within these rulings but may not reinterpret them.

### `required`
Concrete acceptance requirements. These should be task-local.

### `stop`
Events that require immediate halt. Claude must favor STOP over improvisation.

A STOP result is a successful execution outcome when the repository exposes a genuine decision boundary.

### `commit`
Specifies whether Claude may commit and the exact conceptual scope. If scope broadens unexpectedly: **STOP**.

### `next`
This is critical. Default:

```yaml
next:
  authorized: NONE
```

Claude must never begin another packet or phase merely because the current one passes.

---

## 6. TASK RESULT — temporary schema

Claude should return compact YAML.

Recommended shape:

```yaml
schema: mtj-result/0
task: AQ4.P2.RAMP-CORRECTION
status: PASS

base:
  expected: 9cb214a
  measured: 9cb214a

commit:
  sha: abc1234
  files:
    - experiments/aq4_benchmark/aq4_population.py
    - experiments/aq4_benchmark/sampling.json

checks:
  gate2: PASS
  authority: PASS
  codebook: PASS
  registry: PASS
  determinism: PASS
  worktree_conservation: PASS

measurements:
  ramp_population: 123
  open_half: 61
  closed_half: 62

controls:
  total: 6
  passed: 6
  rigged_red: 6

findings:
  - code: RAMP.LAND_TO_BATTLEFIELD
    severity: INFO
    summary: objective structural arm added

discrepancies: []

decision_required: false

next_ready:
  - AQ4.P3
```

---

## 7. Result statuses

Allowed top-level values:

```text
PASS
STOP
FAIL
COMMIT_READY
```

- **PASS** — task completed within contract; does not authorize the next task.
- **STOP** — genuine boundary requiring Manager/Captain review; STOP is not failure.
- **FAIL** — implementation/test state is incorrect and unresolved.
- **COMMIT_READY** — work is complete and verified but commit authorization/scope was unavailable.

---

## 8. Evidence should be lazy, not dumped by default

Claude should not return a giant checkpoint unless requested.

Use concise `findings` with stable codes:

```yaml
findings:
  - code: P3.POPULATION.LATTICE_GAP
    severity: MATERIAL
    summary: fight and attach are unreachable in lattice-derived population
    evidence_ref: evidence/P3.POPULATION.LATTICE_GAP.md
```

If ChatGPT needs more detail, request that evidence specifically.

Until the actual bridge exists, the user may paste only the evidence block when asked.

This reduces unnecessary model-to-model token transport.

---

## 9. When prose is still required

Structured communication should not replace reasoning where prose is useful.

Claude should include concise prose for:
- a novel repository defect;
- why a STOP fired;
- why a negative control was mis-aimed;
- architecture-relevant interpretation that cannot be represented as simple fields;
- an ambiguity requiring Captain ruling.

ChatGPT may issue prose alongside a task contract for a new conceptual distinction, rationale needed to prevent optimizing the wrong objective, or nuanced safety/governance interpretation.

The rule is:

> **Structure carries state. Prose carries meaning.**

---

## 10. Stop-on-drift remains mandatory

The protocol is more compact, not less strict.

Claude must STOP if:
- HEAD is wrong;
- allowed file scope must expand unexpectedly;
- production state must change;
- authority changes;
- Gate 2 turns red unexpectedly;
- baseline movement is not authorized;
- a new architecture decision is required;
- unrelated worktree state changes;
- the task would enter the next packet;
- a blind cohort/holdout would be exposed outside authorized timing;
- the contract conflicts with live ratified repository law.

Repository law beats the task contract. Captain rulings beat implementation convenience.

---

## 11. Temporary human workflow

1. **Captain talks to ChatGPT** in normal English.
2. **ChatGPT emits one compact `mtj-task/0`.** The user pastes it to Claude Code.
3. **Claude works against the live repo** and returns `mtj-result/0`.
4. **User pastes the compact result to ChatGPT.** Do not paste full command transcripts unless requested.
5. **ChatGPT reviews** and may accept, request one evidence reference, ask Captain for a ruling, or emit the next task contract.

---

## 12. Fresh-session Claude bootstrap

At the start of a new Claude Code session using this temporary protocol, give Claude:

```text
MTJAWNNY TEMPORARY AGENT COMMUNICATION MODE

This project is temporarily replacing long prose task/checkpoint handoffs with a compact structured protocol while a future agent bridge/orchestrator is still unbuilt.

You are the repository WORKER.
ChatGPT is the MANAGER / architecture reviewer.
The user is the CAPTAIN and final authority.

For this session:

1. The live repository is authoritative.
2. Read project routing/current-entry-point documentation before work.
3. Tasks will normally arrive as YAML with schema `mtj-task/0`.
4. Treat the task contract as a bounded execution contract, not as permission to infer future work.
5. Repository law overrides a task contract if they conflict.
6. `next.authorized: NONE` means STOP after the current task even on PASS.
7. Prefer deterministic repository evidence over prose claims.
8. STOP on drift rather than improvising.
9. Return a compact YAML `mtj-result/0`, not a long narrative checkpoint.
10. Put unusual detail into `findings` with concise stable codes.
11. Only provide long evidence when:
    - the task explicitly requests it,
    - a STOP requires explanation,
    - or the Manager later asks for a particular finding.
12. Do not omit meaningful discrepancies merely to keep the result short.

Structured state should carry:
- commit/base state;
- checks;
- measurements;
- controls;
- mutation scope;
- discrepancies;
- next-readiness.

Prose should carry:
- novel reasoning;
- ambiguity;
- architecture-relevant interpretation;
- stop rationale.

Do not build the future orchestrator during ordinary Foundry/AQ4 work.

This protocol is temporary and may evolve after several real tasks reveal what the eventual agent API needs.
```

Then provide the task contract.

---

## 13. Current transition plan

### Now
Use `mtj-task/0` and `mtj-result/0` manually through copy/paste.

This immediately reduces token waste and gives us real examples.

### After several real tasks
Review which fields are repeatedly needed, which are never used, common stop reasons, common evidence requests, and what can be checked deterministically.

Do not prematurely freeze the schema.

### Appropriate architecture boundary
After AQ4 reaches its architecture ruling, and before large production retrofit / Stage F, evaluate building the real bridge.

Target design:

```text
Captain
   |
ChatGPT Manager
   |
task contract
   |
deterministic orchestrator
   |
Claude Code Worker
   |
result contract
   |
deterministic verification
   |
ChatGPT Manager
```

---

## 14. Future bridge — likely minimal concepts

The first actual bridge should probably expose only:

```text
STATE
TASK
RESULT
DECISION
EVIDENCE
```

Possible filesystem prototype:

```text
.agent/
  state.json
  task.yaml
  result.yaml
  decisions/
  evidence/
  locks/
```

The bridge should initially be local and boring. Avoid building a universal multi-agent framework. Build the smallest controller that solves MTJawnny's real coordination loop.

---

## 15. Future deterministic checks

The eventual controller should remove these jobs from both LLMs:
- expected HEAD;
- allowed/forbidden changed paths;
- staged file scope;
- codebook SHA/size;
- selected authority;
- Gate 2 invocation/result;
- registry metrics;
- W6 fingerprint;
- baseline movement;
- unrelated worktree collision detection;
- deterministic output comparison;
- commit scope.

Models should spend reasoning on questions like:

> Is this benchmark population architecture-neutral?

not:

> Did this SHA change?

---

## 16. Authority classes for future automation

Potential future classes:

```text
L0 — mechanical
L1 — implementation-local
L2 — architecture-affecting
L3 — governance / authority / data
L4 — destructive / external publication
```

Suggested policy:
- **L0** may run automatically: deterministic regeneration, formatting, tests.
- **L1** Manager may authorize: probe-local parser correction, negative-control repair, bounded implementation refactor.
- **L2** Captain review: new semantic structure, benchmark-law change, canonical ownership decision.
- **L3** Captain review required: authority selection, baseline governance, evidence-law change, vocabulary ratification.
- **L4** Captain explicit authorization: destructive migration, publication of new authority, remote deletion/pruning.

This is design guidance only until formally implemented.

---

## 17. Core principle

The lesson applies both to Foundry and to its development process:

> Human-readable language is an excellent reasoning and presentation interface, but it is not always the best canonical representation of structured state.

For agent coordination:

> **Structure carries state.**  
> **Prose carries meaning.**  
> **Deterministic software should carry invariants.**  
> **Models should spend reasoning on ambiguity and architecture.**  
> **The Captain retains authority over decisions that matter.**

---

## 18. Current status

This protocol is authorized as a **temporary communication optimization**.

It does NOT:
- change Foundry semantic architecture;
- change AQ4 benchmark law;
- authorize any AQ4 packet;
- change Git authority;
- modify Gate 2;
- authorize a background/autonomous agent loop;
- authorize the full orchestrator build.

Individual work still requires a bounded task contract.

The full bridge/orchestrator should be evaluated at an appropriate architectural stopping point, preferably after the AQ4 architecture ruling and before production retrofit / Stage F.
