#!/usr/bin/env python3
"""DET census of CR 702 keyword abilities by ABILITY CLASS -- zero tokens.

WHY THIS EXISTS
---------------
Captain, 2026-08-03: *"check the CR and how keywords have different
properties. static versus trigger keywords."*

This is load-bearing for the delivery-vocabulary batch. Grammar §2 is explicit
that DELIVERY is determined by ability STRUCTURE, never by effect words -- and
for a keyword ability the structure is not a judgement call, it is stated
verbatim by the CR in the keyword's own `702.Na` sub-rule:

    702.6a  "Equip is an ACTIVATED ability of Equipment cards."
    702.9a  "Flying is an EVASION ability."
    702.108a "Prowess is a TRIGGERED ability."

So the delivery slot of every CR 702 keyword is DERIVABLE, exactly the way
`cycling` was derived (CR 702.29a -> activated -> §2's `activated` token, no
new vocabulary needed). This tool derives all 193 of them at once instead of
one ruling at a time.

WHAT IT DOES NOT DO
-------------------
It judges nothing and writes nothing to the codebook. A keyword whose 702.Na
line does not state a class is reported as UNSTATED and listed by name -- never
assigned to the nearest-looking class. Per house style it halts loudly if the
CR file or the 702 section cannot be read.

THE CLASSES ARE NOT INVENTED
----------------------------
Class words are discovered from the CR's own "X is a ___ ability" sentences,
then validated against CR 113.3a-d -- which is the CR's authoritative
enumeration of the four ability classes, parsed at run time rather than
hand-listed. A discovered word outside it is reported, never assigned: 702.11b's
"a 'hexproof from [quality]' ability is a hexproof ability" is self-reference,
not a class claim. `--unstated` prints the residual so the gap stays visible.

USAGE
  python3 experiments/foundry_cr702_classes.py
  python3 experiments/foundry_cr702_classes.py --unstated
  python3 experiments/foundry_cr702_classes.py --json out.json
"""
import re
import sys
import json
import argparse
import collections
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402

# Deliberate absolute path: CLAUDE.md names the CR as one of exactly two
# site-resident documents this repo reads by absolute path.
CR_PATH = Path.home() / "Projects" / "mtjawnny.github.io" / "docs" / "mtg-comprehensive-rules.md"

HEADER = re.compile(r"^702\.(\d+)\.\s+(.+?)\s*$")
SUBRULE = re.compile(r"^702\.(\d+)([a-z])\s+(.*)$")
# CR 205 is the authority on the type words CR 702.14a's "[type]walk" template
# composes from. Parsed at run time, never hand-listed -- same discipline as
# CLASS_RULE above and as parsing grammar §2's token table.
TYPE_RULES = {
    "card_types": re.compile(r"^205\.2a The card types are (.+?)\. See", re.M),
    "land_types": re.compile(r"^205\.3i .*?The land types are (.+?)\. Of that", re.M),
    "supertypes": re.compile(r"^205\.4a .*?The supertypes are (.+?)\.\s*$", re.M),
    # EVERY subtype list is enumerated by the CR, in one uniform sentence
    # shape, and CR 205.3r closes the set by naming the four card types that
    # have NO subtypes ("Phenomenon cards, scheme cards, vanguard cards, and
    # conspiracy cards have no subtypes"). An earlier comment in this project
    # claimed the CR "does not enumerate them in one place" and used a corpus
    # harvest instead -- that claim was simply wrong, and CR 205.3g-q is the
    # refutation. A harvest can only ever contain what the gated corpus holds.
    "artifact_types": re.compile(r"^205\.3g .*?The artifact types are (.+?)\.\s*$", re.M),
    "enchantment_types": re.compile(r"^205\.3h .*?The enchantment types are (.+?)\.\s*$", re.M),
    "planeswalker_types": re.compile(r"^205\.3j .*?The planeswalker types are (.+?)\.\s*$", re.M),
    "spell_types": re.compile(r"^205\.3k .*?The spell types are (.+?)\.\s*$", re.M),
    # 205.3m states the ONE two-word type separately, then the rest.
    "creature_types": re.compile(r"^205\.3m .*?All other creature types are one word long: (.+?)\.\s*$", re.M),
    "creature_types_multiword": re.compile(r"^205\.3m .*?creature type is two words long: (.+?)\. All other", re.M),
    "planar_types": re.compile(r"^205\.3n .*?The planar types are (.+?)\.\s*$", re.M),
    "dungeon_types": re.compile(r"^205\.3p .*?That dungeon type is (.+?)\.\s*$", re.M),
    "battle_types": re.compile(r"^205\.3q .*?That battle type is (.+?)\.\s*$", re.M),
}
# CR 205.3g/h names its members with cross-references -- "Attraction (see rule
# 717)", "Aura (see rule 303.4)". Strip them before splitting, or the type is
# `attraction (see rule 717)`.
_CR_XREF = re.compile(r"\s*\((?:see|as in)[^)]*\)")
SUBTYPE_KEYS = ("artifact_types", "enchantment_types", "land_types",
                "planeswalker_types", "spell_types", "creature_types",
                "creature_types_multiword", "planar_types", "dungeon_types",
                "battle_types")
