#!/usr/bin/env python3
"""Combined per-axis walk scaffold (CORPUS-PASS-PLAN.md step 3). Produces a
FIRST-DRAFT, mechanically-assisted pass over every active codebook.json axis:
  1. grammar validation summary (from validate_slug.py) + rename category
  2. agent-legible definition rewrite scaffold (DELIVERY / COST / EFFECT)
  3. first-pass DET-able vs SYNTH-only signal (heuristic, NOT a ruling)
  4. grammar-family match against docs/grammars.json (existing or candidate)

This is deliberately a SCAFFOLD, not a finished ruling: the walk's real
judgment (which DET patterns to actually propose with corpus hit-counts,
which rename to actually recommend, which SYNTH classification is right)
is applied on top of this output, by hand, before anything goes in the
ratification document. Nothing here is written back to codebook.json.

Usage: python3 experiments/foundry_axis_walk.py
"""
import sys
import re
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402
import validate_slug as vs  # noqa: E402

CODEBOOK_PATH = fc.FOUNDRY_OUT_DIR / "codebook.json"
GRAMMARS_PATH = REPO_ROOT.parent / "docs" / "grammars.json"
OUT_PATH = fc.FOUNDRY_OUT_DIR / "axis_walk_scaffold.json"

# slug-prefix -> DELIVERY value, longest-prefix-wins (checked in this order)
DELIVERY_PREFIX_MAP = [
    ("activation-restricted-", "activated (restriction facet)"),
    ("activation-condition-", "activated (restriction facet)"),
    ("activated-", "activated"),
    ("etb-and-attack-trigger", "etb + attack-trigger (dual delivery)"),
    ("etb-", "etb"),
    ("death-trigger-", "death-trigger"),
    ("leaves-battlefield-trigger-", "leaves-battlefield-trigger"),
    ("attack-trigger-", "attack-trigger"),
    ("cast-trigger-", "cast-trigger"),
    ("cast-from-", "static (casting permission)"),
    ("combat-damage-to-player-", "combat-damage-to-player"),
    ("combat-damage-to-creature-", "combat-damage-to-creature"),
    ("combat-damage-triggers-", "combat-damage-to-player (unnormalized -- migration ledger)"),
    ("combat-trigger-", "combat (start-of-combat trigger, not in closed DELIVERY vocab)"),
    ("upkeep-", "upkeep-trigger"),
    ("landfall-", "landfall"),
    ("delayed-", "delayed"),
    ("kicker-", "kicker"),
    ("draw-second-", "delayed (turn-scoped counting trigger, not in closed vocab)"),
    ("postcombat-main-phase-", "static (phase-scoped trigger, not in closed vocab)"),
]

# Definition-text signals pushing toward SYNTH (judgment-dependent) --
# open-ended filters, free-form conditions, idiomatic job patterns.
SYNTH_SIGNALS = [
    (re.compile(r"matching a (filter|condition)", re.I), "open-ended filter"),
    (re.compile(r"\ba (stated|specific|specified|board-state|game-state) condition\b", re.I), "free-form condition"),
    (re.compile(r"\bthreshold\b", re.I), "threshold judgment"),
    (re.compile(r"\bchosen\b|\bchoose\b", re.I), "modal/chosen text"),
    (re.compile(r"\bcondition\b", re.I), "condition-gated"),
    (re.compile(r"\bpayoff\b|\bvalue\b|\badvantage\b|\bsynerg", re.I), "strategic/job framing, not a print pattern"),
    (re.compile(r"\bjob\b", re.I), "explicitly a job pattern"),
]

# Definition/slug-text signals pushing toward DET (fixed, anchorable print pattern).
DET_SIGNALS = [
    (re.compile(r"enters? (the battlefield )?tapped", re.I), "fixed printed phrase 'enters tapped'"),
    (re.compile(r"regenerat\w*", re.I), "fixed printed phrase 'can't be regenerated' (CR 701.15)"),
    (re.compile(r"maximum hand size", re.I), "fixed printed phrase 'no maximum hand size'"),
    (re.compile(r"stun counter", re.I), "fixed printed phrase 'stun counter'"),
    (re.compile(r"\bthe ring tempts you\b", re.I), "fixed printed phrase 'The Ring tempts you'"),
    (re.compile(r"\blandfall\b", re.I), "landfall is a CR ability word, keyword-detectable"),
    (re.compile(r"\bkicker\b|\bkicked\b", re.I), "kicker is a CR keyword, Scryfall-keyword-detectable"),
    (re.compile(r"\benergy counters?\b", re.I), "energy counter is a fixed countable resource"),
    (re.compile(r"\+1/\+1 counters? on it\b.*enters", re.I), "etb-with-counters fixed print shape"),
    (re.compile(r"activation-restricted", re.I), "closed activation-restriction family, D-4 DET-owned"),
    (re.compile(r"unblockable|can'?t be blocked", re.I), "fixed printed phrase 'can't be blocked'/'unblockable'"),
    (re.compile(r"attacks? each combat if able|must attack", re.I), "fixed printed phrase 'attacks each combat if able' (CR 508.1a)"),
    (re.compile(r"^grants-(hexproof|double-strike|trample|ward|haste|flying|creature-type|flashback"
                r"|extra-land-drop|extra-turn|additional-combat-phase|cascade|controller-hexproof)", re.I),
     "single-keyword grants-<keyword> family member -- fixed keyword-grant phrase, ties to ratified grammar family"),
    (re.compile(r"only be spent to (cast|activate)|can'?t be spent", re.I), "fixed printed mana-restriction phrase"),
    (re.compile(r"first strike.{0,20}(your turn|opponent'?s turn)", re.I), "fixed CR keyword + fixed turn-scope phrase combo"),
]


