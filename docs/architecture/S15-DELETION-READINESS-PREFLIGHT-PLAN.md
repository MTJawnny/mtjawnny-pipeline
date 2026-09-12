# S15 Deletion-Readiness Preflight Plan

Status: **PLANNED / NON-EXECUTING**  
Objective: **4 of 5**  
Fresh Claude session: **REQUIRED**  
Target migration slice: **S15**  
Implementation authorization: **NONE**

## Mission

Build a setwise, evidence-backed deletion/readiness matrix for the legacy `experiments/` tree and other S15 retirement targets so that S15 can be executed as a controlled conservation step rather than a late-stage archaeology exercise.

This preflight does **not delete anything**. It classifies, traces dependencies, records blockers, and designs the final conservation proof.

## Timing rule

This work may begin now as a planning exercise, but any destructive S15 contract must be regenerated/revalidated against the **actual accepted pre-S15 head after S10–S14**.

A file classified “safe to delete” today may acquire or lose consumers during S10–S14. Therefore every classification must carry:

- head measured;
- dependency evidence;
- migration prerequisite;
- revalidation requirement.

## Existing cleanup evidence

The cleanup branch already contains `docs/to-be-deleted/REMOVAL-LEDGER.md`, which establishes a quarantine-first safety model and records:

- obsolete execution directives moved behind compact tombstones;
- zero-ruling historical handoffs quarantined;
- a completed session specification quarantined;
- stale refoundation present-tense state replaced while preserving originals;
- explicitly withheld documents with sole-home/corroborated ruling or architecture value.

That ledger is evidence, not blanket deletion authorization. S15 must reconcile it with the then-current migrated repository.

## Inventory scope

Mechanically enumerate all tracked and relevant ignored/runtime content implicated by S15, including at minimum:

- `experiments/**` Python modules;
- `experiments/moves/**` and other live fixtures;
- `experiments/measure/**` legacy thesaurus measurement;
- AQ4 assets still under legacy paths before S14;
- one-off executors and schema migrations;
- census/probe/reporter scripts;
- legacy batch/triage machinery;
- generated-output path assumptions and `.gitignore` rules;
- docs embedded under `experiments/`;
- `.claude/commands` or other command references to legacy paths;
- tests importing or invoking legacy modules;
- workflows/scripts/subprocess commands referring to legacy paths;
- root docs that name legacy files as current operational steps;
- quarantine/tombstone paths intended for eventual deletion.

Also search for string references to candidate paths so deletion does not rely only on Python import analysis.

## Classification model

Every candidate path must land in exactly one category:

1. **KEEP_PERMANENT** — still canonical/current after migration.
2. **MIGRATED_REPLACED** — permanent successor exists; old path may be retired after conservation proof.
3. **ARCHIVE_EVIDENCE** — no runtime role, but historical/decision evidence must remain in a non-operational location.
4. **DELETE_SAFE** — no runtime, governance, evidence, test, or unique-document role remains after prerequisites.
5. **BLOCKED_LIVE_CONSUMER** — deletion would break a current caller/test/command/workflow.
6. **BLOCKED_TRUTH_HOME** — file retains unique or insufficiently preserved semantic/ruling/incident/research evidence.
7. **BLOCKED_UNKNOWN** — role cannot yet be established mechanically.

No candidate may be deleted from an “probably obsolete” category.

## Required dependency proof

For every `MIGRATED_REPLACED` or `DELETE_SAFE` candidate, capture evidence across:

- tracked imports;
- dynamic imports;
- subprocess invocations;
- command files;
- tests/fixtures;
- workflows;
- docs treated as current instructions;
- ruling-registry participation;
- authority manifests/selectors;
- baseline/ratchet inputs;
- generated-output consumers;
- package data/config references;
- exact path string search.

Where a successor exists, record the successor path/API and the accepted migration slice that created it.

## Truth-preservation proof

Deletion readiness must distinguish **plumbing** from **truth**.

Before any evidence-bearing file is retired, determine whether its information exists elsewhere with equivalent authority/provenance. Particular caution applies to:

