"""Oracle-text normalisation, reminder parsing, and keyword-line recognition.

## What this is

The permanent home of one coherent capability: turning printed card text into
the normalised forms everything else compares against. Reminder spans in and
out, curly/case/whitespace folding, the card's own printed name reduced to a
token, and the recognition of a paragraph that is nothing but keywords.

## What this is NOT

It is not a move of `tier_engine`. That module is the ORACLE — every value below
is differentially compared against it over the whole corpus — but its boundary
is not the target architecture and three of its habits are not inherited:

* **No engine coupling.** Stdlib only. Nothing here imports `tier_engine`,
  `foundry_common`, `mtj_foundry.corpus` or any other module. Face splitting
  belongs to the corpus capability and is deliberately absent: callers pass text.
* **No process behaviour.** Pure functions. No I/O, no printing, no `sys.exit`,
  no `sys.path`, no module-level repository-relative constant.
* **No hidden coupling between siblings.** `strip_reminders` and
  `reminder_bodies` are both defined in terms of `paren_spans`, so they cannot
  disagree about where a reminder starts — the legacy erratum made that an
  explicit requirement and it is structural here rather than a convention.

## The two rules that are law, not convenience

**N2 — printed-name self-reference (Captain-ratified 2026-08-30).** When a
card's own printed name is also one of its keyword-action names, an occurrence
that is sentence-initial and immediately followed by `target` is the keyword
VERB and stays literal. Every ordinary occurrence still becomes `~`. The witness
is the card *Regenerate*: `"Regenerate target creature."` must never become
`"~ target creature."`, which would stop it matching every other card's genuine
regenerate text. This is Captain-ratified authority, not inherited legacy prose.

**This is the PRINTED-NAME mechanism only.** It is not CR 205 noun-phrase
self-reference (`this creature`, `this scheme`), which is a different rule with
a different home. Conflating them is explicitly out of bounds.

## Compatibility behaviours, declared rather than inherited

* **Unbalanced parentheses.** An unmatched leading or trailing paren does not
  raise and does not complete a span. That is the accepted legacy behaviour,
  kept deliberately; it is a compatibility decision, not a claim about MTG.
* **Generic keyword names.** A keyword whose name does not literally prefix its
  templated text (`Landwalk` vs. printed `Swampwalk`) is not recognised and the
  paragraph falls through to ordinary matching. Carried forward unchanged; this
  slice does not widen the semantics or add a curated exception list.

## S10: two more capabilities lifted here, and one that deliberately was NOT

Migration slice 10 lifted, verbatim and under full-population differential, the
card-text observations the Captain-approved ownership decision
(`docs/architecture/S10-CARD-TEXT-OWNERSHIP-DECISION-2026-09-11.md`) places in
this module:

* **The DET-compatible self-reference contract** — `DET_CARDNAME_TOKEN`,
  `det_self_name_candidates` and `det_canonicalize_self_reference`. It is a
  SEPARATE NAMED CONTRACT from N2 above, not a second spelling of it: it adds
  CR 201.5c shortened names (comma and legendary-subtitle forms) and Alchemy
  `A-` base names, and it has no keyword-verb exception. Measured, the two
  differ on real cards, so neither may stand in for the other. **Ownership
  consolidation is not semantic consolidation.** It reads the card record's
  NAME and TYPE-LINE fields to build candidates; it still splits no faces for
  text, which stays the corpus capability's job.
* **Neutral printed-text structure recognition** — modal headers and mode
  lines (CR 700.2/.2h/.2i), roll instructions and results-table rows
  (CR 706.3), and leveler/class striation markers (CR 711.2/716.2).
  RECOGNITION ONLY: whether a mode or a table row inherits a delivery is
  `mtj_foundry.mtg.shapes.delivery`'s decision, and turning these into
  DET-matchable synthetic text is DET preprocessing policy, not neutral
  structure. That synthetic composition (`det_scan_texts`,
  `expand_modal_bullets`) was deliberately NOT moved here.

These are lifted AS ACCEPTED, including every measured gap of the pipelines
built on them (the S16A parser-seam evidence under
`docs/architecture/preflight/s16a/`). Improving them is S16A's work; S10
conserves.
"""

from __future__ import annotations

import re

