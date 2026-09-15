#!/usr/bin/env python3
"""AQ4 BENCHMARK — SHARED CANDIDATE-NEUTRAL COMPARISON ALGEBRA (packet 7, repaired).

WHAT THIS IS AND IS NOT
-----------------------
Shared benchmark EVALUATION machinery, never a candidate. It consumes the
frozen Packet-4 evaluation projection at schema 2.0.0 and derives three-valued
comparison verdicts from it. Production AQ4 architecture remains UNRATIFIED.

It does not parse Oracle text, read a candidate-native field, branch on
candidate identity, adjudicate truth, write an answer key, or score anything.

THIS FILE SUPERSEDES A QUARANTINED ATTEMPT
------------------------------------------
The earlier implementation crossed a pre-registered STOP and embedded
unratified law (`docs/INCIDENT-AQ4-PACKET7-STOP-BREACH-2026-08-17.md`). Nothing
of it is authority here. Removed and NOT revived:

  · the generic whole-unit equality operation and its self-designed
    necessary-condition list;
  · action-head identity, relation-edge absence, cost-region absence and
    participant integer-set identity as comparison conditions;
  · PROVEN components carrying a contract proof kind for a check that merely
    did not block, and prose sitting in a contract-anchor field;
  · a false disjointness proof on partially-forbidden disjunctions;
  · the cardinality and interval payload readings, which are now Packet-4 law.

THE ORGANIZING LAW
------------------
    A UNIVERSAL claim is contract-provable.
    An EXISTENTIAL claim needs a corpus witness.

Entailment and disjointness are universal -> `CR_CONTRACT`. Non-entailment and
overlap assert that some object exists -> `CORPUS_WITNESS`. This is why an
inability to prove something can never become PROVEN_NOT.

THREE OPERATIONS, AND NO WHOLE-UNIT EQUALITY
---------------------------------------------
`OP_ENTAILS` · `OP_ELIGIBILITY_EQUALITY` · `OP_INTERSECTION`.

**There is deliberately no operation named for whole-unit equality.** The only
ratified positive equality is eligibility/constraint equality, and it is named
in full at every site precisely so the whole-unit reading cannot creep back in
under a shorter name.

B1's POSITIVE ARM IS UNAVAILABLE IN v1
--------------------------------------
The projection does not represent all uncontracted semantic residue, so equality
of projected content is not equality of semantic content. B1 returns PROVEN_NOT
only where eligibility non-equivalence is independently proven, and UNKNOWN
otherwise. Identical heads, identical participant integers, an absent cost
region, an absent relation edge and matching visible fields are each REFUSED as
positive evidence.

PARTICIPANT ORDINALS DO NOT CORRESPOND ACROSS OCCURRENCES
----------------------------------------------------------
Participant integers are local to one semantic occurrence and no cross-card
correspondence is ratified. A comparison whose outcome would depend on a
participant-scoped fact therefore returns UNKNOWN with reason
`NO_PARTICIPANT_CORRESPONDENCE`. Aligning by ordinal would give those integers a
meaning the contract explicitly withholds — so the restriction is implemented
rather than reasoned around, and its cost is reported.

A NON-BLOCKING CHECK IS NOT A PROOF
------------------------------------
A structural check that was evaluated and did not block is recorded as a
PRECONDITION: no result, no proof kind, no anchor, and it never enters the
three-valued composition. Only genuine semantic proof components do, and a
contract proof must cite a real anchor.

THE PROJECTION VALIDATOR IS AUTHORITATIVE
------------------------------------------
Payload shape is Packet-4's job, and this file never re-implements it as a
competing validator. Defensive readers still fail CLOSED: a malformed payload
becomes UNKNOWN and can never become evidence for a negative verdict.
"""
import sys
import copy
import json
import hashlib
import argparse
import itertools
import collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
sys.path.insert(0, str(EXPERIMENTS))
sys.path.insert(0, str(HERE))

import foundry_common as fc                # noqa: E402
import foundry_cr as CR                    # noqa: E402
import foundry_codebook as fcb             # noqa: E402
import foundry_probe as p                  # noqa: E402
import foundry_object_lattice as ol        # noqa: E402
import foundry_cr702_classes as crc        # noqa: E402
import aq4_projection as pj                # noqa: E402

ALGEBRA_PATH = HERE / "comparison-algebra.json"
PAIRS_PATH = HERE / "pairs-open.json"

ALGEBRA_NAME = "aq4-comparison-algebra"
ALGEBRA_VERSION = "3.0.0"

PROVEN, PROVEN_NOT, UNKNOWN = "PROVEN", "PROVEN_NOT", "UNKNOWN"
CR_CONTRACT, CORPUS_WITNESS = "CR_CONTRACT", "CORPUS_WITNESS"


def load_algebra() -> dict:
    a = json.loads(ALGEBRA_PATH.read_text(encoding="utf-8"))
    if a.get("schema") != ALGEBRA_NAME or a.get("version") != ALGEBRA_VERSION:
        fc.halt(f"comparison algebra identity mismatch: "
                f"{a.get('schema')!r}/{a.get('version')!r}")
    dep = a["projection_dependency"]
    if dep["schema"] != pj.SCHEMA_NAME or dep["version"] != pj.SCHEMA_VERSION:
        fc.halt(f"the algebra declares projection {dep['schema']}/"
                f"{dep['version']} but the live projection is "
                f"{pj.SCHEMA_NAME}/{pj.SCHEMA_VERSION}. A comparison law "
                f"pinned to a schema it is not running against is not pinned.")
    return a


ALGEBRA = load_algebra()
OPERATIONS = {o["id"]: o for o in ALGEBRA["operations"]}
RESULTS = tuple(ALGEBRA["result_domain"]["values"])
PROOF_KINDS = tuple(ALGEBRA["proof_kinds"]["values"])
REASONS = set(ALGEBRA["unknown_propagation"]["reason_classes"])
DIMENSIONS = pj.DIMENSIONS

#: Complement inference is sound only where an object carries exactly one value
#: and the CR closes the set. `controller_relation` fails must-have and is
#: ALSO excluded by name, because the contract forbids its complement by name
#: and a property test that quietly changed would re-admit it.
COMPLEMENT_FORBIDDEN = {"controller_relation"}
SINGLE_VALUED_EXHAUSTIVE = {
    n for n, d in DIMENSIONS.items()
    if d.get("closed") is True and d.get("multi") is False
    and d.get("must_have") is True and n not in COMPLEMENT_FORBIDDEN
}
EQUALITY_ONLY = {n for n, d in DIMENSIONS.items()
                 if str(d.get("v1_status", "")).startswith("equality-only")}

#: The ratified subtype -> parent-type edge, CONSUMED, never re-derived.
HIERARCHY = ol.SUBTYPE_TO_TYPE
if not HIERARCHY:
    fc.halt("the ratified subtype-to-type hierarchy parsed EMPTY. Comparing "
            "with an empty hierarchy silently downgrades every hierarchy "
            "entailment to UNKNOWN and reads as a clean conservative result.")

_TV = crc.type_vocabulary()
CLOSED_VOCABULARY = {
    "card_type": {t.lower() for t in _TV["card_types"]},
    "supertype": {t.lower() for t in _TV["supertypes"]},
    "subtype": {t.lower() for t in _TV["subtypes"]},
}
for _n, _v in CLOSED_VOCABULARY.items():
    if not _v:
        fc.halt(f"closed vocabulary for {_n!r} parsed EMPTY; an empty "
                f"vocabulary turns every value into an out-of-vocabulary "
                f"UNKNOWN and reads as conservatism.")


# ==========================================================================
# INGEST — only documents that validate under the frozen Packet-4 schema
# ==========================================================================

class Unit:
    """One projected semantic occurrence plus the artifact role that produced it.

    The role decides only the disposition SIDES. It is not a candidate identity
    and no verdict branches on which candidate exported a document.
    """

    __slots__ = ("occ", "role", "addr", "id")

    def __init__(self, occ: dict, role: str):
        self.occ, self.role = occ, role
        a = occ["occurrence"]
        self.addr = (a["oracle_id"], a["face"], a["paragraph"], a["clause"])
        self.id = pj.surface_id(self.addr)

    @property
    def participants(self):
        return tuple(r["ordinal"] for r in self.occ.get("participants", []))

    @property
    def heads(self):
        return tuple(h.get("head") for h in self.occ.get("action_heads", []))

    @property
    def head_disposition(self):
        return self.occ.get("action_head_disposition")

    @property
    def regions(self):
        return list(self.occ.get("structural_regions", []))

    @property
    def relations(self):
        return list(self.occ.get("relations", []))

    @property
    def facts(self):
        return list(self.occ.get("facts", []))


class Projection:
    """A validated, canonicalized projection document."""

    __slots__ = ("role", "units", "choice_groups")

    def __init__(self, role, units, choice_groups):
        self.role, self.units = role, units
        self.choice_groups = choice_groups

    def unit(self, key):
        return self.units[key]


def load_document(doc: dict) -> Projection:
    """Validate under the FROZEN Packet-4 schema 2.0.0, canonicalize, index.

    Rejection is a halt, never a warning. A document that does not validate is
    never partially consumed: the whole point of a shared projection is that a
    comparison cannot quietly reach around it. Payload shape is checked THERE,
    not re-implemented here.
    """
    pj.assert_valid(doc)
    c = pj.canonicalize(doc)
    units = {}
    for occ in c.get("occurrences", []):
        u = Unit(occ, c["artifact_role"])
        if u.id in units:
            fc.halt(f"duplicate occurrence address {u.id!r}; an address is an "
                    f"identity and cannot repeat.")
        units[u.id] = u
    return Projection(c["artifact_role"], units, c.get("choice_groups", []))


# ==========================================================================
# FACT READING — dispositions, wrappers, earned absence
# ==========================================================================

class FactView:
    __slots__ = ("key", "dimension", "scope_kind", "participant", "atom",
                 "status", "reason", "evidence", "provenance")

    def __init__(self, key, dimension, scope_kind, participant, atom, status,
                 reason, evidence, provenance):
        self.key, self.dimension = key, dimension
        self.scope_kind, self.participant = scope_kind, participant
        self.atom, self.status, self.reason = atom, status, reason
        self.evidence, self.provenance = evidence, provenance


def _fact_key(f: dict):
    sc = f.get("scope") or {}
    return (sc.get("kind"), sc.get("participant"), f.get("dimension"))


def obligations_satisfied(ledger, unit: Unit, key) -> bool:
    """Are the claimant-side absence obligations REPRESENTED as satisfied?

    They are discharged by the claiming candidate at scoring time under its own
    rule, so they arrive as EVALUATION CONTEXT rather than projection content.
    Default: not represented.
    """
    if not ledger:
        return False
    return bool(ledger.get((unit.id,) + tuple(key)))


def read_fact(f: dict, unit: Unit, ledger=None) -> FactView:
    key, sc = _fact_key(f), (f.get("scope") or {})
    d, ev = f.get("disposition"), f.get("evidence")
    prov = {"disposition": d}

    def mk(atom, status, reason):
        return FactView(key, f.get("dimension"), sc.get("kind"),
                        sc.get("participant"), atom, status, reason, ev, prov)

    if d == "PRESENT":
        return mk(f.get("atom"), "ATOM", None)
    if d == "HUMAN_RESOLVED":
        # Wrapper transparency: the payload compares, the wrapper survives in
        # provenance, and the adjudication METHOD is never a disposition.
        prov["adjudication"] = copy.deepcopy(f.get("adjudication"))
        r = f.get("resolved")
        if isinstance(r, dict) and r.get("absent") is True:
            return mk(None, "ABSENT", None)
        if isinstance(r, dict) and isinstance(r.get("atom"), dict):
            return mk(r["atom"], "ATOM", None)
        return mk(None, "BLOCKED", "ADJUDICATION_PAYLOAD_UNREADABLE")
    if d == "ABSENT_PROVEN":
        if obligations_satisfied(ledger, unit, key):
            prov["claimant_obligations"] = "REPRESENTED_SATISFIED"
            return mk(None, "ABSENT", None)
        prov["claimant_obligations"] = "NOT_REPRESENTED"
        return mk(None, "BLOCKED", "ABSENCE_NOT_EARNED")
    return mk(None, "BLOCKED", "DISPOSITION_NOT_ACTIONABLE")


