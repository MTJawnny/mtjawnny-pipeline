# S10 Worker Contract Refresh — 2026-09-13

Status: **DRAFT CONTRACT / NOT AUTHORIZED BY THIS FILE / DO NOT EXECUTE WITHOUT ISSUE-#1 `T`**

This contract supersedes the old execution assumptions in `docs/architecture/preflight/S10-WORKER-IMPLEMENTATION-CONTRACT-DRAFT-NOT-AUTHORIZED.md` only where the accepted tree has changed. The earlier detailed symbol ownership and conservation design remain supporting evidence.

## Base law

At execution time, the Worker must start from the exact accepted implementation/planning head named by the active GitHub Issue #1 `T`. If measured HEAD differs by even one commit, STOP before mutation.

The planning lineage for this refreshed contract descends from accepted cleanup/conservation head:

`493483aa1d54210c35e1665686a5e0136588da6d`

The final exact S10 base is intentionally supplied by the later Issue-#1 task after all verification/report commits are complete; do not substitute this document's own commit or an older branch tip.

## Governing principle

**PRESERVE TRUTH, NOT PLUMBING.**

S10 dissolves the live `foundry_common` aggregation boundary only to the extent mechanically proven safe. It does not earn credit for making the legacy filename disappear if doing so invents semantic ownership, edits frozen AQ4, changes parser behavior, or breaks loose-script compatibility.

## Refreshed live topology

The 2026-09-13 refresh establishes:

- live `foundry_common` Python importers: **86**;
- archived historical importers: **1** — excluded from migration;
- live externally referenced provider names: **35**;
- provider module responsibilities: **45**;
- provider blob still `21192e3e6b8a1693abfe6a3b993e1014a2d84894`;
- five live AQ4 benchmark importers remain frozen;
- `experiments/foundry_build_reaudit_packet.py` is a retired tombstone and is **not a caller to migrate**.

Normative evidence:

- `docs/architecture/preflight/S10-FOUNDRY-COMMON-CENSUS-REFRESH-2026-09-13.md`;
- `docs/architecture/preflight/objective1/S10-FOUNDRY-COMMON-IMPORTER-SYMBOL-MATRIX.csv` as the historical 87-importer snapshot, with the refresh's exact one-caller subtraction applied;
- `docs/architecture/preflight/objective1/S10-FOUNDRY-COMMON-SYMBOL-MAP.json`;
- `docs/architecture/S10-CARD-TEXT-OWNERSHIP-DECISION-2026-09-11.md`;
- `docs/architecture/S10-S16-CURRENT-PLAN-2026-09-13.md`.

Archive paths must never be counted as implementation callers.

## Hard scope

S10 may:

1. install/lift the already-decided reusable owners required to remove live S10 dependencies;
2. convert eligible `foundry_common` responsibilities to thin compatibility delegation/provider facades;
3. migrate explicitly bounded live caller families from the refreshed 86-importer universe;
4. add conservation tests/negative controls required to prove those moves;
5. retire an individual facade/helper only after caller and bootstrap closure are mechanically demonstrated.

S10 must not:

- change card semantics to fix known parser gaps;
- collapse neutral Oracle normalization and DET synthetic representation;
- alter codebook membership, AG-CLI-01 mutation semantics, or R8.3 activation state;
- resume or rederive AQ4;
- edit the five frozen AQ4 benchmark importers without separate explicit authority;
- begin S11 codebook/store/membership migration;
- begin S12 authority/transport migration;
- begin S13 operator/CLI migration beyond compatibility changes strictly required by an explicitly authorized S10 caller tranche;
- begin S14 AQ4 relocation;
- begin S15 deletion/archive retirement;
- begin S16A/S16B implementation;
- use Bridge v0;
- start Step6;
- merge or move `main`/default branch;
- alter baselines, CR, codebook authority, selected codebook, or W6 fingerprint.

## S10.1 — lift only decided permanent owners

Under differential proof, install the minimum permanent APIs already decided by the ownership evidence:

- `mtj_foundry.corpus.full_oracle_text(card)` preserving exact all-face string/order/empty-text behavior;
- DET-compatible self-reference capability in `mtj_foundry.oracle_text` as a **separate named contract** from neutral N2 normalization;
- neutral modal header/mode-line recognition in `mtj_foundry.oracle_text`;
- neutral roll/die-row recognition in `mtj_foundry.oracle_text`;
- neutral live Level/Class marker recognition in `mtj_foundry.oracle_text`.

Do **not** move `det_scan_texts` synthetic scan composition into neutral Oracle ownership merely to achieve deletion. DET representation remains distinct policy/plumbing unless a later explicit owner decision says otherwise.

Do **not** move delivery/grouping consequences out of `mtj_foundry.mtg.shapes.delivery`.

Known S16A evidence is a conservation warning, not permission to improve behavior in S10. In particular:

- neutral-vs-DET self-reference differs on 1,818 Gate-0 cards;
- current modal recognizers have measured gaps;
- reminder/quote ownership defects exist.

S10 preserves accepted contracts; S16A owns semantic improvement.

## S10.2 — compatibility facades and S7 substitution law

Convert eligible legacy names into thin delegates/provider facades while preserving observable call-time behavior.

Existing exact delegate contracts such as `raw_faces` and `write_json` remain delegates. `gate_passes` may delegate to the permanent Gate0 predicate only after equivalence is re-proven on the selected corpus.

**Mandatory S7 negative control:**

1. construct the provider/consumer;
2. replace the self-reference provider after construction;
3. prove downstream shape extraction observes the replacement;
4. deliberately replace the implementation with a captured/snapshotted provider and prove the control goes RED.

Output-only equality without this falsification is insufficient.

