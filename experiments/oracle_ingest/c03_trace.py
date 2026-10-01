#!/usr/bin/env python3
"""C03b — minimal H-REGION trace renderer (V1 §5 M4). A VALIDATION TOOL ONLY.

PINNED TO oracle-compiler-interface/3 (oracle_compiler/INTERFACES.md blob
119778a68c0e4e8378f0a117b7c22884ec5eda4b, Captain ratification 5925134485 +
5925371124). The code follows h_region.py's pin (`hr.INTERFACE_VERSION`,
`hr.verify_interface()`).

Reads `c03/regions.json` and `c03/kill.json` and renders one human-readable
trace per C03 clause record (every population clause and every fixture
clause): its owning four-coordinate occurrence, its regions with spans, its
ATTACH-3 role marks with their attachment, and each K1-K7 outcome. Spans are
offsets into the frozen chain clause; the Oracle text excerpts beside them
appear only in this ignored output, never in git. The renderer decides
nothing and is never a source of truth: every figure is copied from C03, and a
C03 record it cannot read (e.g. one missing its owning occurrence) HALTS.

INTERFACE/3 §I3a R4. Each trace also carries the clause's R4 `ability-label`
label as C03 records it (offsets, class, CR citation, IGNORED or KEPT, scope
start, heads dropped) and every value R4 changed -- scope or head field,
region, role mark (with its attachment), K1-K7 outcome -- beside its
interface/2 value, copied from regions.json (`r4_label`, `r4_interface2`,
`interface2`) and kill.json (`r4_label`, `r4_off_tests`,
`interface2_changes`). An R4 record the renderer cannot account for HALTS.
`--check-complete` also asserts that every R4 label and every R4-changed value
recorded in regions.json and kill.json appears in exactly one trace.

HAND-OFF RULE. An existing C03 artifact is never trusted: `h_region.py
--verify` and `h_region_kill.py --verify` run first and a stale report HALTS.
A missing artifact is regenerated ONLY by invoking its producer unchanged
(`h_region.py`, then `h_region_kill.py`); those invocations are this script's
only effect on c03/. It never edits C03 output. `--verify` recomputes the
embedded hashes (regions.json, kill.json, this script) and also requires both
producers' own `--verify` to pass.

    python3 experiments/oracle_ingest/c03_trace.py                      # write
    python3 experiments/oracle_ingest/c03_trace.py --emit               # stdout only
    python3 experiments/oracle_ingest/c03_trace.py --check-determinism  # x2 + write
    python3 experiments/oracle_ingest/c03_trace.py --verify             # stale?
    python3 experiments/oracle_ingest/c03_trace.py --check-complete     # one per clause
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))

import h_region as hr                        # noqa: E402  (sets sys.path)
import h_region_kill as hk                   # noqa: E402
import foundry_common as fc                  # noqa: E402

SCRIPT = "experiments/oracle_ingest/c03_trace.py"
OUT_REL = "experiments/out/oracle_ingest/c03b/trace.json"
OUT = ROOT / OUT_REL
REGIONS_REL = hr.OUT_REL
KILL_REL = hk.OUT_REL
# Producers in hand-off order: (script, artifact).
PRODUCERS = ((hr.SCRIPT, REGIONS_REL), (hk.SCRIPT, KILL_REL))
OUTCOMES = (hk.PASS, hk.UNRESOLVED, hk.KILL)
COORDS = ("oracle_id", "face", "paragraph", "clause")


def _sha_at(root: Path, rel: str) -> str:
    return hashlib.sha256((root / rel).read_bytes()).hexdigest()


# ------------------------------------------------------------- hand-off rule

def _run(args: list) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable] + args, cwd=str(ROOT), capture_output=True)


def stale_producers() -> list:
    """Every C03 artifact whose unchanged producer's --verify reports stale."""
    out = []
    for script, art in PRODUCERS:
        p = _run([str(ROOT / script), "--verify"])
        if p.returncode != 0:
            out.append(f"{art} ({script} --verify): "
                       f"{p.stderr.decode('utf-8', 'replace').strip()}")
    return out


def ensure_inputs() -> None:
    """Regenerate a missing C03 artifact by its unchanged producer; then run
    every producer's --verify and halt on stale."""
    for script, art in PRODUCERS:
        if not (ROOT / art).exists():
            p = _run([str(ROOT / script)])
            if p.returncode != 0:
                sys.stderr.write(p.stderr.decode("utf-8", "replace"))
                fc.halt(f"{script} could not regenerate the missing {art}")
    stale = stale_producers()
    if stale:
        fc.halt("stale C03 input: " + "; ".join(stale))


# ------------------------------------------------------------------ rendering

def owning_occurrence(rec: dict) -> dict:
    """The record's four-coordinate owner. Halts if it is missing, incomplete,
    or disagrees with any region's owner."""
    addr = rec.get("address")
    if (not isinstance(addr, dict)
            or not isinstance(addr.get("oracle_id"), str) or not addr["oracle_id"]
            or not isinstance(addr.get("id"), str)
            or any(not isinstance(addr.get(k), int) or isinstance(addr[k], bool)
                   or addr[k] < 0 for k in COORDS[1:])):
        fc.halt(f"C03 record {addr!r} has no complete owning occurrence "
                f"({', '.join(COORDS)})")
    want = ":".join(str(addr[k]) for k in COORDS)
    if addr["id"] != want:
        fc.halt(f"C03 record {addr['id']!r}: its id is not its coordinates {want!r}")
    for r in rec.get("regions") or []:
        if r.get("owner") != addr["id"]:
            fc.halt(f"C03 record {addr['id']!r}: region {r.get('ordinal')} is owned by "
                    f"{r.get('owner')!r}, not by its occurrence")
    return {k: addr[k] for k in COORDS + ("id",)}


def _key(cid: str, ck) -> list:
    return [cid, list(ck) if ck else None]


def _excerpt(text: str, span: list) -> str:
    a, b = span
    if not (0 <= a <= b <= len(text)):
        fc.halt(f"span {span} leaves its clause [0, {len(text)})")
    return text[a:b]


