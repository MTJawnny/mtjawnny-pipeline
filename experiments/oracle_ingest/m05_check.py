#!/usr/bin/env python3
"""M05 -- coverage and consistency checker for the C04 reference read.

Checks the M05 read documents (`oracle_compiler/analysis/M05-<rule>-P<k>-READ.md`
and `oracle_compiler/analysis/M05-FIXTURES-READ.md`) and the summary
(`oracle_compiler/analysis/M05-SUMMARY.md`) against the verified C04 output
`experiments/out/oracle_ingest/c04/refs.json`, and carries the M05 READING
PROTOCOL (`PROTOCOL`, printed by `--protocol`), which binds this checker as
well as every reader. It judges no row: every verdict cell is the reader's;
this script checks that each document is complete, well-formed and
consistent with its own ledger.

READ SET (§I5.4). A rule's rows are its refs.json candidates with outcome
RESOLVED (E5: NOT-COREFERENCE), sorted by (class, row_id), split into P
contiguous parts, part k (1-based) holding rows [floor((k-1)n/P), floor(kn/P));
P is E1 4, E2 4, E3 2, E4 5, E5 1. The fixture rows are every candidate whose
fixture_role is one of the five §I5.4 roles, sorted by (class, row_id). In
both sorts a null class sorts as the empty string.

A READ DOCUMENT (--doc) fails unless: (a) it holds exactly one line
`refs.json sha256: <64 hex>` and it cites the verified refs.json; (b) exactly
one ledger table, its header line exactly
`| row | class | endpoint | kind | duplicate | note |`, holds exactly the
document's rows, each once, in skeleton order, with no foreign row and no
row-shaped pipe line anywhere outside it (a row detached by a blank line, in
another table or in a fence) nor any pipe line belonging to no table, the row
and class cells literal (no code or emphasis markup; the class equal to
refs.json's, `none` when null), each verdict cell exactly yes, no or
cannot-judge, and each note holding a double-quoted phrase
of at most 12 words that occurs verbatim in the row's paragraph_text,
endpoint_text or face_text -- and, when a cell is no or cannot-judge, at
least two further words outside the quotes giving the reason; (c) exactly one
'## Verdict' section holding the one canonical line
`- <rule>/P<k>: <WORD> (rows n, endpoint-no n, kind-no n, duplicate-no n,
cannot-judge n); <text>` (fixture document `- FIXTURES: ...`), its counts the
ledger's (cannot-judge counts rows with at least one cannot-judge cell) and
its word the PART VERDICT precedence: FAIL when endpoint-no > 0, else
INCONCLUSIVE when cannot-judge x 20 > rows, else PASS; (d) a FAIL has a
'## Failing classes' section naming every class with an endpoint-no row and
each such row_id; (e) exactly one '## Captain questions' heading.

CHECKER THREAT MODEL (Captain rulings 5987664829 A, 6002030055 A2, 6007151819
A3): accidental malformation only, on the RAW text, code spans and fences
included. (A) '<!--', '-->' or '<' followed by an ASCII letter, '/' or '!'
anywhere fails; (A3) '](', ']:', '&' or a backslash anywhere fails; (A2) the
canonical verdict line has exactly one form and position -- any other line
that reads as a verdict line for the document's label (any indentation, quote
or list marker, emphasis or code markup) fails -- and any occurrence anywhere
of a row address, the document's rule id or label followed within 6
non-alphanumeric characters by a verdict word (PASS, FAIL, INCONCLUSIVE, any
case) must agree with the canonical line; any other rule id, part or FIXTURES
label followed by a verdict word fails. Each failure names the line.

--rule <r> checks the rule's P part documents, which must partition the
rule's rows exactly and cite one refs.json sha256, and prints the RULE
VERDICT: the same precedence over the parts' summed counts. --summary checks
M05-SUMMARY.md: one canonical line `- <rule>: <WORD> (...); <text>` per rule
E1-E5 and FIXTURES, equal to the --rule aggregates and the fixture document,
all documents citing the same sha256.

HAND-OFF RULE. An existing refs.json is never trusted: it is first checked by
`c04_refs.py --verify`, and stale STOPs; a missing one is regenerated ONLY by
`c04_refs.py --check-determinism`, unchanged. That invocation is this script's
only write.

    python3 experiments/oracle_ingest/m05_check.py --protocol
    python3 experiments/oracle_ingest/m05_check.py --skeleton --rule E4 --part 2
    python3 experiments/oracle_ingest/m05_check.py --skeleton --fixtures
    python3 experiments/oracle_ingest/m05_check.py --doc oracle_compiler/analysis/M05-E4-P2-READ.md
    python3 experiments/oracle_ingest/m05_check.py --rule E4
    python3 experiments/oracle_ingest/m05_check.py --summary
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]

SCRIPT = "experiments/oracle_ingest/m05_check.py"
C04_SCRIPT = "experiments/oracle_ingest/c04_refs.py"
REFS_REL = "experiments/out/oracle_ingest/c04/refs.json"
ANALYSIS = "oracle_compiler/analysis"
SUMMARY_REL = f"{ANALYSIS}/M05-SUMMARY.md"
FIXTURES_REL = f"{ANALYSIS}/M05-FIXTURES-READ.md"

PROTOCOL_SHA256 = "66e13172e565b21189008995b936a1b5a931dff205ae2f794bca04eb57835873"
# The M05 READING PROTOCOL, exactly as the authorizing command quotes it.
PROTOCOL = """M05 READING PROTOCOL (goal plan v9, binding for every M05 read wave)

