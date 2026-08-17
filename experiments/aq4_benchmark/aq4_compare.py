#!/usr/bin/env python3
"""AQ4 BENCHMARK — SHARED CANDIDATE-NEUTRAL COMPARISON ALGEBRA (contract 17, packet 7).

WHAT THIS IS AND IS NOT
-----------------------
This is SHARED BENCHMARK EVALUATION MACHINERY, not a candidate. It consumes the
frozen Packet-4 evaluation projection and derives three-valued comparison
verdicts from it. Production AQ4 architecture remains UNRATIFIED and nothing
here changes it.

It MUST NOT, and does not:
  · parse Oracle text;
  · read a candidate-native field, or branch on candidate identity;
  · adjudicate open truth, write an answer key, or score a candidate;
  · store a derived verdict as a canonical projection fact;
  · carry a card-specific exception.

THE ORGANIZING LAW — READ THIS BEFORE ADDING AN OPERATION
---------------------------------------------------------
    A UNIVERSAL claim is contract-provable.
    An EXISTENTIAL claim needs a corpus witness.

Entailment, equality and disjointness are universal, so they are proved from
the dimension contracts, the section 13 atom semantics and the ratified
subtype-to-type hierarchy -> `CR_CONTRACT`.

Non-entailment, non-equality and OVERLAP are existential -- they assert that
some object exists -- so they are proved only by a named printed card ->
`CORPUS_WITNESS`. This is register 17's ruling generalized: non-contradiction
is not nonempty intersection, measured at 54.8% empty cells over a CR-closed
product space. It is also why "I could not prove equality" can never become
PROVEN_NOT, and why corpus absence proves nothing in either direction.

THREE VERDICTS, TWO PROOF KINDS, NO FOURTH ANYTHING
---------------------------------------------------
`PROVEN` / `PROVEN_NOT` / `UNKNOWN`, and UNKNOWN is first-class. It never means
false, absent, incompatible, disjoint, or searched-and-not-found. `proof_kind`
is provenance on the derived relation and is never a verdict; an UNKNOWN reason
class is audit metadata and is never a verdict either. Nothing branches on
either except the audit trail.

WHAT BLOCKS, AND WHY BLOCKING IS NOT DISPROVING
-----------------------------------------------
Uncontracted material cannot be compared, so it can only ever move a verdict
toward UNKNOWN:

  COST      register 27 gives COST a structural region and NO comparison
            algebra, so a cost region on either side BLOCKS a strict PROVEN
            equality. It never yields PROVEN_NOT: differing cost bytes prove
            nothing, and there is no absence claim over cost on either side.
  ACTION    section 17's closed table authorizes no action-head comparison and
            an action head is expressly not a dimension (register 23). Head
            identity is used as a NECESSARY CONDITION only. A missing head is
            never read as an equal action, and a differing head is never
            PROVEN_NOT.
  RELATION  section 16 lets relations participate only where the contract
            authorizes it; section 17's table does not. Edges are blockers.
  MISSING   a dimension with no fact contributes no atom and is never read as
            ABSENT. In the strict operations it is reported as MISSING_FACT and
            forces UNKNOWN.

WHY THE ALGEBRA IS A JSON FILE AND NOT A PYTHON LITERAL
-------------------------------------------------------
`comparison-algebra.json` is the single versioned source of the operation
table, the result domain, the proof-kind vocabulary and the UNKNOWN reason
classes. This module reads it rather than restating it, so the two cannot
drift, and `compare()` refuses any operation the file does not register.

TWO DECLARED READINGS, FLAGGED RATHER THAN SMUGGLED
---------------------------------------------------
1. The projection schema fixes an atom's `op` but not the payload shape of a
   `CARD` or `INTERVAL` value. This module declares one (`{"comparison", "n"}`
   and `{"min", "max"}`) and reports it as a declared reading.
2. Section 20's B4 speaks of "destination / timing / quantity"; section 14's
   rows are named `zone`, `timing_duration`, `quantity` and `numeric`. The
   mapping between them is recorded in `comparison-algebra.json` as a DECLARED
   READING and is reversible without touching a single verdict.

Neither is presented as ratified law, and neither is load-bearing for any
verdict -- both live beside the full per-dimension verdict table.
"""
import io
import sys
import copy
import json
import argparse
import itertools
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
REPO_ROOT = EXPERIMENTS.parent
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
ALGEBRA_VERSION = "1.0.0"

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

#: Dimensions on which REQUIRES(d, v) discharges FORBIDS(d, w) for w != v.
#: All three properties are required: an object carries exactly one value, and
#: the CR closes the value set. `controller_relation` fails must_have and is
#: therefore already out -- it is ALSO named explicitly below, because the
#: contract forbids its complement by name and a property test that happened to
#: change would silently re-admit it.
COMPLEMENT_FORBIDDEN = {"controller_relation"}
SINGLE_VALUED_EXHAUSTIVE = {
    n for n, d in DIMENSIONS.items()
    if d.get("closed") is True and d.get("multi") is False
    and d.get("must_have") is True and n not in COMPLEMENT_FORBIDDEN
}

EQUALITY_ONLY = {n for n, d in DIMENSIONS.items()
                 if str(d.get("v1_status", "")).startswith("equality-only")}

#: The ratified subtype -> parent-type edge, CONSUMED, never re-derived. It is
#: the only hierarchy this algebra asserts (contract 17, EXTRACT-3).
HIERARCHY = ol.SUBTYPE_TO_TYPE
if not HIERARCHY:
    fc.halt("the ratified subtype-to-type hierarchy parsed EMPTY. Comparing "
            "with an empty hierarchy silently downgrades every hierarchy "
            "entailment to UNKNOWN and reads as a clean conservative result.")

#: Closed vocabularies available WITHOUT any new parse. Only these dimensions
#: get an out-of-vocabulary guard; the rest are reported as unguarded rather
#: than pretended to be checked.
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
# UNITS — the only thing a comparison ever consumes
# ==========================================================================

class Unit:
    """One projected semantic occurrence, plus the artifact role that produced it.

    The role is used for exactly one thing: the section 18 disposition SIDES
    (`HUMAN_RESOLVED` is key-side, `ABSENT_PROVEN` is claimant-side). It is not
    a candidate identity and no verdict branches on which candidate exported a
    document -- the projection carries no such field, and the forbidden-native
    check refuses one.
    """

    __slots__ = ("occ", "role", "addr", "id")

    def __init__(self, occ: dict, role: str):
        self.occ = occ
        self.role = role
        a = occ["occurrence"]
        self.addr = (a["oracle_id"], a["face"], a["paragraph"], a["clause"])
        self.id = pj.surface_id(self.addr)

    @property
    def participants(self):
        return tuple(sorted(set(self.occ.get("participants", []))))

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


def load_document(doc: dict) -> dict:
    """Validate under the FROZEN Packet-4 schema, canonicalize, index by address.

    Rejection is a halt, not a warning. A document that does not validate is
    never partially consumed: the whole point of a shared projection is that a
    comparison cannot quietly reach around it.
    """
    pj.assert_valid(doc)
    c = pj.canonicalize(doc)
    role = c["artifact_role"]
    out = {}
    for occ in c.get("occurrences", []):
        u = Unit(occ, role)
        if u.id in out:
            fc.halt(f"duplicate occurrence address {u.id!r} in one projection "
                    f"document; an address is an identity and cannot repeat.")
        out[u.id] = u
    return out


# ==========================================================================
# FACT READING — dispositions, wrappers, and earned absence
# ==========================================================================

class FactView:
    """A fact reduced to what a comparison may act on.

    `status` is one of:
      ATOM    an actionable constraint atom
      ABSENT  a proven/adjudicated absence of any constraint on that dimension
      BLOCKED the fact exists but is not actionable; carries its reason class

    BLOCKED is not a verdict and never leaves this module as one -- it becomes
    an UNKNOWN component with the reason attached.
    """

    __slots__ = ("key", "dimension", "scope_kind", "participant", "atom",
                 "status", "reason", "evidence", "provenance")

    def __init__(self, key, dimension, scope_kind, participant, atom, status,
                 reason, evidence, provenance):
        self.key = key
        self.dimension = dimension
        self.scope_kind = scope_kind
        self.participant = participant
        self.atom = atom
        self.status = status
        self.reason = reason
        self.evidence = evidence
        self.provenance = provenance


def _fact_key(f: dict):
    sc = f.get("scope") or {}
    return (sc.get("kind"), sc.get("participant"), f.get("dimension"))


def obligations_satisfied(ledger, unit: Unit, key) -> bool:
    """Are the section 18 claimant-side obligations REPRESENTED as satisfied?

    Obligations 1-3 (residue-honest exhaustion, template/emission adequacy, a
    per-dimension negative control that changes THAT claimant's output) are
    discharged by the claiming candidate at scoring time under its OWN rule.
    They are not projection content and the key never discharges them on a
    candidate's behalf, so they arrive as EVALUATION CONTEXT rather than as a
    projection field. Default: not represented.
    """
    if not ledger:
        return False
    return bool(ledger.get((unit.id,) + tuple(key)))


def read_fact(f: dict, unit: Unit, ledger=None) -> FactView:
    key = _fact_key(f)
    sc = f.get("scope") or {}
    d = f.get("disposition")
    prov = {"disposition": d}
    ev = f.get("evidence")
    mk = lambda atom, status, reason: FactView(
        key, f.get("dimension"), sc.get("kind"), sc.get("participant"),
        atom, status, reason, ev, prov)

    if d == "PRESENT":
        return mk(f.get("atom"), "ATOM", None)
    if d == "HUMAN_RESOLVED":
        # WRAPPER TRANSPARENCY: the payload is compared, the wrapper survives
        # in provenance. The adjudication METHOD is metadata and is never a
        # disposition value (register 28).
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
    if d in ("UNRESOLVED", "AMBIGUOUS"):
        return mk(None, "BLOCKED", "DISPOSITION_NOT_ACTIONABLE")
    return mk(None, "BLOCKED", "DISPOSITION_NOT_ACTIONABLE")


