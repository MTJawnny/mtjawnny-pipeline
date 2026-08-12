#!/usr/bin/env python3
"""TEMPLATED-TEXT REACH CENSUS — how much of the corpus a parser can decide.

WHY THIS EXISTS. `docs/ARCHITECTURE-AUDIT.md` §6.0a rests Option B's entire
ceiling on one number: 66.6% of the corpus is reachable by CR-derived templated
frames, against the object lattice's shipped 6.5%. That number was measured in a
session scratchpad and was therefore, the moment it was written, exactly the
thing this repository calls a carried-forward count. Audit question AQ6 asked
whether it should be committed. This is that commit.

THIS IS A REPORTER, NOT A GATE. Its exit code is 0 whether reach went up or
down. Do not add it to `foundry_gate2.py` and read its exit code as a verdict —
that is precisely the defect `docs/SYSTEM-SELF-TEST-2026-08-09.md` found in
`foundry_definition_drift.py` and `foundry_ruling_registry.py`. If Captain wants
it ratcheted, it emits `--json` for `foundry_audit_baseline.py` to pin, and the
ratchet is what would make it a gate.

THE BOUNDARY, STATED RATHER THAN IMPLIED. A card is TEMPLATE-REACHABLE at frame
T if at least one of its `det_scan_texts()` variants matches T, and every slot
in T is filled from a CLOSED vocabulary the CR publishes and this repository
already parses at run time. No hand-typed word list. No judgment threshold.
That is exactly the standard `foundry_object_lattice.py` met; these frames widen
its SLOTS and change nothing about its standard.

REACH IS NOT MEMBERSHIP. A frame matching is an upper bound on what a parser
could decide, not a claim that it decides it correctly. The lattice read all 39
of its subtype-derived hits by hand and found zero defects; nobody has read a
sample outside destroy/exile/bounce. Treat every number below as a ceiling.

THE FRAMES ARE NESTED, NOT DISJOINT, so `p.assert_disjoint` does not apply and
summing them would be the overlapping-probe defect (`CLAUDE.md`: a probe that
overlaps another probe reports a correlation as a finding). Every number is
reported as INCREMENTAL reach over the union of the frames above it.

FOUR PROBE DEFECTS OCCURRED WRITING THIS, all caught, all kept as comments
below, because the house record is that a probe defect is the default outcome
and the notes are what stop the next one.
"""
import argparse
import collections
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import foundry_probe as p          # noqa: E402
import foundry_common as fc        # noqa: E402
import foundry_shape_extractor as fx   # noqa: E402
import foundry_object_lattice as ol    # noqa: E402

SEED = 20260812


# ---------------------------------------------------------------------------
# frame construction
# ---------------------------------------------------------------------------

def keyword_actions() -> dict:
    """CR 701's keyword actions, parsed, with a CONTENT-bearing halt-guard.

    `cr_action_terms()` reads `docs/cr-checks.json`, which is GENERATED. A
    generated artifact is not the CR: the first post-refresh routing diff read
    a meaningless 0 because this file had not been regenerated. The guard below
    asserts membership, not cardinality, because a count cannot see a
    substitution.
    """
    ka = {t: v for t, v in fx.cr_action_terms().items()
          if v.get("kind") == "keyword-action"}
    if len(ka) < 50:
        fc.halt(f"only {len(ka)} CR 701 keyword actions parsed — refusing to "
                f"run on a truncated vocabulary. Regenerate docs/cr-checks.json "
                f"with experiments/foundry_cr_checks.py.")
    for must in ("destroy", "exile", "sacrifice", "create", "search"):
        if must not in ka:
            fc.halt(f"CR 701 keyword action {must!r} is absent from the parsed "
                    f"vocabulary. A count cannot see a substitution; this can.")
    return ka


def verb_alt(spec: dict) -> str:
    """Printed forms of one keyword action, longest first so `manifest dread`
    is tried before `manifest`."""
    alts = sorted({re.escape(f) for f in spec["forms"] if f},
                  key=len, reverse=True)
    return r"(?:" + "|".join(alts) + r")(?:es|s)?"


