#!/usr/bin/env python3
"""THE QUALIFIER CENSUS — how often a broad object fact omits a restriction.

WHY THIS FILE EXISTS
--------------------
`docs/PICK-UP-HERE.md` §0AB (committed) tells the next arc to use *"48.0% of
2,106 clauses"*, *"×9.2"* and *"68.0% / 68.3%"*. Those numbers live in
`docs/FACT-GRANULARITY-CENSUS-INDEPENDENT-VERIFICATION-2026-08-13.md`, whose
own §V records: *"Verification code was run from the session scratchpad and is
not added to the repository."*

So a committed document points at numbers **no tool in this repository can
re-derive**. That is CLAUDE.md's two most-cited traps at once -- *a count is
not a measurement* and *a carried-forward count in a handoff is not a
measurement* -- aimed at the document that governs the next arc. This file is
the fix: the qualifier packet cites a COMMAND, not a handoff line.

    python3 experiments/foundry_qualifier_census.py            # the report
    python3 experiments/foundry_qualifier_census.py --json     # machine-readable
    python3 experiments/foundry_qualifier_census.py --selftest # negative controls
    python3 experiments/foundry_qualifier_census.py --gate     # Gate 2 row

WHAT IT MEASURES, AND THE ONE THING IT CANNOT
---------------------------------------------
It measures what is TRUE OF the clauses the object lattice classifies. It does
**not** independently verify WHICH clauses the lattice classifies -- there is
no second implementation of the lattice, and this module consumes
`foundry_object_lattice.classify_clause` directly. Any recall defect in the
lattice is inherited here silently. That boundary is stated in the report
output as well as here, because the prior verification report was read as
though it settled both questions and it never could.

THE METHOD: RESIDUAL, NOT CATEGORY MATCH
-----------------------------------------
The superseded census asked *"does category regex X match?"* and therefore
could only ever find the categories somebody had already thought of. It had no
CR 702 keyword category at all, so `destroy target creature with flying` scored
**unrestricted** -- 110 false negatives.

This module inverts that. It strips the template scaffolding and the base-class
words THE CLASSIFIER ITSELF USED, and asks what content tokens remain. **A
remaining token is a restriction by construction.** Categories are applied
afterwards and are purely DESCRIPTIVE: a token nobody wrote a category for
lands in `uncategorized`, where it is reported loudly, and the measured
qualifier RATE does not move. That is the structural property the old detector
lacked, and `--selftest` NC4 proves it by deleting the keyword category and
checking the rate holds while `uncategorized` rises.

THE COUNTING KEY, WHICH IS WHERE THE PRIOR NUMBER WENT WRONG
-------------------------------------------------------------
`clauses_for` iterates every `det_scan_texts` variant -- `[canonical full text,
*modal-bullet expansions]` -- so a clause inside a modal bullet is yielded
twice. That is harmless for MATCHING (`classes_for_card` unions) and fatal for
COUNTING. Raw classified yields: **2,389**, which is exactly the superseded
census's published denominator.

The prior verification deduped by `(card, stem, clause text)` **case-folded**
and published **2,106**. Case-folding is one step too far, and it is
measurable:

  * **Seize the Soul** prints `Destroy target nonwhite, nonblack creature` as
    its spell effect (paragraph 0) and `destroy target nonwhite, nonblack
    creature` inside its Haunt trigger (paragraph 2). `foundry_locality.resolve`
    reports AMBIGUOUS across `(0,0)` and `(0,2)` -- the repository's own
    ratified machinery calls them TWO SEMANTIC UNITS. Case-folding merges them.

Dropping the case-fold gives 2,107. Counting OCCURRENCES rather than distinct
strings gives **2,110**, and the three extra rows are all genuine:

  * **Ugin, Eye of the Storms** -- a cast trigger and a separate whenever
    trigger printing the same clause;
  * **Act of Authority** -- an enters trigger and an upkeep trigger;
  * **Outland Liberator // Frenzied Trapbreaker** -- the same activated ability
    printed on BOTH FACES of a DFC.

Every one is two abilities that would carry two addresses under FL-2, so
merging them under-counts the thing the census exists to measure. **The default
key is the OCCURRENCE**, and all three keys are reported so a later packet can
say which one it means.

The dedupe is done by reading **only `det_scan_texts()[0]`**, the canonical full
text, which removes every preprocessing duplicate by construction rather than
by string comparison. That is safe only if no classified clause is reachable
ONLY through an expansion -- measured zero, and asserted every run by
`gate_expansion_adds_no_clause()` rather than assumed.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
It mints nothing. No axis, no slug, no predicate, no facet, no schema field, no
codebook write. It does not resolve AQ4 or AQ5, and it is not a production
qualifier emitter. It is the measurement half, exactly as
`foundry_object_lattice` was before its ratification.
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
import foundry_object_lattice as ol          # noqa: E402
import foundry_probe as p                    # noqa: E402

# `p.corpus()` is deliberately NOT used to stand this up. It builds the
# DELIVERY classifier's order-dependent module state (`build_self_noun_rx`,
# `build_keyword_homes`), which this census never consumes -- guard A is about
# using ONE canonical corpus entry point, and `fc.load_corpus_gated()` is that
# entry point, the same one `foundry_object_lattice` itself calls. Guards C and
# D are used, below, where they aim at a defect this module can actually have.


# --------------------------------------------------------------------------
# CR-derived vocabulary. Every closed list here is PARSED, never typed.
# --------------------------------------------------------------------------

_COLORS_RE = re.compile(
    r"^105\.1\.?\s+There are (\w+) colors in the Magic game:\s*([^.]+)\.", re.M)
_SUPERTYPES_RE = re.compile(r"The supertypes are\s*([^.]+)\.", re.M)


def colors(path: Path = None) -> set:
    """CR 105.1's five, parsed, with the rule's OWN stated cardinality as the
    guard. Same shape as `foundry_object_lattice.permanent_types` -- a count
    typed here would be the hand-list this house forbids one indirection out."""
    m = _COLORS_RE.search(cr.text(path) if path else cr.text())
    if not m:
        fc.halt("Could not parse CR 105.1's colour list. The CR's wording has "
                "changed; fix the parser, never fall back to a remembered five.")
    stated, parsed = m.group(1).lower(), ol._split_cr_list(m.group(2))
    want = ol._NUMBER_WORDS.get(stated, 5 if stated == "five" else None)
    if want is None:
        fc.halt(f"CR 105.1 states its cardinality as {stated!r}, unreadable.")
    if len(parsed) != want:
        fc.halt(f"CR 105.1 says {want} colours; the parse yielded "
                f"{len(parsed)}: {sorted(parsed)}")
    return parsed


def supertypes(path: Path = None) -> set:
    """CR 205.4a. No stated cardinality in the rule, so the guard is CONTENT --
    a count cannot see a substitution (`type_vocabulary`'s `and world`)."""
    m = _SUPERTYPES_RE.search(cr.text(path) if path else cr.text())
    if not m:
        fc.halt("Could not parse CR 205.4a's supertype list.")
    parsed = ol._split_cr_list(m.group(1))
    if not {"basic", "legendary", "snow", "world"} <= parsed:
        fc.halt(f"CR 205.4a supertype parse lost a known member: "
                f"{sorted(parsed)}")
    return parsed


def cr_keyword_names(path: Path = None) -> set:
    """CR 702 keyword names, by the SAME derivation `foundry_shape_extractor`
    uses -- `load_702` minus the preamble rule. Not `KEYWORD_HOME`: the
    recorded trap is that a DERIVED MAP IS NOT THE LIST IT WAS DERIVED FROM,
    and `build_keyword_homes` skips any keyword whose home cannot be derived,
    so asking it "is this a keyword?" answers no for `awaken` and `impending`.

    This is the category the superseded census lacked entirely -- 110 false
    negatives, `with flying` and `with defender` among them."""
    kws = crc.load_702(path or crc.CR_PATH)
    names = {kw["name"].lower() for num, kw in kws.items()
             if kw["name"] and num != crc.PREAMBLE_RULE}
    if not {"flying", "defender", "trample", "ward"} <= names:
        fc.halt(f"CR 702 keyword-name parse lost a keyword the qualifier "
                f"census is measured against. got {len(names)} names.")
    return names


COLORS = colors()
SUPERTYPES = supertypes()
KEYWORDS = cr_keyword_names()
MULTIWORD_KEYWORDS = sorted((k for k in KEYWORDS if " " in k),
                            key=len, reverse=True)


# --------------------------------------------------------------------------
# Spans that are NOT target eligibility
# --------------------------------------------------------------------------

# Each opener ends the target's eligibility description and starts something
# else, and each carries the CR rule that says so. Everything from the first
# match to the end of the span is recorded as non-eligibility residue and
# excluded from the qualifier measurement -- reported, never silently dropped.
_NON_ELIGIBILITY = (
    # CR 611.2a -- a continuous effect "lasts as long as stated ... (such as
    # 'until end of turn')". `exile target creature an opponent controls UNTIL
    # THIS CREATURE LEAVES THE BATTLEFIELD` is a duration on the exile, not a
    # restriction on what may be exiled. 89 clauses print it.
    ("duration", re.compile(r"\b(?:until|for as long as)\b", re.I)),
    # CR 107.3 -- X is a placeholder whose value is defined elsewhere;
    # `where X is the number of ...` defines the COUNT, not the target.
    ("x-definition", re.compile(r"\bwhere\s+x\b", re.I)),
    # CR 603.2 -- a trigger's timing. `Destroy target blocking creature AT END
    # OF COMBAT` times the destruction; `blocking` is the restriction.
    ("action-timing", re.compile(r"\bat (?:end of|the beginning of)\b", re.I)),
    # CR 601.2b -- an additional cost or an escape hatch attached to the
    # effect. `unless its controller pays {2}` is not an eligibility test.
    ("unless-clause", re.compile(r"\bunless\b", re.I)),
)


def eligibility_span(tail: str) -> tuple:
    """The span that describes WHICH object may be chosen, plus what was cut.

    **This deliberately does NOT use `target_noun_phrase`.** That helper ends
    the span at `_NP_END`, which includes `with` and `that` -- precisely where
    qualifiers are printed. Reading the noun phrase would score `destroy target
    creature with flying` as unrestricted, which is the exact false negative
    this module exists to remove. The lattice needs the narrow span to decide a
    CLASS; the census needs the wide one to see a RESTRICTION, and they are
    different questions on the same string.

    The three cuts that ARE kept are the ones that end the target itself:
      * CR 608.2c -- `, then` starts the next instruction;
      * CR 601.2c -- a second printed `target` is a different target;
      * CR 601.2c -- `and <determiner>` names a second, untargeted object.
    """
    t = ol.target_instruction(tail)
    cut = re.search(r"\btarget\b", t)
    if cut:
        t = t[:cut.start()]
    second = ol._SECOND_OBJECT.search(t)
    if second:
        t = t[:second.start()]

    removed = {}
    for name, rx in _NON_ELIGIBILITY:
        m = rx.search(t)
        if m:
            removed[name] = t[m.start():].strip()
            t = t[:m.start()]
    return t, removed


# --------------------------------------------------------------------------
# Scaffolding
# --------------------------------------------------------------------------

# ENGLISH FUNCTION WORDS AND THE LATTICE'S OWN TEMPLATE TOKENS.
#
# CLAUDE.md's rule is that a hand-list is a defect with a delay *when the CR
# publishes the list*. The CR publishes card types, subtypes, supertypes,
# colours and keywords -- all five are parsed above. It does not publish
# English grammar, and there is no rule to derive `the` from. CR 207.2d's
# precedent governs: a list the CR does not enumerate is the one honest place a
# declared list may stand. So this is declared, kept to closed-class function
# words, and negative-controlled -- NC5 proves that removing a word from it
# cannot lower the measured rate, only raise `uncategorized`.
#
# Words that LOOK like function words and are deliberately absent, because each
# carries a real restriction: you, your, own, owns, control, controls, player,
# opponent, defending, another, other, don't, doesn't.
_SCAFFOLDING = {
    # determiners / articles
    "a", "an", "the", "this", "that", "these", "those", "its", "their", "it",
    "there", "one",
    # the lattice's printed template (`_TARGET_HEAD`, `_CLAUSE_TAIL`)
    "target", "up", "to", "each", "all", "and", "or",
    # copulas / relativisers that only introduce a restriction, never are one
    "is", "are", "was", "be", "been", "has", "have", "had", "s", "'s", "that's",
    "who", "whose", "which", "then", "of", "in", "on", "at", "by", "as", "than",
    "from", "into", "onto", "for", "with", "without", "any",
}

# `up to N` -- the number words the lattice's own `_TARGET_HEAD` admits. Parsed
# from the lattice rather than retyped, so the two cannot drift apart.
_SCAFFOLDING |= set(ol._NUMBER_WORDS)


def _strip_base_classes(span: str, cls: dict) -> str:
    """Remove the words the CLASSIFIER ITSELF consumed to decide the class.

    This is the `nonland` requirement: `destroy target nonland permanent`
    yields the broad class `nonland-permanent`, so BOTH `nonland` and
    `permanent` are base-class words and neither may be counted as an
    additional qualifier. Scoring `nonland` twice was one of the superseded
    census's two self-corrected defects, and NC2 proves this strip is what
    prevents it rather than a happy accident of the token list.

    Only what the classifier used is removed. `destroy up to one target
    NONCREATURE artifact` classifies as `artifact`, so `noncreature` survives
    and is correctly a qualifier.

    **A SUBTYPE IS NOT A BASE CLASS, AND STRIPPING IT WAS A REAL FALSE NEGATIVE
    IN THIS MODULE'S FIRST DRAFT.** `classify_clause` routes `destroy target
    Wall` to `creature` through CR 205.3g-q, and the axis it lands on is
    `targeted-destroy-creature` -- which does NOT encode `Wall`. So the subtype
    is exactly the kind of restriction a broad object fact omits, and it must
    be counted, not stripped. 60 clauses turn on this (Equipment 9, Aura 9,
    Wall 7, Island 4), and the prior verification agrees: its §M reads Active
    Volcano's bounce mode as restricted to an **Island**. The test is the
    EMITTED CLASS NAME, never the path taken to reach it.

    `conjunctive` pairs are different and ARE stripped: CR 300.2's `artifact
    creature` names one object of two types, and the card takes BOTH class
    tags, so neither word is an unencoded restriction. The lattice reports that
    shape as unruled, and this module reports it rather than deciding it.
    """
    words = set()
    for c in cls["classes"]:
        words |= set(c.split("-"))
    for a, b in cls["conjunctive"]:
        words |= {a, b}
    for w in sorted(words, key=len, reverse=True):
        span = re.sub(rf"\b{re.escape(w)}(?:s|es)?\b", " ", span)
    return span


# `another target creature` -- the restriction that lives in the lattice's own
# `_TARGET_HEAD`, BEFORE the tail this module is handed, and therefore invisible
# to a residual method reading the tail alone. 58 classified clauses print it
# and 26 carry no other restriction, so omitting it is a false negative of
# exactly the kind this module exists to remove.
#
# **ITS ANCHOR IS THE PRINTED TEMPLATE, NOT A CR ENUMERATION, AND THAT IS
# STATED RATHER THAN DRESSED UP.** The CR has no rule defining "another" as a
# quantifier -- searched, and the four rules that use the word are about zones,
# continuous effects and DFC faces. So this is a declared restriction under the
# CR 207.2d precedent (a list the CR does not enumerate is the one honest place
# a declared list may stand), not a CR-derived one.
#
# `up to N`, `each` and `all` are deliberately NOT captured: they set how MANY
# objects are chosen, not WHICH objects qualify. 164 clauses print one, and
# counting cardinality as eligibility would inflate the headline by 7.8 points.
_HEAD_RESTRICTION = re.compile(r"\b(another)\s+target\b", re.I)


def residual(tail: str, cls: dict, whole: str = "") -> dict:
    """The restriction tokens a clause carries beyond its base object class."""
    span, removed = eligibility_span(tail)
    if whole:
        m = _HEAD_RESTRICTION.search(whole)
        if m:
            span = m.group(1) + " " + span
    span = _strip_base_classes(span.lower(), cls)

    # Multi-word CR terms first, longest-first, so `first strike` cannot be
    # tokenized into `first` + `strike` and land in `uncategorized`, and
    # `mana value` cannot be read as two unrelated tokens.
    phrases = []
    for kw in MULTIWORD_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", span):
            phrases.append(kw)
            span = re.sub(rf"\b{re.escape(kw)}\b", " ", span)
    for phrase in ("mana value", "power or toughness"):
        if re.search(rf"\b{phrase}\b", span):
            phrases.append(phrase)
            span = re.sub(rf"\b{phrase}\b", " ", span)

    toks = [t for t in re.findall(r"[a-z][a-z'\-]*|\d+", span)
            if t not in _SCAFFOLDING]
    # A bare `non` survives hyphen splitting on `non-Saga`; it is a negation
    # marker, not a token of its own.
    toks = [t for t in toks if t != "non"]
    return {"tokens": sorted(set(toks + phrases)),
            "non_eligibility": removed}


# --------------------------------------------------------------------------
# Categories -- DESCRIPTIVE ONLY. They cannot change the qualifier rate.
# --------------------------------------------------------------------------

_NEG = re.compile(r"^non-?")
_SUBTYPES = {s.lower() for s in ol.SUBTYPE_TO_TYPE}


def _base(tok: str) -> str:
    return _NEG.sub("", tok).rstrip("s")


# The three CR-derived categories are exact-membership tests against a parsed
# closed list. The four behavioural ones are declared word sets: they describe
# the residual, and under-coverage shows up as `uncategorized` rather than as a
# lower rate. NC4 is the proof.
_CONTROLLER = {"you", "your", "opponent", "opponents", "control", "controls",
               "controlled", "own", "owns", "owned", "player", "players",
               "defending", "don't", "doesn't"}
_NUMERIC = {"power", "toughness", "mana value", "greater", "less", "least",
            "most", "equal", "exactly", "number", "x", "counter", "counters",
            "or greater", "or less", "power or toughness"}
_STATE = {"tapped", "untapped", "attacking", "blocking", "blocked", "attacked",
          "dealt", "damage", "damaged", "enchanted", "equipped", "face",
          "down", "monstrous", "suspended", "renowned", "transformed",
          "kicked", "crewed", "turn", "colors", "color", "shares", "phased"}
# `another` / `other` restrict object IDENTITY (not this object), which is a
# different dimension from who CONTROLS it -- Noxious Gearhulk's `destroy
# another target creature` says nothing about controllers.
_IDENTITY = {"token", "nontoken", "named", "name", "same", "spell", "spells",
             "another", "other"}
_CONDITION = {"if", "could", "can", "can't"}


def categorize(tokens: list) -> dict:
    """token -> category. `uncategorized` is a real bucket and is reported."""
    out = defaultdict(list)
    for t in tokens:
        b = _base(t)
        # EVERY BRANCH TESTS BOTH THE RAW TOKEN AND ITS NEGATION/PLURAL-STRIPPED
        # FORM. Testing only the stripped form put `plains` in `uncategorized`
        # -- `_base` takes it to `plain`, which is not a CR 205.3j land type,
        # while `plains` is. Four clauses, and it was visible only because
        # `uncategorized` is printed rather than swallowed.
        if t in KEYWORDS or b in KEYWORDS:
            out["keyword"].append(t)
        elif t in COLORS or b in COLORS or \
                b in {"colorless", "multicolored", "monocolored"}:
            out["color"].append(t)
        elif t in SUPERTYPES or b in SUPERTYPES:
            out["supertype"].append(t)
        elif t in ol.CARD_TYPES or b in ol.CARD_TYPES or \
                t in _SUBTYPES or b in _SUBTYPES:
            out["type"].append(t)
        elif t in _CONTROLLER or b in _CONTROLLER:
            out["controller"].append(t)
        elif t in _NUMERIC or b in _NUMERIC or t.isdigit():
            out["numeric"].append(t)
        elif t in _STATE or b in _STATE:
            out["state"].append(t)
        elif t in _IDENTITY or b in _IDENTITY:
            out["identity"].append(t)
        elif t in _CONDITION:
            out["condition"].append(t)
        else:
            out["uncategorized"].append(t)
    return dict(out)


# --------------------------------------------------------------------------
# Population -- the counting key
# --------------------------------------------------------------------------

def population(cards=None) -> list:
    """Every classified target clause, ONE ROW PER OCCURRENCE.

    Reads only `det_scan_texts()[0]`, the canonical full text. Every modal
    expansion is derived from that text, so reading one variant removes the
    preprocessing duplicate BY CONSTRUCTION instead of by string comparison --
    and string comparison is what merged Seize the Soul's two abilities.
    `gate_expansion_adds_no_clause()` is what makes that safe rather than
    assumed.
    """
    if cards is None:
        cards, _, _ = fc.load_corpus_gated()
    rows = []
    for oid, card in sorted(cards.items()):
        base = list(fc.det_scan_texts(card))[0]
        for stem in sorted(ol.ACTION_VERBS):
            for i, m in enumerate(ol._CLAUSE_RES[stem].finditer(base)):
                cls = ol.classify_clause(m.group(1), ol.PERMANENT_TYPES)
                if not cls["classes"]:
                    continue
                res = residual(m.group(1), cls, m.group(0))
                rows.append({
                    "oracle_id": oid, "name": card["name"], "stem": stem,
                    "occurrence": i, "clause": m.group(0).strip(),
                    "classes": sorted(cls["classes"]),
                    "tokens": res["tokens"],
                    "non_eligibility": res["non_eligibility"],
                    "categories": categorize(res["tokens"]),
                })
    return rows


def _rate(rows, pred=None):
    sel = [r for r in rows if pred(r)] if pred else rows
    q = [r for r in sel if r["tokens"]]
    return len(q), len(sel), (100.0 * len(q) / len(sel) if sel else 0.0)


def census(rows=None) -> dict:
    rows = rows if rows is not None else population()

    qualified, total, rate = _rate(rows)
    strict = [r for r in rows
              if [t for t in r["tokens"]
                  if "condition" not in categorize([t])]]

    # UPPER BOUND -- non-eligibility residue counted as qualification too. The
    # prior verification published both (48.0% eligibility-only against 48.6%
    # any-residual) precisely because the two nearly coincide; publishing the
    # pair is what makes the eligibility boundary auditable rather than
    # asserted.
    upper = sum(1 for r in rows if r["tokens"] or r["non_eligibility"])
    only_ne = sum(1 for r in rows if not r["tokens"] and r["non_eligibility"])

    cat_clauses, cat_tokens = Counter(), Counter()
    for r in rows:
        for c, toks in r["categories"].items():
            cat_clauses[c] += 1
            cat_tokens[c] += len(toks)

    # THE BASE UNIT IS THE (stem, class) AXIS, NOT THE CLASS. `creature` is not
    # a fact; `targeted-destroy-creature` is -- it is the slug the lattice
    # emits, and it is what a compound qualifier axis would multiply. Counting
    # bare classes gives 9 and makes the expansion look 1.6x worse than it is.
    # This reproduces the prior reports' 23 exactly, which is what confirmed
    # the definition rather than guessing at it.
    axes = {(r["stem"], c) for r in rows for c in r["classes"]}

    # Order-normalised (frozenset) so ordering cannot duplicate a shape, and a
    # clause naming several classes contributes one pair per axis -- the rule
    # the prior reports used, kept so the numbers stay comparable.
    combos = set()
    for r in rows:
        cats = frozenset(c for c in r["categories"] if c != "uncategorized")
        for cls in r["classes"]:
            combos.add(((r["stem"], cls), cats))

    per_axis = {}
    for stem, cls in sorted(axes):
        q, n, pc = _rate(rows, lambda r, s=stem, c=cls:
                         r["stem"] == s and c in r["classes"])
        per_axis[ol.slug_for(stem, cls)] = {
            "clauses": n, "qualified": q, "rate": round(pc, 1)}

    per_stem = {}
    for stem in sorted(ol.ACTION_VERBS):
        q, n, pc = _rate(rows, lambda r, s=stem: r["stem"] == s)
        per_stem[stem] = {"clauses": n, "qualified": q, "rate": round(pc, 1)}

    kw_rows = [r for r in rows if "keyword" in r["categories"]]
    uncat = Counter(t for r in rows for t in r["categories"].get(
        "uncategorized", []))
    nonelig = Counter(k for r in rows for k in r["non_eligibility"])

    return {
        "counting_key": "(oracle_id, stem, occurrence index in det_scan_texts[0])",
        "clause_occurrences": total,
        "qualified_clauses": qualified,
        "qualifier_rate": round(rate, 1),
        "qualified_excluding_condition_only": len(strict),
        "rate_excluding_condition_only": round(100.0 * len(strict) / total, 1)
        if total else 0.0,
        "qualified_upper_bound_any_residue": upper,
        "rate_upper_bound_any_residue": round(100.0 * upper / total, 1)
        if total else 0.0,
        "clauses_with_only_non_eligibility_residue": only_ne,
        "base_class_axes": len(axes),
        "class_x_qualifier_combinations": len(combos),
        "combination_expansion": round(len(combos) / len(axes), 1)
        if axes else 0.0,
        "per_axis": per_axis,
        "per_stem": per_stem,
        "categories_by_clause": dict(sorted(cat_clauses.items())),
        "categories_by_token": dict(sorted(cat_tokens.items())),
        "cr702_keyword_clauses": len(kw_rows),
        "cr702_keywords_seen": sorted({t for r in kw_rows
                                       for t in r["categories"]["keyword"]}),
        "non_eligibility_spans": dict(sorted(nonelig.items())),
        "uncategorized_tokens": dict(uncat.most_common(40)),
        "uncategorized_distinct": len(uncat),
        "vocabulary": {
            "cr105_1_colors": sorted(COLORS),
            "cr205_4a_supertypes": sorted(SUPERTYPES),
            "cr702_keyword_names": len(KEYWORDS),
            "cr205_2a_card_types": len(ol.CARD_TYPES),
            "cr110_4_permanent_types": sorted(ol.PERMANENT_TYPES),
        },
    }


def counting_keys(cards=None) -> dict:
    """Every key that has been used to count this population, side by side.

    Published so a later packet can say WHICH denominator it means. The
    superseded reports each quoted one of these without naming it, which is how
    2,389 and 2,106 both ended up in circulation as "the" number.
    """
    if cards is None:
        cards, _, _ = fc.load_corpus_gated()
    raw = 0
    occ = 0
    distinct, folded = set(), set()
    for oid, card in cards.items():
        variants = list(fc.det_scan_texts(card))
        for stem in sorted(ol.ACTION_VERBS):
            rx = ol._CLAUSE_RES[stem]
            for m in rx.finditer(variants[0]):
                if ol.classify_clause(m.group(1), ol.PERMANENT_TYPES)["classes"]:
                    occ += 1
            for text in variants:
                for m in rx.finditer(text):
                    if not ol.classify_clause(
                            m.group(1), ol.PERMANENT_TYPES)["classes"]:
                        continue
                    raw += 1
                    distinct.add((oid, stem, m.group(0)))
                    folded.add((oid, stem, m.group(0).lower()))
    return {
        "raw_yields_all_variants": raw,
        "occurrences_canonical_text": occ,
        "distinct_strings": len(distinct),
        "distinct_strings_case_folded": len(folded),
    }


# --------------------------------------------------------------------------
# Guards and negative controls
# --------------------------------------------------------------------------

def gate_expansion_adds_no_clause(cards=None) -> list:
    """THE PREMISE OF THE COUNTING KEY, ASSERTED RATHER THAN ASSUMED.

    Reading only the canonical text is safe iff no classified clause is
    reachable ONLY through a modal expansion. Measured zero today. If
    `expand_modal_bullets` ever produces a clause the full text cannot match --
    a header joined to a bullet, say -- this halts instead of silently
    shrinking the census.
    """
    if cards is None:
        cards, _, _ = fc.load_corpus_gated()
    missed = []
    for oid, card in cards.items():
        variants = list(fc.det_scan_texts(card))
        if len(variants) < 2:
            continue
        base = variants[0]
        for stem in sorted(ol.ACTION_VERBS):
            for text in variants[1:]:
                for m in ol._CLAUSE_RES[stem].finditer(text):
                    if not ol.classify_clause(
                            m.group(1), ol.PERMANENT_TYPES)["classes"]:
                        continue
                    if m.group(0) not in base:
                        missed.append((card["name"], stem, m.group(0)[:70]))
    return missed


class _Case:
    """A synthetic clause. Fixtures are card-shaped, never card-specific: the
    house rule is that named cards are good fixtures and production rules must
    generalize, so these assert the RULE and name the card that proved it."""

    def __init__(self, tail, want_qualified, want_cats=(), why="", whole=""):
        self.tail, self.want = tail, want_qualified
        self.cats, self.why = set(want_cats), why
        # The clause as printed, when the case turns on something OUTSIDE the
        # tail -- `another target creature` lives in `_TARGET_HEAD`.
        self.whole = whole


_CASES = [
    _Case(" creature", False, (), "bare base class carries no restriction"),
    _Case(" nonland permanent", False, (),
          "NC2: `nonland` is the base class, not a qualifier"),
    _Case(" noncreature artifact", True, {"type"},
          "`noncreature` survives because the class is artifact"),
    _Case(" creature with flying", True, {"keyword"},
          "NC4: CR 702 keyword restriction (Oran-Rief Recluse)"),
    _Case(" creature with defender", True, {"keyword"},
          "CR 702 keyword restriction (Clear a Path)"),
    _Case(" blue permanent", True, {"color"},
          "CR 105.1 colour restriction (Active Volcano)"),
    _Case(" creature an opponent controls", True, {"controller"},
          "controller restriction"),
    _Case(" creature with power 3 or greater", True, {"numeric"},
          "numeric eligibility"),
    _Case(" tapped creature", True, {"state"}, "state restriction"),
    _Case(" nontoken creature", True, {"identity"}, "identity restriction"),
    _Case(" legendary permanent", True, {"supertype"},
          "CR 205.4a supertype restriction"),
    _Case(" creature that was dealt damage this turn", True, {"state"},
          "past-event state (Ogre Siegebreaker) -- the census scored this "
          "unrestricted"),
    _Case(" Wall", True, {"type"},
          "CR 205.3g-q subtype: the axis is -creature and does not encode Wall"),
    _Case(" Equipment", True, {"type"},
          "same, via CR 205.3g -> artifact (Chaos Charm / Wear // Tear shape)"),
    _Case(" Island", True, {"type"},
          "Active Volcano's bounce mode -- the prior report reads this as "
          "restricted and this module's first draft did not"),
    _Case(" creature", True, {"identity"},
          "`another` sits in the lattice's _TARGET_HEAD, outside the tail",
          whole="destroy another target creature"),
    _Case(" creature", False, (),
          "and `up to one` is CARDINALITY, not eligibility -- it must NOT "
          "count, or the headline inflates by 7.8 points",
          whole="destroy up to one target creature"),
]


def selftest() -> int:
    """Every recorded historical failure, aimed at the code path that caused it.

    A guard that has never been shown to fail is not known to be a guard, and
    three of eight negative controls on 2026-08-09 were MIS-AIMED -- each first
    reading as "this gate is broken". So each control below states which
    rigging it applies and what must change.
    """
    fails = []

    def check(label, cond, detail=""):
        print(f"  [{'ok' if cond else 'FAIL'}] {label}" +
              (f"  -- {detail}" if detail and not cond else ""))
        if not cond:
            fails.append(label)

    print("FIXTURES -- the qualifier decision on known shapes")
    for c in _CASES:
        cls = ol.classify_clause(c.tail, ol.PERMANENT_TYPES)
        r = residual(c.tail, cls, c.whole)
        got_q = bool(r["tokens"])
        cats = set(categorize(r["tokens"]))
        ok = got_q == c.want and c.cats <= cats
        label = (c.whole or f"target{c.tail}").strip()
        check(f"{label:44s} qualified={got_q} cats={sorted(cats)}", ok, c.why)

    # GUARD D. The same fixture again through the probe library, because an
    # over-narrow filter under-reports and reads as a clean measurement -- and
    # the loop above is code I wrote, while this is the shared guard.
    try:
        p.must_capture(
            lambda pair: bool(residual(pair[0], ol.classify_clause(
                pair[0], ol.PERMANENT_TYPES), pair[1])["tokens"]),
            [((c.tail, c.whole), c.want) for c in _CASES],
            name="qualifier detector")
        check("probe guard D: detector matches its known-positive fixture", True)
    except SystemExit as e:
        check("probe guard D: detector matches its known-positive fixture",
              False, str(e))

    print("\nNC1 -- modal/preprocessing duplicate counting")
    keys = counting_keys()
    check("raw all-variant yields exceed canonical occurrences",
          keys["raw_yields_all_variants"] > keys["occurrences_canonical_text"],
          f"{keys}")
    check("no classified clause is reachable ONLY via an expansion",
          not gate_expansion_adds_no_clause())

    print("\nNC2 -- base-class-as-qualifier double counting")
    cls = ol.classify_clause(" nonland permanent", ol.PERMANENT_TYPES)
    span, _ = eligibility_span(" nonland permanent")
    unstripped = [t for t in re.findall(r"[a-z][a-z'\-]*", span.lower())
                  if t not in _SCAFFOLDING]
    check("WITHOUT the base-class strip the clause reads as qualified",
          bool(unstripped), f"rigged residual={unstripped}")
    check("WITH the strip it reads as unqualified",
          not residual(" nonland permanent", cls)["tokens"])

    print("\nNC3 -- overlapping numeric/relative matching")
    # THIS CONTROL WAS MIS-AIMED ON ITS FIRST WRITING, and the rigging run is
    # what showed it. It asked whether `categorize()` returns two categories
    # for one token -- which it CANNOT, because `categorize` is an if/elif
    # chain that returns at most one. Putting `flying` into two membership sets
    # left it green. A guard that cannot fail is decorative, so it is re-aimed
    # at the real risk: when two MEMBERSHIP SETS share a word, the if/elif
    # ORDER silently decides the category and the overlap is invisible.
    sets = {
        "keyword": KEYWORDS, "color": COLORS, "supertype": SUPERTYPES,
        "type": {s.lower() for s in ol.SUBTYPE_TO_TYPE} | set(ol.CARD_TYPES),
        "controller": _CONTROLLER, "numeric": _NUMERIC, "state": _STATE,
        "identity": _IDENTITY, "condition": _CONDITION,
    }
    samples = sorted(set().union(*sets.values()) |
                     {t for r in _CASES
                      for t in residual(r.tail, ol.classify_clause(
                          r.tail, ol.PERMANENT_TYPES))["tokens"]})
    try:
        p.assert_disjoint(
            {name: (lambda s, w=words: s in w) for name, words in sets.items()},
            samples, name="qualifier category membership sets")
        check("probe guard C: category membership sets are disjoint", True)
    except SystemExit as e:
        check("probe guard C: category membership sets are disjoint",
              False, str(e))

    print("\nNC4 -- a missing category cannot lower the RATE (the structural one)")
    tail = " creature with flying"
    cls = ol.classify_clause(tail, ol.PERMANENT_TYPES)
    toks = residual(tail, cls)["tokens"]
    saved = set(KEYWORDS)
    try:
        KEYWORDS.clear()          # delete the category the census lacked
        blinded = categorize(toks)
        check("with the keyword category deleted the clause is STILL qualified",
              bool(toks))
        check("and the token moves to `uncategorized`, not out of the count",
              "flying" in blinded.get("uncategorized", []), f"{blinded}")
    finally:
        KEYWORDS.update(saved)
    check("restoring the category re-classifies it as a keyword",
          "keyword" in categorize(toks))

    print("\nNC5 -- a clause with no genuine additional qualifier")
    check("`destroy target creature` yields zero residual tokens",
          not residual(" creature", ol.classify_clause(
              " creature", ol.PERMANENT_TYPES))["tokens"])

    print("\nNC6 -- non-eligibility residue is separated, not counted")
    tail = " creature an opponent controls until this creature leaves the battlefield"
    cls = ol.classify_clause(tail, ol.PERMANENT_TYPES)
    r = residual(tail, cls)
    check("the duration span is removed and recorded",
          "duration" in r["non_eligibility"], f"{r}")
    check("only the controller restriction survives as eligibility",
          set(r["tokens"]) == {"opponent", "controls"}, f"{r['tokens']}")

    print("\nDETERMINISM x2")
    a = json.dumps(census(), sort_keys=True)
    b = json.dumps(census(), sort_keys=True)
    check("two runs are byte-identical", a == b)

    print()
    if fails:
        print(f"SELFTEST FAILED -- {len(fails)} control(s): {fails}")
        return 1
    print("SELFTEST PASSED -- every control fired on the path it guards.")
    return 0


def gate() -> int:
    """Gate 2 row. STRUCTURAL AND NEGATIVE-CONTROL ONLY, ON PURPOSE.

    It does NOT pin 48%, 2,110 or ×9.2. Those are detector-sensitive: they move
    whenever the categories widen, and `docs/OBJECT-LATTICE-RESIDUAL-RULING`
    §8's own reasoning applies -- a measurement at probe time is not an
    equality invariant, and a tolerance band would be the tuning knob the
    engine rules forbid. What IS pinned is that the measurement stays
    REPRODUCIBLE: the CR vocabulary parses, the counting key's premise holds,
    the strip still prevents the double count, and a missing category still
    cannot move the rate.
    """
    print("=" * 78)
    print("QUALIFIER CENSUS — reproducibility gate")
    print("=" * 78)
    rc = selftest()
    print("=" * 78)
    print("GREEN — the census is re-derivable." if rc == 0
          else "RED — the census can no longer be re-derived as published.")
    return rc


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _report(c: dict, keys: dict) -> None:
    print("=" * 78)
    print("QUALIFIER CENSUS — object-lattice clauses, restriction beyond class")
    print("=" * 78)
    print("\nWHAT THIS CANNOT VERIFY: which clauses the lattice classifies.")
    print("There is no second implementation; `classify_clause` is consumed")
    print("directly, so a lattice recall defect is inherited here silently.\n")

    print("COUNTING KEYS — name the one you quote")
    print(f"  raw yields, all det_scan_texts variants   {keys['raw_yields_all_variants']:>7,}"
          "   <- the superseded census's denominator")
    print(f"  OCCURRENCES in the canonical text         {keys['occurrences_canonical_text']:>7,}"
          "   <- DEFAULT, one row per ability")
    print(f"  distinct clause strings                   {keys['distinct_strings']:>7,}")
    print(f"  distinct strings, case-folded             {keys['distinct_strings_case_folded']:>7,}"
          "   <- the prior verification's")

    print(f"\nQUALIFIER RATE  (key: {c['counting_key']})")
    print(f"  classified clause occurrences             {c['clause_occurrences']:>7,}")
    print(f"  carrying >=1 additional restriction       {c['qualified_clauses']:>7,}"
          f"   {c['qualifier_rate']}%")
    print(f"  excluding condition-only residue          "
          f"{c['qualified_excluding_condition_only']:>7,}"
          f"   {c['rate_excluding_condition_only']}%")
    print(f"  upper bound, ANY residue incl. duration   "
          f"{c['qualified_upper_bound_any_residue']:>7,}"
          f"   {c['rate_upper_bound_any_residue']}%")
    print(f"  clauses whose ONLY residue is ineligible  "
          f"{c['clauses_with_only_non_eligibility_residue']:>7,}")

    print("\nBY ACTION")
    for stem, d in c["per_stem"].items():
        print(f"  {stem:<34s} {d['qualified']:>5,} / {d['clauses']:>5,}"
              f"   {d['rate']:>5}%")

    print("\nBY BASE OBJECT AXIS  (the unit a compound qualifier would multiply)")
    for slug, d in sorted(c["per_axis"].items(),
                          key=lambda kv: -kv[1]["clauses"]):
        print(f"  {slug.replace('rule:', ''):<34s} {d['qualified']:>5,} /"
              f" {d['clauses']:>5,}   {d['rate']:>5}%")

    print("\nRESTRICTION CATEGORIES  (descriptive; they cannot move the rate)")
    for cat, n in sorted(c["categories_by_clause"].items(),
                         key=lambda kv: -kv[1]):
        mark = "  <- reported, never silently dropped" if cat == "uncategorized" else ""
        print(f"  {cat:<28s} {n:>5,} clauses{mark}")

    print(f"\nCR 702 KEYWORD RESTRICTIONS  (the category the census LACKED)")
    print(f"  clauses                                   {c['cr702_keyword_clauses']:>7,}")
    print(f"  distinct keywords: {', '.join(c['cr702_keywords_seen'])}")

    print("\nCOMBINATION PRESSURE")
    print(f"  base object axes                          {c['base_class_axes']:>7,}")
    print(f"  axis x qualifier-combination              "
          f"{c['class_x_qualifier_combinations']:>7,}")
    print(f"  expansion                                 "
          f"x{c['combination_expansion']}")

    print("\nNON-ELIGIBILITY RESIDUE  (separated, not counted as qualification)")
    for k, n in c["non_eligibility_spans"].items():
        print(f"  {k:<28s} {n:>5,} clauses")

    print(f"\nUNCATEGORIZED RESIDUAL  ({c['uncategorized_distinct']} distinct tokens)")
    for t, n in list(c["uncategorized_tokens"].items())[:14]:
        print(f"  {t:<28s} {n:>5,}")
    print()


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="machine-readable")
    ap.add_argument("--selftest", action="store_true",
                    help="negative controls")
    ap.add_argument("--gate", action="store_true", help="Gate 2 row")
    ap.add_argument("--sample", type=int, metavar="N",
                    help="N qualified clauses, fixed order, for hand audit")
    args = ap.parse_args()

    if args.gate:
        return gate()
    if args.selftest:
        return selftest()

    rows = population()
    c = census(rows)
    keys = counting_keys()

    if args.sample:
        out = [r for r in rows if r["tokens"]][:args.sample]
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0
    if args.json:
        print(json.dumps({"census": c, "counting_keys": keys},
                         indent=2, sort_keys=True))
        return 0
    _report(c, keys)
    return 0


if __name__ == "__main__":
    sys.exit(main())
