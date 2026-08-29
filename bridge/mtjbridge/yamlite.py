"""Strict YAML-subset parser/emitter for mtj-bridge protocol blocks.

Deliberately NOT a general YAML implementation. It supports exactly the
constructs the mtj-* protocol blocks use and HALTS LOUDLY on anything else,
so an unsupported construct becomes a visible error instead of a silently
dropped field.

House rule this follows: never best-guess a data shape. Every unrecognised
line raises YamlLiteError naming the line number and the exact problem.

Supported:
  * block mappings, arbitrarily nested (indent by 2+ spaces, consistent)
  * block sequences of scalars, of mappings, and of nested collections
  * plain, single-quoted and double-quoted scalars
  * block scalars: | |- |+ > >- >+
  * comments (# at start of line, or preceded by whitespace outside quotes)
  * null/~/empty, true/false, ints, floats
  * document start marker (---)

Not supported (raises): flow collections ({}, []), anchors/aliases/tags,
multiple documents, complex keys, tabs for indentation.
"""

from __future__ import annotations

from typing import Any

__all__ = ["YamlLiteError", "parse", "emit", "parse_first_block", "find_blocks"]


class YamlLiteError(ValueError):
    """Raised on any construct this parser refuses to guess at."""

    def __init__(self, message: str, line_no: int | None = None, line: str | None = None):
        self.line_no = line_no
        self.line = line
        if line_no is not None:
            message = f"line {line_no}: {message}"
            if line is not None:
                message = f"{message}\n  >> {line.rstrip()}"
        super().__init__(message)


# --------------------------------------------------------------------------
# scalar handling
# --------------------------------------------------------------------------

_BOOL_TRUE = {"true", "True", "TRUE", "yes", "Yes", "YES", "on", "On", "ON"}
_BOOL_FALSE = {"false", "False", "FALSE", "no", "No", "NO", "off", "Off", "OFF"}
_NULLS = {"", "~", "null", "Null", "NULL"}


