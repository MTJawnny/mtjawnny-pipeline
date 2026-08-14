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
import foundry_locality as fl  # noqa: E402
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


# --------------------------------------------------------------------------
# LATTICE ROWS (det-patterns schema /2, added 2026-08-12)
#
# Every other row in det-patterns-v2.json is `slug` + one regex -> ONE axis.
# A lattice row is one MATCHER -> N AXES DECIDED AT MATCH TIME, because M8
# (b6 D3) says a multi-class `targeted-<action>` card gets every applicable
# per-class tag and never a combo tag. Putrefy is destroy-artifact AND
# destroy-creature.
#
# The expansion happens HERE rather than in the lattice module so that the
# rest of this pass sees ordinary per-axis entries and its ratified behaviour
# for the 38 regex patterns is untouched. That was verified rather than
# assumed: det_pass_full_hits.json is byte-identical across this change for
# all 38, 3,697 hits.
# --------------------------------------------------------------------------

def is_lattice_pattern(p: dict) -> bool:
    """Delegates to `foundry_common`, which owns the single definition.

    It moved there 2026-08-14 because `foundry_family_sweep` needs the same
    concept and does not import this module -- so the sweep applied the
    ordinary one-pattern/one-axis orphan law to a lattice record and minted a
    false BLOCKING finding. Kept as a name here because this module's own
    call site and its docs refer to it.
    """
    return fc.is_lattice_pattern(p)


def assert_lattice_invariant(p: dict) -> None:
    """THE RESIDUAL INVARIANT IS A PRECONDITION OF THE WRITE, not a report.

    det-patterns-v2.json's own standing_condition is *"ANY sample row failing
    its axis definition halts the pass before provenance writes"*, and the
    sample sheet is a 12-row fixed-seed slice. A membership that is MISSING is
    invisible to a sample of what was produced — which is how seven correct
    memberships vanished in `e780842` past a green sample gate.

    So the lattice's own invariant runs here, on BOTH sides of the two-phase
    gate, and halts exactly where the standing condition says to halt. It is
    the same shape as the cache-reconciliation halt below: a lattice whose
    behaviour changed since review may not write.

    Record: docs/OBJECT-LATTICE-RESIDUAL-RULING-2026-08-13.md.
    """
    import foundry_object_lattice as ol

    # THE MEMBERSHIP FLOOR, and it must be the TRACKED one. The per-class
    # ratchet in audit-baseline.json lives under experiments/out/, which is
    # gitignored -- on a fresh clone its section is unpinned and
    # `foundry_audit_baseline.report()` returns 0 without comparing anything.
    # Enforcing that here would be enforcing nothing. The ratified row in
    # det-patterns-v2.json IS tracked, so it is the floor a write must clear.
    # Same shape as the hit-cache reconciliation below: what Captain reviewed
    # and what is about to be written have to be the same population.
    # A FALL halts; a RISE is corpus growth and is reported. `corpus_hits` is
    # a measurement at probe time, not an equality invariant -- three ratified
    # patterns have already drifted from theirs with Gate 2 green, and the
    # sibling field is literally named `codebook_n_members_at_probe`.
    floor_fatal, floor_notes = ol.assert_ratified_total()
    for note in floor_notes:
        print(f"NOTE: object lattice membership floor -- {note}")
    for problem in floor_fatal:
        fc.halt(f"object lattice membership floor FAILED: {problem}")

    for stem in p["lattice"]["stems"]:
        r = ol.residual_invariant(stem, ol.PERMANENT_TYPES)
        if r["unexplained"]:
            rows = "\n".join(
                f"    {name}: arm {arm!r} -> {ol.slug_for(stem, cls)}"
                for name, arm, cls, _q in r["unexplained"][:10])
            fc.halt(
                f"object lattice residual invariant FAILED for {stem!r}: "
                f"{len(r['unexplained'])} residual clause(s) still carry a "
                f"target arm resolving to a battlefield class, so the "
                f"producer is dropping memberships nobody reviewed.\n{rows}\n"
                f"  Run: python3 experiments/foundry_object_lattice.py --gate")


