#!/usr/bin/env python3
"""Generate the CR-derived check registry.

WHY
---
C1-C4 were each written AFTER a specific failure. That is backwards: the
Comprehensive Rules already enumerate the game's logic components, so the check
set is derivable rather than discovered. Captain, 2026-08-02: "why aren't we
building checks for all game logic components and having them fire when they
are spotted? the logic is so hardcoded. You almost don't need to think. just
sort."

This walks the CR and emits one registry row per game-logic term, with its rule
number and its printed forms. `foundry_definition_drift.py` can then LOOP the
registry instead of carrying hand-written checks, so adding a term is DATA, not
code.

The single most important field is `era_variants`. Every check that has broken
this project broke the same way: it encoded ONE printed form of a law and
reported every other form as a defect.
  * C4g knew "defending player" and condemned every modern card printing
    "the player or planeswalker it's attacking" -- the same CR 506.2 object.
  * C4f tested "each|all" and flagged ~50 correct axes, because modern
    templating writes a mass effect as a bare plural noun phrase.
  * §3's activation-restriction family needs "Activate this ability only ..."
    canonicalized to the modern phrase.
Era variants belong in one field, not in each check's regex.

Generated artifact -- never hand-edit it (G4: generated artifacts get generator
fixes). Read-only against the CR and the codebook. Zero tokens.

Usage:
  python3 experiments/foundry_cr_checks.py            # write docs/cr-checks.json
  python3 experiments/foundry_cr_checks.py --coverage # which CR terms have no axis
"""
import re
import sys
import json
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402
import foundry_codebook as fcb  # noqa: E402

CR_PATH = Path.home() / "Projects/mtjawnny.github.io/docs/mtg-comprehensive-rules.md"
OUT = REPO_ROOT.parent / "docs" / "cr-checks.json"

# Templating-era equivalences. Each entry is one CR object written two ways
# across printing eras; a check that knows only one form manufactures defects.
# Captain-ratified terms only -- this table is law, not convenience.
ERA_VARIANTS = {
    "defending player": ["the player or planeswalker it's attacking",
                         "the player or planeswalker that creature is attacking"],
    "activate only as a sorcery": ["activate this ability only as a sorcery",
                                   "play only as a sorcery"],
    "enters": ["enters the battlefield"],
    "dies": ["is put into a graveyard from the battlefield"],
}

# Scope / targeting terms. These are not keyword actions; they are the words
# that decide WHO and HOW MANY, and they are where C4's findings came from.
SCOPE_TERMS = [
    ("target", "601.2c", ["target", "targets"], "scope"),
    ("each", "n/a", ["each", "all", "every"], "scope"),
    ("defending player", "506.2", ["defending player"], "scope"),
    ("opponent", "102.1", ["opponent", "opponents"], "scope"),
    ("you control", "108.4", ["you control", "your"], "scope"),
    ("another", "109.1", ["another", "other"], "scope"),
    ("controller", "108.4", ["controller", "controllers"], "scope"),
]


def load_cr() -> str:
    if not CR_PATH.exists():
        fc.halt(f"Comprehensive Rules not found at {CR_PATH}. "
                f"CLAUDE.md names this file by absolute path; if it moved, fix "
                f"the contract rather than guessing a location.")
    return CR_PATH.read_text(errors="replace")


def keyword_actions(cr: str) -> list:
    """CR 701 — keyword actions. Closed vocabulary, one rule number each."""
    rows = []
    for m in re.finditer(r"^(701\.(\d+))\. ([A-Z][a-zA-Z' ]+?)\s*$", cr, re.M):
        rule, name = m.group(1), m.group(3).strip()
        if name.lower().startswith("most actions"):
            continue          # 701.1 is prose, not an action
        if len(name) > 30:
            continue
        low = name.lower()
        rows.append({
            "term": low,
            "cr": rule,
            "kind": "keyword-action",
            "printed_forms": sorted({low, low + "s", low + "es"}
                                    if not low.endswith("s") else {low}),
            "era_variants": ERA_VARIANTS.get(low, []),
        })
    return rows