def trace(rec: dict, row: dict) -> dict:
    """One trace: the C03 record `rec` and its kill.json row `row`, copied."""
    occ = owning_occurrence(rec)
    ck = rec.get("census_key")
    # Validated before any use of it: a malformed key halts with its diagnostic.
    if ck is not None and not _census_ok(ck):
        fc.halt(f"C03 record {occ['id']!r}: census key {ck!r} is malformed")
    if rec.get("population") and ck is None:
        fc.halt(f"C03 population record {occ['id']!r}: census key {ck!r} is malformed")
    key = _key(occ["id"], ck)
    if _key(row.get("id"), row.get("census_key")) != key:
        fc.halt(f"kill.json row {row.get('id')!r} {row.get('census_key')!r} does not "
                f"belong to C03 record {key}")
    text = rec["clause_text"]
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != rec["clause_sha256"]:
        fc.halt(f"C03 record {key}: clause_text does not hash to its clause_sha256")
    regions = [{"ordinal": r["ordinal"], "head": r["head"], "head_span": r["head_span"],
                "span": r["span"], "start_rule": r["start_rule"],
                "end_rule": r["end_rule"], "text": _excerpt(text, r["span"])}
               for r in rec["regions"]]
    marks = [{"role": s["role"], "span": s["span"], "rules": s["rules"],
              "outcome": s["outcome"], "attached": s["attached"],
              "attach_rule": s["rule"], "r1_shape": s.get("r1_shape"),
              "text": _excerpt(text, s["span"])}
             for s in rec["role_spans"]]
    tests = {}
    for k in hk.CONDITIONS:
        t = row["tests"].get(k)
        if not t or t.get("outcome") not in OUTCOMES:
            fc.halt(f"kill.json row {key}: {k} has no outcome")
        tests[k] = {"outcome": t["outcome"], "relevant": t["relevant"],
                    "reason": t["reason"]}
    lines = [f"clause {occ['id']}" + (f"  census {ck[0]}#{ck[1]}" if ck else "")
             + ("  [population]" if rec["population"] else "")
             + (f"  [fixtures: {', '.join(rec['fixture_roles'])}]"
                if rec["fixture_roles"] else ""),
             "  occurrence: " + "  ".join(f"{k}={occ[k]}" for k in COORDS),
             f"  scope [{rec['scope'][0]}, {rec['scope'][1]}) {rec['scope_kind']}"
             f"  clause sha256 {rec['clause_sha256']}",
             f"  source: {text}"]
    for r in regions:
        lines.append(f"  region {r['ordinal']} {r['head']}  head [{r['head_span'][0]}, "
                     f"{r['head_span'][1]})  span [{r['span'][0]}, {r['span'][1]})  "
                     f"{r['start_rule']} .. {r['end_rule']}: {r['text']}")
    if not regions:
        lines.append("  region: none derived")
    for m in marks:
        lines.append(f"  mark {m['role']} [{m['span'][0]}, {m['span'][1]})  "
                     f"{'/'.join(m['rules'])} -> {m['outcome']} {m['attached']}"
                     + (f" (R1 {m['r1_shape']}, to the ability)" if m["r1_shape"] else "")
                     + f": {m['text']}")
    for k, t in tests.items():
        lines.append(f"  {k} {t['outcome']}{'' if t['relevant'] else ' (not relevant)'}"
                     f": {t['reason']}")
    label, changed = r4_record(rec, row, key)
    if label is not None:
        lines.append(f"  R4 label [{label['span'][0]}, {label['span'][1]})  "
                     f"{label['class']} ({label['cr']}) {label['effect'].upper()}"
                     + (f"  scope from {label['scope_start']}"
                        if label["scope_start"] is not None else "")
                     + "  heads dropped: "
                     + (", ".join(f"{h}@{s}" for h, s in label["dropped_heads"]) or "none")
                     + "  R4 changed: " + (", ".join(label["r4_changed"]) or "nothing")
                     + f": {label['text']}")
    for c in changed:
        lines.append(f"  R4 changed {c['item']}: interface/2 {_fmt(c['interface2'])}"
                     f"  |  interface/3 {_fmt(c['interface3'])}")
    return {"key": key, "occurrence": occ, "population": rec["population"],
            "fixture_roles": list(rec["fixture_roles"]), "scope": rec["scope"],
            "scope_kind": rec["scope_kind"], "clause_sha256": rec["clause_sha256"],
            "regions": regions, "role_marks": marks, "tests": tests,
            "r4_label": label, "r4_changed": changed, "lines": lines}


# ------------------------------------------------------ interface/3 §I3a R4

R4_LABEL_KEYS = ("span", "text", "class", "cr", "effect", "scope_start")
# R4-changeable record fields rendered whole; regions and role marks are
# rendered one by one.
R4_FIELD_ITEMS = tuple(f for f in hr.R4_FIELDS if f not in ("regions", "role_spans"))
R4_KINDS = ("field", "region", "mark", "outcome")


def _span_label(kind: str, name: str, span: list) -> str:
    return f"{kind} {name} [{span[0]}, {span[1]})"


def _item(item: str, kind: str, was, now) -> dict:
    return {"item": item, "kind": kind, "interface2": was, "interface3": now,
            "rule": "R4"}


def _overlap(x: dict, y: dict) -> bool:
    return x["span"][0] < y["span"][1] and y["span"][0] < x["span"][1]


