"""C8 step 2 — measure legacy and candidate state against ONE invariant definition.

## The problem this solves

`conservation.py` (step 1) answers *did these bytes survive*, keyed on a repository
path. That is the right question while nothing has moved, and the wrong one the
moment anything does: the same truth read from a new location looks like a deleted
file plus an unrelated new one, and a file that stayed exactly where it was looks
conserved even when the thing it is supposed to carry has changed underneath it.

Step 2 separates the two. An **invariant** is a named truth with a contracted
**value**. Where that value was read is **evidence**, and evidence is never
compared. So:

- the same invariant read from two different paths, with equal values, is CONSERVED;
- an invariant whose contracted value changed is DRIFTED, wherever it was read from.

This is what `PRESERVE_TRUTH_NOT_PLUMBING` means operationally, and it is why
`Measurement` keeps `value` and `evidence` in separate objects rather than in one
flat record where a comparison could reach the wrong field.

## Refusing to guess

The C7 inventory has seven items. Three can be measured mechanically today. Four
need a semantic comparator nobody has ratified, and each is `DEFERRED_WITH_REASON`
in the contract with the specific thing it is missing written down.

The harness **refuses to measure a deferred invariant** — `measure_side` raises
rather than returning a placeholder, and a deferred item can never appear in a
report as CONSERVED. A comparator invented to make step 2 look complete would be
worse than a gap: a gap is visible, and a green row is not.

## Fail-closed

Everything below is an exception, not a verdict, because none of it is a fact about
the state being measured — it is a fact about the harness being unusable:

    duplicate invariant id        the second declaration silently wins
    a C7 item omitted             the inventory stops being an inventory
    comparison-kind mismatch      two sides comparing different things
    an active invariant unmeasured on either side
    a malformed digest, size or value field
    a binding for a deferred invariant
    a declared source that is absent

Only *value drift* is reported as a verdict. That distinction is the design: a
harness that returned "not conserved" for its own misconfiguration would let a
broken run read as a finding about the repository.

## Read-only, explicit, no discovery

Nothing here writes, and nothing here searches. A root is passed in; every source
is a path the contract DECLARES. No tree is walked, so this cannot become the
census it is not.
"""

from __future__ import annotations

import dataclasses
import json
import os
import re
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from mtj_foundry.conservation import FileDigest, canonical_relpath, digest_file

__all__ = [
    "CONTRACT_SCHEMA",
    "C7_INVENTORY",
    "ACTIVE_MECHANICAL",
    "DEFERRED_WITH_REASON",
    "COMPARISON_KINDS",
    "VALUE_FIELD_TYPES",
    "ConservationError",
    "ContractError",
    "MeasurementError",
    "SourceUnavailable",
    "ComparisonError",
    "ValueField",
    "Invariant",
    "Binding",
    "Side",
    "Contract",
    "Evidence",
    "Measurement",
    "InvariantVerdict",
    "ConservationReport",
    "load_contract",
    "measure_side",
    "compare",
    "CONSERVED",
    "DRIFTED",
    "DEFERRED_NOT_COMPARED",
]

CONTRACT_SCHEMA = "mtj-conservation-contract/1"

# The C7 inventory is CLOSED. P0.2 correction C7 names exactly these seven truths,
# and the loader refuses a contract that omits one — an inventory you may quietly
# shorten records only what somebody remembered.
C7_INVENTORY: tuple[str, ...] = (
    "CODEBOOK_AUTHORITY_IDENTITY",
    "GATE2_INVARIANTS_AND_KNOWN_DEBT",
    "ROUTING_RELATION",
    "RULING_DECISIONS",
    "CR_EDITION_CONTENT",
    "AQ4_FROZEN_STATE_AND_GOVERNANCE",
    "RATCHET_BASELINE_BYTES",
)

