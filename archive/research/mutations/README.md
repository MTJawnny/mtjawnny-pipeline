# `archive/research/mutations` — the `/1 -> /2` codebook migration, as evidence

**These files are inert historical evidence. There is no promise that they run,
and running them is not a recovery procedure.** An archived file is retained
because it is historical; nothing under `archive/` is a live path.

Current support policy: [`docs/architecture/S15-D6-MIGRATION-RETIREMENT.md`](../../../docs/architecture/S15-D6-MIGRATION-RETIREMENT.md).
Authority: Captain decision `D-20260915-S15-D6-RETIRE-V1-MIGRATION-SUPPORT`,
GitHub Issue #1 comment
[5693041826](https://github.com/MTJawnny/mtjawnny-pipeline/issues/1#issuecomment-5693041826).

## What was archived

Both files moved byte-for-byte from `experiments/`, at base commit
`6a52098e1e809a330f5469f759e5272f62e757ad`. The Git blob id is unchanged by the
move, which is the machine-checkable statement that the bytes were not edited.

| archived file | source path | git blob | SHA-256 | bytes |
|---|---|---|---|---|
| `foundry_migrate_codebook_v2.py` | `experiments/foundry_migrate_codebook_v2.py` | `f99d404dc7767299ef990b473169e8d251e65a36` | `34444cfe841c8f2fed9ba5b5d9c0ebc695390cc754dd1b24a712e3d45115c631` | 23,043 |
| `foundry_verify_migration.py` | `experiments/foundry_verify_migration.py` | `df8ac0a41960c959b7ec6de8fef8e1fdb4291e92` | `d95c35d8a26fc8722589622cda9fbffb42fd41a61c8db0d0a2b9a1900d9dd64e` | 37,573 |

They are archived **together, and that is a rule, not a convenience.** They have
no import, call, subprocess or artifact dependency on each other in either
direction — the verifier's independence from the mutator is the whole point of
it. The co-move rule is about evidence: the verifier is the migration's only
proof, so archiving them apart would retain the record of a change without the
evidence that it was correct.

## Completed scope

A one-shot migration of the operational codebook from schema
`foundry-codebook/1` to `foundry-codebook/2`, over batches 1–7. It is complete;
it is not a general-purpose backup converter and never was.

The mutator gates the result against a fixed expected population — 455 records,
7,699 members, 4,002 human and 3,699 human-live assertions, 3,697 rule-derived,
295 human-shell, 8 pay-life, and per-status totals of 307 active / 75 killed /
45 renamed / 26 merged / 2 deferred. Those numbers describe **that** migration.
A different input does not make them true.

### The independent checker

`foundry_verify_migration.py` re-derives the migration's claims from the sources
rather than reading the mutator's answer back: it deliberately does **not** read
`migration_manifest.json`, and it distinguishes "lint refused it" from "the
process died" so two different failures cannot agree by accident. It also
carried the original `os.replace` interruption rig for A13.

That rig is now historical. **The live A13 interruption control does not depend
on these bytes** — it is behavioural and lives in
`tests/refoundation/test_codebook_store.py`. What remains asserted about the
files here is their recorded independence, checked by reading this source, never
by importing it.

## Why they cannot simply be run

Both derive their root as `Path(__file__).resolve().parents[1]` and then
bootstrap `sys.path` with `REPO_ROOT / "experiments"`. From this directory that
resolves to `archive/research/experiments`, which does not exist, so the
`foundry_common` import fails. **This was not edited to make the point** — no
import, root derivation, constant or algorithm was touched, because doing so
would have destroyed the byte identity that makes them evidence.

Reconstruction, if it is ever wanted, needs an isolated historical checkout at a
commit where these files sat in `experiments/`, that era's dependency set, and
matching historical inputs. It is separately scoped work and is deliberately not
set up here.

## Inputs and outputs

The source artifacts these scripts required, and the outputs they recorded, live
in gitignored runtime state (`experiments/out/foundry/`, `data/`) — no card data
is in Git, ever. **Availability on one machine is not durability.** The table
below is what was measured at archive time, not a guarantee.

| artifact | role | status at archive time |
|---|---|---|
| `migration_manifest.json` | mutator output | present, 2,130,789 B, SHA-256 `7004432b677f5a3c49db50158fa5d0e7b164db23ae56aa38e1954b3cb935a839` — matches the identity recorded in `refoundation/conservation/OUTPUT-EXCEPTION-CENSUS.yaml` |
| `migration_verification_report.json` | verifier output | present, 2,602 B, SHA-256 `2371c1f520baf2c139814b1c3c8010a4d8440357766bc593849cc194e9c59e20` — matches the recorded identity |
| `migration_negative_tests.json` | verifier negative-control output | present, 3,053 B, SHA-256 `cffd1b6e76546a6d9fb4957831bf935de02fea8604a04e9dd0581d8ededa8848` — **not** carried in the output census |
| `codebook.json` | mutation target | present, 5,066,147 B, SHA-256 `6aa6193f…` — the selected `/2` authority |
| `det_pass_full_hits.json` | input | present, 279,918 B |
| `config/semantic/det-patterns-v2.json` | input | present, 39,901 B (tracked) |
| `batch7_pay_life_scrub_report.json` | input | present, 1,554 B |
| `data/artifacts/latest.json` | corpus-ref input | present, 599 B |
| `decisions/`, `review/` | batch provenance inputs | present, 16 and 28 entries |

The two census-pinned outputs were re-hashed from their actual bytes for this
record: a hash written in a census is a claim about a payload, not the payload.

Retention of these historical artifacts is **not** settled by this archive move.
Nothing here authorizes disposing of them, and no claim is made that the
migration could be reproduced from them — reproduction would additionally need
the historical code environment described above.

## Related record

- `docs/B-MIGRATION-DISCOVERY.md` — the migration's derivation and the durable
  home of its rulings. The rulings registry reports it as sole home of twelve,
  so it is undeletable.
- `archive/routing/docs/B-MIGRATION-DIRECTIVE.md` — what was authorized.
