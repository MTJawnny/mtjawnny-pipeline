# Oracle Compiler Program

**Status:** CAPTAIN-DECIDED PROGRAM (Issue #1, "Captain decision — Autonomous
Oracle Compiler program", decisions C–G, 2026-09-28).

This file is not a selector. Work runs only when the latest `K` on Issue #1
selects its `T`. It records how the `PLAN.md` package map is carried to its
finish line, and where it must stop for the Captain.

## How a package runs

- One package is one `T`. Its Worker is Claude Code or Codex; its reviewer is
  the **other** model (decision E). The reviewer's verdict is the `V`; no model
  accepts its own work.
- A task-internal conflict is first sent to the other model; the Worker then
  proceeds only within the task's scope and records both analyses (decision F).
- Unattended continuation uses the Agent Bus: a Captain-rooted goal plan
  (`refoundation/AGENT-BUS-MANAGER-TRIGGER.md` section 6) names each wave's
  command and checks, and the local cross-review Manager
  (`agent_bus.local_manager`) accepts, repairs or escalates each wave.
- Evidence is durable on Issue #1 before a package is accepted.

## Finish line per package

| package | finish line (accepted by cross-review unless marked) |
|---|---|
| C00, M01, M02, M03 | done before this program |
| C01 | AQ4 Packet-0 preflight PASS: freeze intact, Gate 2 green, no law conflict |
| C02 | sec. 27 probes P1–P4 measured under frozen code, deterministic x2 |
| Wave-1 review | `analysis/` review of C01–C02 against V1; may propose `oracle-compiler-interface/1` — **ratifying it is Captain's** |
| C03 | H-REGION falsification over C02's multi-effect clauses and the COST-region precedent, with every V1 P0.3 output and its kill conditions — **a fired kill condition returns to the Captain** |
| C03b | trace renderer for C03 output (validation tool only) |
| M04 | H-REGION semantic review |
| C04 | reference-resolution experiment over the P4 population (V1 P0.4); unknown stays explicit |
| M05 | reference semantic audit |
| C05 | coverage-ledger prototype as the smallest extension of residue machinery (V1 P0.5) |
| C06 | full verbalizer (V1 P0.7), validation tool only |
| M06 | adversarial acceptance review of C03–C06 |
| Wave 4 | parser bake-off on `FIXTURES.json` (V1 P0.8) — **parser selection is Captain's** |

**Program finish line:** M06 accepted and the Wave-4 bake-off report delivered.
Nothing here adopts production schema, vocabulary or AQ4 architecture.

V1 P0.6 (the Round-2 seam audits) is required by V1 but not placed in the
`PLAN.md` map; where it runs is a batched Captain decision.

## Captain boundaries (recorded on Issue #1, batched; other work continues)

- `oracle-compiler-interface/1` and any semantic-law interface change;
- a fired H-REGION kill condition;
- vocabulary or schema minting; any semantics or scoring change;
- AQ4 production adoption or ownership;
- parser technology selection;
- every merge and any `main` movement.