HAND-OFF RULE: a consumer never trusts an existing experiments/out/oracle_ingest/c04/refs.json. If it is missing, the consumer regenerates it ONLY by invoking `python3 experiments/oracle_ingest/c04_refs.py --check-determinism` unchanged; if it exists, the consumer first runs `python3 experiments/oracle_ingest/c04_refs.py --verify` and STOPs if it reports stale.

a row is identified by refs.json's row_id ('<oracle_id>:<face>:<paragraph>:<clause>@<char_offset>:<phrase>').

THE READER (§I5.8 ruling 15, override 5966663066): the headless CLAUDE session executing a read wave, fresh and isolated, neither the C04 Worker nor the author of the rules; a Codex session receiving a read unit on a capacity failover STOPs (models decided under standing approval, reversible: Worker Claude in every wave; reviewers per decision E as amended -- a fresh isolated Claude session for non-terminal waves, Codex for a plan's terminal wave). RULES FROZEN (§I5.4): the reader judges rows and never edits c04_refs.py, refs.json or any rule. CARDS FIRST: for each row read paragraph_text, ref_text, endpoint_text and (for E2) face_text from refs.json and decide what the reference means under the Comprehensive Rules (read through experiments/foundry_cr.py when a rule is cited) BEFORE comparing with C04's endpoint. Every row is read; no sampling, no inference from neighbouring rows. NO CARD DATA IN GIT: documents and tests carry no Oracle text beyond the short printed phrase a verdict turns on (at most 12 words, as INTERFACES.md quotes labels); rows and cards are named only by four-coordinate address (oracle_id:face:paragraph:clause) and offset, or by refs.json's row_id, never by card name; card text lives only in the ignored refs.json.

ROW VERDICTS (definitions binding for every M05 reader and checker): each row carries THREE cells, each exactly yes, no or cannot-judge (§I5.4). ENDPOINT = yes when the endpoint refs.json records is what the reference means under the Comprehensive Rules; for E5, when the clause is a printed comparison; for a fixture row whose outcome is not RESOLVED, when that outcome and reason are right. KIND = yes when the endpoint kind is right (EVENT, LINKED, COREFERENT, PRODUCT, OBJECT; measurement labels only, §I5.8 ruling 5); for E5, and for a fixture row with no endpoint, yes exactly when refs.json records no endpoint. A null class is written none. DUPLICATE = yes when no other row of the read set claims an intersecting printed reference span (same clause address, and the spans [char_offset, char_offset + len(phrase)) intersect; §I4 identity, §I5.1 overlap). A no or cannot-judge cell carries its reason. EVERY row's note quotes, in double quotes, a phrase of at most 12 words that occurs verbatim in that row's paragraph_text, endpoint_text or face_text and shows what the reference points to (the evidence that the card was read). PART VERDICT (decided under standing approval, reversible by the Captain): FAIL when any ENDPOINT is no (a wrong RESOLVED is a false success, §I5.4, and goes to the Captain under §I5.8 ruling 4); otherwise INCONCLUSIVE when rows with at least one cannot-judge cell x 20 > rows (more than 5%); otherwise PASS. KIND-no and DUPLICATE-no rows are listed findings for the Captain, not FAIL. A RULE VERDICT applies the same precedence to the rule's parts' summed counts. The FIXTURES verdict uses the same precedence (decided under standing approval, reversible: an endpoint-no on a fixture row is a wrong claim about that candidate).

PATTERN CLASSES (§I5.4, ratified by §I5.8 ruling 4) are refs.json's class field: E1 one class per frozen head, E2 'exiled' and 'chosen', E3 one, E4 one per marker phrase, E5 one. A FAIL names its failing classes.

PARTS (decided under standing approval, reversible: the reading is split so each part is read by its own fresh session; the rule stays the audit unit of §I5.4 through the aggregated rule verdict): a rule's rows are its refs.json candidates with outcome RESOLVED (E5: outcome NOT-COREFERENCE), per §I5.4; sorted by (class, row_id), are split into P contiguous parts, part k (1-based) holding rows [floor((k-1)*n/P), floor(k*n/P)); P is E1 4, E2 4, E3 2, E4 5, E5 1. `m05_check.py --skeleton --rule <r> --part <k>` prints that part's rows.

DOCUMENT FORMAT (every read document; checked by m05_check.py): (1) a line exactly `refs.json sha256: <64 hex>` citing the verified refs.json; every read document and the summary cite the SAME sha256, or --rule and --summary fail. (2) a ledger table whose header row is exactly `| row | class | endpoint | kind | duplicate | note |`, one line per row of the part (fixture document: per fixture candidate) in skeleton order: row = row_id, class = refs.json class (none when null), three verdict cells, note. (3) `## Verdict` holding exactly one canonical line `- <rule>/P<k>: <PASS|FAIL|INCONCLUSIVE> (rows n, endpoint-no n, kind-no n, duplicate-no n, cannot-judge n); <text>` (fixture document: `- FIXTURES: ...`). (4) for a FAIL, `## Failing classes` listing each failing class and its row_ids. (5) exactly one `## Captain questions` heading. Any other rule id, part or FIXTURES label followed by a verdict word is rejected. `python3 experiments/oracle_ingest/m05_check.py --skeleton --rule <r> --part <k>` prints a part's ledger rows to fill, and `--skeleton --fixtures` the fixture rows (sorted by (class, row_id)).

CHECKER THREAT MODEL (Captain rulings 5987664829 A, 6002030055 A2, 6007151819 A3, carried here from the start): the checker guards against ACCIDENTAL malformation of documents a Worker writes, which a reviewer then reads in full; concealment through Markdown rendering is outside its threat model. It enforces on the RAW text: (A) any '<!--', '-->' or raw HTML tag ('<' followed by an ASCII letter, '/' or '!') anywhere is rejected; (A3) any '](', ']:', '&' or backslash anywhere is rejected; (A2-style) every required verdict line has exactly one canonical form and position, and any other occurrence anywhere of a row address or rule id followed within 6 non-alphanumeric characters by a verdict word must agree with that canonical line (verdict words: PASS, FAIL, INCONCLUSIVE). Each rejection names the line in plain English."""  # noqa: E501

PARTS = {"E1": 4, "E2": 4, "E3": 2, "E4": 5, "E5": 1}
FIXTURES = "FIXTURES"
FIXTURE_ROLES = ("delayed-return-same-object", "prior-set-complement-reference",
                 "replacement-event-lineage", "ability-borrowing-inheritance-pressure",
                 "two-sequential-operations")
PASS, FAIL, INCONCLUSIVE = "PASS", "FAIL", "INCONCLUSIVE"
WORDS = (PASS, FAIL, INCONCLUSIVE)
YES, NO, CANNOT = "yes", "no", "cannot-judge"
CELLS = (YES, NO, CANNOT)
NONE = "none"
LEDGER_HEAD = ["row", "class", "endpoint", "kind", "duplicate", "note"]
LEDGER_LINE = "| " + " | ".join(LEDGER_HEAD) + " |"
COUNTS = ("rows", "endpoint-no", "kind-no", "duplicate-no", "cannot-judge")
QUOTE_WORDS = 12
REASON_WORDS = 2

SHA_LINE = re.compile(r"^refs\.json sha256: ([0-9a-f]{64})$")
SHA_MENTION = re.compile(r"refs\.json sha256", re.I)
LABEL = r"E[1-5]/P[0-9]+|E[1-5]|FIXTURES"
COUNTS_RX = r"\(" + ", ".join(rf"{w} (\d+)" for w in COUNTS) + r"\)"
VERDICT_LINE = re.compile(rf"^- ({LABEL}): (\S+) {COUNTS_RX}; (\S.*)$")
VERDICT_WORD = r"PASS|FAIL|INCONCLUSIVE"
# A line that reads as a verdict line for some label: any leading spaces,
# quote or list markers, emphasis or code markup around the label, a colon
# followed by a space, the line end or a verdict word. A class ('E4:it',
# 'E1:exile') is not a label: its colon is followed by a letter.
VERDICT_LIKE = re.compile(rf"^[\s>]*(?:(?:[-*+]|\d+[.)])\s+)*[*_`]*({LABEL})[*_`]*\s*:"
                          rf"(?=\s|$|[*_`]*(?:{VERDICT_WORD}))", re.I)
LABEL_WORD = re.compile(rf"(?<![A-Za-z0-9/])({LABEL})[^A-Za-z0-9]{{0,6}}({VERDICT_WORD})"
                        rf"(?![A-Za-z0-9])", re.I)
ADDRESS = (r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
           r":[0-9]+:[0-9]+:[0-9]+(?:@[0-9]+)?")
FORBIDDEN = re.compile(r"<!--|-->|<[A-Za-z/!]")
FORBIDDEN_RAW = re.compile(r"\]\(|\]:|&|\\")
FORBIDDEN_RAW_NAMES = {"](": "a Markdown link target ']('",
                       "]:": "a link reference ']:'",
                       "&": "an HTML entity marker '&'",
                       "\\": "a backslash"}
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def halt(msg: str):
    sys.stderr.write(f"HALT: {msg}\n")
    raise SystemExit(1)


# ------------------------------------------------------------- hand-off rule

def _run(args: list) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable] + args, cwd=str(ROOT), capture_output=True)


def obtain(root: Path = None, run=None) -> str:
    """The verified refs.json's sha256. An existing refs.json is checked by
    `c04_refs.py --verify` first, and stale STOPs; a missing one is regenerated
    only by `c04_refs.py --check-determinism`, unchanged."""
    root = ROOT if root is None else root
    run = _run if run is None else run
    script, art = str(root / C04_SCRIPT), root / REFS_REL
    if not art.exists():
        p = run([script, "--check-determinism"])
        if p.returncode != 0 or not art.exists():
            sys.stderr.write(p.stderr.decode("utf-8", "replace"))
            halt(f"{C04_SCRIPT} --check-determinism could not regenerate the missing "
                 f"{REFS_REL}")
    p = run([script, "--verify"])
    if p.returncode != 0:
        halt(f"stale C04 input: {REFS_REL} ({C04_SCRIPT} --verify): "
             f"{p.stderr.decode('utf-8', 'replace').strip()} -- a STOP")
    return hashlib.sha256(art.read_bytes()).hexdigest()


def load() -> tuple:
    """(refs.json candidates, sha256), after the hand-off rule."""
    sha = obtain()
    doc = json.loads((ROOT / REFS_REL).read_text(encoding="utf-8"))
    return doc["candidates"], sha


# ------------------------------------------------------------- the read set

def _key(r: dict) -> tuple:
    return (r["class"] or "", r["row_id"])


def rule_rows(rows: list, rule: str) -> list:
    """§I5.4: the rule's RESOLVED rows (E5: NOT-COREFERENCE), by (class, row_id)."""
    if rule not in PARTS:
        raise ValueError(f"no M05 rule {rule!r}")
    want = "NOT-COREFERENCE" if rule == "E5" else "RESOLVED"
    return sorted((r for r in rows if r["rule"] == rule and r["outcome"] == want), key=_key)


def part_rows(rows: list, rule: str, k: int) -> list:
    """Part k (1-based) of the rule: rows [floor((k-1)n/P), floor(kn/P))."""
    p = PARTS[rule]
    if not 1 <= k <= p:
        raise ValueError(f"{rule} has parts 1-{p}, not {k}")
    rr = rule_rows(rows, rule)
    n = len(rr)
    return rr[((k - 1) * n) // p:(k * n) // p]


def fixture_rows(rows: list) -> list:
    """§I5.4: every candidate in the five fixture roles, by (class, row_id)."""
    return sorted((r for r in rows if r["fixture_role"] in FIXTURE_ROLES), key=_key)


def class_text(r: dict) -> str:
    return r["class"] if r["class"] is not None else NONE


def skeleton(rows: list, sha: str) -> str:
    out = [f"refs.json sha256: {sha}", "", "| " + " | ".join(LEDGER_HEAD) + " |",
           "|" + "---|" * len(LEDGER_HEAD)]
    out += [f"| {r['row_id']} | {class_text(r)} |  |  |  |  |" for r in rows]
    return "\n".join(out)


def verdict_of(counts: dict) -> str:
    """PART / RULE / FIXTURES VERDICT precedence."""
    if counts["endpoint-no"]:
        return FAIL
    if counts["cannot-judge"] * 20 > counts["rows"]:
        return INCONCLUSIVE
    return PASS


# ------------------------------------------------------------- parsing

def _cell(s: str) -> str:
    """A table cell as written: only the padding whitespace is removed, never
    code or emphasis markup -- the row, class and verdict cells are literal."""
    return s.strip()


def _split(line: str) -> list:
    return [_cell(c) for c in line.strip().strip("|").split("|")]


def _fenced(lines: list) -> list:
    """Per line: inside (or delimiting) a fenced code block."""
    out, fence = [], None
    for line in lines:
        m = FENCE.match(line)
        if fence is not None:
            out.append(True)
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
                fence = None
            continue
        if m:
            fence = m.group(1)
            out.append(True)
            continue
        out.append(False)
    return out


def tables(lines: list, fenced: list) -> tuple:
    """Every pipe block outside code fences. Returns (tables, orphans): each
    table is (header line no, raw header line, header cells, [(line no,
    cells)]); an orphan is (line no, raw line) for every pipe line of a block
    that is no table (no header and separator row: e.g. a row detached from
    its table by a blank line)."""
    out, orphans, block = [], [], []
    for n, (line, f) in enumerate(list(zip(lines, fenced)) + [("", False)], 1):
        if not f and line.strip().startswith("|"):
            block.append((n, line))
            continue
        if block:
            sep = _split(block[1][1]) if len(block) >= 2 else []
            if sep and all(re.fullmatch(r":?-{3,}:?", c) for c in sep):
                out.append((block[0][0], block[0][1], _split(block[0][1]),
                            [(m, _split(l)) for m, l in block[2:]]))
            else:
                orphans += block
        block = []
    return out, orphans


def _ledger_like(head: list) -> bool:
    """A header that names the ledger's columns, whatever its markup or case."""
    return [re.sub(r"[`*_\s]", "", c).lower() for c in head] == LEDGER_HEAD


def _row_shaped(line: str, row_ids: set) -> bool:
    """A pipe line whose first cell names a row (a row_id or a row address)."""
    if "|" not in line:
        return False
    first = re.sub(r"^[\s>]*\|?", "", line).split("|")[0].strip().strip("`*_ ")
    return first in row_ids or re.match(ADDRESS, first) is not None


def sections(lines: list, fenced: list, title: str) -> list:
    """[(first, last)] 0-based body line spans of each '## <title>' section."""
    heads = [n for n, (l, f) in enumerate(zip(lines, fenced))
             if not f and re.fullmatch(rf"## {re.escape(title)}[ \t]*", l)]
    out = []
    for h in heads:
        end = next((n for n in range(h + 1, len(lines))
                    if not fenced[n] and lines[n].startswith("## ")), len(lines))
        out.append((h + 1, end - 1))
    return out


def marker_failures(text: str) -> list:
    """(A) and (A3), one plain-English failure per offending raw line."""
    bad = []
    for n, line in enumerate(text.split("\n"), 1):
        hits = list(dict.fromkeys(m.group() for m in FORBIDDEN.finditer(line)))
        if hits:
            bad.append(f"line {n} contains {' and '.join(repr(h) for h in hits)}: HTML tags "
                       f"and HTML comments are not allowed anywhere in an M05 document, "
                       f"not even in code spans or fences; write e.g. '[verb]', not '<verb>'")
        hits = list(dict.fromkeys(m.group() for m in FORBIDDEN_RAW.finditer(line)))
        if hits:
            what = " and ".join(FORBIDDEN_RAW_NAMES[h] for h in hits)
            bad.append(f"line {n} contains {what}: Markdown links, link references, HTML "
                       f"entities and backslashes are not allowed anywhere in an M05 "
                       f"document; rewrite the line in plain text (write 'and' for '&')")
    return bad


def sha_failures(lines: list, sha: str) -> tuple:
    """Exactly one `refs.json sha256: <hex>` line, equal to `sha`. Returns
    (failures, cited sha or None)."""
    bad, cited = [], []
    for n, line in enumerate(lines, 1):
        m = SHA_LINE.match(line)
        if m:
            cited.append((n, m.group(1)))
        elif SHA_MENTION.search(line) and re.search(r"[0-9a-f]{64}", line):
            bad.append(f"line {n} cites a refs.json sha256 but is not exactly "
                       f"'refs.json sha256: <64 hex>'")
    if len(cited) != 1:
        bad.append(f"the document has {len(cited)} lines 'refs.json sha256: <64 hex>'; "
                   f"exactly one is required")
    for n, s in cited:
        if sha is not None and s != sha:
            bad.append(f"line {n} cites refs.json sha256 {s}, but the verified refs.json "
                       f"is {sha}")
    return bad, (cited[0][1] if len(cited) == 1 else None)


def _quotes(note: str) -> list:
    return re.findall(r'"([^"]*)"', note)


def note_failures(n: int, rid: str, note: str, row: dict, cells: list) -> list:
    bad = []
    texts = [t for t in (row.get("paragraph_text"), row.get("endpoint_text"),
                         row.get("face_text")) if t]
    quotes = _quotes(note)
    ok = [q for q in quotes if q.strip() and len(q.split()) <= QUOTE_WORDS
          and any(q in t for t in texts)]
    if not quotes:
        bad.append(f"line {n}: row {rid}: the note quotes no phrase in double quotes; every "
                   f"note quotes a phrase of at most {QUOTE_WORDS} words from the row's "
                   f"texts")
    elif not ok:
        bad.append(f"line {n}: row {rid}: no double-quoted phrase in the note is at most "
                   f"{QUOTE_WORDS} words and found verbatim in the row's paragraph_text, "
                   f"endpoint_text or face_text")
    for q in quotes:
        if len(q.split()) > QUOTE_WORDS:
            bad.append(f"line {n}: row {rid}: a quoted phrase has {len(q.split())} words; "
                       f"at most {QUOTE_WORDS} (no card data in git)")
    if any(c in (NO, CANNOT) for c in cells):
        rest = re.sub(r'"[^"]*"', " ", note)
        if len(re.findall(r"[A-Za-z][A-Za-z'-]*", rest)) < REASON_WORDS:
            bad.append(f"line {n}: row {rid}: a no or cannot-judge cell needs its reason in "
                       f"the note, outside the quoted phrase")
    return bad


def ledger(lines: list, fenced: list, rows: list) -> tuple:
    """Check the ledger against the document's rows. Returns (failures,
    counts, {row_id: (cells)})."""
    bad = []
    found, orphans = tables(lines, fenced)
    want = {r["row_id"]: r for r in rows}
    hit = [t for t in found if _ledger_like(t[2])]
    if len(hit) != 1:
        bad.append(f"the document has {len(hit)} tables headed {LEDGER_LINE}; exactly one "
                   f"is required")
        return bad, None, {}
    hn, hraw, _, body = hit[0]
    if hraw != LEDGER_LINE:
        bad.append(f"line {hn}: the ledger header {hraw!r} is not exactly {LEDGER_LINE!r} "
                   f"(no code or emphasis markup, no other spacing)")
    # Every row is judged in the ledger only: a row-shaped pipe line anywhere
    # else (detached by a blank line, in another table, in a fence) fails, as
    # does any pipe line that belongs to no table.
    inside = {hn, hn + 1} | {n for n, _ in body}
    for n, line in enumerate(lines, 1):
        if n not in inside and _row_shaped(line, set(want)):
            bad.append(f"line {n}: a ledger row outside the ledger table (detached from it by "
                       f"a blank line, or in another table or a code block); every row is "
                       f"judged once, in the one ledger table")
    shaped = {n for n, line in enumerate(lines, 1) if _row_shaped(line, set(want))}
    for n, _ in orphans:
        if n not in shaped:
            bad.append(f"line {n}: a table row that belongs to no table (no header and "
                       f"separator row above it)")
    seen, order, cells_of = {}, [], {}
    for n, cells in body:
        if len(cells) != len(LEDGER_HEAD):
            bad.append(f"line {n}: a ledger row has {len(cells)} cells, not "
                       f"{len(LEDGER_HEAD)}")
            continue
        rid, cls, ep, kd, dup, note = cells
        seen[rid] = seen.get(rid, 0) + 1
        if rid not in want:
            plain = re.sub(r"[`*_]", "", rid)
            bad.append(f"line {n}: row {rid} is written in code or emphasis markup; write "
                       f"the row_id plain" if plain in want and plain != rid else
                       f"line {n}: row {rid} is not a row of this document (a foreign row)")
            continue
        if seen[rid] > 1:
            bad.append(f"line {n}: row {rid} appears {seen[rid]} times; exactly once")
            continue
        order.append(rid)
        row = want[rid]
        if cls != class_text(row):
            bad.append(f"line {n}: row {rid}: class {cls!r}, refs.json's is "
                       f"{class_text(row)!r}" + (" (a null class is written none)"
                                                 if row["class"] is None else ""))
        for name, v in (("endpoint", ep), ("kind", kd), ("duplicate", dup)):
            if v not in CELLS:
                bad.append(f"line {n}: row {rid}: {name} cell {v!r} is not exactly yes, no "
                           f"or cannot-judge")
        cells_of[rid] = (ep, kd, dup)
        bad += note_failures(n, rid, note, row, [ep, kd, dup])
    for r in rows:
        if r["row_id"] not in seen:
            bad.append(f"the ledger omits row {r['row_id']}")
    want_order = [r["row_id"] for r in rows if r["row_id"] in cells_of]
    if order != want_order and sorted(order) == sorted(want_order):
        bad.append("the ledger rows are not in skeleton order (class, row_id)")
    vals = list(cells_of.values())
    counts = {"rows": len(vals), "endpoint-no": sum(c[0] == NO for c in vals),
              "kind-no": sum(c[1] == NO for c in vals),
              "duplicate-no": sum(c[2] == NO for c in vals),
              "cannot-judge": sum(CANNOT in c for c in vals)}
    return bad, counts, cells_of


def canonical(lines: list, fenced: list, labels: tuple, bad: list) -> dict:
    """{label: (line index, word, counts)} for the canonical verdict lines of
    `labels`, each required exactly once under '## Verdict' outside a fence;
    every other verdict-like line for any label fails."""
    spans = sections(lines, fenced, "Verdict")
    if len(spans) != 1:
        bad.append(f"the document has {len(spans)} sections headed '## Verdict'; exactly "
                   f"one is required")
    span = spans[0] if len(spans) == 1 else None
    found = {}
    for i, line in enumerate(lines):
        m = VERDICT_LIKE.match(line)
        if not m:
            continue
        label = m.group(1).upper()
        c = VERDICT_LINE.match(line)
        inside = bool(span and span[0] <= i <= span[1]) and not fenced[i]
        if label not in labels:
            bad.append(f"line {i + 1}: {line.strip()!r} is a verdict line for {label}, which "
                       f"this document does not carry")
            continue
        if not c or not inside:
            why = ("is not in the canonical form '- " + label + ": WORD (rows n, "
                   "endpoint-no n, kind-no n, duplicate-no n, cannot-judge n); text'"
                   if not c else "is outside '## Verdict' or inside a code block")
            bad.append(f"line {i + 1}: {line.strip()!r} reads as a verdict line for {label} "
                       f"but {why}")
            continue
        if label in found:
            bad.append(f"line {i + 1}: a second verdict line for {label} (the first is line "
                       f"{found[label][0] + 1}); exactly one is allowed")
            continue
        if c.group(2) not in WORDS:
            bad.append(f"line {i + 1}: verdict word {c.group(2)!r} is not PASS, FAIL or "
                       f"INCONCLUSIVE")
        found[label] = (i, c.group(2), dict(zip(COUNTS, map(int, c.group(3, 4, 5, 6, 7)))))
    for label in labels:
        if label not in found:
            bad.append(f"'## Verdict' has no canonical line '- {label}: WORD (rows n, "
                       f"endpoint-no n, kind-no n, duplicate-no n, cannot-judge n); text'")
    return found


def scan_failures(text: str, agree: dict, row_ids: list = ()) -> list:
    """(A2) Anywhere in the raw text, across line breaks: a label followed
    within six non-alphanumeric characters by a verdict word must be a label in
    `agree` and say its word; a row address or row_id so followed must say
    agree['*'] (the document's own word)."""
    bad, lines = [], text.split("\n")

    def line_of(pos):
        return text.count("\n", 0, pos) + 1

    for m in LABEL_WORD.finditer(text):
        label, said = m.group(1).upper(), m.group(2).upper()
        n = line_of(m.start())
        if label not in agree:
            bad.append(f"line {n}: {label} is followed by the verdict word {m.group(2)!r}, "
                       f"but this document carries no verdict for {label} "
                       f"({lines[n - 1].strip()!r})")
        elif agree[label] is not None and said != agree[label]:
            bad.append(f"line {n}: {label} is followed by {m.group(2)!r}, but its canonical "
                       f"verdict is {agree[label]} ({lines[n - 1].strip()!r})")
    own = agree.get("*")
    pats = [re.escape(r) for r in sorted(set(row_ids), key=len, reverse=True)] + [ADDRESS]
    rx = re.compile(rf"(?<![A-Za-z0-9])(?:{'|'.join(pats)})[^A-Za-z0-9]{{0,6}}"
                    rf"({VERDICT_WORD})(?![A-Za-z0-9])", re.I)
    for m in rx.finditer(text):
        if own is not None and m.group(1).upper() != own:
            n = line_of(m.start())
            bad.append(f"line {n}: a row address is followed by {m.group(1)!r}, but the "
                       f"document's canonical verdict is {own} ({lines[n - 1].strip()!r})")
    return bad


def heading_failures(lines: list, fenced: list, title: str) -> list:
    k = len(sections(lines, fenced, title))
    return [] if k == 1 else [f"the document has {k} headings '## {title}'; exactly one is "
                              f"required"]


def document_failures(text: str, rows: list, sha: str, label: str = None) -> list:
    """Every failure of one read document. `rows` are the document's rows in
    skeleton order (a part's, or the fixture rows); `label` is 'E<r>/P<k>' or
    'FIXTURES' (read from the canonical line when not given)."""
    lines = text.split("\n")
    fenced = _fenced(lines)
    bad = marker_failures(text)
    bad += sha_failures(lines, sha)[0]
    lbad, counts, cells_of = ledger(lines, fenced, rows)
    bad += lbad
    if label is None:
        got = sorted({VERDICT_LINE.match(l).group(1) for l in lines if VERDICT_LINE.match(l)})
        label = got[0] if len(got) == 1 else None
        if label is None:
            bad.append("the document's label (E<r>/P<k> or FIXTURES) cannot be read from "
                       "exactly one canonical verdict line")
            return bad
    found = canonical(lines, fenced, (label,), bad)
    word = None
    if label in found:
        i, word, said = found[label]
        if counts is not None:
            for k in COUNTS:
                if said[k] != counts[k]:
                    bad.append(f"line {i + 1}: {label} states {k} {said[k]}, the ledger has "
                               f"{counts[k]}")
            want = verdict_of(counts)
            if word in WORDS and word != want:
                bad.append(f"line {i + 1}: {label} says {word}, but the PART VERDICT "
                           f"precedence over the ledger gives {want} (FAIL when endpoint-no "
                           f"> 0; else INCONCLUSIVE when cannot-judge x 20 > rows; else PASS)")
            word = want
    agree = {label: word, "*": word}
    if label != FIXTURES:
        agree[label.split("/")[0]] = word
    bad += scan_failures(text, agree, [r["row_id"] for r in rows])
    if word == FAIL and counts is not None:
        spans = sections(lines, fenced, "Failing classes")
        if len(spans) != 1:
            bad.append(f"a FAIL needs exactly one '## Failing classes' section; the document "
                       f"has {len(spans)}")
        else:
            body = "\n".join(lines[spans[0][0]:spans[0][1] + 1])
            by_id = {r["row_id"]: r for r in rows}
            for rid, c in cells_of.items():
                if c[0] == NO:
                    cls = class_text(by_id[rid])
                    if cls not in body:
                        bad.append(f"'## Failing classes' does not name the failing class "
                                   f"{cls}")
                    if rid not in body:
                        bad.append(f"'## Failing classes' does not list the failing row {rid}")
    bad += heading_failures(lines, fenced, "Captain questions")
    return list(dict.fromkeys(bad))


def parse_document(text: str, rows: list, label: str) -> dict:
    """The part a (checked) document states: its cited sha256, ledger row_ids
    and counts, and the verdict its ledger gives."""
    lines = text.split("\n")
    fenced = _fenced(lines)
    _, cited = sha_failures(lines, None)
    hit = [t for t in tables(lines, fenced)[0] if _ledger_like(t[2])]
    ids = [c[0] for _, c in hit[0][3] if len(c) == len(LEDGER_HEAD)] if len(hit) == 1 else []
    _, counts, _ = ledger(lines, fenced, rows)
    return {"label": label, "sha": cited, "rows": ids, "counts": counts,
            "word": verdict_of(counts) if counts else None}


# ------------------------------------------------------------- aggregation

def aggregate(parts: list) -> dict:
    """RULE VERDICT over parts ({label, sha, rows, counts}): summed counts and
    the same precedence; failures for overlapping rows or differing sha256."""
    bad = []
    shas = sorted({p["sha"] for p in parts})
    if len(shas) != 1 or shas[0] is None:
        bad.append(f"the part documents cite {len(shas)} refs.json sha256 values "
                   f"({', '.join(str(s) for s in shas)}); every document cites the same one")
    seen = {}
    for p in parts:
        for rid in p["rows"]:
            if rid in seen:
                bad.append(f"row {rid} is in both {seen[rid]} and {p['label']}; parts must "
                           f"not overlap")
            seen.setdefault(rid, p["label"])
    counts = {k: sum((p["counts"] or {}).get(k, 0) for p in parts) for k in COUNTS}
    return {"counts": counts, "word": verdict_of(counts), "failures": bad,
            "sha": shas[0] if len(shas) == 1 else None}


def rule_failures(parts: list, rows: list, rule: str) -> tuple:
    """--rule: the parts must be parts 1..P of `rule` and partition its rows
    exactly. Returns (failures, aggregate)."""
    agg = aggregate(parts)
    bad = list(agg["failures"])
    labels = [p["label"] for p in parts]
    want_labels = [f"{rule}/P{k}" for k in range(1, PARTS[rule] + 1)]
    if sorted(labels) != sorted(want_labels):
        bad.append(f"{rule} has parts {', '.join(labels)}; it needs exactly "
                   f"{', '.join(want_labels)}")
    got = [rid for p in parts for rid in p["rows"]]
    want = [r["row_id"] for r in rule_rows(rows, rule)]
    unread = [rid for rid in want if rid not in got]
    for rid in unread[:10]:
        bad.append(f"no part reads {rule} row {rid}; the parts must cover the rule")
    if len(unread) > 10:
        bad.append(f"... and {len(unread) - 10} more {rule} rows no part reads "
                   f"({len(unread)} in all)")
    for rid in sorted(set(got) - set(want)):
        bad.append(f"row {rid} is not a {rule} read-set row")
    return bad, agg


def rule_line(label: str, agg: dict) -> str:
    c = agg["counts"]
    return (f"- {label}: {agg['word']} (" + ", ".join(f"{k} {c[k]}" for k in COUNTS)
            + ")")


def summary_failures(text: str, aggs: dict, sha: str) -> list:
    """M05-SUMMARY.md against {label: aggregate} for E1-E5 and FIXTURES."""
    lines = text.split("\n")
    fenced = _fenced(lines)
    bad = marker_failures(text)
    sbad, cited = sha_failures(lines, sha)
    bad += sbad
    for label, a in aggs.items():
        if a.get("sha") is not None and cited is not None and a["sha"] != cited:
            bad.append(f"the summary cites refs.json sha256 {cited}, but the {label} "
                       f"documents cite {a['sha']}; every document cites the same one")
    labels = tuple(list(PARTS) + [FIXTURES])
    found = canonical(lines, fenced, labels, bad)
    agree = {}
    for label in labels:
        a = aggs.get(label)
        agree[label] = a["word"] if a else None
        if label not in found or a is None:
            if a is None:
                bad.append(f"no aggregate for {label}")
            continue
        i, word, said = found[label]
        for k in COUNTS:
            if said[k] != a["counts"][k]:
                bad.append(f"line {i + 1}: {label} states {k} {said[k]}, the aggregate has "
                           f"{a['counts'][k]}")
        if word != a["word"]:
            bad.append(f"line {i + 1}: {label} says {word}, the aggregate gives {a['word']}")
    for label, a in aggs.items():
        for p in a.get("parts", []):
            agree[p["label"]] = p["word"]
    bad += scan_failures(text, agree)
    bad += heading_failures(lines, fenced, "Captain questions")
    return list(dict.fromkeys(bad))


# ------------------------------------------------------------- CLI

def _doc_rel(rule: str, k: int) -> str:
    return f"{ANALYSIS}/M05-{rule}-P{k}-READ.md"


def _label_of(path: str):
    name = Path(path).name
    m = re.fullmatch(r"M05-(E[1-5])-P([0-9]+)-READ\.md", name)
    if m:
        return f"{m.group(1)}/P{m.group(2)}", m.group(1), int(m.group(2))
    if name == Path(FIXTURES_REL).name:
        return FIXTURES, None, None
    return None, None, None


def _doc_rows(rows: list, rule, k) -> list:
    return fixture_rows(rows) if rule is None else part_rows(rows, rule, k)


def _report(bad: list, ok: str) -> int:
    for b in bad:
        print(f"FAIL: {b}", file=sys.stderr)
    if bad:
        return 1
    print(ok)
    return 0


def _read(rel: str):
    p = ROOT / rel
    return p.read_text(encoding="utf-8") if p.exists() else None


def _rule_parts(rows: list, rule: str, sha: str) -> tuple:
    bad, parts = [], []
    for k in range(1, PARTS[rule] + 1):
        rel = _doc_rel(rule, k)
        text = _read(rel)
        if text is None:
            bad.append(f"{rel} does not exist")
            continue
        prow = part_rows(rows, rule, k)
        bad += [f"{rel}: {b}" for b in document_failures(text, prow, sha, f"{rule}/P{k}")]
        parts.append(parse_document(text, prow, f"{rule}/P{k}"))
    rbad, agg = rule_failures(parts, rows, rule)
    agg["parts"] = parts
    return bad + rbad, agg


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--protocol", action="store_true")
    ap.add_argument("--skeleton", action="store_true")
    ap.add_argument("--fixtures", action="store_true")
    ap.add_argument("--rule", choices=sorted(PARTS))
    ap.add_argument("--part", type=int)
    ap.add_argument("--doc")
    ap.add_argument("--summary", action="store_true")
    a = ap.parse_args(argv)
    if a.protocol:
        sys.stdout.write(PROTOCOL)
        return 0
    if hashlib.sha256(PROTOCOL.encode("utf-8")).hexdigest() != PROTOCOL_SHA256:
        halt("PROTOCOL is not the commanded M05 READING PROTOCOL (sha256 differs)")
    if a.skeleton:
        if a.fixtures == bool(a.rule):
            ap.error("--skeleton needs --fixtures, or --rule with --part")
        rows, sha = load()
        if a.fixtures:
            print(skeleton(fixture_rows(rows), sha))
            return 0
        if a.part is None:
            ap.error("--skeleton --rule needs --part")
        print(skeleton(part_rows(rows, a.rule, a.part), sha))
        return 0
    if a.doc:
        label, rule, k = _label_of(a.doc)
        if label is None or (rule and not 1 <= k <= PARTS[rule]):
            print(f"FAIL: {a.doc} is not named M05-<rule>-P<k>-READ.md or "
                  f"M05-FIXTURES-READ.md", file=sys.stderr)
            return 1
        rows, sha = load()
        text = Path(a.doc).read_text(encoding="utf-8")
        return _report(document_failures(text, _doc_rows(rows, rule, k), sha, label),
                       f"{a.doc}: consistent")
    if a.rule:
        rows, sha = load()
        bad, agg = _rule_parts(rows, a.rule, sha)
        return _report(bad, rule_line(a.rule, agg))
    if a.summary:
        rows, sha = load()
        bad, aggs = [], {}
        for rule in PARTS:
            rbad, aggs[rule] = _rule_parts(rows, rule, sha)
            bad += rbad
        text = _read(FIXTURES_REL)
        if text is None:
            bad.append(f"{FIXTURES_REL} does not exist")
        else:
            frows = fixture_rows(rows)
            bad += [f"{FIXTURES_REL}: {b}" for b in document_failures(text, frows, sha,
                                                                       FIXTURES)]
            fp = parse_document(text, frows, FIXTURES)
            aggs[FIXTURES] = dict(aggregate([fp]), parts=[])
        stext = _read(SUMMARY_REL)
        if stext is None:
            bad.append(f"{SUMMARY_REL} does not exist")
        else:
            bad += [f"{SUMMARY_REL}: {b}" for b in summary_failures(stext, aggs, sha)]
        return _report(bad, "\n".join(rule_line(k, v) for k, v in aggs.items()))
    ap.error("one of --protocol, --skeleton, --doc, --rule or --summary is required")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
