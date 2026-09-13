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

# THE `experiments` PATH INSERT STAYS, AND IS STILL LOAD-BEARING. C8.5G removed
# this module's own `import tier_engine`, but the insert is not that import's
# private scaffolding: it is the LEGACY_SIBLING_IMPORT bootstrap family recorded
# in refoundation/PACKAGE-EXECUTION-CONTRACT.yaml, 87 sites strong, and its
# deletion prerequisite (the legacy tree becoming importable) is nowhere near
# satisfied. Inserting at 0 after the src bootstrap keeps `experiments` at the
# same precedence it has always had.
sys.path.insert(0, str(_PATHS.legacy_experiments))

# C8.5G: corpus access now comes from the permanent package, not from the engine.
# This module no longer imports `tier_engine` at all — the upward dependency that
# P0.2 named as the shared foundation's structural defect is gone from HERE. The
# engine keeps its own copies of these helpers for its ten other consumers; they
# are untouched, and the two implementations coexist and are differentially
# compared while that remains true.
from mtj_foundry import corpus as _corpus  # noqa: E402
from mtj_foundry.infra import artifact as _artifact  # noqa: E402
# S10: the card-text observations this module used to DEFINE now have permanent
# owners -- `mtj_foundry.corpus` (full oracle text) and `mtj_foundry.oracle_text`
# (the DET-compatible self-reference contract and neutral printed-text structure
# recognition). The names below that remain are COMPATIBILITY FACADES for callers
# whose migration belongs to a later slice or is frozen (AQ4). Functions delegate
# BY CALL-TIME LOOKUP on the owner module, never by a value captured at import:
# replacing an owner's function at run time must still reach every consumer that
# comes through here (the S7 substitution law, WB4).
from mtj_foundry import oracle_text as _oracle_text  # noqa: E402

FOUNDRY_OUT_DIR = _PATHS.legacy_foundry_out
REVIEW_DIR = _PATHS.legacy_foundry_review

# C8.5C: the boundary also exposes the legacy pipeline-artifact directory, so
# `foundry_codebook` can stop deriving a root of its own to reach it. Like the
# three above, this is the OWNER's value -- it is not derived here.
DATA_ARTIFACTS_DIR = _PATHS.legacy_data_artifacts

# S3: the six tracked CONFIG GROUPS, direct aliases of the S1-accepted owner.
# Migration slice 3 relocated ten tracked inputs into the `config/` groups slice
# 1 named, and these names are what let fifteen legacy readers say
# `fc.CONFIG_SEMANTIC / "x.json"` instead of each restating `"config"/"<group>"`.
# Same shape and same reason as the four names above: the VALUE is the owner's,
# derived nowhere here, so a group re-points in exactly one place.
CONFIG_SELECTORS = _PATHS.config_selectors
CONFIG_SEMANTIC = _PATHS.config_semantic
CONFIG_GENERATED = _PATHS.config_generated
CONFIG_REGISTERS = _PATHS.config_registers
CONFIG_CR = _PATHS.config_cr
CONFIG_THESAURUS = _PATHS.config_thesaurus


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
    try:
        cards = _corpus.load_cards(_PATHS.legacy_oracle_cards)
    except _corpus.CorpusLoadError as error:
        # THE ERROR BOUNDARY. The permanent library raises; this transitional
        # facade turns that back into the legacy halt-loudly behavior, so every
        # legacy caller keeps the stderr line and the exit code it always had
        # while the library itself stays free of process-exit semantics.
        halt(str(error))
    name_index = _corpus.build_name_index(cards)
    return cards, name_index


def gate_passes(card: dict) -> bool:
    """Gate #0 (ratified batch-6 D1, 2026-07-30): a card is a valid target for
    the T3 Axis Foundry pipeline -- the DET pass, batch assembly, SYNTH, and
    reconcile -- iff it is legal or restricted in at least one Scryfall
    'legalities' format.

    S10 COMPATIBILITY FACADE. The permanent owner is
    `mtj_foundry.corpus.is_gate0_eligible`; this name delegates at call time and
    carries no copy of the predicate. The delegation was taken only after the
    legacy body and the owner were re-proven VALUE_EXACT over the full selected
    corpus. `load_corpus_gated` below still reaches the predicate through THIS
    name, so a caller replacing it keeps the effect it always had."""
    return _corpus.is_gate0_eligible(card)


def load_corpus_gated():
    """Gate #0-filtered corpus for foundry pipeline stages. Returns
    (cards, name_index, gated_out_count) -- cards/name_index contain only
    gate-passing rows; name_index is rebuilt from the filtered set so
    resolve_name() can never resolve a gated-out card by name. Raw
    load_corpus() is untouched and still available for reference/debugging."""
    cards, _ = load_corpus()
    gated_cards = {oid: c for oid, c in cards.items() if gate_passes(c)}
    gated_name_index = _corpus.build_name_index(gated_cards)
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
    matches = name_index.get(_corpus.normalize_name(name), [])
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
    """All-faces oracle text, newline-joined.

    S10 COMPATIBILITY FACADE. The permanent owner is
    `mtj_foundry.corpus.full_oracle_text` (all faces in order, one `\\n` join,
    empty faces skipped); this name delegates at call time and carries no copy.
    """
    return _corpus.full_oracle_text(card)