def fact_index(unit: Unit, ledger=None) -> dict:
    out = {}
    for f in unit.facts:
        v = read_fact(f, unit, ledger)
        out.setdefault(v.key, []).append(v)
    return out


# ==========================================================================
# ATOM SEMANTICS — section 13, and nothing beyond it
# ==========================================================================

def _values(atom):
    """An atom's value as a DISJUNCTION list. A printed `or` class is a small
    union (contract 13); a scalar is a one-element union."""
    v = atom.get("value")
    return list(v) if isinstance(v, list) else [v]


def _norm(v):
    return v.lower() if isinstance(v, str) else v


def _card_payload(atom):
    """DECLARED READING: a CARD atom's value carries {"comparison", "n"}."""
    v = atom.get("value")
    if isinstance(v, dict) and "comparison" in v and "n" in v:
        return v["comparison"], v["n"]
    return None, None


def _interval_payload(atom):
    """DECLARED READING: an INTERVAL atom's value carries {"min", "max"}."""
    v = atom.get("value")
    if isinstance(v, dict) and ("min" in v or "max" in v):
        lo = v.get("min")
        hi = v.get("max")
        return (lo if lo is not None else float("-inf"),
                hi if hi is not None else float("inf"))
    return None


def _card_range(comparison, n):
    if comparison == "=":
        return (n, n)
    if comparison == ">=":
        return (n, float("inf"))
    if comparison == ">":
        return (n + 1, float("inf"))
    if comparison == "<=":
        return (0, n)
    if comparison == "<":
        return (0, n - 1)
    return None


def _range_contains(inner, outer):
    return outer[0] <= inner[0] and inner[1] <= outer[1]


def _ranges_disjoint(a, b):
    return a[1] < b[0] or b[1] < a[0]


def _vocab_ok(dim, value):
    vocab = CLOSED_VOCABULARY.get(dim)
    if vocab is None:
        return True
    return _norm(value) in vocab


def _hierarchy_parents(subtype):
    return {t for t in HIERARCHY.get(_norm(subtype), set())}


# ==========================================================================
# ENTAILMENT
# ==========================================================================

def _entity_kinds(index, scope_key_prefix):
    """PRESENT entity_kind values declared at one scope, if any."""
    key = scope_key_prefix + ("entity_kind",)
    out = set()
    for v in index.get(key, []):
        if v.status == "ATOM" and (v.atom or {}).get("op") == "REQUIRES":
            out |= {_norm(x) for x in _values(v.atom)}
    return out


def _context_compatible(index_a, index_b, key):
    """Section 15. Differing PRESENT entity kinds make a scope incomparable."""
    prefix = (key[0], key[1])
    ka, kb = _entity_kinds(index_a, prefix), _entity_kinds(index_b, prefix)
    if ka and kb and not (ka & kb):
        return False
    return True


def _discharge_atom(a_atom, b_atom, dim):
    """Does antecedent atom `a_atom` discharge consequent atom `b_atom`?

    Returns (result, proof_kind, cr_anchor, reason). Never returns PROVEN_NOT:
    non-entailment is existential and needs a witness, which is handled one
    layer up.
    """
    anchor = (DIMENSIONS.get(dim) or {}).get("cr_anchor")
    if pj.canonical_json(a_atom) == pj.canonical_json(b_atom):
        return PROVEN, CR_CONTRACT, anchor, None

    if dim in EQUALITY_ONLY:
        return UNKNOWN, None, anchor, "DIMENSION_EQUALITY_ONLY"

    a_op, b_op = a_atom.get("op"), b_atom.get("op")

    if b_op == "REQUIRES":
        b_vals = _values(b_atom)
        for bv in b_vals:
            if not _vocab_ok(dim, bv):
                return UNKNOWN, None, anchor, "OPEN_DIMENSION_VALUE"
        if a_op == "REQUIRES":
            a_vals = _values(a_atom)
            for av in a_vals:
                if not _vocab_ok(dim, av):
                    return UNKNOWN, None, anchor, "OPEN_DIMENSION_VALUE"
            # A disjunctive antecedent discharges only if EVERY disjunct does.
            ok = all(any(_norm(av) == _norm(bv) for bv in b_vals)
                     for av in a_vals)
            if ok:
                return PROVEN, CR_CONTRACT, anchor, None
            return UNKNOWN, None, anchor, ("DISJUNCTION_NOT_UNIFORM"
                                           if len(a_vals) > 1 else
                                           "NO_CORPUS_WITNESS")
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
        ac, an = _card_payload(a_atom)
        bc, bn = _card_payload(b_atom)
        ar = _card_range(ac, an) if ac else None
        br = _card_range(bc, bn) if bc else None
        if ar and br and _range_contains(ar, br):
            return PROVEN, CR_CONTRACT, anchor, None
        return UNKNOWN, None, anchor, "NO_CORPUS_WITNESS"

    if b_op == "INTERVAL" and a_op == "INTERVAL":
        ar, br = _interval_payload(a_atom), _interval_payload(b_atom)
        if ar and br and _range_contains(ar, br):
            return PROVEN, CR_CONTRACT, anchor, None
        return UNKNOWN, None, anchor, "NO_CORPUS_WITNESS"

    return UNKNOWN, None, anchor, "NO_CORPUS_WITNESS"


def _hierarchy_discharges(index_a, key, b_atom, dim):
    """The ONE ratified hierarchy step: REQUIRES(subtype, X) discharges
    REQUIRES(card_type, parent-of-X). No other edge is asserted."""
    if dim != "card_type" or b_atom.get("op") != "REQUIRES":
        return None
    sub_key = (key[0], key[1], "subtype")
    wanted = {_norm(v) for v in _values(b_atom)}
    for v in index_a.get(sub_key, []):
        if v.status != "ATOM" or (v.atom or {}).get("op") != "REQUIRES":
            continue
        subs = _values(v.atom)
        if subs and all(_hierarchy_parents(s) & wanted for s in subs):
            return v
    return None


def _component(kind, key, result, proof_kind=None, cr_anchor=None,
               reason=None, atoms_a=None, atoms_b=None, evidence=None,
               provenance=None):
    return {
        "kind": kind,
        "scope": {"kind": key[0], "participant": key[1]} if key else None,
        "dimension": key[2] if key else None,
        "result": result,
        "proof_kind": proof_kind,
        "cr_anchor": cr_anchor,
        "unknown_reason": reason,
        "atoms_a": atoms_a,
        "atoms_b": atoms_b,
        "evidence": evidence or [],
        "provenance": provenance or [],
    }


def _ev(*views):
    out = []
    for v in views:
        if v is not None and getattr(v, "evidence", None):
            out.append(v.evidence)
    return out


def _prov(*views):
    return [v.provenance for v in views if v is not None and v.provenance]


def entailment_components(a: Unit, b: Unit, ledger=None) -> list:
    """Components of `constraint-set(a) entails constraint-set(b)`."""
    ia, ib = fact_index(a, ledger), fact_index(b, ledger)
    comps = []
    for key in sorted(ib, key=lambda k: (str(k[0]), str(k[1]), str(k[2]))):
        dim = key[2]
        for bv in ib[key]:
            if bv.status == "BLOCKED":
                comps.append(_component("ENTAILMENT", key, UNKNOWN,
                                        reason=bv.reason, atoms_b=bv.atom,
                                        evidence=_ev(bv), provenance=_prov(bv)))
                continue
            if bv.status == "ABSENT":
                # The consequent places NO constraint on this dimension, so
                # every object satisfies it. A tautology, not a claim about A.
                comps.append(_component(
                    "ENTAILMENT", key, PROVEN, CR_CONTRACT,
                    (DIMENSIONS.get(dim) or {}).get("cr_anchor"),
                    evidence=_ev(bv), provenance=_prov(bv)))
                continue
            if not _context_compatible(ia, ib, key):
                comps.append(_component("ENTAILMENT", key, UNKNOWN,
                                        reason="CONTEXT_INCOMPATIBLE",
                                        atoms_b=bv.atom, evidence=_ev(bv)))
                continue
            avs = ia.get(key, [])
            best = None
            for av in avs:
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
                hv = _hierarchy_discharges(ia, key, bv.atom, dim)
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
                why if r != PROVEN else None,
                atoms_a=av.atom, atoms_b=bv.atom,
                evidence=_ev(av, bv), provenance=_prov(av, bv)))
    return comps


def kleene(components) -> str:
    rs = [c["result"] for c in components]
    if any(r == PROVEN_NOT for r in rs):
        return PROVEN_NOT
    if rs and all(r == PROVEN for r in rs):
        return PROVEN
    return UNKNOWN


# ==========================================================================
# WITNESSES
# ==========================================================================

