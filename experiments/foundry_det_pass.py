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

# S7: the two PURE text matchers moved to `mtj_foundry.mtg.text_match`. They
# know a regex and a list of strings and nothing else, so they are the only part
# of this file that is substrate. Everything else here -- DET record roles,
# pattern resolution, the lattice, samples, apply/write -- was later-slice work
# and S7 left it untouched. NO SECOND IMPLEMENTATION REMAINS HERE.
from mtj_foundry.mtg import text_match as _text_match  # noqa: E402

# S11: the codebook-facing semantics this shell used to DEFINE now have permanent
# owners -- DET record roles and the enters-tapped quote base
# (`codebook_det_patterns`), pattern -> ACTIVE-axis resolution
# (`codebook_det_resolution`), lattice instantiation (`codebook_lattice`), and
# the in-memory A8 application (`codebook_det_apply`). What stays here is the
# operator shell: file reads, the hit cache, the sample sheets, the verdict
# gate, the backup, the atomic write, every print, and the historic `STOP — …`
# process boundary, which the wrappers below re-establish around each owner's
# typed refusal. `det_locality_owner` and the samples stay too: they are review
# orchestration (S13), not codebook semantics.
from mtj_foundry import codebook as _codebook  # noqa: E402
from mtj_foundry import codebook_det_apply as _det_apply  # noqa: E402
from mtj_foundry import codebook_det_patterns as _det_patterns  # noqa: E402
from mtj_foundry import codebook_det_resolution as _det_resolution  # noqa: E402
from mtj_foundry import codebook_lattice as _lattice  # noqa: E402
from mtj_foundry.mtg.shapes import target_classes as _target_classes  # noqa: E402

DET_PATTERNS_PATH = fc.CONFIG_SEMANTIC / "det-patterns-v2.json"
CODEBOOK_PATH = fc.FOUNDRY_OUT_DIR / "codebook.json"
SAMPLES_REPORT_PATH = fc.FOUNDRY_OUT_DIR / "det_pass_samples_report.json"
SAMPLES_REPORT_MD_PATH = fc.FOUNDRY_OUT_DIR / "det_pass_samples_report.md"
HITS_CACHE_PATH = fc.FOUNDRY_OUT_DIR / "det_pass_full_hits.json"
BATCH_LABEL = _det_apply.BATCH_LABEL


# S11: the Captain-ruled axis-less register is the resolution owner's, and this
# is the SAME dict object -- edit it there, not here.
RULED_AXISLESS_PATTERNS = _det_resolution.RULED_AXISLESS_PATTERNS


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
    """Delegates to `mtj_foundry.codebook_det_patterns`, the single definition.

    One definition exists because `foundry_family_sweep` needs the same concept
    and does not import this module -- a second copy once applied the ordinary
    one-pattern/one-axis orphan law to a lattice record and minted a false
    BLOCKING finding. Kept as a name here because this module's docs refer to it.
    """
    return _det_patterns.is_lattice_pattern(p)


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
        failure = _lattice.residual_invariant_failure_message(stem, r["unexplained"])
        if failure:
            fc.halt(failure)


def _halting(fn, *args, **kwargs):
    """Call a permanent owner and re-establish the historic `STOP — …` contract.

    The owners raise typed refusals whose message bodies are the old halt text
    verbatim; a library may not exit a process it does not own. The caught set
    is exactly the owners' refusal types -- nothing broader.
    """
    try:
        return fn(*args, **kwargs)
    except (_det_resolution.DetResolutionError, _lattice.LatticeGovernanceError,
            _target_classes.LatticeError, _det_apply.DetApplyError,
            _codebook.CodebookError) as error:
        fc.halt(str(error))


def expand_lattice_pattern(p: dict, cards: dict) -> dict:
    """slug -> {oracle_id: proving clause}, for every class the lattice names.

    S11: delegates to `mtj_foundry.codebook_lattice.expand_lattice_pattern`,
    handing it this boundary's CR-derived permanent-type domain.
    """
    import foundry_object_lattice as ol
    return _halting(_lattice.expand_lattice_pattern, p, cards, ol.PERMANENT_TYPES)


