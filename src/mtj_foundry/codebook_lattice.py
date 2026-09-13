"""The object lattice's CODEBOOK half — axis identity, instantiation, the floor.

## What this is

S7 put the pure `targeted-<action>-<class>` measurement into
`mtj_foundry.mtg.shapes.target_classes`: it reads card text and CR vocabulary
and returns classes and proving clauses. Everything that turns those facts into
CODEBOOK statements is here:

* **axis identity** -- `slug_for` builds the `rule:targeted-*` slug. Axis
  IDENTITY is the codebook's, never the MTG substrate's.
* **virtual-node instantiation** -- `expand_lattice_pattern` maps a ratified
  lattice record to `{slug: {oracle_id: proving clause}}`, and
  `lattice_axis_record` builds the fresh axis record under grammar sec.11.2 with
  its scope INHERITED from the family parent (`lattice_parent_scopes`).
* **the ratified membership floor** -- `ratified_total` reads the TRACKED
  lattice row's `corpus_hits`, and `ratified_total_verdict` applies the ratchet
  direction to it: a FALL is fatal, a RISE is reported.
* **vocabulary agreement** -- `assert_vocabulary_agrees` refuses to emit a class
  slug out of vocabulary the grammar never ratified.
* **the per-class baseline metrics** the local ratchet pins.

## The invalid states it refuses, and keeps refusing

* a lattice row naming a stem the substrate does not implement (it would match
  nothing and read as a clean empty result);
* a claimed class with no proving clause (evidence-quote-or-discard);
* a lattice row that yields ZERO axes;
* a lattice slug no stem can be derived from;
* a child whose family parent is absent or carries no scope;
* a membership floor that FELL.

A lattice record is never subject to the one-pattern/one-axis orphan law: that
is `codebook_det_patterns.is_lattice_pattern`'s job, consumed here.

## What this is NOT

* No file reads, no corpus loading, no CR reading. The legacy shells supply the
  documents, the gated cards and the CR-derived domain.
* No process exit. Refusals raise `LatticeGovernanceError` carrying the historic
  halt text verbatim; a `target_classes.LatticeError` from the substrate
  propagates untouched. The shells translate both into `STOP — …`.
* Not the audit, the exclusivity report, the sample-sheet writer or the CLI --
  those are operator/report surfaces (S13).

## Layer law

Stdlib, `mtj_foundry.codebook_det_patterns` and the S7 substrate
`mtj_foundry.mtg.shapes.target_classes`, whose state (vocabulary and injected
clause-text rules) is read at CALL time, never captured. Never `experiments`.
"""

from __future__ import annotations

from mtj_foundry import codebook_det_patterns as _det_patterns
from mtj_foundry.mtg.shapes import target_classes as _tc

__all__ = [
    "LATTICE_SCOPE_PARENT",
    "LatticeGovernanceError",
    "assert_vocabulary_agrees",
    "baseline_metrics",
    "expand_lattice_pattern",
    "lattice_axis_record",
    "lattice_parent_scopes",
    "ratified_total",
    "ratified_total_verdict",
    "residual_invariant_failure_message",
    "slug_for",
]


class LatticeGovernanceError(RuntimeError):
    """A codebook-facing lattice refusal. Raised, never printed, never exited."""


def slug_for(stem: str, cls: str = None) -> str:
    """`rule:targeted-destroy` / `rule:targeted-destroy-creature`.

    NOTE THE SPELLING. Grammar §5 line 651 still writes the lattice
    `targeted-destruction-<class>`, the PRE-RENAME form: `targeted-destruction`
    became `targeted-destroy` on 2026-08-09 (A15 ruling §6c) and §7 item 2 of
    that doc logs the grammar's stale spelling as open drift. The live axis is
    the authority, so this emits `-destroy-`; the grammar line needs a G4
    generator fix, not this module bending to it.

    Axis IDENTITY is the codebook's, never the MTG substrate's, so this stays
    above L2 whatever else moves."""
    base = f"rule:targeted-{stem}"
    return base if cls is None else f"{base}-{cls}"


# The family parents whose ratified scope each lattice child inherits. Read
# from the live codebook at run time, never typed, so a re-scoped parent
# carries its children with it.
LATTICE_SCOPE_PARENT = {"destroy": "rule:targeted-destroy",
                        "exile": "rule:targeted-exile",
                        "bounce": "rule:targeted-bounce-creature"}