def _witness_satisfies(witness, unit: Unit, ledger=None):
    """(all_satisfied, any_violated, notes) for one unit's atoms.

    Checks ADMISSIBILITY and coverage mechanically against the witness's own
    declared value assignments. It never asks the corpus anything: whether the
    named card really carries those values is the supplier's evidence
    obligation, and it is traced, not assumed away.
    """
    assign = {k: [_norm(x) for x in (v if isinstance(v, list) else [v])]
              for k, v in (witness.get("assignments") or {}).items()}
    notes, all_ok, violated = [], True, False
    for f in unit.facts:
        v = read_fact(f, unit, ledger)
        if v.status != "ATOM":
            all_ok = False
            notes.append({"dimension": v.dimension, "why": v.reason or
                          "not an actionable atom"})
            continue
        dim, atom = v.dimension, v.atom
        if dim not in assign:
            all_ok = False
            notes.append({"dimension": dim, "why": "witness is silent on this "
                          "dimension"})
            continue
        have, op = assign[dim], atom.get("op")
        vals = [_norm(x) for x in _values(atom)]
        if op == "REQUIRES":
            ok = any(x in have for x in vals)
        elif op == "FORBIDS":
            ok = all(x not in have for x in vals)
        elif op == "EQUALITY":
            ok = any(x in have for x in vals)
        elif op == "CARD":
            c, n = _card_payload(atom)
            rng = _card_range(c, n) if c else None
            ok = bool(rng) and rng[0] <= len(have) <= rng[1]
        elif op == "INTERVAL":
            rng = _interval_payload(atom)
            nums = [x for x in have if isinstance(x, (int, float))]
            ok = bool(rng) and bool(nums) and all(rng[0] <= x <= rng[1]
                                                  for x in nums)
        else:
            ok = False
        if not ok:
            all_ok = False
            violated = True
            notes.append({"dimension": dim, "why": "witness violates this atom"})
    return all_ok, violated, notes


def _witness_admissible(witness) -> list:
    bad = []
    if not isinstance(witness, dict):
        return ["witness is not a record"]
    if not witness.get("corpus_ref"):
        bad.append("a CORPUS_WITNESS must pin the corpus_ref it was "
                   "established against")
    if not (witness.get("witness") or {}).get("oracle_id"):
        bad.append("a CORPUS_WITNESS must name its witness identity")
    if not isinstance(witness.get("assignments"), dict) or \
            not witness["assignments"]:
        bad.append("a CORPUS_WITNESS must declare the dimension/value domain "
                   "it relies on")
    bad += pj._validate_evidence(witness.get("evidence"), "corpus witness")
    return bad


# ==========================================================================
# THE OPERATIONS
# ==========================================================================

def _record(op, direction, a: Unit, b: Unit, result, components,
            proof_kind=None, reason=None, **extra):
    rec = {
        "algebra": {"schema": ALGEBRA_NAME, "version": ALGEBRA_VERSION},
        "projection": {"schema": pj.SCHEMA_NAME, "version": pj.SCHEMA_VERSION},
        "operation": op,
        "direction": direction,
        "result": result,
        "proof_kind": proof_kind,
        "inputs": {"a": a.id, "b": b.id},
        "components": sorted(components, key=lambda c: pj.canonical_json(c)),
        "evidence": [],
        "unknown_reason": reason,
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
    # Every record self-checks on the way out. A trace discipline that has to
    # be remembered at each call site is the "reporter listed as a gate"
    # failure one layer up.
    assert_proof_trace(rec)
    return rec


def _order(a: Unit, b: Unit):
    """Canonical operand order for a SYMMETRIC operation, so the record is
    byte-identical under reversal rather than merely semantically equal."""
    return (a, b) if a.id <= b.id else (b, a)


def entails(a: Unit, b: Unit, witness=None, ledger=None) -> dict:
    """OP_ENTAILS. DIRECTIONAL: does a's constraint set entail b's?"""
    comps = entailment_components(a, b, ledger)
    result = kleene(comps) if comps else UNKNOWN
    reason = None
    proof_kind = CR_CONTRACT if result == PROVEN else None
    extra = {}
    if not comps:
        result, reason = UNKNOWN, "NO_COMPARABLE_CONTENT"
    elif result != PROVEN and witness is not None:
        bad = _witness_admissible(witness)
        if bad:
            result, reason = UNKNOWN, "WITNESS_INADMISSIBLE"
            extra["witness_rejected"] = bad
        else:
            sat_a, _, _ = _witness_satisfies(witness, a, ledger)
            sat_b, viol_b, notes = _witness_satisfies(witness, b, ledger)
            if sat_a and viol_b:
                result, proof_kind = PROVEN_NOT, CORPUS_WITNESS
                extra["witness"] = witness
                extra["corpus_ref"] = witness["corpus_ref"]
                comps.append(_component(
                    "DISTINGUISHING_WITNESS", None, PROVEN_NOT,
                    CORPUS_WITNESS, None, None,
                    evidence=[witness["evidence"]],
                    provenance=[{"witness_notes": notes}]))
            else:
                reason = "WITNESS_DOES_NOT_SATISFY"
    elif result != PROVEN:
        reason = _first_reason(comps) or "NO_CORPUS_WITNESS"
    return _record("OP_ENTAILS", "A_ENTAILS_B", a, b, result, comps,
                   proof_kind, reason, **extra)


def _first_reason(comps):
    for c in sorted(comps, key=lambda c: pj.canonical_json(c)):
        if c["result"] == UNKNOWN and c.get("unknown_reason"):
            return c["unknown_reason"]
    return None


def _blocker_components(a: Unit, b: Unit, ledger=None) -> list:
    """Everything uncontracted that can only move a verdict toward UNKNOWN."""
    comps = []

    if a.participants != b.participants:
        comps.append(_component("PARTICIPANTS", None, UNKNOWN,
                                reason="PARTICIPANT_SET_DIFFERS",
                                atoms_a=list(a.participants),
                                atoms_b=list(b.participants)))
    else:
        comps.append(_component("PARTICIPANTS", None, PROVEN, CR_CONTRACT,
                                "CR 115.1 / contract 12 bare ordinal",
                                atoms_a=list(a.participants),
                                atoms_b=list(b.participants)))

    # ACTION HEADS — necessary-condition identity only. Never a positive
    # semantic claim, and never PROVEN_NOT.
    if a.head_disposition != "PRESENT" or b.head_disposition != "PRESENT":
        comps.append(_component("ACTION_HEADS", None, UNKNOWN,
                                reason="ACTION_HEAD_NOT_COMPARABLE",
                                atoms_a=list(a.heads), atoms_b=list(b.heads)))
    elif a.heads != b.heads:
        comps.append(_component("ACTION_HEADS", None, UNKNOWN,
                                reason="NO_CONTRACTED_COMPARISON_LAW",
                                atoms_a=list(a.heads), atoms_b=list(b.heads)))
    else:
        comps.append(_component(
            "ACTION_HEADS", None, PROVEN, CR_CONTRACT,
            "structural identity of the printed head sequence; NOT a semantic "
            "action-equivalence claim",
            atoms_a=list(a.heads), atoms_b=list(b.heads)))

    # COST — register 27. Any region blocks; bytes never disprove.
    if a.regions or b.regions:
        comps.append(_component("COST_RESIDUE", None, UNKNOWN,
                                reason="UNCONTRACTED_COST_RESIDUE",
                                atoms_a=len(a.regions), atoms_b=len(b.regions)))
    else:
        comps.append(_component("COST_RESIDUE", None, PROVEN, CR_CONTRACT,
                                "no structural COST region on either side",
                                atoms_a=0, atoms_b=0))

    # RELATIONS — section 17's closed table authorizes no relation comparison.
    if a.relations or b.relations:
        comps.append(_component("RELATIONS", None, UNKNOWN,
                                reason="NO_CONTRACTED_COMPARISON_LAW",
                                atoms_a=len(a.relations),
                                atoms_b=len(b.relations)))
    else:
        comps.append(_component("RELATIONS", None, PROVEN, CR_CONTRACT,
                                "no projected relation edge on either side; "
                                "this is NOT a claim that no relation exists",
                                atoms_a=0, atoms_b=0))
    return comps


def _coverage_components(a: Unit, b: Unit, ledger=None) -> list:
    """A dimension actionable on one side and missing on the other is
    MISSING_FACT, never ABSENT. This is the strict-consumer guard."""
    ia, ib = fact_index(a, ledger), fact_index(b, ledger)
    comps = []
    for key in sorted(set(ia) | set(ib),
                      key=lambda k: (str(k[0]), str(k[1]), str(k[2]))):
        ha = any(v.status in ("ATOM", "ABSENT") for v in ia.get(key, []))
        hb = any(v.status in ("ATOM", "ABSENT") for v in ib.get(key, []))
        if ha != hb:
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
    """A PROVEN_NOT that arrived from a sub-record must carry that record's
    witness and corpus_ref forward, or `assert_proof_trace` would be asked to
    accept an existential proof with no pinned pool behind it."""
    for r in records:
        if r.get("proof_kind") == CORPUS_WITNESS and r.get("corpus_ref"):
            return {"witness": r["witness"], "corpus_ref": r["corpus_ref"]}
    return {}


def eligibility_equal(a: Unit, b: Unit, witness=None, ledger=None) -> dict:
    """OP_ELIGIBILITY_EQUALITY. SYMMETRIC mutual entailment of constraint sets."""
    a, b = _order(a, b)
    ab = entails(a, b, witness, ledger)
    ba = entails(b, a, witness, ledger)
    comps = [
        _component("DIRECTION_A_TO_B", None, ab["result"], ab.get("proof_kind"),
                   None, ab.get("unknown_reason")),
        _component("DIRECTION_B_TO_A", None, ba["result"], ba.get("proof_kind"),
                   None, ba.get("unknown_reason")),
    ]
    comps += _coverage_components(a, b, ledger)
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
                   directions={"a_to_b": ab["result"], "b_to_a": ba["result"]},
                   **extra)


def equal(a: Unit, b: Unit, witness=None, ledger=None) -> dict:
    """OP_EQUALITY. SYMMETRIC strict semantic equality of two occurrences."""
    a, b = _order(a, b)
    elig = eligibility_equal(a, b, witness, ledger)
    comps = [_component("ELIGIBILITY", None, elig["result"],
                        elig.get("proof_kind"), None,
                        elig.get("unknown_reason"))]
    comps += _blocker_components(a, b, ledger)
    result = kleene(comps)
    pk = CR_CONTRACT if result == PROVEN else (
        CORPUS_WITNESS if result == PROVEN_NOT else None)
    extra = _carried_witness(elig) if result == PROVEN_NOT else {}
    return _record("OP_EQUALITY", "SYMMETRIC", a, b, result,
                   comps + elig["components"], pk,
                   _first_reason(comps) if result == UNKNOWN else None, **extra)


