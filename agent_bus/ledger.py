"""Issue #1 ledger records: read a checkpoint strictly, write V and K canonically.

R3 recognised a checkpoint by a `schema: mtj-checkpoint/N` line ANYWHERE in a
comment, and read `h`/`a` from any line, indented or not. So a verdict that
quoted a checkpoint, or a nested `h:` under some other key, could become the
selector. This module replaces that with a record boundary.

**A ledger record starts the comment.** Either the comment's first line is a
` ```yaml ` fence and its second line is the schema line -- the record then runs
to the first closing fence -- or the comment's first line IS the schema line and
the record is the whole comment. Nothing before it, no indentation.

**Only top-level scalars are fields.** A key counts only at column 0 inside the
record. Indented keys belong to some nested structure and are never read, and a
field that appears twice is an ambiguity, not a choice.

Text that mentions a checkpoint schema without being a record is a LOOKALIKE. It
selects nothing; callers report it.

The writing half is deliberately tiny: the publisher's V and K are rendered here
from a fixed key order, so "is this exactly what the publisher would have
written?" is a string comparison, not a judgement.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Mapping, Sequence

CHECKPOINT = "mtj-checkpoint"
VERDICT = "mtj-verdict"
DISPOSITION = "mtj-disposition"

_FENCE_OPEN = "```yaml"
_FENCE_CLOSE = "```"
_SCHEMA_RE = re.compile(r"^schema:[ \t]*(?P<name>mtj-[a-z]+)/(?P<version>\d+)[ \t]*$")
_FIELD_RE = re.compile(r"^(?P<key>[A-Za-z_][A-Za-z0-9_]*):(?:[ \t]+(?P<value>.*?))?[ \t]*$")
_TOKEN_RE = re.compile(r"^(?P<token>\S+)(?:[ \t]+#.*)?$")
LOOKALIKE_RE = re.compile(r"mtj-checkpoint/\d")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class LedgerError(ValueError):
    """A comment that opens as a ledger record but is not a well-formed one."""


@dataclass(frozen=True)
class Record:
    """One strictly bounded ledger record."""

    schema: str  # e.g. "mtj-checkpoint"
    version: int
    fields: Mapping[str, str | None]  # column-0 keys; None = a nested block follows
    fenced: bool

    def token(self, key: str) -> str | None:
        """A field's single scalar token (a trailing `# comment` allowed), or None."""
        value = self.fields.get(key)
        if value is None:
            return None
        match = _TOKEN_RE.match(value)
        if not match:
            raise LedgerError(f"field {key!r} is not a single scalar: {value!r}")
        return match.group("token")


def _lines(body: str) -> list[str]:
    return (body or "").splitlines()


def record_lines(body: str) -> tuple[list[str], bool] | None:
    """The lines of the record that STARTS this comment, or None if none does."""
    lines = _lines(body)
    if not lines:
        return None
    if lines[0].rstrip() == _FENCE_OPEN:
        if len(lines) < 2 or not _SCHEMA_RE.match(lines[1]):
            return None
        for index in range(2, len(lines)):
            if lines[index].rstrip() == _FENCE_CLOSE:
                return lines[1:index], True
        raise LedgerError("the record's yaml fence is never closed")
    if _SCHEMA_RE.match(lines[0]):
        return lines, False
    return None


def parse_record(body: str) -> Record | None:
    """The ledger record this comment opens with, or None. Raises on a malformed one."""
    found = record_lines(body)
    if found is None:
        return None
    lines, fenced = found
    schema = _SCHEMA_RE.match(lines[0])
    assert schema is not None  # record_lines only returns on a schema line
    fields: dict[str, str | None] = {}
    for line in lines[1:]:
        if not line or line[0] in " \t#-":
            continue  # blank, nested, comment or sequence item: never a field
        match = _FIELD_RE.match(line)
        if not match:
            continue  # prose at column 0 inside a bare record: not a field
        key = match.group("key")
        if key in fields or key == "schema":
            raise LedgerError(f"field {key!r} appears more than once")
        fields[key] = match.group("value") or None
    return Record(schema=schema.group("name"), version=int(schema.group("version")),
                  fields=fields, fenced=fenced)


