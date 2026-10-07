#!/usr/bin/env python3
"""C03 — H-REGION candidate derivation and measurement (interface/3, V1 §5 M1).

PINNED TO oracle-compiler-interface/5 (oracle_compiler/INTERFACES.md blob
282c295c03f2a4b43e723d01710baaf479aa716c, landing 0390385, record 6031691630),
whose §I3a is interface/3's (ratified by Captain decisions 5925134485 and
5925371124; landing record 5925482946) with the R4 errata (a)-(c) applied.

Derives deterministic H-REGION CANDIDATES over the C03 population (interface/3
I2, unchanged) and the frozen F0 fixtures, and measures them. It decides no kill: the
seven I3 tests read this output in `h_region_kill.py`. Read-only over the
corpus; writes one ignored JSON report.

INPUTS (a). The four I1 identities (unchanged from interface/1) are verified
first; a differing identity HALTS. The I2 population is re-derived with the
frozen functions (`foundry_qualifier_census.population`,
`foundry_aq4_probes.effect_heads`)
and every I2 figure is reconciled against both the interface's literals and the
pinned C02 output before any other work; a mismatch HALTS. Fixture members
come from `oracle_compiler/FIXTURES.json` only -- none added, dropped or
swapped. `f0_select.py` is reused for its pins, hash and census key.

REGIONS (b). One region per candidate operation head of the frozen LEGACY
detector (the population's own detector). A head occupies a predicate slot
only at a CR 608.2c instruction boundary -- the frozen `_BOUNDARY_WORD` rule;
head positions are recovered with the frozen `_HEAD_RE`/`_BOUNDARY_WORD` and
then REQUIRED to equal `effect_heads` exactly, so the positions cannot drift
from the frozen detector. A region runs from its head to the boundary
connector printed before the next head (CR 608.2c: instructions in the order
written), or to the end of the clause scope. Every region is owned by the
four-coordinate occurrence (oracle_id, face, paragraph, clause) produced by
the ratified chain (AQ4 register #29): `foundry_locality.units` (CR 113.2c)
-> `foundry_shape_extractor.strip_reminder` (CR 207.2a) -> `sentence_spans`
(quoted created abilities blanked; owns the clause ordinal). A census clause
is placed by the ratified resolution law (`foundry_locality.resolve`) and must
sit inside exactly one chain clause; otherwise it HALTS (a population clause
whose address cannot be resolved is a STOP). Spans are offsets into that
frozen clause text.

INTERFACE/2 §I3a. R2 `head-not-payment-cast`: a legacy head `cast` whose
printed tokens are immediately preceded by `spent to` starts no region (the
frozen detector is not edited; every dropped head is reported per clause), and
the region cut rule then runs over the heads that do start regions. R1
`attach-ability-prefix` is narrowed to its three shapes, each starting at the
start of the chain clause (the `clause-scope` rule): a `cost-colon` span, a
`condition-trigger` span opening When/Whenever/At, and a `condition-marker`
span beginning `if` immediately after such a trigger condition's comma. Such a
span is ONE attachment, to the ability. Any other prefix span keeps its
interface/1 outcome. R3 `group-back-reference` is a table entry here only; it
is evaluated by `h_region_kill.py`. Every span whose attachment differs from
interface/1 records the interface/1 attachment beside it, with the rule.

INTERFACE/3 §I3a R4 `ability-label`. A label is located only at the start of a
chain clause of ordinal 0 (a paragraph is a line), after a CR 700.2 bullet if
the line has one, up to the first ` — ` with text after it, holding none of
`— : ; . • "`. It is classified, first match deciding, from the pinned CR read
at run time through `foundry_cr` (the 207.2c ability words, the 701/702
keyword titles, the quoted CR label forms, the rule 107 symbol inventory --
each parse checked complete, or the derivation STOPs) and the card's own rules
text: ticket cost, ability word (both IGNORED), rules-meaningful (KEPT), or
flavor label (IGNORED). An IGNORED label moves the scope start past its ` — `:
a legacy head inside the label starts no region (reported per clause, as R2's
are) and R1's scope start, with the cost-colon and condition-trigger marks R1
reads, is read from there. A KEPT label keeps its interface/2 outcome.

THE R4-OFF VIEW is the interface/2 derivation exactly (no label located). Every
interface/1-versus-interface/2 record (the `interface1` annotations, R1-R3
reach) is computed on it; the R4-on view is the record, and wherever R4 alone
changes it the interface/2 value is kept beside it (`interface2`, rule R4).
R4 IS CONFINED: a clause with no IGNORED label whose R4-on record differs from
its R4-off record HALTS.

ROLE MARKS are the ATTACH-3 categories only -- cost, condition, duration,
destination -- as MEASUREMENT LABELS, each from printed tokens and a CR rule
parsed at run time (or a declared, sized English list under the CR 207.2d
precedent). They mint no vocabulary.

The corrected detector (`semantic_action_heads`) is reported per clause beside
the legacy one and is never substituted.

    python3 experiments/oracle_ingest/h_region.py                      # write
    python3 experiments/oracle_ingest/h_region.py --emit               # stdout only
    python3 experiments/oracle_ingest/h_region.py --check-determinism  # x2 + write
    python3 experiments/oracle_ingest/h_region.py --verify             # stale?
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
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))

import f0_select as f0                       # noqa: E402  (also sets sys.path)
import foundry_common as fc                  # noqa: E402
import foundry_cr as cr                      # noqa: E402
import foundry_qualifier_census as fqc       # noqa: E402
import foundry_shape_extractor as fx         # noqa: E402
import foundry_locality as fl                # noqa: E402
import foundry_aq4_probes as aq              # noqa: E402

SCRIPT = "experiments/oracle_ingest/h_region.py"
OUT_REL = "experiments/out/oracle_ingest/c03/regions.json"
OUT = ROOT / OUT_REL

# I1 (unchanged from interface/1) -- f0_select pins three; the accepted C02
# output is the fourth.
C02_REL = "experiments/out/oracle_ingest/c02/all-run1.json"
I1 = dict(f0.PINNED)
I1[C02_REL] = "74e3559d785dc3ac47d14823ac1fec96dd446ae446d82a3ee45b03ef3f818dfd"

# oracle-compiler-interface/5, by git blob id (the wave's STOP condition).
INTERFACE_VERSION = "oracle-compiler-interface/5"
INTERFACES_REL = "oracle_compiler/INTERFACES.md"
INTERFACES_BLOB = "282c295c03f2a4b43e723d01710baaf479aa716c"
FIXTURES_REL = "oracle_compiler/FIXTURES.json"
CONTRACT_REL = "benchmarks/aq4/docs/AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md"

# Every input this output depends on, hashed into it; `--verify` recomputes them.
INPUTS = sorted(set(I1) | {
    FIXTURES_REL, INTERFACES_REL, CONTRACT_REL,
    "experiments/oracle_ingest/f0_select.py",
    "tests/guards/gate2/foundry_qualifier_census.py",
    "src/mtj_foundry/mtg/shapes/locality.py",
    "src/mtj_foundry/mtg/shapes/delivery.py",
})

# I2 (unchanged from interface/1) -- the accepted C02 figures, every one of them.
I2 = dict(f0.C02, families={"exile": 60, "destroy": 6, "bounce": 0},
          examples=25)
I2.pop("p3_multi", None)
I2.pop("p3_qual", None)

# AQ4 register #27, CITED and not re-measured (I2).
COST_PRECEDENT = {
    "source": f"{CONTRACT_REL} register #27 (RATIFIED -- CAPTAIN 2026-08-17)",
    "surface": "frozen 782-occurrence open surface",
    "cost_regions": 113,
    "by_cr_arm": {"CR 113.3b/602.1a": 84, "CR 606.2": 27, "CR 702.6b": 2},
    "crossing_clause_boundary": 0,
    "crossing_paragraph_boundary": 0,
    "crossing_face_boundary": 0,
    "ambiguous": 0,
    "max_span_characters": 58,
    "status": "cited, not re-measured; importing AQ4 benchmark code to re-measure "
              "it needs its own authorization",
}


class Refused(Exception):
    """A derivation the rules refuse (the caller decides whether that halts)."""


def _sha(rel: str) -> str:
    return f0._sha(ROOT / rel)


def _blob(rel: str) -> str:
    data = (ROOT / rel).read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


# ------------------------------------------------------------------ (a) inputs

def verify_identities(pins: dict) -> dict:
    for rel, want in sorted(pins.items()):
        got = _sha(rel)
        if got != want:
            fc.halt(f"pinned input {rel} is {got}, {INTERFACE_VERSION} I1 pins {want}")
    return dict(sorted(pins.items()))


def verify_interface() -> str:
    got = _blob(INTERFACES_REL)
    if got != INTERFACES_BLOB:
        fc.halt(f"{INTERFACES_REL} is blob {got}, not {INTERFACE_VERSION} "
                f"({INTERFACES_BLOB})")
    return got


def reconcile(rows: list, c02: dict, want: dict = None) -> dict:
    """Every I2 figure, re-derived, against the interface's literals AND the
    pinned C02 output. Any mismatch halts."""
    want = I2 if want is None else want
    p2 = c02["p2"]
    heads = [(r, aq.effect_heads(r["clause"])) for r in rows]
    dist, fam = {}, {s: 0 for s in sorted(p2["by_action_family"])}
    multi, examples = [], []
    for r, h in heads:
        dist[min(len(h), 5)] = dist.get(min(len(h), 5), 0) + 1
        if len(h) > 1:
            multi.append((r, h))
            fam[r["stem"]] = fam.get(r["stem"], 0) + 1
            if len(examples) < 25:          # the p2 examples rule, verbatim
                examples.append({"name": r["name"], "stem": r["stem"],
                                 "heads": h, "clause": r["clause"][:110]})
    forms = {}
    for _, h in multi:
        forms[" + ".join(h[:4])] = forms.get(" + ".join(h[:4]), 0) + 1
    members = sum(1 for e in p2["examples"]
                  if any((r["name"], r["stem"], h, r["clause"][:110])
                         == (e["name"], e["stem"], e["heads"], e["clause"])
                         for r, h in multi))
    measured = {"rows": len(rows), "multi": len(multi), "heads": dist,
                "exile_return": forms.get("exile + return", 0),
                "families": fam, "examples": members}
    pinned = {"rows": p2["denominator"],
              "multi": p2["clauses_with_multiple_effect_heads"],
              "heads": {int(k): v for k, v in p2["head_count_distribution"].items()},
              "exile_return": next((f["clauses"] for f in p2["top_structural_forms"]
                                    if f["heads"] == "exile + return"), None),
              "families": {s: d["multi_effect"]
                           for s, d in p2["by_action_family"].items()},
              "examples": len(p2["examples"])}
    for label, ref in ((f"{INTERFACE_VERSION} I2", want), ("accepted C02 output", pinned)):
        if measured != ref:
            fc.halt(f"re-derived population does not reconcile with {label}: "
                    f"{measured} != {ref}")
    if examples != p2["examples"]:
        fc.halt("the re-derived first 25 multi-head clauses are not the accepted "
                "C02 examples")
    out = dict(measured, heads={str(k): v for k, v in sorted(dist.items())})
    return out


def load_fixtures(cards: dict) -> list:
    """Every FIXTURES.json role and its members, by oracle_id. A name-only
    member is looked up by exact card name, then exact face name; anything but
    exactly one card halts. No member is added, dropped or swapped."""
    doc = json.loads((ROOT / FIXTURES_REL).read_text(encoding="utf-8"))
    out = []
    for fam in doc["fixture_family"]:
        sel = fam.get("selection") or {}
        names = fam.get("members") or ([fam["member"]] if fam.get("member") else [])
        oids = sel.get("oracle_ids") or ([sel["oracle_id"]] if sel.get("oracle_id")
                                          else [])
        members = []
        for i, name in enumerate(names):
            if i < len(oids):
                oid = oids[i]
                if oid not in cards or cards[oid]["name"] != name:
                    fc.halt(f"fixture {fam['id']}: {name!r} is not {oid} in the "
                            f"pinned corpus")
            else:
                hit = sorted(o for o, c in cards.items() if c["name"] == name)
                if not hit:
                    hit = sorted(o for o, c in cards.items()
                                 if any(f.get("name") == name
                                        for f in c.get("card_faces") or []))
                if len(hit) != 1:
                    # Never a guess and never a swap: the member stays in the
                    # fixture, UNRESOLVED (FIXTURES.json gold_law:
                    # unresolved_is_valid), with the prefix matches shown and
                    # NOT used.
                    members.append({
                        "oracle_id": None, "census_key": None,
                        "name_as_recorded": name,
                        "unresolved": f"matches {len(hit)} cards by exact card or "
                                      f"face name; exactly one is required",
                        "prefix_matches_not_used": sorted(
                            o for o, c in cards.items()
                            if c["name"].lower().startswith(name.lower()))})
                    continue
                oid = hit[0]
            members.append({"oracle_id": oid,
                            "census_key": sel.get("census_key") if len(names) == 1
                            else None})
        out.append({"role": fam["id"], "member_status": fam["member_status"],
                    "members": members})
    return out


# ------------------------------------------------ the chain (register #29)

def chain_clauses(card: dict) -> list:
    """[(face, paragraph, clause, clause_text)] -- the ratified chain, canonical
    detector view, exactly as the open surface is produced."""
    out = []
    for (fi, pi), _raw, canon in fl.units(card):
        para = fx.strip_reminder(canon)
        for ci, seg in enumerate(fx.sentence_spans(para)):
            out.append((fi, pi, ci, seg))
    return out


def card_rules_text(card: dict) -> str:
    """The card's own rules text in the chain's canonical view, one paragraph
    (line) per unit -- what R4's anchor-word class reads."""
    return "\n".join(fx.strip_reminder(canon) for _, _raw, canon in fl.units(card))