# CR 113.3a-d is the authority on which ability classes EXIST. Derived at run
# time, never hand-listed -- same discipline as parsing §2's token table.
CLASS_RULE = re.compile(r"^113\.3([a-d])\s+([A-Za-z-]+) abilit", re.M)

# "<Keyword> is a/an <class> ability" -- the CR's own sentence shape.
CLASS_SENT = re.compile(
    r"\bis (?:a|an) ((?:[a-z-]+ ){0,2}?)ability\b", re.I)

# §2 DELIVERY token implied by each CR class word, where the CR class maps onto
# a slot value that grammar §2 already ratifies. Anything not here is reported,
# never guessed.
CLASS_TO_DELIVERY = {
    "activated": "activated",
    "triggered": "triggered -> needs its own §2 trigger token",
    "static": "static",
    "spell": "(none -- spell ability, §2 omits DELIVERY)",
}

# Two CR class words are SUBCLASSES of static, and the CR says so itself. These
# are not my inference -- each carries the quote that makes it CR-stated.
SUBSUMES = {
    "evasion": ("static", "CR 509.1b",
                "an evasion ability (a static ability an attacking creature "
                "has that restricts what can block it)"),
    "characteristic-defining": ("static", "CR 604.3",
                "Some static abilities are characteristic-defining abilities."),
}

# "X is a keyword ability" is the CR's GENERIC phrase, not a class claim -- so
# these fall through to UNSTATED rather than inventing a "keyword" class.
# CR 702.169a proves it: Solved's text "represent[s] a static ability, a
# triggered ability, or an activated ability" -- class-polymorphic by design.
NOT_A_CLASS = {"keyword"}

# CR 702.1 is the section preamble, not a keyword.
PREAMBLE_RULE = 1

# Populated from CR 113.3a-d at load time.
CR_CLASSES = set()


def load_702(path: Path) -> dict:
    if not path.exists():
        fc.halt(f"CR markdown not found at {path}. CLAUDE.md names this as one "
                f"of two documents read by absolute path; it must exist.")
    text = path.read_text(encoding="utf-8", errors="strict")
    lines = text.splitlines()

    global CR_CLASSES
    CR_CLASSES = {m.group(2).lower() for m in CLASS_RULE.finditer(text)}
    if len(CR_CLASSES) != 4:
        fc.halt(f"CR 113.3a-d should enumerate exactly 4 ability classes; "
                f"parsed {sorted(CR_CLASSES)}. Fix the parser, do not "
                f"fall back to a remembered list.")

    keywords = {}     # number -> {"name":..., "subrules": {letter: text}}
    for raw in lines:
        m = HEADER.match(raw)
        if m:
            keywords.setdefault(int(m.group(1)),
                                {"name": m.group(2).strip(), "subrules": {}})
            continue
        m = SUBRULE.match(raw)
        if m:
            num = int(m.group(1))
            keywords.setdefault(num, {"name": None, "subrules": {}})
            keywords[num]["subrules"][m.group(2)] = m.group(3).strip()

    if not keywords:
        fc.halt("Parsed zero CR 702 keywords. The CR file's section 702 "
                "formatting has changed; fix the parser, do not fall back.")
    return keywords


