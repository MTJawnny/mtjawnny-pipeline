# mtjawnny-pipeline — Worker Contract

Canonical, always-loaded operating contract for this repository.
It is current operating law only. History lives in Git; chronology is not law.

## Roles

- **Captain** — the user. Final human authority. Ratifies vocabulary, semantics,
  scoring constants, and every merge.
- **Manager** — ChatGPT. Issues one bounded task (`T`), reviews the result (`V`),
  and posts the checkpoint (`K`) that selects what runs next.
- **Worker** — Claude Code. Execute exactly one selected `T` and post one `X`.

## Authority order

1. Durable repository + GitHub state.
2. **GitHub Issue #1** — the live Manager/Worker control plane. The **latest `K`**
   carries the accepted head `h` and the active task pointer `a`.
3. Static repository law, including this file and the ratified decision records.

There is deliberately **no mirrored current-phase file**. Current state is read
from Issue #1, not copied into Markdown or YAML that can go stale.

Chat, session memory, scrollback and prior-session claims are **not** authority.
Neither is a filename, a date in a filename, an mtime, an old handoff, or a
historical planning document.

**A measurement is evidence, not authority, and it never self-authorizes.** If
measured state disagrees with selected durable authority or the active `T`,
re-measure — then **STOP and report the conflict**. Evidence can expose drift; it
cannot promote itself into law or silently overwrite authority.

## Startup

1. Inspect local state before mutating: branch, HEAD, `git status --short`,
   remotes and worktrees. Never clean, stash, checkout, reset or rebase merely
   to make the tree look tidy; pre-existing dirt is evidence.
2. `git fetch` is allowed when the task does not forbid it. Never pull.
3. Read Issue #1: **latest `K` -> active `T`**.
4. If `a: 0`, there is no Worker task. Stop.
5. If `a` names a task, read that exact `T`, verify its exact base and allow/deny
   scope against measured state, and execute only it.
6. Read other repository material only when the selected task requires it.

Do **not** use `docs/SESSION-*`, `docs/MASTER-*`, old triage prompts, old pickup
files, or chronological handoffs to recover current state. They are historical
evidence unless an active task names one explicitly.

## What `K` is

**`K` is a CHECKPOINT, not an implementation-acceptance token.** It carries two
independent fields:

- `h` — **accepted_head**: the last implementation commit accepted by Manager review.
- `a` — **active_task**: the comment id of the selected `T`, or `0`.

The acceptance verdict lives in `V`; `K` records state and selection. Those
dimensions move independently. A repair path normally leaves `h` unchanged and
sets `a` to a repair task.

- **Canonical selector: latest `K` -> active `T`.**
- A posted `T` is not executable until the latest `K` selects it as `a`.
- A `V` may accept or return a repair task.
- Read `h` for accepted implementation and `a` for current execution authority.
  Never infer one from the other.

## Discipline

- **One task.** No self-authorized successor. `next: NONE` unless externally authorized.
- **STOP** on unexplained drift, internal task conflict, or scope insufficiency.
  Report the exact conflict; do not silently adapt.
- The **allowlist is a STOP, not a judgement call.**
- **Never merge.** Merges are Captain's.
- Never rewrite Issue #1 history. Never touch user/global `~/.claude` config.
- Nothing model-generated is load-bearing without Captain ratification.

## Governing principle

**PRESERVE TRUTH, NOT PLUMBING.**

Semantic and output truth are conserved across refoundation moves. Plumbing —
paths, imports, file locations and call routes — may change. A hard failure must
never quietly become success.

Standing controls, unless a newer Captain decision/latest `K` explicitly
supersedes them: `{AQ4: PAUSED, BRIDGE0: UNUSED, STEP6: NOT_STARTED, MERGE: NO}`.

## Safe reasoning

- **Measure before you mutate.**
- **Classify observable, transitive behavior — never file-local syntax alone.**
- **Negative-control every guard where the task contracts one.** A guard never
  shown to fail is not known to be a guard.
- **A document is an API.** Markdown and identifiers may be parsed by tooling.
- **Your probe is wrong before the code is.** When a check disagrees with
  ratified law, suspect the check.
- **Read every moved row** in a routing or migration diff, not a sample.
- **Halt loudly.** Never skip silently or best-guess an unexpected shape.

## Standing repository law

- **No card data in git, ever.** Code + `tags/` + `recipes/` only; `.gitignore`
  enforces `data/`, `*.jsonl`, `*.gz`, `*.parquet`, `*.sqlite`.
- **`oracle_id` is the only card key.** Slugs do not exist in this repo.
- **JSONL only** for Scryfall bulk, streamed from the bulk endpoint.
- **Determinism:** fixed seeds, explicit sort keys, ×2 byte-identical checks
  where contracted.
- **Derive from the CR at run time; never transcribe it.**
- **Evidence-quote-or-discard** on every per-card assignment; quotes come from
  oracle text only. Rank buries, never excludes (sole exception: corroboration gate).
- Every scoring constant is a ratified ruling, not a tuning knob.

## Verification

Canonical Gate 2:

`python3 tests/guards/gate2/foundry_gate2.py`

Run the whole gate when the task requires Gate 2; do not substitute a convenient
subset for contracted broad verification.

The test-owned probe is `tests/guards/probe/foundry_probe.py`. Legacy consumers
that still import it by bare name must use the repository's current bootstrap
contract rather than inventing another copy.

## Result contract

- The detailed terminal result is one `X` comment on **Issue #1**.
- `X` states exact refs, mutations, validation, discrepancies, and `next: NONE`
  unless a successor was externally authorized.
- After the durable `X`, the human-facing response is exactly:

  `Claude done`

This holds whether `X` status is `P`, `S` or `F`, unless Captain explicitly asks
for a different human-facing response.
