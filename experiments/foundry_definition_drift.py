#!/usr/bin/env python3
"""Definition/name/member contradiction audit -- DET, read-only, zero tokens.

No existing gate reads the `definition` field at all (foundry_family_sweep.py
never touches it), so an axis whose ratified NAME and ratified DEFINITION
disagree, or whose MEMBERS contradict both, passes every check in the system.
The CDR-09 walk surfaced one live instance by accident:
`rule:draw-second-card-trigger-plus1-counter` carries a counter name, a
definition asserting a creature TOKEN, and 4 members that split two ways on
delivery and two ways on payoff. This audit looks for the rest of that class.

Checks, each anchored to a ratified law:

  C1  counter/token confusion -- grammar §8 rule 3, quoting CR 122.1 verbatim:
      "a counter is not a token and a token is not a counter". An axis naming
      one whose definition or member evidence names the OTHER is a defect.
  C2  delivery mismatch -- the slug's DELIVERY prefix (grammar §1/§2, closed
      vocabulary) against what the card actually says. A `death-trigger-` axis
      whose member never dies is misfiled.

Precision discipline (the 2026-08-02 lesson): a checker that encodes one law
reports every slug governed by a DIFFERENT ratified law as a defect. The
ratified exemptions are encoded below WITH their citations, and every member
test is double-gated -- the evidence quote AND the card's full oracle text
(all faces, all paragraphs) must both lack the expected concept before
anything is reported.

Usage:
  python3 experiments/foundry_definition_drift.py            # with card names
  python3 experiments/foundry_definition_drift.py --no-corpus # slugs only, fast
"""
import sys
import re
import json
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402
import foundry_codebook as fcb  # noqa: E402

REPORT_MD = REPO_ROOT.parent / "docs" / "DEFINITION-DRIFT-AUDIT-2026-08-02.md"
REPORT_JSON = fc.FOUNDRY_OUT_DIR / "definition_drift_report.json"

# --- Ratified exemptions ------------------------------------------------------
# Idiomatic job-names, EXEMPT as leaves: "jobs are parent/display vocabulary;
# grammar governs mechanism slugs" (CODEBOOK-NAMING-GRAMMAR.md §12, plus the
# 7 further exemptions ratified at Q6, walk-ratification 2026-07-31).
IDIOMATIC_LEAVES = {
    "rule:compensates-controller-with-token", "rule:cheat-creature-into-play",
    "rule:rhystic-tax", "rule:the-ring-tempts-you",
    "rule:burst-draw", "rule:cantrip", "rule:modal", "rule:drain-life",
    "rule:combat-trick-pump-own-creature", "rule:tribal-anthem-buff",
    "rule:alternate-win-condition",
}

COUNTER_RE = re.compile(r"\bcounters?\b", re.I)
TOKEN_RE = re.compile(r"\btokens?\b", re.I)
# The VERB sense of "counter" is not a marker -- an axis that counters spells
# must not be read as naming a CR 122.1 counter (grammar §8a).
COUNTER_VERB_RE = re.compile(
    r"\bcounters?\s+(?:(?:a|an|the|that|this|target|any|each|all|it)\s+)*"
    r"(?:[a-z-]+\s+){0,2}?(?:spell|ability|abilities)\b|\bcounter(?:ed|ing)\b", re.I)

