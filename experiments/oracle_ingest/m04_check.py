#!/usr/bin/env python3
"""M04 — coverage and consistency checker for the H-REGION semantic review.

PINNED TO oracle-compiler-interface/3 (oracle_compiler/INTERFACES.md blob
119778a68c0e4e8378f0a117b7c22884ec5eda4b, Captain ratification 5925134485 +
5925371124). The code follows h_region.py's pin (`hr.INTERFACE_VERSION`,
`hr.verify_interface()`).

Checks `oracle_compiler/analysis/M04-H-REGION-REVIEW-I3.md` (by default)
against the verified interface/3 C03 / C03b artifacts. The interface/2 review
`M04-H-REGION-REVIEW.md` stays on record untouched; it is checkable at its own
commit by that commit's checker. It decides nothing about H-REGION: every figure it
compares is kill.json's, and the result words are C03-KILL's RESULT
PRECEDENCE. It exits non-zero unless the document

  * cites the sha256 of regions.json, kill.json AND trace.json, each equal to
    the verified artifact (the `artifact | sha256` table);
  * has a coverage ledger (the `clause | census key | ...` table) listing every
    C03 clause record -- every population clause (oracle_id + census key) and
    every fixture clause -- exactly once, with each row's population flag,
    fixture roles and K1-K7 outcomes equal to kill.json's, and a disposition on
    every row with an UNRESOLVED outcome;
  * lists every C03 fixture exactly once (the `fixture | member status | ...`
    table), with its member and traced-clause counts, and a disposition on
    every fixture that kill.json records as having a member without a clause;
  * where a disposition is required, it is a real disposition code or text,
    never a placeholder: null/None, JSON `null`, none, n/a, a dash or em-dash,
    TBD/TODO or empty, case-insensitively;
  * states, per condition, the per-outcome totals, the relevant count, the
    relevant PASS / UNRESOLVED / KILL counts, the PASS-coverage flag and the
    result, each equal to kill.json's (the `condition | all PASS | ...` table);
  * states its H-REGION result (`H-REGION result: <words>`) as the RESULT
    PRECEDENCE gives it: 'killed' if any condition has a KILL on a fixture or a
    relevant population clause, otherwise 'not killed on the P2 population';
  * INTERFACE/3 §I3a R4: has an R4 table (`clause | item | interface/2 |
    interface/3 | rule`) with ONE ROW PER (clause, item) R4 changed -- scope or
    head field, region, role mark with its attachment, K1-K7 outcome -- every
    such pair exactly once, each value equal to regions.json's and kill.json's
    (written as c03_trace.py renders it), rule R4, and no row for a clause
    without an IGNORED label (outside R4 reach);
  * and, per clause, kill.json's R4-off K1-K7 outcomes (`r4_off_tests`, the
    interface/2 derivation) equal that clause's row in the section 6 coverage
    ledger of the interface/2 review M04-H-REGION-REVIEW.md, read only at its
    git blob on record (I2_REVIEW_BLOB).

HAND-OFF RULE. An existing C03/C03b artifact is never trusted. In hand-off
order (h_region.py, h_region_kill.py, c03_trace.py): a missing artifact is
regenerated ONLY by invoking its producer unchanged; an existing one is first
checked by its producer's --verify, and a stale report STOPs this checker.
Those producer invocations are this script's only writes; it never edits
C03/C03b output and never writes the review document.

    python3 experiments/oracle_ingest/m04_check.py               # check the review
    python3 experiments/oracle_ingest/m04_check.py --doc PATH    # another document
    python3 experiments/oracle_ingest/m04_check.py --skeleton    # tables, to stdout
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))

import h_region as hr                        # noqa: E402  (sets sys.path)
import h_region_kill as hk                   # noqa: E402
import c03_trace as ct                       # noqa: E402
import foundry_common as fc                  # noqa: E402

SCRIPT = "experiments/oracle_ingest/m04_check.py"
DOC_REL = "oracle_compiler/analysis/M04-H-REGION-REVIEW-I3.md"
# The interface/2 review, on record and untouched: its section 6 ledger is read
# only when the file is this git blob.
I2_REVIEW_REL = "oracle_compiler/analysis/M04-H-REGION-REVIEW.md"
I2_REVIEW_BLOB = "52630e924ae730af0cd696dab06daa5ef3f94e42"
I2_LEDGER_SECTION = re.compile(r"^## 6\.[^\n]*\n(.*?)(?=^## |\Z)", re.M | re.S)
REGIONS_REL, KILL_REL, TRACE_REL = hr.OUT_REL, hk.OUT_REL, ct.OUT_REL
ARTIFACTS = (REGIONS_REL, KILL_REL, TRACE_REL)
# Producers in hand-off order: (script, artifact).
PRODUCERS = ((hr.SCRIPT, REGIONS_REL), (hk.SCRIPT, KILL_REL), (ct.SCRIPT, TRACE_REL))
CONDITIONS = hk.CONDITIONS
OUTCOMES = (hk.PASS, hk.UNRESOLVED, hk.KILL)
NONE = "none"                                 # an absent census key or disposition
# Never a disposition (lower-cased); a run of dashes is refused separately.
PLACEHOLDERS = ("null", NONE, "n/a", "tbd", "todo")
# Each refused placeholder as a document might write it; one negative control
# per form, on an UNRESOLVED ledger row and on a fixture without a clause.
PLACEHOLDER_FORMS = ("null", "NULL", "None", "`null`", "none", "NONE", "-", "—", "TBD",
                     "tbd", "TODO", "todo", "")
RESULT_LINE = re.compile(r"^\s*(?:[-*]\s*)?\**H-REGION result:\**\s*(.*?)\s*$", re.M)

# Each table the document must carry, by the exact cells of its header row.
CITE_HEAD = ["artifact", "sha256"]
LEDGER_HEAD = (["clause", "census key", "population", "fixtures"] + list(CONDITIONS)
               + ["disposition"])
FIXTURE_HEAD = ["fixture", "member status", "members", "clauses", "disposition"]
TOTALS_HEAD = (["condition"] + [f"all {o}" for o in OUTCOMES] + ["relevant"]
               + [f"relevant {o}" for o in OUTCOMES] + ["PASS coverage", "result"])
R4_HEAD = ["clause", "item", "interface/2", "interface/3", "rule"]


# ------------------------------------------------------------- hand-off rule

def _run(args: list) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable] + args, cwd=str(ROOT), capture_output=True)


def obtain(root: Path = None, run=None) -> dict:
    """The verified artifacts' sha256 by path. A missing artifact is
    regenerated by its unchanged producer; an existing one is checked by its
    producer's --verify first, and stale STOPs. `root` and `run` exist only so
    the negative controls can rig the hand-off without touching c03/ or c03b/."""
    root = ROOT if root is None else root
    run = _run if run is None else run
    for script, art in PRODUCERS:
        if (root / art).exists():
            p = run([str(root / script), "--verify"])
            if p.returncode != 0:
                fc.halt(f"stale C03 input: {art} ({script} --verify): "
                        f"{p.stderr.decode('utf-8', 'replace').strip()}")
            continue
        p = run([str(root / script)])
        if p.returncode != 0:
            sys.stderr.write(p.stderr.decode("utf-8", "replace"))
            fc.halt(f"{script} could not regenerate the missing {art}")
        if not (root / art).exists():
            fc.halt(f"{script} exited 0 but did not write {art}")
        p = run([str(root / script), "--verify"])
        if p.returncode != 0:
            fc.halt(f"regenerated {art} does not pass {script} --verify: "
                    f"{p.stderr.decode('utf-8', 'replace').strip()}")
    return {rel: hashlib.sha256((root / rel).read_bytes()).hexdigest()
            for rel in ARTIFACTS}


def load(root: Path = None) -> tuple:
    """(regions_doc, kill_doc, trace_doc, shas), after the hand-off rule."""
    root = ROOT if root is None else root
    shas = obtain(root)
    docs = [json.loads((root / rel).read_text(encoding="utf-8")) for rel in ARTIFACTS]
    regions_doc, kill_doc, trace_doc = docs
    blob = hr.verify_interface()
    for rel, d in zip(ARTIFACTS, docs):
        if d["interface"]["version"] != hr.INTERFACE_VERSION or d["interface"]["blob"] != blob:
            fc.halt(f"{rel} was derived under {d['interface']}, not "
                    f"{hr.INTERFACE_VERSION} ({blob})")
    bad = ct.completeness_failures(trace_doc, regions_doc, kill_doc)
    if bad:
        fc.halt(f"{TRACE_REL} does not trace every C03 clause: " + "; ".join(bad))
    return regions_doc, kill_doc, trace_doc, shas


# ---------------------------------------------------------- document parsing

def _cell(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] == "`":
        s = s[1:-1].strip()
    return s


def tables(text: str) -> list:
    """Every Markdown pipe table: [header cells, [row cells, ...]]."""
    out, block = [], []
    for line in text.splitlines() + [""]:
        if line.strip().startswith("|"):
            block.append(line.strip())
            continue
        if len(block) >= 2:
            split = lambda l: [_cell(c) for c in l.strip("|").split("|")]
            head, sep = split(block[0]), split(block[1])
            if all(re.fullmatch(r":?-{3,}:?", c) for c in sep):
                out.append([head, [split(l) for l in block[2:]]])
        block = []
    return out


def table(text: str, head: list, bad: list):
    """The rows of the one table whose header is `head`, else None (reported)."""
    hit = [rows for h, rows in tables(text) if h == head]
    if len(hit) != 1:
        bad.append(f"the document has {len(hit)} tables headed | {' | '.join(head)} |; "
                   f"exactly one is required")
        return None
    width = [r for r in hit[0] if len(r) != len(head)]
    for r in width:
        bad.append(f"table | {head[0]} | ...: row {r!r} has {len(r)} cells, not "
                   f"{len(head)}")
    return [r for r in hit[0] if len(r) == len(head)]


def census_text(ck) -> str:
    return NONE if ck is None else f"{ck[0]}#{ck[1]}"


def roles_text(roles: list) -> str:
    return ", ".join(roles) if roles else NONE


def _int(s: str):
    return int(s) if re.fullmatch(r"\d+", s) else None


def _disposed(s: str) -> bool:
    """A real disposition code or text: never empty, and never a placeholder
    (null/None, JSON `null`, none, n/a, a dash run, TBD, TODO), compared
    case-insensitively after stripping quoting, emphasis and a trailing period."""
    t = s.strip().strip("`*_\"' ").rstrip(".").strip().lower()
    return bool(t) and t not in PLACEHOLDERS and not re.fullmatch(r"[-–—]+", t)


# ------------------------------------------------------------------ checking

def expected_result(kill_doc: dict) -> str:
    """C03-KILL RESULT PRECEDENCE over the whole of H-REGION: a KILL on a
    fixture or a relevant population clause of any condition -> 'killed';
    otherwise 'not killed on the P2 population' (never 'confirmed')."""
    killed = any(kill_doc["conditions"][k]["relevant"][hk.KILL]["count"]
                 for k in CONDITIONS)
    return hk.RESULT_KILLED if killed else hk.RESULT_NOT_KILLED


def condition_result(cond: dict) -> str:
    return hk.RESULT_KILLED if cond["relevant"][hk.KILL]["count"] else hk.RESULT_NOT_KILLED


def coverage_flag(cond: dict) -> str:
    return hk.COVERAGE_FLAG if cond["relevant"][hk.PASS]["count"] == 0 else "sufficient"


def kill_doc_failures(kill_doc: dict) -> list:
    """kill.json's own stated result and flag per condition against its counts;
    a disagreement is C03's defect, reported, never adapted to."""
    bad = []
    for k in CONDITIONS:
        c = kill_doc["conditions"][k]
        if c["result"] != condition_result(c):
            bad.append(f"kill.json {k}: result {c['result']!r} does not follow RESULT "
                       f"PRECEDENCE over its own counts")
        if c["pass_coverage"] != coverage_flag(c):
            bad.append(f"kill.json {k}: pass_coverage {c['pass_coverage']!r} does not "
                       f"follow its own relevant PASS count")
    return bad


