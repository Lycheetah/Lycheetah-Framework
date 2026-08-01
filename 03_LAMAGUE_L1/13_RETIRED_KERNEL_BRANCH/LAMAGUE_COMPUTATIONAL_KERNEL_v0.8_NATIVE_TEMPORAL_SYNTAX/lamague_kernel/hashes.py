from __future__ import annotations
import dataclasses, hashlib, json
from enum import Enum

def normalise(value):
    if dataclasses.is_dataclass(value):
        value = dataclasses.asdict(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(k): normalise(v) for k, v in sorted(value.items(), key=lambda x: str(x[0]))}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [normalise(v) for v in value]
    return value

def canonical_json(value):
    return json.dumps(normalise(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def semantic_hash(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
