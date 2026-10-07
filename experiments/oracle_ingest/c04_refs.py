#!/usr/bin/env python3
"""C04 -- reference resolution, a measurement (oracle-compiler-interface/5 §I5).

PINNED TO oracle-compiler-interface/5 (oracle_compiler/INTERFACES.md blob
282c295c03f2a4b43e723d01710baaf479aa716c, landing 0390385, record 6031691630;
ratified 6031676826 under standing approval 5918781674). §I5 is the ONLY
specification: every word, list and numeric window below is one §I5.3 prints
(ruling 9), and none is keyed to a card.

POPULATION (§I4, §I5.1). The frozen P4 extraction (`relation_candidates`, the
`p4` card order) is re-run over the gated corpus and every §I4 figure is
reconciled against the interface's literals and the accepted C02 P4 output
before any other work; a mismatch HALTS. The unit is a pressure-set candidate
(kind-unclear, cr607-linkage, or delay-marked), created-ability candidates
excluded.

ADDRESS (§I5.1). P4 line k is the k-th non-empty `foundry_locality.units`
paragraph; it must equal that paragraph's chain clauses joined by one space
(HALT otherwise). The P4 sentence index is the clause ordinal. The offset is
the n-th whole-word occurrence of the phrase in the clause, n the candidate's
rank among the P4 candidates with that phrase in that clause.

RULES (§I5.3). E1 event-this-way, E2 cr607-linked, E3 copy-product, E4
singular-back-reference, E5 comparison, E6 conditionality, residue and
overlap. Regions are the interface/3 H-REGION regions of the re-pinned
`h_region.py` (R2 and R4 applied); the R3 plural list is named with
`h_region_kill.py`'s R3 code. CR 400.7, 607.2a/b/d, 608.2c and 707.10 are read
at run time and the run STOPs unless each prints its operative phrase.

A MEASUREMENT ONLY. No row is claimed correct (that is M05's read). An
UNRESOLVED reference is valid output; a guessed one is not. The output is
ignored experimental output carrying card text for the M05 reader.

    python3 experiments/oracle_ingest/c04_refs.py                      # write
    python3 experiments/oracle_ingest/c04_refs.py --emit               # stdout only
    python3 experiments/oracle_ingest/c04_refs.py --check-determinism  # x2 + write
    python3 experiments/oracle_ingest/c04_refs.py --check-reach        # vs §I5.5/§I5.7
    python3 experiments/oracle_ingest/c04_refs.py --verify             # stale?
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))

import h_region as hr                        # noqa: E402  (sets sys.path)
import h_region_kill as hk                   # noqa: E402
import foundry_common as fc                  # noqa: E402
import foundry_cr as cr                      # noqa: E402

aq, fx, fl = hr.aq, hr.fx, hr.fl

SCRIPT = "experiments/oracle_ingest/c04_refs.py"
OUT_REL = "experiments/out/oracle_ingest/c04/refs.json"
OUT = ROOT / OUT_REL

# oracle-compiler-interface/5, by git blob id; must equal h_region.py's pin.
INTERFACE_VERSION = "oracle-compiler-interface/5"
INTERFACES_BLOB = "282c295c03f2a4b43e723d01710baaf479aa716c"
if (hr.INTERFACE_VERSION, hr.INTERFACES_BLOB) != (INTERFACE_VERSION, INTERFACES_BLOB):
    fc.halt(f"h_region.py is pinned to {hr.INTERFACE_VERSION} ({hr.INTERFACES_BLOB}), "
            f"not {INTERFACE_VERSION} ({INTERFACES_BLOB})")
if (hk.INTERFACE_VERSION, hk.INTERFACES_BLOB) != (INTERFACE_VERSION, INTERFACES_BLOB):
    fc.halt(f"h_region_kill.py is pinned to {hk.INTERFACE_VERSION}, not {INTERFACE_VERSION}")

# §I5.8 ruling 6: A01 R2-A has reported; its verdict is cited, never re-derived.
A01_REL = "oracle_compiler/analysis/A01-R2A-REPLACEMENT-LINEAGE.md"
A01_VERDICT = {"A1": "GENUINELY_MISSING", "A3": "GENUINELY_MISSING",
               "A4": "GENUINELY_MISSING"}

def a01_verdict() -> dict:
    """§I5.8 ruling 6: A01 R2-A's verdict, read from its document; anything
    but the cited verdict is a STOP (C04 would then owe a lineage rule)."""
    text = (ROOT / A01_REL).read_text(encoding="utf-8")
    sec = text[text.index("## Verdict"):] if "## Verdict" in text else ""
    for seam, verdict in A01_VERDICT.items():
        if not re.search(rf"^- {seam}: {verdict}\b", sec, re.M):
            fc.halt(f"{A01_REL} does not record {seam}: {verdict}: a STOP")
    return dict(A01_VERDICT)


INPUTS = sorted(set(hr.INPUTS) | {hr.SCRIPT, hk.SCRIPT, A01_REL,
                                   "experiments/foundry_cr.py",
                                   "experiments/foundry_locality.py",
                                   "experiments/foundry_shape_extractor.py",
                                   "experiments/foundry_common.py"})

# ------------------------------------------------------- §I4 (reconciled)

I4 = {"cards_in_corpus": 32557, "cards_with_candidates": 16245,
      "total_candidate_references": 32603,
      "by_kind": {"coreference": 21672, "conditionality": 8642,
                  "cr607-linkage": 741, "kind-unclear": 1548},
      "delayed_marked_references": 3774, "cross_line_references": 12400,
      "references_excluded_inside_created_abilities": 607}
I5_PARAGRAPHS = 61383                 # §I5.1: measured equal on every paragraph

# --------------------------------------------- §I5.3 lists, as printed

# IRREG: 19 irregular participles, with their frozen head or none.
IRREG = {"dealt": None, "put": None, "drawn": "draw", "chosen": None, "paid": None,
         "lost": None, "won": None, "made": None, "dug": None, "spent": None,
         "found": None, "kept": None, "left": None, "held": None, "sold": None,
         "taken": None, "given": None, "seen": None, "shown": None}
PREPS = ("into", "in", "from", "to", "of", "the", "a", "an", "with", "on", "onto", "by")
DETS = ("the", "a", "an", "each", "any", "those", "all", "other", "another", "this",
        "these")
COORD = ("or", "and")
# E2
E2_FORMS = ("exiled", "chosen")
E2_EXILE_HEAD = "exile"
E2_NEGATED = ("can't", "don't", "cannot")
E2_YOU = ("you", "you may", "then", "and")
E2_NP_WINDOW = 4                       # words between "choose" and the noun
E2_TRIGGER = ("When", "Whenever", "At")
E2_ADDITIONAL_COST = "As an additional cost to cast this spell,"
E2_SPELL_TYPES = ("Instant", "Sorcery")
# E3
E3_FOLLOW = ("it", "that", "this", "target", "the", "each", "those", "them", "a", "an")
E3_CONDITIONS = ("when", "whenever", "if", "as long as", "unless")
E3_AFTER = ("then", "you may")
# E4
SINGULAR = ("it", "that artifact", "that card", "that creature", "that enchantment",
            "that land", "that object", "that permanent", "that planeswalker",
            "that spell", "that token")
PLURAL = ("they", "them", "those cards", "those creatures", "those permanents",
          "those tokens")
POSSESSIVE = ("its", "their", "that player")       # and any marker + 's
EXPLETIVE_AFTER = ("night", "day", "your turn", "their turn", "an opponent's turn")
OBJ_NOUNS = ("creature", "card", "permanent", "spell", "token", "artifact",
             "enchantment", "land", "planeswalker", "object", "ability")
PLAYER_NOUNS = ("player", "opponent")
MARK_PREFIX = ("another", "each", "all")
MARK_PLURAL = ("two", "three", "four", "x")
NOUN_WINDOW = 3                        # words between the mark and its noun
NOUN_STOP = (".", ";", ":", "!", "?", '"', "(", ")", "—")
AGREE_ANY = ("permanent", "object")
ZONE = ("exile", "return", "destroy", "sacrifice", "discard", "mill", "counter",
        "shuffle", "cast")
CREATE = ("create", "populate", "amass", "incubate", "manifest", "explore",
          "discover", "reveal", "search", "draw", "investigate")
CONT_WINDOW = 80
COMPETE_WINDOW = 60
COMPETE_WORDS = ("copy", "token", "create")
MASS = ("mana", "damage", "life", "energy", "loyalty", "poison")
INDEFINITE = ("a", "an", "another", "each", "any")
INDEFINITE_WINDOW = 2
CARD_NP_WINDOW = 3
CARD_ZONES = ("graveyard", "graveyards", "library", "libraries", "hand", "hands",
              "exile")
CARD_ZONE_WINDOW = 2
DELAYED_SUBSET = "at the beginning of the next"
# Residue
RESIDUE = ("the last", "the exiled", "the returned")
RESIDUE_ZERO = ("that way", "such a", "such an")
# §I5.7 discovery forms (28).
DISCOVERY = ("the rest", "that much", "the other", "the sacrificed", "the discarded",
             "the revealed", "the milled", "the destroyed", "the returned",
             "the countered", "the targeted", "the enchanted", "the blocking",
             "the attacking", "the card", "the cards", "the token", "the tokens",
             "the spell", "the creature", "the creatures", "the permanent",
             "the permanents", "he", "him", "his", "she", "her")

if len(IRREG) != 19 or len(DISCOVERY) != 28:
    fc.halt("a §I5.3/§I5.7 list lost a member")
if set(SINGULAR) | set(PLURAL) | set(POSSESSIVE) != set(aq._PRONOUN_MARKERS):
    fc.halt("the E4 marker lists do not partition the frozen P4 pronoun markers")
if set(PLURAL) != set(hr.R3_PLURAL_MARKERS):
    fc.halt("E4 PLURAL is not interface/2 R3's plural marker list")

OUTCOMES = ("RESOLVED", "UNRESOLVED", "NOT-COREFERENCE", "OUT-OF-SCOPE")
ENDPOINT_KINDS = ("EVENT", "LINKED", "COREFERENT", "PRODUCT", "OBJECT")
REASONS = ("no-candidate", "ambiguous", "detector-reach", "continuity",
           "competing-antecedent", "plural-r3", "overlap", "no-rule", "expletive",
           "other-chooser")
FIXTURE_ROLES = ("delayed-return-same-object", "prior-set-complement-reference",
                 "replacement-event-lineage", "ability-borrowing-inheritance-pressure",
                 "two-sequential-operations")

# --------------------------------------------- the CR reads (§I5.3)

CR_OPERATIVE = {
    "400.7": "becomes a new object with no memory of, or relation to, its previous "
             "existence",
    "607.2a": "instructs a player to exile one or more cards",
    "607.2b": "generates a replacement effect which causes one or more cards to be "
              "exiled",
    "607.2d": "causes a player to “choose a [value]”",
    "608.2c": "follows its instructions in the order written",
    "707.10": "means to put a copy of it onto the stack",
}


def cr_read(txt: str = None) -> dict:
    """Each rule §I5.3 names, read from the pinned CR; a rule missing, or not
    printing its operative phrase, is a STOP."""
    txt = cr.text() if txt is None else txt
    out = {}
    for rule, phrase in CR_OPERATIVE.items():
        m = re.search(rf"^(?:\*\*)?{re.escape(rule)}\.?(?:\*\*)?\s+(.*)$", txt, re.M)
        if not m or phrase not in m.group(1):
            fc.halt(f"CR {rule} does not print its operative phrase {phrase!r}: "
                    f"a STOP to the Captain")
        out[rule] = phrase
    return out


# --------------------------------------------- the rule table (§I5.3)
# Frozen sets are named by reference (several list words are card names).

RULES = (
    {"id": "event-this-way", "kind": "E1", "cr": "CR 608.2c",
     "pattern": "P4 kind-unclear phrase 'this way'; scan back in the clause for the "
                "governing verb: a participle of a single-word frozen head (IRREG) or "
                "a bare single-word frozen head not directly after PREPS; DETS + "
                "participle is skipped; directly after COORD is ambiguous; any other "
                "participle or IRREG word stops (detector-reach); endpoint the unique "
                "region of that head in the earlier clauses of the paragraph or "
                "starting before the offset, the verb's own region and regions "
                "directly after PREPS excluded"},
    {"id": "cr607-linked", "kind": "E2", "cr": "CR 607.2a / 607.2b / 607.2d",
     "pattern": "P4 cr607-linkage phrase holding E2_FORMS; the exiled form: a clause "
                "with a region of the frozen head E2_EXILE_HEAD in the same ability earlier (or "
                "starting before the reference), or in another ability of the face "
                "that is activated, triggered or replacement; the chosen form: a "
                "clause printing choose + at most E2_NP_WINDOW words + the noun, "
                "chosen by you; another chooser is other-chooser; one candidate: "
                "COREFERENT in the same ability, LINKED in another"},
    {"id": "copy-product", "kind": "E3", "cr": "CR 707.10",
     "pattern": "P4 kind-unclear phrase 'the copy'; the unique printed copy "
                "instruction (copy + E3_FOLLOW) earlier in the paragraph, outside an "
                "unclosed E3_CONDITIONS condition; PRODUCT at clause level"},
    {"id": "singular-back-reference", "kind": "E4", "cr": "CR 608.2c / 400.7",
     "pattern": "P4 coreference carrying the _DELAYED flag: expletive, POSSESSIVE no-rule, "
                "PLURAL plural-r3; SINGULAR: one single-object mark (OBJ_NOUNS noun "
                "within NOUN_WINDOW words), agreement, continuity (ZONE, "
                "CONT_WINDOW), competing antecedent (CREATE, COMPETE_WORDS, "
                "COMPETE_WINDOW, MASS, INDEFINITE), else OBJECT"},
    {"id": "comparison", "kind": "E5", "cr": "CR 608.2c",
     "pattern": "P4 kind-unclear phrase 'the same' printed as 'the same ... as': "
                "NOT-COREFERENCE, no endpoint; otherwise no-rule"},
    {"id": "conditionality-flagged", "kind": "E6", "cr": "CR 603.4 / 601.2b / 611.2 / 608.2",
     "pattern": "P4 conditionality in the set only through its _DELAYED flag: "
                "OUT-OF-SCOPE"},
    {"id": "residue", "kind": "residue", "cr": "CR 608.2c",
     "pattern": "RESIDUE phrases no-rule; a candidate inside a longer candidate's "
                "span, or printed fewer times as a whole word than P4 counts, is "
                "overlap"},
)

# ------------------------------------------------------------ words

_WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")          # E1 / E4: letters, ' and -
_E2_WORD = re.compile(r"[A-Za-z'’~-]+")              # E2: ... or "~"
_CARD_NP_WORD = r"[A-Za-z0-9,'’-]+"                  # E4 card noun phrase
_SINGLE_HEADS = tuple(sorted(h for h in aq._EFFECT_HEADS if " " not in h))


def _low(s: str) -> str:
    return s.lower().replace("’", "'")


def _words(text: str, rx=_WORD) -> list:
    return [(m.start(), m.end(), _low(m.group(0))) for m in rx.finditer(text)]


def _ws(text: str, a: int, b: int) -> bool:
    """Only whitespace (at least one character) between a and b."""
    return b > a and not text[a:b].strip()


def _prev_word(text: str, pos: int, rx=_WORD):
    """The word directly before `pos`, separated only by whitespace, or None."""
    ws = [w for w in _words(text[:pos], rx)]
    if ws and _ws(text, ws[-1][1], pos):
        return ws[-1]
    return None


def _ww(phrase: str):
    return re.compile(r"(?<!\w)" + re.escape(phrase).replace(r"\ ", r"\s+")
                      + r"(?!\w)", re.I)


def participle_head(word: str):
    """(head, irregular): the single-word frozen head `word` is a participle of
    (never the bare word), or (None, irregular)."""
    w = _low(word)
    if w in IRREG:
        return IRREG[w], True
    for h in _SINGLE_HEADS:
        if (w == h + "ed" or (h.endswith("e") and w == h + "d")
                or (h.endswith("y") and w == h[:-1] + "ied")
                or w == h + h[-1] + "ed"):
            return h, False
    return None, False


def _after_preps(text: str, pos: int) -> bool:
    p = _prev_word(text, pos)
    return bool(p) and p[2] in PREPS


# ------------------------------------------------------------- E1

def e1(clauses: list, ci: int, offset: int, regions: list) -> dict:
    """§I5.3 E1 on one paragraph. `clauses` the paragraph's chain clauses,
    `regions[k]` clause k's regions ({head, head_span, span}, clause offsets)."""
    text = clauses[ci]
    words = _words(text[:offset])
    for i in range(len(words) - 1, -1, -1):
        a, b, w = words[i]
        prev = words[i - 1][2] if i and _ws(text, words[i - 1][1], a) else None
        head, irregular = participle_head(w)
        verb = None
        if head and not irregular and prev in DETS:
            continue                                    # adjective
        if head:
            verb = head
        elif irregular:
            return {"outcome": "UNRESOLVED", "reason": "detector-reach", "class": None,
                    "verb": [a, b, w]}
        elif w in _SINGLE_HEADS:
            if prev in PREPS:
                continue
            verb = w
        elif w.endswith("ed"):
            if prev in DETS:
                continue                                # adjective
            return {"outcome": "UNRESOLVED", "reason": "detector-reach", "class": None,
                    "verb": [a, b, w]}
        else:
            continue
        cls = f"E1:{verb}"
        if prev in COORD:
            return {"outcome": "UNRESOLVED", "reason": "ambiguous", "class": cls,
                    "verb": [a, b, w]}
        hits = []
        for k in range(ci + 1):
            for r in regions[k]:
                if r["head"] != verb:
                    continue
                if k == ci and not (r["span"][0] < offset
                                    and not r["span"][0] <= a < r["span"][1]):
                    continue
                if _after_preps(clauses[k], r["head_span"][0]):
                    continue
                hits.append((k, r))
        if len(hits) == 1:
            k, r = hits[0]
            return {"outcome": "RESOLVED", "reason": None, "class": cls,
                    "verb": [a, b, w], "endpoint": {"kind": "EVENT", "clause": k,
                                                    "region_span": list(r["span"])}}
        return {"outcome": "UNRESOLVED", "class": cls, "verb": [a, b, w],
                "reason": "ambiguous" if hits else "no-candidate"}
    return {"outcome": "UNRESOLVED", "reason": "no-candidate", "class": None,
            "verb": None}