def fact_index(unit: Unit, ledger=None) -> dict:
    out = {}
    for f in unit.facts:
        v = read_fact(f, unit, ledger)
        out.setdefault(v.key, []).append(v)
    return out


# ==========================================================================
# ATOM SEMANTICS — read defensively; the projection validator owns the shape
# ==========================================================================

def _values(atom):
    v = atom.get("value")
    return list(v) if isinstance(v, list) else [v]


def _norm(v):
    return v.lower() if isinstance(v, str) else v


def _card_range(atom):
    """None on ANY malformed payload -- fail closed. The projection validator
    is what rejects it; here it can only ever produce UNKNOWN."""
    v = atom.get("value")
    if not isinstance(v, dict):
        return None
    c, n = v.get("comparison"), v.get("n")
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        return None
    if c == "=":
        return (n, n)
    if c == ">=":
        return (n, float("inf"))
    return None


def _interval_range(atom):
    v = atom.get("value")
    if not isinstance(v, dict) or "min" not in v or "max" not in v:
        return None
    lo, hi = v.get("min"), v.get("max")
    for x in (lo, hi):
        if x is not None and (isinstance(x, bool) or not isinstance(x, int)):
            return None
    if lo is None and hi is None:
        return None
    lo = float("-inf") if lo is None else lo
    hi = float("inf") if hi is None else hi
    return None if lo > hi else (lo, hi)


def _contains(inner, outer):
    return outer[0] <= inner[0] and inner[1] <= outer[1]


def _disjoint(a, b):
    return a[1] < b[0] or b[1] < a[0]


def _vocab_ok(dim, value):
    vocab = CLOSED_VOCABULARY.get(dim)
    return True if vocab is None else _norm(value) in vocab


def _hierarchy_parents(subtype):
    return set(HIERARCHY.get(_norm(subtype), set()))


# ==========================================================================
# ENTAILMENT
# ==========================================================================

def counterpart_ordinal(corr, frm: "Unit", to: "Unit", ordinal):
    """The corresponding participant on `to`, or None.

    Resolution is by BOUND UNIT ADDRESS, so a correspondence supplied for one
    pair can never be silently applied to another, and reversing the operands
    inverts the mapping instead of reusing it. **Ordinal equality is never a
    fallback and constraint similarity is never consulted** -- no mapping means
    no comparison.
    """
    if not corr:
        return None
    a_u, b_u = corr.get("a_unit"), corr.get("b_unit")
    if tuple(frm.addr) == a_u and tuple(to.addr) == b_u:
        return corr.get("a_to_b", {}).get(ordinal)
    if tuple(frm.addr) == b_u and tuple(to.addr) == a_u:
        return corr.get("b_to_a", {}).get(ordinal)
    return None


def _entity_kinds(index, prefix):
    out = set()
    for v in index.get(prefix + ("entity_kind",), []):
        if v.status == "ATOM" and (v.atom or {}).get("op") == "REQUIRES":
            out |= {_norm(x) for x in _values(v.atom)}
    return out


def _context_compatible(ia, ib, key, a_key=None):
    ka = _entity_kinds(ia, ((a_key or key)[0], (a_key or key)[1]))
    kb = _entity_kinds(ib, (key[0], key[1]))
    return not (ka and kb and not (ka & kb))


def _discharge_atom(a_atom, b_atom, dim):
    """(result, proof_kind, cr_anchor, reason). NEVER returns PROVEN_NOT:
    non-entailment is existential and is handled one layer up by a witness."""
    anchor = (DIMENSIONS.get(dim) or {}).get("cr_anchor")
    if pj.canonical_json(a_atom) == pj.canonical_json(b_atom):
        return PROVEN, CR_CONTRACT, anchor, None
    if dim in EQUALITY_ONLY:
        return UNKNOWN, None, anchor, "DIMENSION_EQUALITY_ONLY"

    a_op, b_op = a_atom.get("op"), b_atom.get("op")

    if b_op == "REQUIRES":
        b_vals = _values(b_atom)
        if any(not _vocab_ok(dim, x) for x in b_vals):
            return UNKNOWN, None, anchor, "OPEN_DIMENSION_VALUE"
        if a_op == "REQUIRES":
            a_vals = _values(a_atom)
            if any(not _vocab_ok(dim, x) for x in a_vals):
                return UNKNOWN, None, anchor, "OPEN_DIMENSION_VALUE"
            if all(any(_norm(av) == _norm(bv) for bv in b_vals)
                   for av in a_vals):
                return PROVEN, CR_CONTRACT, anchor, None
            return UNKNOWN, None, anchor, ("DISJUNCTION_NOT_UNIFORM"
                                           if len(a_vals) > 1
                                           else "NO_CORPUS_WITNESS")
        return UNKNOWN, None, anchor, "NO_CORPUS_WITNESS"

    if b_op == "FORBIDS":
        b_vals = _values(b_atom)
        if a_op == "FORBIDS":
            a_vals = _values(a_atom)
            if all(any(_norm(bv) == _norm(av) for av in a_vals)
                   for bv in b_vals):
                return PROVEN, CR_CONTRACT, anchor, None
            return UNKNOWN, None, anchor, "NO_CORPUS_WITNESS"
        if a_op == "REQUIRES" and dim in SINGLE_VALUED_EXHAUSTIVE:
            a_vals = _values(a_atom)
            if all(_norm(av) != _norm(bv) for av in a_vals for bv in b_vals):
                return (PROVEN, CR_CONTRACT,
                        f"{anchor} (closed, single-valued, must-have)", None)
        return UNKNOWN, None, anchor, "NO_CORPUS_WITNESS"

    if b_op == "CARD" and a_op == "CARD":
        ar, br = _card_range(a_atom), _card_range(b_atom)
        if ar is None or br is None:
            return UNKNOWN, None, anchor, "MALFORMED_PAYLOAD"
        if _contains(ar, br):
            return PROVEN, CR_CONTRACT, anchor, None
        return UNKNOWN, None, anchor, "NO_CORPUS_WITNESS"

    if b_op == "INTERVAL" and a_op == "INTERVAL":
        ar, br = _interval_range(a_atom), _interval_range(b_atom)
        if ar is None or br is None:
            return UNKNOWN, None, anchor, "MALFORMED_PAYLOAD"
        if _contains(ar, br):
            return PROVEN, CR_CONTRACT, anchor, None
        return UNKNOWN, None, anchor, "NO_CORPUS_WITNESS"

    return UNKNOWN, None, anchor, "NO_CORPUS_WITNESS"


def _hierarchy_discharges(ia, key, b_atom, dim):
    """The ONE ratified hierarchy step: a required subtype discharges the
    required parent card type. No other edge is asserted."""
    if dim != "card_type" or b_atom.get("op") != "REQUIRES":
        return None
    wanted = {_norm(v) for v in _values(b_atom)}
    for v in ia.get((key[0], key[1], "subtype"), []):
        if v.status != "ATOM" or (v.atom or {}).get("op") != "REQUIRES":
            continue
        subs = _values(v.atom)
        if subs and all(_hierarchy_parents(s) & wanted for s in subs):
            return v
    return None


def _component(kind, key, result, proof_kind=None, cr_anchor=None,
               reason=None, atoms_a=None, atoms_b=None, evidence=None,
               provenance=None):
    return {"kind": kind,
            "scope": {"kind": key[0], "participant": key[1]} if key else None,
            "dimension": key[2] if key else None,
            "result": result, "proof_kind": proof_kind,
            "cr_anchor": cr_anchor, "unknown_reason": reason,
            "atoms_a": atoms_a, "atoms_b": atoms_b,
            "evidence": evidence or [], "provenance": provenance or []}


def _precondition(check, observed, note=None):
    """A structural check that was EVALUATED AND DID NOT BLOCK.

    No result, no proof kind, no anchor, and it never enters the composition.
    A non-blocking check is not a proof.
    """
    return {"check": check, "observed": observed, "note": note}


def _ev(*views):
    return [v.evidence for v in views
            if v is not None and getattr(v, "evidence", None)]


def _prov(*views):
    return [v.provenance for v in views if v is not None and v.provenance]


def entailment_components(a: Unit, b: Unit, ledger=None, corr=None) -> list:
    ia, ib = fact_index(a, ledger), fact_index(b, ledger)
    comps = []
    for key in sorted(set(ib),
                      key=lambda k: (str(k[0]), str(k[1]), str(k[2]))):
        dim = key[2]
        # PARTICIPANT ORDINALS DO NOT CORRESPOND ACROSS OCCURRENCES. They may
        # be compared ONLY through a supplied frozen correspondence; with no
        # mapping the comparison declines, because aligning by ordinal would
        # give the integers a meaning the contract withholds.
        a_key = key
        if key[0] == "PARTICIPANT":
            mate = counterpart_ordinal(corr, b, a, key[1])
            if mate is None:
                comps.append(_component(
                    "ENTAILMENT", key, UNKNOWN,
                    reason="NO_PARTICIPANT_CORRESPONDENCE"))
                continue
            a_key = (key[0], mate, key[2])
        for bv in ib[key]:
            if bv.status == "BLOCKED":
                comps.append(_component("ENTAILMENT", key, UNKNOWN,
                                        reason=bv.reason, atoms_b=bv.atom,
                                        evidence=_ev(bv),
                                        provenance=_prov(bv)))
                continue
            if bv.status == "ABSENT":
                # The consequent constrains nothing on this dimension, so every
                # object satisfies it. A tautology, not a claim about A.
                comps.append(_component(
                    "ENTAILMENT", key, PROVEN, CR_CONTRACT,
                    (DIMENSIONS.get(dim) or {}).get("cr_anchor"),
                    evidence=_ev(bv), provenance=_prov(bv)))
                continue
            if not _context_compatible(ia, ib, key, a_key):
                comps.append(_component("ENTAILMENT", key, UNKNOWN,
                                        reason="CONTEXT_INCOMPATIBLE",
                                        atoms_b=bv.atom, evidence=_ev(bv)))
                continue
            best = None
            for av in ia.get(a_key, []):
                if av.status == "BLOCKED":
                    cand = (UNKNOWN, None, None, av.reason, av)
                elif av.status == "ABSENT":
                    cand = (UNKNOWN, None, None, "NO_CORPUS_WITNESS", av)
                else:
                    r, pk, anc, why = _discharge_atom(av.atom, bv.atom, dim)
                    cand = (r, pk, anc, why, av)
                if best is None or (cand[0] == PROVEN and best[0] != PROVEN):
                    best = cand
            if best is None or best[0] != PROVEN:
                hv = _hierarchy_discharges(ia, a_key, bv.atom, dim)
                if hv is not None:
                    best = (PROVEN, CR_CONTRACT,
                            "CR 205.3 subtype-to-type (ratified hierarchy)",
                            None, hv)
            if best is None:
                comps.append(_component("ENTAILMENT", key, UNKNOWN,
                                        reason="MISSING_FACT",
                                        atoms_b=bv.atom, evidence=_ev(bv),
                                        provenance=_prov(bv)))
                continue
            r, pk, anc, why, av = best
            comps.append(_component(
                "ENTAILMENT", key, r, pk if r == PROVEN else None, anc,
                why if r != PROVEN else None, atoms_a=av.atom,
                atoms_b=bv.atom, evidence=_ev(av, bv),
                provenance=_prov(av, bv)))
    return comps


def kleene(components) -> str:
    rs = [c["result"] for c in components]
    if any(r == PROVEN_NOT for r in rs):
        return PROVEN_NOT
    if rs and all(r == PROVEN for r in rs):
        return PROVEN
    return UNKNOWN


# ==========================================================================
# CORPUS WITNESSES — satisfaction, and the ratified distinguishing role
# ==========================================================================

SATISFIED, VIOLATED, UNDECIDABLE = "SATISFIED", "VIOLATED", "UNDECIDABLE"


