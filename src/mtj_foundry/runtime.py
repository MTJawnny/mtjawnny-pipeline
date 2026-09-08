"""The read-only Foundry runtime — one composition boundary, no inference.

## What this is

The first permanent code that COMPOSES the capabilities instead of being one.
It resolves the selected codebook through its tracked authority selector,
verifies both inputs against explicitly declared identities, loads them through
the permanent store and corpus capabilities, and returns one deterministic
report describing what it found.

Six steps, in this order, and the order is the guarantee:

    read the authority selector -> measure the codebook's ACTUAL bytes ->
    compare size AND sha256 -> load through the store's schema gate ->
    lint -> only then look at the corpus

A mismatch at any step raises. Nothing downstream of a failed verification runs,
so there is no path on which a report describes bytes that were never checked.

## What this is NOT

* **Not authority.** The report is DERIVED EVIDENCE. It selects nothing,
  ratifies nothing, and is not an input to any later decision merely because it
  exists. `docs/codebook-authority.json` selects the codebook; this reads that
  selection and checks it held.
* **Not a writer.** Nothing here opens a file for writing, creates a directory,
  caches a parse, or touches the network. The report goes to the caller, and the
  CLI prints it; where an operator redirects that stream is the operator's
  business and is not a side effect of this module.
* **Not semantic.** It counts existing structure. It assigns no card to an axis,
  ranks nothing, infers nothing, and turns no absent membership into a claim
  that a card is unlike another. "Uncovered" here means "no active membership
  exists in this codebook", which is a statement about the codebook.
* **Not a corpus fetcher.** The corpus is an INPUT with a declared identity. If
  the declared digest does not match the bytes on disk, that is a stop, not a
  cue to go and get different bytes.

## Why the corpus identity must be passed in

The codebook has a tracked selector; the corpus does not. Defaulting to
"whatever gzip is at the layout owner's corpus path" would make every number in
the report a claim about an unnamed file. So the expected sha256 and a
provenance statement are REQUIRED, either from an input-lock document or from
the caller directly, and a run that cannot state which bytes it measured does
not happen at all.
"""

from __future__ import annotations

import dataclasses
import gzip
import hashlib
import json
import os
from pathlib import Path

from mtj_foundry import __version__, codebook, codebook_store, corpus
from mtj_foundry.paths import ProjectPaths

__all__ = [
    "AUTHORITY_SCHEMA",
    "AuthoritySelectorError",
    "CorpusSelection",
    "FileIdentity",
    "FoundryRuntimeError",
    "INPUT_LOCK_SCHEMA",
    "InputIdentityError",
    "InputLockError",
    "REPORT_SCHEMA",
    "RuntimeInputs",
    "build_report",
    "load_input_lock",
    "measure_file",
    "measure_gzip_content",
    "read_authority_selector",
    "render_report",
    "resolve_corpus_selection",
    "run",
]

REPORT_SCHEMA = "mtj-foundry-runtime-report/1"
INPUT_LOCK_SCHEMA = "mtj-foundry-input-lock/1"
AUTHORITY_SCHEMA = "foundry-authority/1"

_CHUNK_BYTES = 1 << 20

# The active axis status, named once. `mtj_foundry.codebook.AXIS_STATUSES` holds
# all five; only this one means "in force", and every other status is history the
# report must not silently fold into a coverage number.
ACTIVE_AXIS_STATUS = "active"


class FoundryRuntimeError(RuntimeError):
    """Base for this boundary's own typed failures.

    Deliberately its own hierarchy rather than a `CodebookStoreError`: the store's
    base is defined as "the store's own INTEGRITY failures, and only those", and a
    declared-identity mismatch is neither integrity nor persistence. Errors raised
    by the capabilities themselves -- `CorpusLoadError`, `LintError`,
    `SchemaMismatchError`, `CodebookNotFoundError` -- propagate UNWRAPPED, because
    translating them here would hide which layer refused.
    """


class AuthoritySelectorError(FoundryRuntimeError):
    """The tracked selector is missing, unreadable, or not the expected schema."""


class InputIdentityError(FoundryRuntimeError):
    """Measured bytes do not match a declared identity. Carries the two values."""

    def __init__(self, what: str, field: str, expected, measured):
        self.what = what
        self.field = field
        self.expected = expected
        self.measured = measured
        super().__init__(
            f"{what}: declared {field} {expected!r} but measured {measured!r} — "
            f"refusing to report on bytes that are not the selected input")


