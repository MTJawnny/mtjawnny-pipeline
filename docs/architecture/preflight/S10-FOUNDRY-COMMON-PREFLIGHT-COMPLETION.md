# Objective 1 — S10 `foundry_common` preflight completion

**Status:** COMPLETE PREFLIGHT EVIDENCE — S10 IMPLEMENTATION NOT AUTHORIZED  
**Accepted implementation head measured:** `9f92039eb9c7132a351576c31472eb30a2957a67`  
**Provider blob:** `experiments/foundry_common.py` = `21192e3e6b8a1693abfe6a3b993e1014a2d84894`  
**Authority:** Captain direction + durable Issue #1; this document changes no runtime/source behavior.

## Result

The earlier Objective-1 STOP was correct at the time and is now superseded **for preflight completeness only**. The Captain-approved card-text ownership decision removed the prior six-rule ownership blocker. This run re-measured the exact accepted implementation head instead of carrying forward the historical “roughly 39” or stale “83 importers” anchors.

Current accepted-head measurements are:

- tracked files: **430**;
- tracked Python files: **171**, all **171** parsed successfully, **0** parse errors;
- tracked Python importers of `foundry_common`: **87**;
- externally referenced module-level `foundry_common` names: **35**;
- total module-level responsibilities defined by `foundry_common`: **45** = 35 externally referenced + 10 internal-only/load-bearing names;
- tracked text-like files mentioning `foundry_common`: **147**, of which **143** are outside archive/history;
- filesystem-vs-tracked Python cross-check: **0** untracked Python files and **0** tracked Python files missing on disk.

The machine-readable census and importer matrix are normative for exact caller lists. The human summary below does not replace them.

## Exact methodology and completeness proof

A read-only scanner was executed in GitHub Actions after a detached checkout of the exact accepted head. The tracked universe came from `git ls-files -z`, not filesystem grep. Every tracked `.py` file was parsed with Python AST. The scanner records direct imports, `from ... import ...`, module aliases and qualified attributes, statically discoverable dynamic imports/`getattr`, and string-named provider attributes when the string is an actual `foundry_common` module-level name. That last rule captures S7's `CardTextRules` private regex contract. A separate literal scan covers tracked commands/docs/contracts without treating historical prose as executable. `Path.rglob('*.py')` was independently compared with the tracked Python set. There were no parse errors or universe mismatches.

Raw evidence hashes:

- `S10-FOUNDRY-COMMON-CENSUS.json`: `11463eac388849ea8fa527bb239e13ea017179817c0dd314bc3c637563d73cc9`;
- `S10-FOUNDRY-COMMON-IMPORTER-SYMBOL-MATRIX.csv`: `0ec96b701668730522e44d0402015df0cd943140e033b753c0544924008117e0`;
- clean-runner Gate-2 transcript: `4f6b9c9fbff216f92f2908baee1503476db1cfa429a78102c74c03a312f32339`.

The importer responsibility distribution is: **AQ4/frozen benchmark=5**, **authority/transport=1**, **codebook or membership mutation=43**, **gate/check=4**, **operator/CLI=9**, **pipeline/batch=5**, **reporter/census=5**, **test/negative control=15**. Scope distribution is: **aq4_frozen_benchmark=5**, **legacy_executable=66**, **reporter_census=1**, **test_negative_control=15**.

## Bootstrap and side-effect map

Importing `experiments/foundry_common.py` is **not** side-effect free. It resolves its own repository root from `__file__`, conditionally prepends `<root>/src` to `sys.path`, constructs `ProjectPaths`, then unconditionally prepends the legacy `experiments/` sibling path at index 0 before importing permanent corpus/artifact modules. The accepted source explicitly says that legacy sibling insertion remains load-bearing. The permanent `mtj_foundry.paths` owner deliberately does **not** do import-time discovery or mutate `sys.path`; therefore the bootstrap is compatibility plumbing, not domain ownership.

