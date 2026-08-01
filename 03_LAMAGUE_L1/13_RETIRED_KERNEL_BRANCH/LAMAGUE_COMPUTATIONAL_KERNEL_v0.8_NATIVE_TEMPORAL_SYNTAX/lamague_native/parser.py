from __future__ import annotations

import hashlib
import math
import re
import shlex
from typing import Any

from lamague_temporal.bridge import Observability
from .model import NativeProgram, SourceStatement


VERSION = "0.8.0"


class NativeSyntaxError(ValueError):
    pass


_ALLOWED = {
    "packet", "observability", "boundary", "recover",
    "observe", "declare", "calculate", "infer", "unknown",
    "conflict", "drift", "intent", "action", "invariant",
    "preserve", "block", "analyze",
}

_LEGACY_GLYPHS = {
    "∆": ("Δ", "LEGACY_GLYPH", "Use Greek capital delta U+0394."),
    "♾": ("∞", "LEGACY_GLYPH", "Use infinity U+221E."),
    "∮": ("⟲", "LEGACY_GLYPH", "Use recursion operator ⟲ U+27F2."),
}


def _source_hash(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def _strip_comments(source: str) -> str:
    out: list[str] = []
    in_quote = False
    escaped = False
    i = 0
    while i < len(source):
        ch = source[i]
        if escaped:
            out.append(ch)
            escaped = False
            i += 1
            continue
        if ch == "\\" and in_quote:
            out.append(ch)
            escaped = True
            i += 1
            continue
        if ch == '"':
            in_quote = not in_quote
            out.append(ch)
            i += 1
            continue
        if ch == "#" and not in_quote:
            while i < len(source) and source[i] != "\n":
                i += 1
            continue
        out.append(ch)
        i += 1
    if in_quote:
        raise NativeSyntaxError("unterminated quoted string")
    return "".join(out)


def _split_statements(source: str) -> list[str]:
    cleaned = _strip_comments(source)
    out: list[str] = []
    buf: list[str] = []
    in_quote = False
    escaped = False
    for ch in cleaned:
        if escaped:
            buf.append(ch)
            escaped = False
            continue
        if ch == "\\" and in_quote:
            buf.append(ch)
            escaped = True
            continue
        if ch == '"':
            in_quote = not in_quote
            buf.append(ch)
            continue
        if ch == ";" and not in_quote:
            text = "".join(buf).strip()
            if text:
                out.append(text)
            buf = []
        else:
            buf.append(ch)
    trailing = "".join(buf).strip()
    if trailing:
        raise NativeSyntaxError(f"missing semicolon after: {trailing[:80]}")
    return out


def _parse_scalar(text: str) -> Any:
    low = text.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if low in {"null", "none"}:
        return None
    if re.fullmatch(r"[+-]?\d+", text):
        return int(text)
    decimal = r"[+-]?(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?"
    scientific = r"[+-]?\d+[eE][+-]?\d+"
    if re.fullmatch(decimal, text) or re.fullmatch(scientific, text):
        value = float(text)
        if not math.isfinite(value):
            raise NativeSyntaxError("numbers must be finite")
        return value
    return text


def _parse_statement(raw: str, index: int) -> SourceStatement:
    try:
        tokens = shlex.split(raw, comments=False, posix=True)
    except ValueError as exc:
        raise NativeSyntaxError(f"statement {index}: {exc}") from exc
    if not tokens:
        raise NativeSyntaxError(f"statement {index}: empty statement")
    keyword = tokens[0].lower()
    if keyword not in _ALLOWED:
        raise NativeSyntaxError(
            f"statement {index}: unknown keyword {tokens[0]!r}"
        )
    positional: list[str] = []
    options: dict[str, Any] = {}
    for token in tokens[1:]:
        if "=" in token:
            key, value = token.split("=", 1)
            if not key:
                raise NativeSyntaxError(f"statement {index}: empty option name")
            if key in options:
                raise NativeSyntaxError(
                    f"statement {index}: duplicate option {key!r}"
                )
            options[key] = _parse_scalar(value)
        else:
            positional.append(token)
    return SourceStatement(keyword, tuple(positional), options, raw, index)


def parse_source(source: str) -> NativeProgram:
    statements = tuple(
        _parse_statement(raw, i + 1)
        for i, raw in enumerate(_split_statements(source))
    )
    packet_stmts = [s for s in statements if s.keyword == "packet"]
    obs_stmts = [s for s in statements if s.keyword == "observability"]
    if len(packet_stmts) != 1 or len(packet_stmts[0].positional) != 1:
        raise NativeSyntaxError(
            "exactly one `packet ID;` declaration is required"
        )
    if len(obs_stmts) != 1 or len(obs_stmts[0].positional) != 1:
        raise NativeSyntaxError(
            "exactly one `observability CLASS;` declaration is required"
        )
    packet_id = packet_stmts[0].positional[0]
    observability = obs_stmts[0].positional[0]
    try:
        Observability(observability)
    except ValueError as exc:
        raise NativeSyntaxError(
            f"invalid observability class {observability!r}"
        ) from exc

    warnings: list[dict[str, Any]] = []
    for raw, (canonical, code, message) in _LEGACY_GLYPHS.items():
        if raw in source:
            warnings.append({
                "code": code,
                "raw": raw,
                "canonical": canonical,
                "message": message,
            })
    if "↯" in source and "conflict" not in source.lower():
        warnings.append({
            "code": "AMBIGUOUS_LEGACY_JUNCTION",
            "raw": "↯",
            "canonical": "collapse",
            "message": (
                "↯ is canonically collapse in the computational line; "
                "it is not parsed as branching."
            ),
        })

    return NativeProgram(
        packet_id,
        observability,
        statements,
        _source_hash(source),
        tuple(warnings),
    )


def parse_file(path):
    from pathlib import Path
    return parse_source(Path(path).read_text(encoding="utf-8"))
