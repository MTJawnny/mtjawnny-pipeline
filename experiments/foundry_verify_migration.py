#!/usr/bin/env python3
"""Independent verification of the /1 -> /2 codebook migration
(B-MIGRATION-DIRECTIVE.md sec.3, B-MIGRATION-DISCOVERY.md sec.10 A13 / audit
finding B-02). This is the audit's core demand: a migration is not trusted
because the writer says so.

INDEPENDENCE CONTRACT. The verification path in this file imports nothing
from foundry_migrate_codebook_v2.py and nothing from foundry_codebook.py --
not the loader, not the lint, not the vocabularies. It re-reads the raw JSON
itself and re-derives every expected value directly from the SOURCE
artifacts (docs/det-patterns-v2.json, det_pass_full_hits.json, the
decisions/ and review/ paper trail, batch7_pay_life_scrub_report.json). Its
only shared dependency is foundry_common's corpus loaders, which are also
what the batches themselves read. It deliberately does NOT read
migration_manifest.json: a manifest is the writer's own account of what it
did, so treating it as ground truth would verify nothing.

It also re-derives provenance by a DIFFERENT METHOD than the writer. The
writer replays the reconciler and diffs to discover WHICH batch introduced a
row. The verifier does the converse: it takes the batch the file CLAIMS and
confirms that batch's own artifacts genuinely contain that card on a slug
that routes to that axis. Agreement between a forward derivation and a
backward confirmation is worth more than running the same derivation twice.

Report categories (printed as counts + a card-by-card file, never as inline
quotes -- A14). These do NOT halt:
  quote-not-verbatim  -- a quote that is not literally present in the
                         corpus representation it references. A9 accepts
                         that a quote can be historically true and currently
                         stale; each instance is listed for Captain.
Everything else that fails is a HALT.

  python3 experiments/foundry_verify_migration.py [--codebook <path>]
  python3 experiments/foundry_verify_migration.py negative-tests
"""
import os
import re
import sys
import json
import shutil
import argparse
import tempfile
from pathlib import Path
from collections import Counter, defaultdict

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402   (corpus loaders only)

FOUNDRY = fc.FOUNDRY_OUT_DIR
CODEBOOK_PATH = FOUNDRY / "codebook.json"
DECISIONS_DIR = FOUNDRY / "decisions"
REVIEW_DIR = FOUNDRY / "review"
DET_HITS_PATH = FOUNDRY / "det_pass_full_hits.json"
DET_PATTERNS_PATH = REPO_ROOT / "docs" / "det-patterns-v2.json"
PAY_LIFE_REPORT_PATH = FOUNDRY / "batch7_pay_life_scrub_report.json"
LATEST_ARTIFACT_PATH = REPO_ROOT / "data" / "artifacts" / "latest.json"
REPORT_PATH = FOUNDRY / "migration_verification_report.json"

BATCHES = tuple(range(1, 8))
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

EXPECT_RECORDS = 455
EXPECT_MEMBERS = 7699
EXPECT_RULE_DERIVED = 3697
EXPECT_HUMAN = 4002
EXPECT_STATUSES = {"active": 307, "killed": 75, "renamed": 45, "merged": 26, "deferred": 2}

# docs/det-patterns-v2.json records three enters-tapped-family patterns whose
# "pattern" field is not the standalone regex that decided membership: two are
# base regexes that still need the probe's G2 subject classification applied on
# top, and rule:imposes-enters-tapped's field is prose describing that
# classification, not a regex at all. Their membership is confirmed against the
# ratified hit list (the real source artifact) and their quotes against the
# corpus; the "does this pattern match" re-check is not applicable and is
# reported as an explicit, enumerated exemption rather than silently skipped.
PATTERN_MATCH_EXEMPT = {
    "rule:enters-tapped": "base regex + G2 subject split, not a standalone matcher",
    "rule:enters-tapped-conditional": "base regex + G2 subject split, not a standalone matcher",
    "rule:imposes-enters-tapped": "pattern field is prose documentation, not a regex",
}


def fail(problems, msg):
    problems.append(msg)


# --------------------------------------------------------------------------
# source-artifact re-derivation
# --------------------------------------------------------------------------

