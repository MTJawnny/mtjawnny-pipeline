#!/usr/bin/env python3
"""Slug validator -- docs/CODEBOOK-NAMING-GRAMMAR.md sec.10 ("Lane-1 lint,
wire into emit + SUP"). Implements the six pseudo-spec checks:
  1. charset            2. banned tokens         3. closed vocabulary
  4. slot order          5. synonym collision      6. restriction/counter/cost laws

This module never mutates the codebook and never auto-fixes a failure --
"Validator failures are never auto-fixed; they surface for ruling" (sec.10).
validate_slug() is a pure function returning a result dict; main() runs it
in batch over codebook.json for reporting (used by the combined per-axis
walk, CORPUS-PASS-PLAN.md step 3).

Usage:
  python3 experiments/validate_slug.py rule:some-proposed-slug
  python3 experiments/validate_slug.py --batch   # validates every active
                                                  # codebook.json slug
"""
import sys
import re
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402

CODEBOOK_PATH = fc.FOUNDRY_OUT_DIR / "codebook.json"

# ---------------------------------------------------------------------------
# 1. Charset (sec.10.1)
# ---------------------------------------------------------------------------
CHARSET_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# ---------------------------------------------------------------------------
# 2. Banned tokens (sec.10.2)
# ---------------------------------------------------------------------------
# Literal single-token bans. "free" and "counter"/"token" adjacency and
# "creates"/"scaled" are handled by dedicated functions below since they
# need slug-position or definition context, not a flat membership test.
BANNED_LITERAL_TOKENS = {"defender", "countered"}

# ---------------------------------------------------------------------------
# 3. Closed vocabularies -- assembled from CODEBOOK-NAMING-GRAMMAR.md
# sections 2 (DELIVERY), 4 (EFFECT), 5 (OBJECT), 6 (SCOPE), 7 (scaling stats),
# 8 (counter/token types), plus the ratified glossary entries (sec.4/12:
# "scroll", "regrowth") and structural connectives the grammar itself uses
# in every example slug (to/with/of/or/as/from/at/for/each/only/during/
# your/an/a/the excluded -- the grammar bans articles outright, sec.1
# formatting law). Numeric/variable tokens (x, digits, plus1/minus1) are
# always allowed per sec.1.
# ---------------------------------------------------------------------------

DELIVERY_VOCAB = {
    "activated", "static", "etb", "death", "trigger", "leaves", "battlefield",
    "attack", "cast", "combat", "damage", "to", "player", "creature", "upkeep",
    "landfall", "loyalty", "replacement", "kicker", "dies",
    # Q2 (walk-ratification 2026-07-31): becomes-targeted-trigger,
    # blocks-or-becomes-blocked-trigger added to the closed DELIVERY vocab.
    "becomes", "targeted", "blocks", "blocked",
}

EFFECT_VOCAB = {
    "destroy", "exile", "bounce", "tuck", "sacrifice", "discard", "mill",
    "draw", "loot", "scry", "surveil", "proliferate", "tutor", "reanimate",
    "regrowth", "create", "token", "pump", "debuff", "damage", "gain", "life",
    "lose", "drain", "tap", "untap", "or", "transform", "copy", "counters",
    "grants", "taxes", "cost", "reduction",
    # Q4 (walk-ratification 2026-07-31): cant-be-countered -> spell-uncounterable
    # ("spell" is already in OBJECT_VOCAB).
    "uncounterable",
    # Captain-authored rule:imposes-enters-tapped (2026-07-31 follow-on, B3/B4):
    # named directly by Captain, ratifying the token as part of naming the slug.
    "imposes",
}

OBJECT_VOCAB = {
    "creature", "artifact", "enchantment", "planeswalker", "battle", "land",
    "permanent", "nonland", "spell", "noncreature", "player", "opponent",
    "any", "target", "card", "in", "graveyard",
}

SCOPE_VOCAB = {
    "self", "own", "opponent", "any", "each", "mass", "target", "defending",
    "player", "two", "conditional",
}

SCALING_STAT_VOCAB = {
    "creature", "count", "hand", "size", "own", "counters", "graveyard",
    "land", "type", "permanent", "attacker", "legendary", "mana", "value",
    "life", "gained", "x", "opponent", "target", "token", "color", "charge",
    "scales", "with", "counter",
}