def cite_failures(text: str, shas: dict) -> list:
    bad = []
    rows = table(text, CITE_HEAD, bad)
    if rows is None:
        return bad
    got = {}
    for path, sha in rows:
        got.setdefault(path, []).append(sha)
    for rel in ARTIFACTS:
        cited = got.get(rel, [])
        if len(cited) != 1:
            bad.append(f"the document cites {rel} {len(cited)} times; exactly once is "
                       f"required")
        elif cited[0] != shas[rel]:
            bad.append(f"the document cites {rel} sha256 {cited[0]}, the verified "
                       f"artifact is {shas[rel]}")
    for path in sorted(set(got) - set(ARTIFACTS)):
        bad.append(f"the document cites {path!r}, which is not a C03/C03b artifact")
    return bad


def ledger_failures(text: str, regions_doc: dict, kill_doc: dict) -> list:
    bad = []
    rows = table(text, LEDGER_HEAD, bad)
    if rows is None:
        return bad
    want = {}
    for r in kill_doc["clauses"]:
        if r["population"] or r["fixture_roles"]:
            want[(r["id"], census_text(r["census_key"]))] = r
    keys = [(row[0], row[1]) for row in rows]
    for k in sorted(set(keys)):
        if keys.count(k) != 1:
            bad.append(f"the ledger lists clause {k[0]} census {k[1]} {keys.count(k)} "
                       f"times; exactly once is required")
    for k in sorted(set(want) - set(keys)):
        bad.append(f"the ledger omits C03 clause {k[0]} census {k[1]}")
    for k in sorted(set(keys) - set(want)):
        bad.append(f"the ledger lists {k[0]} census {k[1]}, which is not a C03 clause")
    pop = [[k[0].split(":")[0]] + list(want[k]["census_key"]) for k in set(keys)
           if k in want and want[k]["population"]]
    for row in regions_doc["population_keys"]:
        if pop.count(row) != 1:
            bad.append(f"the ledger lists population census row {row} {pop.count(row)} "
                       f"times; exactly once is required")
    for row in rows:
        k = (row[0], row[1])
        if k not in want:
            continue
        r = want[k]
        label = f"ledger {k[0]} census {k[1]}"
        if row[2] != ("yes" if r["population"] else "no"):
            bad.append(f"{label}: population {row[2]!r}, kill.json "
                       f"{'yes' if r['population'] else 'no'}")
        if row[3] != roles_text(r["fixture_roles"]):
            bad.append(f"{label}: fixtures {row[3]!r}, kill.json "
                       f"{roles_text(r['fixture_roles'])!r}")
        got = dict(zip(CONDITIONS, row[4:4 + len(CONDITIONS)]))
        for c in CONDITIONS:
            if got[c] != r["tests"][c]["outcome"]:
                bad.append(f"{label}: {c} {got[c]!r}, kill.json "
                           f"{r['tests'][c]['outcome']}")
        unres = [c for c in CONDITIONS if r["tests"][c]["outcome"] == hk.UNRESOLVED
                 or got[c] == hk.UNRESOLVED]
        if unres and not _disposed(row[-1]):
            bad.append(f"{label}: UNRESOLVED on {', '.join(unres)} carries no "
                       f"disposition")
    return bad