# ------------------------------------------------------------- E2

def _opens(text: str, pos: int, label_scope) -> bool:
    """§I5.3 E2 'chosen by you': the verb at `pos` opens its sentence or a
    comma-separated part, or follows you / you may / then / and."""
    pre = text[:pos].rstrip()
    if not pre or pre == "•" or pre.endswith(":") or pre.endswith(","):
        return True
    if label_scope is not None and label_scope == pos:
        return True
    low = _low(pre)
    return any(re.search(rf"(?<![\w'])({re.escape(y)})$", low) for y in E2_YOU)


def _np_holds(text: str, end: int, noun: str) -> bool:
    """§I5.3 E2 noun phrase: after the verb ending at `end`, at most
    E2_NP_WINDOW words (and nothing else) stand before the noun, which may
    carry a plural 's'; words after the noun do not matter."""
    m = re.match(r"(?:\s+" + _E2_WORD.pattern + r"){0," + str(E2_NP_WINDOW) + r"}?\s+("
                 + re.escape(noun) + r"s?)(?![\w'’~-])", text[end:], re.I)
    return bool(m)


def choices(text: str, noun: str, label_scope=None) -> list:
    """Every choice of `noun` in a clause: [(pos, by_you)]. A non-negated
    'choose' is by you when it opens its sentence or part (`_opens`); every
    other 'choose', and every 'chooses' or 'chose' not after 'you', is a
    choice by someone other than you."""
    out = []
    for m in re.finditer(r"(?<![\w'’])(choose|chooses|chose)(?![\w'’])", text, re.I):
        if not _np_holds(text, m.end(), noun):
            continue
        p = _prev_word(text, m.start(), _E2_WORD)
        if m.group(1).lower() == "choose":
            if p and p[2] in E2_NEGATED:
                continue
            out.append((m.start(), _opens(text, m.start(), label_scope)))
        elif not (p and p[2] == "you"):
            out.append((m.start(), False))
    return out


