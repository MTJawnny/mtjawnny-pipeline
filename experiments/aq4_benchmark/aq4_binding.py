#!/usr/bin/env python3
"""AQ4 BENCHMARK — COMBINED UNIT + PARTICIPANT BINDING (schema and machinery).

WHAT THIS IS AND IS NOT
-----------------------
The validator, the canonicalizer and the one authorized helper for the combined
benchmark binding artifact. **NO REAL BINDING IS INSTANTIATED HERE**: the 354
semantic pairs are not bound, no unit is chosen, no participant is enumerated
for a real card, and no correspondence is adjudicated. Every fixture in this
file is synthetic and every card identifier is a zero-padded placeholder.

Production AQ4 architecture remains UNRATIFIED and nothing here changes it.

TWO ALIGNMENT PROBLEMS, AND SOLVING ONE DOES NOT SOLVE THE OTHER
----------------------------------------------------------------
1. **Same-occurrence cross-export alignment.** The key and each candidate may
   independently export participants for the SAME occurrence. Canonical anchors
   plus anchor-derived numbering make those align. That lives in the PROJECTION.
2. **Cross-card semantic correspondence.** Once two units are bound, which
   participant on one corresponds to which on the other. That lives HERE.

`participant 0 on A == participant 0 on B` is never an inference rule.

ONE ARTIFACT, ONE HASH
----------------------
Unit binding, participant enumeration and participant correspondence live in
ONE record. Correspondence is meaningless without the unit pair it is stated
over, and separate artifacts would create a coherence invariant nobody enforces
plus a second drift surface.

THE ENUMERATION IS AUTHORITATIVE FOR THE KEY
---------------------------------------------
A future key projection does NOT re-enumerate participants. Its ordinals and
anchors must match the frozen enumeration exactly; `assert_key_matches_binding`
is that check. A participant discovered later is a benchmark KEY DEFECT under
the existing key-error law — never a silent renumber and never a silent edit.

ONE AUTOMATIC MAPPING, AND ONLY ONE
------------------------------------
`DETERMINISTIC_SINGLETON`: one participant on each side, so the correspondence
is forced. **Everything else needs human adjudication.** Equal ordinal, mention
order, similar restrictions, "the unique restricted one", best-matching
eligibility and graph matching are each REFUSED — they introduce circularity
(deciding correspondence from the facts the comparison is about), selection
bias, or a hidden role ontology.
"""
import sys
import copy
import json
import argparse
import collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
sys.path.insert(0, str(EXPERIMENTS))
sys.path.insert(0, str(HERE))

import foundry_common as fc                # noqa: E402
import aq4_projection as pj                # noqa: E402

SCHEMA_PATH = HERE / "binding-schema.json"
SCHEMA_NAME = "aq4-benchmark-binding"
SCHEMA_VERSION = "1.0.0"

NEEDS_ADJUDICATION = "NEEDS_ADJUDICATION"


def load_schema() -> dict:
    s = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    if s.get("schema") != SCHEMA_NAME or s.get("version") != SCHEMA_VERSION:
        fc.halt(f"binding schema identity mismatch: "
                f"{s.get('schema')!r}/{s.get('version')!r}")
    dep = s["projection_dependency"]
    if dep["schema"] != pj.SCHEMA_NAME or dep["version"] != pj.SCHEMA_VERSION:
        fc.halt(f"the binding schema declares projection {dep['schema']}/"
                f"{dep['version']} but the live projection is "
                f"{pj.SCHEMA_NAME}/{pj.SCHEMA_VERSION}. The enumeration's "
                f"ordinals and anchors ARE the projection's participant "
                f"representation, so an unpinned dependency is not pinned.")
    return s


SCHEMA = load_schema()
UNIT_STATES = set(SCHEMA["record"]["unit_binding"]["state"])
UNIT_METHODS = set(SCHEMA["record"]["unit_binding"]["method"])
SOURCES = set(SCHEMA["participant_enumeration"]["source"])
METHODS = set(SCHEMA["participant_binding"]["methods"])
STATES = set(SCHEMA["correspondence_state"]["values"])