def locate(segs: list, text: str) -> tuple:
    """The one chain clause holding `text`, and its offset. A text found in no
    single chain clause crosses a clause boundary and is REFUSED; a text found
    in several is ambiguous and is REFUSED."""
    hits = [(s, seg.find(text)) for s in segs for seg in [s[3]] if text in seg]
    if not hits:
        raise Refused("crosses a clause boundary or is absent from every chain "
                      "clause of its paragraph")
    if len(hits) > 1 or hits[0][0][3].count(text) > 1:
        raise Refused(f"appears {len(hits)} time(s) across chain clauses; no "
                      f"single owner")
    return hits[0]


def resolve_census(card: dict, clause: str) -> tuple:
    """Census clause -> (face, paragraph, clause, text, offset) through the
    ratified locality law, then the chain's clause ordinal."""
    res = fl.resolve(card, clause)
    if res["status"] != fl.OWNER:
        raise Refused(f"locality resolution is {res['status']}: {res['reason']}")
    fi, pi = res["owner"]
    segs = [s for s in chain_clauses(card) if (s[0], s[1]) == (fi, pi)]
    seg, off = locate(segs, clause)
    return seg[0], seg[1], seg[2], seg[3], off


# ------------------------------------------------------ derivation rules

def _cr_line(rule: str) -> str:
    m = re.search(rf"^(?:\*\*)?{re.escape(rule)}\.?(?:\*\*)?\s+(.*)$", cr.text(), re.M)
    if not m:
        fc.halt(f"CR {rule} not found in the pinned CR")
    return m.group(1)


def _cr_quotes(rule: str) -> list:
    return re.findall(r"“([^”]+)”", _cr_line(rule))


def _zones() -> list:
    m = re.search(r"zones:\s*([^.]+)\.", _cr_line("400.1"))
    zones = [z.strip() for z in re.split(r",\s*(?:and\s+)?|\s+and\s+",
                                          m.group(1) if m else "") if z.strip()]
    if not {"library", "hand", "battlefield", "graveyard", "exile"} <= set(zones):
        fc.halt(f"CR 400.1 zone parse lost a zone; got {zones}")
    return zones


def _trigger_words() -> list:
    m = re.search(r"\[([A-Za-z/]+)\]", _cr_line("603.1"))
    words = m.group(1).split("/") if m else []
    if set(words) != {"When", "Whenever", "At"}:
        fc.halt(f"CR 603.1 trigger-word parse moved; got {words}")
    return words


def _durations() -> list:
    a = [q for q in _cr_quotes("611.2a") if q.startswith("until")]
    b = [q.replace(". . . .", "").strip() for q in _cr_quotes("611.2b")
         if q.startswith("for as long as")]
    if not a or not b:
        fc.halt(f"CR 611.2a/b duration parse lost a form; got {a} {b}")
    return [a[0].split()[0], b[0]]          # the leading form word; the full prefix


# Declared (H2, CR 207.2d precedent): the CR enumerates no English prepositions.
DESTINATION_PREPOSITIONS = ("on the bottom of", "on top of", "onto", "into", "to")

_ZONE_ALT = "|".join(re.escape(z) for z in sorted(_zones(), key=lambda z: (-len(z), z)))
_TRIGGER_RE = re.compile(r"(?:" + "|".join(_trigger_words()) + r")\b")
_UNTIL, _FOR_AS_LONG_AS = _durations()
_DURATION_RE = re.compile(rf"\b(?:{re.escape(_FOR_AS_LONG_AS)}|{re.escape(_UNTIL)})\b",
                          re.I)
_DESTINATION_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(p) for p in DESTINATION_PREPOSITIONS) + r")"
    r"(?:\s+(?!from\b)[\w'’]+){0,3}?\s+(?:" + _ZONE_ALT + r")s?\b", re.I)
_COLON_RE = re.compile(r":")

# interface/2 §I3a, stated there and nowhere else.
_R1_INTERVENING = re.compile(r"if\b")                    # R1 condition-marker shape
_R2_PRECEDED = re.compile(r"\bspent to $")               # R2: `spent to` + head `cast`
_R3_COORDINATOR = re.compile(r", and|,|and")             # R3 gap coordinators
R3_PLURAL_MARKERS = ("they", "them", "those cards", "those creatures",
                     "those permanents", "those tokens")
if not set(R3_PLURAL_MARKERS) <= aq._PRONOUN_MARKERS:
    fc.halt(f"interface/2 R3 plural markers are not all frozen _PRONOUN_MARKERS: "
            f"{sorted(set(R3_PLURAL_MARKERS) - aq._PRONOUN_MARKERS)}")

# interface/3 §I3a R4, stated there and nowhere else.
R4_DASH = " — "                                          # U+2014, one space each side
R4_BULLET = "•"                                          # CR 700.2
R4_NOT_IN_LABEL = ("—", ":", ";", ".", "•", '"')
R4_OTHER_CHARS = " '’,!?-~"                              # beside letters and digits
R4_TICKET = "{TK}"                                       # CR 107.17
R4_SYMBOLS_REQUIRED = ("{TK}", "{W}", "{U}", "{B}", "{R}", "{G}", "{C}", "{X}",
                       "{S}", "{T}", "{Q}", "{E}")
R4_FORMS_REQUIRED = ("to solve", "solved", "visit", "forecast")
R4_FORM_VILLAINOUS = "villainous choice"
# interface/4 §I3a errata b: CR 702.159b gives "Prize —" rules meaning without
# quoting it as a form; read there at run time, its absence a STOP.
R4_FORM_PRIZE = ("702.159b", "Prize")
# The counts §I3a states were read from the CR; a different read is a STOP.
R4_CR_COUNTS = {"ability_words": 61, "keyword_titles": 264, "label_forms": 23}
_ROMAN = r"M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})"
_R4_CHAPTER = re.compile(rf"(?=[MDCLXVI])({_ROMAN})(?:, (?=[MDCLXVI]){_ROMAN})*")
_R4_NUMBER_ITEM = r"\d+(?: ?[-–] ?\d+)?"
_R4_NUMBER = re.compile(rf"{_R4_NUMBER_ITEM}(?:(?:, or |, | or ){_R4_NUMBER_ITEM})*")
_R4_SYMBOL = re.compile(r"\{[^{}]*\}")
_R4_PARAMETER = re.compile(r"(?:\d+|(?:\{[^{}\s]+\})+)")


class R4CR(dict):
    """What R4 reads from the pinned CR, and nothing else."""


def _apos(s: str) -> str:
    return s.replace("’", "'").casefold()