__all__ = [
    "collapse_whitespace",
    "is_keyword_only",
    "keyword_instances",
    "normalize_clause",
    "normalize_reminder",
    "paren_spans",
    "reminder_bodies",
    "self_name_candidates",
    "normalize_self_references",
    "strip_reminders",
    # S10 — DET-compatible self-reference (separate from N2)
    "DET_CARDNAME_TOKEN",
    "det_self_name_candidates",
    "det_canonicalize_self_reference",
    # S10 — neutral printed-text structure recognition
    "MODAL_HEADER_RE",
    "DIE_ROW_RE",
    "ROLL_INSTRUCTION_RE",
    "LEVEL_BAND_RE",
    "CLASS_LEVEL_RE",
    "is_modal_header",
    "is_mode_line",
    "is_roll_instruction",
    "is_die_row",
    "is_die_result_row",
    "is_level_band",
    "is_class_level_bar",
    "is_striation_marker",
]

# The canonical stand-in for a card's own printed name. INTERNAL: it is an
# implementation constant, not a supported surface — a consumer that imported it
# would be coupled to a detail no contracted function requires it to know.
_SELF_TOKEN = "~"

_WHITESPACE = re.compile(r"\s+")
_CURLY_QUOTES = {"’": "'", "‘": "'", "“": '"', "”": '"'}


# ---------------------------------------------------------------------------
# whitespace / case
# ---------------------------------------------------------------------------


def collapse_whitespace(text: str) -> str:
    """Every run of whitespace to one ASCII space, then strip. No case change.

    A function boundary rather than an exported compiled pattern: a consumer
    that borrows the regex object is coupled to this module's internals, which
    is how `tier_engine.WS_RE` ended up used directly from another file.
    """
    return _WHITESPACE.sub(" ", text).strip()


def _fold_and_lower(text: str) -> str:
    """The shared tail of both normalisers: curly quotes, lowercase, whitespace."""
    for curly, straight in _CURLY_QUOTES.items():
        text = text.replace(curly, straight)
    return collapse_whitespace(text.lower())


# ---------------------------------------------------------------------------
# reminder text
# ---------------------------------------------------------------------------


def paren_spans(text: str) -> list[tuple[int, int]]:
    """Outermost balanced parenthesis spans as `(start, end)`, end-exclusive.

    A depth counter, not a regex. A flat ``\\([^)]*\\)`` cannot express nesting
    and silently corrupts any reminder that contains its own parenthetical — the
    legacy erratum names the single corpus instance, Devoted Mardu, where it
    matched from the outer ``(`` to the FIRST ``)`` and left a dangling paren.

    Nested parens are kept intact inside their outermost span, never split.
    Unbalanced leading or trailing parens are ignored: no span is completed and
    nothing is raised. Spans come back in source order.
    """
    spans: list[tuple[int, int]] = []
    depth = 0
    start = None
    for index, char in enumerate(text):
        if char == "(":
            if depth == 0:
                start = index
            depth += 1
        elif char == ")":
            if depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    spans.append((start, index + 1))
                    start = None
    return spans


def strip_reminders(text: str) -> str:
    """`text` with every span from `paren_spans` removed."""
    spans = paren_spans(text)
    if not spans:
        return text
    parts = []
    last = 0
    for start, end in spans:
        parts.append(text[last:start])
        last = end
    parts.append(text[last:])
    return "".join(parts)


def reminder_bodies(text: str) -> list[str]:
    """The contents of every span from `paren_spans`, outer parens removed.

    The exact complement of `strip_reminders` — what that discards, this
    returns — and both read the same scanner, so they cannot disagree.
    """
    return [text[start + 1:end - 1] for start, end in paren_spans(text)]


def normalize_clause(text: str) -> str:
    """Reminder-stripped, quote-folded, lowercased, whitespace-collapsed.

    The step ORDER is load-bearing: reminders are removed BEFORE folding, so a
    reminder's own punctuation can never reach the normalised clause.
    """
    return _fold_and_lower(strip_reminders(text))


def normalize_reminder(text: str) -> str:
    """The same folding applied to an already-extracted reminder body.

    Deliberately does NOT strip reminders again — this text IS the reminder, and
    a second strip would eat any parenthetical nested inside it.
    """
    return _fold_and_lower(text)


# ---------------------------------------------------------------------------
# the card's own printed name
# ---------------------------------------------------------------------------


def self_name_candidates(name: str) -> set[str]:
    """The printed name, plus each non-empty face name split on ``" // "``."""
    candidates = {name}
    if " // " in name:
        for face_name in name.split(" // "):
            face_name = face_name.strip()
            if face_name:
                candidates.add(face_name)
    return candidates