def is_checkpoint(body: str) -> bool:
    """Does this comment OPEN as a checkpoint record? Malformed ones count."""
    lines = _lines(body)
    if not lines:
        return False
    head = lines[0]
    if head.rstrip() == _FENCE_OPEN:
        head = lines[1] if len(lines) > 1 else ""
    match = _SCHEMA_RE.match(head)
    return bool(match) and match.group("name") == CHECKPOINT


def is_lookalike(body: str) -> bool:
    """Mentions a checkpoint schema without opening as a checkpoint record."""
    return bool(LOOKALIKE_RE.search(body or "")) and not is_checkpoint(body)


@dataclass(frozen=True)
class Checkpoint:
    head: str
    active: int
    record: Record


def read_checkpoint(body: str) -> Checkpoint:
    """`h` and `a` from a checkpoint record, or LedgerError naming what is wrong.

    `h`/`accepted_head` and `a`/`active_task` are two spellings of one field. A
    record may carry either or both; when it carries both they must agree.
    """
    record = parse_record(body)
    if record is None or record.schema != CHECKPOINT:
        raise LedgerError("the comment does not open with a checkpoint record")
    head = _one_of(record, "h", "accepted_head")
    active = _one_of(record, "a", "active_task")
    if head is None or active is None:
        raise LedgerError("missing h/a; it cannot select anything")
    if not SHA_RE.match(head):
        raise LedgerError(f"h={head!r} is not a 40-hex sha")
    if not re.fullmatch(r"\d+", active):
        raise LedgerError(f"a={active!r} is not a comment id")
    return Checkpoint(head=head, active=int(active), record=record)


def _one_of(record: Record, short: str, long: str) -> str | None:
    first, second = record.token(short), record.token(long)
    if first is not None and second is not None and first != second:
        raise LedgerError(f"{short}={first!r} disagrees with {long}={second!r}")
    return first if first is not None else second


# ------------------------------------------------------------------- writing
# Fixed key orders. A publisher record is valid only if it re-renders to itself.

VERDICT_KEYS = (
    "recorded_by", "transaction", "task_comment", "selecting_checkpoint",
    "transport_pr", "result_comment", "result_message", "result_digest", "wave",
    "verdict", "candidate_head", "accepted_head", "next_accepted_head",
    "next_active_task", "review_message", "override", "goal_plan", "validation", "decision",
)
CHECKPOINT_KEYS = (
    "h", "a", "accepted_head", "active_task", "recorded_by", "transaction",
    "prior_checkpoint", "latest_manager_verdict", "verdict", "transport_pr",
    "result_comment", "result_message", "result_head", "origin_command",
    "repair_round", "successor_command", "unanswered", "next",
)


# One per Manager-bound message a checkpoint displaced without answering it.
DISPOSITION_KEYS = (
    "recorded_by", "transaction", "message_comment", "message_id", "kind", "wave",
    "cited_checkpoint", "superseded_by", "deciding_transaction", "disposition",
    "captain_attention", "next",
)


def compact_json(value) -> str:
    """One line, sorted, ASCII: a JSON value that is also a YAML flow scalar."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def render(schema: str, version: int, keys: Sequence[str], fields: Mapping[str, object]) -> str:
    if set(fields) != set(keys):
        missing = sorted(set(keys) - set(fields))
        extra = sorted(set(fields) - set(keys))
        raise LedgerError(f"fields do not match the record form: missing {missing}, extra {extra}")
    lines = [_FENCE_OPEN, f"schema: {schema}/{version}"]
    for key in keys:
        value = fields[key]
        text = value if isinstance(value, str) else compact_json(value)
        if "\n" in text or "\r" in text or not text:
            raise LedgerError(f"field {key!r} must be one non-empty line")
        lines.append(f"{key}: {text}")
    lines.append(_FENCE_CLOSE)
    return "\n".join(lines) + "\n"


def render_verdict(fields: Mapping[str, object]) -> str:
    return render(VERDICT, 0, VERDICT_KEYS, fields)


def render_checkpoint(fields: Mapping[str, object]) -> str:
    return render(CHECKPOINT, 2, CHECKPOINT_KEYS, fields)


def render_disposition(fields: Mapping[str, object]) -> str:
    return render(DISPOSITION, 0, DISPOSITION_KEYS, fields)
