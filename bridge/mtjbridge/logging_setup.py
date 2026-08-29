"""Structured JSON logging with secret redaction applied at the handler."""

from __future__ import annotations

import json
import logging
import os
import sys
import time

from .redact import redact

_CONFIGURED = False
_RESERVED = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__) | {"message", "asctime"}


class RedactingJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return redact(json.dumps(payload, default=str, sort_keys=False))


def configure(level: str | None = None, stream=None) -> None:
    global _CONFIGURED
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(RedactingJsonFormatter())
    root = logging.getLogger("mtjbridge")
    root.handlers[:] = [handler]
    root.setLevel((level or os.environ.get("MTJ_LOG_LEVEL", "INFO")).upper())
    root.propagate = False
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    if not _CONFIGURED:
        configure()
    return logging.getLogger(name if name.startswith("mtjbridge") else f"mtjbridge.{name}")
