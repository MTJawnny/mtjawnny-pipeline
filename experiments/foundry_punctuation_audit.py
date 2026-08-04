#!/usr/bin/env python3
"""CONSERVATION AUDIT for the punctuation rulings — did anything get LOST?

Captain, 2026-08-06: *"we'll need to rescan the corpus with the new punctuation
rulings to make sure nothing got lost."*

The rulings in question all cut a line on punctuation, and each one can lose an
ability by cutting in the wrong place:

  CR 207.2c/207.2d  the em-dash ability/flavor-word prefix   (2026-08-06)
  CR 113.2c         a PARAGRAPH is the ability boundary
  CR 603.11/607.2h  ...but one paragraph may hold several abilities, so the
                    sentence split on `.` / `!` is load-bearing (2026-08-05)
  CR 603.12         a reflexive "when you do" is CREATED, not separate
  CR 700.2          a modal header's bullets are its modes

**A GAP CENSUS CANNOT ANSWER THIS QUESTION.** A census reports shapes with no
ratified token; a line that was silently truncated, dropped, or never emitted
looks to a census exactly like a shape the corpus does not contain. So every
test here is a CONSERVATION test — it asserts that something which went in came
back out — plus one recall inversion, which is the only method that sees an
absence.

Exit 1 on any violation. Zero tokens, deterministic, safe to gate on.

    python3 experiments/foundry_punctuation_audit.py
    python3 experiments/foundry_punctuation_audit.py --json out.json
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


def rule(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


# Punctuation classes the rulings touch. A line is counted in a class if its
# ability text carries that character AT ALL -- the point is to compare each
# class's unrouted RATE against the corpus rate, not to claim the character
# caused anything.
CLASSES = {
    "em-dash prefix": lambda l: fx._DASH_PREFIX.match(l) is not None,
    "terminal !": lambda l: "!" in l,
    "terminal ?": lambda l: "?" in l,
    "ellipsis ...": lambda l: "..." in l or "…" in l,
    "comma": lambda l: "," in l,
    "colon": lambda l: ":" in l,
    "semicolon": lambda l: ";" in l,
    "quote": lambda l: '"' in l or "“" in l,
    "digit": lambda l: re.search(r"\d", l) is not None,
    # LETTERS only. `[^\x00-\x7f]` also matches the em-dash, the bullet and the
    # curly apostrophe, so it scored 6,342 lines and simply re-measured three
    # classes already in this table. A probe that overlaps another probe
    # reports a correlation as a finding.
    "non-ASCII letter": lambda l: re.search(r"[^\W\d_]", l, re.A) is not None
    and re.search(r"[^\x00-\x7f]", re.sub(r"[^\w]", "", l)) is not None,
    "multi-sentence": lambda l: len(fx.sentence_spans(l)) > 1,
    "bullet (modal mode)": lambda l: l.lstrip().startswith("•"),
}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json")
    ap.add_argument("--limit", type=int, default=12)
    args = ap.parse_args()

    cards, _, _ = fc.load_corpus_gated()
    fx.build_self_noun_rx(cards)
    ratified = fx.ratified_delivery_tokens()
    fx.build_keyword_homes(ratified)

    violations = []
    report = {}

    # ------------------------------------------------------------------ A
    # TEXT CONSERVATION. The strip may only remove a PREFIX. This is the test
    # that would have caught the 2026-08-04 hyphen disaster ("When Spider-Ham
    # enters" -> "Ham enters", 556 lines mutilated) on the day it landed,
    # without knowing anything about ability words: a strip that deletes from
    # the MIDDLE of a line is wrong whatever its regex intended.
    rule("A — TEXT CONSERVATION.  The strip removes a PREFIX or nothing.")
    lines_all, stripped_n = 0, 0
    for oid, card in cards.items():
        for line in fx.ability_lines(card):
            lines_all += 1
            pre, body = fx.ability_word_prefix(line)
            if pre is None:
                if body != line:
                    violations.append(("A", card["name"], line, "refused but altered"))
                continue
            stripped_n += 1
            if not line.endswith(body):
                violations.append(("A", card["name"], line, f"body not a suffix: {body!r}"))
            # what was removed must be the prefix we say it is
            removed = line[:len(line) - len(body)]
            if pre not in removed:
                violations.append(("A", card["name"], line, f"prefix {pre!r} not in removed {removed!r}"))
    print(f"  ability lines                        {lines_all:>7}")
    print(f"  prefix stripped                      {stripped_n:>7}")
    print(f"  violations                           {len([v for v in violations if v[0]=='A']):>7}")
    report["lines"] = lines_all
    report["stripped"] = stripped_n

    # ------------------------------------------------------------------ B
    # SENTENCE CONSERVATION. `sentence_spans` feeds the CR 603.11/607.2h split;
    # if it drops characters, a second ability in the paragraph is unreachable
    # and the loss is invisible downstream.
    rule("B — SENTENCE CONSERVATION.  Splitting on '.'/'!' loses no text.")
    lossy = 0
    for oid, card in cards.items():
        for line in fx.ability_lines(card):
            body = fx.strip_ability_word(line)
            sents = fx.sentence_spans(body)
            if not sents:
                if body.strip():
                    violations.append(("B", card["name"], line, "no sentences from non-empty body"))
                continue
            joined = re.sub(r"\s+", "", "".join(sents))
            if joined != re.sub(r"\s+", "", body):
                lossy += 1
                violations.append(("B", card["name"], line, "sentence split lost text"))
    print(f"  lines whose sentences do not reassemble   {lossy:>3}")

    # ------------------------------------------------------------------ C
    # ABILITY CONSERVATION. Every ability line must yield AT LEAST ONE delivery
    # row. A line yielding zero is an ability that left the pipeline.
    rule("C — ABILITY CONSERVATION.  Every line yields >=1 delivery.")
    emitted, zero, multi, linked = 0, 0, 0, 0
    per_desc = collections.Counter()
    for oid, card in cards.items():
        for line, parsed in fx.deliveries_for_lines(card, ratified):
            if not parsed:
                zero += 1
                violations.append(("C", card["name"], line, "ZERO deliveries"))
                continue
            emitted += len(parsed)
            if len(parsed) > 1:
                multi += 1
            for tok, desc in parsed:
                if str(desc).startswith("linked:"):
                    linked += 1
                if tok is None:
                    per_desc[desc] += 1
    print(f"  deliveries emitted                   {emitted:>7}")
    print(f"  lines yielding ZERO                  {zero:>7}")
    print(f"  lines yielding >1                    {multi:>7}")
    print(f"  ...linked abilities (CR 607.2h)      {linked:>7}")
    report.update(emitted=emitted, zero=zero, multi=multi, linked=linked)

    # ------------------------------------------------------------------ D
    # RECALL INVERSION. The only method that sees an ABSENCE. If a punctuation
    # class is over-represented among UNROUTED lines relative to the corpus,
    # the cut for that class is still losing recall.
    rule("D — RECALL INVERSION.  Is a punctuation class over-represented\n"
         "    among UNROUTED lines?  (ratio > 1 = worse than the corpus)")
    tot = collections.Counter()
    unr = collections.Counter()
    n_lines = n_unrouted = 0
    for oid, card in cards.items():
        for line, parsed in fx.deliveries_for_lines(card, ratified):
            n_lines += 1
            is_unrouted = all(t is None for t, _ in parsed)
            n_unrouted += is_unrouted
            for name, test in CLASSES.items():
                try:
                    hit = test(line)
                except Exception:
                    hit = False
                if hit:
                    tot[name] += 1
                    unr[name] += is_unrouted
    base = n_unrouted / n_lines if n_lines else 0
    print(f"  corpus unrouted rate  {n_unrouted}/{n_lines} = {base:.3f}\n")
    print(f"  {'class':<22}{'lines':>8}{'unrouted':>10}{'rate':>8}{'ratio':>8}")
    rows = []
    for name in CLASSES:
        t, u = tot[name], unr[name]
        r = (u / t) if t else 0
        rows.append((r / base if base else 0, name, t, u, r))
    for ratio, name, t, u, r in sorted(rows, reverse=True):
        flag = "  <-- over-represented" if ratio > 1.25 and t >= 50 else ""
        print(f"  {name:<22}{t:>8}{u:>10}{r:>8.3f}{ratio:>8.2f}{flag}")
    report["recall_inversion"] = {n: {"lines": tot[n], "unrouted": unr[n]} for n in CLASSES}

    # ------------------------------------------------------------------ E
    # The unrouted descriptors, so a loss cannot hide inside a catch-all.
    rule("E — WHERE THE UNROUTED LINES ARE  (a loss must show up here)")
    for desc, n in per_desc.most_common(args.limit):
        print(f"  {n:>7}  {desc}")
    report["unrouted_descriptors"] = dict(per_desc)

    # ------------------------------------------------------------------
    rule("VERDICT")
    if violations:
        print(f"  ✗ {len(violations)} CONSERVATION VIOLATIONS\n")
        for cls, name, line, why in violations[:args.limit]:
            print(f"  [{cls}] {name}: {why}\n        {line[:96]}")
        if len(violations) > args.limit:
            print(f"  ... and {len(violations) - args.limit} more")
    else:
        print("  ✓ no text, sentence or ability was lost.")
        print("    Every line yields a delivery; every strip removes a prefix;")
        print("    every sentence split reassembles to its input.")

    if args.json:
        report["violations"] = [
            {"test": c, "card": n, "line": l, "why": w} for c, n, l, w in violations]
        Path(args.json).write_text(json.dumps(report, indent=2, sort_keys=True))
        print(f"\nwrote {args.json}")
    sys.exit(1 if violations else 0)


if __name__ == "__main__":
    main()
