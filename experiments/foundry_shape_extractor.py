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
# CR 207.2c ability words are printed with an EM-DASH -- "Landfall —",
# "Battalion —", "Parley —". The pattern also allowed a plain hyphen, and a
# hyphen is a WORD character in Magic templating, so it matched across
# hyphenated names and P/T minus signs and deleted the front of the line:
#
#     "When Spider-Ham enters, create a Food token."  -> "Ham enters, ..."
#     "Whenever a non-Human creature ... attacks, ..." -> "Human creature ..."
#     "Put a -1/-1 counter on target creature."       -> "1/-1 counter ..."
#
# Measured 2026-08-04 across the whole corpus: 556 lines were mutilated -- 333
# minus signs, 223 hyphenated words, and ZERO legitimate ability words. All
# 3,004 real ones use the em-dash. 90 of the 556 were triggers whose CR 113.3c
# condition was decapitated, so they could not enter the trigger branch at all.
#
# Found by a METAMORPHIC test, not by reading: a card's DELIVERY cannot depend
# on its NAME, so renaming every card to a neutral string must not change any
# routing. 62 of the 63 violations were this one line.
ABILITY_WORD = re.compile(r"^\s*[A-Z][A-Za-z'’\- ]{2,40}\s*—\s*")
# CR 606.2: "An activated ability with a loyalty symbol in its cost is a
# loyalty ability." The printed symbol IS the cost, so the shape is the test.
# Sign mandatory except a bare `0`, which is what excludes CR 702.184 Station
# tier bars ("20+ | {T}: …") that the old first-3-characters test swallowed.
LOYALTY_COST = re.compile(r"^([+\u2212\-][0-9X]+|0)\s*:")


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
    """Compile the 'this <noun>' self-reference test.

    TWO SOURCES, because CR 205 makes them different KINDS of list:

      CARD TYPES  -- CR 205.2a publishes a CLOSED list in one sentence, so it
                     is PARSED FROM THE CR (`type_vocabulary`, which already
                     existed for CR 702.14a's landwalk template). Harvesting
                     these from the corpus is what this fix replaces, and it
                     was losing SIX of the fifteen: conspiracy, dungeon,
                     phenomenon, plane, scheme and vanguard -- including
                     CR 109.2d's OWN worked case, *"If an ability of a scheme
                     card includes the text 'this scheme,' it means the scheme
                     card in the command zone on which that ability is
                     printed."* The corpus gate excludes those layouts, so the
                     vocabulary was derived from a population that STRUCTURALLY
                     CANNOT contain them -- a hand-list's failure mode with a
                     data source standing in for the hand. Measured today all
                     six are at zero corpus lines; zero members is a hypothesis
                     (the `is-attacked-trigger` battle-slot precedent), and a
                     widened gate must not silently fail to see them.

      SUBTYPES    -- CR 205.3b makes these open and set-specific ("Equipment",
                     "Siege", "Spacecraft", "Class", "Case"), and the CR does
                     not enumerate them in one place, so the corpus harvest is
                     legitimate here and stays. It is now taken only from AFTER
                     the long dash, per CR 205.3b's own description of where
                     subtypes are printed.

    SUPERTYPES ARE EXCLUDED. CR 205.4a's five (basic, legendary, ongoing, snow,
    world) are adjectives, never the noun of a self-reference -- no card says
    "this legendary". The old whole-type-line harvest swept them in, along with
    planeswalker names (ajani, ashiok, arlinn) picked up as planeswalker
    subtypes.
    """
    global SELF_NOUN_RX
    import foundry_cr702_classes as k7
    vocab = k7.type_vocabulary()
    nouns = set(_ALWAYS_SELF_NOUNS) | set(vocab["card_types"])
    supertypes = set(vocab["supertypes"])
    for card in cards.values():
        parts = [card.get("type_line") or ""]
        parts += [f.get("type_line") or "" for f in (card.get("card_faces") or [])]
        for part in parts:
            # CR 205.3b: "Subtypes ... are listed AFTER A LONG DASH."
            for chunk in part.split("//"):
                if "—" not in chunk:
                    continue
                for word in re.findall(r"[A-Za-z'’\-]+", chunk.split("—", 1)[1]):
                    if len(word) > 2 and word.lower() not in supertypes:
                        nouns.add(word.lower())
    if "equipment" not in nouns:
        fc.halt("Derived self-reference noun set has no 'equipment' — the "
                "corpus type lines did not load. Refusing to run with a "
                "vocabulary that would silently misfile self-triggers.")
    missing = sorted(set(vocab["card_types"]) - nouns)
    if missing:
        fc.halt(f"Self-reference noun set is missing CR 205.2a card types: "
                f"{missing}. Every card type must be reachable as a 'this "
                f"<type>' self-reference (CR 109.2d).")
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


def deliveries_for_lines(card: dict, ratified: dict):
    """(line, [(token, descriptor), ...]) for every ability line of `card`,
    with D3's modal-mode inheritance applied.

    A modal ability is printed as a HEADER line carrying the delivery, then one
    `• ` line per mode:

        When this creature enters, choose one —      <- etb
        • Cure Wounds — You gain 2 life.             <- had NO delivery
        • Dispel Magic — Destroy target enchantment. <- had NO delivery

    Split on newlines, each bullet became its own ability line with no trigger
    of its own, so 516 bullets under a delivery-bearing header routed nowhere.
    Grammar §1 is explicit that this is wrong -- *"modal modes each earn their
    axis"*, and Blizzard Specter is its worked case.

    The mode's delivery IS the header's delivery, so it is INHERITED rather
    than re-parsed from a joined string: re-parsing would hand `trigger_clause`
    a header condition glued to a mode's effect text, which is the CR 113.3c
    whole-line-vs-clause bug this file has now been bitten by six times.

    The modal test is `foundry_common._MODAL_HEADER_RE`, the ratified DET
    preprocessing standard v1 (2026-07-31) -- not a fresh one. Bullets under a
    non-modal header are deliberately NOT inherited: Celebr-8000's
    `• 2 — menace` is a die-roll RESULT table, not a set of modes.
    """
    lines = ability_lines(card)
    header_deliveries, is_modal = None, False
    for line in lines:
        if line.lstrip().startswith("•"):
            if is_modal and header_deliveries:
                yield line, [(t, f"modal-mode:{d}") for t, d in header_deliveries]
            else:
                yield line, parse_deliveries(line, ratified, card)
            continue
        parsed = parse_deliveries(line, ratified, card)
        header_deliveries = [(t, d) for t, d in parsed if t is not None]
        is_modal = bool(fc._MODAL_HEADER_RE.search(line.strip()))
        yield line, parsed