COUNTER_TOKEN_VOCAB = {
    "plus1", "minus1", "charge", "stun", "loyalty", "counter", "counters",
    "treasure", "clue", "food", "blood", "gold", "powerstone", "mutagen",
    "lander", "producing",
}

# `delayed` moved here from DELIVERY_VOCAB by grammar §2d (Captain-ratified
# 2026-08-03): a delayed trigger is a CREATED ability, and CR 603.7d/e give
# its source to the creator -- so the card's delivery is whatever created it,
# and `delayed` describes WHEN the effect happens.
QUALIFIER_VOCAB = {"mass", "scales", "with", "cost", "activation", "additional",
                   "delayed"}

# sec.3 activation-restriction closed family -- vocabulary its slugs use.
RESTRICTION_VOCAB = {
    "activation", "restricted", "to", "sorcery", "speed", "instant", "only",
    "during", "your", "turn", "own", "upkeep", "combat", "opponents", "once",
    "each", "condition", "gated",
}

# sec.12 idiomatic-leaf exemption list -- job-names EXEMPT from closed-vocab
# checking (grammar governs mechanism slugs; these are Captain-ratified
# per-slug exceptions). Extend this set only via explicit Captain ruling.
EXEMPT_LEAF_SLUGS = {
    "rule:compensates-controller-with-token",
    "rule:cheat-creature-into-play",
    "rule:rhystic-tax",
    "rule:the-ring-tempts-you",
    # Q6 (walk-ratification 2026-07-31), CODEBOOK-NAMING-GRAMMAR.md sec.12/13.
    "rule:burst-draw",
    "rule:cantrip",
    "rule:modal",
    "rule:drain-life",
    "rule:combat-trick-pump-own-creature",
    "rule:tribal-anthem-buff",
    "rule:alternate-win-condition",
}

# Ratified glossary (sec.4/sec.12): standing shorthand vocabulary.
GLOSSARY_VOCAB = {"scroll", "regrowth"}

# Q5 extended structural/descriptive vocabulary (walk-ratification 2026-07-31,
# CODEBOOK-NAMING-GRAMMAR.md sec.14) -- the EXACT list Captain ratified from
# CORPUS-PASS-WALK-RATIFICATION.md sec.2.2.2's proposal, not the full 179-token
# frequency list. Deliberately excludes 'scaled' (banned, D-3), 'a'/'the'
# (banned articles), 'targeted' (targeted-<action>-<class> grammar family
# needs a membership check first), 'lifegain' (synonym-collision candidate
# against the ratified gain-life EFFECT verb) -- those stay in the final
# naming-audit backlog, not silently passed here.
WALK_RATIFICATION_VOCAB_20260731 = {
    "creatures", "other", "on", "from", "library", "triggers", "ability",
    "and", "by", "prevents", "unblockable", "buff", "tapped", "restriction",
    "top", "targets", "doubles", "energy", "forces", "controller", "prevent",
    "into", "growth", "tribal", "effect", "choose", "enters", "cards",
    "threshold", "recursion",
}

# Q8.5 (walk-ratification 2026-07-31): cant-be-blocked compound stem token,
# ratified into vocabulary for the new cant-be-blocked-<restriction> grammar
# family. Does not affect the 'countered' ban (sec.10.2) -- separate token.
CANT_BE_BLOCKED_STEM_VOCAB = {"cant", "be", "blocked"}

# F4 (walk-ratification 2026-07-31): tokens that are ratified vocabulary (so
# they do NOT fail unknown_vocabulary) but still deserve a non-blocking
# reviewer warning ("grab-bag smell") rather than a silent clean pass.
SOFT_WARNING_TOKENS = {"and"}

# "grants-<keyword>" (sec.4 EFFECT) and the keyword-grant facet scheme
# (addendum-3 sec.7) parameterize on CR keyword names -- any of the 193
# CR-702 keyword names (tokenized) is legitimate vocabulary in that
# position. Loaded from keyword-buckets.json (this session's step-2
# output) so the two artifacts stay in sync; falls back to an empty set if
# that file has not been generated yet (keeps this module standalone).
def _load_keyword_vocab() -> set:
    path = fc.FOUNDRY_OUT_DIR / "keyword-buckets.json"
    if not path.exists():
        return set()
    data = json.loads(path.read_text())
    vocab = {"keyword", "grant", "grants", "temporary", "removal", "instead"}
    for slug in data.get("keywords", {}):
        vocab.update(slug.split("-"))
    return vocab


