```yaml
schema: mtj-task/1
task: BRIDGE.V0.BUILD
base_branch: refoundation-manager-bootstrap-2026-08-28
base: ec3eb8f75a1bf889e8998bec353212880228d808
status: READY

objective:
  - build the first local automation bridge between a model-driven ChatGPT/OpenAI Manager and Claude Code Worker using GitHub as durable state/control plane
  - eliminate Captain as routine message courier while preserving Captain-only decision boundaries
  - make Manager and Worker sessions disposable: one fresh model invocation per task/review, reconstructed from durable GitHub/repo state

scope:
  kind: infrastructure_only
  location: "isolated bridge tooling; do not refactor Foundry/AQ4 or depend on the final P0 repository architecture being ratified"
  delivery: "dedicated branch + draft PR targeting refoundation-manager-bootstrap-2026-08-28; DO NOT MERGE"

captain_authorization:
  mtj_worker: APPROVED
  mtj_manager_model_service: APPROVED
  unattended_mechanical_cycles_after_validation: APPROVED
  captain_boundaries_remain: true

known_local_state:
  canonical_dirty_worktree: /Users/jawnny/Projects/mtjawnny-pipeline
  note: "main has one modified tracked registry + nine untracked docs. Do not use that dirty worktree for bridge implementation."

required_preflight:
  - fetch remote refs
  - verify bootstrap branch resolves exactly to ec3eb8f75a1bf889e8998bec353212880228d808
  - inspect `claude --help` / installed Claude Code capabilities rather than assuming CLI flags
  - inspect `gh --version` and `gh auth status` without exposing credentials
  - inspect local Python/runtime tooling
  - confirm no OPENAI_API_KEY or other secret is printed or persisted

worktree_rule:
  - create a separate clean git worktree or clean clone derived from the bootstrap branch
  - never checkout/switch/reset/clean the Captain's existing dirty main worktree
  - preserve its tracked/untracked bytes exactly

architecture_requirements:
  shared:
    - GitHub Issues are task/decision ledger
    - branches + PRs are proposed mutation evidence
    - comments carry structured task/result/review events
    - one active Worker task at a time
    - every task pins an accepted base SHA
    - stale base/state mismatch => STOP
    - no model self-authorizes semantic/authority decisions
    - secrets only via environment/existing auth; never committed or logged
    - all external/model adapters mockable for offline tests
    - `--once` and `--dry-run` modes required before daemon/poll mode

  worker:
    command: mtj-worker
    required_behavior:
      - discover exactly one READY worker task
      - verify base SHA/state before execution
      - use a fresh isolated worktree/branch per mutating task
      - start a FRESH Claude Code invocation for each task; do not rely on prior Claude conversation state
      - provide Worker bootstrap + issue contract + required referenced state to Claude
      - prefer wrapper-owned git/GitHub lifecycle where practical; model should not receive broader mutation authority than task requires
      - validate changed paths against task allow/deny where machine-readable
      - capture commands/tests/result evidence
      - push task branch and open draft PR for mutation tasks
      - post `mtj-result/1`
      - stop after one task in `--once` mode
      - never touch Captain dirty main worktree

  manager:
    command: mtj-manager
    implementation_model: "OpenAI API Responses API; model configurable via environment/config. Current recommended reasoning/coding default may be GPT-5.6 Sol, but do not make long-term correctness depend on a hard-coded model name."
    required_behavior:
      - run a FRESH model invocation for each review; no conversational continuation required
      - reconstruct context from refoundation bootstrap/state + task issue + Worker result + PR diff + tests/evidence
      - model outputs strict structured `mtj-review/1`
      - verdict domain: PASS | REPAIR | CAPTAIN_DECISION_REQUIRED | STOP
      - model must not directly execute shell/git/GitHub mutations
      - deterministic local policy layer validates review schema and autonomy boundary before any GitHub write
      - PASS may create/activate the next already-defined mechanical task only when policy allows
      - REPAIR may create one bounded repair task when no Captain decision is needed
      - CAPTAIN_DECISION_REQUIRED posts a compact decision packet and HALTS automation
      - STOP halts automation
      - never auto-merge PRs in v0

  autonomy_policy:
    manager_may_auto_authorize:
      - mechanical implementation consistent with ratified target architecture
      - internal refactoring
      - path/import migration
      - test fixes that restore specified behavior without weakening tests
      - deterministic migration repairs
      - documentation/reference rewrites mechanically implied by accepted moves
    captain_required:
      - Foundry semantic truth change
      - authoritative codebook-content change
      - authority succession change
      - frozen AQ4 benchmark-truth change
      - new semantic vocabulary/law
      - product architecture choice not already ratified
      - weakening/removing a conservation or validation gate
      - deletion/extraction when unique systematic value is ambiguous
      - conflict between durable authorities

  orchestration:
    - GitHub polling is acceptable for v0; webhooks are not required
    - keep polling logic boring and inspectable
    - avoid uncontrolled Manager<->Worker loops
    - enforce maximum cycle/repair limits and halt on repeated failure
    - provide an operator command that runs one complete Manager/Worker cycle at a time before unattended loop mode is enabled

credentials:
  github: "reuse existing gh authentication where possible; do not add a token file"
  claude: "reuse existing Claude Code authentication; discover supported noninteractive invocation locally"
  openai: "OPENAI_API_KEY or standard OpenAI client environment configuration; never store the key"

openai_note:
  - use the current OpenAI Responses API / official SDK rather than legacy chat-specific architecture
  - model name should be configurable (for example MTJ_MANAGER_MODEL) so model upgrades do not require architectural changes

implementation_quality:
  - typed/validated protocol schemas
  - clear finite-state transitions
  - idempotent GitHub operations where practical
  - structured logs with secret redaction
  - crash recovery: durable GitHub state must let a restarted process determine what happened
  - explicit claim/lock mechanism so two workers cannot execute the same issue
  - no important execution state only in RAM

required_tests:
  unit:
    - task parser/schema validation
    - result parser/schema validation
    - review parser/schema validation
    - autonomy policy PASS/REPAIR/CAPTAIN/STOP routing
    - state/base mismatch halt
    - allow/deny path enforcement
    - secret redaction
    - duplicate-claim/idempotency behavior
  integration_offline:
    - fake GitHub adapter + fake Claude adapter + fake OpenAI adapter
    - successful read-only task
    - successful mutation task -> draft PR -> review PASS
    - Worker failure -> REPAIR path
    - semantic change request -> CAPTAIN halt
    - stale base -> STOP before Claude execution
    - restart halfway through cycle reconstructs state without conversation memory
    - repeated repair limit halts rather than loops forever
  live_read_only:
    - may read Issue #1/bootstrap branch through gh as smoke test
    - must not invoke a real autonomous mutation cycle during this task

required_docs:
  - operator README
  - architecture/state-machine diagram in text
  - credential/environment setup
  - commands for `--dry-run`, `--once`, and future polling mode
  - explicit Captain boundaries
  - recovery procedure after process/session crash
  - how a fresh ChatGPT/OpenAI Manager and fresh Claude session reconstruct state

prohibited:
  - Foundry/AQ4 semantic changes
  - repository reconstruction work
  - modifying main
  - modifying refoundation-baseline-2026-08-28
  - modifying Captain's existing dirty local worktree
  - merging its own PR
  - enabling auto-merge
  - storing API keys/tokens
  - autonomous production run
  - silently changing Issue #1 architecture conclusions

stop:
  - bootstrap base differs
  - safe separate worktree/clone cannot be established
  - Claude Code cannot be invoked noninteractively without unsafe credential handling
  - GitHub lifecycle requires credentials to be stored in repo
  - Manager cannot be made policy-gated between model output and mutations
  - implementation would require ratifying any P0.1 D1-D9 architecture choice

return:
  schema: mtj-result/1
  include:
    - exact implementation branch
    - draft PR number
    - changed files
    - service architecture
    - discovered Claude CLI invocation mode
    - test counts/results
    - live read-only smoke-test result
    - credential requirements remaining for Captain
    - known limitations
    - decision_required

next:
  authorized: NONE
```

## Manager implementation note

This bridge is temporary/refoundation infrastructure and must not force the final MTG Thesaurus package/directory architecture. Prefer isolation and replaceability over premature integration with Foundry.

The Manager service is an API-driven orchestrator/reviewer, not this exact ChatGPT UI conversation. Durable project state is what makes fresh Manager invocations equivalent enough for mechanical review.

Build both services in this task, but validate them in layers: shared protocol/state -> `mtj-worker` -> `mtj-manager` -> offline closed-loop harness -> live read-only smoke test. Do not run a live autonomous mutation loop yet.
