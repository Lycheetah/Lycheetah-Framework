"""Deterministic JSON and privacy helpers for Assurance Receipts."""

from __future__ import annotations

import hashlib
import json
import math
from enum import Enum
from typing import Any, Mapping, Sequence


class CanonicalJSONError(ValueError):
    """Raised when a value cannot be represented by lycheetah-json-v1."""


def jsonable(value: Any) -> Any:
    """Return a defensive, JSON-safe copy or fail visibly.

    The accepted type surface is intentionally small. Silent ``default=str``
    coercion would make hashes depend on arbitrary object representations.
    """

    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise CanonicalJSONError("NaN and infinity are not valid receipt values")
        return value
    if isinstance(value, Enum):
        return jsonable(value.value)
    if isinstance(value, Mapping):
        out = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise CanonicalJSONError("receipt object keys must be strings")
            out[key] = jsonable(item)
        return out
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [jsonable(item) for item in value]
    raise CanonicalJSONError(f"unsupported receipt value: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    """Encode a value using the documented ``lycheetah-json-v1`` profile."""

    return json.dumps(
        jsonable(value),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sensitive_key(key: str, configured: Sequence[str]) -> bool:
    normalized = key.lower().replace("-", "_").replace(" ", "_")
    tokens = (
        token.lower().replace("-", "_").replace(" ", "_")
        for token in configured
    )
    return any(token in normalized for token in tokens)


def redact(value: Any, configured_keys: Sequence[str]) -> tuple[Any, bool]:
    """Recursively redact values under sensitive-looking keys.

    Returns ``(redacted_value, changed)`` so callers can state whether captured
    material is sufficient for exact replay.
    """

    if isinstance(value, Mapping):
        out = {}
        changed = False
        for key, item in value.items():
            if not isinstance(key, str):
                raise CanonicalJSONError("tool argument keys must be strings")
            if sensitive_key(key, configured_keys):
                out[key] = "[REDACTED]"
                changed = True
            else:
                out[key], child_changed = redact(item, configured_keys)
                changed = changed or child_changed
        return out, changed
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        out = []
        changed = False
        for item in value:
            redacted, child_changed = redact(item, configured_keys)
            out.append(redacted)
            changed = changed or child_changed
        return out, changed
    return jsonable(value), False
