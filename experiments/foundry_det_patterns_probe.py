#!/usr/bin/env python3
"""Corpus hit-count probe for the CORPUS-PASS-PLAN.md step-3 walk's DET-able
axis proposals. Every pattern below is a PROPOSAL for Captain ratification
(CORPUS-PASS-PLAN.md sec.1: "Each candidate DET pattern is proposed with a
measured corpus hit-list, sampled and RATIFIED by Captain like a scoring
constant"). This script only measures; it never writes to codebook.json.

All-paragraph, all-faces scanning (house style, MASTER-HANDOFF sec.6) via
foundry_common.full_oracle_text() + re.search across the WHOLE joined text
(not per-line), on the Gate #0-filtered corpus (foundry_common.load_corpus_gated()).

Usage: python3 experiments/foundry_det_patterns_probe.py
"""
import sys
import re
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402

OUT_PATH = fc.FOUNDRY_OUT_DIR / "det_patterns_probe.json"

# Q8.2/Q8.8 (walk-ratification 2026-07-31): shared restriction-continuation
# exclusion for every "absolute unblockable" pattern in the family below. A
# duration phrase ("this turn" / "until end of turn") is explicitly NOT a
# restriction and is allowed to intervene before the check.
RESTRICTION_GUARD = r"(?!(?:\s+this turn)?(?:\s+until end of turn)?\s*,?\s*(?:except by|by creatures with|unless|as long as))"