class InputLockError(FoundryRuntimeError):
    """The corpus identity/provenance a run needs is missing or self-contradictory."""


# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True)
class FileIdentity:
    """What was actually on disk: exact bytes, exact length."""

    path: Path
    sha256: str
    byte_size: int


def measure_file(path) -> FileIdentity:
    """sha256 and length of a file's EXACT bytes, streamed.

    A second private digest helper rather than `mtj_foundry.conservation`: that
    module's contract requires a canonical repository-relative label domain, and
    this reads arbitrary explicit paths -- including a corpus outside the root.
    Widening conservation to fit would trade an enforced manifest contract for a
    shared abstraction neither caller wants. Same reasoning, verbatim, as the
    store's own private digest.
    """
    path = Path(path)
    digest = hashlib.sha256()
    size = 0
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(_CHUNK_BYTES), b""):
            digest.update(chunk)
            size += len(chunk)
    return FileIdentity(path=path, sha256=digest.hexdigest(), byte_size=size)


def measure_gzip_content(path) -> str:
    """sha256 of what a gzip file DECOMPRESSES to, streamed.

    A SECOND identity, and it answers a different question from the container
    digest. A gzip header carries an mtime field, so re-compressing identical
    bytes yields a different file digest while the content is unchanged. The
    container digest is what pins the exact artifact; this is what lets an
    artifact be recognised as the same DATA as an archived copy. Neither
    substitutes for the other, and a report that carried only one would be
    silently answering the question nobody asked.
    """
    digest = hashlib.sha256()
    with gzip.open(Path(path), "rb") as handle:
        for chunk in iter(lambda: handle.read(_CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


# ---------------------------------------------------------------------------
# Input resolution
# ---------------------------------------------------------------------------

def read_authority_selector(path) -> dict:
    """The tracked selector document, schema-gated.

    Raises `AuthoritySelectorError` when it is absent or carries a different
    schema. A JSON decode error propagates raw: the file is tracked, so a
    malformed one is a repository fact and not something to soften.
    """
    path = Path(path)
    if not path.exists():
        raise AuthoritySelectorError(
            f"{path} not found — the codebook authority selector is a tracked "
            "file and there is no default selection without it")
    with open(path, "r", encoding="utf-8") as handle:
        document = json.load(handle)
    schema = document.get("schema")
    if schema != AUTHORITY_SCHEMA:
        raise AuthoritySelectorError(
            f"{path}: unexpected schema {schema!r}, expected {AUTHORITY_SCHEMA!r}")
    for field in ("sha256", "byte_size"):
        if not document.get(field):
            raise AuthoritySelectorError(
                f"{path}: selector is missing {field!r} — a selection that names "
                "no exact identity cannot be verified")
    return document


@dataclasses.dataclass(frozen=True)
class CorpusSelection:
    """The corpus identity a run was told to expect, and where it came from.

    `status` is carried, not inferred. A lock document that says it is PROPOSED
    stays PROPOSED all the way into the report; nothing in this module promotes a
    measured digest to a ratified one, and there is no code path that could.
    """

    path: Path
    expected_sha256: str
    expected_content_sha256: str | None
    provenance: dict
    lock_source: str
    status: str


def load_input_lock(path) -> dict:
    """An input-lock document: identity and provenance metadata, nothing else."""
    path = Path(path)
    if not path.exists():
        raise InputLockError(f"{path} not found — no corpus identity to verify against")
    with open(path, "r", encoding="utf-8") as handle:
        document = json.load(handle)
    schema = document.get("schema")
    if schema != INPUT_LOCK_SCHEMA:
        raise InputLockError(
            f"{path}: unexpected schema {schema!r}, expected {INPUT_LOCK_SCHEMA!r}")
    if not isinstance(document.get("corpus"), dict):
        raise InputLockError(f"{path}: 'corpus' is missing or is not an object")
    return document


def resolve_corpus_selection(paths: ProjectPaths, *, lock_path=None,
                             corpus_path=None, expected_sha256: str = None,
                             expected_content_sha256: str = None,
                             provenance: str = None) -> CorpusSelection:
    """Decide which corpus bytes a run is allowed to measure, and say why.

    Two sources, and they may be combined: an input-lock document, and direct
    arguments. A DISAGREEMENT between them is fatal rather than resolved by
    precedence -- silently preferring one would let a stale lock and a fresh flag
    coexist while the report named only one of them.

    A lock's `path` is repository-relative when it is not absolute, so the
    document stays portable and the root stays the caller's explicit input.
    """
    lock = load_input_lock(lock_path) if lock_path is not None else None
    lock_corpus = (lock or {}).get("corpus", {})

    def settle(field: str, direct, from_lock):
        if direct is not None and from_lock is not None and direct != from_lock:
            raise InputLockError(
                f"corpus {field}: the input lock says {from_lock!r} and the caller "
                f"says {direct!r} — refusing to pick one; state a single identity")
        return direct if direct is not None else from_lock

    resolved_sha = settle("sha256", expected_sha256, lock_corpus.get("sha256"))
    resolved_content = settle("content_sha256", expected_content_sha256,
                              lock_corpus.get("content_sha256"))
    lock_provenance = lock_corpus.get("provenance")
    if provenance is not None and lock_provenance is not None:
        raise InputLockError(
            "corpus provenance was declared twice — by the input lock and by the "
            "caller. State it once, in the document that will be reviewed")
    resolved_provenance = (
        {"statement": provenance} if provenance is not None else lock_provenance)

    raw_path = corpus_path
    if raw_path is None:
        raw_path = lock_corpus.get("path")
    if raw_path is None:
        resolved_path = paths.legacy_oracle_cards
    else:
        resolved_path = Path(raw_path)
        if not resolved_path.is_absolute():
            resolved_path = paths.resolve(*Path(raw_path).parts)

    if not resolved_sha:
        raise InputLockError(
            "no expected corpus sha256 — a run must state which bytes it believes "
            "it is measuring, so every count in the report names its input")
    if not resolved_provenance:
        raise InputLockError(
            "no declared corpus provenance — a digest with no stated origin "
            "identifies bytes without identifying where they came from")

    declared_size = lock_corpus.get("byte_size")
    if declared_size is not None:
        resolved_provenance = dict(resolved_provenance)
        resolved_provenance.setdefault("declared_byte_size", declared_size)

    return CorpusSelection(
        path=resolved_path,
        expected_sha256=resolved_sha,
        expected_content_sha256=resolved_content,
        provenance=resolved_provenance,
        lock_source=str(Path(lock_path)) if lock_path is not None else "caller-arguments",
        status=(lock or {}).get("status", "DECLARED_BY_CALLER"),
    )


@dataclasses.dataclass(frozen=True)
class RuntimeInputs:
    """Everything a run needs, resolved and explicit. No defaults are read here."""

    paths: ProjectPaths
    authority_path: Path
    codebook_path: Path
    corpus: CorpusSelection


def resolve_inputs(root, *, authority_path=None, codebook_path=None,
                   corpus_path=None, lock_path=None, expected_corpus_sha256=None,
                   expected_corpus_content_sha256=None,
                   corpus_provenance=None) -> RuntimeInputs:
    """Turn an explicit root plus optional overrides into one resolved input set.

    Every default comes from `ProjectPaths`, which is the layout owner; this
    module states no repository-relative literal of its own. Nothing here touches
    the filesystem except through the resolver for the input lock, which must be
    read to know what the corpus identity even is.
    """
    paths = ProjectPaths.for_root(root)
    return RuntimeInputs(
        paths=paths,
        authority_path=(Path(authority_path) if authority_path is not None
                        else paths.codebook_authority_selector),
        codebook_path=(Path(codebook_path) if codebook_path is not None
                       else paths.legacy_codebook_json),
        corpus=resolve_corpus_selection(
            paths, lock_path=lock_path, corpus_path=corpus_path,
            expected_sha256=expected_corpus_sha256,
            expected_content_sha256=expected_corpus_content_sha256,
            provenance=corpus_provenance),
    )


# ---------------------------------------------------------------------------
# Verified loading
# ---------------------------------------------------------------------------

def load_verified_codebook(inputs: RuntimeInputs):
    """Selector -> exact bytes -> schema gate -> lint. In that order.

    Returns `(document, lint_stats, identity, selector)`.

    The byte check runs BEFORE the parse on purpose. Parsing first and hashing
    afterwards would report a schema or lint verdict about a file the run had not
    yet established was the selected one, and the verdict would read as if it
    were about the selection.
    """
    selector = read_authority_selector(inputs.authority_path)
    identity = measure_file(inputs.codebook_path)
    if identity.byte_size != selector["byte_size"]:
        raise InputIdentityError("selected codebook", "byte_size",
                                 selector["byte_size"], identity.byte_size)
    if identity.sha256 != selector["sha256"]:
        raise InputIdentityError("selected codebook", "sha256",
                                 selector["sha256"], identity.sha256)
    document = codebook_store.read(inputs.codebook_path)
    stats = codebook.lint(document, str(inputs.codebook_path))
    return document, stats, identity, selector


def load_verified_corpus(inputs: RuntimeInputs):
    """Declared identity -> exact bytes -> the permanent loader. In that order.

    Returns `(cards, identity, content_sha256)`. `content_sha256` is measured
    whenever a run declared one to compare against, and is `None` otherwise --
    an unrequested second digest is work nobody asked for, and reporting one that
    was never compared invites it to be read as verified.
    """
    selection = inputs.corpus
    identity = measure_file(selection.path)
    if identity.sha256 != selection.expected_sha256:
        raise InputIdentityError("selected corpus", "sha256",
                                 selection.expected_sha256, identity.sha256)
    declared_size = (selection.provenance or {}).get("declared_byte_size")
    if declared_size is not None and identity.byte_size != declared_size:
        raise InputIdentityError("selected corpus", "byte_size",
                                 declared_size, identity.byte_size)
    content_sha256 = None
    if selection.expected_content_sha256:
        content_sha256 = measure_gzip_content(selection.path)
        if content_sha256 != selection.expected_content_sha256:
            raise InputIdentityError("selected corpus", "content_sha256",
                                     selection.expected_content_sha256, content_sha256)
    cards = corpus.load_cards(selection.path)
    return cards, identity, content_sha256


# ---------------------------------------------------------------------------
# Measurement over the loaded inputs
# ---------------------------------------------------------------------------

def _axis_membership_index(document: dict):
    """`(active_ids, active_membership_count, per_status_counts, any_status_ids)`.

    One walk, four facts, and they are kept apart because collapsing them is the
    error the report exists to prevent. A MEMBERSHIP is one (axis, card) pair; a
    covered CARD is one oracle_id that has at least one of them. The two numbers
    differ by however many cards sit on more than one axis, and quoting either as
    "coverage" without the other has been wrong in both directions.
    """
    axes = document.get("axes", {})
    active_ids: set[str] = set()
    any_status_ids: set[str] = set()
    active_memberships = 0
    any_memberships = 0
    per_status: dict[str, int] = {}
    for entry in axes.values():
        status = entry.get("status")
        per_status[status] = per_status.get(status, 0) + 1
        members = entry.get("members") or []
        any_memberships += len(members)
        for member in members:
            oracle_id = member.get("oracle_id")
            if oracle_id is None:
                continue
            any_status_ids.add(oracle_id)
            if status == ACTIVE_AXIS_STATUS:
                active_ids.add(oracle_id)
                active_memberships += 1
    return {
        "axes_total": len(axes),
        "axes_by_status": {k: per_status[k] for k in sorted(per_status, key=str)},
        "memberships_all_statuses": any_memberships,
        "memberships_active_axes": active_memberships,
        "distinct_member_ids_all_statuses": len(any_status_ids),
        "distinct_member_ids_active_axes": len(active_ids),
        "_active_ids": active_ids,
    }


def _evidence_field_presence(document: dict) -> dict:
    """How many assertions on ACTIVE axes still carry each evidence field.

    This is a CONSERVATION observation, not a semantic one. It proves the loaded
    document still holds the quote, locality and source provenance the codebook
    stores -- i.e. that loading did not flatten a member into an id -- and says
    nothing whatever about whether a quote is correct or an address resolves.
    Resolution is a corpus-relative question and is deliberately not asked here.
    """
    present = {"assertions": 0, "with_quote": 0, "with_locality": 0,
               "with_source_ref": 0, "with_corpus_ref": 0}
    for entry in document.get("axes", {}).values():
        if entry.get("status") != ACTIVE_AXIS_STATUS:
            continue
        for member in entry.get("members") or []:
            for assertion in member.get("assertions") or []:
                present["assertions"] += 1
                if assertion.get("quote"):
                    present["with_quote"] += 1
                if "locality" in assertion:
                    present["with_locality"] += 1
                if assertion.get("source_ref"):
                    present["with_source_ref"] += 1
                if assertion.get("corpus_ref"):
                    present["with_corpus_ref"] += 1
    return present


def _corpus_population(cards: dict) -> dict:
    """Full population and face structure, measured through the capability.

    Face counts go through `corpus.card_faces`, never through `card_faces` on the
    raw record: split, flip and adventure cards HAVE a `card_faces` list and one
    root-level text, so counting the raw list would report a face structure the
    readers of this corpus do not see.
    """
    faces_total = 0
    multi_face = 0
    max_faces = 0
    eligible = 0
    for card in cards.values():
        faces = corpus.card_faces(card)
        faces_total += len(faces)
        if len(faces) > 1:
            multi_face += 1
        max_faces = max(max_faces, len(faces))
        if corpus.is_gate0_eligible(card):
            eligible += 1
    name_index = corpus.build_name_index(cards)
    shared = [ids for ids in name_index.values() if len(ids) > 1]
    return {
        "unique_oracle_ids": len(cards),
        "faces_total": faces_total,
        "multi_face_cards": multi_face,
        "single_face_cards": len(cards) - multi_face,
        "max_faces_on_one_card": max_faces,
        "distinct_normalized_names": len(name_index),
        "normalized_names_shared_by_more_than_one_id": len(shared),
        "ids_sharing_a_normalized_name": sum(len(ids) for ids in shared),
        "duplicate_oracle_id_semantics": "last_write_wins",
        "_eligible": eligible,
    }


def build_report(document: dict, lint_stats: dict, codebook_identity: FileIdentity,
                 selector: dict, cards: dict, corpus_identity: FileIdentity,
                 corpus_content_sha256, selection: CorpusSelection,
                 inputs: RuntimeInputs) -> dict:
    """The whole deterministic payload. Pure: it reads nothing and writes nothing.

    Every count below is a count of EXISTING STRUCTURE. None of them is a quality
    measurement, none is evidence that a card is or is not similar to another,
    and an id with no active membership means only that this codebook records no
    active membership for it.
    """
    axis_facts = _axis_membership_index(document)
    active_ids = axis_facts.pop("_active_ids")
    population = _corpus_population(cards)
    eligible = population.pop("_eligible")

    corpus_ids = set(cards)
    covered = active_ids & corpus_ids
    absent = active_ids - corpus_ids
    memberships_on_absent = 0
    for entry in document.get("axes", {}).values():
        if entry.get("status") != ACTIVE_AXIS_STATUS:
            continue
        for member in entry.get("members") or []:
            if member.get("oracle_id") in absent:
                memberships_on_absent += 1

    eligible_covered = sum(
        1 for oracle_id in covered if corpus.is_gate0_eligible(cards[oracle_id]))

    return {
        "schema": REPORT_SCHEMA,
        "generator": {
            "package": "mtj_foundry",
            "version": __version__,
            "capability": "read_only_input_population_coverage_report",
        },
        "scope": {
            "performs": [
                "authority-selector read",
                "declared-identity verification of the codebook and the corpus",
                "schema-gated codebook load and lint",
                "full corpus load through the permanent capability",
                "counting of existing structure",
            ],
            "does_not_perform": [
                "semantic inference",
                "membership assignment",
                "ranking or retrieval",
                "codebook mutation",
                "any write of canonical input, cache, manifest or authority state",
            ],
            "report_is": "DERIVED_EVIDENCE_NOT_AUTHORITY",
        },
        "inputs": {
            # THE ROOT IS NOT IN THE PAYLOAD, ON PURPOSE. It is a machine fact, and
            # a report carrying one is comparable only to reports from the same
            # checkout. Identity here means DIGESTS; the exact invocation belongs in
            # whatever record cites the report, not inside the deterministic bytes.
            "paths_are": ("repository-relative to the caller's declared root; "
                          "absolute only when the file lies outside it"),
            "authority_selector": {
                "path": _label(inputs.paths, inputs.authority_path),
                "schema": selector.get("schema"),
                "snapshot_id": selector.get("snapshot_id"),
                "object_path": selector.get("object_path"),
                "codebook_schema": selector.get("codebook_schema"),
                "codebook_version": selector.get("codebook_version"),
                "corpus_ref": selector.get("corpus_ref"),
                "selected_sha256": selector.get("sha256"),
                "selected_byte_size": selector.get("byte_size"),
            },
            "codebook": {
                "path": _label(inputs.paths, codebook_identity.path),
                "measured_sha256": codebook_identity.sha256,
                "measured_byte_size": codebook_identity.byte_size,
                "matches_selected_authority": True,
                "verification": "LOCAL_BYTES_VERIFIED_AGAINST_TRACKED_SELECTOR",
                "remote_durability_verified": False,
            },
            "corpus": {
                "path": _label(inputs.paths, corpus_identity.path),
                "measured_sha256": corpus_identity.sha256,
                "measured_byte_size": corpus_identity.byte_size,
                "expected_sha256": selection.expected_sha256,
                "expected_content_sha256": selection.expected_content_sha256,
                "measured_content_sha256": corpus_content_sha256,
                "identity_source": _label(inputs.paths, Path(selection.lock_source))
                if selection.lock_source != "caller-arguments" else "caller-arguments",
                "identity_status": selection.status,
                "provenance": selection.provenance,
            },
        },
        "codebook_lint": {
            "axes": lint_stats.get("axes"),
            "members_with_assertions": lint_stats.get("members"),
            "assertions": lint_stats.get("assertions"),
            "exemptions_applied": [list(k) for k in lint_stats.get("exemptions_applied", [])],
            "result": "PASS",
        },
        "codebook_structure": axis_facts,
        "codebook_evidence_fields_present_on_active_axes": _evidence_field_presence(document),
        "corpus_population": population,
        "eligibility": {
            "predicate": "legal or restricted in at least one Scryfall legalities format",
            "ruling": "Gate #0, batch-6 D1, ratified 2026-07-30",
            "full_population_unique_ids": len(cards),
            "eligible_unique_ids": eligible,
            "ineligible_unique_ids": len(cards) - eligible,
            "note": ("eligibility partitions the full population and removes nothing "
                     "from it; every count above is reported against the full corpus"),
        },
        "coverage": {
            "definition": ("a corpus oracle_id is COVERED iff at least one axis with "
                           "status 'active' lists it as a member. this is a statement "
                           "about the codebook's recorded structure, never about "
                           "similarity, quality, or whether a card has been reviewed"),
            "memberships_are_not_cards": ("memberships_active_axes counts (axis, card) "
                                          "pairs; covered counts distinct cards"),
            "corpus_ids_total": len(corpus_ids),
            "corpus_ids_covered": len(covered),
            "corpus_ids_uncovered": len(corpus_ids) - len(covered),
            "eligible_ids_covered": eligible_covered,
            "eligible_ids_uncovered": eligible - eligible_covered,
            "ineligible_ids_covered": len(covered) - eligible_covered,
            "active_member_ids_absent_from_corpus": len(absent),
            "memberships_on_active_member_ids_absent_from_corpus": memberships_on_absent,
            "absent_ids_are": ("accounted for separately and NOT discarded: they are "
                               "member ids this corpus snapshot does not contain"),
        },
    }


def _label(paths: ProjectPaths, target: Path) -> str:
    """A repository-relative posix label when the path is inside the root.

    Two runs from the same root must produce byte-identical reports, and they do
    either way; this exists so a report is also comparable across roots, which an
    absolute path would quietly prevent. A path outside the root keeps its
    absolute form rather than growing a chain of `..` segments that would read as
    if it were repository-relative.
    """
    target = Path(os.path.normpath(
        target if target.is_absolute() else Path(os.getcwd()) / target))
    try:
        return target.relative_to(paths.root).as_posix()
    except ValueError:
        return target.as_posix()


def render_report(report: dict) -> str:
    """The byte contract: `indent=2`, `ensure_ascii=False`, one trailing newline.

    The same contract the codebook store uses, for the same reason: a report
    whose bytes depend on the platform's default encoding decisions cannot be
    compared between two runs, and comparing two runs is how determinism is
    proven here.
    """
    return json.dumps(report, indent=2, ensure_ascii=False) + "\n"


def run(root, **kwargs) -> dict:
    """THE composition entry point. Resolve, verify, load, count, return.

    Returns the report as a dict. Raises on every failure; the CLI is what turns
    a raised failure into a process exit status, and no partial or
    success-shaped report is produced on any error path.
    """
    inputs = resolve_inputs(root, **kwargs)
    document, lint_stats, codebook_identity, selector = load_verified_codebook(inputs)
    cards, corpus_identity, content_sha256 = load_verified_corpus(inputs)
    return build_report(document, lint_stats, codebook_identity, selector, cards,
                        corpus_identity, content_sha256, inputs.corpus, inputs)