def fixture_failures(text: str, regions_doc: dict, kill_doc: dict) -> list:
    bad = []
    rows = table(text, FIXTURE_HEAD, bad)
    if rows is None:
        return bad
    want = {f["role"]: f for f in regions_doc["fixtures"]}
    open_ = {x["role"] for x in kill_doc.get("fixtures_without_clauses", [])}
    roles = [row[0] for row in rows]
    for r in sorted(set(roles)):
        if roles.count(r) != 1:
            bad.append(f"the fixture table lists {r} {roles.count(r)} times; exactly "
                       f"once is required")
    for r in sorted(set(want) - set(roles)):
        bad.append(f"the fixture table omits C03 fixture {r}")
    for r in sorted(set(roles) - set(want)):
        bad.append(f"the fixture table lists {r!r}, which is not a C03 fixture")
    for row in rows:
        f = want.get(row[0])
        if f is None:
            continue
        n_mem = len(f["members"])
        n_cl = sum(len(m["clauses"]) for m in f["members"])
        if row[1] != f["member_status"]:
            bad.append(f"fixture {row[0]}: member status {row[1]!r}, C03 "
                       f"{f['member_status']}")
        if _int(row[2]) != n_mem:
            bad.append(f"fixture {row[0]}: members {row[2]!r}, C03 {n_mem}")
        if _int(row[3]) != n_cl:
            bad.append(f"fixture {row[0]}: clauses {row[3]!r}, C03 {n_cl}")
        if row[0] in open_ and not _disposed(row[4]):
            bad.append(f"fixture {row[0]}: a member without a clause (kill.json "
                       f"fixtures_without_clauses) carries no disposition")
    return bad


