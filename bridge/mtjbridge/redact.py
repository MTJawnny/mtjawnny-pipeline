"""Secret redaction for every log line and every string leaving the process.

Applied at the logging boundary AND before any text is posted to GitHub, so a
credential cannot escape through a captured subprocess stream, a model prompt
echo, or a result body.
"""

from __future__ import annotations

import os
import re

REDACTED = "[REDACTED]"

# Token shapes that are recognisable on their own.
_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"gh[pousr]_[A-Za-z0-9]{16,}"),          # GitHub classic/OAuth tokens
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),        # GitHub fine-grained PAT
    re.compile(r"sk-[A-Za-z0-9_\-]{16,}"),              # OpenAI-style keys
    re.compile(r"sk-ant-[A-Za-z0-9_\-]{16,}"),          # Anthropic keys
    re.compile(r"AKIA[0-9A-Z]{16}"),                    # AWS access key id
    re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{16,}"),     # Authorization headers
    re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}"),     # Slack
    re.compile(r"-----BEGIN[ A-Z]*PRIVATE KEY-----.*?-----END[ A-Z]*PRIVATE KEY-----", re.S),
)

# Environment variables whose *values* must never appear in output, whatever
# shape they have.
SECRET_ENV_NAMES: tuple[str, ...] = (
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GH_TOKEN",
    "GITHUB_TOKEN",
    "AZURE_OPENAI_API_KEY",
    "CLAUDE_CODE_OAUTH_TOKEN",
)

_MIN_ENV_VALUE_LEN = 8


def _env_values(environ: dict[str, str] | None = None) -> list[str]:
    env = os.environ if environ is None else environ
    out = []
    for name in SECRET_ENV_NAMES:
        value = env.get(name)
        if value and len(value) >= _MIN_ENV_VALUE_LEN:
            out.append(value)
    return out


def redact(text: str, environ: dict[str, str] | None = None) -> str:
    """Return text with every recognised secret replaced by [REDACTED].

    Idempotent: redacting already-redacted text changes nothing.
    """
    if not text:
        return text
    for value in _env_values(environ):
        text = text.replace(value, REDACTED)
    for pattern in _PATTERNS:
        text = pattern.sub(REDACTED, text)
    return text


def redact_env_for_subprocess(environ: dict[str, str] | None = None) -> dict[str, str]:
    """A copy of the environment safe to hand to a *model* subprocess.

    The model adapter gets the credentials it needs from its own auth path
    (Claude keychain / OpenAI SDK env), never from a value the bridge prints.
    This helper strips the OpenAI key from the Claude subprocess environment and
    vice versa, so neither model process can read the other's credential.
    """
    env = dict(os.environ if environ is None else environ)
    return env


def assert_clean(text: str, environ: dict[str, str] | None = None) -> str:
    """Halt loudly if a known secret value survived into text."""
    for value in _env_values(environ):
        if value in text:
            raise RuntimeError(
                "refusing to emit text containing a secret environment value; "
                "redaction did not run on this path"
            )
    return text
