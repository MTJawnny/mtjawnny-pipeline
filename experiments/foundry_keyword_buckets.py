#!/usr/bin/env python3
"""Keyword-bucket extraction DET job (CORPUS-PASS-PLAN.md step 2, ratified
MASTER-HANDOFF-ADDENDUM-3.md sec.2/4, 2026-07-29 session). Walks CR 702
(Keyword Abilities) in the local mtg-comprehensive-rules.md and classifies
every keyword's ability class mechanically from the CR's own first-line
characterization ("[Keyword] is a static/triggered/activated/evasion/
characteristic-defining ability."). Every classification cites the exact
CR sub-rule it came from. Verify-or-drop: no recall, no guessing -- a
keyword whose CR text does not state one of the closed classes is bucketed
"unclassified" with the raw quote, never force-fit.

This is a DET job: zero tokens, fully mechanical regex extraction over the
CR markdown. It does not touch codebook.json and is not gated on anything.

Usage: python3 experiments/foundry_keyword_buckets.py
"""
import sys
import re
import json
from pathlib import Path
from datetime import date

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402
import foundry_cr as fcr  # noqa: E402

# The CR is rules text, not Scryfall card data, so the "no card data in git"
# rule never applied to it -- and as of the 2026-08-07 refresh it is TRACKED IN
# THIS REPO rather than referenced across into the gitignored site `docs/`,
# which means a future refresh is a diff instead of an act of faith. Its
# location and its formatting are both owned by `foundry_cr`.
CR_PATH = fcr.CR_PATH

OUT_PATH = fc.FOUNDRY_OUT_DIR / "keyword-buckets.json"
REPORT_PATH = fc.FOUNDRY_OUT_DIR / "keyword-buckets_report.md"


# ---------------------------------------------------------------------------
# S6 — THE DERIVATION NOW LIVES IN THE PERMANENT CR SUBSTRATE
# ---------------------------------------------------------------------------
# Migration slice 6 moved CR 702 entry/sub-rule parsing, the closed bucket
# vocabulary, `classify_entry`, `slugify` and the pure `build_registry()`
# derivation into `mtj_foundry.mtg.cr.keyword_buckets`. NO DUPLICATE
# CLASSIFICATION OR REGISTRY IMPLEMENTATION REMAINS HERE.
#
# What stays is the operator half a library may not own: the output paths, the
# run-metadata envelope, the file write, the Markdown report and the CLI. That
# split is why the permanent derivation is comparable run-to-run at all -- the
# `generated` date lives out here, not inside the payload.
#
# `expand_and_split` was dead at the accepted base and its accepted disposition
# is NOT PROMOTED, so it is gone rather than carried into L2.
from mtj_foundry.mtg.cr import keyword_buckets as _buckets  # noqa: E402

CLOSED_BUCKETS = _buckets.CLOSED_BUCKETS
TRIGGER_FAMILY_PATTERNS = _buckets.TRIGGER_FAMILY_PATTERNS
CASTING_MODIFIER_PATTERNS = _buckets.CASTING_MODIFIER_PATTERNS
HEADER_RE = _buckets.HEADER_RE
SUBRULE_RE = _buckets.SUBRULE_RE

slugify = _buckets.slugify
split_entries = _buckets.split_entries
parse_subrules = _buckets.parse_subrules
classify_entry = _buckets.classify_entry


def load_cr_text():
    """The normalized CR, from the permanent owner."""
    return _buckets.cr_text(CR_PATH)


def find_cr_date(text):
    """The CR effective date, from the permanent owner."""
    return _buckets.cr_date(text)


def build_registry(text=None):
    """The pure derivation, with the legacy process boundary restored."""
    try:
        return _buckets.build_registry(text)
    except _buckets.KeywordBucketError as exc:
        fc.halt(str(exc))


