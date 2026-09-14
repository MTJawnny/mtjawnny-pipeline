"""Full-corpus DET pass job — `generate-samples` and `apply`, as operator flows.

## What this is

The two-phase operator S11 left in the legacy `foundry_det_pass` shell as review
orchestration: `generate-samples` (full hit lists, fixed-seed samples, the
review report and the hit cache — no codebook write) and `apply` (the verdict
gate, lattice re-expansion and cache reconciliation, backup, the A8 assertion
operation, the atomic write and its reports). S13 moved the flows, the CLI,
the NOTE lines and the locality-owner accounting here. Every printed line,
refusal, write order and output byte is the shell's.

`apply` MUTATES THE CODEBOOK. This module is not an installed script and must not
become one; discoverability of the mutation is not widened here.

## What this is NOT

* **Not DET semantics.** Pattern resolution, lattice expansion and instantiation,
  the cache reconciliation, the A8 application and the text matchers are
  `mtj_foundry.codebook_det_resolution`, `codebook_lattice`,
  `codebook_det_apply` and `mtg.text_match`. They are reached through the
  composition boundary's halting wrapper or its thin delegates.
* **Not a reader, writer, backup or process owner.** Every path, the corpus
  load, the facade codebook read, the corpus reference, the backup, the atomic
  write, the JSON writer and the historic `STOP — …` come from the boundary.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from mtj_foundry import codebook_det_apply as _det_apply

__all__ = ["DetPassContext", "axis_pattern_notes", "cmd_apply", "cmd_generate_samples",
           "det_locality_owner", "new_locality_stats", "run"]

_SPECIAL_SLUGS = {"rule:enters-tapped", "rule:enters-tapped-conditional",
                  "rule:imposes-enters-tapped"}


@dataclasses.dataclass(frozen=True)
class DetPassContext:
    description: str
    samples_report_path: Path
    samples_report_md_path: Path
    hits_cache_path: Path
    codebook_path: Path
    load_axis_patterns: Callable[[], tuple]
    load_corpus_gated: Callable[[], tuple]
    det_scan_texts: Callable[[dict], Any]
    full_oracle_text: Callable[[dict], str]
    assert_lattice_invariant: Callable[[dict], None]
    expand_lattice_pattern: Callable[[dict, dict], dict]
    compute_special_hits: Callable[..., tuple]
    compute_full_hits: Callable[..., list]
    quote_pattern_src: Callable[[dict], str]
    det_locality_owner: Callable[..., Any]
    lattice_parent_scopes: Callable[[dict], dict]
    halting: Callable[..., Any]
    stop: Callable[[str], None]
    write_json: Callable[[Path, Any], None]
    load_codebook: Callable[[], dict]
    corpus_ref_current: Callable[[], str]
    backup_codebook: Callable[[str], Any]
    write_codebook_atomic: Callable[[Path, dict, str], str]


def axis_pattern_notes(ruled_gaps, deferred_gaps, ruled_register: dict) -> list:
    """The NOTE lines for ratified patterns that receive no membership this run."""
    out = []
    for slug in sorted(ruled_gaps):
        out.append(f"NOTE: ratified pattern {slug!r} has no axis yet — "
                   f"{ruled_register[slug]}. Not applied this run.")
    for slug, st in sorted(deferred_gaps):
        out.append(f"NOTE: ratified pattern {slug!r} targets a {st!r} axis — "
                   f"not applied (only active axes receive DET membership).")
    return out


def new_locality_stats() -> dict:
    return {"OWNER": 0, "SPAN": 0, "AMBIGUOUS": 0, "UNRESOLVED": 0,
            "no card": 0}


def det_locality_owner(card, clause: str, stats: dict, resolve, owner_status: str):
    """The semantic owner coordinate for a DET clause, or None. NEVER RAISES.

    The "never raises" part is the ratified rule, not a convenience:
    `strict=False` means even a card whose CARDNAME canonicalisation reflows
    paragraphs yields an unaddressed assertion instead of killing a
    Captain-ratified write.
    """
    if card is None:
        stats["no card"] += 1
        return None
    r = resolve(card, clause, strict=False)
    stats[r["status"]] += 1
    return r["owner"] if r["status"] == owner_status else None


def cmd_generate_samples(ctx: DetPassContext) -> None:
    axis_patterns, prefilter_patterns, lattice_rows = ctx.load_axis_patterns()
    cards, _, gated_out = ctx.load_corpus_gated()
    print(f"corpus: {len(cards)} gate-passing cards ({gated_out} gated out)")
    texts = {oid: ctx.det_scan_texts(c) for oid, c in cards.items()}

    # Lattice rows expand into ordinary per-axis entries carrying their own
    # hits and their own proving clauses, so everything downstream is uniform.
    lattice_quotes = {}
    for p in lattice_rows:
        ctx.assert_lattice_invariant(p)
        expanded = ctx.expand_lattice_pattern(p, cards)
        print(f"lattice pattern_index={p['pattern_index']}: "
              f"{len(expanded)} axes, "
              f"{sum(len(v) for v in expanded.values())} memberships")
        for slug, hits in sorted(expanded.items()):
            lattice_quotes[slug] = hits
            axis_patterns.append(dict(
                p, resolved_slug=slug, is_lattice=True,
                pattern=f"(lattice) {slug}",
                # per-AXIS count, not the row's family total. Reporting 2,653
                # against each of 24 axes would be a carried-forward count
                # wearing a per-axis label.
                corpus_hits=len(hits)))

    full_hits = {}
    samples_report = {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                      "n_axis_patterns": len(axis_patterns), "patterns": []}
    md_lines = ["# DET pass -- sample-sheet review report", ""]

    for p in axis_patterns:
        slug = p["resolved_slug"]
        if p.get("is_lattice"):
            hits = sorted(lattice_quotes[slug])
        elif slug in _SPECIAL_SLUGS:
            hits, _ = ctx.compute_special_hits(slug, texts, cards)
        else:
            hits = ctx.compute_full_hits(p["pattern"], texts)
        full_hits[slug] = hits
        seed = p["seed"]
        rng = random.Random(seed)
        sample_ids = rng.sample(hits, min(20, len(hits))) if hits else []

        sample_rows = []
        for oid in sample_ids:
            c = cards[oid]
            text = ctx.full_oracle_text(c)
            sample_rows.append({"oracle_id": oid, "name": c.get("name", ""), "oracle_text": text})

        entry = {
            "slug": slug, "pattern": p["pattern"], "seed": seed,
            "def_anchor": p["def_anchor"], "corpus_hits_now": len(hits),
            "corpus_hits_at_ratification": p["corpus_hits"], "sample": sample_rows,
        }
        samples_report["patterns"].append(entry)

        md_lines.append(f"## {slug}")
        md_lines.append(f"pattern: `{p['pattern']}`")
        md_lines.append(f"definition: {p['def_anchor']}")
        md_lines.append(f"hits now: {len(hits)} (at ratification: {p['corpus_hits']})")
        md_lines.append(f"sample size: {len(sample_rows)} (seed {seed})")
        md_lines.append("")
        for row in sample_rows:
            md_lines.append(f"- **{row['name']}** (`{row['oracle_id']}`)")
            for line in row["oracle_text"].splitlines():
                md_lines.append(f"    {line}")
        md_lines.append("")

    ctx.write_json(ctx.samples_report_path, samples_report)
    ctx.write_json(ctx.hits_cache_path, full_hits)
    ctx.samples_report_md_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"wrote {ctx.samples_report_path}")
    print(f"wrote {ctx.hits_cache_path} (full hit lists, {sum(len(v) for v in full_hits.values())} total oracle_ids)")
    print(f"wrote {ctx.samples_report_md_path} for review")
    print(f"\n{len(axis_patterns)} patterns need per-sample verification against their def_anchor before `apply`.")


def cmd_apply(verdicts_path: str, ctx: DetPassContext) -> None:
    if not ctx.hits_cache_path.exists():
        ctx.stop(f"{ctx.hits_cache_path} not found -- run generate-samples first")
    verdicts = json.loads(Path(verdicts_path).read_text())
    axis_patterns, _, lattice_rows = ctx.load_axis_patterns()
    full_hits = json.loads(ctx.hits_cache_path.read_text())

    # Re-expand the lattice rather than trusting the cache for QUOTES: the
    # cache holds oracle_ids only, and a rule-derived assertion needs the
    # clause that proves its own axis. Re-deriving also means a lattice whose
    # code changed since generate-samples cannot silently apply stale hits --
    # the reconciliation below halts on any disagreement.
    cards_for_lattice, _, _ = ctx.load_corpus_gated()
    lattice_quotes = {}
    for p in lattice_rows:
        ctx.assert_lattice_invariant(p)
        for slug, hits in ctx.expand_lattice_pattern(p, cards_for_lattice).items():
            lattice_quotes[slug] = hits
            axis_patterns.append(dict(p, resolved_slug=slug, is_lattice=True,
                                      pattern=f"(lattice) {slug}"))
    disagreement = _det_apply.lattice_cache_disagreement(lattice_quotes, full_hits)
    if disagreement:
        ctx.stop(disagreement)

    missing_verdicts = [p["resolved_slug"] for p in axis_patterns if p["resolved_slug"] not in verdicts]
    if missing_verdicts:
        ctx.stop(f"no verdict recorded for {len(missing_verdicts)} pattern(s): {missing_verdicts} -- "
                 f"refusing to apply partial verdicts")

    failed = [slug for slug, v in verdicts.items() if v.get("verdict") != "PASS"]
    if failed:
        print(f"HALT: {len(failed)} pattern(s) FAILED sample verification -- ZERO codebook.json writes:")
        for slug in failed:
            print(f"  {slug}: {verdicts[slug]}")
        ctx.stop("DET pass sample-sheet gate failed for at least one pattern; fix the pattern and re-run "
                 "generate-samples before attempting apply again")

    print(f"all {len(axis_patterns)} patterns PASSED their sample-sheet gate. Applying DET-derived membership...")

    # Post-migration the codebook is foundry-codebook/2, so a DET refresh is an
    # assertion operation, not a list swap (A8): it drops ONLY its own
    # rule-derived assertions and merges the new ones back, leaving any human
    # or llm assertion on the same member untouched.
    cb = ctx.load_codebook()
    axes = cb["axes"]
    corpus_ref = ctx.corpus_ref_current()

    cards, _, _ = ctx.load_corpus_gated()
    texts = {oid: ctx.det_scan_texts(c) for oid, c in cards.items()}

    ctx.backup_codebook("pre-det-pass")

    # Virtual-node instantiation, grammar sec.11.2 -- the semantics are
    # `codebook_det_apply.instantiate_lattice_axes`.
    parent_scopes = ctx.lattice_parent_scopes(axes)
    instantiated = ctx.halting(_det_apply.instantiate_lattice_axes, axes,
                               lattice_quotes, parent_scopes)
    if instantiated:
        print(f"instantiated {len(instantiated)} virtual node(s) under "
              f"grammar sec.11.2")

    # SEMANTIC LOCALITY (FL-2, ratified 2026-08-13). New rule-derived output is
    # born addressed; an address is optional by ratification, so a quote that
    # resolves to SPAN, AMBIGUOUS or UNRESOLVED is written WITHOUT an address
    # rather than refused. Counted by outcome and reported below.
    locality_stats = new_locality_stats()

    def resolve_owner(oid, clause):
        return ctx.det_locality_owner(cards.get(oid), clause, locality_stats)

    applied = ctx.halting(_det_apply.apply_axis_patterns, axes, axis_patterns,
                          full_hits, lattice_quotes, texts, corpus_ref,
                          quote_pattern_src=lambda p: ctx.quote_pattern_src(p),
                          resolve_owner=resolve_owner)

    digest = ctx.write_codebook_atomic(ctx.codebook_path, cb, "codebook.json")
    print(f"wrote {ctx.codebook_path}")
    print(f"  sha256={digest}")
    for slug, old_n, new_n, dropped in applied:
        print(f"  {slug}: {old_n} -> {new_n} members ({dropped} dropped with no remaining assertion)")

    # ADDED AND UNADDRESSED REPORTED SEPARATELY, never as a coverage percentage
    # standing in for both.
    total = sum(locality_stats.values())
    if total:
        print(f"\nsemantic locality on the {total} rule-derived assertion(s) written:")
        print(f"  addressed (OWNER)   : {locality_stats['OWNER']}")
        for k in ("SPAN", "AMBIGUOUS", "UNRESOLVED", "no card"):
            if locality_stats[k]:
                print(f"  unaddressed ({k:10}): {locality_stats[k]}")
        print("  unaddressed assertions are fully valid card-level evidence "
              "(ratified 2026-08-13);\n  they simply cannot prove same-unit "
              "co-occurrence. Nothing was refused for lacking an address.")


def build_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("generate-samples")
    p_apply = sub.add_parser("apply")
    p_apply.add_argument("--verdicts", required=True)
    return parser


def run(argv, ctx: DetPassContext) -> None:
    args = build_parser(ctx.description).parse_args(argv)
    if args.command == "generate-samples":
        cmd_generate_samples(ctx)
    elif args.command == "apply":
        cmd_apply(args.verdicts, ctx)