def lattice_parent_scopes(axes: dict) -> dict:
    """`{stem: inherited scope}`. Refuses a parent that is absent or scopeless."""
    out = {}
    for stem, parent in LATTICE_SCOPE_PARENT.items():
        rec = axes.get(parent)
        if rec is None or not rec.get("scope"):
            raise LatticeGovernanceError(
                f"lattice scope parent {parent!r} is absent or carries no "
                f"scope. A child cannot inherit what the parent does not "
                f"have, and guessing a scope is minting vocabulary.")
        out[stem] = rec["scope"]
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
    body = slug[len("rule:targeted-"):]
    stem = next((s for s in _tc.ACTION_VERBS if body.startswith(s + "-")), None)
    if stem is None:
        raise LatticeGovernanceError(
            f"cannot derive a stem from lattice slug {slug!r}")
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


def expand_lattice_pattern(pattern: dict, cards: dict, domain: set) -> dict:
    """slug -> {oracle_id: proving clause}, for every class the lattice names.

    The quote comes from the lattice's own `quotes` map, which is the clause
    that proved THAT class -- not the card's first matching clause. Evidence
    must prove ITS OWN axis (standing discipline); a card destroying an
    artifact and exiling a creature must not cite one clause for both.

    `domain` is the class domain the shell derived from its CR edition (CR
    110.4's permanent types for every ratified stem).
    """
    stems = pattern["lattice"]["stems"]
    unknown = [s for s in stems if s not in _tc.ACTION_VERBS]
    if unknown:
        raise LatticeGovernanceError(
            f"lattice row names stem(s) {unknown!r} that "
            f"foundry_object_lattice does not implement. Its ACTION_VERBS "
            f"are {sorted(_tc.ACTION_VERBS)}. A stem that does not exist "
            f"matches nothing and reads as a clean empty result.")
    out = {}
    for stem in stems:
        for oid in sorted(cards):
            r = _tc.classes_for_card(cards[oid], stem, domain)
            for cls in sorted(r["classes"]):
                quote = r["quotes"].get(cls)
                if not quote:
                    raise LatticeGovernanceError(
                        f"lattice claimed {slug_for(stem, cls)} for "
                        f"{oid} with no proving clause. Evidence-quote-or-"
                        f"discard is not optional.")
                out.setdefault(slug_for(stem, cls), {})[oid] = quote
    if not out:
        raise LatticeGovernanceError(
            "lattice row produced ZERO axes. An empty result from a "
            "ratified pattern is a defect, not a clean run.")
    return out


def ratified_total(det_document: dict, source_name: str) -> int:
    """The membership total the RATIFIED, TRACKED lattice row asserts.

    **THE LOCAL RATCHET CANNOT BE THE MEMBERSHIP FLOOR, BECAUSE IT IS NOT
    TRACKED.** `experiments/out/` is gitignored, so `audit-baseline.json` is
    per-machine and a fresh clone compares nothing. `det-patterns-v2.json` is
    tracked, reviewed and ratified, and its lattice row already carries the
    reviewed population as `corpus_hits`, so the floor is read from there
    rather than duplicated. `foundry_recorded_numbers.py` is the precedent.

    `source_name` is only the document's display name, for the refusal text.
    """
    row = None
    for p in det_document.get("patterns", []):
        if _det_patterns.is_lattice_pattern(p):
            row = p
            break
    if row is None:
        raise LatticeGovernanceError(
            f"{source_name} carries no lattice row, so the "
            f"ratified membership total cannot be read. The lattice's "
            f"floor is the RATIFIED number, never a locally pinned one; "
            f"a missing row halts rather than falling back.")
    stems = set(row["lattice"]["stems"])
    if stems != set(_tc.ACTION_VERBS):
        raise LatticeGovernanceError(
            f"the ratified lattice row covers {sorted(stems)} but this "
            f"module implements {sorted(_tc.ACTION_VERBS)}. The asserted total "
            f"counts a different population than the one measured here.")
    total = row.get("corpus_hits")
    if not isinstance(total, int):
        raise LatticeGovernanceError(
            f"the ratified lattice row's corpus_hits is {total!r}, not an "
            f"integer. It is the membership floor and cannot be absent.")
    return total