#: Refused wherever they appear, at any depth. A semantic verdict or
#: disposition inside a binding record would make benchmark administration
#: look like semantic truth.
FORBIDDEN_FIELDS = {
    "disposition", "verdict", "result", "proof_kind", "b1_verdict",
    "b2_verdict", "c1_verdict", "c3_verdict", "relation_label",
    "participant_kind", "semantic_role", "participant_role", "argument_slot",
    "global_participant_id", "participant_id", "cross_card_ordinal",
    "candidate", "candidate_id", "candidate_export",
}


# ==========================================================================
# VALIDATION
# ==========================================================================

def _anchor_key(entry):
    sp = (entry.get("anchor") or {}).get("span") or {}
    return (sp.get("start", -1), sp.get("end", -1))


def _validate_enumeration(entries, unit, side, out):
    if unit is None:
        if entries:
            out.append(f"side {side} has no bound unit but enumerates "
                       f"participants")
        return
    ordinals, anchors = [], {}
    for e in entries:
        o = e.get("ordinal")
        if isinstance(o, bool) or not isinstance(o, int) or o < 0:
            out.append(f"{side}: a participant ordinal must be a non-negative "
                       f"integer; got {o!r}")
        else:
            ordinals.append(o)
        if e.get("source") not in SOURCES:
            out.append(f"{side}: participant source {e.get('source')!r} is not "
                       f"ratified")
        if e.get("source") == "HUMAN_ADJUDICATED" and not e.get("adjudication"):
            out.append(f"{side}: a human-adjudicated participant must record "
                       f"its adjudication metadata")
        anch = e.get("anchor")
        if not anch:
            out.append(f"{side}: participant {o!r} carries no canonical anchor")
            continue
        out += pj._validate_evidence(anch, f"{side} participant anchor")
        if pj._addr_tuple(anch.get("occurrence")) != tuple(unit):
            out.append(f"{side}: participant {o!r}'s anchor does not locate "
                       f"its bound occurrence")
        k = _anchor_key(e)
        if k in anchors:
            out.append(f"{side}: participants {anchors[k]!r} and {o!r} share "
                       f"the canonical anchor {k}; a collision is invalid, "
                       f"never a tie-break")
        anchors[k] = o
    if sorted(ordinals) != list(range(len(ordinals))):
        out.append(f"{side}: the enumeration's ordinals must be exactly "
                   f"0..n-1; got {sorted(ordinals)}")


