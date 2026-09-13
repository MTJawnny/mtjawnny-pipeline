"""DET apply — the pure semantic application of verified DET hits to a codebook.

## What this is

What it MEANS to apply a sample-sheet-verified DET pass to a
`foundry-codebook/2` document, in memory:

1. **the review/apply population must be the same one.** A lattice axis whose
   re-derived hits disagree with the cached hits Captain reviewed may not apply
   (`lattice_cache_disagreement`).
2. **virtual-node instantiation.** Every lattice slug with no axis yet is
   instantiated under grammar sec.11.2, scope inherited from its family parent
   (`instantiate_lattice_axes`).
3. **the A8 assertion operation.** For each resolved pattern the pass drops ONLY
   its own rule-derived assertions and merges the fresh ones back, each carrying
   the clause that proves ITS axis as evidence and, where the resolver finds one
   owner, a semantic address. A member survives exactly as long as some
   assertion still supports it; a human or llm assertion on the same member is
   never touched (`apply_axis_patterns`).

The pre-migration behaviour -- overwrite the whole member list, paste the old
list into a history note -- would now silently delete Captain-ratified
provenance, which is why the operation is assertion-shaped.

## Semantic locality is NOT a gate, and must not become one

An address is optional by ratification, and an unaddressed assertion stays fully
valid card-level evidence. `resolve_owner` is injected and is expected never to
raise; a quote that resolves to SPAN, AMBIGUOUS or UNRESOLVED is written WITHOUT
an address rather than refused.

## What this is NOT

* No file I/O, no hit-cache read, no verdict file, no corpus load, no backup, no
  atomic write, no printing and no process exit. Those are the operator's
  (`foundry_det_pass`, S13) and the store's (`codebook_store`).
* Not the sample-sheet review gate: verdict completeness and PASS/FAIL are human
  review orchestration and stay operator-side.
* It does not choose regexes or read the probe: `quote_pattern_src` and
  `resolve_owner` are injected and called at the moment they are needed.

Refusals raise `DetApplyError` (or a codebook model error from the merge
primitive) carrying the historic halt text verbatim.

## Layer law

Stdlib, `mtj_foundry.codebook` (model), `mtj_foundry.codebook_lattice` and the
S7 `mtj_foundry.mtg.text_match`. Never `experiments`, never the store's write.
"""

from __future__ import annotations

import re
from typing import Callable

from mtj_foundry import codebook as _codebook
from mtj_foundry import codebook_lattice as _lattice
from mtj_foundry.mtg import text_match as _text_match

__all__ = [
    "BATCH_LABEL",
    "DetApplyError",
    "apply_axis_patterns",
    "instantiate_lattice_axes",
    "lattice_cache_disagreement",
]

BATCH_LABEL = "det-pass-1"


class DetApplyError(RuntimeError):
    """A DET application refusal. Raised, never printed, never exited."""


def lattice_cache_disagreement(lattice_quotes: dict, full_hits: dict):
    """The refusal text for the first lattice axis (by slug) whose re-derived
    hits differ from the reviewed cache, or None when every axis agrees.

    The cache holds oracle_ids only, so the lattice is re-derived for its
    quotes; re-deriving also means a lattice whose code changed since review
    cannot silently apply stale hits."""
    for slug, hits in sorted(lattice_quotes.items()):
        cached = set(full_hits.get(slug, []))
        if cached != set(hits):
            return (
                f"lattice axis {slug!r} re-derives {len(hits)} hits but the "
                f"cache from generate-samples holds {len(cached)}. The sample "
                f"sheet Captain ratified was drawn from the cached set, so "
                f"applying the new one would write membership nobody reviewed. "
                f"Re-run generate-samples and re-review.")
    return None


