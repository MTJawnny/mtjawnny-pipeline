#!/usr/bin/env python3
"""C03b — minimal H-REGION trace renderer (V1 §5 M4). A VALIDATION TOOL ONLY.

PINNED TO oracle-compiler-interface/2 (oracle_compiler/INTERFACES.md blob
4ac4d856b651edde05b15c7065aa593f59561dcf, Captain ratification 5900431196).

Reads `c03/regions.json` and `c03/kill.json` and renders one human-readable
trace per C03 clause record (every population clause and every fixture
clause): its owning four-coordinate occurrence, its regions with spans, its
ATTACH-3 role marks with their attachment, and each K1-K7 outcome. Spans are
offsets into the frozen chain clause; the Oracle text excerpts beside them
appear only in this ignored output, never in git. The renderer decides
nothing and is never a source of truth: every figure is copied from C03, and a
C03 record it cannot read (e.g. one missing its owning occurrence) HALTS.

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
    key = _key(occ["id"], rec.get("census_key"))
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
    ck = rec.get("census_key")
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
    return {"key": key, "occurrence": occ, "population": rec["population"],
            "fixture_roles": list(rec["fixture_roles"]), "scope": rec["scope"],
            "scope_kind": rec["scope_kind"], "clause_sha256": rec["clause_sha256"],
            "regions": regions, "role_marks": marks, "tests": tests, "lines": lines}


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
        except (KeyError, TypeError, ValueError, AttributeError) as e:
            fc.halt(f"C03 record {n} cannot be read: {type(e).__name__} {e}")
        ck = rec.get("census_key")
        if rec["population"] and not _census_ok(ck):
            fc.halt(f"C03 population record {rec['address']['id']!r}: census key "
                    f"{ck!r} is malformed")
        if ck is not None and not _census_ok(ck):
            fc.halt(f"C03 record {rec['address']['id']!r}: census key {ck!r} is malformed")
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
    for t in doc["traces"]:
        k, problems = _trace_key(t)
        bad += problems
        if k is None:
            continue
        keys.append(k)
        traces[k] = t
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

def _halts(fn) -> bool:
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            fn()
    except SystemExit:
        return True
    return False


def synthetic() -> tuple:
    """(regions_doc, kill_doc) over two inline synthetic clauses."""
    a = hk._rig("Exile target artifact you control, then return that card to the "
                "battlefield.", census=("exile", 0), population=True)
    b = hk._rig("Destroy target artifact, then proliferate.", roles=["rig-role"], ci=1)
    regions_doc = {"clauses": [a, b], "population_keys": [["rig", "exile", 0]],
                   "fixtures": [{"role": "rig-role", "member_status": "rig",
                                 "members": [{"oracle_id": "rig", "census_key": None,
                                              "clauses": [b["address"]["id"]]}]}]}
    return regions_doc, hk.evaluate([a, b], list(hr.RULES), ["Rig Widget"])


def negative_controls() -> list:
    regions_doc, kill_doc = synthetic()
    clean = render_traces(regions_doc, kill_doc)
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
         lambda: _halts(lambda: render_traces(null_rec, null_row))),
        ("--verify fails on a rigged stale kill.json", stale_kill),
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
          f"{len(doc['fixtures'])} fixtures; per-outcome counts equal kill.json's")
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
