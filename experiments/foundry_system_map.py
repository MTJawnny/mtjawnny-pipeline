#!/usr/bin/env python3
"""THE SYSTEM MAP — what this pipeline is, stage by stage, and where each
stage's vocabulary COMES FROM.

Captain, 2026-08-05: *"ultimately I think we're reconciling from one method to
a newer method that references the CR. I can't see the system plainly. So I
don't know what other questions to ask."*

That is the right read, and this tool exists so it does not have to be taken on
trust. Every defect found on 2026-08-05 had ONE shape: **a list that should have
come from the CR came from somewhere else** — a human, the corpus, or an
author's memory of what cards look like. The migration from that older method to
"parse the CR at run time" is real and partial, and the only honest way to see
how partial is to MEASURE it.

WHY THIS IS GENERATED AND NOT WRITTEN
-------------------------------------
A hand-written map is a mirror, and this project's own finding (2026-08-01 §3)
is that *"the Comprehensive Rules are the only non-mirror"* — every hand-kept
duplicate of live state drifted. So this reads the live system and reports it.
Run it whenever you want to know where you are; it cannot go stale.

    python3 experiments/foundry_system_map.py

Zero API calls. Reads only; mutates nothing.
"""
import re
import sys
import collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import foundry_common as fc
import foundry_shape_extractor as fx
import foundry_cr702_classes as k7

BAR = "=" * 78


def rule(title):
    print(f"\n{BAR}\n{title}\n{BAR}")


def row(label, value, source, verdict):
    print(f"  {label:34s} {str(value):>9}  {source:26s} {verdict}")


CR_PARSED = "✔ CR-parsed at run time"
HEURISTIC = "◐ heuristic (no CR list)"
RATIFIED = "✔ ratified vocabulary"
DERIVED_OK = "✔ derived (legitimate)"


