"""The `mtj-agent-bus/1` envelope: extraction, strict parsing, strict validation.

Two rules shape everything below.

1. **No prose parsing.** A message exists only inside a fenced block whose info
   string is exactly `mtj-bus`, and its content is JSON. Free text in a comment
   is not a fallback source of fields; it is not read at all.
2. **Strict or nothing.** Unknown keys, wrong types, unsupported schema versions
   and actor/kind mismatches are rejections with codes, never best-guesses. A
   message that does not validate cannot authorize anything.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Mapping

from agent_bus import SCHEMA
from agent_bus import errors as E
from agent_bus.errors import BusError

FENCE_INFO = "mtj-bus"
# A fenced block opened by >=3 backticks with the exact info string, closed by a
# fence of at least the same length. Indentation is not allowed: a bus block is
# a top-level block, never a quoted or nested fragment of someone's example.
_FENCE_RE = re.compile(
    r"^(?P<fence>`{3,})[ \t]*" + FENCE_INFO + r"[ \t]*\r?\n"
    r"(?P<payload>.*?)\r?\n?(?P=fence)[ \t]*$",
    re.MULTILINE | re.DOTALL,
)

ACTORS = ("CAPTAIN", "MANAGER", "WORKER")
KINDS = (
    "WAVE_COMMAND",
    "WAVE_PROGRESS",
    "WAVE_RESULT",
    "WAVE_REVIEW",
    "CAPTAIN_REQUIRED",
    "WAVE_ABORT",
)

# Which actor may speak which kind. This table is the whole of actor/kind law;
# there is no second place where a kind's speaker is decided.
ACTOR_KIND: Mapping[str, frozenset[str]] = {
    "WAVE_COMMAND": frozenset({"MANAGER"}),
    "WAVE_REVIEW": frozenset({"MANAGER"}),
    "WAVE_ABORT": frozenset({"MANAGER", "CAPTAIN"}),
    "WAVE_PROGRESS": frozenset({"WORKER"}),
    "WAVE_RESULT": frozenset({"WORKER"}),
    "CAPTAIN_REQUIRED": frozenset({"MANAGER", "WORKER"}),
}

# Loop prevention lives here, as data. An agent acts on the kinds addressed to
# it and on nothing else, so its own output can never wake it.
WAKES: Mapping[str, frozenset[str]] = {
    "WORKER": frozenset({"WAVE_COMMAND", "WAVE_ABORT"}),
    "MANAGER": frozenset({"WAVE_RESULT", "CAPTAIN_REQUIRED"}),
    "CAPTAIN": frozenset({"CAPTAIN_REQUIRED"}),
}

ENVELOPE_FIELDS = (
    "schema",
    "message_id",
    "actor",
    "kind",
    "wave",
    "parent",
    "authority",
    "base",
    "created_at",
    "body",
)
AUTHORITY_FIELDS = ("issue", "checkpoint", "task")

MESSAGE_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
WAVE_RE = re.compile(r"^[A-Z0-9][A-Z0-9._-]{2,80}$")
UNIT_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9._-]{0,60}$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
TIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

# Kinds whose parent is structurally required. A result that cannot name the
# command it answers is not a result.
PARENT_REQUIRED_KINDS = frozenset({"WAVE_PROGRESS", "WAVE_RESULT", "WAVE_REVIEW"})

_BODY_SPEC: Mapping[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    # kind: (required keys, optional keys)
    # `candidate_base` is how a REPAIR wave says "build on this unaccepted commit"
    # without weakening `base`, which must stay equal to the accepted head so a
    # stale command is still detectable. Two different ideas, two different fields.
    "WAVE_COMMAND": (("branch", "units", "review_boundary"),
                     ("stop_conditions", "note", "candidate_base")),
    "WAVE_PROGRESS": (("unit", "status"), ("commit", "note")),
    "WAVE_RESULT": (
        ("status", "branch", "head", "units"),
        ("validation", "discrepancies", "next", "note"),
    ),
    "WAVE_REVIEW": (("verdict",), ("accepted_head", "note")),
    "CAPTAIN_REQUIRED": (("question",), ("options", "blocking", "note")),
    "WAVE_ABORT": (("reason",), ()),
}

PROGRESS_STATUS = ("STARTED", "DONE", "FAILED", "BLOCKED")
RESULT_STATUS = ("P", "S", "F")
UNIT_RESULT_STATUS = ("DONE", "FAILED", "BLOCKED", "SKIPPED")
VERDICTS = ("ACCEPT", "REPAIR", "CAPTAIN")


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    seen: dict[str, Any] = {}
    for key, value in pairs:
        if key in seen:
            raise BusError(E.DUPLICATE_JSON_KEY, f"key {key!r} appears twice")
        seen[key] = value
    return seen


def extract(comment_body: str) -> str | None:
    """Return the single bus payload in `comment_body`, or None if there is none.

    None is the answer for every ordinary human comment, every `@claude` mention
    and every unrelated review note: they are inert, not errors. Two bus blocks
    in one comment IS an error, because there would be no deterministic answer
    to "which message is this comment".
    """
    found = _FENCE_RE.findall(comment_body or "")
    if not found:
        return None
    if len(found) > 1:
        raise BusError(E.AMBIGUOUS_ENVELOPE, f"{len(found)} bus blocks in one comment")
    return found[0][1]


@dataclass(frozen=True)
class Envelope:
    schema: str
    message_id: str
    actor: str
    kind: str
    wave: str
    parent: str | None
    authority: dict[str, int]
    base: str
    created_at: str
    body: dict[str, Any]

    def wakes(self, actor: str) -> bool:
        """True when this message is one the given actor is allowed to act on."""
        return self.kind in WAKES.get(actor, frozenset()) and self.actor != actor

    def to_json(self) -> str:
        return json.dumps(
            {f: getattr(self, f) for f in ENVELOPE_FIELDS},
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )

    def render(self) -> str:
        """The exact comment body that carries this message."""
        return f"```{FENCE_INFO}\n{self.to_json()}\n```\n"


def _require_object(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BusError(E.BAD_TYPE, f"{where} must be an object, got {type(value).__name__}")
    return value


def _require_str(mapping: Mapping[str, Any], key: str, where: str) -> str:
    value = mapping[key]
    if not isinstance(value, str):
        raise BusError(E.BAD_TYPE, f"{where}.{key} must be a string, got {type(value).__name__}")
    return value


def _require_list_of_str(mapping: Mapping[str, Any], key: str, where: str) -> list[str]:
    value = mapping.get(key, [])
    if not isinstance(value, list) or any(not isinstance(v, str) for v in value):
        raise BusError(E.BAD_TYPE, f"{where}.{key} must be a list of strings")
    return list(value)


def _exact_keys(mapping: Mapping[str, Any], required, optional, where: str) -> None:
    for key in required:
        if key not in mapping:
            raise BusError(E.MISSING_FIELD, f"{where}.{key}")
    allowed = set(required) | set(optional)
    for key in sorted(mapping):
        if key not in allowed:
            raise BusError(E.UNKNOWN_FIELD, f"{where}.{key}")


def parse(payload: str) -> Envelope:
    """Parse and fully validate one bus payload. Raises `BusError` on anything else."""
    try:
        raw = json.loads(payload, object_pairs_hook=_no_duplicate_keys)
    except BusError:
        raise
    except json.JSONDecodeError as exc:
        raise BusError(E.MALFORMED_JSON, f"line {exc.lineno} column {exc.colno}: {exc.msg}")
    if not isinstance(raw, dict):
        raise BusError(E.NOT_AN_OBJECT, f"envelope is {type(raw).__name__}, not an object")

    # Schema first: an unsupported version must not be read with v1 field law.
    if "schema" not in raw:
        raise BusError(E.MISSING_FIELD, "envelope.schema")
    schema = raw["schema"]
    if not isinstance(schema, str):
        raise BusError(E.BAD_TYPE, "envelope.schema must be a string")
    if schema != SCHEMA:
        raise BusError(E.SCHEMA_UNSUPPORTED, f"{schema!r} is not {SCHEMA!r}")

    _exact_keys(raw, ENVELOPE_FIELDS, (), "envelope")

    message_id = _require_str(raw, "message_id", "envelope")
    if not MESSAGE_ID_RE.match(message_id) or not 8 <= len(message_id) <= 120:
        raise BusError(E.BAD_VALUE, f"envelope.message_id {message_id!r} is not a bus id")

    actor = _require_str(raw, "actor", "envelope")
    if actor not in ACTORS:
        raise BusError(E.ACTOR_UNKNOWN, f"{actor!r} not in {list(ACTORS)}")

    kind = _require_str(raw, "kind", "envelope")
    if kind not in KINDS:
        raise BusError(E.KIND_UNKNOWN, f"{kind!r} not in {list(KINDS)}")

    if actor not in ACTOR_KIND[kind]:
        raise BusError(
            E.ACTOR_KIND_MISMATCH,
            f"{actor} may not speak {kind}; allowed: {sorted(ACTOR_KIND[kind])}",
        )

    wave = _require_str(raw, "wave", "envelope")
    if not WAVE_RE.match(wave):
        raise BusError(E.BAD_VALUE, f"envelope.wave {wave!r} is not a wave id")

    parent = raw["parent"]
    if parent is not None:
        if not isinstance(parent, str):
            raise BusError(E.BAD_TYPE, "envelope.parent must be a string or null")
        if not MESSAGE_ID_RE.match(parent):
            raise BusError(E.BAD_VALUE, f"envelope.parent {parent!r} is not a bus id")
    if parent is None and kind in PARENT_REQUIRED_KINDS:
        raise BusError(E.PARENT_REQUIRED, f"{kind} must name the command it answers")

    authority = _require_object(raw["authority"], "envelope.authority")
    _exact_keys(authority, AUTHORITY_FIELDS, (), "envelope.authority")
    for key in AUTHORITY_FIELDS:
        value = authority[key]
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise BusError(E.BAD_VALUE, f"envelope.authority.{key} must be a positive integer")

    base = _require_str(raw, "base", "envelope")
    if not SHA_RE.match(base):
        raise BusError(E.BAD_VALUE, "envelope.base must be a 40-character lowercase sha")

    created_at = _require_str(raw, "created_at", "envelope")
    if not TIME_RE.match(created_at):
        raise BusError(E.BAD_VALUE, "envelope.created_at must be YYYY-MM-DDTHH:MM:SSZ")

    body = _require_object(raw["body"], "envelope.body")
    _validate_body(kind, actor, body)

    return Envelope(
        schema=schema,
        message_id=message_id,
        actor=actor,
        kind=kind,
        wave=wave,
        parent=parent,
        authority={k: int(authority[k]) for k in AUTHORITY_FIELDS},
        base=base,
        created_at=created_at,
        body=body,
    )


def _validate_body(kind: str, actor: str, body: Mapping[str, Any]) -> None:
    required, optional = _BODY_SPEC[kind]
    _exact_keys(body, required, optional, "body")

    if kind == "WAVE_COMMAND":
        _require_str(body, "branch", "body")
        _require_str(body, "review_boundary", "body")
        _require_list_of_str(body, "stop_conditions", "body")
        _optional_sha(body, "candidate_base")
        units = body["units"]
        if not isinstance(units, list):
            raise BusError(E.BAD_TYPE, "body.units must be a list")
        # Shape only here; dependency law lives in agent_bus.wave.
        for index, unit in enumerate(units):
            _validate_unit(_require_object(unit, f"body.units[{index}]"), index)

    elif kind == "WAVE_PROGRESS":
        unit = _require_str(body, "unit", "body")
        if not UNIT_ID_RE.match(unit):
            raise BusError(E.BAD_VALUE, f"body.unit {unit!r} is not a unit id")
        status = _require_str(body, "status", "body")
        if status not in PROGRESS_STATUS:
            raise BusError(E.BAD_VALUE, f"body.status {status!r} not in {list(PROGRESS_STATUS)}")
        _optional_sha(body, "commit")

    elif kind == "WAVE_RESULT":
        status = _require_str(body, "status", "body")
        if status not in RESULT_STATUS:
            raise BusError(E.BAD_VALUE, f"body.status {status!r} not in {list(RESULT_STATUS)}")
        _require_str(body, "branch", "body")
        head = _require_str(body, "head", "body")
        if not SHA_RE.match(head):
            raise BusError(E.BAD_VALUE, "body.head must be a 40-character lowercase sha")
        units = body["units"]
        if not isinstance(units, list):
            raise BusError(E.BAD_TYPE, "body.units must be a list")
        for index, entry in enumerate(units):
            where = f"body.units[{index}]"
            entry = _require_object(entry, where)
            _exact_keys(entry, ("id", "status"), ("commit", "note"), where)
            if not UNIT_ID_RE.match(_require_str(entry, "id", where)):
                raise BusError(E.BAD_VALUE, f"{where}.id is not a unit id")
            if entry["status"] not in UNIT_RESULT_STATUS:
                raise BusError(E.BAD_VALUE, f"{where}.status not in {list(UNIT_RESULT_STATUS)}")
            _optional_sha(entry, "commit", where)
        for key in ("validation", "discrepancies"):
            _require_list_of_str(body, key, "body")
        # A Worker never selects what runs next. `next` exists so the Worker can
        # say NONE durably; any other value is the Worker authorizing itself.
        if body.get("next", "NONE") != "NONE":
            raise BusError(E.BAD_VALUE, "body.next must be NONE; a Worker cannot select successors")

    elif kind == "WAVE_REVIEW":
        verdict = _require_str(body, "verdict", "body")
        if verdict not in VERDICTS:
            raise BusError(E.BAD_VALUE, f"body.verdict {verdict!r} not in {list(VERDICTS)}")
        _optional_sha(body, "accepted_head")

    elif kind == "CAPTAIN_REQUIRED":
        _require_str(body, "question", "body")
        _require_list_of_str(body, "options", "body")
        if not isinstance(body.get("blocking", True), bool):
            raise BusError(E.BAD_TYPE, "body.blocking must be a boolean")

    elif kind == "WAVE_ABORT":
        _require_str(body, "reason", "body")


def _optional_sha(mapping: Mapping[str, Any], key: str, where: str = "body") -> None:
    value = mapping.get(key)
    if value is None:
        return
    if not isinstance(value, str) or not SHA_RE.match(value):
        raise BusError(E.BAD_VALUE, f"{where}.{key} must be a 40-character lowercase sha or null")


UNIT_REQUIRED = ("id", "objective", "depends_on", "allow_paths", "validation", "mutating")
UNIT_OPTIONAL = (
    "deny_paths",
    "negative_controls",
    "stop_conditions",
    "commit_boundary",
    "concurrency",
    "note",
)
CONCURRENCY = ("SERIAL", "PARALLEL_SAFE")


def _validate_unit(unit: Mapping[str, Any], index: int) -> None:
    where = f"body.units[{index}]"
    _exact_keys(unit, UNIT_REQUIRED, UNIT_OPTIONAL, where)
    unit_id = _require_str(unit, "id", where)
    if not UNIT_ID_RE.match(unit_id):
        raise BusError(E.BAD_VALUE, f"{where}.id {unit_id!r} is not a unit id")
    _require_str(unit, "objective", where)
    for key in ("depends_on", "allow_paths", "validation"):
        _require_list_of_str(unit, key, where)
    for key in ("deny_paths", "negative_controls", "stop_conditions"):
        _require_list_of_str(unit, key, where)
    mutating = unit["mutating"]
    if not isinstance(mutating, bool):
        raise BusError(E.BAD_TYPE, f"{where}.mutating must be a boolean")
    if not isinstance(unit.get("commit_boundary", True), bool):
        raise BusError(E.BAD_TYPE, f"{where}.commit_boundary must be a boolean")
    concurrency = unit.get("concurrency", "SERIAL")
    if concurrency not in CONCURRENCY:
        raise BusError(E.BAD_VALUE, f"{where}.concurrency not in {list(CONCURRENCY)}")
    # Scope and validation are not optional on a unit that changes the repository.
    if mutating and not unit["allow_paths"]:
        raise BusError(E.UNIT_SCOPE_MISSING, f"{where} mutates but declares no allow_paths")
    if not unit["validation"]:
        raise BusError(E.UNIT_VALIDATION_MISSING, f"{where} declares no validation")


def parse_comment(comment_body: str) -> Envelope | None:
    """Extract and parse in one step. None means "inert human comment"."""
    payload = extract(comment_body)
    if payload is None:
        return None
    return parse(payload)
