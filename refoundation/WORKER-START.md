# FRESH WORKER — START HERE

This file is a pointer, not a manual. Nothing here is authority on its own.

## Where the rules actually live

- **Root `CLAUDE.md` is the canonical Worker contract**, auto-loaded every
  session. Read it there; it is not duplicated here.
- It imports `refoundation/ACTIVE-PHASE.yaml`, which carries the current phase.
  That is replaceable state, not task authority.
- **Live task authority is GitHub Issue #1**, through one canonical selector:
  **latest `K` -> active `T`**. Nothing else assigns you work.

## What a fresh session does

1. Inspect local state before mutating anything.
2. Read Issue #1 — **latest `K` -> active `T`**.
3. Verify the exact base and scope against measured state.
4. Execute exactly that one task.
5. Post the detailed terminal `X` to Issue #1.
6. Reply to the human with exactly: `Claude done`

## What a fresh session does not do

- Do not ask for a transcript, a scrollback dump, or a session handoff. A new
  session is normal, not exceptional. If the contract plus durable
  repository/GitHub state is not enough to resume, that is a refoundation
  defect to report — not a reason to request old chat history.
- Do not treat a prior session's claims, a filename, or an mtime as authority.
- Do not take a successor task you authorized yourself.
