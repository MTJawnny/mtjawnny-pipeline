#!/usr/bin/env python3
"""Full-corpus DET pass (CORPUS-PASS-PLAN.md step 4), executed per Captain's
2026-08-01 trigger. Every ratified pattern in docs/det-patterns-v2.json (v2
superseded v1 2026-08-01, mid-pass, per two sample-gate catches -- see
det-patterns-v2.json's v2_changelog) that maps to a real active codebook
axis (39 of 44 ratified; the other 5 are Lane-1 pre-filters with no axis of
their own) gets its FULL corpus hit list computed against the Gate
#0-filtered corpus using the DET preprocessing standard
(foundry_common.det_scan_texts -- CARDNAME canonicalization + modal-mode
splitting), then a fixed-seed 20-hit sample (seed = the pattern's own
recorded seed, det-patterns-v2.json's pattern_index-derived value) for
Captain's/Claude's per-pattern verification per the standing condition
(det-patterns-v2.json's own "standing_condition": ANY sample row failing
its axis definition halts the pass before provenance writes).

Two-phase, matching the standing condition's own "gate before write" shape:
  generate-samples -- computes hit lists + fixed-seed samples, writes a
                       review report (no codebook.json mutation). Zero spend.
  apply             -- reads verdicts (hand-authored after reviewing the
                       samples report), and ONLY IF EVERY pattern passed,
                       writes DET-derived membership to codebook.json. Under
                       foundry-codebook/2 that means: drop this pass's own
                       rule-derived assertions and merge the freshly computed
                       ones back, each carrying its matched clause as evidence
                       (A8). DET's premise is "decidable by pattern, no
                       judgment call," so it supersedes the necessarily-partial
                       sampling-era rule-derived set -- but it has no authority
                       over a human or llm assertion on the same card, and
                       never touches one. ANY failing verdict halts with zero
                       codebook.json writes, full stop.

Run:
  python3 experiments/foundry_det_pass.py generate-samples
  # review experiments/out/foundry/det_pass_samples_report.json /.md
  python3 experiments/foundry_det_pass.py apply --verdicts <path to verdicts json>
"""
import sys
import json
import random
import argparse
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402
import foundry_codebook as fcb  # noqa: E402
import foundry_det_patterns_probe as probe  # noqa: E402
import re  # noqa: E402

DET_PATTERNS_PATH = REPO_ROOT / "docs" / "det-patterns-v2.json"
CODEBOOK_PATH = fc.FOUNDRY_OUT_DIR / "codebook.json"
SAMPLES_REPORT_PATH = fc.FOUNDRY_OUT_DIR / "det_pass_samples_report.json"
SAMPLES_REPORT_MD_PATH = fc.FOUNDRY_OUT_DIR / "det_pass_samples_report.md"
HITS_CACHE_PATH = fc.FOUNDRY_OUT_DIR / "det_pass_full_hits.json"
BATCH_LABEL = "det-pass-1"


# Ratified AXIS-BEARING patterns that legitimately have no axis yet, each
# with the Captain ruling that authorises the gap. Anything ratified,
# axis-bearing and axis-less that is NOT listed here HALTS.
#
# EMPTY THIS LIST as session 4 creates each axis — a stale entry here
# re-opens exactly the hole this guard closes.
RULED_AXISLESS_PATTERNS = {
    "rule:cant-be-blocked-by-power":
        "ADD-01 Option A, Captain-ruled 2026-08-01 — DET path, session 4 "
        "(57 corpus hits)",
    "rule:cant-be-blocked-except-by-count":
        "ADD-01 Option A, Captain-ruled 2026-08-01 — DET path, session 4 "
        "(10 corpus hits)",
    "rule:cant-be-blocked-as-long-as-state":
        "ADD-01 Option A, Captain-ruled 2026-08-01 — DET path, session 4 "
        "(18 corpus hits)",
}