def _contradiction_components(a: Unit, b: Unit, ledger=None) -> list:
    """CR contract contradictions -- the ONLY admissible proof of empty
    intersection. Corpus absence is inadmissible, in both directions."""
    ia, ib = fact_index(a, ledger), fact_index(b, ledger)
    comps = []
    for key in sorted(set(ia) & set(ib),
                      key=lambda k: (str(k[0]), str(k[1]), str(k[2]))):
        dim = key[2]
        if not _context_compatible(ia, ib, key):
            continue
        anchor = (DIMENSIONS.get(dim) or {}).get("cr_anchor")
        for av, bv in itertools.product(ia[key], ib[key]):
            if av.status != "ATOM" or bv.status != "ATOM":
                continue
            x, y = av.atom, bv.atom
            hit = None
            for lo, hi in ((x, y), (y, x)):
                if lo.get("op") == "REQUIRES" and hi.get("op") == "FORBIDS":
                    if any(_norm(v) == _norm(w) for v in _values(lo)
                           for w in _values(hi)):
                        hit = ("contract 13 atom semantics: REQUIRES against "
                               "FORBIDS on one dimension")
            if hit is None and x.get("op") == y.get("op") == "REQUIRES" \
                    and dim in SINGLE_VALUED_EXHAUSTIVE:
                xs = {_norm(v) for v in _values(x)}
                ys = {_norm(v) for v in _values(y)}
                if xs and ys and not (xs & ys):
                    hit = (f"{anchor}: different values on a closed, "
                           f"single-valued, must-have dimension")
            if hit is None and x.get("op") == y.get("op") == "CARD":
                xc, xn = _card_payload(x)
                yc, yn = _card_payload(y)
                xr = _card_range(xc, xn) if xc else None
                yr = _card_range(yc, yn) if yc else None
                if xr and yr and _ranges_disjoint(xr, yr):
                    hit = f"{anchor}: disjoint cardinality ranges"
            if hit is None and x.get("op") == y.get("op") == "INTERVAL":
                xr, yr = _interval_payload(x), _interval_payload(y)
                if xr and yr and _ranges_disjoint(xr, yr):
                    hit = f"{anchor}: disjoint intervals"
            if hit:
                comps.append(_component(
                    "CR_CONTRADICTION", key, PROVEN_NOT, CR_CONTRACT, hit,
                    atoms_a=av.atom, atoms_b=bv.atom,
                    evidence=_ev(av, bv), provenance=_prov(av, bv)))
    return comps


def intersection(a: Unit, b: Unit, witness=None, ledger=None) -> dict:
    """OP_INTERSECTION. SYMMETRIC. One proposition, two poles.

    PROVEN     NONEMPTY_INTERSECTION_PROVEN -- a corpus witness satisfying both.
    PROVEN_NOT EMPTY_INTERSECTION_PROVEN -- a CR contract contradiction.
    UNKNOWN    everything else, including compatibility and a failed search.
    """
    a, b = _order(a, b)
    contras = _contradiction_components(a, b, ledger)
    if contras:
        return _record("OP_INTERSECTION", "SYMMETRIC", a, b, PROVEN_NOT,
                       contras, CR_CONTRACT, None,
                       proof_label="EMPTY_INTERSECTION_PROVEN")

    comps, reason, extra = [], "NO_CORPUS_WITNESS", {}
    comps.append(_component("CR_CONTRADICTION", None, UNKNOWN,
                            reason="NO_CR_CONTRADICTION"))
    if witness is not None:
        bad = _witness_admissible(witness)
        if bad:
            reason = "WITNESS_INADMISSIBLE"
            extra["witness_rejected"] = bad
        else:
            sat_a, _, na = _witness_satisfies(witness, a, ledger)
            sat_b, _, nb = _witness_satisfies(witness, b, ledger)
            if sat_a and sat_b:
                comps.append(_component(
                    "CORPUS_WITNESS", None, PROVEN, CORPUS_WITNESS,
                    None, None, evidence=[witness["evidence"]],
                    provenance=[{"assignments_relied_on":
                                 sorted(witness["assignments"])}]))
                return _record("OP_INTERSECTION", "SYMMETRIC", a, b, PROVEN,
                               comps[1:], CORPUS_WITNESS, None,
                               proof_label="NONEMPTY_INTERSECTION_PROVEN",
                               witness=witness,
                               corpus_ref=witness["corpus_ref"])
            reason = "WITNESS_DOES_NOT_SATISFY"
            extra["witness_notes"] = {"a": na, "b": nb}
    return _record("OP_INTERSECTION", "SYMMETRIC", a, b, UNKNOWN, comps,
                   None, reason, **extra)


def overlap(a: Unit, b: Unit, witness=None, ledger=None) -> dict:
    """Reader for OP_INTERSECTION's PROVEN pole."""
    r = intersection(a, b, witness, ledger)
    r["reads_pole"] = "NONEMPTY_INTERSECTION_PROVEN"
    return r


def disjoint(a: Unit, b: Unit, ledger=None) -> dict:
    """Reader for OP_INTERSECTION's PROVEN_NOT pole. Takes NO witness:
    a witness is inadmissible for disjointness, so the parameter does not
    exist rather than being ignored."""
    r = intersection(a, b, None, ledger)
    r["reads_pole"] = "EMPTY_INTERSECTION_PROVEN"
    return r


_DISPATCH = {
    "OP_ENTAILS": entails,
    "OP_EQUALITY": equal,
    "OP_ELIGIBILITY_EQUALITY": eligibility_equal,
    "OP_INTERSECTION": intersection,
}


def compare(op: str, a: Unit, b: Unit, **kw) -> dict:
    """The one entry point. An operation the frozen table does not register is
    REFUSED -- adding an operator is a ratification, not an import."""
    if op not in OPERATIONS or op not in _DISPATCH:
        fc.halt(f"comparison operation {op!r} is not registered in "
                f"{ALGEBRA_PATH.name}. The authorized set is "
                f"{sorted(OPERATIONS)}. Minting an operator to complete a "
                f"table is a ratification, not an implementation detail.")
    return _DISPATCH[op](a, b, **kw)


# ==========================================================================
# PROOF-RECORD DISCIPLINE
# ==========================================================================

def assert_no_native_identifiers(rec) -> None:
    """A proof record may never expose a candidate-native identifier."""
    for _path, key in pj._walk_keys(rec):
        if str(key).lower() in pj.FORBIDDEN_NATIVE:
            fc.halt(f"proof record exposes candidate-native field {key!r}")
    for s in pj._walk_strings(rec):
        if s.lower() in pj.FORBIDDEN_NATIVE:
            fc.halt(f"proof record exposes candidate-native value {s!r}")


def assert_proof_trace(rec) -> None:
    """A PROVEN or PROVEN_NOT record must trace to admissible evidence."""
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
        fc.halt("a CORPUS_WITNESS verdict must pin the corpus_ref it was "
                "established against -- it is a claim about the printed pool")
    if not rec.get("evidence"):
        fc.halt(f"a {rec['result']} verdict carries no evidence trace. "
                f"Normalization is not evidence and a verdict without a "
                f"deterministic trace back through the projection is not a "
                f"proof.")


def assert_not_a_projection_fact(doc: dict, rec: dict) -> None:
    """Injecting a derived verdict into a projection document must FAIL."""
    rig = copy.deepcopy(doc)
    rig["occurrences"][0]["facts"][0]["B2_verdict"] = rec["result"]
    if pj.validate(rig) == []:
        fc.halt("a derived comparison verdict was accepted into the canonical "
                "projection substrate. Derived relationships are never "
                "canonical stored facts.")


# ==========================================================================
# THE DERIVED CONSUMER-QUESTION LAYER — derived output, never a key
# ==========================================================================

def b1(a: Unit, b: Unit, witness=None, ledger=None) -> dict:
    r = equal(a, b, witness, ledger)
    return {"question": "B1", "verdict": r["result"],
            "unknown_reason": r.get("unknown_reason"), "record": r}


def b2(a: Unit, b: Unit, witness=None, ledger=None) -> dict:
    a, b = _order(a, b)
    ab, ba = entails(a, b, witness, ledger), entails(b, a, witness, ledger)
    inter = intersection(a, b, witness, ledger)
    if ab["result"] == PROVEN and ba["result"] == PROVEN:
        label = "EQUAL"
    elif ab["result"] == PROVEN:
        label = "NARROWER"
    elif ba["result"] == PROVEN:
        label = "BROADER"
    elif inter["result"] == PROVEN_NOT:
        label = "DISJOINT"
    elif inter["result"] == PROVEN:
        label = "OVERLAPPING"
    else:
        label = "UNKNOWN"
    return {"question": "B2", "relation_label": label,
            "_label_law": "a derived answer label for one consumer question, "
                          "not a comparison verdict",
            "entails_a_b": ab["result"], "entails_b_a": ba["result"],
            "intersection": inter["result"],
            "per_dimension": [c for c in ab["components"]
                              if c["kind"] == "ENTAILMENT"],
            "records": {"a_to_b": ab, "b_to_a": ba, "intersection": inter}}


