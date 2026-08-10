#!/usr/bin/env python3
"""REACHABILITY — does this work reach a shipped card?

`PRODUCT-REALITY-AUDIT-2026-08-09.md` §10 asked for exactly this file, and gave
the reason in one line:

> **every defect class that got a TOOL stopped recurring; the one class that got
> a PARAGRAPH reached 21 instances.**

The audit's central finding — the foundry produces nothing the product reads —
got a paragraph. Every gate in this repo answers *"did I break anything?"* and
none answers *"does this reach a card?"* This one answers the second question,
and only that one.

WHAT IT DOES
------------
1. Reads the **shipped build's own entry points out of `.github/workflows/`**,
   never a hand-list. "A hand-list is not a shortcut, it is a defect with a
   delay" — and the workflow is the only artifact that decides what actually
   runs.
2. Walks the transitive local-import closure of those entry points.
3. Collects every path literal the closure can read, by AST, not by regex.
4. Reports which FOUNDRY artifacts land inside that closure, and which do not.
5. Rides the existing ratchet (`foundry_audit_baseline.py`), so a wire that
   appears and later disappears is FATAL rather than merely printed.

WHY IT IS NOT JUST A REPORTER
-----------------------------
"A GUARD THAT HAS NEVER BEEN SHOWN TO FAIL IS NOT KNOWN TO BE A GUARD", and
`foundry_definition_drift` / `foundry_ruling_registry` were both listed as
gates while being incapable of failing. So: `--selftest` proves this file can
report a failure, and the pinned metric `reaching_product` is `WORSE_IF_DOWN`.
Today it is **0** and cannot fall — which is precisely the finding, stated as a
number that a session cannot skim past.

    python3 experiments/foundry_reachability.py
    python3 experiments/foundry_reachability.py --update-baseline
    python3 experiments/foundry_reachability.py --selftest
"""
import argparse
import ast
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "experiments"))
import foundry_common as fc                # noqa: E402
import foundry_audit_baseline as baseline  # noqa: E402

WORKFLOWS = REPO / ".github" / "workflows"
SEARCH_DIRS = ("pipeline", "experiments")

# A foundry artifact is anything the foundry GENERATES or PARSES AT RUN TIME to
# produce vocabulary. Both halves matter: grammar §2 is parsed at run time, so a
# markdown file is as load-bearing here as a json one ("a markdown table is an
# API", recorded three times in CLAUDE.md).
FOUNDRY_ARTIFACTS = {
    "experiments/out/foundry/codebook.json":
        "the 403-axis codebook — every ratified membership",
    "experiments/out/foundry/det-patterns-v2.json":
        "the ratified DET patterns",
    "docs/CODEBOOK-NAMING-GRAMMAR.md":
        "grammar §2 — the DELIVERY vocabulary, parsed at run time",
    "experiments/out/foundry/corpus_pass_run1_classification.json":
        "the full-corpus pass (STOPPED_FOR_CAPTAIN)",
    "experiments/out/card-tags.json.gz":
        "the inverted Tagger index tier_engine scores against",
}

# Paths that are DATA the pipeline already ships, listed so the report can say
# what the closure DOES read rather than only what it does not.
PATH_HINT = re.compile(r"[/\\]|\.(json|jsonl|gz|md|yaml|yml|parquet|sqlite|bin|txt)$")


def entry_points() -> list:
    """The shipped build's entry points, parsed out of the workflow.

    HALTS if the workflow yields none. A reachability report built on an empty
    entry set would find every artifact unreachable and read as a catastrophic
    finding rather than a broken probe -- the guessed-vocabulary defect aimed at
    this file's own input.
    """
    if not WORKFLOWS.is_dir():
        fc.halt(f"{WORKFLOWS} does not exist. The shipped entry points are "
                f"derived from the workflow, never hand-listed, so there is "
                f"nothing to derive from and this check cannot run.")
    found = []
    for wf in sorted(WORKFLOWS.glob("*.y*ml")):
        for m in re.finditer(r"python3?\s+([\w./\\-]+\.py)", wf.read_text(encoding="utf-8")):
            rel = m.group(1)
            if (REPO / rel).exists() and rel not in [f[0] for f in found]:
                found.append((rel, wf.name))
    if not found:
        fc.halt(f"no `python3 <script>.py` step found in any workflow under "
                f"{WORKFLOWS}. Either the build stopped being Python or the "
                f"step syntax changed; refusing to report 'nothing reaches the "
                f"product' on an empty entry set.")
    return found


