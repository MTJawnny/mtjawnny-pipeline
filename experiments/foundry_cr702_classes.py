#!/usr/bin/env python3
"""DET census of CR 702 keyword abilities by ABILITY CLASS -- zero tokens.

WHY THIS EXISTS
---------------
Captain, 2026-08-03: *"check the CR and how keywords have different
properties. static versus trigger keywords."*

This is load-bearing for the delivery-vocabulary batch. Grammar §2 is explicit
that DELIVERY is determined by ability STRUCTURE, never by effect words -- and
for a keyword ability the structure is not a judgement call, it is stated
verbatim by the CR in the keyword's own `702.Na` sub-rule:

    702.6a  "Equip is an ACTIVATED ability of Equipment cards."
    702.9a  "Flying is an EVASION ability."
    702.108a "Prowess is a TRIGGERED ability."

So the delivery slot of every CR 702 keyword is DERIVABLE, exactly the way
`cycling` was derived (CR 702.29a -> activated -> §2's `activated` token, no
new vocabulary needed). This tool derives all 193 of them at once instead of
one ruling at a time.

WHAT IT DOES NOT DO
-------------------
It judges nothing and writes nothing to the codebook. A keyword whose 702.Na
line does not state a class is reported as UNSTATED and listed by name -- never
assigned to the nearest-looking class. Per house style it halts loudly if the
CR file or the 702 section cannot be read.

THE CLASSES ARE NOT INVENTED
----------------------------
Class words are discovered from the CR's own "X is a ___ ability" sentences,
then validated against CR 113.3a-d -- which is the CR's authoritative
enumeration of the four ability classes, parsed at run time rather than
hand-listed. A discovered word outside it is reported, never assigned: 702.11b's
"a 'hexproof from [quality]' ability is a hexproof ability" is self-reference,
not a class claim. `--unstated` prints the residual so the gap stays visible.

USAGE
  python3 experiments/foundry_cr702_classes.py
  python3 experiments/foundry_cr702_classes.py --unstated
  python3 experiments/foundry_cr702_classes.py --json out.json
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402
import foundry_cr as cr  # noqa: E402

# The CR's LOCATION and its FORMATTING are both owned by `foundry_cr`. This
# module is re-exported as the historical name because five other modules and
# every ruling doc reference `k7.CR_PATH`.

# ---------------------------------------------------------------------------
# S6 — CR PARSING NOW LIVES IN THE PERMANENT SUBSTRATE
# ---------------------------------------------------------------------------
# Migration slice 6 moved the CR-only half of this module into
# `mtj_foundry.mtg.cr.keywords`: the CR 702/205 constants, `load_702`,
# `type_vocabulary`, `classify`, `effective_classes`, and the pure
# `keyword_rows()` derivation lifted out of `main()`'s reporting flow. NO SECOND
# PARSE REMAINS HERE.
#
# S7 then moved `find_home` OUT, into `mtj_foundry.mtg.shapes.delivery`, which
# is where R6 places it: it consumes `parse_delivery`, so the CR half cannot own
# it without being the cycle. What remains below is a thin delegation keeping
# this module's public surface intact, plus `cmd_homes` and `main`, which S13
# reduced to delegates over `mtj_foundry.cr702_report`.
#
# THE OLD REVERSE EDGE IS GONE. `mtg/cr/**` names no shapes symbol at all, so the
# `_twin` cross-module-instance state sync that the edge forced has been deleted
# rather than carried: the derived shape state now has exactly one owner.
#
# The `--unstated` KeyError is recorded debt and is deliberately NOT fixed -- it
# travelled with the operator into `cr702_report`, unrepaired.
#
# The halt boundary is re-established at this shell: the permanent module raises
# `CRKeywordError`, and the wrappers below convert it to `fc.halt`, preserving
# the historic `STOP — …` process contract for every legacy caller.
from mtj_foundry.mtg.cr import keywords as _keywords  # noqa: E402

CRKeywordError = _keywords.CRKeywordError

# The CR's LOCATION and its FORMATTING are both owned by `foundry_cr`. This
# module is re-exported as the historical name because five other modules and
# every ruling doc reference `k7.CR_PATH`.
CR_PATH = cr.CR_PATH

# CR 702/205 vocabulary, constants and derivations -- the permanent owner's.
HEADER = _keywords.HEADER
SUBRULE = _keywords.SUBRULE
TYPE_RULES = _keywords.TYPE_RULES
SUBTYPE_KEYS = _keywords.SUBTYPE_KEYS
CLASS_RULE = _keywords.CLASS_RULE
CLASS_SENT = _keywords.CLASS_SENT
CLASS_TO_DELIVERY = _keywords.CLASS_TO_DELIVERY
SUBSUMES = _keywords.SUBSUMES
NOT_A_CLASS = _keywords.NOT_A_CLASS
PREAMBLE_RULE = _keywords.PREAMBLE_RULE
CR_CLASSES = _keywords.CR_CLASSES
MULTI_HINT = _keywords.MULTI_HINT
MEANS = _keywords.MEANS


def _halting(fn, default_path=False):
    """Wrap a permanent CR entry point in the legacy process boundary.

    `default_path` restores THIS boundary's default edition for callers that
    pass none. The permanent functions have no default on purpose -- they do not
    know where the repository is -- so supplying it is the boundary's job, and
    nine legacy callers depend on the no-argument form.
    """
    def wrapper(*args, **kwargs):
        if default_path and not args and "path" not in kwargs:
            args = (CR_PATH,)
        elif default_path and args and args[0] is None:
            args = (CR_PATH,) + args[1:]
        try:
            return fn(*args, **kwargs)
        except _keywords.CRKeywordError as exc:
            fc.halt(str(exc))
    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    return wrapper


load_702 = _halting(_keywords.load_702, default_path=True)
type_vocabulary = _halting(_keywords.type_vocabulary, default_path=True)
classify = _keywords.classify                 # pure, no halt path
effective_classes = _keywords.effective_classes   # pure, no halt path
def keyword_rows(path=None):
    """Every CR 702 keyword as a pure row, defaulting to this boundary's CR."""
    try:
        return _keywords.keyword_rows(path if path is not None else CR_PATH)
    except _keywords.CRKeywordError as exc:
        fc.halt(str(exc))


