"""The model's whole voice: one typed decision, bounded, and nothing else.

R3 asked the model for finished authority records -- a WAVE_REVIEW body and the
V and K texts -- and checked them by substring. That made the model the author of
the checkpoint. Here the model answers ONE question with a verdict and a little
bounded prose; every record is then built by `agent_bus.transition` from live,
independently read state. The model never names a head, a checkpoint, a task, a
selector or a successor, because there is no field to put one in.

The bounded prose is still text the model controls, and it is copied into the
ledger. So it is held to a narrow alphabet: one line per item, printable, and
free of anything that could be mistaken for a record -- a fence, a bus or ledger
schema name, or a `schema:` key. Text that looks like authority is refused, not
escaped: the model has no reason to write it.

`python3 -m agent_bus.decision --schema` prints the JSON Schema handed to the
model runner, derived from the same constants the parser enforces.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from typing import Any

from agent_bus import errors as E
from agent_bus.errors import BusError

VERDICTS = ("ACCEPT", "REPAIR", "CAPTAIN")
KEYS = ("verdict", "reason", "findings", "evidence")
MAX_REASON = 600
MAX_ITEM = 300
MAX_ITEMS = 12

_PRINTABLE = re.compile(r"^[\x20-\x7e]+$")
# Anything that could be read as a record, or break out of one.
_FORBIDDEN = re.compile(r"`|mtj-bus|mtj-checkpoint|mtj-verdict|mtj-task|mtj-result|schema\s*:",
                        re.IGNORECASE)


@dataclass(frozen=True)
class Decision:
    verdict: str
    reason: str
    findings: tuple[str, ...]
    evidence: tuple[str, ...]

    def as_dict(self) -> dict:
        return {"verdict": self.verdict, "reason": self.reason,
                "findings": list(self.findings), "evidence": list(self.evidence)}


def _refuse(detail: str) -> BusError:
    return BusError(E.DECISION_INVALID, detail)


def _no_duplicates(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise _refuse(f"key {key!r} appears twice")
        out[key] = value
    return out


def _text(value: Any, where: str, limit: int) -> str:
    if not isinstance(value, str):
        raise _refuse(f"{where} must be a string")
    if not value.strip() or len(value) > limit:
        raise _refuse(f"{where} must be 1..{limit} characters")
    if not _PRINTABLE.match(value):
        raise _refuse(f"{where} must be one printable ASCII line")
    if _FORBIDDEN.search(value):
        raise _refuse(f"{where} carries record-shaped text")
    return value


def _items(value: Any, where: str) -> tuple[str, ...]:
    if not isinstance(value, list) or len(value) > MAX_ITEMS:
        raise _refuse(f"{where} must be a list of at most {MAX_ITEMS} strings")
    return tuple(_text(v, f"{where}[{i}]", MAX_ITEM) for i, v in enumerate(value))


def from_mapping(raw: Any) -> Decision:
    if not isinstance(raw, dict):
        raise _refuse("the decision must be a JSON object")
    if set(raw) != set(KEYS):
        raise _refuse(f"the decision must have exactly {list(KEYS)}; got {sorted(raw)}")
    verdict = raw["verdict"]
    if verdict not in VERDICTS:
        raise _refuse(f"verdict {verdict!r} not in {list(VERDICTS)}")
    return Decision(verdict=verdict, reason=_text(raw["reason"], "reason", MAX_REASON),
                    findings=_items(raw["findings"], "findings"),
                    evidence=_items(raw["evidence"], "evidence"))


def parse(text: str) -> Decision:
    """Exactly one decision object, or `BUS_DECISION_INVALID`."""
    if not isinstance(text, str) or not text.strip():
        raise _refuse("the model returned nothing")
    try:
        raw = json.loads(text, object_pairs_hook=_no_duplicates)
    except json.JSONDecodeError as exc:
        raise _refuse(f"not JSON: {exc.msg}")
    return from_mapping(raw)


def json_schema() -> dict:
    """The output schema for the model runner. Same limits as `parse`."""
    item = {"type": "string", "minLength": 1, "maxLength": MAX_ITEM}
    return {
        "type": "object",
        "additionalProperties": False,
        "required": list(KEYS),
        "properties": {
            "verdict": {"type": "string", "enum": list(VERDICTS)},
            "reason": {"type": "string", "minLength": 1, "maxLength": MAX_REASON},
            "findings": {"type": "array", "maxItems": MAX_ITEMS, "items": item},
            "evidence": {"type": "array", "maxItems": MAX_ITEMS, "items": item},
        },
    }


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv != ["--schema"]:
        print("usage: python3 -m agent_bus.decision --schema", file=sys.stderr)
        return 2
    print(json.dumps(json_schema(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - module entry point
    raise SystemExit(main())
