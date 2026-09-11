"""TARGET CLASSES — which battlefield-object class a targeted clause names. L2.

## What this owns

The pure half of the object lattice: the CR-derived type vocabulary, the
boundaries of a target's own noun phrase, and the classification of a targeted
clause into CR 110.4 permanent types. `measure`, `residual_invariant` and
`anchor_coverage` are the measurement surfaces over that classification.

**A `<type> card` IS NOT A PERMANENT** (CR 110.1 — *"A permanent is a card or
token on the battlefield"*). Card text names an object in a non-battlefield
zone as a CARD and an object on the battlefield by its permanent type, so
`creature card` is graveyard recursion and `creature` is the permanent. That
rule, and the arm-versus-phrase reading of a coordination that a printed zone
ORIGIN decides, are the two facts this module exists to get right.

## What this deliberately does NOT own

`rule:targeted-*` slug construction, the ratified-membership floor and its
assertion, the live codebook read, `validate_slug` governance, the baseline
metrics, the audit and exclusivity reports, the locality binding, the fixtures,
the ratchet wiring, the report writer and the CLI. Every one of those is a
later slice's, and none of them is duplicated here. A class slug is an IDENTITY
the codebook owns; this module answers a question about a clause.

## Inert until built

`PERMANENT_TYPES`, `CARD_TYPES`, `SUBTYPE_TO_TYPE`, `AMBIGUOUS_SUBTYPES` and
the CR 300.2 conjunctive pattern are DERIVED from the Comprehensive Rules, and
they are None until `build_vocabulary(cr_text, type_vocabulary)` runs. The
legacy boundary builds them at ITS import, exactly where they were built
before; an installed consumer calls the builder itself.

That is the whole reason this module has a builder at all: the values used to
be computed at import time by reading the repository's CR, which is precisely
what an installed library may not do.

## Layer law

Imports stdlib only — the CR text and the CR 205 type vocabulary arrive as
arguments, from the permanent CR substrate through a composition boundary. No
repository path, no root derivation, no import-time file read, no
`experiments`, no process exit: this module RAISES `LatticeError` and the
legacy shell re-establishes the historic `STOP — …` contract.
"""

from __future__ import annotations

import re
from collections import Counter


class LatticeError(RuntimeError):
    """A CR-vocabulary or lattice defect the pipeline refuses to proceed on."""


class ClauseTextRules:
    """The ratified DET preprocessing this module consumes but does not own.

    Every name is resolved ON THE PROVIDER AT CALL TIME, which is exactly how
    the moved code resolved it: `fc.<name>` was an attribute lookup per call,
    not a value captured once. Freezing a snapshot at install time would be a
    quiet behaviour change, and a ratified negative control proves it -- the
    locality write-boundary fixture REPLACES the CARDNAME canonicaliser at run
    time to force a reflow, and a snapshot would have made that control test
    nothing. It did: the first S7 pass captured values and the fixture went red.

    The provider is RECEIVED, never imported and never located. A missing name
    is refused loudly at install, not discovered at the first call.
    """

    REQUIRED = frozenset({"det_scan_texts"})

    def __init__(self, provider, names):
        missing = sorted(self.REQUIRED - set(names))
        extra = sorted(set(names) - self.REQUIRED)
        if missing or extra:
            raise LatticeError(
                f"card-text rules must name exactly {sorted(self.REQUIRED)}; "
                f"missing={missing} unexpected={extra}")
        for alias, attr in names.items():
            if not hasattr(provider, attr):
                raise LatticeError(
                    f"the supplied provider has no {attr!r} for {alias!r}")
        self._provider = provider
        self._names = dict(names)

    def __getattr__(self, item):
        try:
            attr = self._names[item]
        except KeyError:
            raise AttributeError(item) from None
        return getattr(self._provider, attr)


_CLAUSE_TEXT_RULES: ClauseTextRules | None = None


