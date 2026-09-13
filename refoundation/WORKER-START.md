# FRESH WORKER — START HERE

This file is a pointer, not a manual. Nothing here is authority on its own.

- **Root `CLAUDE.md` is the canonical Worker contract**, auto-loaded every session.
- **Live task authority is GitHub Issue #1: latest `K` -> active `T`.** Nothing else assigns work.

A fresh Worker inspects local state, resolves the latest valid `K`, verifies the selected task's exact base and scope, executes exactly that one task, posts its durable result to Issue #1, and follows `CLAUDE.md`'s human-return contract.

Do not ask for a transcript or select work from a handoff, filename, date, mtime, roadmap, archived prompt, or branch chronology. A new session is normal; durable GitHub/repository state must be enough.
