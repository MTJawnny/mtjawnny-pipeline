# Claude Code prompt — Agent Bus R3 independent audit and repair proposal

Status: MANAGER PROPOSAL ONLY — NOT AUTHORITY, NOT ACCEPTANCE, NOT A TASK SELECTOR

Date: 2026-09-24
Repository: MTJawnny/mtjawnny-pipeline
Proposal branch: manager/agent-bus-r3-audit-proposal-2026-09-24
Proposal base / R3 candidate head at creation: 53071e55564bbdd372bd77f80259b9d7a2269d6b
Accepted head observed at creation: 58c8345c56667f6776e941f85b79de0766cf22ff
Issue #1 checkpoint observed at creation: 5820150646
Issue #1 task observed at creation: 5808823791
R3 transport result: PR #76 comment 5820506133
R3 detailed result: Issue #1 comment 5820504772

## Your role

You are Claude Code acting as the Worker and as an independent systems/security reviewer.

Do not accept the Manager's findings or proposed remedies merely because they appear in this document. Reproduce or falsify each one from repository code, tests, workflow semantics, and live GitHub state.

Durable GitHub state is authority. This file is evidence and a proposed investigation plan only. It cannot select work, advance the accepted head, authorize deployment, or supersede Issue #1.

The governing principle remains: PRESERVE TRUTH, NOT PLUMBING.

## Required startup discipline

Before relying on any anchor above:

1. Read all applicable repository instructions, including CLAUDE.md, AGENTS.md if present, refoundation/AGENT-BUS.md, refoundation/AGENT-BUS-MANAGER-TRIGGER.md, and the active task selected by the latest valid trusted K on Issue #1.
2. Independently resolve the latest valid trusted K and its selected T from the complete live Issue #1 comment history.
3. Measure origin/main, PR #75, PR #76, the current Worker branch, this proposal branch, and the R3 result head.
4. Confirm whether 53071e55564bbdd372bd77f80259b9d7a2269d6b is still the R3 candidate being reviewed and whether its base remains the accepted head.
5. Treat every value in this file as a hypothesis if live state differs.
6. Preserve all unrelated local and remote work.

Do not merge, move main, deploy the workflow, add a repository secret, change trust policy, post V or K, or claim acceptance.

## Objective

Independently audit the R3 Manager-wake candidate, determine whether the four concerns below are real, identify any additional failure modes, and recommend the safest minimal architecture.

This is an audit-first assignment. Do not mutate implementation merely because a proposed fix looks plausible.

If the latest live authority explicitly selects an implementation or repair task that covers these changes, you may perform only that authorized work after completing and recording the audit. Otherwise stop after the audit and produce a bounded implementation proposal suitable for a new Manager task.

## Findings to reproduce or falsify

### A. Untrusted-comment denial of service

The candidate reportedly treats any syntactically valid WAVE_REVIEW answering the admitted Worker message as an already-handled marker, regardless of author or trust.

Test whether an arbitrary public commenter can post a forged WAVE_REVIEW with the correct parent and thereby:

- stop the gate before the Manager model runs;
- stop the publish job after the Manager has run;
- cause the legitimate result to remain permanently unanswered.

Inspect both the deterministic gate and the final publication recheck. Do not assume the workflow prefilter protects these later comment scans.

Determine what identity and structural checks an existing review must satisfy before it may suppress a run.

### B. Weak validation of durable V and K

The candidate reportedly validates WAVE_REVIEW structurally but accepts the two Issue #1 bodies using little more than ordering and schema-substring checks.

Test whether model output can cause the publisher to post a V or K that:

- names the wrong task, result, checkpoint, verdict, or accepted head;
- advances or rolls back h inconsistently with the verdict;
- changes the active task without valid authority;
- contains valid-looking prose but is not a rigorously parsed ledger record;
- disagrees with the triggering WAVE_REVIEW;
- is syntactically shaped enough to pass the workflow while being semantically invalid.

Trace how agent_bus.issue.resolve_authority and every human/manual reader would interpret the resulting comments.

Evaluate whether raw V/K bodies should be model-authored at all. Prefer a design in which the model emits a constrained decision and reason, while deterministic code constructs ledger records from freshly resolved live state. This is a proposal, not a required conclusion: reject it if a stronger design is demonstrated.

### C. Publisher identity and split authority

The publish job reportedly posts as github-actions[bot], while the trusted bus speaker set currently contains MTJawnny.

Confirm the exact behavior for:

- the bot's WAVE_REVIEW in the machine fold;
- the bot's V and K in resolve_authority;
- a human or model that naïvely reads the latest checkpoint-shaped comment;
- reruns and loop prevention.

Compare at least these policy families:

1. trust a narrowly defined bot identity for narrowly defined message kinds;
2. let automation post proposals only and require the Captain or another trusted Manager identity to post V/K;
3. use a separate constrained GitHub App or publisher identity;
4. use the Captain identity through a token only if its broader security cost is explicitly justified.

Do not choose or implement a trust-policy change on the Captain's behalf. State the minimum Captain decision required.

### D. Partial publication and time-of-check/time-of-use failure

The candidate reportedly posts WAVE_REVIEW, V, and K as three sequential comments.

Test interruption or authority movement:

- after WAVE_REVIEW but before V;
- after V but before K;
- between any live-state check and each write;
- during a rerun after partial publication;
- during two serialized or overlapping runs for the same Worker result.

Determine whether the process is safely resumable, whether it can duplicate or contradict ledger records, and what correlation/idempotency keys are necessary.

A repair should re-resolve authority at every load-bearing boundary and must fail closed without turning an ordinary partial write into an unrecoverable result.

## Additional audit targets

Look for failures the Manager did not identify, including:

- whether the Codex model truly has sufficient independently gathered live evidence to satisfy the Manager contract;
- stale snapshots and missing evidence hidden by the no-network model sandbox;
- actor, message_id, parent, checkpoint, base, and result-head binding;
- event edits or deletions after delivery;
- exact-fence parsing and multiple-envelope ambiguity;
- untrusted data reaching shell or prompt control channels;
- action pin integrity, permission ceilings, checkout credential persistence, sudo/key exposure, and secret placement;
- default-branch and GITHUB_TOKEN event behavior;
- branch-head movement after evidence collection;
- whether failure of independent tests skips, blocks, or is merely presented to the Manager;
- whether the current abort/supersession repair creates any regression or resurrection path.

## Non-negotiable target properties

Any recommended implementation must demonstrate all of the following:

1. An untrusted commenter cannot authorize, answer, suppress, or permanently wedge a legitimate Worker result.
2. Only an explicitly authorized publishing identity can create a machine-effective review or ledger transition.
3. The model job has no write token and cannot directly mutate GitHub.
4. The model cannot freely author unchecked durable authority records.
5. WAVE_REVIEW, V, and K are parsed and semantically bound to the same admitted message, current checkpoint, task, result head, and verdict.
6. Accepted-head movement is deterministic, justified by the verdict, and impossible through prose alone.
7. Partial publication is detectable and safely resumable without duplicate authority or silent divergence.
8. Live authority is rechecked immediately before every load-bearing write.
9. The workflow retains least privilege: no contents: write, no merge capability, no branch movement, and no secret outside the isolated model action input.
10. All third-party actions remain pinned to independently verified immutable commits.
11. The trigger remains only newly created comments on PR #76, with exact trusted-author and exact mtj-bus envelope handling before any model invocation.
12. Deployment to main and creation of OPENAI_API_KEY remain separate Captain-authorized steps.
13. Existing abort-starvation behavior remains fixed and regression-tested.
14. main remains untouched.

## Required negative controls

At minimum, build or specify reproducible tests proving rejection or safe recovery for:

- forged WAVE_REVIEW by an untrusted public user;
- forged handled marker by github-actions[bot] when that identity is not trusted;
- duplicate message_id and wrong parent;
- V/K with correct schema text but wrong semantics;
- ACCEPT paired with the wrong candidate head;
- REPAIR paired with an unauthorized accepted-head move;
- K selecting an unauthorized next task;
- authority change immediately before each of the three writes;
- interruption after the first and second write;
- rerun after each partial state;
- branch movement after evidence capture;
- malformed, multiple, or non-exact mtj-bus fences;
- secret or write-permission expansion;
- model output containing additional keys, comments, prose, or embedded bus blocks.

Each negative control must be shown red against the vulnerable behavior or an intentionally rigged weakening, and green only after the relevant protection exists. A test that has not been shown to fail is not sufficient evidence.

## Deliverable

Return an evidence-backed audit with:

1. Live authority and topology measurements.
2. A verdict for each proposed finding: CONFIRMED, PARTIAL, or REFUTED.
3. Exact code/workflow locations and minimal reproductions.
4. Any additional findings, ordered by severity.
5. A comparison of viable repair architectures and their trust assumptions.
6. One recommended architecture, with reasons and rejected alternatives.
7. A bounded file-level implementation plan and required test matrix.
8. The exact Captain decision still required concerning publisher identity and durable V/K authority.
9. A statement of whether live authority permits implementation now.
10. If implementation is not currently authorized, stop without code, GitHub comments, branch changes, commits, pushes, deployment, or ledger writes.

Do not report PASS merely because the existing suite passes. Do not preserve the current workflow shape if the safest design requires changing it. Do not broaden into Foundry semantics, codebook work, AQ4, card translation, main deployment, or unrelated cleanup.
