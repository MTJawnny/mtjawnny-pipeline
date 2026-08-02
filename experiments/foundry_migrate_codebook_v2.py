#!/usr/bin/env python3
"""codebook.json schema migration: foundry-codebook/1 -> foundry-codebook/2
(B-MIGRATION-DIRECTIVE.md sec.2, B-MIGRATION-DISCOVERY.md sec.10 A1/A3/A5,
sec.9 R2/R3). Deterministic, re-runnable, G4-clean: the migration is a
script, never a hand-edit, and running it twice from the same pre-state
produces byte-identical output.

What it does: every existing /1 membership row becomes a member object
carrying exactly ONE assertion -- the single support event that is actually
known for it. Multi-assertion stacks are a session-3+ phenomenon; nothing
here invents a second proof.

Provenance table (counts measured in B-MIGRATION-DISCOVERY.md sec.2 and
re-measured by this script every run -- they are gates, not decoration):

  3,697  DET-owned axes (source=="DET", oracle_id in that axis's ratified
         hit list)  -> class=rule-derived, source_ref=det-patterns-v2:<idx>,
         quote = the matched clause, regenerated read-only through the det
         pass's own machinery
  3,699  decisions-traceable rows on live axes -> class=human,
         source_ref=batch-N (captain_axes seed rows: captain-seed-batch-N)
    295  the same replay-derived human assertions riding on non-active
         shells, under their ORIGINAL slugs (R3)
      8  the pay-life rehome additions -> class=human,
         source_ref=pay-life-scrub-2026-07-30
  -----
  7,699

How the human trail is established: an in-memory replay of batches 1->7
through the REAL foundry_reconcile.reconcile(), every path monkeypatched to
a temp dir so the live file is never touched, recording the batch and
pathway at which each (slug, oracle_id) pair first entered the codebook,
then following the current codebook's rename chains to reach today's slugs.
This is provenance ATTRIBUTION only -- per A4 there is no replay-based
rebuild chain, and the live file plus its verified backups remain the source
of truth.

Transcript hygiene (A14): evidence quotes go to files, never to stdout.

Run:
  python3 experiments/foundry_migrate_codebook_v2.py            # writes live
  python3 experiments/foundry_migrate_codebook_v2.py --input <p> --output <p>
"""
import io
import re
import sys
import json
import shutil
import hashlib
import argparse
import tempfile
import contextlib
from pathlib import Path
from collections import defaultdict, Counter

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402
import foundry_codebook as fcb  # noqa: E402
import foundry_reconcile as fr  # noqa: E402
import foundry_det_pass as dp  # noqa: E402

FOUNDRY = fc.FOUNDRY_OUT_DIR
CODEBOOK_PATH = FOUNDRY / "codebook.json"
DECISIONS_DIR = FOUNDRY / "decisions"
REVIEW_DIR = FOUNDRY / "review"
DET_HITS_PATH = FOUNDRY / "det_pass_full_hits.json"
DET_PATTERNS_PATH = REPO_ROOT / "docs" / "det-patterns-v2.json"
PAY_LIFE_REPORT_PATH = FOUNDRY / "batch7_pay_life_scrub_report.json"
MANIFEST_PATH = FOUNDRY / "migration_manifest.json"

BATCHES = tuple(range(1, 8))
PAY_LIFE_SOURCE_REF = "pay-life-scrub-2026-07-30"

EXPECTED = {
    "records": 455,
    "members": 7699,
    "rule_derived": 3697,
    "human": 4002,
    "human_live": 3699,
    "human_shell": 295,
    "pay_life": 8,
    "statuses": {"active": 307, "killed": 75, "renamed": 45, "merged": 26, "deferred": 2},
}


# --------------------------------------------------------------------------
# 1. provenance replay (human class)
# --------------------------------------------------------------------------

