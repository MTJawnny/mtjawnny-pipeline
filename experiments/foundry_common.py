#!/usr/bin/env python3
"""Shared corpus-loading and card-record helpers for the T3 Axis Foundry
(T3-AXIS-FOUNDRY-v3.md). Used by foundry_emit.py, foundry_reconcile.py, and
experiments/measure/axis_foundry.py -- kept here once instead of copied
three times. Never imported by tier_engine.py itself.
"""
import sys
import json
import re
from pathlib import Path

# --- C8.5A COMPATIBILITY BOOTSTRAP -- TEMPORARY, AND NOT A LAYOUT API -------
#
# `mtj_foundry.paths.ProjectPaths` is the ratified permanent owner of
# repository-relative layout, but the package is not installed and legacy tools
# are invoked as loose scripts, so `import mtj_foundry` fails from the legacy
# execution environment. These three lines exist ONLY to close that gap without
# asking anyone to set PYTHONPATH by hand.
#
# `_BOOTSTRAP_ROOT` and the literal `"src"` are the ONE piece of layout knowledge
# that genuinely cannot be delegated: it is the knowledge needed to LOCATE the
# owner, and nothing can ask the owner where it lives before importing it. It is
# deliberately private, deliberately used for nothing else, and is NOT a second
# layout API -- every other path below comes from ProjectPaths. When the package
# is properly installed (later C8 step 5), these lines delete outright and
# nothing else in this module changes.
#
# The derivation is the SAME pure lexical one this module already used
# (`Path(__file__).resolve().parents[1]`); no filesystem discovery, no
# `discover_root`, and no new import-time assumption beyond what was here before.
_BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
_BOOTSTRAP_SRC = _BOOTSTRAP_ROOT / "src"
if str(_BOOTSTRAP_SRC) not in sys.path:
    sys.path.insert(0, str(_BOOTSTRAP_SRC))
from mtj_foundry.paths import ProjectPaths  # noqa: E402

_PATHS = ProjectPaths.for_root(_BOOTSTRAP_ROOT)

# ---------------------------------------------------------------------------
# Layout now comes FROM THE OWNER. These three names keep their exact previous
# values -- 134 legacy expressions delegate to them and none of them moves.
REPO_ROOT = _PATHS.root

# UNCHANGED ON PURPOSE: the engine still needs `experiments` on sys.path, and the
# upward foundry_common -> tier_engine dependency is NOT this task's to solve.
# Inserting at 0 after the bootstrap keeps `experiments` at the same precedence
# it has always had.
sys.path.insert(0, str(_PATHS.legacy_experiments))
import tier_engine as te  # noqa: E402

FOUNDRY_OUT_DIR = _PATHS.legacy_foundry_out
REVIEW_DIR = _PATHS.legacy_foundry_review

# C8.5C: the boundary also exposes the legacy pipeline-artifact directory, so
# `foundry_codebook` can stop deriving a root of its own to reach it. Like the
# three above, this is the OWNER's value -- it is not derived here.
DATA_ARTIFACTS_DIR = _PATHS.legacy_data_artifacts


def halt(message: str) -> None:
    print(f"STOP — {message}", file=sys.stderr)
    sys.exit(1)


# --- DET pattern roles -------------------------------------------------
# A ratified DET pattern is one of exactly two things:
#
#   AXIS-BEARING  its slug names a codebook axis whose membership it
#                 decides. It MUST have an active axis to apply to.
#   PRE-FILTER    a Lane-1 net that narrows the corpus for a family and
#                 is never a classifier, e.g.
#                 "rule:energy-<family> pre-filter (spends {E})".
#
# The role is carried in the slug text itself. These two helpers are the
# SINGLE definition of that fact. foundry_det_pass and
# foundry_family_sweep both read them from here; each previously derived
# the distinction independently, and that duplication is precisely how
# three ratified patterns sat orphaned and unapplied for weeks — the
# det pass silently demoted them to "prefilter" because they had no axis,
# which is the same shape as having been declared a prefilter.


def is_prefilter_pattern(pattern: dict) -> bool:
    """True iff this ratified pattern is a deliberate Lane-1 pre-filter."""
    return "pre-filter" in pattern["slug"]


