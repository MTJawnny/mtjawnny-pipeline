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


def trigger_clause(low: str) -> str:
    """The condition half of a triggered ability -- everything up to the comma
    that ends it. Whose permanent the trigger watches is decided HERE; reading
    the effect half too is how 'Parley — Whenever this creature attacks, each
    player reveals…' gets misread as an other-creature trigger, because `each`
    appears in the effect."""
    depth = 0
    for i, ch in enumerate(low):
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        elif ch == "," and depth == 0:
            return low[:i]
    return low


def parse_deliveries(line: str, ratified: dict, card: dict = None) -> list:
    """One ability line can carry SEVERAL deliveries -- "Whenever ~ enters or
    attacks", "When ~ enters and at the beginning of your upkeep". Grammar §1's
    multi-axis rule means each earns its membership, so returning only the
    first would silently under-tag the compound-trigger population.

    Splits the trigger clause on `or`/`and` and re-classifies each alternative
    against the same subject. Returns a de-duplicated list of (token, descriptor).
    """
    raw = line.strip()
    body = ABILITY_WORD.sub("", raw)
    if card is not None:
        body = fc.canonicalize_self_reference(body, card)
    low = body.lower()

    if not re.match(r"^(when|whenever|at )", low):
        return [parse_delivery(line, ratified, card)]

    clause = trigger_clause(low)
    rest = low[len(clause):]
    parts = re.split(r"\s+(?:or|and)\s+", clause)
    # Only a part that is itself a trigger PREDICATE is a second delivery.
    # "whenever you cast an instant or sorcery spell" splits on an `or` inside
    # the OBJECT phrase -- "sorcery spell" is not an event, and treating it as
    # one loses a real cast-trigger. Same for "a spell or ability".
    PREDICATE = re.compile(
        r"^(?:at\b|when(?:ever)?\b|~\b|this \w+|"
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
            if re.search(r"\bupkeep\b", clause):
                return mark("upkeep-trigger", "upkeep")
            if re.search(r"\bend step\b", clause):
                return mark("end-step-trigger", "end-step")
            if re.search(r"\bcombat\b", clause):
                return None, "begin-combat"
            if re.search(r"\bdraw step\b", clause):
                return None, "draw-step"

        if re.search(r"\bland (you control )?enters\b", low) or low.startswith("landfall"):
            return mark("landfall", "landfall")
        if re.search(r"\benters\b", low):
            return msub("etb", "enters")
        if re.search(r"\bdies\b|\bdie\b", low):
            if re.search(r"\bfrom (your |a )?(library|hand|anywhere)\b", low):
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
            return None, "to-graveyard-from-anywhere"
        if re.search(r"\bleaves? the battlefield\b|\bleave the battlefield\b", low):
            return msub("leaves-battlefield-trigger", "ltb")
        if re.search(r"\battacks?\b", low):
            if re.search(r"\battacks? you\b|\battacks? a planeswalker\b", low):
                return None, "is-attacked"
            if re.search(r"^when(ever)? you attack\b", low):
                return None, "player-attacks"
            return msub("attack-trigger", "attacks")
        if re.search(r"\bcasts?\b", low):
            return mark("cast-trigger", "casts")
        if re.search(r"combat damage to (a|target)?\s*(player|opponent)", low):
            return msub("combat-damage-to-player", "combat-damage-player")
        if re.search(r"combat damage to (a|target)?\s*creature", low):
            return mark("combat-damage-to-creature", "combat-damage-creature")
        if re.search(r"\bis dealt\b.{0,30}\bdamage\b", low):
            return None, "damage-received"
        if re.search(r"\bdeals? damage to\b.{0,24}\bplayer\b", low):
            return mark("any-damage-to-player", "any-damage-player")
        if re.search(r"\bdeals? damage to\b", low):
            return mark("any-damage-to-creature", "any-damage-creature")
        if re.search(r"\bupkeep\b", clause):
            return mark("upkeep-trigger", "upkeep")
        if re.search(r"\bend step\b", clause):
            return mark("end-step-trigger", "end-step")
        if re.search(r"beginning of (each |your )?combat", clause):
            return None, "begin-combat"
        if re.search(r"\bdraw step\b", clause):
            return None, "draw-step"
        if re.search(r"\bbecomes the target of\b", low):
            return mark("becomes-targeted-trigger", "becomes-targeted")
        if re.search(r"\bblocks\b|\bbecomes blocked\b", low):
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
        if re.search(r"\bis turned face up\b|\bturned face up\b", low):
            return None, "turned-face-up"
        if re.search(r"\bdiscards?\b", low):
            return None, "discard-trigger"
        if re.search(r"counters? (are|is) put on", low):
            return None, "counter-placed"
        if re.search(r"\bgains? life\b|\bgained\b", low):
            return None, "lifegain-trigger"
        if re.search(r"\bsacrifices?\b", low):
            return None, "sacrifice-trigger"
        return None, "unclassified-trigger"

    if re.search(r"\bwould\b.{0,60}\binstead\b|\bskips?\b|\benters? with\b|\benters? tapped\b", low):
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
