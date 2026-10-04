#!/usr/bin/env python3
"""A01-PROBE — the V1 P0.6 Round-2 seam measurement (R2-A, R2-B, R2-C).

PINNED TO oracle-compiler-interface/3 (oracle_compiler/INTERFACES.md blob
119778a68c0e4e8378f0a117b7c22884ec5eda4b). A MEASUREMENT ONLY: it decides no
truth item, mints no vocabulary, schema field, relation kind, coordinate or
primitive, and writes one ignored JSON report. Read-only over the corpus.

INPUTS. The interface/3 I1 identities are verified first through
`h_region.verify_identities` (f0_select's pins plus the accepted C02 output)
and the interface blob through `h_region.verify_interface`; a differing
identity HALTS. The corpus is read through the ratified chain
(`h_region.chain_clauses`: foundry_locality.units > strip_reminder >
sentence_spans; reminder text stripped). Every clause is addressed by its
four-coordinate occurrence (oracle_id, face, paragraph, clause).

MEMBERSHIP FORMS ARE DATA: `RULES`, each entry exactly {id, kind, cr,
pattern}, one per membership, pronoun-candidate and contrast form, checked by
`h_region.assert_not_card_keyed` over every corpus card and face name. A
pattern names a frozen set by reference, never inline. Every cited CR rule is
read at run time through `foundry_cr`; a cited rule missing from the pinned CR
is a STOP.

R2-A  CR 614.1a: a chain clause holding the rule's quoted word. Partitioned by
      the word after the last 'would' before it (two words after 'be'), or
      'no-would:' + the clause's first word. Scope: 614.1a only (the 614.1b-e
      forms and CR 616 ordering are not audited).
R2-B  CR 723: a control verb immediately followed by an explicit player term;
      pronoun candidates and the CR 108.4 / 613.1b object-control contrast set
      are listed beside it (precedence member > pronoun > contrast).
R2-C  CR 613.1f / 607.2a: has/have/gains/gain + 'all (activated) abilities
      of' + a noun phrase; the quoted-ability and CR 702 keyword grants are
      the contrast set (precedence member > contrast).

PER MEMBER (and per R2-B pronoun candidate), for the member clause and each
following chain clause of its (face, paragraph) -- its paragraph tail -- the
existing code's own output, never re-implemented: the interface/3 H-REGION
derivation (`h_region.clause_record`), the frozen P4 `relation_candidates`
mapped to chain clauses by order, and `foundry_aq4_probes.participants`.

    python3 experiments/oracle_ingest/a01_seams.py                      # write
    python3 experiments/oracle_ingest/a01_seams.py --emit               # stdout only
    python3 experiments/oracle_ingest/a01_seams.py --check-determinism  # x2 + write
    python3 experiments/oracle_ingest/a01_seams.py --verify             # stale?
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))

import h_region as h                         # noqa: E402  (also sets sys.path)
import foundry_common as fc                  # noqa: E402
import foundry_cr as cr                      # noqa: E402
import foundry_shape_extractor as fx         # noqa: E402
import foundry_locality as fl                # noqa: E402
import foundry_aq4_probes as aq              # noqa: E402

SCRIPT = "experiments/oracle_ingest/a01_seams.py"
OUT_REL = "experiments/out/oracle_ingest/a01/seams.json"
OUT = ROOT / OUT_REL

INPUTS = sorted(set(h.INPUTS) | {
    "experiments/oracle_ingest/h_region.py",
    "experiments/foundry_cr.py",
    "experiments/foundry_common.py",
    "experiments/foundry_locality.py",
    "experiments/foundry_shape_extractor.py",
})

# Recall controls are CHECKS, never keys: no rule reads them.
R2A_CONTROLS = ("eccc9a54-2b56-4a02-9926-258d5b2e25fb",
                "51d517c9-2812-44ce-ab4d-e5422b5ecf6c",
                "eae87919-6322-4bd2-ae9c-b1ce25d686da",
                "766c644c-04fe-4b01-93dd-09a50d78d01f")
R2A_FIXTURE_ROLE = "replacement-event-lineage"
R2B_CONTROLS = ("a806f4ee-f48a-46c3-8772-5aaabebe4c7e",
                "face0a43-6604-4508-b511-81ab0bef7b18",
                "4e7a8817-1a66-45c3-ade9-eac79b40b89f",
                "1f438b8f-fe23-4f3b-ab2e-f6c33676c462")
R2C_CONTROLS = ("c259e16f-2a44-4552-8678-815f757a02e8",
                "2fdeb920-2e48-4308-9517-743eec219c04",
                "93cfa771-067f-44ed-9e29-6caf698ee9aa")
R2C_FIXTURE_ROLE = "ability-borrowing-inheritance-pressure"

# Every CR rule this probe cites; each is read at run time, a missing one STOPs.
CITED = {
    "R2-A": ("614.1a", "614.5", "616.1"),
    "R2-A scope (excluded forms, cited only)": ("614.1b", "614.1c", "614.1d",
                                                "614.1e"),
    "R2-B": ("723.1", "723.2", "723.3", "723.4", "723.5", "723.6", "723.7",
             "723.8"),
    "R2-B contrast": ("108.4", "613.1b"),
    "R2-C": ("613.1f", "607.2a"),
}
READ_POSITIONS = 10


# ------------------------------------------------------------- CR readers

def cr_rule(rule: str, txt: str) -> str:
    """The text of one numbered rule in `txt`; anything but exactly one line
    carrying that number STOPs."""
    hits = re.findall(rf"^(?:\*\*)?{re.escape(rule)}\.?(?:\*\*)? (.*)$", txt, re.M)
    if len(hits) != 1:
        fc.halt(f"CR {rule} is cited by A01 but found {len(hits)} time(s) in the "
                f"pinned CR")
    return hits[0]


def cr_read_cited(txt: str) -> dict:
    """Every cited rule, read from `txt`."""
    return {r: cr_rule(r, txt) for rules in CITED.values() for r in rules}


def cr_instead_word(txt: str) -> str:
    """CR 614.1a's quoted word: exactly one distinct quoted single word."""
    quoted = sorted(set(re.findall(r"“([^”]+)”", cr_rule("614.1a", txt))))
    if len(quoted) != 1 or not re.fullmatch(r"[a-z]+", quoted[0]):
        fc.halt(f"CR 614.1a does not quote exactly one word: {quoted}")
    return quoted[0]