def load_det_sources():
    """{slug: pattern_index} and {slug: set(oracle_id)}, re-derived from the
    ratified pattern file and hit list without touching the det-pass code."""
    det = json.loads(DET_PATTERNS_PATH.read_text(encoding="utf-8"))
    hits = {s: set(v) for s, v in json.loads(DET_HITS_PATH.read_text(encoding="utf-8")).items()}
    index_by_slug = {}
    pattern_by_slug = {}
    for p in det["patterns"]:
        if p.get("status") != "ratified":
            continue
        # The pattern file records some slugs with a parenthetical or trailing
        # qualifier ("rule:enters-tapped (unconditional)"); the axis slug is
        # the bare leading token.
        slug = p["slug"].split(" (")[0].split(" ")[0]
        if slug in hits:
            index_by_slug[slug] = p["pattern_index"]
            pattern_by_slug[slug] = p["pattern"]
    return index_by_slug, pattern_by_slug, hits


def load_batch_routing():
    """For each batch N: which current-slug destinations each reviewed axis's
    membership could legitimately reach, plus that batch's captain seeds and
    member_additions. Built straight from the decisions/review paper trail."""
    per_batch = {}
    for n in BATCHES:
        decisions = json.loads((DECISIONS_DIR / f"batch-{n}.foundry-decisions-v1.json").read_text(encoding="utf-8"))
        review = json.loads((REVIEW_DIR / f"batch-{n}.json").read_text(encoding="utf-8"))
        staged = defaultdict(set)       # destination slug -> oracle_ids
        for axis in review["axes"]:
            dec = decisions.get("axes", {}).get(axis["slug"])
            if dec is None:
                continue
            verdict = dec.get("verdict")
            if verdict in ("keep", "defer"):
                dest = axis["slug"]
            elif verdict == "merge":
                dest = dec.get("merge_into")
            elif verdict == "rename":
                dest = dec.get("new_slug")
            else:
                continue
            if not dest:
                continue
            dropped = {r["oracle_id"] for r in dec.get("removed_members", [])}
            for m in axis["members"]:
                if m["oracle_id"] not in dropped:
                    staged[dest].add(m["oracle_id"])
        seeds = defaultdict(set)
        for ca in decisions.get("captain_axes", []):
            seeds[ca["slug"]] |= set(ca.get("seed_members", []))
        adds = {(a["slug"], a["oracle_id"]) for a in decisions.get("member_additions", [])}
        per_batch[n] = {"staged": staged, "seeds": seeds, "adds": adds}
    return per_batch


def build_chain(axes):
    """Returns chain(slug) -> every slug on the rename path starting at `slug`,
    INCLUDING intermediates. A row can legitimately rest on a middle node: when
    A was renamed to B and B later renamed to C, B survives as a shell still
    holding its audit rows (R3), so a membership row on B is confirmed by A's
    batch-era decisions just as one on C is. Endpoints-only would reject those
    rows for existing."""
    forward = {slug: e["renamed_to"] for slug, e in axes.items()
               if e.get("status") == "renamed" and e.get("renamed_to")}

    def chain(slug):
        path = [slug]
        seen = {slug}
        while slug in forward and forward[slug] not in seen:
            slug = forward[slug]
            seen.add(slug)
            path.append(slug)
        return path
    return chain


def load_pay_life(cards, name_index):
    report = json.loads(PAY_LIFE_REPORT_PATH.read_text(encoding="utf-8"))
    pairs = set()
    for slug, names in report.get("additions", {}).items():
        for name in names:
            pairs.add((slug, fc.resolve_name(name, cards, name_index)))
    return pairs


# --------------------------------------------------------------------------
# verification
# --------------------------------------------------------------------------