def build_frames(ka: dict) -> dict:
    """T2 targeted / T2b untargeted, sharing one verb slot.

    T2 reuses `ol._TARGET_HEAD` rather than re-implementing it: grammar §6's b7
    Unwind ruling says a `-target-` slug needs the printed word (CR 601.2c), and
    re-typing that frame here would be the re-implementation defect that caused
    the majority of the recorded 21.
    """
    return {
        "T2": {t: re.compile(r"\b" + verb_alt(v) + r"\s+" + ol._TARGET_HEAD
                             + r"\s+([^.;]*)", re.I) for t, v in ka.items()},
        "T2b": {t: re.compile(r"\b" + verb_alt(v) + r"\s+([^.;]*)", re.I)
                for t, v in ka.items()},
    }


def card_object_re(domain: set) -> re.Pattern:
    """The `<CR type> card` object family — a DIFFERENT family, not a widening.

    CR 110.1: "A permanent is a card or token on the battlefield." So card text
    names an object in a non-battlefield zone as a CARD and an object on the
    battlefield by its permanent type, and `ol.classify_clause` REFUSES a type
    word followed by `card(s)` on purpose. Grammar §5 lists `card-in-graveyard`
    separately. Every tutor, every reanimation and every graveyard effect lives
    here, and Rampant Growth is the worked case.
    """
    return re.compile(r"\b(" + "|".join(sorted(map(re.escape, domain),
                                               key=len, reverse=True))
                      + r")\s+cards?\b", re.I)


def sweep(cards, texts, res, accept):
    """Cards matching any frame in `res` whose clause tail satisfies `accept`."""
    hit, by_term = set(), collections.Counter()
    for oid in cards:
        found = None
        for term, rx in res.items():
            for text in texts[oid]:
                for m in rx.finditer(text):
                    if accept(m.group(1)):
                        found = term
                        break
                if found:
                    break
            if found:
                break
        if found:
            hit.add(oid)
            by_term[found] += 1
    return hit, by_term


# ---------------------------------------------------------------------------
# census
# ---------------------------------------------------------------------------

def census(ctx=None, domain_override=None) -> dict:
    ctx = ctx or p.corpus()
    cards = ctx.cards
    n = len(cards)
    texts = {oid: fc.det_scan_texts(c) for oid, c in cards.items()}

    perm = ol.PERMANENT_TYPES if domain_override is None else domain_override
    wide = perm | ol.CARD_TYPES

    # T1 -- the lattice as shipped. `classes_for_card` returns a DICT, and a
    # dict with keys is ALWAYS truthy: testing it directly scored every one of
    # the 32,557 cards as reachable. Test ["classes"]. Probe defect #1.
    t1 = set()
    for oid, card in cards.items():
        for stem in ol.ACTION_VERBS:
            if ol.classes_for_card(card, stem, perm)["classes"]:
                t1.add(oid)
                break

    ka = keyword_actions()
    frames = build_frames(ka)
    perm_ok = lambda tail: bool(ol.classify_clause(tail, perm)["classes"])
    wide_ok = lambda tail: bool(ol.classify_clause(tail, wide)["classes"])
    cardobj = card_object_re(wide)

    t2, _ = sweep(cards, texts, frames["T2"], perm_ok)
    t2b, t2b_terms = sweep(cards, texts, frames["T2b"], wide_ok)
    t2c, t2c_terms = sweep(cards, texts, frames["T2b"],
                           lambda tail: bool(cardobj.search(tail)))

    # T3 -- CR 702 keyword presence. Membership is `keyword_line_tokens`, which
    # tests KEYWORD_HOME / KEYWORD_FORMS built from load_702.
    t3 = set()
    for oid, card in cards.items():
        for line in fx.ability_lines(card):
            if fx.keyword_line_tokens(line):
                t3.add(oid)
                break

    # T4 -- widest frame already in production. TIMING reach, not effect reach.
    # `p.rows` is used rather than `parse_deliveries` so D3 modal inheritance is
    # not lost, which is the defect that reported Charming Scoundrel a mismatch.
    t4 = set()
    for card, _line, toks, _descs in p.rows(ctx):
        if any(t and t != "None" for t in toks):
            t4.add(card["oracle_id"])

    effect = t1 | t2 | t2b | t2c | t3
    allf = effect | t4
    vanilla = {oid for oid, c in cards.items()
               if not (fc.full_oracle_text(c) or "").strip()}

    return {
        "corpus": n,
        "frames": {
            "T1_lattice_shipped": len(t1),
            "T2_cr701_targeted": len(t2),
            "T2b_cr701_untargeted": len(t2b),
            "T2c_card_object": len(t2c),
            "T3_cr702_keyword": len(t3),
            "T4_delivery_token_timing_only": len(t4),
        },
        "incremental": {
            "T2_over_T1": len(t2 - t1),
            "T2b_over_prior": len(t2b - t1 - t2),
            "T2c_over_prior": len(t2c - t1 - t2 - t2b),
            "T3_over_prior": len(t3 - t1 - t2 - t2b - t2c),
            "T4_over_prior": len(t4 - effect),
        },
        "effect_bearing_union": len(effect),
        "effect_bearing_pct": round(100 * len(effect) / n, 1),
        "union_with_timing": len(allf),
        "residual": n - len(effect),
        "vanilla": len(vanilla),
        "cr701_verbs": len(ka),
        "top_terms_T2b": t2b_terms.most_common(12),
        "top_terms_T2c": t2c_terms.most_common(10),
        "_sets": {"t1": t1, "effect": effect, "t2b": t2b, "t2c": t2c,
                  "t3": t3, "residual": set(cards) - effect},
    }