def totals_failures(text: str, kill_doc: dict) -> list:
    bad = []
    rows = table(text, TOTALS_HEAD, bad)
    if rows is None:
        return bad
    conds = [row[0] for row in rows]
    for k in sorted(set(conds)):
        if conds.count(k) != 1:
            bad.append(f"the totals table states {k} {conds.count(k)} times")
    for k in CONDITIONS:
        if k not in conds:
            bad.append(f"the totals table omits condition {k}")
    for k in sorted(set(conds) - set(CONDITIONS)):
        bad.append(f"the totals table states {k!r}, which is not a condition")
    for row in rows:
        k = row[0]
        if k not in CONDITIONS:
            continue
        c = kill_doc["conditions"][k]
        want = ([c["all"][o]["count"] for o in OUTCOMES] + [c["relevant"]["count"]]
                + [c["relevant"][o]["count"] for o in OUTCOMES])
        for name, got, w in zip(TOTALS_HEAD[1:8], row[1:8], want):
            if _int(got) != w:
                bad.append(f"{k} {name}: stated {got!r}, kill.json {w}")
        if row[8] != c["pass_coverage"]:
            bad.append(f"{k} PASS coverage: stated {row[8]!r}, kill.json "
                       f"{c['pass_coverage']!r}")
        if row[9] != condition_result(c):
            bad.append(f"{k} result: stated {row[9]!r}, RESULT PRECEDENCE gives "
                       f"{condition_result(c)!r}")
    return bad


def result_failures(text: str, kill_doc: dict) -> list:
    got = RESULT_LINE.findall(text)
    want = expected_result(kill_doc)
    if len(got) != 1:
        return [f"the document states 'H-REGION result:' {len(got)} times; exactly once "
                f"is required"]
    stated = got[0].strip().strip("*_`").strip()
    if stated != want:
        return [f"the H-REGION result is stated as {stated!r}; RESULT PRECEDENCE gives "
                f"{want!r}"]
    return []


# ------------------------------------------------------ interface/3 §I3a R4

def _ignored_clauses(regions_doc: dict) -> set:
    """The clauses within R4 reach: those with an IGNORED label."""
    return {c["address"]["id"] for c in regions_doc["clauses"]
            if (c.get("r4_label") or {}).get("effect") == "ignored"}


def r4_expected(regions_doc: dict, kill_doc: dict) -> list:
    """[(clause, item, interface/2, interface/3, rule)], in C03 order: one per
    (clause, item) R4 changed, each value as c03_trace.py renders it from
    regions.json and kill.json. Two records of one clause that disagree on a
    pair HALT (the pair would not be one row)."""
    rows = {(r["id"], json.dumps(r.get("census_key"))): r for r in kill_doc["clauses"]}
    out, seen = [], {}
    for c in regions_doc["clauses"]:
        cid = c["address"]["id"]
        row = rows.get((cid, json.dumps(c.get("census_key"))))
        if row is None:
            fc.halt(f"kill.json has no row for C03 record {cid} {c.get('census_key')!r}")
        _, changed = ct.r4_record(c, row, [cid, c.get("census_key")])
        for i in changed:
            r = (cid, i["item"], ct._fmt(i["interface2"]), ct._fmt(i["interface3"]),
                 i["rule"])
            if (cid, i["item"]) in seen:
                if seen[(cid, i["item"])] != r:
                    fc.halt(f"two C03 records of {cid} disagree on R4 item {i['item']}")
                continue
            seen[(cid, i["item"])] = r
            out.append(r)
    return out


