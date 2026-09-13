# mtjawnny-pipeline

Weekly GitHub Actions pipeline: fetches Scryfall bulk data, merges custom tags,
and builds corpus artifacts for mtjawnny.com's tools. Card data is external to git.

## Cold start for any LLM

**There is exactly one task-authority mechanism: GitHub Issue #1, latest `K` -> active `T`.**

1. Read Issue #1 and resolve the latest valid `K` yourself.
2. Read `h` from that checkpoint for the accepted implementation head and `a` for the active task pointer.
3. If an active `T` exists, execute only that task and read only the subsystem authority/evidence it names.
4. If no task is selected, do not infer one from a filename, date, mtime, branch age, handoff, roadmap, or archived prompt.

Claude Code Workers also obey root `CLAUDE.md`, the role-specific operating contract.
Other LLMs should use this router plus Issue #1 and the exact active task.

`archive/` is inert history. Files there may explain prior work but never assign current work.