def is_lattice_pattern(pattern: dict) -> bool:
    """True iff this ratified record is a LATTICE matcher -- one matcher that
    yields N concrete axes at match time, rather than one pattern owning one
    axis.

    **ITS SLUG IS A GRAMMAR TEMPLATE, NOT AN AXIS NAME.**
    `rule:targeted-<action>-<class>` carries facet placeholders and can never
    be a concrete codebook axis; the axes it produces are
    `rule:targeted-destroy-creature` and its siblings, instantiated under
    `b6 sec.11.2` (*"virtual nodes instantiate on first quote-verified member,
    no fresh ratification"*). A `pattern` of `null` is the other half of the
    same shape: there is no single regex to run.

    **THIS LIVES HERE SO THERE IS EXACTLY ONE DEFINITION.** It was
    `foundry_det_pass.is_lattice_pattern` alone, and `foundry_family_sweep`
    -- which does not import that module -- applied the ordinary
    one-pattern/one-axis orphan law to the lattice record and reported a
    BLOCKING `ratified-pattern-has-no-axis` for a slug that is virtual BY
    DESIGN. That is this repository's most expensive recurring defect (*"a
    hand-maintained MIRROR of a ratified record is trusted as the record"*)
    aimed at the sweep that exists to catch it. `foundry_det_pass` now
    delegates here; nothing re-derives the concept.

    Deliberately keyed on the RECORD'S SHAPE, never on the literal slug: a
    second lattice family ratified tomorrow is covered without an edit, which
    is the sweep's own self-calibration rule.
    """
    return isinstance(pattern.get("lattice"), dict)


def pattern_slug(pattern: dict) -> str:
    """The bare `rule:` slug, stripped of parenthetical/qualifier text."""
    return pattern["slug"].split(" (")[0].split(" ")[0]


# A DET pattern is matched against det_scan_texts() output, in which a card's
# own printed NAME has already been rewritten to CARDNAME_TOKEN ("~") by
# canonicalize_self_reference(). So a pattern that anchors only on the
# literal "this creature" silently misses every card that self-references by
# name -- and those are disproportionately the legendaries.
#
# Measured 2026-08-02 on rule:forced-attack-each-combat: 59 hits anchored on
# "this creature" alone, 67 with the token accepted, 8 missed, 0 regressions.
# The missed cards are Ruric Thar, Toski, Xantcha, Ares, Alexios, Amarant
# Coral and both Hulks -- all name-self-referencing. That is finding F-C, and
# it is why the pattern looked wrong and the model looked right.
_SELF_REF_FORMS = (
    "this creature", "this permanent", "this artifact", "this enchantment",
    "this land", "this planeswalker", "this spell", "this card",
)


def pattern_misses_cardname_token(pattern_src: str) -> list:
    """Self-reference forms this pattern anchors WITHOUT also accepting `~`.

    Empty list means the pattern is safe. Non-empty means it will silently
    under-match cards that self-reference by printed name.
    """
    if not isinstance(pattern_src, str):
        return []
    if CARDNAME_TOKEN in pattern_src:
        return []
    low = pattern_src.lower()
    return [form for form in _SELF_REF_FORMS if form in low]


def batch_paths(batch_num: int) -> dict:
    """Canonical per-batch output filenames for every foundry_*.py script.
    Batch 1 kept its original unsuffixed filenames (already committed
    before this convention existed); batch 2+ gets batch-numbered filenames
    so no two batches' artifacts ever collide. Single source of truth --
    foundry_stage1b.py, foundry_consolidate.py, and foundry_enrich.py all
    import this instead of each defining their own copy."""
    suffix = "" if batch_num == 1 else f"_batch{batch_num}"
    bsuffix = "-1" if batch_num == 1 else f"-{batch_num}"  # review/ files use batch-N.json naming
    return {
        "assembled": FOUNDRY_OUT_DIR / f"batch{batch_num}_assembled.json",
        "requests": FOUNDRY_OUT_DIR / f"stage1b_requests{suffix}.json",
        "batch_record": FOUNDRY_OUT_DIR / f"stage1b_batch{suffix}.json",
        "completion_note": FOUNDRY_OUT_DIR / f"stage1b_completion_note{suffix}.md",
        "cost_estimate": FOUNDRY_OUT_DIR / f"stage1b_cost_estimate{suffix}.json",
        "raw_results": FOUNDRY_OUT_DIR / f"stage1b_raw_results{suffix}.jsonl",
        "consolidated": FOUNDRY_OUT_DIR / f"consolidated_batch{batch_num}.json",
        "consolidate_clusters_raw": FOUNDRY_OUT_DIR / f"consolidate_clusters_raw{suffix}.json",
        "review": REVIEW_DIR / f"batch{bsuffix}.json",
        "enriched": REVIEW_DIR / f"batch{bsuffix}-enriched.json",
        "enriched_stats": REVIEW_DIR / f"batch{bsuffix}-enriched-stats.json",
        "digest": REVIEW_DIR / f"digest-batch-{batch_num}.md",
    }


