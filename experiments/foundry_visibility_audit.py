#!/usr/bin/env python3
"""OPTION VISIBILITY AUDIT — can the system SEE each in-card option's effect?

Captain, 2026-08-06, on the two regressions the modal pass caught: *"are you
saying that these options are now invisible? if so we need to build out
mechanisms to figure this out."*

The honest answer needed a measurement, not an argument. This is that
measurement, and it asks three DIFFERENT questions of every option a card
prints, because an option can be lost at three different layers:

  1. DROPPED    the line produces no delivery row at all
                -> the option left the pipeline

  2. UNSCANNED  the option's own EFFECT TEXT appears in no det_scan_texts()
                variant -> no DET pattern can ever match it

  3. UNCONTEXTED  the effect text is scannable, but never appears JOINED to the
                header that says WHEN it happens -> a proximity pattern
                ("whenever X … create a Treasure") cannot span the newline.
                This is exactly what `expand_modal_bullets` exists to fix, and
                it only fires when the header is recognised, so a header the
                modal test declines silently costs context.

**Layer 3 is the one no other tool in this repo reports.** The routing
regression compares tokens, the gap census counts missing vocabulary, and the
conservation audit proves nothing was deleted -- all three are blind to an
option whose effect is readable but whose TIMING is unreachable.

An option is any of CR 700.2's bulleted modes, CR 700.2i's pawprint modes,
CR 700.2h's cost-prefixed spree modes, CR 706.3b's die-roll result rows, and
the CR 711.2 / 721.2 striations. Each is a piece of card text that sits under
or beside a separator, which is the whole class Captain named.

Exit 1 on any DROPPED or UNSCANNED option. UNCONTEXTED is REPORTED, not fatal:
some of it is correct (a mode of an instant has no timing to inherit).

    python3 experiments/foundry_visibility_audit.py
    python3 experiments/foundry_visibility_audit.py --json out.json --limit 20
"""
import sys
import re
import json
import argparse
import collections
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc            # noqa: E402
import foundry_shape_extractor as fx   # noqa: E402
import foundry_audit_baseline as ab     # noqa: E402