def r4_record(rec: dict, row: dict, key) -> tuple:
    """(label, changed) of one C03 record: its R4 label and every value R4
    changed beside its interface/2 value, copied from regions.json and
    kill.json. HALTS on an R4 record it cannot account for."""
    where = f"C03 record {key}"
    if "r4_label" not in rec or "r4_label" not in row or "r4_off_tests" not in row:
        fc.halt(f"{where} carries no interface/3 R4 record (r4_label, r4_off_tests)")
    bare = hr._bare
    lab, i2 = rec["r4_label"], rec.get("r4_interface2")
    label = None
    if lab is None:
        if row["r4_label"] is not None:
            fc.halt(f"{where}: kill.json records an R4 label regions.json does not")
    else:
        if row["r4_label"] != {k: lab[k] for k in R4_LABEL_KEYS}:
            fc.halt(f"{where}: kill.json's R4 label {row['r4_label']!r} is not "
                    f"regions.json's")
        if lab["effect"] not in ("ignored", "kept"):
            fc.halt(f"{where}: R4 label effect {lab['effect']!r} is neither ignored "
                    f"nor kept")
        if _excerpt(rec["clause_text"], lab["span"]) != lab["text"]:
            fc.halt(f"{where}: R4 label text is not its span of the clause")
        heads = [[h["head"], h["start"]] for h in lab["dropped_heads"]]
        if heads != [[h["head"], h["start"]] for h in rec["r4_dropped_heads"]]:
            fc.halt(f"{where}: R4 label's dropped heads are not the record's")
        label = dict({k: lab[k] for k in R4_LABEL_KEYS}, dropped_heads=heads,
                     r4_changed=list(i2["changed"]) if i2 else [])
    if i2 is not None and (lab is None or lab["effect"] != "ignored"):
        fc.halt(f"{where}: an interface/2 value beside a clause with no IGNORED R4 "
                f"label (R4 IS CONFINED)")
    changed = []
    if i2 is not None:
        if i2.get("rule") != "R4":
            fc.halt(f"{where}: r4_interface2 rule is {i2.get('rule')!r}, not R4")
        for f in R4_FIELD_ITEMS:
            if (f in i2["changed"]) != (bare(i2[f]) != bare(rec[f])):
                fc.halt(f"{where}: R4's changed list disagrees with {f}")
            if f in i2["changed"]:
                changed.append(_item(f, "field", bare(i2[f]), bare(rec[f])))
        changed += _r4_regions(rec, i2, where) + _r4_marks(rec, i2, where)
        for f, kind in (("regions", "region"), ("role_spans", "mark")):
            if (f in i2["changed"]) != any(c["kind"] == kind for c in changed):
                fc.halt(f"{where}: R4's changed list disagrees with its {f} records")
    for k in hk.CONDITIONS:
        now, was = row["tests"][k], row["r4_off_tests"][k]
        ch = (row.get("interface2_changes") or {}).get(k)
        moved = (now["outcome"], now["relevant"]) != (was["outcome"], was["relevant"])
        want = {"interface2": was["outcome"], "interface2_relevant": was["relevant"],
                "interface3": now["outcome"], "interface3_relevant": now["relevant"],
                "changed_by": ["R4"]}
        if moved != (ch is not None) or (ch is not None and ch != want):
            fc.halt(f"{where}: kill.json's {k} R4 record disagrees with its R4-off "
                    f"outcome")
        if ch is not None:
            if label is None or label["effect"] != "ignored":
                fc.halt(f"{where}: R4 changed {k} on a clause with no IGNORED label "
                        f"(R4 IS CONFINED)")
            changed.append(_item(k, "outcome",
                                 {"outcome": was["outcome"], "relevant": was["relevant"]},
                                 {"outcome": now["outcome"], "relevant": now["relevant"]}))
    return label, changed


def _r4_regions(rec: dict, i2: dict, where: str) -> list:
    bare, off, out = hr._bare, i2["regions"], []
    for r in rec["regions"]:
        if "interface2" in r:
            if r["interface2"].get("changed_by") != ["R4"]:
                fc.halt(f"{where}: region {r['ordinal']} interface/2 value is not R4's")
            was = r["interface2"]["region"]
            out.append(_item(_span_label("region", r["head"], r["head_span"]), "region",
                             None if was is None else bare(was), bare(r)))
        elif not any(bare(x) == bare(r) for x in off):
            fc.halt(f"{where}: region {r['ordinal']} differs from interface/2 but "
                    f"carries no interface/2 value")
    for x in off:
        if all(x["head_span"] != r["head_span"] for r in rec["regions"]):
            out.append(_item(_span_label("region", x["head"], x["head_span"]), "region",
                             bare(x), None))
    return out


def _r4_marks(rec: dict, i2: dict, where: str) -> list:
    bare, off, on, out, was_of = hr._bare, i2["role_spans"], rec["role_spans"], [], []
    for s in on:
        if "interface2" in s:
            if s["interface2"].get("changed_by") != ["R4"]:
                fc.halt(f"{where}: role mark {s['role']} {s['span']} interface/2 value "
                        f"is not R4's")
            was = s["interface2"]["span"]
            if was is not None:
                was_of.append(bare(was))
            out.append(_item(_span_label("mark", s["role"], s["span"]), "mark",
                             None if was is None else bare(was), bare(s)))
        elif not any(bare(x) == bare(s) for x in off):
            fc.halt(f"{where}: role mark {s['role']} {s['span']} differs from "
                    f"interface/2 but carries no interface/2 value")
    for x in off:
        if any(bare(x) == bare(s) for s in on) or bare(x) in was_of:
            continue
        if any(x["role"] == s["role"] and _overlap(x, s) for s in on):
            fc.halt(f"{where}: interface/2 role mark {x['role']} {x['span']} changed "
                    f"under R4 but no interface/3 mark records it")
        out.append(_item(_span_label("mark", x["role"], x["span"]), "mark", bare(x), None))
    return out


def _fmt(v) -> str:
    """One R4 value, as a trace line shows it."""
    if v is None:
        return "none"
    if isinstance(v, dict) and "head_span" in v:
        return (f"region {v['ordinal']} {v['head']}  head [{v['head_span'][0]}, "
                f"{v['head_span'][1]})  span [{v['span'][0]}, {v['span'][1]})  "
                f"{v['start_rule']} .. {v['end_rule']}")
    if isinstance(v, dict) and "role" in v:
        return (f"{v['role']} [{v['span'][0]}, {v['span'][1]})  "
                f"{'/'.join(v.get('rules') or [])} -> {v['outcome']} {v['attached']}"
                + (f" ({v['rule']})" if v.get("rule") else "")
                + (f" (R1 {v['r1_shape']}, to the ability)" if v.get("r1_shape") else ""))
    if isinstance(v, dict) and "outcome" in v:
        return v["outcome"] + ("" if v["relevant"] else " (not relevant)")
    return json.dumps(v, sort_keys=True, ensure_ascii=True)


