"""Lycheetah Compaction Shield & Semantic Codec.

Provable context compaction preserving negative constraints, unknown dependencies,
authorities, dissents, and rollback anchors across agent sessions.
"""

from __future__ import annotations

from .codec import (
    CODEBOOK_SCHEMA,
    CRITICAL_FIELDS,
    REQUIRED_FIELDS,
    SCHEMA,
    VALID_OPS,
    VALID_RISKS,
    CodecError,
    build_codebook,
    canonical_bytes,
    canonical_json,
    classify,
    critical_hash,
    critical_projection,
    decode,
    encode,
    full_hash,
    safety_violations,
    sha256_json,
    validate_codebook,
    validate_packet,
)
from .shield import (
    AgentStatePacket,
    CompactionShield,
    ContextProtector,
)

__all__ = [
    "CODEBOOK_SCHEMA",
    "CRITICAL_FIELDS",
    "REQUIRED_FIELDS",
    "SCHEMA",
    "VALID_OPS",
    "VALID_RISKS",
    "AgentStatePacket",
    "CodecError",
    "CompactionShield",
    "ContextProtector",
    "build_codebook",
    "canonical_bytes",
    "canonical_json",
    "classify",
    "critical_hash",
    "critical_projection",
    "decode",
    "encode",
    "full_hash",
    "safety_violations",
    "sha256_json",
    "validate_codebook",
    "validate_packet",
]
