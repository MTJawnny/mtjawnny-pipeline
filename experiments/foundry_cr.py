#!/usr/bin/env python3
"""THE ONE PLACE THAT KNOWS HOW A COMPREHENSIVE RULES FILE IS FORMATTED.

WHY THIS EXISTS
---------------
The 2026-08-07 CR edition is not a drop-in replacement for the vendored
2026-06-19 one. Same content, different markup:

    2026-08-07:  **205.2a.** The card types are artifact, battle, …
    2026-06-19:  205.2a The card types are artifact, battle, …

Every CR parser in this repo keys on the plain shape (`load_702`,
`type_vocabulary`, CR 113.3 / 120.1 / 205 / 207.2c / 400.1 / 701 / 702), so a
file copy makes those enumerations return empty or partial. The halt-guards
would fire — that is them working — but the fix is not a file copy.

Ratified 2026-08-09: **NORMALIZE AT READ TIME, NEVER TRANSLATE THE FILE.**
Translating the CR is transcribing it, which CLAUDE.md forbids outright, and a
translated file would need its own conservation audit forever after. So the new
file stays pristine, and this module hands every parser the shape it already
expects. One definition of "CR formatting", one place to fix it.

WHY THE BOLD FORM IS THE BETTER SOURCE, and is therefore kept
------------------------------------------------------------
`**605.1a.**` at line start is an UNAMBIGUOUS rule marker. In the plain form a
parser cannot tell `605.1a` opening a line from `605.1a` cited mid-sentence
without extra context. The ambiguity stays out of the file; the stripping lives
here.

THE CONSERVATION LAW — every transformation is a PURE DELETION
--------------------------------------------------------------
CLAUDE.md, from the 2026-08-04 hyphen disaster: *"A CENSUS CANNOT ANSWER 'did
anything get LOST' — conservation can."* Every rule below deletes markup
characters and never substitutes, reorders or inserts:

    **205.2a.** The …   ->   205.2a The …      deleted: * * . * *
    **205.2.** Card …   ->   205.2. Card …     deleted: * * * *
    > **Example:** …    ->   Example: …        deleted: > ␠ * * * *
    ### 100. General    ->   ## 100. General   deleted: #

So the law this module asserts on EVERY line is that the normalized line is a
subsequence of the raw line whose only deleted characters come from the markup
set. That is strong enough to catch the greedy-regex class of
damage, which a reassembly check cannot see, and it is
asserted per line rather than per file so a single damaged line halts the run.
(The damage it is aimed at: a greedy span regex eating everything between the
first and last delimiter on a line, which a reassembly check cannot see because
kept + removed still reassembles perfectly.)

The content guard is separate and asserts CONTENT, not cardinality — the CR 205
Oxford-comma lesson, where `len() >= 15` stayed green while the last member of
every list was destroyed.

USAGE
    import foundry_cr
    txt = foundry_cr.text()             # normalized, cached
    foundry_cr.effective_date(txt)      # "August 7, 2026"

    python3 experiments/foundry_cr.py             # report + self-test
    python3 experiments/foundry_cr.py --selftest  # guards only
"""
import re
import sys
import argparse
import collections
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402

# ---------------------------------------------------------------------------
# WHERE THE CR LIVES
# ---------------------------------------------------------------------------
# CLAUDE.md names the CR as one of exactly two documents read by absolute path,
# because it used to be site-resident and gitignored there. The 2026-08-07
# edition is TRACKED IN THIS REPO, which is strictly better — it has version
# history, so a future refresh is a diff rather than an act of faith.
CR_PATH = fc.REPO_ROOT / "docs" / "MTG_Comprehensive_Rules_2026-08-07_LLM.md"

# The 2026-06-19 edition, kept reachable so a refresh can be VERIFIED as a
# comparison rather than taken on trust. Never read by the pipeline.
PRIOR_CR_PATH = (Path.home() / "Projects" / "mtjawnny.github.io" / "docs"
                 / "mtg-comprehensive-rules.md")