`ProjectPaths` owns the actual path/layout vocabulary. `REPO_ROOT`, output/config aliases and review/data paths in `foundry_common` are compatibility aliases. They do not themselves perform I/O. `load_corpus` reads the selected legacy corpus path through permanent `mtj_foundry.corpus.load_cards`, translates `CorpusLoadError` into the historical `STOP — ...` stderr line and `sys.exit(1)`, then builds the permanent name index. `load_corpus_gated` applies Gate #0 and rebuilds the index. `halt` is the process-exit adapter and must not migrate into ordinary library APIs.

This distinction is binding for S10: preserve observable loose-script/operator compatibility only where it is still intentional; do not preserve root derivation or `sys.path` plumbing as permanent architecture merely because current scripts rely on it.

## Importer × symbol matrix

The exact 87-importer graph is `S10-FOUNDRY-COMMON-IMPORTER-SYMBOL-MATRIX.csv`. It contains one row per importer/symbol pair, the mechanically observed reference kinds and line numbers, and importer classifications. Five importers are frozen AQ4 benchmark code; fifteen are tests/negative controls. A future S10 task must partition migration by these measured caller families rather than rediscovering them.

**Important frozen-evidence boundary:** AQ4 remains paused. The five `experiments/aq4_benchmark/*` consumers are evidence callers, not permission to edit/re-run AQ4. Any S10 implementation must either leave a compatibility surface for them or obtain explicit authorization before changing their frozen bytes.

## Duplicate / equivalence register

The detailed per-symbol register is `S10-FOUNDRY-COMMON-SYMBOL-MAP.json`. The highest-risk relationships are:

| Legacy responsibility | Permanent/other capability | Relationship / ruling |
|---|---|---|
| path/config aliases | `mtj_foundry.paths.ProjectPaths` | compatibility aliases; delete after caller migration |
| `load_corpus` | `corpus.load_cards` + `build_name_index` | compatibility wrapper; legacy exit adaptation is intentionally outside permanent library |
| `gate_passes` | `corpus.is_gate0_eligible` | behaviorally equivalent duplicate; permanent owner documents VALUE_EXACT, future S10 reruns full-pop differential |
| `raw_faces` | `corpus.card_faces` | exact delegation; Objective-3 full-pop face comparison was 32,557/32,557 equal |
| `full_oracle_text` | no permanent function yet | owner is `mtj_foundry.corpus`; permanent owner needs lift |
| DET `canonicalize_self_reference` | `oracle_text.normalize_self_references` | **divergent contract**, not an equivalence target; Objective 3 measured 1,818 Gate-0-card divergences |
| modal/die/roll + live Level/Class recognizers | delivery/locality consumers | neutral printed-text recognition belongs in `mtj_foundry.oracle_text`; delivery keeps semantic grouping/consequences |
| `det_scan_texts` / synthetic expansion | no permanent DET module | legacy DET-specific representation; deliberately not assigned to neutral Oracle or delivery ownership |
| `_extract_faces` | `corpus.card_faces` | differential overlap: review projection carries different schema/details, including loyalty |
| `write_json` | `infra.artifact.write_json` | exact delegation; permanent byte contract already exists |

Objective-3 evidence is supporting evidence, not accepted implementation. It measured the selected corpus at 38,233 raw records / 32,557 Gate #0 cards / 33,393 Gate #0 faces with decompressed SHA-256 `5e47e1325a3987db745a941307080830696cbac2f6aa80d8f88f8a6dad90723c`. In that evidence, neutral self-reference equaled its legacy neutral peer on all 32,557 Gate #0 cards, while neutral-vs-DET differed on 1,818. It also found known modal-structure gaps (69 genuine mode lines missed, 28 nonmodal lines invented; DET synthetic expansion covered 1,821/1,824 certified mode lines). S10 must therefore preserve contracts rather than “simplifying” them into one parser.

## Ownership table