# Declared (CR 207.2d precedent): the CR spells a count as an English word.
NUMBER_WORDS = ("one", "two", "three", "four", "five", "six", "seven", "eight",
                "nine", "ten")


def cr_723_2_names(txt: str) -> list:
    """The cards CR 723.2 names, from its one parenthetical; the count the
    rule states must equal the names parsed, or the parse STOPs."""
    line = cr_rule("723.2", txt)
    paren = re.findall(r"\(([^()]+)\)", line)
    count = re.match(r"([A-Za-z]+) cards \(", line)
    if len(paren) != 1 or not count or count.group(1).lower() not in NUMBER_WORDS:
        fc.halt(f"CR 723.2 is not of the form '<N> cards (<a> and <b>) ...': {line!r}")
    names = [n.strip() for n in re.split(r", and |, | and ", paren[0]) if n.strip()]
    if len(names) != NUMBER_WORDS.index(count.group(1).lower()) + 1:
        fc.halt(f"CR 723.2 states {count.group(1)} cards but names {names}")
    return names


INSTEAD = cr_instead_word(cr.text())

# --------------------------------------------------------- membership forms

PLAYER_TERMS = ("target player", "target opponent", "that player", "each opponent",
                "your opponents", "an opponent")
PRONOUN_FORMS = ("them", "him or her")
_ALT = lambda xs: "(?:" + "|".join(re.escape(x) for x in xs) + ")"
_R2B_VERB = r"\b(?:gains? control of|controls?)"
_R2B_MEMBER = re.compile(_R2B_VERB + r"\s+" + _ALT(PLAYER_TERMS) + r"\b", re.I)
_R2B_PRONOUN = re.compile(_R2B_VERB + r"\s+" + _ALT(PRONOUN_FORMS) + r"\b", re.I)
_R2B_CONTRAST_OF = re.compile(
    r"\b(?:gains?|exchanges?) control of\s+(?!" + _ALT(PLAYER_TERMS) + r"\b|"
    + _ALT(PRONOUN_FORMS) + r"\b)\S", re.I)
_R2B_CONTRAST_ATTACHED = re.compile(r"\bcontrols?\s+(?:enchanted|equipped)\b", re.I)
_R2C_VERB = re.compile(r"\b(?:has|have|gains|gain)\s+", re.I)
_R2C_MEMBER = re.compile(
    r"\b(?:has|have|gains|gain)\s+(?:all activated abilities of|all abilities of)\s+\S",
    re.I)
_R2A_WORD = re.compile(rf"\b{re.escape(INSTEAD)}\b", re.I)
_WOULD = re.compile(r"\bwould\b", re.I)
_WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")
_R2C_KEYWORDS = sorted(aq._CR702_KEYWORD_NAMES, key=lambda k: (-len(k), k))

