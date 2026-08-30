# INCIDENT — LOCALITY REVERSION, 2026-08-14

**Gate 2 is RED on one row (`locality`). The repair is one command and its
success is verifiable against a git-tracked sha. Nothing is lost.**

---

## Current state

| | |
|---|---|
| `experiments/out/foundry/codebook.json` | 4,425,891 bytes · `b4197e94…` |
| byte-identical to | `backups/codebook.v0.7.pre-locality-backfill.20260814-015858.json` (`cmp` exit 0, the only matching backup) |
| axes / assertions | 615 total, **403 active** · **7,930** on active axes |
| human / rule-derived | **4,233 / 3,697** — matches the ratified counts exactly |
| **locality addresses** | **0** (was 7,808) |
| Gate 2 | **RED**, 16 rows: 14 pass, `family_sweep` known-excused, **1 unexpected — `locality`** |

**No human assertion was lost.** The only deficit is the locality layer.

## What happened

Two events on one inode (birth 14:58:40, mtime 15:00:54 — an unlink-and-create,
then an overwrite-in-place):

1. **14:58:40 — destroyed.** A C6 Tranche-1 rigging run disabled the
   restore-staging guard (rig **R8**), and **NC20 — the control for that guard —
   passed the real operational codebook path** to
   `foundry_authority.get_verified`, which `unlink()`s its destination before
   fetching. The file became 27 bytes of selftest fixture.
2. **15:00:54 — restored** the pre-locality backup by `cp`.

Both were my actions during the C6 Tranche 1 session.

**Root lesson: a negative control must be safe when the guard it tests is
absent — that is the only condition it is ever run under.** Aiming it at the
real artifact turned the test into the accident it was written to prevent.

## The repair

**Re-run the locality backfill. Nothing else** — no backup restore, no hand
edit, no `--update-baseline`.

```
python3 experiments/foundry_locality_backfill.py --dry-run
python3 experiments/foundry_locality_backfill.py --execute --go-sha256 8cdbfa346cd729948bfc0d9cd50641f7dca7768f1ef7299443cfe577330c1835
```

Verified reproducible before any write: the stored plan is **bit-identical** to
the re-derived plan (7,808 rows, `corpus_ref` 2026-07-04), and applying it to
the current file on a temp copy yields **exactly** the ratified state —

```
5,066,147 bytes   sha256 6aa6193f8a457ae4c7884e364f519749a9d68b96f7ecedf3fa903bfa4677426c
```

Stripping locality back off reproduces the current file byte-for-byte, so the
current file is provably that codebook minus its addresses.

Expect afterwards: 7,808 addresses restored, `locality` green, Gate 2 back to
**16 / 15 pass / 1 known-excused / 0 unexpected**.

## Two corrections to the first incident report

1. **There was never a "2,411-byte unexplained gap."** I compared the dry-run's
   **character** count (5,063,736) against an on-disk **byte** count
   (5,066,147). The delta is the UTF-8 overhead of 1,516 non-ASCII characters —
   the curly apostrophes in oracle quotes. *A count is not a measurement*, and I
   made that error while auditing for it. The ratified state is fully
   reproducible.
2. **The state was never unreproducible**, and the codebook was never at risk of
   permanent loss.

## What the audit cleared

- **No writer drops `locality`.** Round-trips through `json.load → _serialize`,
  `load_codebook()`, `_reorder_member` over every member, and both
  `merge_assertion` paths all preserve all 7,808 addresses byte-identically.
  `locality` is appended **last** in `ASSERTION_KEY_ORDER` as an optional key
  precisely so pre-existing assertions re-serialize unchanged.
- **Consolidation is SAFE** — zero `locality` references, append-only via
  `merge_assertion`, installs through the pass-through serializer.
- **A schema-destructive rewrite (hypothesis B) is excluded**: `os.replace`
  would have produced a new inode with birth == mtime; the observed file has an
  earlier birth on one inode, which is a `cp` overwrite. No post-`015858` backup
  exists, and every mutation path takes one first.

## C6 Tranche 1 — where it stands

`experiments/foundry_authority.py` is **untracked and uncommitted**. It is
complete: manifest schema + validator, deterministic serializer, exact-byte
verifier, narrow rclone transport, status states A–E, **26/26 offline
selftests**, **10 rigs all proven red**. Live-proven against R2: atomic
create-only publication via `If-None-Match: *` (rejected with **412
PreconditionFailed**, occupant unchanged).

**The NC20 defect is fixed** — the control now rebinds the operational path to a
disposable decoy with a canary, and a full rigging run leaves the codebook
byte-identical.

Nothing was committed. No production manifest exists; no codebook bytes were
ever uploaded.

## Do first, next session

1. Run the repair above and confirm the sha matches `6aa6193f…`.
2. Confirm Gate 2 returns to 16 / 15 / 1 / 0.
3. Then resume C6 Tranche 1 review (`docs/P3-CODEBOOK-DURABILITY-PACKET-2026-08-14.md`).