# --- C2: DELIVERY prefix -> what the card must actually say -------------------
# Only prefixes whose oracle phrasing is unambiguous. `activated-` is omitted
# deliberately: an activation cost has no single reliable phrase.
DELIVERY_EXPECT = [
    ("leaves-battlefield-trigger-", re.compile(r"leaves the battlefield", re.I),
     "'leaves the battlefield'"),
    ("draw-second-card-trigger-", re.compile(r"draws? (?:your|their) second card", re.I),
     "'draw(s) your/their second card'"),
    ("combat-damage-to-player-", re.compile(r"combat damage to an? (?:player|opponent)", re.I),
     "'combat damage to a player'"),
    ("combat-damage-to-creature-", re.compile(r"combat damage to an? creature", re.I),
     "'combat damage to a creature'"),
    # Inflection matters: a plural subject takes the bare stem ("whenever one or
    # more creatures you control DIE", "creatures you control ENTER as a copy").
    # Matching only the -s form reports those as misfiles. They are not.
    ("death-trigger-", re.compile(r"\bdies?\b|put into a graveyard", re.I),
     "'dies'/'die' / 'put into a graveyard'"),
    ("attack-trigger-", re.compile(r"\battack(?:s|ing|ed)?\b", re.I), "'attacks'"),
    ("landfall-", re.compile(r"land enters|\blandfall\b", re.I), "'land enters' / 'landfall'"),
    ("upkeep-", re.compile(r"\bupkeep\b", re.I), "'upkeep'"),
    # Entering the battlefield has several ratified phrasings -- a card
    # RETURNED or PUT onto the battlefield enters it (CR 400.7 / 614 class).
    ("etb-", re.compile(r"\benters?\b|\bentering\b|puts?\b[^.;]{0,30}onto the battlefield|"
                        r"returns?\b[^.;]{0,60}to the battlefield|\bmanifest", re.I),
     "'enters' / 'put onto the battlefield' / 'return … to the battlefield'"),
    ("cast-trigger-", re.compile(r"\bcasts?\b|\bcasting\b", re.I), "'cast'"),
]


# --- C3: EFFECT token -> what the card must actually say ----------------------
# The slug's effect suffix is a claim about what the member DOES. Captain
# 2026-08-02, on Keen Sense sitting under `-discard` while its text reads "you
# may draw a card": delivery being right does not make the effect right, and no
# check was testing the effect at all.
#
# Deliberately biased toward FALSE NEGATIVES: a member passes if the phrase
# appears anywhere in its quote or full oracle text, even in reminder or cost
# text. An audit awaiting ratification must not cry wolf.
EFFECT_EXPECT = [
    ("loot", re.compile(r"\bdiscards?\b", re.I), "a discard (looting is draw-THEN-discard)"),
    ("discard", re.compile(r"\bdiscards?\b", re.I), "'discard'"),
    ("surveil", re.compile(r"\bsurveils?\b", re.I), "'surveil'"),
    ("scry", re.compile(r"\bscrys?\b|\bscries\b", re.I), "'scry'"),
    ("mill", re.compile(r"\bmills?\b", re.I), "'mill'"),
    ("regenerate", re.compile(r"\bregenerates?\b", re.I), "'regenerate'"),
    ("fight", re.compile(r"\bfights?\b", re.I), "'fight'"),
    ("destroy", re.compile(r"\bdestroys?\b|\bdestroying\b", re.I), "'destroy'"),
    ("exile", re.compile(r"\bexil(?:e|es|ed|ing)\b", re.I), "'exile'"),
    ("sacrifice", re.compile(r"\bsacrific(?:e|es|ed|ing)\b", re.I), "'sacrifice'"),
    ("bounce", re.compile(r"returns?\b[^.;]{0,90}(?:owner|hand)", re.I),
     "'return … to its owner's hand'"),
    ("unblockable", re.compile(r"can'?t be blocked", re.I), "\"can't be blocked\""),
    ("lifegain", re.compile(r"gains?\b[^.;]{0,30}\blife\b", re.I), "'gain … life'"),
    ("draw", re.compile(r"\bdraws?\b", re.I), "'draw'"),
]


# --- C4 vocabulary: templating words hardcoded to the mechanic they name -----
# Captain-ratified 2026-08-02. Each row is (token-in-slug, what the card must
# print, human phrasing, law citation, finding id). These are CR terms of art,
# not English: "target" is CR 115.1/601.2c, "another" excludes the source, and
# "you control" is an ownership restriction on the affected object.
OWN_CONTROL = re.compile(r"\byou control\b|\byour creatures?\b", re.I)