# `MTJ_CR_PATH=<file>` runs the WHOLE pipeline against another edition. This is
# what makes a CR refresh a measurement instead of a leap: the routing diff can
# hold the code fixed and move only the rules, which is the one thing that
# separates "the refresh moved this line" from "my edit moved this line". A CR
# refresh is the only change in this system that can move routing with no code
# edit at all, because the vocabulary is parsed at run time.
if "MTJ_CR_PATH" in __import__("os").environ:
    CR_PATH = Path(__import__("os").environ["MTJ_CR_PATH"]).expanduser()

# ---------------------------------------------------------------------------
# THE MARKUP THIS MODULE KNOWS ABOUT
# ---------------------------------------------------------------------------
# A rule marker is `**<number>.**` at line start. Subrules carry a letter
# (`205.2a`) and the plain form prints NO trailing period; numbered rules
# (`205.2`) are section headings and the plain form KEEPS it:
#
#     2026-06-19:  205.2. Card Types
#     2026-06-19:  205.2a The card types are …
#
# Two-letter subrules exist as of this edition (704.5aa) and the reformatting
# tool missed them — see `--report`. The pattern accepts them so that a future
# edition which bolds them normalizes identically.
_BOLD_RULE = re.compile(r"^\*\*(\d{3}\.\d+[a-z]{0,2})\.\*\*(?=\s|$)")

# `> **Example:** …` is CR example text lifted into a blockquote for
# navigation. The plain form is `Example: …`, which `foundry_keyword_buckets`
# tests for by `startswith` when it drops examples from a keyword's sub-rules.
_QUOTE_LABEL = re.compile(r"^>\s+\*\*([^*]+?):\*\*\s")

# Navigation headings sit one level deeper than the plain form (`### 100.
# General` where the plain edition writes `## 100. General`). Nothing in this
# repo parses a CR heading — every parser keys on the rule number — but the
# dedent is free and keeps the normalized text a true drop-in.
_HEADING = re.compile(r"^(#{2,})(\s)")

# Whatever bold survives the rules above is a navigation label (`**Glossary**`,
# `**1. Game Concepts**`, the effective-date line). Its content is stripped of
# the wrapper only — and the wrapper is required to hold no asterisk of its
# own, because CR 208.2 PRINTS A LITERAL ASTERISK ("power and toughness each
# equal to 1+*") and a blanket `\*\*` strip is one edit away from eating it.
_BOLD_LABEL = re.compile(r"\*\*([^*]+?)\*\*")

# Characters a normalization step is permitted to delete. Anything else
# disappearing from a line is damage, and halts.
_MARKUP_CHARS = set("*#>. ")

# ---------------------------------------------------------------------------
# THE CONTENT GUARD
# ---------------------------------------------------------------------------
# ASSERT CONTENT, NOT CARDINALITY. A count cannot see a substitution: the
# Oxford-comma defect kept `len() == 15` correct while `vanguard` was replaced
# by `and vanguard`. So the guard names actual line openings that every parser
# in this repo depends on, one per CR area, and each is quoted from the rule it
# anchors. A normalized file that cannot produce these is not usable.
_REQUIRED_ANCHORS = (
    ("113.3a Spell abilities are", "CR 113.3 ability classes (cr702_classes.CLASS_RULE)"),
    ("120.1. Objects can deal damage to",
     "CR 120.1 damage recipients (build_cr_enumerations)"),
    ("205.2a The card types are", "CR 205.2a card types (type_vocabulary)"),
    ("205.4a ", "CR 205.4a supertypes (type_vocabulary)"),
    ("207.2c ", "CR 207.2c ability words (build_cr_enumerations)"),
    ("400.1. A zone is", "CR 400.1 zones (build_cr_enumerations)"),
    ("701.1. ", "CR 701 keyword actions (foundry_cr_checks.keyword_actions)"),
    ("702.6a Equip is an activated ability",
     "CR 702.Na keyword classes (load_702 / classify)"),
    ("702.6. Equip", "CR 702.N keyword headings (load_702.HEADER)"),
)

