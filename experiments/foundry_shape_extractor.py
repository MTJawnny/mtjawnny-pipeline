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
import re                   # noqa: F401  (used by the operator census below)
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
# and `main`. Those belong to later slices, not to L2.
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
# canonicaliser and the ratified DET preprocessing patterns are shared helpers
# whose permanent home a LATER slice decides. Until then the substrate receives
# them from here -- it never imports them, and it never infers them.
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
    """The CR term registry, read from this boundary's generated artifact."""
    return _halting(_delivery.cr_action_terms)(
        CR_CHECKS if checks_path is None else checks_path)


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
_delivery.build_trigger_verbs(_delivery.cr_action_terms(CR_CHECKS))


def cmd_gaps(args, cards, ratified, actions):
    """Corpus-wide census of delivery shapes that have NO ratified token.

    This is the ratification-throughput lever: it ranks the missing vocabulary
    by how many cards it blocks across the WHOLE corpus, so one vocabulary
    batch can be ruled with the real numbers in hand -- rather than the gaps
    being rediscovered one mechanic at a time, which is what happened to Clues.
    """
    rows = scan(cards, ratified, None)
    gap = collections.Counter()
    cardset = collections.defaultdict(set)
    inside = collections.defaultdict(collections.Counter)
    inside_cards = collections.defaultdict(lambda: collections.defaultdict(set))
    for r in rows:
        if r["delivery"] is not None:
            continue
        if r["descriptor"] not in ("spell-or-static",):
            gap[r["descriptor"]] += 1
            cardset[r["descriptor"]].add(r["name"])
        else:
            # THE CENSUS WAS BLIND HERE BY CONSTRUCTION, and this is where
            # almost all of the unrouted mass lives: 14,898 of 15,902 lines,
            # 93.7%. The exclusion is right -- these are not missing
            # VOCABULARY, which is what the table above ranks -- but "excluded
            # from this table" turned into "unreportable", and 236 CR 614.1c
            # replacement effects hid in here indefinitely.
            #
            # CR 113.3a decides the split and needs no new vocabulary to do it:
            # *"a spell ability ... is an ability that functions only while the
            # spell is on the stack"*, and a spell is an instant or a sorcery.
            # So a card with NO instant/sorcery face leaves CR 113.3's
            # four-category enumeration closed on `static` -- the line is
            # decidably a static ability that simply has no branch yet. A card
            # WITH such a face is genuinely undecidable from its faces alone,
            # and grammar §1 makes the unmarked default correct for it anyway.
            key = ("CR 113.3a closes: decidably STATIC"
                   if not _has_spell_face(cards[r["oracle_id"]])
                   else "undecidable — has an instant/sorcery face (§1 default)")
            shape = " ".join(re.sub(r"[^\w\s'’—•|+{}/-]", "", r["line"].strip())
                             .split()[:3]).lower()
            inside[key][shape] += 1
            inside_cards[key][shape].add(r["name"])
    print(f"ratified DELIVERY tokens parsed from grammar §2: {len(ratified)}")
    print(f"  {', '.join(sorted(ratified))}\n")
    print(f"ability lines scanned: {len(rows)}   gate-passing cards: {len(cards)}\n")
    print(f"{'unratified delivery shape':38s} {'lines':>7} {'cards':>7}")
    print("-" * 56)
    for desc, n in gap.most_common():
        print(f"{desc:38s} {n:7d} {len(cardset[desc]):7d}")

    total_inside = sum(sum(c.values()) for c in inside.values())
    print(f"\n{'=' * 68}")
    print(f"INSIDE `spell-or-static` — {total_inside} lines the table above CANNOT see")
    print(f"{'=' * 68}")
    print("This bucket is excluded from the census because it is not missing")
    print("VOCABULARY. But excluded became unreportable, and 236 CR 614.1c")
    print("replacement effects once hid here indefinitely. CR 113.3a splits it")
    print("with no new vocabulary at all:\n")
    for key in sorted(inside, key=lambda k: -sum(inside[k].values())):
        n = sum(inside[key].values())
        print(f"  {key:52}{n:>7}  ({n / total_inside:.1%})")
    print("\nSo the headline 'unrouted' number is not a gap count. Most of it is")
    print("grammar §1's UNMARKED DEFAULT for a spell ability, which is correct")
    print("and needs nothing. The decidably-static half is the real queue.\n")
    for key in sorted(inside, key=lambda k: -sum(inside[k].values())):
        print(f"--- {key} — top opening shapes ---")
        print(f"  {'shape':34}{'lines':>7}{'cards':>7}")
        for shape, n in inside[key].most_common(args.limit):
            print(f"  {shape:34}{n:>7}{len(inside_cards[key][shape]):>7}")
        print()
    if args.json:
        Path(args.json).write_text(json.dumps(
            {d: {"lines": n, "cards": sorted(cardset[d])} for d, n in gap.most_common()},
            indent=1), encoding="utf-8")
        print(f"\nwrote {args.json}")


