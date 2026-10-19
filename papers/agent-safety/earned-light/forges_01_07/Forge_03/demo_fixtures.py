"""TEST-ONLY approval and attestation issuers; never import into production agent."""
from dataclasses import replace
from typing import Any
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from earned_authority import SCHEMA, Grant, OriginProof, Request, canonical, digest


def grant_for(key: Ed25519PrivateKey, r: Request, *, issued: int = 100,
              expires: int = 500, grant_id: str = "grant-001", issuer: str = "auth-service") -> Grant:
    g = Grant(SCHEMA, issuer, grant_id, "human-42", r.agent_id, r.session_id,
              r.tool, r.operation, r.scope, r.state_version, issued, expires, "")
    return replace(g, signature=key.sign(canonical(g.payload())).hex())


def origin_for(key: Ed25519PrivateKey, r: Request, g: Grant, field: str,
               *, kind: str = "authenticated_human_input", issued: int = 100,
               expires: int = 500, reference: str = "trusted-ui/event-001",
               attester: str = "trusted-ingress") -> OriginProof:
    p = OriginProof(SCHEMA, attester, g.grant_id, r.session_id, field,
                    digest(r.arguments[field]), kind, reference, issued, expires, "")
    return replace(p, signature=key.sign(canonical(p.payload())).hex())


def default_request() -> Request:
    return Request("agent-a", "session-a", "mail", "send", "customer-updates",
                   "state-7", {"recipient": "customer@example.test", "subject": "Update", "body": "Your order is ready."})
