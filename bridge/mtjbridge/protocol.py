"""Typed, validated protocol schemas for the mtj bridge.

Four message kinds travel over GitHub, each as a fenced ```yaml block:

  mtj-task/1    Manager -> Worker    an authorization to do exactly one thing
  mtj-claim/1   Worker  -> ledger    a durable "I am executing this issue" lock
  mtj-result/1  Worker  -> Manager   what actually happened
  mtj-review/1  Manager -> ledger    the verdict on a result

Validation is strict about the fields the state machine reads and permissive
about extra descriptive fields, because the Manager is a model and will write
more prose than the machine consumes. Anything the state machine *acts on*
must be present and in-domain, or parsing raises ProtocolError.
"""

from __future__ import annotations

import dataclasses
import datetime as _dt
import re
from typing import Any

from . import yamlite

__all__ = [
    "ProtocolError",
    "Task",
    "Result",
    "Review",
    "Claim",
    "VERDICTS",
    "RESULT_STATUSES",
    "TASK_STATUSES",
    "parse_task",
    "parse_result",
    "parse_review",
    "parse_claim",
    "render_block",
]


class ProtocolError(ValueError):
    """A protocol message is missing a field the state machine acts on, or is out of domain."""


VERDICTS = ("PASS", "REPAIR", "CAPTAIN_DECISION_REQUIRED", "STOP")
RESULT_STATUSES = ("COMPLETE", "PASS", "STOP", "FAIL")
TASK_STATUSES = ("READY", "BLOCKED", "DONE", "DRAFT", "SUPERSEDED")

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _require(data: dict, key: str, kind: str) -> Any:
    if not isinstance(data, dict):
        raise ProtocolError(f"{kind}: expected a mapping, got {type(data).__name__}")
    if key not in data:
        raise ProtocolError(f"{kind}: missing required field '{key}'")
    value = data[key]
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ProtocolError(f"{kind}: required field '{key}' is empty")
    return value


def _enum(value: Any, domain: tuple[str, ...], kind: str, key: str) -> str:
    text = str(value).strip()
    if text not in domain:
        raise ProtocolError(
            f"{kind}: field '{key}' is '{text}', which is outside the domain {list(domain)}"
        )
    return text


