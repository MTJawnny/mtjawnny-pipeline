"""Keyword-bucket job — the artifact envelope, the Markdown report, the summary.

## What this is

The operator composition of the keyword-bucket DET job, moved by S13 out of the
legacy `foundry_keyword_buckets` shell. Its artifact, `keyword-buckets.json`, is
read at run time by three Gate 2 guards, so the bytes it describes are live.

Three pure functions:

* `envelope` — the run-metadata document written around the registry;
* `report` — the Markdown report text;
* `summary` — the lines the job prints.

Key order, wording and line shapes are the shell's, character for character.

## What this is NOT

* **Not the derivation.** CR 702 parsing, the closed bucket vocabulary and the
  registry itself are `mtj_foundry.mtg.cr.keyword_buckets` (S6). This module is
  handed a registry and never builds one.
* **Not a writer, and not a layout owner.** The output paths, the file writes,
  the run date, printing and the `STOP — …` boundary stay in the shell. Every
  path here is a label passed in; nothing is opened, created or derived from a
  root.
"""

from __future__ import annotations

from mtj_foundry.mtg.cr import keyword_buckets as _buckets

__all__ = ["RULING_BASIS", "SCHEMA", "envelope", "report", "summary"]

SCHEMA = "foundry-keyword-buckets/1"
RULING_BASIS = "CORPUS-PASS-PLAN.md step 2 / MASTER-HANDOFF-ADDENDUM-3.md sec.2,4"

_NOTE = (
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
)


def envelope(registry: dict, cr_date: str, cr_source_path: str, generated: str) -> dict:
    """The document written to `keyword-buckets.json`, in its contracted key order."""
    return {
        "schema": SCHEMA,
        "cr_version_date": cr_date,
        "cr_source_path": cr_source_path,
        "generated": generated,
        "ruling_basis": RULING_BASIS,
        "closed_buckets": registry["closed_buckets"],
        "note": _NOTE,
        "keywords": registry["keywords"],
    }


def report(registry: dict, cr_date: str, cr_source_path: str, run_date: str) -> str:
    """The Markdown report, including its single trailing newline."""
    keywords = registry["keywords"]
    bucket_counts = registry["bucket_counts"]
    lines = [
        "# Keyword-bucket extraction report", "",
        f"Run: {run_date} against CR effective {cr_date} ({cr_source_path})", "",
        f"Total keyword entries parsed: {len(keywords)} (from {registry['n_entries']} CR 702 headers, "
        "702.145 Daybound-and-Nightbound split into 2)", "",
        "## Bucket counts", "",
    ]
    for b in _buckets.CLOSED_BUCKETS:
        lines.append(f"- `{b}`: {bucket_counts[b]}")
    lines += ["", "## Verify-or-drop (no fixed CR class stated -- do NOT force-fit)", ""]
    for slug in registry["verify_or_drop"]:
        k = keywords[slug]
        lines.append(f"- `{slug}` ({k['cr_number']}, class={k['class']}): \"{k['class_evidence']}\"")
    lines += ["", "## Triggered keywords with no closed-vocabulary trigger-family match", "",
              "(DELIVERY slot per CODEBOOK-NAMING-GRAMMAR.md sec.2; these need either a new closed-vocab entry or per-keyword ruling)", ""]
    for slug in registry["trigger_gaps"]:
        k = keywords[slug]
        lines.append(f"- `{slug}` ({k['class_cr_citation']}): \"{k['class_evidence']}\"")
    lines += ["", "## casting_modifier_heuristic hits (non-CR-anchored, flagged for Captain review)", ""]
    for slug in registry["casting_modifier_hits"]:
        k = keywords[slug]
        lines.append(f"- `{slug}` (base class={k['class']}, {k['class_cr_citation']}): \"{k['casting_modifier_evidence']}\"")
    lines += ["", "## Hybrid keywords with unparsed components", ""]
    for slug, k in sorted(keywords.items()):
        if k["class"] == "hybrid" and not k["hybrid_components"]:
            lines.append(f"- `{slug}` ({k['class_cr_citation']}): \"{k['class_evidence']}\"")
    return "\n".join(lines) + "\n"


def summary(out_path, report_path, registry: dict) -> list:
    """The lines the job prints after both writes."""
    return [
        f"wrote {out_path} ({len(registry['keywords'])} keywords)",
        f"wrote {report_path}",
        f"bucket counts: {registry['bucket_counts']}",
        f"verify_or_drop: {len(registry['verify_or_drop'])}  "
        f"trigger_gaps: {len(registry['trigger_gaps'])}  "
        f"casting_modifier_hits: {len(registry['casting_modifier_hits'])}",
    ]
