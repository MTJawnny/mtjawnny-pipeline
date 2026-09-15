# S15 Post-S14 Conservation Test Design

Status: **EVIDENCE / DESIGN ONLY. No guard is installed and no harness is committed.**
Base: `49fcb292e0668b70901118c52dedc0ffd00f389f` (accepted S14 head).
Authority: Issue #1 K `5675514144` selects T `5675512901` (S15.R0).
Repair: S15.R0.R2 — Issue #1 K `5683296790` selects T `5683294052` (parent review `5683255432`); repair parent `7aeb24721d7511f18644afbf46d7dc4ed2fc3088`, measurement base unchanged.
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

A green top-level count does not satisfy this. The comparison unit is **row identity + argv + status + waiver**, together with the **failing/error node-ID sets** and **value-level failure identity** (the assertion body of every failing block). R0.R2 showed why the last part is needed: under D1 all 12 inherited-red `test_layout_delegation` methods kept their IDs while their measured values changed.

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
6. **R2 edge classifier (added by R0.R2).** Every mention line of a candidate — full path, original path of an archived body, basename, module token, and **composed-name fragments** such as `f"experiments/foundry_{name}.py"` — is classified by zone and AST features into exactly one of `BEHAVIORAL_CONSUMER`, `CURRENT_OPERATOR_OR_LAW_ROUTE`, `SOURCE_INSPECTION_GUARD`, `POPULATION_PIN`, `SYNTHETIC_NEGATIVE_CONTROL`, `HISTORICAL_PROVENANCE`, `FALSE_POSITIVE_OR_IRRELEVANT` or `UNKNOWN_BLOCK`. Current roots include executable halt/raise/print diagnostics (and message constants they emit), canonical extracted law, the current planning router, stubs/tombstones, config registers and tests that read candidate source or bytes. An undecidable material mention is `UNKNOWN_BLOCK`. Each class drives an explicit prerequisite.
7. **Analyzer participation (added by R0.R2).** Name-free dependencies are measured by running the repository's own test analyzers read-only on tracked-only trees (`codebook_consumer_analysis`, `layout_census`, the S10 caller census, bootstrap families). This found that `test_the_live_external_UNKNOWN_rows_now_say_why` depends on `foundry_reach_census.py`, which it never names.
8. **Deletion-impact rigs.** A disposable worktree at BASE gets the ignored state cloned in and the candidate set removed. Gate 2 and the broad suite then run, and the node-ID sets are diffed against BASE.
9. **Registry `--check` / read-only `build()`.** No emit, no `--update-baseline`.
10. **Validator.** No `DELETE_SAFE` without all eight evidenced criteria. No protected `benchmarks/aq4/**` outside `KEEP_PERMANENT`. No shell with a caller marked safe. No UNKNOWN rule promoted.

## 4. Negative controls: executed in R0

Rig: one detached worktree at BASE. Each paired control ran the sequence PRE (unrigged) → RIG → DETECT → `reset --hard BASE` + `clean -fdx` → residue check; NC8b has no unrigged arm (see its row). Every residue check returned `HEAD == BASE` with an empty `status --ignored --untracked-files=all` (bytecode excluded). The rig worktree was removed afterwards.

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

**Result (corrected by R0.R2):** 12 sub-controls ran. **11 paired sub-controls** (NC1, NC2a, NC2b, NC3, NC4, NC5, NC6, NC7, NC8a, NC9, NC10) showed a normal/control state and a rigged RED/BLOCKED state. **NC8b is an intentional standing-red BASE observation**: with `.gitignore` unchanged, `var/codebook/nc8b_sentinel.json` is untracked-visible, proving the current `var/**` exposure (B08); it has no green→red pair. All NC1–NC10 hazard classes are demonstrated. Zero residue after every restore is a Worker-execution claim recorded by R0 (scratch `nc_run.log`), not independently repo-verifiable history.

## 5. Deletion-impact rigs (measurement, not controls)

| rig | removed | Gate 2 | broad suite vs BASE |
|---|---|---|---|
| D1 | 47 tracked `experiments/**` files (42 ARCHIVE_PRESERVE + 5 BLOCKED_UNKNOWN) with no R0 first-pass conservative live reach — R0.R2 shows such members still carry current routes, source-inspection guards and s10-sidecar pins | unchanged: 16/15/1 W6/0 | **raw** `FAILED (failures=17, errors=8)` vs BASE `FAILED (failures=12)`. **Unique methods:** 16 failing (12 inherited + 4 new: `test_s10…test_the_live_caller_set_is_exactly_the_reviewed_one` and 3 `test_codebook_store` population/arithmetic/UNKNOWN-frontier pins) and 1 new erroring method (`test_the_fifteen_C8_5V_candidates…`) carrying **8** `module=` subtest errors. **Value level:** all 12 inherited-red methods changed values (e.g. `81 != 82` → `38 != 82`), plus a new subtest identity under an inherited method. "+4 failures, +1 error" is method-level only. |
| D2 | 4 zero-ruling docs stubs | **RED**: `ruling_registry` documents 138→134, WORSE | **+1 failure**: `test_s14…test_the_pinned_section_is_the_registry_measured_now` |
| D3 | ignored `experiments/out/foundry/audit-baseline.json` only | identical: rc 0, 16/15/1 W6/0 | **identical**: 1850 / 12 same IDs / 0 errors / 0 skips; R0.R2 re-parse: every failure block identical to BASE at value level |