def instantiate_lattice_axes(axes: dict, lattice_quotes: dict,
                             parent_scopes: dict) -> list:
    """Create every missing lattice axis, in slug order. Returns their slugs.

    Virtual-node instantiation, grammar sec.11.2: "virtual nodes instantiate on
    first quote-verified member, no fresh ratification". Captain ratifies the
    GRAMMAR (stem + closed facet slots); the nodes are automatic. This is the
    same route docs/CLUE-INSTANTIATION-2026-08-03.md took for ten axes."""
    instantiated = []
    for slug in sorted(lattice_quotes):
        if slug in axes:
            continue
        axes[slug] = _lattice.lattice_axis_record(slug, parent_scopes)
        axes[slug]["history"] = [{
            "batch": BATCH_LABEL, "action": "created",
            "note": ("virtual node self-instantiated under grammar sec.11.2 on "
                     "its first quote-verified member; object lattice, "
                     "docs/OBJECT-LATTICE-2026-08-09.md, DET pattern_index=45 "
                     "ratified 2026-08-12. Definition generated from stem+class; "
                     "scope inherited from the family parent."),
        }]
        instantiated.append(slug)
    return instantiated


def apply_axis_patterns(axes: dict, axis_patterns: list, full_hits: dict,
                        lattice_quotes: dict, texts: dict, corpus_ref: str, *,
                        quote_pattern_src: Callable[[dict], str],
                        resolve_owner: Callable) -> list:
    """Apply every resolved pattern's hits to `axes`, in pattern order.

    Returns `[(slug, members_before, members_after, members_dropped), ...]`.

    `texts` is `{oracle_id: DET scan texts}` for the Gate #0 corpus; a hit
    outside it is refused. `quote_pattern_src(pattern)` gives the regex whose
    match is the evidence clause for a non-lattice pattern, and
    `resolve_owner(oracle_id, clause)` gives the semantic owner or None.
    """
    applied = []
    for p in axis_patterns:
        slug = p["resolved_slug"]
        e = axes[slug]
        before_n = len(_codebook.member_ids(e))
        removal = _codebook.remove_det_assertions(e)
        source_ref = f"{_codebook.DET_SOURCE_REF_PREFIX}{p['pattern_index']}"
        compiled = None if p.get("is_lattice") else re.compile(
            quote_pattern_src(p), re.I)
        for oid in full_hits[slug]:
            if oid not in texts:
                raise DetApplyError(
                    f"DET hit {slug}/{oid} is not in the Gate #0 corpus — hit list and corpus "
                    f"disagree; nothing written")
            if p.get("is_lattice"):
                # The lattice's own proving clause for THIS class, not a
                # re-scan: a re-scan would hand every class on a multi-class
                # card the same first-matching clause.
                clause = lattice_quotes[slug].get(oid)
            else:
                clause = _text_match.matched_clause(compiled, texts[oid])
            if clause is None:
                raise DetApplyError(
                    f"DET hit {slug}/{oid} produced no matched clause on re-scan — the recorded hit "
                    f"list and the ratified pattern disagree; nothing written")
            _codebook.merge_assertion(e, oid, _codebook.build_assertion(
                "rule-derived", source_ref, clause, corpus_ref, "quoted",
                locality=resolve_owner(oid, clause)))
        e["source"] = "DET"
        after_n = len(_codebook.member_ids(e))
        e["history"] = list(e["history"]) + [{
            "batch": BATCH_LABEL, "action": "det_membership_applied",
            # Counts only. Under /2 an embedded previous member list would
            # inline a wall of member objects into a history note for no audit
            # value the manifest and backups do not already provide.
            "note": (f"Full-corpus DET pass (docs/det-patterns-v2.json pattern_index={p['pattern_index']}, "
                     f"seed={p['seed']}, sample-sheet verified). rule-derived assertions replaced under "
                     f"{source_ref}: {removal['assertions_removed']} removed, {len(full_hits[slug])} "
                     f"merged; {len(removal['members_dropped'])} member(s) dropped for having no "
                     f"remaining assertion; membership {before_n} -> {after_n}."),
        }]
        applied.append((slug, before_n, after_n, len(removal["members_dropped"])))
    return applied
