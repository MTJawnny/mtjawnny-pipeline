# Current Manager Handoff — 2026-09-10

> **NON-AUTHORITATIVE DISCOVERY HINTS.** Re-fetch GitHub Issue #1 and live PR/source state before acting. If anything here is stale, live durable state wins.

## Current discovery anchors

Repository: `MTJawnny/mtjawnny-pipeline`

As of this handoff:

- accepted implementation head: `d7f1fe025ed35a95f57585fb5a8e71303951b062`
- latest Manager review accepting S1 / resolving S2: Issue #1 comment `5620096956`
- active Worker task: `REFOUNDATION.EXPERIMENTS-MIGRATION.S3-CONFIG-AUTHORITY-RELOCATION`
- active T: Issue #1 comment `5620109839`
- latest known K selecting S3: Issue #1 comment `5620113268`
- S1 implementation PR: **#43**, expected OPEN / draft / unmerged at `d7f1fe025ed35a95f57585fb5a8e71303951b062`
- prior Path-E PR: **#42**, expected OPEN / draft / unmerged at `6bbd69fe8b1a0aac9c711ae96c1d01f54de40def`
- accepted R6 migration master-plan Worker X: `5613155741`
- Manager V accepting R6 / implementation-ready plan: `5613242327`
- Captain overnight/autonomy directive referenced by the active S3 task: `5614053424`

Revalidate all of the above. Do not assume these are still latest.

## Accepted migration frontier at this handoff

- **S1 — Layout ownership: ACCEPTED.** `ProjectPaths` received the accepted destination layout. PR #43 is the implementation surface.
- **S2 — Install package: SATISFIED_BY_EXISTING_CAPABILITY.** No S2 commit was required. The substantive installed-package capability already existed and was guarded.
- **S2 correction:** the old broad negative-control wording incorrectly pulled final cleanup forward. The S2 predicate is installed-package capability outside the checkout with no `PYTHONPATH`/repo path surgery; removing the installed mapping must make that same external import fail. Remaining legacy `sys.path` bootstrap deletion stays final-slice/D6 work.
- Old bootstrap counts are **not** acceptance targets. Re-derive the active-scope denominator at the future deletion head instead of forcing a stale number.
- **S3 — Config / authority / input relocation: ACTIVE** at the time this file was written.

## S3 high-value reminder

Read T `5620109839` in full. Its core shape is a bounded relocation, not semantic change:

- move the ten already-classified tracked config/authority/input blobs to S1-owned destinations;
- preserve moved bytes exactly;
- perform a **pre-edit reader census** and classify references as `ACTIVE_READER`, `ACTIVE_CONTRACT`, `HISTORICAL_TEXT`, or `NON_READER`;
- change only the mechanically proven active reader/contract closure plus authorized tests/path-owner edits;
- historical path prose is not a cleanup target;
- authority selection, codebook bytes, corpus bytes, AQ4 bytes, experiment Python semantics, baselines, deployment/publication, and R2 writes are not authorized;
- require the routing/conservation predicates named in the T and STOP on unexplained drift or scope expansion.

If a Worker X for S3 exists when the new session starts, review it before issuing anything new.

## R6 architecture seam worth preserving

The accepted R6 repair exists because the earlier plan accidentally created a permanent CR↔shapes cycle. The accepted ownership direction is:

`shapes -> cr -> edition -> infra`

Critical seam:

- CR parsing/classification facts stay in `mtj_foundry.mtg.cr.*`;
- shape composition such as `find_home` / `keyword_homes()` belongs with `mtj_foundry.mtg.shapes.delivery` where it may depend on CR;
- active `mtg/cr/**` must not import/call/reference `mtg/shapes/**`, including function-local imports;
- no reusable semantic logic is to be duplicated merely to break a cycle.

Read R6 X `5613155741` and Manager V `5613242327` for the exact dependency graph before implementing later semantic slices.

## R6 15-slice prerequisite graph — navigation copy only

The accepted table is the authority; this copy is here only to accelerate orientation:

1. Layout ownership — none.
2. Install package — 1.
3. Config/authority relocation — 1, 2.
4. Fixtures + ground truth — 2.
5. Infra — 2.
6. MTG CR substrate — 3, 5.
7. MTG shapes substrate — 4, 6.
8. Evidence/composition/thesaurus — 2.
9. Gate 2 -> tests — 4, 7.
10. `foundry_common` dissolution — 5, 6, 7.
11. Codebook/store/membership — 7, 10.
12. Authority law/transport — 11.
13. Operator tooling — 6, 7, 10, 11.
14. Freeze benchmark — 2.
15. Archive & delete — 1 through 14.

Do not infer authorization solely from graph eligibility. A later slice still needs durable Manager selection unless a live Captain directive explicitly and durably grants a bounded continuation frontier.

## Standing controls expected at this handoff

`{AQ4:P, BRIDGE0:U, STEP6:N, MERGE:N}`

Also: no deployment/publication and no authority publication/R2 write unless newer durable state explicitly authorizes it.

## Fresh-session first move

Do **not** answer from this file. First:

1. fetch Issue #1 newest comments;
2. identify the latest `k: K`;
3. read its selected T and associated X/V;
4. inspect live PR/source topology;
5. only then continue management.
