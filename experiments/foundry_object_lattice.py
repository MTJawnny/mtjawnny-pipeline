#!/usr/bin/env python3
"""The `targeted-<action>-<class>` OBJECT LATTICE — class extraction, derived.

THE LAW THIS IMPLEMENTS IS ALREADY RATIFIED, AND WAS NEVER IMPLEMENTED.
`docs/MASTER-HANDOFF-ADDENDUM-4.md` §4, the ratified rulings registry:

    | M8 generalized (b6 D3) | Multi-class targeted-<action> cards get every
    | applicable per-class tag, all action verbs, NEVER COMBO TAGS;
    | removal-for-breadth is wrong. |

restated in `docs/CODEBOOK-NAMING-GRAMMAR.md` §5:

    Per-object-class siblings are the law for every `targeted-<action>` family
    (M8 generalized, b6 D3): OR-shaped multi-class targets get every applicable
    class tag; the class lattice (`targeted-bounce-<class>`,
    `targeted-destruction-<class>`...) is a ratified grammar with virtual nodes.

Measured 2026-08-09, before this module existed: **zero cards in the codebook
carried two class siblings of one action family.** Putrefy — "Destroy target
artifact or creature. It can't be regenerated." — carried exactly one tag,
`rule:prevents-regeneration`, the rider and not the spell.

WHERE THE VOCABULARY COMES FROM, AND WHY NONE OF IT IS TYPED HERE
-----------------------------------------------------------------
* **CR 701.8a** — *"To destroy a permanent, move it from the battlefield to
  its owner's graveyard."* Only a PERMANENT can be destroyed, so the destroy
  lattice's class slot is the permanent-type list and not the card-type list.
* **CR 110.4** — *"There are six permanent types: artifact, battle, creature,
  enchantment, land, and planeswalker."* Closed, and parsed at run time.
* **CR 205.2a** — the fifteen card types, for actions that reach beyond the
  battlefield (exile, bounce and counter can name an instant or sorcery).
* **`validate_slug.OBJECT_VOCAB`** — the ratified grammar §5 OBJECT slot. Every
  class this module emits is asserted to be in it, so a CR term with no ratified
  slug token halts instead of minting vocabulary.

`_assert_vocabulary_agrees()` runs all three against each other at import. A
hand-list is a defect with a delay; three sources that must agree is the
closest thing to a guard against one of them silently moving.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
* **CR 701.8b** names exactly two routes to destruction: *"an effect that uses
  the word 'destroy'"* or the lethal-damage state-based action (704.5g). This
  module reads the WORD. That is not a heuristic boundary, it is one of the
  CR's own two, and the other route is not a targeted destroy at all.
* **AND-shaped targets are not OR-shaped ones.** CR 300.2 — *"Some objects have
  more than one card type (for example, an artifact creature)"* — so
  "destroy target artifact creature" names ONE object that must be both, while
  "artifact or creature" names either. M8 governs the OR case by name and is
  silent on AND. `classify_clause` reports AND separately (`conjunctive=True`)
  and never fuses it into a union; what tag it earns is unruled and is
  reported, not decided.
* It mints nothing and writes nothing. It is the measurement half.
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
import foundry_common as fc                  # noqa: E402
import foundry_cr as cr                      # noqa: E402
import foundry_cr702_classes as crc          # noqa: E402
import validate_slug as vs                   # noqa: E402


# --------------------------------------------------------------------------
# CR-derived vocabulary
# --------------------------------------------------------------------------

_PERMANENT_TYPES_RE = re.compile(
    r"^110\.4\.?\s+There are (\w+) permanent types:\s*([^.]+)\.", re.M)
_CARD_TYPES_RE = re.compile(
    r"^205\.2a\.?\s+The card types are\s*([^.]+)\.", re.M)

_NUMBER_WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
                 "seven": 7, "eight": 8, "nine": 9, "ten": 10}


def _split_cr_list(blob: str) -> set:
    """The CR writes these with an OXFORD COMMA — '…, land, and planeswalker'.

    THIS FUNCTION SHIPPED THE DEFECT ITS OWN DOCSTRING WARNED ABOUT. The first
    version split on `,\\s*|\\s+and\\s+`; at ', and planeswalker' the comma arm
    matches first and consumes the space, so the `and` arm — which requires
    leading whitespace — can never fire, and the last member parsed as
    'and planeswalker'. Identical to `type_vocabulary`'s `and vanguard`.

    **The cardinality guard would have passed**: six members, one of them
    wrong. `_assert_vocabulary_agrees` caught it in one run, because a subset
    assertion against CR 205.2a reads CONTENT. A count cannot see a
    substitution — which is why the guard is a content check and not a `len()`.
    """
    out = set()
    for part in re.split(r",\s*(?:and\s+)?|\s+and\s+", blob):
        term = part.strip().lower()
        if term and term != "and":
            out.add(term)
    return out


def permanent_types(path: Path = None) -> set:
    """CR 110.4's six, parsed. The rule states its own cardinality in words
    ('There are SIX permanent types'), so the guard compares the parsed list
    against the CR's OWN count rather than against a number typed here."""
    m = _PERMANENT_TYPES_RE.search(cr.text(path) if path else cr.text())
    if not m:
        fc.halt("Could not parse CR 110.4's permanent-type list. The CR's "
                "wording has changed; fix the parser, never fall back to a "
                "remembered list of six.")
    stated, parsed = m.group(1).lower(), _split_cr_list(m.group(2))
    want = _NUMBER_WORDS.get(stated)
    if want is None:
        fc.halt(f"CR 110.4 states its cardinality as {stated!r}, which this "
                f"parser cannot read as a number.")
    if len(parsed) != want:
        fc.halt(f"CR 110.4 says there are {want} permanent types; the parse "
                f"yielded {len(parsed)}: {sorted(parsed)}")
    return parsed


