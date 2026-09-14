#!/usr/bin/env python3
"""DET ability-shape extractor -- corpus-wide, zero tokens.

WHY THIS EXISTS
---------------
The 2026-08-03 Clue pass burned model tokens deciding things that are not
interpretive. Grammar §6b is explicit about the split:

    SHAPE -- what the card literally does -- printed text, CR terms of art,
             *no ambiguity*                              -> the axis (child)
    JOB   -- what the card is for -- play outcome, deck role,
             *genuine ambiguity*                         -> the parent

Shape is decidable, so it belongs in a script. This is that script. It reads
every gate-passing card, decomposes it into ability lines, and names each
line's DELIVERY slot structurally. It costs nothing to run and it is the same
parse for all 40 uncovered CR keyword actions, not just Clues.

WHAT IT DOES NOT DO
-------------------
It judges nothing and writes nothing to the codebook. It emits candidates for
audit. Per house style it halts loudly rather than guessing, and an ability
whose delivery has no RATIFIED token is reported as `UNRATIFIED:<descriptor>`
-- never approximated onto the nearest ratified one. That approximation is the
exact error the Clue pass had to undo (Fae Offering's "if you've cast" is not a
cast-trigger; §2 forbids it via the b6 Village Ironsmith ruling).

THE VOCABULARY IS NOT HARDCODED
-------------------------------
The ratified DELIVERY tokens are parsed out of §2 of
`docs/CODEBOOK-NAMING-GRAMMAR.md` at run time. If a token is ratified into that
table, this tool picks it up; if one is retired, this tool stops emitting it.
Same principle as `foundry_cr_checks.py` deriving its check set from the CR:
the check set is DERIVED, never discovered after each failure.

USAGE
  python3 experiments/foundry_shape_extractor.py --gaps
  python3 experiments/foundry_shape_extractor.py --action investigate
  python3 experiments/foundry_shape_extractor.py --action goad --json out.json
"""
import sys
import re                   # noqa: F401  (kept: the census moved to mtj_foundry.shape_report)
import json
import argparse
import collections
import inspect
import functools
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402
import foundry_cr as cr  # noqa: E402

# ---------------------------------------------------------------------------
# S7 — THE ABILITY-SHAPE SUBSTRATE NOW LIVES IN THE PERMANENT PACKAGE
# ---------------------------------------------------------------------------
# Migration slice 7 moved the reusable half of this module into
# `mtj_foundry.mtg.shapes.delivery`: the whole stage-1/2/3 shape pipeline, the
# CR enumerations, the keyword machinery, `parse_delivery` and `scan`. NO SECOND
# IMPLEMENTATION REMAINS HERE -- every name below is the permanent owner's,
# re-exported so the nineteen legacy consumers and Gate 2 keep working
# unchanged until their own slices.
#
# What stays is precisely what the permanent MTG layer may not own: the
# repository-owned INPUT LOCATIONS (`GRAMMAR`, `CR_CHECKS`, the CR edition),
# the `fc.halt` process boundary, the operator censuses (`cmd_gaps`,
# `cmd_action`, `cmd_rank`), the live-codebook read `codebook_covered_actions`,
# and `main`. S13 moved the censuses' aggregation and printed text to
# `mtj_foundry.shape_report`; what those names still hold is the boundary.
#
# R6's `find_home` ARRIVED in delivery with this slice, from
# `foundry_cr702_classes`. With it, the cycle that forced the old `_twin`
# cross-module-instance state sync is gone: the derived, order-dependent state
# now has exactly ONE owner and therefore exactly one instance, whatever this
# file is imported as. The `_twin` block is deleted rather than carried.
from mtj_foundry.mtg.shapes import delivery as _delivery  # noqa: E402

# THE REPOSITORY-OWNED INPUTS, AND THEY STAY THE FIRST THREE ASSIGNMENTS IN THIS
# FILE. A committed guard pins that ordering as the module's constant surface,
# so nothing may be inserted above them. The permanent substrate has no default
# for any of them on purpose -- a library that defaults a path has manufactured
# a root. Supplying them is this boundary's job, and nineteen legacy callers
# depend on the no-argument forms restored below.
GRAMMAR = fc.REPO_ROOT / "docs" / "CODEBOOK-NAMING-GRAMMAR.md"
CR_CHECKS = fc.CONFIG_GENERATED / "cr-checks.json"
CR_PATH = cr.CR_PATH

ShapeError = _delivery.ShapeError

