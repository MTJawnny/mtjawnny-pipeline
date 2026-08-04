#!/usr/bin/env python3
"""DET ability-shape extractor -- corpus-wide, zero tokens.

WHY THIS EXISTS
---------------
The 2026-08-03 Clue pass burned model tokens deciding things that are not
interpretive. Grammar §6b is explicit about the split:

    SHAPE -- what the card literally does -- printed text, CR terms of art,
             *no ambiguity*                              -> the axis (child)
    JOB   -- what the card is for -- play outcome, deck role,
             *genuine ambiguity*                         -> the parent

Shape is decidable, so it belongs in a script. This is that script. It reads
every gate-passing card, decomposes it into ability lines, and names each
line's DELIVERY slot structurally. It costs nothing to run and it is the same
parse for all 40 uncovered CR keyword actions, not just Clues.

WHAT IT DOES NOT DO
-------------------
It judges nothing and writes nothing to the codebook. It emits candidates for
audit. Per house style it halts loudly rather than guessing, and an ability
whose delivery has no RATIFIED token is reported as `UNRATIFIED:<descriptor>`
-- never approximated onto the nearest ratified one. That approximation is the
exact error the Clue pass had to undo (Fae Offering's "if you've cast" is not a
cast-trigger; §2 forbids it via the b6 Village Ironsmith ruling).

THE VOCABULARY IS NOT HARDCODED
-------------------------------
The ratified DELIVERY tokens are parsed out of §2 of
`docs/CODEBOOK-NAMING-GRAMMAR.md` at run time. If a token is ratified into that
table, this tool picks it up; if one is retired, this tool stops emitting it.
Same principle as `foundry_cr_checks.py` deriving its check set from the CR:
the check set is DERIVED, never discovered after each failure.

USAGE
  python3 experiments/foundry_shape_extractor.py --gaps
  python3 experiments/foundry_shape_extractor.py --action investigate
  python3 experiments/foundry_shape_extractor.py --action goad --json out.json
"""
import sys
import re
import json
import argparse
import collections
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402

GRAMMAR = REPO_ROOT.parent / "docs" / "CODEBOOK-NAMING-GRAMMAR.md"
CR_CHECKS = REPO_ROOT.parent / "docs" / "cr-checks.json"

REMINDER = re.compile(r"\([^)]*\)")
ABILITY_WORD = re.compile(r"^\s*[A-Z][A-Za-z'’\- ]{2,40}(\s*—|\s*-)\s*")
CHAPTER = re.compile(r"^\s*[IVX]+\s*(,\s*[IVX]+\s*)*(—|-)\s*")

# "this <noun>" is a SELF-reference, and the noun set is not guessable: a card
# says "When this Equipment enters", "Whenever this Siege ...", "this
# Spacecraft", "this Class". Measured 2026-08-03, a hand-written list missed
# equipment(104) siege(36) spacecraft(16) class(13) -- 170 ability lines that
# were then counted as OTHER-permanent triggers, inflating the self-vs-other
# gap census. So the set is DERIVED from the corpus's own type lines at load
# time, the same discipline as parsing §2's vocabulary out of the grammar.
# It must not include time/stack words ("this turn", "this combat", "this
# spell") -- type lines never contain them, which is exactly why deriving
# beats listing.
SELF_NOUN_RX = None          # compiled by build_self_noun_rx()
_ALWAYS_SELF_NOUNS = {"creature", "permanent", "card", "token", "aura", "case"}


def build_self_noun_rx(cards: dict) -> None:
    """Compile the 'this <noun>' self-reference test from corpus type lines."""
    global SELF_NOUN_RX
    nouns = set(_ALWAYS_SELF_NOUNS)
    for card in cards.values():
        parts = [card.get("type_line") or ""]
        parts += [f.get("type_line") or "" for f in (card.get("card_faces") or [])]
        for word in re.findall(r"[A-Za-z'-]+", " ".join(parts)):
            if len(word) > 2:
                nouns.add(word.lower())
    if "equipment" not in nouns:
        fc.halt("Derived self-reference noun set has no 'equipment' — the "
                "corpus type lines did not load. Refusing to run with a "
                "vocabulary that would silently misfile self-triggers.")
    SELF_NOUN_RX = re.compile(r"\bthis (" + "|".join(sorted(map(re.escape, nouns))) + r")\b")


# ---------------------------------------------------------------------------
# ratified vocabulary, parsed from the grammar rather than remembered
# ---------------------------------------------------------------------------
def ratified_delivery_tokens() -> dict:
    """Parse §2's table. Returns {token: CR anchor}. Halts if §2 is unreadable --
    a silently-empty vocabulary would make every shape look unratified."""
    if not GRAMMAR.exists():
        fc.halt(f"{GRAMMAR} not found — the ratified DELIVERY vocabulary lives there")
    text = GRAMMAR.read_text(encoding="utf-8")
    # Stop at the first ### subsection, not at "## 3." -- §2a's ratified
    # subject-prefix tables live between them, and their cells ("prefix",
    # "axis", "other-", "any-") are NOT delivery tokens. Reading to "## 3."
    # ingested all four, silently widening the vocabulary from 19 to 23.
    m = re.search(r"^## 2\. DELIVERY slot.*?$(.*?)^(?:###\s|## 3\.)", text, re.S | re.M)
    if not m:
        fc.halt("CODEBOOK-NAMING-GRAMMAR.md: could not locate §2's DELIVERY table. "
                "The section heading may have been renamed — this tool must not "
                "fall back to a remembered vocabulary.")
    tokens = {}
    for row in m.group(1).splitlines():
        if not row.strip().startswith("|"):
            continue
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0].startswith("---") or cells[0] == "Slot value":
            continue
        tok = cells[0].strip("`*_ ")
        if tok.startswith("(") or not tok:
            continue          # the "(none)" spell-ability row
        if re.fullmatch(r"[a-z0-9\-]+", tok):
            tokens[tok] = cells[-1]
    if len(tokens) < 10:
        fc.halt(f"parsed only {len(tokens)} DELIVERY tokens from §2 — expected ~19. "
                f"Refusing to run with a truncated vocabulary.")
    return tokens


def cr_action_terms() -> dict:
    if not CR_CHECKS.exists():
        fc.halt(f"{CR_CHECKS} not found — run experiments/foundry_cr_checks.py first")
    data = json.loads(CR_CHECKS.read_text(encoding="utf-8"))
    out = {}
    for t in data["terms"]:
        forms = set(t.get("printed_forms") or []) | set(t.get("era_variants") or [])
        forms.add(t["term"])
        out[t["term"]] = {"cr": t["cr"], "kind": t.get("kind"),
                          "forms": sorted(f for f in forms if f)}
    return out


