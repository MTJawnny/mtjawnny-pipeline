#!/usr/bin/env python3
"""DESIGN GOAL #1 — is one mechanic wearing two names in the live codebook?

Grammar §4's whole premise is *"One verb per mechanic, chosen once, used
everywhere."* §14 Q5 then RULED on a specific violation of it, excluding the
token `lifegain` as *"a synonym-collision candidate against the ratified
`gain-life` EFFECT verb"*. §4 says the same of the other direction: *"All
`creates-` slugs normalize at the walk."*

Both rulings exist. Nothing enforces either. This measures it.

NOT A HAND-LIST OF SYNONYMS -- that would be the recorded "a hand-list is a
defect with a delay" trap aimed at the very check meant to catch it. The
collision is DERIVED: a ratified multi-word §4 verb defines a WORD SET, and any
slug run carrying the same stems in a different arrangement is the same mechanic
spelled differently. `gain-life` -> {gain, life}; `lifegain` carries both stems
concatenated; `token-creation` carries {token, creat*} which is `create-token`
reordered and inflected.

Reports only. Renaming an axis is codebook surgery and rides the backup law.

    python3 experiments/foundry_synonym_collision.py
    python3 experiments/foundry_synonym_collision.py --strict
"""
import sys
import re
import argparse
import collections
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_probe as p   # noqa: E402

# Suffixes stripped to compare stems. Deliberately short and English-generic:
# these are morphological, not a vocabulary of this domain.
_SUFFIX = ("ations", "ation", "ings", "ing", "ions", "ion", "ers", "er",
           "ies", "ed", "es", "s")


def stem(w: str) -> str:
    w = w.lower()
    for s in _SUFFIX:
        if len(w) > len(s) + 2 and w.endswith(s):
            return w[:-len(s)]
    return w


def stems(term: str) -> frozenset:
    return frozenset(stem(x) for x in re.split(r"[-_]", term) if x)


def compatible(a: str, b: str) -> bool:
    """Two stems are the same word if either is a prefix of the other.

    EXACT stem equality was this file's own first defect, and it is the same
    family as everything else on the record: `stem("creation")` -> `cre` while
    `stem("create")` -> `create`, because one suffix rule fired and the other
    did not. `token-creation` therefore did NOT collide with the ratified
    `create-token`, and the checker reported a clean result for the exact case
    §4 names in its own text. Caught by `must_capture` below, which is the
    guard the probe library exists to make cheap.
    """
    return a == b or (len(a) >= 3 and len(b) >= 3
                      and (a.startswith(b) or b.startswith(a)))


def stemsets_match(got: frozenset, want: frozenset) -> bool:
    """Every wanted stem has a compatible partner, one-to-one."""
    if len(got) != len(want):
        return False
    pool = list(got)
    for w in want:
        hit = next((g for g in pool if compatible(g, w)), None)
        if hit is None:
            return False
        pool.remove(hit)
    return True


def classify(hit: str, verb: str) -> str:
    """WHICH KIND of collision -- because one of the three is probably not one.

    REORDERED    `token-creation` vs `create-token`. Unambiguous: §4 fixes the
                 order and this is the other one.
    CONCATENATED `lifegain` vs `gain-life`. §14 Q5 already RULED this out by
                 name.
    INFLECTED    `created-token`, `gains-life` -- SAME order, different form.
                 §4's "bare verb stem everywhere" makes `gains-life` a
                 collision, but `created-token` may be a SUBJECT reference
                 ("a token that was created", cf. §2a's subject prefixes)
                 rather than the verb at all. Reported separately BECAUSE a
                 checker that lumps them would hand back a number nobody
                 should act on -- 297 of the raw 414 are this shape.
    """
    if "-" not in hit:
        return "CONCATENATED"
    order = [stem(x) for x in hit.split("-")]
    want_order = [stem(x) for x in verb.split("-")]
    if len(order) == len(want_order) and all(
            compatible(a, b) for a, b in zip(order, want_order)):
        return "INFLECTED"
    return "REORDERED"


