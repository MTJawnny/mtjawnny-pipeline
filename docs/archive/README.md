# docs/archive — parked, not dead

Nothing here is current law. Nothing here is deleted either — this is a
**retrieval index**, written on the assumption that the tool-building phase
after T3 will want several of these back.

The T3 arc is the priority; this material was a distraction from it. When
T3 lands and tool work starts (`BACKEND-BUILD-PLAN.md` phases 3.1–3.11, and
`T3-BUILDOUT-PLAYBOOK.md` steps 6–9), come here first — the "bring back for"
column says which ones will matter.

## Entry gate

A document may only land here when **all four** hold:

1. `python3 experiments/foundry_ruling_registry.py --check <doc>` reports it
   is the sole home of no ruling;
2. it is not cited as live law by `CLAUDE.md`, `.claude/` skills, or loaded
   by code;
3. no pending work item depends on it;
4. any live-law *section* inside it has been extracted verbatim to a
   document that stays in `docs/`.

Archived docs drop out of the registry scan (it globs `docs/*.md`, not
subdirectories), so condition 1 must be checked **before** the move.

## Index

| document | lines | why parked | bring back for |
|---|---:|---|---|
| `B-MIGRATION-AUDIT-PACKET.md` | 1359 | audit packet, consumed; verdict lives in the CDR register | re-auditing the `/2` schema if provenance changes again |
| `CORPUS-PASS-WALK-RATIFICATION.md` | 469 | self-declares HISTORICAL; outcomes in `WALK-RATIFICATION-EXECUTION-HANDOFF.md` | **the next naming walk** — holds the per-axis proposal method |
| `B-SESSION-SPLIT-REVIEW-PACKET.md` | 446 | consumed review packet | — |
| `B-MIGRATION-SESSION-1-REPORT.md` | 275 | consumed report | — |
| `TRIAGE-BATCH-4.md` | 672 | §10 extracted to `docs/RATIFIED-DIRECTIVES-BATCH-4-6.md`; remainder is working record | Captain's reasoning behind D1–D7 |
| `TRIAGE-BATCH-6.md` | 1008 | §10 extracted (same file); remainder is working record | Captain's reasoning behind D1–D8 |
| `BATCH-8-AB-DRESS-REHEARSAL-SPEC.md` | 133 | batch 8 executed | designing any future A/B cost experiment |
| `CONSOLIDATION-RUN1-DIRECTIVE-2.md` | 127 | superseded | — |
| `CONSOLIDATION-PLAN-DIRECTIVE.md` | 121 | executed | — |
| `T3-BUILDOUT-STEP3-HANDOFF.md` | 72 | superseded by `T3-BUILDOUT-STEP4-HANDOFF.md` | — |
| `B-MIGRATION-DISCOVERY-DIRECTIVE.md` | 201 | executed directive | — |
| `CONSOLIDATION-APPLY-DIRECTIVE.md` | 66 | executed directive | — |
| `RESUME-NOTE.md` | 176 | self-declared COMPLETE 2026-08-01 | **a corroboration run (M=2)** — holds run 1's submission mechanics and the two remediation fixes |
| `OUTPUT-TRIM-PROPOSAL.md` | 200 | REJECTED 2026-08-01 | revisiting output cost if a second corpus pass is priced |

**14 documents, 5,325 lines.**

## Restoring one

```bash
git mv docs/archive/<NAME>.md docs/<NAME>.md
python3 experiments/foundry_ruling_registry.py     # re-scan
```

Then repoint any `docs/archive/<NAME>.md` references back to `docs/<NAME>.md`.
