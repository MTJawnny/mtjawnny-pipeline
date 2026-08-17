#!/usr/bin/env python3
"""AQ4 PACKET 1 — THE FOUR §27 PRE-BENCHMARK READ-ONLY PROBES.

WHAT THIS IS, AND WHAT IT IS EMPHATICALLY NOT
---------------------------------------------
`docs/AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md` §27 names four
measurements that must exist BEFORE any candidate encoding. This module is
those four and nothing else:

    P1  residual / absence-proof feasibility      (§18's ABSENT-PROVEN, priced)
    P2  multi-effect-per-clause (MEC) pressure    (the RESERVED effect ordinal)
    P3  multi-participant (MPR) pressure          (RUNG-3's cohort, sized)
    P4  relation-kind diversity                   (RUNG-5's three kinds, tested)

**AQ4 production architecture is UNRATIFIED.** This module mints no
vocabulary, writes no codebook, adds no schema field, implements no
occurrence identity, no participant record, no relation edge and no
ABSENT-PROVEN. It is read-only over the corpus and it decides nothing. A
prevalence number here is NOT an architecture threshold — register #4
withdrew the one threshold that ever existed, and §26's adoption gate
replaced it with a qualitative question this module cannot answer.

    python3 experiments/foundry_aq4_probes.py --all        # all four, report
    python3 experiments/foundry_aq4_probes.py --all --json # machine-readable
    python3 experiments/foundry_aq4_probes.py --p1         # one probe
    python3 experiments/foundry_aq4_probes.py --selftest   # negative controls
    python3 experiments/foundry_aq4_probes.py --rig        # rigging transcript

THE POPULATION, STATED ONCE
---------------------------
P1/P2/P3 consume `foundry_qualifier_census.population()` — the committed
census population, one row per `(oracle_id, stem, occurrence index in
det_scan_texts[0])`. That key is the census's own, chosen there over three
rivals for reasons its docstring records; re-deriving it here would be the
re-implementation defect the probe library exists to prevent. P4's
population is different by construction (cards, not clauses) and says so.

`foundry_probe` is used for the guards that aim at defects this module can
actually have (D `must_capture` on every detector, C `assert_disjoint` on
every classification set, B `domain` on the census rows). `p.corpus()` is
deliberately NOT used to stand up the corpus: it builds the DELIVERY
classifier's order-dependent module state, which none of these probes
consume, and `fc.load_corpus_gated()` is the canonical entry point the
census and the lattice both already call. That is guard A honoured, not
skipped — the same call the census makes, made once.

THE ONE HAND-LIST, DECLARED
---------------------------
Every closed list here is PARSED at run time: CR 105.1 colours, CR 205.2a
card types, CR 205.3g–q subtypes, CR 205.4a supertypes, CR 110.4 permanent
types, CR 702 keyword names, CR 701 keyword actions, CR 607.2's referring
phrases. The exceptions are declared, sized and inventoried by
`--all --json`'s `h2_inventory`, under the CR 207.2d precedent (a list the
CR declines to enumerate is the one honest place a declared list may
stand):

  · English closed-class function words — REUSED from the census's own
    `_SCAFFOLDING` rather than retyped, so the two cannot drift apart.
  · `draw` as an effect head (CR 121.1 defines the action; CR 701 does not
    list it). Size 1. Required by §27's own mandated P2 positive control.
  · English demonstrative/pronoun back-reference markers for P4. The CR
    enumerates no such list; CR 607.1 defines the RELATION, not the words.

P1 reports its rate with and without the function-word tier, so the reader
can see exactly how much of the number rests on that one list.
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
import foundry_object_lattice as ol          # noqa: E402
import foundry_qualifier_census as fqc       # noqa: E402
import foundry_shape_extractor as fx         # noqa: E402
import foundry_probe as p                    # noqa: E402


# ==========================================================================
# SHARED — the claim vocabulary, every tier parsed or declared-and-verified
# ==========================================================================

def _plural_forms(term: str) -> set:
    """A closed-vocabulary term and its printed plurals. NOT a stemmer: the
    forms are generated from the term, so a term that never pluralizes simply
    contributes two dead alternatives rather than a wrong match."""
    return {term, term + "s", term + "es"}


def _verified_literals(source: str, literals: tuple, what: str) -> list:
    """A DECLARED literal list, verified against the source of truth it claims
    to come from.

    The recorded trap is that a hand-list is a defect with a delay. These
    literals are the lattice's own printed template — they exist in
    `ol._TARGET_HEAD` and `ol.ACTION_VERBS[...]['tail']` as regex source, and
    a regex is not a list. So they are declared HERE and asserted to occur in
    the pattern THERE: if the lattice re-words its template, this halts
    instead of quietly claiming text the matcher no longer prints.
    """
    missing = [t for t in literals if t not in source]
    if missing:
        fc.halt(f"{what}: declared template literal(s) {missing!r} no longer "
                f"occur in the pattern they were read from:\n  {source!r}\n"
                f"  A template literal that the matcher no longer prints would "
                f"claim text on the strength of a stale declaration.")
    return list(literals)


# --- tier 1: the lattice's own printed template (EXTRACT-3) ----------------

_HEAD_LITERALS = _verified_literals(
    ol._TARGET_HEAD, ("up to", "each", "all", "target"),
    "CR 601.2c target head")

# `another` SITS IN THE LATTICE'S TARGET HEAD AND IS NOT SCAFFOLDING.
# §13 names it outright — *"`another`(excludes self)"* — and the census's own
# `_HEAD_RESTRICTION` counts it as an identity restriction on 58 clauses.
# Claiming it as template would let `destroy another target creature` reach
# zero residue with its restriction filed as punctuation, which is §18.1's
# own warning ("an open capture can consume `target creature with flying` and
# emit only `creature`") wearing a literal instead of a wildcard. It is still
# CLAIMED — the restriction is deterministically named — but under a tier the
# report cannot mistake for scaffolding.
_RESTRICTION_ATOMS = _verified_literals(
    ol._TARGET_HEAD, ("another",), "CR 601.2c target head") + ["other"]


_NONCAP_GROUP = re.compile(r"\(\?:([^()|]+(?:\|[^()|]+)*)\)")


def _expand_bounded(pattern: str) -> set:
    """Expand a regex that uses ONLY top-level `|`, `(?:a|b)` groups and `x?`
    optional single characters into the finite set of strings it matches.

    This is deliberately a total function over a tiny grammar rather than a
    regex-to-string converter: anything outside that grammar HALTS. The
    recorded trap is that a hand-list is a defect with a delay, so the bounce
    destination is READ from the lattice rather than typed here — and a read
    that silently mis-expands would be worse than a hand-list, because it
    would look derived. The guard is what makes the derivation trustworthy.
    """
    forms = {pattern}
    while True:
        grown = set()
        for f in forms:
            m = _NONCAP_GROUP.search(f)
            if m:
                for alt in m.group(1).split("|"):
                    grown.add(f[:m.start()] + alt + f[m.end():])
            else:
                grown.add(f)
        if grown == forms:
            break
        forms = grown
    out = set()
    for f in forms:
        for alt in f.split("|"):
            variants = {alt}
            while True:
                nxt = set()
                for v in variants:
                    m = re.search(r"(.)\?", v)
                    if m:
                        nxt.add(v[:m.start()] + m.group(1) + v[m.end():])
                        nxt.add(v[:m.start()] + v[m.end():])
                    else:
                        nxt.add(v)
                if nxt == variants:
                    break
                variants = nxt
            out |= variants
    leftover = [f for f in out if re.search(r"[\\()\[\]{}*+.^$?|]", f)]
    if leftover:
        fc.halt("the bounce destination regex uses a construct outside the "
                "bounded grammar (`|`, `(?:a|b)`, `x?`); expanding it to "
                f"literals is no longer safe:\n  residue={leftover!r}")
    return {f.strip() for f in out if f.strip()}


def _bounce_destination_literals() -> list:
    """The bounce destination, expanded from the lattice's `tail` regex.

    `_clause_re` REQUIRES this phrase, so it is inside every bounce clause
    occurrence and is template, not content."""
    lits = _expand_bounded(ol.ACTION_VERBS["bounce"]["tail"])
    if not any(l.startswith("to ") and l.endswith("hand") for l in lits):
        fc.halt(f"the bounce destination expansion lost its printed form; "
                f"got {sorted(lits)}")
    return sorted(lits)


_TEMPLATE_TERMS = set(_HEAD_LITERALS) | set(_bounce_destination_literals())
for _spec in ol.ACTION_VERBS.values():
    _TEMPLATE_TERMS |= {_spec["word"], _spec["word"] + "s"}
# The destination phrases decompose into their own words when a clause prints
# a variant; each is still lattice template.
_TEMPLATE_TERMS |= {"to", "its", "their", "your", "owner", "owner's", "owners",
                    "hand", "hands"}


# --- tier 2: CR-closed vocabulary (EXTRACT-1) -----------------------------

_CR_CLOSED = {}
for _t in ol.CARD_TYPES:
    _CR_CLOSED.setdefault("cr205_2a_card_type", set()).update(_plural_forms(_t))
for _t in ol.PERMANENT_TYPES:
    _CR_CLOSED.setdefault("cr110_4_permanent_type", set()).update(_plural_forms(_t))
for _t in ol.SUBTYPE_TO_TYPE:
    _CR_CLOSED.setdefault("cr205_3_subtype", set()).update(_plural_forms(_t.lower()))
for _t in fqc.COLORS:
    _CR_CLOSED.setdefault("cr105_1_color", set()).update(_plural_forms(_t))
for _t in fqc.SUPERTYPES:
    _CR_CLOSED.setdefault("cr205_4a_supertype", set()).update(_plural_forms(_t))
for _t in fqc.KEYWORDS:
    _CR_CLOSED.setdefault("cr702_keyword", set()).update(_plural_forms(_t))
_CR_CLOSED["number_word"] = set(ol._NUMBER_WORDS) | {"one"}

# `permanent` is grammar §5 ratified OBJECT vocabulary and the lattice's own
# broad form; it is not a CR 205.2a card type.
_CR_CLOSED["cr110_4_permanent_type"].update(_plural_forms("permanent"))

_CR_CLOSED_ALL = set().union(*_CR_CLOSED.values())


# --- tier 3: the declared function-word scaffolding (H2, size stated) ------

_SCAFFOLD_TERMS = set(fqc._SCAFFOLDING)

H2_INVENTORY = {
    "english_function_words": {
        "size": len(_SCAFFOLD_TERMS),
        "source": "foundry_qualifier_census._SCAFFOLDING (reused, not retyped)",
        "cr_exemption": "CR 207.2d precedent — the CR enumerates no English "
                        "grammar; there is no rule to derive `the` from",
        "growth_exposure": "static — closed-class function words do not grow "
                           "with a set release",
        "used_by": ["P1 tier 3 (reported separately from the strict rate)"],
    },
    "draw_as_effect_head": {
        "size": 1,
        "source": "declared here; CR 121.1 defines drawing a card as an action",
        "cr_exemption": "CR 701 does not list `draw`; the action is defined at "
                        "CR 121.1 instead",
        "growth_exposure": "static",
        "used_by": ["P2 effect heads (required by §27's mandated control)"],
    },
    "pronoun_back_reference_markers": {
        "size": None,       # filled below, once the set is built
        "source": "declared here",
        "cr_exemption": "CR 607.1 defines the RELATION, never the English "
                        "words that realize it; CR 207.2d precedent",
        "growth_exposure": "static — closed-class English demonstratives",
        "used_by": ["P4 coreference candidates"],
    },
}


# ==========================================================================
# THE CLAIMER — residue-honest by construction (§18.1)
# ==========================================================================
#
# §18.1: *"only literal template tokens and closed-vocabulary matches may
# claim text; text matched by an open capture group is residue by
# definition."*
#
# THERE IS NO WILDCARD ANYWHERE IN THIS FUNCTION, AND THAT IS THE WHOLE
# POINT. Every claim is an exact membership test against a list that was
# parsed from the CR, expanded from the lattice's own printed template, or
# declared and inventoried above. `--rig` demonstrates what a catch-all
# would have manufactured, so the number this probe reports can be read
# against the number dishonesty would have produced.

_WORDISH = re.compile(r"[A-Za-z][A-Za-z'’]*(?:-[A-Za-z][A-Za-z'’]*)*|\d+")
_NEG_PREFIX = re.compile(r"^non-?", re.I)

# Longest-first so `first strike` cannot be shredded into two unknown tokens
# and `mana value` cannot be read as two unrelated ones.
def _term_matcher(terms: set) -> list:
    return sorted(terms, key=lambda t: (-len(t), t))


_TIERS = (
    ("template", _term_matcher(_TEMPLATE_TERMS)),
    ("restriction-atom", _term_matcher(set(_RESTRICTION_ATOMS))),
    ("cr-closed", _term_matcher(_CR_CLOSED_ALL)),
    ("scaffold", _term_matcher(_SCAFFOLD_TERMS)),
)
_TIER_INDEX = {name: i for i, (name, _) in enumerate(_TIERS)}


def _closed_kind(term: str) -> str:
    for kind, members in sorted(_CR_CLOSED.items()):
        if term in members:
            return kind
    return "cr-closed"


def claim(text: str,
          tiers=("template", "restriction-atom", "cr-closed", "scaffold"),
          catch_all: bool = False) -> dict:
    """Walk `text` left to right, claiming maximal literal spans.

    Returns {claims: [(span, tier, kind)], residue: [token], residue_spans}.
    `catch_all=True` is the RIGGING ONLY — it claims any leftover word and is
    what §18.1 forbids. It exists so the honest rate can be reported beside
    the manufactured one.
    """
    low = text.lower()
    active = [(n, ts) for n, ts in _TIERS if n in tiers]
    claims, residue = [], []
    i, n = 0, len(low)
    while i < n:
        ch = low[i]
        if not (ch.isalnum() or ch in "'’"):
            i += 1
            continue
        best = None
        for tier_name, terms in active:
            for term in terms:
                end = i + len(term)
                if low.startswith(term, i) and _boundary(low, i, end):
                    if best is None or end > best[0]:
                        best = (end, tier_name, term)
                    break          # terms are longest-first within a tier
        # A negated closed-vocabulary word (`nonland`, `non-Saga`) is the
        # printed FORBIDS atom of grammar §5's ratified OBJECT vocabulary; the
        # negation marker claims with the word it negates, never alone.
        if best is None:
            neg = _NEG_PREFIX.match(low[i:])
            if neg:
                j = i + neg.end()
                for term in _term_matcher(_CR_CLOSED_ALL):
                    end = j + len(term)
                    # THE BOUNDARY IS MEASURED FROM `i`, NOT FROM `j`. Checking
                    # it from `j` looks left at the `n` of `non` and refuses
                    # every negated word — `nonland`, the most common atom in
                    # this population, scored as residue and the P1 fixture
                    # caught it on the first run.
                    if low.startswith(term, j) and _boundary(low, i, end):
                        best = (end, "cr-closed", "non" + term)
                        break
        if best is not None:
            end, tier_name, term = best
            kind = _closed_kind(term.replace("non", "", 1)
                                if term.startswith("non") else term) \
                if tier_name == "cr-closed" else tier_name
            claims.append((text[i:end], tier_name, kind))
            i = end
            continue
        m = _WORDISH.match(low, i)
        if not m:
            i += 1
            continue
        tok = m.group(0)
        if catch_all:
            claims.append((tok, "CATCH-ALL", "open-capture"))
        else:
            residue.append(tok)
        i = m.end()
    return {"claims": claims, "residue": residue}


def _boundary(low: str, start: int, end: int) -> bool:
    """A term matches only on word boundaries, so `all` cannot claim the `all`
    inside `allied` and `art` cannot claim the head of `artifact`."""
    if start > 0 and (low[start - 1].isalnum() or low[start - 1] in "'’-"):
        return False
    if end < len(low) and (low[end].isalnum() or low[end] in "'’"):
        return False
    return True


# ==========================================================================
# P1 — RESIDUAL / ABSENCE-PROOF FEASIBILITY
# ==========================================================================

_REMINDER_PAREN = re.compile(r"\([^)]*\)")
# A clause tail is `[^.;]*`, and reminder text usually carries a period, so a
# WHOLE parenthetical rarely survives inside one occurrence. An UNCLOSED paren
# does, and counting only closed pairs would report zero reminder contact while
# half a reminder sat in the text. Both are counted.
_REMINDER_OPEN = re.compile(r"[()]")


def clause_tail(row: dict) -> str:
    """The census clause's TAIL — group(1) of the lattice's own clause regex.

    **THE CENSUS'S `eligibility_span` TAKES THE TAIL, NOT THE WHOLE CLAUSE**,
    and handing it the whole clause is silent: it cuts at the first printed
    `target`, which in `m.group(0)` is the clause's OWN target head, so the
    span collapses to `destroy ` and the measurement reads 99.6% zero residue.
    Found by reading the number, not by a failing test — a span of two words
    is trivially exhaustible and looks like a spectacular result.

    Re-matched with the lattice's own compiled pattern rather than sliced by
    hand, and halt-guarded, so a clause the pattern can no longer reproduce
    stops the run instead of yielding an empty tail.
    """
    m = ol._CLAUSE_RES[row["stem"]].match(row["clause"])
    if not m:
        fc.halt(f"the lattice clause pattern for {row['stem']!r} no longer "
                f"matches a clause it produced:\n  {row['clause']!r}")
    return m.group(1)


def p1(rows=None) -> dict:
    """Zero-residue rate under residue-honest claiming.

    POPULATION  object-lattice-classified clause occurrences (the census).
    UNIT        clause occurrence.
    DEDUPE      none beyond the census's own key — one row per occurrence.
    EXCLUSIONS  none. The FULL clause occurrence text is measured, not the
                census's narrower eligibility span: ABSENT-PROVEN is a claim
                about an occurrence, and text the census cuts (durations,
                `unless` clauses) is still text that could carry the
                dimension being claimed absent. The eligibility-span-only
                rate is reported beside it as a labeled sensitivity.
    DENOMINATOR every classified clause occurrence.
    """
    rows = rows if rows is not None else fqc.population()
    p.domain(rows, "stem", *sorted(ol.ACTION_VERBS))

    strict_zero = primary_zero = 0
    elig_zero = 0
    reminder_rows = 0
    reminder_free = reminder_free_zero = 0
    by_stem = defaultdict(lambda: [0, 0])
    by_axis = defaultdict(lambda: [0, 0])
    residue_tokens = Counter()
    residue_by_category = Counter()
    forms = Counter()
    unresolved = []

    for r in rows:
        text = r["clause"]
        prim = claim(text)
        strict = claim(text,
                       tiers=("template", "restriction-atom", "cr-closed"))

        has_reminder = bool(_REMINDER_PAREN.search(text)
                            or _REMINDER_OPEN.search(text))
        reminder_rows += 1 if has_reminder else 0

        zero = not prim["residue"]
        primary_zero += zero
        strict_zero += not strict["residue"]

        # The census's own eligibility span, for comparison only — fed the
        # TAIL, which is what it takes.
        span, _ = fqc.eligibility_span(clause_tail(r))
        elig_zero += not claim(span)["residue"]

        if not has_reminder:
            reminder_free += 1
            reminder_free_zero += zero

        by_stem[r["stem"]][0] += 1
        by_stem[r["stem"]][1] += zero
        for c in r["classes"]:
            slug = ol.slug_for(r["stem"], c)
            by_axis[slug][0] += 1
            by_axis[slug][1] += zero

        if not zero:
            residue_tokens.update(prim["residue"])
            for cat, toks in fqc.categorize(sorted(set(prim["residue"]))).items():
                residue_by_category[cat] += len(toks)
            forms[" ".join(sorted(set(prim["residue"])))] += 1
            if len(unresolved) < 40:
                unresolved.append({"name": r["name"], "stem": r["stem"],
                                   "clause": text[:110],
                                   "residue": sorted(set(prim["residue"]))})

    total = len(rows)
    pct = lambda n: round(100.0 * n / total, 1) if total else 0.0
    return {
        "population": "object-lattice-classified clause occurrences "
                      "(foundry_qualifier_census.population)",
        "unit": "clause occurrence",
        "counting_key": "(oracle_id, stem, occurrence index in det_scan_texts[0])",
        "dedupe": "none beyond the census key",
        "exclusions": "none — the full clause occurrence text is measured",
        "denominator": total,
        "eligible_clause_occurrences": total,
        "zero_residue_primary": primary_zero,
        "rate_zero_residue_primary": pct(primary_zero),
        "zero_residue_strict_no_function_words": strict_zero,
        "rate_zero_residue_strict": pct(strict_zero),
        "zero_residue_eligibility_span_only": elig_zero,
        "rate_zero_residue_eligibility_span_only": pct(elig_zero),
        "nonzero_residue": total - primary_zero,
        "rate_nonzero_residue": pct(total - primary_zero),
        "clauses_carrying_reminder_text": reminder_rows,
        "reminder_free_denominator": reminder_free,
        "reminder_free_zero_residue": reminder_free_zero,
        "rate_zero_residue_reminder_free":
            round(100.0 * reminder_free_zero / reminder_free, 1)
            if reminder_free else 0.0,
        "by_action_family": {
            s: {"clauses": n, "zero_residue": z,
                "rate": round(100.0 * z / n, 1) if n else 0.0}
            for s, (n, z) in sorted(by_stem.items())},
        "by_base_object_axis": {
            s: {"clauses": n, "zero_residue": z,
                "rate": round(100.0 * z / n, 1) if n else 0.0}
            for s, (n, z) in sorted(by_axis.items())},
        "residue_by_restriction_family": dict(sorted(residue_by_category.items())),
        "residue_tokens_top": dict(residue_tokens.most_common(30)),
        "residue_tokens_distinct": len(residue_tokens),
        "representative_structural_forms":
            [{"residue_signature": k, "clauses": v}
             for k, v in forms.most_common(15)],
        "unresolved_examples": unresolved,
    }


# ==========================================================================
# P2 — MULTI-EFFECT-PER-CLAUSE PRESSURE
# ==========================================================================

_CR701_HEADING = re.compile(r"^701\.(\d+)\.\s+(\w[\w '’-]*?)\s*$", re.M)


def cr701_keyword_actions() -> dict:
    """CR 701's keyword actions, parsed from the CR's own sub-rule headings.

    NOT `cr_action_terms()`: that reads `docs/cr-checks.json`, a GENERATED
    artifact, and the recorded trap is that a generated artifact is not the
    CR — it made a post-refresh routing diff read clean. Halt-guarded on
    CONTENT, because a count cannot see a substitution.
    """
    out = {}
    for num, name in _CR701_HEADING.findall(cr.text()):
        low = name.strip().lower()
        if low and low != "keyword actions":
            out[low] = f"701.{num}"
    if not {"destroy", "exile", "sacrifice", "discard", "counter", "create",
            "fight", "tap and untap"} <= set(out):
        fc.halt(f"CR 701 keyword-action parse lost a known action; got "
                f"{len(out)}: {sorted(out)[:20]}")
    return out


CR701_ACTIONS = cr701_keyword_actions()

# Effect heads: CR 701 keyword actions (EXTRACT-1) + the object lattice's own
# printed action words (EXTRACT-3 — `return` is a zone change the CR does not
# file as a keyword action, and omitting it would blind P2 to every bounce
# clause in its own population) + the single declared `draw` (H2, CR 121.1).
_EFFECT_HEADS = {}
for _a, _rule in CR701_ACTIONS.items():
    _EFFECT_HEADS[_a] = ("CR " + _rule, "EXTRACT-1")
for _spec in ol.ACTION_VERBS.values():
    _EFFECT_HEADS.setdefault(_spec["word"], ("object lattice", "EXTRACT-3"))
_EFFECT_HEADS.setdefault("draw", ("CR 121.1", "H2"))

# CR 608.2c — *"the spell or ability's controller follows the instructions in
# the ORDER WRITTEN"*. Oracle templating writes each instruction as its own
# imperative, so an effect head occupies a PREDICATE slot only at an
# instruction boundary. This is the whole guard: without it, `counter` in
# `destroy target creature with a +1/+1 counter on it` is an effect head,
# and the noun/verb confusion inflates MEC by counting object phrases.
_BOUNDARY_WORD = re.compile(
    r"(?:^|[,;:.]|\b(?:then|and/or|and|or|may|to)\b)\s*$", re.I)

_HEAD_RE = re.compile(
    r"\b(" + "|".join(re.escape(h) for h in
                      sorted(_EFFECT_HEADS, key=lambda t: (-len(t), t)))
    + r")(?:es|s|d|ed)?\b", re.I)


def effect_heads(clause: str, require_boundary: bool = True) -> list:
    """Every candidate effect head in predicate position, in printed order.

    ⛔ **FROZEN PACKET-2 BENCHMARK HISTORY — DO NOT "FIX" THIS FUNCTION.**

    Captain ruled `CORRECT_BEFORE_OPEN_KEY` on 2026-08-16 (AQ4 contract §27a,
    supersession register #23): the detector defect is corrected for
    ground-truth work while the Packet-2 population and pairing stay exactly
    as drawn. `aq4_population.action_family_of` is one of cohort 4's two
    stratum coordinates AND one of the S-tranche pairing coordinates, and it
    calls THIS function. Measured that day: re-running it with the corrected
    boundary rules moves the coordinate on **7 of the 272** published open
    exemplars, which would silently redraw the frozen 486-pair artifact.

    So this boundary rule is deliberately incomplete and its incompleteness
    is load-bearing. It reaches **307 of 782** open occurrences (39.3%), and
    that number is a committed benchmark fact, not a target to improve.

    **The corrected path is `semantic_action_heads` below.** New
    ground-truth, answer-key and projection work uses that one. Never route
    it back into Packet-2 regeneration, and never add a boolean mode to this
    function to reach it -- a flag reads identically at both call sites,
    which is exactly how a frozen artifact gets substituted by accident.
    """
    out = []
    for m in _HEAD_RE.finditer(clause):
        if require_boundary and not _BOUNDARY_WORD.search(clause[:m.start()]):
            continue
        out.append(m.group(1).lower())
    return out


# ==========================================================================
# CORRECTED SEMANTIC ACTION HEADS — AQ4 contract §27a, register #23
# ==========================================================================
# Two authorized structural classes, both CR-grounded, both independent of
# which text view the caller supplies (that is a packet-4 decision, §27a).
#
# P1 CR 700.2 -- *"two or more options in a BULLETED LIST preceded by
#    instructions for a player to choose a number of those options … each of
#    those options is a MODE"*. The bullet is LIST PUNCTUATION, so the mode's
#    instruction begins after it. It marks the OPTION, so only the bulleted
#    clause itself opens an instruction -- a follow-on sentence inside the
#    same mode is an ordinary sentence and is left to the boundary rule.
#: NOTE on anchoring: every prefix below is applied with `.match(clause, pos)`,
#: which already anchors the attempt at `pos`. A literal `^` must NOT appear in
#: them -- Python's `^` matches only the real start of the string even when a
#: pos is supplied, so an anchored pattern silently stops composing after the
#: first step. That is exactly how the CR 601.2b cost inside
#: `• <mode name> — {0} — Destroy …` was missed on the first draft.
_MODE_BULLET = re.compile(r"\s*•\s*")

# P2 -- a printed MARKER or COST precedes the instruction, which begins after
#    the em-dash. Each form cites the rule that puts it there; this is the
#    recorded "an em-dash prefix is one of six things and the CR decides
#    which" trap, so the forms are enumerated rather than pattern-guessed.
_P2_PREFIXES = (
    (re.compile(r"\s*(?:\{P\}\s*)+—\s*"),                     "CR 700.2i"),
    (re.compile(r"\s*[IVXL]+(?:\s*,\s*[IVXL]+)*\s*—\s*"),     "CR 714.2"),
    (re.compile(r"\s*[+\-−]?\s*(?:\{[^}]+\}\s*)+—\s*"),       "CR 606.2/700.2h"),
)
# CR 207.2d -- a flavor word may sit between the marker and the instruction
# ("I, II — Jecht Beam — …"). It carries no rules meaning, so it is stripped
# THROUGH, exactly as `foundry_shape_extractor.ability_word_prefix` rules.
_P2_FLAVOR = re.compile(r"\s*[\w'’\-.,!?& ]{3,40}?\s*—\s*")
# CR 702.Na -- a keyword prefix is REFUSED. CR 702.6b writes `Equip [cost]`,
# so the body after the dash is the keyword's own COST, not an effect:
# "Equip—Sacrifice a creature" must NOT promote `sacrifice` to an effect head.
_P2_KEYWORD = re.compile(r"\s*([A-Za-z][A-Za-z '’\-]*?)\s*—")


def _cr702_keyword_names() -> set:
    """CR 702 keyword names, parsed at run time and halt-guarded on CONTENT.

    NOT `foundry_shape_extractor.CR_KEYWORD_NAMES`: that global is populated
    lazily by `build_keyword_homes` and is None on a bare import, which would
    turn the CR 702.Na refusal off SILENTLY -- the recorded "a derived map is
    not the list it was derived from" trap, one door over. A count cannot see
    a substitution, so the guard asserts named members.
    """
    import foundry_cr702_classes as k7
    names = {kw["name"].lower() for num, kw in k7.load_702(k7.CR_PATH).items()
             if kw["name"] and num != k7.PREAMBLE_RULE}
    if not {"equip", "awaken", "ward"} <= names:
        fc.halt(f"CR 702 keyword-name parse lost a keyword that prints an "
                f"em-dash parameter; the CR 702.Na cost refusal would then "
                f"promote a cost body to an effect head. got {len(names)}.")
    return names


_CR702_KEYWORD_NAMES = _cr702_keyword_names()


def _instruction_offset(clause: str) -> int:
    """Offset at which the semantic instruction begins, else 0.

    The prefixes COMPOSE, and they have to: a printed mode line of the form
    `• <mode name> — {0} — Destroy target tapped creature.` carries a
    CR 700.2 bullet, then a CR 207.2d flavor word, then a CR 601.2b cost,
    before the instruction. So this advances a cursor while any recognized
    prefix still matches, rather than testing one form once.

    CLAUDE.md's ratified line is what licenses the flavor step through the
    bullet: *"The bullet is CR 700.2 list punctuation, so a mode name must be
    stripped through it"* -- and `foundry_shape_extractor._DASH_PREFIX`
    already encodes the same `(?:•\\s*)?` allowance.

    A CR 702.Na keyword prefix HALTS the cursor and is never consumed, at any
    depth: CR 702.6b writes `Equip [cost]`, so the body is the keyword's own
    cost and nothing in it is an effect head.
    """
    pos = 0
    m = _MODE_BULLET.match(clause)          # CR 700.2, at most once
    if m:
        pos = m.end()
    for _ in range(4):                      # bounded; deepest printed form is 3
        kw = _P2_KEYWORD.match(clause, pos)
        if kw and kw.group(1).strip().lower() in _CR702_KEYWORD_NAMES:
            break                           # CR 702.6b -- the body is a COST
        for rx, _rule in _P2_PREFIXES:
            m = rx.match(clause, pos)
            if m:
                pos = m.end()
                break
        else:
            fm = _P2_FLAVOR.match(clause, pos)   # CR 207.2d
            if not fm or re.search(r"[{}:•]", fm.group(0)):
                break
            pos = fm.end()
    return pos


def semantic_action_heads(clause: str) -> list:
    """Effect heads in predicate position, with the §27a corrections applied.

    The corrected counterpart of `effect_heads`. **Distinct public semantics,
    deliberately a separate function and not a mode of the frozen one.**

    Adds exactly two CR-grounded instruction boundaries to the legacy rule:

      P1  a CR 700.2 mode bullet opening the clause;
      P2  a CR 714.2 / 606.2 / 700.2h / 700.2i marker-or-cost prefix,
          with a CR 702.Na keyword prefix refused (CR 702.6b: cost, not effect).

    Everything the legacy rule already rejects stays rejected -- noun-position
    `counter` (CR 122.1 marker), the keyword-name fragment in `double strike`
    (CR 702.4), the zone noun in `from exile` (CR 400.1), participles such as
    "destroyed this way", and trigger-condition mentions (CR 113.3c) -- because
    this only ever ADDS boundary positions and never relaxes the boundary test.

    Finite-verb-with-printed-subject recovery is DEFERRED and is not here: it
    needs a subject-word list the CR does not enumerate, and a text-view ruling
    that belongs to packet 4. Returns heads in printed order, multi-head
    preserved, no card-specific branch anywhere.
    """
    out = []
    start = _instruction_offset(clause)
    for m in _HEAD_RE.finditer(clause):
        ok = bool(_BOUNDARY_WORD.search(clause[:m.start()]))
        if not ok and start and clause[start:m.start()].strip() == "":
            ok = True
        if ok:
            out.append(m.group(1).lower())
    return out


def p2(rows=None, require_boundary: bool = True) -> dict:
    """MEC pressure. POPULATION all classified clause occurrences. UNIT clause.

    This prices the RESERVED `effect` sub-clause ordinal (§11). It does NOT
    build a splitter and does NOT license one. **A candidate action verb is
    not a proven distinct semantic effect** — `destroy target creature, then
    exile it` is two heads and arguably one composite removal; the number is
    an upper bound on pressure, not a count of effects.
    """
    rows = rows if rows is not None else fqc.population()
    multi = 0
    by_stem = defaultdict(lambda: [0, 0])
    combos = Counter()
    forms = Counter()
    head_counts = Counter()
    examples = []
    for r in rows:
        heads = effect_heads(r["clause"], require_boundary)
        n = len(heads)
        head_counts[min(n, 5)] += 1
        by_stem[r["stem"]][0] += 1
        if n > 1:
            multi += 1
            by_stem[r["stem"]][1] += 1
            combos[tuple(heads[:4])] += 1
            forms[" + ".join(heads[:4])] += 1
            if len(examples) < 25:
                examples.append({"name": r["name"], "stem": r["stem"],
                                 "heads": heads, "clause": r["clause"][:110]})
    total = len(rows)
    return {
        "population": "all classified clause occurrences "
                      "(foundry_qualifier_census.population)",
        "unit": "clause",
        "dedupe": "none beyond the census key",
        "exclusions": "none",
        "denominator": total,
        "effect_head_source": {
            "cr701_keyword_actions": len(CR701_ACTIONS),
            "object_lattice_action_words": sorted(
                {s["word"] for s in ol.ACTION_VERBS.values()}),
            "declared": ["draw (CR 121.1)"],
            "total_heads": len(_EFFECT_HEADS),
        },
        "clauses_with_multiple_effect_heads": multi,
        "rate_multi_effect": round(100.0 * multi / total, 1) if total else 0.0,
        "head_count_distribution": {str(k): v
                                    for k, v in sorted(head_counts.items())},
        "by_action_family": {
            s: {"clauses": n, "multi_effect": m,
                "rate": round(100.0 * m / n, 1) if n else 0.0}
            for s, (n, m) in sorted(by_stem.items())},
        "top_structural_forms": [{"heads": k, "clauses": v}
                                 for k, v in forms.most_common(15)],
        "examples": examples,
        "limitation": "a candidate action verb does not prove a distinct "
                      "semantic effect; this is an upper bound on pressure",
    }


# ==========================================================================
# P3 — MULTI-PARTICIPANT PRESSURE
# ==========================================================================

_TARGET_TOKEN = re.compile(r"\btarget\b", re.I)


def participants(clause: str, count_possessives: bool = False) -> list:
    """Restricted-participant candidates in one clause.

    A participant candidate is an object the clause selects:

      · **each printed `target`** — CR 601.2c, *"the player announces their
        choice of an appropriate object or player for EACH TARGET the spell
        requires"*. Two printed targets are two participants;
      · **each `and <determiner>` conjunct** — the lattice's own
        `_SECOND_OBJECT`, CR 601.2c again: the single printed `target` does
        not reach an `and`-conjunct carrying its own determiner, so that
        conjunct is a second, untargeted object.

    **A POSSESSIVE IS NOT A PARTICIPANT.** `return it to ITS OWNER'S hand`
    names a relation on participant 0 (CR 108.3 ownership), not a second
    object the effect selects. `count_possessives=True` is the RIGGING for
    that control and must never be used for measurement.
    """
    # `whole` MATTERS, AND OMITTING IT LOSES A WHOLE RESTRICTION CLASS.
    # `foundry_qualifier_census.residual` takes (tail, cls, whole) because
    # `another target creature` puts its restriction in the lattice's
    # `_TARGET_HEAD`, BEFORE the tail. Passing the tail alone scored 20
    # census-qualified clauses as carrying zero restricted participants —
    # the census and this probe disagreeing about the same clause, which is
    # how it was found. Each participant is handed the slice running from
    # the previous head to its own successor, so its own `another` is inside
    # it and its neighbour's is not.
    spans = []
    marks = [m.start() for m in _TARGET_TOKEN.finditer(clause)]
    prev_end = 0
    for i, s in enumerate(marks):
        nxt = marks[i + 1] if i + 1 < len(marks) else len(clause)
        head_end = s + len("target")
        spans.append(("target", clause[head_end:nxt], clause[prev_end:nxt]))
        prev_end = head_end
    second = ol._SECOND_OBJECT.search(clause)
    if second:
        spans.append(("second-object", clause[second.end():],
                      clause[second.start():]))
    if count_possessives:
        for m in re.finditer(r"\b(?:owner'?s?|controller'?s?)\b", clause, re.I):
            spans.append(("possessive", clause[m.end():], clause[m.start():]))

    out = []
    for kind, tail, whole in spans:
        cls = ol.classify_clause(tail, ol.PERMANENT_TYPES)
        toks = fqc.residual(tail, cls, whole)["tokens"]
        out.append({"kind": kind, "restricted": bool(toks),
                    "restrictions": toks})
    return out


def _participants_no_head(clause: str) -> list:
    """RIGGING ONLY — `participants` with the `whole` argument dropped, i.e.
    the defective first writing. Never used for measurement; it exists so
    NC-P3c is shown capable of failing."""
    out = []
    marks = [m.start() for m in _TARGET_TOKEN.finditer(clause)]
    for i, s in enumerate(marks):
        nxt = marks[i + 1] if i + 1 < len(marks) else len(clause)
        tail = clause[s + len("target"):nxt]
        cls = ol.classify_clause(tail, ol.PERMANENT_TYPES)
        out.append({"restricted": bool(fqc.residual(tail, cls)["tokens"])})
    second = ol._SECOND_OBJECT.search(clause)
    if second:
        tail = clause[second.end():]
        cls = ol.classify_clause(tail, ol.PERMANENT_TYPES)
        out.append({"restricted": bool(fqc.residual(tail, cls)["tokens"])})
    return out


def p3(rows=None) -> dict:
    """MPR pressure.

    POPULATION  qualifier-bearing clauses — census rows carrying >=1 residual
                restriction token. That is the census's own definition of
                "qualifier-bearing" and is not re-derived here.
    UNIT        clause.

    **STATED LIMITATION, AND IT IS THE LOAD-BEARING ONE.** The object lattice
    covers exactly three actions (destroy / exile / bounce). `fight` is not
    among them, so the **Prey Upon class is structurally absent from this
    population** — its template is proven countable by the selftest fixture,
    not by a row here. A corpus-wide structural sizing of the two-target
    cohort is reported separately, and is labeled SECONDARY because it is not
    the contract's population.
    """
    rows = rows if rows is not None else fqc.population()
    qual = [r for r in rows if r["tokens"]]
    multi = 0
    forms = Counter()
    kinds = Counter()
    examples = []
    dist = Counter()
    for r in qual:
        parts = participants(r["clause"])
        restricted = [x for x in parts if x["restricted"]]
        dist[min(len(restricted), 4)] += 1
        if len(restricted) >= 2:
            multi += 1
            kinds[tuple(sorted(x["kind"] for x in restricted))] += 1
            forms[_structural_form(r["clause"])] += 1
            if len(examples) < 25:
                examples.append({"name": r["name"], "stem": r["stem"],
                                 "clause": r["clause"][:120],
                                 "participants": [x["kind"] for x in restricted],
                                 "restrictions": [x["restrictions"]
                                                  for x in restricted]})
    total = len(qual)
    return {
        "population": "qualifier-bearing clauses (census rows with >=1 "
                      "residual restriction token)",
        "unit": "clause",
        "dedupe": "none beyond the census key",
        "exclusions": "clauses carrying no restriction token",
        "denominator": total,
        "all_classified_clauses": len(rows),
        "qualifier_bearing_clauses": total,
        "clauses_with_2plus_restricted_participants": multi,
        "rate_multi_participant": round(100.0 * multi / total, 1) if total else 0.0,
        "restricted_participant_distribution": {str(k): v
                                                for k, v in sorted(dist.items())},
        # RECONCILIATION AGAINST THE CENSUS, REPORTED EVERY RUN. Every row
        # here is qualifier-bearing by the census's own verdict, so every row
        # must carry >=1 restricted participant. A non-zero number means this
        # probe and the census disagree about the same clause — which is
        # exactly how the dropped `another target` head restriction was found.
        "census_qualified_with_zero_restricted_participants": dist.get(0, 0),
        "participant_kind_combinations": {" + ".join(k): v
                                          for k, v in kinds.most_common()},
        "structural_forms": dict(forms.most_common(15)),
        "examples": examples,
        "structurally_absent_from_this_population": {
            "fight_templates": "CR 701.15 `fight` is not one of the object "
                               "lattice's three actions; the Prey Upon class "
                               "cannot appear here. Proven countable by the "
                               "selftest template fixture instead.",
            "attach": "CR 701.3 `attach` is likewise outside the lattice.",
        },
        "limitation": "no prevalence number here selects an architecture "
                      "(register #4); this sizes a cohort and nothing more",
    }


_FORM_TESTS = (
    ("exile-and-return", re.compile(r"\bexiles?\b.*\breturns?\b", re.I)),
    ("two-printed-targets", re.compile(r"\btarget\b.*\btarget\b", re.I)),
    ("second-object-conjunct", ol._SECOND_OBJECT),
    ("controller-relation", re.compile(r"\b(?:you|an opponent|its controller)\s+"
                                       r"(?:controls?|don't control)\b", re.I)),
)


def _structural_form(clause: str) -> str:
    hit = [n for n, rx in _FORM_TESTS if rx.search(clause)]
    return " | ".join(hit) if hit else "other"


def p3_secondary_corpus_wide(cards=None) -> dict:
    """SECONDARY, and labeled so it can never be quoted as P3's rate.

    P3's contract population is qualifier-bearing lattice clauses, which the
    lattice's three actions make structurally blind to fight/attach templates.
    This sizes the two-printed-target cohort across the whole gated corpus
    using the RATIFIED segmentation (`fx.ability_lines` + `fx.sentence_spans`),
    so the reader can see how much of the cohort P3's own denominator cannot
    reach. It is a structural count, not a participant analysis.
    """
    if cards is None:
        cards, _, _ = fc.load_corpus_gated()
    sentences = two_target = 0
    fight = Counter()
    for oid, card in sorted(cards.items()):
        for line in fx.ability_lines(card):
            for sent in fx.sentence_spans(line):
                sentences += 1
                if len(_TARGET_TOKEN.findall(sent)) >= 2:
                    two_target += 1
                    for a in sorted(CR701_ACTIONS):
                        if re.search(rf"\b{re.escape(a)}(?:es|s)?\b", sent, re.I):
                            fight[a] += 1
    return {
        "label": "SECONDARY — not P3's contract population",
        "unit": "sentence (fx.sentence_spans over fx.ability_lines)",
        "sentences": sentences,
        "sentences_with_2plus_printed_targets": two_target,
        "rate": round(100.0 * two_target / sentences, 2) if sentences else 0.0,
        "cr701_actions_present_in_those_sentences": dict(fight.most_common(15)),
    }


# ==========================================================================
# P4 — RELATION-KIND DIVERSITY
# ==========================================================================

_BRACKET = re.compile(r"\[[^\]]+\]")
# 607.2a-q publish the linkage kinds; **607.3 publishes the SINGULAR forms of
# the same vocabulary** (*"refers to a single object as 'the exiled card,'
# 'a card exiled with [this object],' or a similar phrase"*). Reading 607.2
# alone lost every singular referring phrase and filed 160 `the exiled ...`
# references as KIND-UNCLEAR — the recorded "look one rule up" trap, pointed
# one rule DOWN.
_CR607_RULE = re.compile(r"^607\.(?:2[a-z]|3)\.?\s.*$", re.M)
_CR607_QUOTED = re.compile(r"[“\"]([^”\"]+)[”\"]")
# *"See rule 614, 'Replacement Effects.'"* — a quoted RULE TITLE inside a
# cross-reference is not a referring phrase. Without this, CR 607.2b donated
# `replacement effects.` and CR 607.2k donated `champion.` to the relation
# vocabulary.
_SEE_RULE = re.compile(r"[Ss]ee rule\s+[\d.]+,?\s*$")


def cr607_referring_phrases() -> dict:
    """The phrases CR 607.2 / 607.3 themselves PRINT IN QUOTES as the
    REFERRING form of a linked ability.

    **THE RULE DISTINGUISHES THE TWO ABILITIES AND SO MUST THIS PARSE.**
    CR 607.2d reads *"...an ability printed on it that causes a player to
    'choose a [value]' and an ability printed on it that REFERS TO 'the
    chosen [value],' 'the last chosen [value],' or similar..."*. The first
    quoted phrase belongs to the SOURCE ability; only the ones after
    `refers` are references. Taking every quoted phrase scored `choose a
    color` as a relation candidate — a card that makes a choice, counted as
    a card that refers back to one.

    `[this object]` becomes the canonical self-reference token `~`, because
    `fc.canonicalize_self_reference` is what the corpus text is read through.
    Other bracketed placeholders become a BOUNDED one-or-two-word matcher —
    bounded, never an open capture. Trailing sentence punctuation is dropped:
    the CR prints the comma INSIDE the quote (American style), and requiring
    it made `exiled with ~` unmatchable on every card that ends the sentence
    there instead.
    """
    out = {}
    for rule_line in _CR607_RULE.findall(cr.text()):
        rule = rule_line.split()[0].rstrip(".")
        refers = rule_line.find("refers")
        if refers < 0:
            continue                      # no referring phrase in this rule
        for m in _CR607_QUOTED.finditer(rule_line):
            if m.start() < refers or _SEE_RULE.search(rule_line[:m.start()]):
                continue
            ph = m.group(1).strip().rstrip(",.;").lower()
            if len(ph) < 6 or "\n" in ph:
                continue
            parts = _BRACKET.split(ph)
            slots = _BRACKET.findall(ph)
            pat = re.escape(parts[0]).replace(r"\ ", r"\s+")
            for slot, nxt in zip(slots, parts[1:]):
                pat += (re.escape(fc.CARDNAME_TOKEN) if "this object" in slot
                        else r"[a-z]+(?:\s+[a-z]+)?")
                pat += re.escape(nxt).replace(r"\ ", r"\s+")
            out.setdefault(ph, {"rule": rule, "pattern": pat})
    for want in ("exiled with", "the exiled card", "the chosen"):
        if not any(want in k for k in out):
            fc.halt(f"CR 607 referring-phrase parse lost {want!r}; got "
                    f"{sorted(out)}")
    if any(k in ("champion", "replacement effects") for k in out):
        fc.halt(f"a quoted RULE TITLE entered the referring-phrase "
                f"vocabulary: {sorted(out)}")
    return out


CR607_PHRASES = cr607_referring_phrases()
_CR607_RES = {ph: re.compile(d["pattern"], re.I)
              for ph, d in CR607_PHRASES.items()}

# DECLARED (H2). CR 607.1 defines the RELATION — *"the other one directly
# refers to those actions, objects, or players"* — and never enumerates the
# English words that realize it. CR 207.2d precedent; inventoried above.
_PRONOUN_MARKERS = {
    "that card", "that creature", "that permanent", "that player",
    "that spell", "that token", "that object", "that land", "that artifact",
    "that enchantment", "that planeswalker", "those cards", "those creatures",
    "those permanents", "those tokens", "it", "them", "they", "its", "their",
}
H2_INVENTORY["pronoun_back_reference_markers"]["size"] = len(_PRONOUN_MARKERS)

_PRONOUN_RE = re.compile(
    r"\b(" + "|".join(re.escape(m) for m in
                      sorted(_PRONOUN_MARKERS, key=lambda t: (-len(t), t)))
    + r")\b", re.I)

# BACK-REFERENCE STRUCTURES THAT ARE NOT PRONOUNS AND NOT CR 607.2 PHRASES.
#
# **THESE EXIST SO `KIND-UNCLEAR` CAN FIRE.** The first writing of this probe
# emitted a candidate only when a kind rule already matched, so KIND-UNCLEAR
# was structurally unreachable and reported 0.0% — the repository's recorded
# dead-arm defect (the locality backfill's `changed` check, which could not
# differ from a value that was never there) aimed at the one number §27 asks
# P4 to watch. A hypothesis cannot be tested by a detector that can only
# confirm it.
#
# Every marker here is a printed Oracle back-reference form. None is in
# CR 607.2's published phrase list and none is a pronoun, so each reaches the
# kind rules and is REPORTED as unclear rather than assigned.
_BACKREF_MARKERS = {
    "this way", "that way", "the same", "such a", "such an",
    "the exiled", "the returned", "the chosen", "the copy", "the last",
}
_BACKREF_RE = re.compile(
    r"\b(" + "|".join(re.escape(m) for m in
                      sorted(_BACKREF_MARKERS, key=lambda t: (-len(t), t)))
    + r")\b", re.I)
H2_INVENTORY["backref_structure_markers"] = {
    "size": len(_BACKREF_MARKERS),
    "source": "declared here",
    "cr_exemption": "CR 607.1 defines the relation, never its English "
                    "realizations; CR 207.2d precedent",
    "growth_exposure": "static — printed Oracle templating forms",
    "used_by": ["P4 reference structures that reach the kind rules and may "
                "land in KIND-UNCLEAR"],
}

# CONDITIONALITY, each arm carrying the CR rule that makes it one.
_CONDITION_MARKERS = (
    ("intervening-if", re.compile(r"\bif\b", re.I), "CR 603.4"),
    ("unless", re.compile(r"\bunless\b", re.I), "CR 601.2b"),
    ("as-long-as", re.compile(r"\b(?:for )?as long as\b", re.I), "CR 611.2"),
    ("otherwise", re.compile(r"\botherwise\b", re.I), "CR 608.2"),
)

# CR 603.7 delayed triggered abilities — a MARKER on a relation, not a fourth
# kind (§16 lists three kinds "+ delayed marker").
_DELAYED = re.compile(
    r"\b(?:at the beginning of the next|when .{0,40} next|"
    r"at the end of (?:this|the next) turn|this turn,|until end of turn)\b",
    re.I)


def _card_lines(card: dict) -> list:
    """Reminder-stripped (CR 207.2a, §6a), CARDNAME-canonicalized, all faces.

    The strip runs FIRST so a reminder parenthetical printing the card's own
    name cannot supply a self-reference the printed text does not claim — and
    so a `choose one` inside a Spree reminder cannot be read as card text,
    which is the recorded reminder-text inversion.
    """
    txt = fc.canonicalize_self_reference(
        fx.strip_reminder(fc.full_oracle_text(card)), card)
    return [l.strip() for l in txt.split("\n") if l.strip()]


def _assign_kind(phrase: str, cr607_rule: str, kind_rules=("cr607", "coref")):
    """The kind rules, separable so each can be REMOVED and shown to move the
    KIND-UNCLEAR count. `kind_rules` is the rigging handle and defaults to all
    of them."""
    if cr607_rule and "cr607" in kind_rules:
        return "cr607-linkage", f"CR {cr607_rule}"
    if "coref" in kind_rules and phrase in _PRONOUN_MARKERS:
        return "coreference", "CR 607.1"
    return "kind-unclear", None


def relation_candidates(card: dict, kind_rules=("cr607", "coref")) -> list:
    """Candidate cross-occurrence references on one card, kind-assigned.

    STRUCTURE FIRST, KIND SECOND — and the two steps are separate on purpose.
    Step 1 finds every printed reference structure (a CR 607.2 published
    phrase, a demonstrative/pronoun, or a non-pronoun back-reference form).
    Step 2 assigns a kind, and a structure that reaches no kind rule stays
    **KIND-UNCLEAR**. Conditionality is scanned separately because it is a
    relation between an effect and a condition, not a back-reference.

    Precedence inside step 2 is CR-first: a phrase CR 607.2 itself publishes
    is CR 607 linkage; otherwise a demonstrative is coreference. Nothing is
    forced into a bucket to preserve the three-kind hypothesis.
    """
    lines = _card_lines(card)
    out = []
    for li, line in enumerate(lines):
        low = line.lower()
        sentences = fx.sentence_spans(line)
        delayed = bool(_DELAYED.search(line))

        # A reference occurrence is (position, printed phrase, cr607 rule|None).
        found = []
        for ph, rx in sorted(_CR607_RES.items()):
            for m in rx.finditer(line):
                found.append((m.start(), m.group(0).strip().lower(),
                              CR607_PHRASES[ph]["rule"]))
        covered = [(s, s + len(t)) for s, t, _ in found]
        for rx in (_PRONOUN_RE, _BACKREF_RE):
            for m in rx.finditer(line):
                if any(a <= m.start() < b for a, b in covered):
                    continue
                # A back-reference needs an antecedent. A card whose very
                # first words are a pronoun is naming a subject, not
                # referring back to one.
                if li == 0 and m.start() == 0:
                    continue
                found.append((m.start(), m.group(1).lower(), None))

        for pos, phrase, rule in sorted(found):
            kind, anchor = _assign_kind(phrase, rule, kind_rules)
            si = _sentence_index(line, sentences, pos)
            out.append({"kind": kind, "line": li, "sentence": si,
                        "cr": anchor, "phrase": phrase,
                        "cross_line": li > 0,
                        "cross_unit": li > 0 or si > 0,
                        "created_ability": fx.in_created_ability(line, pos),
                        "delayed": delayed})

        for name, rx, anchor in _CONDITION_MARKERS:
            for m in rx.finditer(low):
                si = _sentence_index(line, sentences, m.start())
                out.append({"kind": "conditionality", "line": li,
                            "sentence": si, "cr": anchor, "phrase": name,
                            "cross_line": False,
                            "cross_unit": li > 0 or si > 0,
                            "created_ability": fx.in_created_ability(
                                line, m.start()),
                            "delayed": delayed})
    return out


def _sentence_index(line: str, sentences: list, pos: int) -> int:
    """Which `fx.sentence_spans` sentence a character position falls in.

    Sentences are reassembled by offset rather than searched by string, so a
    line printing the same sentence twice cannot report both occurrences as
    the first one."""
    off = 0
    for i, s in enumerate(sentences):
        nxt = line.find(s, off)
        if nxt < 0:
            return i
        if pos < nxt + len(s):
            return i
        off = nxt + len(s)
    return max(len(sentences) - 1, 0)


def p4(cards=None) -> dict:
    """Relation-kind diversity.

    POPULATION  gated corpus cards carrying >=1 candidate reference.
    UNIT        card, and candidate reference.

    It resolves NOTHING. A candidate is a printed structure that a relation
    edge would have to represent; whether it actually refers to what it looks
    like it refers to is out of scope and stays UNRESOLVED by construction.
    """
    if cards is None:
        cards, _, _ = fc.load_corpus_gated()
    by_kind = Counter()
    by_rule = Counter()
    by_marker = defaultdict(Counter)
    cards_with = 0
    delayed = 0
    cross_line = 0
    cross_unit = 0
    unclear_forms = Counter()
    unclear_cards = set()
    total_refs = 0
    per_card_kinds = Counter()
    created = 0
    for oid, card in sorted(cards.items(), key=lambda kv: kv[1]["name"]):
        all_refs = relation_candidates(card)
        # §2's CREATED-ABILITY RULE: *a card does not deliver an ability it
        # CREATES.* A pronoun inside a quoted granted ability belongs to that
        # ability, not to this card's relation structure. Measured 484 of
        # them; excluding is the repository's ratified boundary, and the
        # excluded count is reported rather than dropped.
        created += sum(1 for r in all_refs if r["created_ability"])
        refs = [r for r in all_refs if not r["created_ability"]]
        if not refs:
            continue
        cards_with += 1
        total_refs += len(refs)
        per_card_kinds[len({r["kind"] for r in refs})] += 1
        for r in refs:
            by_kind[r["kind"]] += 1
            by_rule[r["cr"] or "(none — kind unclear)"] += 1
            by_marker[r["kind"]][r["phrase"]] += 1
            delayed += bool(r["delayed"])
            cross_line += bool(r["cross_line"])
            cross_unit += bool(r["cross_unit"])
            if r["kind"] == "kind-unclear":
                unclear_forms[r["phrase"]] += 1
                unclear_cards.add(card["name"])
    unclear = by_kind.get("kind-unclear", 0)
    return {
        "population": "gated corpus cards carrying >=1 candidate "
                      "cross-occurrence reference",
        "unit": "card and candidate reference",
        "dedupe": "none — every printed occurrence is one candidate",
        "exclusions": "reminder text (CR 207.2a strip); references inside a "
                      "QUOTED granted ability (grammar §2 created-ability "
                      "rule), counted and reported below",
        "references_excluded_inside_created_abilities": created,
        "cards_in_corpus": len(cards),
        "cards_with_candidates": cards_with,
        "total_candidate_references": total_refs,
        "by_kind": dict(sorted(by_kind.items())),
        "by_cr_anchor": dict(by_rule.most_common()),
        "kind_unclear": unclear,
        "rate_kind_unclear": round(100.0 * unclear / total_refs, 2)
        if total_refs else 0.0,
        "top_unclear_forms": dict(unclear_forms.most_common(15)),
        "cards_with_unclear_references": len(unclear_cards),
        "top_markers_by_kind": {k: dict(v.most_common(10))
                                for k, v in sorted(by_marker.items())},
        "delayed_marked_references": delayed,
        "cross_line_references": cross_line,
        "cross_unit_references": cross_unit,
        "distinct_kinds_per_card": {str(k): v
                                    for k, v in sorted(per_card_kinds.items())},
        "cr607_referring_phrases_parsed": len(CR607_PHRASES),
        "cr607_phrase_rules": sorted({d["rule"]
                                      for d in CR607_PHRASES.values()}),
        "limitation": "counts structure only; establishes no referent and "
                      "ratifies no three-kind model",
    }


# ==========================================================================
# NEGATIVE CONTROLS — every one rigged red before it is believed
# ==========================================================================

_P1_ZERO_FIXTURE = "destroy target nonland permanent"
_P1_INJECT = "destroy target nonland qwzzlx permanent"

_P2_POSITIVE = "Draw a card, then discard a card."
_P2_NEGATIVE_COORD = "destroy target artifact or enchantment"
_P2_NEGATIVE_NOUN = "destroy target creature with a +1/+1 counter on it"

_P3_POSITIVE = ("Target creature you control fights target creature you "
                "don't control.")
_P3_NEGATIVE = "return target creature to its owner's hand"


def selftest() -> int:
    fails = []

    def check(label, cond, detail=""):
        print(f"  [{'ok' if cond else 'FAIL'}] {label}"
              + (f"\n         -> {detail}" if detail and not cond else ""))
        if not cond:
            fails.append(label)

    print("=" * 78)
    print("AQ4 PACKET 1 — NEGATIVE CONTROLS")
    print("=" * 78)

    # ---------------------------------------------------------------- P1
    print("\nP1 — residue-honest claiming")
    base = claim(_P1_ZERO_FIXTURE)
    check("a fully-templated clause reaches ZERO residue",
          not base["residue"], f"residue={base['residue']}")
    inj = claim(_P1_INJECT)
    check("NC-P1a injecting an unclaimable token flips it to NON-zero residue",
          inj["residue"] == ["qwzzlx"], f"residue={inj['residue']}")

    rigged = claim(_P1_INJECT, catch_all=True)
    check("NC-P1a-RIG with a catch-all claimer the SAME injection reads clean "
          "(the control is load-bearing)",
          not rigged["residue"], f"residue={rigged['residue']}")

    check("NC-P1b an open capture never claims: no wildcard in the tier terms",
          all(not re.search(r"[.*+?\\]", t)
              for _, terms in _TIERS for t in terms))
    check("NC-P1c a closed-vocabulary word claims only on a word boundary",
          claim("allied artifact")["residue"] == ["allied"],
          f"{claim('allied artifact')}")
    check("NC-P1d the negation marker claims WITH its word, never alone",
          not claim("nonland")["residue"] and claim("nonqwzzlx")["residue"])

    # GUARD D — the detector against its own known-positive fixture.
    try:
        p.must_capture(lambda t: bool(claim(t)["residue"]),
                       [(_P1_ZERO_FIXTURE, False), (_P1_INJECT, True),
                        ("exile target creature you control", True),
                        ("destroy target permanent", False)],
                       name="P1 residue detector")
        check("probe guard D: P1 detector matches its fixture", True)
    except SystemExit as e:
        check("probe guard D: P1 detector matches its fixture", False, str(e))

    # GUARD C — the claim tiers must not double-claim the same term.
    try:
        # ALL THREE PAIRWISE INTERSECTIONS, not two. The first writing tested
        # `template n cr-closed` and `scaffold n cr-closed` and forgot
        # `template n scaffold` — where `all`, `to`, `each` and `or` live,
        # because the lattice's target head IS made of function words. A
        # shared term is claimed identically by either tier, so the honest
        # form of this guard is "disjoint outside a REPORTED shared set",
        # never "disjoint".
        sets = {name: set(terms) for name, terms in _TIERS}
        overlap = set()
        names = sorted(sets)
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                overlap |= sets[a] & sets[b]
        p.assert_disjoint(
            {n: (lambda s, w=(v - overlap): s in w) for n, v in sets.items()},
            sorted(set().union(*sets.values())),
            name="P1 claim tiers (shared terms excluded and reported)")
        check(f"probe guard C: claim tiers disjoint outside "
              f"{len(overlap)} declared shared term(s)", True)
    except SystemExit as e:
        check("probe guard C: claim tiers disjoint", False, str(e))

    # ---------------------------------------------------------------- P2
    print("\nP2 — multi-effect-per-clause")
    pos = effect_heads(_P2_POSITIVE)
    check("NC-P2a `Draw a card, then discard a card.` counts as MULTI-effect",
          len(pos) >= 2, f"heads={pos}")
    negc = effect_heads(_P2_NEGATIVE_COORD)
    check("NC-P2b coordination INSIDE an object phrase is ONE effect",
          len(negc) == 1, f"heads={negc}")
    negn = effect_heads(_P2_NEGATIVE_NOUN)
    check("NC-P2c `counter` as a NOUN is not an effect head",
          len(negn) == 1, f"heads={negn}")
    rig_n = effect_heads(_P2_NEGATIVE_NOUN, require_boundary=False)
    check("NC-P2c-RIG removing the CR 608.2c boundary rule turns NC-P2c RED",
          len(rig_n) >= 2, f"heads={rig_n}")
    rig_c = effect_heads(_P2_NEGATIVE_COORD, require_boundary=False)
    check("NC-P2b-RIG and it is the same rule guarding NC-P2b",
          len(rig_c) >= 1, f"heads={rig_c}")

    try:
        p.must_capture(lambda t: len(effect_heads(t)) > 1,
                       [(_P2_POSITIVE, True), (_P2_NEGATIVE_COORD, False),
                        (_P2_NEGATIVE_NOUN, False),
                        ("exile target creature, then return it", True)],
                       name="P2 MEC detector")
        check("probe guard D: P2 detector matches its fixture", True)
    except SystemExit as e:
        check("probe guard D: P2 detector matches its fixture", False, str(e))

    # ---------------------------------------------------------------- P3
    print("\nP3 — multi-participant")
    pp = [x for x in participants(_P3_POSITIVE) if x["restricted"]]
    check("NC-P3a the Prey Upon template counts TWO restricted participants",
          len(pp) == 2, f"{participants(_P3_POSITIVE)}")
    np_ = participants(_P3_NEGATIVE)
    check("NC-P3b `its owner's hand` does NOT make the owner a participant",
          len(np_) == 1, f"{np_}")
    rig_p = participants(_P3_NEGATIVE, count_possessives=True)
    check("NC-P3b-RIG counting possessives as participants turns NC-P3b RED",
          len(rig_p) >= 2, f"{rig_p}")

    try:
        p.must_capture(
            lambda t: len([x for x in participants(t) if x["restricted"]]) >= 2,
            # MIS-AIMED ON ITS FIRST WRITING, corrected rather than hidden:
            # `destroy target creature and the top card of your library` has
            # TWO participants and only ONE that is RESTRICTED, so it is a
            # negative for this detector, not a positive. P3 counts restricted
            # participants — an unrestricted target does not raise MPR.
            [(_P3_POSITIVE, True), (_P3_NEGATIVE, False),
             ("destroy target creature and the top card of your library", False),
             ("destroy target creature you control and the top card of "
              "your library", True),
             ("destroy target creature", False)],
            name="P3 MPR detector")
        check("probe guard D: P3 detector matches its fixture", True)
    except SystemExit as e:
        check("probe guard D: P3 detector matches its fixture", False, str(e))

    # ---------------------------------------------------------------- P4
    print("\nP4 — relation kinds")
    cards, _, _ = fc.load_corpus_gated()
    by_name = {c["name"]: c for c in cards.values()}

    cloud = by_name.get("Cloudshift")
    if cloud is None:
        check("NC-P4a Cloudshift is present in the gated corpus", False,
              "fixture card absent")
    else:
        refs = relation_candidates(cloud)
        kinds = {r["kind"] for r in refs}
        check("NC-P4a Cloudshift yields a COREFERENCE candidate",
              "coreference" in kinds, f"{refs}")

    # A card with no reference structure MUST yield zero. Chosen from the
    # corpus by a structural test, not by name, so the control cannot be
    # satisfied by picking a convenient card.
    silent = None
    for oid, card in sorted(cards.items(), key=lambda kv: kv[1]["name"]):
        lines = _card_lines(card)
        if lines and not any(
                _PRONOUN_RE.search(l) or
                any(rx.search(l) for _, rx, _ in _CONDITION_MARKERS) or
                any(rx.search(l) for rx in _CR607_RES.values())
                for l in lines):
            silent = card
            break
    check("NC-P4b a corpus card with no reference structure yields ZERO "
          f"candidates ({silent['name'] if silent else 'none found'})",
          silent is not None and not relation_candidates(silent))

    # CR 607 linkage, from repository DATA: the first card by name whose text
    # matches a phrase CR 607.2 itself publishes. Never a hand-picked name.
    linked = None
    for oid, card in sorted(cards.items(), key=lambda kv: kv[1]["name"]):
        refs = relation_candidates(card)
        if any(r["kind"] == "cr607-linkage" for r in refs):
            linked = (card["name"], [r for r in refs
                                     if r["kind"] == "cr607-linkage"][:2])
            break
    check("NC-P4c a CR 607 linked-ability fixture exists in corpus data "
          f"({linked[0] if linked else 'NONE'})", linked is not None,
          "no corpus card matches any CR 607.2 published referring phrase")

    # NC-P4d — KIND-UNCLEAR MUST BE A LIVE BRANCH, NOT A DEAD ARM.
    # The first writing emitted a candidate only when a kind rule matched, so
    # this number could never leave 0 and would have been reported as
    # "the three kinds cover everything".
    unclear_fixture = "Exile target creature, then return the exiled cards " \
                      "and create a token copy of it this way."
    class _F(dict):
        pass
    fixture_card = {"name": "NC-P4d fixture", "oracle_text": unclear_fixture,
                    "type_line": "Instant", "layout": "normal"}
    fx_refs = relation_candidates(fixture_card)
    check("NC-P4d a non-pronoun, non-CR-607 back-reference reaches "
          "KIND-UNCLEAR (the branch is live)",
          any(r["kind"] == "kind-unclear" for r in fx_refs),
          f"{[(r['kind'], r['phrase']) for r in fx_refs]}")
    dropped = relation_candidates(fixture_card, kind_rules=("cr607",))
    base_unclear = sum(1 for r in fx_refs if r["kind"] == "kind-unclear")
    drop_unclear = sum(1 for r in dropped if r["kind"] == "kind-unclear")
    check("NC-P4d-RIG removing the coreference kind rule MOVES references "
          "into KIND-UNCLEAR (the assignment is what decides, not the scan)",
          drop_unclear > base_unclear,
          f"base={base_unclear} rigged={drop_unclear}")

    try:
        p.assert_disjoint(
            {"cr607-phrase": lambda s: any(rx.search(s)
                                           for rx in _CR607_RES.values()),
             "conditionality": lambda s: any(rx.search(s)
                                             for _, rx, _ in _CONDITION_MARKERS)},
            [_P2_POSITIVE, _P3_POSITIVE, "exiled with ~", "unless you pay {2}",
             "as long as you control a Forest"],
            name="P4 CR 607 vs conditionality markers")
        check("probe guard C: CR 607 phrases and condition markers disjoint",
              True)
    except SystemExit as e:
        check("probe guard C: CR 607 phrases and condition markers disjoint",
              False, str(e))

    # ---------------------------------------------- cross-probe agreement
    print("\nCROSS-PROBE RECONCILIATION")
    rows = fqc.population()
    p3r = p3(rows)
    check("NC-P3c every census-qualified clause carries >=1 restricted "
          "participant (this probe and the census agree per clause)",
          p3r["census_qualified_with_zero_restricted_participants"] == 0,
          f"{p3r['census_qualified_with_zero_restricted_participants']} rows "
          f"disagree")
    rig_zero = sum(
        1 for r in rows if r["tokens"] and not any(
            x["restricted"] for x in _participants_no_head(r["clause"])))
    check("NC-P3c-RIG dropping the head-restriction argument turns NC-P3c RED",
          rig_zero > 0, f"rigged disagreements={rig_zero}")

    # -------------------------------- §27a corrected semantic action heads
    # Every fixture below is a PRINTED FORM, never a card-specific branch:
    # the implementation never sees a name or an oracle_id. Active Volcano
    # appears only as a historical positive control and is written as its two
    # printed mode lines, which any modal card of that shape reproduces.
    print("\n§27a SEMANTIC ACTION HEADS (P1 mode bullet + P2 instruction prefix)")
    S = semantic_action_heads

    check("ACTION.MODE_BULLET_GENERIC a CR 700.2 bullet opens an instruction",
          S("• Destroy target artifact.") == ["destroy"], S("• Destroy target artifact."))
    check("ACTION.MODE_BULLET_GENERIC-RIG without the bullet rule it is unreachable",
          effect_heads("• Destroy target artifact.", True) == [])

    av = ["• Destroy target blue permanent.", "• Return target Island to its owner's hand."]
    check("ACTION.ACTIVE_VOLCANO_GENERIC both printed modes recover generically",
          [S(x) for x in av] == [["destroy"], ["return"]], [S(x) for x in av])
    check("ACTION.ACTIVE_VOLCANO_GENERIC-RIG legacy path reaches neither",
          all(effect_heads(x, True) == [] for x in av))

    # A follow-on sentence inside a mode is an ordinary sentence: the bullet
    # marks the OPTION, so only the bulleted clause opens an instruction, and
    # the head must be ADJACENT to the prefix rather than merely after it.
    follow = "It can't be regenerated."
    check("ACTION.MODE_FOLLOWON a follow-on sentence is not a new bullet boundary",
          S(follow) == [] and S("• " + follow) == [],
          f"{S(follow)} / {S('• ' + follow)}")

    def _rig_nonadjacent(clause):
        """The same rule with ADJACENCY dropped: any head after the prefix."""
        start = _instruction_offset(clause)
        return [m.group(1).lower() for m in _HEAD_RE.finditer(clause)
                if _BOUNDARY_WORD.search(clause[:m.start()])
                or (start and m.start() >= start)]
    check("ACTION.MODE_FOLLOWON-RIG dropping adjacency claims the follow-on head",
          _rig_nonadjacent("• " + follow) == ["regenerate"]
          and S("• " + follow) == [],
          _rig_nonadjacent("• " + follow))
    check("ACTION.MODE_FOLLOWON-RIG adjacency also protects a real bulleted mode",
          _rig_nonadjacent("• You draw three cards.") == ["draw"]
          and S("• You draw three cards.") == [])

    check("ACTION.SAGA_PREFIX CR 714.2 chapter bar exposes the instruction",
          S("III — Destroy all other permanents.") == ["destroy"])
    check("ACTION.SAGA_PREFIX-RIG legacy path cannot reach it",
          effect_heads("III — Destroy all other permanents.", True) == [])

    check("ACTION.LOYALTY_PREFIX CR 606.2 loyalty cost exposes the instruction",
          S("+ {1}{U} — Counter target spell.") == ["counter"])
    check("ACTION.LOYALTY_PREFIX-RIG legacy path cannot reach it",
          effect_heads("+ {1}{U} — Counter target spell.", True) == [])

    check("ACTION.ADDITIONAL_COST_PREFIX CR 700.2h marker exposes the instruction",
          S("+ {3}{W}{W} — Destroy all creatures.") == ["destroy"])
    check("ACTION.ADDITIONAL_COST_PREFIX-RIG legacy path cannot reach it",
          effect_heads("+ {3}{W}{W} — Destroy all creatures.", True) == [])

    check("ACTION.PAWPRINT_PREFIX CR 700.2i pawprint exposes the instruction",
          S("{P}{P} — Exile target nonland permanent.") == ["exile"])
    check("ACTION.PAWPRINT_PREFIX-RIG legacy path cannot reach it",
          effect_heads("{P}{P} — Exile target nonland permanent.", True) == [])

    # CR 702.6b writes `Equip [cost]`, so the body is the keyword's own cost.
    check("ACTION.KEYWORD_COST_REFUSED a CR 702.Na body is a cost, not an effect",
          S("Equip—Sacrifice a creature.") == [], S("Equip—Sacrifice a creature."))
    check("ACTION.KEYWORD_COST_REFUSED-RIG treating it as a flavor word promotes it",
          _P2_FLAVOR.match("Equip—Sacrifice a creature.") is not None)

    # CR 122.1 marker noun / CR 702.4 keyword fragment / CR 400.1 zone noun.
    for label, txt in (("noun counter", "• Put a +1/+1 counter on each creature you control."),
                       ("keyword fragment", "IV — Creatures you control gain double strike."),
                       ("zone noun", "III — Put two cards from exile into their owners' graveyards.")):
        check(f"ACTION.NOUN_COUNTER {label} stays rejected", S(txt) == [], f"{txt} -> {S(txt)}")
    check("ACTION.NOUN_COUNTER-RIG dropping the boundary test admits all three",
          effect_heads("• Put a +1/+1 counter on each creature you control.", False) != [])

    check("ACTION.PARTICIPLE a nonfinite participle stays rejected",
          S("• A creature destroyed this way can't be regenerated.") == [],
          S("• A creature destroyed this way can't be regenerated."))
    check("ACTION.PARTICIPLE-RIG guard-off would claim it",
          effect_heads("A creature destroyed this way can't be regenerated.", False) != [])

    mh = "• Destroy target creature, then create a Treasure token."
    check("ACTION.MULTI_HEAD multiple heads preserved in printed order",
          S(mh) == ["destroy", "create"], S(mh))
    check("ACTION.MULTI_HEAD determinism x2", S(mh) == S(mh))

    src = Path(__file__).read_text(encoding="utf-8")
    seg = src[src.index("# CORRECTED SEMANTIC ACTION HEADS"):
              src.index("def p3(")]
    check("ACTION.NO_CARD_EXCEPTION no oracle_id/name branch in the implementation",
          "oracle_id" not in seg and "Volcano" not in seg and "Cross-Slash" not in seg)

    # The frozen path must be untouched by everything above.
    frozen = [("destroy target nonland permanent", ["destroy"]),
              ("• Destroy target artifact.", []),
              ("III — Destroy all other permanents.", []),
              ("destroy target creature with a +1/+1 counter on it", ["destroy"])]
    check("ACTION.LEGACY_FROZEN effect_heads output unchanged by the correction",
          all(effect_heads(t, True) == e for t, e in frozen),
          [(t, effect_heads(t, True)) for t, e in frozen if effect_heads(t, True) != e])
    check("ACTION.LEGACY_FROZEN-RIG the two paths genuinely differ",
          any(effect_heads(t, True) != S(t) for t, _e in frozen))

    # ------------------------------------------------------- determinism
    print("\nDETERMINISM x2 (probe outputs, no timestamps)")
    for name, fn in (("P1", lambda: p1(rows)), ("P2", lambda: p2(rows)),
                     ("P3", lambda: p3(rows))):
        a = json.dumps(fn(), sort_keys=True)
        b = json.dumps(fn(), sort_keys=True)
        check(f"{name} two runs byte-identical", a == b)

    print()
    if fails:
        print(f"SELFTEST FAILED — {len(fails)} control(s): {fails}")
        return 1
    print("SELFTEST PASSED — every control fired on the path it guards, and "
          "every rigging turned its control red.")
    return 0


def rig_transcript() -> int:
    """The rigging results, printed as evidence rather than asserted in prose."""
    print("=" * 78)
    print("RIGGING TRANSCRIPT — what each guard looks like when removed")
    print("=" * 78)
    print(f"\nP1  guard: residue-honest claiming (no open capture)")
    print(f"    fixture           {_P1_INJECT!r}")
    print(f"    honest            residue={claim(_P1_INJECT)['residue']}")
    print(f"    RIGGED catch-all  residue="
          f"{claim(_P1_INJECT, catch_all=True)['residue']}   <- reads CLEAN")
    rows = fqc.population()
    honest = sum(1 for r in rows if not claim(r['clause'])['residue'])
    rigged = sum(1 for r in rows
                 if not claim(r['clause'], catch_all=True)['residue'])
    print(f"    corpus-wide       honest zero-residue {honest:,}/{len(rows):,}"
          f"  ({100.0*honest/len(rows):.1f}%)")
    print(f"                      RIGGED               {rigged:,}/{len(rows):,}"
          f"  ({100.0*rigged/len(rows):.1f}%)  <- manufactured")

    print(f"\nP2  guard: CR 608.2c instruction-boundary requirement")
    for fixture in (_P2_NEGATIVE_NOUN, _P2_NEGATIVE_COORD):
        print(f"    fixture           {fixture!r}")
        print(f"    honest            heads={effect_heads(fixture)}")
        print(f"    RIGGED no-boundary heads="
              f"{effect_heads(fixture, require_boundary=False)}")
    hn = sum(1 for r in rows if len(effect_heads(r["clause"])) > 1)
    hr = sum(1 for r in rows
             if len(effect_heads(r["clause"], require_boundary=False)) > 1)
    print(f"    corpus-wide       honest MEC {hn:,}/{len(rows):,} "
          f"({100.0*hn/len(rows):.1f}%) · RIGGED {hr:,} "
          f"({100.0*hr/len(rows):.1f}%)")

    print(f"\nP3  guard: a possessive is not a participant")
    print(f"    fixture           {_P3_NEGATIVE!r}")
    print(f"    honest            participants="
          f"{len(participants(_P3_NEGATIVE))}")
    print(f"    RIGGED possessive participants="
          f"{len(participants(_P3_NEGATIVE, count_possessives=True))}")
    print()
    return 0


# ==========================================================================
# report / CLI
# ==========================================================================

def _bar(label, n, d, width=34):
    pct = (100.0 * n / d) if d else 0.0
    return f"  {label:<{width}s} {n:>7,} / {d:>7,}   {pct:>5.1f}%"


def _report_p1(r):
    print("=" * 78)
    print("P1 — RESIDUAL / ABSENCE-PROOF FEASIBILITY")
    print("=" * 78)
    print(f"\nPOPULATION  {r['population']}")
    print(f"UNIT        {r['unit']}")
    print(f"KEY         {r['counting_key']}")
    print(f"EXCLUSIONS  {r['exclusions']}\n")
    print(_bar("zero residue (primary)", r["zero_residue_primary"],
               r["denominator"]))
    print(_bar("zero residue (strict, CR+template only)",
               r["zero_residue_strict_no_function_words"], r["denominator"]))
    print(_bar("zero residue (eligibility span only)",
               r["zero_residue_eligibility_span_only"], r["denominator"]))
    print(_bar("zero residue (reminder-free rows)",
               r["reminder_free_zero_residue"], r["reminder_free_denominator"]))
    print(f"\n  clauses carrying reminder text          "
          f"{r['clauses_carrying_reminder_text']:>7,}")
    print("\nBY ACTION FAMILY")
    for s, d in r["by_action_family"].items():
        print(_bar(s, d["zero_residue"], d["clauses"]))
    print("\nBY BASE OBJECT AXIS")
    for s, d in sorted(r["by_base_object_axis"].items(),
                       key=lambda kv: -kv[1]["clauses"]):
        print(_bar(s.replace("rule:", ""), d["zero_residue"], d["clauses"]))
    print("\nUNCLAIMED RESIDUE, BY RESTRICTION FAMILY (census categories)")
    for c, n in sorted(r["residue_by_restriction_family"].items(),
                       key=lambda kv: -kv[1]):
        print(f"  {c:<34s} {n:>7,} tokens")
    print(f"\nTOP RESIDUE TOKENS  ({r['residue_tokens_distinct']} distinct)")
    for t, n in list(r["residue_tokens_top"].items())[:16]:
        print(f"  {t:<34s} {n:>7,}")
    print("\nREPRESENTATIVE STRUCTURAL FORMS (residue signature)")
    for f in r["representative_structural_forms"][:10]:
        print(f"  {f['clauses']:>5,}  {f['residue_signature'][:64]}")
    print()


def _report_p2(r):
    print("=" * 78)
    print("P2 — MULTI-EFFECT-PER-CLAUSE PRESSURE")
    print("=" * 78)
    print(f"\nPOPULATION  {r['population']}")
    print(f"UNIT        {r['unit']}")
    src = r["effect_head_source"]
    print(f"HEADS       {src['total_heads']} "
          f"({src['cr701_keyword_actions']} CR 701 keyword actions + "
          f"{src['object_lattice_action_words']} lattice + "
          f"{src['declared']})\n")
    print(_bar(">1 candidate effect head", r["clauses_with_multiple_effect_heads"],
               r["denominator"]))
    print("\nHEAD-COUNT DISTRIBUTION")
    for k, v in r["head_count_distribution"].items():
        print(f"  {k} head(s){'+' if k == '5' else ' '}                      "
              f"        {v:>7,}")
    print("\nBY ACTION FAMILY")
    for s, d in r["by_action_family"].items():
        print(_bar(s, d["multi_effect"], d["clauses"]))
    print("\nTOP STRUCTURAL FORMS")
    for f in r["top_structural_forms"][:12]:
        print(f"  {f['clauses']:>5,}  {f['heads']}")
    print(f"\nLIMITATION  {r['limitation']}\n")


def _report_p3(r, sec):
    print("=" * 78)
    print("P3 — MULTI-PARTICIPANT PRESSURE")
    print("=" * 78)
    print(f"\nPOPULATION  {r['population']}")
    print(f"UNIT        {r['unit']}")
    print(f"  all classified clauses {r['all_classified_clauses']:,} -> "
          f"qualifier-bearing {r['qualifier_bearing_clauses']:,}\n")
    print(_bar(">=2 restricted participants",
               r["clauses_with_2plus_restricted_participants"],
               r["denominator"]))
    print("\nRESTRICTED-PARTICIPANT DISTRIBUTION")
    for k, v in r["restricted_participant_distribution"].items():
        print(f"  {k} restricted participant(s)              {v:>7,}")
    print("\nPARTICIPANT KIND COMBINATIONS")
    for k, v in r["participant_kind_combinations"].items():
        print(f"  {k:<34s} {v:>7,}")
    print("\nSTRUCTURAL FORMS")
    for k, v in r["structural_forms"].items():
        print(f"  {k:<52s} {v:>7,}")
    print("\nSTRUCTURALLY ABSENT FROM THIS POPULATION")
    for k, v in r["structurally_absent_from_this_population"].items():
        print(f"  {k}: {v}")
    print(f"\nSECONDARY ({sec['label']})")
    print(f"  sentences scanned                       {sec['sentences']:>7,}")
    print(f"  with >=2 printed `target`               "
          f"{sec['sentences_with_2plus_printed_targets']:>7,}   "
          f"{sec['rate']}%")
    print(f"  CR 701 actions present in those: "
          f"{', '.join(f'{k}={v}' for k, v in list(sec['cr701_actions_present_in_those_sentences'].items())[:8])}")
    print(f"\nLIMITATION  {r['limitation']}\n")


def _report_p4(r):
    print("=" * 78)
    print("P4 — RELATION-KIND DIVERSITY")
    print("=" * 78)
    print(f"\nPOPULATION  {r['population']}")
    print(f"UNIT        {r['unit']}\n")
    print(f"  cards in gated corpus                   {r['cards_in_corpus']:>7,}")
    print(f"  cards with >=1 candidate reference      "
          f"{r['cards_with_candidates']:>7,}")
    print(f"  total candidate references              "
          f"{r['total_candidate_references']:>7,}")
    print(f"  excluded, inside a granted ability      "
          f"{r['references_excluded_inside_created_abilities']:>7,}")
    print("\nBY HYPOTHESIZED KIND")
    for k, v in sorted(r["by_kind"].items(), key=lambda kv: -kv[1]):
        print(f"  {k:<34s} {v:>7,}")
    print(f"\n  KIND-UNCLEAR                            {r['kind_unclear']:>7,}"
          f"   {r['rate_kind_unclear']}%")
    if r["top_unclear_forms"]:
        for t, n in r["top_unclear_forms"].items():
            print(f"    {t:<32s} {n:>7,}")
    print("\nBY CR ANCHOR")
    for k, v in list(r["by_cr_anchor"].items())[:12]:
        print(f"  {k:<34s} {v:>7,}")
    print("\nTOP MARKER BY KIND")
    for k, d in r["top_markers_by_kind"].items():
        print(f"  {k}: " + ", ".join(f"{t}={n:,}" for t, n in
                                     list(d.items())[:6]))
    print(f"\n  delayed-marked references               "
          f"{r['delayed_marked_references']:>7,}")
    print(f"  cross-line references                   "
          f"{r['cross_line_references']:>7,}")
    print(f"  cross-unit references (line or sentence)"
          f"{r['cross_unit_references']:>8,}")
    print(f"  CR 607.2 referring phrases parsed       "
          f"{r['cr607_referring_phrases_parsed']:>7,}"
          f"   rules {', '.join(r['cr607_phrase_rules'])}")
    print(f"\nLIMITATION  {r['limitation']}\n")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--p1", action="store_true")
    ap.add_argument("--p2", action="store_true")
    ap.add_argument("--p3", action="store_true")
    ap.add_argument("--p4", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--rig", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if a.rig:
        return rig_transcript()

    want = {"p1": a.p1 or a.all, "p2": a.p2 or a.all,
            "p3": a.p3 or a.all, "p4": a.p4 or a.all}
    if not any(want.values()):
        ap.print_help()
        return 2

    out = {}
    rows = fqc.population() if (want["p1"] or want["p2"] or want["p3"]) else None
    if want["p1"]:
        out["p1"] = p1(rows)
    if want["p2"]:
        out["p2"] = p2(rows)
    if want["p3"]:
        out["p3"] = p3(rows)
        out["p3_secondary"] = p3_secondary_corpus_wide()
    if want["p4"]:
        out["p4"] = p4()
    out["h2_inventory"] = H2_INVENTORY

    if a.json:
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0
    if "p1" in out:
        _report_p1(out["p1"])
    if "p2" in out:
        _report_p2(out["p2"])
    if "p3" in out:
        _report_p3(out["p3"], out["p3_secondary"])
    if "p4" in out:
        _report_p4(out["p4"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
