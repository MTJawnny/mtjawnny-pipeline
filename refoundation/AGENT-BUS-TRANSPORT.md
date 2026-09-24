# AGENT BUS TRANSPORT SURFACE — DO NOT MERGE

This branch exists to hold one long-lived pull request whose **comments are the
event surface** the Manager wakes on. It carries no implementation and is never
intended to merge.

## Why a pull request at all

ChatGPT Work can be configured to wake on GitHub pull request activity. It does
not wake on issue comments. The Worker therefore posts its typed `WAVE_RESULT`
messages where a pull request event is produced, and the Manager wakes there and
then goes and inspects live repository state.

## What this surface is NOT

It is **not** authority. Task selection has exactly one owner:

> GitHub Issue #1 — latest `K` -> active `T`.

Every message carried here pins the checkpoint, the task and the accepted head it
was issued under. A message citing anything else is inert. A Manager `ACCEPT`
verdict posted here is a proposal; the accepted head moves only when a checkpoint
on Issue #1 says it moved. Nothing becomes law by being the newest comment on
this pull request.

If this surface and Issue #1 ever disagree, Issue #1 wins and the disagreement is
a STOP to report, not a conflict to resolve locally.

## Rules

- Do not merge this pull request.
- Do not close it while it is the configured event surface.
- Do not put implementation on this branch.
- Prose comments here are inert. Only a fenced `mtj-bus` JSON block is a message.

The transport contract is `refoundation/AGENT-BUS.md` on the accepted line of
development.
