"""The deterministic full-population evidence index — one row per corpus card.

## What this is

Path E milestone 2's first half. It COMPOSES the accepted milestone-1 loaders
rather than reimplementing them: `runtime.load_verified_codebook` and
`runtime.load_verified_corpus` do the identity verification, the schema gate and
the lint, and this module walks what they returned and writes one versioned JSON
artifact describing every card in the selected corpus.

The artifact is what milestone 3 would consume statically, so the whole point is
that it stands on its own bytes: a reader with the artifact and nothing else can
see every card, every face, every active membership and every stored assertion,
and can tell an absence of evidence from a claim of dissimilarity.

## The three things it must not do, restated because they are easy to lose

* **It is not a filter.** The index contains the ENTIRE selected corpus —
  38,233 rows on the pilot input, not the 32,557 Gate-#0-eligible ones and not
  the 6,275 covered ones. Eligibility is a boolean ON the row. A card that no
  active axis lists is present, with its faces and its text, carrying
  `UNASSIGNED_NO_ACTIVE_EVIDENCE`.
* **It is not a ranking policy.** No score, no weight, no threshold and no order
  other than `oracle_id`. Ranking lives one layer up in
  `mtj_foundry.thesaurus.retrieval`, which consumes this. Putting a presentation decision
  in the index would make the artifact an authority about similarity, which it
  is not and must never become.
* **It is not authority, and it invents nothing.** Every membership, quote,
  locality, corpus_ref and source_ref below is COPIED from the selected
  codebook. Nothing here infers a membership, repairs one, checks whether a
  quote still entails its card, synthesizes an axis, embeds a card, or calls a
  model. The only values this module ORIGINATES are counts of what it copied.

## UNASSIGNED means one thing and it is stated in the artifact

`UNASSIGNED_NO_ACTIVE_EVIDENCE` means: *the selected codebook records no
membership for this card on any axis whose status is `active`.* It does not mean
the card is dissimilar to anything, was reviewed and rejected, carries negative
evidence, or is semantically empty. At 6,275 of 38,233 covered, the overwhelming
majority of the corpus is unreviewed rather than judged, and an index that let
those two states share a representation would convert unknown into false at the
first join. That is why the state is written out as a named string on every row
instead of being inferred from an empty list.

## Conservation is checked here, against a SECOND derivation

The milestone-1 report walks the codebook AXIS BY AXIS and the corpus card by
card. This module walks CARD BY CARD and accumulates memberships per card. Those
are different code paths over the same loaded objects, so requiring them to agree
is a real cross-check rather than a restatement — and it is the check that would
fire if this walk ever dropped a member, double-counted a multi-axis card, or
quietly reintroduced a filter.

The expectations are NOT hardcoded counts. The report is generated in the same
run and its numbers are the reference, which is what keeps a carried-forward
number from becoming a premise. Where the report itself is cross-checked against
an independent tracked source — `docs/codebook-authority.json` records
`active_axis_count` and `assertion_count` for this snapshot — that check already
lives in the accepted milestone-1 suite and is not duplicated here.
"""

from __future__ import annotations

import json

from mtj_foundry import __version__, corpus, runtime

__all__ = [
    "ACTIVE_AXIS_STATUS",
    "EVIDENCE_STATE_ASSIGNED",
    "EVIDENCE_STATE_MEANINGS",
    "EVIDENCE_STATE_UNASSIGNED",
    "INDEX_SCHEMA",
    "EvidenceIndexConservationError",
    "build_index",
    "evidence_state_semantics",
    "generate",
    "render_index",
]

INDEX_SCHEMA = "mtj-foundry-evidence-index/1"

# Re-exported from the accepted boundary rather than restated. `codebook.
# AXIS_STATUSES` holds all five; only this one means "in force", and a second
# literal here would be a second place for that fact to drift.
ACTIVE_AXIS_STATUS = runtime.ACTIVE_AXIS_STATUS

EVIDENCE_STATE_ASSIGNED = "ACTIVE_EVIDENCE_PRESENT"
EVIDENCE_STATE_UNASSIGNED = "UNASSIGNED_NO_ACTIVE_EVIDENCE"