def b3(a: Unit, b: Unit, witness=None, ledger=None) -> dict:
    """B3 is PARTIAL BY LAW, and the blocked arm is stated rather than filled."""
    a, b = _order(a, b)
    elig = b2(a, b, witness, ledger)
    if a.head_disposition != "PRESENT" or b.head_disposition != "PRESENT":
        identity = "NOT_COMPARABLE"
    elif a.heads == b.heads:
        identity = "IDENTICAL"
    else:
        identity = "DIFFERENT"
    return {
        "question": "B3",
        "action_head_identity": identity,
        "_identity_law": "STRUCTURAL identity of the printed head sequence. It "
                         "is evidence for a future ruling, never a semantic "
                         "claim, and never PROVEN_NOT.",
        "action_equivalence": {
            "verdict": UNKNOWN,
            "unknown_reason": "NO_CONTRACTED_COMPARISON_LAW",
            "why": "contract section 17's closed operation table authorizes no "
                   "action-head comparison, and an action head is expressly "
                   "not a section 14 dimension. The operator is NOT minted "
                   "here; the arm returns UNKNOWN and the gap is reported.",
        },
        "eligibility": elig,
        "derivable": "PARTIAL",
    }


B4_READING = ALGEBRA["derived_question_layer"]["B4"]["declared_reading"]


def b4(a: Unit, b: Unit, witness=None, ledger=None) -> dict:
    a, b = _order(a, b)
    named = {d for k in ("destination", "timing", "quantity")
             for d in B4_READING[k]}
    ab, ba = entails(a, b, witness, ledger), entails(b, a, witness, ledger)
    per = {}
    for rec, side in ((ab, "a_to_b"), (ba, "b_to_a")):
        for c in rec["components"]:
            if c["kind"] != "ENTAILMENT":
                continue
            per.setdefault(c["dimension"], {})[side] = c["result"]
    equal_dims = sorted(d for d, v in per.items()
                        if v.get("a_to_b") == v.get("b_to_a") == PROVEN)
    inter = intersection(a, b, witness, ledger)
    differing = sorted({c["dimension"] for c in inter["components"]
                        if c["kind"] == "CR_CONTRADICTION"
                        and c["result"] == PROVEN_NOT and c["dimension"]})
    rest_equal = all(d in equal_dims for d in per if d not in named)
    hit = any(d in named for d in differing)
    answer = PROVEN if (rest_equal and hit and per) else UNKNOWN
    return {"question": "B4", "answer": answer,
            "per_dimension": {d: v for d, v in sorted(per.items())},
            "dimensions_equal_proven": equal_dims,
            "dimensions_differing_proven": differing,
            "declared_reading": B4_READING,
            "_reading_law": "the summary depends on a DECLARED READING of "
                            "section 20's wording onto section 14 row names; "
                            "the per-dimension table above does not",
            "records": {"a_to_b": ab, "b_to_a": ba, "intersection": inter}}


def c1(pair, direction: str, witness=None, ledger=None) -> dict:
    """C1 — what prevents the replacement, in a NAMED direction.

    `pair` is the frozen UNORDERED pair. The direction is an argument derived
    at answer time; no directed pair is stored and the pair-storage law is
    untouched.
    """
    x, y = pair
    if direction not in ("X_REPLACES_Y", "Y_REPLACES_X"):
        fc.halt(f"C1 direction {direction!r} must be named explicitly; a "
                f"directional operation may never silently reverse operands.")
    replacement, original = (x, y) if direction == "X_REPLACES_Y" else (y, x)
    strict = equal(replacement, original, witness, ledger)
    ent = entails(replacement, original, witness, ledger)
    blockers = [c for c in strict["components"] + ent["components"]
                if c["result"] != PROVEN]
    return {
        "question": "C1",
        "direction": direction,
        "replacement": replacement.id,
        "original": original.id,
        "blockers": sorted(blockers, key=lambda c: pj.canonical_json(c)),
        "blocker_count": len(blockers),
        "_empty_is_not_a_claim": "an empty blocker list means no blocking fact "
                                 "is derivable under v1 law. It is NOT a proof "
                                 "that the replacement holds: no positive "
                                 "strict-replacement relation is contracted.",
        "records": {"strict_equality": strict, "entailment": ent},
    }


def c2(unit: Unit) -> dict:
    """C2 — a within-card structural read; no comparison operation involved."""
    kinds = sorted({r.get("kind") for r in unit.relations})
    linked = [r for r in unit.relations
              if r.get("kind") in ("CR607_LINKAGE", "COREFERENCE")]
    return {"question": "C2", "occurrence": unit.id,
            "relation_kinds": kinds, "linked_edges": len(linked),
            "_absence_law": "absence of an edge is NOT proof of no linkage; an "
                            "unresolvable reference stays UNRESOLVED",
            "derivable": "STRUCTURAL"}


def discovery1(a: Unit, b: Unit, ledger=None) -> dict:
    a, b = _order(a, b)
    pool = []
    for u in (a, b):
        for f in u.facts:
            v = read_fact(f, u, ledger)
            if v.status != "ATOM":
                continue
            pool.append((v.key, v.atom))
            if v.dimension == "subtype" and v.atom.get("op") == "REQUIRES":
                for s in _values(v.atom):
                    for parent in _hierarchy_parents(s):
                        pool.append(((v.scope_kind, v.participant, "card_type"),
                                     {"op": "REQUIRES", "value": parent}))
    shared, seen = [], set()
    for key, atom in pool:
        sig = pj.canonical_json([key, atom])
        if sig in seen:
            continue
        seen.add(sig)
        probe = {"dimension": key[2], "atom": atom, "disposition": "PRESENT",
                 "scope": ({"kind": key[0], "participant": key[1]}
                           if key[0] == "PARTICIPANT" else {"kind": key[0]}),
                 "derivation_class": "EXTRACT-4",
                 "provenance_class": "rule-derived",
                 "evidence": pj._evidence()}
        target = Unit({"occurrence": {"oracle_id": "shared", "face": 0,
                                      "paragraph": 0, "clause": 0},
                       "participants": list(a.participants),
                       "action_heads": [], "action_head_disposition":
                       "UNRESOLVED", "facts": [probe]}, a.role)
        ra = kleene(entailment_components(a, target, ledger))
        rb = kleene(entailment_components(b, target, ledger))
        if ra == PROVEN and rb == PROVEN:
            shared.append({"dimension": key[2], "scope": key[0], "atom": atom})
    shared.sort(key=pj.canonical_json)
    return {"question": "DISCOVERY-1", "shared_atoms": shared,
            "shared_count": len(shared),
            "index_shaped": all(not isinstance(s["atom"].get("value"), (list, dict))
                                for s in shared),
            "_pool_law": "candidates are the two units' OWN atoms plus their "
                         "ratified hierarchy ancestors. No atom is invented "
                         "and no vocabulary is minted."}


# ==========================================================================
# E1 — a trace/provenance property, one per unordered pair, never prose
# ==========================================================================

def e1_domain() -> dict:
    """The frozen E1 domain: the unique unordered pairs of the SEMANTIC
    tranches, never multiplied by question count and never over the
    semantics-free control tranche."""
    if not PAIRS_PATH.exists():
        fc.halt(f"no frozen pairing at {PAIRS_PATH}")
    d = json.loads(PAIRS_PATH.read_text(encoding="utf-8"))
    sem = sorted({tuple(sorted(p)) for t in ("S0", "S1", "S2")
                  for p in d["pairs"][t]})
    ctrl = {tuple(sorted(p)) for p in d["pairs"]["PAIR_K_CHAIN"]}
    return {
        "semantic_tranches": ["S0", "S1", "S2"],
        "unique_semantic_pairs": len(sem),
        "control_tranche_pairs_excluded_from_domain": len(ctrl - set(sem)),
        "instancing": "ONE trace per unordered pair, never one per question "
                      "instance",
        "pairs_sha256": d["pairs_sha256"],
    }


def e1_trace(records, pair=None) -> dict:
    """Validate and expose the section 19 trace supporting a derived comparison.

    Produces STRUCTURE, never prose. A hand-authored explanation string would
    be an unscoreable free-text surface and would smuggle native vocabulary
    into a key required to be architecture-neutral.
    """
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
                steps.append({
                    "operation": rec["operation"],
                    "result": rec["result"],
                    "component": c["kind"],
                    "dimension": c.get("dimension"),
                    "scope": c.get("scope"),
                    "cr_anchor": c.get("cr_anchor"),
                    "proof_kind": c.get("proof_kind"),
                    "evidence_category": (e or {}).get("category"),
                    "evidence_view": (e or {}).get("view"),
                    "occurrence": [occ.get("oracle_id"), occ.get("face"),
                                   occ.get("paragraph"), occ.get("clause")],
                    "span": [span.get("start"), span.get("end")],
                })
    if bad:
        fc.halt("section 19 trace is not producible:\n  - "
                + "\n  - ".join(sorted(set(bad))))
    steps.sort(key=pj.canonical_json)
    return {"question": "E1", "pair": list(pair) if pair else None,
            "trace_steps": steps, "step_count": len(steps),
            "_form": "a trace/provenance property, never a prose gold answer"}


def honesty1(a: Unit, b: Unit, ledger=None) -> dict:
    r = equal(a, b, None, ledger)
    blocked = [c for c in r["components"]
               if c.get("unknown_reason") in
               ("DISPOSITION_NOT_ACTIONABLE", "ABSENCE_NOT_EARNED",
                "ADJUDICATION_PAYLOAD_UNREADABLE")]
    return {"question": "HONESTY-1",
            "non_actionable_components": sorted(
                blocked, key=lambda c: pj.canonical_json(c)),
            "blocks_strict_claim": r["result"] != PROVEN,
            "strict_verdict": r["result"]}


# ==========================================================================
# FIXTURES — synthetic only. No real card is used as a comparison fixture.
# ==========================================================================

OID_A = "00000000-0000-0000-0000-00000000000a"
OID_B = "00000000-0000-0000-0000-00000000000b"


