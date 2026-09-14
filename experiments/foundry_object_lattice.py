#!/usr/bin/env python3
"""The `targeted-<action>-<class>` OBJECT LATTICE — class extraction, derived.

THE LAW THIS IMPLEMENTS IS ALREADY RATIFIED, AND WAS NEVER IMPLEMENTED.
`docs/MASTER-HANDOFF-ADDENDUM-4.md` §4, the ratified rulings registry:

    | M8 generalized (b6 D3) | Multi-class targeted-<action> cards get every
    | applicable per-class tag, all action verbs, NEVER COMBO TAGS;
    | removal-for-breadth is wrong. |

restated in `docs/CODEBOOK-NAMING-GRAMMAR.md` §5:

    Per-object-class siblings are the law for every `targeted-<action>` family
    (M8 generalized, b6 D3): OR-shaped multi-class targets get every applicable
    class tag; the class lattice (`targeted-bounce-<class>`,
    `targeted-destruction-<class>`...) is a ratified grammar with virtual nodes.

Measured 2026-08-09, before this module existed: **zero cards in the codebook
carried two class siblings of one action family.** Putrefy — "Destroy target
artifact or creature. It can't be regenerated." — carried exactly one tag,
`rule:prevents-regeneration`, the rider and not the spell.

WHERE THE VOCABULARY COMES FROM, AND WHY NONE OF IT IS TYPED HERE
-----------------------------------------------------------------
* **CR 701.8a** — *"To destroy a permanent, move it from the battlefield to
  its owner's graveyard."* Only a PERMANENT can be destroyed, so the destroy
  lattice's class slot is the permanent-type list and not the card-type list.
* **CR 110.4** — *"There are six permanent types: artifact, battle, creature,
  enchantment, land, and planeswalker."* Closed, and parsed at run time.
* **CR 205.2a** — the fifteen card types, for actions that reach beyond the
  battlefield (exile, bounce and counter can name an instant or sorcery).
* **`validate_slug.OBJECT_VOCAB`** — the ratified grammar §5 OBJECT slot. Every
  class this module emits is asserted to be in it, so a CR term with no ratified
  slug token halts instead of minting vocabulary.

`_assert_vocabulary_agrees()` runs all three against each other at import. A
hand-list is a defect with a delay; three sources that must agree is the
closest thing to a guard against one of them silently moving.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
* **CR 701.8b** names exactly two routes to destruction: *"an effect that uses
  the word 'destroy'"* or the lethal-damage state-based action (704.5g). This
  module reads the WORD. That is not a heuristic boundary, it is one of the
  CR's own two, and the other route is not a targeted destroy at all.
* **AND-shaped targets are not OR-shaped ones.** CR 300.2 — *"Some objects have
  more than one card type (for example, an artifact creature)"* — so
  "destroy target artifact creature" names ONE object that must be both, while
  "artifact or creature" names either. M8 governs the OR case by name and is
  silent on AND. `classify_clause` reports AND separately (`conjunctive=True`)
  and never fuses it into a union; what tag it earns is unruled and is
  reported, not decided.
* It mints nothing and writes nothing. It is the measurement half.
"""
import functools
import inspect
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
import foundry_common as fc                  # noqa: E402
import foundry_cr as cr                      # noqa: E402
import foundry_cr702_classes as crc          # noqa: E402
import validate_slug as vs                   # noqa: E402

# C8.5J: the standing ratchet now comes from the permanent package. The import
# sits AFTER `foundry_common`, which is what establishes the C8.5A package
# bootstrap -- this module adds no bootstrap and no sys.path mutation of its own.
#
# C8.5R adds the codebook READ beside it, for the same reason and under the same
# constraint. `codebook_store.read` takes an EXPLICIT path, so the path has to
# come from the layout owner -- and it comes from the SAME view bound below.
# Constructing a second view would state the repository root twice and move
# three delegation-census counts while changing nothing.
#
# THIS COMMENT MAY NOT SPELL THE VIEW CONSTRUCTOR OUT. `test_ratchet_capability`
# asserts the bound-view consumers build exactly one view by COUNTING that call
# in the source TEXT, so prose naming it is ingested as a second construction --
# the repository's standing "a document is an API" trap, aimed at a comment.
from mtj_foundry import codebook_store       # noqa: E402
from mtj_foundry.paths import ProjectPaths   # noqa: E402

# S9: the C8.5J standing-ratchet import and the baseline constant it fed both
# left with the guard that called them. Neither is NAMED here on purpose -- a
# guard checks this file textually for the absence of that constant, and prose
# spelling it would score documentation as a live binding. The view itself
# STAYS: this shell still owns the codebook path it hands to
# `codebook_store.read`, so exactly one view is still built here, for exactly
# one path.
PATHS = ProjectPaths.for_root(fc.REPO_ROOT)