# THE CARD-TEXT PRIMITIVES, INJECTED. `full_oracle_text`, the CARDNAME
# canonicaliser and the ratified DET preprocessing patterns are owned since S10
# by `mtj_foundry.corpus` / `mtj_foundry.oracle_text`; the `fc` names below are
# call-time facades onto those owners. The substrate still receives them from
# here -- it never imports them, and it never infers them -- so a run-time
# replacement of either the facade or the owner reaches it.
_delivery.use_card_text_rules(_delivery.CardTextRules(fc, {
    "full_oracle_text": "full_oracle_text",
    "canonicalize_self_reference": "canonicalize_self_reference",
    "is_mode_line": "is_mode_line",
    "modal_header_re": "_MODAL_HEADER_RE",
    "roll_instruction_re": "_ROLL_INSTRUCTION_RE",
    "die_row_re": "_DIE_ROW_RE",
}))


def _halting(fn):
    """Re-establish the historic `STOP — …` process contract at this boundary.

    The permanent module RAISES; a library may not exit a process it does not
    own. Generators are wrapped as generators, or the halt would be deferred
    until the first `next()` and the exception would escape uncaught.
    """
    if inspect.isgeneratorfunction(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                yield from fn(*args, **kwargs)
            except ShapeError as exc:
                fc.halt(str(exc))
        return wrapper

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ShapeError as exc:
            fc.halt(str(exc))
    return wrapper


# Re-export by REFERENCE, mechanically, so a name cannot be silently dropped on
# its way through the shell. `DERIVED_STATE` is deliberately excluded: those
# names are rebound by the substrate's build steps, and a value copied at import
# time would be stale forever -- the second-module hazard, one layer over. They
# are served live by `__getattr__` below instead.
_NOT_REEXPORTED = {"annotations", "Any", "Callable"}
for _name, _obj in sorted(vars(_delivery).items()):
    if _name.startswith("__") or _name in _NOT_REEXPORTED:
        continue
    if _name in _delivery.DERIVED_STATE or _name in globals():
        continue
    if inspect.ismodule(_obj):
        continue
    globals()[_name] = _halting(_obj) if inspect.isfunction(_obj) else _obj
del _name, _obj


def __getattr__(name):
    """Live reads of the substrate's derived, order-dependent state.

    `SELF_NOUN_RX`, `KEYWORD_HOME`, `CR_KEYWORD_NAMES` and the CR enumerations
    are None until their build step runs, and six legacy consumers read them
    through this module AFTER running it. Forwarding the read is what keeps one
    fact in one place.
    """
    if name in _delivery.DERIVED_STATE:
        return getattr(_delivery, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# ---------------------------------------------------------------------------
# The no-argument forms the legacy callers use. The DEFAULT is the boundary's;
# the permanent functions keep none.
# ---------------------------------------------------------------------------
def ratified_delivery_tokens(grammar_path=None):
    """Parse §2's table from this boundary's grammar. {token: CR anchor}."""
    return _halting(_delivery.ratified_delivery_tokens)(
        GRAMMAR if grammar_path is None else grammar_path)


def cr_action_terms(checks_path=None):
    """The CR term registry, read from this boundary's generated artifact.

    THE MISSING-ARTIFACT MESSAGE IS THIS BOUNDARY'S, NOT THE LIBRARY'S, and the
    two are deliberately different sentences. `STOP — … not found — run
    experiments/foundry_cr_checks.py first` names a SCRIPT IN THIS REPOSITORY;
    a library installed into an arbitrary `site-packages` must not tell its
    caller to run a file it cannot know exists, so the permanent module says
    the domain-neutral thing instead. Restoring the historic sentence is what
    this precheck is for, and it is a MESSAGE ADAPTER: it derives nothing, it
    decides nothing the library also decides, and the library keeps its own
    guard for every caller that does not come through here.
    """
    path = CR_CHECKS if checks_path is None else checks_path
    if not path.exists():
        fc.halt(f"{path} not found — run experiments/foundry_cr_checks.py first")
    return _halting(_delivery.cr_action_terms)(path)


def build_cr_enumerations(cr_path=None):
    return _halting(_delivery.build_cr_enumerations)(
        CR_PATH if cr_path is None else cr_path)


def build_self_noun_rx(cards, cr_path=None):
    return _halting(_delivery.build_self_noun_rx)(
        cards, CR_PATH if cr_path is None else cr_path)


def build_keyword_homes(ratified, cr_path=None):
    return _halting(_delivery.build_keyword_homes)(
        ratified, CR_PATH if cr_path is None else cr_path)


def build_landwalk_template(cr_path=None):
    return _halting(_delivery.build_landwalk_template)(
        CR_PATH if cr_path is None else cr_path)


def keyword_homes(keywords=None, ratified=None, cr_path=None):
    """R6's single keyword->home derivation, defaulted to this boundary's CR."""
    if keywords is None:
        keywords = _halting(_delivery._keywords.load_702)(
            CR_PATH if cr_path is None else cr_path)
    return _halting(_delivery.keyword_homes)(keywords, ratified)


# BUILT AT IMPORT TIME, exactly as before. `foundry_cr702_classes` and this
# module used to import each other, so a main()-time build left one copy's
# TRIGGER_VERB as None and the CR 702 keyword pass crashed on it. That cycle is
# gone, but the import-time build is still the CONTRACT every consumer relies on
# -- the original hand-written regex was a module-level constant -- so it stays,
# and it stays HERE, where the artifact's location is known.
#
# S7.R1 — IT GOES THROUGH THE BOUNDARY, AND THE SPELLING IS THE ACCEPTED ONE.
# The first S7 candidate wrote this as
#
#     _delivery.build_trigger_verbs(_delivery.cr_action_terms(CR_CHECKS))
#
# which reaches PAST the adapter defined above into two functions that RAISE.
# A missing CR-check artifact or a lost trigger-vocabulary anchor then escaped
# this module as an uncaught `ShapeError` traceback instead of the historic
# `STOP — …` + exit 1 that every legacy caller and every operator procedure
# depends on. The happy path was identical, which is exactly why no corpus
# differential and no Gate-2 row could see it: a failure boundary is only
# observable on the failure path.
#
# The two names below are THIS module's -- `cr_action_terms` above and the
# `_halting`-wrapped `build_trigger_verbs` from the re-export -- so the line is
# once again byte-for-byte the accepted-S6 spelling, and the process contract
# is owned where the docstring of `_halting` says it is owned.
build_trigger_verbs(cr_action_terms())


# S13: the three censuses' aggregation and every printed line are
# `mtj_foundry.shape_report`'s. This boundary keeps the parse calls behind its
# STOP, the codebook-coverage read and its handler, argument parsing, printing
# and both `--json` writes -- committed guards pin all of those here.
from mtj_foundry import shape_report as _report  # noqa: E402


def cmd_gaps(args, cards, ratified, actions):
    """Corpus-wide census of delivery shapes that have NO ratified token.

    This is the ratification-throughput lever: it ranks the missing vocabulary
    by how many cards it blocks across the WHOLE corpus, so one vocabulary
    batch can be ruled with the real numbers in hand -- rather than the gaps
    being rediscovered one mechanic at a time, which is what happened to Clues.
    """
    rows = scan(cards, ratified, None)
    lines, document = _report.gaps(rows, cards, ratified, args.limit,
                                   lambda card: _has_spell_face(card))
    for line in lines:
        print(line)
    if args.json:
        Path(args.json).write_text(json.dumps(document, indent=1), encoding="utf-8")
        print(f"\nwrote {args.json}")


def cmd_action(args, cards, ratified, actions):
    """Every card printing one CR keyword action, grouped by delivery shape."""
    refusal = _report.unknown_action_message(args.action, actions)
    if refusal:
        fc.halt(refusal)
    meta = actions[args.action]
    rows = scan(cards, ratified, meta["forms"])
    for line in _report.action_lines(args.action, meta, rows, args.limit):
        print(line)
    if args.json:
        Path(args.json).write_text(json.dumps(rows, indent=1), encoding="utf-8")
        print(f"wrote {args.json}")


def cmd_rank(args, cards, ratified, actions):
    """Rank every CR keyword action by how much of it is buildable today."""
    covered = codebook_covered_actions()
    for line in _report.rank_lines(cards, ratified, actions, covered, args.limit,
                                   lambda card, rat: deliveries_for_lines(card, rat),
                                   lambda line, forms: find_action(line, forms)):
        print(line)


def codebook_covered_actions() -> set:
    """Which CR action words already appear in an active axis slug.

    S11: the tokenization is `mtj_foundry.codebook_coverage.covered_action_tokens`.
    The read and its `except Exception` fallback stay HERE, unchanged: the
    accepted consumer analysis pins exactly that handler around exactly that
    read."""
    try:
        import foundry_codebook as fcb
        cb = fcb.load_codebook()
    except Exception:
        return set()
    from mtj_foundry import codebook_coverage as _coverage
    return _coverage.covered_action_tokens(cb["axes"])


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gaps", action="store_true",
                    help="corpus-wide census of delivery shapes with no ratified token")
    ap.add_argument("--action", help="one CR keyword action, grouped by delivery shape")
    ap.add_argument("--rank", action="store_true",
                    help="rank CR actions by how much is buildable today")
    ap.add_argument("--limit", type=int, default=12)
    ap.add_argument("--json")
    args = ap.parse_args()

    cards, _, gated_out = fc.load_corpus_gated()
    build_self_noun_rx(cards)
    ratified = ratified_delivery_tokens()
    actions = cr_action_terms()
    build_keyword_homes(ratified)

    if args.gaps:
        cmd_gaps(args, cards, ratified, actions)
    elif args.action:
        cmd_action(args, cards, ratified, actions)
    elif args.rank:
        cmd_rank(args, cards, ratified, actions)
    else:
        ap.error("pick one of --gaps / --action <term> / --rank")


if __name__ == "__main__":
    main()