def r4_table_failures(text: str, regions_doc: dict, kill_doc: dict) -> list:
    bad = []
    rows = table(text, R4_HEAD, bad)
    if rows is None:
        return bad
    want = {(r[0], r[1]): r for r in r4_expected(regions_doc, kill_doc)}
    reach = _ignored_clauses(regions_doc)
    keys = [(row[0], row[1]) for row in rows]
    for k in sorted(set(keys)):
        if keys.count(k) != 1:
            bad.append(f"the R4 table lists clause {k[0]} item {k[1]} {keys.count(k)} "
                       f"times; exactly once is required")
    for k in sorted(set(want) - set(keys)):
        bad.append(f"the R4 table omits clause {k[0]} item {k[1]} (R4 changed it)")
    for cid in sorted({k[0] for k in keys} - reach):
        bad.append(f"the R4 table has a row for clause {cid}, which is outside R4 reach "
                   f"(no IGNORED label)")
    for k in sorted(set(keys) - set(want)):
        if k[0] in reach:
            bad.append(f"the R4 table lists clause {k[0]} item {k[1]}, which R4 did not "
                       f"change")
    for row in rows:
        w = want.get((row[0], row[1]))
        if w is None:
            continue
        for name, got, exp in zip(R4_HEAD[2:], row[2:], w[2:]):
            if got != exp:
                bad.append(f"R4 table {row[0]} {row[1]}: {name} {got!r}, artifacts "
                           f"{exp!r}")
    return bad


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def read_i2_review(root: Path = None) -> str:
    """The interface/2 review's text, only as the git blob on record."""
    data = ((ROOT if root is None else root) / I2_REVIEW_REL).read_bytes()
    if git_blob(data) != I2_REVIEW_BLOB:
        fc.halt(f"{I2_REVIEW_REL} is blob {git_blob(data)}, not the interface/2 review "
                f"on record ({I2_REVIEW_BLOB})")
    return data.decode("utf-8")


def r4_off_failures(i2_text: str, kill_doc: dict) -> list:
    """Per clause: kill.json's R4-off K1-K7 outcomes equal the clause's row in
    the interface/2 review's section 6 coverage ledger."""
    sec = I2_LEDGER_SECTION.findall(i2_text)
    if len(sec) != 1:
        return [f"the interface/2 review has {len(sec)} section 6 (coverage ledger); "
                f"exactly one is required"]
    bad = []
    rows = table(sec[0], LEDGER_HEAD, bad)
    bad = [f"interface/2 review section 6: {b}" for b in bad]
    if rows is None:
        return bad
    ledger = {}
    for row in rows:
        ledger.setdefault((row[0], row[1]), []).append(row)
    want = {(r["id"], census_text(r["census_key"])): r for r in kill_doc["clauses"]
            if r["population"] or r["fixture_roles"]}
    for k in sorted(want):
        got = ledger.get(k, [])
        if len(got) != 1:
            bad.append(f"the interface/2 ledger has {len(got)} rows for clause {k[0]} "
                       f"census {k[1]}; exactly one is required")
            continue
        r = want[k]
        if "r4_off_tests" not in r:
            bad.append(f"kill.json clause {k[0]} census {k[1]} carries no R4-off outcomes")
            continue
        for c, cell in zip(CONDITIONS, got[0][4:4 + len(CONDITIONS)]):
            if cell != r["r4_off_tests"][c]["outcome"]:
                bad.append(f"R4-off {c} of clause {k[0]} census {k[1]}: kill.json "
                           f"{r['r4_off_tests'][c]['outcome']}, interface/2 ledger "
                           f"{cell!r}")
    for k in sorted(set(ledger) - set(want)):
        bad.append(f"the interface/2 ledger lists {k[0]} census {k[1]}, which is not a "
                   f"C03 clause")
    return bad


def document_failures(text: str, regions_doc: dict, kill_doc: dict, shas: dict,
                      i2_text: str) -> list:
    """Every way the document (and the interface/2 ledger `i2_text` it carries
    forward) disagrees with the verified artifacts."""
    return (kill_doc_failures(kill_doc) + cite_failures(text, shas)
            + ledger_failures(text, regions_doc, kill_doc)
            + fixture_failures(text, regions_doc, kill_doc)
            + totals_failures(text, kill_doc) + result_failures(text, kill_doc)
            + r4_table_failures(text, regions_doc, kill_doc)
            + r4_off_failures(i2_text, kill_doc))