def load_axis_patterns():
    # Deliberately a raw json.load rather than the schema-checking /2 loader:
    # this reads axis STATUS only, never membership, so it is correct against
    # /1 and /2 alike -- and the migration writer calls it while the live file
    # is still /1.
    det = json.loads(DET_PATTERNS_PATH.read_text())
    cb = json.loads(CODEBOOK_PATH.read_text())
    active = {s for s, e in cb["axes"].items() if e.get("status") == "active"}
    axis_patterns, prefilter_patterns = [], []
    ruled_gaps, deferred_gaps = [], []
    for p in det["patterns"]:
        if p["status"] != "ratified":
            continue
        slug = fc.pattern_slug(p)

        if fc.is_prefilter_pattern(p):
            prefilter_patterns.append(p)          # declared a pre-filter
            continue
        if slug in active:
            axis_patterns.append(dict(p, resolved_slug=slug))
            continue

        # Axis-bearing, ratified, and no ACTIVE axis to apply to. This used
        # to fall through to prefilter_patterns silently, so the pattern
        # never ran, never wrote membership, and never reported.
        record = cb["axes"].get(slug)
        if record is not None and record.get("status") != "active":
            deferred_gaps.append((slug, record.get("status")))
            prefilter_patterns.append(p)
            continue
        if slug in RULED_AXISLESS_PATTERNS:
            ruled_gaps.append(slug)
            prefilter_patterns.append(p)
            continue
        fc.halt(
            f"ratified axis-bearing DET pattern {slug!r} has no axis in "
            f"codebook.json at all.\n"
            f"  It is not marked '(pre-filter)' in det-patterns-v2.json, so it "
            f"is expected to decide an axis's membership.\n"
            f"  Silently demoting it to the prefilter list is what hid three "
            f"ratified patterns for weeks.\n"
            f"  Resolve one of these ways, then re-run:\n"
            f"    - create the axis (the pattern is genuinely axis-bearing), or\n"
            f"    - mark the slug '(pre-filter)' in docs/det-patterns-v2.json "
            f"(it is a Lane-1 net, not a classifier), or\n"
            f"    - add it to RULED_AXISLESS_PATTERNS here WITH the Captain "
            f"ruling that authorises the gap."
        )

    for slug in sorted(ruled_gaps):
        print(f"NOTE: ratified pattern {slug!r} has no axis yet — "
              f"{RULED_AXISLESS_PATTERNS[slug]}. Not applied this run.")
    for slug, st in sorted(deferred_gaps):
        print(f"NOTE: ratified pattern {slug!r} targets a {st!r} axis — "
              f"not applied (only active axes receive DET membership).")
    return axis_patterns, prefilter_patterns


def compute_full_hits(pattern_src: str, texts: dict) -> list:
    pat = re.compile(pattern_src, re.I)
    return sorted(oid for oid, text_list in texts.items() if any(pat.search(t) for t in text_list))


# rule:enters-tapped, rule:enters-tapped-conditional, and rule:imposes-
# enters-tapped are NOT plain-regex patterns -- their det-patterns-v1.json
# "pattern" field is either the base regex that STILL needs the G2 subject-
# check applied on top (enters-tapped/-conditional), or, for imposes-
# enters-tapped, a DOCUMENTATION STRING ("[same base pattern as ...] +
# subject classified 'imposed'..."), not a compilable regex at all --
# compiling it literally yields 0 hits, not an error, so this would have
# silently written an EMPTY membership list for that axis without this
# special-casing. Caught during generate-samples' first run (hits_now=0
# vs corpus_hits_at_ratification=24), fixed before any apply.
_ENTERS_TAPPED_BASE_SLUG = "rule:enters-tapped (unconditional)"
_ENTERS_TAPPED_COND_SLUG = "rule:enters-tapped-conditional"
_IMPOSES_SLUG = "rule:imposes-enters-tapped"


def _base_pattern_src(slug_key: str) -> str:
    for s, pattern_src, _ in probe.PATTERNS:
        if s == slug_key:
            return pattern_src
    fc.halt(f"could not find base pattern source for {slug_key!r} in foundry_det_patterns_probe.PATTERNS")


# The pattern whose match IS the evidence clause for an axis. For the three
# enters-tapped-family axes that is NOT the det-patterns-v2 "pattern" field:
# membership there is decided by compute_special_hits() running the probe's
# real G2 subject split on a BASE pattern, so the clause has to come from that
# base pattern. This mapping is the single place that fact is written down --
# the migration writer and any future DET pass both read it from here rather
# than re-deriving it.
_QUOTE_BASE_SLUG = {
    "rule:enters-tapped": _ENTERS_TAPPED_BASE_SLUG,
    "rule:enters-tapped-conditional": _ENTERS_TAPPED_COND_SLUG,
    "rule:imposes-enters-tapped": _ENTERS_TAPPED_BASE_SLUG,
}


