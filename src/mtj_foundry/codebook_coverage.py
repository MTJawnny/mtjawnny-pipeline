"""Codebook coverage — which CR action words the ACTIVE axes already model.

## What this is

The pure half of the question "does Foundry already own this concept?". It is
codebook ownership by definition -- its answer depends on live axis STATUS -- so
the MTG substrate may not ask it (master plan R4: `cr/checks.py` ships the
generator only, and coverage lands above it).

Two consumers ask it today, and they tokenize the active slugs in two ways that
are NOT the same function:

* `covered_action_tokens` -- `foundry_shape_extractor`'s form:
  `slug.replace("rule:", "").split("-")`, which removes EVERY occurrence of
  `rule:` in the slug;
* `slug_body_tokens` -- `foundry_cr_checks.coverage`'s form:
  `slug.split(":", 1)[-1].split("-")`, which drops everything up to the FIRST
  colon.

They agree on every slug shaped `rule:<body>` with no further colon, which is
every live slug today. They are kept as two definitions on purpose: collapsing
them would be a semantic change riding an ownership move, and the day a slug
carries a second colon they answer differently.

`uncovered_keyword_actions` is the CR-registry comparison: every keyword action
whose FIRST WORD is not an active slug token, with its corpus pressure.

## What this is NOT

* No codebook read, no corpus load, no CR build. The shells supply the axes, the
  registry and the Gate-0-eligible cards, and the read's failure handling stays
  exactly where the accepted C8.5U/C8.5X consumer analysis pins it.
* No report text and no printing (S13).

## Layer law

Stdlib only.
"""

from __future__ import annotations

import re

__all__ = [
    "covered_action_tokens",
    "keyword_action_count",
    "slug_body_tokens",
    "uncovered_keyword_actions",
]


def covered_action_tokens(axes: dict) -> set:
    """Which CR action words already appear in an active axis slug."""
    toks = set()
    for slug, e in axes.items():
        if e.get("status") == "active":
            toks.update(slug.replace("rule:", "").split("-"))
    return toks


def slug_body_tokens(axes: dict) -> set:
    """Every hyphen token of every ACTIVE slug's body (text after the first ':')."""
    tokens = set()
    for slug, e in axes.items():
        if e.get("status") == "active":
            tokens.update(slug.split(":", 1)[-1].split("-"))
    return tokens


def _card_text(c: dict) -> str:
    """The coverage count's own card text: the root field, else faces joined.

    NOT `corpus.full_oracle_text`: a card with root text never reads its faces
    here, and an empty face contributes an empty line. Preserved as measured.
    """
    t = c.get("oracle_text") or ""
    if not t and c.get("card_faces"):
        t = "\n".join(f.get("oracle_text", "") for f in c["card_faces"])
    return t


def keyword_action_count(registry: dict) -> int:
    return sum(1 for r in registry["terms"] if r["kind"] == "keyword-action")


def uncovered_keyword_actions(registry: dict, tokens: set, cards) -> list:
    """`[(n, term, cr), ...]` for keyword actions with no active slug token.

    Sorted descending, exactly as reported. `n` counts the given cards printing
    the whole term (word-bounded, case-insensitive). It matches the action's
    FIRST WORD against slug tokens, so a morphological near-miss counts as
    uncovered -- a worklist to verify, not a count to quote.
    """
    missing = []
    for r in registry["terms"]:
        if r["kind"] != "keyword-action":
            continue
        head = r["term"].split()[0]
        if head in tokens:
            continue
        n = sum(1 for c in cards
                if re.search(rf"\b{re.escape(r['term'])}\b", _card_text(c), re.I))
        missing.append((n, r["term"], r["cr"]))
    missing.sort(reverse=True)
    return missing