def card_types(path: Path = None) -> set:
    m = _CARD_TYPES_RE.search(cr.text(path) if path else cr.text())
    if not m:
        fc.halt("Could not parse CR 205.2a's card-type list.")
    return _split_cr_list(m.group(1))


def _assert_vocabulary_agrees() -> None:
    """Three sources, asserted against each other. CR 110.4 must be a subset of
    CR 205.2a (a permanent type is a card type), and every permanent type must
    already be a ratified grammar §5 OBJECT token — otherwise this module would
    be about to emit a slug out of vocabulary the grammar never ratified."""
    perms, cards_ = permanent_types(), card_types()
    if not perms <= cards_:
        fc.halt(f"CR 110.4 names permanent type(s) absent from CR 205.2a: "
                f"{sorted(perms - cards_)}")
    missing = sorted(perms - set(vs.OBJECT_VOCAB))
    if missing:
        fc.halt(f"CR 110.4 permanent type(s) {missing} are not in the ratified "
                f"grammar §5 OBJECT vocabulary (validate_slug.OBJECT_VOCAB). "
                f"Emitting a class slug for them would mint vocabulary; that "
                f"is a ratification, not a code change.")


PERMANENT_TYPES = permanent_types()
CARD_TYPES = card_types()
_assert_vocabulary_agrees()


# --------------------------------------------------------------------------
# subtype -> permanent type, derived from CR 205.3g-q
# --------------------------------------------------------------------------