def load_corpus():
    """Returns (cards: {oracle_id: raw_card}, name_index: {normalized_name: [oracle_id,...]}).
    Unfiltered/raw -- shared with tier_engine.py's other, non-foundry consumers,
    so this function's output must not change shape based on foundry-specific
    rulings. Foundry pipeline stages should use load_corpus_gated() instead
    (see Gate #0, batch-6 D1)."""
    cards = te.load_cards(te.CARDS_PATH)
    name_index = te.build_name_index(cards)
    return cards, name_index


def gate_passes(card: dict) -> bool:
    """Gate #0 (ratified batch-6 D1, 2026-07-30): a card is a valid target for
    the T3 Axis Foundry pipeline -- the DET pass, batch assembly, SYNTH, and
    reconcile -- iff it is legal or restricted in at least one Scryfall
    'legalities' format. Nowhere-legal cards (playtest/CMB1/CMB2/MB2, Unknown
    Event promos, prototype/event cards, bare token printings) fail outright.
    This is dataset-level and independent of the corroboration gate; it does
    not touch tier_engine.py's own load_cards()/CARDS_PATH consumers, which
    are out of this ruling's scope (production tier scoring, not foundry)."""
    legalities = card.get("legalities") or {}
    return any(v in ("legal", "restricted") for v in legalities.values())


def load_corpus_gated():
    """Gate #0-filtered corpus for foundry pipeline stages. Returns
    (cards, name_index, gated_out_count) -- cards/name_index contain only
    gate-passing rows; name_index is rebuilt from the filtered set so
    resolve_name() can never resolve a gated-out card by name. Raw
    load_corpus() is untouched and still available for reference/debugging."""
    cards, _ = load_corpus()
    gated_cards = {oid: c for oid, c in cards.items() if gate_passes(c)}
    gated_name_index = te.build_name_index(gated_cards)
    return gated_cards, gated_name_index, len(cards) - len(gated_cards)


def resolve_name(name: str, cards: dict, name_index: dict) -> str:
    """Exact-match name resolution, house halt-loudly discipline (pipeline
    CLAUDE.md: 'never fuzzy-matches a card name'). The corpus carries a known
    class of duplicate oracle rows sharing a display name with a set_type
    'token' entry (verified 2026-07-17: Llanowar Elves x2, Ajani's Pridemate
    x2 -- both times one entry is a real paper-legal printing, the other a
    token-set duplicate that is not a constructed-legal card). When matches
    split exactly this way, auto-resolve to the non-token entry ('paper' per
    the seed's own notes field); any OTHER ambiguity halts loudly rather than
    guessing."""
    matches = name_index.get(te.normalize_name(name), [])
    if len(matches) == 0:
        halt(f"card {name!r} matched 0 cards in the corpus — check spelling, no fuzzy fallback")
    if len(matches) == 1:
        return matches[0]

    non_token = [oid for oid in matches if cards[oid].get("set_type") != "token"]
    if len(non_token) == 1:
        return non_token[0]

    detail = ", ".join(f"{oid} (set={cards[oid].get('set')}, set_type={cards[oid].get('set_type')})" for oid in matches)
    halt(f"card {name!r} matched {len(matches)} cards, ambiguity NOT the known token-duplicate shape ({detail}) — resolve by hand")


def _extract_faces(card: dict) -> list:
    raw_faces = card.get("card_faces")
    if not raw_faces:
        return []
    faces = []
    for f in raw_faces:
        faces.append({
            "name": f.get("name") or card.get("name"),
            "mana_cost": f.get("mana_cost") or "",
            "type_line": f.get("type_line") or "",
            "oracle_text": f.get("oracle_text") or "",
            "power": f.get("power"),
            "toughness": f.get("toughness"),
            "loyalty": f.get("loyalty"),
        })
    return faces


def full_oracle_text(card: dict) -> str:
    """All-faces oracle text, newline-joined -- the root-level 'oracle_text'
    field is empty for multi-face layouts (transform/modal_dfc/adventure/
    prepare/etc.), so this always goes through te.get_raw_faces() (which
    falls back to the root field itself for single-face cards) rather than
    reading card['oracle_text'] directly. Mirrors foundry_enrich.py's own
    full_oracle_text() -- same source, same join convention."""
    return "\n".join(f["oracle_text"] for f in te.get_raw_faces(card) if f["oracle_text"])


