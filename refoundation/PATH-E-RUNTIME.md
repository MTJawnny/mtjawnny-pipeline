# The read-only Foundry runtime — operator page

One installed command, `mtj-foundry-report`. It verifies the selected codebook
and an explicitly pinned corpus, loads both through the permanent capabilities,
and prints one deterministic JSON report. It infers nothing, ranks nothing,
assigns nothing and writes nothing.

**Task authority is not here.** It is GitHub Issue #1: latest `K` -> active `T`.
Current phase state is `refoundation/ACTIVE-PHASE.yaml`. This page describes how
to run the thing and what its numbers mean, and nothing else.

## Install

```
python3 -m venv /some/env
/some/env/bin/pip install /path/to/mtjawnny-pipeline
```

`pyproject.toml` declares `setuptools>=68` as its build requirement, and that
dependency has to be obtainable — from an index or from an environment that
already has it. There is no offline path on a machine whose interpreter ships no
setuptools; `refoundation/PACKAGE-EXECUTION-CONTRACT.yaml` records that
measurement and keeps real-install evidence separate from the committed offline
guard.

An install produces `build/`, `dist/` and `*.egg-info/` if run in the repository.
All three are gitignored. They are generated artifacts, never source, never an
input to a decision.

## Run

```
/some/env/bin/mtj-foundry-report \
    --root /path/to/mtjawnny-pipeline \
    --input-lock /path/to/mtjawnny-pipeline/refoundation/path-e/input-lock.json
```

Runs from any working directory, with `PYTHONPATH` unset and no repository on the
path. `--root` is required and explicit on purpose: the command never derives the
repository from the working directory.

The report goes to **stdout**; a failure goes to **stderr** and exits non-zero
with nothing on stdout, so a redirected report file can never hold a
success-shaped document for a run that failed. Redirect stdout wherever you like
— that is an operator choice, not a side effect of the command.

Overrides, all optional: `--codebook`, `--authority`, `--corpus`,
`--corpus-sha256`, `--corpus-content-sha256`, `--corpus-provenance`. A value
supplied both by the input lock and on the command line must AGREE; a
disagreement is refused rather than resolved by precedence.

## Which inputs, and which of them are ratified

**The codebook is SELECTED and the selection is ratified.**
`docs/codebook-authority.json` is tracked and names the snapshot: sha256
`6aa6193f…7426c`, 5,066,147 bytes. The runtime measures the local file's actual
bytes and refuses unless BOTH match. That is a LOCAL verification; the report
says so, and says explicitly that remote durability was not verified.

**The corpus is PINNED BY PROPOSAL and is NOT ratified.** No durable authority
pins a raw-corpus digest. `refoundation/path-e/input-lock.json` records what was
measured and how its provenance was checked, marked
`status: PROPOSED_PILOT_INPUT_LOCK`, `ratified: false`. The runtime carries that
status into the report unchanged; nothing in the code can promote it. Ratifying,
correcting or rejecting that lock is a Manager/Captain decision.

The provenance that WAS established: the local corpus decompresses to bytes
identical to the archived snapshot object
`r2:mtjawnny/data/snapshots/2026-07-03/oracle-cards.jsonl.gz`. The two containers
are the same length and differ at exactly three byte offsets — 4, 5 and 6, the
gzip header MTIME field. That is why the lock carries two digests: the container
sha256 pins this exact artifact, and the content sha256 is what survives
recompression and matches the archive.

## Runtime dependency closure

Standard library only, plus `mtj_foundry` itself. The command imports no
`experiments`, `pipeline`, `foundry_*`, `tier_engine` or AQ4 module, performs no
`sys.path` bootstrap, and opens no network connection. A committed test asserts
this over the live `sys.modules` graph, not only over the source text.

## What the report's numbers mean

Every count is a count of EXISTING STRUCTURE. None is a quality measurement.

- **Full population** is every unique `oracle_id` in the corpus. **Eligibility**
  (Gate #0, batch-6 D1: legal or restricted in at least one Scryfall format)
  PARTITIONS that population and removes nothing from it. Eligible + ineligible
  always equals the full population, and both are reported.
- **Coverage**: a corpus id is *covered* iff at least one axis with status
  `active` lists it as a member. **This is a statement about the codebook, not
  about the card.** An uncovered id means no active membership is recorded — it
  is not evidence that the card is unlike any other, and it must never be read
  as one.
- **Memberships are not cards.** `memberships_active_axes` counts (axis, card)
  pairs; `corpus_ids_covered` counts distinct cards. A card on three axes is one
  covered card and three memberships.
- **Member ids absent from the corpus** are counted separately, with their
  membership count, rather than being dropped into a ratio.
- Face counts come from the corpus capability, so split, flip and adventure
  layouts — which carry `card_faces` AND one root-level text — read correctly.
- Duplicate `oracle_id` records collapse last-write-wins, which is the loader's
  accepted semantics; the report names the rule rather than leaving it implied.

The report is **derived evidence, never authority**. It selects nothing and
ratifies nothing, and it says so in its own payload.

## Determinism

Two runs over the same inputs produce byte-identical output. Nothing
time-dependent, machine-dependent or cwd-dependent enters the payload: paths are
repository-relative to the declared root, and the root itself is deliberately not
in the report so two checkouts remain comparable.

## Deferred — not started, not promised here

The per-card evidence index, any retrieval or ranking policy, Searcher-B scoring,
the viewer and any static publication are **milestone 2 and 3** and require new
Manager authorization. Legacy consumer migration is frozen; C8.5X is a frozen
temporary migration aid and is not the product architecture. AQ4 is PAUSED,
Bridge v0 PARKED_UNUSED, Step6 NOT_STARTED, Merge NO.
