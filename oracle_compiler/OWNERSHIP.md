# Oracle Compiler Ownership

**Status:** RATIFIED

This file records writable surfaces and decision ownership for the Oracle Compiler workspace. It does not select current work. Task authority remains GitHub Issue #1, `latest K -> active T`.

## Captain-owned decisions

The Captain owns:

- V1 semantic/architecture ratification;
- semantic-law interface changes;
- ownership-law changes;
- the AQ4 production decision;
- merge, accepted-head movement, and production cutover.

## Manager normal writable surface

Subject to Captain authority over ratified content, the Manager normally owns:

```text
oracle_compiler/README.md
oracle_compiler/OWNERSHIP.md
oracle_compiler/PLAN.md
oracle_compiler/INTERFACES.md
oracle_compiler/RESULTS.md
oracle_compiler/FIXTURES.json
oracle_compiler/analysis/**
```

## Worker normal writable surface when explicitly allowed by `T`

```text
src/mtj_foundry/oracle_ingest/**
tests/oracle_ingest/**
experiments/oracle_ingest/**
experiments/out/**
oracle_compiler/measurement/**
```

A Worker receives no standing write authority merely because a path appears here. The active `T` must allow the write.

## Default read-only dependencies

```text
src/mtj_foundry/** outside oracle_ingest/
benchmarks/aq4/**
docs/architecture/preflight/s16a/**
docs/architecture/preflight/s16b/**
tests/guards/**
config/**
```

## M00 bootstrap exception

M00 is a historical/bootstrap-specific exception that may update the single layout owner and its refoundation guards while installing this control surface. It is not a permanent Worker write grant to those files.

> **Do not rewrite equivalent compiler probes.**

If a task requires a write outside its listed writable surface or active-task allowlist, STOP and return the dependency. Do not widen the task locally.