# The MEANING of the two states. Fixed prose, because it is a statement about
# what the vocabulary means and not about any particular corpus — it is true of
# every index this module will ever build. Carried INTO the artifact so a static
# consumer that never reads this module cannot invent a third reading.
EVIDENCE_STATE_MEANINGS = {
    EVIDENCE_STATE_ASSIGNED: (
        "the selected codebook records at least one membership for this card on "
        "an axis whose status is 'active'. the memberships and their stored "
        "assertions are on this row, verbatim"),
    EVIDENCE_STATE_UNASSIGNED: (
        "the selected codebook records NO membership for this card on any axis "
        "whose status is 'active'. that is the whole claim"),
    "UNASSIGNED_IS_NOT": [
        "not a judgement that the card is dissimilar to any other card",
        "not a review that rejected the card",
        "not negative evidence of any kind",
        "not a claim that the card is semantically empty",
        "not a claim that the card was ever looked at",
    ],
}


def _absent_membership_clause(coverage: dict) -> str:
    """The UNKNOWN-never-FALSE sentence, with its POPULATION FACTS DERIVED.

    M2.R1 repair B, from Manager review `5593405124`. This clause used to be a
    module-level constant reading "31,958 of 38,233 corpus ids are uncovered".
    Those counts were true of the selected pilot on the day they were typed, and
    that is exactly the defect: a permanent capability that can build an index
    over ANY verified inputs was carrying one measurement as though it were part
    of the vocabulary's meaning. The next verified index with different coverage
    would have shipped the old sentence and read as authoritative.

    So the numbers now come from `coverage` — the same re-derived block the
    artifact publishes and `_conserve` checks against the accepted milestone-1
    report — and no replacement literal is substituted for them.

    **The QUANTIFIER is derived too, and that is not incidental.** "an unreviewed
    majority" is as much a population claim as "31,958" is; fixing the digits and
    leaving the adjective would have moved the same defect one word to the right,
    where it would be harder to see. On the selected pilot 31,958 of 38,233 are
    uncovered, so the derived word is "majority" and the emitted sentence is
    byte-identical to the constant it replaces — which is why this repair does
    not move the artifact's digest.

    The MEANING does not move and must not: absence of an active membership is
    UNKNOWN, never FALSE. Only the measured facts inside the sentence are
    derived.
    """
    uncovered = coverage["corpus_ids_uncovered"]
    total = coverage["corpus_ids_total"]
    if uncovered * 2 > total:
        share = "majority"
    elif uncovered * 2 < total:
        share = "minority"
    else:
        share = "half"
    return (f"UNKNOWN, never FALSE. {uncovered:,} of {total:,} corpus ids are "
            f"uncovered on the selected codebook; treating absence as a negative "
            f"signal would convert an unreviewed {share} into a fabricated "
            f"judgement")


def evidence_state_semantics(report: dict) -> dict:
    """The semantics block for ONE artifact: fixed meanings plus derived facts.

    A function rather than a constant, because half of this block is a statement
    about vocabulary (true always) and half is a statement about the inputs this
    particular artifact was built from (true only of them). Keeping them in one
    module-level dict is what let a measurement masquerade as a definition.
    """
    return {**EVIDENCE_STATE_MEANINGS,
            "absent_membership_is": _absent_membership_clause(report["coverage"])}


class EvidenceIndexConservationError(RuntimeError):
    """A per-card walk and the milestone-1 per-axis walk disagree.

    Deliberately fatal and deliberately not repaired. The two derivations exist
    to disagree when something was lost; softening this into a warning would
    leave the artifact carrying the number nobody checked.
    """


def _axis_catalogue(document: dict) -> dict:
    """`{axis_id: axis facts}` for ACTIVE axes only, in sorted axis-id order.

    The definition/scope/source fields are copied so a static consumer can show
    WHY two cards were linked without holding the codebook. `active_member_count`
    is this axis's cardinality in the selected codebook — the specificity feature
    the retrieval layer ranks on, computed once here rather than re-counted per
    query.

    Non-active axes are omitted from the catalogue AND from every row's
    memberships. That is the milestone-1 coverage definition applied unchanged:
    a killed, merged, renamed or deferred axis is history, and folding it into
    an evidence claim would silently widen what "active evidence" means.
    """
    catalogue = {}
    for axis_id in sorted(document.get("axes", {})):
        entry = document["axes"][axis_id]
        if entry.get("status") != ACTIVE_AXIS_STATUS:
            continue
        members = entry.get("members") or []
        catalogue[axis_id] = {
            "axis_id": axis_id,
            "status": entry.get("status"),
            "definition": entry.get("definition"),
            "scope": entry.get("scope"),
            "source": entry.get("source"),
            "parameterized": entry.get("parameterized"),
            "active_member_count": len(members),
            "active_member_count_is": (
                "cardinality of this axis in the SELECTED codebook, including "
                "member ids that may not be in the selected corpus"),
        }
    return catalogue


