"""W3 — partition every `unclassified-trigger` line by THE CR RULE THAT DECIDES IT.

WHY THIS EXISTS
---------------
`WORK-PACKETS-2026-08-07.md` scoped W3 as a Batch API job: ship the distinct
shapes plus CR 701/702 to a model and get back
`shape | CR rule | proposed token | justification`. The packet's own sentence
is the reason that is the wrong instrument:

    "This is a CR-LOOKUP JOB, not a judgement job -- which is why it batches."

A CR-lookup job is exactly what a DET tool does, and CLAUDE.md's central rule
is *"NEVER TRANSCRIBE THE CR -- DERIVE FROM IT AT RUN TIME"*, with the
corollary that a hand-list *"is not a shortcut, it is a defect with a delay."*
Paying a model to read an enumeration the CR publishes -- and to hand back an
`llm`-class, never-gate-bearing proposal that must then be reconciled -- is the
old method wearing a batch job's clothes.

So this script answers the same question for free. It does NOT propose
vocabulary and it does NOT judge: it partitions, counts, and cites. Every
class below is keyed to a CR rule, and anything that matches no class is
reported as RESIDUAL rather than forced into the nearest bucket (house style:
halt loudly, never best-guess).

WHAT IT IS NOT
--------------
It mints nothing. Several classes below have NO ratified §2 token, and naming
one is a Captain ratification (`SESSION-START-PROCEDURE.md` Gate 1). The
output is a decision sheet's evidence, not a decision.

PROBE DISCIPLINE
----------------
The clause strings are the ones the CLASSIFIER computed, recovered by wrapping
`parse_delivery` in the extractor's own module -- not re-derived by asking the
question a second time. That is the recorded defect family (ten instances
across three sessions) and it is why attribution here is order-preserving and
why anything unanchored is COUNTED, never dropped.

USAGE
  python3 experiments/foundry_w3_census.py
  python3 experiments/foundry_w3_census.py --residual     # what matched nothing
  python3 experiments/foundry_w3_census.py --class draw   # one class, with cards
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import foundry_common as fc
import foundry_shape_extractor as fse


# ---------------------------------------------------------------------------
# recover the clause the classifier actually tested
# ---------------------------------------------------------------------------
def collect(cards, ratified):
    """Every unrouted trigger row, with the trigger clause that produced it.

    Wraps the extractor's own `parse_delivery` / `trigger_clause` so the clause
    is byte-identical to what the branch chain saw -- same reminder strip, same
    ability-word strip, same self-reference canonicalization, same CR 113.3c
    comma cut. Attribution is per-card and ORDER-PRESERVING: rows come out in
    the order the calls went in, so a line yielding two deliveries cannot hand
    its neighbour's clause to the wrong row.
    """
    last = {"clause": None}
    record = []

    real_tc = fse.trigger_clause
    def tc(low):
        out = real_tc(low)
        last["clause"] = out
        return out

    real_pd = fse.parse_delivery
    def pd(line, rat, card=None):
        last["clause"] = None
        res = real_pd(line, rat, card)
        record.append((last["clause"], res[1]))
        return res

    fse.trigger_clause, fse.parse_delivery = tc, pd
    try:
        rows, unanchored = [], 0
        for oid, card in cards.items():
            record.clear()
            emitted = list(fse.deliveries_for_lines(card, ratified))
            pending = [r for r in record if r[1] == "unclassified-trigger"]
            k = 0
            for line, parsed in emitted:
                for _tok, desc in parsed:
                    if desc != "unclassified-trigger":
                        continue
                    if k < len(pending):
                        clause = pending[k][0]
                        k += 1
                    else:
                        clause = None
                        unanchored += 1
                    rows.append({"oracle_id": oid, "name": card["name"],
                                 "line": line, "clause": clause or ""})
    finally:
        fse.trigger_clause, fse.parse_delivery = real_tc, real_pd
    return rows, unanchored


# ---------------------------------------------------------------------------
# the partition -- one entry per CR rule, in the order tested
# ---------------------------------------------------------------------------
# Each row: (key, CR anchor, one-line note, regex over the TRIGGER CLAUSE).
# Order matters only where two classes could both match; the note says which.
CLASSES = [
    # --- CR rules that are not keyword lists -------------------------------
    #
    # THESE ARE TESTED FIRST, AND THE KEYWORD CLASSES LAST. A specific CR rule
    # beats a keyword-word match, because a keyword name can appear anywhere in
    # a clause while a CR rule names the EVENT. Ordering them the other way
    # round -- which the first run did -- let `craft` claim Market Gnome, whose
    # event is "is exiled from the battlefield" and whose craft mention is a
    # timing qualifier.
    ("draw", "121.1 / 121.2",
     "'draws a card' -- CR 121 defines drawing; the DRAW STEP has a ratified "
     "token (504.1) and §2's own row says the draw EVENT 'is a different "
     "family and is not this token'",
     r"\bdraws?\b(?![^,]*\bstep\b)"),

    # CR 603.8 is a whole CR-published trigger CATEGORY with no §2 token. The
    # "N or more counters on this permanent" shape belongs here and not to the
    # counter family: the trigger is the STATE ("there ARE four or more"), not
    # a placement event -- which is what separates it from §8b's
    # `<type>-counter-placed-trigger` (CR 122.6) and from the proposed
    # `<type>-counter-threshold-trigger`, whose ruling doc is already open.
    ("state-trigger", "603.8",
     "CR 603.8 STATE TRIGGERS -- 'a state trigger triggers whenever the game "
     "state matches the trigger condition'",
     r"\b(?:controls? no|control no|there are no|are no|has no|have no)\b"
     r"|\b(?:have|has|there are|there is)\b[^,]{0,20}?\b\d+ or (?:less|fewer|more)\b"
     r"|\b(?:two|three|four|five|six|seven|eight|nine|ten) or (?:fewer|more)\b"),

    ("life-loss", "119.3",
     "life LOSS. CR 119.3 defines it; §2 ratified `gain-life-trigger` "
     "(119.9) and left the mirror unnamed",
     r"\bloses? life\b|\blost life\b|\blose exactly\b"),

    ("leaves-graveyard", "400.1 / 700.4",
     "a card LEAVES the graveyard. §2 names four to-graveyard tokens and "
     "`leaves-battlefield-trigger`; leaving the graveyard has no token",
     r"\bleaves?\b[^,]{0,40}\bgraveyard\b|\bleave\b[^,]{0,40}\bgraveyard\b"),

    ("exiled-from-battlefield", "400.1 / 700.4",
     "put into EXILE from the battlefield -- an LTB event whose printed zone "
     "is exile, not the graveyard",
     r"\b(?:is|are) (?:put into exile|exiled)\b[^,]{0,30}\bbattlefield\b"
     r"|\bput into exile from the battlefield\b"),

    ("returned-to-hand", "400.1",
     "a permanent is RETURNED TO HAND -- bounce, the zone change §2 never "
     "named; origin often unprinted (the `to-graveyard-zone-unstated` shape)",
     r"\b(?:is|are) returned to\b[^,]{0,30}\bhand\b|\breturned to hand\b"),

    ("ability-activated", "602.1 / 113.3b",
     "triggers when an ABILITY IS ACTIVATED. §2's `activated` token means "
     "'this ability IS activated', a different claim",
     r"\bactivates?\b[^,]{0,60}\bability\b|\bability\b[^,]{0,30}\bis activated\b"),

    ("day-night", "728.1",
     "CR 728 day/night -- 'day becomes night or night becomes day'",
     r"\bday becomes night\b|\bnight becomes day\b|\bbecomes day\b|\bbecomes night\b"),

    ("dice-roll", "706.2 / 706.3",
     "rolling dice as the trigger EVENT (distinct from W2's results-table "
     "rows, which inherit)",
     r"\brolls?\b[^,]{0,40}\b(?:dice|die|d\d+)\b"),

    ("coin-flip", "705.1",
     "CR 705 flipping a coin",
     r"\b(?:win|lose|wins|loses|flips?)\b[^,]{0,20}\bcoin\b|\bcoin flip\b"),

    ("monarch-initiative", "720 / 721",
     "the monarch (CR 720) and the initiative -- named CR mechanics",
     r"\bbecomes? the monarch\b|\bmonarch\b|\binitiative\b"),

    ("ring-tempts", "701.54",
     "'the Ring tempts you' -- CR 701.54 keyword action, listed here because "
     "it is a multi-word term the 701 pass reports separately",
     r"\bring tempts\b"),

    ("counter-placed-active", "122.6 / §8b",
     "counters PUT ON in the active voice ('whenever you put one or more "
     "+1/+1 counters on'). §8b's grammar family is passive-only today",
     r"\bputs?\b[^,]{0,40}\bcounters?\b[^,]{0,20}\bon\b"),

    ("counter-removed", "122.1 / 122.6",
     "a counter is REMOVED -- the mirror of §8b's placement family; "
     "suspend/vanishing time counters are the bulk (CR 702.62, 702.63)",
     r"\bcounters?\b[^,]{0,30}\b(?:is|are) removed\b|\bremoves? a\b[^,]{0,20}\bcounter\b"),

    ("plays-a-card", "601.1a / 305.1",
     "PLAYING a card or a land -- CR 601.1a: 'to play a land ... or to cast "
     "a spell'. Distinct from `cast-trigger` (701.5a), which §2 already has",
     r"\bplays?\b[^,]{0,40}\b(?:a card|a land|cards|lands|a permanent)\b"),

    ("search-shuffle", "701.19 / 701.23",
     "an opponent SEARCHES or SHUFFLES their library",
     r"\bsearch(?:es)?\b|\bshuffles?\b"),

    ("gain-control", "800.4 / 720",
     "a change of CONTROL as the trigger event",
     r"\bgains? control\b|\blose[s]? control\b"),

    # CR 700.10-700.16 is a vein of NAMED MECHANICS that are neither keyword
    # actions nor keywords, so neither closed list reaches them. `commit a
    # crime` was nearly filed as CR-LAG on a failed exact-phrase grep -- the
    # CR states it as the GERUND, "Some cards refer to COMMITTING a crime"
    # (700.13). An inflection miss on a literal search is the same family as
    # every other inflection defect this arc.
    ("named-mechanic-700", "700.10 – 700.16",
     "CR 700.13 committing a crime · 700.14 'Some abilities trigger \"Whenever "
     "you expend N\"' (Bark-Knuckle Boxer is the CR's own example) · 700.11 "
     "descended · 700.12 outlaw",
     r"\bcommits? a crime\b|\bexpends? \d+\b|\bdescended\b"),

    # CR 709.5 / 116.2m -- Rooms are split cards with locked/unlocked halves,
    # and "unlock" is CR vocabulary, not a set-specific coinage.
    ("room-unlock", "709.5 / 116.2m",
     "a Room's door is UNLOCKED. CR 709.5c: 'left half unlocked' and 'right "
     "half unlocked' are designations; 116.2m names the unlock cost",
     r"\bunlocks?\b|\bfully unlock\b"),

    ("monstrosity", "701.37",
     "CR 701.37a: 'Monstrosity N means ... it BECOMES MONSTROUS.' The printed "
     "word differs from the CR term name, which is why the 701 pass misses it",
     r"\bbecomes? monstrous\b|\bmonstrosity\b"),

    ("level-up", "711 / 716",
     "a leveler (CR 711) or Class (CR 716) reaching a level. 711.2a keys on "
     "level COUNTERS; the printed trigger is 'becomes level N'",
     r"\bbecomes? level \d+\b"),

    ("player-loses-game", "603.9 / 104.3",
     "CR 603.9 gives this its own rule: 'Some triggered abilities trigger "
     "SPECIFICALLY WHEN A PLAYER LOSES THE GAME'",
     r"\bloses? the game\b|\bleaves? the game\b"),

    ("phasing", "702.26",
     "CR 702.26 phasing -- 'phases in' / 'phases out'",
     r"\bphases? (?:in|out)\b"),

    ("attach", "701.3 / 701.4",
     "CR 701.3 attach / 701.4 unattach -- 'becomes attached to' / 'becomes "
     "unattached from'",
     r"\bbecomes? (?:un)?attached\b"),

    ("dungeon", "701.49 / 309",
     "CR 701.49 venture into the dungeon; CR 309 Dungeons. 'complete a "
     "dungeon' is the completion event",
     r"\bdungeon\b"),

    # --- the CR publishes a CLOSED LIST and the event is drawn from it -------
    # Tested LAST, deliberately -- see the note at the top of this list.
    ("cr701-keyword-action", "701", "the EVENT is a CR 701 keyword ACTION", None),
    ("cr702-keyword-event", "702", "the EVENT is a CR 702 keyword happening", None),
]


def build_keyword_matchers():
    """CR 701 keyword ACTIONS and CR 702 KEYWORDS, parsed, never listed.

    The membership list for 702 is `CR_KEYWORD_NAMES` (parsed from load_702),
    NEVER `KEYWORD_HOME` -- the recorded trap: the home map SKIPS any keyword
    whose delivery cannot be derived, so `awaken` and `impending` are absent
    from it while still being keywords.

    A term counts only where it reads as the clause's EVENT, so the match
    requires a VERB inflection. Bare noun occurrences are the CDR-09
    homograph failure ("+1/+1 COUNTERS" is not the keyword action `counter`),
    and matching them scored 56 false `counter` hits on the first run.
    """
    actions = fse.cr_action_terms()
    ka = {t: m for t, m in actions.items() if m.get("kind") == "keyword-action"}
    names = fse.CR_KEYWORD_NAMES or set()

    # THE TERM MUST OCCUPY A VERB FRAME, NOT MERELY OCCUR.
    #
    # The first run matched the bare term plus `s|es|ed` and produced exactly
    # the CDR-09 homograph failure this project has already paid for once --
    # sense read off grammatical shape instead of position:
    #     "whenever ENCHANTED player draws a card"   -> claimed by `enchant`
    #     "when this creature has FLYING"            -> claimed by `flying`
    #     "when there are five or more PLOT counters" -> claimed by `plot`
    # All three are the keyword's name in an ADJECTIVE or NOUN slot. The bare
    # `-ed` participle is where it happens, so the bare participle is gone.
    #
    # Four frames, and they are English verb frames rather than a list of
    # keywords, so a keyword ratified next year needs no edit here:
    #   1. FINITE VERB      "this creature MUTATES", "crews a vehicle"
    #   2. becomes <term>ed "becomes CREWED", "becomes RENOWNED" (CR 603.2e's
    #                       own "becomes" construction)
    #   3. activating one   "activate a NINJUTSU ability" (CR 602.1)
    #   4. you <term> a/an  "you FORETELL a card"
    #   5. INTRANSITIVE      "whenever you SCRY", "whenever you EXPEND 4" --
    #                       many CR 701 actions take no object at all, and
    #                       frame 4's object requirement lost 40 lines of them
    #                       (scry 14, surveil 6, proliferate 4, clash, discover,
    #                       forage, collect evidence, investigate)
    # Anything else is reported as RESIDUAL rather than claimed -- a homograph
    # is a sense question and this script does not judge senses.
    def frames(term):
        head = re.escape(term.split()[0])
        rest = re.escape(term[len(term.split()[0]):])
        t = re.escape(term)
        return re.compile(
            r"\b" + head + r"(?:s|es)" + rest + r"\b"          # 1
            r"|\bbecomes? " + t + r"(?:e?d|ned)\b"             # 2
            r"|\bactivat\w+ (?:an?|this \w+'s|the) [\w' ]{0,20}?"
            + t + r"\b"                                        # 3
            r"|\byou " + t + r"\b(?= (?:an?|one|up to|that|it)\b)"  # 4
            r"|\byou " + t + r"\b(?=\s*(?:$|\d|and\b|or\b|for\b|during\b))"  # 5
        )

    # `counter` NEEDS §8a's RATIFIED TEST, NOT A FRAME. Frame 1 reads
    # `counters` as the finite verb -- and §8a says outright why that is
    # wrong: *"plural is itself ambiguous -- `counters` is both the verb stem
    # AND the noun plural."* It is the CDR-09 homograph failure, which this
    # project has already paid for once (17 of 33 counter axes misfiled), and
    # it scored "nine or more INCARNATION COUNTERS", "four or more TIDE
    # COUNTERS" and "two or fewer LOYALTY COUNTERS" as the keyword action.
    #
    # §8a rule 1, verbatim: the VERB sense *"is IMMEDIATELY FOLLOWED by what
    # is countered (`spell`, `ability`, or a restriction word binding to
    # one)"*. Encoding the ratified law beats inventing a new test -- Gate 4.
    ka_rx = {t: frames(t) for t in ka if t != "counter"}
    ka_rx["counter"] = re.compile(
        r"\bcounters?\b(?=\s+(?:that\s+|a\s+|an\s+|the\s+|target\s+|"
        r"one\s+|each\s+)?[\w' -]{0,24}?\b(?:spell|ability|abilities)\b)")
    kw_rx = {n: frames(n) for n in names}
    return ka, ka_rx, kw_rx


def classify(rows, ka, ka_rx, kw_rx):
    out = collections.defaultdict(list)
    detail = collections.defaultdict(collections.Counter)
    for r in rows:
        c = r["clause"]
        hit = None
        for key, _cr, _note, rx in CLASSES:
            if key == "cr701-keyword-action":
                m = sorted(t for t, x in ka_rx.items() if x.search(c))
                if m:
                    hit = key
                    detail[key][m[0]] += 1
                    break
                continue
            if key == "cr702-keyword-event":
                m = sorted(n for n, x in kw_rx.items() if x.search(c))
                if m:
                    hit = key
                    detail[key][m[0]] += 1
                    break
                continue
            if rx and re.search(rx, c):
                hit = key
                break
        out[hit or "RESIDUAL"].append(r)
    return out, detail


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--residual", action="store_true",
                    help="print the clauses that matched no CR class")
    ap.add_argument("--klass", "--class", dest="klass",
                    help="print one class in full, with card names")
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--json")
    args = ap.parse_args()

    cards, _, _ = fc.load_corpus_gated()
    fse.build_self_noun_rx(cards)
    ratified = fse.ratified_delivery_tokens()
    fse.build_keyword_homes(ratified)

    rows, unanchored = collect(cards, ratified)
    if unanchored:
        print(f"  ! {unanchored} row(s) could not be anchored to a clause "
              f"-- reported, not dropped")
    ka, ka_rx, kw_rx = build_keyword_matchers()
    groups, detail = classify(rows, ka, ka_rx, kw_rx)

    notes = {k: (cr, note) for k, cr, note, _ in CLASSES}

    if args.klass:
        rs = groups.get(args.klass)
        if rs is None:
            fc.halt(f"{args.klass!r} is not a class. "
                    f"Known: {', '.join(sorted(groups))}")
        seen = collections.Counter(r["clause"] for r in rs)
        print(f"## {args.klass}   n={len(rs)}   distinct clauses={len(seen)}")
        cr, note = notes.get(args.klass, ("—", ""))
        print(f"   CR {cr} — {note}\n")
        for cl, n in seen.most_common(args.limit):
            ex = next(r["name"] for r in rs if r["clause"] == cl)
            print(f"   {n:4d}  {cl[:82]:84s} {ex[:28]}")
        return

    if args.residual:
        rs = groups.get("RESIDUAL", [])
        seen = collections.Counter(r["clause"] for r in rs)
        print(f"RESIDUAL — matched no CR class: {len(rs)} lines, "
              f"{len(seen)} distinct clauses\n")
        for cl, n in seen.most_common(args.limit * 4):
            ex = next(r["name"] for r in rs if r["clause"] == cl)
            print(f"   {n:4d}  {cl[:82]:84s} {ex[:26]}")
        return

    total = len(rows)
    print("=" * 78)
    print(f"W3 — {total} `unclassified-trigger` lines, partitioned by CR rule")
    print("=" * 78)
    print("Nothing here is vocabulary. Every class is a CR rule with a line")
    print("count; naming a token for any of them is a Captain ratification.\n")
    print(f"{'class':26s} {'CR':>16} {'lines':>6} {'cards':>6}")
    print("-" * 78)
    ordered = sorted(groups.items(), key=lambda kv: -len(kv[1]))
    for key, rs in ordered:
        cr, _note = notes.get(key, ("—", ""))
        n_cards = len({r["oracle_id"] for r in rs})
        print(f"{key:26s} {cr:>16} {len(rs):6d} {n_cards:6d}")
    print("-" * 78)
    covered = total - len(groups.get("RESIDUAL", []))
    print(f"{'CR-CLASSIFIED':26s} {'':>16} {covered:6d} "
          f"{covered / total:5.1%}")

    for key in ("cr701-keyword-action", "cr702-keyword-event"):
        if not detail[key]:
            continue
        print(f"\n--- {key}: which CR term ---")
        for t, n in detail[key].most_common(20):
            cr = ka.get(t, {}).get("cr", "702.Na")
            print(f"   {n:4d}  {t:26s} CR {cr}")

    if args.json:
        Path(args.json).write_text(json.dumps(
            {k: [{"name": r["name"], "clause": r["clause"]} for r in v]
             for k, v in groups.items()}, indent=1), encoding="utf-8")
        print(f"\nwrote {args.json}")


if __name__ == "__main__":
    main()