def _chose(text: str) -> bool:
    return bool(re.search(r"(?<![\w'’])(?:chooses|chose)(?![\w'’])", text, re.I))


def paragraph_kind(paras: list) -> dict:
    """The E2 'activated / triggered / replacement' test on one ability (its
    paragraphs, the opening one first)."""
    first = paras[0]["clauses"][0] if paras[0]["clauses"] else ""
    loc = hr.r4_locate(paras[0]["text"], 0)
    head = paras[0]["text"][loc[2]:] if loc else paras[0]["text"]
    head = head.lstrip().lstrip("•").lstrip()
    joined = " ".join(p["text"] for p in paras)
    return {"activated": ":" in first,
            "triggered": bool(re.match(r"(?:" + "|".join(E2_TRIGGER) + r")\b", head)),
            "replacement": bool(re.search(r"(?<![\w'’])instead(?![\w'’])", joined, re.I)
                                or re.search(r"\bAs (?:~|this\b)[^.]*?\benters\b",
                                             joined))}


def abilities(face: dict) -> list:
    """§I5.3 E2 'one ability': a paragraph; '•' paragraphs join the paragraph
    that opened them; on an instant or sorcery face the additional-cost
    paragraph joins the paragraph after it. Returns an ability id per paragraph."""
    spell = any(t in (face["type_line"] or "") for t in E2_SPELL_TYPES)
    ids, cur, pending = [], -1, False
    for p in face["paragraphs"]:
        if (p["text"].lstrip().startswith("•") and cur >= 0) or pending:
            pending = False
        else:
            cur += 1
        ids.append(cur)
        if spell and p["text"].startswith(E2_ADDITIONAL_COST):
            pending = True
    return ids


def e2(phrase: str, face: dict, pi: int, ci: int, offset: int) -> dict:
    """§I5.3 E2 on one face. `face` = {type_line, paragraphs: [{text, clauses,
    regions}]}; the reference is paragraph `pi` (index into the face's
    paragraphs), clause `ci`, at `offset`."""
    low = _low(phrase)
    if "chosen" in low.split():
        form = "chosen"
    elif "exiled" in low.split():
        form = "exiled"
    else:
        return {"outcome": "UNRESOLVED", "reason": "no-rule", "class": None}
    cls = f"E2:{form}"
    paras = face["paragraphs"]
    ids = abilities(face)
    own = ids[pi]
    by_ability = {}
    for k, a in enumerate(ids):
        by_ability.setdefault(a, []).append(paras[k])
    kinds = {a: paragraph_kind(ps) for a, ps in by_ability.items()}
    same, other = [], []
    if form == "exiled":
        for k, p in enumerate(paras):
            for j, regs in enumerate(p["regions"]):
                ex = [r for r in regs if r["head"] == E2_EXILE_HEAD]
                if ids[k] == own:
                    if (k, j) < (pi, ci) and ex:
                        same.append((k, j))
                    elif (k, j) == (pi, ci) and any(r["span"][0] < offset for r in ex):
                        same.append((k, j))
                elif ex and any(kinds[ids[k]].values()):
                    other.append((k, j))
    else:
        ws = low.split()
        noun = ws[ws.index("chosen") + 1] if ws.index("chosen") + 1 < len(ws) else None
        if noun is None:
            return {"outcome": "UNRESOLVED", "reason": "no-candidate", "class": cls}
        another = False
        for k, p in enumerate(paras):
            loc = hr.r4_locate(p["text"], 0)
            for j, t in enumerate(p["clauses"]):
                for pos, by_you in choices(t, noun, loc[2] if (loc and j == 0) else None):
                    if not by_you:
                        another = True
                    elif ids[k] == own and ((k, j) < (pi, ci)
                                            or ((k, j) == (pi, ci) and pos < offset)):
                        same.append((k, j))
                    elif ids[k] != own:
                        other.append((k, j))
                if ids[k] == own and (k, j) < (pi, ci) and _chose(t):
                    another = True
                if (k, j) == (pi, ci) and _chose(t[:offset]):
                    another = True
        if another:
            return {"outcome": "UNRESOLVED", "reason": "other-chooser", "class": cls}
    same, other = sorted(set(same)), sorted(set(other))
    if len(same) + len(other) == 1:
        k, j = (same or other)[0]
        return {"outcome": "RESOLVED", "reason": None, "class": cls,
                "endpoint": {"kind": "COREFERENT" if same else "LINKED",
                             "paragraph": k, "clause": j}}
    return {"outcome": "UNRESOLVED", "class": cls,
            "reason": "ambiguous" if same or other else "no-candidate"}


# ------------------------------------------------------------- E3

_COPY = re.compile(r"(?<![\w'’])copy\s+(?:" + "|".join(E3_FOLLOW) + r")(?![\w'’])", re.I)
_COND = re.compile(r"(?<![\w'’])(?:" + "|".join(re.escape(c) for c in E3_CONDITIONS)
                   + r")(?![\w'’])", re.I)


def copy_instruction_ok(text: str, pos: int) -> bool:
    """A copy at `pos` sits outside every When/Whenever/If/As long as/Unless
    condition, or after one that closed with a comma, directly or after
    'then' / 'you may'."""
    pre = text[:pos]
    conds = list(_COND.finditer(pre))
    if not conds:
        return True
    rest = pre[conds[-1].end():]
    if "," not in rest:
        return False
    tail = _low(rest[rest.rindex(",") + 1:]).strip()
    return tail == "" or tail in E3_AFTER


def e3(clauses: list, ci: int, offset: int) -> dict:
    hits = []
    for k in range(ci + 1):
        for m in _COPY.finditer(clauses[k]):
            if k == ci and m.start() >= offset:
                continue
            if copy_instruction_ok(clauses[k], m.start()):
                hits.append(k)
    if len(hits) == 1:
        return {"outcome": "RESOLVED", "reason": None, "class": "E3",
                "endpoint": {"kind": "PRODUCT", "clause": hits[0]}}
    return {"outcome": "UNRESOLVED", "class": "E3",
            "reason": "ambiguous" if hits else "no-candidate"}


# ------------------------------------------------------------- E4

_EXPLETIVE = re.compile(r"it(?:['’]s| is)(?: not)? (?:"
                        + "|".join(re.escape(x).replace("'", "['’]")
                                   for x in EXPLETIVE_AFTER)
                        + r"|the [A-Za-z'’-]+ turn)(?![\w'’])", re.I)
_TARGET_OF = re.compile(r"the target of(?![\w'’])", re.I)
_CONT_TEXT = (re.compile(r"(?<![\w'’])onto the battlefield(?![\w'’])", re.I),
              re.compile(r"(?<![\w'’])(?:cast|play)(?![\w'’]).*?(?<![\w'’])from(?![\w'’])",
                         re.I),
              re.compile(r"(?<![\w'’])put(?![\w'’]).*?(?<![\w'’])into(?![\w'’])", re.I))
_CARD_NP = re.compile(
    r"(?:\s+" + _CARD_NP_WORD + r"){0," + str(CARD_NP_WINDOW) + r"}?\s+cards?(?![\w'’])"
    r"[^.,;]*?(?<![\w'’])(?:in|from)\s+(?:[A-Za-z0-9'’-]+\s+){0,"
    + str(CARD_ZONE_WINDOW) + r"}(?:" + "|".join(CARD_ZONES) + r")(?![\w'’])", re.I)
_COMPETE = re.compile(r"(?<![\w'’])(?:" + "|".join(COMPETE_WORDS) + r")(?![\w'’])", re.I)
_MASS = re.compile(r"(?<![\w'’])(?:" + "|".join(MASS) + r")(?![\w'’])", re.I)
_SELF = re.compile(r"~(?!['’]s)|(?<![\w'’])this (?:" + "|".join(OBJ_NOUNS)
                   + r")(?![\w'’])(?!['’]s)", re.I)