def _subtype_map() -> dict:
    """`Equipment` -> artifact, `Angel` -> creature, `Aura` -> enchantment.

    `foundry_cr702_classes.type_vocabulary()` already parses all ten CR 205.3
    subtype lists AND KEYS THEM BY THEIR PARENT TYPE, which is exactly this
    map — so it is consumed, not re-derived. Re-implementing a parse that
    already exists is this repo's most expensive recurring defect.

    Only the six CR 110.4 permanent types get a bucket. `spell_types` (CR
    205.3k) and `planar_types` are deliberately absent: an instant is not a
    permanent and cannot be destroyed (CR 701.8a), and plane layouts are
    outside Gate #0 anyway."""
    tv = crc.type_vocabulary()
    buckets = {
        "artifact": "artifact_types", "creature": "creature_types",
        "enchantment": "enchantment_types", "land": "land_types",
        "planeswalker": "planeswalker_types", "battle": "battle_types",
    }
    missing = sorted(set(buckets) - PERMANENT_TYPES)
    if missing:
        fc.halt(f"subtype map names {missing}, which CR 110.4 does not list as "
                f"permanent types — the two CR rules have diverged.")
    unmapped = sorted(PERMANENT_TYPES - set(buckets))
    if unmapped:
        fc.halt(f"CR 110.4 permanent type(s) {unmapped} have no CR 205.3 "
                f"subtype list in type_vocabulary(). A permanent type with no "
                f"bucket silently loses every card that names one of its "
                f"subtypes; fix the map, do not skip.")
    out = {}
    for parent, key in buckets.items():
        for sub in tv[key]:
            # A word claimed by two lists cannot decide a class on its own.
            # Recorded as ambiguous rather than resolved by list order.
            out.setdefault(sub, set()).add(parent)
    for sub in tv.get("creature_types_multiword", ()):
        out.setdefault(sub, set()).add("creature")
    return out


SUBTYPE_TO_TYPE = _subtype_map()
AMBIGUOUS_SUBTYPES = {s for s, p in SUBTYPE_TO_TYPE.items() if len(p) > 1}

# CR 110.4 names the six types; the cards also target the PERMANENT itself,
# with or without a negative qualifier. Every token here is already in the
# ratified grammar §5 OBJECT vocabulary (`permanent`, `nonland`, `noncreature`),
# so these compose rather than mint. A broad form is NOT OR-shaped — "nonland
# permanent" names one target of any nonland type — so it takes exactly its own
# tag and never the per-type ones, which would assert a reach the card lacks.
PERMANENT_FORMS = (
    ("noncreature-permanent", re.compile(r"\bnoncreature permanents?\b", re.I)),
    ("nonland-permanent", re.compile(r"\bnonland permanents?\b", re.I)),
    ("permanent", re.compile(r"\bpermanents?\b", re.I)),
)


# --------------------------------------------------------------------------
# clause extraction
# --------------------------------------------------------------------------

# A targeted clause runs from the action verb to the end of its sentence. `;`
# ends it too: CR 700.2's modal bullets are already split upstream by
# `det_scan_texts`, but a semicolon inside one sentence separates independent
# instructions ("Destroy target creature; its controller loses 2 life").
_CLAUSE_TAIL = r"([^.;]*)"

# slug stem -> how the cards PRINT that action. Every stem is already in
# `grammars.json`'s `targeted-<action>` closed facet vocab
# (`destruction`->`destroy`, `bounce`, `exile`, `discard`, `damage`), so this
# maps ratified stems to printed forms and mints no vocabulary.
#
# `discard` and `damage` are deliberately absent. Discard targets a PLAYER and
# its object is a card in hand, not a permanent type. Damage has its own closed
# recipient list — **CR 120.1's four** — which is a different enumeration the
# grammar already tracks separately, and the 2026-08-09 audit found one arm of
# that family enumerated against it and the other not. Folding either into the
# permanent-type lattice would assert one closed list where the CR names two.
ACTION_VERBS = {
    "destroy": {"verb": r"destroys?", "word": "destroy"},
    "exile": {"verb": r"exiles?", "word": "exile"},
    # CR 701.8a's counterpart for bounce is the zone change itself; the cards
    # print it as `return … to … hand`, and the destination is REQUIRED —
    # without it `return target creature` is reanimation (to the battlefield),
    # a different axis family entirely. Same shape as the `put into ‹DEST›
    # from ‹ORIGIN›` trap: the closing phrase is what makes the match correct.
    "bounce": {"verb": r"returns?", "word": "return",
               "tail": r"to (?:its|their) owner'?s? hand|to your hand|"
                       r"to (?:its|their) owner'?s? hands"},
}