def fixtures(ctx, r) -> None:
    """GUARD D. `must_capture` cases are (text, should_match) and the predicate
    receives the TEXT element, NOT the tuple -- passing a (name, oid) pair made
    the first run report a clean pass on a broken filter. Probe defect #2.

    Two of these fixtures were WRONG on their first writing, and both were wrong
    about the CR rather than about the code, which is the recorded base rate:

      * `Rampant Growth` was asserted reachable by a permanent-type frame. It is
        not, and must not be: CR 110.1 makes `basic land card` a card in a
        library. It belongs to T2c. The refusal is the lattice working.
      * `Raise Dead` was asserted reachable by T2c. It is not, because `return`
        is NOT a CR 701 keyword action. CR 701 omits return, draw, deal, gain,
        put, tap and untap -- it is a list of NAMED actions, not an effect-verb
        vocabulary, and that is the hard cap on this census.
    """
    byname = {c["name"]: oid for oid, c in ctx.cards.items()}
    s = r["_sets"]

    def cap(label, members, names, want=True):
        missing = [n for n in names if n not in byname]
        if missing:
            fc.halt(f"{label} fixture names card(s) absent from the gated "
                    f"corpus: {missing}. Fix the fixture, not the census.")
        p.must_capture(lambda nm: byname[nm] in members,
                       [(nm, want) for nm in names], name=label)

    cap("T1 lattice", s["t1"], ["Putrefy", "Beast Within"])
    cap("T2b untargeted", s["t2b"], ["Wrath of God", "Day of Judgment"])
    cap("T2c card object", s["t2c"], ["Rampant Growth", "Cultivate"])
    cap("T3 keyword", s["t3"], ["Serra Angel", "Sengir Vampire"])
    # NEGATIVE control aimed at the CODE PATH, not the tool's name: a vanilla
    # creature must reach NO effect-bearing frame. Three of eight negative
    # controls on 2026-08-09 were mis-aimed and each first read as a broken gate.
    cap("effect union negative", s["effect"], ["Grizzly Bears"], want=False)


def selftest(ctx) -> int:
    """Break the census on purpose. A guard never shown to fail is not known to
    be a guard (`docs/SYSTEM-SELF-TEST-2026-08-09.md`, all eight Gate 2 checks)."""
    ok = True

    print("  [1] truncated CR 701 vocabulary must HALT")
    real = fx.cr_action_terms
    fx.cr_action_terms = lambda: {"destroy": real()["destroy"]}
    try:
        keyword_actions()
        print("      FAIL — a 1-term vocabulary was accepted")
        ok = False
    except SystemExit:
        print("      ok — halted")
    finally:
        fx.cr_action_terms = real

    print("  [2] substituted vocabulary must HALT (a count cannot see it)")
    ka = real()
    fx.cr_action_terms = lambda: {k: v for k, v in ka.items() if k != "destroy"}
    try:
        keyword_actions()
        print("      FAIL — a vocabulary missing `destroy` was accepted")
        ok = False
    except SystemExit:
        print("      ok — halted on CONTENT, with 68 members still present")
    finally:
        fx.cr_action_terms = real

    print("  [3] emptied object domain must fail the T1 fixture")
    r = census(ctx, domain_override=set())
    try:
        fixtures(ctx, r)
        print("      FAIL — fixtures passed with an empty permanent-type domain")
        ok = False
    except SystemExit:
        print("      ok — must_capture caught it")

    print("\n  SELFTEST " + ("PASSED — every guard is capable of failing."
                             if ok else "FAILED — a guard did not fire."))
    return 0 if ok else 1