def r4_cr_read(txt: str = None) -> R4CR:
    """interface/3 §I3a R4: the CR reads that classify a label, each parse
    checked complete or the derivation STOPs (halts)."""
    txt = cr.text() if txt is None else txt
    lines = txt.splitlines()
    # -- CR 207.2c: the ability words.
    lead = "The ability words are "
    hits = [l for l in lines if l.startswith("207.2c ")]
    if len(hits) != 1 or txt.count(lead) != 1 or hits[0].count(lead) != 1:
        fc.halt(f"R4: the CR 207.2c ability-word sentence is not found exactly once "
                f"({len(hits)} rule line(s), {txt.count(lead)} sentence(s))")
    body = hits[0][hits[0].index(lead) + len(lead):]
    if not body.endswith(".") or "." in body[:-1]:
        fc.halt("R4: the CR 207.2c ability-word sentence does not end its rule")
    body = body[:-1]
    raw = body.split(", ")
    if len(raw) < 3 or not raw[-1].startswith("and "):
        fc.halt("R4: the CR 207.2c sentence is not of the form '<a>, <b>, ..., and <z>.'")
    items = [re.sub(r"^and ", "", w) for w in raw]
    if ", ".join(items[:-1]) + ", and " + items[-1] != body:
        fc.halt("R4: the CR 207.2c ability words do not re-join to their source text")
    bad = [w for w in items if not re.fullmatch(r"[a-z'’]+(?: [a-z'’]+)*(?: \d+)?", w)]
    if bad or len(set(items)) != len(items):
        fc.halt(f"R4: CR 207.2c items are not distinct lowercase phrases: {bad}")
    # -- CR 701 / 702: the keyword titles.
    heads, rules = {"701": {}, "702": {}}, {"701": set(), "702": set()}
    for l in lines:
        m = re.match(r"(70[12])\.(\d+)\.(?: (.*))?$", l)
        if m:
            if int(m.group(2)) in heads[m.group(1)]:
                fc.halt(f"R4: CR {m.group(1)}.{m.group(2)} has two headings")
            heads[m.group(1)][int(m.group(2))] = (m.group(3) or "").strip()
        m = re.match(r"(70[12])\.(\d+)[a-z]+ ", l)
        if m:
            rules[m.group(1)].add(int(m.group(2)))
    titles = {}                                  # casefolded title -> (title, rule)
    for sec in ("701", "702"):
        ns = sorted(heads[sec])
        if not ns or ns != list(range(1, ns[-1] + 1)):
            fc.halt(f"R4: the CR {sec} headings are not a complete 1..N sequence")
        if rules[sec] - set(ns):
            fc.halt(f"R4: CR {sec} rules without a heading: {sorted(rules[sec] - set(ns))}")
        for n in ns:
            title = heads[sec][n]
            if not title:
                fc.halt(f"R4: CR {sec}.{n} heading has no title")
            if title.endswith("."):
                # x.1 is the section's general rule (a sentence), not a keyword.
                if n != 1:
                    fc.halt(f"R4: CR {sec}.{n} heading is a sentence, not a title")
                continue
            m = re.fullmatch(r"(.+?) \(([^()]+)\)", title)
            for t in ((m.group(1), m.group(2)) if m else (title,)):
                titles.setdefault(_apos(t), (t, f"{sec}.{n}"))
    # -- CR 107: the symbol inventory.
    inv = sorted({s for l in lines if re.match(r"107\.\d", l)
                  for s in re.findall(r"\{[^{}\s]+\}", l)})
    missing = [s for s in R4_SYMBOLS_REQUIRED if s not in inv]
    if missing:
        fc.halt(f"R4: the CR 107 symbol inventory lacks {missing}")
    # -- every quoted label form the CR's numbered rules print: “<form> — [.
    # A form that is wholly one [placeholder] (`[Anchor word]`, CR 614.12c) is
    # counted, and is the anchor-word class: its placeholder is a word the
    # card's own text names, read there -- never a wildcard over every label.
    forms = {}
    for l in lines:
        rule = re.match(r"(\d{3}\.\d+[a-z]*)\.? ", l)
        if not rule:
            continue
        for m in re.finditer(r"“([^“”‘’]+?) ?— ?\[", l):
            forms.setdefault(_apos(m.group(1)), (m.group(1), []))[1].append(rule.group(1))
    lost = [f for f in R4_FORMS_REQUIRED if f not in forms]
    if lost or not any(R4_FORM_VILLAINOUS in f for f in forms):
        fc.halt(f"R4: the CR label forms lack {lost or [R4_FORM_VILLAINOUS]}")
    prize_rule, prize = R4_FORM_PRIZE
    prize_at = [l for l in lines if l.startswith(prize_rule + " ")]
    if len(prize_at) != 1 or f"“{prize}”" not in prize_at[0]:
        fc.halt(f"R4: CR {prize_rule} does not give '{prize}' rules meaning "
                f"(interface/4 §I3a errata b): a STOP to the Captain")
    forms.setdefault(_apos(prize), (prize, []))[1].append(prize_rule)
    form_rx, anchor_forms = [], []
    for key, (f, at) in sorted(forms.items()):
        if re.fullmatch(r"\[[^\]]*\]", f):
            anchor_forms.append((f, sorted(set(at))))
            continue
        rx = re.sub(r"\\\[[^\]]*?\\\]", ".+", re.escape(f))
        rx = re.sub(r"(?<![A-Za-z])N\d?(?![A-Za-z0-9])|(?<=\{r)N\d?", r"\\d+", rx)
        form_rx.append((re.compile(rx, re.I), f, sorted(set(at))))
    out = R4CR(ability_words=sorted(items), titles=titles,
               titles_702={k for k, (_, r) in titles.items() if r.startswith("702.")},
               symbols=inv, forms=form_rx, anchor_forms=anchor_forms)
    out["counts"] = {"ability_words": len(items), "keyword_titles": len(titles),
                     "label_forms": len(form_rx) + len(anchor_forms)}
    return out


def r4_cr_report(crr: R4CR) -> dict:
    """What regions.json records of the R4 CR read."""
    return {"counts": r4_check_counts(crr["counts"]),
            "counts_stated_by_interface": dict(R4_CR_COUNTS),
            "ability_words": list(crr["ability_words"]),
            "keyword_titles": sorted([t, "CR " + r] for t, r in crr["titles"].values()),
            "label_forms": sorted([f, at] for _, f, at in crr["forms"]),
            "label_forms_anchor_word": sorted([f, at] for f, at in crr["anchor_forms"]),
            "symbol_inventory_cr107": list(crr["symbols"]),
            "read_through": "experiments/foundry_cr.py",
            "completeness_checks": [
                "CR 207.2c ability-word sentence found exactly once, of the form "
                "'<a>, <b>, ..., and <z>.', re-joined exactly to its source, every "
                "item a distinct lowercase phrase (optionally with a number)",
                "CR 701 and 702 headings each a complete 1..N sequence with a title "
                "on every heading, and every 701.N / 702.N rule under its heading",
                "CR 107 symbol inventory holds " + " ".join(R4_SYMBOLS_REQUIRED),
                "CR label forms include " + ", ".join(R4_FORMS_REQUIRED)
                + " and a " + R4_FORM_VILLAINOUS + " form"]}


def r4_check_counts(counts: dict) -> dict:
    """§I3a: 61 ability words, 264 keyword titles, 23 CR label forms."""
    if counts != R4_CR_COUNTS:
        fc.halt(f"R4: the CR read gives {counts}, interface/4 §I3a states "
                f"{R4_CR_COUNTS}: a STOP to the Captain")
    return dict(counts)


_R4 = {}


def _r4cr() -> R4CR:
    if "cr" not in _R4:
        _R4["cr"] = r4_cr_read()
        r4_check_counts(_R4["cr"]["counts"])
    return _R4["cr"]


def r4_locate(text: str, ci: int = 0):
    """interface/3 §I3a R4 LOCATE: (label start, label end, scope start) or None.
    Only a chain clause of ordinal 0 opens a line (a paragraph)."""
    if ci != 0:
        return None
    a = len(text) - len(text.lstrip())
    if text.startswith(R4_BULLET, a):
        a += len(R4_BULLET)
        a += len(text[a:]) - len(text[a:].lstrip())
    d = text.find(R4_DASH, a)
    if d < 0:
        return None
    line_end = text.find("\n", d)
    after = text[d + len(R4_DASH):len(text) if line_end < 0 else line_end]
    label = text[a:d]
    if not after.strip() or not label.strip() or any(ch in label for ch in R4_NOT_IN_LABEL):
        return None                     # an end-of-line dash, or a forbidden character
    s = d + len(R4_DASH)
    s += len(text[s:]) - len(text[s:].lstrip())
    return a, d, s


def _own_names(card_name) -> list:
    if not card_name:
        return ["~"]
    return ["~"] + sorted({card_name, *card_name.split(" // ")}, key=lambda n: (-len(n), n))


def _anchor_named(label: str, card_text: str, card_name) -> bool:
    """CR 614.12c: the card's own rules text names the label elsewhere, outside
    every label and outside the card's own name."""
    if _apos(label) in {_apos(n) for n in _own_names(card_name)}:
        return False
    lines = []
    for line in card_text.split("\n"):
        loc = r4_locate(line, 0)
        lines.append(line if loc is None else line[:loc[0]] + "\0" + line[loc[1]:])
    rest = "\n".join(lines)
    for n in _own_names(card_name):
        rest = rest.replace(n, "\0")
    return bool(re.search(rf"(?<!\w){re.escape(label)}(?!\w)", rest))


def r4_classify(label: str, card_text: str, card_name=None, crr: R4CR = None) -> tuple:
    """interface/3 §I3a R4 CLASSIFY, in the stated order, the first match
    deciding: (class, CR citation, 'ignored' | 'kept')."""
    crr = _r4cr() if crr is None else crr
    key = _apos(label)
    if re.fullmatch(f"(?:{re.escape(R4_TICKET)})+", label):
        return "ticket cost", "CR 107.17a / 123.3c", "ignored"
    if key in {_apos(w) for w in crr["ability_words"]}:
        return "ability word", "CR 207.2c", "ignored"
    parts = key.split(", ")
    if all(p in crr["titles"] for p in parts):
        return "keyword", "CR " + " / ".join(crr["titles"][p][1] for p in parts), "kept"
    m = re.fullmatch(rf"(.+?) ({_R4_PARAMETER.pattern})", label)
    if m and _apos(m.group(1)) in crr["titles_702"]:
        return "keyword", "CR " + crr["titles"][_apos(m.group(1))][1], "kept"
    for rx, form, at in crr["forms"]:
        if rx.fullmatch(label.replace("’", "'")) or rx.fullmatch(label):
            return "CR label form", "CR " + " / ".join(at), "kept"
    if _R4_CHAPTER.fullmatch(label):
        return "chapter symbol", "CR 714.2a / 714.2c", "kept"
    if _R4_NUMBER.fullmatch(label):
        return "number", "CR 706", "kept"
    if _R4_SYMBOL.search(label) or any(not (ch.isalpha() or ch.isdigit()
                                            or ch in R4_OTHER_CHARS) for ch in label):
        return "symbol-bearing", "CR 107", "kept"
    if _anchor_named(label, card_text, card_name):
        return "anchor word", "CR 614.12c", "kept"
    return "flavor label", "CR 207.2d", "ignored"