RULES = (
    {"id": "r2a-member", "kind": "member", "cr": "CR 614.1a",
     "pattern": "the one word CR 614.1a quotes, read from the pinned CR through "
                "foundry_cr, word-bounded, in a chain clause"},
    {"id": "r2a-class-would", "kind": "partition", "cr": "CR 614.1a",
     "pattern": "lowercased word after the final " + _WOULD.pattern + " before the "
                "member word; with the next word when it is 'be'; the key's final "
                "word is the would-verb"},
    {"id": "r2a-class-no-would", "kind": "partition", "cr": "CR 614.1a",
     "pattern": "no " + _WOULD.pattern + " before the member word: 'no-would:' + "
                "the clause's first " + _WORD.pattern},
    {"id": "r2b-member", "kind": "member", "cr": "CR 723.1 / 723.2",
     "pattern": _R2B_MEMBER.pattern},
    {"id": "r2b-pronoun", "kind": "pronoun-candidate", "cr": "CR 723.1",
     "pattern": _R2B_PRONOUN.pattern},
    {"id": "r2b-contrast-of", "kind": "contrast", "cr": "CR 108.4 / 613.1b",
     "pattern": _R2B_CONTRAST_OF.pattern},
    {"id": "r2b-contrast-attached", "kind": "contrast", "cr": "CR 108.4 / 613.1b",
     "pattern": _R2B_CONTRAST_ATTACHED.pattern},
    {"id": "r2c-member", "kind": "member", "cr": "CR 613.1f / 607.2a",
     "pattern": _R2C_MEMBER.pattern},
    {"id": "r2c-contrast-quoted", "kind": "contrast", "cr": "CR 613.1f",
     "pattern": _R2C_VERB.pattern + " then a span of "
                "foundry_shape_extractor.quoted_spans starting there"},
    {"id": "r2c-contrast-keyword", "kind": "contrast", "cr": "CR 613.1f / 702",
     "pattern": _R2C_VERB.pattern + " then a CR 702 keyword name in "
                "foundry_aq4_probes._CR702_KEYWORD_NAMES, word-bounded"},
)
PRECEDENCE = {"R2-B": ["member", "pronoun", "contrast"], "R2-C": ["member", "contrast"]}


# ----------------------------------------------------------- pure functions

def r2a_member(text: str) -> bool:
    return bool(_R2A_WORD.search(text))


def r2a_would(text: str):
    """(class key, would-verb, would-verb offset) of an R2-A member; the verb
    and offset are None for a no-would class; None for a non-member."""
    m = _R2A_WORD.search(text)
    if not m:
        return None
    woulds = list(_WOULD.finditer(text, 0, m.start()))
    if not woulds:
        first = _WORD.search(text)
        if not first:
            fc.halt(f"R2-A member clause has no word to key its class: {text!r}")
        return "no-would:" + first.group(0).lower(), None, None
    w = list(_WORD.finditer(text, woulds[-1].end()))
    if not w or text[woulds[-1].end():w[0].start()].strip():
        fc.halt(f"R2-A: 'would' is not followed by a word: {text!r}")
    verb = w[0]
    key = verb.group(0).lower()
    if key == "be":
        if len(w) < 2 or text[verb.end():w[1].start()].strip():
            fc.halt(f"R2-A: 'would be' is not followed by a word: {text!r}")
        verb = w[1]
        key += " " + verb.group(0).lower()
    return key, verb.group(0).lower(), verb.start()


def r2a_class(text: str):
    got = r2a_would(text)
    return None if got is None else got[0]


def r2b_matches(text: str) -> dict:
    return {"member": [m.span() for m in _R2B_MEMBER.finditer(text)],
            "pronoun": [m.span() for m in _R2B_PRONOUN.finditer(text)],
            "contrast": sorted([m.span() for m in _R2B_CONTRAST_OF.finditer(text)]
                               + [m.span() for m in
                                  _R2B_CONTRAST_ATTACHED.finditer(text)])}


def r2b_classify(text: str) -> str:
    """member | pronoun | contrast | none (precedence member > pronoun > contrast)."""
    got = r2b_matches(text)
    return next((k for k in PRECEDENCE["R2-B"] if got[k]), "none")


def r2c_matches(text: str) -> dict:
    quoted = {a for a, _ in fx.quoted_spans(text)}
    contrast = []
    for m in _R2C_VERB.finditer(text):
        if m.end() in quoted:
            contrast.append((m.start(), m.end(), "quoted"))
            continue
        low = text[m.end():].lower()
        kw = next((k for k in _R2C_KEYWORDS if low.startswith(k)
                   and not re.match(r"\w", low[len(k):len(k) + 1])), None)
        if kw:
            contrast.append((m.start(), m.end() + len(kw), "keyword:" + kw))
    return {"member": [m.span() for m in _R2C_MEMBER.finditer(text)],
            "contrast": contrast}


