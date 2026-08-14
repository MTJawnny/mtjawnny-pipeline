#!/usr/bin/env python3
"""GATE 2, AS ONE COMMAND — because ten commands can be run as nine.

`SESSION-START-PROCEDURE.md` Gate 2 is a list of shell commands a session is
trusted to run in full. That trust is the same shape as every other failure
this project has measured: **a control that depends on someone remembering is
not a control.** A skipped gate is indistinguishable from a passing one in the
transcript, and the procedure's own opening line admits the risk -- *"a long
procedure does not get followed."*

This runs every gate, reports a single table, and exits 1 if ANY of them fails.

WHAT IT DOES NOT DO
-------------------
It does not re-implement a single check. Each row shells out to the real tool,
so there is exactly one definition of each gate and this file cannot drift from
it. That is the `foundry_probe` principle applied to the runner itself.

`--selftest` proves the runner can REPORT a failure, by running a gate that is
rigged to fail. A runner that always prints green is worse than no runner.

    python3 experiments/foundry_gate2.py
    python3 experiments/foundry_gate2.py --selftest
    python3 experiments/foundry_gate2.py --only ground_truth,conservation
"""
import sys
import time
import argparse
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXP = "experiments"

# name -> (argv, what a FAILURE means). Order is the procedure's order.
GATES = [
    ("lint",             [f"{EXP}/foundry_codebook.py", "lint"],
     "the codebook is structurally invalid"),
    ("family_sweep",     [f"{EXP}/foundry_family_sweep.py", "--strict"],
     "a ratified family and its members contradict"),
    ("definition_drift", [f"{EXP}/foundry_definition_drift.py"],
     "an axis definition drifted from its name (ratcheted 2026-08-09)"),
    ("ruling_registry",  [f"{EXP}/foundry_ruling_registry.py"],
     "a ruling lost its home (ratcheted 2026-08-09)"),
    ("conservation",     [f"{EXP}/foundry_punctuation_audit.py"],
     "text, a sentence or an ability was LOST"),
    ("visibility",       [f"{EXP}/foundry_visibility_audit.py"],
     "an option became unreachable"),
    ("ground_truth",     [f"{EXP}/foundry_ground_truth.py"],
     "a ratified assignment and the extractor disagree"),
    ("ground_truth_wide", [f"{EXP}/foundry_ground_truth.py", "--wide"],
     "the 1,181-assertion fixture regressed (ratcheted, not zero-based)"),
    ("gate_audit",       [f"{EXP}/foundry_gate_audit.py"],
     "the extractor crashes on what the corpus gate excludes"),
    ("probe_guards",     [f"{EXP}/foundry_probe.py"],
     "a probe-library guard stopped being able to halt"),
    ("recorded_numbers", [f"{EXP}/foundry_recorded_numbers.py", "--strict"],
     "a count grammar §2 asserts no longer reproduces"),
    ("invariance",       [f"{EXP}/foundry_routing_regression.py", "invariance",
                          "--strict"],
     "a delivery depends on the CARD NAME"),
    # PRODUCT-REALITY-AUDIT-2026-08-09.md §10, added 2026-08-09. Every row
    # above answers "did I break anything?"; this one answers "does this reach
    # a card?" -- the question the audit found no gate could ask. It is
    # ratcheted (WORSE_IF_DOWN on `reaching`) and negative-controlled
    # (`--selftest`), so it is a gate rather than a reporter listed as one.
    ("reachability",     [f"{EXP}/foundry_reachability.py"],
     "a foundry artifact stopped reaching a shipped card"),
    # OBJECT-LATTICE-RESIDUAL-RULING-2026-08-13.md, added 2026-08-13 with the
    # lattice's ratification. Three checks, one exit code: the grammar-shape
    # fixtures, the independent residual invariant, and the pinned per-class
    # membership ratchet. The ratchet is the row that makes a REMOVAL fatal --
    # `e780842` removed 170 memberships, verified 83, and nothing on this list
    # could see the other 87.
    ("object_lattice",   [f"{EXP}/foundry_object_lattice.py", "--gate"],
     "the object lattice lost memberships, or a residual went unexplained"),
    # SEMANTIC-ADDRESS ratification, 2026-08-13 (resolves FL-2). Fixtures for
    # the six ratified negative controls plus a ratchet on owner coverage.
    # Negative-controlled by `--selftest`, which swaps in a first-match-wins
    # resolver and requires the fixtures to catch it.
    ("locality",         [f"{EXP}/foundry_locality.py", "--gate"],
     "semantic-locality coverage fell, or the resolution law regressed"),
    # Added 2026-08-13. THIS ROW PROTECTS REPRODUCIBILITY, NOT A NUMBER. The
    # qualifier packet's evidence base previously lived only in a scratchpad
    # that was thrown away, so a committed document pointed at figures nothing
    # could re-derive. It deliberately pins NO rate: 49.3%, 2,110 and x9.7 are
    # detector-sensitive and a tolerance band would be the tuning knob the
    # engine rules forbid. What it pins is that the CR vocabulary still parses,
    # the counting key's premise still holds, the base-class strip still
    # prevents the double count, and a missing category still cannot move the
    # rate. It ratifies no qualifier vocabulary and mints nothing.
    ("qualifier_census", [f"{EXP}/foundry_qualifier_census.py", "--gate"],
     "the qualifier census can no longer be re-derived as published"),
]

