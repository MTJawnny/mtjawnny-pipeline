"""Deterministic failure vocabulary for the Agent Bus.

Every rejection in this package is one `BusError` carrying one stable `code`.
The codes are the contract: a Manager, a Worker, a workflow and a test all read
the same string for the same rejection, and the human-readable detail never
carries decision weight.

The governing repository principle applies unchanged here. A hard failure must
never quietly become a success, so nothing in this package returns a usable
message on a rejected input -- it raises, and the caller records the code.
"""

from __future__ import annotations

# --- transport / envelope extraction -----------------------------------------
AMBIGUOUS_ENVELOPE = "BUS_AMBIGUOUS_ENVELOPE"
MALFORMED_JSON = "BUS_MALFORMED_JSON"
DUPLICATE_JSON_KEY = "BUS_DUPLICATE_JSON_KEY"
NOT_AN_OBJECT = "BUS_NOT_AN_OBJECT"

# --- envelope shape -----------------------------------------------------------
MISSING_FIELD = "BUS_MISSING_FIELD"
UNKNOWN_FIELD = "BUS_UNKNOWN_FIELD"
BAD_TYPE = "BUS_BAD_TYPE"
BAD_VALUE = "BUS_BAD_VALUE"
SCHEMA_UNSUPPORTED = "BUS_SCHEMA_UNSUPPORTED"
ACTOR_UNKNOWN = "BUS_ACTOR_UNKNOWN"
KIND_UNKNOWN = "BUS_KIND_UNKNOWN"
ACTOR_KIND_MISMATCH = "BUS_ACTOR_KIND_MISMATCH"

# --- correlation / freshness ---------------------------------------------------
DUPLICATE_MESSAGE_ID = "BUS_DUPLICATE_MESSAGE_ID"
UNKNOWN_PARENT = "BUS_UNKNOWN_PARENT"
PARENT_KIND_MISMATCH = "BUS_PARENT_KIND_MISMATCH"
PARENT_WAVE_MISMATCH = "BUS_PARENT_WAVE_MISMATCH"
PARENT_REQUIRED = "BUS_PARENT_REQUIRED"
STALE_AUTHORITY = "BUS_STALE_AUTHORITY"
STALE_BASE = "BUS_STALE_BASE"
WAVE_NOT_SELECTED = "BUS_WAVE_NOT_SELECTED"
WAVE_ALREADY_COMMANDED = "BUS_WAVE_ALREADY_COMMANDED"

# --- authority separation -------------------------------------------------------
UNAUTHORIZED_ACCEPTED_HEAD = "BUS_UNAUTHORIZED_ACCEPTED_HEAD"
UNTRUSTED_AUTHOR = "BUS_UNTRUSTED_AUTHOR"

# --- wave plan -------------------------------------------------------------------
DUPLICATE_UNIT_ID = "BUS_DUPLICATE_UNIT_ID"
UNKNOWN_DEPENDENCY = "BUS_UNKNOWN_DEPENDENCY"
DEPENDENCY_CYCLE = "BUS_DEPENDENCY_CYCLE"
UNIT_SCOPE_MISSING = "BUS_UNIT_SCOPE_MISSING"
UNIT_VALIDATION_MISSING = "BUS_UNIT_VALIDATION_MISSING"
EMPTY_WAVE = "BUS_EMPTY_WAVE"

# --- speaker trust (fail closed) ---------------------------------------------------
TRUST_NOT_CONFIGURED = "BUS_TRUST_NOT_CONFIGURED"

# --- checkout preflight -------------------------------------------------------------
WRONG_WORKTREE = "BUS_WRONG_WORKTREE"
WRONG_BRANCH = "BUS_WRONG_BRANCH"
BASE_NOT_ANCESTOR = "BUS_BASE_NOT_ANCESTOR"
PROGRESS_HEAD_MISMATCH = "BUS_PROGRESS_HEAD_MISMATCH"
UNEXPECTED_DIRT = "BUS_UNEXPECTED_DIRT"
PREFLIGHT_FAILED = "BUS_PREFLIGHT_FAILED"

# --- unit boundary enforcement --------------------------------------------------------
UNIT_NO_COMMIT = "BUS_UNIT_NO_COMMIT"
UNIT_TRAILER_MISSING = "BUS_UNIT_TRAILER_MISSING"
UNIT_SCOPE_ESCAPE = "BUS_UNIT_SCOPE_ESCAPE"
UNIT_UNCOMMITTED = "BUS_UNIT_UNCOMMITTED"
READONLY_UNIT_MUTATED = "BUS_READONLY_UNIT_MUTATED"

# --- running an external command ----------------------------------------------------------
# A launch failure is a FAILURE, not a crash. These codes exist so a long-running
# watcher can back off from one instead of dying and being restarted forever.
EXECUTABLE_NOT_FOUND = "BUS_EXECUTABLE_NOT_FOUND"
COMMAND_TIMEOUT = "BUS_COMMAND_TIMEOUT"
GIT_FAILED = "BUS_GIT_FAILED"
AUTHORITY_UNRESOLVED = "BUS_AUTHORITY_UNRESOLVED"

# --- watcher ----------------------------------------------------------------------------
WATCHER_ALREADY_RUNNING = "BUS_WATCHER_ALREADY_RUNNING"
WATCHER_NOT_INSTALLED = "BUS_WATCHER_NOT_INSTALLED"

# --- dispatch ---------------------------------------------------------------------
ALREADY_CLAIMED = "BUS_ALREADY_CLAIMED"
NOTHING_ACTIONABLE = "BUS_NOTHING_ACTIONABLE"
TRANSPORT_FAILED = "BUS_TRANSPORT_FAILED"

# --- Manager wake pre-gate ------------------------------------------------------------
# Every one of these ends a GitHub event BEFORE any model is invoked.
GATE_WRONG_EVENT = "BUS_GATE_WRONG_EVENT"
GATE_WRONG_SURFACE = "BUS_GATE_WRONG_SURFACE"
GATE_NO_ENVELOPE = "BUS_GATE_NO_ENVELOPE"
GATE_NOT_FOR_MANAGER = "BUS_GATE_NOT_FOR_MANAGER"
GATE_COMMENT_MISMATCH = "BUS_GATE_COMMENT_MISMATCH"
GATE_ALREADY_HANDLED = "BUS_GATE_ALREADY_HANDLED"

CODES = frozenset(
    v for k, v in list(globals().items())
    if k.isupper() and isinstance(v, str) and v.startswith("BUS_")
)


class BusError(Exception):
    """One rejection, one stable code.

    `str(err)` is `"<CODE>: <detail>"` and is deliberately stable: tests and the
    Manager both read it, so a reworded detail is a protocol change, not a
    cosmetic one.
    """

    def __init__(self, code: str, detail: str) -> None:
        if code not in CODES:
            raise AssertionError(f"undeclared bus error code: {code!r}")
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