# ---------------------------------------------------------------------------
# THE ENCODING GUARD — and its DECLARED register
# ---------------------------------------------------------------------------
# MEASURED 2026-08-09, `foundry_cr_edition_diff.py`: the 2026-08-07 reformatting
# introduced MOJIBAKE — UTF-8 bytes decoded as Latin-1 — in exactly one rule.
# CR 206.3a is City in a Bottle's Arabian Nights name list, and 7 characters in
# it are damaged:
#
#     Dandân -> DandÃ¢n      El-Hajjâj -> El-HajjÃ¢j    Ghazbán -> GhazbÃ¡n
#     Junún  -> JunÃºn       Juzám     -> JuzÃ¡m        Khabál  -> KhabÃ¡l
#     Ring of Ma’rûf -> Ma’rÃ»f
#
# Those are the ONLY 7, and the prior edition has zero — measured, not sampled:
# `á â ú û` appear in the whole CR only inside 206.3a, and all four are gone
# from the new file. The curly apostrophe (U+2019) is untouched throughout, so
# the damage is narrow rather than a whole-file encoding failure.
#
# This is handled the way CLAUDE.md already handles a vendored-CR discrepancy:
# **a dated register that names its evidence, and anything outside it halts.**
# A derivative that corrupts characters is exactly what "confirm the provenance"
# was asking about, and an undeclared corruption in a future edition must stop
# the run rather than become the source of a derived vocabulary.
#
# REPAIRED AT READ TIME — Captain's ruling, 2026-08-09 (decision D-CR-1 option
# b). The file stays pristine; the repair is a third read-time pass beside the
# formatting normalization, and it is confined to the rules named below. Damage
# anywhere else still HALTS.
#
# THE REPAIR IS DERIVED, NOT TYPED. `"Ã¡".encode("latin-1").decode("utf-8")`
# returns `"á"` — the corruption is its own inverse, so this is a mechanical
# transformation of the damaged bytes, in the same family as emitting both
# apostrophe forms for a CR-parsed value. A table of 7 characters typed by hand
# would be a hand-list, and this repo has one rule about those.
#
# WHAT PINS IT IS GROUND TRUTH, NOT MY ARITHMETIC. Two independent assertions,
# because a derivation still needs a positive-correctness test and this repo has
# exactly one honest source of one — the 2026-06-19 edition, which is
# WotC-derived and carries zero mojibake:
#
#   1. the derived repairs must match `repairs` below EXACTLY, both directions;
#   2. when the prior edition is reachable, the whole repaired rule must come
#      out byte-identical to it.
#
# (2) is the real check and (1) is what keeps this runnable on a machine
# without the site repo. Neither is a count.
_KNOWN_ENCODING_DAMAGE = {
    "206.3a": {
        "why": ("City in a Bottle's Arabian Nights name list (CR 206.3a). "
                "7 characters, measured 2026-08-09 by "
                "`foundry_cr_edition_diff.py` against the 2026-06-19 edition. "
                "No rule this pipeline parses reads CR 206 — but the resolver "
                "(3.11) exact-matches card NAMES, and `Juzám Djinn` is a name "
                "it will eventually meet."),
        # corrupt -> correct, and the count each appears with in CR 206.3a.
        # Verified against the prior edition, not typed from the screen.
        "repairs": {"Ã¡": ("á", 3),    # Ghazbán, Juzám, Khabál
                    "Ã¢": ("â", 2),    # Dandân, El-Hajjâj
                    "Ãº": ("ú", 1),    # Junún
                    "Ã»": ("û", 1)},   # Ring of Ma’rûf
    },
}

