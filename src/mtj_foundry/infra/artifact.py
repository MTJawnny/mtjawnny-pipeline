"""The ONE owner of generated-artifact byte format.

## Why this module exists

`write_json` was defined in `experiments/foundry_common.py`, the legacy
compatibility boundary, and forty-three legacy tools call it. Its byte format is
therefore a real contract with every tracked artifact those tools have written,
and it was owned by a module the refoundation is dissolving.

S5 promotes the FORMAT, not a redesign. The policy below is the legacy policy,
character for character:

    indent=2 · ensure_ascii=False · UTF-8 · exactly one trailing LF

`ensure_ascii=False` is the load-bearing one. Flipping it changes no JSON
VALUE — the documents stay equivalent and stay deterministic — while rewriting
every non-ASCII byte in the corpus's own vocabulary (`Juzám`, `Urza’s`, the CR's
curly apostrophe) into `\\uXXXX` escapes. A determinism check cannot see that,
because deterministically wrong is still deterministic; only a comparison
against the contracted BYTES can. That is what the S5 negative control aims at.

## What this module is NOT

It owns a byte format and nothing else: no path discovery, no repository
layout, no semantic knowledge, no CLI. The caller passes the destination.
"""

from __future__ import annotations

import json
from pathlib import Path

__all__ = ["write_json"]


def write_json(path: Path, data) -> None:
    """Write `data` as JSON at `path`, in the ratified byte format.

    Creates missing parents. Byte-identical to the legacy
    `foundry_common.write_json` this replaces — that equality is asserted over
    fixtures, not assumed.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