_INDEF = re.compile(r"(?<![\w'’])(?:" + "|".join(INDEFINITE) + r")\s+(?:[A-Za-z][A-Za-z'’-]*\s+){0,"
                    + str(INDEFINITE_WINDOW) + r"}(?:" + "|".join(OBJ_NOUNS)
                    + r")(?![\w'’])", re.I)
_CHOOSE = re.compile(r"(?<![\w'’])(?:choose|chosen)(?![\w'’])", re.I)


def _noun_of(word: str):
    w = _low(word)
    if w.endswith("'s"):
        w = w[:-2]
    for n in OBJ_NOUNS + PLAYER_NOUNS:
        if w == n or w == n + "s":
            return n
    return None


def marks(line: str, end: int) -> list:
    """The P3 `target` marks in line[:end], 'the target of' excepted:
    [(target start, target end)]."""
    return [(m.start(), m.end()) for m in aq._TARGET_TOKEN.finditer(line[:end])
            if not (m.start() >= 4 and _TARGET_OF.match(line, m.start() - 4))]


def mark_np(line: str, t0: int, t1: int) -> dict:
    """§I5.3 E4 step 2 on the mark whose 'target' is line[t0:t1]."""
    start, plural = t0, False
    p = _prev_word(line, t0)
    if p and p[2] in MARK_PREFIX:
        start = p[0]
    elif p and p[2] in MARK_PLURAL:
        plural = True
    elif p:
        pp = _prev_word(line, p[0])
        ppp = _prev_word(line, pp[0]) if pp else None
        if pp and ppp and (ppp[2], pp[2]) == ("up", "to"):
            start, plural = ppp[0], p[2] != "one"
        elif pp and ppp and (ppp[2], pp[2], p[2]) == ("any", "number", "of"):
            plural = True
    noun = None
    pos = t1
    for i, (a, b, w) in enumerate(_words(line[t1:])):
        a, b = a + t1, b + t1
        if any(ch in line[pos:a] for ch in NOUN_STOP):
            break
        n = _noun_of(line[a:b])
        if n:
            noun = (a, b, n)
            break
        if i >= NOUN_WINDOW:
            break
        pos = b
    return {"start": start, "end": t1, "plural": plural, "noun": noun}


def e4(phrase: str, clauses: list, ci: int, offset: int, regions: list) -> dict:
    """§I5.3 E4 on one paragraph (clauses joined by one space)."""
    starts, at = [], 0
    for c in clauses:
        starts.append(at)
        at += len(c) + 1
    line = " ".join(clauses)
    ref = starts[ci] + offset
    cls = f"E4:{phrase}"
    after = line[ref + len(phrase):]
    if phrase == "it" and _EXPLETIVE.match(line, ref):
        return {"outcome": "UNRESOLVED", "reason": "expletive", "class": cls}
    # "that spell's" is possessive; "it's" is "it is", not a possessive.
    if phrase in POSSESSIVE or (phrase != "it" and re.match(r"['’]s(?![\w'’])", after)):
        return {"outcome": "UNRESOLVED", "reason": "no-rule", "class": cls}
    lregs = [dict(r, k=k, span=[starts[k] + r["span"][0], starts[k] + r["span"][1]],
                  head_span=[starts[k] + r["head_span"][0], starts[k] + r["head_span"][1]])
             for k in range(len(clauses)) for r in regions[k]]
    if phrase in PLURAL:
        return {"outcome": "UNRESOLVED", "reason": "plural-r3", "class": cls}
    if phrase not in SINGULAR:
        return {"outcome": "UNRESOLVED", "reason": "no-rule", "class": cls}
    ms = marks(line, ref)
    if len(ms) != 1:
        return {"outcome": "UNRESOLVED", "class": cls,
                "reason": "ambiguous" if ms else "no-candidate"}
    m = mark_np(line, *ms[0])
    if m["plural"] or not m["noun"] or m["noun"][2] in PLAYER_NOUNS:
        return {"outcome": "UNRESOLVED", "reason": "no-candidate", "class": cls}
    mark_noun = m["noun"][2]
    if phrase != "it":
        want = phrase.split()[1]
        if not (want == mark_noun or want in AGREE_ANY or mark_noun in AGREE_ANY):
            return {"outcome": "UNRESOLVED", "reason": "no-candidate", "class": cls}
    mk = next(k for k in range(len(clauses)) if starts[k] <= m["start"]
              and (k + 1 == len(clauses) or m["start"] < starts[k + 1]))
    np_end = m["noun"][1]
    # Between, with the reference's own governing region left out.
    cut = ref
    if ci > mk:
        own = [r for r in lregs if r["k"] == ci and r["span"][0] <= ref < r["span"][1]]
        if own and len(aq.effect_heads(line[own[0]["span"][0]:ref])) == 1:
            cut = own[0]["span"][0]
    between = line[m["end"]:cut]
    heads = [r["head"] for r in lregs if m["end"] <= r["head_span"][0] < cut]
    mreg = [r for r in lregs if r["k"] == mk and r["span"][0] <= m["start"] < r["span"][1]]
    mhead = mreg[0]["head"] if mreg else None
    pw = _prev_word(line, m["start"])
    # 4. continuity (CR 400.7)
    if (mhead in ZONE or (pw and pw[2] in ZONE) or any(h in ZONE for h in heads)
            or any(rx.search(t) for rx in _CONT_TEXT
                   for t in (between, line[max(0, m["start"] - CONT_WINDOW):np_end]))
            or _CARD_NP.match(line, m["end"])):
        return {"outcome": "UNRESOLVED", "reason": "continuity", "class": cls}
    # 5. competing antecedent
    full = line[m["end"]:ref]
    if (mhead in CREATE or heads
            or _COMPETE.search(full)
            or _COMPETE.search(line[max(0, m["start"] - COMPETE_WINDOW):m["start"]])
            or _MASS.search(full)
            or (phrase == "it" and _SELF.search(full))
            or any(_INDEF.search(t) or _CHOOSE.search(t)
                   for t in (line[:m["start"]], line[np_end:ref]))):
        return {"outcome": "UNRESOLVED", "reason": "competing-antecedent", "class": cls}
    return {"outcome": "RESOLVED", "reason": None, "class": cls,
            "endpoint": {"kind": "OBJECT", "clause": mk,
                         "mark_span": [m["start"] - starts[mk], m["end"] - starts[mk]]}}


def r3_named(clauses: list, ci: int, offset: int, regions: list) -> list:
    """§I5.8 note: the R3 list a plural reference names, by h_region_kill.py's
    R3 code -- named only when exactly one earlier region holds one
    coordinated P3 list; never a resolution."""
    found = []
    for k in range(ci + 1):
        rec = {"clause_text": clauses[k]}
        for r in regions[k]:
            if k == ci and r["span"][0] >= offset:
                continue
            seg = clauses[k][r["span"][0]:r["span"][1]]
            lst = hk.r3_list(seg, hk._candidates(rec, r))
            if lst:
                found.append({"clause": k, "region_span": list(r["span"]),
                              "list_marks": [[r["span"][0] + a, r["span"][0] + b, kd]
                                             for a, b, kd in lst]})
    return found if len(found) == 1 else []


# ------------------------------------------------------------- E5 / E6 / residue

def e5(clause: str, offset: int) -> dict:
    if re.match(r"the same(?![\w'’]).*?(?<![\w'’])as(?![\w'’])", clause[offset:], re.I):
        return {"outcome": "NOT-COREFERENCE", "reason": None, "class": "E5"}
    return {"outcome": "UNRESOLVED", "reason": "no-rule", "class": "E5"}


def e6(kind: str, delayed: bool) -> dict:
    if kind == "conditionality" and delayed:
        return {"outcome": "OUT-OF-SCOPE", "reason": None, "class": None}
    return None


def residue(phrase: str) -> dict:
    return {"outcome": "UNRESOLVED", "reason": "no-rule", "class": None}


def overlap(spans: list, counts: dict) -> list:
    """§I5.1 overlap over one clause. `spans` [(start, end, phrase)] of every
    P4 candidate there (in rank order), `counts` phrase -> whole-word
    occurrences. Returns, per span, whether it is an overlap."""
    per = Counter(p for _, _, p in spans)
    out = []
    for a, b, p in spans:
        inside = any(x <= a and b <= y and (y - x) > (b - a) for x, y, _ in spans)
        out.append(inside or counts.get(p, 0) < per[p])
    return out


def discovery(line: str, candidate_phrases: list) -> list:
    """§I5.7: every whole-word, case-insensitive occurrence of a discovery form
    in a line: [(form, position, covered)]."""
    low = [_low(p) for p in candidate_phrases]
    out = []
    for f in DISCOVERY:
        cov = any(p.startswith(f) for p in low)
        for m in _ww(f).finditer(line):
            out.append((f, m.start(), cov))
    return sorted(out, key=lambda x: (x[1], x[0]))


# ------------------------------------------------------------- the card

def _faces(card: dict) -> list:
    return fl._rules().raw_faces(card)


