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

# (slug, pattern_description, compiled-regex-source, current codebook n_members)
# n_members filled in at runtime from codebook.json; kept here as a comment
# reference for the humans reading this file.
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
    ("rule:grants-flying-and-pump-to-creature", r"gets? \+\d+/\+\d+ and gains flying|gains flying and gets \+\d+/\+\d+", "fixed phrase, both grants same clause"),
    ("rule:grants-haste-to-created-tokens", r"(?:that|those|token)[^.]*(?:has|have|gains?) haste", "haste grant scoped to token(s) just created"),
    ("rule:grants-haste-to-your-creatures", r"creatures you control have haste", "fixed phrase, board-wide static"),
    ("rule:grants-trample-to-creatures-with-counters", r"creatures? (?:you control )?with (?:a |one or more )?\+1/\+1 counters? on (?:it|them|it have|them have)[^.]*trample|trample[^.]*with a \+1/\+1 counter", "conditional-scope trample grant"),
    ("rule:grants-trample-to-other-creatures", r"other creatures you control have trample", "fixed phrase"),
    ("rule:grants-unblockable", r"can'?t be blocked (?:this turn|as long as)", "activated/self unblockable grant"),
    ("rule:grants-unblockable-target", r"target creature can'?t be blocked", "targeted unblockable grant"),
    ("rule:grants-ward-to-other-creatures", r"other creatures you control have ward", "fixed phrase"),
    ("rule:innate-unblockable", r"this creature can'?t be blocked\b(?! except)", "static self-unblockable (excludes 'can't be blocked except by...' partial-evasion which is a different axis)"),
    ("rule:activated-grants-self-unblockable", r"\{[^}]*\}[^.]*:[^.]*this (?:creature|permanent) can'?t be blocked", "activated-cost self-unblockable"),
    ("rule:kicker-conditional-bonus-effect", r"\bkicker\b|\bwas kicked\b|\bif this spell was kicked\b", "CR-702.33 keyword presence"),
    ("rule:landfall-gain-life", r"landfall[^.]*gain[^.]*life|gain[^.]*life[^.]*landfall", "landfall ability word + gain-life effect in same paragraph"),
    ("rule:landfall-produces-mana", r"landfall[^.]*add[^.]*\{|add[^.]*\{[^.]*landfall", "landfall ability word + mana symbol in same paragraph"),
    ("rule:landfall-self-pump", r"landfall[^.]*gets? \+\d+/\+\d+|gets? \+\d+/\+\d+[^.]*landfall", "landfall ability word + self-pump in same paragraph"),
    ("rule:no-maximum-hand-size", r"no maximum hand size|doesn'?t have a maximum hand size|have no maximum hand size", "fixed phrase"),
    ("rule:prevents-regeneration", r"can'?t be regenerated|couldn'?t be regenerated", "fixed phrase, CR 701.15"),
    ("rule:restricted-purpose-mana", r"spend this mana only to|can be spent only to|this mana can'?t be spent", "fixed mana-restriction phrase"),
    ("rule:stun-counter", r"stun counters?\b", "CR 701.44/122.1 typed counter name"),
    ("rule:the-ring-tempts-you", r"the ring tempts you", "fixed phrase, unique to Ring-bearer mechanic"),
    ("rule:energy-<family> pre-filter (spends {E})", r"pay\w* (?:one or more |any amount of |[\w-]+ )?\{E\}", "activated-ability cost spends energy -- pre-filter for the 4-axis energy family, NOT a full classifier"),
    ("rule:gives-energy-counters (grant pre-filter)", r"gets? [^.]*\{E\}|you get \{E\}|\{E\} counters?", "energy-counter GRANT text -- pre-filter for gives-energy-counters-condition/-immediately"),
]


def main():
    codebook = json.loads((fc.FOUNDRY_OUT_DIR / "codebook.json").read_text())
    axes = codebook["axes"]
    cards, _, gated_out = fc.load_corpus_gated()
    print(f"corpus: {len(cards)} gate-passing cards ({gated_out} gated out)")

    texts = {oid: fc.full_oracle_text(c) for oid, c in cards.items()}

    results = []
    for slug, pattern_src, note in PATTERNS:
        pat = re.compile(pattern_src, re.I)
        hits = [oid for oid, text in texts.items() if text and pat.search(text)]
        n_members = len(axes.get(slug, {}).get("member_oracle_ids", [])) if slug in axes else None
        results.append({
            "slug": slug, "pattern": pattern_src, "note": note,
            "corpus_hits": len(hits), "current_codebook_n_members": n_members,
            "sample_hit_names": sorted({cards[oid].get("name", "") for oid in hits[:8]}),
        })
        n_str = f"n_members={n_members}" if n_members is not None else "n_members=n/a"
        print(f"{slug}: hits={len(hits)}  {n_str}  pattern={pattern_src!r}")

    fc.write_json(OUT_PATH, {
        "corpus_size_gated": len(cards), "gated_out": gated_out,
        "ruling_basis": "CORPUS-PASS-PLAN.md sec.1 (Lane 1 DET pass) -- these are PROPOSALS, not ratified patterns",
        "results": results,
    })
    print(f"\nwrote {OUT_PATH}")


if __name__ == "__main__":
    main()