def find_home(kw: dict, ratified: dict) -> tuple:
    """(delivery_token, descriptor, cr_templated_text) for one keyword, or
    (None, None, None) when the CR states no templated text to parse.

    §2b, verbatim: *"A keyword's CLASS and its TRIGGER EVENT are separate
    questions. The class says WHICH SLOT; the templated text says which token
    in that slot."* This used to let the templated text decide the slot too,
    and for the `activated` class that was wrong in both directions:

      * DROPPED 6 keywords. CR 702.6a's templated text opens `"[Cost]: Attach
        this permanent…"` -- a literal placeholder where a card prints a real
        cost. `parse_delivery`'s activated branch requires a recognisable cost
        left of the colon ({mana}, sacrifice, discard, tap, …), so `[Cost]`
        matched nothing and Equip fell to `spell-or-static`. Cycling routed
        only because its cost half happens to print the word "Discard".
      * MISROUTED Unearth. CR 702.84a states `activated`, but its templated
        EFFECT says "exile it instead", so the text parsed as `replacement` --
        which §2's created-ability rule already forbids: the delivery belongs
        to the ability that CREATES the replacement effect, not to it.

    So for a keyword the CR states as `activated` and nothing else, the slot is
    CR 113.3b's "[Cost]: [Effect]" outright and the templated text is not
    consulted.

    The other classes are deliberately untouched. A `static` keyword whose
    templated text is a CR 614 replacement still routes to `replacement`,
    because the CR chains the two rather than opposing them -- 113.3d: *"Static
    abilities ... create continuous effects"*; 614.1: *"Some continuous effects
    are replacement effects."* So `replacement` is the MORE SPECIFIC reading of
    a static keyword, not a contradiction of it, and §2b's ratified table
    already routes 16 keywords (Amplify, Bloodthirst, Dredge, Madness, Modular,
    Riot …) exactly that way. Widening this to "the class always wins" would
    have destroyed all 16.

    S7: THE IMPLEMENTATION MOVED, this name did not. The reasoning above is the
    permanent owner's and is not repeated there in a second copy -- read
    `mtj_foundry.mtg.shapes.delivery.find_home`. The delegation goes through the
    shapes BOUNDARY rather than straight at the library because the substrate
    receives its card-text rules and its CR-check registry from that boundary;
    reaching past it would ask a library to locate a repository.
    """
    import foundry_shape_extractor as fse
    return fse.find_home(kw, ratified)


# S13: the row composition, the class report, `--unstated` (with its declared
# `KeyError` debt, unrepaired), the routing report, `--json` and the CLI are
# `mtj_foundry.cr702_report`'s. This shell keeps the CR location, the halting
# loader and the corpus-bound homes computation, and hands them over.
from mtj_foundry import cr702_report as _report  # noqa: E402


def cmd_homes(rows: list, keywords: dict) -> None:
    """Captain, 2026-08-03: 'keywords that are attack triggers should go into
    When this creature attacks rulings. then look at other keywords and find
    them appropriate homes.'

    S13: the corpus load and the keyword-home computation stay at this boundary;
    attaching the homes to the rows and the printed report are
    `cr702_report.homes_lines`'."""
    import foundry_shape_extractor as fse
    import foundry_common as fc
    cards, _, _ = fc.load_corpus_gated()
    fse.build_self_noun_rx(cards)
    ratified = fse.ratified_delivery_tokens()

    recs = fse.keyword_homes(keywords, ratified)
    for line in _report.homes_lines(rows, recs):
        print(line)


def _context():
    return _report.Cr702Context(
        cr_path=CR_PATH,
        load_702=lambda path: load_702(path),
        keyword_rows=lambda path: keyword_rows(path),
        homes=lambda rows, keywords: cmd_homes(rows, keywords),
    )


def main() -> None:
    _report.run(None, _context())


if __name__ == "__main__":
    main()
