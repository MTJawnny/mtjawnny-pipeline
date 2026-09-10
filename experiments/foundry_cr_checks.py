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
import foundry_cr as fcr  # noqa: E402

# C8.5U: the codebook read comes from the permanent package, at the path the
# layout owner states. The imports sit AFTER `foundry_common`, which is what
# establishes the C8.5A package bootstrap -- this module adds no bootstrap and no
# `sys.path` mutation of its own, and the one insert above is untouched.
#
# THE VIEW IS BUILT FROM THE BOUNDARY ROOT, NOT FROM THIS MODULE'S OWN
# `REPO_ROOT`. The local name is `Path(__file__).resolve().parent`, which is the
# `experiments` DIRECTORY rather than the repository -- `OUT` below compensates
# with `.parent`. Building the view from it yields
# `experiments/experiments/out/foundry/codebook.json`, so the misnaming is a live
# trap and not a cosmetic one.
#
# THIS COMMENT MAY NOT SPELL THE BOUNDARY ROOT EXPRESSION OUT.
# `test_raw_textual_equals_the_scoped_total_and_is_not_ASSUMED_to` reconciles the
# AST census against a LITERAL SUBSTRING count whose docstring says "comments and
# shell commands included", so naming the dotted form in prose is ingested as a
# second delegation and the raw total goes to 24 against a scoped 23. That is the
# repository's standing "a document is an API" trap aimed at a comment, and
# C8.5R's sibling note in `foundry_object_lattice` records the same hazard for
# the view constructor. Written out because it was hit here first, not avoided.
from mtj_foundry import codebook_store       # noqa: E402
from mtj_foundry.paths import ProjectPaths   # noqa: E402

PATHS = ProjectPaths.for_root(fc.REPO_ROOT)
CR_PATH = fcr.CR_PATH        # location and formatting both owned by foundry_cr
OUT = fc.CONFIG_GENERATED / "cr-checks.json"

# Templating-era equivalences. Each entry is one CR object written two ways
# across printing eras; a check that knows only one form manufactures defects.
# Captain-ratified terms only -- this table is law, not convenience.

# ---------------------------------------------------------------------------
# S6 — THE GENERATOR NOW LIVES IN THE PERMANENT CR SUBSTRATE
# ---------------------------------------------------------------------------
# Migration slice 6 moved `ERA_VARIANTS`, `SCOPE_TERMS`, `load_cr`,
# `keyword_actions`, `keywords` and `build` into
# `mtj_foundry.mtg.cr.checks`. NO SECOND GENERATOR REMAINS HERE.
#
# `coverage()` deliberately did NOT move: it reads the live codebook, and a
# generator in the MTG substrate that imported the codebook would put a codebook
# dependency underneath L2. R4 assigns that question to a later
# `codebook/coverage.py`; until then it stays here with `main`.
#
# The tracked artifact's `source` field is now the REPOSITORY-RELATIVE path of
# the CR, not an absolute one (Manager reconciliation R-S6-1). Same schema, same
# 264 derived rows in the same order -- only the provenance representation is
# corrected, so the tracked file stops being machine-specific.
from mtj_foundry.mtg.cr import checks as _checks  # noqa: E402

ERA_VARIANTS = _checks.ERA_VARIANTS
SCOPE_TERMS = _checks.SCOPE_TERMS
keyword_actions = _checks.keyword_actions
keywords = _checks.keywords


def load_cr():
    """The normalized CR at THIS boundary's edition path."""
    return _checks.load_cr(CR_PATH)


def build(cr):
    """The registry, with provenance composed HERE.

    The permanent generator is handed the provenance STRING rather than being
    asked where the repository is: `PATHS.root` is this boundary's, from the
    accepted layout owner. That is what keeps the tracked artifact
    repository-portable without a library inventing a root.
    """
    return _checks.build(cr, _checks_source())


def _checks_source():
    return _edition_module().repo_relative_source(CR_PATH, PATHS.root)


def _edition_module():
    from mtj_foundry.mtg.cr import edition
    return edition


def coverage(reg: dict) -> None:
    """Which CR terms does the codebook model, and which does it not?

    C8.5U: the permanent read, at the layout owner's explicit path. This
    consumer has NO enclosing handler anywhere -- no module imports it -- so
    C8.5S.V's DISCARD_LEGACY_STOP_FORMAT applies cleanly: a missing or
    wrong-schema codebook still ends the process nonzero, and only the stderr
    shape changes from the facade's `STOP -- ` line to the typed error's own
    traceback. Exit status, stdout and `docs/cr-checks.json` are unaffected.

    THE WRITE ORDERING IS THE REASON THAT IS SAFE, and it is not incidental.
    `main()` writes `docs/cr-checks.json` and only then calls this function, and
    only under `--coverage`. So the generated artifact is already complete and
    on disk before this line can fail, and the default invocation never reads
    the codebook at all.
    """
    cb = codebook_store.read(PATHS.legacy_codebook_json)
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