# `Ã`/`Â` followed by a character in the Latin-1 supplement is the signature of
# UTF-8 read as Latin-1. It cannot occur in correct CR text.
_MOJIBAKE = re.compile(r"[ÃÂ][\x80-\xbf\xa0-\xffŒœŠš"
                       r"ŸŽžƒˆ˜–—"
                       r"‘-„†-•…‰‹›"
                       r"€™]")

_cache = {}


def _pure_deletion(raw: str, norm: str) -> bool:
    """Is `norm` `raw` with only markup characters deleted?

    Walks both strings once. Every character of `raw` either matches the next
    character of `norm` or must be a markup character being dropped. This is
    the per-line form of conservation test A: nothing may be substituted,
    reordered or inserted, only removed, and only from a declared set.
    """
    i = 0
    for ch in raw:
        if i < len(norm) and norm[i] == ch:
            i += 1
        elif ch in _MARKUP_CHARS:
            continue
        else:
            return False
    return i == len(norm)


def normalize_line(raw: str) -> str:
    """One line of any supported CR edition -> the plain vendored shape.

    A line already in the plain shape passes through untouched, which is what
    makes this loader safe to point at either edition — and is how the refresh
    was verified as a rule-by-rule comparison rather than a leap.
    """
    line = raw
    m = _BOLD_RULE.match(line)
    if m:
        num = m.group(1)
        # A lettered subrule drops the marker's period; a numbered rule keeps
        # it, because that period is what `^702\.(\d+)\. ` matches on.
        head = num if num[-1].isalpha() else num + "."
        return head + line[m.end():]
    m = _QUOTE_LABEL.match(line)
    if m:
        return m.group(1) + ": " + line[m.end():]
    m = _HEADING.match(line)
    if m:
        line = m.group(1)[1:] + m.group(2) + line[m.end():]
    return _BOLD_LABEL.sub(r"\1", line)


def normalize(raw: str) -> str:
    """Whole file, with the conservation law asserted on every line."""
    out = []
    for n, line in enumerate(raw.split("\n"), start=1):
        norm = normalize_line(line)
        if not _pure_deletion(line, norm):
            fc.halt(
                f"CR normalization is not a pure deletion at line {n}. A "
                f"normalization step may only REMOVE markup characters "
                f"({''.join(sorted(_MARKUP_CHARS))!r}); this one changed the "
                f"text.\n  raw:  {line[:120]!r}\n  norm: {norm[:120]!r}")
        out.append(norm)
    return "\n".join(out)


_ANY_RULE = re.compile(r"^(\d{3}\.\d+[a-z]{0,2})(?:\.)?\s")


def _assert_encoding(norm: str, path: Path) -> None:
    """Halt on character corruption outside the declared register.

    Attribution is by CR rule, not by line number, because a line number moves
    with every edition and a rule number does not — the same reason the CR-LAG
    register is keyed on rules.
    """
    undeclared, rule = {}, "(before the first rule)"
    for n, line in enumerate(norm.splitlines(), start=1):
        m = _ANY_RULE.match(line)
        if m:
            rule = m.group(1)
        hits = _MOJIBAKE.findall(line)
        if hits and rule not in _KNOWN_ENCODING_DAMAGE:
            undeclared.setdefault(rule, (n, line[:100], hits))
    if undeclared:
        detail = "\n".join(
            f"    CR {r} (line {n}) {chars} in: {snippet!r}"
            for r, (n, snippet, chars) in sorted(undeclared.items()))
        fc.halt(
            f"{path} carries UNDECLARED character corruption — UTF-8 bytes "
            f"decoded as Latin-1 — in {len(undeclared)} rule(s):\n{detail}\n"
            f"  This repo treats the CR as ground truth and derives its "
            f"vocabulary from it at run time, so a corrupted edition must not "
            f"become that source silently. Verify against the official release, "
            f"then either fix the file or add the rule to "
            f"foundry_cr._KNOWN_ENCODING_DAMAGE with its evidence.")