# ------------------------------------------------------------------ skeleton

def _row(cells: list) -> str:
    return "| " + " | ".join(str(c) for c in cells) + " |"


def _sep(n: int) -> str:
    return "|" + "---|" * n


def skeleton(regions_doc: dict, kill_doc: dict, shas: dict) -> str:
    """The tables the checker requires, filled with kill.json's figures; every
    disposition cell is `none`. A starting point for the review, never a review:
    each UNRESOLVED row still fails until it carries a real disposition."""
    out = [_row(CITE_HEAD), _sep(len(CITE_HEAD))]
    out += [_row([f"`{rel}`", f"`{shas[rel]}`"]) for rel in ARTIFACTS]
    out += ["", _row(LEDGER_HEAD), _sep(len(LEDGER_HEAD))]
    for r in kill_doc["clauses"]:
        if r["population"] or r["fixture_roles"]:
            out.append(_row([f"`{r['id']}`", census_text(r["census_key"]),
                             "yes" if r["population"] else "no",
                             roles_text(r["fixture_roles"])]
                            + [r["tests"][k]["outcome"] for k in CONDITIONS] + [NONE]))
    out += ["", _row(FIXTURE_HEAD), _sep(len(FIXTURE_HEAD))]
    for f in regions_doc["fixtures"]:
        out.append(_row([f["role"], f["member_status"], len(f["members"]),
                         sum(len(m["clauses"]) for m in f["members"]), NONE]))
    out += ["", _row(TOTALS_HEAD), _sep(len(TOTALS_HEAD))]
    for k in CONDITIONS:
        c = kill_doc["conditions"][k]
        out.append(_row([k] + [c["all"][o]["count"] for o in OUTCOMES]
                        + [c["relevant"]["count"]]
                        + [c["relevant"][o]["count"] for o in OUTCOMES]
                        + [c["pass_coverage"], condition_result(c)]))
    out += ["", _row(R4_HEAD), _sep(len(R4_HEAD))]
    out += [_row([f"`{r[0]}`", r[1], f"`{r[2]}`", f"`{r[3]}`", r[4]])
            for r in r4_expected(regions_doc, kill_doc)]
    out += ["", f"H-REGION result: {expected_result(kill_doc)}"]
    return "\n".join(out) + "\n"


def i2_ledger(kill_doc: dict) -> str:
    """A synthetic interface/2 review: its section 6 ledger holds each
    clause's R4-off outcomes. For the negative controls only."""
    out = ["## 6. Coverage ledger", "", _row(LEDGER_HEAD), _sep(len(LEDGER_HEAD))]
    for r in kill_doc["clauses"]:
        if r["population"] or r["fixture_roles"]:
            out.append(_row([f"`{r['id']}`", census_text(r["census_key"]),
                             "yes" if r["population"] else "no",
                             roles_text(r["fixture_roles"])]
                            + [r["r4_off_tests"][k]["outcome"] for k in CONDITIONS]
                            + ["interface/2"]))
    return "\n".join(out + ["", "## 7. Totals", ""]) + "\n"


# ---------------------------------------------------------- negative controls

def _halts(fn, needle: str = "") -> bool:
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            fn()
    except SystemExit:
        return needle in err.getvalue()
    return False


R4_CLAUSE = "rig:0:1:0"                         # the synthetic clause behind a label


def synthetic() -> tuple:
    """(regions_doc, kill_doc, shas, document, interface/2 review) over inline
    synthetic clauses: one population clause whose K1/K2 are UNRESOLVED, one
    fixture clause, one fixture without a clause, and one population clause
    behind an IGNORED R4 label that changes its scope, role marks and outcomes.
    The document is the skeleton with every disposition filled; the
    interface/2 review's ledger holds the R4-off outcomes."""
    a = hk._rig("Destroy target artifact, then proliferate.", census=("destroy", 0),
                population=True)
    b = hk._rig("Exile target artifact you control, then return that card to the "
                "battlefield.", census=("exile", 0), roles=["rig-role"], ci=1)
    c = ct.rig_paragraph(ct.RIG_R4, 1, census=("exile", 1), population=True)
    regions_doc, kill_doc = ct.rig_docs(
        [a, b, c], [["rig", "destroy", 0], ["rig", "exile", 1]],
        [{"role": "rig-role", "member_status": "rig",
          "members": [{"oracle_id": "rig", "census_key": ["exile", 0],
                       "clauses": [b["address"]["id"]]}]},
         {"role": "rig-empty", "member_status": "rig", "members": []}], ["Rig Widget"])
    kill_doc["fixtures_without_clauses"] = [{"role": "rig-empty", "member": None,
                                             "member_status": "rig",
                                             "reason": "no member"}]
    shas = {rel: hashlib.sha256(rel.encode()).hexdigest() for rel in ARTIFACTS}
    doc = skeleton(regions_doc, kill_doc, shas).replace(
        f" | {NONE} |\n", " | reviewed: an extraction gap, not a kill |\n")
    return regions_doc, kill_doc, shas, doc, i2_ledger(kill_doc)


