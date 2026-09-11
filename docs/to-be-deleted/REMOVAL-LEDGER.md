# Removal ledger — provisional quarantine

**Status: QUARANTINED, NOT DELETED.**

Created 2026-09-11 on branch `cleanup/obsolete-doc-quarantine-2026-09-11` from accepted implementation head `9f92039eb9c7132a351576c31472eb30a2957a67`.

Purpose: remove obsolete present-tense/execution material from the normal `docs/` retrieval surface without destroying historical evidence. Whole-file moves below preserve the exact existing blob bytes. No in-file passages have been excised in these tranches, so there is no snippet-level removal record yet.

## Admission rule

A document may enter this quarantine only when all of the following are true:

1. its operational task/phase is completed or superseded;
2. it is not the current home of semantic or governance law;
3. the repository ruling-registry deletion gate reports **zero sole-home rulings** for the file;
4. the original bytes are preserved here unchanged;
5. the accepted implementation branch is not modified and nothing is merged by this cleanup.

A file being present here does **not** mean final deletion is authorized. Final deletion requires a later setwise conservation check across the whole proposed deletion set.

## Tranche 1 — obsolete execution directives

| previous path | quarantine path | original blob SHA | registry status | reason |
|---|---|---|---|---|
| `docs/CONSOLIDATION-2A-CLASSIFY-DIRECTIVE.md` | `docs/to-be-deleted/obsolete-directives/CONSOLIDATION-2A-CLASSIFY-DIRECTIVE.md` | `04e5eb40b078fc2eda3c74c401ffedd7e14c3ada` | 6 ruling refs, 0 sole-home; deletable=yes | Session-2A execution contract; explicitly governed by the durable B-migration law and superseded workflow. |
| `docs/CONSOLIDATION-2B-ENUMERATE-DIRECTIVE.md` | `docs/to-be-deleted/obsolete-directives/CONSOLIDATION-2B-ENUMERATE-DIRECTIVE.md` | `b510d3b9706535acb5e2b4f9b019cee263586a42` | 2 ruling refs, 0 sole-home; deletable=yes | Session-2B arithmetic/expansion contract; no judgment authority of its own and explicitly consumes the already-frozen 2A decisions. |
| `docs/CONSOLIDATION-RUN1-DIRECTIVE.md` | `docs/to-be-deleted/obsolete-directives/CONSOLIDATION-RUN1-DIRECTIVE.md` | `75ac9e765979e4b378d361ee5138a0092a77d887` | 1 ruling ref, 0 sole-home; deletable=yes | 2026-08-01 run-1 execution directive; superseded by later consolidation/refoundation state. |
| `docs/DET-PATTERNS-RUN2-DIRECTIVE.md` | `docs/to-be-deleted/obsolete-directives/DET-PATTERNS-RUN2-DIRECTIVE.md` | `3c47b2025b25a9b8ec2af18c709417c6b5fe7aa2` | 3 ruling refs, 0 sole-home; deletable=yes | Session-4 pattern-run directive; governing DET laws and pattern artifacts live elsewhere. |

## Tranche 2 — obsolete zero-ruling session handoffs

This tranche deliberately uses a stronger rule than Tranche 1: every moved file has **zero ruling IDs at all** in the accepted ruling-registry view. Therefore moving the entire tranche cannot remove or jointly orphan a registered ruling. The twelve original blobs total 137,171 bytes.