# "up to N target", "another target", "each target" — the quantity words that
# sit between the verb and the word `target`. `target` itself is required:
# grammar §6's b7 Unwind ruling says a `-target-` slug needs the printed word
# (CR 601.2c), so a clause without it is not this lattice's business.
_TARGET_HEAD = r"(?:up to \w+ |another |each |all )?target"


def _clause_re(spec: dict) -> re.Pattern:
    """A clause the action opens, optionally required to CLOSE on a phrase.

    The `tail` constraint is not cosmetic: `return target creature` with no
    destination is reanimation, not bounce, and matching without it would put
    every reanimation spell on the bounce lattice."""
    body = rf"\b{spec['verb']} {_TARGET_HEAD} {_CLAUSE_TAIL}"
    if spec.get("tail"):
        body = (rf"\b{spec['verb']} {_TARGET_HEAD} ([^.;]*?)"
                rf"(?:{spec['tail']})")
    return re.compile(body, re.I)


_CLAUSE_RES = {stem: _clause_re(spec) for stem, spec in ACTION_VERBS.items()}

# A type word is a class only when it is the TARGET's own type. These strip the
# phrases where a type word appears for another reason, before classes are read.
_NOT_THE_TARGET = (
    # "an artifact you control", "a creature an opponent controls" inside a
    # trailing relative clause still describes the target, so these are the
    # narrow cases only: comparisons and counted references elsewhere.
    re.compile(r"\bfor each\b[^,;]*", re.I),
    re.compile(r"\bequal to the number of\b[^,;]*", re.I),
    re.compile(r"\bunless (?:its|their) controller\b[^,;]*", re.I),
)

# CR 300.2's conjunctive form: two type words adjacent, naming ONE object.
_CONJUNCTIVE_RE = re.compile(
    rf"\b({'|'.join(sorted(CARD_TYPES))})\s+({'|'.join(sorted(CARD_TYPES))})\b", re.I)


def classify_clause(clause: str, domain: set = None) -> dict:
    """The classes a target clause names.

    **A `<type> card` IS NOT A PERMANENT (CR 110.1** — *"A permanent is a card
    or token on the battlefield"*). Card text names an object in a
    non-battlefield zone as a CARD and an object on the battlefield by its
    permanent type, so `creature card` is graveyard recursion and `creature` is
    the permanent. Found by the sample sheet on its first run: Auriok Salvagers,
    *"Return target artifact card … from your graveyard to your hand"*, had been
    claimed for the bounce lattice. The lookahead is what the DET standing
    condition is for.

    `domain` is the closed set the action can reach — CR 110.4's permanents for
    destroy, CR 205.2a's card types for actions that leave the battlefield. It
    is passed in rather than inferred, so a caller cannot silently widen it.

    Returns {classes, conjunctive, qualified}: `conjunctive` marks CR 300.2's
    "artifact creature" (one object, two types), `qualified` marks a clause
    carrying a restriction ("with power 3 or greater") that the class slot does
    not encode.
    """
    domain = domain if domain is not None else PERMANENT_TYPES
    text = clause.lower()
    for rx in _NOT_THE_TARGET:
        text = rx.sub(" ", text)

    conj = []
    for m in _CONJUNCTIVE_RE.finditer(text):
        a, b = m.group(1).lower(), m.group(2).lower()
        if a in domain and b in domain:
            conj.append((a, b))

    classes = {t for t in domain if re.search(rf"\b{t}s?\b(?!\s+cards?\b)", text)}

    # A broad permanent form OUTRANKS the per-type read of the same clause.
    # "destroy target nonland permanent" contains no type word, but "destroy
    # target permanent that's an artifact or creature" would — and there the
    # types are a RESTRICTION on one broad target, not two targets.
    broad = None
    for form, rx in PERMANENT_FORMS:
        if rx.search(text):
            broad = form
            break

    # Subtypes only fill in when the clause named no type of its own:
    # "destroy target Equipment" is artifact by CR 205.3g, while "destroy
    # target creature that's a Wall" already said creature and the subtype
    # adds nothing.
    via_subtype = {}
    if not classes and broad is None:
        for sub, parents in SUBTYPE_TO_TYPE.items():
            if len(parents) != 1:
                continue
            parent = next(iter(parents))
            if parent in domain and re.search(
                    rf"\b{re.escape(sub)}s?\b(?!\s+cards?\b)", text):
                classes.add(parent)
                via_subtype[sub] = parent

    qualified = bool(re.search(r"\bwith \w+|\bthat\b|\bwhose\b|\bif it\b", text))
    return {"classes": {broad} if broad else classes, "broad": broad,
            "via_subtype": via_subtype, "conjunctive": conj,
            "qualified": qualified}


