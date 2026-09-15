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

ATOM PAYLOADS (schema 2.0.0) -- VALIDATION ONLY, NO NEW SEMANTICS
------------------------------------------------------------------
The CARD and INTERVAL payload shapes were already frozen law -- contract 13
states `CARD(dim, op, n)` and `{min,max}` -- and this file validated an atom's
OPERATOR while never inspecting its VALUE. A differently-keyed or malformed
payload therefore validated here and failed later, silently, as an UNKNOWN
nobody could attribute to anything. It now fails HERE:

    CARD      {"comparison": <ratified operator>, "n": <integer >= 0>}
    INTERVAL  {"min": <int|null>, "max": <int|null>}  not both null, min <= max

The CARD operator set is EXACTLY the two ratified law attests -- `=` and `>=`,
from contract 13's monocolored/colorless/multicolored examples. A third is a
ratification request and is refused loudly; admitting one silently would let an
exporter mint comparison law. **A malformed payload is invalid input, never
evidence for a negative verdict.**

CHOICE GROUPS -- GENERATED STRUCTURE, NEVER A VERDICT
------------------------------------------------------
`derive_choice_groups` materializes the structural input that already-ratified
law requires and the projection was missing, so a later comparison layer never
has to parse Oracle text. It carries an owning header, a `{min,max}` selection,
member occurrence addresses and a trace -- and no dimension, no atom, no
disposition and no verdict.

**There is no mode identifier and none may be added.** Each CR 700.2 option is
its own paragraph under the ratified locality split, so a member's PARAGRAPH
coordinate already says which option it belongs to. That is why the existing
four coordinates suffice.

**Every step is a ratified helper** -- `foundry_locality.units`,
`foundry_shape_extractor.strip_reminder`, `foundry_common.is_mode_line`,
`foundry_common._MODAL_HEADER_RE`, `foundry_shape_extractor.sentence_spans`,
`foundry_object_lattice._NUMBER_WORDS`. No modal parser is written here.

**THE DERIVATION REFUSES RATHER THAN GUESSES, and the refusal is the safety
property.** CR 700.2 does not enumerate header forms, so a count is trusted
only when nothing remains between the matched count token and the modal
separator. The ratified matcher accepts `chooses? one`, and that alternative
also fires inside "Choose one or more --" and "Choose one or both --", where
the selection is not one. Residue means refuse. Measured over the frozen open
surface: 21 groups derived, 6 candidate headers refused, and every refusal is
correct. **Absence of a choice group is NOT proof that units are independent.**

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
import foundry_object_lattice as ol      # noqa: E402
import aq4_pairing as pr                 # noqa: E402

SCHEMA_PATH = HERE / "evaluation-projection-schema.json"
MANIFEST_PATH = HERE / "open-surface-manifest.json"
CONTRACT_PATH = REPO_ROOT / "docs" / \
    "AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md"

SCHEMA_NAME = "aq4-evaluation-projection"
SCHEMA_VERSION = "3.0.0"
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
ATOM_PAYLOADS = SCHEMA["atom_payloads"]
CARD_COMPARISONS = set(ATOM_PAYLOADS["CARD"]["comparisons"])
CHOICE_GROUPS = SCHEMA["choice_groups"]
PARTICIPANT_KEYS = set(SCHEMA["participants"]["record_keys"])


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
# CHOICE GROUPS — generated structural input, positional and CR-grounded
# ==========================================================================

#: The count vocabulary, CONSUMED rather than retyped. `_MODAL_HEADER_RE` is
#: the ratified DET preprocessing standard (2026-07-31) and already owns which
#: header shapes are modal; `_NUMBER_WORDS` is the ratified numeral map. The
#: composition mirrors `foundry_aq4_probes`, which builds the same set the same
#: way -- one convention, not two.
_COUNT_WORDS = dict(ol._NUMBER_WORDS)
_COUNT_WORDS["one"] = 1
_COUNT_TOKEN = re.compile(r"\bchooses?\s+(\w+)", re.I)


def _selection_from_header(header: str):
    """({min,max}, None) for a deterministically derivable header, else
    (None, generic form) naming why it was REFUSED.

    THE TEST IS RESIDUE-HONEST, which is the whole safety property. The
    ratified modal matcher accepts `chooses? one`, and that alternative also
    matches INSIDE "Choose one or more —" and "Choose one or both —" — where
    the real selection is not one. So the count is trusted only when NOTHING
    remains between the matched token and the modal separator. Anything left
    over is residue, and residue means refuse rather than guess.

    Nothing here widens the ratified matcher; it only declines part of what
    the matcher already accepts.
    """
    m = fc._MODAL_HEADER_RE.search(header)
    if not m:
        return None, "no ratified modal header"
    residue = re.split(r"\s*[—–]\s*", header[m.end():], maxsplit=1)[0].strip()
    if residue:
        return None, f"residue between the count and the separator: {residue[:40]!r}"
    tok = _COUNT_TOKEN.match(m.group(0))
    if not tok:
        return None, "count token not recoverable"
    word = tok.group(1).lower()
    if word.isdigit():
        n = int(word)
    elif word in _COUNT_WORDS:
        n = _COUNT_WORDS[word]
    else:
        return None, f"count word {word!r} is not a ratified numeral"
    return {"min": n, "max": n}, None