def main():
    text = load_cr_text()
    cr_date = find_cr_date(text)
    reg = build_registry(text)

    keywords = reg["keywords"]
    verify_or_drop = reg["verify_or_drop"]
    trigger_gaps = reg["trigger_gaps"]
    casting_modifier_hits = reg["casting_modifier_hits"]
    bucket_counts = reg["bucket_counts"]
    entries = range(reg["n_entries"])

    out = {
        "schema": "foundry-keyword-buckets/1",
        "cr_version_date": cr_date,
        "cr_source_path": str(CR_PATH),
        "generated": date.today().isoformat(),
        "ruling_basis": "CORPUS-PASS-PLAN.md step 2 / MASTER-HANDOFF-ADDENDUM-3.md sec.2,4",
        "closed_buckets": reg["closed_buckets"],
        "note": (
            "Base 'class' is mechanically extracted from the CR's own first-class "
            "statement per keyword (verify-or-drop: 'unclassified'/'ambiguous-card-dependent' "
            "means the CR text does not commit to one fixed class -- never guessed). "
            "'casting_modifier_heuristic' is a SEPARATE, non-CR-anchored regex heuristic "
            "flag (not a class) -- addendum-3's assumption that casting-modifier is a "
            "peer of static/triggered/activated does not hold: CR classifies Flash, "
            "Convoke, Kicker, etc. as ordinary ability classes (mostly static) whose "
            "TEXT happens to modify casting; this field surfaces that distinction for "
            "Captain rather than silently folding it into the addendum's original 5-bucket "
            "assumption. 'death-trigger' is used for the CR-700.4 graveyard-from-battlefield "
            "family per sec.13 D-1 of CODEBOOK-NAMING-GRAMMAR.md, NOT the literal 'dies' "
            "value printed in that same document's sec.2 table -- see report for the flagged "
            "internal inconsistency."
        ),
        "keywords": keywords,
    }

    fc.write_json(OUT_PATH, out)

    report_lines = [
        "# Keyword-bucket extraction report", "",
        f"Run: {date.today().isoformat()} against CR effective {cr_date} ({CR_PATH})", "",
        f"Total keyword entries parsed: {len(keywords)} (from {len(entries)} CR 702 headers, "
        "702.145 Daybound-and-Nightbound split into 2)", "",
        "## Bucket counts", "",
    ]
    for b in CLOSED_BUCKETS:
        report_lines.append(f"- `{b}`: {bucket_counts[b]}")
    report_lines += ["", "## Verify-or-drop (no fixed CR class stated -- do NOT force-fit)", ""]
    for slug in verify_or_drop:
        k = keywords[slug]
        report_lines.append(f"- `{slug}` ({k['cr_number']}, class={k['class']}): \"{k['class_evidence']}\"")
    report_lines += ["", "## Triggered keywords with no closed-vocabulary trigger-family match", "",
                      "(DELIVERY slot per CODEBOOK-NAMING-GRAMMAR.md sec.2; these need either a new closed-vocab entry or per-keyword ruling)", ""]
    for slug in trigger_gaps:
        k = keywords[slug]
        report_lines.append(f"- `{slug}` ({k['class_cr_citation']}): \"{k['class_evidence']}\"")
    report_lines += ["", "## casting_modifier_heuristic hits (non-CR-anchored, flagged for Captain review)", ""]
    for slug in casting_modifier_hits:
        k = keywords[slug]
        report_lines.append(f"- `{slug}` (base class={k['class']}, {k['class_cr_citation']}): \"{k['casting_modifier_evidence']}\"")
    report_lines += ["", "## Hybrid keywords with unparsed components", ""]
    for slug, k in sorted(keywords.items()):
        if k["class"] == "hybrid" and not k["hybrid_components"]:
            report_lines.append(f"- `{slug}` ({k['class_cr_citation']}): \"{k['class_evidence']}\"")

    REPORT_PATH.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_PATH} ({len(keywords)} keywords)")
    print(f"wrote {REPORT_PATH}")
    print(f"bucket counts: {bucket_counts}")
    print(f"verify_or_drop: {len(verify_or_drop)}  trigger_gaps: {len(trigger_gaps)}  casting_modifier_hits: {len(casting_modifier_hits)}")


if __name__ == "__main__":
    main()