def cmd_action(args, cards, ratified, actions):
    """Every card printing one CR keyword action, grouped by delivery shape."""
    if args.action not in actions:
        near = [t for t in actions if args.action in t]
        fc.halt(f"{args.action!r} is not a CR term in cr-checks.json. "
                f"Did you mean: {', '.join(near[:8]) or '(no near matches)'}")
    meta = actions[args.action]
    rows = scan(cards, ratified, meta["forms"])
    groups = collections.defaultdict(list)
    for r in rows:
        key = r["delivery"] or f"UNRATIFIED:{r['descriptor']}"
        if r["created_ability"] and r["delivery"] is None:
            key = "UNRATIFIED:created-ability(§2)"
        groups[key].append(r)
    cards_hit = {r["oracle_id"] for r in rows}
    print(f"CR {meta['cr']}  {args.action}  ({meta['kind']})")
    print(f"forms: {', '.join(meta['forms'])}")
    print(f"cards: {len(cards_hit)}   ability lines: {len(rows)}\n")
    ready = sum(len(v) for k, v in groups.items() if not k.startswith("UNRATIFIED"))
    print(f"  buildable now (ratified delivery): {ready} lines")
    print(f"  need a ruling:                     {len(rows) - ready} lines\n")
    for key in sorted(groups, key=lambda k: (-len(groups[k]), k)):
        rs = groups[key]
        print(f"## {key}   n={len(rs)}")
        for r in sorted(rs, key=lambda r: r["name"])[:args.limit]:
            print(f"   {r['name'][:36]:38s} {r['line'][:88]}")
        if len(rs) > args.limit:
            print(f"   … and {len(rs) - args.limit} more")
        print()
    if args.json:
        Path(args.json).write_text(json.dumps(rows, indent=1), encoding="utf-8")
        print(f"wrote {args.json}")


def cmd_rank(args, cards, ratified, actions):
    """Rank every CR keyword action by how much of it is buildable today.

    Single corpus pass -- one delivery parse per ability line, matched against
    every action at once. Scanning per-action instead would be 262 full passes.
    """
    covered = codebook_covered_actions()
    # CR 701 is the keyword-ACTION section. 702 keywords (flying, trample) are
    # static/evasion abilities, not actions, and they are the keyword-bucket
    # job -- including them buries the population this ranking is about.
    actions = {t: m for t, m in actions.items() if str(m["cr"]).startswith("701.")}
    stat = collections.defaultdict(lambda: {"cards": set(), "ready": 0, "blocked": 0})
    for oid, card in cards.items():
        for line, line_parsed in deliveries_for_lines(card, ratified):
            parsed = None
            for term, meta in actions.items():
                form, _ = find_action(line, meta["forms"])
                if form is None:
                    continue
                if parsed is None:
                    parsed = line_parsed
                s = stat[term]
                s["cards"].add(oid)
                for tok, _d in parsed:
                    if tok:
                        s["ready"] += 1
                    else:
                        s["blocked"] += 1
    print(f"{'CR action':24s} {'CR':>8} {'cards':>6} {'ready':>6} {'blocked':>7} {'%':>6}  axis?")
    print("-" * 72)
    rows = sorted(stat.items(), key=lambda kv: -len(kv[1]["cards"]))
    for term, s in rows[:args.limit]:
        n = s["ready"] + s["blocked"]
        pct = 100.0 * s["ready"] / n if n else 0.0
        print(f"{term:24s} {actions[term]['cr']:>8} {len(s['cards']):6d} "
              f"{s['ready']:6d} {s['blocked']:7d} {pct:5.1f}%  "
              f"{'yes' if term in covered else 'NO AXIS'}")


def codebook_covered_actions() -> set:
    """Which CR action words already appear in an active axis slug."""
    try:
        import foundry_codebook as fcb
        cb = fcb.load_codebook()
    except Exception:
        return set()
    toks = set()
    for slug, e in cb["axes"].items():
        if e.get("status") == "active":
            toks.update(slug.replace("rule:", "").split("-"))
    return toks


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