def normalize_self_references(text: str, candidates: set, keywords: list = None) -> str:
    """Replace the card's own printed name with `~`, except under N2.

    N2 (Captain-ratified 2026-08-30): when a candidate is also one of the card's
    own keyword-action names, an occurrence that is BOTH sentence-initial AND
    immediately followed by ``target`` is the keyword verb and stays literal.
    Everything else — including a self-name used as a subject elsewhere in the
    same text — still becomes the token.

    Candidates are applied longest-first so a short face name cannot consume the
    inside of a longer one. Sentence-initial means position 0 or preceded by a
    ``.`` or newline and optional space, measured against the ORIGINAL text so
    earlier substitutions cannot move the boundary.
    """
    lowered_keywords = {k.lower() for k in (keywords or ())}
    for candidate in sorted(candidates, key=len, reverse=True):
        pattern = r"\b" + re.escape(candidate) + r"\b"
        is_keyword_action_name = candidate.lower() in lowered_keywords

        def _sub(match, _text=text, _is_action=is_keyword_action_name):
            if _is_action:
                start = match.start()
                sentence_initial = start == 0 or bool(
                    re.search(r"[.\n]\s*$", _text[:start]))
                if sentence_initial and re.match(r"target\b", _text[match.end():].lstrip()):
                    return match.group(0)
            return _SELF_TOKEN

        text = re.sub(pattern, _sub, text)
    return text


# ---------------------------------------------------------------------------
# keyword lines
# ---------------------------------------------------------------------------


def keyword_instances(normalized_paragraph: str, keywords: list) -> list[dict]:
    """`[{"keyword": lowered, "param": str | None}, ...]` for a normalised line.

    Comma-separated fragments; trailing period stripped; a fragment matches a
    keyword by equality or by ``keyword + " "``. Keywords are tried
    LONGEST-FIRST so a short name cannot prefix-match inside a longer one's
    fragment. `param` is `None` for a bare keyword.

    Shares its fragment convention with `is_keyword_only`; the two must never
    disagree about what counts as a keyword fragment.
    """
    if not normalized_paragraph or not keywords:
        return []
    lowered_keywords = sorted({k.lower() for k in keywords}, key=len, reverse=True)
    instances = []
    for fragment in normalized_paragraph.split(","):
        fragment = fragment.strip().rstrip(".").strip()
        if not fragment:
            continue
        for keyword in lowered_keywords:
            if fragment == keyword:
                instances.append({"keyword": keyword, "param": None})
                break
            if fragment.startswith(keyword + " "):
                param = fragment[len(keyword):].strip()
                instances.append({"keyword": keyword, "param": param or None})
                break
    return instances


def _where_param_is(normalized_paragraph: str, keywords: list):
    """The closed ``<Keyword> <param>, where <param> is <clause>.`` pattern.

    The where-clause explains the keyword's own variable, so it belongs to the
    keyword line. Deliberately narrow: the parameter token must be literally the
    same in both places, so an unrelated ``where Y is ...`` inside a differently
    templated line (an em-dash ability-word construction, say) does not match.
    Returns the matched keyword's lowered name, or None.
    """
    fragments = [f.strip() for f in normalized_paragraph.split(",") if f.strip()]
    if len(fragments) < 2:
        return None
    first = fragments[0]
    matched = None
    for keyword in sorted({k.lower() for k in keywords}, key=len, reverse=True):
        if first.startswith(keyword + " "):
            matched = keyword
            break
    if matched is None:
        return None
    param = first[len(matched):].strip()
    if not param:
        return None
    param_token = param.split()[0]
    rest = ", ".join(fragments[1:]).strip()
    if re.match(r"^where\s+" + re.escape(param_token) + r"\s+is\b", rest):
        return matched
    return None


def _is_bare_keyword_fragment(fragment: str, keyword: str) -> bool:
    """One fragment against one keyword, with both corrective exclusions.

    WORD-BOUNDARY SAFE. A raw substring prefix made Swiftfoot Boots's own
    ``"equipped creature has hexproof and haste."`` match its keyword ``Equip``
    and silently swallow an entire grant clause. Equality or ``keyword + " "``,
    never a bare `startswith`.

    Two exclusions, both corrective — each can only decline a paragraph that a
    real keyword-only line never claimed:

    * an em dash directly after the keyword name marks an ability word
      introducing its own sentence, which is definitionally not a bare
      ``<keyword> <param>`` line;
    * a continuation of literal ``target`` means the keyword name is being used
      as an ACTION verb with an object. No legitimate keyword parameter is
      spelled ``target`` — real params are costs, types and qualities.
    """
    if fragment == keyword:
        return True
    if not fragment.startswith(keyword + " "):
        return False
    rest = fragment[len(keyword):].lstrip()
    if rest.startswith("—"):
        return False
    return re.match(r"target\b", rest) is None