# ---------------------------------------------------------------------------
# decomposition
# ---------------------------------------------------------------------------
def ability_lines(card: dict) -> list:
    """All-faces oracle text, reminder parentheticals removed (§6a: a card's
    claim is its printed text with reminder text EXCLUDED), split into the
    one-ability-per-line form Scryfall already uses."""
    txt = REMINDER.sub("", fc.full_oracle_text(card))
    return [l.strip() for l in txt.split("\n") if l.strip()]


def quoted_spans(line: str) -> list:
    """Character ranges inside double quotes -- granted or token ability text.
    §2's created-ability rule: a card does not deliver an ability it CREATES."""
    return [(m.start(), m.end()) for m in re.finditer(r"[\"“][^\"”]*[\"”]", line)]


def in_created_ability(line: str, pos: int) -> bool:
    return any(a <= pos < b for a, b in quoted_spans(line))


# The event verbs a trigger CONDITION can carry (CR 113.3c: the condition names
# the event). Used only to decide WHERE the condition ends when commas appear
# inside an object phrase -- never to classify.
#
# THE OLD COMMENT HERE STATED THE SAFETY PROPERTY BACKWARDS. It claimed "a verb
# missing here only makes the clause end earlier, which is the conservative
# direction." That is false, and it hid a defect for as long as it stood:
# `trigger_clause` returns the FIRST comma-prefix that carries a listed verb, so
# when the real event verb is ABSENT the loop walks PAST the condition and
# returns a prefix whose verb came from the EFFECT half. A missing verb makes
# the clause end LATER, not earlier.
#
# Measured 2026-08-04: the curated list held 24 verbs, and 488 of 13,028
# when/whenever lines had no listed verb before their first comma. Worked cases,
# each a real misfile:
#   Illuna, Apex of Wishes  "Whenever this creature MUTATES, ..."   CR 702.140
#   Ulrich of the Krallenhorde "Whenever this creature TRANSFORMS"  CR 701.27
#   Fell Stinger            "When this creature EXPLOITS a creature" CR 702.110
# All three were filed as `discard-trigger` because "discard" appears in their
# effect half and was a listed verb. Ninth instance of the CR 113.3c bug class.
#
# The vocabulary is now DERIVED from the CR's own keyword-action list rather
# than curated -- the same principle that parses the DELIVERY tokens out of
# grammar §2 at run time. A curated list is only ever as good as the last
# failure someone happened to notice.
#
# Only `kind == "keyword-action"` is derived. CR 702 KEYWORDS are deliberately
# NOT bulk-derived: they are ability NAMES, not event verbs, and folding in
# words like `flying` or `absorb` would match inside a SUBJECT phrase and cut
# the clause too early -- "Whenever Flying Men, Goblin King, or a Bird enters"
# would stop at "whenever flying men" and lose the event entirely. The handful
# of CR 702 keywords that genuinely appear as trigger EVENTS are listed
# explicitly below, each with its anchor.
TRIGGER_VERB = None

_SUPPLEMENT_VERBS = {
    # CR 702 keywords that are printed as trigger events ("whenever ~ mutates")
    "mutate": "702.140", "exploit": "702.110", "crew": "702.122",
    "saddle": "702.171",
    # verbs the CR defines outside the keyword-action list
    "tap": "701.26", "untap": "701.26",          # 701.26 Tap and Untap
    "lose": "104.3",                              # lose the game / lose life 118
    "control": "109.4",                           # "when you lose control of ~"
    "phase": "702.26a",                           # phase in / phase out
    "tempt": "701.54d",                           # "Whenever the Ring tempts you"
    "roll": "701.52",                             # roll to visit / dice rolls
    # `cycle` is NOT in the CR keyword-action list -- CR 702.29 files it as a
    # KEYWORD -- so deriving from that list alone silently dropped it. Measured:
    # that flipped Radiant Smite off `cycled-trigger` and Crystalline Resonance
    # off `any-cycled-trigger`, because the clause ran on into the effect and
    # picked up "another target permanent" / "the starting player".
    "cycle": "702.29c",
    # structural verbs with no single CR keyword-action home
    "enter": "603.6a", "die": "700.4", "leave": "700.4", "attack": "508.1",
    "block": "509.1", "cast": "601.2", "deal": "120.3", "become": "603.2e",
    "is": "113.3c", "are": "113.3c", "put": "701.9a", "turned": "701.34",
    "declared": "508.1", "drawn": "121.1", "draw": "121.1", "gain": "119.3",
    # PAST PARTICIPLES are not reachable by the `(es|s)?` inflection below and
    # must be listed outright -- "becomes tapped" (CR 603.2e) is a trigger event.
    "tapped": "603.2e", "untapped": "603.2e",
}


def build_trigger_verbs(actions: dict) -> None:
    """Compile the trigger-CONDITION event-verb test from the CR term list."""
    global TRIGGER_VERB
    stems = set(_SUPPLEMENT_VERBS)
    for term, meta in actions.items():
        if meta.get("kind") != "keyword-action":
            continue
        # multi-word CR terms ("tap and untap", "venture into the dungeon",
        # "collect evidence") carry their verb in the first word.
        stems.add(term.split()[0])
    if not {"discard", "sacrifice", "mutate", "transform",
            "cycle", "tapped", "enter"} <= stems:
        fc.halt("Trigger-verb vocabulary lost a known CR keyword action — "
                "refusing to run with a verb set that would silently extend "
                "trigger clauses into the effect half (CR 113.3c).")
    # `s` and `es` cover the printed inflections; the bare stem covers plural
    # subjects ("whenever one or more creatures you control enter").
    alts = sorted((re.escape(s) for s in stems), key=len, reverse=True)
    TRIGGER_VERB = re.compile(r"\b(?:" + "|".join(alts) + r")(?:es|s)?\b")


# Built at IMPORT time, not from main(). `foundry_cr702_classes` does
# `import foundry_shape_extractor as fse`, and when this file runs as a script
# it is `__main__` -- so that import creates a SECOND module object with its own
# globals. A main()-time build left that copy's TRIGGER_VERB as None and the
# CR 702 keyword pass crashed on it. Keeping this a module-level constant is
# what the original hand-written regex was doing implicitly.
build_trigger_verbs(cr_action_terms())