def type_vocabulary(path: Path = CR_PATH) -> dict:
    """Every CR 205 type list -> sets, read from the CR at run time.

    Card types (205.2a), supertypes (205.4a), and ALL TEN subtype lists
    (205.3g-q). Required by CR 702.14a's landwalk template, which is stated as
    a GRAMMAR over these lists rather than as a list of keyword names, and by
    the self-reference noun set, which needs "this <subtype>" to be complete.

    `subtypes` is the union of the ten, provided so a caller never has to
    remember which ten they are."""
    if not path.exists():
        fc.halt(f"CR markdown not found at {path}.")
    text = path.read_text(encoding="utf-8", errors="strict")
    out = {}
    for key, rx in TYPE_RULES.items():
        m = rx.search(text)
        if not m:
            fc.halt(f"Could not parse {key} from the CR (rule 205). The CR's "
                    f"wording has changed; fix the parser, do not fall back to "
                    f"a remembered list.")
        # The CR writes these lists with an OXFORD COMMA -- "…, scheme, and
        # vanguard." Splitting on `,\s*` first consumed the comma and left the
        # conjunction attached, so the final item of EVERY list parsed as
        # garbage: `and vanguard`, `and world`, `and urza's`. The last real
        # card type, supertype and land type were therefore all MISSING.
        #
        # And the count guard below did not catch it, because the junk token
        # kept the count correct -- 15 card types, of which one was `and
        # vanguard` and `vanguard` itself absent. **A guard that counts is
        # satisfied by the defect it exists to catch.** So the guard now
        # asserts CONTENT, not cardinality: a known-last member of each list,
        # which is exactly the item this bug class destroys.
        words = re.split(r",\s*(?:and\s+)?|\s+and\s+", _CR_XREF.sub("", m.group(1)))
        vals = {w.strip().strip(".").lower() for w in words if w.strip()}
        # THE CR PRINTS A CURLY APOSTROPHE (U+2019); SCRYFALL TYPE LINES PRINT
        # A STRAIGHT ONE. `Urza’s` from CR 205.3i never equals `Urza's` from a
        # type line, and the same mismatch hits C’tan, Shi’ar, Serra’s Realm,
        # Bolas’s Meditation Realm and Outside Mutter’s Spiral. Landwalk has
        # been composing over `urza’s` and could never match a printed
        # `Urza'swalk`. Both forms are emitted -- a mechanical transformation
        # of a CR-parsed value, not a hand-added member.
        vals |= {w.replace("’", "'") for w in vals if "’" in w}
        out[key] = vals
    out["subtypes"] = set().union(*(out[k] for k in SUBTYPE_KEYS))
    for key, least, tail in (("card_types", 15, "vanguard"),
                             ("land_types", 17, "urza’s"),
                             ("supertypes", 5, "world"),
                             ("artifact_types", 20, "vibranium"),
                             ("enchantment_types", 12, "shrine"),
                             ("planeswalker_types", 80, "zariel"),
                             ("spell_types", 5, "trap"),
                             ("creature_types", 250, "zubera"),
                             ("planar_types", 60, "zhalfir"),
                             ("dungeon_types", 1, "undercity"),
                             ("battle_types", 1, "siege"),
                             ("creature_types_multiword", 1, "time lord")):
        if len(out[key]) < least:
            fc.halt(f"parsed only {len(out[key])} {key} from CR 205 "
                    f"(expected >= {least}): {sorted(out[key])}")
        if tail not in out[key]:
            fc.halt(f"CR 205 {key} parsed without its LAST member {tail!r} — "
                    f"the Oxford-comma split has regressed. Got: "
                    f"{sorted(out[key])}")
        if any(w.startswith("and ") for w in out[key]):
            fc.halt(f"CR 205 {key} contains a conjunction fragment: "
                    f"{sorted(w for w in out[key] if w.startswith('and '))}")
    return out