# ---------------------------------------------------------------------------
# S7 — THE PURE TARGET-CLASS CAPABILITY NOW LIVES IN THE PERMANENT SUBSTRATE
# ---------------------------------------------------------------------------
# Migration slice 7 moved the category-(1) half of this module into
# `mtj_foundry.mtg.shapes.target_classes`: the CR-derived type vocabulary, the
# target noun-phrase boundaries, `classify_clause`, `clauses_for`,
# `classes_for_card`, and the `measure` / `residual_invariant` /
# `anchor_coverage` measurement surfaces. NO SECOND IMPLEMENTATION REMAINS HERE.
#
# What stayed was everything the permanent MTG layer may not own: `slug_for` and
# the `rule:targeted-*` identity it builds, the ratified-membership floor and
# its assertion, the live codebook read, `validate_slug` governance, the
# baseline metrics, the audit and exclusivity reports, the locality binding, the
# fixtures, the ratchet wiring, the report writer and the CLI.
#
# S9 took the GUARD half of that list out. The grammar fixtures, the seven
# recorded regressions, the per-class anchors, `--gate` and `--fixtures` are now
# owned by `tests/guards/gate2/test_object_lattice.py`, and NO COPY OF THEM
# REMAINS HERE. S13 moved the audit, exclusivity and locality reports, the
# packet composition and the CLI to `mtj_foundry.object_lattice_report`; the
# rest of the list is still this shell's, and those names delegate.
#
# The vocabulary used to be derived AT IMPORT TIME by reading this repository's
# CR. That is exactly what an installed library may not do, so the derivation
# now takes the CR text and the CR 205 type vocabulary as ARGUMENTS and this
# boundary supplies them -- at import, in the same place and the same order.
from mtj_foundry.mtg.shapes import target_classes as _tc  # noqa: E402

# S11: the CODEBOOK half of the lattice -- `rule:targeted-*` identity, the
# ratified membership floor and its verdict, vocabulary agreement and the
# baseline metrics -- is `mtj_foundry.codebook_lattice`'s. The names below keep
# their legacy shapes (no-argument reads of this boundary's CR, corpus and
# ratified pattern file) and delegate; the halt boundary stays here.
from mtj_foundry import codebook_lattice as _lattice  # noqa: E402

LatticeError = _tc.LatticeError

# THE RATIFIED DET PREPROCESSING, INJECTED. `det_scan_texts` is
# `foundry_common`'s today and a later slice's tomorrow; the substrate receives
# it from here rather than importing it.
_tc.use_clause_text_rules(
    _tc.ClauseTextRules(fc, {"det_scan_texts": "det_scan_texts"}))