def _relevant_kill(kill_doc: dict) -> dict:
    """kill.json with the population clause's K4 rigged to a relevant KILL."""
    k = copy.deepcopy(kill_doc)
    t = k["clauses"][0]["tests"]["K4"]
    t.update(outcome=hk.KILL, relevant=True)
    # An unlabelled clause: its R4-off outcome is its outcome (R4 IS CONFINED).
    k["clauses"][0]["r4_off_tests"]["K4"].update(outcome=hk.KILL, relevant=True)
    k["conditions"] = hk.summarize(k["clauses"])
    return k


def _r4_off_rigged(kill_doc: dict) -> dict:
    """kill.json with the R4 clause's R4-off K1 outcome rigged (and its R4
    record kept consistent), so it differs from the interface/2 ledger row."""
    k = copy.deepcopy(kill_doc)
    row = next(r for r in k["clauses"] if r["id"] == R4_CLAUSE)
    was = row["r4_off_tests"]["K1"]
    now = row["tests"]["K1"]
    was["outcome"] = next(o for o in OUTCOMES if o not in (was["outcome"], now["outcome"]))
    row.setdefault("interface2_changes", {})["K1"] = {
        "interface2": was["outcome"], "interface2_relevant": was["relevant"],
        "interface3": now["outcome"], "interface3_relevant": now["relevant"],
        "changed_by": ["R4"]}
    return k


def rigs() -> dict:
    """name -> (document, regions_doc, kill_doc, shas, interface/2 review,
    needle): each rig must fail with a diagnostic containing `needle`."""
    rigs5 = _rigs()
    regions_doc, kill_doc, shas, doc, i2 = synthetic()
    out = {name: (d, rd, kd, sh, i2, needle)
           for name, (d, rd, kd, sh, needle) in rigs5.items()}
    lines = doc.splitlines(keepends=True)
    r4_rows = [l for l in lines if l.startswith(f"| `{R4_CLAUSE}` |")
               and l.endswith(" | R4 |\n")]
    misstated = r4_rows[0].split("|")
    misstated[3] = " `misstated` "
    outside = f"| `rig:0:0:0` | K1 | `{hk.UNRESOLVED}` | `{hk.PASS}` | R4 |\n"
    i2_row = next(l for l in i2.splitlines(keepends=True)
                  if l.startswith(f"| `{R4_CLAUSE}` |"))
    i2_cells = i2_row.split("|")
    i2_cells[5] = f" {next(o for o in OUTCOMES if o != i2_cells[5].strip())} "
    return out | {
        "a document whose R4 section misses one R4-changed clause": (
            "".join(l for l in lines if l not in r4_rows), regions_doc, kill_doc, shas,
            i2, f"the R4 table omits clause {R4_CLAUSE}"),
        "a document misstating one interface/2 value in its R4 section": (
            doc.replace(r4_rows[0], "|".join(misstated)), regions_doc, kill_doc, shas,
            i2, "interface/2 'misstated', artifacts"),
        "an R4-off outcome that differs from the interface/2 review's ledger row": (
            doc, regions_doc, _r4_off_rigged(kill_doc), shas, i2,
            f"R4-off K1 of clause {R4_CLAUSE}"),
        "an interface/2 ledger row that differs from kill.json's R4-off outcome": (
            doc, regions_doc, kill_doc, shas, i2.replace(i2_row, "|".join(i2_cells)),
            f"R4-off K1 of clause {R4_CLAUSE}"),
        "an R4-table row for a clause outside R4 reach": (
            doc.replace(r4_rows[-1], r4_rows[-1] + outside), regions_doc, kill_doc,
            shas, i2, "rig:0:0:0, which is outside R4 reach"),
    }


