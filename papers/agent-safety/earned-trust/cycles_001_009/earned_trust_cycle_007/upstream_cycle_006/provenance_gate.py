"""Earned Trust Cycle 005 — provenance-aware agreement gate (synthetic reference).

A *trusted, preconfigured* source genealogy constrains claims of independence.
HMAC authenticates the lab signer's statement, not its truth or operational
independence. No live payment, network, or agent execution occurs.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
from typing import Mapping, Sequence


def canonical(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def object_sha(obj: object) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


@dataclass(frozen=True)
class Source:
    source_id: str
    controller: str
    upstream: tuple[str, ...] = ()
    # Anchors are root collection sources; witness signers are non-root nodes.
    witness_signer: bool = False


class RegistryError(ValueError):
    pass


class TrustedRegistry:
    """Administrative configuration, not discovered provenance or third-party audit."""
    def __init__(self, sources: Sequence[Source], keys: Mapping[str, bytes]):
        if not sources or len({x.source_id for x in sources}) != len(sources):
            raise RegistryError("source set must be nonempty with unique IDs")
        self.sources = {x.source_id: x for x in sources}
        self.keys = dict(keys)
        for source in sources:
            if not source.source_id or not source.controller:
                raise RegistryError("source and controller IDs required")
            if source.witness_signer and not source.upstream:
                raise RegistryError("signer must disclose a root lineage")
            if not source.witness_signer and source.upstream:
                # Intermediate nodes can be non-signers if they have upstream.
                pass
            if len(set(source.upstream)) != len(source.upstream):
                raise RegistryError("repeated upstream source")
            for p in source.upstream:
                if p not in self.sources:
                    raise RegistryError("unknown upstream source: " + p)
            if source.witness_signer and (source.source_id not in self.keys
                                           or not isinstance(self.keys[source.source_id], bytes)
                                           or len(self.keys[source.source_id]) < 32):
                raise RegistryError("signer has no adequate registered key")
        # Cycles make roots undefined. Walk the entire registry, not only signers.
        visiting, visited = set(), set()
        def visit(sid: str) -> None:
            if sid in visiting:
                raise RegistryError("provenance cycle detected")
            if sid in visited:
                return
            visiting.add(sid)
            for upstream in self.sources[sid].upstream:
                visit(upstream)
            visiting.remove(sid)
            visited.add(sid)
        for sid in self.sources:
            visit(sid)
        if set(self.keys) - {s.source_id for s in sources if s.witness_signer}:
            raise RegistryError("key for undeclared witness signer")

    def exposure(self, sid: str) -> tuple[frozenset[str], frozenset[str]]:
        """Root sources and *all* controllers on transitive provenance path."""
        if sid not in self.sources:
            raise RegistryError("unknown source")
        roots, controllers = set(), set()
        def walk(node: str):
            src = self.sources[node]
            controllers.add(src.controller)
            if not src.upstream:
                roots.add(node)
            else:
                for p in src.upstream:
                    walk(p)
        walk(sid)
        return frozenset(roots), frozenset(controllers)


FIELDS = frozenset(("schema", "source_id", "effect_id", "action_sha256", "token_sha256",
                    "status", "correctness", "observed_at", "revision"))


def sign_statement(registry: TrustedRegistry, sid: str, *, effect_id: str,
                   action_sha256: str, token_sha256: str, status: str = "COMMITTED",
                   correctness: str = "TRUE", observed_at: int = 100,
                   revision: int = 1) -> dict:
    """Fixture-only signed observation; no externally verified telemetry."""
    if sid not in registry.keys:
        raise RegistryError("no registered signing key")
    body = {"schema": "earned-trust.witness.v1", "source_id": sid, "effect_id": effect_id,
            "action_sha256": action_sha256, "token_sha256": token_sha256,
            "status": status, "correctness": correctness,
            "observed_at": observed_at, "revision": revision}
    mac = hmac.new(registry.keys[sid], canonical(body), hashlib.sha256).hexdigest()
    return {"body": body, "hmac_sha256": mac}


@dataclass(frozen=True)
class Verdict:
    decision: str
    reason: str
    authenticated_signers: int
    disjoint_witnesses: int
    evidence_signers: tuple[str, ...] = ()

    def as_dict(self) -> dict:
        return {"decision": self.decision, "reason": self.reason,
                "authenticated_signers": self.authenticated_signers,
                "disjoint_witnesses": self.disjoint_witnesses,
                "evidence_signers": list(self.evidence_signers)}


class ProvenanceGate:
    def __init__(self, registry: TrustedRegistry, *, min_independent: int = 2,
                 max_age: int = 30, max_future_skew: int = 0):
        if type(min_independent) is not int or min_independent < 2:
            raise ValueError("minimum needs at least two independent witnesses")
        if type(max_age) is not int or max_age < 0 or type(max_future_skew) is not int or max_future_skew < 0:
            raise ValueError("invalid time bounds")
        self.registry = registry
        self.min_independent, self.max_age, self.max_future_skew = min_independent, max_age, max_future_skew

    def verify_one(self, claim: object, *, effect_id: str, action_sha256: str,
                   token_sha256: str, now: int) -> tuple[bool, str]:
        if not isinstance(claim, dict) or set(claim) != {"body", "hmac_sha256"}:
            return False, "malformed-envelope"
        b, mac = claim["body"], claim["hmac_sha256"]
        if not isinstance(b, dict) or set(b) != FIELDS or not isinstance(mac, str):
            return False, "malformed-body"
        sid = b["source_id"]
        if not isinstance(sid, str) or sid not in self.registry.keys:
            return False, "unknown-signer"
        if any(type(b[k]) is not str for k in ("schema","effect_id","action_sha256","token_sha256","status","correctness")):
            return False, "invalid-field-type"
        if type(b["observed_at"]) is not int or type(b["revision"]) is not int or b["revision"] < 1:
            return False, "invalid-revision-or-time"
        if b["schema"] != "earned-trust.witness.v1":
            return False, "schema-mismatch"
        if b["status"] not in {"COMMITTED", "NOT_COMMITTED", "UNKNOWN"} or b["correctness"] not in {"TRUE", "FALSE", "UNKNOWN"}:
            return False, "invalid-assertion"
        if any(b[k] != exp for k,exp in (("effect_id",effect_id),("action_sha256",action_sha256),("token_sha256",token_sha256))):
            return False, "different-subject"
        if b["observed_at"] < now-self.max_age or b["observed_at"] > now+self.max_future_skew:
            return False, "stale-or-future"
        expected = hmac.new(self.registry.keys[sid], canonical(b), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, mac):
            return False, "invalid-authentication"
        return True, "ok"

    def evaluate(self, claims: Sequence[object], *, effect_id: str, action_sha256: str,
                 token_sha256: str, now: int, provider_receipt_valid: bool = True,
                 current_revisions: Mapping[str, int] | None = None) -> Verdict:
        """A confirm means independent *declared pathways*, never ground truth.

        provider_receipt_valid comes from the separate Cycle-004 verifier; this
        function does not independently verify that provider proof.
        """
        if type(now) is not int or not effect_id or not action_sha256 or not token_sha256:
            return Verdict("REVIEW", "invalid-request", 0, 0)
        if not provider_receipt_valid:
            return Verdict("REVIEW", "provider-proof-not-verified", 0, 0)
        if not isinstance(claims, (list, tuple)) or not claims or len(claims) > 32:
            return Verdict("REVIEW", "missing-or-too-many-witnesses", 0, 0)
        witnessed: dict[str, dict] = {}
        for claim in claims:
            valid, reason = self.verify_one(claim, effect_id=effect_id,
                                            action_sha256=action_sha256,
                                            token_sha256=token_sha256, now=now)
            if not valid:
                return Verdict("REVIEW", reason, len(witnessed), 0)
            body = claim["body"]
            sid = body["source_id"]
            if sid in witnessed:
                return Verdict("REVIEW", "duplicate-signer", len(witnessed), 0)
            witnessed[sid] = body
        signed = len(witnessed)
        # Explicit trusted caller / observer-backend boundary: no current
        # revision readback means we cannot establish replay freshness.
        if current_revisions is None:
            return Verdict("REVIEW", "current-witness-readback-unavailable", signed, 0)
        for sid, b in witnessed.items():
            if (type(current_revisions.get(sid)) is not int
                    or current_revisions[sid] != b["revision"]):
                return Verdict("REVIEW", "witness-revision-not-current", signed, 0)
        if any(b["status"] == "NOT_COMMITTED" or b["correctness"] == "FALSE" for b in witnessed.values()):
            return Verdict("CONFLICT", "authenticated-negative-or-contradiction", signed, 0)
        ready = [sid for sid,b in witnessed.items() if b["status"]=="COMMITTED" and b["correctness"]=="TRUE"]
        if any(b["status"] == "UNKNOWN" or b["correctness"] == "UNKNOWN" for b in witnessed.values()):
            return Verdict("REVIEW", "witness-uncertainty", signed, 0)
        # Enumerate small input (max 32). Early return when a qualifying subset found.
        paths = {sid:self.registry.exposure(sid) for sid in ready}
        def largest_disjoint():
            best: tuple[str, ...] = ()
            # Branch-and-bound search. If min_independent found, decision is settled.
            order=sorted(ready)
            def scan(i,chosen,roots,controllers):
                nonlocal best
                if len(chosen)>len(best):
                    best=tuple(chosen)
                if len(best)>=self.min_independent or i>=len(order) or len(chosen)+len(order)-i<=len(best):
                    return
                sid=order[i]; r,c=paths[sid]
                if r.isdisjoint(roots) and c.isdisjoint(controllers):
                    scan(i+1,chosen+[sid],roots|r,controllers|c)
                scan(i+1,chosen,roots,controllers)
            scan(0,[],frozenset(),frozenset())
            return best
        best=largest_disjoint()
        if len(best) < self.min_independent:
            return Verdict("REVIEW", "common-origin-or-insufficient-independent-evidence",signed,len(best),best)
        return Verdict("CONFIRMED", "independent-declared-paths-agree",signed,len(best),best)


def naive_signed_quorum(registry: TrustedRegistry, claims: Sequence[dict], **params) -> str:
    """Ablation: signatures validated, but dependencies/ownership ignored."""
    gate = ProvenanceGate(registry)
    if not params.get("provider_receipt_valid", True):
        return "REVIEW"
    valid=[]
    for c in claims:
        ok,_ = gate.verify_one(c, effect_id=params["effect_id"],
                               action_sha256=params["action_sha256"],token_sha256=params["token_sha256"],now=params["now"])
        if not ok:
            return "REVIEW"
        valid.append(c["body"])
    if any(x["correctness"] == "FALSE" or x["status"] == "NOT_COMMITTED" for x in valid):
        return "CONFLICT"
    revisions = params.get("current_revisions")
    if revisions is None or any(type(revisions.get(x["source_id"])) is not int or
                                revisions[x["source_id"]] != x["revision"] for x in valid):
        return "REVIEW"
    if len({x["source_id"] for x in valid if x["correctness"]=="TRUE" and x["status"]=="COMMITTED"})>=2:
        return "CONFIRMED"
    return "REVIEW"
