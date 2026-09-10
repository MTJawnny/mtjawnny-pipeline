"""CR 702 keyword abilities and CR 205 type vocabulary — L2, CR-only.

## What this owns

The CR-only half of the keyword seam: the CR 702/205 parsing constants,
`load_702`, `type_vocabulary`, `classify`, `effective_classes`, and the pure
`keyword_rows()` derivation lifted out of the legacy reporting flow.

## What this deliberately does NOT own — R6, and it is the whole point

`find_home` and `keyword_homes()` are NOT here. They consume `parse_delivery`,
so putting them in the CR half is exactly the import cycle R6 was written to
remove: the reverse edge was carried by one reusable function, and the `_twin`
cross-instance sync in the legacy shape extractor exists only because of it.
They belong to `mtg/shapes/delivery.py` and arrive in S7, not S6.

`CLASS_TO_DELIVERY` stays here and its VALUES are grammar §2 DELIVERY token
strings. As literal constants they create no edge. The moment anything in
`mtg/cr/**` validates them against `ratified_delivery_tokens()` the cycle is
back -- which is what B10 exists to stop.

## Two facts that are not one fact

`CR_KEYWORD_NAMES` (the membership list, 194) and `KEYWORD_HOME` (the derived
map, 151) are different objects and neither substitutes for the other. A derived
map is not the list it was derived from: asking a home map "is this a keyword?"
answered no for `awaken`, and `Awaken 4—{4}{W}` was read as a flavor word.

## Layer law

Imports stdlib and `mtj_foundry.mtg.cr.edition` only. Never `mtg/shapes/**`,
never `experiments`, never a process exit -- the halt boundary is re-established
by the legacy shell.
"""

from __future__ import annotations

import re
import collections
from pathlib import Path

from mtj_foundry.mtg.cr import edition as _edition

__all__ = ["CRKeywordError", "load_702", "type_vocabulary", "classify",
           "effective_classes", "keyword_rows", "CLASS_TO_DELIVERY",
           "PREAMBLE_RULE", "SUBSUMES", "MULTI_HINT"]


class CRKeywordError(RuntimeError):
    """A CR 702/205 parse the pipeline refuses to proceed on."""


# NO DEFAULT CR PATH HERE. This library derives no repository root and holds no
# module-level CR location: the caller supplies the edition path, which it gets
# from the accepted layout owner through its own composition boundary. See
# `edition.select_cr_path`.


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
    # Read through the normalizing loader, never `path.read_text()`. The
    # 2026-08-07 edition prints `**702.6a.**`, which HEADER/SUBRULE below do
    # not match — parsing it raw returns zero keywords.
    text = _edition.text(path)
    lines = text.splitlines()

    global CR_CLASSES
    CR_CLASSES = {m.group(2).lower() for m in CLASS_RULE.finditer(text)}
    if len(CR_CLASSES) != 4:
        raise CRKeywordError(f"CR 113.3a-d should enumerate exactly 4 ability classes; "
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
        raise CRKeywordError("Parsed zero CR 702 keywords. The CR file's section 702 "
                "formatting has changed; fix the parser, do not fall back.")
    return keywords


def type_vocabulary(path: Path) -> dict:
    """Every CR 205 type list -> sets, read from the CR at run time.

    Card types (205.2a), supertypes (205.4a), and ALL TEN subtype lists
    (205.3g-q). Required by CR 702.14a's landwalk template, which is stated as
    a GRAMMAR over these lists rather than as a list of keyword names, and by
    the self-reference noun set, which needs "this <subtype>" to be complete.

    `subtypes` is the union of the ten, provided so a caller never has to
    remember which ten they are."""
    text = _edition.text(path)
    out = {}
    for key, rx in TYPE_RULES.items():
        m = rx.search(text)
        if not m:
            raise CRKeywordError(f"Could not parse {key} from the CR (rule 205). The CR's "
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
            raise CRKeywordError(f"parsed only {len(out[key])} {key} from CR 205 "
                    f"(expected >= {least}): {sorted(out[key])}")
        if tail not in out[key]:
            raise CRKeywordError(f"CR 205 {key} parsed without its LAST member {tail!r} — "
                    f"the Oxford-comma split has regressed. Got: "
                    f"{sorted(out[key])}")
        if any(w.startswith("and ") for w in out[key]):
            raise CRKeywordError(f"CR 205 {key} contains a conjunction fragment: "
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




def keyword_rows(path) -> list:
    """Every CR 702 keyword as a pure row. NO reporting, NO delivery lookup.

    Lifted verbatim out of the legacy `main()`'s reporting flow (R5/R6): the
    derivation was always pure, it was merely trapped inside a function that
    also printed. Splitting it is what lets the CR half be consumed without
    running an operator command -- and what keeps `find_home` out of L2, since
    the rows carry no `home` key at all. The legacy shell adds that, one layer
    up, where delivery parsing is allowed to be reached.
    """
    keywords = load_702(path)
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
    return rows