def r2c_classify(text: str) -> str:
    """member | contrast | none (precedence member > contrast)."""
    got = r2c_matches(text)
    return next((k for k in PRECEDENCE["R2-C"] if got[k]), "none")


def read_positions(n: int) -> list:
    """The 10 READ POSITIONS round(i*(n-1)/9), i = 0..9; all when n <= 10."""
    if n <= READ_POSITIONS:
        return list(range(n))
    return [round(i * (n - 1) / (READ_POSITIONS - 1)) for i in range(READ_POSITIONS)]


# ------------------------------------------------------------- the corpus

def addr(oid: str, fi: int, pi: int, ci: int) -> str:
    return f"{oid}:{fi}:{pi}:{ci}"


def _sort_key(a: str) -> tuple:
    oid, fi, pi, ci = a.split(":")
    return oid, int(fi), int(pi), int(ci)


def p4_paragraphs(lines: list, paragraphs: list, label: str) -> list:
    """P4 line k is the k-th foundry_locality.units paragraph holding a chain
    clause (a wholly-reminder paragraph prints no P4 line); it must equal that
    paragraph's chain clauses joined by one space, and its P4 sentence count
    must equal its chain clause count, or HALT."""
    if len(lines) != len(paragraphs):
        fc.halt(f"{label}: {len(lines)} P4 line(s) but {len(paragraphs)} chain "
                f"paragraph(s)")
    for k, (line, (coord, clauses)) in enumerate(zip(lines, paragraphs)):
        if line != " ".join(clauses):
            fc.halt(f"{label}: P4 line {k} differs from chain paragraph {coord}")
        if len(fx.sentence_spans(line)) != len(clauses):
            fc.halt(f"{label}: P4 line {k} has {len(fx.sentence_spans(line))} "
                    f"sentence(s), chain paragraph {coord} has {len(clauses)} clause(s)")
    return [coord for coord, _ in paragraphs]


def card_view(oid: str, card: dict) -> dict:
    chain = h.chain_clauses(card)
    by_para = {}
    for fi, pi, ci, seg in chain:
        by_para.setdefault((fi, pi), []).append(seg)
    paragraphs = [(k, by_para[k]) for k, _r, _c in fl.units(card) if k in by_para]
    return {"oid": oid, "card": card, "chain": chain, "paragraphs": paragraphs}


def p4_by_clause(view: dict) -> dict:
    coords = p4_paragraphs(aq._card_lines(view["card"]), view["paragraphs"],
                           view["oid"])
    out = {}
    for c in aq.relation_candidates(view["card"]):
        fi, pi = coords[c["line"]]
        out.setdefault(addr(view["oid"], fi, pi, c["sentence"]), []).append(
            {"kind": c["kind"], "arm": c["phrase"], "cr": c["cr"],
             "delayed": c["delayed"], "created_ability": c["created_ability"]})
    return out


H_FIELDS = ("scope", "heads_legacy", "heads_region", "r2_dropped_heads",
            "r4_dropped_heads", "r4_label", "regions", "role_spans",
            "role_marks_in_created_ability")


def clause_evidence(view: dict, p4: dict, fi: int, pi: int, ci: int, text: str,
                    role: str) -> dict:
    card = view["card"]
    rec = h.clause_record(view["oid"], fi, pi, ci, text, 0, len(text), "chain-clause",
                          card_text=h.card_rules_text(card), card_name=card["name"])
    a = addr(view["oid"], fi, pi, ci)
    return {"address": a, "role": role, "clause_text": text,
            "h_region": {k: rec[k] for k in H_FIELDS},
            "p4": p4.get(a, []), "participants": aq.participants(text)}


def paragraph_evidence(view: dict, p4: dict, fi: int, pi: int, ci: int) -> list:
    """The member clause, then each following chain clause of its (face,
    paragraph) -- the paragraph tail -- each with its own address."""
    return [clause_evidence(view, p4, f, p, c, seg, "member" if c == ci else "tail")
            for f, p, c, seg in view["chain"] if (f, p) == (fi, pi) and c >= ci]