C4_CLAIMS = [
    (re.compile(r"(?<![a-z])target(?![a-z])"),
     re.compile(r"\btargets?\b", re.I),
     "targeting ('target' in the slug)",
     "grammar §6 + CR 601.2c — 'target' appears in a slug ONLY when the word "
     "'target' appears in the ability (the b7 Unwind ruling)",
     "C4a"),
    (re.compile(r"(?<![a-z])(another|other)(?![a-z])"),
     re.compile(r"\banother\b|\bother\b", re.I),
     "exclusion of the source ('another'/'other' in the slug)",
     "grammar §5/§6 — 'another' excludes the source; a slug may not claim it of "
     "a card whose printed text can affect itself",
     "C4c"),
]


def strip_reminder(text: str) -> str:
    """Reminder text is not the card's own claim.

    Tier-4 §S4: a token-definition parenthetical states what the TOKEN does,
    and grammar §2's created-ability rule says that is not the card's ability.
    Matching inside it is how 44 DET memberships were written off token text.
    """
    return re.sub(r"\([^)]*\)", "", text or "")


def slug_body(slug: str) -> str:
    return slug.split(":", 1)[-1]


def names_counter(slug: str) -> bool:
    return any(t in ("counter", "counters") for t in slug_body(slug).split("-"))


def names_token(slug: str) -> bool:
    return any(t in ("token", "tokens") for t in slug_body(slug).split("-"))


def mentions_counter_noun(text: str) -> bool:
    """A counter MARKER mention -- verb-sense `counters a spell` doesn't count."""
    if not COUNTER_RE.search(text):
        return False
    stripped = COUNTER_VERB_RE.sub(" ", text)
    return bool(COUNTER_RE.search(stripped))


def member_texts(member: dict, cards: dict) -> tuple:
    """(evidence_quote, full_oracle_text). Full text is all faces, all
    paragraphs, per the house all-faces scanning rule."""
    quotes = " ".join(a.get("quote", "") or "" for a in member.get("assertions", []))
    card = (cards or {}).get(member["oracle_id"])
    full = fc.full_oracle_text(card) if card else ""
    return quotes, full


def card_label(oracle_id: str, cards: dict) -> str:
    c = (cards or {}).get(oracle_id)
    return (c.get("name") if c else None) or oracle_id


