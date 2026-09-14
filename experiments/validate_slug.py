#!/usr/bin/env python3
"""Slug validator -- docs/CODEBOOK-NAMING-GRAMMAR.md sec.10 ("Lane-1 lint,
wire into emit + SUP"). Implements the six pseudo-spec checks:
  1. charset            2. banned tokens         3. closed vocabulary
  4. slot order          5. synonym collision      6. restriction/counter/cost laws

This module never mutates the codebook and never auto-fixes a failure --
"Validator failures are never auto-fixed; they surface for ruling" (sec.10).
validate_slug() is a pure function returning a result dict; main() runs it
in batch over codebook.json for reporting (used by the combined per-axis
walk, CORPUS-PASS-PLAN.md step 3).

Usage:
  python3 experiments/validate_slug.py rule:some-proposed-slug
  python3 experiments/validate_slug.py --batch   # validates every active
                                                  # codebook.json slug
"""
import sys
import re
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402

CODEBOOK_PATH = fc.FOUNDRY_OUT_DIR / "codebook.json"


# ---------------------------------------------------------------------------
# S11: THE SLUG SEMANTICS NOW LIVE IN `mtj_foundry.codebook_slug`
# ---------------------------------------------------------------------------
# The six grammar checks, every ratified vocabulary (byte-for-byte, provenance
# comments included), the Q8.5 restriction PARSE with its content guards, the
# live-axis cross-check, the keyword-vocabulary derivation and the D-2/D-3
# collision normalization moved to the permanent owner. NO SECOND
# IMPLEMENTATION REMAINS HERE.
#
# What stays is what a library may not own: WHERE the grammar document, the
# codebook and `keyword-buckets.json` live, whether they exist, reading them at
# import in the SAME order as before, the `--batch` report and the CLI, and the
# historic `STOP — …` process contract around each refusal.
#
# The module-level names are the owner's OBJECTS, so every reader that reaches
# `validate_slug.<VOCAB>` sees the one definition. `CLOSED_VOCAB` is composed
# here, from the two loaded parts, and `validate_slug()` reads it at CALL time.
from mtj_foundry import codebook_slug as _slug  # noqa: E402

CHARSET_RE = _slug.CHARSET_RE
BANNED_LITERAL_TOKENS = _slug.BANNED_LITERAL_TOKENS
DELIVERY_VOCAB = _slug.DELIVERY_VOCAB
EFFECT_VOCAB = _slug.EFFECT_VOCAB
OBJECT_VOCAB = _slug.OBJECT_VOCAB
SCOPE_VOCAB = _slug.SCOPE_VOCAB
SCALING_STAT_VOCAB = _slug.SCALING_STAT_VOCAB
COUNTER_TOKEN_VOCAB = _slug.COUNTER_TOKEN_VOCAB
QUALIFIER_VOCAB = _slug.QUALIFIER_VOCAB
RESTRICTION_VOCAB = _slug.RESTRICTION_VOCAB
EXEMPT_LEAF_SLUGS = _slug.EXEMPT_LEAF_SLUGS
GLOSSARY_VOCAB = _slug.GLOSSARY_VOCAB
WALK_RATIFICATION_VOCAB_20260731 = _slug.WALK_RATIFICATION_VOCAB_20260731
CANT_BE_BLOCKED_STEM_VOCAB = _slug.CANT_BE_BLOCKED_STEM_VOCAB
_RESTRICTION_ANCHOR = _slug._RESTRICTION_ANCHOR


def _load_q85_restriction_vocab() -> set:
    """Tokens of grammar §13 Q8.5's closed restriction vocabulary.

    HALTS rather than returning a short set. The parse and its content guards
    are `codebook_slug.parse_q85_restriction_vocab`; the file is this boundary's.
    """
    path = fc.REPO_ROOT / "docs" / "CODEBOOK-NAMING-GRAMMAR.md"
    if not path.exists():
        fc.halt(f"{path} not found — Q8.5's closed restriction vocabulary is "
                f"parsed from it and cannot be recovered from anywhere else.")
    text = path.read_text(encoding="utf-8")
    try:
        return _slug.parse_q85_restriction_vocab(text)
    except _slug.SlugVocabularyError as error:
        fc.halt(str(error))


def _q85_covers_live_axes(tokens: set) -> None:
    """The live-axis cross-check (`codebook_slug.q85_live_axis_violation`) over
    this boundary's codebook -- silently skipped when there is none to read."""
    try:
        codebook = json.loads(CODEBOOK_PATH.read_text())
    except (OSError, ValueError):
        return                              # standalone use; nothing to check
    violation = _slug.q85_live_axis_violation(tokens, codebook)
    if violation:
        fc.halt(violation)


Q85_RESTRICTION_VOCAB = _load_q85_restriction_vocab()
_q85_covers_live_axes(Q85_RESTRICTION_VOCAB)

SOFT_WARNING_TOKENS = _slug.SOFT_WARNING_TOKENS


def _load_keyword_vocab() -> set:
    """The keyword-grant vocabulary from keyword-buckets.json, or EMPTY when that
    file has not been generated (keeps this module standalone)."""
    path = fc.FOUNDRY_OUT_DIR / "keyword-buckets.json"
    if not path.exists():
        return set()
    data = json.loads(path.read_text())
    return _slug.keyword_vocab_from_buckets(data)


KEYWORD_VOCAB = _load_keyword_vocab()

CLOSED_VOCAB = _slug.compose_closed_vocab(Q85_RESTRICTION_VOCAB, KEYWORD_VOCAB)

ACTIVATION_RESTRICTION_FAMILY = _slug.ACTIVATION_RESTRICTION_FAMILY
SCALES_WITH_RE = _slug.SCALES_WITH_RE
SCALES_PREFIX_RE = _slug.SCALES_PREFIX_RE
normalize_for_collision = _slug.normalize_for_collision
find_collisions = _slug.find_collisions


def validate_slug(slug: str, definition: str = None, all_slugs: list = None) -> dict:
    """slug must include the 'rule:' prefix. Returns
    {"slug", "ok", "failures": [...], "warnings": [...], "unknown_tokens": [...]}.

    S11 COMPATIBILITY FACADE for `codebook_slug.validate_slug`, handing it this
    module's `CLOSED_VOCAB` as it stands at call time."""
    return _slug.validate_slug(slug, definition, all_slugs, closed_vocab=CLOSED_VOCAB)


# S13: the CLI -- per-slug JSON, `--batch` summary and report, usage -- is
# `mtj_foundry.slug_report`'s. This boundary supplies the codebook read, the
# report location and writer, the usage text, and the process exit.
from mtj_foundry import slug_report as _report  # noqa: E402


def _context():
    return _report.SlugReportContext(
        usage=__doc__,
        read_codebook=lambda: json.loads(CODEBOOK_PATH.read_text()),
        validate_slug=lambda *a, **k: validate_slug(*a, **k),
        report_path=fc.FOUNDRY_OUT_DIR / "validate_slug_report.json",
        write_json=lambda path, data: fc.write_json(path, data),
    )


def main():
    code = _report.run(sys.argv[1:], _context())
    if code:
        sys.exit(code)


if __name__ == "__main__":
    main()
