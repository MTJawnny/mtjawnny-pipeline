"""The frozen-panel evaluation — a measurement, and only a measurement.

## What this is

Path E milestone 2's third piece. It runs `mtj_foundry.retrieval` against the
named-correct neighbour lists that a human froze in
`docs/WIRE-PREDICTIONS-2026-08-09.md` **before** the 2026-08-09 wire experiment
existed, and reports what happened.

It grades nothing else, and it decides nothing. A poor result here is a valid
milestone-2 outcome and is reported at full volume; the task that authorised
this module says so in those words, and the historical result document it draws
its panel from is itself a recorded failure that was not tuned away.

## The three numbers this keeps apart, because collapsing them is the failure

1. **Candidate discovery.** Can the selected evidence reach this named-correct
   card AT ALL, from this anchor? That is a question about the codebook's
   coverage and has nothing to do with ordering.
2. **Presentation.** For the ones it can reach, where does the declared default
   ordering put them? That is a question about the ranking policy, and it is
   only askable about a card discovery already found.
3. **Absence.** A named-correct card the evidence cannot reach is reported as
   `NOT_DISCOVERABLE_FROM_SELECTED_EVIDENCE` and is **never scored negatively**.
   It is not given rank infinity, not counted as a wrong answer, and not folded
   into an average. The selected codebook covers 6,275 of 38,233 corpus ids;
   most absence here is unreviewed, and a metric that punished it would be
   measuring the review backlog while claiming to measure similarity.

`WIRE-RESULT-2026-08-09.md` is the reason the split is structural rather than a
convention. Its whole finding was that one blended number hid two opposite
effects — an axis at 100% recall that moved nothing, and a broad axis that moved
everything in the wrong direction — and no single figure could have shown that.

## What it does NOT do

No model is called and no relevance label is invented: every name it grades
against was transcribed from the frozen document into
`refoundation/path-e/m2-evaluation.json`, whose recorded source blob id is
checked against the tracked file. The ordering it measures was declared in
`retrieval.ORDERING_RULE` before this ran and is not adjusted afterwards. The
evaluation writes no canonical state, mutates nothing, and confers no permission
on any later milestone.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from mtj_foundry import __version__, evidence_index, retrieval

__all__ = [
    "EVALUATION_SCHEMA",
    "PANEL_SCHEMA",
    "PanelError",
    "evaluate",
    "git_blob_sha",
    "load_panel",
    "render_evaluation",
]

EVALUATION_SCHEMA = "mtj-foundry-m2-evaluation/1"
PANEL_SCHEMA = "mtj-foundry-m2-evaluation-panel/1"

# The three per-card verdicts. `NOT_DISCOVERABLE_FROM_SELECTED_EVIDENCE` is the
# one that carries the milestone's whole argument: it is an ABSENCE, and it is
# reported as an absence rather than as a failure.
DISCOVERABLE = "DISCOVERABLE_FROM_SELECTED_EVIDENCE"
NOT_DISCOVERABLE = "NOT_DISCOVERABLE_FROM_SELECTED_EVIDENCE"
NOT_IN_CORPUS = "NOT_IN_SELECTED_CORPUS"

TOP_K = (10, 25)


class PanelError(retrieval.RetrievalError):
    """The frozen panel is missing, unreadable, or not the expected schema."""


def git_blob_sha(path) -> str:
    """The git object id of a file's exact bytes, DERIVED rather than shelled out.

    `sha1("blob <length>\0" + content)` is git's own object identity, so this is
    the same value `git rev-parse HEAD:<path>` prints for an unmodified tracked
    file — computed here with stdlib only, because the query side of this
    milestone must not need a repository, a git binary or a subprocess.

    It is used for ONE thing: proving the frozen panel fixture still names the
    bytes it was transcribed from. A panel whose recorded source id no longer
    matches the tracked document has either had its source edited or been
    re-pointed, and both are events a reviewer must see rather than infer.
    """
    content = Path(path).read_bytes()
    digest = hashlib.sha1()
    digest.update(b"blob " + str(len(content)).encode("ascii") + b"\0")
    digest.update(content)
    return digest.hexdigest()


def load_panel(path) -> dict:
    """Read the frozen panel fixture. Schema-gated, never repaired."""
    path = Path(path)
    try:
        with open(path, "r", encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PanelError(
            f"evaluation panel at {path}: {type(error).__name__}: {error}") from error
    if not isinstance(document, dict) or document.get("schema") != PANEL_SCHEMA:
        raise PanelError(
            f"{path}: unexpected schema {document.get('schema') if isinstance(document, dict) else type(document).__name__!r}, "
            f"expected {PANEL_SCHEMA!r}")
    return document


def _resolve(view: retrieval.EvidenceIndexView, name: str):
    """`(oracle_id, status)`. Ambiguity HALTS rather than resolving.

    A shared normalized name is a real property of this corpus — 216 of them —
    and picking one id would answer a question about a different card while
    reporting a number about this one.
    """
    matches = view.resolve_name(name)
    if not matches:
        return None, NOT_IN_CORPUS
    if len(matches) > 1:
        raise retrieval.AmbiguousNameError(name, matches)
    return matches[0], None


def _card_evidence_state(view: retrieval.EvidenceIndexView, oracle_id: str) -> dict:
    """A card's own selected-evidence state, independent of any anchor."""
    row = view.cards[oracle_id]
    return {
        "oracle_id": oracle_id,
        "name": row["name"],
        "evidence_state": row["evidence_state"],
        "active_membership_count": len(row["memberships"]),
        "active_axis_ids": [m["axis_id"] for m in row["memberships"]],
    }


