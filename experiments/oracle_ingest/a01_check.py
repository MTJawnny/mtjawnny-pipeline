#!/usr/bin/env python3
"""A01-CHECK — coverage and consistency checker for the Round-2 seam audits.

PINNED TO oracle-compiler-interface/3 (oracle_compiler/INTERFACES.md blob
119778a68c0e4e8378f0a117b7c22884ec5eda4b) through h_region.py's pin. It
decides no truth item and mints nothing: it checks that each audit document
covers the verified seams.json population exactly, uses only the five cell
words, honours the R2-A read rule, and states each verdict as the rule gives
it from the document's own ledger.

    R2-A  oracle_compiler/analysis/A01-R2A-REPLACEMENT-LINEAGE.md
    R2-B  oracle_compiler/analysis/A01-R2B-DECISION-AUTHORITY.md
    R2-C  oracle_compiler/analysis/A01-R2C-ABILITY-BORROWING.md

Per document it exits non-zero unless ALL hold:

  (a) it cites seams.json's sha256 (on a line whose every '*seams.json' token is
      an exact reference to the artifact: 'seams.json', or a path suffix of
      experiments/out/oracle_ingest/a01/seams.json), equal to the verified
      artifact, and no other sha256 on such a line;
  (b) its ledgers, each a table whose header row is exactly as given, cover the
      population exactly once and nothing else:
        R2-A `| class | members | read | A1 | A2 | A3 | A4 | A5 | note |`, one
          row per seams.json class, or for a SPLIT class one row per part
          '<class>/part-<k>' whose member list ('### <class>/part-<k>' under
          '## Splits', one four-coordinate address per line) is disjoint from
          the others and whose union is exactly the class; 'members' is the row
          size; '## Reads' lists, under '### <row>', the addresses read (each a
          member of the row, every READ POSITION of the class in the row
          included -- or, for a part holding none, its first member in
          seams.json order -- their count equal to 'read', read >= 1); and the recall
          table `| clause | class | A1 | A2 | A3 | A4 | A5 | note |`, one row
          per recall control clause;
        R2-B `| clause | B1 | B2 | B3 | B4 | note |`, one row per member, and
          under '## Pronoun candidates' `| clause | membership | B1 | B2 | B3 |
          B4 | note |`, one row per pronoun candidate, MEMBER or NOT-MEMBER
          (NOT-MEMBER: '—' in every truth cell, excluded from totals), every
          note holding a double-quoted antecedent span;
        R2-C `| clause | C1 | C2 | C3 | C4 | note |`, one row per member;
      every truth cell (but a NOT-MEMBER '—') one of the five cell words;
  (c) R2-A read rule: an EXPRESSED A1/A2/A3/A5 cell has read == members or
      supports_A<n> true for every member of the row; an EXPRESSED A4 cell has
      read == members; read < members says 'inferred from <read> of <members>
      read' in the note;
  (d) '## Verdict': one line per truth item, '- <id>: <WORD> (EXPRESSED n,
      PARTIAL n, NOT-EXPRESSED n, UNRESOLVED n, OUT-OF-CONTRACT n)', counts
      equal to the ledger's (R2-A: class/part rows; R2-B: members plus MEMBER
      pronoun rows) and WORD as VERDICT RULE gives it; a SUFFICES line carries
      a status phrase, and the CANDIDATE phrase whenever it cites AQ4 §9 rungs
      2-5, §12, §13 or §16. Captain decision 6002030055 (A2), repair verdict
      6002198078: exactly one canonical verdict line per truth item, in item
      order, in exactly that form (single spaces; any further text only after
      '; '), and no '- ID:' line for a truth item anywhere outside '## Verdict';
      and anywhere in the document (raw lines, fences included, across line
      breaks) a truth id followed within six non-alphanumeric characters by a
      verdict word other than VERDICT RULE's fails, naming the line;
  (e) a section headed exactly '## Captain questions'.

NO HTML, NO COMMENTS (Captain decision 5987664829). A document fails if any
line, anywhere -- prose, table, heading, code span or code fence alike --
holds '<!--', '-->', or '<' immediately followed by an ASCII letter, '/' or
'!'; each such line is reported by number in plain English. Nothing is
interpreted as HTML or as a comment: Markdown is classified on the unmodified
lines, and only fenced code blocks (``` or ~~~) and indented code blocks are
set aside, so a heading, table, list or citation inside one does not exist. A
seams.json reference is the whole whitespace-delimited word holding
'seams.json'.

HAND-OFF RULE. An existing seams.json is never trusted: it is first checked by
`a01_seams.py --verify`, and a stale report STOPs this checker. A missing one is
regenerated ONLY by invoking `a01_seams.py --check-determinism` unchanged (the
mode that writes it). That invocation is this script's only write.

    python3 experiments/oracle_ingest/a01_check.py               # all three
    python3 experiments/oracle_ingest/a01_check.py --doc PATH    # one document
    python3 experiments/oracle_ingest/a01_check.py --skeleton    # rows to fill
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))

import h_region as hr                        # noqa: E402  (sets sys.path)
import foundry_common as fc                  # noqa: E402
from m04_check import tables, _cell, _int, _row, _sep, _halts  # noqa: E402

SCRIPT = "experiments/oracle_ingest/a01_check.py"
SEAMS_SCRIPT = "experiments/oracle_ingest/a01_seams.py"
SEAMS_REL = "experiments/out/oracle_ingest/a01/seams.json"
DOCS = {"R2-A": "oracle_compiler/analysis/A01-R2A-REPLACEMENT-LINEAGE.md",
        "R2-B": "oracle_compiler/analysis/A01-R2B-DECISION-AUTHORITY.md",
        "R2-C": "oracle_compiler/analysis/A01-R2C-ABILITY-BORROWING.md"}
ITEMS = {"R2-A": ("A1", "A2", "A3", "A4", "A5"),
         "R2-B": ("B1", "B2", "B3", "B4"),
         "R2-C": ("C1", "C2", "C3", "C4")}

EXPRESSED, PARTIAL, NOT_EXPRESSED = "EXPRESSED", "PARTIAL", "NOT-EXPRESSED"
UNRESOLVED, OUT_OF_CONTRACT = "UNRESOLVED", "OUT-OF-CONTRACT"
WORDS = (EXPRESSED, PARTIAL, NOT_EXPRESSED, UNRESOLVED, OUT_OF_CONTRACT)
SUFFICES, MISSING, UNDETERMINED = "SUFFICES", "GENUINELY_MISSING", "UNDETERMINED"
VERDICTS = (SUFFICES, MISSING, UNDETERMINED)
MEMBER, NOT_MEMBER, DASH = "MEMBER", "NOT-MEMBER", "—"

# The status phrases a SUFFICES line may rest on; the first is required
# whenever the line cites AQ4 §9 rungs 2-5, §12, §13 or §16.
CANDIDATE = "CANDIDATE benchmark structure"
I3A = "oracle-compiler-interface/3 §I3a (ratified measurement interface"
RUNG1 = "AQ4 §9 rung 1 (ratified, §11 law)"
STATUS_PHRASES = (CANDIDATE, I3A, RUNG1)

# Each table a document must carry, by the exact cells of its header row.
R2A_HEAD = ["class", "members", "read"] + list(ITEMS["R2-A"]) + ["note"]
R2A_RECALL_HEAD = ["clause", "class"] + list(ITEMS["R2-A"]) + ["note"]
R2B_HEAD = ["clause"] + list(ITEMS["R2-B"]) + ["note"]
PRONOUN_HEAD = ["clause", "membership"] + list(ITEMS["R2-B"]) + ["note"]
R2C_HEAD = ["clause"] + list(ITEMS["R2-C"]) + ["note"]

PART = re.compile(r"^(.+)/part-(\d+)$")
ADDR_LINE = re.compile(r"^\s*(?:[-*]\s+)?`?([^\s`:]+:\d+:\d+:\d+)`?\s*$")
QUOTED = re.compile(r'"[^"\n]+"|“[^”\n]+”')
SHA = re.compile(r"\b[0-9a-f]{64}\b")
# A reference to seams.json is the whole whitespace-delimited word holding it,
# so 'unrelated+seams.json' or 'unrelated@seams.json' is one foreign reference,
# never 'seams.json' with a prefix ignored.
SEAMS_TOKEN = re.compile(r"\S*seams\.json\S*")
WRAP_OPEN, WRAP_CLOSE = "`\"'([{<“‘", "`\"')]}>”’.,:;!?"
MD_LINK = re.compile(r"([^\[]*)\[([^\[\]\s]+)\]\(([^()\s]+)\)(.*)")
FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
# Captain decision 5987664829: these markers are forbidden on every line of an
# audit document, code spans and fences included; nothing is parsed as HTML.
FORBIDDEN = re.compile(r"<!--|-->|<[A-Za-z/!]")
VERDICT_ITEM = re.compile(r"^- ([A-Za-z]\d+):")
# Captain decision 6002030055 (A2), repair verdict 6002198078: the canonical
# line is exactly '- ID: WORD (five counts)', optionally followed by '; text'.
VERDICT_LINE = re.compile(
    r"^- ([A-Za-z]\d+): (\S+) \(" + ", ".join(rf"{w} (\d+)" for w in WORDS)
    + r"\)(?:; (\S.*))?$")
# A verdict word, as a reader would take it: any case, 'GENUINELY MISSING' or
# 'GENUINELY-MISSING' as well as the canonical underscore form.
VERDICT_WORD = r"SUFFICES|GENUINELY[^A-Za-z0-9]{0,3}MISSING|UNDETERMINED"
# A line that reads as a verdict but is not in the canonical column-zero form:
# indented, quoted, another list marker, an emphasised or code-spanned id, a
# space before the colon -- or any line stating a verdict word with its counts.
# Such a line is rejected, never skipped (repair verdict 5988024375).
VERDICT_LIKE = re.compile(
    r"^[\s>]*(?:(?:[-*+]|\d+[.)])\s*)?[*_`]*\s*[A-Za-z]\d+\s*[*_`]*\s*:"
    r"|\b(?:" + "|".join(re.escape(w) for w in ("SUFFICES", "GENUINELY_MISSING",
                                                 "UNDETERMINED")) + r")\W*\(\s*EXPRESSED\b")
# Repair verdict 5988156977: an id wrapped in a Markdown link ('[C2](#c2):'),
# behind nested list markers ('- - C2:', '  * > C2:'), and a count statement
# ('NOT-EXPRESSED 2') anywhere outside a canonical line's own counts -- so a
# verdict whose counts are wrapped onto the next line -- are verdict-like too.
LINK_TARGET = re.compile(r"\]\s*(?:\([^)]*\)|\[[^\]]*\])")
MARKUP = re.compile(r"[\[\]*_`~\\]")
LEAD_MARKERS = re.compile(r"^(?:\s|>|(?:[-+]|\d+[.)])(?=\s|$))*")
ID_COLON = re.compile(r"^[A-Za-z]\d+\s*[:：]")
COUNT_STATEMENT = re.compile(
    r"(?<![\w-])(?:" + "|".join(re.escape(w) for w in WORDS) + r")\s*[:=]?\s*\d")


def verdict_like(line: str) -> bool:
    """True for a line that states, or carries part of, a verdict: any
    VERDICT_LIKE form, an id followed by a colon once Markdown link, emphasis
    and code markup and any number of leading list or quote markers are set
    aside, or a count statement of a cell word."""
    if VERDICT_LIKE.search(line) or COUNT_STATEMENT.search(line):
        return True
    bare = LEAD_MARKERS.sub("", MARKUP.sub("", LINK_TARGET.sub("]", line)))
    return bool(ID_COLON.match(bare))
CANDIDATE_CITE = re.compile(r"§\s*1[236]\b")
RUNG_CITE = re.compile(r"\brungs?\s+(\d+(?:\s*(?:-|–|,|and|to)\s*\d+)*)", re.I)


# ------------------------------------------------------------- hand-off rule

def _run(args: list) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable] + args, cwd=str(ROOT), capture_output=True)


def obtain(root: Path = None, run=None) -> str:
    """The verified seams.json's sha256. An existing one is checked by
    `a01_seams.py --verify` first, and stale STOPs; a missing one is
    regenerated only by `a01_seams.py --check-determinism`. `root` and `run`
    exist only so the negative controls can rig the hand-off."""
    root = ROOT if root is None else root
    run = _run if run is None else run
    script, art = str(root / SEAMS_SCRIPT), root / SEAMS_REL
    if not art.exists():
        p = run([script, "--check-determinism"])
        if p.returncode != 0:
            sys.stderr.write(p.stderr.decode("utf-8", "replace"))
            fc.halt(f"{SEAMS_SCRIPT} --check-determinism could not regenerate the "
                    f"missing {SEAMS_REL}")
        if not art.exists():
            fc.halt(f"{SEAMS_SCRIPT} --check-determinism exited 0 but did not write "
                    f"{SEAMS_REL}")
    p = run([script, "--verify"])
    if p.returncode != 0:
        fc.halt(f"stale seams input: {SEAMS_REL} ({SEAMS_SCRIPT} --verify): "
                f"{p.stderr.decode('utf-8', 'replace').strip()}")
    return hashlib.sha256(art.read_bytes()).hexdigest()


def load() -> tuple:
    """(seams_doc, sha256), after the hand-off rule and the interface pin."""
    sha = obtain()
    doc = json.loads((ROOT / SEAMS_REL).read_text(encoding="utf-8"))
    blob = hr.verify_interface()
    if doc.get("interface", {}).get("version") != hr.INTERFACE_VERSION or \
            doc["interface"].get("blob") != blob:
        fc.halt(f"{SEAMS_REL} was derived under {doc.get('interface')}, not "
                f"{hr.INTERFACE_VERSION} ({blob})")
    return doc, sha


# ---------------------------------------------------------- document parsing

def markup_failures(text: str) -> list:
    """One plain-English failure per line holding an HTML or comment marker
    ('<!--', '-->', or '<' followed by an ASCII letter, '/' or '!'), wherever it
    sits: prose, table, heading, code span or code fence alike."""
    bad = []
    for n, line in enumerate(text.split("\n"), 1):
        hits = list(dict.fromkeys(m.group() for m in FORBIDDEN.finditer(line)))
        if hits:
            bad.append(f"line {n} contains {' and '.join(repr(h) for h in hits)}: HTML tags "
                       f"and HTML comments are not allowed anywhere in an audit document, "
                       f"not even inside code spans or code fences; rewrite the line "
                       f"without them (for a placeholder write e.g. 'VERB' or '[verb]', "
                       f"not '<verb>')")
    return bad


def structure(text: str) -> str:
    """The document with every line inside a fenced code block (delimiters
    included; an unclosed fence runs to the end) or an indented code block (a
    run of lines indented four or more columns that opens after a blank line)
    blanked, line count kept. Every other line is returned unmodified: nothing
    is read as HTML or as a comment (markup_failures rejects both outright)."""
    lines, kept, fence, code, prev_blank = text.split("\n"), [], None, False, True
    for line in lines:
        blank = not line.strip()
        if fence is not None:
            if re.fullmatch(rf" {{0,3}}{re.escape(fence[0])}{{{len(fence)},}}[ \t]*", line):
                fence = None
            kept.append(False)
            continue
        m = FENCE_OPEN.match(line)
        if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
            fence = m.group(1)
            kept.append(False)
            prev_blank, code = False, False
            continue
        indented = re.match(r"^(?: {4}|\t| {0,3}\t)", line) is not None
        code = (not blank and indented and (prev_blank or code)) or (code and blank)
        kept.append(not code)
        prev_blank = blank
    return "\n".join(l if k else "" for l, k in zip(lines, kept))


def table(text: str, head: list, bad: list, where: str = "the document") -> list:
    """The rows of the one table whose header is `head` (wrong-width rows
    reported and dropped); [] and a failure unless exactly one exists."""
    hit = [rows for h, rows in tables(text) if h == head]
    if len(hit) != 1:
        bad.append(f"{where} has {len(hit)} tables headed | {' | '.join(head)} |; "
                   f"exactly one is required")
        return []
    for r in hit[0]:
        if len(r) != len(head):
            bad.append(f"table | {head[0]} | ...: row {r!r} has {len(r)} cells, not "
                       f"{len(head)}")
    return [r for r in hit[0] if len(r) == len(head)]


def headings(text: str, title: str) -> int:
    return len(re.findall(rf"^## {re.escape(title)}[ \t]*$", text, re.M))


def section(text: str, title: str, bad: list, required: bool = True):
    """The body of the one section headed exactly '## <title>', else None."""
    got = re.findall(rf"^## {re.escape(title)}[ \t]*\n(.*?)(?=^## |\Z)", text + "\n",
                     re.M | re.S)
    if len(got) > 1 or (required and not got):
        bad.append(f"the document has {len(got)} sections headed '## {title}'; exactly "
                   f"one is required")
        return None
    return got[0] if got else None


def address_lists(text: str, title: str, bad: list, required: bool) -> dict:
    """'### <name>' -> [addresses] under the section '## <title>'; any other
    non-blank line under a '###' heading, or a repeated heading, fails."""
    body = section(text, title, bad, required)
    out, cur = {}, None
    for line in (body or "").splitlines():
        m = re.match(r"^### (.+?)\s*$", line)
        if m:
            cur = _cell(m.group(1))
            if cur in out:
                bad.append(f"'## {title}' has more than one '### {cur}'")
            out[cur] = []
            continue
        if cur is None or not line.strip():
            continue
        a = ADDR_LINE.match(line)
        if a:
            out[cur].append(a.group(1))
        else:
            bad.append(f"'## {title}' / '### {cur}': line {line.strip()!r} is not one "
                       f"four-coordinate address")
    return out


def _once(keys: list, what: str, bad: list) -> None:
    for k in sorted(set(keys)):
        if keys.count(k) != 1:
            bad.append(f"{what} {k} {keys.count(k)} times; exactly once is required")


def _coverage(keys: list, want: list, what: str, kind: str, bad: list) -> None:
    _once(keys, f"the {what} lists", bad)
    for k in want:
        if k not in keys:
            bad.append(f"the {what} omits {kind} {k}")
    for k in sorted(set(keys) - set(want)):
        bad.append(f"the {what} lists {k}, which is not a seams.json {kind}")


def _words(label: str, cells: dict, bad: list) -> None:
    for item, w in cells.items():
        if w not in WORDS:
            bad.append(f"{label}: {item} {w!r} is not one of the five cell words "
                       f"({', '.join(WORDS)})")


# ------------------------------------------------------------- the verdicts

def verdict_word(counts: dict) -> str:
    """VERDICT RULE: GENUINELY_MISSING when any cell is NOT-EXPRESSED or
    PARTIAL; else SUFFICES when any is EXPRESSED; else (every cell UNRESOLVED or
    OUT-OF-CONTRACT) UNDETERMINED."""
    if counts[NOT_EXPRESSED] or counts[PARTIAL]:
        return MISSING
    return SUFFICES if counts[EXPRESSED] else UNDETERMINED


def cites_candidate(line: str) -> bool:
    """True when the line cites AQ4 §12, §13, §16 or a §9 rung 2-5."""
    if CANDIDATE_CITE.search(line):
        return True
    for m in RUNG_CITE.finditer(line):
        nums = []
        for lo, hi in re.findall(r"(\d+)(?:\s*(?:-|–|to)\s*(\d+))?", m.group(1)):
            nums += list(range(int(lo), int(hi or lo) + 1))
        if any(2 <= n <= 5 for n in nums):
            return True
    return False


def _verdict_span(text: str):
    """(first, last) 0-based line indices of the one '## Verdict' section's
    body in the structure text, else None."""
    lines = text.split("\n")
    heads = [n for n, l in enumerate(lines) if re.fullmatch(r"## Verdict[ \t]*", l)]
    if len(heads) != 1:
        return None
    end = next((n for n in range(heads[0] + 1, len(lines)) if lines[n].startswith("## ")),
               len(lines))
    return heads[0] + 1, end - 1


def stray_verdict_failures(raw: str, text: str, seam_id: str) -> list:
    """Exactly one canonical verdict line per truth item: a '- ID:' line for one
    of the seam's truth items anywhere outside '## Verdict' -- prose, another
    section, a code fence -- is a second verdict line and fails by number."""
    span, bad = _verdict_span(text), []
    for n, line in enumerate(raw.split("\n")):
        m = VERDICT_ITEM.match(line)
        if m and m.group(1) in ITEMS[seam_id] and not (span and span[0] <= n <= span[1]):
            bad.append(f"line {n + 1}: {line.strip()!r} is a verdict line for "
                       f"{m.group(1)} outside '## Verdict'; exactly one canonical verdict "
                       f"line per truth item, under '## Verdict', is allowed")
    return bad


def contradiction_failures(raw: str, seam_id: str, columns: dict) -> list:
    """Repair verdict 6002198078 (Captain decision 6002030055, A2): anywhere in
    the document -- every raw line, code spans and fences included, across line
    breaks -- one of the seam's truth ids followed within six non-alphanumeric
    characters by a verdict word other than the one VERDICT RULE gives over the
    ledger fails, naming the offending line. Markdown link targets
    ('[A1](#a1): ...') are also set aside, line by line."""
    rule = {i: verdict_word({w: columns[i].count(w) for w in WORDS})
            for i in ITEMS[seam_id] if i in columns}
    ids = "|".join(re.escape(i) for i in rule)
    if not ids:
        return []
    pat = re.compile(rf"(?<![A-Za-z0-9])({ids})[^A-Za-z0-9]{{0,6}}({VERDICT_WORD})", re.I)
    hits = {}
    for m in pat.finditer(raw):
        hits.setdefault((raw.count("\n", 0, m.start()) + 1, m.group(1).upper(),
                         m.group(2)), None)
    for n, line in enumerate(raw.split("\n"), 1):
        for m in pat.finditer(LINK_TARGET.sub("]", line)):
            hits.setdefault((n, m.group(1).upper(), m.group(2)), None)
    bad = []
    lines = raw.split("\n")
    for n, i, said in sorted(hits):
        word = re.sub(r"[^A-Za-z0-9]+", "_", said.upper())
        if word != rule[i]:
            bad.append(f"line {n}: {i} is followed by {said!r}, but VERDICT RULE over the "
                       f"ledger gives {rule[i]} ({lines[n - 1].strip()!r}); a truth id "
                       f"followed within six non-alphanumeric characters by a verdict "
                       f"word must not contradict its verdict anywhere in the document")
    return bad


def verdict_failures(text: str, seam_id: str, columns: dict) -> list:
    """'## Verdict' against the ledger columns (item -> [cell words])."""
    bad = []
    body = section(text, "Verdict", bad)
    if body is None:
        return bad
    for l in body.splitlines():
        if not VERDICT_ITEM.match(l) and verdict_like(l):
            bad.append(f"'## Verdict': line {l.strip()!r} reads as a verdict but is not "
                       f"in the form '- ID: WORD (counts)' starting in column zero; "
                       f"every verdict-like line is checked, so write it in that form "
                       f"or reword it as prose")
    lines = [l.rstrip() for l in body.splitlines() if VERDICT_ITEM.match(l)]
    ids = [VERDICT_ITEM.match(l).group(1) for l in lines]
    _once(ids, "'## Verdict' states", bad)
    for i in ITEMS[seam_id]:
        if i not in ids:
            bad.append(f"'## Verdict' has no line for truth item {i}")
    for i in sorted(set(ids) - set(ITEMS[seam_id])):
        bad.append(f"'## Verdict' states {i}, which is not a {seam_id} truth item")
    if ids != list(ITEMS[seam_id]):
        bad.append(f"'## Verdict' states {', '.join(ids) or 'no item'}; exactly one line per "
                   f"truth item, in the order {', '.join(ITEMS[seam_id])}, is required")
    for line in lines:
        m = VERDICT_LINE.match(line)
        i = VERDICT_ITEM.match(line).group(1)
        if i not in columns:
            continue
        if not m:
            bad.append(f"verdict {i}: {line!r} is not '- {i}: SUFFICES|GENUINELY_MISSING|"
                       f"UNDETERMINED (" + ", ".join(f"{w} n" for w in WORDS) + ")', "
                       f"optionally followed by '; text', with single spaces")
            continue
        tail = m.group(8) or ""
        if COUNT_STATEMENT.search(tail) or VERDICT_LIKE.search(tail):
            bad.append(f"verdict {i}: the line's text after its counts states another "
                       f"verdict or count ({tail.strip()!r}); one verdict per line")
        word, got = m.group(2), dict(zip(WORDS, (int(n) for n in m.groups()[2:7])))
        want = {w: columns[i].count(w) for w in WORDS}
        for w in WORDS:
            if got[w] != want[w]:
                bad.append(f"verdict {i}: {w} {got[w]}, the ledger has {want[w]}")
        rule = verdict_word(want)
        if word not in VERDICTS:
            bad.append(f"verdict {i}: {word!r} is not one of {', '.join(VERDICTS)}")
        elif word != rule:
            bad.append(f"verdict {i}: {word}, but VERDICT RULE over the ledger gives "
                       f"{rule}")
        if word == SUFFICES:
            if not any(p in line for p in STATUS_PHRASES):
                bad.append(f"verdict {i}: a SUFFICES line carries no status phrase "
                           f"({' | '.join(repr(p) for p in STATUS_PHRASES)})")
            if cites_candidate(line) and CANDIDATE not in line:
                bad.append(f"verdict {i}: a SUFFICES line citing AQ4 §9 rungs 2-5, §12, "
                           f"§13 or §16 does not say {CANDIDATE!r}")
    return bad


# --------------------------------------------------------------- checking

def exact_reference(token: str) -> bool:
    """True for 'seams.json' or a path suffix of SEAMS_REL (whole path
    components only); never for 'unrelated-seams.json', 'other/seams.json' or
    'seams.json.bak', 'unrelated+seams.json' or 'unrelated@seams.json'. The
    token is the whole whitespace-delimited word: only wrapping punctuation
    (backticks, quotes, emphasis, brackets, a sentence's full stop or comma), a
    possessive "'s" and a Markdown link '[ref](ref)' with both sides exact are
    set aside."""
    link = MD_LINK.fullmatch(token)
    if link:
        return (_unwrap(link.group(1) + link.group(4)) == ""
                and all(exact_reference(p) for p in link.group(2, 3)))
    t = _unwrap(token)
    t = t[2:] if t.startswith("./") else t
    return t == SEAMS_REL or SEAMS_REL.endswith("/" + t)


def _unwrap(t: str) -> str:
    """`t` without its wrapping punctuation: leading WRAP_OPEN and trailing
    WRAP_CLOSE characters, a trailing possessive "'s", and Markdown emphasis
    ('*' or '_') only as a matched pair around the rest."""
    while t:
        if t.endswith(("'s", "’s")):
            t = t[:-2]
        elif t[0] in WRAP_OPEN:
            t = t[1:]
        elif t[-1] in WRAP_CLOSE:
            t = t[:-1]
        elif len(t) > 1 and t[0] == t[-1] and t[0] in "*_":
            t = t[1:-1]
        else:
            break
    return t


def cite_failures(text: str, sha: str) -> list:
    """A sha256 is attributed to the artifact only on a line that names it
    by an exact reference and names no other '*seams.json' (every
    whitespace-delimited word holding 'seams.json' is an exact reference)."""
    lines = [l for l in text.splitlines()
             if SEAMS_TOKEN.search(l) and all(exact_reference(t) for t in SEAMS_TOKEN.findall(l))]
    cited = [s for l in lines for s in SHA.findall(l)]
    bad = [f"the document cites seams.json sha256 {s}, the verified artifact is {sha}"
           for s in sorted(set(cited)) if s != sha]
    if sha not in cited:
        bad.append(f"the document does not cite the verified seams.json sha256 {sha}")
    return bad


def common_failures(text: str, sha: str) -> list:
    bad = cite_failures(text, sha)
    if headings(text, "Captain questions") != 1:
        bad.append(f"the document has {headings(text, 'Captain questions')} sections "
                   f"headed '## Captain questions'; exactly one is required")
    return bad


def part_of(name: str, classes: dict):
    """(class, part) for a ledger row name; part None for a whole class; (None,
    None) for a name that is neither."""
    if name in classes:
        return name, None
    m = PART.match(name)
    if m and m.group(1) in classes:
        return m.group(1), int(m.group(2))
    return None, None


def r2a_failures(text: str, seam: dict) -> tuple:
    bad, items = [], ITEMS["R2-A"]
    classes = seam["classes"]
    recs = {m["address"]: m for m in seam["members"]}
    rows = table(text, R2A_HEAD, bad)
    names = [r[0] for r in rows]
    _once(names, "the R2-A ledger lists row", bad)
    splits = address_lists(text, "Splits", bad, required=False)
    reads = address_lists(text, "Reads", bad, required=True)

    members = {}                                 # ledger row -> its member list
    for n in dict.fromkeys(names):
        cls, part = part_of(n, classes)
        if cls is None:
            bad.append(f"the R2-A ledger lists row {n!r}, which is not a seams.json "
                       f"class or '<class>/part-<k>' of one")
        elif part is None:
            members[n] = classes[cls]["members"]
        elif n not in splits:
            bad.append(f"R2-A part row {n}: no member list '### {n}' under '## Splits'")
        else:
            members[n] = splits[n]
    for h in splits:
        if part_of(h, classes)[1] is None:
            bad.append(f"'## Splits' / '### {h}' is not '<class>/part-<k>' of a "
                       f"seams.json class")
        elif h not in names:
            bad.append(f"'## Splits' / '### {h}' has no R2-A ledger row")
    for cls, c in classes.items():
        parts = [n for n in dict.fromkeys(names) if n != cls and part_of(n, classes)[0] == cls]
        if cls not in names and not parts:
            bad.append(f"the R2-A ledger omits class {cls!r}")
        if cls in names and parts:
            bad.append(f"class {cls!r} has both a whole-class row and part rows")
        if not parts:
            continue
        where = {}
        for p in parts:
            for a in splits.get(p, []):
                where.setdefault(a, []).append(p)
        for a, ps in sorted(where.items()):
            if a not in c["members"]:
                bad.append(f"split of class {cls!r}: {', '.join(ps)} lists {a}, which is "
                           f"not a member of the class")
            if len(ps) > 1:
                bad.append(f"split of class {cls!r}: parts are not disjoint; {a} is in "
                           f"{', '.join(ps)}")
        lost = [a for a in c["members"] if a not in where]
        if lost:
            bad.append(f"split of class {cls!r}: the union of its parts misses {len(lost)} "
                       f"member(s) ({lost[0]}, ...); the parts must partition the class")
    for h in reads:
        if h not in members and h not in names:
            bad.append(f"'## Reads' / '### {h}' is not an R2-A ledger row")

    columns = {i: [] for i in items}
    for row in rows:
        n = row[0]
        if n not in members:
            continue
        mem, cls = members[n], part_of(n, classes)[0]
        size, read = len(set(mem)), _int(row[2])
        cells = dict(zip(items, row[3:3 + len(items)]))
        label = f"R2-A row {n}"
        _words(label, cells, bad)
        for i in items:
            columns[i].append(cells[i])
        if _int(row[1]) != size:
            bad.append(f"{label}: members {row[1]!r}, seams.json {size}")
        got = reads.get(n)
        if got is None:
            bad.append(f"{label}: no '### {n}' list under '## Reads'")
            got = []
        _once(got, f"{label}: '## Reads' lists", bad)
        for a in got:
            if a not in mem:
                bad.append(f"{label}: '## Reads' lists {a}, which is not a member of "
                           f"that row")
        if read != len(got):
            bad.append(f"{label}: read {row[2]!r}, but '## Reads' lists {len(got)} "
                       f"address(es)")
        held = [a for a in classes[cls]["read"] if a in mem]
        for a in held:
            if a not in got:
                bad.append(f"{label}: READ POSITION {a} is not listed under '## Reads'")
        first = next((a for a in classes[cls]["members"] if a in mem), None)
        if not held and first is not None and first not in got:
            bad.append(f"{label}: the row holds no READ POSITION, and its first member "
                       f"in seams.json order, {first}, is not listed under '## Reads'")
        if read is not None and read < 1:
            bad.append(f"{label}: read {read}; every class or part reads at least one "
                       f"member")
        full = read == size
        for i in items:
            if cells[i] != EXPRESSED or full:
                continue
            if i == "A4":
                bad.append(f"{label}: A4 EXPRESSED with read {row[2]} of {size}; A4 has "
                           f"no mechanical evidence and needs every member read")
                continue
            unsupported = [a for a in mem if (recs.get(a) or {}).get(f"supports_{i}")
                           is not True]
            if unsupported:
                bad.append(f"{label}: {i} EXPRESSED with read {row[2]} of {size} and "
                           f"supports_{i} not true for {len(unsupported)} member(s) "
                           f"({unsupported[0]}, ...)")
        if read is not None and read < size and \
                f"inferred from {read} of {size} read" not in row[-1]:
            bad.append(f"{label}: read {read} < members {size}, and the note does not "
                       f"say 'inferred from {read} of {size} read'")

    recall = table(text, R2A_RECALL_HEAD, bad)
    want = sorted({a for v in seam["recall_controls"].values() for a in v})
    _coverage([r[0] for r in recall], want, "R2-A recall table", "recall control clause",
              bad)
    for row in recall:
        if row[0] not in want:
            continue
        ok = {(recs.get(row[0]) or {}).get("class")} | {
            n for n, mem in members.items() if row[0] in mem}
        if row[1] not in ok:
            bad.append(f"R2-A recall {row[0]}: class {row[1]!r}, the member is in "
                       f"{' or '.join(sorted(x for x in ok if x))}")
        _words(f"R2-A recall {row[0]}", dict(zip(items, row[2:2 + len(items)])), bad)
    return bad, columns


def r2b_failures(text: str, seam: dict) -> tuple:
    bad, items = [], ITEMS["R2-B"]
    rows = table(text, R2B_HEAD, bad)
    _coverage([r[0] for r in rows], seam["population"], "R2-B ledger", "member", bad)
    columns = {i: [] for i in items}
    for row in rows:
        if row[0] not in seam["population"]:
            continue
        cells = dict(zip(items, row[1:1 + len(items)]))
        _words(f"R2-B row {row[0]}", cells, bad)
        for i in items:
            columns[i].append(cells[i])
    body = section(text, "Pronoun candidates", bad)
    pron = table(body, PRONOUN_HEAD, bad, "'## Pronoun candidates'") if body is not None else []
    want = [x["address"] for x in seam["pronoun_candidates"]["list"]]
    _coverage([r[0] for r in pron], want, "pronoun table", "pronoun candidate", bad)
    for row in pron:
        if row[0] not in want:
            continue
        label = f"pronoun row {row[0]}"
        cells = dict(zip(items, row[2:2 + len(items)]))
        if not QUOTED.search(row[-1]):
            bad.append(f"{label}: the note holds no double-quoted antecedent span")
        if row[1] == NOT_MEMBER:
            for i, w in cells.items():
                if w != DASH:
                    bad.append(f"{label}: NOT-MEMBER carries {w!r} in {i}; every truth "
                               f"cell must be '{DASH}'")
        elif row[1] == MEMBER:
            _words(label, cells, bad)
            for i in items:
                columns[i].append(cells[i])
        else:
            bad.append(f"{label}: membership {row[1]!r} is not {MEMBER} or {NOT_MEMBER}")
    return bad, columns


def r2c_failures(text: str, seam: dict) -> tuple:
    bad, items = [], ITEMS["R2-C"]
    rows = table(text, R2C_HEAD, bad)
    _coverage([r[0] for r in rows], seam["population"], "R2-C ledger", "member", bad)
    columns = {i: [] for i in items}
    for row in rows:
        if row[0] not in seam["population"]:
            continue
        cells = dict(zip(items, row[1:1 + len(items)]))
        _words(f"R2-C row {row[0]}", cells, bad)
        for i in items:
            columns[i].append(cells[i])
    return bad, columns


LEDGERS = {"R2-A": r2a_failures, "R2-B": r2b_failures, "R2-C": r2c_failures}


def document_failures(seam_id: str, text: str, seams_doc: dict, sha: str) -> list:
    """Every way the `seam_id` audit document disagrees with (a)-(e), over
    its document structure only, after markup_failures over every raw line."""
    raw, markup = text, markup_failures(text)
    text = structure(text)
    bad, columns = LEDGERS[seam_id](text, seams_doc["seams"][seam_id])
    return (markup + common_failures(text, sha) + bad + verdict_failures(text, seam_id, columns)
            + stray_verdict_failures(raw, text, seam_id)
            + contradiction_failures(raw, seam_id, columns))


# ------------------------------------------------------------------ skeleton

def skeleton(seam_id: str, seams_doc: dict, sha: str) -> str:
    """The rows to fill: every truth cell and note empty, every split absent.
    A starting point, never an audit: it fails until it is filled."""
    seam = seams_doc["seams"][seam_id]
    items = ITEMS[seam_id]
    blank = [""] * (len(items) + 1)
    out = [f"seams.json sha256: `{sha}`", ""]
    if seam_id == "R2-A":
        out += [_row(R2A_HEAD), _sep(len(R2A_HEAD))]
        out += [_row([f"`{k}`", c["count"], len(c["read"])] + blank)
                for k, c in seam["classes"].items()]
        out += ["", "## Reads", ""]
        for k, c in seam["classes"].items():
            out += [f"### {k}", ""] + [f"- `{a}`" for a in c["read"]] + [""]
        cls = {m["address"]: m["class"] for m in seam["members"]}
        out += ["## Recall controls", "", _row(R2A_RECALL_HEAD), _sep(len(R2A_RECALL_HEAD))]
        out += [_row([f"`{a}`", f"`{cls.get(a)}`"] + blank)
                for a in sorted({a for v in seam["recall_controls"].values() for a in v})]
    else:
        head = R2B_HEAD if seam_id == "R2-B" else R2C_HEAD
        out += [_row(head), _sep(len(head))]
        out += [_row([f"`{a}`"] + blank) for a in seam["population"]]
    if seam_id == "R2-B":
        out += ["", "## Pronoun candidates", "", _row(PRONOUN_HEAD), _sep(len(PRONOUN_HEAD))]
        out += [_row([f"`{x['address']}`", ""] + blank)
                for x in seam["pronoun_candidates"]["list"]]
    out += ["", "## Verdict", ""]
    out += [f"- {i}: " for i in items]
    out += ["", "## Captain questions", ""]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------- negative controls

def _member(a: str, cls: str, a2: bool = True) -> dict:
    return {"address": a, "class": cls, "supports_A1": None, "supports_A2": a2,
            "supports_A3": False, "supports_A5": False}


def _positions(n: int) -> list:
    return list(range(n)) if n <= 10 else [round(i * (n - 1) / 9) for i in range(10)]


def synthetic_seams() -> dict:
    """A synthetic seams.json: R2-A classes 'draw' (12 members, every
    supports_A2 true), 'deal' (13 members, split so part-2 holds no READ
    POSITION) and 'no-would:if' (2 members); two R2-B members and two pronoun
    candidates; two R2-C members. Generic addresses only."""
    classes, recs = {}, []
    for cls, tag, n in (("draw", "d", 12), ("deal", "e", 13), ("no-would:if", "i", 2)):
        ids = [f"rig-{tag}{k:02d}:0:0:0" for k in range(n)]
        pos = _positions(n)
        classes[cls] = {"count": n, "members": ids, "read_positions": pos,
                        "read": [ids[i] for i in pos]}
        recs += [_member(a, cls, a2=(cls == "draw")) for a in ids]
    return {"interface": {"version": hr.INTERFACE_VERSION, "blob": hr.INTERFACES_BLOB},
            "seams": {
                "R2-A": {"classes": classes, "members": recs,
                         "recall_controls": {"rig-d00": ["rig-d00:0:0:0"],
                                             "rig-e02": ["rig-e02:0:0:0"]}},
                "R2-B": {"population": ["rig-b0:0:0:0", "rig-b1:0:1:0"],
                         "pronoun_candidates": {"count": 2, "list": [
                             {"address": "rig-b2:0:0:0"}, {"address": "rig-b3:0:0:1"}]}},
                "R2-C": {"population": ["rig-c0:0:0:0", "rig-c1:0:1:0"]}}}


SYN_SHA = hashlib.sha256(b"rig seams.json").hexdigest()
DEAL_PART2 = ("rig-e02:0:0:0", "rig-e06:0:0:0", "rig-e10:0:0:0")
I3A_LINE = "carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, " \
           "not production law)"
CAND_LINE = "carried by CANDIDATE benchmark structure §13, not ratified production law"


def _vline(i: str, word: str, cells: list, tail: str = "") -> str:
    return (f"- {i}: {word} (" + ", ".join(f"{w} {cells.count(w)}" for w in WORDS)
            + ")" + (f"; {tail}" if tail else ""))


def synthetic_docs() -> dict:
    """seam -> a clean audit document over synthetic_seams() that passes."""
    s = synthetic_seams()["seams"]
    A = s["R2-A"]["classes"]
    deal1 = [a for a in A["deal"]["members"] if a not in DEAL_PART2]
    rows = [("draw", 12, 10, [UNRESOLVED, EXPRESSED, NOT_EXPRESSED, UNRESOLVED,
                              OUT_OF_CONTRACT], "A2 by region heads; inferred from 10 of 12 read"),
            ("deal/part-1", 10, 10, [UNRESOLVED, UNRESOLVED, NOT_EXPRESSED, UNRESOLVED,
                                     UNRESOLVED], "the read members"),
            ("deal/part-2", 3, 1, [UNRESOLVED, UNRESOLVED, NOT_EXPRESSED, UNRESOLVED,
                                   UNRESOLVED], "inferred from 1 of 3 read"),
            ("no-would:if", 2, 2, [UNRESOLVED, UNRESOLVED, NOT_EXPRESSED, UNRESOLVED,
                                   UNRESOLVED], "both read")]
    ledger = [_row(R2A_HEAD), _sep(len(R2A_HEAD))] + [
        _row([f"`{n}`", m, r] + c + [note]) for n, m, r, c, note in rows]
    deal1_reads = [a for a in A["deal"]["read"] if a in deal1]
    col = lambda k: [r[3][k] for r in rows]
    a_doc = "\n".join(
        ["# A01 R2-A (synthetic)", "", f"seams.json sha256 `{SYN_SHA}`", ""] + ledger
        + ["", "## Splits", "", "### deal/part-1", ""] + [f"- `{a}`" for a in deal1]
        + ["", "### deal/part-2", ""] + [f"- `{a}`" for a in DEAL_PART2]
        + ["", "## Reads", "", "### draw", ""] + [f"- `{a}`" for a in A["draw"]["read"]]
        + ["", "### deal/part-1", ""] + [f"- `{a}`" for a in deal1_reads]
        + ["", "### deal/part-2", "", f"- `{DEAL_PART2[0]}`", "", "### no-would:if", ""]
        + [f"- `{a}`" for a in A["no-would:if"]["members"]]
        + ["", "## Recall", "", _row(R2A_RECALL_HEAD), _sep(len(R2A_RECALL_HEAD)),
           _row(["`rig-d00:0:0:0`", "draw", UNRESOLVED, EXPRESSED, NOT_EXPRESSED,
                 UNRESOLVED, OUT_OF_CONTRACT, "read"]),
           _row(["`rig-e02:0:0:0`", "deal/part-2", UNRESOLVED, UNRESOLVED, NOT_EXPRESSED,
                 UNRESOLVED, UNRESOLVED, "read"]),
           "", "## Verdict", "",
           _vline("A1", UNDETERMINED, col(0)),
           _vline("A2", SUFFICES, col(1), I3A_LINE),
           _vline("A3", MISSING, col(2), "no CR 614 carrier"),
           _vline("A4", UNDETERMINED, col(3)),
           _vline("A5", UNDETERMINED, col(4)),
           "", "## Captain questions", "", "- none raised by the synthetic audit.", ""])
    b_cells = {"rig-b0:0:0:0": [EXPRESSED, PARTIAL, UNRESOLVED, OUT_OF_CONTRACT],
               "rig-b1:0:1:0": [EXPRESSED, PARTIAL, UNRESOLVED, OUT_OF_CONTRACT]}
    b_member = [EXPRESSED, PARTIAL, UNRESOLVED, OUT_OF_CONTRACT]
    bcol = lambda k: [c[k] for c in b_cells.values()] + [b_member[k]]
    b_doc = "\n".join(
        ["# A01 R2-B (synthetic)", "", f"seams.json sha256 `{SYN_SHA}`", "",
         _row(R2B_HEAD), _sep(len(R2B_HEAD))]
        + [_row([f"`{a}`"] + c + ["read"]) for a, c in b_cells.items()]
        + ["", "## Pronoun candidates", "", _row(PRONOUN_HEAD), _sep(len(PRONOUN_HEAD)),
           _row(["`rig-b2:0:0:0`", MEMBER] + b_member + ['antecedent "target player"']),
           _row(["`rig-b3:0:0:1`", NOT_MEMBER] + [DASH] * 4
                + ['antecedent "those widgets"']),
           "", "## Verdict", "",
           _vline("B1", SUFFICES, bcol(0), CAND_LINE),
           _vline("B2", MISSING, bcol(1)), _vline("B3", UNDETERMINED, bcol(2)),
           _vline("B4", UNDETERMINED, bcol(3)),
           "", "## Captain questions", ""])
    c_cells = [UNRESOLVED, NOT_EXPRESSED, OUT_OF_CONTRACT, UNRESOLVED]
    c_doc = "\n".join(
        ["# A01 R2-C (synthetic)", "", f"seams.json sha256 `{SYN_SHA}`", "",
         _row(R2C_HEAD), _sep(len(R2C_HEAD))]
        + [_row([f"`{a}`"] + c_cells + ["read"]) for a in ("rig-c0:0:0:0", "rig-c1:0:1:0")]
        + ["", "## Verdict", ""]
        + [_vline(i, verdict_word({w: [c].count(w) for w in WORDS}), [c, c])
           for i, c in zip(ITEMS["R2-C"], c_cells)]
        + ["", "## Captain questions", ""])
    return {"R2-A": a_doc, "R2-B": b_doc, "R2-C": c_doc}


def _line(doc: str, prefix: str) -> str:
    return next(l for l in doc.splitlines(keepends=True) if l.startswith(prefix))


def _cells(row: str, k: int, value: str) -> str:
    c = row.split("|")
    c[k] = f" {value} "
    return "|".join(c)


def rigs() -> dict:
    """name -> (seam, document, seams_doc, sha, needle): each must fail with a
    diagnostic containing `needle`. One per contracted negative control."""
    seams, docs = synthetic_seams(), synthetic_docs()
    a, b = docs["R2-A"], docs["R2-B"]
    draw = _line(a, "| `draw` |")
    p2 = _line(a, "| `deal/part-2` |")
    v = lambda d, i: _line(d, f"- {i}:")
    unsupported = copy.deepcopy(seams)
    unsupported["seams"]["R2-A"]["members"][3]["supports_A2"] = False   # rig-d03, unread
    reads_draw = a.split("## Reads")[1].split("### deal/part-1")[0]
    pos = seams["seams"]["R2-A"]["classes"]["draw"]["read"]
    unread = next(x for x in seams["seams"]["R2-A"]["classes"]["draw"]["members"]
                  if x not in pos)
    swapped = reads_draw.replace(f"- `{pos[3]}`\n", f"- `{unread}`\n")
    extra = reads_draw.replace(f"- `{pos[3]}`\n", f"- `{pos[3]}`\n- `{unread}`\n")
    part2_reads = f"### deal/part-2\n\n- `{DEAL_PART2[0]}`\n"
    head, tail = a.split("## Reads\n")
    in_reads = lambda new: head + "## Reads\n" + tail.replace(part2_reads, new)
    pron = _line(b, "| `rig-b2:0:0:0` |")
    notm = _line(b, "| `rig-b3:0:0:1` |")
    a3 = v(a, "A3")
    c1, c2, c3 = (v(docs["R2-C"], i) for i in ("C1", "C2", "C3"))
    return {
        "a ledger missing one class": (
            "R2-A", a.replace(_line(a, "| `no-would:if` |"), ""), seams, SYN_SHA,
            "the R2-A ledger omits class 'no-would:if'"),
        "a ledger missing one member": (
            "R2-C", docs["R2-C"].replace(_line(docs["R2-C"], "| `rig-c1:0:1:0` |"), ""),
            seams, SYN_SHA, "the R2-C ledger omits member rig-c1:0:1:0"),
        "a ledger with a non-member row": (
            "R2-B", b.replace(_line(b, "| `rig-b1:0:1:0` |"),
                              _line(b, "| `rig-b1:0:1:0` |")
                              + _line(b, "| `rig-b1:0:1:0` |").replace("rig-b1", "rig-zz")),
            seams, SYN_SHA, "lists rig-zz:0:1:0, which is not a seams.json member"),
        "an R2-A ledger with a non-class row": (
            "R2-A", a.replace(draw, draw + draw.replace("`draw`", "`rig-foreign`")),
            seams, SYN_SHA, "'rig-foreign', which is not a seams.json class"),
        "a cell outside the five cell words": (
            "R2-C", docs["R2-C"].replace(f"| {NOT_EXPRESSED} |", "| ABSENT |", 1),
            seams, SYN_SHA, "'ABSENT' is not one of the five cell words"),
        "a SUFFICES over a NOT-EXPRESSED cell": (
            "R2-A", a.replace(a3, a3.replace(MISSING, SUFFICES).rstrip("\n")
                              + f"; {I3A_LINE}\n"), seams, SYN_SHA,
            f"verdict A3: SUFFICES, but VERDICT RULE over the ledger gives {MISSING}"),
        "a SUFFICES over all-UNRESOLVED cells": (
            "R2-A", a.replace(v(a, "A1"), v(a, "A1").replace(UNDETERMINED, SUFFICES)
                              .rstrip("\n") + f"; {I3A_LINE}\n"), seams, SYN_SHA,
            f"verdict A1: SUFFICES, but VERDICT RULE over the ledger gives {UNDETERMINED}"),
        "a SUFFICES line citing AQ4 §16 without 'CANDIDATE benchmark structure'": (
            "R2-A", a.replace(v(a, "A2"), v(a, "A2").rstrip("\n")
                              + "; edges per AQ4 §16\n"), seams, SYN_SHA,
            "a SUFFICES line citing AQ4 §9 rungs 2-5, §12, §13 or §16"),
        "a '## Reads' list missing a READ POSITION of its row": (
            "R2-A", a.replace(reads_draw, swapped), seams, SYN_SHA,
            f"R2-A row draw: READ POSITION {pos[3]} is not listed"),
        "a '## Reads' list whose count differs from 'read'": (
            "R2-A", a.replace(reads_draw, extra), seams, SYN_SHA,
            "R2-A row draw: read '10', but '## Reads' lists 11"),
        "a split part with read 0": (
            "R2-A", in_reads("### deal/part-2\n").replace(
                p2, _cells(p2, 3, "0").replace("1 of 3", "0 of 3")), seams, SYN_SHA,
            "R2-A row deal/part-2: read 0; every class or part reads at least one"),
        "a split whose parts overlap": (
            "R2-A", a.replace("### deal/part-2\n\n", f"### deal/part-2\n\n- `rig-e00:0:0:0`\n",
                              1), seams, SYN_SHA, "parts are not disjoint; rig-e00:0:0:0"),
        "a split whose parts miss a member of the class": (
            "R2-A", a.replace(f"- `{DEAL_PART2[2]}`\n", "", 1), seams, SYN_SHA,
            "the union of its parts misses 1 member(s)"),
        "an R2-A row with EXPRESSED A4 and read < members": (
            "R2-A", a.replace(draw, _cells(draw, 7, EXPRESSED)), seams, SYN_SHA,
            "R2-A row draw: A4 EXPRESSED with read 10 of 12"),
        "an R2-A row with EXPRESSED A2, read < members and one member's supports_A2 false": (
            "R2-A", a, unsupported, SYN_SHA,
            "R2-A row draw: A2 EXPRESSED with read 10 of 12 and supports_A2 not true"),
        "an R2-A row with read < members and no 'inferred from' note": (
            "R2-A", a.replace(p2, p2.replace("inferred from 1 of 3 read", "one read")),
            seams, SYN_SHA, "does not say 'inferred from 1 of 3 read'"),
        "a pronoun row whose note has no double-quoted antecedent": (
            "R2-B", b.replace(pron, pron.replace('"target player"', "target player")),
            seams, SYN_SHA, "pronoun row rig-b2:0:0:0: the note holds no double-quoted"),
        "a NOT-MEMBER pronoun row with a truth word": (
            "R2-B", b.replace(notm, _cells(notm, 3, UNRESOLVED)), seams, SYN_SHA,
            f"pronoun row rig-b3:0:0:1: NOT-MEMBER carries '{UNRESOLVED}' in B1"),
        "a split part with no READ POSITION that skips its first member": (
            "R2-A", in_reads(f"### deal/part-2\n\n- `{DEAL_PART2[1]}`\n"),
            seams, SYN_SHA, f"its first member in seams.json order, {DEAL_PART2[0]}, is "
                            f"not listed"),
        "a hash attributed only to an unrelated seams.json": (
            "R2-C", docs["R2-C"].replace("seams.json sha256", "unrelated-seams.json sha256"),
            seams, SYN_SHA, "does not cite the verified seams.json sha256"),
        "a hash attributed only to unrelated+seams.json": (
            "R2-C", docs["R2-C"].replace("seams.json sha256", "unrelated+seams.json sha256"),
            seams, SYN_SHA, "does not cite the verified seams.json sha256"),
        "a hash attributed only to unrelated@seams.json": (
            "R2-C", docs["R2-C"].replace("seams.json sha256", "unrelated@seams.json sha256"),
            seams, SYN_SHA, "does not cite the verified seams.json sha256"),
        "an audit entirely inside a code fence": (
            "R2-B", "```markdown\n" + b + "```\n", seams, SYN_SHA,
            "0 sections headed '## Captain questions'"),
        "an audit entirely inside <pre>...</pre>": (
            "R2-B", "<pre>\n" + b + "</pre>\n", seams, SYN_SHA,
            "line 1 contains '<p': HTML tags and HTML comments are not allowed"),
        "a duplicate section hidden in an HTML comment": (
            "R2-B", b + "\n<!--\n## Captain questions\n-->\n", seams, SYN_SHA,
            "contains '<!--': HTML tags and HTML comments are not allowed"),
        "a comment opener inside a code span": (
            "R2-C", docs["R2-C"] + "\nsee `<!--` here\n", seams, SYN_SHA,
            "contains '<!--': HTML tags and HTML comments are not allowed"),
        "a comment closer inside a code fence": (
            "R2-C", docs["R2-C"] + "\n```\n-->\n```\n", seams, SYN_SHA,
            "contains '-->': HTML tags and HTML comments are not allowed"),
        "a wrong seams.json hash": (
            "R2-C", docs["R2-C"], seams, "0" * 64,
            "does not cite the verified seams.json sha256"),
        "a document without '## Captain questions'": (
            "R2-B", b.replace("## Captain questions", "## Questions"), seams, SYN_SHA,
            "0 sections headed '## Captain questions'"),
        "an indented duplicate SUFFICES verdict over NOT-EXPRESSED cells": (
            "R2-C", docs["R2-C"].replace(
                v(docs["R2-C"], "C2"), v(docs["R2-C"], "C2") + "  " + v(docs["R2-C"], "C2")
                .replace(MISSING, SUFFICES).rstrip("\n") + f"; {I3A_LINE}\n"),
            seams, SYN_SHA, "'## Verdict': line '- C2: SUFFICES"),
        "a verdict count that differs from the ledger": (
            "R2-C", docs["R2-C"].replace("UNRESOLVED 2", "UNRESOLVED 3", 1), seams,
            SYN_SHA, "verdict C1: UNRESOLVED 3, the ledger has 2"),
        "a verdict section whose lines are out of item order": (
            "R2-C", docs["R2-C"].replace(c1 + c2, c2 + c1), seams, SYN_SHA,
            "'## Verdict' states C2, C1, C3, C4; exactly one line per truth item, in the "
            "order C1, C2, C3, C4"),
        "a second canonical verdict line outside '## Verdict'": (
            "R2-C", docs["R2-C"] + c3, seams, SYN_SHA,
            "is a verdict line for C3 outside '## Verdict'"),
        "a canonical verdict line with text not after '; '": (
            "R2-C", docs["R2-C"].replace(c1, c1.rstrip("\n") + " because\n"), seams, SYN_SHA,
            "optionally followed by '; text'"),
        "a contradictory verdict word after a truth id in prose": (
            "R2-C", docs["R2-C"] + "\nIn short, C2 -- SUFFICES.\n", seams, SYN_SHA,
            f"C2 is followed by 'SUFFICES', but VERDICT RULE over the ledger gives {MISSING}"),
        "a contradictory verdict word wrapped onto the next line": (
            "R2-C", docs["R2-C"] + "\nso C2:\n  *suffices*\n", seams, SYN_SHA,
            "C2 is followed by 'suffices'"),
        "a contradictory verdict word inside a code fence": (
            "R2-C", docs["R2-C"] + "\n```\nC2: UNDETERMINED\n```\n", seams, SYN_SHA,
            "C2 is followed by 'UNDETERMINED'"),
        "a contradictory verdict word after a link-wrapped truth id": (
            "R2-C", docs["R2-C"] + "\nsee [C2](#c2): SUFFICES\n", seams, SYN_SHA,
            "C2 is followed by 'SUFFICES'"),
    }


def stale_seams_stops() -> bool:
    """A rigged stale seams.json (--verify exits 1) STOPs obtain() before any
    regeneration; a missing one is regenerated only by --check-determinism."""
    import tempfile
    calls = []

    def stale(args):
        calls.append(args[1:])
        return subprocess.CompletedProcess(args, 1 if args[-1] == "--verify" else 0, b"",
                                           b"STALE: rigged")

    regen = []

    def writes(args):
        regen.append(args[1:])
        if args[-1] == "--check-determinism":
            (root / SEAMS_REL).write_bytes(b"{}\n")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / SEAMS_REL).parent.mkdir(parents=True)
        (root / SEAMS_REL).write_bytes(b"{}\n")
        halted = _halts(lambda: obtain(root, stale), f"stale seams input: {SEAMS_REL}")
        (root / SEAMS_REL).unlink()
        got = obtain(root, writes)
    return (halted and calls == [["--verify"]]
            and regen == [["--check-determinism"], ["--verify"]]
            and got == hashlib.sha256(b"{}\n").hexdigest())


def negative_controls() -> list:
    seams, docs = synthetic_seams(), synthetic_docs()
    cases = [("the unrigged synthetic documents pass",
              lambda: all(document_failures(k, docs[k], seams, SYN_SHA) == []
                          for k in docs))]
    for name, (k, d, sd, sha, needle) in rigs().items():
        cases.append((f"a rigged {name} fails",
                      lambda k=k, d=d, sd=sd, sha=sha, needle=needle: any(
                          needle in x for x in document_failures(k, d, sd, sha))))
    cases.append(("a rigged stale seams.json STOPs the checker", stale_seams_stops))
    out = []
    for name, check in cases:
        if not check():
            fc.halt(f"negative control failed: {name}")
        out.append(name)
    return out


# ----------------------------------------------------------------------- CLI

def seam_of(doc: str) -> str:
    """The seam a document audits: by its path, else by 'A01-R2<X>-' in its name."""
    for k, rel in DOCS.items():
        if Path(doc).name == Path(rel).name:
            return k
    m = re.search(r"A01-R2([ABC])-", Path(doc).name)
    if not m:
        fc.halt(f"{doc} is not one of the three A01 audit documents ({', '.join(DOCS.values())})")
    return f"R2-{m.group(1)}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--doc", help="one audit document (repo-relative); default all three")
    ap.add_argument("--skeleton", action="store_true",
                    help="print the ledger rows to fill, to stdout")
    a = ap.parse_args(argv)
    targets = [(seam_of(a.doc), a.doc)] if a.doc else list(DOCS.items())
    controls = negative_controls()
    seams_doc, sha = load()
    if a.skeleton:
        for k, _ in targets:
            sys.stdout.write(skeleton(k, seams_doc, sha))
        return 0
    rc = 0
    for k, rel in targets:
        path = Path(rel) if Path(rel).is_absolute() else ROOT / rel
        if not path.exists():
            print(f"FAIL: {rel} does not exist", file=sys.stderr)
            rc = 1
            continue
        bad = document_failures(k, path.read_text(encoding="utf-8"), seams_doc, sha)
        for b in bad:
            print(f"FAIL: {rel}: {b}", file=sys.stderr)
        if bad:
            rc = 1
            continue
        print(f"{rel}: {k} ledger coverage, cell words, read rule, verdicts and the "
              f"seams.json sha256 ({sha}) agree; {len(controls)} negative controls hold")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