def clauses_for(card: dict, stem: str):
    """Every targeted clause of one action on one card, over the RATIFIED DET
    preprocessing (all faces, CARDNAME canonicalized, modal bullets expanded).

    Consuming `det_scan_texts` is not optional: a probe that matched raw lines
    under-reported by 43 on 2026-08-05, and the four consumers that use it are
    outnumbered by nineteen that do not."""
    rx = _CLAUSE_RES[stem]
    for text in fc.det_scan_texts(card):
        for m in rx.finditer(text):
            yield m.group(0), m.group(1)


def classes_for_card(card: dict, stem: str, domain: set = None) -> dict:
    """Union of the classes every clause of this action names on this card,
    with the quote that proves each class."""
    domain = domain if domain is not None else PERMANENT_TYPES
    found, quotes, conj, qual = set(), {}, [], False
    subs = {}
    for whole, tail in clauses_for(card, stem):
        r = classify_clause(tail, domain)
        conj += r["conjunctive"]
        qual = qual or r["qualified"]
        subs.update(r["via_subtype"])
        for c in r["classes"]:
            found.add(c)
            quotes.setdefault(c, whole.strip())
    return {"classes": found, "quotes": quotes, "conjunctive": conj,
            "qualified": qual, "via_subtype": subs}


def slug_for(stem: str, cls: str = None) -> str:
    """`rule:targeted-destroy` / `rule:targeted-destroy-creature`.

    NOTE THE SPELLING. Grammar §5 line 651 still writes the lattice
    `targeted-destruction-<class>`, the PRE-RENAME form: `targeted-destruction`
    became `targeted-destroy` on 2026-08-09 (A15 ruling §6c) and §7 item 2 of
    that doc logs the grammar's stale spelling as open drift. The live axis is
    the authority, so this emits `-destroy-`; the grammar line needs a G4
    generator fix, not this module bending to it."""
    base = f"rule:targeted-{stem}"
    return base if cls is None else f"{base}-{cls}"


# --------------------------------------------------------------------------
# measurement CLI
# --------------------------------------------------------------------------

def measure(stem: str, domain: set) -> dict:
    cards, _, _ = fc.load_corpus_gated()
    per_class = Counter()
    combos = Counter()
    n_classes = Counter()
    conj_cards, qual_cards, residual = [], [], []
    hits = {}
    for oid, card in cards.items():
        clauses = list(clauses_for(card, stem))
        if not clauses:
            continue
        r = classes_for_card(card, stem, domain)
        if not r["classes"]:
            residual.append((card["name"], clauses[0][0][:90]))
            continue
        hits[oid] = r
        n_classes[len(r["classes"])] += 1
        for c in r["classes"]:
            per_class[c] += 1
        if len(r["classes"]) > 1:
            combos[tuple(sorted(r["classes"]))] += 1
        if r["conjunctive"]:
            conj_cards.append(card["name"])
        if r["qualified"]:
            qual_cards.append(card["name"])
    return {"stem": stem, "cards": len(hits), "per_class": per_class,
            "combos": combos, "n_classes": n_classes,
            "memberships": sum(per_class.values()),
            "conjunctive": conj_cards, "qualified": qual_cards,
            "residual": residual, "hits": hits}