Consequence: archiving or deleting tracked legacy files is **not topology-only** under current guards (N02). Stub removal is a registry-population change that needs authorized succession (B09).

D1 attribution (R0.R2, repository analyzers on tracked-only BASE and BASE-minus-D1 trees, reproducing every changed value): the 8 C8.5V members in D1 → the 8 `KeyError` subtests; 9 consumer rows (those 8 + `foundry_slug_dossier`) → totals `SAFE_NO_TRANSITIVE_HANDLER` 15→6 and fan-in 28→19; `foundry_reach_census` → the only live UNKNOWN-frontier row; 34 members → S10 live caller set 88→54; layout census sys.path calls 81→38. **D1 is a batch experiment.** It proves nothing member-by-member and nothing about candidates it did not remove; see `DEPENDENCY-EVIDENCE` → `impact_rigs.D1.r2_outcome_accounting`.

## 6. Clean-checkout probe

The probe used a worktree of exact BASE with no copied ignored or untracked state.

- **Gate 2 (re-derived by R0.R2, runner and per-row argv):** rc 1 · 16 run / 3 ok / 13 unexpected.
  - 3 rows STOP on the missing `experiments/out/foundry/codebook.json`.
  - 10 rows STOP on the missing `data/raw/oracle-cards.jsonl.gz`.
  - The runner prints each failing row's standing semantic explanation (e.g. lint "the codebook is structurally invalid") for what are missing-input STOPs.