def _demojibake(s: str) -> str:
    """Undo one UTF-8-read-as-Latin-1 run. Derived, never typed.

    Halts rather than returning the input on a run it cannot decode: a repair
    that silently no-ops leaves corrupted text wearing a repaired file's
    credibility, which is worse than the corruption.
    """
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError) as exc:
        fc.halt(f"cannot reverse the encoding damage in {s!r}: {exc}. This is "
                f"not the UTF-8-as-Latin-1 corruption the register describes; "
                f"do not guess at a replacement.")


def _repair_encoding(norm: str, path: Path) -> str:
    """Repair the declared encoding damage, and prove the repair was right.

    Captain's ruling 2026-08-09 (D-CR-1 option b). Runs AFTER `normalize`, as
    its own pass, because the conservation law there is pure deletion and a
    repair is a substitution — folding them together would mean neither law
    could be stated. Two passes, two laws, both asserted.
    """
    if not _MOJIBAKE.search(norm):
        return norm

    out, rule, applied = [], "(before the first rule)", collections.Counter()
    for line in norm.splitlines():
        m = _ANY_RULE.match(line)
        if m:
            rule = m.group(1)
        if rule in _KNOWN_ENCODING_DAMAGE and _MOJIBAKE.search(line):
            for corrupt in _MOJIBAKE.findall(line):
                applied[(rule, corrupt)] += 1
            line = _MOJIBAKE.sub(lambda mm: _demojibake(mm.group(0)), line)
        out.append(line)
    repaired = "\n".join(out) + ("\n" if norm.endswith("\n") else "")

    # ASSERTION 1 — the derived repairs are exactly the pinned ones, both
    # directions. A repair that fires MORE than declared is scope creep; one
    # that fires LESS means the damage moved and the register is stale.
    for rule, decl in _KNOWN_ENCODING_DAMAGE.items():
        want = {c: n for c, (_fixed, n) in decl["repairs"].items()}
        got = {c: n for (r, c), n in applied.items() if r == rule}
        if got != want:
            fc.halt(
                f"the declared encoding repair for CR {rule} in {path} does not "
                f"match what this edition actually carries.\n"
                f"    declared: {want}\n    found:    {got}\n"
                f"  Re-measure with `foundry_cr_edition_diff.py` and update the "
                f"register with its evidence. Never widen the repair to fit.")
        for corrupt, (fixed, _n) in decl["repairs"].items():
            derived = _demojibake(corrupt)
            if derived != fixed:
                fc.halt(f"the repair derived for {corrupt!r} is {derived!r}, "
                        f"but the register pins {fixed!r}. One of the two is "
                        f"wrong and this refuses to pick.")

    # ASSERTION 2 — POSITIVE CORRECTNESS, and it is the one that matters. The
    # 2026-06-19 edition is WotC-derived and carries zero mojibake, so a
    # repaired rule must come out byte-identical to it. Skipped, loudly in the
    # report rather than silently, when the prior edition is not on this
    # machine — this is a public repo and its CI has no reason to hold it.
    if path != PRIOR_CR_PATH and PRIOR_CR_PATH.exists():
        prior = {}
        for line in text(PRIOR_CR_PATH).splitlines():
            m = _ANY_RULE.match(line)
            if m and m.group(1) in _KNOWN_ENCODING_DAMAGE:
                prior[m.group(1)] = line
        for line in repaired.splitlines():
            m = _ANY_RULE.match(line)
            if m and m.group(1) in prior and line != prior[m.group(1)]:
                rule = m.group(1)
                where = next((i for i, (a, b) in
                              enumerate(zip(line, prior[rule])) if a != b),
                             min(len(line), len(prior[rule])))
                fc.halt(
                    f"CR {rule} does not match the 2026-06-19 edition after "
                    f"repair, first difference at character {where}:\n"
                    f"    repaired {line[max(0, where-40):where+40]!r}\n"
                    f"    prior    {prior[rule][max(0, where-40):where+40]!r}\n"
                    f"  Either the repair is wrong or WotC reworded the rule. "
                    f"Read it before touching the register.")
    return repaired


