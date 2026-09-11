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

### Tranche-1 setwise ruling check

The four files are safe as a set, not just individually: every registered ruling they reference retains at least one root-`docs/` home outside this quarantine. The relevant IDs are A1, A15, AG-COUNT-01, D4, H-02, R5, G1, A2, A8, and NEW-02. Canonical/non-quarantined homes include `B-MIGRATION-DISCOVERY.md`, `B-CONSOLIDATION-REAUDIT-PACKET.md`, `RATIFIED-DIRECTIVES-BATCH-4-6.md`, `WALK-RATIFICATION-EXECUTION-HANDOFF.md`, and `CDR-PROPOSALS.md`. No registered ruling becomes homeless when Tranche 1 is excluded from the root-doc population.

## Tranche 2 — obsolete session handoffs with zero ruling references

For this tranche the criterion is stronger than individual deletability: each moved file appears in the accepted registry's explicit **"Documents carrying no ruling reference"** list. Moving this set therefore cannot jointly orphan a registered ruling. The three original blobs total 37,118 bytes.

| previous path | quarantine path | original blob SHA | registry status |
|---|---|---|---|
| `docs/SESSION-HANDOFF-2026-08-06.md` | `docs/to-be-deleted/obsolete-session-handoffs/SESSION-HANDOFF-2026-08-06.md` | `5fbb35d2c567108d17e73748a11d9908188e122f` | 0 ruling refs |
| `docs/SESSION-HANDOFF-2026-08-07.md` | `docs/to-be-deleted/obsolete-session-handoffs/SESSION-HANDOFF-2026-08-07.md` | `ce5ce94ac6d63ab302018e0e0260bcabe5190cd2` | 0 ruling refs |
| `docs/SESSION-HANDOFF-2026-08-09.md` | `docs/to-be-deleted/obsolete-session-handoffs/SESSION-HANDOFF-2026-08-09.md` | `2395024f8a881da60f6f200b1c5224bba2cd2098` | 0 ruling refs |

These are dated session-state snapshots from August. Their evidence remains byte-preserved in quarantine, but they should not compete with the September Issue-#1 K/T control plane as present-tense startup context.

### Tranche-2 correction record

Commit `3d0c3116f8dda182f9ae869282e8e8b346d553d2` initially moved twelve session handoffs after I incorrectly conflated the registry's **deletable=yes** column with its separate **no ruling reference** list. Before expanding cleanup further, I re-read the registry and corrected the mistake. Nine handoffs that contain corroborated ruling references were restored byte-for-byte to their original root `docs/` paths in commit `31c0187e4248e1b2f5026e375f08cb33e3481d74`. No accepted branch was touched, no content was lost, and the incorrect stronger claim is not carried forward here.

## Tranche 3 — completed next-session specification

| previous path | quarantine path | original blob SHA | registry status | permanent successor |
|---|---|---|---|---|
| `docs/NEXT-SESSION-CR-NORMALIZATION.md` | `docs/to-be-deleted/completed-session-specs/NEXT-SESSION-CR-NORMALIZATION.md` | `f11c5f79263d07623b15c0c5538785f3bc7d8294` | 0 ruling refs | `docs/CR-REFRESH-2026-08-09.md` |

The document itself begins `DONE — 2026-08-09` and points readers to the completed CR-refresh record. Repository search at the accepted head found no other file referencing this filename. Its exact bytes are retained here as execution-history evidence; the completed refresh record remains in normal `docs/` retrieval.

## Explicitly withheld

- `docs/B-MIGRATION-DIRECTIVE.md` — **NOT MOVED**. The current registry marks it sole home for `AG-CLI-01`; moving it out of root `docs/` would remove that ruling from the registry population.
- `docs/B-CONSOLIDATION-REAUDIT-PACKET.md`, `docs/MASTER-HANDOFF*.md`, `docs/PARENT-TREE-CANDIDATES.md`, `docs/WALK-RATIFICATION-EXECUTION-HANDOFF.md`, `docs/TRIAGE-BATCH-2.md`, and `docs/SESSION-HANDOFF-2026-08-04-EVE.md` — not moved because the registry currently reports one or more sole-home rulings.
- Other dated session handoffs — not moved in Tranche 2 if they carry even corroborated ruling references. They require a setwise ruling-conservation check before any multi-file relocation.
- AQ4 current contract, dated AQ4 evidence papers, incident records, architecture research, canonical grammar/locality documents, and current refoundation controls — outside these deletion tranches.

## In-file removals

None in Tranches 1–3. If later cleanup removes passages from a surviving file, this ledger will record the exact prior path, heading/line context, removed text, reason, and replacement/canonical home before the edit is made.
