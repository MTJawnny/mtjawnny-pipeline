"""Shared helpers for the refoundation skeleton tests.

No third-party dependency is used anywhere in this tree. P0.3A's constraint is
`deps: do_not_migrate_or_pin_legacy_dependencies_yet`, so a test suite that
imported PyYAML to read its own artifacts would quietly pin one.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def scalars(text: str) -> dict[str, str]:
    """Extract `key: value` scalars from a YAML document at ANY indent.

    Deliberately dumb: this is a targeted reader for asserting recorded values,
    not a YAML parser, and it does not pretend to understand structure. Later
    keys win, so it is only used on documents where the asserted keys are unique.
    """
    out: dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(r"^\s*-?\s*([A-Za-z_][A-Za-z0-9_]*):\s*(.*?)\s*$", line)
        if m and m.group(2) and not m.group(2).startswith((">", "|", "#")):
            out[m.group(1)] = m.group(2).strip('"')
    return out


def block(text: str, key: str) -> str:
    """Return the indented body of a top-level `key:` block.

    Needed because `scalars()` lets a later duplicate key win, and the inventory
    deliberately repeats keys like `file_count` inside nested counter-examples.
    """
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith(f"{key}:"))
    out = []
    for line in lines[start + 1:]:
        if line and not line[0].isspace() and not line.startswith("#"):
            break
        out.append(line)
    return "\n".join(out)


def top_level_keys(text: str) -> list[str]:
    return [line.split(":", 1)[0] for line in text.splitlines()
            if line and line[0].isalpha() and ":" in line]