def audit(stem: str, domain: set) -> dict:
    """The negative controls. A guard that has never been shown to fail is not
    known to be a guard, so each of these was run against the live corpus and
    its output READ, card by card, before being written down here.

    NC1  every claimed card prints the word `destroy` — CR 701.8b's first of
         exactly two routes to destruction, and the only one this reads.
    NC2  a card with no targeted clause yields nothing (the extractor cannot
         invent a membership).
    NC3  quoted grants are reported, not silently included. All 16 were read
         2026-08-09: self-grants (Harmonic Sliver IS a Sliver) and Equipment
         grants (Heartseeker). Both genuinely hand the player that removal, so
         they are TAGGED — grammar §2's quoted-grant exclusion governs
         DELIVERY, and the class slot is an EFFECT question. Captain's ratified
         criterion is deck-building relevance.
    NC4  no emitted slug may fall outside the ratified grammar — every one is
         re-validated through `validate_slug`.
    """
    cards, _, _ = fc.load_corpus_gated()
    qspan = re.compile(r"[\"“]([^\"”]*)[\"”]")
    dest = _CLAUSE_RES[stem]
    no_verb, quoted_only, silent, bad_slug = [], [], 0, []
    # NC1 must test the PRINTED verb, not the slug stem. `bounce` is a ratified
    # stem that no card prints -- they print `return` -- so keying this on the
    # stem flagged every bounce card. A probe defect in the negative control
    # itself, which is the default outcome and why this note stays.
    verb_word = ACTION_VERBS[stem]["word"]
    for oid, card in cards.items():
        clauses = list(clauses_for(card, stem))
        if not clauses:
            silent += 1
            continue
        full = fc.full_oracle_text(card)
        if verb_word not in full.lower():
            no_verb.append(card["name"])
        spans = [m.span(1) for m in qspan.finditer(full)]
        hits = [m.start() for m in dest.finditer(full)]
        if hits and all(any(a <= h < b for a, b in spans) for h in hits):
            quoted_only.append(card["name"])

    for cls in sorted(domain | {f for f, _ in PERMANENT_FORMS}):
        slug = slug_for(stem, cls)
        v = vs.validate_slug(slug, definition=None, all_slugs=[])
        if not v["ok"]:
            bad_slug.append((slug, v.get("failures") or v.get("reason")))
    return {"nc1_no_verb": no_verb, "nc2_silent": silent,
            "nc3_quoted_only": quoted_only, "nc4_bad_slug": bad_slug}


SAMPLE_REPORT_JSON = fc.FOUNDRY_OUT_DIR / "object_lattice_samples.json"
SAMPLE_REPORT_MD = fc.FOUNDRY_OUT_DIR / "object_lattice_samples.md"