# (slug, pattern_description, compiled-regex-source, current codebook n_members)
# n_members filled in at runtime from codebook.json; kept here as a comment
# reference for the humans reading this file. pattern_src=None marks a
# withdrawn pattern (Q9 kicker kill) -- measured as withdrawn, not run.
PATTERNS = [
    ("rule:activation-restricted-during-combat", r"activate\w* (?:this ability )?only during combat", "activation-restriction family (D-4 closed, DET-owned)"),
    ("rule:activation-restricted-only-during-your-turn", r"activate\w* (?:this ability )?only during your (?:turn|next turn)", "activation-restriction family"),
    ("rule:activation-restricted-to-own-upkeep", r"activate\w* (?:this ability )?only during your upkeep", "activation-restriction family"),
    ("rule:activation-restricted-to-sorcery-speed", r"activate\w* (?:this ability )?only as a sorcery", "activation-restriction family"),
    ("rule:created-token-enters-tapped",
     r"create[^.]*\btapped\b[^.]*token|create[^.]*token[^.]*\benters?(?: the battlefield)? tapped\b",
     "'create a tapped ... token' (adjective-before-noun, the dominant print form) OR 'create ... token. It enters tapped' (verified against 5 live members -- all use the adjective form, e.g. Koilos Roc 'create a tapped Powerstone token')"),
    ("rule:enters-tapped (unconditional)", r"\benters?(?: the battlefield)? tapped\b(?!,? (?:unless|if))", "broad pre-filter; conditional variant subtracted separately below"),
    ("rule:enters-tapped-conditional", r"\benters?(?: the battlefield)? tapped\b,? (?:unless|if)|unless [^.]*,? [^.]*enters? tapped|if [^.]* enters? tapped", "both-polarity: 'tapped unless/if' AND the reversed 'unless X, ~ enters tapped' shape (Lesson 1)"),
    ("rule:etb-tap-and-stun-target", r"enters[^.]*\btap[^.]*stun counter|\btap[^.]*stun counter[^.]*enters", "ETB clause containing both 'tap' and 'stun counter'"),
    ("rule:forced-attack-each-combat", r"\bthis creature attacks each (?:combat|turn) if able\b", "CR 508.1a fixed phrase, self-scoped"),
    ("rule:forces-all-creatures-attack", r"(?:all|each) creatures? [^.]*attacks? each combat if able", "CR 508.1a fixed phrase, all-creatures scoped"),
    ("rule:grants-additional-combat-phase", r"an additional combat phase|another combat phase|extra combat phase", "fixed phrase"),
    ("rule:grants-cascade-to-own-spells", r"spells you cast have cascade|have cascade[^.]*you cast", "fixed phrase, granted (not printed) cascade"),
    ("rule:grants-controller-hexproof", r"you have hexproof|you gain hexproof", "player-hexproof grant, distinct from permanent-hexproof"),
    ("rule:grants-creature-type", r"in addition to (?:its|their|his or her) other (?:creature )?types", "fixed CR type-addition phrase"),
    ("rule:grants-double-strike-target", r"target creature gains double strike|gains double strike until end of turn", "fixed phrase"),
    ("rule:grants-extra-land-drop", r"an additional land|play (?:an additional|two|three) lands?|additional lands? this turn", "fixed phrase"),
    ("rule:grants-extra-turn", r"takes? an (?:extra|additional) turn", "fixed phrase"),
    ("rule:grants-flashback-to-graveyard-card", r"gains? flashback\b", "granted (not printed) flashback -- excludes cards with printed Flashback keyword"),
    ("rule:grants-flying-and-pump-to-creature", r"gets? \+(?:\d+|[Xx])/\+(?:\d+|[Xx]) and gains flying|gains flying and gets \+(?:\d+|[Xx])/\+(?:\d+|[Xx])", "fixed phrase, both grants same clause (F2 sweep: pump amount may be X, not just a literal digit)"),
    ("rule:grants-haste-to-created-tokens", r"(?:that|those|token)[^.]*(?:has|have|gains?) haste", "haste grant scoped to token(s) just created"),
    ("rule:grants-haste-to-your-creatures", r"creatures you control have haste", "fixed phrase, board-wide static"),
    ("rule:grants-trample-to-creatures-with-counters", r"creatures? (?:you control )?with (?:a |one or more )?\+1/\+1 counters? on (?:it|them|it have|them have)[^.]*trample|trample[^.]*with a \+1/\+1 counter", "conditional-scope trample grant"),
    ("rule:grants-trample-to-other-creatures", r"other creatures you control have trample", "fixed phrase"),
    # Q8.8 DET rebuild (walk-ratification 2026-07-31): the 4 unblockable-family
    # patterns below all now require the "can't be blocked" clause NOT be
    # followed by a restriction-rider continuation (Q8.2 terminology law:
    # "except by", "by creatures with", "unless", "as long as" -- duration
    # phrases like "this turn"/"until end of turn" are NOT a restriction and
    # are explicitly allowed to intervene). grants-unblockable's old pattern
    # matched its own "as long as" branch as if absolute -- that branch now
    # belongs to the cant-be-blocked-<restriction> family below and was
    # dropped here. KNOWN RESIDUAL GAP (not fixed by this rebuild, flagged
    # not silently papered over): the restriction-token list above doesn't
    # cover "by creatures that [a player] controls" (The Black Gate,
    # rule:grants-unblockable-target member) -- that phrase doesn't match
    # "by creatures with" and doesn't fit any of the 4 ratified
    # cant-be-blocked-<restriction> closed-vocab values either (it's a
    # by-PLAYER shape none of them enumerate); see docs/grammars.json's
    # cant-be-blocked-<restriction> notes for the full Captain-flag. The
    # standing 20-hit sample-sheet gate (sec.2.5) is the safety net for this
    # gap at actual DET-pass time.
    ("rule:grants-unblockable", rf"can'?t be blocked this turn{RESTRICTION_GUARD}",
     "Q8.8 rebuild: dropped the old 'as long as' branch (now routes to cant-be-blocked-<restriction>); requires the eot duration marker since granted-unblockable effects are inherently temporary (distinguishes from rule:innate-unblockable's unmarked/permanent shape)"),
    ("rule:grants-unblockable-target", rf"target creature can'?t be blocked{RESTRICTION_GUARD}",
     "Q8.8 rebuild: added the restriction-continuation guard (see KNOWN RESIDUAL GAP note above re: The Black Gate)"),
    ("rule:grants-ward-to-other-creatures", r"other creatures you control have ward", "fixed phrase"),
    ("rule:innate-unblockable", rf"(?:this creature|{re.escape(fc.CARDNAME_TOKEN)}) can'?t be blocked{RESTRICTION_GUARD}",
     "Q8.8 rebuild: replaced the old partial '(?!except)' guard with the full 4-phrase restriction-continuation guard. PREVIOUSLY a known gap (pronoun/proper-noun subject anchor missed 5/11 current members: 'It', 'Sygg', 'Willie Lumpkin', 'Ukkima') -- FIXED by the DET preprocessing standard v1 (CARDNAME canonicalization, 2026-07-31 follow-on): proper-noun self-references now canonicalize to the ~ token before matching. 'It' pronoun self-reference (Creeping Tar Pit) remains a separate, unaddressed gap -- pronoun coreference, not CARDNAME canonicalization."),
    ("rule:activated-grants-self-unblockable",
     rf"(?:\{{[^}}]*\}}|\b(?:Sacrifice|Discard|Remove|Tap|Exile|Pay)\b[^.:\n]*)[^.]*:[^.]*(?:this (?:creature|permanent)|{re.escape(fc.CARDNAME_TOKEN)}) can'?t be blocked{RESTRICTION_GUARD}",
     "activated-cost self-unblockable (F2 sweep: cost isn't always a mana/tap symbol -- 'Sacrifice X:', 'Discard a card:', 'Remove a counter:' etc. are equally valid activation costs; excludes loyalty-ability '−N:' costs by requiring one of these literal cost words, verified against the corpus not to pick up Vronos, Masked Inquisitor's quoted grant text. Q8.8 rebuild: added the restriction-continuation guard. DET preprocessing standard v1: CARDNAME token added as a subject alternative)"),
    # Q8.5 NEW ratified grammar cant-be-blocked-<restriction> (walk-ratification
    # 2026-07-31): closed vocab by-color/by-power/except-by-count/
    # as-long-as-<state>. "Non-keyword oracle text only" (Q8.5) -- each
    # pattern below was corpus-verified to exclude printed keyword reminder
    # text (Menace's fixed "two or more creatures", Skulk's fixed "greater
    # power" with no number, Landwalk's fixed "defending player controls a/an
    # <land type>") since the keyword layer owns those, not this family (Q8.6).
    ("rule:cant-be-blocked-by-color", r"can'?t be blocked by (?:white|blue|black|red|green) creatures",
     "seed axis, pattern newly authored this session (walk didn't originally propose one for this pre-existing axis); no keyword contamination risk found"),
    ("rule:cant-be-blocked-by-power", r"can'?t be blocked by creatures with power \d+ or (?:less|greater)",
     "corpus-verified: requiring a literal number excludes Skulk's fixed numberless 'greater power' reminder text (81 raw hits collapse to 57 once the numberless Skulk phrasing is excluded)"),
    ("rule:cant-be-blocked-except-by-count", r"can'?t be blocked except by (?!two\b)[a-z0-9-]+ or more creatures",
     "corpus-verified: excluding 'two' specifically excludes Menace's fixed reminder text (0/244 'two or more' hits lack the word 'menace' nearby -- 100% Menace-owned); 'three or more'/'six or more' etc. are genuine non-keyword variants (10 hits)"),
    ("rule:cant-be-blocked-as-long-as-state", r"can'?t be blocked as long as (?!defending player controls\b)[^.\n]*",
     "corpus-verified: excluding 'defending player controls' excludes Landwalk's fixed reminder-text shape (209 hits, all landwalk); remainder are genuine non-keyword state-conditions (18 hits: life total, graveyard count, attacking-alone, etc.)"),
    ("rule:cant-be-blocked-by-controller", r"can'?t be blocked by creatures (?:that|who|your opponents?|[a-z' ]*player)[^.\n]*controls?",
     "B1 ruling (2026-07-31, post-execution follow-on): new restriction-vocab value, names WHO may not block rather than what the blocker is like. Corpus-verified 2 hits: The Black Gate (quote-verified member, moved from rule:grants-unblockable-target) and Rikku, Resourceful Guardian (corpus candidate, NOT added as a member -- B1 only ordered Black Gate's move)"),
    ("rule:kicker-conditional-bonus-effect", None, "WITHDRAWN (Q9, walk-ratification 2026-07-31): rule:kicker-conditional-bonus-effect killed as a bare-keyword duplicate (b1/b2 precedent); its DET pattern is withdrawn from the ratified set, not measured."),
    ("rule:landfall-gain-life", r"landfall[^\n]*gain[^\n]*life|gain[^\n]*life[^\n]*landfall", "landfall ability word + gain-life effect in same paragraph (F2 sweep: paragraph-scoped not sentence-scoped, same fix class as landfall-produces-mana)"),
    ("rule:landfall-produces-mana",
     r"landfall[^\n]*\badd\w*\b[^\n]*(?:\{[^}]+\}|\bmana\b)|\badd\w*\b[^\n]*(?:\{[^}]+\}|\bmana\b)[^\n]*landfall",
     "F2 fix: landfall ability word + 'add ... mana' in same paragraph (was sentence-scoped [^.]* and symbol-only \\{ -- Omnath, Locus of Creation's landfall clause has a period between the ability-word sentence and the 'add {R}{G}{W}{U}' sentence, AND the pattern must also catch prose mana description with no {} symbol at all, e.g. 'add one mana of any color')"),
    ("rule:landfall-self-pump", r"landfall[^\n]*gets? \+(?:\d+|[Xx])/\+(?:\d+|[Xx])|gets? \+(?:\d+|[Xx])/\+(?:\d+|[Xx])[^\n]*landfall", "landfall ability word + self-pump in same paragraph (F2 sweep: paragraph-scoped not sentence-scoped, and pump amount may be X. KNOWN GAP, flagged not silently dropped: single-line scoping intentionally does NOT cross a newline, so a modal 'choose one —' + bulleted pump option on its own line (Retreat to Hagra/Valakut) isn't caught -- an unbounded cross-newline window was tested and rejected because it produces real false positives, matching an unrelated static pump ability elsewhere on the same card, e.g. Moraug/Maja Bretagard Protector/Springheart Nantuko; modal-bullet handling needs per-mode text splitting, out of scope for this sweep)"),
    ("rule:no-maximum-hand-size", r"no maximum hand size|doesn'?t have a maximum hand size|have no maximum hand size", "fixed phrase"),
    ("rule:prevents-regeneration", r"can'?t be regenerated|couldn'?t be regenerated", "fixed phrase, CR 701.15"),
    ("rule:restricted-purpose-mana", r"spend this mana only to|can be spent only to|this mana can'?t be spent", "fixed mana-restriction phrase"),
    ("rule:stun-counter", r"stun counters?\b", "CR 701.44/122.1 typed counter name"),
    ("rule:the-ring-tempts-you", r"the ring tempts you", "fixed phrase, unique to Ring-bearer mechanic"),
    ("rule:energy-<family> pre-filter (spends {E})", r"pay\w* (?:one or more |any amount of |[\w-]+ )?\{E\}", "activated-ability cost spends energy -- pre-filter for the 4-axis energy family, NOT a full classifier"),
    ("rule:gives-energy-counters (grant pre-filter)", r"gets? [^.]*\{E\}|you get \{E\}|\{E\} counters?", "energy-counter GRANT text -- pre-filter for gives-energy-counters-condition/-immediately"),
]