def audit(cb: dict, cards: dict) -> list:
    findings = []
    for slug, entry in sorted(cb["axes"].items()):
        if entry.get("status") != "active" or slug in IDIOMATIC_LEAVES:
            continue
        definition = entry.get("definition", "") or ""
        has_counter, has_token = names_counter(slug), names_token(slug)

        # --- C1: counter/token confusion (§8 rule 3) -------------------------
        # An axis naming BOTH legitimately spans both (e.g. a token that enters
        # with counters) -- §7 ratifies create-token-with-x-counters. Skip it.
        if has_counter != has_token:
            wants_counter = has_counter
            label = "counter" if wants_counter else "token"
            other = "token" if wants_counter else "counter"

            def has_wanted(t):
                return mentions_counter_noun(t) if wants_counter else bool(TOKEN_RE.search(t))

            def has_other(t):
                return bool(TOKEN_RE.search(t)) if wants_counter else mentions_counter_noun(t)

            # C1a -- the axis's own definition contradicts its ratified name.
            if definition and has_other(definition) and not has_wanted(definition):
                findings.append({
                    "check": "C1a", "severity": "BLOCKING", "slug": slug,
                    "law": "grammar §8 rule 3 (CR 122.1 verbatim): a counter is not a token",
                    "what": f"slug names a {label}; its definition names a {other} and never a {label}",
                    "definition": definition,
                    "fix": f"definition is stale or the name is wrong — reconcile against the members, "
                           f"then correct the DEFINITION (the name is ratified) or ratify a rename",
                })

            # C1b -- member evidence contradicts the ratified name. Double-gated:
            # the cited quote AND the card's full oracle text must both lack it.
            bad = []
            for m in entry.get("members", []):
                quote, full = member_texts(m, cards)
                if not quote.strip():
                    continue  # no quote cited -- nothing to contradict
                if has_other(quote) and not has_wanted(quote) and not has_wanted(full or quote):
                    bad.append({"oracle_id": m["oracle_id"],
                                "card": card_label(m["oracle_id"], cards),
                                "quote": quote.strip()})
            if bad:
                findings.append({
                    "check": "C1b", "severity": "BLOCKING", "slug": slug,
                    "law": "grammar §8 rule 3 (CR 122.1 verbatim): a counter is not a token",
                    "what": f"slug names a {label}; {len(bad)} of {len(entry.get('members', []))} "
                            f"members are evidenced by a {other} and carry no {label} anywhere in "
                            f"their oracle text",
                    "members": bad,
                    "fix": f"these members do not belong on a {label} axis — split them to the "
                           f"{other} sibling, or if the majority is {other}, the axis is misnamed",
                })

        # --- C2: delivery mismatch (grammar §1/§2 closed DELIVERY vocab) -----
        body = slug_body(slug)
        for prefix, expect_re, human in DELIVERY_EXPECT:
            if not body.startswith(prefix):
                continue
            bad = []
            for m in entry.get("members", []):
                quote, full = member_texts(m, cards)
                if not quote.strip():
                    continue
                if not expect_re.search(quote) and not expect_re.search(full or quote):
                    bad.append({"oracle_id": m["oracle_id"],
                                "card": card_label(m["oracle_id"], cards),
                                "quote": quote.strip()})
            if bad:
                findings.append({
                    "check": "C2", "severity": "BLOCKING", "slug": slug,
                    "law": "grammar §1/§2 — DELIVERY is closed vocabulary",
                    "what": f"slug's delivery is {prefix.rstrip('-')!r}, so members must say {human}; "
                            f"{len(bad)} of {len(entry.get('members', []))} never do, in the cited "
                            f"quote or anywhere in their oracle text",
                    "members": bad,
                    "fix": f"re-home these members onto the axis matching their real delivery "
                           f"(or ratify a new sibling if none exists)",
                })
            break  # longest-prefix-wins; one delivery per slug

        # --- C3: effect mismatch (grammar §4 EFFECT verbs) -------------------
        # Strip the DELIVERY prefix first: `draw` in `draw-second-card-trigger-`
        # names WHEN the ability triggers, not what it does. Reading it as an
        # effect claim accuses every member of failing to draw.
        effect_body = body
        for _pre, _re, _h in DELIVERY_EXPECT:
            if effect_body.startswith(_pre):
                effect_body = effect_body[len(_pre):]
                break
        parts = set(effect_body.split("-"))
        for tok, expect_re, human in EFFECT_EXPECT:
            if tok not in parts:
                continue
            bad = []
            for m in entry.get("members", []):
                quote, full = member_texts(m, cards)
                if not quote.strip():
                    continue
                if not expect_re.search(quote) and not expect_re.search(full or quote):
                    bad.append({"oracle_id": m["oracle_id"],
                                "card": card_label(m["oracle_id"], cards),
                                "quote": quote.strip()})
            if bad:
                findings.append({
                    "check": "C3", "severity": "BLOCKING", "slug": slug,
                    "law": "grammar §4 — EFFECT verbs are standardized; the suffix is a "
                           "claim about what the member DOES",
                    "what": f"slug's effect is {tok!r}, so members must show {human}; "
                            f"{len(bad)} of {len(entry.get('members', []))} never do, in the "
                            f"cited quote or anywhere in their oracle text",
                    "members": bad,
                    "fix": f"these members do not perform {tok!r} — re-home onto the axis "
                           f"matching their real effect, or ratify a sibling",
                })
            break  # one effect claim per slug, most specific first

        # --- C4: the printed word is the claim ------------------------------
        # Captain-ratified 2026-08-02: "game logic is game logic. it can not be
        # partially assumed or opened for interpretation. if something targets
        # it targets. if it does not target, it does not target." Templating
        # words are chosen deliberately by the CR and are hardcoded here as
        # mechanics, not read as prose.
        #
        # Reminder text is EXCLUDED from the card's own claim (tier-4 §S4:
        # a token's printed text is the TOKEN's ability, not the card's).
        for tok_re, need_re, human, law, sub in C4_CLAIMS:
            if not tok_re.search(body):
                continue
            bad = []
            for m in entry.get("members", []):
                quote, full = member_texts(m, cards)
                if not quote.strip():
                    continue          # unevidenced: NO QUOTE owns that, not C4
                hay = quote + " " + strip_reminder(full or "")
                if not need_re.search(hay):
                    bad.append({"oracle_id": m["oracle_id"],
                                "card": card_label(m["oracle_id"], cards),
                                "quote": quote.strip()})
            if bad:
                findings.append({
                    "check": sub, "severity": "BLOCKING", "slug": slug,
                    "law": law,
                    "what": f"slug claims {human}; {len(bad)} of "
                            f"{len(entry.get('members', []))} member(s) never say so in "
                            f"the cited quote or in printed oracle text "
                            f"(reminder text excluded)",
                    "members": bad,
                    "fix": "the printed word is the claim — re-home these members, or "
                           "correct the slug so it stops asserting what they do not do",
                })

        # C4b: the scope FIELD contradicts the members' printed ownership.
        scope = (entry.get("scope") or "")
        if scope.startswith("any"):
            bad = []
            for m in entry.get("members", []):
                quote, _full = member_texts(m, cards)
                if quote.strip() and OWN_CONTROL.search(quote):
                    bad.append({"oracle_id": m["oracle_id"],
                                "card": card_label(m["oracle_id"], cards),
                                "quote": quote.strip()})
            if bad:
                findings.append({
                    "check": "C4b", "severity": "BLOCKING", "slug": slug,
                    "law": "grammar §6 — ownership is AXIS IDENTITY, not a facet "
                           "(Captain-ratified 2026-08-02; explicit partial reversal of "
                           "batch-6 D3, which had logged ownership as a schema-pass facet)",
                    "what": f"scope is {scope!r} — an any-ownership claim — but "
                            f"{len(bad)} of {len(entry.get('members', []))} member(s) are "
                            f"printed 'you control' and cannot affect an opponent's",
                    "members": bad,
                    "fix": "split the own-restricted members onto an -own- sibling, or "
                           "correct the scope; 'any' must mean any",
                })

        # C4d: the scope field contradicts the slug's own name.
        if scope.startswith("any") and re.search(r"you-control|own-", body):
            findings.append({
                "check": "C4d", "severity": "BLOCKING", "slug": slug,
                "law": "grammar §6 — a slug and its scope field may not make "
                       "opposite ownership claims",
                "what": f"slug name asserts controller-restricted ownership while the "
                        f"scope field says {scope!r}",
                "members": [],
                "fix": "correct the scope field to match the ratified name",
            })
    return findings