def expand_lattice_pattern(p: dict, cards: dict) -> dict:
    """slug -> {oracle_id: proving clause}, for every class the lattice names.

    The quote comes from the lattice's own `quotes` map, which is the clause
    that proved THAT class -- not the card's first matching clause. Evidence
    must prove ITS OWN axis (standing discipline); a card destroying an
    artifact and exiling a creature must not cite one clause for both.
    """
    import foundry_object_lattice as ol
    stems = p["lattice"]["stems"]
    unknown = [s for s in stems if s not in ol.ACTION_VERBS]
    if unknown:
        fc.halt(f"lattice row names stem(s) {unknown!r} that "
                f"foundry_object_lattice does not implement. Its ACTION_VERBS "
                f"are {sorted(ol.ACTION_VERBS)}. A stem that does not exist "
                f"matches nothing and reads as a clean empty result.")
    out = {}
    for stem in stems:
        for oid in sorted(cards):
            r = ol.classes_for_card(cards[oid], stem, ol.PERMANENT_TYPES)
            for cls in sorted(r["classes"]):
                quote = r["quotes"].get(cls)
                if not quote:
                    fc.halt(f"lattice claimed {ol.slug_for(stem, cls)} for "
                            f"{oid} with no proving clause. Evidence-quote-or-"
                            f"discard is not optional.")
                out.setdefault(ol.slug_for(stem, cls), {})[oid] = quote
    if not out:
        fc.halt("lattice row produced ZERO axes. An empty result from a "
                "ratified pattern is a defect, not a clean run.")
    return out


def lattice_axis_record(slug: str, parent_scope: dict) -> dict:
    """A fresh axis record for a virtual node, per grammar sec.11.2.

    Precedent is docs/CLUE-INSTANTIATION-2026-08-03.md, which self-instantiated
    ten axes the same way. The definition is GENERATED from the stem and the
    class rather than hand-written, so 24 axes cannot drift apart in wording;
    the scope is INHERITED from the family's existing ratified parent rather
    than chosen here, because the lattice decides an object class and makes no
    scope claim of its own.
    """
    import foundry_object_lattice as ol
    body = slug[len("rule:targeted-"):]
    stem = next((s for s in ol.ACTION_VERBS if body.startswith(s + "-")), None)
    if stem is None:
        fc.halt(f"cannot derive a stem from lattice slug {slug!r}")
    cls = body[len(stem) + 1:].replace("-", " ")
    verb = {"destroy": "destroys", "exile": "exiles",
            "bounce": "returns to its owner's hand"}[stem]
    anchor = {
        "destroy": "CR 701.8a: to destroy a permanent is to move it from the "
                   "battlefield to its owner's graveyard.",
        "exile": "CR 406.1: an exiled object is in the exile zone, which is "
                 "why exile bypasses indestructible.",
        "bounce": "CR 110.1: a permanent is a card or token on the "
                  "battlefield, so the target is the permanent and not a card "
                  "in another zone.",
    }[stem]
    return {
        "definition": (
            f"A spell or ability {verb} a target {cls}. {anchor} The class "
            f"slot is CR 110.4's permanent-type list; a clause naming two "
            f"types yields one membership per type (M8, b6 D3), never a combo "
            f"axis. Instantiated as a virtual node under grammar sec.11.2 on "
            f"its first quote-verified member."),
        "scope": parent_scope[stem],
        "source": "DET",
        "parameterized": False,
        "members": [],
        "status": "active",
        "merged_into": None,
        "history": [],
    }


# The family parents whose ratified scope each lattice child inherits. Read
# from the live codebook at run time, never typed, so a re-scoped parent
# carries its children with it.
LATTICE_SCOPE_PARENT = {"destroy": "rule:targeted-destroy",
                        "exile": "rule:targeted-exile",
                        "bounce": "rule:targeted-bounce-creature"}


def lattice_parent_scopes(axes: dict) -> dict:
    out = {}
    for stem, parent in LATTICE_SCOPE_PARENT.items():
        rec = axes.get(parent)
        if rec is None or not rec.get("scope"):
            fc.halt(f"lattice scope parent {parent!r} is absent or carries no "
                    f"scope. A child cannot inherit what the parent does not "
                    f"have, and guessing a scope is minting vocabulary.")
        out[stem] = rec["scope"]
    return out


