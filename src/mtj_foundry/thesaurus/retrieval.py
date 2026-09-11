"""Evidence-only retrieval — a derived layer over the index, never inside it.

## What this is

Path E milestone 2's second half. It answers one bounded question:

> *Given an anchor card, which cards does the SELECTED EVIDENCE connect it to,
> and what exactly is the evidence that connected them?*

The candidate rule for this milestone is deliberately narrow and is stated in
one line: **a candidate is evidence-discoverable when the anchor and the
candidate share at least one ACTIVE axis in the selected codebook.** Nothing
else generates a candidate. There is no text similarity, no embedding, no tier
label, no learned feature and no model call anywhere in this file.

## Why this is a separate module from the index

Because the index must not become a ranking policy. `WIRE-RESULT-2026-08-09.md`
is the measured reason: the last time membership was wired into a scorer, the
derived term did not rank, it PARTITIONED — into "reviewed" and "not yet
reviewed" — and every named-correct neighbour not on the anchor's axis was
demoted, without exception across 33 graded cards. That failure was invisible
because the policy and the facts were the same object. Here they are two, the
index is the one that gets published, and every candidate carries the raw
features so a reviewer can re-rank from the artifact and check the ordering
rather than trust it.

## THE ORDERING RULE, DECLARED IN FULL

Fixed before the frozen evaluation panel was ever run, and not to be adjusted
after seeing its result. Candidates are sorted by:

1. `shared_axis_count` **descending** — more shared positive evidence first;
2. `shared_axis_cardinalities` **ascending, lexicographically** — the list of
   each shared axis's active member count in the selected codebook, sorted
   ascending. A candidate whose sharpest shared axis is smaller sorts first, and
   ties fall through to the next-sharpest. Rule 1 has already equalised the
   lengths, so the comparison is always between lists of the same size;
3. `oracle_id` **ascending** — an arbitrary but deterministic identity
   tie-break that carries NO semantics.

**There is no constant in that rule.** No weight, no threshold, no DF ceiling,
no tuning knob — every term is a raw count read off the artifact, which is what
keeps it out of "every scoring constant is a ratified ruling" territory. It is
still a POLICY and it is still unratified; it is a default presentation order
for a measurement, not a ruling about similarity.

**Rank 3 orders a tie block, and a tie block is not a ranking.** Every candidate
carries `tie_block_size` and `tie_block_first_rank`, because the last
measurement's clearest product finding was that a shipped top-10 was an
alphabetical slice of a 44-row score tie and read as if it were ranked. A
consumer that shows the head of a 40-wide tie block is showing an arbitrary
sample, and the artifact says so per row.

## Positive evidence only — what that forbids, precisely

* A candidate that shares no active axis with the anchor is simply **not
  returned**. It is not returned with a low score, and nothing in the result
  says anything about it. Absence in a result is absence of evidence.
* A non-shared axis contributes **zero**. The ordering key reads only the SHARED
  axes and the candidate's own id, so no membership a candidate lacks can lower
  its rank, and no membership it holds elsewhere can either.
* An **UNASSIGNED anchor returns no candidates and says so as its own result
  state.** It does not fabricate neighbours, and it does not claim the card has
  none — those are different sentences and the second one is not true.

## One honest asymmetry, named rather than hidden

Rule 2 reads an axis's CARDINALITY, which is a property of the axis and
therefore moves when any other card joins or leaves it. That is a specificity
feature over positive evidence, not a penalty for absence — but it does mean one
card's membership can change another card's ORDER, and `WIRE-RESULT` §7 records
a live instance of the hazard: 88 Alchemy (`A-`) memberships sit on 51 active
axes, 48 of them duplicate pairs with their own paper twin, inflating exactly
this number. The measurement is reported with that property intact rather than
corrected for, because correcting it would be a codebook mutation.
"""

from __future__ import annotations

import json
from pathlib import Path

from mtj_foundry import __version__, runtime
from mtj_foundry.corpus import normalize_name
from mtj_foundry.evidence import index as evidence_index

__all__ = [
    "AmbiguousNameError",
    "IndexAccessError",
    "IndexSchemaError",
    "ORDERING_RULE",
    "RESULT_STATE_ASSIGNED",
    "RESULT_STATE_UNASSIGNED",
    "RETRIEVAL_SCHEMA",
    "RetrievalError",
    "UnknownAnchorError",
    "EvidenceIndexView",
    "load_index",
    "query",
    "render_result",
]