- **Broad discover:** aborts with no summary. The corpus `SystemExit` escapes `test_mtg_shapes_substrate` and ends the process (N01).
- **Per module (re-derived by R0.R2; R0's "30 modules OK" was false):** 32 modules; **29 rc=0** (7 of them with 22 silent skips, 0 at the populated BASE); **3 nonzero**:
  - `test_layout_delegation`: the 12 inherited failures;
  - `test_s13r2_manual_operator_closure`: 2 failures, diagnosed **missing input** (no local codebook → status stops at `NO_LOCAL_CODEBOOK` before any transport call, which also disarms a negative control);
  - `test_mtg_shapes_substrate`: aborted, no summary.
- **Broad discover, verbose:** reaches 13 modules (last `test_mtg_shapes_substrate`); 971 ok / 12 FAIL / 5 ERROR / 2 skipped outcome lines, then the abort; **19 modules (786 tests) never execute**.
- **`test_mtg_shapes_substrate` isolation (one process per class and per test, no source edit, SystemExit not caught):** the module run prints 19 ok, then **5 pre-abort errors** — `setUpClass` of `TestG4bOverTheSliceSevenTree` (its 3 tests never run) and 4 `TestTheB8AndB9Controls` tests — then `TestTheKeywordHomeDerivationHasExactlyONEOwner.test_a_CR_spell_keyword_gets_a_HOME_and_NO_delivery_token` raises the corpus STOP and **55 tests (including that one) are censored**. In isolation the 81 tests give 46 ok / 28 `FileNotFoundError` on the corpus / 7 halt-loud `SystemExit` on the corpus: every non-OK outcome is **missing input**, 0 semantic regressions.

## 7. Pass conditions a destructive S15 slice must meet

1. Re-run §2 at its own base. Any drift is a STOP.
2. Re-run the R2 edge census (names, composed fragments, analyzer participation) over the slice's exact set. Every material edge must be discharged by its own class prerequisite; any `UNKNOWN_BLOCK` edge, any undischarged current route/consumer/guard/pin, or any unexplained new edge is a STOP. Co-move edges are discharged only by moving both ends in the same slice.
3. Re-run NC1–NC10 at that base, including a slice-specific NC5/NC3 over the slice's own members.
4. Run an impact rig of the slice before committing. Compare **value-level** failure identity, not only node IDs. Every change must be an authorized conservation of the guarded proposition (value-identical retarget) or an authorized retirement of that proposition; anything else is a STOP.
5. **Gate 2** must stay at row identity 16/15/1 with the exact W6 set, unless an authorized registry succession accompanies a document change.
6. **Registry** before/after:
   - ruling-ID set identical;
   - sole-home and corroborated state identical;
   - raw-reference delta fully attributed.
7. **Archive moves:** byte/blob manifest (R100) and provenance pairs kept together (`migrate_codebook_v2` + `verify_migration`).
8. **Clean checkout:** state the result explicitly. A slice may not *increase* dependence on ignored state.
9. **Protected invariants:** `benchmarks/aq4/**`, the ratchet files, `src/**` and `config/**` unchanged unless named.

## 8. Negative controls for the R2 edge classifier (executed in R0.R2)

Rig: one disposable detached worktree at `49fcb292`. Each control measured the edges of `experiments/foundry_synonym_collision.py` (ARCHIVE_PRESERVE, zero material edges at BASE) **unrigged**, applied the rig (`git add`), measured again, then ran `reset --hard BASE` + `clean -fdx` and proved `HEAD == BASE`, an empty `status --ignored --untracked-files=all`, and a tracked-file sha256 manifest equal to BASE's. The rig worktree was removed afterwards.

| id | hazard | candidate | unrigged material edges | rigged referrer → class | result | restore |
|---|---|---|---|---|---|---|
| NC-R2-1 | current-law Markdown route to a legacy candidate | `experiments/foundry_synonym_collision.py` | none | `docs/ZZ-NC-R2-LAW.md` → CURRENT_OPERATOR_OR_LAW_ROUTE | PASS | byte-exact |
| NC-R2-2 | executable halt/diagnostic string directing an operator to a legacy candidate | `experiments/foundry_synonym_collision.py` | none | `src/mtj_foundry/zz_nc_r2_diag.py` → CURRENT_OPERATOR_OR_LAW_ROUTE; `tests/refoundation/zz_nc_r2_msg.py` → CURRENT_OPERATOR_OR_LAW_ROUTE | PASS | byte-exact |
| NC-R2-3 | test/guard reads a candidate's source text without importing it | `experiments/foundry_synonym_collision.py` | none | `tests/refoundation/zz_nc_r2_read.py` → SOURCE_INSPECTION_GUARD | PASS | byte-exact |
| NC-R2-4 | legacy diagnostic route from a current shell (foundry_cr_checks) to an archive candidate | `experiments/foundry_synonym_collision.py` | none | `experiments/foundry_cr_checks.py` → CURRENT_OPERATOR_OR_LAW_ROUTE | PASS | byte-exact |
| NC-R2-5 | historical prose naming the path is not automatically promoted to current routing | `experiments/foundry_synonym_collision.py` | none | `archive/zz_nc_r2_old.md` → HISTORICAL_PROVENANCE; `docs/SESSION-HANDOFF-2026-08-04-EVE.md` → HISTORICAL_PROVENANCE; `docs/ZZ-NC-R2-PENDING-2026-07-02.md` → UNKNOWN_BLOCK; `docs/ZZ-NC-R2-RECORD-2026-07-01.md` → HISTORICAL_PROVENANCE | PASS | byte-exact |
| NC-R2-6 | archive/readiness promotion refused while a material edge is UNKNOWN_BLOCK or an unfulfilled current route | `experiments/foundry_synonym_collision.py` | none | `docs/ZZ-NC-R2-LAW.md` → CURRENT_OPERATOR_OR_LAW_ROUTE; `docs/ZZ-NC-R2-PENDING-2026-07-02.md` → UNKNOWN_BLOCK | PASS | byte-exact |

- **NC-R2-2 first went RED against the classifier itself.** `raise RuntimeError(f"... run experiments/X.py first")` was not recognised as a diagnostic. The worker-local classifier was fixed; re-running the whole BASE census afterwards changed **0** classifications, and all six controls then passed.
- **NC-R2-5** shows the method neither promotes nor dismisses by path name: the same imperative sentence is `HISTORICAL_PROVENANCE` in `archive/**` and in a doc that declares its instructions inert, while an unmarked record carrying it stays `UNKNOWN_BLOCK`.
- **NC-R2-6** tests the validator on edges, never on the matrix label. Unrigged (name-edge layer): `[]` — analyzer participation (layout census) is a separate prerequisite layer and still keeps the candidate NOT_READY in the matrix. Rigged: `[['docs/ZZ-NC-R2-LAW.md', 'CURRENT_OPERATOR_OR_LAW_ROUTE'], ['docs/ZZ-NC-R2-PENDING-2026-07-02.md', 'UNKNOWN_BLOCK']]`. Declaring both the route and the unknown edge satisfied still leaves `[['docs/ZZ-NC-R2-PENDING-2026-07-02.md', 'UNKNOWN_BLOCK']]` — an `UNKNOWN_BLOCK` edge cannot be declared away. On the real BASE tree the validator also refuses `foundry_w3_census.py` (`[['docs/W3-TRIGGER-VOCABULARY-2026-08-07.md', 'UNKNOWN_BLOCK'], ['tests/refoundation/s10_foundry_common_callers.json', 'POPULATION_PIN']]`) and `invert_tags.py` (`[['experiments/tier_engine.py', 'CURRENT_OPERATOR_OR_LAW_ROUTE']]`).

Nothing in this document authorizes any of those slices.