def load_axis_patterns():
    # Deliberately a raw json.load rather than the schema-checking /2 loader:
    # this reads axis STATUS only, never membership, so it is correct against
    # /1 and /2 alike -- and the migration writer calls it while the live file
    # is still /1.
    det = json.loads(DET_PATTERNS_PATH.read_text())
    cb = json.loads(CODEBOOK_PATH.read_text())
    active = {s for s, e in cb["axes"].items() if e.get("status") == "active"}
    axis_patterns, prefilter_patterns = [], []
    lattice_rows = []
    ruled_gaps, deferred_gaps = [], []
    for p in det["patterns"]:
        if p["status"] != "ratified":
            continue
        if is_lattice_pattern(p):
            # Deliberately NOT slug-resolved here: its slugs do not exist yet
            # and the axis-less halt below is correct for every OTHER row.
            lattice_rows.append(p)
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
    return axis_patterns, prefilter_patterns, lattice_rows


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
    axis_patterns, prefilter_patterns, lattice_rows = load_axis_patterns()
    cards, _, gated_out = fc.load_corpus_gated()
    print(f"corpus: {len(cards)} gate-passing cards ({gated_out} gated out)")
    texts = {oid: fc.det_scan_texts(c) for oid, c in cards.items()}

    # Lattice rows expand into ordinary per-axis entries carrying their own
    # hits and their own proving clauses, so everything downstream is uniform.
    lattice_quotes = {}
    for p in lattice_rows:
        assert_lattice_invariant(p)
        expanded = expand_lattice_pattern(p, cards)
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

    special_slugs = {"rule:enters-tapped", "rule:enters-tapped-conditional", "rule:imposes-enters-tapped"}
    for p in axis_patterns:
        slug = p["resolved_slug"]
        if p.get("is_lattice"):
            hits = sorted(lattice_quotes[slug])
        elif slug in special_slugs:
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


def new_locality_stats() -> dict:
    return {"OWNER": 0, "SPAN": 0, "AMBIGUOUS": 0, "UNRESOLVED": 0,
            "no card": 0}


def det_locality_owner(card, clause: str, stats: dict):
    """The semantic owner coordinate for a DET clause, or None. NEVER RAISES.

    Module-level rather than a closure inside `cmd_apply` so the write
    boundary's behaviour can be exercised without performing a codebook
    mutation. A guard reachable only by mutating the codebook is a guard nobody
    will test twice.

    The "never raises" part is the ratified rule, not a convenience:
    `strict=False` means even a card whose CARDNAME canonicalisation reflows
    paragraphs yields an unaddressed assertion instead of killing a
    Captain-ratified write.
    """
    if card is None:
        stats["no card"] += 1
        return None
    r = fl.resolve(card, clause, strict=False)
    stats[r["status"]] += 1
    return r["owner"] if r["status"] == fl.OWNER else None