def resolve_module(name: str) -> Path:
    """A local module path for `name`, or None if it is third-party/stdlib."""
    tail = name.split(".")[-1]
    for d in SEARCH_DIRS:
        p = REPO / d / f"{tail}.py"
        if p.exists():
            return p
    return None


def scan(path: Path) -> tuple:
    """(imported local modules, path-shaped string literals) for one file, by AST."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as e:
        fc.halt(f"{path} does not parse ({e}). A file skipped silently would "
                f"drop its whole import subtree from the closure and understate "
                f"what the product reads.")
    imports, literals = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imports.add(a.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                imports.add(node.module)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            v = node.value
            if PATH_HINT.search(v) and len(v) < 200 and "\n" not in v:
                literals.add(v)
    return imports, literals


def closure(entries: list) -> tuple:
    """Transitive local-import closure, and every path literal reachable in it."""
    seen, literals, queue = {}, {}, [REPO / e for e, _ in entries]
    while queue:
        path = queue.pop()
        rel = str(path.relative_to(REPO))
        if rel in seen:
            continue
        imps, lits = scan(path)
        seen[rel] = sorted(imps)
        for l in lits:
            literals.setdefault(l, set()).add(rel)
        for name in imps:
            m = resolve_module(name)
            if m is not None:
                queue.append(m)
    return seen, literals


def reaches(artifact: str, literals: dict) -> list:
    """Modules in the closure whose path literals name `artifact`.

    Matched on the BASENAME as well as the full relative path: a module may
    build its path from a directory constant plus a filename, so requiring the
    whole string would under-report a real wire -- and under-reporting here
    means reporting a wire that EXISTS as absent, the one direction this file
    must never get wrong.
    """
    base = Path(artifact).name
    hits = set()
    for lit, mods in literals.items():
        if artifact in lit or lit.endswith(base) or base in lit:
            hits |= mods
    return sorted(hits)


def inverse_census(literals_all_repo=True) -> dict:
    """artifact -> experiments/ modules that read it. Context, not a verdict:
    it is what makes "13 importers, all audits" a number instead of a story."""
    out = {a: [] for a in FOUNDRY_ARTIFACTS}
    for py in sorted((REPO / "experiments").glob("*.py")):
        try:
            _, lits = scan(py)
        except SystemExit:
            raise
        for a in FOUNDRY_ARTIFACTS:
            base = Path(a).name
            if any(base in l for l in lits):
                out[a].append(f"experiments/{py.name}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--update-baseline", action="store_true")
    ap.add_argument("--selftest", action="store_true",
                    help="prove this check can FAIL — inject a lost wire")
    args = ap.parse_args()

    entries = entry_points()
    mods, literals = closure(entries)

    print("=" * 78)
    print("REACHABILITY — which foundry artifacts reach a shipped card")
    print("=" * 78)
    print(f"\nSHIPPED ENTRY POINTS ({len(entries)}) — parsed from the workflow, "
          f"never hand-listed:")
    for rel, wf in entries:
        print(f"    {rel:<34} ({wf})")
    print(f"\nTRANSITIVE IMPORT CLOSURE: {len(mods)} local module(s)")
    for rel in sorted(mods):
        print(f"    {rel}")

    print("\n" + "-" * 78)
    print("FOUNDRY ARTIFACTS vs THE SHIPPED CLOSURE")
    print("-" * 78)
    reaching, orphaned = [], []
    for art, why in sorted(FOUNDRY_ARTIFACTS.items()):
        hits = reaches(art, literals)
        (reaching if hits else orphaned).append(art)
        mark = "REACHES PRODUCT" if hits else "orphaned"
        print(f"  [{mark:^15}] {art}")
        print(f"                    {why}")
        if hits:
            for h in hits:
                print(f"                    read by: {h}")

    print("\n" + "-" * 78)
    print("WHO DOES READ THEM — the closed loop, as a census")
    print("-" * 78)
    inv = inverse_census()
    for art in sorted(FOUNDRY_ARTIFACTS):
        consumers = inv[art]
        print(f"  {Path(art).name:<42} {len(consumers):>3} experiments/ consumer(s)")

    print("\n" + "=" * 78)
    print("VERDICT")
    print("=" * 78)
    print(f"  foundry artifacts reaching a shipped card   {len(reaching):>3}"
          f" of {len(FOUNDRY_ARTIFACTS)}")
    for a in reaching:
        print(f"      + {a}")
    print(f"  orphaned (read only by audits/probes)       {len(orphaned):>3}")
    if not reaching:
        print("\n  NOTHING THE FOUNDRY PRODUCES REACHES A SHIPPED CARD.")
        print("  This is the product audit's central finding, as a number that")
        print("  a session cannot skim past. It is not a build failure — it is")
        print("  the state of the wire, reported every run until it changes.")

    metrics = {
        "entry_points": len(entries),
        "closure_modules": len(mods),
        "artifacts_reaching_product": len(reaching),
        "artifacts_orphaned": len(orphaned),
        "consumers": {Path(a).name.replace(".", "_"): len(inv[a])
                      for a in sorted(FOUNDRY_ARTIFACTS)},
    }
    if args.selftest:
        return selftest(metrics)

    regressions = baseline.report("reachability", metrics, args.update_baseline)
    return 1 if regressions else 0


def selftest(metrics: dict) -> int:
    """NEGATIVE CONTROL — aimed at the code path, not at this file's name.

    "Three of the eight negative controls were mis-aimed, each first reading as
    'this gate is broken'." The obvious injection here is mis-aimed: today
    `artifacts_reaching_product` is **0**, so simulating a LOST wire changes
    nothing and the tool would correctly report no regression — which reads as
    a broken guard.

    The path that must be proven is the ratchet's WORSE_IF_DOWN arm on
    `reaching`. So this pins a SYNTHETIC baseline in which one wire existed,
    compares today's reality against it, and asserts the drop is fatal. It
    writes to its own section and removes it afterwards, so the real pinned
    baseline is never touched.
    """
    import json
    section = "reachability_selftest"
    pretend = dict(metrics)
    pretend["artifacts_reaching_product"] = metrics["artifacts_reaching_product"] + 1
    pretend["consumers"] = dict(metrics["consumers"])
    baseline.save(section, pretend)
    try:
        regressions, changes, _ = baseline.compare(section, metrics)
        keys = [k for k, *_ in regressions]
        print("\n" + "=" * 78)
        print("SELFTEST — can this check REPORT a lost wire?")
        print("=" * 78)
        print(f"  pinned a synthetic baseline claiming "
              f"{pretend['artifacts_reaching_product']} artifact(s) reached the")
        print(f"  product; reality is {metrics['artifacts_reaching_product']}.")
        for k, a, b, why in regressions:
            print(f"    ✗ {k}: {a} → {b}   {why}")
        ok = any("reaching" in k for k in keys)
        print(f"\n  {'PASS' if ok else 'FAIL'} — a lost wire is "
              f"{'FATAL' if ok else 'INVISIBLE'} to this check.")
        if not ok:
            print("  This check cannot fail and must not be listed as a gate.")
        return 0 if ok else 1
    finally:
        doc = json.loads(baseline.BASELINE.read_text(encoding="utf-8"))
        doc.pop(section, None)
        baseline.BASELINE.write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
