# archive/site-forks — diverged copies recovered from the site repo

Historical artifacts only. **Never cite these.** The authoritative copies
are `docs/SUP-TRIAGE-PROTOCOL.md` and `docs/KEYWORD-LEDGER-CANDIDATES.md`.

## How these came to exist

Commit `abf9c2b` (2026-07-19) migrated four documents from
`mtjawnny.github.io/docs` into this repo by **copy, not move**. The site
originals stayed put — and because that directory is gitignored wholesale,
they had no version history and nothing detected them drifting. Both copies
then grew independently for six weeks. Neither became a superset:

| | gained |
|---|---|
| this repo | Gate #0 (b6 D1), member roster (b6 D6), remove-and-rehome (b6 D5), naming grammar (b7 §12) |
| the site fork | *"SUP standard updates (ratified batch 2, binding from batch 3 onward)"* |

So the copy the `/triage-*` skills actually load was missing five ratified
standing rules — including **"Don't absorb, expand"** — from 2026-07-19
until 2026-08-02. Batches 4–7 and corpus-pass run 1 all ran without it in
the operational protocol.

## Status of each fork

| file | verdict |
|---|---|
| `SUP-TRIAGE-PROTOCOL.md` (120 ln) | **fully absorbed** into `docs/SUP-TRIAGE-PROTOCOL.md` (§ "SUP standard updates", restored 2026-08-02, commit `25613c6`). The only remaining diff is older phrasing of a rule the live copy already carries. |
| `KEYWORD-LEDGER-CANDIDATES.md` (135 ln) | **nothing unique** — the live copy was already a strict superset. Kept purely as evidence of the fork. |

`BACKEND-BUILD-PLAN.md` was the third duplicate. It was **byte-identical**
to `docs/BACKEND-BUILD-PLAN.md`, so it was removed rather than archived —
storing a third verbatim copy would have invited exactly the "which one is
real" confusion this directory documents. `CLAUDE.md` now points at the
local tracked copy.

## The lesson, since it cost six weeks

A copy is not a migration. If a document belongs in this repo, **move** it,
and leave nothing behind that can drift. `CLAUDE.md`'s Reference section
now states this as a standing rule.

Still deliberately site-resident, read by absolute path from two scripts:
`mtg-comprehensive-rules.md` and `PHASE-2-COMPLETION.md`.
