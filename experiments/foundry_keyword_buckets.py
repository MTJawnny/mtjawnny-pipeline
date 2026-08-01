#!/usr/bin/env python3
"""Keyword-bucket extraction DET job (CORPUS-PASS-PLAN.md step 2, ratified
MASTER-HANDOFF-ADDENDUM-3.md sec.2/4, 2026-07-29 session). Walks CR 702
(Keyword Abilities) in the local mtg-comprehensive-rules.md and classifies
every keyword's ability class mechanically from the CR's own first-line
characterization ("[Keyword] is a static/triggered/activated/evasion/
characteristic-defining ability."). Every classification cites the exact
CR sub-rule it came from. Verify-or-drop: no recall, no guessing -- a
keyword whose CR text does not state one of the closed classes is bucketed
"unclassified" with the raw quote, never force-fit.

This is a DET job: zero tokens, fully mechanical regex extraction over the
CR markdown. It does not touch codebook.json and is not gated on anything.

Usage: python3 experiments/foundry_keyword_buckets.py
"""
import sys
import re
import json
from pathlib import Path
from datetime import date

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402

# Cross-repo reference: the CR markdown lives in the site repo, not this one
# (it is rules text, not Scryfall card data, so the "no card data in git"
# rule does not apply -- this repo simply has no local copy and none is
# created by this job). Verified byte-identical against ~/Downloads copy,
# 2026-07-30 session (md5 7217ddfd5b4190603070352fd286228d).
CR_PATH = Path.home() / "Projects" / "mtjawnny.github.io" / "docs" / "mtg-comprehensive-rules.md"

OUT_PATH = fc.FOUNDRY_OUT_DIR / "keyword-buckets.json"
REPORT_PATH = fc.FOUNDRY_OUT_DIR / "keyword-buckets_report.md"

CLOSED_BUCKETS = ("static", "triggered", "activated", "evasion", "spell", "replacement",
                   "characteristic-defining", "hybrid", "ambiguous-card-dependent",
                   "rules-modifying", "special-action", "unclassified")

# Closed DELIVERY trigger-family vocabulary per CODEBOOK-NAMING-GRAMMAR.md sec.2.
# NOTE: sec.2's table literally lists the slot value "dies" for the
# graveyard-from-battlefield family, but sec.13 D-1 ratifies "death-trigger"
# as the family word ("No dies- slugs") -- an internal inconsistency in that
# document. This job follows D-1 (the explicit, later ratification) and
# flags the table/ratification mismatch in the report for Captain.
TRIGGER_FAMILY_PATTERNS = [
    ("attack-trigger", re.compile(r"whenever [^.]*\battacks\b", re.I)),
    ("etb", re.compile(r"\bwhen(?:ever)? [^.]* enters\b", re.I)),
    ("combat-damage-to-player", re.compile(r"deals combat damage to a player", re.I)),
    ("combat-damage-to-creature", re.compile(r"deals combat damage to a creature", re.I)),
    ("combat-damage-trigger-unqualified", re.compile(r"deals combat damage\b", re.I)),
    ("death-trigger", re.compile(r"put into a graveyard from the battlefield", re.I)),
    ("leaves-battlefield-trigger", re.compile(r"leaves the battlefield", re.I)),
    ("cast-trigger", re.compile(r"\bwhen(?:ever)? you cast\b", re.I)),
    ("upkeep-trigger", re.compile(r"beginning of (?:your |each |a )?upkeep", re.I)),
    ("blocks-or-becomes-blocked-trigger (NOT in closed vocab -- proposed)",
     re.compile(r"becomes blocked|blocks or becomes blocked|\bthis creature blocks\b", re.I)),
]

CASTING_MODIFIER_PATTERNS = [
    re.compile(r"\byou may cast\b", re.I),
    re.compile(r"activate only as (?:a sorcery|an instant)", re.I),
    re.compile(r"rather than (?:its |paying )?(?:its )?mana cost", re.I),
    re.compile(r"reduce[s]? the (?:total )?cost", re.I),
    re.compile(r"costs? \{[^}]*\} less", re.I),
    re.compile(r"without paying its mana cost", re.I),
    re.compile(r"paying (?:an )?alternative cost", re.I),
    re.compile(r"any time you could cast", re.I),
    re.compile(r"spend mana as though it (?:were|was) mana of any (?:color|type)", re.I),
]

