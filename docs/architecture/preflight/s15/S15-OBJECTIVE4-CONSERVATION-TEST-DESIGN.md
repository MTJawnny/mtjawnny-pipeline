# S15 Objective 4 Conservation Test Design

Status: **PREFLIGHT DESIGN ONLY / NO GUARDS INSTALLED**  
Measured accepted head: `9f92039eb9c7132a351576c31472eb30a2957a67`  
Timing law: regenerate/revalidate this suite at the actual accepted pre-S15 head after S10-S14.

## Conservation target

S15 is allowed to change legacy topology only. It must not change semantic behavior, selected authority, accepted baselines, ruling truth/provenance, benchmark commitments, command reachability, or clean-checkout reproducibility. A green package test suite is insufficient if the deletion changes Gate-2 semantics or silently depends on ignored local state.

The pre-S15 Manager should snapshot, before mutation:

- accepted Git head and complete tracked path set;
- candidate deletion/archive set and successor map;
- tracked document population;
- ruling-ID set, raw reference multiplicity, sole-home/corroborated state, and intentional false-positive state;
- Gate-2 row identities, commands, statuses, known-excused fingerprint, and baseline/ratchet values + directions;
- selected authority selector/object identity and local-mirror identity;
- ground-truth fixture set + hashes;
- frozen benchmark/AQ4 file set + hashes/commitments;
- `.gitignore` semantics for runtime roots and every tracked control/baseline/fixture;
- every exact legacy path/module string found in tracked code, tests, commands, workflows, configuration, and operational docs;
- clean-checkout regeneration/restore recipe and the set of allowed runtime outputs.

## Required negative controls

Every control below must be shown capable of going red on the actual pre-S15 rig. A control that has only been designed is **UNPROVEN**.

| ID | Hazard it must catch | Rigged-red experiment | Required detector | Objective-4 status |
|---|---|---|---|---|
| NC01 | Delete a file with one hidden tracked caller | In an isolated temporary tree, remove a candidate but leave/inject one `importlib.util.spec_from_file_location`, module-by-string, or legacy facade caller | caller-closure analyzer must report the removed path as reachable; deletion gate fails | **UNPROVEN in this session**. Existing `test_det_batch_retirement.py` and `codebook_consumer_analysis.py` prove these caller classes exist and must be modeled. |
| NC02 | Delete a live fixture misidentified as history | Remove one `tests/fixtures/ground_truth/**` file from a temporary candidate set | fixture manifest/hash or owning test must go red before package acceptance | **UNPROVEN**; fixture ownership is already guarded by refoundation layout tests. |
| NC03 | Lose a sole-home ruling | Remove a known sole-home source document (e.g. a ledger-identified sole-home) only in an isolated rig | before/after ruling registry must show missing ruling ID / changed sole-home state and fail | **UNPROVEN**. Cleanup correction history is the adversarial antecedent. |
| NC04 | Delete the only provenance for permanent semantic behavior | Remove one executor/verifier or research artifact that is the only provenance edge in the truth-home manifest | provenance-coverage check must report an orphaned accepted behavior/decision | **UNPROVEN**; this control must be created before destructive S15. |
| NC05 | Leave stale command/workflow path after removal | Change candidate set as if legacy path were gone while keeping one `.claude/commands`, workflow, script, subprocess, config, or current operational-doc exact path string | post-removal exact-path/module-string scan must fail | **UNPROVEN**. Current triage commands provide real positive fixtures. |
| NC06 | Retire before successor covers every caller | Mark a partial successor complete while leaving one caller on legacy wrapper/API | successor-closure proof must show uncovered caller class and fail | **UNPROVEN**. Objective 3 supplies known partial-successor cases for wrapper/tier-engine rigs. |
| NC07 | `.gitignore` change begins tracking runtime output | In an isolated worktree remove/alter the runtime ignore and generate a sentinel under the intended runtime root | `git status --porcelain --untracked-files=all` / `git check-ignore` contract must go red | **UNPROVEN**; Objective 4 does not mutate `.gitignore`. |
| NC08 | `.gitignore` change hides a tracked control/baseline | In an isolated rig add an ignore rule matching `config/baselines/**`, a selector, fixture, or other tracked control | ownership checker using `git check-ignore --no-index` against protected tracked-control patterns must fail | **UNPROVEN**. This checks the opposite direction from NC07. |
| NC09 | Package/test success depends on local ignored file | Run from a pristine checkout with no inherited ignored state; do not copy `experiments/out/**` | required restore/generation must succeed from authoritative inputs, or the S15 readiness gate must block explicitly | **UNPROVEN / BLOCKED in GitHub-only session**. The output census shows why this is mandatory. |
| NC10 | Deletion changes Gate-2/verification semantics, not topology only | In a temporary rig alter/remove a Gate-2 row, change its command/known-excused semantics, or alter a protected baseline while keeping superficial overall green possible | before/after semantic manifest comparison must fail on row identity/argv/status/waiver/baseline direction or protected output hash | **UNPROVEN**. Top-level green count alone is explicitly insufficient. |

## Setwise ruling/document proof

The future guard should compare sets and multiplicities, not only filenames:

1. `tracked_documents_before` vs `tracked_documents_after`, with every intentional removal mapped to an archive/tombstone/deletion disposition.
2. `ruling_ids_before == ruling_ids_after`, unless a later Captain-authorized semantic change explicitly says otherwise.
3. Raw reference multiplicity changes are enumerated and explained. A sole-home must never become zero-home silently.
4. Corroborated vs sole-home classification remains equivalent or is strengthened.
5. Known intentional false positives remain known and pinned; a disappearance is investigated rather than celebrated automatically.
6. Baseline/ratchet values and directions remain identical unless separately authorized.

If S15 retires the registry mechanism itself, the replacement must pass the same before/after proof and demonstrate equivalent or stronger conservation before the old guard disappears.

## Generated/runtime proof

A deletion candidate labeled derivable is not ready until a clean checkout can regenerate it from tracked/authoritative inputs and all downstream consumers accept the regenerated bytes/semantics. Ignored status is never evidence of derivability. Unknown ignored bytes remain blockers.

The future run should separately prove:

- no required source-like control exists only in local ignored state;
- tracked files regenerated by tools reproduce accepted bytes or an explicitly authorized semantic equivalent;
- caches used as control inputs are owned and versioned intentionally;
- runtime `var/**` ownership and `.gitignore` behavior are mutually consistent;
- no legacy `experiments/out/**` reader survives after the owning migration slice.

## Pass condition for the destructive S15 contract

S15 may call its conservation suite proven only when all ten negative controls have a recorded rigged-red observation on the actual pre-S15 test harness, the unrigged suite is green, and every Objective-4 blocker is mechanically cleared or explicitly decided by the Captain. This document does not authorize deletion.