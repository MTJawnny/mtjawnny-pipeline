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
import re
import sys
import json
import argparse
import collections
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
# this module's public surface intact, plus `cmd_homes` -- its operator report --
# and `main`. Both are later-slice work and neither is duplicated anywhere.
#
# THE OLD REVERSE EDGE IS GONE. `mtg/cr/**` names no shapes symbol at all, so the
# `_twin` cross-module-instance state sync that the edge forced has been deleted
# rather than carried: the derived shape state now has exactly one owner.
#
# The `--unstated` KeyError is recorded debt and is deliberately NOT fixed here.
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


def cmd_homes(rows: list, keywords: dict) -> None:
    """Captain, 2026-08-03: 'keywords that are attack triggers should go into
    When this creature attacks rulings. then look at other keywords and find
    them appropriate homes.'

    Right, and it makes the 44-triggered-keyword 'gap' mostly illusory: a
    triggered keyword does not need NEW delivery vocabulary, it needs to be
    routed to the token its own CR templated text already resolves to.

    S7/R6: THE FALLBACK RULE IS NO LONGER DECIDED HERE. It used to exist twice
    -- once in this loop and once inside `build_keyword_homes` -- one rule with
    two implementations, in the two modules on opposite ends of the old cycle.
    `keyword_homes()` is now its single owner and this report CONSUMES it. What
    remains below is composition and printing, which is what an operator command
    is."""
    import foundry_shape_extractor as fse
    import foundry_common as fc
    cards, _, _ = fc.load_corpus_gated()
    fse.build_self_noun_rx(cards)
    ratified = fse.ratified_delivery_tokens()

    recs = fse.keyword_homes(keywords, ratified)

    homed = collections.defaultdict(list)
    unresolved = []
    for r in rows:
        rec = recs[int(r["cr"].split(".")[1])]
        r["home"] = rec["home"]
        r["home_descriptor"] = rec["home_descriptor"]
        r["cr_text"] = rec["cr_text"]
        if rec["home_via"]:
            r["home_via"] = rec["home_via"]
        if rec["home"] is not None:
            homed[rec["home"]].append(r)
        else:
            unresolved.append((r, rec["unresolved_reason"]))

    total = sum(len(v) for v in homed.values())
    print(f"\n{'='*78}\nKEYWORD -> DELIVERY HOME, derived from the CR's own "
          f"templated text\n{'='*78}")
    print(f"routed to an EXISTING ratified token: {total} of {len(rows)} keywords\n")
    for tok in sorted(homed, key=lambda t: -len(homed[t])):
        names = ", ".join(sorted(r["keyword"] for r in homed[tok]))
        print(f"[{tok}]  ({len(homed[tok])})\n  {names}\n")

    print(f"{'='*78}\nNOT ROUTED — {len(unresolved)} keywords. Reported, never "
          f"approximated.\n{'='*78}")
    by_reason = collections.defaultdict(list)
    for r, why in unresolved:
        by_reason[why].append(r["keyword"])
    for why in sorted(by_reason, key=lambda w: -len(by_reason[w])):
        print(f"\n({len(by_reason[why])}) {why}\n  "
              + ", ".join(sorted(by_reason[why])))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--unstated", action="store_true",
                    help="list keywords whose CR text states no ability class")
    ap.add_argument("--homes", action="store_true",
                    help="route each keyword to its §2 DELIVERY token, derived "
                         "from the CR's own templated text")
    ap.add_argument("--json", metavar="PATH")
    args = ap.parse_args()

    keywords = load_702(CR_PATH)
    named = {n: k for n, k in keywords.items()
             if k["name"] and n != PREAMBLE_RULE}

    rows = []
    for num in sorted(named):
        kw = named[num]
        classes, ev = classify(kw)
        effective = effective_classes(kw)
        blob = " ".join(kw["subrules"].values())
        rows.append({"cr": f"702.{num}", "keyword": kw["name"],
                     "cr_classes": classes, "effective_classes": effective,
                     "evidence": ev,
                     "multi": len(effective) > 1,
                     "multi_hint_unresolved": bool(MULTI_HINT.search(blob))
                     and len(effective) <= 1,
                     "delivery": [CLASS_TO_DELIVERY.get(e) for e in effective]})

    def label(r, key):
        v = r[key]
        return "+".join(v) if v else "UNSTATED"

    by_class = collections.Counter(label(r, "cr_classes") for r in rows)
    by_effective = collections.Counter(label(r, "effective_classes")
                                       for r in rows)

    print(f"CR file: {CR_PATH}")
    print(f"CR 702 keywords parsed: {len(rows)}\n")
    print("AS THE CR WORDS IT")
    print(f"{'CR ability class':26s} {'keywords':>9}")
    print("-" * 78)
    for cls, n in by_class.most_common():
        note = ""
        if cls in SUBSUMES:
            note = f"   -> rolls up to {SUBSUMES[cls][0]} ({SUBSUMES[cls][1]})"
        print(f"{cls:26s} {n:9d}{note}")

    print("\nAFTER CR-STATED ROLLUP -- what the §2 DELIVERY slot must be")
    print(f"{'ability class':26s} {'keywords':>9}   {'§2 DELIVERY slot':s}")
    print("-" * 78)
    for cls, n in by_effective.most_common():
        slot = CLASS_TO_DELIVERY.get(cls, "— no §2 slot —")
        print(f"{cls:26s} {n:9d}   {slot}")

    print("\nkeywords by class")
    print("-" * 78)
    grouped = collections.defaultdict(list)
    for r in rows:
        grouped[label(r, "effective_classes")].append(r["keyword"])
    for cls, n in by_effective.most_common():
        names = ", ".join(sorted(grouped[cls]))
        print(f"\n[{cls}]  ({n})\n  {names}")

    unresolved = [r for r in rows if r["multi_hint_unresolved"]]
    if unresolved:
        print("\n" + "=" * 78)
        print("⚠ MULTIPLICITY HINTED BUT NOT RESOLVED -- read these by hand.")
        print("The CR prose says the keyword represents several abilities, but")
        print("only one class sentence parsed. Reported, never assumed.")
        print("=" * 78)
        for r in unresolved:
            print(f"  {r['cr']:9s} {r['keyword']}")

    if args.unstated:
        print("\n" + "=" * 78)
        print("UNSTATED -- the CR does not call these '<X> ability' in 702.Na.")
        print("Reported, NOT assigned to a nearest class.")
        print("=" * 78)
        for r in rows:
            if r["cr_class"] is None:
                first = (r["evidence"] or
                         keywords[int(r['cr'].split('.')[1])]["subrules"].get("a", ""))
                print(f"  {r['cr']:9s} {r['keyword']:28s} {first[:90]}")

    if args.homes:
        cmd_homes(rows, keywords)

    if args.json:
        Path(args.json).write_text(json.dumps(rows, indent=1), encoding="utf-8")
        print(f"\nwrote {args.json}")


if __name__ == "__main__":
    main()
