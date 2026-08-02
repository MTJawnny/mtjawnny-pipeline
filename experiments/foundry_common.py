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

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import tier_engine as te  # noqa: E402

FOUNDRY_OUT_DIR = REPO_ROOT / "experiments" / "out" / "foundry"
REVIEW_DIR = FOUNDRY_OUT_DIR / "review"


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
_MODAL_HEADER_RE = re.compile(r"choose (?:one|two|three|one or more|up to \w+)\b.*—\s*$", re.I)


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
            names.add(part)
            if "," in part:
                names.add(part.split(",")[0].strip())
    return sorted((n for n in names if n), key=len, reverse=True)


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
    unaffected and still scanned once via the original)."""
    lines = text.split("\n")
    extra = []
    i = 0
    while i < len(lines):
        if _MODAL_HEADER_RE.search(lines[i].strip()):
            header = lines[i]
            j = i + 1
            bullets = []
            while j < len(lines) and lines[j].lstrip().startswith("•"):
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
            i = j
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