def quote_pattern_src(p: dict) -> str:
    slug = p["resolved_slug"]
    if slug in _QUOTE_BASE_SLUG:
        return _base_pattern_src(_QUOTE_BASE_SLUG[slug])
    return p["pattern"]


def matched_clause(compiled, text_list: list):
    """The oracle-text clause a ratified pattern matched on this card -- the
    evidence quote for a rule-derived assertion (R2). Returns None when the
    pattern matches none of the card's DET scan texts, which for a card on
    that pattern's own hit list means the hit list and the pattern have
    drifted apart; every caller treats that as a halt, never a skip."""
    for text in text_list:
        m = compiled.search(text)
        if m and m.group(0).strip():
            return m.group(0)
    return None


def compute_special_hits(resolved_slug: str, texts: dict, cards: dict) -> tuple:
    """Returns (self_hits, imposed_rows) for the 3 enters-tapped-family
    axes; reuses the REAL G2 logic from foundry_det_patterns_probe.py
    rather than re-implementing it."""
    base_hits = compute_full_hits(_base_pattern_src(_ENTERS_TAPPED_BASE_SLUG), texts)
    self_hits, imposed_rows = probe._enters_tapped_subject_split(base_hits, texts, cards)
    if resolved_slug == "rule:enters-tapped":
        return sorted(self_hits), imposed_rows
    if resolved_slug == "rule:enters-tapped-conditional":
        cond_hits = compute_full_hits(_base_pattern_src(_ENTERS_TAPPED_COND_SLUG), texts)
        cond_self, _ = probe._enters_tapped_subject_split(cond_hits, texts, cards)
        return sorted(cond_self), imposed_rows
    if resolved_slug == "rule:imposes-enters-tapped":
        return sorted(row["oracle_id"] for row in imposed_rows), imposed_rows
    raise ValueError(resolved_slug)


def cmd_generate_samples():
    axis_patterns, prefilter_patterns = load_axis_patterns()
    cards, _, gated_out = fc.load_corpus_gated()
    print(f"corpus: {len(cards)} gate-passing cards ({gated_out} gated out)")
    texts = {oid: fc.det_scan_texts(c) for oid, c in cards.items()}

    full_hits = {}
    samples_report = {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                       "n_axis_patterns": len(axis_patterns), "patterns": []}
    md_lines = ["# DET pass -- sample-sheet review report", ""]

    special_slugs = {"rule:enters-tapped", "rule:enters-tapped-conditional", "rule:imposes-enters-tapped"}
    for p in axis_patterns:
        slug = p["resolved_slug"]
        if slug in special_slugs:
            hits, _ = compute_special_hits(slug, texts, cards)
        else:
            hits = compute_full_hits(p["pattern"], texts)
        full_hits[slug] = hits
        seed = p["seed"]
        rng = random.Random(seed)
        sample_ids = rng.sample(hits, min(20, len(hits))) if hits else []

        sample_rows = []
        for oid in sample_ids:
            c = cards[oid]
            text = fc.full_oracle_text(c)
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

    fc.write_json(SAMPLES_REPORT_PATH, samples_report)
    fc.write_json(HITS_CACHE_PATH, full_hits)
    SAMPLES_REPORT_MD_PATH.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"wrote {SAMPLES_REPORT_PATH}")
    print(f"wrote {HITS_CACHE_PATH} (full hit lists, {sum(len(v) for v in full_hits.values())} total oracle_ids)")
    print(f"wrote {SAMPLES_REPORT_MD_PATH} for review")
    print(f"\n{len(axis_patterns)} patterns need per-sample verification against their def_anchor before `apply`.")