def _census_ok(ck) -> bool:
    return (isinstance(ck, list) and len(ck) == 2 and isinstance(ck[0], str)
            and isinstance(ck[1], int) and not isinstance(ck[1], bool))


def _identity(m: dict) -> list:
    """A fixture member's identity: the card, its census key, and (for an
    unresolved member) the name as recorded."""
    return [m.get("oracle_id"), m.get("census_key"), m.get("name_as_recorded")]


def expected_fixtures(regions_doc: dict) -> tuple:
    """(expected, problems): for every C03 fixture, its role and, per member,
    the member's identity and the exact trace key of each of its clauses,
    derived from C03 alone. A member clause owns exactly one C03 record that
    carries the fixture's role, belongs to the member's card, and is keyed by
    the member's census key or by none."""
    problems, expected = [], []
    by_id = {}
    for c in regions_doc["clauses"]:
        by_id.setdefault(c["address"]["id"], []).append(c)
    roles = [f["role"] for f in regions_doc["fixtures"]]
    for r in sorted(set(roles)):
        if roles.count(r) != 1:
            problems.append(f"C03 lists fixture {r} {roles.count(r)} times")
    for f in regions_doc["fixtures"]:
        members = []
        for m in f["members"]:
            keys = []
            for cid in m["clauses"]:
                hit = [c for c in by_id.get(cid, []) if f["role"] in c["fixture_roles"]]
                if len(hit) != 1:
                    problems.append(f"fixture {f['role']}: clause {cid} has {len(hit)} "
                                    f"C03 records carrying the role")
                    continue
                c = hit[0]
                if c["address"]["oracle_id"] != m["oracle_id"]:
                    problems.append(f"fixture {f['role']}: clause {cid} is not of member "
                                    f"{m['oracle_id']}")
                if c.get("census_key") not in (None, m["census_key"]):
                    problems.append(f"fixture {f['role']}: clause {cid} is keyed "
                                    f"{c['census_key']}, not by member key "
                                    f"{m['census_key']}")
                keys.append(_key(cid, c.get("census_key")))
            members.append({"identity": _identity(m), "keys": keys})
        expected.append({"role": f["role"], "members": members})
    return expected, problems


def render_traces(regions_doc: dict, kill_doc: dict) -> dict:
    recs, rows = regions_doc["clauses"], kill_doc["clauses"]
    if len(recs) != len(rows):
        fc.halt(f"regions.json has {len(recs)} clauses, kill.json {len(rows)}")
    traces = []
    for n, (rec, row) in enumerate(zip(recs, rows)):
        try:
            traces.append(trace(rec, row))
        except (KeyError, TypeError, ValueError, AttributeError, IndexError) as e:
            fc.halt(f"C03 record {n} cannot be read: {type(e).__name__} {e}")
    expected, problems = expected_fixtures(regions_doc)
    if problems:
        fc.halt("C03 fixtures cannot be traced: " + "; ".join(problems))
    fixtures = []
    for f, ef in zip(regions_doc["fixtures"], expected):
        members = [{"oracle_id": m["oracle_id"], "census_key": m["census_key"],
                    "name_as_recorded": m.get("name_as_recorded"),
                    "unresolved": m.get("unresolved"), "traces": em["keys"]}
                   for m, em in zip(f["members"], ef["members"])]
        fixtures.append({"role": f["role"], "member_status": f["member_status"],
                         "members": members})
    return {"traces": traces, "fixtures": fixtures,
            "population_keys": regions_doc["population_keys"]}


# ------------------------------------------------------------- completeness

def outcome_counts(traces: list) -> dict:
    out = {}
    for k in hk.CONDITIONS:
        allc = {o: 0 for o in OUTCOMES}
        relc = {o: 0 for o in OUTCOMES}
        for t in traces:
            o = t["tests"][k]["outcome"]
            allc[o] += 1
            if t["fixture_roles"] or t["tests"][k]["relevant"]:
                relc[o] += 1
        out[k] = {"all": allc, "relevant": relc}
    return out


def _trace_key(t) -> tuple:
    """(json key, problems) of one trace; the key is None when it is malformed
    (unreadable, or a population trace whose census key is null)."""
    k = t.get("key") if isinstance(t, dict) else None
    if (not isinstance(k, list) or len(k) != 2 or not isinstance(k[0], str)
            or not (k[1] is None or _census_ok(k[1]))):
        return None, [f"trace {k!r} has a malformed key"]
    if t.get("population") and k[1] is None:
        return None, [f"population trace {k[0]!r} is malformed: its census key is null"]
    occ = t.get("occurrence")
    if not isinstance(occ, dict) or occ.get("id") != k[0]:
        return json.dumps(k), [f"trace {json.dumps(k)} is not keyed by its owning "
                               f"occurrence"]
    return json.dumps(k), []


def completeness_failures(doc: dict, regions_doc: dict, kill_doc: dict) -> list:
    """Exactly one trace per C03 clause and fixture clause, exact fixture
    coverage (each fixture once, each member's identity and its expected trace
    keys, nothing else), and per-outcome counts recomputed from the traces
    equal to kill.json's. Never raises on a malformed trace.json: it reports."""
    try:
        return _completeness_failures(doc, regions_doc, kill_doc)
    except (KeyError, TypeError, ValueError, AttributeError, IndexError) as e:
        return [f"trace.json is malformed: {type(e).__name__} {e}"]