| previous path | quarantine path | original blob SHA | registry status |
|---|---|---|---|
| `docs/SESSION-HANDOFF-2026-08-02.md` | `docs/to-be-deleted/obsolete-session-handoffs/SESSION-HANDOFF-2026-08-02.md` | `b4012d8929125bad7300612cd57cbf7c38d3c75c` | 0 ruling refs |
| `docs/SESSION-HANDOFF-2026-08-02-EVE.md` | `docs/to-be-deleted/obsolete-session-handoffs/SESSION-HANDOFF-2026-08-02-EVE.md` | `33605ba21757813be5579c6d89eac7b29feb96f6` | 0 ruling refs |
| `docs/SESSION-HANDOFF-2026-08-03.md` | `docs/to-be-deleted/obsolete-session-handoffs/SESSION-HANDOFF-2026-08-03.md` | `8c96ed389a1d94a1ff81b593a3874b6d77e016b1` | 0 ruling refs |
| `docs/SESSION-HANDOFF-2026-08-03-PM.md` | `docs/to-be-deleted/obsolete-session-handoffs/SESSION-HANDOFF-2026-08-03-PM.md` | `8cef9a02a7f1a6dea3678bff84bee463e9c3b3b7` | 0 ruling refs |
| `docs/SESSION-HANDOFF-2026-08-03-EVE.md` | `docs/to-be-deleted/obsolete-session-handoffs/SESSION-HANDOFF-2026-08-03-EVE.md` | `ba46cd0bdd3d43856bf48e37496b3754ec519686` | 0 ruling refs |
| `docs/SESSION-HANDOFF-2026-08-04.md` | `docs/to-be-deleted/obsolete-session-handoffs/SESSION-HANDOFF-2026-08-04.md` | `d3d1e6f4f7aa263dfc3e21e8ad52468a33648cde` | 0 ruling refs |
| `docs/SESSION-HANDOFF-2026-08-05.md` | `docs/to-be-deleted/obsolete-session-handoffs/SESSION-HANDOFF-2026-08-05.md` | `13b31ac082e68ded45b1aed2b64f56badf159f97` | 0 ruling refs |
| `docs/SESSION-HANDOFF-2026-08-06.md` | `docs/to-be-deleted/obsolete-session-handoffs/SESSION-HANDOFF-2026-08-06.md` | `5fbb35d2c567108d17e73748a11d9908188e122f` | 0 ruling refs |
| `docs/SESSION-HANDOFF-2026-08-07.md` | `docs/to-be-deleted/obsolete-session-handoffs/SESSION-HANDOFF-2026-08-07.md` | `ce5ce94ac6d63ab302018e0e0260bcabe5190cd2` | 0 ruling refs |
| `docs/SESSION-HANDOFF-2026-08-07-EVE.md` | `docs/to-be-deleted/obsolete-session-handoffs/SESSION-HANDOFF-2026-08-07-EVE.md` | `cc49e27b0a0bd1bd3c9c787bad1943c683ac7c1c` | 0 ruling refs |
| `docs/SESSION-HANDOFF-2026-08-08.md` | `docs/to-be-deleted/obsolete-session-handoffs/SESSION-HANDOFF-2026-08-08.md` | `1dcb50c10a33cddf48f1829ee41279b8c7fc46ef` | 0 ruling refs |
| `docs/SESSION-HANDOFF-2026-08-09.md` | `docs/to-be-deleted/obsolete-session-handoffs/SESSION-HANDOFF-2026-08-09.md` | `2395024f8a881da60f6f200b1c5224bba2cd2098` | 0 ruling refs |

These are dated session-state snapshots from August. Their evidence remains byte-preserved in quarantine, but they should not compete with the September Issue-#1 K/T control plane as present-tense startup context.

## Explicitly withheld

- `docs/B-MIGRATION-DIRECTIVE.md` — **NOT MOVED**. The current registry marks it sole home for `AG-CLI-01`; moving it out of root `docs/` would remove that ruling from the registry population.
- `docs/B-CONSOLIDATION-REAUDIT-PACKET.md`, `docs/MASTER-HANDOFF*.md`, `docs/PARENT-TREE-CANDIDATES.md`, `docs/WALK-RATIFICATION-EXECUTION-HANDOFF.md`, `docs/TRIAGE-BATCH-2.md`, and `docs/SESSION-HANDOFF-2026-08-04-EVE.md` — not moved because the registry currently reports one or more sole-home rulings.
- `docs/SESSION-HANDOFF-2026-08-01.md` and `docs/SESSION-HANDOFF-2026-08-02-PM.md` — not moved yet. They have no sole-home rulings individually, but they do contain ruling references; they require a setwise conservation check before joining a multi-file tranche.
- AQ4 current contract, dated AQ4 evidence papers, incident records, architecture research, canonical grammar/locality documents, and current refoundation controls — outside these deletion tranches.

## In-file removals

None in Tranches 1–2. If later cleanup removes passages from a surviving file, this ledger will record the exact prior path, heading/line context, removed text, reason, and replacement/canonical home before the edit is made.
