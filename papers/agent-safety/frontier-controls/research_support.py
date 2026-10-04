"""New public integration adapter, 2026-10-04; not recovered original code.

Only an exact synthetic Action value/hash contract is reconstructed here.
This supplies no authorization, broker, witness or production-security mechanism.
"""
from dataclasses import asdict, dataclass
import hashlib
import json

@dataclass(frozen=True)
class Action:
    principal: str
    tool: str
    operation: str
    object_id: str
    destination: str
    arguments: dict
    effect_id: str

    @property
    def action_hash(self):
        body = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"), allow_nan=False)
        return hashlib.sha256(body.encode()).hexdigest()