def _completeness_failures(doc: dict, regions_doc: dict, kill_doc: dict) -> list:
    bad = []
    traces = {}                                    # json key -> trace
    keys = []
    listed = []                                    # (json key, trace), duplicates kept
    for t in doc["traces"]:
        k, problems = _trace_key(t)
        bad += problems
        if k is None:
            continue
        keys.append(k)
        traces[k] = t
        listed.append((k, t))
    recs = {json.dumps(_key(c["address"]["id"], c.get("census_key"))): c
            for c in regions_doc["clauses"] if c["population"] or c["fixture_roles"]}
    for k in sorted(set(keys)):
        if keys.count(k) != 1:
            bad.append(f"{keys.count(k)} traces for {k}")
    for k in sorted(set(recs) - set(keys)):
        bad.append(f"no trace for C03 clause {k}")
    for k in sorted(set(keys) - set(recs)):
        bad.append(f"trace {k} is not a C03 clause")
    for k in sorted(set(keys) & set(recs)):
        t, c = traces[k], recs[k]
        if bool(t.get("population")) != bool(c["population"]):
            bad.append(f"trace {k}: population {t.get('population')!r}, C03 "
                       f"{c['population']!r}")
        if t.get("fixture_roles") != c["fixture_roles"]:
            bad.append(f"trace {k}: fixture roles {t.get('fixture_roles')!r}, C03 "
                       f"{c['fixture_roles']!r}")
    pop = [[traces[k]["occurrence"]["oracle_id"]] + json.loads(k)[1] for k in keys
           if traces[k].get("population")]
    for row in regions_doc["population_keys"]:
        if pop.count(row) != 1:
            bad.append(f"{pop.count(row)} population traces for census row {row}")

    expected, problems = expected_fixtures(regions_doc)
    bad += [f"C03: {p}" for p in problems]
    got_roles = [f.get("role") for f in doc["fixtures"]]
    for r in sorted(set(got_roles), key=repr):
        if got_roles.count(r) != 1:
            bad.append(f"{got_roles.count(r)} trace entries for fixture {r!r}")
    want_roles = {ef["role"] for ef in expected}
    for r in sorted(set(got_roles) - want_roles, key=repr):
        bad.append(f"trace entry for fixture {r!r} is not a C03 fixture")
    by_role = {f.get("role"): f for f in doc["fixtures"]}
    referenced = {}                                # json key -> roles referencing it
    for ef in expected:
        role = ef["role"]
        got = by_role.get(role)
        if got is None:
            bad.append(f"no trace entry for fixture {role}")
            continue
        gms = got["members"]
        if len(gms) != len(ef["members"]):
            bad.append(f"fixture {role}: {len(gms)} members traced of "
                       f"{len(ef['members'])}")
        ids = [json.dumps(_identity(gm)) for gm in gms]
        for i in sorted(set(ids)):
            if ids.count(i) != 1:
                bad.append(f"fixture {role}: member {i} is entered {ids.count(i)} times")
        for n, (em, gm) in enumerate(zip(ef["members"], gms)):
            if _identity(gm) != em["identity"]:
                bad.append(f"fixture {role} member {n}: identity {_identity(gm)}, "
                           f"C03 {em['identity']}")
            got_keys = [json.dumps(k) for k in gm["traces"]]
            want_keys = [json.dumps(k) for k in em["keys"]]
            for k in sorted(set(got_keys)):
                if got_keys.count(k) != 1:
                    bad.append(f"fixture {role} member {n}: trace {k} is entered "
                               f"{got_keys.count(k)} times")
            for k in sorted(set(got_keys) - set(want_keys)):
                bad.append(f"fixture {role} member {n}: trace {k} is not one of the "
                           f"member's clauses")
            for k in sorted(set(want_keys) - set(got_keys)):
                bad.append(f"fixture {role} member {n}: expected trace {k} is absent")
            if got_keys != want_keys and sorted(got_keys) == sorted(want_keys):
                bad.append(f"fixture {role} member {n}: traces are out of C03 order")
        for gm in gms:
            for k in gm["traces"]:
                k = json.dumps(k)
                referenced.setdefault(k, set()).add(role)
                if k not in traces:
                    bad.append(f"fixture {role}: trace {k} is missing")
                elif role not in (traces[k].get("fixture_roles") or []):
                    bad.append(f"fixture {role}: trace {k} does not carry the role")
    for k in sorted(traces):
        for role in traces[k].get("fixture_roles") or []:
            if role in want_roles and role not in referenced.get(k, set()):
                bad.append(f"trace {k} carries fixture {role} but no member of it "
                           f"references the trace")
    counts = outcome_counts([traces[k] for k in keys])
    for k in hk.CONDITIONS:
        cond = kill_doc["conditions"][k]
        for o in OUTCOMES:
            for view in ("all", "relevant"):
                if counts[k][view][o] != cond[view][o]["count"]:
                    bad.append(f"{k} {view} {o}: traces count {counts[k][view][o]}, "
                               f"kill.json {cond[view][o]['count']}")
    return bad + r4_failures(listed, regions_doc, kill_doc)


def _tally(sigs) -> dict:
    out = {}
    for s in sigs:
        s = json.dumps(s, sort_keys=True, ensure_ascii=True)
        out[s] = out.get(s, 0) + 1
    return out


def _exactly_once(what: str, src: str, recorded: list, traced: list) -> list:
    """Every R4 entry recorded in `src` appears in exactly one trace (as often
    as `src` records it), and no trace carries one `src` does not record."""
    want, got = _tally(recorded), _tally(traced)
    return [f"R4 {what} {s} is recorded {want.get(s, 0)} time(s) in {src} but appears "
            f"in {got.get(s, 0)} trace(s)"
            for s in sorted(set(want) | set(got)) if want.get(s, 0) != got.get(s, 0)]