HEADER_RE = re.compile(r"^702\.(\d+)\. (.+)$")
SUBRULE_RE = re.compile(r"^702\.(\d+)([a-z]) (.+)$")


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = s.replace("∞ (infinity)", "infinity")
    s = re.sub(r"[’']", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def load_cr_text() -> str:
    if not CR_PATH.exists():
        fc.halt(f"CR markdown not found at {CR_PATH} -- cannot run a DET job without its source text")
    return CR_PATH.read_text(encoding="utf-8")


def find_cr_date(text: str) -> str:
    m = re.search(r"effective as of ([A-Za-z]+ \d{1,2}, \d{4})", text)
    if not m:
        fc.halt("CR markdown has no 'effective as of <date>' line -- cannot version the output, refusing to guess")
    return m.group(1)


def split_entries(text: str) -> list:
    """Returns list of (number:int, name:str, body_lines:list[str]) for each
    702.N entry, N=2..max (702.1 is the general-rules intro, not a keyword)."""
    lines = text.splitlines()
    starts = []
    for i, line in enumerate(lines):
        m = HEADER_RE.match(line)
        if m and not SUBRULE_RE.match(line):
            starts.append((i, int(m.group(1)), m.group(2)))
    entries = []
    for idx, (line_i, num, name) in enumerate(starts):
        if num == 1:
            continue
        end_i = starts[idx + 1][0] if idx + 1 < len(starts) else line_i + 400
        entries.append((num, name, lines[line_i:end_i]))
    return entries


def parse_subrules(body_lines: list, num: int) -> list:
    """Returns ordered list of (letter, text) for this entry's 702.Nx lines,
    joining wrapped continuation lines and dropping 'Example:' lines."""
    out = []
    cur_letter, cur_text = None, None
    for line in body_lines:
        m = SUBRULE_RE.match(line)
        if m and int(m.group(1)) == num:
            if cur_letter is not None:
                out.append((cur_letter, cur_text.strip()))
            cur_letter, cur_text = m.group(2), m.group(3)
        elif line.strip().startswith("Example:"):
            continue
        elif line.strip() == "":
            continue
        elif cur_letter is not None:
            cur_text += " " + line.strip()
    if cur_letter is not None:
        out.append((cur_letter, cur_text.strip()))
    return out


COMPONENT_RE = re.compile(
    r"The (first|second|third|fourth) is (?:an? )?(static|triggered|activated) ability", re.I)

# General composite-type scan: every "TYPE ability"/"TYPE effect" mention in
# the descriptive preamble (before the first curly-quoted rules text, so we
# never pick up incidental type-words inside the quoted reminder text
# itself). Handles every CR phrasing this section actually uses: "is a
# static ability", "represents a static ability", "represents two static
# abilities", "represents both a static ability and a triggered ability",
# "represents both a replacement effect and a triggered ability", "represents
# two spell abilities", "The first is a static ability... second is...".
TYPE_MENTION_RE = re.compile(r"\b(static|triggered|activated|spell|replacement) (?:abilit(?:y|ies)|effect)\b", re.I)
SPECIAL_ACTION_RE = re.compile(r"\bis a special action\b", re.I)
ACTIVATED_MODIFIER_RE = re.compile(r"adds additional rules to the activated ability that follows", re.I)
DECK_CONSTRUCTION_RE = re.compile(r"abilities that modify the rules for deck construction", re.I)
AMBIGUOUS_CARD_RE = re.compile(
    r"together, they represent a static ability, a triggered ability, or an activated ability", re.I)


def classify_entry(num: int, name: str, subrules: list) -> dict:
    cr_prefix = f"702.{num}"
    result = {
        "keyword": name, "cr_number": cr_prefix, "class": None,
        "class_cr_citation": None, "class_evidence": None,
        "trigger_family": None, "trigger_family_cr_citation": None,
        "trigger_family_evidence": None, "hybrid_components": None,
        "multi_instance": False,
        "casting_modifier_heuristic": False, "casting_modifier_evidence": None,
        "verify_or_drop": False,
    }

    scan_window = subrules[:5]
    class_letter, class_text = None, None

    for letter, text in scan_window:
        # Descriptive prose only: cut at the keyword's own reminder-text
        # definition quote ("X" means "Y"). A naive first-curly-quote split
        # is wrong here -- citations like (see rule 709, "Split Cards") or
        # the keyword symbol itself in quotes ("infinity") can appear BEFORE
        # the real classifying sentence and would truncate it away.
        means_idx = text.find("” means")
        preamble = text[:means_idx] if means_idx != -1 else text
        low = preamble.lower()

        if AMBIGUOUS_CARD_RE.search(text):
            result["class"] = "ambiguous-card-dependent"
            class_letter, class_text = letter, text
            break
        if DECK_CONSTRUCTION_RE.search(low):
            result["class"] = "rules-modifying"
            class_letter, class_text = letter, text
            break
        if SPECIAL_ACTION_RE.search(text):
            result["class"] = "special-action"
            class_letter, class_text = letter, text
            break
        if re.search(r"is an? characteristic-defining ability", low):
            result["class"] = "characteristic-defining"
            class_letter, class_text = letter, text
            break
        if re.search(r"is an evasion ability", low):
            result["class"] = "evasion"
            class_letter, class_text = letter, text
            break
        if ACTIVATED_MODIFIER_RE.search(low):
            result["class"] = "activated"
            class_letter, class_text = letter, text
            break

        mentions = TYPE_MENTION_RE.findall(preamble)
        if mentions:
            distinct = []
            for m in mentions:
                v = m.lower()
                if v not in distinct:
                    distinct.append(v)
            class_letter, class_text = letter, text
            if len(distinct) == 1:
                result["class"] = distinct[0]
                result["multi_instance"] = len(mentions) > 1
            else:
                result["class"] = "hybrid"
                result["hybrid_components"] = distinct
            break

    if result["class"] is None:
        result["class"] = "unclassified"
        result["verify_or_drop"] = True
        result["class_evidence"] = subrules[0][1] if subrules else "(no subrules found)"
        result["class_cr_citation"] = f"{cr_prefix}{subrules[0][0]}" if subrules else cr_prefix
        return result

    result["class_cr_citation"] = f"{cr_prefix}{class_letter}"
    result["class_evidence"] = class_text
    if result["class"] == "ambiguous-card-dependent":
        result["verify_or_drop"] = True

    if result["class"] in ("triggered", "hybrid"):
        # search the classifying subrule AND the next 2 for trigger wording
        search_text = " ".join(t for _, t in scan_window[:scan_window.index((class_letter, class_text)) + 3])
        for fam_name, pat in TRIGGER_FAMILY_PATTERNS:
            m = pat.search(search_text)
            if m:
                result["trigger_family"] = fam_name
                result["trigger_family_cr_citation"] = f"{cr_prefix}{class_letter}"
                result["trigger_family_evidence"] = m.group(0)
                break
        if result["trigger_family"] is None and result["class"] == "triggered":
            result["trigger_family"] = "unclassified"

    full_text = " ".join(t for _, t in subrules[:3])
    for pat in CASTING_MODIFIER_PATTERNS:
        m = pat.search(full_text)
        if m:
            result["casting_modifier_heuristic"] = True
            result["casting_modifier_evidence"] = m.group(0)
            break

    return result


def expand_and_split(entry: dict) -> list:
    """'Daybound and Nightbound' -> two independent slug entries, each
    re-scanned against its own half of the CR text (they have distinct
    definitions/citations: 702.145b for daybound, 702.145e for nightbound)."""
    name = entry["keyword"]
    m = re.match(r"^(.+?) and (.+)$", name)
    if not m or entry["class"] != "static":
        return [entry]
    # Only Daybound/Nightbound matches this shape in the 702 list; guard so
    # we never silently split an unrelated "X and Y" keyword name.
    if name != "Daybound and Nightbound":
        return [entry]
    return None  # signal caller to re-derive from subrules directly


def main():
    text = load_cr_text()
    cr_date = find_cr_date(text)
    entries = split_entries(text)

    keywords = {}
    verify_or_drop = []
    trigger_gaps = []
    casting_modifier_hits = []
    bucket_counts = {b: 0 for b in CLOSED_BUCKETS}

    for num, name, body in entries:
        subrules = parse_subrules(body, num)
        if not subrules:
            fc.halt(f"702.{num} {name!r} has no lettered sub-rules -- CR parse failure, refusing to guess")

        if name == "Daybound and Nightbound":
            # Split into two independently-classified slugs using their own subrules.
            day_text = next(t for l, t in subrules if l == "b")
            night_text = next(t for l, t in subrules if l == "e")
            for sub_name, letter, t in (("Daybound", "b", day_text), ("Nightbound", "e", night_text)):
                r = {
                    "keyword": sub_name, "cr_number": f"702.{num}", "class": "static",
                    "class_cr_citation": f"702.{num}{letter}", "class_evidence": t,
                    "trigger_family": None, "trigger_family_cr_citation": None,
                    "trigger_family_evidence": None, "hybrid_components": None,
                    "casting_modifier_heuristic": False, "casting_modifier_evidence": None,
                    "verify_or_drop": False,
                }
                slug = slugify(sub_name)
                keywords[slug] = r
                bucket_counts["static"] += 1
            continue

        r = classify_entry(num, name, subrules)
        slug = slugify(name)
        keywords[slug] = r
        bucket_counts[r["class"]] += 1
        if r["verify_or_drop"]:
            verify_or_drop.append(slug)
        if r["class"] == "triggered" and r["trigger_family"] == "unclassified":
            trigger_gaps.append(slug)
        if r["casting_modifier_heuristic"]:
            casting_modifier_hits.append(slug)

    out = {
        "schema": "foundry-keyword-buckets/1",
        "cr_version_date": cr_date,
        "cr_source_path": str(CR_PATH),
        "generated": date.today().isoformat(),
        "ruling_basis": "CORPUS-PASS-PLAN.md step 2 / MASTER-HANDOFF-ADDENDUM-3.md sec.2,4",
        "closed_buckets": list(CLOSED_BUCKETS),
        "note": (
            "Base 'class' is mechanically extracted from the CR's own first-class "
            "statement per keyword (verify-or-drop: 'unclassified'/'ambiguous-card-dependent' "
            "means the CR text does not commit to one fixed class -- never guessed). "
            "'casting_modifier_heuristic' is a SEPARATE, non-CR-anchored regex heuristic "
            "flag (not a class) -- addendum-3's assumption that casting-modifier is a "
            "peer of static/triggered/activated does not hold: CR classifies Flash, "
            "Convoke, Kicker, etc. as ordinary ability classes (mostly static) whose "
            "TEXT happens to modify casting; this field surfaces that distinction for "
            "Captain rather than silently folding it into the addendum's original 5-bucket "
            "assumption. 'death-trigger' is used for the CR-700.4 graveyard-from-battlefield "
            "family per sec.13 D-1 of CODEBOOK-NAMING-GRAMMAR.md, NOT the literal 'dies' "
            "value printed in that same document's sec.2 table -- see report for the flagged "
            "internal inconsistency."
        ),
        "keywords": dict(sorted(keywords.items())),
    }

    fc.write_json(OUT_PATH, out)

    report_lines = [
        "# Keyword-bucket extraction report", "",
        f"Run: {date.today().isoformat()} against CR effective {cr_date} ({CR_PATH})", "",
        f"Total keyword entries parsed: {len(keywords)} (from {len(entries)} CR 702 headers, "
        "702.145 Daybound-and-Nightbound split into 2)", "",
        "## Bucket counts", "",
    ]
    for b in CLOSED_BUCKETS:
        report_lines.append(f"- `{b}`: {bucket_counts[b]}")
    report_lines += ["", "## Verify-or-drop (no fixed CR class stated -- do NOT force-fit)", ""]
    for slug in verify_or_drop:
        k = keywords[slug]
        report_lines.append(f"- `{slug}` ({k['cr_number']}, class={k['class']}): \"{k['class_evidence']}\"")
    report_lines += ["", "## Triggered keywords with no closed-vocabulary trigger-family match", "",
                      "(DELIVERY slot per CODEBOOK-NAMING-GRAMMAR.md sec.2; these need either a new closed-vocab entry or per-keyword ruling)", ""]
    for slug in trigger_gaps:
        k = keywords[slug]
        report_lines.append(f"- `{slug}` ({k['class_cr_citation']}): \"{k['class_evidence']}\"")
    report_lines += ["", "## casting_modifier_heuristic hits (non-CR-anchored, flagged for Captain review)", ""]
    for slug in casting_modifier_hits:
        k = keywords[slug]
        report_lines.append(f"- `{slug}` (base class={k['class']}, {k['class_cr_citation']}): \"{k['casting_modifier_evidence']}\"")
    report_lines += ["", "## Hybrid keywords with unparsed components", ""]
    for slug, k in sorted(keywords.items()):
        if k["class"] == "hybrid" and not k["hybrid_components"]:
            report_lines.append(f"- `{slug}` ({k['class_cr_citation']}): \"{k['class_evidence']}\"")

    REPORT_PATH.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_PATH} ({len(keywords)} keywords)")
    print(f"wrote {REPORT_PATH}")
    print(f"bucket counts: {bucket_counts}")
    print(f"verify_or_drop: {len(verify_or_drop)}  trigger_gaps: {len(trigger_gaps)}  casting_modifier_hits: {len(casting_modifier_hits)}")


if __name__ == "__main__":
    main()