def _rigs() -> dict:
    """The interface/2-era rigs: name -> (document, regions_doc, kill_doc, shas,
    needle)."""
    regions_doc, kill_doc, shas, doc, _i2 = synthetic()
    lines = doc.splitlines(keepends=True)
    first = next(l for l in lines if l.startswith("| `rig:0:0:0`"))
    unres = first.rsplit("|", 2)[0] + f"| {NONE} |\n"
    tot = next(l for l in lines if l.startswith("| K7 |"))
    cells = tot.split("|")
    cells[1 + 1] = f" {int(cells[2]) + 1} "
    k1 = next(l for l in lines if l.startswith("| K1 |"))
    k1_cells = k1.split("|")
    k1_cells[9] = " "
    killed = _relevant_kill(kill_doc)
    killed_doc = skeleton(regions_doc, killed, shas).replace(
        f" | {NONE} |\n", " | reviewed |\n").replace(
        f"H-REGION result: {hk.RESULT_KILLED}", f"H-REGION result: {hk.RESULT_NOT_KILLED}")
    bad_sha = dict(shas, **{TRACE_REL: "0" * 64})
    empty = next(l for l in lines if l.startswith("| rig-empty |"))
    disposed = lambda row, form: row.rsplit("|", 2)[0] + f"| {form} |\n"
    placeholders = {}
    for form in PLACEHOLDER_FORMS:
        placeholders[f"an UNRESOLVED row disposed as {form!r}"] = (
            doc.replace(first, disposed(first, form)), regions_doc, kill_doc, shas,
            "rig:0:0:0 census destroy#0: UNRESOLVED on K1")
        placeholders[f"a fixture without a clause disposed as {form!r}"] = (
            doc.replace(empty, disposed(empty, form)), regions_doc, kill_doc, shas,
            "fixture rig-empty: a member without a clause")
    return placeholders | {
        "a ledger missing one clause": (doc.replace(first, ""), regions_doc, kill_doc,
                                        shas, "the ledger omits C03 clause rig:0:0:0"),
        "a total mismatch": (doc.replace(tot, "|".join(cells)), regions_doc, kill_doc,
                             shas, "K7 all PASS: stated"),
        "an UNRESOLVED row without a disposition": (doc.replace(first, unres), regions_doc,
                                                    kill_doc, shas,
                                                    "carries no disposition"),
        "a document citing a wrong trace.json hash": (doc, regions_doc, kill_doc, bad_sha,
                                                      f"cites {TRACE_REL} sha256"),
        "a document stating 'not killed' over a relevant KILL": (
            killed_doc, regions_doc, killed, shas, "RESULT PRECEDENCE gives 'killed'"),
        "a document omitting a PASS-coverage flag": (doc.replace(k1, "|".join(k1_cells)),
                                                     regions_doc, kill_doc, shas,
                                                     "K1 PASS coverage: stated ''"),
    }


def stale_trace_stops() -> bool:
    """A rigged stale trace.json (c03_trace.py --verify exits 1) STOPs obtain(),
    after the two upstream producers verified and before any regeneration."""
    import tempfile
    calls = []

    def run(args):
        calls.append(args)
        stale = args[-1] == "--verify" and args[0].endswith(ct.SCRIPT)
        return subprocess.CompletedProcess(args, 1 if stale else 0, b"",
                                           b"STALE: rigged" if stale else b"")

    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        for rel in ARTIFACTS:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_bytes(b"{}\n")
        halted = _halts(lambda: obtain(root, run), f"stale C03 input: {TRACE_REL}")
        fresh = []
        ok = lambda args: fresh.append(args) or subprocess.CompletedProcess(args, 0, b"", b"")
        with contextlib.redirect_stderr(io.StringIO()):
            got = obtain(root, ok)
    return (halted and [c[0].split(str(root) + "/")[1] for c in calls]
            == [s for s, _ in PRODUCERS] and all(c[-1] == "--verify" for c in calls)
            and set(got) == set(ARTIFACTS) and len(fresh) == 3)


def negative_controls() -> list:
    regions_doc, kill_doc, shas, doc, i2 = synthetic()
    cases = [("the unrigged synthetic document passes",
              lambda: document_failures(doc, regions_doc, kill_doc, shas, i2) == [])]
    for name, (d, rd, kd, sh, i2t, needle) in rigs().items():
        cases.append((f"a rigged {name} fails",
                      lambda d=d, rd=rd, kd=kd, sh=sh, i2t=i2t, needle=needle: any(
                          needle in b for b in document_failures(d, rd, kd, sh, i2t))))
    cases.append(("a rigged stale trace.json STOPs the checker", stale_trace_stops))
    out = []
    for name, check in cases:
        if not check():
            fc.halt(f"negative control failed: {name}")
        out.append(name)
    return out


# ----------------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--doc", default=DOC_REL, help="the review document (repo-relative)")
    ap.add_argument("--skeleton", action="store_true",
                    help="print the required tables, filled from kill.json, to stdout")
    a = ap.parse_args(argv)
    controls = negative_controls()
    regions_doc, kill_doc, _trace, shas = load()
    if a.skeleton:
        sys.stdout.write(skeleton(regions_doc, kill_doc, shas))
        return 0
    path = Path(a.doc) if Path(a.doc).is_absolute() else ROOT / a.doc
    if not path.exists():
        print(f"FAIL: {a.doc} does not exist", file=sys.stderr)
        return 1
    bad = document_failures(path.read_text(encoding="utf-8"), regions_doc, kill_doc, shas,
                            read_i2_review())
    for b in bad:
        print(f"FAIL: {b}", file=sys.stderr)
    if bad:
        return 1
    flags = [k for k in CONDITIONS if kill_doc["conditions"][k]["pass_coverage"]
             != "sufficient"]
    print(f"{a.doc}: coverage ledger, fixtures, totals, PASS-coverage flags, the "
          f"H-REGION result ({expected_result(kill_doc)}), the three artifact hashes "
          f"and the R4 table ({len(r4_expected(regions_doc, kill_doc))} rows) agree with "
          f"the verified C03/C03b artifacts; every clause's R4-off outcomes equal the "
          f"interface/2 ledger ({I2_REVIEW_REL}); {len(controls)} negative controls hold"
          + (f"; {hk.COVERAGE_FLAG}: {', '.join(flags)}" if flags else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
