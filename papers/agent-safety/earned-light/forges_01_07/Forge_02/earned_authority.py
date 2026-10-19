"""Earned Authority Chain (EAC) v0.2 -- isolated research prototype.

Adds externally verifiable authority and field-level provenance preconditions to
an existing action/permit gateway. Not an execution sandbox, identity provider,
or production-ready reference implementation.

Security boundary: approval signing keys and provenance attester keys live in
trusted services OUTSIDE the agent. No agent-generated labels are trusted.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any, Mapping, Sequence
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

SCHEMA = "lycheetah.eac.v0.2"


def canonical(value: Any) -> bytes:
    """Strict canonical encoding within the explicitly restricted JSON domain.

    This is NOT RFC 8785. It forbids floats and nonstring dict keys to avoid
    cross-language numeric/serialization ambiguities. No custom objects.
    """
    def validate(v: Any) -> None:
        if v is None or type(v) in (str, int, bool):
            return
        if isinstance(v, list):
            for sub in v:
                validate(sub)
            return
        if isinstance(v, dict):
            if any(type(k) is not str for k in v):
                raise ValueError("NON_STRING_KEY")
            for sub in v.values():
                validate(sub)
            return
        raise ValueError("UNSUPPORTED_CANONICAL_TYPE")
    validate(value)
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


@dataclass(frozen=True)
class Grant:
    """Signed by a trusted approval/authentication service (not by the agent)."""
    schema: str
    issuer: str
    grant_id: str
    principal: str
    agent_id: str
    session_id: str
    tool: str
    operation: str
    scope: str
    state_version: str
    issued_at: int
    expires_at: int
    signature: str

    def payload(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("signature")
        return d


@dataclass(frozen=True)
class OriginProof:
    """Signed by a trusted data-ingress adapter (not by the agent)."""
    schema: str
    attester: str
    grant_id: str
    session_id: str
    field: str
    value_digest: str
    origin_kind: str
    origin_reference: str
    issued_at: int
    expires_at: int
    signature: str

    def payload(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("signature")
        return d


@dataclass(frozen=True)
class Request:
    agent_id: str
    session_id: str
    tool: str
    operation: str
    scope: str
    state_version: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class Decision:
    allowed: bool
    code: str
    grant_id: str | None
    request_digest: str
    proof_digests: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ActionPolicy:
    required_fields: tuple[str, ...]
    allowed_fields: tuple[str, ...]
    controlled_fields: tuple[str, ...]
    acceptable_origins: frozenset[str]


# Operator-owned policy. Treat all effectful destinations as controlled,
# including optional cc and bcc. Bodies can contain untrusted quoted material;
# this does not mean instructions in those bodies gain write authority.
POLICIES: Mapping[tuple[str, str], ActionPolicy] = {
    ("mail", "send"): ActionPolicy(
        required_fields=("recipient", "subject", "body"),
        allowed_fields=("recipient", "cc", "bcc", "subject", "body"),
        controlled_fields=("recipient", "cc", "bcc"),
        acceptable_origins=frozenset(("authenticated_human_input", "trusted_crm")),
    ),
    ("calendar", "create"): ActionPolicy(
        required_fields=("title", "start", "attendees"),
        allowed_fields=("title", "start", "attendees", "description"),
        controlled_fields=("attendees",),
        acceptable_origins=frozenset(("authenticated_human_input", "trusted_contacts")),
    ),
}


def _valid_signature(pub: Ed25519PublicKey | None, payload: dict[str, Any], sig: str) -> bool:
    if pub is None or type(sig) is not str:
        return False
    try:
        if len(sig) != 128:
            return False
        pub.verify(bytes.fromhex(sig), canonical(payload))
        return True
    except (ValueError, InvalidSignature):
        return False


class EarnedAuthorityGate:
    def __init__(
        self,
        approval_keys: Mapping[str, Ed25519PublicKey],
        attester_keys: Mapping[str, Ed25519PublicKey],
        *,
        revoked: set[str] | None = None,
        policies: Mapping[tuple[str, str], ActionPolicy] = POLICIES,
        clock_skew_seconds: int = 0,
    ) -> None:
        self.approval_keys = dict(approval_keys)
        self.attester_keys = dict(attester_keys)
        self.revoked = revoked if revoked is not None else set()
        self.policies = dict(policies)
        if clock_skew_seconds < 0:
            raise ValueError("negative clock skew")
        self.clock_skew_seconds = clock_skew_seconds

    def _decision(self, r: Request, g: Grant | None, allowed: bool, code: str,
                  proofs: Sequence[OriginProof] = ()) -> Decision:
        return Decision(
            allowed=allowed,
            code=code,
            grant_id=g.grant_id if isinstance(g, Grant) else None,
            request_digest=digest(asdict(r)),
            proof_digests=tuple(digest(p.payload()) for p in proofs),
        )

    def check_grant(self, r: Request, g: Grant | None, *, now: int) -> Decision:
        """Conventional cryptographic scoped grant; does NOT check origin proofs."""
        if not isinstance(g, Grant):
            return self._decision(r, None, False, "GRANT_MISSING")
        if g.schema != SCHEMA or not _valid_signature(
            self.approval_keys.get(g.issuer), g.payload(), g.signature
        ):
            return self._decision(r, g, False, "GRANT_UNTRUSTED")
        if g.grant_id in self.revoked:
            return self._decision(r, g, False, "GRANT_REVOKED")
        if g.issued_at > now + self.clock_skew_seconds or now >= g.expires_at:
            return self._decision(r, g, False, "GRANT_NOT_CURRENT")
        if not g.principal or not g.grant_id:
            return self._decision(r, g, False, "GRANT_MALFORMED")
        for f in ("agent_id", "session_id", "tool", "operation", "scope", "state_version"):
            if getattr(g, f) != getattr(r, f):
                return self._decision(r, g, False, "GRANT_BINDING_MISMATCH")
        return self._decision(r, g, True, "GRANT_VALID")

    def evaluate(self, r: Request, g: Grant | None,
                 proofs: Sequence[OriginProof], *, now: int) -> Decision:
        """Fail closed on unknown actions, untracked fields, or missing trusted provenance."""
        try:
            canonical(asdict(r))
        except ValueError:
            return Decision(False, "NON_CANONICAL_REQUEST", None, "unhashable")
        policy = self.policies.get((r.tool, r.operation))
        if policy is None:
            return self._decision(r, g, False, "OPERATION_NOT_POLICY_CONTROLLED")
        if not isinstance(r.arguments, dict):
            return self._decision(r, g, False, "INVALID_ARGUMENTS")
        keys = set(r.arguments)
        if not set(policy.required_fields).issubset(keys):
            return self._decision(r, g, False, "REQUIRED_FIELD_MISSING")
        if keys - set(policy.allowed_fields):
            return self._decision(r, g, False, "UNRECOGNIZED_EFFECT_FIELD")
        gd = self.check_grant(r, g, now=now)
        if not gd.allowed:
            return gd
        assert g is not None
        controlled_present = set(policy.controlled_fields).intersection(keys)
        per_field: dict[str, OriginProof] = {}
        for proof in proofs:
            if not isinstance(proof, OriginProof):
                return self._decision(r, g, False, "MALFORMED_PROOF")
            if proof.field not in controlled_present or proof.field in per_field:
                return self._decision(r, g, False, "EXTRA_OR_DUPLICATE_PROOF")
            per_field[proof.field] = proof
        if set(per_field) != controlled_present:
            return self._decision(r, g, False, "FIELD_PROOF_MISSING")
        for f in sorted(controlled_present):
            p = per_field[f]
            if p.schema != SCHEMA or not _valid_signature(
                self.attester_keys.get(p.attester), p.payload(), p.signature
            ):
                return self._decision(r, g, False, "ORIGIN_UNTRUSTED")
            if p.grant_id != g.grant_id or p.session_id != r.session_id:
                return self._decision(r, g, False, "ORIGIN_CONTEXT_MISMATCH")
            if p.issued_at > now + self.clock_skew_seconds or now >= p.expires_at:
                return self._decision(r, g, False, "ORIGIN_NOT_CURRENT")
            if p.value_digest != digest(r.arguments[f]):
                return self._decision(r, g, False, "ORIGIN_VALUE_MISMATCH")
            if not p.origin_reference or p.origin_kind not in policy.acceptable_origins:
                return self._decision(r, g, False, "ORIGIN_DISALLOWED")
        return self._decision(r, g, True, "EAC_ALLOW", [per_field[f] for f in sorted(per_field)])