def use_clause_text_rules(rules: ClauseTextRules) -> None:
    """Install the injected clause-text rules. Called by the boundary, once."""
    global _CLAUSE_TEXT_RULES
    if not isinstance(rules, ClauseTextRules):
        raise LatticeError(f"clause-text rules must be a ClauseTextRules, got "
                           f"{type(rules).__name__}")
    _CLAUSE_TEXT_RULES = rules


def _rules() -> ClauseTextRules:
    if _CLAUSE_TEXT_RULES is None:
        raise LatticeError(
            "clause-text rules have not been installed. This substrate receives "
            "the ratified DET preprocessing from its composition boundary "
            "(`use_clause_text_rules`); it does not go looking for a repository "
            "to read it out of.")
    return _CLAUSE_TEXT_RULES


# THE DERIVED CR VOCABULARY, named in one place. Every name here is assigned by
# `build_vocabulary` and is None until it runs.
DERIVED_STATE = ("AMBIGUOUS_SUBTYPES", "CARD_TYPES", "PERMANENT_TYPES",
                 "SUBTYPE_TO_TYPE", "_CONJUNCTIVE_RE")

PERMANENT_TYPES = None
CARD_TYPES = None
SUBTYPE_TO_TYPE = None
AMBIGUOUS_SUBTYPES = None
_CONJUNCTIVE_RE = None


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


def permanent_types(cr_text: str) -> set:
    """CR 110.4's six, parsed. The rule states its own cardinality in words
    ('There are SIX permanent types'), so the guard compares the parsed list
    against the CR's OWN count rather than against a number typed here."""
    m = _PERMANENT_TYPES_RE.search(cr_text)
    if not m:
        raise LatticeError("Could not parse CR 110.4's permanent-type list. The CR's "
                           "wording has changed; fix the parser, never fall back to a "
                           "remembered list of six.")
    stated, parsed = m.group(1).lower(), _split_cr_list(m.group(2))
    want = _NUMBER_WORDS.get(stated)
    if want is None:
        raise LatticeError(f"CR 110.4 states its cardinality as {stated!r}, which this "
                           f"parser cannot read as a number.")
    if len(parsed) != want:
        raise LatticeError(f"CR 110.4 says there are {want} permanent types; the parse "
                           f"yielded {len(parsed)}: {sorted(parsed)}")
    return parsed


def card_types(cr_text: str) -> set:
    m = _CARD_TYPES_RE.search(cr_text)
    if not m:
        raise LatticeError("Could not parse CR 205.2a's card-type list.")
    return _split_cr_list(m.group(1))


def build_vocabulary(cr_text: str, type_vocabulary: dict) -> None:
    """Derive the CR vocabulary this module classifies against.

    Both inputs are EXPLICIT: the normalized Comprehensive Rules text, and the
    CR 205 type vocabulary the permanent CR substrate already parses. This
    module re-parses neither and locates neither.

    It also compiles CR 300.2's conjunctive pattern, which is a GRAMMAR over
    the parsed card types — two type words adjacent, naming one object — and so
    cannot exist before the vocabulary does.
    """
    global PERMANENT_TYPES, CARD_TYPES, SUBTYPE_TO_TYPE, AMBIGUOUS_SUBTYPES
    global _CONJUNCTIVE_RE
    PERMANENT_TYPES = permanent_types(cr_text)
    CARD_TYPES = card_types(cr_text)
    SUBTYPE_TO_TYPE = _subtype_map(type_vocabulary, PERMANENT_TYPES)
    AMBIGUOUS_SUBTYPES = {s for s, p in SUBTYPE_TO_TYPE.items() if len(p) > 1}
    # CR 300.2's conjunctive form: two type words adjacent, naming ONE object.
    _CONJUNCTIVE_RE = re.compile(
        rf"\b({'|'.join(sorted(CARD_TYPES))})\s+({'|'.join(sorted(CARD_TYPES))})\b",
        re.I)


# --------------------------------------------------------------------------
# subtype -> permanent type, derived from CR 205.3g-q
# --------------------------------------------------------------------------

