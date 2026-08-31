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