def r2a_record(view: dict, p4: dict, fi: int, pi: int, ci: int, text: str) -> dict:
    key, verb, off = r2a_would(text)
    ev = paragraph_evidence(view, p4, fi, pi, ci)
    member, tail = ev[0], ev[1:]
    regions = member["h_region"]["regions"]
    a1 = None if off is None else any(r["head_span"][0] == off for r in regions)
    other = [r for r in regions if off is None or r["head_span"][0] != off]
    after = 0 if off is None else off
    pron = [[m.group(1), m.start()] for m in aq._PRONOUN_RE.finditer(text)
            if m.start() >= after]
    p4c = [dict(c, address=e["address"]) for e in ev for c in e["p4"]]
    n614 = sum(1 for c in p4c if (c["cr"] or "").startswith("CR 614"))
    return {
        "address": member["address"], "class": key,
        "would_verb": None if off is None else {"word": verb, "offset": off},
        "a1": a1,
        "a2": {"count": len(other), "heads": [[r["head"], r["head_span"][0]]
                                              for r in other]},
        "a2_tail": [{"address": e["address"],
                     "count": len(e["h_region"]["regions"]),
                     "heads": [[r["head"], r["head_span"][0]]
                               for r in e["h_region"]["regions"]]} for e in tail],
        "a3": {"candidates": [{"address": c["address"], "kind": c["kind"],
                               "arm": c["arm"], "cr": c["cr"]} for c in p4c],
               "count_614_anchored": n614},
        "a5": pron,
        "a5_tail": [{"address": e["address"],
                     "matches": [[m.group(1), m.start()] for m in
                                 aq._PRONOUN_RE.finditer(e["clause_text"])]}
                    for e in tail],
        "supports_A1": a1, "supports_A2": len(other) >= 1,
        "supports_A3": n614 >= 1, "supports_A5": bool(pron),
        "evidence": ev,
    }


def check_recall(seam: str, members: set, controls) -> dict:
    """Every recall control is a member of its seam, or HALT."""
    out = {}
    for oid in controls:
        hit = sorted((a for a in members if a.split(":")[0] == oid), key=_sort_key)
        if not hit:
            fc.halt(f"{seam}: recall control {oid} is not a member of the population")
        out[oid] = hit
    return dict(sorted(out.items()))


def resolve_723_2(names: list, cards: dict) -> dict:
    out = {}
    for n in names:
        hit = sorted(o for o, c in cards.items() if c["name"] == n)
        if len(hit) != 1:
            fc.halt(f"CR 723.2 names {n!r}, which matches {len(hit)} corpus card(s) "
                    f"by exact name; exactly one is required")
        out[n] = hit[0]
    return out


def fixture_check(cards: dict) -> dict:
    """The recall controls the command cites from FIXTURES.json are its members.
    A member FIXTURES.json leaves UNRESOLVED (h_region.load_fixtures: no exact
    name match) counts only through its one recorded prefix match, and is
    reported as supplied by the command's oracle_id, not by the fixture."""
    out = {}
    for f in h.load_fixtures(cards):
        if f["role"] not in (R2A_FIXTURE_ROLE, R2C_FIXTURE_ROLE):
            continue
        got = []
        for m in f["members"]:
            if m["oracle_id"]:
                got.append({"oracle_id": m["oracle_id"], "via": "fixture"})
            elif len(m.get("prefix_matches_not_used") or []) == 1:
                got.append({"oracle_id": m["prefix_matches_not_used"][0],
                            "via": "command oracle_id; FIXTURES.json member "
                                   "unresolved, its one recorded prefix match",
                            "unresolved": m["unresolved"]})
            else:
                fc.halt(f"FIXTURES.json role {f['role']}: an unresolved member has "
                        f"no single prefix match")
        out[f["role"]] = sorted(got, key=lambda x: x["oracle_id"])
    ids = lambda role: sorted(x["oracle_id"] for x in out.get(role, []))
    if ids(R2A_FIXTURE_ROLE) != sorted(R2A_CONTROLS):
        fc.halt(f"FIXTURES.json role {R2A_FIXTURE_ROLE} is {ids(R2A_FIXTURE_ROLE)}, "
                f"not the four R2-A recall controls")
    if R2C_CONTROLS[0] not in ids(R2C_FIXTURE_ROLE):
        fc.halt(f"FIXTURES.json role {R2C_FIXTURE_ROLE} does not hold {R2C_CONTROLS[0]}")
    return out


def corpus_names(cards: dict) -> list:
    return sorted({c["name"] for c in cards.values()}
                  | {f["name"] for c in cards.values()
                     for f in c.get("card_faces") or [] if f.get("name")})


# ---------------------------------------------------------- negative controls

def _rig_card_keyed(name: str, oid: str) -> list:
    """Each RULES entry with a card name or an oracle_id put in each key."""
    return [dict(r, **{k: f"{r[k]} {key}"}) for r in RULES
            for k in sorted(h._RULE_KEYS) for key in (name, oid)]


def _drop_rule(txt: str, rule: str) -> str:
    lines = [l for l in txt.splitlines()
             if not re.match(rf"(?:\*\*)?{re.escape(rule)}\.?(?:\*\*)? ", l)]
    return "\n".join(lines)