def verify(codebook_path: Path) -> dict:
    problems = []
    codebook = json.loads(Path(codebook_path).read_text(encoding="utf-8"))
    if codebook.get("schema") != "foundry-codebook/2":
        fc.halt(f"{codebook_path}: schema is {codebook.get('schema')!r}, expected 'foundry-codebook/2' "
                f"— nothing to verify")
    axes = codebook.get("axes") or {}

    expected_corpus_ref = json.loads(LATEST_ARTIFACT_PATH.read_text(encoding="utf-8"))["version"]
    det_index, det_pattern_src, det_hits = load_det_sources()
    routing = load_batch_routing()
    chain = build_chain(axes)
    cards, name_index = fc.load_corpus()
    pay_life = load_pay_life(cards, name_index)

    # Where each batch's staged/seeded membership can legitimately land today.
    dest_now = {}
    for n in BATCHES:
        staged_now = defaultdict(set)
        for dest, oids in routing[n]["staged"].items():
            for node in chain(dest):
                staged_now[node] |= oids
        seeds_now = defaultdict(set)
        for dest, oids in routing[n]["seeds"].items():
            for node in chain(dest):
                seeds_now[node] |= oids
        adds_now = set()
        for slug, oid in routing[n]["adds"]:
            for node in chain(slug):
                adds_now.add((node, oid))
        dest_now[n] = {"staged": staged_now, "seeds": seeds_now, "adds": adds_now}

    det_owned = {slug for slug, e in axes.items() if e.get("source") == "DET"}
    if det_owned != set(det_hits):
        fail(problems, f"DET-owned axes {sorted(det_owned - set(det_hits))} / hit-list slugs "
                       f"{sorted(set(det_hits) - det_owned)} disagree")

    text_cache = {}

    def representations(oid):
        if oid not in text_cache:
            card = cards.get(oid)
            if card is None:
                text_cache[oid] = None
            else:
                text_cache[oid] = [fc.full_oracle_text(card)] + fc.det_scan_texts(card)
        return text_cache[oid]

    classes = Counter()
    statuses = Counter()
    n_members = 0
    errata = []
    overlap_rows = []
    exempt_pattern_checks = Counter()

    for slug, entry in axes.items():
        statuses[entry.get("status")] += 1
        if "member_oracle_ids" in entry:
            fail(problems, f"{slug}: still carries the /1 'member_oracle_ids' field")
        if "members" not in entry:
            continue
        ids = [m.get("oracle_id") for m in entry["members"]]
        if ids != sorted(ids):
            fail(problems, f"{slug}: members are not sorted by oracle_id")
        if len(ids) != len(set(ids)):
            fail(problems, f"{slug}: duplicate member oracle_id(s)")

        for member in entry["members"]:
            n_members += 1
            oid = member.get("oracle_id")
            where = f"{slug}/{oid}"
            if not isinstance(oid, str) or not UUID_RE.match(oid):
                fail(problems, f"{where}: oracle_id is not a valid uuid shape")
                continue

            assertions = member.get("assertions")
            if not isinstance(assertions, list) or len(assertions) != 1:
                fail(problems, f"{where}: expected exactly 1 assertion post-migration, found "
                               f"{len(assertions) if isinstance(assertions, list) else type(assertions).__name__}")
                continue
            a = assertions[0]
            cls, sref = a.get("class"), a.get("source_ref")
            classes[cls] += 1

            # -- (5) tier / lane / evidence_status rules --------------------
            if "tier" in member:
                fail(problems, f"{where}: carries a tier, but no assertion is llm-class "
                               f"(tier is present iff the whole stack is llm)")
            if cls not in ("human", "rule-derived"):
                fail(problems, f"{where}: class {cls!r} — post-migration rows are human or "
                               f"rule-derived only (no llm assertion exists before session 3)")
            for lane_field in ("original_lane", "effective_lane", "promotion_reason"):
                if lane_field in a:
                    fail(problems, f"{where}: {lane_field} is llm-class only, found on {cls!r}")
            ev = a.get("evidence_status")
            if ev not in ("quoted", "legacy-captain-seed"):
                fail(problems, f"{where}: evidence_status {ev!r} outside the ratified vocabulary")
            if a.get("corpus_ref") != expected_corpus_ref:
                fail(problems, f"{where}: corpus_ref {a.get('corpus_ref')!r}, expected "
                               f"{expected_corpus_ref!r} (the snapshot every quote is drawn from)")
            quote = a.get("quote")
            if not isinstance(quote, str):
                fail(problems, f"{where}: quote is not a string")
                continue
            if not quote.strip() and ev != "legacy-captain-seed":
                fail(problems, f"{where}: empty quote without the A3 legacy-captain-seed exemption")

            # -- (1)(2)(4) class + source_ref against the source artifacts --
            # Dispatch on what the file CLAIMS, then demand a source artifact
            # that supports the claim. Forcing each row into a precomputed
            # bucket instead would mis-reject the legitimate overlaps: the
            # pay-life scrub UNIONS its rehomes, so a card already on the axis
            # from an earlier batch keeps its earlier, truer provenance and is
            # a no-op there (this is exactly why the ratified pay-life count is
            # 8 rows and not the report's 9 names).
            is_det_hit = slug in det_owned and oid in det_hits.get(slug, set())
            if is_det_hit and cls != "rule-derived":
                fail(problems, f"{where}: is in {slug}'s ratified DET hit list but claims class {cls!r} "
                               f"— a DET-decided row may not present as anything else")

            if sref and sref.startswith("det-patterns-v2:"):
                if not is_det_hit:
                    fail(problems, f"{where}: claims a DET source_ref but is not in {slug}'s ratified "
                                   f"hit list (or {slug} is not DET-owned)")
                elif sref != f"det-patterns-v2:{det_index.get(slug)}":
                    fail(problems, f"{where}: source_ref {sref!r}, expected "
                                   f"'det-patterns-v2:{det_index.get(slug)}'")
                elif slug in PATTERN_MATCH_EXEMPT:
                    exempt_pattern_checks[slug] += 1
                else:
                    reps = representations(oid)
                    if reps is None:
                        fail(problems, f"{where}: oracle_id is not in the corpus at all")
                    else:
                        pat = re.compile(det_pattern_src[slug], re.I)
                        if not any(pat.search(t) for t in reps):
                            fail(problems, f"{where}: the pattern at index {det_index[slug]} does not "
                                           f"match this card — source_ref does not hold")

            elif sref == "pay-life-scrub-2026-07-30":
                if cls != "human":
                    fail(problems, f"{where}: pay-life rehome rows are human-class, found {cls!r}")
                if (slug, oid) not in pay_life:
                    fail(problems, f"{where}: claims the pay-life scrub, but that report's additions "
                                   f"do not put this card on this axis")

            elif re.match(r"^(captain-seed-)?batch-[1-7]$", sref or ""):
                if cls != "human":
                    fail(problems, f"{where}: claims a batch source_ref but class is {cls!r}")
                m = re.match(r"^(captain-seed-)?batch-([1-7])$", sref)
                n = int(m.group(2))
                d = dest_now[n]
                if m.group(1):
                    confirmed = oid in d["seeds"].get(slug, set())
                    kind = "captain_axes seed_members"
                else:
                    confirmed = (oid in d["staged"].get(slug, set())
                                 or (slug, oid) in d["adds"])
                    kind = "staged decisions / member_additions"
                if not confirmed:
                    fail(problems, f"{where}: source_ref {sref!r} is not confirmed — batch {n}'s "
                                   f"{kind} do not put this card on this axis")
                elif (slug, oid) in pay_life:
                    overlap_rows.append({"slug": slug, "oracle_id": oid,
                                         "name": cards[oid].get("name"), "source_ref": sref})
            else:
                fail(problems, f"{where}: source_ref {sref!r} is outside the ratified vocabulary")

            # -- (3) quote verbatim in the referenced corpus representation --
            if quote.strip():
                reps = representations(oid)
                if reps is None:
                    fail(problems, f"{where}: oracle_id is not in the corpus, cannot check the quote")
                elif not any(quote in t for t in reps):
                    normalized = " ".join(quote.split())
                    if any(normalized in " ".join(t.split()) for t in reps):
                        errata.append({"slug": slug, "oracle_id": oid, "name": cards[oid].get("name"),
                                       "source_ref": sref, "kind": "whitespace-only difference",
                                       "quote": quote})
                    else:
                        errata.append({"slug": slug, "oracle_id": oid, "name": cards[oid].get("name"),
                                       "source_ref": sref, "kind": "not present in current corpus",
                                       "quote": quote})

    # -- global counts ----------------------------------------------------
    if len(axes) != EXPECT_RECORDS:
        fail(problems, f"records: {len(axes)}, expected {EXPECT_RECORDS}")
    if n_members != EXPECT_MEMBERS:
        fail(problems, f"members: {n_members}, expected {EXPECT_MEMBERS}")
    if classes["rule-derived"] != EXPECT_RULE_DERIVED:
        fail(problems, f"class rule-derived: {classes['rule-derived']}, expected {EXPECT_RULE_DERIVED}")
    if classes["human"] != EXPECT_HUMAN:
        fail(problems, f"class human: {classes['human']}, expected {EXPECT_HUMAN}")
    for status, want in EXPECT_STATUSES.items():
        if statuses.get(status, 0) != want:
            fail(problems, f"status {status}: {statuses.get(status, 0)}, expected {want}")

    report = {
        "schema": "foundry-migration-verification/1",
        "codebook": str(codebook_path),
        "corpus_ref_expected": expected_corpus_ref,
        "records": len(axes),
        "members": n_members,
        "classes": dict(sorted(classes.items())),
        "statuses": dict(sorted((k, v) for k, v in statuses.items() if k)),
        "report_categories": {
            "quote-not-verbatim": len(errata),
            "pay-life-name-with-earlier-trail": len(overlap_rows),
            "det-pattern-match-exempt": dict(sorted(exempt_pattern_checks.items())),
        },
        "det_pattern_match_exemption_reasons": PATTERN_MATCH_EXEMPT,
        "quote_not_verbatim_rows": errata,
        "pay_life_name_with_earlier_trail_rows": overlap_rows,
        "problems": problems,
    }
    fc.write_json(REPORT_PATH, report)

    print(f"records={len(axes)} members={n_members} classes={dict(sorted(classes.items()))}")
    print(f"statuses={dict(sorted((k, v) for k, v in statuses.items() if k))}")
    print(f"corpus_ref checked against {expected_corpus_ref}")
    print(f"report category 'quote-not-verbatim': {len(errata)} row(s) "
          f"— listed card-by-card in {REPORT_PATH.name} (quotes to file only, never console)")
    for e in errata:
        print(f"    {e['slug']} / {e['name']} ({e['oracle_id']}) — {e['kind']}, source_ref={e['source_ref']}")
    print(f"report category 'pay-life-name-with-earlier-trail': {len(overlap_rows)} row(s) "
          f"— named in the scrub report but already a member from an earlier batch, so the earlier "
          f"provenance stands (this is why the ratified pay-life count is 8, not 9)")
    for r in overlap_rows:
        print(f"    {r['slug']} / {r['name']} ({r['oracle_id']}) — kept {r['source_ref']}")
    print(f"report category 'det-pattern-match-exempt': {sum(exempt_pattern_checks.values())} row(s) "
          f"across {len(exempt_pattern_checks)} axes ({', '.join(sorted(exempt_pattern_checks))})")
    print(f"wrote {REPORT_PATH}")

    if problems:
        print(f"\nVERIFIER FOUND {len(problems)} PROBLEM(S):")
        for p in problems[:40]:
            print(f"  - {p}")
        fc.halt(f"independent verification FAILED with {len(problems)} problem(s) outside the declared "
                f"report categories — see {REPORT_PATH}")
    print("\nindependent verification CLEAN.")
    return report


