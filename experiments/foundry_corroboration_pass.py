#!/usr/bin/env python3
"""Corroboration pass -- PRE-BUILT, NOT RUN (Captain directive, 2026-08-01,
point 3). Runs AFTER the full-corpus SYNTH pass (step 6), never before:
takes the flagged subset of that pass's output, re-packs it with DIFFERENT
neighbors and a DIFFERENT shuffle than the original pass, and re-submits.
Agreement between the original and corroboration result for a card becomes
a "corroborated" provenance note; divergence becomes a halt-loudly review
row (never silently resolved either way -- same discipline as every other
halt-loudly gate in this pipeline).

Flagged-subset criteria (four categories, per Captain's directive):
  1. DET-SYNTH contradiction rows -- a DET pattern's verdict for a card
     disagrees with SYNTH's own labeling for the same card/axis.
  2. Free-lane-heavy cards -- SYNTH found little to no existing-codebook
     coverage (this module's flag_free_lane_heavy() default: ALL of a
     card's axes are lane=free, i.e. zero codebook/codebook-grammar hits --
     stricter than "majority free", see the projection note below on why).
  3. Validator-rejected grammar compositions -- lane=codebook-grammar
     labels that failed validate_slug.py and were downgraded to lane=free
     (foundry_consolidate.py's D7 wiring already records these as
     anomalies; this module just re-selects them for corroboration).
  4. Tail-position cards -- ONLY included if batch 8's tail-decay check
     (foundry_batch8_diff.tail_decay_check) shows >5pp drop for whichever
     N the full pass ends up using (a stricter trigger than batch 8's own
     10pp acceptance-gate threshold -- 5pp here is "worth corroborating,"
     10pp there is "reject the architecture").

This module builds the re-packing + comparison machinery now (fully
functional, reuses foundry_stage1b.build_packed_request) so it's ready the
moment the full pass exists to feed it. It does not run anything -- there
is no `main()` that submits a batch. flag_*() functions operate on
real full-pass output once that exists; until then they're documented,
typed, and byte-compilable, not executable against real data.
"""
import sys
import json
import random
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402
import foundry_stage1b as s1b  # noqa: E402

# Deliberately DIFFERENT from foundry_stage1b.PACK_SHUFFLE_SEED (20260731)
# and from any batch-8 seed -- the whole point of the corroboration pass is
# DIFFERENT neighbors and DIFFERENT positions than the original pass, so
# reusing the same seed (which would reproduce the identical packs, per
# pack_oracle_ids' own determinism) would defeat it.
CORROBORATION_SHUFFLE_SEED = 20260802
CORROBORATION_PACK_SIZE = 20  # matches whichever N the full pass adopts; override at call time if different


def flag_det_synth_contradictions(det_membership: dict, synth_results: dict) -> set:
    """det_membership: {oid: set(det-assigned axis slugs)}. synth_results:
    {oid: set((lane, label))} from the full pass. A contradiction is a card
    where DET assigned axis X but SYNTH's own labeling for that card
    contains NO lane=codebook hit on X at all (SYNTH silently missed or
    disagreed with a DET-decided membership) -- returns the flagged oid
    set. No historical baseline exists for this rate (DET patterns are new
    this session, never run against real SYNTH output before); this
    function is real and callable, but its RATE is unmeasured until both
    the DET pass and the SYNTH pass have real output -- see the projection
    note in this module's docstring / the session report."""
    flagged = set()
    for oid, det_slugs in det_membership.items():
        synth_axes = synth_results.get(oid, set())
        synth_codebook_labels = {label for lane, label in synth_axes if lane == "codebook"}
        if det_slugs - synth_codebook_labels:
            flagged.add(oid)
    return flagged


def flag_free_lane_heavy(synth_results: dict) -> set:
    """ALL of a card's axes are lane=free (zero codebook/codebook-grammar
    hits) -- stricter than "majority free" deliberately: batch-6/7's real
    historical rate for "majority free" is 56.8% of all cards and for
    "100% free" is 47.2% (both measured directly from
    stage1b_raw_results_batch{6,7}.jsonl) -- either reading taken at face
    value would flag roughly HALF the corpus, which defeats the point of a
    targeted follow-up pass. Both numbers are almost certainly an
    OVERESTIMATE of what the full pass will show anyway, since batch 6/7
    ran against a much less mature codebook than the one the full pass
    will use -- not usable as a reliable full-pass projection either way,
    see the projection note below."""
    flagged = set()
    for oid, axes in synth_results.items():
        if axes and all(lane == "free" for lane, _ in axes):
            flagged.add(oid)
    return flagged


