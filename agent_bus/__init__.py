"""Agent Bus v1 -- the typed Manager/Worker transport layer.

This package is CONTROL PLANE, not Foundry semantics. It carries no card data,
no scoring constant and no codebook content, and it is stdlib-only for the same
reason the Foundry package is: a control plane that cannot start because a
dependency is missing is not a control plane.

Authority is NOT here. GitHub Issue #1 (`latest K -> active T`) remains the only
selector. This package transports typed messages and refuses to let a newer
message become law -- see `agent_bus.machine`.
"""

from __future__ import annotations

__all__ = ["SCHEMA", "VERSION"]

SCHEMA = "mtj-agent-bus/1"
VERSION = 1
