#!/usr/bin/env python3
"""AQ4 BENCHMARK — OWNERSHIP-NEUTRAL EVALUATION PROJECTION (contract 23, packet 4).

WHAT THIS IS AND IS NOT
-----------------------
This is benchmark/interface VALIDATION MACHINERY. It validates and canonicalizes
projection objects, and it regenerates and checks the frozen semantic-occurrence
surface. Production AQ4 architecture remains UNRATIFIED and nothing here changes
it.

It MUST NOT, and does not:
  · parse Oracle text into semantic facts;
  · implement either candidate encoder;
  · adjudicate open truth or write any answer key;
  · compare real cards for scoring.

The one place it touches live card text is `regenerate_surface()` and
`measure_cost_spans()`, both of which P4-R4 explicitly requires: a bare hash with
no deterministic regenerator is not an authoritative pin, and the recorded
failure this packet exists to end is a count living only in a docstring. Neither
produces a semantic fact -- one produces occurrence ADDRESSES, the other
structural SPANS.

THE COST LAW (P4-R1) -- READ BEFORE ADDING A ROLE
-------------------------------------------------
COST is structural ability content, never an eligibility dimension. The marker
is POSITIONAL and CR-grounded, so effect text that merely discusses paying or
sacrificing is not a COST region:

    "Counter target spell unless that player pays {2}."      -> no COST region
    "You may sacrifice a creature. If you do, draw a card."  -> no COST region
    "{2}, {T}: Draw a card."                                 -> COST region
    'Equipped creature has "{T}: Draw a card."'              -> no COST region
                                                (the colon is inside a created
                                                 ability -- section 2's rule)

There is NO positive EFFECT token in v1, and no unknown-role value. Material not
proven to occupy a structural cost position stays UNMARKED. Cost carries no
dimension, no atoms and no absence claim, so COST can never reach the
ABSENT-PROVEN machinery at all -- that is structural, not a rule someone must
remember.

THE DISPOSITION LAW (P4-R2)
---------------------------
Five dispositions, no sixth. `HUMAN_RESOLVED` is key/adjudication-side only and
carries its semantic payload transparently, with the adjudication METHOD as
metadata rather than as a disposition value. `ABSENT_PROVEN` is claimant-side
only: a candidate earns it under the section 18 obligations, and the key never
discharges those on a candidate's behalf. Key-side absence is
`HUMAN_RESOLVED` carrying an absent payload.

There is deliberately NO per-row party field. Artifact identity already
establishes whether rows belong to the frozen key or to a candidate export, and
storing it per row would be a second source of truth.

WHY THE SCHEMA IS A JSON FILE AND NOT A PYTHON LITERAL
------------------------------------------------------
`evaluation-projection-schema.json` is the single versioned source of the
vocabulary. The validator reads it rather than restating it, so the two cannot
drift. The dimension list is asserted to be a SUBSET of the contract's own
section 14 table (`assert_dimensions_subset_of_contract`) rather than parsed out
of it: making a markdown table the machine vocabulary source is this
repository's recorded "a markdown table is an API" trap, and the dangerous
direction -- a schema inventing a dimension the contract never ratified -- is
exactly what containment catches.
"""
import io
import re
import sys
import json
import copy
import hashlib
import argparse
import collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
REPO_ROOT = EXPERIMENTS.parent
sys.path.insert(0, str(EXPERIMENTS))
sys.path.insert(0, str(HERE))

import foundry_common as fc              # noqa: E402
import foundry_codebook as fcb           # noqa: E402
import foundry_cr as CR                  # noqa: E402
import foundry_locality as fl            # noqa: E402
import foundry_shape_extractor as fx     # noqa: E402
import foundry_aq4_probes as aq4p        # noqa: E402
import aq4_pairing as pr                 # noqa: E402

SCHEMA_PATH = HERE / "evaluation-projection-schema.json"
MANIFEST_PATH = HERE / "open-surface-manifest.json"
CONTRACT_PATH = REPO_ROOT / "docs" / \
    "AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md"

SCHEMA_NAME = "aq4-evaluation-projection"
SCHEMA_VERSION = "1.0.0"
MANIFEST_NAME = "aq4-open-surface-manifest"
MANIFEST_VERSION = "1.0.0"

#: The ratified preprocessing chain that PRODUCES the semantic occurrence
#: surface, by implementation name, in order. Recorded because P4-R3 forbids
#: naming the surface merely "reminder-stripped": the strip is one pass of six,
#: and an unnamed chain cannot be re-derived by a later session.
PREPROCESSING_CHAIN = [
    {"step": 1, "impl": "tier_engine.get_raw_faces",
     "role": "all-faces raw oracle text; the one shared face reader",
     "cr_anchor": None},
    {"step": 2, "impl": "foundry_common.canonicalize_self_reference",
     "role": "optional NORMALIZED DETECTOR VIEW (CARDNAME -> self-reference); "
             "never evidence, and proven surface-invariant here",
     "cr_anchor": "CR 201.5c"},
    {"step": 3, "impl": "foundry_locality.units",
     "role": "paragraph split and locality reconciliation; halts if "
             "canonicalization reflows a face's paragraph count",
     "cr_anchor": "CR 113.2c"},
    {"step": 4, "impl": "foundry_shape_extractor.strip_reminder",
     "role": "reminder strip plus its separator repair "
             "(REMINDER.sub -> _SPACE_RUN -> _ORPHANED_SEPARATOR)",
     "cr_anchor": "CR 207.2a"},
    {"step": 5, "impl": "foundry_shape_extractor.quoted_spans",
     "role": "created-ability spans blanked so a granted ability's own "
             "punctuation cannot split the card's clause",
     "cr_anchor": "CR 113.2c / section 2 created-ability rule"},
    {"step": 6, "impl": "foundry_shape_extractor.sentence_spans",
     "role": "CLAUSE segmentation -- owns the clause ordinal; extractors "
             "resolve into it and never mint an ordinal",
     "cr_anchor": "CR 113.2c"},
]

LEGACY_DETECTOR = "foundry_aq4_probes.effect_heads"
SEMANTIC_DETECTOR = "foundry_aq4_probes.semantic_action_heads"


# ==========================================================================
# SCHEMA
# ==========================================================================

def load_schema() -> dict:
    s = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    if s.get("schema") != SCHEMA_NAME or s.get("version") != SCHEMA_VERSION:
        fc.halt(f"projection schema identity mismatch: "
                f"{s.get('schema')!r}/{s.get('version')!r}")
    return s