# --------------------------------------------------------------------------
# negative tests (scratch copies only -- the live file is never touched)
# --------------------------------------------------------------------------

def negative_tests(codebook_path: Path):
    """Each test asserts that a specific WRONG thing fails, and fails the way
    the house style demands. Run entirely inside a temp dir on copies.

    These import foundry_codebook because they are testing it; the
    verification path above still does not."""
    import foundry_codebook as fcb

    live_before = fcb.sha256_of(CODEBOOK_PATH) if CODEBOOK_PATH.exists() else None
    tmp = Path(tempfile.mkdtemp(prefix="foundry-negative-"))
    results = []

    def record(name, passed, detail):
        results.append({"test": name, "passed": bool(passed), "detail": detail})
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}: {detail}")

    def expect_lint_error(name, mutate):
        cb = json.loads(Path(codebook_path).read_text(encoding="utf-8"))
        mutate(cb)
        try:
            fcb.lint(cb, "negative-test")
        except fcb.LintError as e:
            record(name, True, f"lint refused it ({str(e).splitlines()[0][:80]})")
            return
        record(name, False, "lint ACCEPTED a file it must refuse")

    try:
        v2 = json.loads(Path(codebook_path).read_text(encoding="utf-8"))
        first_slug_with_members = next(s for s, e in v2["axes"].items() if e.get("members"))

        # 1. a /1-era consumer meeting a /2 file
        entry = v2["axes"][first_slug_with_members]
        try:
            set(entry["member_oracle_ids"])          # reconcile's own read shape
            record("/1 consumer x /2 file (direct key)", False, "read succeeded — it must not")
        except KeyError:
            # The .get(..., []) shape used by foundry_consolidate_run1.py does
            # NOT raise: it silently yields an empty set. The rename alone is
            # therefore not a safe failure mode, which is exactly why every
            # consumer is routed through the schema-checking loader.
            silent = set(entry.get("member_oracle_ids", []))
            record("/1 consumer x /2 file (direct key)", True,
                   f"KeyError as required; note the .get() shape returns {silent!r} SILENTLY "
                   f"— schema check in load_codebook() is what makes that safe")

        # 2. a /2 loader meeting a /1 file
        v1_path = tmp / "codebook_v1.json"
        legacy = {"schema": "foundry-codebook/1", "version": "0.7",
                  "axes": {"rule:x": {"member_oracle_ids": []}}, "batches_reconciled": []}
        v1_path.write_text(json.dumps(legacy), encoding="utf-8")
        code = os.system(f'{sys.executable} -c "'
                         f"import sys; sys.path.insert(0, r'{REPO_ROOT / 'experiments'}'); "
                         f"import foundry_codebook as f; f.load_codebook(r'{v1_path}')"
                         f'" 2>/dev/null')
        record("/2 loader x /1 file", code != 0, f"loader exited {os.waitstatus_to_exitcode(code) if code else 0} "
                                                 f"(non-zero = halted as required)")

        # 3-8. lint invariants
        def dup_member(cb):
            e = cb["axes"][first_slug_with_members]
            e["members"] = e["members"] + [json.loads(json.dumps(e["members"][0]))]
        expect_lint_error("duplicate member oracle_id", dup_member)

        def dup_assertion(cb):
            m = cb["axes"][first_slug_with_members]["members"][0]
            m["assertions"] = m["assertions"] + [json.loads(json.dumps(m["assertions"][0]))]
        expect_lint_error("duplicate (class, source_ref)", dup_assertion)

        def bad_uuid(cb):
            cb["axes"][first_slug_with_members]["members"][0]["oracle_id"] = "not-a-uuid"
        expect_lint_error("invalid uuid shape", bad_uuid)

        def empty_quote(cb):
            a = cb["axes"][first_slug_with_members]["members"][0]["assertions"][0]
            a["quote"] = ""
            a["evidence_status"] = "quoted"
        expect_lint_error("empty quote without exemption", empty_quote)

        def bad_corpus_ref(cb):
            del cb["axes"][first_slug_with_members]["members"][0]["assertions"][0]["corpus_ref"]
        expect_lint_error("missing corpus_ref", bad_corpus_ref)

        def bad_tier(cb):
            cb["axes"][first_slug_with_members]["members"][0]["tier"] = "corroborated"
        expect_lint_error("tier contradicting the assertion stack", bad_tier)

        def bad_source_ref(cb):
            cb["axes"][first_slug_with_members]["members"][0]["assertions"][0]["source_ref"] = "vibes"
        expect_lint_error("source_ref outside the ratified vocabulary", bad_source_ref)

        # 9. interrupted write: temp present, live untouched
        target = tmp / "interrupted.json"
        shutil.copy2(codebook_path, target)
        before = fcb.sha256_of(target)
        real_replace = os.replace

        def boom(src, dst):
            raise OSError("simulated crash between verify and rename")
        os.replace = boom
        try:
            fcb.write_codebook_atomic(target, v2)
            record("interrupted write", False, "write reported success despite a failing rename")
        except OSError:
            leftover = target.with_suffix(target.suffix + ".tmp")
            ok = fcb.sha256_of(target) == before and leftover.exists()
            record("interrupted write", ok,
                   f"live file unchanged={fcb.sha256_of(target) == before}, "
                   f"inert temp left behind={leftover.exists()}")
        finally:
            os.replace = real_replace
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    live_after = fcb.sha256_of(CODEBOOK_PATH) if CODEBOOK_PATH.exists() else None
    if live_before != live_after:
        fc.halt("negative tests changed the live codebook — they must run on copies only")
    record("live codebook untouched by the suite", True, f"sha256 unchanged ({live_before[:16]}...)")

    failed = [r for r in results if not r["passed"]]
    fc.write_json(FOUNDRY / "migration_negative_tests.json",
                  {"schema": "foundry-migration-negative-tests/1", "results": results})
    if failed:
        fc.halt(f"{len(failed)} negative test(s) FAILED: {[r['test'] for r in failed]}")
    print(f"\nall {len(results)} negative tests passed.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", nargs="?", default="verify", choices=["verify", "negative-tests"])
    parser.add_argument("--codebook", default=str(CODEBOOK_PATH))
    args = parser.parse_args()
    if args.command == "verify":
        verify(Path(args.codebook))
    else:
        negative_tests(Path(args.codebook))


if __name__ == "__main__":
    main()