def _memberships_by_card(document: dict) -> dict:
    """`{oracle_id: [(axis_id, member_object), ...]}` over ACTIVE axes.

    The member object is carried WHOLE and verbatim — not a projection of the
    fields this milestone happens to name. `class`, `source_ref`, `quote`,
    `corpus_ref`, `evidence_status`, `locality`, a member-level `tier` and any
    key a later schema adds all survive, because the copy does not enumerate
    them. Flattening a member to an id is the exact loss this index exists to
    prevent, and a projection is that loss with a longer delay.
    """
    by_card: dict = {}
    for axis_id in sorted(document.get("axes", {})):
        entry = document["axes"][axis_id]
        if entry.get("status") != ACTIVE_AXIS_STATUS:
            continue
        for member in entry.get("members") or []:
            oracle_id = member.get("oracle_id")
            if oracle_id is None:
                continue
            by_card.setdefault(oracle_id, []).append((axis_id, member))
    return by_card


def _card_row(oracle_id: str, card: dict, memberships: list) -> dict:
    """One index row. Every field is copied or counted; none is inferred.

    Faces come from `corpus.card_faces`, never from `card["card_faces"]`: split,
    flip and adventure layouts carry a faces list AND one root-level text, so the
    raw field describes a face structure the Foundry's own readers do not see.
    """
    return {
        "oracle_id": oracle_id,
        "name": card["name"],
        "normalized_name": corpus.normalize_name(card["name"]),
        "gate0_eligible": corpus.is_gate0_eligible(card),
        "faces": corpus.card_faces(card),
        "evidence_state": (EVIDENCE_STATE_ASSIGNED if memberships
                           else EVIDENCE_STATE_UNASSIGNED),
        "memberships": [{"axis_id": axis_id, "member": member}
                        for axis_id, member in memberships],
    }


def _conserve(index: dict, report: dict) -> None:
    """Require the per-card walk to agree with the accepted per-axis report.

    Raises `EvidenceIndexConservationError` naming the exact field and both
    values. There is no tolerance band and no repair path: a disagreement means
    one of the two walks lost something, and which one is a question for a
    reviewer, not for a default.
    """
    rows = index["cards"]
    derived = {
        "unique_oracle_ids": len(rows),
        "eligible_unique_ids": sum(1 for r in rows if r["gate0_eligible"]),
        "ineligible_unique_ids": sum(1 for r in rows if not r["gate0_eligible"]),
        "corpus_ids_covered": sum(
            1 for r in rows if r["evidence_state"] == EVIDENCE_STATE_ASSIGNED),
        "corpus_ids_uncovered": sum(
            1 for r in rows if r["evidence_state"] == EVIDENCE_STATE_UNASSIGNED),
        "memberships_active_axes": sum(len(r["memberships"]) for r in rows),
        "active_axes": len(index["axes"]),
    }
    expected = {
        "unique_oracle_ids": report["corpus_population"]["unique_oracle_ids"],
        "eligible_unique_ids": report["eligibility"]["eligible_unique_ids"],
        "ineligible_unique_ids": report["eligibility"]["ineligible_unique_ids"],
        "corpus_ids_covered": report["coverage"]["corpus_ids_covered"],
        "corpus_ids_uncovered": report["coverage"]["corpus_ids_uncovered"],
        # The report counts EVERY active membership, including those on member
        # ids the corpus does not contain; the index can only hold the ones whose
        # card is present. They are equal exactly when no active member id is
        # absent from the corpus, which the report states as its own number — so
        # the two are reconciled here rather than assumed equal.
        "memberships_active_axes": (
            report["codebook_structure"]["memberships_active_axes"]
            - report["coverage"]["memberships_on_active_member_ids_absent_from_corpus"]),
        "active_axes": report["codebook_structure"]["axes_by_status"].get(
            ACTIVE_AXIS_STATUS, 0),
    }
    for field, value in expected.items():
        if derived[field] != value:
            raise EvidenceIndexConservationError(
                f"{field}: the per-card index walk derived {derived[field]!r} but "
                f"the accepted milestone-1 per-axis report derived {value!r} — "
                f"refusing to emit an index whose population does not reconcile "
                f"with the accepted composition")