def rule(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


# Every printed SEPARATED form, and the rule that makes it one.
#
# The first five were the whole list, and that covered 5 of the 11 constructs
# `IN-CARD-SEPARATION-CENSUS-2026-08-06.md` measured. The other six had no
# reporter for layers 2 and 3 AT ALL -- including the CR 711.2 leveler, which
# was the construct this arc moved from 100% unrouted to 0%. A mechanism that
# does not cover the thing it was built to protect is the gap, not the fix.
#
# Regexes are REUSED from the extractor wherever it already has one. A probe
# that re-derives the classifier's own pattern is a probe that can disagree
# with it, which is how `{TK}` got read as a CR 721 station symbol.
OPTION_FORMS = [
    ("CR 700.2  bulleted mode",   re.compile(r"^\s*•\s*")),
    ("CR 700.2i pawprint mode",   re.compile(r"^\s*(?:\{P\})+\s*—\s*")),
    ("CR 700.2h spree mode",      re.compile(r"^\s*\+\s*\{[^}]*\}[^—]*—\s*")),
    # all three printed range separators -- see foundry_common._DIE_ROW_RE
    ("CR 706.3b die-roll row",    re.compile(r"^\s*\d+(?:\s*[-–—]\s*\d+)?\s*\|\s*")),
    ("CR 721.2  station striation", fx.STATION_SYMBOL),
    ("CR 714.2  Saga chapter",    fx.CHAPTER),
    ("CR 606.2  loyalty ability", fx.LOYALTY_COST),
]

# The two constructs whose marker is on its OWN line, with the abilities it
# governs printed BELOW it. Everything in OPTION_FORMS carries its effect on
# the same line, so the three questions are asked of `line[m.end():]`; for
# these the effect is the FOLLOWING lines, up to the next marker.
BAND_FORMS = [
    ("CR 711.2  leveler band",    fc._LEVEL_BAND_RE),
    ("CR 716.2  class level bar", fc._CLASS_LEVEL_RE),
]

# `Visit —` (CR 702.159a, 22 lines) is deliberately absent. Attractions are in
# `docs/OUT-OF-SCOPE.md`, a DECLINE register: measured, then declined on
# Captain's deck-building-relevance criterion. Reported as declined, never as
# open, and not re-derived here.


# Forms whose governing CONTEXT is printed on the SAME LINE, so there is
# nothing for a join to add and counting them as UNCONTEXTED is a probe defect.
# CR 721.2's station marker and the abilities it governs share one line
# (`9+ | Flying, first strike`) -- the condition is right there. I reported
# these 49 as needing a join and was wrong; the test is corrected rather than
# the code bent to match it. (Fourth probe defect this session.)
INLINE_CONTEXT = {
    "CR 721.2  station striation",
    # CR 714.2's chapter symbol and its ability share one line ("III — Knights
    # you control get +2/+1"), and CR 606.2's loyalty cost likewise ("+1: Until
    # your next turn…"). The condition is printed right there, so counting
    # these as needing a join would repeat the station mistake exactly.
    "CR 714.2  Saga chapter",
    "CR 606.2  loyalty ability",
}


def option_form(line: str):
    for label, rx in OPTION_FORMS:
        m = rx.match(line)
        if m:
            return label, line[m.end():].strip()
    return None, None


def norm(s: str) -> str:
    """Whitespace-insensitive comparison key. The scan variants are built by
    joining lines with a space, so exact string containment would fail on
    nothing more interesting than a newline."""
    return re.sub(r"\s+", " ", s).strip().lower()


def align(text: str, card: dict) -> str:
    """Put a string into the SAME preprocessing state on both sides of the
    comparison, which is the whole correctness condition of this audit.

    The first run of this file reported **165 options as UNSCANNABLE** and every
    one was this bug. `det_scan_texts()` canonicalizes the card's own name to
    `~`; `ability_lines()` does not. So `• Consuming Sinkhole deals 4 damage …`
    was searched for inside `• ~ deals 4 damage …` and never found — an
    over-report, on exactly the cards that self-reference by name, which are
    disproportionately the legendaries.

    This is the recorded trap — *"a measurement probe must consume the SAME
    preprocessing as the classifier it is measuring"* — and it is the THIRD
    probe defect in this session (after the `non-ASCII` class that re-measured
    the em-dash, and reading `{TK}` as a station symbol). A probe is code and
    gets audited like code.

    Reminder text is stripped from both sides too: `ability_lines` removes it
    (§6a) and `det_scan_texts` does not, so a mode carrying a mid-line
    parenthetical would fail containment for the same spurious reason.

    It must be `strip_reminder`, not a bare `REMINDER.sub`. Removing a mid-line
    parenthetical orphans the space before the following punctuation, and
    `ability_lines` now repairs that; `norm()` collapses whitespace RUNS but
    cannot put back a space the repair deleted, so `you get {E}{E}.` was
    searched for inside `you get {E}{E} .` and one option reported UNSCANNED.
    Fifth probe defect of the same family, and it appeared the moment the two
    pipelines drifted by one space -- which is the argument for the shared
    helper rather than two hand-matched strips.
    """
    return norm(fx.strip_reminder(fc.canonicalize_self_reference(text, card)))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json")
    ap.add_argument("--limit", type=int, default=12)
    ap.add_argument("--update-baseline", action="store_true",
                    help="pin the CURRENT numbers as the baseline, on purpose")
    args = ap.parse_args()

    cards, _, _ = fc.load_corpus_gated()
    fx.build_self_noun_rx(cards)
    ratified = fx.ratified_delivery_tokens()
    fx.build_keyword_homes(ratified)

    dropped, unscanned, uncontexted = [], [], []
    by_form = collections.Counter()
    ctx_ok = collections.Counter()
    ctx_no = collections.Counter()
    inherited = collections.Counter()
    own = collections.Counter()

    for oid, card in cards.items():
        lines = fx.ability_lines(card)
        forms = [option_form(l) for l in lines]
        if not any(f for f, _ in forms):
            continue

        # what the DET layer can see, and what it can see TOGETHER
        scan = [align(t, card) for t in fc.det_scan_texts(card)]
        canon = align(fc.full_oracle_text(card), card)
        joined = [s for s in scan if s != canon]   # the header+option expansions

        delivered = {}
        for line, parsed in fx.deliveries_for_lines(card, ratified):
            delivered.setdefault(line, []).append(parsed)

        for line, (label, effect) in zip(lines, forms):
            if label is None:
                continue
            by_form[label] += 1
            rec = (card["name"], label, line[:88])

            # 1. DROPPED
            parsed = delivered.get(line, [[]])[0]
            if not parsed:
                dropped.append(rec)
                continue
            if any(str(d).startswith("modal-mode:") for _, d in parsed):
                inherited[label] += 1
            else:
                own[label] += 1

            if not effect:
                continue
            key = align(effect, card)

            # 2. UNSCANNED -- the effect text must be findable by a DET pattern
            if not any(key in s for s in scan):
                unscanned.append(rec)
                continue

            # 3. UNCONTEXTED -- is it ever joined to a header?
            if label in INLINE_CONTEXT or any(key in s for s in joined):
                ctx_ok[label] += 1
            else:
                ctx_no[label] += 1
                uncontexted.append(rec)

    # ------------------------------------------------------------- BANDS
    # CR 711.2 / 716.2: the marker is its own line and the abilities it governs
    # are the lines below it, so the effect text is not `line[m.end():]` and the
    # loop above cannot see these at all. Same three questions, one layer out.
    band_forms = collections.Counter()
    band_content = collections.Counter()
    band_unscanned, band_uncontexted = [], []
    for oid, card in cards.items():
        lines = fx.ability_lines(card)
        marks = [next((lbl for lbl, rx in BAND_FORMS if rx.match(l.strip())), None)
                 for l in lines]
        if not any(marks):
            continue
        scan = [align(t, card) for t in fc.det_scan_texts(card)]
        canon = align(fc.full_oracle_text(card), card)
        joined = [s for s in scan if s != canon]
        for i, label in enumerate(marks):
            if label is None:
                continue
            band_forms[label] += 1
            j = i + 1
            while j < len(lines) and not fc._is_band_marker(lines[j]):
                band_content[label] += 1
                key = align(lines[j], card)
                head = align(lines[i], card)
                if not any(key in s for s in scan):
                    band_unscanned.append((card["name"], label, lines[j][:80]))
                elif not any(key in s and head in s for s in joined):
                    band_uncontexted.append((card["name"], label, lines[j][:80]))
                j += 1

    rule("OPTIONS FOUND, by the rule that makes them options")
    for label, n in by_form.most_common():
        print(f"  {label:30}{n:6}   inherited timing {inherited[label]:5}"
              f"   parsed alone {own[label]:5}")

    rule("1. DROPPED — the option produced no delivery row at all")
    print(f"  {len(dropped)}")
    for r in dropped[:args.limit]:
        print(f"     {r[0][:26]:28}{r[2]}")

    rule("2. UNSCANNED — no DET pattern could ever match this effect text")
    print(f"  {len(unscanned)}")
    for r in unscanned[:args.limit]:
        print(f"     {r[0][:26]:28}{r[2]}")

    rule("3. UNCONTEXTED — effect is scannable, but never joined to a header\n"
         "   (a proximity pattern cannot span the newline to reach its timing)")
    print(f"  {len(uncontexted)} of {sum(ctx_ok.values()) + sum(ctx_no.values())}"
          f" options carrying effect text\n")
    print(f"  {'form':32}{'joined':>8}{'NOT joined':>12}")
    for label in by_form:
        print(f"  {label:32}{ctx_ok[label]:>8}{ctx_no[label]:>12}")
    print()
    seen = set()
    for nm, label, line in uncontexted:
        if nm in seen:
            continue
        seen.add(nm)
        if len(seen) > args.limit:
            break
        print(f"     {nm[:26]:28}{line}")

    rule("BANDS — marker on its own line, governed abilities BELOW it\n"
         "   (CR 711.2 / 716.2: 'any abilities printed within the same text\n"
         "    box striation are part of its static ability')")
    print(f"  {'form':32}{'bands':>8}{'content':>9}{'UNSCANNED':>11}{'NOT joined':>12}")
    for label, _rx in BAND_FORMS:
        u = sum(1 for r in band_unscanned if r[1] == label)
        c = sum(1 for r in band_uncontexted if r[1] == label)
        print(f"  {label:32}{band_forms[label]:>8}{band_content[label]:>9}{u:>11}{c:>12}")
    for r in (band_unscanned + band_uncontexted)[:args.limit]:
        print(f"     {r[0][:26]:28}{r[2]}")

    # UNCONTEXTED is non-fatal by design -- some of it is correct, a mode of an
    # instant has no timing to inherit. But it was also UNBOUNDED: nothing
    # noticed it going from 33 to 900. The pinned baseline is what bounds it,
    # without turning a judgement call into a fatal absolute.
    metrics = {
        "options": sum(by_form.values()),
        "dropped": len(dropped),
        "unscanned": len(unscanned),
        "uncontexted": len(uncontexted),
        "by_form": dict(by_form),
        "uncontexted_by_form": {k: ctx_no[k] for k in by_form},
        "band_content": sum(band_content.values()),
        "band_unscanned": len(band_unscanned),
        "band_uncontexted": len(band_uncontexted),
    }
    n_regressions = ab.report("visibility", metrics, args.update_baseline)

    rule("VERDICT")
    invisible = len(dropped) + len(unscanned) + len(band_unscanned)
    fatal = invisible + n_regressions
    if invisible:
        print(f"  ✗ {invisible} option(s) are INVISIBLE — dropped or unscannable.")
    if n_regressions:
        print(f"  ✗ {n_regressions} pinned metric(s) moved the WRONG way.")
    if not fatal:
        print("  ✓ No option is invisible. Every one produces a delivery row and")
        print("    every effect text is reachable by a DET pattern.")
        if uncontexted:
            print(f"\n  ◐ {len(uncontexted)} options are readable but have NO joined")
            print("    header, so a pattern needing timing+effect proximity cannot")
            print("    span them. Reported, not fatal — see §3.")

    if args.json:
        Path(args.json).write_text(json.dumps({
            "by_form": dict(by_form),
            "dropped": [list(r) for r in dropped],
            "unscanned": [list(r) for r in unscanned],
            "uncontexted": [list(r) for r in uncontexted],
        }, indent=2, sort_keys=True))
        print(f"\nwrote {args.json}")
    sys.exit(1 if fatal else 0)


if __name__ == "__main__":
    main()