def _halting(fn):
    """Re-establish the historic `STOP — …` process contract at this boundary.

    A library may not exit a process it does not own, so the permanent module
    raises and this converts.
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (LatticeError, _lattice.LatticeGovernanceError) as exc:
            fc.halt(str(exc))
    return wrapper


# Re-export by REFERENCE, mechanically, so a name cannot be silently dropped on
# its way through the shell. The DERIVED vocabulary is excluded here and bound
# BELOW, after the build, because it does not exist yet at this point.
_NOT_REEXPORTED = {"annotations", "Any", "Callable"}
for _name, _obj in sorted(vars(_tc).items()):
    if _name.startswith("__") or _name in _NOT_REEXPORTED:
        continue
    if _name in _tc.DERIVED_STATE or _name in globals():
        continue
    if inspect.ismodule(_obj):
        continue
    globals()[_name] = _halting(_obj) if inspect.isfunction(_obj) else _obj
del _name, _obj


# ---------------------------------------------------------------------------
# The forms the legacy callers use. The CR LOCATION and the CORPUS are the
# boundary's; the permanent functions take text and cards.
# ---------------------------------------------------------------------------
def permanent_types(path: Path = None) -> set:
    """CR 110.4's six, parsed out of this boundary's CR edition."""
    return _halting(_tc.permanent_types)(cr.text(path) if path else cr.text())


def card_types(path: Path = None) -> set:
    """CR 205.2a's card types, parsed out of this boundary's CR edition."""
    return _halting(_tc.card_types)(cr.text(path) if path else cr.text())


def measure(stem: str, domain: set, cards: dict = None) -> dict:
    if cards is None:
        cards, _, _ = fc.load_corpus_gated()
    return _halting(_tc.measure)(stem, domain, cards)


def residual_invariant(stem: str, domain: set, selftest: bool = False,
                       cards: dict = None) -> dict:
    if cards is None:
        cards, _, _ = fc.load_corpus_gated()
    return _halting(_tc.residual_invariant)(stem, domain, cards,
                                            selftest=selftest)


def anchor_coverage(anchors, cards: dict = None) -> dict:
    # S9: `CLASS_ANCHORS` is a FIXTURE and moved with the guard, so this
    # boundary no longer carries a default that reaches one. The anchors are
    # now supplied by whoever owns them, which is the only caller there is.
    if cards is None:
        cards, _, _ = fc.load_corpus_gated()
    return _halting(_tc.anchor_coverage)(anchors, cards)


def _assert_vocabulary_agrees() -> None:
    """Three sources, asserted against each other, BEFORE the subtype map is built.

    S11: the agreement law is `codebook_lattice.assert_vocabulary_agrees`. This
    boundary supplies its three inputs -- CR 110.4 and CR 205.2a from its CR
    edition, and `validate_slug.OBJECT_VOCAB` -- exactly as it did."""
    perms, cards_ = permanent_types(), card_types()
    _halting(_lattice.assert_vocabulary_agrees)(perms, cards_, vs.OBJECT_VOCAB)


# THE GUARD FIRES IN ITS ORIGINAL ORDER, before the subtype map is built —
# which is why it is called here and not after the derivation below.
_assert_vocabulary_agrees()
_tc.build_vocabulary(cr.text(), crc.type_vocabulary())

# Bound AFTER the build and by value, which is what they always were: the
# derivation runs exactly once, at this module's import, in the same place it
# used to. Nothing rebinds them afterwards, so there is no live-read problem to
# solve here -- unlike the shape substrate, whose state is built by a caller
# long after import.
PERMANENT_TYPES = _tc.PERMANENT_TYPES
CARD_TYPES = _tc.CARD_TYPES
SUBTYPE_TO_TYPE = _tc.SUBTYPE_TO_TYPE
AMBIGUOUS_SUBTYPES = _tc.AMBIGUOUS_SUBTYPES
_CONJUNCTIVE_RE = _tc._CONJUNCTIVE_RE


def slug_for(stem: str, cls: str = None) -> str:
    """`rule:targeted-destroy` / `rule:targeted-destroy-creature`.

    S11 COMPATIBILITY FACADE for `mtj_foundry.codebook_lattice.slug_for`, which
    owns axis identity (and the note on the `-destroy-` spelling)."""
    return _lattice.slug_for(stem, cls)


DET_PATTERNS_PATH = fc.CONFIG_SEMANTIC / "det-patterns-v2.json"


def ratified_total() -> int:
    """The membership total the RATIFIED, TRACKED pattern row asserts.

    S11: the law (and why the local ratchet cannot be the floor) is
    `codebook_lattice.ratified_total`. This boundary reads its tracked pattern
    file and hands the document over."""
    doc = json.loads(DET_PATTERNS_PATH.read_text(encoding="utf-8"))
    return _halting(_lattice.ratified_total)(doc, DET_PATTERNS_PATH.name)


def assert_ratified_total() -> tuple:
    """Live memberships vs the ratified total. A FALL is fatal; a RISE reports.

    Returns `(fatal, notes)`. S11: the verdict is
    `codebook_lattice.ratified_total_verdict`; the live count is measured here,
    over this boundary's gated corpus, exactly as before."""
    want = ratified_total()
    live = sum(measure(stem, PERMANENT_TYPES)["memberships"]
               for stem in sorted(ACTION_VERBS))
    return _lattice.ratified_total_verdict(want, live)


def baseline_metrics() -> dict:
    """Per-class membership counts, residual, and unexplained residual.

    S11: computed by `codebook_lattice.baseline_metrics` over this boundary's
    gated corpus and CR-derived permanent types."""
    cards, _, _ = fc.load_corpus_gated()
    return _halting(_lattice.baseline_metrics)(cards, PERMANENT_TYPES)


# S13: the NC audit, the exclusivity report, the per-quote locality view, the
# ratification-packet composition and the CLI are
# `mtj_foundry.object_lattice_report`'s. This boundary keeps the corpus load,
# the protected codebook read, both writes, the halting semantic wrappers above,
# the lazily-imported locality boundary, and the paths.
from mtj_foundry import object_lattice_report as _report  # noqa: E402


def _loc():
    import foundry_locality as loc
    return loc


def _gated_cards():
    cards, _, _ = fc.load_corpus_gated()
    return cards


def audit(stem: str, domain: set) -> dict:
    """The NC1-NC4 negative controls -- `object_lattice_report.audit`."""
    return _report.audit(stem, domain, _context())


def _locality_of(card: dict, quote: str) -> dict:
    """The semantic owner of one proving quote, through `foundry_locality`."""
    loc = _loc()
    return _report.locality_of(card, quote, loc.resolve, loc.owning_header)