KEYWORD_VOCAB = _load_keyword_vocab()

CLOSED_VOCAB = (DELIVERY_VOCAB | EFFECT_VOCAB | OBJECT_VOCAB | SCOPE_VOCAB
                | SCALING_STAT_VOCAB | COUNTER_TOKEN_VOCAB | QUALIFIER_VOCAB
                | RESTRICTION_VOCAB | GLOSSARY_VOCAB | KEYWORD_VOCAB
                | WALK_RATIFICATION_VOCAB_20260731 | CANT_BE_BLOCKED_STEM_VOCAB)

# ---------------------------------------------------------------------------
# sec.3 closed activation-restriction family -- exact enumeration
# ---------------------------------------------------------------------------
ACTIVATION_RESTRICTION_FAMILY = {
    "activation-restricted-to-sorcery-speed",
    "activation-restricted-to-instant-speed",
    "activation-restricted-only-during-your-turn",
    "activation-restricted-to-own-upkeep",
    "activation-restricted-during-combat",
    "activation-restricted-during-opponents-turn",
    "activation-restricted-once-each-turn",
    "activation-condition-gated",
}

# ---------------------------------------------------------------------------
# 5. Synonym-collision normalization (sec.10.5 / D-2 / D-3)
# ---------------------------------------------------------------------------
SCALES_WITH_RE = re.compile(r"^(.+)-scaled-by-(.+)$")          # D-3: retire -scaled-by-
SCALES_PREFIX_RE = re.compile(r"^scales-(.+)-with-(.+)$")       # scales-X-with-Y -> X-scales-with-Y


def normalize_for_collision(bare_slug: str) -> str:
    """bare_slug has the 'rule:' prefix already stripped. Canonicalizes
    known synonym/connective variants so two slugs describing the same
    mechanic collapse to the same string (sec.10.5). Conservative by
    design -- this is NOT a token-sort/bag-of-words normalizer (that would
    produce false collisions between unrelated mechanics); it only applies
    the specific ratified equivalences (D-2 bare-verb-stem, D-3
    -scales-with- connective)."""
    s = bare_slug
    m = SCALES_PREFIX_RE.match(s)
    if m:
        s = f"{m.group(1)}-scales-with-{m.group(2)}"
    m = SCALES_WITH_RE.match(s)
    if m:
        s = f"{m.group(1)}-scales-with-{m.group(2)}"
    if s.startswith("creates-"):
        s = "create-" + s[len("creates-"):]
    s = s.replace("-creates-", "-create-")
    return s


def find_collisions(slugs: list) -> list:
    """Returns [(slug_a, slug_b, normalized_form), ...] for every pair of
    distinct slugs (rule:-prefixed) that normalize identically."""
    buckets = {}
    for s in slugs:
        bare = s[len("rule:"):] if s.startswith("rule:") else s
        norm = normalize_for_collision(bare)
        buckets.setdefault(norm, []).append(s)
    collisions = []
    for norm, group in buckets.items():
        if len(group) > 1:
            group_sorted = sorted(group)
            for i in range(len(group_sorted)):
                for j in range(i + 1, len(group_sorted)):
                    collisions.append((group_sorted[i], group_sorted[j], norm))
    return collisions


# ---------------------------------------------------------------------------
# Main per-slug validator
# ---------------------------------------------------------------------------

def _check_charset(bare: str, failures: list):
    if not CHARSET_RE.match(bare):
        failures.append({"check": "charset", "detail": "must match ^[a-z0-9]+(-[a-z0-9]+)*$"})