def trigger_clause(low: str) -> str:
    """The condition half of a triggered ability -- everything up to the comma
    that ends it. Whose permanent the trigger watches is decided HERE; reading
    the effect half too is how 'Parley — Whenever this creature attacks, each
    player reveals…' gets misread as an other-creature trigger, because `each`
    appears in the effect.
    A comma does NOT always end it. "Whenever a Mutant, Ninja, or Turtle you
    control enters, investigate" has commas inside the OBJECT phrase, and
    stopping at the first one yields "whenever a mutant" -- no event, so the
    line went unclassified. CR 113.3c says the condition is the half that
    carries the trigger EVENT, so extend across commas until an event verb is
    present, then stop at that segment's end."""
    cuts, depth = [], 0
    for i, ch in enumerate(low):
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        elif ch == "," and depth == 0:
            cuts.append(i)
    if not cuts:
        return low
    for i in cuts:
        if TRIGGER_VERB.search(low[:i]):
            return low[:i]
    return low[:cuts[0]]



# ---------------------------------------------------------------------------
# CR 702 keyword lines -- §2b (Captain-ratified 2026-08-03)
# ---------------------------------------------------------------------------
# A keyword printed bare ("Battle cry", "Flying", "Cycling {2}") IS an ability,
# and §2b says its DELIVERY is derived from the keyword's own 702.Na text --
# never ruled per keyword. Nothing was applying that to the corpus: measured
# 2026-08-03, 12,419 ability lines (20% of the corpus) were bare keyword lines
# falling through to `spell-or-static`.
#
# Hero of Bladehold is the case Captain raised. It has TWO attack triggers:
#     "Battle cry"                                     -> attack-trigger
#     "Whenever this creature attacks, create two ..." -> attack-trigger
# Only the second was seen. The first is a keyword whose CR text (702.35a) is
# "Whenever this creature attacks, each other attacking creature gets +1/+0."
#
# NOT applied to a sentence that merely MENTIONS a keyword: Adriana's "Other
# creatures you control have melee." GRANTS the ability, and §2's
# created-ability rule gives the delivery to the creator, not the created one.
# Only a line that IS one or more keywords (with costs/params stripped) matches.
KEYWORD_HOME = None


def build_keyword_homes(ratified: dict) -> None:
    """keyword name -> §2 DELIVERY token, derived from the CR (§2b)."""
    global KEYWORD_HOME
    import foundry_cr702_classes as k7
    # k7 does `import foundry_shape_extractor`, which under `python3
    # foundry_shape_extractor.py` is a SECOND module instance whose globals are
    # unset -- so its parse_delivery would crash on SELF_NOUN_RX=None. Sync the
    # derived state across instead of letting the copy run blind.
    import foundry_shape_extractor as _twin
    if _twin is not sys.modules[__name__]:
        _twin.SELF_NOUN_RX = SELF_NOUN_RX
        _twin.KEYWORD_HOME = None
    kws = k7.load_702(k7.CR_PATH)
    homes = {}
    for num, kw in kws.items():
        if not kw["name"] or num == k7.PREAMBLE_RULE:
            continue
        tok, _desc, _txt = k7.find_home(kw, ratified)
        if tok is None:
            # fall back to the CR-stated ability CLASS, exactly as --homes does
            classes, _ev = k7.classify(kw)
            eff = [k7.SUBSUMES.get(c, (None,))[0] or c for c in classes]
            if eff == ["static"] and "static" in ratified:
                tok = "static"
        if tok:
            homes[kw["name"].lower()] = tok
    if "battle cry" not in homes:
        fc.halt("Keyword home map has no 'battle cry' — the CR 702 parse "
                "failed. Refusing to run with a partial keyword vocabulary.")
    KEYWORD_HOME = homes


COST_OR_PARAM = re.compile(r"\{[^}]*\}|\bN\b|\d+")


def keyword_line_tokens(line: str) -> list:
    """Tokens for a line that IS one or more printed keywords, else []."""
    if KEYWORD_HOME is None:
        return []
    core = COST_OR_PARAM.sub("", line).strip().rstrip(".").lower()
    core = re.sub(r"\s+", " ", core)
    if not core:
        return []
    parts = [p.strip() for p in core.split(",") if p.strip()]
    if not parts or not all(p in KEYWORD_HOME for p in parts):
        return []
    out, seen = [], set()
    for p in parts:
        t = KEYWORD_HOME[p]
        if t not in seen:
            seen.add(t)
            out.append((t, f"keyword:{p}"))
    return out


def parse_deliveries(line: str, ratified: dict, card: dict = None) -> list:
    """One ability line can carry SEVERAL deliveries -- "Whenever ~ enters or
    attacks", "When ~ enters and at the beginning of your upkeep". Grammar §1's
    multi-axis rule means each earns its membership, so returning only the
    first would silently under-tag the compound-trigger population.

    Splits the trigger clause on `or`/`and` and re-classifies each alternative
    against the same subject. Returns a de-duplicated list of (token, descriptor).
    """
    raw = line.strip()
    kw = keyword_line_tokens(raw)
    if kw:
        return kw
    body = ABILITY_WORD.sub("", raw)
    if card is not None:
        body = fc.canonicalize_self_reference(body, card)
    low = body.lower()

    if not re.match(r"^(when|whenever|at )", low):
        return [parse_delivery(line, ratified, card)]

    clause = trigger_clause(low)
    rest = low[len(clause):]
    # Split on or/and KEEPING the connective, so a bad split can be undone.
    _toks = re.split(r"\s+(or|and)\s+", clause)
    parts, seps = _toks[0::2], _toks[1::2]
    # An `or`/`and` inside the SUBJECT phrase leaves part 0 a bare subject with
    # no event verb -- "Whenever Giott or another Dwarf you control enters"
    # split to "whenever ~", whose clause then ran on into the EFFECT and was
    # filed as a discard-trigger off "you may discard a card". Re-join leading
    # segments until part 0 actually carries an event (CR 113.3c).
    while len(parts) > 1 and not TRIGGER_VERB.search(parts[0]):
        parts[0] = f"{parts[0]} {seps.pop(0)} {parts[1]}"
        del parts[1]
    # Only a part that is itself a trigger PREDICATE is a second delivery.
    # "whenever you cast an instant or sorcery spell" splits on an `or` inside
    # the OBJECT phrase -- "sorcery spell" is not an event, and treating it as
    # one loses a real cast-trigger. Same for "a spell or ability".
    # `at` opens a timing clause ("at the beginning of your upkeep"), but
    # "at least" is a QUANTIFIER, not a trigger. Kytheon's "if Kytheon and at
    # least two other creatures attacked this combat" split into a bogus second
    # delivery until this was excluded.
    PREDICATE = re.compile(
        r"^(?:at (?!least\b)|when(?:ever)?\b|~\b|this \w+|"
        r"(?:enters?|attacks?|dies|die|leaves?|leave|becomes?|is|are|deals?|"
        r"blocks?|deals)\b)")
    if len(parts) > 1:
        parts = [parts[0]] + [p for p in parts[1:] if PREDICATE.match(p.strip())]
    if len(parts) < 2:
        return [parse_delivery(line, ratified, card)]

    # part 0 keeps its subject ("whenever ~ enters"); later parts are bare verb
    # phrases ("attacks") or full sub-clauses ("at the beginning of your upkeep")
    subject = re.match(r"^(when(?:ever)?|at)\s+(.*?)\s*$", parts[0])
    head = subject.group(1) if subject else "whenever"
    subj = ""
    if subject:
        # `~` takes no trailing \b -- it is not a word character.
        mm = re.match(r"^(?:(~)|(this \w+|a \w+|another[\w ]*|one or more[\w ]*|you)\b)",
                      subject.group(2))
        subj = mm.group(0) if mm else ""

    out, seen = [], set()
    for i, p in enumerate(parts):
        p = p.strip()
        if i == 0:
            cand = p + rest
        elif re.match(r"^(at|when|whenever)\b", p):
            cand = p + rest
        else:
            cand = f"{head} {subj} {p}".strip() + rest
        tok, desc = parse_delivery(cand, ratified, None)
        if (tok, desc) not in seen:
            seen.add((tok, desc))
            out.append((tok, desc))
    return out or [parse_delivery(line, ratified, card)]


