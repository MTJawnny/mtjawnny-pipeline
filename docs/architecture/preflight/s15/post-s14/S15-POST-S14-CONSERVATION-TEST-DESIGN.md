# S15 Post-S14 Conservation Test Design

Status: **EVIDENCE / DESIGN ONLY. No guard is installed and no harness is committed.**
Base: `49fcb292e0668b70901118c52dedc0ffd00f389f` (accepted S14 head).
Authority: Issue #1 K `5675514144` selects T `5675512901` (S15.R0).
Supersedes as *current design* (but does not rewrite): `docs/architecture/preflight/s15/S15-OBJECTIVE4-CONSERVATION-TEST-DESIGN.md`. Every Objective-4 control was UNPROVEN, and this revision executed every control.

## 1. Conservation target

S15 may change legacy topology only. The following must stay identical across any destructive slice unless a separately authorized T says otherwise:

- semantic behavior;
- selected authority;
- ratchet baseline and succession;
- ruling truth and topology;
- frozen AQ4 evidence;
- command reachability;
- clean-checkout reproducibility.

A green top-level count does not satisfy this. The comparison unit is **row identity + argv + status + waiver**, together with the **failing/error node-ID sets**.

## 2. Invariants measured at BASE (pin these before any mutation)

| invariant | BASE value |
|---|---|
| tracked paths | 556 (86 under `experiments/**`) |
| Gate 2 (`python3 tests/guards/gate2/foundry_gate2.py`) | rc 0 · 16 run · 15 ok · 1 KNOWN (`family_sweep`) · 0 unexpected |
| W6 blocking set (exact) | `[family-members-contradict-template] activated-tap-or-untap-<scope>`, `[family-members-contradict-template] targeted-<action>-<class>`, `[pattern-misses-cardname-token] rule:forced-attack-each-combat`, `[ratified-pattern-has-no-axis] rule:cant-be-blocked-as-long-as-state`, `[ratified-pattern-has-no-axis] rule:cant-be-blocked-by-power`, `[ratified-pattern-has-no-axis] rule:cant-be-blocked-except-by-count` |
| W6 register | `config/registers/family-sweep-known-debt.json` sha256 `db9f0c45…8ddff` |
| broad suite (`python3 -m unittest discover -s tests/refoundation -t .`) | 1850 tests · 12 failures · 0 errors · 0 skips; failures = the 12 inherited `test_layout_delegation` IDs |
| live ratchet baseline | `config/baselines/foundry-audit-baseline.json` sha256 `b0f3d6d7…aaa1` (4324 B) |
| succession record | sha256 `1de16afa…6dec`; latest ordinal 1 |
| genesis snapshot | `refoundation/conservation/P0-3A-FOUNDRY-AUDIT-BASELINE.json` sha256 `51fca151…7601` |
| ruling registry | 138 docs / 127 ids / 660 refs / 86 corroborated / 41 sole-home (== live `ruling_registry` section) |
| selector / codebook mirror / corpus | `fa6686e0…` / `6aa6193f…` / `2be88ba8…` (input-lock) |
| AQ4 freeze manifest | `benchmarks/aq4/FREEZE-MANIFEST.json` sha256 `bb939fbf…365b`; 30 tracked files |
| tracked-but-ignored set (`git ls-files -ci --exclude-standard`) | `[docs/architecture/preflight/s16b/claims.jsonl]` |
| ignored local inventory | 3,620 files · 3,355,335,202 B · digest `ab3d1c10…6d27` |

## 3. Detection instruments (worker-local in R0; a destructive S15 must reproduce them)

1. **Reference census.** Every tracked file is scanned by AST import, string constant, and module/basename token. Each referrer line is categorised as IMPORT, LOAD, PIN, COMMENT or TEXT.
2. **Helper-loader discovery.** The census finds the 75 live functions whose bodies perform a dynamic load. A same-line call such as `load_legacy("foundry_x")` then counts as a LOAD.
3. **Operator-surface edges.** A text reference in `.claude/commands/**`, `.github/workflows/**`, `CLAUDE.md`, `pyproject.toml` or `README.md` counts as an execution-capable consumer.
4. **Two detection modes.**
   - **Strict:** IMPORT, same-line LOAD, helper call, or operator text.
   - **Conservative:** strict, plus any code-line mention inside a live file that dynamically loads anywhere.
   - Conservative is an upper bound and is used only to *block*.
5. **Transitive reachability.** A reverse BFS runs through `experiments/**` intermediates to live roots. Frozen `benchmarks/aq4/**` consumers are reported separately.
6. **Deletion-impact rigs.** A disposable worktree at BASE gets the ignored state cloned in and the candidate set removed. Gate 2 and the broad suite then run, and the node-ID sets are diffed against BASE.
7. **Registry `--check` / read-only `build()`.** No emit, no `--update-baseline`.
8. **Validator.** No `DELETE_SAFE` without all eight evidenced criteria. No protected `benchmarks/aq4/**` outside `KEEP_PERMANENT`. No shell with a caller marked safe. No UNKNOWN rule promoted.

## 4. Negative controls: executed in R0

Rig: one detached worktree at BASE. Each control ran the sequence PRE (unrigged) → RIG → DETECT → `reset --hard BASE` + `clean -fdx` → residue check. Every residue check returned `HEAD == BASE` with an empty `status --ignored --untracked-files=all` (bytecode excluded). The rig worktree was removed afterwards.