def _witness_atom(atom, dim, assign, complete):
    """How one witness bears on one atom, under the ratified decidability law.

    The asymmetry is the ruling's, not a convenience: a forbidden value that is
    PRESENT is an observation and needs nothing else, while proving a required
    value ABSENT needs an evidence-traced complete assignment for that
    dimension. Everything undecidable returns UNDECIDABLE, never VIOLATED.
    """
    if dim not in assign:
        return UNDECIDABLE
    have, op = assign[dim], atom.get("op")
    vals = [_norm(x) for x in _values(atom)]
    if dim in EQUALITY_ONLY:
        # A mismatch on an equality-only dimension is NOT a violation.
        return SATISFIED if any(x in have for x in vals) else UNDECIDABLE
    if op == "REQUIRES":
        if any(x in have for x in vals):
            return SATISFIED
        return VIOLATED if dim in complete else UNDECIDABLE
    if op == "FORBIDS":
        if any(x in have for x in vals):
            return VIOLATED
        return SATISFIED if dim in complete else UNDECIDABLE
    if op == "EQUALITY":
        return SATISFIED if any(x in have for x in vals) else UNDECIDABLE
    if op == "CARD":
        rng = _card_range(atom)
        if rng is None or dim not in complete:
            return UNDECIDABLE
        return SATISFIED if rng[0] <= len(have) <= rng[1] else VIOLATED
    if op == "INTERVAL":
        rng = _interval_range(atom)
        nums = [x for x in have if isinstance(x, int)
                and not isinstance(x, bool)]
        if rng is None or dim not in complete or not nums:
            return UNDECIDABLE
        return (SATISFIED if all(rng[0] <= x <= rng[1] for x in nums)
                else VIOLATED)
    return UNDECIDABLE


def _witness_assignments(witness):
    return {k: [_norm(x) for x in (v if isinstance(v, list) else [v])]
            for k, v in (witness.get("assignments") or {}).items()}


def _witness_bearing(witness, unit: Unit, ledger=None):
    """(all_satisfied, any_violated, notes) over one unit's atoms."""
    assign = _witness_assignments(witness)
    complete = {d for d in (witness.get("complete_dimensions") or [])}
    notes, all_ok, violated = [], True, False
    for f in unit.facts:
        v = read_fact(f, unit, ledger)
        if v.status != "ATOM":
            all_ok = False
            notes.append({"dimension": v.dimension,
                          "why": v.reason or "not an actionable atom"})
            continue
        r = _witness_atom(v.atom, v.dimension, assign, complete)
        if r == VIOLATED:
            violated = True
            all_ok = False
            notes.append({"dimension": v.dimension, "why": "violated"})
        elif r == UNDECIDABLE:
            all_ok = False
            notes.append({"dimension": v.dimension,
                          "why": "undecidable from this witness"})
    return all_ok, violated, notes


def _witness_admissible(witness) -> list:
    bad = []
    if not isinstance(witness, dict):
        return ["witness is not a record"]
    if not witness.get("corpus_ref"):
        bad.append("a corpus witness must pin the corpus_ref it was "
                   "established against")
    if not (witness.get("witness") or {}).get("oracle_id"):
        bad.append("a corpus witness must name its witness identity")
    if not isinstance(witness.get("assignments"), dict) or \
            not witness["assignments"]:
        bad.append("a corpus witness must declare the dimension/value domain "
                   "it relies on")
    cd = witness.get("complete_dimensions")
    if cd is not None and not isinstance(cd, list):
        bad.append("complete_dimensions must be a list of dimension names")
    bad += pj._validate_evidence(witness.get("evidence"), "corpus witness")
    return bad


# ==========================================================================
# THE OPERATIONS
# ==========================================================================

def _record(op, direction, a: Unit, b: Unit, result, components,
            proof_kind=None, reason=None, preconditions=None, **extra):
    rec = {
        "algebra": {"schema": ALGEBRA_NAME, "version": ALGEBRA_VERSION},
        "projection": {"schema": pj.SCHEMA_NAME, "version": pj.SCHEMA_VERSION},
        "operation": op, "direction": direction, "result": result,
        "proof_kind": proof_kind,
        "inputs": {"a": a.id, "b": b.id},
        "components": sorted(components, key=pj.canonical_json),
        "preconditions": sorted(preconditions or [], key=pj.canonical_json),
        "evidence": [], "unknown_reason": reason,
    }
    seen, ev = set(), []
    for c in rec["components"]:
        for e in c.get("evidence", []):
            k = pj.canonical_json(e)
            if k not in seen:
                seen.add(k)
                ev.append(e)
    rec["evidence"] = ev
    rec.update(extra)
    if result != UNKNOWN:
        rec.pop("unknown_reason", None)
    assert_no_native_identifiers(rec)
    assert_preconditions_are_not_proofs(rec)
    assert_proof_trace(rec)
    return rec


def _order(a: Unit, b: Unit):
    return (a, b) if a.id <= b.id else (b, a)


def _first_reason(comps):
    for c in sorted(comps, key=pj.canonical_json):
        if c["result"] == UNKNOWN and c.get("unknown_reason"):
            return c["unknown_reason"]
    return None


def _audit_preconditions(a: Unit, b: Unit, corr=None) -> list:
    """Structural observations, recorded so the trace stays legible.

    NONE of these is a proof and none influences a verdict. Cost, relations,
    heads and participant ordinals live here precisely because the law refuses
    them as comparison conditions.
    """
    return [
        _precondition("cost_regions_observed", [len(a.regions), len(b.regions)],
                      "structural only; no cost comparison and no absence "
                      "claim exists on either side"),
        _precondition("relation_edges_observed",
                      [len(a.relations), len(b.relations)],
                      "absence of an edge is never proof of no relation"),
        _precondition("action_head_sequences",
                      [list(a.heads), list(b.heads)],
                      "printed order; no action comparison is authorized"),
        _precondition("participant_ordinal_sets",
                      [list(a.participants), list(b.participants)],
                      "occurrence-local integers; equal ordinals are never "
                      "evidence and never an inference rule"),
        _precondition("participant_correspondence_supplied", bool(corr),
                      "an explicitly supplied frozen mapping, or none. There "
                      "is no global lookup, and the mapping itself proves no "
                      "semantic relation"),
    ]


def entails(a: Unit, b: Unit, witness=None, ledger=None,
            corr=None) -> dict:
    """OP_ENTAILS. DIRECTIONAL: does a's constraint set entail b's?"""
    comps = entailment_components(a, b, ledger, corr)
    pre = _audit_preconditions(a, b, corr)
    result = kleene(comps) if comps else UNKNOWN
    proof_kind = CR_CONTRACT if result == PROVEN else None
    reason, extra = None, {}
    if not comps:
        result, reason = UNKNOWN, "NO_COMPARABLE_CONTENT"
    elif result != PROVEN and witness is not None:
        bad = _witness_admissible(witness)
        if bad:
            result, reason = UNKNOWN, "WITNESS_INADMISSIBLE"
            extra["witness_rejected"] = bad
        else:
            sat_a, _va, _na = _witness_bearing(witness, a, ledger)
            _sb, viol_b, notes = _witness_bearing(witness, b, ledger)
            if sat_a and viol_b:
                result, proof_kind = PROVEN_NOT, CORPUS_WITNESS
                extra["witness"] = witness
                extra["corpus_ref"] = witness["corpus_ref"]
                comps.append(_component(
                    "DISTINGUISHING_WITNESS", None, PROVEN_NOT,
                    CORPUS_WITNESS, None, None,
                    evidence=[witness["evidence"]],
                    provenance=[{
                        "witness_notes": notes,
                        "completeness_declared": sorted(
                            witness.get("complete_dimensions") or []),
                    }]))
            elif not sat_a:
                reason = "WITNESS_DOES_NOT_SATISFY"
            else:
                reason = "WITNESS_COMPLETENESS_MISSING"
    elif result != PROVEN:
        reason = _first_reason(comps) or "NO_CORPUS_WITNESS"
    return _record("OP_ENTAILS", "A_ENTAILS_B", a, b, result, comps,
                   proof_kind, reason, preconditions=pre, **extra)


def _coverage_components(a: Unit, b: Unit, ledger=None, corr=None,
                        _skip_participants=False) -> list:
    """A dimension actionable on one side and missing on the other is
    MISSING_FACT, never ABSENT.

    CORRESPONDENCE-AWARE, and it has to be. While all participant comparison
    was universally refused, skipping participant scopes here was safe because
    nothing could be proven through them anyway. The moment a correspondence
    can be supplied that stops being true: an actionable restricted participant
    that is UNBOUND on either side must prevent eligibility equality, and an
    extra participant may never be silently ignored.

    `_skip_participants` exists ONLY to rig that: it reproduces the old
    skipping behaviour so the control can show it turning red.
    """
    ia, ib = fact_index(a, ledger), fact_index(b, ledger)
    comps = []
    for key in sorted(set(ia) | set(ib),
                      key=lambda k: (str(k[0]), str(k[1]), str(k[2]))):
        if key[0] == "PARTICIPANT":
            continue
        ha = any(v.status in ("ATOM", "ABSENT") for v in ia.get(key, []))
        hb = any(v.status in ("ATOM", "ABSENT") for v in ib.get(key, []))
        if ha != hb:
            comps.append(_component("COVERAGE", key, UNKNOWN,
                                    reason="MISSING_FACT"))
    if _skip_participants:
        return comps
    for side, (idx, unit, other_idx, other) in (
            ("a", (ia, a, ib, b)), ("b", (ib, b, ia, a))):
        for key in sorted(idx, key=lambda k: (str(k[0]), str(k[1]),
                                              str(k[2]))):
            if key[0] != "PARTICIPANT":
                continue
            if not any(v.status in ("ATOM", "ABSENT") for v in idx[key]):
                continue
            mate = counterpart_ordinal(corr, unit, other, key[1])
            if mate is None:
                comps.append(_component(
                    "COVERAGE", key, UNKNOWN,
                    reason="NO_PARTICIPANT_CORRESPONDENCE"))
                continue
            other_key = (key[0], mate, key[2])
            if not any(v.status in ("ATOM", "ABSENT")
                       for v in other_idx.get(other_key, [])):
                comps.append(_component("COVERAGE", key, UNKNOWN,
                                        reason="MISSING_FACT"))
    return comps


def _actionable(a: Unit, b: Unit, ledger=None) -> bool:
    for u in (a, b):
        for f in u.facts:
            if read_fact(f, u, ledger).status in ("ATOM", "ABSENT"):
                return True
    return False


def _carried_witness(*records):
    for r in records:
        if r.get("proof_kind") == CORPUS_WITNESS and r.get("corpus_ref"):
            return {"witness": r["witness"], "corpus_ref": r["corpus_ref"]}
    return {}


def eligibility_equality(a: Unit, b: Unit, witness=None, ledger=None,
                         corr=None) -> dict:
    """OP_ELIGIBILITY_EQUALITY — the ONLY ratified positive equality operation.

    Named in full at every site. There is no bare whole-unit equality operation
    and none may be added: a shorter name is exactly how the refused whole-unit
    reading creeps back in.
    """
    a, b = _order(a, b)
    ab = entails(a, b, witness, ledger, corr)
    ba = entails(b, a, witness, ledger, corr)
    comps = [
        # A COMPOSITION node, not a contract proof: it carries no proof kind,
        # because the sub-record it summarizes carries the proof and the
        # anchors. Giving it one would be a proof kind with nothing behind it.
        _component("DIRECTION_A_TO_B", None, ab["result"], None, None,
                   ab.get("unknown_reason")),
        _component("DIRECTION_B_TO_A", None, ba["result"], None, None,
                   ba.get("unknown_reason")),
    ]
    comps += _coverage_components(a, b, ledger, corr)
    if not _actionable(a, b, ledger):
        comps.append(_component("VACUITY", None, UNKNOWN,
                                reason="NO_COMPARABLE_CONTENT"))
    result = kleene(comps)
    pk = CR_CONTRACT if result == PROVEN else (
        CORPUS_WITNESS if result == PROVEN_NOT else None)
    extra = _carried_witness(ab, ba) if result == PROVEN_NOT else {}
    return _record("OP_ELIGIBILITY_EQUALITY", "SYMMETRIC", a, b, result,
                   comps + ab["components"] + ba["components"], pk,
                   _first_reason(comps) if result == UNKNOWN else None,
                   preconditions=_audit_preconditions(a, b, corr),
                   directions={"a_to_b": ab["result"], "b_to_a": ba["result"]},
                   **extra)