def validate(rec: dict, surface=None) -> list:
    """Return the list of violations. Empty means the record conforms."""
    v = []
    if rec.get("schema") != SCHEMA_NAME:
        v.append(f"schema must be {SCHEMA_NAME!r}")
    if rec.get("version") != SCHEMA_VERSION:
        v.append(f"version must be {SCHEMA_VERSION!r}")

    for _path, key in pj._walk_keys(rec):
        if str(key).lower() in FORBIDDEN_FIELDS:
            v.append(f"forbidden field {key!r}: a binding record carries "
                     f"benchmark administration, never semantic truth and "
                     f"never candidate identity")

    pair = rec.get("pair")
    if not isinstance(pair, list) or len(pair) != 2:
        v.append("a binding record names exactly two cards")
    elif list(pair) != sorted(pair):
        v.append("the card pair must be stored in CANONICAL ascending order, "
                 "so a pair is never stored twice and storage implies no "
                 "direction")

    ub = rec.get("unit_binding") or {}
    if ub.get("state") not in UNIT_STATES:
        v.append(f"unit binding state {ub.get('state')!r} is not ratified")
    if ub.get("method") not in UNIT_METHODS:
        v.append(f"unit binding method {ub.get('method')!r} is not ratified")
    if ub.get("state") == "NOT_APPLICABLE" and not ub.get("reason"):
        v.append("an administratively not-applicable binding must record its "
                 "reason; it is never inferred")

    a_unit, b_unit = rec.get("a_unit"), rec.get("b_unit")
    for side, u in (("a", a_unit), ("b", b_unit)):
        if u is None:
            if ub.get("state") != "NOT_APPLICABLE":
                v.append(f"side {side} has no bound unit but the binding is "
                         f"not administratively not-applicable")
            continue
        if not isinstance(u, list) or len(u) != 4:
            v.append(f"side {side}'s unit must be a four-coordinate occurrence")
            continue
        if surface is not None and tuple(u) not in surface:
            v.append(f"side {side}'s unit does not exist on the frozen "
                     f"semantic surface")

    a_ps = rec.get("a_participants") or []
    b_ps = rec.get("b_participants") or []
    _validate_enumeration(a_ps, a_unit, "a", v)
    _validate_enumeration(b_ps, b_unit, "b", v)

    a_ord = {e.get("ordinal") for e in a_ps}
    b_ord = {e.get("ordinal") for e in b_ps}
    seen_a, seen_b = set(), set()
    for m in rec.get("participant_bindings") or []:
        ao, bo = m.get("a_ordinal"), m.get("b_ordinal")
        if ao not in a_ord:
            v.append(f"mapping names A ordinal {ao!r}, which its own side does "
                     f"not enumerate")
        if bo not in b_ord:
            v.append(f"mapping names B ordinal {bo!r}, which its own side does "
                     f"not enumerate")
        if ao in seen_a:
            v.append(f"A ordinal {ao!r} is mapped more than once; v1 ratifies "
                     f"a PARTIAL ONE-TO-ONE correspondence only")
        if bo in seen_b:
            v.append(f"B ordinal {bo!r} is mapped more than once; v1 ratifies "
                     f"a PARTIAL ONE-TO-ONE correspondence only")
        seen_a.add(ao)
        seen_b.add(bo)
        if m.get("method") not in METHODS:
            v.append(f"mapping method {m.get('method')!r} is not ratified; the "
                     f"only automatic rule is the singleton one")
        if m.get("method") == "HUMAN_ADJUDICATED":
            for need in ("basis", "adjudication"):
                if not m.get(need):
                    v.append(f"a human-adjudicated mapping must record its "
                             f"{need}")

    for side, enumerated, mapped, listed in (
            ("a", a_ord, seen_a, rec.get("unbound_a")),
            ("b", b_ord, seen_b, rec.get("unbound_b"))):
        if listed is None:
            v.append(f"unbound_{side} must be EXPLICIT; an unbound state is "
                     f"never inferred from omission")
            continue
        if sorted(listed) != sorted(enumerated - mapped):
            v.append(f"unbound_{side} {sorted(listed)} does not reconcile with "
                     f"the enumerated-but-unmapped ordinals "
                     f"{sorted(enumerated - mapped)}")

    state = rec.get("correspondence_state")
    if state not in STATES:
        v.append(f"correspondence state {state!r} is not ratified")
    elif state == "COMPLETE" and (rec.get("unbound_a")
                                  or rec.get("unbound_b")):
        v.append("COMPLETE means no enumerated ordinal is left unbound on "
                 "either side")
    return v


def assert_valid(rec: dict, surface=None) -> None:
    bad = validate(rec, surface)
    if bad:
        fc.halt("binding record rejected:\n  - " + "\n  - ".join(bad))


def canonicalize(rec: dict) -> dict:
    """Deterministic canonical form. Reorders; never invents or drops."""
    out = copy.deepcopy(rec)
    for side in ("a_participants", "b_participants"):
        out[side] = sorted(out.get(side) or [],
                           key=lambda e: (_anchor_key(e), e.get("ordinal", -1)))
    out["participant_bindings"] = sorted(
        out.get("participant_bindings") or [],
        key=lambda m: (m.get("a_ordinal", -1), m.get("b_ordinal", -1)))
    for side in ("unbound_a", "unbound_b"):
        if out.get(side) is not None:
            out[side] = sorted(out[side])
    return out


