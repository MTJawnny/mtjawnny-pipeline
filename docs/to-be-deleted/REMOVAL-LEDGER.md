# Removal ledger — provisional quarantine

**Status: QUARANTINED, NOT DELETED.**

Created 2026-09-11 on branch `cleanup/obsolete-doc-quarantine-2026-09-11` from accepted implementation head `9f92039eb9c7132a351576c31472eb30a2957a67`.

Purpose: remove obsolete present-tense/execution material from normal retrieval without destroying historical evidence. Whole-file moves preserve exact existing blobs. When a surviving file is rewritten, its complete pre-cleanup blob is preserved under `docs/to-be-deleted/replaced-content/`.

## Admission rule

A document may enter quarantine only when its operational role is completed/superseded, it is not a sole home of semantic/governance law, and the original bytes are preserved. Final deletion requires a later setwise conservation check. The accepted implementation branch is never modified by this cleanup and nothing here authorizes a merge.

## Tranche 1 — obsolete execution directives

| previous path | quarantine path | original blob SHA | registry status | reason |
|---|---|---|---|---|
| `docs/CONSOLIDATION-2A-CLASSIFY-DIRECTIVE.md` | `docs/to-be-deleted/obsolete-directives/CONSOLIDATION-2A-CLASSIFY-DIRECTIVE.md` | `04e5eb40b078fc2eda3c74c401ffedd7e14c3ada` | 6 ruling refs, 0 sole-home | Completed Session-2A execution contract. |
| `docs/CONSOLIDATION-2B-ENUMERATE-DIRECTIVE.md` | `docs/to-be-deleted/obsolete-directives/CONSOLIDATION-2B-ENUMERATE-DIRECTIVE.md` | `b510d3b9706535acb5e2b4f9b019cee263586a42` | 2 ruling refs, 0 sole-home | Completed Session-2B expansion contract. |
| `docs/CONSOLIDATION-RUN1-DIRECTIVE.md` | `docs/to-be-deleted/obsolete-directives/CONSOLIDATION-RUN1-DIRECTIVE.md` | `75ac9e765979e4b378d361ee5138a0092a77d887` | 1 ruling ref, 0 sole-home | Completed run-1 execution directive. |
| `docs/DET-PATTERNS-RUN2-DIRECTIVE.md` | `docs/to-be-deleted/obsolete-directives/DET-PATTERNS-RUN2-DIRECTIVE.md` | `3c47b2025b25a9b8ec2af18c709417c6b5fe7aa2` | 3 ruling refs, 0 sole-home | Completed Session-4 DET execution directive. |

### Tranche-1 setwise ruling check

The four files are safe as a set: every registered ruling they reference retains at least one root-`docs/` home outside quarantine. Relevant IDs are A1, A15, AG-COUNT-01, D4, H-02, R5, G1, A2, A8, and NEW-02. Non-quarantined homes include `B-MIGRATION-DISCOVERY.md`, `B-CONSOLIDATION-REAUDIT-PACKET.md`, `RATIFIED-DIRECTIVES-BATCH-4-6.md`, `WALK-RATIFICATION-EXECUTION-HANDOFF.md`, and `CDR-PROPOSALS.md`.

## Tranche 2 — obsolete session handoffs with zero ruling references

Each moved file appears in the accepted registry's explicit `Documents carrying no ruling reference` list, so this set cannot jointly orphan a registered ruling. The three original blobs total 37,118 bytes.

| previous path | quarantine path | original blob SHA |
|---|---|---|
| `docs/SESSION-HANDOFF-2026-08-06.md` | `docs/to-be-deleted/obsolete-session-handoffs/SESSION-HANDOFF-2026-08-06.md` | `5fbb35d2c567108d17e73748a11d9908188e122f` |
| `docs/SESSION-HANDOFF-2026-08-07.md` | `docs/to-be-deleted/obsolete-session-handoffs/SESSION-HANDOFF-2026-08-07.md` | `ce5ce94ac6d63ab302018e0e0260bcabe5190cd2` |
| `docs/SESSION-HANDOFF-2026-08-09.md` | `docs/to-be-deleted/obsolete-session-handoffs/SESSION-HANDOFF-2026-08-09.md` | `2395024f8a881da60f6f200b1c5224bba2cd2098` |

### Tranche-2 correction record