def negative_controls(cards: dict, names: list, r2a_members: set,
                      sample_view: dict) -> list:
    txt = cr.text()
    oid = R2A_CONTROLS[0]
    rig_name = cards[oid]["name"]
    lines = aq._card_lines(sample_view["card"])
    bad_lines = [lines[0] + " x"] + lines[1:]
    kicked = "If this spell was kicked, it deals 4 damage instead."
    cases = [
        ("a rigged identity hash halts",
         lambda: h._halts(lambda: h.verify_identities(
             dict(h.I1, **{h.C02_REL: "0" * 64})))),
        ("a rigged recall control removed from a population halts",
         lambda: h._halts(lambda: check_recall(
             "R2-A", {a for a in r2a_members if not a.startswith(oid)}, R2A_CONTROLS))
         and not h._halts(lambda: check_recall("R2-A", r2a_members, R2A_CONTROLS))),
        ("a rigged card-keyed RULES entry (a card name or oracle_id in id, kind, cr "
         "or pattern) halts",
         lambda: all(h._halts(lambda v=v: h.assert_not_card_keyed(
             (v,) + RULES, [rig_name] + names)) for v in _rig_card_keyed(rig_name, oid))
         and h._halts(lambda: h.assert_not_card_keyed(
             RULES + (dict(RULES[0], oracle_id=oid),), names))),
        ("a rigged clause 'gain control of target creature' is a contrast, not an "
         "R2-B member",
         lambda: r2b_classify("Gain control of target creature.") == "contrast"),
        ("a rigged clause 'you control enchanted creature' is a contrast, not an R2-B "
         "member",
         lambda: r2b_classify("You control enchanted creature.") == "contrast"),
        ("a rigged clause 'gain control of them' is a pronoun candidate, not an R2-B "
         "member",
         lambda: r2b_classify("Gain control of them.") == "pronoun"
         and r2b_classify("Then you control target opponent until your next "
                          "upkeep.") == "member"),
        ("a rigged clause 'for each land you control, target player draws a card' is "
         "not an R2-B member (punctuation breaks adjacency)",
         lambda: r2b_classify("For each land you control, target player draws a "
                              "card.") == "none"),
        ("a rigged clause 'target creature gains \"{T}: Draw a card.\"' and one "
         "'target creature gains flying' are contrasts, not R2-C members",
         lambda: r2c_classify('Target creature gains "{T}: Draw a card."') == "contrast"
         and r2c_classify("Target creature gains flying.") == "contrast"
         and r2c_classify("Each token you control has all activated abilities of "
                          "each Wall you own.") == "member"),
        ("a rigged clause without 'instead' is not an R2-A member; 'If you would draw "
         "a card, exile it instead' is in class 'draw'; 'If this spell was kicked, it "
         "deals 4 damage instead' is in class 'no-would:if'",
         lambda: not r2a_member("If you would draw a card, exile it.")
         and r2a_class("If you would draw a card, exile it instead.") == "draw"
         and r2a_would("If you would draw a card, exile it instead.")[1:] == ("draw", 13)
         and r2a_class(kicked) == "no-would:if" and r2a_would(kicked)[1:] == (None, None)
         and r2a_class("If a token would be put into your library, mill two cards "
                       "instead.") == "be put"),
        ("a rigged CR text missing 614.1a, 723.1, 723.2 or 613.1f STOPs",
         lambda: all(h._halts(lambda r=r: cr_read_cited(_drop_rule(txt, r)))
                     for r in ("614.1a", "723.1", "723.2", "613.1f"))
         and h._halts(lambda: cr_instead_word(_drop_rule(txt, "614.1a")))
         and h._halts(lambda: cr_723_2_names(_drop_rule(txt, "723.2")))
         and not h._halts(lambda: cr_read_cited(txt))),
        ("a rigged P4 line whose text differs from its chain paragraph halts",
         lambda: h._halts(lambda: p4_paragraphs(bad_lines, sample_view["paragraphs"],
                                                "rigged"))
         and h._halts(lambda: p4_paragraphs(lines[:-1] if len(lines) > 1 else lines
                                            + ["x"], sample_view["paragraphs"], "rigged"))
         and not h._halts(lambda: p4_paragraphs(lines, sample_view["paragraphs"],
                                                "rigged"))),
        ("a rigged output containing the absolute repository root fails "
         "--check-determinism",
         lambda: bool(h.portability_violations(
             b'{"p": "' + str(ROOT).encode() + b'"}'))
         and not h.portability_violations(b'{"p": "experiments/out"}')),
    ]
    out = []
    for name, check in cases:
        if not check():
            fc.halt(f"negative control failed: {name}")
        out.append(name)
    return out


# ------------------------------------------------------------------- build

def _count(it) -> dict:
    out = {}
    for x in it:
        out[x] = out.get(x, 0) + 1
    return dict(sorted(out.items()))