def is_keyword_only(normalized_paragraph: str, keywords: list) -> bool:
    """True when every comma fragment is a bare keyword line for this card.

    Or when the whole line is the closed ``<Keyword> <param>, where <param>
    is ...`` construction. Keywords come from the card's own list; this never
    guesses a keyword from free text.
    """
    if not normalized_paragraph or not keywords:
        return False
    lowered_keywords = [k.lower() for k in keywords]
    fragments = [f.strip() for f in normalized_paragraph.split(",") if f.strip()]
    if not fragments:
        return False
    if all(any(_is_bare_keyword_fragment(fragment, keyword)
               for keyword in lowered_keywords)
           for fragment in fragments):
        return True
    return _where_param_is(normalized_paragraph, keywords) is not None


# ---------------------------------------------------------------------------
# DET-compatible self-reference — a SEPARATE contract from N2 (S10)
# ---------------------------------------------------------------------------
#
# Lifted verbatim from `experiments/foundry_common.py` (`CARDNAME_TOKEN`,
# `_cardname_candidates`, `_is_legendary`, `canonicalize_self_reference`), which
# now delegates here. It is NOT `normalize_self_references` with extra steps:
# the candidate set is different (CR 201.5c short forms, Alchemy base names) and
# there is no N2 keyword-verb exception. The two are kept apart on purpose.

# The canonical stand-in a DET pattern anchors on. The same glyph as N2's
# internal `_SELF_TOKEN` by MTG templating convention, but PUBLIC and separately
# named, because it is part of the DET contract: ratified DET patterns are
# written against it, and a pattern that accepts it is how a pattern survives
# name self-reference.
DET_CARDNAME_TOKEN = "~"


def det_self_name_candidates(card: dict) -> list:
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
            if _det_is_legendary(card):
                for sep in (" the ", " of "):
                    if sep in part.lower():
                        idx = part.lower().index(sep)
                        head = part[:idx].strip()
                        if len(head) > 2:
                            names.add(head)
    return sorted((n for n in names if n), key=len, reverse=True)


def _det_is_legendary(card: dict) -> bool:
    """CR 205.4a supertype, read from the type line of the card OR any face --
    a modal DFC carries its type line per face and the root may be empty."""
    lines = [card.get("type_line") or ""]
    lines += [f.get("type_line") or "" for f in (card.get("card_faces") or [])]
    return any("Legendary" in t for t in lines)


def det_canonicalize_self_reference(text: str, card: dict) -> str:
    """DET preprocessing standard v1, part 1 (CARDNAME canonicalization,
    ratified 2026-07-31 as a follow-on to the walk-ratification's B3/B4
    blockers): a card's own printed NAME used as a self-reference (Sygg,
    Willie Lumpkin, Ukkima, ...) doesn't match a DET pattern anchored on
    'this creature'/'this permanent' -- replace every whole-word occurrence
    of the card's own name (full printed name, and the short pre-comma/
    pre-'//' form actually used in ability text) with the canonical token
    DET_CARDNAME_TOKEN ('~', the standard MTG-templating self-reference marker)
    BEFORE pattern matching. Does not attempt pronoun resolution ('It' / 'He'
    / 'She' self-reference is a different, harder problem -- out of scope
    for this rule, a separate known gap).

    Both names it uses are looked up on THIS MODULE at call time, as they were
    on the legacy module. That is the S7 call-time substitution law: replacing
    this function (or its candidate rule) at run time must reach every consumer
    that reaches it, and a value captured once would not.
    """
    for name in det_self_name_candidates(card):
        text = re.sub(r"\b" + re.escape(name) + r"\b", DET_CARDNAME_TOKEN, text)
    return text