def _mark_top(tok, desc, ratified):
    """mark() for the branches that run BEFORE the trigger block defines it."""
    return (tok, desc) if tok in ratified else (None, desc)


def parse_delivery(line: str, ratified: dict, card: dict = None) -> tuple:
    """(token, descriptor) -- token is a ratified §2 value, or None when the
    shape is real but unnamed. descriptor always describes what was actually
    printed, so gaps are reportable without inventing vocabulary."""
    raw = line.strip()
    if CHAPTER.match(raw):
        # NOT "saga-or-class": measured 2026-08-03, all 576 lines are Sagas
        # and ZERO are Classes. A Class level bar prints "{1}{G}: Level 2 —",
        # which has a cost and a colon, so it is claimed by the `activated`
        # branch above -- correctly, because CR 716.2a says a class level bar
        # "represents both an ACTIVATED ability and a STATIC ability". Only
        # Saga chapters are triggered (CR 714.2).
        return _mark_top("chapter-trigger", "saga-chapter", ratified)
    body = ABILITY_WORD.sub("", raw)
    # Collapse the card's own name (and short forms) to `~` so a self-reference
    # is detectable without case or spelling games. This is the same helper the
    # DET pass uses, so the two agree by construction.
    if card is not None:
        body = fc.canonicalize_self_reference(body, card)
    low = body.lower()

    # activated -- a cost left of a colon (CR 113.3b), colon not inside quotes
    if ":" in body:
        head = body.split(":")[0]
        if not in_created_ability(body, body.index(":")) and \
           re.search(r"[{}]|\bsacrifice\b|\bdiscard\b|\bpay\b|\btap\b|\bexile\b|\bremove\b",
                     head, re.I):
            if re.search(r"^[+\-−]?\d|loyalty", head.strip()[:3]) and "loyalty" in ratified:
                return "loyalty", "loyalty-ability"
            return ("activated", "cost-colon") if "activated" in ratified else (None, "cost-colon")

    # CR 113.3c: "Triggered abilities have a TRIGGER CONDITION and an EFFECT.
    # They are written as '[Trigger condition], [effect]'." The event that names
    # the delivery is in the CONDITION, by definition -- so every event test in
    # this block reads `clause`, never the whole line. Seven separate defects
    # were fixed one at a time before this was done systematically: self/other,
    # phase triggers, graveyard, Snowfall's upkeep, is-attacked, sacrifice,
    # discard. All of them were the same root cause.
    if re.match(r"^(when|whenever|at )", low):
        # the SUBJECT matters: §2's rows read "when ~ enters", "whenever ~
        # attacks" -- the tilde is the SOURCE. Other-permanent triggers are a
        # different printed shape (§6b) and must not be folded in.
        clause = trigger_clause(low)
        # NB: `~` is not a word character, so \b~\b can never match. Match it
        # positionally instead -- this silently blinded the self-reference test.
        selfish = bool(SELF_NOUN_RX.search(clause)) or \
            bool(re.search(r"(?:^|\s)~(?:\s|$|'s)", clause))
        other = bool(re.search(r"\banother\b|\bother\b|\byou control\b|\ba creature\b|"
                               r"\bone or more\b|\beach\b|\bplayers?\b", clause))
        # "Whenever ~ enters or attacks" -- the source naming itself as the
        # trigger subject wins over a stray `other` token later in the clause.
        if re.search(r"^when(ever)?\s+~(?:\s|'s)", clause) or \
           re.search(r"^when(ever)?\s+this\b", clause):
            other = False

        def mark(tok, desc):
            if tok not in ratified:
                return None, desc
            return tok, desc

        # §2a (Captain-ratified 2026-08-03): the trigger SUBJECT is a DELIVERY
        # prefix on any §2 trigger token. Unmarked = the source; `other-` =
        # printed "another" (source excluded); `any-` = printed bare "a"
        # (source INCLUDED, CR 603.6a "including the newcomers"). `any-` is
        # deliberately the marked form even though it is the majority shape --
        # only the source earns the unmarked slot.
        def msub(base, desc):
            """Compose the ratified subject prefix onto a base §2 token."""
            if base not in ratified:
                return None, desc
            if selfish and not other:
                return base, desc
            pre = "other-" if re.search(r"\banother\b|\bother\b", clause) else "any-"
            return pre + base, pre + desc

        # NB: the generic phase branches further down also test `clause`.
        # Snowfall proved why: "Whenever an Island IS TAPPED FOR MANA, ... Spend
        # this mana only to pay CUMULATIVE UPKEEP costs" -- the tail mentions
        # upkeep, so a whole-line test stole it from tapped-for-mana-trigger.
        # Fourth instance of this bug class in this file.
        # PHASE triggers are decided on the CLAUSE, and decided FIRST. The
        # event tests below scan the whole line, so "At the beginning of combat
        # on your turn, create a Goblin ... that ATTACKS this combat" reads as
        # an attack trigger unless the phase is claimed first. Measured
        # 2026-08-03: 45 cards were misfiled into the self-vs-other families
        # this way (Legion Warboss, Mathas, Curious Obsession...). Same
        # whole-line-vs-clause bug the census already fixed for self/other --
        # it was still live for family selection.
        if re.match(r"^at the beginning\b", clause):
            # §2d / CR 603.7a: "at the beginning of the NEXT <phase>" is a
            # DELAYED triggered ability. §2's created-ability rule gives the
            # delivery to whatever CREATED it -- here the spell's own
            # resolution -- so this is NOT a phase delivery. Siren's Call,
            # Vivien's Stampede. (The other ~332 "next end step" cards carry
            # the delayed trigger in the EFFECT half of a real trigger and
            # already resolve to their creator's delivery.)
            if re.match(r"^at the beginning of the next\b", clause):
                return None, "spell-or-static"
            # PLURALS are printed: "each of your postcombat main phaseS",
            # "each of that player's upkeepS". A \b-anchored singular silently
            # dropped them into phase-trigger-unnamed.
            if re.search(r"\bupkeeps?\b", clause):
                return mark("upkeep-trigger", "upkeep")
            if re.search(r"\bend steps?\b", clause):
                return mark("end-step-trigger", "end-step")
            if re.search(r"\bdraw steps?\b", clause):
                return None, "draw-step"
            # CR 505.1 names THREE printed main phases and 505.1a/b keep them
            # apart. Checked before the bare `combat` test: "precombat" and
            # "postcombat" contain no \b-delimited "combat", but the ordering
            # is made explicit rather than left to regex luck.
            #   505.1  "the first main phase (also known as the precombat
            #           main phase)" -- the CR makes these one phase.
            #   505.1a "All OTHER main phases are postcombat main phases" --
            #           so postcombat is a CATEGORY, not the second phase.
            #   505.1b "first/second main phase ... COUNT the number of main
            #           phases that have occurred only in the current turn."
            # With an extra combat phase a third main phase is postcombat but
            # is NOT the second -- so "second" and "postcombat" differ in WHEN
            # the trigger fires, which is the ratified split test (§2, D3f).
            if re.search(r"\b(?:first|precombat) main phases?\b", clause):
                return mark("precombat-main-phase-trigger", "precombat-main-phase")
            if re.search(r"\bpostcombat main phases?\b", clause):
                return mark("postcombat-main-phase-trigger", "postcombat-main-phase")
            if re.search(r"\bsecond main phases?\b", clause):
                return mark("second-main-phase-trigger", "second-main-phase")
            if re.search(r"\bmain phases?\b", clause):
                return None, "main-phase-unqualified"
            if re.search(r"\bcombat\b", clause):
                return mark("begin-combat-trigger", "begin-combat")
            # A clause that opens "at the beginning of ..." IS a phase trigger,
            # even when the phase has no token yet. Falling through let the
            # event branches read the EFFECT half -- "at the beginning of your
            # first main phase, you may DISCARD a card" was filed as a discard
            # trigger. Claim it here and report the phase honestly instead.
            return None, "phase-trigger-unnamed"

        if re.search(r"\bland (you control )?enters\b", clause) or low.startswith("landfall"):
            return mark("landfall", "landfall")
        if re.search(r"\benters\b", clause):
            return msub("etb", "enters")
        if re.search(r"\bdies\b|\bdie\b", clause):
            if re.search(r"\bfrom (your |a )?(library|hand|anywhere)\b", clause):
                return None, "to-graveyard-from-nonbattlefield"
            return msub("death-trigger", "dies")
        # CR 700.4, verbatim: "The term DIES means 'is put into a graveyard
        # from the battlefield.'" So this phrasing IS a death trigger, not a
        # separate shape -- §2 calls the dies/leaves-battlefield boundary "hard
        # both directions" and D-1 made `death-trigger` the family word on this
        # exact anchor. Measured 2026-08-03: without this, the seven CR 702
        # keywords templated this way (Persist, Undying, Afterlife, Haunt,
        # Soulshift, Recover, Gravestorm -- the canonical death triggers in the
        # game) all missed their home.
        # Tested on the CLAUSE, never the whole line. Gravestorm is the proof:
        # "WHEN YOU CAST THIS SPELL, copy it for each permanent that was put
        # into a graveyard from the battlefield this turn" is a cast trigger
        # whose EFFECT mentions the graveyard. Scanning `low` routed it to
        # death-trigger. Third occurrence of this same bug class in this file
        # (self/other, then phase triggers, now this) -- when adding a branch
        # here, match the trigger condition, not the sentence.
        if re.search(r"\bput into (a |their |your |its owner's )?graveyards?\b", clause) \
                and re.search(r"\bfrom the battlefield\b", clause):
            return msub("death-trigger", "dies")
        if re.search(r"\bput into (a |their |your )?graveyards?\b", clause):
            # CR 700.4 defines `dies` NARROWLY -- "from the battlefield" -- and
            # that case is claimed above. Everything here is a DIFFERENT event,
            # so the printed ZONE is the claim (§6a) and is reported rather
            # than collapsed. "From anywhere" is strictly WIDER than dies;
            # "from your library" is a mill shape and narrower still. Folding
            # them together would repeat the dies/leaves-battlefield error that
            # §2 calls "a hard boundary both directions".
            if re.search(r"\bfrom anywhere\b", clause):
                return None, "to-graveyard-from-anywhere"
            if re.search(r"\bfrom (a |your |their )?library\b", clause):
                return None, "to-graveyard-from-library"
            if re.search(r"\bfrom (a |your |their )?hand\b", clause):
                return None, "to-graveyard-from-hand"
            if re.search(r"\bfrom (a |your |their )?exile\b|\bfrom the stack\b", clause):
                return None, "to-graveyard-from-other-zone"
            # No zone printed. CR 110.1 makes a PERMANENT necessarily on the
            # battlefield, so "a permanent you control is put into a graveyard"
            # is dies by CR 700.4 even unstated -- but a "card" is not, and the
            # two cannot be told apart mechanically here. Reported for ruling
            # rather than routed. House style: halt loudly, never best-guess.
            return None, "to-graveyard-zone-unstated"
        if re.search(r"\bleaves? the battlefield\b|\bleave the battlefield\b", clause):
            return msub("leaves-battlefield-trigger", "ltb")
        # Tested on the CLAUSE. Fifth instance of the whole-line-vs-clause bug:
        # Willie Lumpkin ("Whenever ~ deals combat damage to an opponent, ...
        # that player CAN'T ATTACK YOU") and Unstable Glyphbridge ("Whenever an
        # opponent casts a spell ..., they CAN'T ATTACK YOU") were both stolen
        # into is-attacked by their effect text.
        if re.search(r"\battacks?\b", clause):
            if re.search(r"\battacks? you\b|\battacks? a planeswalker\b", clause):
                return mark("is-attacked-trigger", "is-attacked")
            if re.search(r"^when(ever)? you attack\b", clause):
                return mark("player-attack-trigger", "player-attacks")
            return msub("attack-trigger", "attacks")
        if re.search(r"\bcasts?\b", clause):
            return mark("cast-trigger", "casts")
        # "an opponent" was unmatched by `(a|target)?` -- 17 cards print "deals
        # combat damage to AN OPPONENT" (Kosei, Strixhaven Stadium, Etrata...).
        # It IS a combat claim, so it takes combat-damage-to-player; only a
        # non-combat "deals damage to an opponent" takes any-damage-to-player
        # per DAMAGE-DELIVERY-RULING-2026-08-02.
        if re.search(r"combat damage to (a |an |target )?\s*(player|opponent)", clause):
            return msub("combat-damage-to-player", "combat-damage-player")
        if re.search(r"combat damage to (a|target)?\s*creature", clause):
            return mark("combat-damage-to-creature", "combat-damage-creature")
        # RECIPIENT-side damage: "«X» is dealt damage". This is the mirror of the
        # source-side `*-damage-to-*` tokens above, exactly as
        # `is-attacked-trigger` mirrors `attack-trigger`. CR 120.1 is a CLOSED
        # recipient enumeration -- "Objects can deal damage to battles,
        # creatures, planeswalkers, and players" -- sealed by 120.1a: "Damage
        # can't be dealt to an object that's not a battle, a creature, or a
        # planeswalker." So the recipient slot is enumerable, not open.
        m_recv = re.search(r"\b(?:is|are) dealt\b([^,]{0,60}?)\bdamage\b", clause)
        if m_recv:
            qual = m_recv.group(1)
            # CR 120.10 makes "excess damage" its own triggered-ability check:
            # "Some triggered abilities check whether a permanent has been
            # dealt EXCESS damage." A CR-defined qualifier, not prose.
            if re.search(r"\bexcess\b", qual):
                return None, "is-dealt-excess-damage"
            # `combat-` is a RESTRICTION, not decoration
            # (DAMAGE-DELIVERY-RULING-2026-08-02), and its negation is printed
            # too -- "noncombat damage" is a real, narrower claim.
            if re.search(r"\bnoncombat\b", qual):
                return None, "is-dealt-noncombat-damage"
            if re.search(r"\bcombat\b", qual):
                return None, "is-dealt-combat-damage"
            return None, "is-dealt-damage"
        if re.search(r"\bdeals? damage to\b.{0,24}\bplayer\b", clause):
            return mark("any-damage-to-player", "any-damage-player")
        if re.search(r"\bdeals? damage to\b", clause):
            return mark("any-damage-to-creature", "any-damage-creature")
        if re.search(r"\bupkeep\b", clause):
            return mark("upkeep-trigger", "upkeep")
        if re.search(r"\bend step\b", clause):
            return mark("end-step-trigger", "end-step")
        if re.search(r"beginning of (each |your )?combat", clause):
            return mark("begin-combat-trigger", "begin-combat")
        # CR 511.2: "Abilities that trigger 'at end of combat' trigger as the
        # end of combat step begins." Tested on the CLAUSE -- 94 further cards
        # print the same phrase as a DURATION inside an effect, which CR 603.7
        # makes a delayed trigger whose source is the creating ability
        # (603.7d/e), so those belong to their creator, not here.
        if re.search(r"\bend of combat\b", clause):
            return mark("end-combat-trigger", "end-combat")
        if re.search(r"\bdraw step\b", clause):
            return None, "draw-step"
        if re.search(r"\bbecomes the target of\b", clause):
            return mark("becomes-targeted-trigger", "becomes-targeted")
        if re.search(r"\bblocks\b|\bbecomes blocked\b", clause):
            return mark("blocks-or-becomes-blocked-trigger", "blocks")
        # --- Captain-ratified 2026-08-03, the six remaining trigger tokens ---
        # ORDER MATTERS: "whenever you cycle OR DISCARD a card" contains the
        # word "discard", so every cycling shape must be claimed before the
        # generic discard-trigger branch below or it is swallowed by it.
        # CR 702.29d also states these fire ONCE per cycle, which is what makes
        # cycle-or-discard a distinct shape rather than a naive "cycle OR
        # discard" reading.
        if re.search(r"\bcycles? or discards?\b|\bcycle or discard\b", clause):
            return mark("cycle-or-discard-trigger", "cycle-or-discard")
        if re.search(r"\bcycles?\b", clause):
            # CR 702.29c "When you cycle THIS CARD" is the source; "whenever you
            # cycle A card" is any card. §2a's subject prefix already names that
            # difference, so there is no separate `cycles-a-card-trigger` token
            # -- minting one would give two slugs for one mechanic (design
            # goal #1).
            return msub("cycled-trigger", "cycled")
        # CR 106.12a: "is tapped for mana" triggers when a MANA ABILITY resolves
        # and produces mana -- strictly narrower than becoming tapped, so it is
        # claimed first and is not a synonym of becomes-tapped (CR 603.2e).
        if re.search(r"\bis tapped for mana\b|\btapped for mana\b", clause):
            return mark("tapped-for-mana-trigger", "tapped-for-mana")
        # CR 603.2e: "becomes tapped/untapped" is a STATE CHANGE and does not
        # trigger if the permanent enters the battlefield in that state -- so it
        # is neither `enters-tapped` (a replacement, CR 614) nor a tapped-state
        # check.
        if re.search(r"\bbecomes? untapped\b", clause):
            return msub("becomes-untapped-trigger", "becomes-untapped")
        if re.search(r"\bbecomes? tapped\b", clause):
            return msub("becomes-tapped-trigger", "becomes-tapped")
        if re.search(r"\bis turned face up\b|\bturned face up\b", clause):
            return None, "turned-face-up"
        # ORDER MATTERS, same reason as the cycling pair above. CR 701.9b
        # distinguishes a discard the AFFECTED PLAYER chooses from one that
        # "another player" directs. "When a spell or ability an opponent
        # controls CAUSES you to discard this card" is keyed on WHO CAUSED it
        # and never fires on a voluntary discard -- folding it into
        # discard-trigger would assert something false of all 11 lines
        # (Sand Golem, Quagnoth, Guerrilla Tactics, the madness-adjacent
        # family). Ruled a distinct shape, NOT ratified: reported as its own
        # gap rather than approximated onto the nearest ratified token.
        if re.search(r"causes? (?:you|a player|that player|them) to discard",
                     clause):
            return None, "caused-to-discard-trigger"
        # CR 701.9a: "To discard a card, move it from its owner's HAND to that
        # player's graveyard." Captain-ratified 2026-08-04.
        if re.search(r"\bdiscards?\b", clause):
            return msub("discard-trigger", "discard")
        # CR 122.1 noun sense is ALWAYS TYPED (§8 rule 1); the bare noun
        # "counter" never appears in a slug. §8a ratified `any-` for axes that
        # genuinely span every counter type and therefore cannot be typed.
        # This is a §11 GRAMMAR family -- `<type>-counter-placed-trigger` --
        # so a new counter type instantiates without fresh ratification.
        # The type word must be captured WITHOUT a leading \b -- "+" is not a
        # word character, so \b before "+1/+1" matched at the "1" and produced
        # the nonsense type `1/+1`. §8 rule 1's polarity tokens are `plus1` /
        # `minus1` (ratified), never the printed glyphs.
        m_ctr = re.search(r"([+\-]\d/[+\-]\d|[a-z][a-z0-9]*)\s+counters?\s+"
                          r"(?:are|is)\s+put on", clause)
        if m_ctr or re.search(r"counters? (are|is) put on", clause):
            word = m_ctr.group(1) if m_ctr else ""
            if word == "+1/+1":
                return None, "plus1-counter-placed"
            if word == "-1/-1":
                return None, "minus1-counter-placed"
            # "one or more counterS are put on" -- no type word to bind to, so
            # §8a's `any-` fills the type slot rather than leaving it bare.
            if word in ("", "more", "or"):
                return None, "any-counter-placed"
            return None, f"{word}-counter-placed"
        # CR 119.9 names this trigger family in its own sentence: "Some
        # triggered abilities are written, 'Whenever [a player] gains life,
        # . . . .' Such abilities are treated as though they are written,
        # 'Whenever A SOURCE CAUSES [a player] to gain life'." So unlike
        # discard -- where CR 701.9b makes "causes you to discard" a SEPARATE
        # shape -- the CR here EQUATES the two phrasings, and Firesong and
        # Sunspeaker's "whenever a white instant or sorcery spell causes you to
        # gain life" is the same token with a source restriction.
        # Descriptor is `gain-life`, NOT `lifegain`: grammar §14 Q5 excluded
        # the token `lifegain` as a synonym collision against the ratified §4
        # EFFECT verb `gain-life` (design goal #1).
        if re.search(r"\bgains? life\b|\bcauses?\b.{0,40}\bto gain life\b|"
                     r"\bgained\b", clause):
            return None, "gain-life-trigger"
        # SIXTH whole-line-vs-clause instance. Afiya Grove ("When this
        # enchantment has no +1/+1 counters on it, SACRIFICE IT") and Ember
        # Swallower ("When this creature becomes monstrous, SACRIFICE three
        # lands") were counted as sacrifice triggers by their EFFECT text.
        if re.search(r"\bsacrifices?\b", clause):
            return msub("sacrifice-trigger", "sacrifice")
        return None, "unclassified-trigger"

    # CR 614.1c names THREE replacement templates verbatim: "[This permanent]
    # enters with . . . ," "As [this permanent] enters . . . ," and "[This
    # permanent] enters as . . ." Only the first was matched, so 236 lines
    # printing the second template fell through to `spell-or-static` -- which
    # the gap census EXCLUDES, so the defect was invisible rather than merely
    # unfixed. CR 708.11 extends the same treatment to "As [this permanent] is
    # turned face up . . .", applied WHILE the permanent turns face up.
    # The lookahead keeps CR 601.2b additional-cost clauses and `as long as`
    # static abilities out -- neither is a replacement effect.
    if re.match(r"^as (?!an additional cost|long as)\b.{0,40}?"
                r"\b(?:enters|is turned face up)\b", low) or \
       re.search(r"\benters as\b", low) or \
       re.search(r"\bwould\b.{0,60}\binstead\b|\bskips?\b|\benters? with\b|\benters? tapped\b", low):
        return ("replacement", "replacement") if "replacement" in ratified else (None, "replacement")
    if re.search(r"^(enchant|equipped creature|enchanted )", low):
        return ("static", "static-aura") if "static" in ratified else (None, "static-aura")
    return None, "spell-or-static"


