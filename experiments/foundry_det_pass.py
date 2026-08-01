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
                       writes DET-derived membership to codebook.json
                       (replacing existing member_oracle_ids for that axis,
                       old membership preserved in the axis's history --
                       DET's whole premise is "decidable by pattern, no
                       judgment call," so once ratified+verified it
                       supersedes the necessarily-partial sampling-era
                       membership, not merges with it). ANY failing verdict
                       halts with zero codebook.json writes, full stop.

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
import foundry_det_patterns_probe as probe  # noqa: E402
import re  # noqa: E402

DET_PATTERNS_PATH = REPO_ROOT / "docs" / "det-patterns-v2.json"
CODEBOOK_PATH = fc.FOUNDRY_OUT_DIR / "codebook.json"
SAMPLES_REPORT_PATH = fc.FOUNDRY_OUT_DIR / "det_pass_samples_report.json"
SAMPLES_REPORT_MD_PATH = fc.FOUNDRY_OUT_DIR / "det_pass_samples_report.md"
HITS_CACHE_PATH = fc.FOUNDRY_OUT_DIR / "det_pass_full_hits.json"
BATCH_LABEL = "det-pass-1"


def load_axis_patterns():
    det = json.loads(DET_PATTERNS_PATH.read_text())
    cb = json.loads(CODEBOOK_PATH.read_text())
    active = {s for s, e in cb["axes"].items() if e.get("status") == "active"}
    axis_patterns, prefilter_patterns = [], []
    for p in det["patterns"]:
        if p["status"] != "ratified":
            continue
        slug = p["slug"].split(" (")[0].split(" ")[0]
        if slug in active:
            axis_patterns.append(dict(p, resolved_slug=slug))
        else:
            prefilter_patterns.append(p)
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
    cb = json.loads(CODEBOOK_PATH.read_text())
    axes = cb["axes"]
    applied = []
    for p in axis_patterns:
        slug = p["resolved_slug"]
        e = axes[slug]
        old_members = list(e["member_oracle_ids"])
        new_members = full_hits[slug]
        e["member_oracle_ids"] = new_members
        e["source"] = "DET"
        e["history"] = list(e["history"]) + [{
            "batch": BATCH_LABEL, "action": "det_membership_applied",
            "note": (f"Full-corpus DET pass (docs/det-patterns-v2.json pattern_index={p['pattern_index']}, "
                     f"seed={p['seed']}, sample-sheet verified). Membership REPLACED (rule-derived, full "
                     f"corpus, supersedes the necessarily-partial sampling-era set): "
                     f"{len(old_members)} -> {len(new_members)} members. Old member set preserved below for "
                     f"audit trail, not merged: {old_members}"),
        }]
        applied.append((slug, len(old_members), len(new_members)))

    CODEBOOK_PATH.write_text(json.dumps(cb, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {CODEBOOK_PATH}")
    for slug, old_n, new_n in applied:
        print(f"  {slug}: {old_n} -> {new_n} members")


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