def r4_label(text: str, ci: int = 0, card_text: str = None, card_name=None,
             crr: R4CR = None):
    """The located and classified R4 label of a chain clause, or None."""
    loc = r4_locate(text, ci)
    if loc is None:
        return None
    a, b, s = loc
    cls, cite, effect = r4_classify(text[a:b], text if card_text is None else card_text,
                                    card_name, crr)
    return {"span": [a, b], "text": text[a:b], "class": cls, "cr": cite,
            "effect": effect, "scope_start": s if effect == "ignored" else None}

# The rule table. K7 reads it: every boundary is one of these, each carries a
# CR anchor (or a declared list), and none may be keyed to a card, a name or an
# oracle_id -- `assert_not_card_keyed` halts otherwise.
RULES = (
    {"id": "clause-scope", "kind": "scope", "cr": "CR 113.2c / 207.2a",
     "pattern": "foundry_locality.units > strip_reminder > sentence_spans"},
    {"id": "region-start-head", "kind": "region", "cr": "CR 608.2c",
     "pattern": aq._BOUNDARY_WORD.pattern + " ++ " + aq._HEAD_RE.pattern},
    {"id": "region-end-next-connector", "kind": "region", "cr": "CR 608.2c",
     "pattern": aq._BOUNDARY_WORD.pattern},
    {"id": "region-end-scope", "kind": "region", "cr": "CR 113.2c",
     "pattern": "end of clause scope"},
    {"id": "cost-colon", "kind": "role:cost", "cr": "CR 602.1a / 606.2",
     "pattern": _COLON_RE.pattern},
    {"id": "cost-keyword-dash", "kind": "role:cost", "cr": "CR 702.6b",
     "pattern": aq._P2_KEYWORD.pattern},
    {"id": "condition-trigger", "kind": "role:condition", "cr": "CR 603.1",
     "pattern": _TRIGGER_RE.pattern},
    {"id": "condition-marker", "kind": "role:condition",
     "cr": "P4 _CONDITION_MARKERS (CR 603.4 / 601.2b / 611.2 / 608.2)",
     "pattern": " | ".join(rx.pattern for _, rx, _ in aq._CONDITION_MARKERS)},
    {"id": "duration-marker", "kind": "role:duration", "cr": "CR 611.2a / 611.2b",
     "pattern": _DURATION_RE.pattern},
    {"id": "destination-zone", "kind": "role:destination",
     "cr": "CR 400.1 zones; prepositions declared (CR 207.2d precedent)",
     "pattern": _DESTINATION_RE.pattern},
    {"id": "attach-contained", "kind": "attach", "cr": "CR 608.2c",
     "pattern": "span overlaps exactly the regions it attaches to"},
    # interface/2 §I3a R1 (narrowed): only these three shapes are ability-level.
    {"id": "attach-ability-prefix", "kind": "attach", "cr": "CR 602.1a / 603.1 / 603.4",
     "pattern": "a span wholly before the first region, starting at the start of "
                "the clause scope, that is: cost-colon ending at the colon; or "
                "condition-trigger opening " + _TRIGGER_RE.pattern + " ending at "
                "the trigger condition's comma; or condition-marker "
                + _R1_INTERVENING.pattern + " starting immediately after that "
                "comma -- governs every region of its ability as one attachment"},
    # interface/2 §I3a R2: a payment description is not an operation.
    {"id": "head-not-payment-cast", "kind": "region", "cr": "CR 106.1 / 601.2h",
     "pattern": _R2_PRECEDED.pattern + " ++ head cast"},
    # interface/2 §I3a R3: a table entry here; evaluated by h_region_kill.py.
    {"id": "group-back-reference", "kind": "reference", "cr": "CR 608.2c",
     "pattern": "plural " + " | ".join(R3_PLURAL_MARKERS) + " ; one earlier region "
                "with >= 2 candidates ; list marks " + aq._TARGET_TOKEN.pattern
                + " | " + aq.ol._SECOND_OBJECT.pattern + " ; each gap exactly one "
                "coordinator " + _R3_COORDINATOR.pattern + " and no "
                + aq._HEAD_RE.pattern + " , " + aq._BOUNDARY_WORD.pattern
                + " , [.;:]"},
    # interface/3 §I3a R4: a label before an ability or a mode is ignored unless
    # the CR gives it rules meaning; the ability itself is never dropped.
    {"id": "ability-label", "kind": "scope",
     "cr": "CR 700.2 / 107.17a / 123.3c / 207.2c / 701 / 702 / 714.2a / 714.2c / "
           "706 / 107 / 614.12c / 207.2d",
     "pattern": "LOCATE at the start of a chain clause of ordinal 0, after an "
                "optional " + R4_BULLET + " , up to the first '" + R4_DASH + "' with "
                "text after it on its line, holding none of "
                + " ".join(R4_NOT_IN_LABEL) + " ; CLASSIFY, first match deciding: "
                "ticket cost (" + re.escape(R4_TICKET) + ")+ IGNORED | ability word "
                "of the CR 207.2c list IGNORED | KEPT: CR 701/702 title, alias, comma "
                "list, or 702 title + " + _R4_PARAMETER.pattern + " ; CR quoted label "
                "form, [placeholder] wildcard, N number ; chapter "
                + _R4_CHAPTER.pattern + " ; number " + _R4_NUMBER.pattern + " ; "
                + _R4_SYMBOL.pattern + " or a character outside letters, digits and '"
                + R4_OTHER_CHARS + "' ; anchor word the card's own rules text names "
                "outside every label and its own name | otherwise flavor label "
                "IGNORED ; an IGNORED label moves the scope start past its dash: no "
                "head inside it starts a region, and R1 reads its scope start there"},
)
_RULE_KEYS = {"id", "kind", "cr", "pattern"}
_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)


def assert_not_card_keyed(rules, names) -> list:
    """K7's structural guard: halt on any rule keyed to a card, name or
    oracle_id, or carrying no CR anchor."""
    for r in rules:
        extra = set(r) - _RULE_KEYS
        if extra:
            fc.halt(f"derivation rule {r.get('id')!r} carries non-structural key(s) "
                    f"{sorted(extra)}; a region rule may not be card-keyed")
        if not r.get("cr"):
            fc.halt(f"derivation rule {r['id']!r} has no CR anchor")
        text = " ".join(str(v) for v in r.values())
        # Read a pattern as the literal it would match: drop regex class
        # escapes (\b, \s, ...) and escaping backslashes, so `\bName\b` or
        # `Some\ Name` cannot hide a name from the word-bounded search below.
        text = re.sub(r"\\([bBsSwWdDAZ])", " ", text).replace("\\", "")
        if _UUID.search(text):
            fc.halt(f"derivation rule {r['id']!r} names an oracle_id")
        for n in names:
            if re.search(rf"(?<![\w]){re.escape(n)}(?![\w])", text, re.I):
                fc.halt(f"derivation rule {r['id']!r} names the card {n!r}")
    return [r["id"] for r in rules]


# ------------------------------------------------------------------ (b) regions

def head_positions(text: str, corrected: bool = False) -> list:
    """Head positions under the frozen rule, REQUIRED to equal the frozen
    detector's output exactly (halts otherwise)."""
    start = aq._instruction_offset(text) if corrected else 0
    out = []
    for m in aq._HEAD_RE.finditer(text):
        b = aq._BOUNDARY_WORD.search(text[:m.start()])
        ok = bool(b)
        if corrected and not ok and start and text[start:m.start()].strip() == "":
            ok = True
        if ok:
            out.append({"head": m.group(1).lower(), "start": m.start(),
                        "end": m.end(), "connector": b.start() if b else None})
    want = aq.semantic_action_heads(text) if corrected else aq.effect_heads(text)
    if [h["head"] for h in out] != want:
        fc.halt(f"head positions diverge from the frozen detector on {text!r}")
    return out


def r2_drops(scope: str, h: dict) -> bool:
    """interface/2 §I3a R2: a head `cast` whose printed tokens are immediately
    preceded by `spent to` is a payment description and starts no region."""
    return h["head"] == "cast" and bool(_R2_PRECEDED.search(scope[:h["start"]]))


def derive_regions(text: str, lo: int, hi: int, owner: dict, r2: bool = True,
                   *, r4_start: int = None) -> tuple:
    """One region per legacy head of text[lo:hi] that R2 does not drop; offsets
    into `text`. Returns (regions, legacy heads, R2-dropped heads). `r2=False`
    is the interface/1 derivation, kept only to report what R2 changed.
    `r4_start` (interface/3 R4): the scope start after an IGNORED label; a
    legacy head before it lies inside the label and starts no region (see
    `r4_dropped_heads`); None is the interface/2 derivation."""
    scope = text[lo:hi]
    legacy = head_positions(scope)
    in_label = [h for h in legacy if r4_start is not None and lo + h["start"] < r4_start]
    dropped = [h for h in legacy if r2 and h not in in_label and r2_drops(scope, h)]
    heads = [h for h in legacy if h not in dropped and h not in in_label]
    regions = []
    for i, h in enumerate(heads):
        start = lo + h["start"]
        if i + 1 < len(heads):
            nxt = heads[i + 1]
            cut = nxt["connector"] if nxt["connector"] is not None else nxt["start"]
            end, rule = lo + max(cut, h["end"]), "region-end-next-connector"
        else:
            end, rule = hi, "region-end-scope"
        while end > start + (h["end"] - h["start"]) and text[end - 1] in " ,;:.":
            end -= 1
        regions.append({"ordinal": i, "head": h["head"],
                        "head_span": [start, lo + h["end"]], "span": [start, end],
                        "start_rule": "region-start-head", "end_rule": rule,
                        "owner": owner["id"]})
    for r in regions:
        check_bounds(r, len(text))
    shift = lambda hs: [dict(h, start=lo + h["start"], end=lo + h["end"],
                             connector=None if h["connector"] is None
                             else lo + h["connector"]) for h in hs]
    return regions, shift(legacy), shift(dropped)