CARDNAME_TOKEN = "~"
# CR 700.2 defines modality by the LIST and the INSTRUCTION, never by
# punctuation: *"A spell or ability is modal if it has two or more options in a
# BULLETED LIST preceded by INSTRUCTIONS FOR A PLAYER TO CHOOSE A NUMBER of
# those options, such as 'Choose one —.'"* The em-dash is the CR's EXAMPLE of
# how such a header is printed, not its definition.
#
# The old form anchored on `—\s*$` and therefore missed every header whose
# sentence CONTINUES past the mode count -- 102 lists, 259 bullets, 102 cards:
#
#   Choose three. You may choose the same mode more than once.   (CR 700.2d)
#   Choose one. If you control a commander as you cast this spell, you may …
#   An opponent chooses one —                                    (CR 700.2e)
#   Trick Arrows — Whenever Hawkeye becomes tapped, … choose up to that many.
#
# `chooses` is required by CR 700.2e (*"some spells and abilities specify that
# a player OTHER THAN THEIR CONTROLLER chooses a mode"*).
#
# A NUMBER is required, and that is what keeps the SIEGE cycle out. "As this
# enchantment enters, choose Khans or Dragons" NAMES its options instead of
# counting them, so it is not CR 700.2 modal -- and that is the right answer:
# a Siege's bullets are the permanent's OWN triggered/static abilities, gated
# on a choice made as it enters, not modes of a spell. Measured 2026-08-06,
# all 16 lists this test declines are correctly non-modal (14 Sieges,
# Celebr-8000's CR 706.3b die table, and a granted ability in quotes).
#
# Modality is confirmed STRUCTURALLY by the caller -- every consumer requires a
# bulleted list to follow -- so this line only has to recognise the
# instruction. Ratified DET preprocessing standard v1; widened 2026-08-06 on
# Captain's word ("yes let's fix this modal stoppage").
_MODAL_HEADER_RE = re.compile(
    r"\bchooses?\s+(?:one|two|three|four|five|six|seven|eight|nine|ten|"
    r"X|\d+|any number|up to \w+)\b", re.I)


# CR 706.3b: a die-roll RESULTS TABLE row -- "1—9 | …", "20 | …", "5 | …".
# THE RANGE HAS FIVE PRINTED FORMS, NOT THREE. Measured 2026-08-06 across 106
# rows: em-dash 75, plain HYPHEN 5 (Mathise, Surge Channeler prints `1-9 |`),
# single number 26. An em-dash-only test silently dropped the hyphen rows --
# the same "an inflection is not a shape" family that has now bitten this
# project four times, wearing punctuation instead of a verb ending.
#
# THE CR ENUMERATES THESE, so they are not measured -- CR 706.3a, verbatim:
# *"The possible results indicated could be A SINGLE NUMBER, a range of numbers
# with two endpoints in the form 'N1–N2,' or a range with a single endpoint in
# the form 'N+.'"*  A closed list of three, and the earlier census missed two of
# them because it counted only rows this regex ALREADY matched -- a recall
# measurement taken through the very filter under test. `N+` is why: an
# UNBOUNDED roll can exceed the die's face value ("roll a d20 AND ADD the number
# of cards in your hand"), so a table's last row is open.
#
# NOTE the CR prints `N1–N2` with an EN-DASH (U+2013) and the corpus prints an
# EM-DASH or a hyphen -- the recorded CR-vs-Scryfall character split, here in a
# rule rather than a card name. Measured: en-dash is 0 corpus-wide.
#
# Measured against CR 706.3a's three forms: N1-N2 80, N+ 49, single 26 -- 155 of
# 156 rows. `or more` is attested ZERO times and is deliberately NOT here; a
# member with no evidence is a hand-list defect regardless of how plausible.
#
# CR-LAG REGISTER ENTRY (see `_CR_LAG` in foundry_shape_extractor.py for the
# same mechanism on CR 205.3 subtypes):
#
#   `N or less`  -- ONE row, Druid of the Emerald Grove ("9 or less | Put those
#                   cards into your hand, then shuffle."). CR 706.3a's closed
#                   list does NOT include it, and it is that table's FIRST row,
#                   so excluding it costs all THREE rows -- a first-row form gap
#                   loses the whole table. Recorded as a discrepancy between two
#                   upstream sources with its evidence named, exactly as
#                   `chorus` is.
#
#                   **RE-CONFIRMED AGAINST THE 2026-08-07 EDITION, 2026-08-09.**
#                   This entry used to say "the real fix is to refresh the CR
#                   snapshot". The refresh happened and 706.3a is byte-identical
#                   — still *"a single number, a range … 'N1–N2,' or a range
#                   with a single endpoint in the form 'N+.'"* The CR is behind
#                   the printed card, not the snapshot behind the CR, so this
#                   entry is permanent until WotC catches up.
#
# Widening cannot reach a CR 721 station row (`9+ | Flying, first strike`),
# which is the same shape and a different rule: both consumers test this only
# AFTER `_ROLL_INSTRUCTION_RE` has opened a block, and a station card prints no
# roll instruction. Verified live -- 0 station rows joined.
_DIE_ROW_RE = re.compile(r"^\s*\d+\s*(?:[-–—]\s*\d+|\+|or less)?\s*\|")
# The instruction that opens such a table. The CR names the shape ("an
# instruction to roll one or more dice") and the corpus prints "roll a d20",
# "roll two six-sided dice", "roll a d20 and add the number of cards in your
# hand". Confirmed structurally: it only opens a block if rows follow.
_ROLL_INSTRUCTION_RE = re.compile(
    r"\broll\w*\b(?:[^.\n]{0,40}?)\b(?:d\d+|dice|die)\b", re.I)