def find_action(line: str, forms: list) -> tuple:
    """Locate a CR action used as an EFFECT. Returns (matched_form, position) or
    (None, -1). A hit inside a created-ability quote is rejected per §2, and so
    is a hit inside a trigger CONDITION -- the Val, Marooned Surveyor class,
    where 'investigate' names the trigger event, not the effect."""
    for form in sorted(forms, key=len, reverse=True):
        for m in re.finditer(r"\b" + re.escape(form) + r"(s|es|d|ed|ing)?\b", line, re.I):
            if in_created_ability(line, m.start()):
                continue
            prefix = line[:m.start()].lower()
            if re.match(r"^\s*when(ever)?\b", prefix) and "," not in prefix:
                continue   # still inside the trigger clause
            return form, m.start()
    return None, -1


# ---------------------------------------------------------------------------
# passes
# ---------------------------------------------------------------------------
def scan(cards: dict, ratified: dict, action_forms=None) -> list:
    rows = []
    for oid, card in cards.items():
        for line in ability_lines(card):
            if action_forms is not None:
                form, pos = find_action(line, action_forms)
                if form is None:
                    continue
            else:
                form = None
            for tok, desc in parse_deliveries(line, ratified, card):
                rows.append({
                    "oracle_id": oid, "name": card["name"], "line": line,
                    "delivery": tok, "descriptor": desc, "matched": form,
                    "created_ability": bool(quoted_spans(line)),
                })
    return rows