def _contradiction_components(a: Unit, b: Unit, ledger=None) -> list:
    """CR contract contradictions -- the ONLY admissible proof of empty
    intersection. Corpus absence is inadmissible in both directions."""
    ia, ib = fact_index(a, ledger), fact_index(b, ledger)
    comps = []
    for key in sorted(set(ia) & set(ib),
                      key=lambda k: (str(k[0]), str(k[1]), str(k[2]))):
        if key[0] == "PARTICIPANT" or not _context_compatible(ia, ib, key):
            continue
        dim = key[2]
        anchor = (DIMENSIONS.get(dim) or {}).get("cr_anchor")
        for av, bv in itertools.product(ia[key], ib[key]):
            if av.status != "ATOM" or bv.status != "ATOM":
                continue
            hit = _contradiction(av.atom, bv.atom, dim, anchor)
            if hit:
                comps.append(_component(
                    "CR_CONTRADICTION", key, PROVEN_NOT, CR_CONTRACT, hit,
                    None, atoms_a=av.atom, atoms_b=bv.atom,
                    evidence=_ev(av, bv), provenance=_prov(av, bv)))
    return comps


def _contradiction(x, y, dim, anchor):
    """The repaired contradiction test.

    THE DISJUNCTION RULE IS THE REPAIR. A required value SET contradicts a
    forbidding constraint only when EVERY admissible alternative is eliminated:
    requiring `artifact or creature` against forbidding `artifact` leaves
    `creature` satisfiable, so the intersection is not proven empty. The
    quarantined implementation proved contradiction on ANY overlap, which is a
    false PROVEN_NOT.
    """
    for lo, hi in ((x, y), (y, x)):
        if lo.get("op") == "REQUIRES" and hi.get("op") == "FORBIDS":
            req = {_norm(v) for v in _values(lo)}
            forb = {_norm(v) for v in _values(hi)}
            if req and req <= forb:
                return ("contract 13 atom semantics: every required "
                        "alternative is forbidden")
    if x.get("op") == y.get("op") == "REQUIRES" and \
            dim in SINGLE_VALUED_EXHAUSTIVE:
        xs = {_norm(v) for v in _values(x)}
        ys = {_norm(v) for v in _values(y)}
        if xs and ys and not (xs & ys):
            return (f"{anchor}: different values on a closed, single-valued, "
                    f"must-have dimension")
    if x.get("op") == y.get("op") == "CARD":
        xr, yr = _card_range(x), _card_range(y)
        if xr and yr and _disjoint(xr, yr):
            return f"{anchor}: disjoint cardinality ranges"
    if x.get("op") == y.get("op") == "INTERVAL":
        xr, yr = _interval_range(x), _interval_range(y)
        if xr and yr and _disjoint(xr, yr):
            return f"{anchor}: disjoint intervals"
    return None


def intersection(a: Unit, b: Unit, witness=None, ledger=None,
                 corr=None) -> dict:
    """OP_INTERSECTION. One proposition, two poles."""
    a, b = _order(a, b)
    pre = _audit_preconditions(a, b, corr)
    contras = _contradiction_components(a, b, ledger)
    if contras:
        return _record("OP_INTERSECTION", "SYMMETRIC", a, b, PROVEN_NOT,
                       contras, CR_CONTRACT, None, preconditions=pre,
                       proof_label="EMPTY_INTERSECTION_PROVEN")
    comps = [_component("CR_CONTRADICTION", None, UNKNOWN,
                        reason="NO_CR_CONTRADICTION")]
    reason, extra = "NO_CORPUS_WITNESS", {}
    if witness is not None:
        bad = _witness_admissible(witness)
        if bad:
            reason, extra = "WITNESS_INADMISSIBLE", {"witness_rejected": bad}
        else:
            sat_a, _x, na = _witness_bearing(witness, a, ledger)
            sat_b, _y, nb = _witness_bearing(witness, b, ledger)
            if sat_a and sat_b:
                return _record(
                    "OP_INTERSECTION", "SYMMETRIC", a, b, PROVEN,
                    [_component("CORPUS_WITNESS", None, PROVEN,
                                CORPUS_WITNESS, None, None,
                                evidence=[witness["evidence"]],
                                provenance=[{"assignments_relied_on":
                                             sorted(witness["assignments"])}])],
                    CORPUS_WITNESS, None, preconditions=pre,
                    proof_label="NONEMPTY_INTERSECTION_PROVEN",
                    witness=witness, corpus_ref=witness["corpus_ref"])
            reason = "WITNESS_DOES_NOT_SATISFY"
            extra["witness_notes"] = {"a": na, "b": nb}
    return _record("OP_INTERSECTION", "SYMMETRIC", a, b, UNKNOWN, comps,
                   None, reason, preconditions=pre, **extra)


def overlap(a: Unit, b: Unit, witness=None, ledger=None, corr=None) -> dict:
    r = intersection(a, b, witness, ledger, corr)
    r["reads_pole"] = "NONEMPTY_INTERSECTION_PROVEN"
    return r


def disjoint(a: Unit, b: Unit, ledger=None, corr=None) -> dict:
    """Takes NO witness: a witness is inadmissible for disjointness, so the
    parameter does not exist rather than being ignored."""
    r = intersection(a, b, None, ledger, corr)
    r["reads_pole"] = "EMPTY_INTERSECTION_PROVEN"
    return r


_DISPATCH = {"OP_ENTAILS": entails,
             "OP_ELIGIBILITY_EQUALITY": eligibility_equality,
             "OP_INTERSECTION": intersection}


def compare(op: str, a: Unit, b: Unit, **kw) -> dict:
    if op not in OPERATIONS or op not in _DISPATCH:
        fc.halt(f"comparison operation {op!r} is not registered in "
                f"{ALGEBRA_PATH.name}. The authorized set is "
                f"{sorted(OPERATIONS)}. Minting an operator to complete a "
                f"table is a ratification, not an implementation detail.")
    return _DISPATCH[op](a, b, **kw)


# ==========================================================================
# RECORD DISCIPLINE
# ==========================================================================

def assert_no_native_identifiers(rec) -> None:
    for _path, key in pj._walk_keys(rec):
        if str(key).lower() in pj.FORBIDDEN_NATIVE:
            fc.halt(f"proof record exposes candidate-native field {key!r}")
    for s in pj._walk_strings(rec):
        if s.lower() in pj.FORBIDDEN_NATIVE:
            fc.halt(f"proof record exposes candidate-native value {s!r}")


def assert_preconditions_are_not_proofs(rec) -> None:
    """A precondition may never acquire a verdict, a proof kind or an anchor."""
    for pcd in rec.get("preconditions", []):
        for banned in ("result", "proof_kind", "cr_anchor", "unknown_reason"):
            if banned in pcd:
                fc.halt(f"a precondition carries {banned!r}. A non-blocking "
                        f"check is not a proof and never enters the "
                        f"three-valued composition.")


def assert_proof_trace(rec) -> None:
    if rec["result"] == UNKNOWN:
        if not rec.get("unknown_reason"):
            fc.halt("an UNKNOWN verdict must carry its reason class")
        if rec["unknown_reason"] not in REASONS:
            fc.halt(f"unknown_reason {rec['unknown_reason']!r} is not a "
                    f"registered reason class")
        return
    if rec.get("proof_kind") not in PROOF_KINDS:
        fc.halt(f"a {rec['result']} verdict must carry one of "
                f"{list(PROOF_KINDS)}; got {rec.get('proof_kind')!r}")
    if rec["proof_kind"] == CORPUS_WITNESS and not rec.get("corpus_ref"):
        fc.halt("a corpus-witness verdict must pin the corpus_ref it was "
                "established against")
    if not rec.get("evidence"):
        fc.halt(f"a {rec['result']} verdict carries no evidence trace")
    for c in rec["components"]:
        if c.get("proof_kind") == CR_CONTRACT and not c.get("cr_anchor"):
            fc.halt(f"a {c['result']} component of kind {c['kind']!r} claims a "
                    f"CONTRACT proof and cites NO anchor. A contract proof "
                    f"must name a real applicable rule, and prose is never "
                    f"one. (A corpus witness is anchored by its corpus_ref and "
                    f"identity instead, both checked above.)")


def assert_not_a_projection_fact(doc: dict, rec: dict) -> None:
    rig = copy.deepcopy(doc)
    rig["occurrences"][0]["facts"][0]["B2_verdict"] = rec["result"]
    if pj.validate(rig) == []:
        fc.halt("a derived comparison verdict was accepted into the canonical "
                "projection substrate.")


# ==========================================================================
# DERIVED CONSUMER LAYER — derived output, never a key
# ==========================================================================

def b1(a: Unit, b: Unit, witness=None, ledger=None, corr=None) -> dict:
    """B1 — PARTIAL IN v1. The positive pole cannot be reached."""
    r = eligibility_equality(a, b, witness, ledger, corr)
    verdict = PROVEN_NOT if r["result"] == PROVEN_NOT else UNKNOWN
    return {
        "question": "B1", "verdict": verdict,
        "positive_arm": "UNAVAILABLE_IN_V1",
        "_law": "there is no positive whole-unit semantic-equality proof in "
                "v1. Identical heads, identical participant integers, an "
                "absent cost region, an absent relation edge and matching "
                "visible fields are each refused as positive evidence, because "
                "the projection does not represent all uncontracted semantic "
                "residue.",
        "unknown_reason": (None if verdict == PROVEN_NOT
                           else r.get("unknown_reason") or
                           "NO_CONTRACTED_COMPARISON_LAW"),
        "record": r,
    }


B2_LABELS = ("EQUAL", "BROADER", "NARROWER", "OVERLAPPING", "DISJOINT",
             "UNKNOWN")


def b2(subject: Unit, counterpart: Unit, witness=None, ledger=None,
       corr=None) -> dict:
    """B2 — is the SUBJECT's eligibility broader/narrower/... than the
    counterpart's?

    Orientation audited against the consumer contract's own wording: the
    question is about A's eligibility RELATIVE TO B's, so BROADER means the
    subject admits at least everything the counterpart admits — which is
    entailment FROM the counterpart TO the subject.
    """
    s_to_c = entails(subject, counterpart, witness, ledger, corr)
    c_to_s = entails(counterpart, subject, witness, ledger, corr)
    eq = eligibility_equality(subject, counterpart, witness, ledger, corr)
    inter = intersection(subject, counterpart, witness, ledger, corr)

    if eq["result"] == PROVEN:
        label = "EQUAL"
    elif c_to_s["result"] == PROVEN and s_to_c["result"] == PROVEN_NOT:
        label = "BROADER"
    elif s_to_c["result"] == PROVEN and c_to_s["result"] == PROVEN_NOT:
        label = "NARROWER"
    elif inter["result"] == PROVEN_NOT:
        label = "DISJOINT"
    elif inter["result"] == PROVEN:
        label = "OVERLAPPING"
    else:
        label = "UNKNOWN"
    return {
        "question": "B2", "subject": subject.id, "counterpart": counterpart.id,
        "relation_label": label,
        "_label_law": "a derived answer label for one consumer question, not a "
                      "comparison verdict. BROADER and NARROWER are STRICT: "
                      "the containing direction PROVEN and the reverse "
                      "PROVEN_NOT. EQUAL is never mapped to OVERLAPPING.",
        "eligibility_equality": eq["result"],
        "subject_entails_counterpart": s_to_c["result"],
        "counterpart_entails_subject": c_to_s["result"],
        "intersection": inter["result"],
        "per_dimension": [c for c in s_to_c["components"]
                          if c["kind"] == "ENTAILMENT"],
        "records": {"subject_to_counterpart": s_to_c,
                    "counterpart_to_subject": c_to_s,
                    "eligibility_equality": eq, "intersection": inter},
    }


def b3(subject: Unit, counterpart: Unit, witness=None, ledger=None) -> dict:
    """B3 — PARTIAL BY LAW. The action arm is not implemented and not minted."""
    if subject.head_disposition != "PRESENT" or \
            counterpart.head_disposition != "PRESENT":
        identity = "UNAVAILABLE"
    elif subject.heads == counterpart.heads:
        identity = "IDENTICAL"
    else:
        identity = "DIFFERENT"
    return {
        "question": "B3", "derivable": "PARTIAL",
        "action_equivalence": {
            "verdict": UNKNOWN,
            "unknown_reason": "NO_CONTRACTED_COMPARISON_LAW",
            "why": "no action-equivalence comparison is authorized; the "
                   "operator is not minted here",
        },
        "action_head_structural_report": {
            "value": identity,
            "_law": "NON-VERDICT audit metadata. It never influences a "
                    "semantic result: an identical sequence proves nothing and "
                    "a different one disproves nothing.",
        },
        "eligibility": b2(subject, counterpart, witness, ledger),
    }


B4_GROUPING = ALGEBRA["derived_question_layer"]["B4"]["summary_grouping"]