RETRIEVAL_SCHEMA = "mtj-foundry-evidence-retrieval/1"

RESULT_STATE_ASSIGNED = "ANCHOR_HAS_ACTIVE_EVIDENCE"
RESULT_STATE_UNASSIGNED = "ANCHOR_UNASSIGNED_NO_ACTIVE_EVIDENCE"

# The declared policy, carried into every result so a reader never has to find
# this file to know how the rows were ordered.
ORDERING_RULE = {
    "declared_before": "the frozen milestone-2 evaluation panel was run",
    "keys": [
        "1. shared_axis_count DESCENDING",
        "2. shared_axis_cardinalities ASCENDING, lexicographically (each shared "
        "axis's active member count in the selected codebook, sorted ascending)",
        "3. oracle_id ASCENDING — arbitrary, deterministic, carries no semantics",
    ],
    "constants": "NONE. every term is a raw count read from the index artifact",
    "uses_no": ["learned or model-generated features", "legacy tier labels",
                "text similarity", "thresholds or magic numbers",
                "any penalty for a membership a candidate does not have"],
    "is": ("an UNRATIFIED default presentation order for a measurement, not a "
           "ruling about similarity and not authority"),
    "tie_blocks": ("candidates equal under keys 1 and 2 form a tie block that key 3 "
                   "orders arbitrarily. every row carries tie_block_size and "
                   "tie_block_first_rank so a tie is never read as a ranking"),
}


class RetrievalError(runtime.FoundryRuntimeError):
    """Base for this layer's typed refusals.

    Hung under the milestone-1 runtime base ON PURPOSE: the installed command's
    exit contract already translates that lineage into `STOP — …` on stderr with
    exit 1 and nothing on stdout, and a query that cannot find its anchor is the
    same KIND of event as a run that cannot find its corpus — a fact about the
    operator's input, visible and fixable.
    """


class IndexAccessError(RetrievalError):
    """The index artifact could not be read, decoded or parsed as JSON."""


class IndexSchemaError(RetrievalError):
    """The document is not an `mtj-foundry-evidence-index/1`."""


class UnknownAnchorError(RetrievalError):
    """No card in the index carries the requested oracle_id or name.

    NOT the same as an unassigned anchor, and the distinction is the whole point.
    "This corpus has no such card" and "this card has no active evidence" are
    different facts, and collapsing them would let a typo read as a measurement.
    """


class AmbiguousNameError(RetrievalError):
    """A normalized name maps to more than one oracle_id. Carries them all.

    HALT-LOUDLY, never disambiguate. 216 normalized names in the selected corpus
    are shared by more than one id, 709 ids among them, and picking one would
    quietly answer a question about a different card — including the paper /
    `A-` Alchemy variant pairs the house rules already have a stated preference
    about. `oracle_id` is the only card key; a name is a lookup convenience.
    """

    def __init__(self, name: str, oracle_ids: list):
        self.name = name
        self.oracle_ids = list(oracle_ids)
        super().__init__(
            f"the name {name!r} matches {len(self.oracle_ids)} oracle_ids "
            f"({', '.join(self.oracle_ids)}) — refusing to pick one; query by "
            f"oracle_id, which is the only card key")