def r4_failures(listed: list, regions_doc: dict, kill_doc: dict) -> list:
    """interface/3 §I3a R4: every R4 label and every R4-changed value recorded
    in regions.json (its records and its R4 measurement) and in kill.json (its
    rows and its changed_from_interface2 rows) appears in exactly one trace,
    and each trace's R4 label and changed values are its C03 record's."""
    bad = []
    try:
        summary = regions_doc["measurements"]["all"]["interface3_rules"][
            "R4_ability_label"]
        s_labels, s_changed = summary["labels"], summary["changed_from_interface2"]
        k_rows = kill_doc["changed_from_interface2"]["rows"]
    except (KeyError, TypeError):
        return ["C03 carries no interface/3 R4 record (regions.json measurements.all."
                "interface3_rules.R4_ability_label, kill.json changed_from_interface2)"]
    for k, t in listed:
        for f in ("r4_label", "r4_changed"):
            if f not in t:
                bad.append(f"trace {k} carries no {f}")
    listed = [(k, t) for k, t in listed if "r4_label" in t and "r4_changed" in t]

    # Per trace: its R4 label and changed values are exactly its record's.
    rows = {json.dumps(_key(r["id"], r.get("census_key"))): r for r in kill_doc["clauses"]}
    recs = {json.dumps(_key(c["address"]["id"], c.get("census_key"))): c
            for c in regions_doc["clauses"]}
    for k, t in listed:
        if k in recs and k in rows:
            label, changed = r4_record(recs[k], rows[k], json.loads(k))
            if t["r4_label"] != label:
                bad.append(f"trace {k}: R4 label {t['r4_label']!r}, C03 {label!r}")
            if t["r4_changed"] != changed:
                bad.append(f"trace {k}: R4 changed values differ from C03's")

    # Exactly one trace per recorded label (regions.json by clause, kill.json by key).
    lab_keys = ("span", "text", "class", "cr", "effect", "scope_start", "dropped_heads",
                "r4_changed")
    bad += _exactly_once(
        "label", "regions.json",
        [[e["clause"]] + [e[x] for x in lab_keys] for e in s_labels],
        [[json.loads(k)[0]] + [t["r4_label"][x] for x in lab_keys]
         for k, t in listed if t["r4_label"] is not None])
    bad += _exactly_once(
        "label", "kill.json",
        [[json.loads(k), r["r4_label"]] for k, r in rows.items()
         if r.get("r4_label") is not None],
        [[json.loads(k), {x: t["r4_label"][x] for x in R4_LABEL_KEYS}]
         for k, t in listed if t["r4_label"] is not None])

    # Exactly one trace per R4-changed value regions.json records.
    want, got = [], []
    for e in s_changed:
        c = e["clause"]
        want += [[c, "field", f] for f in e["changed"] if f in R4_FIELD_ITEMS]
        want += [[c, "region", r["head"], r["span"], r["interface2"]] for r in e["regions"]]
        want += [[c, "region gone", r["head"], r["span"]]
                 for r in e["interface2_regions_dropped"]]
        want += [[c, "mark", s["role"], s["span"], s["outcome"], s["r1_shape"],
                  s["interface2"]] for s in e["role_spans"]]
        want += [[c, "mark gone", s["role"], s["span"], s["outcome"]]
                 for s in e["interface2_role_spans_gone"]]
    for k, t in listed:
        c = json.loads(k)[0]
        for i in t["r4_changed"]:
            was, now = i.get("interface2"), i.get("interface3")
            if i.get("kind") == "field":
                got.append([c, "field", i["item"]])
            elif i.get("kind") == "region":
                got.append([c, "region", now["head"], now["span"],
                            {"region": was, "changed_by": ["R4"]}] if now is not None
                           else [c, "region gone", was["head"], was["span"]])
            elif i.get("kind") == "mark":
                got.append([c, "mark", now["role"], now["span"], now["outcome"],
                            now.get("r1_shape"), {"span": was, "changed_by": ["R4"]}]
                           if now is not None
                           else [c, "mark gone", was["role"], was["span"], was["outcome"]])
            elif i.get("kind") != "outcome":
                bad.append(f"trace {k}: R4 changed item {i.get('item')!r} has no kind "
                           f"of {R4_KINDS}")
    bad += _exactly_once("changed value", "regions.json", want, got)

    # Exactly one trace per R4-changed outcome kill.json records.
    bad += _exactly_once(
        "changed outcome", "kill.json",
        [[[r[0], r[1]], r[2], r[3], r[4], r[6], r[7]] for r in k_rows],
        [[json.loads(k), i["item"], i["interface2"]["outcome"],
          i["interface3"]["outcome"], i["interface2"]["relevant"],
          i["interface3"]["relevant"]]
         for k, t in listed for i in t["r4_changed"] if i.get("kind") == "outcome"])
    return bad


# ----------------------------------------------------------------- staleness

def stale_inputs(doc: dict, root: Path = None) -> list:
    """Every embedded hash (regions.json, kill.json, this script) that no
    longer matches the file under `root` (the repository by default)."""
    root = ROOT if root is None else root
    embedded = dict(doc.get("inputs") or {})
    embedded[SCRIPT] = (doc.get("script") or {}).get("sha256")
    out = [rel for rel, want in sorted(embedded.items())
           if not (root / rel).exists() or _sha_at(root, rel) != want]
    out += [f"{rel} is not embedded" for rel in (REGIONS_REL, KILL_REL)
            if rel not in (doc.get("inputs") or {})]
    return out


# ---------------------------------------------------------- negative controls

def _halts(fn, needle: str = "") -> bool:
    """True if `fn` halts (SystemExit) and its diagnostic contains `needle`."""
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            fn()
    except SystemExit:
        return needle in err.getvalue()
    return False


def rig_docs(records: list, population_keys: list, fixtures: list, names: list) -> tuple:
    """(regions_doc, kill_doc) over inline synthetic records, with the R4
    records the producers write: regions.json's R4 measurement, and kill.json's
    R4-off outcomes, R4 labels and interface/2 changes."""
    regions_doc = {"clauses": records, "population_keys": population_keys,
                   "fixtures": fixtures,
                   "measurements": {"all": {"interface3_rules": {
                       "R4_ability_label": hr.r4_measure(records)}}}}
    kill_doc = hk.evaluate(records, list(hr.RULES), names)
    off = hk.evaluate([hk.r4_off_view(c) for c in records], list(hr.RULES), names)
    kill_doc["changed_from_interface2"] = {
        "rows": hk.r4_changes(records, kill_doc["clauses"], off["clauses"])}
    return regions_doc, kill_doc