def keywords(cr: str) -> list:
    """CR 702 — keyword abilities. Already bucketed by foundry_keyword_buckets."""
    rows = []
    for m in re.finditer(r"^(702\.(\d+))\. ([A-Z][a-zA-Z' ]+?)\s*$", cr, re.M):
        name = m.group(3).strip()
        if len(name) > 30:
            continue
        rows.append({"term": name.lower(), "cr": m.group(1),
                     "kind": "keyword", "printed_forms": [name.lower()],
                     "era_variants": ERA_VARIANTS.get(name.lower(), [])})
    return rows


def build(cr: str) -> dict:
    rows = keyword_actions(cr) + keywords(cr)
    for term, rule, forms, kind in SCOPE_TERMS:
        rows.append({"term": term, "cr": rule, "kind": kind,
                     "printed_forms": forms,
                     "era_variants": ERA_VARIANTS.get(term, [])})
    # deterministic: sort by kind then term, and de-duplicate on (kind, term)
    seen, out = set(), []
    for r in sorted(rows, key=lambda r: (r["kind"], r["term"])):
        k = (r["kind"], r["term"])
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    return {"schema": "cr-checks/1",
            "source": str(CR_PATH),
            "generated_from_cr_lines": cr.count("\n") + 1,
            "n_terms": len(out),
            "terms": out}


def coverage(reg: dict) -> None:
    """Which CR terms does the codebook model, and which does it not?"""
    cb = fcb.load_codebook()
    tokens = set()
    for slug, e in cb["axes"].items():
        if e.get("status") == "active":
            tokens.update(slug.split(":", 1)[-1].split("-"))
    cards, _ = fc.load_corpus()
    gated = [c for c in cards.values() if fc.gate_passes(c)]

    def card_text(c):
        t = c.get("oracle_text") or ""
        if not t and c.get("card_faces"):
            t = "\n".join(f.get("oracle_text", "") for f in c["card_faces"])
        return t

    missing = []
    for r in reg["terms"]:
        if r["kind"] != "keyword-action":
            continue
        head = r["term"].split()[0]
        if head in tokens:
            continue
        n = sum(1 for c in gated
                if re.search(rf"\b{re.escape(r['term'])}\b", card_text(c), re.I))
        missing.append((n, r["term"], r["cr"]))
    missing.sort(reverse=True)
    n_actions = sum(1 for r in reg["terms"] if r["kind"] == "keyword-action")
    print(f"CR keyword actions        : {n_actions}")
    print(f"  modelled by some axis   : {n_actions - len(missing)}")
    print(f"  NO axis token           : {len(missing)}")
    print("\n  uncovered, by corpus pressure (gate-passing cards printing the term):")
    for n, term, rule in missing:
        if n >= 20:
            print(f"     {n:5d}  {term:28s} CR {rule}")
    print("\n  NOTE: this matches the action's FIRST WORD against slug tokens, so a")
    print("  morphological near-miss counts as uncovered (prevents-regeneration")
    print("  carries 'regeneration', not 'regenerate'). Treat the list as a")
    print("  worklist to verify, not a count to quote.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coverage", action="store_true")
    args = ap.parse_args()
    reg = build(load_cr())

    once = json.dumps(reg, indent=1, sort_keys=True)
    twice = json.dumps(build(load_cr()), indent=1, sort_keys=True)
    if once != twice:
        fc.halt("determinism gate FAILED — two builds of the registry differ")

    OUT.write_text(once + "\n")
    print(f"wrote {OUT}  ({reg['n_terms']} terms, determinism x2 OK)")
    by = {}
    for r in reg["terms"]:
        by[r["kind"]] = by.get(r["kind"], 0) + 1
    for k, v in sorted(by.items()):
        print(f"  {k:16s} {v}")
    if args.coverage:
        print()
        coverage(reg)


if __name__ == "__main__":
    main()