Commit `3d0c3116f8dda182f9ae869282e8e8b346d553d2` initially moved twelve handoffs after I conflated `deletable=yes` with the separate zero-ruling list. The mistake was caught before expansion. Nine handoffs with corroborated ruling references were restored byte-for-byte in `31c0187e4248e1b2f5026e375f08cb33e3481d74`. No accepted branch was touched and no content was lost.

## Tranche 3 — completed next-session specification

| previous path | quarantine path | original blob SHA | permanent successor |
|---|---|---|---|
| `docs/NEXT-SESSION-CR-NORMALIZATION.md` | `docs/to-be-deleted/completed-session-specs/NEXT-SESSION-CR-NORMALIZATION.md` | `f11c5f79263d07623b15c0c5538785f3bc7d8294` | `docs/CR-REFRESH-2026-08-09.md` |

This file has zero ruling references, begins `DONE — 2026-08-09`, points to the completed refresh record, and repository search found no current reference to its filename.

## Tranche 4 — replace stale present-tense refoundation state

These files remain at their live paths, but stale bootstrap/current-state prose is replaced with minimal durable routing. The complete old blobs are preserved, not summarized.

| live file | preserved pre-cleanup blob | original blob SHA | removal/replacement reason |
|---|---|---|---|
| `refoundation/MANAGER-START.md` | `docs/to-be-deleted/replaced-content/refoundation-MANAGER-START.pre-cleanup.md` | `5c3aed7de8806f3928dc9d16b04ef11752deda86` | Old text instructed a fresh Manager to adjudicate the original P0.1 architecture task and cited August bootstrap refs. Replaced by latest-K/current-protocol routing. |
| `refoundation/ACTIVE-PHASE.yaml` | `docs/to-be-deleted/replaced-content/refoundation-ACTIVE-PHASE.pre-cleanup.yaml` | `a8a309d4324fad23565b164b312110d44fbbb857` | Old replaceable state still said `PATH_E_M3_STATIC_DIAGNOSTIC_PILOT` and carried M3/browser-specific reasoning axes. Replaced from live Issue-#1 checkpoint `K-20260911-EXPERIMENTS-MIGRATION-S9-ACCEPTED-RECOVERY`: accepted S9 head, `a: 0`, migration-first, unchanged controls. |
| `refoundation/README.md` | `docs/to-be-deleted/replaced-content/refoundation-README.pre-cleanup.md` | `01408a1b746a28bbf3f85fd3fedde29b4b8e15f0` | Old README still presented the August P0.1/bootstrap hard stop and old read order as current. Replaced by the current Issue-#1/SESSION-PROTOCOL routing model. |

Source for the replacement current-state fields: live Issue #1 Manager V accepts S9 at `9f92039eb9c7132a351576c31472eb30a2957a67`; the following K `K-20260911-EXPERIMENTS-MIGRATION-S9-ACCEPTED-RECOVERY` records `h` at that commit, `a: 0`, strategy `MIGRATION_FIRST`, and controls `{AQ4:P,BRIDGE0:U,STEP6:N,MERGE:N}`. Root `CLAUDE.md` independently states that Issue #1 outranks refoundation phase context.

## Explicitly withheld

- `docs/B-MIGRATION-DIRECTIVE.md` — sole home for `AG-CLI-01`; not moved.
- `docs/B-CONSOLIDATION-REAUDIT-PACKET.md`, `docs/MASTER-HANDOFF*.md`, `docs/PARENT-TREE-CANDIDATES.md`, `docs/WALK-RATIFICATION-EXECUTION-HANDOFF.md`, `docs/TRIAGE-BATCH-2.md`, and `docs/SESSION-HANDOFF-2026-08-04-EVE.md` — blocked by one or more sole-home rulings.
- Other dated session handoffs carrying corroborated ruling references — withheld pending setwise ruling-conservation proof.
- AQ4 current contract, dated AQ4 evidence papers, incident records, architecture research, canonical grammar/locality documents, and current semantic law — outside these deletion tranches.

## In-file removals / replacements

Tranche 4 is the first in-place replacement. Instead of copying individual snippets here, the **entire exact pre-cleanup version** of each modified file is preserved under `replaced-content/`, with its former path and blob SHA recorded above. That is strictly more complete than a snippet ledger and makes every removed passage recoverable verbatim.