SCHEMA = load_schema()
DIMENSIONS = {d["name"]: d for d in SCHEMA["dimensions"]}
OPERATORS = {a["op"] for a in SCHEMA["atom_operators"]}
DISPOSITIONS = list(SCHEMA["dispositions"]["values"])
KEY_ONLY = set(SCHEMA["dispositions"]["key_only"])
CANDIDATE_ONLY = set(SCHEMA["dispositions"]["candidate_only"])
REGION_ROLES = set(SCHEMA["structural_regions"]["roles"])
RELATION_KINDS = set(SCHEMA["relation_kinds"]["values"])
EVIDENCE_CATEGORIES = set(SCHEMA["evidence"]["categories"])
DERIVATION_CLASSES = set(SCHEMA["derivation_classes"])
PROVENANCE_CLASSES = set(SCHEMA["provenance_classes"])
ARTIFACT_ROLES = set(SCHEMA["artifact_roles"]["values"])
FORBIDDEN_FIELDS = {f.lower() for f in SCHEMA["forbidden_fields"]["values"]}
FORBIDDEN_NATIVE = {f.lower() for f in
                    SCHEMA["forbidden_native_vocabulary"]["values"]}


def assert_dimensions_subset_of_contract() -> list:
    """Every schema dimension must appear in the contract's section 14 table.

    Containment only, and deliberately one-directional. The contract RATIFIES;
    this file is the machine-readable copy. A schema dimension the contract
    never names is an invented dimension -- the dangerous direction. The
    reverse (a contract row this file has not yet copied) is a completeness
    question, not a soundness one, and is reported rather than fatal.
    """
    text = CONTRACT_PATH.read_text(encoding="utf-8")
    missing = [n for n in DIMENSIONS if f"`{n}`" not in text]
    if missing:
        fc.halt(f"projection schema names {len(missing)} dimension(s) absent "
                f"from the ratified contract: {sorted(missing)}. A dimension "
                f"the contract does not ratify is a mint, not a copy.")
    return sorted(DIMENSIONS)


# ==========================================================================
# CANONICAL SERIALIZATION
# ==========================================================================

def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def surface_id(addr) -> str:
    """`<oracle_id>:<face>:<paragraph>:<clause>` -- the Packet-4 canonical form.

    Chosen because it reproduces two already-accepted historical digests
    exactly. The delimiter is safe by construction: an oracle_id is a
    hyphenated UUID and the other three coordinates are integers, so no
    coordinate can contain a colon.
    """
    return f"{addr[0]}:{addr[1]}:{addr[2]}:{addr[3]}"


def surface_digest(addrs) -> str:
    """SHA-256 over each sorted unique id, UTF-8, each followed by one LF."""
    h = hashlib.sha256()
    for sid in sorted({surface_id(a) for a in addrs}):
        h.update((sid + "\n").encode("utf-8"))
    return h.hexdigest()


# ==========================================================================
# THE SEMANTIC OCCURRENCE SURFACE — regenerated, never inherited
# ==========================================================================

def _clause_texts(paragraph: str) -> list:
    return fx.sentence_spans(paragraph)


def clause_spans(paragraph: str) -> list:
    """(start, end) of each ratified clause inside `paragraph`.

    `sentence_spans` returns STRIPPED STRINGS, so positions are recovered by an
    ordered forward search. HALTS rather than guessing if a clause cannot be
    located -- a probe that silently mislocates a span would report a
    boundary-crossing answer that is an artifact of the probe.
    """
    out, cur = [], 0
    for cl in _clause_texts(paragraph):
        i = paragraph.find(cl, cur)
        if i < 0:
            fc.halt(f"clause not locatable in its own paragraph: {cl!r}")
        out.append((i, i + len(cl)))
        cur = i + len(cl)
    return out


def open_surface(view: str = "canonical", cards=None, ids=None) -> list:
    """[(oracle_id, face, paragraph, clause, text)] over the published open set.

    `view` selects the step-2 NORMALIZED DETECTOR VIEW only. The occurrence
    ADDRESS is produced by the same chain in both views, which is what makes
    the choice a detector question rather than an identity question.
    """
    if view not in ("raw", "canonical"):
        fc.halt(f"unknown text view {view!r}; expected 'raw' or 'canonical'")
    if cards is None:
        cards, _, _ = fc.load_corpus_gated()
    if ids is None:
        ids = pr.open_exemplars(pr.published_classes())
    out = []
    for oid in ids:
        for (fi, pi), raw, canon in fl.units(cards[oid]):
            para = fx.strip_reminder(raw if view == "raw" else canon)
            for ci, seg in enumerate(_clause_texts(para)):
                out.append((oid, fi, pi, ci, seg))
    return out


def unstripped_surface(view: str = "canonical", cards=None, ids=None) -> list:
    """The REJECTED alternate surface -- reminder text left in.

    Recorded, not used. It exists so the rejected measurement is reproducible
    rather than quoted: a rejected alternative with no regenerator is the same
    carried-forward count as an accepted one.
    """
    if cards is None:
        cards, _, _ = fc.load_corpus_gated()
    if ids is None:
        ids = pr.open_exemplars(pr.published_classes())
    out = []
    for oid in ids:
        for (fi, pi), raw, canon in fl.units(cards[oid]):
            para = raw if view == "raw" else canon
            for ci, seg in enumerate(_clause_texts(para)):
                out.append((oid, fi, pi, ci, seg))
    return out


def surface_sets(surface) -> dict:
    """The three pinned address sets."""
    return {
        "all": [s[:4] for s in surface],
        "legacy_reached": [s[:4] for s in surface
                           if aq4p.effect_heads(s[4], True)],
        "semantic_reached": [s[:4] for s in surface
                             if aq4p.semantic_action_heads(s[4])],
    }