def flag_validator_rejected_grammar(consolidation_anomalies: list) -> set:
    """consolidation_anomalies: foundry_consolidate.load_raw_instances()'s
    `anomalies` list from the full pass. Selects the subset whose reason
    string matches the D7 lane=codebook-grammar validation-failure shape
    (see foundry_consolidate.py's own anomaly-reason text) -- these are
    cards where SYNTH attempted a grammar composition and validate_slug.py
    rejected it; corroboration re-checks whether the underlying pattern
    judgment was sound even though the slug wasn't. No historical baseline
    exists (lane=codebook-grammar is new this session)."""
    flagged = set()
    for a in consolidation_anomalies:
        if "lane=codebook-grammar" in a.get("reason", "") and "validate_slug failed" in a.get("reason", ""):
            flagged.add(a["oracle_id"])
    return flagged


def flag_tail_position_cards(full_pass_pack_map: dict, tail_decay_report: dict,
                              decay_threshold_pp: float = 5.0, early_positions: int = 5) -> set:
    """full_pass_pack_map: {oid: (pack_idx, position)} for the full pass's
    OWN packing (same shape as foundry_batch8_diff.load_pack_position_maps'
    output, but for the real 32,557-card run, not batch 8's 1,200).
    tail_decay_report: batch 8's own tail_decay_check() output for the N
    the full pass used -- if worst_drop_pp <= decay_threshold_pp, returns
    an EMPTY set (no tail-position corroboration needed at all). Otherwise
    flags every card whose position is AT OR PAST the position where batch
    8's curve first crossed the threshold (a conservative "everything from
    here back is suspect" cut, not just the single worst position)."""
    letter_report = tail_decay_report.get("packed", tail_decay_report)
    worst_drop_pp = letter_report.get("worst_drop_pp")
    if worst_drop_pp is None or worst_drop_pp <= decay_threshold_pp:
        return set()
    cutoff_position = letter_report.get("decay_onset_position")
    if cutoff_position is None:
        fc.halt("tail_decay_report shows a decay beyond threshold but no decay_onset_position was supplied -- "
                 "refusing to guess where the tail starts")
    return {oid for oid, (_, pos) in full_pass_pack_map.items() if pos >= cutoff_position}


def build_corroboration_packs(flagged_oracle_ids: set, cards: dict, pack_size: int = CORROBORATION_PACK_SIZE) -> list:
    """Re-packs the flagged subset with a DIFFERENT seed than any prior
    pass -- different neighbors (which cards end up together) AND
    different positions (where each card lands within its new pack), both
    following from the different seed's shuffle-then-chunk, same mechanism
    as foundry_stage1b.pack_oracle_ids() but deliberately not calling it
    (that function is pinned to PACK_SHUFFLE_SEED as standing production
    behavior; corroboration needs its own independent seed)."""
    ids = sorted(flagged_oracle_ids)  # sort first for a deterministic PRE-shuffle order
    shuffled = list(ids)
    random.Random(CORROBORATION_SHUFFLE_SEED).shuffle(shuffled)
    packs = [shuffled[i:i + pack_size] for i in range(0, len(shuffled), pack_size)]

    packed_prompt = s1b.build_packed_system_prompt(pack_size)
    requests = []
    for i, pack in enumerate(packs):
        req = s1b.build_packed_request(f"corrob-pack{i}", pack, cards, packed_prompt)
        requests.append(req)
    return requests


def compare_corroboration(original_results: dict, corroboration_results: dict) -> dict:
    """original_results / corroboration_results: {oid: set((lane, label))}.
    Returns {oid: {"verdict": "corroborated"|"halt_loudly", "original":
    [...], "corroboration": [...]}}. agreement (identical axis sets) ->
    corroborated provenance note; ANY divergence -> halt_loudly review row,
    never silently resolved toward either side."""
    out = {}
    for oid, orig_axes in original_results.items():
        corrob_axes = corroboration_results.get(oid)
        if corrob_axes is None:
            out[oid] = {"verdict": "missing_corroboration_result", "original": sorted(orig_axes)}
            continue
        if orig_axes == corrob_axes:
            out[oid] = {"verdict": "corroborated", "original": sorted(orig_axes)}
        else:
            out[oid] = {
                "verdict": "halt_loudly",
                "original": sorted(orig_axes),
                "corroboration": sorted(corrob_axes),
                "only_in_original": sorted(orig_axes - corrob_axes),
                "only_in_corroboration": sorted(corrob_axes - orig_axes),
            }
    return out


# No main(). This module is imported and called once the full pass exists;
# it does not submit anything on its own. See the session report for the
# projected card count / cost (category 4 only -- categories 1-3 have no
# reliable pre-pass projection, computed for real once the full pass runs).