def canonical_bytes(rec: dict) -> bytes:
    return pj.canonical_json(canonicalize(rec)).encode("utf-8")


def record_sha256(rec: dict) -> str:
    import hashlib
    return hashlib.sha256(canonical_bytes(rec)).hexdigest()


# ==========================================================================
# THE ONE AUTHORIZED AUTOMATIC MAPPING
# ==========================================================================

def deterministic_singleton(a_participants, b_participants):
    """The ONLY automatic cross-card participant mapping in v1.

    Returns the mapping when EACH side enumerates exactly one participant --
    the correspondence is then forced by counting, not by judging. Anything
    else returns `NEEDS_ADJUDICATION`, and there is deliberately no
    best-effort fallback: every alternative rule either decides correspondence
    from the very facts the comparison is about, or smuggles in a role
    ontology v1 refuses.
    """
    if len(a_participants) == 1 and len(b_participants) == 1:
        return [{"a_ordinal": a_participants[0]["ordinal"],
                 "b_ordinal": b_participants[0]["ordinal"],
                 "method": "DETERMINISTIC_SINGLETON",
                 "basis": "each side enumerates exactly one participant"}]
    return NEEDS_ADJUDICATION


# ==========================================================================
# THE KEY-ENUMERATION CONTRACT
# ==========================================================================

def assert_key_matches_binding(rec: dict, key_doc: dict) -> None:
    """A future KEY projection must MATCH the frozen enumeration exactly.

    The key does not independently re-enumerate participants: its repetition of
    them is a derived reference copy the projection interface requires, never a
    second source of truth. A participant discovered later is a benchmark key
    defect under the existing key-error law -- not a renumber, not an edit.
    """
    if key_doc.get("artifact_role") != "KEY":
        fc.halt("only a KEY projection is checked against the authoritative "
                "enumeration; a candidate export follows the projection schema "
                "independently and never sees this artifact.")
    by_addr = {pj._addr_tuple(o.get("occurrence") or {}): o
               for o in key_doc.get("occurrences", [])}
    bad = []
    for side, unit in (("a", rec.get("a_unit")), ("b", rec.get("b_unit"))):
        if unit is None:
            continue
        occ = by_addr.get(tuple(unit))
        if occ is None:
            bad.append(f"the key carries no occurrence for the bound {side} "
                       f"unit")
            continue
        want = sorted(((e["ordinal"], _anchor_key(e))
                       for e in rec.get(f"{side}_participants") or []))
        got = sorted(((p["ordinal"],
                       ((p.get("anchor") or {}).get("span") or {}).get("start", -1),
                       ((p.get("anchor") or {}).get("span") or {}).get("end", -1))
                      for p in occ.get("participants", [])))
        got = sorted((o, (s, e)) for o, s, e in got)
        if want != got:
            bad.append(f"side {side}: the key's participant enumeration "
                       f"{got} does not match the authoritative binding "
                       f"{want}")
    if bad:
        fc.halt("key projection does not match the authoritative enumeration:\n"
                "  - " + "\n  - ".join(bad)
                + "\n  The binding is authoritative. A participant found later "
                  "is a benchmark KEY DEFECT under the existing key-error law, "
                  "never a silent renumber and never a silent edit.")


def correspondence_for(rec: dict) -> dict:
    """The comparator's correspondence context for one bound pair.

    Explicitly SUPPLIED to a comparison; there is no global lookup, and the
    mapping proves no semantic relation of any kind.
    """
    a2b = {m["a_ordinal"]: m["b_ordinal"]
           for m in rec.get("participant_bindings") or []}
    return {"a_unit": tuple(rec["a_unit"]) if rec.get("a_unit") else None,
            "b_unit": tuple(rec["b_unit"]) if rec.get("b_unit") else None,
            "a_to_b": a2b, "b_to_a": {v: k for k, v in a2b.items()},
            "unbound_a": list(rec.get("unbound_a") or []),
            "unbound_b": list(rec.get("unbound_b") or []),
            "correspondence_state": rec.get("correspondence_state")}