def report(r, ctx, show_residual=0) -> None:
    n = r["corpus"]
    f, inc = r["frames"], r["incremental"]

    def row(label, k, ik=None):
        c = f[k]
        i = f"+{inc[ik]:,}" if ik else "baseline"
        print(f"  {label:52s} {c:>7,}  {100*c/n:>5.1f}%  {i:>9s}")

    print(f"\nCorpus (load_corpus_gated): {n:,} cards"
          f"   CR 701 verbs: {r['cr701_verbs']}\n")
    print(f"  {'frame':52s} {'cards':>7s}  {'share':>6s}  {'incr':>9s}")
    print("  " + "-" * 78)
    row("T1  object lattice as shipped", "T1_lattice_shipped")
    row("T2  all CR 701 verbs, `target` required",
        "T2_cr701_targeted", "T2_over_T1")
    row("T2b same verbs, untargeted, CR 205.2a types",
        "T2b_cr701_untargeted", "T2b_over_prior")
    row("T2c same verbs, `<CR type> card` (CR 110.1)",
        "T2c_card_object", "T2c_over_prior")
    row("T3  CR 702 keyword printed", "T3_cr702_keyword", "T3_over_prior")
    print("  " + "-" * 78)
    print(f"  {'EFFECT-BEARING UNION (T1..T3)':52s} "
          f"{r['effect_bearing_union']:>7,}  {r['effect_bearing_pct']:>5.1f}%"
          f"  {r['effect_bearing_union']-f['T1_lattice_shipped']:>+9,}")
    row("T4  ratified DELIVERY token — TIMING ONLY, upper bound",
        "T4_delivery_token_timing_only", "T4_over_prior")
    print(f"  {'union incl. timing':52s} {r['union_with_timing']:>7,}"
          f"  {100*r['union_with_timing']/n:>5.1f}%")
    print(f"\n  residual (no effect-bearing frame): {r['residual']:,}"
          f"   of which vanilla: {r['vanilla']:,}")
    print(f"  top T2b verbs: {r['top_terms_T2b']}")
    print(f"  top T2c verbs: {r['top_terms_T2c']}")

    if show_residual:
        resid = sorted(r["_sets"]["residual"])
        random.Random(SEED).shuffle(resid)
        print(f"\n  RESIDUAL SAMPLE (seed {SEED}), {show_residual}:")
        for oid in resid[:show_residual]:
            c = ctx.cards[oid]
            txt = " / ".join((fc.full_oracle_text(c) or "").split("\n"))[:96]
            print(f"    {c['name'][:30]:30s} | {c.get('type_line','')[:22]:22s}"
                  f" | {txt}")
        print("\n  The residual is NOT a judgment tail. Sampling shows "
              "counterspells,\n  damage against CR 120.1's recipient list, mana "
              "production and scry —\n  families templated against a closed list "
              "nobody has wired up yet.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", metavar="PATH",
                    help="write the census as JSON (for a future ratchet)")
    ap.add_argument("--residual", type=int, default=0, metavar="N",
                    help="print N residual cards, fixed seed")
    ap.add_argument("--selftest", action="store_true",
                    help="break every guard on purpose and prove it fires")
    a = ap.parse_args()

    ctx = p.corpus()
    if a.selftest:
        print("REACH CENSUS — NEGATIVE CONTROLS")
        return selftest(ctx)

    r = census(ctx)
    fixtures(ctx, r)
    report(r, ctx, a.residual)

    if a.json:
        out = {k: v for k, v in r.items() if k != "_sets"}
        Path(a.json).write_text(json.dumps(out, indent=1), encoding="utf-8")
        print(f"\n  wrote {a.json}")

    print("\n  REPORTER, NOT A GATE — exit 0 regardless of direction.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