def _grade_anchor(view: retrieval.EvidenceIndexView, anchor_spec: dict) -> dict:
    """One panel anchor: discovery, then presentation, then absence. In that order."""
    anchor_id, status = _resolve(view, anchor_spec["name"])
    if anchor_id is None:
        return {"label": anchor_spec["label"], "name": anchor_spec["name"],
                "anchor_status": status,
                "note": "the anchor itself is not in the selected corpus; nothing "
                        "below it can be measured"}

    result = retrieval.query(view.document, oracle_id=anchor_id, view=view)
    by_id = {c["oracle_id"]: c for c in result["candidates"]}

    graded = []
    for name in anchor_spec["named_correct"]:
        oracle_id, status = _resolve(view, name)
        if oracle_id is None:
            graded.append({"named_correct": name, "status": status,
                           "scored_negatively": False})
            continue
        candidate = by_id.get(oracle_id)
        if candidate is None:
            graded.append({
                "named_correct": name,
                "oracle_id": oracle_id,
                "status": NOT_DISCOVERABLE,
                "scored_negatively": False,
                "why": ("the anchor and this card share no ACTIVE axis in the "
                        "selected codebook. that is an absence of evidence about "
                        "this pair, not evidence that they are unalike"),
                "card_evidence_state": _card_evidence_state(view, oracle_id),
            })
            continue
        graded.append({
            "named_correct": name,
            "oracle_id": oracle_id,
            "status": DISCOVERABLE,
            "shared_axis_ids": candidate["features"]["shared_axis_ids"],
            "shared_axis_count": candidate["features"]["shared_axis_count"],
            "shared_axis_cardinalities":
                candidate["features"]["shared_axis_cardinalities"],
            "presentation": {
                "rank": candidate["rank"],
                **{f"in_top_{k}": candidate["rank"] <= k for k in TOP_K},
                "tie_block_size": candidate["tie_block_size"],
                "tie_block_first_rank": candidate["tie_block_first_rank"],
                "rank_is_meaningful_within_tie_block": candidate["tie_block_size"] == 1,
            },
        })

    discoverable = [g for g in graded if g["status"] == DISCOVERABLE]
    absent = [g for g in graded if g["status"] != DISCOVERABLE]
    head = result["candidates"][:TOP_K[0]]
    return {
        "label": anchor_spec["label"],
        "name": anchor_spec["name"],
        "oracle_id": anchor_id,
        "document_axis_annotation": anchor_spec.get("document_axis_annotation"),
        "document_axis_annotation_used": False,
        "anchor_evidence": {
            "result_state": result["result_state"],
            "active_memberships": [
                {"axis_id": m["axis_id"],
                 "axis_active_member_count": m["axis_active_member_count"]}
                for m in result["anchor"]["active_memberships"]],
        },
        "candidate_pool_size": result["candidate_count"],
        "candidate_discovery": {
            "named_correct_total": len(graded),
            "discoverable": len(discoverable),
            "not_discoverable": len(absent),
            "recall": (round(len(discoverable) / len(graded), 4) if graded else None),
            "recall_denominator_is": "the frozen named-correct list for this anchor",
        },
        "presentation": {
            "measured_over": "discoverable named-correct cards ONLY",
            **{f"named_correct_in_top_{k}":
               sum(1 for g in discoverable if g["presentation"][f"in_top_{k}"])
               for k in TOP_K},
            "top_10_is_a_slice_of_tie_blocks": sorted(
                {c["tie_block_first_rank"] for c in head}),
            "top_10": [{"rank": c["rank"], "name": c["name"],
                        "oracle_id": c["oracle_id"],
                        "shared_axis_count": c["features"]["shared_axis_count"],
                        "shared_axis_cardinalities":
                            c["features"]["shared_axis_cardinalities"],
                        "tie_block_size": c["tie_block_size"],
                        "tie_block_first_rank": c["tie_block_first_rank"]}
                       for c in head],
        },
        "named_correct": graded,
    }