def _assert_parseable(norm: str, path: Path) -> None:
    missing = [(a, why) for a, why in _REQUIRED_ANCHORS
               if not re.search(r"(?m)^" + re.escape(a), norm)]
    if missing:
        detail = "\n".join(f"    {a!r:44s} needed by {why}" for a, why in missing)
        fc.halt(
            f"{path} does not normalize to a parseable CR — these rule lines "
            f"are absent after normalization:\n{detail}\n"
            f"  The edition's formatting has changed again. Fix "
            f"foundry_cr.normalize_line; never fall back to a remembered list, "
            f"and never translate the file.")
    if re.search(r"(?m)^\*\*\d", norm):
        survivors = re.findall(r"(?m)^\*\*\d[^\s*]*[.*]*", norm)[:5]
        fc.halt(f"bold rule markers survived normalization of {path}: "
                f"{survivors}. Fix _BOLD_RULE.")


def text(path: Path = None) -> str:
    """The CR, normalized to the plain shape every parser here expects."""
    path = Path(path) if path else CR_PATH
    key = str(path)
    if key not in _cache:
        if not path.exists():
            fc.halt(f"Comprehensive Rules not found at {path}. This repo "
                    f"derives its vocabulary from the CR at run time and has "
                    f"no fallback by design.")
        norm = normalize(path.read_text(encoding="utf-8", errors="strict"))
        _assert_parseable(norm, path)
        # ORDER IS LOAD-BEARING. `_assert_encoding` halts on damage OUTSIDE the
        # register, and it must run BEFORE the repair — afterwards it could not
        # tell "never damaged" from "quietly repaired", which is the whole
        # difference between a declared exception and a silent one.
        _assert_encoding(norm, path)
        norm = _repair_encoding(norm, path)
        if _MOJIBAKE.search(norm):
            left = sorted(set(_MOJIBAKE.findall(norm)))
            fc.halt(f"encoding damage survived the repair pass in {path}: "
                    f"{left}. The register claims to cover every occurrence; "
                    f"it does not.")
        _cache[key] = norm
    return _cache[key]


def lines(path: Path = None) -> list:
    return text(path).splitlines()


def effective_date(txt: str = None) -> str:
    """The rules-effective date, from the CR's own sentence.

    Never the file mtime — that is the copy date. The 2026-06-19 edition read
    `Jul 16` on disk, which is how the snapshot lag went unnoticed.
    """
    txt = txt if txt is not None else text()
    m = re.search(r"effective as of ([A-Za-z]+ \d{1,2}, \d{4})", txt)
    if not m:
        fc.halt("CR has no 'effective as of <date>' sentence — cannot version "
                "anything derived from it, and refusing to guess.")
    return m.group(1)


# ---------------------------------------------------------------------------
# SELF-TEST — a guard that has never been shown to fail is not known to be a
# guard (CLAUDE.md, 2026-08-09). Each case below is a NEGATIVE control aimed at
# the code path, not at the module's name.
# ---------------------------------------------------------------------------
_CASES = [
    # (label, raw, expected-or-None-if-must-halt)
    ("bold subrule drops its period",
     "**205.2a.** The card types are artifact, battle, and vanguard.",
     "205.2a The card types are artifact, battle, and vanguard."),
    ("bold numbered rule KEEPS its period",
     "**702.6.** Equip", "702.6. Equip"),
    ("two-letter subrule",
     "**704.5aa.** If a player controls a permanent",
     "704.5aa If a player controls a permanent"),
    ("plain line is untouched (the prior edition still loads)",
     "205.2a The card types are artifact.",
     "205.2a The card types are artifact."),
    ("blockquoted example becomes a plain Example: line",
     "> **Example:** Lost Order of Jarkeld has power 1+*.",
     "Example: Lost Order of Jarkeld has power 1+*."),
    ("heading dedents one level",
     "### 702. Keyword Abilities", "## 702. Keyword Abilities"),
    ("top-level heading is left alone",
     "# Magic: The Gathering Comprehensive Rules",
     "# Magic: The Gathering Comprehensive Rules"),
    ("navigation label loses only its wrapper",
     "**These rules are effective as of August 7, 2026.**",
     "These rules are effective as of August 7, 2026."),
    # CR 208.2 prints a literal asterisk. A blanket `\*\*` strip would survive
    # this line by luck; the test pins that it must not be attempted.
    ("a LITERAL CR asterisk survives",
     "**208.2.** Some creature cards have power and/or toughness of */*.",
     "208.2. Some creature cards have power and/or toughness of */*."),
    ("a rule number cited MID-SENTENCE is not a marker",
     "See rule 605.1a for mana abilities.",
     "See rule 605.1a for mana abilities."),
]


