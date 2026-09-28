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
| Wave-1 review | `analysis/WAVE1-REVIEW.md`: C01–C02 against V1; proposes `oracle-compiler-interface/1`, ratified on cross-review acceptance within decision H3's bounds (no production vocabulary/schema, no AQ4 promotion) |
| F0 | fixture selection freeze (Wave-1 review F2): `FIXTURES.json` and the M03 crosswalk brought byte-identical from `1efd2e0`, null members filled by recorded deterministic rules over accepted C02 output, before any C03 result exists — **C03 does not start before F0 is accepted** |
| C03 | H-REGION falsification over C02's multi-effect clauses and the COST-region precedent, with every V1 P0.3 output and its kill conditions — **a fired kill condition returns to the Captain** |
| C03b | trace renderer for C03 output (validation tool only) |
| M04 | H-REGION semantic review |
| A01 | V1 P0.6 Round-2 seam audits, one unit each: R2-A replacement-event lineage, R2-B decision authority (CR 723), R2-C ability borrowing/inheritance. Each first proves whether an existing structure suffices, and each STOPs before vocabulary/schema minting |
| C04 | reference-resolution experiment over the P4 population (V1 P0.4); unknown stays explicit |
| M05 | reference semantic audit |
| C05 | coverage-ledger prototype as the smallest extension of residue machinery (V1 P0.5) |
| C06 | full verbalizer (V1 P0.7), validation tool only |
| M06 | adversarial acceptance review of C03–C06 |
| Wave 4 | parser bake-off on `FIXTURES.json` (V1 P0.8) — **parser selection is Captain's** |

**Program finish line:** M06 accepted and the Wave-4 bake-off report delivered.
Nothing here adopts production schema, vocabulary or AQ4 architecture.

V1 P0.6 (the Round-2 seam audits) is required by V1 but not in the `PLAN.md`
map. Placement was delegated to cross-review (decision H4, Issue #1 comment
5877426463) and is A01 above, after M04 and before C04: read-only and
independent of H-REGION, ahead of C04's replacement-lineage endpoints, and ahead
of every later package that could approach schema (Wave-1 review §6).

## Captain boundaries (recorded on Issue #1, batched; other work continues)

- `oracle-compiler-interface/1` beyond decision H3's bounds, and any semantic-law
  interface change;
- a fired H-REGION kill condition;
- vocabulary or schema minting; any semantics or scoring change;
- AQ4 production adoption or ownership;
- parser technology selection;
- every merge and any `main` movement.