# CR 711.2 (leveler) and CR 716.2 (class level bar) print the SAME sentence as
# CR 721.2: *"any abilities printed within the same text box striation are part
# of its static ability."*  But unlike the station striation, whose marker and
# abilities share ONE line, these two put the marker on its own line and the
# abilities it governs on the lines BELOW:
#
#     Level up {W}            {1}{R}: Level 2
#     LEVEL 2-6               Whenever you roll one or more dice, …
#     3/3                     {2}{R}: Level 3
#     First strike            Creatures you control have haste.
#     LEVEL 7+
#
# So `3/3` and `First strike` are governed by `LEVEL 2-6` and a proximity
# pattern cannot span the newline to learn it -- exactly the CR 706.3b die-row
# case one rule over. Measured 2026-08-07: 96 leveler content lines and 78
# class content lines, NONE of them joined to the band that governs them.
_LEVEL_BAND_RE = re.compile(r"^LEVEL\s+\d+\s*(?:-\s*\d+|\+)\s*$", re.I)
_CLASS_LEVEL_RE = re.compile(r"^(?:\{[^}]*\})+\s*:\s*Level\s+\d+\s*$", re.I)


def _is_band_marker(line: str) -> bool:
    """Does this line OPEN a new striation, closing the previous one?

    ONLY the two band markers. It is tempting to also stop at a modal header or
    a roll instruction so an inner block is not swallowed -- and that was the
    first version, and it was wrong: Barbarian Class's level-2 ability is
    *"Whenever you ROLL one or more DICE, target creature you control gets
    +2/+0…"*, which matches `_ROLL_INSTRUCTION_RE` and silently ended the band
    one line early. The inner-block problem is real but belongs to the LOOP,
    which solves it by not consuming a striation (see `expand_modal_bullets`),
    not to the boundary test, which CR 711.2/716.2 define in terms of the
    striation markers alone.
    """
    s = line.strip()
    return bool(_LEVEL_BAND_RE.match(s) or _CLASS_LEVEL_RE.match(s))


def _is_die_row(line: str) -> bool:
    """A CR 706.3b results-table row, however it is printed.

    Celebr-8000 prints its table with BULLETS (`• 2 — menace`) rather than the
    `N |` bar. CR 706.3b says "the associated results table" without
    prescribing typography, so a roll header claims either form -- otherwise
    the five rows of a bulleted table are the only part of that one ability
    that cannot reach its own trigger."""
    return bool(_DIE_ROW_RE.match(line)) or is_mode_line(line)


def is_mode_line(line: str) -> bool:
    """Is this line one of CR 700.2's options (a MODE)?

    CR 700.2 describes modes as a BULLETED list, and CR 700.2i names the other
    printed form outright: *"Some modal spells have one or more PAWPRINT
    SYMBOLS ({P}) RATHER THAN BULLET POINTS, as well as an instruction to
    choose up to a specified number of {P} 'worth of modes.'"*

    Season of Loss prints `Choose up to five {P} worth of modes.` then
    `{P} — …`, `{P}{P} — …`, `{P}{P}{P} — …`. Testing only for `•` made all 15
    such lines invisible as modes, so each parsed alone and routed nowhere.

    Shared by BOTH consumers -- `expand_modal_bullets` (the DET preprocessing
    standard) and the extractor's `deliveries_for_lines` -- so the two cannot
    drift apart. Fixing one and not the other is the D8 semicolon lesson.

    CR 700.2h is the third printed form: *"Some modal spells have one or more
    modes with a COST LISTED BEFORE THE EFFECT of that mode."* Spree prints
    `+ {2}{B} — Destroy target creature.` Its header carries the choose
    instruction inside REMINDER text (`Spree (Choose one or more additional
    costs.)`), which §6a strips for the classifier but which
    `expand_modal_bullets` still sees, because that runs on the full oracle
    text. So the DET side can join these and the routing side cannot -- and
    that asymmetry is correct, not a bug: a spree spell's own delivery is
    `spell-or-static` by CR 113.3a, so there is no timing for a mode to inherit.
    """
    s = line.lstrip()
    return (s.startswith("•")
            or bool(re.match(r"^(?:\{P\})+\s*—", s))       # CR 700.2i
            or bool(re.match(r"^\+\s*\{[^}]*\}[^—]*—", s)))  # CR 700.2h


