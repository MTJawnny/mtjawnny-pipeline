# S15 Objective 4 Result

Status: **COMPLETE_EVIDENCE**  
Mission: S15 deletion-readiness preflight only. No deletion, move, migration, repair, merge, authority change, AQ4 work, Bridge0 use, Step6, or Objective 5 activation is authorized by this result.

## Heads and lineage

- Measured accepted implementation head: `9f92039eb9c7132a351576c31472eb30a2957a67`
- Evidence branch: `preflight/objective4-s15-deletion-readiness-2026-09-12`
- Evidence branch base: `6b7e1fa2224be610b09cc00e9838d27658f59583` (completed Objective-3 evidence lineage)
- Cleanup evidence branch/head inspected: `cleanup/obsolete-doc-quarantine-2026-09-11` / `fcb11e19296209aecac4c8b3526be39bcce0196a`
- Evidence head before this result file: `dfdbf8268584bf1bc3a1030d2ba8a65883be0188`
- Final evidence head rule: the Git commit containing this result is the final Objective-4 evidence head; its exact SHA is recorded durably in the Issue #1 Objective-4 result/checkpoint because a file cannot contain its own commit SHA without changing that SHA.

Accepted implementation `h` is measured separately from the evidence branch. Evidence-branch source is not treated as accepted implementation truth.

## Completion verdict

Objective 4 met its preflight completion bar. A future S15 Manager now has a setwise candidate model, dependency evidence, successor map, truth/provenance dispositions, quarantine reconciliation, runtime/generated-state map, falsifiable conservation design, explicit blockers, and a draft destructive contract.

This is **not** deletion authorization. Every classification must be regenerated or revalidated at the actual accepted pre-S15 head after S10-S14.

## Candidate census

The accepted head contains **107 tracked files under `experiments/**`**. Every one is represented in the readiness matrix. The matrix also includes implicated permanent/runtime/quarantine surfaces for a total of **127 candidates**.

| Classification | Count |
|---|---:|
| `KEEP_PERMANENT` | 16 |
| `MIGRATED_REPLACED` | 1 |
| `ARCHIVE_EVIDENCE` | 45 |
| `DELETE_SAFE` | 0 |
| `BLOCKED_LIVE_CONSUMER` | 29 |
| `BLOCKED_TRUTH_HOME` | 21 |
| `BLOCKED_UNKNOWN` | 15 |

Important interpretation: **no current tracked `experiments/**` file is classified `DELETE_SAFE`.** This is the expected consequence of measuring before S10-S14, not an Objective-4 failure. The only high-confidence `MIGRATED_REPLACED` legacy namespace is `experiments/moves/**`, whose tracked behavior fixtures were already relocated to `tests/fixtures/ground_truth/**` and whose old tracked namespace is absent.

## Major dependency findings

1. Objective 3 confirms that `foundry_common.py`, `foundry_det_pass.py`, `tier_engine.py`, and multiple compatibility wrappers are still live policy/product surfaces at accepted `h`.
2. Static import search is insufficient. Tracked tests/analyzers explicitly model path loaders, module-by-string loading, legacy facades, bootstrap paths, and transitive consumers.
3. `.claude/commands/triage-alpha.md`, `triage-beta.md`, and `triage-emit.md` still name legacy modules and `experiments/out` operational paths, making S13 command repair a concrete S15 prerequisite.
4. The accepted workflow `.github/workflows/build.yml` has no direct `experiments/**` invocation. That is a useful negative result, not proof that no other dynamic consumer exists.
5. A similarly named permanent module is never treated as migration proof. Retirement requires all caller classes to be covered plus behavioral/conservation evidence.

## Truth and provenance findings

- `tests/fixtures/ground_truth/**`, permanent config/selectors/baselines, `src/mtj_foundry/**`, and ruling-registry guard surfaces are permanent truth/control homes.
- AQ4 benchmark/precommit/holdout/binding/projection artifacts under `experiments/**` remain unique frozen truth/provenance and are `BLOCKED_TRUTH_HOME` until S14 proves conservation.
- Measurement scripts/memos and one-off semantic/codebook mutation executors/verifiers are `ARCHIVE_EVIDENCE`, not deletion candidates, because summaries do not preserve equivalent provenance.
- The ruling registry/document topology remains a live conservation concern. Sole-home, corroborated, raw-reference multiplicity, and known false-positive state must be preserved setwise.

## Quarantine reconciliation

The active cleanup ledger's 12 quarantined/tombstoned items reconcile as:

