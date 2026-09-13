# DRAFT / NOT AUTHORIZED — S10 `foundry_common` implementation contract

**Status: DRAFT / NOT AUTHORIZED / DO NOT EXECUTE**

This contract is derived from the exact accepted-head Objective-1 census. It is not an active `k: T`, does not authorize a Worker, and must not be executed until durable Issue #1 authority explicitly selects S10 implementation.

## Fixed base and required inputs

Implementation must start from the accepted implementation head selected by the then-current valid Issue-#1 checkpoint. The Objective-1 evidence measured `9f92039eb9c7132a351576c31472eb30a2957a67`; if accepted `h` changes, STOP and rebase/re-run the census before using this contract.

Before semantic-equivalence stages, verify the repository-selected Oracle corpus and runtime codebook identities. Do not use an unverified “latest” file. If either required input is absent, evidence that depends on it is STOPPED, not waived.

## Hard scope

S10 decomposes the legacy `foundry_common` aggregation boundary under conservation. It may lift already-decided permanent ownership and migrate authorized caller families. It must not alter semantic meaning, improve known parser gaps, collapse N2/DET policy, resume AQ4, change authority/baselines/CR, start S11-S16, use Bridge v0, start Step6, merge, deploy or publish.

## Ordered stages

### S10.1 — Install/lift only the already-decided permanent owners

Under full differential proof, add the smallest permanent APIs required by the binding ownership decision:

- `mtj_foundry.corpus`: exact `full_oracle_text(card)` contract;
- `mtj_foundry.oracle_text`: DET-compatible self-reference capability as a **separate named contract** from neutral N2 normalization;
- `mtj_foundry.oracle_text`: neutral modal-header/mode-line, roll/die-row and live Level/Class marker recognition.

Do not move DET synthetic scan composition into neutral Oracle ownership. Do not move delivery/grouping consequences out of `mtj_foundry.mtg.shapes.delivery`.

Acceptance: full selected-population differential where applicable; exact list/string/order behavior; installed-package import test; zero imports from `experiments` in permanent package; no new repository-root derivation. Every guard runs a private corruption that proves it goes red.

### S10.2 — Keep compatibility facades and preserve S7 call-time substitution

Convert eligible `foundry_common` semantic names into thin delegation/provider facades without changing callers yet. Existing exact delegates (`raw_faces`, `write_json`) remain delegates. `gate_passes` delegates to the permanent Gate0 predicate only after full-pop equivalence is re-confirmed.

For shape delivery, preserve observable **call-time** provider resolution. Mandatory negative control: construct the provider/consumer, monkeypatch the self-reference provider afterwards, and prove downstream extraction uses the replacement. A deliberately captured/snapshotted provider must fail.

### S10.3 — Migrate caller families from the measured 87-importer matrix

Migrate only caller families explicitly authorized by the active task. Use `S10-FOUNDRY-COMMON-IMPORTER-SYMBOL-MATRIX.csv` as the partition source; do not rediscover by ad hoc grep.

Suggested order: tests/negative controls needed to prove the new owners; ordinary legacy executable consumers of already-permanent path/artifact/corpus primitives; semantic consumers covered by S10.1; remaining legacy composition consumers only when their target boundary is explicit.

**AQ4 exception:** the five frozen `experiments/aq4_benchmark/*` consumers remain byte-unchanged unless separate durable authority permits their migration. A compatibility facade may therefore remain even after ordinary callers move.

### S10.4 — Prove topology, bootstrap and failure conservation

Required checks:

- full-pop corpus/Gate0/name/full-text differentials;
- exact path-value parity;
- byte-level artifact parity;
- error stderr/exit parity for legacy composition boundaries;
- installed-package behavior with no `experiments` dependency;
- no new root derivation outside `ProjectPaths`;
- `sys.path`/import-order negative controls;
- clean-checkout/fresh-clone behavior;
- caller census regenerated from `git ls-files` + AST with zero unexplained additions;
- canonical Gate 2 green under verified required inputs.

### S10.5 — Retire only proven-dead compatibility pieces

Delete an individual legacy facade/helper only after the measured graph proves zero live callers and no bootstrap prerequisite depends on it. Do not remove the legacy sibling-path bootstrap until loose-script importability has a separately proven replacement. Do not remove `CardTextRules` merely because permanent structural functions exist; remove it only after no live compatibility role remains and the S7 substitution negative control still passes at the new seam.

Do not force complete deletion of `foundry_common` by inventing a permanent owner for DET-specific synthetic preprocessing, review/prompt composition, or other true legacy boundaries. If complete deletion is a task requirement and no explicit owner exists, STOP with the smallest owner decision required.

## Mandatory falsification suite

Each acceptance guard must have a paired corruption: wrong path segment/root; reordered/removed sys.path insertion; changed Gate0 value; pre-filter name index; fuzzy name fallback; root-only Oracle text; reordered face join; N2 substituted for DET self-reference; captured provider attribute; modal/pawprint/Spree/die/Level/Class corruption; deleted/reordered DET synthetic variant; changed JSON final LF/encoding/indent; permanent import from `experiments`; new root derivation; reintroduced `foundry_common` caller.

A check with no demonstrated red state is not a conservation guard.

## Completion condition

S10 implementation is complete only to the boundary explicitly authorized by its future active task. It may legitimately end with a thin legacy compatibility boundary for frozen AQ4 or other separately governed legacy composition. It must report exact remaining callers and why they remain. No evidence or implementation commit self-authorizes merge or the next slice.
