"""The CR-derived check registry — L2, GENERATOR ONLY.

## What this owns

`ERA_VARIANTS`, `SCOPE_TERMS`, `load_cr`, `keyword_actions`, `keywords` and
`build` — the derivation that turns the Comprehensive Rules into the pinned
registry `config/generated/cr-checks.json`.

## What it deliberately does NOT own

`coverage()` is NOT here and neither is any codebook import. R4 assigns the
active-axis coverage question to a later `codebook/coverage.py`; a generator in
L2 that read the live codebook would put a codebook dependency underneath the
MTG substrate. The CLI and the output path stay in the legacy operator shell.

## Provenance is repository-relative, and that is a correction

The generated artifact records which CR it came from. It used to record
`str(CR_PATH)` — an ABSOLUTE path, so the same CR built in two worktrees
produced two different tracked files and the recorded provenance was a fact
about a machine rather than about the repository. S6 records the POSIX
repository-relative path instead (Manager reconciliation R-S6-1). Same field,
same schema, same derived rows; only the representation of the path is
corrected, and it is now deterministic and portable.

**A generated artifact is not the CR.** Regenerate this after any CR change, or
a routing diff reads clean against a stale cache.

## Layer law

Imports stdlib and `mtj_foundry.mtg.cr.edition` only. Never `mtg/shapes/**`,
never a codebook module, never `experiments`.
"""

from __future__ import annotations

import re

from mtj_foundry.mtg.cr import edition as _edition

__all__ = ["ERA_VARIANTS", "SCOPE_TERMS", "load_cr", "keyword_actions",
           "keywords", "build"]

CR_PATH = _edition.CR_PATH


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


def load_cr(path=None) -> str:
    # Normalized: `keyword_actions` and `keywords` below anchor on `^701.N. `
    # and `^702.N. `, which the 2026-08-07 edition writes in bold.
    return _edition.text(path or CR_PATH)


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
            "source": _edition.repo_relative_source(),
            "generated_from_cr_lines": cr.count("\n") + 1,
            "n_terms": len(out),
            "terms": out}