def _cardname_candidates(card: dict) -> list:
    """All the proper-noun strings a card's own oracle text might use to
    self-reference instead of 'this creature'/'this permanent' -- the FULL
    printed name, and (for legendary-subtitle and multi-face names) the
    short pre-comma/pre-'//' form actually used in ability text (Oracle
    convention: 'Willie Lumpkin, Postman' is written on its own card as just
    'Willie Lumpkin'). Sorted longest-first so a longer name's substring
    (e.g. a short form that is itself a substring of another candidate)
    never gets replaced first and corrupts a longer match."""
    names = set()
    for raw in [card.get("name")] + [f.get("name") for f in (card.get("card_faces") or [])]:
        if not raw:
            continue
        for part in raw.split(" // "):
            part = part.strip()
            if not part:
                continue
            # Alchemy rebalanced cards are named "A-Elderleaf Mentor" but their
            # oracle text self-references the BASE name. Measured 2026-08-03:
            # without this, every A- card's self-trigger reads as a trigger on
            # another permanent. (CLAUDE.md prefers paper rows over A- variants,
            # but the A- rows are still in the corpus and still scanned.)
            if re.match(r"^A-\S", part):
                names.add(part[2:].strip())
                part = part[2:].strip()
            names.add(part)
            if "," in part:
                names.add(part.split(",")[0].strip())
            # Legendary subtitle without a comma: "Sharuum the Hegemon" prints
            # "When Sharuum enters"; "Rosie Cotton of South Lane" prints "Rosie
            # Cotton".
            #
            # CR 201.5c is the rule this whole function implements, and it is
            # explicit: "Text printed on some cards refers to that card by a
            # SHORTENED VERSION OF ITS NAME. Instances of a card's shortened
            # name used in this manner are treated as though they used the
            # card's FULL NAME." The comma case was already handled; the
            # subtitle case is the same rule and was simply missing.
            # (Captain-ratified 2026-08-03, batch Q6.)
            #
            # Guarded to >2 chars so a leading article ("The Ring") can never
            # produce a degenerate token.
            #
            # LEGENDARY ONLY (2026-08-07). CR 201.5c licenses a shortened name
            # only where the text "refers to that card BY a shortened version
            # of its name" -- "used IN THIS MANNER" is the rule's own qualifier,
            # and a name is not a name+subtitle construction just because it
            # contains " of ". Ungated, this branch was erasing CR 205 TYPE
            # words from oracle text on 26 non-legendary cards, silently and
            # upstream of every DET pattern:
            #
            #   Destroy the Evidence   "Destroy target land"      -> "~ target land"
            #   Knight of the New …    "create a … Knight token"  -> "… ~ token"
            #   Case of the Uneaten …  "When this Case enters"    -> "When this ~ enters"
            #   Storm of Memories      "Storm (When you cast …"   -> "~ (When you cast …"
            #
            # `Case` is a CR 205.3 enchantment subtype, `Knight`/`Wall`/`Angel`
            # /`Cleric` creature types, `Storm` a CR 702.40 keyword. Every one
            # of the 26 was a corruption; every one of the 118 LEGENDARY hits
            # (Sharuum, Phage, Zo-Zu, Vraska, …) was a correct self-reference,
            # which is what makes the supertype the honest cut. Both batch-Q6
            # worked cases -- "Sharuum the Hegemon", "Rosie Cotton of South
            # Lane" -- are legendary, so the ratified intent is preserved.
            #
            # The comma branch above is NOT gated: a comma subtitle is an
            # explicit two-part name whatever the supertype.
            if _is_legendary(card):
                for sep in (" the ", " of "):
                    if sep in part.lower():
                        idx = part.lower().index(sep)
                        head = part[:idx].strip()
                        if len(head) > 2:
                            names.add(head)
    return sorted((n for n in names if n), key=len, reverse=True)


def _is_legendary(card: dict) -> bool:
    """CR 205.4a supertype, read from the type line of the card OR any face --
    a modal DFC carries its type line per face and the root may be empty."""
    lines = [card.get("type_line") or ""]
    lines += [f.get("type_line") or "" for f in (card.get("card_faces") or [])]
    return any("Legendary" in t for t in lines)


