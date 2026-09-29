#!/usr/bin/env python3
"""C03 — H-REGION candidate derivation and measurement (interface/1, V1 §5 M1).

Derives deterministic H-REGION CANDIDATES over the C03 population (interface/1
I2) and the frozen F0 fixtures, and measures them. It decides no kill: the
seven I3 tests read this output in `h_region_kill.py`. Read-only over the
corpus; writes one ignored JSON report.

INPUTS (a). The four interface/1 I1 identities are verified first; a differing
identity HALTS. The I2 population is re-derived with the frozen functions
(`foundry_qualifier_census.population`, `foundry_aq4_probes.effect_heads`)
and every I2 figure is reconciled against both interface/1's literals and the
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

# interface/1 I1 -- f0_select pins three; the accepted C02 output is the fourth.
C02_REL = "experiments/out/oracle_ingest/c02/all-run1.json"
I1 = dict(f0.PINNED)
I1[C02_REL] = "74e3559d785dc3ac47d14823ac1fec96dd446ae446d82a3ee45b03ef3f818dfd"

# oracle-compiler-interface/1, by git blob id (the wave's STOP condition).
INTERFACES_REL = "oracle_compiler/INTERFACES.md"
INTERFACES_BLOB = "3c34cf5a4e8150e43cbce2ec6a92e30272560f6e"
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

# interface/1 I2 -- the accepted C02 figures, every one of them.
I2 = dict(f0.C02, families={"exile": 60, "destroy": 6, "bounce": 0},
          examples=25)
I2.pop("p3_multi", None)
I2.pop("p3_qual", None)

# AQ4 register #27, CITED and not re-measured (interface/1 I2).
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
            fc.halt(f"pinned input {rel} is {got}, interface/1 pins {want}")
    return dict(sorted(pins.items()))


def verify_interface() -> str:
    got = _blob(INTERFACES_REL)
    if got != INTERFACES_BLOB:
        fc.halt(f"{INTERFACES_REL} is blob {got}, not oracle-compiler-interface/1 "
                f"({INTERFACES_BLOB})")
    return got


def reconcile(rows: list, c02: dict, want: dict = None) -> dict:
    """Every I2 figure, re-derived, against interface/1's literals AND the
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
    for label, ref in (("interface/1 I2", want), ("accepted C02 output", pinned)):
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
    {"id": "attach-ability-prefix", "kind": "attach", "cr": "CR 602.1a / 603.1",
     "pattern": "a span wholly before the first region governs every region"},
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


def derive_regions(text: str, lo: int, hi: int, owner: dict) -> tuple:
    """One region per legacy head of text[lo:hi]; offsets into `text`."""
    scope = text[lo:hi]
    heads = head_positions(scope)
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
    return regions, [dict(h, start=lo + h["start"], end=lo + h["end"],
                          connector=None if h["connector"] is None
                          else lo + h["connector"]) for h in heads]


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


def role_spans(text: str) -> tuple:
    """ATTACH-3 spans -- measurement labels only. Returns (spans, skipped),
    where `skipped` counts marks inside a quoted created ability (CR 113.2c /
    section 2 created-ability rule)."""
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
    if colon is not None:
        add("cost", "cost-colon", 0, colon)
    kw = aq._P2_KEYWORD.match(text)
    if kw and kw.group(1).strip().lower() in aq._CR702_KEYWORD_NAMES:
        add("cost", "cost-keyword-dash", kw.end(), len(text.rstrip(" .")))
    body = colon + 1 if colon is not None else 0
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


def attach(span: dict, regions: list) -> dict:
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
        return {"attached": every, "rule": "attach-ability-prefix",
                "outcome": "attached" if len(every) == 1 else "multiple",
                "reason": "" if len(every) == 1 else
                "an ability-prefix span governs every region of the clause"}
    return {"attached": [], "rule": None, "outcome": "none",
            "reason": "span lies outside every region and after the first"}


def clause_record(oid: str, fi: int, pi: int, ci: int, text: str, lo: int, hi: int,
                  scope_kind: str) -> dict:
    owner = {"oracle_id": oid, "face": fi, "paragraph": pi, "clause": ci,
             "id": f"{oid}:{fi}:{pi}:{ci}"}
    regions, legacy = derive_regions(text, lo, hi, owner)
    corrected = [dict(h, start=lo + h["start"], end=lo + h["end"],
                      connector=None if h["connector"] is None
                      else lo + h["connector"])
                 for h in head_positions(text[lo:hi], corrected=True)]
    spans, skipped = role_spans(text)
    for s in spans:
        s.update(attach(s, regions))
    lk = [(h["head"], h["start"]) for h in legacy]
    ck = [(h["head"], h["start"]) for h in corrected]
    counts = {}
    for h, _ in lk:
        counts[h] = counts.get(h, 0) + 1
    pairs = list(combinations(regions, 2))
    return {
        "address": owner, "clause_text": text,
        "clause_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "scope": [lo, hi], "scope_kind": scope_kind,
        "heads_legacy": legacy, "heads_corrected": corrected,
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

def measure(records: list) -> dict:
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
    for v in att.values():
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
        "legacy_vs_corrected": {
            "clauses_differing": sum(1 for c in records if c["detector_diff"]["differs"]),
            "clauses": ids(lambda c: c["detector_diff"]["differs"]),
            "note": "reported only; regions are derived from the legacy detector "
                    "and the corrected one is never substituted (interface/1 I2)"},
    }


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


def negative_controls(rows: list, c02: dict, names: list) -> list:
    """Each guard this script contracts, shown to fire on a rigged input."""
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
    ]
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
            rec = clause_record(oid, fi, pi, ci, text, lo, hi, kind)
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
    inputs = {rel: _sha(rel) for rel in INPUTS}
    return {
        "schema": "oracle-compiler-c03-regions/0",
        "interface": {"version": "oracle-compiler-interface/1",
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
        "negative_controls": negative_controls(rows, c02, names),
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