def _doc(oid, facts, role="CANDIDATE_EXPORT", heads=("destroy",),
         regions=(), relations=(), participants=(0,), clause=0):
    return {
        "schema": pj.SCHEMA_NAME,
        "version": pj.SCHEMA_VERSION,
        "artifact_role": role,
        "occurrences": [{
            "occurrence": {"oracle_id": oid, "face": 0, "paragraph": 0,
                           "clause": clause},
            "participants": list(participants),
            "action_heads": [
                {"head": h, "cr_anchor": "CR 701", "derivation_class":
                 "EXTRACT-1", "evidence": pj._evidence(oid)} for h in heads],
            "action_head_disposition": "PRESENT" if heads else "UNRESOLVED",
            "facts": facts,
            "structural_regions": list(regions),
            "relations": list(relations),
        }],
    }


def _f(dim, op, value, oid, disposition="PRESENT", participant=0, **extra):
    f = {"dimension": dim, "atom": {"op": op, "value": value},
         "disposition": disposition,
         "scope": {"kind": "PARTICIPANT", "participant": participant},
         "derivation_class": "EXTRACT-1", "provenance_class": "rule-derived",
         "evidence": pj._evidence(oid)}
    f.update(extra)
    return f


def _unit(doc):
    return next(iter(load_document(doc).values()))


