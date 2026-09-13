"""DET-record interpretation — the ONE definition of a ratified pattern's role.

## What this is

S11's canonical owner of what a `det-patterns-v2.json` record *means relative to
the codebook*. A ratified DET record is exactly one of three things:

  AXIS-BEARING  its slug names a codebook axis whose membership it decides. It
                MUST have an active axis to apply to.
  PRE-FILTER    a Lane-1 net that narrows the corpus for a family and is never a
                classifier, e.g. "rule:energy-<family> pre-filter (spends {E})".
  LATTICE       one matcher that yields N concrete axes at match time.

`is_prefilter_pattern`, `is_lattice_pattern` and `pattern_slug` are the SINGLE
definition of that fact. `foundry_det_pass` and `foundry_family_sweep` each once
derived the distinction independently, and that duplication is precisely how
three ratified patterns sat orphaned and unapplied for weeks -- the det pass
silently demoted them to "prefilter" because they had no axis, which is the same
shape as having been declared a prefilter.

The quote-base mapping for the enters-tapped family is here for the same reason:
it is how a DET record's `pattern` field is READ, and the migration writer and
the DET pass both consume it rather than re-deriving it.

## Why this is codebook ownership and not MTG substrate

Every definition below is stated in codebook-axis terms: one tests whether a
record decides axis membership, one tests whether a record's slug can be an axis
at all, one extracts the slug that gets resolved against axis status. A module
holding them is codebook ontology whatever it is called, so it sits ABOVE
`mtj_foundry.mtg` and is never imported by it (master plan R3 §1.1).

## What this is NOT

* Not the orphan law. Resolving a slug against ACTIVE axes is
  `codebook_det_resolution`.
* Not the `pattern_misses_cardname_token` lint. Its input is a regex SOURCE and
  its only consumer is a Gate 2 check; it is guard-only (R3 §1.2) and stays with
  the legacy DET pattern policy until its test owner takes it.
* Not a regex runner and not a corpus reader. The base pattern SOURCE for the
  enters-tapped family lives in the legacy probe, so it is INJECTED.

## Layer law

Stdlib only. No `experiments`, no `sys.path`, no repository root, no file I/O.
"""

from __future__ import annotations

from typing import Callable

__all__ = [
    "ENTERS_TAPPED_BASE_SLUG",
    "ENTERS_TAPPED_COND_SLUG",
    "IMPOSES_SLUG",
    "QUOTE_BASE_SLUG",
    "is_lattice_pattern",
    "is_prefilter_pattern",
    "pattern_slug",
    "quote_pattern_src",
]


def is_prefilter_pattern(pattern: dict) -> bool:
    """True iff this ratified pattern is a deliberate Lane-1 pre-filter.

    The role is carried in the slug text itself."""
    return "pre-filter" in pattern["slug"]


def is_lattice_pattern(pattern: dict) -> bool:
    """True iff this ratified record is a LATTICE matcher -- one matcher that
    yields N concrete axes at match time, rather than one pattern owning one
    axis.

    **ITS SLUG IS A GRAMMAR TEMPLATE, NOT AN AXIS NAME.**
    `rule:targeted-<action>-<class>` carries facet placeholders and can never
    be a concrete codebook axis; the axes it produces are
    `rule:targeted-destroy-creature` and its siblings, instantiated under
    `b6 sec.11.2` (*"virtual nodes instantiate on first quote-verified member,
    no fresh ratification"*). A `pattern` of `null` is the other half of the
    same shape: there is no single regex to run.

    **THIS IS THE ONE DEFINITION.** It was `foundry_det_pass.is_lattice_pattern`
    alone, and `foundry_family_sweep` -- which does not import that module --
    applied the ordinary one-pattern/one-axis orphan law to the lattice record
    and reported a BLOCKING `ratified-pattern-has-no-axis` for a slug that is
    virtual BY DESIGN. That is this repository's most expensive recurring defect
    (*"a hand-maintained MIRROR of a ratified record is trusted as the record"*)
    aimed at the sweep that exists to catch it.

    Deliberately keyed on the RECORD'S SHAPE, never on the literal slug: a
    second lattice family ratified tomorrow is covered without an edit, which
    is the sweep's own self-calibration rule.
    """
    return isinstance(pattern.get("lattice"), dict)


def pattern_slug(pattern: dict) -> str:
    """The bare `rule:` slug, stripped of parenthetical/qualifier text."""
    return pattern["slug"].split(" (")[0].split(" ")[0]


# rule:enters-tapped, rule:enters-tapped-conditional, and rule:imposes-
# enters-tapped are NOT plain-regex patterns -- their det-patterns "pattern"
# field is either the base regex that STILL needs the G2 subject-check applied
# on top (enters-tapped/-conditional), or, for imposes-enters-tapped, a
# DOCUMENTATION STRING ("[same base pattern as ...] + subject classified
# 'imposed'..."), not a compilable regex at all -- compiling it literally yields
# 0 hits, not an error, so the DET pass would have silently written an EMPTY
# membership list for that axis without this special-casing. Caught during
# generate-samples' first run (hits_now=0 vs corpus_hits_at_ratification=24).
ENTERS_TAPPED_BASE_SLUG = "rule:enters-tapped (unconditional)"
ENTERS_TAPPED_COND_SLUG = "rule:enters-tapped-conditional"
IMPOSES_SLUG = "rule:imposes-enters-tapped"


# The pattern whose match IS the evidence clause for an axis. For the three
# enters-tapped-family axes that is NOT the det-patterns-v2 "pattern" field:
# membership there is decided by a G2 subject split on a BASE pattern, so the
# clause has to come from that base pattern. This mapping is the single place
# that fact is written down.
QUOTE_BASE_SLUG = {
    "rule:enters-tapped": ENTERS_TAPPED_BASE_SLUG,
    "rule:enters-tapped-conditional": ENTERS_TAPPED_COND_SLUG,
    "rule:imposes-enters-tapped": ENTERS_TAPPED_BASE_SLUG,
}


def quote_pattern_src(pattern: dict, base_pattern_src: Callable[[str], str]) -> str:
    """The regex source whose match is the evidence clause for a RESOLVED record.

    `base_pattern_src` maps a probe slug key to its base regex source. It is
    injected because the base patterns are owned by the legacy probe; this
    module decides WHICH source proves the axis, never what that source is.
    It is called only when the record needs it, exactly as before.
    """
    slug = pattern["resolved_slug"]
    if slug in QUOTE_BASE_SLUG:
        return base_pattern_src(QUOTE_BASE_SLUG[slug])
    return pattern["pattern"]
