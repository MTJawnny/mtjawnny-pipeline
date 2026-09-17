#!/usr/bin/env python3
"""CDR-09 §12a rename walk -- DERIVATION ONLY, writes nothing.

Re-derives the counter-homograph rename worklist from LIVE codebook state, per
the session handoff's precondition 4: "Re-derive the 16 renames from live state
rather than pasting §12a's list. If the live set disagrees with §12a, halt."

Conformance is the CODEBOOK-NAMING-GRAMMAR.md §8a test, applied across the
whole slug (not just final position):
  VERB  (CR 701.6) -- token is `counters` (plural), immediately followed by what
        is countered, looking PAST scope tokens (§6). Singular `counter` in verb
        sense is BANNED. Never bare, never slug-final.
  NOUN  (CR 122.1) -- `counter`/`counters` bound on the LEFT by a counter TYPE
        word, the preposition `with`, or `any`.

Sense itself is NOT guessed from the name -- that is the corruption §8a exists
to fix. Sense comes from each axis's own ratified definition text; the name is
then tested for whether it conforms to the rule for that sense.

Usage: python3 experiments/foundry_cdr09_derive.py
"""
import sys
import re
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402
import foundry_codebook as fcb  # noqa: E402

# §8a noun-side left-binders. Counter TYPE words (§8 rule 1), the `with`
# preposition, and `any` (newly ratified by CDR-09).
TYPE_WORDS = {
    "plus1", "minus1", "charge", "stun", "oil", "energy", "loyalty",
    "shield", "flying", "lore", "poison", "experience", "ice", "level",
}
LEFT_BINDERS = TYPE_WORDS | {"with", "any"}

# §6 SCOPE tokens the verb rule must look PAST when hunting the object
# (grammar §8a correction 1: in `counters-target-spell` the next token is
# `target`, not `spell`).
SCOPE_TOKENS = {"target", "each", "all", "another", "other", "any", "a", "the"}

# What can be countered (CR 701.6): a spell or an ability, possibly reached
# through a restriction word binding to one (`noncreature-spell`).
COUNTERABLE = {"spell", "ability", "spells", "abilities"}

COUNTER_TOKENS = {"counter", "counters"}

# --- Prior ratifications this derivation must not re-litigate -----------------
# §8a is not the only ratified law touching a counter token. Three further
# rulings already govern specific slugs, and a derivation blind to them
# re-raises settled questions as if they were new findings.

# §7 scaling standard: `<subject>-scales-with-<stat>` over a CLOSED stat
# vocabulary that includes `own-counters` ("counters ON the source; the
# charge-counter class") and its `charge-counters` alias. The counter token is
# bound by the ratified stat name, not left dangling.
SCALING_STATS_WITH_COUNTER = {"own-counters", "charge-counters"}

# Slugs a ratified document names VERBATIM as the correct form. Renaming these
# would break the ruling that chose them.
RATIFIED_NAMES = {
    "rule:create-token-with-x-counters":
        "CODEBOOK-NAMING-GRAMMAR.md §7 — ratified verbatim as the answer to b7 "
        "line-84: 'X scales counters ON one created token'.",
    "rule:cost-reduction-scales-with-own-counters":
        "CODEBOOK-NAMING-GRAMMAR.md §7 closed stat vocab (`own-counters`); the "
        "bare_counter_noun question was raised at the walk-ratification pass and "
        "RESOLVED AS A PASS (archive/CORPUS-PASS-WALK-RATIFICATION.md).",
    "rule:etb-with-negative-counters":
        "TRIAGE-BATCH-5 — counter polarity (+1/+1 vs -1/-1) is ratified a "
        "PARAMETER, not a distinct axis. Typing this slug `minus1-` would encode "
        "exactly the distinction that ruling rejects. Its live existence "
        "(batch-5 MERGE vs batch-6/7 KEEP vs the 2026-08-01 pointer clearing) is "
        "an open question about the AXIS, not about its name — out of walk scope.",
}