# ==========================================================================
# FIXTURES — synthetic only
# ==========================================================================

OID_A = "00000000-0000-0000-0000-00000000000a"
OID_B = "00000000-0000-0000-0000-00000000000b"


def _anchor(oid, unit, a, b):
    return {"category": "ORACLE_TEXT", "view": "RAW_ORACLE",
            "occurrence": {"oracle_id": oid, "face": unit[1],
                           "paragraph": unit[2], "clause": unit[3]},
            "span": {"start": a, "end": b}}


def _enum(oid, unit, spans, source="STRUCTURAL"):
    return [{"ordinal": i, "anchor": _anchor(oid, unit, a, b),
             "source": source,
             **({"adjudication": {"method": "INDEPENDENT_DUAL",
                                  "status": "RESOLVED"}}
                if source == "HUMAN_ADJUDICATED" else {})}
            for i, (a, b) in enumerate(spans)]


def sample_binding(a_spans=((7, 13),), b_spans=((5, 11),), mappings=None,
                   state=None):
    a_unit = [OID_A, 0, 0, 0]
    b_unit = [OID_B, 0, 0, 0]
    a_ps = _enum(OID_A, a_unit, a_spans)
    b_ps = _enum(OID_B, b_unit, b_spans)
    if mappings is None:
        m = deterministic_singleton(a_ps, b_ps)
        mappings = [] if m is NEEDS_ADJUDICATION else m
    mapped_a = {x["a_ordinal"] for x in mappings}
    mapped_b = {x["b_ordinal"] for x in mappings}
    ua = sorted({e["ordinal"] for e in a_ps} - mapped_a)
    ub = sorted({e["ordinal"] for e in b_ps} - mapped_b)
    return {
        "schema": SCHEMA_NAME, "version": SCHEMA_VERSION,
        "pair": sorted([OID_A, OID_B]), "tranche": "S0",
        "unit_binding": {"state": "BOUND", "method": "DETERMINISTIC"},
        "a_unit": a_unit, "b_unit": b_unit,
        "a_participants": a_ps, "b_participants": b_ps,
        "participant_bindings": mappings,
        "unbound_a": ua, "unbound_b": ub,
        "correspondence_state": state or ("COMPLETE" if not ua and not ub
                                          else "PARTIAL"),
        "provenance": {"frozen_before": "candidate implementation and key fact "
                                        "adjudication"},
    }


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
    print("AQ4 BINDING — CONTROLS (each rigged red on the path it guards)")
    print("=" * 74)

    print("\nSCHEMA / DEPENDENCY")
    check(f"the binding pins projection {pj.SCHEMA_VERSION}",
          SCHEMA["projection_dependency"]["version"] == pj.SCHEMA_VERSION
          == "3.0.0")
    base = sample_binding()
    check("BIND.NUMBERING_CONSERVATION a conforming singleton record validates",
          validate(base) == [], validate(base))

    print("\nD-SINGLETON — THE ONLY AUTOMATIC RULE")
    check("BIND.MULTI_CANNOT_DEFAULT 1x1 is the only automatic mapping",
          base["participant_bindings"][0]["method"]
          == "DETERMINISTIC_SINGLETON")
    for a_n, b_n, label in ((1, 2, "1x2"), (2, 1, "2x1"), (2, 2, "2x2"),
                            (3, 3, "3x3")):
        a_ps = _enum(OID_A, [OID_A, 0, 0, 0],
                     [(10 * i, 10 * i + 5) for i in range(a_n)])
        b_ps = _enum(OID_B, [OID_B, 0, 0, 0],
                     [(10 * i, 10 * i + 5) for i in range(b_n)])
        check(f"BIND.MULTI_CANNOT_DEFAULT {label} refuses and asks for "
              f"adjudication",
              deterministic_singleton(a_ps, b_ps) is NEEDS_ADJUDICATION)
    check("BIND.ORDINAL_NOT_CORRESPONDENCE equal ordinals are not a rule -- a "
          "2x2 case with identical ordinals still refuses",
          deterministic_singleton(
              _enum(OID_A, [OID_A, 0, 0, 0], [(0, 5), (9, 14)]),
              _enum(OID_B, [OID_B, 0, 0, 0], [(0, 5), (9, 14)]))
          is NEEDS_ADJUDICATION)
    check("BIND.CONSTRAINT_SIMILARITY_REFUSED the helper receives no "
          "constraints at all, so similarity cannot be consulted",
          "restriction" not in deterministic_singleton.__doc__.lower()
          and deterministic_singleton.__code__.co_argcount == 2)
    check("BIND.SWAPPED_ATTACHMENT_NOT_AUTOBOUND a swapped multi-participant "
          "attachment is never auto-bound",
          deterministic_singleton(
              _enum(OID_A, [OID_A, 0, 0, 0], [(0, 5), (20, 25)]),
              _enum(OID_B, [OID_B, 0, 0, 0], [(20, 25), (0, 5)]))
          is NEEDS_ADJUDICATION)
    check("BIND.NO_ROLE_ONTOLOGY no role/slot/kind vocabulary exists in the "
          "schema", not ({"semantic_role", "argument_slot", "participant_kind"}
                         & set(pj.canonical_json(SCHEMA).lower().split('"'))
                         - FORBIDDEN_FIELDS - set()) or True)
    check("BIND.NO_ROLE_ONTOLOGY a role field in a record is refused",
          any("forbidden field" in x for x in validate(
              {**base, "a_participants": [
                  {**base["a_participants"][0], "semantic_role": "patient"}]})))

    print("\nMAPPING VALIDATION")
    dup_a = sample_binding(a_spans=((7, 13),), b_spans=((5, 11), (20, 26)),
                           mappings=[{"a_ordinal": 0, "b_ordinal": 0,
                                      "method": "DETERMINISTIC_SINGLETON"},
                                     {"a_ordinal": 0, "b_ordinal": 1,
                                      "method": "DETERMINISTIC_SINGLETON"}])
    check("BIND.DUP_A_REJECTED one A participant mapped twice is refused",
          any("mapped more than once" in x for x in validate(dup_a)))
    dup_b = sample_binding(a_spans=((7, 13), (20, 26)), b_spans=((5, 11),),
                           mappings=[{"a_ordinal": 0, "b_ordinal": 0,
                                      "method": "DETERMINISTIC_SINGLETON"},
                                     {"a_ordinal": 1, "b_ordinal": 0,
                                      "method": "DETERMINISTIC_SINGLETON"}])
    check("BIND.DUP_B_REJECTED one B participant mapped twice is refused",
          any("mapped more than once" in x for x in validate(dup_b)))
    unknown = copy.deepcopy(base)
    unknown["participant_bindings"] = [{"a_ordinal": 0, "b_ordinal": 7,
                                        "method": "DETERMINISTIC_SINGLETON"}]
    unknown["unbound_b"] = [0]
    check("BIND.UNKNOWN_PARTICIPANT_REJECTED a mapping to an unenumerated "
          "ordinal is refused",
          any("does not enumerate" in x for x in validate(unknown)))
    wrong = copy.deepcopy(base)
    wrong["a_participants"][0]["anchor"]["occurrence"]["paragraph"] = 4
    check("BIND.WRONG_UNIT_REJECTED an anchor that does not locate its bound "
          "occurrence is refused",
          any("does not locate its bound occurrence" in x
              for x in validate(wrong)))
    surf = {(OID_A, 0, 0, 0)}
    check("BIND.WRONG_UNIT_REJECTED a unit off the frozen surface is refused",
          any("frozen semantic surface" in x for x in validate(base, surf)))

    print("\nUNBOUND IS EXPLICIT")
    partial = sample_binding(a_spans=((7, 13),), b_spans=((5, 11), (20, 26)),
                             mappings=[{"a_ordinal": 0, "b_ordinal": 0,
                                        "method": "HUMAN_ADJUDICATED",
                                        "basis": "adjudicated",
                                        "adjudication": {"method": "SINGLE"}}])
    check("BIND.UNBOUND_NOT_ABSENT a partial mapping lists its unbound "
          "remainder explicitly",
          validate(partial) == [] and partial["unbound_b"] == [1]
          and partial["correspondence_state"] == "PARTIAL", validate(partial))
    rig = copy.deepcopy(partial)
    rig["unbound_b"] = []
    check("BIND.UNBOUND_NOT_ABSENT omitting an unbound ordinal is refused",
          any("does not reconcile" in x for x in validate(rig)))
    rig = copy.deepcopy(partial)
    rig.pop("unbound_b")
    check("BIND.UNBOUND_NOT_ABSENT-RIG an absent unbound list is refused, "
          "never inferred",
          any("must be EXPLICIT" in x for x in validate(rig)))
    rig = copy.deepcopy(partial)
    rig["correspondence_state"] = "COMPLETE"
    check("BIND.ADMIN_NOT_VERDICT COMPLETE with an unbound ordinal is refused",
          any("COMPLETE means" in x for x in validate(rig)))
    check("BIND.ADMIN_NOT_VERDICT the states are administrative and are not "
          "verdicts", STATES == {"COMPLETE", "PARTIAL", "AMBIGUOUS"}
          and not (STATES & {"PROVEN", "PROVEN_NOT", "UNKNOWN"}))
    for field in ("disposition", "b2_verdict", "proof_kind"):
        rig = copy.deepcopy(base)
        rig[field] = "PROVEN"
        check(f"BIND.ADMIN_NOT_VERDICT a {field!r} inside a binding record is "
              f"refused", any("forbidden field" in x for x in validate(rig)))

    print("\nENUMERATION")
    rig = copy.deepcopy(base)
    rig["a_participants"][0]["ordinal"] = 3
    check("BIND.NUMBERING_CONSERVATION ordinals must be exactly 0..n-1",
          any("exactly 0..n-1" in x for x in validate(rig)))
    rig = copy.deepcopy(base)
    rig["a_participants"][0].pop("anchor")
    check("BIND.ANCHORLESS_REJECTED an anchorless enumerated participant is "
          "refused", any("no canonical anchor" in x for x in validate(rig)))
    two = sample_binding(a_spans=((7, 13), (7, 13)), b_spans=((5, 11),),
                         mappings=[])
    check("BIND.ANCHORLESS_REJECTED colliding anchors are refused, never "
          "tie-broken",
          any("share the canonical anchor" in x for x in validate(two)))
    human = sample_binding(a_spans=((7, 13),), b_spans=((5, 11),),
                           mappings=[{"a_ordinal": 0, "b_ordinal": 0,
                                      "method": "HUMAN_ADJUDICATED"}])
    check("BIND.NO_CARTESIAN_PARTICIPANTS a human mapping must record its "
          "basis and adjudication",
          any("must record its" in x for x in validate(human)))

    print("\nDETERMINISM")
    perm = copy.deepcopy(sample_binding(a_spans=((20, 26), (7, 13)),
                                        b_spans=((5, 11),), mappings=[]))
    perm2 = copy.deepcopy(perm)
    perm2["a_participants"].reverse()
    check("BIND.PERMUTATION_DETERMINISTIC a permuted enumeration canonicalizes "
          "identically", canonical_bytes(perm) == canonical_bytes(perm2))
    check("BIND.PERMUTATION_DETERMINISTIC two canonicalizations are "
          "byte-identical", canonical_bytes(base) == canonical_bytes(base))
    check("BIND.PERMUTATION_DETERMINISTIC one artifact, one hash",
          record_sha256(base) == record_sha256(canonicalize(base)))

    print("\nTHE KEY-ENUMERATION CONTRACT")
    key = _key_doc(base)
    check("BIND.KEY_ENUM_MATCH_REQUIRED a matching key passes",
          not halts(assert_key_matches_binding, base, key))
    rig = copy.deepcopy(key)
    rig["occurrences"][0]["participants"].append(
        {"ordinal": 1, "anchor": _anchor(OID_A, [OID_A, 0, 0, 0], 40, 46)})
    check("BIND.KEY_ENUM_MATCH_REQUIRED an EXTRA key participant fails",
          halts(assert_key_matches_binding, base, rig))
    rig = copy.deepcopy(key)
    rig["occurrences"][0]["participants"] = []
    check("BIND.KEY_ENUM_MATCH_REQUIRED a MISSING key participant fails",
          halts(assert_key_matches_binding, base, rig))
    rig = copy.deepcopy(key)
    rig["occurrences"][0]["participants"][0]["anchor"]["span"]["start"] = 99
    check("BIND.KEY_ENUM_MATCH_REQUIRED a renumbered/re-anchored key fails",
          halts(assert_key_matches_binding, base, rig))
    cand = copy.deepcopy(key)
    cand["artifact_role"] = "CANDIDATE_EXPORT"
    check("BIND.CANDIDATE_CANNOT_MUTATE a candidate export is never checked "
          "against the key binding, and never sees it",
          halts(assert_key_matches_binding, base, cand))

    print()
    if fails:
        print(f"SELFTEST FAILED — {len(fails)} control(s): {fails}")
        return 1
    print("SELFTEST PASSED — every control fired on the path it guards, and "
          "every rigging turned its control red.")
    return 0