def load_grammars():
    if not GRAMMARS_PATH.exists():
        return {}
    return json.loads(GRAMMARS_PATH.read_text())["grammars"]


def delivery_for(bare_slug: str) -> str:
    for prefix, delivery in DELIVERY_PREFIX_MAP:
        if bare_slug.startswith(prefix):
            return delivery
    return "static/spell (no marked delivery prefix -- default per grammar sec.1)"


def cost_for(definition: str, delivery: str) -> str:
    if re.search(r"additional cost|as an additional cost", definition, re.I):
        m = re.search(r"(sacrific\w+|discard\w*|exil\w+|pay\w* life|return\w* .{0,40} to (its|their) owner'?s hand)"
                       r"[^.]*", definition, re.I)
        return f"additional cost -- {m.group(0)}" if m else "additional cost (see definition)"
    if re.search(r"\bpay(ing|s)? mana\b|mana cost\b|reduced cost\b|rather than (its |paying )?(its )?mana cost", definition, re.I):
        return "mana/cost-modification (see definition)"
    if "activated" in delivery:
        return "activation cost per printed ability (mana/tap/sacrifice as stated -- generic unless definition names a specific facet)"
    return "none (resolves as part of casting/triggering, no separate cost facet)"


def effect_for(definition: str) -> str:
    # Strip a leading delivery/cost clause if the definition already states one didactically
    return definition.strip()


def rewrite_definition(bare_slug: str, definition: str) -> dict:
    delivery = delivery_for(bare_slug)
    cost = cost_for(definition, delivery)
    effect = effect_for(definition)
    return {
        "delivery": delivery, "cost": cost, "effect": effect,
        "rewritten": f"TRIGGER/DELIVERY: {delivery}. COST: {cost}. EFFECT: {effect}",
    }


def det_synth_signal(definition: str, bare_slug: str, exempt: bool) -> dict:
    # NOTE: naming-vocabulary exemption (idiomatic leaf, grammar sec.12) is
    # ORTHOGONAL to DET-ability -- rule:the-ring-tempts-you is both an
    # exempt idiomatic name AND a high-confidence DET pattern (a literal
    # printed phrase). Do not early-return on exempt; let the signal scan
    # run for every axis regardless.
    det_hits = [note for pat, note in DET_SIGNALS if pat.search(definition) or pat.search(bare_slug)]
    synth_hits = [note for pat, note in SYNTH_SIGNALS if pat.search(definition)]
    if det_hits and not synth_hits:
        lean = "DET-able (high confidence)"
    elif det_hits and synth_hits:
        lean = "DET-able for a NARROW sub-pattern, SYNTH for the rest (mixed)"
    elif synth_hits:
        lean = "SYNTH-only"
    else:
        lean = "SYNTH-only (default -- no anchored print pattern detected)"
    return {"lean": lean, "det_signals": det_hits, "synth_signals": synth_hits}


def grammar_family_match(bare_slug: str, grammars: dict) -> str:
    for name, g in grammars.items():
        stem = g["stem"].split(" / ")[0].split("[")[0].rstrip("-")
        stem_bare = re.sub(r"<[^>]+>", "", stem).strip("-")
        if bare_slug.startswith(stem_bare) and stem_bare:
            return name
    return ""


def rename_category(slug: str, val_result: dict) -> str:
    if val_result.get("exempt"):
        return "EXEMPT (already on the sec.12 idiomatic-leaf list)"
    if val_result.get("ok"):
        return "CONFORMS"
    checks = [f["check"] for f in val_result.get("failures", [])]
    if checks == ["unknown_vocabulary"]:
        return "VOCAB-QUESTION (structure fine; tokens need exemption-or-extension ruling)"
    return f"STRUCTURAL: {','.join(checks)}"


def main():
    codebook = json.loads(CODEBOOK_PATH.read_text())
    axes = codebook["axes"]
    grammars = load_grammars()
    val_results = {r["slug"]: r for r in
                    json.loads((fc.FOUNDRY_OUT_DIR / "validate_slug_report.json").read_text())["results"]}

    rows = []
    for slug in sorted(s for s, e in axes.items() if e.get("status") == "active"):
        e = axes[slug]
        bare = slug[len("rule:"):]
        definition = e.get("definition") or ""
        val = val_results.get(slug, {})
        rows.append({
            "slug": slug,
            "n_members": len(e.get("members") or []),
            "definition": definition,
            "rename_category": rename_category(slug, val),
            "validator_failures": [f["check"] for f in val.get("failures", [])],
            "definition_rewrite": rewrite_definition(bare, definition),
            "det_synth": det_synth_signal(definition, bare, val.get("exempt", False)),
            "grammar_family_match": grammar_family_match(bare, grammars),
        })

    fc.write_json(OUT_PATH, {"schema": "foundry-axis-walk-scaffold/1", "total": len(rows), "rows": rows})
    lean_counts = {}
    for r in rows:
        lean_counts[r["det_synth"]["lean"]] = lean_counts.get(r["det_synth"]["lean"], 0) + 1
    print(f"wrote {OUT_PATH} ({len(rows)} axes)")
    print("DET/SYNTH lean counts:", lean_counts)


if __name__ == "__main__":
    main()