def _subtype_map(type_vocabulary: dict, permanent: set) -> dict:
    """`Equipment` -> artifact, `Angel` -> creature, `Aura` -> enchantment.

The permanent CR substrate's `type_vocabulary` already parses all ten
    CR 205.3 subtype lists AND KEYS THEM BY THEIR PARENT TYPE, which is exactly
    this map — so it is consumed, not re-derived. Re-implementing a parse that
    already exists is this repo's most expensive recurring defect.

    Only the six CR 110.4 permanent types get a bucket. `spell_types` (CR
    205.3k) and `planar_types` are deliberately absent: an instant is not a
    permanent and cannot be destroyed (CR 701.8a), and plane layouts are
    outside Gate #0 anyway."""
    tv = type_vocabulary
    buckets = {
        "artifact": "artifact_types", "creature": "creature_types",
        "enchantment": "enchantment_types", "land": "land_types",
        "planeswalker": "planeswalker_types", "battle": "battle_types",
    }
    missing = sorted(set(buckets) - permanent)
    if missing:
        raise LatticeError(f"subtype map names {missing}, which CR 110.4 does not list as "
                           f"permanent types — the two CR rules have diverged.")
    unmapped = sorted(permanent - set(buckets))
    if unmapped:
        raise LatticeError(f"CR 110.4 permanent type(s) {unmapped} have no CR 205.3 "
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


# CR 110.4 names the six types; the cards also target the PERMANENT itself,
# with or without a negative qualifier. Every token here is already in the
# ratified grammar §5 OBJECT vocabulary (`permanent`, `nonland`, `noncreature`),
# so these compose rather than mint. A broad form is NOT OR-shaped — "nonland
# permanent" names one target of any nonland type — so it takes exactly its own
# tag and never the per-type ones, which would assert a reach the card lacks.
PERMANENT_FORMS = (
    ("noncreature-permanent", "noncreature permanent"),
    ("nonland-permanent", "nonland permanent"),
    ("permanent", "permanent"),
)



# Where the TARGET's own noun phrase ends. Everything past this belongs to the
# rest of the sentence and cannot supply the target's type.
_NP_END = re.compile(
    r"\b(?:from|in|into|onto|on|to|with|that|whose|unless|equal|where|"
    r"until|for|if)\b", re.I)

# CR 608.2c — *"the spell or ability's controller follows the instructions in
# the order written"*. `then` is how the CR's own templating writes the NEXT
# instruction, and a later instruction's objects are not this target's. Cutting
# here is what stops `exile target creature you control, THEN return those
# CARDS` from reading as a card-form.
_INSTRUCTION_END = re.compile(r",\s*then\b", re.I)

# CR 601.2c — *"the player announces their choice of an appropriate object or
# player for each target the spell requires"*. Only what falls under the
# printed `target` is a target, so an `and`-conjunct carrying its OWN determiner
# names a SECOND, untargeted object: Suspend Aggression's `exile target nonland
# permanent AND THE top card of your library`. The determiner is what separates
# it from a coordination INSIDE one target phrase (`artifact and/or enchantment
# cards`), where the arms share the single `target`.
_SECOND_OBJECT = re.compile(
    r"\band\s+(?:the|a|an|each|all|both|that|those|up\s+to|its|their|your)\b",
    re.I)

# A zone ORIGIN is what makes a coordinated `card` distribute across every arm.
# The recorded trap is the same shape one family over: the CR writes `put into
# <DESTINATION> from <ORIGIN>`, and `from` is what CLOSES the phrase. Pharika's
# Mender's `target creature or enchantment card FROM YOUR GRAVEYARD` names a
# card in a graveyard for BOTH arms; Venser's Diffusion's `target nonland
# permanent or suspended card` names no origin and its arms are independent.
_ZONE_ORIGIN = re.compile(
    r"\bfrom\b[^.;]*?\b(?:graveyard|exile|library|hand|stack|battlefield)\b",
    re.I)


def target_instruction(tail: str) -> str:
    """The clause tail truncated to the instruction the TARGET belongs to.

    **THE ZONE TEST BELOW MUST NOT READ A LATER INSTRUCTION'S ZONE.** Lukka,
    Coppercoat Outcast prints `exile target creature you control, then reveal
    cards FROM THE TOP OF YOUR LIBRARY`: that origin belongs to the reveal, not
    to the exile, and reading the whole tail scored Lukka as graveyard
    recursion. Measured 2026-08-13 — it is 1 of the 7.
    """
    end = _INSTRUCTION_END.search(tail)
    return tail[:end.start()] if end else tail


def target_noun_phrase(tail: str) -> str:
    """The span that actually names the target, out of a clause tail.

    **THE CLASS MUST COME FROM THE TARGET'S OWN NOUN PHRASE, NOT FROM ANYWHERE
    AFTER THE VERB.** The tail runs to the end of the sentence, so without this
    every type word downstream is a candidate class. Measured 2026-08-12 on the
    DET sample gate, before any codebook write: 83 of 2,653 memberships were
    decided by a word outside the target phrase, and fixing the two narrow
    causes only took it to 35, because they were symptoms rather than the
    cause.

    Two boundaries, and both are needed:

      * **the next printed `target`** starts a DIFFERENT target. Ragnarok,
        Divine Deliverance prints `destroy target permanent and return target
        nonlegendary permanent CARD`; it genuinely destroys a permanent, and
        truncating here is what keeps its correct membership while the card-form
        that follows stops being its business.
      * **the first preposition or relative pronoun** ends the noun phrase.
        Pharika's Mender prints `return target creature or enchantment CARD from
        your graveyard`, where `card` distributes across BOTH coordinated arms,
        so the whole phrase is graveyard recursion and neither arm is a
        permanent. Reading to `from` is what sees that; a per-word lookahead
        never can, because `creature` is followed by ` or`.

    Two more, added 2026-08-13 after Captain's read of the sample sheet found
    the boundary running PAST the target on seven cards — all seven regressions
    from the 2026-08-12 noun-phrase fix, which removed 170 memberships while
    verifying 83:

      * **`, then` ends the instruction** (CR 608.2c), so a later instruction's
        `cards` cannot refuse this target. Vengeful Pharaoh, Illusionist's
        Stratagem, Displace, Lukka.
      * **`and <determiner>` starts a SECOND object** (CR 601.2c), which the
        single printed `target` does not reach. Suspend Aggression, Become
        Anonymous. `and/or` is deliberately not matched — no determiner
        follows, and those arms share the one target.
    """
    tail = target_instruction(tail)
    cut = re.search(r"\btarget\b", tail)
    if cut:
        tail = tail[:cut.start()]
    second = _SECOND_OBJECT.search(tail)
    if second:
        tail = tail[:second.start()]
    end = _NP_END.search(tail)
    return tail[:end.start()] if end else tail


def names_type(text: str, word: str) -> bool:
    """True iff this clause names `word` as a PERMANENT (CR 110.1).

    **The FIRST occurrence decides, and a later bare occurrence must not
    rescue a refused one.** Found 2026-08-12 by the DET standing condition,
    before any codebook write, on 83 of 2,653 memberships:

      * `exile target creature CARD from a graveyard and untap this CREATURE`
        (Eater of the Dead) — the first `creature` is refused by CR 110.1, and
        a plain `re.search` for an unrefused occurrence then found the SECOND
        one, in `untap this creature`, which is not the target at all. 36 rows.
      * `Exile up to five target permanent CARDS from your graveyard`
        (Split the Spoils) — the per-type scan carried the `card` lookahead but
        `PERMANENT_FORMS` did not, and a broad form OUTRANKS the per-type read,
        so the refusal never got a chance to fire. 47 rows.

    Both are the same shape one layer apart: the lookahead was written per
    OCCURRENCE while the test was written per CLAUSE. `Ragnarok, Divine
    Deliverance` is the case that proves first-occurrence is the right rule
    rather than "refuse if any occurrence is a card-form": it prints
    `destroy target permanent AND return target nonlegendary permanent card`,
    genuinely destroys a permanent, and must keep its membership.
    """
    m = re.search(rf"\b{word}s?\b", text)
    if not m:
        return False
    return not re.match(r"\s+cards?\b", text[m.end():])



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
    text = target_noun_phrase(clause.lower())
    for rx in _NOT_THE_TARGET:
        text = rx.sub(" ", text)

    # CR 110.1 AT PHRASE LEVEL, NOT WORD LEVEL. `card` distributes across a
    # coordination: `target creature or enchantment CARD from your graveyard`
    # (Pharika's Mender) names a card in a graveyard for BOTH arms, so neither
    # is a permanent. A per-word lookahead cannot see that, because `creature`
    # is followed by ` or`. Once the span is the target's own noun phrase, one
    # `card` anywhere inside it disqualifies the whole phrase.
    # CR 110.1 AT ARM LEVEL WHEN THE ARMS ARE INDEPENDENT, AT PHRASE LEVEL WHEN
    # THEY SHARE A HEAD — and a printed zone ORIGIN is what tells them apart.
    #
    # Refusing the whole phrase on any `card` was right for Pharika's Mender and
    # wrong for Venser's Diffusion (`target nonland permanent or suspended
    # card`), where one arm is a battlefield permanent and the other is a card
    # in exile. Measured 2026-08-13 over all three actions: 50 residual clauses
    # carry an arm that resolves to a class, and the origin test splits them
    # 43 correct-residual / 7 false negatives with no overlap.
    scan = text
    if re.search(r"\bcards?\b", text):
        if _ZONE_ORIGIN.search(target_instruction(clause.lower())):
            return {"classes": set(), "broad": None, "via_subtype": {},
                    "conjunctive": [], "qualified": False}
        arms = [a for a in re.split(r",|\band/or\b|\bor\b|\band\b", text)
                if not re.search(r"\bcards?\b", a)]
        scan = " , ".join(a.strip() for a in arms if a.strip())
        if not scan:
            return {"classes": set(), "broad": None, "via_subtype": {},
                    "conjunctive": [], "qualified": False}

    text = scan
    conj = []
    for m in _CONJUNCTIVE_RE.finditer(text):
        a, b = m.group(1).lower(), m.group(2).lower()
        if a in domain and b in domain:
            conj.append((a, b))

    classes = {t for t in domain if names_type(text, t)}

    # A broad permanent form OUTRANKS the per-type read of the same clause.
    # "destroy target nonland permanent" contains no type word, but "destroy
    # target permanent that's an artifact or creature" would — and there the
    # types are a RESTRICTION on one broad target, not two targets.
    broad = None
    for form, word in PERMANENT_FORMS:
        if names_type(text, word):
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
            # Same first-occurrence rule: without it, refusing `creature
            # card` above just hands the clause to the SUBTYPE path, which
            # re-adds creature from `Assassin creature card` (Altair).
            if parent in domain and names_type(text, re.escape(sub)):
                classes.add(parent)
                via_subtype[sub] = parent

    qualified = bool(re.search(r"\bwith \w+|\bthat\b|\bwhose\b|\bif it\b", text))
    return {"classes": {broad} if broad else classes, "broad": broad,
            "via_subtype": via_subtype, "conjunctive": conj,
            "qualified": qualified}


def clauses_for(card: dict, stem: str):
    """Every targeted clause of one action on one card, over the RATIFIED DET
    preprocessing (all faces, CARDNAME canonicalized, modal bullets expanded).

    Consuming the ratified DET preprocessing is not optional: a probe that
    matched raw lines under-reported by 43 on 2026-08-05, and the four consumers
    that use it are outnumbered by nineteen that do not. It arrives INJECTED,
    because its permanent home is a later slice's decision."""
    rx = _CLAUSE_RES[stem]
    for text in _rules().det_scan_texts(card):
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



# --------------------------------------------------------------------------
# measurement CLI
# --------------------------------------------------------------------------

def measure(stem: str, domain: set, cards: dict) -> dict:
    """The per-class census of one action over an EXPLICIT card population.

    The corpus arrives as an argument. A substrate function that loaded the
    corpus itself would have to know where the repository is."""
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


def residual_invariant(stem: str, domain: set, cards: dict,
                      selftest: bool = False) -> dict:
    """THE RESIDUAL INVARIANT — Captain's, 2026-08-13.

    *"After classification, inspect every residual clause again. If a residual
    still contains a target branch that resolves through the ratified
    type/subtype vocabulary to one of your recognized battlefield-object
    classes, HALT."*

    **A GUARD COMPUTED WITH THE CLASSIFIER'S OWN RESOLVER IS A NO-OP BY
    CONSTRUCTION**, so this one is deliberately not that. It scans the RAW
    clause tail — never `target_noun_phrase` — which makes it independent of
    the boundary logic, and the boundary is exactly where the seven false
    negatives came from. A future re-truncation cannot hide from it.

    Being deliberately over-broad, it flags every coordinated `<type> or
    <type> card` too. Those are CORRECT residual, and each is explained by a
    printed CR zone ORIGIN, so a flagged row is accounted for in one of exactly
    two ways:

      * the classifier claimed the arm  -> not residual, nothing to explain;
      * the instruction prints `from <zone>` -> CR 110.1 graveyard recursion,
        the `card` distributes across the arms (Pharika's Mender).

    Anything else is an UNEXPLAINED live arm and halts the pass before
    provenance writes, which is the standing `det-patterns-v2.json` condition.

    `selftest=True` disables the zone explanation, so every explained row
    becomes unexplained. A guard that has never been shown to fail is not known
    to be a guard.
    """
    explained, unexplained = [], []
    for oid, card in sorted(cards.items(), key=lambda kv: kv[1]["name"]):
        if classes_for_card(card, stem, domain)["classes"]:
            continue
        for whole, tail in clauses_for(card, stem):
            span = target_instruction(tail.lower())
            for arm in re.split(r",|\band/or\b|\bor\b|\band\b", span):
                arm = arm.strip()
                if not arm or re.search(r"\bcards?\b", arm):
                    continue
                cls = None
                for form, word in PERMANENT_FORMS:
                    if names_type(arm, word):
                        cls = form
                        break
                if cls is None:
                    named = {t for t in domain if names_type(arm, t)}
                    cls = "+".join(sorted(named)) if named else None
                if cls is None:
                    for sub, parents in SUBTYPE_TO_TYPE.items():
                        if len(parents) == 1 and next(iter(parents)) in domain \
                                and names_type(arm, re.escape(sub)):
                            cls = next(iter(parents))
                            break
                if cls is None:
                    continue
                row = (card["name"], arm, cls, whole.strip()[:100])
                if not selftest and _ZONE_ORIGIN.search(span):
                    explained.append(row)
                else:
                    unexplained.append(row)
    return {"explained": explained, "unexplained": unexplained}


def anchor_coverage(anchors, cards: dict) -> dict:
    """Which live classes have an anchor and which do not.

    Reported, never fatal. A class with members and no anchor is a KNOWN blind
    spot for zero-sum movement, and naming it is the difference between a gap
    and an unknown. Zero members is a hypothesis, not an absence (the
    `is-attacked-trigger` precedent), so an empty class needs no anchor.

    The anchor TABLE is passed in. It is ratified fixture data owned by the
    boundary that replays it; the reusable capability is the comparison.
    """
    have = {(s, c) for s, c, _ in anchors}
    live, uncovered = set(), []
    for stem in sorted(ACTION_VERBS):
        for cls in measure(stem, PERMANENT_TYPES, cards)["per_class"]:
            live.add((stem, cls))
            if (stem, cls) not in have:
                uncovered.append(f"{stem}-{cls}")
    return {"live": len(live), "anchored": len(have & live),
            "uncovered": sorted(uncovered)}