ACTIVE_MECHANICAL = "ACTIVE_MECHANICAL"
DEFERRED_WITH_REASON = "DEFERRED_WITH_REASON"
_STATUSES = (ACTIVE_MECHANICAL, DEFERRED_WITH_REASON)

COMPARISON_KINDS: tuple[str, ...] = (
    "EXACT_BYTES",
    "EXACT_VALUE",
    "EXACT_BYTES_PLUS_DECLARED_IDENTITY",
)

VALUE_FIELD_TYPES: tuple[str, ...] = ("sha256", "byte_size", "string")

CONSERVED = "CONSERVED"
DRIFTED = "DRIFTED"
DEFERRED_NOT_COMPARED = "DEFERRED_NOT_COMPARED"

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_FRONT_MATTER = re.compile(rb"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


class ConservationError(ValueError):
    """The harness cannot produce a trustworthy answer. Always fatal, never a verdict."""


class ContractError(ConservationError):
    """The contract document itself is unusable."""


class MeasurementError(ConservationError):
    """A measurement cannot be made, or is malformed."""


class SourceUnavailable(MeasurementError):
    """A DECLARED source is not present.

    Fatal rather than skipped. A skipped invariant is an unmeasured one, and an
    unmeasured invariant that vanishes from the report is indistinguishable from a
    conserved one — which is the whole failure this module exists to prevent.
    """


class ComparisonError(ConservationError):
    """Two measurement sets cannot be compared at all."""


# ---------------------------------------------------------------------------
# Contract
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ValueField:
    """One contracted field, with the type the contract declares for it.

    The type is DECLARED, not inferred from the field's name. A convention like
    "anything called sha256 is a digest" is a hand-list of naming habits standing
    where the contract should speak, and it validates nothing on the first field
    somebody names differently.
    """

    name: str
    type: str

    def __post_init__(self) -> None:
        if not self.name:
            raise ContractError("a value field must have a name")
        if self.type not in VALUE_FIELD_TYPES:
            raise ContractError(
                f"value field {self.name!r} declares unknown type {self.type!r}; "
                f"known types are {list(VALUE_FIELD_TYPES)}"
            )

    def validate(self, value: Any, *, where: str) -> None:
        if self.type == "sha256":
            if not isinstance(value, str) or not _SHA256.match(value):
                raise MeasurementError(
                    f"{where}: field {self.name!r} must be a 64-character lowercase hex "
                    f"sha256, got {value!r}"
                )
        elif self.type == "byte_size":
            # bool is an int subclass; True would otherwise pass as size 1.
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise MeasurementError(
                    f"{where}: field {self.name!r} must be a non-negative integer byte "
                    f"count, got {value!r}"
                )
        else:
            if not isinstance(value, str) or not value.strip():
                raise MeasurementError(
                    f"{where}: field {self.name!r} must be a non-empty string, got {value!r}"
                )


@dataclasses.dataclass(frozen=True)
class Invariant:
    invariant_id: str
    c7_item: str
    title: str
    status: str
    comparison_kind: str | None
    extractor: str | None
    extractor_args: Mapping[str, Any]
    value_fields: tuple[ValueField, ...]
    deferred_reason: str | None
    what_a_comparator_would_require: tuple[str, ...]

    @property
    def is_active(self) -> bool:
        return self.status == ACTIVE_MECHANICAL

    def validate_value(self, value: Mapping[str, Any], *, where: str) -> None:
        """A value must carry EXACTLY the contracted fields — no more, no fewer.

        An extra field is refused as hard as a missing one. A measurement carrying a
        field the contract does not name compares as drift the moment one side stops
        emitting it, and nothing would say why.
        """
        declared = {field.name for field in self.value_fields}
        present = set(value)
        missing = sorted(declared - present)
        extra = sorted(present - declared)
        if missing or extra:
            raise MeasurementError(
                f"{where}: value for {self.invariant_id} does not match the contract "
                f"(missing {missing}, unexpected {extra})"
            )
        for field in self.value_fields:
            field.validate(value[field.name], where=where)


@dataclasses.dataclass(frozen=True)
class Binding:
    """Where ONE side reads ONE invariant. Evidence, never truth."""

    invariant_id: str
    source_path: str
    availability: str

    def __post_init__(self) -> None:
        canonical_relpath(self.source_path)


@dataclasses.dataclass(frozen=True)
class Side:
    side_id: str
    description: str
    bindings: Mapping[str, Binding]


@dataclasses.dataclass(frozen=True)
class Contract:
    schema: str
    phase: str
    invariants: Mapping[str, Invariant]
    sides: Mapping[str, Side]
    document: Mapping[str, Any]

    @property
    def active_ids(self) -> tuple[str, ...]:
        return tuple(i for i in C7_INVENTORY if self.invariants[i].is_active)

    @property
    def deferred_ids(self) -> tuple[str, ...]:
        return tuple(i for i in C7_INVENTORY if not self.invariants[i].is_active)

    def require(self, invariant_id: str) -> Invariant:
        try:
            return self.invariants[invariant_id]
        except KeyError:
            raise ComparisonError(
                f"{invariant_id!r} is not in the C7 inventory this contract declares"
            ) from None


def _require_unique(ids: Iterable[str], *, what: str) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in ids:
        if value in seen:
            raise ContractError(
                f"duplicate {what} {value!r}. A second declaration would silently win, "
                "and the first would be conserved by nothing."
            )
        seen.add(value)
        ordered.append(value)
    return ordered


def load_contract(path: str | os.PathLike[str]) -> Contract:
    """Read and VALIDATE the contract. Every check here fails closed.

    Read-only: opens one declared file and nothing else.
    """
    raw = Path(path).read_text(encoding="utf-8")
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ContractError(f"contract at {path} is not valid JSON: {exc}") from None
    if not isinstance(doc, dict):
        raise ContractError("contract must be a JSON object")
    if doc.get("schema") != CONTRACT_SCHEMA:
        raise ContractError(
            f"contract declares schema {doc.get('schema')!r}, expected {CONTRACT_SCHEMA!r}"
        )

    authority = doc.get("authority")
    if not isinstance(authority, dict) or authority.get("this_document_ratifies") != "NOTHING":
        raise ContractError(
            "contract must declare authority.this_document_ratifies: NOTHING. A record "
            "that can ratify itself is the self-created authority C5 refuses."
        )

    declared = doc.get("invariants")
    if not isinstance(declared, list) or not declared:
        raise ContractError("contract declares no invariants")

    invariants: dict[str, Invariant] = {}
    for entry in declared:
        invariant = _load_invariant(entry)
        if invariant.invariant_id in invariants:
            raise ContractError(
                f"duplicate invariant id {invariant.invariant_id!r}. The second "
                "declaration would silently win."
            )
        invariants[invariant.invariant_id] = invariant

    missing = [item for item in C7_INVENTORY if item not in invariants]
    extra = sorted(set(invariants) - set(C7_INVENTORY))
    if missing or extra:
        raise ContractError(
            f"the C7 inventory is closed and must be stated in full: missing {missing}, "
            f"unknown {extra}. Omitting an item is how an unconserved truth stops being "
            "visible as one."
        )

    sides = _load_sides(doc.get("sides"), invariants)
    return Contract(schema=doc["schema"], phase=doc.get("phase", ""),
                    invariants=invariants, sides=sides, document=doc)


def _load_invariant(entry: Any) -> Invariant:
    if not isinstance(entry, dict):
        raise ContractError(f"an invariant declaration must be an object, got {entry!r}")
    invariant_id = entry.get("invariant_id")
    if not isinstance(invariant_id, str) or not invariant_id:
        raise ContractError(f"an invariant declaration has no invariant_id: {entry!r}")
    status = entry.get("status")
    if status not in _STATUSES:
        raise ContractError(
            f"{invariant_id}: status must be one of {list(_STATUSES)}, got {status!r}. "
            "There is no third state: an item is measured mechanically, or its deferral "
            "carries a reason."
        )

    kind = entry.get("comparison_kind")
    extractor = entry.get("extractor")
    args = entry.get("extractor_args") or {}
    fields = tuple(ValueField(name=f.get("name", ""), type=f.get("type", ""))
                   for f in entry.get("value_fields", []))
    reason = entry.get("deferred_reason")
    requires = tuple(entry.get("what_a_comparator_would_require", []))

    if status == ACTIVE_MECHANICAL:
        if kind not in COMPARISON_KINDS:
            raise ContractError(
                f"{invariant_id}: comparison_kind must be one of {list(COMPARISON_KINDS)}, "
                f"got {kind!r}"
            )
        if extractor not in _EXTRACTORS:
            raise ContractError(
                f"{invariant_id}: unknown extractor {extractor!r}; known extractors are "
                f"{sorted(_EXTRACTORS)}"
            )
        if not fields:
            raise ContractError(f"{invariant_id}: an active invariant must contract at "
                                "least one value field")
        _require_unique((f.name for f in fields), what=f"value field in {invariant_id}")
    else:
        if kind is not None or extractor is not None or fields:
            raise ContractError(
                f"{invariant_id}: a deferred invariant must declare no comparison_kind, "
                "no extractor and no value fields. Half a comparator reads as a working "
                "one to everything downstream."
            )
        if not isinstance(reason, str) or not reason.strip():
            raise ContractError(
                f"{invariant_id}: DEFERRED_WITH_REASON requires the reason. 'Deferred' "
                "without one is indistinguishable from forgotten."
            )
        if not requires:
            raise ContractError(
                f"{invariant_id}: a deferred invariant must state what a comparator "
                "would require, so the deferral names work rather than closing it."
            )

    return Invariant(
        invariant_id=invariant_id,
        c7_item=str(entry.get("c7_item", "")),
        title=str(entry.get("title", "")),
        status=status,
        comparison_kind=kind,
        extractor=extractor,
        extractor_args=args,
        value_fields=fields,
        deferred_reason=reason,
        what_a_comparator_would_require=requires,
    )


def _load_sides(declared: Any, invariants: Mapping[str, Invariant]) -> dict[str, Side]:
    if not isinstance(declared, list) or not declared:
        raise ContractError("contract declares no sides")
    active = {i for i, inv in invariants.items() if inv.is_active}
    sides: dict[str, Side] = {}
    for entry in declared:
        side_id = entry.get("side_id")
        if not isinstance(side_id, str) or not side_id:
            raise ContractError(f"a side declaration has no side_id: {entry!r}")
        if side_id in sides:
            raise ContractError(f"duplicate side_id {side_id!r}")
        bindings: dict[str, Binding] = {}
        for raw in entry.get("bindings", []):
            invariant_id = raw.get("invariant_id")
            if invariant_id not in invariants:
                raise ContractError(
                    f"{side_id}: binding names {invariant_id!r}, which is not in the "
                    "C7 inventory"
                )
            if not invariants[invariant_id].is_active:
                raise ContractError(
                    f"{side_id}: {invariant_id} is {DEFERRED_WITH_REASON} and must not be "
                    "bound to a source. Binding one is how a deferred item acquires a "
                    "comparator nobody ratified."
                )
            if invariant_id in bindings:
                raise ContractError(
                    f"{side_id}: duplicate binding for {invariant_id!r}"
                )
            bindings[invariant_id] = Binding(
                invariant_id=invariant_id,
                source_path=raw.get("source_path", ""),
                availability=str(raw.get("availability", "")),
            )
        unbound = sorted(active - set(bindings))
        if unbound:
            raise ContractError(
                f"{side_id}: no source declared for active invariant(s) {unbound}. A side "
                "that cannot measure an active invariant must say so here, not discover it "
                "at comparison time."
            )
        sides[side_id] = Side(side_id=side_id,
                              description=str(entry.get("description", "")),
                              bindings=bindings)
    return sides


# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Evidence:
    """WHERE a value was read. Deliberately not comparable.

    Kept beside the value rather than inside it so that no comparison can reach a
    path by accident. `source_sha256` records the bytes of the SOURCE DOCUMENT,
    which for an EXACT_VALUE invariant is a different thing from the value: the
    selector may be reformatted without the selection changing.
    """

    side_id: str
    source_path: str
    source_sha256: str
    source_size_bytes: int

    def as_dict(self) -> dict:
        return {
            "side_id": self.side_id,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "source_size_bytes": self.source_size_bytes,
        }


@dataclasses.dataclass(frozen=True)
class Measurement:
    invariant_id: str
    comparison_kind: str
    value: Mapping[str, Any]
    evidence: Evidence

    def as_dict(self) -> dict:
        return {
            "invariant_id": self.invariant_id,
            "comparison_kind": self.comparison_kind,
            "value": dict(self.value),
            "evidence": self.evidence.as_dict(),
        }


def _read_source(root: Path, relpath: str, *, side_id: str) -> tuple[FileDigest, Path]:
    canonical_relpath(relpath)
    target = root.joinpath(*relpath.split("/"))
    if not target.is_file():
        raise SourceUnavailable(
            f"{side_id}: declared source {relpath!r} is not present under {root}. An "
            "absent source is not a conserved invariant; the harness stops rather than "
            "omitting the row."
        )
    return digest_file(target, relative_to=root), target


def _extract_exact_file_bytes(digest: FileDigest, target: Path,
                              args: Mapping[str, Any]) -> dict:
    return {"sha256": digest.sha256, "size_bytes": digest.size_bytes}


def _extract_json_declared_scalars(digest: FileDigest, target: Path,
                                   args: Mapping[str, Any]) -> dict:
    fields = args.get("fields")
    if not isinstance(fields, dict) or not fields:
        raise ContractError("json_declared_scalars requires a non-empty 'fields' map")
    try:
        doc = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MeasurementError(f"{target} is not valid JSON: {exc}") from None
    if not isinstance(doc, dict):
        raise MeasurementError(f"{target} is not a JSON object")
    out: dict[str, Any] = {}
    for value_name, source_key in fields.items():
        if source_key not in doc:
            raise MeasurementError(
                f"{target} declares no {source_key!r}, so the contracted field "
                f"{value_name!r} cannot be read. A missing key is a halt, never a None."
            )
        out[value_name] = doc[source_key]
    return out


def _extract_exact_file_bytes_plus_front_matter(digest: FileDigest, target: Path,
                                                args: Mapping[str, Any]) -> dict:
    """Exact bytes, plus an identity the document states about ITSELF.

    The identity is read from the document's own front matter, never from its
    filename. A filename is a source path, and this whole module exists to keep a
    source path out of the compared truth — an edition identified by its name would
    "drift" the moment the file were renamed and stay put if it were overwritten.
    """
    fields = args.get("front_matter_fields")
    if not isinstance(fields, dict) or not fields:
        raise ContractError(
            "exact_file_bytes_plus_front_matter requires a non-empty "
            "'front_matter_fields' map"
        )
    head = target.read_bytes()
    match = _FRONT_MATTER.match(head)
    if not match:
        raise MeasurementError(
            f"{target} declares no YAML front matter block, so it states no identity "
            "about itself that could be read mechanically."
        )
    block = match.group(1).decode("utf-8")
    out: dict[str, Any] = {"sha256": digest.sha256, "size_bytes": digest.size_bytes}
    for value_name, key in fields.items():
        found = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", block, re.MULTILINE)
        if not found:
            raise MeasurementError(
                f"{target}: front matter declares no {key!r}, so the contracted field "
                f"{value_name!r} cannot be read."
            )
        out[value_name] = found.group(1).strip().strip('"').strip("'")
    return out


_EXTRACTORS: Mapping[str, Callable[[FileDigest, Path, Mapping[str, Any]], dict]] = {
    "exact_file_bytes": _extract_exact_file_bytes,
    "json_declared_scalars": _extract_json_declared_scalars,
    "exact_file_bytes_plus_front_matter": _extract_exact_file_bytes_plus_front_matter,
}


def measure_side(contract: Contract, side_id: str,
                 root: str | os.PathLike[str]) -> tuple[Measurement, ...]:
    """Measure every ACTIVE invariant for one side, under an EXPLICIT root.

    `root` is required and is never discovered. Nothing is walked: only the paths
    the contract declares are opened, and only for reading.

    Deferred invariants are not measured and no placeholder is emitted for them.
    """
    if side_id not in contract.sides:
        raise ComparisonError(
            f"{side_id!r} is not a side this contract declares "
            f"({sorted(contract.sides)})"
        )
    base = Path(root)
    side = contract.sides[side_id]
    out: list[Measurement] = []
    for invariant_id in contract.active_ids:
        invariant = contract.invariants[invariant_id]
        binding = side.bindings[invariant_id]
        digest, target = _read_source(base, binding.source_path, side_id=side_id)
        value = _EXTRACTORS[invariant.extractor](digest, target, invariant.extractor_args)
        invariant.validate_value(value, where=f"{side_id}/{invariant_id}")
        out.append(Measurement(
            invariant_id=invariant_id,
            comparison_kind=invariant.comparison_kind,
            value=dict(value),
            evidence=Evidence(side_id=side_id, source_path=binding.source_path,
                              source_sha256=digest.sha256,
                              source_size_bytes=digest.size_bytes),
        ))
    return tuple(out)


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class InvariantVerdict:
    invariant_id: str
    verdict: str
    comparison_kind: str | None
    differing_fields: tuple[str, ...]
    left: Measurement | None
    right: Measurement | None
    deferred_reason: str | None = None

    def as_dict(self) -> dict:
        out: dict[str, Any] = {
            "invariant_id": self.invariant_id,
            "verdict": self.verdict,
            "comparison_kind": self.comparison_kind,
            "differing_fields": list(self.differing_fields),
        }
        if self.deferred_reason:
            out["deferred_reason"] = self.deferred_reason
        if self.left is not None:
            out["left"] = self.left.as_dict()
        if self.right is not None:
            out["right"] = self.right.as_dict()
        return out


@dataclasses.dataclass(frozen=True)
class ConservationReport:
    left_side: str
    right_side: str
    verdicts: tuple[InvariantVerdict, ...]

    @property
    def conserved(self) -> bool:
        """True only if at least one invariant was compared and every one compared equal.

        A deferred invariant contributes nothing in either direction. It cannot make
        this False — it is not evidence of drift — and it must never help make it
        True, which is why `deferred_ids` is reported alongside and why no caller can
        read this flag as "C7 is conserved".

        The `compared_ids` guard is the vacuous-truth case, and it is the one a
        reader is least likely to picture: `all([])` is True, so a report in which
        EVERY invariant was deferred would otherwise announce itself conserved while
        having compared nothing at all. Nothing measured is not the same as nothing
        changed.
        """
        return bool(self.compared_ids) and all(
            v.verdict == CONSERVED for v in self.verdicts
            if v.verdict != DEFERRED_NOT_COMPARED)

    @property
    def compared_ids(self) -> tuple[str, ...]:
        return tuple(v.invariant_id for v in self.verdicts
                     if v.verdict != DEFERRED_NOT_COMPARED)

    @property
    def deferred_ids(self) -> tuple[str, ...]:
        return tuple(v.invariant_id for v in self.verdicts
                     if v.verdict == DEFERRED_NOT_COMPARED)

    @property
    def drifted_ids(self) -> tuple[str, ...]:
        return tuple(v.invariant_id for v in self.verdicts if v.verdict == DRIFTED)

    def as_dict(self) -> dict:
        return {
            "schema": "mtj-conservation-report/1",
            "left_side": self.left_side,
            "right_side": self.right_side,
            "conserved": self.conserved,
            "compared": list(self.compared_ids),
            "deferred_not_compared": list(self.deferred_ids),
            "drifted": list(self.drifted_ids),
            "verdicts": [v.as_dict() for v in self.verdicts],
        }

    def as_json(self) -> str:
        return json.dumps(self.as_dict(), sort_keys=True, indent=2,
                          separators=(",", ": "), ensure_ascii=True) + "\n"


def _index(contract: Contract, measurements: Sequence[Measurement],
           *, label: str) -> dict[str, Measurement]:
    out: dict[str, Measurement] = {}
    for measurement in measurements:
        invariant = contract.require(measurement.invariant_id)
        if not invariant.is_active:
            raise ComparisonError(
                f"{label}: {measurement.invariant_id} is {DEFERRED_WITH_REASON} and was "
                "measured anyway. A deferred item with a value is a comparator nobody "
                "ratified."
            )
        if measurement.invariant_id in out:
            raise ComparisonError(
                f"{label}: duplicate measurement of {measurement.invariant_id!r}. One of "
                "the two would silently win and the other would be conserved by nothing."
            )
        if measurement.comparison_kind != invariant.comparison_kind:
            raise ComparisonError(
                f"{label}: {measurement.invariant_id} was measured as "
                f"{measurement.comparison_kind!r} but the contract says "
                f"{invariant.comparison_kind!r}"
            )
        invariant.validate_value(measurement.value, where=f"{label}/{measurement.invariant_id}")
        out[measurement.invariant_id] = measurement
    return out


def compare(contract: Contract,
            left: Sequence[Measurement], right: Sequence[Measurement],
            *, left_side: str = "left", right_side: str = "right") -> ConservationReport:
    """Compare two sides by CONTRACTED VALUE ONLY.

    Evidence — which path each value came from — is carried into the report and takes
    no part in the verdict. That is the whole point: two sides reading one truth from
    two locations are conserved, and a truth that changed in place is not.
    """
    left_by_id = _index(contract, left, label=left_side)
    right_by_id = _index(contract, right, label=right_side)

    for label, measured in ((left_side, left_by_id), (right_side, right_by_id)):
        missing = [i for i in contract.active_ids if i not in measured]
        if missing:
            raise ComparisonError(
                f"{label}: active invariant(s) {missing} were not measured. An unmeasured "
                "invariant must stop the comparison, because a row that is absent from a "
                "report reads exactly like a row that passed."
            )

    verdicts: list[InvariantVerdict] = []
    for invariant_id in C7_INVENTORY:
        invariant = contract.invariants[invariant_id]
        if not invariant.is_active:
            verdicts.append(InvariantVerdict(
                invariant_id=invariant_id, verdict=DEFERRED_NOT_COMPARED,
                comparison_kind=None, differing_fields=(), left=None, right=None,
                deferred_reason=invariant.deferred_reason))
            continue
        a, b = left_by_id[invariant_id], right_by_id[invariant_id]
        if a.comparison_kind != b.comparison_kind:  # pragma: no cover - _index pins both
            raise ComparisonError(
                f"{invariant_id}: {left_side} compared as {a.comparison_kind!r} and "
                f"{right_side} as {b.comparison_kind!r}"
            )
        differing = tuple(f.name for f in invariant.value_fields
                          if a.value[f.name] != b.value[f.name])
        verdicts.append(InvariantVerdict(
            invariant_id=invariant_id,
            verdict=CONSERVED if not differing else DRIFTED,
            comparison_kind=invariant.comparison_kind,
            differing_fields=differing, left=a, right=b))
    return ConservationReport(left_side=left_side, right_side=right_side,
                              verdicts=tuple(verdicts))