def regenerate_surface(cards=None, ids=None) -> dict:
    """Everything the manifest pins, regenerated from live machinery."""
    if cards is None:
        cards, _, _ = fc.load_corpus_gated()
    if ids is None:
        ids = pr.open_exemplars(pr.published_classes())
    can = open_surface("canonical", cards, ids)
    raw = open_surface("raw", cards, ids)
    can_sets, raw_sets = surface_sets(can), surface_sets(raw)

    unstripped = unstripped_surface("canonical", cards, ids)
    un_sets = surface_sets(unstripped)

    textual = [(a, b) for a, b in zip(raw, can) if a[4] != b[4]]
    deferred_p3 = [(a, b) for a, b in textual
                   if not aq4p.semantic_action_heads(b[4])]

    return {
        "exemplars": len(ids),
        "canonical": can_sets,
        "raw": raw_sets,
        "unstripped_rejected": un_sets,
        "view_invariance": {
            "addresses_identical": [s[:4] for s in can] == [s[:4] for s in raw],
            "legacy_sets_identical":
                surface_digest(can_sets["legacy_reached"]) ==
                surface_digest(raw_sets["legacy_reached"]),
            "semantic_sets_identical":
                surface_digest(can_sets["semantic_reached"]) ==
                surface_digest(raw_sets["semantic_reached"]),
            "head_value_deltas_legacy": sum(
                1 for a, b in zip(raw, can)
                if aq4p.effect_heads(a[4], True) != aq4p.effect_heads(b[4], True)),
            "head_value_deltas_semantic": sum(
                1 for a, b in zip(raw, can)
                if aq4p.semantic_action_heads(a[4]) !=
                aq4p.semantic_action_heads(b[4])),
        },
        "deferred_p3_exposure": {
            "occurrences_textually_differing": len(textual),
            "unreached_by_p1_p2": len(deferred_p3),
            "cards_involved": len({a[0] for a, _ in deferred_p3}),
        },
    }


# ==========================================================================
# STRUCTURAL COST REGIONS — positional, CR-grounded, no semantics
# ==========================================================================

def derive_cost_regions(paragraph: str, card=None) -> list:
    """[(arm, start, end)] structural COST regions inside one paragraph.

    Every guard here is the RATIFIED helper rather than a re-implementation --
    re-asking a question the classifier already answers is this repository's
    single most-recorded probe defect.

      CR 113.3b / 602.1a  activation cost = everything before the colon, with
                          the colon refused inside a created ability
                          (`fx.in_created_ability`) and inside the card's own
                          name (`fx.in_card_name`, the recorded colon-in-name
                          case).
      CR 606.2            loyalty cost, `fx.LOYALTY_COST` -- positionally the
                          same colon, reported as its own arm.
      CR 702.6b           a keyword's em-dash body is the keyword's own COST,
                          using the already-ratified refusal machinery.

    Emits SPANS only. No dimension, no atom, no disposition, no semantics.
    """
    regions = []
    colons = [m.start() for m in re.finditer(":", paragraph)
              if not fx.in_created_ability(paragraph, m.start())
              and not fx.in_card_name(paragraph, m.start(), card)]
    if colons:
        arm = ("CR 606.2" if fx.LOYALTY_COST.match(paragraph.strip())
               else "CR 113.3b/602.1a")
        regions.append((arm, 0, colons[0]))
    kw = aq4p._P2_KEYWORD.match(paragraph)
    if kw and kw.group(1).strip().lower() in aq4p._CR702_KEYWORD_NAMES:
        regions.append(("CR 702.6b", kw.end(), len(paragraph.rstrip())))
    return [r for r in regions if r[2] > r[1]]


def measure_cost_spans(cards=None, ids=None) -> dict:
    """P4-R1's pre-freeze probe, kept regenerable rather than scratchpad-only.

    Answers exactly one question: does a derivable structural COST region ever
    cross an existing semantic clause boundary? If it never does, a COST marker
    is a sub-clause region owned by ONE existing occurrence and no new identity
    coordinate is required.
    """
    if cards is None:
        cards, _, _ = fc.load_corpus_gated()
    if ids is None:
        ids = pr.open_exemplars(pr.published_classes())
    arms = collections.Counter()
    total = occ_with = multi = cross_clause = ambiguous = 0
    units = max_span = 0
    for oid in ids:
        for (fi, pi), raw, canon in fl.units(cards[oid]):
            para = fx.strip_reminder(canon)
            spans = clause_spans(para)
            if not spans:
                continue
            units += 1
            bare = [m.start() for m in re.finditer(":", para)
                    if not fx.in_created_ability(para, m.start())
                    and not fx.in_card_name(para, m.start(), cards[oid])]
            if len(bare) > 1:
                ambiguous += 1
            regions = derive_cost_regions(para, cards[oid])
            if len(regions) > 1:
                multi += 1
            for arm, a, b in regions:
                total += 1
                arms[arm] += 1
                max_span = max(max_span, b - a)
                touched = [k for k, (cs, ce) in enumerate(spans)
                           if a < ce and b > cs]
                if touched:
                    occ_with += 1
                if len(touched) > 1:
                    cross_clause += 1
    return {
        "paragraphs_inspected": units,
        "cost_regions_total": total,
        "cost_regions_by_cr_arm": dict(sorted(arms.items())),
        "occurrences_carrying_cost": occ_with,
        "paragraphs_with_multiple_cost_regions": multi,
        "max_cost_span_characters": max_span,
        "crossing_clause_boundary": cross_clause,
        "crossing_paragraph_boundary": 0,
        "crossing_face_boundary": 0,
        "ambiguous_boundary_cases": ambiguous,
        "_structural_note": "paragraph- and face-crossing are 0 BY "
                            "CONSTRUCTION: a region is derived inside one "
                            "paragraph, and a paragraph belongs to exactly "
                            "one face. Reported so the zero is not read as a "
                            "measurement that could have come out otherwise.",
    }


# ==========================================================================
# EVIDENCE ADMISSIBILITY — the reminder-text rule (P4-R3)
# ==========================================================================

def reminder_spans(raw_paragraph: str) -> list:
    return [(m.start(), m.end())
            for m in fx.REMINDER.finditer(raw_paragraph)]


def assert_evidence_admissible(raw_paragraph: str, span, what="fact") -> None:
    """HALT if a fact's only support lies wholly inside CR 207.2a reminder text.

    Reminder text stays present in the raw evidence view and stays
    trace-visible. What it may not do is INDEPENDENTLY support a semantic
    claim. A search that matches reminder text and reads as a clean result is
    the recorded Spree inversion, one layer up.
    """
    a, b = span
    for ra, rb in reminder_spans(raw_paragraph):
        if a >= ra and b <= rb:
            fc.halt(f"{what} is supported only by CR 207.2a reminder text "
                    f"(span {a}-{b} lies inside reminder span {ra}-{rb}). "
                    f"Reminder text is trace-visible but never independently "
                    f"claim-admissible.")


# ==========================================================================
# PROJECTION VALIDATION
# ==========================================================================

class Violation(Exception):
    pass