def check_bounds(region: dict, n: int) -> None:
    a, b = region["span"]
    if not (0 <= a < b <= n):
        raise Refused(f"region {region['ordinal']} [{a}, {b}) leaves its clause "
                      f"[0, {n})")


def _to_comma(text: str, start: int, quoted: list) -> int:
    for i in range(start, len(text)):
        if text[i] == "," and not any(a <= i < b for a, b in quoted):
            return i
    return len(text.rstrip(" ."))


def role_spans(text: str, *, scope_start: int = None) -> tuple:
    """ATTACH-3 spans -- measurement labels only. Returns (spans, skipped),
    where `skipped` counts marks inside a quoted created ability (CR 113.2c /
    section 2 created-ability rule). `scope_start` (interface/3 R4): the scope
    start after an IGNORED label, from which the cost-colon and
    condition-trigger marks R1 reads are read; None is the interface/2 view."""
    s0 = 0 if scope_start is None else scope_start
    quoted = fx.quoted_spans(text)
    inq = lambda p: any(a <= p < b for a, b in quoted)
    raw, skipped = [], 0

    def add(role, rule, a, b):
        nonlocal skipped
        if inq(a):
            skipped += 1
        elif b > a:
            raw.append((role, a, b, rule))

    colon = next((m.start() for m in _COLON_RE.finditer(text) if not inq(m.start())),
                 None)
    if colon is not None and colon >= s0:
        add("cost", "cost-colon", s0, colon)
    kw = aq._P2_KEYWORD.match(text)
    if kw and kw.group(1).strip().lower() in aq._CR702_KEYWORD_NAMES:
        add("cost", "cost-keyword-dash", kw.end(), len(text.rstrip(" .")))
    body = colon + 1 if colon is not None and colon >= s0 else s0
    lead = len(text[body:]) - len(text[body:].lstrip())
    if _TRIGGER_RE.match(text, body + lead):
        add("condition", "condition-trigger", body + lead,
            _to_comma(text, body + lead, quoted))
    durations = []
    for m in _DURATION_RE.finditer(text):
        durations.append((m.start(), _to_comma(text, m.end(), quoted)))
        add("duration", "duration-marker", *durations[-1])
    low = text.lower()
    for _name, rx, _anchor in aq._CONDITION_MARKERS:
        for m in rx.finditer(low):
            if any(a <= m.start() < b for a, b in durations):
                continue                 # CR 611.2b: "for as long as" is a duration
            add("condition", "condition-marker", m.start(),
                _to_comma(text, m.end(), quoted))
    for m in _DESTINATION_RE.finditer(text):
        add("destination", "destination-zone", m.start(), m.end())
    # Same-role overlapping marks are one span (union), deterministically.
    merged = []
    for role, a, b, rule in sorted(raw):
        if merged and merged[-1]["role"] == role and a < merged[-1]["span"][1]:
            last = merged[-1]
            last["span"][1] = max(last["span"][1], b)
            last["rules"] = sorted(set(last["rules"]) | {rule})
            continue
        merged.append({"role": role, "span": [a, b], "rules": [rule]})
    return merged, skipped


def r1_shape(text: str, span: dict, spans: list, *, scope_start: int = None):
    """interface/2 §I3a R1: the ability-level shape of `span`, or None. The
    clause scope starts at the start of the chain clause (`clause-scope`), or
    (interface/3) at `scope_start`, after an IGNORED R4 label."""
    a, b = span["span"]
    start = len(text) - len(text.lstrip()) if scope_start is None else scope_start
    if span["role"] == "cost" and "cost-colon" in span["rules"]:
        colon = next((m.start() for m in _COLON_RE.finditer(text)
                      if not any(x <= m.start() < y for x, y in fx.quoted_spans(text))),
                     None)
        if a == start and b == colon:
            return "cost-colon"
    if span["role"] != "condition":
        return None
    quoted = fx.quoted_spans(text)

    def trigger(s):
        x, y = s["span"]
        return (s["role"] == "condition" and x == start and _TRIGGER_RE.match(text, x)
                and y == _to_comma(text, x, quoted) and y < len(text)
                and text[y] == ",")
    if trigger(span):
        return "condition-trigger"
    if any(trigger(s) and text[s["span"][1] + 1:a].strip() == ""
           and s["span"][1] < a for s in spans) and _R1_INTERVENING.match(text, a):
        return "condition-marker"
    return None


def attach(span: dict, regions: list, shape=None) -> dict:
    a, b = span["span"]
    if not regions:
        # Not "none": no region was derived because the detector found no head
        # here -- an extraction failure, kept apart so it is never read as an
        # attachment the derivation rule refused.
        return {"attached": [], "rule": None, "outcome": "no_region",
                "reason": "clause has no region (no legacy head was extracted)"}
    over = [r["ordinal"] for r in regions if a < r["span"][1] and r["span"][0] < b]
    if over:
        return {"attached": over, "rule": "attach-contained",
                "outcome": "attached" if len(over) == 1 else "multiple",
                "reason": "" if len(over) == 1 else "span crosses a region boundary"}
    if b <= regions[0]["span"][0]:
        every = [r["ordinal"] for r in regions]
        if shape:
            # interface/2 §I3a R1: ONE attachment, to the ability.
            return {"attached": every, "rule": "attach-ability-prefix",
                    "outcome": "attached", "attached_to": "ability",
                    "r1_shape": shape,
                    "reason": f"R1 {shape}: an ability-level span governs every "
                              f"region of its ability as one attachment"}
        # Not an R1 shape: the interface/1 outcome, unchanged.
        return {"attached": every, "rule": "attach-ability-prefix",
                "outcome": "attached" if len(every) == 1 else "multiple",
                "reason": "" if len(every) == 1 else
                "an ability-prefix span governs every region of the clause"}
    return {"attached": [], "rule": None, "outcome": "none",
            "reason": "span lies outside every region and after the first"}


# The fields of a clause record R4 may change (R4 IS CONFINED compares them).
R4_FIELDS = ("scope", "heads_region", "r4_dropped_heads", "r2_dropped_heads",
             "regions", "repeated_heads", "overlaps", "nestings", "role_spans")


def r4_confined(off: dict, on: dict, label) -> None:
    """interface/3 R4 IS CONFINED: with no IGNORED label (no label, or a KEPT
    one) the R4-on record equals the R4-off record. A difference HALTS (a STOP
    to the Captain)."""
    if label is not None and label["effect"] == "ignored":
        return
    strip = lambda c: {k: c[k] for k in R4_FIELDS}
    if strip(off) != strip(on):
        diff = sorted(k for k in R4_FIELDS if off[k] != on[k])
        fc.halt(f"R4 IS CONFINED: {on['address']['id']} has "
                f"{'no label' if label is None else 'a KEPT label'} yet R4 changes "
                f"{diff}: a STOP to the Captain")


def _r4_beside(off: dict, on: dict) -> None:
    """Every region and role span R4 alone changed carries its interface/2
    value beside it (`interface2`, rule R4)."""
    for r in on["regions"]:
        was = next((x for x in off["regions"] if x["head_span"] == r["head_span"]), None)
        if was != {k: v for k, v in r.items() if k != "interface2"}:
            r["interface2"] = {"region": was, "changed_by": ["R4"]}
    bare = _bare
    for s in on["role_spans"]:
        if any(bare(x) == bare(s) for x in off["role_spans"]):
            continue
        was = next((x for x in off["role_spans"] if x["role"] == s["role"]
                    and x["span"][0] < s["span"][1] and s["span"][0] < x["span"][1]),
                   None)
        s["interface2"] = {"span": None if was is None else bare(was),
                           "changed_by": ["R4"]}


def clause_record(oid: str, fi: int, pi: int, ci: int, text: str, lo: int, hi: int,
                  scope_kind: str, *, card_text: str = None, card_name: str = None,
                  r4: bool = True) -> dict:
    """The interface/3 record of one clause. `card_text` and `card_name` feed
    R4's anchor-word and own-name classes (defaults: the clause text, no name).
    `r4=False` is the R4-off view: the interface/2 derivation exactly."""
    off = _clause_view(oid, fi, pi, ci, text, lo, hi, scope_kind, None)
    label = r4_label(text, ci, card_text, card_name) if r4 else None
    s = label["scope_start"] if label and label["effect"] == "ignored" else None
    on = _clause_view(oid, fi, pi, ci, text, lo, hi, scope_kind, s)
    r4_confined(off, on, label)
    if label is not None:
        label["dropped_heads"] = on["r4_dropped_heads"]
    on["r4_label"] = label
    if s is not None:
        # R1-R3 (interface/1 vs interface/2) records come from the R4-off view
        # only: a span R4 left untouched carries the R4-off annotation; a span
        # R4 changed carries none (its interface/2 value stands beside it).
        for sp in on["role_spans"]:
            sp.pop("interface1", None)
            was = next((x for x in off["role_spans"] if _bare(x) == _bare(sp)), None)
            if was is not None and "interface1" in was:
                sp["interface1"] = was["interface1"]
        changed = sorted(k for k in R4_FIELDS if _bare(off[k]) != _bare(on[k]))
        _r4_beside(off, on)
        on["r4_interface2"] = {"rule": "R4", "changed": changed,
                               **{k: off[k] for k in R4_FIELDS}}
    return on


def _bare(x):
    """A derivation value without its rule-comparison annotations."""
    if isinstance(x, list):
        return [_bare(v) for v in x]
    if isinstance(x, dict):
        return {k: _bare(v) for k, v in x.items() if k not in ("interface1", "interface2")}
    return x


