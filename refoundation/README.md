# REFOUNDATION CONTROL PLANE

This directory is temporary refoundation governance/scaffolding. It exists so ChatGPT Manager and Claude Code Worker sessions can be disposable without losing durable project state.

It is **not Foundry semantic law** and it is not a substitute for GitHub Issue #1.

## Governing principle

> **PRESERVE TRUTH, NOT PLUMBING.**

Paths, imports, handoffs, temporary plans, and scaffolding may be rewritten or removed. Semantic truth and accepted governance state must not change silently as a side effect.

## Authority and current-state routing

- **GitHub Issue #1** — durable Manager/Worker control plane. The latest valid `K` carries accepted head `h` and active task `a`; `a` selects the only executable Worker `T`.
- `CAPTAIN-DIRECTION.md` — durable Captain direction for the refoundation.
- `SESSION-PROTOCOL.md` — current Manager/Worker state-machine rules.
- `ACTIVE-PHASE.yaml` — compact, replaceable phase context only; Issue #1 outranks it.
- `BOOTSTRAP-STATE.yaml` — superseded bootstrap pointer retained only to route old references forward.
- `MANAGER-START.md` — cold-start pointer for a GitHub-enabled ChatGPT Manager.
- `WORKER-START.md` — cold-start pointer for Claude Code; root `CLAUDE.md` remains the canonical Worker contract.

## Fresh Manager read order

1. `CAPTAIN-DIRECTION.md`
2. `SESSION-PROTOCOL.md`
3. `MANAGER-START.md`
4. GitHub Issue #1 — latest `K`, then only its selected `T` and relevant `X`/`V`
5. `ACTIVE-PHASE.yaml` for phase context
6. deeper repository evidence only as required

## Fresh Worker read order

Root `CLAUDE.md` is auto-loaded and authoritative for Worker operation. Follow its startup contract: inspect local state, read Issue #1 latest `K -> active T`, verify base/scope, and execute exactly that task. `WORKER-START.md` is only a short pointer.

## Current standing controls

Unless a newer durable GitHub record explicitly supersedes them: AQ4 is paused, Bridge v0 is unused/parked, Step6 is not started, and merge is not authorized.

No old bootstrap branch, dated handoff, historical task, or README statement assigns work. History remains in Git and in the durable Issue #1 event log.