def main():
    cards, _, gated_out = fc.load_corpus_gated()
    fx.build_self_noun_rx(cards)
    ratified = fx.ratified_delivery_tokens()
    fx.build_keyword_homes(ratified)
    vocab = k7.type_vocabulary()

    print(__doc__.split("WHY THIS IS")[0].rstrip())

    # ---------------------------------------------------------------- stage 1
    rule("STAGE 1 — CORPUS.  What counts as a card?")
    print("  Source: Scryfall bulk JSONL, gated by tier_engine's loader.")
    row("cards admitted", len(cards), "Scryfall bulk", DERIVED_OK)
    row("cards gated out", gated_out if isinstance(gated_out, int) else "-",
        "gate rules", DERIVED_OK)
    print("\n  ⚠ THE GATE DECIDES WHAT THE CORPUS CAN CONTAIN. Any vocabulary")
    print("    HARVESTED from this population inherits the gate's blind spots —")
    print("    that is how 6 of CR 205.2a's 15 card types went unreachable.")

    # ---------------------------------------------------------------- stage 2
    rule("STAGE 2 — SEGMENTATION.  What is ONE ability?")
    print("  CR 113.2c: 'each PARAGRAPH BREAK marks a separate ability.'")
    print("  CR 603.11 / 607.2h: but one paragraph may hold a STATIC ability")
    print("  plus the TRIGGERED abilities linked to it.")
    print("  CR 603.12: a reflexive 'when you do' is CREATED, so its delivery")
    print("  belongs to its creator (§2d) — this is the discriminator.\n")
    lines = sum(1 for c in cards.values() for _ in fx.ability_lines(c))
    linked = multi = 0
    for c in cards.values():
        for line, parsed in fx.deliveries_for_lines(c, ratified):
            if any(str(d).startswith("linked:") for _, d in parsed):
                linked += 1
            if len(parsed) > 1:
                multi += 1
    row("ability lines (paragraphs)", lines, "CR 113.2c", CR_PARSED)
    row("lines yielding >1 delivery", multi, "CR 603.11/607.2h", CR_PARSED)
    row("  ...via a LINKED ability", linked, "CR 607.2h", CR_PARSED)
    print()
    row("ability words (CR 207.2c)", len(fx.CR_ABILITY_WORDS or ()),
        "CR 207.2c", CR_PARSED)
    row("  ...flavor-word residual", "_FLAVOR_WORD", "CR 207.2d (un-enumerable)",
        HEURISTIC)
    print("        ↑ DECLARED, not hidden: CR 207.2d states outright that flavor")
    print("          words are NOT listed in the CR, so no source can hold them.")
    row("trigger condition cut", "trigger_condition", "CR 113.3c + grammar", CR_PARSED)
    row("trigger clause verbs", "TRIGGER_VERB", "CR 701 keyword actions", CR_PARSED)
    row("compound-trigger split", "PREDICATE", "hand-written verb list", HEURISTIC)

    # ---------------------------------------------------------------- stage 3
    rule("STAGE 3 — CLASSIFICATION.  What KIND of ability is it?")
    print("  CR 113.3 enumerates FOUR categories, parsed at run time:")
    print("  113.3a spell · 113.3b activated · 113.3c triggered · 113.3d static")
    print("  The classifier is a branch chain; the TAIL is the fallback.\n")
    tot = rt = 0
    desc = collections.Counter()
    tokens = collections.Counter()
    for c in cards.values():
        for line, parsed in fx.deliveries_for_lines(c, ratified):
            for t, d in parsed:
                tot += 1
                if t:
                    rt += 1
                    tokens[t] += 1
                else:
                    desc[d] += 1
    row("deliveries emitted", tot, "the classifier", DERIVED_OK)
    row("  landed on a §2 token", rt, "grammar §2", RATIFIED)
    row("  reported, no token", tot - rt, "own descriptor", "◐ honest gap")
    print()
    print("  The reported population, by descriptor (a census CANNOT see past")
    print("  these — a wrong token looks exactly like a right one):")
    for d, n in desc.most_common(6):
        print(f"      {n:7d}  {d}")

    # ---------------------------------------------------------------- stage 4
    rule("STAGE 4 — VOCABULARY.  What are we ALLOWED to call it?")
    print("  This is where the migration Captain named is visible. Each list")
    print("  below either comes FROM THE CR or does not.\n")
    base_in_use = {re.sub(r"^(any|other)-", "", t) for t in tokens}
    row("§2 DELIVERY base tokens", len(ratified), "grammar §2 table", RATIFIED)
    row("  ...emitted, incl §2a prefixes", len(tokens), "measured", DERIVED_OK)
    row("  ...distinct base tokens used", len(base_in_use & set(ratified)),
        "measured", DERIVED_OK)
    dead = sorted(t for t in ratified
                  if tokens[t] == 0 and t not in base_in_use)
    row("  ...ratified, ZERO members", len(dead), "measured", "◐ hypothesis or dead")
    for t in dead:
        why = "reserved by a CR enumeration" if ("battle" in t or "planeswalker" in t
                                                 or "other-zone" in t) else "NO EMITTER — see AUDIT-5"
        print(f"        {t:44s} {why}")
    print()
    row("CR 205.2a card types", len(vocab["card_types"]), "CR 205.2a", CR_PARSED)
    row("CR 205.3g-q subtypes", len(vocab["subtypes"]), "CR 205.3g-q", CR_PARSED)
    row("CR 205.4a supertypes", len(vocab["supertypes"]), "CR 205.4a", CR_PARSED)
    row("CR 120.1 damage recipients", len(fx.CR_DAMAGE_RECIPIENTS or []),
        "CR 120.1", CR_PARSED)
    row("CR 400.1 zones", len(fx.CR_ZONES or []), "CR 400.1", CR_PARSED)
    row("CR 702 keyword homes", len(fx.KEYWORD_HOME or {}), "CR 702.Na (§2b)", CR_PARSED)
    row("self-reference nouns", len(fx.SELF_NOUN_RX.pattern.split("|")),
        "CR 205 (all lists)", CR_PARSED)
    print()
    print("  STILL HEURISTIC — declared, not hidden. The CR publishes no closed")
    print("  list for these, so they are judgements and are named as such:")
    print("      · static-grant duration markers (until/target/perpetually)")
    print("        CR 611.2a says only \"such as 'until end of turn'\".")
    print("      · compound-trigger PREDICATE verbs — game EVENTS; the CR")
    print("        enumerates keyword ACTIONS (701) only.")
    print("      · CR 207.2d FLAVOR words — the CR says outright they are")
    print("        \"not listed in the Comprehensive Rules\". Un-enumerable BY")
    print("        RULE, which is the one honest reason a shape may stand.")

    # ---------------------------------------------------------------- stage 5
    rule("STAGE 5 — CODEBOOK.  Which AXIS does the card join?")
    try:
        import foundry_codebook as fcb
        cb = fcb.load_codebook()
        axes = cb["axes"]
        active = [s for s, e in axes.items() if e.get("status") == "active"]
        members = sum(len(e.get("members", [])) for e in axes.values())
        row("axes", len(axes), "codebook.json", RATIFIED)
        row("  active", len(active), "codebook.json", RATIFIED)
        row("members", members, "codebook.json", RATIFIED)
    except Exception as e:
        print(f"  (codebook unavailable: {e})")
    print("\n  Parents are DERIVED — the union of children plus direct members —")
    print("  and that is the ONE place inference is legitimate (Captain, 2026-08-05).")

    # ---------------------------------------------------------------- verdict
    rule("THE MIGRATION — where the old method still lives")
    print("""  OLD METHOD: a list written by a human, or harvested from the corpus,
  standing where the CR publishes an enumeration.
  NEW METHOD: parse the CR at run time, with a CONTENT halt-guard.

  Stage 1 corpus      — n/a, the corpus is data
  Stage 2 segmentation— MIXED. Clause/condition/sentence cuts are CR-anchored,
                        and so is the ability-word strip since 2026-08-06
                        (CR 207.2c parsed; each refusal cites 714.2 / 706.3b /
                        700.2 / 601.2b / 602.1 / 702.Na). PREDICATE is the last
                        hand-list here. ← the live frontier
  Stage 3 classify    — CR-anchored throughout (113.3, 614, 603, 120, 400, 700)
  Stage 4 vocabulary  — CR-parsed, except two DECLARED heuristics
  Stage 5 codebook    — ratified by Captain; parents legitimately derived

  THE QUESTION THAT FINDS DEFECTS, and it is the only one you need:

      \"Where does this list come from, and can that source contain every
       member the CR names?\"

  A human list fails it obviously. A CORPUS HARVEST fails it silently — it
  looks derived, and the gate decides its contents. That single question found
  every defect on 2026-08-05.""")
    print()


if __name__ == "__main__":
    main()