def canonicalize_self_reference(text: str, card: dict) -> str:
    """DET preprocessing standard v1, part 1 (CARDNAME canonicalization,
    ratified 2026-07-31 as a follow-on to the walk-ratification's B3/B4
    blockers): a card's own printed NAME used as a self-reference (Sygg,
    Willie Lumpkin, Ukkima, ...) doesn't match a DET pattern anchored on
    'this creature'/'this permanent' -- replace every whole-word occurrence
    of the card's own name (full printed name, and the short pre-comma/
    pre-'//' form actually used in ability text) with the canonical token
    CARDNAME_TOKEN ('~', the standard MTG-templating self-reference marker)
    BEFORE pattern matching. Does not attempt pronoun resolution ('It' / 'He'
    / 'She' self-reference is a different, harder problem -- out of scope
    for this rule, a separate known gap)."""
    for name in _cardname_candidates(card):
        text = re.sub(r"\b" + re.escape(name) + r"\b", CARDNAME_TOKEN, text)
    return text


def expand_modal_bullets(text: str) -> list:
    """DET preprocessing standard v1, part 2 (modal-mode splitting, ratified
    2026-07-31): a modal spell's 'Choose one/two/... —' header followed by
    '• ' bullet lines is one ability with several independently-scannable
    MODES, not one continuous paragraph -- a paragraph-scoped DET pattern
    (house style: same-clause proximity, not cross-ability) correctly does
    NOT cross from the header into a bullet several lines down, so a pattern
    anchored on the header ability word (e.g. 'landfall') never sees a
    bullet's own effect text (e.g. '+1/+0'). Returns a list of SYNTHETIC
    scan-texts, one per bullet, each formed as
    '<header line>\\n<that bullet's line>' -- callers scan the original text
    PLUS these additions (never a replacement -- non-modal text is
    unaffected and still scanned once via the original).

    EXTENDED 2026-08-06 on Captain's word to CR 706.3b's die-roll tables, which
    are the same shape one rule over:

    > *"An INSTRUCTION TO ROLL one or more dice, any instructions to modify
    > that roll printed in the same paragraph, any additional instructions
    > based on the result of the roll, and THE ASSOCIATED RESULTS TABLE are
    > ALL PART OF ONE ABILITY."*

    So `1—9 | Each player sacrifices a permanent…` is not a separate ability;
    it belongs to `At the beginning of combat on your turn, roll two six-sided
    dice…`, and without the join a pattern can see the row's EFFECT but never
    the trigger that says when it happens. Measured 2026-08-06 by
    `foundry_visibility_audit.py`: 101 rows, none joined.

    STATION STRIATIONS ARE DELIBERATELY NOT JOINED. CR 721.2's marker and the
    abilities it governs share ONE line (`9+ | Flying, first strike`), so the
    context is already inline and there is nothing for a join to add. I
    reported them as needing this and was wrong; the audit's own test has been
    corrected rather than the code bent to match it.
    """
    lines = text.split("\n")
    extra = []
    i = 0
    while i < len(lines):
        # (header test, option test) -- each pair is one CR rule about a unit
        # of card text that is split across lines. Modality and the die table
        # are both confirmed STRUCTURALLY: a header only opens a block if
        # option lines actually follow it.
        header = None
        opt_test = None
        consume = True
        # A BAR ROW OUTRANKS THE MODAL TEST; A BULLET DOES NOT. `N |` is
        # typography only a CR 706.3b results table uses, so it decides the
        # block on its own; a BULLET is shared with CR 700.2, so there the
        # modal header keeps precedence. Without this, `_MODAL_HEADER_RE` wins
        # the if/elif on Song of Inspiration -- "CHOOSE UP TO TWO target
        # permanent cards in your graveyard. Roll a d20 and add …" matches its
        # `up to \w+` arm, which is a TARGETING instruction and not a mode list
        # -- and the table is then tested with `is_mode_line`, which no bar row
        # satisfies, so the whole table goes unjoined.
        _nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if _ROLL_INSTRUCTION_RE.search(lines[i]) and _DIE_ROW_RE.match(_nxt):
            header, opt_test = lines[i], _is_die_row     # CR 706.3b
        elif _MODAL_HEADER_RE.search(lines[i].strip()):      # CR 700.2/.2h/.2i
            header, opt_test = lines[i], is_mode_line
        elif _ROLL_INSTRUCTION_RE.search(lines[i]):          # CR 706.3b
            header, opt_test = lines[i], _is_die_row
        elif (_LEVEL_BAND_RE.match(lines[i].strip())         # CR 711.2
              or _CLASS_LEVEL_RE.match(lines[i].strip())):   # CR 716.2
            # A striation claims every line until the NEXT marker -- the other
            # two forms test each option positively, this one tests the
            # boundary, because CR 711.2/716.2 say the striation owns whatever
            # is printed in it rather than naming a shape those lines take.
            #
            # CONSUME=FALSE. A striation's content can itself be a modal header
            # or a roll instruction, and consuming the block would rob it of
            # its own expansion. These joins are purely additive -- the caller
            # scans the original text too -- so the loop advances one line and
            # every inner header still gets its turn.
            header, opt_test, consume = lines[i], lambda l: not _is_band_marker(l), False
        if header is not None:
            j = i + 1
            bullets = []
            while j < len(lines) and opt_test(lines[j]):
                bullets.append(lines[j])
                j += 1
            for b in bullets:
                # Space join, not newline: the whole point is to let a
                # same-clause (paragraph-internal but newline-blocked)
                # pattern see the header and its mode as one continuous
                # unit -- a literal newline join would defeat this against
                # every pattern using "[^\n]*" proximity (F2's own scoping
                # fix).
                extra.append(header + " " + b)
            i = j if (bullets and consume) else i + 1
        else:
            i += 1
    return extra