def card_context(card: dict) -> dict:
    """The card's chain (units paragraphs, clauses, regions) and P4 lines,
    tied line-for-paragraph or HALT."""
    oid = card["oracle_id"]
    units = fl.units(card)
    faces = _faces(card)
    paras = []
    for (fi, pi), _raw, canon in units:
        text = fx.strip_reminder(canon)
        paras.append({"face": fi, "paragraph": pi, "text": text,
                      "clauses": fx.sentence_spans(text)})
    lines = aq._card_lines(card)
    tied = [p for p in paras if p["clauses"]]
    if len(tied) != len(lines):
        fc.halt(f"{oid}: {len(lines)} P4 lines against {len(tied)} chain paragraphs")
    for k, (line, p) in enumerate(zip(lines, tied)):
        if line != " ".join(p["clauses"]):
            fc.halt(f"{oid}: P4 line {k} differs from its chain paragraph "
                    f"{p['face']}:{p['paragraph']}")
        p["line"] = k
    ctext = hr.card_rules_text(card)
    regions = {}

    def regs(p: dict) -> list:
        key = (p["face"], p["paragraph"])
        if key not in regions:
            out = []
            for ci, seg in enumerate(p["clauses"]):
                rec = hr.clause_record(oid, p["face"], p["paragraph"], ci, seg, 0,
                                       len(seg), "chain-clause", card_text=ctext,
                                       card_name=card.get("name"))
                out.append([{"head": r["head"], "head_span": r["head_span"],
                             "span": r["span"]} for r in rec["regions"]])
            regions[key] = out
        return regions[key]

    face_paras = {}
    for p in tied:
        face_paras.setdefault(p["face"], []).append(p)
    return {"oid": oid, "card": card, "paras": paras, "lines": lines, "tied": tied,
            "regs": regs, "face_paras": face_paras,
            "type_lines": [f.get("type_line") or card.get("type_line") for f in faces]}


def _face(ctx: dict, fi: int) -> dict:
    """§I5.3 E2's face: its own type line (the card's for a single-faced
    card) and its paragraphs with their regions."""
    ps = ctx["face_paras"][fi]
    tl = (ctx["type_lines"][fi] if fi < len(ctx["type_lines"])
          else ctx["card"].get("type_line"))
    return {"type_line": tl,
            "paragraphs": [{"text": p["text"], "clauses": p["clauses"],
                            "regions": ctx["regs"](p)} for p in ps]}


def locate(ctx: dict, refs: list) -> list:
    """§I5.1 offsets and overlap for every P4 candidate of a card (created
    ones included, so ranks match the printed occurrences)."""
    by_clause = {}
    for i, r in enumerate(refs):
        by_clause.setdefault((r["line"], r["sentence"]), []).append(i)
    cond = {n: rx for n, rx, _ in aq._CONDITION_MARKERS}
    out = [None] * len(refs)
    for (li, si), idx in by_clause.items():
        clause = ctx["tied"][li]["clauses"][si]
        rank, spans, sidx, counts = Counter(), [], [], {}
        for i in idx:
            r = refs[i]
            ph = r["phrase"]
            n = rank[(r["kind"] == "conditionality", ph)]
            rank[(r["kind"] == "conditionality", ph)] += 1
            if r["kind"] == "conditionality":
                occ = [m.start() for m in cond[ph].finditer(clause.lower())]
                out[i] = {"char_offset": occ[n] if n < len(occ) else None, "rank": n,
                          "overlap": False}
                continue
            occ = [m.start() for m in _ww(ph).finditer(clause)]
            counts[ph] = len(occ)
            if n < len(occ):
                pos = occ[n]
            else:
                plain = [m.start() for m in re.finditer(re.escape(ph), clause, re.I)]
                pos = plain[n] if n < len(plain) else None
            out[i] = {"char_offset": pos, "rank": n, "overlap": False}
            if pos is not None:
                spans.append((pos, pos + len(ph), ph))
                sidx.append(i)
            else:
                out[i]["overlap"] = True
        for i, ov in zip(sidx, overlap(spans, counts)):
            out[i]["overlap"] = out[i]["overlap"] or ov
    return out


def resolve(ctx: dict, r: dict, loc: dict) -> dict:
    """Route one pressure-set candidate to its §I5.3 rule."""
    p = ctx["tied"][r["line"]]
    ci, off, ph, kind = r["sentence"], loc["char_offset"], r["phrase"], r["kind"]
    six = e6(kind, r["delayed"])
    if six:
        return dict(six, rule="E6")
    if loc["overlap"]:
        return {"rule": "residue", "outcome": "UNRESOLVED", "reason": "overlap",
                "class": None}
    if kind == "cr607-linkage":
        fps = ctx["face_paras"][p["face"]]
        res = e2(ph, _face(ctx, p["face"]), fps.index(p), ci, off)
        if res.get("endpoint"):
            q = fps[res["endpoint"].pop("paragraph")]
            res["endpoint"]["address"] = [q["face"], q["paragraph"],
                                          res["endpoint"].pop("clause")]
        return dict(res, rule="E2")
    regions = ctx["regs"](p)
    if kind == "kind-unclear":
        if ph == "this way":
            res = dict(e1(p["clauses"], ci, off, regions), rule="E1")
            res.pop("verb", None)
        elif ph == "the copy":
            res = dict(e3(p["clauses"], ci, off), rule="E3")
        elif ph == "the same":
            res = dict(e5(p["clauses"][ci], off), rule="E5")
        else:
            res = dict(residue(ph), rule="residue")
    elif kind == "coreference":
        res = dict(e4(ph, p["clauses"], ci, off, regions), rule="E4")
        if res["reason"] == "plural-r3":
            res["r3"] = r3_named(p["clauses"], ci, off, regions)
    else:
        fc.halt(f"a pressure-set candidate of kind {kind!r} reaches no rule")
    if res.get("endpoint"):
        res["endpoint"]["address"] = [p["face"], p["paragraph"],
                                      res["endpoint"].pop("clause")]
    return res


# ------------------------------------------------------------- build

def reconcile_i4(fig: dict, c02: dict, want: dict = None) -> dict:
    want = I4 if want is None else want
    p4 = c02["p4"]
    for k, v in want.items():
        if fig[k] != v or p4.get(k) != v:
            fc.halt(f"§I4 reconciliation: {k} is {fig[k]} (C02 {p4.get(k)}), §I4 "
                    f"states {v}: a STOP")
    return dict(want)


def extract(cards: dict) -> tuple:
    """The frozen P4 extraction in the frozen `p4` order, every candidate with
    its card context index; and the §I4 figures."""
    out, ctxs = [], {}
    fig = {"cards_in_corpus": len(cards), "cards_with_candidates": 0,
           "total_candidate_references": 0, "by_kind": Counter(),
           "delayed_marked_references": 0, "cross_line_references": 0,
           "references_excluded_inside_created_abilities": 0}
    for oid, card in sorted(cards.items(), key=lambda kv: kv[1]["name"]):
        allr = aq.relation_candidates(card)
        refs = [r for r in allr if not r["created_ability"]]
        fig["references_excluded_inside_created_abilities"] += len(allr) - len(refs)
        if not allr:
            continue
        ctxs[oid] = (allr, refs)
        if not refs:
            continue
        fig["cards_with_candidates"] += 1
        fig["total_candidate_references"] += len(refs)
        for r in refs:
            fig["by_kind"][r["kind"]] += 1
            fig["delayed_marked_references"] += bool(r["delayed"])
            fig["cross_line_references"] += bool(r["cross_line"])
        out.append(oid)
    fig["by_kind"] = dict(sorted(fig["by_kind"].items()))
    return out, ctxs, fig


def in_set(r: dict) -> bool:
    return r["kind"] in ("kind-unclear", "cr607-linkage") or bool(r["delayed"])


def _fixture_roles(cards: dict) -> dict:
    roles = {}
    for fam in hr.load_fixtures(cards):
        for m in fam["members"]:
            if m["oracle_id"]:
                roles.setdefault(m["oracle_id"], []).append(fam["role"])
    return {k: sorted(v) for k, v in roles.items()}


def _clause_text(ctx, addr):
    for p in ctx["paras"]:
        if (p["face"], p["paragraph"]) == (addr[0], addr[1]):
            return p["clauses"][addr[2]]
    return None