def _clause_view(oid: str, fi: int, pi: int, ci: int, text: str, lo: int, hi: int,
                 scope_kind: str, r4_start) -> dict:
    owner = {"oracle_id": oid, "face": fi, "paragraph": pi, "clause": ci,
             "id": f"{oid}:{fi}:{pi}:{ci}"}
    regions, legacy, dropped = derive_regions(text, lo, hi, owner, r4_start=r4_start)
    in_label = [h for h in legacy if r4_start is not None and h["start"] < r4_start]
    regions_i1, _, _ = derive_regions(text, lo, hi, owner, r2=False)
    corrected = [dict(h, start=lo + h["start"], end=lo + h["end"],
                      connector=None if h["connector"] is None
                      else lo + h["connector"])
                 for h in head_positions(text[lo:hi], corrected=True)]
    spans, skipped = role_spans(text, scope_start=r4_start)
    shapes = [r1_shape(text, s, spans, scope_start=r4_start) for s in spans]
    key = lambda x: (x["attached"], x["outcome"])
    for s, shape in zip(spans, shapes):
        i1 = attach(s, regions_i1)
        by = [rule for rule, alone in (("R1", attach(s, regions_i1, shape)),
                                       ("R2", attach(s, regions)))
              if key(alone) != key(i1)]
        s.update(attach(s, regions, shape))
        if key(i1) != key(s):
            # Reported beside the interface/2 attachment (interface/2 I3).
            s["interface1"] = {"attached": i1["attached"], "outcome": i1["outcome"],
                               "rule": i1["rule"], "changed_by": by}
    lk = [(h["head"], h["start"]) for h in legacy]
    ck = [(h["head"], h["start"]) for h in corrected]
    counts = {}
    for r in regions:
        counts[r["head"]] = counts.get(r["head"], 0) + 1
    pairs = list(combinations(regions, 2))
    return {
        "address": owner, "clause_text": text,
        "clause_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "scope": [lo if r4_start is None else max(lo, r4_start), hi],
        "scope_kind": scope_kind,
        "heads_legacy": legacy, "heads_corrected": corrected,
        "heads_region": [h for h in legacy if h not in dropped and h not in in_label],
        "r2_dropped_heads": dropped, "r4_dropped_heads": in_label,
        "detector_diff": {"differs": lk != ck,
                          "only_legacy": [list(x) for x in lk if x not in ck],
                          "only_corrected": [list(x) for x in ck if x not in lk]},
        "regions": regions,
        "repeated_heads": sorted(h for h, n in counts.items() if n > 1),
        "overlaps": [[x["ordinal"], y["ordinal"]] for x, y in pairs
                     if x["span"][0] < y["span"][1] and y["span"][0] < x["span"][1]],
        "nestings": [[x["ordinal"], y["ordinal"]] for x, y in pairs
                     if (x["span"][0] <= y["span"][0] and y["span"][1] <= x["span"][1])
                     or (y["span"][0] <= x["span"][0] and x["span"][1] <= y["span"][1])],
        "role_spans": spans, "role_marks_in_created_ability": skipped,
    }


# ------------------------------------------------------------ (c) measurement

def r4_off(c: dict) -> dict:
    """The R4-off (interface/2) view of a record: equal to the record unless an
    IGNORED label moved its scope."""
    return dict(c, **{k: v for k, v in c["r4_interface2"].items()
                      if k in R4_FIELDS}) if c.get("r4_interface2") else c


def r4_measure(records: list) -> dict:
    """R4 reach (clauses with an IGNORED label, per class) and the KEPT labels
    listed separately; every label with its offsets, class, CR citation and
    effect; and what R4 changed, beside the interface/2 value."""
    labelled = [c for c in records if c.get("r4_label")]
    by = lambda eff: {cls: {"count": len(ids), "clauses": ids} for cls, ids in sorted(
        _group((c["r4_label"]["class"], c["address"]["id"]) for c in labelled
               if c["r4_label"]["effect"] == eff).items())}
    return {
        "labels": [{"clause": c["address"]["id"], "span": c["r4_label"]["span"],
                    "text": c["r4_label"]["text"], "class": c["r4_label"]["class"],
                    "cr": c["r4_label"]["cr"], "effect": c["r4_label"]["effect"],
                    "scope_start": c["r4_label"]["scope_start"],
                    "dropped_heads": [[h["head"], h["start"]]
                                      for h in c["r4_label"]["dropped_heads"]],
                    "r4_changed": (c.get("r4_interface2") or {}).get("changed", [])}
                   for c in labelled],
        "reach_ignored": by("ignored"),
        "reach_ignored_clauses": sorted(c["address"]["id"] for c in labelled
                                        if c["r4_label"]["effect"] == "ignored"),
        "kept": by("kept"),
        "labelled_not_named_by_interface": [
            {"clause": c["address"]["id"], "class": c["r4_label"]["class"],
             "effect": c["r4_label"]["effect"],
             "r4_changed": (c.get("r4_interface2") or {}).get("changed", []),
             "note": "R4 changes nothing here" if not (c.get("r4_interface2") or {})
             .get("changed") else "see changed_from_interface2"}
            for c in labelled if c["address"]["id"] not in R4_EXPECTED],
        "dropped_heads": sorted([c["address"]["id"], h["head"], h["start"]]
                                for c in records for h in c["r4_dropped_heads"]),
        "changed_from_interface2": [
            {"clause": c["address"]["id"], "changed": c["r4_interface2"]["changed"],
             "role_spans": [{"role": s["role"], "span": s["span"],
                             "outcome": s["outcome"], "r1_shape": s.get("r1_shape"),
                             "interface2": s["interface2"]}
                            for s in c["role_spans"] if "interface2" in s],
             "regions": [{"head": r["head"], "span": r["span"],
                          "interface2": r["interface2"]}
                         for r in c["regions"] if "interface2" in r],
             "interface2_regions_dropped": [
                 {"head": r["head"], "span": r["span"]}
                 for r in c["r4_interface2"]["regions"]
                 if all(r["head_span"] != x["head_span"] for x in c["regions"])],
             "interface2_role_spans_gone": [
                 {"role": s["role"], "span": s["span"], "outcome": s["outcome"]}
                 for s in c["r4_interface2"]["role_spans"]
                 if not any(s["role"] == x["role"] and s["span"][0] < x["span"][1]
                            and x["span"][0] < s["span"][1] for x in c["role_spans"])]}
            for c in records if c.get("r4_interface2")],
        "rule": "interface/3 §I3a R4 ability-label; the R4-off view is the "
                "interface/2 derivation and carries every R1-R3 record",
    }


def _group(pairs) -> dict:
    out = {}
    for k, v in pairs:
        out.setdefault(k, []).append(v)
    return {k: sorted(v) for k, v in out.items()}


def measure(records: list) -> dict:
    out = _measure(records)
    # interface/1-versus-interface/2 records come from the R4-off view only.
    out["interface2_rules"] = _measure([r4_off(c) for c in records])["interface2_rules"]
    out["interface3_rules"] = {"R4_ability_label": r4_measure(records)}
    return out


def _measure(records: list) -> dict:
    regions = [r for c in records for r in c["regions"]]
    att = {k: {"spans": 0, "attached": 0, "multiple": 0, "none": 0, "no_region": 0,
               "multiple_ability_prefix": 0, "multiple_crossing": 0}
           for k in ("cost", "condition", "duration", "destination")}
    for c in records:
        for s in c["role_spans"]:
            a = att[s["role"]]
            a["spans"] += 1
            a[s["outcome"]] += 1
            if s["outcome"] == "multiple":
                a["multiple_ability_prefix" if s["rule"] == "attach-ability-prefix"
                  else "multiple_crossing"] += 1
            if s.get("r1_shape"):
                a["attached_r1_ability"] = a.get("attached_r1_ability", 0) + 1
    for v in att.values():
        v.setdefault("attached_r1_ability", 0)
        v["success"] = v["attached"]
        v["failure"] = v["multiple"] + v["none"]
        v["extraction_failure"] = v["no_region"]
    crossing = {"clause": 0, "paragraph": 0, "face": 0}
    for c in records:
        n = len(c["clause_text"])
        for r in c["regions"]:
            a, b = r["span"]
            if not (0 <= a < b <= n):
                crossing["clause"] += 1
            if "\n" in c["clause_text"][a:b]:
                crossing["paragraph"] += 1
            if r["owner"] != c["address"]["id"]:
                crossing["face"] += 1
    ids = lambda pred: sorted({c["address"]["id"] for c in records if pred(c)})
    return {
        "clauses": len(records), "regions": len(regions),
        "clauses_without_region": ids(lambda c: not c["regions"]),
        "regions_per_clause": {str(k): v for k, v in sorted(
            _count(len(c["regions"]) for c in records).items())},
        "boundary_crossing": crossing,
        "overlap_pairs": sum(len(c["overlaps"]) for c in records),
        "nesting_pairs": sum(len(c["nestings"]) for c in records),
        "clauses_with_overlap": ids(lambda c: c["overlaps"]),
        "clauses_with_repeated_operation": ids(lambda c: c["repeated_heads"]),
        "repeated_operation_clauses": sum(1 for c in records if c["repeated_heads"]),
        "attach3": att,
        "attach3_failures": sorted(
            [c["address"]["id"], s["role"], s["outcome"]]
            for c in records for s in c["role_spans"] if s["outcome"] != "attached"),
        "interface2_rules": {
            "R1_attach_ability_prefix": {
                "spans": sum(1 for c in records for s in c["role_spans"]
                             if s.get("r1_shape")),
                "by_shape": {k: v for k, v in sorted(_count(
                    s["r1_shape"] for c in records for s in c["role_spans"]
                    if s.get("r1_shape")).items())},
                "clauses": ids(lambda c: any(s.get("r1_shape")
                                             for s in c["role_spans"])),
                "prefix_spans_of_no_r1_shape": sorted(
                    [c["address"]["id"], s["role"], s["outcome"]]
                    for c in records for s in c["role_spans"]
                    if s["rule"] == "attach-ability-prefix" and not s.get("r1_shape"))},
            "R2_head_not_payment_cast": {
                "clauses": ids(lambda c: c["r2_dropped_heads"]),
                "dropped_heads": sorted([c["address"]["id"], h["head"], h["start"]]
                                        for c in records for h in c["r2_dropped_heads"]),
                "note": "the frozen detector is not edited; these legacy heads start "
                        "no region (interface/2 §I3a R2)"},
            "R3_group_back_reference": "a derivation-table entry here; evaluated "
                                       "by h_region_kill.py (C03-KILL)",
            "attach3_changed_from_interface1": sorted(
                [c["address"]["id"], s["role"], s["span"], s["interface1"]["outcome"],
                 s["outcome"], s["interface1"]["changed_by"]]
                for c in records for s in c["role_spans"] if "interface1" in s),
        },
        "legacy_vs_corrected": {
            "clauses_differing": sum(1 for c in records if c["detector_diff"]["differs"]),
            "clauses": ids(lambda c: c["detector_diff"]["differs"]),
            "note": "reported only; regions are derived from the legacy detector "
                    "and the corrected one is never substituted (I2)"},
    }