def _selftest() -> int:
    bad = 0
    for label, raw, want in _CASES:
        got = normalize_line(raw)
        ok = got == want and _pure_deletion(raw, got)
        print(f"  [{'ok' if ok else 'FAIL'}] {label}")
        if not ok:
            bad += 1
            print(f"        raw  {raw!r}\n        want {want!r}\n        got  {got!r}")

    # Guard D — the conservation law must REJECT a deliberately broken
    # normalizer. Without this the law is decoration.
    broken = [("substitution", "205.2a x", "205.2a y"),
              ("insertion", "205.2a x", "205.2a xy"),
              ("greedy span eaten", "205.2a (see 300) x", "205.2a x"),
              ("reordering", "205.2a ab", "205.2a ba")]
    for label, raw, fake in broken:
        if _pure_deletion(raw, fake):
            print(f"  [FAIL] conservation accepted a {label}")
            bad += 1
        else:
            print(f"  [ok] conservation rejects a {label}")

    # And it must ACCEPT a legitimate markup deletion, or it is merely strict.
    if not _pure_deletion("**205.2a.** x", "205.2a x"):
        print("  [FAIL] conservation rejects a legitimate markup deletion")
        bad += 1
    else:
        print("  [ok] conservation accepts a legitimate markup deletion")

    # The encoding guard, aimed at the CODE PATH rather than at the tool's
    # name: three of eight negative controls on 2026-08-09 were mis-aimed and
    # each first read as "this gate is broken".
    def halts(text):
        try:
            _assert_encoding(text, Path("<selftest>"))
            return False
        except SystemExit:
            return True

    declared = next(iter(_KNOWN_ENCODING_DAMAGE))
    checks = [
        ("encoding guard fires on an UNDECLARED corrupted rule",
         "702.6a Equip is an activated ability of JuzÃ¡m cards.", True),
        (f"encoding guard stays quiet on the declared rule ({declared})",
         f"{declared} Those names are DandÃ¢n, JuzÃ¡m Djinn.", False),
        ("encoding guard stays quiet on correct accented text",
         "206.3a Those names are Dandân, Juzám Djinn, Ring of Ma’rûf.", False),
        ("encoding guard stays quiet on the curly apostrophe alone",
         "205.3i The land types are Urza’s, Desert.", False),
    ]
    for label, line, want_halt in checks:
        got = halts(line)
        if got == want_halt:
            print(f"  [ok] {label}")
        else:
            print(f"  [FAIL] {label} (halted={got}, wanted {want_halt})")
            bad += 1

    # THE REPAIR (D-CR-1b). Every case is aimed at the code path, not at the
    # feature's name — the three mis-aimed negative controls of 2026-08-09 each
    # first read as "this gate is broken".
    if _demojibake("JuzÃ¡m Djinn") == "Juzám Djinn":
        print("  [ok] repair is DERIVED from the damage, not typed")
    else:
        print("  [FAIL] repair derivation is wrong")
        bad += 1

    def repairs(text_in):
        try:
            return _repair_encoding(text_in, PRIOR_CR_PATH)   # skips assert 2
        except SystemExit:
            return "<HALTED>"

    rule = declared
    repair_cases = [
        ("declared damage is repaired",
         f"{rule} Those names are DandÃ¢n, GhazbÃ¡n Ogre, JuzÃ¡m Djinn, "
         f"KhabÃ¡l Ghoul, JunÃºn Efreet, Ring of Ma’rÃ»f, El-HajjÃ¢j.",
         f"{rule} Those names are Dandân, Ghazbán Ogre, Juzám Djinn, "
         f"Khabál Ghoul, Junún Efreet, Ring of Ma’rûf, El-Hajjâj."),
        # A count that does not match the register means the damage MOVED.
        # Widening the repair to fit is how a register stops being evidence.
        ("a DIFFERENT amount of damage halts rather than being absorbed",
         f"{rule} Those names are DandÃ¢n and JuzÃ¡m Djinn.", "<HALTED>"),
        # Clean text must survive the pass untouched, or the repair is a
        # rewrite wearing a repair's name.
        ("already-correct text passes through unchanged",
         f"{rule} Those names are Dandân, Juzám Djinn.",
         f"{rule} Those names are Dandân, Juzám Djinn."),
    ]
    for label, src, want in repair_cases:
        got = repairs(src)
        if got == want:
            print(f"  [ok] {label}")
        else:
            print(f"  [FAIL] {label}\n        got  {got!r}\n        want {want!r}")
            bad += 1
    return bad


