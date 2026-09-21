# Oracle Compiler Plan

**Status:** RATIFIED DEPENDENCY / PACKAGE MAP

This file is not a selector and does not make any package executable. Current work is selected only by GitHub Issue #1: **latest `K` -> active `T`**.

## Package map

```text
C00  Worker mechanical census -> ignored measurement output only
M01  Manager authority classification over C00
M02  Manager fixture/gold contract; creates FIXTURES.json
M03  Manager S16A/S16B/AQ4 boundary crosswalk
C01  AQ4 Packet-0 preflight
C02  existing pre-registered AQ4 read-only probe wave after C01 PASS
Wave-1 review -> interface/1
C03  H-REGION falsification prototype
C03b minimal trace renderer
M04  H-REGION semantic review
C04  reference-resolution prototype
M05  reference semantic audit
C05  coverage-ledger prototype
C06  full verbalizer
M06  adversarial acceptance review
Wave 4 parser bake-off: Worker implements, Manager evaluates
```

Normal Captain decisions are batched at wave boundaries. A package or line above is not executable merely because it appears here; the active `T` must authorize it.

> **Do not rewrite equivalent compiler probes.**

Generated output belongs under already-ignored `experiments/out/**`. Empty analysis, measurement, archive, source, test, or experiment directories are not materialized with placeholders.
