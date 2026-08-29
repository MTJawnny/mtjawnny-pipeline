"""mtj_foundry — the refounded Foundry namespace.

Ratified by Captain on 2026-08-29 (issue #1, `mtj-captain-decision/1`,
`A.python_namespace: mtj_foundry`).

This package is DELIBERATELY TINY. P0.2 correction C2 found that mandatory
re-export through `__init__.py` is not an API-enforcement mechanism — `__all__`
controls wildcard export, not importability — and that re-export-heavy package
inits recreate the import cycles the refoundation exists to remove. Public
surface therefore belongs in named facade modules, not here.

As of P0.3A this package has NO BEHAVIOR. It moves no legacy module, changes no
legacy behavior, decides nothing semantic, and nothing in the legacy tree imports
it. It exists so later bounded phases have somewhere to land.
"""

from __future__ import annotations

__all__ = ["__version__"]

__version__ = "0.0.0"