# Sense ratified by a Captain ruling, where the axis's own definition text does
# not decide it. The ruling outranks the stale definition.
RATIFIED_SENSE = {
    "rule:draw-second-card-trigger-plus1-counter": ("noun",
        "TRIAGE-BATCH-5 D12 — renamed FROM `-token` TO `-plus1-counter` precisely "
        "because its member is a counter, not a token ('the old slug's effect "
        "suffix did not match its only member'). The NAME is ratified; the "
        "definition text was never updated from the token era and is stale."),
}


def tokens(slug: str) -> list:
    return slug.split(":", 1)[-1].split("-")


def carries_counter_token(slug: str) -> bool:
    return any(t in COUNTER_TOKENS for t in tokens(slug))


# Each sense must show POSITIVE evidence of its own CR sense. Deriving noun as
# "whatever isn't verb" over-fires: `the counter's legal targets` is a
# nominalized verb, not a CR 122.1 marker, and a mere-proximity verb test
# misreads `a +1/+1 counter ... whenever you cast a noncreature spell`.

# VERB (CR 701.6): `counter(s)` taking a spell/ability as its grammatical
# OBJECT -- determiners and scope words may intervene, arbitrary text may not.
_VERB_OBJ = re.compile(
    r"\bcounters?\s+(?:(?:a|an|the|that|this|target|any|each|all|it)\s+)*"
    r"(?:[a-z-]+\s+){0,2}?(?:spell|ability|abilities)\b", re.I)
# `countered`/`countering` are verb-only -- CR 122.1's marker has no participle.
_VERB_INFLECTED = re.compile(r"\bcounter(?:ed|ing)\b", re.I)

# NOUN (CR 122.1): a marker. Either explicitly TYPED, or placed/removed/moved,
# or sitting `on`/`from` something.
_NOUN_TYPED = re.compile(
    r"(?:\+1/\+1|-1/-1|−1/−1|\b(?:charge|stun|oil|energy|loyalty|shield|"
    r"poison|lore|level|experience|ice)\b)[\s-]*counters?\b", re.I)
_NOUN_PLACED = re.compile(
    r"\b(?:place|places|placing|placed|put|puts|putting|remove|removes|removing|"
    r"removed|move|moves|moving|moved|add|adds|adding|added|distribute\w*|"
    r"proliferat\w*|double\w*|transfer\w*)\b[^.;]{0,40}?\bcounters?\b", re.I)
# A short participle gap is allowed: `counters accumulated on the permanent`,
# `counters it had been placing on ...` are the same marker relation.
_NOUN_ON = re.compile(r"\bcounters?\s+(?:[a-z-]+\s+){0,4}?(?:on|onto|from|off)\b", re.I)


def definition_sense(entry: dict) -> str:
    """Classify NOUN vs VERB from the DEFINITION text, never from the slug.

    NOUN (CR 122.1) = a marker placed on an object or player.
    VERB (CR 701.6) = countering a spell or ability.
    Returns 'noun', 'verb', or an 'ambiguous-*' value (which HALTS -- an axis
    whose own definition does not decide its sense is a Captain ruling).
    """
    d = entry.get("definition", "") or ""
    verb = bool(_VERB_OBJ.search(d) or _VERB_INFLECTED.search(d))
    noun = bool(_NOUN_TYPED.search(d) or _NOUN_PLACED.search(d) or _NOUN_ON.search(d))
    if verb and not noun:
        return "verb"
    if noun and not verb:
        return "noun"
    return "ambiguous-both" if verb else "ambiguous-neither"


def verb_conforms(slug: str) -> tuple:
    """§8a rule 1. Every counter token must be plural `counters` and be followed
    -- past any SCOPE tokens -- by something counterable."""
    tk = tokens(slug)
    for i, t in enumerate(tk):
        if t not in COUNTER_TOKENS:
            continue
        if t == "counter":
            return False, "singular `counter` in verb sense (§8a rule 1: BANNED)"
        j = i + 1
        while j < len(tk) and tk[j] in SCOPE_TOKENS:
            j += 1
        if j >= len(tk):
            return False, "`counters` is slug-final / bare -- nothing countered follows"
        if tk[j] not in COUNTERABLE:
            # restriction word binding to one, e.g. noncreature-spell
            if j + 1 < len(tk) and tk[j + 1] in COUNTERABLE:
                continue
            return False, f"token after `counters` is {tk[j]!r}, not a counterable object"
    return True, ""