_SPELL_TYPE = re.compile(r"\b(Instant|Sorcery)\b")


def _has_spell_face(card: dict) -> bool:
    """Does ANY face of this card have an instant/sorcery type line?

    CR 113.3a makes a spell ability possible only on an instant or sorcery, so
    this is the test for "could a line on this card be an unmarked spell
    ability at all". It is deliberately ALL-FACES and deliberately pessimistic:
    `ability_lines` joins every face's text into one stream, so a line on the
    creature half of a Creature // Sorcery card is indistinguishable here from
    a line on the sorcery half. One instant/sorcery face disqualifies the whole
    card rather than risking a spell ability being marked `static`."""
    faces = [card.get("type_line") or ""]
    faces += [f.get("type_line") or "" for f in (card.get("card_faces") or [])]
    return any(_SPELL_TYPE.search(t) for t in faces)


def quoted_spans(line: str) -> list:
    """Character ranges inside double quotes -- granted or token ability text.
    §2's created-ability rule: a card does not deliver an ability it CREATES."""
    return [(m.start(), m.end()) for m in re.finditer(r"[\"“][^\"”]*[\"”]", line)]


def in_created_ability(line: str, pos: int) -> bool:
    return any(a <= pos < b for a, b in quoted_spans(line))


def in_card_name(line: str, pos: int, card: dict) -> bool:
    """Is `pos` inside an occurrence of the card's own printed NAME?

    A positional guard, the same shape as `in_created_ability`. Needed because
    CR 113.3b's cost test keys on a colon, and a handful of cards have a colon
    IN THEIR NAME -- `Ultimate Magic: Meteor deals 7 damage to each creature.`
    is a spell ability, not a `Ultimate Magic:` cost.

    `fc.canonicalize_self_reference` normally collapses the name to `~` before
    this point and would have prevented the question; it does not fire on these
    because the colon breaks its matching. That is the root cause and it lives
    in a shared ratified helper, so it is reported rather than patched here.
    """
    if not card:
        return False
    names = [card.get("name") or ""]
    names += [f.get("name") or "" for f in (card.get("card_faces") or [])]
    for name in names:
        if ":" not in name:
            continue          # only a colon-bearing name can create this case
        start = 0
        while True:
            a = line.find(name, start)
            if a < 0:
                break
            if a <= pos < a + len(name):
                return True
            start = a + 1
    return False


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
    present, then stop at that segment's end.

    A clause may also never run into a QUOTED created ability. §2's ratified
    created-ability rule -- "a card does not deliver an ability it CREATES" --
    already says so, and without the guard a missing event verb walks the clause
    straight into the quote: Benalish Knight-Counselor's "Whenever ~ ENLISTS a
    creature, you get a one-time boon with 'When you CAST a creature spell...'"
    was read as a cast-trigger off the boon's text. `enlist` and `unlock` are CR
    702 keywords, not CR 701 keyword-ACTIONS, so the derived verb set cannot
    contain them -- and hand-adding them is what the 2026-08-04 derivation
    deliberately stopped doing. The structural guard needs no verb list."""
    cuts, depth = [], 0
    for i, ch in enumerate(low):
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        elif ch == "," and depth == 0:
            cuts.append(i)
    quote_at = min((a for a, _b in quoted_spans(low)), default=len(low))
    if not cuts:
        return low[:quote_at]
    for i in cuts:
        if i > quote_at:
            break
        if TRIGGER_VERB.search(low[:i]):
            return low[:i]
    return low[:min(cuts[0], quote_at)]



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
            if k7.effective_classes(kw) == ["static"] and "static" in ratified:
                tok = "static"
        if tok:
            homes[kw["name"].lower()] = tok
    if "battle cry" not in homes:
        fc.halt("Keyword home map has no 'battle cry' — the CR 702 parse "
                "failed. Refusing to run with a partial keyword vocabulary.")
    if homes.get("equip") != "activated":
        fc.halt("Equip is not routing to `activated`. CR 702.6a states it "
                "outright and §2b quotes that rule as its worked example; a "
                "map that loses it is not a §2b router.")
    KEYWORD_HOME = homes
    build_landwalk_template(k7)
    build_keyword_forms(kws, k7)


# CR 702.14a: *"Landwalk is a generic term that appears within an object's
# rules text as '[type]walk,' where [type] is usually a land type, but it can
# also be the card type land plus any combination of land types, card types,
# and/or supertypes."*
#
# So CR 702.14's own heading -- "Landwalk" -- is the one name NO card prints.
# `landwalk` sat in KEYWORD_HOME and every variant a card actually prints was
# absent, so Whispering Shade's bare "Swampwalk" line was not a keyword line at
# all. The template is a GRAMMAR over CR 205's type lists, so it is derived the
# same way, not enumerated: an enumeration would have to guess which of the 17
# land types ever appear, and 702.14c's own examples span three shapes
# ("artifact landwalk", "nonbasic landwalk", "snow swampwalk").
LANDWALK_BASES = None      # what may sit immediately left of "walk"
LANDWALK_MODIFIERS = None  # what may precede that base


def build_landwalk_template(k7) -> None:
    global LANDWALK_BASES, LANDWALK_MODIFIERS
    v = k7.type_vocabulary()
    LANDWALK_BASES = v["land_types"] | {"land"}
    LANDWALK_MODIFIERS = v["land_types"] | v["card_types"] | v["supertypes"]
    if not {"swamp", "island", "land"} <= LANDWALK_BASES:
        fc.halt(f"CR 205.3i parse lost a basic land type: {sorted(LANDWALK_BASES)}")


def landwalk_variant(part: str) -> bool:
    """Is `part` a CR 702.14a '[type]walk' name?

    Strict on purpose. `planeswalk` is not one -- CR 205.2a's card type is
    `plane`, not `planes` -- and neither is Quagmire's "creatures with
    swampwalk can be blocked as though they didn't have swampwalk", which ends
    in the right seven letters and is a sentence, not a keyword."""
    if LANDWALK_BASES is None or not part.endswith("walk"):
        return False
    words = part[:-len("walk")].split()
    if not words or words[-1] not in LANDWALK_BASES:
        return False
    # CR 702.14c's "nonbasic landwalk" -- the `non` prefix negates a supertype
    # rather than naming a new one.
    return all(w in LANDWALK_MODIFIERS or
               (w.startswith("non") and w[3:] in LANDWALK_MODIFIERS)
               for w in words[:-1])


COST_OR_PARAM = re.compile(r"\{[^}]*\}|\bN\b|\d+")

# D8. A printed keyword list is joined by a comma OR a semicolon, and only the
# comma was handled -- "Flying; banding", "Defender; reach", "Trample; rampage
# 1", "Flying; trample; rampage 4". 34 lines. There is no CR question here:
# both are ordinary list punctuation, and the semicolon carries no rules
# meaning the comma does not. Shared by BOTH keyword paths so the two cannot
# drift apart -- `keyword_line_tokens` now falls through to
# `keyword_form_tokens`, and fixing only one would leave
# "Protection from red; banding" (a §2b parameterized form beside a bare
# keyword) split correctly on one path and not the other.
KEYWORD_LIST_SPLIT = re.compile(r"[,;]")

# ---------------------------------------------------------------------------
# D4 -- PARAMETERIZED keyword lines, derived from each keyword's own CR form
# ---------------------------------------------------------------------------
# COST_OR_PARAM only strips mana symbols and bare digits, so a keyword whose
# parameter is TYPED or a CLAUSE is invisible to the test above: `Ward-Pay 3
# life.`, `Equip Knight {1}`, `Craft with artifact {2}{W}`, `Champion a
# Kithkin`. Measured: 172 such lines on a NON-`static` home.
#
# The locked rule applies -- do not hand-list the forms, PARSE THEM. The CR
# states each keyword's printed form verbatim, and it does so in FOUR shapes,
# all four of which are load-bearing:
#
#   QUOTED     702.6a   "Equip [cost]" means ...
#   UNQUOTED   702.21a  Ward [cost] means ...          <- Ward is the single
#                                                         biggest keyword here
#                                                         (53 lines); a
#                                                         quote-only parse
#                                                         loses all of it
#   WRITTEN    702.57a  It's written "Forecast - [Activated ability]."
#              702.167a It is written as "Craft with [materials] [cost],"
#   IN-FORM    702.6c   restrictions ... appear in the form "Equip [quality]"
#                       or "Equip [quality] creature."
#
# SAFETY FILTER: a captured form counts only if it BEGINS with the keyword's
# own name. Without it, 702.29c's `"When you cycle this card" means ...`
# becomes a printed form of Cycling, which it is not.
KEYWORD_FORMS = None      # keyword name (lower) -> [compiled form regex]

# A cost is not free text. CR 118.1 makes it mana and/or an action, and oracle
# text prints it two ways only: a symbol run, or a long dash + an action
# clause. The dash is the CR's OWN convention -- 702.49a writes the form as
# "Reinforce N-[cost]", with the dash inside the quoted form.
_KF_SYMS = r"(?:\{[^}]*\}\s*)+"
# ... and a symbol run may be a CHOICE: "Cumulative upkeep {W} or {U}".
_KF_SYMBOL_RUN = rf"{_KF_SYMS}(?:(?:or|and)\s+{_KF_SYMS})*"
# The clause may contain commas ("Ward-{2}, Pay 2 life.") but may NOT cross a
# sentence boundary. Without that bound, "Equip-Sacrifice another nonland
# permanent. Activate only once each turn." matched while its symbol-form twin
# "Equip {0}. Activate only once each turn." did not -- one shape decided two
# ways by which arm happened to match.
_KF_DASH_CLAUSE = r"[—–]\s*(?:[^—–.]|\.(?=\s*$))+"
_KF_COST = rf"(?:{_KF_SYMBOL_RUN}|{_KF_DASH_CLAUSE})"
_KF_NUMBER = r"(?:\d+|x)"
_KF_PHRASE = r"[a-z][a-z',/ ]*"          # [quality] [object] [text] [materials]
_KF_ACTIVATED = r".+:.+"                  # [Activated ability] -- CR 113.3b
_KF_PLACEHOLDER = re.compile(r"\[([^\]]+)\]")

_KF_QUOTED_MEANS = re.compile(r"[“\"]([^”\"]+)[”\"]\s+means\b")
_KF_WRITTEN = re.compile(r"written(?:\s+as)?\s+[“\"]([^”\"]+)[”\"]", re.I)
_KF_IN_FORM = re.compile(
    r"in the form\s+((?:[“\"][^”\"]+[”\"]\s*(?:or|and)?\s*)+)", re.I)
_KF_QUOTED_ANY = re.compile(r"[“\"]([^”\"]+)[”\"]")


def cr_printed_forms(kw: dict) -> list:
    """Every printed form the CR states for this keyword, in rule order."""
    name = (kw.get("name") or "").strip()
    if not name:
        return []
    low, out = name.lower(), []
    for _letter, text in sorted(kw.get("subrules", {}).items()):
        cands = _KF_QUOTED_MEANS.findall(text) + _KF_WRITTEN.findall(text)
        for blob in _KF_IN_FORM.findall(text):
            cands += _KF_QUOTED_ANY.findall(blob)
        for m in re.finditer(r"\b" + re.escape(name) + r"\b([^.“”\"]{0,40}?)\s+means\b",
                             text, re.I):
            cands.append(name + m.group(1))
        for c in cands:
            c = c.strip().rstrip(".,").strip()
            if c.lower().startswith(low) and c not in out:
                out.append(c)
    # COMPOSITION, CR 702.6a + 702.6c. 702.6c states Equip's restriction form
    # WITHOUT the cost -- "Equip [quality]" -- but 702.6a's cost is still part
    # of the ability, and every printed card carries both ("Equip Knight {1}",
    # "Equip legendary creature {2}"). Composing the two rules is a derivation
    # from the CR; reading 702.6c literally loses 18 Equip lines.
    if any("[cost]" in f.lower() for f in out):
        for f in list(out):
            if "[cost]" not in f.lower() and f + " [cost]" not in out:
                out.append(f + " [cost]")
    return out


def _kf_form_to_regex(form: str) -> str:
    """CR printed form -> regex. The separator before a placeholder is NOT
    uniform, and getting it wrong is how a keyword matcher eats prose:

      before a COST   `\\s*` -- the cost may follow a long dash with no space.
      everywhere else `\\s+` -- REQUIRED. With `\\s*`, 702.6c's "Equip
                                [quality]" matched Kor Blademaster's
                                "EQUIPPED Warriors you control have double
                                strike" -- a static routed to `activated`.
    """
    out, last = [], 0
    for m in _KF_PLACEHOLDER.finditer(form):
        lit = re.escape(form[last:m.start()]).replace(r"\ ", r"\s+")
        kind = m.group(1).lower()
        is_cost = kind == "cost"
        if is_cost and lit.endswith(r"\s+"):
            lit = lit[: -len(r"\s+")] + r"\s*"
        out.append(lit)
        out.append(_KF_COST if is_cost
                   else _KF_ACTIVATED if kind.startswith("activated abilit")
                   else _KF_PHRASE)
        last = m.end()
    out.append(re.escape(form[last:]).replace(r"\ ", r"\s+"))
    pat = "".join(out)
    # The CR writes the article that suits ITS placeholder word (702.72a,
    # "Champion an [object]"); a card prints the article agreeing with the
    # object it actually names. Nine of Champion's twelve lines print "a".
    pat = re.sub(r"\ban(?=\\s\+)", "an?", pat)
    # A literal `\d` in a re.sub REPLACEMENT is read as a group escape, not as
    # the character class -- hence the lambda. Same family as the recorded
    # `re.escape`-before-substitution trap.
    pat = re.sub(r"(?<![A-Za-z])N(?![A-Za-z])", lambda _m: _KF_NUMBER, pat)
    pat = re.sub(r"(?<![A-Za-z\\])X(?![A-Za-z])", lambda _m: _KF_NUMBER, pat)
    return pat


def build_keyword_forms(kws: dict, k7) -> None:
    global KEYWORD_FORMS
    forms = {}
    for num, kw in kws.items():
        if not kw["name"] or num == k7.PREAMBLE_RULE:
            continue
        rxs = []
        for f in cr_printed_forms(kw):
            # A form whose parameter is a whole ABILITY is REFUSED here, and
            # this is the one guard that had to be added after measurement.
            # CR 702.178a: `"Max speed — [Ability]" means "As long as your
            # speed is 4, this object has '[Ability]'."` The parameter is a
            # real ability with its own delivery, which the classifier already
            # reads correctly -- so matching the wrapper OVERWRITES a correct
            # ratified routing with the wrapper's class. Measured: it moved
            # Pride of the Road off `begin-combat-trigger` and Vnwxt off
            # `replacement`, both onto `static`. Destroying a correct routing
            # is the exact failure PRE-STEP-2-AUDIT stopped step 2 for.
            # §2's created-ability rule says the same thing: the delivery
            # belongs to the ability, not to the wrapper that grants it.
            if re.search(r"\[[^\]]*\babilit(?:y|ies)\b[^\]]*\]", f, re.I):
                continue
            try:
                rxs.append(re.compile("^" + _kf_form_to_regex(f) + r"\.?$", re.I))
            except re.error as e:
                fc.halt(f"CR 702 printed form {f!r} for {kw['name']} did not "
                        f"compile: {e}. Fix the derivation; never fall back to "
                        f"a hand-written form list.")
        if rxs:
            forms[kw["name"].lower()] = rxs
    # Halt-guard. A silently-degraded CR parse would make every parameterized
    # keyword line look unrouted, which is exactly the defect being closed.
    for anchor in ("ward", "equip", "craft", "cumulative upkeep", "champion"):
        if anchor not in forms:
            fc.halt(f"No CR printed form derived for {anchor!r}. The 702 parse "
                    f"has degraded; refusing to run with a partial form set.")
    KEYWORD_FORMS = forms


def _keyword_by_form(part: str):
    """The keyword this whole part names, by CR printed FORM or by bare name.

    Both are checked here because a printed list may MIX the two, and the two
    paths could not previously cooperate on one line: `Protection from red;
    banding` has a parameterized form on the left (CR 702.16b's
    "Protection from [quality]") and a bare keyword on the right. The
    bare-name path rejected the line because of the left half, the form path
    rejected it because of the right, and it routed nowhere -- while
    `Protection from black; flanking` routed fine only because Flanking
    happens to have a CR form too.
    """
    if not KEYWORD_FORMS:
        return None
    low = part.lower()
    if low in KEYWORD_HOME:
        return low
    if landwalk_variant(low):
        return "landwalk"
    for name, rxs in KEYWORD_FORMS.items():
        if name in KEYWORD_HOME and any(rx.match(part) for rx in rxs):
            return name
    return None


def keyword_line_tokens(line: str) -> list:
    """Tokens for a line that IS one or more printed keywords, else []."""
    if KEYWORD_HOME is None:
        return []
    core = COST_OR_PARAM.sub("", line).strip().rstrip(".").lower()
    core = re.sub(r"\s+", " ", core)
    if not core:
        return []
    parts = [p.strip() for p in KEYWORD_LIST_SPLIT.split(core) if p.strip()]
    if parts and all(p in KEYWORD_HOME or landwalk_variant(p) for p in parts):
        out, seen = [], set()
        for p in parts:
            t = KEYWORD_HOME[p] if p in KEYWORD_HOME else KEYWORD_HOME["landwalk"]
            if t not in seen:
                seen.add(t)
                out.append((t, f"keyword:{p}"))
        return out
    return keyword_form_tokens(line)


def keyword_form_tokens(line: str) -> list:
    """D4: the same job for keywords whose parameter is TYPED or a CLAUSE.

    WHOLE LINE FIRST, comma-split second. A keyword parameter may itself
    contain commas -- "Ward-{2}, Pay 2 life.", "Craft with a Dinosaur, a
    Merfolk, a Pirate, and a Vampire {4}" -- so splitting first destroys the
    form before it is ever tested. Splitting stays the fallback because a line
    may also be a comma-LIST of keywords.

    A keyword with no §2 home is NOT routed here. Those are D9 (49 keywords /
    ~1,229 lines) and KEYWORD-LEDGER-CANDIDATES.md sends them to Phase B; that
    is a Captain ruling, not a fix, so `_keyword_by_form` gates on KEYWORD_HOME.
    """
    if not KEYWORD_FORMS:
        return []
    text = line.strip()
    names = None
    whole = _keyword_by_form(text)
    if whole:
        names = [whole]
    else:
        parts = [p.strip() for p in KEYWORD_LIST_SPLIT.split(text) if p.strip()]
        if parts:
            got = [_keyword_by_form(p) for p in parts]
            if all(got):
                names = got
    if not names:
        return []
    out, seen = [], set()
    for n in names:
        t = KEYWORD_HOME[n]
        if t not in seen:
            seen.add(t)
            out.append((t, f"keyword:{n}"))
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

    # loyalty (CR 606.1/606.2) -- MUST be tested before the generic activated
    # branch, not inside it. It used to sit nested under the head-cost test
    # below, which requires a mana symbol or one of six verbs left of the colon.
    # A loyalty cost is `+1`. It has neither, so the outer gate rejected it and
    # the loyalty branch was unreachable for exactly the cards it exists for:
    # measured 2026-08-04, 900 planeswalker loyalty lines fell to
    # `spell-or-static`, while the 7 lines that DID reach `loyalty` were all
    # wrong -- Station tier bars (CR 702.184) printed "20+ | {T}: Add …", where
    # `head.strip()[:3]` saw "20+" and `^[+\-−]?\d` matched the 2.
    #
    # CR 606.2 makes the printed symbol definitional: "An activated ability with
    # a LOYALTY SYMBOL IN ITS COST is a loyalty ability." So anchor on the
    # printed shape, with the sign mandatory except for a bare `0` -- which
    # excludes "20+ |" by construction. Verified corpus-wide: 909 matches, 100%
    # on planeswalkers, zero Station bars.
    if ":" in body and LOYALTY_COST.match(body.strip()) and \
       not in_created_ability(body, body.index(":")):
        return _mark_top("loyalty", "loyalty-ability", ratified)

    # activated -- a cost left of a colon (CR 113.3b), colon not inside quotes
    #
    # D6. The head test used to require `{}` or one of SIX hand-listed verbs,
    # and lost 26 activated abilities whose cost carries no mana symbol:
    # `Put a -1/-1 counter on this creature:` (Barrenton Medic, Wall of Roots),
    # `Return a Forest you control to its owner's hand:` (Quirion Ranger),
    # `Reveal the player you chose:`, `Collect evidence 6:`.
    #
    # **The CR publishes no closed list of cost verbs, and that is why every
    # hand-list here fails.** CR 118.1 defines a cost as *"an action or payment
    # necessary to take another action"* -- deliberately open-ended. What the
    # CR does publish is the STRUCTURE: CR 113.3b, *"Activated abilities have a
    # cost and an effect. They are written as '[Cost]: [Effect.]'"* So the
    # colon is the claim.
    #
    # Extending the list with CR 701's derived keyword actions -- the obvious
    # fix, and the one the work order proposed -- was MEASURED and is
    # insufficient: it catches 11 of the 27 candidates, because `return` and
    # `put` are ordinary English verbs and not CR keyword actions at all. That
    # would have been a hand-list wearing a derivation's clothes.
    #
    # Measured safe: the only lines a pure-structure test could take from
    # another token are the 909 `loyalty` ones, and the loyalty branch above
    # already claims them first. Nothing else in the corpus is at risk.
    if ":" in body:
        i = body.index(":")
        if not in_created_ability(body, i) and not in_card_name(body, i, card):
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
            # Captain-ratified 2026-08-04 (§2 row 14). CR 504.1 -- the token
            # names the STEP, not the draw: the draw itself is a turn-based
            # action, not an ability, so a trigger on the draw EVENT is a
            # different family.
            if re.search(r"\bdraw steps?\b", clause):
                return mark("draw-step-trigger", "draw-step")
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
            # Captain-ratified 2026-08-04 (§2 rows 10-13). `mark`, not `msub`:
            # the ruling measured the printed ZONE, and no §2a subject split
            # was measured on this family. Under-marking is reportable;
            # asserting an unmeasured prefix is not.
            if re.search(r"\bfrom anywhere\b", clause):
                return mark("to-graveyard-from-anywhere-trigger", "to-graveyard-from-anywhere")
            if re.search(r"\bfrom (a |your |their )?library\b", clause):
                return mark("to-graveyard-from-library-trigger", "to-graveyard-from-library")
            if re.search(r"\bfrom (a |your |their )?hand\b", clause):
                return mark("to-graveyard-from-hand-trigger", "to-graveyard-from-hand")
            if re.search(r"\bfrom (a |your |their )?exile\b|\bfrom the stack\b", clause):
                return mark("to-graveyard-from-other-zone-trigger", "to-graveyard-from-other-zone")
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
            # Captain-ratified 2026-08-04 (§2 rows 4-7). §2a applies and was
            # MEASURED on this family -- source 74 · any- 38 · other- 0 -- so
            # these take the subject prefix (msub), not a bare mark.
            if re.search(r"\bexcess\b", qual):
                return msub("is-dealt-excess-damage-trigger", "is-dealt-excess-damage")
            # `combat-` is a RESTRICTION, not decoration
            # (DAMAGE-DELIVERY-RULING-2026-08-02), and its negation is printed
            # too -- "noncombat damage" is a real, narrower claim.
            if re.search(r"\bnoncombat\b", qual):
                return msub("is-dealt-noncombat-damage-trigger", "is-dealt-noncombat-damage")
            if re.search(r"\bcombat\b", qual):
                return msub("is-dealt-combat-damage-trigger", "is-dealt-combat-damage")
            return msub("is-dealt-damage-trigger", "is-dealt-damage")
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
            return mark("draw-step-trigger", "draw-step")
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
        # Captain-ratified 2026-08-04 (§2 row 8). §2a applies and was MEASURED
        # -- source 94 · any- 18 · other- 9 -- so unlike the discard and
        # is-dealt families the `other-` node is POPULATED here (Salt Road
        # Ambushers). Hard-disjoint from `etb` by CR 708.8 / 702.37e.
        if re.search(r"\bis turned face up\b|\bturned face up\b", clause):
            return msub("turned-face-up-trigger", "turned-face-up")
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
        # Captain-ratified 2026-08-04 (§2 row 9). `mark`, not `msub`: CR 119.9's
        # trigger subject is a PLAYER ("Whenever [a player] gains life"), not a
        # permanent, so §2a's source/other/any distinction does not arise. The
        # ruling measured SCOPE instead -- you-control 83 · opponent 3.
        if re.search(r"\bgains? life\b|\bcauses?\b.{0,40}\bto gain life\b|"
                     r"\bgained\b", clause):
            return mark("gain-life-trigger", "gain-life")
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
    # D5. The `{0,60}` window between `would` and `instead` was a hand-chosen
    # number with no CR behind it, and it lost 128 permanent-side lines
    # (Doubling Season 90, Embermaw Hellion 100, Soul-Scar Mage 105; measured
    # gap max 173). **CR 614.1a states no distance at all** -- *"Effects that
    # use the word 'instead' are replacement effects"* -- so the window is
    # removed rather than widened to another guessed number. Widening it to
    # 200 would be the same defect with a later expiry date.
    #
    # The `would` -> `instead` ORDER is kept, and that is the whole safety
    # margin. Measured on the unrouted population: `would ... instead`
    # unbounded claims 128 permanent + 25 spell lines, while a bare `instead`
    # (614.1a read at its widest) claims 148 permanent + **298** spell -- it
    # sweeps in every instant whose effect merely contains the word. CR 614.1a
    # describes the EFFECT; §1 says an instant/sorcery's delivery is the
    # unmarked default regardless. The template, not the bare word, is what
    # identifies a replacement ABILITY.
    #
    # `.` does not match a newline and an ability line is one line, so the
    # unbounded form cannot leave this ability.
    # ... but it MUST NOT read inside a quoted CREATED ability. §2's
    # created-ability rule (Captain-ratified 2026-08-02): an ability GRANTED to
    # another permanent belongs to the creating ability, not to this card.
    # Bewitching Leechcraft is the worked case -- `Enchanted creature has "If
    # this creature would untap during your untap step, remove a +1/+1 counter
    # from it instead."` The Aura's own delivery is `static`; the replacement
    # is the enchanted creature's. The old window missed it only by luck (the
    # gap is 61 characters, one past the cut), so removing the window exposed
    # a guard that had never been needed here. Same class as the standing trap
    # "a trigger clause must never cross into a quoted created ability".
    unq = low
    for a, b in quoted_spans(low):
        unq = unq[:a] + " " * (b - a) + unq[b:]
    # CR 614.1d states the GENERAL case that 614.1c's three templates are
    # instances of: *"Continuous effects that read '[This permanent]
    # enters . . .' … are replacement effects."* The alternation below is
    # 614.1c's three named templates, and hand-listing them lost every OTHER
    # way a card writes the same shape -- 35 lines, in three distinct ways:
    #
    #   `This creature enters PREPARED.`            24  (CR 722.3, no template)
    #   `~ enters the battlefield TAPPED.`           7  (the Gates; old wording)
    #   `~ enters UNDER THE CONTROL of an opponent.` 4  (Xantcha, Captive Audience)
    #
    # The seven Gates are the instructive ones: `\benters? tapped\b` requires
    # ADJACENCY, and the pre-2024 templating prints "enters THE BATTLEFIELD
    # tapped". Same defect class as `enters as` being tested plural-only
    # (STEP-2A §2) and as D5's guessed `{0,60}` window -- a hand-list, or a
    # hand-chosen distance, standing in for what the CR states generally.
    #
    # The SUBJECT test is `SELF_NOUN_RX`, which is DERIVED from the corpus's
    # own type lines, not a list of permanent types. 614.1d's SECOND template
    # ("[Objects] enter [the battlefield] . . .") is deliberately NOT taken
    # here -- measured, it is not decidable by this shape: of 15 candidate
    # lines only Vigorous Farming is a replacement effect, while 9 are
    # Landfall/Trap INSTANTS whose "enter" sits inside a condition (§1's
    # unmarked default) and 5 are "can't enter" PROHIBITIONS, which are
    # continuous effects but not replacement ones. Reported, not routed.
    m_self = re.match(r"^~|^" + SELF_NOUN_RX.pattern, unq)
    if m_self and re.match(r"\s+enters\b", unq[m_self.end():]):
        return ("replacement", "replacement") if "replacement" in ratified else (None, "replacement")
    if re.match(r"^as (?!an additional cost|long as)\b.{0,40}?"
                r"\b(?:enters|is turned face up)\b", unq) or \
       re.search(r"\benters? as\b", unq) or \
       re.search(r"\bwould\b.*\binstead\b|\bskips?\b|\benters? with\b|\benters? tapped\b", unq):
        return ("replacement", "replacement") if "replacement" in ratified else (None, "replacement")
    if re.search(r"^(enchant|equipped creature|enchanted )", low):
        return ("static", "static-aura") if "static" in ratified else (None, "static-aura")
    # THE ATTACHMENT VOCABULARY HAS THREE MEMBERS, NOT TWO. The branch above
    # covers Auras (CR 303.4, "enchanted <object>") and Equipment (CR 301.5a,
    # "the creature an Equipment is attached to is called the EQUIPPED
    # CREATURE") and silently omitted the third, which the CR states as an
    # explicit analogy rather than leaving to inference:
    #
    #   CR 301.6 -- "Some artifacts have the subtype 'Fortification.' A
    #   Fortification can be attached to a LAND. ... **Rules 301.5a-f apply to
    #   Fortifications in relation to lands just as they apply to Equipment in
    #   relation to creatures**."
    #
    # So 301.5a's "equipped creature" has an exact CR-stated analog, "fortified
    # land", and the classifier could not see it. Measured: 1 line (Darksteel
    # Garrison, "Fortified land has indestructible"), fully unrouted.
    #
    # n=1 is the point rather than a caveat. This is the SAME shape as the
    # self-reference card-type gap Captain caught the same day: a rule written
    # for the card types that happened to be in front of the author, where the
    # CR names another and says outright that the rule extends to it. It routes
    # to `static`, already ratified -- no new vocabulary, only scaffolding that
    # should always have been there.
    #
    # Its own descriptor, not `static-aura`: the census must keep reporting
    # what was PRINTED (§6a), and folding a Fortification into the Aura bucket
    # would hide the very distinction this fix exists to make visible.
    if re.match(r"^fortified\b", low):
        return ("static", "static-fortification") if "static" in ratified \
            else (None, "static-fortification")
    # A line that GRANTS a quoted ability to a class of permanents is a static
    # ability. CR 113.3d: static abilities "are written as statements. They're
    # simply true." §2's created-ability rule then assigns the QUOTED ability
    # to whatever it is granted to, and the grant itself to this card -- so
    # `Creatures you control have "{T}: Add one mana of any color."` (Cryptolith
    # Rite) is `static`, and the mana ability inside the quote is the creature's.
    #
    # Reached only at the TAIL, so the loyalty, activated, trigger and
    # replacement branches have all already declined the line. That ordering is
    # what makes this safe: `enters? as` is tested above, so the 57-card clone
    # family ("You may have this creature ENTER AS a copy of ...") is claimed by
    # `replacement` first and never reaches here.
    #
    # This is the FIRST piece of step 2, taken as a named shape rather than as
    # a sweep. PRE-STEP-2-AUDIT stopped the blanket version because routing
    # `spell-or-static` wholesale into `static` would turn 1,883 wrong answers
    # into answers that READ as resolved.
    # THE GRANT MUST BE THE LINE'S OWN STRUCTURE, NOT A CLAUSE INSIDE AN EFFECT.
    # `[^.]*?` forbids a sentence break before the grant, and that single
    # constraint is what separates the two:
    #
    #   Cryptolith Rite  `Creatures you control have "{T}: Add one mana ..."`
    #                    -> static. The line IS the grant.
    #   Ethereal Grasp   `Tap target creature. That creature perpetually
    #                     gains "..."`
    #                    -> an INSTANT whose effect grants. §1: a spell
    #                       ability's delivery is the unmarked default.
    #
    # Without it this branch swept in 97 instants and sorceries -- Can't Stay
    # Away, Corpsehatch, Make Mischief, Growth Spasm -- and would have UNDONE
    # two of D5's nine created-ability corrections (Brokers' Safeguard, The
    # Eighth Doctor). Eighth instance of the whole-line-vs-clause bug class in
    # this file, and the first on the static side.
    # ...and it must be CONTINUOUSLY TRUE. CR 113.3d: static abilities "are
    # written as statements. They're simply true." A DURATION or a TARGET makes
    # the grant a one-shot effect handed out by a resolving spell, not a static:
    #
    #   All Slivers have "{B}: Regenerate this permanent."      -> static
    #   Until end of turn, lands you control gain "{T}: Add ..." -> an INSTANT
    #                                    (Divergent Growth); §1, unmarked
    #   Target creature card ... perpetually gains "..."         -> a SORCERY
    #
    # Measured: without this, 65 instants and sorceries leaked in -- Showstopper,
    # Demonic Gifts, Warriors' Lesson, Shoving Match, Divergent Growth. The
    # markers are checked only on the text BEFORE the grant, so a granted
    # ability that itself says "until end of turn" inside its quote is unaffected.
    m = re.match(r"^([^.]*?)\b(?:have|has|gain|gains)\s+[\"“]", low)
    if m and not re.search(r"\buntil\b|\btarget\b|\bperpetually\b|\bthis turn\b",
                           m.group(1)):
        return ("static", "static-grant") if "static" in ratified else (None, "static-grant")
    # A line whose FIRST WORDS are "As long as" states a CONDITION under which
    # something is true, which is CR 113.3d's definition of a static ability:
    # "Static abilities are written as statements. They're simply true."
    # CR 604.2 supplies the duration -- the effect is active "as long as the
    # permanent with the ability remains on the battlefield ... OR AS LONG AS
    # THE OBJECT WITH THE ABILITY REMAINS IN THE APPROPRIATE ZONE" -- so a
    # static that functions from the graveyard (Anger, Brawn, Filth, Valor,
    # Wonder), from the library (Chittering Illuminator, Pearl Lake Warden) or
    # from the STACK (Kaervek's Torch) is still `static`. That is why this
    # branch takes no permanent-side type gate: the one instant/sorcery it
    # claims is the Torrent of Lava case STEP-2A-STATIC-GRANT §3b already ruled
    # correct, and §1's unmarked default governs a spell's RESOLUTION effect,
    # not a static that functions on the stack.
    #
    # LINE-INITIAL IS THE WHOLE CLAIM, and it is doing two jobs:
    #
    #   1. CR 611.2b -- "Some continuous effects generated by the resolution of
    #      a spell or ability have durations worded 'FOR as long as . . . .'"
    #      That is a spell's duration, NOT a static, and `^as long as` excludes
    #      it by construction. Measured: ZERO lines in the corpus open with
    #      "for as long as", so the exclusion costs nothing and the shape it
    #      guards against is real (Master Thief is CR 611.2b's own example).
    #   2. Mid-line "as long as" is a condition attached to something else's
    #      effect, and that something else owns the delivery. Reaching this
    #      branch only at the TAIL is the other half: loyalty, activated, every
    #      trigger family and replacement have all already declined the line.
    #
    # Measured on the unrouted population before the change: 400 lines, and
    # reading all 400 individually found ZERO leakage -- no trigger word, no
    # activation cost, no CR 614.1a-c template outside a quoted created ability.
    # Two shapes were checked against ratified law before being kept:
    #   * 7 lines create a PREVENTION effect (Thunderstaff, Spirit of
    #     Resistance, Camel). CR 615.1 makes prevention a category PARALLEL to
    #     replacement -- "Like replacement effects (see rule 614)" -- and §2's
    #     `replacement` row is anchored to 614.1a-c only, so §2e (a static that
    #     GENERATES a replacement effect takes `replacement`) does not reach
    #     them. Armament of Nyx already carries a prevention effect on ratified
    #     `static` via the aura branch, so this is consistent with practice.
    #   * Cloud, Midgar Mercenary ("that ability triggers an additional time")
    #     is CR 603.2d, filed under triggered abilities, not under 614.
    if re.match(r"^as long as\b", low):
        return ("static", "static-condition") if "static" in ratified else (None, "static-condition")
    # A line-initial SELF-REFERENCE statement, on a card that cannot carry a
    # spell ability, is a static ability.
    #
    # CR 113.3 enumerates FOUR ability categories, and CR 113.3a seals the one
    # that would otherwise compete: *"Spell abilities are abilities that are
    # followed as instructions **while an instant or sorcery spell is
    # resolving**."* So a spell ability can exist ONLY on an instant or sorcery.
    # At the tail, loyalty (113.3b/606), activated (113.3b), every triggered
    # family (113.3c) and replacement (614) have already declined the line --
    # and if the card has no instant/sorcery FACE, 113.3a is unavailable too.
    # The enumeration is closed, so `static` (113.3d) is what remains. This is
    # a derivation from the CR's own category list, not a verb list.
    #
    # THE FACE TEST IS THE WHOLE SAFETY MARGIN, and it was not the first
    # boundary tried. Measured on the unrouted population, 2,185 lines open
    # with a self-reference -- and 738 of them are burn spells:
    #
    #   Chain of Plasma   `~ deals 3 damage to any target.`   <- CR 113.3a,
    #                                                            unmarked (§1)
    #   Marang River Prowler `This creature can't block and can't be blocked.`
    #                                                         <- CR 113.3d
    #
    # Both open with a self-reference; no test on the SUBJECT separates them.
    # The CR 113.3a cut does, exactly: after it, **ZERO** `deals` lines remain
    # on the routable side (measured, all 91 surviving verb heads are state
    # predicates -- can't / can / gets / has / is / doesn't / must / 's power).
    # 760 lines on cards WITH an instant or sorcery face are left reported
    # rather than routed, because attributing a line to a FACE is a different
    # job than attributing it to a card, and `ability_lines` joins all faces.
    #
    # `escapes with` (12 lines, Phoenix of Ash) is HELD OUT deliberately. CR
    # 113.6h -- *"An object's ability that modifies how that particular object
    # enters the battlefield … **See rule 614.12**"* -- chains it into the
    # replacement section, so its home is probably `replacement`, not `static`.
    # That is a second shape and it gets its own pass; sweeping it in here
    # would be the lumping this method exists to avoid.
    m_self = re.match(r"^~|^" + SELF_NOUN_RX.pattern, low)
    if m_self and card is not None and not _has_spell_face(card) and \
       not re.match(r"\s+escapes\b", low[m_self.end():]):
        return ("static", "static-self-statement") if "static" in ratified \
            else (None, "static-self-statement")
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
        for line, parsed in deliveries_for_lines(card, ratified):
            if action_forms is not None:
                form, pos = find_action(line, action_forms)
                if form is None:
                    continue
            else:
                form = None
            for tok, desc in parsed:
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
        for line, line_parsed in deliveries_for_lines(card, ratified):
            parsed = None
            for term, meta in actions.items():
                form, _ = find_action(line, meta["forms"])
                if form is None:
                    continue
                if parsed is None:
                    parsed = line_parsed
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
