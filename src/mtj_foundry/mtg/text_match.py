"""Pure regex/text matching over card text — L2, and nothing else.

## What this owns

Exactly two derivations, lifted out of the legacy DET pass:

* `compute_full_hits(pattern_src, texts)` — which cards a compiled pattern
  matches, in a deterministic order;
* `matched_clause(compiled, text_list)` — the clause a pattern matched, which
  is the evidence quote for a rule-derived assertion.

## What this deliberately does NOT own

Everything else in the legacy DET pass. This module knows about a regex and a
list of strings. It knows nothing about DET records, pattern roles, prefilters,
axis slugs, the lattice, the codebook, membership, samples, locality
orchestration, mutation, apply/write behaviour, or a process. Pattern
INTERPRETATION — which source a slug's evidence pattern comes from, the
enters-tapped family's G2 subject split — stays above, with the governance that
owns it.

## Layer law

Imports `re` and nothing else. No repository path, no root derivation, no
import-time file read, no `experiments`, no process exit. Installed anywhere,
it behaves the same, because its only inputs are its arguments.
"""

from __future__ import annotations

import re

__all__ = ["compute_full_hits", "matched_clause"]


def compute_full_hits(pattern_src: str, texts: dict) -> list:
    pat = re.compile(pattern_src, re.I)
    return sorted(oid for oid, text_list in texts.items() if any(pat.search(t) for t in text_list))


def matched_clause(compiled, text_list: list):
    """The oracle-text clause a ratified pattern matched on this card -- the
    evidence quote for a rule-derived assertion (R2). Returns None when the
    pattern matches none of the card's DET scan texts, which for a card on
    that pattern's own hit list means the hit list and the pattern have
    drifted apart; every caller treats that as a halt, never a skip."""
    for text in text_list:
        m = compiled.search(text)
        if m and m.group(0).strip():
            return m.group(0)
    return None
