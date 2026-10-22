"""Lycheetah Compaction Shield & Semantic Codec.

Hash-checked context compaction. A reference packet declares negative constraints,
unknown dependencies, authorities, dissent and rollback anchors; the shield reports
when a candidate drops, weakens or alters them. It cannot tell whether a declaration
is true or complete, and risk, evidence, horizon and yield sit outside the hash.
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