# G2 (holes-found-in-pre-execution-review guard, walk-ratification 2026-07-31):
# "enters tapped" false-positives on cards imposing tapped entry on OTHER
# permanents (Root Maze class: "Artifacts and lands enter the battlefield
# tapped"). The pattern must verify the clause's subject is the card itself;
# imposed-on-others hits are excluded and reported as a candidate sibling axis
# (rule:imposes-enters-tapped), not silently tagged.
ENTERS_TAPPED_CLAUSE_RE = re.compile(
    r"""([A-Za-z][A-Za-z "',-]{0,70}?)\s+enters?(?: the battlefield)? tapped\b(?!,? (?:unless|if))""", re.I)
# Words that disqualify a captured subject from being the bare Root-Maze
# class-noun shape -- their presence means the true subject is a specific
# self-reference (this/it/that/proper noun), a definite single object ("the
# token"), or a conditional clause wrapping a self-reference ("If you
# control..., this land"), none of which are imposed-on-others.
_DISQUALIFY_RE = re.compile(r"\b(this|it|that|you|may|have|if|unless|when|whenever|the)\b", re.I)
# Bare plural-class subject (no disqualifying word) -- the Root Maze shape:
# "Artifacts and lands", "Creatures your opponents control", "Permanents",
# "Non-Phyrexian creatures", etc. Corpus-verified 2026-07-31 against all 709
# raw "enters tapped" hits (23-24 imposed-on-others; remainder self-
# referential and NOT excluded). KNOWN RESIDUAL GAP, flagged not silently
# claimed complete: novel imposed-on-others phrasings outside this suffix
# list (e.g. Radiant Grace's "Creatures enchanted player controls") aren't
# caught and stay in the self bucket -- the standing 20-hit sample-sheet
# gate (sec.2.5) is the safety net at actual DET-pass time.
_BARE_CLASS_RE = re.compile(
    r"""^(?:[A-Za-z-]+,?\s+(?:and\s+)?)*\b(artifacts?|lands?|creatures?|permanents?|tokens?)\b"""
    r"""(?:\s+(?:you control|your opponents control|played by (?:your )?opponents|your opponents cast))?$""", re.I)


