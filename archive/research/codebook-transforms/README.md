# `archive/research/codebook-transforms` — retired codebook-CONTENT transforms

**This owner is CLOSED at exactly seven files.** They are inert historical
evidence. There is no promise that they run, and running them is not a recovery
procedure. An archived file is retained BECAUSE it is historical; nothing under
`archive/` is a live path.

Authority: Captain decision `D-20260916-S15-D5-R2-CODEBOOK-TRANSFORMS-EXECUTION`,
as corrected by `D-20260916-S15-D5-R3-LAYOUT-PIN-ALLOWLIST-CORRECTION`, GitHub
Issue #1. Archived byte-for-byte from `experiments/` at base commit `f429776fb5fa461b9d44425bf40e858d4527a17b`.
The Git blob id is unchanged by the move, which is the machine-checkable
statement that the bytes were not edited.

## What this owner is, and what it is not

These seven are completed one-shot transformations of codebook **CONTENT** —
members, slugs, and axis or assertion fields. Each artifact's authorized effect
is already embodied in the selected codebook, and its authorization lives in a
tracked ruling. They are retained as **provenance only**: none is a supported
operator, and archived execution is not authorized.

Three neighbouring owners exist and are deliberately separate:

| owner | holds | boundary |
|---|---|---|
| `archive/research/mutations` | the closed `foundry-codebook/1 -> foundry-codebook/2` **schema** migration pair | those two files do **not** belong in this directory |
| `archive/research/triage` | the thirteen batch decision adapters and assemblers | triage evidence belongs to its own owner |
| `archive/research/batch8` | the Batch-8 comparative research scripts | Batch-8 evidence belongs to its own owner |

## The closed population

| archived file | source path | git blob | SHA-256 | bytes | mode |
|---|---|---|---|---:|---|
| `foundry_any_damage_split.py` | `experiments/foundry_any_damage_split.py` | `7d518c7e1147e70d63d91dead813f830b916c0b7` | `03862b8e0b5a282bf93ec31709aae0e75586be8095ab807d190b55437392f69a` | 6,505 | `100644` |
| `foundry_cdr09_derive.py` | `experiments/foundry_cdr09_derive.py` | `bfca628df5e5a5fe99e2300639c4d050fe3c3562` | `f958d12f469d4b138fc68d656338e09b6597f8fdc781720e67b28b84908f1882` | 11,861 | `100644` |
| `foundry_cdr09_walk.py` | `experiments/foundry_cdr09_walk.py` | `5b5ceca6e143c4c5c102f8059e7a9cf5e11e56f5` | `903466dffb0544f2693ebac9802e5c34825a3b72ba3635eb2fa8a1abd7c7cb96` | 8,796 | `100644` |
| `foundry_axis_merge_pointer_correction.py` | `experiments/foundry_axis_merge_pointer_correction.py` | `19821de01af6efb1ea1889344097540800d1c401` | `6577b768ebd03b01866e46bd8e7710ddf73bf62805ceab402857716120b6bf5c` | 4,757 | `100644` |
| `foundry_batch7_pay_life_scrub.py` | `experiments/foundry_batch7_pay_life_scrub.py` | `221950912811b84e8047e6b9594979405b9e035b` | `a41f9832eb6e4005788b688002abfe2e0e48aae444e95adc4cb61c89e7b6317b` | 6,311 | `100644` |
| `foundry_gate0_scrub.py` | `experiments/foundry_gate0_scrub.py` | `35e895565cd539f3b8f468922f512baf6e575e37` | `2df02d3fd28f40ff88b619b7f4ae1dc2703c2d5022a856978ee488780a7d02b9` | 3,077 | `100644` |
| `foundry_locality_backfill.py` | `experiments/foundry_locality_backfill.py` | `2110f7ad36d9845ab01629ce367c6e4860245cac` | `a5e5edc370ed21d741d48109372f93a59b065f843cc4e5ebf1cb5219e598cbc0` | 25,934 | `100644` |

## Provenance, per artifact

| archived file | kind | ratifying decision / record |
|---|---|---|
| `foundry_any_damage_split.py` | EXECUTOR -- moved members between axes, carrying their assertions verbatim. | Captain-ratified 2026-08-02 any-damage / combat-damage delivery split; recorded in `docs/DAMAGE-DELIVERY-RULING-2026-08-02.md`. |
| `foundry_cdr09_derive.py` | DERIVATION -- writes nothing; re-derived the rename worklist from live state. | CDR-09 s12a counter-homograph rename derivation against grammar s8a; recorded in `docs/CDR-09-WALK-DERIVATION-2026-08-02.md` and `docs/CODEBOOK-NAMING-GRAMMAR.md`. |
| `foundry_cdr09_walk.py` | EXECUTOR -- name-only; old slugs became `renamed` tombstones. | CDR-09 s12a rename walk, Captain-ratified 2026-08-02; same records as its derivation. |
| `foundry_axis_merge_pointer_correction.py` | CORRECTION -- cleared one stale `merged_into` pointer; idempotent. | Captain ruling 2026-08-01 un-merging `rule:etb-with-negative-counters`; recorded in `docs/archive/B-MIGRATION-SESSION-1-REPORT.md`. |
| `foundry_batch7_pay_life_scrub.py` | CORRECTION -- one-off post-emit scrub, explicitly never to be re-run. | Batch-7 D4 GRAMMAR-SS9 quote-pull, Captain-approved 2026-07-30; recorded in `docs/PARENT-TREE-CANDIDATES.md` and `docs/B-MIGRATION-DISCOVERY.md`. |
| `foundry_gate0_scrub.py` | SCRUB -- the reusable capability now lives in `src/mtj_foundry/codebook_membership.py`. | Batch-6 D1 retroactive Gate #0 legality scrub, ratified 2026-07-30; recorded in `docs/RATIFIED-DIRECTIVES-BATCH-4-6.md`. |
| `foundry_locality_backfill.py` | MIGRATION -- one-shot assertion-field backfill under a byte-identity conservation invariant. | Semantic locality backfill, step 4 of the locality roadmap resolving FL-2; the resulting snapshot is named in `config/selectors/codebook-authority.json` (`codebook-20260814-locality-backfill`). |

## The CDR-09 evidence pair

`foundry_cdr09_derive.py` and `foundry_cdr09_walk.py` are **one evidence pair**
and were moved atomically. The walk imports the derivation and uses its sense
table at nine sites, so the walk cannot be read — let alone interpreted —
without it. Archiving them apart would retain the record of a rename without the
derivation that decided it, and would additionally leave the archived walk able
to bind to a still-live sibling whenever an external bootstrap supplied
`experiments/` on the path.

## Why they cannot simply be run

Six derive their root as `Path(__file__).resolve().parent` and bootstrap
`sys.path` with it; `foundry_axis_merge_pointer_correction.py` uses `parents[1]`
and then `REPO_ROOT / "experiments"`. From this directory neither shape reaches
the live `experiments/` tree, so the `foundry_common` import fails. **This was
not edited to make the point** — no import, root derivation, constant or
algorithm was touched, because doing so would have destroyed the byte identity
that makes them evidence. That is inertness under the default bootstrap, not a
boundary against a supplied `PYTHONPATH`.

## Discoverability

`experiments/foundry_prior_art.py` registers this directory as an explicit
historical family, labelled `archived codebook-transforms set`. Registration
happened in the same commit as the move, so the strict prior-art refusal never
lapsed. Discovery reads these files as TEXT only — it never imports, compiles,
executes or subprocess-launches them.