def cmd_gaps(args, cards, ratified, actions):
    """Corpus-wide census of delivery shapes that have NO ratified token.

    This is the ratification-throughput lever: it ranks the missing vocabulary
    by how many cards it blocks across the WHOLE corpus, so one vocabulary
    batch can be ruled with the real numbers in hand -- rather than the gaps
    being rediscovered one mechanic at a time, which is what happened to Clues.
    """
    rows = scan(cards, ratified, None)
    gap = collections.Counter()
    cardset = collections.defaultdict(set)
    for r in rows:
        if r["delivery"] is None and r["descriptor"] not in ("spell-or-static",):
            gap[r["descriptor"]] += 1
            cardset[r["descriptor"]].add(r["name"])
    print(f"ratified DELIVERY tokens parsed from grammar §2: {len(ratified)}")
    print(f"  {', '.join(sorted(ratified))}\n")
    print(f"ability lines scanned: {len(rows)}   gate-passing cards: {len(cards)}\n")
    print(f"{'unratified delivery shape':38s} {'lines':>7} {'cards':>7}")
    print("-" * 56)
    for desc, n in gap.most_common():
        print(f"{desc:38s} {n:7d} {len(cardset[desc]):7d}")
    if args.json:
        Path(args.json).write_text(json.dumps(
            {d: {"lines": n, "cards": sorted(cardset[d])} for d, n in gap.most_common()},
            indent=1), encoding="utf-8")
        print(f"\nwrote {args.json}")


