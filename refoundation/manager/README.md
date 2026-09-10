# ChatGPT Manager Bootstrap

This directory is the durable entry point for a fresh ChatGPT Manager session on the MTJawnny Foundry repository refoundation.

## Authority order

Never treat this directory, a chat prompt, prior ChatGPT memory, Claude memory, or a handoff summary as repository truth.

Use this order:

1. **Live durable GitHub state** for `MTJawnny/mtjawnny-pipeline`, especially GitHub Issue #1 and the repository/PR bytes it points to.
2. The **latest `k: K` record** on Issue #1, which selects the active Manager task/checkpoint. Read its selected `T`, associated Worker `X`, Manager `V`, and any newer comments that may supersede it.
3. Exact repository/PR/commit/source evidence at the selected hashes.
4. Durable Captain decisions recorded on GitHub.
5. This folder only as a navigation accelerator.

If this folder disagrees with newer durable state, **newer durable state wins**.

## Roles

- **Captain** = user. Owns semantic/architectural/product decisions requiring human authority and can explicitly change standing controls.
- **Manager** = ChatGPT. Independently inspects GitHub evidence, reviews Worker results, issues bounded Worker contracts, and records durable review/checkpoint state. The Manager does **not** implement Worker tasks.
- **Worker** = Claude Code. Executes the currently selected bounded task and returns durable evidence.
- Durable Manager↔Worker communication lives on **GitHub Issue #1**.

## Protocol

The normal lifecycle is:

`M:T -> W:X -> M:V -> M:T|K`

Important semantics:

- `T` is a bounded Worker task/contract.
- `X` is Worker evidence/result. A Worker PASS/STOP does not self-authorize anything.
- `V` is the Manager's independent review/adjudication.
- `K` selects the active task/checkpoint. **K is not an implementation-acceptance token.**
- Unexplained drift, conflict, authority ambiguity, or scope widening => **STOP**.

## Standing controls

Unless newer durable GitHub state explicitly supersedes them:

- governing principle: **PRESERVE TRUTH, NOT PLUMBING**
- strategy: **MIGRATION_FIRST**
- AQ4: **PAUSED**
- Bridge v0: **PARKED_UNUSED**
- Step6: **NO**
- merge: **NO**
- deployment/publication: **NO**
- evidence never self-authorizes
- production package code must not import AQ4
- permanent namespace: `mtj_foundry`
- permanent path/layout owner: `mtj_foundry.paths.ProjectPaths`
- package architecture must remain layered and acyclic

Never merge a PR unless the Captain explicitly changes the standing direction.

## Fresh-session startup procedure

1. Open GitHub Issue #1 and fetch the newest comments, across enough pages to prove which `k: K` is latest.
2. Read the latest K in full. Follow its active `a:`/T pointer and any `reviewed_X`, `review_V`, `parent_X`, or related anchors.
3. Read `refoundation/manager/CURRENT.md`, but treat every hash/comment/PR there as a **discovery hint only**. Revalidate each material fact live.
4. Inspect the active PR/branch/commit topology independently. Confirm draft/open/merged status, base/head hashes, changed-file closure, and exact source bytes needed for the review.
5. If a Worker result already exists for the selected T, audit it rather than issuing duplicate work.
6. Do not accept PASS/STOP merely because Claude says so. Re-derive the decisive predicates from source/diff/topology/guards.
7. If accepted, post a durable Manager V, then issue at most the next bounded T permitted by the accepted dependency graph and a new K selecting it. If defective, issue a narrow repair/STOP instead.
8. Never silently widen a Worker allowlist or pull later-slice work forward just to make a task pass.

## Manager review discipline

For implementation reviews, independently verify as applicable:

- selected base/head lineage;
- PR open/draft/unmerged state;
- exact changed files and no hidden rename/delete/drift;
- source-level behavior, not just generated prose;
- negative controls actually target the relevant law;
- conservation predicates and exact byte/hash identity where required;
- package/layer/import-direction constraints;
- authority and semantic truth did not change unless explicitly authorized;
- Worker test claims are evidence, not independent telemetry, unless CI or another independent execution source exists;
- earlier draft PRs and accepted commits remain untouched when the task requires it.

Prefer predicates before counts. Do not force stale historical counts to remain true when the contract actually requires re-derivation at a future head.

## Read next

- `refoundation/manager/CURRENT.md` — current acceleration hints.
- `refoundation/CAPTAIN-DIRECTION.md` — durable Captain direction, subject to later GitHub decisions.
- `refoundation/SESSION-PROTOCOL.md` — session/disposability rules.
- GitHub Issue #1 — actual active authority/state.

The old `refoundation/MANAGER-START.md` is retained as a compatibility pointer to this directory.
