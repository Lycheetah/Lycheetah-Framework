"""Canonical encoding and digests for Sync Zone cycle records. Standard library only.

A digest identifies bytes. It does not authenticate who produced them and it does not
show that what they describe is true.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from typing import Any


def canonical_json(value: Any) -> str:
    """Compact JSON with sorted keys. NaN and infinity are refused."""
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_digest(value: Any) -> str:
    return sha256_hex(canonical_json(value).encode("utf-8"))


def candidate_digest(artifacts: Iterable[Mapping[str, Any]]) -> str:
    """Digest of a candidate's artifact list: path plus content hash, order-independent.

    A deleted artifact is recorded with ``sha256: None`` so a deletion changes the
    digest exactly as an edit does.
    """
    rows = sorted((str(a["path"]), a.get("sha256")) for a in artifacts)
    return json_digest([{"path": p, "sha256": h} for p, h in rows])


def failure_digest(failure: Mapping[str, Any]) -> str:
    """Digest of the parts of a failure record that may never be rewritten."""
    return json_digest({"id": failure.get("id"), "text": failure.get("text")})
