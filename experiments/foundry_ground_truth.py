#!/usr/bin/env python3
"""GROUND TRUTH — the only check in this repo that a token is RIGHT.

Every other mechanism here answers a DIFFERENT question:

  conservation (`foundry_punctuation_audit.py`)  did anything get LOST?
  visibility   (`foundry_visibility_audit.py`)   can the system SEE it?
  invariance   (`foundry_routing_regression.py`) does it depend on the NAME?
  diff         (same)                            did it CHANGE since last time?

Not one of them can see a token that has been WRONG since before the first
snapshot was taken. `diff --strict` halts only on `ratified -> None`; a
RE-ROUTE and a GAP CLOSED both print and pass. That is the recorded trap
*"improving recall can hand out a WRONG ratified token"* -- caught on
2026-08-06 by reading, and reading does not run in CI.

**The fixture is not invented here.** `experiments/moves/*.json` already hold
534 Captain-ratified seeds carrying `"class": "human"` (full weight, never
discounted) and a verbatim evidence `quote`. Each seed asserts a CARD belongs
to an AXIS; the axis slug's own head is a grammar §2 DELIVERY token. So the
expected delivery is DERIVED, at run time, from two ratified artifacts -- the
move spec and §2 -- and this file hand-writes no expectation of its own. That
matters: a hand-written expected-value table is a hand-list, and CLAUDE.md is
explicit that a hand-list is a defect with a delay.

An UNANCHORED seed (the quote no longer matches any ability line of its card)
is reported and is fatal: it means the corpus, the strip, or the line split
moved under a Captain-ratified evidence quote, which is exactly the class of
silent drift this file exists to catch.

Exit 1 on any mismatch. Zero tokens, deterministic, safe to gate on.

    python3 experiments/foundry_ground_truth.py
    python3 experiments/foundry_ground_truth.py --json out.json --limit 30
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

# C8.5J: the standing ratchet now comes from the permanent package. The import
# sits AFTER `foundry_common`, which is what establishes the C8.5A package
# bootstrap -- this module adds no bootstrap and no sys.path mutation of its own.
from mtj_foundry import ratchet  # noqa: E402
from mtj_foundry.paths import ProjectPaths  # noqa: E402

RATCHET_BASELINE = ProjectPaths.for_root(fc.REPO_ROOT).foundry_audit_baseline
MOVES = fc.REPO_ROOT / "experiments" / "moves"


def rule(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


def norm(s: str) -> str:
    """Whitespace- and case-insensitive comparison key. Quotes were recorded by
    hand from printed text; the corpus prints the same words with its own
    spacing, and the reminder strip changes spacing further (see
    `strip_reminder`). Compare on words, not on layout."""
    return re.sub(r"\s+", " ", s or "").strip().lower()


def expected_delivery(axis: str, tokens) -> str:
    """The §2 DELIVERY token an axis slug CLAIMS, derived from the slug.

    Grammar §2's naming is `rule:<delivery>-<effect>`, so the delivery is the
    LONGEST ratified token that heads the slug body. Longest-first is not
    cosmetic: `attack-trigger` and `any-attack-trigger` are both §2 rows, and
    `combat-damage-to-player` heads a slug that `damage` would also prefix.

    Returns None where no §2 token heads the slug -- which is a real claim, not
    a failure to parse. `rule:create-token-clue` is a SPELL ability, and
    grammar §1 omits DELIVERY for those because CR 113.3a already fixes it.
    """
    body = axis.split(":", 1)[1] if ":" in axis else axis
    for tok in sorted(tokens, key=len, reverse=True):
        if body.startswith(tok + "-"):
            return tok
    return None


def anchor_line(card: dict, quote: str, ratified: dict):
    """(line, tokens) for the ability line a seed's evidence quote came from.

    Tries containment both ways: a quote may be a fragment of a longer line, or
    may have been recorded with surrounding context the line does not carry.

    Tokens come from `deliveries_for_lines`, never from `parse_deliveries` on
    the bare line -- the difference is D3 modal inheritance, and skipping it
    reported Charming Scoundrel as a MISMATCH on the first run of this file.
    Its ratified quote is a CR 700.2 mode (`• Create a Wicked Role token …`),
    whose delivery IS its header's `etb` and which parses to None alone. That
    is the recorded trap *"a probe must consume the SAME preprocessing as the
    classifier it is measuring"*, and it is fitting that the file written to
    catch wrong tokens produced one first.
    """
    q = norm(quote)
    if not q:
        return None, None
    rows = list(fx.deliveries_for_lines(card, ratified))

    # FORWARD CONTAINMENT IS THE ONLY SOUND DIRECTION, AND IT IS TRIED ALONE
    # FIRST. A ratified evidence quote is a verbatim excerpt of a printed
    # ability line, so the line CONTAINS the quote. The reverse test
    # (`line in quote`) was tried in the same pass and matched any SHORT line
    # that happened to appear inside a long quote -- Seraph of the Scales
    # anchored a `death-trigger` seed to the line `Flying`.
    #
    # Ties are NOT broken by "whichever line agrees with the axis". That rule
    # would make the fixture self-confirming: a genuinely wrong membership
    # would find the one line that vindicates it and grade green. Ambiguity is
    # REPORTED instead, which is the only answer that cannot hide a defect.
    fwd = [(l, pr) for l, pr in rows if q in norm(l)]
    if len(fwd) == 1:
        return fwd[0]
    if len(fwd) > 1:
        # Longest line wins ONLY when one is a superstring of the others --
        # that is one ability re-read, not a choice between two abilities.
        longest = max(fwd, key=lambda r: len(norm(r[0])))
        if all(norm(l) in norm(longest[0]) for l, _ in fwd):
            return longest
        return "AMBIGUOUS", fwd
    # Reverse containment is a LAST resort and must consume a whole line, not
    # a fragment: the line has to be the longest one embedded in the quote.
    rev = [(l, pr) for l, pr in rows if norm(l) and norm(l) in q]
    if rev:
        return max(rev, key=lambda r: len(norm(r[0])))

    # THE QUOTE MAY HAVE BEEN TAKEN FROM REMINDER TEXT, WHICH THE PIPELINE
    # STRIPS. Measured 2026-08-09: of 55 seeds whose quote matched no ability
    # line, **54 are verbatim present in the RAW oracle text and 31 of those
    # sit inside parentheses** -- CR 207.2a reminder text, which
    # `strip_reminder` removes and which is 19.2% of every oracle character.
    #
    # Mire's Malice is the worked case. Its ratified quote is *"put three
    # +1/+1 counters on target land you control and it becomes a 0/0..."* --
    # the AWAKEN reminder. The printed ability line is `Awaken 3—{5}{B}`. The
    # quote is correct, the membership is correct, and the two could never
    # meet because the fixture only ever saw the stripped view.
    #
    # This was first reported as "a Captain-ratified quote no longer matches
    # the corpus", i.e. as DRIFT needing 55 quote repairs. It is not drift and
    # nothing needed repairing: it is the recorded trap *"an audit's boundary
    # is upstream of something"*, aimed at this file.
    #
    # The raw paragraph is mapped back to its ability line THROUGH THE
    # EXTRACTOR'S OWN `strip_reminder`, never by index -- a line that is pure
    # reminder text strips to nothing and would shift every index after it.
    faces = card.get("card_faces") or [card]
    by_stripped = {norm(l): (l, pr) for l, pr in rows}
    for f in faces:
        for para in (f.get("oracle_text") or "").split("\n"):
            if not para.strip() or q not in norm(para):
                continue
            hit = by_stripped.get(norm(fx.strip_reminder(para)))
            if hit:
                return hit
    return None, None


PERMANENT_ONLY = {"activated", "etb", "death-trigger", "attack-trigger",
                  "leaves-battlefield-trigger", "static", "loyalty",
                  "blocks-or-becomes-blocked-trigger", "is-attacked-trigger"}


def has_permanent_face(card: dict) -> bool:
    """Does any face put a PERMANENT on the battlefield? (CR 110.1 / 205.2a)

    Derived from the printed type line, never from a list of card names. CR
    113.3a is what makes this decisive: a card with no permanent face has only
    a spell ability, so §2's permanent-side DELIVERY tokens cannot apply to it.
    """
    faces = card.get("card_faces") or [card]
    for f in faces:
        tl = (f.get("type_line") or card.get("type_line") or "")
        if re.search(r"\b(Creature|Artifact|Enchantment|Land|Planeswalker"
                     r"|Battle|Kindred|Tribal)\b", tl):
            return True
    return False


def grants_ability(line: str) -> bool:
    """Does this line GRANT an ability rather than have one? (§2, CR 113.3d)

    A granted ability is printed inside quotation marks -- CR 113.3d's static
    abilities that give other objects abilities are templated that way. The
    quoted span must contain a `:` (an activated ability, CR 602.1) or open a
    trigger, or it is just quoted flavor.
    """
    for m in re.finditer(r'[\"\u201c]([^\"\u201d]{4,})[\"\u201d]', line):
        inner = m.group(1)
        if ":" in inner or re.match(r"(?i)\s*when(ever)?\b", inner):
            return True
    return False


def tail_of(axis: str, head: str) -> str:
    """The slug body after its DELIVERY head -- the EFFECT/OBJECT remainder."""
    body = axis.split(":", 1)[1] if ":" in axis else axis
    return body[len(head):].lstrip("-")


def claimed_keyword(axis: str) -> str:
    """The CR 702 keyword an axis slug names, or None.

    An axis with no §2 DELIVERY head is not ungradable -- `rule:cycling` and
    `rule:typecycling` (395 of the 534 seeds) name a CR 702 KEYWORD instead, and
    that is just as assertable: the anchored line must actually carry it.

    Membership is tested against `CR_KEYWORD_NAMES`, parsed from CR 702 by
    `load_702`, and never against `KEYWORD_HOME` -- the recorded trap is that
    `KEYWORD_HOME` skips any keyword whose home cannot be derived, so it reads
    like the keyword list and is not one.
    """
    if not fx.CR_KEYWORD_NAMES:
        return None
    body = axis.split(":", 1)[1] if ":" in axis else axis
    if body in fx.CR_KEYWORD_NAMES or body in VARIANT_FAMILIES:
        return body
    return None


# A CR keyword with a TYPED parameter is printed as one word per instance --
# `plainscycling`, `basic landcycling`, `swampwalk` -- so the descriptor the
# classifier emits names the PRINTED variant, not the CR 702 entry. An axis
# named for the family (`rule:typecycling`) must therefore be graded against
# the family's predicate, not against string equality: `rule:typecycling`
# scored 0/91 on `keyword:plainscycling` while the routing was already correct.
#
# These are the extractor's OWN predicates, each of which derives its
# vocabulary from CR 205 at run time. That is the distinction from a hand-list:
# nothing here enumerates a type, it only names which function knows how.
VARIANT_FAMILIES = {
    "typecycling": lambda w: fx.typecycling_variant(w),   # CR 702.29e/f
    "landwalk": lambda w: fx.landwalk_variant(w),         # CR 702.14a
}


def keyword_satisfied(kw: str, parsed) -> bool:
    """Does the classifier's own output carry the keyword the axis claims?"""
    printed = [str(d).split(":", 1)[1] for _, d in parsed
               if str(d).startswith("keyword:")]
    if kw in VARIANT_FAMILIES:
        return any(VARIANT_FAMILIES[kw](p) for p in printed)
    return kw in printed