def _check_banned_tokens(bare: str, tokens: list, definition: str, failures: list):
    for tok in tokens:
        if tok in BANNED_LITERAL_TOKENS:
            failures.append({"check": "banned_token", "detail": f"'{tok}' is banned (sec.10.2)"})

    # bare "counter" as final noun without a preceding type word (sec.8.1)
    typed_counter_words = {"plus1", "minus1", "charge", "stun", "loyalty"}
    # words that definitely are NOT a counter type name (vs. the generic
    # "<name>-counter" shape sec.8.1 explicitly allows, e.g. oil-counter,
    # energy-counter -- unenumerable in full, so this is a blocklist, not
    # an allowlist)
    non_type_words = {"self", "own", "any", "some", "the", "for", "a", "an", "negative"}
    if tokens and tokens[-1] in ("counter", "counters"):
        preceding = tokens[-2] if len(tokens) >= 2 else None
        # "...-with-[X-]counters" binding-word exception (sec.8.1 example:
        # etb-with-counters; sec.7 example: create-token-with-x-counters --
        # "with" can be 1-3 tokens before "counters", not just adjacent).
        has_with_binding = "with" in tokens[max(0, len(tokens) - 4):-1]
        # Fail only when we can be SURE it's untyped: no binding/removal
        # exception, not an explicit typed-counter word, AND the preceding
        # token is either absent or a known non-type filler -- anything
        # else (oil, energy, ...) is treated as a plausible "<name>-counter"
        # per sec.8.1 and passed through (verify at the per-axis walk, not
        # here: this validator does not have a full MTG counter-type list).
        if (not has_with_binding and "removal" not in tokens
                and preceding not in typed_counter_words
                and (preceding is None or preceding in non_type_words)):
            failures.append({
                "check": "bare_counter_noun",
                "detail": "'counter(s)' as final token must be typed (plus1/minus1/charge/stun/loyalty/<name>) "
                           "or bound by a recognized shape (-with-counters, counter-removal-...) -- sec.8.1",
            })

    # "free" unless the axis definition quotes a zero-cost (sec.10.2) -- needs definition
    if "free" in tokens:
        if not definition or not re.search(
                r"\bfree\b|\bzero.cost\b|\{0\}|without paying|at no (?:mana )?cost|no mana cost", definition, re.I):
            failures.append({
                "check": "free_must_be_free",
                "detail": "'free' token requires the definition to quote a zero-cost (ratified b2) -- no definition "
                           "evidence found" if not definition else "'free' token present but definition text does "
                           "not quote a zero-cost",
            })

    if "creates" in tokens:
        failures.append({"check": "post_d2_creates", "detail": "'creates' retired post-D-2 -- use bare stem 'create'"})
    if "scaled" in tokens:
        failures.append({"check": "post_d3_scaled", "detail": "'scaled' retired post-D-3 -- use '-scales-with-'"})

    # token immediately adjacent to counter without section-8 shapes
    for i in range(len(tokens) - 1):
        pair = (tokens[i], tokens[i + 1])
        if {"token", "counter"} <= {pair[0], pair[1]} or {"token", "counters"} <= {pair[0], pair[1]}:
            failures.append({
                "check": "token_counter_adjacency",
                "detail": f"'{pair[0]}-{pair[1]}' adjacency not a recognized section-8 shape "
                           "(a counter is not a token and a token is not a counter, CR 122.1)",
            })


def _check_closed_vocabulary(bare: str, tokens: list, exempt: bool, failures: list) -> list:
    if exempt:
        return []
    unknown = [t for t in tokens if t not in CLOSED_VOCAB and not t.isdigit() and t not in ("x", "plus1", "minus1")]
    if unknown:
        failures.append({
            "check": "unknown_vocabulary",
            "detail": f"token(s) {unknown} not in the closed vocabulary (sections 2,4-8) or ratified glossary -- "
                      "new vocabulary requires Captain ratification, not silent pass (sec.10.3)",
        })
    return unknown


def _check_restriction_family(bare: str, failures: list):
    if bare.startswith("activation-restricted") or bare.startswith("activation-condition"):
        if bare not in ACTIVATION_RESTRICTION_FAMILY:
            failures.append({
                "check": "restriction_family_closed",
                "detail": f"'{bare}' looks like the sec.3 activation-restriction family but is not one of the "
                          f"8 enumerated members -- that family is CLOSED and DET-owned (D-4); SYNTH may not "
                          f"mint new members",
            })