def split_concat(seg: str, wanted: set) -> bool:
    """Does a single unhyphenated segment concatenate the wanted stems?

    `lifegain` is one segment carrying {life, gain}; the hyphen the ratified
    form uses is exactly what was dropped.
    """
    s = seg.lower()
    for a in wanted:
        for b in wanted:
            if a != b and s.startswith(a) and s[len(a):].startswith(b):
                return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    ctx = p.corpus()
    axes = p.active_axes(ctx)
    v4 = p.vocab("4")

    # GUARD D (foundry_probe.must_capture) -- this checker's own known
    # positives, every one a real slug from the live codebook or a ratified
    # §4 form. The exact-stem version of `stemsets_match` failed the first two
    # and reported a clean result for the case §4 names in its own text.
    p.must_capture(
        lambda pair: stemsets_match(stems(pair[0]), stems(pair[1])),
        [(("token-creation", "create-token"), True),
         (("creates-token", "create-token"), True),
         (("gains-life", "gain-life"), True),
         (("life-gained", "gain-life"), True),
         (("create-token", "gain-life"), False),
         (("draw-card", "gain-life"), False)],
        name="synonym stem matcher")

    # Only multi-word ratified verbs can BE rearranged.
    targets = {v: stems(v) for v in v4 if "-" in v and len(stems(v)) > 1}
    if not targets:
        p.fc.halt("no multi-word §4 verbs parsed; the collision test would "
                  "vacuously pass.")

    collisions = collections.defaultdict(list)
    for slug, ax in sorted(axes.items()):
        body = slug.split(":", 1)[1]
        segs = [s for s in body.split("-") if s]
        n = len(ax.get("members") or [])
        for verb, want in targets.items():
            if verb in body:
                continue                       # already the ratified spelling
            hit = None
            # (a) same stems, adjacent, wrong ORDER
            for i in range(len(segs)):
                for j in range(i + 1, min(len(segs), i + len(want)) + 1):
                    if stemsets_match(stems("-".join(segs[i:j])), want):
                        hit = "-".join(segs[i:j])
                        break
                if hit:
                    break
            # (b) same stems CONCATENATED into one segment
            if not hit:
                for s in segs:
                    if split_concat(s, want):
                        hit = s
                        break
            if hit:
                collisions[verb].append((n, slug, hit, classify(hit, verb)))

    print("=" * 78)
    print("SYNONYM COLLISIONS — one mechanic, two live spellings")
    print("=" * 78)
    print(f"  active axes                   {len(axes):>6}")
    print(f"  multi-word §4 verbs tested    {len(targets):>6}")
    print()

    total_axes = total_mem = 0
    for verb in sorted(collisions, key=lambda v: -sum(r[0] for r in collisions[v])):
        rows = sorted(collisions[verb], reverse=True)
        mem = sum(r[0] for r in rows)
        total_axes += len(rows)
        total_mem += mem
        print(f"  RATIFIED §4 VERB: `{verb}`")
        print(f"     {len(rows)} axis/axes spell it otherwise — {mem} members")
        for n, slug, hit, kind in rows:
            print(f"       {n:>4}  {slug:<50} (as `{hit}`)  {kind}")
        print()

    print("-" * 78)
    by_kind = collections.Counter()
    mem_kind = collections.Counter()
    for rows in collisions.values():
        for n, _, _, k in rows:
            by_kind[k] += 1
            mem_kind[k] += n
    print(f"  colliding axes                {total_axes:>6}   members {total_mem:>6}")
    for k in ("REORDERED", "CONCATENATED", "INFLECTED"):
        print(f"    {k:14}              {by_kind[k]:>6}   members {mem_kind[k]:>6}")
    print("  REORDERED + CONCATENATED are collisions on the ratified rulings.")
    print("  INFLECTED needs a READ: a past participle may be a SUBJECT")
    print("  reference (§2a) rather than the §4 verb.")

    print("\n" + "=" * 78)
    print("VERDICT")
    print("=" * 78)
    if collisions:
        print("  ✗ Design goal #1: one mechanic is wearing two names.")
        print("    §4's premise is 'one verb per mechanic, chosen once, used")
        print("    everywhere', and §14 Q5 already RULED on `lifegain` against")
        print("    the ratified `gain-life`. Both rulings exist; nothing")
        print("    enforced them. Renaming is codebook surgery — run it through")
        print("    `foundry_membership_move.py` under the backup law.")
    else:
        print("  ✓ No ratified §4 verb is spelled two ways in the live codebook.")
    return 1 if (collisions and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