def lattice_axis_record(slug: str, parent_scope: dict) -> dict:
    """A fresh axis record for a virtual node, per grammar sec.11.2.

    S11: delegates to `mtj_foundry.codebook_lattice.lattice_axis_record`. The
    object-lattice shell is imported first, as before, so the substrate's
    vocabulary exists before the owner reads it.
    """
    import foundry_object_lattice as ol  # noqa: F401 -- establishes the substrate state
    return _halting(_lattice.lattice_axis_record, slug, parent_scope)


# S11: the owner's register, the same dict object.
LATTICE_SCOPE_PARENT = _lattice.LATTICE_SCOPE_PARENT


def lattice_parent_scopes(axes: dict) -> dict:
    return _halting(_lattice.lattice_parent_scopes, axes)


def load_axis_patterns():
    # Deliberately a raw json.load rather than the schema-checking /2 loader:
    # this reads axis STATUS only, never membership, so it is correct against
    # /1 and /2 alike -- and the migration writer calls it while the live file
    # is still /1.
    #
    # S11: the partition itself is `codebook_det_resolution`'s. The READ and the
    # NOTE lines stay here.
    det = json.loads(DET_PATTERNS_PATH.read_text())
    cb = json.loads(CODEBOOK_PATH.read_text())
    axis_patterns, prefilter_patterns, lattice_rows, ruled_gaps, deferred_gaps = \
        _halting(_det_resolution.resolve_axis_patterns, det, cb)

    for slug in sorted(ruled_gaps):
        print(f"NOTE: ratified pattern {slug!r} has no axis yet — "
              f"{RULED_AXISLESS_PATTERNS[slug]}. Not applied this run.")
    for slug, st in sorted(deferred_gaps):
        print(f"NOTE: ratified pattern {slug!r} targets a {st!r} axis — "
              f"not applied (only active axes receive DET membership).")
    return axis_patterns, prefilter_patterns, lattice_rows


compute_full_hits = _text_match.compute_full_hits


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
#
# S11: the slug constants and the quote-base mapping are the DET-record owner's
# (`codebook_det_patterns`); these names are the same objects.
_ENTERS_TAPPED_BASE_SLUG = _det_patterns.ENTERS_TAPPED_BASE_SLUG
_ENTERS_TAPPED_COND_SLUG = _det_patterns.ENTERS_TAPPED_COND_SLUG
_IMPOSES_SLUG = _det_patterns.IMPOSES_SLUG


def _base_pattern_src(slug_key: str) -> str:
    for s, pattern_src, _ in probe.PATTERNS:
        if s == slug_key:
            return pattern_src
    fc.halt(f"could not find base pattern source for {slug_key!r} in foundry_det_patterns_probe.PATTERNS")


# The pattern whose match IS the evidence clause for an axis is decided by
# `codebook_det_patterns.quote_pattern_src`; the BASE sources it may need are
# the probe's, so this shell injects its own `_base_pattern_src` (looked up at
# call time) and keeps the legacy one-argument name.
_QUOTE_BASE_SLUG = _det_patterns.QUOTE_BASE_SLUG


def quote_pattern_src(p: dict) -> str:
    return _det_patterns.quote_pattern_src(p, lambda key: _base_pattern_src(key))


matched_clause = _text_match.matched_clause


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
    disagreement = _det_apply.lattice_cache_disagreement(lattice_quotes, full_hits)
    if disagreement:
        fc.halt(disagreement)

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

    # Virtual-node instantiation, grammar sec.11.2 -- the semantics are
    # `codebook_det_apply.instantiate_lattice_axes`.
    parent_scopes = lattice_parent_scopes(axes)
    instantiated = _halting(_det_apply.instantiate_lattice_axes, axes,
                            lattice_quotes, parent_scopes)
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

    # S11: the A8 assertion operation is `codebook_det_apply.apply_axis_patterns`.
    # The quote source and the owner resolver are this shell's, injected and
    # looked up at the moment they are called.
    applied = _halting(_det_apply.apply_axis_patterns, axes, axis_patterns,
                       full_hits, lattice_quotes, texts, corpus_ref,
                       quote_pattern_src=lambda p: quote_pattern_src(p),
                       resolve_owner=resolve_owner)

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