def b4(subject: Unit, counterpart: Unit, witness=None, ledger=None) -> dict:
    """B4 — the per-dimension verdict table, plus a PRESENTATION grouping."""
    s_to_c = entails(subject, counterpart, witness, ledger)
    c_to_s = entails(counterpart, subject, witness, ledger)
    per = {}
    for rec, side in ((s_to_c, "subject_to_counterpart"),
                      (c_to_s, "counterpart_to_subject")):
        for c in rec["components"]:
            if c["kind"] == "ENTAILMENT":
                per.setdefault(c["dimension"], {})[side] = c["result"]
    equal_dims = sorted(d for d, v in per.items()
                        if v.get("subject_to_counterpart")
                        == v.get("counterpart_to_subject") == PROVEN)
    inter = intersection(subject, counterpart, witness, ledger)
    differing = sorted({c["dimension"] for c in inter["components"]
                        if c["kind"] == "CR_CONTRADICTION"
                        and c["result"] == PROVEN_NOT and c["dimension"]})
    grouped = {g: sorted(set(dims) & set(differing))
               for g, dims in B4_GROUPING.items() if not g.startswith("_")}
    return {
        "question": "B4",
        "per_dimension": dict(sorted(per.items())),
        "dimensions_equal_proven": equal_dims,
        "dimensions_differing_proven": differing,
        "summary_grouping": grouped,
        "_grouping_law": "PRESENTATION ONLY. It groups already-authorized "
                         "per-dimension verdicts for display and changes no "
                         "semantic truth; the table above does not depend on "
                         "it.",
        "records": {"subject_to_counterpart": s_to_c,
                    "counterpart_to_subject": c_to_s, "intersection": inter},
    }


def c1(pair, direction: str, witness=None, ledger=None) -> dict:
    """C1 — what prevents the replacement, in a NAMED direction."""
    x, y = pair
    if direction not in ("X_REPLACES_Y", "Y_REPLACES_X"):
        fc.halt(f"C1 direction {direction!r} must be named explicitly; a "
                f"directional operation may never silently reverse operands.")
    replacement, original = (x, y) if direction == "X_REPLACES_Y" else (y, x)
    ent = entails(replacement, original, witness, ledger)
    blockers = [c for c in ent["components"] if c["result"] != PROVEN]
    return {
        "question": "C1", "direction": direction,
        "replacement": replacement.id, "original": original.id,
        "blockers": sorted(blockers, key=pj.canonical_json),
        "blocker_count": len(blockers),
        "cost_residue": _precondition(
            "cost_regions_observed",
            [len(replacement.regions), len(original.regions)],
            "the authorized structural residue condition; never a compared "
            "dimension"),
        "_empty_is_not_a_claim": "an EMPTY blocker list is NEVER a positive "
                                 "equality or replacement claim. No positive "
                                 "strict-replacement relation is contracted.",
        "record": ent,
    }


def c2(unit: Unit) -> dict:
    kinds = sorted({r.get("kind") for r in unit.relations})
    linked = [r for r in unit.relations
              if r.get("kind") in ("CR607_LINKAGE", "COREFERENCE")]
    return {"question": "C2", "occurrence": unit.id, "relation_kinds": kinds,
            "linked_edges": len(linked), "derivable": "STRUCTURAL",
            "_absence_law": "absence of an edge is NOT proof of no linkage"}


def c3(proj: Projection, a: Unit, b: Unit) -> dict:
    """C3 — from POSITIVE projected choice-group structure only.

    The comparator parses no Oracle text; it reads the Packet-4 generated
    structural record. INDEPENDENT is NOT derivable in v1 and is reported
    rather than minted: absence of a group is not proof of independence.
    """
    aa, ba = list(a.addr), list(b.addr)
    groups = [g for g in proj.choice_groups
              if aa in [list(_m(m)) for m in g.get("members", [])]
              and ba in [list(_m(m)) for m in g.get("members", [])]]
    if not groups:
        return _c3(UNKNOWN, "NO_CONTRACTED_COMPARISON_LAW",
                   "the two units share no projected choice group. ABSENCE OF "
                   "A GROUP IS NOT PROOF OF INDEPENDENCE.")
    if len(groups) > 1:
        return _c3(UNKNOWN, "NO_CONTRACTED_COMPARISON_LAW",
                   "the two units share more than one projected group")
    g = groups[0]
    sel = g["selection"]
    options = {_m(m)[2] for m in g["members"]}
    if a.addr[2] == b.addr[2]:
        return _c3("CUMULATIVE", None,
                   "both units sit in ONE option, so if that option is chosen "
                   "both resolve", g)
    if sel["max"] == 1:
        return _c3("ALTERNATIVE", None,
                   "the group's selection permits at most one option, and the "
                   "units sit in different options", g)
    if sel["min"] == len(options):
        return _c3("CUMULATIVE", None,
                   "the selection minimum equals the option count, so every "
                   "option is chosen", g)
    return _c3(UNKNOWN, "NO_CONTRACTED_COMPARISON_LAW",
               "the selection cardinality permits, but does not require, both "
               "options", g)


def _m(member):
    return (member["oracle_id"], member["face"], member["paragraph"],
            member["clause"])


def _c3(value, reason, why, group=None):
    return {"question": "C3", "value": value, "unknown_reason": reason,
            "why": why,
            "independent_arm": "NOT_DERIVABLE_IN_V1",
            "_independent_law": "nothing the projection carries positively "
                                "establishes independent structure, and "
                                "absence of a choice group is never proof of "
                                "independence. The arm is reported, not "
                                "minted.",
            "selection": (group or {}).get("selection")}


def discovery1(a: Unit, b: Unit, ledger=None) -> dict:
    a, b = _order(a, b)
    pool = []
    for u in (a, b):
        for f in u.facts:
            v = read_fact(f, u, ledger)
            if v.status != "ATOM" or v.scope_kind != "OCCURRENCE":
                continue
            pool.append((v.key, v.atom))
            if v.dimension == "subtype" and v.atom.get("op") == "REQUIRES":
                for s in _values(v.atom):
                    for parent in _hierarchy_parents(s):
                        pool.append(((v.scope_kind, v.participant,
                                      "card_type"),
                                     {"op": "REQUIRES", "value": parent}))
    shared, seen = [], set()
    for key, atom in pool:
        sig = pj.canonical_json([key, atom])
        if sig in seen:
            continue
        seen.add(sig)
        target = Unit({"occurrence": {"oracle_id": "shared", "face": 0,
                                      "paragraph": 0, "clause": 0},
                       "participants": [], "action_heads": [],
                       "action_head_disposition": "UNRESOLVED",
                       "facts": [{"dimension": key[2], "atom": atom,
                                  "disposition": "PRESENT",
                                  "scope": {"kind": "OCCURRENCE"},
                                  "derivation_class": "EXTRACT-4",
                                  "provenance_class": "rule-derived",
                                  "evidence": pj._evidence()}]}, a.role)
        if kleene(entailment_components(a, target, ledger)) == PROVEN and \
                kleene(entailment_components(b, target, ledger)) == PROVEN:
            shared.append({"dimension": key[2], "scope": key[0], "atom": atom})
    shared.sort(key=pj.canonical_json)
    return {"question": "DISCOVERY-1", "shared_atoms": shared,
            "shared_count": len(shared),
            "index_shaped": all(not isinstance(s["atom"].get("value"),
                                               (list, dict))
                                for s in shared),
            "_scope_law": "occurrence-scoped atoms only; participant-scoped "
                          "atoms have no cross-occurrence correspondence."}


def e1_domain() -> dict:
    if not PAIRS_PATH.exists():
        fc.halt(f"no frozen pairing at {PAIRS_PATH}")
    d = json.loads(PAIRS_PATH.read_text(encoding="utf-8"))
    sem = sorted({tuple(sorted(x)) for t in ("S0", "S1", "S2")
                  for x in d["pairs"][t]})
    ctrl = {tuple(sorted(x)) for x in d["pairs"]["PAIR_K_CHAIN"]}
    return {"unique_semantic_pairs": len(sem),
            "control_tranche_pairs_excluded_from_domain": len(ctrl - set(sem)),
            "instancing": "ONE trace per unordered pair",
            "pairs_sha256": d["pairs_sha256"]}


def e1_trace(records, pair=None) -> dict:
    recs = records if isinstance(records, (list, tuple)) else [records]
    steps, bad = [], []
    for rec in recs:
        for c in rec["components"]:
            for e in c.get("evidence", []):
                occ = (e or {}).get("occurrence") or {}
                span = (e or {}).get("span") or {}
                if (e or {}).get("category") == "ORACLE_TEXT":
                    if e.get("view") != "RAW_ORACLE":
                        bad.append("normalization presented as evidence")
                    if not isinstance(span.get("start"), int):
                        bad.append("evidence without a deterministic span")
                    if not occ.get("oracle_id"):
                        bad.append("evidence that does not locate its "
                                   "occurrence")
                steps.append({"operation": rec["operation"],
                              "result": rec["result"], "component": c["kind"],
                              "dimension": c.get("dimension"),
                              "scope": c.get("scope"),
                              "cr_anchor": c.get("cr_anchor"),
                              "proof_kind": c.get("proof_kind"),
                              "evidence_category": (e or {}).get("category"),
                              "evidence_view": (e or {}).get("view"),
                              "occurrence": [occ.get("oracle_id"),
                                             occ.get("face"),
                                             occ.get("paragraph"),
                                             occ.get("clause")],
                              "span": [span.get("start"), span.get("end")]})
    if bad:
        fc.halt("the trace is not producible:\n  - " + "\n  - ".join(sorted(set(bad))))
    steps.sort(key=pj.canonical_json)
    return {"question": "E1", "pair": list(pair) if pair else None,
            "trace_steps": steps, "step_count": len(steps),
            "_form": "a trace/provenance property, never a prose gold answer"}


def honesty1(a: Unit, b: Unit, ledger=None) -> dict:
    r = eligibility_equality(a, b, None, ledger)
    blocked = [c for c in r["components"]
               if c.get("unknown_reason") in
               ("DISPOSITION_NOT_ACTIONABLE", "ABSENCE_NOT_EARNED",
                "ADJUDICATION_PAYLOAD_UNREADABLE")]
    return {"question": "HONESTY-1",
            "non_actionable_components": sorted(blocked, key=pj.canonical_json),
            "blocks_strict_claim": r["result"] != PROVEN,
            "eligibility_equality": r["result"]}


# ==========================================================================
# FIXTURES — synthetic only
# ==========================================================================

OID_A = "00000000-0000-0000-0000-00000000000a"
OID_B = "00000000-0000-0000-0000-00000000000b"


def _part(ordinal, a, b, oid, clause=0):
    return {"ordinal": ordinal,
            "anchor": {"category": "ORACLE_TEXT", "view": "RAW_ORACLE",
                       "occurrence": {"oracle_id": oid, "face": 0,
                                      "paragraph": 0, "clause": clause},
                       "span": {"start": a, "end": b}}}


def _doc(oid, facts, role="CANDIDATE_EXPORT", heads=("destroy",), regions=(),
         relations=(), participants=(), clause=0, groups=None, occs=None):
    d = {"schema": pj.SCHEMA_NAME, "version": pj.SCHEMA_VERSION,
         "artifact_role": role,
         "occurrences": occs or [{
             "occurrence": {"oracle_id": oid, "face": 0, "paragraph": 0,
                            "clause": clause},
             "participants": [_part(i, 10 * i, 10 * i + 5, oid, clause)
                              for i in participants],
             "action_heads": [
                 {"head": h, "cr_anchor": "CR 701",
                  "derivation_class": "EXTRACT-1",
                  "evidence": pj._evidence(oid)} for h in heads],
             "action_head_disposition": "PRESENT" if heads else "UNRESOLVED",
             "facts": facts, "structural_regions": list(regions),
             "relations": list(relations)}]}
    if groups:
        d["choice_groups"] = groups
    return d


def _f(dim, op, value, oid, disposition="PRESENT", scope=None, **extra):
    f = {"dimension": dim, "atom": {"op": op, "value": value},
         "disposition": disposition, "scope": scope or {"kind": "OCCURRENCE"},
         "derivation_class": "EXTRACT-1", "provenance_class": "rule-derived",
         "evidence": pj._evidence(oid)}
    f.update(extra)
    return f


def _unit(doc):
    return next(iter(load_document(doc).units.values()))