def _as_list(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


_SENTINEL_EMPTY = {"none", "n/a", "na", "null", "nothing", "no", "-"}


def _as_str_list(value: Any, drop_sentinels: bool = False) -> list[str]:
    """Coerce to a list of strings.

    With drop_sentinels, a placeholder like `- NONE` is treated as an EMPTY list.
    Workers and models both write 'NONE' to mean 'nothing here', and reading that
    as content would fire a Captain halt on a clean result.
    """
    items = [str(v) for v in _as_list(value) if v is not None]
    if drop_sentinels:
        items = [i for i in items if i.strip().lower() not in _SENTINEL_EMPTY]
    return items


def _check_sha(value: Any, kind: str, key: str) -> str:
    text = str(value).strip()
    if not _SHA_RE.match(text):
        raise ProtocolError(
            f"{kind}: field '{key}' must be a full 40-character lowercase git SHA, got '{text}'. "
            "Abbreviated SHAs are refused so a base cannot silently resolve to a different commit."
        )
    return text


def _parse_body(markdown_or_yaml: str, kind: str) -> Any:
    """Parse a protocol block, converting any parser failure into a ProtocolError.

    The manager and worker both treat ProtocolError as 'halt cleanly'. A model that
    answers in prose, or emits malformed YAML, must produce a STOP verdict - never
    an uncaught traceback that kills the cycle mid-write.
    """
    try:
        data = yamlite.parse_first_block(markdown_or_yaml)
    except yamlite.YamlLiteError as exc:
        raise ProtocolError(f"{kind}: body is not parseable as a {kind} block: {exc}") from exc
    if not isinstance(data, dict):
        raise ProtocolError(f"{kind}: body did not contain a YAML mapping")
    return data


# --------------------------------------------------------------------------
# mtj-task/1
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Task:
    schema: str
    task: str
    base: str
    base_branch: str
    status: str
    issue_number: int | None = None
    objective: list[str] = dataclasses.field(default_factory=list)
    allow_paths: list[str] = dataclasses.field(default_factory=list)
    deny_paths: list[str] = dataclasses.field(default_factory=list)
    prohibited: list[str] = dataclasses.field(default_factory=list)
    stop: list[str] = dataclasses.field(default_factory=list)
    delivery: str = ""
    next_authorized: str = "NONE"
    mutating: bool = True
    raw: dict = dataclasses.field(default_factory=dict, repr=False)

    @property
    def is_ready(self) -> bool:
        return self.status == "READY"

    @property
    def authorizes_successor(self) -> bool:
        return str(self.next_authorized).strip().upper() not in ("NONE", "", "NULL")


def _scope_paths(raw: dict) -> tuple[list[str], list[str]]:
    """Extract machine-readable allow/deny path globs when the task provides them.

    A task that does not provide them yields empty lists, and the caller must
    treat that as 'not machine-checkable' rather than as 'everything allowed'.
    """
    allow: list[str] = []
    deny: list[str] = []
    scope = raw.get("scope")
    if isinstance(scope, dict):
        allow += _as_str_list(scope.get("allow_paths") or scope.get("allow"))
        deny += _as_str_list(scope.get("deny_paths") or scope.get("deny"))
    allow += _as_str_list(raw.get("allow_paths"))
    deny += _as_str_list(raw.get("deny_paths"))
    return allow, deny


def parse_task(markdown_or_yaml: str, issue_number: int | None = None) -> Task:
    data = _parse_body(markdown_or_yaml, "mtj-task")
    schema = str(_require(data, "schema", "mtj-task"))
    if not schema.startswith("mtj-task/"):
        raise ProtocolError(f"mtj-task: wrong schema '{schema}'")
    status = _enum(_require(data, "status", "mtj-task"), TASK_STATUSES, "mtj-task", "status")
    base = _check_sha(_require(data, "base", "mtj-task"), "mtj-task", "base")
    allow, deny = _scope_paths(data)
    scope = data.get("scope") if isinstance(data.get("scope"), dict) else {}
    delivery = str(scope.get("delivery", data.get("delivery", "")) or "")
    nxt = data.get("next")
    next_auth = "NONE"
    if isinstance(nxt, dict):
        next_auth = str(nxt.get("authorized", "NONE") or "NONE")
    elif nxt is not None:
        next_auth = str(nxt)
    kind = str(scope.get("kind", "")).lower()
    mutating = "read_only" not in kind and "read-only" not in kind
    return Task(
        schema=schema,
        task=str(_require(data, "task", "mtj-task")),
        base=base,
        base_branch=str(_require(data, "base_branch", "mtj-task")),
        status=status,
        issue_number=issue_number,
        objective=_as_str_list(data.get("objective")),
        allow_paths=allow,
        deny_paths=deny,
        prohibited=_as_str_list(data.get("prohibited")),
        stop=_as_str_list(data.get("stop")),
        delivery=delivery,
        next_authorized=next_auth,
        mutating=mutating,
        raw=data,
    )


# --------------------------------------------------------------------------
# mtj-result/1
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Result:
    schema: str
    task: str
    status: str
    base_expected: str = ""
    base_measured: str = ""
    branch: str = ""
    pr: int | None = None
    mutations: list[str] = dataclasses.field(default_factory=list)
    validation: list[str] = dataclasses.field(default_factory=list)
    discrepancies: list[str] = dataclasses.field(default_factory=list)
    decision_required: list[str] = dataclasses.field(default_factory=list)
    next_authorized: str = "NONE"
    raw: dict = dataclasses.field(default_factory=dict, repr=False)

    @property
    def base_matches(self) -> bool:
        return bool(self.base_expected) and self.base_expected == self.base_measured

    @property
    def needs_captain(self) -> bool:
        return bool(self.decision_required)


def parse_result(markdown_or_yaml: str) -> Result:
    data = _parse_body(markdown_or_yaml, "mtj-result")
    schema = str(_require(data, "schema", "mtj-result"))
    if not schema.startswith("mtj-result/"):
        raise ProtocolError(f"mtj-result: wrong schema '{schema}'")
    status = _enum(_require(data, "status", "mtj-result"), RESULT_STATUSES, "mtj-result", "status")
    pr = data.get("pr") or data.get("pr_number")
    nxt = data.get("next")
    next_auth = "NONE"
    if isinstance(nxt, dict):
        next_auth = str(nxt.get("authorized", "NONE") or "NONE")
    elif nxt is not None:
        next_auth = str(nxt)
    decision = data.get("decision_required")
    if isinstance(decision, str) and decision.strip().upper() in ("NONE", "NO", "NULL"):
        decision = None
    return Result(
        schema=schema,
        task=str(_require(data, "task", "mtj-result")),
        status=status,
        base_expected=str(data.get("base_expected", "") or ""),
        base_measured=str(data.get("base_measured", "") or ""),
        branch=str(data.get("branch", "") or ""),
        pr=int(pr) if isinstance(pr, int) or (isinstance(pr, str) and pr.isdigit()) else None,
        mutations=_as_str_list(data.get("mutations"), drop_sentinels=True),
        validation=_as_str_list(data.get("validation")),
        discrepancies=_as_str_list(data.get("discrepancies"), drop_sentinels=True),
        decision_required=_as_str_list(decision, drop_sentinels=True),
        next_authorized=next_auth,
        raw=data,
    )


# --------------------------------------------------------------------------
# mtj-review/1
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Review:
    schema: str
    task: str
    verdict: str
    reasons: list[str] = dataclasses.field(default_factory=list)
    findings: list[str] = dataclasses.field(default_factory=list)
    captain_question: list[str] = dataclasses.field(default_factory=list)
    next_task_id: str = ""
    raw: dict = dataclasses.field(default_factory=dict, repr=False)

    @property
    def halts_automation(self) -> bool:
        return self.verdict in ("CAPTAIN_DECISION_REQUIRED", "STOP")


def parse_review(markdown_or_yaml: str) -> Review:
    data = _parse_body(markdown_or_yaml, "mtj-review")
    schema = str(_require(data, "schema", "mtj-review"))
    if not schema.startswith("mtj-review/"):
        raise ProtocolError(f"mtj-review: wrong schema '{schema}'")
    verdict = _enum(_require(data, "verdict", "mtj-review"), VERDICTS, "mtj-review", "verdict")
    nxt = data.get("next_task")
    next_id = ""
    if isinstance(nxt, dict):
        next_id = str(nxt.get("id", "") or "")
    elif nxt:
        next_id = str(nxt)
    return Review(
        schema=schema,
        task=str(_require(data, "task", "mtj-review")),
        verdict=verdict,
        reasons=_as_str_list(data.get("reasons")),
        findings=_as_str_list(data.get("findings"), drop_sentinels=True),
        captain_question=_as_str_list(data.get("captain_question"), drop_sentinels=True),
        next_task_id=next_id,
        raw=data,
    )


# --------------------------------------------------------------------------
# mtj-claim/1  (durable execution lock)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Claim:
    schema: str
    task: str
    worker_id: str
    issue: int
    claimed_at: str
    lease_seconds: int = 3600
    raw: dict = dataclasses.field(default_factory=dict, repr=False)

    def is_expired(self, now: _dt.datetime | None = None) -> bool:
        now = now or _dt.datetime.now(_dt.timezone.utc)
        try:
            started = _dt.datetime.fromisoformat(self.claimed_at.replace("Z", "+00:00"))
        except ValueError:
            return True
        if started.tzinfo is None:
            started = started.replace(tzinfo=_dt.timezone.utc)
        return (now - started).total_seconds() > self.lease_seconds


def parse_claim(markdown_or_yaml: str) -> Claim:
    data = _parse_body(markdown_or_yaml, "mtj-claim")
    schema = str(_require(data, "schema", "mtj-claim"))
    if not schema.startswith("mtj-claim/"):
        raise ProtocolError(f"mtj-claim: wrong schema '{schema}'")
    lease = data.get("lease_seconds", 3600)
    return Claim(
        schema=schema,
        task=str(_require(data, "task", "mtj-claim")),
        worker_id=str(_require(data, "worker_id", "mtj-claim")),
        issue=int(_require(data, "issue", "mtj-claim")),
        claimed_at=str(_require(data, "claimed_at", "mtj-claim")),
        lease_seconds=int(lease) if str(lease).isdigit() else 3600,
        raw=data,
    )


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------


def render_block(payload: dict, note: str = "") -> str:
    """Render a protocol payload as a fenced yaml block, optionally with prose after it."""
    body = yamlite.emit(payload)
    text = f"```yaml\n{body}```"
    if note:
        text = f"{text}\n\n{note.strip()}\n"
    return text