Every one of the 45 live module-level responsibilities is classified exactly once in the symbol map. Current counts are: **DELETE_AFTER_CALLER_MIGRATION=13**, **LEGACY_COMPOSITION_BOUNDARY=19**, **PERMANENT_OWNER_NEEDS_LIFT=13**. There are **0** entries assigned `BLOCKED_ARCHITECTURE_DECISION_REQUIRED` at this preflight stage because genuine legacy composition boundaries are allowed to remain legacy boundaries rather than being forced into invented permanent modules.

Binding lifts are:

- `full_oracle_text` -> `mtj_foundry.corpus`;
- DET-compatible self-reference capability (token/candidate/canonicalization contract) -> `mtj_foundry.oracle_text`, **distinct from N2**;
- modal header/mode-line, roll/die-row, and mechanically live Level/Class neutral structural recognition -> `mtj_foundry.oracle_text`;
- delivery remains owner of delivery/grouping consequences;
- DET synthetic scan representations remain the DET policy's responsibility, not neutral Oracle structure.

A future task that insists on permanently relocating the DET-specific composition itself must STOP and obtain an explicit owner decision; this preflight will not invent a `det` module to make the table look tidy.

## Ownership-bloat audit

`foundry_common` has high fan-in because it is a legacy aggregation boundary, not because it semantically owns every concept. `mtj_foundry.mtg.shapes.delivery` is also a visible consumer of Oracle structure, but its semantic ownership is delivery/routing consequence, not neutral printed-text recognition. Likewise `corpus` owns face/corpus mechanics, not review schema or DET synthetic representation. S10 must ask “semantic owner or visible consumer?” before every lift. This evidence does not authorize S16A or broaden parser ownership.

## Risk register

1. **Stale graph facts:** historical 39/83 figures are not current; exact values are 45/35 and 87 as described above.
2. **Import precedence:** changing/removing legacy `sys.path` insertion early can resolve sibling modules differently without changing call sites.
3. **S7 substitution:** capturing card-text primitives by value reintroduces the WB4 failure family. Observable call-time provider lookup is a conservation law.
4. **DET/N2 collapse:** 1,818 measured divergences make an unreviewed substitution semantically unsafe.
5. **Known modal gaps:** Objective-3 evidence proves current recognizers are not a gold definition; migration must preserve accepted behavior while any semantic improvement is separately authorized.
6. **Private names are public in practice:** S7 string resolution and guards consume private regex/helpers; renaming them before caller migration breaks live contracts.
7. **AQ4 frozen callers:** five current importers may require compatibility retention; migration authority is not AQ4 authority.
8. **Gate #0 population drift:** filtering/index order/count must remain exact; an index built before filtering can resolve excluded cards.
9. **Failure semantics:** legacy CLI callers rely on stderr+exit; permanent libraries must not inherit process exits.
10. **Artifact bytes:** forty callers still rely on the exact JSON byte contract.
11. **Review projection:** `_extract_faces` is not a drop-in alias for `corpus.card_faces`.
12. **Input availability:** the clean GitHub runner lacks repository-external runtime inputs, but this execution session does have the project-source Oracle corpus. Its compressed SHA-256 is `b46e0670a8f3fa2d5357ec35ff7f8d58e7c2f9f15db0e27a3b0543672b00c217`; independent decompression produced SHA-256 `5e47e1325a3987db745a941307080830696cbac2f6aa80d8f88f8a6dad90723c`, 38,233 raw records, 32,557 Gate #0 cards, 5,676 exclusions, and 33,393 Gate #0 face records. This exactly matches the repository-selected Objective-3 corpus identity. The runtime codebook remains unavailable to the clean runner, so canonical Gate 2 still cannot be honestly reported green from that run.

## Gate 2 / input identity limitation

The canonical Gate-2 command was executed from the exact accepted head on a clean GitHub runner. It exited 1 because that runner lacked repository-external runtime inputs: the transcript records missing `data/raw/oracle-cards.jsonl.gz` and `experiments/out/foundry/codebook.js` failures. This is **not** accepted as a semantic regression and is **not** reported as green. No baseline or guard was relaxed.