## S10.3 — migrate live caller families only

Use the refreshed 86-live-importer universe. The old 87-importer matrix is a historical input; remove only the retired live generator row before partitioning work.

Refreshed class counts:

- AQ4/frozen benchmark: 5;
- authority/transport: 1;
- codebook or membership mutation: 43;
- gate/check: 3;
- operator/CLI: 9;
- pipeline/batch: 5;
- reporter/census: 5;
- test/negative control: 15.

Scope counts:

- AQ4 frozen: 5;
- legacy executable: 65;
- reporter census: 1;
- test/negative control: 15.

The active `T` may authorize S10 as one bounded transaction or smaller reviewed caller tranches. In either case, do not widen into a caller family owned by a later migration slice merely because its import is inconvenient.

### Frozen AQ4 exception

These five frozen benchmark importers remain byte-unchanged unless the Captain separately authorizes AQ4-file mutation:

- `experiments/aq4_benchmark/aq4_binding.py`
- `experiments/aq4_benchmark/aq4_compare.py`
- `experiments/aq4_benchmark/aq4_pairing.py`
- `experiments/aq4_benchmark/aq4_population.py`
- `experiments/aq4_benchmark/aq4_projection.py`

A thin compatibility surface may legitimately remain for them after ordinary S10 callers migrate.

## S10.4 — prove conservation

Required proof includes, as applicable to each migrated responsibility/caller family:

- selected-corpus full-pop corpus/Gate0/name/full-text differential;
- exact face order and text-join parity;
- exact path-value parity;
- byte-level artifact parity;
- error stderr/exit parity at legacy composition boundaries;
- installed-package importability with no permanent import from `experiments`;
- no new repository-root derivation outside `ProjectPaths`/authorized compatibility shell;
- loose-script/bootstrap behavior where still intentionally supported;
- `sys.path`/import-order negative controls;
- clean-checkout/fresh-clone proof;
- refreshed caller census from `git ls-files` + AST/string-bound provider analysis;
- zero unexplained new importers;
- canonical Gate 2 green under verified runtime inputs;
- deliberate corruption for every new acceptance guard.

The exact project inputs used by the cleanup Gate-2 closeout were:

- selected codebook SHA-256 `6aa6193f8a457ae4c7884e364f519749a9d68b96f7ecedf3fa903bfa4677426c`, size 5,066,147 bytes;
- historical Oracle gzip SHA-256 `b46e0670a8f3fa2d5357ec35ff7f8d58e7c2f9f15db0e27a3b0543672b00c217`, 38,233 raw records;
- decompressed Oracle SHA-256 `5e47e1325a3987db745a941307080830696cbac2f6aa80d8f88f8a6dad90723c`.

If S10 is tested against different required runtime inputs without explicit authority, STOP rather than silently substituting them.

## S10.5 — retire only proven-dead compatibility

A facade/helper may be deleted only after:

- the refreshed graph proves no live caller remains for it;
- dynamic/string-bound callers have been covered;
- no bootstrap prerequisite depends on it;
- relevant negative controls still pass;
- no frozen AQ4 caller loses its allowed compatibility surface.

Do not remove the sibling-path bootstrap until loose-script importability has a separately proven replacement.

Do not force total deletion of `foundry_common` by inventing a permanent owner for true legacy composition, DET synthetic preprocessing, prompt/review composition, or other later-slice behavior. If an active task requires complete deletion but a live responsibility lacks an accepted destination, STOP with the smallest required owner decision.

## Canonical law protections

### R8.3

`docs/ACTIVATED-REGENERATE-SELF-DET-LAW.md` is binding. S10 must not install, activate, auto-route, or infer an active home for `rule:activated-regenerate-self`. A draft pattern/sample/historical generator is evidence only until Captain pattern ratification.

### AG-CLI-01

`docs/MEMBER-ADD-MUTATION-LAW.md` is binding. S10 must not weaken merge-never-overwrite, validation, backup, history, lint, atomic write, SHA reporting, or DET restrictions in any compatibility path it touches. This law is not authority to add an installed mutating CLI.

### W6

`config/registers/family-sweep-known-debt.json` remains the sole machine-enforced known-debt set. The exact six `(kind, subject)` fingerprint must remain unchanged unless the corresponding defect is genuinely fixed and the waiver is reviewed in the same authorized change.

## Mandatory falsification catalog

At minimum demonstrate RED for corruption of:

- path segment/root;
- legacy import precedence where still supported;
- Gate0 eligibility/filter-before-index order;
- exact-name ambiguity/fallback;
- root-only rather than all-face Oracle text;
- face order or join separator;
- neutral N2 substituted for DET self-reference;
- captured provider rather than call-time substitution;
- modal/pawprint/Spree/Tiered recognition relevant to moved contracts;
- die/roll recognition;
- Level/Class markers;
- deleted/reordered DET synthetic variant;
- JSON final LF/encoding/indent;
- permanent import from `experiments`;
- new repository-root derivation;
- one deliberately reintroduced live `foundry_common` caller;
- one archive-only importer deliberately misclassified as live.

A guard that has never been observed RED under its intended corruption is not accepted as a conservation guard.

## Completion condition

S10 is complete only to the exact boundary selected by its active Issue-#1 task. Its result must report:

- exact base and final commit;
- exact changed files;
- caller count before/after and complete remaining caller list;
- the reason for every intentionally retained caller/facade;
- all differential and negative-control results;
- Gate-2 result with verified input identities;
- confirmation that AQ4, R8.3, AG-CLI-01, W6, authority selector, codebook, Bridge v0, Step6, merge, and `main` remained within their controls.

No S10 PASS self-authorizes S11, merge, or any later slice.
