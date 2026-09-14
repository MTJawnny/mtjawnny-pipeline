#!/usr/bin/env python3
"""SEMANTIC LOCALITY — which structured part of a card owns a fact.

RATIFIED 2026-08-13, resolving FL-2.

CANONICAL RULING: `docs/B-MIGRATION-DISCOVERY.md` sec.11 -- tracked, and it
sits with sec.10's A1, the section that defines the assertion object this
amends. Cite THAT for the law.

**AMENDMENTS A1-A4 ARE RESTATED IN FULL AT sec.11.2 OF THAT SAME TRACKED
DOCUMENT, AND THAT IS THE CITATION TO USE.** Every `A1`/`A2`/`A3`/`A4` below
means sec.11.2. This was repointed 2026-08-14: the amendments were previously
cited to the architecture-review packet, which is UNTRACKED, so on a fresh
clone a Gate 2 module cited a path that does not exist -- the same fail-open
shape as `SESSION-START-PROCEDURE.md` Gate 3b's missing-manifest corollary,
and as a ratified standard with no caller.

Working packets, historical records rather than authority -- and they differ in
whether a fresh clone even has them:
  * `docs/SEMANTIC-ADDRESS-PREIMPLEMENTATION-CHECK-2026-08-13.md` (PASS) --
    TRACKED, committed in 35f77b7. Safe to cite for detail.
  * `docs/SEMANTIC-ADDRESS-ARCHITECTURE-REVIEW-2026-08-13.md` (RATIFY WITH
    AMENDMENTS A1-A4) -- **UNTRACKED**. Do not cite it as authority; its
    binding content is sec.11.2.

THE PROBLEM THIS SOLVES, IN ONE CARD
------------------------------------
Active Volcano prints `Choose one — • Destroy target blue permanent. • Return
target Island to its owner's hand.` The codebook knows the card destroys a
permanent AND bounces a land. Both true. It does not know they are two options
you choose BETWEEN. Measured 2026-08-13: **41 cards** carry two object-lattice
facts proven by mutually exclusive modes.

An assertion already carries the quote that proves it. It never carried WHICH
PART of the card that quote came from. This module derives that.

WHAT AN ADDRESS IS, AND WHAT IT DELIBERATELY IS NOT
---------------------------------------------------
* **Semantic OWNER** — the one structured location that owns the fact.
* **Evidence SPAN** — the wider contiguous range some quotes cover.

They are different, and A2 exists because 39 quoted assertions legitimately
cover a whole modal block. **The span is DERIVED, never stored** (§13 of the
pre-implementation check): it is a pure function of quote + corpus snapshot,
and storing it would duplicate something that can go stale on its own.

**NO MODE IDENTIFIER IS DERIVED (amendment A1).** Measured over the whole
corpus: **1,791 paragraphs hold exactly one modal bullet and ZERO hold two or
more.** Scryfall puts every mode on its own line, so the paragraph coordinate
IS the mode path. A separate mode field would be a second source of truth for
a fact the paragraph index already carries.

**EXCLUSIVITY IS DERIVED, NEVER STORED (amendment A4).** `owning_header()`
walks back to the nearest preceding non-bullet paragraph on the same face:
**1,783 of 1,791 bullets** resolve deterministically. The 8 exceptions are
Celebr-8000's CR 706.3b die-roll table, which the repository already rules is
not modal.

THE RESOLUTION LAW (amendment A3) — RECONCILED, NEVER RACED
------------------------------------------------------------
A quote is resolved against EVERY supported text representation, and the owner
is accepted only when the union of matched COORDINATES holds exactly one
element. This is not first-match-wins and it privileges no producer class.

Why both representations are required, measured 2026-08-13 over 7,891 quoted
assertions: human evidence is verbatim, DET evidence is CARDNAME-canonicalized.

    raw only        98.6%          canonical only  93.7%          either  99.44%

Canonical-only would orphan **423 human assertions**; raw-only orphans 26 DET
ones. And the tie the law never has to break: **Case F — the two
representations resolving to DIFFERENT single units — is 0**, as are the cases
where one narrows the other. The union is safe because the corpus contains no
disagreement, and it returns AMBIGUOUS by construction if one ever appears.

**The union is over COORDINATES, not over strings.** That is what makes a
canonicalization collision safe: `Rahilda, Wanted Cutthroat // Rahilda, Feral
Outlaw` has two faces whose distinct raw text collapses to identical
canonical text, and two paragraphs collapsing to the same STRING still hold
different COORDINATES, so the union has 2 elements and the law returns
AMBIGUOUS rather than silently merging them.

WHAT THIS MODULE DOES NOT DO
----------------------------
* It writes nothing. No assertion is modified; the backfill migration is a
  separate, Captain-authorised codebook mutation under the backup law.
* **Locality does not certify CORRECTNESS.** A perfectly addressed assertion
  can still sit on the wrong axis -- `foundry_definition_drift` C4 measured 93
  such memberships. Where locality analysis finds a membership contradicting
  its axis, it is routed there, never forced into an address.
* No child-effect decomposition, no qualifier vocabulary, no roles.

    python3 experiments/foundry_locality.py --census
    python3 experiments/foundry_locality.py --report

The GATE is no longer here. S9 moved the fixtures, the schema and
write-boundary controls, the ratchet and `--selftest` to their test owner:

    python3 tests/guards/gate2/test_locality.py --gate
"""
import functools
import inspect
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
import foundry_common as fc                    # noqa: E402