def write_report(seed: int, n: int) -> dict:
    """The ratification packet: `det-patterns-v2.json`'s standing condition is a
    fixed-seed per-pattern sample, and ANY row failing its axis definition halts
    the pass before provenance writes. This writes that sheet for every class of
    every action.

    **Quotes go in the FILE, never to console (A14).** The console gets counts.

    It also emits the `det-patterns-v2.json` entries the lattice would need —
    as a PROPOSAL inside the report, not written into the ratified file. A
    `rule-derived` assertion may only cite `det-patterns-v2:<n>`
    (`SOURCE_REF_FAMILIES`), so those entries are what makes the membership
    legal, and minting them is Captain's."""
    import random
    cards, _, _ = fc.load_corpus_gated()
    cb_axes = None
    try:
        import foundry_codebook as fcb
        cb_axes = fcb.load_codebook()["axes"]
    except BaseException:
        pass

    actions = {}
    proposed_patterns = []
    for idx, stem in enumerate(sorted(ACTION_VERBS)):
        m = measure(stem, PERMANENT_TYPES)
        rng = random.Random(seed)
        by_class = defaultdict(list)
        for oid, r in m["hits"].items():
            for c in r["classes"]:
                by_class[c].append((oid, r["quotes"][c]))
        classes = {}
        for cls in sorted(by_class):
            pool = sorted(by_class[cls])
            slug = slug_for(stem, cls)
            exists = cb_axes.get(slug, {}).get("status") if cb_axes else None
            classes[cls] = {
                "slug": slug,
                "members": len(pool),
                "axis_status_today": exists or "ABSENT — self-instantiates per b6 §11.2",
                "sample": [{"card": cards[o]["name"], "oracle_id": o, "quote": q}
                           for o, q in rng.sample(pool, min(n, len(pool)))],
            }
        actions[stem] = {
            "printed_verb": ACTION_VERBS[stem]["word"],
            "cards": m["cards"], "memberships": m["memberships"],
            "multi_class_cards": sum(v for k, v in m["n_classes"].items() if k > 1),
            "residual": [{"card": c, "clause": q} for c, q in m["residual"]],
            "conjunctive_cr300_2": m["conjunctive"],
            "classes": classes,
        }
        proposed_patterns.append({
            "slug": slug_for(stem),
            "lattice": True,
            "class_domain": "CR 110.4 permanent types + permanent/nonland/noncreature forms",
            "pattern": _CLAUSE_RES[stem].pattern,
            "status": "PROPOSED — not ratified, not written to det-patterns-v2.json",
            "cr_anchor": {"destroy": "701.8a/701.8b", "exile": "406.1",
                          "bounce": "zone change to hand"}.get(stem),
            "note": "One matcher -> N axes. det-patterns-v2.json's schema is "
                    "slug + one regex -> one axis; this needs the lattice "
                    "extension before it can be an entry.",
        })

    report = {
        "schema": "foundry-object-lattice-samples/1",
        "generated_by": "experiments/foundry_object_lattice.py",
        "law": "M8 generalized (b6 D3), MASTER-HANDOFF-ADDENDUM-4.md §4; "
               "lattice grammars b6 §11.2 (virtual nodes self-instantiate on "
               "first quote-verified member, no fresh ratification)",
        "record": "docs/OBJECT-LATTICE-2026-08-09.md",
        "seed": seed, "sample_size": n,
        "cr_sources": {
            "permanent_types_110_4": sorted(PERMANENT_TYPES),
            "card_types_205_2a": len(CARD_TYPES),
            "subtype_lists_205_3": "consumed from foundry_cr702_classes.type_vocabulary()",
        },
        "actions": actions,
        "proposed_det_patterns": proposed_patterns,
    }
    fc.write_json(SAMPLE_REPORT_JSON, report)

    lines = ["# OBJECT LATTICE — sample sheet for ratification", "",
             f"Seed `{seed}`, {n} rows per class. Record: "
             f"`docs/OBJECT-LATTICE-2026-08-09.md`.", "",
             "Standing condition (`det-patterns-v2.json`): **any sample row "
             "failing its axis definition halts the pass before provenance "
             "writes.**", ""]
    for stem, a in actions.items():
        lines += [f"## `targeted-{stem}` — printed *{a['printed_verb']}*", "",
                  f"{a['cards']:,} cards · **{a['memberships']:,} memberships** · "
                  f"{a['multi_class_cards']} multi-class · "
                  f"{len(a['residual'])} residual", ""]
        for cls, c in a["classes"].items():
            lines += [f"### `{c['slug']}` — {c['members']:,} members "
                      f"({c['axis_status_today']})", ""]
            for row in c["sample"]:
                lines.append(f"- **{row['card']}** — {row['quote']}")
            lines.append("")
        if a["residual"]:
            lines += ["**Residual (no class named):**", ""]
            lines += [f"- {r['card']} — {r['clause']}" for r in a["residual"][:20]]
            lines.append("")
    SAMPLE_REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    return {"json": str(SAMPLE_REPORT_JSON), "md": str(SAMPLE_REPORT_MD),
            "actions": {k: v["memberships"] for k, v in actions.items()}}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--action", default="destroy", choices=sorted(ACTION_VERBS))
    ap.add_argument("--domain", default="permanent",
                    choices=["permanent", "card"],
                    help="permanent = CR 110.4 (destroy); card = CR 205.2a")
    ap.add_argument("--residual", action="store_true",
                    help="print the clauses that matched the action but named "
                         "NO class — where the defects are")
    ap.add_argument("--audit", action="store_true",
                    help="run the negative controls (NC1-NC4) and exit 1 on "
                         "any hard failure")
    ap.add_argument("--samples", type=int, default=0, metavar="N",
                    help="fixed-seed sample of N cards per class, for the DET "
                         "standing condition's per-pattern verification")
    ap.add_argument("--seed", type=int, default=20260809)
    ap.add_argument("--report", type=int, default=0, metavar="N",
                    help="write the ratification packet (N rows per class) to "
                         "experiments/out/foundry/object_lattice_samples.{json,md}. "
                         "Quotes go in the FILE, never to console (A14).")
    args = ap.parse_args()

    if args.report:
        r = write_report(args.seed, args.report)
        print("wrote the ratification packet (quotes are in the files, not here)")
        print(f"  {r['json']}")
        print(f"  {r['md']}")
        for stem, n in r["actions"].items():
            print(f"  targeted-{stem}: {n:,} memberships")
        return 0

    domain = PERMANENT_TYPES if args.domain == "permanent" else CARD_TYPES
    print(f"CR 110.4 permanent types : {sorted(PERMANENT_TYPES)}")
    print(f"CR 205.2a card types     : {len(CARD_TYPES)}")
    print(f"domain for `{args.action}` : {args.domain} ({len(domain)})\n")

    m = measure(args.action, domain)
    print(f"cards with a targeted `{args.action}` clause and >=1 class: "
          f"{m['cards']:,}")
    print(f"memberships the ratified lattice implies : {m['memberships']:,}")
    print(f"  per class      : {dict(m['per_class'].most_common())}")
    print(f"  by class count : {dict(sorted(m['n_classes'].items()))}")
    print(f"  multi-class    : {sum(v for k, v in m['n_classes'].items() if k > 1):,}"
          f"  <- the population M8 is about")
    for combo, n in m["combos"].most_common(10):
        print(f"      {n:>4}  {' + '.join(combo)}")
    print(f"\n  CR 300.2 conjunctive ('artifact creature', ONE object): "
          f"{len(m['conjunctive'])}  <- UNRULED, reported not decided")
    print(f"  qualified clauses (restriction the class slot cannot hold): "
          f"{len(m['qualified']):,}")
    print(f"  residual (action matched, no class named): {len(m['residual'])}")
    if args.residual:
        for name, clause in m["residual"][:60]:
            print(f"      {name}: {clause}")

    if args.audit:
        a = audit(args.action, domain)
        print("\n--- negative controls " + "-" * 50)
        print(f"  NC1 claimed without the printed verb "
              f"`{ACTION_VERBS[args.action]['word']}` (CR 701.8b): "
              f"{len(a['nc1_no_verb'])}   must be 0")
        print(f"  NC2 cards yielding nothing                   : "
              f"{a['nc2_silent']:,}")
        print(f"  NC3 clause only inside a quoted grant        : "
              f"{len(a['nc3_quoted_only'])}   reported, tagged on purpose")
        for n in a["nc3_quoted_only"]:
            print(f"        {n}")
        print(f"  NC4 emitted slugs failing validate_slug      : "
              f"{len(a['nc4_bad_slug'])}   must be 0")
        for slug, why in a["nc4_bad_slug"]:
            print(f"        {slug}: {why}")
        if a["nc1_no_verb"] or a["nc4_bad_slug"]:
            print("\n  AUDIT FAILED")
            return 1
        print("\n  audit clean")

    if args.samples:
        import random
        rng = random.Random(args.seed)
        by_class = defaultdict(list)
        for oid, r in m["hits"].items():
            for c in r["classes"]:
                by_class[c].append((oid, r["quotes"][c]))
        print(f"\n--- fixed-seed samples (seed {args.seed}) " + "-" * 30)
        cards, _, _ = fc.load_corpus_gated()
        for cls in sorted(by_class):
            pool = sorted(by_class[cls])
            pick = rng.sample(pool, min(args.samples, len(pool)))
            print(f"\n  {slug_for(args.action, cls)}  (n={len(pool)})")
            for oid, q in pick:
                print(f"      {cards[oid]['name']:<34} | {q[:78]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