# Synthetic R4 clause: an IGNORED flavor label before a trigger whose
# intervening 'if' R1 attaches to the ability once R4 moves the scope start.
RIG_R4 = ("Rig Drill — When this widget enters, if you control an artifact, exile "
          "target artifact, then return it to the battlefield.")


def rig_paragraph(text: str, pi: int, census=None, population=False, roles=()) -> dict:
    """hk._rig's synthetic record, opening paragraph `pi` (chain clause 0: the
    only clause R4 locates a label in)."""
    c = hr.clause_record("rig", 0, pi, 0, text, 0, len(text.rstrip(" .")), "rig")
    c.update(census_key=list(census) if census else None, population=population,
             fixture_roles=sorted(roles))
    return c


def synthetic() -> tuple:
    """(regions_doc, kill_doc) over three inline synthetic clauses, one of them
    behind an IGNORED R4 label that changes a role mark and a K4 outcome."""
    a = hk._rig("Exile target artifact you control, then return that card to the "
                "battlefield.", census=("exile", 0), population=True)
    b = hk._rig("Destroy target artifact, then proliferate.", roles=["rig-role"], ci=1)
    c = rig_paragraph(RIG_R4, 1, census=("exile", 1), population=True)
    return rig_docs([a, b, c], [["rig", "exile", 0], ["rig", "exile", 1]],
                    [{"role": "rig-role", "member_status": "rig",
                      "members": [{"oracle_id": "rig", "census_key": None,
                                   "clauses": [b["address"]["id"]]}]}], ["Rig Widget"])


