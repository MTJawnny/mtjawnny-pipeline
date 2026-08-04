#!/usr/bin/env python3
"""GATE AUDIT — what does Gate #0 hide from every other check?

Gate #0 (batch-6 D1, ratified 2026-07-30) is not in question here: a card is a
foundry target iff it is legal or restricted in some format, and that is the
right population to BUILD on. The problem is that **every** standing check
calls `load_corpus_gated()` -- lint, family sweep, definition drift, ruling
registry, conservation, visibility, ground truth, the routing regression. So
the gate is a single blind spot shared by all of them, and nothing reports what
it removed.

That has already cost this project once. The self-reference noun set was
DERIVED from live corpus type lines and was still missing 6 of CR 205.2a's 15
card types -- including CR 109.2d's own worked case, `this scheme` -- because
the gate excludes the `scheme` layout. CLAUDE.md's rule came out of it:

    a corpus scan of type lines is kept only as a TEST of the CR parse,
    never as its source ... the test is not "did a human type this list"
    but "CAN THE SOURCE CONTAIN EVERY MEMBER THE CR NAMES?"

This file runs that test. Three questions:

  1. COVERAGE   for each CR-parsed enumeration, which members are attested
                only OUTSIDE the gate -- i.e. which ones a gated corpus scan
                could never have found
  2. EXPOSURE   run the extractor over the gated-OUT cards and report any
                DESCRIPTOR that never occurs inside the gate -- a shape the
                whole toolchain has never been shown
  3. SURVIVAL   the gated-out cards must not crash the extractor. Halt-loudly
                is house style, so a halt here is a finding, not a pass.

Exit 1 only on SURVIVAL. Coverage and exposure are REPORTED: a CR member with
no in-gate attestation is expected (the CR is the source, the corpus is the
test), and the number is the point.

    python3 experiments/foundry_gate_audit.py
    python3 experiments/foundry_gate_audit.py --json out.json
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
import foundry_cr702_classes as k7     # noqa: E402


def rule(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


def type_blob(cards) -> str:
    """One newline-joined blob of every DISTINCT type line, all faces, lowered.

    Attestation is tested by whole-word search against this, NOT by splitting
    type lines into words. The first run of this file did split on whitespace
    and reported 28 CR subtypes as attested nowhere in the corpus. Every one
    was the probe's fault, in two families the repo has already recorded:

      MULTIWORD members  `time lord`, `serra's realm`, `bolas's meditation
                         realm`, `outside mutter's spiral` -- CR 205.3 names
                         them, a word split cannot see them
      CURLY APOSTROPHE   `urza’s`, `c’tan`, `shi’ar` -- "the CR prints a CURLY
                         apostrophe (U+2019); Scryfall prints a straight one",
                         so the search has to try both forms

    Distinct lines, not per-card sets: there are ~10k of them against 38k
    cards, and the answer is a set question either way.
    """
    seen = set()
    for c in cards:
        for t in [c.get("type_line") or ""] + [f.get("type_line") or ""
                                               for f in (c.get("card_faces") or [])]:
            if t:
                seen.add(t.lower())
    return "\n".join(sorted(seen))


def attested(member: str, blob: str) -> bool:
    """Is a CR 205 member printed on any type line in `blob`?"""
    for form in {member, member.replace("’", "'"), member.replace("'", "’")}:
        if re.search(r"(?<!\w)" + re.escape(form) + r"(?!\w)", blob):
            return True
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json")
    ap.add_argument("--limit", type=int, default=16)
    args = ap.parse_args()

    raw, _ = fc.load_corpus()
    inside, _, _ = fc.load_corpus_gated()
    outside = {oid: c for oid, c in raw.items() if oid not in inside}

    fx.build_self_noun_rx(inside)
    ratified = fx.ratified_delivery_tokens()
    fx.build_keyword_homes(ratified)

    rule("THE GATE")
    print(f"  corpus                               {len(raw):>7}")
    print(f"  inside Gate #0                       {len(inside):>7}")
    print(f"  OUTSIDE                              {len(outside):>7}"
          f"   ({len(outside)/len(raw):.1%})")
    lay_in = collections.Counter(c.get("layout", "?") for c in inside.values())
    lay_out = collections.Counter(c.get("layout", "?") for c in outside.values())
    only_out = sorted(set(lay_out) - set(lay_in))
    print(f"\n  layouts that exist ONLY outside the gate ({len(only_out)}):")
    for lay in only_out:
        print(f"     {lay:26}{lay_out[lay]:>6} cards")

    report = {"inside": len(inside), "outside": len(outside),
              "layouts_only_outside": only_out}

    # ----------------------------------------------------------------- 1
    rule("1. COVERAGE — CR members a GATED corpus scan could never attest")
    v = k7.type_vocabulary()
    blob_in = type_blob(inside.values())
    blob_out = type_blob(outside.values())

    enums = {
        "CR 205.2a card types": v["card_types"],
        "CR 205.4a supertypes": v["supertypes"],
        "CR 205.3 subtypes (all)": v["subtypes"],
        "CR 205.3i land types": v["land_types"],
        "CR 205.3k spell types": v["spell_types"],
    }
    print("  'nowhere' = printed on NO type line in the whole corpus. That is")
    print("  not a defect: a token-only creature type (blinkmoth, camarid,")
    print("  caribou, prism, tetravite …) is named in ORACLE TEXT and never on")
    print("  a type line, so CR 205.3 lists it and no type-line scan can see it.")
    print("  One more reason the CR is the source and this is only the test.\n")
    print(f"  {'enumeration':30}{'members':>9}{'in gate':>9}{'ONLY out':>10}{'nowhere':>9}")
    cov = {}
    for name, members in enums.items():
        out_only, never = [], []
        for m in sorted(members):
            if attested(m, blob_in):
                continue
            (out_only if attested(m, blob_out) else never).append(m)
        only = out_only
        n_in = len(members) - len(only) - len(never)
        cov[name] = {"members": len(members), "in_gate": n_in,
                     "only_outside": only, "nowhere": never}
        print(f"  {name:30}{len(members):>9}{n_in:>9}{len(only):>10}{len(never):>9}")
        if only:
            print(f"     ONLY OUTSIDE: {', '.join(only[:args.limit])}"
                  + (f" … +{len(only)-args.limit}" if len(only) > args.limit else ""))
    report["coverage"] = cov

    # ----------------------------------------------------------------- 2
    rule("2. EXPOSURE — descriptors the toolchain has NEVER been shown")
    desc_in = collections.Counter()
    for c in inside.values():
        for _line, parsed in fx.deliveries_for_lines(c, ratified):
            for _t, d in parsed:
                desc_in[str(d)] += 1
    desc_out = collections.Counter()
    crashed = []
    for oid, c in outside.items():
        try:
            for _line, parsed in fx.deliveries_for_lines(c, ratified):
                for _t, d in parsed:
                    desc_out[str(d)] += 1
        except SystemExit:
            crashed.append((c.get("name", oid), "HALTED"))
        except Exception as exc:                      # noqa: BLE001
            crashed.append((c.get("name", oid), f"{type(exc).__name__}: {exc}"))
    novel = {d: n for d, n in desc_out.items() if d not in desc_in}
    print(f"  distinct descriptors inside the gate  {len(desc_in):>6}")
    print(f"  distinct descriptors outside          {len(desc_out):>6}")
    print(f"  NOVEL (never seen inside)             {len(novel):>6}")
    for d, n in sorted(novel.items(), key=lambda kv: -kv[1])[:args.limit]:
        print(f"     {n:>6}  {d}")
    report["novel_descriptors"] = novel

    # ----------------------------------------------------------------- 3
    rule("3. SURVIVAL — the extractor must not crash on what the gate excludes")
    print(f"  gated-out cards parsed                {len(outside) - len(crashed):>6}")
    print(f"  CRASHED or HALTED                     {len(crashed):>6}")
    for name, why in crashed[:args.limit]:
        print(f"     {name[:34]:36}{why}")
    report["crashed"] = [list(x) for x in crashed]

    rule("VERDICT")
    if crashed:
        print(f"  ✗ {len(crashed)} gated-out card(s) crashed the extractor.")
    else:
        print("  ✓ Every gated-out card parses. The gate is a POPULATION")
        print("    decision, not a capability limit -- so a CR enumeration can")
        print("    be tested against the whole corpus even where the foundry")
        print("    only builds on part of it.")
    if any(cov[k]["only_outside"] for k in cov):
        n = sum(len(cov[k]["only_outside"]) for k in cov)
        print(f"\n  ◐ {n} CR member(s) are attested ONLY outside the gate. Any")
        print("    vocabulary derived from a GATED corpus scan would have")
        print("    missed them. Derive from the CR; use the corpus as the test.")

    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=2, sort_keys=True))
        print(f"\nwrote {args.json}")
    sys.exit(1 if crashed else 0)


if __name__ == "__main__":
    main()