def _cost_region(oid):
    return {"role": "COST", "cr_anchors": ["CR 113.3b"],
            "derivation_class": "EXTRACT-0",
            "evidence": pj._evidence(oid, 0, 9)}


def _witness(assignments, complete=(), oid="00000000-0000-0000-0000-0000000000cc"):
    return {"corpus_ref": fcb.corpus_ref_current(),
            "witness": {"oracle_id": oid}, "assignments": assignments,
            "complete_dimensions": list(complete),
            "evidence": pj._evidence(oid)}


# ==========================================================================
# SELFTEST
# ==========================================================================

def selftest() -> int:
    fails = []

    def check(name, ok, detail=""):
        print(f"  [{'ok' if ok else 'FAIL'}] {name}"
              + (f"  <- {detail}" if detail and not ok else ""))
        if not ok:
            fails.append(name)

    def halts(fn, *a, **kw):
        try:
            fn(*a, **kw)
            return False
        except SystemExit:
            return True

    print("=" * 74)
    print("AQ4 COMPARISON ALGEBRA — CONTROLS (repaired; each rigged red)")
    print("=" * 74)

    print("\nLAW / DEPENDENCY")
    check(f"ALG.PROJECTION_VERSION_PINNED the algebra pins projection "
          f"{pj.SCHEMA_VERSION} and refuses any other",
          ALGEBRA["projection_dependency"]["version"] == "3.0.0"
          == pj.SCHEMA_VERSION)
    check("ALG.PROJECTION_VERSION_PINNED-RIG a stale payload shape is refused "
          "by the PROJECTION validator, not re-implemented here",
          halts(_unit, _doc(OID_A, [_f("color", "CARD", 1, OID_A)])))
    check(f"ALG.NO_GENERIC_UNIT_EQUALITY no whole-unit equality operation is "
          f"registered ({sorted(OPERATIONS)})",
          set(OPERATIONS) == {"OP_ENTAILS", "OP_ELIGIBILITY_EQUALITY",
                              "OP_INTERSECTION"})
    check("ALG.NO_GENERIC_UNIT_EQUALITY-RIG asking for one is refused",
          halts(compare, "OP_EQUALITY",
                _unit(_doc(OID_A, [_f("card_type", "REQUIRES", "creature", OID_A)])),
                _unit(_doc(OID_B, [_f("card_type", "REQUIRES", "creature", OID_B)]))))

    ua = _unit(_doc(OID_A, [_f("card_type", "REQUIRES", "creature", OID_A)]))
    ub = _unit(_doc(OID_B, [_f("card_type", "REQUIRES", "creature", OID_B)]))

    print("\nB1 — PARTIAL BY LAW")
    r = b1(ua, ub)
    check("ALG.B1_VISIBLE_IDENTITY_NOT_PROVEN identical visible projections do "
          "NOT yield B1 PROVEN", r["verdict"] == UNKNOWN
          and r["positive_arm"] == "UNAVAILABLE_IN_V1", r["verdict"])
    check("ALG.B1_VISIBLE_IDENTITY_NOT_PROVEN-RIG the underlying eligibility "
          "equality IS proven on the same input, so the refusal is B1's law "
          "and not a broken fixture",
          eligibility_equality(ua, ub)["result"] == PROVEN)
    ident = _unit(_doc(OID_B, [_f("card_type", "REQUIRES", "creature", OID_B)],
                       heads=("destroy",), participants=(0, 1)))
    check("ALG.B1_VISIBLE_IDENTITY_NOT_PROVEN identical heads and participant "
          "sets add nothing", b1(ua, ident)["verdict"] == UNKNOWN)
    check("ALG.B1_VISIBLE_IDENTITY_NOT_PROVEN B1 has no PROVEN branch at all",
          "PROVEN" not in {b1(ua, u)["verdict"]
                           for u in (ub, ident)} - {PROVEN_NOT, UNKNOWN})

    print("\nELIGIBILITY EQUALITY")
    empty_a = _unit(_doc(OID_A, []))
    empty_b = _unit(_doc(OID_B, []))
    check("ALG.ELIGIBILITY_EMPTY_NOT_EQUAL two projection-empty constraint "
          "sets are UNKNOWN, not EQUAL",
          eligibility_equality(empty_a, empty_b)["result"] == UNKNOWN)
    sparse = _unit(_doc(OID_B, [_f("card_type", "REQUIRES", "creature", OID_B),
                                _f("color", "REQUIRES", "blue", OID_B)]))
    check("ALG.MISSING_NOT_ABSENT_EQUALITY a dimension present on one side and "
          "missing on the other blocks",
          any(c["unknown_reason"] == "MISSING_FACT"
              for c in eligibility_equality(ua, sparse)["components"]))
    hr_absent = _unit(_doc(OID_B, [
        _f("card_type", "REQUIRES", "creature", OID_B),
        _f("color", "REQUIRES", "blue", OID_B, disposition="HUMAN_RESOLVED",
           resolved={"absent": True},
           adjudication={"method": "INDEPENDENT_DUAL"})], role="KEY"))
    check("ALG.MISSING_NOT_ABSENT_EQUALITY a MISSING fact does not equal an "
          "adjudicated ABSENT one",
          eligibility_equality(ua, hr_absent)["result"] == UNKNOWN)
    check("ALG.ELIGIBILITY_EMPTY_NOT_EQUAL-RIG two ADJUDICATED "
          "constraint-free cases can prove equality",
          eligibility_equality(
              _unit(_doc(OID_A, [_f("color", "REQUIRES", "blue", OID_A,
                                    disposition="HUMAN_RESOLVED",
                                    resolved={"absent": True},
                                    adjudication={"method": "SINGLE"})],
                         role="KEY")),
              _unit(_doc(OID_B, [_f("color", "REQUIRES", "blue", OID_B,
                                    disposition="HUMAN_RESOLVED",
                                    resolved={"absent": True},
                                    adjudication={"method": "SINGLE"})],
                         role="KEY")))["result"] == PROVEN)

    print("\nDISTINGUISHING WITNESS")
    needs_blue = _unit(_doc(OID_B, [
        _f("card_type", "REQUIRES", "creature", OID_B),
        _f("color", "REQUIRES", "blue", OID_B)]))
    w_complete = _witness({"card_type": ["creature"], "color": ["red"]},
                          complete=("card_type", "color"))
    rw = entails(ua, needs_blue, witness=w_complete)
    check("ALG.WITNESS_REQUIRES_NEEDS_COMPLETE_ASSIGNMENT a complete "
          "assignment lets a witness refute a REQUIRES",
          rw["result"] == PROVEN_NOT and rw["proof_kind"] == CORPUS_WITNESS
          and rw.get("corpus_ref"), rw["result"])
    w_incomplete = _witness({"card_type": ["creature"], "color": ["red"]})
    check("ALG.WITNESS_REQUIRES_NEEDS_COMPLETE_ASSIGNMENT-RIG without the "
          "completeness declaration the SAME witness proves nothing",
          entails(ua, needs_blue, witness=w_incomplete)["result"] == UNKNOWN)
    forbids_blue = _unit(_doc(OID_B, [
        _f("card_type", "REQUIRES", "creature", OID_B),
        _f("color", "FORBIDS", "blue", OID_B)]))
    w_presence = _witness({"card_type": ["creature"], "color": ["blue"]})
    check("ALG.WITNESS_FORBIDS_PRESENCE_OK an observed forbidden value refutes "
          "a FORBIDS with no completeness declaration",
          entails(ua, forbids_blue, witness=w_presence)["result"] == PROVEN_NOT)
    eqonly = _unit(_doc(OID_B, [
        _f("card_type", "REQUIRES", "creature", OID_B),
        _f("counter_kind", "REQUIRES", "charge", OID_B)]))
    check("ALG.WITNESS_EQUALITY_ONLY_MISMATCH_UNKNOWN an equality-only "
          "mismatch is never a violation",
          entails(ua, eqonly, witness=_witness(
              {"card_type": ["creature"], "counter_kind": ["loyalty"]},
              complete=("card_type", "counter_kind")))["result"] == UNKNOWN)
    check("ALG.WITNESS_MALFORMED_NEVER_PROVEN_NOT a malformed payload can "
          "never be violated=true",
          _witness_atom({"op": "CARD", "value": {"comparison": "!!", "n": 1}},
                        "color", {"color": ["blue"]}, {"color"}) == UNDECIDABLE)
    check("ALG.WITNESS_MALFORMED_NEVER_PROVEN_NOT-RIG a WELL-FORMED cardinality "
          "atom does decide",
          _witness_atom({"op": "CARD", "value": {"comparison": "=", "n": 2}},
                        "color", {"color": ["blue"]}, {"color"}) == VIOLATED)
    check("ALG.WITNESS_SEARCH_MISS_UNKNOWN no witness stays UNKNOWN",
          entails(ua, needs_blue)["result"] == UNKNOWN
          and entails(ua, needs_blue).get("unknown_reason") is not None)
    nopin = dict(w_complete)
    nopin.pop("corpus_ref")
    check("ALG.WITNESS_SEARCH_MISS_UNKNOWN a witness with no corpus_ref is "
          "inadmissible",
          entails(ua, needs_blue, witness=nopin).get("unknown_reason")
          == "WITNESS_INADMISSIBLE")

    print("\nINTERSECTION — THE DISJUNCTION REPAIR")
    disj = _unit(_doc(OID_A, [_f("card_type", "REQUIRES",
                                 ["artifact", "creature"], OID_A)]))
    forb_art = _unit(_doc(OID_B, [_f("card_type", "FORBIDS", "artifact",
                                     OID_B)]))
    r = disjoint(disj, forb_art)
    check("ALG.DISJUNCTIVE_REQUIRES_PARTIAL_FORBID_NOT_CONTRADICTION requiring "
          "[artifact, creature] against forbidding artifact is NOT empty "
          "intersection", r["result"] == UNKNOWN, r["result"])
    check("ALG.DISJUNCTIVE_REQUIRES_PARTIAL_FORBID_NOT_CONTRADICTION-RIG the "
          "quarantined any-overlap rule WOULD have proved it",
          bool({"artifact", "creature"} & {"artifact"}))
    forb_both = _unit(_doc(OID_B, [
        _f("card_type", "FORBIDS", ["artifact", "creature"], OID_B)]))
    check("ALG.DISJUNCTIVE_REQUIRES_ALL_FORBIDDEN_CONTRADICTION every "
          "alternative forbidden IS empty intersection",
          disjoint(disj, forb_both)["result"] == PROVEN_NOT)
    zone_a = _unit(_doc(OID_A, [_f("zone", "REQUIRES", "battlefield", OID_A)]))
    zone_b = _unit(_doc(OID_B, [_f("zone", "REQUIRES", "graveyard", OID_B)]))
    check("ALG.DISJOINT_NEEDS_CR_CONTRADICTION a closed single-valued "
          "must-have dimension still proves it",
          disjoint(zone_a, zone_b)["result"] == PROVEN_NOT)
    check("ALG.DISJOINT_NEEDS_CR_CONTRADICTION disjoint() takes no witness",
          "witness" not in disjoint.__code__.co_varnames)
    check("ALG.OVERLAP_NEEDS_WITNESS compatibility alone is not overlap",
          overlap(ua, sparse)["result"] == UNKNOWN)
    check("ALG.OVERLAP_NEEDS_WITNESS-RIG an admissible witness proves it",
          overlap(ua, sparse, witness=_witness(
              {"card_type": ["creature"], "color": ["blue"]},
              complete=("card_type", "color")))["result"] == PROVEN)

    print("\nPROOF RECORDS")
    rec = eligibility_equality(ua, ub)
    proven_kinds = {c["kind"] for c in rec["components"]
                    if c["result"] == PROVEN}
    check("ALG.NONBLOCKING_NOT_PROOF cost, relation, head and participant "
          "checks are NOT proof components",
          not (proven_kinds & {"COST_RESIDUE", "RELATIONS", "ACTION_HEADS",
                               "PARTICIPANTS"}), sorted(proven_kinds))
    check("ALG.NONBLOCKING_NOT_PROOF they are recorded as preconditions with "
          "no verdict",
          {p["check"] for p in rec["preconditions"]} ==
          {"cost_regions_observed", "relation_edges_observed",
           "action_head_sequences", "participant_ordinal_sets",
           "participant_correspondence_supplied"}
          and all(set(p) == {"check", "observed", "note"}
                  for p in rec["preconditions"]))
    check("ALG.NONBLOCKING_NOT_PROOF-RIG moving a blocking condition into a "
          "precondition is refused",
          halts(assert_preconditions_are_not_proofs,
                {"preconditions": [{"check": "x", "result": PROVEN,
                                    "proof_kind": CR_CONTRACT}]}))
    check("ALG.CR_ANCHOR_NOT_PROSE every proven component cites a real anchor",
          all(c.get("cr_anchor") for c in rec["components"]
              if c["result"] in (PROVEN, PROVEN_NOT) and c.get("proof_kind")))
    bad_anchor = copy.deepcopy(rec)
    for c in bad_anchor["components"]:
        if c["result"] == PROVEN and c.get("proof_kind"):
            c["cr_anchor"] = None
    check("ALG.CR_ANCHOR_NOT_PROSE-RIG an anchorless proven component is "
          "refused", halts(assert_proof_trace, bad_anchor))
    check("ALG.COST_ABSENCE_NOT_PROOF a cost region changes no verdict",
          eligibility_equality(
              ua, _unit(_doc(OID_B, [_f("card_type", "REQUIRES", "creature",
                                        OID_B)], regions=[_cost_region(OID_B)]))
          )["result"] == PROVEN)
    check("ALG.RELATION_ABSENCE_NOT_PROOF absence of an edge proves nothing "
          "and is precondition-only",
          all(c["kind"] != "RELATIONS" for c in rec["components"]))
    part_a = _unit(_doc(OID_A, [_f("card_type", "REQUIRES", "creature", OID_A,
                                   scope={"kind": "PARTICIPANT",
                                          "participant": 0})],
                        participants=(0,)))
    part_b = _unit(_doc(OID_B, [_f("card_type", "REQUIRES", "creature", OID_B,
                                   scope={"kind": "PARTICIPANT",
                                          "participant": 0})],
                        participants=(0,)))
    pr_ = eligibility_equality(part_a, part_b)
    check("ALG.PARTICIPANT_ORDINAL_NOT_CROSSCARD_EQUALITY identical "
          "participant-scoped facts at the same ordinal do NOT prove equality",
          pr_["result"] == UNKNOWN
          and any(c["unknown_reason"] == "NO_PARTICIPANT_CORRESPONDENCE"
                  for c in pr_["components"]), pr_["result"])
    check("ALG.PARTICIPANT_ORDINAL_NOT_CROSSCARD_EQUALITY-RIG the SAME atoms "
          "at occurrence scope DO prove it, so the refusal is the ordinal law",
          eligibility_equality(ua, ub)["result"] == PROVEN)

    print("\nPARTICIPANT CORRESPONDENCE — SUPPLIED, NEVER INFERRED")
    pa = _unit(_doc(OID_A, [_f("card_type", "REQUIRES", "creature", OID_A,
                               scope={"kind": "PARTICIPANT",
                                      "participant": 0})],
                    participants=(0,)))
    pb = _unit(_doc(OID_B, [_f("card_type", "REQUIRES", "creature", OID_B,
                               scope={"kind": "PARTICIPANT",
                                      "participant": 0})],
                    participants=(0,)))
    check("ALG.PARTICIPANT_NO_MAPPING_UNKNOWN without a supplied mapping the "
          "comparison declines",
          eligibility_equality(pa, pb)["result"] == UNKNOWN
          and any(c["unknown_reason"] == "NO_PARTICIPANT_CORRESPONDENCE"
                  for c in eligibility_equality(pa, pb)["components"]))
    corr = _corr(pa, pb, {0: 0})
    check("ALG.PARTICIPANT_CORRESPONDENCE_LIFT a supplied mapping makes the "
          "same facts comparable",
          eligibility_equality(pa, pb, corr=corr)["result"] == PROVEN,
          eligibility_equality(pa, pb, corr=corr)["result"])
    other_pair = dict(corr, a_unit=(OID_A, 9, 9, 9))
    check("BIND.ORDINAL_NOT_CORRESPONDENCE a mapping frozen for ANOTHER pair "
          "does not apply, and ordinal equality is no fallback",
          eligibility_equality(pa, pb, corr=other_pair)["result"] == UNKNOWN)
    swapped = _unit(_doc(OID_B, [
        _f("card_type", "REQUIRES", "creature", OID_B,
           scope={"kind": "PARTICIPANT", "participant": 1}),
        _f("color", "REQUIRES", "blue", OID_B,
           scope={"kind": "PARTICIPANT", "participant": 0})],
        participants=(0, 1)))
    pa2 = _unit(_doc(OID_A, [
        _f("card_type", "REQUIRES", "creature", OID_A,
           scope={"kind": "PARTICIPANT", "participant": 0}),
        _f("color", "REQUIRES", "blue", OID_A,
           scope={"kind": "PARTICIPANT", "participant": 1})],
        participants=(0, 1)))
    check("BIND.SWAPPED_ATTACHMENT_NOT_AUTOBOUND a swapped attachment is only "
          "comparable through the mapping that states the swap",
          eligibility_equality(pa2, swapped)["result"] == UNKNOWN
          and eligibility_equality(pa2, swapped,
                                   corr=_corr(pa2, swapped,
                                              {0: 1, 1: 0}))["result"]
          == PROVEN)
    check("BIND.ORDINAL_NOT_CORRESPONDENCE-RIG the SAME pair under the "
          "identity mapping is NOT proven, so ordinal equality really is not "
          "the rule",
          eligibility_equality(pa2, swapped,
                               corr=_corr(pa2, swapped,
                                          {0: 0, 1: 1}))["result"] != PROVEN)

    print("\nCOVERAGE REPAIR — AN EXTRA UNBOUND PARTICIPANT BLOCKS")
    extra = _unit(_doc(OID_B, [
        _f("card_type", "REQUIRES", "creature", OID_B,
           scope={"kind": "PARTICIPANT", "participant": 0}),
        _f("color", "REQUIRES", "blue", OID_B,
           scope={"kind": "PARTICIPANT", "participant": 1})],
        participants=(0, 1)))
    c_one = _corr(pa, extra, {0: 0})
    r_extra = eligibility_equality(pa, extra, corr=c_one)
    check("BIND.EXTRA_UNBOUND_BLOCKS_EQUALITY one mapped participant plus an "
          "extra actionable UNBOUND one does not prove equality",
          r_extra["result"] == UNKNOWN, r_extra["result"])
    check("BIND.EXTRA_UNBOUND_BLOCKS_EQUALITY it is UNKNOWN, never PROVEN_NOT "
          "-- an extra participant is not a proof of difference",
          r_extra["result"] != PROVEN_NOT)
    skipped = kleene(
        [c for c in _coverage_components(pa, extra, None, c_one,
                                         _skip_participants=True)]
        + [_component("DIRECTION_A_TO_B", None, PROVEN),
           _component("DIRECTION_B_TO_A", None, PROVEN)])
    check("BIND.EXTRA_UNBOUND_BLOCKS_EQUALITY-RIG the OLD participant-skipping "
          "coverage would have let it through",
          skipped == PROVEN and r_extra["result"] == UNKNOWN, skipped)

    print("\nB1 SAFETY UNDER COMPLETE CORRESPONDENCE")
    r_b1 = b1(pa, pb, corr=corr)
    check("BIND.COMPLETE_MAPPING_NOT_B1_PROOF a complete binding and complete "
          "correspondence with mutually entailing eligibility is STILL not "
          "whole-unit equality",
          r_b1["verdict"] == UNKNOWN
          and r_b1["positive_arm"] == "UNAVAILABLE_IN_V1", r_b1["verdict"])
    check("BIND.COMPLETE_MAPPING_NOT_B1_PROOF-RIG the eligibility layer IS "
          "proven on that same input, so the refusal is B1's law",
          eligibility_equality(pa, pb, corr=corr)["result"] == PROVEN)

    print("\nB2 — SIX LABELS, STRICT")
    sub = _unit(_doc(OID_A, [_f("subtype", "REQUIRES", "goblin", OID_A)]))
    typ = _unit(_doc(OID_B, [_f("card_type", "REQUIRES", "creature", OID_B)]))
    check("ALG.B2_EQUAL eligibility equality PROVEN yields EQUAL",
          b2(ua, ub)["relation_label"] == "EQUAL")
    check("ALG.B2_EQUAL_NOT_OVERLAP_WITHOUT_WITNESS EQUAL is not remapped to "
          "OVERLAPPING", b2(ua, ub)["intersection"] == UNKNOWN
          and b2(ua, ub)["relation_label"] == "EQUAL")
    wit_nb = _witness({"card_type": ["creature"], "subtype": ["dwarf"]},
                      complete=("card_type", "subtype"))
    check("ALG.B2_NARROWER_STRICT NARROWER needs the reverse PROVEN_NOT",
          b2(sub, typ, witness=wit_nb)["relation_label"] == "NARROWER",
          b2(sub, typ, witness=wit_nb)["relation_label"])
    check("ALG.B2_BROADER_STRICT the mirror is BROADER",
          b2(typ, sub, witness=wit_nb)["relation_label"] == "BROADER",
          b2(typ, sub, witness=wit_nb)["relation_label"])
    check("ALG.B2_BROADER_STRICT-RIG one direction PROVEN with the reverse "
          "UNKNOWN is UNKNOWN, not NARROWER",
          b2(sub, typ)["relation_label"] == "UNKNOWN",
          b2(sub, typ)["relation_label"])
    check("ALG.B2_EQUAL DISJOINT comes from the contradiction pole",
          b2(zone_a, zone_b)["relation_label"] == "DISJOINT")
    check("ALG.B2_EQUAL OVERLAPPING needs the witness",
          b2(ua, sparse, witness=_witness(
              {"card_type": ["creature"], "color": ["blue"]},
              complete=("card_type", "color")))["relation_label"]
          == "OVERLAPPING")
    check("ALG.B2_EQUAL the six labels are exactly the ratified set",
          set(B2_LABELS) == {"EQUAL", "BROADER", "NARROWER", "OVERLAPPING",
                             "DISJOINT", "UNKNOWN"})

    print("\nB3 — PARTIAL")
    r3 = b3(ua, _unit(_doc(OID_B, [_f("card_type", "REQUIRES", "creature",
                                      OID_B)], heads=("exile",))))
    check("ALG.B3_NO_ACTION_LAW the action arm is UNKNOWN with the "
          "missing-law reason",
          r3["action_equivalence"]["verdict"] == UNKNOWN
          and r3["action_equivalence"]["unknown_reason"]
          == "NO_CONTRACTED_COMPARISON_LAW")
    check("ALG.B3_NO_ACTION_LAW-RIG identical heads still yield UNKNOWN",
          b3(ua, ub)["action_equivalence"]["verdict"] == UNKNOWN
          and b3(ua, ub)["action_head_structural_report"]["value"]
          == "IDENTICAL")

    print("\nC3 — POSITIVE GROUP STRUCTURE ONLY")
    proj = _choice_group_projection()
    u0 = proj.unit(pj.surface_id((OID_A, 0, 1, 0)))
    u1 = proj.unit(pj.surface_id((OID_A, 0, 2, 0)))
    u_out = proj.unit(pj.surface_id((OID_A, 0, 3, 0)))
    check("ALG.C3_POSITIVE_GROUP_ONLY different options under selection max 1 "
          "are ALTERNATIVE", c3(proj, u0, u1)["value"] == "ALTERNATIVE",
          c3(proj, u0, u1)["value"])
    check("ALG.C3_NO_GROUP_ABSENCE_INFERENCE a unit outside every group yields "
          "UNKNOWN, never INDEPENDENT",
          c3(proj, u0, u_out)["value"] == UNKNOWN
          and c3(proj, u0, u_out)["independent_arm"] == "NOT_DERIVABLE_IN_V1")
    proj2 = _choice_group_projection(selection={"min": 2, "max": 2},
                                     same_option=True)
    check("ALG.C3_POSITIVE_GROUP_ONLY two units in ONE option are CUMULATIVE",
          c3(proj2, proj2.unit(pj.surface_id((OID_A, 0, 1, 0))),
             proj2.unit(pj.surface_id((OID_A, 0, 1, 1))))["value"]
          == "CUMULATIVE")
    proj3 = _choice_group_projection(selection={"min": 1, "max": 2})
    check("ALG.C3_POSITIVE_GROUP_ONLY-RIG a permissive selection is UNKNOWN, "
          "not guessed",
          c3(proj3, proj3.unit(pj.surface_id((OID_A, 0, 1, 0))),
             proj3.unit(pj.surface_id((OID_A, 0, 2, 0))))["value"] == UNKNOWN)

    print("\nDISPOSITIONS · DERIVED BOUNDARY · TRACE")
    key_doc = _doc(OID_B, [_f("card_type", "REQUIRES", "creature", OID_B,
                              disposition="HUMAN_RESOLVED",
                              resolved={"atom": {"op": "REQUIRES",
                                                 "value": "creature"}},
                              adjudication={"method": "INDEPENDENT_DUAL"})],
                   role="KEY")
    ku = _unit(key_doc)
    rk = eligibility_equality(ua, ku)
    check("ALG.HUMAN_RESOLVED_TRANSPARENT the payload compares and the wrapper "
          "survives in the trace",
          rk["result"] == PROVEN and any(
              pv.get("adjudication") for c in rk["components"]
              for pv in c.get("provenance", []) if isinstance(pv, dict)))
    cand_hr = copy.deepcopy(key_doc)
    cand_hr["artifact_role"] = "CANDIDATE_EXPORT"
    check("ALG.CANDIDATE_HUMAN_RESOLVED_REJECTED a candidate emitting it is "
          "rejected at ingest", halts(load_document, cand_hr))
    ap = _unit(_doc(OID_B, [_f("color", "REQUIRES", "blue", OID_B,
                               disposition="ABSENT_PROVEN")]))
    blue = _unit(_doc(OID_A, [_f("color", "REQUIRES", "blue", OID_A)]))
    check("ALG.ABSENT_PROOF_REQUIRED an unearned absence claim degrades to "
          "UNKNOWN",
          any(c["unknown_reason"] == "ABSENCE_NOT_EARNED"
              for c in eligibility_equality(blue, ap)["components"]))
    check("ALG.ABSENT_PROOF_REQUIRED-RIG represented obligations make it "
          "actionable",
          not any(c["unknown_reason"] == "ABSENCE_NOT_EARNED"
                  for c in eligibility_equality(
                      blue, ap,
                      ledger={(ap.id, "OCCURRENCE", None, "color"): True}
                  )["components"]))
    doc_a = _doc(OID_A, [_f("card_type", "REQUIRES", "creature", OID_A)])
    check("ALG.DERIVED_NOT_PROJECTION a verdict cannot enter the projection",
          not halts(assert_not_a_projection_fact, doc_a, rec))
    check("ALG.NO_NATIVE_BRANCH a native identifier in a record is refused",
          halts(assert_no_native_identifiers, {"canonical_owner": "x"}))
    stripped = copy.deepcopy(rec)
    stripped["evidence"] = []
    check("ALG.PROOF_TRACE_REQUIRED-RIG a proven record with no trace is "
          "refused", halts(assert_proof_trace, stripped))

    print("\nDETERMINISM · SYMMETRY · DIRECTION · E1")
    check("ALG.SYMMETRY a symmetric operation is byte-identical under reversal",
          pj.canonical_json(eligibility_equality(ua, ub))
          == pj.canonical_json(eligibility_equality(ub, ua)))
    f_ab, f_ba = entails(sub, typ), entails(typ, sub)
    check("ALG.DIRECTION_EXPLICIT a directional operation names its direction",
          f_ab["direction"] == f_ba["direction"] == "A_ENTAILS_B"
          and f_ab["inputs"] != f_ba["inputs"]
          and f_ab["result"] != f_ba["result"])
    check("ALG.DIRECTION_EXPLICIT B2 mirrors under operand reversal",
          b2(sub, typ, witness=wit_nb)["relation_label"] == "NARROWER"
          and b2(typ, sub, witness=wit_nb)["relation_label"] == "BROADER")
    check("ALG.DIRECTION_EXPLICIT C1 refuses an unnamed direction",
          halts(c1, (ua, ub), "WHICHEVER"))
    check("ALG.DIRECTION_EXPLICIT C1's empty blocker list is not a claim",
          "NEVER a positive equality" in c1((ua, ub),
                                            "X_REPLACES_Y")["_empty_is_not_a_claim"])
    check("ALG.DETERMINISM two runs are byte-identical",
          pj.canonical_json(eligibility_equality(ua, ub))
          == pj.canonical_json(eligibility_equality(ua, ub)))
    dom = e1_domain()
    check("E1's domain is the frozen semantic pair union",
          dom["unique_semantic_pairs"] == 354, dom["unique_semantic_pairs"])
    tr = e1_trace(rec, pair=(ua.id, ub.id))
    check("E1 emits a validated trace and no prose",
          tr["step_count"] > 0 and "explanation" not in pj.canonical_json(tr))

    print("\nPROBE-LIBRARY GUARD")
    p.must_capture(
        lambda pr2: eligibility_equality(*pr2)["result"] == PROVEN,
        [((ua, ub), True), ((ua, sparse), False), ((part_a, part_b), False),
         ((empty_a, empty_b), False), ((zone_a, zone_b), False)],
        name="eligibility equality")
    check("GUARD D eligibility equality agrees with its own fixture", True)

    print()
    if fails:
        print(f"SELFTEST FAILED — {len(fails)} control(s): {fails}")
        return 1
    print("SELFTEST PASSED — every control fired on the path it guards, and "
          "every rigging turned its control red.")
    return 0