def negative_controls() -> list:
    regions_doc, kill_doc = synthetic()
    clean = render_traces(regions_doc, kill_doc)
    r4_trace = next(t for t in clean["traces"] if t["r4_label"] is not None)
    r4_i = clean["traces"].index(r4_trace)
    no_label = copy.deepcopy(clean)
    no_label["traces"][r4_i]["r4_label"] = None
    no_outcome = copy.deepcopy(clean)
    ch = no_outcome["traces"][r4_i]["r4_changed"]
    ch.remove(next(i for i in ch if i["kind"] == "outcome"))
    no_addr = copy.deepcopy(regions_doc)
    del no_addr["clauses"][0]["address"]
    no_coord = copy.deepcopy(regions_doc)
    del no_coord["clauses"][1]["address"]["paragraph"]
    dropped = copy.deepcopy(clean)
    dropped["traces"].pop()
    mismatch = copy.deepcopy(clean)
    t = mismatch["traces"][0]["tests"]["K1"]
    t["outcome"] = hk.KILL if t["outcome"] != hk.KILL else hk.PASS
    pop_key = clean["traces"][0]["key"]              # the population trace
    unrelated = copy.deepcopy(clean)                 # a real trace, wrong member
    unrelated["fixtures"][0]["members"][0]["traces"] = [pop_key]
    wrong_id = copy.deepcopy(clean)
    wrong_id["fixtures"][0]["members"][0]["oracle_id"] = "not-rig"
    dup_role = copy.deepcopy(clean)
    dup_role["fixtures"].append(copy.deepcopy(dup_role["fixtures"][0]))
    dup_member = copy.deepcopy(clean)
    ms = dup_member["fixtures"][0]["members"]
    ms.append(copy.deepcopy(ms[0]))
    dup_key = copy.deepcopy(clean)
    tk = dup_key["fixtures"][0]["members"][0]["traces"]
    tk.append(copy.deepcopy(tk[0]))
    null_ck = copy.deepcopy(clean)
    null_ck["traces"][0]["key"][1] = None
    null_rec = copy.deepcopy(regions_doc)
    null_rec["clauses"][0]["census_key"] = None
    null_row = copy.deepcopy(kill_doc)               # so only the null key differs
    null_row["clauses"][0]["census_key"] = None
    short_rec = copy.deepcopy(regions_doc)           # ["exile"]: once an IndexError
    short_rec["clauses"][0]["census_key"] = ["exile"]
    short_row = copy.deepcopy(kill_doc)
    short_row["clauses"][0]["census_key"] = ["exile"]

    def fails(doc, needle) -> bool:
        return any(needle in b for b in completeness_failures(doc, regions_doc, kill_doc))

    def stale_kill() -> bool:
        """verify() itself, on a temporary root: current, then stale on kill.json."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for rel, body in ((REGIONS_REL, b"{}\n"), (KILL_REL, b"{}\n"),
                              (SCRIPT, b"# rig\n")):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_bytes(body)
            doc = {"inputs": {r: _sha_at(root, r) for r in (REGIONS_REL, KILL_REL)},
                   "script": {"path": SCRIPT, "sha256": _sha_at(root, SCRIPT)}}
            (root / OUT_REL).parent.mkdir(parents=True, exist_ok=True)
            (root / OUT_REL).write_text(json.dumps(doc), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()) as err:
                fresh = verify(root)
                (root / KILL_REL).write_bytes(b'{"rigged": true}\n')
                rigged = verify(root)
            return (fresh == 0 and rigged == 1
                    and err.getvalue().splitlines() == [f"STALE: {KILL_REL}"])

    cases = [
        ("a C03 record missing its owning occurrence halts the renderer",
         lambda: _halts(lambda: render_traces(no_addr, kill_doc))
         and _halts(lambda: render_traces(no_coord, kill_doc))
         and not _halts(lambda: render_traces(regions_doc, kill_doc))),
        ("--check-complete fails on a rigged dropped trace",
         lambda: not completeness_failures(clean, regions_doc, kill_doc)
         and bool(completeness_failures(dropped, regions_doc, kill_doc))),
        ("--check-complete fails on a rigged outcome mismatch",
         lambda: bool(completeness_failures(mismatch, regions_doc, kill_doc))),
        ("--check-complete fails on a fixture member pointing at an unrelated trace",
         lambda: fails(unrelated, "is not one of the member's clauses")),
        ("--check-complete fails on an incorrect fixture member identity",
         lambda: fails(wrong_id, "identity")),
        ("--check-complete fails on a duplicate fixture role",
         lambda: fails(dup_role, "2 trace entries for fixture 'rig-role'")),
        ("--check-complete fails on a duplicate fixture member entry",
         lambda: fails(dup_member, "is entered 2 times")),
        ("--check-complete fails on a duplicate fixture trace entry",
         lambda: fails(dup_key, "is entered 2 times")),
        ("--check-complete reports a null population census key as malformed",
         lambda: fails(null_ck, "is malformed: its census key is null")),
        ("a C03 population record with a null census key halts the renderer",
         lambda: _halts(lambda: render_traces(null_rec, null_row), "is malformed")),
        ("a C03 record with a malformed census key halts the renderer with its "
         "diagnostic",
         lambda: _halts(lambda: render_traces(short_rec, short_row),
                        "census key ['exile'] is malformed")
         and _halts(lambda: trace(short_rec["clauses"][0], short_row["clauses"][0]),
                    "census key ['exile'] is malformed")),
        ("--verify fails on a rigged stale kill.json", stale_kill),
        ("--check-complete fails on a rigged trace that drops one R4 label",
         lambda: r4_trace["r4_label"]["effect"] == "ignored"
         and fails(no_label, "R4 label")),
        ("--check-complete fails on a rigged trace that drops an R4-changed outcome",
         lambda: any(i["kind"] == "outcome" for i in r4_trace["r4_changed"])
         and fails(no_outcome, "R4 changed outcome")),
        ("a rigged output containing the absolute repository root fails "
         "--check-determinism",
         lambda: bool(hr.portability_violations(b'"' + str(ROOT).encode() + b'"'))),
    ]
    out = []
    for name, check in cases:
        if not check():
            fc.halt(f"negative control failed: {name}")
        out.append(name)
    return out


# --------------------------------------------------------------------- build

def build() -> dict:
    blob = hr.verify_interface()
    ensure_inputs()
    regions_doc = json.loads((ROOT / REGIONS_REL).read_text(encoding="utf-8"))
    kill_doc = json.loads((ROOT / KILL_REL).read_text(encoding="utf-8"))
    for label, d in (("regions.json", regions_doc), ("kill.json", kill_doc)):
        if d["interface"]["version"] != hr.INTERFACE_VERSION or d["interface"]["blob"] != blob:
            fc.halt(f"{label} was derived under {d['interface']}, not "
                    f"{hr.INTERFACE_VERSION} ({blob})")
    if kill_doc["regions"]["sha256"] != _sha_at(ROOT, REGIONS_REL):
        fc.halt("kill.json was not derived from the current regions.json")
    body = render_traces(regions_doc, kill_doc)
    return {
        "schema": "oracle-compiler-c03b-trace/0",
        "interface": {"version": hr.INTERFACE_VERSION, "blob": blob},
        "note": "validation tool only (V1 §5 M4): every figure is copied from C03; "
                "spans are offsets into the chain clause; text excerpts are Oracle "
                "text and live only in this ignored output",
        "inputs": {rel: _sha_at(ROOT, rel) for rel in (REGIONS_REL, KILL_REL)},
        "script": {"path": SCRIPT, "sha256": _sha_at(ROOT, SCRIPT)},
        "negative_controls": negative_controls(),
        "outcome_counts": outcome_counts(body["traces"]),
        **body,
    }


def render(report: dict) -> bytes:
    return (json.dumps(report, indent=1, sort_keys=True, ensure_ascii=True)
            + "\n").encode("utf-8")


# ----------------------------------------------------------------------- CLI

def verify(root: Path = None) -> int:
    """Recompute trace.json's embedded hashes under `root`. On the repository
    itself the C03 producers' own --verify must also pass, as kill.json's
    --verify chains to regions.json's: a byte-identical input can still be
    stale against its own inputs."""
    out = OUT if root is None else root / OUT_REL
    if not out.exists():
        print(f"STALE: {OUT_REL} does not exist", file=sys.stderr)
        return 1
    stale = stale_inputs(json.loads(out.read_text(encoding="utf-8")), root)
    if root is None:
        stale += stale_producers()
    for rel in stale:
        print(f"STALE: {rel}", file=sys.stderr)
    if stale:
        return 1
    print(f"{OUT_REL}: regions.json, kill.json, this script and the C03 producers' "
          f"--verify are current" if root is None else
          f"{OUT_REL}: regions.json, kill.json and this script are current")
    return 0


def check_determinism() -> int:
    runs = []
    for _ in range(2):
        p = _run([str(HERE), "--emit"])
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


def check_complete() -> int:
    # Hand-off order: the C03 inputs first (regenerated only if missing, then
    # their producers' --verify), then this script's own output.
    ensure_inputs()
    if not OUT.exists():
        rc = main([])
        if rc:
            return rc
    elif verify() != 0:
        fc.halt(f"{OUT_REL} is stale (c03_trace.py --verify)")
    doc = json.loads(OUT.read_text(encoding="utf-8"))
    regions_doc = json.loads((ROOT / REGIONS_REL).read_text(encoding="utf-8"))
    kill_doc = json.loads((ROOT / KILL_REL).read_text(encoding="utf-8"))
    bad = completeness_failures(doc, regions_doc, kill_doc)
    for b in bad:
        print(f"INCOMPLETE: {b}", file=sys.stderr)
    if bad:
        return 1
    print(f"{OUT_REL}: {len(doc['traces'])} traces, one per C03 clause; "
          f"{len(doc['fixtures'])} fixtures; per-outcome counts equal kill.json's; "
          f"{sum(t['r4_label'] is not None for t in doc['traces'])} R4 labels and "
          f"{sum(len(t['r4_changed']) for t in doc['traces'])} R4-changed values, "
          f"each in exactly one trace")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--emit", action="store_true", help="write the report to stdout only")
    g.add_argument("--check-determinism", action="store_true")
    g.add_argument("--verify", action="store_true")
    g.add_argument("--check-complete", action="store_true")
    a = ap.parse_args(argv)
    if a.verify:
        return verify()
    if a.check_determinism:
        return check_determinism()
    if a.check_complete:
        return check_complete()
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