def classify(kw: dict) -> tuple:
    """Return (classes, evidence) read from the keyword's own sub-rules, where
    `classes` is the ORDERED list of every distinct class the CR states for it.

    Multi-class keywords are real and must not be collapsed to the first hit.
    CR 702.62a: "Suspend is a keyword that represents three abilities. The
    first is a static ability... The second and third are triggered abilities."
    Reporting that as plain "static" would be exactly the approximation this
    tool exists to refuse. Only the CR's literal wording is used."""
    classes, evidence, unrecognised = [], {}, kw.setdefault("_unrecognised", {})
    for letter in sorted(kw["subrules"]):
        body = kw["subrules"][letter]
        for sentence in re.split(r"(?<=\.)\s+", body):
            for m in CLASS_SENT.finditer(sentence):
                words = m.group(1).strip().split()
                if not words:
                    continue
                word = words[-1].lower()
                if word in NOT_A_CLASS:
                    continue     # generic phrasing, not a class claim
                if word not in CR_CLASSES and word not in SUBSUMES:
                    # CR 113.3 does not enumerate this as an ability class.
                    # e.g. 702.11b's "a 'hexproof from [quality]' ability is a
                    # hexproof ability" is self-reference, not a class claim.
                    unrecognised.setdefault(word, sentence.strip())
                    continue
                if word not in classes:
                    classes.append(word)
                    evidence[word] = sentence.strip()
    return classes, evidence


# The CR also states multiplicity in prose ("represents three abilities"). Used
# only to WARN that a single-class read may be incomplete -- never to assign.
MULTI_HINT = re.compile(
    r"\brepresents? (two|three|four) abilities\b|"
    r"\bThe (second|third) (is|are)\b", re.I)


# The CR spells out most keywords as templated text: `"Prowess" means "Whenever
# you cast a noncreature spell, ..."`. That quote is the keyword's ACTUAL
# printed shape, so its DELIVERY slot is derivable by running it through the
# same extractor every card goes through -- no per-keyword ruling required.
MEANS = re.compile(r"means\s+[“\"]([^”\"]+)[”\"]")


def effective_classes(kw: dict) -> list:
    """The keyword's CR-stated ability classes after the CR's own rollups."""
    classes, _ev = classify(kw)
    out, seen = [], set()
    for c in classes:
        e = SUBSUMES.get(c, (None,))[0] or c
        if e not in seen:
            seen.add(e)
            out.append(e)
    return out