def exclusivity_report(cards: dict) -> list:
    """Cards whose lattice facts come from MUTUALLY EXCLUSIVE modes."""
    return _report.exclusivity_report(cards, _context())


SAMPLE_REPORT_JSON = fc.FOUNDRY_OUT_DIR / "object_lattice_samples.json"
SAMPLE_REPORT_MD = fc.FOUNDRY_OUT_DIR / "object_lattice_samples.md"


def write_report(seed: int, n: int) -> dict:
    """The ratification packet: `det-patterns-v2.json`'s standing condition is a
    fixed-seed per-pattern sample, and ANY row failing its axis definition halts
    the pass before provenance writes. This writes that sheet for every class of
    every action.

    **Quotes go in the FILE, never to console (A14).** The console gets counts.

    S13: the packet's composition is `object_lattice_report.sample_packet`. The
    corpus load, the protected codebook read below and both writes stay here."""
    cards, _, _ = fc.load_corpus_gated()
    cb_axes = None
    try:
        # C8.5R: the permanent read, at the layout owner's explicit path.
        #
        # THE HANDLER IS THE REASON THIS CONSUMER COULD MOVE FIRST, so it is not
        # tidied. `fc.halt` raises `SystemExit`, which `except Exception` does
        # NOT catch; `codebook_store` raises a `RuntimeError`, which it does. So
        # the repoint changes the CLASS of the failure, and whether that is
        # observable depends entirely on the enclosing handler. C8.5Q measured
        # all six seed consumers, and they fall into three groups, not two:
        #
        #   except BaseException  this module                  -> no delta
        #   except Exception      foundry_shape_extractor      -> hard exit becomes
        #                         foundry_system_map              a silent fallback
        #   no handler            foundry_cr_checks            -> exit 1 either way,
        #                         foundry_slug_dossier            but a clean `STOP -- `
        #                         foundry_consolidate_run1        becomes a traceback
        #
        # Only the first row is unobservable, which is why this slice is one file.
        # Here the failure is discarded either way and `cb_axes` stays None, which
        # the `if cb_axes else None` read below is already written for.
        cb_axes = codebook_store.read(PATHS.legacy_codebook_json)["axes"]
    except BaseException:
        pass

    report, md = _report.sample_packet(
        seed, n, cards,
        lambda slug: cb_axes.get(slug, {}).get("status") if cb_axes else None,
        _context())
    fc.write_json(SAMPLE_REPORT_JSON, report)
    SAMPLE_REPORT_MD.write_text(md, encoding="utf-8")
    return {"json": str(SAMPLE_REPORT_JSON), "md": str(SAMPLE_REPORT_MD),
            "actions": {k: v["memberships"] for k, v in report["actions"].items()}}


def _context():
    return _report.ObjectLatticeContext(
        description=__doc__,
        report_help=("write the ratification packet (N rows per class) to "
                     "experiments/out/foundry/object_lattice_samples.{json,md}. "
                     "Quotes go in the FILE, never to console (A14)."),
        generated_by="experiments/foundry_object_lattice.py",
        subtype_source="consumed from foundry_cr702_classes.type_vocabulary()",
        action_verbs=ACTION_VERBS,
        clause_res=_CLAUSE_RES,
        permanent_types=PERMANENT_TYPES,
        card_types=CARD_TYPES,
        permanent_forms=PERMANENT_FORMS,
        load_cards=lambda: _gated_cards(),
        measure=lambda stem, domain: measure(stem, domain),
        residual_invariant=lambda stem, domain, selftest=False:
            residual_invariant(stem, domain, selftest=selftest),
        slug_for=lambda stem, cls=None: slug_for(stem, cls),
        clauses_for=lambda card, stem: clauses_for(card, stem),
        classes_for_card=lambda card, stem, domain: classes_for_card(card, stem, domain),
        full_oracle_text=lambda card: fc.full_oracle_text(card),
        validate_slug=lambda *a, **k: vs.validate_slug(*a, **k),
        resolve=lambda card, quote: _loc().resolve(card, quote),
        owning_header=lambda card, owner: _loc().owning_header(card, owner),
        mutually_exclusive=lambda card, a, b: _loc().mutually_exclusive(card, a, b),
        owner_status=lambda: _loc().OWNER,
        locality_of=lambda card, quote: _locality_of(card, quote),
        exclusivity=lambda cards: exclusivity_report(cards),
        audit=lambda stem, domain: audit(stem, domain),
        write_report=lambda seed, n: write_report(seed, n),
    )


def main() -> int:
    return _report.run(None, _context())


if __name__ == "__main__":
    sys.exit(main())