def replay_attribution() -> dict:
    """Replays batches 1->7 through the real reconciler into a temp dir and
    returns {(slug, oracle_id): {batch, pathway, review_slug, quote}} keyed on
    the slug as it stood AT THAT BATCH.

    Four pathways, in the order reconcile itself applies them:
      verdict_union    -- the pair came in through a keep/defer/merge/rename
                          union of that batch's own review membership
      rename_carryover -- a rename created a new slug and carried the old
                          entry's pre-existing members onto it; the pair
                          inherits whatever the old slug already had
      captain_seed     -- a captain_axes seed_members row
      member_addition  -- an explicit cross-axis member_additions row
    """
    tmp = Path(tempfile.mkdtemp(prefix="foundry-migrate-replay-"))
    saved = (fr.CODEBOOK_PATH, fr.TAGS_QUEUE_PATH, fr.REPORTS_DIR)
    fr.CODEBOOK_PATH = tmp / "codebook.json"
    fr.TAGS_QUEUE_PATH = tmp / "captain_tags_queue.json"
    fr.REPORTS_DIR = tmp / "reports"

    attribution = {}
    prev = {}
    try:
        for n in BATCHES:
            dec_path = DECISIONS_DIR / f"batch-{n}.foundry-decisions-v1.json"
            rev_path = REVIEW_DIR / f"batch-{n}.json"
            for p in (dec_path, rev_path):
                if not p.exists():
                    fc.halt(f"{p} not found — the batch paper trail is the whole basis of the human "
                            f"class; refusing to migrate without it")
            decisions = json.loads(dec_path.read_text(encoding="utf-8"))
            review = json.loads(rev_path.read_text(encoding="utf-8"))

            removed = {slug: {r["oracle_id"] for r in d.get("removed_members", [])}
                       for slug, d in decisions.get("axes", {}).items()}

            # Where each reviewed axis's staged membership lands, and the quote
            # the proposing batch recorded for it.
            contrib = defaultdict(dict)   # target_slug -> oid -> (review_slug, quote)
            rename_src = {}               # new_slug -> old_slug (this batch's renames)
            for axis in review["axes"]:
                rslug = axis["slug"]
                dec = decisions.get("axes", {}).get(rslug)
                if dec is None:
                    continue
                verdict = dec.get("verdict")
                if verdict in ("keep", "defer"):
                    target = rslug
                elif verdict == "merge":
                    target = dec.get("merge_into")
                elif verdict == "rename":
                    target = dec.get("new_slug")
                    rename_src[target] = rslug
                else:
                    continue  # kill: reconcile unions no members
                if not target:
                    continue
                dropped = removed.get(rslug, set())
                for m in axis["members"]:
                    oid = m["oracle_id"]
                    if oid in dropped:
                        continue
                    # A card can reach one target slug from two reviewed axes
                    # (a merge into a kept axis). Lowest review slug wins --
                    # an explicit deterministic tie-break, not dict order.
                    cur = contrib[target].get(oid)
                    if cur is None or rslug < cur[0]:
                        contrib[target][oid] = (rslug, m.get("quote") or "")

            seeds = {ca["slug"]: set(ca.get("seed_members", []))
                     for ca in decisions.get("captain_axes", [])}
            adds = {(a["slug"], a["oracle_id"]) for a in decisions.get("member_additions", [])}

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                codebook = fr.reconcile(rev_path, dec_path, False)

            state = {slug: set(e.get("member_oracle_ids", []))
                     for slug, e in codebook["axes"].items()}
            for slug in sorted(state):
                for oid in sorted(state[slug] - prev.get(slug, set())):
                    hit = contrib.get(slug, {}).get(oid)
                    if hit is not None:
                        rec = {"batch": n, "pathway": "verdict_union",
                               "review_slug": hit[0], "quote": hit[1]}
                    elif oid in seeds.get(slug, set()):
                        rec = {"batch": n, "pathway": "captain_seed",
                               "review_slug": None, "quote": ""}
                    elif (slug, oid) in adds:
                        rec = {"batch": n, "pathway": "member_addition",
                               "review_slug": None, "quote": ""}
                    else:
                        # A rename carries the OLD entry's pre-existing members
                        # onto the new slug; those rows keep the provenance
                        # they already had under the old name.
                        src = rename_src.get(slug)
                        inherited = attribution.get((src, oid)) if src else None
                        if inherited is None:
                            fc.halt(f"replay: (slug={slug!r}, oracle_id={oid}) appeared at batch {n} "
                                    f"through no recognised pathway — the provenance trail has a hole; "
                                    f"nothing written")
                        rec = dict(inherited, pathway="rename_carryover")
                    attribution[(slug, oid)] = rec
            prev = state
    finally:
        fr.CODEBOOK_PATH, fr.TAGS_QUEUE_PATH, fr.REPORTS_DIR = saved
        shutil.rmtree(tmp, ignore_errors=True)
    return attribution