def build_index(document: dict, cards: dict, report: dict) -> dict:
    """The whole artifact, as a dict. Pure: reads no file and writes none.

    `report` is the milestone-1 report for the SAME loaded inputs. It is embedded
    (so the artifact carries its own input identities and population arithmetic)
    and it is the conservation reference (so the two walks have to agree).
    """
    catalogue = _axis_catalogue(document)
    by_card = _memberships_by_card(document)
    rows = [_card_row(oracle_id, cards[oracle_id], by_card.get(oracle_id, []))
            for oracle_id in sorted(cards)]

    index = {
        "schema": INDEX_SCHEMA,
        "generator": {
            "package": "mtj_foundry",
            "version": __version__,
            "capability": "full_population_evidence_index",
        },
        "artifact_is": "DERIVED_EVIDENCE_NOT_AUTHORITY",
        "scope": {
            "performs": [
                "composition of the accepted milestone-1 verified loaders",
                "one row per unique oracle_id in the ENTIRE selected corpus",
                "verbatim copy of every active-axis membership and its assertions",
                "counting of existing structure",
            ],
            "does_not_perform": [
                "membership inference, repair or synthesis",
                "quote entailment validation",
                "ranking, scoring or ordering by anything but oracle_id",
                "embedding, model calls or network access",
                "codebook or corpus mutation",
                "any write of canonical input, cache, manifest or authority state",
            ],
            "population": ("the FULL corpus. eligibility and coverage are fields on "
                           "a row, never a filter over rows"),
            "evidence_polarity": ("POSITIVE ONLY. the index records what the codebook "
                                  "asserts. it records no negative or exclusionary "
                                  "claim about any card, and none may be derived from "
                                  "an absence in it"),
        },
        "evidence_state_semantics": evidence_state_semantics(report),
        "selected_inputs": report["inputs"],
        "conservation": {
            "source": ("re-derived by this module's per-card walk and required to "
                       "equal the milestone-1 per-axis report generated in the same "
                       "run over the same verified bytes"),
            "corpus_population": report["corpus_population"],
            "eligibility": report["eligibility"],
            "coverage": report["coverage"],
            "codebook_structure": report["codebook_structure"],
            "codebook_lint": report["codebook_lint"],
            "codebook_evidence_fields_present_on_active_axes":
                report["codebook_evidence_fields_present_on_active_axes"],
        },
        "axes": catalogue,
        "name_index": corpus.build_name_index(cards),
        "cards": rows,
    }
    _conserve(index, report)
    return index


def render_index(index: dict) -> str:
    """The byte contract: COMPACT separators, `ensure_ascii=False`, one newline.

    Deliberately NOT the report's `indent=2`, and the difference is a decision
    rather than an oversight. The report is a page an operator reads; this is a
    38,233-row machine artifact a static consumer loads, and indenting it costs
    roughly three quarters of the file for whitespace nobody reads. Both
    contracts give the same guarantee that matters here — the same input renders
    to the same bytes — because `json.dumps` preserves insertion order and every
    mapping above is built in a fixed order.

    `ensure_ascii=False` is not cosmetic. Card text and codebook quotes carry
    real curly apostrophes and non-ASCII names, and escaping them would make the
    artifact's bytes disagree with the corpus they were copied from.
    """
    return json.dumps(index, ensure_ascii=False, separators=(",", ":")) + "\n"


def generate(root, **kwargs) -> dict:
    """THE entry point: verify, load, report, index. Returns the artifact dict.

    Every input check is milestone 1's, unchanged and not re-implemented — a
    digest mismatch, an unreadable file, a schema rejection or a lint failure
    raises exactly what it raised before, from the same code, and nothing
    downstream of a failed verification runs.
    """
    inputs = runtime.resolve_inputs(root, **kwargs)
    document, lint_stats, codebook_identity, selector = runtime.load_verified_codebook(inputs)
    cards, corpus_identity, content_sha256 = runtime.load_verified_corpus(inputs)
    report = runtime.build_report(document, lint_stats, codebook_identity, selector,
                                  cards, corpus_identity, content_sha256,
                                  inputs.corpus, inputs)
    return build_index(document, cards, report)
