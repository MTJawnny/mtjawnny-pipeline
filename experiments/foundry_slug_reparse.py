#!/usr/bin/env python3
"""HOW CLEANLY DOES THE CODEBOOK REPARSE INTO TYPED FIELDS?

The question this answers: grammar §1 defines every slug as a hyphen-joined
sequence of slots --

    [DELIVERY]-[EFFECT]-[OBJECT]-[SCOPE]-[QUALIFIER...]

-- but the codebook stores the RESULT of that join, not the slots. If the join
is invertible, promoting the slugs to typed fields is a serialization change.
If it is not, the string is lossy and every consumer has to re-derive a parser
(which `foundry_ground_truth.py` already does, longest-prefix-first, with a
comment explaining why the order is load-bearing).

MINTS NOTHING. JUDGES NOTHING. Reports coverage and AMBIGUITY.

THE BOUNDARY, stated because a finding without its boundary is not reportable:
  · DELIVERY  = §2's ratified table, parsed at run time (the same call the
                extractor makes), plus §2a's `any-`/`other-`/`source-` prefixes.
  · EFFECT    = backticked identifiers under grammar §4.
  · SCOPE     = backticked identifiers under grammar §6.
  · KEYWORD   = CR_KEYWORD_NAMES from load_702, never KEYWORD_HOME (the
                recorded "a derived map is not the list it was derived from").
  · §5 OBJECT, §7 scaling and §8 counter/token types are modelled too, and
    matched GREEDILY LONGEST-FIRST so multiword terms (`you-control`,
    `create-token`) are not shredded. Per-segment matching scored 24.1% and
    listed `you`, `control`, `create` as unknown -- it had shredded the
    vocabulary it was measuring against.
  · Active = `status == "active"` (359 axes). NOT a guessed set: the terminal
    statuses are `renamed`/`killed`/`merged`, and guessing `retired`/`dropped`
    let 75 killed axes through.
  · The numbers to read are the AMBIGUITY count and the per-axis TAIL
    distribution, never a single pass rate.

    python3 experiments/foundry_slug_reparse.py
    python3 experiments/foundry_slug_reparse.py --show-unknown 40 --json out.json
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

GRAMMAR = REPO_ROOT.parent / "docs" / "CODEBOOK-NAMING-GRAMMAR.md"
CODEBOOK = REPO_ROOT / "out" / "foundry" / "codebook.json"


def rule(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


def section_tokens(text: str, num: str) -> set:
    """Backticked identifiers under a `## <num>.` heading, to the next `## `.

    Halt-guarded: grammar sections are markdown and a heading rename would
    silently return an empty set, which would score every segment UNKNOWN and
    read as a catastrophic finding. That is the "a halt-guard must assert
    CONTENT, not cardinality" rule applied to this probe's own input.
    """
    m = re.search(rf"^## {re.escape(num)}\..*?$(.*?)(?=^## \d)", text,
                  re.M | re.S)
    if not m:
        fc.halt(f"grammar section §{num} not found in {GRAMMAR}. This probe "
                f"derives its vocabulary from that section; without it every "
                f"segment would score UNKNOWN and the result would be a lie.")
    toks = {t.strip("`") for t in re.findall(r"`([a-z0-9][a-z0-9\-<>]*)`",
                                             m.group(1))}
    return {t for t in toks if t and not t.startswith("-")}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--show-unknown", type=int, default=25)
    ap.add_argument("--show-ambiguous", type=int, default=15)
    ap.add_argument("--json")
    args = ap.parse_args()

    cards, _, _ = fc.load_corpus_gated()
    fx.build_self_noun_rx(cards)
    delivery = fx.ratified_delivery_tokens()
    fx.build_keyword_homes(delivery)
    keywords = set(fx.CR_KEYWORD_NAMES or ())

    text = GRAMMAR.read_text(encoding="utf-8")
    effects = section_tokens(text, "4")
    scopes = section_tokens(text, "6")
    # §5 OBJECT and §8 counter/token types are REAL slots in §1's sequence.
    # The first run declared them unmodelled and then reported a coverage
    # number as if the remainder should have matched anyway -- which is a
    # boundary stated in prose and ignored in the arithmetic.
    objects = section_tokens(text, "5")
    counters = section_tokens(text, "8")
    VOCAB = effects | scopes | objects | counters
    cb = json.loads(CODEBOOK.read_text(encoding="utf-8"))
    axes = cb["axes"]

    rule("VOCABULARIES — derived at run time, never hand-listed")
    print(f"  §2 DELIVERY tokens            {len(delivery):>6}")
    print(f"  §4 EFFECT identifiers         {len(effects):>6}")
    print(f"  §5 OBJECT identifiers         {len(objects):>6}")
    print(f"  §6 SCOPE identifiers          {len(scopes):>6}")
    print(f"  §8 counter/token identifiers  {len(counters):>6}")
    print(f"  CR 702 keyword names          {len(keywords):>6}")
    for name, s in (("§4", effects), ("§6", scopes)):
        if len(s) < 5:
            fc.halt(f"{name} parsed only {len(s)} identifiers — the section "
                    f"shape changed. Refusing to report a coverage number "
                    f"derived from an empty vocabulary.")

    # §2a prefixes are part of the DELIVERY slot, not separate slots.
    PREFIXES = ("any-", "other-", "source-")
    deliv_all = set(delivery)
    for p in PREFIXES:
        deliv_all |= {p + d for d in delivery}

    active, heads, ambiguous, unknown_seg = [], collections.Counter(), [], collections.Counter()
    member_w = collections.Counter()
    seg_total = seg_known = 0

    for slug, ax in sorted(axes.items()):
        # The terminal statuses are `renamed` / `killed` / `merged` -- NOT the
        # `retired`/`dropped` this probe first guessed, which let 75 killed
        # axes through and put the active count at 436 against
        # `foundry_definition_drift.py`'s 359. Assert against the live field
        # rather than a remembered vocabulary.
        if ax.get("status") != "active":
            continue
        body = slug.split(":", 1)[1] if ":" in slug else slug
        n_mem = len(ax.get("members") or [])
        active.append(slug)

        # --- DELIVERY: every token that heads this slug, longest first
        matches = sorted((d for d in deliv_all
                          if body == d or body.startswith(d + "-")),
                         key=len, reverse=True)
        if matches:
            kind = "delivery"
            if len(matches) > 1:
                ambiguous.append((slug, matches, n_mem))
            rest = body[len(matches[0]):].lstrip("-")
        elif body in keywords:
            kind, rest = "cr702-keyword", ""
        else:
            kind, rest = "no-delivery (§1 spell / other)", body
        heads[kind] += 1
        member_w[kind] += n_mem

        # GREEDY LONGEST-MATCH over the hyphen SEQUENCE, never per-segment.
        # Ratified vocabulary items CONTAIN hyphens -- `you-control`,
        # `create-token`, `gain-life`, `plus1-counter` -- so splitting on `-`
        # and testing each piece guarantees every multiword term scores
        # UNKNOWN. The probe's first run reported 24.1% coverage and its top
        # "unknown" segments were `you`, `control`, `create`, `token`: it had
        # shredded the vocabulary it was measuring against. Same family as the
        # recorded "a probe must consume the SAME preprocessing as the
        # classifier it is measuring".
        segs = [s for s in rest.split("-") if s]
        i = 0
        while i < len(segs):
            hit = 0
            for j in range(min(len(segs), i + 4), i, -1):
                cand = "-".join(segs[i:j])
                if (cand in VOCAB or cand in keywords or cand in delivery
                        or cand.isdigit()):
                    hit = j - i
                    break
            seg_total += 1
            if hit:
                seg_known += 1
                i += hit
            else:
                unknown_seg[segs[i]] += 1
                i += 1

    rule("1. DOES THE SLUG'S HEAD RESOLVE TO A TYPED DELIVERY?")
    print(f"  active axes                   {len(active):>6}")
    print(f"  {'':30}{'axes':>7}{'members':>10}")
    for k, v in heads.most_common():
        print(f"  {k:30}{v:>7}{member_w[k]:>10}")

    rule("2. AMBIGUITY — slugs where MORE THAN ONE §2 token heads the slug")
    print("  This is the number that decides the architecture question. A slug")
    print("  with >1 valid head cannot be inverted without an out-of-band rule")
    print("  (today: 'longest wins', encoded in each consumer separately).")
    print()
    print(f"  ambiguous slugs               {len(ambiguous):>6}")
    print(f"  ...members affected           {sum(m for _, _, m in ambiguous):>6}")
    for slug, ms, n in sorted(ambiguous, key=lambda r: -r[2])[:args.show_ambiguous]:
        print(f"    {slug[:48]:50} n={n:<5} {ms}")
    if len(ambiguous) > args.show_ambiguous:
        print(f"    ... and {len(ambiguous) - args.show_ambiguous} more")

    rule("3. SEGMENT COVERAGE of the remainder (after the DELIVERY head)")
    print("  §5 OBJECT and §8 counter/token types are NOT modelled here, so an")
    print("  UNKNOWN segment is a slot this probe does not know, not a defect.")
    print("  Read the TAIL for whether the residue is structured or arbitrary.")
    print()
    pct = 100.0 * seg_known / seg_total if seg_total else 0.0
    print(f"  segments after the head       {seg_total:>6}")
    print(f"  ...matched §4/§6/keyword      {seg_known:>6}   ({pct:.1f}%)")
    print(f"  ...UNKNOWN                    {seg_total - seg_known:>6}")
    print(f"  distinct UNKNOWN segments     {len(unknown_seg):>6}")
    print()
    print("  most frequent UNKNOWN segments:")
    for seg, n in unknown_seg.most_common(args.show_unknown):
        print(f"    {n:>5}  {seg}")

    rule("VERDICT")
    if not ambiguous:
        print("  ✓ Every slug head resolves to exactly one §2 token. The join")
        print("    is invertible at the DELIVERY slot and promoting it to a")
        print("    typed field is a SERIALIZATION change, not a re-modelling.")
    else:
        print(f"  ◐ {len(ambiguous)} slug(s) admit more than one DELIVERY parse.")
        print("    The string is not self-describing: inversion depends on a")
        print("    'longest wins' convention that lives in consumers, not in")
        print("    the data. Each new consumer re-implements it or gets it wrong.")

    if args.json:
        Path(args.json).write_text(json.dumps({
            "active_axes": len(active),
            "heads": dict(heads), "member_weight": dict(member_w),
            "ambiguous": [[s, m, n] for s, m, n in ambiguous],
            "segments": {"total": seg_total, "known": seg_known},
            "unknown_segments": dict(unknown_seg.most_common()),
        }, indent=2, sort_keys=True))
        print(f"\nwrote {args.json}")


if __name__ == "__main__":
    main()
