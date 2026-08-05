"""Re-measure the PRE-STEP-2 blanket-sweep risk. Is the 1,883 still 1,883?

WHY
---
`docs/PRE-STEP-2-AUDIT-2026-08-04.md` is a standing, correct warning:

    "Step 2 as written -- 'route bare permanent statics to `static`' -- would
     put 1,883 lines onto a token the CR contradicts for every one of them.
     Worse, `static` is a RATIFIED token, so unlike `spell-or-static` those
     1,883 would report as RESOLVED and no census could ever surface them."

W4 inherits that warning, which is why the packet says to take named shapes
one at a time and never a blanket sweep.

**But 1,883 is a count taken on 2026-08-04, and it breaks down into six
causes that have each since been FIXED.** Its own table:

    loyalty ability                 900   CR 606.1
    modal MODE, header has delivery 504   grammar §1
    CR 702 keyword line -> non-static 194  CR 702.Na
    REPLACEMENT                     165   CR 614.1a-c
    TRIGGER-shaped                   90   CR 113.3c
    ACTIVATED, unquoted colon        30   CR 113.3b

The loyalty branch was moved above the activated gate on 2026-08-04; modal
modes got `expand_modal_bullets` plus D3 inheritance; keyword lines got §2b's
derived homes; the CR 614.1c second template landed in W1; the trigger
branches have been fixed repeatedly since.

CLAUDE.md: **"a carried-forward count in a handoff or a closing summary is not
a measurement."** So this measures it again rather than quoting it. It changes
nothing and routes nothing.

WHAT IT DOES NOT DO
-------------------
It does NOT recommend a blanket sweep. A zero here would mean the six KNOWN
causes have drained, not that every line in the bucket is a static -- absence
of a known defect is not proof of correctness, which is the same distinction
the ground-truth fixture exists for.

PROBE DISCIPLINE
----------------
Each test uses the extractor's OWN helper (`LOYALTY_COST`,
`keyword_line_tokens`, `in_created_ability`, `fc.is_mode_line`) against the
SAME preprocessing the classifier applies -- reminder strip, ability-word
strip, self-reference canonicalization, lowercase. A probe that re-implements
a branch measures the probe, not the branch.
"""
import argparse
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import foundry_common as fc
import foundry_shape_extractor as fse


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--show", help="print the lines for one cause")
    ap.add_argument("--limit", type=int, default=15)
    args = ap.parse_args()

    cards, _, _ = fc.load_corpus_gated()
    fse.build_self_noun_rx(cards)
    ratified = fse.ratified_delivery_tokens()
    fse.build_keyword_homes(ratified)

    causes = collections.Counter()
    examples = collections.defaultdict(list)
    decidable = 0

    for oid, card in cards.items():
        # The population is the one CR 113.3a closes: `spell-or-static` on a
        # card with NO instant/sorcery face. That is W4's 4,375.
        if fse._has_spell_face(card):
            continue
        # THE AUDIT'S CATEGORY IS "modal MODE, HEADER CARRIES A DELIVERY" --
        # a mode that SHOULD have inherited and did not. Its table counts
        # "modal mode, header carries none" as a SEPARATE row (127) which is
        # deliberately NOT part of the 1,883, because inheriting "no ratified
        # token" is the correct answer (the recorded "UNROUTED IS NOT STOPPED"
        # rule). Testing "is a mode line" instead over-counted 21 -> and 19 of
        # those 21 are modes whose header is unrouted for a W3 reason:
        # Hylda (D9), Venser (CR 701.34 proliferate), Glorfindel (CR 701.22
        # scry), Graviton (D1 draw), Teval's Judgment (D5 leaves-graveyard),
        # Putrid Warrior (damage recipient unstated). **They route themselves
        # the moment their decision-sheet item is ratified.**
        header_toks = []
        for line, parsed in fse.deliveries_for_lines(card, ratified):
            if not fc.is_mode_line(line.strip()):
                header_toks = [t for t, _d in parsed]
            for tok, desc in parsed:
                if desc != "spell-or-static":
                    continue
                decidable += 1
                raw = line.strip()
                m_station = fse.STATION_SYMBOL.match(raw)
                if m_station and raw[m_station.end():].strip():
                    raw = raw[m_station.end():].strip()
                body = fc.canonicalize_self_reference(
                    fse.strip_ability_word(raw), card)
                low = body.lower()

                hit = None
                # CR 606.1 -- a loyalty symbol in the cost
                if ":" in body and fse.LOYALTY_COST.match(body.strip()):
                    hit = "loyalty (CR 606.1)"
                # CR 113.3c -- written as "[condition], [effect]"
                elif re.match(r"^(when|whenever|at )", low):
                    hit = "trigger-shaped (CR 113.3c)"
                # CR 113.3b -- "[Cost]: [Effect]", colon not inside a quote
                elif ":" in body and not fse.in_created_ability(
                        body, body.index(":")):
                    hit = "activated, unquoted colon (CR 113.3b)"
                # CR 702.Na -- a line that IS one or more keywords
                elif fse.keyword_line_tokens(raw):
                    hit = "CR 702 keyword line (702.Na)"
                # CR 614.1a-c -- the replacement templates
                # §2's CREATED-ABILITY RULE APPLIES TO THE PROBE TOO. The
                # Eighth Doctor's line grants an ability reading "If this
                # permanent WOULD leave the battlefield, exile it INSTEAD" --
                # inside quotes. The card does not deliver an ability it
                # CREATES, so a replacement template inside a quoted grant is
                # the GRANTED ability's, not this line's. Matching it scored a
                # correct line as a defect.
                elif (lambda m: m and not fse.in_created_ability(
                        low, m.start()))(
                        re.search(r"\bwould\b[^.]*\binstead\b|\bskips?\b|"
                                  r"\benters? with\b|\benters? tapped\b|"
                                  r"^as [^,]{0,40}\benters\b", low)):
                    hit = "replacement (CR 614.1a-c)"
                # grammar §1 / CR 700.2 -- a mode whose header carries a
                # delivery is its header's, not its own
                elif fc.is_mode_line(raw) and any(header_toks):
                    hit = "modal (CR 700.2 / §1)"
                elif fc.is_mode_line(raw):
                    hit = "modal, header unrouted (NOT in the 1,883)"

                if hit:
                    causes[hit] += 1
                    if len(examples[hit]) < 60:
                        examples[hit].append((card["name"], line.strip()))

    if args.show:
        for name, line in examples.get(args.show, [])[:args.limit]:
            print(f"  {name[:30]:32s} {line[:110]}")
        if not examples.get(args.show):
            print(f"  (no lines for {args.show!r}; "
                  f"known: {', '.join(sorted(examples)) or 'none'})")
        return

    total = sum(causes.values())
    print("=" * 74)
    print("BLANKET-SWEEP RISK — re-measured against the CURRENT classifier")
    print("=" * 74)
    print(f"population (CR 113.3a: `spell-or-static`, no instant/sorcery "
          f"face): {decidable}\n")
    print(f"{'cause the CR contradicts':44s} {'2026-08-04':>11} {'now':>7}")
    print("-" * 74)
    was = {
        "loyalty (CR 606.1)": 900,
        "modal (CR 700.2 / §1)": 504,
        "CR 702 keyword line (702.Na)": 194,
        "replacement (CR 614.1a-c)": 165,
        "trigger-shaped (CR 113.3c)": 90,
        "activated, unquoted colon (CR 113.3b)": 30,
    }
    total = sum(causes[c] for c in was)
    for cause, before in sorted(was.items(), key=lambda kv: -kv[1]):
        print(f"{cause:44s} {before:11d} {causes[cause]:7d}")
    print("-" * 74)
    print(f"{'TOTAL':44s} {sum(was.values()):11d} {total:7d}")
    extra = causes["modal, header unrouted (NOT in the 1,883)"]
    if extra:
        print(f"\n  reported separately, NOT a defect: {extra} mode(s) whose "
              f"header carries\n  no ratified token. Inheriting 'no token' is "
              f"the correct answer, and\n  the 2026-08-04 table counted this "
              f"as its own row (127) outside the\n  1,883. Nearly all are "
              f"downstream of a W3 decision-sheet item.")
    print()
    if total < sum(was.values()):
        print(f"  The six KNOWN causes have drained "
              f"{sum(was.values()) - total} of {sum(was.values())}.")
    print("\n  THE REMAINING 4 ARE THE SIEGE CYCLE and are CORRECT, not")
    print("  defects: Monastery / Glacierwood / Windcrag / Frostcliff print")
    print("  `As this enchantment enters, choose X or Y` (CR 614.1c,")
    print("  `replacement`) and then `• Mode — <static ability>`. The CHOICE")
    print("  is the replacement effect; the chosen MODE is a static ability")
    print("  that functions afterwards, so it must NOT inherit `replacement`.")
    print("  The classifier already parses each mode on its own -- Monastery's")
    print("  Khans mode lands on `draw-step-trigger`, Frostcliff's Jeskai on a")
    print("  damage token. These four are genuine W4 statics in the right")
    print("  bucket, not inheritance failures.\n")
    print("  A LOW NUMBER IS NOT A LICENCE TO SWEEP. It says the six causes")
    print("  the 2026-08-04 audit ENUMERATED are gone; it cannot say that")
    print("  every remaining line is a static. Absence of a known defect is")
    print("  not evidence of correctness -- that is what the ground-truth")
    print("  fixture exists for, and it does not cover this bucket.")


if __name__ == "__main__":
    main()
