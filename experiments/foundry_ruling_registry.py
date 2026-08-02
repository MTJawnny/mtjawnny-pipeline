#!/usr/bin/env python3
"""Harvest every ratified-ruling reference across docs/ into one registry.

Purpose: no document may be deleted until every ruling it carries is
provably recorded somewhere else. Dependency analysis alone proved
insufficient -- 2026-08-02, every deletion candidate turned out to carry
ruling text (44 markers in B-MIGRATION-AUDIT-PACKET alone).

This is a DET job. No mutation of anything but its own outputs, no API
calls, no card data. Deterministic: explicit sort keys everywhere, no
reliance on set/dict iteration order (see CLAUDE.md traps).

Outputs:
  docs/RATIFIED-RULINGS-REGISTRY.md    human-readable registry
  experiments/out/foundry/ruling_registry.json   machine-checkable

Usage:
  python3 experiments/foundry_ruling_registry.py
  python3 experiments/foundry_ruling_registry.py --check <doc.md>
      exit 0 if every ruling in <doc> also appears elsewhere (safe to
      delete), exit 1 otherwise, listing the unique rulings that block it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs"
OUT_JSON = REPO_ROOT / "experiments" / "out" / "foundry" / "ruling_registry.json"
OUT_MD = DOCS / "RATIFIED-RULINGS-REGISTRY.md"

# Generated artifact -- never a harvest source (it would cite every ruling
# and make every doc look redundantly covered).
SELF_EXCLUDE = {"RATIFIED-RULINGS-REGISTRY.md"}

# IDs whose shape is unambiguous: harvested wherever they appear.
UNAMBIGUOUS = re.compile(
    r"\b(?:CDR-\d{1,2}|ADD-\d{1,2}|NEW-\d{1,2}|GRAMMAR-SS\d{1,2}|AG-[A-Z]+-\d{2}|B-\d{2}|H-\d{2}|M-\d{2})\b"
)

# Short IDs (D5, Q8.5, S3, A15...). Ambiguous on their own -- a bare "A1"
# is often prose -- so a hit only counts in one of two contexts:
#   (a) the line carries a ruling word, or
#   (b) the id sits in DEFINITION POSITION.
# (b) was missing in the first cut and it mattered: this codebase writes
# rulings as "- **A8** -- statement", which contains no ruling keyword, so
# A8 was harvested from 1 doc when it actually lives in 6. That produced a
# FALSE deletion-block. Under-harvesting is not "safely conservative"
# here -- it makes the gate untrustworthy in both directions.
SHORT_ID = re.compile(r"\b([ADQSTMRFG])[-\s]?(\d{1,2}(?:\.\d{1,2})?)\b")
RULING_WORD = re.compile(
    r"ratifi|ruled|ruling|captain|verdict|decision|standing|precedent|overturn|amend",
    re.IGNORECASE,
)
# "**A8**", "- **A8 (CDR-07):**", "| A8 |", "1. A8 —", "A8." at line start
DEFINITION_POS = re.compile(
    r"(?:^|[-*|]\s*|^\d+\.\s*)\*{0,2}([ADQSTMRFG])[-\s]?(\d{1,2}(?:\.\d{1,2})?)"
    r"\*{0,2}\s*(?:[(:—–.-]|\*\*)"
)

# Lines that are pure navigation rather than a ruling statement.
NOISE = re.compile(r"^\s*(?:\||#{1,6}\s*$|-{3,}|={3,})")

MAX_STATEMENT = 220


def normalise_id(kind: str, num: str) -> str:
    return f"{kind}{num}"


def harvest_file(path: Path) -> list[dict]:
    """Return one record per ruling reference found in `path`."""
    hits: list[dict] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        print(f"HALT: {path.name} is not valid UTF-8", file=sys.stderr)
        raise

    for lineno, raw in enumerate(lines, start=1):
        line = raw.rstrip()
        if not line.strip() or NOISE.match(line):
            continue
        statement = re.sub(r"\s+", " ", line.strip().lstrip("-*# ").strip())
        if len(statement) > MAX_STATEMENT:
            statement = statement[: MAX_STATEMENT - 1] + "…"

        found: list[str] = []
        for m in UNAMBIGUOUS.finditer(line):
            found.append(m.group(0))
        if RULING_WORD.search(line):
            for m in SHORT_ID.finditer(line):
                found.append(normalise_id(m.group(1), m.group(2)))
        for m in DEFINITION_POS.finditer(line):
            found.append(normalise_id(m.group(1), m.group(2)))

        # sorted+dedup, so ordering never depends on set iteration
        for rid in sorted(set(found)):
            hits.append(
                {
                    "id": rid,
                    "doc": path.name,
                    "line": lineno,
                    "statement": statement,
                }
            )
    return hits


def build() -> dict:
    docs = sorted(p for p in DOCS.glob("*.md") if p.name not in SELF_EXCLUDE)
    if not docs:
        raise SystemExit("HALT: no markdown found under docs/")

    all_hits: list[dict] = []
    for p in docs:
        all_hits.extend(harvest_file(p))
    all_hits.sort(key=lambda h: (h["id"], h["doc"], h["line"]))

    by_id: dict[str, list[dict]] = {}
    for h in all_hits:
        by_id.setdefault(h["id"], []).append(h)

    # A ruling is CORROBORATED when it appears in more than one document.
    # A doc is DELETION-BLOCKED while it is the sole home of any ruling.
    sole_home: dict[str, list[str]] = {}
    for rid in sorted(by_id):
        docs_with = sorted({h["doc"] for h in by_id[rid]})
        if len(docs_with) == 1:
            sole_home.setdefault(docs_with[0], []).append(rid)

    per_doc: dict[str, dict] = {}
    for p in docs:
        ids = sorted({h["id"] for h in all_hits if h["doc"] == p.name})
        unique = sorted(sole_home.get(p.name, []))
        per_doc[p.name] = {
            "lines": len(p.read_text(encoding="utf-8").splitlines()),
            "ruling_ids": ids,
            "sole_home_for": unique,
            "deletion_blocked": bool(unique),
        }

    return {
        "schema": "foundry-ruling-registry/1",
        "generated_from": f"{len(docs)} documents under docs/",
        "total_references": len(all_hits),
        "distinct_rulings": len(by_id),
        "corroborated": sum(
            1 for rid in by_id if len({h["doc"] for h in by_id[rid]}) > 1
        ),
        "sole_home": sum(
            1 for rid in by_id if len({h["doc"] for h in by_id[rid]}) == 1
        ),
        "rulings": {rid: by_id[rid] for rid in sorted(by_id)},
        "per_doc": {k: per_doc[k] for k in sorted(per_doc)},
    }


def write_markdown(reg: dict) -> None:
    L: list[str] = []
    A = L.append
    A("# RATIFIED RULINGS REGISTRY — generated, do not hand-edit")
    A("")
    A("Generated by `experiments/foundry_ruling_registry.py`. Re-run after any")
    A("doc change. Per ADD-06 the numbers below are pasted from generator")
    A("output, never restated by hand.")
    A("")
    A("**This registry is the deletion gate.** A document may not be deleted")
    A("while it is the SOLE HOME of any ruling — that ruling must first be")
    A("moved somewhere durable. Check one doc with:")
    A("")
    A("```")
    A("python3 experiments/foundry_ruling_registry.py --check <NAME>.md")
    A("```")
    A("")
    A("## Summary")
    A("")
    A(f"- documents scanned: **{reg['generated_from']}**")
    A(f"- ruling references found: **{reg['total_references']}**")
    A(f"- distinct ruling ids: **{reg['distinct_rulings']}**")
    A(f"- corroborated (appear in >1 doc): **{reg['corroborated']}**")
    A(f"- **sole-home (appear in exactly 1 doc): {reg['sole_home']}**")
    A("")
    A("## Deletion gate — per document")
    A("")
    A("| document | lines | rulings | sole home for | deletable |")
    A("|---|---:|---:|---:|---|")
    for name in sorted(reg["per_doc"]):
        d = reg["per_doc"][name]
        if not d["ruling_ids"]:
            continue
        A(
            f"| `{name}` | {d['lines']} | {len(d['ruling_ids'])} | "
            f"{len(d['sole_home_for'])} | "
            f"{'**NO**' if d['deletion_blocked'] else 'yes'} |"
        )
    A("")
    A("### Documents carrying no ruling reference (deletable on this test alone)")
    A("")
    clean = [n for n in sorted(reg["per_doc"]) if not reg["per_doc"][n]["ruling_ids"]]
    A(", ".join(f"`{n}`" for n in clean) if clean else "_(none)_")
    A("")
    A("## Sole-home rulings — these block their document")
    A("")
    for name in sorted(reg["per_doc"]):
        d = reg["per_doc"][name]
        if not d["sole_home_for"]:
            continue
        A(f"**`{name}`** — sole home for {len(d['sole_home_for'])}:")
        A("")
        for rid in d["sole_home_for"]:
            occ = reg["rulings"][rid][0]
            A(f"- `{rid}` (line {occ['line']}) — {occ['statement']}")
        A("")
    A("## Full registry")
    A("")
    for rid in sorted(reg["rulings"]):
        occ = reg["rulings"][rid]
        homes = sorted({o["doc"] for o in occ})
        A(f"### `{rid}` — {len(occ)} reference(s) across {len(homes)} doc(s)")
        A("")
        for o in occ:
            A(f"- `{o['doc']}:{o['line']}` — {o['statement']}")
        A("")
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", metavar="DOC", help="is DOC safe to delete?")
    args = ap.parse_args()

    reg = build()

    if args.check:
        name = Path(args.check).name
        d = reg["per_doc"].get(name)
        if d is None:
            print(f"HALT: {name} not found under docs/", file=sys.stderr)
            return 2
        if not d["deletion_blocked"]:
            print(f"SAFE: {name} — {len(d['ruling_ids'])} ruling(s), all "
                  f"recorded elsewhere.")
            return 0
        print(f"BLOCKED: {name} is the sole home of "
              f"{len(d['sole_home_for'])} ruling(s):")
        for rid in d["sole_home_for"]:
            occ = reg["rulings"][rid][0]
            print(f"  {rid:14s} line {occ['line']:5d}  {occ['statement'][:90]}")
        return 1

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(
        json.dumps(reg, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_markdown(reg)

    # ADD-06: print the exact block a commit message should carry.
    print("=" * 62)
    print("RULING REGISTRY")
    print(f"  documents scanned      {reg['generated_from']}")
    print(f"  ruling references      {reg['total_references']}")
    print(f"  distinct ruling ids    {reg['distinct_rulings']}")
    print(f"  corroborated (>1 doc)  {reg['corroborated']}")
    print(f"  sole-home (1 doc only) {reg['sole_home']}")
    blocked = sorted(
        n for n in reg["per_doc"] if reg["per_doc"][n]["deletion_blocked"]
    )
    clean = sorted(
        n for n in reg["per_doc"]
        if reg["per_doc"][n]["ruling_ids"] and not reg["per_doc"][n]["deletion_blocked"]
    )
    print(f"  docs deletion-BLOCKED  {len(blocked)}")
    print(f"  docs deletable         {len(clean)}")
    print("=" * 62)
    print(f"wrote {OUT_MD.relative_to(REPO_ROOT)}")
    print(f"wrote {OUT_JSON.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