# S9: `foundry_codebook`, the C8.5J ratchet import and the `ProjectPaths` view it
# bound left WITH the guard they existed for. The schema and write-boundary
# fixtures were this shell's only `foundry_codebook` callers, and the ratchet
# baseline was read only by the gate. Keeping either here would leave a binding
# with no reader -- the "ratified token with no emitter" shape this repository
# has paid for three times -- so they live at the guard's owner,
# `tests/guards/gate2/test_locality.py`, and nowhere else.


# ---------------------------------------------------------------------------
# S7 — THE RATIFIED ADDRESS LAW NOW LIVES IN THE PERMANENT SUBSTRATE
# ---------------------------------------------------------------------------
# Migration slice 7 moved the six pure definitions into
# `mtj_foundry.mtg.shapes.locality`: the four statuses, `_norm`, `units`,
# `resolve`, `owning_header`, `mutually_exclusive` and `_by_name`. NO SECOND
# IMPLEMENTATION REMAINS HERE.
#
# What stayed was everything the permanent MTG layer may not own: the
# codebook-facing census and binding, the assertion-schema fixtures, the
# boundary-fixture writer, the ratchet directions and their baseline, the
# unaddressed report, and the CLI.
#
# S9 split that list in two rather than leaving it standing. The GUARD half --
# every fixture, the ratchet directions with their baseline read and direction
# assertion, `--gate` and `--selftest` -- is now owned by
# `tests/guards/gate2/test_locality.py`, and NO COPY OF IT REMAINS HERE. What is
# still this shell's is the codebook-facing `census()` and the unaddressed
# reporter with its `--census`/`--report` doors; S13 moved the reporter and
# the CLI to `mtj_foundry.locality_report`, and these names delegate.
#
# The halt boundary is re-established here: the permanent module raises
# `LocalityError`, and the wrappers below convert it to `fc.halt`, preserving
# the historic `STOP — …` process contract for every legacy caller.
from mtj_foundry.mtg.shapes import locality as _locality  # noqa: E402

# S11: the CODEBOOK-FACING binding of that law -- the census and the unaddressed
# walk over live assertions -- is `mtj_foundry.codebook_locality`. It takes the
# resolver as an argument, so the injection above is still the only route to the
# card primitives.
from mtj_foundry import codebook_locality as _binding  # noqa: E402

LocalityError = _locality.LocalityError

# THE CARD-TEXT PRIMITIVES, INJECTED. The shared face reader and the ratified
# CARDNAME collapse are owned by `mtj_foundry.corpus` / (since S10)
# `mtj_foundry.oracle_text`; the `fc` names are call-time facades onto them.
# The substrate receives them from here; it never imports them and never infers
# them.
_locality.use_card_face_rules(_locality.CardFaceRules(fc, {
    "raw_faces": "raw_faces",
    "canonicalize_self_reference": "canonicalize_self_reference",
}))