def find_home(kw: dict, ratified: dict) -> tuple:
    """(delivery_token, descriptor, cr_templated_text) for one keyword, or
    (None, None, None) when the CR states no templated text to parse.

    §2b, verbatim: *"A keyword's CLASS and its TRIGGER EVENT are separate
    questions. The class says WHICH SLOT; the templated text says which token
    in that slot."* This used to let the templated text decide the slot too,
    and for the `activated` class that was wrong in both directions:

      * DROPPED 6 keywords. CR 702.6a's templated text opens `"[Cost]: Attach
        this permanent…"` -- a literal placeholder where a card prints a real
        cost. `parse_delivery`'s activated branch requires a recognisable cost
        left of the colon ({mana}, sacrifice, discard, tap, …), so `[Cost]`
        matched nothing and Equip fell to `spell-or-static`. Cycling routed
        only because its cost half happens to print the word "Discard".
      * MISROUTED Unearth. CR 702.84a states `activated`, but its templated
        EFFECT says "exile it instead", so the text parsed as `replacement` --
        which §2's created-ability rule already forbids: the delivery belongs
        to the ability that CREATES the replacement effect, not to it.

    So for a keyword the CR states as `activated` and nothing else, the slot is
    CR 113.3b's "[Cost]: [Effect]" outright and the templated text is not
    consulted.

    The other classes are deliberately untouched. A `static` keyword whose
    templated text is a CR 614 replacement still routes to `replacement`,
    because the CR chains the two rather than opposing them -- 113.3d: *"Static
    abilities ... create continuous effects"*; 614.1: *"Some continuous effects
    are replacement effects."* So `replacement` is the MORE SPECIFIC reading of
    a static keyword, not a contradiction of it, and §2b's ratified table
    already routes 16 keywords (Amplify, Bloodthirst, Dredge, Madness, Modular,
    Riot …) exactly that way. Widening this to "the class always wins" would
    have destroyed all 16."""
    import foundry_shape_extractor as fse
    text = None
    for letter in sorted(kw["subrules"]):
        m = MEANS.search(kw["subrules"][letter])
        if m:
            text = m.group(1).strip()
            break
    if effective_classes(kw) == ["activated"]:
        if "activated" not in ratified:
            fc.halt("grammar §2 no longer ratifies the `activated` DELIVERY "
                    "token, which CR 113.3b's ability class requires. Refusing "
                    "to route CR-stated activated keywords anywhere else.")
        return "activated", "cr-class:activated (702.Na)", text
    if text is None:
        return None, None, None
    tok, desc = fse.parse_delivery(text, ratified, None)
    return tok, desc, text


