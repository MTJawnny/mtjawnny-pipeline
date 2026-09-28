"""Bounded final Worker output. Evidence only: never a bus command or acceptance."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from agent_bus import errors as E
from agent_bus.errors import BusError
from agent_bus.shell import Completed

# UTF-8 bytes, including the serialized wrapper. Safely below GitHub's comment
# limit even with JSON escaping; required evidence is never silently truncated.
MAX_EVIDENCE_BYTES = 24000
MAX_COMMENT_BYTES = 60000
PREFIX = 'Worker evidence/result — non-authoritative; not Manager acceptance.\n\n```json\n'
SUFFIX = '\n```\n'


def _pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f'duplicate JSON key: {key}')
        obj[key] = value
    return obj


def _json(text):
    return json.loads(text, object_pairs_hook=_pairs)


def _refuse(detail):
    raise BusError(E.WORKER_EVIDENCE_INVALID, detail)


def _bounded(text):
    if not isinstance(text, str) or not text.strip():
        _refuse('missing final substantive Worker response')
    if text.strip().lower() in {'claude done', 'done', 'ok'}:
        _refuse('final Worker response is only an acknowledgement, not substantive evidence')
    try:
        size = len(text.encode('utf-8'))
    except UnicodeError:
        _refuse('final Worker response is not valid UTF-8')
    if size > MAX_EVIDENCE_BYTES:
        _refuse(f'Worker evidence exceeds {MAX_EVIDENCE_BYTES} UTF-8 bytes; not truncated')
    return text


# Every headless final response ends with this fenced JSON footer (Captain
# decision D, Issue #1 comment 5864993788). Prose above it is free; the footer is
# what the host checks. An acknowledgement, however it is punctuated or dressed
# up, has no footer and is refused.
FOOTER_FENCE = 'mtj-evidence'
FOOTER_STATUSES = ('DONE', 'STOP')
_FOOTER_KEYS = {'status', 'changed', 'validation'}


@dataclass(frozen=True)
class Footer:
    status: str
    changed: tuple[str, ...]
    validation: tuple[tuple[str, int], ...]


def footer_block(status: str, changed=(), validation=()) -> str:
    """The canonical footer text, for the brief and for tests."""
    body = {'status': status, 'changed': sorted(changed),
            'validation': [{'command': c, 'exit': e} for c, e in validation]}
    return f'```{FOOTER_FENCE}\n' + json.dumps(body, sort_keys=True) + '\n```'


def footer(text: str) -> Footer:
    """Parse the required trailing footer, or refuse. Nothing is guessed."""
    body = _bounded(text).rstrip()
    opener = f'```{FOOTER_FENCE}\n'
    start = body.rfind(opener)
    if body.count('```' + FOOTER_FENCE) > 1:
        _refuse(f'final Worker response has more than one ```{FOOTER_FENCE} footer')
    if start < 0 or not body.endswith('\n```'):
        _refuse(f'final Worker response does not end with a ```{FOOTER_FENCE} footer '
                '(status, changed, validation)')
    raw = body[start + len(opener):-len('\n```')]
    try:
        data = _json(raw)
    except (ValueError, TypeError) as exc:
        _refuse(f'evidence footer is not one JSON object: {exc}')
    if not isinstance(data, dict) or set(data) != _FOOTER_KEYS:
        _refuse(f'evidence footer must have exactly the keys {sorted(_FOOTER_KEYS)}')
    status, changed, validation = data['status'], data['changed'], data['validation']
    if status not in FOOTER_STATUSES:
        _refuse(f'evidence footer status must be one of {FOOTER_STATUSES}, not {status!r}')
    if (not isinstance(changed, list) or not all(isinstance(p, str) and p for p in changed)
            or len(set(changed)) != len(changed)):
        _refuse('evidence footer `changed` must be a list of distinct non-empty paths')
    if not isinstance(validation, list):
        _refuse('evidence footer `validation` must be a list')
    rows = []
    for row in validation:
        if (not isinstance(row, dict) or set(row) != {'command', 'exit'}
                or not isinstance(row['command'], str) or not row['command'].strip()
                or type(row['exit']) is not int):
            _refuse('each evidence footer validation row must be {"command": str, "exit": int}')
        rows.append((row['command'], row['exit']))
    if status == 'DONE' and not rows:
        _refuse('a DONE evidence footer must name the validation that ran')
    return Footer(status, tuple(sorted(changed)), tuple(rows))


def extract(provider: str, result: Completed | None) -> str:
    """Return the exact final text, or refuse. No prose fallback or tool output.

    Claude has one JSON result. Codex has one completed turn with a terminal
    item.completed agent_message; earlier agent messages are commentary. Explicit
    final_answer phases, when present, must agree with that terminal message.
    Duplicate keys, duplicate final ids, multiple turns and error events fail
    closed rather than guessing which result the supervisor should publish.
    """
    if result is None or result.returncode != 0:
        _refuse('no successful provider result available')
    try:
        if provider == 'claude':
            payload = _json(result.stdout)
            if (not isinstance(payload, dict) or payload.get('type') != 'result'
                    or payload.get('subtype') != 'success'
                    or payload.get('is_error') is not False):
                _refuse('Claude output is not one successful JSON result')
            return _bounded(payload.get('result'))
        if provider != 'codex':
            _refuse(f'unsupported Worker evidence provider: {provider}')
        events = [_json(line) for line in result.stdout.splitlines() if line.strip()]
        if not events or not all(isinstance(e, dict) for e in events):
            _refuse('Codex output is not JSONL objects')
        turns = [i for i, e in enumerate(events) if e.get('type') == 'turn.completed']
        if len(turns) != 1 or turns[0] != len(events) - 1:
            _refuse('Codex output needs exactly one terminal completed turn')
        if any(e.get('type') in {'error', 'turn.failed'} for e in events):
            _refuse('Codex output contains an error event')
        items = [e.get('item') for e in events if e.get('type') == 'item.completed']
        if not items or not all(isinstance(item, dict) for item in items):
            _refuse('Codex output has no unambiguous completed final item')
        final = items[-1]
        if final.get('type') != 'agent_message' or final.get('phase') not in (None, 'final_answer'):
            _refuse('Codex final completed item is not a final agent message')
        finals = [item for item in items if item.get('phase') == 'final_answer']
        if finals and (len(finals) != 1 or finals[0] is not final):
            _refuse('Codex output contains ambiguous final agent messages')
        ids = [item.get('id') for item in items]
        if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
            _refuse('Codex completed item ids are missing or ambiguous')
        return _bounded(final.get('text'))
    except (ValueError, TypeError) as exc:
        _refuse(f'{provider} final evidence is malformed JSON: {exc}')


def failure_detail(provider: str, result: Completed) -> str:
    """Diagnostic text only. This is deliberately not capacity classification."""
    detail = result.stderr.strip()
    if provider == 'claude':
        try:
            payload = _json(result.stdout)
        except (ValueError, TypeError):
            payload = None
        if isinstance(payload, dict) and payload.get('type') == 'result' and payload.get('is_error') is True:
            fields = {k: payload[k] for k in ('subtype', 'result', 'errors', 'api_error_status')
                      if k in payload}
            detail = 'stdout result error: ' + json.dumps(fields, ensure_ascii=True) + ('; stderr: ' + detail if detail else '')
    return detail[:1000]


def render(command, unit: str, head: str, provider: str, text: str,
           problems=None) -> str:
    """The durable evidence comment. `problems` (a failed unit's codes) marks it
    as the evidence of a unit that did NOT complete; it can never satisfy resume."""
    text = _bounded(text)
    payload = {
        'schema': 'mtj-worker-evidence/1', 'actor': 'WORKER',
        'authority': False, 'manager_acceptance': False,
        'command': command.message_id, 'wave': command.wave,
        'selection': dict(command.authority), 'base': command.base,
        'unit': unit, 'head': head, 'provider': provider,
        'sha256': hashlib.sha256(text.encode('utf-8')).hexdigest(),
        'response': text,
    }
    if problems is not None:
        payload['outcome'] = 'F'
        payload['problems'] = [[code, detail] for code, detail in problems]
    # Keep response newlines escaped inside a JSON string. Even a quoted K or
    # mtj-bus fence in model output cannot become a top-level authority/message.
    body = PREFIX + json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + SUFFIX
    if len(body.encode('utf-8')) > MAX_COMMENT_BYTES:
        _refuse(f'encoded Worker evidence exceeds {MAX_COMMENT_BYTES} bytes; not truncated')
    return body
