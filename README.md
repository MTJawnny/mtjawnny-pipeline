# mtjawnny-pipeline

The MTJawnny repository contains two related systems:

1. the production data pipeline that builds card artifacts for mtjawnny.com; and
2. **Foundry**, the refounded semantic substrate behind the MTG Thesaurus and
   future MTJawnny tools.

Foundry is broader than one similarity page. Its permanent package is intended
to supply reusable MTG semantics, verified evidence and retrieval capabilities
to the Thesaurus, static website tools, future deck/card utilities and later
research layers without making each product reimplement the same rules.

## Current project state

**Do not read this README for the current task, accepted head, or migration
slice.** Those facts change too often to mirror safely in a tracked prose file.

Durable operational state is:

1. Git/repository objects;
2. GitHub Issue #1, especially the **latest `K`**;
3. the active `T` selected by that `K`, if `a` is nonzero.

The canonical selector is:

`latest K -> active T`

A `K` is a checkpoint. `h` is the accepted implementation head; `a` is the
active task pointer. The acceptance decision itself lives in Manager review
`V`.

For a fresh Manager, start at `refoundation/README.md`.
For a Claude Code Worker, root `CLAUDE.md` is the canonical always-loaded
contract.

## Repository map

```text
src/mtj_foundry/        permanent Foundry package
config/                 tracked machine-readable source/configuration
tests/                  standing tests, Gate 2 guards and fixtures
experiments/            legacy Foundry implementation still being decomposed
refoundation/           static governance, conservation and migration contracts
benchmarks/             frozen benchmark/evaluation material when present
pipeline/               production card-data build pipeline
tags/ + recipes/        production pipeline inputs
docs/                   semantic evidence/history; NOT current task routing
```

`mtj_foundry.paths.ProjectPaths` is the permanent repository-layout owner.
Production package code must remain layered and acyclic; production must not
import paused AQ4 benchmark code.

## Foundry layer direction

The permanent architecture is moving toward the following dependency direction:

```text
paths              L0
  ↓
infra              L1
  ↓
mtg                L2
  ↓
codebook           L3
  ↓
runtime            L3.5
  ↓
evidence           L4
  ↓
thesaurus          L5
  ↓
operators/products L6
```

Tests, benchmarks, configuration, generated state and historical evidence are
supporting surfaces, not additional semantic layers.

The MTG Thesaurus is one consumer of Foundry. Future consumers may include card
replacement, deck-completion, card-role exploration, Commander tools and other
static-site utilities.

## Installed Foundry commands

The package metadata currently exposes three operator surfaces.

### Read-only verified report

```bash
mtj-foundry-report \
  --root /path/to/mtjawnny-pipeline \
  --input-lock /path/to/mtjawnny-pipeline/refoundation/path-e/input-lock.json
```

This verifies the selected codebook and the explicitly pinned corpus, loads them
through permanent capabilities and prints a deterministic report to stdout. It
does not infer, rank, assign or write.

### Evidence index / retrieval / evaluation

```bash
mtj-foundry-evidence index \
  --root /path/to/mtjawnny-pipeline \
  --input-lock /path/to/mtjawnny-pipeline/refoundation/path-e/input-lock.json \
  > index.json

mtj-foundry-evidence query \
  --index index.json \
  --name "Reanimate" \
  --top 25

mtj-foundry-evidence evaluate \
  --index index.json \
  --panel /path/to/mtjawnny-pipeline/refoundation/path-e/m2-evaluation.json \
  --source-document /path/to/mtjawnny-pipeline/docs/WIRE-PREDICTIONS-2026-08-09.md
```

The index is full-population: Gate-0 eligibility is a field, never a row filter.
Only active codebook evidence contributes memberships. An unassigned card means
only that the selected codebook records no active membership for it; it is not
negative evidence and must never be interpreted as “dissimilar.”

`query` and `evaluate` operate from the emitted index artifact rather than
needing to rediscover repository state.

### Static diagnostic bundle

```bash
mtj-foundry-pilot \
  --index index.json \
  --evaluation evaluation.json \
  --output /tmp/pilot-bundle \
  --verify
```

The builder consumes emitted artifacts and package-owned static assets and
writes only below the declared output directory. Python precomputes retrieval;
browser JavaScript renders the emitted result and does not own a second ranking
algorithm.

The resulting bundle is diagnostic, not publication authorization.

## Accepted pilot finding

The frozen Path-E evaluation is historical **measurement evidence**, not a
current-state pointer and not a product-quality claim. Its important finding was
that evidence coverage, not UI code, was the limiting factor:

- 12 of 28 named-correct panel cards were discoverable from recorded evidence;
- 3 of those 12 appeared in the top 10;
- 7 of 12 appeared in the top 25;
- all 12 discoverable examples were inside non-singleton tie blocks.

That measurement is intentionally not “fixed” in documentation. Foundry must
first improve the semantic/evidence substrate; absence of recorded evidence
must never be converted into a negative similarity signal.

## Verification

Canonical Gate 2 is:

```bash
python3 tests/guards/gate2/foundry_gate2.py
```

Gate 2 is a single procedure with one final exit status. Broad verification
must not be replaced by a narrow subset when a task contracts the full gate.

The refoundation suite lives under `tests/refoundation/`.

## Documentation policy

`docs/` contains semantic rulings, evidence, old handoffs, audits and historical
work products. It is **not a startup directory**.

A model must not recover current project state from:

- dated `SESSION-*` documents;
- `MASTER-*` handoffs;
- `PICK-UP-*` files;
- old triage instructions;
- filename order or modification time.

Read a historical document only when a current task, current decision record or
specific investigation requires it.

Deletion from top-level `docs/` is additionally guarded by the generated
ratified-rulings registry. A file that looks obsolete may still be the sole home
of a ruling, so historical cleanup is a conservation operation rather than a
bulk `rm`.

## Card data and pipeline

No card corpus is committed to Git.

The production pipeline fetches Scryfall bulk data, merges MTJawnny inputs and
builds versioned artifacts for R2/CDN publication. Generated card data belongs
outside source control.

Pipeline dependencies remain in `requirements.txt`; the permanent
`mtj_foundry` package intentionally has its own stdlib-only dependency contract.

## Governance

The standing principle is:

> **PRESERVE TRUTH, NOT PLUMBING.**

Paths, filenames, imports and compatibility layers may change when authorized.
Semantic truth, authority identity, failure boundaries, frozen commitments and
accepted output behavior may not change silently.

Static Captain direction: `refoundation/CAPTAIN-DIRECTION.md`.
Session protocol: `refoundation/SESSION-PROTOCOL.md`.
Current task/state: GitHub Issue #1, latest `K`.