def cmd_action(args, cards, ratified, actions):
    """Every card printing one CR keyword action, grouped by delivery shape."""
    if args.action not in actions:
        near = [t for t in actions if args.action in t]
        fc.halt(f"{args.action!r} is not a CR term in cr-checks.json. "
                f"Did you mean: {', '.join(near[:8]) or '(no near matches)'}")
    meta = actions[args.action]
    rows = scan(cards, ratified, meta["forms"])
    groups = collections.defaultdict(list)
    for r in rows:
        key = r["delivery"] or f"UNRATIFIED:{r['descriptor']}"
        if r["created_ability"] and r["delivery"] is None:
            key = "UNRATIFIED:created-ability(§2)"
        groups[key].append(r)
    cards_hit = {r["oracle_id"] for r in rows}
    print(f"CR {meta['cr']}  {args.action}  ({meta['kind']})")
    print(f"forms: {', '.join(meta['forms'])}")
    print(f"cards: {len(cards_hit)}   ability lines: {len(rows)}\n")
    ready = sum(len(v) for k, v in groups.items() if not k.startswith("UNRATIFIED"))
    print(f"  buildable now (ratified delivery): {ready} lines")
    print(f"  need a ruling:                     {len(rows) - ready} lines\n")
    for key in sorted(groups, key=lambda k: (-len(groups[k]), k)):
        rs = groups[key]
        print(f"## {key}   n={len(rs)}")
        for r in sorted(rs, key=lambda r: r["name"])[:args.limit]:
            print(f"   {r['name'][:36]:38s} {r['line'][:88]}")
        if len(rs) > args.limit:
            print(f"   … and {len(rs) - args.limit} more")
        print()
    if args.json:
        Path(args.json).write_text(json.dumps(rows, indent=1), encoding="utf-8")
        print(f"wrote {args.json}")


