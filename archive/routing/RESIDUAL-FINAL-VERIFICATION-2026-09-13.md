# Residual routing closeout — final verification evidence — 2026-09-13

Status: VERIFIED EVIDENCE; NOT MERGED; ACCEPTED IMPLEMENTATION HEAD UNCHANGED.

This file is historical verification evidence, not current task authority. Current task selection remains GitHub Issue #1 latest `K` -> active `T`.

## Scope and source identity

- Accepted implementation head remains `9f92039eb9c7132a351576c31472eb30a2957a67`.
- Previously full-Gate-2-verified cleanup base: `7aa321d656c211a7dd54103ed9b4e45950bd2b08`.
- Residual-closeout audit/export source tested: `fa214e3e0af6d5d7d7b3ba2ff606de7281efd1bf` on `cleanup/residual-routing-closeout-2026-09-12`.
- That source contained one temporary read-only audit/export workflow. The workflow was deleted after evidence capture. The post-test tree changes are only removal of that audit scaffold plus this evidence report; no semantic, config, guard, law, or runtime source bytes changed after the tested source.

## External inputs

The exported tracked source was tested locally against the exact project inputs supplied for this closeout:

| Input | SHA-256 | Size / population |
|---|---|---|
| selected codebook | `6aa6193f8a457ae4c7884e364f519749a9d68b96f7ecedf3fa903bfa4677426c` | 5,066,147 bytes |
| historical Oracle gzip | `b46e0670a8f3fa2d5357ec35ff7f8d58e7c2f9f15db0e27a3b0543672b00c217` | 38,233 nonblank JSONL records |

The source export was initialized as a local Git worktree before Gate 2 because the ruling-registry checks intentionally derive their universe with `git ls-files`. A first tar-only attempt therefore produced an invalid registry environment and was discarded; it is not evidence of a repository failure.

## R8.3 and AG-CLI-01 conservation

The separately implemented law-conservation branches were independently inspected before integration. Their canonical law blobs, inert historical stubs, byte-exact archives, and the R8.3 retired generator tombstone were reused on this cleanup lineage without merging those evidence branches.

- `R8.3` canonical live home: `docs/ACTIVATED-REGENERATE-SELF-DET-LAW.md`.
- `AG-CLI-01` canonical live home: `docs/MEMBER-ADD-MUTATION-LAW.md`.
- Original `B-CONSOLIDATION-REAUDIT-PACKET.md` Git blob `3f57d5cd9909aed5e8d9de6a8fbfa9c096f0ab44` is preserved byte-exact in archive.
- Original `B-MIGRATION-DIRECTIVE.md` Git blob `213206b6560d9f097ae86af1673b4630a1c1a64a` is preserved byte-exact in archive.
- Original re-audit generator Git blob `3a1fd7019c8c4d9f37054f5f1fc91e2b13bc41d0` is preserved byte-exact in archive; the live former generator path halts loudly instead of regenerating stale routing.

No DET pattern was activated, no membership semantics changed, and no mutation behavior was broadened.

## Remaining stale-routing closeout

The other residual present-tense execution documents identified by the prior full closeout audit are now inert live compatibility stubs with byte-exact historical bodies under `archive/routing/`:

- `docs/T3-BUILDOUT-PLAYBOOK.md` -> original blob `d4cffd89edddc15deb9a13c875365c4e019c492b`;
- `docs/T3-AXIS-FOUNDRY-v3.md` -> original blob `2b89ea43fa371945ee9f8b487758d4dddb2d60cc`;
- `docs/WORK-PACKETS-2026-08-07.md` -> original blob `e1bab565d6da493016d65fdef298eb4412f96e4a`.

The stubs retain only the exact source lines required to conserve the ruling-registry reference topology; those lines are explicitly historical and assign no work.

`docs/AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md` is now a paused compatibility pointer. Its exact prior body is preserved under archive as Git blob `92e254b222c76f4570d0870b371bfd371093a4c0`. The archived payload remains frozen benchmark/design evidence. This classification does not withdraw, amend, ratify, execute, or resume AQ4.

## Routing and ruling-registry verification

The temporary GitHub Actions audit executed on exact head `fa214e3e0af6d5d7d7b3ba2ff606de7281efd1bf` and completed successfully.

- Worker/cold-start + residual-routing tests: **28/28 passed**.
- Ruling-registry selftest: GREEN.
- `git diff --check`: GREEN.
- live registry measurements:
  - source documents: **144**;
  - ruling references: **685**;
  - distinct ruling IDs: **127**;
  - corroborated rulings: **86**;
  - sole-home rulings: **41**;
  - deletion-blocked documents: **13**.

The two additional source documents relative to the earlier cleanup registry are the two new canonical law homes. The substantive ruling population is conserved: 127 IDs, 685 references, 86 corroborated, and 41 sole-home.

`tests/refoundation/test_residual_routing_closeout.py` additionally pins all seven archived originals by Git blob identity, requires the direct historical paths to remain inert, checks both canonical law statements, checks the retired generator halts, and includes a deliberate reactivation negative control.

## Gate 2

Every canonical Gate 2 row was executed through `tests/guards/gate2/foundry_gate2.py` against the same exact exported source tree and the exact inputs above. Because the host command window is shorter than the full object-lattice run, coverage was completed with the runner's own `--only` mechanism rather than falsely claiming one uninterrupted process.

Results:

| Row | Result |
|---|---|
| `lint` | PASS |
| `family_sweep` | KNOWN-EXCUSED, exit 3; blocker fingerprint exactly equals authorized W6 |
| `definition_drift` | PASS |
| `ruling_registry` | PASS |
| `conservation` | PASS |
| `visibility` | PASS |
| `ground_truth` | PASS |
| `ground_truth_wide` | PASS |
| `gate_audit` | PASS |
| `probe_guards` | PASS |
| `recorded_numbers` | PASS |
| `invariance` | PASS |
| `reachability` | PASS |
| `object_lattice` | PASS; 72.7 s |
| `locality` | PASS |
| `qualifier_census` | PASS |

Aggregate semantic verdict: **16 rows / 15 PASS / 1 exact known-excused W6 / 0 unexpected failures**.

A runner negative control was then invoked as `--selftest --only SELFTEST_rigged`. It failed deliberately with exit 1 and the expected `SELFTEST_rigged` verdict. The tracked worktree was clean after verification.

## Objective 1 checksum correction

Objective 1 remains a separate evidence branch and S10 remains NOT AUTHORIZED. The completion record's importer-matrix digest was corrected to the SHA-256 of the exact LF bytes stored in Git:

`b60be70cef45fc03324452242f144f2cfb82d4638c0208408532dfa26ab53282`

The prior recorded digest `0ec96b701668730522e44d0402015df0cd943140e033b753c0544924008117e0` is retained only as provenance: it is the digest produced by CRLF-converted bytes, not the tracked Git payload.

No census, matrix, symbol-map, runtime, source, or S10 implementation content was changed by that correction.

## Authority boundary

This verification does not move accepted h, merge a branch, change the default branch, resume AQ4, activate Bridge v0, start Step6, implement S10-S16, mutate semantic truth, change the authority selector, or change the codebook.

The residual routing/conservation repair and Objective 1 checksum-record repair are now evidence-complete for Manager/Captain review. Any acceptance/merge/ref/default-branch action remains a separate Captain decision.