def derive_choice_groups(card: dict, oracle_id: str) -> tuple:
    """([group], [refusal]) for one card. Structural; parses no semantics.

    Every step is a ratified helper: `foundry_locality.units` for the paragraph
    split, `foundry_shape_extractor.strip_reminder` for CR 207.2a,
    `foundry_common.is_mode_line` for the CR 700.2 bullet,
    `foundry_common._MODAL_HEADER_RE` for the header, and
    `foundry_shape_extractor.sentence_spans` for the clause ordinal. No new
    modal parser is written, and membership is never lexical.

    MODALITY IS CONFIRMED STRUCTURALLY, exactly as the ratified consumers
    confirm it: a header opens a group only if two or more bullet paragraphs
    actually follow it on the same face (CR 700.2 — *"two or more options in a
    bulleted list"*). A header with no bullets under it is a targeting
    instruction, not a mode list.
    """
    units = list(fl.units(card))
    groups, refused = [], []
    for k, ((fi, pi), raw, canon) in enumerate(units):
        head = fx.strip_reminder(canon).strip()
        if fc.is_mode_line(head) or not fc._MODAL_HEADER_RE.search(head):
            continue
        options = []
        for (fj, pj_), raw2, canon2 in units[k + 1:]:
            if fj != fi:
                break
            body = fx.strip_reminder(canon2).strip()
            if not fc.is_mode_line(body):
                break
            options.append((fj, pj_, body))
        if len(options) < 2:
            refused.append({"reason": "fewer than two bulleted options follow",
                            "generic_form": _generic(head)})
            continue
        sel, why = _selection_from_header(head)
        if sel is None:
            refused.append({"reason": why, "generic_form": _generic(head)})
            continue
        span = _raw_header_span(raw)
        if span is None:
            refused.append({"reason": "the header phrase is not locatable in "
                                      "the RAW evidence view",
                            "generic_form": _generic(head)})
            continue
        members = []
        for fj, pj_, body in options:
            for ci in range(len(fx.sentence_spans(body))):
                members.append({"oracle_id": oracle_id, "face": fj,
                                "paragraph": pj_, "clause": ci})
        groups.append({
            "owning_header": {
                "occurrence": {"oracle_id": oracle_id, "face": fi,
                               "paragraph": pi, "clause": 0}},
            "selection": sel,
            "members": members,
            "derivation_class": "EXTRACT-0",
            "cr_anchors": ["CR 700.2"],
            "evidence": {"category": "ORACLE_TEXT", "view": "RAW_ORACLE",
                         "occurrence": {"oracle_id": oracle_id, "face": fi,
                                        "paragraph": pi, "clause": 0},
                         "span": {"start": span[0], "end": span[1]}},
        })
    return groups, refused


def _raw_header_span(raw_paragraph: str):
    m = fc._MODAL_HEADER_RE.search(raw_paragraph)
    return (m.start(), m.end()) if m else None


def _generic(header: str) -> str:
    """A STRUCTURAL shape, never a card's text: numerals and any word carrying
    a capital letter are masked, so a refusal can be reported and counted
    without publishing oracle text."""
    masked = re.sub(r"\b[A-Z][\w'’-]*", "<W>", header)
    return re.sub(r"\d+", "<N>", masked)[:80]