# interface/3 §I3a: the classes R4 must give on C03's sets (FS-2 population
# clauses and the FS-1 fixture clause). A verification table read from the
# ratified text, not a derivation rule: no rule in RULES names a clause.
R4_EXPECTED = {
    "0988d2cd-4e1d-47c6-b0db-0ff0335b12e6:0:2:0": "ability word",
    "b095526e-94a4-416b-83de-d6271804ccf3:0:0:0": "ability word",
    "60a69ddc-3289-4786-944d-27a82c5f0dc8:0:0:0": "ticket cost",
    "09ef446c-a13d-49d9-a94c-cd5f5a2d440b:0:0:0": "flavor label",
    "9ad12c75-e97d-404a-bfa9-26ff1d0bb506:0:0:0": "flavor label",
    "19b229c4-1c21-4c7c-a25e-4e8c1cd4ed4b:0:0:0": "flavor label",
}

# interface/3 §I3a R4 reach report, CITED and not re-measured.
R4_CORPUS_REACH = {
    "source": f"{INTERFACES_REL} §I3a 'R4 reach report' (measured 2026-10-01 over "
              f"the pinned corpus with this derivation's chain_clauses)",
    "cards": 32557, "clauses": 74106, "halts": 0,
    "cr_counts": dict(R4_CR_COUNTS),
    "clauses_with_label": 3105,
    "by_class": {"ability word": [1356, "ignored"], "ticket cost": [192, "ignored"],
                 "flavor label": [625, "ignored"], "keyword": [221, "kept"],
                 "chapter symbol": [576, "kept"], "symbol-bearing": [66, "kept"],
                 "anchor word": [29, "kept"], "CR label form": [25, "kept"],
                 "number": [15, "kept"]},
    "ignored_clauses": 2173, "ignored_cards": 1892, "kept_clauses": 932,
    "status": "cited, not re-measured",
}


def r4_check_expected(records: list) -> dict:
    """Each FS-1 / FS-2 clause carries exactly the class §I3a states, IGNORED,
    or HALT (a STOP to the Captain)."""
    out = {}
    for cid, want in sorted(R4_EXPECTED.items()):
        recs = [c for c in records if c["address"]["id"] == cid]
        got = sorted({(c["r4_label"] or {}).get("class") for c in recs}, key=str)
        if not recs or got != [want] or any(c["r4_label"]["effect"] != "ignored"
                                            for c in recs):
            fc.halt(f"R4: {cid} classifies as {got}, interface/3 §I3a states "
                    f"{want!r}: a STOP to the Captain")
        out[cid] = {"class": want, "effect": "ignored",
                    "label_span": recs[0]["r4_label"]["span"],
                    "scope_start": recs[0]["r4_label"]["scope_start"]}
    return out


def _count(it) -> dict:
    out = {}
    for x in it:
        out[x] = out.get(x, 0) + 1
    return out


# ---------------------------------------------------------- negative controls

def _halts(fn) -> bool:
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            fn()
    except SystemExit:
        return True
    return False


def _refused(fn) -> bool:
    try:
        fn()
    except Refused:
        return True
    return False


def portability_violations(data: bytes) -> list:
    out = []
    for label, s in (("repository root", str(ROOT)), ("home directory", str(Path.home()))):
        if s.encode("utf-8") in data:
            out.append(label)
    return out


def _rigged(text: str) -> dict:
    return clause_record("rigged", 0, 0, 0, text, 0, len(text), "rigged")


def _card_keyed_variants(names: list, oid: str) -> list:
    """Each §I3a rule with a card name or an oracle_id put in each of its four
    keys, one at a time."""
    out = []
    for r in RULES:
        if r["id"] not in ("attach-ability-prefix", "head-not-payment-cast",
                           "group-back-reference", "ability-label"):
            continue
        for k in sorted(_RULE_KEYS):
            for key in (names[0], oid):
                out.append(dict(r, **{k: f"{r[k]} {key}"}))
    if len(out) != 4 * len(_RULE_KEYS) * 2:
        fc.halt("the derivation table is missing an interface/3 §I3a rule")
    return out


def _tampered(old: str, new: str, count: int = 1) -> str:
    txt = cr.text()
    if old not in txt:
        fc.halt(f"negative control: {old!r} is not in the pinned CR")
    return txt.replace(old, new, count)


def _cr_tamper_rigs() -> list:
    """Each R4 completeness check, rigged to STOP on a tampered CR."""
    txt = cr.text()
    line = next(l for l in txt.splitlines() if l.startswith("207.2c "))
    lead = "The ability words are "
    first = line[line.index(lead) + len(lead):].split(", ")[1]
    h701 = next(l for l in txt.splitlines() if l.startswith("701.30. "))
    h702 = next(l for l in txt.splitlines() if l.startswith("702.30. "))
    tk = "\n".join(l.replace("{TK}", "{ZZ}") if l.startswith("107.") else l
                   for l in txt.splitlines())
    return [
        ("the 207.2c sentence missing", _tampered(lead, "The ability-word list is ")),
        ("the 207.2c sentence not re-joining its source",
         _tampered(line, line.replace(", " + first + ", ", ", and " + first + ", ", 1))),
        ("a gap in the 701 heading sequence", _tampered(h701 + "\n", "")),
        ("a gap in the 702 heading sequence", _tampered(h702 + "\n", "")),
        ("a CR 107 symbol inventory missing {TK}", tk),
        ("the CR label forms missing 'to solve'", _tampered("“To solve — [", "“To solve [")),
        ("CR 702.159b without 'Prize'",
         _tampered("the word “Prize” and a long dash", "a long dash")),
    ]


def _label_of(text: str, card_text: str = None, card_name: str = None):
    return (r4_label(text, 0, card_text, card_name) or {}).get("class")


def _r4_controls() -> list:
    """The interface/3 §I3a R4 guards, each shown to fire on a rigged input."""
    blink = (" — Whenever a land you control enters, exile target creature you "
             "control, then return it to the battlefield under its owner's control.")
    aw = _rigged("Landfall" + blink)
    fl_ = _rigged("Quiet Drill" + blink)
    kw = _rigged("Flying" + blink)
    kw_off = clause_record("rigged", 0, 0, 0, kw["clause_text"], 0,
                           len(kw["clause_text"]), "rigged", r4=False)
    head = _rigged("Exile Protocol — Roll a six-sided die.")
    trig = lambda c: [(s["span"][0], s.get("r1_shape"), s["outcome"],
                       s.get("attached_to")) for s in c["role_spans"]
                      if s["role"] == "condition"]
    anchor_text = "As this enters, choose Khans or Dragons.\n• Khans — Draw a card."
    plain_text = "As this enters, draw a card.\n• Khans — Draw a card."
    named_text = "Whenever Bloody Plan attacks, draw a card.\n• Bloody Plan — Draw a card."
    unl = _rigged("When this creature enters, exile target creature.")
    moved = lambda c: dict(c, scope=[c["scope"][0] + 1, c["scope"][1]])
    kept_label = {"effect": "kept", "class": "keyword"}
    counts_off = [dict(R4_CR_COUNTS, **{k: v + 1}) for k, v in R4_CR_COUNTS.items()]
    return [
        ("a rigged tampered CR STOPs the derivation for each R4 completeness check: "
         "the 207.2c sentence missing or not re-joining its source; a gap in the 701 "
         "or 702 heading sequence; a CR 107 symbol inventory missing {TK}; the CR "
         "label forms missing 'to solve'; CR 702.159b without 'Prize'",
         lambda: all(_halts(lambda t=t: r4_cr_read(t)) for _, t in _cr_tamper_rigs())
         and not _halts(lambda: r4_cr_read(cr.text()))),
        ("a rigged flavor label (synthetic label text only) holding a frozen effect "
         "head starts no region from that head, and the dropped head is reported",
         lambda: head["r4_label"]["class"] == "flavor label"
         and [h["head"] for h in head["heads_legacy"]] == ["exile"]
         and not head["regions"]
         and [h["head"] for h in head["r4_dropped_heads"]] == ["exile"]
         and [h["head"] for h in head["r4_label"]["dropped_heads"]] == ["exile"]),
        ("a rigged ability-word or flavor label before 'Whenever ..., exile <x>, then "
         "return it' yields a condition-trigger mark at the new scope start that R1 "
         "attaches once, to the ability; the same clause with a KEPT keyword label "
         "keeps its interface/2 outcome",
         lambda: aw["r4_label"]["class"] == "ability word"
         and fl_["r4_label"]["class"] == "flavor label"
         and all(trig(c) == [(c["r4_label"]["scope_start"], "condition-trigger",
                              "attached", "ability")] for c in (aw, fl_))
         and kw["r4_label"]["class"] == "keyword" and kw["r4_label"]["effect"] == "kept"
         and not trig(kw)
         and {k: kw[k] for k in R4_FIELDS} == {k: kw_off[k] for k in R4_FIELDS}),
        ("a rigged end-of-line 'Choose one —' and a rigged label holding '.' or ':' "
         "are no label",
         lambda: r4_locate("Choose one —", 0) is None
         and r4_locate("Choose one — ", 0) is None
         and r4_locate("Mr. Plan — Draw a card.", 0) is None
         and r4_locate("Plan: B — Draw a card.", 0) is None
         and r4_locate("Plan B — Draw a card.", 1) is None
         and r4_locate("Plan B — Draw a card.", 0) is not None),
        ("a rigged label the card's own rules text names elsewhere is KEPT (anchor "
         "word); the same label not named elsewhere, and a label equal to the card's "
         "own name, are flavor labels",
         lambda: _label_of("• Khans — Draw a card.", anchor_text) == "anchor word"
         and _label_of("• Khans — Draw a card.", plain_text) == "flavor label"
         and _label_of("• Bloody Plan — Draw a card.", named_text,
                       "Bloody Plan") == "flavor label"
         and _label_of("• ~ — Draw a card.", "Whenever ~ attacks, draw.\n• ~ — Draw "
                       "a card.") == "flavor label"),
        ("classification order holds on a rigged label that matches two classes (the "
         "earlier class decides)",
         lambda: _label_of("{TK}{TK} — Draw a card.") == "ticket cost"
         and _label_of("Landfall — Draw a card.",
                       "Landfall — Draw a card.\nLandfall matters.") == "ability word"
         and _label_of("Exhaust — Draw a card.") == "keyword"
         and _label_of("+ {1} — Draw a card.") == "symbol-bearing"),
        ("a rigged R4-on change on an unlabelled clause, and one on a KEPT-label "
         "clause, each STOP (R4 IS CONFINED)",
         lambda: _halts(lambda: r4_confined(unl, moved(unl), None))
         and _halts(lambda: r4_confined(kw, moved(kw), kept_label))
         and not _halts(lambda: r4_confined(unl, unl, None))),
        ("a rigged CR read whose ability-word, keyword-title or label-form count "
         "differs from §I3a's 61 / 264 / 23 STOPs",
         lambda: all(_halts(lambda c=c: r4_check_counts(c)) for c in counts_off)
         and not _halts(lambda: r4_check_counts(dict(R4_CR_COUNTS)))),
    ]


