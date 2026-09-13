# Future S15 Worker Contract

> # **DRAFT / NOT AUTHORIZED / MUST BE REVALIDATED AT ACTUAL PRE-S15 ACCEPTED HEAD**

This is a contract shape for a future destructive S15. It is not an active task, does not authorize deletion, and must not be pasted to a Worker unchanged after S10-S14.

```yaml
schema: mtj-task/0
task: REFOUNDATION.S15.LEGACY-RETIREMENT
status: DRAFT_NOT_AUTHORIZED
base: <ACTUAL_ACCEPTED_PRE_S15_HEAD_AFTER_S10_S14>

objective:
  - retire only legacy topology whose callers, truth, provenance, runtime ownership, and successors are mechanically proven conserved
  - archive evidence-bearing legacy material into accepted final archive homes
  - leave permanent package/config/fixtures/authority/ruling truth unchanged

required_preflight_inputs:
  - regenerated S15-OBJECTIVE4-PATH-READINESS-MATRIX at base
  - regenerated S15-OBJECTIVE4-DEPENDENCY-EVIDENCE at base
  - regenerated successor map with all caller classes closed
  - regenerated truth-home matrix with no unresolved unique truth
  - reconciled quarantine ledger and document/ruling topology proof
  - complete ignored/runtime inventory from the actual local environment
  - conservation suite with all required negative controls demonstrated red and unrigged suite green

allow:
  - delete only candidates classified DELETE_SAFE at the actual pre-S15 head
  - remove only legacy paths classified MIGRATED_REPLACED after successor/caller closure is proven
  - move ARCHIVE_EVIDENCE only to predeclared final archive homes with byte/set/provenance conservation
  - make the narrowly pre-authorized .gitignore edit, if and only if its exact semantics were separately accepted by the Manager/Captain before execution

deny:
  - any path classified KEEP_PERMANENT
  - any path classified BLOCKED_LIVE_CONSUMER
  - any path classified BLOCKED_TRUTH_HOME
  - any path classified BLOCKED_UNKNOWN
  - semantic/ruling changes
  - baseline or ratchet movement
  - authority succession/selection changes
  - AQ4 activation or benchmark-law changes
  - Bridge0 use
  - Step6
  - merge/deploy/publication
  - deletion based only on ignored status, filename, age, similar successor name, zero static imports, or zero ruling refs
  - broad staging or cleanup that can absorb unrelated work

invariants:
  accepted_head: <PIN>
  authority_selector_and_selected_object: <PIN>
  codebook_identity: <PIN>
  gate2_semantic_manifest: <PIN_ROWS_COMMANDS_WAIVERS_BASELINES>
  ruling_id_set: <PIN>
  raw_ruling_reference_multiplicity: <PIN_OR_EXPLAINED_DELTA>
  sole_home_and_corroborated_state: <PIN>
  ground_truth_fixture_manifest: <PIN>
  aq4_frozen_evidence_manifest: <PIN_AFTER_S14>
  ignored_runtime_ownership_manifest: <PIN>
  protected_tracked_controls_ignore_status: NOT_IGNORED

required:
  - re-enumerate tracked and ignored/runtime candidate universe before mutation
  - rerun static + dynamic + subprocess/shell + command + workflow + config + direct-open + path-string + authority + baseline + ruling + generated-output consumer proof
  - prove every retired legacy API/path has full caller-class coverage by its permanent successor
  - prove every evidence-bearing path has an equivalent-authority/provenance archive or permanent home
  - compare ruling/document topology setwise before and after
  - run from a pristine checkout with no inherited ignored state
  - prove runtime outputs remain untracked as intended
  - prove tracked selectors/baselines/fixtures/controls are not hidden by .gitignore
  - run all ten Objective-4 conservation negative controls and retain rigged-red evidence
  - run unrigged conservation suite and Gate 2 semantic-manifest comparison
  - produce exact changed-path report and classify every deletion/move by the revalidated matrix

stop:
  - base differs from authorized pre-S15 head
  - any candidate classification differs materially from the revalidated matrix without Manager review
  - any live/static/dynamic/command/workflow consumer survives
  - unique or insufficiently preserved truth/provenance is found
  - ignored/runtime ownership is unknown
  - clean checkout needs undeclared local state
  - ruling ID/reference/sole-home topology changes unexpectedly
  - Gate-2 row, command, waiver, baseline, or semantic output changes beyond topology-only expectations
  - .gitignore would track runtime output or hide a protected tracked control
  - authority/codebook/AQ4/baseline/ruling semantics move
  - unrelated worktree drift

commit:
  allowed: <CAPTAIN_TO_DECIDE>
  subject: "refoundation: retire conserved legacy experiments topology"
  scope: <REGENERATED_EXACT_ALLOWLIST>

next:
  authorized: NONE

return:
  schema: mtj-result/0
  include:
    - exact base/head and commit if authorized
    - deleted/moved paths by revalidated classification
    - archive byte/set conservation proof
    - caller closure proof
    - ruling/document topology before/after
    - ignored/runtime ownership before/after
    - all negative-control red evidence plus unrigged green results
    - Gate-2 semantic-manifest before/after
    - authority/codebook/baseline/AQ4 conservation
    - discrepancies and any decision_required
```

## Regeneration rule

The placeholders are intentional. The actual S15 Manager must regenerate this contract after S10-S14, using the accepted head that immediately precedes destructive S15. Objective-4 classifications measured at `9f92039e...` are evidence for planning only and must never be copied forward as deletion authorization.