def cmd_apply(verdicts_path: str):
    if not HITS_CACHE_PATH.exists():
        fc.halt(f"{HITS_CACHE_PATH} not found -- run generate-samples first")
    verdicts = json.loads(Path(verdicts_path).read_text())
    axis_patterns, _ = load_axis_patterns()
    full_hits = json.loads(HITS_CACHE_PATH.read_text())

    missing_verdicts = [p["resolved_slug"] for p in axis_patterns if p["resolved_slug"] not in verdicts]
    if missing_verdicts:
        fc.halt(f"no verdict recorded for {len(missing_verdicts)} pattern(s): {missing_verdicts} -- "
                 f"refusing to apply partial verdicts")

    failed = [slug for slug, v in verdicts.items() if v.get("verdict") != "PASS"]
    if failed:
        print(f"HALT: {len(failed)} pattern(s) FAILED sample verification -- ZERO codebook.json writes:")
        for slug in failed:
            print(f"  {slug}: {verdicts[slug]}")
        fc.halt("DET pass sample-sheet gate failed for at least one pattern; fix the pattern and re-run "
                 "generate-samples before attempting apply again")

    print(f"all {len(axis_patterns)} patterns PASSED their sample-sheet gate. Applying DET-derived membership...")

    # Post-migration the codebook is foundry-codebook/2, so a DET refresh is an
    # assertion operation, not a list swap (A8): it drops ONLY its own
    # rule-derived assertions and merges the new ones back, leaving any human
    # or llm assertion on the same member untouched. A member survives exactly
    # as long as some assertion still supports it. The pre-migration behaviour
    # -- overwrite the whole member list, paste the old list into a history
    # note -- would now silently delete Captain-ratified provenance.
    cb = fcb.load_codebook(CODEBOOK_PATH)
    axes = cb["axes"]
    corpus_ref = fcb.corpus_ref_current()

    cards, _, _ = fc.load_corpus_gated()
    texts = {oid: fc.det_scan_texts(c) for oid, c in cards.items()}

    fcb.backup_codebook("pre-det-pass")
    applied = []
    for p in axis_patterns:
        slug = p["resolved_slug"]
        e = axes[slug]
        before_n = len(fcb.member_ids(e))
        removal = fcb.remove_det_assertions(e)
        source_ref = f"{fcb.DET_SOURCE_REF_PREFIX}{p['pattern_index']}"
        compiled = re.compile(quote_pattern_src(p), re.I)
        for oid in full_hits[slug]:
            if oid not in texts:
                fc.halt(f"DET hit {slug}/{oid} is not in the Gate #0 corpus — hit list and corpus "
                        f"disagree; nothing written")
            clause = matched_clause(compiled, texts[oid])
            if clause is None:
                fc.halt(f"DET hit {slug}/{oid} produced no matched clause on re-scan — the recorded hit "
                        f"list and the ratified pattern disagree; nothing written")
            fcb.merge_assertion(e, oid, fcb.build_assertion(
                "rule-derived", source_ref, clause, corpus_ref, "quoted"))
        e["source"] = "DET"
        after_n = len(fcb.member_ids(e))
        e["history"] = list(e["history"]) + [{
            "batch": BATCH_LABEL, "action": "det_membership_applied",
            # Counts only. The old note embedded the entire previous member
            # list verbatim; under /2 that would inline a wall of member
            # objects into a history note for no audit value the manifest and
            # backups do not already provide.
            "note": (f"Full-corpus DET pass (docs/det-patterns-v2.json pattern_index={p['pattern_index']}, "
                     f"seed={p['seed']}, sample-sheet verified). rule-derived assertions replaced under "
                     f"{source_ref}: {removal['assertions_removed']} removed, {len(full_hits[slug])} "
                     f"merged; {len(removal['members_dropped'])} member(s) dropped for having no "
                     f"remaining assertion; membership {before_n} -> {after_n}."),
        }]
        applied.append((slug, before_n, after_n, len(removal["members_dropped"])))

    digest = fcb.write_codebook_atomic(CODEBOOK_PATH, cb, "codebook.json")
    print(f"wrote {CODEBOOK_PATH}")
    print(f"  sha256={digest}")
    for slug, old_n, new_n, dropped in applied:
        print(f"  {slug}: {old_n} -> {new_n} members ({dropped} dropped with no remaining assertion)")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("generate-samples")
    p_apply = sub.add_parser("apply")
    p_apply.add_argument("--verdicts", required=True)
    args = parser.parse_args()

    if args.command == "generate-samples":
        cmd_generate_samples()
    elif args.command == "apply":
        cmd_apply(args.verdicts)


if __name__ == "__main__":
    main()