def _grade_control(view: retrieval.EvidenceIndexView, control_spec: dict) -> dict:
    """A control: it must acquire NO fabricated semantic evidence.

    The check is a positive one about what the artifact records, not "did the
    output change" — there is no before-state here to diff against. A control
    that carries active memberships in the selected codebook is REPORTED as
    carrying them; that would be a fact about the codebook, not a fabrication,
    and hiding it would be the tuning this milestone is forbidden.
    """
    oracle_id, status = _resolve(view, control_spec["name"])
    if oracle_id is None:
        return {"label": control_spec["label"], "name": control_spec["name"],
                "status": status}
    result = retrieval.query(view.document, oracle_id=oracle_id, view=view)
    state = _card_evidence_state(view, oracle_id)
    unassigned = (state["evidence_state"]
                  == evidence_index.EVIDENCE_STATE_UNASSIGNED)
    return {
        "label": control_spec["label"],
        "name": control_spec["name"],
        "oracle_id": oracle_id,
        "document_statement": control_spec.get("document_statement"),
        "selected_evidence": state,
        "result_state": result["result_state"],
        "candidate_count": result["candidate_count"],
        "fabricated_semantic_evidence": False,
        "fabricated_semantic_evidence_basis": (
            "every membership reported for this card was copied from the selected "
            "codebook; the retrieval layer creates none, and an unassigned control "
            "returns an explicit no-evidence result with zero candidates"),
        "unassigned_and_empty": bool(unassigned and result["candidate_count"] == 0),
    }


def _grade_probes(view: retrieval.EvidenceIndexView, panel: dict,
                  anchor_results: list) -> dict:
    """The historical failure probes, reported as ABSENCE where absence is the fact.

    Each probe is reported against EVERY panel anchor rather than only the one
    its source section discussed. That is deliberate: choosing the "relevant"
    anchor would be this module making a semantic judgement, and the full cross
    product is seven rows by four anchors, which is small enough to just print.
    """
    anchor_ids = [(a["label"], a["name"], a.get("oracle_id")) for a in anchor_results]
    rows = []
    for probe in panel["known_failure_probes"]["probes"]:
        oracle_id, status = _resolve(view, probe["name"])
        if oracle_id is None:
            rows.append({"name": probe["name"], "status": status})
            continue
        against = []
        for label, anchor_name, anchor_id in anchor_ids:
            if anchor_id is None:
                continue
            result = retrieval.query(view.document, oracle_id=anchor_id, view=view)
            match = next((c for c in result["candidates"]
                          if c["oracle_id"] == oracle_id), None)
            against.append({
                "anchor_label": label,
                "anchor_name": anchor_name,
                "status": DISCOVERABLE if match else NOT_DISCOVERABLE,
                "rank": match["rank"] if match else None,
                "shared_axis_ids": (match["features"]["shared_axis_ids"]
                                    if match else []),
            })
        rows.append({
            "name": probe["name"],
            "source_section": probe.get("source_section"),
            "historical_finding": probe.get("historical_finding"),
            "selected_evidence": _card_evidence_state(view, oracle_id),
            "against_panel_anchors": against,
        })
    return {
        "what_these_are": panel["known_failure_probes"]["what_these_are"],
        "reported_as": ("presence or ABSENCE in the selected evidence. a probe that "
                        "is not discoverable is reported as not discoverable, never "
                        "as a low-ranked candidate — which is the exact disguise the "
                        "2026-08-09 result document warns about"),
        "probes": rows,
    }


