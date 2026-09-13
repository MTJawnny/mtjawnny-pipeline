"""DET resolution — which ratified pattern applies to which ACTIVE axis.

## What this is

S11's permanent owner of the pure mapping from the ratified DET pattern set onto
the codebook's axis STATE. Given the two documents, every ratified record lands
in exactly one of five outcomes, and the five are kept distinct on purpose:

  RESOLVED        axis-bearing, and its slug names an ACTIVE axis
  PRE-FILTER      declared a Lane-1 net by its own slug text
  LATTICE         a grammar-template matcher; deliberately NOT slug-resolved,
                  because its slugs do not exist until instantiation
  DEFERRED GAP    axis-bearing, and its axis exists under a non-active status
  RULED GAP       axis-bearing, axis absent, and a Captain ruling authorises it

Anything ratified, axis-bearing and axis-less that is none of those is a
REFUSAL. It used to fall through to the prefilter list silently, so the pattern
never ran, never wrote membership and never reported; `UnresolvedAxisPatternError`
carries the historic halt text verbatim so the legacy shell's `STOP — …` line is
byte-identical.

## What this is NOT

* No file reads. The legacy shell reads `det-patterns-v2.json` and the codebook
  with a raw `json.loads` -- deliberately not the schema-checking loader, because
  this reads axis STATUS only and must stay correct against `/1` and `/2` alike.
  That read, and the NOTE lines it prints, stay at the shell.
* No process exit, no printing. The gaps are RETURNED; presentation is the
  shell's.
* Not the role predicates: those are `codebook_det_patterns`, consumed here.

## Layer law

Stdlib plus `mtj_foundry.codebook_det_patterns`. Never `experiments`, never the
operator layer, never authority transport.
"""

from __future__ import annotations

from mtj_foundry import codebook_det_patterns as _det_patterns

__all__ = [
    "AxisPatternResolution",
    "DetResolutionError",
    "RULED_AXISLESS_PATTERNS",
    "UnresolvedAxisPatternError",
    "resolve_axis_patterns",
]


# Ratified AXIS-BEARING patterns that legitimately have no axis yet, each
# with the Captain ruling that authorises the gap. Anything ratified,
# axis-bearing and axis-less that is NOT listed here is REFUSED.
#
# EMPTY THIS LIST as session 4 creates each axis — a stale entry here
# re-opens exactly the hole this guard closes.
RULED_AXISLESS_PATTERNS = {
    "rule:cant-be-blocked-by-power":
        "ADD-01 Option A, Captain-ruled 2026-08-01 — DET path, session 4 "
        "(57 corpus hits)",
    "rule:cant-be-blocked-except-by-count":
        "ADD-01 Option A, Captain-ruled 2026-08-01 — DET path, session 4 "
        "(10 corpus hits)",
    "rule:cant-be-blocked-as-long-as-state":
        "ADD-01 Option A, Captain-ruled 2026-08-01 — DET path, session 4 "
        "(18 corpus hits)",
}


class DetResolutionError(RuntimeError):
    """Base for DET-resolution refusals. Raised, never printed, never exited."""


class UnresolvedAxisPatternError(DetResolutionError):
    """A ratified axis-bearing pattern with no axis and no ruling. Carries `slug`."""

    def __init__(self, slug: str, message: str):
        self.slug = slug
        super().__init__(message)


class AxisPatternResolution(tuple):
    """`(axis_patterns, prefilter_patterns, lattice_rows, ruled_gaps, deferred_gaps)`.

    A plain tuple with names, so the legacy three-value unpacking reads the
    first three positions exactly as it always did.
    """

    __slots__ = ()

    def __new__(cls, axis_patterns, prefilter_patterns, lattice_rows,
                ruled_gaps, deferred_gaps):
        return super().__new__(cls, (axis_patterns, prefilter_patterns,
                                     lattice_rows, ruled_gaps, deferred_gaps))

    axis_patterns = property(lambda self: self[0])
    prefilter_patterns = property(lambda self: self[1])
    lattice_rows = property(lambda self: self[2])
    ruled_gaps = property(lambda self: self[3])
    deferred_gaps = property(lambda self: self[4])


def _unresolved_message(slug: str) -> str:
    return (
        f"ratified axis-bearing DET pattern {slug!r} has no axis in "
        f"codebook.json at all.\n"
        f"  It is not marked '(pre-filter)' in det-patterns-v2.json, so it "
        f"is expected to decide an axis's membership.\n"
        f"  Silently demoting it to the prefilter list is what hid three "
        f"ratified patterns for weeks.\n"
        f"  Resolve one of these ways, then re-run:\n"
        f"    - create the axis (the pattern is genuinely axis-bearing), or\n"
        f"    - mark the slug '(pre-filter)' in docs/det-patterns-v2.json "
        f"(it is a Lane-1 net, not a classifier), or\n"
        f"    - add it to RULED_AXISLESS_PATTERNS here WITH the Captain "
        f"ruling that authorises the gap."
    )


def resolve_axis_patterns(det_document: dict, codebook_document: dict,
                          ruled_axisless: dict = None) -> AxisPatternResolution:
    """Partition the RATIFIED records of `det_document` against axis status.

    Records are visited in document order and each list keeps that order; a
    resolved record is a shallow copy carrying `resolved_slug`. `ruled_gaps`
    and `deferred_gaps` are returned UNSORTED, in visit order -- presentation
    order is the caller's. Raises `UnresolvedAxisPatternError` on the FIRST
    record that is none of the five outcomes, before any later record is
    looked at.

    `ruled_axisless` defaults to `RULED_AXISLESS_PATTERNS`, read at call time.
    """
    ruled = RULED_AXISLESS_PATTERNS if ruled_axisless is None else ruled_axisless
    axes = codebook_document["axes"]
    active = {s for s, e in axes.items() if e.get("status") == "active"}
    axis_patterns, prefilter_patterns = [], []
    lattice_rows = []
    ruled_gaps, deferred_gaps = [], []
    for p in det_document["patterns"]:
        if p["status"] != "ratified":
            continue
        if _det_patterns.is_lattice_pattern(p):
            # Deliberately NOT slug-resolved here: its slugs do not exist yet
            # and the axis-less refusal below is correct for every OTHER row.
            lattice_rows.append(p)
            continue
        slug = _det_patterns.pattern_slug(p)

        if _det_patterns.is_prefilter_pattern(p):
            prefilter_patterns.append(p)          # declared a pre-filter
            continue
        if slug in active:
            axis_patterns.append(dict(p, resolved_slug=slug))
            continue

        # Axis-bearing, ratified, and no ACTIVE axis to apply to.
        record = axes.get(slug)
        if record is not None and record.get("status") != "active":
            deferred_gaps.append((slug, record.get("status")))
            prefilter_patterns.append(p)
            continue
        if slug in ruled:
            ruled_gaps.append(slug)
            prefilter_patterns.append(p)
            continue
        raise UnresolvedAxisPatternError(slug, _unresolved_message(slug))

    return AxisPatternResolution(axis_patterns, prefilter_patterns, lattice_rows,
                                 ruled_gaps, deferred_gaps)
