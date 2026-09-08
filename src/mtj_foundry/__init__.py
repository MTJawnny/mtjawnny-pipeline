"""mtj_foundry — the refounded Foundry namespace.

Ratified by Captain on 2026-08-29 (issue #1, `mtj-captain-decision/1`,
`A.python_namespace: mtj_foundry`).

This package is DELIBERATELY TINY. P0.2 correction C2 found that mandatory
re-export through `__init__.py` is not an API-enforcement mechanism — `__all__`
controls wildcard export, not importability — and that re-export-heavy package
inits recreate the import cycles the refoundation exists to remove. Public
surface therefore belongs in named facade modules, not here.

P0.3A created it with NO BEHAVIOR. It now carries permanent capabilities and,
since Path E milestone 1, one installed read-only command. It still moves no
legacy module, changes no legacy behavior and decides nothing semantic.

`__version__` is the ONE value duplicated between this file and `pyproject.toml`,
and it is duplicated because there is no third place for it to live: the metadata
is what an installer reads, and this is what code reads without importing the
installed distribution. A committed guard asserts the two agree, so the pair
cannot drift silently.
"""

from __future__ import annotations

__all__ = ["__version__"]

__version__ = "0.1.0"
