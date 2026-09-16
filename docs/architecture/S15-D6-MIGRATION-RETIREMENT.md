# Codebook schema support policy — `/1` migration retired

**Status:** current support policy.
**Authority:** Captain decision `D-20260915-S15-D6-RETIRE-V1-MIGRATION-SUPPORT`,
GitHub Issue #1 comment
[5693041826](https://github.com/MTJawnny/mtjawnny-pipeline/issues/1#issuecomment-5693041826).

This document says what is supported **now**. It is not a task tracker, not a
phase mirror, and it rewrites no earlier ruling: the historical documents keep
saying exactly what they always said, and what they describe genuinely happened.
What changed is which of it is still a live obligation.

## The supported reader

`experiments/foundry_codebook.load_codebook` and the permanent
`mtj_foundry.codebook_store.read` accept schema `foundry-codebook/2` **only**. A
`foundry-codebook/1` document is rejected loudly: the permanent store raises a
typed `SchemaMismatchError` carrying `path`, `actual` and `expected`, and the
legacy facade turns that into the operator's `STOP — …` line and exit 1.

That rejection is unchanged by this policy. Only the **advice** changed.

## Routine `/1 -> /2` conversion is RETIRED

There is no supported current command that converts a `foundry-codebook/1`
document to `foundry-codebook/2`, and no successor engine was written to replace
one. The two scripts that performed and checked the original one-shot migration —
"foundry_migrate_codebook_v2.py" and "foundry_verify_migration.py" — are retained
as historical evidence under `archive/research/mutations/`, and nothing under
`archive/` is a live path. They are inert: read them, do not run them.

Reconstructing a `/1` document is **separately scoped historical work**. It is
not a step in operational recovery, and it is not blocked by this policy — it is
simply not something the current runtime does for you.

## Supported recovery

Recovering a working operational codebook does not require, and never routes
through, either archived script. The supported path is the verified authority
architecture:

| step | owner |
|---|---|
| immutable remote object, content-addressed by SHA-256 | `mtj_foundry.authority_transport` |
| fetch to STAGING, then exact sha + size verification | `mtj_foundry.authority_restore` |
| codebook validation of the staged payload | `mtj_foundry.authority_restore` + `mtj_foundry.codebook` |
| pre-install backup, then atomic install | `mtj_foundry.authority_restore` |
| operator surface | `mtj_foundry.authority_cli` (`status`, `verify`, `verify-remote`, `restore`) |

The selected authority is named by `config/selectors/codebook-authority.json`,
which pins the snapshot id, object path, SHA-256 and byte size.

**The order is the safety property**: remote → staging → verify → validate →
install, never remote → operational → verify afterward. `authority_restore`
records each step in a trace and asserts it, because an ordering that is only
documented is an ordering nobody checks. Replacing an existing codebook requires
a pre-install backup; without one, replacement is refused rather than performed
unbacked.

This document deliberately prints **no ready-to-paste restore command**, and the
`/1` halt does not emit one either. Restoring authority overwrites the
operational codebook: it is an operator decision made with the selector in hand,
not an autocomplete handed out by a failed read.

## What is preserved

- **The `/1` backups.** They are untouched. Nothing in this policy deletes,
  moves, rewrites or reclassifies them, and `backup_codebook`'s readback-verified
  backups remain the rollback path they always were.
- **The migration evidence.** The original manifest and verification report keep
  their recorded identities in
  `refoundation/conservation/OUTPUT-EXCEPTION-CENSUS.yaml`, and the archived pair
  keeps the gate constants the migration was accepted against.
- **The historical record.** `docs/B-MIGRATION-DISCOVERY.md` and its siblings
  remain the durable home of the migration's rulings and derivation. The rulings
  registry still reports that document as sole home of twelve rulings and
  therefore undeletable.

## What is still required

Retiring a migration route retires **no safety obligation**.

- **A13 interruption behaviour is unchanged and still live.** An interrupted
  `os.replace` must raise a **raw** `OSError`, leave the live file
  byte-identical, and leave an inert `.tmp` behind. `os.replace`, `os.fsync` and
  `json.load` stay late-bound through their modules so that control can be armed.
  Its live home is `tests/refoundation/test_codebook_store.py`
  (`TestTheProtocolRefusesBeforeInstalling.test_an_interrupted_rename_raises_a_RAW_OSError`
  for the permanent protocol, and
  `TestTheLegacyWriterBoundary.test_an_interrupted_rename_still_escapes_the_facade_RAW`
  for the facade). Both are behavioural, and both fail when the protected
  behaviour is broken.
- **Independent verification still applies to applicable mutations.** A
  successful serialization, lint or digest check is not proof of semantic
  correctness, and atomic-write tests do not substitute for independent
  source-grounded verification. Historical implementation identity was never the
  obligation; the obligation is that something independent of the writer checks
  the writer's claim.
- **C8.5P.V correction C3 still holds.** The permanent library carries no
  repository-relative guidance; the legacy facade owns the operator sentence.
  This policy changed what that sentence says, not where it lives.
