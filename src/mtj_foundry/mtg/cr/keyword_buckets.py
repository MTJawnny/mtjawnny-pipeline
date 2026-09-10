"""CR 702 keyword buckets — L2, CR-only derivation.

## What this owns

The reusable half of the keyword-bucket extraction: CR 702 entry and sub-rule
parsing, the closed bucket vocabulary, `classify_entry`, `slugify`, and the pure
`build_registry()` derivation lifted out of the legacy `main()`.

## What it deliberately does NOT own

Output paths, the run-metadata envelope (`generated` date, `cr_source_path`),
file writes, the Markdown report and the CLI all stay in the legacy operator
shell. A run date inside a derived payload makes the payload undiffable, which
is why `build_registry()` returns the DERIVATION and the shell wraps it.

`expand_and_split` was dead at the accepted base and its accepted disposition is
NOT PROMOTED, so it does not appear here.

CR access is `mtg/cr/edition` — this module parses no CR location of its own and
duplicates no CR reading.

## Layer law

Imports stdlib and `mtj_foundry.mtg.cr.edition` only. Never `mtg/shapes/**`,
never `experiments`, never a process exit.
"""

from __future__ import annotations

import re

from mtj_foundry.mtg.cr import edition as _edition

__all__ = ["KeywordBucketError", "CLOSED_BUCKETS", "slugify", "split_entries",
           "parse_subrules", "classify_entry", "build_registry", "cr_text",
           "cr_date"]


class KeywordBucketError(RuntimeError):
    """A CR 702 bucket parse the pipeline refuses to proceed on."""


CR_PATH = _edition.CR_PATH


def cr_text(path=None) -> str:
    """The normalized CR. Location and formatting both owned by `edition`."""
    return _edition.text(path or CR_PATH)


def cr_date(text: str = None) -> str:
    """The CR's effective date, from the same owner."""
    return _edition.effective_date(text)


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

# F1 fix (2026-07-31 walk ratification): a keyword whose class is split across
# SEPARATE lettered subrules by card type (Ascend: 702.131a "on an instant or
# sorcery spell represents a spell ability" / 702.131b "on a permanent
# represents a static ability") is a genuine multi-class statement and must
# classify as hybrid, not just whichever subrule happens to be scanned first.
# The original code only ever inspected the single subrule where the FIRST
# TYPE_MENTION_RE hit occurred (scan_window loop breaks on first match), so a
# second, independently-declared class in a later subrule was silently
# dropped. This is intentionally much stricter than TYPE_MENTION_RE (which
# free-scans for "<class> ability/effect" anywhere in a subrule's preamble --
# necessary to catch same-subrule compounds like Modular's "represents both a
# static ability and a triggered ability", but far too loose to also gate a
# cross-subrule merge: incidental mentions like Split Second 702.61b
# ("Triggered abilities trigger and are put on the stack as normal...",
# describing OTHER cards' triggered abilities, not Split Second's own class)
# or Tribute 702.104b ("Objects with tribute have triggered abilities that
# check...") would otherwise be misread as a second class declaration).
# Verified empirically against all 194 CR 702 entries (2026-07-31): this
# pattern fires on 2+ distinct classes for Ascend ONLY -- no other keyword's
# extraction changes.
TYPE_CONDITIONAL_CLASS_RE = re.compile(
    r"\bon an? [^.]{0,60}?(?:represents|is) an? (static|triggered|activated|spell|replacement) abilit", re.I)


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

    # F1 cross-subrule merge (see TYPE_CONDITIONAL_CLASS_RE comment above):
    # only applies when the class found above is a single plain CR ability
    # class -- ambiguous-card-dependent/special-action/rules-modifying/
    # characteristic-defining/evasion/hybrid are already resolved and are
    # never a type-conditional class split.
    merged = False
    if result["class"] in ("static", "triggered", "activated", "spell", "replacement"):
        conditional_classes = []
        conditional_letters = []
        for letter, text in scan_window:
            means_idx = text.find("” means")
            preamble = text[:means_idx] if means_idx != -1 else text
            for m in TYPE_CONDITIONAL_CLASS_RE.finditer(preamble):
                v = m.group(1).lower()
                if v not in conditional_classes:
                    conditional_classes.append(v)
                    conditional_letters.append(letter)
        if len(conditional_classes) > 1:
            merged = True
            result["class"] = "hybrid"
            result["hybrid_components"] = conditional_classes
            result["class_cr_citation"] = "/".join(f"{cr_prefix}{l}" for l in conditional_letters)
            result["class_evidence"] = " | ".join(
                t for l, t in scan_window if l in conditional_letters)

    if not merged:
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




def build_registry(text: str = None) -> dict:
    """The DERIVED keyword-bucket registry. No metadata, no I/O, no printing.

    Lifted out of the legacy `main()` (R5): the derivation was always pure, but
    it was interleaved with the run date, the output path and the Markdown
    report, so nothing could consume it without writing a file.

    What comes back is only what the CR decides -- keywords, bucket counts and
    the three review lists. The envelope (`schema`, `cr_version_date`,
    `cr_source_path`, `generated`, the ruling-basis note) is the operator
    shell's, which is what makes THIS comparable run-to-run.

    The 702.145 Daybound/Nightbound split is preserved exactly: the CR gives one
    header two independently-classified abilities, and each is classified from
    its own sub-rule rather than the pair being collapsed.
    """
    text = text if text is not None else cr_text()
    entries = split_entries(text)

    keywords = {}
    verify_or_drop = []
    trigger_gaps = []
    casting_modifier_hits = []
    bucket_counts = {b: 0 for b in CLOSED_BUCKETS}

    for num, name, body in entries:
        subrules = parse_subrules(body, num)
        if not subrules:
            raise KeywordBucketError(
                f"702.{num} {name!r} has no lettered sub-rules -- CR parse "
                f"failure, refusing to guess")

        if name == "Daybound and Nightbound":
            # Split into two independently-classified slugs using their own subrules.
            day_text = next(t for l, t in subrules if l == "b")
            night_text = next(t for l, t in subrules if l == "e")
            for sub_name, letter, t in (("Daybound", "b", day_text),
                                        ("Nightbound", "e", night_text)):
                r = {
                    "keyword": sub_name, "cr_number": f"702.{num}", "class": "static",
                    "class_cr_citation": f"702.{num}{letter}", "class_evidence": t,
                    "trigger_family": None, "trigger_family_cr_citation": None,
                    "trigger_family_evidence": None, "hybrid_components": None,
                    "casting_modifier_heuristic": False, "casting_modifier_evidence": None,
                    "verify_or_drop": False,
                }
                keywords[slugify(sub_name)] = r
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

    return {
        "closed_buckets": list(CLOSED_BUCKETS),
        "keywords": dict(sorted(keywords.items())),
        "bucket_counts": bucket_counts,
        "verify_or_drop": verify_or_drop,
        "trigger_gaps": trigger_gaps,
        "casting_modifier_hits": casting_modifier_hits,
        "n_entries": len(entries),
    }