def _cost_region(oid):
    return {"role": "COST", "cr_anchors": ["CR 113.3b", "CR 602.1a"],
            "derivation_class": "EXTRACT-0",
            "evidence": pj._evidence(oid, 0, 9)}


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

    def halts(fn, *a, **kw):
        try:
            fn(*a, **kw)
            return False
        except SystemExit:
            return True

    print("=" * 74)
    print("AQ4 COMPARISON ALGEBRA — CONTROLS (each rigged red on its own path)")
    print("=" * 74)

    print("\nLAW / VOCABULARY PROVENANCE")
    check(f"the operation table is read from {ALGEBRA_PATH.name} "
          f"({len(OPERATIONS)} operations, {len(RESULTS)} verdicts, "
          f"{len(PROOF_KINDS)} proof kinds)",
          len(OPERATIONS) == 4 and set(RESULTS) == {PROVEN, PROVEN_NOT, UNKNOWN}
          and set(PROOF_KINDS) == {CR_CONTRACT, CORPUS_WITNESS})
    check("the ratified subtype-to-type hierarchy is CONSUMED, not re-derived "
          f"({len(HIERARCHY)} edges, {len(ol.AMBIGUOUS_SUBTYPES)} ambiguous)",
          len(HIERARCHY) > 400 and not ol.AMBIGUOUS_SUBTYPES)

    # -- ALG.NO_NEW_OPERATOR ------------------------------------------------
    ua = _unit(_doc(OID_A, [_f("card_type", "REQUIRES", "creature", OID_A)]))
    ub = _unit(_doc(OID_B, [_f("card_type", "REQUIRES", "creature", OID_B)]))
    check("ALG.NO_NEW_OPERATOR an unregistered comparison op is refused",
          halts(compare, "OP_BROADER_THAN", ua, ub))
    check("ALG.NO_NEW_OPERATOR-RIG a registered op runs on the same inputs",
          compare("OP_ENTAILS", ua, ub)["result"] == PROVEN)

    print("\nTHREE-VALUED CORE")
    # A: creature. B: creature AND blue. A does not entail B; nothing
    # contradicts; no witness -> UNKNOWN, and specifically not PROVEN_NOT.
    ub2 = _unit(_doc(OID_B, [_f("card_type", "REQUIRES", "creature", OID_B),
                             _f("color", "REQUIRES", "blue", OID_B)]))
    r = entails(ua, ub2)
    check("ALG.UNKNOWN_NOT_FALSE inability to prove entailment is UNKNOWN, "
          "never PROVEN_NOT", r["result"] == UNKNOWN, r["result"])
    closed_world = PROVEN_NOT if any(c["result"] != PROVEN
                                     for c in r["components"]) else PROVEN
    check("ALG.UNKNOWN_NOT_FALSE-RIG a closed-world reading of the SAME "
          "components would say PROVEN_NOT, and the algebra does not",
          closed_world == PROVEN_NOT and r["result"] == UNKNOWN)

    check("ALG.MISSING_NOT_ABSENT a dimension present on one side and missing "
          "on the other is MISSING_FACT and blocks, never ABSENT",
          any(c["unknown_reason"] == "MISSING_FACT"
              for c in eligibility_equal(ua, ub2)["components"]))
    absent_claims = [c for c in eligibility_equal(ua, ub2)["components"]
                     if c.get("unknown_reason") == "ABSENCE_NOT_EARNED"
                     or c["result"] == PROVEN_NOT]
    check("ALG.MISSING_NOT_ABSENT-RIG the missing dimension produced NO "
          "absence claim and NO negative verdict", absent_claims == [])

    # The POSITIVE arm of the same law: non-entailment is EXISTENTIAL, so it is
    # reachable only through a corpus witness -- never through the absence of a
    # proof. Same fixture as ALG.UNKNOWN_NOT_FALSE, one input added.
    dwit = {"corpus_ref": fcb.corpus_ref_current(),
            "witness": {"oracle_id": "00000000-0000-0000-0000-0000000000dd"},
            "assignments": {"card_type": ["creature"], "color": []},
            "evidence": pj._evidence("00000000-0000-0000-0000-0000000000dd")}
    rw = entails(ua, ub2, witness=dwit)
    check("ALG.UNKNOWN_NOT_FALSE PROVEN_NOT is reachable ONLY through a "
          "distinguishing corpus witness, pinned to its corpus_ref",
          rw["result"] == PROVEN_NOT and rw["proof_kind"] == CORPUS_WITNESS
          and rw.get("corpus_ref") and not halts(assert_proof_trace, rw),
          rw["result"])
    ew = equal(ua, ub2, witness=dwit)
    check("ALG.UNKNOWN_NOT_FALSE a component PROVEN_NOT propagates to equality "
          "and carries the witness pin with it",
          ew["result"] == PROVEN_NOT and ew.get("corpus_ref")
          and not halts(assert_proof_trace, ew), ew["result"])
    nonwit = dict(dwit, assignments={"card_type": ["creature"],
                                     "color": ["blue"]})
    check("ALG.UNKNOWN_NOT_FALSE-RIG a witness that does NOT distinguish "
          "leaves the same pair UNKNOWN",
          entails(ua, ub2, witness=nonwit)["result"] == UNKNOWN)

    print("\nEQUALITY")
    check("ALG.EQUALITY_PROVEN identical constraint sets and identical heads "
          "prove equality", equal(ua, ub)["result"] == PROVEN,
          equal(ua, ub)["result"])
    unresolved = _unit(_doc(OID_B, [
        _f("card_type", "REQUIRES", "creature", OID_B),
        _f("condition", "EQUALITY", "as long as you control a Forest", OID_B,
           disposition="UNRESOLVED")]))
    check("ALG.EQUALITY_RESIDUE_BLOCK relevant uncontracted residue "
          "(UNRESOLVED) blocks PROVEN equality",
          equal(ua, unresolved)["result"] == UNKNOWN)
    check("ALG.EQUALITY_RESIDUE_BLOCK-RIG dropping the residue row makes the "
          "SAME pair PROVEN, so the block is the residue and not the fixture",
          equal(ua, ub)["result"] == PROVEN)

    print("\nCOST RESIDUE")
    cost_b = _unit(_doc(OID_B, [_f("card_type", "REQUIRES", "creature", OID_B)],
                        regions=[_cost_region(OID_B)]))
    r = equal(ua, cost_b)
    naive = kleene([c for c in r["components"] if c["kind"] != "COST_RESIDUE"])
    check("ALG.COST_RESIDUE_BLOCK a cost region blocks a PROVEN equality that "
          "ignoring it would grant", r["result"] == UNKNOWN and naive == PROVEN,
          f"real={r['result']} ignoring-cost={naive}")
    check("ALG.COST_RESIDUE_BLOCK the block is reported as cost residue",
          r.get("unknown_reason") == "UNCONTRACTED_COST_RESIDUE" or
          any(c["unknown_reason"] == "UNCONTRACTED_COST_RESIDUE"
              for c in r["components"]))
    cost_a = _unit(_doc(OID_A, [_f("card_type", "REQUIRES", "creature", OID_A)],
                        regions=[{"role": "COST", "cr_anchors": ["CR 606.2"],
                                  "derivation_class": "EXTRACT-0",
                                  "evidence": pj._evidence(OID_A, 0, 3)}]))
    check("ALG.COST_RESIDUE_BLOCK-RIG differing cost bytes NEVER yield "
          "PROVEN_NOT", equal(cost_a, cost_b)["result"] == UNKNOWN)
    check("ALG.COST_RESIDUE_BLOCK cost is absent from the dimension vocabulary "
          "entirely, so no absence claim over cost can exist",
          "cost" not in DIMENSIONS)

    print("\nACTION HEADS")
    noheads = _unit(_doc(OID_B, [_f("card_type", "REQUIRES", "creature", OID_B)],
                         heads=()))
    check("ALG.ACTION_UNKNOWN_BLOCK a missing action head prevents a false "
          "action equality", equal(ua, noheads)["result"] == UNKNOWN)
    other = _unit(_doc(OID_B, [_f("card_type", "REQUIRES", "creature", OID_B)],
                       heads=("exile",)))
    e = equal(ua, other)
    check("ALG.ACTION_UNKNOWN_BLOCK-RIG a DIFFERENT head is UNKNOWN too, never "
          "PROVEN_NOT", e["result"] == UNKNOWN)
    check("ALG.ACTION_UNKNOWN_BLOCK B3's action arm returns UNKNOWN with the "
          "missing-law reason rather than minting the operator",
          b3(ua, other)["action_equivalence"]["unknown_reason"]
          == "NO_CONTRACTED_COMPARISON_LAW")

    print("\nOVERLAP — WITNESS OR NOTHING")
    compat_a = _unit(_doc(OID_A, [_f("supertype", "REQUIRES", "snow", OID_A)]))
    compat_b = _unit(_doc(OID_B, [_f("subtype", "REQUIRES", "soldier", OID_B)]))
    check("ALG.OVERLAP_NEEDS_WITNESS compatible constraints with no witness do "
          "NOT prove overlap",
          overlap(compat_a, compat_b)["result"] == UNKNOWN)
    check("ALG.OVERLAP_SEARCH_MISS_UNKNOWN a search that found nothing is "
          "UNKNOWN and is reported as such",
          overlap(compat_a, compat_b).get("unknown_reason")
          == "NO_CORPUS_WITNESS")
    wit = {"corpus_ref": fcb.corpus_ref_current(),
           "witness": {"oracle_id": "00000000-0000-0000-0000-0000000000cc"},
           "assignments": {"supertype": ["snow"], "subtype": ["soldier"]},
           "evidence": pj._evidence("00000000-0000-0000-0000-0000000000cc")}
    ov = overlap(compat_a, compat_b, witness=wit)
    check("ALG.OVERLAP_NEEDS_WITNESS-RIG the SAME pair with an admissible "
          "witness is PROVEN, pinned to its corpus_ref",
          ov["result"] == PROVEN and ov["proof_kind"] == CORPUS_WITNESS
          and ov.get("corpus_ref"), ov["result"])
    nopin = dict(wit)
    nopin.pop("corpus_ref")
    check("ALG.OVERLAP_NEEDS_WITNESS a witness with no corpus_ref is "
          "inadmissible", overlap(compat_a, compat_b, witness=nopin)
          .get("unknown_reason") == "WITNESS_INADMISSIBLE")
    silent = dict(wit, assignments={"supertype": ["snow"]})
    check("ALG.OVERLAP_NEEDS_WITNESS a witness silent on a needed dimension is "
          "not a proof", overlap(compat_a, compat_b, witness=silent)["result"]
          == UNKNOWN)

    print("\nDISJOINT — CR CONTRADICTION OR NOTHING")
    zone_a = _unit(_doc(OID_A, [_f("zone", "REQUIRES", "battlefield", OID_A)]))
    zone_b = _unit(_doc(OID_B, [_f("zone", "REQUIRES", "graveyard", OID_B)]))
    dj = disjoint(zone_a, zone_b)
    check("ALG.DISJOINT_NEEDS_CR_CONTRADICTION a closed, single-valued, "
          "must-have dimension proves empty intersection",
          dj["result"] == PROVEN_NOT and dj["proof_kind"] == CR_CONTRACT,
          dj["result"])
    check("ALG.DISJOINT_NONCONTRADICTION_UNKNOWN compatible values stay "
          "UNKNOWN, and are never read as overlap",
          disjoint(compat_a, compat_b)["result"] == UNKNOWN)
    check("ALG.DISJOINT_NEEDS_CR_CONTRADICTION corpus absence is inadmissible: "
          "`disjoint` takes no witness parameter at all",
          "witness" not in disjoint.__code__.co_varnames)
    forb = _unit(_doc(OID_B, [_f("color", "FORBIDS", "blue", OID_B)]))
    reqd = _unit(_doc(OID_A, [_f("color", "REQUIRES", "blue", OID_A)]))
    check("ALG.DISJOINT_NEEDS_CR_CONTRADICTION-RIG REQUIRES against FORBIDS on "
          "one dimension is the atom-semantics arm",
          disjoint(reqd, forb)["result"] == PROVEN_NOT)

    print("\nDIMENSION CONTRACTS")
    check("ALG.NO_CONTROLLER_COMPLEMENT FORBIDS(controller, you) never entails "
          "REQUIRES(controller, opponent)",
          entails(_unit(_doc(OID_A, [_f("controller_relation", "FORBIDS",
                                        "you", OID_A)])),
                  _unit(_doc(OID_B, [_f("controller_relation", "REQUIRES",
                                        "opponent", OID_B)])))["result"]
          == UNKNOWN)
    check("ALG.NO_CONTROLLER_COMPLEMENT-RIG the same complement step IS taken "
          "on zone, which is closed, single-valued AND must-have",
          entails(zone_a, _unit(_doc(OID_B, [_f("zone", "FORBIDS", "graveyard",
                                                OID_B)])))["result"] == PROVEN)
    check("ALG.NO_CONTROLLER_COMPLEMENT controller_relation is excluded by "
          "name as well as by property",
          "controller_relation" in COMPLEMENT_FORBIDDEN
          and "controller_relation" not in SINGLE_VALUED_EXHAUSTIVE
          and "owner_relation" != "controller_relation")
    eqonly = _unit(_doc(OID_A, [_f("counter_kind", "REQUIRES", "charge",
                                   OID_A)]))
    eqonly2 = _unit(_doc(OID_B, [_f("counter_kind", "REQUIRES", "loyalty",
                                    OID_B)]))
    check("ALG.EQUALITY_ONLY an equality-only dimension yields nothing beyond "
          "verbatim equality",
          entails(eqonly, eqonly2)["result"] == UNKNOWN
          and "counter_kind" in EQUALITY_ONLY)
    sub = _unit(_doc(OID_A, [_f("subtype", "REQUIRES", "goblin", OID_A)]))
    typ = _unit(_doc(OID_B, [_f("card_type", "REQUIRES", "creature", OID_B)]))
    check("ALG.HIERARCHY the ratified subtype-to-type edge discharges a "
          "card_type requirement", entails(sub, typ)["result"] == PROVEN)
    kinds_a = _unit(_doc(OID_A, [
        _f("entity_kind", "REQUIRES", "card", OID_A),
        _f("card_type", "REQUIRES", "creature", OID_A)]))
    kinds_b = _unit(_doc(OID_B, [
        _f("entity_kind", "REQUIRES", "permanent", OID_B),
        _f("card_type", "REQUIRES", "creature", OID_B)]))
    check("ALG.CONTEXT_GUARD differing entity kinds make a scope incomparable "
          "(a creature card is not a permanent)",
          any(c["unknown_reason"] == "CONTEXT_INCOMPATIBLE"
              for c in entails(kinds_a, kinds_b)["components"]))
    check("ALG.PARTICIPANT_EXPLICIT differing participant sets block rather "
          "than being best-effort paired",
          any(c["unknown_reason"] == "PARTICIPANT_SET_DIFFERS"
              for c in equal(ua, _unit(_doc(
                  OID_B, [_f("card_type", "REQUIRES", "creature", OID_B)],
                  participants=(0, 1))))["components"]))

    print("\nDISPOSITIONS")
    key_doc = _doc(OID_B, [_f("card_type", "REQUIRES", "creature", OID_B,
                              disposition="HUMAN_RESOLVED",
                              resolved={"atom": {"op": "REQUIRES",
                                                 "value": "creature"}},
                              adjudication={"method": "INDEPENDENT_DUAL",
                                            "disagreement_status": "RESOLVED"})],
                   role="KEY")
    ku = _unit(key_doc)
    r = equal(ua, ku)
    wrapper = [pv for c in r["components"] for pv in c.get("provenance", [])
               if isinstance(pv, dict) and pv.get("adjudication")]
    check("ALG.HUMAN_RESOLVED_TRANSPARENT the payload is compared and the "
          "wrapper survives in the proof trace",
          r["result"] == PROVEN and wrapper, f"{r['result']} wrapper={bool(wrapper)}")
    cand_hr = copy.deepcopy(key_doc)
    cand_hr["artifact_role"] = "CANDIDATE_EXPORT"
    check("ALG.CANDIDATE_HUMAN_RESOLVED_REJECTED a candidate export emitting "
          "HUMAN_RESOLVED is rejected at ingest", halts(load_document, cand_hr))

    ap_doc = _doc(OID_B, [_f("color", "REQUIRES", "blue", OID_B,
                             disposition="ABSENT_PROVEN")])
    apu = _unit(ap_doc)
    unearned = eligibility_equal(reqd, apu)
    check("ALG.ABSENT_PROOF_REQUIRED ABSENT_PROVEN without the claimant "
          "obligations cannot act as proven absence",
          any(c["unknown_reason"] == "ABSENCE_NOT_EARNED"
              for c in unearned["components"]))
    ledger = {(apu.id, "PARTICIPANT", 0, "color"): True}
    earned = eligibility_equal(reqd, apu, ledger=ledger)
    check("ALG.ABSENT_PROOF_REQUIRED-RIG with the obligations represented the "
          "SAME row becomes actionable, so the control is the obligations and "
          "not the fixture",
          not any(c["unknown_reason"] == "ABSENCE_NOT_EARNED"
                  for c in earned["components"]))

    print("\nDERIVED / CANONICAL BOUNDARY")
    doc_a = _doc(OID_A, [_f("card_type", "REQUIRES", "creature", OID_A)])
    rec = equal(ua, ub)
    check("ALG.DERIVED_NOT_PROJECTION injecting a comparison verdict into the "
          "canonical projection fails",
          not halts(assert_not_a_projection_fact, doc_a, rec))
    rigged_doc = copy.deepcopy(doc_a)
    rigged_doc["occurrences"][0]["facts"][0]["B2_verdict"] = "BROADER"
    check("ALG.DERIVED_NOT_PROJECTION-RIG the projection validator is what "
          "refuses it", pj.validate(rigged_doc) != [])
    check("ALG.NO_NATIVE_BRANCH a candidate-native semantic branch in a "
          "projection turns red", halts(load_document, _native_rig(doc_a)))
    check("ALG.NO_NATIVE_BRANCH a proof record carrying a native identifier "
          "is refused", halts(assert_no_native_identifiers,
                              {"canonical_owner": "assertion"}))

    print("\nPROOF TRACE")
    check("ALG.PROOF_TRACE_REQUIRED a real PROVEN record carries its trace",
          not halts(assert_proof_trace, rec))
    stripped = copy.deepcopy(rec)
    stripped["evidence"] = []
    check("ALG.PROOF_TRACE_REQUIRED-RIG a PROVEN record with no admissible "
          "trace is refused", halts(assert_proof_trace, stripped))
    nokind = copy.deepcopy(rec)
    nokind["proof_kind"] = None
    check("ALG.PROOF_TRACE_REQUIRED a verdict with no proof kind is refused",
          halts(assert_proof_trace, nokind))
    badreason = {"result": UNKNOWN, "unknown_reason": "BECAUSE_I_SAID_SO"}
    check("ALG.PROOF_TRACE_REQUIRED an unregistered UNKNOWN reason class is "
          "refused", halts(assert_proof_trace, badreason))

    print("\nDETERMINISM · SYMMETRY · DIRECTION")
    check("ALG.SYMMETRY a symmetric operation is byte-identical under operand "
          "reversal",
          pj.canonical_json(equal(ua, ub)) == pj.canonical_json(equal(ub, ua)))
    check("ALG.SYMMETRY-RIG the two operands are genuinely distinct objects, "
          "so the identity is not vacuous", ua.id != ub.id)
    f_ab = entails(sub, typ)
    f_ba = entails(typ, sub)
    check("ALG.DIRECTION_EXPLICIT a directional operation names its direction "
          "and does not silently reverse",
          f_ab["direction"] == f_ba["direction"] == "A_ENTAILS_B"
          and f_ab["inputs"] != f_ba["inputs"]
          and f_ab["result"] != f_ba["result"],
          f"{f_ab['result']} vs {f_ba['result']}")
    check("ALG.DIRECTION_EXPLICIT C1 refuses an unnamed direction",
          halts(c1, (ua, ub), "WHICHEVER"))
    c_xy = c1((ua, ub), "X_REPLACES_Y")
    c_yx = c1((ua, ub), "Y_REPLACES_X")
    check("ALG.DIRECTION_EXPLICIT C1's direction is an argument over the "
          "FROZEN UNORDERED pair, and both directions derive from it",
          c_xy["replacement"] == ua.id and c_yx["replacement"] == ub.id)
    check("ALG.DETERMINISM_X2 two runs of the same comparison are "
          "byte-identical",
          pj.canonical_json(equal(ua, ub)) == pj.canonical_json(equal(ua, ub)))
    perm = copy.deepcopy(_doc(OID_B, [
        _f("color", "REQUIRES", "blue", OID_B),
        _f("card_type", "REQUIRES", "creature", OID_B)]))
    perm2 = copy.deepcopy(perm)
    perm2["occurrences"][0]["facts"].reverse()
    check("ALG.DETERMINISM_X2 a permitted reordering of the input "
          "canonicalizes and compares identically",
          pj.canonical_json(equal(ua, _unit(perm)))
          == pj.canonical_json(equal(ua, _unit(perm2))))

    print("\nDERIVED QUESTION LAYER")
    check("B2 produces a relation label from the three verdicts",
          b2(sub, typ)["relation_label"] == "NARROWER",
          b2(sub, typ)["relation_label"])
    check("B2 DISJOINT comes only from the CR contradiction pole",
          b2(zone_a, zone_b)["relation_label"] == "DISJOINT")
    check("B4 reports the full per-dimension table beside its declared "
          "reading", "per_dimension" in b4(zone_a, zone_b)
          and b4(zone_a, zone_b)["declared_reading"]["destination"] == ["zone"])
    d1 = discovery1(sub, typ)
    check("DISCOVERY-1 finds the shared broad fact behind a narrower "
          "predicate", any(s["dimension"] == "card_type" and
                           s["atom"]["value"] == "creature"
                           for s in d1["shared_atoms"]), d1["shared_atoms"])
    check("DISCOVERY-1 invents no atom outside the two units and their "
          "ratified ancestors",
          all(s["dimension"] in ("card_type", "subtype")
              for s in d1["shared_atoms"]))
    blockers = c1((ua, cost_b), "X_REPLACES_Y")
    check("C1 names the blocking component rather than asserting a "
          "replacement", blockers["blocker_count"] > 0)
    h1 = honesty1(ua, unresolved)
    check("HONESTY-1 names the non-actionable component that blocks the "
          "strict claim",
          h1["blocks_strict_claim"] and h1["non_actionable_components"])

    print("\nE1 — TRACE, NEVER PROSE")
    dom = e1_domain()
    check("E1's domain is the frozen semantic pair union, not multiplied by "
          "question count",
          dom["unique_semantic_pairs"] == 354,
          dom["unique_semantic_pairs"])
    tr = e1_trace(rec, pair=(ua.id, ub.id))
    check("E1 exposes a validated section 19 trace and emits no prose",
          tr["step_count"] > 0 and "explanation" not in pj.canonical_json(tr))
    badrec = copy.deepcopy(rec)
    for c in badrec["components"]:
        for e in c.get("evidence", []):
            e["view"] = "CANONICAL"
    check("E1-RIG normalization presented as evidence turns the trace red",
          halts(e1_trace, badrec))

    print("\nPROBE-LIBRARY GUARD")
    p.must_capture(
        lambda pair: equal(*pair)["result"] == PROVEN,
        [((ua, ub), True), ((ua, cost_b), False), ((ua, other), False),
         ((ua, noheads), False), ((ua, unresolved), False)],
        name="strict equality")
    check("GUARD D the strict-equality predicate agrees with its own "
          "known-positive fixture", True)

    print()
    if fails:
        print(f"SELFTEST FAILED — {len(fails)} control(s): {fails}")
        return 1
    print("SELFTEST PASSED — every control fired on the path it guards, and "
          "every rigging turned its control red.")
    return 0


