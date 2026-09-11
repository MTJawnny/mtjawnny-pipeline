# Removal ledger — provisional quarantine

**Status: QUARANTINED, NOT DELETED.**

Created 2026-09-11 on branch `cleanup/obsolete-doc-quarantine-2026-09-11` from accepted implementation head `9f92039eb9c7132a351576c31472eb30a2957a67`.

Purpose: remove obsolete present-tense/execution material from the normal `docs/` retrieval surface without destroying historical evidence. Whole-file moves below preserve the exact existing blob bytes. No in-file passages were excised in this tranche, so there is no snippet-level removal record yet.

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

## Explicitly withheld from this tranche

- `docs/B-MIGRATION-DIRECTIVE.md` — **NOT MOVED**. The current registry marks it sole home for `AG-CLI-01`; moving it out of root `docs/` would remove that ruling from the registry population.
- `docs/B-CONSOLIDATION-REAUDIT-PACKET.md`, `docs/MASTER-HANDOFF*.md`, `docs/PARENT-TREE-CANDIDATES.md`, `docs/WALK-RATIFICATION-EXECUTION-HANDOFF.md`, `docs/TRIAGE-BATCH-2.md`, and `docs/SESSION-HANDOFF-2026-08-04-EVE.md` — not moved because the registry currently reports one or more sole-home rulings.
- AQ4 current contract, dated AQ4 evidence papers, incident records, architecture research, canonical grammar/locality documents, and current refoundation controls — outside this deletion tranche.

## In-file removals

None in tranche 1. If later cleanup removes passages from a surviving file, this ledger will record the exact prior path, heading/line context, removed text, reason, and replacement/canonical home before the edit is made.