def raw_faces(card: dict) -> list:
    """TEMPORARY COMPATIBILITY FACADE for the permanent corpus capability.

    Legacy modules used to reach the shared face reader as `fc.te.get_raw_faces`
    -- through this module's `tier_engine` binding. C8.5G removed that binding,
    so this is the one place they reach it now. It DELEGATES; it must never grow
    a copy of the implementation, because two face readers is exactly the drift
    this capability exists to prevent.

    It deletes when its callers import `mtj_foundry.corpus` directly, which is
    gated on the installed-package context, not on anything in this file.
    """
    return _corpus.card_faces(card)


# --- S10: card-text observations, now owned by `mtj_foundry.oracle_text` ------
#
# The definitions (and the CR rationale that justified each of them) moved
# verbatim to the permanent owner. What stays here is the legacy NAME for each
# one a live caller still reaches, and why that caller has not moved:
#
#   CARDNAME_TOKEN          AQ4 packet probes (AQ4 paused; S14) and this module's
#                           own `pattern_misses_cardname_token`
#   _MODAL_HEADER_RE        frozen AQ4 benchmark; the shapes substrate's injection
#   _DIE_ROW_RE             the shapes substrate's injection
#   _ROLL_INSTRUCTION_RE    the shapes substrate's injection
#   _LEVEL_BAND_RE, _CLASS_LEVEL_RE, _is_band_marker
#                           the Gate-2 visibility audit, which an accepted C8.5G
#                           guard holds to reaching card text through this facade
#   is_mode_line            frozen AQ4 benchmark; the injection; operator tools
#   _cardname_candidates    the definition-drift re-audit worklist, whose
#                           bootstrap route is pinned by S11 codebook evidence
#   canonicalize_self_reference  the shapes/locality injections; later-slice tools
#
# Retired, with no caller anywhere once the lift made them internal to the owner:
# `_is_die_row` (now `oracle_text.is_die_result_row`) and `_is_legendary`.
#
# The compiled patterns are the owner's OBJECTS, aliased rather than rebuilt, so
# there is one definition of each. The functions are call-time delegates.
CARDNAME_TOKEN = _oracle_text.DET_CARDNAME_TOKEN
_MODAL_HEADER_RE = _oracle_text.MODAL_HEADER_RE
_DIE_ROW_RE = _oracle_text.DIE_ROW_RE
_ROLL_INSTRUCTION_RE = _oracle_text.ROLL_INSTRUCTION_RE
_LEVEL_BAND_RE = _oracle_text.LEVEL_BAND_RE
_CLASS_LEVEL_RE = _oracle_text.CLASS_LEVEL_RE


def _is_band_marker(line: str) -> bool:
    """Does this line open a CR 711.2 / 716.2 striation?

    S10 COMPATIBILITY FACADE for `mtj_foundry.oracle_text.is_striation_marker`.
    """
    return _oracle_text.is_striation_marker(line)


def is_mode_line(line: str) -> bool:
    """Is this line one of CR 700.2's options (a MODE)?

    S10 COMPATIBILITY FACADE for `mtj_foundry.oracle_text.is_mode_line`.
    """
    return _oracle_text.is_mode_line(line)


def _cardname_candidates(card: dict) -> list:
    """The card's own printed-name strings, longest first (CR 201.5c short forms).

    S10 COMPATIBILITY FACADE for `mtj_foundry.oracle_text.det_self_name_candidates`.
    """
    return _oracle_text.det_self_name_candidates(card)


def canonicalize_self_reference(text: str, card: dict) -> str:
    """DET preprocessing standard v1, part 1: the card's own printed name (and
    its CR 201.5c short forms) becomes CARDNAME_TOKEN before DET matching.

    S10 COMPATIBILITY FACADE for
    `mtj_foundry.oracle_text.det_canonicalize_self_reference` -- the
    DET-compatible contract, deliberately NOT neutral N2
    `normalize_self_references`; the two differ on real cards. Delegates at call
    time, so replacing either this name or the owner's function at run time
    reaches `det_scan_texts` and every substrate this module is injected into.
    """
    return _oracle_text.det_canonicalize_self_reference(text, card)


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
        # modal header keeps precedence. Without this, the modal-header test wins
        # the if/elif on Song of Inspiration -- "CHOOSE UP TO TWO target
        # permanent cards in your graveyard. Roll a d20 and add …" matches its
        # `up to \w+` arm, which is a TARGETING instruction and not a mode list
        # -- and the table is then tested with `is_mode_line`, which no bar row
        # satisfies, so the whole table goes unjoined.
        _nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if _oracle_text.is_roll_instruction(lines[i]) and _oracle_text.is_die_row(_nxt):
            header, opt_test = lines[i], _oracle_text.is_die_result_row  # CR 706.3b
        elif _oracle_text.is_modal_header(lines[i].strip()):  # CR 700.2/.2h/.2i
            header, opt_test = lines[i], _oracle_text.is_mode_line
        elif _oracle_text.is_roll_instruction(lines[i]):      # CR 706.3b
            header, opt_test = lines[i], _oracle_text.is_die_result_row
        elif (_oracle_text.is_level_band(lines[i].strip())        # CR 711.2
              or _oracle_text.is_class_level_bar(lines[i].strip())):  # CR 716.2
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
            header, opt_test, consume = lines[i], lambda l: not _oracle_text.is_striation_marker(l), False
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
    """TRANSITIONAL FACADE. The byte format is owned by `infra.artifact`.

    S5 promoted the serialization policy to
    `mtj_foundry.infra.artifact.write_json` as its single permanent owner. This
    name stays because forty-three legacy tools call it and dissolving
    `foundry_common` is slice 10, not this one -- but it now carries NO copy of
    the policy. Two implementations of a byte contract is how one of them drifts.

    Signature, return and behaviour are unchanged.
    """
    _artifact.write_json(path, data)