def _native_rig(doc):
    rig = copy.deepcopy(doc)
    rig["occurrences"][0]["facts"][0]["canonical_owner"] = "assertion"
    return rig


# ==========================================================================
# CENSUS / VALIDATION
# ==========================================================================

def validate_pins() -> list:
    bad = []
    dep = ALGEBRA["dependencies"]
    if dep["corpus_ref"] != fcb.corpus_ref_current():
        bad.append(f"corpus_ref moved: pinned {dep['corpus_ref']} != live "
                   f"{fcb.corpus_ref_current()}")
    if dep["cr_edition"] != CR.CR_PATH.name:
        bad.append("CR edition moved")
    import hashlib
    live = hashlib.sha256(CR.CR_PATH.read_bytes()).hexdigest()
    if dep["cr_sha256"] != live:
        bad.append("CR edition hash moved")
    if dep["hierarchy_edges"] != len(HIERARCHY):
        bad.append(f"hierarchy edges moved: pinned {dep['hierarchy_edges']} "
                   f"!= live {len(HIERARCHY)}")
    if dep["hierarchy_ambiguous_subtypes"] != len(ol.AMBIGUOUS_SUBTYPES):
        bad.append("ambiguous-subtype count moved")
    return bad


def census() -> int:
    print("=" * 74)
    print("AQ4 SHARED COMPARISON ALGEBRA — CENSUS (law only, no card answer)")
    print("=" * 74)
    print(f"  algebra                 {ALGEBRA_NAME} {ALGEBRA_VERSION}")
    print(f"  consumes projection     {pj.SCHEMA_NAME} {pj.SCHEMA_VERSION}")
    print(f"  verdicts                {', '.join(RESULTS)}")
    print(f"  proof kinds             {', '.join(PROOF_KINDS)}")
    print(f"  UNKNOWN reason classes  {len(REASONS)}")
    print(f"  operations              {len(OPERATIONS)}")
    for oid, o in OPERATIONS.items():
        print(f"    {oid:<28s} {o['direction']:<12s} {o['name']}")
    print(f"  single-valued exhaustive {sorted(SINGLE_VALUED_EXHAUSTIVE)}")
    print(f"  complement forbidden     {sorted(COMPLEMENT_FORBIDDEN)}")
    print(f"  equality-only dimensions {sorted(EQUALITY_ONLY)}")
    print(f"  ratified hierarchy edges {len(HIERARCHY)} "
          f"({len(ol.AMBIGUOUS_SUBTYPES)} ambiguous)")
    print("\n  derived consumer questions")
    for q, spec in ALGEBRA["derived_question_layer"].items():
        if q.startswith("_"):
            continue
        print(f"    {q:<12s} {spec.get('derivable', '-')}")
    d = e1_domain()
    print(f"\n  E1 domain               {d['unique_semantic_pairs']} unique "
          f"semantic pairs (control-only pairs excluded: "
          f"{d['control_tranche_pairs_excluded_from_domain']})")
    bad = validate_pins()
    print(f"  dependency pins         {'MATCH' if not bad else bad}")
    return 0 if not bad else 1


def main() -> int:
    ap_ = argparse.ArgumentParser(
        description="AQ4 shared candidate-neutral comparison algebra.")
    ap_.add_argument("--selftest", action="store_true")
    ap_.add_argument("--census", action="store_true")
    ap_.add_argument("--validate-pins", action="store_true")
    a = ap_.parse_args()
    if a.selftest:
        return selftest()
    if a.census:
        return census()
    if a.validate_pins:
        bad = validate_pins()
        if bad:
            fc.halt("comparison-algebra dependency pins do not match live "
                    "machinery:\n  - " + "\n  - ".join(bad))
        print("comparison-algebra dependency pins MATCH live machinery.")
        return 0
    ap_.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