| id | hazard | rig | detector | unrigged | rigged |
|---|---|---|---|---|---|
| NC1 | hidden tracked caller of a would-be safe module | stage `tests/refoundation/zz_nc1_hidden_caller.py` importing `foundry_synonym_collision` | reach strict + conservative | no live reach | **RED** (caller listed in both modes) |
| NC2a | string/subprocess consumer without import | stage a test with the path constant on line 3 and `subprocess.run` on line 6, targeting `foundry_digest.py` | reach conservative | no live reach | **RED**. Strict mode stayed **blind by construction** (recorded limitation) |
| NC2b | command consumer, no Python | stage `.claude/commands/zz-nc2b.md` naming `experiments/foundry_emit.py` | reach operator-surface edge (strict) | no live reach | **RED** |
| NC3 | only provenance owner removed | `git rm archive/routing/experiments/foundry_build_reaudit_packet.py` (1 blob copy in tree) | `test_residual_routing_closeout` + blob-uniqueness | OK | **RED** (archived-payload blob test errors) |
| NC4 | document becomes sole home of a synthetic ruling | append `- **G99** — …ratified by Captain` to the SAFE stub `docs/SESSION-HANDOFF-2026-08-06.md` and stage it | `foundry_ruling_registry.py --check` | SAFE rc 0 | **BLOCKED rc 1** |
| NC5 | compatibility shell declared safe while a caller remains | `git rm experiments/foundry_cr_edition_diff.py` | `test_mtg_cr_substrate` + reach caller list | OK (19) | **RED** (`test_edition_diff_was_not_migrated_as_substrate`) |
| NC6 | frozen AQ4 misclassified as disposable | `git rm benchmarks/aq4/experiments/foundry_aq4_probes.py` | `test_s14_aq4_freeze_relocation` | OK (23) | **RED** |
| NC7 | `.gitignore` hides a tracked control | append `config/baselines/` | tracked-but-ignored set | baseline not ignored | **RED** (baseline enters the set) |
| NC8a | `.gitignore` starts tracking runtime output | ignored sentinel under `experiments/out/`, then delete that ignore line | `git status --untracked-files=all` | sentinel invisible | **RED** (sentinel untracked-visible) |
| NC8b | runtime owner `var/**` not ignored at BASE | create `var/codebook/nc8b_sentinel.json` with `.gitignore` unchanged | `git status` + `git check-ignore` | — | **RED at BASE** (standing exposure, B08) |
| NC9 | success depends on a local ignored artifact | stage a test requiring `data/raw/oracle-cards.jsonl.gz` | clean vs populated run | OK populated | **RED clean** |
| NC10 | UNKNOWN / protected / shell-with-caller promoted to `DELETE_SAFE` | in-memory copy of the real matrix flips `foundry_digest.py`, `benchmarks/aq4/**`, and `foundry_authority.py` (with fabricated criteria) | validator | 0 errors | **RED** (errors for all three) |

**Result: 12/12 sub-controls green unrigged and red rigged, zero residue.**

## 5. Deletion-impact rigs (measurement, not controls)

| rig | removed | Gate 2 | broad suite vs BASE |
|---|---|---|---|
| D1 | 47 tracked `experiments/**` files with no conservative live reach at the first census pass | unchanged: 16/15/1 W6/0 | **+4 failures, +1 error**: `test_s10_card_text_owners…test_the_live_caller_set_is_exactly_the_reviewed_one`, 3 `test_codebook_store` population/arithmetic pins, 1 `test_codebook_store` error |
| D2 | 4 zero-ruling docs stubs | **RED**: `ruling_registry` documents 138→134, WORSE | **+1 failure**: `test_s14…test_the_pinned_section_is_the_registry_measured_now` |
| D3 | ignored `experiments/out/foundry/audit-baseline.json` only | identical: rc 0, 16/15/1 W6/0 | **identical**: 1850 / 12 same IDs / 0 errors / 0 skips |

Consequence: archiving or deleting tracked legacy files is **not topology-only** under current guards (N02). Stub removal is a registry-population change that needs authorized succession (B09).

## 6. Clean-checkout probe

The probe used a worktree of exact BASE with no copied ignored or untracked state.

- **Gate 2:** 3/16 ok.
  - 3 rows STOP on the missing `experiments/out/foundry/codebook.json`.
  - 10 rows STOP on the missing `data/raw/oracle-cards.jsonl.gz`.
- **Broad discover:** aborts with no summary. The corpus `SystemExit` escapes `test_mtg_shapes_substrate` and ends the process (N01).
- **Per module:**
  - 30 modules OK, with 22 skips between them (0 at the populated BASE);
  - `test_layout_delegation` shows the 12 inherited failures;
  - `test_s13r2_manual_operator_closure` has 2 clean-only failures;
  - `test_mtg_shapes_substrate` aborts.

## 7. Pass conditions a destructive S15 slice must meet

1. Re-run §2 at its own base. Any drift is a STOP.
2. Re-run the reference census in both modes over the slice's exact set. Any strict consumer, or any unexplained conservative consumer, is a STOP.
3. Re-run NC1–NC10 at that base, including a slice-specific NC5/NC3 over the slice's own members.
4. Run an impact rig of the slice before committing. Every changed node ID must be an explicitly authorized guard retarget; anything else is a STOP.
5. **Gate 2** must stay at row identity 16/15/1 with the exact W6 set, unless an authorized registry succession accompanies a document change.
6. **Registry** before/after:
   - ruling-ID set identical;
   - sole-home and corroborated state identical;
   - raw-reference delta fully attributed.
7. **Archive moves:** byte/blob manifest (R100) and provenance pairs kept together (`migrate_codebook_v2` + `verify_migration`).
8. **Clean checkout:** state the result explicitly. A slice may not *increase* dependence on ignored state.
9. **Protected invariants:** `benchmarks/aq4/**`, the ratchet files, `src/**` and `config/**` unchanged unless named.

Nothing in this document authorizes any of those slices.