def write_markdown(findings: list, n_active: int, corpus_note: str) -> None:
    by_check = {}
    for f in findings:
        by_check.setdefault(f["check"], []).append(f)
    lines = [
        "# Definition/name/member contradiction audit — 2026-08-02",
        "",
        "**DET, read-only, zero tokens.** Generated by",
        "`experiments/foundry_definition_drift.py`. Nothing here is a ruling;",
        "every row is a proposed resolution awaiting Captain ratification.",
        "",
        "## Why this audit exists",
        "",
        "No gate in the system reads the `definition` field —",
        "`foundry_family_sweep.py` never touches it. An axis whose ratified NAME",
        "and ratified DEFINITION disagree, or whose MEMBERS contradict both,",
        "passes every existing check. The CDR-09 walk surfaced one instance by",
        "accident; this is the systematic pass for the rest.",
        "",
        f"Scope: {n_active} active axes. {corpus_note}",
        "",
        f"**{len(findings)} findings.**",
        "",
        "| check | law | count |",
        "|---|---|--:|",
        "| C1a | §8 rule 3 — definition contradicts the name | "
        f"{len(by_check.get('C1a', []))} |",
        "| C1b | §8 rule 3 — member evidence contradicts the name | "
        f"{len(by_check.get('C1b', []))} |",
        "| C2 | §1/§2 — member delivery contradicts the slug prefix | "
        f"{len(by_check.get('C2', []))} |",
        "| C3 | §4 — member effect contradicts the slug suffix | "
        f"{len(by_check.get('C3', []))} |",
        "",
        "Member tests are **double-gated**: a member is only reported when the",
        "cited evidence quote *and* the card's full oracle text (all faces, all",
        "paragraphs) both lack the expected concept. Members with no cited quote",
        "are skipped, not guessed at.",
        "",
        "Ratified exemptions encoded: the 11 idiomatic leaves (§12 + Q6), and",
        "axes naming both a counter and a token, which §7 ratifies as legitimate",
        "(`create-token-with-x-counters`).",
        "",
    ]

    # Rollup by delivery prefix -- where the drift actually concentrates.
    roll = {}
    for f in findings:
        if f["check"] != "C2":
            continue
        body = f["slug"].split(":", 1)[-1]
        pre = next((p for p, _, _ in DELIVERY_EXPECT if body.startswith(p)), "?")
        a, m = roll.get(pre, (0, 0))
        roll[pre] = (a + 1, m + len(f.get("members", [])))
    if roll:
        total_m = sum(m for _, m in roll.values())
        lines += [
            "## Where the drift concentrates",
            "",
            f"{total_m} misfiled member assignments across {sum(a for a, _ in roll.values())} axes:",
            "",
            "| delivery prefix | axes | misfiled members |",
            "|---|--:|--:|",
        ]
        for pre, (a, m) in sorted(roll.items(), key=lambda kv: -kv[1][1]):
            lines.append(f"| `{pre}` | {a} | {m} |")
        top = max(roll.items(), key=lambda kv: kv[1][1])
        lines += [
            "",
            f"**`{top[0]}` accounts for {top[1][1]} of {total_m}.** The pattern is one-way: "
            "planeswalker loyalty abilities, Saga chapters, Room unlock triggers, "
            "instants/sorceries with no permanent to enter, activated abilities, "
            "megamorph turn-face-up, and even *leaves*-the-battlefield triggers have all "
            "been absorbed onto ETB axes. The reverse — a genuine ETB filed elsewhere — "
            "appears once (`upkeep-surveil`). That asymmetry suggests ETB is functioning "
            "as a default home when delivery is unclear, rather than a claim about "
            "delivery.",
            "",
        ]
    for check in ("C1a", "C1b", "C2", "C3"):
        rows = by_check.get(check, [])
        if not rows:
            continue
        lines += [f"## {check} — {rows[0]['law']}", ""]
        for f in rows:
            lines += [f"### `{f['slug']}`", "", f"**{f['what']}**", ""]
            if f.get("definition"):
                lines += [f"> definition: {f['definition']}", ""]
            for m in f.get("members", []):
                lines.append(f"- **{m['card']}** — \"{m['quote']}\"")
            if f.get("members"):
                lines.append("")
            lines += [f"*Proposed:* {f['fix']}", ""]
    REPORT_MD.write_text("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-corpus", action="store_true",
                    help="skip corpus load: no card names, quote-only gating")
    args = ap.parse_args()

    cb = fcb.load_codebook()
    fcb.lint_or_halt(cb, "codebook")
    n_active = sum(1 for e in cb["axes"].values() if e.get("status") == "active")

    cards = {}
    if args.no_corpus:
        note = "Corpus NOT loaded (--no-corpus): card names unresolved and " \
               "member tests gated on the cited quote only."
    else:
        cards, _ = fc.load_corpus()
        note = f"Corpus loaded ({len(cards)} cards) for card names and full-oracle-text gating."
    print(note)

    findings = audit(cb, cards)
    REPORT_JSON.write_text(json.dumps({"findings": findings}, indent=2, sort_keys=True) + "\n")
    write_markdown(findings, n_active, note)

    counts = {}
    for f in findings:
        counts[f["check"]] = counts.get(f["check"], 0) + 1
    print(f"\n{len(findings)} findings across {n_active} active axes")
    for k in sorted(counts):
        print(f"  {k}: {counts[k]}")
    print(f"\nwrote {REPORT_MD}")
    print(f"wrote {REPORT_JSON}")


if __name__ == "__main__":
    main()