def _halting(fn):
    """Re-establish the historic `STOP — …` process contract at this boundary.

    A library may not exit a process it does not own, so the permanent module
    raises and this converts.
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except LocalityError as exc:
            fc.halt(str(exc))
    return wrapper


# Re-export by REFERENCE, mechanically, so a name cannot be silently dropped on
# its way through the shell. Doing it BY HAND lost `_BULLET` -- the census and
# the fixtures still read it as a module global, and only the full Gate-2 run
# saw the `NameError`. The address law has no derived state, so every name is
# safe to bind at import; the list is the permanent module's, not a guess.
_NOT_REEXPORTED = {"annotations", "Any", "Callable"}
for _name, _obj in sorted(vars(_locality).items()):
    if _name.startswith("__") or _name in _NOT_REEXPORTED:
        continue
    if _name in globals() or inspect.ismodule(_obj):
        continue
    globals()[_name] = _halting(_obj) if inspect.isfunction(_obj) else _obj
del _name, _obj


def census(cards, codebook_path=None) -> dict:
    """Coverage over every live assertion, with EXACT denominators.

    S11: the binding is `mtj_foundry.codebook_locality.census`. This shell reads
    the codebook (raw JSON, unchanged) and injects ITS OWN `resolve` -- the S7
    law behind this module's halt boundary, looked up when the census runs -- so
    every route the Gate-2 locality controls rig is still the route measured.
    """
    import json
    path = codebook_path or (fc.FOUNDRY_OUT_DIR / "codebook.json")
    cb = json.loads(Path(path).read_text(encoding="utf-8"))
    return _binding.census(cards, cb, resolve)


# --------------------------------------------------------------------------
# STEP 5 — the unaddressed-assertion reporter
#
# `census()` returns COUNTS. What a human needs in order to work the ambiguous
# rows down over time is the LIST, grouped by reason. Written to
# `experiments/out/foundry/` (gitignored: local, never committed), for the same
# reason the object-lattice sample sheet is.
#
# **The remainder is 122, not 83.** The implementation handoff sec.6 enumerates
# "the other 83 (40 ambiguous + 4 unresolved + 39 quoteless)" and omits the
# **39 SPAN** rows, which are equally unaddressed -- `resolve()` returns no
# owner for them, so the backfill skips them exactly as it skips the rest.
# Almost certainly because span and quoteless are BOTH 39 and read as the same
# number twice. The backfill rule itself ("address only where resolve()
# returns OWNER") is unaffected and correct; only the count of its complement
# was wrong. Re-derived here so the reporter can never inherit it.
# --------------------------------------------------------------------------

UNADDRESSED_JSON = fc.FOUNDRY_OUT_DIR / "locality-unaddressed.json"
UNADDRESSED_MD = fc.FOUNDRY_OUT_DIR / "locality-unaddressed.md"

# S13: the reason notes, the sheet renderer, `--report`'s checks, gate and
# summary, `--census`'s lines and the CLI are `mtj_foundry.locality_report`'s.
# This boundary keeps the corpus load, its halting resolver, the codebook reads,
# the output paths, both writers, the provenance string and the historic STOP.
from mtj_foundry import locality_report as _report  # noqa: E402

_REASON_NOTES = _report.REASON_NOTES
_GENERATED_BY = "experiments/foundry_locality.py --report"


def unaddressed_rows(cards, codebook_path=None) -> list:
    """Every live assertion the backfill will NOT address, with its reason.

    S11: the binding is `mtj_foundry.codebook_locality.unaddressed_rows`, fed
    this shell's codebook read and its own `resolve`, exactly as `census`.
    """
    import json
    path = codebook_path or (fc.FOUNDRY_OUT_DIR / "codebook.json")
    cb = json.loads(Path(path).read_text(encoding="utf-8"))
    return _binding.unaddressed_rows(cards, cb, resolve)


def render_unaddressed_md(rows: list, totals: dict) -> str:
    """The human-readable sheet. Pure function of `rows` -- determinism ×2."""
    return _report.render_unaddressed_md(rows, totals, _GENERATED_BY)


def _gated_cards():
    cards, _, _ = fc.load_corpus_gated()
    return cards


def _context():
    return _report.LocalityReportContext(
        description=__doc__,
        report_help=("write the unaddressed-assertion sheet to "
                     "experiments/out/foundry/ (gitignored)"),
        generated_by=_GENERATED_BY,
        load_cards=lambda: _gated_cards(),
        census=lambda cards: census(cards),
        unaddressed_rows=lambda cards: unaddressed_rows(cards),
        json_path=UNADDRESSED_JSON,
        md_path=UNADDRESSED_MD,
        write_json=lambda path, data: fc.write_json(path, data),
        write_text=lambda path, text: path.write_text(text, encoding="utf-8"),
        stop=lambda message: fc.halt(message),
    )


def cmd_report(cards) -> int:
    """Writes the two artifacts, with determinism ×2 byte-identical."""
    return _report.cmd_report(cards, _context())


def main() -> int:
    return _report.run(None, _context())


if __name__ == "__main__":
    sys.exit(main())