def project_through_renames(attribution: dict, axes: dict) -> dict:
    """The replay speaks pre-walk-ratification slug names. Follows the live
    codebook's rename chains so replay provenance also answers to today's
    slugs, while KEEPING the original-slug keys -- the 295 audit rows on
    non-active shells are addressed under their original names (R3).

    On collision (two old slugs chasing to one current slug) the earliest
    batch wins, then the pathway name: a fixed, stated rule rather than
    whatever the iteration order happened to be."""
    forward = {slug: e["renamed_to"] for slug, e in axes.items()
               if e.get("status") == "renamed" and e.get("renamed_to")}

    def chase(slug):
        seen = set()
        while slug in forward and slug not in seen:
            seen.add(slug)
            slug = forward[slug]
        return slug

    projected = {}
    for slug, oid in sorted(attribution):
        rec = attribution[(slug, oid)]
        for key in sorted({(slug, oid), (chase(slug), oid)}):
            prior = projected.get(key)
            if prior is None or (rec["batch"], rec["pathway"]) < (prior["batch"], prior["pathway"]):
                projected[key] = rec
    return projected


# --------------------------------------------------------------------------
# 2. DET evidence (rule-derived class)
# --------------------------------------------------------------------------

def det_evidence(scan_texts: dict) -> tuple:
    """Returns ({(slug, oracle_id): (pattern_index, quote)}, {slug: pattern_index}).

    Regenerated READ-ONLY through the det pass's own machinery: the ratified
    patterns via foundry_det_pass.load_axis_patterns(), the evidence pattern
    via its quote_pattern_src() (which knows the enters-tapped family's clause
    comes from a base pattern, not the documentation string in the pattern
    file), the clause via its matched_clause(), and the scan texts from the
    ratified DET preprocessing standard. No part of DET matching is
    re-implemented in this file -- a second implementation would be a second
    thing to keep true."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        axis_patterns, _ = dp.load_axis_patterns()
    if not DET_HITS_PATH.exists():
        fc.halt(f"{DET_HITS_PATH} not found — the DET hit lists are the source artifact for the "
                f"rule-derived class; refusing to migrate without them")
    full_hits = json.loads(DET_HITS_PATH.read_text(encoding="utf-8"))

    evidence = {}
    indices = {}
    for p in axis_patterns:
        slug = p["resolved_slug"]
        indices[slug] = p["pattern_index"]
        compiled = re.compile(dp.quote_pattern_src(p), re.I)
        for oid in full_hits.get(slug, []):
            texts = scan_texts.get(oid)
            if texts is None:
                fc.halt(f"DET hit {slug}/{oid} is not in the Gate #0 corpus — the hit list and the "
                        f"corpus disagree; resolve before migrating")
            clause = dp.matched_clause(compiled, texts)
            if clause is None:
                fc.halt(f"DET hit {slug}/{oid} produced no matched clause on re-scan — the recorded "
                        f"hit list and the ratified pattern disagree; resolve before migrating")
            evidence[(slug, oid)] = (p["pattern_index"], clause)
    return evidence, indices


# --------------------------------------------------------------------------
# 3. pay-life rehome (human class, committed-script trail)
# --------------------------------------------------------------------------

def pay_life_pairs(cards: dict, name_index: dict) -> dict:
    """{(slug, oracle_id): quote} for the batch-7 pay-life rehome additions.
    Names resolve through the house exact-match resolver -- never fuzzy."""
    if not PAY_LIFE_REPORT_PATH.exists():
        fc.halt(f"{PAY_LIFE_REPORT_PATH} not found — it is the paper trail for the 8 rows with no "
                f"decisions-file entry; refusing to migrate without it")
    report = json.loads(PAY_LIFE_REPORT_PATH.read_text(encoding="utf-8"))
    out = {}
    for slug, names in report.get("additions", {}).items():
        for name in names:
            oid = fc.resolve_name(name, cards, name_index)
            out[(slug, oid)] = fc.full_oracle_text(cards[oid])
    return out


# --------------------------------------------------------------------------
# 4. migration
# --------------------------------------------------------------------------

def _manifest_key(path: Path) -> str:
    """Repo-relative where possible so the manifest reads the same from any
    working directory; absolute otherwise (a determinism run reads its input
    from a scratch dir outside the repo)."""
    resolved = Path(path).resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        return str(resolved)


def migrate(input_path: Path, output_path: Path, manifest_path: Path) -> dict:
    if not input_path.exists():
        fc.halt(f"{input_path} not found")
    source = json.loads(input_path.read_text(encoding="utf-8"))
    if source.get("schema") != fcb.SCHEMA_V1:
        fc.halt(f"{input_path}: schema is {source.get('schema')!r}, expected {fcb.SCHEMA_V1!r}. "
                f"This script migrates /1 forward exactly once; a /2 file is already migrated.")
    axes = source["axes"]

    corpus_ref = fcb.corpus_ref_current()
    print(f"corpus_ref (from data/artifacts/latest.json): {corpus_ref}")

    print("replaying batches 1-7 for provenance attribution (temp dir, live file untouched)...")
    attribution = project_through_renames(replay_attribution(), axes)
    print(f"  replay-attributed (slug, oracle_id) keys: {len(attribution)}")

    cards, name_index = fc.load_corpus()
    gated_cards, _, gated_out = fc.load_corpus_gated()
    scan_texts = {oid: fc.det_scan_texts(c) for oid, c in gated_cards.items()}
    print(f"corpus: {len(cards)} cards ({len(gated_cards)} gate-passing, {gated_out} gated out)")

    print("regenerating DET matched clauses read-only from the det-pass machinery...")
    det_ev, det_indices = det_evidence(scan_texts)
    print(f"  DET evidence rows: {len(det_ev)} across {len(det_indices)} patterns")

    pay_life = pay_life_pairs(cards, name_index)
    det_owned = {slug for slug, e in axes.items() if e.get("source") == "DET"}
    if det_owned != set(det_indices):
        fc.halt(f"DET-owned axes in the codebook ({len(det_owned)}) and DET patterns with a live axis "
                f"({len(det_indices)}) disagree: {sorted(det_owned ^ set(det_indices))}")

    out_axes = {}
    counts = Counter()
    pathways = Counter()
    quote_cov = Counter()
    manifest_rows = {}

    for slug, entry in axes.items():
        new_entry = {}
        for key, value in entry.items():
            if key != "member_oracle_ids":
                new_entry[key] = value
                continue
            new_entry["members"] = []   # placeholder, filled below in key position
        if "member_oracle_ids" not in entry:
            out_axes[slug] = new_entry
            continue

        target = {"members": []}
        rows = []
        for oid in entry["member_oracle_ids"]:
            det_hit = det_ev.get((slug, oid)) if slug in det_owned else None
            if det_hit is not None:
                pattern_index, clause = det_hit
                assertion = fcb.build_assertion(
                    "rule-derived", f"{fcb.DET_SOURCE_REF_PREFIX}{pattern_index}",
                    clause, corpus_ref, "quoted")
                counts["rule-derived"] += 1
                quote_cov["rule-derived/quoted"] += 1
            elif (slug, oid) in attribution:
                rec = attribution[(slug, oid)]
                if rec["pathway"] == "captain_seed":
                    source_ref = f"captain-seed-batch-{rec['batch']}"
                else:
                    source_ref = f"batch-{rec['batch']}"
                quote = rec["quote"] or ""
                # A3: a Captain-ratified row with no recorded quote is KEPT and
                # marked, not discarded. Evidence-quote-or-discard was aimed at
                # model assignments; applying it here would delete ratified
                # truth to satisfy a rule written to protect it.
                evidence_status = "quoted" if quote.strip() else "legacy-captain-seed"
                assertion = fcb.build_assertion("human", source_ref, quote, corpus_ref, evidence_status)
                counts["human"] += 1
                pathways[rec["pathway"]] += 1
                quote_cov[f"human/{evidence_status}"] += 1
            elif (slug, oid) in pay_life:
                assertion = fcb.build_assertion(
                    "human", PAY_LIFE_SOURCE_REF, pay_life[(slug, oid)], corpus_ref, "quoted")
                counts["human"] += 1
                counts["pay-life"] += 1
                quote_cov["human/quoted"] += 1
            else:
                fc.halt(f"({slug}, {oid}) traces to no DET hit list, no batch decisions trail and no "
                        f"pay-life report row — the backfill claims zero unknown rows, so this is a "
                        f"real discrepancy; nothing written")
            fcb.merge_assertion(target, oid, assertion)
            rows.append({"oracle_id": oid,
                         "class": assertion["class"],
                         "source_ref": assertion["source_ref"],
                         "evidence_status": assertion["evidence_status"],
                         "quote_sha256": hashlib.sha256(assertion["quote"].encode("utf-8")).hexdigest()})

        new_entry["members"] = target["members"]
        out_axes[slug] = new_entry
        manifest_rows[slug] = rows

    migrated = {}
    for key, value in source.items():
        migrated[key] = out_axes if key == "axes" else value
    migrated["schema"] = fcb.SCHEMA_V2

    # ---- gates measured against the pre-state, before anything is written ----
    problems = []
    for slug, entry in axes.items():
        before = list(entry.get("member_oracle_ids", []))
        after = fcb.member_ids(out_axes[slug])
        if before != after:
            problems.append(slug)
    if problems:
        fc.halt(f"membership-identity gate FAILED on {len(problems)} record(s): {problems[:10]} — "
                f"the migration must reshape membership, never change it; nothing written")

    total_members = sum(len(fcb.member_ids(e)) for e in out_axes.values())
    statuses = Counter(e.get("status") for e in out_axes.values())
    checks = [
        ("records", len(out_axes), EXPECTED["records"]),
        ("members", total_members, EXPECTED["members"]),
        ("class rule-derived", counts["rule-derived"], EXPECTED["rule_derived"]),
        ("class human", counts["human"], EXPECTED["human"]),
        ("pay-life rows", counts["pay-life"], EXPECTED["pay_life"]),
    ]
    for status, want in EXPECTED["statuses"].items():
        checks.append((f"status {status}", statuses.get(status, 0), want))
    failures = [(what, got, want) for what, got, want in checks if got != want]
    if failures:
        fc.halt("count gate FAILED — " + "; ".join(f"{w}: got {g}, expected {e}" for w, g, e in failures)
                + " — nothing written")

    digest = fcb.write_codebook_atomic(output_path, migrated, str(output_path))

    manifest = {
        "schema": "foundry-migration-manifest/1",
        "source_schema": fcb.SCHEMA_V1,
        "target_schema": fcb.SCHEMA_V2,
        "corpus_ref": corpus_ref,
        "inputs": {
            _manifest_key(p): fcb.sha256_of(p)
            for p in [input_path, DET_HITS_PATH, DET_PATTERNS_PATH, PAY_LIFE_REPORT_PATH]
            + [DECISIONS_DIR / f"batch-{n}.foundry-decisions-v1.json" for n in BATCHES]
            + [REVIEW_DIR / f"batch-{n}.json" for n in BATCHES]
        },
        "totals": {
            "records": len(out_axes),
            "members": total_members,
            "class_rule_derived": counts["rule-derived"],
            "class_human": counts["human"],
            "pay_life_rows": counts["pay-life"],
            "statuses": dict(sorted(statuses.items())),
            "human_pathways": dict(sorted(pathways.items())),
            "quote_coverage": dict(sorted(quote_cov.items())),
        },
        "output_sha256": digest,
        "expected_assertions": {slug: manifest_rows[slug] for slug in sorted(manifest_rows)},
    }
    fc.write_json(manifest_path, manifest)

    print(f"\nwrote {output_path}")
    print(f"  sha256={digest}  size={output_path.stat().st_size}")
    print(f"wrote {manifest_path}")
    print(f"\nrecords={len(out_axes)} members={total_members} "
          f"rule-derived={counts['rule-derived']} human={counts['human']}")
    print(f"human pathways: {dict(sorted(pathways.items()))}")
    print(f"quote coverage: {dict(sorted(quote_cov.items()))}")
    return migrated


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", default=str(CODEBOOK_PATH))
    parser.add_argument("--output", default=str(CODEBOOK_PATH))
    parser.add_argument("--manifest", default=str(MANIFEST_PATH))
    args = parser.parse_args()
    migrate(Path(args.input), Path(args.output), Path(args.manifest))


if __name__ == "__main__":
    main()