def measure(cards: dict, order: list, ctxs: dict) -> tuple:
    """Every pressure-set row, the coverage counts and the discovery report."""
    roles = _fixture_roles(cards)
    rows, coverage, out_phrase = [], Counter(), Counter()
    disc = {f: {"covered": 0, "uncovered": 0, "first_uncovered": []} for f in DISCOVERY}
    disc_occ = {f: [] for f in DISCOVERY}
    seen_ids = Counter()
    contexts = {}
    for oid, card in sorted(cards.items(), key=lambda kv: kv[1]["name"]):
        lines = aq._card_lines(card)
        allr, refs = ctxs.get(oid, ([], []))
        by_line = {}
        for r in refs:
            by_line.setdefault(r["line"], []).append(r["phrase"])
        for li, line in enumerate(lines):
            for f, pos, cov in discovery(line, by_line.get(li, [])):
                disc[f]["covered" if cov else "uncovered"] += 1
                if not cov:
                    disc_occ[f].append((card["name"], li, pos))
        if not refs:
            continue
        for r in refs:
            coverage[(r["kind"], in_set(r))] += 1
            if r["kind"] == "coreference" and not in_set(r):
                out_phrase[r["phrase"]] += 1
        members = [r for r in refs if in_set(r)]
        if not members:
            continue
        ctx = card_context(card)
        contexts[oid] = ctx
        locs = locate(ctx, allr)
        loc_of = {id(r): l for r, l in zip(allr, locs)}
        role = roles.get(oid)
        for r in refs:
            if not in_set(r):
                continue
            loc = loc_of[id(r)]
            p = ctx["tied"][r["line"]]
            res = resolve(ctx, r, loc)
            addr = f"{oid}:{p['face']}:{p['paragraph']}:{r['sentence']}"
            phrase = r["phrase"]
            row_id = f"{addr}@{loc['char_offset']}:{phrase}"
            seen_ids[row_id] += 1
            ep = res.get("endpoint")
            endpoint = None
            ep_text = None
            if ep:
                a = ep["address"]
                endpoint = {"kind": ep["kind"],
                            "clause": f"{oid}:{a[0]}:{a[1]}:{a[2]}"}
                if "region_span" in ep:
                    endpoint["region_span"] = ep["region_span"]
                if "mark_span" in ep:
                    endpoint["mark_span"] = ep["mark_span"]
                ep_text = _clause_text(ctx, a)
            face_text = "\n".join(q["text"] for q in ctx["face_paras"][p["face"]])
            rows.append({
                "row_id": row_id, "address": addr, "offset": loc["rank"],
                "char_offset": loc["char_offset"], "kind": r["kind"], "phrase": phrase,
                "delayed": bool(r["delayed"]), "rule": res["rule"],
                "outcome": res["outcome"], "reason": res["reason"],
                "endpoint": endpoint, "class": res["class"],
                "fixture_role": role[0] if role else None,
                "ref_text": p["clauses"][r["sentence"]], "endpoint_text": ep_text,
                "paragraph_text": p["text"], "face_text": face_text,
                "_r3": res.get("r3"),
            })
    dup = sorted(k for k, n in seen_ids.items() if n > 1)
    if dup:
        fc.halt(f"row_id is not unique: {dup[:5]}")
    for f in DISCOVERY:
        disc[f]["first_uncovered"] = [n for n, _, _ in sorted(disc_occ[f])[:3]]
    cov = {k: {"in_set": coverage[(k, True)], "out_of_set": coverage[(k, False)],
               "total": coverage[(k, True)] + coverage[(k, False)]}
           for k in sorted({k for k, _ in coverage})}
    return rows, cov, dict(sorted(out_phrase.items())), disc, contexts


def reach(rows: list) -> dict:
    by_rule = {}
    for r in rows:
        d = by_rule.setdefault(r["rule"], {"candidates": 0, **{o: 0 for o in OUTCOMES}})
        d["candidates"] += 1
        d[r["outcome"]] += 1
    reasons = Counter((r["rule"], r["reason"]) for r in rows if r["reason"])
    tot = {"candidates": len(rows), **{o: sum(1 for r in rows if r["outcome"] == o)
                                       for o in OUTCOMES}}
    e2 = Counter(r["endpoint"]["kind"] for r in rows
                 if r["rule"] == "E2" and r["outcome"] == "RESOLVED")
    sub = [r for r in rows if r["rule"] == "E4" and DELAYED_SUBSET in r["ref_text"].lower()]
    sub_c = Counter(r["outcome"] if r["outcome"] == "RESOLVED" else r["reason"]
                    for r in sub)
    return {
        "by_rule": dict(sorted(by_rule.items())), "total": tot,
        "by_rule_reason": [{"rule": k[0], "reason": k[1], "candidates": n}
                           for k, n in sorted(reasons.items(),
                                              key=lambda kv: (-kv[1], kv[0]))],
        "e2_endpoint_kinds": dict(sorted(e2.items())),
        "delayed_trigger_subset": {"candidates": len(sub),
                                   "by_outcome_or_reason": dict(sorted(sub_c.items()))},
    }


# §I5.5 and §I5.7, every printed figure (plus the plan's discovery addition).
EXPECTED = {
    "total": {"candidates": 5856, "RESOLVED": 1784, "UNRESOLVED": 3230,
              "NOT-COREFERENCE": 119, "OUT-OF-SCOPE": 723},
    "by_rule": {
        "E1": {"candidates": 1088, "RESOLVED": 529, "UNRESOLVED": 559,
               "NOT-COREFERENCE": 0, "OUT-OF-SCOPE": 0},
        "E2": {"candidates": 676, "RESOLVED": 498, "UNRESOLVED": 178,
               "NOT-COREFERENCE": 0, "OUT-OF-SCOPE": 0},
        "E3": {"candidates": 208, "RESOLVED": 196, "UNRESOLVED": 12,
               "NOT-COREFERENCE": 0, "OUT-OF-SCOPE": 0},
        "E4": {"candidates": 2844, "RESOLVED": 561, "UNRESOLVED": 2283,
               "NOT-COREFERENCE": 0, "OUT-OF-SCOPE": 0},
        "E5": {"candidates": 225, "RESOLVED": 0, "UNRESOLVED": 106,
               "NOT-COREFERENCE": 119, "OUT-OF-SCOPE": 0},
        "E6": {"candidates": 723, "RESOLVED": 0, "UNRESOLVED": 0,
               "NOT-COREFERENCE": 0, "OUT-OF-SCOPE": 723},
        "residue": {"candidates": 92, "RESOLVED": 0, "UNRESOLVED": 92,
                    "NOT-COREFERENCE": 0, "OUT-OF-SCOPE": 0},
    },
    "by_rule_reason": {
        ("E4", "no-candidate"): 1174, ("E4", "no-rule"): 488,
        ("E1", "detector-reach"): 335, ("E4", "plural-r3"): 302,
        ("E1", "no-candidate"): 211, ("E4", "competing-antecedent"): 179,
        ("E2", "no-candidate"): 135, ("E4", "continuity"): 120,
        ("E5", "no-rule"): 106, ("residue", "overlap"): 65,
        ("E2", "other-chooser"): 31, ("residue", "no-rule"): 27,
        ("E4", "ambiguous"): 14, ("E1", "ambiguous"): 13, ("E3", "no-candidate"): 12,
        ("E2", "ambiguous"): 10, ("E4", "expletive"): 6, ("E2", "no-rule"): 2},
    "e2_endpoint_kinds": {"LINKED": 322, "COREFERENT": 176},
    "delayed_trigger_subset": {"candidates": 450, "RESOLVED": 25, "no-candidate": 186,
                               "no-rule": 108, "plural-r3": 55, "continuity": 48,
                               "competing-antecedent": 26, "ambiguous": 2},
    "coverage": {"coreference": (21672, 2844), "conditionality": (8642, 723),
                 "cr607-linkage": (741, 741), "kind-unclear": (1548, 1548)},
    "discovery": {"uncovered": 1670, "covered": 2},
}


def reach_differences(rep: dict, expected: dict = None) -> list:
    """Every §I5.5 / §I5.7 figure the measurement differs on: [(figure, want, got)]."""
    want = EXPECTED if expected is None else expected
    got = rep["reach"]
    out = []
    for k, v in want["total"].items():
        out.append((f"total {k}", v, got["total"].get(k, 0)))
    for rule, d in want["by_rule"].items():
        for k, v in d.items():
            out.append((f"{rule} {k}", v, got["by_rule"].get(rule, {}).get(k, 0)))
    gr = {(x["rule"], x["reason"]): x["candidates"] for x in got["by_rule_reason"]}
    for k in sorted(set(want["by_rule_reason"]) | set(gr)):
        out.append((f"{k[0]} reason {k[1]}", want["by_rule_reason"].get(k, 0),
                    gr.get(k, 0)))
    for k, v in want["e2_endpoint_kinds"].items():
        out.append((f"E2 {k}", v, got["e2_endpoint_kinds"].get(k, 0)))
    sub = got["delayed_trigger_subset"]
    for k, v in want["delayed_trigger_subset"].items():
        g = sub["candidates"] if k == "candidates" else sub["by_outcome_or_reason"].get(k, 0)
        out.append((f"delayed-trigger subset {k}", v, g))
    for k in sorted(set(sub["by_outcome_or_reason"]) - set(want["delayed_trigger_subset"])):
        out.append((f"delayed-trigger subset {k}", 0, sub["by_outcome_or_reason"][k]))
    for k, (tot, ins) in want["coverage"].items():
        c = rep["coverage"]["by_kind"].get(k, {})
        out.append((f"coverage {k} total", tot, c.get("total", 0)))
        out.append((f"coverage {k} in set", ins, c.get("in_set", 0)))
    d = rep["coverage"]["discovery"]
    for k, v in want["discovery"].items():
        out.append((f"discovery {k}", v, sum(x[k] for x in d.values())))
    return [(f, w, g) for f, w, g in out if w != g]