def _classify_enters_tapped_subject(subj: str) -> str:
    if _DISQUALIFY_RE.search(subj):
        return "self"
    if _BARE_CLASS_RE.match(subj):
        return "imposed"
    return "self"


def _enters_tapped_subject_split(oids_matching_base_pattern, texts, cards):
    """Returns (self_oids, imposed_rows) -- G2 subject check applied on top of
    the base regex hit set (used for both enters-tapped variants). `texts`
    maps oid -> list of scan-texts (DET preprocessing standard v1); subjects
    are pooled across every scan-text for the card. PER-CLAUSE, not per-card:
    a card with both a self clause and an imposed clause (False Floor: "This
    artifact enters tapped." + "Creatures enter tapped.") counts toward BOTH
    self_oids and imposed_rows -- an imposed clause elsewhere on the card
    must never suppress a genuine self hit."""
    self_oids = []
    imposed_rows = []
    for oid in oids_matching_base_pattern:
        subjects = [m.group(1).strip() for text in texts[oid]
                    for m in ENTERS_TAPPED_CLAUSE_RE.finditer(text)]
        if not subjects:
            # base pattern matched via the conditional-variant's reversed
            # "unless X, ~ enters tapped" branch, which the clause regex
            # (anchored on "<subject> enters tapped") doesn't parse the same
            # way -- treat as self (that branch is always self-referential
            # per its own construction, e.g. "Unless you pay {1}, this
            # permanent enters tapped").
            self_oids.append(oid)
            continue
        classes = {_classify_enters_tapped_subject(s) for s in subjects}
        if "self" in classes:
            self_oids.append(oid)
        if "imposed" in classes:
            imposed_rows.append({"oracle_id": oid, "name": cards[oid].get("name", ""),
                                  "subjects": subjects})
    return self_oids, imposed_rows


