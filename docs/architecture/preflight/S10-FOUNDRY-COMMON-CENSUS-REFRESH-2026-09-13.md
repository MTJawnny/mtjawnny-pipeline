# S10 `foundry_common` Census Refresh — 2026-09-13

Status: **COMPLETE REFRESH EVIDENCE / NOT IMPLEMENTATION AUTHORITY**

## Why this refresh exists

Objective 1 originally measured S10 at accepted implementation head:

`9f92039eb9c7132a351576c31472eb30a2957a67`

That census found 87 tracked Python importers of `foundry_common`, 35 externally referenced module-level names, and 45 total provider responsibilities.

The accepted cleanup/conservation head is now:

`493483aa1d54210c35e1665686a5e0136588da6d`

Cleanup deliberately retired `experiments/foundry_build_reaudit_packet.py` as live execution plumbing and preserved its original bytes under `archive/routing/experiments/foundry_build_reaudit_packet.py`. Because the Objective-1 implementation contract requires a re-census when accepted `h` changes, the live caller universe was re-measured rather than manually assumed unchanged.

## Method

A temporary read-only GitHub Actions audit checked out the planning lineage descended from the accepted cleanup head and enumerated the tracked universe using `git ls-files -z`.

Every tracked Python file was parsed with Python AST. The scanner recognized:

- direct `import foundry_common`;
- `from foundry_common import ...`;
- `experiments.foundry_common` forms;
- aliased module-qualified attribute access;
- statically discoverable `getattr` names; and
- string-bound provider contracts when the string names an actual module-level `foundry_common` responsibility, preserving the Objective-1/S7 `CardTextRules` census rule.

Archive paths were measured separately from live paths. Historical archived code is not implementation work.

Final audit source head carrying the scanner:

`53c0f7215b0327c75b9ec3292a25f5e6828f0490`

Workflow run: `34742611416`.

## Refreshed result

- tracked Python parse errors: **0**;
- live tracked Python importers of `foundry_common`: **86**;
- archived historical Python importers: **1**;
- all tracked importers if archive history is incorrectly counted: **87**;
- live externally referenced provider names: **35**;
- original provider blob remains unchanged: `experiments/foundry_common.py` blob `21192e3e6b8a1693abfe6a3b993e1014a2d84894`;
- provider responsibility count therefore remains **45 total = 35 externally referenced + 10 internal/load-bearing**.

The one archived importer is exactly:

`archive/routing/experiments/foundry_build_reaudit_packet.py`

It references `FOUNDRY_OUT_DIR` exactly as the original live generator did. The live path `experiments/foundry_build_reaudit_packet.py` is now a halt-loud retirement tombstone and no longer imports `foundry_common`.

## Delta from Objective-1 importer matrix

The original machine matrix remains a valid historical snapshot of `9f92039e...`; it must not be silently rewritten as though it measured the new accepted tree.

For S10 execution, the current live matrix is its old live caller set minus:

`experiments/foundry_build_reaudit_packet.py`

No replacement live importer appeared.

The removed caller's old classifications were:

- responsibility: `gate/check`;
- scope: `legacy_executable`;
- referenced provider name: `FOUNDRY_OUT_DIR`.

Therefore the deterministic caller-class delta from the old machine matrix is:

- AQ4/frozen benchmark: **5** unchanged;
- authority/transport: **1** unchanged;
- codebook or membership mutation: **43** unchanged;
- gate/check: **4 -> 3**;
- operator/CLI: **9** unchanged;
- pipeline/batch: **5** unchanged;
- reporter/census: **5** unchanged;
- test/negative control: **15** unchanged.

Scope delta:

- `aq4_frozen_benchmark`: **5** unchanged;
- `legacy_executable`: **66 -> 65**;
- `reporter_census`: **1** unchanged;
- `test_negative_control`: **15** unchanged.

These deltas are arithmetic consequences of the exact removed importer and its existing machine classification, not a new subjective reclassification pass.

## Live referenced provider names

The refreshed live set remains the same 35 names:

`CARDNAME_TOKEN`, `CONFIG_CR`, `CONFIG_GENERATED`, `CONFIG_REGISTERS`, `CONFIG_SELECTORS`, `CONFIG_SEMANTIC`, `CONFIG_THESAURUS`, `DATA_ARTIFACTS_DIR`, `FOUNDRY_OUT_DIR`, `REPO_ROOT`, `_CLASS_LEVEL_RE`, `_DIE_ROW_RE`, `_LEVEL_BAND_RE`, `_MODAL_HEADER_RE`, `_ROLL_INSTRUCTION_RE`, `_cardname_candidates`, `_is_band_marker`, `batch_paths`, `build_review_card_record`, `canonicalize_self_reference`, `condense_definition_for_prompt`, `det_scan_texts`, `full_oracle_text`, `gate_passes`, `halt`, `is_lattice_pattern`, `is_mode_line`, `is_prefilter_pattern`, `load_corpus`, `load_corpus_gated`, `pattern_misses_cardname_token`, `pattern_slug`, `raw_faces`, `resolve_name`, `write_json`.

The earlier audit variant that only counted qualified attributes temporarily reported 33 names; that scanner was immediately tightened to restore the original Objective-1 rule for string-bound provider contracts. The final refresh result is **35**, matching the original semantic provider surface.

## Related stale-reference repairs

This planning lineage also repairs two current-machine path defects without changing semantic truth:

1. `config/registers/family-sweep-known-debt.json`
   - provenance now points to the byte-exact archived W6 body at `archive/routing/docs/WORK-PACKETS-2026-08-07.md`;
   - the live Gate invocation now points to `tests/guards/gate2/foundry_family_sweep.py`;
   - the exact six-row `(kind, subject)` W6 fingerprint is unchanged.

2. `tests/guards/gate2/foundry_family_sweep.py`
   - command examples and `generated_by` now identify its S9 permanent guard location;
   - stale `docs/grammars.json` and `docs/det-patterns-v2.json` prose paths now identify `config/semantic/grammars.json` and `config/semantic/det-patterns-v2.json`;
   - no sweep decision logic, blocker semantics, or W6 fingerprint changed.

## S10 execution law after refresh

A future S10 task must:

- use **86 live importers**, not 87;
- exclude archived historical code from migration topology;
- preserve the 35-name / 45-responsibility provider contracts unless a reviewed caller migration proves a responsibility dead;
- leave the five frozen AQ4 importers byte-unchanged absent separate AQ4 authority;
- preserve S7 call-time provider substitution;
- preserve the explicit neutral-vs-DET representation boundary;
- preserve R8.3's no-activation gate;
- preserve AG-CLI-01 without using S10 as authority to expose a new mutating installed CLI;
- verify exact runtime corpus/codebook identities before claiming canonical Gate-2 green.

## Authority boundary

This refresh changes planning truth only. It does not itself authorize S10 implementation, S11–S16, AQ4, Bridge v0, Step6, merge, default-branch movement, deployment, publication, or semantic changes.
