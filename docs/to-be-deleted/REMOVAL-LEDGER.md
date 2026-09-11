# Removal ledger — provisional quarantine

**Status: QUARANTINED, NOT DELETED.**

Created 2026-09-11 on branch `cleanup/obsolete-doc-quarantine-2026-09-11` from accepted implementation head `9f92039eb9c7132a351576c31472eb30a2957a67`.

Purpose: remove obsolete present-tense/execution material from normal retrieval without destroying historical evidence. Full source blobs are preserved under this directory. Historical root paths use compact tombstones where keeping the tracked document population is needed for existing guards.

## Safety model

- No merge is authorized by this cleanup.
- The accepted implementation branch is untouched.
- Final deletion requires a later setwise conservation decision.
- No Gate-2 baseline/ratchet update is authorized or performed.
- For root `docs/*.md` candidates, a compact tombstone remains at the original path so the ruling-registry tracked-document population does not shrink.
- Ruling-bearing tombstones reproduce the same raw ruling-reference multiplicity as their original document, preserving `documents`, `ruling_ids`, `total_references`, `corroborated`, and `sole_home` inputs by construction.

## Tranche 1 — obsolete execution directives

| root tombstone | quarantined full original | original blob SHA | original registry refs |
|---|---|---|---:|
| `docs/CONSOLIDATION-2A-CLASSIFY-DIRECTIVE.md` | `docs/to-be-deleted/obsolete-directives/CONSOLIDATION-2A-CLASSIFY-DIRECTIVE.md` | `04e5eb40b078fc2eda3c74c401ffedd7e14c3ada` | 7 raw refs / 6 IDs |
| `docs/CONSOLIDATION-2B-ENUMERATE-DIRECTIVE.md` | `docs/to-be-deleted/obsolete-directives/CONSOLIDATION-2B-ENUMERATE-DIRECTIVE.md` | `b510d3b9706535acb5e2b4f9b019cee263586a42` | 2 raw refs / 2 IDs |
| `docs/CONSOLIDATION-RUN1-DIRECTIVE.md` | `docs/to-be-deleted/obsolete-directives/CONSOLIDATION-RUN1-DIRECTIVE.md` | `75ac9e765979e4b378d361ee5138a0092a77d887` | 1 raw ref / 1 ID |
| `docs/DET-PATTERNS-RUN2-DIRECTIVE.md` | `docs/to-be-deleted/obsolete-directives/DET-PATTERNS-RUN2-DIRECTIVE.md` | `3c47b2025b25a9b8ec2af18c709417c6b5fe7aa2` | 3 raw refs / 3 IDs |

Setwise check: every referenced ruling also retains a non-quarantined authoritative/canonical home. Relevant IDs are A1, A15, AG-COUNT-01, D4, H-02, R5, G1, A2, A8, and NEW-02.

## Tranche 2 — obsolete session handoffs carrying no ruling reference

| root tombstone | quarantined full original | original blob SHA |
|---|---|---|
| `docs/SESSION-HANDOFF-2026-08-06.md` | `docs/to-be-deleted/obsolete-session-handoffs/SESSION-HANDOFF-2026-08-06.md` | `5fbb35d2c567108d17e73748a11d9908188e122f` |
| `docs/SESSION-HANDOFF-2026-08-07.md` | `docs/to-be-deleted/obsolete-session-handoffs/SESSION-HANDOFF-2026-08-07.md` | `ce5ce94ac6d63ab302018e0e0260bcabe5190cd2` |
| `docs/SESSION-HANDOFF-2026-08-09.md` | `docs/to-be-deleted/obsolete-session-handoffs/SESSION-HANDOFF-2026-08-09.md` | `2395024f8a881da60f6f200b1c5224bba2cd2098` |

### Correction record

Commit `3d0c3116f8dda182f9ae869282e8e8b346d553d2` temporarily moved twelve handoffs after `deletable=yes` was mistakenly conflated with the registry's zero-ruling list. The error was caught before further expansion. Nine handoffs with corroborated references were restored byte-for-byte in `31c0187e4248e1b2f5026e375f08cb33e3481d74`.

## Tranche 3 — completed next-session specification

| root tombstone | quarantined full original | original blob SHA | durable successor |
|---|---|---|---|
| `docs/NEXT-SESSION-CR-NORMALIZATION.md` | `docs/to-be-deleted/completed-session-specs/NEXT-SESSION-CR-NORMALIZATION.md` | `f11c5f79263d07623b15c0c5538785f3bc7d8294` | `docs/CR-REFRESH-2026-08-09.md` |

The original carried zero ruling references, explicitly began `DONE — 2026-08-09`, and repository search found no current consumer of its filename.

## Tranche 4 — stale present-tense refoundation state replaced in place

| live file | complete pre-cleanup copy | original blob SHA | reason |
|---|---|---|---|
| `refoundation/MANAGER-START.md` | `docs/to-be-deleted/replaced-content/refoundation-MANAGER-START.pre-cleanup.md` | `5c3aed7de8806f3928dc9d16b04ef11752deda86` | Old startup still directed P0.1 adjudication and August bootstrap refs. |
| `refoundation/ACTIVE-PHASE.yaml` | `docs/to-be-deleted/replaced-content/refoundation-ACTIVE-PHASE.pre-cleanup.yaml` | `a8a309d4324fad23565b164b312110d44fbbb857` | Old replaceable state still claimed the M3 static-browser pilot. |
| `refoundation/README.md` | `docs/to-be-deleted/replaced-content/refoundation-README.pre-cleanup.md` | `01408a1b746a28bbf3f85fd3fedde29b4b8e15f0` | Old README still presented August bootstrap/P0.1 state as current. |

Replacement state comes from live Issue #1: Manager V accepted S9 at `9f92039eb9c7132a351576c31472eb30a2957a67`; checkpoint `K-20260911-EXPERIMENTS-MIGRATION-S9-ACCEPTED-RECOVERY` records `h` at that commit, `a: 0`, strategy `MIGRATION_FIRST`, and controls `{AQ4:P,BRIDGE0:U,STEP6:N,MERGE:N}`. Root `CLAUDE.md` independently says Issue #1 outranks refoundation phase context.

## Explicitly withheld

- `docs/B-MIGRATION-DIRECTIVE.md` — sole home for `AG-CLI-01`.
- `docs/B-CONSOLIDATION-REAUDIT-PACKET.md`, `docs/MASTER-HANDOFF*.md`, `docs/PARENT-TREE-CANDIDATES.md`, `docs/WALK-RATIFICATION-EXECUTION-HANDOFF.md`, `docs/TRIAGE-BATCH-2.md`, and `docs/SESSION-HANDOFF-2026-08-04-EVE.md` — blocked by sole-home rulings.
- Other dated handoffs carrying corroborated ruling references — withheld pending setwise proof.
- AQ4 current contract, dated AQ4 evidence, incident records, architecture research, canonical grammar/locality documents, and current semantic law.

## Removed-content preservation

For Tranches 1–3, the entire original file is retained under its quarantine path while the old root path is a compact tombstone. For Tranche 4, the entire exact pre-cleanup file is retained under `replaced-content/`. This is intentionally more complete than a snippet-only `what was removed` file: every removed passage is recoverable verbatim together with its former path and blob SHA.