- sole-home ruling references;
- ratified semantic law;
- incident records;
- benchmark precommitments;
- research/evidence that justifies a permanent behavior;
- historical negative controls that remain the only explanation of a guard;
- fixture data consumed by tests;
- codebook authority selectors and succession records.

If truth has only been summarized but not preserved with sufficient provenance, classify `ARCHIVE_EVIDENCE` or `BLOCKED_TRUTH_HOME`, not `DELETE_SAFE`.

## Ruling-registry/setwise conservation

S15 must not discover after deletion that document topology was part of a guard.

The preflight should design a before/after setwise comparison covering the registry’s meaningful inputs and outputs, including:

- tracked document population;
- ruling IDs;
- raw reference multiplicity where relevant;
- corroborated versus sole-home status;
- known false-positive state that is intentionally preserved until separately repaired;
- baseline/ratchet values and directions.

If S15 is intended to retire the old registry mechanism itself, the replacement must prove equivalent or stronger truth preservation before the old topology guard is removed.

## Generated/runtime boundary

S15 also owns final cleanup of legacy generated-output assumptions. Inventory:

- ignored output directories;
- tracked files still regenerated by legacy tools;
- generated caches that became source-like controls;
- stale `.gitignore` exceptions;
- scripts that expect `experiments/out` or legacy review paths;
- data that must move to permanent `var/`, config, fixtures, or authority storage before legacy deletion.

Do not conflate “ignored” with “safe to delete”; ignored runtime state may still be required to run a live tool and therefore expose an incomplete migration.

## Quarantine reconciliation

Compare the existing cleanup branch ledger against the actual pre-S15 accepted tree and classify each quarantined/tombstoned item as:

- preserve indefinitely as evidence;
- move to final history/archive home;
- safe for final deletion;
- restore because later evidence shows continued live value.

The cleanup branch is provisional evidence; S15 is the first point at which final deletion decisions may be proposed.

## Negative controls

The final S15 verification design must be capable of detecting at least:

- deletion of a file with one hidden tracked caller;
- deletion of a live fixture mistaken for historical data;
- loss of a sole-home ruling;
- deletion of the only provenance for a permanent semantic behavior;
- stale command/workflow path left behind;
- removal of a legacy path before its successor handles all callers;
- `.gitignore` change that accidentally tracks runtime output;
- `.gitignore` change that hides a tracked control/baseline;
- package import or Gate/test success that depends on a local ignored file;
- deletion that changes Gate-2/verification semantics rather than merely topology.

## Required deliverables

1. **Path-level deletion-readiness matrix** for all S15 candidates.
2. **Dependency evidence report** with exact search methods.
3. **Successor map** for migrated/replaced paths.
4. **Truth-home / provenance matrix** for evidence-bearing candidates.
5. **Quarantine reconciliation table** against `REMOVAL-LEDGER.md`.
6. **Generated/runtime-state inventory** and final ownership target.
7. **S15 conservation/negative-control test design**.
8. **Blocker list** that must be zero or explicitly decided before deletion.
9. **Draft S15 Worker contract**, marked DRAFT / NOT AUTHORIZED and explicitly requiring revalidation at the actual pre-S15 accepted head.

## Non-goals

This preflight must not:

- delete or move candidate files;
- alter `.gitignore`;
- repair legacy callers;
- perform S10–S14 work early;
- change ruling semantics;
- update ratchets/baselines;
- merge cleanup into the accepted branch;
- decide that historical evidence is valueless merely because runtime code no longer imports it.

## STOP conditions

STOP rather than downgrade evidence if:

- a candidate has an unexplained consumer;
- a document retains sole-home or unique provenance not preserved elsewhere;
- the difference between generated state and source/authority is unclear;
- a proposed deletion requires changing a guard’s semantic meaning;
- S10–S14 are incomplete in a way that makes final ownership unknowable;
- the cleanup ledger and accepted branch have diverged so much that path identity cannot be reconciled mechanically.

## Completion bar

Objective 4 is complete when the future S15 session can start with every candidate path classified, every live dependency and truth-home traced, every cleanup-branch quarantine reconciled, and a conservation suite designed to prove that removing legacy plumbing does not remove Foundry truth.