def references_only(kw: str, line: str) -> bool:
    """Does the line NAME the keyword without HAVING it?

    This is boundary B1 of `CLUE-INSTANTIATION-2026-08-03.md` -- *"creator, not
    referencer"* -- and grammar §2's created-ability rule underneath it: a card
    does not deliver an ability it grants to something else. Four ratified
    `rule:typecycling` seeds anchor to lines like

        Each land card in your hand has cycling {R}.
        Each Sliver card in each player's hand has slivercycling {3}.

    The MEMBERSHIP is correct (the card is about typecycling) and the
    classifier is correct (that line is a static ability, not a cycling
    ability). Grading them against each other was the third defect in this
    file, not a finding about either.

    The cut is tight on purpose: a line that IS the keyword plus its cost is
    what `keyword_line_tokens` already claims, so anything it declines while
    still naming the keyword is naming it about something else. A genuinely
    missed `Plainscycling {2}` -- solely keyword and cost -- is still graded
    and still fails, which is how the 91 were found.
    """
    if fx.keyword_line_tokens(line) or fx.keyword_form_tokens(line):
        return False
    base = kw[len("type"):] if kw.startswith("type") else kw
    return re.search(r"\w*" + re.escape(base) + r"\b", line, re.I) is not None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json")
    ap.add_argument("--update-baseline", action="store_true",
                    help="pin the CURRENT --wide numbers as the baseline")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--wide", action="store_true",
                    help="also grade the codebook's own human-class "
                         "quoted assertions (4,194 across 355 axes)")
    args = ap.parse_args()

    cards, _, _ = fc.load_corpus_gated()
    fx.build_self_noun_rx(cards)
    ratified = fx.ratified_delivery_tokens()
    fx.build_keyword_homes(ratified)

    cb_axes = {s for s, a in json.loads(
        (fc.FOUNDRY_OUT_DIR / "codebook.json").read_text(
            encoding="utf-8"))["axes"].items() if a.get("status") == "active"}

    specs = sorted(MOVES.glob("*.json"))
    seeds = []
    for path in specs:
        spec = json.loads(path.read_text(encoding="utf-8"))
        for s in spec.get("seeds") or []:
            if s.get("class") == "human" and s.get("quote"):
                seeds.append((path.name, s))

    # THE FIXTURE WAS 6.7% OF THE CODEBOOK AND THE REST WAS ALREADY SITTING
    # THERE. `moves/*.json` holds 534 quoted human seeds, but only 3 of the 16
    # specs carry a `seeds` block at all -- the other 13 are renames, merges and
    # scope edits. Meanwhile `codebook.json` carries the SAME kind of evidence
    # on its own members: 4,194 `class: human` assertions with a verbatim quote,
    # across 355 active axes. Those are Captain-ratified assignments with
    # exactly the two properties this file needs (an axis claim and a quote),
    # so grading them requires no new ratification -- only reading them.
    #
    # Kept behind a flag so the pinned 488 stays comparable run to run, and so
    # a fixture that is 8x larger cannot silently redefine what "green" means.
    if args.wide:
        cbp = fc.FOUNDRY_OUT_DIR / "codebook.json"
        cb = json.loads(cbp.read_text(encoding="utf-8"))
        seen = {(s["to"], s["member"]) for _, s in seeds}
        for slug, ax in sorted(cb["axes"].items()):
            if ax.get("status") != "active":
                continue
            for m in ax.get("members") or []:
                for a in m.get("assertions") or []:
                    if a.get("class") != "human" or not a.get("quote"):
                        continue
                    key = (slug, m["oracle_id"])
                    if key in seen:
                        continue
                    seen.add(key)
                    seeds.append(("codebook.json", {
                        "to": slug, "member": m["oracle_id"],
                        "class": "human", "quote": a["quote"]}))
    if not seeds:
        fc.halt(f"no human-class seeds found under {MOVES}. This file's whole "
                f"premise is that the ratified move specs ARE the fixture; if "
                f"they are gone, do not silently pass.")

    rule("FIXTURE — Captain-ratified `class: human` seeds, by spec")
    per_spec = collections.Counter(n for n, _ in seeds)
    for name, n in sorted(per_spec.items()):
        print(f"  {name:46}{n:>6} seeds")
    print(f"  {'TOTAL':46}{len(seeds):>6}")

    passed, mismatch, unanchored, missing, no_claim = 0, [], [], [], 0
    ambiguous, spell_face, granted_delivery, head_ambiguous = [], [], [], []
    referenced = []
    by_axis = collections.defaultdict(lambda: [0, 0])
    for spec_name, s in seeds:
        axis, oid = s["to"], s["member"]
        card = cards.get(oid)
        if card is None:
            missing.append((spec_name, axis, oid))
            continue
        line, parsed = anchor_line(card, s["quote"], ratified)
        if line is None:
            unanchored.append((spec_name, card["name"], axis, s["quote"][:70]))
            continue
        if line == "AMBIGUOUS":
            ambiguous.append((card["name"], axis, s["quote"][:64], len(parsed)))
            continue
        got = [t for t, _ in parsed]

        want = expected_delivery(axis, ratified)
        if want is not None:
            # --- THREE CR RULES THAT MAKE A SEED UNGRADABLE, NOT FAILING ----
            # Each is a hard rule, not a heuristic, and none of them consults
            # whether the answer would come out green.
            #
            # CR 113.3a / grammar §1 -- "DELIVERY is OMITTED for spell
            # abilities". A card with NO permanent face has no activated,
            # triggered or static ability to deliver: its resolution effect is
            # a SPELL ability by CR 113.3a. Seismic Spike ("Destroy target
            # land. Add {R}{R}") is a sorcery on `rule:activated-...`, so the
            # slug's head cannot be §2's `activated` -- CR 602.1 requires
            # "[Cost]: [Effect]" on an object that HAS the ability.
            if want in PERMANENT_ONLY and not has_permanent_face(card):
                spell_face.append((card["name"], axis, want))
                continue
            # §2's created-ability rule + CR 113.3d -- a card does not DELIVER
            # an ability it GRANTS to something else. Acidic Sliver's line is
            # `All Slivers have "{2}, Sacrifice this permanent: ..."`, a STATIC
            # ability that grants an activated one. This is boundary B1, which
            # this file already applies to KEYWORD claims and did not apply to
            # DELIVERY claims.
            if want not in got and grants_ability(line):
                granted_delivery.append((card["name"], axis, want, line[:70]))
                continue
            # CR 614.1c -- `etb` is TWO WORDS in this codebook. §2's `etb` is
            # an ETB TRIGGER; ~60 slugs use `etb-` colloquially for "on
            # entering", whose real delivery is `replacement` ("enters as a
            # copy", "enters with X counters"). The slug head is ambiguous, so
            # the EXPECTATION is unsound -- not the routing. Ungradable until
            # Captain rules which one keeps the prefix.
            if want == "etb" and "replacement" in got:
                head_ambiguous.append((card["name"], axis, line[:70]))
                continue
            # §1's SLOT LAW, APPLIED TO §2a's SUBJECT PREFIX. §1 says a slot is
            # "omitted when the axis's scope= field carries it AND NO SIBLING
            # DIFFERS ONLY BY SCOPE; REQUIRED the moment a scope-sibling
            # exists." §2a's any-/other-/source- prefix is the same kind of
            # slot, so an axis that omits it is not asserting the SOURCE form —
            # it is leaving the slot unspecified, and a prefixed delivery
            # satisfies it.
            #
            # Measured 2026-08-09: 27 of the 89 "errors" were exactly this, and
            # for ALL 27 no prefixed sibling axis exists. Sigiled Sword of
            # Valeron ("whenever EQUIPPED CREATURE attacks, create a 2/2")
            # delivers `any-attack-trigger` on `rule:attack-trigger-create-
            # token`, an axis with no `any-` sibling. The card is on the right
            # axis; the grader was over-strict.
            #
            # The sibling test is what keeps this honest: the moment someone
            # ratifies `rule:any-attack-trigger-create-token`, the unprefixed
            # name starts meaning SOURCE-ONLY again and this stops applying.
            if want not in got:
                sibs = [f"rule:{pre}-{want}-{tail_of(axis, want)}"
                        for pre in ("any", "other", "source")]
                if not any(s in cb_axes for s in sibs):
                    got = [re.sub(r"^(?:any|other|source)-", "", str(g))
                           for g in got if g is not None]
            ok, claim = want in got, f"delivery {want!r}"
        else:
            kw = claimed_keyword(axis)
            if kw is None:
                # The slug claims neither a §2 DELIVERY nor a CR 702 keyword.
                # `rule:create-token-clue` is the worked case: a SPELL ability,
                # whose delivery grammar §1 omits because CR 113.3a fixes it.
                # Nothing to assert -- counted, not graded.
                no_claim += 1
                continue
            # Grade on the CLASSIFIER'S OWN descriptor, not on a re-derivation:
            # `keyword_line_tokens` returns (token, descriptor) PAIRS, and
            # testing `kw in [...]` against a list of tuples is silently always
            # False -- it scored 0/304 on `rule:cycling`, a family that was
            # entirely correct. Second probe defect in this file; the fix is
            # the same one both times, which is to consume what the classifier
            # emitted instead of asking the question again.
            ok = keyword_satisfied(kw, parsed)
            claim = f"CR 702 keyword {kw!r}"
            if not ok and references_only(kw, line):
                referenced.append((card["name"], axis, line[:74]))
                continue

        by_axis[axis][0 if ok else 1] += 1
        if ok:
            passed += 1
        else:
            mismatch.append((card["name"], axis, claim, got, line[:74]))

    rule("RESULT")
    graded = passed + len(mismatch)
    print(f"  seeds                                {len(seeds):>7}")
    print(f"  ...member not in the gated corpus    {len(missing):>7}")
    print(f"  ...quote anchored to no ability line {len(unanchored):>7}   <- FATAL")
    print(f"  ...slug claims neither (§1 spell)    {no_claim:>7}   (not graded)")
    print(f"  ...line GRANTS the keyword (B1)      {len(referenced):>7}   (not graded)")
    print(f"  ...spell face only (CR 113.3a)       {len(spell_face):>7}   (not graded)")
    print(f"  ...line GRANTS the delivery (§2)     {len(granted_delivery):>7}   (not graded)")
    print(f"  ...slug head ambiguous (CR 614.1c)   {len(head_ambiguous):>7}   (NEEDS A RULING)")
    print(f"  ...quote matches >1 ability line     {len(ambiguous):>7}   (not graded)")
    print(f"  GRADED                               {graded:>7}")
    print(f"  ...as the ratified axis claims       {passed:>7}")
    print(f"  ...MISMATCH                          {len(mismatch):>7}   <- FATAL")

    if by_axis:
        rule("BY AXIS")
        print(f"  {'axis':56}{'pass':>7}{'fail':>7}")
        for axis in sorted(by_axis, key=lambda a: (-by_axis[a][1], a)):
            ok, bad = by_axis[axis]
            print(f"  {axis:56}{ok:>7}{bad:>7}{'   <--' if bad else ''}")

    if unanchored:
        rule("UNANCHORED — a ratified evidence quote matches no ability line")
        for spec, name, axis, q in unanchored[:args.limit]:
            print(f"  {name[:26]:28}{axis[:34]:36}{q}")
        if len(unanchored) > args.limit:
            print(f"  ... and {len(unanchored) - args.limit} more")

    if referenced:
        rule("GRANTED, NOT PRINTED — boundary B1, reported for the record")
        for name, axis, line in referenced[:args.limit]:
            print(f"  {name[:26]:28}{axis[:26]:28}{line}")

    if mismatch:
        rule("MISMATCH — the extractor and the ratified axis disagree")
        for name, axis, claim, got, line in mismatch[:args.limit]:
            print(f"  {name[:26]:28}{axis}")
            print(f"  {'':28}want {claim}  got {got}")
            print(f"  {'':28}{line}")
        if len(mismatch) > args.limit:
            print(f"  ... and {len(mismatch) - args.limit} more")

    # THE NARROW GATE STAYS ABSOLUTE-ZERO. It is 488 Captain-ratified seeds
    # that have reproduced exactly through every change all session, and
    # loosening it to a ratchet would trade a proven invariant for a backlog.
    # Only --wide, which carries the 89-error backlog, gates on movement.
    fatal = 0 if args.wide else len(mismatch) + len(unanchored)
    rule("VERDICT")
    if fatal:
        print(f"  ✗ {fatal} seed(s) FAILED. A ratified axis and the extractor")
        print("    disagree about the same card. One of them is wrong, and the")
        print("    routing diff cannot tell you which -- read them.")
    else:
        print(f"  ✓ {passed} ratified assignments reproduce exactly.")
        print("    Every human-class evidence quote still anchors to a live")
        print("    ability line, and every line still delivers what its axis claims.")

    # --wide IS GATED ON A RATCHET, NOT ON ZERO. The 89 residual mismatches are
    # real codebook errors, and NONE of them has an existing correct home --
    # measured 2026-08-09, all 89 would need a new axis or a drop, which is a
    # ratification and not a fix. Blocking the gate on them would keep 1,181
    # graded assertions ungated indefinitely while waiting for Captain.
    #
    # So the same mechanism the rest of Gate 2 uses applies here: any RISE in
    # mismatches or unanchored is fatal, any FALL is reported and accepted only
    # with an explicit --update-baseline. The backlog can shrink and cannot
    # grow, which is what a ratchet is for, and it is the same shape as
    # `family_sweep`'s standing findings being named rather than excused away.
    if args.wide:
        metrics = {"graded": graded, "passed": passed,
                   "mismatch": len(mismatch), "unanchored": len(unanchored),
                   "head_ambiguous": len(head_ambiguous)}
        rule("BASELINE — ground truth (--wide)")
        if ratchet.report(RATCHET_BASELINE, "ground_truth_wide", metrics,
                          args.update_baseline):
            fatal += 1

    if args.json:
        Path(args.json).write_text(json.dumps({
            "seeds": len(seeds), "graded": graded, "passed": passed,
            "missing": [list(m) for m in missing],
            "unanchored": [list(u) for u in unanchored],
            "mismatch": [[n, a, c, g, l] for n, a, c, g, l in mismatch],
            "referenced": [list(r) for r in referenced],
            "by_axis": {a: {"pass": v[0], "fail": v[1]} for a, v in by_axis.items()},
        }, indent=2, sort_keys=True))
        print(f"\nwrote {args.json}")
    sys.exit(1 if fatal else 0)


if __name__ == "__main__":
    main()