def _corr(a: Unit, b: Unit, a_to_b: dict) -> dict:
    """A synthetic correspondence context, shaped exactly as the binding
    artifact's `correspondence_for` emits it."""
    return {"a_unit": tuple(a.addr), "b_unit": tuple(b.addr),
            "a_to_b": dict(a_to_b),
            "b_to_a": {v: k for k, v in a_to_b.items()},
            "unbound_a": [], "unbound_b": [],
            "correspondence_state": "COMPLETE"}


def _choice_group_projection(selection=None, same_option=False):
    """A synthetic document carrying one choice group and one outside unit."""
    sel = selection or {"min": 1, "max": 1}

    def occ(par, cl):
        return {"occurrence": {"oracle_id": OID_A, "face": 0, "paragraph": par,
                               "clause": cl},
                "participants": [], "action_heads": [],
                "action_head_disposition": "UNRESOLVED", "facts": []}

    members = ([{"oracle_id": OID_A, "face": 0, "paragraph": 1, "clause": 0},
                {"oracle_id": OID_A, "face": 0, "paragraph": 1, "clause": 1}]
               if same_option else
               [{"oracle_id": OID_A, "face": 0, "paragraph": 1, "clause": 0},
                {"oracle_id": OID_A, "face": 0, "paragraph": 2, "clause": 0}])
    occs = [occ(0, 0), occ(1, 0), occ(1, 1), occ(2, 0), occ(3, 0)]
    doc = {"schema": pj.SCHEMA_NAME, "version": pj.SCHEMA_VERSION,
           "artifact_role": "KEY", "occurrences": occs,
           "choice_groups": [{
               "owning_header": {"occurrence": {"oracle_id": OID_A, "face": 0,
                                                "paragraph": 0, "clause": 0}},
               "selection": sel, "members": members,
               "derivation_class": "EXTRACT-0", "cr_anchors": ["CR 700.2"],
               "evidence": pj._evidence(OID_A, 0, 10)}]}
    return load_document(doc)