def ratified_total_verdict(want: int, live: int) -> tuple:
    """Live memberships vs the ratified total. Returns `(fatal, notes)`.

    **`corpus_hits` IS A MEASUREMENT AT PROBE TIME, NOT AN EQUALITY
    INVARIANT.** Three ratified patterns have already drifted from their
    recorded `corpus_hits` with Gate 2 green, the sibling field is named
    `codebook_n_members_at_probe`, and the file's own `preprocessing_standard`
    records these counts being updated on re-probe. Equality would freeze
    normal corpus growth.

    The direction carries the meaning, and it is `foundry_audit_baseline`'s own
    ratchet semantics applied to a number that lives in git: a FALL is the
    2026-08-13 incident and is fatal; a RISE is corpus growth and is reported.

    **THIS TOTAL IS STRUCTURALLY BLIND TO REDISTRIBUTION.** A compensating
    −7/+7 across two classes nets zero and passes here. That is the per-class
    ratchet's job, and the gap is recorded (docs/OBJECT-LATTICE-RESIDUAL-RULING
    -2026-08-13.md §8b), not silently closed.
    """
    if live == want:
        return [], []
    msg = (f"det-patterns-v2.json lattice row asserts {want:,} memberships; "
           f"the producer now yields {live:,} ({live - want:+,}). ")
    if live < want:
        return [msg + "MEMBERSHIPS WERE LOST. Re-review the sample sheet and "
                      "re-ratify corpus_hits on purpose — never edit the "
                      "number to match the code."], []
    return [], [msg + "Corpus growth or a recall improvement; the ratified row "
                      "is now stale. Re-review and re-pin corpus_hits when the "
                      "growth is accounted for."]


def residual_invariant_failure_message(stem: str, unexplained: list) -> str:
    """The write-refusal text for a stem whose residual still carries live arms.

    Returns None when `unexplained` is empty. The residual invariant is a
    PRECONDITION OF THE WRITE, not a report: a membership that is MISSING is
    invisible to a sample of what was produced, which is how seven correct
    memberships vanished in `e780842` past a green sample gate.
    """
    if not unexplained:
        return None
    rows = "\n".join(
        f"    {name}: arm {arm!r} -> {slug_for(stem, cls)}"
        for name, arm, cls, _q in unexplained[:10])
    return (
        f"object lattice residual invariant FAILED for {stem!r}: "
        f"{len(unexplained)} residual clause(s) still carry a "
        f"target arm resolving to a battlefield class, so the "
        f"producer is dropping memberships nobody reviewed.\n{rows}\n"
        f"  Run: python3 tests/guards/gate2/test_object_lattice.py --gate")


def assert_vocabulary_agrees(permanent_types: set, card_types: set,
                             object_vocab) -> None:
    """Three sources, asserted against each other. CR 110.4 must be a subset of
    CR 205.2a (a permanent type is a card type), and every permanent type must
    already be a ratified grammar §5 OBJECT token — otherwise the lattice would
    be about to emit a slug out of vocabulary the grammar never ratified.

    A check that an emitted SLUG is in vocabulary belongs with the emitter,
    which is why it is codebook-side and not in the substrate."""
    if not permanent_types <= card_types:
        raise LatticeGovernanceError(
            f"CR 110.4 names permanent type(s) absent from CR 205.2a: "
            f"{sorted(permanent_types - card_types)}")
    missing = sorted(permanent_types - set(object_vocab))
    if missing:
        raise LatticeGovernanceError(
            f"CR 110.4 permanent type(s) {missing} are not in the ratified "
            f"grammar §5 OBJECT vocabulary (validate_slug.OBJECT_VOCAB). "
            f"Emitting a class slug for them would mint vocabulary; that "
            f"is a ratification, not a code change.")


def baseline_metrics(cards: dict, domain: set) -> dict:
    """Per-class membership counts, residual, and unexplained residual.

    **THE MEMBERSHIP COUNTS ARE PINNED SO THAT A REMOVAL IS FATAL.** They carry
    the `memberships` marker, which `foundry_audit_baseline.WORSE_IF_DOWN`
    reads, so a count that FALLS is a regression and has to be re-pinned on
    purpose. That is the half of the diff nothing watched: `e780842` removed
    170 memberships, verified 83, and the other 87 shipped unread.
    """
    memberships, residual, unexplained = {}, {}, {}
    for stem in sorted(_tc.ACTION_VERBS):
        m = _tc.measure(stem, domain, cards)
        memberships[stem] = {cls: n for cls, n in sorted(m["per_class"].items())}
        residual[stem] = len(m["residual"])
        unexplained[stem] = len(
            _tc.residual_invariant(stem, domain, cards)["unexplained"])
    return {"memberships": memberships, "residual": residual,
            "residual_unexplained": unexplained}