def _report() -> None:
    txt = text()
    ls = txt.splitlines()
    raw = CR_PATH.read_text(encoding="utf-8", errors="strict").splitlines()
    rule_rx = re.compile(r"^\d{3}\.\d+[a-z]{0,2}[\s.]")
    print(f"CR file            {CR_PATH}")
    print(f"effective          {effective_date(txt)}")
    print(f"lines              {len(ls)}")
    print(f"rule-numbered      {sum(1 for l in ls if rule_rx.match(l))}")
    print(f"lines normalized   {sum(1 for a, b in zip(raw, ls) if a != b)}")
    print(f"curly apostrophes  {txt.count(chr(0x2019))}")
    print(f"mojibake remaining {len(_MOJIBAKE.findall(txt))}")
    print("\nDECLARED ENCODING DAMAGE, repaired at read time (D-CR-1b, Captain "
          "2026-08-09).\nAnything outside this register HALTS.")
    for rule, decl in sorted(_KNOWN_ENCODING_DAMAGE.items()):
        fixes = "  ".join(f"{c!r}->{f!r}×{n}"
                          for c, (f, n) in sorted(decl["repairs"].items()))
        print(f"  CR {rule}   {fixes}\n    {decl['why']}")
    if PRIOR_CR_PATH.exists():
        print("    verified byte-identical to the 2026-06-19 edition after "
              "repair.")
    else:
        print("    ⚠ the 2026-06-19 edition is not on this machine, so the "
              "repair was checked\n      against its pinned fixture ONLY — the "
              "positive-correctness half did\n      not run. Stated, not "
              "silently skipped.")
    print("\nanchors required by the parsers, all present:")
    for a, why in _REQUIRED_ANCHORS:
        print(f"  {a!r:44s} {why}")
    if PRIOR_CR_PATH.exists():
        prior = text(PRIOR_CR_PATH)
        print(f"\nprior edition      {effective_date(prior)}  ({PRIOR_CR_PATH})")
        print(f"  rule-numbered    "
              f"{sum(1 for l in prior.splitlines() if rule_rx.match(l))}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true",
                    help="run the guards only")
    args = ap.parse_args()
    if not args.selftest:
        _report()
        print()
    print("SELF-TEST — every guard shown to both pass and fail.")
    print("Each negative control prints its guard's real STOP message to "
          "stderr. Those\nare the controls WORKING; the verdict is the "
          "[ok]/[FAIL] column below.")
    bad = _selftest()
    if bad:
        print(f"\n{bad} self-test failure(s)")
        return 1
    print("\nall guards behaved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