# ---------------------------------------------------------------------------
# neutral printed-text structure recognition (S10)
# ---------------------------------------------------------------------------
#
# Lifted verbatim from `experiments/foundry_common.py` (`_MODAL_HEADER_RE`,
# `_DIE_ROW_RE`, `_ROLL_INSTRUCTION_RE`, `_LEVEL_BAND_RE`, `_CLASS_LEVEL_RE`,
# `is_mode_line`, `_is_die_row`, `_is_band_marker`). RECOGNITION ONLY. The
# predicates are the preferred surface. The compiled patterns stay public
# because two accepted contracts consume the pattern objects themselves: the
# shapes substrate's injected `CardTextRules` names `modal_header_re`,
# `roll_instruction_re` and `die_row_re`, and frozen AQ4 benchmark code reads the
# legacy names that now alias these.

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
MODAL_HEADER_RE = re.compile(
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
# AFTER `ROLL_INSTRUCTION_RE` has opened a block, and a station card prints no
# roll instruction. Verified live -- 0 station rows joined.
DIE_ROW_RE = re.compile(r"^\s*\d+\s*(?:[-–—]\s*\d+|\+|or less)?\s*\|")
# The instruction that opens such a table. The CR names the shape ("an
# instruction to roll one or more dice") and the corpus prints "roll a d20",
# "roll two six-sided dice", "roll a d20 and add the number of cards in your
# hand". Confirmed structurally: it only opens a block if rows follow.
ROLL_INSTRUCTION_RE = re.compile(
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
LEVEL_BAND_RE = re.compile(r"^LEVEL\s+\d+\s*(?:-\s*\d+|\+)\s*$", re.I)
CLASS_LEVEL_RE = re.compile(r"^(?:\{[^}]*\})+\s*:\s*Level\s+\d+\s*$", re.I)


def is_modal_header(text: str) -> bool:
    """Does `text` carry a CR 700.2 choose-a-NUMBER instruction?

    `MODAL_HEADER_RE.search`, nothing more. The caller decides what to pass
    (stripped or not) and confirms modality structurally by requiring mode lines
    to follow; this recognises the instruction only.
    """
    return bool(MODAL_HEADER_RE.search(text))


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
    standard) and the shapes substrate's `deliveries_for_lines` -- so the two
    cannot drift apart. Fixing one and not the other is the D8 semicolon lesson.

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


def is_roll_instruction(text: str) -> bool:
    """Does `text` carry a CR 706.3b instruction to roll dice?

    `ROLL_INSTRUCTION_RE.search`. It opens a results table only if rows follow,
    and confirming that is the caller's structural job.
    """
    return bool(ROLL_INSTRUCTION_RE.search(text))


def is_die_row(line: str) -> bool:
    """Is this line a CR 706.3b results-table BAR row (`N |`, `N1—N2 |`, `N+ |`)?

    `DIE_ROW_RE.match`, nothing more.
    """
    return bool(DIE_ROW_RE.match(line))


def is_die_result_row(line: str) -> bool:
    """A CR 706.3b results-table row, however it is printed.

    Celebr-8000 prints its table with BULLETS (`• 2 — menace`) rather than the
    `N |` bar. CR 706.3b says "the associated results table" without
    prescribing typography, so a roll header claims either form -- otherwise
    the five rows of a bulleted table are the only part of that one ability
    that cannot reach its own trigger."""
    return is_die_row(line) or is_mode_line(line)


def is_level_band(line: str) -> bool:
    """`LEVEL 2-6` / `LEVEL 7+` (CR 711.2). `LEVEL_BAND_RE.match`; no strip."""
    return bool(LEVEL_BAND_RE.match(line))


def is_class_level_bar(line: str) -> bool:
    """`{1}{R}: Level 2` (CR 716.2). `CLASS_LEVEL_RE.match`; no strip."""
    return bool(CLASS_LEVEL_RE.match(line))


def is_striation_marker(line: str) -> bool:
    """Does this line OPEN a new striation, closing the previous one?

    ONLY the two band markers. It is tempting to also stop at a modal header or
    a roll instruction so an inner block is not swallowed -- and that was the
    first version, and it was wrong: Barbarian Class's level-2 ability is
    *"Whenever you ROLL one or more DICE, target creature you control gets
    +2/+0…"*, which matches `ROLL_INSTRUCTION_RE` and silently ended the band
    one line early. The inner-block problem is real but belongs to the LOOP,
    which solves it by not consuming a striation (see `expand_modal_bullets`),
    not to the boundary test, which CR 711.2/716.2 define in terms of the
    striation markers alone.
    """
    s = line.strip()
    return is_level_band(s) or is_class_level_bar(s)