def cmd_homes(rows: list, keywords: dict) -> None:
    """Captain, 2026-08-03: 'keywords that are attack triggers should go into
    When this creature attacks rulings. then look at other keywords and find
    them appropriate homes.'

    Right, and it makes the 44-triggered-keyword 'gap' mostly illusory: a
    triggered keyword does not need NEW delivery vocabulary, it needs to be
    routed to the token its own CR templated text already resolves to."""
    import foundry_shape_extractor as fse
    import foundry_common as fc
    cards, _, _ = fc.load_corpus_gated()
    fse.build_self_noun_rx(cards)
    ratified = fse.ratified_delivery_tokens()

    homed = collections.defaultdict(list)
    unresolved = []
    for r in rows:
        num = int(r["cr"].split(".")[1])
        tok, desc, text = find_home(keywords[num], ratified)
        r["home"] = tok
        r["home_descriptor"] = desc
        r["cr_text"] = text
        if tok is not None:
            homed[tok].append(r)
            continue
        # No trigger/activated shape parsed out of the templated text. Fall
        # back to the keyword's CR ABILITY CLASS, which §2 already has a slot
        # for -- a static keyword's home is `static`, and that is a real home,
        # not a gap. Only keywords whose class ALSO fails to give a slot are
        # reported unresolved.
        eff = r["effective_classes"]
        if eff == ["static"]:
            r["home"] = "static"
            r["home_via"] = "CR ability class (702.Na)"
            homed["static"].append(r)
        elif eff == ["spell"]:
            r["home"] = "(none — spell ability)"
            r["home_via"] = "CR ability class (702.Na)"
            homed["(none — spell ability)"].append(r)
        elif text is None:
            unresolved.append((r, "no templated text AND no single-class fallback"))
        else:
            unresolved.append((r, f"templated shape has no ratified token: {desc}"))

    total = sum(len(v) for v in homed.values())
    print(f"\n{'='*78}\nKEYWORD -> DELIVERY HOME, derived from the CR's own "
          f"templated text\n{'='*78}")
    print(f"routed to an EXISTING ratified token: {total} of {len(rows)} keywords\n")
    for tok in sorted(homed, key=lambda t: -len(homed[t])):
        names = ", ".join(sorted(r["keyword"] for r in homed[tok]))
        print(f"[{tok}]  ({len(homed[tok])})\n  {names}\n")

    print(f"{'='*78}\nNOT ROUTED — {len(unresolved)} keywords. Reported, never "
          f"approximated.\n{'='*78}")
    by_reason = collections.defaultdict(list)
    for r, why in unresolved:
        by_reason[why].append(r["keyword"])
    for why in sorted(by_reason, key=lambda w: -len(by_reason[w])):
        print(f"\n({len(by_reason[why])}) {why}\n  "
              + ", ".join(sorted(by_reason[why])))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--unstated", action="store_true",
                    help="list keywords whose CR text states no ability class")
    ap.add_argument("--homes", action="store_true",
                    help="route each keyword to its §2 DELIVERY token, derived "
                         "from the CR's own templated text")
    ap.add_argument("--json", metavar="PATH")
    args = ap.parse_args()

    keywords = load_702(CR_PATH)
    named = {n: k for n, k in keywords.items()
             if k["name"] and n != PREAMBLE_RULE}

    rows = []
    for num in sorted(named):
        kw = named[num]
        classes, ev = classify(kw)
        effective = effective_classes(kw)
        blob = " ".join(kw["subrules"].values())
        rows.append({"cr": f"702.{num}", "keyword": kw["name"],
                     "cr_classes": classes, "effective_classes": effective,
                     "evidence": ev,
                     "multi": len(effective) > 1,
                     "multi_hint_unresolved": bool(MULTI_HINT.search(blob))
                     and len(effective) <= 1,
                     "delivery": [CLASS_TO_DELIVERY.get(e) for e in effective]})

    def label(r, key):
        v = r[key]
        return "+".join(v) if v else "UNSTATED"

    by_class = collections.Counter(label(r, "cr_classes") for r in rows)
    by_effective = collections.Counter(label(r, "effective_classes")
                                       for r in rows)

    print(f"CR file: {CR_PATH}")
    print(f"CR 702 keywords parsed: {len(rows)}\n")
    print("AS THE CR WORDS IT")
    print(f"{'CR ability class':26s} {'keywords':>9}")
    print("-" * 78)
    for cls, n in by_class.most_common():
        note = ""
        if cls in SUBSUMES:
            note = f"   -> rolls up to {SUBSUMES[cls][0]} ({SUBSUMES[cls][1]})"
        print(f"{cls:26s} {n:9d}{note}")

    print("\nAFTER CR-STATED ROLLUP -- what the §2 DELIVERY slot must be")
    print(f"{'ability class':26s} {'keywords':>9}   {'§2 DELIVERY slot':s}")
    print("-" * 78)
    for cls, n in by_effective.most_common():
        slot = CLASS_TO_DELIVERY.get(cls, "— no §2 slot —")
        print(f"{cls:26s} {n:9d}   {slot}")

    print("\nkeywords by class")
    print("-" * 78)
    grouped = collections.defaultdict(list)
    for r in rows:
        grouped[label(r, "effective_classes")].append(r["keyword"])
    for cls, n in by_effective.most_common():
        names = ", ".join(sorted(grouped[cls]))
        print(f"\n[{cls}]  ({n})\n  {names}")

    unresolved = [r for r in rows if r["multi_hint_unresolved"]]
    if unresolved:
        print("\n" + "=" * 78)
        print("⚠ MULTIPLICITY HINTED BUT NOT RESOLVED -- read these by hand.")
        print("The CR prose says the keyword represents several abilities, but")
        print("only one class sentence parsed. Reported, never assumed.")
        print("=" * 78)
        for r in unresolved:
            print(f"  {r['cr']:9s} {r['keyword']}")

    if args.unstated:
        print("\n" + "=" * 78)
        print("UNSTATED -- the CR does not call these '<X> ability' in 702.Na.")
        print("Reported, NOT assigned to a nearest class.")
        print("=" * 78)
        for r in rows:
            if r["cr_class"] is None:
                first = (r["evidence"] or
                         keywords[int(r['cr'].split('.')[1])]["subrules"].get("a", ""))
                print(f"  {r['cr']:9s} {r['keyword']:28s} {first[:90]}")

    if args.homes:
        cmd_homes(rows, keywords)

    if args.json:
        Path(args.json).write_text(json.dumps(rows, indent=1), encoding="utf-8")
        print(f"\nwrote {args.json}")


if __name__ == "__main__":
    main()