def card_test(cards: dict, rows: list, contexts: dict, ctxs: dict) -> list:
    """§I5.7's card-test table, read from the pinned INTERFACES.md at run
    time (the script carries no card name), measured: per row, the P4
    candidates printed inside the quoted reference with in/out-of-set status,
    outcome and endpoint kind, and the discovery occurrences there."""
    text = (ROOT / hr.INTERFACES_REL).read_text(encoding="utf-8")
    sec = text[text.index("### I5.7"):text.index("### I5.8")]
    tab = sec[sec.index("| card | reference | C04 outcome |"):]
    out = []
    by_name = {}
    for oid, c in cards.items():
        by_name.setdefault(c["name"], []).append(oid)
    row_by_pos = {}
    for r in rows:
        row_by_pos[(r["address"], r["char_offset"], r["phrase"])] = r
    for ln in tab.split("\n")[2:]:
        if not ln.startswith("|"):
            break
        name, ref, printed = [x.strip() for x in ln.strip("|").split("|")]
        quote = ref.strip('"').strip("“”")
        parts = [x.strip() for x in quote.split("…") if x.strip()]
        oids = by_name.get(name, [])
        entry = {"card": name, "reference": ref, "printed_outcome": printed,
                 "found": False, "candidates": [], "discovery": []}
        if len(oids) != 1:
            entry["note"] = f"{len(oids)} cards carry this name"
            out.append(entry)
            continue
        card = cards[oids[0]]
        lines = aq._card_lines(card)
        hit = None
        for li, line in enumerate(lines):
            a = line.find(parts[0])
            if a >= 0:
                b = a + len(parts[0])
                for x in parts[1:]:
                    j = line.find(x, b)
                    if j >= 0:
                        b = j + len(x)
                hit = (li, a, b)
                break
        if hit is None:
            out.append(entry)
            continue
        entry["found"] = True
        li, a, b = hit
        allr, refs = ctxs.get(oids[0], ([], []))
        ctx = contexts.get(oids[0]) or card_context(card)
        p = ctx["tied"][li]
        starts, at = [], 0
        for c in p["clauses"]:
            starts.append(at)
            at += len(c) + 1
        locs = locate(ctx, allr)
        for r, loc in zip(allr, locs):
            if r["created_ability"] or r["line"] != li or loc["char_offset"] is None:
                continue
            pos = starts[r["sentence"]] + loc["char_offset"]
            if not (a <= pos < b):
                continue
            addr = f"{oids[0]}:{p['face']}:{p['paragraph']}:{r['sentence']}"
            row = row_by_pos.get((addr, loc["char_offset"], r["phrase"]))
            entry["candidates"].append({
                "phrase": r["phrase"], "kind": r["kind"], "in_set": in_set(r),
                "row_id": row["row_id"] if row else None,
                "outcome": row["outcome"] if row else None,
                "reason": row["reason"] if row else None,
                "endpoint_kind": (row["endpoint"] or {}).get("kind") if row else None})
        phrases = [r["phrase"] for r in refs if r["line"] == li]
        for f, pos, cov in discovery(lines[li], phrases):
            if a <= pos < b:
                entry["discovery"].append({"form": f, "covered": cov})
        out.append(entry)
    return out


# ------------------------------------------------------------- negative controls

def _halts(fn) -> bool:
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            fn()
    except SystemExit:
        return True
    return False


def synthetic(text: str, type_line: str = "Instant") -> list:
    """Every pressure-set row of a synthetic one-face card."""
    card = {"name": "Synthetic Control", "oracle_id": "synthetic", "oracle_text": text,
            "type_line": type_line, "layout": "normal"}
    allr = aq.relation_candidates(card)
    ctx = card_context(card)
    locs = locate(ctx, allr)
    out = []
    for r, loc in zip(allr, locs):
        if r["created_ability"] or not in_set(r):
            continue
        res = resolve(ctx, r, loc)
        out.append(dict(res, phrase=r["phrase"], kind=r["kind"]))
    return out


# (text, type line, rule, phrase, outcome, reason, endpoint kind)
SYNTHETIC = (
    ("Target creature gets +2/+2 until end of turn. Sacrifice it at the beginning of "
     "the next end step.", "Instant", "E4", "it", "RESOLVED", None, "OBJECT"),
    ("+ {1} — Exile target creature. Return it at the beginning of the next end step.",
     "Instant", "E4", "it", "UNRESOLVED", "continuity", None),
    ("Target creature gets +3/+3 until end of turn. Exile ~ with three time counters "
     "on it.", "Instant", "E4", "it", "UNRESOLVED", "competing-antecedent", None),
    ("You may play that card and you may spend mana as though it were mana of any "
     "color to cast it. When you cast a spell this way, draw a card.", "Instant",
     "E1", "this way", "UNRESOLVED", "no-candidate", None),
    ("Create a token. For each Aura attached to ~, create a token. Sacrifice all "
     "tokens created this way.", "Instant", "E1", "this way", "UNRESOLVED",
     "ambiguous", None),
    ("Sacrifice a permanent or discard a card this way.", "Instant", "E1", "this way",
     "UNRESOLVED", "ambiguous", None),
    ("Target creature gets +2/+2 until end of turn. Put a +1/+1 counter on it.",
     "Instant", "E4", "it", "RESOLVED", None, "OBJECT"),
    ("Put a +1/+1 counter on another target creature you control. It gains hexproof "
     "until end of turn.", "Instant", "E4", "it", "RESOLVED", None, "OBJECT"),
    ("Until end of turn, double target creature's power and it gains first strike.",
     "Instant", "E4", "it", "RESOLVED", None, "OBJECT"),
    ("Target attacking or blocking creature gets +4/+0 until end of turn. Destroy that "
     "creature at the beginning of the next end step.", "Instant", "E4",
     "that creature", "RESOLVED", None, "OBJECT"),
    ("~ deals 3 damage to any target. If a creature is dealt damage this way, it gets "
     "+5/+0 until end of turn.", "Instant", "E4", "it", "UNRESOLVED", "no-candidate",
     None),
    ("{T}: Choose a color. Creatures you control gain protection from the chosen "
     "color until end of turn.", "Artifact", "E2", "the chosen color", "RESOLVED",
     None, "COREFERENT"),
    ("Choose target creature with mana value 3 or less. If this spell was kicked, "
     "instead choose target creature. Exile the chosen creature.", "Sorcery", "E2",
     "the chosen creature", "UNRESOLVED", "other-chooser", None),
    ("Whenever this creature attacks, choose one of those creatures. Tap the chosen "
     "creature.", "Creature", "E2", "the chosen creature", "RESOLVED", None,
     "COREFERENT"),
    ("{X}: Choose a color. Target opponent exiles the top X cards of their library. "
     "For each card of the chosen color exiled this way, draw a card.", "Artifact",
     "E2", "the chosen color exiled", "RESOLVED", None, "COREFERENT"),
)


def _tampered_cr(rule: str) -> str:
    txt = cr.text()
    phrase = CR_OPERATIVE[rule]
    m = re.search(rf"^(?:\*\*)?{re.escape(rule)}\.?(?:\*\*)?\s+(.*)$", txt, re.M)
    a, b = m.span(1)
    return txt[:a] + m.group(1).replace(phrase, "") + txt[b:]


def negative_controls(names: list, oid: str, c02: dict, fig: dict, sample: dict,
                      rep_for_reach: dict) -> list:
    out = []

    def ctl(name, ok):
        if not ok:
            fc.halt(f"negative control failed: {name}")
        out.append({"control": name, "result": "fired"})

    for key in ("id", "kind", "cr", "pattern"):
        for bad_val in (names[0], oid):
            bad = dict(RULES[0], **{key: f"{RULES[0][key]} {bad_val}"})
            ctl(f"a card-keyed rule ({'card name' if bad_val == names[0] else 'oracle_id'} "
                f"in {key}) halts",
                _halts(lambda b=bad: hr.assert_not_card_keyed(list(RULES) + [b], names)))
    for rule in CR_OPERATIVE:
        ctl(f"a CR text missing {rule}'s operative phrase STOPs",
            _halts(lambda t=_tampered_cr(rule): cr_read(t)))
    for k in I4:
        bad = dict(I4, **{k: ({kk: v + 1 for kk, v in I4[k].items()}
                              if isinstance(I4[k], dict) else I4[k] + 1)})
        ctl(f"a rigged §I4 figure ({k}) halts",
            _halts(lambda b=bad: reconcile_i4(fig, c02, b)))
    card = dict(sample)
    real = aq._card_lines

    def rigged_lines(c):
        ls = real(c)
        return [ls[0] + " "] + ls[1:]
    aq._card_lines = rigged_lines
    try:
        ctl("a rigged P4 line differing from its chain paragraph halts",
            _halts(lambda: card_context(card)))
    finally:
        aq._card_lines = real
    bad = json.loads(json.dumps(EXPECTED["by_rule"]))
    bad["E1"]["RESOLVED"] += 1
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        code = check_reach(rep_for_reach, dict(EXPECTED, by_rule=bad))
    ctl("a rigged reach figure differing from §I5.5 makes --check-reach exit non-zero",
        code != 0)
    ctl("a rigged output carrying the absolute repository root fails "
        "--check-determinism",
        bool(hr.portability_violations(b'{"x": "' + str(ROOT).encode() + b'"}')))
    for text, tl, rule, phrase, outcome, reason, kind in SYNTHETIC:
        got = [x for x in synthetic(text, tl) if x["rule"] == rule
               and (x["phrase"] + " ").startswith(phrase + " ")]
        ok = (len(got) == 1 and got[0]["outcome"] == outcome
              and got[0]["reason"] == reason
              and (got[0].get("endpoint") or {}).get("kind") == kind)
        ctl(f"synthetic {rule} {phrase!r}: {outcome}"
            f"{' ' + reason if reason else ''}{' ' + kind if kind else ''} "
            f"({hashlib.sha256(text.encode()).hexdigest()[:12]})", ok)
    return out


# ------------------------------------------------------------- build

KEYS = ("row_id", "address", "offset", "char_offset", "kind", "phrase", "delayed",
        "rule", "outcome", "reason", "endpoint", "class", "fixture_role", "ref_text",
        "endpoint_text", "paragraph_text", "face_text")