def det_scan_texts(card: dict) -> list:
    """DET preprocessing standard v1 (walk-ratification 2026-07-31 follow-on,
    joining the existing polarity/templating-era/all-faces rules as a single
    standing pipeline): returns the list of text variants a DET pattern
    should be checked against for this card -- CARDNAME-canonicalized full
    oracle text, plus one synthetic text per modal bullet (also
    canonicalized). A pattern HITS the card if it matches ANY entry. Order:
    [canonicalized full text, *canonicalized modal-bullet expansions]."""
    canon = canonicalize_self_reference(full_oracle_text(card), card)
    return [canon] + expand_modal_bullets(canon)


def build_review_card_record(card: dict) -> dict:
    """The exact 'cards' entry shape T3-AXIS-FOUNDRY-v3.md's batch-N.json
    schema wants, extended with the fields the review tool's card-inspector
    pane also promises (loyalty, set/rarity of the oracle print) -- the
    schema's '...' is illustrative, not a closed field list."""
    return {
        "oracle_id": card["oracle_id"],
        "name": card.get("name") or "",
        "mana_cost": card.get("mana_cost") or "",
        "type_line": card.get("type_line") or "",
        "oracle_text": full_oracle_text(card),
        "power": card.get("power"),
        "toughness": card.get("toughness"),
        "loyalty": card.get("loyalty"),
        "color_identity": card.get("color_identity") or [],
        "keywords": card.get("keywords") or [],
        "layout": card.get("layout") or "normal",
        "set": card.get("set") or "",
        "rarity": card.get("rarity") or "",
        "faces": _extract_faces(card),
    }


_CONDENSE_EFFECT_RE = re.compile(r"EFFECT:\s*(.+?)(?:\s+FLAGGED\b|\s+Quote-checked\b|$)", re.S)


def condense_definition_for_prompt(definition: str, max_chars: int = 220) -> str:
    """Codebook condensation (CORPUS-PASS-PLAN.md step 5 / MASTER-HANDOFF.md
    sec.7 item 8, actioned 2026-07-31): the SYNTH-embedded codebook
    reference needs slug + a SHORT definition, not the full audit-trail
    prose some definitions have accumulated (member-specific examples,
    FLAGGED notes, DELIVERY/SCOPE/DURATION/EFFECT facet breakdowns from the
    walk-ratification's Q8.4 rewrites). Does NOT mutate codebook.json's own
    definition field -- this only shapes what load_codebook_reference()
    shows SYNTH. Two-step: (1) if the definition uses the structured
    facet-reading format, extract just the EFFECT clause (the part that
    actually describes what the pattern matches; DELIVERY/SCOPE/DURATION and
    any trailing FLAGGED/audit note are for codebook maintainers, not
    SYNTH's coarse fit judgment); (2) hard-cap at max_chars, cutting on the
    nearest sentence boundary when one exists in range, else a flagged
    ellipsis truncation (never mid-word)."""
    text = definition
    m = _CONDENSE_EFFECT_RE.search(text)
    if m:
        text = m.group(1).strip()
    if len(text) > max_chars:
        m2 = re.match(r"(.{1,%d}?[.!?])\s" % max_chars, text)
        if m2:
            text = m2.group(1)
        else:
            text = text[:max_chars].rstrip() + "…"
    return text


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