def negative_controls(rows: list, c02: dict, names: list, oid: str) -> list:
    """Each guard this script contracts, shown to fire on a rigged input."""
    standalone = _rigged("If you control an artifact, exile target creature, then "
                         "return it to the battlefield under its owner's control.")
    permission = _rigged("Exile target card, then you may cast that card.")
    payment = _rigged("Destroy target creature if {G} was spent to cast this spell.")
    trigger = _rigged("When this creature enters, if you control an artifact, exile "
                      "target creature, then return it to the battlefield.")
    cases = [
        ("a rigged identity hash halts",
         lambda: _halts(lambda: verify_identities(dict(I1, **{C02_REL: "0" * 64})))),
        ("a rigged reconciliation figure halts",
         lambda: _halts(lambda: reconcile(rows, c02, dict(I2, rows=I2["rows"] + 1)))),
        ("a rigged clause whose region would cross the clause boundary is refused",
         lambda: _refused(lambda: locate(
             [(0, 0, i, s) for i, s in enumerate(fx.sentence_spans(
                 "Exile target creature! Return it to the battlefield."))],
             "Exile target creature! Return it to the battlefield"))
         and _refused(lambda: check_bounds({"ordinal": 0, "span": [0, 9]}, 8))),
        ("a rigged card-keyed rule halts",
         lambda: _halts(lambda: assert_not_card_keyed(
             RULES + ({"id": "rig", "kind": "region", "cr": "CR 608.2c",
                       "pattern": "x", "oracle_id": "rig"},), names))
         and _halts(lambda: assert_not_card_keyed(
             RULES + ({"id": "rig", "kind": "region", "cr": "CR 608.2c",
                       "pattern": rf"\b{names[0]}\b"},), names))),
        ("a rigged output containing the absolute repository root fails "
         "--check-determinism",
         lambda: bool(portability_violations(b'{"p": "' + str(ROOT).encode() + b'"}'))
         and not portability_violations(b'{"p": "experiments/out"}')),
        ("a rigged card-keyed variant of R1, R2, R3 and R4 (a card name or oracle_id "
         "in id, kind, cr or pattern) halts",
         lambda: all(_halts(lambda v=v: assert_not_card_keyed(RULES + (v,), names))
                     for v in _card_keyed_variants(names, oid))),
        ("a rigged standalone 'If <condition>, exile <x>, then return it' (no "
         "trigger word) keeps a multiple attachment under R1",
         lambda: [(s["role"], s["outcome"], s.get("r1_shape"))
                  for s in standalone["role_spans"] if s["span"][0] == 0]
         == [("condition", "multiple", None)] and len(standalone["regions"]) == 2),
        ("a rigged 'you may cast <x>' is not discounted by R2 and still starts a "
         "region",
         lambda: [r["head"] for r in permission["regions"]] == ["exile", "cast"]
         and not permission["r2_dropped_heads"]
         # the arm itself fires: `spent to cast` starts no region
         and [r["head"] for r in payment["regions"]] == ["destroy"]
         and [h["head"] for h in payment["r2_dropped_heads"]] == ["cast"]),
        ("a rigged trigger and its intervening 'if' attach once, to the ability, "
         "under R1",
         lambda: sorted((s["r1_shape"], s["outcome"]) for s in trigger["role_spans"]
                        if s.get("r1_shape"))
         == [("condition-marker", "attached"), ("condition-trigger", "attached")]),
    ] + _r4_controls()
    out = []
    for name, check in cases:
        if not check():
            fc.halt(f"negative control failed: {name}")
        out.append(name)
    return out


# ------------------------------------------------------------------- build

def build() -> dict:
    identities = verify_identities(I1)
    blob = verify_interface()
    cards, _, _ = fc.load_corpus_gated()
    rows = fqc.population(cards)
    c02 = json.loads((ROOT / C02_REL).read_text(encoding="utf-8"))
    reconciled = reconcile(rows, c02)
    population = sorted((r for r in rows if len(aq.effect_heads(r["clause"])) > 1),
                        key=f0.key)
    fixtures = load_fixtures(cards)
    names = sorted({cards[r["oracle_id"]]["name"] for r in population}
                   | {cards[m["oracle_id"]]["name"] for f in fixtures
                      for m in f["members"] if m["oracle_id"]})
    rule_ids = assert_not_card_keyed(RULES, names)

    records = {}                                   # (address id, census key) -> record

    def put(oid, stem_occ, text_loc, kind):
        fi, pi, ci, text, lo, hi = text_loc
        k = (f"{oid}:{fi}:{pi}:{ci}", tuple(stem_occ) if stem_occ else None)
        if k not in records:
            rec = clause_record(oid, fi, pi, ci, text, lo, hi, kind,
                                card_text=card_rules_text(cards[oid]),
                                card_name=cards[oid]["name"])
            rec.update(census_key=list(stem_occ) if stem_occ else None,
                       population=False, fixture_roles=[])
            records[k] = rec
        return records[k]

    by_key = {f0.key(r): r for r in rows}
    for r in population:
        try:
            fi, pi, ci, text, off = resolve_census(cards[r["oracle_id"]], r["clause"])
        except Refused as exc:
            fc.halt(f"population clause {f0.key(r)} has no four-coordinate address "
                    f"through the ratified chain: {exc}")
        rec = put(r["oracle_id"], (r["stem"], r["occurrence"]),
                  (fi, pi, ci, text, off, off + len(r["clause"])), "census-clause")
        rec["population"] = True

    fixture_out = []
    for fam in fixtures:
        entry = {"role": fam["role"], "member_status": fam["member_status"],
                 "members": []}
        for m in fam["members"]:
            oid, ck = m["oracle_id"], m["census_key"]
            if oid is None:
                entry["members"].append(dict(m, clauses=[]))
                continue
            card = cards[oid]
            keyed = None
            if ck:
                row = by_key.get((oid, ck[0], ck[1]))
                if row is None:
                    fc.halt(f"fixture {fam['role']}: census key {ck} is not a census "
                            f"row of {oid}")
                try:
                    keyed = resolve_census(card, row["clause"])
                except Refused as exc:
                    fc.halt(f"fixture {fam['role']}: census clause {ck} has no "
                            f"address: {exc}")
            addrs = []
            for fi, pi, ci, seg in chain_clauses(card):
                if keyed and keyed[:3] == (fi, pi, ci):
                    rec = put(oid, ck, (fi, pi, ci, seg, keyed[4],
                                        keyed[4] + len(row["clause"])), "census-clause")
                else:
                    rec = put(oid, None, (fi, pi, ci, seg, 0, len(seg)), "chain-clause")
                rec["fixture_roles"] = sorted(set(rec["fixture_roles"]) | {fam["role"]})
                addrs.append(rec["address"]["id"])
            entry["members"].append({"oracle_id": oid, "census_key": ck,
                                     "clauses": addrs})
        entry["clauses"] = sum(len(m["clauses"]) for m in entry["members"])
        fixture_out.append(entry)

    ordered = [records[k] for k in sorted(records, key=lambda k: (k[0], k[1] or ()))]
    pop = [c for c in ordered if c["population"]]
    fix = [c for c in ordered if c["fixture_roles"]]
    r4_expected = r4_check_expected(ordered)
    inputs = {rel: _sha(rel) for rel in INPUTS}
    return {
        "schema": "oracle-compiler-c03-regions/0",
        "interface": {"version": INTERFACE_VERSION,
                      "blob": blob, "i1_identities": identities},
        "inputs": inputs,
        "script": {"path": SCRIPT, "sha256": _sha(SCRIPT)},
        "reconciled_with_c02": reconciled,
        "chain": ["tier_engine.get_raw_faces", "foundry_common.canonicalize_self_reference",
                  "foundry_locality.units", "foundry_shape_extractor.strip_reminder",
                  "foundry_shape_extractor.quoted_spans",
                  "foundry_shape_extractor.sentence_spans"],
        "chain_note": "AQ4 register #29, canonical detector view; a census clause "
                      "is placed by foundry_locality.resolve and must sit inside "
                      "exactly one chain clause",
        "detectors": {"regions_from": "foundry_aq4_probes.effect_heads (legacy, frozen)",
                      "reported_beside": "foundry_aq4_probes.semantic_action_heads"},
        "rules": list(RULES), "rules_checked_not_card_keyed": rule_ids,
        "declared_lists": {"destination_prepositions": list(DESTINATION_PREPOSITIONS),
                           "size": len(DESTINATION_PREPOSITIONS),
                           "cr_exemption": "CR 207.2d precedent -- the CR "
                                           "enumerates no English prepositions"},
        "structural_notes": {
            "overlap_nesting": "regions are cut at the next head's printed connector, "
                               "so legacy regions of one clause cannot overlap or "
                               "nest; the zero is by construction and is reported "
                               "so it is not read as a measurement that could have "
                               "come out otherwise",
            "paragraph_face": "a region is derived inside one chain clause, which "
                              "belongs to one paragraph of one face; paragraph- and "
                              "face-crossing are 0 by construction (as register #27 "
                              "notes for COST). A census clause crossing a chain "
                              "clause is refused and halts."},
        "cost_region_precedent": COST_PRECEDENT,
        "r4_cr_read": r4_cr_report(_r4cr()),
        "r4_expected_reach": r4_expected,
        "r4_corpus_reach": R4_CORPUS_REACH,
        "negative_controls": negative_controls(rows, c02, names,
                                               population[0]["oracle_id"]),
        "population_keys": [[r["oracle_id"], r["stem"], r["occurrence"]]
                            for r in population],
        "fixtures": fixture_out,
        "measurements": {"population": measure(pop), "fixtures": measure(fix),
                         "all": measure(ordered)},
        "clauses": ordered,
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
             if not (ROOT / rel).exists() or _sha(rel) != want]
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
    bad = portability_violations(runs[0])
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
    bad = portability_violations(data)
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
