# Member-add mutation boundary

Status: **RATIFIED — canonical law extraction.**

This file isolates one already-ratified invariant from the completed historical `/1 -> /2` migration directive. It changes no codebook semantics, no command behavior, no authority selection, and grants no new mutation authority.

## Canonical law

**Member-add CLI (AG-CLI-01): validates schema/target status/UUID/evidence, backs up, MERGES an assertion (never overwrites), appends history, lints, writes atomically, prints final sha256, halts on DET-axis operations other than assertion-merge of non-DET classes.**

The identifier and law text above are preserved from the Captain-ratified migration directive. “MERGES” and “never overwrites” are load-bearing. The DET boundary is also load-bearing: this law does not authorize hand-writing rule-derived membership on a DET-owned axis.

## Current embodiment and provenance

The historical source body is preserved byte-for-byte at `archive/routing/docs/B-MIGRATION-DIRECTIVE.md`, original Git blob `213206b6560d9f097ae86af1673b4630a1c1a64a`.

The current legacy command embodiment remains `experiments/foundry_codebook.py add-member`. Its semantic merge primitive has a permanent home in `mtj_foundry.codebook`, and its atomic local persistence primitive has a permanent home in `mtj_foundry.codebook_store`. This extraction does not move or widen the command boundary.

The installed read-only Foundry command remains read-only. This ruling is not permission to add a new installed mutating command.

## Conservation rule

Future plumbing may relocate the CLI, backup policy, persistence boundary, or presentation of its result, but the observable contract above must survive unchanged unless the Captain explicitly reratifies it.