def _strip_comment(text: str) -> str:
    """Remove a trailing comment that sits outside any quoted span."""
    out = []
    quote = None
    i = 0
    while i < len(text):
        ch = text[i]
        if quote:
            out.append(ch)
            if ch == "\\" and quote == '"' and i + 1 < len(text):
                out.append(text[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            out.append(ch)
        elif ch == "#" and (not out or out[-1] in " \t"):
            break
        else:
            out.append(ch)
        i += 1
    return "".join(out).rstrip()


def _unescape_double(raw: str, line_no: int, line: str) -> str:
    out = []
    i = 0
    simple = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\", "/": "/", "0": "\0"}
    while i < len(raw):
        ch = raw[i]
        if ch != "\\":
            out.append(ch)
            i += 1
            continue
        if i + 1 >= len(raw):
            raise YamlLiteError("dangling backslash in double-quoted scalar", line_no, line)
        nxt = raw[i + 1]
        if nxt in simple:
            out.append(simple[nxt])
            i += 2
        elif nxt == "u":
            if i + 6 > len(raw):
                raise YamlLiteError("truncated \\u escape", line_no, line)
            out.append(chr(int(raw[i + 2 : i + 6], 16)))
            i += 6
        else:
            raise YamlLiteError(f"unsupported escape '\\{nxt}'", line_no, line)
    return "".join(out)


def _scalar(text: str, line_no: int, line: str) -> Any:
    text = text.strip()
    if text in ("[]", "{}"):
        # Empty flow collections are accepted because models and hand-authors both
        # write them constantly. NON-empty flow style is still refused below.
        return [] if text == "[]" else {}
    if text.startswith(("{", "[")):
        raise YamlLiteError(
            "non-empty flow collections are not supported by yamlite; use block style",
            line_no, line
        )
    if text.startswith(("&", "*", "!")):
        raise YamlLiteError("anchors, aliases and tags are not supported", line_no, line)
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        return _unescape_double(text[1:-1], line_no, line)
    if len(text) >= 2 and text[0] == "'" and text[-1] == "'":
        return text[1:-1].replace("''", "'")
    if text in _NULLS:
        return None
    if text in _BOOL_TRUE:
        return True
    if text in _BOOL_FALSE:
        return False
    if text.lstrip("+-").isdigit():
        # Only accept an int when it round-trips exactly. '0000...0' (a 40-zero SHA)
        # and '007' must stay strings: coercing them silently destroys an identifier.
        value = int(text)
        if str(value) == text:
            return value
        return text
    try:
        return float(text)
    except ValueError:
        pass
    return text


# --------------------------------------------------------------------------
# line model
# --------------------------------------------------------------------------


class _Line:
    __slots__ = ("no", "raw", "indent", "text")

    def __init__(self, no: int, raw: str):
        self.no = no
        self.raw = raw
        stripped = raw.lstrip(" ")
        self.indent = len(raw) - len(stripped)
        self.text = stripped

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"_Line({self.no}, indent={self.indent}, {self.text!r})"


def _lines(source: str) -> list[_Line]:
    out: list[_Line] = []
    for i, raw in enumerate(source.splitlines(), start=1):
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise YamlLiteError("tab used for indentation", i, raw)
        line = _Line(i, raw.rstrip("\r"))
        if not line.text or line.text.startswith("#"):
            continue
        if line.text == "---":
            continue
        if line.text == "...":
            continue
        out.append(line)
    return out


def _split_key(text: str, line_no: int, raw: str) -> tuple[str, str] | None:
    """Split 'key: value' outside quotes. Returns None when not a mapping line."""
    quote = None
    i = 0
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == "\\" and quote == '"':
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == ":" and (i + 1 == len(text) or text[i + 1] in " \t"):
            key_raw = text[:i].strip()
            if not key_raw:
                raise YamlLiteError("empty mapping key", line_no, raw)
            if key_raw.startswith("?"):
                raise YamlLiteError("complex mapping keys are not supported", line_no, raw)
            key = _scalar(key_raw, line_no, raw)
            return str(key), text[i + 1 :].strip()
        i += 1
    return None


# --------------------------------------------------------------------------
# block scalars
# --------------------------------------------------------------------------


def _block_scalar(header: str, lines: list[_Line], idx: int, parent_indent: int,
                  line_no: int, raw: str) -> tuple[str, int]:
    style = header[0]
    rest = header[1:]
    chomp = ""
    explicit_indent = None
    for ch in rest:
        if ch in "+-":
            if chomp:
                raise YamlLiteError("duplicate chomping indicator", line_no, raw)
            chomp = ch
        elif ch.isdigit():
            explicit_indent = int(ch)
        else:
            raise YamlLiteError(f"bad block scalar header '{header}'", line_no, raw)

    # Collect raw physical lines (blank lines included) belonging to the block.
    body: list[str] = []
    src_idx = idx
    while src_idx < len(lines):
        ln = lines[src_idx]
        if ln.indent <= parent_indent:
            break
        body.append(ln)
        src_idx += 1

    if not body:
        return ("" if chomp == "-" else ""), idx

    indent = explicit_indent + parent_indent if explicit_indent else min(l.indent for l in body)
    texts = [l.raw[indent:] if len(l.raw) > indent else "" for l in body]

    if style == "|":
        text = "\n".join(texts)
        if chomp != "-":
            text += "\n"
        if chomp != "+":
            text = text.rstrip("\n") + ("\n" if chomp == "" else "")
    else:  # folded
        parts: list[str] = []
        for t in texts:
            if not t.strip():
                parts.append("\n")
            elif parts and parts[-1] not in ("\n",) and not t.startswith(" "):
                parts.append(" " + t)
            else:
                parts.append(t)
        text = "".join(parts).strip("\n" if chomp == "-" else "")
        text = text.replace("\n ", "\n")
        if chomp == "":
            text = text.rstrip("\n") + "\n"
        elif chomp == "-":
            text = text.rstrip("\n")
    return text, src_idx


# --------------------------------------------------------------------------
# recursive-descent block parser
# --------------------------------------------------------------------------


def _parse_block(lines: list[_Line], idx: int, indent: int) -> tuple[Any, int]:
    if idx >= len(lines):
        return None, idx
    first = lines[idx]
    if first.text.startswith("- "):
        return _parse_sequence(lines, idx, indent)
    if first.text == "-":
        return _parse_sequence(lines, idx, indent)
    return _parse_mapping(lines, idx, indent)


def _parse_mapping(lines: list[_Line], idx: int, indent: int) -> tuple[dict, int]:
    out: dict[str, Any] = {}
    while idx < len(lines):
        ln = lines[idx]
        if ln.indent < indent:
            break
        if ln.indent > indent:
            raise YamlLiteError(
                f"unexpected indent {ln.indent} inside mapping at indent {indent}", ln.no, ln.raw
            )
        if ln.text.startswith("- "):
            break
        split = _split_key(_strip_comment(ln.text), ln.no, ln.raw)
        if split is None:
            raise YamlLiteError(
                "expected 'key: value' inside a mapping (multi-line plain scalars "
                "are not supported; quote the value or use a block scalar)",
                ln.no,
                ln.raw,
            )
        key, value_text = split
        if key in out:
            raise YamlLiteError(f"duplicate mapping key '{key}'", ln.no, ln.raw)
        idx += 1
        if value_text.startswith(("|", ">")):
            out[key], idx = _block_scalar(value_text, lines, idx, ln.indent, ln.no, ln.raw)
        elif value_text == "":
            if idx < len(lines) and lines[idx].indent > ln.indent:
                out[key], idx = _parse_block(lines, idx, lines[idx].indent)
            elif idx < len(lines) and lines[idx].indent == ln.indent and lines[idx].text.startswith("- "):
                out[key], idx = _parse_sequence(lines, idx, ln.indent)
            else:
                out[key] = None
        else:
            out[key] = _scalar(value_text, ln.no, ln.raw)
    return out, idx


def _parse_sequence(lines: list[_Line], idx: int, indent: int) -> tuple[list, int]:
    out: list[Any] = []
    while idx < len(lines):
        ln = lines[idx]
        if ln.indent < indent:
            break
        if ln.indent > indent:
            raise YamlLiteError(
                f"unexpected indent {ln.indent} inside sequence at indent {indent}", ln.no, ln.raw
            )
        if not (ln.text == "-" or ln.text.startswith("- ")):
            break
        item_text = ln.text[1:].strip()
        item_col = ln.indent + 2
        idx += 1
        if item_text == "":
            if idx < len(lines) and lines[idx].indent > ln.indent:
                value, idx = _parse_block(lines, idx, lines[idx].indent)
            else:
                value = None
            out.append(value)
            continue
        if item_text.startswith(("|", ">")):
            value, idx = _block_scalar(item_text, lines, idx, ln.indent, ln.no, ln.raw)
            out.append(value)
            continue
        split = _split_key(_strip_comment(item_text), ln.no, ln.raw)
        if split is None:
            out.append(_scalar(_strip_comment(item_text), ln.no, ln.raw))
            continue
        # sequence item that is itself a mapping: re-parse from a synthetic view
        synth = [_Line(ln.no, " " * item_col + _strip_comment(item_text))]
        while idx < len(lines) and lines[idx].indent >= item_col:
            synth.append(lines[idx])
            idx += 1
        value, consumed = _parse_mapping(synth, 0, item_col)
        if consumed != len(synth):
            bad = synth[consumed]
            raise YamlLiteError("could not parse sequence item mapping", bad.no, bad.raw)
        out.append(value)
    return out, idx


def parse(source: str) -> Any:
    """Parse a YAML-subset document. Raises YamlLiteError on anything unsupported."""
    lines = _lines(source)
    if not lines:
        return None
    base = lines[0].indent
    value, idx = _parse_block(lines, 0, base)
    if idx != len(lines):
        bad = lines[idx]
        raise YamlLiteError("trailing content could not be parsed", bad.no, bad.raw)
    return value


# --------------------------------------------------------------------------
# emitter
# --------------------------------------------------------------------------

_PLAIN_SAFE_FIRST = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/._")


def _needs_quotes(text: str) -> bool:
    if text == "":
        return True
    if text[0] not in _PLAIN_SAFE_FIRST:
        return True
    if text != text.strip():
        return True
    if ": " in text or text.endswith(":"):
        return True
    if " #" in text:
        return True
    if "\n" in text or "\t" in text:
        return True
    if text in _BOOL_TRUE or text in _BOOL_FALSE or text in _NULLS:
        return True
    try:
        float(text)
        return True
    except ValueError:
        return False


def _emit_scalar(value: Any) -> str:
    if value == [] and isinstance(value, list):
        return "[]"
    if value == {} and isinstance(value, dict):
        return "{}"
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return repr(value)
    text = str(value)
    if _needs_quotes(text):
        escaped = (
            text.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\t", "\\t")
        )
        return f'"{escaped}"'
    return text


def emit(value: Any, indent: int = 0) -> str:
    """Serialise to the same subset. Deterministic: dict insertion order preserved."""
    pad = " " * indent
    if isinstance(value, dict):
        if not value:
            return f"{pad}{{}}\n"
        chunks = []
        for key, val in value.items():
            key_text = _emit_scalar(str(key))
            if isinstance(val, (dict, list)) and val:
                chunks.append(f"{pad}{key_text}:\n{emit(val, indent + 2)}")
            elif isinstance(val, (dict, list)):
                chunks.append(f"{pad}{key_text}: {'{}' if isinstance(val, dict) else '[]'}\n")
            else:
                chunks.append(f"{pad}{key_text}: {_emit_scalar(val)}\n")
        return "".join(chunks)
    if isinstance(value, list):
        if not value:
            return f"{pad}[]\n"
        chunks = []
        for item in value:
            if isinstance(item, (dict, list)) and item:
                body = emit(item, indent + 2)
                chunks.append(f"{pad}-{body[indent + 1 :]}")
            else:
                chunks.append(f"{pad}- {_emit_scalar(item)}\n")
        return "".join(chunks)
    return f"{pad}{_emit_scalar(value)}\n"


# --------------------------------------------------------------------------
# fenced-block extraction
# --------------------------------------------------------------------------


def find_blocks(markdown: str, language: str = "yaml") -> list[str]:
    """Return the bodies of every ```<language> fenced block, in order."""
    blocks: list[str] = []
    current: list[str] | None = None
    for line in markdown.splitlines():
        stripped = line.strip()
        if current is None:
            if stripped.startswith("```") and stripped[3:].strip().lower() in (
                language,
                f"{language}\n",
            ):
                current = []
            continue
        if stripped.startswith("```"):
            blocks.append("\n".join(current))
            current = None
            continue
        current.append(line)
    return blocks


def parse_first_block(markdown: str, language: str = "yaml") -> Any:
    """Parse the first fenced block; fall back to the whole text when unfenced."""
    blocks = find_blocks(markdown, language)
    if blocks:
        return parse(blocks[0])
    return parse(markdown)