def main():
    codebook = json.loads((fc.FOUNDRY_OUT_DIR / "codebook.json").read_text())
    axes = codebook["axes"]
    cards, _, gated_out = fc.load_corpus_gated()
    print(f"corpus: {len(cards)} gate-passing cards ({gated_out} gated out)")

    # DET preprocessing standard v1 (walk-ratification 2026-07-31 follow-on,
    # B3/B4): CARDNAME canonicalization + modal-mode bullet splitting, joining
    # the existing polarity/templating-era/all-faces rules into one standing
    # pipeline. texts[oid] is a LIST of scan-texts; a pattern hits the card
    # if it matches ANY of them.
    texts = {oid: fc.det_scan_texts(c) for oid, c in cards.items()}

    results = []
    imposed_on_others_report = None
    for slug, pattern_src, note in PATTERNS:
        if pattern_src is None:
            results.append({
                "slug": slug, "pattern": None, "note": note,
                "corpus_hits": None, "codebook_n_members_at_probe": None,
                "sample_hit_names": [], "status": "withdrawn",
            })
            print(f"{slug}: WITHDRAWN -- {note}")
            continue

        pat = re.compile(pattern_src, re.I)
        hits = [oid for oid, text_list in texts.items() if any(pat.search(t) for t in text_list)]

        if slug in ("rule:enters-tapped (unconditional)", "rule:enters-tapped-conditional"):
            self_hits, imposed_rows = _enters_tapped_subject_split(hits, texts, cards)
            if slug == "rule:enters-tapped (unconditional)":
                imposed_on_others_report = imposed_rows
            hits = self_hits

        n_members = len(axes.get(slug, {}).get("members", [])) if slug in axes else None
        results.append({
            "slug": slug, "pattern": pattern_src, "note": note,
            "corpus_hits": len(hits), "codebook_n_members_at_probe": n_members,
            "sample_hit_names": sorted({cards[oid].get("name", "") for oid in hits[:8]}),
        })
        n_str = f"n_members={n_members}" if n_members is not None else "n_members=n/a"
        print(f"{slug}: hits={len(hits)}  {n_str}  pattern={pattern_src!r}")

    print(f"\nG2 enters-tapped subject check: {len(imposed_on_others_report)} imposed-on-others hits "
          f"excluded (candidate sibling axis rule:imposes-enters-tapped, NOT auto-tagged):")
    for row in imposed_on_others_report:
        print(f"    {row['name']} | subject={row['subjects']!r}")

    # rule:imposes-enters-tapped (authored 2026-07-31, B3/B4 follow-on):
    # reuses the enters-tapped base pattern + the G2 subject classifier
    # (ENTERS_TAPPED_CLAUSE_RE + _classify_enters_tapped_subject) rather than
    # a standalone regex -- its hit set IS the imposed_on_others_report
    # computed above, by construction (not a separate measurement).
    imposes_slug = "rule:imposes-enters-tapped"
    imposes_pattern_doc = (
        r"[same base pattern as rule:enters-tapped] + subject classified 'imposed' "
        r"(bare plural class noun -- artifacts?/lands?/creatures?/permanents?/tokens?, "
        r"optionally with 'you control'/'your opponents control'/'played by opponents' "
        r"suffix, with NO self-reference word (this/it/that/the/CARDNAME) present)"
    )
    n_members = len(axes.get(imposes_slug, {}).get("members", [])) if imposes_slug in axes else None
    results.append({
        "slug": imposes_slug, "pattern": imposes_pattern_doc,
        "note": "Root Maze class sibling of rule:enters-tapped; seeded via the G2 guard's own exclusion list",
        "corpus_hits": len(imposed_on_others_report), "codebook_n_members_at_probe": n_members,
        "sample_hit_names": sorted({row["name"] for row in imposed_on_others_report[:8]}),
    })
    print(f"{imposes_slug}: hits={len(imposed_on_others_report)}  n_members={n_members}  "
          f"pattern={imposes_pattern_doc!r}")

    fc.write_json(OUT_PATH, {
        "corpus_size_gated": len(cards), "gated_out": gated_out,
        "ruling_basis": "CORPUS-PASS-PLAN.md sec.1 (Lane 1 DET pass) -- these are PROPOSALS, not ratified patterns",
        "results": results,
        "g2_imposed_on_others_candidates": imposed_on_others_report,
    })
    print(f"\nwrote {OUT_PATH}")


if __name__ == "__main__":
    main()