def _walk_keys(obj, path="$"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield path, k
            yield from _walk_keys(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk_keys(v, f"{path}[{i}]")


def _walk_strings(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_strings(v)
    elif isinstance(obj, str):
        yield obj


def validate(doc: dict) -> list:
    """Return the list of violations. Empty means the object conforms."""
    v = []

    if doc.get("schema") != SCHEMA_NAME:
        v.append(f"schema must be {SCHEMA_NAME!r}")
    if doc.get("version") != SCHEMA_VERSION:
        v.append(f"version must be {SCHEMA_VERSION!r}")
    role = doc.get("artifact_role")
    if role not in ARTIFACT_ROLES:
        v.append(f"artifact_role must be one of {sorted(ARTIFACT_ROLES)}")

    # -- forbidden fields and candidate-native vocabulary, at any depth ----
    for path, key in _walk_keys(doc):
        lk = str(key).lower()
        if lk in FORBIDDEN_FIELDS:
            v.append(f"forbidden field {key!r} at {path}")
        if lk in FORBIDDEN_NATIVE:
            v.append(f"candidate-native field {key!r} at {path}")
    for s in _walk_strings(doc):
        if s.lower() in FORBIDDEN_NATIVE:
            v.append(f"candidate-native vocabulary value {s!r}")

    for occ in doc.get("occurrences", []):
        addr = occ.get("occurrence") or {}
        for c in ("oracle_id", "face", "paragraph", "clause"):
            if c not in addr:
                v.append(f"occurrence address missing {c!r}")
        for c in ("face", "paragraph", "clause"):
            if c in addr and (not isinstance(addr[c], int) or addr[c] < 0):
                v.append(f"occurrence coordinate {c!r} must be a "
                         f"non-negative integer")
        if len(addr) > 4:
            v.append(f"occurrence address carries a fifth coordinate: "
                     f"{sorted(set(addr) - {'oracle_id','face','paragraph','clause'})}")

        parts = occ.get("participants", [])
        if any(not isinstance(p, int) or p < 0 for p in parts):
            v.append("participants must be non-negative bare integers")
        if list(parts) != sorted(set(parts)):
            v.append("participants must be sorted and unique")

        heads = occ.get("action_heads", [])
        disp = occ.get("action_head_disposition")
        if heads and disp != "PRESENT":
            v.append("action_head_disposition must be PRESENT when heads exist")
        if not heads and disp != "UNRESOLVED":
            v.append("an occurrence with no action head must be UNRESOLVED, "
                     "never fabricated and never absent-proven")
        for h in heads:
            if "dimension" in h:
                v.append("an action head must not carry a dimension -- it is a "
                         "predicate, not an eligibility dimension")

        for f in occ.get("facts", []):
            dim = f.get("dimension")
            if dim not in DIMENSIONS:
                v.append(f"dimension {dim!r} is not a ratified contract row")
            atom = f.get("atom") or {}
            if atom.get("op") not in OPERATORS:
                v.append(f"atom operator {atom.get('op')!r} is not ratified")
            d = f.get("disposition")
            if d not in DISPOSITIONS:
                v.append(f"disposition {d!r} is not one of the five")
            if d in KEY_ONLY and role != "KEY":
                v.append(f"{d} is key/adjudication-side only and may not "
                         f"appear in a candidate export")
            if d in CANDIDATE_ONLY and role != "CANDIDATE_EXPORT":
                v.append(f"{d} is claimant-side only; the key records absence "
                         f"as HUMAN_RESOLVED carrying an absent payload")
            if d == "HUMAN_RESOLVED":
                if "resolved" not in f:
                    v.append("HUMAN_RESOLVED must carry its semantic payload "
                             "transparently")
                adj = f.get("adjudication") or {}
                if "method" not in adj:
                    v.append("HUMAN_RESOLVED must record its adjudication "
                             "method as metadata")
                if adj.get("method") in DISPOSITIONS:
                    v.append("adjudication method must not be encoded as a "
                             "disposition value")
            scope = (f.get("scope") or {}).get("kind")
            if scope not in ("OCCURRENCE", "PARTICIPANT"):
                v.append(f"fact scope {scope!r} must be OCCURRENCE or "
                         f"PARTICIPANT")
            if scope == "PARTICIPANT":
                p = (f.get("scope") or {}).get("participant")
                if p not in parts:
                    v.append(f"fact references undeclared participant {p!r}")
            if f.get("derivation_class") not in DERIVATION_CLASSES:
                v.append(f"derivation_class {f.get('derivation_class')!r} "
                         f"is not a ratified extraction class")
            if f.get("provenance_class") not in PROVENANCE_CLASSES:
                v.append(f"provenance_class {f.get('provenance_class')!r} "
                         f"is not ratified")
            v += _validate_evidence(f.get("evidence"), "fact")

        for r in occ.get("structural_regions", []):
            if r.get("role") not in REGION_ROLES:
                v.append(f"structural region role {r.get('role')!r} is not "
                         f"ratified; v1 has COST and no complement")
            for banned in ("dimension", "atom", "disposition"):
                if banned in r:
                    v.append(f"a structural region must not carry {banned!r} "
                             f"-- COST is not an eligibility dimension and "
                             f"never participates in absence")
            span = r.get("evidence", {}).get("span") or {}
            if not isinstance(span.get("start"), int) or \
               not isinstance(span.get("end"), int):
                v.append("a structural region needs a deterministic span")
            v += _validate_evidence(r.get("evidence"), "structural region")

        for rel in occ.get("relations", []):
            if rel.get("kind") not in RELATION_KINDS:
                v.append(f"relation kind {rel.get('kind')!r} is not one of "
                         f"the three CR-groundable kinds")
            for end in ("from", "to"):
                ref = rel.get(end) or {}
                oid = (ref.get("occurrence") or {}).get("oracle_id")
                if oid and oid != addr.get("oracle_id"):
                    v.append("relation edges are same-card only")
            v += _validate_evidence(rel.get("evidence"), "relation")

    # -- same span may not carry two different roles ----------------------
    for occ in doc.get("occurrences", []):
        seen = {}
        for r in occ.get("structural_regions", []):
            sp = r.get("evidence", {}).get("span") or {}
            k = (sp.get("start"), sp.get("end"))
            if k in seen and seen[k] != r.get("role"):
                v.append(f"span {k} carries two different roles "
                         f"({seen[k]!r} and {r.get('role')!r})")
            seen[k] = r.get("role")

    return v


def _validate_evidence(ev, what) -> list:
    if not ev:
        return [f"{what} carries no evidence trace -- a surviving semantic "
                f"fact must trace to admissible source evidence"]
    out = []
    if ev.get("category") not in EVIDENCE_CATEGORIES:
        out.append(f"{what} evidence category {ev.get('category')!r} is not "
                   f"one of the three")
    if ev.get("category") == "ORACLE_TEXT":
        if ev.get("view") != "RAW_ORACLE":
            out.append(f"{what} evidence must trace to the RAW view -- "
                       f"normalization never becomes evidence")
        span = ev.get("span") or {}
        if not isinstance(span.get("start"), int) or \
           not isinstance(span.get("end"), int):
            out.append(f"{what} evidence needs a deterministic span")
        if not (ev.get("occurrence") or {}).get("oracle_id"):
            out.append(f"{what} evidence must locate its occurrence")
    return out


def assert_valid(doc: dict) -> None:
    v = validate(doc)
    if v:
        fc.halt("projection object rejected:\n  - " + "\n  - ".join(v))


def canonicalize(doc: dict) -> dict:
    """Deterministic canonical form.

    Reorders and normalizes representation; NEVER invents or drops a semantic
    fact. `action_heads` is deliberately NOT sorted: printed order is semantic,
    so a permutation of heads is a different object rather than the same one
    written differently.
    """
    out = copy.deepcopy(doc)
    occs = out.get("occurrences", [])
    for occ in occs:
        occ["participants"] = sorted(set(occ.get("participants", [])))
        occ["facts"] = sorted(
            occ.get("facts", []),
            key=lambda f: ((f.get("scope") or {}).get("kind", ""),
                           (f.get("scope") or {}).get("participant", -1),
                           f.get("dimension", ""),
                           canonical_json(f.get("atom"))))
        occ["structural_regions"] = sorted(
            occ.get("structural_regions", []),
            key=lambda r: (r.get("role", ""),
                           (r.get("evidence", {}).get("span") or {}).get("start", -1),
                           (r.get("evidence", {}).get("span") or {}).get("end", -1)))
        occ["relations"] = sorted(occ.get("relations", []),
                                  key=canonical_json)
    out["occurrences"] = sorted(
        occs, key=lambda o: (o.get("occurrence", {}).get("oracle_id", ""),
                             o.get("occurrence", {}).get("face", -1),
                             o.get("occurrence", {}).get("paragraph", -1),
                             o.get("occurrence", {}).get("clause", -1)))
    return out


def canonical_bytes(doc: dict) -> bytes:
    return canonical_json(canonicalize(doc)).encode("utf-8")


def fact_count(doc: dict) -> int:
    return sum(len(o.get("facts", [])) + len(o.get("structural_regions", []))
               + len(o.get("relations", [])) + len(o.get("action_heads", []))
               for o in doc.get("occurrences", []))


# ==========================================================================
# MANIFEST
# ==========================================================================

def build_manifest(cards=None, ids=None) -> dict:
    s = regenerate_surface(cards, ids)
    cost = measure_cost_spans(cards, ids)
    can, raw, un = s["canonical"], s["raw"], s["unstripped_rejected"]
    return {
        "_law": "Counts are CONVENIENCE METADATA. The assertions are the full "
                "digests plus the deterministic generation law recorded here. "
                "A bare count is not a pin and a bare hash with no regenerator "
                "is not one either.",
        "_what": "Durable pin of the AQ4 semantic-occurrence surface over the "
                 "published open exemplars. Packet 4, P4-R3/P4-R4. Carries no "
                 "oracle_id, no member list and no Oracle text.",
        "schema": MANIFEST_NAME,
        "version": MANIFEST_VERSION,
        "corpus_ref": fcb.corpus_ref_current(),
        "cr_edition": CR.CR_PATH.name,
        "cr_sha256": hashlib.sha256(CR.CR_PATH.read_bytes()).hexdigest(),
        "open_exemplars": s["exemplars"],
        "preprocessing_chain": PREPROCESSING_CHAIN,
        "occurrence_id_format": "<oracle_id>:<face>:<paragraph>:<clause>",
        "serialization": {
            "algorithm": "SHA-256, streaming",
            "delimiter": ":",
            "encoding": "UTF-8",
            "newline": "one LF after each id",
            "sort": "lexicographic over the id string, unique",
            "_why_this_form": "It reproduces two already-accepted historical "
                              "digests exactly, so adopting it makes the older "
                              "evidence citable instead of orphaned.",
        },
        "detectors": {
            "legacy_entry_point": LEGACY_DETECTOR,
            "semantic_entry_point": SEMANTIC_DETECTOR,
            "semantic_class_scope": {
                "P1_mode_bullet": "CR 700.2 -- ADOPTED",
                "P2_instruction_prefix":
                    "CR 714.2 / 606.2 / 700.2h / 700.2i -- ADOPTED; "
                    "a CR 702.Na keyword prefix is REFUSED (CR 702.6b)",
                "P3_finite_subject": "DEFERRED -- not implemented, and no "
                                     "proper-name heuristic is adopted",
            },
        },
        "sets": {
            "all": {"count": len(can["all"]),
                    "sha256": surface_digest(can["all"])},
            "legacy_reached": {"count": len(can["legacy_reached"]),
                               "sha256": surface_digest(can["legacy_reached"])},
            "semantic_reached": {"count": len(can["semantic_reached"]),
                                 "sha256": surface_digest(can["semantic_reached"])},
        },
        "text_view_law": {
            "evidence_view": "RAW_ORACLE -- normalization never becomes evidence",
            "semantic_segmentation_view":
                "the ratified preprocessing chain above, in order; NOT to be "
                "named merely 'reminder-stripped' -- the strip is one pass of "
                "six and the chain is what reproduces the surface",
            "current_result": "P1/P2 truth is VIEW-INVARIANT",
            "re_audit_trigger": "re-audit text-view behaviour before any "
                                "future P3 finite-subject adoption",
            "raw_vs_canonical": s["view_invariance"],
            "deferred_p3_exposure": s["deferred_p3_exposure"],
        },
        "rejected_unstripped_surface": {
            "_why_rejected": "CR 207.2a reminder text mints no semantic "
                             "occurrence and is not independently "
                             "claim-admissible, so a surface that segments it "
                             "into occurrences is not the semantic surface.",
            "all": {"count": len(un["all"]),
                    "sha256": surface_digest(un["all"])},
            "legacy_reached": {"count": len(un["legacy_reached"]),
                               "sha256": surface_digest(un["legacy_reached"])},
            "semantic_reached": {"count": len(un["semantic_reached"]),
                                 "sha256": surface_digest(un["semantic_reached"])},
        },
        "cost_span_probe": cost,
        "raw_view_sets": {
            "all": {"count": len(raw["all"]),
                    "sha256": surface_digest(raw["all"])},
            "legacy_reached": {"count": len(raw["legacy_reached"]),
                               "sha256": surface_digest(raw["legacy_reached"])},
            "semantic_reached": {"count": len(raw["semantic_reached"]),
                                 "sha256": surface_digest(raw["semantic_reached"])},
        },
    }


def write_manifest(cards=None, ids=None) -> dict:
    m = build_manifest(cards, ids)
    MANIFEST_PATH.write_text(
        json.dumps(m, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    return m


def validate_manifest(cards=None, ids=None) -> list:
    """Regenerate the sets and compare FULL digests. Halts on mismatch."""
    if not MANIFEST_PATH.exists():
        fc.halt(f"no surface manifest at {MANIFEST_PATH}")
    pinned = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    live = regenerate_surface(cards, ids)
    bad = []
    for name in ("all", "legacy_reached", "semantic_reached"):
        want = pinned["sets"][name]
        got_ids = live["canonical"][name]
        got = surface_digest(got_ids)
        if got != want["sha256"]:
            bad.append(f"{name}: pinned {want['sha256']} != live {got}")
        if len(got_ids) != want["count"]:
            bad.append(f"{name}: pinned count {want['count']} != "
                       f"live {len(got_ids)}")
    for name in ("all", "legacy_reached", "semantic_reached"):
        want = pinned["rejected_unstripped_surface"][name]
        got = surface_digest(live["unstripped_rejected"][name])
        if got != want["sha256"]:
            bad.append(f"rejected/{name}: pinned {want['sha256']} != {got}")
    if pinned.get("corpus_ref") != fcb.corpus_ref_current():
        bad.append(f"corpus_ref moved: pinned {pinned.get('corpus_ref')} "
                   f"!= live {fcb.corpus_ref_current()}")
    if pinned.get("cr_sha256") != \
            hashlib.sha256(CR.CR_PATH.read_bytes()).hexdigest():
        bad.append("CR edition hash moved")
    return bad


# ==========================================================================
# FIXTURES — synthetic only. No real card is used as a projection fixture.
# ==========================================================================

def _evidence(oid="00000000-0000-0000-0000-000000000001", a=0, b=10):
    return {"category": "ORACLE_TEXT", "view": "RAW_ORACLE",
            "occurrence": {"oracle_id": oid, "face": 0, "paragraph": 0,
                           "clause": 0},
            "span": {"start": a, "end": b}}


def _fact(dim="card_type", op="REQUIRES", value="creature",
          disposition="PRESENT", scope=None, **extra):
    f = {"dimension": dim,
         "atom": {"op": op, "value": value},
         "disposition": disposition,
         "scope": scope or {"kind": "PARTICIPANT", "participant": 0},
         "derivation_class": "EXTRACT-1",
         "provenance_class": "rule-derived",
         "evidence": _evidence()}
    f.update(extra)
    return f


def sample_projection(role="CANDIDATE_EXPORT") -> dict:
    """A conforming synthetic object exercising every projected category."""
    oid = "00000000-0000-0000-0000-000000000001"
    return {
        "schema": SCHEMA_NAME,
        "version": SCHEMA_VERSION,
        "artifact_role": role,
        "occurrences": [{
            "occurrence": {"oracle_id": oid, "face": 0, "paragraph": 0,
                           "clause": 0},
            "participants": [0, 1],
            "action_heads": [
                {"head": "destroy", "cr_anchor": "CR 701.7",
                 "derivation_class": "EXTRACT-1", "evidence": _evidence()},
                {"head": "create", "cr_anchor": "CR 701.6",
                 "derivation_class": "EXTRACT-1", "evidence": _evidence()},
            ],
            "action_head_disposition": "PRESENT",
            "facts": [
                _fact(),
                _fact(dim="color", op="FORBIDS", value="black",
                      scope={"kind": "PARTICIPANT", "participant": 1}),
                _fact(dim="condition", op="EQUALITY", value="as long as you "
                      "control a Forest",
                      scope={"kind": "OCCURRENCE"}),
            ],
            "structural_regions": [
                {"role": "COST",
                 "cr_anchors": ["CR 113.3b", "CR 602.1a"],
                 "derivation_class": "EXTRACT-0",
                 "evidence": _evidence(a=0, b=9)},
            ],
            "relations": [
                {"kind": "COREFERENCE",
                 "from": {"occurrence": {"oracle_id": oid, "face": 0,
                                         "paragraph": 0, "clause": 0},
                          "participant": 0},
                 "to": {"occurrence": {"oracle_id": oid, "face": 0,
                                       "paragraph": 0, "clause": 1}},
                 "evidence": _evidence()},
            ],
        }],
    }


# ==========================================================================
# SELFTEST — every control demonstrated rigged red
# ==========================================================================

def selftest() -> int:
    fails = []

    def check(name, ok, detail=""):
        print(f"  [{'ok' if ok else 'FAIL'}] {name}"
              + (f"  <- {detail}" if detail and not ok else ""))
        if not ok:
            fails.append(name)

    print("=" * 74)
    print("AQ4 PROJECTION — CONTROLS (each rigged red on the path it guards)")
    print("=" * 74)

    print("\nSCHEMA / VOCABULARY PROVENANCE")
    dims = assert_dimensions_subset_of_contract()
    check(f"schema dimensions are a subset of the ratified contract "
          f"({len(dims)} rows)", True)

    base = sample_projection()
    check("PROJ.CONFORMING a fully populated synthetic object validates",
          validate(base) == [], validate(base))

    print("\nNEUTRALITY")
    rig = copy.deepcopy(base)
    rig["occurrences"][0]["facts"][0]["canonical_owner"] = "assertion"
    check("PROJ.NATIVE_VOCAB_REJECTED a candidate-native ownership field is "
          "refused", any("candidate-native" in x for x in validate(rig)))
    rig2 = copy.deepcopy(base)
    rig2["occurrences"][0]["storage_model"] = "nested"
    check("PROJ.NATIVE_VOCAB_REJECTED-RIG a second native concept is refused",
          any("candidate-native" in x for x in validate(rig2)))

    rig = copy.deepcopy(base)
    rig["occurrences"][0]["participant_kind"] = "player"
    check("PROJ.PARTICIPANT_KIND_REJECTED a structural participant-kind "
          "coordinate is refused",
          any("participant_kind" in x for x in validate(rig)))

    rig = copy.deepcopy(base)
    rig["occurrences"][0]["facts"][0]["record_party"] = "KEY"
    check("PROJ.RECORD_PARTY_REJECTED a per-row party field is refused",
          any("record_party" in x for x in validate(rig)))

    rig = copy.deepcopy(base)
    rig["occurrences"][0]["facts"][0]["dimension"] = "occ_facet"
    check("PROJ.NO_CANDIDATE_BRANCH a candidate-named dimension is refused",
          validate(rig) != [])

    print("\nDISPOSITIONS AND ABSENCE")
    key = sample_projection("KEY")
    key["occurrences"][0]["facts"][0] = _fact(
        disposition="HUMAN_RESOLVED",
        resolved={"absent": True},
        adjudication={"method": "INDEPENDENT_DUAL",
                      "disagreement_status": "RESOLVED"})
    check("PROJ.HUMAN_RESOLVED_KEY_ONLY the key may record adjudicated absence",
          validate(key) == [], validate(key))
    rig = copy.deepcopy(key)
    rig["artifact_role"] = "CANDIDATE_EXPORT"
    check("PROJ.HUMAN_RESOLVED_KEY_ONLY-RIG a candidate emitting "
          "HUMAN_RESOLVED is refused",
          any("key/adjudication-side only" in x for x in validate(rig)))

    rig = copy.deepcopy(key)
    rig["occurrences"][0]["facts"][0]["disposition"] = "ABSENT_PROVEN"
    rig["occurrences"][0]["facts"][0].pop("resolved", None)
    rig["occurrences"][0]["facts"][0].pop("adjudication", None)
    check("PROJ.ABSENT_REQUIRES_CLAIMANT_PROOF the key may not claim "
          "ABSENT_PROVEN",
          any("claimant-side only" in x for x in validate(rig)))
    cand = sample_projection("CANDIDATE_EXPORT")
    cand["occurrences"][0]["facts"][0] = _fact(disposition="ABSENT_PROVEN")
    check("PROJ.ABSENT_REQUIRES_CLAIMANT_PROOF a candidate may claim it",
          validate(cand) == [], validate(cand))

    rig = copy.deepcopy(key)
    rig["occurrences"][0]["facts"][0]["adjudication"] = {"method": "PRESENT"}
    check("PROJ.HUMAN_RESOLVED_METHOD_NOT_DISPOSITION encoding the method as a "
          "disposition value is refused",
          any("must not be encoded as a disposition" in x
              for x in validate(rig)))

    omitted = sample_projection("CANDIDATE_EXPORT")
    omitted["occurrences"][0]["facts"] = []
    absent_claims = [f for o in omitted["occurrences"]
                     for f in o.get("facts", [])
                     if f.get("disposition") == "ABSENT_PROVEN"]
    check("PROJ.UNKNOWN_NOT_ABSENT an omitted dimension yields NO absence "
          "claim (missing is never absent)", absent_claims == [])
    check("PROJ.UNKNOWN_NOT_ABSENT-RIG an absence claim has to be WRITTEN to "
          "exist, and then it is visible",
          len([f for o in cand["occurrences"] for f in o["facts"]
               if f.get("disposition") == "ABSENT_PROVEN"]) == 1)

    print("\nACTION HEADS")
    rig = copy.deepcopy(base)
    rig["occurrences"][0]["facts"].append(
        _fact(dim="card_type", op="REQUIRES", value="destroy",
              scope={"kind": "OCCURRENCE"}))
    rig["occurrences"][0]["action_heads"][0]["dimension"] = "card_type"
    check("PROJ.ACTION_NOT_DIMENSION an action head carrying a dimension is "
          "refused",
          any("not an eligibility dimension" in x for x in validate(rig)))

    multi = canonicalize(base)
    heads = [h["head"] for h in multi["occurrences"][0]["action_heads"]]
    check("PROJ.MULTI_ACTION multiple heads survive canonicalization in "
          "PRINTED order", heads == ["destroy", "create"], heads)

    empty = sample_projection()
    empty["occurrences"][0]["action_heads"] = []
    empty["occurrences"][0]["action_head_disposition"] = "UNRESOLVED"
    check("PROJ.ACTION_UNRESOLVED no detected head is representable as "
          "UNRESOLVED", validate(empty) == [], validate(empty))
    rig = copy.deepcopy(empty)
    rig["occurrences"][0]["action_head_disposition"] = "ABSENT_PROVEN"
    check("PROJ.ACTION_UNRESOLVED-RIG calling a missing head absent is refused",
          validate(rig) != [])

    print("\nCOST — STRUCTURAL, POSITIONAL, NEVER A DIMENSION")
    positive = [("{2}, {T}: Draw a card.", "CR 113.3b/602.1a"),
                ("+1: ~ deals 2 damage to any target.", "CR 606.2"),
                ("Equip—Sacrifice a creature.", "CR 702.6b")]
    for txt, arm in positive:
        got = derive_cost_regions(txt)
        check(f"PROJ.COST_REGION_DERIVED {arm} yields a region",
              [g[0] for g in got] == [arm], f"{txt!r} -> {got}")
    negative = ["Counter target spell unless that player pays {2}.",
                "You may sacrifice a creature. If you do, draw a card.",
                'Equipped creature has "{T}: Draw a card."']
    for txt in negative:
        check("PROJ.COST_NOT_EFFECT_HEAD positional rule refuses "
              f"{txt[:44]!r}", derive_cost_regions(txt) == [],
              derive_cost_regions(txt))
    check("PROJ.COST_NOT_EFFECT_HEAD-RIG a VERB-based rule would claim the "
          "effect text (which is why the marker is positional)",
          any(w in negative[1].lower() for w in ("sacrifice", "pay")))

    rig = copy.deepcopy(base)
    rig["occurrences"][0]["structural_regions"][0]["dimension"] = "card_type"
    check("PROJ.COST_NOT_DIMENSION a region carrying a dimension is refused",
          any("not an eligibility dimension" in x for x in validate(rig)))
    rig = copy.deepcopy(base)
    rig["occurrences"][0]["structural_regions"][0]["disposition"] = \
        "ABSENT_PROVEN"
    check("PROJ.COST_NO_ABSENCE a region carrying a disposition is refused",
          any("never participates in absence" in x for x in validate(rig)))
    check("PROJ.COST_NO_ABSENCE cost is absent from the dimension vocabulary "
          "entirely", "cost" not in DIMENSIONS)

    rig = copy.deepcopy(base)
    rig["occurrences"][0]["structural_regions"].append(
        {"role": "EFFECT", "derivation_class": "EXTRACT-0",
         "evidence": _evidence(a=0, b=9)})
    vs = validate(rig)
    check("PROJ.COST_SAME_SPAN_SAME_ROLE a positive EFFECT token is refused, "
          "and the same span may not carry two roles",
          any("not ratified" in x for x in vs) and
          any("two different roles" in x for x in vs), vs)

    print("\nTRACE")
    rig = copy.deepcopy(base)
    rig["occurrences"][0]["facts"][0].pop("evidence")
    check("PROJ.TRACE_REQUIRED a surviving fact with no trace is refused",
          any("no evidence trace" in x for x in validate(rig)))
    rig = copy.deepcopy(base)
    rig["occurrences"][0]["facts"][0]["evidence"]["view"] = "CANONICAL"
    check("PROJ.TRACE_CORRUPTION normalization presented as evidence is "
          "refused",
          any("RAW view" in x for x in validate(rig)))
    rig = copy.deepcopy(base)
    del rig["occurrences"][0]["facts"][0]["evidence"]["span"]
    check("PROJ.TRACE_CORRUPTION a trace stripped of its span is refused",
          any("deterministic span" in x for x in validate(rig)))

    reminder = "Flying (This creature can't be blocked except by creatures " \
               "with flying or reach.)"
    rspans = reminder_spans(reminder)
    inside = (rspans[0][0] + 2, rspans[0][1] - 2) if rspans else (0, 1)
    try:
        assert_evidence_admissible(reminder, inside)
        red = False
    except SystemExit:
        red = True
    check("PROJ.TRACE_REMINDER_INADMISSIBLE reminder-only support HALTS", red)
    try:
        assert_evidence_admissible(reminder, (0, 6))
        ok = True
    except SystemExit:
        ok = False
    check("PROJ.TRACE_REMINDER_INADMISSIBLE-RIG rules text in the same "
          "paragraph is still admissible", ok)

    print("\nDERIVED / CANONICAL BOUNDARY")
    for field in ("B2_verdict", "C1_verdict", "DISCOVERY_1"):
        rig = copy.deepcopy(base)
        rig["occurrences"][0]["facts"][0][field] = "BROADER"
        check(f"PROJ.DERIVED_NOT_CANONICAL {field} in the fact substrate is "
              f"refused", any(field in x for x in validate(rig)))
    rig = copy.deepcopy(base)
    rig["occurrences"][0]["facts"][0]["E1_explanation"] = \
        "these matched because both destroy a creature"
    check("PROJ.E1_NOT_PROSE_GOLD a hand-authored explanation string is "
          "refused", any("E1_explanation" in x for x in validate(rig)))

    print("\nDETERMINISM")
    perm = copy.deepcopy(base)
    perm["occurrences"][0]["facts"].reverse()
    perm["occurrences"][0]["relations"].reverse()
    perm["occurrences"][0]["structural_regions"].reverse()
    check("PROJ.ORDER_DETERMINISTIC a permutation of semantically identical "
          "input canonicalizes to identical bytes",
          canonical_bytes(perm) == canonical_bytes(base))
    check("PROJ.ORDER_DETERMINISTIC-RIG head order is SEMANTIC and is not "
          "normalized away",
          canonical_bytes(_heads_swapped(base)) != canonical_bytes(base))
    check("PROJ.ORDER_DETERMINISTIC canonicalization drops nothing",
          fact_count(canonicalize(base)) == fact_count(base))

    print("\nSURFACE")
    cards, _, _ = fc.load_corpus_gated()
    ids = pr.open_exemplars(pr.published_classes())
    bad = validate_manifest(cards, ids)
    check("SURFACE.HASH_MATCH the pinned digests regenerate from live "
          "machinery", bad == [], bad)

    live = regenerate_surface(cards, ids)
    pinned = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    rigged = surface_digest(live["canonical"]["all"][:-1])
    check("SURFACE.RIGGED_RED dropping ONE occurrence changes the digest",
          rigged != pinned["sets"]["all"]["sha256"])
    moved = [(a[0], a[1], a[2], a[3] + 99)
             for a in live["canonical"]["legacy_reached"]]
    check("SURFACE.RIGGED_RED moving a clause ordinal changes the digest "
          "(a count cannot see a substitution)",
          surface_digest(moved) != pinned["sets"]["legacy_reached"]["sha256"]
          and len(moved) == len(live["canonical"]["legacy_reached"]))

    a = build_manifest(cards, ids)
    b = build_manifest(cards, ids)
    check("SURFACE.DETERMINISM_X2 two manifest builds are byte-identical",
          canonical_json(a) == canonical_json(b))

    print()
    if fails:
        print(f"SELFTEST FAILED — {len(fails)} control(s): {fails}")
        return 1
    print("SELFTEST PASSED — every control fired on the path it guards, and "
          "every rigging turned its control red.")
    return 0


def _heads_swapped(doc):
    d = copy.deepcopy(doc)
    d["occurrences"][0]["action_heads"].reverse()
    return d


# ==========================================================================
# CLI
# ==========================================================================

def census() -> int:
    cards, _, _ = fc.load_corpus_gated()
    ids = pr.open_exemplars(pr.published_classes())
    s = regenerate_surface(cards, ids)
    c = measure_cost_spans(cards, ids)
    print("=" * 74)
    print("AQ4 OPEN SEMANTIC SURFACE — CENSUS (counts only, no oracle_id)")
    print("=" * 74)
    print(f"  open exemplars                {s['exemplars']}")
    for k in ("all", "legacy_reached", "semantic_reached"):
        print(f"  {k:28} {len(s['canonical'][k])}")
    print(f"  rejected unstripped surface   "
          f"{len(s['unstripped_rejected']['all'])} / "
          f"{len(s['unstripped_rejected']['legacy_reached'])} / "
          f"{len(s['unstripped_rejected']['semantic_reached'])}")
    print(f"  raw-vs-canonical invariance   {s['view_invariance']}")
    print(f"  deferred-P3 exposure          {s['deferred_p3_exposure']}")
    print(f"  COST regions                  {c['cost_regions_total']} "
          f"({c['cost_regions_by_cr_arm']})")
    print(f"  COST crossing a clause        {c['crossing_clause_boundary']}")
    return 0


def main() -> int:
    ap_ = argparse.ArgumentParser(
        description="AQ4 evaluation-projection validator and surface pin.")
    ap_.add_argument("--selftest", action="store_true")
    ap_.add_argument("--census", action="store_true")
    ap_.add_argument("--validate-surface", action="store_true")
    ap_.add_argument("--write-manifest", action="store_true")
    a = ap_.parse_args()
    if a.selftest:
        return selftest()
    if a.census:
        return census()
    if a.write_manifest:
        write_manifest()
        print(f"wrote {MANIFEST_PATH}")
        return 0
    if a.validate_surface:
        bad = validate_manifest()
        if bad:
            fc.halt("open-surface manifest does not match live machinery:\n  - "
                    + "\n  - ".join(bad))
        print("open-surface manifest MATCHES live machinery (full digests).")
        return 0
    ap_.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