def build() -> dict:
    identities = hr.verify_identities(hr.I1)
    blob = hr.verify_interface()
    crr = cr_read()
    cards, _, _ = fc.load_corpus_gated()
    c02 = json.loads((ROOT / hr.C02_REL).read_text(encoding="utf-8"))
    order, ctxs, fig = extract(cards)
    i4 = reconcile_i4(fig, c02)
    names = sorted({c["name"] for c in cards.values()})
    rule_ids = hr.assert_not_card_keyed(RULES, names)
    rows, cov, out_phrase, disc, contexts = measure(cards, order, ctxs)
    paragraphs = sum(len(ctx["tied"]) for ctx in contexts.values())
    all_pars = sum(1 for c in cards.values() for p in fl.units(c)
                   if fx.sentence_spans(fx.strip_reminder(p[2])))
    if all_pars != I5_PARAGRAPHS:
        fc.halt(f"§I5.1: {all_pars} non-empty chain paragraphs, §I5.1 states "
                f"{I5_PARAGRAPHS}")
    pressure = {"candidates": len(rows),
                "kind_unclear": sum(1 for r in rows if r["kind"] == "kind-unclear"),
                "cr607_linkage": sum(1 for r in rows if r["kind"] == "cr607-linkage"),
                "delay_marked": sum(1 for r in rows if r["delayed"]),
                "kind_unclear_and_delay_marked": sum(
                    1 for r in rows if r["kind"] == "kind-unclear" and r["delayed"]),
                "cr607_linkage_and_delay_marked": sum(
                    1 for r in rows if r["kind"] == "cr607-linkage" and r["delayed"]),
                "kind_unclear_and_cr607_linkage": 0}
    if (pressure["kind_unclear"], pressure["cr607_linkage"], pressure["delay_marked"]) \
            != (I4["by_kind"]["kind-unclear"], I4["by_kind"]["cr607-linkage"],
                I4["delayed_marked_references"]):
        fc.halt(f"the pressure set does not reconcile with §I4: {pressure}")
    rep = {"reach": reach(rows),
           "coverage": {"by_kind": cov, "discovery": disc}}
    sample = cards[rows[0]["address"].split(":")[0]]
    controls = negative_controls(names, rows[0]["address"].split(":")[0], c02, fig,
                                 sample, rep)
    r3 = [{"row_id": r["row_id"], "named_list": r["_r3"][0] if r["_r3"] else None}
          for r in rows if r["reason"] == "plural-r3"]
    sub = [r["row_id"] for r in rows
           if r["rule"] == "E4" and DELAYED_SUBSET in r["ref_text"].lower()]
    fixture_rows = [r["row_id"] for r in rows if r["fixture_role"] in FIXTURE_ROLES]
    tests = card_test(cards, rows, contexts, ctxs)
    candidates = [{k: r[k] for k in KEYS} for r in rows]
    return {
        "schema": "c04-refs/1",
        "interface": {"version": INTERFACE_VERSION, "path": hr.INTERFACES_REL,
                      "blob": blob, "sections": "§I5 (§I4 population)"},
        "script": {"path": SCRIPT, "sha256": hr._sha(SCRIPT)},
        "inputs": {rel: hr._sha(rel) for rel in INPUTS},
        "identities_i1": identities,
        "cr_read": crr,
        "rules": list(RULES), "rules_checked_not_card_keyed": rule_ids,
        "lists": {"IRREG": IRREG, "PREPS": list(PREPS), "DETS": list(DETS),
                  "SINGULAR": list(SINGULAR), "PLURAL": list(PLURAL),
                  "POSSESSIVE": list(POSSESSIVE), "OBJ_NOUNS": list(OBJ_NOUNS),
                  "ZONE": list(ZONE), "CREATE": list(CREATE), "MASS": list(MASS),
                  "DISCOVERY": list(DISCOVERY)},
        "vocabulary": {"outcomes": list(OUTCOMES), "endpoint_kinds": list(ENDPOINT_KINDS),
                       "reasons": list(REASONS), "status": "measurement labels only"},
        "reconciliation_i4": {"figures": i4, "c02": hr.C02_REL,
                              "paragraphs_tied": paragraphs,
                              "corpus_paragraphs_tied": all_pars},
        "pressure_set": pressure,
        "replacement_lineage": {
            "ruling": "§I5.8 ruling 6", "source": A01_REL, "verdict": a01_verdict(),
            "result": "A01 R2-A reported A1, A3 and A4 GENUINELY_MISSING; no "
                      "candidate resolves to a replacement-lineage endpoint"},
        "reach": rep["reach"],
        "delayed_trigger_subset": {
            "ruling": "§I5.8 ruling 14",
            "definition": f"E4 reference clause printing {DELAYED_SUBSET!r}",
            "finding": "the CR 603.7 trigger-to-creator link stays UNRESOLVED "
                       "(no-rule); this subset is the delayed-link measurement",
            "rows": sub},
        "plural_r3": r3,
        "coverage": {
            "by_kind": cov, "out_of_set_coreference_by_phrase": out_phrase,
            "discovery": disc,
            "note": "§I5.7: a report only; resolves nothing and is not read by M05",
            "card_test": tests},
        "m05_read_set": {
            "per_rule": {rule: sum(1 for r in rows if r["rule"] == rule
                                   and r["outcome"] == ("NOT-COREFERENCE" if rule == "E5"
                                                        else "RESOLVED"))
                         for rule in ("E1", "E2", "E3", "E4", "E5")},
            "fixture_rows": fixture_rows},
        "negative_controls": controls,
        "candidates": candidates,
    }


def render(report: dict) -> bytes:
    return (json.dumps(report, indent=1, sort_keys=True, ensure_ascii=True)
            + "\n").encode("utf-8")


# ---------------------------------------------------------------------- CLI

def verify() -> int:
    if not OUT.exists():
        print(f"STALE: {OUT_REL} does not exist", file=sys.stderr)
        return 1
    doc = json.loads(OUT.read_text(encoding="utf-8"))
    embedded = dict(doc.get("inputs") or {})
    embedded[SCRIPT] = (doc.get("script") or {}).get("sha256")
    stale = [rel for rel, want in sorted(embedded.items())
             if not (ROOT / rel).exists() or hr._sha(rel) != want]
    missing = sorted(set(INPUTS) - set(doc.get("inputs") or {}))
    for rel in stale:
        print(f"STALE: {rel}", file=sys.stderr)
    for rel in missing:
        print(f"STALE: {rel} is not embedded", file=sys.stderr)
    if stale or missing:
        return 1
    print(f"{OUT_REL}: every embedded hash is current ({len(embedded)} files)")
    return 0


def check_determinism() -> int:
    runs = []
    for _ in range(2):
        p = subprocess.run([sys.executable, str(HERE), "--emit"], cwd=str(ROOT),
                           capture_output=True)
        if p.returncode != 0:
            sys.stderr.write(p.stderr.decode("utf-8", "replace"))
            print(f"FAIL: regeneration exited {p.returncode}", file=sys.stderr)
            return 1
        runs.append(p.stdout)
    if runs[0] != runs[1]:
        print("FAIL: two regenerations differ byte-for-byte", file=sys.stderr)
        return 1
    bad = hr.portability_violations(runs[0])
    if bad:
        print(f"FAIL: output carries the {', '.join(bad)}", file=sys.stderr)
        return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(runs[0])
    print(f"{OUT_REL}: x2 byte-identical, portable, sha256 "
          f"{hashlib.sha256(runs[0]).hexdigest()} ({len(runs[0])} bytes)")
    return 0


def _figure_rows(rep: dict, figure: str) -> list:
    """The measured rows behind a per-rule or per-reason figure."""
    parts = figure.split()
    rows = rep.get("candidates") or []
    if len(parts) == 3 and parts[1] == "reason":
        return [r["row_id"] for r in rows if r["rule"] == parts[0] and r["reason"] == parts[2]]
    if len(parts) == 2 and parts[1] in OUTCOMES:
        return [r["row_id"] for r in rows if r["rule"] == parts[0] and r["outcome"] == parts[1]]
    if len(parts) == 2 and parts[0] == "E2" and parts[1] in ENDPOINT_KINDS:
        return [r["row_id"] for r in rows if r["rule"] == "E2"
                and (r["endpoint"] or {}).get("kind") == parts[1]]
    return []


def check_reach(rep: dict = None, expected: dict = None) -> int:
    rep = build() if rep is None else rep
    diffs = reach_differences(rep, expected)
    if not diffs:
        print("REACH: every §I5.5 and §I5.7 figure equal "
              f"({rep['reach']['total']['candidates']} candidates)")
        return 0
    for f, w, g in diffs:
        print(f"DIFFERS: {f}: §I5 states {w}, measured {g}")
        for rid in _figure_rows(rep, f):
            print(f"    row {rid}")
    print(f"STOP to the Captain: {len(diffs)} figure(s) differ from §I5.5/§I5.7; "
          f"the rules are not tuned to match", file=sys.stderr)
    return 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--emit", action="store_true", help="write the report to stdout only")
    g.add_argument("--check-determinism", action="store_true")
    g.add_argument("--check-reach", action="store_true")
    g.add_argument("--verify", action="store_true")
    a = ap.parse_args(argv)
    if a.verify:
        return verify()
    if a.check_determinism:
        return check_determinism()
    if a.check_reach:
        return check_reach()
    data = render(build())
    bad = hr.portability_violations(data)
    if bad:
        fc.halt(f"output carries the {', '.join(bad)}")
    if a.emit:
        sys.stdout.buffer.write(data)
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(data)
    print(f"wrote {OUT_REL} sha256 {hashlib.sha256(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