def cmd_apply(verdicts_path: str):
    if not HITS_CACHE_PATH.exists():
        fc.halt(f"{HITS_CACHE_PATH} not found -- run generate-samples first")
    verdicts = json.loads(Path(verdicts_path).read_text())
    axis_patterns, _, lattice_rows = load_axis_patterns()
    full_hits = json.loads(HITS_CACHE_PATH.read_text())

    # Re-expand the lattice rather than trusting the cache for QUOTES: the
    # cache holds oracle_ids only, and a rule-derived assertion needs the
    # clause that proves its own axis. Re-deriving also means a lattice whose
    # code changed since generate-samples cannot silently apply stale hits --
    # the reconciliation below halts on any disagreement.
    cards_for_lattice, _, _ = fc.load_corpus_gated()
    lattice_quotes = {}
    for p in lattice_rows:
        assert_lattice_invariant(p)
        for slug, hits in expand_lattice_pattern(p, cards_for_lattice).items():
            lattice_quotes[slug] = hits
            axis_patterns.append(dict(p, resolved_slug=slug, is_lattice=True,
                                      pattern=f"(lattice) {slug}"))
    for slug, hits in sorted(lattice_quotes.items()):
        cached = set(full_hits.get(slug, []))
        if cached != set(hits):
            fc.halt(
                f"lattice axis {slug!r} re-derives {len(hits)} hits but the "
                f"cache from generate-samples holds {len(cached)}. The sample "
                f"sheet Captain ratified was drawn from the cached set, so "
                f"applying the new one would write membership nobody reviewed. "
                f"Re-run generate-samples and re-review.")

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

    # Virtual-node instantiation, grammar sec.11.2: "virtual nodes instantiate
    # on first quote-verified member, no fresh ratification". Captain ratifies
    # the GRAMMAR (stem + closed facet slots); the nodes are automatic. This is
    # the same route docs/CLUE-INSTANTIATION-2026-08-03.md took for ten axes.
    parent_scopes = lattice_parent_scopes(axes)
    instantiated = []
    for slug in sorted(lattice_quotes):
        if slug in axes:
            continue
        axes[slug] = lattice_axis_record(slug, parent_scopes)
        axes[slug]["history"] = [{
            "batch": BATCH_LABEL, "action": "created",
            "note": ("virtual node self-instantiated under grammar sec.11.2 on "
                     "its first quote-verified member; object lattice, "
                     "docs/OBJECT-LATTICE-2026-08-09.md, DET pattern_index=45 "
                     "ratified 2026-08-12. Definition generated from stem+class; "
                     "scope inherited from the family parent."),
        }]
        instantiated.append(slug)
    if instantiated:
        print(f"instantiated {len(instantiated)} virtual node(s) under "
              f"grammar sec.11.2")

    # SEMANTIC LOCALITY (FL-2, ratified 2026-08-13). New rule-derived output is
    # born addressed: the clause below is the exact text that proves the
    # assertion, so the one place that mints DET provenance is also the one
    # place where the address is free and unambiguous.
    #
    # THIS IS NOT A GATE, AND MUST NOT BECOME ONE. An address is optional by
    # ratification, and an unaddressed assertion stays fully valid card-level
    # evidence -- so a quote that resolves to SPAN, AMBIGUOUS or UNRESOLVED is
    # written WITHOUT an address rather than refused. Blocking a write on
    # address coverage would make an unaddressable-but-valid membership
    # unwritable, which is directly against the ratified unaddressed rule.
    # `strict=False` carries that guarantee structurally: the resolver cannot
    # halt this path even on a card whose canonicalisation reflows.
    #
    # Counted by outcome and reported below, never as a net number -- the
    # unaddressed rows are the ones a human works down over time.
    locality_stats = new_locality_stats()

    def resolve_owner(oid, clause):
        return det_locality_owner(cards.get(oid), clause, locality_stats)

    applied = []
    for p in axis_patterns:
        slug = p["resolved_slug"]
        e = axes[slug]
        before_n = len(fcb.member_ids(e))
        removal = fcb.remove_det_assertions(e)
        source_ref = f"{fcb.DET_SOURCE_REF_PREFIX}{p['pattern_index']}"
        compiled = None if p.get("is_lattice") else re.compile(
            quote_pattern_src(p), re.I)
        for oid in full_hits[slug]:
            if oid not in texts:
                fc.halt(f"DET hit {slug}/{oid} is not in the Gate #0 corpus — hit list and corpus "
                        f"disagree; nothing written")
            if p.get("is_lattice"):
                # The lattice's own proving clause for THIS class, not a
                # re-scan: a re-scan would hand every class on a multi-class
                # card the same first-matching clause.
                clause = lattice_quotes[slug].get(oid)
            else:
                clause = matched_clause(compiled, texts[oid])
            if clause is None:
                fc.halt(f"DET hit {slug}/{oid} produced no matched clause on re-scan — the recorded hit "
                        f"list and the ratified pattern disagree; nothing written")
            fcb.merge_assertion(e, oid, fcb.build_assertion(
                "rule-derived", source_ref, clause, corpus_ref, "quoted",
                locality=resolve_owner(oid, clause)))
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

    # ADDED AND UNADDRESSED REPORTED SEPARATELY, never as a coverage percentage
    # standing in for both. The unaddressed rows are not failures -- they are
    # the working queue foundry_locality.py --report enumerates.
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