# family_sweep has a STANDING failure (the 6 blocking findings) that predates
# this runner and is tracked as W6. Listing it here keeps the runner honest --
# it is not silently excused, it is reported as a known-failing gate with the
# reason, and `--strict-all` refuses to accept even that.
KNOWN_FAILING = {"family_sweep": "the standing 6 blocking findings (W6)"}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", help="comma-separated gate names")
    ap.add_argument("--strict-all", action="store_true",
                    help="do not excuse the known-failing gates either")
    ap.add_argument("--selftest", action="store_true",
                    help="prove this runner can REPORT a failure")
    args = ap.parse_args()

    gates = list(GATES)
    if args.selftest:
        gates.append(("SELFTEST_rigged", ["-c", "raise SystemExit(1)"],
                      "this row is rigged to fail on purpose"))
    if args.only:
        want = {s.strip() for s in args.only.split(",")}
        gates = [g for g in gates if g[0] in want]
        missing = want - {g[0] for g in gates}
        if missing:
            print(f"unknown gate(s): {sorted(missing)}", file=sys.stderr)
            return 2

    print("=" * 78)
    print("GATE 2 — every check, one exit code")
    print("=" * 78)
    results, unexpected = [], 0
    for name, argv, meaning in gates:
        t0 = time.time()
        r = subprocess.run([sys.executable] + argv, cwd=REPO_ROOT,
                           capture_output=True, text=True)
        dt = time.time() - t0
        ok = r.returncode == 0
        known = name in KNOWN_FAILING and not args.strict_all
        if not ok and not known:
            unexpected += 1
        mark = "  ok  " if ok else ("KNOWN " if known else " FAIL ")
        print(f"  [{mark}] {name:20} exit={r.returncode}  {dt:5.1f}s")
        if not ok:
            why = KNOWN_FAILING.get(name) if known else meaning
            print(f"           -> {why}")
        results.append((name, r.returncode, ok, known, r.stdout + r.stderr))

    print("\n" + "=" * 78)
    print("VERDICT")
    print("=" * 78)
    passed = sum(1 for _, _, ok, _, _ in results if ok)
    excused = sum(1 for _, _, ok, kn, _ in results if not ok and kn)
    print(f"  gates run                     {len(results):>4}")
    print(f"  passed                        {passed:>4}")
    print(f"  known-failing (excused)       {excused:>4}")
    print(f"  UNEXPECTED failures           {unexpected:>4}")

    if unexpected:
        print("\n  ✗ Gate 2 is RED. The failing tool's own output is the")
        print("    report -- run it directly and read it. Do not proceed on")
        print("    a red gate; that is the drift this procedure exists to stop.")
        for name, code, ok, known, out in results:
            if not ok and not known:
                tail = [l for l in out.splitlines() if l.strip()][-6:]
                print(f"\n  --- {name} (exit {code}) ---")
                for l in tail:
                    print(f"    {l[:96]}")
    else:
        print("\n  ✓ Gate 2 is GREEN. Every check ran, and every one of them")
        print("    is capable of failing -- negative-controlled 2026-08-09,")
        print("    see docs/SYSTEM-SELF-TEST-2026-08-09.md.")
    return 1 if unexpected else 0


if __name__ == "__main__":
    sys.exit(main())