def noun_conforms(slug: str) -> tuple:
    """§8a rule 2. Every counter token must be bound on the LEFT by a type word,
    `with`, or `any` -- OR by a ratified §7 scaling stat."""
    tk = tokens(slug)
    for i, t in enumerate(tk):
        if t not in COUNTER_TOKENS:
            continue
        if i == 0:
            return False, "counter token is slug-initial -- no left binder"
        # §7: `-scales-with-own-counters` / `-charge-counters`. The stat name is
        # itself ratified closed vocabulary, so it binds the counter token.
        if i >= 2 and f"{tk[i-1]}-{tk[i]}" in SCALING_STATS_WITH_COUNTER:
            continue
        left = tk[i - 1]
        if left not in LEFT_BINDERS:
            return False, f"left neighbour is {left!r}, not a type word / `with` / `any`"
    return True, ""


def main():
    cb = fcb.load_codebook()
    fcb.lint_or_halt(cb, "codebook")
    axes = cb["axes"]

    rows = []
    undecided = []
    for slug, entry in sorted(axes.items()):
        if entry.get("status") != "active":
            continue
        if not carries_counter_token(slug):
            continue
        ratified_sense = RATIFIED_SENSE.get(slug)
        if ratified_sense:
            sense, why_sense = ratified_sense
        else:
            sense = definition_sense(entry)
            why_sense = "derived from definition text"
        if sense.startswith("ambiguous"):
            # Collect rather than halt-on-first: the Captain needs the whole
            # set in one look, not one axis per run.
            undecided.append({"slug": slug, "sense": sense,
                              "definition": entry.get("definition", ""),
                              "members": len(entry.get("members", []))})
            continue

        if slug in RATIFIED_NAMES:
            ok, why = True, f"ratified name — {RATIFIED_NAMES[slug]}"
        else:
            ok, why = (verb_conforms(slug) if sense == "verb" else noun_conforms(slug))
        rows.append({
            "slug": slug, "sense": sense, "sense_basis": why_sense,
            "conforms": ok, "why": why,
            "members": len(entry.get("members", [])),
            "definition": entry.get("definition", ""),
        })

    conforming = [r for r in rows if r["conforms"]]
    non = [r for r in rows if not r["conforms"]]

    print(f"counter-bearing ACTIVE axes: {len(rows) + len(undecided)}")
    print(f"  sense-decidable from definition: {len(rows)}")
    print(f"  UNDECIDED (needs ruling)       : {len(undecided)}")
    print(f"  conforming     : {len(conforming)}")
    print(f"  NON-conforming : {len(non)}")
    print(f"  by sense       : noun={sum(1 for r in rows if r['sense']=='noun')} "
          f"verb={sum(1 for r in rows if r['sense']=='verb')}")
    print()
    print("--- NON-CONFORMING (the walk's worklist) " + "-" * 36)
    for r in non:
        print(f"[{r['sense']:4}] {r['slug']}  ({r['members']} members)")
        print(f"       reason: {r['why']}")
    print()
    print("--- CONFORMING (no action) " + "-" * 50)
    for r in conforming:
        print(f"[{r['sense']:4}] {r['slug']}  ({r['members']} members)")

    if undecided:
        print()
        print("--- UNDECIDED: definition does not decide the sense " + "-" * 25)
        for r in undecided:
            print(f"[{r['sense']}] {r['slug']}  ({r['members']} members)")
            print(f"       definition: {r['definition']}")

    out = fc.FOUNDRY_OUT_DIR / "cdr09_derivation.json"
    out.write_text(json.dumps({"rows": rows, "undecided": undecided},
                              indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {out}")

    if undecided:
        fc.halt(
            f"{len(undecided)} counter-bearing axis/axes cannot have their sense derived from "
            f"their own ratified definition (listed above). §8a requires sense to come from the "
            f"definition, so renaming these would be name-guessing — the exact corruption CDR-09 "
            f"exists to end. These are Captain rulings. The walk cannot proceed over them."
        )


if __name__ == "__main__":
    main()