The Oracle-corpus half of that limitation is resolved for this execution session. The project sources contain `data_snapshots_2026-07-03_oracle-cards.jsonl.gz`; its compressed SHA-256 is `b46e0670a8f3fa2d5357ec35ff7f8d58e7c2f9f15db0e27a3b0543672b00c217`. Independent streaming decompression measured SHA-256 `5e47e1325a3987db745a941307080830696cbac2f6aa80d8f88f8a6dad90723c`, 38,233 raw records, 32,557 Gate #0 cards, 5,676 exclusions and 33,393 Gate #0 face records. Those values exactly match the selected corpus identity and population used by completed Objective-3 evidence, so Objective-3 full-pop differentials may be used as supporting evidence for the same input rather than treated as an unknown corpus.

The remaining clean-runner blocker for canonical Gate 2 is the runtime codebook/other generated runtime state, not the Oracle corpus. A future S10 implementation must still verify every supplied runtime identity before claiming Gate-2 green.

## S10 conservation and negative-control design

Every future guard must demonstrate that it can fail. The draft implementation contract binds these clusters:

1. **Bootstrap/path cluster:** exact path-value parity, import-order/sys.path precedence, installed-package importability, loose-script behavior where intentionally retained; negative controls corrupt root/path segment and reorder/remove legacy insertions.
2. **Corpus/Gate0/name cluster:** full-pop cards/index/order/count and error-path parity; negatives corrupt duplicate handling, filter-before-index order, Gate0 values, fuzzy/ambiguity behavior.
3. **Face/full-text cluster:** all-face string/order/empty-text parity and structured-face parity; negatives read only root text, reorder faces, or change join separator.
4. **Oracle structural + DET self-reference cluster:** exact accepted behavior plus separately identified gold/known-gap evidence; preserve call-time substitution; negatives snapshot provider attributes, replace DET with N2, or corrupt modal/die/Level-Class cases.
5. **DET synthetic representation cluster:** exact list length/order/string parity; negatives delete/reorder synthetic variants or change space/newline join.
6. **Artifact cluster:** byte-for-byte JSON parity; negatives alter trailing LF, UTF-8/ASCII behavior or indentation.
7. **Review/prompt legacy composition:** exact schema/string fixtures; negatives remove review fields or change condensation boundaries.
8. **Caller/topology cluster:** no new permanent import from `experiments`, no new root derivation, measured importer count monotonically falls only with reviewed caller migrations, and permanent package imports cleanly from an installed-package context. Negative controls deliberately add an `experiments` import/root derivation/stale `foundry_common` caller and require topology guards to fail.

The **S7 negative control is mandatory**: private test code must replace `fc.canonicalize_self_reference` (or the future provider equivalent) *after* the consumer/provider object is constructed and prove downstream shape extraction observes the replacement. A deliberately snapshot-captured implementation must fail this control. Passing output-only tests without this falsification is insufficient.

## Remaining STOP / decision list

No new card-text ownership decision is required; the prior blocker is resolved. The following remain implementation-time constraints rather than evidence gaps:

- The selected Oracle corpus is available in the project sources and identity-verified as above. The selected runtime codebook/generated runtime state must still be supplied and identity-verified before claiming canonical Gate-2 green; future full-pop corpus proofs must use this pinned corpus identity or a separately authorized successor.
- AQ4 frozen benchmark consumers may not be edited merely to reach zero `foundry_common` imports; retain compatibility or obtain separate authorization.
- Legacy sibling-import bootstrap cannot be removed until its loose-script/importability prerequisite is mechanically satisfied.
- DET-specific synthetic preprocessing has no permanent module today. It may remain a declared legacy composition boundary. If complete `foundry_common` deletion requires relocating that policy, STOP for an explicit owner decision rather than assigning it to `oracle_text` or `delivery` by convenience.

These constraints do **not** require rediscovering the dependency graph. A Manager can now issue a bounded S10 implementation contract from the measured matrix and symbol map once S10 itself is authorized and the required runtime inputs are available.

## Authority boundary

This package is evidence only. It does not authorize S10, S11-S16, semantic changes, AQ4, Bridge v0, Step6, merge, deployment, publication, or authority succession.