# ==========================================================================
# MEASUREMENTS
# ==========================================================================

def sweep() -> dict:
    """The synthetic regression sweep, occurrence-scoped and participant-scoped.

    Deliberately BOTH: the participant arm is what quantifies the cost of the
    ratified ordinal restriction, and quoting only the occurrence arm would
    hide it.
    """
    def variants(oid, scope):
        out = []
        for dims in ([("card_type", "REQUIRES", "creature")],
                     [("card_type", "REQUIRES", "creature"),
                      ("color", "REQUIRES", "blue")],
                     [("zone", "REQUIRES", "graveyard")]):
            for heads in (("destroy",), ("exile",), ()):
                for regions in ((), (_cost_region(oid),)):
                    for rel in ((), ({"kind": "COREFERENCE",
                                      "from": {"occurrence": {
                                          "oracle_id": oid, "face": 0,
                                          "paragraph": 0, "clause": 0}},
                                      "to": {"occurrence": {
                                          "oracle_id": oid, "face": 0,
                                          "paragraph": 0, "clause": 1}},
                                      "evidence": pj._evidence(oid)},)):
                        for parts in ((), (0, 1)):
                            sc = ({"kind": "PARTICIPANT", "participant": 0}
                                  if scope == "PARTICIPANT" else
                                  {"kind": "OCCURRENCE"})
                            facts = [_f(d, op, v, oid, scope=sc)
                                     for d, op, v in dims]
                            out.append(_unit(_doc(
                                oid, facts, heads=heads, regions=list(regions),
                                relations=list(rel),
                                participants=parts if scope != "PARTICIPANT"
                                else (0,))))
        return out

    res = {}
    for scope in ("OCCURRENCE", "PARTICIPANT"):
        A, B = variants(OID_A, scope), variants(OID_B, scope)
        counts = collections.Counter(
            eligibility_equality(x, y)["result"] for x in A for y in B)
        res[scope] = {"pairs": len(A) * len(B), **dict(counts)}
    return res


def c3_derivability() -> dict:
    """How far C3 reaches over the 21 projected choice groups. Counts only."""
    cards, _, _ = fc.load_corpus_gated()
    import aq4_pairing as pr2
    ids = pr2.open_exemplars(pr2.published_classes())
    per_group = collections.Counter()
    pair_verdicts = collections.Counter()
    groups = 0
    for oid in ids:
        gs, _ = pj.derive_choice_groups(cards[oid], oid)
        for g in gs:
            groups += 1
            opts = {m["paragraph"] for m in g["members"]}
            alt = g["selection"]["max"] == 1 and len(opts) >= 2
            cum = (len(g["members"]) > len(opts)
                   or g["selection"]["min"] == len(opts))
            per_group["ALTERNATIVE_derivable"] += bool(alt)
            per_group["CUMULATIVE_derivable"] += bool(cum)
            per_group["INDEPENDENT_derivable"] += 0
            if not alt and not cum:
                per_group["UNKNOWN_remains"] += 1
            for m1, m2 in itertools.combinations(g["members"], 2):
                if m1["paragraph"] == m2["paragraph"]:
                    pair_verdicts["CUMULATIVE"] += 1
                elif g["selection"]["max"] == 1:
                    pair_verdicts["ALTERNATIVE"] += 1
                elif g["selection"]["min"] == len(opts):
                    pair_verdicts["CUMULATIVE"] += 1
                else:
                    pair_verdicts["UNKNOWN"] += 1
    return {"choice_groups": groups, "per_group": dict(sorted(per_group.items())),
            "member_pair_verdicts": dict(sorted(pair_verdicts.items())),
            "INDEPENDENT": "NOT_DERIVABLE_IN_V1 — reported, not minted"}


def census() -> int:
    print("=" * 74)
    print("AQ4 SHARED COMPARISON ALGEBRA — CENSUS (law only, no card answer)")
    print("=" * 74)
    print(f"  algebra                 {ALGEBRA_NAME} {ALGEBRA_VERSION}")
    print(f"  consumes projection     {pj.SCHEMA_NAME} {pj.SCHEMA_VERSION}")
    print(f"  verdicts                {', '.join(RESULTS)}")
    print(f"  proof kinds             {', '.join(PROOF_KINDS)}")
    print(f"  operations              {sorted(OPERATIONS)}")
    print(f"  UNKNOWN reason classes  {len(REASONS)}")
    print(f"  B1 positive arm         UNAVAILABLE_IN_V1")
    print(f"  B2 labels               {', '.join(B2_LABELS)}")
    print(f"  B3 action arm           UNKNOWN (no contracted law)")
    print(f"  C3 INDEPENDENT arm      NOT_DERIVABLE_IN_V1")
    print(f"\n  synthetic sweep         {sweep()}")
    print(f"  C3 over the 21 groups   {c3_derivability()}")
    d = e1_domain()
    print(f"  E1 domain               {d['unique_semantic_pairs']} pairs")
    return 0


def main() -> int:
    ap_ = argparse.ArgumentParser(
        description="AQ4 shared candidate-neutral comparison algebra.")
    ap_.add_argument("--selftest", action="store_true")
    ap_.add_argument("--census", action="store_true")
    a = ap_.parse_args()
    if a.selftest:
        return selftest()
    if a.census:
        return census()
    ap_.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