def load_index(path) -> dict:
    """Read an emitted index artifact. Schema-gated, and nothing else is read.

    This is the only file this module opens. No repository root, no codebook, no
    corpus and no authority selector — once the artifact exists it is the whole
    input, which is the property milestone 3 would need and the reason the
    milestone-2 acceptance copies one outside the repository and queries it
    there.
    """
    path = Path(path)
    try:
        with open(path, "r", encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise IndexAccessError(
            f"evidence index at {path}: {type(error).__name__}: {error}") from error
    if not isinstance(document, dict):
        raise IndexSchemaError(
            f"{path}: the index is a {type(document).__name__}, expected a JSON object")
    schema = document.get("schema")
    if schema != evidence_index.INDEX_SCHEMA:
        raise IndexSchemaError(
            f"{path}: unexpected schema {schema!r}, expected "
            f"{evidence_index.INDEX_SCHEMA!r}")
    return document


class EvidenceIndexView:
    """Lookup structures over one loaded artifact. Builds nothing semantic.

    Three maps, all derived mechanically from rows the artifact already carries:
    id -> row, axis -> member ids, and the artifact's own stored name index. The
    stored one is used rather than a rebuilt one so the name semantics stay
    EXACTLY the corpus capability's — every id kept for a shared name, in
    first-seen corpus order — instead of quietly becoming this module's.
    """

    def __init__(self, document: dict):
        self.document = document
        self.axes = document["axes"]
        self.cards = {row["oracle_id"]: row for row in document["cards"]}
        self.name_index = document["name_index"]
        self.axis_members: dict = {}
        for row in document["cards"]:
            for membership in row["memberships"]:
                self.axis_members.setdefault(
                    membership["axis_id"], []).append(row["oracle_id"])

    def resolve_name(self, name: str) -> list:
        """Every oracle_id for a normalized name, ambiguity preserved."""
        return list(self.name_index.get(normalize_name(name), []))

    def anchor_id(self, *, oracle_id: str = None, name: str = None) -> str:
        """One oracle_id, or a typed refusal. Never a guess.

        An id that is not in the index is `UnknownAnchorError` rather than an
        empty result: an empty result would be indistinguishable from a card
        with no evidence, which is the one confusion this whole milestone is
        built to prevent.
        """
        if (oracle_id is None) == (name is None):
            raise RetrievalError(
                "state exactly one of an anchor oracle_id or an anchor name")
        if oracle_id is not None:
            if oracle_id not in self.cards:
                raise UnknownAnchorError(
                    f"oracle_id {oracle_id!r} is not in this index — it is not a "
                    f"card of the selected corpus. this is NOT the same as a card "
                    f"with no active evidence")
            return oracle_id
        matches = self.resolve_name(name)
        if not matches:
            raise UnknownAnchorError(
                f"no card in this index is named {name!r} — this is NOT the same "
                f"as a card with no active evidence")
        if len(matches) > 1:
            raise AmbiguousNameError(name, matches)
        return matches[0]


def _shared_axes(view: EvidenceIndexView, anchor_row: dict, candidate_id: str) -> list:
    anchor_axes = {m["axis_id"] for m in anchor_row["memberships"]}
    candidate_row = view.cards[candidate_id]
    return sorted(anchor_axes & {m["axis_id"] for m in candidate_row["memberships"]})


def _membership_on(row: dict, axis_id: str) -> dict:
    for membership in row["memberships"]:
        if membership["axis_id"] == axis_id:
            return membership["member"]
    raise RetrievalError(
        f"{row['oracle_id']} has no membership on {axis_id!r} — the index's "
        f"axis->member map and its rows disagree, which is a defect in the "
        f"artifact and not an operator input state")


def _candidate(view: EvidenceIndexView, anchor_row: dict, candidate_id: str,
               shared: list) -> dict:
    """One candidate with its RAW FEATURES exposed before any presentation order.

    The evidence block carries BOTH members' stored assertions on each shared
    axis — the anchor's and the candidate's — because "why was this returned" is
    answered by the pair, not by one side of it. That is what makes a result
    explainable from the index alone: every quote, source_ref, corpus_ref,
    evidence_status and locality below was copied out of the artifact and can be
    checked against it row by row.
    """
    candidate_row = view.cards[candidate_id]
    evidence = []
    for axis_id in shared:
        axis = view.axes[axis_id]
        evidence.append({
            "axis_id": axis_id,
            "axis_definition": axis.get("definition"),
            "axis_scope": axis.get("scope"),
            "axis_source": axis.get("source"),
            "axis_active_member_count": axis["active_member_count"],
            "anchor_member": _membership_on(anchor_row, axis_id),
            "candidate_member": _membership_on(candidate_row, axis_id),
        })
    cardinalities = sorted(e["axis_active_member_count"] for e in evidence)
    return {
        "oracle_id": candidate_id,
        "name": candidate_row["name"],
        "gate0_eligible": candidate_row["gate0_eligible"],
        "features": {
            "shared_axis_ids": list(shared),
            "shared_axis_count": len(shared),
            "shared_axis_cardinalities": cardinalities,
            "candidate_total_active_memberships": len(candidate_row["memberships"]),
            "features_are": ("raw, positive, and complete. every ordering key below "
                             "is computed from these values and from oracle_id, and "
                             "from nothing else"),
        },
        "evidence": evidence,
    }


def _sort_key(candidate: dict):
    """The declared ordering, as one key. Reads SHARED evidence and id only.

    It cannot see a membership the candidate lacks, because no such value is in
    scope — which is the structural form of "missing membership is not a
    penalty", and is stronger than a test that merely observes it once.
    """
    features = candidate["features"]
    return (-features["shared_axis_count"],
            tuple(features["shared_axis_cardinalities"]),
            candidate["oracle_id"])


def _rank(candidates: list) -> list:
    """Apply the ordering and annotate every row with its tie block."""
    ordered = sorted(candidates, key=_sort_key)
    blocks: dict = {}
    for candidate in ordered:
        blocks.setdefault(_sort_key(candidate)[:2], []).append(candidate)
    first_rank = {}
    for position, candidate in enumerate(ordered, start=1):
        block = _sort_key(candidate)[:2]
        first_rank.setdefault(block, position)
    for position, candidate in enumerate(ordered, start=1):
        block = _sort_key(candidate)[:2]
        candidate["rank"] = position
        candidate["tie_block_size"] = len(blocks[block])
        candidate["tie_block_first_rank"] = first_rank[block]
    return ordered


def query(document: dict, *, oracle_id: str = None, name: str = None,
          view: EvidenceIndexView = None, top: int = None) -> dict:
    """One anchor in, one deterministic evidence result out.

    `view` is accepted so a caller running many queries over one artifact — the
    frozen evaluation does exactly that — builds the lookup maps once. It changes
    no value in the result.

    `top` truncates the PRINTED list only. Ranks and tie blocks are computed over
    the whole candidate set first, `candidate_count` always reports the full
    number, and the result says how many rows were dropped — so a truncated view
    can never be mistaken for a smaller pool.
    """
    view = view or EvidenceIndexView(document)
    anchor = view.anchor_id(oracle_id=oracle_id, name=name)
    anchor_row = view.cards[anchor]
    assigned = anchor_row["evidence_state"] == evidence_index.EVIDENCE_STATE_ASSIGNED

    candidate_ids = set()
    for membership in anchor_row["memberships"]:
        candidate_ids.update(view.axis_members.get(membership["axis_id"], []))
    candidate_ids.discard(anchor)

    candidates = _rank([
        _candidate(view, anchor_row, candidate_id,
                   _shared_axes(view, anchor_row, candidate_id))
        for candidate_id in sorted(candidate_ids)])

    return {
        "schema": RETRIEVAL_SCHEMA,
        "generator": {"package": "mtj_foundry", "version": __version__,
                      "capability": "evidence_only_retrieval"},
        "result_is": "DERIVED_EVIDENCE_NOT_AUTHORITY",
        "index": {
            "schema": document.get("schema"),
            "selected_codebook_sha256":
                document["selected_inputs"]["codebook"]["measured_sha256"],
            "selected_corpus_sha256":
                document["selected_inputs"]["corpus"]["measured_sha256"],
        },
        "anchor": {
            "oracle_id": anchor,
            "name": anchor_row["name"],
            "gate0_eligible": anchor_row["gate0_eligible"],
            "evidence_state": anchor_row["evidence_state"],
            "active_memberships": [
                {"axis_id": m["axis_id"],
                 "axis_active_member_count": view.axes[m["axis_id"]]["active_member_count"],
                 "member": m["member"]}
                for m in anchor_row["memberships"]],
        },
        "result_state": RESULT_STATE_ASSIGNED if assigned else RESULT_STATE_UNASSIGNED,
        "result_state_means": (
            "the anchor carries active evidence and every card sharing an active "
            "axis with it is below" if assigned else
            "the selected codebook records no active membership for this anchor, so "
            "the selected evidence connects it to nothing. this is an ABSENCE OF "
            "EVIDENCE. it is not a finding that the card has no similar cards, and "
            "no neighbour has been fabricated to fill it"),
        "candidate_rule": (
            "a candidate shares at least one ACTIVE axis with the anchor in the "
            "selected codebook. non-shared axes and absent memberships contribute "
            "exactly zero, in either direction"),
        "ordering": ORDERING_RULE,
        "candidate_count": len(candidates),
        "candidates_shown": len(candidates) if top is None else min(top, len(candidates)),
        "truncation": ("none — every candidate is below" if top is None else
                       f"the candidate list below is truncated to the first {top} "
                       f"rows of {len(candidates)}. ranks and tie blocks were "
                       f"computed over the whole set before truncating"),
        "candidates": candidates if top is None else candidates[:top],
    }


def render_result(result: dict) -> str:
    """`indent=2`, `ensure_ascii=False`, one trailing newline.

    The report's contract rather than the index's compact one, and for the
    report's reason: a query result is a page a person reads. A result is small
    enough that the whitespace costs nothing.
    """
    return json.dumps(result, indent=2, ensure_ascii=False) + "\n"