def _check_cost_law(bare: str, definition: str, failures: list):
    """sec.9: cost-vs-effect law. codebook.json definitions are Captain/SUP
    PARAPHRASES, not CR-style '[Cost]: [Effect]' notation or oracle-text
    quotes (those live only in the per-batch review JSON, not on the
    codebook entry) -- so this can only do a weak semantic check (does the
    definition talk about paying/cost at all), not the strict colon-position
    check the law describes. The strict check belongs at DET-pattern design
    time against real oracle text (per-axis walk), not here."""
    if not re.search(r"(^|-)cost(-|$)|as-activation-cost|^additional-cost-", bare):
        return
    if definition is None:
        failures.append({
            "check": "cost_law_unverified",
            "detail": "slug names a cost-side mechanic (sec.9) but no definition text was supplied to weak-check "
                      "against",
        })
        return
    if not re.search(r"\bcost\b|\bpay(ing|s)?\b|\bactivat(e|ed|ion)\b", definition, re.I):
        failures.append({
            "check": "cost_law_weak_check_failed",
            "detail": "slug names a cost-side mechanic but its definition text never mentions cost/pay/activate -- "
                      "worth a second look, but NOT the strict sec.9 colon-position check (that needs oracle text, "
                      "done at DET-pattern design time)",
        })


def _check_soft_warnings(tokens: list, warnings: list):
    """F4 (walk-ratification 2026-07-31): ratified-but-flagged tokens. NOT a
    pass and NOT a failure -- surfaces for review without blocking ('and'-
    slugs are a grab-bag smell worth a second look)."""
    hit = sorted(set(tokens) & SOFT_WARNING_TOKENS)
    for tok in hit:
        warnings.append({
            "check": "soft_vocab_warning",
            "detail": f"'{tok}' is ratified vocabulary but flagged for review (sec.14 F4) -- "
                       "'and'-slugs are a grab-bag smell; consider whether this should split into two axes",
        })


def validate_slug(slug: str, definition: str = None, all_slugs: list = None) -> dict:
    """slug must include the 'rule:' prefix. Returns
    {"slug", "ok", "failures": [...], "warnings": [...], "unknown_tokens": [...]}.
    'warnings' (F4) never affects 'ok' -- non-blocking, surfaced for review."""
    if not slug.startswith("rule:"):
        return {"slug": slug, "ok": False,
                "failures": [{"check": "prefix", "detail": "slug must start with 'rule:'"}],
                "warnings": [], "unknown_tokens": []}
    bare = slug[len("rule:"):]
    tokens = bare.split("-") if bare else []
    exempt = slug in EXEMPT_LEAF_SLUGS
    failures = []
    warnings = []

    _check_charset(bare, failures)
    if CHARSET_RE.match(bare):  # only run token-level checks on a charset-valid slug
        _check_banned_tokens(bare, tokens, definition, failures)
        unknown = _check_closed_vocabulary(bare, tokens, exempt, failures)
        _check_soft_warnings(tokens, warnings)
    else:
        unknown = []
    _check_restriction_family(bare, failures)
    _check_cost_law(bare, definition, failures)

    if all_slugs:
        norm = normalize_for_collision(bare)
        others = [s for s in all_slugs if s != slug and normalize_for_collision(
            s[len("rule:"):] if s.startswith("rule:") else s) == norm]
        if others:
            failures.append({"check": "synonym_collision", "detail": f"normalizes identically to {others}"})

    return {"slug": slug, "ok": len(failures) == 0, "exempt": exempt,
            "failures": failures, "warnings": warnings, "unknown_tokens": unknown}


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    if args[0] == "--batch":
        codebook = json.loads(CODEBOOK_PATH.read_text())
        axes = codebook["axes"]
        active_slugs = sorted(s for s, e in axes.items() if e.get("status") == "active")
        results = []
        for slug in active_slugs:
            defn = axes[slug].get("definition")
            r = validate_slug(slug, definition=defn, all_slugs=active_slugs)
            results.append(r)
        n_fail = sum(1 for r in results if not r["ok"])
        n_warn_only = sum(1 for r in results if r["ok"] and r["warnings"])
        n_clean = len(results) - n_fail - n_warn_only
        print(f"validated {len(results)} active slugs: {n_clean} clean, {n_warn_only} warned (non-blocking), "
              f"{n_fail} flagged")
        out_path = fc.FOUNDRY_OUT_DIR / "validate_slug_report.json"
        fc.write_json(out_path, {"total": len(results), "clean": n_clean, "warned": n_warn_only,
                                  "flagged": n_fail, "results": results})
        print(f"wrote {out_path}")
    else:
        for slug in args:
            r = validate_slug(slug)
            print(json.dumps(r, indent=2))


if __name__ == "__main__":
    main()