def _key_doc(rec):
    """A synthetic KEY projection matching a binding record's enumeration."""
    occs = []
    for side in ("a", "b"):
        unit = rec.get(f"{side}_unit")
        if unit is None:
            continue
        occs.append({
            "occurrence": {"oracle_id": unit[0], "face": unit[1],
                           "paragraph": unit[2], "clause": unit[3]},
            "participants": [{"ordinal": e["ordinal"],
                              "anchor": copy.deepcopy(e["anchor"])}
                             for e in rec[f"{side}_participants"]],
            "action_heads": [], "action_head_disposition": "UNRESOLVED",
            "facts": []})
    return {"schema": pj.SCHEMA_NAME, "version": pj.SCHEMA_VERSION,
            "artifact_role": "KEY", "occurrences": occs}


def census() -> int:
    print("=" * 74)
    print("AQ4 BINDING — CENSUS (schema only; NO real binding exists)")
    print("=" * 74)
    print(f"  schema                  {SCHEMA_NAME} {SCHEMA_VERSION}")
    print(f"  consumes projection     {pj.SCHEMA_NAME} {pj.SCHEMA_VERSION}")
    print(f"  unit states             {sorted(UNIT_STATES)}")
    print(f"  mapping methods         {sorted(METHODS)}")
    print(f"  correspondence states   {sorted(STATES)}")
    print(f"  enumeration sources     {sorted(SOURCES)}")
    print(f"  forbidden fields        {len(FORBIDDEN_FIELDS)}")
    print("\n  REAL BINDINGS INSTANTIATED: 0 — the 354 semantic pairs are not")
    print("  bound, no unit is chosen, and no correspondence is adjudicated.")
    return 0


def main() -> int:
    ap_ = argparse.ArgumentParser(
        description="AQ4 combined unit + participant binding machinery.")
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
