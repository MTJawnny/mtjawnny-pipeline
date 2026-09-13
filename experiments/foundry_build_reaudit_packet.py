#!/usr/bin/env python3
"""Retired historical re-audit packet generator.

The completed packet and this generator's original implementation are preserved
under archive/routing. The direct docs packet path is now an inert compatibility
stub, so regenerating the historical body there would resurrect obsolete
present-tense routing and external-audit instructions.

This tombstone intentionally refuses execution. It preserves a callable
``build`` name only so an accidental importer fails loudly at the retired
boundary instead of getting an AttributeError that hides why the capability is
gone.
"""
from __future__ import annotations

import sys


_MESSAGE = (
    "HALT: the B-consolidation re-audit packet generator is retired. "
    "The historical generator is preserved at "
    "archive/routing/experiments/foundry_build_reaudit_packet.py and the "
    "historical packet at archive/routing/docs/B-CONSOLIDATION-REAUDIT-PACKET.md. "
    "Do not regenerate the completed packet into docs/."
)


def build(*args, **kwargs):
    """Refuse historical packet regeneration from library callers."""
    raise RuntimeError(_MESSAGE)


def main() -> int:
    print(_MESSAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