def measure_choice_groups(cards=None, ids=None) -> dict:
    """The full census over the frozen open surface. Counts only."""
    if cards is None:
        cards, _, _ = fc.load_corpus_gated()
    if ids is None:
        ids = pr.open_exemplars(pr.published_classes())
    surface = {s[:4] for s in open_surface("canonical", cards, ids)}
    sel = collections.Counter()
    refusals = collections.Counter()
    groups_all, members_all, headers_seen = [], [], 0
    for oid in ids:
        gs, rs = derive_choice_groups(cards[oid], oid)
        for r in rs:
            refusals[r["reason"].split(":")[0]] += 1
        headers_seen += len(gs) + len(rs)
        for g in gs:
            groups_all.append(g)
            sel[f"{g['selection']['min']},{g['selection']['max']}"] += 1
            members_all += [tuple(_addr_tuple(m)) for m in g["members"]]
    sizes = [len(g["members"]) for g in groups_all]
    off = [m for m in members_all if m not in surface]
    dupes = len(members_all) - len(set(members_all))
    overlap = sum(1 for _m, c in collections.Counter(members_all).items()
                  if c > 1)
    faces = sum(1 for g in groups_all
                if len({m["face"] for m in g["members"]}
                       | {g["owning_header"]["occurrence"]["face"]}) > 1)
    paras = sum(1 for g in groups_all
                if len({m["paragraph"] for m in g["members"]}) > 1)
    return {
        "owning_headers_recognized": headers_seen,
        "choice_groups_derived": len(groups_all),
        "member_occurrences": len(members_all),
        "options_bulleted_paragraphs": sum(
            len({m["paragraph"] for m in g["members"]}) for g in groups_all),
        "selection_distribution": dict(sorted(sel.items())),
        "groups_with_1_member": sum(1 for n in sizes if n == 1),
        "groups_with_more_than_1_member": sum(1 for n in sizes if n > 1),
        "max_members_in_one_group": max(sizes) if sizes else 0,
        "refused_by_reason": dict(sorted(refusals.items())),
        "refused_total": sum(refusals.values()),
        "members_not_on_frozen_surface": len(off),
        "groups_crossing_a_face_boundary": faces,
        "groups_spanning_more_than_one_paragraph": paras,
        "duplicate_member_references": dupes,
        "occurrences_in_more_than_one_group": overlap,
        "_paragraph_note": "SPANNING PARAGRAPHS IS THE CORRECT RESULT, not a "
                           "violation: each CR 700.2 option is its own "
                           "paragraph under the ratified locality split, which "
                           "is exactly why the option a member belongs to is "
                           "carried by its paragraph coordinate and no mode "
                           "identifier exists. A FACE crossing would be the "
                           "defect, and there are none.",
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

        parts, seen_anchor = [], {}
        for rec in occ.get("participants", []):
            if not isinstance(rec, dict):
                v.append("a participant must be a record carrying its ordinal "
                         "and its canonical anchor")
                continue
            extra = sorted(set(rec) - PARTICIPANT_KEYS)
            if extra:
                v.append(f"participant record carries unratified key(s) "
                         f"{extra}; the key set is closed, which is what "
                         f"refuses a role or an argument slot by construction")
            o = rec.get("ordinal")
            if isinstance(o, bool) or not isinstance(o, int) or o < 0:
                v.append("a participant ordinal must be a non-negative bare "
                         "integer")
            else:
                parts.append(o)
            anch = rec.get("anchor")
            if not anch:
                v.append(f"participant {o!r} carries NO canonical anchor; "
                         f"without one its ordinal is exporter list order, "
                         f"which has no authority")
                continue
            v += _validate_evidence(anch, "participant anchor")
            if (anch.get("occurrence") or {}) and \
                    _addr_tuple(anch.get("occurrence")) != _addr_tuple(addr):
                v.append("a participant anchor must locate its OWN occurrence")
            sp = anch.get("span") or {}
            k = (sp.get("start"), sp.get("end"))
            if k in seen_anchor:
                v.append(f"participants {seen_anchor[k]!r} and {o!r} share the "
                         f"canonical anchor {k}. A collision is INVALID, never "
                         f"an arbitrary tie-break: a tie-break would silently "
                         f"decide an identity the evidence does not.")
            seen_anchor[k] = o
        if list(parts) != sorted(set(parts)):
            v.append("participant ordinals must be unique")

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
            v += _validate_atom_payload(atom)
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

    v += _validate_choice_groups(
        doc, {_addr_tuple(o.get("occurrence") or {})
              for o in doc.get("occurrences", [])} - {None})

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


def _validate_atom_payload(atom: dict) -> list:
    """The payload shapes are ALREADY FROZEN LAW; only the check is new.

    A malformed payload fails HERE, loudly. It must never reach a comparator
    and become an UNKNOWN nobody can attribute, and it may never become
    evidence for a negative verdict -- an unparseable value is invalid input,
    not a proof about a card.
    """
    op, v, out = atom.get("op"), atom.get("value"), []
    if op == "CARD":
        if not isinstance(v, dict):
            return ["a CARD atom's value must be the frozen payload object "
                    "{comparison, n}"]
        extra = sorted(set(v) - set(ATOM_PAYLOADS["CARD"]["required_keys"]))
        missing = sorted(set(ATOM_PAYLOADS["CARD"]["required_keys"]) - set(v))
        if missing:
            out.append(f"CARD payload is missing {missing}")
        if extra:
            out.append(f"CARD payload carries unratified key(s) {extra}")
        if "comparison" in v and v["comparison"] not in CARD_COMPARISONS:
            out.append(f"CARD comparison {v['comparison']!r} is not ratified; "
                       f"the attested set is {sorted(CARD_COMPARISONS)}. A "
                       f"further operator is a ratification, not an export "
                       f"choice.")
        n = v.get("n")
        if "n" in v and (isinstance(n, bool) or not isinstance(n, int)
                         or n < 0):
            out.append(f"CARD n must be a non-negative integer; got {n!r}")
    elif op == "INTERVAL":
        if not isinstance(v, dict):
            return ["an INTERVAL atom's value must be the frozen payload "
                    "object {min,max}"]
        extra = sorted(set(v) - set(ATOM_PAYLOADS["INTERVAL"]["required_keys"]))
        missing = sorted(set(ATOM_PAYLOADS["INTERVAL"]["required_keys"])
                         - set(v))
        if missing:
            out.append(f"INTERVAL payload is missing {missing}")
        if extra:
            out.append(f"INTERVAL payload carries unratified key(s) {extra}")
        lo, hi = v.get("min"), v.get("max")
        for name, x in (("min", lo), ("max", hi)):
            if x is not None and (isinstance(x, bool) or not isinstance(x, int)):
                out.append(f"INTERVAL {name} must be an integer or null; "
                           f"got {x!r}")
        if "min" in v and "max" in v and lo is None and hi is None:
            out.append("an INTERVAL with both endpoints null constrains "
                       "nothing and is not a constraint")
        if isinstance(lo, int) and isinstance(hi, int) and not \
                isinstance(lo, bool) and not isinstance(hi, bool) and lo > hi:
            out.append(f"INTERVAL min {lo} is greater than max {hi}")
    return out


def _validate_choice_groups(doc: dict, addrs: set) -> list:
    """Structural only. No dimension, no atom, no disposition, no verdict."""
    out = []
    for g in doc.get("choice_groups", []):
        for banned in ("dimension", "atom", "disposition"):
            if banned in g:
                out.append(f"a choice group must not carry {banned!r} -- it is "
                           f"structural, not an eligibility dimension and not "
                           f"a comparison answer")
        hdr = (g.get("owning_header") or {}).get("occurrence") or {}
        if not hdr:
            out.append("a choice group must name its owning header occurrence")
        elif len(hdr) > 4:
            out.append("the owning header address carries a fifth coordinate")
        htup = _addr_tuple(hdr)
        if htup and addrs and htup not in addrs:
            out.append(f"owning header {htup!r} does not resolve to a declared "
                       f"occurrence")
        sel = g.get("selection") or {}
        lo, hi = sel.get("min"), sel.get("max")
        ok = all(isinstance(x, int) and not isinstance(x, bool) and x >= 0
                 for x in (lo, hi))
        if not ok or lo > hi:
            out.append(f"choice-group selection must be {{min,max}} with "
                       f"0 <= min <= max; got {sel!r}")
        members = g.get("members") or []
        if len(members) < 2:
            out.append("a choice group needs at least two members -- CR 700.2 "
                       "requires two or more options")
        seen = []
        for m in members:
            if len(m) > 4:
                out.append("a member address carries a fifth coordinate")
            t = _addr_tuple(m)
            if t is None:
                out.append(f"member address {m!r} is not a four-coordinate "
                           f"occurrence")
                continue
            if addrs and t not in addrs:
                out.append(f"member {t!r} does not resolve to a declared "
                           f"occurrence")
            if htup and t[0] != htup[0]:
                out.append("choice groups are same-card only")
            if t in seen:
                out.append(f"duplicate member reference {t!r}")
            seen.append(t)
        if g.get("derivation_class") not in DERIVATION_CLASSES:
            out.append(f"choice-group derivation_class "
                       f"{g.get('derivation_class')!r} is not ratified")
        out += _validate_evidence(g.get("evidence"), "choice group")
    return out


def _addr_tuple(a):
    if not isinstance(a, dict):
        return None
    try:
        return (a["oracle_id"], a["face"], a["paragraph"], a["clause"])
    except KeyError:
        return None


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
        _canonicalize_participants(occ)
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
    if "choice_groups" in out:
        for g in out["choice_groups"]:
            # Members are a SET of occurrences; their option is carried by the
            # paragraph coordinate, so member order is not semantic and is
            # normalized. Head order is semantic and is not -- the two cases
            # are deliberately opposite.
            g["members"] = sorted(g.get("members", []),
                                  key=lambda m: (_addr_tuple(m) or ()))
        out["choice_groups"] = sorted(
            out["choice_groups"],
            key=lambda g: ((_addr_tuple((g.get("owning_header") or {})
                                        .get("occurrence") or {}) or ()),
                           canonical_json(g)))
    return out


def _anchor_key(rec):
    sp = ((rec.get("anchor") or {}).get("span") or {})
    return (sp.get("start", -1), sp.get("end", -1))


def _canonicalize_participants(occ: dict) -> None:
    """Ordinals are DERIVED FROM ANCHORS, never from exporter list order.

    Sort by canonical anchor and assign 0..n-1, then remap every reference in
    facts and relations. This is what lets the key and two independently built
    candidates align their participants for the SAME occurrence -- and it gives
    equal ordinals on DIFFERENT occurrences no meaning whatsoever.
    """
    recs = occ.get("participants", [])
    if not recs or not all(isinstance(r, dict) for r in recs):
        return
    ordered = sorted(recs, key=lambda r: (_anchor_key(r), r.get("ordinal", -1)))
    remap = {}
    for new, rec in enumerate(ordered):
        old = rec.get("ordinal")
        if old is not None:
            remap[old] = new
        rec["ordinal"] = new
    occ["participants"] = ordered
    for f in occ.get("facts", []):
        sc = f.get("scope") or {}
        if sc.get("kind") == "PARTICIPANT" and sc.get("participant") in remap:
            sc["participant"] = remap[sc["participant"]]
    for rel in occ.get("relations", []):
        for end in ("from", "to"):
            ref = rel.get(end)
            if isinstance(ref, dict) and ref.get("participant") in remap:
                ref["participant"] = remap[ref["participant"]]


def canonical_bytes(doc: dict) -> bytes:
    return canonical_json(canonicalize(doc)).encode("utf-8")


def fact_count(doc: dict) -> int:
    return sum(len(o.get("facts", [])) + len(o.get("structural_regions", []))
               + len(o.get("relations", [])) + len(o.get("action_heads", []))
               for o in doc.get("occurrences", [])) \
        + len(doc.get("choice_groups", []))


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


def _participant(ordinal, a, b, oid="00000000-0000-0000-0000-000000000001"):
    """A participant record: a bare ordinal plus ONE canonical RAW anchor."""
    return {"ordinal": ordinal,
            "anchor": {"category": "ORACLE_TEXT", "view": "RAW_ORACLE",
                       "occurrence": {"oracle_id": oid, "face": 0,
                                      "paragraph": 0, "clause": 0},
                       "span": {"start": a, "end": b}}}


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
            "participants": [_participant(0, 7, 13),
                             _participant(1, 30, 36)],
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

    print("\nPARTICIPANTS — canonical anchors and derived local numbering")
    base_p = sample_projection()
    check("PART.ANCHOR_REQUIRED-RIG the anchored fixture validates",
          validate(base_p) == [], validate(base_p))
    rig = copy.deepcopy(base_p)
    rig["occurrences"][0]["participants"][0].pop("anchor")
    check("PART.ANCHOR_REQUIRED an anchorless participant is refused",
          any("NO canonical anchor" in x for x in validate(rig)))
    rig = copy.deepcopy(base_p)
    rig["occurrences"][0]["participants"][0]["anchor"]["view"] = "CANONICAL"
    check("PART.ANCHOR_RAW_ONLY a normalized detector view cannot anchor a "
          "participant", any("RAW view" in x for x in validate(rig)))
    rig = copy.deepcopy(base_p)
    rig["occurrences"][0]["participants"][1]["anchor"]["span"] = \
        dict(rig["occurrences"][0]["participants"][0]["anchor"]["span"])
    check("PART.ANCHOR_COLLISION two participants sharing a canonical anchor "
          "are refused, never tie-broken",
          any("share the canonical anchor" in x for x in validate(rig)))
    rig = copy.deepcopy(base_p)
    rig["occurrences"][0]["participants"][0]["anchor"]["occurrence"][
        "paragraph"] = 9
    check("PART.ANCHOR_REQUIRED an anchor must locate its OWN occurrence",
          any("locate its OWN occurrence" in x for x in validate(rig)))
    for field in ("participant_kind", "role", "argument_slot",
                  "semantic_role", "global_participant_id"):
        rig = copy.deepcopy(base_p)
        rig["occurrences"][0]["participants"][0][field] = "agent"
        check(f"PART.NO_ROLE {field!r} on a participant is refused",
              any("unratified key" in x for x in validate(rig)),
              validate(rig))

    perm = copy.deepcopy(base_p)
    perm["occurrences"][0]["participants"].reverse()
    for r_, o_ in zip(perm["occurrences"][0]["participants"], (0, 1)):
        r_["ordinal"] = o_
    for f_ in perm["occurrences"][0]["facts"]:
        sc = f_.get("scope") or {}
        if sc.get("kind") == "PARTICIPANT":
            sc["participant"] = 1 - sc["participant"]
    # The relation reference has to be relabelled too, or the "permuted"
    # document is not the same document written differently -- it points at a
    # different participant. Getting this wrong is how a permutation fixture
    # reports a canonicalization defect that is really a fixture defect.
    for rel_ in perm["occurrences"][0]["relations"]:
        for end_ in ("from", "to"):
            ref_ = rel_.get(end_)
            if isinstance(ref_, dict) and "participant" in ref_:
                ref_["participant"] = 1 - ref_["participant"]
    check("PART.NUMBERING_ORDER_INDEPENDENT a permuted export canonicalizes "
          "byte-identically", canonical_bytes(perm) == canonical_bytes(base_p),
          "permutation changed the canonical bytes")
    canon = canonicalize(perm)["occurrences"][0]
    check("PART.NUMBERING_ORDER_INDEPENDENT ordinals are 0..n-1 by ascending "
          "anchor", [r["ordinal"] for r in canon["participants"]] == [0, 1]
          and [_anchor_key(r) for r in canon["participants"]]
          == sorted(_anchor_key(r) for r in canon["participants"]))
    check("PART.REFERENCE_REMAP canonical renumbering remaps every fact "
          "reference",
          [(f.get("scope") or {}).get("participant") for f in canon["facts"]]
          == [(f.get("scope") or {}).get("participant")
              for f in canonicalize(base_p)["occurrences"][0]["facts"]])
    relremap = copy.deepcopy(perm)
    relremap["occurrences"][0]["relations"][0]["from"]["participant"] = 1
    got = canonicalize(relremap)["occurrences"][0]["relations"][0]["from"][
        "participant"]
    check("PART.REFERENCE_REMAP canonical renumbering remaps a relation "
          "reference too", got == 0, got)
    check("PART.LOCAL_ONLY the schema states equal ordinals carry NO "
          "cross-card meaning, and correspondence is not projection content",
          "no cross-card semantic meaning" in
          SCHEMA["participants"]["canonical_numbering"]["_law"].lower()
          .replace("cross-card semantic meaning", "cross-card semantic meaning")
          or "NOT PROJECTION CONTENT"
          in SCHEMA["participants"]["cross_card_correspondence"])

    print("\nATOM PAYLOAD — already-frozen shapes, newly VALIDATED")
    good_card = sample_projection()
    good_card["occurrences"][0]["facts"].append(
        _fact(dim="color", op="CARD", value={"comparison": "=", "n": 1},
              scope={"kind": "PARTICIPANT", "participant": 0}))
    check("PROJ.CARD_OK the ratified payload validates",
          validate(good_card) == [], validate(good_card))
    for name, payload, needle in (
            ("PROJ.CARD_BAD_OPERATOR", {"comparison": "!=", "n": 1},
             "is not ratified"),
            ("PROJ.CARD_BAD_N", {"comparison": "=", "n": -1},
             "non-negative integer"),
            ("PROJ.CARD_BAD_N-RIG", {"comparison": "=", "n": "1"},
             "non-negative integer"),
            ("PROJ.CARD_BAD_SHAPE", {"op": "=", "count": 1}, "unratified key"),
            ("PROJ.CARD_BAD_SHAPE-RIG", {"comparison": "="}, "missing")):
        rig = copy.deepcopy(good_card)
        rig["occurrences"][0]["facts"][-1]["atom"]["value"] = payload
        check(f"{name} malformed CARD payload is refused",
              any(needle in x for x in validate(rig)), validate(rig))
    rig = copy.deepcopy(good_card)
    rig["occurrences"][0]["facts"][-1]["atom"]["value"] = "1"
    check("PROJ.CARD_BAD_SHAPE a non-object CARD value is refused",
          any("frozen payload object" in x for x in validate(rig)))

    good_int = sample_projection()
    good_int["occurrences"][0]["facts"].append(
        _fact(dim="quantity", op="INTERVAL", value={"min": 1, "max": 3},
              scope={"kind": "OCCURRENCE"}))
    check("PROJ.INTERVAL_OK the ratified payload validates",
          validate(good_int) == [], validate(good_int))
    check("PROJ.INTERVAL_OK-RIG a half-open interval is still valid",
          validate(_with_interval({"min": 2, "max": None})) == [])
    for name, payload, needle in (
            ("PROJ.INTERVAL_BOTH_NULL", {"min": None, "max": None},
             "constrains nothing"),
            ("PROJ.INTERVAL_REVERSED", {"min": 5, "max": 2},
             "greater than max"),
            ("PROJ.INTERVAL_BAD_TYPE", {"min": "1", "max": 3},
             "integer or null"),
            ("PROJ.INTERVAL_BAD_TYPE-RIG", {"min": 1}, "missing")):
        check(f"{name} malformed INTERVAL payload is refused",
              any(needle in x for x in validate(_with_interval(payload))),
              validate(_with_interval(payload)))
    check("PROJ.MALFORMED_NEVER_UNKNOWN a malformed payload FAILS validation "
          "rather than reaching a comparator as an unattributable UNKNOWN",
          validate(_with_interval({"min": 5, "max": 2})) != [])

    print("\nCHOICE GROUPS — generated structure, never a verdict")
    cg = sample_choice_group()
    check("PROJ.CHOICEGROUP_OK a conforming group validates",
          validate(cg) == [], validate(cg))
    rig = copy.deepcopy(cg)
    rig["choice_groups"][0]["members"][0]["clause"] = 99
    check("PROJ.CHOICEGROUP_MEMBER_MISSING an unresolvable member is refused",
          any("does not resolve" in x for x in validate(rig)))
    rig = copy.deepcopy(cg)
    rig["choice_groups"][0]["members"].append(
        dict(rig["choice_groups"][0]["members"][0]))
    check("PROJ.CHOICEGROUP_DUP_MEMBER a duplicate member is refused",
          any("duplicate member" in x for x in validate(rig)))
    for bad in ({"min": 2, "max": 1}, {"min": -1, "max": 1}, {"min": 1}):
        rig = copy.deepcopy(cg)
        rig["choice_groups"][0]["selection"] = bad
        check(f"PROJ.CHOICEGROUP_BAD_SELECTION {bad} is refused",
              any("selection must be" in x for x in validate(rig)))
    for field in ("mode_id", "mode_ordinal", "mode_index"):
        rig = copy.deepcopy(cg)
        rig["choice_groups"][0][field] = 0
        check(f"PROJ.CHOICEGROUP_NO_MODE_ID an injected {field} is refused",
              any(field in x for x in validate(rig)))
    rig = copy.deepcopy(cg)
    rig["choice_groups"][0]["members"][0]["mode"] = 1
    check("PROJ.CHOICEGROUP_NO_MODE_ID a fifth coordinate on a member is "
          "refused", any("fifth coordinate" in x for x in validate(rig)))
    rig = copy.deepcopy(cg)
    rig["choice_groups"][0].pop("evidence")
    check("PROJ.CHOICEGROUP_TRACE_REQUIRED a group with no owning-header "
          "evidence is refused",
          any("no evidence trace" in x for x in validate(rig)))
    rig = copy.deepcopy(cg)
    rig["choice_groups"][0]["evidence"]["view"] = "CANONICAL"
    check("PROJ.CHOICEGROUP_TRACE_REQUIRED-RIG normalization as the group's "
          "evidence is refused", any("RAW view" in x for x in validate(rig)))
    for field in ("dimension", "atom", "disposition"):
        rig = copy.deepcopy(cg)
        rig["choice_groups"][0][field] = "card_type"
        check(f"PROJ.CHOICEGROUP_NOT_DIMENSION a group carrying {field!r} is "
              f"refused", any("structural, not an eligibility" in x
                              for x in validate(rig)))
    for field in ("C3_verdict", "choice_verdict", "exclusivity_verdict",
                  "alternative_or_cumulative"):
        rig = copy.deepcopy(cg)
        rig["choice_groups"][0][field] = "ALTERNATIVE"
        check(f"PROJ.CHOICEGROUP_NOT_VERDICT {field} injected as canonical "
              f"fact is refused", any(field in x for x in validate(rig)))
    rig = copy.deepcopy(cg)
    rig["choice_groups"][0]["members"] = rig["choice_groups"][0]["members"][:1]
    check("PROJ.CHOICEGROUP_NOT_VERDICT-RIG CR 700.2 needs two or more "
          "options, so a one-member group is refused",
          any("at least two members" in x for x in validate(rig)))
    rig = copy.deepcopy(cg)
    rig["choice_groups"][0]["members"][1]["oracle_id"] = \
        "00000000-0000-0000-0000-0000000000ff"
    check("PROJ.CHOICEGROUP_EXISTING_OCCURRENCES a cross-card member is "
          "refused", any("same-card only" in x for x in validate(rig)))

    print("\nCHOICE GROUPS — the derivation refuses rather than guesses")
    for form, want in (("Choose one —", {"min": 1, "max": 1}),
                       ("Choose two —", {"min": 2, "max": 2}),
                       ("An opponent chooses one —", {"min": 1, "max": 1})):
        got, _why = _selection_from_header(form)
        check(f"PROJ.CHOICEGROUP_SELECTION {form!r} -> {want}", got == want,
              f"{form!r} -> {got}")
    for form in ("Choose one or more —", "Choose one or both —",
                 "Choose up to five {P} worth of modes.",
                 "Choose one. If you control an artifact and an enchantment "
                 "as you cast this spell, you may choose both instead."):
        got, why = _selection_from_header(form)
        check(f"PROJ.CHOICEGROUP_NO_GUESS an ambiguous header yields NO "
              f"structure ({form[:26]!r})", got is None and bool(why),
              f"{form!r} -> {got}")
    check("PROJ.CHOICEGROUP_NO_GUESS-RIG the ratified matcher ACCEPTS the "
          "ambiguous forms, so the refusal is ours and not the matcher's",
          all(fc._MODAL_HEADER_RE.search(f) for f in
              ("Choose one or more —", "Choose one or both —")))

    perm = copy.deepcopy(cg)
    perm["choice_groups"][0]["members"].reverse()
    check("PROJ.CHOICEGROUP_ORDER_DETERMINISTIC a member permutation "
          "canonicalizes to identical bytes",
          canonical_bytes(perm) == canonical_bytes(cg))
    check("PROJ.CHOICEGROUP_ORDER_DETERMINISTIC canonicalization drops no "
          "group", fact_count(canonicalize(cg)) == fact_count(cg))

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

    cg1 = measure_choice_groups(cards, ids)
    cg2 = measure_choice_groups(cards, ids)
    check("PROJ.CHOICEGROUP_ORDER_DETERMINISTIC the live derivation is "
          "byte-identical across two runs",
          canonical_json(cg1) == canonical_json(cg2))
    check(f"PROJ.CHOICEGROUP_EXISTING_OCCURRENCES every derived member "
          f"({cg1['member_occurrences']}) resolves on the frozen surface, and "
          f"no group crosses a face",
          cg1["members_not_on_frozen_surface"] == 0
          and cg1["groups_crossing_a_face_boundary"] == 0
          and cg1["duplicate_member_references"] == 0
          and cg1["occurrences_in_more_than_one_group"] == 0, cg1)
    check(f"PROJ.CHOICEGROUP_NO_GUESS the live derivation REFUSES "
          f"{cg1['refused_total']} of {cg1['owning_headers_recognized']} "
          f"candidate headers rather than guessing",
          cg1["refused_total"] > 0
          and cg1["choice_groups_derived"]
          + cg1["refused_total"] == cg1["owning_headers_recognized"])

    print()
    if fails:
        print(f"SELFTEST FAILED — {len(fails)} control(s): {fails}")
        return 1
    print("SELFTEST PASSED — every control fired on the path it guards, and "
          "every rigging turned its control red.")
    return 0


def _with_interval(payload):
    d = sample_projection()
    d["occurrences"][0]["facts"].append(
        _fact(dim="quantity", op="INTERVAL", value=payload,
              scope={"kind": "OCCURRENCE"}))
    return d


def sample_choice_group(role="KEY") -> dict:
    """A conforming synthetic document carrying one choice group.

    Synthetic throughout: the oracle_id is a zero-padded placeholder and no
    real card is used as a projection fixture.
    """
    oid = "00000000-0000-0000-0000-000000000001"

    def occ(par, cl):
        return {"occurrence": {"oracle_id": oid, "face": 0, "paragraph": par,
                               "clause": cl},
                "participants": [], "action_heads": [],
                "action_head_disposition": "UNRESOLVED", "facts": []}

    return {
        "schema": SCHEMA_NAME, "version": SCHEMA_VERSION,
        "artifact_role": role,
        "occurrences": [occ(0, 0), occ(1, 0), occ(2, 0)],
        "choice_groups": [{
            "owning_header": {"occurrence": {"oracle_id": oid, "face": 0,
                                             "paragraph": 0, "clause": 0}},
            "selection": {"min": 1, "max": 1},
            "members": [
                {"oracle_id": oid, "face": 0, "paragraph": 1, "clause": 0},
                {"oracle_id": oid, "face": 0, "paragraph": 2, "clause": 0},
            ],
            "derivation_class": "EXTRACT-0",
            "cr_anchors": ["CR 700.2"],
            "evidence": _evidence(oid, 0, 10),
        }],
    }


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
    g = measure_choice_groups(cards, ids)
    print("  " + "-" * 70)
    for k in ("owning_headers_recognized", "choice_groups_derived",
              "member_occurrences", "options_bulleted_paragraphs",
              "selection_distribution", "groups_with_1_member",
              "groups_with_more_than_1_member", "max_members_in_one_group",
              "refused_total", "refused_by_reason",
              "members_not_on_frozen_surface",
              "groups_crossing_a_face_boundary",
              "groups_spanning_more_than_one_paragraph",
              "duplicate_member_references",
              "occurrences_in_more_than_one_group"):
        print(f"  {k:<42} {g[k]}")
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