def cmd_rank(args, cards, ratified, actions):
    """Rank every CR keyword action by how much of it is buildable today.

    Single corpus pass -- one delivery parse per ability line, matched against
    every action at once. Scanning per-action instead would be 262 full passes.
    """
    covered = codebook_covered_actions()
    # CR 701 is the keyword-ACTION section. 702 keywords (flying, trample) are
    # static/evasion abilities, not actions, and they are the keyword-bucket
    # job -- including them buries the population this ranking is about.
    actions = {t: m for t, m in actions.items() if str(m["cr"]).startswith("701.")}
    stat = collections.defaultdict(lambda: {"cards": set(), "ready": 0, "blocked": 0})
    for oid, card in cards.items():
        for line in ability_lines(card):
            parsed = None
            for term, meta in actions.items():
                form, _ = find_action(line, meta["forms"])
                if form is None:
                    continue
                if parsed is None:
                    parsed = parse_deliveries(line, ratified, card)
                s = stat[term]
                s["cards"].add(oid)
                for tok, _d in parsed:
                    if tok:
                        s["ready"] += 1
                    else:
                        s["blocked"] += 1
    print(f"{'CR action':24s} {'CR':>8} {'cards':>6} {'ready':>6} {'blocked':>7} {'%':>6}  axis?")
    print("-" * 72)
    rows = sorted(stat.items(), key=lambda kv: -len(kv[1]["cards"]))
    for term, s in rows[:args.limit]:
        n = s["ready"] + s["blocked"]
        pct = 100.0 * s["ready"] / n if n else 0.0
        print(f"{term:24s} {actions[term]['cr']:>8} {len(s['cards']):6d} "
              f"{s['ready']:6d} {s['blocked']:7d} {pct:5.1f}%  "
              f"{'yes' if term in covered else 'NO AXIS'}")


def codebook_covered_actions() -> set:
    """Which CR action words already appear in an active axis slug."""
    try:
        import foundry_codebook as fcb
        cb = fcb.load_codebook()
    except Exception:
        return set()
    toks = set()
    for slug, e in cb["axes"].items():
        if e.get("status") == "active":
            toks.update(slug.replace("rule:", "").split("-"))
    return toks


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gaps", action="store_true",
                    help="corpus-wide census of delivery shapes with no ratified token")
    ap.add_argument("--action", help="one CR keyword action, grouped by delivery shape")
    ap.add_argument("--rank", action="store_true",
                    help="rank CR actions by how much is buildable today")
    ap.add_argument("--limit", type=int, default=12)
    ap.add_argument("--json")
    args = ap.parse_args()

    cards, _, gated_out = fc.load_corpus_gated()
    build_self_noun_rx(cards)
    ratified = ratified_delivery_tokens()
    actions = cr_action_terms()
    build_keyword_homes(ratified)

    if args.gaps:
        cmd_gaps(args, cards, ratified, actions)
    elif args.action:
        cmd_action(args, cards, ratified, actions)
    elif args.rank:
        cmd_rank(args, cards, ratified, actions)
    else:
        ap.error("pick one of --gaps / --action <term> / --rank")


if __name__ == "__main__":
    main()