def evaluate(document: dict, panel: dict, *, panel_source_blob_sha: str = None,
             panel_source_blob_sha_verified: bool = None) -> dict:
    """Run the whole frozen panel over one index artifact. Pure and deterministic."""
    view = retrieval.EvidenceIndexView(document)
    anchors = [_grade_anchor(view, spec) for spec in panel["anchors"]]
    controls = [_grade_control(view, spec) for spec in panel["controls"]]
    probes = _grade_probes(view, panel, anchors)

    graded = [g for a in anchors for g in a.get("named_correct", [])]
    discoverable = [g for g in graded if g["status"] == DISCOVERABLE]

    return {
        "schema": EVALUATION_SCHEMA,
        "generator": {"package": "mtj_foundry", "version": __version__,
                      "capability": "frozen_panel_retrieval_evaluation"},
        "evaluation_is": (
            "A MEASUREMENT. it is not semantic authority, it is not a quality "
            "ruling, and it is not permission for any later milestone. a poor "
            "result here is a valid outcome and has not been tuned away"),
        "panel": {
            "id": panel.get("id"),
            "schema": panel.get("schema"),
            "source_document": panel["source"]["document"],
            "source_git_blob_sha": panel["source"]["git_blob_sha"],
            "source_blob_sha_measured": panel_source_blob_sha,
            "source_blob_sha_verified": panel_source_blob_sha_verified,
            "labels_are": ("transcribed from a human precommit written before the "
                           "2026-08-09 experiment. no model invented any of them"),
        },
        "index": {
            "schema": document.get("schema"),
            "selected_codebook_sha256":
                document["selected_inputs"]["codebook"]["measured_sha256"],
            "selected_corpus_sha256":
                document["selected_inputs"]["corpus"]["measured_sha256"],
            "corpus_ids_total": document["conservation"]["coverage"]["corpus_ids_total"],
            "corpus_ids_covered":
                document["conservation"]["coverage"]["corpus_ids_covered"],
            "corpus_ids_uncovered":
                document["conservation"]["coverage"]["corpus_ids_uncovered"],
        },
        "ordering": retrieval.ORDERING_RULE,
        "aggregate_candidate_discovery": {
            "named_correct_total": len(graded),
            "discoverable": len(discoverable),
            "not_discoverable": len(graded) - len(discoverable),
            "recall": (round(len(discoverable) / len(graded), 4) if graded else None),
            "recall_is": ("candidate DISCOVERY recall only. it says nothing about "
                          "where a discovered card was placed, and a not-discoverable "
                          "card is an absence of evidence, never a wrong answer"),
        },
        "aggregate_presentation": {
            "measured_over": "discoverable named-correct cards ONLY",
            "discoverable_total": len(discoverable),
            **{f"in_top_{k}": sum(1 for g in discoverable
                                  if g["presentation"][f"in_top_{k}"])
               for k in TOP_K},
            "in_a_tie_block_larger_than_one": sum(
                1 for g in discoverable
                if g["presentation"]["tie_block_size"] > 1),
        },
        "anchors": anchors,
        "controls": controls,
        "known_failure_probes": probes,
        "what_this_does_not_prove": [
            "that the selected evidence is sufficient for a product",
            "that the declared ordering is the right ordering, or a ratified one",
            "that a not-discoverable card is dissimilar to its anchor",
            "that a discoverable card is similar to its anchor beyond the shared "
            "axis the codebook records",
            "that any later milestone is authorised",
        ],
    }


def render_evaluation(evaluation: dict) -> str:
    """`indent=2`, `ensure_ascii=False`, one trailing newline — a page for a reader."""
    return json.dumps(evaluation, indent=2, ensure_ascii=False) + "\n"