def r2a_summary(records: list, read: set) -> dict:
    def tally(k):
        return {str(v).lower(): n for v, n in sorted(
            _count(r[k] for r in records).items(), key=lambda x: str(x[0]))}
    rd = [r for r in records if r["address"] in read]
    return {"members": len(records),
            "supports_A1": tally("supports_A1"), "supports_A2": tally("supports_A2"),
            "supports_A3": tally("supports_A3"), "supports_A5": tally("supports_A5"),
            "read_members": len(rd),
            "read_with_tail_regions": sum(1 for r in rd
                                          if any(t["count"] for t in r["a2_tail"])),
            "read_with_tail_pronoun_matches": sum(1 for r in rd if any(
                t["matches"] for t in r["a5_tail"]))}


def build() -> dict:
    identities = h.verify_identities(h.I1)
    blob = h.verify_interface()
    txt = cr.text()
    cited = cr_read_cited(txt)
    instead = cr_instead_word(txt)
    names_723 = cr_723_2_names(txt)
    cards, _, _ = fc.load_corpus_gated()
    names = corpus_names(cards)
    rule_ids = h.assert_not_card_keyed(RULES, names)
    fixtures = fixture_check(cards)
    resolved_723 = resolve_723_2(names_723, cards)

    views, hits = {}, {"R2-A": [], "R2-B": {}, "R2-C": {}}
    for oid in sorted(cards):
        view = None
        for fi, pi, ci, seg in h.chain_clauses(cards[oid]):
            a = addr(oid, fi, pi, ci)
            b, c = r2b_classify(seg), r2c_classify(seg)
            if r2a_member(seg):
                hits["R2-A"].append((oid, fi, pi, ci, seg))
            if b != "none":
                hits["R2-B"].setdefault(b, []).append((oid, fi, pi, ci, seg))
            if c != "none":
                hits["R2-C"].setdefault(c, []).append((oid, fi, pi, ci, seg))
            if r2a_member(seg) or b in ("member", "pronoun") or c == "member":
                views[oid] = view = view or card_view(oid, cards[oid])

    p4 = {oid: p4_by_clause(v) for oid, v in sorted(views.items())}
    key = lambda t: (t[0], t[1], t[2], t[3])

    # R2-A
    a_recs = [r2a_record(views[o], p4[o], fi, pi, ci, s)
              for o, fi, pi, ci, s in sorted(hits["R2-A"], key=key)]
    a_ids = {r["address"] for r in a_recs}
    classes = {}
    for r in a_recs:
        classes.setdefault(r["class"], []).append(r["address"])
    class_out, read = {}, set()
    for k, ids in sorted(classes.items()):
        pos = read_positions(len(ids))
        read |= {ids[i] for i in pos}
        class_out[k] = {"count": len(ids), "members": ids, "read_positions": pos,
                        "read": [ids[i] for i in pos],
                        "summary": r2a_summary([r for r in a_recs if r["class"] == k],
                                               {ids[i] for i in pos})}
    anchors = sorted({a for _, _, a in aq._CONDITION_MARKERS}
                     | {f"CR {d['rule']}" for d in aq.CR607_PHRASES.values()}
                     | {"CR 607.1"})

    def listing(rows, matcher):
        return [{"address": addr(o, fi, pi, ci), "clause_text": s,
                 "matches": matcher(s)} for o, fi, pi, ci, s in sorted(rows, key=key)]

    def evidence(rows):
        return [{"address": addr(o, fi, pi, ci),
                 "evidence": paragraph_evidence(views[o], p4[o], fi, pi, ci)}
                for o, fi, pi, ci, _ in sorted(rows, key=key)]

    def ids_of(rows):
        return [addr(o, fi, pi, ci) for o, fi, pi, ci, _ in sorted(rows, key=key)]

    b_rows, c_rows = hits["R2-B"], hits["R2-C"]
    b_ids, c_ids = set(ids_of(b_rows.get("member", []))), set(ids_of(c_rows.get("member", [])))
    b_controls = tuple(R2B_CONTROLS) + tuple(v for v in resolved_723.values()
                                             if v not in R2B_CONTROLS)
    recall = {"R2-A": check_recall("R2-A", a_ids, R2A_CONTROLS),
              "R2-B": check_recall("R2-B", b_ids, b_controls),
              "R2-C": check_recall("R2-C", c_ids, R2C_CONTROLS)}
    neg = negative_controls(cards, names, a_ids, views[R2A_CONTROLS[0]])

    inputs = {rel: h._sha(rel) for rel in INPUTS}
    return {
        "schema": "oracle-compiler-a01-seams/0",
        "measurement_only": "this output decides no truth item; it records what "
                            "the existing code derives over each seam population",
        "interface": {"version": h.INTERFACE_VERSION, "blob": blob,
                      "i1_identities": identities},
        "inputs": inputs,
        "script": {"path": SCRIPT, "sha256": h._sha(SCRIPT)},
        "chain": ["foundry_locality.units", "foundry_shape_extractor.strip_reminder",
                  "foundry_shape_extractor.sentence_spans"],
        "chain_via": "h_region.chain_clauses",
        "cr": {"read_through": "experiments/foundry_cr.py",
               "cited": {k: list(v) for k, v in CITED.items()},
               "rules": cited, "r2a_member_word_cr614_1a": instead,
               "cr723_2_names": names_723, "cr723_2_resolved": resolved_723},
        "rules": list(RULES), "rules_checked_not_card_keyed": rule_ids,
        "rules_checked_over_names": len(names), "precedence": PRECEDENCE,
        "fixtures_checked": fixtures,
        "p4": {"mapping": "P4 line k (foundry_aq4_probes._card_lines order) is the "
                          "k-th foundry_locality.units paragraph holding a chain clause "
                          "(a wholly-reminder paragraph prints no P4 line); each line "
                          "equals its paragraph's chain clauses joined by one space and "
                          "its P4 sentence ordinal is the chain clause ordinal; checked "
                          "on every card holding a member or pronoun candidate",
               "cards_checked": len(views),
               "frozen_arm_anchors": anchors,
               "frozen_arm_anchors_in_cr614": [a for a in anchors
                                               if a.startswith("CR 614")]},
        "negative_controls": neg,
        "seams": {
            "R2-A": {
                "cr": "CR 614.1a (with 614.5 nesting, 616.1 ordering cited)",
                "scope": "CR 614.1a clauses holding the quoted word only; the "
                         "614.1b-e forms without it (skip, 'enters with', 'as ... "
                         "enters', ...) and CR 616 ordering are NOT audited; any "
                         "overturn of M03 covers only this scope",
                "a3_note": "A3 is EXPRESSED only by a carrier whose CR anchor is in "
                           "614; no frozen P4 arm has one (frozen_arm_anchors), so "
                           "count_614_anchored is 0 by definition, not by measurement",
                "count_614_anchored_total": sum(r["a3"]["count_614_anchored"]
                                                for r in a_recs),
                "population_count": len(a_recs),
                "population": [r["address"] for r in a_recs],
                "no_would_count": sum(1 for r in a_recs
                                      if r["class"].startswith("no-would:")),
                "classes": class_out,
                "tail_note": "tail evidence counts only for members that were read",
                "recall_controls": recall["R2-A"],
                "members": a_recs,
            },
            "R2-B": {
                "cr": "CR 723.1-723.8; contrast CR 108.4 / 613.1b",
                "player_terms": list(PLAYER_TERMS), "pronoun_forms": list(PRONOUN_FORMS),
                "population_count": len(b_ids),
                "population": ids_of(b_rows.get("member", [])),
                "pronoun_candidates": {"count": len(b_rows.get("pronoun", [])),
                                       "list": listing(b_rows.get("pronoun", []),
                                                       r2b_matches)},
                "contrast": {"count": len(b_rows.get("contrast", [])),
                             "list": listing(b_rows.get("contrast", []), r2b_matches)},
                "recall_controls": recall["R2-B"],
                "members": [dict(m, matches=r2b_matches(m["evidence"][0]["clause_text"]))
                            for m in evidence(b_rows.get("member", []))],
                "pronoun_records": evidence(b_rows.get("pronoun", [])),
            },
            "R2-C": {
                "cr": "CR 613.1f; CR 607.2a for 'exiled with [this object]'",
                "population_count": len(c_ids),
                "population": ids_of(c_rows.get("member", [])),
                "contrast": {"count": len(c_rows.get("contrast", [])),
                             "list": listing(c_rows.get("contrast", []), r2c_matches)},
                "recall_controls": recall["R2-C"],
                "members": [dict(m, matches=r2c_matches(m["evidence"][0]["clause_text"]))
                            for m in evidence(c_rows.get("member", []))],
            },
        },
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
             if not (ROOT / rel).exists() or h._sha(rel) != want]
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
    bad = h.portability_violations(runs[0])
    if bad:
        print(f"FAIL: output carries the {', '.join(bad)}", file=sys.stderr)
        return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(runs[0])
    print(f"{OUT_REL}: x2 byte-identical, portable, sha256 "
          f"{hashlib.sha256(runs[0]).hexdigest()} ({len(runs[0])} bytes)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--emit", action="store_true", help="write the report to stdout only")
    g.add_argument("--check-determinism", action="store_true")
    g.add_argument("--verify", action="store_true")
    a = ap.parse_args(argv)
    if a.verify:
        return verify()
    if a.check_determinism:
        return check_determinism()
    data = render(build())
    bad = h.portability_violations(data)
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