- **8**: move to final history/archive home;
- **4**: safe for eventual deletion only after prerequisites and actual pre-S15 revalidation;
- **0**: preserve indefinitely as the final disposition at this stage;
- **0**: newly restore from the currently quarantined 12.

The ledger's correction history is retained as an adversarial control: twelve handoffs were initially moved using `deletable=yes`; nine were later restored after ruling references were discovered. Therefore `deletable` and `zero ruling references` are explicitly non-equivalent. Additional withheld documents remain blocked where sole-home/corroborated ruling value persists.

## Generated/runtime findings

The existing output census reports:

- 3,321 known ignored files under `experiments/out/**`;
- 110 distinct referenced output path shapes;
- 9 unresolvable dynamic shapes;
- 31 exact candidates still tagged `UNKNOWN_REVIEW`;
- critical ignored paths serving as authority mirrors, acceptance controls, frozen benchmark inputs, and governance/incident evidence.

This GitHub-side session cannot inspect arbitrary untracked/ignored local bytes. Accordingly `experiments/out/**` is `BLOCKED_UNKNOWN` as a wildcard. Ignored is not disposable. A clean-checkout/local ignored-state audit is mandatory before destructive S15.

At accepted `h`, `.gitignore` ignores `experiments/out/` but does **not** ignore `var/`, even though permanent path policy anticipates runtime ownership under `var/**`. Any later ignore edit must prove both directions: runtime output does not become tracked, and tracked controls/baselines/fixtures do not become hidden.

## Blockers

The blocker register contains **13** explicit blockers. They cover S10, S11, S12, S13, S14, ignored-state visibility, unresolved dynamic output shapes, future `.gitignore` ownership, ruling/document topology, the still-live tier-engine product/differential peer, clean-checkout proof, cleanup sole-home truth, and mandatory post-S10-S14 revalidation.

Blockers are an expected Objective-4 output. A future destructive S15 may proceed only after every blocker is mechanically cleared or explicitly decided by the Captain under a later authorized contract.

## Conservation / negative controls

Ten required negative-control designs are specified, covering:

1. a hidden tracked caller;
2. a live fixture misidentified as history;
3. loss of a sole-home ruling;
4. deletion of the only provenance for permanent semantic behavior;
5. stale command/workflow paths;
6. retirement before successor caller coverage;
7. `.gitignore` begins tracking runtime output;
8. `.gitignore` hides a tracked control/baseline;
9. clean-checkout success depends on local ignored state;
10. deletion changes Gate-2/verification semantics rather than topology only.

**New Objective-4 rigged-red executions: 0/10. Status: UNPROVEN until the actual pre-S15 harness demonstrates every control can go red.** Existing tracked guards/tests provide antecedents for several hazard classes, but this preflight does not misrepresent those antecedents as execution of the future destructive S15 suite.

## Deliverables

1. `S15-OBJECTIVE4-PATH-READINESS-MATRIX.json`
2. `S15-OBJECTIVE4-DEPENDENCY-EVIDENCE.json`
3. `S15-OBJECTIVE4-SUCCESSOR-MAP.json`
4. `S15-OBJECTIVE4-TRUTH-HOME-MATRIX.json`
5. `S15-OBJECTIVE4-QUARANTINE-RECONCILIATION.json`
6. `S15-OBJECTIVE4-GENERATED-RUNTIME-INVENTORY.json`
7. `S15-OBJECTIVE4-CONSERVATION-TEST-DESIGN.md`
8. `S15-OBJECTIVE4-BLOCKERS.json`
9. `S15-OBJECTIVE4-WORKER-CONTRACT-DRAFT.md`
10. `S15-OBJECTIVE4-RESULT.md`

The Worker contract is prominently marked:

**DRAFT / NOT AUTHORIZED / MUST BE REVALIDATED AT ACTUAL PRE-S15 ACCEPTED HEAD**

## Final verification

Before writing this result, comparison of the evidence branch to its base showed exactly nine added files, all under `docs/architecture/preflight/s15/`, and no source/runtime/test/`.gitignore`/authority/AQ4 mutation. This result is the tenth documentation/evidence file.

The cleanup branch was re-read and remained exactly at `fcb11e19296209aecac4c8b3526be39bcce0196a`. Issue #1 still showed Objective 4 as the active evidence-only task with accepted `h` unchanged at `9f92039e...`, controls `{AQ4:P, BRIDGE0:U, STEP6:N, MERGE:N}`, and Objective 5 inactive. A final post-result branch comparison and durable Issue checkpoint are required immediately after this file is committed.

## Routing

Objective 4 is complete as evidence. The next state is **Captain review/selection**. Objective 5 remains `PLANNED_NOT_ACTIVE` and is not self-authorized.